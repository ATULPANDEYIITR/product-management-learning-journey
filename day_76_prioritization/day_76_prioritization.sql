/*
===============================================================================
ADVANCED OPPORTUNITY PRIORITIZATION DATABASE
===============================================================================

Domain:
    Opportunity scoring
    Weighted scoring
    Economic prioritization
    Strategic alignment
    Portfolio optimization
    Investment decisions
    Governance and audit history

PostgreSQL: 14+

Features:
    Relational domain modeling
    Normalized criteria and weights
    Economic evaluation
    Weighted scoring
    Confidence adjustments
    WSJF calculation
    Dependency validation
    Lifecycle management
    Approval policies
    Budget-constrained portfolio selection
    Reporting and aggregation
    Constraints, indexes, functions and triggers

The script is designed to run as a complete demonstration.
It recreates the prioritization_demo schema.
*/

BEGIN;

DROP SCHEMA IF EXISTS prioritization_demo CASCADE;

CREATE SCHEMA prioritization_demo;

SET search_path TO prioritization_demo, public;


-- ============================================================================
-- 1. ENUMERATIONS
-- ============================================================================

CREATE TYPE opportunity_status AS ENUM (
    'proposed',
    'evaluated',
    'approved',
    'deferred',
    'rejected'
);

CREATE TYPE priority_tier AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);

CREATE TYPE decision_type AS ENUM (
    'created',
    'evaluated',
    'approved',
    'deferred',
    'rejected'
);

CREATE TYPE criterion_type AS ENUM (
    'strategic',
    'economic',
    'customer',
    'urgency',
    'feasibility',
    'risk'
);


-- ============================================================================
-- 2. ORGANIZATIONAL STRUCTURE
-- ============================================================================

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_name VARCHAR(150) NOT NULL UNIQUE,

    currency_code CHAR(3) NOT NULL DEFAULT 'INR',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    username VARCHAR(100) NOT NULL,

    role_name VARCHAR(50) NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (organization_id, username),

    UNIQUE (organization_id, user_id)
);


-- ============================================================================
-- 3. PORTFOLIO AND FINANCIAL BUDGET
-- ============================================================================

CREATE TABLE portfolios (
    portfolio_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    portfolio_name VARCHAR(150) NOT NULL,

    description TEXT,

    total_budget NUMERIC(18, 2) NOT NULL,

    currency_code CHAR(3) NOT NULL DEFAULT 'INR',

    planning_period VARCHAR(30) NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (total_budget >= 0),

    UNIQUE (organization_id, portfolio_name)
);


-- ============================================================================
-- 4. SCORING MODEL
-- ============================================================================

CREATE TABLE scoring_models (
    scoring_model_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    model_name VARCHAR(120) NOT NULL,

    version INTEGER NOT NULL DEFAULT 1,

    description TEXT,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (version > 0),

    UNIQUE (
        organization_id,
        model_name,
        version
    )
);


CREATE TABLE scoring_criteria (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    scoring_model_id BIGINT NOT NULL
        REFERENCES scoring_models(scoring_model_id)
        ON DELETE CASCADE,

    criterion_code VARCHAR(40) NOT NULL,

    criterion_name VARCHAR(100) NOT NULL,

    criterion_category criterion_type NOT NULL,

    weight NUMERIC(8, 6) NOT NULL,

    description TEXT,

    UNIQUE (scoring_model_id, criterion_code),

    CHECK (weight >= 0 AND weight <= 1)
);


-- ============================================================================
-- 5. STRATEGIC OBJECTIVES
-- ============================================================================

CREATE TABLE strategic_objectives (
    objective_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    objective_code VARCHAR(40) NOT NULL,

    objective_name VARCHAR(150) NOT NULL,

    description TEXT,

    strategic_weight NUMERIC(8, 4) NOT NULL DEFAULT 1,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (organization_id, objective_code),

    CHECK (strategic_weight >= 0 AND strategic_weight <= 100)
);


-- ============================================================================
-- 6. OPPORTUNITIES
-- ============================================================================

CREATE TABLE opportunities (
    opportunity_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    opportunity_code VARCHAR(40) NOT NULL,

    opportunity_name VARCHAR(180) NOT NULL,

    description TEXT,

    owner_user_id BIGINT
        REFERENCES users(user_id),

    expected_benefit NUMERIC(18, 2) NOT NULL,

    implementation_cost NUMERIC(18, 2) NOT NULL,

    implementation_effort NUMERIC(12, 2) NOT NULL,

    cost_of_delay NUMERIC(18, 2) NOT NULL DEFAULT 0,

    confidence_score NUMERIC(5, 2) NOT NULL,

    customer_value_score NUMERIC(5, 2) NOT NULL,

    urgency_score NUMERIC(5, 2) NOT NULL,

    feasibility_score NUMERIC(5, 2) NOT NULL,

    risk_score NUMERIC(5, 2) NOT NULL,

    status opportunity_status NOT NULL DEFAULT 'proposed',

    mandatory BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (portfolio_id, opportunity_code),

    CHECK (expected_benefit >= 0),

    CHECK (implementation_cost > 0),

    CHECK (implementation_effort > 0),

    CHECK (cost_of_delay >= 0),

    CHECK (
        confidence_score BETWEEN 0 AND 100
    ),

    CHECK (
        customer_value_score BETWEEN 0 AND 100
    ),

    CHECK (
        urgency_score BETWEEN 0 AND 100
    ),

    CHECK (
        feasibility_score BETWEEN 0 AND 100
    ),

    CHECK (
        risk_score BETWEEN 0 AND 100
    )
);


-- ============================================================================
-- 7. STRATEGIC ALIGNMENT
-- ============================================================================

CREATE TABLE opportunity_objectives (
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id)
        ON DELETE CASCADE,

    objective_id BIGINT NOT NULL
        REFERENCES strategic_objectives(objective_id),

    alignment_score NUMERIC(5, 2) NOT NULL,

    contribution_weight NUMERIC(8, 6) NOT NULL DEFAULT 1,

    PRIMARY KEY (
        opportunity_id,
        objective_id
    ),

    CHECK (alignment_score BETWEEN 0 AND 100),

    CHECK (contribution_weight >= 0)
);


-- ============================================================================
-- 8. OPPORTUNITY DEPENDENCIES
-- ============================================================================

CREATE TABLE opportunity_dependencies (
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id)
        ON DELETE CASCADE,

    depends_on_opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id),

    dependency_type VARCHAR(30) NOT NULL DEFAULT 'required',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        opportunity_id,
        depends_on_opportunity_id
    ),

    CHECK (
        opportunity_id <> depends_on_opportunity_id
    ),

    CHECK (
        dependency_type IN (
            'required',
            'optional'
        )
    )
);


-- ============================================================================
-- 9. SCORING RESULTS
-- ============================================================================

CREATE TABLE opportunity_scores (
    score_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id)
        ON DELETE CASCADE,

    scoring_model_id BIGINT NOT NULL
        REFERENCES scoring_models(scoring_model_id),

    strategic_score NUMERIC(8, 4) NOT NULL,

    economic_score NUMERIC(8, 4) NOT NULL,

    weighted_score NUMERIC(8, 4) NOT NULL,

    adjusted_score NUMERIC(8, 4) NOT NULL,

    expected_net_value NUMERIC(18, 2) NOT NULL,

    expected_roi NUMERIC(12, 4) NOT NULL,

    wsjf_score NUMERIC(12, 4) NOT NULL,

    priority priority_tier NOT NULL,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (
        opportunity_id,
        scoring_model_id
    ),

    CHECK (strategic_score BETWEEN 0 AND 100),

    CHECK (economic_score BETWEEN 0 AND 100),

    CHECK (weighted_score BETWEEN 0 AND 100),

    CHECK (adjusted_score BETWEEN 0 AND 100),

    CHECK (wsjf_score >= 0)
);


-- ============================================================================
-- 10. APPROVAL GOVERNANCE
-- ============================================================================

CREATE TABLE approval_policies (
    approval_policy_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id),

    policy_name VARCHAR(120) NOT NULL,

    required_approvals INTEGER NOT NULL DEFAULT 2,

    minimum_strategic_fit NUMERIC(5, 2) NOT NULL DEFAULT 60,

    require_positive_net_value BOOLEAN NOT NULL DEFAULT FALSE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CHECK (required_approvals > 0),

    CHECK (
        minimum_strategic_fit BETWEEN 0 AND 100
    )
);


CREATE TABLE opportunity_approvals (
    approval_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id)
        ON DELETE CASCADE,

    user_id BIGINT NOT NULL
        REFERENCES users(user_id),

    approval_policy_id BIGINT NOT NULL
        REFERENCES approval_policies(approval_policy_id),

    approved BOOLEAN NOT NULL,

    comments TEXT,

    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (
        opportunity_id,
        user_id,
        approval_policy_id
    )
);


-- ============================================================================
-- 11. DECISION AUDIT HISTORY
-- ============================================================================

CREATE TABLE decision_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id),

    actor_user_id BIGINT
        REFERENCES users(user_id),

    event_type decision_type NOT NULL,

    previous_status opportunity_status,

    new_status opportunity_status,

    reason TEXT,

    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- 12. INDEXES
-- ============================================================================

CREATE INDEX idx_opportunities_portfolio_status
    ON opportunities (
        portfolio_id,
        status
    );

CREATE INDEX idx_opportunities_mandatory
    ON opportunities (
        portfolio_id,
        mandatory
    );

CREATE INDEX idx_scores_priority_adjusted
    ON opportunity_scores (
        priority,
        adjusted_score DESC
    );

CREATE INDEX idx_scores_model
    ON opportunity_scores (
        scoring_model_id,
        adjusted_score DESC
    );

CREATE INDEX idx_dependencies_reverse
    ON opportunity_dependencies (
        depends_on_opportunity_id
    );

CREATE INDEX idx_approvals_opportunity
    ON opportunity_approvals (
        opportunity_id,
        approval_policy_id,
        approved
    );

CREATE INDEX idx_audit_opportunity_time
    ON decision_audit (
        opportunity_id,
        event_time DESC
    );


-- ============================================================================
-- 13. WEIGHT VALIDATION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_scoring_model_weights()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_model_id BIGINT;
    v_total NUMERIC(12, 8);
    v_count INTEGER;
BEGIN
    v_model_id := COALESCE(
        NEW.scoring_model_id,
        OLD.scoring_model_id
    );

    SELECT
        COALESCE(SUM(weight), 0),
        COUNT(*)
    INTO
        v_total,
        v_count
    FROM scoring_criteria
    WHERE scoring_model_id = v_model_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION
            'Scoring model % must have criteria.',
            v_model_id;
    END IF;

    IF ABS(v_total - 1.0) > 0.000001 THEN
        RAISE EXCEPTION
            'Scoring model % has invalid weight total: %',
            v_model_id,
            v_total;
    END IF;

    RETURN NULL;
END;
$$;


CREATE CONSTRAINT TRIGGER trg_validate_scoring_weights
AFTER INSERT OR UPDATE OR DELETE
ON scoring_criteria
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION validate_scoring_model_weights();


-- ============================================================================
-- 14. DEPENDENCY CYCLE VALIDATION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_dependency_graph()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cycle BOOLEAN;
BEGIN
    IF NEW.opportunity_id = NEW.depends_on_opportunity_id THEN
        RAISE EXCEPTION 'Self-dependency is prohibited.';
    END IF;

    WITH RECURSIVE dependency_tree(id, path, cycle) AS (
        SELECT
            NEW.depends_on_opportunity_id,
            ARRAY[NEW.opportunity_id,
                  NEW.depends_on_opportunity_id]::BIGINT[],
            NEW.depends_on_opportunity_id =
                NEW.opportunity_id

        UNION ALL

        SELECT
            d.depends_on_opportunity_id,
            t.path || d.depends_on_opportunity_id,
            d.depends_on_opportunity_id =
                ANY(t.path)
        FROM dependency_tree t
        JOIN opportunity_dependencies d
          ON d.opportunity_id = t.id
        WHERE NOT t.cycle
    )
    SELECT COALESCE(BOOL_OR(cycle), FALSE)
    INTO v_cycle
    FROM dependency_tree;

    IF v_cycle THEN
        RAISE EXCEPTION
            'Circular dependency detected.';
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_validate_dependency_graph
BEFORE INSERT OR UPDATE
ON opportunity_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_graph();


-- ============================================================================
-- 15. AUTOMATIC UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_opportunity_updated_at
BEFORE UPDATE
ON opportunities
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();


-- ============================================================================
-- 16. DECISION AUDIT TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION audit_opportunity_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_event decision_type;
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO decision_audit (
            opportunity_id,
            event_type,
            previous_status,
            new_status,
            reason
        )
        VALUES (
            NEW.opportunity_id,
            'created',
            NULL,
            NEW.status,
            'Opportunity created.'
        );

        RETURN NEW;
    END IF;

    IF NEW.status IS DISTINCT FROM OLD.status THEN
        v_event := CASE NEW.status
            WHEN 'evaluated' THEN 'evaluated'::decision_type
            WHEN 'approved' THEN 'approved'::decision_type
            WHEN 'deferred' THEN 'deferred'::decision_type
            WHEN 'rejected' THEN 'rejected'::decision_type
            ELSE 'created'::decision_type
        END;

        INSERT INTO decision_audit (
            opportunity_id,
            event_type,
            previous_status,
            new_status,
            reason
        )
        VALUES (
            NEW.opportunity_id,
            v_event,
            OLD.status,
            NEW.status,
            'Status transition recorded.'
        );
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_audit_opportunity_status
AFTER INSERT OR UPDATE OF status
ON opportunities
FOR EACH ROW
EXECUTE FUNCTION audit_opportunity_status();


-- ============================================================================
-- 17. ECONOMIC EVALUATION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_economic_score(
    p_benefit NUMERIC,
    p_cost NUMERIC,
    p_confidence NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_expected NUMERIC;
    v_net NUMERIC;
BEGIN
    IF p_cost <= 0 THEN
        RAISE EXCEPTION
            'Implementation cost must be positive.';
    END IF;

    IF p_benefit < 0 OR p_confidence NOT BETWEEN 0 AND 100 THEN
        RAISE EXCEPTION
            'Invalid economic inputs.';
    END IF;

    v_expected := p_benefit * p_confidence / 100.0;

    v_net := v_expected - p_cost;

    RETURN LEAST(
        100,
        GREATEST(
            0,
            50 + 50 * v_net / p_cost
        )
    );
END;
$$;


-- ============================================================================
-- 18. STRATEGIC FIT FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_strategic_fit(
    p_opportunity_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_score NUMERIC;
BEGIN
    SELECT
        COALESCE(
            SUM(alignment_score * contribution_weight)
            / NULLIF(SUM(contribution_weight), 0),
            0
        )
    INTO v_score
    FROM opportunity_objectives
    WHERE opportunity_id = p_opportunity_id;

    RETURN ROUND(v_score, 4);
END;
$$;


-- ============================================================================
-- 19. SCORING PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE evaluate_opportunity(
    p_opportunity_id BIGINT,
    p_scoring_model_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_opportunity opportunities%ROWTYPE;

    v_strategic NUMERIC;
    v_economic NUMERIC;
    v_weighted NUMERIC;
    v_adjusted NUMERIC;

    v_net NUMERIC;
    v_roi NUMERIC;
    v_wsjf NUMERIC;

    v_tier priority_tier;

    v_weight_total NUMERIC;
BEGIN
    SELECT *
    INTO STRICT v_opportunity
    FROM opportunities
    WHERE opportunity_id = p_opportunity_id
    FOR UPDATE;

    SELECT COALESCE(SUM(weight), 0)
    INTO v_weight_total
    FROM scoring_criteria
    WHERE scoring_model_id = p_scoring_model_id;

    IF ABS(v_weight_total - 1.0) > 0.000001 THEN
        RAISE EXCEPTION
            'Invalid scoring model weight total: %',
            v_weight_total;
    END IF;

    v_strategic :=
        calculate_strategic_fit(p_opportunity_id);

    v_economic := calculate_economic_score(
        v_opportunity.expected_benefit,
        v_opportunity.implementation_cost,
        v_opportunity.confidence_score
    );

    v_net :=
        v_opportunity.expected_benefit
        * v_opportunity.confidence_score / 100
        - v_opportunity.implementation_cost;

    v_roi :=
        v_net / v_opportunity.implementation_cost * 100;

    v_wsjf :=
        v_opportunity.cost_of_delay
        / v_opportunity.implementation_effort;

    SELECT SUM(
        CASE c.criterion_category
            WHEN 'strategic' THEN
                v_strategic * c.weight

            WHEN 'economic' THEN
                v_economic * c.weight

            WHEN 'customer' THEN
                v_opportunity.customer_value_score * c.weight

            WHEN 'urgency' THEN
                v_opportunity.urgency_score * c.weight

            WHEN 'feasibility' THEN
                v_opportunity.feasibility_score * c.weight

            WHEN 'risk' THEN
                (100 - v_opportunity.risk_score) * c.weight
        END
    )
    INTO v_weighted
    FROM scoring_criteria c
    WHERE c.scoring_model_id = p_scoring_model_id;

    v_adjusted :=
        v_weighted * v_opportunity.confidence_score / 100;

    v_tier := CASE
        WHEN v_adjusted >= 85 THEN 'critical'::priority_tier
        WHEN v_adjusted >= 70 THEN 'high'::priority_tier
        WHEN v_adjusted >= 50 THEN 'medium'::priority_tier
        ELSE 'low'::priority_tier
    END;

    INSERT INTO opportunity_scores (
        opportunity_id,
        scoring_model_id,
        strategic_score,
        economic_score,
        weighted_score,
        adjusted_score,
        expected_net_value,
        expected_roi,
        wsjf_score,
        priority
    )
    VALUES (
        p_opportunity_id,
        p_scoring_model_id,
        v_strategic,
        v_economic,
        v_weighted,
        v_adjusted,
        v_net,
        v_roi,
        v_wsjf,
        v_tier
    )
    ON CONFLICT (
        opportunity_id,
        scoring_model_id
    )
    DO UPDATE SET
        strategic_score = EXCLUDED.strategic_score,
        economic_score = EXCLUDED.economic_score,
        weighted_score = EXCLUDED.weighted_score,
        adjusted_score = EXCLUDED.adjusted_score,
        expected_net_value = EXCLUDED.expected_net_value,
        expected_roi = EXCLUDED.expected_roi,
        wsjf_score = EXCLUDED.wsjf_score,
        priority = EXCLUDED.priority,
        evaluated_at = CURRENT_TIMESTAMP;

    UPDATE opportunities
    SET status = 'evaluated'
    WHERE opportunity_id = p_opportunity_id
      AND status = 'proposed';
END;
$$;


-- ============================================================================
-- 20. APPROVAL ELIGIBILITY FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION check_approval_eligibility(
    p_opportunity_id BIGINT,
    p_approval_policy_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_required INTEGER;
    v_minimum NUMERIC;
    v_positive_required BOOLEAN;

    v_strategic NUMERIC;
    v_net NUMERIC;
    v_approvals INTEGER;
BEGIN
    SELECT
        required_approvals,
        minimum_strategic_fit,
        require_positive_net_value
    INTO STRICT
        v_required,
        v_minimum,
        v_positive_required
    FROM approval_policies
    WHERE approval_policy_id = p_approval_policy_id
      AND active = TRUE;

    SELECT
        s.strategic_score,
        s.expected_net_value
    INTO
        v_strategic,
        v_net
    FROM opportunity_scores s
    WHERE s.opportunity_id = p_opportunity_id
    ORDER BY s.evaluated_at DESC
    LIMIT 1;

    IF v_strategic IS NULL THEN
        RETURN FALSE;
    END IF;

    IF v_strategic < v_minimum THEN
        RETURN FALSE;
    END IF;

    IF v_positive_required AND v_net <= 0 THEN
        RETURN FALSE;
    END IF;

    SELECT COUNT(DISTINCT a.user_id)
    INTO v_approvals
    FROM opportunity_approvals a
    JOIN users u
      ON u.user_id = a.user_id
    WHERE a.opportunity_id = p_opportunity_id
      AND a.approval_policy_id = p_approval_policy_id
      AND a.approved = TRUE
      AND u.active = TRUE;

    RETURN v_approvals >= v_required;
END;
$$;


-- ============================================================================
-- 21. APPROVAL PROCESSING PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE approve_opportunity(
    p_opportunity_id BIGINT,
    p_approval_policy_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE opportunities
    SET status = 'approved'
    WHERE opportunity_id = p_opportunity_id
      AND status = 'evaluated'
      AND check_approval_eligibility(
          p_opportunity_id,
          p_approval_policy_id
      );

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Opportunity is not eligible for approval.';
    END IF;
END;
$$;


-- ============================================================================
-- 22. DEPENDENCY ELIGIBILITY FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION dependencies_satisfied(
    p_opportunity_id BIGINT,
    p_selected BIGINT[]
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM opportunity_dependencies d
        WHERE d.opportunity_id = p_opportunity_id
          AND d.dependency_type = 'required'
          AND NOT (
              d.depends_on_opportunity_id =
              ANY(COALESCE(p_selected, ARRAY[]::BIGINT[]))
          )
    );
$$;


-- ============================================================================
-- 23. VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW opportunity_priority_dashboard AS
SELECT
    o.opportunity_id,
    o.opportunity_code,
    o.opportunity_name,
    o.status,
    o.mandatory,

    p.portfolio_name,

    o.expected_benefit,
    o.implementation_cost,

    s.strategic_score,
    s.economic_score,
    s.weighted_score,
    s.adjusted_score,
    s.expected_net_value,
    s.expected_roi,
    s.wsjf_score,
    s.priority,

    s.evaluated_at

FROM opportunities o

JOIN portfolios p
  ON p.portfolio_id = o.portfolio_id

LEFT JOIN LATERAL (
    SELECT *
    FROM opportunity_scores os
    WHERE os.opportunity_id = o.opportunity_id
    ORDER BY os.evaluated_at DESC
    LIMIT 1
) s ON TRUE;


CREATE OR REPLACE VIEW portfolio_financial_summary AS
SELECT
    p.portfolio_id,
    p.portfolio_name,
    p.total_budget,

    COALESCE(
        SUM(o.implementation_cost),
        0
    ) AS proposed_cost,

    COALESCE(
        SUM(
            o.expected_benefit
            * o.confidence_score / 100
        ),
        0
    ) AS confidence_adjusted_benefit,

    COUNT(o.opportunity_id) AS opportunity_count,

    COUNT(*) FILTER (
        WHERE o.status = 'approved'
    ) AS approved_count

FROM portfolios p

LEFT JOIN opportunities o
  ON o.portfolio_id = p.portfolio_id

GROUP BY
    p.portfolio_id,
    p.portfolio_name,
    p.total_budget;


-- ============================================================================
-- 24. SAMPLE ORGANIZATION AND USERS
-- ============================================================================

INSERT INTO organizations (
    organization_name,
    currency_code
)
VALUES (
    'Enterprise Investment Group',
    'INR'
);


INSERT INTO users (
    organization_id,
    username,
    role_name
)
VALUES
    (1, 'product_director', 'product_director'),
    (1, 'finance_director', 'finance_director'),
    (1, 'security_director', 'security_director'),
    (1, 'portfolio_manager', 'portfolio_manager');


INSERT INTO portfolios (
    organization_id,
    portfolio_name,
    description,
    total_budget,
    currency_code,
    planning_period
)
VALUES (
    1,
    'Digital Transformation Portfolio',
    'Technology, customer experience and security investments.',
    700000,
    'INR',
    'FY2026-Q4'
);


INSERT INTO scoring_models (
    organization_id,
    model_name,
    version,
    description
)
VALUES (
    1,
    'Enterprise Weighted Prioritization',
    1,
    'Strategic, economic, customer and execution scoring.'
);


-- ============================================================================
-- 25. SAMPLE SCORING CRITERIA
-- ============================================================================

INSERT INTO scoring_criteria (
    scoring_model_id,
    criterion_code,
    criterion_name,
    criterion_category,
    weight
)
VALUES
    (1, 'STRATEGIC', 'Strategic Fit', 'strategic', 0.25),
    (1, 'ECONOMIC', 'Economic Value', 'economic', 0.25),
    (1, 'CUSTOMER', 'Customer Value', 'customer', 0.15),
    (1, 'URGENCY', 'Business Urgency', 'urgency', 0.15),
    (1, 'FEASIBILITY', 'Execution Feasibility', 'feasibility', 0.10),
    (1, 'RISK', 'Risk Adjustment', 'risk', 0.10);


-- ============================================================================
-- 26. STRATEGIC OBJECTIVES
-- ============================================================================

INSERT INTO strategic_objectives (
    organization_id,
    objective_code,
    objective_name,
    description,
    strategic_weight
)
VALUES
    (
        1,
        'OBJ-SEC',
        'Security Resilience',
        'Strengthen detection, protection and response.',
        100
    ),
    (
        1,
        'OBJ-CX',
        'Customer Experience',
        'Improve digital customer interactions.',
        90
    ),
    (
        1,
        'OBJ-EFF',
        'Operational Efficiency',
        'Reduce operating cost and manual work.',
        85
    ),
    (
        1,
        'OBJ-DATA',
        'Data-Driven Operations',
        'Improve organizational analytical capabilities.',
        95
    );


-- ============================================================================
-- 27. SAMPLE OPPORTUNITIES
-- ============================================================================

INSERT INTO opportunities (
    portfolio_id,
    opportunity_code,
    opportunity_name,
    description,
    owner_user_id,
    expected_benefit,
    implementation_cost,
    implementation_effort,
    cost_of_delay,
    confidence_score,
    customer_value_score,
    urgency_score,
    feasibility_score,
    risk_score,
    mandatory
)
VALUES
(
    1,
    'OP-001',
    'Customer Analytics Platform',
    'Centralized customer intelligence platform.',
    4,
    900000,
    250000,
    12,
    120000,
    85,
    90,
    85,
    80,
    25,
    FALSE
),
(
    1,
    'OP-002',
    'Cloud Cost Optimization',
    'Reduce infrastructure expenditure.',
    4,
    600000,
    150000,
    8,
    85000,
    90,
    65,
    75,
    90,
    15,
    FALSE
),
(
    1,
    'OP-003',
    'Security Monitoring Modernization',
    'Modernize security monitoring capabilities.',
    4,
    750000,
    300000,
    15,
    180000,
    90,
    80,
    95,
    75,
    20,
    TRUE
),
(
    1,
    'OP-004',
    'Mobile Experience Improvement',
    'Improve customer mobile application usability.',
    4,
    450000,
    120000,
    7,
    70000,
    80,
    95,
    70,
    85,
    15,
    FALSE
),
(
    1,
    'OP-005',
    'Reporting Automation',
    'Automate repetitive reporting operations.',
    4,
    180000,
    80000,
    5,
    20000,
    95,
    50,
    45,
    95,
    10,
    FALSE
);


-- ============================================================================
-- 28. SAMPLE STRATEGIC ALIGNMENT
-- ============================================================================

INSERT INTO opportunity_objectives (
    opportunity_id,
    objective_id,
    alignment_score,
    contribution_weight
)
VALUES
    (1, 4, 95, 1),
    (1, 2, 90, 1),
    (2, 3, 85, 1),
    (3, 1, 100, 1),
    (4, 2, 75, 1),
    (5, 3, 60, 1);


-- ============================================================================
-- 29. SAMPLE DEPENDENCY
-- ============================================================================

INSERT INTO opportunity_dependencies (
    opportunity_id,
    depends_on_opportunity_id,
    dependency_type
)
VALUES (
    4,
    1,
    'required'
);


-- ============================================================================
-- 30. APPROVAL POLICY AND SAMPLE APPROVALS
-- ============================================================================

INSERT INTO approval_policies (
    portfolio_id,
    policy_name,
    required_approvals,
    minimum_strategic_fit,
    require_positive_net_value
)
VALUES (
    1,
    'Investment Committee Approval',
    2,
    60,
    FALSE
);


INSERT INTO opportunity_approvals (
    opportunity_id,
    user_id,
    approval_policy_id,
    approved,
    comments
)
VALUES
(
    1,
    1,
    1,
    TRUE,
    'Product strategy alignment verified.'
),
(
    1,
    2,
    1,
    TRUE,
    'Economic assessment reviewed.'
);


-- ============================================================================
-- 31. EVALUATE ALL OPPORTUNITIES
-- ============================================================================

DO $$
DECLARE
    v_id BIGINT;
BEGIN
    FOR v_id IN
        SELECT opportunity_id
        FROM opportunities
        ORDER BY opportunity_id
    LOOP
        CALL evaluate_opportunity(v_id, 1);
    END LOOP;
END;
$$;


-- ============================================================================
-- 32. APPROVAL WORKFLOW
-- ============================================================================

CALL approve_opportunity(1, 1);


-- ============================================================================
-- 33. RETRIEVAL: PRIORITIZATION DASHBOARD
-- ============================================================================

SELECT
    opportunity_code,
    opportunity_name,
    status,
    strategic_score,
    economic_score,
    weighted_score,
    adjusted_score,
    expected_net_value,
    expected_roi,
    wsjf_score,
    priority
FROM opportunity_priority_dashboard
ORDER BY
    adjusted_score DESC NULLS LAST,
    wsjf_score DESC NULLS LAST;


-- ============================================================================
-- 34. AGGREGATION: PORTFOLIO FINANCIAL POSITION
-- ============================================================================

SELECT *
FROM portfolio_financial_summary;


-- ============================================================================
-- 35. EVALUATION: ECONOMIC COMPARISON
-- ============================================================================

SELECT
    opportunity_code,
    opportunity_name,

    expected_benefit,

    implementation_cost,

    expected_benefit
        * confidence_score / 100
        AS confidence_adjusted_benefit,

    expected_benefit
        * confidence_score / 100
        - implementation_cost
        AS expected_net_value,

    ROUND(
        (
            expected_benefit
            * confidence_score / 100
            - implementation_cost
        ) / implementation_cost * 100,
        2
    ) AS expected_roi_percent

FROM opportunities
ORDER BY expected_net_value DESC;


-- ============================================================================
-- 36. EVALUATION: WSJF
-- ============================================================================

SELECT
    opportunity_code,
    opportunity_name,

    cost_of_delay,

    implementation_effort,

    ROUND(
        cost_of_delay / implementation_effort,
        2
    ) AS wsjf

FROM opportunities

ORDER BY wsjf DESC;


-- ============================================================================
-- 37. CTE: DEPENDENCY VALIDATION
-- ============================================================================

WITH RECURSIVE dependency_tree AS (
    SELECT
        d.opportunity_id,
        d.depends_on_opportunity_id,
        ARRAY[
            d.opportunity_id,
            d.depends_on_opportunity_id
        ]::BIGINT[] AS path,
        FALSE AS cycle
    FROM opportunity_dependencies d

    UNION ALL

    SELECT
        t.opportunity_id,
        d.depends_on_opportunity_id,
        t.path || d.depends_on_opportunity_id,
        d.depends_on_opportunity_id = ANY(t.path)
    FROM dependency_tree t
    JOIN opportunity_dependencies d
      ON d.opportunity_id = t.depends_on_opportunity_id
    WHERE NOT t.cycle
)
SELECT
    opportunity_id,
    depends_on_opportunity_id,
    path,
    cycle
FROM dependency_tree
ORDER BY opportunity_id;


-- ============================================================================
-- 38. CTE: APPROVAL ELIGIBILITY REPORT
-- ============================================================================

SELECT
    o.opportunity_code,
    o.opportunity_name,

    p.policy_name,

    check_approval_eligibility(
        o.opportunity_id,
        p.approval_policy_id
    ) AS approval_eligible

FROM opportunities o

JOIN approval_policies p
  ON p.portfolio_id = o.portfolio_id

ORDER BY o.opportunity_id;


-- ============================================================================
-- 39. CTE: REQUIRED DEPENDENCY COMPLETENESS
-- ============================================================================

WITH proposed AS (
    SELECT
        o.opportunity_id,
        o.opportunity_code,
        o.opportunity_name
    FROM opportunities o
    WHERE o.status IN ('evaluated', 'approved')
)
SELECT
    p.opportunity_code,
    p.opportunity_name,
    d.depends_on_opportunity_id,
    dependency.status AS dependency_status,

    CASE
        WHEN dependency.status = 'approved'
        THEN TRUE
        ELSE FALSE
    END AS dependency_approved

FROM proposed p

JOIN opportunity_dependencies d
  ON d.opportunity_id = p.opportunity_id
 AND d.dependency_type = 'required'

JOIN opportunities dependency
  ON dependency.opportunity_id =
     d.depends_on_opportunity_id

ORDER BY p.opportunity_code;


-- ============================================================================
-- 40. PORTFOLIO BUDGET ELIGIBILITY
-- ============================================================================

SELECT
    p.portfolio_name,
    p.total_budget,

    COALESCE(
        SUM(o.implementation_cost)
            FILTER (WHERE o.mandatory),
        0
    ) AS mandatory_cost,

    CASE
        WHEN COALESCE(
            SUM(o.implementation_cost)
                FILTER (WHERE o.mandatory),
            0
        ) <= p.total_budget
        THEN 'FEASIBLE'
        ELSE 'BUDGET_CONFLICT'
    END AS mandatory_budget_status

FROM portfolios p

LEFT JOIN opportunities o
  ON o.portfolio_id = p.portfolio_id

GROUP BY
    p.portfolio_id,
    p.portfolio_name,
    p.total_budget;


-- ============================================================================
-- 41. WORKFLOW: DEFER AN OPPORTUNITY
-- ============================================================================

UPDATE opportunities
SET status = 'deferred'
WHERE opportunity_code = 'OP-005'
  AND status = 'evaluated';


-- ============================================================================
-- 42. AUDIT REPORT
-- ============================================================================

SELECT
    a.audit_id,
    o.opportunity_code,
    a.event_type,
    a.previous_status,
    a.new_status,
    a.reason,
    a.event_time

FROM decision_audit a

JOIN opportunities o
  ON o.opportunity_id = a.opportunity_id

ORDER BY a.event_time, a.audit_id;


-- ============================================================================
-- 43. TRANSACTION AND FAILURE-HANDLING EXAMPLE
-- ============================================================================

DO $$
BEGIN
    BEGIN
        -- Demonstrate an invalid economic input.
        -- The exception is isolated within the subtransaction.
        PERFORM calculate_economic_score(
            100000,
            0,
            80
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected validation failure: %',
                SQLERRM;
    END;
END;
$$;


-- ============================================================================
-- 44. FINAL OPERATIONAL REPORT
-- ============================================================================

SELECT
    o.opportunity_code,
    o.opportunity_name,
    o.status,
    o.mandatory,

    s.adjusted_score,
    s.expected_net_value,
    s.expected_roi,
    s.wsjf_score,
    s.priority,

    CASE
        WHEN o.status = 'approved'
            THEN 'APPROVED'

        WHEN o.status = 'deferred'
            THEN 'DEFERRED'

        WHEN s.adjusted_score IS NULL
            THEN 'NOT_EVALUATED'

        WHEN s.expected_net_value <= 0
            THEN 'ECONOMIC_REVIEW_REQUIRED'

        ELSE 'REQUIRES_GOVERNANCE_DECISION'
    END AS decision_assessment

FROM opportunities o

LEFT JOIN opportunity_scores s
  ON s.opportunity_id = o.opportunity_id

ORDER BY
    s.adjusted_score DESC NULLS LAST,
    o.opportunity_code;


COMMIT;

-- ============================================================================
-- END OF ADVANCED OPPORTUNITY PRIORITIZATION DATABASE
-- ============================================================================
