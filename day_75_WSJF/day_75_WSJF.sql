/*
    WEIGHTED SHORTEST JOB FIRST (WSJF)
    PostgreSQL 14+

    Cost of Delay =
        Business Value
        + Time Criticality
        + Risk Reduction

    WSJF = Cost of Delay / Job Size

    Implements:
    - Portfolio and team management
    - Work-item scoring
    - Dependency management
    - Work-item lifecycle
    - WSJF calculations
    - Prioritization policies
    - Capacity planning
    - Scenario evaluation
    - Audit history
    - Validation triggers
    - Reporting views
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS wsjf;

SET search_path TO wsjf, public;

-- =========================================================
-- 1. DOMAIN TYPES
-- =========================================================

CREATE TYPE work_status AS ENUM (
    'BACKLOG',
    'READY',
    'IN_PROGRESS',
    'BLOCKED',
    'COMPLETED'
);

CREATE TYPE audit_action AS ENUM (
    'CREATED',
    'UPDATED',
    'STATUS_CHANGED',
    'SCORED',
    'SCHEDULED'
);

-- =========================================================
-- 2. ORGANIZATIONAL ENTITIES
-- =========================================================

CREATE TABLE teams (
    team_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE team_members (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(team_id),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(40) NOT NULL CHECK (
        role IN (
            'PRODUCT_OWNER',
            'PROJECT_MANAGER',
            'DEVELOPER',
            'ARCHITECT',
            'SECURITY',
            'ANALYST',
            'ADMIN'
        )
    ),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE portfolios (
    portfolio_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    portfolio_name VARCHAR(150) NOT NULL UNIQUE,
    business_owner BIGINT REFERENCES team_members(member_id),
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

-- =========================================================
-- 3. PRIORITIZATION POLICY
-- =========================================================

CREATE TABLE prioritization_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name VARCHAR(150) NOT NULL UNIQUE,

    minimum_business_value NUMERIC(12, 2)
        NOT NULL DEFAULT 0 CHECK (minimum_business_value >= 0),

    minimum_time_criticality NUMERIC(12, 2)
        NOT NULL DEFAULT 0 CHECK (minimum_time_criticality >= 0),

    minimum_risk_reduction NUMERIC(12, 2)
        NOT NULL DEFAULT 0 CHECK (minimum_risk_reduction >= 0),

    maximum_job_size NUMERIC(12, 2)
        NOT NULL CHECK (maximum_job_size > 0),

    require_ready_status BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 4. WORK ITEMS
-- =========================================================

CREATE TABLE work_items (
    work_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    external_key VARCHAR(40) NOT NULL UNIQUE,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    team_id BIGINT NOT NULL
        REFERENCES teams(team_id),

    owner_id BIGINT
        REFERENCES team_members(member_id),

    title VARCHAR(250) NOT NULL,
    description TEXT,

    business_value NUMERIC(12, 2) NOT NULL
        CHECK (business_value >= 0),

    time_criticality NUMERIC(12, 2) NOT NULL
        CHECK (time_criticality >= 0),

    risk_reduction NUMERIC(12, 2) NOT NULL
        CHECK (risk_reduction >= 0),

    job_size NUMERIC(12, 2) NOT NULL
        CHECK (job_size > 0),

    status work_status NOT NULL DEFAULT 'BACKLOG',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),

    CONSTRAINT nonempty_work_title
        CHECK (LENGTH(BTRIM(title)) > 0)
);

-- =========================================================
-- 5. DEPENDENCY GRAPH
-- =========================================================

CREATE TABLE work_item_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id) ON DELETE CASCADE,

    depends_on_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id) ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_dependency
        UNIQUE (work_item_id, depends_on_id),

    CONSTRAINT no_self_dependency
        CHECK (work_item_id <> depends_on_id)
);

CREATE INDEX idx_dependencies_work_item
    ON work_item_dependencies(work_item_id);

CREATE INDEX idx_dependencies_parent
    ON work_item_dependencies(depends_on_id);

-- =========================================================
-- 6. SCORE CALCULATION
-- =========================================================

CREATE OR REPLACE FUNCTION calculate_cost_of_delay(
    p_business_value NUMERIC,
    p_time_criticality NUMERIC,
    p_risk_reduction NUMERIC
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT
        p_business_value
        + p_time_criticality
        + p_risk_reduction;
$$;

CREATE OR REPLACE FUNCTION calculate_wsjf(
    p_business_value NUMERIC,
    p_time_criticality NUMERIC,
    p_risk_reduction NUMERIC,
    p_job_size NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_job_size <= 0 THEN
        RAISE EXCEPTION 'Job size must be greater than zero';
    END IF;

    IF p_business_value < 0
       OR p_time_criticality < 0
       OR p_risk_reduction < 0 THEN
        RAISE EXCEPTION 'Cost of Delay components cannot be negative';
    END IF;

    RETURN (
        p_business_value
        + p_time_criticality
        + p_risk_reduction
    ) / p_job_size;
END;
$$;

-- =========================================================
-- 7. AUTOMATIC SCORE AND UPDATE MANAGEMENT
-- =========================================================

CREATE OR REPLACE FUNCTION update_work_item_metadata()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();

    IF TG_OP = 'UPDATE' THEN
        NEW.version := OLD.version + 1;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_work_item_metadata
BEFORE UPDATE ON work_items
FOR EACH ROW
EXECUTE FUNCTION update_work_item_metadata();

-- =========================================================
-- 8. DEPENDENCY CYCLE PROTECTION
-- =========================================================

CREATE OR REPLACE FUNCTION prevent_dependency_cycles()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    IF NEW.work_item_id = NEW.depends_on_id THEN
        RAISE EXCEPTION 'Self-dependency is prohibited';
    END IF;

    WITH RECURSIVE dependency_path AS (
        SELECT
            NEW.depends_on_id AS current_id,
            ARRAY[NEW.depends_on_id]::BIGINT[] AS visited

        UNION ALL

        SELECT
            d.depends_on_id,
            dp.visited || d.depends_on_id
        FROM dependency_path dp
        JOIN work_item_dependencies d
            ON d.work_item_id = dp.current_id
        WHERE NOT d.depends_on_id = ANY(dp.visited)
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE current_id = NEW.work_item_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION
            'Dependency cycle detected for work item %',
            NEW.work_item_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_dependency_cycle
BEFORE INSERT OR UPDATE ON work_item_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_dependency_cycles();

-- =========================================================
-- 9. DEPENDENCY READINESS
-- =========================================================

CREATE OR REPLACE FUNCTION are_dependencies_complete(
    p_work_item_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM work_item_dependencies d
        JOIN work_items parent
            ON parent.work_item_id = d.depends_on_id
        WHERE d.work_item_id = p_work_item_id
          AND parent.status <> 'COMPLETED'
    );
$$;

CREATE OR REPLACE FUNCTION validate_ready_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'READY'
       AND NOT are_dependencies_complete(NEW.work_item_id) THEN

        RAISE EXCEPTION
            'Work item % has incomplete dependencies',
            NEW.external_key;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_ready_transition
BEFORE INSERT OR UPDATE OF status ON work_items
FOR EACH ROW
EXECUTE FUNCTION validate_ready_transition();

-- =========================================================
-- 10. REVIEWABLE PRIORITIZATION RESULTS
-- =========================================================

CREATE VIEW v_wsjf_ranking AS
SELECT
    w.work_item_id,
    w.external_key,
    w.title,
    t.team_name,
    p.portfolio_name,
    w.status,

    w.business_value,
    w.time_criticality,
    w.risk_reduction,
    w.job_size,

    calculate_cost_of_delay(
        w.business_value,
        w.time_criticality,
        w.risk_reduction
    ) AS cost_of_delay,

    ROUND(
        calculate_wsjf(
            w.business_value,
            w.time_criticality,
            w.risk_reduction,
            w.job_size
        ),
        4
    ) AS wsjf,

    w.created_at,
    w.updated_at

FROM work_items w
JOIN teams t
    ON t.team_id = w.team_id
JOIN portfolios p
    ON p.portfolio_id = w.portfolio_id;

CREATE INDEX idx_work_items_status_team
    ON work_items(status, team_id);

CREATE INDEX idx_work_items_portfolio
    ON work_items(portfolio_id);

-- =========================================================
-- 11. AUDIT LOG
-- =========================================================

CREATE TABLE audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    work_item_id BIGINT REFERENCES work_items(work_item_id),

    action audit_action NOT NULL,
    actor_id BIGINT REFERENCES team_members(member_id),

    description TEXT NOT NULL,

    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_work_item_time
    ON audit_log(work_item_id, event_timestamp DESC);

-- =========================================================
-- 12. CAPACITY PLANNING
-- =========================================================

CREATE TABLE capacity_plans (
    capacity_plan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    team_id BIGINT NOT NULL
        REFERENCES teams(team_id),

    plan_name VARCHAR(150) NOT NULL,

    available_capacity NUMERIC(12, 2) NOT NULL
        CHECK (available_capacity >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (portfolio_id, team_id, plan_name)
);

CREATE TABLE capacity_plan_items (
    capacity_plan_id BIGINT NOT NULL
        REFERENCES capacity_plans(capacity_plan_id)
        ON DELETE CASCADE,

    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id),

    allocated_size NUMERIC(12, 2) NOT NULL
        CHECK (allocated_size > 0),

    selection_order INTEGER NOT NULL
        CHECK (selection_order > 0),

    PRIMARY KEY (capacity_plan_id, work_item_id),

    UNIQUE (capacity_plan_id, selection_order)
);

-- =========================================================
-- 13. SCENARIO ANALYSIS
-- =========================================================

CREATE TABLE scoring_scenarios (
    scenario_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id),

    scenario_name VARCHAR(150) NOT NULL,

    business_value NUMERIC(12, 2) NOT NULL
        CHECK (business_value >= 0),

    time_criticality NUMERIC(12, 2) NOT NULL
        CHECK (time_criticality >= 0),

    risk_reduction NUMERIC(12, 2) NOT NULL
        CHECK (risk_reduction >= 0),

    job_size NUMERIC(12, 2) NOT NULL
        CHECK (job_size > 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE VIEW v_scenario_comparison AS
SELECT
    s.scenario_id,
    s.scenario_name,
    w.external_key,

    ROUND(
        calculate_wsjf(
            w.business_value,
            w.time_criticality,
            w.risk_reduction,
            w.job_size
        ),
        4
    ) AS original_wsjf,

    ROUND(
        calculate_wsjf(
            s.business_value,
            s.time_criticality,
            s.risk_reduction,
            s.job_size
        ),
        4
    ) AS scenario_wsjf

FROM scoring_scenarios s
JOIN work_items w
    ON w.work_item_id = s.work_item_id;

-- =========================================================
-- 14. POLICY ELIGIBILITY
-- =========================================================

CREATE OR REPLACE FUNCTION evaluate_policy(
    p_work_item_id BIGINT,
    p_policy_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    item work_items%ROWTYPE;
    policy prioritization_policies%ROWTYPE;
    reasons TEXT[] := ARRAY[]::TEXT[];
BEGIN
    SELECT *
    INTO item
    FROM work_items
    WHERE work_item_id = p_work_item_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown work item: %', p_work_item_id;
    END IF;

    SELECT *
    INTO policy
    FROM prioritization_policies
    WHERE policy_id = p_policy_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active policy not found: %', p_policy_id;
    END IF;

    IF policy.require_ready_status
       AND item.status <> 'READY' THEN
        reasons := array_append(
            reasons,
            'Work item is not READY'
        );
    END IF;

    IF item.business_value < policy.minimum_business_value THEN
        reasons := array_append(
            reasons,
            'Business value below minimum'
        );
    END IF;

    IF item.time_criticality < policy.minimum_time_criticality THEN
        reasons := array_append(
            reasons,
            'Time criticality below minimum'
        );
    END IF;

    IF item.risk_reduction < policy.minimum_risk_reduction THEN
        reasons := array_append(
            reasons,
            'Risk reduction below minimum'
        );
    END IF;

    IF item.job_size > policy.maximum_job_size THEN
        reasons := array_append(
            reasons,
            'Job size exceeds maximum'
        );
    END IF;

    RETURN QUERY
    SELECT
        cardinality(reasons) = 0,
        CASE
            WHEN cardinality(reasons) = 0 THEN 'Eligible'
            ELSE array_to_string(reasons, '; ')
        END;
END;
$$;

-- =========================================================
-- 15. CAPACITY PLAN GENERATION PROCEDURE
-- =========================================================

CREATE OR REPLACE PROCEDURE generate_capacity_plan(
    p_capacity_plan_id BIGINT,
    p_policy_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    plan capacity_plans%ROWTYPE;
    candidate RECORD;
    remaining NUMERIC(12, 2);
    selected_count INTEGER := 0;
BEGIN
    -- Serialize planning operations for the same capacity plan.
    SELECT *
    INTO plan
    FROM capacity_plans
    WHERE capacity_plan_id = p_capacity_plan_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Capacity plan does not exist';
    END IF;

    remaining := plan.available_capacity;

    DELETE FROM capacity_plan_items
    WHERE capacity_plan_id = p_capacity_plan_id;

    FOR candidate IN
        SELECT
            r.work_item_id,
            r.external_key,
            r.job_size,
            r.wsjf
        FROM v_wsjf_ranking r
        JOIN work_items w
            ON w.work_item_id = r.work_item_id
        WHERE w.portfolio_id = plan.portfolio_id
          AND w.team_id = plan.team_id
          AND w.status = 'READY'
          AND EXISTS (
              SELECT 1
              FROM evaluate_policy(
                  r.work_item_id,
                  p_policy_id
              ) e
              WHERE e.eligible = TRUE
          )
        ORDER BY
            r.wsjf DESC,
            r.cost_of_delay DESC,
            r.job_size ASC,
            r.work_item_id ASC
    LOOP
        IF candidate.job_size > remaining THEN
            CONTINUE;
        END IF;

        IF NOT are_dependencies_complete(candidate.work_item_id)
           AND NOT EXISTS (
               SELECT 1
               FROM capacity_plan_items selected
               JOIN work_item_dependencies d
                   ON d.work_item_id = candidate.work_item_id
                  AND d.depends_on_id = selected.work_item_id
               WHERE selected.capacity_plan_id = p_capacity_plan_id
           ) THEN
            CONTINUE;
        END IF;

        -- The plan is an ordered selection proposal.
        -- Actual execution remains a separate workflow.
        selected_count := selected_count + 1;

        INSERT INTO capacity_plan_items (
            capacity_plan_id,
            work_item_id,
            allocated_size,
            selection_order
        )
        VALUES (
            p_capacity_plan_id,
            candidate.work_item_id,
            candidate.job_size,
            selected_count
        );

        remaining := remaining - candidate.job_size;

        INSERT INTO audit_log (
            work_item_id,
            action,
            description
        )
        VALUES (
            candidate.work_item_id,
            'SCHEDULED',
            'Selected for capacity plan ' || p_capacity_plan_id
        );
    END LOOP;

END;
$$;

-- =========================================================
-- 16. REPORTING VIEW
-- =========================================================

CREATE VIEW v_portfolio_wsjf_report AS
SELECT
    p.portfolio_name,
    t.team_name,

    COUNT(w.work_item_id) AS total_items,

    COUNT(*) FILTER (
        WHERE w.status = 'READY'
    ) AS ready_items,

    COUNT(*) FILTER (
        WHERE w.status = 'BLOCKED'
    ) AS blocked_items,

    COUNT(*) FILTER (
        WHERE w.status = 'COMPLETED'
    ) AS completed_items,

    ROUND(AVG(r.wsjf), 4) AS average_wsjf,

    ROUND(MAX(r.wsjf), 4) AS highest_wsjf,

    ROUND(SUM(w.job_size), 2) AS total_estimated_size

FROM portfolios p
JOIN work_items w
    ON w.portfolio_id = p.portfolio_id
JOIN teams t
    ON t.team_id = w.team_id
JOIN v_wsjf_ranking r
    ON r.work_item_id = w.work_item_id

GROUP BY p.portfolio_name, t.team_name;

-- =========================================================
-- 17. SAMPLE DATA
-- =========================================================

INSERT INTO teams (team_name, description)
VALUES
    ('Platform Engineering', 'Core infrastructure and platform'),
    ('Security Engineering', 'Security and risk management'),
    ('Product Engineering', 'Customer-facing product delivery'),
    ('Quality Engineering', 'Testing and reliability');

INSERT INTO team_members (
    team_id, full_name, email, role
)
SELECT
    t.team_id,
    x.full_name,
    x.email,
    x.role
FROM (
    VALUES
    ('Platform Engineering', 'Aarav Sharma',
     'aarav@example.org', 'ARCHITECT'),
    ('Security Engineering', 'Mira Kapoor',
     'mira@example.org', 'SECURITY'),
    ('Product Engineering', 'Rohan Mehta',
     'rohan@example.org', 'PRODUCT_OWNER'),
    ('Quality Engineering', 'Ananya Rao',
     'ananya@example.org', 'DEVELOPER')
) AS x(team_name, full_name, email, role)
JOIN teams t ON t.team_name = x.team_name;

INSERT INTO portfolios (portfolio_name, business_owner)
SELECT
    'Digital Transformation',
    member_id
FROM team_members
WHERE email = 'rohan@example.org';

INSERT INTO prioritization_policies (
    policy_name,
    minimum_business_value,
    minimum_time_criticality,
    minimum_risk_reduction,
    maximum_job_size
)
VALUES (
    'Enterprise Standard WSJF',
    3,
    0,
    0,
    20
);

INSERT INTO work_items (
    external_key,
    portfolio_id,
    team_id,
    owner_id,
    title,
    business_value,
    time_criticality,
    risk_reduction,
    job_size,
    status
)
SELECT
    x.external_key,
    p.portfolio_id,
    t.team_id,
    m.member_id,
    x.title,
    x.business_value,
    x.time_criticality,
    x.risk_reduction,
    x.job_size,
    x.status::work_status
FROM (
    VALUES
    (
        'WSJF-401',
        'Security vulnerability remediation',
        'Security Engineering',
        'mira@example.org',
        9::NUMERIC, 10::NUMERIC, 10::NUMERIC, 3::NUMERIC,
        'READY'
    ),
    (
        'WSJF-402',
        'Payment gateway modernization',
        'Product Engineering',
        'rohan@example.org',
        9::NUMERIC, 10::NUMERIC, 8::NUMERIC, 5::NUMERIC,
        'READY'
    ),
    (
        'WSJF-403',
        'Database migration foundation',
        'Platform Engineering',
        'aarav@example.org',
        7::NUMERIC, 6::NUMERIC, 9::NUMERIC, 5::NUMERIC,
        'READY'
    ),
    (
        'WSJF-404',
        'Automated regression testing',
        'Quality Engineering',
        'ananya@example.org',
        6::NUMERIC, 7::NUMERIC, 8::NUMERIC, 3::NUMERIC,
        'BACKLOG'
    ),
    (
        'WSJF-405',
        'Customer analytics dashboard',
        'Product Engineering',
        'rohan@example.org',
        8::NUMERIC, 5::NUMERIC, 3::NUMERIC, 8::NUMERIC,
        'READY'
    ),
    (
        'WSJF-406',
        'Infrastructure monitoring',
        'Platform Engineering',
        'aarav@example.org',
        7::NUMERIC, 8::NUMERIC, 7::NUMERIC, 4::NUMERIC,
        'READY'
    ),
    (
        'WSJF-407',
        'Legacy reporting optimization',
        'Product Engineering',
        'rohan@example.org',
        2::NUMERIC, 2::NUMERIC, 1::NUMERIC, 6::NUMERIC,
        'BLOCKED'
    )
) AS x(
    external_key,
    title,
    team_name,
    owner_email,
    business_value,
    time_criticality,
    risk_reduction,
    job_size,
    status
)
JOIN portfolios p
    ON p.portfolio_name = 'Digital Transformation'
JOIN teams t
    ON t.team_name = x.team_name
JOIN team_members m
    ON m.email = x.owner_email;

-- Dependency: regression testing depends on database migration.
INSERT INTO work_item_dependencies (
    work_item_id,
    depends_on_id
)
SELECT
    child.work_item_id,
    parent.work_item_id
FROM work_items child
JOIN work_items parent
    ON parent.external_key = 'WSJF-403'
WHERE child.external_key = 'WSJF-404';

INSERT INTO capacity_plans (
    portfolio_id,
    team_id,
    plan_name,
    available_capacity
)
SELECT
    p.portfolio_id,
    t.team_id,
    'Platform Engineering Sprint 01',
    12
FROM portfolios p
JOIN teams t
    ON t.team_name = 'Platform Engineering'
WHERE p.portfolio_name = 'Digital Transformation';

-- =========================================================
-- 18. SAMPLE SCENARIO
-- =========================================================

INSERT INTO scoring_scenarios (
    work_item_id,
    scenario_name,
    business_value,
    time_criticality,
    risk_reduction,
    job_size
)
SELECT
    work_item_id,
    'Increased customer demand',
    business_value + 3,
    time_criticality + 2,
    risk_reduction,
    job_size
FROM work_items
WHERE external_key = 'WSJF-405';

-- =========================================================
-- 19. INITIAL AUDIT EVENTS
-- =========================================================

INSERT INTO audit_log (
    work_item_id,
    action,
    description
)
SELECT
    work_item_id,
    'CREATED',
    'Initial work item registration'
FROM work_items;

COMMIT;

-- =========================================================
-- 20. RETRIEVAL QUERIES
-- =========================================================

-- Highest-priority eligible items.
SELECT
    external_key,
    title,
    cost_of_delay,
    job_size,
    wsjf
FROM v_wsjf_ranking
WHERE status = 'READY'
ORDER BY wsjf DESC, cost_of_delay DESC, job_size ASC;

-- Individual item scoring.
SELECT
    external_key,
    calculate_cost_of_delay(
        business_value,
        time_criticality,
        risk_reduction
    ) AS cost_of_delay,
    calculate_wsjf(
        business_value,
        time_criticality,
        risk_reduction,
        job_size
    ) AS wsjf
FROM work_items
WHERE external_key = 'WSJF-401';

-- =========================================================
-- 21. VALIDATION QUERIES
-- =========================================================

-- Verify dependency readiness.
SELECT
    w.external_key,
    w.status,
    are_dependencies_complete(w.work_item_id)
        AS dependencies_complete
FROM work_items w;

-- Evaluate policy eligibility.
SELECT
    w.external_key,
    result.eligible,
    result.reason
FROM work_items w
CROSS JOIN LATERAL evaluate_policy(
    w.work_item_id,
    (
        SELECT policy_id
        FROM prioritization_policies
        WHERE policy_name = 'Enterprise Standard WSJF'
    )
) AS result
ORDER BY w.external_key;

-- =========================================================
-- 22. AGGREGATION AND REPORTING
-- =========================================================

SELECT *
FROM v_portfolio_wsjf_report
ORDER BY portfolio_name, team_name;

-- Compare average WSJF by team.
SELECT
    team_name,
    COUNT(*) AS item_count,
    ROUND(AVG(wsjf), 4) AS average_wsjf,
    ROUND(MAX(wsjf), 4) AS maximum_wsjf,
    ROUND(SUM(job_size), 2) AS total_job_size
FROM v_wsjf_ranking
GROUP BY team_name
ORDER BY average_wsjf DESC;

-- =========================================================
-- 23. SCENARIO EVALUATION
-- =========================================================

SELECT
    scenario_name,
    external_key,
    original_wsjf,
    scenario_wsjf,
    ROUND(
        scenario_wsjf - original_wsjf,
        4
    ) AS score_difference
FROM v_scenario_comparison;

-- =========================================================
-- 24. WORKFLOW PROCESSING
-- =========================================================

-- Generate a capacity plan atomically.
BEGIN;

CALL generate_capacity_plan(
    (
        SELECT capacity_plan_id
        FROM capacity_plans
        WHERE plan_name = 'Platform Engineering Sprint 01'
    ),
    (
        SELECT policy_id
        FROM prioritization_policies
        WHERE policy_name = 'Enterprise Standard WSJF'
    )
);

COMMIT;

-- Inspect the generated schedule.
SELECT
    cp.plan_name,
    cpi.selection_order,
    w.external_key,
    w.title,
    cpi.allocated_size,
    r.wsjf
FROM capacity_plan_items cpi
JOIN capacity_plans cp
    ON cp.capacity_plan_id = cpi.capacity_plan_id
JOIN work_items w
    ON w.work_item_id = cpi.work_item_id
JOIN v_wsjf_ranking r
    ON r.work_item_id = w.work_item_id
ORDER BY cpi.selection_order;

-- =========================================================
-- 25. CAPACITY UTILIZATION
-- =========================================================

SELECT
    cp.plan_name,
    cp.available_capacity,
    COALESCE(SUM(cpi.allocated_size), 0) AS allocated_capacity,

    cp.available_capacity
        - COALESCE(SUM(cpi.allocated_size), 0)
        AS remaining_capacity,

    ROUND(
        100 * COALESCE(SUM(cpi.allocated_size), 0)
        / NULLIF(cp.available_capacity, 0),
        2
    ) AS utilization_percentage

FROM capacity_plans cp
LEFT JOIN capacity_plan_items cpi
    ON cpi.capacity_plan_id = cp.capacity_plan_id

GROUP BY cp.capacity_plan_id, cp.plan_name,
         cp.available_capacity;

-- =========================================================
-- 26. AUDIT RETRIEVAL
-- =========================================================

SELECT
    w.external_key,
    a.action,
    a.description,
    a.event_timestamp
FROM audit_log a
JOIN work_items w
    ON w.work_item_id = a.work_item_id
ORDER BY a.event_timestamp DESC;

-- =========================================================
-- 27. FAILURE CASES
-- =========================================================

-- These statements are intentionally not executed because they
-- must fail:
--
-- INSERT INTO work_items (...) VALUES (..., 0, ...);
-- Violates the positive job-size constraint.
--
-- INSERT INTO work_item_dependencies
-- (work_item_id, depends_on_id)
-- VALUES (10, 10);
-- Violates the self-dependency constraint.
--
-- Adding a dependency that creates a cycle is rejected by
-- trg_dependency_cycle.
--
-- Moving a dependent item to READY while its prerequisite is
-- incomplete is rejected by trg_validate_ready_transition.
--
-- A transaction containing a failed statement must be rolled
-- back before the connection can continue.
