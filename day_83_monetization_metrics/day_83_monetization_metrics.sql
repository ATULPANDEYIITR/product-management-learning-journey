-- ============================================================
-- MONETIZATION METRICS AND FINANCIAL PERFORMANCE DATABASE
-- PostgreSQL 15+
--
-- Metrics:
-- ARPU, ARPPU, MRR, ARR, LTV, CAC, Gross Margin
--
-- Includes:
-- Relational modeling, constraints, indexes, triggers,
-- functions, views, reporting, validation, and transactions.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS monetization;

SET search_path TO monetization, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_reference VARCHAR(100) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    acquisition_date DATE NOT NULL,
    customer_status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_customer_status
        CHECK (customer_status IN (
            'active', 'inactive', 'churned'
        ))
);

CREATE TABLE IF NOT EXISTS plans (
    plan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL UNIQUE,
    billing_interval_months INTEGER NOT NULL,
    standard_price NUMERIC(14,2) NOT NULL,

    CONSTRAINT valid_billing_interval
        CHECK (billing_interval_months IN (1, 3, 6, 12)),

    CONSTRAINT nonnegative_plan_price
        CHECK (standard_price >= 0)
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    plan_id BIGINT NOT NULL REFERENCES plans(plan_id),
    start_date DATE NOT NULL,
    end_date DATE,
    subscription_status VARCHAR(20) NOT NULL DEFAULT 'active',
    agreed_price NUMERIC(14,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_subscription_status
        CHECK (subscription_status IN (
            'active', 'cancelled', 'past_due', 'suspended'
        )),

    CONSTRAINT valid_subscription_dates
        CHECK (end_date IS NULL OR end_date >= start_date),

    CONSTRAINT nonnegative_agreed_price
        CHECK (agreed_price >= 0)
);

CREATE TABLE IF NOT EXISTS monthly_financials (
    financial_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reporting_month DATE NOT NULL UNIQUE,
    total_users INTEGER NOT NULL,
    paying_users INTEGER NOT NULL,
    one_time_revenue NUMERIC(16,2) NOT NULL DEFAULT 0,
    variable_cost NUMERIC(16,2) NOT NULL DEFAULT 0,
    fixed_cost NUMERIC(16,2) NOT NULL DEFAULT 0,
    marketing_spend NUMERIC(16,2) NOT NULL DEFAULT 0,
    sales_spend NUMERIC(16,2) NOT NULL DEFAULT 0,
    new_customers INTEGER NOT NULL,
    churned_customers INTEGER NOT NULL DEFAULT 0,
    monthly_churn_rate NUMERIC(8,6),

    CONSTRAINT valid_reporting_month
        CHECK (
            EXTRACT(DAY FROM reporting_month) = 1
        ),

    CONSTRAINT valid_user_counts
        CHECK (
            total_users >= 0
            AND paying_users >= 0
            AND paying_users <= total_users
        ),

    CONSTRAINT valid_financial_values
        CHECK (
            one_time_revenue >= 0
            AND variable_cost >= 0
            AND fixed_cost >= 0
            AND marketing_spend >= 0
            AND sales_spend >= 0
            AND new_customers >= 0
            AND churned_customers >= 0
        ),

    CONSTRAINT valid_churn_rate
        CHECK (
            monthly_churn_rate IS NULL
            OR monthly_churn_rate BETWEEN 0 AND 1
        )
);

-- ------------------------------------------------------------
-- 2. OPERATIONAL INDEXES
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_customers_status
    ON customers(customer_status);

CREATE INDEX IF NOT EXISTS idx_customers_acquisition_date
    ON customers(acquisition_date);

CREATE INDEX IF NOT EXISTS idx_subscriptions_customer
    ON subscriptions(customer_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_active
    ON subscriptions(subscription_status, customer_id)
    WHERE subscription_status = 'active';

CREATE INDEX IF NOT EXISTS idx_subscriptions_plan
    ON subscriptions(plan_id);

CREATE INDEX IF NOT EXISTS idx_financials_reporting_month
    ON monthly_financials(reporting_month DESC);

-- ------------------------------------------------------------
-- 3. SAMPLE PLANS
-- ------------------------------------------------------------

INSERT INTO plans (
    plan_name,
    billing_interval_months,
    standard_price
)
VALUES
    ('Starter Monthly', 1, 100),
    ('Professional Quarterly', 3, 450),
    ('Enterprise Annual', 12, 1200),
    ('Business Semiannual', 6, 900)
ON CONFLICT (plan_name) DO NOTHING;

-- ------------------------------------------------------------
-- 4. SAMPLE CUSTOMERS
-- ------------------------------------------------------------

INSERT INTO customers (
    external_reference,
    customer_name,
    acquisition_date,
    customer_status
)
VALUES
    ('EXT001', 'Customer Alpha', '2026-03-10', 'active'),
    ('EXT002', 'Customer Beta', '2026-04-15', 'active'),
    ('EXT003', 'Customer Gamma', '2026-06-20', 'active'),
    ('EXT004', 'Customer Delta', '2026-07-05', 'active'),
    ('EXT005', 'Customer Epsilon', '2026-08-12', 'churned')
ON CONFLICT (external_reference) DO NOTHING;

-- ------------------------------------------------------------
-- 5. SAMPLE SUBSCRIPTIONS
-- ------------------------------------------------------------

INSERT INTO subscriptions (
    customer_id,
    plan_id,
    start_date,
    end_date,
    subscription_status,
    agreed_price
)
SELECT
    c.customer_id,
    p.plan_id,
    DATE '2026-09-01',
    NULL,
    'active',
    p.standard_price
FROM customers c
JOIN plans p
    ON (
        (c.external_reference = 'EXT001'
            AND p.plan_name = 'Starter Monthly')
        OR
        (c.external_reference = 'EXT002'
            AND p.plan_name = 'Professional Quarterly')
        OR
        (c.external_reference = 'EXT003'
            AND p.plan_name = 'Enterprise Annual')
        OR
        (c.external_reference = 'EXT004'
            AND p.plan_name = 'Business Semiannual')
    )
WHERE NOT EXISTS (
    SELECT 1
    FROM subscriptions s
    WHERE s.customer_id = c.customer_id
);

-- ------------------------------------------------------------
-- 6. MONTHLY FINANCIAL INPUT
-- ------------------------------------------------------------

INSERT INTO monthly_financials (
    reporting_month,
    total_users,
    paying_users,
    one_time_revenue,
    variable_cost,
    fixed_cost,
    marketing_spend,
    sales_spend,
    new_customers,
    churned_customers,
    monthly_churn_rate
)
VALUES
(
    DATE '2026-10-01',
    1000,
    200,
    5000,
    12000,
    25000,
    18000,
    12000,
    80,
    10,
    0.050000
),
(
    DATE '2026-11-01',
    1200,
    250,
    7000,
    15000,
    27000,
    20000,
    15000,
    100,
    12,
    0.045000
)
ON CONFLICT (reporting_month) DO NOTHING;

-- ------------------------------------------------------------
-- 7. MRR FUNCTION
--
-- Monthly revenue is normalized by billing interval.
-- Annual subscriptions contribute one-twelfth of their price.
-- Cancelled, suspended, and past-due subscriptions are excluded.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_mrr(
    p_reporting_date DATE
)
RETURNS NUMERIC(16,2)
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(
        SUM(
            s.agreed_price /
            p.billing_interval_months
        ),
        0
    )::NUMERIC(16,2)
    FROM subscriptions s
    JOIN plans p ON p.plan_id = s.plan_id
    JOIN customers c ON c.customer_id = s.customer_id
    WHERE s.subscription_status = 'active'
      AND c.customer_status = 'active'
      AND s.start_date <= p_reporting_date
      AND (
          s.end_date IS NULL
          OR s.end_date >= p_reporting_date
      );
$$;

-- ------------------------------------------------------------
-- 8. COMPLETE MONETIZATION METRICS FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_monetization_metrics(
    p_reporting_date DATE
)
RETURNS TABLE (
    reporting_month DATE,
    total_users BIGINT,
    paying_users BIGINT,
    arpu NUMERIC,
    arppu NUMERIC,
    mrr NUMERIC,
    arr NUMERIC,
    ltv NUMERIC,
    cac NUMERIC,
    gross_profit NUMERIC,
    gross_margin NUMERIC,
    ltv_cac_ratio NUMERIC,
    payback_months NUMERIC
)
LANGUAGE SQL
STABLE
AS $$
    WITH user_counts AS (
        SELECT
            COUNT(*) FILTER (
                WHERE customer_status = 'active'
            ) AS total_users
        FROM customers
    ),
    paying_counts AS (
        SELECT
            COUNT(DISTINCT s.customer_id) AS paying_users
        FROM subscriptions s
        JOIN customers c
            ON c.customer_id = s.customer_id
        WHERE s.subscription_status = 'active'
          AND c.customer_status = 'active'
          AND s.start_date <= p_reporting_date
          AND (
              s.end_date IS NULL
              OR s.end_date >= p_reporting_date
          )
    ),
    financial_data AS (
        SELECT *
        FROM monthly_financials mf
        WHERE mf.reporting_month = DATE_TRUNC(
            'month',
            p_reporting_date
        )::DATE
    ),
    base_metrics AS (
        SELECT
            p_reporting_date AS reporting_month,
            uc.total_users,
            pc.paying_users,
            calculate_mrr(p_reporting_date) AS mrr,
            COALESCE(fd.one_time_revenue, 0) AS one_time_revenue,
            COALESCE(fd.variable_cost, 0) AS variable_cost,
            COALESCE(fd.marketing_spend, 0) AS marketing_spend,
            COALESCE(fd.sales_spend, 0) AS sales_spend,
            COALESCE(fd.new_customers, 0) AS new_customers,
            fd.monthly_churn_rate
        FROM user_counts uc
        CROSS JOIN paying_counts pc
        LEFT JOIN financial_data fd ON TRUE
    ),
    economic_metrics AS (
        SELECT
            bm.*,
            (
                bm.mrr + bm.one_time_revenue
                - bm.variable_cost
            ) AS gross_profit,

            CASE
                WHEN bm.mrr + bm.one_time_revenue = 0
                THEN NULL
                ELSE (
                    bm.mrr + bm.one_time_revenue
                    - bm.variable_cost
                ) / (
                    bm.mrr + bm.one_time_revenue
                )
            END AS gross_margin,

            CASE
                WHEN bm.total_users = 0 THEN NULL
                ELSE bm.mrr / bm.total_users
            END AS arpu,

            CASE
                WHEN bm.paying_users = 0 THEN NULL
                ELSE bm.mrr / bm.paying_users
            END AS arppu,

            CASE
                WHEN bm.new_customers = 0 THEN NULL
                ELSE (
                    bm.marketing_spend + bm.sales_spend
                ) / bm.new_customers
            END AS cac
        FROM base_metrics bm
    ),
    lifetime_metrics AS (
        SELECT
            em.*,
            CASE
                WHEN em.monthly_churn_rate IS NULL
                  OR em.monthly_churn_rate = 0
                  OR em.arppu IS NULL
                  OR em.gross_margin IS NULL
                THEN NULL
                ELSE (
                    em.arppu
                    * em.gross_margin
                    / em.monthly_churn_rate
                )
            END AS ltv
        FROM economic_metrics em
    )
    SELECT
        lm.reporting_month,
        lm.total_users,
        lm.paying_users,
        ROUND(lm.arpu, 2),
        ROUND(lm.arppu, 2),
        ROUND(lm.mrr, 2),
        ROUND(lm.mrr * 12, 2),
        ROUND(lm.ltv, 2),
        ROUND(lm.cac, 2),
        ROUND(lm.gross_profit, 2),
        ROUND(lm.gross_margin, 4),
        ROUND(
            lm.ltv / NULLIF(lm.cac, 0),
            2
        ),
        ROUND(
            lm.cac / NULLIF(
                lm.arppu * lm.gross_margin,
                0
            ),
            2
        )
    FROM lifetime_metrics lm;
$$;

-- ------------------------------------------------------------
-- 9. METRICS REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW monetization_monthly_report AS
SELECT
    mf.reporting_month,
    mf.total_users,
    mf.paying_users,
    mf.new_customers,
    mf.churned_customers,
    mf.monthly_churn_rate,
    calculate_mrr(mf.reporting_month) AS mrr,
    calculate_mrr(mf.reporting_month) * 12 AS arr,
    mf.marketing_spend + mf.sales_spend AS acquisition_spend,
    mf.variable_cost,
    mf.fixed_cost,
    mf.one_time_revenue
FROM monthly_financials mf;

-- ------------------------------------------------------------
-- 10. DATA INTEGRITY TRIGGER
--
-- Prevents acquisition records from being dated after
-- the reporting month and invalidating the monthly population.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_customer_acquisition_date()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.acquisition_date > CURRENT_DATE THEN
        RAISE EXCEPTION
            'Customer acquisition date cannot be in the future.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_customer_acquisition_validation
ON customers;

CREATE TRIGGER trg_customer_acquisition_validation
BEFORE INSERT OR UPDATE OF acquisition_date
ON customers
FOR EACH ROW
EXECUTE FUNCTION validate_customer_acquisition_date();

-- ------------------------------------------------------------
-- 11. SUBSCRIPTION STATE VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_subscription_dates()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.end_date IS NOT NULL
       AND NEW.end_date < NEW.start_date THEN
        RAISE EXCEPTION
            'Subscription end date cannot precede start date.';
    END IF;

    IF NEW.subscription_status = 'cancelled'
       AND NEW.end_date IS NULL THEN
        NEW.end_date := CURRENT_DATE;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_subscription_date_validation
ON subscriptions;

CREATE TRIGGER trg_subscription_date_validation
BEFORE INSERT OR UPDATE
ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION validate_subscription_dates();

-- ------------------------------------------------------------
-- 12. ACQUISITION COHORT REPORT
--
-- Measures customers acquired during each calendar month.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW acquisition_cohort_report AS
SELECT
    DATE_TRUNC('month', acquisition_date)::DATE AS cohort_month,
    COUNT(*) AS acquired_customers,
    COUNT(*) FILTER (
        WHERE customer_status = 'active'
    ) AS currently_active_customers,
    COUNT(*) FILTER (
        WHERE customer_status = 'churned'
    ) AS churned_customers
FROM customers
GROUP BY DATE_TRUNC('month', acquisition_date)::DATE;

-- ------------------------------------------------------------
-- 13. MONETIZATION POLICY EVALUATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_monetization_policy(
    p_reporting_date DATE,
    p_minimum_ltv_cac NUMERIC DEFAULT 3.00,
    p_minimum_gross_margin NUMERIC DEFAULT 0.50
)
RETURNS TABLE (
    metric_name TEXT,
    metric_value NUMERIC,
    policy_threshold NUMERIC,
    policy_status TEXT
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        'LTV_CAC_RATIO',
        r.ltv_cac_ratio,
        p_minimum_ltv_cac,
        CASE
            WHEN r.ltv_cac_ratio IS NULL THEN 'UNAVAILABLE'
            WHEN r.ltv_cac_ratio >= p_minimum_ltv_cac THEN 'PASS'
            ELSE 'FAIL'
        END
    FROM calculate_monetization_metrics(p_reporting_date) r

    UNION ALL

    SELECT
        'GROSS_MARGIN',
        r.gross_margin,
        p_minimum_gross_margin,
        CASE
            WHEN r.gross_margin IS NULL THEN 'UNAVAILABLE'
            WHEN r.gross_margin >= p_minimum_gross_margin THEN 'PASS'
            ELSE 'FAIL'
        END
    FROM calculate_monetization_metrics(p_reporting_date) r;
$$;

-- ------------------------------------------------------------
-- 14. HISTORICAL MONTHLY RETRIEVAL
-- ------------------------------------------------------------

SELECT *
FROM monetization_monthly_report
ORDER BY reporting_month;

-- ------------------------------------------------------------
-- 15. COMPLETE FINANCIAL METRICS
-- ------------------------------------------------------------

SELECT *
FROM calculate_monetization_metrics(DATE '2026-11-01');

-- ------------------------------------------------------------
-- 16. POLICY EVALUATION
-- ------------------------------------------------------------

SELECT *
FROM evaluate_monetization_policy(
    DATE '2026-11-01',
    3.00,
    0.50
);

-- ------------------------------------------------------------
-- 17. COHORT PERFORMANCE
-- ------------------------------------------------------------

SELECT *
FROM acquisition_cohort_report
ORDER BY cohort_month;

-- ------------------------------------------------------------
-- 18. CUSTOMER-LEVEL SUBSCRIPTION RETRIEVAL
-- ------------------------------------------------------------

SELECT
    c.external_reference,
    c.customer_name,
    s.subscription_id,
    p.plan_name,
    s.agreed_price,
    p.billing_interval_months,
    ROUND(
        s.agreed_price / p.billing_interval_months,
        2
    ) AS normalized_mrr,
    s.subscription_status
FROM customers c
JOIN subscriptions s
    ON s.customer_id = c.customer_id
JOIN plans p
    ON p.plan_id = s.plan_id
ORDER BY c.customer_id;

-- ------------------------------------------------------------
-- 19. ACQUISITION AND RETENTION ANALYSIS
-- ------------------------------------------------------------

SELECT
    reporting_month,
    new_customers,
    churned_customers,
    ROUND(
        churned_customers::NUMERIC /
        NULLIF(total_users, 0),
        4
    ) AS approximate_churn_ratio,
    ROUND(
        (
            marketing_spend + sales_spend
        ) / NULLIF(new_customers, 0),
        2
    ) AS acquisition_cost_per_customer
FROM monthly_financials
ORDER BY reporting_month;

-- ------------------------------------------------------------
-- 20. TRANSACTIONAL SUBSCRIPTION UPDATE
--
-- The update is atomic. A failed operation rolls back.
-- ------------------------------------------------------------

BEGIN;

UPDATE subscriptions
SET subscription_status = 'cancelled',
    end_date = DATE '2026-11-30'
WHERE subscription_id = (
    SELECT MIN(subscription_id)
    FROM subscriptions
    WHERE subscription_status = 'active'
);

-- Verify state before committing.
SELECT
    subscription_id,
    subscription_status,
    end_date
FROM subscriptions
ORDER BY subscription_id;

COMMIT;

-- ------------------------------------------------------------
-- 21. DATA QUALITY VALIDATION
-- ------------------------------------------------------------

-- Customers without valid subscriptions.
SELECT c.customer_id, c.external_reference
FROM customers c
LEFT JOIN subscriptions s
    ON s.customer_id = c.customer_id
WHERE s.subscription_id IS NULL;

-- Active subscriptions belonging to inactive customers.
SELECT
    s.subscription_id,
    c.external_reference,
    c.customer_status
FROM subscriptions s
JOIN customers c
    ON c.customer_id = s.customer_id
WHERE s.subscription_status = 'active'
  AND c.customer_status <> 'active';

-- Financial records with missing churn information.
SELECT reporting_month
FROM monthly_financials
WHERE monthly_churn_rate IS NULL;

-- Duplicate monthly reporting periods are prevented
-- by the unique constraint on reporting_month.

-- ------------------------------------------------------------
-- END OF MONETIZATION DATABASE
-- ------------------------------------------------------------
