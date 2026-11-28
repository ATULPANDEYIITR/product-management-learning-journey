-- ============================================================
-- EXPERIMENT METRICS MANAGEMENT SYSTEM
-- PostgreSQL 14+
--
-- Domain:
-- Primary metrics
-- Secondary metrics
-- Guardrail metrics
-- Sample-size planning
-- Experiment allocation
-- User-level observations
-- Statistical evaluation
-- Experiment decisions
-- Governance and auditability
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS experiment_metrics;

SET search_path TO experiment_metrics, public;

-- ------------------------------------------------------------
-- ENUMERATED DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE metric_type AS ENUM (
    'primary',
    'secondary',
    'guardrail'
);

CREATE TYPE experiment_status AS ENUM (
    'draft',
    'running',
    'completed',
    'invalid'
);

CREATE TYPE experiment_variant AS ENUM (
    'control',
    'treatment'
);

CREATE TYPE experiment_decision AS ENUM (
    'ship',
    'do_not_ship',
    'inconclusive',
    'invalid'
);

CREATE TYPE metric_value_type AS ENUM (
    'proportion',
    'continuous',
    'count',
    'duration'
);

-- ------------------------------------------------------------
-- EXPERIMENT REGISTRY
-- ------------------------------------------------------------

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_key VARCHAR(80) NOT NULL UNIQUE,

    experiment_name VARCHAR(200) NOT NULL,

    description TEXT,

    status experiment_status NOT NULL DEFAULT 'draft',

    baseline_conversion NUMERIC(12,8) NOT NULL,

    relative_mde NUMERIC(12,8) NOT NULL,

    alpha NUMERIC(8,6) NOT NULL DEFAULT 0.05,

    statistical_power NUMERIC(8,6) NOT NULL DEFAULT 0.80,

    traffic_allocation NUMERIC(8,6) NOT NULL DEFAULT 1.0,

    planned_sample_per_group INTEGER,

    actual_start_time TIMESTAMPTZ,

    actual_end_time TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        baseline_conversion > 0
        AND baseline_conversion < 1
    ),

    CHECK (
        relative_mde > 0
        AND relative_mde < 1
    ),

    CHECK (alpha > 0 AND alpha < 1),

    CHECK (
        statistical_power > 0
        AND statistical_power < 1
    ),

    CHECK (
        traffic_allocation > 0
        AND traffic_allocation <= 1
    ),

    CHECK (
        planned_sample_per_group IS NULL
        OR planned_sample_per_group >= 2
    ),

    CHECK (
        actual_end_time IS NULL
        OR actual_start_time IS NULL
        OR actual_end_time >= actual_start_time
    )
);

-- ------------------------------------------------------------
-- METRIC DEFINITIONS
-- ------------------------------------------------------------

CREATE TABLE metric_definitions (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    metric_name VARCHAR(120) NOT NULL,

    metric_category metric_type NOT NULL,

    value_type metric_value_type NOT NULL,

    unit VARCHAR(50) NOT NULL,

    higher_is_better BOOLEAN NOT NULL,

    minimum_allowed NUMERIC,

    maximum_allowed NUMERIC,

    guardrail_threshold NUMERIC,

    metric_description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (experiment_id, metric_name),

    CHECK (
        minimum_allowed IS NULL
        OR maximum_allowed IS NULL
        OR minimum_allowed <= maximum_allowed
    ),

    CHECK (
        metric_category <> 'guardrail'
        OR guardrail_threshold IS NOT NULL
    )
);

-- One primary metric per experiment.
CREATE UNIQUE INDEX one_primary_metric_per_experiment
ON metric_definitions(experiment_id)
WHERE metric_category = 'primary';

CREATE INDEX idx_metric_category
ON metric_definitions(experiment_id, metric_category);

-- ------------------------------------------------------------
-- EXPERIMENT VARIANTS
-- ------------------------------------------------------------

CREATE TABLE experiment_variants (
    variant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    variant_name experiment_variant NOT NULL,

    allocation_percentage NUMERIC(8,6) NOT NULL,

    description TEXT,

    UNIQUE (experiment_id, variant_name),

    CHECK (
        allocation_percentage > 0
        AND allocation_percentage <= 1
    )
);

-- ------------------------------------------------------------
-- EXPERIMENT USERS
-- ------------------------------------------------------------

CREATE TABLE experiment_assignments (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    variant_id BIGINT NOT NULL
        REFERENCES experiment_variants(variant_id),

    participant_key VARCHAR(128) NOT NULL,

    assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (experiment_id, participant_key),

    UNIQUE (assignment_id, experiment_id)
);

CREATE INDEX idx_assignment_variant
ON experiment_assignments(experiment_id, variant_id);

CREATE INDEX idx_assignment_time
ON experiment_assignments(assigned_at);

-- ------------------------------------------------------------
-- METRIC OBSERVATIONS
--
-- Each row represents one user-level metric observation.
-- A user may have multiple metric observations.
-- ------------------------------------------------------------

CREATE TABLE metric_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assignment_id BIGINT NOT NULL,

    experiment_id BIGINT NOT NULL,

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    numeric_value NUMERIC(20,6) NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (assignment_id, experiment_id)
        REFERENCES experiment_assignments(
            assignment_id,
            experiment_id
        )
        ON DELETE CASCADE,

    UNIQUE (assignment_id, metric_id),

    CHECK (
        numeric_value > '-Infinity'::NUMERIC
        AND numeric_value < 'Infinity'::NUMERIC
    )
);

CREATE INDEX idx_observation_experiment_metric
ON metric_observations(
    experiment_id,
    metric_id,
    observed_at
);

CREATE INDEX idx_observation_assignment
ON metric_observations(assignment_id);

-- ------------------------------------------------------------
-- EXPERIMENT EVALUATION
-- ------------------------------------------------------------

CREATE TABLE experiment_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id),

    control_sample_size INTEGER NOT NULL,

    treatment_sample_size INTEGER NOT NULL,

    primary_control_value NUMERIC(20,8) NOT NULL,

    primary_treatment_value NUMERIC(20,8) NOT NULL,

    absolute_effect NUMERIC(20,8) NOT NULL,

    relative_effect NUMERIC(20,8),

    p_value NUMERIC(12,10),

    significance_level NUMERIC(8,6) NOT NULL,

    sample_sufficient BOOLEAN NOT NULL,

    guardrails_passed BOOLEAN NOT NULL,

    decision experiment_decision NOT NULL,

    evaluation_notes TEXT,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (control_sample_size >= 0),

    CHECK (treatment_sample_size >= 0),

    CHECK (
        p_value IS NULL
        OR (p_value >= 0 AND p_value <= 1)
    ),

    CHECK (
        significance_level > 0
        AND significance_level < 1
    )
);

CREATE INDEX idx_evaluation_experiment
ON experiment_evaluations(experiment_id, evaluated_at DESC);

-- ------------------------------------------------------------
-- EXPERIMENT AUDIT LOG
-- ------------------------------------------------------------

CREATE TABLE experiment_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT
        REFERENCES experiments(experiment_id)
        ON DELETE SET NULL,

    action VARCHAR(100) NOT NULL,

    previous_status experiment_status,

    new_status experiment_status,

    actor VARCHAR(128) NOT NULL DEFAULT CURRENT_USER,

    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    details JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX idx_audit_experiment_time
ON experiment_audit_log(experiment_id, event_time DESC);

-- ------------------------------------------------------------
-- SAMPLE-SIZE CALCULATION
--
-- Equal allocation, two-sided two-proportion z-test.
-- Uses a normal approximation.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_sample_size(
    p_baseline NUMERIC,
    p_relative_mde NUMERIC,
    p_alpha NUMERIC DEFAULT 0.05,
    p_power NUMERIC DEFAULT 0.80
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_treatment NUMERIC;
    v_pooled NUMERIC;
    v_difference NUMERIC;
    v_z_alpha NUMERIC;
    v_z_power NUMERIC;
    v_result NUMERIC;
BEGIN
    IF p_baseline <= 0 OR p_baseline >= 1 THEN
        RAISE EXCEPTION 'Baseline conversion must be between 0 and 1';
    END IF;

    IF p_relative_mde <= 0 OR p_relative_mde >= 1 THEN
        RAISE EXCEPTION 'Invalid relative MDE';
    END IF;

    IF p_alpha <= 0 OR p_alpha >= 1 THEN
        RAISE EXCEPTION 'Invalid significance level';
    END IF;

    IF p_power <= 0 OR p_power >= 1 THEN
        RAISE EXCEPTION 'Invalid statistical power';
    END IF;

    v_treatment := p_baseline * (1 + p_relative_mde);

    IF v_treatment >= 1 THEN
        RAISE EXCEPTION 'Treatment conversion must be below 1';
    END IF;

    v_pooled := (p_baseline + v_treatment) / 2;

    v_difference := v_treatment - p_baseline;

    -- Normal quantiles for common planning values.
    -- Other values use an inverse-normal approximation.
    v_z_alpha := CASE
        WHEN p_alpha = 0.05 THEN 1.95996398454005
        WHEN p_alpha = 0.01 THEN 2.57582930354890
        ELSE inverse_normal_quantile(1 - p_alpha / 2)
    END;

    v_z_power := inverse_normal_quantile(p_power);

    v_result := POWER(
        v_z_alpha * SQRT(
            2 * v_pooled * (1 - v_pooled)
        )
        +
        v_z_power * SQRT(
            p_baseline * (1 - p_baseline)
            +
            v_treatment * (1 - v_treatment)
        ),
        2
    ) / POWER(v_difference, 2);

    RETURN CEIL(v_result)::BIGINT;
END;
$$;

-- Inverse standard-normal CDF using the Acklam approximation.
CREATE OR REPLACE FUNCTION inverse_normal_quantile(p NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    a NUMERIC[] := ARRAY[
        -39.6968302866538,
        220.946098424521,
        -275.928510446969,
        138.357751867269,
        -30.6647980661472,
        2.50662827745924
    ];

    b NUMERIC[] := ARRAY[
        -54.4760987982241,
        161.585836858041,
        -155.698979859887,
        66.8013118877197,
        -13.2806815528857
    ];

    c NUMERIC[] := ARRAY[
        -0.00778489400243029,
        -0.322396458041136,
        -2.40075827716184,
        -2.54973253934373,
        4.37466414146497,
        2.93816398269878
    ];

    d NUMERIC[] := ARRAY[
        0.00778469570904146,
        0.32246712907004,
        2.445134137143,
        3.75440866190742
    ];

    q NUMERIC;
    r NUMERIC;
BEGIN
    IF p <= 0 OR p >= 1 THEN
        RAISE EXCEPTION 'Probability must be between 0 and 1';
    END IF;

    IF p < 0.02425 THEN
        q := SQRT(-2 * LN(p));

        RETURN (((((c[1] * q + c[2]) * q + c[3]) * q +
            c[4]) * q + c[5]) * q + c[6]) /
            ((((d[1] * q + d[2]) * q + d[3]) * q +
                d[4]) * q + 1);
    END IF;

    IF p > 0.97575 THEN
        RETURN -inverse_normal_quantile(1 - p);
    END IF;

    q := p - 0.5;
    r := q * q;

    RETURN (((((a[1] * r + a[2]) * r + a[3]) * r +
        a[4]) * r + a[5]) * r + a[6]) * q /
        (((((b[1] * r + b[2]) * r + b[3]) * r +
            b[4]) * r + b[5]) * r + 1);
END;
$$;

-- ------------------------------------------------------------
-- STATUS TRANSITION ENFORCEMENT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_experiment_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = OLD.status THEN
        RETURN NEW;
    END IF;

    IF OLD.status = 'draft'
       AND NEW.status NOT IN ('running', 'invalid') THEN
        RAISE EXCEPTION 'Invalid transition from draft';
    END IF;

    IF OLD.status = 'running'
       AND NEW.status NOT IN ('completed', 'invalid') THEN
        RAISE EXCEPTION 'Invalid transition from running';
    END IF;

    IF OLD.status IN ('completed', 'invalid') THEN
        RAISE EXCEPTION 'Terminal experiment status cannot change';
    END IF;

    IF NEW.status = 'running' THEN
        NEW.actual_start_time := CURRENT_TIMESTAMP;
    END IF;

    IF NEW.status IN ('completed', 'invalid') THEN
        NEW.actual_end_time := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_transition
BEFORE UPDATE OF status ON experiments
FOR EACH ROW
EXECUTE FUNCTION validate_experiment_transition();

-- ------------------------------------------------------------
-- AUTOMATIC AUDIT LOGGING
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION log_experiment_status_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status <> OLD.status THEN
        INSERT INTO experiment_audit_log (
            experiment_id,
            action,
            previous_status,
            new_status,
            details
        )
        VALUES (
            NEW.experiment_id,
            'STATUS_CHANGE',
            OLD.status,
            NEW.status,
            jsonb_build_object(
                'experiment_key', NEW.experiment_key
            )
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_audit
AFTER UPDATE OF status ON experiments
FOR EACH ROW
EXECUTE FUNCTION log_experiment_status_change();

-- ------------------------------------------------------------
-- VALIDATE METRIC OBSERVATIONS
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_metric_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_metric metric_definitions%ROWTYPE;
    v_status experiment_status;
BEGIN
    SELECT *
    INTO v_metric
    FROM metric_definitions
    WHERE metric_id = NEW.metric_id
      AND experiment_id = NEW.experiment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Metric does not belong to experiment';
    END IF;

    SELECT status
    INTO v_status
    FROM experiments
    WHERE experiment_id = NEW.experiment_id;

    IF v_status <> 'running' THEN
        RAISE EXCEPTION 'Observations require a running experiment';
    END IF;

    IF v_metric.minimum_allowed IS NOT NULL
       AND NEW.numeric_value < v_metric.minimum_allowed THEN
        RAISE EXCEPTION 'Metric below minimum allowed value';
    END IF;

    IF v_metric.maximum_allowed IS NOT NULL
       AND NEW.numeric_value > v_metric.maximum_allowed THEN
        RAISE EXCEPTION 'Metric above maximum allowed value';
    END IF;

    IF v_metric.value_type = 'proportion'
       AND (NEW.numeric_value < 0 OR NEW.numeric_value > 1) THEN
        RAISE EXCEPTION 'Proportion must be between 0 and 1';
    END IF;

    IF v_metric.value_type IN ('count', 'duration')
       AND NEW.numeric_value < 0 THEN
        RAISE EXCEPTION 'Count and duration cannot be negative';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_observation
BEFORE INSERT OR UPDATE ON metric_observations
FOR EACH ROW
EXECUTE FUNCTION validate_metric_observation();

-- ------------------------------------------------------------
-- SAMPLE SIZE PLANNING PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE plan_experiment(
    p_experiment_key VARCHAR(80)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiments%ROWTYPE;
    v_required BIGINT;
BEGIN
    SELECT *
    INTO STRICT v_experiment
    FROM experiments
    WHERE experiment_key = p_experiment_key
    FOR UPDATE;

    IF v_experiment.status <> 'draft' THEN
        RAISE EXCEPTION 'Only draft experiments can be planned';
    END IF;

    v_required := calculate_sample_size(
        v_experiment.baseline_conversion,
        v_experiment.relative_mde,
        v_experiment.alpha,
        v_experiment.statistical_power
    );

    UPDATE experiments
    SET planned_sample_per_group = v_required
    WHERE experiment_id = v_experiment.experiment_id;

    RAISE NOTICE 'Required sample per group: %', v_required;
END;
$$;

-- ------------------------------------------------------------
-- EXPERIMENT START PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE start_experiment(
    p_experiment_key VARCHAR(80)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment_id BIGINT;
    v_status experiment_status;
    v_primary_count INTEGER;
    v_variant_count INTEGER;
    v_allocation NUMERIC;
BEGIN
    SELECT experiment_id, status
    INTO STRICT v_experiment_id, v_status
    FROM experiments
    WHERE experiment_key = p_experiment_key
    FOR UPDATE;

    IF v_status <> 'draft' THEN
        RAISE EXCEPTION 'Experiment must be in draft status';
    END IF;

    SELECT COUNT(*)
    INTO v_primary_count
    FROM metric_definitions
    WHERE experiment_id = v_experiment_id
      AND metric_category = 'primary';

    IF v_primary_count <> 1 THEN
        RAISE EXCEPTION 'Exactly one primary metric is required';
    END IF;

    SELECT COUNT(*), COALESCE(SUM(allocation_percentage), 0)
    INTO v_variant_count, v_allocation
    FROM experiment_variants
    WHERE experiment_id = v_experiment_id;

    IF v_variant_count <> 2 THEN
        RAISE EXCEPTION 'Exactly two variants are required';
    END IF;

    IF ABS(v_allocation - 1.0) > 0.000001 THEN
        RAISE EXCEPTION 'Variant allocations must total 1';
    END IF;

    UPDATE experiments
    SET status = 'running'
    WHERE experiment_id = v_experiment_id;
END;
$$;

-- ------------------------------------------------------------
-- USER-LEVEL ASSIGNMENT FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION assign_experiment_variant(
    p_experiment_key VARCHAR(80),
    p_participant_key VARCHAR(128)
)
RETURNS experiment_variant
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiments%ROWTYPE;
    v_existing experiment_assignments%ROWTYPE;
    v_bucket BIGINT;
    v_result experiment_variant;
    v_control BIGINT;
    v_treatment BIGINT;
BEGIN
    IF p_participant_key IS NULL
       OR LENGTH(TRIM(p_participant_key)) = 0 THEN
        RAISE EXCEPTION 'Participant key cannot be empty';
    END IF;

    SELECT *
    INTO STRICT v_experiment
    FROM experiments
    WHERE experiment_key = p_experiment_key;

    SELECT *
    INTO v_existing
    FROM experiment_assignments
    WHERE experiment_id = v_experiment.experiment_id
      AND participant_key = p_participant_key;

    IF FOUND THEN
        SELECT variant_name
        INTO v_result
        FROM experiment_variants
        WHERE variant_id = v_existing.variant_id;

        RETURN v_result;
    END IF;

    IF v_experiment.status <> 'running' THEN
        RAISE EXCEPTION 'Experiment is not running';
    END IF;

    -- Deterministic hash-based allocation.
    v_bucket := MOD(
        ('x' || SUBSTRING(
            ENCODE(
                DIGEST(
                    v_experiment.experiment_key || ':' ||
                    p_participant_key,
                    'sha256'
                ),
                'hex'
            ),
            1,
            8
        ))::BIT(32)::BIGINT,
        1000000
    );

    SELECT variant_id
    INTO v_control
    FROM experiment_variants
    WHERE experiment_id = v_experiment.experiment_id
      AND variant_name = 'control';

    SELECT variant_id
    INTO v_treatment
    FROM experiment_variants
    WHERE experiment_id = v_experiment.experiment_id
      AND variant_name = 'treatment';

    IF v_bucket < 500000 THEN
        v_result := 'control';
    ELSE
        v_result := 'treatment';
    END IF;

    INSERT INTO experiment_assignments (
        experiment_id,
        variant_id,
        participant_key
    )
    VALUES (
        v_experiment.experiment_id,
        CASE
            WHEN v_result = 'control' THEN v_control
            ELSE v_treatment
        END,
        p_participant_key
    );

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- EXPERIMENT METRIC REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW v_experiment_metric_summary AS
SELECT
    e.experiment_key,
    e.experiment_name,
    e.status,
    md.metric_name,
    md.metric_category,
    ev.variant_name,

    COUNT(DISTINCT a.assignment_id) AS assigned_users,

    COUNT(mo.observation_id) AS observed_users,

    AVG(mo.numeric_value) AS average_value,

    MIN(mo.numeric_value) AS minimum_value,

    MAX(mo.numeric_value) AS maximum_value,

    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY mo.numeric_value)
        AS p95_value

FROM experiments e

JOIN metric_definitions md
    ON md.experiment_id = e.experiment_id

JOIN experiment_assignments a
    ON a.experiment_id = e.experiment_id

JOIN experiment_variants ev
    ON ev.variant_id = a.variant_id

LEFT JOIN metric_observations mo
    ON mo.assignment_id = a.assignment_id
   AND mo.metric_id = md.metric_id

GROUP BY
    e.experiment_key,
    e.experiment_name,
    e.status,
    md.metric_name,
    md.metric_category,
    ev.variant_name;

-- ------------------------------------------------------------
-- SAMPLE SIZE AND PARTICIPATION REPORT
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW v_sample_size_progress AS
SELECT
    e.experiment_key,
    e.planned_sample_per_group,

    COUNT(a.assignment_id)
        FILTER (
            WHERE ev.variant_name = 'control'
        ) AS control_users,

    COUNT(a.assignment_id)
        FILTER (
            WHERE ev.variant_name = 'treatment'
        ) AS treatment_users,

    CASE
        WHEN e.planned_sample_per_group IS NULL THEN FALSE

        ELSE
            COUNT(a.assignment_id)
                FILTER (
                    WHERE ev.variant_name = 'control'
                ) >= e.planned_sample_per_group

            AND

            COUNT(a.assignment_id)
                FILTER (
                    WHERE ev.variant_name = 'treatment'
                ) >= e.planned_sample_per_group
    END AS sample_sufficient

FROM experiments e

LEFT JOIN experiment_assignments a
    ON a.experiment_id = e.experiment_id

LEFT JOIN experiment_variants ev
    ON ev.variant_id = a.variant_id

GROUP BY
    e.experiment_id,
    e.experiment_key,
    e.planned_sample_per_group;

-- ------------------------------------------------------------
-- GUARDRAIL EVALUATION VIEW
--
-- For each guardrail, compare treatment and control averages.
-- Thresholds are expressed in the metric's stored unit.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW v_guardrail_evaluation AS
WITH metric_values AS (
    SELECT
        e.experiment_key,
        md.metric_name,
        md.guardrail_threshold,
        md.higher_is_better,
        ev.variant_name,
        AVG(mo.numeric_value) AS metric_value

    FROM experiments e

    JOIN metric_definitions md
        ON md.experiment_id = e.experiment_id

    JOIN experiment_assignments a
        ON a.experiment_id = e.experiment_id

    JOIN experiment_variants ev
        ON ev.variant_id = a.variant_id

    JOIN metric_observations mo
        ON mo.assignment_id = a.assignment_id
       AND mo.metric_id = md.metric_id

    WHERE md.metric_category = 'guardrail'

    GROUP BY
        e.experiment_key,
        md.metric_name,
        md.guardrail_threshold,
        md.higher_is_better,
        ev.variant_name
)
SELECT
    experiment_key,
    metric_name,

    MAX(metric_value)
        FILTER (WHERE variant_name = 'control')
        AS control_value,

    MAX(metric_value)
        FILTER (WHERE variant_name = 'treatment')
        AS treatment_value,

    MAX(guardrail_threshold) AS threshold,

    MAX(higher_is_better::INTEGER) = 1 AS higher_is_better,

    CASE
        WHEN MAX(higher_is_better::INTEGER) = 1 THEN
            MAX(metric_value)
                FILTER (WHERE variant_name = 'treatment')
            >=
            MAX(metric_value)
                FILTER (WHERE variant_name = 'control')
            - MAX(guardrail_threshold)

        ELSE
            MAX(metric_value)
                FILTER (WHERE variant_name = 'treatment')
            <=
            MAX(metric_value)
                FILTER (WHERE variant_name = 'control')
            + MAX(guardrail_threshold)
    END AS guardrail_passed

FROM metric_values

GROUP BY experiment_key, metric_name;

-- ------------------------------------------------------------
-- SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO experiments (
    experiment_key,
    experiment_name,
    description,
    baseline_conversion,
    relative_mde,
    alpha,
    statistical_power,
    traffic_allocation
)
VALUES (
    'EXP-CHECKOUT-001',
    'Checkout Redesign',
    'Evaluate a redesigned checkout experience',
    0.10,
    0.10,
    0.05,
    0.80,
    1.00
);

INSERT INTO metric_definitions (
    experiment_id,
    metric_name,
    metric_category,
    value_type,
    unit,
    higher_is_better,
    guardrail_threshold,
    metric_description
)
SELECT
    experiment_id,
    'conversion_rate',
    'primary',
    'proportion',
    'ratio',
    TRUE,
    NULL,
    'Percentage of assigned users completing checkout'
FROM experiments
WHERE experiment_key = 'EXP-CHECKOUT-001';

INSERT INTO metric_definitions (
    experiment_id,
    metric_name,
    metric_category,
    value_type,
    unit,
    higher_is_better,
    metric_description
)
SELECT
    experiment_id,
    'revenue_per_conversion',
    'secondary',
    'continuous',
    'currency',
    TRUE,
    'Average revenue per converted user'
FROM experiments
WHERE experiment_key = 'EXP-CHECKOUT-001';

INSERT INTO metric_definitions (
    experiment_id,
    metric_name,
    metric_category,
    value_type,
    unit,
    higher_is_better,
    guardrail_threshold,
    metric_description
)
SELECT
    experiment_id,
    'refund_rate',
    'guardrail',
    'proportion',
    'ratio',
    FALSE,
    0.02,
    'Maximum acceptable absolute increase in refund rate'
FROM experiments
WHERE experiment_key = 'EXP-CHECKOUT-001';

INSERT INTO metric_definitions (
    experiment_id,
    metric_name,
    metric_category,
    value_type,
    unit,
    higher_is_better,
    guardrail_threshold,
    metric_description
)
SELECT
    experiment_id,
    'p95_latency',
    'guardrail',
    'duration',
    'milliseconds',
    FALSE,
    40,
    'Maximum acceptable increase in p95 response latency'
FROM experiments
WHERE experiment_key = 'EXP-CHECKOUT-001';

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    allocation_percentage,
    description
)
SELECT
    experiment_id,
    'control',
    0.50,
    'Existing checkout'
FROM experiments
WHERE experiment_key = 'EXP-CHECKOUT-001';

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    allocation_percentage,
    description
)
SELECT
    experiment_id,
    'treatment',
    0.50,
    'Redesigned checkout'
FROM experiments
WHERE experiment_key = 'EXP-CHECKOUT-001';

-- Calculate planned sample size.
CALL plan_experiment('EXP-CHECKOUT-001');

-- Start the experiment.
CALL start_experiment('EXP-CHECKOUT-001');

-- ------------------------------------------------------------
-- SAMPLE USER ASSIGNMENTS
-- ------------------------------------------------------------

DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..1000 LOOP
        PERFORM assign_experiment_variant(
            'EXP-CHECKOUT-001',
            'customer-' || i
        );
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- GENERATE REPRODUCIBLE EXAMPLE OBSERVATIONS
--
-- This dataset is synthetic and intended to demonstrate
-- relational workflow and metric aggregation.
-- ------------------------------------------------------------

INSERT INTO metric_observations (
    assignment_id,
    experiment_id,
    metric_id,
    numeric_value
)
SELECT
    a.assignment_id,
    a.experiment_id,
    md.metric_id,

    CASE md.metric_name

        WHEN 'conversion_rate' THEN
            CASE
                WHEN ev.variant_name = 'control' THEN
                    CASE
                        WHEN MOD(a.assignment_id, 10) = 0
                        THEN 1 ELSE 0
                    END
                ELSE
                    CASE
                        WHEN MOD(a.assignment_id, 10) IN (0, 1)
                        THEN 1 ELSE 0
                    END
            END

        WHEN 'revenue_per_conversion' THEN
            CASE
                WHEN ev.variant_name = 'control' THEN
                    100 + MOD(a.assignment_id, 50)
                ELSE
                    110 + MOD(a.assignment_id, 50)
            END

        WHEN 'refund_rate' THEN
            CASE
                WHEN MOD(a.assignment_id, 29) = 0 THEN 1
                ELSE 0
            END

        WHEN 'p95_latency' THEN
            CASE
                WHEN ev.variant_name = 'control' THEN
                    180 + MOD(a.assignment_id, 30)
                ELSE
                    190 + MOD(a.assignment_id, 30)
            END

    END

FROM experiment_assignments a

JOIN experiment_variants ev
    ON ev.variant_id = a.variant_id

JOIN metric_definitions md
    ON md.experiment_id = a.experiment_id

WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_key = 'EXP-CHECKOUT-001'
);

-- ------------------------------------------------------------
-- RETRIEVAL QUERY
-- ------------------------------------------------------------

SELECT *
FROM v_experiment_metric_summary
WHERE experiment_key = 'EXP-CHECKOUT-001'
ORDER BY metric_category, metric_name, variant_name;

-- ------------------------------------------------------------
-- SAMPLE SIZE VALIDATION
-- ------------------------------------------------------------

SELECT *
FROM v_sample_size_progress
WHERE experiment_key = 'EXP-CHECKOUT-001';

-- ------------------------------------------------------------
-- GUARDRAIL VALIDATION
-- ------------------------------------------------------------

SELECT *
FROM v_guardrail_evaluation
WHERE experiment_key = 'EXP-CHECKOUT-001';

-- ------------------------------------------------------------
-- AGGREGATION: PRIMARY METRIC COMPARISON
-- ------------------------------------------------------------

WITH primary_results AS (
    SELECT
        e.experiment_key,
        ev.variant_name,

        AVG(mo.numeric_value) AS conversion_rate,

        COUNT(*) AS observations

    FROM experiments e

    JOIN metric_definitions md
        ON md.experiment_id = e.experiment_id

    JOIN metric_observations mo
        ON mo.metric_id = md.metric_id

    JOIN experiment_assignments a
        ON a.assignment_id = mo.assignment_id

    JOIN experiment_variants ev
        ON ev.variant_id = a.variant_id

    WHERE e.experiment_key = 'EXP-CHECKOUT-001'
      AND md.metric_category = 'primary'

    GROUP BY
        e.experiment_key,
        ev.variant_name
)
SELECT
    experiment_key,

    MAX(conversion_rate)
        FILTER (WHERE variant_name = 'control')
        AS control_conversion,

    MAX(conversion_rate)
        FILTER (WHERE variant_name = 'treatment')
        AS treatment_conversion,

    MAX(observations)
        FILTER (WHERE variant_name = 'control')
        AS control_sample,

    MAX(observations)
        FILTER (WHERE variant_name = 'treatment')
        AS treatment_sample

FROM primary_results

GROUP BY experiment_key;

-- ------------------------------------------------------------
-- VALIDATION: MISSING OBSERVATIONS
-- ------------------------------------------------------------

SELECT
    a.assignment_id,
    a.participant_key,
    md.metric_name

FROM experiment_assignments a

JOIN metric_definitions md
    ON md.experiment_id = a.experiment_id

LEFT JOIN metric_observations mo
    ON mo.assignment_id = a.assignment_id
   AND mo.metric_id = md.metric_id

WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_key = 'EXP-CHECKOUT-001'
)

AND mo.observation_id IS NULL;

-- ------------------------------------------------------------
-- WORKFLOW: RECORD EVALUATION
--
-- Statistical p-values must be computed by a validated
-- statistical analysis service. This statement stores an
-- externally calculated result rather than treating an
-- arbitrary SQL aggregate as a significance test.
-- ------------------------------------------------------------

INSERT INTO experiment_evaluations (
    experiment_id,
    control_sample_size,
    treatment_sample_size,
    primary_control_value,
    primary_treatment_value,
    absolute_effect,
    relative_effect,
    p_value,
    significance_level,
    sample_sufficient,
    guardrails_passed,
    decision,
    evaluation_notes
)
SELECT
    e.experiment_id,

    COALESCE(s.control_users, 0),

    COALESCE(s.treatment_users, 0),

    COALESCE(p.control_value, 0),

    COALESCE(p.treatment_value, 0),

    COALESCE(p.treatment_value, 0) -
        COALESCE(p.control_value, 0),

    CASE
        WHEN COALESCE(p.control_value, 0) = 0 THEN NULL
        ELSE
            (
                COALESCE(p.treatment_value, 0) -
                p.control_value
            ) / p.control_value
    END,

    NULL,

    e.alpha,

    COALESCE(s.sample_sufficient, FALSE),

    COALESCE(g.guardrails_passed, FALSE),

    'inconclusive',

    'Descriptive database evaluation. Statistical significance requires a separately calculated p-value.'

FROM experiments e

LEFT JOIN v_sample_size_progress s
    ON s.experiment_key = e.experiment_key

LEFT JOIN (
    SELECT
        experiment_key,

        MAX(metric_value)
            FILTER (WHERE variant_name = 'control')
            AS control_value,

        MAX(metric_value)
            FILTER (WHERE variant_name = 'treatment')
            AS treatment_value

    FROM (
        SELECT
            e.experiment_key,
            ev.variant_name,
            AVG(mo.numeric_value) AS metric_value

        FROM experiments e

        JOIN metric_definitions md
            ON md.experiment_id = e.experiment_id

        JOIN metric_observations mo
            ON mo.metric_id = md.metric_id

        JOIN experiment_assignments a
            ON a.assignment_id = mo.assignment_id

        JOIN experiment_variants ev
            ON ev.variant_id = a.variant_id

        WHERE md.metric_category = 'primary'

        GROUP BY
            e.experiment_key,
            ev.variant_name
    ) values_by_variant

    GROUP BY experiment_key
) p
    ON p.experiment_key = e.experiment_key

LEFT JOIN (
    SELECT
        experiment_key,
        BOOL_AND(guardrail_passed) AS guardrails_passed
    FROM v_guardrail_evaluation
    GROUP BY experiment_key
) g
    ON g.experiment_key = e.experiment_key

WHERE e.experiment_key = 'EXP-CHECKOUT-001';

-- ------------------------------------------------------------
-- FAILURE CASE: INVALID SAMPLE SIZE INPUT
-- The following example is intentionally commented out.
--
-- SELECT calculate_sample_size(1.2, 0.10, 0.05, 0.80);
--
-- Expected behavior: exception for invalid baseline conversion.
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- REPORTING: FINAL EXPERIMENT DASHBOARD
-- ------------------------------------------------------------

SELECT
    e.experiment_key,
    e.experiment_name,
    e.status,

    e.baseline_conversion,
    e.relative_mde,
    e.alpha,
    e.statistical_power,
    e.planned_sample_per_group,

    s.control_users,
    s.treatment_users,
    s.sample_sufficient,

    evaluation.decision,
    evaluation.p_value,
    evaluation.guardrails_passed,
    evaluation.evaluated_at

FROM experiments e

LEFT JOIN v_sample_size_progress s
    ON s.experiment_key = e.experiment_key

LEFT JOIN LATERAL (
    SELECT *
    FROM experiment_evaluations ee
    WHERE ee.experiment_id = e.experiment_id
    ORDER BY evaluated_at DESC
    LIMIT 1
) evaluation ON TRUE

WHERE e.experiment_key = 'EXP-CHECKOUT-001';

COMMIT;

-- ============================================================
-- END OF EXPERIMENT METRICS MANAGEMENT SYSTEM
-- ============================================================
