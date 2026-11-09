/*
 * PRIORITIZATION FUNDAMENTALS
 * PostgreSQL 15+
 *
 * Relational portfolio prioritization and decision governance.
 *
 * Includes:
 * - Organizations and portfolios
 * - Initiatives and dependencies
 * - Scoring criteria and framework configuration
 * - RICE, WSJF and weighted scoring
 * - MoSCoW classification
 * - Resource constraints
 * - Mandatory initiatives
 * - Allocation decisions
 * - Opportunity-cost reporting
 * - Audit history
 * - Validation triggers
 * - Transaction-safe allocation procedures
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS prioritization;

SET search_path TO prioritization, public;


-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE initiative_priority AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);

CREATE TYPE moscow_classification AS ENUM (
    'must',
    'should',
    'could',
    'wont'
);

CREATE TYPE initiative_status AS ENUM (
    'proposed',
    'evaluated',
    'selected',
    'deferred',
    'rejected'
);

CREATE TYPE scoring_framework AS ENUM (
    'rice',
    'wsjf',
    'weighted'
);


-- ============================================================
-- 2. ORGANIZATIONAL MODEL
-- ============================================================

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE portfolios (
    portfolio_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    portfolio_name VARCHAR(150) NOT NULL,

    available_effort NUMERIC(12,2) NOT NULL
        CHECK (available_effort >= 0),

    available_budget NUMERIC(14,2) NOT NULL
        CHECK (available_budget >= 0),

    minimum_confidence NUMERIC(5,4) NOT NULL DEFAULT 0
        CHECK (minimum_confidence BETWEEN 0 AND 1),

    require_strategic_alignment BOOLEAN NOT NULL DEFAULT TRUE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (organization_id, portfolio_name)
);


-- ============================================================
-- 3. INITIATIVE DOMAIN
-- ============================================================

CREATE TABLE initiatives (
    initiative_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    initiative_code VARCHAR(30) NOT NULL,

    initiative_name VARCHAR(200) NOT NULL,

    description TEXT,

    priority initiative_priority NOT NULL DEFAULT 'medium',

    classification moscow_classification NOT NULL DEFAULT 'could',

    status initiative_status NOT NULL DEFAULT 'proposed',

    reach NUMERIC(14,2) NOT NULL DEFAULT 0
        CHECK (reach >= 0),

    impact NUMERIC(5,2) NOT NULL
        CHECK (impact BETWEEN 0 AND 10),

    confidence NUMERIC(5,4) NOT NULL
        CHECK (confidence BETWEEN 0 AND 1),

    effort NUMERIC(12,2) NOT NULL
        CHECK (effort > 0),

    business_value NUMERIC(5,2) NOT NULL
        CHECK (business_value BETWEEN 0 AND 10),

    urgency NUMERIC(5,2) NOT NULL
        CHECK (urgency BETWEEN 0 AND 10),

    risk_reduction NUMERIC(5,2) NOT NULL
        CHECK (risk_reduction BETWEEN 0 AND 10),

    strategic_alignment NUMERIC(5,2) NOT NULL
        CHECK (strategic_alignment BETWEEN 0 AND 10),

    estimated_cost NUMERIC(14,2) NOT NULL
        CHECK (estimated_cost >= 0),

    mandatory BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (portfolio_id, initiative_code),

    CHECK (
        NOT (mandatory AND classification = 'wont')
    )
);


-- ============================================================
-- 4. DEPENDENCY RELATIONSHIPS
-- ============================================================

CREATE TABLE initiative_dependencies (
    initiative_id BIGINT NOT NULL
        REFERENCES initiatives(initiative_id)
        ON DELETE CASCADE,

    dependency_id BIGINT NOT NULL
        REFERENCES initiatives(initiative_id)
        ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (initiative_id, dependency_id),

    CHECK (initiative_id <> dependency_id)
);


-- ============================================================
-- 5. FRAMEWORK CONFIGURATION
-- ============================================================

CREATE TABLE scoring_configurations (
    configuration_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    framework scoring_framework NOT NULL,

    criterion_weights JSONB NOT NULL DEFAULT
        '{"business_value":0.30,
          "strategic_alignment":0.30,
          "urgency":0.15,
          "risk_reduction":0.15,
          "confidence":0.10}'::JSONB,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (portfolio_id, framework)
);


-- ============================================================
-- 6. ALLOCATION RUNS AND DECISION HISTORY
-- ============================================================

CREATE TABLE allocation_runs (
    allocation_run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    framework scoring_framework NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'completed'
        CHECK (status IN ('running', 'completed', 'failed')),

    effort_consumed NUMERIC(12,2) NOT NULL DEFAULT 0,

    budget_consumed NUMERIC(14,2) NOT NULL DEFAULT 0,

    business_value NUMERIC(14,2) NOT NULL DEFAULT 0,

    opportunity_cost NUMERIC(14,4) NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ
);

CREATE TABLE initiative_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    allocation_run_id BIGINT NOT NULL
        REFERENCES allocation_runs(allocation_run_id)
        ON DELETE CASCADE,

    initiative_id BIGINT NOT NULL
        REFERENCES initiatives(initiative_id),

    framework scoring_framework NOT NULL,

    calculated_score NUMERIC(18,4) NOT NULL,

    decision_status initiative_status NOT NULL,

    explanation TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (allocation_run_id, initiative_id)
);


-- ============================================================
-- 7. DECISION CRITERIA AND FRAMEWORK SCORING
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_initiative_score(
    p_initiative_id BIGINT,
    p_framework scoring_framework
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_item initiatives%ROWTYPE;
    v_score NUMERIC;
BEGIN
    SELECT *
    INTO v_item
    FROM initiatives
    WHERE initiative_id = p_initiative_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Initiative % does not exist',
            p_initiative_id;
    END IF;

    CASE p_framework

        WHEN 'rice' THEN
            v_score :=
                v_item.reach *
                v_item.impact *
                v_item.confidence /
                v_item.effort;

        WHEN 'wsjf' THEN
            v_score :=
                (
                    v_item.business_value +
                    v_item.urgency +
                    v_item.risk_reduction
                ) / v_item.effort;

        WHEN 'weighted' THEN
            v_score :=
                v_item.business_value * 0.30 +
                v_item.strategic_alignment * 0.30 +
                v_item.urgency * 0.15 +
                v_item.risk_reduction * 0.15 +
                v_item.confidence * 10 * 0.10;

    END CASE;

    RETURN ROUND(v_score, 4);
END;
$$;


-- ============================================================
-- 8. DEPENDENCY CYCLE VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_dependency_graph()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cycle BOOLEAN;
    v_source_portfolio BIGINT;
    v_target_portfolio BIGINT;
BEGIN
    SELECT portfolio_id
    INTO v_source_portfolio
    FROM initiatives
    WHERE initiative_id = NEW.initiative_id;

    SELECT portfolio_id
    INTO v_target_portfolio
    FROM initiatives
    WHERE initiative_id = NEW.dependency_id;

    IF v_source_portfolio <> v_target_portfolio THEN
        RAISE EXCEPTION
            'Dependencies must belong to the same portfolio.';
    END IF;

    WITH RECURSIVE dependency_path(node_id) AS (
        SELECT NEW.dependency_id

        UNION

        SELECT d.dependency_id
        FROM initiative_dependencies d
        JOIN dependency_path p
          ON d.initiative_id = p.node_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE node_id = NEW.initiative_id
    )
    INTO v_cycle;

    IF v_cycle THEN
        RAISE EXCEPTION
            'Circular initiative dependency detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency
BEFORE INSERT OR UPDATE
ON initiative_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_graph();


-- ============================================================
-- 9. AUDIT UPDATE TIMESTAMPS
-- ============================================================

CREATE OR REPLACE FUNCTION update_initiative_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_initiative_timestamp
BEFORE UPDATE ON initiatives
FOR EACH ROW
EXECUTE FUNCTION update_initiative_timestamp();


-- ============================================================
-- 10. PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_initiatives_portfolio_status
ON initiatives(portfolio_id, status);

CREATE INDEX idx_initiatives_priority
ON initiatives(portfolio_id, priority);

CREATE INDEX idx_initiatives_mandatory
ON initiatives(portfolio_id, mandatory)
WHERE mandatory = TRUE;

CREATE INDEX idx_dependencies_target
ON initiative_dependencies(dependency_id);

CREATE INDEX idx_allocation_runs_portfolio
ON allocation_runs(portfolio_id, created_at DESC);

CREATE INDEX idx_decisions_run_status
ON initiative_decisions(allocation_run_id, decision_status);

CREATE INDEX idx_initiatives_attributes
ON initiatives(portfolio_id, business_value DESC, strategic_alignment DESC);


-- ============================================================
-- 11. PORTFOLIO RANKING VIEW
-- ============================================================

CREATE OR REPLACE VIEW initiative_ranking AS
SELECT
    i.initiative_id,
    i.portfolio_id,
    i.initiative_code,
    i.initiative_name,
    i.priority,
    i.classification,
    i.mandatory,
    i.effort,
    i.estimated_cost,

    calculate_initiative_score(
        i.initiative_id,
        'rice'
    ) AS rice_score,

    calculate_initiative_score(
        i.initiative_id,
        'wsjf'
    ) AS wsjf_score,

    calculate_initiative_score(
        i.initiative_id,
        'weighted'
    ) AS weighted_score

FROM initiatives i;


-- ============================================================
-- 12. DEPENDENCY-AWARE ALLOCATION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE allocate_portfolio(
    IN p_portfolio_id BIGINT,
    IN p_framework scoring_framework,
    OUT p_allocation_run_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_portfolio portfolios%ROWTYPE;
    v_item RECORD;
    v_candidate RECORD;

    v_closure BIGINT[];
    v_new_items BIGINT[];

    v_additional_effort NUMERIC;
    v_additional_budget NUMERIC;

    v_effort_used NUMERIC := 0;
    v_budget_used NUMERIC := 0;
    v_business_value NUMERIC := 0;
    v_opportunity_cost NUMERIC := 0;

    v_selected BIGINT[] := ARRAY[]::BIGINT[];
    v_processed BIGINT[] := ARRAY[]::BIGINT[];

    v_policy_failure BOOLEAN;
    v_mandatory_count INTEGER;
    v_remaining_count INTEGER;
BEGIN
    -- Lock the portfolio row to serialize concurrent allocation runs.
    SELECT *
    INTO v_portfolio
    FROM portfolios
    WHERE portfolio_id = p_portfolio_id
      AND active = TRUE
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Active portfolio % does not exist',
            p_portfolio_id;
    END IF;

    SELECT COUNT(*)
    INTO v_remaining_count
    FROM initiatives
    WHERE portfolio_id = p_portfolio_id;

    IF v_remaining_count = 0 THEN
        RAISE EXCEPTION 'Portfolio has no initiatives.';
    END IF;

    INSERT INTO allocation_runs (
        portfolio_id,
        framework,
        status
    )
    VALUES (
        p_portfolio_id,
        p_framework,
        'running'
    )
    RETURNING allocation_run_id
    INTO p_allocation_run_id;

    -- Mandatory initiatives are processed first.
    FOR v_item IN
        SELECT
            initiative_id,
            initiative_code
        FROM initiatives
        WHERE portfolio_id = p_portfolio_id
          AND mandatory = TRUE
        ORDER BY initiative_id
    LOOP

        WITH RECURSIVE dependency_closure(id) AS (
            SELECT v_item.initiative_id

            UNION

            SELECT d.dependency_id
            FROM initiative_dependencies d
            JOIN dependency_closure c
              ON d.initiative_id = c.id
        )
        SELECT ARRAY_AGG(id)
        INTO v_closure
        FROM dependency_closure;

        SELECT COALESCE(
            ARRAY_AGG(id),
            ARRAY[]::BIGINT[]
        )
        INTO v_new_items
        FROM UNNEST(v_closure) AS id
        WHERE NOT id = ANY(v_selected);

        SELECT
            COALESCE(SUM(effort), 0),
            COALESCE(SUM(estimated_cost), 0)
        INTO
            v_additional_effort,
            v_additional_budget
        FROM initiatives
        WHERE initiative_id = ANY(v_new_items);

        IF
            v_effort_used + v_additional_effort >
                v_portfolio.available_effort
            OR
            v_budget_used + v_additional_budget >
                v_portfolio.available_budget
        THEN
            RAISE EXCEPTION
                'Mandatory initiative % cannot fit portfolio capacity.',
                v_item.initiative_code;
        END IF;

        v_selected := v_selected || v_new_items;

        v_effort_used :=
            v_effort_used + v_additional_effort;

        v_budget_used :=
            v_budget_used + v_additional_budget;

    END LOOP;

    -- Optional initiatives are evaluated by their chosen framework.
    FOR v_candidate IN
        SELECT
            i.initiative_id,
            i.initiative_code,
            calculate_initiative_score(
                i.initiative_id,
                p_framework
            ) AS score
        FROM initiatives i
        WHERE i.portfolio_id = p_portfolio_id
          AND i.mandatory = FALSE
        ORDER BY
            CASE i.priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END,
            score DESC,
            i.initiative_id
    LOOP

        IF v_candidate.initiative_id = ANY(v_selected) THEN
            CONTINUE;
        END IF;

        -- A dependency closure ensures prerequisites are considered
        -- together with the initiative that requires them.
        WITH RECURSIVE dependency_closure(id) AS (
            SELECT v_candidate.initiative_id

            UNION

            SELECT d.dependency_id
            FROM initiative_dependencies d
            JOIN dependency_closure c
              ON d.initiative_id = c.id
        )
        SELECT ARRAY_AGG(id)
        INTO v_closure
        FROM dependency_closure;

        SELECT COALESCE(
            ARRAY_AGG(id),
            ARRAY[]::BIGINT[]
        )
        INTO v_new_items
        FROM UNNEST(v_closure) AS id
        WHERE NOT id = ANY(v_selected);

        -- Every newly required dependency must satisfy the portfolio policy.
        SELECT EXISTS (
            SELECT 1
            FROM initiatives i
            WHERE i.initiative_id = ANY(v_new_items)
              AND (
                  i.confidence < v_portfolio.minimum_confidence
                  OR (
                      v_portfolio.require_strategic_alignment
                      AND i.strategic_alignment = 0
                  )
              )
        )
        INTO v_policy_failure;

        IF v_policy_failure THEN
            CONTINUE;
        END IF;

        SELECT
            COALESCE(SUM(effort), 0),
            COALESCE(SUM(estimated_cost), 0)
        INTO
            v_additional_effort,
            v_additional_budget
        FROM initiatives
        WHERE initiative_id = ANY(v_new_items);

        IF
            v_effort_used + v_additional_effort >
                v_portfolio.available_effort
            OR
            v_budget_used + v_additional_budget >
                v_portfolio.available_budget
        THEN
            CONTINUE;
        END IF;

        v_selected := v_selected || v_new_items;

        v_effort_used :=
            v_effort_used + v_additional_effort;

        v_budget_used :=
            v_budget_used + v_additional_budget;

    END LOOP;

    -- Compute the value of selected initiatives.
    SELECT COALESCE(SUM(business_value), 0)
    INTO v_business_value
    FROM initiatives
    WHERE initiative_id = ANY(v_selected);

    -- Opportunity cost is the sum of framework scores for deferred work.
    SELECT COALESCE(
        SUM(calculate_initiative_score(
            initiative_id,
            p_framework
        )),
        0
    )
    INTO v_opportunity_cost
    FROM initiatives
    WHERE portfolio_id = p_portfolio_id
      AND NOT initiative_id = ANY(v_selected);

    -- Store a decision for every initiative.
    INSERT INTO initiative_decisions (
        allocation_run_id,
        initiative_id,
        framework,
        calculated_score,
        decision_status,
        explanation
    )
    SELECT
        p_allocation_run_id,
        i.initiative_id,
        p_framework,
        calculate_initiative_score(
            i.initiative_id,
            p_framework
        ),
        CASE
            WHEN i.initiative_id = ANY(v_selected)
                THEN 'selected'::initiative_status
            ELSE 'deferred'::initiative_status
        END,
        CASE
            WHEN i.initiative_id = ANY(v_selected)
                THEN 'Included within portfolio capacity.'
            ELSE 'Deferred due to policy, ranking or resource constraints.'
        END
    FROM initiatives i
    WHERE i.portfolio_id = p_portfolio_id;

    UPDATE initiatives
    SET status = CASE
        WHEN initiative_id = ANY(v_selected)
            THEN 'selected'::initiative_status
        ELSE 'deferred'::initiative_status
    END
    WHERE portfolio_id = p_portfolio_id;

    UPDATE allocation_runs
    SET
        status = 'completed',
        effort_consumed = v_effort_used,
        budget_consumed = v_budget_used,
        business_value = v_business_value,
        opportunity_cost = v_opportunity_cost,
        completed_at = CURRENT_TIMESTAMP
    WHERE allocation_run_id = p_allocation_run_id;

END;
$$;


-- ============================================================
-- 13. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW portfolio_allocation_report AS
SELECT
    r.allocation_run_id,
    p.portfolio_name,
    r.framework,
    r.status,
    p.available_effort,
    r.effort_consumed,
    p.available_effort - r.effort_consumed AS remaining_effort,
    p.available_budget,
    r.budget_consumed,
    p.available_budget - r.budget_consumed AS remaining_budget,
    r.business_value,
    r.opportunity_cost,
    r.created_at,
    r.completed_at
FROM allocation_runs r
JOIN portfolios p
    ON p.portfolio_id = r.portfolio_id;


CREATE OR REPLACE VIEW initiative_decision_report AS
SELECT
    d.allocation_run_id,
    p.portfolio_name,
    i.initiative_code,
    i.initiative_name,
    i.priority,
    i.classification,
    i.mandatory,
    d.framework,
    d.calculated_score,
    d.decision_status,
    d.explanation
FROM initiative_decisions d
JOIN initiatives i
    ON i.initiative_id = d.initiative_id
JOIN allocation_runs r
    ON r.allocation_run_id = d.allocation_run_id
JOIN portfolios p
    ON p.portfolio_id = r.portfolio_id;


-- ============================================================
-- 14. SAMPLE ORGANIZATIONAL DATA
-- ============================================================

INSERT INTO organizations (organization_name)
VALUES ('Enterprise Technology Division');

INSERT INTO portfolios (
    organization_id,
    portfolio_name,
    available_effort,
    available_budget,
    minimum_confidence,
    require_strategic_alignment
)
SELECT
    organization_id,
    'Technology Modernization 2026',
    35,
    45000,
    0.60,
    TRUE
FROM organizations
WHERE organization_name = 'Enterprise Technology Division';


INSERT INTO scoring_configurations (
    portfolio_id,
    framework,
    criterion_weights
)
SELECT
    portfolio_id,
    'weighted',
    '{
        "business_value": 0.30,
        "strategic_alignment": 0.30,
        "urgency": 0.15,
        "risk_reduction": 0.15,
        "confidence": 0.10
    }'::JSONB
FROM portfolios
WHERE portfolio_name = 'Technology Modernization 2026';


-- ============================================================
-- 15. SAMPLE INITIATIVES
-- ============================================================

INSERT INTO initiatives (
    portfolio_id,
    initiative_code,
    initiative_name,
    description,
    priority,
    classification,
    reach,
    impact,
    confidence,
    effort,
    business_value,
    urgency,
    risk_reduction,
    strategic_alignment,
    estimated_cost,
    mandatory
)
SELECT
    p.portfolio_id,
    v.code,
    v.name,
    v.description,
    v.priority::initiative_priority,
    v.classification::moscow_classification,
    v.reach,
    v.impact,
    v.confidence,
    v.effort,
    v.business_value,
    v.urgency,
    v.risk_reduction,
    v.strategic_alignment,
    v.estimated_cost,
    v.mandatory
FROM portfolios p
CROSS JOIN (
    VALUES
    (
        'I001',
        'Security compliance',
        'Mandatory regulatory security remediation.',
        'critical',
        'must',
        100::NUMERIC,
        10::NUMERIC,
        0.99::NUMERIC,
        8::NUMERIC,
        10::NUMERIC,
        10::NUMERIC,
        10::NUMERIC,
        10::NUMERIC,
        12000::NUMERIC,
        TRUE
    ),
    (
        'I002',
        'Customer analytics',
        'Build customer intelligence capabilities.',
        'high',
        'should',
        8000::NUMERIC,
        8::NUMERIC,
        0.85::NUMERIC,
        13::NUMERIC,
        9::NUMERIC,
        7::NUMERIC,
        4::NUMERIC,
        9::NUMERIC,
        18000::NUMERIC,
        FALSE
    ),
    (
        'I003',
        'Infrastructure optimization',
        'Reduce recurring infrastructure costs.',
        'high',
        'must',
        5000::NUMERIC,
        7::NUMERIC,
        0.95::NUMERIC,
        5::NUMERIC,
        8::NUMERIC,
        8::NUMERIC,
        6::NUMERIC,
        8::NUMERIC,
        7000::NUMERIC,
        FALSE
    ),
    (
        'I004',
        'Internal dashboard',
        'Improve operational reporting.',
        'medium',
        'could',
        2000::NUMERIC,
        5::NUMERIC,
        0.90::NUMERIC,
        4::NUMERIC,
        5::NUMERIC,
        3::NUMERIC,
        2::NUMERIC,
        6::NUMERIC,
        4000::NUMERIC,
        FALSE
    ),
    (
        'I005',
        'Disaster recovery',
        'Improve business continuity and recovery.',
        'high',
        'should',
        1000::NUMERIC,
        9::NUMERIC,
        0.90::NUMERIC,
        7::NUMERIC,
        9::NUMERIC,
        9::NUMERIC,
        10::NUMERIC,
        9::NUMERIC,
        10000::NUMERIC,
        FALSE
    ),
    (
        'I006',
        'Mobile redesign',
        'Improve the mobile user experience.',
        'low',
        'could',
        6000::NUMERIC,
        6::NUMERIC,
        0.75::NUMERIC,
        10::NUMERIC,
        7::NUMERIC,
        5::NUMERIC,
        3::NUMERIC,
        8::NUMERIC,
        14000::NUMERIC,
        FALSE
    )
) AS v(
    code,
    name,
    description,
    priority,
    classification,
    reach,
    impact,
    confidence,
    effort,
    business_value,
    urgency,
    risk_reduction,
    strategic_alignment,
    estimated_cost,
    mandatory
)
WHERE p.portfolio_name = 'Technology Modernization 2026';


-- ============================================================
-- 16. SAMPLE DEPENDENCY
-- ============================================================

INSERT INTO initiative_dependencies (
    initiative_id,
    dependency_id
)
SELECT
    child.initiative_id,
    parent.initiative_id
FROM initiatives child
JOIN initiatives parent
    ON parent.portfolio_id = child.portfolio_id
WHERE child.initiative_code = 'I002'
  AND parent.initiative_code = 'I001';


-- ============================================================
-- 17. TRANSACTIONAL ALLOCATION
-- ============================================================

DO $$
DECLARE
    v_portfolio_id BIGINT;
    v_run_id BIGINT;
BEGIN
    SELECT portfolio_id
    INTO v_portfolio_id
    FROM portfolios
    WHERE portfolio_name = 'Technology Modernization 2026';

    CALL allocate_portfolio(
        v_portfolio_id,
        'weighted',
        v_run_id
    );

    RAISE NOTICE
        'Completed allocation run: %',
        v_run_id;
END;
$$;


-- ============================================================
-- 18. RETRIEVAL QUERIES
-- ============================================================

SELECT
    initiative_code,
    initiative_name,
    priority,
    classification,
    mandatory,
    effort,
    estimated_cost
FROM initiatives
ORDER BY priority, initiative_code;


-- ============================================================
-- 19. FRAMEWORK EVALUATION
-- ============================================================

SELECT
    initiative_code,
    initiative_name,
    rice_score,
    wsjf_score,
    weighted_score
FROM initiative_ranking
ORDER BY portfolio_id, weighted_score DESC;


-- ============================================================
-- 20. DECISION RETRIEVAL
-- ============================================================

SELECT *
FROM initiative_decision_report
ORDER BY allocation_run_id, decision_status, calculated_score DESC;


-- ============================================================
-- 21. AGGREGATION
-- ============================================================

SELECT
    allocation_run_id,
    framework,
    COUNT(*) AS total_initiatives,
    COUNT(*) FILTER (
        WHERE decision_status = 'selected'
    ) AS selected_count,
    COUNT(*) FILTER (
        WHERE decision_status = 'deferred'
    ) AS deferred_count,
    ROUND(
        AVG(calculated_score),
        4
    ) AS average_score
FROM initiative_decisions
GROUP BY allocation_run_id, framework;


-- ============================================================
-- 22. CAPACITY AND OPPORTUNITY-COST REPORTING
-- ============================================================

SELECT
    portfolio_name,
    framework,
    effort_consumed,
    remaining_effort,
    budget_consumed,
    remaining_budget,
    business_value,
    opportunity_cost
FROM portfolio_allocation_report;


-- ============================================================
-- 23. VALIDATION QUERIES
-- ============================================================

-- Detect initiatives whose dependencies are outside their portfolio.
SELECT
    child.initiative_code,
    parent.initiative_code AS dependency_code
FROM initiative_dependencies d
JOIN initiatives child
    ON child.initiative_id = d.initiative_id
JOIN initiatives parent
    ON parent.initiative_id = d.dependency_id
WHERE child.portfolio_id <> parent.portfolio_id;


-- Find initiatives below confidence requirements.
SELECT
    i.initiative_code,
    i.confidence,
    p.minimum_confidence
FROM initiatives i
JOIN portfolios p
    ON p.portfolio_id = i.portfolio_id
WHERE i.confidence < p.minimum_confidence;


-- Find unallocated mandatory initiatives.
SELECT
    i.initiative_code,
    i.initiative_name
FROM initiatives i
WHERE i.mandatory = TRUE
  AND i.status <> 'selected';


-- ============================================================
-- 24. COMPARATIVE FRAMEWORK REPORT
-- ============================================================

SELECT
    initiative_code,
    ROUND(rice_score, 2) AS rice,
    ROUND(wsjf_score, 2) AS wsjf,
    ROUND(weighted_score, 2) AS weighted,
    CASE
        WHEN rice_score >= 10000 THEN 'High RICE'
        ELSE 'Standard RICE'
    END AS rice_interpretation
FROM initiative_ranking
ORDER BY weighted_score DESC;


-- ============================================================
-- 25. SECOND ALLOCATION UNDER WSJF
-- ============================================================

DO $$
DECLARE
    v_portfolio_id BIGINT;
    v_run_id BIGINT;
BEGIN
    SELECT portfolio_id
    INTO v_portfolio_id
    FROM portfolios
    WHERE portfolio_name = 'Technology Modernization 2026';

    CALL allocate_portfolio(
        v_portfolio_id,
        'wsjf',
        v_run_id
    );

    RAISE NOTICE
        'WSJF allocation run completed: %',
        v_run_id;
END;
$$;


-- ============================================================
-- 26. HISTORICAL FRAMEWORK COMPARISON
-- ============================================================

SELECT
    r.framework,
    r.allocation_run_id,
    r.effort_consumed,
    r.budget_consumed,
    r.business_value,
    r.opportunity_cost,
    COUNT(d.decision_id) FILTER (
        WHERE d.decision_status = 'selected'
    ) AS selected_initiatives
FROM allocation_runs r
LEFT JOIN initiative_decisions d
    ON d.allocation_run_id = r.allocation_run_id
GROUP BY
    r.allocation_run_id,
    r.framework,
    r.effort_consumed,
    r.budget_consumed,
    r.business_value,
    r.opportunity_cost
ORDER BY r.created_at;


COMMIT;
