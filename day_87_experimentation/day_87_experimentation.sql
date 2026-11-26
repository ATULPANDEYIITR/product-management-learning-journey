-- ============================================================
-- EXPERIMENTATION MANAGEMENT AND ANALYTICS
-- PostgreSQL 15+
--
-- Models:
-- Research questions
-- Hypotheses
-- Experimental designs
-- Control and treatment variants
-- Participant randomization
-- Observations and outcomes
-- Metrics and guardrails
-- Statistical analysis
-- Experiment decisions
-- Audit history
--
-- Execute as a database user with schema creation privileges.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS experimentation;

SET search_path TO experimentation, public;


-- ============================================================
-- 1. ENUMERATED DOMAIN TYPES
-- ============================================================

CREATE TYPE experiment_status AS ENUM (
    'draft',
    'running',
    'completed',
    'cancelled'
);

CREATE TYPE variant_type AS ENUM (
    'control',
    'treatment'
);

CREATE TYPE hypothesis_direction AS ENUM (
    'increase',
    'decrease',
    'different'
);

CREATE TYPE experiment_decision AS ENUM (
    'reject_null',
    'fail_to_reject_null',
    'invalid'
);

CREATE TYPE observation_status AS ENUM (
    'valid',
    'excluded',
    'invalid'
);


-- ============================================================
-- 2. EXPERIMENT OWNERS AND RESEARCHERS
-- ============================================================

CREATE TABLE researchers (
    researcher_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(full_name)) > 0)
);


-- ============================================================
-- 3. EXPERIMENT DEFINITIONS
-- ============================================================

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_code VARCHAR(40) NOT NULL UNIQUE,
    experiment_name VARCHAR(200) NOT NULL,

    research_question TEXT NOT NULL,
    null_hypothesis TEXT NOT NULL,
    alternative_hypothesis TEXT NOT NULL,

    primary_metric VARCHAR(100) NOT NULL,

    expected_direction hypothesis_direction NOT NULL,

    significance_level NUMERIC(6,5) NOT NULL DEFAULT 0.05,
    statistical_power NUMERIC(6,5) NOT NULL DEFAULT 0.80,

    baseline_rate NUMERIC(10,8) NOT NULL,
    minimum_detectable_effect NUMERIC(10,8) NOT NULL,

    minimum_group_size INTEGER NOT NULL DEFAULT 30,

    random_seed BIGINT NOT NULL DEFAULT 42,

    status experiment_status NOT NULL DEFAULT 'draft',

    owner_id BIGINT NOT NULL REFERENCES researchers(researcher_id),

    planned_start TIMESTAMPTZ,
    planned_end TIMESTAMPTZ,

    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(experiment_name)) > 0),
    CHECK (length(trim(research_question)) > 0),
    CHECK (length(trim(null_hypothesis)) > 0),
    CHECK (length(trim(alternative_hypothesis)) > 0),

    CHECK (significance_level > 0 AND significance_level < 1),
    CHECK (statistical_power > 0 AND statistical_power < 1),

    CHECK (baseline_rate > 0 AND baseline_rate < 1),
    CHECK (minimum_detectable_effect > 0),

    CHECK (minimum_group_size >= 2),

    CHECK (
        planned_end IS NULL
        OR planned_start IS NULL
        OR planned_end > planned_start
    )
);


-- ============================================================
-- 4. EXPERIMENT VARIANTS
-- ============================================================

CREATE TABLE experiment_variants (
    variant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id),

    variant_name VARCHAR(100) NOT NULL,

    variant_kind variant_type NOT NULL,

    allocation_weight NUMERIC(8,6) NOT NULL,

    intervention_description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (experiment_id, variant_name),

    UNIQUE (experiment_id, variant_kind),

    CHECK (allocation_weight > 0 AND allocation_weight <= 1),

    CHECK (length(trim(intervention_description)) > 0)
);

CREATE INDEX idx_variants_experiment
ON experiment_variants(experiment_id);


-- ============================================================
-- 5. PARTICIPANT ASSIGNMENT
-- ============================================================

CREATE TABLE participants (
    participant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    external_subject_key VARCHAR(150) NOT NULL UNIQUE,

    consented BOOLEAN NOT NULL DEFAULT FALSE,

    eligible BOOLEAN NOT NULL DEFAULT TRUE,

    registered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assignments (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id),

    participant_id BIGINT NOT NULL
        REFERENCES participants(participant_id),

    variant_id BIGINT NOT NULL
        REFERENCES experiment_variants(variant_id),

    assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    randomization_key VARCHAR(100) NOT NULL,

    UNIQUE (experiment_id, participant_id),

    UNIQUE (experiment_id, randomization_key),

    UNIQUE (assignment_id, experiment_id, variant_id)
);

CREATE INDEX idx_assignments_experiment_variant
ON assignments(experiment_id, variant_id);

CREATE INDEX idx_assignments_participant
ON assignments(participant_id);


-- ============================================================
-- 6. METRIC DEFINITIONS
-- ============================================================

CREATE TABLE metric_definitions (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_code VARCHAR(100) NOT NULL UNIQUE,

    metric_name VARCHAR(150) NOT NULL,

    metric_description TEXT NOT NULL,

    is_guardrail BOOLEAN NOT NULL DEFAULT FALSE,

    higher_is_better BOOLEAN NOT NULL DEFAULT TRUE,

    maximum_allowed_increase NUMERIC(12,6),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        maximum_allowed_increase IS NULL
        OR maximum_allowed_increase >= 0
    )
);


-- ============================================================
-- 7. OBSERVATIONS
-- ============================================================

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assignment_id BIGINT NOT NULL
        REFERENCES assignments(assignment_id),

    metric_id BIGINT NOT NULL
        REFERENCES metric_definitions(metric_id),

    numeric_value NUMERIC(20,8) NOT NULL,

    status observation_status NOT NULL DEFAULT 'valid',

    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (assignment_id, metric_id),

    CHECK (
        numeric_value > '-Infinity'::NUMERIC
        AND numeric_value < 'Infinity'::NUMERIC
    )
);

CREATE INDEX idx_observations_metric
ON observations(metric_id, status);

CREATE INDEX idx_observations_time
ON observations(observed_at);


-- ============================================================
-- 8. ANALYSIS RESULTS
-- ============================================================

CREATE TABLE analysis_results (
    analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id),

    analysis_version INTEGER NOT NULL DEFAULT 1,

    control_sample_size INTEGER NOT NULL,

    treatment_sample_size INTEGER NOT NULL,

    control_metric_value NUMERIC(20,10) NOT NULL,

    treatment_metric_value NUMERIC(20,10) NOT NULL,

    absolute_effect NUMERIC(20,10) NOT NULL,

    relative_effect NUMERIC(20,10),

    z_score NUMERIC(20,10),

    p_value NUMERIC(20,10),

    confidence_lower NUMERIC(20,10),

    confidence_upper NUMERIC(20,10),

    guardrail_passed BOOLEAN NOT NULL,

    decision experiment_decision NOT NULL,

    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (experiment_id, analysis_version),

    CHECK (analysis_version > 0),

    CHECK (control_sample_size >= 0),
    CHECK (treatment_sample_size >= 0),

    CHECK (
        p_value IS NULL
        OR (p_value >= 0 AND p_value <= 1)
    ),

    CHECK (
        confidence_lower IS NULL
        OR confidence_upper IS NULL
        OR confidence_lower <= confidence_upper
    )
);

CREATE INDEX idx_analysis_decision
ON analysis_results(decision, analyzed_at DESC);


-- ============================================================
-- 9. AUDIT EVENTS
-- ============================================================

CREATE TABLE experiment_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id),

    event_type VARCHAR(100) NOT NULL,

    event_description TEXT NOT NULL,

    event_data JSONB NOT NULL DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_experiment_audit
ON experiment_audit(experiment_id, created_at);


-- ============================================================
-- 10. LIFECYCLE VALIDATION TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION validate_experiment_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF OLD.status = 'draft' AND NEW.status = 'running' THEN

        IF NOT EXISTS (
            SELECT 1
            FROM experiment_variants
            WHERE experiment_id = NEW.experiment_id
              AND variant_kind = 'control'
        ) THEN
            RAISE EXCEPTION
                'A control variant is required before execution.';
        END IF;

        IF NOT EXISTS (
            SELECT 1
            FROM experiment_variants
            WHERE experiment_id = NEW.experiment_id
              AND variant_kind = 'treatment'
        ) THEN
            RAISE EXCEPTION
                'A treatment variant is required before execution.';
        END IF;

        IF (
            SELECT COUNT(*)
            FROM experiment_variants
            WHERE experiment_id = NEW.experiment_id
        ) <> 2 THEN
            RAISE EXCEPTION
                'This two-arm design requires exactly two variants.';
        END IF;

        IF (
            SELECT COALESCE(SUM(allocation_weight), 0)
            FROM experiment_variants
            WHERE experiment_id = NEW.experiment_id
        ) <> 1 THEN
            RAISE EXCEPTION
                'Variant allocation weights must total 1.';
        END IF;

        NEW.actual_start := CURRENT_TIMESTAMP;

    ELSIF OLD.status = 'running' AND NEW.status = 'completed' THEN

        NEW.actual_end := CURRENT_TIMESTAMP;

    ELSIF OLD.status = 'running' AND NEW.status = 'cancelled' THEN

        NEW.actual_end := CURRENT_TIMESTAMP;

    ELSIF OLD.status = 'draft' AND NEW.status = 'cancelled' THEN

        NEW.actual_end := CURRENT_TIMESTAMP;

    ELSIF OLD.status = NEW.status THEN

        RETURN NEW;

    ELSE

        RAISE EXCEPTION
            'Invalid experiment state transition: % to %',
            OLD.status,
            NEW.status;

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_experiment_transition
BEFORE UPDATE OF status ON experiments
FOR EACH ROW
EXECUTE FUNCTION validate_experiment_transition();


-- ============================================================
-- 11. CROSS-ENTITY ASSIGNMENT VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_assignment_variant()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    variant_experiment BIGINT;
BEGIN

    SELECT experiment_id
    INTO variant_experiment
    FROM experiment_variants
    WHERE variant_id = NEW.variant_id;

    IF variant_experiment IS NULL THEN
        RAISE EXCEPTION 'Variant does not exist.';
    END IF;

    IF variant_experiment <> NEW.experiment_id THEN
        RAISE EXCEPTION
            'Variant belongs to a different experiment.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM experiments
        WHERE experiment_id = NEW.experiment_id
          AND status = 'running'
    ) THEN
        RAISE EXCEPTION
            'Participants can only be assigned to running experiments.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM participants
        WHERE participant_id = NEW.participant_id
          AND consented = TRUE
          AND eligible = TRUE
    ) THEN
        RAISE EXCEPTION
            'Participant is not consented and eligible.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_assignment
BEFORE INSERT ON assignments
FOR EACH ROW
EXECUTE FUNCTION validate_assignment_variant();


-- ============================================================
-- 12. CROSS-ENTITY OBSERVATION VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF NOT EXISTS (
        SELECT 1
        FROM assignments a
        JOIN experiments e
          ON e.experiment_id = a.experiment_id
        WHERE a.assignment_id = NEW.assignment_id
          AND e.status = 'running'
    ) THEN
        RAISE EXCEPTION
            'Observations require an active experiment assignment.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_observation
BEFORE INSERT ON observations
FOR EACH ROW
EXECUTE FUNCTION validate_observation();


-- ============================================================
-- 13. RANDOMIZED ASSIGNMENT PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE assign_participants(
    p_experiment_id BIGINT,
    p_participant_ids BIGINT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_control BIGINT;
    v_treatment BIGINT;
    v_total BIGINT;
BEGIN

    IF p_participant_ids IS NULL
       OR cardinality(p_participant_ids) = 0 THEN
        RAISE EXCEPTION 'Participant list cannot be empty.';
    END IF;

    IF cardinality(p_participant_ids) <> (
        SELECT COUNT(DISTINCT participant_id)
        FROM unnest(p_participant_ids) AS participant_id
    ) THEN
        RAISE EXCEPTION 'Duplicate participant identifiers supplied.';
    END IF;

    SELECT variant_id
    INTO v_control
    FROM experiment_variants
    WHERE experiment_id = p_experiment_id
      AND variant_kind = 'control';

    SELECT variant_id
    INTO v_treatment
    FROM experiment_variants
    WHERE experiment_id = p_experiment_id
      AND variant_kind = 'treatment';

    IF v_control IS NULL OR v_treatment IS NULL THEN
        RAISE EXCEPTION 'Both experiment variants are required.';
    END IF;

    IF (
        SELECT status
        FROM experiments
        WHERE experiment_id = p_experiment_id
    ) <> 'running' THEN
        RAISE EXCEPTION 'Experiment is not running.';
    END IF;

    SELECT COUNT(*)
    INTO v_total
    FROM unnest(p_participant_ids);

    IF v_total < 2 THEN
        RAISE EXCEPTION 'At least two participants are required.';
    END IF;

    -- Random ordering allocates participants across the two groups.
    -- The experiment random seed is used as a reproducibility reference
    -- in the audit record; production randomization should use a
    -- controlled assignment service with a persistent allocation log.

    INSERT INTO assignments (
        experiment_id,
        participant_id,
        variant_id,
        randomization_key
    )
    SELECT
        p_experiment_id,
        participant_id,
        CASE
            WHEN row_number % 2 = 1 THEN v_control
            ELSE v_treatment
        END,
        md5(
            p_experiment_id::TEXT || ':' ||
            participant_id::TEXT
        )
    FROM (
        SELECT
            participant_id,
            ROW_NUMBER() OVER (ORDER BY random()) AS row_number
        FROM unnest(p_participant_ids) AS participant_id
    ) randomized;

    INSERT INTO experiment_audit (
        experiment_id,
        event_type,
        event_description,
        event_data
    )
    VALUES (
        p_experiment_id,
        'PARTICIPANTS_ASSIGNED',
        'Randomized participant allocation completed.',
        jsonb_build_object('participant_count', v_total)
    );

END;
$$;


-- ============================================================
-- 14. METRIC AGGREGATION VIEW
-- ============================================================

CREATE OR REPLACE VIEW experiment_group_metrics AS
SELECT
    a.experiment_id,
    v.variant_id,
    v.variant_name,
    v.variant_kind,
    m.metric_id,
    m.metric_code,
    m.is_guardrail,

    COUNT(o.observation_id) FILTER (
        WHERE o.status = 'valid'
    ) AS observation_count,

    COALESCE(
        AVG(o.numeric_value) FILTER (
            WHERE o.status = 'valid'
        ),
        0
    ) AS mean_metric_value,

    COALESCE(
        SUM(o.numeric_value) FILTER (
            WHERE o.status = 'valid'
        ),
        0
    ) AS total_metric_value

FROM assignments a

JOIN experiment_variants v
    ON v.variant_id = a.variant_id

CROSS JOIN metric_definitions m

LEFT JOIN observations o
    ON o.assignment_id = a.assignment_id
   AND o.metric_id = m.metric_id

GROUP BY
    a.experiment_id,
    v.variant_id,
    v.variant_name,
    v.variant_kind,
    m.metric_id,
    m.metric_code,
    m.is_guardrail;


-- ============================================================
-- 15. EXPERIMENT ELIGIBILITY FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION experiment_is_ready(
    p_experiment_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_status experiment_status;
    v_variants INTEGER;
    v_total_weight NUMERIC;
BEGIN

    SELECT status
    INTO v_status
    FROM experiments
    WHERE experiment_id = p_experiment_id;

    IF NOT FOUND OR v_status <> 'draft' THEN
        RETURN FALSE;
    END IF;

    SELECT
        COUNT(*),
        COALESCE(SUM(allocation_weight), 0)
    INTO
        v_variants,
        v_total_weight
    FROM experiment_variants
    WHERE experiment_id = p_experiment_id;

    RETURN (
        v_variants = 2
        AND v_total_weight = 1
        AND EXISTS (
            SELECT 1
            FROM experiment_variants
            WHERE experiment_id = p_experiment_id
              AND variant_kind = 'control'
        )
        AND EXISTS (
            SELECT 1
            FROM experiment_variants
            WHERE experiment_id = p_experiment_id
              AND variant_kind = 'treatment'
        )
    );
END;
$$;


-- ============================================================
-- 16. STATISTICAL ANALYSIS FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION analyze_conversion_experiment(
    p_experiment_id BIGINT,
    p_metric_code VARCHAR,
    p_guardrail_passed BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    control_n BIGINT,
    treatment_n BIGINT,
    control_rate NUMERIC,
    treatment_rate NUMERIC,
    absolute_effect NUMERIC,
    relative_effect NUMERIC,
    z_score NUMERIC,
    p_value NUMERIC,
    decision experiment_decision
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_control_n BIGINT;
    v_treatment_n BIGINT;

    v_control_x BIGINT;
    v_treatment_x BIGINT;

    v_control_rate NUMERIC;
    v_treatment_rate NUMERIC;

    v_pooled NUMERIC;
    v_se NUMERIC;
    v_effect NUMERIC;
    v_z NUMERIC;
    v_p NUMERIC;

    v_alpha NUMERIC;
    v_minimum INTEGER;

    v_direction hypothesis_direction;

    v_favorable BOOLEAN;
    v_decision experiment_decision;

    v_metric_id BIGINT;
BEGIN

    SELECT
        e.significance_level,
        e.minimum_group_size,
        e.expected_direction
    INTO
        v_alpha,
        v_minimum,
        v_direction
    FROM experiments e
    WHERE e.experiment_id = p_experiment_id
      AND e.status = 'running';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Experiment does not exist or is not running.';
    END IF;

    SELECT metric_id
    INTO v_metric_id
    FROM metric_definitions
    WHERE metric_code = p_metric_code;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown metric.';
    END IF;

    -- This example uses binary conversion observations:
    -- 1 represents conversion and 0 represents no conversion.

    SELECT
        COUNT(*) FILTER (WHERE v.variant_kind = 'control'),
        COUNT(*) FILTER (
            WHERE v.variant_kind = 'treatment'
        ),

        COUNT(*) FILTER (
            WHERE v.variant_kind = 'control'
              AND o.numeric_value = 1
        ),

        COUNT(*) FILTER (
            WHERE v.variant_kind = 'treatment'
              AND o.numeric_value = 1
        )

    INTO
        v_control_n,
        v_treatment_n,
        v_control_x,
        v_treatment_x

    FROM assignments a

    JOIN experiment_variants v
        ON v.variant_id = a.variant_id

    JOIN observations o
        ON o.assignment_id = a.assignment_id
       AND o.metric_id = v_metric_id
       AND o.status = 'valid'

    WHERE a.experiment_id = p_experiment_id;

    IF
        v_control_n < v_minimum
        OR v_treatment_n < v_minimum
    THEN
        RAISE EXCEPTION 'Insufficient valid observations.';
    END IF;

    IF v_control_x > v_control_n
       OR v_treatment_x > v_treatment_n THEN
        RAISE EXCEPTION 'Invalid conversion counts.';
    END IF;

    v_control_rate :=
        v_control_x::NUMERIC / v_control_n;

    v_treatment_rate :=
        v_treatment_x::NUMERIC / v_treatment_n;

    v_pooled :=
        (v_control_x + v_treatment_x)::NUMERIC
        / (v_control_n + v_treatment_n);

    v_se := sqrt(
        v_pooled * (1 - v_pooled) *
        (
            1.0 / v_control_n +
            1.0 / v_treatment_n
        )
    );

    IF v_se = 0 THEN
        RAISE EXCEPTION 'Statistical variance is zero.';
    END IF;

    v_effect := v_treatment_rate - v_control_rate;

    v_z := v_effect / v_se;

    v_p := 2 * (
        1 - 0.5 * (
            1 + sign(v_z) * (
                1 - exp(
                    -0.717 * abs(v_z)
                    -0.416 * power(v_z, 2)
                )
            )
        )
    );

    -- Use a bounded normal-tail approximation for reporting.
    -- For formal regulatory inference, replace this approximation
    -- with a validated statistical implementation.

    v_p := LEAST(1, GREATEST(0, v_p));

    v_favorable := CASE v_direction
        WHEN 'increase' THEN v_effect > 0
        WHEN 'decrease' THEN v_effect < 0
        WHEN 'different' THEN TRUE
    END;

    IF NOT p_guardrail_passed THEN
        v_decision := 'invalid';
    ELSIF v_p < v_alpha AND v_favorable THEN
        v_decision := 'reject_null';
    ELSE
        v_decision := 'fail_to_reject_null';
    END IF;

    RETURN QUERY
    SELECT
        v_control_n,
        v_treatment_n,
        v_control_rate,
        v_treatment_rate,
        v_effect,
        CASE
            WHEN v_control_rate > 0
            THEN v_effect / v_control_rate
            ELSE NULL
        END,
        v_z,
        v_p,
        v_decision;

END;
$$;


-- ============================================================
-- 17. RESEARCHER SAMPLE DATA
-- ============================================================

INSERT INTO researchers (
    full_name,
    email,
    department
)
VALUES
(
    'Research Analyst',
    'analyst@example.org',
    'Product Analytics'
),
(
    'Experiment Manager',
    'manager@example.org',
    'Digital Product Research'
);


-- ============================================================
-- 18. METRIC DEFINITIONS
-- ============================================================

INSERT INTO metric_definitions (
    metric_code,
    metric_name,
    metric_description,
    is_guardrail,
    higher_is_better,
    maximum_allowed_increase
)
VALUES
(
    'purchase_conversion',
    'Purchase Conversion',
    'Binary indicator of successful purchase completion.',
    FALSE,
    TRUE,
    NULL
),
(
    'checkout_error',
    'Checkout Error Rate',
    'Binary indicator of checkout processing errors.',
    TRUE,
    FALSE,
    0.01
),
(
    'session_duration',
    'Session Duration',
    'Duration of the participant session in seconds.',
    FALSE,
    TRUE,
    NULL
);


-- ============================================================
-- 19. EXPERIMENT SAMPLE DATA
-- ============================================================

INSERT INTO experiments (
    experiment_code,
    experiment_name,
    research_question,
    null_hypothesis,
    alternative_hypothesis,
    primary_metric,
    expected_direction,
    significance_level,
    statistical_power,
    baseline_rate,
    minimum_detectable_effect,
    minimum_group_size,
    random_seed,
    owner_id,
    planned_start,
    planned_end
)
VALUES
(
    'EXP-001',
    'Checkout Optimization',
    'Does a redesigned checkout increase purchase conversion?',
    'The redesigned checkout does not change conversion.',
    'The redesigned checkout increases conversion.',
    'purchase_conversion',
    'increase',
    0.05,
    0.80,
    0.10,
    0.025,
    30,
    42,
    1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '14 days'
),
(
    'EXP-002',
    'Search Interface Experiment',
    'Does a revised search interface improve conversion?',
    'The revised search interface does not change conversion.',
    'The revised search interface increases conversion.',
    'purchase_conversion',
    'increase',
    0.05,
    0.80,
    0.12,
    0.03,
    30,
    99,
    2,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '14 days'
);


-- ============================================================
-- 20. VARIANT DEFINITIONS
-- ============================================================

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    variant_kind,
    allocation_weight,
    intervention_description
)
SELECT
    experiment_id,
    'Existing Checkout',
    'control',
    0.50,
    'Existing checkout experience.'
FROM experiments
WHERE experiment_code = 'EXP-001';

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    variant_kind,
    allocation_weight,
    intervention_description
)
SELECT
    experiment_id,
    'Redesigned Checkout',
    'treatment',
    0.50,
    'Redesigned checkout with simplified purchase steps.'
FROM experiments
WHERE experiment_code = 'EXP-001';

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    variant_kind,
    allocation_weight,
    intervention_description
)
SELECT
    experiment_id,
    'Existing Search',
    'control',
    0.50,
    'Existing search interface.'
FROM experiments
WHERE experiment_code = 'EXP-002';

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    variant_kind,
    allocation_weight,
    intervention_description
)
SELECT
    experiment_id,
    'Revised Search',
    'treatment',
    0.50,
    'Search interface with improved filtering.'
FROM experiments
WHERE experiment_code = 'EXP-002';


-- ============================================================
-- 21. VALIDATION AND READINESS REPORT
-- ============================================================

SELECT
    experiment_code,
    experiment_name,
    experiment_is_ready(experiment_id) AS ready_to_start
FROM experiments
ORDER BY experiment_id;


-- ============================================================
-- 22. START EXPERIMENT
-- ============================================================

UPDATE experiments
SET status = 'running'
WHERE experiment_code = 'EXP-001';


-- ============================================================
-- 23. PARTICIPANT REGISTRATION
-- ============================================================

INSERT INTO participants (
    external_subject_key,
    consented,
    eligible
)
SELECT
    'SUBJECT-' || generate_series,
    TRUE,
    TRUE
FROM generate_series(1, 2000);


-- ============================================================
-- 24. RANDOMIZED PARTICIPANT ALLOCATION
-- ============================================================

CALL assign_participants(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_code = 'EXP-001'
    ),
    ARRAY(
        SELECT participant_id
        FROM participants
        ORDER BY participant_id
        LIMIT 2000
    )
);


-- ============================================================
-- 25. SIMULATED OBSERVATION GENERATION
-- ============================================================

-- Deterministic sample outcomes make the SQL demonstration
-- reproducible. Production observations must come from actual
-- participant events and validated measurement pipelines.

INSERT INTO observations (
    assignment_id,
    metric_id,
    numeric_value,
    status
)
SELECT
    a.assignment_id,
    m.metric_id,
    CASE
        WHEN v.variant_kind = 'control'
             AND (a.participant_id % 10) = 0
        THEN 1

        WHEN v.variant_kind = 'treatment'
             AND (a.participant_id % 8) = 0
        THEN 1

        ELSE 0
    END,
    'valid'
FROM assignments a

JOIN experiment_variants v
    ON v.variant_id = a.variant_id

JOIN metric_definitions m
    ON m.metric_code = 'purchase_conversion'

WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_code = 'EXP-001'
);


-- Generate a checkout error observation for every assignment.
INSERT INTO observations (
    assignment_id,
    metric_id,
    numeric_value,
    status
)
SELECT
    a.assignment_id,
    m.metric_id,
    CASE
        WHEN v.variant_kind = 'control'
             AND a.participant_id % 50 = 0
        THEN 1

        WHEN v.variant_kind = 'treatment'
             AND a.participant_id % 48 = 0
        THEN 1

        ELSE 0
    END,
    'valid'
FROM assignments a

JOIN experiment_variants v
    ON v.variant_id = a.variant_id

JOIN metric_definitions m
    ON m.metric_code = 'checkout_error'

WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_code = 'EXP-001'
);


-- ============================================================
-- 26. GROUP METRIC REPORT
-- ============================================================

SELECT
    experiment_id,
    variant_name,
    variant_kind,
    metric_code,
    observation_count,
    mean_metric_value,
    total_metric_value
FROM experiment_group_metrics
WHERE experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_code = 'EXP-001'
)
ORDER BY metric_code, variant_kind;


-- ============================================================
-- 27. CONVERSION ANALYSIS
-- ============================================================

SELECT *
FROM analyze_conversion_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_code = 'EXP-001'
    ),
    'purchase_conversion',
    TRUE
);


-- ============================================================
-- 28. GUARDRAIL EVALUATION
-- ============================================================

WITH error_rates AS (
    SELECT
        v.variant_kind,
        AVG(o.numeric_value) AS error_rate
    FROM assignments a

    JOIN experiment_variants v
        ON v.variant_id = a.variant_id

    JOIN observations o
        ON o.assignment_id = a.assignment_id

    JOIN metric_definitions m
        ON m.metric_id = o.metric_id

    WHERE a.experiment_id = (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_code = 'EXP-001'
    )
      AND m.metric_code = 'checkout_error'
      AND o.status = 'valid'

    GROUP BY v.variant_kind
)
SELECT
    control.error_rate AS control_error_rate,
    treatment.error_rate AS treatment_error_rate,
    treatment.error_rate - control.error_rate AS error_increase,
    treatment.error_rate - control.error_rate <= 0.01
        AS guardrail_passed
FROM error_rates control
CROSS JOIN error_rates treatment
WHERE control.variant_kind = 'control'
  AND treatment.variant_kind = 'treatment';


-- ============================================================
-- 29. STORE ANALYSIS RESULTS
-- ============================================================

INSERT INTO analysis_results (
    experiment_id,
    analysis_version,
    control_sample_size,
    treatment_sample_size,
    control_metric_value,
    treatment_metric_value,
    absolute_effect,
    relative_effect,
    z_score,
    p_value,
    confidence_lower,
    confidence_upper,
    guardrail_passed,
    decision
)
SELECT
    e.experiment_id,
    1,
    result.control_n::INTEGER,
    result.treatment_n::INTEGER,
    result.control_rate,
    result.treatment_rate,
    result.absolute_effect,
    result.relative_effect,
    result.z_score,
    result.p_value,

    result.absolute_effect - 1.96 * sqrt(
        result.control_rate * (1 - result.control_rate)
        / result.control_n
        +
        result.treatment_rate * (1 - result.treatment_rate)
        / result.treatment_n
    ),

    result.absolute_effect + 1.96 * sqrt(
        result.control_rate * (1 - result.control_rate)
        / result.control_n
        +
        result.treatment_rate * (1 - result.treatment_rate)
        / result.treatment_n
    ),

    TRUE,
    result.decision

FROM experiments e

CROSS JOIN LATERAL analyze_conversion_experiment(
    e.experiment_id,
    'purchase_conversion',
    TRUE
) result

WHERE e.experiment_code = 'EXP-001';


-- ============================================================
-- 30. COMPLETE EXPERIMENT
-- ============================================================

UPDATE experiments
SET status = 'completed'
WHERE experiment_code = 'EXP-001'
  AND status = 'running';


-- ============================================================
-- 31. AUDIT LOG
-- ============================================================

INSERT INTO experiment_audit (
    experiment_id,
    event_type,
    event_description,
    event_data
)
SELECT
    experiment_id,
    'EXPERIMENT_COMPLETED',
    'Experiment execution and analysis completed.',
    jsonb_build_object(
        'experiment_code',
        experiment_code,
        'status',
        'completed'
    )
FROM experiments
WHERE experiment_code = 'EXP-001';


-- ============================================================
-- 32. MANAGEMENT REPORT
-- ============================================================

SELECT
    e.experiment_code,
    e.experiment_name,
    e.status,
    e.expected_direction,
    a.control_sample_size,
    a.treatment_sample_size,
    a.control_metric_value,
    a.treatment_metric_value,
    a.absolute_effect,
    a.relative_effect,
    a.p_value,
    a.guardrail_passed,
    a.decision,
    a.analyzed_at

FROM experiments e

LEFT JOIN LATERAL (
    SELECT *
    FROM analysis_results ar
    WHERE ar.experiment_id = e.experiment_id
    ORDER BY ar.analysis_version DESC
    LIMIT 1
) a ON TRUE

ORDER BY e.created_at DESC;


-- ============================================================
-- 33. DATA QUALITY VALIDATION
-- ============================================================

-- Detect participants assigned more than once to the same experiment.
SELECT
    experiment_id,
    participant_id,
    COUNT(*) AS assignment_count
FROM assignments
GROUP BY experiment_id, participant_id
HAVING COUNT(*) > 1;


-- Detect missing primary metric observations.
SELECT
    a.assignment_id,
    a.participant_id,
    a.experiment_id
FROM assignments a
WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_code = 'EXP-001'
)
AND NOT EXISTS (
    SELECT 1
    FROM observations o
    JOIN metric_definitions m
        ON m.metric_id = o.metric_id
    WHERE o.assignment_id = a.assignment_id
      AND m.metric_code = 'purchase_conversion'
      AND o.status = 'valid'
);


-- ============================================================
-- 34. ANALYTICAL CTE: EXPERIMENT COMPARISON
-- ============================================================

WITH latest_results AS (
    SELECT DISTINCT ON (experiment_id)
        experiment_id,
        absolute_effect,
        p_value,
        decision,
        analyzed_at
    FROM analysis_results
    ORDER BY experiment_id, analysis_version DESC
)
SELECT
    e.experiment_code,
    e.experiment_name,
    lr.absolute_effect,
    lr.p_value,
    lr.decision,
    lr.analyzed_at
FROM experiments e
LEFT JOIN latest_results lr
    ON lr.experiment_id = e.experiment_id
ORDER BY lr.p_value NULLS LAST;


-- ============================================================
-- 35. TRANSACTIONAL FAILURE DEMONSTRATION
-- ============================================================

-- This savepoint demonstrates rollback without damaging the
-- valid completed experiment.

SAVEPOINT before_invalid_experiment;

INSERT INTO experiments (
    experiment_code,
    experiment_name,
    research_question,
    null_hypothesis,
    alternative_hypothesis,
    primary_metric,
    expected_direction,
    baseline_rate,
    minimum_detectable_effect,
    owner_id
)
VALUES (
    'EXP-INVALID',
    'Invalid Experiment',
    'Test invalid configuration handling.',
    'No effect.',
    'Positive effect.',
    'purchase_conversion',
    'increase',
    0.10,
    0.02,
    1
);

-- An invalid variant allocation is rejected by the eligibility function.
INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    variant_kind,
    allocation_weight,
    intervention_description
)
SELECT
    experiment_id,
    'Invalid Control',
    'control',
    0.60,
    'Invalid allocation example.'
FROM experiments
WHERE experiment_code = 'EXP-INVALID';

INSERT INTO experiment_variants (
    experiment_id,
    variant_name,
    variant_kind,
    allocation_weight,
    intervention_description
)
SELECT
    experiment_id,
    'Invalid Treatment',
    'treatment',
    0.60,
    'Invalid allocation example.'
FROM experiments
WHERE experiment_code = 'EXP-INVALID';

SELECT experiment_is_ready(experiment_id)
FROM experiments
WHERE experiment_code = 'EXP-INVALID';

ROLLBACK TO SAVEPOINT before_invalid_experiment;


-- ============================================================
-- 36. PERFORMANCE AND OPERATIONAL INSPECTION
-- ============================================================

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'experimentation'
ORDER BY tablename, indexname;


-- Final consistency check.
SELECT
    experiment_code,
    status,
    actual_start,
    actual_end
FROM experiments
ORDER BY experiment_id;


COMMIT;
