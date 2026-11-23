/*
===============================================================================
SAAS METRICS AND REVENUE ANALYTICS DATABASE
===============================================================================

PostgreSQL 15+

Business domains:
1. Subscription and customer management
2. Monthly recurring revenue movements
3. Churn, expansion and contraction
4. Net Revenue Retention
5. Gross Revenue Retention
6. Customer acquisition cost
7. CAC payback period
8. Cohort revenue retention
9. Metric reporting and eligibility validation

Revenue reconciliation:

Ending MRR =
    Starting MRR
    + New MRR
    + Expansion MRR
    - Contraction MRR
    - Churned MRR

NRR =
    (Starting MRR + Expansion MRR
     - Contraction MRR - Churned MRR)
    / Starting MRR * 100

GRR =
    (Starting MRR - Contraction MRR - Churned MRR)
    / Starting MRR * 100

===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS saas_analytics;

SET search_path TO saas_analytics, public;

-- ============================================================================
-- 1. DOMAIN TYPES
-- ============================================================================

CREATE TYPE subscription_status AS ENUM (
    'active',
    'churned',
    'suspended'
);

CREATE TYPE movement_type AS ENUM (
    'new_business',
    'expansion',
    'contraction',
    'churn',
    'unchanged'
);

CREATE TYPE acquisition_channel AS ENUM (
    'organic',
    'paid_search',
    'paid_social',
    'referral',
    'partner',
    'sales_outbound'
);

CREATE TYPE metric_status AS ENUM (
    'calculated',
    'insufficient_data',
    'validation_failed'
);

-- ============================================================================
-- 2. CORE ENTITIES
-- ============================================================================

CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_customer_id VARCHAR(100) NOT NULL UNIQUE,
    customer_name VARCHAR(200) NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    acquisition_date DATE NOT NULL,
    acquisition_channel acquisition_channel NOT NULL,
    country_code CHAR(2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_segment CHECK (
        customer_segment IN (
            'SMB',
            'MID_MARKET',
            'ENTERPRISE'
        )
    ),

    CONSTRAINT valid_external_id CHECK (
        LENGTH(TRIM(external_customer_id)) > 0
    )
);

CREATE TABLE subscription_plans (
    plan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL UNIQUE,
    billing_interval VARCHAR(20) NOT NULL,
    list_price NUMERIC(14,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_billing_interval CHECK (
        billing_interval IN ('monthly', 'annual')
    ),

    CONSTRAINT valid_plan_price CHECK (
        list_price >= 0
    )
);

CREATE TABLE subscriptions (
    subscription_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),
    plan_id BIGINT NOT NULL
        REFERENCES subscription_plans(plan_id),
    status subscription_status NOT NULL DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE,
    monthly_recurring_revenue NUMERIC(14,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_subscription_dates CHECK (
        end_date IS NULL OR end_date >= start_date
    ),

    CONSTRAINT valid_subscription_mrr CHECK (
        monthly_recurring_revenue >= 0
    )
);

CREATE INDEX idx_subscriptions_customer
    ON subscriptions(customer_id);

CREATE INDEX idx_subscriptions_status
    ON subscriptions(status);

-- ============================================================================
-- 3. MONTHLY REVENUE MOVEMENTS
-- ============================================================================

CREATE TABLE revenue_movements (
    movement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),

    reporting_period DATE NOT NULL,

    starting_mrr NUMERIC(14,2) NOT NULL,
    ending_mrr NUMERIC(14,2) NOT NULL,

    movement movement_type NOT NULL,

    new_mrr NUMERIC(14,2) NOT NULL DEFAULT 0,
    expansion_mrr NUMERIC(14,2) NOT NULL DEFAULT 0,
    contraction_mrr NUMERIC(14,2) NOT NULL DEFAULT 0,
    churned_mrr NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_reporting_period CHECK (
        EXTRACT(DAY FROM reporting_period) = 1
    ),

    CONSTRAINT valid_revenue_values CHECK (
        starting_mrr >= 0
        AND ending_mrr >= 0
        AND new_mrr >= 0
        AND expansion_mrr >= 0
        AND contraction_mrr >= 0
        AND churned_mrr >= 0
    ),

    CONSTRAINT one_customer_per_period UNIQUE (
        customer_id,
        reporting_period
    ),

    CONSTRAINT valid_movement_type CHECK (
        (
            starting_mrr = 0
            AND ending_mrr > 0
            AND movement = 'new_business'
            AND new_mrr = ending_mrr
            AND expansion_mrr = 0
            AND contraction_mrr = 0
            AND churned_mrr = 0
        )
        OR
        (
            starting_mrr > 0
            AND ending_mrr = 0
            AND movement = 'churn'
            AND new_mrr = 0
            AND expansion_mrr = 0
            AND contraction_mrr = 0
            AND churned_mrr = starting_mrr
        )
        OR
        (
            starting_mrr > 0
            AND ending_mrr > starting_mrr
            AND movement = 'expansion'
            AND new_mrr = 0
            AND expansion_mrr = ending_mrr - starting_mrr
            AND contraction_mrr = 0
            AND churned_mrr = 0
        )
        OR
        (
            starting_mrr > 0
            AND ending_mrr > 0
            AND ending_mrr < starting_mrr
            AND movement = 'contraction'
            AND new_mrr = 0
            AND expansion_mrr = 0
            AND contraction_mrr = starting_mrr - ending_mrr
            AND churned_mrr = 0
        )
        OR
        (
            starting_mrr = ending_mrr
            AND starting_mrr > 0
            AND movement = 'unchanged'
            AND new_mrr = 0
            AND expansion_mrr = 0
            AND contraction_mrr = 0
            AND churned_mrr = 0
        )
    )
);

CREATE INDEX idx_revenue_period
    ON revenue_movements(reporting_period);

CREATE INDEX idx_revenue_customer_period
    ON revenue_movements(customer_id, reporting_period);

CREATE INDEX idx_revenue_movement_type
    ON revenue_movements(movement, reporting_period);

-- ============================================================================
-- 4. CUSTOMER ACQUISITION COST
-- ============================================================================

CREATE TABLE acquisition_costs (
    acquisition_cost_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    reporting_period DATE NOT NULL,
    channel acquisition_channel NOT NULL,

    sales_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    marketing_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    new_customers INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_acquisition_period CHECK (
        EXTRACT(DAY FROM reporting_period) = 1
    ),

    CONSTRAINT valid_acquisition_cost CHECK (
        sales_cost >= 0
        AND marketing_cost >= 0
        AND new_customers >= 0
    ),

    CONSTRAINT unique_channel_period UNIQUE (
        reporting_period,
        channel
    )
);

CREATE INDEX idx_acquisition_period
    ON acquisition_costs(reporting_period);

-- ============================================================================
-- 5. GROSS MARGIN INPUT
-- ============================================================================

CREATE TABLE monthly_financials (
    financial_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    reporting_period DATE NOT NULL UNIQUE,

    revenue NUMERIC(14,2) NOT NULL,
    cost_of_revenue NUMERIC(14,2) NOT NULL,

    CONSTRAINT valid_financial_period CHECK (
        EXTRACT(DAY FROM reporting_period) = 1
    ),

    CONSTRAINT valid_financial_values CHECK (
        revenue >= 0
        AND cost_of_revenue >= 0
    )
);

-- ============================================================================
-- 6. AUTOMATIC MOVEMENT CLASSIFICATION
-- ============================================================================

CREATE OR REPLACE FUNCTION classify_revenue_movement()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.new_mrr := 0;
    NEW.expansion_mrr := 0;
    NEW.contraction_mrr := 0;
    NEW.churned_mrr := 0;

    IF NEW.starting_mrr = 0 AND NEW.ending_mrr > 0 THEN
        NEW.movement := 'new_business';
        NEW.new_mrr := NEW.ending_mrr;

    ELSIF NEW.starting_mrr > 0 AND NEW.ending_mrr = 0 THEN
        NEW.movement := 'churn';
        NEW.churned_mrr := NEW.starting_mrr;

    ELSIF NEW.ending_mrr > NEW.starting_mrr THEN
        NEW.movement := 'expansion';
        NEW.expansion_mrr :=
            NEW.ending_mrr - NEW.starting_mrr;

    ELSIF NEW.ending_mrr < NEW.starting_mrr THEN
        NEW.movement := 'contraction';
        NEW.contraction_mrr :=
            NEW.starting_mrr - NEW.ending_mrr;

    ELSE
        NEW.movement := 'unchanged';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_classify_revenue_movement
BEFORE INSERT OR UPDATE OF starting_mrr, ending_mrr
ON revenue_movements
FOR EACH ROW
EXECUTE FUNCTION classify_revenue_movement();

-- ============================================================================
-- 7. MONTHLY METRICS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW monthly_revenue_metrics AS

WITH aggregated AS (
    SELECT
        reporting_period,

        SUM(starting_mrr) AS starting_mrr,
        SUM(ending_mrr) AS ending_mrr,

        SUM(new_mrr) AS new_mrr,
        SUM(expansion_mrr) AS expansion_mrr,
        SUM(contraction_mrr) AS contraction_mrr,
        SUM(churned_mrr) AS churned_mrr,

        COUNT(*) FILTER (
            WHERE starting_mrr > 0
        ) AS starting_customers,

        COUNT(*) FILTER (
            WHERE ending_mrr > 0
        ) AS ending_customers,

        COUNT(*) FILTER (
            WHERE movement = 'churn'
        ) AS churned_customers,

        COUNT(*) FILTER (
            WHERE movement = 'new_business'
        ) AS new_customers

    FROM revenue_movements
    GROUP BY reporting_period
)

SELECT
    reporting_period,

    starting_mrr,
    ending_mrr,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churned_mrr,

    starting_customers,
    ending_customers,
    churned_customers,
    new_customers,

    CASE
        WHEN starting_mrr = 0 THEN NULL
        ELSE ROUND(
            (
                starting_mrr
                - churned_mrr
                - contraction_mrr
            ) / starting_mrr * 100,
            2
        )
    END AS grr_percentage,

    CASE
        WHEN starting_mrr = 0 THEN NULL
        ELSE ROUND(
            (
                starting_mrr
                - churned_mrr
                - contraction_mrr
                + expansion_mrr
            ) / starting_mrr * 100,
            2
        )
    END AS nrr_percentage,

    CASE
        WHEN starting_mrr = 0 THEN NULL
        ELSE ROUND(
            (
                churned_mrr + contraction_mrr
            ) / starting_mrr * 100,
            2
        )
    END AS revenue_churn_percentage,

    CASE
        WHEN starting_customers = 0 THEN NULL
        ELSE ROUND(
            churned_customers::NUMERIC
            / starting_customers * 100,
            2
        )
    END AS logo_churn_percentage,

    CASE
        WHEN starting_mrr = 0 THEN NULL
        ELSE ROUND(
            expansion_mrr / starting_mrr * 100,
            2
        )
    END AS expansion_percentage,

    CASE
        WHEN starting_mrr = 0 THEN NULL
        ELSE ROUND(
            (ending_mrr - starting_mrr)
            / starting_mrr * 100,
            2
        )
    END AS mrr_growth_percentage

FROM aggregated;

-- ============================================================================
-- 8. CAC VIEW
-- ============================================================================

CREATE OR REPLACE VIEW channel_cac AS

SELECT
    reporting_period,
    channel,

    SUM(sales_cost) AS sales_cost,
    SUM(marketing_cost) AS marketing_cost,

    SUM(sales_cost + marketing_cost) AS acquisition_cost,

    SUM(new_customers) AS new_customers,

    CASE
        WHEN SUM(new_customers) = 0 THEN NULL
        ELSE ROUND(
            SUM(sales_cost + marketing_cost)
            / SUM(new_customers),
            2
        )
    END AS cac

FROM acquisition_costs

GROUP BY reporting_period, channel;

CREATE OR REPLACE VIEW monthly_cac AS

SELECT
    reporting_period,

    SUM(sales_cost + marketing_cost) AS total_acquisition_cost,

    SUM(new_customers) AS new_customers,

    CASE
        WHEN SUM(new_customers) = 0 THEN NULL
        ELSE ROUND(
            SUM(sales_cost + marketing_cost)
            / SUM(new_customers),
            2
        )
    END AS cac

FROM acquisition_costs

GROUP BY reporting_period;

-- ============================================================================
-- 9. CAC PAYBACK VIEW
-- ============================================================================

CREATE OR REPLACE VIEW monthly_cac_payback AS

WITH acquisition AS (
    SELECT
        reporting_period,
        SUM(sales_cost + marketing_cost) AS total_cost,
        SUM(new_customers) AS new_customers

    FROM acquisition_costs
    GROUP BY reporting_period
),

financials AS (
    SELECT
        reporting_period,
        revenue,
        cost_of_revenue,

        CASE
            WHEN revenue = 0 THEN NULL
            ELSE (
                revenue - cost_of_revenue
            ) / revenue
        END AS gross_margin

    FROM monthly_financials
)

SELECT
    a.reporting_period,
    a.total_cost,
    a.new_customers,

    CASE
        WHEN a.new_customers = 0 THEN NULL
        ELSE ROUND(
            a.total_cost / a.new_customers,
            2
        )
    END AS cac,

    f.gross_margin,

    CASE
        WHEN a.new_customers = 0
            OR f.revenue = 0
            OR f.gross_margin <= 0
        THEN NULL

        ELSE ROUND(
            (
                a.total_cost / a.new_customers
            )
            /
            (
                (f.revenue / a.new_customers)
                * f.gross_margin
            ),
            2
        )
    END AS cac_payback_months

FROM acquisition a

LEFT JOIN financials f
    ON f.reporting_period = a.reporting_period;

-- ============================================================================
-- 10. COHORT RETENTION ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW customer_cohort_revenue AS

SELECT
    DATE_TRUNC(
        'month',
        c.acquisition_date
    )::DATE AS cohort_month,

    r.reporting_period,

    (
        (
            EXTRACT(YEAR FROM r.reporting_period)
            - EXTRACT(YEAR FROM
                DATE_TRUNC('month', c.acquisition_date)
            )
        ) * 12
        +
        (
            EXTRACT(MONTH FROM r.reporting_period)
            - EXTRACT(MONTH FROM
                DATE_TRUNC('month', c.acquisition_date)
            )
        )
    )::INTEGER AS cohort_age_month,

    SUM(r.ending_mrr) AS cohort_ending_mrr,

    COUNT(*) FILTER (
        WHERE r.ending_mrr > 0
    ) AS active_customers

FROM customers c

JOIN revenue_movements r
    ON r.customer_id = c.customer_id

GROUP BY
    DATE_TRUNC('month', c.acquisition_date)::DATE,
    r.reporting_period;

CREATE OR REPLACE VIEW cohort_revenue_retention AS

WITH cohort_baseline AS (
    SELECT
        cohort_month,
        SUM(cohort_ending_mrr) AS baseline_mrr

    FROM customer_cohort_revenue

    WHERE cohort_age_month = 0

    GROUP BY cohort_month
)

SELECT
    cr.cohort_month,
    cr.reporting_period,
    cr.cohort_age_month,

    cr.cohort_ending_mrr,
    cb.baseline_mrr,

    CASE
        WHEN cb.baseline_mrr = 0 THEN NULL
        ELSE ROUND(
            cr.cohort_ending_mrr
            / cb.baseline_mrr * 100,
            2
        )
    END AS cohort_revenue_retention_percentage,

    cr.active_customers

FROM customer_cohort_revenue cr

JOIN cohort_baseline cb
    ON cb.cohort_month = cr.cohort_month;

-- ============================================================================
-- 11. RECONCILIATION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_monthly_revenue(
    p_period DATE
)
RETURNS TABLE (
    period DATE,
    opening_mrr NUMERIC,
    calculated_closing_mrr NUMERIC,
    recorded_closing_mrr NUMERIC,
    reconciliation_valid BOOLEAN
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        reporting_period,

        starting_mrr,

        starting_mrr
            + new_mrr
            + expansion_mrr
            - contraction_mrr
            - churned_mrr,

        ending_mrr,

        (
            starting_mrr
            + new_mrr
            + expansion_mrr
            - contraction_mrr
            - churned_mrr
        ) = ending_mrr

    FROM monthly_revenue_metrics

    WHERE reporting_period = p_period;
$$;

-- ============================================================================
-- 12. METRIC ELIGIBILITY FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION evaluate_metric_eligibility(
    p_period DATE
)
RETURNS TABLE (
    reporting_period DATE,
    metric_name TEXT,
    metric_value NUMERIC,
    status metric_status,
    explanation TEXT
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        m.reporting_period,
        'NRR'::TEXT,
        m.nrr_percentage,
        CASE
            WHEN m.starting_mrr = 0
                THEN 'insufficient_data'::metric_status
            ELSE 'calculated'::metric_status
        END,
        CASE
            WHEN m.starting_mrr = 0
                THEN 'Opening MRR is zero'
            ELSE 'NRR calculated from opening customer revenue'
        END

    FROM monthly_revenue_metrics m

    WHERE m.reporting_period = p_period

    UNION ALL

    SELECT
        m.reporting_period,
        'GRR'::TEXT,
        m.grr_percentage,
        CASE
            WHEN m.starting_mrr = 0
                THEN 'insufficient_data'::metric_status
            ELSE 'calculated'::metric_status
        END,
        CASE
            WHEN m.starting_mrr = 0
                THEN 'Opening MRR is zero'
            ELSE 'GRR calculated without expansion revenue'
        END

    FROM monthly_revenue_metrics m

    WHERE m.reporting_period = p_period;
$$;

-- ============================================================================
-- 13. STORED PROCEDURE FOR MONTHLY REPORTING
-- ============================================================================

CREATE OR REPLACE PROCEDURE generate_monthly_report(
    p_period DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_metrics monthly_revenue_metrics%ROWTYPE;
BEGIN
    SELECT *
    INTO v_metrics

    FROM monthly_revenue_metrics

    WHERE reporting_period = p_period;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No revenue metrics found for %',
            p_period;
    END IF;

    IF v_metrics.starting_mrr = 0 THEN
        RAISE NOTICE
            'NRR and GRR unavailable for period %',
            p_period;
    END IF;

    RAISE NOTICE
        'Period: %, Starting MRR: %, Ending MRR: %, NRR: %, GRR: %',
        p_period,
        v_metrics.starting_mrr,
        v_metrics.ending_mrr,
        v_metrics.nrr_percentage,
        v_metrics.grr_percentage;
END;
$$;

-- ============================================================================
-- 14. SAMPLE MASTER DATA
-- ============================================================================

INSERT INTO subscription_plans (
    plan_name,
    billing_interval,
    list_price,
    currency
)
VALUES
    ('Starter', 'monthly', 100, 'USD'),
    ('Growth', 'monthly', 250, 'USD'),
    ('Enterprise', 'monthly', 1000, 'USD');

INSERT INTO customers (
    external_customer_id,
    customer_name,
    customer_segment,
    acquisition_date,
    acquisition_channel,
    country_code
)
VALUES
    ('EXT-001', 'Northstar Retail', 'SMB',
        '2026-01-15', 'organic', 'US'),

    ('EXT-002', 'Vertex Systems', 'MID_MARKET',
        '2026-02-10', 'paid_search', 'US'),

    ('EXT-003', 'Apex Technologies', 'ENTERPRISE',
        '2026-03-20', 'sales_outbound', 'IN'),

    ('EXT-004', 'Bluewave Consulting', 'SMB',
        '2026-04-12', 'referral', 'GB'),

    ('EXT-005', 'Quantum Logistics', 'MID_MARKET',
        '2026-10-05', 'partner', 'IN'),

    ('EXT-006', 'Orion Analytics', 'SMB',
        '2026-10-08', 'paid_social', 'US');

INSERT INTO subscriptions (
    customer_id,
    plan_id,
    status,
    start_date,
    monthly_recurring_revenue
)
SELECT
    c.customer_id,
    p.plan_id,
    'active',
    c.acquisition_date,
    CASE c.external_customer_id
        WHEN 'EXT-001' THEN 1200
        WHEN 'EXT-002' THEN 1500
        WHEN 'EXT-004' THEN 500
        WHEN 'EXT-005' THEN 1000
        WHEN 'EXT-006' THEN 800
        ELSE 0
    END

FROM customers c

JOIN subscription_plans p
    ON p.plan_name = CASE
        WHEN c.external_customer_id IN ('EXT-001', 'EXT-004')
            THEN 'Starter'
        WHEN c.external_customer_id IN ('EXT-002', 'EXT-005')
            THEN 'Growth'
        ELSE 'Enterprise'
    END;

-- ============================================================================
-- 15. SAMPLE REVENUE MOVEMENTS
-- ============================================================================

-- The trigger derives movement classification and MRR components.

INSERT INTO revenue_movements (
    customer_id,
    reporting_period,
    starting_mrr,
    ending_mrr
)
SELECT
    c.customer_id,
    DATE '2026-10-01',

    CASE c.external_customer_id
        WHEN 'EXT-001' THEN 1000
        WHEN 'EXT-002' THEN 2000
        WHEN 'EXT-003' THEN 1500
        WHEN 'EXT-004' THEN 500
        WHEN 'EXT-005' THEN 0
        WHEN 'EXT-006' THEN 0
    END,

    CASE c.external_customer_id
        WHEN 'EXT-001' THEN 1200
        WHEN 'EXT-002' THEN 1500
        WHEN 'EXT-003' THEN 0
        WHEN 'EXT-004' THEN 500
        WHEN 'EXT-005' THEN 1000
        WHEN 'EXT-006' THEN 800
    END

FROM customers c;

-- Expected movement distribution:
-- Expansion: C001, 200
-- Contraction: C002, 500
-- Churn: C003, 1500
-- Unchanged: C004
-- New business: C005, 1000
-- New business: C006, 800

-- Opening MRR = 5000
-- New MRR = 1800
-- Expansion MRR = 200
-- Contraction MRR = 500
-- Churned MRR = 1500
-- Ending MRR = 5000

-- NRR = 64%
-- GRR = 60%

-- ============================================================================
-- 16. ACQUISITION COST SAMPLE
-- ============================================================================

INSERT INTO acquisition_costs (
    reporting_period,
    channel,
    sales_cost,
    marketing_cost,
    new_customers
)
VALUES
    ('2026-10-01', 'partner', 3000, 2000, 1),
    ('2026-10-01', 'paid_social', 2000, 5000, 1);

INSERT INTO monthly_financials (
    reporting_period,
    revenue,
    cost_of_revenue
)
VALUES
    ('2026-10-01', 45000, 9000);

-- CAC = 12000 / 2 = 6000
-- Gross margin = (45000 - 9000) / 45000 = 80%
-- Average new customer MRR = 900
-- Monthly gross profit per new customer = 720
-- CAC payback = 6000 / 720 = 8.33 months

-- ============================================================================
-- 17. RETRIEVAL QUERIES
-- ============================================================================

-- Monthly revenue performance.
SELECT *
FROM monthly_revenue_metrics
ORDER BY reporting_period;

-- Customer-level movement details.
SELECT
    c.external_customer_id,
    c.customer_name,
    c.customer_segment,
    r.reporting_period,
    r.movement,
    r.starting_mrr,
    r.ending_mrr,
    r.new_mrr,
    r.expansion_mrr,
    r.contraction_mrr,
    r.churned_mrr

FROM revenue_movements r

JOIN customers c
    ON c.customer_id = r.customer_id

ORDER BY
    r.reporting_period,
    c.external_customer_id;

-- ============================================================================
-- 18. AGGREGATION AND CHANNEL EVALUATION
-- ============================================================================

SELECT *
FROM channel_cac
ORDER BY reporting_period, cac DESC NULLS LAST;

SELECT *
FROM monthly_cac
ORDER BY reporting_period;

SELECT *
FROM monthly_cac_payback
ORDER BY reporting_period;

-- Segment-level revenue performance.
SELECT
    c.customer_segment,
    r.reporting_period,

    SUM(r.starting_mrr) AS starting_mrr,
    SUM(r.ending_mrr) AS ending_mrr,
    SUM(r.expansion_mrr) AS expansion_mrr,
    SUM(r.contraction_mrr) AS contraction_mrr,
    SUM(r.churned_mrr) AS churned_mrr,

    CASE
        WHEN SUM(r.starting_mrr) = 0 THEN NULL
        ELSE ROUND(
            (
                SUM(r.starting_mrr)
                - SUM(r.churned_mrr)
                - SUM(r.contraction_mrr)
                + SUM(r.expansion_mrr)
            ) / SUM(r.starting_mrr) * 100,
            2
        )
    END AS segment_nrr

FROM revenue_movements r

JOIN customers c
    ON c.customer_id = r.customer_id

GROUP BY
    c.customer_segment,
    r.reporting_period

ORDER BY
    r.reporting_period,
    c.customer_segment;

-- ============================================================================
-- 19. COHORT REPORTING
-- ============================================================================

SELECT *
FROM cohort_revenue_retention
ORDER BY cohort_month, cohort_age_month;

-- ============================================================================
-- 20. VALIDATION AND ELIGIBILITY
-- ============================================================================

SELECT *
FROM validate_monthly_revenue(DATE '2026-10-01');

SELECT *
FROM evaluate_metric_eligibility(DATE '2026-10-01');

-- ============================================================================
-- 21. CTE-BASED EXECUTIVE PERFORMANCE REPORT
-- ============================================================================

WITH monthly AS (
    SELECT *
    FROM monthly_revenue_metrics
),

acquisition AS (
    SELECT *
    FROM monthly_cac
),

payback AS (
    SELECT *
    FROM monthly_cac_payback
)

SELECT
    m.reporting_period,

    m.starting_mrr,
    m.ending_mrr,

    m.nrr_percentage,
    m.grr_percentage,

    m.logo_churn_percentage,
    m.revenue_churn_percentage,

    a.cac,

    p.cac_payback_months,

    CASE
        WHEN m.nrr_percentage >= 110
            THEN 'STRONG_EXPANSION'

        WHEN m.nrr_percentage >= 100
            THEN 'REVENUE_STABLE'

        WHEN m.nrr_percentage >= 90
            THEN 'MODERATE_CONTRACTION'

        ELSE 'HIGH_REVENUE_RISK'
    END AS retention_assessment

FROM monthly m

LEFT JOIN acquisition a
    ON a.reporting_period = m.reporting_period

LEFT JOIN payback p
    ON p.reporting_period = m.reporting_period

ORDER BY m.reporting_period;

-- ============================================================================
-- 22. STORED PROCEDURE EXECUTION
-- ============================================================================

CALL generate_monthly_report(DATE '2026-10-01');

COMMIT;

-- ============================================================================
-- 23. OPERATIONAL NOTES
-- ============================================================================
--
-- 1. Reporting periods represent the first day of a calendar month.
-- 2. All MRR amounts in a reporting period must use a consistent currency.
-- 3. Annual subscription amounts must be normalized to monthly recurring
--    revenue before insertion.
-- 4. Revenue movements must represent opening and closing recurring revenue.
-- 5. The movement trigger classifies revenue changes automatically.
-- 6. GRR excludes expansion revenue.
-- 7. NRR includes expansion revenue.
-- 8. CAC must use a consistent acquisition-cost attribution policy.
-- 9. CAC payback uses monthly gross profit, not total revenue.
-- 10. The CAC payback view assumes the monthly reporting period's average
--     revenue per acquired customer is a reasonable proxy for new-customer
--     MRR. A production system should store new-customer cohort MRR directly.
-- 11. Cohort retention uses acquisition-month MRR as its baseline.
-- 12. A cohort's revenue retention can exceed 100% through expansion.
-- 13. A missing baseline is not interpreted as zero retention.
-- 14. Production ingestion should be idempotent and transactionally controlled.
-- 15. Currency conversion, refunds, taxes, credits, usage revenue and
--     non-recurring charges require explicit accounting policies.
-- 16. Restrict application roles to appropriate tables and views.
-- 17. Do not expose customer-level revenue records through public reporting.
--
-- ============================================================================
