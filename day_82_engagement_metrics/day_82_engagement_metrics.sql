-- ============================================================
-- ENGAGEMENT METRICS ANALYTICS
-- PostgreSQL 14+
--
-- Metrics:
-- DAU, WAU, MAU, stickiness, event frequency and sessions.
--
-- All event timestamps are stored as TIMESTAMPTZ.
-- Reporting uses UTC calendar days.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS engagement;

SET search_path TO engagement, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    external_user_key VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (organization_id, external_user_key)
);

CREATE TABLE IF NOT EXISTS event_types (
    event_type_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_name VARCHAR(40) NOT NULL UNIQUE,
    qualifies_as_activity BOOLEAN NOT NULL
);

INSERT INTO event_types (event_name, qualifies_as_activity)
VALUES
    ('login', TRUE),
    ('page_view', TRUE),
    ('action', TRUE),
    ('purchase', TRUE),
    ('logout', FALSE)
ON CONFLICT (event_name) DO UPDATE
SET qualifies_as_activity = EXCLUDED.qualifies_as_activity;

CREATE TABLE IF NOT EXISTS engagement_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    event_uuid UUID NOT NULL UNIQUE,
    event_type_id SMALLINT NOT NULL
        REFERENCES event_types(event_type_id),
    occurred_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    properties JSONB NOT NULL DEFAULT '{}'::JSONB,

    CONSTRAINT valid_properties
        CHECK (jsonb_typeof(properties) = 'object'),

    CONSTRAINT valid_event_time
        CHECK (occurred_at <= received_at + INTERVAL '5 minutes')
);

CREATE TABLE IF NOT EXISTS analytics_sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    started_at TIMESTAMPTZ NOT NULL,
    last_event_at TIMESTAMPTZ NOT NULL,
    event_count INTEGER NOT NULL CHECK (event_count > 0),
    session_timeout_minutes INTEGER NOT NULL DEFAULT 30,
    session_status VARCHAR(15) NOT NULL DEFAULT 'completed',

    CONSTRAINT valid_session_interval
        CHECK (last_event_at >= started_at),

    CONSTRAINT valid_session_timeout
        CHECK (session_timeout_minutes BETWEEN 1 AND 1440),

    CONSTRAINT valid_session_status
        CHECK (session_status IN ('active', 'completed'))
);

CREATE TABLE IF NOT EXISTS daily_engagement_metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    report_date DATE NOT NULL,
    dau INTEGER NOT NULL CHECK (dau >= 0),
    wau INTEGER NOT NULL CHECK (wau >= 0),
    mau INTEGER NOT NULL CHECK (mau >= 0),
    stickiness NUMERIC(8, 2) NOT NULL CHECK (stickiness >= 0),
    qualifying_events BIGINT NOT NULL DEFAULT 0,
    total_sessions BIGINT NOT NULL DEFAULT 0,
    average_session_duration NUMERIC(14, 2) NOT NULL DEFAULT 0,
    average_sessions_per_user NUMERIC(14, 2) NOT NULL DEFAULT 0,
    average_events_per_session NUMERIC(14, 2) NOT NULL DEFAULT 0,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (organization_id, report_date),

    CHECK (dau <= wau),
    CHECK (wau <= mau),
    CHECK (stickiness <= 100)
);

-- ------------------------------------------------------------
-- 2. INDEXES
-- ------------------------------------------------------------

-- Supports time-range scans and organization-level analytics.
CREATE INDEX IF NOT EXISTS idx_events_org_time
ON engagement_events (organization_id, occurred_at);

-- Supports distinct-user activity queries.
CREATE INDEX IF NOT EXISTS idx_events_org_user_time
ON engagement_events (organization_id, user_id, occurred_at);

-- Supports event-type filtering.
CREATE INDEX IF NOT EXISTS idx_events_type_time
ON engagement_events (event_type_id, occurred_at);

-- JSONB properties are indexed for selected attribute searches.
CREATE INDEX IF NOT EXISTS idx_events_properties
ON engagement_events USING GIN (properties);

CREATE INDEX IF NOT EXISTS idx_sessions_org_user_start
ON analytics_sessions (
    organization_id,
    user_id,
    started_at
);

CREATE INDEX IF NOT EXISTS idx_metrics_org_date
ON daily_engagement_metrics (
    organization_id,
    report_date DESC
);

-- ------------------------------------------------------------
-- 3. EVENT INTEGRITY TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_event_organization()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    actual_organization_id BIGINT;
BEGIN
    SELECT organization_id
    INTO actual_organization_id
    FROM users
    WHERE user_id = NEW.user_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown user ID: %', NEW.user_id;
    END IF;

    IF actual_organization_id <> NEW.organization_id THEN
        RAISE EXCEPTION
            'User and event organization do not match';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_event_organization
ON engagement_events;

CREATE TRIGGER trg_validate_event_organization
BEFORE INSERT OR UPDATE OF user_id, organization_id
ON engagement_events
FOR EACH ROW
EXECUTE FUNCTION validate_event_organization();

-- ------------------------------------------------------------
-- 4. ACTIVITY VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW qualifying_activity AS
SELECT
    e.event_id,
    e.organization_id,
    e.user_id,
    e.event_uuid,
    et.event_name,
    e.occurred_at,
    e.properties
FROM engagement_events e
JOIN event_types et
    ON et.event_type_id = e.event_type_id
WHERE et.qualifies_as_activity = TRUE;

-- ------------------------------------------------------------
-- 5. SESSION GENERATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION generate_sessions(
    p_organization_id BIGINT,
    p_start TIMESTAMPTZ,
    p_end TIMESTAMPTZ,
    p_timeout_minutes INTEGER DEFAULT 30
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    inserted_count BIGINT;
BEGIN
    IF p_start >= p_end THEN
        RAISE EXCEPTION 'Invalid session reporting interval';
    END IF;

    IF p_timeout_minutes NOT BETWEEN 1 AND 1440 THEN
        RAISE EXCEPTION 'Invalid session timeout';
    END IF;

    /*
       The LAG window function compares each event with the
       preceding event for the same user.

       A new session begins when the inactivity gap exceeds
       the configured timeout.
    */

    WITH ordered_events AS (
        SELECT
            organization_id,
            user_id,
            occurred_at,
            LAG(occurred_at) OVER (
                PARTITION BY organization_id, user_id
                ORDER BY occurred_at, event_id
            ) AS previous_event
        FROM qualifying_activity
        WHERE organization_id = p_organization_id
          AND occurred_at < p_end
    ),

    session_markers AS (
        SELECT
            organization_id,
            user_id,
            occurred_at,
            CASE
                WHEN previous_event IS NULL THEN 1
                WHEN occurred_at - previous_event >
                    make_interval(mins => p_timeout_minutes)
                THEN 1
                ELSE 0
            END AS new_session
        FROM ordered_events
    ),

    numbered_events AS (
        SELECT
            organization_id,
            user_id,
            occurred_at,
            SUM(new_session) OVER (
                PARTITION BY organization_id, user_id
                ORDER BY occurred_at
                ROWS UNBOUNDED PRECEDING
            ) AS session_number
        FROM session_markers
    ),

    grouped_sessions AS (
        SELECT
            organization_id,
            user_id,
            MIN(occurred_at) AS started_at,
            MAX(occurred_at) AS last_event_at,
            COUNT(*)::INTEGER AS event_count
        FROM numbered_events
        GROUP BY
            organization_id,
            user_id,
            session_number
    ),

    inserted_sessions AS (
        INSERT INTO analytics_sessions (
            organization_id,
            user_id,
            started_at,
            last_event_at,
            event_count,
            session_timeout_minutes,
            session_status
        )
        SELECT
            organization_id,
            user_id,
            started_at,
            last_event_at,
            event_count,
            p_timeout_minutes,
            'completed'
        FROM grouped_sessions
        WHERE started_at >= p_start
          AND started_at < p_end
        RETURNING session_id
    )

    SELECT COUNT(*)
    INTO inserted_count
    FROM inserted_sessions;

    RETURN inserted_count;
END;
$$;

-- ------------------------------------------------------------
-- 6. DAILY METRICS CALCULATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_daily_metrics(
    p_organization_id BIGINT,
    p_report_date DATE
)
RETURNS TABLE (
    result_dau INTEGER,
    result_wau INTEGER,
    result_mau INTEGER,
    result_stickiness NUMERIC,
    result_sessions BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_start TIMESTAMPTZ;
    v_end TIMESTAMPTZ;

    v_dau INTEGER;
    v_wau INTEGER;
    v_mau INTEGER;
    v_stickiness NUMERIC;
    v_events BIGINT;
    v_sessions BIGINT;

    v_avg_duration NUMERIC;
    v_avg_sessions NUMERIC;
    v_avg_events NUMERIC;
BEGIN
    IF p_organization_id IS NULL OR p_report_date IS NULL THEN
        RAISE EXCEPTION 'Organization and report date are required';
    END IF;

    v_start := p_report_date::TIMESTAMP AT TIME ZONE 'UTC';
    v_end := (p_report_date + 1)::TIMESTAMP AT TIME ZONE 'UTC';

    -- DAU: distinct users active during the UTC calendar day.
    SELECT COUNT(DISTINCT user_id)
    INTO v_dau
    FROM qualifying_activity
    WHERE organization_id = p_organization_id
      AND occurred_at >= v_start
      AND occurred_at < v_end;

    -- WAU: rolling seven-day window including report date.
    SELECT COUNT(DISTINCT user_id)
    INTO v_wau
    FROM qualifying_activity
    WHERE organization_id = p_organization_id
      AND occurred_at >= v_start - INTERVAL '6 days'
      AND occurred_at < v_end;

    -- MAU: rolling thirty-day window including report date.
    SELECT COUNT(DISTINCT user_id)
    INTO v_mau
    FROM qualifying_activity
    WHERE organization_id = p_organization_id
      AND occurred_at >= v_start - INTERVAL '29 days'
      AND occurred_at < v_end;

    v_stickiness := CASE
        WHEN v_mau = 0 THEN 0
        ELSE ROUND(v_dau::NUMERIC / v_mau * 100, 2)
    END;

    SELECT COUNT(*)
    INTO v_events
    FROM qualifying_activity
    WHERE organization_id = p_organization_id
      AND occurred_at >= v_start
      AND occurred_at < v_end;

    /*
       Generate sessions before aggregation.

       The session function considers previous events before the
       reporting day to avoid incorrectly splitting sessions that
       begin shortly before midnight.
    */
    PERFORM generate_sessions(
        p_organization_id,
        v_start,
        v_end,
        30
    );

    SELECT
        COUNT(*),
        COALESCE(
            ROUND(AVG(
                EXTRACT(EPOCH FROM last_event_at - started_at)
            )::NUMERIC, 2),
            0
        ),
        COALESCE(
            ROUND(
                COUNT(*)::NUMERIC /
                NULLIF(COUNT(DISTINCT user_id), 0),
                2
            ),
            0
        ),
        COALESCE(
            ROUND(AVG(event_count)::NUMERIC, 2),
            0
        )
    INTO
        v_sessions,
        v_avg_duration,
        v_avg_sessions,
        v_avg_events
    FROM analytics_sessions
    WHERE organization_id = p_organization_id
      AND started_at >= v_start
      AND started_at < v_end;

    INSERT INTO daily_engagement_metrics (
        organization_id,
        report_date,
        dau,
        wau,
        mau,
        stickiness,
        qualifying_events,
        total_sessions,
        average_session_duration,
        average_sessions_per_user,
        average_events_per_session,
        calculated_at
    )
    VALUES (
        p_organization_id,
        p_report_date,
        v_dau,
        v_wau,
        v_mau,
        v_stickiness,
        v_events,
        v_sessions,
        v_avg_duration,
        v_avg_sessions,
        v_avg_events,
        NOW()
    )
    ON CONFLICT (organization_id, report_date)
    DO UPDATE SET
        dau = EXCLUDED.dau,
        wau = EXCLUDED.wau,
        mau = EXCLUDED.mau,
        stickiness = EXCLUDED.stickiness,
        qualifying_events = EXCLUDED.qualifying_events,
        total_sessions = EXCLUDED.total_sessions,
        average_session_duration =
            EXCLUDED.average_session_duration,
        average_sessions_per_user =
            EXCLUDED.average_sessions_per_user,
        average_events_per_session =
            EXCLUDED.average_events_per_session,
        calculated_at = NOW();

    RETURN QUERY
    SELECT
        v_dau,
        v_wau,
        v_mau,
        v_stickiness,
        v_sessions;
END;
$$;

-- ------------------------------------------------------------
-- 7. SESSION FREQUENCY REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW user_session_frequency AS
SELECT
    organization_id,
    user_id,
    (started_at AT TIME ZONE 'UTC')::DATE AS session_date,
    COUNT(*) AS session_count,
    SUM(event_count) AS event_count
FROM analytics_sessions
GROUP BY
    organization_id,
    user_id,
    (started_at AT TIME ZONE 'UTC')::DATE;

-- ------------------------------------------------------------
-- 8. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO organizations (organization_name)
VALUES ('Enterprise Analytics')
ON CONFLICT (organization_name) DO NOTHING;

INSERT INTO users (
    organization_id,
    external_user_key
)
SELECT
    organization_id,
    user_key
FROM organizations
CROSS JOIN (
    VALUES
        ('user_001'),
        ('user_002'),
        ('user_003'),
        ('user_004'),
        ('user_005')
) AS sample_users(user_key)
WHERE organization_name = 'Enterprise Analytics'
ON CONFLICT (organization_id, external_user_key) DO NOTHING;

-- Sample event timestamps are explicitly UTC.
WITH sample_data (
    external_user_key,
    event_uuid,
    event_name,
    occurred_at
) AS (
    VALUES
    (
        'user_001',
        '00000000-0000-4000-8000-000000000001'::UUID,
        'login',
        '2026-11-19 09:00:00+00'::TIMESTAMPTZ
    ),
    (
        'user_001',
        '00000000-0000-4000-8000-000000000002'::UUID,
        'page_view',
        '2026-11-19 09:05:00+00'::TIMESTAMPTZ
    ),
    (
        'user_001',
        '00000000-0000-4000-8000-000000000003'::UUID,
        'action',
        '2026-11-19 09:15:00+00'::TIMESTAMPTZ
    ),
    (
        'user_001',
        '00000000-0000-4000-8000-000000000004'::UUID,
        'login',
        '2026-11-19 11:00:00+00'::TIMESTAMPTZ
    ),
    (
        'user_002',
        '00000000-0000-4000-8000-000000000005'::UUID,
        'login',
        '2026-11-19 10:00:00+00'::TIMESTAMPTZ
    ),
    (
        'user_002',
        '00000000-0000-4000-8000-000000000006'::UUID,
        'purchase',
        '2026-11-19 10:10:00+00'::TIMESTAMPTZ
    ),
    (
        'user_003',
        '00000000-0000-4000-8000-000000000007'::UUID,
        'page_view',
        '2026-11-18 12:00:00+00'::TIMESTAMPTZ
    ),
    (
        'user_003',
        '00000000-0000-4000-8000-000000000008'::UUID,
        'action',
        '2026-11-17 12:00:00+00'::TIMESTAMPTZ
    ),
    (
        'user_004',
        '00000000-0000-4000-8000-000000000009'::UUID,
        'login',
        '2026-11-01 08:00:00+00'::TIMESTAMPTZ
    ),
    (
        'user_005',
        '00000000-0000-4000-8000-000000000010'::UUID,
        'logout',
        '2026-11-19 12:00:00+00'::TIMESTAMPTZ
    )
)
INSERT INTO engagement_events (
    organization_id,
    user_id,
    event_uuid,
    event_type_id,
    occurred_at,
    properties
)
SELECT
    o.organization_id,
    u.user_id,
    s.event_uuid,
    et.event_type_id,
    s.occurred_at,
    jsonb_build_object(
        'source', 'sample_application',
        'environment', 'production'
    )
FROM sample_data s
JOIN organizations o
    ON o.organization_name = 'Enterprise Analytics'
JOIN users u
    ON u.organization_id = o.organization_id
   AND u.external_user_key = s.external_user_key
JOIN event_types et
    ON et.event_name = s.event_name
ON CONFLICT (event_uuid) DO NOTHING;

-- ------------------------------------------------------------
-- 9. EXECUTE DAILY CALCULATION
-- ------------------------------------------------------------

DO $$
DECLARE
    v_organization_id BIGINT;
BEGIN
    SELECT organization_id
    INTO v_organization_id
    FROM organizations
    WHERE organization_name = 'Enterprise Analytics';

    PERFORM calculate_daily_metrics(
        v_organization_id,
        DATE '2026-11-19'
    );
END;
$$;

-- ------------------------------------------------------------
-- 10. RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- Daily engagement report.
SELECT
    o.organization_name,
    m.report_date,
    m.dau,
    m.wau,
    m.mau,
    m.stickiness,
    m.qualifying_events,
    m.total_sessions
FROM daily_engagement_metrics m
JOIN organizations o
    ON o.organization_id = m.organization_id
WHERE o.organization_name = 'Enterprise Analytics'
ORDER BY m.report_date DESC;

-- User activity frequency.
SELECT
    u.external_user_key,
    COUNT(DISTINCT a.event_id) AS qualifying_events
FROM qualifying_activity a
JOIN users u
    ON u.user_id = a.user_id
WHERE a.occurred_at >=
    TIMESTAMPTZ '2026-11-19 00:00:00+00'
  AND a.occurred_at <
    TIMESTAMPTZ '2026-11-20 00:00:00+00'
GROUP BY u.external_user_key
ORDER BY qualifying_events DESC;

-- Session frequency by user.
SELECT
    u.external_user_key,
    f.session_date,
    f.session_count,
    f.event_count
FROM user_session_frequency f
JOIN users u
    ON u.user_id = f.user_id
WHERE f.session_date = DATE '2026-11-19'
ORDER BY f.session_count DESC;

-- ------------------------------------------------------------
-- 11. VALIDATION AND ELIGIBILITY QUERIES
-- ------------------------------------------------------------

-- DAU must not exceed WAU, and WAU must not exceed MAU.
SELECT
    report_date,
    dau,
    wau,
    mau,
    CASE
        WHEN dau <= wau AND wau <= mau THEN 'VALID'
        ELSE 'INVALID'
    END AS metric_validation
FROM daily_engagement_metrics;

-- Identify users with multiple sessions.
SELECT
    external_user_key,
    session_date,
    session_count,
    CASE
        WHEN session_count >= 2 THEN 'MULTI_SESSION'
        WHEN session_count = 1 THEN 'SINGLE_SESSION'
        ELSE 'NO_SESSION'
    END AS frequency_category
FROM user_session_frequency
JOIN users USING (user_id)
ORDER BY session_count DESC;

-- Identify organizations with no qualifying activity.
SELECT
    o.organization_id,
    o.organization_name
FROM organizations o
WHERE NOT EXISTS (
    SELECT 1
    FROM qualifying_activity a
    WHERE a.organization_id = o.organization_id
);

-- ------------------------------------------------------------
-- 12. AGGREGATION AND TREND REPORTING
-- ------------------------------------------------------------

-- Rolling seven-day distinct-user calculation.
WITH calendar AS (
    SELECT generate_series(
        DATE '2026-11-17',
        DATE '2026-11-19',
        INTERVAL '1 day'
    )::DATE AS report_date
),
activity_windows AS (
    SELECT
        c.report_date,
        COUNT(DISTINCT a.user_id) AS wau
    FROM calendar c
    LEFT JOIN qualifying_activity a
        ON a.occurred_at >=
            (c.report_date - 6)::TIMESTAMP AT TIME ZONE 'UTC'
       AND a.occurred_at <
            (c.report_date + 1)::TIMESTAMP AT TIME ZONE 'UTC'
    GROUP BY c.report_date
)
SELECT *
FROM activity_windows
ORDER BY report_date;

-- Daily stickiness trend.
SELECT
    report_date,
    dau,
    wau,
    mau,
    stickiness,
    LAG(stickiness) OVER (
        ORDER BY report_date
    ) AS previous_day_stickiness,
    stickiness - LAG(stickiness) OVER (
        ORDER BY report_date
    ) AS stickiness_change
FROM daily_engagement_metrics
ORDER BY report_date;

-- ------------------------------------------------------------
-- 13. TRANSACTION SAFETY
-- ------------------------------------------------------------

-- All sample records, generated sessions and metrics are committed
-- together. Re-running sample ingestion is safe through event_uuid
-- uniqueness, while metric rows are updated through their unique key.

COMMIT;
