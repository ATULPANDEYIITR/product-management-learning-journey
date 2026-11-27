-- ============================================================
-- A/B TESTING EXPERIMENT MANAGEMENT SYSTEM
-- PostgreSQL 15+
--
-- Domain:
--   Experiments
--   Randomization
--   Control and treatment groups
--   Participants
--   Exposure events
--   Conversion outcomes
--   Statistical significance
--   Approval and experiment governance
--   Experiment lifecycle
--   Reporting
--
-- Execute using psql or a PostgreSQL SQL client.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS ab_testing;

SET search_path TO ab_testing, public;

-- ------------------------------------------------------------
-- 1. ENUMERATED DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE experiment_status AS ENUM (
    'draft',
    'running',
    'completed',
    'stopped'
);

CREATE TYPE experiment_group AS ENUM (
    'control',
    'treatment'
);

CREATE TYPE experiment_decision AS ENUM (
    'inconclusive',
    'treatment_wins',
    'control_wins',
    'significant_without_practical_win',
    'insufficient_sample'
);

-- ------------------------------------------------------------
-- 2. EXPERIMENTS
-- ------------------------------------------------------------

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_key VARCHAR(100) NOT NULL UNIQUE,

    experiment_name VARCHAR(200) NOT NULL,

    hypothesis TEXT NOT NULL,

    primary_metric VARCHAR(100) NOT NULL,

    baseline_conversion_rate NUMERIC(8,6) NOT NULL,

    expected_treatment_rate NUMERIC(8,6) NOT NULL,

    allocation_ratio NUMERIC(5,4) NOT NULL DEFAULT 0.5000,

    significance_level NUMERIC(5,4) NOT NULL DEFAULT 0.0500,

    minimum_detectable_effect NUMERIC(8,6) NOT NULL DEFAULT 0.010000,

    statistical_power NUMERIC(5,4) NOT NULL DEFAULT 0.8000,

    minimum_group_size INTEGER NOT NULL DEFAULT 100,

    status experiment_status NOT NULL DEFAULT 'draft',

    randomization_seed BIGINT NOT NULL DEFAULT 42,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_experiment_name
        CHECK (LENGTH(TRIM(experiment_name)) > 0),

    CONSTRAINT valid_baseline_rate
        CHECK (
            baseline_conversion_rate > 0
            AND baseline_conversion_rate < 1
        ),

    CONSTRAINT valid_treatment_rate
        CHECK (
            expected_treatment_rate > 0
            AND expected_treatment_rate < 1
        ),

    CONSTRAINT valid_allocation
        CHECK (allocation_ratio > 0 AND allocation_ratio < 1),

    CONSTRAINT valid_alpha
        CHECK (significance_level > 0 AND significance_level < 1),

    CONSTRAINT valid_effect
        CHECK (minimum_detectable_effect >= 0),

    CONSTRAINT valid_power
        CHECK (statistical_power > 0 AND statistical_power < 1),

    CONSTRAINT valid_minimum_sample
        CHECK (minimum_group_size > 0)
);

-- ------------------------------------------------------------
-- 3. EXPERIMENT GROUPS
-- ------------------------------------------------------------

CREATE TABLE experiment_groups (
    group_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE RESTRICT,

    group_name experiment_group NOT NULL,

    allocation_weight NUMERIC(5,4) NOT NULL,

    CONSTRAINT unique_experiment_group
        UNIQUE (experiment_id, group_name),

    CONSTRAINT valid_group_weight
        CHECK (allocation_weight > 0 AND allocation_weight < 1)
);

-- ------------------------------------------------------------
-- 4. PARTICIPANTS
-- ------------------------------------------------------------

CREATE TABLE participants (
    participant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    participant_key VARCHAR(150) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_participant_key
        UNIQUE (participant_key),

    CONSTRAINT valid_participant_key
        CHECK (LENGTH(TRIM(participant_key)) > 0)
);

-- ------------------------------------------------------------
-- 5. EXPERIMENT ASSIGNMENTS
-- ------------------------------------------------------------

CREATE TABLE assignments (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE RESTRICT,

    participant_id BIGINT NOT NULL
        REFERENCES participants(participant_id)
        ON DELETE RESTRICT,

    group_id BIGINT NOT NULL
        REFERENCES experiment_groups(group_id)
        ON DELETE RESTRICT,

    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT one_assignment_per_experiment
        UNIQUE (experiment_id, participant_id),

    CONSTRAINT unique_assignment_record
        UNIQUE (assignment_id, experiment_id, group_id)
);

CREATE INDEX idx_assignments_experiment
    ON assignments(experiment_id);

CREATE INDEX idx_assignments_group
    ON assignments(group_id);

-- ------------------------------------------------------------
-- 6. EXPOSURE EVENTS
-- ------------------------------------------------------------

CREATE TABLE exposure_events (
    exposure_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assignment_id BIGINT NOT NULL
        REFERENCES assignments(assignment_id)
        ON DELETE RESTRICT,

    exposure_type VARCHAR(50) NOT NULL DEFAULT 'initial',

    exposed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_exposure_type
        CHECK (LENGTH(TRIM(exposure_type)) > 0),

    CONSTRAINT unique_assignment_exposure
        UNIQUE (assignment_id, exposure_type)
);

-- ------------------------------------------------------------
-- 7. CONVERSION OUTCOMES
-- ------------------------------------------------------------

CREATE TABLE conversion_outcomes (
    outcome_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assignment_id BIGINT NOT NULL UNIQUE
        REFERENCES assignments(assignment_id)
        ON DELETE RESTRICT,

    converted BOOLEAN NOT NULL,

    revenue NUMERIC(14,2) NOT NULL DEFAULT 0,

    conversion_time TIMESTAMPTZ,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_revenue
        CHECK (revenue >= 0),

    CONSTRAINT converted_requires_revenue
        CHECK (NOT converted OR revenue > 0)
);

CREATE INDEX idx_conversion_recorded
    ON conversion_outcomes(recorded_at);

-- ------------------------------------------------------------
-- 8. GUARDRAIL METRICS
-- ------------------------------------------------------------

CREATE TABLE guardrail_measurements (
    guardrail_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assignment_id BIGINT NOT NULL
        REFERENCES assignments(assignment_id)
        ON DELETE RESTRICT,

    metric_name VARCHAR(100) NOT NULL,

    metric_value NUMERIC(16,6) NOT NULL,

    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_guardrail_measurement
        UNIQUE (assignment_id, metric_name),

    CONSTRAINT valid_metric_name
        CHECK (LENGTH(TRIM(metric_name)) > 0)
);

CREATE INDEX idx_guardrail_metric
    ON guardrail_measurements(metric_name, measured_at);

-- ------------------------------------------------------------
-- 9. EXPERIMENT EVALUATIONS
-- ------------------------------------------------------------

CREATE TABLE experiment_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE RESTRICT,

    control_sample_size INTEGER NOT NULL,

    treatment_sample_size INTEGER NOT NULL,

    control_conversions INTEGER NOT NULL,

    treatment_conversions INTEGER NOT NULL,

    control_rate NUMERIC(12,8) NOT NULL,

    treatment_rate NUMERIC(12,8) NOT NULL,

    absolute_lift NUMERIC(12,8) NOT NULL,

    relative_lift NUMERIC(12,8),

    z_score NUMERIC(14,8) NOT NULL,

    p_value NUMERIC(12,10) NOT NULL,

    confidence_low NUMERIC(12,8) NOT NULL,

    confidence_high NUMERIC(12,8) NOT NULL,

    statistically_significant BOOLEAN NOT NULL,

    practically_significant BOOLEAN NOT NULL,

    decision experiment_decision NOT NULL,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_evaluation_counts
        CHECK (
            control_sample_size > 0
            AND treatment_sample_size > 0
            AND control_conversions BETWEEN 0 AND control_sample_size
            AND treatment_conversions BETWEEN 0 AND treatment_sample_size
        ),

    CONSTRAINT valid_p_value
        CHECK (p_value BETWEEN 0 AND 1)
);

CREATE INDEX idx_evaluations_experiment
    ON experiment_evaluations(experiment_id, evaluated_at DESC);

-- ------------------------------------------------------------
-- 10. GROUP MEMBERSHIP INTEGRITY
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_assignment_group()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    expected_experiment_id BIGINT;
BEGIN
    SELECT experiment_id
    INTO expected_experiment_id
    FROM experiment_groups
    WHERE group_id = NEW.group_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment group does not exist.';
    END IF;

    IF expected_experiment_id <> NEW.experiment_id THEN
        RAISE EXCEPTION
            'Assignment group must belong to the assigned experiment.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_assignment_group
BEFORE INSERT OR UPDATE ON assignments
FOR EACH ROW
EXECUTE FUNCTION validate_assignment_group();

-- ------------------------------------------------------------
-- 11. EXPERIMENT LIFECYCLE ENFORCEMENT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION enforce_experiment_lifecycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = 'draft' AND NEW.status = 'running' THEN
        NEW.started_at = COALESCE(NEW.started_at, NOW());

    ELSIF OLD.status = 'running'
          AND NEW.status IN ('completed', 'stopped') THEN
        NEW.completed_at = COALESCE(NEW.completed_at, NOW());

    ELSIF NEW.status <> OLD.status THEN
        RAISE EXCEPTION
            'Invalid experiment transition: % -> %',
            OLD.status,
            NEW.status;
    END IF;

    IF OLD.status IN ('completed', 'stopped')
       AND (
           NEW.status <> OLD.status
           OR NEW.experiment_name <> OLD.experiment_name
           OR NEW.baseline_conversion_rate <> OLD.baseline_conversion_rate
           OR NEW.expected_treatment_rate <> OLD.expected_treatment_rate
       ) THEN
        RAISE EXCEPTION
            'Finalized experiments cannot be reopened or reconfigured.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_lifecycle
BEFORE UPDATE ON experiments
FOR EACH ROW
EXECUTE FUNCTION enforce_experiment_lifecycle();

-- ------------------------------------------------------------
-- 12. OUTCOME VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_outcome_assignment()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    assignment_time TIMESTAMPTZ;
    experiment_state experiment_status;
BEGIN
    SELECT
        a.assigned_at,
        e.status
    INTO
        assignment_time,
        experiment_state
    FROM assignments a
    JOIN experiments e
      ON e.experiment_id = a.experiment_id
    WHERE a.assignment_id = NEW.assignment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Assignment does not exist.';
    END IF;

    IF experiment_state <> 'running' THEN
        RAISE EXCEPTION
            'Outcomes can only be recorded for running experiments.';
    END IF;

    IF NEW.conversion_time IS NOT NULL
       AND NEW.conversion_time < assignment_time THEN
        RAISE EXCEPTION
            'Conversion cannot precede participant assignment.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_outcome
BEFORE INSERT OR UPDATE ON conversion_outcomes
FOR EACH ROW
EXECUTE FUNCTION validate_outcome_assignment();

-- ------------------------------------------------------------
-- 13. EXPERIMENT CREATION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE create_experiment(
    p_key VARCHAR(100),
    p_name VARCHAR(200),
    p_hypothesis TEXT,
    p_baseline NUMERIC,
    p_treatment NUMERIC,
    p_seed BIGINT DEFAULT 42
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_experiment_id BIGINT;
BEGIN
    INSERT INTO experiments (
        experiment_key,
        experiment_name,
        hypothesis,
        primary_metric,
        baseline_conversion_rate,
        expected_treatment_rate,
        randomization_seed
    )
    VALUES (
        p_key,
        p_name,
        p_hypothesis,
        'conversion_rate',
        p_baseline,
        p_treatment,
        p_seed
    )
    RETURNING experiment_id INTO new_experiment_id;

    INSERT INTO experiment_groups (
        experiment_id,
        group_name,
        allocation_weight
    )
    VALUES
        (new_experiment_id, 'control', 0.50),
        (new_experiment_id, 'treatment', 0.50);
END;
$$;

-- ------------------------------------------------------------
-- 14. RANDOM ASSIGNMENT FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION assign_participant(
    p_experiment_id BIGINT,
    p_participant_key VARCHAR(150)
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    current_status experiment_status;
    selected_group_id BIGINT;
    allocation NUMERIC;
    generated_random NUMERIC;
    new_participant_id BIGINT;
    new_assignment_id BIGINT;
BEGIN
    SELECT status, allocation_ratio
    INTO current_status, allocation
    FROM experiments
    WHERE experiment_id = p_experiment_id
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment does not exist.';
    END IF;

    IF current_status <> 'running' THEN
        RAISE EXCEPTION 'Experiment is not running.';
    END IF;

    IF p_participant_key IS NULL
       OR LENGTH(TRIM(p_participant_key)) = 0 THEN
        RAISE EXCEPTION 'Participant key is required.';
    END IF;

    INSERT INTO participants(participant_key)
    VALUES (p_participant_key)
    ON CONFLICT (participant_key)
    DO UPDATE SET participant_key = EXCLUDED.participant_key
    RETURNING participant_id INTO new_participant_id;

    -- The database random generator is used for independent assignment.
    -- A production service requiring reproducible assignment should use
    -- a keyed deterministic hash of experiment and participant identifiers.
    generated_random := random();

    IF generated_random < allocation THEN
        SELECT group_id
        INTO selected_group_id
        FROM experiment_groups
        WHERE experiment_id = p_experiment_id
          AND group_name = 'control';
    ELSE
        SELECT group_id
        INTO selected_group_id
        FROM experiment_groups
        WHERE experiment_id = p_experiment_id
          AND group_name = 'treatment';
    END IF;

    INSERT INTO assignments (
        experiment_id,
        participant_id,
        group_id
    )
    VALUES (
        p_experiment_id,
        new_participant_id,
        selected_group_id
    )
    RETURNING assignment_id INTO new_assignment_id;

    RETURN new_assignment_id;
END;
$$;

-- ------------------------------------------------------------
-- 15. EXPERIMENT REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW experiment_group_summary AS
SELECT
    e.experiment_id,
    e.experiment_key,
    e.experiment_name,
    e.status,
    eg.group_name,

    COUNT(DISTINCT a.assignment_id) AS assigned_participants,

    COUNT(DISTINCT o.outcome_id) AS observed_participants,

    COUNT(o.outcome_id) FILTER (
        WHERE o.converted
    ) AS conversions,

    ROUND(
        COUNT(o.outcome_id) FILTER (WHERE o.converted)::NUMERIC
        / NULLIF(COUNT(o.outcome_id), 0),
        6
    ) AS conversion_rate,

    ROUND(
        COALESCE(AVG(o.revenue), 0),
        2
    ) AS average_revenue

FROM experiments e

JOIN experiment_groups eg
    ON eg.experiment_id = e.experiment_id

LEFT JOIN assignments a
    ON a.group_id = eg.group_id

LEFT JOIN conversion_outcomes o
    ON o.assignment_id = a.assignment_id

GROUP BY
    e.experiment_id,
    e.experiment_key,
    e.experiment_name,
    e.status,
    eg.group_name;

-- ------------------------------------------------------------
-- 16. STATISTICAL EVALUATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_experiment(
    p_experiment_id BIGINT
)
RETURNS experiment_evaluations
LANGUAGE plpgsql
AS $$
DECLARE
    exp experiments%ROWTYPE;

    c_total INTEGER;
    t_total INTEGER;

    c_conversions INTEGER;
    t_conversions INTEGER;

    p1 NUMERIC;
    p2 NUMERIC;
    pooled NUMERIC;

    difference NUMERIC;
    pooled_se NUMERIC;
    unpooled_se NUMERIC;

    z NUMERIC;
    p_val NUMERIC;

    ci_low NUMERIC;
    ci_high NUMERIC;

    critical NUMERIC := 1.959963984540054;

    is_significant BOOLEAN;
    is_practical BOOLEAN;

    final_decision experiment_decision;

    result experiment_evaluations%ROWTYPE;
BEGIN
    SELECT *
    INTO exp
    FROM experiments
    WHERE experiment_id = p_experiment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment not found.';
    END IF;

    IF exp.status NOT IN ('running', 'completed', 'stopped') THEN
        RAISE EXCEPTION 'Experiment has not started.';
    END IF;

    SELECT
        COUNT(*) FILTER (WHERE eg.group_name = 'control'),
        COUNT(*) FILTER (WHERE eg.group_name = 'treatment'),

        COUNT(*) FILTER (
            WHERE eg.group_name = 'control' AND o.converted
        ),

        COUNT(*) FILTER (
            WHERE eg.group_name = 'treatment' AND o.converted
        )

    INTO c_total, t_total, c_conversions, t_conversions

    FROM assignments a

    JOIN experiment_groups eg
        ON eg.group_id = a.group_id

    JOIN conversion_outcomes o
        ON o.assignment_id = a.assignment_id

    WHERE a.experiment_id = p_experiment_id;

    IF c_total = 0 OR t_total = 0 THEN
        RAISE EXCEPTION
            'Both groups require recorded outcomes.';
    END IF;

    p1 := c_conversions::NUMERIC / c_total;
    p2 := t_conversions::NUMERIC / t_total;

    difference := p2 - p1;

    pooled :=
        (c_conversions + t_conversions)::NUMERIC
        / (c_total + t_total);

    pooled_se := SQRT(
        pooled * (1 - pooled)
        * (1.0 / c_total + 1.0 / t_total)
    );

    IF pooled_se = 0 THEN
        z := 0;
        p_val := 1;
    ELSE
        z := difference / pooled_se;

        -- Two-sided standard normal probability using PostgreSQL erf.
        p_val := 2 * (
            1 - (
                0.5 * (
                    1 + erf(ABS(z) / SQRT(2.0))
                )
            )
        );
    END IF;

    p_val := GREATEST(0, LEAST(1, p_val));

    unpooled_se := SQRT(
        p1 * (1 - p1) / c_total
        + p2 * (1 - p2) / t_total
    );

    ci_low := difference - critical * unpooled_se;
    ci_high := difference + critical * unpooled_se;

    is_significant := p_val < exp.significance_level;

    is_practical :=
        difference >= exp.minimum_detectable_effect;

    IF
        c_total < exp.minimum_group_size
        OR t_total < exp.minimum_group_size
    THEN
        final_decision := 'insufficient_sample';

    ELSIF NOT is_significant THEN
        final_decision := 'inconclusive';

    ELSIF difference > 0 AND is_practical THEN
        final_decision := 'treatment_wins';

    ELSIF difference < 0 THEN
        final_decision := 'control_wins';

    ELSE
        final_decision := 'significant_without_practical_win';
    END IF;

    INSERT INTO experiment_evaluations (
        experiment_id,
        control_sample_size,
        treatment_sample_size,
        control_conversions,
        treatment_conversions,
        control_rate,
        treatment_rate,
        absolute_lift,
        relative_lift,
        z_score,
        p_value,
        confidence_low,
        confidence_high,
        statistically_significant,
        practically_significant,
        decision
    )
    VALUES (
        p_experiment_id,
        c_total,
        t_total,
        c_conversions,
        t_conversions,
        p1,
        p2,
        difference,
        CASE
            WHEN p1 = 0 THEN NULL
            ELSE difference / p1
        END,
        z,
        p_val,
        ci_low,
        ci_high,
        is_significant,
        is_practical,
        final_decision
    )
    RETURNING * INTO result;

    RETURN result;
END;
$$;

-- ------------------------------------------------------------
-- 17. SAMPLE DATA
-- ------------------------------------------------------------

CALL create_experiment(
    'checkout-v1',
    'Checkout Button Optimization',
    'A simplified checkout button increases conversion rate.',
    0.10,
    0.12,
    2026
);

CALL create_experiment(
    'pricing-v1',
    'Pricing Page Experiment',
    'A revised pricing page changes purchase conversion.',
    0.08,
    0.09,
    2027
);

-- ------------------------------------------------------------
-- 18. EXPERIMENT LIFECYCLE
-- ------------------------------------------------------------

UPDATE experiments
SET status = 'running'
WHERE experiment_key IN ('checkout-v1', 'pricing-v1');

-- ------------------------------------------------------------
-- 19. PARTICIPANT ASSIGNMENT
-- ------------------------------------------------------------

DO $$
DECLARE
    checkout_id BIGINT;
    pricing_id BIGINT;
    assignment_id BIGINT;
    i INTEGER;
BEGIN
    SELECT experiment_id
    INTO checkout_id
    FROM experiments
    WHERE experiment_key = 'checkout-v1';

    SELECT experiment_id
    INTO pricing_id
    FROM experiments
    WHERE experiment_key = 'pricing-v1';

    FOR i IN 1..1000 LOOP

        assignment_id := assign_participant(
            checkout_id,
            'checkout-user-' || i
        );

        INSERT INTO exposure_events(assignment_id)
        VALUES (assignment_id);

        assignment_id := assign_participant(
            pricing_id,
            'pricing-user-' || i
        );

        INSERT INTO exposure_events(assignment_id)
        VALUES (assignment_id);

    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 20. SIMULATED CONVERSION DATA
-- ------------------------------------------------------------

-- Fixed pseudorandom seeds make this demonstration reproducible
-- within the PostgreSQL session.

SELECT setseed(0.42);

INSERT INTO conversion_outcomes (
    assignment_id,
    converted,
    revenue,
    conversion_time
)
SELECT
    a.assignment_id,

    CASE
        WHEN eg.group_name = 'control'
            THEN random() < 0.10
        ELSE random() < 0.12
    END,

    CASE
        WHEN
            CASE
                WHEN eg.group_name = 'control'
                    THEN random() < 0.10
                ELSE random() < 0.12
            END
        THEN 150.00
        ELSE 0.00
    END,

    CASE
        WHEN random() < 0.10
            THEN a.assigned_at + INTERVAL '1 hour'
        ELSE NULL
    END

FROM assignments a

JOIN experiment_groups eg
    ON eg.group_id = a.group_id

WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_key = 'checkout-v1'
);

-- The following statement inserts valid pricing outcomes.
INSERT INTO conversion_outcomes (
    assignment_id,
    converted,
    revenue
)
SELECT
    a.assignment_id,
    CASE
        WHEN eg.group_name = 'control'
            THEN random() < 0.08
        ELSE random() < 0.09
    END,
    150.00
FROM assignments a
JOIN experiment_groups eg
    ON eg.group_id = a.group_id
WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_key = 'pricing-v1'
);

-- ------------------------------------------------------------
-- 21. GUARDRAIL DATA
-- ------------------------------------------------------------

INSERT INTO guardrail_measurements (
    assignment_id,
    metric_name,
    metric_value
)
SELECT
    a.assignment_id,
    'page_latency_ms',
    150 + random() * 100
FROM assignments a
WHERE a.experiment_id = (
    SELECT experiment_id
    FROM experiments
    WHERE experiment_key = 'checkout-v1'
);

-- ------------------------------------------------------------
-- 22. STATISTICAL EVALUATION
-- ------------------------------------------------------------

SELECT evaluate_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_key = 'checkout-v1'
    )
);

SELECT evaluate_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_key = 'pricing-v1'
    )
);

-- ------------------------------------------------------------
-- 23. RETRIEVAL: EXPERIMENT GROUP COMPARISON
-- ------------------------------------------------------------

SELECT
    experiment_name,
    group_name,
    assigned_participants,
    observed_participants,
    conversions,
    conversion_rate,
    average_revenue
FROM experiment_group_summary
ORDER BY experiment_name, group_name;

-- ------------------------------------------------------------
-- 24. AGGREGATION: OVERALL CONVERSION
-- ------------------------------------------------------------

SELECT
    e.experiment_key,
    eg.group_name,
    COUNT(o.outcome_id) AS observations,
    SUM(o.converted::INTEGER) AS conversions,

    ROUND(
        AVG(o.converted::INTEGER)::NUMERIC,
        4
    ) AS conversion_rate,

    ROUND(
        AVG(o.revenue),
        2
    ) AS average_revenue

FROM experiments e

JOIN experiment_groups eg
    ON eg.experiment_id = e.experiment_id

JOIN assignments a
    ON a.group_id = eg.group_id

JOIN conversion_outcomes o
    ON o.assignment_id = a.assignment_id

GROUP BY e.experiment_key, eg.group_name
ORDER BY e.experiment_key, eg.group_name;

-- ------------------------------------------------------------
-- 25. EVALUATION HISTORY
-- ------------------------------------------------------------

SELECT
    e.experiment_name,
    v.control_sample_size,
    v.treatment_sample_size,
    v.control_rate,
    v.treatment_rate,
    v.absolute_lift,
    v.relative_lift,
    v.z_score,
    v.p_value,
    v.confidence_low,
    v.confidence_high,
    v.statistically_significant,
    v.practically_significant,
    v.decision,
    v.evaluated_at
FROM experiment_evaluations v
JOIN experiments e
    ON e.experiment_id = v.experiment_id
ORDER BY v.evaluated_at DESC;

-- ------------------------------------------------------------
-- 26. GUARDRAIL EVALUATION
-- ------------------------------------------------------------

SELECT
    e.experiment_key,
    eg.group_name,
    gm.metric_name,

    ROUND(AVG(gm.metric_value), 2)
        AS average_metric,

    ROUND(
        PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY gm.metric_value)::NUMERIC,
        2
    ) AS percentile_95

FROM guardrail_measurements gm

JOIN assignments a
    ON a.assignment_id = gm.assignment_id

JOIN experiment_groups eg
    ON eg.group_id = a.group_id

JOIN experiments e
    ON e.experiment_id = a.experiment_id

GROUP BY
    e.experiment_key,
    eg.group_name,
    gm.metric_name;

-- ------------------------------------------------------------
-- 27. VALIDATION: ASSIGNMENT DISTRIBUTION
-- ------------------------------------------------------------

SELECT
    e.experiment_key,
    eg.group_name,
    COUNT(a.assignment_id) AS participant_count,
    eg.allocation_weight AS expected_allocation,

    ROUND(
        COUNT(a.assignment_id)::NUMERIC
        / NULLIF(
            SUM(COUNT(a.assignment_id)) OVER (
                PARTITION BY e.experiment_id
            ),
            0
        ),
        4
    ) AS actual_allocation

FROM experiments e

JOIN experiment_groups eg
    ON eg.experiment_id = e.experiment_id

LEFT JOIN assignments a
    ON a.group_id = eg.group_id

GROUP BY
    e.experiment_id,
    e.experiment_key,
    eg.group_name,
    eg.allocation_weight

ORDER BY e.experiment_key, eg.group_name;

-- ------------------------------------------------------------
-- 28. VALIDATION: DUPLICATE PARTICIPANT ASSIGNMENTS
-- ------------------------------------------------------------

SELECT
    experiment_id,
    participant_id,
    COUNT(*) AS assignment_count
FROM assignments
GROUP BY experiment_id, participant_id
HAVING COUNT(*) > 1;

-- The unique constraint should make this query return zero rows.

-- ------------------------------------------------------------
-- 29. VALIDATION: MISSING OUTCOMES
-- ------------------------------------------------------------

SELECT
    e.experiment_key,
    COUNT(*) AS assignments_without_outcomes
FROM assignments a
JOIN experiments e
    ON e.experiment_id = a.experiment_id
LEFT JOIN conversion_outcomes o
    ON o.assignment_id = a.assignment_id
WHERE o.outcome_id IS NULL
GROUP BY e.experiment_key;

-- ------------------------------------------------------------
-- 30. ELIGIBILITY REPORT
-- ------------------------------------------------------------

SELECT
    e.experiment_key,
    e.status,

    COALESCE(
        latest.decision,
        'insufficient_sample'
    ) AS latest_decision,

    CASE
        WHEN e.status <> 'running'
            THEN 'NOT_RUNNING'

        WHEN latest.evaluation_id IS NULL
            THEN 'NOT_EVALUATED'

        WHEN latest.decision = 'insufficient_sample'
            THEN 'INSUFFICIENT_SAMPLE'

        WHEN latest.decision = 'inconclusive'
            THEN 'NO_STATISTICAL_EVIDENCE'

        WHEN latest.decision = 'treatment_wins'
            THEN 'TREATMENT_CANDIDATE'

        WHEN latest.decision = 'control_wins'
            THEN 'RETAIN_CONTROL'

        ELSE 'REQUIRES_PRACTICAL_REVIEW'
    END AS operational_eligibility

FROM experiments e

LEFT JOIN LATERAL (
    SELECT *
    FROM experiment_evaluations v
    WHERE v.experiment_id = e.experiment_id
    ORDER BY v.evaluated_at DESC
    LIMIT 1
) latest ON TRUE;

-- ------------------------------------------------------------
-- 31. FAILURE CASE DEMONSTRATION
-- ------------------------------------------------------------

DO $$
DECLARE
    experiment_id_value BIGINT;
BEGIN
    SELECT experiment_id
    INTO experiment_id_value
    FROM experiments
    WHERE experiment_key = 'checkout-v1';

    -- The database rejects duplicate assignment.
    BEGIN
        PERFORM assign_participant(
            experiment_id_value,
            'checkout-user-1'
        );

        RAISE EXCEPTION
            'Expected duplicate assignment rejection did not occur.';

    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'Expected failure handled: duplicate assignment.';
    END;

END;
$$;

-- ------------------------------------------------------------
-- 32. COMPLETE EXPERIMENTS
-- ------------------------------------------------------------

UPDATE experiments
SET status = 'completed'
WHERE status = 'running';

-- ------------------------------------------------------------
-- 33. FINAL STATE
-- ------------------------------------------------------------

SELECT
    experiment_key,
    experiment_name,
    status,
    started_at,
    completed_at
FROM experiments
ORDER BY experiment_id;

COMMIT;
