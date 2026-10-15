-- PostgreSQL 15+
-- Relational product-planning model for epics, features, stories, and tasks.
--
-- The schema distinguishes parent-child decomposition from dependencies.
-- Story points are stored only on stories; hours are stored only on tasks.
-- Aggregate progress is calculated from leaf-level delivery estimates.
-- This script runs in a transaction and recreates its demonstration schema.

BEGIN;

DROP SCHEMA IF EXISTS product_planning CASCADE;
CREATE SCHEMA product_planning;
SET search_path TO product_planning, public;

CREATE TYPE work_type AS ENUM ('epic', 'feature', 'story', 'task');

CREATE TYPE work_status AS ENUM (
    'backlog',
    'ready',
    'in_progress',
    'blocked',
    'done',
    'cancelled'
);

CREATE TYPE work_priority AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TABLE teams (
    team_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE team_members (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(team_id),
    display_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (team_id, member_id)
);

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_key TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE work_items (
    work_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    item_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    item_type work_type NOT NULL,
    parent_id BIGINT REFERENCES work_items(work_item_id),
    status work_status NOT NULL DEFAULT 'backlog',
    priority work_priority NOT NULL DEFAULT 'medium',
    owner_id BIGINT REFERENCES team_members(member_id),
    story_points NUMERIC(7,2),
    estimate_hours NUMERIC(9,2),
    due_date DATE,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_item_key_not_blank CHECK (length(trim(item_key)) > 0),
    CONSTRAINT ck_title_not_blank CHECK (length(trim(title)) > 0),
    CONSTRAINT ck_version_positive CHECK (version > 0),
    CONSTRAINT ck_nonnegative_story_points CHECK (
        story_points IS NULL OR story_points >= 0
    ),
    CONSTRAINT ck_nonnegative_estimate_hours CHECK (
        estimate_hours IS NULL OR estimate_hours >= 0
    ),
    CONSTRAINT ck_story_points_only_on_stories CHECK (
        story_points IS NULL OR item_type = 'story'
    ),
    CONSTRAINT ck_hours_only_on_tasks CHECK (
        estimate_hours IS NULL OR item_type = 'task'
    ),
    CONSTRAINT ck_epic_has_no_parent CHECK (
        item_type <> 'epic' OR parent_id IS NULL
    ),
    CONSTRAINT ck_non_epic_has_parent CHECK (
        item_type = 'epic' OR parent_id IS NOT NULL
    ),
    CONSTRAINT ck_not_own_parent CHECK (
        parent_id IS NULL OR parent_id <> work_item_id
    ),
    CONSTRAINT uq_item_product_id UNIQUE (product_id, work_item_id)
);

CREATE INDEX idx_work_items_parent
    ON work_items(parent_id, item_type, status);

CREATE INDEX idx_work_items_product_status
    ON work_items(product_id, status, priority);

CREATE INDEX idx_work_items_owner
    ON work_items(owner_id, status)
    WHERE owner_id IS NOT NULL;

CREATE TABLE acceptance_criteria (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    story_id BIGINT NOT NULL REFERENCES work_items(work_item_id)
        ON DELETE CASCADE,
    criterion_text TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (story_id, position),
    CHECK (length(trim(criterion_text)) > 0)
);

CREATE TABLE work_dependencies (
    work_item_id BIGINT NOT NULL REFERENCES work_items(work_item_id)
        ON DELETE CASCADE,
    depends_on_id BIGINT NOT NULL REFERENCES work_items(work_item_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (work_item_id, depends_on_id),
    CHECK (work_item_id <> depends_on_id)
);

CREATE INDEX idx_dependencies_target
    ON work_dependencies(depends_on_id);

CREATE TABLE status_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    work_item_id BIGINT NOT NULL REFERENCES work_items(work_item_id),
    previous_status work_status,
    new_status work_status NOT NULL,
    changed_by BIGINT REFERENCES team_members(member_id),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_status_history_item_time
    ON status_history(work_item_id, changed_at DESC);

-- Enforce the exact hierarchy and prevent cross-product parent relationships.
CREATE FUNCTION validate_work_item_hierarchy()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_type work_type;
    parent_product BIGINT;
BEGIN
    IF NEW.item_type = 'epic' THEN
        IF NEW.parent_id IS NOT NULL THEN
            RAISE EXCEPTION 'An epic cannot have a parent';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.parent_id IS NULL THEN
        RAISE EXCEPTION '% requires a parent', NEW.item_type;
    END IF;

    SELECT item_type, product_id
    INTO parent_type, parent_product
    FROM work_items
    WHERE work_item_id = NEW.parent_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Parent work item % does not exist', NEW.parent_id;
    END IF;

    IF parent_product <> NEW.product_id THEN
        RAISE EXCEPTION 'Parent and child must belong to the same product';
    END IF;

    IF (NEW.item_type = 'feature' AND parent_type <> 'epic')
       OR (NEW.item_type = 'story' AND parent_type <> 'feature')
       OR (NEW.item_type = 'task' AND parent_type <> 'story') THEN
        RAISE EXCEPTION 'Invalid hierarchy: % cannot be a child of %',
            NEW.item_type, parent_type;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_work_item_hierarchy
BEFORE INSERT OR UPDATE OF item_type, parent_id, product_id
ON work_items
FOR EACH ROW
EXECUTE FUNCTION validate_work_item_hierarchy();

-- Acceptance criteria must belong to stories, not epics, features, or tasks.
CREATE FUNCTION validate_acceptance_criterion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM work_items
        WHERE work_item_id = NEW.story_id
          AND item_type = 'story'
    ) THEN
        RAISE EXCEPTION 'Acceptance criteria can only belong to stories';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_acceptance_criterion
BEFORE INSERT OR UPDATE ON acceptance_criteria
FOR EACH ROW
EXECUTE FUNCTION validate_acceptance_criterion();

-- Validate dependency targets and reject dependency cycles.
CREATE FUNCTION validate_dependency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_product BIGINT;
    target_product BIGINT;
BEGIN
    SELECT product_id INTO source_product
    FROM work_items
    WHERE work_item_id = NEW.work_item_id;

    SELECT product_id INTO target_product
    FROM work_items
    WHERE work_item_id = NEW.depends_on_id;

    IF source_product IS NULL OR target_product IS NULL THEN
        RAISE EXCEPTION 'Both dependency work items must exist';
    END IF;

    IF source_product <> target_product THEN
        RAISE EXCEPTION 'Dependencies must remain within one product';
    END IF;

    IF EXISTS (
        WITH RECURSIVE dependency_path(item_id) AS (
            SELECT depends_on_id
            FROM work_dependencies
            WHERE work_item_id = NEW.depends_on_id

            UNION

            SELECT dependency.depends_on_id
            FROM work_dependencies dependency
            JOIN dependency_path path
              ON dependency.work_item_id = path.item_id
        )
        SELECT 1
        FROM dependency_path
        WHERE item_id = NEW.work_item_id
    ) THEN
        RAISE EXCEPTION 'Dependency would introduce a cycle';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency
BEFORE INSERT OR UPDATE ON work_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency();

-- State transitions are recorded as part of the same database transaction.
CREATE FUNCTION record_work_item_status_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        IF NOT (
            (OLD.status = 'backlog'
                AND NEW.status IN ('ready', 'cancelled'))
            OR
            (OLD.status = 'ready'
                AND NEW.status IN ('in_progress', 'blocked', 'cancelled'))
            OR
            (OLD.status = 'in_progress'
                AND NEW.status IN ('ready', 'blocked', 'done', 'cancelled'))
            OR
            (OLD.status = 'blocked'
                AND NEW.status IN ('ready', 'in_progress', 'cancelled'))
            OR
            (OLD.status = 'done' AND NEW.status = 'ready')
            OR
            (OLD.status = 'cancelled' AND NEW.status = 'backlog')
        ) THEN
            RAISE EXCEPTION 'Invalid status transition: % -> %',
                OLD.status, NEW.status;
        END IF;

        IF NEW.status = 'in_progress' AND EXISTS (
            SELECT 1
            FROM work_dependencies dependency
            JOIN work_items prerequisite
              ON prerequisite.work_item_id = dependency.depends_on_id
            WHERE dependency.work_item_id = NEW.work_item_id
              AND prerequisite.status <> 'done'
        ) THEN
            RAISE EXCEPTION 'Work cannot start with unfinished dependencies';
        END IF;

        IF NEW.status = 'done' AND NEW.item_type = 'story' AND EXISTS (
            SELECT 1
            FROM work_items task
            WHERE task.parent_id = NEW.work_item_id
              AND task.status NOT IN ('done', 'cancelled')
        ) THEN
            RAISE EXCEPTION 'Story cannot complete with unfinished tasks';
        END IF;

        IF NEW.status = 'done'
           AND NEW.item_type IN ('epic', 'feature')
           AND EXISTS (
               WITH RECURSIVE descendants(item_id, item_type, status) AS (
                   SELECT child.work_item_id, child.item_type, child.status
                   FROM work_items child
                   WHERE child.parent_id = NEW.work_item_id

                   UNION ALL

                   SELECT child.work_item_id, child.item_type, child.status
                   FROM work_items child
                   JOIN descendants parent
                     ON child.parent_id = parent.item_id
               )
               SELECT 1
               FROM descendants
               WHERE item_type IN ('story', 'task')
                 AND status NOT IN ('done', 'cancelled')
           ) THEN
            RAISE EXCEPTION 'Aggregate work has unfinished descendants';
        END IF;

        NEW.version := OLD.version + 1;
        NEW.updated_at := CURRENT_TIMESTAMP;

        INSERT INTO status_history (
            work_item_id, previous_status, new_status
        )
        VALUES (
            OLD.work_item_id, OLD.status, NEW.status
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_record_status_change
BEFORE UPDATE OF status ON work_items
FOR EACH ROW
EXECUTE FUNCTION record_work_item_status_change();

CREATE TABLE planning_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    action TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE FUNCTION audit_work_item_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO planning_audit_log(entity_type, entity_key, action, details)
    VALUES (
        'work_item',
        NEW.item_key,
        CASE WHEN TG_OP = 'INSERT' THEN 'created' ELSE 'updated' END,
        jsonb_build_object(
            'status', NEW.status,
            'priority', NEW.priority,
            'owner_id', NEW.owner_id,
            'version', NEW.version
        )
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_work_item_changes
AFTER INSERT OR UPDATE ON work_items
FOR EACH ROW
EXECUTE FUNCTION audit_work_item_changes();

-- Product planning policy data is distinct from the work hierarchy.
CREATE TABLE delivery_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL UNIQUE REFERENCES products(product_id),
    minimum_story_points NUMERIC(7,2) NOT NULL DEFAULT 0
        CHECK (minimum_story_points >= 0),
    require_story_owners BOOLEAN NOT NULL DEFAULT TRUE,
    require_task_owners BOOLEAN NOT NULL DEFAULT TRUE,
    require_verified_acceptance_criteria BOOLEAN NOT NULL DEFAULT FALSE,
    forbid_blocked_work BOOLEAN NOT NULL DEFAULT TRUE,
    require_estimates BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO teams(team_name) VALUES
    ('Product Management'),
    ('Platform Engineering'),
    ('Quality Engineering'),
    ('Security Engineering');

INSERT INTO team_members(team_id, display_name, email)
SELECT team_id, 'Product Owner', 'product.owner@example.org'
FROM teams WHERE team_name = 'Product Management';

INSERT INTO team_members(team_id, display_name, email)
SELECT team_id, 'Platform Engineer', 'platform.engineer@example.org'
FROM teams WHERE team_name = 'Platform Engineering';

INSERT INTO team_members(team_id, display_name, email)
SELECT team_id, 'Quality Engineer', 'quality.engineer@example.org'
FROM teams WHERE team_name = 'Quality Engineering';

INSERT INTO team_members(team_id, display_name, email)
SELECT team_id, 'Security Engineer', 'security.engineer@example.org'
FROM teams WHERE team_name = 'Security Engineering';

INSERT INTO products(product_key, product_name, description)
VALUES (
    'GOVDATA',
    'Government Data Quality Platform',
    'Configurable data validation and evidence management for public services.'
);

INSERT INTO delivery_policies(
    product_id,
    minimum_story_points,
    require_story_owners,
    require_task_owners,
    require_verified_acceptance_criteria,
    forbid_blocked_work,
    require_estimates
)
SELECT product_id, 13, TRUE, TRUE, TRUE, TRUE, TRUE
FROM products
WHERE product_key = 'GOVDATA';

-- Parent records are inserted before children to satisfy foreign keys.
INSERT INTO work_items(
    product_id, item_key, title, description, item_type,
    parent_id, status, priority, owner_id, due_date
)
SELECT product_id, 'EP-500', 'Data Quality Programme',
       'Deliver governed validation and inspection workflows.',
       'epic', NULL, 'backlog', 'critical', member_id,
       DATE '2026-12-15'
FROM products
CROSS JOIN team_members
WHERE product_key = 'GOVDATA'
  AND email = 'product.owner@example.org';

INSERT INTO work_items(
    product_id, item_key, title, description, item_type,
    parent_id, status, priority, owner_id
)
SELECT p.product_id, 'FE-510', 'Validation Rule Management',
       'Define, version, and execute validation rules.',
       'feature', epic.work_item_id, 'backlog', 'high', member.member_id
FROM products p
JOIN work_items epic ON epic.item_key = 'EP-500'
JOIN team_members member ON member.email = 'platform.engineer@example.org'
WHERE p.product_key = 'GOVDATA';

INSERT INTO work_items(
    product_id, item_key, title, description, item_type,
    parent_id, status, priority, owner_id, story_points
)
SELECT p.product_id, 'ST-511',
       'As a data steward, I can define a required-field rule',
       'Configure required-field checks for incoming datasets.',
       'story', feature.work_item_id, 'backlog', 'high', member.member_id, 5
FROM products p
JOIN work_items feature ON feature.item_key = 'FE-510'
JOIN team_members member ON member.email = 'platform.engineer@example.org'
WHERE p.product_key = 'GOVDATA';

INSERT INTO acceptance_criteria(story_id, criterion_text, position)
SELECT work_item_id, 'A required-field rule detects missing values.', 1
FROM work_items WHERE item_key = 'ST-511';

INSERT INTO acceptance_criteria(story_id, criterion_text, position)
SELECT work_item_id, 'Validation results record failed-row counts.', 2
FROM work_items WHERE item_key = 'ST-511';

INSERT INTO work_items(
    product_id, item_key, title, description, item_type,
    parent_id, status, priority, owner_id, estimate_hours
)
SELECT p.product_id, 'TS-511A', 'Persist validation rule definitions',
       'Store rule configuration and version metadata.',
       'task', story.work_item_id, 'backlog', 'high', member.member_id, 8
FROM products p
JOIN work_items story ON story.item_key = 'ST-511'
JOIN team_members member ON member.email = 'platform.engineer@example.org'
WHERE p.product_key = 'GOVDATA';

INSERT INTO work_items(
    product_id, item_key, title, description, item_type,
    parent_id, status, priority, owner_id, estimate_hours
)
SELECT p.product_id, 'TS-511B', 'Test validation execution',
       'Verify required-field behavior against representative datasets.',
       'task', story.work_item_id, 'backlog', 'medium', member.member_id, 5
FROM products p
JOIN work_items story ON story.item_key = 'ST-511'
JOIN team_members member ON member.email = 'quality.engineer@example.org'
WHERE p.product_key = 'GOVDATA';

INSERT INTO work_dependencies(work_item_id, depends_on_id)
SELECT dependent.work_item_id, prerequisite.work_item_id
FROM work_items dependent
CROSS JOIN work_items prerequisite
WHERE dependent.item_key = 'TS-511B'
  AND prerequisite.item_key = 'TS-511A';

INSERT INTO work_items(
    product_id, item_key, title, description, item_type,
    parent_id, status, priority, owner_id, story_points
)
SELECT p.product_id, 'ST-512',
       'As a steward, I can inspect failed validation records',
       'Inspect failed records without exposing unauthorized data.',
       'story', feature.work_item_id, 'backlog', 'high', member.member_id, 8
FROM products p
JOIN work_items feature ON feature.item_key = 'FE-510'
JOIN team_members member ON member.email = 'platform.engineer@example.org'
WHERE p.product_key = 'GOVDATA';

INSERT INTO acceptance_criteria(story_id, criterion_text, position)
SELECT work_item_id,
       'Each failure identifies the validation rule that was violated.',
       1
FROM work_items WHERE item_key = 'ST-512';

INSERT INTO acceptance_criteria(story_id, criterion_text, position)
SELECT work_item_id,
       'Standard reports mask sensitive field values.',
       2
FROM work_items WHERE item_key = 'ST-512';

-- Recursive view: each work item is associated with its ancestor epic.
CREATE VIEW epic_work_breakdown AS
WITH RECURSIVE hierarchy AS (
    SELECT
        work_item_id,
        item_key,
        title,
        item_type,
        status,
        parent_id,
        work_item_id AS root_id,
        0 AS depth
    FROM work_items
    WHERE item_type = 'epic'

    UNION ALL

    SELECT
        child.work_item_id,
        child.item_key,
        child.title,
        child.item_type,
        child.status,
        child.parent_id,
        hierarchy.root_id,
        hierarchy.depth + 1
    FROM work_items child
    JOIN hierarchy
      ON child.parent_id = hierarchy.work_item_id
)
SELECT
    root.item_key AS epic_key,
    hierarchy.item_key,
    hierarchy.title,
    hierarchy.item_type,
    hierarchy.status,
    hierarchy.parent_id,
    hierarchy.root_id,
    hierarchy.depth
FROM hierarchy
JOIN work_items root ON root.work_item_id = hierarchy.root_id;

-- Calculate progress from story estimates without adding task hours to points.
CREATE VIEW epic_progress AS
WITH story_rollup AS (
    SELECT
        epic.root_id AS epic_id,
        COUNT(*) FILTER (
            WHERE hierarchy.item_type = 'story'
              AND hierarchy.status <> 'cancelled'
        ) AS story_count,
        COUNT(*) FILTER (
            WHERE hierarchy.item_type = 'story'
              AND hierarchy.status = 'done'
        ) AS completed_story_count,
        COUNT(*) FILTER (
            WHERE hierarchy.item_type = 'story'
              AND hierarchy.status <> 'cancelled'
              AND story.story_points IS NULL
        ) AS unestimated_story_count,
        COALESCE(SUM(story.story_points) FILTER (
            WHERE hierarchy.item_type = 'story'
              AND hierarchy.status <> 'cancelled'
        ), 0) AS total_story_points,
        COALESCE(SUM(story.story_points) FILTER (
            WHERE hierarchy.item_type = 'story'
              AND hierarchy.status = 'done'
        ), 0) AS completed_story_points
    FROM epic_work_breakdown hierarchy
    JOIN work_items epic ON epic.work_item_id = hierarchy.root_id
    JOIN work_items story ON story.work_item_id = hierarchy.work_item_id
    GROUP BY epic.root_id
)
SELECT
    epic_id,
    story_count,
    completed_story_count,
    unestimated_story_count,
    total_story_points,
    completed_story_points,
    total_story_points - completed_story_points AS remaining_story_points,
    CASE
        WHEN total_story_points = 0 THEN 0
        ELSE ROUND(
            completed_story_points / total_story_points * 100,
            2
        )
    END AS percent_complete
FROM story_rollup;

-- Policy-oriented report: every row explains a concrete readiness failure.
CREATE VIEW work_item_readiness_issues AS
SELECT
    item.work_item_id,
    item.item_key,
    'missing_owner'::TEXT AS issue_code,
    'Work item has no accountable owner'::TEXT AS issue_detail
FROM work_items item
JOIN delivery_policies policy ON policy.product_id = item.product_id
WHERE item.status <> 'cancelled'
  AND (
      (item.item_type = 'story'
       AND policy.require_story_owners
       AND item.owner_id IS NULL)
      OR
      (item.item_type = 'task'
       AND policy.require_task_owners
       AND item.owner_id IS NULL)
  )

UNION ALL

SELECT
    item.work_item_id,
    item.item_key,
    'missing_estimate',
    'Work item is not estimated'
FROM work_items item
JOIN delivery_policies policy ON policy.product_id = item.product_id
WHERE policy.require_estimates
  AND item.status <> 'cancelled'
  AND (
      (item.item_type = 'story' AND item.story_points IS NULL)
      OR
      (item.item_type = 'task' AND item.estimate_hours IS NULL)
  )

UNION ALL

SELECT
    story.work_item_id,
    story.item_key,
    'unverified_acceptance_criteria',
    'At least one acceptance criterion is not verified'
FROM work_items story
JOIN delivery_policies policy ON policy.product_id = story.product_id
WHERE policy.require_verified_acceptance_criteria
  AND story.item_type = 'story'
  AND story.status <> 'cancelled'
  AND EXISTS (
      SELECT 1
      FROM acceptance_criteria criterion
      WHERE criterion.story_id = story.work_item_id
        AND criterion.verified = FALSE
  )

UNION ALL

SELECT
    item.work_item_id,
    item.item_key,
    'blocked_work',
    'Work item is blocked'
FROM work_items item
JOIN delivery_policies policy ON policy.product_id = item.product_id
WHERE policy.forbid_blocked_work
  AND item.status = 'blocked';

-- A reporting query for the complete hierarchy.
SELECT
    epic_key,
    repeat('  ', depth) || item_key AS indented_key,
    item_type,
    title,
    status
FROM epic_work_breakdown
ORDER BY epic_key, depth, item_key;

-- Epic progress report.
SELECT
    epic.item_key AS epic_key,
    progress.story_count,
    progress.completed_story_count,
    progress.total_story_points,
    progress.completed_story_points,
    progress.remaining_story_points,
    progress.percent_complete,
    progress.unestimated_story_count
FROM epic_progress progress
JOIN work_items epic ON epic.work_item_id = progress.epic_id
ORDER BY epic.item_key;

-- Dependency report exposes prerequisites that have not completed.
SELECT
    dependent.item_key AS dependent_item,
    prerequisite.item_key AS prerequisite_item,
    prerequisite.status AS prerequisite_status
FROM work_dependencies dependency
JOIN work_items dependent
  ON dependent.work_item_id = dependency.work_item_id
JOIN work_items prerequisite
  ON prerequisite.work_item_id = dependency.depends_on_id
WHERE prerequisite.status <> 'done'
ORDER BY dependent.item_key;

-- Acceptance criteria verification coverage.
SELECT
    story.item_key AS story_key,
    COUNT(criterion.criterion_id) AS criterion_count,
    COUNT(criterion.criterion_id) FILTER (
        WHERE criterion.verified
    ) AS verified_count,
    CASE
        WHEN COUNT(criterion.criterion_id) = 0 THEN 0
        ELSE ROUND(
            COUNT(criterion.criterion_id) FILTER (WHERE criterion.verified)
            * 100.0 / COUNT(criterion.criterion_id),
            2
        )
    END AS verification_percent
FROM work_items story
LEFT JOIN acceptance_criteria criterion
  ON criterion.story_id = story.work_item_id
WHERE story.item_type = 'story'
GROUP BY story.work_item_id, story.item_key
ORDER BY story.item_key;

-- Readiness issues are data, not merely a Boolean result.
SELECT *
FROM work_item_readiness_issues
ORDER BY item_key, issue_code;

-- Demonstrate a valid dependency-aware task transition.
-- The first task can start because it has no prerequisite.
UPDATE work_items
SET status = 'ready'
WHERE item_key = 'TS-511A';

UPDATE work_items
SET status = 'in_progress'
WHERE item_key = 'TS-511A';

UPDATE work_items
SET status = 'done'
WHERE item_key = 'TS-511A';

-- The dependent task can now start because its prerequisite is complete.
UPDATE work_items
SET status = 'ready'
WHERE item_key = 'TS-511B';

UPDATE work_items
SET status = 'in_progress'
WHERE item_key = 'TS-511B';

UPDATE work_items
SET status = 'done'
WHERE item_key = 'TS-511B';

-- A story can complete after its tasks are terminal.
UPDATE work_items
SET status = 'ready'
WHERE item_key = 'ST-511';

UPDATE work_items
SET status = 'in_progress'
WHERE item_key = 'ST-511';

UPDATE work_items
SET status = 'done'
WHERE item_key = 'ST-511';

SELECT
    item_key,
    status,
    version,
    updated_at
FROM work_items
WHERE item_key IN ('ST-511', 'TS-511A', 'TS-511B')
ORDER BY item_key;

SELECT
    item.item_key,
    history.previous_status,
    history.new_status,
    history.changed_at,
    history.reason
FROM status_history history
JOIN work_items item ON item.work_item_id = history.work_item_id
ORDER BY history.history_id;

SELECT
    entity_key,
    action,
    details,
    occurred_at
FROM planning_audit_log
ORDER BY audit_id;

-- This transaction makes the demonstration repeatable.
ROLLBACK;
