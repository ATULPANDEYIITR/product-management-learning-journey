-- ============================================================
-- PRODUCT ROADMAP MANAGEMENT SYSTEM
-- PostgreSQL 15+
--
-- Covers:
-- Strategic themes, measurable outcomes, initiatives,
-- prioritization, dependencies, timelines, capacity,
-- governance, decisions, progress and reporting.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_roadmap;

SET search_path TO product_roadmap, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE initiative_status AS ENUM (
    'proposed',
    'approved',
    'planned',
    'in_progress',
    'blocked',
    'completed',
    'cancelled'
);

CREATE TYPE decision_status AS ENUM (
    'approve',
    'reject'
);

CREATE TYPE roadmap_role AS ENUM (
    'product_manager',
    'executive',
    'engineering_lead',
    'finance',
    'stakeholder'
);

-- ============================================================
-- 2. CORE ENTITIES
-- ============================================================

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    planning_start DATE NOT NULL,
    planning_end DATE NOT NULL,
    sprint_capacity INTEGER NOT NULL DEFAULT 40,
    required_approvals INTEGER NOT NULL DEFAULT 2,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (planning_end >= planning_start),
    CHECK (sprint_capacity > 0),
    CHECK (required_approvals > 0)
);

CREATE TABLE roadmap_users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role roadmap_role NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE strategic_themes (
    theme_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES products(product_id) ON DELETE RESTRICT,
    theme_name VARCHAR(150) NOT NULL,
    strategic_objective TEXT NOT NULL,
    executive_sponsor BIGINT
        REFERENCES roadmap_users(user_id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (product_id, theme_name),
    UNIQUE (theme_id, product_id)
);

CREATE TABLE outcomes (
    outcome_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES products(product_id) ON DELETE RESTRICT,
    outcome_name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    unit VARCHAR(40) NOT NULL,
    baseline NUMERIC(14,4) NOT NULL,
    target NUMERIC(14,4) NOT NULL,
    current_value NUMERIC(14,4) NOT NULL,
    measurement_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (baseline <> target),
    UNIQUE (outcome_id, product_id)
);

CREATE TABLE initiatives (
    initiative_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES products(product_id) ON DELETE RESTRICT,
    theme_id BIGINT NOT NULL,
    outcome_id BIGINT NOT NULL,
    initiative_name VARCHAR(180) NOT NULL,
    description TEXT NOT NULL,
    owner_id BIGINT NOT NULL
        REFERENCES roadmap_users(user_id) ON DELETE RESTRICT,

    planned_start DATE NOT NULL,
    planned_end DATE NOT NULL,

    effort_points INTEGER NOT NULL,
    impact_score NUMERIC(5,2) NOT NULL,
    confidence_score NUMERIC(5,2) NOT NULL,
    strategic_alignment NUMERIC(5,2) NOT NULL,

    status initiative_status NOT NULL DEFAULT 'proposed',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (theme_id, product_id)
        REFERENCES strategic_themes(theme_id, product_id),

    FOREIGN KEY (outcome_id, product_id)
        REFERENCES outcomes(outcome_id, product_id),

    CHECK (planned_end >= planned_start),
    CHECK (effort_points > 0),
    CHECK (impact_score BETWEEN 0 AND 10),
    CHECK (confidence_score BETWEEN 0 AND 1),
    CHECK (strategic_alignment BETWEEN 0 AND 1),

    UNIQUE (product_id, initiative_name),
    UNIQUE (initiative_id, product_id)
);

-- A directed edge means prerequisite -> dependent initiative.
CREATE TABLE initiative_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL,
    prerequisite_id BIGINT NOT NULL,
    dependent_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (prerequisite_id, product_id)
        REFERENCES initiatives(initiative_id, product_id)
        ON DELETE CASCADE,

    FOREIGN KEY (dependent_id, product_id)
        REFERENCES initiatives(initiative_id, product_id)
        ON DELETE CASCADE,

    CHECK (prerequisite_id <> dependent_id),

    UNIQUE (prerequisite_id, dependent_id)
);

CREATE TABLE initiative_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    initiative_id BIGINT NOT NULL
        REFERENCES initiatives(initiative_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES roadmap_users(user_id) ON DELETE RESTRICT,
    decision decision_status NOT NULL,
    justification TEXT NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (initiative_id, reviewer_id),
    CHECK (length(trim(justification)) >= 10)
);

CREATE TABLE initiative_status_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    initiative_id BIGINT NOT NULL
        REFERENCES initiatives(initiative_id) ON DELETE CASCADE,
    previous_status initiative_status,
    new_status initiative_status NOT NULL,
    changed_by BIGINT
        REFERENCES roadmap_users(user_id) ON DELETE RESTRICT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    change_reason TEXT
);

CREATE TABLE outcome_measurements (
    measurement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    outcome_id BIGINT NOT NULL
        REFERENCES outcomes(outcome_id) ON DELETE CASCADE,
    measured_value NUMERIC(14,4) NOT NULL,
    measured_at DATE NOT NULL,
    measurement_source VARCHAR(150) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (outcome_id, measured_at)
);

-- ============================================================
-- 3. PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_initiatives_product_status
ON initiatives(product_id, status);

CREATE INDEX idx_initiatives_timeline
ON initiatives(product_id, planned_start, planned_end);

CREATE INDEX idx_initiatives_priority
ON initiatives(
    product_id,
    impact_score DESC,
    confidence_score DESC
);

CREATE INDEX idx_dependencies_dependent
ON initiative_dependencies(dependent_id);

CREATE INDEX idx_dependencies_prerequisite
ON initiative_dependencies(prerequisite_id);

CREATE INDEX idx_decisions_initiative
ON initiative_decisions(initiative_id, decision);

CREATE INDEX idx_outcome_measurements_date
ON outcome_measurements(outcome_id, measured_at DESC);

CREATE INDEX idx_history_initiative
ON initiative_status_history(initiative_id, changed_at DESC);

-- ============================================================
-- 4. VALIDATION FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION validate_initiative_timeline()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_start DATE;
    v_end DATE;
BEGIN
    SELECT planning_start, planning_end
    INTO v_start, v_end
    FROM products
    WHERE product_id = NEW.product_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product does not exist.';
    END IF;

    IF NEW.planned_start < v_start
       OR NEW.planned_end > v_end THEN
        RAISE EXCEPTION
            'Initiative dates exceed the product planning period.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_initiative_timeline
BEFORE INSERT OR UPDATE OF
    product_id, planned_start, planned_end
ON initiatives
FOR EACH ROW
EXECUTE FUNCTION validate_initiative_timeline();

-- Detect circular dependencies using a recursive CTE.
CREATE OR REPLACE FUNCTION validate_dependency_graph()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cycle BOOLEAN;
    v_prerequisite_end DATE;
    v_dependent_start DATE;
BEGIN
    IF NEW.prerequisite_id = NEW.dependent_id THEN
        RAISE EXCEPTION 'Self-dependency is prohibited.';
    END IF;

    SELECT planned_end
    INTO v_prerequisite_end
    FROM initiatives
    WHERE initiative_id = NEW.prerequisite_id;

    SELECT planned_start
    INTO v_dependent_start
    FROM initiatives
    WHERE initiative_id = NEW.dependent_id;

    IF v_prerequisite_end >= v_dependent_start THEN
        RAISE EXCEPTION
            'Dependent initiative must start after prerequisite ends.';
    END IF;

    WITH RECURSIVE reachable(id) AS (
        SELECT NEW.dependent_id

        UNION

        SELECT d.dependent_id
        FROM initiative_dependencies d
        JOIN reachable r
            ON d.prerequisite_id = r.id
        WHERE d.product_id = NEW.product_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM reachable
        WHERE id = NEW.prerequisite_id
    )
    INTO v_cycle;

    IF v_cycle THEN
        RAISE EXCEPTION 'Circular dependency detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency_graph
BEFORE INSERT OR UPDATE
ON initiative_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_graph();

-- ============================================================
-- 5. STATUS HISTORY
-- ============================================================

CREATE OR REPLACE FUNCTION capture_initiative_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO initiative_status_history (
            initiative_id,
            previous_status,
            new_status,
            change_reason
        )
        VALUES (
            NEW.initiative_id,
            NULL,
            NEW.status,
            'Initiative created'
        );

    ELSIF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO initiative_status_history (
            initiative_id,
            previous_status,
            new_status,
            change_reason
        )
        VALUES (
            NEW.initiative_id,
            OLD.status,
            NEW.status,
            'Status changed'
        );
    END IF;

    NEW.updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_capture_initiative_status
BEFORE INSERT OR UPDATE OF status
ON initiatives
FOR EACH ROW
EXECUTE FUNCTION capture_initiative_status();

-- ============================================================
-- 6. APPROVAL AND DEPENDENCY POLICIES
-- ============================================================

CREATE OR REPLACE FUNCTION check_initiative_approval(
    p_initiative_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT
        COUNT(*) FILTER (
            WHERE d.decision = 'approve'
        ) >= p.required_approvals

        AND COUNT(*) FILTER (
            WHERE d.decision = 'reject'
        ) = 0

    FROM initiatives i
    JOIN products p
        ON p.product_id = i.product_id
    LEFT JOIN initiative_decisions d
        ON d.initiative_id = i.initiative_id
    WHERE i.initiative_id = p_initiative_id
    GROUP BY p.required_approvals;
$$;

CREATE OR REPLACE FUNCTION check_dependencies_complete(
    p_initiative_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM initiative_dependencies d
        JOIN initiatives prerequisite
            ON prerequisite.initiative_id = d.prerequisite_id
        WHERE d.dependent_id = p_initiative_id
          AND prerequisite.status <> 'completed'
    );
$$;

-- Centralized eligibility function.
CREATE OR REPLACE FUNCTION evaluate_initiative(
    p_initiative_id BIGINT
)
RETURNS TABLE (
    initiative_id BIGINT,
    approval_eligible BOOLEAN,
    dependency_eligible BOOLEAN,
    status_eligible BOOLEAN,
    merge_or_execution_eligible BOOLEAN,
    reason TEXT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        i.initiative_id,

        check_initiative_approval(i.initiative_id),

        check_dependencies_complete(i.initiative_id),

        i.status IN ('approved', 'planned'),

        (
            check_initiative_approval(i.initiative_id)
            AND check_dependencies_complete(i.initiative_id)
            AND i.status IN ('approved', 'planned')
        ),

        CASE
            WHEN NOT check_initiative_approval(i.initiative_id)
                THEN 'Approval requirements not met'
            WHEN NOT check_dependencies_complete(i.initiative_id)
                THEN 'Prerequisite initiatives incomplete'
            WHEN i.status NOT IN ('approved', 'planned')
                THEN 'Initiative status is not eligible'
            ELSE 'Eligible for execution planning'
        END

    FROM initiatives i
    WHERE i.initiative_id = p_initiative_id;
$$;

-- ============================================================
-- 7. PRIORITIZATION VIEW
-- ============================================================

CREATE OR REPLACE VIEW prioritized_initiatives AS
SELECT
    i.initiative_id,
    p.product_name,
    t.theme_name,
    i.initiative_name,
    o.outcome_name,
    u.full_name AS owner,
    i.planned_start,
    i.planned_end,
    i.effort_points,
    i.impact_score,
    i.confidence_score,
    i.strategic_alignment,
    ROUND(
        (
            i.impact_score *
            i.confidence_score *
            i.strategic_alignment /
            i.effort_points
        )::NUMERIC,
        3
    ) AS priority_score,
    i.status
FROM initiatives i
JOIN products p
    ON p.product_id = i.product_id
JOIN strategic_themes t
    ON t.theme_id = i.theme_id
JOIN outcomes o
    ON o.outcome_id = i.outcome_id
JOIN roadmap_users u
    ON u.user_id = i.owner_id;

-- ============================================================
-- 8. OUTCOME PERFORMANCE VIEW
-- ============================================================

CREATE OR REPLACE VIEW outcome_performance AS
SELECT
    outcome_id,
    product_id,
    outcome_name,
    metric_name,
    baseline,
    current_value,
    target,
    unit,

    ROUND(
        GREATEST(
            0,
            LEAST(
                100,
                (
                    (current_value - baseline) /
                    NULLIF(target - baseline, 0)
                ) * 100
            )
        )::NUMERIC,
        2
    ) AS progress_percent,

    CASE
        WHEN target > baseline
            THEN current_value >= target
        ELSE current_value <= target
    END AS target_achieved

FROM outcomes;

-- ============================================================
-- 9. CAPACITY REPORTING
-- ============================================================

CREATE OR REPLACE FUNCTION sprint_capacity_report(
    p_product_id BIGINT
)
RETURNS TABLE (
    sprint_number INTEGER,
    sprint_start DATE,
    sprint_end DATE,
    allocated_effort BIGINT,
    capacity INTEGER,
    overloaded BOOLEAN
)
LANGUAGE sql
STABLE
AS $$
    WITH product_period AS (
        SELECT
            planning_start,
            planning_end,
            sprint_capacity
        FROM products
        WHERE product_id = p_product_id
    ),
    sprints AS (
        SELECT
            gs::INTEGER AS sprint_number,
            pp.planning_start + gs * 14 AS sprint_start,
            LEAST(
                pp.planning_start + gs * 14 + 13,
                pp.planning_end
            ) AS sprint_end,
            pp.sprint_capacity
        FROM product_period pp
        CROSS JOIN LATERAL generate_series(
            0,
            CEIL(
                (pp.planning_end - pp.planning_start + 1)::NUMERIC
                / 14
            )::INTEGER - 1
        ) gs
    ),
    allocations AS (
        SELECT
            s.sprint_number,
            COALESCE(SUM(i.effort_points), 0)::BIGINT AS effort
        FROM sprints s
        LEFT JOIN initiatives i
            ON i.planned_start <= s.sprint_end
           AND i.planned_end >= s.sprint_start
           AND i.product_id = p_product_id
           AND i.status NOT IN ('proposed', 'cancelled')
        GROUP BY s.sprint_number
    )
    SELECT
        s.sprint_number,
        s.sprint_start,
        s.sprint_end,
        a.effort,
        s.sprint_capacity,
        a.effort > s.sprint_capacity
    FROM sprints s
    JOIN allocations a USING (sprint_number)
    ORDER BY s.sprint_number;
$$;

-- ============================================================
-- 10. WORKFLOW PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE transition_initiative(
    p_initiative_id BIGINT,
    p_next_status initiative_status
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current initiative_status;
BEGIN
    SELECT status
    INTO v_current
    FROM initiatives
    WHERE initiative_id = p_initiative_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Initiative not found.';
    END IF;

    IF p_next_status = 'approved' THEN
        IF NOT check_initiative_approval(p_initiative_id) THEN
            RAISE EXCEPTION 'Approval requirements are not met.';
        END IF;

    ELSIF p_next_status = 'planned' THEN
        IF v_current <> 'approved' THEN
            RAISE EXCEPTION 'Only approved initiatives can be planned.';
        END IF;

    ELSIF p_next_status = 'in_progress' THEN
        IF v_current NOT IN ('planned', 'blocked') THEN
            RAISE EXCEPTION 'Invalid status for execution.';
        END IF;

        IF NOT check_dependencies_complete(p_initiative_id) THEN
            RAISE EXCEPTION 'Dependencies are incomplete.';
        END IF;

        IF v_current = 'blocked' THEN
            IF NOT EXISTS (
                SELECT 1
                FROM initiatives
                WHERE initiative_id = p_initiative_id
                  AND status = 'blocked'
            ) THEN
                RAISE EXCEPTION 'Invalid blocked state.';
            END IF;
        END IF;

    ELSIF p_next_status = 'completed' THEN
        IF v_current <> 'in_progress' THEN
            RAISE EXCEPTION
                'Only in-progress initiatives can be completed.';
        END IF;

    ELSIF p_next_status = 'blocked' THEN
        IF v_current NOT IN ('planned', 'in_progress') THEN
            RAISE EXCEPTION 'Initiative cannot be blocked.';
        END IF;

    ELSIF p_next_status = 'cancelled' THEN
        IF v_current IN ('completed', 'cancelled') THEN
            RAISE EXCEPTION 'Terminal state cannot be cancelled.';
        END IF;

    ELSE
        RAISE EXCEPTION
            'Requested transition is not supported by this procedure.';
    END IF;

    UPDATE initiatives
    SET status = p_next_status
    WHERE initiative_id = p_initiative_id;
END;
$$;

-- ============================================================
-- 11. SAMPLE DATA
-- ============================================================

INSERT INTO products (
    product_name,
    description,
    planning_start,
    planning_end,
    sprint_capacity,
    required_approvals
)
VALUES (
    'Enterprise Commerce Platform',
    'Digital commerce and payment experience platform.',
    '2027-01-01',
    '2027-03-31',
    40,
    2
);

INSERT INTO roadmap_users (
    full_name,
    email,
    role
)
VALUES
(
    'Aarav Sharma',
    'aarav.sharma@example.com',
    'executive'
),
(
    'Priya Verma',
    'priya.verma@example.com',
    'product_manager'
),
(
    'Rahul Mehta',
    'rahul.mehta@example.com',
    'engineering_lead'
),
(
    'Neha Singh',
    'neha.singh@example.com',
    'finance'
),
(
    'Karan Rao',
    'karan.rao@example.com',
    'stakeholder'
);

INSERT INTO strategic_themes (
    product_id,
    theme_name,
    strategic_objective,
    executive_sponsor
)
SELECT
    p.product_id,
    data.theme_name,
    data.objective,
    u.user_id
FROM products p
CROSS JOIN (
    VALUES
    (
        'Customer Experience',
        'Increase customer satisfaction and checkout conversion.',
        'aarav.sharma@example.com'
    ),
    (
        'Platform Reliability',
        'Improve availability and payment infrastructure stability.',
        'rahul.mehta@example.com'
    ),
    (
        'Revenue Growth',
        'Increase digital sales through better product discovery.',
        'aarav.sharma@example.com'
    )
) AS data(theme_name, objective, sponsor_email)
JOIN roadmap_users u
    ON u.email = data.sponsor_email
WHERE p.product_name = 'Enterprise Commerce Platform';

INSERT INTO outcomes (
    product_id,
    outcome_name,
    description,
    metric_name,
    unit,
    baseline,
    target,
    current_value,
    measurement_date
)
SELECT
    product_id,
    data.name,
    data.description,
    data.metric,
    data.unit,
    data.baseline,
    data.target,
    data.current_value,
    DATE '2027-01-01'
FROM products
CROSS JOIN (
    VALUES
    (
        'Checkout Completion',
        'Increase the percentage of customers completing checkout.',
        'checkout_completion_rate',
        '%',
        65.0,
        85.0,
        72.0
    ),
    (
        'Platform Availability',
        'Increase monthly system availability.',
        'monthly_availability',
        '%',
        99.0,
        99.9,
        99.5
    ),
    (
        'Checkout Processing Time',
        'Reduce average checkout processing time.',
        'checkout_seconds',
        'seconds',
        8.0,
        3.0,
        5.0
    )
) AS data(
    name,
    description,
    metric,
    unit,
    baseline,
    target,
    current_value
)
WHERE product_name = 'Enterprise Commerce Platform';

INSERT INTO initiatives (
    product_id,
    theme_id,
    outcome_id,
    initiative_name,
    description,
    owner_id,
    planned_start,
    planned_end,
    effort_points,
    impact_score,
    confidence_score,
    strategic_alignment,
    status
)
SELECT
    p.product_id,
    t.theme_id,
    o.outcome_id,
    data.name,
    data.description,
    u.user_id,
    data.start_date,
    data.end_date,
    data.effort,
    data.impact,
    data.confidence,
    data.alignment,
    data.status
FROM products p
JOIN (
    VALUES
    (
        'Payment Infrastructure Upgrade',
        'Modernize payment processing infrastructure.',
        'Platform Reliability',
        'Platform Availability',
        'rahul.mehta@example.com',
        DATE '2027-01-01',
        DATE '2027-01-20',
        30,
        9.0,
        0.90,
        1.0,
        'proposed'::initiative_status
    ),
    (
        'Checkout Optimization',
        'Reduce unnecessary checkout processing steps.',
        'Customer Experience',
        'Checkout Processing Time',
        'priya.verma@example.com',
        DATE '2027-01-21',
        DATE '2027-02-10',
        25,
        8.0,
        0.85,
        0.90,
        'proposed'::initiative_status
    ),
    (
        'One-Click Checkout',
        'Introduce simplified repeat-customer checkout.',
        'Customer Experience',
        'Checkout Completion',
        'priya.verma@example.com',
        DATE '2027-02-11',
        DATE '2027-03-10',
        40,
        10.0,
        0.80,
        1.0,
        'proposed'::initiative_status
    ),
    (
        'Product Recommendations',
        'Improve product discovery and relevance.',
        'Revenue Growth',
        'Checkout Completion',
        'priya.verma@example.com',
        DATE '2027-01-15',
        DATE '2027-02-15',
        20,
        8.0,
        0.75,
        0.80,
        'proposed'::initiative_status
    )
) AS data(
    name,
    description,
    theme_name,
    outcome_name,
    owner_email,
    start_date,
    end_date,
    effort,
    impact,
    confidence,
    alignment,
    status
) ON TRUE
JOIN strategic_themes t
    ON t.product_id = p.product_id
   AND t.theme_name = data.theme_name
JOIN outcomes o
    ON o.product_id = p.product_id
   AND o.outcome_name = data.outcome_name
JOIN roadmap_users u
    ON u.email = data.owner_email
WHERE p.product_name = 'Enterprise Commerce Platform';

-- ============================================================
-- 12. DEPENDENCY DATA
-- ============================================================

INSERT INTO initiative_dependencies (
    product_id,
    prerequisite_id,
    dependent_id
)
SELECT
    p.product_id,
    prerequisite.initiative_id,
    dependent.initiative_id
FROM products p
JOIN initiatives prerequisite
    ON prerequisite.product_id = p.product_id
JOIN initiatives dependent
    ON dependent.product_id = p.product_id
WHERE
    (
        prerequisite.initiative_name =
            'Payment Infrastructure Upgrade'
        AND dependent.initiative_name =
            'Checkout Optimization'
    )
    OR
    (
        prerequisite.initiative_name =
            'Checkout Optimization'
        AND dependent.initiative_name =
            'One-Click Checkout'
    )
AND p.product_name = 'Enterprise Commerce Platform';

-- ============================================================
-- 13. GOVERNANCE DECISIONS
-- ============================================================

INSERT INTO initiative_decisions (
    initiative_id,
    reviewer_id,
    decision,
    justification
)
SELECT
    i.initiative_id,
    u.user_id,
    'approve',
    'Strategic alignment and technical feasibility verified.'
FROM initiatives i
JOIN products p ON p.product_id = i.product_id
JOIN roadmap_users u
    ON u.email IN (
        'aarav.sharma@example.com',
        'rahul.mehta@example.com'
    )
WHERE p.product_name = 'Enterprise Commerce Platform'
AND i.initiative_name = 'Payment Infrastructure Upgrade';

-- ============================================================
-- 14. TRANSACTIONAL WORKFLOW
-- ============================================================

-- Approval, planning and execution transitions are atomic.
DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT initiative_id
    INTO v_id
    FROM initiatives
    WHERE initiative_name = 'Payment Infrastructure Upgrade';

    CALL transition_initiative(v_id, 'approved');
    CALL transition_initiative(v_id, 'planned');
    CALL transition_initiative(v_id, 'in_progress');
    CALL transition_initiative(v_id, 'completed');
END;
$$;

-- The first prerequisite is now completed.
-- Approve the second initiative.
INSERT INTO initiative_decisions (
    initiative_id,
    reviewer_id,
    decision,
    justification
)
SELECT
    i.initiative_id,
    u.user_id,
    'approve',
    'Business impact and implementation feasibility verified.'
FROM initiatives i
JOIN roadmap_users u
    ON u.email IN (
        'priya.verma@example.com',
        'rahul.mehta@example.com'
    )
WHERE i.initiative_name = 'Checkout Optimization';

-- ============================================================
-- 15. RETRIEVAL QUERIES
-- ============================================================

-- A. Strategic themes.
SELECT
    theme_name,
    strategic_objective
FROM strategic_themes
ORDER BY theme_name;

-- B. Initiatives ranked by priority.
SELECT *
FROM prioritized_initiatives
ORDER BY priority_score DESC;

-- C. Initiative dependencies.
SELECT
    prerequisite.initiative_name AS prerequisite,
    dependent.initiative_name AS dependent
FROM initiative_dependencies d
JOIN initiatives prerequisite
    ON prerequisite.initiative_id = d.prerequisite_id
JOIN initiatives dependent
    ON dependent.initiative_id = d.dependent_id
ORDER BY prerequisite.initiative_name;

-- D. Outcome performance.
SELECT *
FROM outcome_performance
ORDER BY progress_percent DESC;

-- ============================================================
-- 16. VALIDATION QUERIES
-- ============================================================

-- Initiatives whose dates violate dependency order.
SELECT
    dependent.initiative_name,
    prerequisite.initiative_name
FROM initiative_dependencies d
JOIN initiatives dependent
    ON dependent.initiative_id = d.dependent_id
JOIN initiatives prerequisite
    ON prerequisite.initiative_id = d.prerequisite_id
WHERE prerequisite.planned_end >= dependent.planned_start;

-- Initiatives without enough approvals.
SELECT
    i.initiative_id,
    i.initiative_name,
    COUNT(*) FILTER (
        WHERE d.decision = 'approve'
    ) AS approval_count,
    p.required_approvals
FROM initiatives i
JOIN products p
    ON p.product_id = i.product_id
LEFT JOIN initiative_decisions d
    ON d.initiative_id = i.initiative_id
GROUP BY
    i.initiative_id,
    i.initiative_name,
    p.required_approvals
HAVING COUNT(*) FILTER (
    WHERE d.decision = 'approve'
) < p.required_approvals;

-- ============================================================
-- 17. ELIGIBILITY EVALUATION
-- ============================================================

SELECT
    i.initiative_name,
    evaluation.approval_eligible,
    evaluation.dependency_eligible,
    evaluation.status_eligible,
    evaluation.merge_or_execution_eligible,
    evaluation.reason
FROM initiatives i
CROSS JOIN LATERAL evaluate_initiative(
    i.initiative_id
) evaluation
ORDER BY i.initiative_id;

-- ============================================================
-- 18. CAPACITY REPORT
-- ============================================================

SELECT *
FROM sprint_capacity_report(
    (
        SELECT product_id
        FROM products
        WHERE product_name = 'Enterprise Commerce Platform'
    )
);

-- ============================================================
-- 19. AGGREGATION AND REPORTING
-- ============================================================

-- Initiatives grouped by strategic theme.
SELECT
    theme_name,
    COUNT(*) AS initiative_count,
    SUM(effort_points) AS total_effort,
    ROUND(AVG(priority_score), 3) AS average_priority
FROM prioritized_initiatives
GROUP BY theme_name
ORDER BY initiative_count DESC;

-- Status distribution.
SELECT
    status,
    COUNT(*) AS initiative_count
FROM initiatives
GROUP BY status
ORDER BY status;

-- Outcome measurements over time.
SELECT
    o.outcome_name,
    m.measured_at,
    m.measured_value,
    o.target
FROM outcome_measurements m
JOIN outcomes o
    ON o.outcome_id = m.outcome_id
ORDER BY o.outcome_name, m.measured_at;

-- Initiative status audit trail.
SELECT
    i.initiative_name,
    h.previous_status,
    h.new_status,
    h.changed_at,
    h.change_reason
FROM initiative_status_history h
JOIN initiatives i
    ON i.initiative_id = h.initiative_id
ORDER BY h.changed_at;

-- ============================================================
-- 20. EDGE-CASE DEMONSTRATION
-- ============================================================

-- A. An unknown dependency is rejected by the foreign key.
-- B. A self-dependency is rejected by the CHECK constraint.
-- C. A dependency cycle is rejected by the recursive trigger.
-- D. An initiative outside its planning period is rejected.
-- E. An initiative with an invalid effort or score is rejected.
-- F. Execution is blocked until approval and dependencies pass.

-- Example of an intentionally rejected transition.
DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT initiative_id
    INTO v_id
    FROM initiatives
    WHERE initiative_name = 'One-Click Checkout';

    BEGIN
        CALL transition_initiative(v_id, 'in_progress');
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected workflow rejection: %', SQLERRM;
    END;
END;
$$;

COMMIT;
