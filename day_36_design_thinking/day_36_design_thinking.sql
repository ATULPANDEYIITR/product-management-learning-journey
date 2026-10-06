DROP SCHEMA IF EXISTS design_thinking CASCADE;
CREATE SCHEMA design_thinking;

SET search_path TO design_thinking;

CREATE TYPE design_stage AS ENUM (
    'EMPATHIZE',
    'DEFINE',
    'IDEATE',
    'PROTOTYPE',
    'TEST'
);

CREATE TYPE idea_status AS ENUM (
    'CANDIDATE',
    'SELECTED',
    'REJECTED'
);

CREATE TYPE test_outcome AS ENUM (
    'SUCCESS',
    'FAILURE'
);

CREATE TABLE users (
    user_id          BIGSERIAL PRIMARY KEY,
    external_key     VARCHAR(50) NOT NULL UNIQUE,
    name             VARCHAR(120) NOT NULL,
    role             VARCHAR(120) NOT NULL,
    context          TEXT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE design_projects (
    project_id       BIGSERIAL PRIMARY KEY,
    project_name     VARCHAR(200) NOT NULL,
    current_stage    design_stage NOT NULL DEFAULT 'EMPATHIZE',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE observations (
    observation_id      BIGSERIAL PRIMARY KEY,
    project_id          BIGINT NOT NULL REFERENCES design_projects(project_id)
                         ON DELETE CASCADE,
    user_id             BIGINT NOT NULL REFERENCES users(user_id),
    behavior            TEXT NOT NULL,
    quote               TEXT,
    pain_point          TEXT NOT NULL,
    evidence_strength   NUMERIC(4,3) NOT NULL
                        CHECK (evidence_strength BETWEEN 0 AND 1),
    observed_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_observations_project_pain_point
    ON observations(project_id, pain_point);

CREATE TABLE insights (
    insight_id       BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES design_projects(project_id)
                     ON DELETE CASCADE,
    statement        TEXT NOT NULL,
    confidence       NUMERIC(4,3) NOT NULL
                     CHECK (confidence BETWEEN 0 AND 1),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE insight_evidence (
    insight_id       BIGINT NOT NULL REFERENCES insights(insight_id)
                     ON DELETE CASCADE,
    observation_id   BIGINT NOT NULL REFERENCES observations(observation_id)
                     ON DELETE CASCADE,
    PRIMARY KEY (insight_id, observation_id)
);

CREATE TABLE problem_statements (
    problem_id       BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES design_projects(project_id)
                     ON DELETE CASCADE,
    user_definition  TEXT NOT NULL,
    need              TEXT NOT NULL,
    insight          TEXT NOT NULL,
    success_measure  TEXT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id)
);

CREATE TABLE ideas (
    idea_id          BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES design_projects(project_id)
                     ON DELETE CASCADE,
    name             VARCHAR(200) NOT NULL,
    description      TEXT NOT NULL,
    user_value       NUMERIC(4,2) NOT NULL CHECK (user_value BETWEEN 0 AND 10),
    feasibility      NUMERIC(4,2) NOT NULL CHECK (feasibility BETWEEN 0 AND 10),
    desirability     NUMERIC(4,2) NOT NULL CHECK (desirability BETWEEN 0 AND 10),
    risk             NUMERIC(4,2) NOT NULL CHECK (risk BETWEEN 0 AND 10),
    status           idea_status NOT NULL DEFAULT 'CANDIDATE',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, name)
);

CREATE INDEX idx_ideas_project_score
    ON ideas(project_id, user_value, feasibility, desirability);

CREATE TABLE prototypes (
    prototype_id     BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES design_projects(project_id)
                     ON DELETE CASCADE,
    idea_id          BIGINT NOT NULL REFERENCES ideas(idea_id),
    fidelity         VARCHAR(40) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prototype_interactions (
    interaction_id   BIGSERIAL PRIMARY KEY,
    prototype_id     BIGINT NOT NULL REFERENCES prototypes(prototype_id)
                     ON DELETE CASCADE,
    interaction      TEXT NOT NULL
);

CREATE TABLE prototype_assumptions (
    assumption_id    BIGSERIAL PRIMARY KEY,
    prototype_id     BIGINT NOT NULL REFERENCES prototypes(prototype_id)
                     ON DELETE CASCADE,
    assumption       TEXT NOT NULL
);

CREATE TABLE usability_tests (
    test_id          BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES design_projects(project_id)
                     ON DELETE CASCADE,
    prototype_id     BIGINT NOT NULL REFERENCES prototypes(prototype_id),
    user_id          BIGINT NOT NULL REFERENCES users(user_id),
    task             TEXT NOT NULL,
    outcome          test_outcome NOT NULL,
    time_seconds     NUMERIC(10,2) NOT NULL CHECK (time_seconds > 0),
    errors           INTEGER NOT NULL CHECK (errors >= 0),
    satisfaction     INTEGER NOT NULL CHECK (satisfaction BETWEEN 1 AND 5),
    observation      TEXT NOT NULL,
    tested_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usability_tests_project_outcome
    ON usability_tests(project_id, outcome);

CREATE VIEW idea_evaluation AS
SELECT
    idea_id,
    project_id,
    name,
    status,
    ROUND(
        (
            user_value * 0.40
            + feasibility * 0.25
            + desirability * 0.25
            - risk * 0.10
        )::numeric,
        2
    ) AS design_score
FROM ideas;

CREATE VIEW project_test_metrics AS
SELECT
    project_id,
    COUNT(*) AS test_count,
    ROUND(
        AVG(CASE WHEN outcome = 'SUCCESS' THEN 1.0 ELSE 0.0 END) * 100,
        2
    ) AS completion_rate_percent,
    ROUND(AVG(time_seconds), 2) AS average_time_seconds,
    ROUND(AVG(errors), 2) AS average_errors,
    ROUND(AVG(satisfaction), 2) AS average_satisfaction
FROM usability_tests
GROUP BY project_id;

INSERT INTO design_projects (project_name)
VALUES ('Internal Request Processing Experience');

INSERT INTO users (external_key, name, role, context)
VALUES
    (
        'U01',
        'Anika',
        'Operations Analyst',
        'Processes a high volume of internal requests.'
    ),
    (
        'U02',
        'Ravi',
        'Finance Analyst',
        'Reviews requests requiring financial approval.'
    ),
    (
        'U03',
        'Meera',
        'Team Manager',
        'Monitors blocked work and queue health.'
    );

INSERT INTO observations (
    project_id,
    user_id,
    behavior,
    quote,
    pain_point,
    evidence_strength
)
SELECT
    p.project_id,
    u.user_id,
    'Copies queue information into a spreadsheet',
    'I need my own sheet to understand what is waiting.',
    'Request state is difficult to see',
    0.95
FROM design_projects p
JOIN users u ON u.external_key = 'U01'
WHERE p.project_name = 'Internal Request Processing Experience';

INSERT INTO observations (
    project_id,
    user_id,
    behavior,
    quote,
    pain_point,
    evidence_strength
)
SELECT
    p.project_id,
    u.user_id,
    'Switches applications to locate request context',
    'I check multiple places before I can start.',
    'Information is fragmented',
    0.90
FROM design_projects p
JOIN users u ON u.external_key = 'U01'
WHERE p.project_name = 'Internal Request Processing Experience';

INSERT INTO observations (
    project_id,
    user_id,
    behavior,
    quote,
    pain_point,
    evidence_strength
)
SELECT
    p.project_id,
    u.user_id,
    'Delays approval when supporting evidence is incomplete',
    'I need enough context to make the decision.',
    'Decision context is incomplete',
    0.92
FROM design_projects p
JOIN users u ON u.external_key = 'U02'
WHERE p.project_name = 'Internal Request Processing Experience';

INSERT INTO observations (
    project_id,
    user_id,
    behavior,
    quote,
    pain_point,
    evidence_strength
)
SELECT
    p.project_id,
    u.user_id,
    'Contacts analysts to discover why work is blocked',
    'The count tells me something is wrong, not why.',
    'Metrics do not explain blockers',
    0.88
FROM design_projects p
JOIN users u ON u.external_key = 'U03'
WHERE p.project_name = 'Internal Request Processing Experience';

INSERT INTO insights (project_id, statement, confidence)
SELECT
    p.project_id,
    'Users experience request-state uncertainty repeatedly and need visible workflow state.',
    AVG(o.evidence_strength)
FROM design_projects p
JOIN observations o ON o.project_id = p.project_id
WHERE o.pain_point = 'Request state is difficult to see'
GROUP BY p.project_id;

INSERT INTO insights (project_id, statement, confidence)
SELECT
    p.project_id,
    'Users lose processing time when request context is distributed across systems.',
    AVG(o.evidence_strength)
FROM design_projects p
JOIN observations o ON o.project_id = p.project_id
WHERE o.pain_point = 'Information is fragmented'
GROUP BY p.project_id;

INSERT INTO insights (project_id, statement, confidence)
SELECT
    p.project_id,
    'Approvers need decision-relevant evidence at the point of approval.',
    AVG(o.evidence_strength)
FROM design_projects p
JOIN observations o ON o.project_id = p.project_id
WHERE o.pain_point = 'Decision context is incomplete'
GROUP BY p.project_id;

INSERT INTO insights (project_id, statement, confidence)
SELECT
    p.project_id,
    'Managers need explanations of blocked work rather than aggregate counts alone.',
    AVG(o.evidence_strength)
FROM design_projects p
JOIN observations o ON o.project_id = p.project_id
WHERE o.pain_point = 'Metrics do not explain blockers'
GROUP BY p.project_id;

INSERT INTO insight_evidence (insight_id, observation_id)
SELECT
    i.insight_id,
    o.observation_id
FROM insights i
JOIN observations o
    ON o.project_id = i.project_id
   AND (
        (i.statement LIKE 'Users experience request-state%' AND
         o.pain_point = 'Request state is difficult to see')
        OR
        (i.statement LIKE 'Users lose processing%' AND
         o.pain_point = 'Information is fragmented')
        OR
        (i.statement LIKE 'Approvers need%' AND
         o.pain_point = 'Decision context is incomplete')
        OR
        (i.statement LIKE 'Managers need%' AND
         o.pain_point = 'Metrics do not explain blockers')
   );

INSERT INTO problem_statements (
    project_id,
    user_definition,
    need,
    insight,
    success_measure
)
SELECT
    project_id,
    'Employees processing internal requests',
    'A contextual workflow that exposes state, evidence, and next action',
    'Observed work is slowed by fragmented information, unclear state, and insufficient decision context.',
    'Reduce processing time while maintaining decision accuracy'
FROM design_projects
WHERE project_name = 'Internal Request Processing Experience';

INSERT INTO ideas (
    project_id,
    name,
    description,
    user_value,
    feasibility,
    desirability,
    risk,
    status
)
SELECT
    project_id,
    'Contextual Request Workspace',
    'A unified request view with state, evidence, history, and next action.',
    9,
    8,
    9,
    3,
    'SELECTED'
FROM design_projects
WHERE project_name = 'Internal Request Processing Experience';

INSERT INTO ideas (
    project_id,
    name,
    description,
    user_value,
    feasibility,
    desirability,
    risk
)
SELECT
    project_id,
    'Decision Summary Panel',
    'A focused approval surface containing purpose, evidence, and exceptions.',
    8,
    9,
    8,
    2
FROM design_projects
WHERE project_name = 'Internal Request Processing Experience';

INSERT INTO ideas (
    project_id,
    name,
    description,
    user_value,
    feasibility,
    desirability,
    risk
)
SELECT
    project_id,
    'Blocker Explanation Engine',
    'A workflow component that explains exactly why a request cannot proceed.',
    8,
    7,
    7,
    5
FROM design_projects
WHERE project_name = 'Internal Request Processing Experience';

INSERT INTO prototypes (
    project_id,
    idea_id,
    fidelity
)
SELECT
    i.project_id,
    i.idea_id,
    'Medium'
FROM ideas i
WHERE i.name = 'Contextual Request Workspace';

INSERT INTO prototype_interactions (prototype_id, interaction)
SELECT prototype_id, interaction
FROM prototypes
CROSS JOIN LATERAL (
    VALUES
        ('Filter the request queue'),
        ('Open request context'),
        ('Inspect decision evidence'),
        ('Identify blocking information'),
        ('Perform the next workflow action')
) AS interaction_values(interaction);

INSERT INTO prototype_assumptions (prototype_id, assumption)
SELECT prototype_id, assumption
FROM prototypes
CROSS JOIN LATERAL (
    VALUES
        ('Users can identify the next action without changing screens.'),
        ('Approvers can access decision context at the decision point.'),
        ('Blocked requests expose the information required for recovery.')
) AS assumption_values(assumption);

INSERT INTO usability_tests (
    project_id,
    prototype_id,
    user_id,
    task,
    outcome,
    time_seconds,
    errors,
    satisfaction,
    observation
)
SELECT
    p.project_id,
    pr.prototype_id,
    u.user_id,
    'Find the next processable request',
    'SUCCESS',
    38,
    1,
    4,
    'The state filter was easy to find, but one status label caused hesitation.'
FROM design_projects p
JOIN prototypes pr ON pr.project_id = p.project_id
JOIN users u ON u.external_key = 'U01';

INSERT INTO usability_tests (
    project_id,
    prototype_id,
    user_id,
    task,
    outcome,
    time_seconds,
    errors,
    satisfaction,
    observation
)
SELECT
    p.project_id,
    pr.prototype_id,
    u.user_id,
    'Approve a request using available evidence',
    'SUCCESS',
    46,
    0,
    5,
    'The decision context was available without leaving the request.'
FROM design_projects p
JOIN prototypes pr ON pr.project_id = p.project_id
JOIN users u ON u.external_key = 'U02';

INSERT INTO usability_tests (
    project_id,
    prototype_id,
    user_id,
    task,
    outcome,
    time_seconds,
    errors,
    satisfaction,
    observation
)
SELECT
    p.project_id,
    pr.prototype_id,
    u.user_id,
    'Identify why a request is blocked',
    'FAILURE',
    71,
    3,
    2,
    'The blocked state was visible, but the missing information was unclear.'
FROM design_projects p
JOIN prototypes pr ON pr.project_id = p.project_id
JOIN users u ON u.external_key = 'U03';

UPDATE design_projects
SET current_stage = 'TEST'
WHERE project_name = 'Internal Request Processing Experience';

SELECT
    p.project_name,
    i.name,
    e.design_score
FROM design_projects p
JOIN idea_evaluation e ON e.project_id = p.project_id
JOIN ideas i ON i.idea_id = e.idea_id
ORDER BY e.design_score DESC;

SELECT
    p.project_name,
    m.test_count,
    m.completion_rate_percent,
    m.average_time_seconds,
    m.average_errors,
    m.average_satisfaction
FROM design_projects p
JOIN project_test_metrics m
    ON m.project_id = p.project_id;

SELECT
    u.name,
    ut.task,
    ut.outcome,
    ut.time_seconds,
    ut.errors,
    ut.satisfaction,
    ut.observation
FROM usability_tests ut
JOIN users u ON u.user_id = ut.user_id
ORDER BY ut.tested_at;

SELECT
    o.pain_point,
    COUNT(*) AS evidence_count,
    ROUND(AVG(o.evidence_strength), 3) AS average_evidence_strength
FROM observations o
GROUP BY o.pain_point
ORDER BY average_evidence_strength DESC;

-- Database integrity prevents invalid evidence scores.
-- The following statement is intentionally commented out because it would fail:
-- INSERT INTO observations (
--     project_id, user_id, behavior, pain_point, evidence_strength
-- ) VALUES (1, 1, 'Invalid evidence', 'Example failure', 1.5);

BEGIN;

UPDATE prototypes
SET fidelity = 'Medium - revised after testing'
WHERE prototype_id = (
    SELECT prototype_id
    FROM prototypes
    ORDER BY prototype_id
    LIMIT 1
);

INSERT INTO prototype_assumptions (
    prototype_id,
    assumption
)
SELECT
    prototype_id,
    'Blocked requests must expose the exact missing information and recovery action.'
FROM prototypes
ORDER BY prototype_id
LIMIT 1;

COMMIT;

SELECT
    p.project_name,
    p.current_stage,
    pr.fidelity,
    pa.assumption
FROM design_projects p
JOIN prototypes pr ON pr.project_id = p.project_id
JOIN prototype_assumptions pa ON pa.prototype_id = pr.prototype_id
ORDER BY pa.assumption_id;
