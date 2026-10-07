-- ============================================================================
-- IDEATION TECHNIQUES RELATIONAL CASE STUDY
-- PostgreSQL-compatible SQL
--
-- The model deliberately distinguishes:
--
--   Brainstorming
--       Participant-based divergent idea generation.
--
--   Crazy 8s
--       Eight rapid directions associated with a time-boxed challenge.
--
--   SCAMPER
--       Transformations applied to an existing concept.
--
--   Mind Mapping
--       Hierarchical nodes connected to a central problem.
--
--   Reverse Brainstorming
--       Failure mechanisms and their corresponding countermeasures.
--
-- The scenario is customer support operations: reducing response time while
-- protecting resolution quality.
-- ============================================================================

DROP SCHEMA IF EXISTS ideation_lab CASCADE;

CREATE SCHEMA ideation_lab;

SET search_path TO ideation_lab;

-- ============================================================================
-- Core reference data
-- ============================================================================

CREATE TABLE technique (
    technique_id BIGSERIAL PRIMARY KEY,
    technique_code TEXT NOT NULL UNIQUE,
    technique_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

INSERT INTO technique (
    technique_code,
    technique_name,
    description
)
VALUES
(
    'BRAINSTORMING',
    'Brainstorming',
    'Participant-driven divergent generation with evaluation deliberately delayed.'
),
(
    'CRAZY_8S',
    'Crazy 8s',
    'Rapid generation of eight distinct directions under a time-boxed constraint.'
),
(
    'SCAMPER',
    'SCAMPER',
    'Structured transformation of an existing concept through seven operators.'
),
(
    'MIND_MAPPING',
    'Mind Mapping',
    'Hierarchical association of a central problem with dimensions and subtopics.'
),
(
    'REVERSE_BRAINSTORMING',
    'Reverse Brainstorming',
    'Failure-first ideation that deliberately worsens an outcome before inversion.'
);

-- ============================================================================
-- Ideation workshop and participant model
-- ============================================================================

CREATE TABLE workshop (
    workshop_id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    challenge TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'DIVERGING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        status IN (
            'DIVERGING',
            'ORGANIZING',
            'EVALUATING',
            'SELECTED',
            'CLOSED'
        )
    )
);

CREATE TABLE participant (
    participant_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    perspective TEXT NOT NULL,
    UNIQUE (name),
    CHECK (
        perspective IN (
            'CUSTOMER',
            'SUPPORT_AGENT',
            'OPERATIONS',
            'TECHNOLOGY',
            'QUALITY'
        )
    )
);

CREATE TABLE workshop_participant (
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    participant_id BIGINT NOT NULL
        REFERENCES participant(participant_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (workshop_id, participant_id)
);

-- ============================================================================
-- Existing concepts
-- ============================================================================

CREATE TABLE existing_concept (
    concept_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

-- ============================================================================
-- Ideas
-- ============================================================================

CREATE TABLE idea (
    idea_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    technique_id BIGINT NOT NULL
        REFERENCES technique(technique_id)
        ON DELETE RESTRICT,
    participant_id BIGINT
        REFERENCES participant(participant_id)
        ON DELETE RESTRICT,
    parent_idea_id BIGINT
        REFERENCES idea(idea_id)
        ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    novelty SMALLINT NOT NULL DEFAULT 3,
    feasibility SMALLINT NOT NULL DEFAULT 3,
    impact SMALLINT NOT NULL DEFAULT 3,
    confidence SMALLINT NOT NULL DEFAULT 3,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(description)) > 0),
    CHECK (novelty BETWEEN 1 AND 5),
    CHECK (feasibility BETWEEN 1 AND 5),
    CHECK (impact BETWEEN 1 AND 5),
    CHECK (confidence BETWEEN 1 AND 5),
    CHECK (parent_idea_id IS NULL OR parent_idea_id <> idea_id)
);

-- A generated score is kept as a view instead of a stored column so that
-- changes to evaluation weights cannot create stale persisted scores.
CREATE VIEW idea_scored AS
SELECT
    i.*,
    (
        i.novelty * 0.25
        + i.feasibility * 0.25
        + i.impact * 0.35
        + i.confidence * 0.15
    )::NUMERIC(6,2) AS weighted_score
FROM idea AS i;

-- Indexes support the two most common workshop queries: technique-specific
-- retrieval and high-scoring ideas within one workshop.
CREATE INDEX idx_idea_workshop_technique
    ON idea(workshop_id, technique_id);

CREATE INDEX idx_idea_workshop_impact
    ON idea(workshop_id, impact DESC, feasibility DESC);

CREATE INDEX idx_idea_parent
    ON idea(parent_idea_id);

-- ============================================================================
-- Idea tags
-- ============================================================================

CREATE TABLE idea_tag (
    idea_id BIGINT NOT NULL
        REFERENCES idea(idea_id)
        ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (idea_id, tag),
    CHECK (length(trim(tag)) > 0)
);

CREATE INDEX idx_idea_tag_tag
    ON idea_tag(tag);

-- ============================================================================
-- Crazy 8s
-- ============================================================================

CREATE TABLE crazy8_round (
    crazy8_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    challenge TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crazy8_prompt (
    crazy8_id BIGINT NOT NULL
        REFERENCES crazy8_round(crazy8_id)
        ON DELETE CASCADE,
    slot SMALLINT NOT NULL,
    prompt TEXT NOT NULL,
    idea_id BIGINT UNIQUE
        REFERENCES idea(idea_id)
        ON DELETE SET NULL,
    PRIMARY KEY (crazy8_id, slot),
    CHECK (slot BETWEEN 1 AND 8)
);

-- The following trigger guarantees that a Crazy 8s round cannot contain
-- duplicate slot numbers through the primary key, while the round-level
-- validation query below verifies completeness of all eight directions.

-- ============================================================================
-- SCAMPER
-- ============================================================================

CREATE TABLE scamper_transformation (
    scamper_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    concept_id BIGINT NOT NULL
        REFERENCES existing_concept(concept_id)
        ON DELETE CASCADE,
    operator TEXT NOT NULL,
    description TEXT NOT NULL,
    idea_id BIGINT UNIQUE
        REFERENCES idea(idea_id)
        ON DELETE SET NULL,
    UNIQUE (concept_id, operator),
    CHECK (
        operator IN (
            'SUBSTITUTE',
            'COMBINE',
            'ADAPT',
            'MODIFY',
            'PUT_TO_ANOTHER_USE',
            'ELIMINATE',
            'REVERSE'
        )
    )
);

-- ============================================================================
-- Mind mapping
-- ============================================================================

CREATE TABLE mind_map (
    mind_map_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    central_problem TEXT NOT NULL
);

CREATE TABLE mind_map_node (
    node_id BIGSERIAL PRIMARY KEY,
    mind_map_id BIGINT NOT NULL
        REFERENCES mind_map(mind_map_id)
        ON DELETE CASCADE,
    parent_node_id BIGINT
        REFERENCES mind_map_node(node_id)
        ON DELETE CASCADE,
    label TEXT NOT NULL,
    relationship TEXT NOT NULL,
    idea_id BIGINT UNIQUE
        REFERENCES idea(idea_id)
        ON DELETE SET NULL,
    CHECK (parent_node_id IS NULL OR parent_node_id <> node_id)
);

CREATE INDEX idx_mind_map_node_parent
    ON mind_map_node(mind_map_id, parent_node_id);

-- ============================================================================
-- Reverse brainstorming
-- ============================================================================

CREATE TABLE reverse_brainstorm (
    reverse_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    desired_outcome TEXT NOT NULL
);

CREATE TABLE failure_mechanism (
    failure_id BIGSERIAL PRIMARY KEY,
    reverse_id BIGINT NOT NULL
        REFERENCES reverse_brainstorm(reverse_id)
        ON DELETE CASCADE,
    failure_description TEXT NOT NULL,
    countermeasure TEXT NOT NULL,
    idea_id BIGINT UNIQUE
        REFERENCES idea(idea_id)
        ON DELETE SET NULL
);

-- ============================================================================
-- Evaluation and selection
-- ============================================================================

CREATE TABLE idea_evaluation (
    evaluation_id BIGSERIAL PRIMARY KEY,
    idea_id BIGINT NOT NULL
        REFERENCES idea(idea_id)
        ON DELETE CASCADE,
    evaluator_name TEXT NOT NULL,
    evaluation_status TEXT NOT NULL DEFAULT 'PENDING',
    rationale TEXT,
    evaluated_at TIMESTAMPTZ,
    CHECK (
        evaluation_status IN (
            'PENDING',
            'ACCEPTED',
            'REJECTED',
            'NEEDS_RESEARCH'
        )
    ),
    UNIQUE (idea_id, evaluator_name)
);

CREATE TABLE selected_concept (
    selection_id BIGSERIAL PRIMARY KEY,
    workshop_id BIGINT NOT NULL
        REFERENCES workshop(workshop_id)
        ON DELETE CASCADE,
    idea_id BIGINT NOT NULL
        REFERENCES idea(idea_id)
        ON DELETE RESTRICT,
    selection_reason TEXT NOT NULL,
    selected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (workshop_id, idea_id)
);

-- ============================================================================
-- Realistic workshop
-- ============================================================================

INSERT INTO workshop (
    title,
    challenge
)
VALUES (
    'Customer Support Response Improvement',
    'Reduce customer support response time without reducing resolution quality.'
);

INSERT INTO participant (name, perspective)
VALUES
    ('Asha', 'CUSTOMER'),
    ('Ravi', 'SUPPORT_AGENT'),
    ('Meera', 'OPERATIONS'),
    ('Kabir', 'TECHNOLOGY'),
    ('Nisha', 'QUALITY');

INSERT INTO workshop_participant (
    workshop_id,
    participant_id
)
SELECT
    1,
    participant_id
FROM participant;

-- ============================================================================
-- Brainstorming ideas
-- ============================================================================

INSERT INTO idea (
    workshop_id,
    technique_id,
    participant_id,
    title,
    description,
    novelty,
    feasibility,
    impact,
    confidence
)
SELECT
    1,
    t.technique_id,
    p.participant_id,
    p.name || ' perspective',
    CASE p.perspective
        WHEN 'CUSTOMER'
            THEN 'Show response expectations and proactive progress updates.'
        WHEN 'SUPPORT_AGENT'
            THEN 'Surface similar resolved cases while an agent works.'
        WHEN 'OPERATIONS'
            THEN 'Escalate cases according to queue age and workload.'
        WHEN 'TECHNOLOGY'
            THEN 'Classify incoming requests automatically before routing.'
        WHEN 'QUALITY'
            THEN 'Measure response speed together with reopening and quality.'
    END,
    CASE p.perspective
        WHEN 'TECHNOLOGY' THEN 5
        ELSE 4
    END,
    4,
    4,
    4
FROM participant p
CROSS JOIN technique t
WHERE t.technique_code = 'BRAINSTORMING';

INSERT INTO idea_tag (idea_id, tag)
SELECT
    idea_id,
    'divergent'
FROM idea
WHERE workshop_id = 1
  AND technique_id = (
      SELECT technique_id
      FROM technique
      WHERE technique_code = 'BRAINSTORMING'
  );

-- This synthesis idea demonstrates building on an existing contribution
-- without replacing the original contribution.
INSERT INTO idea (
    workshop_id,
    technique_id,
    title,
    description,
    novelty,
    feasibility,
    impact,
    confidence
)
VALUES (
    1,
    (
        SELECT technique_id
        FROM technique
        WHERE technique_code = 'BRAINSTORMING'
    ),
    'Unified intelligent intake',
    'Combine automatic classification, duplicate detection, and knowledge retrieval before assignment.',
    5,
    4,
    5,
    4
);

-- ============================================================================
-- Crazy 8s
-- ============================================================================

INSERT INTO crazy8_round (
    workshop_id,
    challenge
)
VALUES (
    1,
    'Reduce response time without adding permanent headcount.'
);

INSERT INTO crazy8_prompt (crazy8_id, slot, prompt)
VALUES
    (1, 1, 'Remove a manual triage step.'),
    (1, 2, 'Automate request classification.'),
    (1, 3, 'Create guided self-service.'),
    (1, 4, 'Reverse the normal assignment flow.'),
    (1, 5, 'Personalize the resolution path.'),
    (1, 6, 'Make queue state visible.'),
    (1, 7, 'Combine intake and knowledge retrieval.'),
    (1, 8, 'Design an intentionally extreme low-touch path.');

INSERT INTO idea (
    workshop_id,
    technique_id,
    title,
    description,
    novelty,
    feasibility,
    impact,
    confidence
)
SELECT
    1,
    (
        SELECT technique_id
        FROM technique
        WHERE technique_code = 'CRAZY_8S'
    ),
    'Crazy 8 direction ' || slot,
    prompt,
    CASE
        WHEN slot >= 7 THEN 5
        ELSE 4
    END,
    CASE
        WHEN slot IN (1, 2, 6, 7) THEN 4
        ELSE 3
    END,
    CASE
        WHEN slot IN (2, 3, 4, 7, 8) THEN 5
        ELSE 4
    END,
    3
FROM crazy8_prompt
WHERE crazy8_id = 1;

UPDATE crazy8_prompt cp
SET idea_id = i.idea_id
FROM idea i
WHERE i.workshop_id = 1
  AND i.technique_id = (
      SELECT technique_id
      FROM technique
      WHERE technique_code = 'CRAZY_8S'
  )
  AND i.title = 'Crazy 8 direction ' || cp.slot;

-- ============================================================================
-- SCAMPER transformations
-- ============================================================================

INSERT INTO existing_concept (
    workshop_id,
    name,
    description
)
VALUES (
    1,
    'Manual support queue',
    'A conventional queue in which requests are manually classified and assigned.'
);

INSERT INTO scamper_transformation (
    workshop_id,
    concept_id,
    operator,
    description
)
VALUES
(
    1,
    1,
    'SUBSTITUTE',
    'Replace first-come-first-served routing with skill and urgency routing.'
),
(
    1,
    1,
    'COMBINE',
    'Combine intake, classification, and knowledge retrieval.'
),
(
    1,
    1,
    'ADAPT',
    'Adapt emergency-dispatch queueing principles for severe cases.'
),
(
    1,
    1,
    'MODIFY',
    'Make intake questions adaptive to previous answers.'
),
(
    1,
    1,
    'PUT_TO_ANOTHER_USE',
    'Use support history to identify recurring product defects.'
),
(
    1,
    1,
    'ELIMINATE',
    'Remove supervisor handoffs for low-risk known resolutions.'
),
(
    1,
    1,
    'REVERSE',
    'Push status updates before customers need to request them.'
);

INSERT INTO idea (
    workshop_id,
    technique_id,
    title,
    description,
    novelty,
    feasibility,
    impact,
    confidence
)
SELECT
    1,
    (
        SELECT technique_id
        FROM technique
        WHERE technique_code = 'SCAMPER'
    ),
    initcap(lower(replace(operator, '_', ' '))),
    description,
    5,
    CASE
        WHEN operator IN (
            'SUBSTITUTE',
            'MODIFY',
            'ELIMINATE'
        ) THEN 4
        ELSE 3
    END,
    CASE
        WHEN operator IN (
            'COMBINE',
            'PUT_TO_ANOTHER_USE',
            'REVERSE'
        ) THEN 5
        ELSE 4
    END,
    4
FROM scamper_transformation;

UPDATE scamper_transformation st
SET idea_id = i.idea_id
FROM idea i
WHERE st.workshop_id = i.workshop_id
  AND i.technique_id = (
      SELECT technique_id
      FROM technique
      WHERE technique_code = 'SCAMPER'
  )
  AND i.description = st.description;

-- ============================================================================
-- Mind map
-- ============================================================================

INSERT INTO mind_map (
    workshop_id,
    central_problem
)
VALUES (
    1,
    'Slow customer support response'
);

INSERT INTO mind_map_node (
    mind_map_id,
    parent_node_id,
    label,
    relationship
)
VALUES
    (1, NULL, 'Slow customer support response', 'central problem');

INSERT INTO mind_map_node (
    mind_map_id,
    parent_node_id,
    label,
    relationship
)
SELECT
    1,
    (
        SELECT node_id
        FROM mind_map_node
        WHERE mind_map_id = 1
          AND parent_node_id IS NULL
    ),
    'Customer experience',
    'dimension'
UNION ALL
SELECT
    1,
    (
        SELECT node_id
        FROM mind_map_node
        WHERE mind_map_id = 1
          AND parent_node_id IS NULL
    ),
    'Workflow',
    'dimension'
UNION ALL
SELECT
    1,
    (
        SELECT node_id
        FROM mind_map_node
        WHERE mind_map_id = 1
          AND parent_node_id IS NULL
    ),
    'Knowledge',
    'dimension';

INSERT INTO mind_map_node (
    mind_map_id,
    parent_node_id,
    label,
    relationship
)
SELECT
    1,
    parent.node_id,
    child.label,
    child.relationship
FROM mind_map_node parent
JOIN (
    VALUES
        ('Customer experience', 'Response expectations', 'concern'),
        ('Customer experience', 'Self-service', 'opportunity'),
        ('Customer experience', 'Progress visibility', 'opportunity'),
        ('Workflow', 'Routing', 'process'),
        ('Workflow', 'Handoffs', 'bottleneck'),
        ('Workflow', 'Queue aging', 'metric'),
        ('Knowledge', 'Search quality', 'capability'),
        ('Knowledge', 'Reusable resolutions', 'capability'),
        ('Knowledge', 'Missing documentation', 'root cause')
) AS child(parent_label, label, relationship)
    ON parent.label = child.parent_label
WHERE parent.mind_map_id = 1;

INSERT INTO mind_map_node (
    mind_map_id,
    parent_node_id,
    label,
    relationship
)
SELECT
    1,
    parent.node_id,
    child.label,
    child.relationship
FROM mind_map_node parent
JOIN (
    VALUES
        ('Routing', 'Skill matching', 'mechanism'),
        ('Routing', 'Urgency classification', 'mechanism')
) AS child(parent_label, label, relationship)
    ON parent.label = child.parent_label
WHERE parent.mind_map_id = 1;

-- ============================================================================
-- Reverse brainstorming
-- ============================================================================

INSERT INTO reverse_brainstorm (
    workshop_id,
    desired_outcome
)
VALUES (
    1,
    'Fast and reliable support response'
);

INSERT INTO failure_mechanism (
    reverse_id,
    failure_description,
    countermeasure
)
VALUES
(
    1,
    'Route every request to one queue regardless of skill.',
    'Route according to skill, urgency, and workload.'
),
(
    1,
    'Hide response expectations from customers.',
    'Expose realistic response windows and progress updates.'
),
(
    1,
    'Require approval for every support decision.',
    'Reserve approval for exceptions and high-risk cases.'
),
(
    1,
    'Copy customer information manually at every handoff.',
    'Maintain one shared case record through the workflow.'
),
(
    1,
    'Measure closure count while ignoring reopened cases.',
    'Track speed together with resolution quality and reopening.'
),
(
    1,
    'Allow aging cases to remain mixed with new cases.',
    'Use aging thresholds and explicit escalation paths.'
);

INSERT INTO idea (
    workshop_id,
    technique_id,
    title,
    description,
    novelty,
    feasibility,
    impact,
    confidence
)
SELECT
    1,
    (
        SELECT technique_id
        FROM technique
        WHERE technique_code = 'REVERSE_BRAINSTORMING'
    ),
    'Countermeasure',
    countermeasure,
    4,
    4,
    5,
    4
FROM failure_mechanism;

UPDATE failure_mechanism fm
SET idea_id = i.idea_id
FROM idea i
WHERE i.workshop_id = 1
  AND i.technique_id = (
      SELECT technique_id
      FROM technique
      WHERE technique_code = 'REVERSE_BRAINSTORMING'
  )
  AND i.description = fm.countermeasure;

-- ============================================================================
-- Topic-specific analytical queries
-- ============================================================================

-- Brainstorming contributions by participant perspective.
SELECT
    p.perspective,
    p.name AS participant,
    i.title,
    i.description
FROM idea i
JOIN participant p
    ON p.participant_id = i.participant_id
WHERE i.technique_id = (
    SELECT technique_id
    FROM technique
    WHERE technique_code = 'BRAINSTORMING'
)
ORDER BY p.perspective, p.name;

-- Compare average evaluation characteristics across techniques.
SELECT
    t.technique_name,
    COUNT(*) AS idea_count,
    ROUND(AVG(i.novelty), 2) AS avg_novelty,
    ROUND(AVG(i.feasibility), 2) AS avg_feasibility,
    ROUND(AVG(i.impact), 2) AS avg_impact,
    ROUND(AVG(s.weighted_score), 2) AS avg_weighted_score
FROM idea_scored s
JOIN idea i
    ON i.idea_id = s.idea_id
JOIN technique t
    ON t.technique_id = i.technique_id
GROUP BY t.technique_name
ORDER BY avg_weighted_score DESC;

-- Highest-scoring concepts across all techniques.
SELECT
    i.idea_id,
    t.technique_name,
    i.title,
    i.description,
    s.weighted_score
FROM idea_scored s
JOIN idea i
    ON i.idea_id = s.idea_id
JOIN technique t
    ON t.technique_id = i.technique_id
ORDER BY s.weighted_score DESC, i.impact DESC
LIMIT 10;

-- Validate that every Crazy 8s round has exactly eight prompts.
SELECT
    c.crazy8_id,
    COUNT(cp.slot) AS prompt_count,
    CASE
        WHEN COUNT(cp.slot) = 8
             AND COUNT(DISTINCT cp.slot) = 8
        THEN 'COMPLETE'
        ELSE 'INCOMPLETE'
    END AS round_status
FROM crazy8_round c
LEFT JOIN crazy8_prompt cp
    ON cp.crazy8_id = c.crazy8_id
GROUP BY c.crazy8_id;

-- Verify that the SCAMPER concept has all seven operators.
SELECT
    ec.name AS existing_concept,
    COUNT(st.scamper_id) AS transformations,
    COUNT(DISTINCT st.operator) AS distinct_operators,
    CASE
        WHEN COUNT(DISTINCT st.operator) = 7
        THEN 'COMPLETE'
        ELSE 'INCOMPLETE'
    END AS scamper_status
FROM existing_concept ec
LEFT JOIN scamper_transformation st
    ON st.concept_id = ec.concept_id
GROUP BY ec.name;

-- Display the mind map as parent-child relationships.
SELECT
    parent.label AS parent_node,
    child.label AS child_node,
    child.relationship
FROM mind_map_node child
LEFT JOIN mind_map_node parent
    ON parent.node_id = child.parent_node_id
WHERE child.mind_map_id = 1
ORDER BY parent.label NULLS FIRST, child.label;

-- Reverse brainstorming makes the failure-to-countermeasure relationship
-- explicit instead of storing only the positive recommendation.
SELECT
    failure_description,
    countermeasure
FROM failure_mechanism
WHERE reverse_id = 1
ORDER BY failure_id;

-- Find ideas that combine high impact with reasonable feasibility.
SELECT
    t.technique_name,
    i.title,
    i.description,
    i.impact,
    i.feasibility,
    s.weighted_score
FROM idea_scored s
JOIN idea i
    ON i.idea_id = s.idea_id
JOIN technique t
    ON t.technique_id = i.technique_id
WHERE i.impact >= 5
  AND i.feasibility >= 4
ORDER BY s.weighted_score DESC;

-- ============================================================================
-- Transactional selection workflow
-- ============================================================================

BEGIN;

-- The selection stage is separate from generation. This reflects the
-- methodological rule that divergent ideation should not be prematurely
-- constrained by evaluation.
INSERT INTO idea_evaluation (
    idea_id,
    evaluator_name,
    evaluation_status,
    rationale,
    evaluated_at
)
SELECT
    s.idea_id,
    'Operations Review Board',
    CASE
        WHEN i.impact >= 5 AND i.feasibility >= 4
            THEN 'ACCEPTED'
        WHEN i.novelty >= 5
            THEN 'NEEDS_RESEARCH'
        ELSE 'REJECTED'
    END,
    CASE
        WHEN i.impact >= 5 AND i.feasibility >= 4
            THEN 'High-impact idea with practical implementation feasibility.'
        WHEN i.novelty >= 5
            THEN 'Novel direction requires evidence before selection.'
        ELSE 'Insufficient impact or feasibility for current constraints.'
    END,
    CURRENT_TIMESTAMP
FROM idea i
JOIN idea_scored s
    ON s.idea_id = i.idea_id
WHERE i.workshop_id = 1;

INSERT INTO selected_concept (
    workshop_id,
    idea_id,
    selection_reason
)
SELECT
    i.workshop_id,
    i.idea_id,
    'Accepted by the evaluation rule for high-impact and feasible concepts.'
FROM idea i
JOIN idea_evaluation e
    ON e.idea_id = i.idea_id
WHERE i.workshop_id = 1
  AND e.evaluation_status = 'ACCEPTED'
ON CONFLICT (workshop_id, idea_id) DO NOTHING;

UPDATE workshop
SET status = 'SELECTED'
WHERE workshop_id = 1;

COMMIT;

-- ============================================================================
-- Final governance-oriented selection report
-- ============================================================================

SELECT
    sc.selection_id,
    t.technique_name,
    i.title,
    i.description,
    s.weighted_score,
    sc.selection_reason
FROM selected_concept sc
JOIN idea i
    ON i.idea_id = sc.idea_id
JOIN technique t
    ON t.technique_id = i.technique_id
JOIN idea_scored s
    ON s.idea_id = i.idea_id
WHERE sc.workshop_id = 1
ORDER BY s.weighted_score DESC;

-- ============================================================================
-- Integrity demonstrations
-- ============================================================================

-- This statement would fail because scoring is restricted to 1 through 5.
-- It is intentionally left as a commented test so the complete script
-- remains executable without aborting.
--
-- INSERT INTO idea (
--     workshop_id,
--     technique_id,
--     title,
--     description,
--     impact
-- )
-- VALUES (
--     1,
--     1,
--     'Invalid score',
--     'This row violates the database scoring constraint.',
--     9
-- );

-- This statement would fail because the SCAMPER operator must be one of the
-- seven defined transformation types.
--
-- INSERT INTO scamper_transformation (
--     workshop_id,
--     concept_id,
--     operator,
--     description
-- )
-- VALUES (
--     1,
--     1,
--     'RANDOMIZE',
--     'Invalid SCAMPER operator.'
-- );

-- The foreign keys prevent an idea from referencing a nonexistent workshop,
-- technique, participant, or parent idea. The uniqueness rules prevent
-- duplicate SCAMPER operators for the same existing concept and duplicate
-- Crazy 8 slots inside one round.
