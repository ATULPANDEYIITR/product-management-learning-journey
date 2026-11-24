-- ============================================================
-- PRODUCT DASHBOARD MANAGEMENT AND ANALYTICS
-- PostgreSQL 14+
--
-- Covers:
-- Metric hierarchy, definitions, observations, dimensions,
-- aggregation, dashboard configuration, access control,
-- visualization data, alert policies, alert lifecycle,
-- reporting, and metric quality.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_analytics;

SET search_path TO product_analytics, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE metric_category AS ENUM (
    'north_star',
    'business',
    'product',
    'engagement',
    'reliability'
);

CREATE TYPE metric_type AS ENUM (
    'count',
    'percentage',
    'currency',
    'duration',
    'ratio'
);

CREATE TYPE aggregation_method AS ENUM (
    'sum',
    'average',
    'minimum',
    'maximum',
    'last',
    'distinct_count'
);

CREATE TYPE dashboard_role AS ENUM (
    'viewer',
    'analyst',
    'admin'
);

CREATE TYPE alert_severity AS ENUM (
    'info',
    'warning',
    'critical'
);

CREATE TYPE alert_status AS ENUM (
    'active',
    'acknowledged',
    'resolved'
);

CREATE TYPE visualization_type AS ENUM (
    'number',
    'line',
    'bar',
    'area',
    'pie',
    'table',
    'gauge'
);

CREATE TYPE comparison_period AS ENUM (
    'previous_period',
    'previous_day',
    'previous_week',
    'previous_month',
    'target'
);

-- ============================================================
-- 2. USERS AND REPOSITORY-LEVEL DASHBOARD OWNERSHIP
-- ============================================================

CREATE TABLE dashboard_users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL UNIQUE,
    product_owner BIGINT REFERENCES dashboard_users(user_id),
    business_unit VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. METRIC DEFINITIONS
-- ============================================================

CREATE TABLE metric_definitions (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id BIGINT NOT NULL
        REFERENCES products(product_id),

    metric_key VARCHAR(120) NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,

    category metric_category NOT NULL,
    data_type metric_type NOT NULL,
    unit VARCHAR(30) NOT NULL,

    aggregation aggregation_method NOT NULL,

    higher_is_better BOOLEAN NOT NULL,

    target_value NUMERIC(20, 6),
    warning_threshold NUMERIC(20, 6),
    critical_threshold NUMERIC(20, 6),

    owner_id BIGINT REFERENCES dashboard_users(user_id),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_product_metric
        UNIQUE(product_id, metric_key),

    CONSTRAINT ck_metric_name
        CHECK (LENGTH(TRIM(metric_name)) > 0),

    CONSTRAINT ck_percentage_unit
        CHECK (
            data_type <> 'percentage'
            OR unit = '%'
        ),

    CONSTRAINT ck_finite_target
        CHECK (
            target_value IS NULL
            OR target_value NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        ),

    CONSTRAINT ck_finite_warning
        CHECK (
            warning_threshold IS NULL
            OR warning_threshold NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        ),

    CONSTRAINT ck_finite_critical
        CHECK (
            critical_threshold IS NULL
            OR critical_threshold NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        ),

    CONSTRAINT ck_thresholds_differ
        CHECK (
            warning_threshold IS NULL
            OR critical_threshold IS NULL
            OR warning_threshold <> critical_threshold
        )
);

CREATE INDEX idx_metric_category
    ON metric_definitions(category, is_active);

CREATE INDEX idx_metric_owner
    ON metric_definitions(owner_id);

-- ============================================================
-- 4. DIMENSIONS AND METRIC OBSERVATIONS
-- ============================================================

CREATE TABLE metric_dimensions (
    dimension_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dimension_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE metric_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    observed_value NUMERIC(20, 6) NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL,

    entity_key VARCHAR(150),

    dimensions JSONB NOT NULL DEFAULT '{}'::JSONB,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_observation_value
        CHECK (
            observed_value NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        ),

    CONSTRAINT ck_dimensions_object
        CHECK (JSONB_TYPEOF(dimensions) = 'object')
);

CREATE INDEX idx_observation_metric_time
    ON metric_observations(metric_id, observed_at DESC);

CREATE INDEX idx_observation_entity
    ON metric_observations(entity_key)
    WHERE entity_key IS NOT NULL;

CREATE INDEX idx_observation_dimensions
    ON metric_observations
    USING GIN(dimensions);

-- ============================================================
-- 5. OBSERVATION VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_metric_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    definition metric_definitions%ROWTYPE;
BEGIN
    SELECT *
    INTO definition
    FROM metric_definitions
    WHERE metric_id = NEW.metric_id
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Metric % does not exist or is inactive',
            NEW.metric_id;
    END IF;

    IF definition.data_type = 'percentage'
       AND (
           NEW.observed_value < 0
           OR NEW.observed_value > 100
       )
    THEN
        RAISE EXCEPTION
            'Percentage value must be between 0 and 100';
    END IF;

    IF definition.data_type IN ('count', 'duration')
       AND NEW.observed_value < 0
    THEN
        RAISE EXCEPTION
            'Count and duration cannot be negative';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_metric_observation
BEFORE INSERT OR UPDATE
ON metric_observations
FOR EACH ROW
EXECUTE FUNCTION validate_metric_observation();

-- ============================================================
-- 6. DASHBOARD CONFIGURATION
-- ============================================================

CREATE TABLE dashboards (
    dashboard_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id BIGINT NOT NULL
        REFERENCES products(product_id),

    dashboard_name VARCHAR(200) NOT NULL,
    description TEXT,

    refresh_interval_seconds INTEGER NOT NULL DEFAULT 60,

    is_published BOOLEAN NOT NULL DEFAULT FALSE,

    created_by BIGINT NOT NULL
        REFERENCES dashboard_users(user_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_refresh_interval
        CHECK (refresh_interval_seconds >= 5),

    CONSTRAINT uq_dashboard_product
        UNIQUE(product_id, dashboard_name)
);

CREATE TABLE dashboard_permissions (
    dashboard_id BIGINT NOT NULL
        REFERENCES dashboards(dashboard_id)
        ON DELETE CASCADE,

    user_id BIGINT NOT NULL
        REFERENCES dashboard_users(user_id)
        ON DELETE CASCADE,

    role dashboard_role NOT NULL,

    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY(dashboard_id, user_id)
);

CREATE TABLE dashboard_widgets (
    widget_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dashboard_id BIGINT NOT NULL
        REFERENCES dashboards(dashboard_id)
        ON DELETE CASCADE,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    visualization visualization_type NOT NULL,

    position_x INTEGER NOT NULL DEFAULT 0,
    position_y INTEGER NOT NULL DEFAULT 0,

    width INTEGER NOT NULL DEFAULT 4,
    height INTEGER NOT NULL DEFAULT 3,

    display_order INTEGER NOT NULL DEFAULT 0,

    show_target BOOLEAN NOT NULL DEFAULT TRUE,
    show_comparison BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT ck_widget_dimensions
        CHECK (
            width BETWEEN 1 AND 12
            AND height BETWEEN 1 AND 20
        ),

    CONSTRAINT uq_dashboard_metric_widget
        UNIQUE(dashboard_id, metric_id)
);

CREATE INDEX idx_dashboard_widgets_order
    ON dashboard_widgets(dashboard_id, display_order);

-- ============================================================
-- 7. ALERT POLICIES AND ALERT EVENTS
-- ============================================================

CREATE TABLE alert_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    warning_threshold NUMERIC(20, 6),
    critical_threshold NUMERIC(20, 6),

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    evaluation_interval_seconds INTEGER NOT NULL DEFAULT 60,

    cooldown_seconds INTEGER NOT NULL DEFAULT 300,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_metric_alert_policy
        UNIQUE(metric_id),

    CONSTRAINT ck_alert_interval
        CHECK (
            evaluation_interval_seconds >= 5
            AND cooldown_seconds >= 0
        ),

    CONSTRAINT ck_alert_threshold_difference
        CHECK (
            warning_threshold IS NULL
            OR critical_threshold IS NULL
            OR warning_threshold <> critical_threshold
        )
);

CREATE TABLE alert_events (
    alert_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_id BIGINT NOT NULL
        REFERENCES alert_policies(policy_id),

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    severity alert_severity NOT NULL,

    observed_value NUMERIC(20, 6) NOT NULL,

    message TEXT NOT NULL,

    status alert_status NOT NULL DEFAULT 'active',

    fingerprint VARCHAR(255) NOT NULL,

    first_triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    last_triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    acknowledged_by BIGINT
        REFERENCES dashboard_users(user_id),

    acknowledged_at TIMESTAMPTZ,

    resolved_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_active_alert_fingerprint
    ON alert_events(fingerprint)
    WHERE status = 'active';

CREATE INDEX idx_alert_metric_time
    ON alert_events(metric_id, first_triggered_at DESC);

-- ============================================================
-- 8. STATUS AND DATA QUALITY AUDIT
-- ============================================================

CREATE TABLE metric_quality_checks (
    quality_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    expected_count INTEGER,

    actual_count INTEGER,

    missing_count INTEGER,

    duplicate_count INTEGER,

    quality_status VARCHAR(20) NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    CONSTRAINT ck_quality_status
        CHECK (
            quality_status IN (
                'passed',
                'warning',
                'failed'
            )
        ),

    CONSTRAINT ck_quality_counts
        CHECK (
            COALESCE(expected_count, 0) >= 0
            AND COALESCE(actual_count, 0) >= 0
            AND COALESCE(missing_count, 0) >= 0
            AND COALESCE(duplicate_count, 0) >= 0
        )
);

-- ============================================================
-- 9. CENTRALIZED AGGREGATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION aggregate_metric(
    p_metric_id BIGINT,
    p_start TIMESTAMPTZ,
    p_end TIMESTAMPTZ,
    p_dimensions JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    metric_id BIGINT,
    metric_name VARCHAR,
    current_value NUMERIC,
    observation_count BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    method aggregation_method;
    selected_value NUMERIC;
BEGIN
    IF p_start IS NULL OR p_end IS NULL
       OR p_start >= p_end
    THEN
        RAISE EXCEPTION 'Invalid aggregation time window';
    END IF;

    IF p_dimensions IS NULL
       OR JSONB_TYPEOF(p_dimensions) <> 'object'
    THEN
        RAISE EXCEPTION 'Dimensions must be a JSON object';
    END IF;

    SELECT aggregation
    INTO method
    FROM metric_definitions
    WHERE metric_definitions.metric_id = p_metric_id
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown or inactive metric';
    END IF;

    SELECT
        CASE method
            WHEN 'sum' THEN SUM(o.observed_value)
            WHEN 'average' THEN AVG(o.observed_value)
            WHEN 'minimum' THEN MIN(o.observed_value)
            WHEN 'maximum' THEN MAX(o.observed_value)
            WHEN 'last' THEN (
                SELECT latest.observed_value
                FROM metric_observations latest
                WHERE latest.metric_id = p_metric_id
                  AND latest.observed_at >= p_start
                  AND latest.observed_at < p_end
                  AND latest.dimensions @> p_dimensions
                ORDER BY latest.observed_at DESC,
                         latest.observation_id DESC
                LIMIT 1
            )
            WHEN 'distinct_count' THEN (
                SELECT COUNT(DISTINCT entity_key)::NUMERIC
                FROM metric_observations distinct_observations
                WHERE distinct_observations.metric_id = p_metric_id
                  AND distinct_observations.observed_at >= p_start
                  AND distinct_observations.observed_at < p_end
                  AND distinct_observations.dimensions @> p_dimensions
            )
        END,
        COUNT(*)
    INTO selected_value, observation_count
    FROM metric_observations o
    WHERE o.metric_id = p_metric_id
      AND o.observed_at >= p_start
      AND o.observed_at < p_end
      AND o.dimensions @> p_dimensions;

    SELECT
        p_metric_id,
        md.metric_name,
        selected_value,
        observation_count
    INTO metric_id, metric_name, current_value, observation_count
    FROM metric_definitions md
    WHERE md.metric_id = p_metric_id;

    RETURN NEXT;
END;
$$;

-- ============================================================
-- 10. ALERT EVALUATION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE evaluate_metric_alert(
    p_metric_id BIGINT,
    p_observed_value NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    policy alert_policies%ROWTYPE;
    definition metric_definitions%ROWTYPE;
    calculated_severity alert_severity;
    alert_fingerprint VARCHAR(255);
BEGIN
    SELECT *
    INTO policy
    FROM alert_policies
    WHERE metric_id = p_metric_id
      AND enabled = TRUE;

    IF NOT FOUND THEN
        RAISE NOTICE 'No enabled alert policy for metric %',
            p_metric_id;
        RETURN;
    END IF;

    SELECT *
    INTO definition
    FROM metric_definitions
    WHERE metric_id = p_metric_id;

    IF definition.higher_is_better THEN
        IF policy.critical_threshold IS NOT NULL
           AND p_observed_value < policy.critical_threshold
        THEN
            calculated_severity := 'critical';
        ELSIF policy.warning_threshold IS NOT NULL
           AND p_observed_value < policy.warning_threshold
        THEN
            calculated_severity := 'warning';
        ELSE
            calculated_severity := NULL;
        END IF;
    ELSE
        IF policy.critical_threshold IS NOT NULL
           AND p_observed_value > policy.critical_threshold
        THEN
            calculated_severity := 'critical';
        ELSIF policy.warning_threshold IS NOT NULL
           AND p_observed_value > policy.warning_threshold
        THEN
            calculated_severity := 'warning';
        ELSE
            calculated_severity := NULL;
        END IF;
    END IF;

    alert_fingerprint :=
        'metric:' || p_metric_id || ':'
        || COALESCE(calculated_severity::TEXT, 'resolved');

    IF calculated_severity IS NULL THEN
        UPDATE alert_events
        SET status = 'resolved',
            resolved_at = NOW()
        WHERE metric_id = p_metric_id
          AND status = 'active';

        RETURN;
    END IF;

    -- Prevent duplicate active alerts for the same metric and severity.
    INSERT INTO alert_events (
        policy_id,
        metric_id,
        severity,
        observed_value,
        message,
        fingerprint
    )
    VALUES (
        policy.policy_id,
        p_metric_id,
        calculated_severity,
        p_observed_value,
        'Metric threshold breached: '
            || definition.metric_name,
        alert_fingerprint
    )
    ON CONFLICT (fingerprint)
    WHERE status = 'active'
    DO UPDATE SET
        observed_value = EXCLUDED.observed_value,
        last_triggered_at = NOW();

END;
$$;

-- ============================================================
-- 11. APPROVAL AND ACCESS VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION has_dashboard_access(
    p_dashboard_id BIGINT,
    p_user_id BIGINT,
    p_required_role dashboard_role
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM dashboard_permissions permission
        JOIN dashboard_users user_account
          ON user_account.user_id = permission.user_id
        WHERE permission.dashboard_id = p_dashboard_id
          AND permission.user_id = p_user_id
          AND user_account.is_active = TRUE
          AND CASE permission.role
              WHEN 'viewer' THEN 1
              WHEN 'analyst' THEN 2
              WHEN 'admin' THEN 3
          END >= CASE p_required_role
              WHEN 'viewer' THEN 1
              WHEN 'analyst' THEN 2
              WHEN 'admin' THEN 3
          END
    );
$$;

-- ============================================================
-- 12. DASHBOARD REPORTING VIEW
-- ============================================================

CREATE OR REPLACE VIEW dashboard_metric_catalog AS
SELECT
    d.dashboard_id,
    d.dashboard_name,
    p.product_name,
    w.widget_id,
    w.display_order,
    w.visualization,
    w.position_x,
    w.position_y,
    w.width,
    w.height,
    m.metric_id,
    m.metric_key,
    m.metric_name,
    m.category,
    m.data_type,
    m.unit,
    m.aggregation,
    m.target_value,
    m.higher_is_better,
    m.owner_id
FROM dashboards d
JOIN products p
    ON p.product_id = d.product_id
JOIN dashboard_widgets w
    ON w.dashboard_id = d.dashboard_id
JOIN metric_definitions m
    ON m.metric_id = w.metric_id
WHERE m.is_active = TRUE;

-- ============================================================
-- 13. LATEST METRIC OBSERVATIONS
-- ============================================================

CREATE OR REPLACE VIEW latest_metric_values AS
SELECT DISTINCT ON (metric_id)
    metric_id,
    observed_value,
    observed_at,
    dimensions
FROM metric_observations
ORDER BY metric_id,
         observed_at DESC,
         observation_id DESC;

-- ============================================================
-- 14. SAMPLE DATA
-- ============================================================

INSERT INTO dashboard_users (
    username,
    email
)
VALUES
    ('administrator', 'admin@example.com'),
    ('analyst', 'analyst@example.com'),
    ('executive', 'executive@example.com');

INSERT INTO products (
    product_name,
    product_owner,
    business_unit
)
VALUES (
    'Market Intelligence Platform',
    (SELECT user_id
     FROM dashboard_users
     WHERE username = 'administrator'),
    'Digital Products'
);

INSERT INTO metric_definitions (
    product_id,
    metric_key,
    metric_name,
    description,
    category,
    data_type,
    unit,
    aggregation,
    higher_is_better,
    target_value,
    warning_threshold,
    critical_threshold,
    owner_id
)
SELECT
    p.product_id,
    data.metric_key,
    data.metric_name,
    data.description,
    data.category::metric_category,
    data.data_type::metric_type,
    data.unit,
    data.aggregation::aggregation_method,
    data.higher_is_better,
    data.target_value,
    data.warning_threshold,
    data.critical_threshold,
    u.user_id
FROM products p
CROSS JOIN dashboard_users u
CROSS JOIN (
    VALUES
    (
        'monthly_active_users',
        'Monthly Active Users',
        'Distinct active users in the reporting period.',
        'north_star',
        'count',
        'users',
        'last',
        TRUE,
        50000::NUMERIC,
        40000::NUMERIC,
        30000::NUMERIC
    ),
    (
        'conversion_rate',
        'Conversion Rate',
        'Percentage of visitors who complete purchases.',
        'business',
        'percentage',
        '%',
        'average',
        TRUE,
        5::NUMERIC,
        3.5::NUMERIC,
        2::NUMERIC
    ),
    (
        'daily_revenue',
        'Daily Revenue',
        'Recognized daily revenue.',
        'business',
        'currency',
        'INR',
        'sum',
        TRUE,
        500000::NUMERIC,
        NULL::NUMERIC,
        NULL::NUMERIC
    ),
    (
        'crash_rate',
        'Application Crash Rate',
        'Percentage of sessions ending in a crash.',
        'reliability',
        'percentage',
        '%',
        'average',
        FALSE,
        0.5::NUMERIC,
        1::NUMERIC,
        2::NUMERIC
    ),
    (
        'average_session_duration',
        'Average Session Duration',
        'Average duration of user sessions.',
        'engagement',
        'duration',
        'seconds',
        'average',
        TRUE,
        300::NUMERIC,
        NULL::NUMERIC,
        NULL::NUMERIC
    )
) AS data(
    metric_key,
    metric_name,
    description,
    category,
    data_type,
    unit,
    aggregation,
    higher_is_better,
    target_value,
    warning_threshold,
    critical_threshold
)
WHERE u.username = 'analyst';

INSERT INTO dashboards (
    product_id,
    dashboard_name,
    description,
    refresh_interval_seconds,
    is_published,
    created_by
)
SELECT
    p.product_id,
    'Product Executive Dashboard',
    'Executive view of product performance and reliability.',
    60,
    TRUE,
    u.user_id
FROM products p
CROSS JOIN dashboard_users u
WHERE u.username = 'administrator';

INSERT INTO dashboard_permissions (
    dashboard_id,
    user_id,
    role
)
SELECT
    d.dashboard_id,
    u.user_id,
    CASE u.username
        WHEN 'administrator' THEN 'admin'::dashboard_role
        WHEN 'analyst' THEN 'analyst'::dashboard_role
        ELSE 'viewer'::dashboard_role
    END
FROM dashboards d
CROSS JOIN dashboard_users u;

INSERT INTO dashboard_widgets (
    dashboard_id,
    metric_id,
    visualization,
    position_x,
    position_y,
    width,
    height,
    display_order
)
SELECT
    d.dashboard_id,
    m.metric_id,
    CASE m.category
        WHEN 'north_star' THEN 'number'::visualization_type
        WHEN 'business' THEN 'line'::visualization_type
        WHEN 'reliability' THEN 'gauge'::visualization_type
        ELSE 'bar'::visualization_type
    END,
    0,
    ROW_NUMBER() OVER (
        ORDER BY m.metric_id
    )::INTEGER - 1,
    6,
    3,
    ROW_NUMBER() OVER (
        ORDER BY m.metric_id
    )::INTEGER
FROM dashboards d
JOIN metric_definitions m
    ON m.product_id = d.product_id;

INSERT INTO alert_policies (
    metric_id,
    warning_threshold,
    critical_threshold,
    enabled,
    evaluation_interval_seconds,
    cooldown_seconds
)
SELECT
    metric_id,
    warning_threshold,
    critical_threshold,
    TRUE,
    60,
    300
FROM metric_definitions
WHERE warning_threshold IS NOT NULL
   OR critical_threshold IS NOT NULL;

-- ============================================================
-- 15. SAMPLE OBSERVATIONS
-- ============================================================

INSERT INTO metric_observations (
    metric_id,
    observed_value,
    observed_at,
    entity_key,
    dimensions
)
SELECT
    m.metric_id,
    sample.observed_value,
    sample.observed_at,
    sample.entity_key,
    sample.dimensions::JSONB
FROM metric_definitions m
CROSS JOIN LATERAL (
    VALUES
    (
        CASE m.metric_key
            WHEN 'monthly_active_users' THEN 35000
            WHEN 'conversion_rate' THEN 4.1
            WHEN 'daily_revenue' THEN 420000
            WHEN 'crash_rate' THEN 0.7
            WHEN 'average_session_duration' THEN 280
        END::NUMERIC,
        NOW() - INTERVAL '2 hours',
        'previous-period',
        '{"platform":"all","region":"india"}'
    ),
    (
        CASE m.metric_key
            WHEN 'monthly_active_users' THEN 38000
            WHEN 'conversion_rate' THEN 3.2
            WHEN 'daily_revenue' THEN 390000
            WHEN 'crash_rate' THEN 2.4
            WHEN 'average_session_duration' THEN 250
        END::NUMERIC,
        NOW() - INTERVAL '30 minutes',
        'current-period',
        '{"platform":"all","region":"india"}'
    )
) AS sample(
    observed_value,
    observed_at,
    entity_key,
    dimensions
);

-- ============================================================
-- 16. SAMPLE QUALITY AUDIT
-- ============================================================

INSERT INTO metric_quality_checks (
    metric_id,
    expected_count,
    actual_count,
    missing_count,
    duplicate_count,
    quality_status,
    details
)
SELECT
    m.metric_id,
    2,
    COUNT(o.observation_id)::INTEGER,
    GREATEST(
        2 - COUNT(o.observation_id)::INTEGER,
        0
    ),
    0,
    CASE
        WHEN COUNT(o.observation_id) >= 2 THEN 'passed'
        WHEN COUNT(o.observation_id) = 1 THEN 'warning'
        ELSE 'failed'
    END,
    JSONB_BUILD_OBJECT(
        'audit_type', 'sample_completeness_check'
    )
FROM metric_definitions m
LEFT JOIN metric_observations o
    ON o.metric_id = m.metric_id
GROUP BY m.metric_id;

-- ============================================================
-- 17. RETRIEVAL: DASHBOARD LAYOUT
-- ============================================================

SELECT *
FROM dashboard_metric_catalog
ORDER BY dashboard_id, display_order;

-- ============================================================
-- 18. RETRIEVAL: LATEST VALUES
-- ============================================================

SELECT
    m.metric_name,
    l.observed_value,
    m.unit,
    l.observed_at
FROM latest_metric_values l
JOIN metric_definitions m
    ON m.metric_id = l.metric_id
ORDER BY m.category, m.metric_name;

-- ============================================================
-- 19. AGGREGATION: METRIC VALUES
-- ============================================================

SELECT *
FROM aggregate_metric(
    (
        SELECT metric_id
        FROM metric_definitions
        WHERE metric_key = 'conversion_rate'
    ),
    NOW() - INTERVAL '24 hours',
    NOW(),
    '{"platform":"all"}'::JSONB
);

-- ============================================================
-- 20. COMPARISON: CURRENT AND PREVIOUS PERIOD
-- ============================================================

WITH metric_periods AS (
    SELECT
        m.metric_id,
        m.metric_name,
        m.unit,
        m.aggregation,

        current_period.current_value,

        previous_period.previous_value

    FROM metric_definitions m

    CROSS JOIN LATERAL (
        SELECT current_value
        FROM aggregate_metric(
            m.metric_id,
            NOW() - INTERVAL '1 hour',
            NOW(),
            '{}'::JSONB
        )
    ) current_period

    CROSS JOIN LATERAL (
        SELECT current_value AS previous_value
        FROM aggregate_metric(
            m.metric_id,
            NOW() - INTERVAL '2 hours',
            NOW() - INTERVAL '1 hour',
            '{}'::JSONB
        )
    ) previous_period
    WHERE m.is_active = TRUE
)
SELECT
    metric_name,
    current_value,
    previous_value,
    unit,
    CASE
        WHEN previous_value IS NULL
             OR previous_value = 0
        THEN NULL
        ELSE ROUND(
            (
                (current_value - previous_value)
                / ABS(previous_value)
            ) * 100,
            2
        )
    END AS percentage_change
FROM metric_periods
ORDER BY metric_name;

-- ============================================================
-- 21. EVALUATION: ALERT PROCESSING
-- ============================================================

DO $$
DECLARE
    metric_record RECORD;
    latest_value NUMERIC;
BEGIN
    FOR metric_record IN
        SELECT metric_id, metric_name
        FROM metric_definitions
        WHERE is_active = TRUE
    LOOP
        SELECT observed_value
        INTO latest_value
        FROM metric_observations
        WHERE metric_id = metric_record.metric_id
        ORDER BY observed_at DESC, observation_id DESC
        LIMIT 1;

        IF FOUND THEN
            CALL evaluate_metric_alert(
                metric_record.metric_id,
                latest_value
            );
        END IF;
    END LOOP;
END;
$$;

-- ============================================================
-- 22. REPORTING: ACTIVE ALERTS
-- ============================================================

SELECT
    a.alert_id,
    m.metric_name,
    a.severity,
    a.observed_value,
    a.status,
    a.first_triggered_at,
    a.last_triggered_at
FROM alert_events a
JOIN metric_definitions m
    ON m.metric_id = a.metric_id
WHERE a.status = 'active'
ORDER BY
    CASE a.severity
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        ELSE 3
    END,
    a.first_triggered_at DESC;

-- ============================================================
-- 23. REPORTING: METRIC PERFORMANCE BY CATEGORY
-- ============================================================

SELECT
    category,
    COUNT(*) AS total_metrics,
    COUNT(*) FILTER (
        WHERE target_value IS NOT NULL
    ) AS metrics_with_targets,
    COUNT(*) FILTER (
        WHERE is_active
    ) AS active_metrics
FROM metric_definitions
GROUP BY category
ORDER BY category;

-- ============================================================
-- 24. REPORTING: DATA QUALITY
-- ============================================================

SELECT
    m.metric_name,
    q.quality_status,
    q.expected_count,
    q.actual_count,
    q.missing_count,
    q.duplicate_count,
    q.checked_at
FROM metric_quality_checks q
JOIN metric_definitions m
    ON m.metric_id = q.metric_id
ORDER BY q.checked_at DESC;

-- ============================================================
-- 25. ELIGIBILITY: DASHBOARD ACCESS
-- ============================================================

SELECT
    d.dashboard_name,
    u.username,
    p.role,
    has_dashboard_access(
        d.dashboard_id,
        u.user_id,
        'viewer'
    ) AS can_view,
    has_dashboard_access(
        d.dashboard_id,
        u.user_id,
        'analyst'
    ) AS can_analyze,
    has_dashboard_access(
        d.dashboard_id,
        u.user_id,
        'admin'
    ) AS can_administer
FROM dashboards d
CROSS JOIN dashboard_users u
LEFT JOIN dashboard_permissions p
    ON p.dashboard_id = d.dashboard_id
   AND p.user_id = u.user_id
ORDER BY d.dashboard_id, u.username;

-- ============================================================
-- 26. VALIDATION: INVALID PERCENTAGE TEST
-- Expected to fail inside the exception block.
-- ============================================================

DO $$
DECLARE
    percentage_metric_id BIGINT;
BEGIN
    SELECT metric_id
    INTO percentage_metric_id
    FROM metric_definitions
    WHERE metric_key = 'conversion_rate';

    BEGIN
        INSERT INTO metric_observations (
            metric_id,
            observed_value,
            observed_at,
            dimensions
        )
        VALUES (
            percentage_metric_id,
            150,
            NOW(),
            '{}'::JSONB
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Invalid observation correctly rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 27. VALIDATION: INACTIVE METRIC TEST
-- ============================================================

DO $$
DECLARE
    invalid_metric_id BIGINT := -1;
BEGIN
    BEGIN
        PERFORM *
        FROM aggregate_metric(
            invalid_metric_id,
            NOW() - INTERVAL '1 hour',
            NOW(),
            '{}'::JSONB
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Unknown metric correctly rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 28. ACKNOWLEDGEMENT WORKFLOW
-- ============================================================

-- Demonstrates an authorized administrator acknowledging
-- the active alerts belonging to a metric.

UPDATE alert_events a
SET status = 'acknowledged',
    acknowledged_by = u.user_id,
    acknowledged_at = NOW()
FROM dashboard_users u
WHERE u.username = 'administrator'
  AND a.metric_id = (
      SELECT metric_id
      FROM metric_definitions
      WHERE metric_key = 'crash_rate'
  )
  AND a.status = 'active'
  AND has_dashboard_access(
      (
          SELECT dashboard_id
          FROM dashboards
          WHERE dashboard_name =
              'Product Executive Dashboard'
      ),
      u.user_id,
      'admin'
  );

-- ============================================================
-- 29. TRANSACTIONAL ALERT RESOLUTION
-- ============================================================

SAVEPOINT before_recovery;

-- A recovery observation can resolve an existing alert
-- when its value is within the configured thresholds.

DO $$
DECLARE
    crash_metric_id BIGINT;
BEGIN
    SELECT metric_id
    INTO crash_metric_id
    FROM metric_definitions
    WHERE metric_key = 'crash_rate';

    INSERT INTO metric_observations (
        metric_id,
        observed_value,
        observed_at,
        dimensions
    )
    VALUES (
        crash_metric_id,
        0.4,
        NOW(),
        '{"platform":"all","region":"india"}'::JSONB
    );

    CALL evaluate_metric_alert(
        crash_metric_id,
        0.4
    );
END;
$$;

RELEASE SAVEPOINT before_recovery;

-- ============================================================
-- 30. DASHBOARD WIDGET CONFIGURATION REPORT
-- ============================================================

SELECT
    dashboard_name,
    metric_name,
    visualization,
    display_order,
    position_x,
    position_y,
    width,
    height
FROM dashboard_metric_catalog
ORDER BY dashboard_id, display_order;

COMMIT;

-- ============================================================
-- OPERATIONAL NOTES
--
-- 1. Use TIMESTAMPTZ for reporting and event timestamps.
-- 2. Keep metric definitions separate from observations.
-- 3. JSONB dimensions support flexible segmentation.
-- 4. Use time-range indexes for observation queries.
-- 5. Partition large observation tables by time.
-- 6. Use a materialized aggregate table for expensive reports.
-- 7. Apply database roles and row-level security in production.
-- 8. Alert evaluation should be scheduled and monitored.
-- 9. Use idempotency keys for external ingestion pipelines.
-- 10. Run dashboard queries against read replicas when appropriate.
-- ============================================================
