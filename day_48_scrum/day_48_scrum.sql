-- PostgreSQL 15+
-- Scrum relational model: Product Backlog, Sprint Backlog, Increment,
-- accountabilities, events, impediments, and retrospective actions.

BEGIN;

DROP SCHEMA IF EXISTS scrum_demo CASCADE;
CREATE SCHEMA scrum_demo;
SET search_path TO scrum_demo, public;

CREATE TYPE accountability AS ENUM (
    'PRODUCT_OWNER',
    'SCRUM_MASTER',
    'DEVELOPER'
);

CREATE TYPE work_status AS ENUM (
    'TO_DO',
    'IN_PROGRESS',
    'DONE'
);

CREATE TYPE scrum_event_type AS ENUM (
    'SPRINT_PLANNING',
    'DAILY_SCRUM',
    'SPRINT_REVIEW',
    'SPRINT_RETROSPECTIVE'
);

CREATE TABLE product (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(product_name)) > 0)
);

CREATE TABLE team_member (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES product(product_id),
    full_name TEXT NOT NULL,
    accountability accountability NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (product_id, full_name),
    UNIQUE (product_id, member_id),
    CHECK (length(trim(full_name)) > 0)
);

-- A product has one active holder of each single-owner accountability.
-- Developer accountability may be held by multiple team members.
CREATE UNIQUE INDEX one_active_product_owner_per_product
    ON team_member(product_id)
    WHERE accountability = 'PRODUCT_OWNER' AND active;

CREATE UNIQUE INDEX one_active_scrum_master_per_product
    ON team_member(product_id)
    WHERE accountability = 'SCRUM_MASTER' AND active;

CREATE TABLE sprint (
    sprint_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES product(product_id),
    sprint_number INTEGER NOT NULL,
    start_date DATE NOT NULL,
    duration_days INTEGER NOT NULL CHECK (duration_days BETWEEN 1 AND 30),
    sprint_goal TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PLANNING'
        CHECK (status IN ('PLANNING', 'ACTIVE', 'CLOSED')),
    review_completed BOOLEAN NOT NULL DEFAULT FALSE,
    retrospective_completed BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (product_id, sprint_number),
    UNIQUE (product_id, sprint_id),
    CHECK (length(trim(sprint_goal)) > 0)
);

CREATE TABLE product_backlog_item (
    item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES product(product_id),
    item_key TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority INTEGER NOT NULL CHECK (priority > 0),
    estimate_points INTEGER NOT NULL CHECK (estimate_points >= 0),
    status work_status NOT NULL DEFAULT 'TO_DO',
    UNIQUE (product_id, item_key),
    UNIQUE (product_id, item_id),
    CHECK (length(trim(item_key)) > 0),
    CHECK (length(trim(title)) > 0)
);

CREATE TABLE acceptance_criterion (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL
        REFERENCES product_backlog_item(item_id) ON DELETE CASCADE,
    criterion_text TEXT NOT NULL,
    satisfied BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (length(trim(criterion_text)) > 0)
);

CREATE TABLE sprint_backlog_item (
    sprint_id BIGINT NOT NULL REFERENCES sprint(sprint_id) ON DELETE CASCADE,
    item_id BIGINT NOT NULL REFERENCES product_backlog_item(item_id),
    selected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (sprint_id, item_id)
);

CREATE TABLE increment_item (
    sprint_id BIGINT NOT NULL,
    item_id BIGINT NOT NULL,
    accepted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    acceptance_notes TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (sprint_id, item_id),
    FOREIGN KEY (sprint_id, item_id)
        REFERENCES sprint_backlog_item(sprint_id, item_id)
        ON DELETE RESTRICT
);

CREATE TABLE scrum_event (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES sprint(sprint_id) ON DELETE CASCADE,
    event_type scrum_event_type NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    description TEXT NOT NULL,
    CHECK (length(trim(description)) > 0)
);

CREATE TABLE impediment (
    impediment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES sprint(sprint_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    identified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT NOT NULL DEFAULT '',
    CHECK (length(trim(description)) > 0),
    CHECK (resolved_at IS NULL OR resolved_at >= identified_at)
);

CREATE TABLE retrospective_action (
    action_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES sprint(sprint_id) ON DELETE CASCADE,
    action_text TEXT NOT NULL,
    owner_member_id BIGINT REFERENCES team_member(member_id),
    due_date DATE,
    completed_at TIMESTAMPTZ,
    CHECK (length(trim(action_text)) > 0)
);

CREATE INDEX backlog_priority_lookup
    ON product_backlog_item(product_id, priority, item_key);

CREATE INDEX sprint_event_timeline
    ON scrum_event(sprint_id, occurred_at);

CREATE INDEX unresolved_impediments
    ON impediment(sprint_id, identified_at)
    WHERE resolved_at IS NULL;

CREATE INDEX open_retrospective_actions
    ON retrospective_action(sprint_id, due_date)
    WHERE completed_at IS NULL;

-- Validate cross-product relationships that ordinary foreign keys do not cover.
CREATE FUNCTION validate_sprint_item_product()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    sprint_product BIGINT;
    item_product BIGINT;
BEGIN
    SELECT product_id INTO sprint_product
    FROM sprint WHERE sprint_id = NEW.sprint_id;

    SELECT product_id INTO item_product
    FROM product_backlog_item WHERE item_id = NEW.item_id;

    IF sprint_product IS DISTINCT FROM item_product THEN
        RAISE EXCEPTION
            'Sprint and backlog item must belong to the same product';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER enforce_sprint_item_product
BEFORE INSERT OR UPDATE ON sprint_backlog_item
FOR EACH ROW EXECUTE FUNCTION validate_sprint_item_product();

-- A simulated Increment may contain only completed work with satisfied criteria.
CREATE FUNCTION validate_increment_item()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    item_state work_status;
    criteria_count BIGINT;
    unsatisfied_count BIGINT;
BEGIN
    SELECT pbi.status INTO item_state
    FROM product_backlog_item pbi
    WHERE pbi.item_id = NEW.item_id;

    IF item_state IS DISTINCT FROM 'DONE' THEN
        RAISE EXCEPTION 'Only completed work can enter the Increment';
    END IF;

    SELECT count(*),
           count(*) FILTER (WHERE NOT satisfied)
    INTO criteria_count, unsatisfied_count
    FROM acceptance_criterion
    WHERE item_id = NEW.item_id;

    IF criteria_count = 0 OR unsatisfied_count > 0 THEN
        RAISE EXCEPTION
            'Increment item requires acceptance criteria and all must be satisfied';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER enforce_increment_acceptance
BEFORE INSERT OR UPDATE ON increment_item
FOR EACH ROW EXECUTE FUNCTION validate_increment_item();

-- A sprint cannot be closed without recording its review and retrospective.
CREATE FUNCTION validate_sprint_closure()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'CLOSED'
       AND (NOT NEW.review_completed OR NOT NEW.retrospective_completed) THEN
        RAISE EXCEPTION
            'Sprint closure requires a completed review and retrospective';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER enforce_sprint_closure
BEFORE UPDATE OF status, review_completed, retrospective_completed
ON sprint
FOR EACH ROW EXECUTE FUNCTION validate_sprint_closure();

-- Demonstration data
INSERT INTO product(product_name)
VALUES ('Digital Banking Reliability');

INSERT INTO team_member(product_id, full_name, accountability)
SELECT product_id, 'Maya', 'PRODUCT_OWNER'
FROM product WHERE product_name = 'Digital Banking Reliability';

INSERT INTO team_member(product_id, full_name, accountability)
SELECT product_id, 'Arjun', 'SCRUM_MASTER'
FROM product WHERE product_name = 'Digital Banking Reliability';

INSERT INTO team_member(product_id, full_name, accountability)
SELECT product_id, person, 'DEVELOPER'
FROM product
CROSS JOIN (VALUES ('Neha'), ('Kabir'), ('Sara')) AS developers(person)
WHERE product_name = 'Digital Banking Reliability';

INSERT INTO sprint(
    product_id, sprint_number, start_date, duration_days, sprint_goal, status
)
SELECT product_id, 1, DATE '2026-10-19', 10,
       'Make payment validation reliable and auditable', 'ACTIVE'
FROM product WHERE product_name = 'Digital Banking Reliability';

INSERT INTO product_backlog_item(
    product_id, item_key, title, description, priority, estimate_points
)
SELECT product_id, data.item_key, data.title, data.description,
       data.priority, data.points
FROM product
CROSS JOIN (
    VALUES
        ('PAY-501', 'Validate payment payload',
         'Reject malformed payment requests.', 1, 5),
        ('PAY-502', 'Persist audit events',
         'Record payment outcomes for investigation.', 2, 8),
        ('PAY-503', 'Expose transaction status',
         'Provide authorized status retrieval.', 3, 3)
) AS data(item_key, title, description, priority, points)
WHERE product_name = 'Digital Banking Reliability';

INSERT INTO acceptance_criterion(item_id, criterion_text)
SELECT item_id, criteria.criterion
FROM product_backlog_item
CROSS JOIN LATERAL (
    VALUES
        ('Malformed payloads are rejected'),
        ('Valid payloads pass validation')
) AS criteria(criterion)
WHERE item_key = 'PAY-501';

INSERT INTO acceptance_criterion(item_id, criterion_text)
SELECT item_id, 'Payment outcome is stored with a correlation identifier'
FROM product_backlog_item
WHERE item_key = 'PAY-502';

INSERT INTO acceptance_criterion(item_id, criterion_text)
SELECT item_id, 'Authorized clients can retrieve transaction status'
FROM product_backlog_item
WHERE item_key = 'PAY-503';

-- Planning query: select work by priority while respecting the available capacity.
WITH RECURSIVE ordered_backlog AS (
    SELECT item_id, item_key, title, priority, estimate_points,
           row_number() OVER (ORDER BY priority, item_key) AS sequence_number
    FROM product_backlog_item
    WHERE product_id = (
        SELECT product_id FROM product
        WHERE product_name = 'Digital Banking Reliability'
    )
      AND status = 'TO_DO'
),
capacity_plan AS (
    SELECT item_id, item_key, title, priority, estimate_points,
           sequence_number, estimate_points AS cumulative_points
    FROM ordered_backlog
    WHERE sequence_number = 1

    UNION ALL

    SELECT next_item.item_id, next_item.item_key, next_item.title,
           next_item.priority, next_item.estimate_points,
           next_item.sequence_number,
           plan.cumulative_points + next_item.estimate_points
    FROM capacity_plan plan
    JOIN ordered_backlog next_item
      ON next_item.sequence_number = plan.sequence_number + 1
    WHERE plan.cumulative_points + next_item.estimate_points <= 16
)
SELECT item_key, title, priority, estimate_points, cumulative_points
FROM capacity_plan
WHERE cumulative_points <= 16
ORDER BY sequence_number;

-- Record two selected items in the Sprint Backlog.
INSERT INTO sprint_backlog_item(sprint_id, item_id)
SELECT s.sprint_id, pbi.item_id
FROM sprint s
JOIN product_backlog_item pbi ON pbi.product_id = s.product_id
WHERE s.sprint_number = 1
  AND pbi.item_key IN ('PAY-501', 'PAY-502');

INSERT INTO scrum_event(sprint_id, event_type, description)
SELECT sprint_id, 'SPRINT_PLANNING',
       'Selected validation and audit work toward the Sprint Goal.'
FROM sprint WHERE sprint_number = 1;

INSERT INTO scrum_event(sprint_id, event_type, description)
SELECT sprint_id, 'DAILY_SCRUM',
       'Inspected progress and identified missing integration test fixtures.'
FROM sprint WHERE sprint_number = 1;

INSERT INTO impediment(sprint_id, description)
SELECT sprint_id, 'Representative payment failure fixtures are not ready.'
FROM sprint WHERE sprint_number = 1;

-- Simulate completed and accepted validation work.
UPDATE product_backlog_item
SET status = 'DONE'
WHERE item_key = 'PAY-501';

UPDATE acceptance_criterion
SET satisfied = TRUE
WHERE item_id = (SELECT item_id FROM product_backlog_item
                 WHERE item_key = 'PAY-501');

INSERT INTO increment_item(sprint_id, item_id, acceptance_notes)
SELECT s.sprint_id, pbi.item_id,
       'Validation criteria satisfied during Increment inspection.'
FROM sprint s
JOIN product_backlog_item pbi ON pbi.product_id = s.product_id
WHERE s.sprint_number = 1 AND pbi.item_key = 'PAY-501';

INSERT INTO scrum_event(sprint_id, event_type, description)
SELECT sprint_id, 'SPRINT_REVIEW',
       'Stakeholders inspected completed validation behavior.'
FROM sprint WHERE sprint_number = 1;

UPDATE sprint
SET review_completed = TRUE
WHERE sprint_number = 1;

INSERT INTO retrospective_action(sprint_id, action_text, due_date)
SELECT sprint_id,
       'Prepare representative failure fixtures before development.',
       DATE '2026-10-26'
FROM sprint WHERE sprint_number = 1;

INSERT INTO retrospective_action(sprint_id, action_text, due_date)
SELECT sprint_id,
       'Clarify audit acceptance criteria during backlog refinement.',
       DATE '2026-10-27'
FROM sprint WHERE sprint_number = 1;

INSERT INTO scrum_event(sprint_id, event_type, description)
SELECT sprint_id, 'SPRINT_RETROSPECTIVE',
       'Agreed on test-fixture preparation and earlier criteria clarification.'
FROM sprint WHERE sprint_number = 1;

UPDATE sprint
SET retrospective_completed = TRUE
WHERE sprint_number = 1;

-- This succeeds because both required closing events have been recorded.
UPDATE sprint
SET status = 'CLOSED'
WHERE sprint_number = 1;

-- Delivery report: distinguish selected work from the accepted Increment.
SELECT
    s.sprint_number,
    s.sprint_goal,
    count(DISTINCT sbi.item_id) AS selected_items,
    COALESCE(sum(pbi.estimate_points), 0) AS selected_points,
    count(DISTINCT ii.item_id) AS increment_items,
    COALESCE(sum(pbi.estimate_points) FILTER (WHERE ii.item_id IS NOT NULL), 0)
        AS accepted_points
FROM sprint s
LEFT JOIN sprint_backlog_item sbi ON sbi.sprint_id = s.sprint_id
LEFT JOIN product_backlog_item pbi ON pbi.item_id = sbi.item_id
LEFT JOIN increment_item ii
    ON ii.sprint_id = sbi.sprint_id AND ii.item_id = sbi.item_id
GROUP BY s.sprint_number, s.sprint_goal;

-- Product Backlog view: remaining work is visible for reordering.
SELECT item_key, title, priority, estimate_points, status
FROM product_backlog_item
ORDER BY priority, item_key;

-- Operational query: unresolved impediments.
SELECT s.sprint_number, i.description, i.identified_at
FROM impediment i
JOIN sprint s ON s.sprint_id = i.sprint_id
WHERE i.resolved_at IS NULL
ORDER BY i.identified_at;

-- Improvement actions remain trackable beyond sprint closure.
SELECT s.sprint_number, a.action_text, a.due_date, a.completed_at
FROM retrospective_action a
JOIN sprint s ON s.sprint_id = a.sprint_id
ORDER BY a.due_date;

COMMIT;
