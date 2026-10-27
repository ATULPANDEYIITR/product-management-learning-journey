DROP SCHEMA IF EXISTS technical_debt_lab CASCADE;
CREATE SCHEMA technical_debt_lab;
SET search_path TO technical_debt_lab;

-- Technical debt is tracked separately from Pull Requests, reviews,
-- approvals, automated checks, and branch-level enforcement. This permits
-- debt to be measured even when no active Pull Request exists.

CREATE TYPE debt_category AS ENUM (
    'code',
    'test',
    'architecture',
    'security',
    'infrastructure',
    'documentation'
);

CREATE TYPE debt_status AS ENUM (
    'open',
    'planned',
    'in_progress',
    'resolved',
    'accepted'
);

CREATE TYPE pr_status AS ENUM (
    'draft',
    'open',
    'closed',
    'merged'
);

CREATE TYPE review_state AS ENUM (
    'pending',
    'approved',
    'changes_requested',
    'commented',
    'dismissed'
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(default_branch)) > 0)
);

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (username ~ '^[A-Za-z0-9_.-]+$'),
    CHECK (length(trim(display_name)) > 0)
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) > 0)
);

CREATE UNIQUE INDEX one_default_branch_per_repository
ON branches(repository_id)
WHERE is_default AND NOT is_deleted;

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_id BIGINT NOT NULL REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    commit_sha CHAR(8) NOT NULL,
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    commit_message TEXT NOT NULL,
    changed_files INTEGER NOT NULL,
    additions INTEGER NOT NULL,
    deletions INTEGER NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, commit_sha),
    CHECK (changed_files >= 0),
    CHECK (additions >= 0),
    CHECK (deletions >= 0),
    CHECK (length(trim(commit_message)) > 0)
);

CREATE TABLE technical_debt (
    debt_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    title TEXT NOT NULL,
    category debt_category NOT NULL,
    status debt_status NOT NULL DEFAULT 'open',
    description TEXT NOT NULL,
    owner_id BIGINT NOT NULL REFERENCES users(user_id),
    principal_hours NUMERIC(10,2) NOT NULL,
    remediation_hours NUMERIC(10,2) NOT NULL,
    monthly_interest_hours NUMERIC(10,2) NOT NULL DEFAULT 0,
    impact SMALLINT NOT NULL,
    probability NUMERIC(4,3) NOT NULL,
    urgency SMALLINT NOT NULL,
    security_exposure SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(description)) > 0),
    CHECK (principal_hours > 0),
    CHECK (remediation_hours > 0),
    CHECK (monthly_interest_hours >= 0),
    CHECK (impact BETWEEN 1 AND 10),
    CHECK (probability BETWEEN 0 AND 1),
    CHECK (urgency BETWEEN 1 AND 10),
    CHECK (security_exposure BETWEEN 0 AND 10),
    CHECK (
        (status = 'resolved' AND resolved_at IS NOT NULL)
        OR status <> 'resolved'
    )
);

CREATE TABLE debt_components (
    debt_id BIGINT NOT NULL REFERENCES technical_debt(debt_id)
        ON DELETE CASCADE,
    component_name TEXT NOT NULL,
    PRIMARY KEY (debt_id, component_name),
    CHECK (length(trim(component_name)) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    status pr_status NOT NULL DEFAULT 'draft',
    merge_strategy TEXT NOT NULL DEFAULT 'squash',
    synchronized_with_base BOOLEAN NOT NULL DEFAULT TRUE,
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ,
    UNIQUE (repository_id, number),
    CHECK (length(trim(title)) > 0),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (merge_strategy IN ('merge', 'squash', 'rebase')),
    CHECK (
        (status IN ('closed', 'merged') AND closed_at IS NOT NULL)
        OR status NOT IN ('closed', 'merged')
    )
);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commits(commit_id),
    sequence_number INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, sequence_number),
    CHECK (sequence_number > 0)
);

CREATE TABLE pull_request_debt (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    debt_id BIGINT NOT NULL REFERENCES technical_debt(debt_id),
    relationship TEXT NOT NULL DEFAULT 'introduces',
    PRIMARY KEY (pull_request_id, debt_id),
    CHECK (relationship IN ('introduces', 'remediates', 'documents'))
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(user_id),
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    dismissed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, reviewer_id, submitted_at)
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(file_path)) > 0),
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE conversations (
    conversation_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    CHECK (length(trim(subject)) > 0),
    CHECK (
        (resolved = TRUE AND resolved_at IS NOT NULL)
        OR resolved = FALSE
    )
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    required BOOLEAN NOT NULL DEFAULT TRUE,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (pull_request_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE
        REFERENCES branches(branch_id) ON DELETE CASCADE,
    required_reviews INTEGER NOT NULL DEFAULT 0,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE,
    max_new_debt_score NUMERIC(12,2) NOT NULL DEFAULT 999999,
    CHECK (required_reviews >= 0),
    CHECK (max_new_debt_score >= 0)
);

CREATE TABLE approval_requirements (
    requirement_id BIGSERIAL PRIMARY KEY,
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    role_name TEXT NOT NULL,
    required_count INTEGER NOT NULL,
    UNIQUE (policy_id, role_name),
    CHECK (length(trim(role_name)) > 0),
    CHECK (required_count > 0)
);

CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    role_name TEXT NOT NULL,
    PRIMARY KEY (user_id, repository_id, role_name),
    CHECK (role_name IN ('author', 'reviewer', 'maintainer', 'administrator'))
);

CREATE INDEX idx_debt_repository_status
ON technical_debt(repository_id, status);

CREATE INDEX idx_debt_priority_inputs
ON technical_debt(repository_id, security_exposure, urgency, impact);

CREATE INDEX idx_pr_target_status
ON pull_requests(target_branch_id, status);

CREATE INDEX idx_reviews_pr_state
ON reviews(pull_request_id, state);

CREATE INDEX idx_status_checks_pr_required
ON status_checks(pull_request_id, required, passed);

CREATE INDEX idx_conversations_pr_unresolved
ON conversations(pull_request_id, resolved);

CREATE OR REPLACE FUNCTION technical_debt_risk_score(
    p_impact INTEGER,
    p_probability NUMERIC,
    p_urgency INTEGER,
    p_security_exposure INTEGER
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT round(
        p_impact * p_probability * 10
        + p_urgency * 2
        + p_security_exposure * 3,
        2
    );
$$;

CREATE OR REPLACE FUNCTION technical_debt_priority_score(
    p_monthly_interest NUMERIC,
    p_impact INTEGER,
    p_probability NUMERIC,
    p_urgency INTEGER,
    p_security_exposure INTEGER,
    p_remediation_hours NUMERIC
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT round(
        (
            p_monthly_interest * 4
            + technical_debt_risk_score(
                p_impact,
                p_probability,
                p_urgency,
                p_security_exposure
            ) * 2
            + p_security_exposure * 5
        ) / greatest(p_remediation_hours, 1),
        2
    );
$$;

CREATE OR REPLACE FUNCTION prevent_invalid_debt_resolution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'resolved' AND NEW.resolved_at IS NULL THEN
        NEW.resolved_at := now();
    END IF;

    IF NEW.status <> 'resolved' THEN
        NEW.resolved_at := NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_debt_resolution
BEFORE INSERT OR UPDATE OF status, resolved_at
ON technical_debt
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_debt_resolution();

CREATE OR REPLACE FUNCTION validate_pr_branch_repository()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_repository BIGINT;
    target_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO source_repository
    FROM branches
    WHERE branch_id = NEW.source_branch_id;

    SELECT repository_id
    INTO target_repository
    FROM branches
    WHERE branch_id = NEW.target_branch_id;

    IF source_repository IS DISTINCT FROM NEW.repository_id
       OR target_repository IS DISTINCT FROM NEW.repository_id THEN
        RAISE EXCEPTION
            'Pull Request branches must belong to the Pull Request repository';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pr_repository
BEFORE INSERT OR UPDATE
ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION validate_pr_branch_repository();

CREATE OR REPLACE FUNCTION validate_pr_debt_repository()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    pr_repository BIGINT;
    debt_repository BIGINT;
BEGIN
    SELECT repository_id
    INTO pr_repository
    FROM pull_requests
    WHERE pull_request_id = NEW.pull_request_id;

    SELECT repository_id
    INTO debt_repository
    FROM technical_debt
    WHERE debt_id = NEW.debt_id;

    IF pr_repository IS DISTINCT FROM debt_repository THEN
        RAISE EXCEPTION
            'Pull Request and technical debt must belong to the same repository';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pr_debt_repository
BEFORE INSERT OR UPDATE
ON pull_request_debt
FOR EACH ROW
EXECUTE FUNCTION validate_pr_debt_repository();

CREATE OR REPLACE VIEW debt_priority_view AS
SELECT
    d.debt_id,
    d.repository_id,
    r.repository_name,
    d.title,
    d.category,
    d.status,
    d.owner_id,
    d.principal_hours,
    d.remediation_hours,
    d.monthly_interest_hours,
    technical_debt_risk_score(
        d.impact,
        d.probability,
        d.urgency,
        d.security_exposure
    ) AS risk_score,
    technical_debt_priority_score(
        d.monthly_interest_hours,
        d.impact,
        d.probability,
        d.urgency,
        d.security_exposure,
        d.remediation_hours
    ) AS priority_score,
    CASE
        WHEN technical_debt_priority_score(
            d.monthly_interest_hours,
            d.impact,
            d.probability,
            d.urgency,
            d.security_exposure,
            d.remediation_hours
        ) >= 70 THEN 'critical'
        WHEN technical_debt_priority_score(
            d.monthly_interest_hours,
            d.impact,
            d.probability,
            d.urgency,
            d.security_exposure,
            d.remediation_hours
        ) >= 40 THEN 'high'
        WHEN technical_debt_priority_score(
            d.monthly_interest_hours,
            d.impact,
            d.probability,
            d.urgency,
            d.security_exposure,
            d.remediation_hours
        ) >= 20 THEN 'medium'
        ELSE 'low'
    END AS priority
FROM technical_debt d
JOIN repositories r ON r.repository_id = d.repository_id;

CREATE OR REPLACE FUNCTION calculate_pr_debt_score(
    p_pull_request_id BIGINT
)
RETURNS NUMERIC
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(
        SUM(dp.priority_score),
        0
    )
    FROM pull_request_debt pd
    JOIN debt_priority_view dp ON dp.debt_id = pd.debt_id
    WHERE pd.pull_request_id = p_pull_request_id;
$$;

CREATE OR REPLACE FUNCTION evaluate_merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    pr RECORD;
    policy RECORD;
    approvals INTEGER;
    requested_changes INTEGER;
    unresolved_conversations INTEGER;
    failed_required_checks INTEGER;
    missing_required_checks INTEGER;
    debt_score NUMERIC;
BEGIN
    SELECT
        p.*,
        source.branch_name AS source_branch,
        target.branch_name AS target_branch
    INTO pr
    FROM pull_requests p
    JOIN branches source ON source.branch_id = p.source_branch_id
    JOIN branches target ON target.branch_id = p.target_branch_id
    WHERE p.pull_request_id = p_pull_request_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Pull Request does not exist';
        RETURN;
    END IF;

    SELECT *
    INTO policy
    FROM branch_protection_policies bp
    WHERE bp.branch_id = pr.target_branch_id;

    IF pr.status <> 'open' THEN
        RETURN QUERY SELECT FALSE, 'Pull Request is not open';
    END IF;

    IF pr.synchronized_with_base = FALSE THEN
        RETURN QUERY SELECT FALSE, 'Base branch synchronization is stale';
    END IF;

    IF pr.has_conflicts THEN
        RETURN QUERY SELECT FALSE, 'Merge conflicts are unresolved';
    END IF;

    IF policy IS NULL THEN
        RETURN QUERY SELECT TRUE, 'No branch protection policy applies';
        RETURN;
    END IF;

    SELECT count(*)
    INTO approvals
    FROM reviews
    WHERE pull_request_id = p_pull_request_id
      AND state = 'approved'
      AND dismissed_at IS NULL;

    IF approvals < policy.required_reviews THEN
        RETURN QUERY SELECT
            FALSE,
            format(
                'Required approvals not met: %s/%s',
                approvals,
                policy.required_reviews
            );
    END IF;

    SELECT count(*)
    INTO requested_changes
    FROM reviews
    WHERE pull_request_id = p_pull_request_id
      AND state = 'changes_requested'
      AND dismissed_at IS NULL;

    IF requested_changes > 0 THEN
        RETURN QUERY SELECT FALSE, 'Reviewer requested changes';
    END IF;

    SELECT count(*)
    INTO unresolved_conversations
    FROM conversations
    WHERE pull_request_id = p_pull_request_id
      AND resolved = FALSE;

    IF policy.require_conversation_resolution
       AND unresolved_conversations > 0 THEN
        RETURN QUERY SELECT FALSE, 'Unresolved review conversations remain';
    END IF;

    SELECT count(*)
    INTO failed_required_checks
    FROM status_checks
    WHERE pull_request_id = p_pull_request_id
      AND required = TRUE
      AND passed = FALSE;

    IF failed_required_checks > 0 THEN
        RETURN QUERY SELECT FALSE, 'A required status check failed';
    END IF;

    SELECT count(*)
    INTO missing_required_checks
    FROM (
        SELECT unnest(
            ARRAY(
                SELECT check_name
                FROM status_checks
                WHERE pull_request_id = p_pull_request_id
                  AND required = TRUE
            )
        ) AS check_name
    ) checks
    WHERE checks.check_name IS NULL;

    debt_score := calculate_pr_debt_score(p_pull_request_id);

    IF debt_score > policy.max_new_debt_score THEN
        RETURN QUERY SELECT
            FALSE,
            format(
                'Technical debt score %.2f exceeds %.2f',
                debt_score,
                policy.max_new_debt_score
            );
    END IF;

    RETURN QUERY SELECT TRUE, 'All configured merge conditions satisfied';
END;
$$;

CREATE OR REPLACE FUNCTION repository_debt_metrics(
    p_repository_id BIGINT
)
RETURNS TABLE (
    active_items BIGINT,
    principal_hours NUMERIC,
    remediation_hours NUMERIC,
    monthly_interest_hours NUMERIC,
    weighted_risk NUMERIC
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        count(*),
        round(coalesce(sum(principal_hours), 0), 2),
        round(coalesce(sum(remediation_hours), 0), 2),
        round(coalesce(sum(monthly_interest_hours), 0), 2),
        round(
            coalesce(
                sum(
                    technical_debt_risk_score(
                        impact,
                        probability,
                        urgency,
                        security_exposure
                    )
                ),
                0
            ),
            2
        )
    FROM technical_debt
    WHERE repository_id = p_repository_id
      AND status NOT IN ('resolved', 'accepted');
$$;

INSERT INTO repositories(repository_name, default_branch)
VALUES ('payments-platform', 'main');

INSERT INTO users(username, display_name)
VALUES
    ('nina', 'Nina Sharma'),
    ('omar', 'Omar Khan'),
    ('priya', 'Priya Singh'),
    ('securitybot', 'Security Automation'),
    ('platform', 'Platform Team');

INSERT INTO branches(repository_id, branch_name, is_default, is_protected)
SELECT repository_id, 'main', TRUE, TRUE
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO branches(repository_id, branch_name)
SELECT repository_id, 'develop'
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO branches(repository_id, branch_name)
SELECT repository_id, 'feature/payment-refactor'
FROM repositories
WHERE repository_name = 'payments-platform';

INSERT INTO technical_debt (
    repository_id,
    title,
    category,
    description,
    owner_id,
    principal_hours,
    remediation_hours,
    monthly_interest_hours,
    impact,
    probability,
    urgency,
    security_exposure
)
SELECT
    r.repository_id,
    x.title,
    x.category::debt_category,
    x.description,
    u.user_id,
    x.principal_hours,
    x.remediation_hours,
    x.monthly_interest_hours,
    x.impact,
    x.probability,
    x.urgency,
    x.security_exposure
FROM repositories r
CROSS JOIN (
    VALUES
    (
        'Duplicated payment validation',
        'code',
        'Validation logic is repeated across payment paths.',
        'nina',
        12.00, 20.00, 8.00, 8, 0.800, 8, 4
    ),
    (
        'Missing payment failure tests',
        'test',
        'Timeout and retry behavior lacks integration coverage.',
        'priya',
        8.00, 16.00, 6.00, 7, 0.700, 7, 3
    ),
    (
        'Static integration credential',
        'security',
        'A legacy integration uses a credential embedded in test configuration.',
        'securitybot',
        3.00, 6.00, 2.00, 10, 0.500, 10, 10
    ),
    (
        'Manual deployment sequence',
        'infrastructure',
        'Production deployment requires undocumented manual ordering.',
        'platform',
        5.00, 10.00, 3.00, 6, 0.600, 5, 2
    )
) AS x(
    title,
    category,
    description,
    owner_username,
    principal_hours,
    remediation_hours,
    monthly_interest_hours,
    impact,
    probability,
    urgency,
    security_exposure
)
JOIN users u ON u.username = x.owner_username
WHERE r.repository_name = 'payments-platform';

INSERT INTO debt_components(debt_id, component_name)
SELECT debt_id, component_name
FROM technical_debt
CROSS JOIN LATERAL (
    VALUES
        ('payments'),
        ('checkout')
) AS c(component_name)
WHERE title = 'Duplicated payment validation';

INSERT INTO debt_components(debt_id, component_name)
SELECT debt_id, 'payment-integration-tests'
FROM technical_debt
WHERE title = 'Missing payment failure tests';

INSERT INTO debt_components(debt_id, component_name)
SELECT debt_id, 'integration-tests'
FROM technical_debt
WHERE title = 'Static integration credential';

INSERT INTO debt_components(debt_id, component_name)
SELECT debt_id, 'deployment'
FROM technical_debt
WHERE title = 'Manual deployment sequence';

INSERT INTO commits (
    repository_id,
    branch_id,
    commit_sha,
    author_id,
    commit_message,
    changed_files,
    additions,
    deletions
)
SELECT
    r.repository_id,
    b.branch_id,
    c.commit_sha,
    u.user_id,
    c.commit_message,
    c.changed_files,
    c.additions,
    c.deletions
FROM repositories r
JOIN branches b
    ON b.repository_id = r.repository_id
   AND b.branch_name = 'feature/payment-refactor'
CROSS JOIN (
    VALUES
        ('abc12345', 'refactor payment validation', 'nina', 8, 180, 120),
        ('def67890', 'add payment failure tests', 'nina', 5, 140, 15)
) AS c(
    commit_sha,
    commit_message,
    author_username,
    changed_files,
    additions,
    deletions
)
JOIN users u ON u.username = c.author_username
WHERE r.repository_name = 'payments-platform';

INSERT INTO pull_requests (
    repository_id,
    number,
    title,
    author_id,
    source_branch_id,
    target_branch_id,
    status,
    merge_strategy,
    synchronized_with_base,
    has_conflicts
)
SELECT
    r.repository_id,
    1,
    'Refactor payment validation',
    author.user_id,
    source.branch_id,
    target.branch_id,
    'open',
    'squash',
    TRUE,
    FALSE
FROM repositories r
JOIN users author ON author.username = 'nina'
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/payment-refactor'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
WHERE r.repository_name = 'payments-platform';

INSERT INTO pull_request_commits(pull_request_id, commit_id, sequence_number)
SELECT
    pr.pull_request_id,
    c.commit_id,
    row_number() OVER (ORDER BY c.committed_at)
FROM pull_requests pr
JOIN commits c
    ON c.repository_id = pr.repository_id
JOIN branches b
    ON b.branch_id = c.branch_id
WHERE pr.number = 1
  AND b.branch_name = 'feature/payment-refactor';

INSERT INTO pull_request_debt(pull_request_id, debt_id, relationship)
SELECT
    pr.pull_request_id,
    d.debt_id,
    x.relationship
FROM pull_requests pr
JOIN technical_debt d ON d.repository_id = pr.repository_id
CROSS JOIN (
    VALUES
        ('Duplicated payment validation', 'remediates'),
        ('Missing payment failure tests', 'remediates')
) AS x(title, relationship)
WHERE pr.number = 1
  AND d.title = x.title;

INSERT INTO reviews(
    pull_request_id,
    reviewer_id,
    state
)
SELECT
    pr.pull_request_id,
    u.user_id,
    x.state::review_state
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('omar', 'approved'),
        ('priya', 'changes_requested')
) AS x(username, state)
JOIN users u ON u.username = x.username
WHERE pr.number = 1;

INSERT INTO review_comments(
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
SELECT
    rv.review_id,
    'src/payment/validator.ts',
    84,
    'Add coverage for duplicate payment requests.',
    FALSE
FROM reviews rv
JOIN users u ON u.user_id = rv.reviewer_id
WHERE u.username = 'priya';

INSERT INTO conversations(
    pull_request_id,
    subject,
    resolved
)
SELECT
    pull_request_id,
    'Duplicate payment behavior',
    FALSE
FROM pull_requests
WHERE number = 1;

INSERT INTO status_checks(
    pull_request_id,
    check_name,
    passed,
    required
)
SELECT
    pr.pull_request_id,
    x.check_name,
    x.passed,
    TRUE
FROM pull_requests pr
CROSS JOIN (
    VALUES
        ('unit-tests', TRUE),
        ('security-scan', TRUE),
        ('integration-tests', FALSE)
) AS x(check_name, passed)
WHERE pr.number = 1;

INSERT INTO branch_protection_policies(
    branch_id,
    required_reviews,
    restrict_direct_push,
    restrict_force_push,
    restrict_deletion,
    require_conversation_resolution,
    require_linear_history,
    allow_administrator_bypass,
    max_new_debt_score
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE,
    85.00
FROM branches
WHERE branch_name = 'main';

INSERT INTO approval_requirements(
    policy_id,
    role_name,
    required_count
)
SELECT
    policy_id,
    'reviewer',
    2
FROM branch_protection_policies;

INSERT INTO user_roles(user_id, repository_id, role_name)
SELECT
    u.user_id,
    r.repository_id,
    x.role_name
FROM users u
JOIN repositories r ON r.repository_name = 'payments-platform'
CROSS JOIN (
    VALUES
        ('nina', 'author'),
        ('omar', 'reviewer'),
        ('priya', 'reviewer'),
        ('securitybot', 'administrator'),
        ('platform', 'maintainer')
) AS x(username, role_name)
WHERE u.username = x.username;

-- Ranking query: interest, risk, security exposure, and remediation cost are
-- combined into a decision score rather than using age alone.
SELECT
    debt_id,
    title,
    category,
    status,
    priority,
    risk_score,
    priority_score,
    remediation_hours,
    monthly_interest_hours
FROM debt_priority_view
WHERE repository_id = (
    SELECT repository_id
    FROM repositories
    WHERE repository_name = 'payments-platform'
)
ORDER BY priority_score DESC, remediation_hours ASC;

-- Portfolio-level debt burden.
SELECT *
FROM repository_debt_metrics(
    (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'payments-platform'
    )
);

-- Show how much debt is connected to the Pull Request and whether the PR
-- primarily introduces or remediates existing debt.
SELECT
    pr.number,
    pr.title,
    d.title AS debt_item,
    pd.relationship,
    dp.priority,
    dp.priority_score
FROM pull_requests pr
JOIN pull_request_debt pd
    ON pd.pull_request_id = pr.pull_request_id
JOIN debt_priority_view dp
    ON dp.debt_id = pd.debt_id
JOIN technical_debt d
    ON d.debt_id = pd.debt_id
WHERE pr.number = 1
ORDER BY dp.priority_score DESC;

-- Review and approval state are intentionally separate from branch protection.
SELECT
    pr.number,
    u.username AS reviewer,
    rv.state,
    rv.dismissed_at,
    count(rc.comment_id) AS comment_count
FROM pull_requests pr
JOIN reviews rv ON rv.pull_request_id = pr.pull_request_id
JOIN users u ON u.user_id = rv.reviewer_id
LEFT JOIN review_comments rc ON rc.review_id = rv.review_id
WHERE pr.number = 1
GROUP BY pr.number, u.username, rv.state, rv.dismissed_at
ORDER BY u.username;

-- Required automated checks.
SELECT
    pr.number,
    sc.check_name,
    sc.required,
    sc.passed
FROM pull_requests pr
JOIN status_checks sc ON sc.pull_request_id = pr.pull_request_id
WHERE pr.number = 1
ORDER BY sc.check_name;

-- Merge eligibility is evaluated from the persisted workflow state.
SELECT *
FROM evaluate_merge_eligibility(
    (
        SELECT pull_request_id
        FROM pull_requests
        WHERE number = 1
    )
);

-- Capacity planning uses a 30% technical-debt allocation and selects the
-- highest-priority complete items that fit within that budget.
WITH ranked_debt AS (
    SELECT
        debt_id,
        title,
        remediation_hours,
        priority_score,
        sum(remediation_hours) OVER (
            ORDER BY priority_score DESC
        ) AS cumulative_hours
    FROM debt_priority_view
    WHERE repository_id = (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'payments-platform'
    )
    AND status NOT IN ('resolved', 'accepted')
)
SELECT
    debt_id,
    title,
    remediation_hours,
    priority_score
FROM ranked_debt
WHERE cumulative_hours <= (
    SELECT 80.00 * 0.30
)
ORDER BY priority_score DESC;

-- Transactional remediation example: resolve one debt item only after its
-- remediation state has been explicitly recorded.
BEGIN;

UPDATE technical_debt
SET
    status = 'in_progress'
WHERE title = 'Static integration credential'
  AND status = 'open';

UPDATE technical_debt
SET
    status = 'resolved'
WHERE title = 'Static integration credential'
  AND status = 'in_progress';

COMMIT;

-- Validation query after the transaction.
SELECT
    debt_id,
    title,
    status,
    resolved_at
FROM technical_debt
WHERE title = 'Static integration credential';

-- Demonstrate an accepted debt decision. Accepted debt remains visible in
-- historical records but is excluded from active remediation metrics.
UPDATE technical_debt
SET status = 'accepted'
WHERE title = 'Manual deployment sequence'
  AND status = 'open';

SELECT
    title,
    status,
    priority_score
FROM debt_priority_view
WHERE repository_id = (
    SELECT repository_id
    FROM repositories
    WHERE repository_name = 'payments-platform'
)
ORDER BY priority_score DESC;
