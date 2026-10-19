DROP SCHEMA IF EXISTS kanban_demo CASCADE;
CREATE SCHEMA kanban_demo;
SET search_path = kanban_demo;

-- The relational model separates work definition, current flow state,
-- historical movement, and the policies controlling WIP capacity.

CREATE TYPE work_stage AS ENUM (
    'backlog',
    'ready',
    'development',
    'review',
    'testing',
    'done'
);

CREATE TYPE priority_level AS ENUM (
    'expedite',
    'high',
    'normal',
    'low'
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    team_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE board_columns (
    column_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    stage work_stage NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 0),
    wip_limit INTEGER,
    UNIQUE (repository_id, stage),
    UNIQUE (repository_id, position),
    CHECK (wip_limit IS NULL OR wip_limit > 0)
);

CREATE TABLE work_items (
    work_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    item_key TEXT NOT NULL,
    title TEXT NOT NULL,
    priority priority_level NOT NULL DEFAULT 'normal',
    stage work_stage NOT NULL DEFAULT 'backlog',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    UNIQUE (repository_id, item_key),
    CHECK (completed_at IS NULL OR stage = 'done'),
    CHECK (started_at IS NULL OR started_at >= created_at),
    CHECK (completed_at IS NULL OR started_at IS NOT NULL),
    CHECK (completed_at IS NULL OR completed_at >= started_at)
);

CREATE TABLE work_item_transitions (
    transition_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    work_item_id BIGINT NOT NULL
        REFERENCES work_items(work_item_id)
        ON DELETE CASCADE,
    from_stage work_stage,
    to_stage work_stage NOT NULL,
    transitioned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (from_stage IS DISTINCT FROM to_stage)
);

CREATE TABLE flow_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    average_wip NUMERIC(12,2) NOT NULL CHECK (average_wip >= 0),
    completed_items INTEGER NOT NULL CHECK (completed_items >= 0),
    observation_hours NUMERIC(12,2) NOT NULL
        CHECK (observation_hours > 0)
);

CREATE INDEX idx_work_items_repository_stage
    ON work_items(repository_id, stage);

CREATE INDEX idx_work_items_completed_at
    ON work_items(repository_id, completed_at)
    WHERE completed_at IS NOT NULL;

CREATE INDEX idx_transitions_item_time
    ON work_item_transitions(work_item_id, transitioned_at);

CREATE INDEX idx_flow_observations_repository_time
    ON flow_observations(repository_id, observed_at);

INSERT INTO repositories (repository_name, team_name)
VALUES
    ('payments-platform', 'Payments Engineering'),
    ('customer-portal', 'Web Platform');

INSERT INTO board_columns
    (repository_id, stage, position, wip_limit)
SELECT
    r.repository_id,
    v.stage,
    v.position,
    v.wip_limit
FROM repositories r
CROSS JOIN (
    VALUES
        ('backlog'::work_stage, 0, NULL::INTEGER),
        ('ready'::work_stage, 1, NULL::INTEGER),
        ('development'::work_stage, 2, 3),
        ('review'::work_stage, 3, 2),
        ('testing'::work_stage, 4, 2),
        ('done'::work_stage, 5, NULL::INTEGER)
) AS v(stage, position, wip_limit);

INSERT INTO work_items
    (repository_id, item_key, title, priority, stage,
     created_at, started_at, completed_at)
SELECT
    repository_id,
    item_key,
    title,
    priority,
    stage,
    created_at,
    started_at,
    completed_at
FROM (
    SELECT
        r.repository_id,
        x.item_key,
        x.title,
        x.priority::priority_level,
        x.stage::work_stage,
        x.created_at,
        x.started_at,
        x.completed_at
    FROM repositories r
    JOIN (
        VALUES
        (
            'PAY-101',
            'Payment timeout reduction',
            'high',
            'development',
            now() - interval '36 hours',
            now() - interval '12 hours',
            NULL::timestamptz
        ),
        (
            'PAY-102',
            'Idempotency audit',
            'expedite',
            'review',
            now() - interval '30 hours',
            now() - interval '20 hours',
            NULL::timestamptz
        ),
        (
            'PAY-103',
            'Settlement metrics',
            'normal',
            'testing',
            now() - interval '18 hours',
            now() - interval '10 hours',
            NULL::timestamptz
        ),
        (
            'PAY-104',
            'Webhook retry policy',
            'normal',
            'ready',
            now() - interval '8 hours',
            NULL::timestamptz,
            NULL::timestamptz
        ),
        (
            'PAY-105',
            'Receipt generation',
            'low',
            'done',
            now() - interval '72 hours',
            now() - interval '48 hours',
            now() - interval '24 hours'
        )
    ) AS x(item_key, title, priority, stage,
           created_at, started_at, completed_at)
    ON r.repository_name = 'payments-platform'
) AS seeded;

INSERT INTO work_item_transitions
    (work_item_id, from_stage, to_stage, transitioned_at)
SELECT
    w.work_item_id,
    NULL,
    'ready',
    w.created_at
FROM work_items w
WHERE w.item_key IN ('PAY-101', 'PAY-102', 'PAY-103', 'PAY-104', 'PAY-105');

INSERT INTO work_item_transitions
    (work_item_id, from_stage, to_stage, transitioned_at)
SELECT
    w.work_item_id,
    'ready',
    w.stage,
    COALESCE(w.started_at, w.created_at)
FROM work_items w
WHERE w.item_key IN ('PAY-101', 'PAY-102', 'PAY-103', 'PAY-105')
  AND w.started_at IS NOT NULL;

INSERT INTO flow_observations
    (repository_id, observed_at, average_wip, completed_items, observation_hours)
SELECT
    repository_id,
    now(),
    4.00,
    1,
    24.00
FROM repositories
WHERE repository_name = 'payments-platform';

-- Current WIP by stage exposes where capacity is being consumed.
CREATE VIEW current_wip AS
SELECT
    r.repository_name,
    b.stage,
    COUNT(w.work_item_id) AS current_wip,
    b.wip_limit,
    CASE
        WHEN b.wip_limit IS NULL THEN FALSE
        ELSE COUNT(w.work_item_id) >= b.wip_limit
    END AS at_wip_limit
FROM repositories r
JOIN board_columns b
    ON b.repository_id = r.repository_id
LEFT JOIN work_items w
    ON w.repository_id = r.repository_id
   AND w.stage = b.stage
GROUP BY
    r.repository_name,
    b.stage,
    b.position,
    b.wip_limit
ORDER BY r.repository_name, b.position;

-- Work aging identifies active items that may be creating hidden flow risk.
CREATE VIEW active_work_aging AS
SELECT
    r.repository_name,
    w.item_key,
    w.title,
    w.stage,
    w.priority,
    now() - w.created_at AS age,
    CASE
        WHEN w.started_at IS NULL THEN NULL
        ELSE now() - w.started_at
    END AS active_cycle_age
FROM work_items w
JOIN repositories r
    ON r.repository_id = w.repository_id
WHERE w.stage <> 'done';

-- Throughput is calculated from completion events, not from WIP counts.
CREATE VIEW daily_throughput AS
SELECT
    r.repository_name,
    date_trunc('day', w.completed_at) AS completion_day,
    COUNT(*) AS completed_items
FROM work_items w
JOIN repositories r
    ON r.repository_id = w.repository_id
WHERE w.completed_at IS NOT NULL
GROUP BY
    r.repository_name,
    date_trunc('day', w.completed_at)
ORDER BY completion_day;

-- Cycle time measures active flow from Development to Done.
SELECT
    item_key,
    title,
    EXTRACT(
        EPOCH FROM (completed_at - started_at)
    ) / 3600.0 AS cycle_time_hours
FROM work_items
WHERE started_at IS NOT NULL
  AND completed_at IS NOT NULL
ORDER BY cycle_time_hours;

-- Little's Law provides a flow-level consistency check:
-- average WIP = throughput * average cycle time.
SELECT
    repository_name,
    AVG(average_wip) AS observed_average_wip,
    SUM(completed_items)
        / NULLIF(SUM(observation_hours) / 24.0, 0)
        AS observed_throughput_per_day,
    AVG(average_wip)
        / NULLIF(
            SUM(completed_items)
                / NULLIF(SUM(observation_hours) / 24.0, 0),
            0
        ) AS estimated_cycle_days
FROM flow_observations
GROUP BY repository_name;

-- The transaction demonstrates database-side validation of a pull.
-- It moves work only when Development has capacity.
BEGIN;

WITH capacity AS (
    SELECT
        b.repository_id,
        b.wip_limit,
        COUNT(w.work_item_id) AS current_wip
    FROM board_columns b
    LEFT JOIN work_items w
        ON w.repository_id = b.repository_id
       AND w.stage = 'development'
    WHERE b.repository_id = (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'payments-platform'
    )
      AND b.stage = 'development'
    GROUP BY b.repository_id, b.wip_limit
)
UPDATE work_items w
SET
    stage = 'development',
    started_at = COALESCE(started_at, clock_timestamp())
FROM capacity c
WHERE w.item_key = 'PAY-104'
  AND w.repository_id = c.repository_id
  AND c.current_wip < c.wip_limit
  AND w.stage = 'ready';

COMMIT;

-- This query shows the resulting state after the capacity-aware pull.
SELECT
    r.repository_name,
    w.item_key,
    w.stage,
    w.started_at
FROM work_items w
JOIN repositories r
    ON r.repository_id = w.repository_id
WHERE r.repository_name = 'payments-platform'
ORDER BY w.created_at;

-- PostgreSQL constraints reject invalid completion state:
-- a completed item cannot exist outside the Done stage.
-- The following statement is intentionally not executed because it would
-- violate the CHECK constraint:
--
-- UPDATE work_items
-- SET completed_at = now()
-- WHERE item_key = 'PAY-104'
--   AND stage <> 'done';

-- WIP utilization identifies columns that are close to becoming bottlenecks.
SELECT
    repository_name,
    stage,
    current_wip,
    wip_limit,
    CASE
        WHEN wip_limit IS NULL THEN NULL
        ELSE ROUND(
            current_wip::NUMERIC / wip_limit * 100,
            2
        )
    END AS utilization_percent
FROM current_wip
WHERE wip_limit IS NOT NULL
ORDER BY utilization_percent DESC;
