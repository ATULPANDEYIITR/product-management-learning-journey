DROP SCHEMA IF EXISTS product_vision CASCADE;
CREATE SCHEMA product_vision;

SET search_path TO product_vision, public;

CREATE TYPE vision_status AS ENUM (
    'draft',
    'validated',
    'approved',
    'active',
    'retired'
);

CREATE TYPE planning_horizon AS ENUM (
    '0-12 months',
    '1-3 years',
    '3-5 years'
);

CREATE TYPE evidence_type AS ENUM (
    'customer_interview',
    'pilot',
    'market_signal',
    'operational_data',
    'strategic_decision'
);

CREATE TABLE product (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_segment (
    segment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE customer_need (
    need_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    segment_id BIGINT NOT NULL
        REFERENCES customer_segment(segment_id)
        ON DELETE CASCADE,
    need TEXT NOT NULL,
    pain_point BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (segment_id, need)
);

CREATE TABLE product_vision (
    vision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES product(product_id)
        ON DELETE CASCADE,
    statement TEXT NOT NULL,
    customer_value TEXT NOT NULL,
    future_state TEXT NOT NULL,
    horizon planning_horizon NOT NULL,
    status vision_status NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(statement)) >= 30),
    CHECK (length(trim(customer_value)) >= 10),
    CHECK (length(trim(future_state)) >= 10),
    UNIQUE (product_id, version)
);

CREATE TABLE strategic_priority (
    priority_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE vision_priority (
    vision_id BIGINT NOT NULL
        REFERENCES product_vision(vision_id)
        ON DELETE CASCADE,
    priority_id BIGINT NOT NULL
        REFERENCES strategic_priority(priority_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (vision_id, priority_id)
);

CREATE TABLE vision_customer_segment (
    vision_id BIGINT NOT NULL
        REFERENCES product_vision(vision_id)
        ON DELETE CASCADE,
    segment_id BIGINT NOT NULL
        REFERENCES customer_segment(segment_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (vision_id, segment_id)
);

CREATE TABLE vision_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vision_id BIGINT NOT NULL
        REFERENCES product_vision(vision_id)
        ON DELETE CASCADE,
    evidence_type evidence_type NOT NULL,
    description TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(description)) >= 15)
);

CREATE TABLE vision_status_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vision_id BIGINT NOT NULL
        REFERENCES product_vision(vision_id)
        ON DELETE CASCADE,
    previous_status vision_status,
    new_status vision_status NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vision_evaluation (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vision_id BIGINT NOT NULL
        REFERENCES product_vision(vision_id)
        ON DELETE CASCADE,
    evaluator TEXT NOT NULL,
    customer_value_score NUMERIC(5,2) NOT NULL,
    strategic_alignment_score NUMERIC(5,2) NOT NULL,
    future_state_score NUMERIC(5,2) NOT NULL,
    evidence_score NUMERIC(5,2) NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (customer_value_score BETWEEN 0 AND 100),
    CHECK (strategic_alignment_score BETWEEN 0 AND 100),
    CHECK (future_state_score BETWEEN 0 AND 100),
    CHECK (evidence_score BETWEEN 0 AND 100)
);

CREATE INDEX idx_vision_product_status
    ON product_vision(product_id, status);

CREATE INDEX idx_vision_evidence_vision
    ON vision_evidence(vision_id);

CREATE INDEX idx_vision_history_vision
    ON vision_status_history(vision_id, changed_at DESC);

CREATE INDEX idx_vision_evaluation_vision
    ON vision_evaluation(vision_id, evaluated_at DESC);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_product_vision_updated_at
BEFORE UPDATE ON product_vision
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE FUNCTION enforce_vision_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'draft' AND NEW.status = 'validated')
        OR
        (OLD.status = 'validated' AND NEW.status = 'approved')
        OR
        (OLD.status = 'approved' AND NEW.status = 'active')
        OR
        (OLD.status = 'active' AND NEW.status = 'retired')
    ) THEN
        RAISE EXCEPTION
            'Invalid vision transition: % -> %',
            OLD.status,
            NEW.status;
    END IF;

    INSERT INTO vision_status_history (
        vision_id,
        previous_status,
        new_status
    )
    VALUES (
        OLD.vision_id,
        OLD.status,
        NEW.status
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_vision_status_transition
BEFORE UPDATE OF status ON product_vision
FOR EACH ROW
EXECUTE FUNCTION enforce_vision_status_transition();

CREATE OR REPLACE FUNCTION validate_vision_before_activation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    priority_count INTEGER;
    segment_count INTEGER;
    evidence_count INTEGER;
BEGIN
    IF NEW.status = 'active' AND OLD.status <> 'active' THEN
        SELECT count(*)
        INTO priority_count
        FROM vision_priority
        WHERE vision_id = NEW.vision_id;

        SELECT count(*)
        INTO segment_count
        FROM vision_customer_segment
        WHERE vision_id = NEW.vision_id;

        SELECT count(*)
        INTO evidence_count
        FROM vision_evidence
        WHERE vision_id = NEW.vision_id;

        IF priority_count = 0 THEN
            RAISE EXCEPTION
                'Active vision requires at least one strategic priority.';
        END IF;

        IF segment_count = 0 THEN
            RAISE EXCEPTION
                'Active vision requires at least one customer segment.';
        END IF;

        IF evidence_count = 0 THEN
            RAISE EXCEPTION
                'Active vision requires evidence.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_vision_activation
BEFORE UPDATE OF status ON product_vision
FOR EACH ROW
EXECUTE FUNCTION validate_vision_before_activation();

INSERT INTO product (name, description)
VALUES (
    'Operations Intelligence Platform',
    'A product focused on improving operational visibility and decision quality.'
);

INSERT INTO customer_segment (name, description)
VALUES
(
    'Operations teams',
    'Teams responsible for monitoring and coordinating operational work.'
),
(
    'Managers',
    'Leaders responsible for operational performance and decision quality.'
);

INSERT INTO customer_need (segment_id, need, pain_point)
SELECT segment_id, 'visibility', FALSE
FROM customer_segment
WHERE name = 'Operations teams';

INSERT INTO customer_need (segment_id, need, pain_point)
SELECT segment_id, 'decision delays', TRUE
FROM customer_segment
WHERE name = 'Operations teams';

INSERT INTO customer_need (segment_id, need, pain_point)
SELECT segment_id, 'predictability', FALSE
FROM customer_segment
WHERE name = 'Managers';

INSERT INTO customer_need (segment_id, need, pain_point)
SELECT segment_id, 'unclear priorities', TRUE
FROM customer_segment
WHERE name = 'Managers';

INSERT INTO strategic_priority (name, description)
VALUES
(
    'customer trust',
    'Improve confidence in operational information and decisions.'
),
(
    'operational efficiency',
    'Reduce avoidable delay and coordination effort.'
),
(
    'data-driven decisions',
    'Use reliable operational evidence for decision-making.'
),
(
    'scalable growth',
    'Create a direction that remains viable as adoption expands.'
);

INSERT INTO product_vision (
    product_id,
    statement,
    customer_value,
    future_state,
    horizon
)
SELECT
    product_id,
    'Enable operations teams to make faster, more reliable decisions from a unified understanding of operational conditions.',
    'Customers gain visibility, reduce decision delays, and improve operational reliability.',
    'Operations become measurable and predictable, allowing teams to identify problems early and coordinate action.',
    '1-3 years'
FROM product
WHERE name = 'Operations Intelligence Platform';

INSERT INTO vision_priority (vision_id, priority_id)
SELECT v.vision_id, p.priority_id
FROM product_vision v
CROSS JOIN strategic_priority p
WHERE p.name IN (
    'customer trust',
    'operational efficiency',
    'data-driven decisions',
    'scalable growth'
);

INSERT INTO vision_customer_segment (vision_id, segment_id)
SELECT v.vision_id, s.segment_id
FROM product_vision v
CROSS JOIN customer_segment s;

INSERT INTO vision_evidence (
    vision_id,
    evidence_type,
    description
)
SELECT
    vision_id,
    'customer_interview',
    'Customer interviews identify fragmented operational information.'
FROM product_vision;

INSERT INTO vision_evidence (
    vision_id,
    evidence_type,
    description
)
SELECT
    vision_id,
    'pilot',
    'Pilot users report delays caused by manual consolidation.'
FROM product_vision;

INSERT INTO vision_evidence (
    vision_id,
    evidence_type,
    description
)
SELECT
    vision_id,
    'operational_data',
    'Managers require consistent operational indicators.'
FROM product_vision;

UPDATE product_vision
SET status = 'validated'
WHERE version = 1;

UPDATE product_vision
SET status = 'approved'
WHERE status = 'validated';

UPDATE product_vision
SET status = 'active'
WHERE status = 'approved';

INSERT INTO vision_evaluation (
    vision_id,
    evaluator,
    customer_value_score,
    strategic_alignment_score,
    future_state_score,
    evidence_score
)
SELECT
    vision_id,
    'Product Strategy Council',
    88,
    92,
    90,
    85
FROM product_vision
WHERE status = 'active';

CREATE OR REPLACE VIEW active_vision_report AS
SELECT
    p.name AS product,
    v.version,
    v.status,
    v.horizon,
    v.statement,
    v.customer_value,
    v.future_state,
    count(DISTINCT vp.priority_id) AS strategic_priority_count,
    count(DISTINCT vcs.segment_id) AS customer_segment_count,
    count(DISTINCT ve.evidence_id) AS evidence_count,
    round(
        avg(
            (
                ev.customer_value_score +
                ev.strategic_alignment_score +
                ev.future_state_score +
                ev.evidence_score
            ) / 4.0
        ),
        2
    ) AS average_evaluation_score
FROM product_vision v
JOIN product p
    ON p.product_id = v.product_id
LEFT JOIN vision_priority vp
    ON vp.vision_id = v.vision_id
LEFT JOIN vision_customer_segment vcs
    ON vcs.vision_id = v.vision_id
LEFT JOIN vision_evidence ve
    ON ve.vision_id = v.vision_id
LEFT JOIN vision_evaluation ev
    ON ev.vision_id = v.vision_id
WHERE v.status = 'active'
GROUP BY
    p.name,
    v.version,
    v.status,
    v.horizon,
    v.statement,
    v.customer_value,
    v.future_state;

-- Retrieval and reporting.
SELECT *
FROM active_vision_report;

-- Strategic direction evaluation.
WITH priority_counts AS (
    SELECT
        v.vision_id,
        count(vp.priority_id) AS priority_count
    FROM product_vision v
    LEFT JOIN vision_priority vp
        ON vp.vision_id = v.vision_id
    WHERE v.status = 'active'
    GROUP BY v.vision_id
)
SELECT
    p.name,
    v.statement,
    pc.priority_count
FROM product_vision v
JOIN product p
    ON p.product_id = v.product_id
JOIN priority_counts pc
    ON pc.vision_id = v.vision_id;

-- Customer coverage validation.
SELECT
    p.name AS product,
    count(DISTINCT vcs.segment_id) AS covered_segments
FROM product_vision v
JOIN product p
    ON p.product_id = v.product_id
LEFT JOIN vision_customer_segment vcs
    ON vcs.vision_id = v.vision_id
GROUP BY p.name;

-- Evidence validation.
SELECT
    p.name AS product,
    count(ve.evidence_id) AS evidence_items,
    bool_and(length(trim(ve.description)) >= 15) AS evidence_valid
FROM product_vision v
JOIN product p
    ON p.product_id = v.product_id
LEFT JOIN vision_evidence ve
    ON ve.vision_id = v.vision_id
GROUP BY p.name;

-- Evaluation aggregation.
SELECT
    p.name AS product,
    round(avg(customer_value_score), 2) AS customer_value,
    round(avg(strategic_alignment_score), 2) AS strategic_alignment,
    round(avg(future_state_score), 2) AS future_state,
    round(avg(evidence_score), 2) AS evidence_quality
FROM vision_evaluation e
JOIN product_vision v
    ON v.vision_id = e.vision_id
JOIN product p
    ON p.product_id = v.product_id
GROUP BY p.name;

-- Workflow history.
SELECT
    p.name AS product,
    h.previous_status,
    h.new_status,
    h.changed_at
FROM vision_status_history h
JOIN product_vision v
    ON v.vision_id = h.vision_id
JOIN product p
    ON p.product_id = v.product_id
ORDER BY h.changed_at;

-- Transactional retirement demonstrates a controlled state change.
BEGIN;

UPDATE product_vision
SET status = 'retired'
WHERE status = 'active'
  AND version = 1;

COMMIT;

-- The state can be inspected after the transaction.
SELECT
    p.name,
    v.status,
    v.updated_at
FROM product_vision v
JOIN product p
    ON p.product_id = v.product_id;
