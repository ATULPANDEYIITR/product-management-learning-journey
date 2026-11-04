-- ============================================================
-- PRODUCT GOALS MANAGEMENT SYSTEM
-- PostgreSQL 15+
--
-- Models:
-- 1. Strategic goals and organizational alignment
-- 2. Outcome goals
-- 3. Objectives and Key Results (OKRs)
-- 4. Key Performance Indicators (KPIs)
-- 5. Metric observations and data quality
-- 6. Weighted progress evaluation
-- 7. Guardrail monitoring
-- 8. Goal ownership and accountability
-- 9. Audit history
-- 10. Portfolio reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_management;

SET search_path TO product_management, public;

-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

CREATE TYPE goal_type AS ENUM (
    'strategic',
    'outcome',
    'okr',
    'kpi'
);

CREATE TYPE goal_status AS ENUM (
    'draft',
    'active',
    'at_risk',
    'achieved',
    'missed',
    'cancelled'
);

CREATE TYPE metric_direction AS ENUM (
    'increase',
    'decrease'
);

CREATE TYPE metric_category AS ENUM (
    'leading',
    'lagging',
    'guardrail'
);

CREATE TYPE aggregation_method AS ENUM (
    'latest',
    'average',
    'sum'
);

-- ------------------------------------------------------------
-- ORGANIZATIONAL STRUCTURE
-- ------------------------------------------------------------

CREATE TABLE teams (
    team_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE employees (
    employee_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id),
    employee_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- GOALS
-- ------------------------------------------------------------

CREATE TABLE goals (
    goal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    goal_code VARCHAR(40) NOT NULL UNIQUE,
    title VARCHAR(250) NOT NULL,
    description TEXT NOT NULL,
    type goal_type NOT NULL,
    status goal_status NOT NULL DEFAULT 'draft',

    owner_id BIGINT NOT NULL REFERENCES employees(employee_id),

    parent_goal_id BIGINT REFERENCES goals(goal_id),

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (end_date > start_date),
    CHECK (parent_goal_id IS NULL OR parent_goal_id <> goal_id)
);

CREATE INDEX idx_goals_owner_status
ON goals(owner_id, status);

CREATE INDEX idx_goals_parent
ON goals(parent_goal_id);

CREATE INDEX idx_goals_period
ON goals(start_date, end_date);

-- ------------------------------------------------------------
-- METRIC DEFINITIONS
-- ------------------------------------------------------------

CREATE TABLE metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_code VARCHAR(50) NOT NULL UNIQUE,
    metric_name VARCHAR(200) NOT NULL,
    description TEXT,

    category metric_category NOT NULL,
    direction metric_direction NOT NULL,

    unit VARCHAR(40) NOT NULL,

    baseline NUMERIC(18, 4) NOT NULL,
    target NUMERIC(18, 4) NOT NULL,

    weight NUMERIC(10, 4) NOT NULL DEFAULT 1,

    aggregation aggregation_method NOT NULL DEFAULT 'latest',

    lower_guardrail NUMERIC(18, 4),
    upper_guardrail NUMERIC(18, 4),

    freshness_hours INTEGER NOT NULL DEFAULT 168,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (baseline <> target),
    CHECK (weight > 0),
    CHECK (freshness_hours > 0),

    CHECK (
        (direction = 'increase' AND target > baseline)
        OR
        (direction = 'decrease' AND target < baseline)
    ),

    CHECK (
        lower_guardrail IS NULL
        OR upper_guardrail IS NULL
        OR lower_guardrail <= upper_guardrail
    )
);

CREATE INDEX idx_metrics_category
ON metrics(category);

-- ------------------------------------------------------------
-- KEY RESULTS
-- ------------------------------------------------------------

CREATE TABLE key_results (
    key_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    goal_id BIGINT NOT NULL REFERENCES goals(goal_id)
        ON DELETE CASCADE,

    metric_id BIGINT NOT NULL REFERENCES metrics(metric_id),

    weight NUMERIC(10, 4) NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(goal_id, metric_id),

    CHECK (weight > 0)
);

CREATE INDEX idx_key_results_goal
ON key_results(goal_id);

CREATE INDEX idx_key_results_metric
ON key_results(metric_id);

-- ------------------------------------------------------------
-- METRIC OBSERVATIONS
-- ------------------------------------------------------------

CREATE TABLE metric_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    metric_id BIGINT NOT NULL REFERENCES metrics(metric_id),

    observed_value NUMERIC(18, 4) NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL,

    source VARCHAR(200) NOT NULL,

    confidence NUMERIC(5, 4) NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (confidence BETWEEN 0 AND 1),

    UNIQUE(metric_id, observed_at)
);

CREATE INDEX idx_observations_metric_time
ON metric_observations(metric_id, observed_at DESC);

-- ------------------------------------------------------------
-- AUDIT HISTORY
-- ------------------------------------------------------------

CREATE TABLE goal_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    goal_id BIGINT NOT NULL REFERENCES goals(goal_id),

    event_type VARCHAR(80) NOT NULL,

    previous_status goal_status,
    new_status goal_status,

    actor_id BIGINT REFERENCES employees(employee_id),

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_goal_audit_history
ON goal_audit(goal_id, created_at DESC);

-- ------------------------------------------------------------
-- AUTOMATIC UPDATED TIMESTAMP
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_goal_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_goal_updated_at
BEFORE UPDATE ON goals
FOR EACH ROW
EXECUTE FUNCTION update_goal_timestamp();

-- ------------------------------------------------------------
-- PREVENT CIRCULAR GOAL HIERARCHIES
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_goal_hierarchy()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.parent_goal_id IS NULL THEN
        RETURN NEW;
    END IF;

    IF NEW.parent_goal_id = NEW.goal_id THEN
        RAISE EXCEPTION 'A goal cannot be its own parent.';
    END IF;

    IF EXISTS (
        WITH RECURSIVE ancestors AS (
            SELECT goal_id, parent_goal_id
            FROM goals
            WHERE goal_id = NEW.parent_goal_id

            UNION ALL

            SELECT g.goal_id, g.parent_goal_id
            FROM goals g
            JOIN ancestors a
                ON g.goal_id = a.parent_goal_id
        )
        SELECT 1
        FROM ancestors
        WHERE goal_id = NEW.goal_id
    ) THEN
        RAISE EXCEPTION 'Circular goal hierarchy detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_goal_hierarchy
BEFORE INSERT OR UPDATE OF parent_goal_id ON goals
FOR EACH ROW
EXECUTE FUNCTION validate_goal_hierarchy();

-- ------------------------------------------------------------
-- VALIDATE KEY RESULT MODIFICATIONS
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_key_result()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_status goal_status;
BEGIN
    SELECT status
    INTO current_status
    FROM goals
    WHERE goal_id = NEW.goal_id
    FOR UPDATE;

    IF current_status IS DISTINCT FROM 'draft'::goal_status THEN
        RAISE EXCEPTION
            'Key Results can only be changed for draft goals.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_key_result_validation
BEFORE INSERT OR UPDATE ON key_results
FOR EACH ROW
EXECUTE FUNCTION validate_key_result();

-- ------------------------------------------------------------
-- VALIDATE MEASUREMENT TIMESTAMPS
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_metric_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    latest_time TIMESTAMPTZ;
BEGIN
    SELECT MAX(observed_at)
    INTO latest_time
    FROM metric_observations
    WHERE metric_id = NEW.metric_id;

    IF latest_time IS NOT NULL
       AND NEW.observed_at <= latest_time THEN
        RAISE EXCEPTION
            'New observations must be later than existing observations.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_observation_chronology
BEFORE INSERT ON metric_observations
FOR EACH ROW
EXECUTE FUNCTION validate_metric_observation();

-- ------------------------------------------------------------
-- CURRENT METRIC VALUES
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW current_metric_values AS
SELECT
    m.metric_id,
    m.metric_code,
    m.metric_name,
    m.category,
    m.unit,
    m.baseline,
    m.target,
    m.direction,
    m.weight,
    m.aggregation,

    CASE m.aggregation
        WHEN 'latest' THEN
            COALESCE(latest.value, m.baseline)

        WHEN 'average' THEN
            COALESCE(average_value.value, m.baseline)

        WHEN 'sum' THEN
            COALESCE(sum_value.value, m.baseline)
    END AS current_value,

    latest.observed_at AS last_observed_at,
    latest.confidence

FROM metrics m

LEFT JOIN LATERAL (
    SELECT
        observed_value AS value,
        observed_at,
        confidence
    FROM metric_observations mo
    WHERE mo.metric_id = m.metric_id
    ORDER BY observed_at DESC
    LIMIT 1
) latest ON TRUE

LEFT JOIN LATERAL (
    SELECT AVG(observed_value) AS value
    FROM metric_observations mo
    WHERE mo.metric_id = m.metric_id
) average_value ON TRUE

LEFT JOIN LATERAL (
    SELECT SUM(observed_value) AS value
    FROM metric_observations mo
    WHERE mo.metric_id = m.metric_id
) sum_value ON TRUE;

-- ------------------------------------------------------------
-- METRIC PROGRESS
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW metric_performance AS
SELECT
    cmv.*,

    ROUND(
        GREATEST(
            0,
            LEAST(
                100,
                (
                    (current_value - baseline)
                    /
                    NULLIF(target - baseline, 0)
                ) * 100
            )
        ),
        2
    ) AS progress_percent,

    target - current_value AS remaining_value,

    CASE
        WHEN last_observed_at IS NULL THEN FALSE
        WHEN last_observed_at <
             NOW() - MAKE_INTERVAL(hours => (
                 SELECT freshness_hours
                 FROM metrics
                 WHERE metric_id = cmv.metric_id
             ))
        THEN FALSE
        ELSE TRUE
    END AS is_fresh

FROM current_metric_values cmv;

-- ------------------------------------------------------------
-- KEY RESULT REPORTING
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW key_result_performance AS
SELECT
    kr.key_result_id,
    kr.goal_id,
    g.goal_code,
    g.title AS objective_title,

    mp.metric_id,
    mp.metric_code,
    mp.metric_name,
    mp.category,
    mp.unit,

    mp.baseline,
    mp.current_value,
    mp.target,

    kr.weight,

    mp.progress_percent,
    mp.remaining_value,
    mp.confidence,
    mp.is_fresh,

    (
        (mp.current_value >= COALESCE(m.lower_guardrail, '-Infinity'))
        AND
        (mp.current_value <= COALESCE(m.upper_guardrail, 'Infinity'))
    ) AS within_guardrails

FROM key_results kr

JOIN goals g
    ON g.goal_id = kr.goal_id

JOIN metric_performance mp
    ON mp.metric_id = kr.metric_id

JOIN metrics m
    ON m.metric_id = kr.metric_id;

-- ------------------------------------------------------------
-- OBJECTIVE PROGRESS
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW objective_performance AS
SELECT
    g.goal_id,
    g.goal_code,
    g.title,
    g.type,
    g.status,
    g.owner_id,
    g.parent_goal_id,
    g.start_date,
    g.end_date,

    COUNT(kr.key_result_id) AS key_result_count,

    COALESCE(
        ROUND(
            SUM(krp.progress_percent * kr.weight)
            / NULLIF(SUM(kr.weight), 0),
            2
        ),
        0
    ) AS weighted_progress,

    COALESCE(
        BOOL_AND(krp.within_guardrails),
        TRUE
    ) AS all_guardrails_pass,

    COALESCE(
        BOOL_AND(krp.is_fresh),
        FALSE
    ) AS all_metrics_fresh

FROM goals g

LEFT JOIN key_results kr
    ON kr.goal_id = g.goal_id

LEFT JOIN key_result_performance krp
    ON krp.key_result_id = kr.key_result_id

GROUP BY g.goal_id;

-- ------------------------------------------------------------
-- GOAL EVALUATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_goal(
    p_goal_id BIGINT
)
RETURNS goal_status
LANGUAGE plpgsql
AS $$
DECLARE
    current_goal goals%ROWTYPE;
    progress NUMERIC;
    guardrails_pass BOOLEAN;
    new_status goal_status;
BEGIN
    SELECT *
    INTO current_goal
    FROM goals
    WHERE goal_id = p_goal_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Goal % does not exist.', p_goal_id;
    END IF;

    IF current_goal.status IN ('draft', 'cancelled') THEN
        RETURN current_goal.status;
    END IF;

    SELECT
        weighted_progress,
        all_guardrails_pass
    INTO
        progress,
        guardrails_pass
    FROM objective_performance
    WHERE goal_id = p_goal_id;

    IF progress >= 100 AND guardrails_pass THEN
        new_status := 'achieved';

    ELSIF NOT guardrails_pass THEN
        new_status := 'at_risk';

    ELSIF CURRENT_DATE > current_goal.end_date THEN
        new_status := 'missed';

    ELSIF progress < 40 THEN
        new_status := 'at_risk';

    ELSE
        new_status := 'active';
    END IF;

    IF new_status IS DISTINCT FROM current_goal.status THEN

        UPDATE goals
        SET status = new_status
        WHERE goal_id = p_goal_id;

        INSERT INTO goal_audit (
            goal_id,
            event_type,
            previous_status,
            new_status,
            details
        )
        VALUES (
            p_goal_id,
            'STATUS_CHANGED',
            current_goal.status,
            new_status,
            jsonb_build_object(
                'progress', progress,
                'guardrails_pass', guardrails_pass
            )
        );
    END IF;

    RETURN new_status;
END;
$$;

-- ------------------------------------------------------------
-- ACTIVATE GOAL
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION activate_goal(
    p_goal_id BIGINT,
    p_actor_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    current_status goal_status;
    result_count INTEGER;
BEGIN
    SELECT status
    INTO current_status
    FROM goals
    WHERE goal_id = p_goal_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Goal does not exist.';
    END IF;

    IF current_status <> 'draft' THEN
        RAISE EXCEPTION 'Only draft goals can be activated.';
    END IF;

    SELECT COUNT(*)
    INTO result_count
    FROM key_results
    WHERE goal_id = p_goal_id;

    IF result_count = 0 THEN
        RAISE EXCEPTION 'Goal requires at least one Key Result.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM employees
        WHERE employee_id = p_actor_id
          AND is_active = TRUE
    ) THEN
        RAISE EXCEPTION 'Actor must be an active employee.';
    END IF;

    UPDATE goals
    SET status = 'active'
    WHERE goal_id = p_goal_id;

    INSERT INTO goal_audit (
        goal_id,
        event_type,
        previous_status,
        new_status,
        actor_id
    )
    VALUES (
        p_goal_id,
        'ACTIVATED',
        'draft',
        'active',
        p_actor_id
    );
END;
$$;

-- ------------------------------------------------------------
-- PORTFOLIO EVALUATION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE evaluate_active_goals()
LANGUAGE plpgsql
AS $$
DECLARE
    item RECORD;
BEGIN
    FOR item IN
        SELECT goal_id
        FROM goals
        WHERE status IN ('active', 'at_risk')
        ORDER BY goal_id
    LOOP
        PERFORM evaluate_goal(item.goal_id);
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- SAMPLE ORGANIZATION
-- ------------------------------------------------------------

INSERT INTO teams (team_name)
VALUES
    ('Product Management'),
    ('Product Analytics'),
    ('Customer Experience');

INSERT INTO employees (
    team_id,
    employee_name,
    email,
    role
)
SELECT
    team_id,
    'Product Director',
    'director@example.com',
    'director'
FROM teams
WHERE team_name = 'Product Management';

INSERT INTO employees (
    team_id,
    employee_name,
    email,
    role
)
SELECT
    team_id,
    'Product Manager',
    'manager@example.com',
    'product_manager'
FROM teams
WHERE team_name = 'Product Management';

INSERT INTO employees (
    team_id,
    employee_name,
    email,
    role
)
SELECT
    team_id,
    'Analytics Lead',
    'analytics@example.com',
    'analyst'
FROM teams
WHERE team_name = 'Product Analytics';

-- ------------------------------------------------------------
-- SAMPLE METRICS
-- ------------------------------------------------------------

INSERT INTO metrics (
    metric_code,
    metric_name,
    description,
    category,
    direction,
    unit,
    baseline,
    target,
    weight,
    aggregation,
    lower_guardrail,
    upper_guardrail,
    freshness_hours
)
VALUES
(
    'RETENTION',
    'Monthly customer retention',
    'Percentage of customers retained monthly.',
    'lagging',
    'increase',
    'percent',
    70,
    85,
    1,
    'latest',
    60,
    100,
    168
),
(
    'ACTIVATION',
    'New customer activation',
    'Percentage of new customers completing activation.',
    'leading',
    'increase',
    'percent',
    40,
    70,
    1,
    'latest',
    30,
    100,
    72
),
(
    'CHURN',
    'Monthly customer churn',
    'Percentage of customers leaving monthly.',
    'lagging',
    'decrease',
    'percent',
    8,
    4,
    1,
    'latest',
    0,
    10,
    168
),
(
    'CSAT',
    'Customer satisfaction',
    'Average customer satisfaction score.',
    'guardrail',
    'increase',
    'score',
    4.2,
    4.7,
    1,
    'average',
    3.8,
    5.0,
    168
);

-- ------------------------------------------------------------
-- SAMPLE STRATEGIC AND OUTCOME GOALS
-- ------------------------------------------------------------

INSERT INTO goals (
    goal_code,
    title,
    description,
    type,
    owner_id,
    start_date,
    end_date
)
VALUES (
    'STR-001',
    'Improve digital product experience',
    'Strategic objective focused on product usability and customer value.',
    'strategic',
    (
        SELECT employee_id
        FROM employees
        WHERE email = 'director@example.com'
    ),
    '2026-01-01',
    '2026-12-31'
);

INSERT INTO goals (
    goal_code,
    title,
    description,
    type,
    owner_id,
    parent_goal_id,
    start_date,
    end_date
)
VALUES (
    'OBJ-001',
    'Improve customer retention',
    'Improve recurring customer relationships and reduce churn.',
    'okr',
    (
        SELECT employee_id
        FROM employees
        WHERE email = 'manager@example.com'
    ),
    (
        SELECT goal_id
        FROM goals
        WHERE goal_code = 'STR-001'
    ),
    '2026-01-01',
    '2026-12-31'
);

INSERT INTO goals (
    goal_code,
    title,
    description,
    type,
    owner_id,
    start_date,
    end_date
)
VALUES (
    'OBJ-002',
    'Improve customer satisfaction',
    'Maintain customer experience above the minimum quality threshold.',
    'outcome',
    (
        SELECT employee_id
        FROM employees
        WHERE email = 'manager@example.com'
    ),
    '2026-01-01',
    '2026-12-31'
);

-- ------------------------------------------------------------
-- ASSIGN KEY RESULTS
-- ------------------------------------------------------------

INSERT INTO key_results (goal_id, metric_id, weight)
SELECT
    g.goal_id,
    m.metric_id,
    CASE
        WHEN m.metric_code = 'RETENTION' THEN 3
        WHEN m.metric_code = 'CHURN' THEN 2
        WHEN m.metric_code = 'ACTIVATION' THEN 1
    END
FROM goals g
CROSS JOIN metrics m
WHERE g.goal_code = 'OBJ-001'
AND m.metric_code IN (
    'RETENTION',
    'CHURN',
    'ACTIVATION'
);

INSERT INTO key_results (goal_id, metric_id, weight)
SELECT
    g.goal_id,
    m.metric_id,
    1
FROM goals g
CROSS JOIN metrics m
WHERE g.goal_code = 'OBJ-002'
AND m.metric_code = 'CSAT';

-- ------------------------------------------------------------
-- SAMPLE MEASUREMENTS
-- ------------------------------------------------------------

INSERT INTO metric_observations (
    metric_id,
    observed_value,
    observed_at,
    source,
    confidence
)
SELECT
    metric_id,
    CASE metric_code
        WHEN 'RETENTION' THEN 80
        WHEN 'ACTIVATION' THEN 60
        WHEN 'CHURN' THEN 5
        WHEN 'CSAT' THEN 4.3
    END,
    '2026-11-01 10:00:00+00',
    'Product analytics platform',
    0.95
FROM metrics;

-- ------------------------------------------------------------
-- ACTIVATE GOALS
-- ------------------------------------------------------------

SELECT activate_goal(
    g.goal_id,
    e.employee_id
)
FROM goals g
CROSS JOIN employees e
WHERE g.goal_code IN ('STR-001', 'OBJ-001', 'OBJ-002')
AND e.email = 'manager@example.com'
AND g.status = 'draft';

-- ------------------------------------------------------------
-- RETRIEVAL: GOAL AND METRIC PERFORMANCE
-- ------------------------------------------------------------

SELECT
    goal_code,
    title,
    type,
    status,
    weighted_progress,
    key_result_count,
    all_guardrails_pass,
    all_metrics_fresh
FROM objective_performance
ORDER BY goal_code;

-- ------------------------------------------------------------
-- RETRIEVAL: INDIVIDUAL KEY RESULTS
-- ------------------------------------------------------------

SELECT
    goal_code,
    metric_code,
    metric_name,
    baseline,
    current_value,
    target,
    progress_percent,
    remaining_value,
    confidence,
    within_guardrails
FROM key_result_performance
ORDER BY goal_code, metric_code;

-- ------------------------------------------------------------
-- AGGREGATION: PORTFOLIO STATUS
-- ------------------------------------------------------------

SELECT
    status,
    COUNT(*) AS objective_count,
    ROUND(AVG(weighted_progress), 2) AS average_progress
FROM objective_performance
GROUP BY status
ORDER BY status;

-- ------------------------------------------------------------
-- STRATEGIC ALIGNMENT REPORT
-- ------------------------------------------------------------

SELECT
    parent.goal_code AS strategic_goal,
    child.goal_code AS aligned_objective,
    child.title,
    child.weighted_progress
FROM objective_performance child
JOIN goals child_record
    ON child_record.goal_id = child.goal_id
JOIN goals parent
    ON parent.goal_id = child_record.parent_goal_id
ORDER BY parent.goal_code, child.goal_code;

-- ------------------------------------------------------------
-- LEADING AND LAGGING INDICATOR ANALYSIS
-- ------------------------------------------------------------

SELECT
    category,
    COUNT(*) AS metric_count,
    ROUND(AVG(progress_percent), 2) AS average_progress
FROM metric_performance
GROUP BY category
ORDER BY category;

-- ------------------------------------------------------------
-- ELIGIBILITY AND DATA QUALITY
-- ------------------------------------------------------------

SELECT
    goal_code,
    title,
    weighted_progress,
    all_guardrails_pass,
    all_metrics_fresh,

    CASE
        WHEN key_result_count = 0 THEN 'INVALID_NO_KEY_RESULTS'
        WHEN NOT all_guardrails_pass THEN 'AT_RISK_GUARDRAIL'
        WHEN NOT all_metrics_fresh THEN 'STALE_DATA'
        WHEN weighted_progress >= 100 THEN 'TARGET_REACHED'
        ELSE 'UNDER_MONITORING'
    END AS evaluation_result

FROM objective_performance;

-- ------------------------------------------------------------
-- IDENTIFY GOALS REQUIRING ATTENTION
-- ------------------------------------------------------------

SELECT
    goal_code,
    title,
    status,
    weighted_progress,
    end_date
FROM objective_performance
WHERE status IN ('active', 'at_risk')
AND (
    weighted_progress < 40
    OR NOT all_guardrails_pass
    OR NOT all_metrics_fresh
)
ORDER BY weighted_progress;

-- ------------------------------------------------------------
-- TRANSACTIONAL GOAL EVALUATION
-- ------------------------------------------------------------

SAVEPOINT before_evaluation;

CALL evaluate_active_goals();

SELECT
    goal_code,
    title,
    status,
    weighted_progress
FROM objective_performance
ORDER BY goal_code;

RELEASE SAVEPOINT before_evaluation;

COMMIT;
