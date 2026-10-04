-- Product Discovery Sprint
-- PostgreSQL 15+ compatible
--
-- This schema models discovery as a traceable evidence system:
-- research questions -> evidence -> themes -> opportunities -> concepts ->
-- experiments -> measured results -> discovery decisions.
--
-- Constraints are used where the database can reliably protect integrity.
-- Subjective research interpretation remains in application/research workflow.

DROP SCHEMA IF EXISTS product_discovery CASCADE;
CREATE SCHEMA product_discovery;

SET search_path TO product_discovery;

CREATE TYPE evidence_type AS ENUM (
    'interview',
    'observation',
    'survey',
    'analytics',
    'support',
    'experiment'
);

CREATE TYPE experiment_type AS ENUM (
    'concept_test',
    'prototype',
    'usability',
    'fake_door'
);

CREATE TYPE decision_type AS ENUM (
    'continue',
    'iterate',
    'stop'
);

CREATE TYPE assumption_type AS ENUM (
    'desirability',
    'behavior',
    'feasibility',
    'business'
);

CREATE TABLE discovery_sprints (
    sprint_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    product_area TEXT NOT NULL,
    target_segment TEXT NOT NULL,
    business_outcome TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CHECK (end_date >= start_date)
);

CREATE TABLE research_questions (
    question_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES discovery_sprints(sprint_id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    CHECK (status IN ('open', 'answered', 'partially_answered')),
    UNIQUE (sprint_id, question)
);

CREATE TABLE participants (
    participant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_code TEXT NOT NULL UNIQUE,
    segment TEXT NOT NULL,
    role_name TEXT NOT NULL,
    research_context TEXT NOT NULL
);

CREATE TABLE research_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES discovery_sprints(sprint_id) ON DELETE CASCADE,
    question_id BIGINT REFERENCES research_questions(question_id) ON DELETE SET NULL,
    participant_id BIGINT REFERENCES participants(participant_id) ON DELETE SET NULL,
    source_reference TEXT NOT NULL,
    evidence_type evidence_type NOT NULL,
    statement TEXT NOT NULL,
    severity NUMERIC(5,4) NOT NULL CHECK (severity BETWEEN 0 AND 1),
    frequency INTEGER NOT NULL CHECK (frequency > 0),
    confidence NUMERIC(5,4) NOT NULL DEFAULT 0.75
        CHECK (confidence BETWEEN 0 AND 1),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence_tags (
    evidence_id BIGINT NOT NULL REFERENCES research_evidence(evidence_id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (evidence_id, tag)
);

CREATE TABLE themes (
    theme_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES discovery_sprints(sprint_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    user_impact NUMERIC(5,2) NOT NULL CHECK (user_impact BETWEEN 0 AND 10),
    frequency_score NUMERIC(5,2) NOT NULL CHECK (frequency_score BETWEEN 0 AND 10),
    strategic_fit NUMERIC(5,2) NOT NULL CHECK (strategic_fit BETWEEN 0 AND 10),
    UNIQUE (sprint_id, name)
);

CREATE TABLE theme_evidence (
    theme_id BIGINT NOT NULL REFERENCES themes(theme_id) ON DELETE CASCADE,
    evidence_id BIGINT NOT NULL REFERENCES research_evidence(evidence_id) ON DELETE RESTRICT,
    PRIMARY KEY (theme_id, evidence_id)
);

CREATE TABLE opportunities (
    opportunity_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    theme_id BIGINT NOT NULL REFERENCES themes(theme_id) ON DELETE RESTRICT,
    statement TEXT NOT NULL,
    target_behavior TEXT NOT NULL,
    evidence_strength NUMERIC(5,2) NOT NULL CHECK (evidence_strength BETWEEN 0 AND 10),
    business_value NUMERIC(5,2) NOT NULL CHECK (business_value BETWEEN 0 AND 10),
    feasibility NUMERIC(5,2) NOT NULL CHECK (feasibility BETWEEN 0 AND 10)
);

CREATE TABLE concepts (
    concept_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    opportunity_id BIGINT NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    mechanism TEXT NOT NULL,
    expected_behavior_change TEXT NOT NULL,
    confidence NUMERIC(5,4) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    effort NUMERIC(6,2) NOT NULL CHECK (effort > 0),
    reach_score NUMERIC(5,2) NOT NULL CHECK (reach_score BETWEEN 0 AND 10)
);

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    concept_id BIGINT NOT NULL REFERENCES concepts(concept_id) ON DELETE RESTRICT,
    experiment_type experiment_type NOT NULL,
    metric_name TEXT NOT NULL,
    participants INTEGER NOT NULL CHECK (participants >= 5),
    baseline_rate NUMERIC(7,5) NOT NULL CHECK (baseline_rate BETWEEN 0 AND 1),
    threshold_rate NUMERIC(7,5) NOT NULL CHECK (threshold_rate BETWEEN 0 AND 1),
    qualitative_threshold NUMERIC(7,5) NOT NULL
        CHECK (qualitative_threshold BETWEEN 0 AND 1),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE TABLE experiment_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL UNIQUE
        REFERENCES experiments(experiment_id) ON DELETE CASCADE,
    observed_rate NUMERIC(7,5) NOT NULL CHECK (observed_rate BETWEEN 0 AND 1),
    qualitative_signal NUMERIC(7,5) NOT NULL
        CHECK (qualitative_signal BETWEEN 0 AND 1),
    decision decision_type NOT NULL,
    interpretation TEXT NOT NULL
);

CREATE TABLE assumptions (
    assumption_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sprint_id BIGINT NOT NULL REFERENCES discovery_sprints(sprint_id) ON DELETE CASCADE,
    statement TEXT NOT NULL,
    assumption_type assumption_type NOT NULL,
    importance NUMERIC(7,5) NOT NULL CHECK (importance BETWEEN 0 AND 1),
    uncertainty NUMERIC(7,5) NOT NULL CHECK (uncertainty BETWEEN 0 AND 1),
    evidence_level NUMERIC(7,5) NOT NULL CHECK (evidence_level BETWEEN 0 AND 1)
);

CREATE INDEX idx_questions_sprint
    ON research_questions(sprint_id);

CREATE INDEX idx_evidence_sprint_type
    ON research_evidence(sprint_id, evidence_type);

CREATE INDEX idx_evidence_participant
    ON research_evidence(participant_id);

CREATE INDEX idx_evidence_capture_time
    ON research_evidence(captured_at);

CREATE INDEX idx_evidence_tags_tag
    ON evidence_tags(tag);

CREATE INDEX idx_theme_evidence_evidence
    ON theme_evidence(evidence_id);

CREATE INDEX idx_opportunities_theme
    ON opportunities(theme_id);

CREATE INDEX idx_concepts_opportunity
    ON concepts(opportunity_id);

CREATE INDEX idx_experiments_concept
    ON experiments(concept_id);

CREATE INDEX idx_assumptions_sprint
    ON assumptions(sprint_id);

INSERT INTO discovery_sprints (
    name,
    product_area,
    target_segment,
    business_outcome,
    start_date,
    end_date
)
VALUES (
    'Supplier Discovery Sprint',
    'B2B supplier discovery',
    'Procurement managers at mid-sized manufacturers',
    'Reduce supplier comparison effort while preserving qualification confidence',
    DATE '2026-10-05',
    DATE '2026-10-16'
);

INSERT INTO research_questions (sprint_id, question)
SELECT sprint_id,
       question
FROM discovery_sprints,
LATERAL (
    VALUES
        ('Where does supplier discovery create unnecessary manual work?'),
        ('What evidence is required before a supplier can be trusted?'),
        ('Which workarounds reveal meaningful unmet needs?'),
        ('What behavior would indicate that a proposed intervention is valuable?')
) AS questions(question);

INSERT INTO participants (
    external_code,
    segment,
    role_name,
    research_context
)
VALUES
(
    'P-001',
    'strategic procurement',
    'procurement manager',
    'high-value supplier comparisons'
),
(
    'P-002',
    'operational procurement',
    'buyer',
    'urgent recurring purchases'
),
(
    'P-003',
    'strategic procurement',
    'category manager',
    'supplier qualification'
),
(
    'P-004',
    'operational procurement',
    'senior buyer',
    'spreadsheet-based comparison'
),
(
    'P-005',
    'strategic procurement',
    'procurement lead',
    'shortlist review'
);

WITH sprint AS (
    SELECT sprint_id
    FROM discovery_sprints
    WHERE name = 'Supplier Discovery Sprint'
),
questions AS (
    SELECT question_id, question
    FROM research_questions
)
INSERT INTO research_evidence (
    sprint_id,
    question_id,
    participant_id,
    source_reference,
    evidence_type,
    statement,
    severity,
    frequency,
    confidence
)
SELECT
    sprint.sprint_id,
    questions.question_id,
    participants.participant_id,
    data.source_reference,
    data.evidence_type::evidence_type,
    data.statement,
    data.severity,
    data.frequency,
    data.confidence
FROM sprint
CROSS JOIN (
    VALUES
    (
        'Where does supplier discovery create unnecessary manual work?',
        'INT-001',
        'P-001',
        'interview',
        'I copy supplier lead time, MOQ, certification, and price into my own spreadsheet.',
        0.90, 5, 0.92
    ),
    (
        'Where does supplier discovery create unnecessary manual work?',
        'OBS-001',
        'P-001',
        'observation',
        'Buyer opens multiple supplier pages and manually transfers attributes into a comparison sheet.',
        0.93, 4, 0.95
    ),
    (
        'What evidence is required before a supplier can be trusted?',
        'INT-002',
        'P-002',
        'interview',
        'Urgent requests cause me to reuse known suppliers because verification takes too long.',
        0.84, 4, 0.88
    ),
    (
        'What evidence is required before a supplier can be trusted?',
        'INT-003',
        'P-003',
        'interview',
        'A lower price does not matter when the required certification cannot be verified.',
        0.95, 3, 0.96
    ),
    (
        'What evidence is required before a supplier can be trusted?',
        'SUP-2026-09',
        NULL,
        'support',
        'Support requests repeatedly ask where supplier qualification evidence is stored.',
        0.72, 18, 0.78
    ),
    (
        'Which workarounds reveal meaningful unmet needs?',
        'INT-004',
        'P-004',
        'interview',
        'I maintain a personal spreadsheet because supplier pages do not preserve my comparison context.',
        0.83, 5, 0.90
    ),
    (
        'Which workarounds reveal meaningful unmet needs?',
        'INT-005',
        'P-005',
        'interview',
        'I return shortlists when the evidence behind supplier recommendations is unclear.',
        0.86, 3, 0.91
    ),
    (
        'What behavior would indicate that a proposed intervention is valuable?',
        'AN-2026-Q3',
        NULL,
        'analytics',
        'Supplier detail pages receive repeat visits but have low shortlist conversion.',
        0.70, 1, 0.75
    )
) AS data(question_text, source_reference, participant_code, evidence_type,
          statement, severity, frequency, confidence)
JOIN questions
    ON questions.question = data.question_text
LEFT JOIN participants
    ON participants.external_code = data.participant_code;

INSERT INTO evidence_tags (evidence_id, tag)
SELECT evidence_id, tag
FROM research_evidence
CROSS JOIN LATERAL (
    SELECT UNNEST(
        CASE
            WHEN source_reference IN ('INT-001', 'OBS-001', 'INT-004')
                THEN ARRAY['comparison', 'manual_work', 'spreadsheet']
            WHEN source_reference IN ('INT-002', 'INT-003', 'SUP-2026-09')
                THEN ARRAY['qualification', 'trust', 'evidence']
            WHEN source_reference = 'INT-005'
                THEN ARRAY['shortlist', 'evidence', 'review']
            ELSE ARRAY['discovery', 'shortlist']
        END
    )
) AS tags(tag);

INSERT INTO themes (
    sprint_id,
    name,
    description,
    user_impact,
    frequency_score,
    strategic_fit
)
SELECT
    sprint_id,
    'Manual comparison burden',
    'Buyers reconstruct comparable supplier information in spreadsheets and other personal artifacts.',
    8.9,
    8.4,
    8.7
FROM discovery_sprints
WHERE name = 'Supplier Discovery Sprint';

INSERT INTO themes (
    sprint_id,
    name,
    description,
    user_impact,
    frequency_score,
    strategic_fit
)
SELECT
    sprint_id,
    'Qualification evidence gap',
    'Supplier qualification evidence is fragmented enough to slow trust decisions.',
    9.4,
    8.2,
    9.3
FROM discovery_sprints
WHERE name = 'Supplier Discovery Sprint';

INSERT INTO themes (
    sprint_id,
    name,
    description,
    user_impact,
    frequency_score,
    strategic_fit
)
SELECT
    sprint_id,
    'Shortlist verification friction',
    'Decision makers cannot efficiently verify the evidence behind a supplier shortlist.',
    8.7,
    7.7,
    9.0
FROM discovery_sprints
WHERE name = 'Supplier Discovery Sprint';

INSERT INTO theme_evidence (theme_id, evidence_id)
SELECT
    themes.theme_id,
    evidence.evidence_id
FROM themes
JOIN research_evidence evidence
    ON (
        themes.name = 'Manual comparison burden'
        AND evidence.source_reference IN ('INT-001', 'OBS-001', 'INT-004')
    )
    OR (
        themes.name = 'Qualification evidence gap'
        AND evidence.source_reference IN ('INT-002', 'INT-003', 'SUP-2026-09')
    )
    OR (
        themes.name = 'Shortlist verification friction'
        AND evidence.source_reference IN ('INT-005', 'AN-2026-Q3')
    )
WHERE themes.sprint_id = (
    SELECT sprint_id
    FROM discovery_sprints
    WHERE name = 'Supplier Discovery Sprint'
);

INSERT INTO opportunities (
    theme_id,
    statement,
    target_behavior,
    evidence_strength,
    business_value,
    feasibility
)
SELECT
    theme_id,
    'Procurement managers need comparable supplier evidence without manually reconstructing equivalent fields.',
    'Complete supplier comparisons using normalized evidence.',
    8.8,
    8.9,
    7.8
FROM themes
WHERE name = 'Manual comparison burden';

INSERT INTO opportunities (
    theme_id,
    statement,
    target_behavior,
    evidence_strength,
    business_value,
    feasibility
)
SELECT
    theme_id,
    'Procurement managers need qualification evidence attached to supplier decisions so that alternatives can be evaluated without restarting verification.',
    'Verify qualification evidence before shortlisting a supplier.',
    9.2,
    9.1,
    7.0
FROM themes
WHERE name = 'Qualification evidence gap';

INSERT INTO opportunities (
    theme_id,
    statement,
    target_behavior,
    evidence_strength,
    business_value,
    feasibility
)
SELECT
    theme_id,
    'Procurement leads need shortlist decisions to expose their supporting evidence so review does not restart the research process.',
    'Review supplier shortlist decisions through traceable evidence.',
    8.7,
    8.9,
    7.4
FROM themes
WHERE name = 'Shortlist verification friction';

INSERT INTO concepts (
    opportunity_id,
    name,
    mechanism,
    expected_behavior_change,
    confidence,
    effort,
    reach_score
)
SELECT
    opportunity_id,
    'Evidence comparison workspace',
    'Normalize supplier attributes into a comparison matrix and preserve source evidence beside each field.',
    'Buyer completes supplier comparison without repeatedly switching between supplier pages.',
    0.82,
    5.0,
    8.5
FROM opportunities
WHERE statement LIKE 'Procurement managers need comparable supplier evidence%';

INSERT INTO concepts (
    opportunity_id,
    name,
    mechanism,
    expected_behavior_change,
    confidence,
    effort,
    reach_score
)
SELECT
    opportunity_id,
    'Qualification evidence ledger',
    'Represent qualification claims with source, verification state, and evidence freshness.',
    'Buyer verifies supplier eligibility without searching separate documents.',
    0.76,
    6.0,
    8.0
FROM opportunities
WHERE statement LIKE 'Procurement managers need qualification evidence%';

INSERT INTO concepts (
    opportunity_id,
    name,
    mechanism,
    expected_behavior_change,
    confidence,
    effort,
    reach_score
)
SELECT
    opportunity_id,
    'Decision evidence packet',
    'Expose the evidence supporting every supplier recommendation in a review-ready structure.',
    'Procurement lead verifies shortlist rationale without repeating the research.',
    0.80,
    4.0,
    8.1
FROM opportunities
WHERE statement LIKE 'Procurement leads need shortlist decisions%';

INSERT INTO experiments (
    concept_id,
    experiment_type,
    metric_name,
    participants,
    baseline_rate,
    threshold_rate,
    qualitative_threshold
)
SELECT
    concept_id,
    'usability',
    'supplier comparison task completion',
    8,
    0.45,
    0.75,
    0.65
FROM concepts
WHERE name = 'Evidence comparison workspace';

INSERT INTO experiments (
    concept_id,
    experiment_type,
    metric_name,
    participants,
    baseline_rate,
    threshold_rate,
    qualitative_threshold
)
SELECT
    concept_id,
    'prototype',
    'qualification verification task completion',
    8,
    0.50,
    0.75,
    0.65
FROM concepts
WHERE name = 'Qualification evidence ledger';

INSERT INTO experiments (
    concept_id,
    experiment_type,
    metric_name,
    participants,
    baseline_rate,
    threshold_rate,
    qualitative_threshold
)
SELECT
    concept_id,
    'usability',
    'shortlist rationale verification completion',
    8,
    0.35,
    0.70,
    0.65
FROM concepts
WHERE name = 'Decision evidence packet';

INSERT INTO experiment_results (
    experiment_id,
    observed_rate,
    qualitative_signal,
    decision,
    interpretation
)
SELECT
    experiment_id,
    0.875,
    0.84,
    'continue',
    'Both behavioral completion and qualitative evidence cleared the validation thresholds.'
FROM experiments
WHERE metric_name = 'supplier comparison task completion';

INSERT INTO experiment_results (
    experiment_id,
    observed_rate,
    qualitative_signal,
    decision,
    interpretation
)
SELECT
    experiment_id,
    0.625,
    0.71,
    'iterate',
    'The qualitative signal is meaningful, but the observed verification completion rate remains below the quantitative threshold.'
FROM experiments
WHERE metric_name = 'qualification verification task completion';

INSERT INTO experiment_results (
    experiment_id,
    observed_rate,
    qualitative_signal,
    decision,
    interpretation
)
SELECT
    experiment_id,
    0.75,
    0.68,
    'continue',
    'Reviewers could verify shortlist rationale at the required behavioral rate and the qualitative signal cleared the policy threshold.'
FROM experiments
WHERE metric_name = 'shortlist rationale verification completion';

INSERT INTO assumptions (
    sprint_id,
    statement,
    assumption_type,
    importance,
    uncertainty,
    evidence_level
)
SELECT
    sprint_id,
    'Procurement managers will trust normalized supplier attributes only when important fields retain visible evidence provenance.',
    'desirability',
    0.95,
    0.75,
    0.65
FROM discovery_sprints
WHERE name = 'Supplier Discovery Sprint';

INSERT INTO assumptions (
    sprint_id,
    statement,
    assumption_type,
    importance,
    uncertainty,
    evidence_level
)
SELECT
    sprint_id,
    'Reducing comparison effort will cause buyers to evaluate more qualified alternatives rather than merely completing the existing workflow faster.',
    'behavior',
    0.88,
    0.80,
    0.35
FROM discovery_sprints
WHERE name = 'Supplier Discovery Sprint';

INSERT INTO assumptions (
    sprint_id,
    statement,
    assumption_type,
    importance,
    uncertainty,
    evidence_level
)
SELECT
    sprint_id,
    'Supplier qualification evidence can remain sufficiently current to support decisions.',
    'feasibility',
    0.92,
    0.85,
    0.30
FROM discovery_sprints
WHERE name = 'Supplier Discovery Sprint';

CREATE VIEW evidence_signal_view AS
SELECT
    e.evidence_id,
    e.source_reference,
    e.evidence_type,
    e.statement,
    e.severity,
    e.frequency,
    e.confidence,
    ROUND(
        (
            e.severity
            * LN(1 + e.frequency)
            * e.confidence
        )::numeric,
        3
    ) AS evidence_signal
FROM research_evidence e;

CREATE VIEW theme_priority_view AS
SELECT
    t.theme_id,
    t.name,
    t.description,
    COUNT(te.evidence_id) AS evidence_count,
    ROUND(
        (
            t.user_impact * 0.40
            + t.frequency_score * 0.30
            + t.strategic_fit * 0.30
        )::numeric,
        2
    ) AS priority_score
FROM themes t
LEFT JOIN theme_evidence te
    ON te.theme_id = t.theme_id
GROUP BY
    t.theme_id,
    t.name,
    t.description,
    t.user_impact,
    t.frequency_score,
    t.strategic_fit;

CREATE VIEW opportunity_priority_view AS
SELECT
    o.opportunity_id,
    t.name AS theme,
    o.statement,
    o.target_behavior,
    ROUND(
        (
            o.evidence_strength * 0.40
            + o.business_value * 0.35
            + o.feasibility * 0.25
        )::numeric,
        2
    ) AS opportunity_score
FROM opportunities o
JOIN themes t
    ON t.theme_id = o.theme_id;

CREATE VIEW concept_priority_view AS
SELECT
    c.concept_id,
    c.name,
    o.statement AS opportunity_statement,
    ROUND(
        (
            c.confidence * c.reach_score
            / NULLIF(c.effort, 0)
        )::numeric,
        2
    ) AS concept_score
FROM concepts c
JOIN opportunities o
    ON o.opportunity_id = c.opportunity_id;

CREATE VIEW validation_view AS
SELECT
    e.experiment_id,
    c.name AS concept,
    e.metric_name,
    e.participants,
    e.baseline_rate,
    r.observed_rate,
    e.threshold_rate,
    e.qualitative_threshold,
    r.qualitative_signal,
    r.decision,
    CASE
        WHEN e.baseline_rate = 0 THEN NULL
        ELSE ROUND(
            (
                (r.observed_rate - e.baseline_rate)
                / e.baseline_rate
            )::numeric,
            4
        )
    END AS relative_lift,
    r.interpretation
FROM experiments e
JOIN concepts c
    ON c.concept_id = e.concept_id
JOIN experiment_results r
    ON r.experiment_id = e.experiment_id;

CREATE VIEW assumption_risk_view AS
SELECT
    assumption_id,
    statement,
    assumption_type,
    ROUND(
        (
            importance
            * uncertainty
            * (1 - evidence_level)
        )::numeric,
        4
    ) AS risk_score
FROM assumptions;

-- Research synthesis query: identify high-signal evidence.
SELECT
    evidence_id,
    evidence_type,
    source_reference,
    ROUND(evidence_signal, 3) AS signal,
    statement
FROM evidence_signal_view
ORDER BY evidence_signal DESC;

-- Theme synthesis query: themes are ranked using impact, frequency,
-- and strategic fit rather than raw evidence count alone.
SELECT
    theme_id,
    name,
    evidence_count,
    priority_score
FROM theme_priority_view
ORDER BY priority_score DESC;

-- Opportunity query: separate the problem space from solution concepts.
SELECT
    opportunity_id,
    theme,
    ROUND(opportunity_score, 2) AS score,
    statement,
    target_behavior
FROM opportunity_priority_view
ORDER BY opportunity_score DESC;

-- Concept query: effort is explicitly penalized so an expensive concept
-- does not automatically outrank a smaller validation candidate.
SELECT
    concept_id,
    name,
    ROUND(concept_score, 2) AS score
FROM concept_priority_view
ORDER BY concept_score DESC;

-- Validation query: observed behavior, threshold, qualitative signal,
-- and decision remain visible together.
SELECT
    experiment_id,
    concept,
    metric_name,
    participants,
    ROUND(observed_rate * 100, 1) AS observed_percent,
    ROUND(threshold_rate * 100, 1) AS threshold_percent,
    ROUND(qualitative_signal * 100, 1) AS qualitative_percent,
    decision,
    relative_lift,
    interpretation
FROM validation_view
ORDER BY
    CASE decision
        WHEN 'continue' THEN 1
        WHEN 'iterate' THEN 2
        WHEN 'stop' THEN 3
    END,
    observed_rate DESC;

-- Assumption query: uncertainty without importance should not determine
-- research priority. The combined risk score exposes assumptions that
-- could invalidate a product direction.
SELECT
    assumption_id,
    assumption_type,
    ROUND(risk_score, 4) AS risk_score,
    statement
FROM assumption_risk_view
ORDER BY risk_score DESC;

-- Evidence-to-theme traceability query.
SELECT
    t.name AS theme,
    e.source_reference,
    e.evidence_type,
    e.statement
FROM theme_evidence te
JOIN themes t
    ON t.theme_id = te.theme_id
JOIN research_evidence e
    ON e.evidence_id = te.evidence_id
ORDER BY t.name, e.source_reference;

-- Opportunity-to-concept traceability query.
SELECT
    o.opportunity_id,
    o.statement AS opportunity,
    c.concept_id,
    c.name AS concept,
    c.mechanism
FROM opportunities o
JOIN concepts c
    ON c.opportunity_id = o.opportunity_id
ORDER BY o.opportunity_id, c.concept_id;

-- Demonstrate database-level transaction behavior with a deliberately
-- invalid experiment that is rolled back. The CHECK constraint prevents
-- an impossible negative participant count from being persisted.
BEGIN;

SAVEPOINT invalid_experiment_attempt;

DO $$
BEGIN
    BEGIN
        INSERT INTO experiments (
            concept_id,
            experiment_type,
            metric_name,
            participants,
            baseline_rate,
            threshold_rate,
            qualitative_threshold
        )
        SELECT
            concept_id,
            'prototype',
            'invalid negative participant test',
            -2,
            0.40,
            0.70,
            0.65
        FROM concepts
        WHERE name = 'Evidence comparison workspace';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Invalid experiment rejected by database constraint.';
    END;
END;
$$;

ROLLBACK TO SAVEPOINT invalid_experiment_attempt;
COMMIT;

-- Final integrity check: all themes should have supporting evidence.
SELECT
    t.theme_id,
    t.name,
    COUNT(te.evidence_id) AS supporting_evidence
FROM themes t
LEFT JOIN theme_evidence te
    ON te.theme_id = t.theme_id
GROUP BY t.theme_id, t.name
HAVING COUNT(te.evidence_id) = 0;

-- Final validation integrity check: completed experiments should have
-- exactly one result row.
SELECT
    e.experiment_id,
    e.metric_name
FROM experiments e
LEFT JOIN experiment_results r
    ON r.experiment_id = e.experiment_id
GROUP BY e.experiment_id, e.metric_name
HAVING COUNT(r.result_id) <> 1;
