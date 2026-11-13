-- ============================================================
-- VALUE VS EFFORT: OPPORTUNITY MANAGEMENT DATABASE
-- PostgreSQL 15+
--
-- Models:
-- 1. Value estimation and effort estimation
-- 2. Opportunity matrix and prioritization
-- 3. Dependencies and capacity planning
-- 4. Repositories, branches and commits
-- 5. Pull Requests and review decisions
-- 6. Status checks and branch protection
-- 7. Merge eligibility and audit history
-- ============================================================

CREATE SCHEMA IF NOT EXISTS prioritization;

SET search_path TO prioritization, public;

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE risk_level AS ENUM (
    'LOW', 'MEDIUM', 'HIGH'
);

CREATE TYPE opportunity_priority AS ENUM (
    'QUICK_WIN',
    'STRATEGIC',
    'FILL_IN',
    'LOW_PRIORITY'
);

CREATE TYPE pull_request_state AS ENUM (
    'DRAFT', 'OPEN', 'MERGED', 'CLOSED'
);

CREATE TYPE review_state AS ENUM (
    'APPROVED',
    'CHANGES_REQUESTED',
    'COMMENTED',
    'DISMISSED'
);

CREATE TYPE check_state AS ENUM (
    'PENDING', 'PASSED', 'FAILED'
);

CREATE TYPE merge_method AS ENUM (
    'MERGE_COMMIT',
    'SQUASH',
    'REBASE'
);

-- ============================================================
-- PORTFOLIO MANAGEMENT
-- ============================================================

CREATE TABLE opportunities (
    opportunity_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    opportunity_code VARCHAR(30) NOT NULL UNIQUE,
    opportunity_name VARCHAR(150) NOT NULL,
    description TEXT,

    customer_impact NUMERIC(5,2) NOT NULL,
    strategic_alignment NUMERIC(5,2) NOT NULL,
    revenue_impact NUMERIC(5,2) NOT NULL,
    urgency NUMERIC(5,2) NOT NULL,

    value_confidence NUMERIC(5,2) NOT NULL,
    effort_confidence NUMERIC(5,2) NOT NULL,

    effort_low NUMERIC(12,2) NOT NULL,
    effort_expected NUMERIC(12,2) NOT NULL,
    effort_high NUMERIC(12,2) NOT NULL,

    risk risk_level NOT NULL DEFAULT 'MEDIUM',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_customer_impact
        CHECK (customer_impact BETWEEN 1 AND 5),

    CONSTRAINT valid_strategic_alignment
        CHECK (strategic_alignment BETWEEN 1 AND 5),

    CONSTRAINT valid_revenue_impact
        CHECK (revenue_impact BETWEEN 1 AND 5),

    CONSTRAINT valid_urgency
        CHECK (urgency BETWEEN 1 AND 5),

    CONSTRAINT valid_value_confidence
        CHECK (value_confidence BETWEEN 1 AND 5),

    CONSTRAINT valid_effort_confidence
        CHECK (effort_confidence BETWEEN 1 AND 5),

    CONSTRAINT valid_effort_range
        CHECK (
            effort_low >= 0
            AND effort_expected > 0
            AND effort_low <= effort_expected
            AND effort_expected <= effort_high
        ),

    CONSTRAINT valid_opportunity_name
        CHECK (length(trim(opportunity_name)) > 0)
);

CREATE TABLE opportunity_dependencies (
    opportunity_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id)
        ON DELETE CASCADE,

    depends_on_id BIGINT NOT NULL
        REFERENCES opportunities(opportunity_id)
        ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (opportunity_id, depends_on_id),

    CONSTRAINT no_self_dependency
        CHECK (opportunity_id <> depends_on_id)
);

CREATE TABLE prioritization_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_name VARCHAR(100) NOT NULL UNIQUE,

    customer_weight NUMERIC(6,4) NOT NULL,
    strategic_weight NUMERIC(6,4) NOT NULL,
    revenue_weight NUMERIC(6,4) NOT NULL,
    urgency_weight NUMERIC(6,4) NOT NULL,

    quick_win_threshold NUMERIC(12,4) NOT NULL,
    strategic_threshold NUMERIC(12,4) NOT NULL,

    low_risk_factor NUMERIC(5,4) NOT NULL,
    medium_risk_factor NUMERIC(5,4) NOT NULL,
    high_risk_factor NUMERIC(5,4) NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_weights CHECK (
        customer_weight >= 0
        AND strategic_weight >= 0
        AND revenue_weight >= 0
        AND urgency_weight >= 0
        AND customer_weight + strategic_weight +
            revenue_weight + urgency_weight = 1
    ),

    CONSTRAINT valid_thresholds CHECK (
        quick_win_threshold > strategic_threshold
        AND strategic_threshold >= 0
    ),

    CONSTRAINT valid_risk_factors CHECK (
        low_risk_factor BETWEEN 0 AND 1
        AND medium_risk_factor BETWEEN 0 AND 1
        AND high_risk_factor BETWEEN 0 AND 1
    )
);

INSERT INTO prioritization_policies (
    policy_name,
    customer_weight,
    strategic_weight,
    revenue_weight,
    urgency_weight,
    quick_win_threshold,
    strategic_threshold,
    low_risk_factor,
    medium_risk_factor,
    high_risk_factor
)
VALUES (
    'STANDARD',
    0.35, 0.30, 0.20, 0.15,
    20, 8,
    1.00, 0.85, 0.65
);

-- ============================================================
-- VALUE AND EFFORT EVALUATION
-- ============================================================

CREATE OR REPLACE FUNCTION evaluate_opportunity(
    p_opportunity_id BIGINT,
    p_policy_id BIGINT DEFAULT 1
)
RETURNS TABLE (
    opportunity_code VARCHAR,
    opportunity_name VARCHAR,
    estimated_value NUMERIC,
    adjusted_value NUMERIC,
    estimated_effort NUMERIC,
    value_effort_ratio NUMERIC,
    priority opportunity_priority
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_item opportunities%ROWTYPE;
    v_policy prioritization_policies%ROWTYPE;

    v_value NUMERIC;
    v_adjusted NUMERIC;
    v_effort NUMERIC;
    v_confidence NUMERIC;
    v_risk NUMERIC;
    v_ratio NUMERIC;
    v_priority opportunity_priority;
BEGIN
    SELECT *
    INTO v_item
    FROM opportunities
    WHERE opportunity_id = p_opportunity_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Opportunity % does not exist',
            p_opportunity_id;
    END IF;

    SELECT *
    INTO v_policy
    FROM prioritization_policies
    WHERE policy_id = p_policy_id
      AND active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active policy % does not exist',
            p_policy_id;
    END IF;

    v_value := (
        v_item.customer_impact * v_policy.customer_weight
        + v_item.strategic_alignment * v_policy.strategic_weight
        + v_item.revenue_impact * v_policy.revenue_weight
        + v_item.urgency * v_policy.urgency_weight
    ) / 5 * 100;

    v_confidence := LEAST(
        v_item.value_confidence,
        v_item.effort_confidence
    ) / 5;

    v_risk := CASE v_item.risk
        WHEN 'LOW' THEN v_policy.low_risk_factor
        WHEN 'MEDIUM' THEN v_policy.medium_risk_factor
        WHEN 'HIGH' THEN v_policy.high_risk_factor
    END;

    v_adjusted := v_value * v_confidence * v_risk;

    v_effort := (
        v_item.effort_low
        + v_item.effort_expected
        + v_item.effort_high
    ) / 3;

    v_ratio := v_adjusted / v_effort;

    v_priority := CASE
        WHEN v_ratio >= v_policy.quick_win_threshold
            THEN 'QUICK_WIN'::opportunity_priority
        WHEN v_ratio >= v_policy.strategic_threshold
            THEN 'STRATEGIC'::opportunity_priority
        WHEN v_adjusted >= 25
            THEN 'FILL_IN'::opportunity_priority
        ELSE 'LOW_PRIORITY'::opportunity_priority
    END;

    RETURN QUERY
    SELECT
        v_item.opportunity_code,
        v_item.opportunity_name,
        ROUND(v_value, 2),
        ROUND(v_adjusted, 2),
        ROUND(v_effort, 2),
        ROUND(v_ratio, 2),
        v_priority;
END;
$$;

CREATE OR REPLACE VIEW opportunity_matrix AS
SELECT
    o.opportunity_id,
    o.opportunity_code,
    o.opportunity_name,
    e.estimated_value,
    e.adjusted_value,
    e.estimated_effort,
    e.value_effort_ratio,
    e.priority,
    o.risk,
    o.value_confidence,
    o.effort_confidence
FROM opportunities o
CROSS JOIN LATERAL evaluate_opportunity(
    o.opportunity_id,
    1
) e;

-- ============================================================
-- DEPENDENCY VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cycle BOOLEAN;
BEGIN
    IF NEW.opportunity_id = NEW.depends_on_id THEN
        RAISE EXCEPTION 'Self-dependency is prohibited.';
    END IF;

    WITH RECURSIVE dependency_path(id) AS (
        SELECT NEW.depends_on_id

        UNION

        SELECT d.depends_on_id
        FROM opportunity_dependencies d
        JOIN dependency_path p
          ON d.opportunity_id = p.id
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE id = NEW.opportunity_id
    )
    INTO v_cycle;

    IF v_cycle THEN
        RAISE EXCEPTION
            'Dependency cycle detected for opportunity %',
            NEW.opportunity_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER prevent_dependency_cycle
BEFORE INSERT OR UPDATE
ON opportunity_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_cycle();

-- ============================================================
-- CAPACITY PLANNING
-- ============================================================

CREATE OR REPLACE FUNCTION allocate_opportunities(
    p_capacity NUMERIC
)
RETURNS TABLE (
    opportunity_code VARCHAR,
    opportunity_name VARCHAR,
    estimated_effort NUMERIC,
    priority opportunity_priority
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_selected BIGINT[] := ARRAY[]::BIGINT[];
    v_candidate RECORD;
    v_bundle BIGINT[];
    v_required NUMERIC;
    v_remaining NUMERIC := p_capacity;
    v_id BIGINT;
BEGIN
    IF p_capacity IS NULL OR p_capacity < 0 THEN
        RAISE EXCEPTION 'Capacity must be non-negative.';
    END IF;

    FOR v_candidate IN
        SELECT *
        FROM opportunity_matrix
        ORDER BY value_effort_ratio DESC,
                 adjusted_value DESC
    LOOP
        -- Resolve the full transitive dependency bundle.
        WITH RECURSIVE dependency_bundle(id) AS (
            SELECT v_candidate.opportunity_id

            UNION

            SELECT d.depends_on_id
            FROM opportunity_dependencies d
            JOIN dependency_bundle b
              ON d.opportunity_id = b.id
        )
        SELECT ARRAY(
            SELECT id FROM dependency_bundle
        )
        INTO v_bundle;

        SELECT COALESCE(SUM(
            (o.effort_low + o.effort_expected + o.effort_high) / 3
        ), 0)
        INTO v_required
        FROM opportunities o
        WHERE o.opportunity_id = ANY(v_bundle)
          AND NOT (o.opportunity_id = ANY(v_selected));

        IF v_required <= v_remaining THEN
            FOREACH v_id IN ARRAY v_bundle LOOP
                IF NOT (v_id = ANY(v_selected)) THEN
                    v_selected := array_append(v_selected, v_id);
                END IF;
            END LOOP;

            v_remaining := v_remaining - v_required;
        END IF;
    END LOOP;

    RETURN QUERY
    SELECT
        m.opportunity_code,
        m.opportunity_name,
        m.estimated_effort,
        m.priority
    FROM opportunity_matrix m
    WHERE m.opportunity_id = ANY(v_selected)
    ORDER BY m.value_effort_ratio DESC;
END;
$$;

-- ============================================================
-- REPOSITORY GOVERNANCE DOMAIN
-- ============================================================

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name VARCHAR(150) NOT NULL UNIQUE,
    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    user_id VARCHAR(100) NOT NULL,

    role VARCHAR(30) NOT NULL
        CHECK (role IN (
            'ADMIN',
            'MAINTAINER',
            'DEVELOPER',
            'REVIEWER'
        )),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (repository_id, user_id)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    branch_name VARCHAR(150) NOT NULL,

    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    head_commit_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (repository_id, branch_name),
    UNIQUE (branch_id, repository_id)
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    commit_hash VARCHAR(64) NOT NULL,
    author_id VARCHAR(100) NOT NULL,
    commit_message TEXT NOT NULL,

    parent_commit_id BIGINT
        REFERENCES commits(commit_id)
        ON DELETE SET NULL,

    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (repository_id, commit_hash),
    UNIQUE (commit_id, repository_id)
);

ALTER TABLE branches
ADD CONSTRAINT branch_head_commit_fk
FOREIGN KEY (head_commit_id, repository_id)
REFERENCES commits(commit_id, repository_id);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id),

    source_branch_id BIGINT NOT NULL,
    target_branch_id BIGINT NOT NULL,

    title VARCHAR(200) NOT NULL,
    description TEXT,

    state pull_request_state NOT NULL DEFAULT 'OPEN',

    is_source_updated BOOLEAN NOT NULL DEFAULT FALSE,
    has_merge_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    linear_history BOOLEAN NOT NULL DEFAULT TRUE,

    merge_commit_id BIGINT
        REFERENCES commits(commit_id),

    merge_strategy merge_method,

    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMPTZ,

    FOREIGN KEY (source_branch_id, repository_id)
        REFERENCES branches(branch_id, repository_id),

    FOREIGN KEY (target_branch_id, repository_id)
        REFERENCES branches(branch_id, repository_id),

    CHECK (source_branch_id <> target_branch_id),

    CHECK (
        (state = 'MERGED'
         AND merged_at IS NOT NULL
         AND merge_commit_id IS NOT NULL
         AND merge_strategy IS NOT NULL)
        OR
        (state <> 'MERGED'
         AND merged_at IS NULL
         AND merge_commit_id IS NULL
         AND merge_strategy IS NULL)
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),

    PRIMARY KEY (pull_request_id, commit_id)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    reviewer_id VARCHAR(100) NOT NULL,

    review_state review_state NOT NULL,

    eligible BOOLEAN NOT NULL DEFAULT TRUE,
    stale BOOLEAN NOT NULL DEFAULT FALSE,

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (review_id, pull_request_id)
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,

    file_path TEXT NOT NULL,
    line_number INTEGER,

    comment_body TEXT NOT NULL,

    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,

    parent_comment_id BIGINT
        REFERENCES review_comments(comment_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (length(trim(comment_body)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,

    check_name VARCHAR(100) NOT NULL,
    check_state check_state NOT NULL,

    commit_hash VARCHAR(64) NOT NULL,

    completed_at TIMESTAMPTZ,

    UNIQUE (pull_request_id, check_name),

    CHECK (
        (check_state = 'PENDING' AND completed_at IS NULL)
        OR
        (check_state <> 'PENDING' AND completed_at IS NOT NULL)
    )
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    branch_id BIGINT NOT NULL,

    required_approvals INTEGER NOT NULL DEFAULT 1,

    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    require_updated_source BOOLEAN NOT NULL DEFAULT TRUE,

    prohibit_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_branch_deletion BOOLEAN NOT NULL DEFAULT TRUE,

    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    prohibit_draft_merge BOOLEAN NOT NULL DEFAULT TRUE,

    administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (branch_id, repository_id)
        REFERENCES branches(branch_id, repository_id),

    UNIQUE (branch_id),

    CHECK (required_approvals >= 0)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,

    check_name VARCHAR(100) NOT NULL,

    PRIMARY KEY (policy_id, check_name)
);

CREATE TABLE merge_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id),

    decision VARCHAR(30) NOT NULL
        CHECK (decision IN (
            'ELIGIBLE',
            'BLOCKED',
            'MERGED'
        )),

    evaluated_by VARCHAR(100) NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- REVIEWER ELIGIBILITY AND APPROVALS
-- ============================================================

CREATE OR REPLACE FUNCTION eligible_approval_count(
    p_pull_request_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM (
        SELECT DISTINCT ON (r.reviewer_id)
            r.reviewer_id,
            r.review_state,
            r.eligible,
            r.stale
        FROM reviews r
        WHERE r.pull_request_id = p_pull_request_id
        ORDER BY r.reviewer_id, r.submitted_at DESC, r.review_id DESC
    ) latest
    JOIN pull_requests pr
      ON pr.pull_request_id = p_pull_request_id
    JOIN repository_members rm
      ON rm.repository_id = pr.repository_id
     AND rm.user_id = latest.reviewer_id
     AND rm.active = TRUE
     AND rm.role IN ('ADMIN', 'MAINTAINER', 'REVIEWER')
    WHERE latest.eligible = TRUE
      AND latest.stale = FALSE
      AND latest.review_state = 'APPROVED';
$$;

CREATE OR REPLACE FUNCTION has_active_change_request(
    p_pull_request_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM (
            SELECT DISTINCT ON (reviewer_id)
                reviewer_id,
                review_state,
                eligible,
                stale
            FROM reviews
            WHERE pull_request_id = p_pull_request_id
            ORDER BY reviewer_id, submitted_at DESC, review_id DESC
        ) latest
        JOIN pull_requests pr
          ON pr.pull_request_id = p_pull_request_id
        JOIN repository_members rm
          ON rm.repository_id = pr.repository_id
         AND rm.user_id = latest.reviewer_id
         AND rm.active = TRUE
        WHERE latest.eligible
          AND NOT latest.stale
          AND latest.review_state = 'CHANGES_REQUESTED'
    );
$$;

-- ============================================================
-- MERGE ELIGIBILITY FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    blockers TEXT[],
    approval_count INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_pr pull_requests%ROWTYPE;
    v_policy branch_protection_policies%ROWTYPE;

    v_blockers TEXT[] := ARRAY[]::TEXT[];
    v_approvals INTEGER := 0;
    v_unresolved BOOLEAN;
    v_missing_check BOOLEAN;
BEGIN
    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request % does not exist',
            p_pull_request_id;
    END IF;

    IF v_pr.state <> 'OPEN' THEN
        v_blockers := array_append(
            v_blockers, 'Pull Request is not open.'
        );
    END IF;

    IF v_pr.has_merge_conflicts THEN
        v_blockers := array_append(
            v_blockers, 'Merge conflicts exist.'
        );
    END IF;

    SELECT *
    INTO v_policy
    FROM branch_protection_policies
    WHERE branch_id = v_pr.target_branch_id;

    IF FOUND THEN
        IF v_pr.state = 'DRAFT'
           AND v_policy.prohibit_draft_merge THEN
            v_blockers := array_append(
                v_blockers, 'Draft Pull Request cannot merge.'
            );
        END IF;

        IF v_policy.require_updated_source
           AND NOT v_pr.is_source_updated THEN
            v_blockers := array_append(
                v_blockers, 'Source branch is not synchronized.'
            );
        END IF;

        IF v_policy.require_linear_history
           AND NOT v_pr.linear_history THEN
            v_blockers := array_append(
                v_blockers, 'Linear history requirement failed.'
            );
        END IF;

        SELECT EXISTS (
            SELECT 1
            FROM review_comments rc
            JOIN reviews r
              ON r.review_id = rc.review_id
            WHERE r.pull_request_id = p_pull_request_id
              AND rc.is_resolved = FALSE
        )
        INTO v_unresolved;

        IF v_policy.require_resolved_conversations
           AND v_unresolved THEN
            v_blockers := array_append(
                v_blockers, 'Unresolved review conversations.'
            );
        END IF;

        v_approvals := eligible_approval_count(
            p_pull_request_id
        );

        IF v_approvals < v_policy.required_approvals THEN
            v_blockers := array_append(
                v_blockers, 'Required approvals not satisfied.'
            );
        END IF;

        IF has_active_change_request(p_pull_request_id) THEN
            v_blockers := array_append(
                v_blockers, 'Active changes-requested review exists.'
            );
        END IF;

        IF v_policy.require_status_checks THEN
            SELECT EXISTS (
                SELECT 1
                FROM required_status_checks required
                WHERE required.policy_id = v_policy.policy_id
                  AND NOT EXISTS (
                      SELECT 1
                      FROM status_checks actual
                      WHERE actual.pull_request_id = p_pull_request_id
                        AND actual.check_name = required.check_name
                        AND actual.check_state = 'PASSED'
                        AND actual.commit_hash = (
                            SELECT c.commit_hash
                            FROM branches b
                            JOIN commits c
                              ON c.commit_id = b.head_commit_id
                            WHERE b.branch_id = v_pr.source_branch_id
                        )
                  )
            )
            INTO v_missing_check;

            IF v_missing_check THEN
                v_blockers := array_append(
                    v_blockers,
                    'One or more required status checks are missing or unsuccessful.'
                );
            END IF;
        END IF;
    END IF;

    RETURN QUERY
    SELECT
        cardinality(v_blockers) = 0,
        v_blockers,
        v_approvals;
END;
$$;

-- ============================================================
-- AUDIT ELIGIBILITY DECISIONS
-- ============================================================

CREATE OR REPLACE PROCEDURE record_merge_evaluation(
    p_pull_request_id BIGINT,
    p_actor VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_decision RECORD;
BEGIN
    SELECT *
    INTO v_decision
    FROM evaluate_merge_eligibility(p_pull_request_id);

    INSERT INTO merge_audit (
        pull_request_id,
        decision,
        evaluated_by,
        details
    )
    VALUES (
        p_pull_request_id,
        CASE
            WHEN v_decision.eligible THEN 'ELIGIBLE'
            ELSE 'BLOCKED'
        END,
        p_actor,
        jsonb_build_object(
            'blockers', v_decision.blockers,
            'approval_count', v_decision.approval_count
        )
    );
END;
$$;

-- ============================================================
-- SAFE MERGE OPERATION
-- ============================================================

CREATE OR REPLACE PROCEDURE merge_pull_request(
    p_pull_request_id BIGINT,
    p_merge_commit_id BIGINT,
    p_method merge_method,
    p_actor VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pr pull_requests%ROWTYPE;
    v_decision RECORD;
BEGIN
    -- Serialize concurrent merge attempts for this Pull Request.
    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request not found.';
    END IF;

    IF v_pr.state <> 'OPEN' THEN
        RAISE EXCEPTION 'Only open Pull Requests can merge.';
    END IF;

    PERFORM 1
    FROM branches
    WHERE branch_id IN (
        v_pr.source_branch_id,
        v_pr.target_branch_id
    )
    ORDER BY branch_id
    FOR UPDATE;

    SELECT *
    INTO v_decision
    FROM evaluate_merge_eligibility(p_pull_request_id);

    IF NOT v_decision.eligible THEN
        INSERT INTO merge_audit (
            pull_request_id,
            decision,
            evaluated_by,
            details
        )
        VALUES (
            p_pull_request_id,
            'BLOCKED',
            p_actor,
            jsonb_build_object(
                'blockers', v_decision.blockers
            )
        );

        RAISE EXCEPTION
            'Merge blocked: %',
            array_to_string(v_decision.blockers, '; ');
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM commits
        WHERE commit_id = p_merge_commit_id
          AND repository_id = v_pr.repository_id
    ) THEN
        RAISE EXCEPTION
            'Merge commit must belong to the same repository.';
    END IF;

    UPDATE pull_requests
    SET
        state = 'MERGED',
        merge_commit_id = p_merge_commit_id,
        merge_strategy = p_method,
        merged_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = p_pull_request_id;

    UPDATE branches
    SET head_commit_id = p_merge_commit_id
    WHERE branch_id = v_pr.target_branch_id;

    INSERT INTO merge_audit (
        pull_request_id,
        decision,
        evaluated_by,
        details
    )
    VALUES (
        p_pull_request_id,
        'MERGED',
        p_actor,
        jsonb_build_object(
            'method', p_method,
            'commit_id', p_merge_commit_id
        )
    );
END;
$$;

-- ============================================================
-- PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_opportunities_priority_inputs
ON opportunities (
    risk,
    value_confidence,
    effort_confidence
);

CREATE INDEX idx_dependencies_reverse
ON opportunity_dependencies(depends_on_id);

CREATE INDEX idx_pull_requests_repository_state
ON pull_requests(repository_id, state);

CREATE INDEX idx_pull_requests_target
ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_reviewer_time
ON reviews(
    pull_request_id,
    reviewer_id,
    submitted_at DESC
);

CREATE INDEX idx_review_comments_unresolved
ON review_comments(review_id)
WHERE is_resolved = FALSE;

CREATE INDEX idx_status_checks_pr_name_state
ON status_checks(
    pull_request_id,
    check_name,
    check_state
);

CREATE INDEX idx_merge_audit_created
ON merge_audit(created_at DESC);

-- ============================================================
-- SAMPLE OPPORTUNITIES
-- ============================================================

INSERT INTO opportunities (
    opportunity_code,
    opportunity_name,
    customer_impact,
    strategic_alignment,
    revenue_impact,
    urgency,
    value_confidence,
    effort_confidence,
    effort_low,
    effort_expected,
    effort_high,
    risk
)
VALUES
(
    'OP-501', 'Deployment Automation',
    5, 5, 4, 5, 5, 5,
    2, 3, 5, 'LOW'
),
(
    'OP-502', 'Analytics Dashboard',
    4, 3, 3, 3, 4, 4,
    5, 8, 12, 'MEDIUM'
),
(
    'OP-503', 'Security Automation',
    5, 5, 4, 5, 4, 4,
    4, 6, 10, 'LOW'
),
(
    'OP-504', 'Documentation Upgrade',
    2, 3, 1, 2, 5, 5,
    2, 3, 4, 'LOW'
),
(
    'OP-505', 'Data Integration',
    5, 5, 5, 4, 3, 3,
    12, 18, 25, 'HIGH'
);

INSERT INTO opportunity_dependencies (
    opportunity_id,
    depends_on_id
)
SELECT a.opportunity_id, b.opportunity_id
FROM opportunities a
JOIN opportunities b
  ON b.opportunity_code = 'OP-504'
WHERE a.opportunity_code = 'OP-505';

-- ============================================================
-- SAMPLE REPOSITORY AND BRANCHES
-- ============================================================

INSERT INTO repositories(repository_name, default_branch)
VALUES ('portfolio-platform', 'main');

INSERT INTO repository_members(repository_id, user_id, role)
SELECT repository_id, member.user_id, member.role
FROM repositories
CROSS JOIN (
    VALUES
        ('project-admin', 'ADMIN'),
        ('maintainer-1', 'MAINTAINER'),
        ('reviewer-1', 'REVIEWER'),
        ('reviewer-2', 'REVIEWER'),
        ('developer-1', 'DEVELOPER')
) AS member(user_id, role)
WHERE repository_name = 'portfolio-platform';

INSERT INTO commits (
    repository_id,
    commit_hash,
    author_id,
    commit_message
)
SELECT repository_id, 'a100000000000001', 'developer-1',
       'Initial main branch commit'
FROM repositories
WHERE repository_name = 'portfolio-platform';

INSERT INTO commits (
    repository_id,
    commit_hash,
    author_id,
    commit_message,
    parent_commit_id
)
SELECT
    r.repository_id,
    'b200000000000002',
    'developer-1',
    'Implement security automation',
    c.commit_id
FROM repositories r
JOIN commits c
  ON c.repository_id = r.repository_id
 AND c.commit_hash = 'a100000000000001'
WHERE r.repository_name = 'portfolio-platform';

INSERT INTO branches (
    repository_id,
    branch_name,
    is_protected,
    head_commit_id
)
SELECT
    r.repository_id,
    'main',
    TRUE,
    c.commit_id
FROM repositories r
JOIN commits c
  ON c.repository_id = r.repository_id
 AND c.commit_hash = 'a100000000000001'
WHERE r.repository_name = 'portfolio-platform';

INSERT INTO branches (
    repository_id,
    branch_name,
    head_commit_id
)
SELECT
    r.repository_id,
    'feature/security-automation',
    c.commit_id
FROM repositories r
JOIN commits c
  ON c.repository_id = r.repository_id
 AND c.commit_hash = 'b200000000000002'
WHERE r.repository_name = 'portfolio-platform';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    title,
    description,
    state,
    is_source_updated,
    has_merge_conflicts,
    linear_history,
    created_by
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    'Implement security automation',
    'Introduce automated security validation.',
    'OPEN',
    TRUE,
    FALSE,
    TRUE,
    'developer-1'
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'feature/security-automation'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
WHERE r.repository_name = 'portfolio-platform';

INSERT INTO pull_request_commits(pull_request_id, commit_id)
SELECT pr.pull_request_id, c.commit_id
FROM pull_requests pr
JOIN commits c
  ON c.repository_id = pr.repository_id
 AND c.commit_hash = 'b200000000000002';

-- ============================================================
-- BRANCH PROTECTION
-- ============================================================

INSERT INTO branch_protection_policies (
    repository_id,
    branch_id,
    required_approvals,
    require_status_checks,
    require_resolved_conversations,
    require_updated_source,
    prohibit_direct_push,
    prohibit_force_push,
    prohibit_branch_deletion,
    require_linear_history,
    prohibit_draft_merge,
    administrator_bypass
)
SELECT
    r.repository_id,
    b.branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE
FROM repositories r
JOIN branches b
  ON b.repository_id = r.repository_id
 AND b.branch_name = 'main'
WHERE r.repository_name = 'portfolio-platform';

INSERT INTO required_status_checks(policy_id, check_name)
SELECT policy_id, required.check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES ('build'), ('tests'), ('security')
) AS required(check_name);

-- ============================================================
-- REVIEW DECISIONS
-- ============================================================

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state,
    eligible,
    stale
)
SELECT
    pr.pull_request_id,
    reviewers.reviewer_id,
    'APPROVED',
    TRUE,
    FALSE
FROM pull_requests pr
CROSS JOIN (
    VALUES ('reviewer-1'), ('reviewer-2')
) AS reviewers(reviewer_id);

-- ============================================================
-- STATUS CHECK RESULTS
-- ============================================================

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    check_state,
    commit_hash,
    completed_at
)
SELECT
    pr.pull_request_id,
    checks.check_name,
    'PASSED',
    'b200000000000002',
    CURRENT_TIMESTAMP
FROM pull_requests pr
CROSS JOIN (
    VALUES ('build'), ('tests'), ('security')
) AS checks(check_name);

-- ============================================================
-- REVIEW CONVERSATION FAILURE CASE
-- ============================================================

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state,
    eligible
)
SELECT
    pull_request_id,
    'reviewer-1',
    'COMMENTED',
    TRUE
FROM pull_requests;

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    comment_body,
    is_resolved
)
SELECT
    review_id,
    'src/security.py',
    42,
    'Validate the external input before processing.',
    FALSE
FROM reviews
WHERE reviewer_id = 'reviewer-1'
ORDER BY submitted_at DESC, review_id DESC
LIMIT 1;

-- ============================================================
-- REPORTING AND RETRIEVAL
-- ============================================================

-- 1. Opportunity matrix.
SELECT *
FROM opportunity_matrix
ORDER BY value_effort_ratio DESC;

-- 2. Value and effort evaluation for one opportunity.
SELECT *
FROM evaluate_opportunity(1, 1);

-- 3. Priority aggregation.
SELECT
    priority,
    COUNT(*) AS opportunity_count,
    ROUND(AVG(adjusted_value), 2) AS average_adjusted_value,
    ROUND(AVG(estimated_effort), 2) AS average_effort
FROM opportunity_matrix
GROUP BY priority
ORDER BY opportunity_count DESC;

-- 4. Opportunity dependency retrieval.
SELECT
    parent.opportunity_code,
    parent.opportunity_name,
    dependency.opportunity_code AS dependency_code,
    dependency.opportunity_name AS dependency_name
FROM opportunity_dependencies d
JOIN opportunities parent
  ON parent.opportunity_id = d.opportunity_id
JOIN opportunities dependency
  ON dependency.opportunity_id = d.depends_on_id;

-- 5. Capacity planning.
SELECT *
FROM allocate_opportunities(15);

-- 6. Pull Request and review report.
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    COUNT(DISTINCT r.review_id) AS review_count,
    eligible_approval_count(pr.pull_request_id) AS approvals,
    COUNT(DISTINCT sc.status_check_id) FILTER (
        WHERE sc.check_state = 'PASSED'
    ) AS passed_checks
FROM pull_requests pr
LEFT JOIN reviews r
  ON r.pull_request_id = pr.pull_request_id
LEFT JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
GROUP BY pr.pull_request_id;

-- 7. Merge eligibility.
SELECT *
FROM evaluate_merge_eligibility(1);

-- 8. Persist the decision in the audit log.
CALL record_merge_evaluation(1, 'project-admin');

-- 9. Report governance blockers.
SELECT
    pull_request_id,
    decision,
    details,
    created_at
FROM merge_audit
ORDER BY created_at DESC;

-- ============================================================
-- TRANSACTIONAL FAILURE DEMONSTRATION
-- ============================================================

-- This transaction attempts an invalid merge and is rolled back.
-- The Pull Request remains open.

BEGIN;

DO $$
DECLARE
    v_result RECORD;
BEGIN
    SELECT *
    INTO v_result
    FROM evaluate_merge_eligibility(1);

    IF NOT v_result.eligible THEN
        RAISE NOTICE
            'Expected blocked state: %',
            array_to_string(v_result.blockers, '; ');
    END IF;
END;
$$;

ROLLBACK;

-- ============================================================
-- OPTIONAL SUCCESSFUL MERGE WORKFLOW
-- ============================================================

-- Resolve the review conversation.
UPDATE review_comments
SET is_resolved = TRUE
WHERE comment_body =
    'Validate the external input before processing.';

-- Remove the failure-producing latest COMMENTED review by
-- recording a fresh approval from reviewer-1.
INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state,
    eligible,
    stale
)
VALUES (
    1,
    'reviewer-1',
    'APPROVED',
    TRUE,
    FALSE
);

-- Re-evaluate before merging.
SELECT *
FROM evaluate_merge_eligibility(1);

-- The successful merge procedure is intentionally explicit.
-- Execute only when all checks pass.
--
-- CALL merge_pull_request(
--     1,
--     2,
--     'SQUASH',
--     'project-admin'
-- );

-- ============================================================
-- FINAL DATA INTEGRITY AND REPORTING CHECKS
-- ============================================================

SELECT
    COUNT(*) AS total_opportunities,
    COUNT(*) FILTER (
        WHERE priority = 'QUICK_WIN'
    ) AS quick_wins,
    COUNT(*) FILTER (
        WHERE priority = 'STRATEGIC'
    ) AS strategic_investments,
    COUNT(*) FILTER (
        WHERE priority = 'FILL_IN'
    ) AS fill_in_opportunities,
    COUNT(*) FILTER (
        WHERE priority = 'LOW_PRIORITY'
    ) AS low_priority_opportunities
FROM opportunity_matrix;

SELECT
    repository_name,
    default_branch
FROM repositories;

SELECT
    b.branch_name,
    b.is_protected,
    bp.required_approvals,
    bp.prohibit_direct_push,
    bp.prohibit_force_push,
    bp.prohibit_branch_deletion
FROM branches b
LEFT JOIN branch_protection_policies bp
  ON bp.branch_id = b.branch_id;
