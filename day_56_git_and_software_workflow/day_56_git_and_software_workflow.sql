DROP SCHEMA IF EXISTS git_workflow CASCADE;
CREATE SCHEMA git_workflow;

SET search_path = git_workflow, public;

CREATE TYPE pr_state AS ENUM ('draft', 'open', 'closed', 'merged');
CREATE TYPE review_state AS ENUM (
    'commented',
    'approved',
    'changes_requested',
    'dismissed'
);
CREATE TYPE check_state AS ENUM ('pending', 'passed', 'failed');
CREATE TYPE merge_strategy AS ENUM ('merge', 'squash', 'rebase');

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (username <> '')
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (name <> '')
);

CREATE TABLE repository_members (
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id)
        ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('admin', 'maintainer', 'developer')),
    PRIMARY KEY (repository_id, user_id)
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    head_sha TEXT,
    UNIQUE (repository_id, name)
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    sha CHAR(12) NOT NULL,
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    message TEXT NOT NULL CHECK (message <> ''),
    parent_sha CHAR(12),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, sha)
);

CREATE TABLE branch_commits (
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id)
        ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position > 0),
    PRIMARY KEY (branch_id, commit_id),
    UNIQUE (branch_id, position)
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    number INTEGER NOT NULL CHECK (number > 0),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    state pr_state NOT NULL DEFAULT 'open',
    head_sha CHAR(12),
    merge_strategy merge_strategy,
    synchronized BOOLEAN NOT NULL DEFAULT TRUE,
    unresolved_conversations INTEGER NOT NULL DEFAULT 0
        CHECK (unresolved_conversations >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    UNIQUE (repository_id, number),
    CHECK (source_branch_id <> target_branch_id)
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    position INTEGER NOT NULL CHECK (position > 0),
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(user_id),
    state review_state NOT NULL,
    commit_sha CHAR(12) NOT NULL,
    body TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER CHECK (line_number > 0),
    body TEXT NOT NULL CHECK (body <> ''),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    state check_state NOT NULL,
    commit_sha CHAR(12) NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, name, commit_sha)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL CHECK (check_name <> ''),
    PRIMARY KEY (policy_id, check_name)
);

CREATE TABLE allowed_merge_strategies (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    strategy merge_strategy NOT NULL,
    PRIMARY KEY (policy_id, strategy)
);

CREATE INDEX idx_pr_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_commit
    ON reviews(pull_request_id, commit_sha);

CREATE INDEX idx_status_checks_pr_commit
    ON status_checks(pull_request_id, commit_sha);

CREATE INDEX idx_review_comments_unresolved
    ON review_comments(review_id)
    WHERE resolved = FALSE;

CREATE OR REPLACE FUNCTION prevent_self_approval()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    pr_author BIGINT;
BEGIN
    SELECT author_id
    INTO pr_author
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    IF NEW.reviewer_id = pr_author AND NEW.state = 'approved' THEN
        RAISE EXCEPTION 'Pull Request authors cannot approve their own Pull Request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_self_approval
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION prevent_self_approval();

CREATE OR REPLACE FUNCTION validate_requested_changes_comment()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.state = 'changes_requested'
       AND COALESCE(length(trim(NEW.body)), 0) = 0 THEN
        RAISE EXCEPTION
            'A changes_requested review requires review text';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_review_comment_required
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION validate_requested_changes_comment();

CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT,
    p_strategy merge_strategy
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pr RECORD;
    v_policy RECORD;
    v_approvals INTEGER;
    v_requested_changes BOOLEAN;
    v_required_check TEXT;
    v_check_passed BOOLEAN;
BEGIN
    SELECT *
    INTO v_pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Pull Request does not exist';
        RETURN;
    END IF;

    IF v_pr.state <> 'open' THEN
        RETURN QUERY SELECT FALSE, 'Pull Request is not open';
    END IF;

    IF v_pr.head_sha IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Pull Request has no head commit';
    END IF;

    IF NOT v_pr.synchronized THEN
        RETURN QUERY SELECT FALSE, 'Source branch is not synchronized';
    END IF;

    SELECT bpp.*
    INTO v_policy
    FROM branch_protection_policies bpp
    WHERE bpp.branch_id = v_pr.target_branch_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT TRUE, 'Target branch has no protection policy';
        RETURN;
    END IF;

    /*
     * DISTINCT ON gives the latest decision for each reviewer.
     * This is important because a new review can supersede an older approval.
     */
    SELECT COUNT(*)
    INTO v_approvals
    FROM (
        SELECT DISTINCT ON (reviewer_id)
            reviewer_id,
            state,
            commit_sha
        FROM reviews
        WHERE pull_request_id = p_pull_request_id
        ORDER BY reviewer_id, submitted_at DESC, review_id DESC
    ) latest
    WHERE latest.state = 'approved'
      AND latest.commit_sha = v_pr.head_sha;

    SELECT EXISTS (
        SELECT 1
        FROM (
            SELECT DISTINCT ON (reviewer_id)
                reviewer_id,
                state,
                commit_sha
            FROM reviews
            WHERE pull_request_id = p_pull_request_id
            ORDER BY reviewer_id, submitted_at DESC, review_id DESC
        ) latest
        WHERE latest.state = 'changes_requested'
          AND latest.commit_sha = v_pr.head_sha
    )
    INTO v_requested_changes;

    IF v_requested_changes THEN
        RETURN QUERY
        SELECT FALSE, 'Current review requests changes';
    END IF;

    IF v_approvals < v_policy.required_approvals THEN
        RETURN QUERY
        SELECT FALSE,
               format(
                   'Approvals %s/%s',
                   v_approvals,
                   v_policy.required_approvals
               );
    END IF;

    IF v_policy.require_conversation_resolution
       AND v_pr.unresolved_conversations > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'Unresolved review conversations remain';
    END IF;

    FOR v_required_check IN
        SELECT check_name
        FROM required_status_checks
        WHERE policy_id = v_policy.policy_id
    LOOP
        SELECT EXISTS (
            SELECT 1
            FROM status_checks sc
            WHERE sc.pull_request_id = p_pull_request_id
              AND sc.name = v_required_check
              AND sc.commit_sha = v_pr.head_sha
              AND sc.state = 'passed'
        )
        INTO v_check_passed;

        IF NOT v_check_passed THEN
            RETURN QUERY
            SELECT FALSE,
                   'Required status check not passed: ' ||
                   v_required_check;
        END IF;
    END LOOP;

    IF NOT EXISTS (
        SELECT 1
        FROM allowed_merge_strategies ams
        WHERE ams.policy_id = v_policy.policy_id
          AND ams.strategy = p_strategy
    ) THEN
        RETURN QUERY
        SELECT FALSE,
               'Merge strategy is not permitted: ' || p_strategy::TEXT;
    END IF;

    RETURN QUERY SELECT TRUE, 'Merge eligible';
END;
$$;

CREATE OR REPLACE FUNCTION merge_pull_request(
    p_pull_request_id BIGINT,
    p_strategy merge_strategy
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_blocked BOOLEAN;
BEGIN
    IF EXISTS (
        SELECT 1
        FROM evaluate_merge_eligibility(
            p_pull_request_id,
            p_strategy
        )
        WHERE eligible = FALSE
    ) THEN
        RAISE EXCEPTION 'Pull Request does not satisfy merge policy';
    END IF;

    /*
     * The state mutation is transactional. If any operation fails,
     * PostgreSQL rolls back the complete merge transaction.
     */
    UPDATE pull_requests
    SET state = 'merged',
        merge_strategy = p_strategy,
        merged_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = p_pull_request_id
      AND state = 'open';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull Request is no longer mergeable';
    END IF;
END;
$$;

INSERT INTO users (username)
VALUES
    ('alice'),
    ('bob'),
    ('carol'),
    ('dave');

INSERT INTO repositories (name, default_branch)
VALUES ('payments-service', 'main');

INSERT INTO repository_members
    (repository_id, user_id, role)
SELECT
    r.repository_id,
    u.user_id,
    CASE u.username
        WHEN 'alice' THEN 'maintainer'
        ELSE 'developer'
    END
FROM repositories r
CROSS JOIN users u
WHERE r.name = 'payments-service';

INSERT INTO branches (repository_id, name, protected)
SELECT repository_id, 'main', TRUE
FROM repositories
WHERE name = 'payments-service';

INSERT INTO branches (repository_id, name, protected)
SELECT repository_id, 'feature/payment-validation', FALSE
FROM repositories
WHERE name = 'payments-service';

INSERT INTO commits
    (repository_id, sha, author_id, message, parent_sha)
SELECT
    r.repository_id,
    'a10000000001',
    u.user_id,
    'Initialize payment service',
    NULL
FROM repositories r
JOIN users u ON u.username = 'alice'
WHERE r.name = 'payments-service';

INSERT INTO commits
    (repository_id, sha, author_id, message, parent_sha)
SELECT
    r.repository_id,
    'b10000000001',
    u.user_id,
    'Add payment validation',
    'a10000000001'
FROM repositories r
JOIN users u ON u.username = 'alice'
WHERE r.name = 'payments-service';

INSERT INTO branch_commits (branch_id, commit_id, position)
SELECT
    b.branch_id,
    c.commit_id,
    1
FROM branches b
JOIN commits c
    ON c.sha = 'a10000000001'
WHERE b.name = 'main';

INSERT INTO branch_commits (branch_id, commit_id, position)
SELECT
    b.branch_id,
    c.commit_id,
    1
FROM branches b
JOIN commits c
    ON c.sha = 'a10000000001'
WHERE b.name = 'feature/payment-validation';

INSERT INTO branch_commits (branch_id, commit_id, position)
SELECT
    b.branch_id,
    c.commit_id,
    2
FROM branches b
JOIN commits c
    ON c.sha = 'b10000000001'
WHERE b.name = 'feature/payment-validation';

UPDATE branches
SET head_sha = CASE
    WHEN name = 'main' THEN 'a10000000001'
    ELSE 'b10000000001'
END
WHERE repository_id = (
    SELECT repository_id
    FROM repositories
    WHERE name = 'payments-service'
);

INSERT INTO pull_requests
    (
        repository_id,
        number,
        source_branch_id,
        target_branch_id,
        author_id,
        state,
        head_sha,
        synchronized,
        unresolved_conversations
    )
SELECT
    r.repository_id,
    1,
    source.branch_id,
    target.branch_id,
    u.user_id,
    'open',
    'b10000000001',
    TRUE,
    0
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.name = 'feature/payment-validation'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.name = 'main'
JOIN users u ON u.username = 'alice'
WHERE r.name = 'payments-service';

INSERT INTO pull_request_commits
    (pull_request_id, commit_id, position)
SELECT
    pr.pull_request_id,
    c.commit_id,
    1
FROM pull_requests pr
JOIN commits c ON c.sha = 'a10000000001'
WHERE pr.number = 1;

INSERT INTO pull_request_commits
    (pull_request_id, commit_id, position)
SELECT
    pr.pull_request_id,
    c.commit_id,
    2
FROM pull_requests pr
JOIN commits c ON c.sha = 'b10000000001'
WHERE pr.number = 1;

INSERT INTO branch_protection_policies
    (
        branch_id,
        required_approvals,
        require_conversation_resolution,
        allow_direct_push,
        allow_force_push,
        allow_branch_deletion,
        require_linear_history
    )
SELECT
    branch_id,
    2,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    TRUE
FROM branches
WHERE name = 'main';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, 'unit-tests'
FROM branch_protection_policies
WHERE branch_id = (
    SELECT branch_id
    FROM branches
    WHERE name = 'main'
);

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, 'security-scan'
FROM branch_protection_policies
WHERE branch_id = (
    SELECT branch_id
    FROM branches
    WHERE name = 'main'
);

INSERT INTO allowed_merge_strategies (policy_id, strategy)
SELECT policy_id, 'squash'
FROM branch_protection_policies
WHERE branch_id = (
    SELECT branch_id
    FROM branches
    WHERE name = 'main'
);

INSERT INTO allowed_merge_strategies (policy_id, strategy)
SELECT policy_id, 'rebase'
FROM branch_protection_policies
WHERE branch_id = (
    SELECT branch_id
    FROM branches
    WHERE name = 'main'
);

INSERT INTO reviews
    (
        pull_request_id,
        reviewer_id,
        state,
        commit_sha,
        body
    )
SELECT
    pr.pull_request_id,
    u.user_id,
    'commented',
    'b10000000001',
    'Please validate unsupported currencies.'
FROM pull_requests pr
JOIN users u ON u.username = 'bob'
WHERE pr.number = 1;

INSERT INTO reviews
    (
        pull_request_id,
        reviewer_id,
        state,
        commit_sha,
        body
    )
SELECT
    pr.pull_request_id,
    u.user_id,
    'changes_requested',
    'b10000000001',
    'Reject unsupported currencies before payment processing.'
FROM pull_requests pr
JOIN users u ON u.username = 'carol'
WHERE pr.number = 1;

INSERT INTO review_comments
    (review_id, file_path, line_number, body)
SELECT
    review_id,
    'payment.py',
    42,
    'Validate currency against the supported currency set.'
FROM reviews
WHERE state = 'changes_requested';

INSERT INTO status_checks
    (pull_request_id, name, state, commit_sha, completed_at)
SELECT
    pull_request_id,
    'unit-tests',
    'passed',
    'b10000000001',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE number = 1;

INSERT INTO status_checks
    (pull_request_id, name, state, commit_sha, completed_at)
SELECT
    pull_request_id,
    'security-scan',
    'passed',
    'b10000000001',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE number = 1;

-- Initial evaluation: requested changes and insufficient approvals block merge.
SELECT *
FROM evaluate_merge_eligibility(
    (SELECT pull_request_id FROM pull_requests WHERE number = 1),
    'squash'
);

-- Resolve the review discussion and submit two approvals.
UPDATE pull_requests
SET unresolved_conversations = 0
WHERE number = 1;

INSERT INTO reviews
    (
        pull_request_id,
        reviewer_id,
        state,
        commit_sha,
        body
    )
SELECT
    pr.pull_request_id,
    u.user_id,
    'approved',
    'b10000000001',
    'Validation is acceptable after review.'
FROM pull_requests pr
JOIN users u ON u.username = 'bob'
WHERE pr.number = 1;

INSERT INTO reviews
    (
        pull_request_id,
        reviewer_id,
        state,
        commit_sha,
        body
    )
SELECT
    pr.pull_request_id,
    u.user_id,
    'approved',
    'b10000000001',
    'Security and validation requirements are satisfied.'
FROM pull_requests pr
JOIN users u ON u.username = 'carol'
WHERE pr.number = 1;

-- Current evaluation uses the latest review per reviewer and the PR head SHA.
SELECT *
FROM evaluate_merge_eligibility(
    (SELECT pull_request_id FROM pull_requests WHERE number = 1),
    'squash'
);

BEGIN;

SELECT merge_pull_request(
    (SELECT pull_request_id FROM pull_requests WHERE number = 1),
    'squash'
);

COMMIT;

-- Reporting query: repository, PR, branch state, review counts, and checks.
SELECT
    r.name AS repository,
    pr.number AS pull_request,
    pr.state,
    source.name AS source_branch,
    target.name AS target_branch,
    pr.head_sha,
    COUNT(DISTINCT rev.review_id) AS review_count,
    COUNT(DISTINCT sc.status_check_id) AS status_check_count,
    pr.unresolved_conversations
FROM pull_requests pr
JOIN repositories r
    ON r.repository_id = pr.repository_id
JOIN branches source
    ON source.branch_id = pr.source_branch_id
JOIN branches target
    ON target.branch_id = pr.target_branch_id
LEFT JOIN reviews rev
    ON rev.pull_request_id = pr.pull_request_id
LEFT JOIN status_checks sc
    ON sc.pull_request_id = pr.pull_request_id
GROUP BY
    r.name,
    pr.number,
    pr.state,
    source.name,
    target.name,
    pr.head_sha,
    pr.unresolved_conversations;

-- Approval audit: identify approvals that are stale because their SHA
-- differs from the current Pull Request head.
SELECT
    pr.number,
    u.username AS reviewer,
    rev.state,
    rev.commit_sha AS reviewed_sha,
    pr.head_sha AS current_head,
    rev.submitted_at
FROM pull_requests pr
JOIN reviews rev
    ON rev.pull_request_id = pr.pull_request_id
JOIN users u
    ON u.user_id = rev.reviewer_id
WHERE rev.state = 'approved'
  AND rev.commit_sha <> pr.head_sha
ORDER BY rev.submitted_at DESC;

-- Branch governance report.
SELECT
    r.name AS repository,
    b.name AS protected_branch,
    p.required_approvals,
    p.require_conversation_resolution,
    p.allow_direct_push,
    p.allow_force_push,
    p.allow_branch_deletion,
    p.require_linear_history
FROM branch_protection_policies p
JOIN branches b ON b.branch_id = p.branch_id
JOIN repositories r ON r.repository_id = b.repository_id;
