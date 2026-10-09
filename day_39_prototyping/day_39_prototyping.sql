-- PostgreSQL 15+
-- Relational prototype research model for an enterprise expense workflow.
-- Fidelity identifies what is being tested; it does not imply product readiness.
-- The schema records artifacts, screen structures, research tasks, observations,
-- design iterations, and evidence-based decisions.

BEGIN;

DROP VIEW IF EXISTS fidelity_evaluation CASCADE;
DROP VIEW IF EXISTS task_usability_metrics CASCADE;
DROP TABLE IF EXISTS prototype_decisions CASCADE;
DROP TABLE IF EXISTS usability_observations CASCADE;
DROP TABLE IF EXISTS research_tasks CASCADE;
DROP TABLE IF EXISTS prototype_revisions CASCADE;
DROP TABLE IF EXISTS prototype_elements CASCADE;
DROP TABLE IF EXISTS prototype_screens CASCADE;
DROP TABLE IF EXISTS prototypes CASCADE;
DROP TYPE IF EXISTS prototype_fidelity CASCADE;
DROP TYPE IF EXISTS prototype_lifecycle CASCADE;
DROP TYPE IF EXISTS task_outcome CASCADE;

CREATE TYPE prototype_fidelity AS ENUM ('low', 'medium', 'high');
CREATE TYPE prototype_lifecycle AS ENUM ('draft', 'testable', 'retired');
CREATE TYPE task_outcome AS ENUM ('completed', 'failed', 'abandoned');

CREATE TABLE prototypes (
    prototype_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    artifact_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    fidelity prototype_fidelity NOT NULL,
    lifecycle prototype_lifecycle NOT NULL DEFAULT 'draft',
    research_question TEXT NOT NULL,
    target_user_group TEXT NOT NULL,
    revision_number INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMPTZ,
    retired_at TIMESTAMPTZ,
    CHECK (length(trim(artifact_key)) > 0),
    CHECK (length(trim(name)) > 0),
    CHECK (length(trim(research_question)) > 0),
    CHECK (length(trim(target_user_group)) > 0),
    CHECK (revision_number > 0),
    CHECK (
        (lifecycle = 'draft' AND published_at IS NULL AND retired_at IS NULL)
        OR
        (lifecycle = 'testable' AND published_at IS NOT NULL
            AND retired_at IS NULL)
        OR
        (lifecycle = 'retired' AND published_at IS NOT NULL
            AND retired_at IS NOT NULL)
    )
);

CREATE TABLE prototype_screens (
    screen_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prototype_id BIGINT NOT NULL REFERENCES prototypes(prototype_id)
        ON DELETE CASCADE,
    screen_key TEXT NOT NULL,
    display_name TEXT NOT NULL,
    purpose TEXT NOT NULL,
    sequence_order INTEGER NOT NULL,
    UNIQUE (prototype_id, screen_key),
    UNIQUE (prototype_id, sequence_order),
    CHECK (length(trim(screen_key)) > 0),
    CHECK (length(trim(display_name)) > 0),
    CHECK (length(trim(purpose)) > 0),
    CHECK (sequence_order >= 0)
);

CREATE TABLE prototype_elements (
    element_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES prototype_screens(screen_id)
        ON DELETE CASCADE,
    element_key TEXT NOT NULL,
    label TEXT NOT NULL,
    element_type TEXT NOT NULL CHECK (
        element_type IN (
            'text', 'button', 'input', 'card', 'table', 'navigation'
        )
    ),
    interactive BOOLEAN NOT NULL DEFAULT FALSE,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (screen_id, element_key),
    CHECK (length(trim(element_key)) > 0),
    CHECK (length(trim(label)) > 0),
    CHECK (jsonb_typeof(properties) = 'object')
);

CREATE TABLE prototype_revisions (
    revision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prototype_id BIGINT NOT NULL REFERENCES prototypes(prototype_id)
        ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    rationale TEXT NOT NULL,
    evidence_source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (prototype_id, revision_number),
    CHECK (revision_number > 0),
    CHECK (length(trim(rationale)) > 0),
    CHECK (length(trim(evidence_source)) > 0)
);

CREATE TABLE research_tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prototype_id BIGINT NOT NULL REFERENCES prototypes(prototype_id)
        ON DELETE CASCADE,
    task_key TEXT NOT NULL,
    task_description TEXT NOT NULL,
    expected_outcome TEXT NOT NULL,
    completion_threshold_seconds NUMERIC(10, 2) NOT NULL,
    UNIQUE (prototype_id, task_key),
    CHECK (length(trim(task_key)) > 0),
    CHECK (length(trim(task_description)) > 0),
    CHECK (length(trim(expected_outcome)) > 0),
    CHECK (completion_threshold_seconds > 0)
);

CREATE TABLE usability_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task_id BIGINT NOT NULL REFERENCES research_tasks(task_id)
        ON DELETE CASCADE,
    participant_code TEXT NOT NULL,
    outcome task_outcome NOT NULL,
    duration_seconds NUMERIC(10, 2) NOT NULL,
    observed_errors INTEGER NOT NULL DEFAULT 0,
    confidence_score INTEGER NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (task_id, participant_code),
    CHECK (length(trim(participant_code)) > 0),
    CHECK (duration_seconds >= 0),
    CHECK (observed_errors >= 0),
    CHECK (confidence_score BETWEEN 1 AND 5)
);

CREATE TABLE prototype_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prototype_id BIGINT NOT NULL REFERENCES prototypes(prototype_id)
        ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK (
        decision IN ('iterate', 'advance', 'hold', 'retire')
    ),
    rationale TEXT NOT NULL,
    evidence_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(rationale)) > 0),
    CHECK (jsonb_typeof(evidence_summary) = 'object')
);

CREATE INDEX idx_prototypes_fidelity_lifecycle
    ON prototypes (fidelity, lifecycle);

CREATE INDEX idx_screens_prototype_order
    ON prototype_screens (prototype_id, sequence_order);

CREATE INDEX idx_elements_interactive
    ON prototype_elements (screen_id)
    WHERE interactive = TRUE;

CREATE INDEX idx_tasks_prototype
    ON research_tasks (prototype_id, task_key);

CREATE INDEX idx_observations_task_outcome
    ON usability_observations (task_id, outcome);

CREATE INDEX idx_observations_time
    ON usability_observations (observed_at DESC);

CREATE INDEX idx_decisions_prototype_time
    ON prototype_decisions (prototype_id, decided_at DESC);

-- Lifecycle transitions are enforced at the database boundary so a direct
-- SQL update cannot bypass the prototype's basic publication rules.
CREATE OR REPLACE FUNCTION enforce_prototype_lifecycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.lifecycle = 'retired' AND NEW.lifecycle <> 'retired' THEN
        RAISE EXCEPTION 'Retired prototypes cannot be reactivated';
    END IF;

    IF OLD.lifecycle = 'draft' AND NEW.lifecycle = 'retired' THEN
        RAISE EXCEPTION 'Publish a draft before retiring it';
    END IF;

    IF OLD.lifecycle = 'testable' AND NEW.lifecycle = 'draft' THEN
        RAISE EXCEPTION 'A published prototype cannot return to draft';
    END IF;

    IF OLD.lifecycle = 'draft' AND NEW.lifecycle = 'testable' THEN
        NEW.published_at := COALESCE(NEW.published_at, CURRENT_TIMESTAMP);
    END IF;

    IF OLD.lifecycle <> 'retired' AND NEW.lifecycle = 'retired' THEN
        IF OLD.lifecycle <> 'testable' THEN
            RAISE EXCEPTION 'Only testable prototypes can be retired';
        END IF;
        NEW.retired_at := COALESCE(NEW.retired_at, CURRENT_TIMESTAMP);
    END IF;

    IF NEW.revision_number < OLD.revision_number THEN
        RAISE EXCEPTION 'Revision number cannot decrease';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prototype_lifecycle
BEFORE UPDATE ON prototypes
FOR EACH ROW
EXECUTE FUNCTION enforce_prototype_lifecycle();

INSERT INTO prototypes (
    artifact_key, name, fidelity, research_question, target_user_group
) VALUES
(
    'EXP-PAPER',
    'Expense submission paper sketch',
    'low',
    'Can employees locate the primary expense action?',
    'Employees'
),
(
    'EXP-CLICK',
    'Clickable expense workflow',
    'medium',
    'Can employees complete the form without assistance?',
    'Employees'
),
(
    'EXP-REALISTIC',
    'Realistic expense interaction model',
    'high',
    'Does visible loading feedback prevent duplicate actions?',
    'Employees and finance reviewers'
);

UPDATE prototypes
SET lifecycle = 'testable'
WHERE artifact_key IN ('EXP-PAPER', 'EXP-CLICK', 'EXP-REALISTIC');

INSERT INTO prototype_screens (
    prototype_id, screen_key, display_name, purpose, sequence_order
)
SELECT prototype_id, 'dashboard', 'Expense dashboard',
       'Locate the expense submission action', 0
FROM prototypes;

INSERT INTO prototype_screens (
    prototype_id, screen_key, display_name, purpose, sequence_order
)
SELECT prototype_id, 'form', 'Expense form',
       'Enter and validate expense details', 1
FROM prototypes;

INSERT INTO prototype_screens (
    prototype_id, screen_key, display_name, purpose, sequence_order
)
SELECT prototype_id, 'confirmation', 'Submission confirmation',
       'Communicate successful submission', 2
FROM prototypes
WHERE fidelity IN ('medium', 'high');

-- Low-fidelity controls are intentionally non-interactive. Medium fidelity
-- introduces clickable structure; high fidelity adds realistic feedback states.
INSERT INTO prototype_elements (
    screen_id, element_key, label, element_type, interactive, properties
)
SELECT s.screen_id, 'submit', 'Submit expense', 'button',
       p.fidelity IN ('medium', 'high'),
       CASE
           WHEN p.fidelity = 'low'
               THEN '{"representation":"paper sketch"}'::jsonb
           WHEN p.fidelity = 'medium'
               THEN '{"behavior":"navigation only"}'::jsonb
           ELSE
               '{"behavior":"loading and confirmation","role":"primary"}'::jsonb
       END
FROM prototype_screens s
JOIN prototypes p ON p.prototype_id = s.prototype_id
WHERE s.screen_key = 'dashboard';

INSERT INTO prototype_elements (
    screen_id, element_key, label, element_type, interactive, properties
)
SELECT s.screen_id, 'description', 'Expense description', 'input',
       p.fidelity IN ('medium', 'high'),
       '{"required":true,"max_length":200}'::jsonb
FROM prototype_screens s
JOIN prototypes p ON p.prototype_id = s.prototype_id
WHERE s.screen_key = 'form';

INSERT INTO prototype_elements (
    screen_id, element_key, label, element_type, interactive, properties
)
SELECT s.screen_id, 'amount', 'Amount in INR', 'input',
       p.fidelity IN ('medium', 'high'),
       '{"minimum":0.01,"maximum":1000000,"currency":"INR"}'::jsonb
FROM prototype_screens s
JOIN prototypes p ON p.prototype_id = s.prototype_id
WHERE s.screen_key = 'form';

INSERT INTO prototype_elements (
    screen_id, element_key, label, element_type, interactive, properties
)
SELECT s.screen_id, 'category', 'Expense category', 'input',
       p.fidelity IN ('medium', 'high'),
       '{"options":["Travel","Operations","Software"]}'::jsonb
FROM prototype_screens s
JOIN prototypes p ON p.prototype_id = s.prototype_id
WHERE s.screen_key = 'form';

INSERT INTO prototype_elements (
    screen_id, element_key, label, element_type, interactive, properties
)
SELECT s.screen_id, 'receipt', 'Submission receipt', 'text', FALSE,
       '{"feedback":"success message","shows_reference":true}'::jsonb
FROM prototype_screens s
JOIN prototypes p ON p.prototype_id = s.prototype_id
WHERE s.screen_key = 'confirmation';

INSERT INTO prototype_revisions (
    prototype_id, revision_number, rationale, evidence_source
)
SELECT prototype_id, 2,
       'Clarify that the amount field expects INR and reject zero values.',
       'Moderated form usability sessions'
FROM prototypes
WHERE artifact_key = 'EXP-CLICK';

UPDATE prototypes
SET revision_number = 2
WHERE artifact_key = 'EXP-CLICK';

INSERT INTO research_tasks (
    prototype_id, task_key, task_description, expected_outcome,
    completion_threshold_seconds
)
SELECT prototype_id, 'submit-expense',
       'Submit a travel expense',
       'A receipt is displayed after valid submission',
       60.00
FROM prototypes;

INSERT INTO research_tasks (
    prototype_id, task_key, task_description, expected_outcome,
    completion_threshold_seconds
)
SELECT prototype_id, 'recover-invalid-amount',
       'Correct an invalid expense amount',
       'The amount is rejected and the user can correct it',
       30.00
FROM prototypes;

INSERT INTO usability_observations (
    task_id, participant_code, outcome, duration_seconds,
    observed_errors, confidence_score, notes
)
SELECT t.task_id, sample.participant_code, sample.outcome::task_outcome,
       sample.duration_seconds, sample.observed_errors,
       sample.confidence_score, sample.notes
FROM research_tasks t
JOIN prototypes p ON p.prototype_id = t.prototype_id
CROSS JOIN (
    VALUES
        ('EMP-A', 'completed', 24.00, 0, 5,
         'Found the primary action quickly'),
        ('EMP-B', 'completed', 39.00, 1, 4,
         'Paused at the amount field'),
        ('EMP-C', 'abandoned', 60.00, 3, 2,
         'Could not determine the next action')
) AS sample(
    participant_code, outcome, duration_seconds,
    observed_errors, confidence_score, notes
)
WHERE p.artifact_key = 'EXP-CLICK'
  AND t.task_key = 'submit-expense';

INSERT INTO usability_observations (
    task_id, participant_code, outcome, duration_seconds,
    observed_errors, confidence_score, notes
)
SELECT t.task_id, sample.participant_code, sample.outcome::task_outcome,
       sample.duration_seconds, sample.observed_errors,
       sample.confidence_score, sample.notes
FROM research_tasks t
JOIN prototypes p ON p.prototype_id = t.prototype_id
CROSS JOIN (
    VALUES
        ('EMP-A', 'completed', 12.00, 1, 4,
         'Recovered after reading the validation message'),
        ('EMP-B', 'completed', 18.00, 2, 3,
         'Entered a negative amount first'),
        ('EMP-C', 'completed', 25.00, 1, 3,
         'Needed time to locate the field')
) AS sample(
    participant_code, outcome, duration_seconds,
    observed_errors, confidence_score, notes
)
WHERE p.artifact_key = 'EXP-CLICK'
  AND t.task_key = 'recover-invalid-amount';

CREATE VIEW task_usability_metrics AS
SELECT
    p.artifact_key,
    p.fidelity,
    t.task_key,
    t.expected_outcome,
    t.completion_threshold_seconds,
    COUNT(o.observation_id) AS attempts,
    COUNT(*) FILTER (WHERE o.outcome = 'completed') AS completions,
    ROUND(
        COUNT(*) FILTER (WHERE o.outcome = 'completed')::NUMERIC
        / NULLIF(COUNT(o.observation_id), 0),
        3
    ) AS completion_rate,
    ROUND(AVG(o.duration_seconds), 2) AS mean_duration_seconds,
    SUM(o.observed_errors) AS total_errors,
    ROUND(AVG(o.confidence_score), 2) AS mean_confidence,
    COUNT(*) FILTER (
        WHERE o.outcome = 'completed'
          AND o.duration_seconds <= t.completion_threshold_seconds
    ) AS successful_attempts_within_threshold
FROM prototypes p
JOIN research_tasks t ON t.prototype_id = p.prototype_id
LEFT JOIN usability_observations o ON o.task_id = t.task_id
GROUP BY
    p.artifact_key,
    p.fidelity,
    t.task_key,
    t.expected_outcome,
    t.completion_threshold_seconds;

CREATE VIEW fidelity_evaluation AS
SELECT
    p.artifact_key,
    p.fidelity,
    p.lifecycle,
    COUNT(DISTINCT s.screen_id) AS screen_count,
    COUNT(e.element_id) AS element_count,
    COUNT(e.element_id) FILTER (WHERE e.interactive) AS interactive_elements,
    COALESCE(
        ROUND(AVG(m.completion_rate), 3),
        NULL
    ) AS mean_task_completion_rate,
    COALESCE(SUM(m.total_errors), 0) AS observed_errors
FROM prototypes p
LEFT JOIN prototype_screens s ON s.prototype_id = p.prototype_id
LEFT JOIN prototype_elements e ON e.screen_id = s.screen_id
LEFT JOIN task_usability_metrics m ON m.artifact_key = p.artifact_key
GROUP BY p.prototype_id, p.artifact_key, p.fidelity, p.lifecycle;

INSERT INTO prototype_decisions (
    prototype_id, decision, rationale, evidence_summary
)
SELECT
    p.prototype_id,
    CASE
        WHEN AVG(m.completion_rate) < 0.90 THEN 'iterate'
        ELSE 'advance'
    END,
    CASE
        WHEN AVG(m.completion_rate) < 0.90
            THEN 'Completion evidence indicates that the interaction needs revision.'
        ELSE 'Observed task completion meets the current experimental threshold.'
    END,
    jsonb_build_object(
        'mean_completion_rate', ROUND(AVG(m.completion_rate), 3),
        'total_errors', SUM(m.total_errors),
        'tasks_evaluated', COUNT(m.task_key)
    )
FROM prototypes p
JOIN task_usability_metrics m ON m.artifact_key = p.artifact_key
WHERE p.artifact_key = 'EXP-CLICK'
GROUP BY p.prototype_id;

-- Compare fidelity as an artifact property and usability as an observed result.
-- High visual detail is not evidence of higher task success.
SELECT *
FROM fidelity_evaluation
ORDER BY CASE fidelity
    WHEN 'low' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'high' THEN 3
END;

SELECT *
FROM task_usability_metrics
ORDER BY artifact_key, task_key;

SELECT
    p.artifact_key,
    d.decision,
    d.rationale,
    d.evidence_summary,
    d.decided_at
FROM prototype_decisions d
JOIN prototypes p ON p.prototype_id = d.prototype_id
ORDER BY d.decided_at DESC;

-- Demonstrate database-level validation without aborting the complete script.
DO $$
BEGIN
    BEGIN
        INSERT INTO usability_observations (
            task_id, participant_code, outcome, duration_seconds,
            observed_errors, confidence_score
        )
        SELECT task_id, 'INVALID-EMPLOYEE', 'completed', 12, 0, 7
        FROM research_tasks
        WHERE task_key = 'submit-expense'
        LIMIT 1;

        RAISE EXCEPTION 'Expected invalid confidence score to be rejected';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Correctly rejected confidence outside 1..5';
        WHEN raise_exception THEN
            IF SQLERRM LIKE 'Expected invalid confidence score%' THEN
                RAISE;
            END IF;
    END;
END;
$$;

COMMIT;
