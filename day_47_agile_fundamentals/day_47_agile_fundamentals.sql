-- Agile Fundamentals: relational model for iterative product delivery.
-- Dialect: PostgreSQL 14 or later.
--
-- The schema separates product backlog management, iteration commitments,
-- incremental acceptance, release evidence, and retrospective improvement.
-- It is designed as a repeatable educational script for a dedicated database.

BEGIN;

DROP SCHEMA IF EXISTS agile_fundamentals CASCADE;
CREATE SCHEMA agile_fundamentals;
SET search_path TO agile_fundamentals, public;

CREATE TYPE work_category AS ENUM (
    'customer_feature',
    'defect',
    'technical_enabler',
    'research'
);

CREATE TYPE work_status AS ENUM (
    'backlog',
    'ready',
    'in_progress',
    'in_review',
    'testing',
    'accepted',
    'released',
    'blocked'
);

CREATE TYPE iteration_status AS ENUM (
    'planning',
    'active',
    'completed',
    'cancelled'
);

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    product_goal TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT products_key_nonempty CHECK (btrim(product_key) <> ''),
    CONSTRAINT products_name_nonempty CHECK (btrim(name) <> '')
);

CREATE TABLE team_members (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    display_name TEXT NOT NULL,
    available_days NUMERIC(5,2) NOT NULL,
    focus_factor NUMERIC(4,3) NOT NULL DEFAULT 0.8,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT member_days_nonnegative CHECK (available_days >= 0),
    CONSTRAINT member_focus_valid CHECK (
        focus_factor > 0 AND focus_factor <= 1
    ),
    CONSTRAINT member_name_nonempty CHECK (btrim(display_name) <> ''),
    CONSTRAINT member_product_name_unique UNIQUE (product_id, display_name)
);

CREATE TABLE backlog_items (
    item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    item_key TEXT NOT NULL,
    title TEXT NOT NULL,
    user_outcome TEXT NOT NULL,
    category work_category NOT NULL,
    status work_status NOT NULL DEFAULT 'backlog',
    story_points INTEGER NOT NULL,
    business_value INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT item_key_product_unique UNIQUE (product_id, item_key),
    CONSTRAINT item_key_nonempty CHECK (btrim(item_key) <> ''),
    CONSTRAINT item_title_nonempty CHECK (btrim(title) <> ''),
    CONSTRAINT item_outcome_nonempty CHECK (btrim(user_outcome) <> ''),
    CONSTRAINT item_points_positive CHECK (story_points > 0),
    CONSTRAINT item_value_nonnegative CHECK (business_value >= 0),
    CONSTRAINT item_completion_consistency CHECK (
        (status IN ('accepted', 'released') AND completed_at IS NOT NULL)
        OR
        (status NOT IN ('accepted', 'released') AND completed_at IS NULL)
    )
);

CREATE TABLE acceptance_criteria (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id)
        ON DELETE CASCADE,
    description TEXT NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by BIGINT REFERENCES team_members(member_id),
    verified_at TIMESTAMPTZ,
    CONSTRAINT criterion_description_nonempty CHECK (
        btrim(description) <> ''
    ),
    CONSTRAINT criterion_verification_consistent CHECK (
        (verified = FALSE AND verified_by IS NULL AND verified_at IS NULL)
        OR
        (verified = TRUE AND verified_at IS NOT NULL)
    ),
    CONSTRAINT criterion_description_unique UNIQUE (item_id, description)
);

CREATE TABLE work_dependencies (
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id)
        ON DELETE CASCADE,
    depends_on_item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (item_id, depends_on_item_id),
    CONSTRAINT dependency_not_self CHECK (item_id <> depends_on_item_id)
);

CREATE TABLE iterations (
    iteration_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    iteration_name TEXT NOT NULL,
    iteration_goal TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status iteration_status NOT NULL DEFAULT 'planning',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT iteration_name_product_unique
        UNIQUE (product_id, iteration_name),
    CONSTRAINT iteration_name_nonempty CHECK (
        btrim(iteration_name) <> ''
    ),
    CONSTRAINT iteration_goal_nonempty CHECK (
        btrim(iteration_goal) <> ''
    ),
    CONSTRAINT iteration_dates_valid CHECK (end_date >= start_date)
);

CREATE TABLE iteration_commitments (
    iteration_id BIGINT NOT NULL REFERENCES iterations(iteration_id),
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    committed_points INTEGER NOT NULL,
    PRIMARY KEY (iteration_id, item_id),
    CONSTRAINT committed_points_positive CHECK (committed_points > 0)
);

CREATE TABLE item_assignments (
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id)
        ON DELETE CASCADE,
    member_id BIGINT NOT NULL REFERENCES team_members(member_id),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (item_id, member_id)
);

CREATE TABLE blocker_events (
    blocker_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    reported_by BIGINT REFERENCES team_members(member_id),
    reason TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    resolution TEXT,
    CONSTRAINT blocker_reason_nonempty CHECK (btrim(reason) <> ''),
    CONSTRAINT blocker_resolution_consistent CHECK (
        (resolved_at IS NULL AND resolution IS NULL)
        OR
        (resolved_at IS NOT NULL AND resolution IS NOT NULL
            AND btrim(resolution) <> '')
    )
);

CREATE TABLE acceptance_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    stakeholder_member_id BIGINT NOT NULL
        REFERENCES team_members(member_id),
    accepted BOOLEAN NOT NULL,
    decision_note TEXT NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT decision_note_nonempty CHECK (
        btrim(decision_note) <> ''
    )
);

CREATE TABLE releases (
    release_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    release_name TEXT NOT NULL,
    released_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    release_notes TEXT NOT NULL,
    CONSTRAINT release_name_product_unique
        UNIQUE (product_id, release_name),
    CONSTRAINT release_name_nonempty CHECK (btrim(release_name) <> '')
);

CREATE TABLE release_items (
    release_id BIGINT NOT NULL REFERENCES releases(release_id),
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    PRIMARY KEY (release_id, item_id)
);

CREATE TABLE retrospective_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    iteration_id BIGINT NOT NULL REFERENCES iterations(iteration_id),
    category TEXT NOT NULL,
    evidence TEXT NOT NULL,
    impact TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT observation_fields_nonempty CHECK (
        btrim(category) <> '' AND
        btrim(evidence) <> '' AND
        btrim(impact) <> ''
    )
);

CREATE TABLE improvement_actions (
    action_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    observation_id BIGINT NOT NULL
        REFERENCES retrospective_observations(observation_id),
    description TEXT NOT NULL,
    owner_member_id BIGINT NOT NULL REFERENCES team_members(member_id),
    success_measure TEXT NOT NULL,
    target_iteration_id BIGINT REFERENCES iterations(iteration_id),
    completed_at TIMESTAMPTZ,
    completion_evidence TEXT,
    CONSTRAINT action_description_nonempty CHECK (
        btrim(description) <> ''
    ),
    CONSTRAINT action_measure_nonempty CHECK (
        btrim(success_measure) <> ''
    ),
    CONSTRAINT action_completion_consistent CHECK (
        (completed_at IS NULL AND completion_evidence IS NULL)
        OR
        (completed_at IS NOT NULL AND
            completion_evidence IS NOT NULL AND
            btrim(completion_evidence) <> '')
    )
);

CREATE TABLE work_item_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT REFERENCES backlog_items(item_id),
    iteration_id BIGINT REFERENCES iterations(iteration_id),
    event_type TEXT NOT NULL,
    event_detail TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT event_type_nonempty CHECK (btrim(event_type) <> ''),
    CONSTRAINT event_detail_nonempty CHECK (btrim(event_detail) <> '')
);

CREATE INDEX backlog_priority_idx
    ON backlog_items (product_id, status, business_value DESC);

CREATE INDEX backlog_category_status_idx
    ON backlog_items (product_id, category, status);

CREATE INDEX iteration_schedule_idx
    ON iterations (product_id, start_date, end_date);

CREATE INDEX blocker_open_idx
    ON blocker_events (item_id, reported_at)
    WHERE resolved_at IS NULL;

CREATE INDEX acceptance_decision_history_idx
    ON acceptance_decisions (item_id, decided_at DESC);

CREATE INDEX work_events_timeline_idx
    ON work_item_events (occurred_at DESC);

-- Keep update timestamps accurate when backlog details change.
CREATE FUNCTION update_backlog_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER backlog_timestamp_trigger
BEFORE UPDATE ON backlog_items
FOR EACH ROW
EXECUTE FUNCTION update_backlog_timestamp();

-- Completion requires verified criteria. This is a database safeguard,
-- independent of the application interface used by a delivery team.
CREATE FUNCTION enforce_item_acceptance()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    criterion_count INTEGER;
    unverified_count INTEGER;
    unmet_dependencies INTEGER;
BEGIN
    IF NEW.status IN ('accepted', 'released') THEN
        SELECT count(*),
               count(*) FILTER (WHERE verified = FALSE)
        INTO criterion_count, unverified_count
        FROM acceptance_criteria
        WHERE item_id = NEW.item_id;

        IF criterion_count = 0 OR unverified_count > 0 THEN
            RAISE EXCEPTION
                'Item % cannot be accepted without verified criteria',
                NEW.item_key;
        END IF;

        SELECT count(*)
        INTO unmet_dependencies
        FROM work_dependencies dependency
        JOIN backlog_items prerequisite
          ON prerequisite.item_id = dependency.depends_on_item_id
        WHERE dependency.item_id = NEW.item_id
          AND prerequisite.status <> 'released';

        IF unmet_dependencies > 0 THEN
            RAISE EXCEPTION
                'Item % has dependencies that have not been released',
                NEW.item_key;
        END IF;

        IF NEW.status = 'accepted' AND NEW.completed_at IS NULL THEN
            NEW.completed_at := now();
        ELSIF NEW.status = 'released' AND NEW.completed_at IS NULL THEN
            NEW.completed_at := now();
        END IF;
    ELSE
        NEW.completed_at := NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER item_acceptance_trigger
BEFORE INSERT OR UPDATE OF status ON backlog_items
FOR EACH ROW
EXECUTE FUNCTION enforce_item_acceptance();

-- Avoid dependencies between products and reject direct self-dependencies.
CREATE FUNCTION validate_dependency_product()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    item_product BIGINT;
    prerequisite_product BIGINT;
BEGIN
    SELECT product_id INTO item_product
    FROM backlog_items
    WHERE item_id = NEW.item_id;

    SELECT product_id INTO prerequisite_product
    FROM backlog_items
    WHERE item_id = NEW.depends_on_item_id;

    IF item_product IS DISTINCT FROM prerequisite_product THEN
        RAISE EXCEPTION 'Dependencies must belong to the same product';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER dependency_product_trigger
BEFORE INSERT OR UPDATE ON work_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_product();

-- Seed a realistic citizen-service product and delivery team.
INSERT INTO products (product_key, name, product_goal)
VALUES (
    'CSP',
    'Civic Service Portal',
    'Make citizen service requests secure, traceable, and accessible.'
);

INSERT INTO team_members (
    product_id, display_name, available_days, focus_factor
)
SELECT product_id, member_name, available_days, focus_factor
FROM products
CROSS JOIN (
    VALUES
        ('Maya', 8.0::NUMERIC, 0.80::NUMERIC),
        ('Arjun', 8.0::NUMERIC, 0.75::NUMERIC),
        ('Nisha', 6.0::NUMERIC, 0.80::NUMERIC),
        ('Ravi', 6.0::NUMERIC, 0.75::NUMERIC)
) AS members(member_name, available_days, focus_factor)
WHERE product_key = 'CSP';

INSERT INTO backlog_items (
    product_id, item_key, title, user_outcome, category,
    status, story_points, business_value
)
SELECT product_id, source.item_key, source.title, source.outcome,
       source.category::work_category, 'backlog',
       source.story_points, source.business_value
FROM products
CROSS JOIN (
    VALUES
        (
            'CSP-401',
            'Secure citizen sign-in',
            'Citizens can access their requests securely.',
            'customer_feature',
            5,
            90
        ),
        (
            'CSP-402',
            'Request status display',
            'Citizens can see whether their requests are pending or resolved.',
            'customer_feature',
            3,
            75
        ),
        (
            'CSP-403',
            'Prevent duplicate submissions',
            'Retries do not create duplicate service requests.',
            'defect',
            3,
            95
        ),
        (
            'CSP-404',
            'Request audit trail',
            'Operators can trace status changes to actors and timestamps.',
            'technical_enabler',
            5,
            80
        )
) AS source(item_key, title, outcome, category, story_points, business_value)
WHERE product_key = 'CSP';

INSERT INTO acceptance_criteria (item_id, description)
SELECT item_id, criterion
FROM backlog_items
JOIN (
    VALUES
        ('CSP-401', 'Valid credentials establish a session'),
        ('CSP-401', 'Invalid credentials are rejected'),
        ('CSP-402', 'Current request status is displayed'),
        ('CSP-402', 'Keyboard navigation is supported'),
        ('CSP-403', 'Repeated identifiers do not duplicate requests'),
        ('CSP-403', 'Distinct identifiers create separate requests'),
        ('CSP-404', 'Each status change records an actor'),
        ('CSP-404', 'Each status change records a timestamp')
) AS criteria(item_key, criterion)
USING (item_key);

INSERT INTO work_dependencies (item_id, depends_on_item_id)
SELECT dependent.item_id, prerequisite.item_id
FROM backlog_items dependent
JOIN backlog_items prerequisite
  ON dependent.product_id = prerequisite.product_id
WHERE dependent.item_key = 'CSP-402'
  AND prerequisite.item_key = 'CSP-401';

INSERT INTO iterations (
    product_id, iteration_name, iteration_goal, start_date, end_date
)
SELECT product_id,
       'Iteration A',
       'Deliver secure sign-in and reliable request submissions.',
       DATE '2026-10-19',
       DATE '2026-10-30'
FROM products
WHERE product_key = 'CSP';

-- Refinement is represented as a real status transition.
UPDATE backlog_items
SET status = 'ready'
WHERE item_key IN ('CSP-401', 'CSP-402', 'CSP-403', 'CSP-404');

-- Only independent items are committed. The status view waits for sign-in
-- to be released, making dependency management explicit.
INSERT INTO iteration_commitments (
    iteration_id, item_id, committed_points
)
SELECT iteration.iteration_id, item.item_id, item.story_points
FROM iterations iteration
JOIN products product ON product.product_id = iteration.product_id
JOIN backlog_items item ON item.product_id = product.product_id
WHERE product.product_key = 'CSP'
  AND iteration.iteration_name = 'Iteration A'
  AND item.item_key IN ('CSP-401', 'CSP-403');

INSERT INTO item_assignments (item_id, member_id)
SELECT item.item_id, member.member_id
FROM backlog_items item
JOIN team_members member ON member.product_id = item.product_id
WHERE (item.item_key = 'CSP-401' AND member.display_name = 'Maya')
   OR (item.item_key = 'CSP-403' AND member.display_name = 'Arjun');

UPDATE iterations
SET status = 'active'
WHERE iteration_name = 'Iteration A';

INSERT INTO work_item_events (
    item_id, iteration_id, event_type, event_detail
)
SELECT item.item_id,
       iteration.iteration_id,
       'iteration_started',
       iteration.iteration_goal
FROM backlog_items item
JOIN iteration_commitments commitment
  ON commitment.item_id = item.item_id
JOIN iterations iteration
  ON iteration.iteration_id = commitment.iteration_id
WHERE iteration.iteration_name = 'Iteration A';

-- Begin and verify the sign-in increment.
UPDATE backlog_items
SET status = 'in_progress'
WHERE item_key = 'CSP-401';

UPDATE backlog_items
SET status = 'in_review'
WHERE item_key = 'CSP-401';

UPDATE backlog_items
SET status = 'testing'
WHERE item_key = 'CSP-401';

UPDATE acceptance_criteria
SET verified = TRUE,
    verified_by = (
        SELECT member_id
        FROM team_members
        WHERE display_name = 'Maya'
          AND product_id = (
              SELECT product_id FROM products WHERE product_key = 'CSP'
          )
    ),
    verified_at = now()
WHERE item_id = (
    SELECT item_id FROM backlog_items WHERE item_key = 'CSP-401'
);

INSERT INTO acceptance_decisions (
    item_id, stakeholder_member_id, accepted, decision_note
)
SELECT item.item_id, member.member_id, TRUE,
       'Authentication criteria passed in the iteration test environment.'
FROM backlog_items item
JOIN team_members member
  ON member.product_id = item.product_id
WHERE item.item_key = 'CSP-401'
  AND member.display_name = 'Nisha';

UPDATE backlog_items
SET status = 'accepted'
WHERE item_key = 'CSP-401';

INSERT INTO releases (product_id, release_name, release_notes)
SELECT product_id,
       'csp-2026.10-a',
       'Secure citizen sign-in and retry-safe submission.'
FROM products
WHERE product_key = 'CSP';

INSERT INTO release_items (release_id, item_id)
SELECT release.release_id, item.item_id
FROM releases release
JOIN products product ON product.product_id = release.product_id
JOIN backlog_items item ON item.product_id = product.product_id
WHERE product.product_key = 'CSP'
  AND release.release_name = 'csp-2026.10-a'
  AND item.item_key = 'CSP-401';

UPDATE backlog_items
SET status = 'released'
WHERE item_key = 'CSP-401';

-- Complete the retry-safety increment.
UPDATE backlog_items
SET status = 'in_progress'
WHERE item_key = 'CSP-403';

INSERT INTO blocker_events (item_id, reported_by, reason)
SELECT item.item_id, member.member_id,
       'Integration environment does not preserve retry identifiers.'
FROM backlog_items item
JOIN team_members member ON member.product_id = item.product_id
WHERE item.item_key = 'CSP-403'
  AND member.display_name = 'Arjun';

UPDATE backlog_items
SET status = 'blocked'
WHERE item_key = 'CSP-403';

UPDATE blocker_events
SET resolved_at = now(),
    resolution = 'Test environment restored and repeated requests verified.'
WHERE item_id = (
    SELECT item_id FROM backlog_items WHERE item_key = 'CSP-403'
)
AND resolved_at IS NULL;

UPDATE backlog_items
SET status = 'in_progress'
WHERE item_key = 'CSP-403';

UPDATE backlog_items
SET status = 'in_review'
WHERE item_key = 'CSP-403';

UPDATE backlog_items
SET status = 'testing'
WHERE item_key = 'CSP-403';

UPDATE acceptance_criteria
SET verified = TRUE,
    verified_by = (
        SELECT member_id
        FROM team_members
        WHERE display_name = 'Arjun'
          AND product_id = (
              SELECT product_id FROM products WHERE product_key = 'CSP'
          )
    ),
    verified_at = now()
WHERE item_id = (
    SELECT item_id FROM backlog_items WHERE item_key = 'CSP-403'
);

INSERT INTO acceptance_decisions (
    item_id, stakeholder_member_id, accepted, decision_note
)
SELECT item.item_id, member.member_id, TRUE,
       'Retry and uniqueness scenarios passed.'
FROM backlog_items item
JOIN team_members member ON member.product_id = item.product_id
WHERE item.item_key = 'CSP-403'
  AND member.display_name = 'Nisha';

UPDATE backlog_items
SET status = 'accepted'
WHERE item_key = 'CSP-403';

INSERT INTO release_items (release_id, item_id)
SELECT release.release_id, item.item_id
FROM releases release
JOIN products product ON product.product_id = release.product_id
JOIN backlog_items item ON item.product_id = product.product_id
WHERE product.product_key = 'CSP'
  AND release.release_name = 'csp-2026.10-a'
  AND item.item_key = 'CSP-403';

UPDATE backlog_items
SET status = 'released'
WHERE item_key = 'CSP-403';

-- Backlog prioritization is a discussion aid, not an automatic commitment.
CREATE VIEW prioritized_backlog AS
SELECT
    item.item_key,
    item.title,
    item.category,
    item.status,
    item.story_points,
    item.business_value,
    round(
        item.business_value::NUMERIC /
        NULLIF(item.story_points, 0),
        2
    ) AS value_per_point
FROM backlog_items item
WHERE item.status IN ('backlog', 'ready')
ORDER BY value_per_point DESC, item.business_value DESC;

-- Team capacity is measured in effective working days, not story points.
CREATE VIEW effective_team_capacity AS
SELECT
    product.product_key,
    round(sum(member.available_days * member.focus_factor), 2)
        AS effective_working_days
FROM products product
JOIN team_members member ON member.product_id = product.product_id
WHERE member.active = TRUE
GROUP BY product.product_key;

-- Iteration results report completed increments separately from commitments.
CREATE VIEW iteration_delivery_report AS
SELECT
    iteration.iteration_name,
    iteration.iteration_goal,
    iteration.status AS iteration_status,
    count(commitment.item_id) AS committed_items,
    coalesce(sum(commitment.committed_points), 0) AS committed_points,
    count(commitment.item_id) FILTER (
        WHERE item.status = 'released'
    ) AS released_items,
    coalesce(sum(item.story_points) FILTER (
        WHERE item.status = 'released'
    ), 0) AS released_points,
    array_agg(item.item_key ORDER BY item.item_key) FILTER (
        WHERE item.status <> 'released'
    ) AS unfinished_items
FROM iterations iteration
LEFT JOIN iteration_commitments commitment
    ON commitment.iteration_id = iteration.iteration_id
LEFT JOIN backlog_items item ON item.item_id = commitment.item_id
GROUP BY iteration.iteration_id;

-- Dependencies become eligible only when their prerequisites are released.
CREATE VIEW dependency_readiness AS
SELECT
    item.item_key,
    item.title,
    count(dependency.depends_on_item_id) AS dependency_count,
    count(dependency.depends_on_item_id) FILTER (
        WHERE prerequisite.status = 'released'
    ) AS released_dependencies,
    bool_and(prerequisite.status = 'released') AS dependencies_satisfied
FROM backlog_items item
LEFT JOIN work_dependencies dependency ON dependency.item_id = item.item_id
LEFT JOIN backlog_items prerequisite
    ON prerequisite.item_id = dependency.depends_on_item_id
GROUP BY item.item_id, item.item_key, item.title;

-- Record a concrete retrospective observation and an owned improvement action.
INSERT INTO retrospective_observations (
    iteration_id, category, evidence, impact
)
SELECT iteration_id,
       'Testing',
       'Retry scenarios exposed unstable behavior in the integration environment.',
       'Acceptance was delayed until retry safety was verified.'
FROM iterations
WHERE iteration_name = 'Iteration A';

INSERT INTO improvement_actions (
    observation_id, description, owner_member_id,
    success_measure, target_iteration_id
)
SELECT observation.observation_id,
       'Stabilize the retry integration test environment.',
       member.member_id,
       'Repeated request identifiers pass consistently in the test suite.',
       iteration.iteration_id
FROM retrospective_observations observation
JOIN iterations iteration
  ON iteration.iteration_id = observation.iteration_id
JOIN team_members member
  ON member.product_id = iteration.product_id
WHERE observation.category = 'Testing'
  AND member.display_name = 'Arjun'
  AND iteration.iteration_name = 'Iteration A';

-- Queries that can be run independently after the seed workflow.
SELECT * FROM prioritized_backlog;
SELECT * FROM effective_team_capacity;
SELECT * FROM iteration_delivery_report;
SELECT * FROM dependency_readiness;

SELECT
    item.item_key,
    blocker.reason,
    blocker.reported_at,
    blocker.resolved_at,
    blocker.resolution
FROM blocker_events blocker
JOIN backlog_items item ON item.item_id = blocker.item_id
ORDER BY blocker.reported_at;

SELECT
    item.item_key,
    item.title,
    decision.accepted,
    decision.decision_note,
    decision.decided_at
FROM acceptance_decisions decision
JOIN backlog_items item ON item.item_id = decision.item_id
ORDER BY decision.decided_at DESC;

-- An invalid completion is demonstrated safely in a savepoint. The
-- exception is caught inside PL/pgSQL, so the outer transaction remains valid.
SAVEPOINT invalid_acceptance_demo;

DO $$
DECLARE
    target_item BIGINT;
BEGIN
    SELECT item_id INTO target_item
    FROM backlog_items
    WHERE item_key = 'CSP-402';

    BEGIN
        UPDATE backlog_items
        SET status = 'accepted'
        WHERE item_id = target_item;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected database safeguard: %',
                SQLERRM;
    END;
END;
$$;

RELEASE SAVEPOINT invalid_acceptance_demo;

COMMIT;
