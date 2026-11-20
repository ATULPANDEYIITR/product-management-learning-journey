-- ============================================================
-- RETENTION ANALYTICS DATABASE
-- PostgreSQL 15+
--
-- Domain:
-- Customers -> Events -> Cohorts -> Retention
--                         |
--                         +-> Churn
--                         |
--                         +-> Resurrection
--
-- Retention definition:
-- A customer is retained at age D when at least one qualifying
-- activity event occurs exactly D calendar days after signup.
--
-- Churn definition:
-- An eligible customer is churned when the number of days
-- since their last qualifying activity reaches the threshold.
--
-- Resurrection definition:
-- A customer returns after an inactivity gap equal to or
-- greater than the churn threshold.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS retention;

SET search_path TO retention, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE event_type AS ENUM (
    'signup',
    'active',
    'login',
    'purchase'
);

CREATE TYPE customer_status AS ENUM (
    'active',
    'churned',
    'not_eligible'
);

CREATE TYPE analytics_job_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed'
);

-- ------------------------------------------------------------
-- 2. Customers
-- ------------------------------------------------------------

CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_customer_id VARCHAR(128) NOT NULL UNIQUE,
    signup_date DATE NOT NULL,
    acquisition_channel VARCHAR(80) NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'IN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_external_customer_id
        CHECK (length(trim(external_customer_id)) > 0),

    CONSTRAINT valid_acquisition_channel
        CHECK (length(trim(acquisition_channel)) > 0),

    CONSTRAINT valid_country_code
        CHECK (country_code ~ '^[A-Z]{2}$')
);

CREATE INDEX idx_customers_signup_date
    ON customers(signup_date);

CREATE INDEX idx_customers_channel_signup
    ON customers(acquisition_channel, signup_date);

-- ------------------------------------------------------------
-- 3. Customer activity events
-- ------------------------------------------------------------

CREATE TABLE customer_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id)
        ON DELETE RESTRICT,

    event_date DATE NOT NULL,
    event_type event_type NOT NULL,

    source_event_id VARCHAR(150),
    event_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_source_event_id
        CHECK (
            source_event_id IS NULL
            OR length(trim(source_event_id)) > 0
        ),

    CONSTRAINT valid_event_metadata
        CHECK (jsonb_typeof(event_metadata) = 'object'),

    CONSTRAINT unique_customer_source_event
        UNIQUE (customer_id, source_event_id)
);

-- Prevent duplicate events from the same customer on the
-- same date and event type when no source event ID exists.
CREATE UNIQUE INDEX uq_customer_daily_event
    ON customer_events(customer_id, event_date, event_type)
    WHERE source_event_id IS NULL;

CREATE INDEX idx_events_customer_date
    ON customer_events(customer_id, event_date);

CREATE INDEX idx_events_date_type
    ON customer_events(event_date, event_type);

CREATE INDEX idx_events_active_customer_date
    ON customer_events(customer_id, event_date)
    WHERE event_type IN ('active', 'login', 'purchase');

CREATE INDEX idx_events_metadata
    ON customer_events USING GIN(event_metadata);

-- ------------------------------------------------------------
-- 4. Retention configuration
-- ------------------------------------------------------------

CREATE TABLE retention_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL UNIQUE,

    churn_days INTEGER NOT NULL DEFAULT 30,

    retention_intervals INTEGER[] NOT NULL
        DEFAULT ARRAY[0, 1, 7, 14, 30],

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_churn_days
        CHECK (churn_days > 0),

    CONSTRAINT valid_intervals
        CHECK (
            cardinality(retention_intervals) > 0
            AND 0 <= ALL(retention_intervals)
        )
);

INSERT INTO retention_policies (
    policy_name,
    churn_days,
    retention_intervals
)
VALUES (
    'standard_30_day',
    30,
    ARRAY[0, 1, 7, 14, 30]
);

-- ------------------------------------------------------------
-- 5. Analytics execution history
-- ------------------------------------------------------------

CREATE TABLE analytics_jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_id BIGINT NOT NULL
        REFERENCES retention_policies(policy_id),

    observation_date DATE NOT NULL,

    job_status analytics_job_status NOT NULL DEFAULT 'pending',

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_job_timestamps
        CHECK (
            completed_at IS NULL
            OR started_at IS NOT NULL
        )
);

CREATE INDEX idx_analytics_jobs_status
    ON analytics_jobs(job_status, created_at DESC);

-- ------------------------------------------------------------
-- 6. Derived daily retention metrics
-- ------------------------------------------------------------

CREATE TABLE retention_metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES analytics_jobs(job_id)
        ON DELETE CASCADE,

    cohort_month DATE NOT NULL,
    age_day INTEGER NOT NULL,

    eligible_customers INTEGER NOT NULL,
    retained_customers INTEGER NOT NULL,

    retention_rate NUMERIC(7, 2) NOT NULL,

    CONSTRAINT unique_cohort_period
        UNIQUE (job_id, cohort_month, age_day),

    CONSTRAINT valid_cohort_month
        CHECK (
            EXTRACT(DAY FROM cohort_month) = 1
        ),

    CONSTRAINT valid_age
        CHECK (age_day >= 0),

    CONSTRAINT valid_customer_counts
        CHECK (
            eligible_customers >= 0
            AND retained_customers >= 0
            AND retained_customers <= eligible_customers
        ),

    CONSTRAINT valid_retention_rate
        CHECK (
            retention_rate >= 0
            AND retention_rate <= 100
        )
);

CREATE INDEX idx_retention_cohort
    ON retention_metrics(cohort_month, age_day);

CREATE INDEX idx_retention_job
    ON retention_metrics(job_id, age_day);

-- ------------------------------------------------------------
-- 7. Churn classification
-- ------------------------------------------------------------

CREATE TABLE customer_churn (
    churn_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES analytics_jobs(job_id)
        ON DELETE CASCADE,

    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),

    last_activity_date DATE NOT NULL,

    inactive_days INTEGER NOT NULL,

    status customer_status NOT NULL,

    classified_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_customer_churn_job
        UNIQUE(job_id, customer_id),

    CONSTRAINT valid_inactive_days
        CHECK (inactive_days >= 0)
);

CREATE INDEX idx_churn_job_status
    ON customer_churn(job_id, status);

-- ------------------------------------------------------------
-- 8. Resurrection events
-- ------------------------------------------------------------

CREATE TABLE customer_resurrections (
    resurrection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES analytics_jobs(job_id)
        ON DELETE CASCADE,

    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),

    previous_activity_date DATE NOT NULL,

    resurrection_date DATE NOT NULL,

    inactive_days INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_resurrection_gap
        CHECK (
            resurrection_date > previous_activity_date
            AND inactive_days > 0
        ),

    CONSTRAINT unique_resurrection_event
        UNIQUE (
            job_id,
            customer_id,
            previous_activity_date,
            resurrection_date
        )
);

CREATE INDEX idx_resurrections_customer
    ON customer_resurrections(customer_id, resurrection_date);

-- ------------------------------------------------------------
-- 9. Signup validation trigger
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_customer_event()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    registered_date DATE;
BEGIN
    SELECT signup_date
    INTO registered_date
    FROM customers
    WHERE customer_id = NEW.customer_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Customer % does not exist',
            NEW.customer_id;
    END IF;

    IF NEW.event_date < registered_date THEN
        RAISE EXCEPTION
            'Event date cannot precede customer signup';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_customer_event
BEFORE INSERT OR UPDATE OF customer_id, event_date
ON customer_events
FOR EACH ROW
EXECUTE FUNCTION validate_customer_event();

-- ------------------------------------------------------------
-- 10. Latest activity view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW customer_activity_summary AS
SELECT
    c.customer_id,
    c.external_customer_id,
    c.signup_date,
    c.acquisition_channel,

    MAX(e.event_date) FILTER (
        WHERE e.event_type IN ('active', 'login', 'purchase')
    ) AS last_activity_date,

    COUNT(DISTINCT e.event_date) FILTER (
        WHERE e.event_type IN ('active', 'login', 'purchase')
    ) AS active_days,

    COUNT(e.event_id) FILTER (
        WHERE e.event_type = 'purchase'
    ) AS purchase_events

FROM customers c
LEFT JOIN customer_events e
    ON e.customer_id = c.customer_id

GROUP BY
    c.customer_id,
    c.external_customer_id,
    c.signup_date,
    c.acquisition_channel;

-- ------------------------------------------------------------
-- 11. Eligibility evaluation function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_customer_status(
    p_signup_date DATE,
    p_last_activity DATE,
    p_observation_date DATE,
    p_churn_days INTEGER
)
RETURNS customer_status
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    tenure_days INTEGER;
    inactive_days INTEGER;
BEGIN
    IF p_churn_days <= 0 THEN
        RAISE EXCEPTION 'Churn threshold must be positive';
    END IF;

    IF p_observation_date < p_signup_date THEN
        RAISE EXCEPTION
            'Observation date precedes signup date';
    END IF;

    tenure_days := p_observation_date - p_signup_date;

    IF tenure_days < p_churn_days THEN
        RETURN 'not_eligible';
    END IF;

    inactive_days := p_observation_date - p_last_activity;

    IF inactive_days >= p_churn_days THEN
        RETURN 'churned';
    END IF;

    RETURN 'active';
END;
$$;

-- ------------------------------------------------------------
-- 12. Create analytics job
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE create_analytics_job(
    IN p_policy_name VARCHAR(100),
    IN p_observation_date DATE,
    INOUT p_job_id BIGINT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_policy BIGINT;
BEGIN
    SELECT policy_id
    INTO selected_policy
    FROM retention_policies
    WHERE policy_name = p_policy_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Active retention policy not found: %',
            p_policy_name;
    END IF;

    INSERT INTO analytics_jobs (
        policy_id,
        observation_date,
        job_status
    )
    VALUES (
        selected_policy,
        p_observation_date,
        'pending'
    )
    RETURNING job_id INTO p_job_id;
END;
$$;

-- ------------------------------------------------------------
-- 13. Retention calculation procedure
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE calculate_retention(
    IN p_job_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_observation DATE;
    v_policy_id BIGINT;
    v_intervals INTEGER[];
BEGIN
    SELECT
        j.observation_date,
        p.policy_id,
        p.retention_intervals
    INTO
        v_observation,
        v_policy_id,
        v_intervals
    FROM analytics_jobs j
    JOIN retention_policies p
        ON p.policy_id = j.policy_id
    WHERE j.job_id = p_job_id
      AND j.job_status IN ('pending', 'failed');

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Analytics job unavailable or already processed';
    END IF;

    UPDATE analytics_jobs
    SET
        job_status = 'running',
        started_at = CURRENT_TIMESTAMP,
        completed_at = NULL,
        error_message = NULL
    WHERE job_id = p_job_id;

    DELETE FROM retention_metrics
    WHERE job_id = p_job_id;

    DELETE FROM customer_churn
    WHERE job_id = p_job_id;

    DELETE FROM customer_resurrections
    WHERE job_id = p_job_id;

    -- Generate retention values for every cohort and requested age.
    INSERT INTO retention_metrics (
        job_id,
        cohort_month,
        age_day,
        eligible_customers,
        retained_customers,
        retention_rate
    )
    WITH cohorts AS (
        SELECT
            customer_id,
            signup_date,
            DATE_TRUNC('month', signup_date)::DATE AS cohort_month
        FROM customers
    ),
    requested_ages AS (
        SELECT UNNEST(v_intervals) AS age_day
    ),
    activity AS (
        SELECT DISTINCT
            customer_id,
            event_date
        FROM customer_events
        WHERE event_type IN ('active', 'login', 'purchase')
    ),
    cohort_counts AS (
        SELECT
            c.cohort_month,
            a.age_day,

            COUNT(*) FILTER (
                WHERE c.signup_date + a.age_day <= v_observation
            )::INTEGER AS eligible,

            COUNT(*) FILTER (
                WHERE c.signup_date + a.age_day <= v_observation
                  AND activity.customer_id IS NOT NULL
            )::INTEGER AS retained

        FROM cohorts c
        CROSS JOIN requested_ages a

        LEFT JOIN activity
            ON activity.customer_id = c.customer_id
           AND activity.event_date = c.signup_date + a.age_day

        GROUP BY
            c.cohort_month,
            a.age_day
    )
    SELECT
        p_job_id,
        cohort_month,
        age_day,
        eligible,
        retained,

        CASE
            WHEN eligible = 0 THEN 0
            ELSE ROUND(
                100.0 * retained / eligible,
                2
            )
        END

    FROM cohort_counts
    WHERE eligible > 0;

    -- Classify customers using their latest qualifying activity.
    INSERT INTO customer_churn (
        job_id,
        customer_id,
        last_activity_date,
        inactive_days,
        status
    )
    SELECT
        p_job_id,
        c.customer_id,

        COALESCE(
            s.last_activity_date,
            c.signup_date
        ),

        v_observation - COALESCE(
            s.last_activity_date,
            c.signup_date
        ),

        evaluate_customer_status(
            c.signup_date,
            COALESCE(s.last_activity_date, c.signup_date),
            v_observation,
            p.churn_days
        )

    FROM customers c
    JOIN retention_policies p
        ON p.policy_id = v_policy_id

    LEFT JOIN customer_activity_summary s
        ON s.customer_id = c.customer_id

    WHERE c.signup_date <= v_observation;

    -- Identify resurrection from consecutive distinct activity dates.
    INSERT INTO customer_resurrections (
        job_id,
        customer_id,
        previous_activity_date,
        resurrection_date,
        inactive_days
    )
    WITH activity_dates AS (
        SELECT DISTINCT
            customer_id,
            event_date
        FROM customer_events
        WHERE event_type IN ('active', 'login', 'purchase')
          AND event_date <= v_observation
    ),
    activity_gaps AS (
        SELECT
            customer_id,
            event_date AS resurrection_date,

            LAG(event_date) OVER (
                PARTITION BY customer_id
                ORDER BY event_date
            ) AS previous_activity_date

        FROM activity_dates
    )
    SELECT
        p_job_id,
        customer_id,
        previous_activity_date,
        resurrection_date,
        resurrection_date - previous_activity_date

    FROM activity_gaps

    WHERE previous_activity_date IS NOT NULL
      AND resurrection_date - previous_activity_date
          >= (
              SELECT churn_days
              FROM retention_policies
              WHERE policy_id = v_policy_id
          );

    UPDATE analytics_jobs
    SET
        job_status = 'completed',
        completed_at = CURRENT_TIMESTAMP
    WHERE job_id = p_job_id;

EXCEPTION
    WHEN OTHERS THEN
        -- Re-raise the error. The caller's transaction controls
        -- rollback and failed-job recording.
        RAISE;
END;
$$;

-- ------------------------------------------------------------
-- 14. Sample customers
-- ------------------------------------------------------------

INSERT INTO customers (
    external_customer_id,
    signup_date,
    acquisition_channel,
    country_code
)
VALUES
    ('U001', '2026-01-01', 'organic', 'IN'),
    ('U002', '2026-01-03', 'paid_search', 'IN'),
    ('U003', '2026-01-10', 'referral', 'IN'),
    ('U004', '2026-02-01', 'organic', 'IN'),
    ('U005', '2026-02-05', 'paid_search', 'IN'),
    ('U006', '2026-02-15', 'referral', 'IN'),
    ('U007', '2026-03-01', 'organic', 'IN'),
    ('U008', '2026-03-10', 'paid_search', 'IN'),
    ('U009', '2026-03-15', 'organic', 'IN');

-- ------------------------------------------------------------
-- 15. Sample activity events
-- ------------------------------------------------------------

INSERT INTO customer_events (
    customer_id,
    event_date,
    event_type,
    source_event_id
)
SELECT
    c.customer_id,
    sample.event_date,
    sample.event_type::event_type,
    sample.source_event_id

FROM (
    VALUES
        ('U001', '2026-01-01', 'active', 'E001'),
        ('U001', '2026-01-02', 'active', 'E002'),
        ('U001', '2026-01-08', 'login', 'E003'),
        ('U001', '2026-03-05', 'purchase', 'E004'),

        ('U002', '2026-01-03', 'active', 'E005'),
        ('U002', '2026-01-04', 'login', 'E006'),

        ('U003', '2026-01-10', 'active', 'E007'),
        ('U003', '2026-02-15', 'active', 'E008'),

        ('U004', '2026-02-01', 'active', 'E009'),
        ('U004', '2026-02-02', 'login', 'E010'),
        ('U004', '2026-02-08', 'active', 'E011'),

        ('U005', '2026-02-05', 'active', 'E012'),

        ('U006', '2026-02-15', 'active', 'E013'),
        ('U006', '2026-03-20', 'purchase', 'E014'),

        ('U007', '2026-03-01', 'active', 'E015'),
        ('U007', '2026-03-02', 'login', 'E016'),

        ('U008', '2026-03-10', 'active', 'E017'),
        ('U008', '2026-04-15', 'active', 'E018'),

        ('U009', '2026-03-15', 'active', 'E019')

) AS sample(
    external_customer_id,
    event_date,
    event_type,
    source_event_id
)

JOIN customers c
    ON c.external_customer_id = sample.external_customer_id;

-- ------------------------------------------------------------
-- 16. Transactional analytics execution
-- ------------------------------------------------------------

DO $$
DECLARE
    v_job_id BIGINT;
BEGIN
    CALL create_analytics_job(
        'standard_30_day',
        '2026-05-01',
        v_job_id
    );

    CALL calculate_retention(v_job_id);

    RAISE NOTICE 'Completed retention job: %', v_job_id;
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- 17. Retrieval: retention curve
-- ------------------------------------------------------------

SELECT
    cohort_month,
    age_day,
    eligible_customers,
    retained_customers,
    retention_rate
FROM retention_metrics
WHERE job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)
ORDER BY cohort_month, age_day;

-- ------------------------------------------------------------
-- 18. Retrieval: cohort retention matrix
-- ------------------------------------------------------------

SELECT
    cohort_month,

    MAX(retention_rate) FILTER (
        WHERE age_day = 0
    ) AS day_0,

    MAX(retention_rate) FILTER (
        WHERE age_day = 1
    ) AS day_1,

    MAX(retention_rate) FILTER (
        WHERE age_day = 7
    ) AS day_7,

    MAX(retention_rate) FILTER (
        WHERE age_day = 14
    ) AS day_14,

    MAX(retention_rate) FILTER (
        WHERE age_day = 30
    ) AS day_30

FROM retention_metrics
WHERE job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)
GROUP BY cohort_month
ORDER BY cohort_month;

-- ------------------------------------------------------------
-- 19. Aggregation: channel-level customer acquisition
-- ------------------------------------------------------------

SELECT
    acquisition_channel,
    COUNT(*) AS acquired_customers,
    MIN(signup_date) AS first_signup,
    MAX(signup_date) AS latest_signup

FROM customers

GROUP BY acquisition_channel
ORDER BY acquired_customers DESC;

-- ------------------------------------------------------------
-- 20. Evaluation: churn distribution
-- ------------------------------------------------------------

SELECT
    status,
    COUNT(*) AS customer_count,

    ROUND(
        100.0 * COUNT(*) /
        NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage

FROM customer_churn

WHERE job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)

GROUP BY status
ORDER BY status;

-- ------------------------------------------------------------
-- 21. Resurrection reporting
-- ------------------------------------------------------------

SELECT
    c.external_customer_id,
    r.previous_activity_date,
    r.resurrection_date,
    r.inactive_days

FROM customer_resurrections r

JOIN customers c
    ON c.customer_id = r.customer_id

WHERE r.job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)

ORDER BY r.resurrection_date;

-- ------------------------------------------------------------
-- 22. Validation: missing signup activity
-- ------------------------------------------------------------

SELECT
    c.external_customer_id,
    c.signup_date

FROM customers c

LEFT JOIN customer_events e
    ON e.customer_id = c.customer_id
   AND e.event_type = 'signup'

WHERE e.event_id IS NULL;

-- ------------------------------------------------------------
-- 23. Validation: events before signup
-- ------------------------------------------------------------

SELECT
    c.external_customer_id,
    e.event_date,
    c.signup_date

FROM customer_events e

JOIN customers c
    ON c.customer_id = e.customer_id

WHERE e.event_date < c.signup_date;

-- ------------------------------------------------------------
-- 24. Retrieval: customer lifecycle status
-- ------------------------------------------------------------

SELECT
    c.external_customer_id,
    c.signup_date,
    s.last_activity_date,
    s.active_days,
    ch.inactive_days,
    ch.status

FROM customer_churn ch

JOIN customers c
    ON c.customer_id = ch.customer_id

LEFT JOIN customer_activity_summary s
    ON s.customer_id = c.customer_id

WHERE ch.job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)

ORDER BY ch.inactive_days DESC;

-- ------------------------------------------------------------
-- 25. Evaluation: cohort comparison
-- ------------------------------------------------------------

WITH cohort_performance AS (
    SELECT
        cohort_month,

        MAX(retention_rate) FILTER (
            WHERE age_day = 7
        ) AS day_7_retention,

        MAX(retention_rate) FILTER (
            WHERE age_day = 30
        ) AS day_30_retention

    FROM retention_metrics

    WHERE job_id = (
        SELECT MAX(job_id)
        FROM analytics_jobs
        WHERE job_status = 'completed'
    )

    GROUP BY cohort_month
)
SELECT
    cohort_month,
    day_7_retention,
    day_30_retention,

    ROUND(
        day_7_retention - day_30_retention,
        2
    ) AS retention_decline

FROM cohort_performance
ORDER BY cohort_month;

-- ------------------------------------------------------------
-- 26. Workflow: analytics job history
-- ------------------------------------------------------------

SELECT
    j.job_id,
    p.policy_name,
    j.observation_date,
    j.job_status,
    j.started_at,
    j.completed_at,
    j.error_message

FROM analytics_jobs j

JOIN retention_policies p
    ON p.policy_id = j.policy_id

ORDER BY j.created_at DESC;

-- ------------------------------------------------------------
-- 27. Eligibility: current customer classification
-- ------------------------------------------------------------

SELECT
    c.external_customer_id,

    evaluate_customer_status(
        c.signup_date,
        COALESCE(
            s.last_activity_date,
            c.signup_date
        ),
        DATE '2026-05-01',
        p.churn_days
    ) AS current_status

FROM customers c

CROSS JOIN retention_policies p

LEFT JOIN customer_activity_summary s
    ON s.customer_id = c.customer_id

WHERE p.policy_name = 'standard_30_day'
  AND p.is_active = TRUE

ORDER BY c.external_customer_id;

-- ------------------------------------------------------------
-- 28. Reporting: overall resurrection performance
-- ------------------------------------------------------------

SELECT
    COUNT(DISTINCT customer_id) AS resurrected_customers,
    COUNT(*) AS resurrection_events,
    ROUND(AVG(inactive_days), 2) AS average_inactive_days,
    MAX(inactive_days) AS maximum_inactive_days

FROM customer_resurrections

WHERE job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
);

-- ------------------------------------------------------------
-- 29. Reporting: retention by acquisition channel
-- ------------------------------------------------------------

SELECT
    c.acquisition_channel,
    r.age_day,

    SUM(r.eligible_customers) AS eligible_customers,
    SUM(r.retained_customers) AS retained_customers,

    ROUND(
        100.0 * SUM(r.retained_customers) /
        NULLIF(SUM(r.eligible_customers), 0),
        2
    ) AS retention_rate

FROM retention_metrics r

JOIN customers c
    ON DATE_TRUNC('month', c.signup_date)::DATE =
       r.cohort_month

WHERE r.job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)

GROUP BY c.acquisition_channel, r.age_day

ORDER BY c.acquisition_channel, r.age_day;

-- ------------------------------------------------------------
-- 30. Reporting: customers with multiple resurrections
-- ------------------------------------------------------------

SELECT
    c.external_customer_id,
    COUNT(*) AS resurrection_count,
    MAX(r.resurrection_date) AS latest_resurrection

FROM customer_resurrections r

JOIN customers c
    ON c.customer_id = r.customer_id

WHERE r.job_id = (
    SELECT MAX(job_id)
    FROM analytics_jobs
    WHERE job_status = 'completed'
)

GROUP BY c.external_customer_id

HAVING COUNT(*) > 1

ORDER BY resurrection_count DESC;

-- ------------------------------------------------------------
-- 31. Performance inspection
-- ------------------------------------------------------------

EXPLAIN
SELECT
    customer_id,
    MAX(event_date)
FROM customer_events
WHERE event_type IN ('active', 'login', 'purchase')
GROUP BY customer_id;

-- ------------------------------------------------------------
-- 32. Operational integrity checks
-- ------------------------------------------------------------

SELECT
    'customer_count' AS validation,
    COUNT(*)::BIGINT AS result
FROM customers

UNION ALL

SELECT
    'event_count',
    COUNT(*)::BIGINT
FROM customer_events

UNION ALL

SELECT
    'completed_jobs',
    COUNT(*)::BIGINT
FROM analytics_jobs
WHERE job_status = 'completed'

UNION ALL

SELECT
    'resurrection_events',
    COUNT(*)::BIGINT
FROM customer_resurrections;
