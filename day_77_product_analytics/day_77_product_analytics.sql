-- ============================================================
-- PRODUCT ANALYTICS PLATFORM
-- PostgreSQL 15+
--
-- Models:
--   Users and anonymous identities
--   Event definitions and event properties
--   Immutable event records
--   Sessions and session events
--   Conversion funnels
--   Cohort retention
--   Event aggregation
--   Data quality
--   Reporting and analytics policies
--
-- Execute:
--   psql -v ON_ERROR_STOP=1 -d analytics_db -f product_analytics.sql
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_analytics;

SET search_path TO product_analytics, public;

-- ============================================================
-- 1. Enumerated domain types
-- ============================================================

CREATE TYPE user_plan AS ENUM (
    'free',
    'premium',
    'enterprise'
);

CREATE TYPE event_status AS ENUM (
    'accepted',
    'rejected'
);

CREATE TYPE funnel_status AS ENUM (
    'draft',
    'active',
    'archived'
);

CREATE TYPE session_source AS ENUM (
    'automatic',
    'explicit'
);

-- ============================================================
-- 2. Users and identities
-- ============================================================

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    external_user_key VARCHAR(150) NOT NULL UNIQUE,

    country CHAR(2) NOT NULL DEFAULT 'IN',

    plan user_plan NOT NULL DEFAULT 'free',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_external_user_key
        CHECK (length(trim(external_user_key)) > 0),

    CONSTRAINT valid_country
        CHECK (country ~ '^[A-Z]{2}$')
);

CREATE TABLE anonymous_identities (
    anonymous_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    anonymous_key VARCHAR(150) NOT NULL UNIQUE,

    user_id BIGINT REFERENCES users(user_id)
        ON DELETE SET NULL,

    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    linked_at TIMESTAMPTZ,

    CONSTRAINT valid_anonymous_key
        CHECK (length(trim(anonymous_key)) > 0),

    CONSTRAINT identity_link_timestamp
        CHECK (
            (user_id IS NULL AND linked_at IS NULL)
            OR
            (user_id IS NOT NULL AND linked_at IS NOT NULL)
        )
);

CREATE INDEX idx_anonymous_user
    ON anonymous_identities(user_id);

-- ============================================================
-- 3. Event catalog
-- ============================================================

CREATE TABLE event_definitions (
    event_type_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT NOT NULL,

    category VARCHAR(50) NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_event_name
        CHECK (
            event_name ~ '^[a-z][a-z0-9_]{0,99}$'
        )
);

INSERT INTO event_definitions (
    event_name,
    description,
    category
)
VALUES
    ('signup', 'User creates an account', 'acquisition'),
    ('login', 'User authenticates', 'engagement'),
    ('page_view', 'User views a page', 'engagement'),
    ('product_view', 'User views a product', 'engagement'),
    ('add_to_cart', 'User adds a product to cart', 'conversion'),
    ('checkout_started', 'User starts checkout', 'conversion'),
    ('purchase', 'User completes a purchase', 'revenue'),
    ('logout', 'User ends an authenticated session', 'engagement');

-- ============================================================
-- 4. Sessions
-- ============================================================

CREATE TABLE sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    session_key UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),

    user_id BIGINT NOT NULL REFERENCES users(user_id),

    started_at TIMESTAMPTZ NOT NULL,

    last_event_at TIMESTAMPTZ NOT NULL,

    ended_at TIMESTAMPTZ,

    source session_source NOT NULL DEFAULT 'automatic',

    CONSTRAINT valid_session_times
        CHECK (last_event_at >= started_at),

    CONSTRAINT valid_session_end
        CHECK (
            ended_at IS NULL OR
            ended_at >= started_at
        )
);

CREATE INDEX idx_sessions_user_start
    ON sessions(user_id, started_at DESC);

CREATE INDEX idx_sessions_started
    ON sessions(started_at DESC);

-- ============================================================
-- 5. Events
-- ============================================================

CREATE TABLE events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_key UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),

    user_id BIGINT NOT NULL REFERENCES users(user_id),

    anonymous_id BIGINT REFERENCES anonymous_identities(
        anonymous_id
    ),

    session_id BIGINT REFERENCES sessions(session_id)
        ON DELETE SET NULL,

    event_type_id SMALLINT NOT NULL REFERENCES event_definitions(
        event_type_id
    ),

    event_timestamp TIMESTAMPTZ NOT NULL,

    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    properties JSONB NOT NULL DEFAULT '{}'::jsonb,

    schema_version SMALLINT NOT NULL DEFAULT 1,

    status event_status NOT NULL DEFAULT 'accepted',

    CONSTRAINT valid_event_properties
        CHECK (jsonb_typeof(properties) = 'object'),

    CONSTRAINT valid_schema_version
        CHECK (schema_version > 0),

    CONSTRAINT valid_event_timestamp
        CHECK (event_timestamp <= received_at + INTERVAL '5 minutes')
);

-- High-volume event retrieval indexes.
CREATE INDEX idx_events_user_timestamp
    ON events(user_id, event_timestamp);

CREATE INDEX idx_events_type_timestamp
    ON events(event_type_id, event_timestamp);

CREATE INDEX idx_events_session_timestamp
    ON events(session_id, event_timestamp);

CREATE INDEX idx_events_properties
    ON events USING GIN(properties jsonb_path_ops);

CREATE INDEX idx_events_timestamp_brin
    ON events USING BRIN(event_timestamp);

-- ============================================================
-- 6. Property definitions
-- ============================================================

CREATE TABLE property_definitions (
    property_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    property_name VARCHAR(100) NOT NULL UNIQUE,

    data_type VARCHAR(20) NOT NULL,

    is_required BOOLEAN NOT NULL DEFAULT FALSE,

    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,

    description TEXT NOT NULL,

    CONSTRAINT valid_property_type
        CHECK (
            data_type IN (
                'string',
                'number',
                'boolean'
            )
        ),

    CONSTRAINT valid_property_name
        CHECK (
            property_name ~ '^[a-zA-Z][a-zA-Z0-9_]{0,99}$'
        )
);

INSERT INTO property_definitions (
    property_name,
    data_type,
    is_required,
    description
)
VALUES
    ('product_id', 'string', TRUE, 'Product identifier'),
    ('amount', 'number', FALSE, 'Transaction amount'),
    ('currency', 'string', FALSE, 'ISO currency code'),
    ('page', 'string', FALSE, 'Page path'),
    ('device_type', 'string', FALSE, 'Device category'),
    ('campaign_id', 'string', FALSE, 'Marketing campaign'),
    ('quantity', 'number', FALSE, 'Purchased quantity');

-- ============================================================
-- 7. Reviewable event quality failures
-- ============================================================

CREATE TABLE event_quality_issues (
    issue_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_id BIGINT REFERENCES events(event_id)
        ON DELETE SET NULL,

    external_event_key UUID,

    issue_code VARCHAR(100) NOT NULL,

    issue_description TEXT NOT NULL,

    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    resolved_at TIMESTAMPTZ,

    CONSTRAINT valid_issue_resolution
        CHECK (
            resolved_at IS NULL OR resolved_at >= detected_at
        )
);

CREATE INDEX idx_quality_unresolved
    ON event_quality_issues(detected_at)
    WHERE resolved_at IS NULL;

-- ============================================================
-- 8. Funnel definitions
-- ============================================================

CREATE TABLE funnels (
    funnel_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    funnel_name VARCHAR(150) NOT NULL UNIQUE,

    status funnel_status NOT NULL DEFAULT 'draft',

    conversion_window_hours INTEGER NOT NULL DEFAULT 168,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_conversion_window
        CHECK (conversion_window_hours BETWEEN 1 AND 2160)
);

CREATE TABLE funnel_steps (
    funnel_id BIGINT NOT NULL REFERENCES funnels(funnel_id)
        ON DELETE CASCADE,

    step_number SMALLINT NOT NULL,

    event_type_id SMALLINT NOT NULL REFERENCES event_definitions(
        event_type_id
    ),

    PRIMARY KEY (funnel_id, step_number),

    UNIQUE (funnel_id, event_type_id),

    CONSTRAINT valid_step_number
        CHECK (step_number > 0)
);

INSERT INTO funnels (
    funnel_name,
    status,
    conversion_window_hours
)
VALUES (
    'Product Purchase Funnel',
    'active',
    168
);

INSERT INTO funnel_steps (
    funnel_id,
    step_number,
    event_type_id
)
SELECT
    f.funnel_id,
    v.step_number,
    d.event_type_id
FROM funnels f
CROSS JOIN (
    VALUES
        (1, 'signup'),
        (2, 'product_view'),
        (3, 'add_to_cart'),
        (4, 'checkout_started'),
        (5, 'purchase')
) AS v(step_number, event_name)
JOIN event_definitions d
    ON d.event_name = v.event_name
WHERE f.funnel_name = 'Product Purchase Funnel';

-- ============================================================
-- 9. Materialized analytics snapshots
-- ============================================================

CREATE TABLE daily_product_metrics (
    metric_date DATE NOT NULL,

    event_type_id SMALLINT NOT NULL REFERENCES event_definitions(
        event_type_id
    ),

    total_events BIGINT NOT NULL DEFAULT 0,

    unique_users BIGINT NOT NULL DEFAULT 0,

    revenue NUMERIC(18, 2) NOT NULL DEFAULT 0,

    PRIMARY KEY (metric_date, event_type_id),

    CONSTRAINT valid_metric_counts
        CHECK (
            total_events >= 0
            AND unique_users >= 0
            AND revenue >= 0
        )
);

CREATE TABLE cohort_retention (
    cohort_month DATE NOT NULL,

    month_offset INTEGER NOT NULL,

    cohort_size INTEGER NOT NULL,

    retained_users INTEGER NOT NULL,

    retention_rate NUMERIC(7, 2) NOT NULL,

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (cohort_month, month_offset),

    CONSTRAINT valid_cohort_month
        CHECK (
            EXTRACT(DAY FROM cohort_month) = 1
        ),

    CONSTRAINT valid_cohort_offset
        CHECK (month_offset >= 0),

    CONSTRAINT valid_cohort_size
        CHECK (
            cohort_size > 0
            AND retained_users BETWEEN 0 AND cohort_size
        ),

    CONSTRAINT valid_retention_rate
        CHECK (retention_rate BETWEEN 0 AND 100)
);

-- ============================================================
-- 10. Event property validation function
-- ============================================================

CREATE OR REPLACE FUNCTION validate_event_properties()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    event_name_value VARCHAR(100);
    amount_value NUMERIC;
BEGIN
    SELECT event_name
    INTO event_name_value
    FROM event_definitions
    WHERE event_type_id = NEW.event_type_id;

    IF event_name_value IS NULL THEN
        RAISE EXCEPTION 'Unknown event definition';
    END IF;

    IF event_name_value = 'purchase' THEN
        IF NOT (NEW.properties ? 'amount') THEN
            RAISE EXCEPTION 'Purchase requires amount property';
        END IF;

        IF jsonb_typeof(NEW.properties -> 'amount') <> 'number' THEN
            RAISE EXCEPTION 'Purchase amount must be numeric';
        END IF;

        amount_value := (NEW.properties ->> 'amount')::NUMERIC;

        IF amount_value < 0 THEN
            RAISE EXCEPTION 'Purchase amount cannot be negative';
        END IF;

        IF NOT (NEW.properties ? 'currency') THEN
            RAISE EXCEPTION 'Purchase requires currency';
        END IF;

        IF NEW.properties ->> 'currency' !~ '^[A-Z]{3}$' THEN
            RAISE EXCEPTION 'Invalid currency code';
        END IF;
    END IF;

    IF event_name_value IN ('product_view', 'add_to_cart')
       AND NOT (NEW.properties ? 'product_id') THEN
        RAISE EXCEPTION '% requires product_id', event_name_value;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_event_properties
BEFORE INSERT OR UPDATE OF properties, event_type_id
ON events
FOR EACH ROW
EXECUTE FUNCTION validate_event_properties();

-- ============================================================
-- 11. Event audit trigger
-- ============================================================

CREATE TABLE event_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_id BIGINT NOT NULL,

    operation VARCHAR(10) NOT NULL,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    changed_by TEXT NOT NULL DEFAULT CURRENT_USER
);

CREATE OR REPLACE FUNCTION audit_event_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO event_audit(event_id, operation)
        VALUES (NEW.event_id, 'INSERT');

        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO event_audit(event_id, operation)
        VALUES (NEW.event_id, 'UPDATE');

        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_event_audit
AFTER INSERT OR UPDATE
ON events
FOR EACH ROW
EXECUTE FUNCTION audit_event_changes();

-- ============================================================
-- 12. Identity linking procedure
-- ============================================================

CREATE OR REPLACE PROCEDURE link_anonymous_identity(
    p_anonymous_key VARCHAR(150),
    p_external_user_key VARCHAR(150)
)
LANGUAGE plpgsql
AS $$
DECLARE
    target_user_id BIGINT;
    target_anonymous_id BIGINT;
    current_user_id BIGINT;
BEGIN
    SELECT user_id
    INTO target_user_id
    FROM users
    WHERE external_user_key = p_external_user_key
    FOR UPDATE;

    IF target_user_id IS NULL THEN
        RAISE EXCEPTION 'Unknown user: %', p_external_user_key;
    END IF;

    SELECT anonymous_id, user_id
    INTO target_anonymous_id, current_user_id
    FROM anonymous_identities
    WHERE anonymous_key = p_anonymous_key
    FOR UPDATE;

    IF target_anonymous_id IS NULL THEN
        RAISE EXCEPTION 'Unknown anonymous identity: %',
            p_anonymous_key;
    END IF;

    IF current_user_id IS NOT NULL
       AND current_user_id <> target_user_id THEN
        RAISE EXCEPTION 'Identity already linked to another user';
    END IF;

    UPDATE anonymous_identities
    SET user_id = target_user_id,
        linked_at = COALESCE(linked_at, NOW())
    WHERE anonymous_id = target_anonymous_id;
END;
$$;

-- ============================================================
-- 13. Event insertion function
-- ============================================================

CREATE OR REPLACE FUNCTION ingest_event(
    p_event_key UUID,
    p_external_user_key VARCHAR(150),
    p_event_name VARCHAR(100),
    p_event_timestamp TIMESTAMPTZ,
    p_properties JSONB,
    p_session_key UUID DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    target_user_id BIGINT;
    target_event_type_id SMALLINT;
    target_session_id BIGINT;
    inserted_event_id BIGINT;
BEGIN
    SELECT user_id
    INTO target_user_id
    FROM users
    WHERE external_user_key = p_external_user_key;

    IF target_user_id IS NULL THEN
        RAISE EXCEPTION 'Unknown user: %', p_external_user_key;
    END IF;

    SELECT event_type_id
    INTO target_event_type_id
    FROM event_definitions
    WHERE event_name = p_event_name
      AND is_active = TRUE;

    IF target_event_type_id IS NULL THEN
        RAISE EXCEPTION 'Inactive or unknown event: %',
            p_event_name;
    END IF;

    IF p_session_key IS NOT NULL THEN
        SELECT session_id
        INTO target_session_id
        FROM sessions
        WHERE session_key = p_session_key
          AND user_id = target_user_id;

        IF target_session_id IS NULL THEN
            RAISE EXCEPTION 'Invalid session for user';
        END IF;
    END IF;

    INSERT INTO events (
        event_key,
        user_id,
        session_id,
        event_type_id,
        event_timestamp,
        properties
    )
    VALUES (
        p_event_key,
        target_user_id,
        target_session_id,
        target_event_type_id,
        p_event_timestamp,
        COALESCE(p_properties, '{}'::jsonb)
    )
    ON CONFLICT (event_key) DO NOTHING
    RETURNING event_id INTO inserted_event_id;

    IF inserted_event_id IS NULL THEN
        RAISE EXCEPTION 'Duplicate event key: %', p_event_key;
    END IF;

    RETURN inserted_event_id;
END;
$$;

-- ============================================================
-- 14. Sessionization query
-- ============================================================

CREATE OR REPLACE VIEW session_event_summary AS
WITH ordered_events AS (
    SELECT
        e.event_id,
        e.user_id,
        e.event_timestamp,
        d.event_name,

        LAG(e.event_timestamp) OVER (
            PARTITION BY e.user_id
            ORDER BY e.event_timestamp, e.event_id
        ) AS previous_timestamp

    FROM events e
    JOIN event_definitions d
        ON d.event_type_id = e.event_type_id
),
session_boundaries AS (
    SELECT
        *,

        CASE
            WHEN previous_timestamp IS NULL THEN 1

            WHEN event_timestamp - previous_timestamp >
                 INTERVAL '30 minutes' THEN 1

            ELSE 0
        END AS new_session

    FROM ordered_events
),
numbered_events AS (
    SELECT
        *,

        SUM(new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp, event_id
        ) AS session_number

    FROM session_boundaries
)
SELECT
    user_id,
    session_number,
    MIN(event_timestamp) AS session_start,
    MAX(event_timestamp) AS session_end,
    COUNT(*) AS event_count,
    COUNT(DISTINCT event_name) AS distinct_event_types,
    ARRAY_AGG(event_name ORDER BY event_timestamp) AS event_sequence

FROM numbered_events

GROUP BY user_id, session_number;

-- ============================================================
-- 15. Funnel evaluation function
-- ============================================================

CREATE OR REPLACE FUNCTION evaluate_funnel(
    p_funnel_id BIGINT
)
RETURNS TABLE (
    step_number SMALLINT,
    event_name VARCHAR,
    unique_users BIGINT,
    previous_step_users BIGINT,
    conversion_rate NUMERIC
)
LANGUAGE sql
STABLE
AS $$
WITH funnel_configuration AS (
    SELECT
        fs.step_number,
        d.event_name,
        f.conversion_window_hours

    FROM funnels f

    JOIN funnel_steps fs
        ON fs.funnel_id = f.funnel_id

    JOIN event_definitions d
        ON d.event_type_id = fs.event_type_id

    WHERE f.funnel_id = p_funnel_id
      AND f.status = 'active'
),
user_events AS (
    SELECT
        e.user_id,
        d.event_name,
        e.event_timestamp

    FROM events e

    JOIN event_definitions d
        ON d.event_type_id = e.event_type_id
),
funnel_users AS (
    SELECT
        user_id,

        MIN(event_timestamp) FILTER (
            WHERE event_name = 'signup'
        ) AS signup_time,

        MIN(event_timestamp) FILTER (
            WHERE event_name = 'product_view'
        ) AS product_view_time,

        MIN(event_timestamp) FILTER (
            WHERE event_name = 'add_to_cart'
        ) AS cart_time,

        MIN(event_timestamp) FILTER (
            WHERE event_name = 'checkout_started'
        ) AS checkout_time,

        MIN(event_timestamp) FILTER (
            WHERE event_name = 'purchase'
        ) AS purchase_time

    FROM user_events
    GROUP BY user_id
),
qualified AS (
    SELECT
        user_id,

        signup_time,

        product_view_time,

        cart_time,

        checkout_time,

        purchase_time,

        CASE
            WHEN signup_time IS NOT NULL
             AND product_view_time >= signup_time
             AND product_view_time <=
                 signup_time + INTERVAL '168 hours'
            THEN TRUE ELSE FALSE
        END AS step_2,

        CASE
            WHEN signup_time IS NOT NULL
             AND product_view_time IS NOT NULL
             AND cart_time >= product_view_time
             AND cart_time <=
                 signup_time + INTERVAL '168 hours'
            THEN TRUE ELSE FALSE
        END AS step_3,

        CASE
            WHEN signup_time IS NOT NULL
             AND product_view_time IS NOT NULL
             AND cart_time IS NOT NULL
             AND checkout_time >= cart_time
             AND checkout_time <=
                 signup_time + INTERVAL '168 hours'
            THEN TRUE ELSE FALSE
        END AS step_4,

        CASE
            WHEN signup_time IS NOT NULL
             AND product_view_time IS NOT NULL
             AND cart_time IS NOT NULL
             AND checkout_time IS NOT NULL
             AND purchase_time >= checkout_time
             AND purchase_time <=
                 signup_time + INTERVAL '168 hours'
            THEN TRUE ELSE FALSE
        END AS step_5

    FROM funnel_users
),
counts AS (
    SELECT
        COUNT(*) FILTER (
            WHERE signup_time IS NOT NULL
        ) AS c1,

        COUNT(*) FILTER (
            WHERE step_2
        ) AS c2,

        COUNT(*) FILTER (
            WHERE step_3
        ) AS c3,

        COUNT(*) FILTER (
            WHERE step_4
        ) AS c4,

        COUNT(*) FILTER (
            WHERE step_5
        ) AS c5

    FROM qualified
),
step_counts AS (
    SELECT 1::SMALLINT AS step_number, c1 AS users FROM counts
    UNION ALL
    SELECT 2::SMALLINT, c2 FROM counts
    UNION ALL
    SELECT 3::SMALLINT, c3 FROM counts
    UNION ALL
    SELECT 4::SMALLINT, c4 FROM counts
    UNION ALL
    SELECT 5::SMALLINT, c5 FROM counts
),
calculated AS (
    SELECT
        step_number,
        users,

        LAG(users) OVER (
            ORDER BY step_number
        ) AS previous_users

    FROM step_counts
)
SELECT
    c.step_number,
    fc.event_name,
    c.users,
    COALESCE(c.previous_users, 0),

    CASE
        WHEN c.previous_users IS NULL AND c.users > 0
            THEN 100.00

        WHEN c.previous_users > 0
            THEN ROUND(
                c.users::NUMERIC /
                c.previous_users * 100,
                2
            )

        ELSE 0.00
    END

FROM calculated c

JOIN funnel_configuration fc
    ON fc.step_number = c.step_number

ORDER BY c.step_number;
$$;

-- ============================================================
-- 16. Cohort retention calculation procedure
-- ============================================================

CREATE OR REPLACE PROCEDURE refresh_cohort_retention(
    p_max_months INTEGER DEFAULT 12
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_max_months < 1 OR p_max_months > 120 THEN
        RAISE EXCEPTION 'Invalid cohort analysis horizon';
    END IF;

    DELETE FROM cohort_retention;

    INSERT INTO cohort_retention (
        cohort_month,
        month_offset,
        cohort_size,
        retained_users,
        retention_rate
    )
    WITH user_cohorts AS (
        SELECT
            user_id,

            DATE_TRUNC(
                'month',
                created_at
            )::DATE AS cohort_month

        FROM users
    ),
    user_activity AS (
        SELECT DISTINCT
            user_id,

            DATE_TRUNC(
                'month',
                event_timestamp
            )::DATE AS activity_month

        FROM events
        WHERE status = 'accepted'
    ),
    cohort_activity AS (
        SELECT
            c.cohort_month,

            (
                EXTRACT(YEAR FROM a.activity_month) -
                EXTRACT(YEAR FROM c.cohort_month)
            )::INTEGER * 12
            +
            (
                EXTRACT(MONTH FROM a.activity_month) -
                EXTRACT(MONTH FROM c.cohort_month)
            )::INTEGER AS month_offset,

            COUNT(DISTINCT c.user_id) AS retained_users,

            COUNT(DISTINCT c.user_id) OVER (
                PARTITION BY c.cohort_month
            ) AS unused_window_count

        FROM user_cohorts c

        JOIN user_activity a
            ON a.user_id = c.user_id

        WHERE a.activity_month >= c.cohort_month
    ),
    cohort_sizes AS (
        SELECT
            cohort_month,
            COUNT(*) AS cohort_size

        FROM user_cohorts

        GROUP BY cohort_month
    ),
    aggregated AS (
        SELECT
            cohort_month,
            month_offset,
            SUM(retained_users) AS retained_users

        FROM cohort_activity

        WHERE month_offset BETWEEN 0 AND p_max_months - 1

        GROUP BY cohort_month, month_offset
    )
    SELECT
        a.cohort_month,
        a.month_offset,
        s.cohort_size,
        a.retained_users,

        ROUND(
            a.retained_users::NUMERIC /
            NULLIF(s.cohort_size, 0) * 100,
            2
        )

    FROM aggregated a

    JOIN cohort_sizes s
        ON s.cohort_month = a.cohort_month;

END;
$$;

-- ============================================================
-- 17. Reporting views
-- ============================================================

CREATE OR REPLACE VIEW event_performance_report AS
SELECT
    d.event_name,

    COUNT(e.event_id) AS total_events,

    COUNT(DISTINCT e.user_id) AS unique_users,

    MIN(e.event_timestamp) AS first_occurrence,

    MAX(e.event_timestamp) AS last_occurrence,

    COUNT(*) FILTER (
        WHERE e.status = 'rejected'
    ) AS rejected_events

FROM event_definitions d

LEFT JOIN events e
    ON e.event_type_id = d.event_type_id

GROUP BY d.event_type_id, d.event_name;

CREATE OR REPLACE VIEW purchase_revenue_report AS
SELECT
    DATE_TRUNC(
        'month',
        e.event_timestamp
    )::DATE AS revenue_month,

    e.properties ->> 'currency' AS currency,

    COUNT(*) AS purchases,

    SUM(
        (e.properties ->> 'amount')::NUMERIC
    ) AS revenue,

    ROUND(
        AVG(
            (e.properties ->> 'amount')::NUMERIC
        ),
        2
    ) AS average_order_value

FROM events e

JOIN event_definitions d
    ON d.event_type_id = e.event_type_id

WHERE d.event_name = 'purchase'
  AND e.status = 'accepted'

GROUP BY
    DATE_TRUNC('month', e.event_timestamp),
    e.properties ->> 'currency';

CREATE OR REPLACE VIEW user_engagement_report AS
SELECT
    u.external_user_key,

    u.country,

    u.plan,

    COUNT(e.event_id) AS total_events,

    COUNT(DISTINCT e.session_id) AS observed_sessions,

    MAX(e.event_timestamp) AS last_activity

FROM users u

LEFT JOIN events e
    ON e.user_id = u.user_id

GROUP BY
    u.user_id,
    u.external_user_key,
    u.country,
    u.plan;

-- ============================================================
-- 18. Seed data
-- ============================================================

INSERT INTO users (
    external_user_key,
    country,
    plan,
    created_at
)
VALUES
    ('U001', 'IN', 'free', '2026-09-01 09:00:00+00'),
    ('U002', 'IN', 'premium', '2026-09-01 11:00:00+00'),
    ('U003', 'US', 'free', '2026-09-02 09:00:00+00'),
    ('U004', 'IN', 'premium', '2026-10-01 09:00:00+00'),
    ('U005', 'GB', 'free', '2026-10-02 09:00:00+00');

INSERT INTO anonymous_identities (
    anonymous_key,
    user_id,
    linked_at
)
SELECT
    'ANON-' || external_user_key,
    user_id,
    created_at
FROM users;

INSERT INTO sessions (
    session_key,
    user_id,
    started_at,
    last_event_at,
    source
)
SELECT
    (
        CASE external_user_key
            WHEN 'U001' THEN '10000000-0000-4000-8000-000000000001'
            WHEN 'U002' THEN '10000000-0000-4000-8000-000000000002'
            WHEN 'U003' THEN '10000000-0000-4000-8000-000000000003'
            WHEN 'U004' THEN '10000000-0000-4000-8000-000000000004'
            WHEN 'U005' THEN '10000000-0000-4000-8000-000000000005'
        END
    )::UUID,

    user_id,

    created_at,

    created_at + INTERVAL '20 minutes',

    'explicit'

FROM users;

-- ============================================================
-- 19. Transactional event ingestion
-- ============================================================

DO $$
DECLARE
    purchase_funnel_id BIGINT;
BEGIN
    SELECT funnel_id
    INTO purchase_funnel_id
    FROM funnels
    WHERE funnel_name = 'Product Purchase Funnel';

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000001',
        'U001',
        'signup',
        '2026-09-01 09:00:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000001'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000002',
        'U001',
        'product_view',
        '2026-09-01 09:05:00+00',
        '{"product_id":"P100","device_type":"mobile"}',
        '10000000-0000-4000-8000-000000000001'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000003',
        'U001',
        'add_to_cart',
        '2026-09-01 09:10:00+00',
        '{"product_id":"P100","quantity":1}',
        '10000000-0000-4000-8000-000000000001'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000004',
        'U001',
        'checkout_started',
        '2026-09-01 09:15:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000001'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000005',
        'U001',
        'purchase',
        '2026-09-01 09:20:00+00',
        '{"amount":1499,"currency":"INR"}',
        '10000000-0000-4000-8000-000000000001'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000006',
        'U002',
        'signup',
        '2026-09-01 11:00:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000002'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000007',
        'U002',
        'product_view',
        '2026-09-01 11:03:00+00',
        '{"product_id":"P200"}',
        '10000000-0000-4000-8000-000000000002'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000008',
        'U002',
        'add_to_cart',
        '2026-09-01 11:05:00+00',
        '{"product_id":"P200"}',
        '10000000-0000-4000-8000-000000000002'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000009',
        'U002',
        'checkout_started',
        '2026-09-01 11:08:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000002'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000010',
        'U002',
        'purchase',
        '2026-09-01 11:12:00+00',
        '{"amount":2499,"currency":"INR"}',
        '10000000-0000-4000-8000-000000000002'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000011',
        'U003',
        'signup',
        '2026-09-02 09:00:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000003'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000012',
        'U003',
        'product_view',
        '2026-09-02 09:04:00+00',
        '{"product_id":"P100"}',
        '10000000-0000-4000-8000-000000000003'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000013',
        'U003',
        'add_to_cart',
        '2026-09-02 09:06:00+00',
        '{"product_id":"P100"}',
        '10000000-0000-4000-8000-000000000003'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000014',
        'U004',
        'signup',
        '2026-10-01 09:00:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000004'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000015',
        'U004',
        'product_view',
        '2026-10-01 09:03:00+00',
        '{"product_id":"P300"}',
        '10000000-0000-4000-8000-000000000004'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000016',
        'U005',
        'signup',
        '2026-10-02 09:00:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000005'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000017',
        'U005',
        'product_view',
        '2026-10-02 09:02:00+00',
        '{"product_id":"P100"}',
        '10000000-0000-4000-8000-000000000005'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000018',
        'U005',
        'add_to_cart',
        '2026-10-02 09:04:00+00',
        '{"product_id":"P100"}',
        '10000000-0000-4000-8000-000000000005'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000019',
        'U005',
        'checkout_started',
        '2026-10-02 09:06:00+00',
        '{}',
        '10000000-0000-4000-8000-000000000005'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000020',
        'U005',
        'purchase',
        '2026-10-02 09:09:00+00',
        '{"amount":799,"currency":"GBP"}',
        '10000000-0000-4000-8000-000000000005'
    );

    -- Later-month engagement for retention analysis.
    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000021',
        'U001',
        'page_view',
        '2026-10-05 10:00:00+00',
        '{"page":"/dashboard"}',
        '10000000-0000-4000-8000-000000000001'
    );

    PERFORM ingest_event(
        '20000000-0000-4000-8000-000000000022',
        'U002',
        'page_view',
        '2026-10-06 10:00:00+00',
        '{"page":"/pricing"}',
        '10000000-0000-4000-8000-000000000002'
    );
END;
$$;

-- ============================================================
-- 20. Data-quality failure examples
-- ============================================================

-- Invalid purchases are rejected by the event validation trigger.
-- Run separately when testing error handling:
--
-- SELECT ingest_event(
--   '30000000-0000-4000-8000-000000000001',
--   'U001',
--   'purchase',
--   NOW(),
--   '{"amount":-100,"currency":"INR"}'
-- );
--
-- Unknown users are rejected by ingest_event.
--
-- Duplicate event keys are rejected transactionally.
--
-- Malformed property types are rejected by the trigger.

-- ============================================================
-- 21. Analytical retrieval queries
-- ============================================================

-- A. Event frequency and unique users.
SELECT
    event_name,
    total_events,
    unique_users
FROM event_performance_report
ORDER BY total_events DESC;

-- B. User-level engagement.
SELECT *
FROM user_engagement_report
ORDER BY total_events DESC;

-- C. Revenue by month and currency.
SELECT *
FROM purchase_revenue_report
ORDER BY revenue_month, currency;

-- D. Property-based analysis.
SELECT
    properties ->> 'product_id' AS product_id,
    COUNT(*) AS product_views,
    COUNT(DISTINCT user_id) AS unique_viewers
FROM events e
JOIN event_definitions d
    ON d.event_type_id = e.event_type_id
WHERE d.event_name = 'product_view'
GROUP BY properties ->> 'product_id'
ORDER BY product_views DESC;

-- E. Session retrieval.
SELECT *
FROM session_event_summary
ORDER BY user_id, session_start;

-- F. Conversion funnel evaluation.
SELECT *
FROM evaluate_funnel(
    (
        SELECT funnel_id
        FROM funnels
        WHERE funnel_name = 'Product Purchase Funnel'
    )
);

-- G. Cohort retention.
CALL refresh_cohort_retention(12);

SELECT
    cohort_month,
    month_offset,
    cohort_size,
    retained_users,
    retention_rate
FROM cohort_retention
ORDER BY cohort_month, month_offset;

-- H. Active users by plan.
SELECT
    u.plan,
    COUNT(DISTINCT e.user_id) AS active_users
FROM users u
JOIN events e
    ON e.user_id = u.user_id
GROUP BY u.plan
ORDER BY active_users DESC;

-- I. Event ingestion latency.
SELECT
    d.event_name,
    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (e.received_at - e.event_timestamp)
            )
        )::NUMERIC,
        2
    ) AS average_latency_seconds
FROM events e
JOIN event_definitions d
    ON d.event_type_id = e.event_type_id
GROUP BY d.event_name
ORDER BY average_latency_seconds DESC;

-- J. Purchase distribution.
SELECT
    properties ->> 'currency' AS currency,
    COUNT(*) AS purchases,
    MIN((properties ->> 'amount')::NUMERIC) AS minimum_order,
    MAX((properties ->> 'amount')::NUMERIC) AS maximum_order,
    ROUND(
        AVG((properties ->> 'amount')::NUMERIC),
        2
    ) AS average_order
FROM events e
JOIN event_definitions d
    ON d.event_type_id = e.event_type_id
WHERE d.event_name = 'purchase'
GROUP BY properties ->> 'currency';

-- K. Unlinked anonymous identities.
SELECT
    anonymous_key,
    first_seen_at
FROM anonymous_identities
WHERE user_id IS NULL
ORDER BY first_seen_at DESC;

-- L. Event audit.
SELECT
    event_id,
    operation,
    changed_at,
    changed_by
FROM event_audit
ORDER BY changed_at DESC;

-- ============================================================
-- 22. Transactional identity operation
-- ============================================================

DO $$
BEGIN
    CALL link_anonymous_identity(
        'ANON-U001',
        'U001'
    );
END;
$$;

COMMIT;

-- ============================================================
-- 23. Operational permissions
-- ============================================================

-- A production deployment should create separate ingestion and
-- reporting roles. The following statements are intentionally
-- provided as optional deployment operations:
--
-- CREATE ROLE analytics_ingestion NOLOGIN;
-- CREATE ROLE analytics_reader NOLOGIN;
--
-- GRANT USAGE ON SCHEMA product_analytics
-- TO analytics_ingestion, analytics_reader;
--
-- GRANT SELECT ON users, event_definitions,
-- property_definitions, funnels, funnel_steps
-- TO analytics_ingestion;
--
-- GRANT INSERT ON events TO analytics_ingestion;
--
-- GRANT SELECT ON events, sessions, anonymous_identities,
-- event_performance_report, purchase_revenue_report,
-- user_engagement_report, session_event_summary,
-- cohort_retention
-- TO analytics_reader;
--
-- Do not grant ingestion clients permission to alter event
-- definitions, schemas, or reporting policies.
