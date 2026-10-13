-- PostgreSQL 15+
-- User story management with personas, acceptance criteria, INVEST,
-- refinement decisions, dependencies, and sprint-readiness evaluation.
--
-- The schema separates product outcomes from acceptance conditions.
-- INVEST is a refinement-quality assessment, not a substitute for testing.

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_backlog;
SET LOCAL search_path TO product_backlog, public;

CREATE TABLE personas (
    persona_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    role_name TEXT NOT NULL,
    usage_context TEXT NOT NULL,
    primary_goal TEXT NOT NULL,
    constraints_text TEXT NOT NULL DEFAULT '',
    CONSTRAINT persona_name_nonempty CHECK (length(trim(name)) > 0),
    CONSTRAINT persona_role_nonempty CHECK (length(trim(role_name)) > 0)
);

CREATE TABLE user_stories (
    story_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    story_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    persona_id BIGINT NOT NULL REFERENCES personas(persona_id),
    user_need TEXT NOT NULL,
    user_value TEXT NOT NULL,
    priority SMALLINT NOT NULL DEFAULT 3,
    story_points INTEGER,
    workflow_state TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT story_key_format
        CHECK (story_key ~ '^[A-Z]+-[0-9]+$'),
    CONSTRAINT story_title_nonempty
        CHECK (length(trim(title)) > 0),
    CONSTRAINT story_need_nonempty
        CHECK (length(trim(user_need)) > 0),
    CONSTRAINT story_value_nonempty
        CHECK (length(trim(user_value)) > 0),
    CONSTRAINT story_priority_range
        CHECK (priority BETWEEN 1 AND 5),
    CONSTRAINT story_points_positive
        CHECK (story_points IS NULL OR story_points > 0),
    CONSTRAINT story_state_valid
        CHECK (workflow_state IN (
            'draft', 'refinement', 'ready',
            'in_progress', 'done', 'blocked'
        ))
);

CREATE TABLE acceptance_criteria (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    story_id BIGINT NOT NULL
        REFERENCES user_stories(story_id) ON DELETE CASCADE,
    criterion_key TEXT NOT NULL,
    criterion_type TEXT NOT NULL DEFAULT 'functional',
    given_context TEXT NOT NULL,
    when_action TEXT NOT NULL,
    then_outcome TEXT NOT NULL,
    is_automated BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT criterion_unique_per_story
        UNIQUE (story_id, criterion_key),
    CONSTRAINT criterion_type_valid
        CHECK (criterion_type IN (
            'functional', 'validation', 'security',
            'performance', 'accessibility', 'error_handling'
        )),
    CONSTRAINT criterion_fields_nonempty
        CHECK (
            length(trim(given_context)) > 0
            AND length(trim(when_action)) > 0
            AND length(trim(then_outcome)) > 0
        )
);

CREATE TABLE invest_assessments (
    story_id BIGINT PRIMARY KEY
        REFERENCES user_stories(story_id) ON DELETE CASCADE,
    independent BOOLEAN NOT NULL DEFAULT TRUE,
    negotiable BOOLEAN NOT NULL DEFAULT TRUE,
    valuable BOOLEAN NOT NULL DEFAULT TRUE,
    estimable BOOLEAN NOT NULL DEFAULT TRUE,
    small BOOLEAN NOT NULL DEFAULT TRUE,
    testable BOOLEAN NOT NULL DEFAULT TRUE,
    assessed_by TEXT NOT NULL,
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    assessment_notes TEXT NOT NULL DEFAULT '',
    CONSTRAINT assessed_by_nonempty
        CHECK (length(trim(assessed_by)) > 0)
);

CREATE TABLE story_dependencies (
    story_id BIGINT NOT NULL
        REFERENCES user_stories(story_id) ON DELETE CASCADE,
    depends_on_story_id BIGINT NOT NULL
        REFERENCES user_stories(story_id) ON DELETE RESTRICT,
    dependency_reason TEXT NOT NULL,
    PRIMARY KEY (story_id, depends_on_story_id),
    CONSTRAINT no_self_dependency
        CHECK (story_id <> depends_on_story_id)
);

CREATE TABLE refinement_reviews (
    refinement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    story_id BIGINT NOT NULL
        REFERENCES user_stories(story_id) ON DELETE CASCADE,
    reviewer_name TEXT NOT NULL,
    decision TEXT NOT NULL,
    findings TEXT NOT NULL DEFAULT '',
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT refinement_decision_valid
        CHECK (decision IN ('accept', 'request_changes', 'reject')),
    CONSTRAINT reviewer_name_nonempty
        CHECK (length(trim(reviewer_name)) > 0)
);

CREATE TABLE acceptance_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    criterion_id BIGINT NOT NULL
        REFERENCES acceptance_criteria(criterion_id) ON DELETE CASCADE,
    execution_reference TEXT NOT NULL,
    result_state TEXT NOT NULL,
    observed_outcome TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT result_state_valid
        CHECK (result_state IN ('passed', 'failed', 'blocked', 'not_run')),
    CONSTRAINT execution_reference_nonempty
        CHECK (length(trim(execution_reference)) > 0)
);

CREATE INDEX user_stories_state_priority_idx
    ON user_stories(workflow_state, priority, story_key);

CREATE INDEX acceptance_criteria_story_idx
    ON acceptance_criteria(story_id, criterion_type);

CREATE INDEX story_dependencies_reverse_idx
    ON story_dependencies(depends_on_story_id, story_id);

CREATE INDEX refinement_reviews_latest_idx
    ON refinement_reviews(story_id, reviewed_at DESC);

CREATE INDEX acceptance_results_latest_idx
    ON acceptance_results(criterion_id, executed_at DESC);

-- State transitions are validated by the database, not only by the UI.
CREATE OR REPLACE FUNCTION enforce_story_state_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.workflow_state = OLD.workflow_state THEN
        NEW.updated_at := now();
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.workflow_state = 'draft'
            AND NEW.workflow_state IN ('refinement', 'blocked'))
        OR
        (OLD.workflow_state = 'refinement'
            AND NEW.workflow_state IN ('draft', 'ready', 'blocked'))
        OR
        (OLD.workflow_state = 'ready'
            AND NEW.workflow_state IN ('in_progress', 'refinement', 'blocked'))
        OR
        (OLD.workflow_state = 'in_progress'
            AND NEW.workflow_state IN ('done', 'blocked', 'refinement'))
        OR
        (OLD.workflow_state = 'blocked'
            AND NEW.workflow_state IN ('refinement', 'ready'))
    ) THEN
        RAISE EXCEPTION
            'Invalid story transition: % -> %',
            OLD.workflow_state, NEW.workflow_state;
    END IF;

    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER user_story_state_transition_guard
BEFORE UPDATE OF workflow_state ON user_stories
FOR EACH ROW
EXECUTE FUNCTION enforce_story_state_transition();

-- This view reports data-quality and refinement readiness.
-- It does not claim that the story is implemented or tested.
CREATE OR REPLACE VIEW story_quality AS
SELECT
    s.story_key,
    s.title,
    s.workflow_state,
    s.priority,
    s.story_points,
    p.role_name AS persona_role,
    COUNT(DISTINCT c.criterion_id) AS criterion_count,
    COALESCE(
        bool_and(
            i.independent AND i.negotiable AND i.valuable
            AND i.estimable AND i.small AND i.testable
        ),
        FALSE
    ) AS invest_passes,
    (
        COUNT(DISTINCT c.criterion_id) > 0
        AND COALESCE(
            bool_and(
                i.independent AND i.negotiable AND i.valuable
                AND i.estimable AND i.small AND i.testable
            ),
            FALSE
        )
    ) AS refinement_quality_passes
FROM user_stories s
JOIN personas p ON p.persona_id = s.persona_id
LEFT JOIN acceptance_criteria c ON c.story_id = s.story_id
LEFT JOIN invest_assessments i ON i.story_id = s.story_id
GROUP BY
    s.story_id, s.story_key, s.title, s.workflow_state,
    s.priority, s.story_points, p.role_name;

-- Sprint readiness requires quality, completed dependencies, and valid state.
CREATE OR REPLACE VIEW sprint_readiness AS
SELECT
    s.story_key,
    s.title,
    s.workflow_state,
    q.criterion_count,
    q.invest_passes,
    NOT EXISTS (
        SELECT 1
        FROM story_dependencies d
        JOIN user_stories dependency
          ON dependency.story_id = d.depends_on_story_id
        WHERE d.story_id = s.story_id
          AND dependency.workflow_state <> 'done'
    ) AS dependencies_complete,
    (
        s.workflow_state = 'ready'
        AND q.refinement_quality_passes
        AND NOT EXISTS (
            SELECT 1
            FROM story_dependencies d
            JOIN user_stories dependency
              ON dependency.story_id = d.depends_on_story_id
            WHERE d.story_id = s.story_id
              AND dependency.workflow_state <> 'done'
        )
    ) AS sprint_eligible
FROM user_stories s
JOIN story_quality q ON q.story_key = s.story_key;

INSERT INTO personas
    (name, role_name, usage_context, primary_goal, constraints_text)
VALUES
    (
        'Ananya', 'bank customer', 'mobile banking application',
        'transfer money with clear confirmation',
        'May retry after a network timeout'
    ),
    (
        'Dev', 'compliance analyst', 'transaction audit workspace',
        'verify transfer evidence',
        'Must access only authorized records'
    );

INSERT INTO user_stories
    (story_key, title, persona_id, user_need, user_value,
     priority, story_points, workflow_state)
VALUES
    (
        'BANK-201', 'Display eligible funding accounts', 1,
        'view an eligible source account',
        'I can select the correct account before transferring money',
        1, 3, 'done'
    ),
    (
        'BANK-202', 'Submit a money transfer', 1,
        'confirm a transfer after reviewing recipient and amount',
        'I can transfer money and receive a traceable reference',
        1, 5, 'ready'
    ),
    (
        'BANK-203', 'Inspect transfer audit evidence', 2,
        'retrieve an authorized transfer audit record',
        'I can verify the recorded transaction outcome',
        2, 3, 'draft'
    );

INSERT INTO acceptance_criteria
    (story_id, criterion_key, criterion_type,
     given_context, when_action, then_outcome, is_automated)
VALUES
    (
        1, 'ACCOUNT-VALID', 'functional',
        'the customer has authenticated',
        'the customer selects an eligible account',
        'the balance and currency are displayed',
        TRUE
    ),
    (
        2, 'TRANSFER-SUCCESS', 'functional',
        'the customer has selected an eligible account',
        'the customer submits a valid transfer',
        'one transfer is recorded and a reference is displayed',
        TRUE
    ),
    (
        2, 'TRANSFER-RETRY', 'error_handling',
        'the original transfer succeeded but the response was lost',
        'the customer retries with the same idempotency key',
        'the original transfer is returned without a second debit',
        TRUE
    ),
    (
        3, 'AUDIT-AUTHORIZATION', 'security',
        'a transfer has completed',
        'an authorized analyst requests its audit record',
        'the reference timestamp and outcome are displayed',
        FALSE
    );

INSERT INTO invest_assessments
    (story_id, independent, negotiable, valuable,
     estimable, small, testable, assessed_by, assessment_notes)
VALUES
    (1, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,
     'product-owner', 'A focused account-selection outcome.'),
    (2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,
     'product-owner', 'Retry semantics are observable and testable.'),
    (3, TRUE, TRUE, TRUE, TRUE, FALSE, TRUE,
     'product-owner', 'Split audit search and export if both are in scope.');

INSERT INTO story_dependencies
    (story_id, depends_on_story_id, dependency_reason)
VALUES
    (2, 1, 'A transfer requires an eligible funding account.'),
    (3, 2, 'Audit evidence must refer to a recorded transfer.');

INSERT INTO refinement_reviews
    (story_id, reviewer_name, decision, findings)
VALUES
    (1, 'product-owner', 'accept', 'Acceptance criteria are observable.'),
    (2, 'engineering-lead', 'accept', 'Retry behavior is explicitly defined.'),
    (3, 'product-owner', 'request_changes',
     'The story is too large for the current delivery window.');

INSERT INTO acceptance_results
    (criterion_id, execution_reference, result_state, observed_outcome)
VALUES
    (1, 'TEST-ACCOUNT-014', 'passed',
     'Eligible account details were displayed.'),
    (2, 'TEST-TRANSFER-041', 'passed',
     'Exactly one transfer was recorded.'),
    (3, 'TEST-TRANSFER-042', 'not_run',
     'Retry scenario awaits execution.');

-- Backlog analysis: distinguish high priority from actual readiness.
SELECT
    story_key,
    title,
    workflow_state,
    priority,
    story_points,
    criterion_count,
    invest_passes,
    refinement_quality_passes
FROM story_quality
ORDER BY priority, story_key;

-- Identify acceptance criteria that have not passed their latest execution.
SELECT
    s.story_key,
    c.criterion_key,
    latest.result_state,
    latest.execution_reference
FROM acceptance_criteria c
JOIN user_stories s ON s.story_id = c.story_id
LEFT JOIN LATERAL (
    SELECT ar.result_state, ar.execution_reference
    FROM acceptance_results ar
    WHERE ar.criterion_id = c.criterion_id
    ORDER BY ar.executed_at DESC, ar.result_id DESC
    LIMIT 1
) latest ON TRUE
WHERE latest.result_state IS DISTINCT FROM 'passed'
ORDER BY s.story_key, c.criterion_key;

-- A story is not sprint eligible merely because it has high priority.
SELECT *
FROM sprint_readiness
ORDER BY sprint_eligible DESC, story_key;

-- Recursive traversal identifies dependency chains and prevents the
-- reporting query from silently ignoring dependency relationships.
WITH RECURSIVE dependency_chain AS (
    SELECT
        d.story_id AS root_story_id,
        d.depends_on_story_id AS dependency_id,
        1 AS depth,
        ARRAY[d.story_id, d.depends_on_story_id] AS path
    FROM story_dependencies d

    UNION ALL

    SELECT
        chain.root_story_id,
        d.depends_on_story_id,
        chain.depth + 1,
        chain.path || d.depends_on_story_id
    FROM dependency_chain chain
    JOIN story_dependencies d
      ON d.story_id = chain.dependency_id
    WHERE NOT d.depends_on_story_id = ANY(chain.path)
      AND chain.depth < 100
)
SELECT
    root.story_key AS dependent_story,
    dependency.story_key AS required_story,
    chain.depth
FROM dependency_chain chain
JOIN user_stories root ON root.story_id = chain.root_story_id
JOIN user_stories dependency ON dependency.story_id = chain.dependency_id
ORDER BY root.story_key, chain.depth;

-- Demonstrate a rejected state transition without aborting the whole script.
DO $$
BEGIN
    BEGIN
        UPDATE user_stories
        SET workflow_state = 'done'
        WHERE story_key = 'BANK-203';

        RAISE EXCEPTION
            'Expected transition validation to reject draft -> done.';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE 'Invalid story transition:%' THEN
                RAISE;
            END IF;
            RAISE NOTICE 'Expected invalid transition was rejected: %',
                SQLERRM;
    END;
END;
$$;

COMMIT;
