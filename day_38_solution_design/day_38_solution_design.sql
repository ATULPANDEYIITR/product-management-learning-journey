DROP SCHEMA IF EXISTS solution_design CASCADE;
CREATE SCHEMA solution_design;

SET search_path TO solution_design;

-- The relational model separates evidence about hypotheses from the
-- constraints that shape the solution and the alternatives evaluated against
-- those constraints.

CREATE TYPE hypothesis_status AS ENUM (
    'proposed',
    'validated',
    'rejected'
);

CREATE TYPE constraint_type AS ENUM (
    'functional',
    'non_functional',
    'technical',
    'business',
    'regulatory'
);

CREATE TYPE decision_status AS ENUM (
    'proposed',
    'selected',
    'rejected'
);

CREATE TABLE solution_case (
    solution_case_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    problem_statement TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hypothesis (
    hypothesis_id BIGSERIAL PRIMARY KEY,
    solution_case_id BIGINT NOT NULL
        REFERENCES solution_case(solution_case_id)
        ON DELETE CASCADE,
    code TEXT NOT NULL,
    statement TEXT NOT NULL,
    evidence_required TEXT NOT NULL,
    status hypothesis_status NOT NULL DEFAULT 'proposed',
    confidence NUMERIC(4,3) NOT NULL DEFAULT 0.500,
    CONSTRAINT uq_hypothesis_code
        UNIQUE (solution_case_id, code),
    CONSTRAINT ck_hypothesis_confidence
        CHECK (confidence BETWEEN 0 AND 1)
);

CREATE TABLE hypothesis_evidence (
    evidence_id BIGSERIAL PRIMARY KEY,
    hypothesis_id BIGINT NOT NULL
        REFERENCES hypothesis(hypothesis_id)
        ON DELETE CASCADE,
    observed_value NUMERIC(12,4) NOT NULL,
    required_value NUMERIC(12,4) NOT NULL,
    evidence_quality NUMERIC(4,3) NOT NULL,
    source_description TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_evidence_quality
        CHECK (evidence_quality BETWEEN 0 AND 1)
);

CREATE TABLE design_constraint (
    constraint_id BIGSERIAL PRIMARY KEY,
    solution_case_id BIGINT NOT NULL
        REFERENCES solution_case(solution_case_id)
        ON DELETE CASCADE,
    code TEXT NOT NULL,
    constraint_type constraint_type NOT NULL,
    description TEXT NOT NULL,
    is_hard BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (solution_case_id, code)
);

CREATE TABLE alternative (
    alternative_id BIGSERIAL PRIMARY KEY,
    solution_case_id BIGINT NOT NULL
        REFERENCES solution_case(solution_case_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    expected_value NUMERIC(8,3) NOT NULL,
    delivery_cost NUMERIC(8,3) NOT NULL,
    operating_cost NUMERIC(8,3) NOT NULL,
    implementation_risk NUMERIC(8,3) NOT NULL,
    scalability NUMERIC(8,3) NOT NULL,
    maintainability NUMERIC(8,3) NOT NULL,
    reversibility NUMERIC(8,3) NOT NULL,
    constraint_penalty NUMERIC(8,3) NOT NULL DEFAULT 0,
    UNIQUE (solution_case_id, name),
    CHECK (delivery_cost >= 0),
    CHECK (operating_cost >= 0),
    CHECK (implementation_risk >= 0),
    CHECK (scalability >= 0),
    CHECK (maintainability >= 0),
    CHECK (reversibility >= 0),
    CHECK (constraint_penalty >= 0)
);

CREATE TABLE alternative_constraint (
    alternative_id BIGINT NOT NULL
        REFERENCES alternative(alternative_id)
        ON DELETE CASCADE,
    constraint_id BIGINT NOT NULL
        REFERENCES design_constraint(constraint_id)
        ON DELETE CASCADE,
    satisfies BOOLEAN NOT NULL,
    rationale TEXT NOT NULL,
    PRIMARY KEY (alternative_id, constraint_id)
);

CREATE TABLE trade_off (
    trade_off_id BIGSERIAL PRIMARY KEY,
    solution_case_id BIGINT NOT NULL
        REFERENCES solution_case(solution_case_id)
        ON DELETE CASCADE,
    criterion TEXT NOT NULL,
    preferred_alternative_id BIGINT NOT NULL
        REFERENCES alternative(alternative_id),
    rationale TEXT NOT NULL
);

CREATE TABLE decision (
    decision_id BIGSERIAL PRIMARY KEY,
    solution_case_id BIGINT NOT NULL
        REFERENCES solution_case(solution_case_id)
        ON DELETE CASCADE,
    alternative_id BIGINT NOT NULL
        REFERENCES alternative(alternative_id),
    status decision_status NOT NULL,
    rationale TEXT NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hypothesis_case_status
    ON hypothesis(solution_case_id, status);

CREATE INDEX idx_alternative_case
    ON alternative(solution_case_id);

CREATE INDEX idx_constraint_case_type
    ON design_constraint(solution_case_id, constraint_type);

CREATE INDEX idx_evidence_hypothesis
    ON hypothesis_evidence(hypothesis_id);

INSERT INTO solution_case (
    name,
    problem_statement
)
VALUES (
    'Operational Event Intake',
    'Select an architecture for durable event ingestion under bursty traffic '
    || 'while balancing latency, cost, replay capability, and operational risk.'
);

INSERT INTO hypothesis (
    solution_case_id,
    code,
    statement,
    evidence_required,
    status,
    confidence
)
SELECT
    solution_case_id,
    'H-ASYNC',
    'Asynchronous processing absorbs traffic bursts without blocking clients.',
    'Load-test p95 latency and queue-depth measurements.',
    'validated',
    0.950
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO hypothesis (
    solution_case_id,
    code,
    statement,
    evidence_required,
    status,
    confidence
)
SELECT
    solution_case_id,
    'H-DURABLE',
    'Durable buffering preserves accepted events through consumer failures.',
    'Failure-injection and restart testing.',
    'validated',
    0.975
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO hypothesis (
    solution_case_id,
    code,
    statement,
    evidence_required,
    status,
    confidence
)
SELECT
    solution_case_id,
    'H-REPLAY',
    'Replay is valuable when downstream transformations change.',
    'Operational reprocessing evidence.',
    'validated',
    0.875
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO hypothesis_evidence (
    hypothesis_id,
    observed_value,
    required_value,
    evidence_quality,
    source_description
)
SELECT
    h.hypothesis_id,
    x.observed_value,
    x.required_value,
    x.evidence_quality,
    x.source_description
FROM hypothesis h
JOIN (
    VALUES
        ('H-ASYNC', 0.91::NUMERIC, 0.80::NUMERIC, 0.90::NUMERIC,
         'Load test showing p95 latency improvement during burst traffic'),
        ('H-DURABLE', 0.98::NUMERIC, 0.90::NUMERIC, 0.95::NUMERIC,
         'Consumer restart test showing durable message recovery'),
        ('H-REPLAY', 0.86::NUMERIC, 0.70::NUMERIC, 0.75::NUMERIC,
         'Historical reprocessing incident analysis')
) AS x(code, observed_value, required_value, evidence_quality, source_description)
ON h.code = x.code;

INSERT INTO design_constraint (
    solution_case_id,
    code,
    constraint_type,
    description,
    is_hard
)
SELECT solution_case_id, 'C-LATENCY', 'non_functional',
       'Client acknowledgement should normally remain below 300 ms.', TRUE
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO design_constraint (
    solution_case_id,
    code,
    constraint_type,
    description,
    is_hard
)
SELECT solution_case_id, 'C-DURABILITY', 'technical',
       'Accepted events must survive a consumer restart.', TRUE
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO design_constraint (
    solution_case_id,
    code,
    constraint_type,
    description,
    is_hard
)
SELECT solution_case_id, 'C-BUDGET', 'business',
       'Infrastructure and operating cost must remain moderate.', TRUE
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO design_constraint (
    solution_case_id,
    code,
    constraint_type,
    description,
    is_hard
)
SELECT solution_case_id, 'C-AUDIT', 'regulatory',
       'Processing outcomes must remain traceable.', TRUE
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO alternative (
    solution_case_id,
    name,
    description,
    expected_value,
    delivery_cost,
    operating_cost,
    implementation_risk,
    scalability,
    maintainability,
    reversibility,
    constraint_penalty
)
SELECT solution_case_id,
       'Direct synchronous API',
       'The request waits for downstream processing.',
       6, 2, 2, 2, 4, 7, 8, 3
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO alternative (
    solution_case_id,
    name,
    description,
    expected_value,
    delivery_cost,
    operating_cost,
    implementation_risk,
    scalability,
    maintainability,
    reversibility,
    constraint_penalty
)
SELECT solution_case_id,
       'Queue-backed asynchronous architecture',
       'The API accepts work while durable workers process messages independently.',
       9, 4, 4, 3, 8, 8, 8, 0
FROM solution_case
WHERE name = 'Operational Event Intake';

INSERT INTO alternative (
    solution_case_id,
    name,
    description,
    expected_value,
    delivery_cost,
    operating_cost,
    implementation_risk,
    scalability,
    maintainability,
    reversibility,
    constraint_penalty
)
SELECT solution_case_id,
       'Managed event-streaming architecture',
       'Partitioned durable streams provide high throughput and replay.',
       9.5, 7, 6, 5, 10, 6, 5, 1.5
FROM solution_case
WHERE name = 'Operational Event Intake';

-- The score is intentionally explicit so the decision remains inspectable.
-- It is not a universal optimization formula; changing business priorities
-- should change the weights or introduce a hard constraint.
CREATE VIEW alternative_scores AS
SELECT
    a.alternative_id,
    a.solution_case_id,
    a.name,
    ROUND(
        a.expected_value
        + 0.20 * a.scalability
        + 0.15 * a.maintainability
        + 0.10 * a.reversibility
        - 0.35 * a.implementation_risk
        - 0.15 * a.delivery_cost
        - 0.10 * a.operating_cost
        - a.constraint_penalty,
        3
    ) AS score
FROM alternative a;

-- Inspect the evidence before making a decision.
SELECT
    h.code,
    h.status,
    h.confidence,
    e.observed_value,
    e.required_value,
    e.evidence_quality
FROM hypothesis h
JOIN hypothesis_evidence e
    ON e.hypothesis_id = h.hypothesis_id
ORDER BY h.code;

-- Rank alternatives within the design case.
SELECT
    name,
    score,
    RANK() OVER (
        ORDER BY score DESC
    ) AS ranking
FROM alternative_scores
ORDER BY score DESC;

-- Identify hard constraints that an alternative does not satisfy.
SELECT
    a.name AS alternative,
    c.code AS constraint_code,
    c.description
FROM alternative a
JOIN alternative_constraint ac
    ON ac.alternative_id = a.alternative_id
JOIN design_constraint c
    ON c.constraint_id = ac.constraint_id
WHERE c.is_hard
  AND ac.satisfies = FALSE;

-- Register explicit alternative-to-constraint relationships.
INSERT INTO alternative_constraint (
    alternative_id,
    constraint_id,
    satisfies,
    rationale
)
SELECT
    a.alternative_id,
    c.constraint_id,
    CASE
        WHEN c.code = 'C-LATENCY'
             AND a.name = 'Direct synchronous API' THEN FALSE
        ELSE TRUE
    END,
    CASE
        WHEN c.code = 'C-LATENCY'
             AND a.name = 'Direct synchronous API'
            THEN 'Waiting for downstream work makes burst latency less predictable.'
        WHEN c.code = 'C-DURABILITY'
            THEN 'Durable buffering can preserve accepted work across consumer restarts.'
        WHEN c.code = 'C-AUDIT'
            THEN 'Processing events can be recorded independently of request completion.'
        ELSE 'The architecture can satisfy the constraint with appropriate configuration.'
    END
FROM alternative a
CROSS JOIN design_constraint c
WHERE a.solution_case_id = c.solution_case_id;

-- Re-run the hard-constraint query after inserting the relationships.
SELECT
    a.name AS alternative,
    c.code AS failed_constraint
FROM alternative a
JOIN alternative_constraint ac
    ON ac.alternative_id = a.alternative_id
JOIN design_constraint c
    ON c.constraint_id = ac.constraint_id
WHERE c.is_hard
  AND NOT ac.satisfies;

-- Record explicit trade-offs rather than hiding them inside a score.
INSERT INTO trade_off (
    solution_case_id,
    criterion,
    preferred_alternative_id,
    rationale
)
SELECT
    s.solution_case_id,
    x.criterion,
    a.alternative_id,
    x.rationale
FROM solution_case s
JOIN alternative a
    ON a.solution_case_id = s.solution_case_id
JOIN (
    VALUES
        (
            'Latency',
            'Queue-backed asynchronous architecture',
            'Client acknowledgement is decoupled from downstream processing.'
        ),
        (
            'Operational simplicity',
            'Direct synchronous API',
            'Fewer infrastructure components make the initial system simpler.'
        ),
        (
            'Replay capability',
            'Managed event-streaming architecture',
            'Partitioned durable streams support high-throughput historical replay.'
        )
) AS x(criterion, alternative_name, rationale)
ON a.name = x.alternative_name
WHERE s.name = 'Operational Event Intake';

-- A transaction protects the decision record from partial updates.
BEGIN;

WITH ranked AS (
    SELECT
        alternative_id,
        solution_case_id,
        name,
        score,
        ROW_NUMBER() OVER (
            PARTITION BY solution_case_id
            ORDER BY score DESC
        ) AS position
    FROM alternative_scores
)
INSERT INTO decision (
    solution_case_id,
    alternative_id,
    status,
    rationale
)
SELECT
    solution_case_id,
    alternative_id,
    CASE
        WHEN position = 1 THEN 'selected'::decision_status
        ELSE 'rejected'::decision_status
    END,
    CASE
        WHEN position = 1
            THEN 'Highest weighted score among the evaluated alternatives.'
        ELSE 'Not selected after comparing value, risk, cost, and constraints.'
    END
FROM ranked;

COMMIT;

-- The final decision is auditable because the score, hypotheses, constraints,
-- alternatives, and explicit trade-offs remain separate records.
SELECT
    s.name AS solution_case,
    a.name AS alternative,
    d.status,
    d.rationale,
    d.decided_at
FROM decision d
JOIN solution_case s
    ON s.solution_case_id = d.solution_case_id
JOIN alternative a
    ON a.alternative_id = d.alternative_id
ORDER BY
    s.name,
    d.status DESC,
    a.name;
