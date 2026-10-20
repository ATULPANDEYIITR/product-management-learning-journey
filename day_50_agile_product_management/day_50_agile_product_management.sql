DROP SCHEMA IF EXISTS agile_product_management CASCADE;
CREATE SCHEMA agile_product_management;
SET search_path TO agile_product_management;

-- Product goals describe measurable outcomes rather than individual features.
CREATE TABLE product_goals (
    product_goal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    goal_key TEXT NOT NULL UNIQUE,
    statement TEXT NOT NULL,
    outcome_metric TEXT NOT NULL,
    target_value NUMERIC(8,4) NOT NULL CHECK (target_value >= 0),
    target_date DATE NOT NULL
);

-- Roadmap entries communicate directional outcomes and timing.
-- They deliberately do not represent a fixed list of promised features.
CREATE TABLE roadmap_outcomes (
    roadmap_outcome_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    outcome_key TEXT NOT NULL UNIQUE,
    statement TEXT NOT NULL,
    target_date DATE NOT NULL,
    product_goal_id BIGINT NOT NULL
        REFERENCES product_goals(product_goal_id)
        ON DELETE RESTRICT
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    product_goal_id BIGINT REFERENCES product_goals(product_goal_id)
);

CREATE TABLE backlog_items (
    backlog_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    customer_problem TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (
        priority IN ('critical', 'high', 'medium', 'low')
    ),
    value_score INTEGER NOT NULL CHECK (value_score BETWEEN 1 AND 100),
    effort_points INTEGER NOT NULL CHECK (effort_points BETWEEN 1 AND 100),
    status TEXT NOT NULL DEFAULT 'discovery' CHECK (
        status IN ('discovery', 'ready', 'in_progress', 'done')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE backlog_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    backlog_item_id BIGINT NOT NULL
        REFERENCES backlog_items(backlog_item_id)
        ON DELETE CASCADE,
    evidence_type TEXT NOT NULL CHECK (
        evidence_type IN (
            'interview',
            'analytics',
            'support_ticket',
            'experiment',
            'prototype',
            'market_research'
        )
    ),
    observation TEXT NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sprints (
    sprint_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_key TEXT NOT NULL UNIQUE,
    sprint_goal TEXT NOT NULL,
    product_goal_id BIGINT NOT NULL
        REFERENCES product_goals(product_goal_id)
        ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    capacity_points INTEGER NOT NULL CHECK (capacity_points > 0),
    CHECK (start_date <= end_date)
);

CREATE TABLE sprint_backlog (
    sprint_id BIGINT NOT NULL
        REFERENCES sprints(sprint_id)
        ON DELETE CASCADE,
    backlog_item_id BIGINT NOT NULL
        REFERENCES backlog_items(backlog_item_id)
        ON DELETE RESTRICT,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sprint_id, backlog_item_id)
);

-- Continuous discovery stores hypotheses and evidence separately from delivery.
CREATE TABLE discovery_experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_key TEXT NOT NULL UNIQUE,
    hypothesis TEXT NOT NULL,
    method TEXT NOT NULL,
    success_threshold NUMERIC(6,4) NOT NULL
        CHECK (success_threshold BETWEEN 0 AND 1),
    status TEXT NOT NULL DEFAULT 'running' CHECK (
        status IN ('planned', 'running', 'validated', 'invalidated')
    )
);

CREATE TABLE experiment_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES discovery_experiments(experiment_id)
        ON DELETE CASCADE,
    observed_rate NUMERIC(6,4) NOT NULL
        CHECK (observed_rate BETWEEN 0 AND 1),
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    decision_key TEXT NOT NULL UNIQUE,
    backlog_item_id BIGINT NOT NULL
        REFERENCES backlog_items(backlog_item_id)
        ON DELETE RESTRICT,
    decision TEXT NOT NULL CHECK (
        decision IN ('continue', 'defer', 'discard', 'experiment')
    ),
    rationale TEXT NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- The score is useful for ranking but does not replace product judgment.
CREATE INDEX idx_backlog_priority_status
    ON backlog_items(priority, status);

CREATE INDEX idx_sprint_backlog_item
    ON sprint_backlog(backlog_item_id);

CREATE INDEX idx_experiment_observations_experiment
    ON experiment_observations(experiment_id);

CREATE OR REPLACE FUNCTION priority_weight(p_priority TEXT)
RETURNS INTEGER
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE p_priority
        WHEN 'critical' THEN 4
        WHEN 'high' THEN 3
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 1
    END;
$$;

CREATE OR REPLACE FUNCTION backlog_priority_score(
    p_value INTEGER,
    p_effort INTEGER,
    p_priority TEXT
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT ROUND(
        (p_value::NUMERIC * priority_weight(p_priority))
        / NULLIF(p_effort, 0),
        2
    );
$$;

-- A backlog item needs discovery evidence before becoming delivery-ready.
CREATE OR REPLACE FUNCTION validate_backlog_readiness()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IN ('ready', 'in_progress', 'done')
       AND NOT EXISTS (
           SELECT 1
           FROM backlog_evidence
           WHERE backlog_item_id = NEW.backlog_item_id
       )
    THEN
        RAISE EXCEPTION
            'Backlog item % cannot enter delivery state without evidence',
            NEW.item_key;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_backlog_readiness
BEFORE INSERT OR UPDATE OF status
ON backlog_items
FOR EACH ROW
EXECUTE FUNCTION validate_backlog_readiness();

-- A completed item cannot be silently returned to discovery.
CREATE OR REPLACE FUNCTION enforce_delivery_state_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = 'done' AND NEW.status <> 'done' THEN
        RAISE EXCEPTION
            'Completed backlog item % cannot move backwards',
            OLD.item_key;
    END IF;

    IF OLD.status = 'discovery'
       AND NEW.status = 'done'
    THEN
        RAISE EXCEPTION
            'Discovery item % must pass through delivery states',
            OLD.item_key;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_delivery_state_transition
BEFORE UPDATE OF status
ON backlog_items
FOR EACH ROW
EXECUTE FUNCTION enforce_delivery_state_transition();

CREATE OR REPLACE VIEW backlog_prioritization AS
SELECT
    b.backlog_item_id,
    b.item_key,
    b.title,
    b.status,
    b.priority,
    b.value_score,
    b.effort_points,
    backlog_priority_score(
        b.value_score,
        b.effort_points,
        b.priority
    ) AS priority_score
FROM backlog_items b;

CREATE OR REPLACE VIEW discovery_results AS
SELECT
    e.experiment_id,
    e.experiment_key,
    e.hypothesis,
    e.success_threshold,
    COUNT(o.observation_id) AS observations,
    AVG(o.observed_rate) AS average_observed_rate,
    CASE
        WHEN AVG(o.observed_rate) >= e.success_threshold
        THEN TRUE
        ELSE FALSE
    END AS hypothesis_supported
FROM discovery_experiments e
LEFT JOIN experiment_observations o
    ON o.experiment_id = e.experiment_id
GROUP BY
    e.experiment_id,
    e.experiment_key,
    e.hypothesis,
    e.success_threshold;

CREATE OR REPLACE FUNCTION sprint_consumed_capacity(
    p_sprint_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(SUM(b.effort_points), 0)
    FROM sprint_backlog sb
    JOIN backlog_items b
      ON b.backlog_item_id = sb.backlog_item_id
    WHERE sb.sprint_id = p_sprint_id;
$$;

CREATE OR REPLACE FUNCTION sprint_is_outcome_aligned(
    p_sprint_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT
        EXISTS (
            SELECT 1
            FROM sprints s
            WHERE s.sprint_id = p_sprint_id
        )
        AND NOT EXISTS (
            SELECT 1
            FROM sprint_backlog sb
            JOIN backlog_items b
              ON b.backlog_item_id = sb.backlog_item_id
            WHERE sb.sprint_id = p_sprint_id
              AND b.status <> 'done'
        );
$$;

INSERT INTO product_goals (
    goal_key,
    statement,
    outcome_metric,
    target_value,
    target_date
)
VALUES (
    'PG-01',
    'Increase successful first-week activation.',
    'activation_rate',
    0.65,
    DATE '2027-01-18'
);

INSERT INTO roadmap_outcomes (
    outcome_key,
    statement,
    target_date,
    product_goal_id
)
SELECT
    'RO-01',
    'Reduce onboarding friction before first value.',
    DATE '2026-12-04',
    product_goal_id
FROM product_goals
WHERE goal_key = 'PG-01';

INSERT INTO repositories (repository_name, product_goal_id)
SELECT 'customer-platform', product_goal_id
FROM product_goals
WHERE goal_key = 'PG-01';

INSERT INTO backlog_items (
    item_key,
    title,
    customer_problem,
    priority,
    value_score,
    effort_points,
    status
)
VALUES
(
    'PB-101',
    'Simplify first-run setup',
    'Users abandon setup before reaching first value.',
    'critical',
    90,
    8,
    'discovery'
),
(
    'PB-102',
    'Add contextual onboarding checklist',
    'Users cannot identify their next useful action.',
    'high',
    82,
    5,
    'discovery'
),
(
    'PB-103',
    'Improve recurring report navigation',
    'Users spend too long locating recurring reports.',
    'medium',
    65,
    13,
    'discovery'
);

INSERT INTO backlog_evidence (
    backlog_item_id,
    evidence_type,
    observation
)
SELECT
    backlog_item_id,
    'analytics',
    'Funnel analysis shows significant abandonment during setup.'
FROM backlog_items
WHERE item_key = 'PB-101';

INSERT INTO backlog_evidence (
    backlog_item_id,
    evidence_type,
    observation
)
SELECT
    backlog_item_id,
    'interview',
    'Customers report uncertainty about the next useful action.'
FROM backlog_items
WHERE item_key = 'PB-102';

INSERT INTO backlog_evidence (
    backlog_item_id,
    evidence_type,
    observation
)
SELECT
    backlog_item_id,
    'analytics',
    'Navigation telemetry shows repeated searches for reports.'
FROM backlog_items
WHERE item_key = 'PB-103';

-- Discovery converts evidence into a decision before delivery commitment.
INSERT INTO discovery_experiments (
    experiment_key,
    hypothesis,
    method,
    success_threshold
)
VALUES (
    'EXP-01',
    'Guided setup improves first-value completion.',
    'Prototype usability test',
    0.70
);

INSERT INTO experiment_observations (
    experiment_id,
    observed_rate
)
SELECT experiment_id, value
FROM discovery_experiments
CROSS JOIN LATERAL (
    VALUES
        (0.72::NUMERIC),
        (0.76::NUMERIC),
        (0.68::NUMERIC),
        (0.74::NUMERIC)
) AS observations(value)
WHERE experiment_key = 'EXP-01';

UPDATE discovery_experiments
SET status = CASE
    WHEN (
        SELECT AVG(observed_rate)
        FROM experiment_observations o
        WHERE o.experiment_id = discovery_experiments.experiment_id
    ) >= success_threshold
    THEN 'validated'
    ELSE 'invalidated'
END
WHERE experiment_key = 'EXP-01';

-- Discovery-backed items can now become delivery-ready.
UPDATE backlog_items
SET status = 'ready'
WHERE item_key IN ('PB-101', 'PB-102')
  AND EXISTS (
      SELECT 1
      FROM backlog_evidence e
      WHERE e.backlog_item_id = backlog_items.backlog_item_id
  );

INSERT INTO product_decisions (
    decision_key,
    backlog_item_id,
    decision,
    rationale
)
SELECT
    'DEC-101',
    backlog_item_id,
    'continue',
    'Strong customer evidence and validated discovery support continued investment.'
FROM backlog_items
WHERE item_key = 'PB-101';

INSERT INTO sprints (
    sprint_key,
    sprint_goal,
    product_goal_id,
    start_date,
    end_date,
    capacity_points
)
SELECT
    'SPR-01',
    'Improve the path from account creation to first value.',
    product_goal_id,
    DATE '2026-10-20',
    DATE '2026-11-02',
    13
FROM product_goals
WHERE goal_key = 'PG-01';

-- Transactionally select work within the sprint capacity.
BEGIN;

INSERT INTO sprint_backlog (sprint_id, backlog_item_id)
SELECT
    s.sprint_id,
    b.backlog_item_id
FROM sprints s
JOIN backlog_items b
  ON b.item_key IN ('PB-101', 'PB-102')
WHERE s.sprint_key = 'SPR-01'
  AND (
      SELECT COALESCE(SUM(candidate.effort_points), 0)
      FROM backlog_items candidate
      WHERE candidate.item_key IN ('PB-101', 'PB-102')
  ) <= s.capacity_points;

UPDATE backlog_items
SET status = 'in_progress'
WHERE item_key IN ('PB-101', 'PB-102');

COMMIT;

-- Retrieval: ranking is useful for decision support, not automatic product strategy.
SELECT *
FROM backlog_prioritization
ORDER BY priority_score DESC, effort_points ASC;

-- Discovery validation and outcome reporting.
SELECT *
FROM discovery_results;

-- Sprint capacity and remaining capacity.
SELECT
    s.sprint_key,
    s.capacity_points,
    sprint_consumed_capacity(s.sprint_id) AS consumed_points,
    s.capacity_points - sprint_consumed_capacity(s.sprint_id)
        AS remaining_points
FROM sprints s;

-- A failed validation attempt demonstrates database-enforced integrity.
DO $$
BEGIN
    BEGIN
        UPDATE backlog_items
        SET status = 'done'
        WHERE item_key = 'PB-103';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected validation failure for PB-103: %',
                SQLERRM;
    END;
END;
$$;

-- Delivery completion after the sprint work is actually finished.
UPDATE backlog_items
SET status = 'done'
WHERE item_key IN ('PB-101', 'PB-102');

SELECT
    s.sprint_key,
    s.sprint_goal,
    sprint_is_outcome_aligned(s.sprint_id) AS outcome_aligned
FROM sprints s;
