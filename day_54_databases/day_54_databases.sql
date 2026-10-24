DROP SCHEMA IF EXISTS repository_governance CASCADE;
CREATE SCHEMA repository_governance;

SET search_path TO repository_governance, public;

-- Enumerated domain states keep workflow values constrained at the database layer.
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

CREATE TYPE merge_strategy AS ENUM (
    'merge_commit',
    'squash',
    'rebase'
);

CREATE TYPE conversation_state AS ENUM (
    'open',
    'resolved'
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(default_branch)) > 0)
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(username)) > 0)
);

CREATE TABLE teams (
    team_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    CHECK (length(trim(team_name)) > 0)
);

CREATE TABLE team_members (
    team_id BIGINT NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (team_id, user_id)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) > 0)
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    commit_sha VARCHAR(40) NOT NULL,
    message TEXT NOT NULL,
    author_user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, commit_sha),
    CHECK (commit_sha ~ '^[0-9a-f]{7,40}$'),
    CHECK (length(trim(message)) > 0)
);

-- A commit may be present on many branches. This is a many-to-many
-- relationship represented by a junction table.
CREATE TABLE branch_commits (
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id) ON DELETE CASCADE,
    position BIGINT NOT NULL,
    PRIMARY KEY (branch_id, commit_id),
    UNIQUE (branch_id, position),
    CHECK (position > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    pull_request_number INTEGER NOT NULL,
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    author_user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    state pull_request_state NOT NULL DEFAULT 'open',
    merge_strategy merge_strategy NOT NULL DEFAULT 'squash',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, pull_request_number),
    CHECK (pull_request_number > 0),
    CHECK (length(trim(title)) > 0),
    CHECK (source_branch_id <> target_branch_id)
);

-- These rows represent the changeset currently associated with the PR.
CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    sequence_number INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, sequence_number),
    CHECK (sequence_number > 0)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    reviewed_commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    review_state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ,
    CHECK (
        (review_state = 'dismissed' AND dismissed_at IS NOT NULL)
        OR
        (review_state <> 'dismissed')
    )
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    line_number INTEGER,
    body TEXT NOT NULL,
    conversation_state conversation_state NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(path)) > 0),
    CHECK (length(trim(body)) > 0),
    CHECK (line_number IS NULL OR line_number > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pull_request_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_review_count INTEGER NOT NULL DEFAULT 0,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (required_review_count >= 0)
);

CREATE TABLE policy_required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE policy_allowed_merge_strategies (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    strategy merge_strategy NOT NULL,
    PRIMARY KEY (policy_id, strategy)
);

CREATE TABLE policy_bypass_users (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    PRIMARY KEY (policy_id, user_id)
);

CREATE TABLE merges (
    merge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL UNIQUE
        REFERENCES pull_requests(pull_request_id),
    merged_by_user_id BIGINT NOT NULL
        REFERENCES users(user_id),
    strategy merge_strategy NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes support common repository and workflow queries.
CREATE INDEX idx_branches_repository
    ON branches(repository_id);

CREATE INDEX idx_commits_repository_time
    ON commits(repository_id, committed_at DESC);

CREATE INDEX idx_pull_requests_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pull_request_state
    ON reviews(pull_request_id, review_state);

CREATE INDEX idx_status_checks_pr
    ON status_checks(pull_request_id, check_name);

CREATE INDEX idx_comments_open
    ON review_comments(review_id)
    WHERE conversation_state = 'open';

-- Keep updated_at consistent with modifications.
CREATE OR REPLACE FUNCTION touch_pull_request_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_pull_request_updated_at
BEFORE UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION touch_pull_request_updated_at();

-- A protected branch cannot silently lose its protection flag while its
-- policy remains present.
CREATE OR REPLACE FUNCTION enforce_protection_consistency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.is_protected = FALSE
       AND EXISTS (
           SELECT 1
           FROM branch_protection_policies
           WHERE branch_id = NEW.branch_id
       )
    THEN
        RAISE EXCEPTION
            'Branch % has a protection policy and cannot be unprotected',
            NEW.branch_name;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_protection_consistency
BEFORE UPDATE OF is_protected ON branches
FOR EACH ROW
EXECUTE FUNCTION enforce_protection_consistency();

-- A merged PR must have a corresponding merge record. A merge record also
-- forces the workflow state to MERGED.
CREATE OR REPLACE FUNCTION enforce_merge_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE pull_requests
    SET state = 'merged'
    WHERE pull_request_id = NEW.pull_request_id
      AND state = 'open';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Only open pull requests can be merged';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_merge_state
BEFORE INSERT ON merges
FOR EACH ROW
EXECUTE FUNCTION enforce_merge_state();

CREATE OR REPLACE FUNCTION get_merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    blocking_reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_required_reviews INTEGER;
    v_require_conversations BOOLEAN;
    v_target_branch BIGINT;
    v_strategy merge_strategy;
    v_state pull_request_state;
    v_approval_count INTEGER;
    v_requested_changes INTEGER;
    v_unresolved_comments INTEGER;
    v_missing_checks INTEGER;
    v_strategy_allowed BOOLEAN;
BEGIN
    SELECT
        pr.state,
        pr.target_branch_id,
        pr.merge_strategy
    INTO
        v_state,
        v_target_branch,
        v_strategy
    FROM pull_requests pr
    WHERE pr.pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT FALSE, 'Pull request does not exist';
        RETURN;
    END IF;

    IF v_state <> 'open' THEN
        RETURN QUERY
        SELECT FALSE, 'Pull request is not open';
        RETURN;
    END IF;

    SELECT
        bpp.required_review_count,
        bpp.require_conversation_resolution
    INTO
        v_required_reviews,
        v_require_conversations
    FROM branch_protection_policies bpp
    WHERE bpp.branch_id = v_target_branch;

    IF NOT FOUND THEN
        RETURN QUERY
        SELECT TRUE, NULL::TEXT;
        RETURN;
    END IF;

    SELECT COUNT(DISTINCT r.reviewer_user_id)
    INTO v_approval_count
    FROM reviews r
    WHERE r.pull_request_id = p_pull_request_id
      AND r.review_state = 'approved'
      AND r.dismissed_at IS NULL
      AND EXISTS (
          SELECT 1
          FROM pull_request_commits pc
          WHERE pc.pull_request_id = r.pull_request_id
            AND pc.commit_id = r.reviewed_commit_id
      )
      AND EXISTS (
          SELECT 1
          FROM users u
          WHERE u.user_id = r.reviewer_user_id
            AND u.active
      );

    IF v_approval_count < v_required_reviews THEN
        RETURN QUERY
        SELECT FALSE,
               format(
                   'Insufficient approvals: %s/%s',
                   v_approval_count,
                   v_required_reviews
               );
        RETURN;
    END IF;

    SELECT COUNT(*)
    INTO v_requested_changes
    FROM reviews r
    WHERE r.pull_request_id = p_pull_request_id
      AND r.review_state = 'changes_requested'
      AND r.dismissed_at IS NULL;

    IF v_requested_changes > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'Active requested-changes review exists';
        RETURN;
    END IF;

    IF v_require_conversations THEN
        SELECT COUNT(*)
        INTO v_unresolved_comments
        FROM review_comments rc
        JOIN reviews r
          ON r.review_id = rc.review_id
        WHERE r.pull_request_id = p_pull_request_id
          AND rc.conversation_state = 'open';

        IF v_unresolved_comments > 0 THEN
            RETURN QUERY
            SELECT FALSE, 'Unresolved review conversations remain';
            RETURN;
        END IF;
    END IF;

    SELECT COUNT(*)
    INTO v_missing_checks
    FROM policy_required_status_checks prsc
    JOIN branch_protection_policies bpp
      ON bpp.policy_id = prsc.policy_id
    WHERE bpp.branch_id = v_target_branch
      AND NOT EXISTS (
          SELECT 1
          FROM status_checks sc
          WHERE sc.pull_request_id = p_pull_request_id
            AND sc.check_name = prsc.check_name
            AND sc.passed = TRUE
      );

    IF v_missing_checks > 0 THEN
        RETURN QUERY
        SELECT FALSE, 'Required status checks are missing or failed';
        RETURN;
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM policy_allowed_merge_strategies pams
        JOIN branch_protection_policies bpp
          ON bpp.policy_id = pams.policy_id
        WHERE bpp.branch_id = v_target_branch
          AND pams.strategy = v_strategy
    )
    INTO v_strategy_allowed;

    IF NOT v_strategy_allowed THEN
        RETURN QUERY
        SELECT FALSE, 'Selected merge strategy is not allowed';
        RETURN;
    END IF;

    RETURN QUERY
    SELECT TRUE, NULL::TEXT;
END;
$$;

CREATE OR REPLACE FUNCTION merge_pull_request(
    p_pull_request_id BIGINT,
    p_actor_user_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_eligible BOOLEAN;
    v_reason TEXT;
    v_strategy merge_strategy;
    v_target_branch BIGINT;
    v_bypass BOOLEAN;
    v_merge_id BIGINT;
BEGIN
    SELECT
        me.eligible,
        me.blocking_reason
    INTO
        v_eligible,
        v_reason
    FROM get_merge_eligibility(p_pull_request_id) me
    LIMIT 1;

    SELECT
        pr.merge_strategy,
        pr.target_branch_id
    INTO
        v_strategy,
        v_target_branch
    FROM pull_requests pr
    WHERE pr.pull_request_id = p_pull_request_id
    FOR UPDATE;

    SELECT EXISTS (
        SELECT 1
        FROM policy_bypass_users pbu
        JOIN branch_protection_policies bpp
          ON bpp.policy_id = pbu.policy_id
        WHERE bpp.branch_id = v_target_branch
          AND pbu.user_id = p_actor_user_id
    )
    INTO v_bypass;

    IF NOT v_eligible AND NOT v_bypass THEN
        RAISE EXCEPTION 'Merge blocked: %', v_reason;
    END IF;

    INSERT INTO merges (
        pull_request_id,
        merged_by_user_id,
        strategy
    )
    VALUES (
        p_pull_request_id,
        p_actor_user_id,
        v_strategy
    )
    RETURNING merge_id INTO v_merge_id;

    RETURN v_merge_id;
END;
$$;

BEGIN;

INSERT INTO repositories (
    repository_name,
    default_branch
)
VALUES (
    'inventory-platform',
    'main'
);

INSERT INTO users (username)
VALUES
    ('atul'),
    ('maya'),
    ('rahul');

INSERT INTO teams (team_name)
VALUES
    ('database-reviewers'),
    ('application-reviewers');

INSERT INTO team_members (team_id, user_id)
SELECT t.team_id, u.user_id
FROM teams t
CROSS JOIN users u
WHERE t.team_name = 'database-reviewers'
  AND u.username = 'maya';

INSERT INTO team_members (team_id, user_id)
SELECT t.team_id, u.user_id
FROM teams t
CROSS JOIN users u
WHERE t.team_name = 'application-reviewers'
  AND u.username = 'rahul';

INSERT INTO branches (
    repository_id,
    branch_name,
    is_protected
)
SELECT repository_id, 'main', TRUE
FROM repositories
WHERE repository_name = 'inventory-platform';

INSERT INTO branches (
    repository_id,
    branch_name,
    is_protected
)
SELECT repository_id, 'feature/relational-schema', FALSE
FROM repositories
WHERE repository_name = 'inventory-platform';

INSERT INTO commits (
    repository_id,
    commit_sha,
    message,
    author_user_id
)
SELECT
    r.repository_id,
    'a1b2c3d',
    'Create warehouse table',
    u.user_id
FROM repositories r
JOIN users u ON u.username = 'atul'
WHERE r.repository_name = 'inventory-platform';

INSERT INTO commits (
    repository_id,
    commit_sha,
    message,
    author_user_id
)
SELECT
    r.repository_id,
    'b2c3d4e',
    'Create inventory foreign key relationship',
    u.user_id
FROM repositories r
JOIN users u ON u.username = 'atul'
WHERE r.repository_name = 'inventory-platform';

INSERT INTO branch_commits (
    branch_id,
    commit_id,
    position
)
SELECT
    b.branch_id,
    c.commit_id,
    1
FROM branches b
JOIN commits c
  ON c.commit_sha = 'a1b2c3d'
WHERE b.branch_name = 'main';

INSERT INTO branch_commits (
    branch_id,
    commit_id,
    position
)
SELECT
    b.branch_id,
    c.commit_id,
    1
FROM branches b
JOIN commits c
  ON c.commit_sha = 'b2c3d4e'
WHERE b.branch_name = 'feature/relational-schema';

INSERT INTO pull_requests (
    repository_id,
    pull_request_number,
    source_branch_id,
    target_branch_id,
    title,
    author_user_id,
    state,
    merge_strategy
)
SELECT
    r.repository_id,
    42,
    source.branch_id,
    target.branch_id,
    'Add relational inventory schema',
    u.user_id,
    'open',
    'squash'
FROM repositories r
JOIN branches source
  ON source.repository_id = r.repository_id
 AND source.branch_name = 'feature/relational-schema'
JOIN branches target
  ON target.repository_id = r.repository_id
 AND target.branch_name = 'main'
JOIN users u
  ON u.username = 'atul'
WHERE r.repository_name = 'inventory-platform';

INSERT INTO pull_request_commits (
    pull_request_id,
    commit_id,
    sequence_number
)
SELECT
    pr.pull_request_id,
    c.commit_id,
    1
FROM pull_requests pr
JOIN commits c
  ON c.commit_sha = 'b2c3d4e'
WHERE pr.pull_request_number = 42;

INSERT INTO branch_protection_policies (
    branch_id,
    required_review_count,
    require_conversation_resolution,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion,
    require_linear_history
)
SELECT
    branch_id,
    1,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    TRUE
FROM branches
WHERE branch_name = 'main';

INSERT INTO policy_required_status_checks (
    policy_id,
    check_name
)
SELECT policy_id, 'sql-tests'
FROM branch_protection_policies;

INSERT INTO policy_required_status_checks (
    policy_id,
    check_name
)
SELECT policy_id, 'integration-tests'
FROM branch_protection_policies;

INSERT INTO policy_allowed_merge_strategies (
    policy_id,
    strategy
)
SELECT policy_id, 'squash'
FROM branch_protection_policies;

INSERT INTO reviews (
    pull_request_id,
    reviewer_user_id,
    reviewed_commit_id,
    review_state
)
SELECT
    pr.pull_request_id,
    u.user_id,
    c.commit_id,
    'approved'
FROM pull_requests pr
JOIN users u
  ON u.username = 'maya'
JOIN commits c
  ON c.commit_sha = 'b2c3d4e'
WHERE pr.pull_request_number = 42;

INSERT INTO review_comments (
    review_id,
    path,
    line_number,
    body,
    conversation_state
)
SELECT
    r.review_id,
    'schema.sql',
    32,
    'Foreign key correctly connects inventory to warehouse.',
    'resolved'
FROM reviews r
JOIN pull_requests pr
  ON pr.pull_request_id = r.pull_request_id
WHERE pr.pull_request_number = 42;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    passed
)
SELECT
    pull_request_id,
    'sql-tests',
    TRUE
FROM pull_requests
WHERE pull_request_number = 42;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    passed
)
SELECT
    pull_request_id,
    'integration-tests',
    TRUE
FROM pull_requests
WHERE pull_request_number = 42;

COMMIT;

-- Retrieval: show the complete relational PR hierarchy.
SELECT
    r.repository_name,
    pr.pull_request_number,
    pr.title,
    pr.state,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch,
    u.username AS author
FROM pull_requests pr
JOIN repositories r
  ON r.repository_id = pr.repository_id
JOIN branches source
  ON source.branch_id = pr.source_branch_id
JOIN branches target
  ON target.branch_id = pr.target_branch_id
JOIN users u
  ON u.user_id = pr.author_user_id
ORDER BY pr.pull_request_number;

-- Review aggregation: distinguish approvals from requested changes.
SELECT
    pr.pull_request_number,
    COUNT(*) FILTER (
        WHERE r.review_state = 'approved'
          AND r.dismissed_at IS NULL
    ) AS approvals,
    COUNT(*) FILTER (
        WHERE r.review_state = 'changes_requested'
          AND r.dismissed_at IS NULL
    ) AS requested_changes
FROM pull_requests pr
LEFT JOIN reviews r
  ON r.pull_request_id = pr.pull_request_id
GROUP BY pr.pull_request_number;

-- Status-check validation.
SELECT
    pr.pull_request_number,
    sc.check_name,
    sc.passed
FROM pull_requests pr
JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
WHERE pr.pull_request_number = 42
ORDER BY sc.check_name;

-- Evaluate merge eligibility through the database function.
SELECT *
FROM get_merge_eligibility(
    (
        SELECT pull_request_id
        FROM pull_requests
        WHERE pull_request_number = 42
    )
);

-- Transactional merge. The row lock in merge_pull_request prevents
-- concurrent merge operations from independently creating merge records.
BEGIN;

SELECT merge_pull_request(
    (
        SELECT pull_request_id
        FROM pull_requests
        WHERE pull_request_number = 42
    ),
    (
        SELECT user_id
        FROM users
        WHERE username = 'atul'
    )
);

COMMIT;

-- Confirm final workflow state and merge record.
SELECT
    pr.pull_request_number,
    pr.state,
    m.merge_id,
    m.strategy,
    u.username AS merged_by,
    m.merged_at
FROM pull_requests pr
LEFT JOIN merges m
  ON m.pull_request_id = pr.pull_request_id
LEFT JOIN users u
  ON u.user_id = m.merged_by_user_id
WHERE pr.pull_request_number = 42;

-- A CTE provides a compact branch-protection report.
WITH protection AS (
    SELECT
        b.branch_name,
        bpp.required_review_count,
        bpp.require_conversation_resolution,
        bpp.allow_direct_push,
        bpp.allow_force_push,
        bpp.require_linear_history
    FROM branches b
    JOIN branch_protection_policies bpp
      ON bpp.branch_id = b.branch_id
)
SELECT *
FROM protection
ORDER BY branch_name;
