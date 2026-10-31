DROP SCHEMA IF EXISTS product_strategy_governance CASCADE;

CREATE SCHEMA product_strategy_governance;

SET search_path = product_strategy_governance, public;

-- Product strategy is kept separate from repository enforcement.
CREATE TYPE product_stage AS ENUM (
    'discovery',
    'validation',
    'delivery',
    'scale'
);

CREATE TYPE pr_state AS ENUM (
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
    product_stage product_stage NOT NULL DEFAULT 'delivery',
    vision TEXT NOT NULL,
    mission TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(repository_name)) >= 2),
    CHECK (length(trim(vision)) >= 20),
    CHECK (length(trim(mission)) >= 20)
);

CREATE TABLE strategic_choices (
    strategic_choice_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    choice_text TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (repository_id, choice_text),
    CHECK (length(trim(choice_text)) >= 10)
);

CREATE TABLE product_goals (
    goal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    goal_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    target_value NUMERIC(14,4) NOT NULL,
    current_value NUMERIC(14,4) NOT NULL DEFAULT 0,
    UNIQUE (repository_id, goal_name),
    CHECK (target_value > 0),
    CHECK (current_value >= 0)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) >= 1)
);

CREATE UNIQUE INDEX one_default_branch_per_repository
    ON branches(repository_id)
    WHERE is_default = TRUE;

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    sha TEXT NOT NULL UNIQUE,
    message TEXT NOT NULL,
    author TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (sha ~ '^[0-9A-Fa-f]{8,64}$'),
    CHECK (length(trim(message)) > 0),
    CHECK (length(trim(author)) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    source_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL
        REFERENCES branches(branch_id),
    state pr_state NOT NULL DEFAULT 'open',
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    merge_strategy merge_strategy NOT NULL DEFAULT 'squash',
    base_synchronized_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    merged_at TIMESTAMPTZ,
    UNIQUE (repository_id, number),
    CHECK (number > 0),
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(author)) > 0),
    CHECK (source_branch_id <> target_branch_id)
);

CREATE INDEX pull_requests_target_branch_idx
    ON pull_requests(target_branch_id, state);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id) ON DELETE RESTRICT,
    position INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, position),
    CHECK (position > 0)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    administrator BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (length(trim(username)) >= 2)
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL
        REFERENCES reviewers(reviewer_id),
    reviewed_commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    state review_state NOT NULL,
    review_body TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX reviews_pr_reviewer_state_idx
    ON reviews(pull_request_id, reviewer_id, state);

CREATE TABLE review_comments (
    review_comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL
        REFERENCES reviews(review_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    file_path TEXT NOT NULL,
    line_number INTEGER,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(file_path)) > 0),
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE conversations (
    conversation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    review_comment_id BIGINT
        REFERENCES review_comments(review_comment_id) ON DELETE SET NULL,
    state conversation_state NOT NULL DEFAULT 'open',
    resolved_by BIGINT REFERENCES reviewers(reviewer_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX conversations_pr_state_idx
    ON conversations(pull_request_id, state);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    commit_id BIGINT NOT NULL
        REFERENCES commits(commit_id),
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (pull_request_id, check_name, commit_id),
    CHECK (length(trim(check_name)) > 0)
);

CREATE INDEX status_checks_pr_name_idx
    ON status_checks(pull_request_id, check_name, passed);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0,
    require_conversations_resolved BOOLEAN NOT NULL DEFAULT TRUE,
    allow_direct_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_branch_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_approvals BETWEEN 0 AND 100)
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL
        REFERENCES branch_protection_policies(policy_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE OR REPLACE FUNCTION prevent_protected_branch_push()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    protected BOOLEAN;
    direct_push_allowed BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM branch_protection_policies p
        WHERE p.branch_id = NEW.branch_id
    )
    INTO protected;

    SELECT COALESCE(
        (
            SELECT p.allow_direct_push
            FROM branch_protection_policies p
            WHERE p.branch_id = NEW.branch_id
        ),
        FALSE
    )
    INTO direct_push_allowed;

    IF protected AND NOT direct_push_allowed THEN
        RAISE EXCEPTION
            'Direct commits to protected branch % are prohibited',
            NEW.branch_id;
    END IF;

    RETURN NEW;
END;
$$;

-- The trigger demonstrates database-level enforcement.
-- Application workflows normally insert commits through a PR process,
-- while direct writes to a protected branch remain blocked.
CREATE TRIGGER protected_branch_commit_guard
BEFORE INSERT ON commits
FOR EACH ROW
EXECUTE FUNCTION prevent_protected_branch_push();

CREATE OR REPLACE FUNCTION prevent_invalid_review()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    reviewer_is_active BOOLEAN;
    review_commit_in_pr BOOLEAN;
BEGIN
    SELECT active
    INTO reviewer_is_active
    FROM reviewers
    WHERE reviewer_id = NEW.reviewer_id;

    IF NOT COALESCE(reviewer_is_active, FALSE) THEN
        RAISE EXCEPTION
            'Inactive or unknown reviewer % cannot submit a review',
            NEW.reviewer_id;
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM pull_request_commits pc
        WHERE pc.pull_request_id = NEW.pull_request_id
          AND pc.commit_id = NEW.reviewed_commit_id
    )
    INTO review_commit_in_pr;

    IF NOT review_commit_in_pr THEN
        RAISE EXCEPTION
            'Review must reference a commit belonging to the Pull Request';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER review_validation_guard
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_review();

CREATE OR REPLACE FUNCTION prevent_invalid_merge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    policy RECORD;
    latest_commit BIGINT;
    approval_count INTEGER;
    unresolved_count INTEGER;
    failed_checks INTEGER;
    requested_changes INTEGER;
BEGIN
    IF NEW.state <> 'merged' OR OLD.state = 'merged' THEN
        RETURN NEW;
    END IF;

    SELECT
        p.required_approvals,
        p.require_conversations_resolved
    INTO policy
    FROM branch_protection_policies p
    WHERE p.branch_id = NEW.target_branch_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Protected branch policy is required before merge';
    END IF;

    SELECT pc.commit_id
    INTO latest_commit
    FROM pull_request_commits pc
    WHERE pc.pull_request_id = NEW.pull_request_id
    ORDER BY pc.position DESC
    LIMIT 1;

    IF latest_commit IS NULL THEN
        RAISE EXCEPTION 'Cannot merge a Pull Request without commits';
    END IF;

    SELECT COUNT(DISTINCT reviewer_id)
    INTO approval_count
    FROM reviews
    WHERE pull_request_id = NEW.pull_request_id
      AND reviewed_commit_id = latest_commit
      AND state = 'approved';

    IF approval_count < policy.required_approvals THEN
        RAISE EXCEPTION
            'Merge requires % current approvals; found %',
            policy.required_approvals,
            approval_count;
    END IF;

    SELECT COUNT(*)
    INTO requested_changes
    FROM reviews
    WHERE pull_request_id = NEW.pull_request_id
      AND state = 'changes_requested';

    IF requested_changes > 0 THEN
        RAISE EXCEPTION 'Requested changes remain on the Pull Request';
    END IF;

    IF policy.require_conversations_resolved THEN
        SELECT COUNT(*)
        INTO unresolved_count
        FROM conversations
        WHERE pull_request_id = NEW.pull_request_id
          AND state = 'open';

        IF unresolved_count > 0 THEN
            RAISE EXCEPTION
                'Cannot merge with % unresolved conversation(s)',
                unresolved_count;
        END IF;
    END IF;

    SELECT COUNT(*)
    INTO failed_checks
    FROM required_status_checks rsc
    WHERE rsc.policy_id = (
        SELECT policy_id
        FROM branch_protection_policies
        WHERE branch_id = NEW.target_branch_id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM status_checks sc
        WHERE sc.pull_request_id = NEW.pull_request_id
          AND sc.check_name = rsc.check_name
          AND sc.commit_id = latest_commit
          AND sc.passed = TRUE
    );

    IF failed_checks > 0 THEN
        RAISE EXCEPTION
            '% required status check(s) are missing or failing',
            failed_checks;
    END IF;

    NEW.merged_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER merge_policy_guard
BEFORE UPDATE OF state ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_merge();

CREATE OR REPLACE VIEW merge_eligibility AS
WITH latest_commit AS (
    SELECT
        pc.pull_request_id,
        pc.commit_id,
        ROW_NUMBER() OVER (
            PARTITION BY pc.pull_request_id
            ORDER BY pc.position DESC
        ) AS rn
    FROM pull_request_commits pc
),
current_approvals AS (
    SELECT
        r.pull_request_id,
        COUNT(DISTINCT r.reviewer_id) AS approval_count
    FROM reviews r
    JOIN latest_commit lc
      ON lc.pull_request_id = r.pull_request_id
     AND lc.commit_id = r.reviewed_commit_id
     AND lc.rn = 1
    WHERE r.state = 'approved'
    GROUP BY r.pull_request_id
),
open_conversations AS (
    SELECT
        pull_request_id,
        COUNT(*) AS open_count
    FROM conversations
    WHERE state = 'open'
    GROUP BY pull_request_id
),
required_checks AS (
    SELECT
        pr.pull_request_id,
        COUNT(rsc.check_name) AS required_count,
        COUNT(sc.status_check_id)
            FILTER (WHERE sc.passed = TRUE) AS passing_count
    FROM pull_requests pr
    JOIN branch_protection_policies bpp
      ON bpp.branch_id = pr.target_branch_id
    JOIN required_status_checks rsc
      ON rsc.policy_id = bpp.policy_id
    LEFT JOIN latest_commit lc
      ON lc.pull_request_id = pr.pull_request_id
     AND lc.rn = 1
    LEFT JOIN status_checks sc
      ON sc.pull_request_id = pr.pull_request_id
     AND sc.check_name = rsc.check_name
     AND sc.commit_id = lc.commit_id
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    r.repository_name,
    pr.number,
    pr.title,
    pr.state,
    COALESCE(ca.approval_count, 0) AS approvals,
    bpp.required_approvals,
    COALESCE(oc.open_count, 0) AS open_conversations,
    COALESCE(rc.required_count, 0) AS required_checks,
    COALESCE(rc.passing_count, 0) AS passing_checks,
    (
        pr.state = 'open'
        AND NOT pr.is_draft
        AND COALESCE(ca.approval_count, 0) >= bpp.required_approvals
        AND COALESCE(oc.open_count, 0) = 0
        AND COALESCE(rc.passing_count, 0) = COALESCE(rc.required_count, 0)
        AND NOT EXISTS (
            SELECT 1
            FROM reviews requested
            WHERE requested.pull_request_id = pr.pull_request_id
              AND requested.state = 'changes_requested'
        )
    ) AS eligible
FROM pull_requests pr
JOIN repositories r
  ON r.repository_id = pr.repository_id
JOIN branch_protection_policies bpp
  ON bpp.branch_id = pr.target_branch_id
LEFT JOIN current_approvals ca
  ON ca.pull_request_id = pr.pull_request_id
LEFT JOIN open_conversations oc
  ON oc.pull_request_id = pr.pull_request_id
LEFT JOIN required_checks rc
  ON rc.pull_request_id = pr.pull_request_id;

BEGIN;

INSERT INTO repositories (
    repository_name,
    product_stage,
    vision,
    mission
)
VALUES (
    'payment-platform',
    'delivery',
    'Make repository change management predictable, reviewable, and safe.',
    'Connect product intent with controlled engineering delivery.'
);

INSERT INTO strategic_choices (repository_id, choice_text)
SELECT repository_id, choice_text
FROM repositories
CROSS JOIN (
    VALUES
        ('Use Pull Requests as the controlled change-entry workflow.'),
        ('Separate review decisions from repository enforcement.'),
        ('Tie approvals to the exact commit being evaluated.'),
        ('Use automated checks as objective merge evidence.'),
        ('Protect critical branches from uncontrolled writes.')
) AS choices(choice_text)
WHERE repository_name = 'payment-platform';

INSERT INTO product_goals (
    repository_id,
    goal_name,
    metric_name,
    target_value,
    current_value
)
SELECT
    repository_id,
    goal_name,
    metric_name,
    target_value,
    current_value
FROM repositories
CROSS JOIN (
    VALUES
        ('review_coverage', 'production PRs reviewed', 95.0, 92.0),
        ('compliant_merges', 'policy-compliant merges', 90.0, 94.0),
        ('unresolved_conversations',
         'unresolved conversations on merged PRs',
         1.0,
         0.5)
) AS goals(
    goal_name,
    metric_name,
    target_value,
    current_value
)
WHERE repository_name = 'payment-platform';

INSERT INTO branches (
    repository_id,
    branch_name,
    is_default
)
SELECT
    repository_id,
    branch_name,
    is_default
FROM repositories
CROSS JOIN (
    VALUES
        ('main', TRUE),
        ('feature/product-strategy', FALSE),
        ('feature/security-policy', FALSE)
) AS branch_data(branch_name, is_default)
WHERE repository_name = 'payment-platform';

INSERT INTO reviewers (username, active, administrator)
VALUES
    ('maya', TRUE, FALSE),
    ('rohan', TRUE, FALSE),
    ('platform-admin', TRUE, TRUE);

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_conversations_resolved,
    allow_direct_push,
    allow_force_push,
    allow_branch_deletion,
    require_linear_history,
    allow_administrator_bypass
)
SELECT
    branch_id,
    2,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    TRUE,
    FALSE
FROM branches
WHERE branch_name = 'main';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT
    policy_id,
    check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES
        ('unit-tests'),
        ('security-scan'),
        ('product-policy')
) AS checks(check_name);

-- The protected-branch trigger prevents a direct commit to main.
-- Commits used by Pull Requests are therefore created on feature branches.
INSERT INTO commits (
    branch_id,
    sha,
    message,
    author
)
SELECT
    b.branch_id,
    c.sha,
    c.message,
    c.author
FROM branches b
CROSS JOIN (
    VALUES
        ('a1b2c3d4',
         'Implement product strategy governance model',
         'atul'),
        ('e5f6a7b8',
         'Address review findings',
         'atul')
) AS c(sha, message, author)
WHERE b.branch_name = 'feature/product-strategy';

INSERT INTO pull_requests (
    repository_id,
    number,
    title,
    author,
    source_branch_id,
    target_branch_id,
    state,
    is_draft,
    merge_strategy,
    base_synchronized_at
)
SELECT
    r.repository_id,
    142,
    'Introduce product strategy governance metrics',
    'atul',
    source_branch.branch_id,
    target_branch.branch_id,
    'open',
    FALSE,
    'squash',
    now()
FROM repositories r
JOIN branches source_branch
  ON source_branch.repository_id = r.repository_id
 AND source_branch.branch_name = 'feature/product-strategy'
JOIN branches target_branch
  ON target_branch.repository_id = r.repository_id
 AND target_branch.branch_name = 'main'
WHERE r.repository_name = 'payment-platform';

INSERT INTO pull_request_commits (
    pull_request_id,
    commit_id,
    position
)
SELECT
    pr.pull_request_id,
    c.commit_id,
    ROW_NUMBER() OVER (ORDER BY c.committed_at, c.commit_id)
FROM pull_requests pr
JOIN commits c
  ON c.branch_id = pr.source_branch_id
WHERE pr.number = 142;

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    reviewed_commit_id,
    state,
    review_body
)
SELECT
    pr.pull_request_id,
    rv.reviewer_id,
    c.commit_id,
    'approved',
    'Architecture and product policy are acceptable.'
FROM pull_requests pr
JOIN reviewers rv
  ON rv.username = 'maya'
JOIN commits c
  ON c.sha = 'e5f6a7b8'
WHERE pr.number = 142;

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    reviewed_commit_id,
    state,
    review_body
)
SELECT
    pr.pull_request_id,
    rv.reviewer_id,
    c.commit_id,
    'approved',
    'Security and delivery controls are acceptable.'
FROM pull_requests pr
JOIN reviewers rv
  ON rv.username = 'rohan'
JOIN commits c
  ON c.sha = 'e5f6a7b8'
WHERE pr.number = 142;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    passed,
    commit_id
)
SELECT
    pr.pull_request_id,
    checks.check_name,
    TRUE,
    c.commit_id
FROM pull_requests pr
JOIN commits c
  ON c.sha = 'e5f6a7b8'
CROSS JOIN (
    VALUES
        ('unit-tests'),
        ('security-scan'),
        ('product-policy')
) AS checks(check_name)
WHERE pr.number = 142;

COMMIT;

-- Product-strategy reporting.
SELECT
    repository_name,
    goal_name,
    metric_name,
    current_value,
    target_value,
    current_value >= target_value AS achieved
FROM repositories r
JOIN product_goals g
  ON g.repository_id = r.repository_id
ORDER BY goal_name;

-- Pull Request retrieval and merge eligibility.
SELECT
    repository_name,
    number,
    title,
    state,
    approvals,
    required_approvals,
    required_checks,
    passing_checks,
    open_conversations,
    eligible
FROM merge_eligibility
ORDER BY number;

-- Review quality report.
SELECT
    pr.number,
    pr.title,
    COUNT(DISTINCT rv.review_id) AS total_reviews,
    COUNT(DISTINCT rv.reviewer_id)
        FILTER (WHERE rv.state = 'approved') AS approval_decisions,
    COUNT(DISTINCT rv.review_id)
        FILTER (WHERE rv.state = 'changes_requested') AS change_requests
FROM pull_requests pr
LEFT JOIN reviews rv
  ON rv.pull_request_id = pr.pull_request_id
GROUP BY pr.number, pr.title
ORDER BY pr.number;

-- Status-check coverage.
SELECT
    pr.number,
    pr.title,
    COUNT(sc.status_check_id) AS submitted_checks,
    COUNT(sc.status_check_id)
        FILTER (WHERE sc.passed) AS passing_checks,
    COUNT(sc.status_check_id)
        FILTER (WHERE NOT sc.passed) AS failing_checks
FROM pull_requests pr
LEFT JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
GROUP BY pr.number, pr.title
ORDER BY pr.number;

-- Approval freshness: approvals must reference the current PR head.
WITH latest AS (
    SELECT
        pc.pull_request_id,
        pc.commit_id,
        ROW_NUMBER() OVER (
            PARTITION BY pc.pull_request_id
            ORDER BY pc.position DESC
        ) AS rn
    FROM pull_request_commits pc
)
SELECT
    pr.number,
    pr.title,
    rv.reviewer_id,
    rv.state,
    rv.reviewed_commit_id = latest.commit_id AS current_for_head
FROM pull_requests pr
JOIN reviews rv
  ON rv.pull_request_id = pr.pull_request_id
JOIN latest
  ON latest.pull_request_id = pr.pull_request_id
 AND latest.rn = 1
ORDER BY pr.number, rv.reviewer_id;

-- A valid merge is performed in a transaction. The trigger verifies
-- approvals, status checks, requested changes, and conversations.
BEGIN;

UPDATE pull_requests
SET state = 'merged'
WHERE number = 142
  AND state = 'open';

COMMIT;

-- Verify the final workflow state.
SELECT
    number,
    title,
    state,
    merged_at
FROM pull_requests
WHERE number = 142;

-- The following query exposes protected-branch governance settings.
SELECT
    b.branch_name,
    p.required_approvals,
    p.require_conversations_resolved,
    p.allow_direct_push,
    p.allow_force_push,
    p.allow_branch_deletion,
    p.require_linear_history,
    p.allow_administrator_bypass
FROM branches b
JOIN branch_protection_policies p
  ON p.branch_id = b.branch_id
WHERE b.branch_name = 'main';
