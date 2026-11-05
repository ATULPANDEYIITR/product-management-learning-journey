-- ============================================================
-- OKR MANAGEMENT AND PERFORMANCE GOVERNANCE SYSTEM
-- PostgreSQL 15+
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS okr;

SET search_path TO okr, public;

-- ------------------------------------------------------------
-- ENUMERATED DOMAIN STATES
-- ------------------------------------------------------------

CREATE TYPE indicator_type AS ENUM (
    'leading',
    'lagging'
);

CREATE TYPE objective_status AS ENUM (
    'draft',
    'active',
    'at_risk',
    'completed',
    'cancelled'
);

CREATE TYPE checkin_status AS ENUM (
    'submitted',
    'approved',
    'rejected'
);

CREATE TYPE organizational_role AS ENUM (
    'administrator',
    'executive',
    'department_head',
    'objective_owner',
    'contributor',
    'viewer'
);

-- ------------------------------------------------------------
-- ORGANIZATIONAL STRUCTURE
-- ------------------------------------------------------------

CREATE TABLE departments (
    department_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    employee_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    department_id BIGINT NOT NULL
        REFERENCES departments(department_id),
    role organizational_role NOT NULL DEFAULT 'contributor',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(full_name)) > 0)
);

CREATE TABLE planning_periods (
    period_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    period_name VARCHAR(30) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'planning',

    CHECK (end_date > start_date),
    CHECK (status IN ('planning', 'active', 'closed'))
);

-- ------------------------------------------------------------
-- OBJECTIVES
-- ------------------------------------------------------------

CREATE TABLE objectives (
    objective_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    objective_code VARCHAR(40) NOT NULL UNIQUE,
    title VARCHAR(250) NOT NULL,
    description TEXT NOT NULL DEFAULT '',

    department_id BIGINT NOT NULL
        REFERENCES departments(department_id),

    owner_id BIGINT NOT NULL
        REFERENCES employees(employee_id),

    period_id BIGINT NOT NULL
        REFERENCES planning_periods(period_id),

    parent_objective_id BIGINT
        REFERENCES objectives(objective_id)
        ON DELETE RESTRICT,

    status objective_status NOT NULL DEFAULT 'draft',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(title)) > 0),
    CHECK (parent_objective_id IS NULL
           OR parent_objective_id <> objective_id)
);

-- ------------------------------------------------------------
-- KEY RESULTS
-- ------------------------------------------------------------

CREATE TABLE key_results (
    key_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    objective_id BIGINT NOT NULL
        REFERENCES objectives(objective_id)
        ON DELETE CASCADE,

    title VARCHAR(250) NOT NULL,

    baseline NUMERIC(18,4) NOT NULL,
    current_value NUMERIC(18,4) NOT NULL,
    target_value NUMERIC(18,4) NOT NULL,

    unit VARCHAR(40) NOT NULL,

    indicator indicator_type NOT NULL,

    weight NUMERIC(8,4) NOT NULL DEFAULT 1.0,

    higher_is_better BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(unit)) > 0),
    CHECK (baseline <> target_value),
    CHECK (weight > 0),

    CHECK (
        (higher_is_better AND target_value > baseline)
        OR
        (NOT higher_is_better AND target_value < baseline)
    ),

    UNIQUE (objective_id, title)
);

-- ------------------------------------------------------------
-- KEY RESULT HISTORY
-- ------------------------------------------------------------

CREATE TABLE key_result_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    key_result_id BIGINT NOT NULL
        REFERENCES key_results(key_result_id)
        ON DELETE CASCADE,

    previous_value NUMERIC(18,4) NOT NULL,
    new_value NUMERIC(18,4) NOT NULL,

    updated_by BIGINT NOT NULL
        REFERENCES employees(employee_id),

    update_note TEXT NOT NULL DEFAULT '',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- CHECK-IN WORKFLOW
-- ------------------------------------------------------------

CREATE TABLE checkins (
    checkin_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    objective_id BIGINT NOT NULL
        REFERENCES objectives(objective_id)
        ON DELETE CASCADE,

    submitted_by BIGINT NOT NULL
        REFERENCES employees(employee_id),

    status checkin_status NOT NULL DEFAULT 'submitted',

    confidence_score SMALLINT NOT NULL,

    narrative TEXT NOT NULL,

    blockers TEXT NOT NULL DEFAULT '',

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    reviewed_by BIGINT REFERENCES employees(employee_id),

    reviewed_at TIMESTAMPTZ,

    CHECK (confidence_score BETWEEN 1 AND 10),

    CHECK (
        (status = 'submitted'
         AND reviewed_by IS NULL
         AND reviewed_at IS NULL)
        OR
        (status IN ('approved', 'rejected')
         AND reviewed_by IS NOT NULL
         AND reviewed_at IS NOT NULL)
    )
);

CREATE TABLE checkin_updates (
    checkin_update_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    checkin_id BIGINT NOT NULL
        REFERENCES checkins(checkin_id)
        ON DELETE CASCADE,

    key_result_id BIGINT NOT NULL
        REFERENCES key_results(key_result_id),

    reported_value NUMERIC(18,4) NOT NULL,

    UNIQUE (checkin_id, key_result_id)
);

-- ------------------------------------------------------------
-- ALIGNMENT AND GOVERNANCE
-- ------------------------------------------------------------

CREATE TABLE objective_alignment (
    parent_objective_id BIGINT NOT NULL
        REFERENCES objectives(objective_id)
        ON DELETE CASCADE,

    child_objective_id BIGINT NOT NULL
        REFERENCES objectives(objective_id)
        ON DELETE CASCADE,

    alignment_description TEXT NOT NULL DEFAULT '',

    PRIMARY KEY (parent_objective_id, child_objective_id),

    CHECK (parent_objective_id <> child_objective_id)
);

CREATE TABLE objective_permissions (
    objective_id BIGINT NOT NULL
        REFERENCES objectives(objective_id)
        ON DELETE CASCADE,

    employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id)
        ON DELETE CASCADE,

    can_update BOOLEAN NOT NULL DEFAULT FALSE,
    can_review BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (objective_id, employee_id)
);

CREATE TABLE audit_events (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    objective_id BIGINT
        REFERENCES objectives(objective_id)
        ON DELETE SET NULL,

    actor_id BIGINT
        REFERENCES employees(employee_id)
        ON DELETE SET NULL,

    event_type VARCHAR(60) NOT NULL,
    event_details JSONB NOT NULL DEFAULT '{}'::jsonb,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- INDEXES
-- ------------------------------------------------------------

CREATE INDEX idx_objectives_department_period
    ON objectives(department_id, period_id);

CREATE INDEX idx_objectives_owner_status
    ON objectives(owner_id, status);

CREATE INDEX idx_objectives_parent
    ON objectives(parent_objective_id);

CREATE INDEX idx_key_results_objective
    ON key_results(objective_id);

CREATE INDEX idx_key_results_indicator
    ON key_results(indicator);

CREATE INDEX idx_history_key_result_date
    ON key_result_history(key_result_id, recorded_at DESC);

CREATE INDEX idx_checkins_objective_date
    ON checkins(objective_id, submitted_at DESC);

CREATE INDEX idx_audit_objective_date
    ON audit_events(objective_id, occurred_at DESC);

CREATE INDEX idx_audit_details
    ON audit_events USING GIN(event_details);

-- ------------------------------------------------------------
-- OBJECTIVE ALIGNMENT VALIDATION
-- Prevents cross-period alignment and cyclic parent relationships.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_objective_alignment()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_period BIGINT;
    child_period BIGINT;
    cycle_found BOOLEAN;
BEGIN
    SELECT period_id
    INTO parent_period
    FROM objectives
    WHERE objective_id = NEW.parent_objective_id;

    SELECT period_id
    INTO child_period
    FROM objectives
    WHERE objective_id = NEW.child_objective_id;

    IF parent_period IS NULL OR child_period IS NULL THEN
        RAISE EXCEPTION 'Both objectives must exist.';
    END IF;

    IF parent_period <> child_period THEN
        RAISE EXCEPTION
            'Parent and child objectives must use the same period.';
    END IF;

    WITH RECURSIVE descendants(id) AS (
        SELECT NEW.child_objective_id

        UNION

        SELECT oa.child_objective_id
        FROM objective_alignment oa
        JOIN descendants d
          ON oa.parent_objective_id = d.id
    )
    SELECT EXISTS (
        SELECT 1
        FROM descendants
        WHERE id = NEW.parent_objective_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION 'Objective alignment cycle detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_alignment
BEFORE INSERT OR UPDATE ON objective_alignment
FOR EACH ROW
EXECUTE FUNCTION validate_objective_alignment();

-- ------------------------------------------------------------
-- KEY RESULT HISTORY TRIGGER
-- Every metric modification creates an audit-history record.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION record_key_result_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    actor BIGINT;
BEGIN
    IF NEW.current_value IS DISTINCT FROM OLD.current_value THEN

        actor := NULLIF(
            current_setting('okr.actor_id', TRUE),
            ''
        )::BIGINT;

        IF actor IS NULL THEN
            RAISE EXCEPTION
                'An authenticated OKR actor must be specified.';
        END IF;

        IF NOT EXISTS (
            SELECT 1
            FROM employees
            WHERE employee_id = actor
              AND is_active = TRUE
        ) THEN
            RAISE EXCEPTION 'Invalid or inactive actor.';
        END IF;

        INSERT INTO key_result_history (
            key_result_id,
            previous_value,
            new_value,
            updated_by
        )
        VALUES (
            OLD.key_result_id,
            OLD.current_value,
            NEW.current_value,
            actor
        );

        UPDATE objectives
        SET updated_at = CURRENT_TIMESTAMP
        WHERE objective_id = NEW.objective_id;

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_key_result_history
AFTER UPDATE OF current_value ON key_results
FOR EACH ROW
EXECUTE FUNCTION record_key_result_change();

-- ------------------------------------------------------------
-- OBJECTIVE PROGRESS FUNCTION
-- Uses weighted key-result progress.
-- Values are clamped between zero and one.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_objective_progress(
    p_objective_id BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(
        SUM(
            LEAST(
                1.0,
                GREATEST(
                    0.0,
                    (current_value - baseline)
                    / (target_value - baseline)
                )
            ) * weight
        ) / NULLIF(SUM(weight), 0),
        0
    )
    FROM key_results
    WHERE objective_id = p_objective_id;
$$;

-- ------------------------------------------------------------
-- INDICATOR PROGRESS FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_indicator_progress(
    p_objective_id BIGINT,
    p_indicator indicator_type
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT AVG(
        LEAST(
            1.0,
            GREATEST(
                0.0,
                (current_value - baseline)
                / (target_value - baseline)
            )
        )
    )
    FROM key_results
    WHERE objective_id = p_objective_id
      AND indicator = p_indicator;
$$;

-- ------------------------------------------------------------
-- OBJECTIVE STATE EVALUATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_objective(
    p_objective_id BIGINT
)
RETURNS objective_status
LANGUAGE plpgsql
AS $$
DECLARE
    current_status objective_status;
    score NUMERIC;
    new_status objective_status;
BEGIN
    SELECT status
    INTO current_status
    FROM objectives
    WHERE objective_id = p_objective_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Objective % not found.', p_objective_id;
    END IF;

    IF current_status IN ('completed', 'cancelled', 'draft') THEN
        RETURN current_status;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM key_results
        WHERE objective_id = p_objective_id
    ) THEN
        RAISE EXCEPTION
            'An active objective requires at least one key result.';
    END IF;

    score := calculate_objective_progress(p_objective_id);

    IF score >= 1.0 THEN
        new_status := 'completed';
    ELSIF score < 0.4 THEN
        new_status := 'at_risk';
    ELSE
        new_status := 'active';
    END IF;

    UPDATE objectives
    SET status = new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE objective_id = p_objective_id;

    RETURN new_status;
END;
$$;

-- ------------------------------------------------------------
-- OBJECTIVE ACTIVATION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE activate_objective(
    p_objective_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE objectives
    SET status = 'active',
        updated_at = CURRENT_TIMESTAMP
    WHERE objective_id = p_objective_id
      AND status = 'draft'
      AND EXISTS (
          SELECT 1
          FROM key_results
          WHERE objective_id = p_objective_id
      );

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Objective cannot be activated or has no key results.';
    END IF;

    INSERT INTO audit_events (
        objective_id,
        event_type,
        event_details
    )
    VALUES (
        p_objective_id,
        'objective_activated',
        jsonb_build_object('status', 'active')
    );
END;
$$;

-- ------------------------------------------------------------
-- CHECK-IN APPROVAL PROCEDURE
-- Only an authorized reviewer may approve a submitted check-in.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE approve_checkin(
    p_checkin_id BIGINT,
    p_reviewer_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    target_objective BIGINT;
BEGIN
    SELECT objective_id
    INTO target_objective
    FROM checkins
    WHERE checkin_id = p_checkin_id
      AND status = 'submitted'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Submitted check-in not found.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM employees
        WHERE employee_id = p_reviewer_id
          AND is_active = TRUE
          AND role IN (
              'administrator',
              'executive',
              'department_head'
          )
    ) AND NOT EXISTS (
        SELECT 1
        FROM objective_permissions
        WHERE objective_id = target_objective
          AND employee_id = p_reviewer_id
          AND can_review = TRUE
    ) THEN
        RAISE EXCEPTION 'Reviewer is not authorized.';
    END IF;

    UPDATE checkins
    SET status = 'approved',
        reviewed_by = p_reviewer_id,
        reviewed_at = CURRENT_TIMESTAMP
    WHERE checkin_id = p_checkin_id;

    INSERT INTO audit_events (
        objective_id,
        actor_id,
        event_type,
        event_details
    )
    VALUES (
        target_objective,
        p_reviewer_id,
        'checkin_approved',
        jsonb_build_object('checkin_id', p_checkin_id)
    );
END;
$$;

-- ------------------------------------------------------------
-- REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW objective_performance AS
SELECT
    o.objective_id,
    o.objective_code,
    o.title,
    d.department_name,
    e.full_name AS owner_name,
    p.period_name,
    o.status,

    COUNT(kr.key_result_id) AS total_key_results,

    calculate_objective_progress(o.objective_id) AS progress,

    calculate_indicator_progress(
        o.objective_id,
        'leading'
    ) AS leading_progress,

    calculate_indicator_progress(
        o.objective_id,
        'lagging'
    ) AS lagging_progress

FROM objectives o

JOIN departments d
    ON d.department_id = o.department_id

JOIN employees e
    ON e.employee_id = o.owner_id

JOIN planning_periods p
    ON p.period_id = o.period_id

LEFT JOIN key_results kr
    ON kr.objective_id = o.objective_id

GROUP BY
    o.objective_id,
    o.objective_code,
    o.title,
    d.department_name,
    e.full_name,
    p.period_name,
    o.status;

-- ------------------------------------------------------------
-- SAMPLE ORGANIZATION
-- ------------------------------------------------------------

INSERT INTO departments (department_name)
VALUES
    ('Executive'),
    ('Product'),
    ('Technology'),
    ('Customer Experience');

INSERT INTO employees (
    full_name, email, department_id, role
)
SELECT
    data.full_name,
    data.email,
    d.department_id,
    data.role::organizational_role
FROM (
    VALUES
        ('Chief Executive Officer', 'ceo@example.com',
         'Executive', 'executive'),
        ('Product Director', 'product@example.com',
         'Product', 'department_head'),
        ('Technology Director', 'technology@example.com',
         'Technology', 'department_head'),
        ('Customer Experience Lead', 'cx@example.com',
         'Customer Experience', 'objective_owner'),
        ('Business Analyst', 'analyst@example.com',
         'Product', 'contributor')
) AS data(full_name, email, department_name, role)
JOIN departments d
    ON d.department_name = data.department_name;

INSERT INTO planning_periods (
    period_name,
    start_date,
    end_date,
    status
)
VALUES (
    '2026-Q4',
    '2026-10-01',
    '2026-12-31',
    'active'
);

-- ------------------------------------------------------------
-- SAMPLE OBJECTIVES
-- ------------------------------------------------------------

INSERT INTO objectives (
    objective_code,
    title,
    description,
    department_id,
    owner_id,
    period_id
)
SELECT
    'COMPANY-001',
    'Improve digital banking competitiveness',
    'Improve customer outcomes and digital adoption.',
    d.department_id,
    e.employee_id,
    p.period_id
FROM departments d
JOIN employees e ON e.email = 'ceo@example.com'
JOIN planning_periods p ON p.period_name = '2026-Q4'
WHERE d.department_name = 'Executive';

INSERT INTO objectives (
    objective_code,
    title,
    description,
    department_id,
    owner_id,
    period_id,
    parent_objective_id
)
SELECT
    'PRODUCT-001',
    'Improve mobile onboarding',
    'Reduce registration friction and improve conversion.',
    d.department_id,
    e.employee_id,
    p.period_id,
    parent.objective_id
FROM departments d
JOIN employees e ON e.email = 'product@example.com'
JOIN planning_periods p ON p.period_name = '2026-Q4'
JOIN objectives parent ON parent.objective_code = 'COMPANY-001'
WHERE d.department_name = 'Product';

INSERT INTO objectives (
    objective_code,
    title,
    description,
    department_id,
    owner_id,
    period_id,
    parent_objective_id
)
SELECT
    'TECH-001',
    'Improve platform reliability',
    'Reduce service interruptions and improve availability.',
    d.department_id,
    e.employee_id,
    p.period_id,
    parent.objective_id
FROM departments d
JOIN employees e ON e.email = 'technology@example.com'
JOIN planning_periods p ON p.period_name = '2026-Q4'
JOIN objectives parent ON parent.objective_code = 'COMPANY-001'
WHERE d.department_name = 'Technology';

-- ------------------------------------------------------------
-- SAMPLE KEY RESULTS
-- ------------------------------------------------------------

INSERT INTO key_results (
    objective_id,
    title,
    baseline,
    current_value,
    target_value,
    unit,
    indicator,
    weight
)
SELECT
    o.objective_id,
    kr.title,
    kr.baseline,
    kr.current_value,
    kr.target_value,
    kr.unit,
    kr.indicator::indicator_type,
    kr.weight
FROM (
    VALUES
        ('COMPANY-001', 'Customer retention rate',
         70.0, 76.0, 90.0, '%', 'lagging', 2.0),

        ('COMPANY-001', 'Monthly active customers',
         100000.0, 125000.0, 200000.0,
         'customers', 'lagging', 1.0),

        ('PRODUCT-001', 'Usability tests completed',
         0.0, 10.0, 20.0, 'tests', 'leading', 1.0),

        ('PRODUCT-001', 'Onboarding completion rate',
         40.0, 55.0, 80.0, '%', 'lagging', 1.0),

        ('TECH-001', 'Automated reliability tests completed',
         0.0, 70.0, 100.0, 'tests', 'leading', 1.0),

        ('TECH-001', 'Service availability',
         99.0, 99.5, 99.9, '%', 'lagging', 2.0)
) AS kr(
    objective_code,
    title,
    baseline,
    current_value,
    target_value,
    unit,
    indicator,
    weight
)
JOIN objectives o
    ON o.objective_code = kr.objective_code;

-- ------------------------------------------------------------
-- ALIGNMENT RELATIONSHIPS
-- ------------------------------------------------------------

INSERT INTO objective_alignment (
    parent_objective_id,
    child_objective_id,
    alignment_description
)
SELECT
    parent.objective_id,
    child.objective_id,
    'Contributes to enterprise digital banking performance.'
FROM objectives parent
JOIN objectives child
    ON child.parent_objective_id = parent.objective_id
WHERE parent.objective_code = 'COMPANY-001';

-- ------------------------------------------------------------
-- UPDATE PERMISSIONS
-- ------------------------------------------------------------

INSERT INTO objective_permissions (
    objective_id,
    employee_id,
    can_update,
    can_review
)
SELECT
    o.objective_id,
    e.employee_id,
    TRUE,
    FALSE
FROM objectives o
JOIN employees e
    ON (
        o.objective_code = 'COMPANY-001'
        AND e.email = 'ceo@example.com'
    )
    OR (
        o.objective_code = 'PRODUCT-001'
        AND e.email = 'product@example.com'
    )
    OR (
        o.objective_code = 'TECH-001'
        AND e.email = 'technology@example.com'
    );

INSERT INTO objective_permissions (
    objective_id,
    employee_id,
    can_update,
    can_review
)
SELECT
    o.objective_id,
    e.employee_id,
    FALSE,
    TRUE
FROM objectives o
CROSS JOIN employees e
WHERE e.role IN ('executive', 'department_head');

-- ------------------------------------------------------------
-- ACTIVATE OBJECTIVES
-- ------------------------------------------------------------

CALL activate_objective(
    (SELECT objective_id
     FROM objectives
     WHERE objective_code = 'COMPANY-001')
);

CALL activate_objective(
    (SELECT objective_id
     FROM objectives
     WHERE objective_code = 'PRODUCT-001')
);

CALL activate_objective(
    (SELECT objective_id
     FROM objectives
     WHERE objective_code = 'TECH-001')
);

-- ------------------------------------------------------------
-- SECURE KEY RESULT UPDATE
-- The actor is transaction-local and required by the trigger.
-- ------------------------------------------------------------

DO $$
DECLARE
    actor BIGINT;
    result_id BIGINT;
BEGIN
    SELECT employee_id
    INTO actor
    FROM employees
    WHERE email = 'product@example.com';

    PERFORM set_config(
        'okr.actor_id',
        actor::TEXT,
        TRUE
    );

    SELECT kr.key_result_id
    INTO result_id
    FROM key_results kr
    JOIN objectives o USING (objective_id)
    WHERE o.objective_code = 'PRODUCT-001'
      AND kr.indicator = 'leading';

    UPDATE key_results
    SET current_value = 16
    WHERE key_result_id = result_id;
END;
$$;

-- ------------------------------------------------------------
-- CHECK-IN EXAMPLE
-- ------------------------------------------------------------

INSERT INTO checkins (
    objective_id,
    submitted_by,
    confidence_score,
    narrative,
    blockers
)
SELECT
    o.objective_id,
    e.employee_id,
    8,
    'Usability testing has progressed according to plan.',
    'Additional testing capacity is required.'
FROM objectives o
JOIN employees e ON e.email = 'product@example.com'
WHERE o.objective_code = 'PRODUCT-001';

-- ------------------------------------------------------------
-- REPORT 1: OBJECTIVE RETRIEVAL
-- ------------------------------------------------------------

SELECT
    objective_code,
    title,
    department_name,
    owner_name,
    status,
    ROUND(progress * 100, 2) AS progress_percentage
FROM objective_performance
ORDER BY department_name, objective_code;

-- ------------------------------------------------------------
-- REPORT 2: LEADING VS LAGGING INDICATORS
-- ------------------------------------------------------------

SELECT
    objective_code,
    title,
    ROUND(leading_progress * 100, 2) AS leading_percentage,
    ROUND(lagging_progress * 100, 2) AS lagging_percentage
FROM objective_performance
ORDER BY objective_code;

-- ------------------------------------------------------------
-- REPORT 3: DEPARTMENT PERFORMANCE AGGREGATION
-- ------------------------------------------------------------

SELECT
    department_name,
    COUNT(*) AS objective_count,
    ROUND(AVG(progress) * 100, 2) AS average_progress,
    COUNT(*) FILTER (
        WHERE status = 'at_risk'
    ) AS at_risk_objectives,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_objectives
FROM objective_performance
GROUP BY department_name
ORDER BY department_name;

-- ------------------------------------------------------------
-- REPORT 4: KEY RESULT EVALUATION
-- ------------------------------------------------------------

SELECT
    o.objective_code,
    kr.title,
    kr.indicator,
    kr.baseline,
    kr.current_value,
    kr.target_value,
    kr.unit,
    ROUND(
        GREATEST(
            0,
            LEAST(
                1,
                (kr.current_value - kr.baseline)
                / (kr.target_value - kr.baseline)
            )
        ) * 100,
        2
    ) AS progress_percentage
FROM key_results kr
JOIN objectives o USING (objective_id)
ORDER BY o.objective_code, kr.key_result_id;

-- ------------------------------------------------------------
-- REPORT 5: ALIGNMENT TREE
-- ------------------------------------------------------------

WITH RECURSIVE alignment_tree AS (
    SELECT
        o.objective_id,
        o.parent_objective_id,
        o.objective_code,
        o.title,
        0 AS depth,
        ARRAY[o.objective_id] AS path
    FROM objectives o
    WHERE o.parent_objective_id IS NULL

    UNION ALL

    SELECT
        child.objective_id,
        child.parent_objective_id,
        child.objective_code,
        child.title,
        parent.depth + 1,
        parent.path || child.objective_id
    FROM objectives child
    JOIN alignment_tree parent
        ON child.parent_objective_id = parent.objective_id
    WHERE NOT child.objective_id = ANY(parent.path)
)
SELECT
    repeat('  ', depth) || title AS hierarchy,
    objective_code,
    depth
FROM alignment_tree
ORDER BY path;

-- ------------------------------------------------------------
-- REPORT 6: OBJECTIVES WITHOUT KEY RESULTS
-- ------------------------------------------------------------

SELECT
    o.objective_code,
    o.title,
    o.status
FROM objectives o
LEFT JOIN key_results kr
    ON kr.objective_id = o.objective_id
GROUP BY o.objective_id
HAVING COUNT(kr.key_result_id) = 0;

-- ------------------------------------------------------------
-- REPORT 7: CHECK-IN STATUS
-- ------------------------------------------------------------

SELECT
    o.objective_code,
    c.checkin_id,
    e.full_name AS submitted_by,
    c.confidence_score,
    c.status,
    c.submitted_at,
    c.blockers
FROM checkins c
JOIN objectives o USING (objective_id)
JOIN employees e
    ON e.employee_id = c.submitted_by
ORDER BY c.submitted_at DESC;

-- ------------------------------------------------------------
-- REPORT 8: KEY RESULT TREND
-- ------------------------------------------------------------

SELECT
    o.objective_code,
    kr.title,
    h.previous_value,
    h.new_value,
    e.full_name AS updated_by,
    h.recorded_at
FROM key_result_history h
JOIN key_results kr USING (key_result_id)
JOIN objectives o USING (objective_id)
JOIN employees e USING (employee_id)
ORDER BY h.recorded_at DESC;

-- ------------------------------------------------------------
-- ELIGIBILITY DETERMINATION
-- An objective is eligible for completion when:
-- 1. It is active or at risk.
-- 2. It has at least one key result.
-- 3. All weighted key results have reached their targets.
-- ------------------------------------------------------------

SELECT
    o.objective_code,
    o.title,
    o.status,
    calculate_objective_progress(o.objective_id) AS progress,
    (
        o.status IN ('active', 'at_risk')
        AND EXISTS (
            SELECT 1
            FROM key_results kr
            WHERE kr.objective_id = o.objective_id
        )
        AND calculate_objective_progress(o.objective_id) >= 1.0
    ) AS completion_eligible
FROM objectives o
ORDER BY o.objective_code;

-- ------------------------------------------------------------
-- VALIDATION EXAMPLE
-- Detect key results whose latest value exceeds their target.
-- ------------------------------------------------------------

SELECT
    o.objective_code,
    kr.title,
    kr.current_value,
    kr.target_value,
    'Target exceeded; investigate whether the metric is valid.'
        AS validation_message
FROM key_results kr
JOIN objectives o USING (objective_id)
WHERE (
    kr.higher_is_better
    AND kr.current_value > kr.target_value
)
OR (
    NOT kr.higher_is_better
    AND kr.current_value < kr.target_value
);

COMMIT;

-- ------------------------------------------------------------
-- OPTIONAL OPERATIONAL QUERIES
-- ------------------------------------------------------------

-- Recalculate an objective:
-- SELECT evaluate_objective(objective_id)
-- FROM objectives
-- WHERE objective_code = 'PRODUCT-001';

-- Inspect audit history:
-- SELECT * FROM audit_events ORDER BY occurred_at DESC;

-- Inspect key result changes:
-- SELECT * FROM key_result_history ORDER BY recorded_at DESC;

-- Rollback a failed multi-statement update:
-- BEGIN;
-- SET LOCAL okr.actor_id = '2';
-- UPDATE key_results SET current_value = 18
-- WHERE key_result_id = 3;
-- ROLLBACK;
