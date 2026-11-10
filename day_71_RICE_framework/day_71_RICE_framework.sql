-- ============================================================
-- RICE FRAMEWORK: PRODUCT PRIORITIZATION DATABASE
-- PostgreSQL 15+
--
-- Models:
--   Opportunities
--   RICE inputs
--   Evidence
--   Dependencies
--   Scoring policies
--   Evaluation history
--   Portfolio budgets
--   Selection decisions
--   Scenario analysis
--   Audit records
--
-- Formula:
--   (Reach * Impact * Confidence / 100) / Effort
--
-- Scores are stored with sufficient precision.
-- The database separates raw estimates from calculated decisions.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS rice;

SET search_path TO rice, public;

-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

CREATE TYPE opportunity_status AS ENUM (
    'draft',
    'submitted',
    'evaluated',
    'approved',
    'deferred',
    'rejected',
    'archived'
);

CREATE TYPE evidence_status AS ENUM (
    'missing',
    'unverified',
    'verified',
    'rejected'
);

CREATE TYPE decision_status AS ENUM (
    'accept',
    'review',
    'defer',
    'reject'
);

CREATE TYPE priority_level AS ENUM (
    'high',
    'medium',
    'low'
);

CREATE TYPE scenario_type AS ENUM (
    'optimistic',
    'baseline',
    'pessimistic',
    'custom'
);

-- ------------------------------------------------------------
-- CORE ENTITIES
-- ------------------------------------------------------------

CREATE TABLE teams (
    team_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id BIGINT REFERENCES teams(team_id),
    email VARCHAR(254) NOT NULL UNIQUE,
    display_name VARCHAR(120) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunities (
    opportunity_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    opportunity_key VARCHAR(30) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category VARCHAR(80) NOT NULL,
    owner_id BIGINT NOT NULL REFERENCES users(user_id),
    status opportunity_status NOT NULL DEFAULT 'draft',
    measurement_period VARCHAR(40) NOT NULL DEFAULT 'monthly',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT opportunity_key_nonempty
        CHECK (length(trim(opportunity_key)) > 0),

    CONSTRAINT opportunity_title_nonempty
        CHECK (length(trim(title)) > 0),

    CONSTRAINT opportunity_period_nonempty
        CHECK (length(trim(measurement_period)) > 0)
);

CREATE TABLE opportunity_estimates (
    estimate_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,

    version INTEGER NOT NULL,
    reach NUMERIC(16,2) NOT NULL,
    impact NUMERIC(8,3) NOT NULL,
    confidence NUMERIC(5,2) NOT NULL,
    effort_person_months NUMERIC(10,2) NOT NULL,
    strategic_value NUMERIC(8,3) NOT NULL DEFAULT 0,

    created_by BIGINT NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_estimate_version
        UNIQUE (opportunity_id, version),

    CONSTRAINT valid_estimate_version
        CHECK (version > 0),

    CONSTRAINT nonnegative_reach
        CHECK (reach >= 0),

    CONSTRAINT positive_impact
        CHECK (impact > 0),

    CONSTRAINT valid_confidence
        CHECK (confidence BETWEEN 0 AND 100),

    CONSTRAINT positive_effort
        CHECK (effort_person_months > 0),

    CONSTRAINT nonnegative_strategic_value
        CHECK (strategic_value >= 0)
);

CREATE TABLE evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,

    evidence_type VARCHAR(80) NOT NULL,
    evidence_reference TEXT NOT NULL,
    status evidence_status NOT NULL DEFAULT 'unverified',
    verified_by BIGINT REFERENCES users(user_id),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT evidence_reference_nonempty
        CHECK (length(trim(evidence_reference)) > 0),

    CONSTRAINT verification_consistency
        CHECK (
            (status = 'verified' AND verified_by IS NOT NULL
             AND verified_at IS NOT NULL)
            OR
            (status <> 'verified' AND verified_at IS NULL)
        )
);

CREATE TABLE opportunity_dependencies (
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,

    depends_on_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id) ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (opportunity_id, depends_on_id),

    CONSTRAINT no_self_dependency
        CHECK (opportunity_id <> depends_on_id)
);

-- ------------------------------------------------------------
-- SCORING POLICIES
-- ------------------------------------------------------------

CREATE TABLE scoring_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name VARCHAR(120) NOT NULL UNIQUE,
    high_threshold NUMERIC(14,4) NOT NULL,
    medium_threshold NUMERIC(14,4) NOT NULL,
    minimum_confidence NUMERIC(5,2) NOT NULL,
    require_verified_evidence BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (high_threshold > medium_threshold),
    CHECK (medium_threshold >= 0),
    CHECK (minimum_confidence BETWEEN 0 AND 100)
);

CREATE TABLE evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,

    estimate_id BIGINT NOT NULL
        REFERENCES opportunity_estimates(estimate_id),

    policy_id BIGINT NOT NULL
        REFERENCES scoring_policies(policy_id),

    rice_score NUMERIC(18,4) NOT NULL,
    priority priority_level NOT NULL,
    decision decision_status NOT NULL,
    limitations TEXT[] NOT NULL DEFAULT '{}',

    evaluated_by BIGINT NOT NULL REFERENCES users(user_id),
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (rice_score >= 0),

    UNIQUE (evaluation_id, opportunity_id)
);

CREATE TABLE evaluation_scenarios (
    scenario_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    evaluation_id BIGINT NOT NULL
        REFERENCES evaluations(evaluation_id) ON DELETE CASCADE,

    scenario scenario_type NOT NULL,
    reach_factor NUMERIC(8,4) NOT NULL,
    impact_factor NUMERIC(8,4) NOT NULL,
    confidence_factor NUMERIC(8,4) NOT NULL,
    effort_factor NUMERIC(8,4) NOT NULL,
    scenario_score NUMERIC(18,4) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (reach_factor > 0),
    CHECK (impact_factor > 0),
    CHECK (confidence_factor > 0),
    CHECK (effort_factor > 0),
    CHECK (scenario_score >= 0),

    UNIQUE (evaluation_id, scenario)
);

-- ------------------------------------------------------------
-- PORTFOLIO GOVERNANCE
-- ------------------------------------------------------------

CREATE TABLE portfolios (
    portfolio_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    portfolio_name VARCHAR(120) NOT NULL UNIQUE,
    effort_budget NUMERIC(12,2) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (effort_budget >= 0),
    CHECK (period_end >= period_start)
);

CREATE TABLE portfolio_selections (
    portfolio_id BIGINT NOT NULL
        REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,

    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id),

    evaluation_id BIGINT NOT NULL,
    selected BOOLEAN NOT NULL DEFAULT FALSE,
    selection_reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (portfolio_id, opportunity_id),

    FOREIGN KEY (evaluation_id, opportunity_id)
        REFERENCES evaluations(evaluation_id, opportunity_id)
);

CREATE TABLE audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type VARCHAR(60) NOT NULL,
    entity_id BIGINT NOT NULL,
    action VARCHAR(60) NOT NULL,
    actor_id BIGINT REFERENCES users(user_id),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- INDEXES
-- ------------------------------------------------------------

CREATE INDEX idx_opportunities_status
    ON opportunities(status, updated_at DESC);

CREATE INDEX idx_opportunities_owner
    ON opportunities(owner_id, created_at DESC);

CREATE INDEX idx_estimates_opportunity_version
    ON opportunity_estimates(opportunity_id, version DESC);

CREATE INDEX idx_evaluations_score
    ON evaluations(rice_score DESC, evaluated_at DESC);

CREATE INDEX idx_evaluations_decision
    ON evaluations(decision, evaluated_at DESC);

CREATE INDEX idx_evidence_status
    ON evidence(opportunity_id, status);

CREATE INDEX idx_dependencies_reverse
    ON opportunity_dependencies(depends_on_id);

CREATE INDEX idx_audit_entity
    ON audit_log(entity_type, entity_id, occurred_at DESC);

CREATE INDEX idx_audit_details
    ON audit_log USING GIN(details);

-- ------------------------------------------------------------
-- UPDATED TIMESTAMP TRIGGER
-- ------------------------------------------------------------

CREATE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_opportunity_updated
BEFORE UPDATE ON opportunities
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

-- ------------------------------------------------------------
-- AUDIT TRIGGER
-- ------------------------------------------------------------

CREATE FUNCTION audit_opportunity_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_log (
        entity_type,
        entity_id,
        action,
        details
    )
    VALUES (
        'opportunity',
        NEW.opportunity_id,
        TG_OP,
        jsonb_build_object(
            'key', NEW.opportunity_key,
            'status', NEW.status,
            'title', NEW.title
        )
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_opportunity_audit
AFTER INSERT OR UPDATE ON opportunities
FOR EACH ROW
EXECUTE FUNCTION audit_opportunity_changes();

-- ------------------------------------------------------------
-- RICE CALCULATION FUNCTION
-- ------------------------------------------------------------

CREATE FUNCTION calculate_rice_score(
    p_reach NUMERIC,
    p_impact NUMERIC,
    p_confidence NUMERIC,
    p_effort NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_reach < 0 THEN
        RAISE EXCEPTION 'Reach cannot be negative';
    END IF;

    IF p_impact <= 0 THEN
        RAISE EXCEPTION 'Impact must be positive';
    END IF;

    IF p_confidence < 0 OR p_confidence > 100 THEN
        RAISE EXCEPTION 'Confidence must be between 0 and 100';
    END IF;

    IF p_effort <= 0 THEN
        RAISE EXCEPTION 'Effort must be positive';
    END IF;

    RETURN ROUND(
        (p_reach * p_impact * p_confidence / 100.0) / p_effort,
        4
    );
END;
$$;

-- ------------------------------------------------------------
-- DEPENDENCY CYCLE VALIDATION
-- ------------------------------------------------------------

CREATE FUNCTION prevent_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        WITH RECURSIVE dependency_tree(id) AS (
            SELECT NEW.depends_on_id

            UNION

            SELECT d.depends_on_id
            FROM opportunity_dependencies d
            JOIN dependency_tree t
                ON d.opportunity_id = t.id
        )
        SELECT 1
        FROM dependency_tree
        WHERE id = NEW.opportunity_id
    ) THEN
        RAISE EXCEPTION
            'Dependency cycle detected for opportunity %',
            NEW.opportunity_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_dependency_cycle
BEFORE INSERT OR UPDATE ON opportunity_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_dependency_cycle();

-- ------------------------------------------------------------
-- EVALUATION PROCEDURE
-- ------------------------------------------------------------

CREATE PROCEDURE evaluate_opportunity(
    p_opportunity_id BIGINT,
    p_policy_id BIGINT,
    p_user_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_estimate opportunity_estimates%ROWTYPE;
    v_policy scoring_policies%ROWTYPE;
    v_score NUMERIC(18,4);
    v_priority priority_level;
    v_decision decision_status;
    v_limitations TEXT[] := '{}';
    v_evidence_verified BOOLEAN;
    v_evidence_exists BOOLEAN;
    v_evaluation_id BIGINT;
BEGIN
    SELECT *
    INTO v_estimate
    FROM opportunity_estimates
    WHERE opportunity_id = p_opportunity_id
    ORDER BY version DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No estimates exist for opportunity %',
            p_opportunity_id;
    END IF;

    SELECT *
    INTO v_policy
    FROM scoring_policies
    WHERE policy_id = p_policy_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active scoring policy not found';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM users
        WHERE user_id = p_user_id AND active = TRUE
    ) THEN
        RAISE EXCEPTION 'Evaluator is inactive or unknown';
    END IF;

    v_score := calculate_rice_score(
        v_estimate.reach,
        v_estimate.impact,
        v_estimate.confidence,
        v_estimate.effort_person_months
    );

    SELECT
        COUNT(*) > 0,
        COALESCE(
            BOOL_AND(status = 'verified'),
            FALSE
        )
    INTO v_evidence_exists, v_evidence_verified
    FROM evidence
    WHERE opportunity_id = p_opportunity_id;

    IF v_estimate.confidence < v_policy.minimum_confidence THEN
        v_limitations := array_append(
            v_limitations,
            'Confidence below policy threshold'
        );
    END IF;

    IF v_estimate.reach = 0 THEN
        v_limitations := array_append(
            v_limitations,
            'Zero measurable reach'
        );
    END IF;

    IF NOT v_evidence_exists THEN
        v_limitations := array_append(
            v_limitations,
            'Evidence missing'
        );
    ELSIF NOT v_evidence_verified THEN
        v_limitations := array_append(
            v_limitations,
            'Evidence is not fully verified'
        );
    END IF;

    IF v_score >= v_policy.high_threshold THEN
        v_priority := 'high';
    ELSIF v_score >= v_policy.medium_threshold THEN
        v_priority := 'medium';
    ELSE
        v_priority := 'low';
    END IF;

    IF (
        v_estimate.confidence < v_policy.minimum_confidence
        OR NOT v_evidence_exists
        OR (
            v_policy.require_verified_evidence
            AND NOT v_evidence_verified
        )
    ) THEN
        v_decision := 'review';
    ELSIF v_score >= v_policy.high_threshold THEN
        v_decision := 'accept';
    ELSIF v_score >= v_policy.medium_threshold THEN
        v_decision := 'review';
    ELSE
        v_decision := 'defer';
    END IF;

    INSERT INTO evaluations (
        opportunity_id,
        estimate_id,
        policy_id,
        rice_score,
        priority,
        decision,
        limitations,
        evaluated_by
    )
    VALUES (
        p_opportunity_id,
        v_estimate.estimate_id,
        p_policy_id,
        v_score,
        v_priority,
        v_decision,
        v_limitations,
        p_user_id
    )
    RETURNING evaluation_id INTO v_evaluation_id;

    UPDATE opportunities
    SET status = 'evaluated'
    WHERE opportunity_id = p_opportunity_id;

    INSERT INTO audit_log (
        entity_type,
        entity_id,
        action,
        actor_id,
        details
    )
    VALUES (
        'evaluation',
        v_evaluation_id,
        'EVALUATED',
        p_user_id,
        jsonb_build_object(
            'score', v_score,
            'priority', v_priority,
            'decision', v_decision,
            'limitations', v_limitations
        )
    );
END;
$$;

-- ------------------------------------------------------------
-- PORTFOLIO BUDGET VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE FUNCTION enforce_portfolio_budget()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_budget NUMERIC(12,2);
    v_total NUMERIC(12,2);
    v_new_effort NUMERIC(12,2);
BEGIN
    IF NEW.selected = FALSE THEN
        RETURN NEW;
    END IF;

    SELECT effort_budget
    INTO v_budget
    FROM portfolios
    WHERE portfolio_id = NEW.portfolio_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Portfolio not found';
    END IF;

    SELECT e.effort_person_months
    INTO v_new_effort
    FROM evaluations ev
    JOIN opportunity_estimates e
        ON e.estimate_id = ev.estimate_id
    WHERE ev.evaluation_id = NEW.evaluation_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Evaluation estimate not found';
    END IF;

    SELECT COALESCE(SUM(e.effort_person_months), 0)
    INTO v_total
    FROM portfolio_selections ps
    JOIN evaluations ev
        ON ev.evaluation_id = ps.evaluation_id
    JOIN opportunity_estimates e
        ON e.estimate_id = ev.estimate_id
    WHERE ps.portfolio_id = NEW.portfolio_id
      AND ps.selected = TRUE
      AND ps.opportunity_id <> NEW.opportunity_id;

    IF v_total + v_new_effort > v_budget THEN
        RAISE EXCEPTION
            'Portfolio budget exceeded: % + % > %',
            v_total,
            v_new_effort,
            v_budget;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_portfolio_budget
BEFORE INSERT OR UPDATE ON portfolio_selections
FOR EACH ROW
EXECUTE FUNCTION enforce_portfolio_budget();

-- ------------------------------------------------------------
-- VIEWS
-- ------------------------------------------------------------

CREATE VIEW opportunity_ranking AS
SELECT
    o.opportunity_id,
    o.opportunity_key,
    o.title,
    o.category,
    o.status,
    e.evaluation_id,
    e.rice_score,
    e.priority,
    e.decision,
    e.limitations,
    e.evaluated_at,
    RANK() OVER (
        PARTITION BY o.category
        ORDER BY e.rice_score DESC
    ) AS category_rank
FROM opportunities o
JOIN LATERAL (
    SELECT *
    FROM evaluations ev
    WHERE ev.opportunity_id = o.opportunity_id
    ORDER BY ev.evaluated_at DESC, ev.evaluation_id DESC
    LIMIT 1
) e ON TRUE;

CREATE VIEW portfolio_utilization AS
SELECT
    p.portfolio_id,
    p.portfolio_name,
    p.effort_budget,
    COALESCE(
        SUM(est.effort_person_months)
        FILTER (WHERE ps.selected = TRUE),
        0
    ) AS allocated_effort,
    p.effort_budget - COALESCE(
        SUM(est.effort_person_months)
        FILTER (WHERE ps.selected = TRUE),
        0
    ) AS remaining_effort
FROM portfolios p
LEFT JOIN portfolio_selections ps
    ON ps.portfolio_id = p.portfolio_id
LEFT JOIN evaluations ev
    ON ev.evaluation_id = ps.evaluation_id
LEFT JOIN opportunity_estimates est
    ON est.estimate_id = ev.estimate_id
GROUP BY p.portfolio_id, p.portfolio_name, p.effort_budget;

-- ------------------------------------------------------------
-- SEED DATA
-- ------------------------------------------------------------

INSERT INTO teams(team_name)
VALUES
    ('Product Engineering'),
    ('Security Engineering'),
    ('Platform Operations');

INSERT INTO users(team_id, email, display_name)
VALUES
    (1, 'product@example.org', 'Product Manager'),
    (2, 'security@example.org', 'Security Lead'),
    (3, 'operations@example.org', 'Operations Lead'),
    (1, 'analyst@example.org', 'Product Analyst');

INSERT INTO scoring_policies(
    policy_name,
    high_threshold,
    medium_threshold,
    minimum_confidence,
    require_verified_evidence
)
VALUES (
    'Standard Product Policy',
    100,
    30,
    40,
    TRUE
);

INSERT INTO opportunities(
    opportunity_key,
    title,
    description,
    category,
    owner_id
)
VALUES
(
    'P001',
    'Self-service account recovery',
    'Reduce account recovery support requests.',
    'Security',
    2
),
(
    'P002',
    'Mobile dashboard redesign',
    'Improve mobile dashboard usability.',
    'Product',
    1
),
(
    'P003',
    'Automated incident notifications',
    'Reduce incident response delays.',
    'Reliability',
    3
),
(
    'P004',
    'Experimental recommendation engine',
    'Test personalized recommendations.',
    'Experiment',
    1
),
(
    'P005',
    'Accessibility improvements',
    'Address accessibility audit findings.',
    'Accessibility',
    1
),
(
    'P006',
    'Legacy reporting migration',
    'Replace an obsolete reporting workflow.',
    'Operations',
    3
);

INSERT INTO opportunity_estimates(
    opportunity_id,
    version,
    reach,
    impact,
    confidence,
    effort_person_months,
    strategic_value,
    created_by
)
VALUES
(1, 1, 12000, 2.0, 90, 3.0, 8, 1),
(2, 1, 8500, 1.0, 85, 4.0, 2, 4),
(3, 1, 15000, 1.5, 95, 2.0, 9, 3),
(4, 1, 5000, 3.0, 35, 8.0, 5, 4),
(5, 1, 6000, 1.5, 95, 2.5, 7, 1),
(6, 1, 0, 1.0, 80, 3.0, 1, 3);

INSERT INTO evidence(
    opportunity_id,
    evidence_type,
    evidence_reference,
    status,
    verified_by,
    verified_at
)
VALUES
(
    1, 'Support analysis', 'support-ticket-study',
    'verified', 2, now()
),
(
    2, 'Customer survey', 'mobile-usability-survey',
    'verified', 1, now()
),
(
    3, 'Incident analysis', 'incident-log-study',
    'verified', 3, now()
),
(
    4, 'Pilot study', 'recommendation-pilot',
    'unverified', NULL, NULL
),
(
    5, 'Accessibility audit', 'accessibility-audit',
    'verified', 1, now()
);

INSERT INTO opportunity_dependencies(
    opportunity_id,
    depends_on_id
)
VALUES
(3, 1);

INSERT INTO portfolios(
    portfolio_name,
    effort_budget,
    period_start,
    period_end,
    created_by
)
VALUES (
    'Q1 Product Portfolio',
    12.0,
    DATE '2027-01-01',
    DATE '2027-03-31',
    1
);

-- ------------------------------------------------------------
-- EVALUATION TRANSACTION
-- ------------------------------------------------------------

DO $$
DECLARE
    v_policy_id BIGINT;
    v_user_id BIGINT;
    v_opportunity_id BIGINT;
BEGIN
    SELECT policy_id
    INTO v_policy_id
    FROM scoring_policies
    WHERE policy_name = 'Standard Product Policy';

    FOR v_opportunity_id IN
        SELECT opportunity_id
        FROM opportunities
        ORDER BY opportunity_id
    LOOP
        CALL evaluate_opportunity(
            v_opportunity_id,
            v_policy_id,
            1
        );
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- SCENARIO ANALYSIS
-- ------------------------------------------------------------

INSERT INTO evaluation_scenarios(
    evaluation_id,
    scenario,
    reach_factor,
    impact_factor,
    confidence_factor,
    effort_factor,
    scenario_score
)
SELECT
    ev.evaluation_id,
    scenario_data.scenario,
    scenario_data.reach_factor,
    scenario_data.impact_factor,
    scenario_data.confidence_factor,
    scenario_data.effort_factor,
    calculate_rice_score(
        est.reach * scenario_data.reach_factor,
        est.impact * scenario_data.impact_factor,
        LEAST(
            100,
            est.confidence * scenario_data.confidence_factor
        ),
        est.effort_person_months * scenario_data.effort_factor
    )
FROM evaluations ev
JOIN opportunity_estimates est
    ON est.estimate_id = ev.estimate_id
CROSS JOIN (
    VALUES
        ('optimistic'::scenario_type, 1.2, 1.2, 1.1, 0.9),
        ('baseline'::scenario_type, 1.0, 1.0, 1.0, 1.0),
        ('pessimistic'::scenario_type, 0.8, 0.8, 0.8, 1.2)
) AS scenario_data(
    scenario,
    reach_factor,
    impact_factor,
    confidence_factor,
    effort_factor
);

-- ------------------------------------------------------------
-- REPORTING QUERIES
-- ------------------------------------------------------------

-- 1. Ranked opportunities.
SELECT *
FROM opportunity_ranking
ORDER BY rice_score DESC;

-- 2. Category-level score aggregation.
SELECT
    o.category,
    COUNT(*) AS opportunity_count,
    ROUND(AVG(e.rice_score), 2) AS average_score,
    ROUND(MAX(e.rice_score), 2) AS highest_score
FROM opportunities o
JOIN evaluations e
    ON e.opportunity_id = o.opportunity_id
GROUP BY o.category
ORDER BY average_score DESC;

-- 3. Evidence validation.
SELECT
    o.opportunity_key,
    o.title,
    COUNT(ev.evidence_id) AS evidence_count,
    COUNT(ev.evidence_id)
        FILTER (WHERE ev.status = 'verified') AS verified_count
FROM opportunities o
LEFT JOIN evidence ev
    ON ev.opportunity_id = o.opportunity_id
GROUP BY o.opportunity_id
ORDER BY o.opportunity_key;

-- 4. Identify items requiring further review.
SELECT
    o.opportunity_key,
    o.title,
    e.rice_score,
    e.limitations
FROM evaluations e
JOIN opportunities o
    ON o.opportunity_id = e.opportunity_id
WHERE e.decision = 'review'
ORDER BY e.rice_score DESC;

-- 5. Scenario sensitivity.
SELECT
    o.opportunity_key,
    o.title,
    MAX(s.scenario_score)
        FILTER (WHERE s.scenario = 'optimistic') AS optimistic,
    MAX(s.scenario_score)
        FILTER (WHERE s.scenario = 'baseline') AS baseline,
    MAX(s.scenario_score)
        FILTER (WHERE s.scenario = 'pessimistic') AS pessimistic
FROM evaluation_scenarios s
JOIN evaluations e
    ON e.evaluation_id = s.evaluation_id
JOIN opportunities o
    ON o.opportunity_id = e.opportunity_id
GROUP BY o.opportunity_key, o.title
ORDER BY baseline DESC;

-- 6. Portfolio utilization.
SELECT *
FROM portfolio_utilization;

-- 7. Latest estimate using a CTE.
WITH latest_estimates AS (
    SELECT DISTINCT ON (opportunity_id)
        opportunity_id,
        reach,
        impact,
        confidence,
        effort_person_months,
        version
    FROM opportunity_estimates
    ORDER BY opportunity_id, version DESC
)
SELECT
    o.opportunity_key,
    o.title,
    le.version,
    calculate_rice_score(
        le.reach,
        le.impact,
        le.confidence,
        le.effort_person_months
    ) AS current_score
FROM latest_estimates le
JOIN opportunities o
    ON o.opportunity_id = le.opportunity_id
ORDER BY current_score DESC;

-- ------------------------------------------------------------
-- PORTFOLIO SELECTION
-- ------------------------------------------------------------

-- The selected records must satisfy the portfolio budget.
-- The trigger serializes competing selections through a portfolio
-- row lock. This prevents concurrent transactions from independently
-- allocating the same remaining budget.

INSERT INTO portfolio_selections(
    portfolio_id,
    opportunity_id,
    evaluation_id,
    selected,
    selection_reason
)
SELECT
    1,
    o.opportunity_id,
    e.evaluation_id,
    TRUE,
    'Eligible based on verified evidence and policy evaluation'
FROM opportunities o
JOIN LATERAL (
    SELECT *
    FROM evaluations ev
    WHERE ev.opportunity_id = o.opportunity_id
    ORDER BY ev.evaluated_at DESC, ev.evaluation_id DESC
    LIMIT 1
) e ON TRUE
WHERE e.decision = 'accept'
  AND NOT EXISTS (
      SELECT 1
      FROM portfolio_selections ps
      WHERE ps.portfolio_id = 1
        AND ps.opportunity_id = o.opportunity_id
  )
ORDER BY e.rice_score DESC
LIMIT 2;

-- ------------------------------------------------------------
-- ELIGIBILITY DETERMINATION
-- ------------------------------------------------------------

SELECT
    o.opportunity_key,
    o.title,
    e.rice_score,
    e.decision,
    (
        e.decision = 'accept'
        AND cardinality(e.limitations) = 0
    ) AS policy_eligible,
    (
        e.decision = 'accept'
        AND est.effort_person_months <= p.effort_budget
    ) AS individually_within_budget
FROM opportunities o
JOIN evaluations e
    ON e.opportunity_id = o.opportunity_id
JOIN opportunity_estimates est
    ON est.estimate_id = e.estimate_id
CROSS JOIN portfolios p
WHERE p.portfolio_id = 1
ORDER BY e.rice_score DESC;

-- ------------------------------------------------------------
-- FAILURE CASES
-- ------------------------------------------------------------

-- Invalid scoring input is rejected by the function.
-- Run independently to observe the exception:
-- SELECT calculate_rice_score(-1, 2, 80, 3);

-- Invalid confidence is rejected by the table constraint.
-- INSERT INTO opportunity_estimates(
--     opportunity_id, version, reach, impact,
--     confidence, effort_person_months, created_by
-- ) VALUES (1, 99, 100, 2, 150, 2, 1);

-- Missing dependencies are rejected by the foreign key.
-- Dependency cycles are rejected by the recursive trigger.

-- A budget overflow is rejected by the portfolio trigger.

-- ------------------------------------------------------------
-- FINAL DATABASE VALIDATION
-- ------------------------------------------------------------

SELECT
    'Opportunity count' AS metric,
    COUNT(*)::TEXT AS value
FROM opportunities

UNION ALL

SELECT
    'Evaluation count',
    COUNT(*)::TEXT
FROM evaluations

UNION ALL

SELECT
    'Verified evidence count',
    COUNT(*)::TEXT
FROM evidence
WHERE status = 'verified';

COMMIT;
