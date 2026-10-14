-- PostgreSQL 15+
-- Acceptance criteria, scenario validation, and repository governance.
-- The schema distinguishes specification quality from runtime merge eligibility.

BEGIN;

CREATE SCHEMA IF NOT EXISTS acceptance_governance;
SET search_path TO acceptance_governance, public;

CREATE TYPE criterion_priority AS ENUM ('must', 'should', 'could');
CREATE TYPE criterion_status AS ENUM ('draft', 'ready', 'verified', 'failed');
CREATE TYPE review_state AS ENUM (
    'pending', 'approved', 'changes_requested', 'commented', 'dismissed'
);
CREATE TYPE check_state AS ENUM ('pending', 'passed', 'failed', 'cancelled');
CREATE TYPE merge_method AS ENUM ('merge_commit', 'squash', 'rebase');

CREATE TABLE repository (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name TEXT NOT NULL CHECK (length(trim(owner_name)) > 0),
    repository_name TEXT NOT NULL CHECK (length(trim(repository_name)) > 0),
    default_branch TEXT NOT NULL DEFAULT 'main',
    UNIQUE (owner_name, repository_name)
);

CREATE TABLE repository_member (
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    username TEXT NOT NULL CHECK (length(trim(username)) > 0),
    can_review BOOLEAN NOT NULL DEFAULT TRUE,
    can_bypass_protection BOOLEAN NOT NULL DEFAULT FALSE,
    is_repository_admin BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (repository_id, username)
);

CREATE TABLE repository_branch (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL CHECK (length(trim(branch_name)) > 0),
    head_sha TEXT NOT NULL CHECK (head_sha ~ '^[a-fA-F0-9]{7,40}$'),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE acceptance_criterion (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    criterion_key TEXT NOT NULL
        CHECK (criterion_key ~ '^AC-[A-Z]{2,8}-[0-9]{3}$'),
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 5 AND 120),
    description TEXT NOT NULL CHECK (length(trim(description)) >= 15),
    priority criterion_priority NOT NULL,
    owner_username TEXT NOT NULL,
    status criterion_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, criterion_key),
    FOREIGN KEY (repository_id, owner_username)
        REFERENCES repository_member(repository_id, username)
);

CREATE TABLE acceptance_scenario (
    scenario_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    criterion_id BIGINT NOT NULL REFERENCES acceptance_criterion(criterion_id)
        ON DELETE CASCADE,
    scenario_name TEXT NOT NULL CHECK (length(trim(scenario_name)) >= 5),
    given_context TEXT NOT NULL CHECK (length(trim(given_context)) >= 8),
    when_action TEXT NOT NULL CHECK (length(trim(when_action)) >= 8),
    then_outcome TEXT NOT NULL CHECK (length(trim(then_outcome)) >= 8),
    expected_behavior TEXT NOT NULL
        CHECK (length(trim(expected_behavior)) >= 8),
    tags TEXT[] NOT NULL DEFAULT ARRAY['functional']::TEXT[],
    CHECK (cardinality(tags) > 0)
);

CREATE TABLE criterion_execution (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    criterion_id BIGINT NOT NULL REFERENCES acceptance_criterion(criterion_id)
        ON DELETE CASCADE,
    commit_sha TEXT NOT NULL CHECK (commit_sha ~ '^[a-fA-F0-9]{7,40}$'),
    passed BOOLEAN NOT NULL,
    evidence TEXT NOT NULL CHECK (length(trim(evidence)) > 0),
    executed_by TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (executed_by) REFERENCES repository_member(username)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE branch_protection (
    protection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES repository_branch(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT TRUE,
    require_code_owner_review BOOLEAN NOT NULL DEFAULT FALSE,
    restrict_direct_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    enforce_for_administrators BOOLEAN NOT NULL DEFAULT TRUE,
    required_merge_method merge_method NOT NULL DEFAULT 'squash'
);

CREATE TABLE required_status_check (
    protection_id BIGINT NOT NULL
        REFERENCES branch_protection(protection_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL CHECK (length(trim(check_name)) > 0),
    PRIMARY KEY (protection_id, check_name)
);

CREATE TABLE pull_request (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    pr_number INTEGER NOT NULL CHECK (pr_number > 0),
    author_username TEXT NOT NULL,
    source_branch_id BIGINT NOT NULL REFERENCES repository_branch(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES repository_branch(branch_id),
    head_sha TEXT NOT NULL CHECK (head_sha ~ '^[a-fA-F0-9]{7,40}$'),
    base_sha TEXT NOT NULL CHECK (base_sha ~ '^[a-fA-F0-9]{7,40}$'),
    title TEXT NOT NULL CHECK (length(trim(title)) >= 5),
    description TEXT NOT NULL DEFAULT '',
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    is_open BOOLEAN NOT NULL DEFAULT TRUE,
    merge_conflict BOOLEAN NOT NULL DEFAULT FALSE,
    conversations_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    mergeable_method merge_method,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    UNIQUE (repository_id, pr_number),
    FOREIGN KEY (repository_id, author_username)
        REFERENCES repository_member(repository_id, username),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (NOT is_open OR closed_at IS NULL),
    CHECK (merged_at IS NULL OR NOT is_open)
);

CREATE TABLE pull_request_commit (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    commit_sha TEXT NOT NULL CHECK (commit_sha ~ '^[a-fA-F0-9]{7,40}$'),
    position INTEGER NOT NULL CHECK (position > 0),
    is_merge_commit BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (pull_request_id, commit_sha),
    UNIQUE (pull_request_id, position)
);

CREATE TABLE pull_request_review (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    reviewer_username TEXT NOT NULL,
    reviewed_commit_sha TEXT NOT NULL
        CHECK (reviewed_commit_sha ~ '^[a-fA-F0-9]{7,40}$'),
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    dismissed_at TIMESTAMPTZ,
    dismissal_reason TEXT,
    FOREIGN KEY (pull_request_id, reviewer_username)
        REFERENCES pull_request(pull_request_id, author_username)
        DEFERRABLE INITIALLY DEFERRED
);

-- Reviewer eligibility is checked through repository membership by the
-- eligibility view. A reviewer need not be the pull request author.
CREATE TABLE review_comment (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES pull_request_review(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL CHECK (length(trim(file_path)) > 0),
    line_number INTEGER CHECK (line_number IS NULL OR line_number > 0),
    is_inline BOOLEAN NOT NULL DEFAULT TRUE,
    comment_body TEXT NOT NULL CHECK (length(trim(comment_body)) > 0),
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pull_request_status_check (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL CHECK (length(trim(check_name)) > 0),
    commit_sha TEXT NOT NULL CHECK (commit_sha ~ '^[a-fA-F0-9]{7,40}$'),
    state check_state NOT NULL,
    details_url TEXT,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name, commit_sha)
);

CREATE TABLE pull_request_merge_event (
    merge_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL UNIQUE
        REFERENCES pull_request(pull_request_id),
    merged_by TEXT NOT NULL,
    method merge_method NOT NULL,
    merge_sha TEXT NOT NULL CHECK (merge_sha ~ '^[a-fA-F0-9]{7,40}$'),
    merged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pr_target_open
    ON pull_request(target_branch_id, is_open);

CREATE INDEX idx_reviews_pr_state
    ON pull_request_review(pull_request_id, state, submitted_at DESC);

CREATE INDEX idx_status_pr_name_sha
    ON pull_request_status_check(pull_request_id, check_name, commit_sha);

CREATE INDEX idx_comments_unresolved
    ON review_comment(review_id)
    WHERE is_resolved = FALSE;

CREATE INDEX idx_scenarios_criterion
    ON acceptance_scenario(criterion_id);

-- This trigger prevents declaring criteria ready without a valid scenario.
CREATE OR REPLACE FUNCTION enforce_criterion_readiness()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'ready' AND OLD.status <> 'ready' THEN
        IF NOT EXISTS (
            SELECT 1
            FROM acceptance_scenario s
            WHERE s.criterion_id = NEW.criterion_id
        ) THEN
            RAISE EXCEPTION
                'Criterion % cannot become ready without a scenario',
                NEW.criterion_key;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_criterion_readiness
BEFORE UPDATE OF status ON acceptance_criterion
FOR EACH ROW
EXECUTE FUNCTION enforce_criterion_readiness();

-- The author must be a repository member, and review eligibility is
-- determined by repository membership rather than by the review row alone.
CREATE OR REPLACE VIEW pull_request_merge_eligibility AS
WITH approval_counts AS (
    SELECT
        pr.pull_request_id,
        COUNT(DISTINCT rv.reviewer_username) FILTER (
            WHERE rv.state = 'approved'
              AND rv.dismissed_at IS NULL
              AND (
                  bp.dismiss_stale_approvals = FALSE
                  OR rv.reviewed_commit_sha = pr.head_sha
              )
              AND reviewer.can_review = TRUE
              AND rv.reviewer_username <> pr.author_username
        ) AS valid_approvals
    FROM pull_request pr
    JOIN repository_branch target
      ON target.branch_id = pr.target_branch_id
    LEFT JOIN branch_protection bp
      ON bp.branch_id = target.branch_id
    LEFT JOIN pull_request_review rv
      ON rv.pull_request_id = pr.pull_request_id
    LEFT JOIN repository_member reviewer
      ON reviewer.repository_id = pr.repository_id
     AND reviewer.username = rv.reviewer_username
    GROUP BY pr.pull_request_id
),
check_results AS (
    SELECT
        pr.pull_request_id,
        COUNT(req.check_name) FILTER (
            WHERE NOT EXISTS (
                SELECT 1
                FROM pull_request_status_check sc
                WHERE sc.pull_request_id = pr.pull_request_id
                  AND sc.check_name = req.check_name
                  AND sc.commit_sha = pr.head_sha
                  AND sc.state = 'passed'
            )
        ) AS missing_checks
    FROM pull_request pr
    LEFT JOIN branch_protection bp
      ON bp.branch_id = pr.target_branch_id
    LEFT JOIN required_status_check req
      ON req.protection_id = bp.protection_id
    GROUP BY pr.pull_request_id
),
unresolved_comments AS (
    SELECT
        pr.pull_request_id,
        COUNT(c.comment_id) AS unresolved_count
    FROM pull_request pr
    LEFT JOIN pull_request_review rv
      ON rv.pull_request_id = pr.pull_request_id
    LEFT JOIN review_comment c
      ON c.review_id = rv.review_id
     AND c.is_resolved = FALSE
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.repository_id,
    pr.pr_number,
    pr.head_sha,
    target.branch_name AS target_branch,
    COALESCE(ac.valid_approvals, 0) AS valid_approvals,
    COALESCE(bp.required_approvals, 0) AS required_approvals,
    COALESCE(cr.missing_checks, 0) AS missing_checks,
    COALESCE(uc.unresolved_count, 0) AS unresolved_comments,
    CASE
        WHEN NOT pr.is_open THEN 'closed'
        WHEN pr.is_draft THEN 'draft'
        WHEN pr.merge_conflict THEN 'merge_conflict'
        WHEN bp.protection_id IS NOT NULL
             AND COALESCE(ac.valid_approvals, 0) < bp.required_approvals
            THEN 'insufficient_approvals'
        WHEN bp.protection_id IS NOT NULL
             AND COALESCE(cr.missing_checks, 0) > 0
            THEN 'required_checks_incomplete'
        WHEN bp.require_conversation_resolution
             AND COALESCE(uc.unresolved_count, 0) > 0
            THEN 'unresolved_conversations'
        ELSE 'eligible_subject_to_merge_transaction'
    END AS eligibility_status
FROM pull_request pr
JOIN repository_branch target
  ON target.branch_id = pr.target_branch_id
LEFT JOIN branch_protection bp
  ON bp.branch_id = pr.target_branch_id
LEFT JOIN approval_counts ac
  ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_results cr
  ON cr.pull_request_id = pr.pull_request_id
LEFT JOIN unresolved_comments uc
  ON uc.pull_request_id = pr.pull_request_id;

INSERT INTO repository (owner_name, repository_name)
VALUES ('engineering', 'release-platform')
RETURNING repository_id;

INSERT INTO repository_member (
    repository_id, username, can_review, can_bypass_protection,
    is_repository_admin
)
VALUES
    (1, 'maintainer', TRUE, FALSE, TRUE),
    (1, 'reviewer_alex', TRUE, FALSE, FALSE),
    (1, 'reviewer_sam', TRUE, FALSE, FALSE),
    (1, 'developer', FALSE, FALSE, FALSE);

INSERT INTO repository_branch (repository_id, branch_name, head_sha)
VALUES
    (1, 'main', 'abcdef1234567'),
    (1, 'feature/session-timeout', 'f19a82c123456');

INSERT INTO branch_protection (
    branch_id, required_approvals, require_conversation_resolution,
    require_linear_history, allow_force_push, allow_deletion,
    dismiss_stale_approvals, restrict_direct_pushes,
    enforce_for_administrators, required_merge_method
)
VALUES (1, 2, TRUE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, 'squash');

INSERT INTO required_status_check (protection_id, check_name)
VALUES (1, 'unit-tests'), (1, 'security-scan');

INSERT INTO acceptance_criterion (
    repository_id, criterion_key, title, description, priority, owner_username
)
VALUES (
    1,
    'AC-GOV-001',
    'Enforce protected branch merge criteria',
    'Changes targeting production must satisfy review and CI policies.',
    'must',
    'maintainer'
);

INSERT INTO acceptance_scenario (
    criterion_id, scenario_name, given_context, when_action,
    then_outcome, expected_behavior, tags
)
VALUES
(
    1,
    'Missing approval',
    'A protected production branch requires independent approval',
    'A pull request is evaluated without eligible approval',
    'The merge is blocked',
    'Passing checks do not replace the approval requirement.',
    ARRAY['approval', 'negative']
),
(
    1,
    'Current approval and checks',
    'The latest revision has eligible approval and passing checks',
    'The merge service evaluates repository policy',
    'The request is eligible when all rules pass',
    'Only current review and check evidence satisfies the policy.',
    ARRAY['branch-protection', 'positive']
);

UPDATE acceptance_criterion
SET status = 'ready'
WHERE criterion_id = 1;

INSERT INTO pull_request (
    repository_id, pr_number, author_username, source_branch_id,
    target_branch_id, head_sha, base_sha, title, description,
    is_draft, is_open, merge_conflict, conversations_resolved
)
VALUES (
    1, 184, 'developer', 2, 1,
    'f19a82c123456', 'abcdef1234567',
    'Add session timeout protection',
    'Introduce bounded session expiry and validation.',
    FALSE, TRUE, FALSE, FALSE
);

INSERT INTO pull_request_commit (
    pull_request_id, commit_sha, position, is_merge_commit
)
VALUES
    (1, 'aa12bc3123456', 1, FALSE),
    (1, 'f19a82c123456', 2, FALSE);

INSERT INTO pull_request_review (
    pull_request_id, reviewer_username, reviewed_commit_sha, state
)
VALUES
    (1, 'reviewer_alex', 'f19a82c123456', 'approved'),
    (1, 'reviewer_sam', 'aa12bc3123456', 'approved');

INSERT INTO pull_request_status_check (
    pull_request_id, check_name, commit_sha, state
)
VALUES
    (1, 'unit-tests', 'f19a82c123456', 'passed'),
    (1, 'security-scan', 'f19a82c123456', 'pending'),
    (1, 'security-scan', 'aa12bc3123456', 'passed');

INSERT INTO pull_request_review (
    pull_request_id, reviewer_username, reviewed_commit_sha, state
)
VALUES (1, 'maintainer', 'f19a82c123456', 'commented');

INSERT INTO review_comment (
    review_id, file_path, line_number, is_inline, comment_body, is_resolved
)
VALUES (
    3,
    'src/session.py',
    48,
    TRUE,
    'Confirm the expiry boundary is inclusive and covered by a test.',
    FALSE
);

-- Initial evaluation exposes stale approval, pending checks, and unresolved
-- discussion without conflating those three failure causes.
SELECT
    pr_number,
    valid_approvals,
    required_approvals,
    missing_checks,
    unresolved_comments,
    eligibility_status
FROM pull_request_merge_eligibility
WHERE pull_request_id = 1;

-- Update the second review to the current revision, complete the security
-- check, and resolve the discussion. Each action updates distinct evidence.
UPDATE pull_request_review
SET reviewed_commit_sha = 'f19a82c123456'
WHERE pull_request_id = 1
  AND reviewer_username = 'reviewer_sam';

UPDATE pull_request_status_check
SET state = 'passed',
    completed_at = now()
WHERE pull_request_id = 1
  AND check_name = 'security-scan'
  AND commit_sha = 'f19a82c123456';

UPDATE review_comment
SET is_resolved = TRUE
WHERE comment_id = 1;

UPDATE pull_request
SET conversations_resolved = TRUE
WHERE pull_request_id = 1;

SELECT
    pr_number,
    eligibility_status
FROM pull_request_merge_eligibility
WHERE pull_request_id = 1;

-- A merge must be guarded by a transaction and row lock. The following
-- transaction illustrates the final policy gate before recording a merge.
BEGIN;

SELECT pull_request_id
FROM pull_request
WHERE pull_request_id = 1
  AND is_open = TRUE
FOR UPDATE;

DO $$
DECLARE
    current_status TEXT;
    current_pr RECORD;
BEGIN
    SELECT *
    INTO current_pr
    FROM pull_request
    WHERE pull_request_id = 1
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pull request not found';
    END IF;

    SELECT eligibility_status
    INTO current_status
    FROM pull_request_merge_eligibility
    WHERE pull_request_id = 1;

    IF current_status <> 'eligible_subject_to_merge_transaction' THEN
        RAISE EXCEPTION 'Merge blocked: %', current_status;
    END IF;

    INSERT INTO pull_request_merge_event (
        pull_request_id, merged_by, method, merge_sha
    )
    VALUES (
        1, 'maintainer', 'squash', 'b123456789abc'
    );

    UPDATE pull_request
    SET is_open = FALSE,
        merged_at = now(),
        closed_at = now(),
        mergeable_method = 'squash'
    WHERE pull_request_id = 1;
END;
$$;

COMMIT;

-- Acceptance execution evidence is tied to the repository member who ran it.
INSERT INTO criterion_execution (
    criterion_id, commit_sha, passed, evidence, executed_by
)
VALUES (
    1,
    'f19a82c123456',
    TRUE,
    'Merge-policy scenarios passed against current review and CI states.',
    'maintainer'
);

SELECT
    ac.criterion_key,
    ac.status,
    COUNT(s.scenario_id) AS scenario_count,
    COUNT(e.execution_id) AS execution_count,
    COUNT(e.execution_id) FILTER (WHERE e.passed) AS passing_executions
FROM acceptance_criterion ac
LEFT JOIN acceptance_scenario s
  ON s.criterion_id = ac.criterion_id
LEFT JOIN criterion_execution e
  ON e.criterion_id = ac.criterion_id
WHERE ac.criterion_id = 1
GROUP BY ac.criterion_key, ac.status;

ROLLBACK;
