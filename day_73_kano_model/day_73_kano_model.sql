-- ============================================================
-- KANO MODEL: CUSTOMER NEEDS AND SATISFACTION MANAGEMENT
-- PostgreSQL 15+
--
-- Models:
-- 1. Customer requirements and product features
-- 2. Functional and dysfunctional questionnaire responses
-- 3. Kano classification
-- 4. Satisfaction and dissatisfaction coefficients
-- 5. Feature prioritization
-- 6. Feature lifecycle and decision records
-- 7. Customer survey validation and reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS kano;

SET search_path TO kano, public;

-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

CREATE TYPE response_option AS ENUM (
    'like',
    'expect',
    'neutral',
    'tolerate',
    'dislike'
);

CREATE TYPE kano_category AS ENUM (
    'must_be',
    'performance',
    'attractive',
    'indifferent',
    'reverse',
    'questionable'
);

CREATE TYPE feature_status AS ENUM (
    'proposed',
    'under_research',
    'approved',
    'in_development',
    'released',
    'rejected'
);

CREATE TYPE decision_type AS ENUM (
    'prioritize',
    'defer',
    'reject',
    'investigate'
);

-- ------------------------------------------------------------
-- CUSTOMERS
-- ------------------------------------------------------------

CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_reference VARCHAR(100) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    customer_segment VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT customer_name_not_empty
        CHECK (length(trim(customer_name)) > 0)
);

-- ------------------------------------------------------------
-- PRODUCTS
-- ------------------------------------------------------------

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT product_name_not_empty
        CHECK (length(trim(product_name)) > 0)
);

-- ------------------------------------------------------------
-- PRODUCT FEATURES
-- ------------------------------------------------------------

CREATE TABLE features (
    feature_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    feature_code VARCHAR(30) NOT NULL UNIQUE,
    feature_name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    status feature_status NOT NULL DEFAULT 'proposed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT feature_name_not_empty
        CHECK (length(trim(feature_name)) > 0)
);

CREATE INDEX idx_features_product
    ON features(product_id);

CREATE INDEX idx_features_status
    ON features(status);

-- ------------------------------------------------------------
-- SURVEYS
-- ------------------------------------------------------------

CREATE TABLE surveys (
    survey_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    survey_name VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT survey_date_check
        CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_surveys_product
    ON surveys(product_id);

-- ------------------------------------------------------------
-- KANO QUESTIONNAIRE RESPONSES
-- ------------------------------------------------------------

CREATE TABLE kano_responses (
    response_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    survey_id BIGINT NOT NULL REFERENCES surveys(survey_id),
    feature_id BIGINT NOT NULL REFERENCES features(feature_id),
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),

    functional_response response_option NOT NULL,
    dysfunctional_response response_option NOT NULL,

    classification kano_category NOT NULL,

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_customer_feature_survey
        UNIQUE (survey_id, feature_id, customer_id)
);

CREATE INDEX idx_kano_responses_feature
    ON kano_responses(feature_id);

CREATE INDEX idx_kano_responses_classification
    ON kano_responses(classification);

CREATE INDEX idx_kano_responses_survey
    ON kano_responses(survey_id, feature_id);

-- ------------------------------------------------------------
-- KANO CLASSIFICATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION classify_kano(
    p_functional response_option,
    p_dysfunctional response_option
)
RETURNS kano_category
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE p_functional
        WHEN 'like' THEN
            CASE p_dysfunctional
                WHEN 'like' THEN 'questionable'::kano_category
                WHEN 'expect' THEN 'reverse'::kano_category
                WHEN 'neutral' THEN 'reverse'::kano_category
                WHEN 'tolerate' THEN 'reverse'::kano_category
                WHEN 'dislike' THEN 'must_be'::kano_category
            END

        WHEN 'expect' THEN
            CASE p_dysfunctional
                WHEN 'like' THEN 'attractive'::kano_category
                WHEN 'dislike' THEN 'must_be'::kano_category
                ELSE 'indifferent'::kano_category
            END

        WHEN 'neutral' THEN
            CASE p_dysfunctional
                WHEN 'like' THEN 'performance'::kano_category
                WHEN 'dislike' THEN 'must_be'::kano_category
                ELSE 'indifferent'::kano_category
            END

        WHEN 'tolerate' THEN
            CASE p_dysfunctional
                WHEN 'like' THEN 'performance'::kano_category
                WHEN 'dislike' THEN 'must_be'::kano_category
                ELSE 'indifferent'::kano_category
            END

        WHEN 'dislike' THEN
            CASE p_dysfunctional
                WHEN 'dislike' THEN 'questionable'::kano_category
                ELSE 'performance'::kano_category
            END
    END;
$$;

-- ------------------------------------------------------------
-- AUTOMATIC CLASSIFICATION TRIGGER
-- The stored classification cannot be independently supplied
-- as an inconsistent value by an application.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION set_kano_classification()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.classification := classify_kano(
        NEW.functional_response,
        NEW.dysfunctional_response
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_set_kano_classification
BEFORE INSERT OR UPDATE OF
    functional_response,
    dysfunctional_response
ON kano_responses
FOR EACH ROW
EXECUTE FUNCTION set_kano_classification();

-- ------------------------------------------------------------
-- FEATURE STATUS TRANSITION VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_feature_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'proposed'
            AND NEW.status IN ('under_research', 'rejected'))
        OR
        (OLD.status = 'under_research'
            AND NEW.status IN ('approved', 'rejected'))
        OR
        (OLD.status = 'approved'
            AND NEW.status IN ('in_development', 'rejected'))
        OR
        (OLD.status = 'in_development'
            AND NEW.status = 'released')
    ) THEN
        RAISE EXCEPTION
            'Invalid feature transition: % -> %',
            OLD.status,
            NEW.status;
    END IF;

    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_feature_transition
BEFORE UPDATE OF status ON features
FOR EACH ROW
EXECUTE FUNCTION validate_feature_transition();

-- ------------------------------------------------------------
-- FEATURE DECISIONS
-- ------------------------------------------------------------

CREATE TABLE feature_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    feature_id BIGINT NOT NULL REFERENCES features(feature_id),
    decision decision_type NOT NULL,
    rationale TEXT NOT NULL,
    decided_by VARCHAR(120) NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT decision_rationale_not_empty
        CHECK (length(trim(rationale)) > 0)
);

CREATE INDEX idx_feature_decisions_feature
    ON feature_decisions(feature_id, decided_at DESC);

-- ------------------------------------------------------------
-- REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW feature_kano_analysis AS
WITH category_counts AS (
    SELECT
        f.feature_id,
        f.feature_code,
        f.feature_name,
        f.status,
        COUNT(r.response_id) AS total_responses,

        COUNT(*) FILTER (
            WHERE r.classification = 'must_be'
        ) AS must_be_count,

        COUNT(*) FILTER (
            WHERE r.classification = 'performance'
        ) AS performance_count,

        COUNT(*) FILTER (
            WHERE r.classification = 'attractive'
        ) AS attractive_count,

        COUNT(*) FILTER (
            WHERE r.classification = 'indifferent'
        ) AS indifferent_count,

        COUNT(*) FILTER (
            WHERE r.classification = 'reverse'
        ) AS reverse_count,

        COUNT(*) FILTER (
            WHERE r.classification = 'questionable'
        ) AS questionable_count

    FROM features f
    LEFT JOIN kano_responses r
        ON r.feature_id = f.feature_id

    GROUP BY
        f.feature_id,
        f.feature_code,
        f.feature_name,
        f.status
),
calculations AS (
    SELECT
        *,
        attractive_count
        + performance_count
        + must_be_count
        + indifferent_count AS coefficient_denominator
    FROM category_counts
)
SELECT
    feature_id,
    feature_code,
    feature_name,
    status,
    total_responses,

    must_be_count,
    performance_count,
    attractive_count,
    indifferent_count,
    reverse_count,
    questionable_count,

    CASE
        WHEN total_responses = 0 THEN NULL
        WHEN GREATEST(
            must_be_count,
            performance_count,
            attractive_count,
            indifferent_count,
            reverse_count
        ) = 0 THEN 'questionable'
        ELSE (
            SELECT category
            FROM (
                VALUES
                    ('must_be', must_be_count),
                    ('performance', performance_count),
                    ('attractive', attractive_count),
                    ('indifferent', indifferent_count),
                    ('reverse', reverse_count)
            ) AS categories(category, category_count)
            ORDER BY category_count DESC,
                     category ASC
            LIMIT 1
        )
    END AS dominant_category,

    ROUND(
        (
            attractive_count + performance_count
        )::NUMERIC
        / NULLIF(coefficient_denominator, 0),
        4
    ) AS satisfaction_coefficient,

    ROUND(
        -(
            performance_count + must_be_count
        )::NUMERIC
        / NULLIF(coefficient_denominator, 0),
        4
    ) AS dissatisfaction_coefficient,

    ROUND(
        questionable_count::NUMERIC
        / NULLIF(total_responses, 0),
        4
    ) AS questionable_rate

FROM calculations;

-- ------------------------------------------------------------
-- FEATURE PRIORITIZATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_feature_priorities()
RETURNS TABLE (
    feature_code VARCHAR,
    feature_name VARCHAR,
    dominant_category TEXT,
    satisfaction NUMERIC,
    dissatisfaction NUMERIC,
    priority_rank BIGINT
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        analysis.feature_code,
        analysis.feature_name,
        analysis.dominant_category::TEXT,
        analysis.satisfaction_coefficient,
        analysis.dissatisfaction_coefficient,

        ROW_NUMBER() OVER (
            ORDER BY
                analysis.dissatisfaction_coefficient ASC NULLS LAST,
                analysis.satisfaction_coefficient DESC NULLS LAST
        )

    FROM feature_kano_analysis analysis
    WHERE analysis.total_responses > 0;
$$;

-- ------------------------------------------------------------
-- STORED PROCEDURE FOR FEATURE DECISIONS
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE record_feature_decision(
    p_feature_code VARCHAR,
    p_decision decision_type,
    p_rationale TEXT,
    p_decided_by VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_feature_id BIGINT;
BEGIN
    SELECT feature_id
    INTO v_feature_id
    FROM features
    WHERE feature_code = p_feature_code
    FOR UPDATE;

    IF v_feature_id IS NULL THEN
        RAISE EXCEPTION 'Unknown feature: %', p_feature_code;
    END IF;

    IF p_rationale IS NULL OR length(trim(p_rationale)) = 0 THEN
        RAISE EXCEPTION 'Decision rationale is required.';
    END IF;

    IF p_decided_by IS NULL OR length(trim(p_decided_by)) = 0 THEN
        RAISE EXCEPTION 'Decision owner is required.';
    END IF;

    INSERT INTO feature_decisions (
        feature_id,
        decision,
        rationale,
        decided_by
    )
    VALUES (
        v_feature_id,
        p_decision,
        p_rationale,
        p_decided_by
    );
END;
$$;

-- ------------------------------------------------------------
-- SAMPLE PRODUCT
-- ------------------------------------------------------------

INSERT INTO products (
    product_name,
    description
)
VALUES (
    'Enterprise Customer Platform',
    'Digital platform for enterprise customer services.'
);

-- ------------------------------------------------------------
-- SAMPLE FEATURES
-- ------------------------------------------------------------

INSERT INTO features (
    product_id,
    feature_code,
    feature_name,
    description
)
SELECT
    product_id,
    sample.feature_code,
    sample.feature_name,
    sample.description
FROM products
CROSS JOIN (
    VALUES
        ('F001', 'Account Security',
         'Secure authentication and data protection.'),
        ('F002', 'Application Speed',
         'Fast application processing and response.'),
        ('F003', 'AI Recommendations',
         'Personalized product suggestions.'),
        ('F004', 'Custom Dashboard',
         'User-configurable dashboard layout.')
) AS sample(feature_code, feature_name, description)
WHERE product_name = 'Enterprise Customer Platform';

-- ------------------------------------------------------------
-- SAMPLE CUSTOMERS
-- ------------------------------------------------------------

INSERT INTO customers (
    external_reference,
    customer_name,
    customer_segment
)
VALUES
    ('C001', 'Customer One', 'Enterprise'),
    ('C002', 'Customer Two', 'Enterprise'),
    ('C003', 'Customer Three', 'SME'),
    ('C004', 'Customer Four', 'SME'),
    ('C005', 'Customer Five', 'Retail');

-- ------------------------------------------------------------
-- SAMPLE SURVEY
-- ------------------------------------------------------------

INSERT INTO surveys (
    product_id,
    survey_name,
    start_date,
    end_date,
    is_active
)
SELECT
    product_id,
    'Enterprise Feature Satisfaction Survey',
    CURRENT_DATE - 30,
    CURRENT_DATE,
    TRUE
FROM products
WHERE product_name = 'Enterprise Customer Platform';

-- ------------------------------------------------------------
-- SAMPLE KANO RESPONSES
-- ------------------------------------------------------------

INSERT INTO kano_responses (
    survey_id,
    feature_id,
    customer_id,
    functional_response,
    dysfunctional_response,
    classification
)
SELECT
    s.survey_id,
    f.feature_id,
    c.customer_id,
    sample.functional_response::response_option,
    sample.dysfunctional_response::response_option,
    'indifferent'::kano_category
FROM (
    VALUES
        ('F001', 'C001', 'like', 'dislike'),
        ('F001', 'C002', 'expect', 'dislike'),
        ('F001', 'C003', 'like', 'dislike'),
        ('F001', 'C004', 'neutral', 'dislike'),
        ('F001', 'C005', 'like', 'dislike'),

        ('F002', 'C001', 'like', 'dislike'),
        ('F002', 'C002', 'like', 'neutral'),
        ('F002', 'C003', 'like', 'dislike'),
        ('F002', 'C004', 'like', 'tolerate'),
        ('F002', 'C005', 'expect', 'dislike'),

        ('F003', 'C001', 'expect', 'dislike'),
        ('F003', 'C002', 'expect', 'dislike'),
        ('F003', 'C003', 'like', 'dislike'),
        ('F003', 'C004', 'expect', 'dislike'),
        ('F003', 'C005', 'neutral', 'neutral'),

        ('F004', 'C001', 'neutral', 'neutral'),
        ('F004', 'C002', 'expect', 'neutral'),
        ('F004', 'C003', 'neutral', 'tolerate'),
        ('F004', 'C004', 'expect', 'neutral'),
        ('F004', 'C005', 'neutral', 'neutral')
) AS sample(
    feature_code,
    customer_reference,
    functional_response,
    dysfunctional_response
)
JOIN features f
    ON f.feature_code = sample.feature_code
JOIN customers c
    ON c.external_reference = sample.customer_reference
CROSS JOIN surveys s
WHERE s.survey_name =
    'Enterprise Feature Satisfaction Survey';

-- ------------------------------------------------------------
-- VALIDATION QUERIES
-- ------------------------------------------------------------

-- 1. Verify automatic Kano classifications.
SELECT
    feature_code,
    customer_reference.external_reference,
    r.functional_response,
    r.dysfunctional_response,
    r.classification
FROM kano_responses r
JOIN features f USING (feature_id)
JOIN customers customer_reference USING (customer_id)
ORDER BY feature_code, external_reference;

-- 2. Feature classification and coefficients.
SELECT *
FROM feature_kano_analysis
ORDER BY feature_code;

-- 3. Feature prioritization.
SELECT *
FROM get_feature_priorities();

-- 4. Customer segment response distribution.
SELECT
    c.customer_segment,
    r.classification,
    COUNT(*) AS response_count
FROM kano_responses r
JOIN customers c USING (customer_id)
GROUP BY
    c.customer_segment,
    r.classification
ORDER BY
    c.customer_segment,
    r.classification;

-- 5. Survey response coverage.
SELECT
    f.feature_code,
    f.feature_name,
    COUNT(r.response_id) AS received_responses,
    COUNT(DISTINCT r.customer_id) AS unique_customers
FROM features f
LEFT JOIN kano_responses r USING (feature_id)
GROUP BY f.feature_id
ORDER BY f.feature_code;

-- 6. Questionable response monitoring.
SELECT
    feature_code,
    feature_name,
    questionable_count,
    questionable_rate
FROM feature_kano_analysis
WHERE questionable_count > 0;

-- 7. Reverse requirement detection.
SELECT
    f.feature_code,
    f.feature_name,
    COUNT(*) AS reverse_responses
FROM kano_responses r
JOIN features f USING (feature_id)
WHERE r.classification = 'reverse'
GROUP BY f.feature_id
ORDER BY reverse_responses DESC;

-- ------------------------------------------------------------
-- DECISION RECORDS
-- ------------------------------------------------------------

CALL record_feature_decision(
    'F001',
    'prioritize',
    'Account security is a fundamental customer requirement.',
    'Product Management'
);

CALL record_feature_decision(
    'F002',
    'prioritize',
    'Performance improvement is associated with customer satisfaction.',
    'Product Management'
);

CALL record_feature_decision(
    'F003',
    'investigate',
    'Assess the business value of personalized recommendations.',
    'Product Research'
);

CALL record_feature_decision(
    'F004',
    'defer',
    'Evaluate dashboard customization against other product priorities.',
    'Product Management'
);

-- ------------------------------------------------------------
-- DECISION REPORT
-- ------------------------------------------------------------

SELECT
    f.feature_code,
    f.feature_name,
    d.decision,
    d.rationale,
    d.decided_by,
    d.decided_at
FROM feature_decisions d
JOIN features f USING (feature_id)
ORDER BY d.decided_at DESC;

-- ------------------------------------------------------------
-- TRANSACTIONAL STATUS TRANSITION
-- ------------------------------------------------------------

-- Demonstrates a valid feature lifecycle transition.
UPDATE features
SET status = 'under_research'
WHERE feature_code = 'F003';

-- Demonstrates rollback for an invalid transition.
SAVEPOINT invalid_transition_test;

DO $$
BEGIN
    BEGIN
        UPDATE features
        SET status = 'released'
        WHERE feature_code = 'F004';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Invalid transition correctly rejected: %',
                SQLERRM;
    END;
END;
$$;

RELEASE SAVEPOINT invalid_transition_test;

COMMIT;

-- ------------------------------------------------------------
-- OPERATIONAL NOTES
-- ------------------------------------------------------------

-- Production applications should restrict direct table access.
-- Use dedicated roles and grant EXECUTE on controlled functions.
-- Customer identifiers should be pseudonymized where possible.
-- Apply survey retention and consent policies.
-- Run EXPLAIN ANALYZE against large survey workloads.
-- The dominant category is a frequency-based classification.
-- Tied categories require business interpretation.
-- Satisfaction coefficients are directional indicators,
-- not direct measures of revenue or absolute satisfaction.
