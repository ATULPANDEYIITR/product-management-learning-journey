DROP SCHEMA IF EXISTS product_engineering CASCADE;
CREATE SCHEMA product_engineering;

SET search_path = product_engineering, public;

CREATE TYPE priority_level AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE work_state AS ENUM (
    'proposed',
    'discovery',
    'estimated',
    'ready',
    'blocked',
    'in_progress',
    'done'
);

CREATE TYPE decision_status AS ENUM (
    'proposed',
    'accepted',
    'rejected'
);

CREATE TYPE review_kind AS ENUM (
    'product',
    'engineering',
    'security',
    'architecture'
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    owner_team TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (btrim(repository_name) <> ''),
    CHECK (btrim(owner_team) <> '')
);

CREATE TABLE team_members (
    member_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    role_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (repository_id, display_name),
    CHECK (btrim(display_name) <> ''),
    CHECK (btrim(role_name) <> '')
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    head_commit_sha CHAR(40),
    UNIQUE (repository_id, branch_name),
    CHECK (branch_name ~ '^[A-Za-z0-9._/-]+$'),
    CHECK (
        head_commit_sha IS NULL
        OR head_commit_sha ~ '^[0-9a-f]{40}$'
    )
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    commit_sha CHAR(40) NOT NULL,
    author_member_id BIGINT
        REFERENCES team_members(member_id),
    message TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, commit_sha),
    CHECK (commit_sha ~ '^[0-9a-f]{40}$'),
    CHECK (btrim(message) <> '')
);

CREATE TABLE requirements (
    requirement_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    requirement_key TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority priority_level NOT NULL,
    state work_state NOT NULL DEFAULT 'proposed',
    product_owner_id BIGINT
        REFERENCES team_members(member_id),
    engineering_owner_id BIGINT
        REFERENCES team_members(member_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, requirement_key),
    CHECK (requirement_key ~ '^[A-Z]{2,8}-[0-9]{1,6}$'),
    CHECK (btrim(title) <> ''),
    CHECK (btrim(description) <> '')
);

CREATE TABLE acceptance_criteria (
    criterion_id BIGSERIAL PRIMARY KEY,
    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    criterion_text TEXT NOT NULL,
    satisfied BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (btrim(criterion_text) <> ''),
    UNIQUE (requirement_id, criterion_text)
);

CREATE TABLE requirement_dependencies (
    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    depends_on_requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (requirement_id, depends_on_requirement_id),
    CHECK (requirement_id <> depends_on_requirement_id)
);

CREATE TABLE estimates (
    estimate_id BIGSERIAL PRIMARY KEY,
    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    story_points INTEGER NOT NULL,
    engineering_days NUMERIC(8,2) NOT NULL,
    confidence NUMERIC(5,4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (requirement_id),
    CHECK (story_points > 0),
    CHECK (engineering_days > 0),
    CHECK (confidence > 0 AND confidence <= 1)
);

CREATE TABLE architecture_options (
    architecture_option_id BIGSERIAL PRIMARY KEY,
    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    option_name TEXT NOT NULL,
    description TEXT NOT NULL,
    delivery_days NUMERIC(8,2) NOT NULL,
    monthly_cost NUMERIC(12,2) NOT NULL,
    scalability_score SMALLINT NOT NULL,
    maintainability_score SMALLINT NOT NULL,
    security_score SMALLINT NOT NULL,
    complexity_score SMALLINT NOT NULL,
    UNIQUE (requirement_id, option_name),
    CHECK (btrim(option_name) <> ''),
    CHECK (delivery_days > 0),
    CHECK (monthly_cost >= 0),
    CHECK (scalability_score BETWEEN 1 AND 5),
    CHECK (maintainability_score BETWEEN 1 AND 5),
    CHECK (security_score BETWEEN 1 AND 5),
    CHECK (complexity_score BETWEEN 1 AND 5)
);

CREATE TABLE architecture_decisions (
    decision_id BIGSERIAL PRIMARY KEY,
    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    architecture_option_id BIGINT NOT NULL
        REFERENCES architecture_options(architecture_option_id)
        ON DELETE RESTRICT,
    decision_key TEXT NOT NULL,
    title TEXT NOT NULL,
    rationale TEXT NOT NULL,
    status decision_status NOT NULL DEFAULT 'proposed',
    decided_by BIGINT REFERENCES team_members(member_id),
    decided_at TIMESTAMPTZ,
    UNIQUE (requirement_id, decision_key),
    CHECK (btrim(decision_key) <> ''),
    CHECK (btrim(title) <> ''),
    CHECK (btrim(rationale) <> '')
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    requirement_id BIGINT
        REFERENCES requirements(requirement_id)
        ON DELETE SET NULL,
    author_member_id BIGINT NOT NULL
        REFERENCES team_members(member_id),
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'open',
    is_draft BOOLEAN NOT NULL DEFAULT TRUE,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    merged_at TIMESTAMPTZ,
    merged_commit_sha CHAR(40),
    CHECK (state IN ('open', 'closed', 'merged')),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (btrim(title) <> ''),
    CHECK (btrim(description) <> ''),
    CHECK (
        merged_commit_sha IS NULL
        OR merged_commit_sha ~ '^[0-9a-f]{40}$'
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (pull_request_id, commit_id)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES team_members(member_id),
    review_kind review_kind NOT NULL,
    status decision_status NOT NULL,
    body TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    dismissed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    commit_id BIGINT
        REFERENCES commits(commit_id)
        ON DELETE SET NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (btrim(file_path) <> ''),
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (btrim(body) <> '')
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name),
    CHECK (status IN ('pending', 'passed', 'failed')),
    CHECK (btrim(check_name) <> '')
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_reviews INTEGER NOT NULL DEFAULT 1,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_branch_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_reviews >= 0)
);

CREATE TABLE merge_attempts (
    merge_attempt_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    attempted_by BIGINT NOT NULL
        REFERENCES team_members(member_id),
    eligible BOOLEAN NOT NULL,
    reason TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_requirements_state
    ON requirements (state, priority);

CREATE INDEX idx_pr_reviews_pr
    ON reviews (pull_request_id, status, dismissed);

CREATE INDEX idx_pr_status_checks
    ON status_checks (pull_request_id, status);

CREATE INDEX idx_review_comments_unresolved
    ON review_comments (review_id)
    WHERE resolved = FALSE;

CREATE INDEX idx_pull_requests_target
    ON pull_requests (target_branch_id, state);

INSERT INTO repositories (repository_name, owner_team)
VALUES ('catalog-platform', 'product-engineering');

INSERT INTO team_members
    (repository_id, display_name, role_name)
VALUES
    (1, 'Asha', 'product_manager'),
    (1, 'Vikram', 'staff_engineer'),
    (1, 'Nina', 'security_engineer'),
    (1, 'Omar', 'backend_engineer');

INSERT INTO branches
    (repository_id, branch_name, is_default, is_protected)
VALUES
    (1, 'main', TRUE, TRUE),
    (1, 'feature/personalization', FALSE, FALSE);

INSERT INTO commits
    (repository_id, commit_sha, author_member_id, message)
VALUES
    (
        1,
        '1111111111111111111111111111111111111111',
        4,
        'Add recommendation service contract'
    ),
    (
        1,
        '2222222222222222222222222222222222222222',
        4,
        'Add fallback ranking behavior'
    );

UPDATE branches
SET head_commit_sha = '2222222222222222222222222222222222222222'
WHERE branch_id = 2;

INSERT INTO requirements (
    repository_id,
    requirement_key,
    title,
    description,
    priority,
    state,
    product_owner_id,
    engineering_owner_id
)
VALUES (
    1,
    'CAT-204',
    'Introduce personalized recommendations',
    'Rank catalog items using permitted behavioral signals while preserving '
    'latency and privacy constraints.',
    'high',
    'ready',
    1,
    2
);

INSERT INTO acceptance_criteria (requirement_id, criterion_text, satisfied)
VALUES
    (1, 'Recommendations meet the agreed latency budget.', TRUE),
    (1, 'Customers without history receive a deterministic fallback.', TRUE),
    (1, 'Sensitive customer attributes are excluded.', TRUE),
    (1, 'The feature can be disabled through controlled configuration.', FALSE);

INSERT INTO estimates (
    requirement_id,
    story_points,
    engineering_days,
    confidence
)
VALUES (1, 8, 7.0, 0.84);

INSERT INTO architecture_options (
    requirement_id,
    option_name,
    description,
    delivery_days,
    monthly_cost,
    scalability_score,
    maintainability_score,
    security_score,
    complexity_score
)
VALUES
(
    1,
    'Precomputed recommendation tables',
    'Build rankings asynchronously and serve a compact read model.',
    7,
    220,
    5,
    5,
    5,
    2
),
(
    1,
    'Synchronous ranking service',
    'Calculate ranking during each request.',
    4,
    380,
    4,
    3,
    5,
    4
),
(
    1,
    'Client-side ranking',
    'Perform ranking in the browser.',
    3,
    90,
    3,
    2,
    1,
    4
);

INSERT INTO architecture_decisions (
    requirement_id,
    architecture_option_id,
    decision_key,
    title,
    rationale,
    status,
    decided_by,
    decided_at
)
VALUES (
    1,
    1,
    'ADR-021',
    'Recommendation computation strategy',
    'Precomputation provides predictable latency, strong scalability, '
    'and a clear server-side privacy boundary.',
    'accepted',
    2,
    now()
);

INSERT INTO pull_requests (
    repository_id,
    requirement_id,
    author_member_id,
    source_branch_id,
    target_branch_id,
    title,
    description,
    state,
    is_draft
)
VALUES (
    1,
    1,
    4,
    2,
    1,
    'Add personalized recommendation service',
    'Implements ranking, fallback behavior, and operational controls.',
    'open',
    FALSE
);

INSERT INTO pull_request_commits (pull_request_id, commit_id)
VALUES
    (1, 1),
    (1, 2);

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_kind,
    status,
    body
)
VALUES
    (1, 2, 'engineering', 'accepted',
     'Architecture and operational boundaries are clear.'),
    (1, 3, 'security', 'accepted',
     'Privacy boundary and authorization controls are acceptable.'),
    (1, 1, 'product', 'accepted',
     'Acceptance criteria are represented in the implementation.');

INSERT INTO review_comments (
    review_id,
    commit_id,
    file_path,
    line_number,
    body,
    resolved
)
VALUES
    (
        1,
        1,
        'src/recommendation_service.cpp',
        84,
        'Please make the fallback ranking deterministic.',
        TRUE
    ),
    (
        2,
        2,
        'src/audit.cpp',
        31,
        'Avoid writing customer identifiers to application logs.',
        FALSE
    );

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    status,
    completed_at
)
VALUES
    (1, 'unit-tests', 'passed', now()),
    (1, 'integration-tests', 'passed', now()),
    (1, 'security-scan', 'passed', now());

INSERT INTO branch_protection_policies (
    branch_id,
    required_reviews,
    require_conversation_resolution,
    require_status_checks,
    restrict_direct_push,
    restrict_force_push,
    restrict_branch_deletion,
    require_linear_history,
    allow_administrator_bypass
)
VALUES (
    1,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE
);

CREATE OR REPLACE FUNCTION validate_review_reviewer()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    pr_repository BIGINT;
    reviewer_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO pr_repository
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    SELECT repository_id
    INTO reviewer_repository
    FROM team_members
    WHERE member_id = NEW.reviewer_id
      AND active = TRUE;

    IF reviewer_repository IS NULL
       OR reviewer_repository <> pr_repository THEN
        RAISE EXCEPTION
            'Reviewer is not an active member of the repository';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review_reviewer
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION validate_review_reviewer();

CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    requested_pr BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    target_branch BIGINT;
    required_reviews INTEGER;
    accepted_reviews INTEGER;
    unresolved_comments INTEGER;
    failed_checks INTEGER;
    pending_checks INTEGER;
    is_draft BOOLEAN;
    pr_state TEXT;
BEGIN
    SELECT
        pr.target_branch_id,
        pr.is_draft,
        pr.state
    INTO
        target_branch,
        is_draft,
        pr_state
    FROM pull_requests pr
    WHERE pr.pull_request_id = requested_pr;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Pull Request does not exist';
        RETURN;
    END IF;

    IF pr_state <> 'open' THEN
        RETURN QUERY SELECT FALSE, 'Pull Request is not open';
        RETURN;
    END IF;

    IF is_draft THEN
        RETURN QUERY SELECT FALSE, 'Draft Pull Request cannot be merged';
        RETURN;
    END IF;

    SELECT
        bp.required_reviews
    INTO required_reviews
    FROM branch_protection_policies bp
    WHERE bp.branch_id = target_branch;

    IF required_reviews IS NULL THEN
        required_reviews := 0;
    END IF;

    SELECT count(*)
    INTO accepted_reviews
    FROM reviews r
    WHERE r.pull_request_id = requested_pr
      AND r.status = 'accepted'
      AND r.dismissed = FALSE;

    IF accepted_reviews < required_reviews THEN
        RETURN QUERY SELECT
            FALSE,
            format(
                'Required approvals not satisfied: %s of %s',
                accepted_reviews,
                required_reviews
            );
        RETURN;
    END IF;

    SELECT count(*)
    INTO unresolved_comments
    FROM review_comments rc
    JOIN reviews r ON r.review_id = rc.review_id
    WHERE r.pull_request_id = requested_pr
      AND rc.resolved = FALSE;

    IF unresolved_comments > 0 THEN
        RETURN QUERY SELECT
            FALSE,
            format(
                'There are %s unresolved review conversations',
                unresolved_comments
            );
        RETURN;
    END IF;

    SELECT count(*)
    INTO failed_checks
    FROM status_checks
    WHERE pull_request_id = requested_pr
      AND status = 'failed';

    IF failed_checks > 0 THEN
        RETURN QUERY SELECT FALSE, 'One or more required checks failed';
        RETURN;
    END IF;

    SELECT count(*)
    INTO pending_checks
    FROM status_checks
    WHERE pull_request_id = requested_pr
      AND status = 'pending';

    IF pending_checks > 0 THEN
        RETURN QUERY SELECT FALSE, 'One or more checks are still pending';
        RETURN;
    END IF;

    RETURN QUERY SELECT TRUE, 'All merge eligibility conditions are satisfied';
END;
$$;

CREATE OR REPLACE VIEW requirement_readiness AS
WITH criteria AS (
    SELECT
        requirement_id,
        count(*) AS total_criteria,
        count(*) FILTER (WHERE satisfied) AS satisfied_criteria
    FROM acceptance_criteria
    GROUP BY requirement_id
),
decisions AS (
    SELECT
        requirement_id,
        count(*) FILTER (WHERE status = 'accepted') AS accepted_decisions
    FROM architecture_decisions
    GROUP BY requirement_id
)
SELECT
    r.requirement_key,
    r.title,
    r.state,
    r.priority,
    COALESCE(c.total_criteria, 0) AS total_criteria,
    COALESCE(c.satisfied_criteria, 0) AS satisfied_criteria,
    COALESCE(d.accepted_decisions, 0) AS accepted_architecture_decisions,
    e.story_points,
    e.engineering_days,
    e.confidence,
    (
        e.estimate_id IS NOT NULL
        AND e.confidence >= 0.60
        AND COALESCE(c.total_criteria, 0) =
            COALESCE(c.satisfied_criteria, 0)
        AND COALESCE(d.accepted_decisions, 0) > 0
    ) AS implementation_ready
FROM requirements r
LEFT JOIN criteria c
    ON c.requirement_id = r.requirement_id
LEFT JOIN decisions d
    ON d.requirement_id = r.requirement_id
LEFT JOIN estimates e
    ON e.requirement_id = r.requirement_id;

CREATE OR REPLACE VIEW architecture_tradeoff_report AS
SELECT
    ao.requirement_id,
    r.requirement_key,
    ao.option_name,
    ao.delivery_days,
    ao.monthly_cost,
    ao.scalability_score,
    ao.maintainability_score,
    ao.security_score,
    ao.complexity_score,
    (
        0.10 / ao.delivery_days
        + 0.05 / GREATEST(ao.monthly_cost, 1)
        + 0.20 * ao.scalability_score
        + 0.20 * ao.maintainability_score
        + 0.35 * ao.security_score
        + 0.10 * (6 - ao.complexity_score)
    ) AS weighted_score
FROM architecture_options ao
JOIN requirements r
    ON r.requirement_id = ao.requirement_id;

CREATE OR REPLACE VIEW pull_request_governance_report AS
SELECT
    pr.pull_request_id,
    r.repository_name,
    pr.title,
    pr.state,
    pr.is_draft,
    bp.required_reviews,
    COUNT(DISTINCT rv.review_id)
        FILTER (
            WHERE rv.status = 'accepted'
              AND rv.dismissed = FALSE
        ) AS active_approvals,
    COUNT(DISTINCT rc.comment_id)
        FILTER (WHERE rc.resolved = FALSE) AS unresolved_comments,
    COUNT(DISTINCT sc.status_check_id)
        FILTER (WHERE sc.status = 'failed') AS failed_checks,
    COUNT(DISTINCT sc.status_check_id)
        FILTER (WHERE sc.status = 'pending') AS pending_checks
FROM pull_requests pr
JOIN repositories r
    ON r.repository_id = pr.repository_id
LEFT JOIN branch_protection_policies bp
    ON bp.branch_id = pr.target_branch_id
LEFT JOIN reviews rv
    ON rv.pull_request_id = pr.pull_request_id
LEFT JOIN review_comments rc
    ON rc.review_id = rv.review_id
LEFT JOIN status_checks sc
    ON sc.pull_request_id = pr.pull_request_id
GROUP BY
    pr.pull_request_id,
    r.repository_name,
    pr.title,
    pr.state,
    pr.is_draft,
    bp.required_reviews;

-- Product requirement readiness.
SELECT *
FROM requirement_readiness
ORDER BY requirement_key;

-- Architecture trade-off evaluation.
SELECT
    requirement_key,
    option_name,
    ROUND(weighted_score::NUMERIC, 4) AS weighted_score,
    delivery_days,
    monthly_cost,
    security_score,
    scalability_score,
    maintainability_score
FROM architecture_tradeoff_report
ORDER BY requirement_id, weighted_score DESC;

-- Review quality and unresolved discussion reporting.
SELECT
    pr.pull_request_id,
    pr.title,
    COUNT(DISTINCT rv.review_id) AS review_count,
    COUNT(DISTINCT rc.comment_id)
        FILTER (WHERE rc.resolved = FALSE) AS unresolved_comments,
    COUNT(DISTINCT rc.comment_id)
        FILTER (WHERE rc.resolved = TRUE) AS resolved_comments
FROM pull_requests pr
LEFT JOIN reviews rv
    ON rv.pull_request_id = pr.pull_request_id
LEFT JOIN review_comments rc
    ON rc.review_id = rv.review_id
GROUP BY pr.pull_request_id, pr.title;

-- Branch protection and review policy reporting.
SELECT *
FROM pull_request_governance_report
ORDER BY pull_request_id;

-- This query is the final merge-eligibility decision.
SELECT *
FROM evaluate_merge_eligibility(1);

-- Demonstrate transactional merge handling.
BEGIN;

WITH eligibility AS (
    SELECT *
    FROM evaluate_merge_eligibility(1)
)
INSERT INTO merge_attempts (
    pull_request_id,
    attempted_by,
    eligible,
    reason
)
SELECT
    1,
    2,
    eligible,
    reason
FROM eligibility;

UPDATE pull_requests
SET
    state = 'merged',
    merged_at = now(),
    merged_commit_sha = '2222222222222222222222222222222222222222'
WHERE pull_request_id = 1
  AND EXISTS (
      SELECT 1
      FROM evaluate_merge_eligibility(1)
      WHERE eligible = TRUE
  );

COMMIT;

-- The unresolved security conversation intentionally makes the sample
-- Pull Request fail the first eligibility evaluation. After resolving it,
-- the same workflow can be evaluated again.
UPDATE review_comments
SET resolved = TRUE
WHERE comment_id = 2;

SELECT *
FROM evaluate_merge_eligibility(1);
