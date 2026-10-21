DROP SCHEMA IF EXISTS repository_governance CASCADE;
CREATE SCHEMA repository_governance;
SET search_path TO repository_governance;

-- Pull Requests propose a changeset; reviews evaluate it; approvals are
-- decisions within reviews; branch protection determines whether a merge
-- is permitted.

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

CREATE TABLE repository (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (name <> ''),
    CHECK (default_branch <> '')
);

CREATE TABLE developer (
    developer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (username <> ''),
    CHECK (email LIKE '%@%')
);

CREATE TABLE repository_member (
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    developer_id BIGINT NOT NULL REFERENCES developer(developer_id),
    role_name TEXT NOT NULL CHECK (role_name IN ('member', 'maintainer', 'admin')),
    PRIMARY KEY (repository_id, developer_id)
);

CREATE TABLE branch (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name),
    CHECK (branch_name <> '')
);

CREATE TABLE commit (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    sha CHAR(40) NOT NULL UNIQUE,
    author_id BIGINT NOT NULL REFERENCES developer(developer_id),
    message TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (message <> ''),
    CHECK (sha ~ '^[0-9a-f]{40}$')
);

CREATE TABLE pull_request (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id),
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    author_id BIGINT NOT NULL REFERENCES developer(developer_id),
    source_branch_id BIGINT NOT NULL REFERENCES branch(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branch(branch_id),
    state pull_request_state NOT NULL DEFAULT 'draft',
    synchronized_with_base BOOLEAN NOT NULL DEFAULT TRUE,
    merge_conflict BOOLEAN NOT NULL DEFAULT FALSE,
    unresolved_conversations INTEGER NOT NULL DEFAULT 0,
    opened_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    UNIQUE (repository_id, number),
    CHECK (title <> ''),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (unresolved_conversations >= 0)
);

CREATE TABLE pull_request_commit (
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commit(commit_id),
    position INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position),
    CHECK (position > 0)
);

CREATE TABLE review_request (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES developer(developer_id),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (pull_request_id, reviewer_id)
);

CREATE TABLE review (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES developer(developer_id),
    state review_state NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_comment (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES review(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (file_path <> ''),
    CHECK (line_number > 0),
    CHECK (body <> '')
);

CREATE TABLE status_check (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection (
    branch_id BIGINT PRIMARY KEY REFERENCES branch(branch_id) ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_approvals >= 0)
);

CREATE TABLE required_status_check (
    branch_id BIGINT NOT NULL REFERENCES branch(branch_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (branch_id, check_name),
    CHECK (check_name <> '')
);

CREATE TABLE merge_event (
    merge_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL UNIQUE
        REFERENCES pull_request(pull_request_id),
    merged_by BIGINT NOT NULL REFERENCES developer(developer_id),
    strategy merge_strategy NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pr_repository_state
    ON pull_request(repository_id, state);

CREATE INDEX idx_review_pr_state
    ON review(pull_request_id, state);

CREATE INDEX idx_status_check_pr
    ON status_check(pull_request_id, check_name);

CREATE INDEX idx_pr_commit_position
    ON pull_request_commit(pull_request_id, position);

CREATE OR REPLACE FUNCTION prevent_invalid_pull_request_review()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    pr_author BIGINT;
BEGIN
    SELECT author_id
    INTO pr_author
    FROM pull_request
    WHERE pull_request_id = NEW.pull_request_id;

    IF pr_author = NEW.reviewer_id THEN
        RAISE EXCEPTION 'Pull Request authors cannot approve or review their own change';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM review_request rr
        WHERE rr.pull_request_id = NEW.pull_request_id
          AND rr.reviewer_id = NEW.reviewer_id
    ) THEN
        RAISE EXCEPTION 'Reviewer has not been requested for this Pull Request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_review
BEFORE INSERT OR UPDATE ON review
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_pull_request_review();

CREATE OR REPLACE FUNCTION merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    blocker TEXT
)
LANGUAGE sql
AS $$
WITH pr AS (
    SELECT
        p.pull_request_id,
        p.state,
        p.target_branch_id,
        p.synchronized_with_base,
        p.merge_conflict,
        p.unresolved_conversations
    FROM pull_request p
    WHERE p.pull_request_id = p_pull_request_id
),
policy AS (
    SELECT
        bp.branch_id,
        bp.required_approvals,
        bp.require_conversation_resolution
    FROM branch_protection bp
    JOIN pr
      ON pr.target_branch_id = bp.branch_id
),
approval_count AS (
    SELECT COUNT(*) AS approved
    FROM review r
    WHERE r.pull_request_id = p_pull_request_id
      AND r.state = 'approved'
),
check_failures AS (
    SELECT rsc.check_name
    FROM required_status_check rsc
    LEFT JOIN status_check sc
      ON sc.pull_request_id = p_pull_request_id
     AND sc.check_name = rsc.check_name
    WHERE rsc.branch_id = (SELECT target_branch_id FROM pr)
      AND COALESCE(sc.passed, FALSE) = FALSE
),
blockers AS (
    SELECT 'Pull Request is not open'::TEXT
    WHERE (SELECT state FROM pr) <> 'open'

    UNION ALL

    SELECT 'Merge conflicts exist'
    WHERE (SELECT merge_conflict FROM pr)

    UNION ALL

    SELECT 'Pull Request is not synchronized with the base branch'
    WHERE NOT (SELECT synchronized_with_base FROM pr)

    UNION ALL

    SELECT 'Unresolved review conversations remain'
    WHERE
        (SELECT require_conversation_resolution FROM policy)
        AND (SELECT unresolved_conversations FROM pr) > 0

    UNION ALL

    SELECT format(
        'Required approvals: %, received: %',
        (SELECT required_approvals FROM policy),
        (SELECT approved FROM approval_count)
    )
    WHERE
        (SELECT approved FROM approval_count)
        < (SELECT required_approvals FROM policy)

    UNION ALL

    SELECT 'Required status check failed or is missing: ' || check_name
    FROM check_failures
)
SELECT
    NOT EXISTS (SELECT 1 FROM blockers) AS eligible,
    blocker
FROM blockers

UNION ALL

SELECT TRUE, NULL::TEXT
WHERE NOT EXISTS (SELECT 1 FROM blockers);
$$;

CREATE OR REPLACE FUNCTION enforce_merge()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    decision RECORD;
BEGIN
    IF NEW.state = 'merged' AND OLD.state <> 'merged' THEN
        SELECT *
        INTO decision
        FROM merge_eligibility(NEW.pull_request_id)
        WHERE blocker IS NOT NULL
        LIMIT 1;

        IF FOUND THEN
            RAISE EXCEPTION 'Merge blocked: %', decision.blocker;
        END IF;

        NEW.merged_at := COALESCE(NEW.merged_at, now());
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_merge
BEFORE UPDATE OF state ON pull_request
FOR EACH ROW
EXECUTE FUNCTION enforce_merge();

INSERT INTO repository (name, default_branch)
VALUES ('payments-platform', 'main');

INSERT INTO developer (username, email)
VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('carol', 'carol@example.com'),
    ('dave', 'dave@example.com');

INSERT INTO repository_member (repository_id, developer_id, role_name)
SELECT 1, developer_id,
       CASE username
           WHEN 'alice' THEN 'member'
           WHEN 'bob' THEN 'maintainer'
           WHEN 'carol' THEN 'maintainer'
           ELSE 'admin'
       END
FROM developer;

INSERT INTO branch (repository_id, branch_name, protected)
VALUES
    (1, 'main', TRUE),
    (1, 'feature/payment-auth', FALSE);

INSERT INTO branch_protection (
    branch_id,
    required_approvals,
    require_conversation_resolution,
    require_linear_history,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion
)
VALUES (
    1,
    2,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE
);

INSERT INTO required_status_check (branch_id, check_name)
VALUES
    (1, 'build'),
    (1, 'tests'),
    (1, 'security');

INSERT INTO commit (repository_id, sha, author_id, message)
VALUES
    (
        1,
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        1,
        'Validate payment authorization token'
    ),
    (
        1,
        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        1,
        'Reject unauthorized payment requests'
    );

INSERT INTO pull_request (
    repository_id,
    number,
    title,
    author_id,
    source_branch_id,
    target_branch_id,
    state,
    opened_at
)
VALUES (
    1,
    101,
    'Harden payment authorization',
    1,
    2,
    1,
    'open',
    now()
);

INSERT INTO pull_request_commit (pull_request_id, commit_id, position)
VALUES
    (1, 1, 1),
    (1, 2, 2);

INSERT INTO review_request (pull_request_id, reviewer_id)
VALUES
    (1, 2),
    (1, 3);

INSERT INTO review (
    pull_request_id,
    reviewer_id,
    state,
    body
)
VALUES
    (
        1,
        2,
        'approved',
        'Authorization boundary is correct.'
    ),
    (
        1,
        3,
        'approved',
        'Failure behavior is explicit.'
    );

INSERT INTO review_comment (
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
VALUES
    (
        1,
        'src/payment/auth.py',
        42,
        'Validate token expiration before authorization.',
        TRUE
    ),
    (
        2,
        'src/payment/service.py',
        77,
        'Return a consistent authorization failure.',
        TRUE
    );

INSERT INTO status_check (pull_request_id, check_name, passed)
VALUES
    (1, 'build', TRUE),
    (1, 'tests', TRUE),
    (1, 'security', TRUE);

-- This query shows whether the current repository policy permits merging.
SELECT *
FROM merge_eligibility(1);

-- Approval report: approvals are review decisions, not branch-protection rules.
SELECT
    p.number,
    p.title,
    COUNT(*) FILTER (WHERE r.state = 'approved') AS approvals,
    COUNT(*) FILTER (WHERE r.state = 'changes_requested') AS changes_requested,
    COUNT(*) FILTER (WHERE r.state = 'commented') AS comments
FROM pull_request p
LEFT JOIN review r
    ON r.pull_request_id = p.pull_request_id
GROUP BY p.number, p.title;

-- Status validation for protected branches.
SELECT
    p.number,
    p.title,
    rsc.check_name,
    COALESCE(sc.passed, FALSE) AS passed
FROM pull_request p
JOIN required_status_check rsc
    ON rsc.branch_id = p.target_branch_id
LEFT JOIN status_check sc
    ON sc.pull_request_id = p.pull_request_id
   AND sc.check_name = rsc.check_name
WHERE p.pull_request_id = 1
ORDER BY rsc.check_name;

-- Review conversations that are still unresolved.
SELECT
    p.number,
    rc.file_path,
    rc.line_number,
    rc.body
FROM pull_request p
JOIN review r
    ON r.pull_request_id = p.pull_request_id
JOIN review_comment rc
    ON rc.review_id = r.review_id
WHERE p.pull_request_id = 1
  AND rc.resolved = FALSE;

-- A transaction demonstrates atomic governance state changes.
BEGIN;

UPDATE pull_request
SET synchronized_with_base = TRUE,
    unresolved_conversations = 0
WHERE pull_request_id = 1;

-- The trigger checks branch-protection conditions before allowing this state.
UPDATE pull_request
SET state = 'merged'
WHERE pull_request_id = 1;

INSERT INTO merge_event (
    pull_request_id,
    merged_by,
    strategy
)
VALUES (
    1,
    4,
    'squash'
);

COMMIT;

SELECT
    number,
    title,
    state,
    merged_at
FROM pull_request
WHERE pull_request_id = 1;
