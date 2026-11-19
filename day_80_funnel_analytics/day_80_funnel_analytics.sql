/*
    FUNNEL ANALYTICS
    PostgreSQL 15+

    Features:
    - Event ingestion and deduplication
    - User-level funnel construction
    - Ordered event progression
    - Conversion windows
    - Cohort analysis
    - Channel and device segmentation
    - Drop-off measurement
    - Aggregated reporting
    - Materialized reporting
    - Data integrity enforcement
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS funnel_analytics;

SET search_path TO funnel_analytics, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE event_category AS ENUM (
    'visit',
    'product_view',
    'add_to_cart',
    'checkout',
    'purchase'
);

CREATE TYPE traffic_channel AS ENUM (
    'organic',
    'paid',
    'referral',
    'direct',
    'email'
);

CREATE TYPE device_category AS ENUM (
    'mobile',
    'desktop',
    'tablet'
);

CREATE TYPE funnel_status AS ENUM (
    'active',
    'paused',
    'archived'
);

-- ============================================================
-- 2. USERS
-- ============================================================

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_user_key VARCHAR(100) NOT NULL UNIQUE,
    country_code CHAR(2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_external_user_key
        CHECK (length(trim(external_user_key)) > 0),

    CONSTRAINT valid_country_code
        CHECK (country_code ~ '^[A-Z]{2}$')
);

-- ============================================================
-- 3. FUNNEL DEFINITIONS
-- ============================================================

CREATE TABLE funnels (
    funnel_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    funnel_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    conversion_window INTERVAL NOT NULL DEFAULT INTERVAL '7 days',
    status funnel_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_funnel_name
        CHECK (length(trim(funnel_name)) > 0),

    CONSTRAINT valid_conversion_window
        CHECK (
            conversion_window > INTERVAL '0 seconds'
            AND conversion_window <= INTERVAL '365 days'
        )
);

CREATE TABLE funnel_steps (
    step_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    funnel_id BIGINT NOT NULL
        REFERENCES funnels(funnel_id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    event_name event_category NOT NULL,

    CONSTRAINT unique_funnel_step_number
        UNIQUE (funnel_id, step_number),

    CONSTRAINT unique_funnel_step_name
        UNIQUE (funnel_id, step_name),

    CONSTRAINT valid_step_number
        CHECK (step_number > 0)
);

CREATE INDEX idx_funnel_steps_order
    ON funnel_steps(funnel_id, step_number);

-- ============================================================
-- 4. EVENT TRACKING
-- ============================================================

CREATE TABLE events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_key UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    event_name event_category NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    channel traffic_channel NOT NULL,
    device device_category NOT NULL,
    campaign VARCHAR(150),
    session_id UUID NOT NULL,
    revenue NUMERIC(14, 2) NOT NULL DEFAULT 0,
    properties JSONB NOT NULL DEFAULT '{}'::JSONB,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_revenue
        CHECK (revenue >= 0),

    CONSTRAINT valid_properties
        CHECK (jsonb_typeof(properties) = 'object')
);

-- User/time ordering supports sequential funnel processing.
CREATE INDEX idx_events_user_time
    ON events(user_id, occurred_at, event_id);

CREATE INDEX idx_events_type_time
    ON events(event_name, occurred_at);

CREATE INDEX idx_events_channel_device
    ON events(channel, device, occurred_at);

CREATE INDEX idx_events_session
    ON events(session_id, occurred_at);

CREATE INDEX idx_events_properties
    ON events USING GIN(properties);

-- ============================================================
-- 5. SAMPLE USERS
-- ============================================================

INSERT INTO users (
    external_user_key,
    country_code
)
VALUES
    ('CUSTOMER_001', 'IN'),
    ('CUSTOMER_002', 'US'),
    ('CUSTOMER_003', 'IN'),
    ('CUSTOMER_004', 'US'),
    ('CUSTOMER_005', 'IN'),
    ('CUSTOMER_006', 'US'),
    ('CUSTOMER_007', 'IN'),
    ('CUSTOMER_008', 'US');

-- ============================================================
-- 6. FUNNEL CONFIGURATION
-- ============================================================

INSERT INTO funnels (
    funnel_name,
    description,
    conversion_window
)
VALUES (
    'E-commerce Purchase Funnel',
    'Tracks users from initial visit through completed purchase.',
    INTERVAL '24 hours'
);

INSERT INTO funnel_steps (
    funnel_id,
    step_number,
    step_name,
    event_name
)
SELECT
    f.funnel_id,
    x.step_number,
    x.step_name,
    x.event_name::event_category
FROM funnels f
CROSS JOIN (
    VALUES
        (1, 'Website Visit', 'visit'),
        (2, 'Product View', 'product_view'),
        (3, 'Add to Cart', 'add_to_cart'),
        (4, 'Checkout', 'checkout'),
        (5, 'Purchase', 'purchase')
) AS x(step_number, step_name, event_name)
WHERE f.funnel_name = 'E-commerce Purchase Funnel';

-- ============================================================
-- 7. EVENT GENERATION
-- ============================================================

WITH journeys(user_number, events) AS (
    VALUES
        (1, ARRAY['visit','product_view','add_to_cart','checkout','purchase']::event_category[]),
        (2, ARRAY['visit','product_view','add_to_cart','checkout']::event_category[]),
        (3, ARRAY['visit','product_view']::event_category[]),
        (4, ARRAY['visit','product_view','add_to_cart','checkout','purchase']::event_category[]),
        (5, ARRAY['visit','product_view','add_to_cart']::event_category[]),
        (6, ARRAY['visit']::event_category[]),
        (7, ARRAY['visit','product_view','add_to_cart','checkout','purchase']::event_category[]),
        (8, ARRAY['visit','product_view','checkout']::event_category[])
),
expanded AS (
    SELECT
        j.user_number,
        e.event_name,
        e.step_number
    FROM journeys j
    CROSS JOIN LATERAL
        unnest(j.events) WITH ORDINALITY
        AS e(event_name, step_number)
)
INSERT INTO events (
    user_id,
    event_name,
    occurred_at,
    channel,
    device,
    campaign,
    session_id,
    revenue,
    properties
)
SELECT
    u.user_id,
    x.event_name,
    TIMESTAMPTZ '2026-11-01 09:00:00+00'
        + ((x.user_number - 1) * 15 + (x.step_number - 1) * 3)
            * INTERVAL '1 minute',

    CASE
        WHEN x.user_number IN (1, 3, 6) THEN 'organic'
        WHEN x.user_number IN (2, 4, 7) THEN 'paid'
        ELSE 'referral'
    END::traffic_channel,

    CASE
        WHEN x.user_number % 2 = 1 THEN 'mobile'
        ELSE 'desktop'
    END::device_category,

    'winter_2026',
    (
        '00000000-0000-0000-0000-' ||
        lpad(x.user_number::TEXT, 12, '0')
    )::UUID,

    CASE
        WHEN x.event_name = 'purchase' THEN 1499.00
        ELSE 0
    END,

    jsonb_build_object(
        'campaign_type', 'seasonal',
        'experiment', 'checkout_v1'
    )
FROM expanded x
JOIN users u
    ON u.external_user_key =
        'CUSTOMER_' || lpad(x.user_number::TEXT, 3, '0');

-- ============================================================
-- 8. DATA VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_event_payload()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.occurred_at > NOW() + INTERVAL '5 minutes' THEN
        RAISE EXCEPTION 'Event timestamp is too far in the future.';
    END IF;

    IF NEW.event_name <> 'purchase' AND NEW.revenue <> 0 THEN
        RAISE EXCEPTION
            'Revenue must be zero for non-purchase events.';
    END IF;

    IF NEW.event_name = 'purchase' AND NEW.revenue <= 0 THEN
        RAISE EXCEPTION
            'Purchase events must have positive revenue.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_event_payload
BEFORE INSERT OR UPDATE ON events
FOR EACH ROW
EXECUTE FUNCTION validate_event_payload();

-- ============================================================
-- 9. FUNNEL COHORT ANALYSIS FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_funnel(
    p_funnel_id BIGINT,
    p_start TIMESTAMPTZ DEFAULT NULL,
    p_end TIMESTAMPTZ DEFAULT NULL,
    p_channel traffic_channel DEFAULT NULL,
    p_device device_category DEFAULT NULL
)
RETURNS TABLE (
    step_number INTEGER,
    step_name VARCHAR,
    event_name event_category,
    users_reached BIGINT,
    previous_users BIGINT,
    dropped_users BIGINT,
    conversion_rate NUMERIC,
    drop_off_rate NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_window INTERVAL;
BEGIN
    IF p_start IS NOT NULL
       AND p_end IS NOT NULL
       AND p_start > p_end THEN
        RAISE EXCEPTION 'Start time must not exceed end time.';
    END IF;

    SELECT f.conversion_window
    INTO v_window
    FROM funnels f
    WHERE f.funnel_id = p_funnel_id
      AND f.status = 'active';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active funnel not found: %', p_funnel_id;
    END IF;

    IF (
        SELECT COUNT(*)
        FROM funnel_steps fs
        WHERE fs.funnel_id = p_funnel_id
    ) < 2 THEN
        RAISE EXCEPTION 'Funnel requires at least two steps.';
    END IF;

    RETURN QUERY
    WITH ordered_steps AS (
        SELECT
            fs.step_number,
            fs.step_name,
            fs.event_name
        FROM funnel_steps fs
        WHERE fs.funnel_id = p_funnel_id
    ),
    entry_events AS (
        SELECT
            e.user_id,
            MIN(e.occurred_at) AS entry_time
        FROM events e
        JOIN ordered_steps s
            ON s.event_name = e.event_name
           AND s.step_number = 1
        WHERE (p_start IS NULL OR e.occurred_at >= p_start)
          AND (p_end IS NULL OR e.occurred_at <= p_end)
          AND (p_channel IS NULL OR e.channel = p_channel)
          AND (p_device IS NULL OR e.device = p_device)
        GROUP BY e.user_id
    ),
    user_progress AS (
        SELECT
            entry.user_id,
            entry.entry_time,
            fs.step_number,
            fs.step_name,
            fs.event_name,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM events ev
                    WHERE ev.user_id = entry.user_id
                      AND ev.event_name = fs.event_name
                      AND ev.occurred_at >= entry.entry_time
                      AND ev.occurred_at <= entry.entry_time + v_window
                      AND NOT EXISTS (
                          SELECT 1
                          FROM funnel_steps prior_step
                          WHERE prior_step.funnel_id = p_funnel_id
                            AND prior_step.step_number < fs.step_number
                            AND NOT EXISTS (
                                SELECT 1
                                FROM events prior_event
                                WHERE prior_event.user_id = entry.user_id
                                  AND prior_event.event_name =
                                      prior_step.event_name
                                  AND prior_event.occurred_at >=
                                      entry.entry_time
                                  AND prior_event.occurred_at <
                                      ev.occurred_at
                                  AND prior_event.occurred_at <=
                                      entry.entry_time + v_window
                            )
                      )
                )
                THEN TRUE
                ELSE FALSE
            END AS completed
        FROM entry_events entry
        CROSS JOIN ordered_steps fs
    ),
    step_counts AS (
        SELECT
            up.step_number,
            up.step_name,
            up.event_name,
            COUNT(*) FILTER (
                WHERE up.completed
            )::BIGINT AS users_reached
        FROM user_progress up
        GROUP BY
            up.step_number,
            up.step_name,
            up.event_name
    ),
    metrics AS (
        SELECT
            sc.*,
            COALESCE(
                LAG(sc.users_reached) OVER (
                    ORDER BY sc.step_number
                ),
                sc.users_reached
            ) AS previous_users
        FROM step_counts sc
    )
    SELECT
        m.step_number,
        m.step_name::VARCHAR,
        m.event_name,
        m.users_reached,
        m.previous_users,
        m.previous_users - m.users_reached,
        ROUND(
            100.0 * m.users_reached /
            NULLIF(m.previous_users, 0),
            2
        ),
        ROUND(
            100.0 * (m.previous_users - m.users_reached) /
            NULLIF(m.previous_users, 0),
            2
        )
    FROM metrics m
    ORDER BY m.step_number;
END;
$$;

-- ============================================================
-- 10. FUNNEL REPORT VIEW
-- ============================================================

CREATE OR REPLACE VIEW funnel_summary AS
SELECT
    f.funnel_id,
    f.funnel_name,
    f.status,
    COUNT(DISTINCT fs.step_id) AS total_steps,
    MIN(fs.step_number) AS first_step,
    MAX(fs.step_number) AS last_step,
    f.conversion_window
FROM funnels f
LEFT JOIN funnel_steps fs
    ON fs.funnel_id = f.funnel_id
GROUP BY
    f.funnel_id,
    f.funnel_name,
    f.status,
    f.conversion_window;

-- ============================================================
-- 11. SEGMENTATION VIEW
-- ============================================================

CREATE OR REPLACE VIEW channel_performance AS
WITH user_entries AS (
    SELECT DISTINCT ON (e.user_id)
        e.user_id,
        e.channel,
        e.device,
        e.occurred_at
    FROM events e
    WHERE e.event_name = 'visit'
    ORDER BY e.user_id, e.occurred_at
),
user_conversions AS (
    SELECT
        ue.user_id,
        ue.channel,
        ue.device,
        EXISTS (
            SELECT 1
            FROM events purchase
            WHERE purchase.user_id = ue.user_id
              AND purchase.event_name = 'purchase'
              AND purchase.occurred_at >= ue.occurred_at
              AND purchase.occurred_at <=
                  ue.occurred_at + INTERVAL '24 hours'
        ) AS converted
    FROM user_entries ue
)
SELECT
    channel,
    device,
    COUNT(*) AS cohort_users,
    COUNT(*) FILTER (
        WHERE converted
    ) AS converted_users,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE converted) /
        NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate
FROM user_conversions
GROUP BY channel, device;

-- ============================================================
-- 12. AGGREGATE REVENUE REPORT
-- ============================================================

CREATE OR REPLACE VIEW revenue_by_channel AS
SELECT
    channel,
    COUNT(*) AS purchase_events,
    COUNT(DISTINCT user_id) AS purchasing_users,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM events
WHERE event_name = 'purchase'
GROUP BY channel;

-- ============================================================
-- 13. FUNNEL REPORT RETRIEVAL
-- ============================================================

SELECT *
FROM funnel_summary
ORDER BY funnel_id;

SELECT *
FROM calculate_funnel(
    (
        SELECT funnel_id
        FROM funnels
        WHERE funnel_name = 'E-commerce Purchase Funnel'
    ),
    TIMESTAMPTZ '2026-11-01 00:00:00+00',
    TIMESTAMPTZ '2026-11-02 00:00:00+00'
);

-- ============================================================
-- 14. CHANNEL SEGMENTATION
-- ============================================================

SELECT *
FROM channel_performance
ORDER BY channel, device;

-- ============================================================
-- 15. DEVICE CONVERSION AGGREGATION
-- ============================================================

SELECT
    device,
    COUNT(DISTINCT user_id) AS visitors,
    COUNT(DISTINCT user_id) FILTER (
        WHERE event_name = 'purchase'
    ) AS purchasing_users
FROM events
GROUP BY device
ORDER BY device;

-- ============================================================
-- 16. DROP-OFF IDENTIFICATION
-- ============================================================

WITH funnel_metrics AS (
    SELECT *
    FROM calculate_funnel(
        (
            SELECT funnel_id
            FROM funnels
            WHERE funnel_name = 'E-commerce Purchase Funnel'
        )
    )
)
SELECT
    step_number,
    step_name,
    users_reached,
    dropped_users,
    drop_off_rate
FROM funnel_metrics
WHERE dropped_users > 0
ORDER BY dropped_users DESC;

-- ============================================================
-- 17. USER-LEVEL CONVERSION VALIDATION
-- ============================================================

SELECT
    u.external_user_key,
    entry.occurred_at AS first_visit,
    purchase.occurred_at AS first_purchase,
    purchase.revenue,
    CASE
        WHEN purchase.occurred_at IS NULL THEN 'not_converted'
        WHEN purchase.occurred_at <=
             entry.occurred_at + INTERVAL '24 hours'
        THEN 'converted'
        ELSE 'outside_conversion_window'
    END AS conversion_status
FROM users u
JOIN LATERAL (
    SELECT e.occurred_at
    FROM events e
    WHERE e.user_id = u.user_id
      AND e.event_name = 'visit'
    ORDER BY e.occurred_at
    LIMIT 1
) entry ON TRUE
LEFT JOIN LATERAL (
    SELECT e.occurred_at, e.revenue
    FROM events e
    WHERE e.user_id = u.user_id
      AND e.event_name = 'purchase'
      AND e.occurred_at >= entry.occurred_at
    ORDER BY e.occurred_at
    LIMIT 1
) purchase ON TRUE
ORDER BY u.user_id;

-- ============================================================
-- 18. DATA QUALITY AUDIT
-- ============================================================

-- Detect users whose event timestamps are not sequentially ingested.
SELECT
    user_id,
    event_name,
    occurred_at,
    previous_event_time
FROM (
    SELECT
        user_id,
        event_name,
        occurred_at,
        LAG(occurred_at) OVER (
            PARTITION BY user_id
            ORDER BY occurred_at, event_id
        ) AS previous_event_time
    FROM events
) event_audit
WHERE occurred_at < previous_event_time;

-- Detect purchases with no preceding visit.
SELECT
    purchase.user_id,
    purchase.event_id,
    purchase.occurred_at
FROM events purchase
WHERE purchase.event_name = 'purchase'
  AND NOT EXISTS (
      SELECT 1
      FROM events visit
      WHERE visit.user_id = purchase.user_id
        AND visit.event_name = 'visit'
        AND visit.occurred_at <= purchase.occurred_at
  );

-- ============================================================
-- 19. MATERIALIZED PERFORMANCE REPORT
-- ============================================================

CREATE MATERIALIZED VIEW daily_funnel_events AS
SELECT
    DATE_TRUNC('day', occurred_at) AS event_day,
    event_name,
    channel,
    device,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(revenue) AS revenue
FROM events
GROUP BY
    DATE_TRUNC('day', occurred_at),
    event_name,
    channel,
    device;

CREATE UNIQUE INDEX idx_daily_funnel_events_unique
    ON daily_funnel_events(
        event_day,
        event_name,
        channel,
        device
    );

-- Refresh when reporting data needs to be updated.
REFRESH MATERIALIZED VIEW daily_funnel_events;

-- ============================================================
-- 20. STORED PROCEDURE FOR REPORT REFRESH
-- ============================================================

CREATE OR REPLACE PROCEDURE refresh_funnel_reporting()
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW daily_funnel_events;
END;
$$;

-- ============================================================
-- 21. TRANSACTIONAL EVENT INGESTION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION ingest_event(
    p_event_key UUID,
    p_user_id BIGINT,
    p_event_name event_category,
    p_occurred_at TIMESTAMPTZ,
    p_channel traffic_channel,
    p_device device_category,
    p_session_id UUID,
    p_revenue NUMERIC DEFAULT 0
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO events (
        event_key,
        user_id,
        event_name,
        occurred_at,
        channel,
        device,
        session_id,
        revenue
    )
    VALUES (
        p_event_key,
        p_user_id,
        p_event_name,
        p_occurred_at,
        p_channel,
        p_device,
        p_session_id,
        p_revenue
    )
    ON CONFLICT (event_key) DO NOTHING;

    RETURN FOUND;
END;
$$;

-- Example of idempotent ingestion.
-- The transaction rolls back if any operation fails.

DO $$
DECLARE
    v_user_id BIGINT;
BEGIN
    SELECT user_id
    INTO v_user_id
    FROM users
    WHERE external_user_key = 'CUSTOMER_001';

    PERFORM ingest_event(
        '11111111-1111-1111-1111-111111111111',
        v_user_id,
        'visit',
        NOW(),
        'organic',
        'mobile',
        '22222222-2222-2222-2222-222222222222',
        0
    );
END;
$$;

COMMIT;

-- ============================================================
-- 22. FINAL REPORTING QUERIES
-- ============================================================

SELECT *
FROM funnel_analytics.funnel_summary;

SELECT *
FROM funnel_analytics.channel_performance;

SELECT *
FROM funnel_analytics.revenue_by_channel;

SELECT
    event_day,
    event_name,
    channel,
    unique_users,
    event_count,
    revenue
FROM funnel_analytics.daily_funnel_events
ORDER BY event_day, event_name, channel;
