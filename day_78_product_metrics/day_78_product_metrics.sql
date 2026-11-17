/*
===============================================================================
PRODUCT METRICS MANAGEMENT AND ANALYTICS DATABASE
===============================================================================

Database: PostgreSQL 15+

Domain:
1. North Star Metrics
2. Input Metrics
3. Output Metrics
4. Guardrail Metrics

Implemented:
- Relational metric catalog
- Product and reporting-period management
- Metric definitions and observations
- Input-to-North-Star relationships
- Guardrail policies
- Experiment measurement
- Metric quality validation
- Automated status evaluation
- Reporting views
- Stored functions and procedures
- Database triggers
- Transactional reporting operations

The script is designed to be executed as a complete PostgreSQL script.
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_analytics;

SET search_path TO product_analytics, public;

-- ============================================================================
-- 1. DOMAIN TYPES
-- ============================================================================

CREATE TYPE metric_category AS ENUM (
    'north_star',
    'input',
    'output',
    'guardrail'
);

CREATE TYPE metric_direction AS ENUM (
    'higher',
    'lower',
    'range'
);

CREATE TYPE metric_status AS ENUM (
    'on_track',
    'below_target',
    'above_limit',
    'below_range',
    'above_range',
    'missing'
);

CREATE TYPE alert_severity AS ENUM (
    'info',
    'warning',
    'critical'
);

CREATE TYPE experiment_status AS ENUM (
    'draft',
    'running',
    'completed',
    'cancelled'
);

-- ============================================================================
-- 2. PRODUCT AND REPORTING PERIODS
-- ============================================================================

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL UNIQUE,
    product_description TEXT,
    business_owner VARCHAR(120) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (LENGTH(TRIM(product_name)) > 0)
);

CREATE TABLE reporting_periods (
    period_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    period_code VARCHAR(40) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (product_id, period_code),
    CHECK (start_date <= end_date)
);

CREATE INDEX idx_reporting_periods_dates
ON reporting_periods(product_id, start_date, end_date);

-- ============================================================================
-- 3. METRIC DEFINITIONS
-- ============================================================================

CREATE TABLE metric_definitions (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id BIGINT NOT NULL
        REFERENCES products(product_id),

    metric_name VARCHAR(150) NOT NULL,
    category metric_category NOT NULL,
    unit VARCHAR(40) NOT NULL,
    direction metric_direction NOT NULL,

    target_value NUMERIC(18,4),
    minimum_value NUMERIC(18,4),
    maximum_value NUMERIC(18,4),

    calculation_method TEXT NOT NULL,
    description TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(product_id, metric_name),

    CHECK (LENGTH(TRIM(metric_name)) > 0),
    CHECK (target_value IS NULL OR target_value >= 0),
    CHECK (minimum_value IS NULL OR minimum_value >= 0),
    CHECK (maximum_value IS NULL OR maximum_value >= 0),
    CHECK (
        minimum_value IS NULL
        OR maximum_value IS NULL
        OR minimum_value <= maximum_value
    )
);

CREATE UNIQUE INDEX uq_one_north_star_per_product
ON metric_definitions(product_id)
WHERE category = 'north_star' AND is_active = TRUE;

CREATE INDEX idx_metric_definitions_category
ON metric_definitions(product_id, category)
WHERE is_active = TRUE;

-- ============================================================================
-- 4. INPUT METRIC DEPENDENCIES
-- ============================================================================

CREATE TABLE metric_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id BIGINT NOT NULL
        REFERENCES products(product_id),

    source_metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    destination_metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    relationship_description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(source_metric_id, destination_metric_id),

    CHECK (source_metric_id <> destination_metric_id)
);

CREATE INDEX idx_metric_dependencies_destination
ON metric_dependencies(destination_metric_id);

-- ============================================================================
-- 5. OBSERVATIONS
-- ============================================================================

CREATE TABLE metric_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    period_id BIGINT NOT NULL
        REFERENCES reporting_periods(period_id),

    metric_value NUMERIC(18,4) NOT NULL,

    sample_size BIGINT NOT NULL,

    numerator BIGINT,
    denominator BIGINT,

    data_source VARCHAR(150) NOT NULL,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(metric_id, period_id),

    CHECK (metric_value >= 0),
    CHECK (sample_size > 0),
    CHECK (numerator IS NULL OR numerator >= 0),
    CHECK (denominator IS NULL OR denominator > 0),
    CHECK (
        numerator IS NULL
        OR denominator IS NULL
        OR numerator <= denominator
    )
);

CREATE INDEX idx_metric_observations_period
ON metric_observations(period_id, metric_id);

CREATE INDEX idx_metric_observations_metric_time
ON metric_observations(metric_id, recorded_at DESC);

-- ============================================================================
-- 6. GUARDRAIL POLICIES
-- ============================================================================

CREATE TABLE guardrail_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    policy_name VARCHAR(150) NOT NULL,

    maximum_allowed NUMERIC(18,4),
    minimum_allowed NUMERIC(18,4),

    severity alert_severity NOT NULL DEFAULT 'critical',

    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (
        maximum_allowed IS NULL
        OR maximum_allowed >= 0
    ),

    CHECK (
        minimum_allowed IS NULL
        OR minimum_allowed >= 0
    ),

    CHECK (
        minimum_allowed IS NULL
        OR maximum_allowed IS NULL
        OR minimum_allowed <= maximum_allowed
    )
);

CREATE INDEX idx_guardrail_policies_metric
ON guardrail_policies(metric_id)
WHERE is_enabled = TRUE;

CREATE TABLE guardrail_alerts (
    alert_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_id BIGINT NOT NULL
        REFERENCES guardrail_policies(policy_id),

    observation_id BIGINT NOT NULL
        REFERENCES metric_observations(observation_id),

    severity alert_severity NOT NULL,

    observed_value NUMERIC(18,4) NOT NULL,

    alert_message TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(policy_id, observation_id)
);

-- ============================================================================
-- 7. EXPERIMENT MANAGEMENT
-- ============================================================================

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id BIGINT NOT NULL
        REFERENCES products(product_id),

    experiment_name VARCHAR(150) NOT NULL,

    hypothesis TEXT NOT NULL,

    primary_metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    status experiment_status NOT NULL DEFAULT 'draft',

    start_date DATE,
    end_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(product_id, experiment_name),

    CHECK (
        end_date IS NULL
        OR start_date IS NULL
        OR end_date >= start_date
    )
);

CREATE TABLE experiment_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id),

    variant_name VARCHAR(80) NOT NULL,

    metric_value NUMERIC(18,4) NOT NULL,

    sample_size BIGINT NOT NULL,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(experiment_id, variant_name),

    CHECK (metric_value >= 0),
    CHECK (sample_size > 0)
);

-- ============================================================================
-- 8. METRIC EVALUATION HISTORY
-- ============================================================================

CREATE TABLE metric_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    period_id BIGINT NOT NULL
        REFERENCES reporting_periods(period_id),

    current_value NUMERIC(18,4) NOT NULL,

    previous_value NUMERIC(18,4),

    change_percent NUMERIC(12,4),

    achievement_percent NUMERIC(12,4),

    status metric_status NOT NULL,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(metric_id, period_id)
);

CREATE INDEX idx_metric_evaluations_status
ON metric_evaluations(status, period_id);

-- ============================================================================
-- 9. VALIDATION TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_metric_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_definition metric_definitions%ROWTYPE;
    v_period_product BIGINT;
BEGIN
    SELECT *
    INTO v_definition
    FROM metric_definitions
    WHERE metric_id = NEW.metric_id
    FOR KEY SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Metric definition does not exist';
    END IF;

    SELECT product_id
    INTO v_period_product
    FROM reporting_periods
    WHERE period_id = NEW.period_id;

    IF v_period_product <> v_definition.product_id THEN
        RAISE EXCEPTION
            'Observation and metric belong to different products';
    END IF;

    IF (
        v_definition.minimum_value IS NOT NULL
        AND NEW.metric_value < v_definition.minimum_value
    ) THEN
        RAISE EXCEPTION
            'Observation below metric valid minimum';
    END IF;

    IF (
        v_definition.maximum_value IS NOT NULL
        AND NEW.metric_value > v_definition.maximum_value
    ) THEN
        RAISE EXCEPTION
            'Observation above metric valid maximum';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_metric_observation
BEFORE INSERT OR UPDATE ON metric_observations
FOR EACH ROW
EXECUTE FUNCTION validate_metric_observation();

-- ============================================================================
-- 10. METRIC EVALUATION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION evaluate_metric(
    p_metric_id BIGINT,
    p_period_id BIGINT
)
RETURNS TABLE (
    metric_name VARCHAR,
    category metric_category,
    current_value NUMERIC,
    previous_value NUMERIC,
    change_percent NUMERIC,
    target_value NUMERIC,
    status metric_status
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_definition metric_definitions%ROWTYPE;
    v_current NUMERIC(18,4);
    v_previous NUMERIC(18,4);
    v_previous_period BIGINT;
    v_change NUMERIC(12,4);
    v_status metric_status;
BEGIN
    SELECT *
    INTO v_definition
    FROM metric_definitions
    WHERE metric_id = p_metric_id
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active metric not found: %', p_metric_id;
    END IF;

    SELECT metric_value
    INTO v_current
    FROM metric_observations
    WHERE metric_id = p_metric_id
      AND period_id = p_period_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT
            v_definition.metric_name::VARCHAR,
            v_definition.category,
            NULL::NUMERIC,
            NULL::NUMERIC,
            NULL::NUMERIC,
            v_definition.target_value,
            'missing'::metric_status;

        RETURN;
    END IF;

    SELECT previous.period_id
    INTO v_previous_period
    FROM reporting_periods current_period
    JOIN reporting_periods previous
      ON previous.product_id = current_period.product_id
     AND previous.end_date < current_period.start_date
    WHERE current_period.period_id = p_period_id
    ORDER BY previous.end_date DESC
    LIMIT 1;

    IF v_previous_period IS NOT NULL THEN
        SELECT metric_value
        INTO v_previous
        FROM metric_observations
        WHERE metric_id = p_metric_id
          AND period_id = v_previous_period;
    END IF;

    IF v_previous IS NOT NULL AND v_previous <> 0 THEN
        v_change := ROUND(
            ((v_current - v_previous) / ABS(v_previous)) * 100,
            4
        );
    END IF;

    v_status := 'on_track';

    IF (
        v_definition.direction = 'higher'
        AND v_definition.target_value IS NOT NULL
        AND v_current < v_definition.target_value
    ) THEN
        v_status := 'below_target';

    ELSIF (
        v_definition.direction = 'lower'
        AND v_definition.target_value IS NOT NULL
        AND v_current > v_definition.target_value
    ) THEN
        v_status := 'above_limit';

    ELSIF (
        v_definition.direction = 'range'
        AND v_definition.minimum_value IS NOT NULL
        AND v_current < v_definition.minimum_value
    ) THEN
        v_status := 'below_range';

    ELSIF (
        v_definition.direction = 'range'
        AND v_definition.maximum_value IS NOT NULL
        AND v_current > v_definition.maximum_value
    ) THEN
        v_status := 'above_range';
    END IF;

    RETURN QUERY
    SELECT
        v_definition.metric_name::VARCHAR,
        v_definition.category,
        v_current,
        v_previous,
        v_change,
        v_definition.target_value,
        v_status;
END;
$$;

-- ============================================================================
-- 11. EVALUATION PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE process_product_metrics(
    p_product_id BIGINT,
    p_period_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_metric RECORD;
    v_result RECORD;
    v_previous NUMERIC(18,4);
    v_achievement NUMERIC(12,4);
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM reporting_periods
        WHERE period_id = p_period_id
          AND product_id = p_product_id
    ) THEN
        RAISE EXCEPTION
            'Reporting period does not belong to product';
    END IF;

    FOR v_metric IN
        SELECT metric_id, target_value
        FROM metric_definitions
        WHERE product_id = p_product_id
          AND is_active = TRUE
    LOOP
        SELECT *
        INTO v_result
        FROM evaluate_metric(
            v_metric.metric_id,
            p_period_id
        );

        IF v_result.current_value IS NULL THEN
            CONTINUE;
        END IF;

        v_achievement := NULL;

        IF (
            v_metric.target_value IS NOT NULL
            AND v_metric.target_value <> 0
        ) THEN
            v_achievement := ROUND(
                v_result.current_value /
                v_metric.target_value * 100,
                4
            );
        END IF;

        INSERT INTO metric_evaluations (
            metric_id,
            period_id,
            current_value,
            previous_value,
            change_percent,
            achievement_percent,
            status
        )
        VALUES (
            v_metric.metric_id,
            p_period_id,
            v_result.current_value,
            v_result.previous_value,
            v_result.change_percent,
            v_achievement,
            v_result.status
        )
        ON CONFLICT (metric_id, period_id)
        DO UPDATE SET
            current_value = EXCLUDED.current_value,
            previous_value = EXCLUDED.previous_value,
            change_percent = EXCLUDED.change_percent,
            achievement_percent = EXCLUDED.achievement_percent,
            status = EXCLUDED.status,
            evaluated_at = NOW();
    END LOOP;
END;
$$;

-- ============================================================================
-- 12. GUARDRAIL EVALUATION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION evaluate_guardrails(
    p_period_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    INSERT INTO guardrail_alerts (
        policy_id,
        observation_id,
        severity,
        observed_value,
        alert_message
    )
    SELECT
        gp.policy_id,
        mo.observation_id,
        gp.severity,
        mo.metric_value,
        CASE
            WHEN gp.maximum_allowed IS NOT NULL
                 AND mo.metric_value > gp.maximum_allowed
            THEN 'Maximum guardrail threshold exceeded'
            WHEN gp.minimum_allowed IS NOT NULL
                 AND mo.metric_value < gp.minimum_allowed
            THEN 'Minimum guardrail threshold breached'
        END
    FROM guardrail_policies gp
    JOIN metric_observations mo
      ON mo.metric_id = gp.metric_id
    WHERE mo.period_id = p_period_id
      AND gp.is_enabled = TRUE
      AND (
          (
              gp.maximum_allowed IS NOT NULL
              AND mo.metric_value > gp.maximum_allowed
          )
          OR
          (
              gp.minimum_allowed IS NOT NULL
              AND mo.metric_value < gp.minimum_allowed
          )
      )
    ON CONFLICT(policy_id, observation_id)
    DO NOTHING;

    GET DIAGNOSTICS v_count = ROW_COUNT;

    RETURN v_count;
END;
$$;

-- ============================================================================
-- 13. REPORTING VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW v_product_metric_dashboard AS
SELECT
    p.product_name,
    rp.period_code,
    md.metric_name,
    md.category,
    md.unit,
    md.direction,
    md.target_value,
    mo.metric_value,
    mo.sample_size,
    me.previous_value,
    me.change_percent,
    me.achievement_percent,
    me.status,
    me.evaluated_at
FROM metric_observations mo
JOIN metric_definitions md
  ON md.metric_id = mo.metric_id
JOIN reporting_periods rp
  ON rp.period_id = mo.period_id
JOIN products p
  ON p.product_id = rp.product_id
LEFT JOIN metric_evaluations me
  ON me.metric_id = md.metric_id
 AND me.period_id = rp.period_id
WHERE md.is_active = TRUE;

CREATE OR REPLACE VIEW v_north_star_performance AS
SELECT
    product_name,
    period_code,
    metric_name,
    metric_value AS north_star_value,
    previous_value,
    change_percent,
    status
FROM v_product_metric_dashboard
WHERE category = 'north_star';

CREATE OR REPLACE VIEW v_guardrail_breaches AS
SELECT
    p.product_name,
    md.metric_name,
    rp.period_code,
    ga.severity,
    ga.observed_value,
    ga.alert_message,
    ga.created_at
FROM guardrail_alerts ga
JOIN guardrail_policies gp
  ON gp.policy_id = ga.policy_id
JOIN metric_definitions md
  ON md.metric_id = gp.metric_id
JOIN metric_observations mo
  ON mo.observation_id = ga.observation_id
JOIN reporting_periods rp
  ON rp.period_id = mo.period_id
JOIN products p
  ON p.product_id = md.product_id;

CREATE OR REPLACE VIEW v_category_performance AS
SELECT
    p.product_name,
    rp.period_code,
    md.category,
    COUNT(*) AS metric_count,
    AVG(me.achievement_percent) AS average_target_achievement,
    COUNT(*) FILTER (
        WHERE me.status <> 'on_track'
    ) AS metrics_outside_target
FROM metric_evaluations me
JOIN metric_definitions md
  ON md.metric_id = me.metric_id
JOIN reporting_periods rp
  ON rp.period_id = me.period_id
JOIN products p
  ON p.product_id = md.product_id
GROUP BY
    p.product_name,
    rp.period_code,
    md.category;

-- ============================================================================
-- 14. EXPERIMENT LIFT REPORT
-- ============================================================================

CREATE OR REPLACE VIEW v_experiment_lift AS
WITH grouped AS (
    SELECT
        e.experiment_id,
        e.experiment_name,
        er.variant_name,
        er.metric_value,
        er.sample_size,
        ROW_NUMBER() OVER (
            PARTITION BY e.experiment_id
            ORDER BY
                CASE
                    WHEN LOWER(er.variant_name) = 'control'
                    THEN 0
                    ELSE 1
                END,
                er.variant_name
        ) AS variant_order
    FROM experiments e
    JOIN experiment_results er
      ON er.experiment_id = e.experiment_id
),
control AS (
    SELECT
        experiment_id,
        metric_value AS control_value
    FROM grouped
    WHERE variant_order = 1
),
treatment AS (
    SELECT
        experiment_id,
        metric_value AS treatment_value
    FROM grouped
    WHERE variant_order = 2
)
SELECT
    e.experiment_name,
    c.control_value,
    t.treatment_value,
    t.treatment_value - c.control_value AS absolute_lift,
    CASE
        WHEN c.control_value = 0 THEN NULL
        ELSE ROUND(
            (
                (t.treatment_value - c.control_value)
                / ABS(c.control_value)
            ) * 100,
            2
        )
    END AS relative_lift_percent
FROM experiments e
JOIN control c
  ON c.experiment_id = e.experiment_id
JOIN treatment t
  ON t.experiment_id = e.experiment_id;

-- ============================================================================
-- 15. SAMPLE PRODUCT AND PERIODS
-- ============================================================================

INSERT INTO products (
    product_name,
    product_description,
    business_owner
)
VALUES (
    'Digital Learning Platform',
    'Subscription-based online learning product',
    'Product Analytics Team'
);

INSERT INTO reporting_periods (
    product_id,
    period_code,
    start_date,
    end_date
)
SELECT
    product_id,
    '2026-W45',
    DATE '2026-11-02',
    DATE '2026-11-08'
FROM products
WHERE product_name = 'Digital Learning Platform';

INSERT INTO reporting_periods (
    product_id,
    period_code,
    start_date,
    end_date
)
SELECT
    product_id,
    '2026-W46',
    DATE '2026-11-09',
    DATE '2026-11-15'
FROM products
WHERE product_name = 'Digital Learning Platform';

-- ============================================================================
-- 16. SAMPLE METRIC DEFINITIONS
-- ============================================================================

INSERT INTO metric_definitions (
    product_id,
    metric_name,
    category,
    unit,
    direction,
    target_value,
    minimum_value,
    maximum_value,
    calculation_method,
    description
)
SELECT
    product_id,
    metric_name,
    category,
    unit,
    direction,
    target_value,
    minimum_value,
    maximum_value,
    calculation_method,
    description
FROM products
CROSS JOIN (
    VALUES
    (
        'Weekly Active Learners',
        'north_star'::metric_category,
        'users',
        'higher'::metric_direction,
        12000::NUMERIC,
        NULL::NUMERIC,
        NULL::NUMERIC,
        'Count of distinct users completing a meaningful learning activity',
        'Primary measure of recurring customer value'
    ),
    (
        'Activation Rate',
        'input'::metric_category,
        '%',
        'higher'::metric_direction,
        65::NUMERIC,
        0::NUMERIC,
        100::NUMERIC,
        'Activated new users / eligible new users * 100',
        'Measures successful initial product adoption'
    ),
    (
        'Lesson Completion Rate',
        'input'::metric_category,
        '%',
        'higher'::metric_direction,
        75::NUMERIC,
        0::NUMERIC,
        100::NUMERIC,
        'Completed lessons / started lessons * 100',
        'Measures meaningful learning progress'
    ),
    (
        'Weekly Learning Sessions',
        'input'::metric_category,
        'sessions',
        'higher'::metric_direction,
        45000::NUMERIC,
        NULL::NUMERIC,
        NULL::NUMERIC,
        'Count of qualifying learning sessions',
        'Measures recurring product engagement'
    ),
    (
        'Subscription Revenue',
        'output'::metric_category,
        'INR',
        'higher'::metric_direction,
        1500000::NUMERIC,
        NULL::NUMERIC,
        NULL::NUMERIC,
        'Recognized subscription revenue for the reporting period',
        'Measures commercial performance'
    ),
    (
        'Retention Rate',
        'output'::metric_category,
        '%',
        'higher'::metric_direction,
        85::NUMERIC,
        0::NUMERIC,
        100::NUMERIC,
        'Retained eligible users / eligible users * 100',
        'Measures continued customer relationships'
    ),
    (
        'Application Error Rate',
        'guardrail'::metric_category,
        '%',
        'lower'::metric_direction,
        1::NUMERIC,
        0::NUMERIC,
        2::NUMERIC,
        'Failed requests / total requests * 100',
        'Protects product reliability'
    ),
    (
        'Page Load Time',
        'guardrail'::metric_category,
        'seconds',
        'lower'::metric_direction,
        2::NUMERIC,
        0::NUMERIC,
        3::NUMERIC,
        'Average page load duration',
        'Protects user experience'
    ),
    (
        'Support Complaint Rate',
        'guardrail'::metric_category,
        '%',
        'lower'::metric_direction,
        2::NUMERIC,
        0::NUMERIC,
        3::NUMERIC,
        'Complaint-producing users / active users * 100',
        'Protects customer experience'
    )
) AS metrics(
    metric_name,
    category,
    unit,
    direction,
    target_value,
    minimum_value,
    maximum_value,
    calculation_method,
    description
)
WHERE product_name = 'Digital Learning Platform';

-- ============================================================================
-- 17. INPUT-TO-NORTH-STAR DEPENDENCIES
-- ============================================================================

INSERT INTO metric_dependencies (
    product_id,
    source_metric_id,
    destination_metric_id,
    relationship_description
)
SELECT
    p.product_id,
    source.metric_id,
    destination.metric_id,
    relationship.description
FROM products p
JOIN metric_definitions source
  ON source.product_id = p.product_id
JOIN metric_definitions destination
  ON destination.product_id = p.product_id
JOIN (
    VALUES
    (
        'Activation Rate',
        'Weekly Active Learners',
        'Improved activation can increase the eligible active user base'
    ),
    (
        'Lesson Completion Rate',
        'Weekly Active Learners',
        'Successful lesson completion supports recurring learning value'
    ),
    (
        'Weekly Learning Sessions',
        'Weekly Active Learners',
        'Meaningful learning sessions contribute to weekly active usage'
    ),
    (
        'Retention Rate',
        'Weekly Active Learners',
        'Retention supports recurring weekly product participation'
    )
) AS relationship(
    source_name,
    destination_name,
    description
)
  ON source.metric_name = relationship.source_name
 AND destination.metric_name = relationship.destination_name
WHERE p.product_name = 'Digital Learning Platform';

-- ============================================================================
-- 18. GUARDRAIL POLICIES
-- ============================================================================

INSERT INTO guardrail_policies (
    metric_id,
    policy_name,
    maximum_allowed,
    minimum_allowed,
    severity
)
SELECT
    metric_id,
    metric_name || ' operational threshold',
    CASE metric_name
        WHEN 'Application Error Rate' THEN 2
        WHEN 'Page Load Time' THEN 3
        WHEN 'Support Complaint Rate' THEN 3
    END,
    0,
    'critical'
FROM metric_definitions
WHERE category = 'guardrail'
  AND product_id = (
      SELECT product_id
      FROM products
      WHERE product_name = 'Digital Learning Platform'
  );

-- ============================================================================
-- 19. SAMPLE OBSERVATIONS
-- ============================================================================

INSERT INTO metric_observations (
    metric_id,
    period_id,
    metric_value,
    sample_size,
    data_source
)
SELECT
    md.metric_id,
    rp.period_id,
    values.metric_value,
    values.sample_size,
    'Product Analytics Pipeline'
FROM metric_definitions md
JOIN products p
  ON p.product_id = md.product_id
JOIN reporting_periods rp
  ON rp.product_id = p.product_id
JOIN (
    VALUES
    ('Weekly Active Learners', '2026-W45', 10800::NUMERIC, 10000::BIGINT),
    ('Weekly Active Learners', '2026-W46', 12400::NUMERIC, 12000::BIGINT),
    ('Activation Rate', '2026-W45', 62::NUMERIC, 10000::BIGINT),
    ('Activation Rate', '2026-W46', 68::NUMERIC, 12000::BIGINT),
    ('Lesson Completion Rate', '2026-W45', 72::NUMERIC, 9000::BIGINT),
    ('Lesson Completion Rate', '2026-W46', 78::NUMERIC, 11000::BIGINT),
    ('Weekly Learning Sessions', '2026-W45', 41000::NUMERIC, 10000::BIGINT),
    ('Weekly Learning Sessions', '2026-W46', 47000::NUMERIC, 12000::BIGINT),
    ('Subscription Revenue', '2026-W45', 1380000::NUMERIC, 10000::BIGINT),
    ('Subscription Revenue', '2026-W46', 1570000::NUMERIC, 12000::BIGINT),
    ('Retention Rate', '2026-W45', 84::NUMERIC, 10000::BIGINT),
    ('Retention Rate', '2026-W46', 86::NUMERIC, 12000::BIGINT),
    ('Application Error Rate', '2026-W45', 0.8::NUMERIC, 100000::BIGINT),
    ('Application Error Rate', '2026-W46', 2.4::NUMERIC, 120000::BIGINT),
    ('Page Load Time', '2026-W45', 1.8::NUMERIC, 10000::BIGINT),
    ('Page Load Time', '2026-W46', 2.2::NUMERIC, 12000::BIGINT),
    ('Support Complaint Rate', '2026-W45', 1.5::NUMERIC, 10000::BIGINT),
    ('Support Complaint Rate', '2026-W46', 1.8::NUMERIC, 12000::BIGINT)
) AS values(metric_name, period_code, metric_value, sample_size)
  ON values.metric_name = md.metric_name
 AND values.period_code = rp.period_code
WHERE p.product_name = 'Digital Learning Platform';

-- ============================================================================
-- 20. INPUT METRIC DATA QUALITY AND VALIDATION
-- ============================================================================

-- Demonstrate an invalid observation inside a subtransaction.
-- The exception is handled without aborting the complete script.

DO $$
DECLARE
    v_metric_id BIGINT;
    v_period_id BIGINT;
BEGIN
    SELECT metric_id
    INTO v_metric_id
    FROM metric_definitions
    WHERE metric_name = 'Activation Rate';

    SELECT period_id
    INTO v_period_id
    FROM reporting_periods
    WHERE period_code = '2026-W46';

    BEGIN
        INSERT INTO metric_observations (
            metric_id,
            period_id,
            metric_value,
            sample_size,
            data_source
        )
        VALUES (
            v_metric_id,
            v_period_id,
            125,
            1000,
            'Invalid Test Import'
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Invalid observation correctly rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================================
-- 21. EXPERIMENT SAMPLE DATA
-- ============================================================================

INSERT INTO experiments (
    product_id,
    experiment_name,
    hypothesis,
    primary_metric_id,
    status,
    start_date,
    end_date
)
SELECT
    p.product_id,
    'Improved Learning Onboarding',
    'Simplified onboarding will improve activation.',
    md.metric_id,
    'completed',
    DATE '2026-11-01',
    DATE '2026-11-15'
FROM products p
JOIN metric_definitions md
  ON md.product_id = p.product_id
WHERE p.product_name = 'Digital Learning Platform'
  AND md.metric_name = 'Activation Rate';

INSERT INTO experiment_results (
    experiment_id,
    variant_name,
    metric_value,
    sample_size
)
SELECT
    experiment_id,
    variant_name,
    metric_value,
    sample_size
FROM experiments
CROSS JOIN (
    VALUES
    ('control', 65::NUMERIC, 500::BIGINT),
    ('treatment', 70::NUMERIC, 520::BIGINT)
) AS results(variant_name, metric_value, sample_size)
WHERE experiment_name = 'Improved Learning Onboarding';

-- ============================================================================
-- 22. TRANSACTIONAL METRIC PROCESSING
-- ============================================================================

DO $$
DECLARE
    v_product_id BIGINT;
    v_period_id BIGINT;
    v_alert_count INTEGER;
BEGIN
    SELECT product_id
    INTO v_product_id
    FROM products
    WHERE product_name = 'Digital Learning Platform';

    SELECT period_id
    INTO v_period_id
    FROM reporting_periods
    WHERE product_id = v_product_id
      AND period_code = '2026-W46';

    CALL process_product_metrics(
        v_product_id,
        v_period_id
    );

    v_alert_count := evaluate_guardrails(v_period_id);

    RAISE NOTICE
        'Metrics evaluated. New guardrail alerts: %',
        v_alert_count;
END;
$$;

COMMIT;

-- ============================================================================
-- 23. RETRIEVAL QUERIES
-- ============================================================================

-- North Star Metric performance.

SELECT *
FROM v_north_star_performance
ORDER BY period_code;

-- Complete product dashboard.

SELECT
    product_name,
    period_code,
    metric_name,
    category,
    metric_value,
    unit,
    target_value,
    change_percent,
    status
FROM v_product_metric_dashboard
ORDER BY
    period_code,
    category,
    metric_name;

-- ============================================================================
-- 24. INPUT, OUTPUT, AND GUARDRAIL AGGREGATION
-- ============================================================================

SELECT
    category,
    COUNT(*) AS metric_count,
    ROUND(AVG(achievement_percent), 2)
        AS average_target_achievement,
    COUNT(*) FILTER (
        WHERE status <> 'on_track'
    ) AS outside_target_count
FROM v_category_performance
GROUP BY category
ORDER BY category;

-- ============================================================================
-- 25. GUARDRAIL REPORT
-- ============================================================================

SELECT *
FROM v_guardrail_breaches
ORDER BY created_at DESC;

-- ============================================================================
-- 26. EXPERIMENT EVALUATION
-- ============================================================================

SELECT
    experiment_name,
    control_value,
    treatment_value,
    absolute_lift,
    relative_lift_percent
FROM v_experiment_lift;

-- ============================================================================
-- 27. METRIC DEPENDENCY RETRIEVAL
-- ============================================================================

SELECT
    source.metric_name AS input_metric,
    destination.metric_name AS affected_metric,
    dependency.relationship_description
FROM metric_dependencies dependency
JOIN metric_definitions source
  ON source.metric_id = dependency.source_metric_id
JOIN metric_definitions destination
  ON destination.metric_id = dependency.destination_metric_id
ORDER BY source.metric_name;

-- ============================================================================
-- 28. MISSING OBSERVATION VALIDATION
-- ============================================================================

SELECT
    md.metric_name,
    rp.period_code,
    md.category
FROM metric_definitions md
CROSS JOIN reporting_periods rp
WHERE md.product_id = rp.product_id
  AND md.is_active = TRUE
  AND NOT EXISTS (
      SELECT 1
      FROM metric_observations mo
      WHERE mo.metric_id = md.metric_id
        AND mo.period_id = rp.period_id
  )
ORDER BY rp.period_code, md.metric_name;

-- ============================================================================
-- 29. METRIC GROWTH AND PERFORMANCE RANKING
-- ============================================================================

SELECT
    product_name,
    period_code,
    metric_name,
    category,
    change_percent,
    RANK() OVER (
        PARTITION BY product_name, period_code, category
        ORDER BY change_percent DESC NULLS LAST
    ) AS growth_rank
FROM v_product_metric_dashboard
WHERE change_percent IS NOT NULL
ORDER BY category, growth_rank;

-- ============================================================================
-- 30. NORTH STAR AND INPUT METRIC RELATIONSHIP
-- ============================================================================

SELECT
    rp.period_code,
    source.metric_name AS input_metric,
    source_observation.metric_value AS input_value,
    destination.metric_name AS north_star_metric,
    destination_observation.metric_value AS north_star_value
FROM metric_dependencies dependency
JOIN metric_definitions source
  ON source.metric_id = dependency.source_metric_id
JOIN metric_definitions destination
  ON destination.metric_id = dependency.destination_metric_id
JOIN reporting_periods rp
  ON rp.product_id = dependency.product_id
JOIN metric_observations source_observation
  ON source_observation.metric_id = source.metric_id
 AND source_observation.period_id = rp.period_id
JOIN metric_observations destination_observation
  ON destination_observation.metric_id = destination.metric_id
 AND destination_observation.period_id = rp.period_id
ORDER BY rp.period_code, source.metric_name;

-- ============================================================================
-- END OF PRODUCT METRICS DATABASE
-- ============================================================================
