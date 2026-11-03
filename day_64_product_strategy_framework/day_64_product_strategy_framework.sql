DROP SCHEMA IF EXISTS repository_governance CASCADE;

CREATE SCHEMA repository_governance;

SET search_path TO repository_governance;

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'commented',
    'approved',
    'changes_requested',
    'dismissed'
);

CREATE TYPE check_state AS ENUM (
    'pending',
    'passed',
    'failed'
);

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit',
    'squash',
    'rebase'
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repository_users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    is_administrator BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    force_push_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    direct_push_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(repository_id, branch_name)
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    sha CHAR(40) NOT NULL,
    author_id BIGINT NOT NULL
        REFERENCES repository_users(user_id),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(repository_id, sha)
);

CREATE TABLE branch_commits (
    branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id)
        ON DELETE CASCADE,
    position BIGINT NOT NULL CHECK (position > 0),
    PRIMARY KEY(branch_id, commit_id),
    UNIQUE(branch_id, position)
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    author_id BIGINT NOT NULL
        REFERENCES repository_users(user_id),
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    state pull_request_state NOT NULL DEFAULT 'open',
    draft BOOLEAN NOT NULL DEFAULT FALSE,
    base_head_sha CHAR(40),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMPTZ,
    UNIQUE(repository_id, number),
    CHECK(source_branch_id <> target_branch_id),
    CHECK(title <> '')
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id)
        ON DELETE RESTRICT,
    position INTEGER NOT NULL CHECK(position > 0),
    PRIMARY KEY(pull_request_id, commit_id),
    UNIQUE(pull_request_id, position)
);

CREATE TABLE review_requests (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES repository_users(user_id),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(pull_request_id, reviewer_id)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES repository_users(user_id),
    state review_state NOT NULL,
    stale BOOLEAN NOT NULL DEFAULT FALSE,
    dismissed BOOLEAN NOT NULL DEFAULT FALSE,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK(NOT (stale AND state = 'approved' AND dismissed = FALSE))
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK(line_number > 0),
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    state check_state NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE(pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0
        CHECK(required_approvals >= 0),
    require_conversations_resolved BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    allow_admin_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    allow_merge_commit BOOLEAN NOT NULL DEFAULT TRUE,
    allow_squash BOOLEAN NOT NULL DEFAULT TRUE,
    allow_rebase BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY(policy_id, check_name)
);

CREATE TABLE merge_events (
    merge_event_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id),
    merged_by BIGINT NOT NULL
        REFERENCES repository_users(user_id),
    strategy merge_strategy NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pr_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_pr_author
    ON pull_requests(author_id);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, state, stale, dismissed);

CREATE INDEX idx_status_checks_pr_state
    ON status_checks(pull_request_id, check_name, state);

CREATE INDEX idx_comments_review_resolution
    ON review_comments(review_id, resolved);

CREATE INDEX idx_branch_commits_order
    ON branch_commits(branch_id, position);

CREATE OR REPLACE FUNCTION prevent_self_review()
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

    IF pr_author = NEW.reviewer_id THEN
        RAISE EXCEPTION
            'Pull Request author cannot review the same Pull Request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_self_review
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION prevent_self_review();

CREATE OR REPLACE FUNCTION prevent_self_review_request()
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

    IF pr_author = NEW.reviewer_id THEN
        RAISE EXCEPTION
            'Pull Request author cannot be a requested reviewer';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_self_review_request
BEFORE INSERT OR UPDATE ON review_requests
FOR EACH ROW
EXECUTE FUNCTION prevent_self_review_request();

CREATE OR REPLACE FUNCTION mark_approvals_stale_after_commit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE reviews
    SET stale = TRUE
    WHERE pull_request_id = NEW.pull_request_id
      AND state = 'approved'
      AND dismissed = FALSE;

    UPDATE pull_requests
    SET updated_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = NEW.pull_request_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_stale_approvals
AFTER INSERT ON pull_request_commits
FOR EACH ROW
EXECUTE FUNCTION mark_approvals_stale_after_commit();

CREATE OR REPLACE FUNCTION merge_eligibility(
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
    pr RECORD;
    policy RECORD;
    valid_approvals INTEGER;
    unresolved_comments INTEGER;
    requested_failures INTEGER;
    strategy_allowed BOOLEAN;
BEGIN
    SELECT *
    INTO pr
    FROM pull_requests
    WHERE pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request does not exist';
        RETURN;
    END IF;

    IF pr.state <> 'open' THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request is not open';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pull_request_commits
        WHERE pull_request_id = p_pull_request_id
    ) THEN
        RETURN QUERY
        SELECT FALSE, 'Pull Request contains no proposed changes';
    END IF;

    SELECT bpp.*
    INTO policy
    FROM branch_protection_policies bpp
    WHERE bpp.branch_id = pr.target_branch_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT TRUE, 'No branch protection policy is configured';
        RETURN;
    END IF;

    strategy_allowed :=
        CASE p_strategy
            WHEN 'merge_commit' THEN policy.allow_merge_commit
            WHEN 'squash' THEN policy.allow_squash
            WHEN 'rebase' THEN policy.allow_rebase
        END;

    IF NOT strategy_allowed THEN
        RETURN QUERY
        SELECT FALSE, 'Selected merge strategy is prohibited';
    END IF;

    SELECT COUNT(DISTINCT r.reviewer_id)
    INTO valid_approvals
    FROM reviews r
    JOIN review_requests rr
      ON rr.pull_request_id = r.pull_request_id
     AND rr.reviewer_id = r.reviewer_id
    WHERE r.pull_request_id = p_pull_request_id
      AND r.state = 'approved'
      AND r.stale = FALSE
      AND r.dismissed = FALSE;

    IF valid_approvals < policy.required_approvals THEN
        RETURN QUERY
        SELECT FALSE,
               format(
                   'Approval requirement not met: %s/%s',
                   valid_approvals,
                   policy.required_approvals
               );
    END IF;

    SELECT COUNT(*)
    INTO requested_failures
    FROM required_status_checks rsc
    LEFT JOIN status_checks sc
      ON sc.pull_request_id = p_pull_request_id
     AND sc.check_name = rsc.check_name
    WHERE rsc.policy_id = policy.policy_id
      AND (sc.status_check_id IS NULL OR sc.state <> 'passed');

    IF requested_failures > 0 THEN
        RETURN QUERY
        SELECT FALSE,
               'One or more required status checks are missing or failed';
    END IF;

    IF policy.require_conversations_resolved THEN
        SELECT COUNT(*)
        INTO unresolved_comments
        FROM review_comments rc
        JOIN reviews r
          ON r.review_id = rc.review_id
        WHERE r.pull_request_id = p_pull_request_id
          AND rc.resolved = FALSE;

        IF unresolved_comments > 0 THEN
            RETURN QUERY
            SELECT FALSE, 'Unresolved review conversations remain';
        END IF;
    END IF;

    IF policy.require_linear_history
       AND p_strategy = 'merge_commit' THEN
        RETURN QUERY
        SELECT FALSE, 'Merge commit violates linear-history policy';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM reviews
        WHERE pull_request_id = p_pull_request_id
          AND state = 'changes_requested'
          AND dismissed = FALSE
    ) THEN
        RETURN QUERY
        SELECT FALSE, 'An active review requests changes';
    END IF;

    RETURN QUERY
    SELECT TRUE, 'Merge eligible';
END;
$$;

CREATE OR REPLACE FUNCTION update_pull_request_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_pr_updated_at
BEFORE UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION update_pull_request_timestamp();

CREATE OR REPLACE FUNCTION record_merge(
    p_pull_request_id BIGINT,
    p_actor BIGINT,
    p_strategy merge_strategy
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    is_eligible BOOLEAN;
    reason_text TEXT;
BEGIN
    SELECT me.eligible, me.reason
    INTO is_eligible, reason_text
    FROM merge_eligibility(
        p_pull_request_id,
        p_strategy
    ) me
    WHERE me.eligible = FALSE
    LIMIT 1;

    IF is_eligible IS FALSE THEN
        RAISE EXCEPTION 'Merge blocked: %', reason_text;
    END IF;

    INSERT INTO merge_events(
        pull_request_id,
        merged_by,
        strategy
    )
    VALUES (
        p_pull_request_id,
        p_actor,
        p_strategy
    );

    UPDATE pull_requests
    SET state = 'merged',
        merged_at = CURRENT_TIMESTAMP
    WHERE pull_request_id = p_pull_request_id;
END;
$$;

INSERT INTO repositories(repository_name, default_branch)
VALUES ('payments-platform', 'main');

INSERT INTO repository_users(username, is_administrator)
VALUES
    ('alice', FALSE),
    ('bob', FALSE),
    ('carol', FALSE),
    ('release-manager', TRUE),
    ('david', FALSE);

INSERT INTO branches(repository_id, branch_name)
SELECT repository_id, 'main'
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO branches(repository_id, branch_name)
SELECT repository_id, 'feature/refunds'
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO commits(repository_id, sha, author_id, message)
SELECT
    r.repository_id,
    'c001',
    u.user_id,
    'Initial release'
FROM repositories r
JOIN repository_users u ON u.username = 'alice'
WHERE r.repository_name = 'payments-platform';

INSERT INTO commits(repository_id, sha, author_id, message)
SELECT
    r.repository_id,
    'c002',
    u.user_id,
    'Add payment service'
FROM repositories r
JOIN repository_users u ON u.username = 'alice'
WHERE r.repository_name = 'payments-platform';

INSERT INTO commits(repository_id, sha, author_id, message)
SELECT
    r.repository_id,
    'c003',
    u.user_id,
    'Implement refund API'
FROM repositories r
JOIN repository_users u ON u.username = 'bob'
WHERE r.repository_name = 'payments-platform';

INSERT INTO branch_commits(branch_id, commit_id, position)
SELECT b.branch_id, c.commit_id, x.position
FROM branches b
JOIN commits c
  ON c.repository_id = b.repository_id
JOIN (
    VALUES
        ('main', 'c001', 1),
        ('main', 'c002', 2),
        ('feature/refunds', 'c001', 1),
        ('feature/refunds', 'c002', 2),
        ('feature/refunds', 'c003', 3)
) AS x(branch_name, sha, position)
  ON x.branch_name = b.branch_name
 AND x.sha = c.sha
WHERE b.repository_id = (
    SELECT repository_id
    FROM repositories
    WHERE repository_name = 'payments-platform'
);

INSERT INTO pull_requests(
    repository_id,
    number,
    title,
    author_id,
    source_branch_id,
    target_branch_id,
    state,
    draft,
    base_head_sha
)
SELECT
    r.repository_id,
    1,
    'Implement refund API',
    author.user_id,
    source.branch_id,
    target.branch_id,
    'open',
    FALSE,
    'c002'
FROM repositories r
JOIN repository_users author
  ON author.username = 'bob'
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'feature/refunds'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
WHERE r.repository_name = 'payments-platform';

INSERT INTO pull_request_commits(
    pull_request_id,
    commit_id,
    position
)
SELECT
    pr.pull_request_id,
    c.commit_id,
    ROW_NUMBER() OVER (ORDER BY c.sha)
FROM pull_requests pr
JOIN commits c
  ON c.repository_id = pr.repository_id
WHERE pr.number = 1
  AND c.sha IN ('c001', 'c002', 'c003');

INSERT INTO review_requests(pull_request_id, reviewer_id)
SELECT pr.pull_request_id, u.user_id
FROM pull_requests pr
JOIN repository_users u
  ON u.username IN ('alice', 'carol')
WHERE pr.number = 1;

INSERT INTO reviews(
    pull_request_id,
    reviewer_id,
    state
)
SELECT pr.pull_request_id, u.user_id, 'approved'
FROM pull_requests pr
JOIN repository_users u
  ON u.username IN ('alice', 'carol')
WHERE pr.number = 1;

INSERT INTO review_comments(
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
SELECT
    r.review_id,
    'refund_service.py',
    42,
    'Validate refund amount against the original order.',
    TRUE
FROM reviews r
JOIN repository_users u
  ON u.user_id = r.reviewer_id
WHERE u.username = 'alice'
  AND r.pull_request_id = (
      SELECT pull_request_id
      FROM pull_requests
      WHERE number = 1
  );

INSERT INTO status_checks(
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT
    pr.pull_request_id,
    check_name,
    'passed',
    CURRENT_TIMESTAMP
FROM pull_requests pr
CROSS JOIN (
    VALUES ('unit-tests'), ('security-scan')
) AS checks(check_name)
WHERE pr.number = 1;

INSERT INTO branch_protection_policies(
    branch_id,
    required_approvals,
    require_conversations_resolved,
    require_linear_history,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion,
    allow_admin_bypass,
    allow_merge_commit,
    allow_squash,
    allow_rebase
)
SELECT
    b.branch_id,
    2,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    TRUE,
    TRUE
FROM branches b
WHERE b.branch_name = 'main';

INSERT INTO required_status_checks(policy_id, check_name)
SELECT policy_id, check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES ('unit-tests'), ('security-scan')
) AS checks(check_name);

-- Retrieval: inspect the Pull Request and its proposed changes.
SELECT
    pr.number,
    pr.title,
    pr.state,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch,
    author.username AS author
FROM pull_requests pr
JOIN branches source
  ON source.branch_id = pr.source_branch_id
JOIN branches target
  ON target.branch_id = pr.target_branch_id
JOIN repository_users author
  ON author.user_id = pr.author_id
ORDER BY pr.number;

-- Review and approval report.
SELECT
    pr.number,
    reviewer.username,
    r.state,
    r.stale,
    r.dismissed
FROM pull_requests pr
JOIN reviews r
  ON r.pull_request_id = pr.pull_request_id
JOIN repository_users reviewer
  ON reviewer.user_id = r.reviewer_id
ORDER BY pr.number, reviewer.username;

-- Status-check evaluation.
SELECT
    pr.number,
    sc.check_name,
    sc.state,
    sc.completed_at
FROM pull_requests pr
JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
ORDER BY pr.number, sc.check_name;

-- Branch-protection configuration.
SELECT
    b.branch_name,
    p.required_approvals,
    p.require_conversations_resolved,
    p.require_linear_history,
    p.allow_direct_push,
    p.allow_force_push,
    p.allow_branch_deletion,
    p.allow_admin_bypass
FROM branches b
JOIN branch_protection_policies p
  ON p.branch_id = b.branch_id
WHERE b.protected = TRUE;

-- Aggregate review activity.
SELECT
    pr.number,
    COUNT(r.review_id) AS review_count,
    COUNT(*) FILTER (
        WHERE r.state = 'approved'
          AND NOT r.stale
          AND NOT r.dismissed
    ) AS active_approvals,
    COUNT(*) FILTER (
        WHERE r.state = 'changes_requested'
          AND NOT r.dismissed
    ) AS active_change_requests
FROM pull_requests pr
LEFT JOIN reviews r
  ON r.pull_request_id = pr.pull_request_id
GROUP BY pr.number
ORDER BY pr.number;

-- Explicit merge-eligibility evaluation.
SELECT *
FROM merge_eligibility(
    (SELECT pull_request_id
     FROM pull_requests
     WHERE number = 1),
    'squash'
);

-- Demonstrate transaction-safe merge processing.
BEGIN;

SELECT *
FROM merge_eligibility(
    (SELECT pull_request_id
     FROM pull_requests
     WHERE number = 1),
    'squash'
);

-- The merge procedure raises an exception if eligibility is violated.
-- Execute only after the eligibility query reports no blocking condition.
SELECT record_merge(
    (SELECT pull_request_id
     FROM pull_requests
     WHERE number = 1),
    (SELECT user_id
     FROM repository_users
     WHERE username = 'release-manager'),
    'squash'
);

COMMIT;

-- Final merge history.
SELECT
    me.merge_event_id,
    pr.number,
    pr.title,
    u.username AS merged_by,
    me.strategy,
    me.merged_at
FROM merge_events me
JOIN pull_requests pr
  ON pr.pull_request_id = me.pull_request_id
JOIN repository_users u
  ON u.user_id = me.merged_by
ORDER BY me.merged_at;
