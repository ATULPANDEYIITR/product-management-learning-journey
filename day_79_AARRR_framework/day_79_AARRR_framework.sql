/*
==============================================================================
AARRR FRAMEWORK: ENTERPRISE PRODUCT GROWTH ANALYTICS
==============================================================================
PostgreSQL 15+

Five growth stages:
1. Acquisition
2. Activation
3. Retention
4. Revenue
5. Referral

Database capabilities:
- Relational customer and event model
- Acquisition source attribution
- Activation qualification
- Daily activity and cohort retention
- Revenue transactions
- Referral attribution
- Configurable growth policies
- Event idempotency
- Transactional event processing
- Reporting views
- Conversion calculations
- Operational indexes
- Audit history

Monetary amounts use NUMERIC rather than floating-point arithmetic.
==============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS aarrr;

SET search_path TO aarrr, public;

-- ---------------------------------------------------------------------------
-- DOMAIN TYPES
-- ---------------------------------------------------------------------------

CREATE TYPE aarrr.growth_stage AS ENUM (
    'acquisition',
    'activation',
    'retention',
    'revenue',
    'referral'
);

CREATE TYPE aarrr.event_type AS ENUM (
    'visit',
    'signup',
    'activation',
    'login',
    'purchase',
    'subscription',
    'referral_sent',
    'cancellation'
);

CREATE TYPE aarrr.customer_status AS ENUM (
    'registered',
    'activated',
    'paying',
    'cancelled'
);

CREATE TYPE aarrr.event_status AS ENUM (
    'accepted',
    'rejected'
);

-- ---------------------------------------------------------------------------
-- ACQUISITION SOURCES
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.acquisition_sources (
    source_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_code VARCHAR(60) NOT NULL UNIQUE,
    source_name VARCHAR(120) NOT NULL,
    source_type VARCHAR(40) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_source_code
        CHECK (source_code ~ '^[a-z0-9_-]+$')
);

-- ---------------------------------------------------------------------------
-- CUSTOMERS
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_user_id VARCHAR(100) NOT NULL UNIQUE,
    source_id BIGINT NOT NULL
        REFERENCES aarrr.acquisition_sources(source_id),
    referred_by BIGINT
        REFERENCES aarrr.customers(customer_id),
    signup_at TIMESTAMPTZ NOT NULL,
    activation_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT no_self_referral
        CHECK (
            referred_by IS NULL OR
            referred_by <> customer_id
        ),

    CONSTRAINT valid_activation_date
        CHECK (
            activation_at IS NULL OR
            activation_at >= signup_at
        ),

    CONSTRAINT valid_activity_date
        CHECK (
            last_activity_at IS NULL OR
            last_activity_at >= signup_at
        ),

    CONSTRAINT valid_cancellation_date
        CHECK (
            cancelled_at IS NULL OR
            cancelled_at >= signup_at
        )
);

CREATE INDEX idx_customers_source
    ON aarrr.customers(source_id);

CREATE INDEX idx_customers_signup_date
    ON aarrr.customers(signup_at);

CREATE INDEX idx_customers_referrer
    ON aarrr.customers(referred_by)
    WHERE referred_by IS NOT NULL;

CREATE INDEX idx_customers_activation
    ON aarrr.customers(activation_at)
    WHERE activation_at IS NOT NULL;

-- ---------------------------------------------------------------------------
-- GROWTH POLICIES
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.growth_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL,
    activation_window_days INTEGER NOT NULL DEFAULT 7,
    purchase_requires_activation BOOLEAN NOT NULL DEFAULT TRUE,
    referral_requires_activation BOOLEAN NOT NULL DEFAULT TRUE,
    maximum_transaction_amount NUMERIC(14,2) NOT NULL DEFAULT 1000000,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_until TIMESTAMPTZ,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_activation_window
        CHECK (activation_window_days >= 0),

    CONSTRAINT valid_maximum_amount
        CHECK (maximum_transaction_amount > 0),

    CONSTRAINT valid_policy_period
        CHECK (
            effective_until IS NULL OR
            effective_until > effective_from
        )
);

CREATE UNIQUE INDEX idx_one_active_growth_policy
    ON aarrr.growth_policies(active)
    WHERE active = TRUE;

-- ---------------------------------------------------------------------------
-- GROWTH EVENTS
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.growth_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    customer_id BIGINT
        REFERENCES aarrr.customers(customer_id),
    external_user_id VARCHAR(100) NOT NULL,
    event_type aarrr.event_type NOT NULL,
    event_at TIMESTAMPTZ NOT NULL,
    source_id BIGINT
        REFERENCES aarrr.acquisition_sources(source_id),
    amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    properties JSONB NOT NULL DEFAULT '{}'::JSONB,
    status aarrr.event_status NOT NULL DEFAULT 'accepted',
    rejection_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT nonnegative_event_amount
        CHECK (amount >= 0),

    CONSTRAINT valid_event_properties
        CHECK (jsonb_typeof(properties) = 'object'),

    CONSTRAINT valid_event_rejection
        CHECK (
            (status = 'accepted' AND rejection_reason IS NULL)
            OR
            (status = 'rejected' AND rejection_reason IS NOT NULL)
        )
);

CREATE INDEX idx_events_customer_time
    ON aarrr.growth_events(customer_id, event_at DESC);

CREATE INDEX idx_events_type_time
    ON aarrr.growth_events(event_type, event_at);

CREATE INDEX idx_events_external_user
    ON aarrr.growth_events(external_user_id);

CREATE INDEX idx_events_properties
    ON aarrr.growth_events USING GIN(properties);

-- ---------------------------------------------------------------------------
-- DAILY CUSTOMER ACTIVITY
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.daily_activity (
    customer_id BIGINT NOT NULL
        REFERENCES aarrr.customers(customer_id),
    activity_date DATE NOT NULL,
    login_count INTEGER NOT NULL DEFAULT 1,
    last_login_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY(customer_id, activity_date),

    CONSTRAINT positive_login_count
        CHECK (login_count > 0)
);

CREATE INDEX idx_activity_date
    ON aarrr.daily_activity(activity_date);

-- ---------------------------------------------------------------------------
-- REVENUE TRANSACTIONS
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.revenue_transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL
        REFERENCES aarrr.customers(customer_id),
    event_id BIGINT UNIQUE
        REFERENCES aarrr.growth_events(event_id),
    transaction_reference VARCHAR(100) NOT NULL UNIQUE,
    transaction_type VARCHAR(30) NOT NULL,
    amount NUMERIC(14,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    transaction_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT positive_revenue
        CHECK (amount > 0),

    CONSTRAINT valid_transaction_type
        CHECK (
            transaction_type IN ('purchase', 'subscription')
        ),

    CONSTRAINT valid_currency
        CHECK (currency ~ '^[A-Z]{3}$')
);

CREATE INDEX idx_revenue_customer_date
    ON aarrr.revenue_transactions(customer_id, transaction_at);

CREATE INDEX idx_revenue_transaction_date
    ON aarrr.revenue_transactions(transaction_at);

-- ---------------------------------------------------------------------------
-- REFERRAL ATTRIBUTION
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.referrals (
    referral_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    referrer_id BIGINT NOT NULL
        REFERENCES aarrr.customers(customer_id),
    referred_customer_id BIGINT NOT NULL UNIQUE
        REFERENCES aarrr.customers(customer_id),
    referral_code VARCHAR(80) NOT NULL UNIQUE,
    sent_at TIMESTAMPTZ NOT NULL,
    converted_at TIMESTAMPTZ,
    reward_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    reward_currency CHAR(3) NOT NULL DEFAULT 'INR',

    CONSTRAINT no_referral_loop
        CHECK (referrer_id <> referred_customer_id),

    CONSTRAINT valid_referral_conversion
        CHECK (
            converted_at IS NULL OR converted_at >= sent_at
        ),

    CONSTRAINT valid_referral_reward
        CHECK (reward_amount >= 0)
);

CREATE INDEX idx_referrals_referrer
    ON aarrr.referrals(referrer_id);

-- ---------------------------------------------------------------------------
-- EXPERIMENTS
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_name VARCHAR(150) NOT NULL UNIQUE,
    target_stage aarrr.growth_stage NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'running',

    CONSTRAINT valid_experiment_period
        CHECK (end_date IS NULL OR end_date >= start_date),

    CONSTRAINT valid_experiment_status
        CHECK (status IN ('draft', 'running', 'completed', 'cancelled'))
);

CREATE TABLE aarrr.experiment_assignments (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES aarrr.experiments(experiment_id),
    customer_id BIGINT NOT NULL
        REFERENCES aarrr.customers(customer_id),
    variant VARCHAR(30) NOT NULL,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(experiment_id, customer_id),

    CONSTRAINT valid_variant
        CHECK (variant IN ('control', 'treatment'))
);

CREATE INDEX idx_experiment_assignments_variant
    ON aarrr.experiment_assignments(experiment_id, variant);

-- ---------------------------------------------------------------------------
-- EVENT AUDIT
-- ---------------------------------------------------------------------------

CREATE TABLE aarrr.event_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_uuid UUID NOT NULL,
    action VARCHAR(30) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::JSONB,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- ACTIVE POLICY RETRIEVAL
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION aarrr.get_active_policy()
RETURNS aarrr.growth_policies
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    selected_policy aarrr.growth_policies%ROWTYPE;
BEGIN
    SELECT *
    INTO selected_policy
    FROM aarrr.growth_policies
    WHERE active = TRUE
      AND effective_from <= NOW()
      AND (
          effective_until IS NULL OR
          effective_until > NOW()
      )
    ORDER BY effective_from DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No active growth policy exists.';
    END IF;

    RETURN selected_policy;
END;
$$;

-- ---------------------------------------------------------------------------
-- CUSTOMER STATUS FUNCTION
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION aarrr.customer_current_status(
    p_customer_id BIGINT
)
RETURNS aarrr.customer_status
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    customer_row aarrr.customers%ROWTYPE;
BEGIN
    SELECT *
    INTO customer_row
    FROM aarrr.customers
    WHERE customer_id = p_customer_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Customer % not found.', p_customer_id;
    END IF;

    IF customer_row.cancelled_at IS NOT NULL THEN
        RETURN 'cancelled';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM aarrr.revenue_transactions
        WHERE customer_id = p_customer_id
    ) THEN
        RETURN 'paying';
    END IF;

    IF customer_row.activation_at IS NOT NULL THEN
        RETURN 'activated';
    END IF;

    RETURN 'registered';
END;
$$;

-- ---------------------------------------------------------------------------
-- EVENT PROCESSING PROCEDURE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE aarrr.process_growth_event(
    p_event_uuid UUID,
    p_external_user_id VARCHAR(100),
    p_event_type aarrr.event_type,
    p_event_at TIMESTAMPTZ,
    p_source_code VARCHAR(60) DEFAULT NULL,
    p_referrer_external_id VARCHAR(100) DEFAULT NULL,
    p_amount NUMERIC(14,2) DEFAULT 0,
    p_transaction_reference VARCHAR(100) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_customer_id BIGINT;
    v_referrer_id BIGINT;
    v_source_id BIGINT;
    v_policy aarrr.growth_policies%ROWTYPE;
    v_signup_at TIMESTAMPTZ;
    v_activation_at TIMESTAMPTZ;
    v_existing_event BIGINT;
BEGIN
    IF p_event_uuid IS NULL OR
       p_external_user_id IS NULL OR
       LENGTH(TRIM(p_external_user_id)) = 0 THEN
        RAISE EXCEPTION 'Event identifier and user ID are required.';
    END IF;

    IF p_event_at IS NULL OR p_event_at > NOW() + INTERVAL '1 day' THEN
        RAISE EXCEPTION 'Invalid event timestamp.';
    END IF;

    IF p_amount IS NULL OR p_amount < 0 THEN
        RAISE EXCEPTION 'Invalid event amount.';
    END IF;

    -- Idempotency check: the UUID is a unique ingestion key.
    PERFORM pg_advisory_xact_lock(
        hashtextextended(p_event_uuid::TEXT, 0)
    );

    SELECT event_id
    INTO v_existing_event
    FROM aarrr.growth_events
    WHERE event_uuid = p_event_uuid;

    IF FOUND THEN
        RAISE EXCEPTION 'Duplicate event UUID: %', p_event_uuid;
    END IF;

    IF p_event_type IN ('visit', 'signup') THEN
        SELECT source_id
        INTO v_source_id
        FROM aarrr.acquisition_sources
        WHERE source_code = p_source_code
          AND active = TRUE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Unknown or inactive acquisition source.';
        END IF;
    END IF;

    IF p_event_type = 'visit' THEN
        INSERT INTO aarrr.growth_events (
            event_uuid,
            external_user_id,
            event_type,
            event_at,
            source_id,
            amount
        )
        VALUES (
            p_event_uuid,
            p_external_user_id,
            p_event_type,
            p_event_at,
            v_source_id,
            0
        );

        RETURN;
    END IF;

    IF p_event_type = 'signup' THEN
        IF EXISTS (
            SELECT 1
            FROM aarrr.customers
            WHERE external_user_id = p_external_user_id
        ) THEN
            RAISE EXCEPTION 'Customer already registered.';
        END IF;

        IF p_referrer_external_id IS NOT NULL THEN
            SELECT customer_id
            INTO v_referrer_id
            FROM aarrr.customers
            WHERE external_user_id = p_referrer_external_id;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Referrer does not exist.';
            END IF;
        END IF;

        INSERT INTO aarrr.customers (
            external_user_id,
            source_id,
            referred_by,
            signup_at
        )
        VALUES (
            p_external_user_id,
            v_source_id,
            v_referrer_id,
            p_event_at
        )
        RETURNING customer_id INTO v_customer_id;

        INSERT INTO aarrr.growth_events (
            event_uuid,
            customer_id,
            external_user_id,
            event_type,
            event_at,
            source_id
        )
        VALUES (
            p_event_uuid,
            v_customer_id,
            p_external_user_id,
            p_event_type,
            p_event_at,
            v_source_id
        );

        RETURN;
    END IF;

    SELECT customer_id, signup_at, activation_at
    INTO v_customer_id, v_signup_at, v_activation_at
    FROM aarrr.customers
    WHERE external_user_id = p_external_user_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Customer must register before this event.';
    END IF;

    IF p_event_at < v_signup_at THEN
        RAISE EXCEPTION 'Event predates customer registration.';
    END IF;

    v_policy := aarrr.get_active_policy();

    CASE p_event_type

        WHEN 'activation' THEN
            IF v_activation_at IS NOT NULL THEN
                RAISE EXCEPTION 'Customer is already activated.';
            END IF;

            IF p_event_at >
               v_signup_at +
               make_interval(days => v_policy.activation_window_days) THEN
                RAISE EXCEPTION 'Activation window exceeded.';
            END IF;

            UPDATE aarrr.customers
            SET activation_at = p_event_at
            WHERE customer_id = v_customer_id;

        WHEN 'login' THEN
            INSERT INTO aarrr.daily_activity (
                customer_id,
                activity_date,
                login_count,
                last_login_at
            )
            VALUES (
                v_customer_id,
                p_event_at::DATE,
                1,
                p_event_at
            )
            ON CONFLICT (customer_id, activity_date)
            DO UPDATE SET
                login_count = aarrr.daily_activity.login_count + 1,
                last_login_at = GREATEST(
                    aarrr.daily_activity.last_login_at,
                    EXCLUDED.last_login_at
                );

            UPDATE aarrr.customers
            SET last_activity_at = GREATEST(
                COALESCE(last_activity_at, p_event_at),
                p_event_at
            )
            WHERE customer_id = v_customer_id;

        WHEN 'purchase', 'subscription' THEN
            IF v_policy.purchase_requires_activation
               AND v_activation_at IS NULL THEN
                RAISE EXCEPTION 'Activation required before purchase.';
            END IF;

            IF p_amount <= 0 OR
               p_amount > v_policy.maximum_transaction_amount THEN
                RAISE EXCEPTION 'Transaction violates amount policy.';
            END IF;

            IF p_transaction_reference IS NULL THEN
                RAISE EXCEPTION 'Transaction reference is required.';
            END IF;

        WHEN 'referral_sent' THEN
            IF v_policy.referral_requires_activation
               AND v_activation_at IS NULL THEN
                RAISE EXCEPTION 'Activation required before referral.';
            END IF;

        WHEN 'cancellation' THEN
            UPDATE aarrr.customers
            SET cancelled_at = p_event_at
            WHERE customer_id = v_customer_id;

        ELSE
            RAISE EXCEPTION 'Unsupported event transition.';
    END CASE;

    INSERT INTO aarrr.growth_events (
        event_uuid,
        customer_id,
        external_user_id,
        event_type,
        event_at,
        amount
    )
    VALUES (
        p_event_uuid,
        v_customer_id,
        p_external_user_id,
        p_event_type,
        p_event_at,
        p_amount
    );

    IF p_event_type IN ('purchase', 'subscription') THEN
        INSERT INTO aarrr.revenue_transactions (
            customer_id,
            event_id,
            transaction_reference,
            transaction_type,
            amount,
            transaction_at
        )
        SELECT
            v_customer_id,
            event_id,
            p_transaction_reference,
            p_event_type::TEXT,
            p_amount,
            p_event_at
        FROM aarrr.growth_events
        WHERE event_uuid = p_event_uuid;
    END IF;

    IF p_event_type = 'referral_sent' THEN
        INSERT INTO aarrr.event_audit (
            event_uuid,
            action,
            details
        )
        VALUES (
            p_event_uuid,
            'referral_recorded',
            jsonb_build_object(
                'customer_id', v_customer_id
            )
        );
    END IF;
END;
$$;

-- ---------------------------------------------------------------------------
-- REFERRAL CONVERSION FUNCTION
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION aarrr.register_referral_conversion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.referred_by IS NOT NULL THEN
        INSERT INTO aarrr.referrals (
            referrer_id,
            referred_customer_id,
            referral_code,
            sent_at,
            converted_at
        )
        VALUES (
            NEW.referred_by,
            NEW.customer_id,
            'REF-' || NEW.customer_id::TEXT,
            NEW.signup_at,
            NEW.signup_at
        )
        ON CONFLICT (referred_customer_id) DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_customer_referral_conversion
AFTER INSERT ON aarrr.customers
FOR EACH ROW
EXECUTE FUNCTION aarrr.register_referral_conversion();

-- ---------------------------------------------------------------------------
-- CUSTOMER STATE REPORT
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_customer_growth_status AS
SELECT
    c.customer_id,
    c.external_user_id,
    s.source_code,
    c.signup_at,
    c.activation_at,
    c.last_activity_at,
    c.cancelled_at,
    CASE
        WHEN c.cancelled_at IS NOT NULL THEN 'cancelled'
        WHEN EXISTS (
            SELECT 1
            FROM aarrr.revenue_transactions r
            WHERE r.customer_id = c.customer_id
        ) THEN 'paying'
        WHEN c.activation_at IS NOT NULL THEN 'activated'
        ELSE 'registered'
    END AS customer_status,
    COALESCE(revenue.total_revenue, 0) AS lifetime_revenue
FROM aarrr.customers c
JOIN aarrr.acquisition_sources s
    ON s.source_id = c.source_id
LEFT JOIN LATERAL (
    SELECT SUM(amount) AS total_revenue
    FROM aarrr.revenue_transactions
    WHERE customer_id = c.customer_id
) revenue ON TRUE;

-- ---------------------------------------------------------------------------
-- ACQUISITION PERFORMANCE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_acquisition_performance AS
WITH visitors AS (
    SELECT
        source_id,
        COUNT(DISTINCT external_user_id) AS visitor_count
    FROM aarrr.growth_events
    WHERE event_type = 'visit'
      AND status = 'accepted'
    GROUP BY source_id
),
signups AS (
    SELECT
        source_id,
        COUNT(*) AS signup_count
    FROM aarrr.customers
    GROUP BY source_id
)
SELECT
    s.source_code,
    s.source_name,
    COALESCE(v.visitor_count, 0) AS visitors,
    COALESCE(g.signup_count, 0) AS signups,
    ROUND(
        100.0 * COALESCE(g.signup_count, 0) /
        NULLIF(v.visitor_count, 0),
        2
    ) AS visitor_to_signup_pct
FROM aarrr.acquisition_sources s
LEFT JOIN visitors v ON v.source_id = s.source_id
LEFT JOIN signups g ON g.source_id = s.source_id;

-- ---------------------------------------------------------------------------
-- ACTIVATION PERFORMANCE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_activation_performance AS
SELECT
    COUNT(*) AS registered_users,
    COUNT(*) FILTER (
        WHERE activation_at IS NOT NULL
    ) AS activated_users,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE activation_at IS NOT NULL
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS activation_rate_pct
FROM aarrr.customers;

-- ---------------------------------------------------------------------------
-- RETENTION COHORT REPORT
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_retention_cohorts AS
WITH cohort_activity AS (
    SELECT
        c.customer_id,
        c.signup_at::DATE AS cohort_date,
        MIN(a.activity_date) AS first_activity_date
    FROM aarrr.customers c
    LEFT JOIN aarrr.daily_activity a
        ON a.customer_id = c.customer_id
       AND a.activity_date > c.signup_at::DATE
       AND a.activity_date <= c.signup_at::DATE + 7
    GROUP BY c.customer_id, c.signup_at
)
SELECT
    cohort_date,
    COUNT(*) AS cohort_size,
    COUNT(*) FILTER (
        WHERE first_activity_date IS NOT NULL
    ) AS retained_users,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE first_activity_date IS NOT NULL
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS retention_rate_pct
FROM cohort_activity
GROUP BY cohort_date;

-- ---------------------------------------------------------------------------
-- REVENUE REPORT
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_revenue_performance AS
SELECT
    COUNT(DISTINCT customer_id) AS paying_customers,
    COUNT(*) AS transaction_count,
    COALESCE(SUM(amount), 0)::NUMERIC(14,2) AS total_revenue,
    ROUND(
        COALESCE(SUM(amount), 0) /
        NULLIF(COUNT(DISTINCT customer_id), 0),
        2
    ) AS arppu
FROM aarrr.revenue_transactions;

CREATE OR REPLACE VIEW aarrr.v_customer_revenue AS
SELECT
    c.customer_id,
    c.external_user_id,
    COUNT(r.transaction_id) AS transaction_count,
    COALESCE(SUM(r.amount), 0)::NUMERIC(14,2) AS lifetime_revenue
FROM aarrr.customers c
LEFT JOIN aarrr.revenue_transactions r
    ON r.customer_id = c.customer_id
GROUP BY c.customer_id, c.external_user_id;

-- ---------------------------------------------------------------------------
-- REFERRAL PERFORMANCE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_referral_performance AS
SELECT
    c.external_user_id AS referrer,
    COUNT(r.referral_id) AS referred_signups,
    COALESCE(SUM(r.reward_amount), 0)::NUMERIC(14,2)
        AS referral_rewards
FROM aarrr.customers c
LEFT JOIN aarrr.referrals r
    ON r.referrer_id = c.customer_id
GROUP BY c.customer_id, c.external_user_id;

-- ---------------------------------------------------------------------------
-- COMPLETE FUNNEL REPORT
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_aarrr_funnel AS
WITH metrics AS (
    SELECT
        (
            SELECT COUNT(DISTINCT external_user_id)
            FROM aarrr.growth_events
            WHERE event_type = 'visit'
              AND status = 'accepted'
        ) AS visitors,

        (
            SELECT COUNT(*)
            FROM aarrr.customers
        ) AS signups,

        (
            SELECT COUNT(*)
            FROM aarrr.customers
            WHERE activation_at IS NOT NULL
        ) AS activated,

        (
            SELECT COUNT(DISTINCT customer_id)
            FROM aarrr.daily_activity
        ) AS retained,

        (
            SELECT COUNT(DISTINCT customer_id)
            FROM aarrr.revenue_transactions
        ) AS paying,

        (
            SELECT COUNT(*)
            FROM aarrr.referrals
        ) AS referred
)
SELECT
    visitors,
    signups,
    activated,
    retained,
    paying,
    referred,

    ROUND(100.0 * signups / NULLIF(visitors, 0), 2)
        AS acquisition_rate_pct,

    ROUND(100.0 * activated / NULLIF(signups, 0), 2)
        AS activation_rate_pct,

    ROUND(100.0 * retained / NULLIF(activated, 0), 2)
        AS retention_proxy_pct,

    ROUND(100.0 * paying / NULLIF(activated, 0), 2)
        AS revenue_conversion_pct,

    ROUND(100.0 * referred / NULLIF(activated, 0), 2)
        AS referral_rate_pct
FROM metrics;

-- ---------------------------------------------------------------------------
-- EXPERIMENT PERFORMANCE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW aarrr.v_experiment_performance AS
SELECT
    e.experiment_name,
    e.target_stage,
    a.variant,
    COUNT(*) AS assigned_users,
    COUNT(*) FILTER (
        WHERE
            CASE e.target_stage
                WHEN 'acquisition' THEN c.customer_id IS NOT NULL
                WHEN 'activation' THEN c.activation_at IS NOT NULL
                WHEN 'retention' THEN EXISTS (
                    SELECT 1
                    FROM aarrr.daily_activity da
                    WHERE da.customer_id = c.customer_id
                )
                WHEN 'revenue' THEN EXISTS (
                    SELECT 1
                    FROM aarrr.revenue_transactions rt
                    WHERE rt.customer_id = c.customer_id
                )
                WHEN 'referral' THEN EXISTS (
                    SELECT 1
                    FROM aarrr.referrals r
                    WHERE r.referrer_id = c.customer_id
                )
            END
    ) AS converted_users,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE
                CASE e.target_stage
                    WHEN 'acquisition' THEN c.customer_id IS NOT NULL
                    WHEN 'activation' THEN c.activation_at IS NOT NULL
                    WHEN 'retention' THEN EXISTS (
                        SELECT 1
                        FROM aarrr.daily_activity da
                        WHERE da.customer_id = c.customer_id
                    )
                    WHEN 'revenue' THEN EXISTS (
                        SELECT 1
                        FROM aarrr.revenue_transactions rt
                        WHERE rt.customer_id = c.customer_id
                    )
                    WHEN 'referral' THEN EXISTS (
                        SELECT 1
                        FROM aarrr.referrals r
                        WHERE r.referrer_id = c.customer_id
                    )
                END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct
FROM aarrr.experiment_assignments a
JOIN aarrr.experiments e
    ON e.experiment_id = a.experiment_id
JOIN aarrr.customers c
    ON c.customer_id = a.customer_id
GROUP BY e.experiment_name, e.target_stage, a.variant;

-- ---------------------------------------------------------------------------
-- SAMPLE DATA
-- ---------------------------------------------------------------------------

INSERT INTO aarrr.acquisition_sources (
    source_code, source_name, source_type
)
VALUES
    ('organic', 'Organic Search', 'organic'),
    ('paid', 'Paid Advertising', 'paid'),
    ('social', 'Social Media', 'social'),
    ('referral', 'Customer Referral', 'referral')
ON CONFLICT (source_code) DO NOTHING;

INSERT INTO aarrr.growth_policies (
    policy_name,
    activation_window_days,
    purchase_requires_activation,
    referral_requires_activation,
    maximum_transaction_amount,
    active
)
VALUES (
    'Standard Product Growth Policy',
    7,
    TRUE,
    TRUE,
    1000000,
    TRUE
)
ON CONFLICT DO NOTHING;

-- Visits are recorded independently from registered customers.
INSERT INTO aarrr.growth_events (
    event_uuid,
    external_user_id,
    event_type,
    event_at,
    source_id
)
SELECT
    gen_random_uuid(),
    v.external_id,
    'visit',
    v.visit_time,
    s.source_id
FROM (
    VALUES
        ('U001', 'organic', '2026-10-01 10:00:00+00'::TIMESTAMPTZ),
        ('U002', 'paid', '2026-10-01 11:00:00+00'::TIMESTAMPTZ),
        ('U003', 'referral', '2026-10-02 10:00:00+00'::TIMESTAMPTZ),
        ('U004', 'social', '2026-10-03 10:00:00+00'::TIMESTAMPTZ),
        ('U005', 'paid', '2026-10-04 10:00:00+00'::TIMESTAMPTZ)
) AS v(external_id, source_code, visit_time)
JOIN aarrr.acquisition_sources s
    ON s.source_code = v.source_code
WHERE NOT EXISTS (
    SELECT 1
    FROM aarrr.growth_events ge
    WHERE ge.external_user_id = v.external_id
      AND ge.event_type = 'visit'
);

-- Register customers in dependency order.
INSERT INTO aarrr.customers (
    external_user_id,
    source_id,
    signup_at
)
SELECT
    'U001',
    source_id,
    '2026-10-01 10:00:00+00'
FROM aarrr.acquisition_sources
WHERE source_code = 'organic'
ON CONFLICT (external_user_id) DO NOTHING;

INSERT INTO aarrr.customers (
    external_user_id,
    source_id,
    signup_at
)
SELECT
    'U002',
    source_id,
    '2026-10-01 11:00:00+00'
FROM aarrr.acquisition_sources
WHERE source_code = 'paid'
ON CONFLICT (external_user_id) DO NOTHING;

INSERT INTO aarrr.customers (
    external_user_id,
    source_id,
    referred_by,
    signup_at
)
SELECT
    'U003',
    s.source_id,
    ref.customer_id,
    '2026-10-02 10:00:00+00'
FROM aarrr.acquisition_sources s
JOIN aarrr.customers ref
    ON ref.external_user_id = 'U001'
WHERE s.source_code = 'referral'
ON CONFLICT (external_user_id) DO NOTHING;

INSERT INTO aarrr.customers (
    external_user_id,
    source_id,
    signup_at
)
SELECT
    'U004',
    source_id,
    '2026-10-03 10:00:00+00'
FROM aarrr.acquisition_sources
WHERE source_code = 'social'
ON CONFLICT (external_user_id) DO NOTHING;

INSERT INTO aarrr.customers (
    external_user_id,
    source_id,
    signup_at
)
SELECT
    'U005',
    source_id,
    '2026-10-04 10:00:00+00'
FROM aarrr.acquisition_sources
WHERE source_code = 'paid'
ON CONFLICT (external_user_id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- CUSTOMER ACTIVATION
-- ---------------------------------------------------------------------------

UPDATE aarrr.customers
SET activation_at = signup_at + INTERVAL '1 day'
WHERE external_user_id = 'U001'
  AND activation_at IS NULL;

UPDATE aarrr.customers
SET activation_at = signup_at + INTERVAL '2 days'
WHERE external_user_id = 'U002'
  AND activation_at IS NULL;

UPDATE aarrr.customers
SET activation_at = signup_at + INTERVAL '2 days'
WHERE external_user_id = 'U003'
  AND activation_at IS NULL;

UPDATE aarrr.customers
SET activation_at = signup_at + INTERVAL '3 days'
WHERE external_user_id = 'U004'
  AND activation_at IS NULL;

-- U005 deliberately remains registered but inactive.

-- ---------------------------------------------------------------------------
-- DAILY ACTIVITY
-- ---------------------------------------------------------------------------

INSERT INTO aarrr.daily_activity (
    customer_id,
    activity_date,
    login_count,
    last_login_at
)
SELECT
    c.customer_id,
    v.activity_date::DATE,
    1,
    v.activity_date
FROM (
    VALUES
        ('U001', '2026-10-04 10:00:00+00'::TIMESTAMPTZ),
        ('U001', '2026-10-05 10:00:00+00'::TIMESTAMPTZ),
        ('U002', '2026-10-06 10:00:00+00'::TIMESTAMPTZ),
        ('U003', '2026-10-06 10:00:00+00'::TIMESTAMPTZ),
        ('U004', '2026-10-08 10:00:00+00'::TIMESTAMPTZ)
) AS v(external_id, activity_date)
JOIN aarrr.customers c
    ON c.external_user_id = v.external_id
ON CONFLICT (customer_id, activity_date)
DO UPDATE SET
    login_count = aarrr.daily_activity.login_count + 1,
    last_login_at = EXCLUDED.last_login_at;

-- ---------------------------------------------------------------------------
-- REVENUE
-- ---------------------------------------------------------------------------

INSERT INTO aarrr.revenue_transactions (
    customer_id,
    transaction_reference,
    transaction_type,
    amount,
    currency,
    transaction_at
)
SELECT
    c.customer_id,
    v.reference,
    v.transaction_type,
    v.amount,
    'INR',
    v.transaction_at
FROM (
    VALUES
        (
            'U001',
            'TXN-1001',
            'purchase',
            4999.00::NUMERIC,
            '2026-10-05 10:00:00+00'::TIMESTAMPTZ
        ),
        (
            'U002',
            'TXN-1002',
            'subscription',
            9900.00::NUMERIC,
            '2026-10-07 10:00:00+00'::TIMESTAMPTZ
        ),
        (
            'U004',
            'TXN-1003',
            'purchase',
            2900.00::NUMERIC,
            '2026-10-08 10:00:00+00'::TIMESTAMPTZ
        )
) AS v(
    external_id,
    reference,
    transaction_type,
    amount,
    transaction_at
)
JOIN aarrr.customers c
    ON c.external_user_id = v.external_id
WHERE c.activation_at IS NOT NULL
ON CONFLICT (transaction_reference) DO NOTHING;

-- ---------------------------------------------------------------------------
-- REFERRAL ATTRIBUTION
-- ---------------------------------------------------------------------------

-- U003's referral relationship was inserted with customer registration.
-- The trigger creates its referral conversion record.

-- ---------------------------------------------------------------------------
-- EXPERIMENT DATA
-- ---------------------------------------------------------------------------

INSERT INTO aarrr.experiments (
    experiment_name,
    target_stage,
    start_date,
    end_date,
    status
)
VALUES (
    'Onboarding Activation Experiment',
    'activation',
    '2026-10-01',
    '2026-10-31',
    'completed'
)
ON CONFLICT (experiment_name) DO NOTHING;

INSERT INTO aarrr.experiment_assignments (
    experiment_id,
    customer_id,
    variant
)
SELECT
    e.experiment_id,
    c.customer_id,
    CASE c.external_user_id
        WHEN 'U001' THEN 'control'
        WHEN 'U002' THEN 'treatment'
        WHEN 'U003' THEN 'treatment'
        WHEN 'U004' THEN 'control'
        ELSE 'control'
    END
FROM aarrr.experiments e
CROSS JOIN aarrr.customers c
WHERE e.experiment_name = 'Onboarding Activation Experiment'
ON CONFLICT (experiment_id, customer_id) DO NOTHING;

COMMIT;

-- ---------------------------------------------------------------------------
-- REPORTING: ACQUISITION
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_acquisition_performance
ORDER BY visitors DESC;

-- ---------------------------------------------------------------------------
-- REPORTING: ACTIVATION
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_activation_performance;

-- ---------------------------------------------------------------------------
-- REPORTING: RETENTION COHORTS
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_retention_cohorts
ORDER BY cohort_date;

-- ---------------------------------------------------------------------------
-- REPORTING: REVENUE
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_revenue_performance;

SELECT *
FROM aarrr.v_customer_revenue
ORDER BY lifetime_revenue DESC;

-- ---------------------------------------------------------------------------
-- REPORTING: REFERRALS
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_referral_performance
ORDER BY referred_signups DESC;

-- ---------------------------------------------------------------------------
-- COMPLETE AARRR FUNNEL
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_aarrr_funnel;

-- ---------------------------------------------------------------------------
-- CUSTOMER LIFECYCLE VALIDATION
-- ---------------------------------------------------------------------------

SELECT
    external_user_id,
    customer_status,
    signup_at,
    activation_at,
    last_activity_at,
    lifetime_revenue
FROM aarrr.v_customer_growth_status
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- ELIGIBILITY DETERMINATION
-- ---------------------------------------------------------------------------

SELECT
    c.external_user_id,
    CASE
        WHEN c.cancelled_at IS NOT NULL
            THEN 'ineligible_cancelled'
        WHEN c.activation_at IS NULL
            THEN 'ineligible_not_activated'
        WHEN c.activation_at >
             c.signup_at + INTERVAL '7 days'
            THEN 'ineligible_late_activation'
        ELSE 'eligible_for_purchase'
    END AS purchase_eligibility
FROM aarrr.customers c
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- RETENTION: DAY-LEVEL COHORT ANALYSIS
-- ---------------------------------------------------------------------------

WITH cohorts AS (
    SELECT
        customer_id,
        signup_at::DATE AS cohort_date
    FROM aarrr.customers
),
activity AS (
    SELECT
        c.cohort_date,
        (da.activity_date - c.cohort_date) AS day_number,
        COUNT(DISTINCT da.customer_id) AS active_users
    FROM cohorts c
    JOIN aarrr.daily_activity da
        ON da.customer_id = c.customer_id
    WHERE da.activity_date >= c.cohort_date
      AND da.activity_date <= c.cohort_date + 30
    GROUP BY c.cohort_date, day_number
),
cohort_sizes AS (
    SELECT
        cohort_date,
        COUNT(*) AS cohort_size
    FROM cohorts
    GROUP BY cohort_date
)
SELECT
    a.cohort_date,
    a.day_number,
    s.cohort_size,
    a.active_users,
    ROUND(
        100.0 * a.active_users / NULLIF(s.cohort_size, 0),
        2
    ) AS retention_pct
FROM activity a
JOIN cohort_sizes s USING (cohort_date)
ORDER BY a.cohort_date, a.day_number;

-- ---------------------------------------------------------------------------
-- CHANNEL REVENUE AND ACQUISITION EFFICIENCY
-- ---------------------------------------------------------------------------

SELECT
    s.source_code,
    COUNT(DISTINCT c.customer_id) AS customers,
    COALESCE(SUM(r.amount), 0)::NUMERIC(14,2) AS revenue,
    ROUND(
        COALESCE(SUM(r.amount), 0) /
        NULLIF(COUNT(DISTINCT c.customer_id), 0),
        2
    ) AS revenue_per_acquired_customer
FROM aarrr.acquisition_sources s
LEFT JOIN aarrr.customers c
    ON c.source_id = s.source_id
LEFT JOIN aarrr.revenue_transactions r
    ON r.customer_id = c.customer_id
GROUP BY s.source_id, s.source_code
ORDER BY revenue DESC;

-- ---------------------------------------------------------------------------
-- EXPERIMENT EVALUATION
-- ---------------------------------------------------------------------------

SELECT *
FROM aarrr.v_experiment_performance
ORDER BY experiment_name, variant;

-- ---------------------------------------------------------------------------
-- OPERATIONAL VALIDATION
-- ---------------------------------------------------------------------------

-- Events with missing registered customer relationships.
SELECT
    event_id,
    external_user_id,
    event_type,
    event_at
FROM aarrr.growth_events
WHERE event_type NOT IN ('visit', 'signup')
  AND customer_id IS NULL;

-- Customers without activation.
SELECT
    external_user_id,
    signup_at,
    source_id
FROM aarrr.customers
WHERE activation_at IS NULL;

-- Duplicate activity records are prevented by the primary key.
SELECT
    customer_id,
    activity_date,
    login_count
FROM aarrr.daily_activity
ORDER BY activity_date, customer_id;

-- Revenue reconciliation.
SELECT
    SUM(amount) AS total_revenue,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT customer_id) AS paying_customers
FROM aarrr.revenue_transactions;

-- Referral attribution reconciliation.
SELECT
    COUNT(*) AS referral_records,
    COUNT(DISTINCT referred_customer_id) AS unique_referred_customers
FROM aarrr.referrals;

-- ---------------------------------------------------------------------------
-- TRANSACTIONAL EVENT PROCESSING EXAMPLE
-- ---------------------------------------------------------------------------

-- This example uses an isolated test customer.
-- The entire transaction is rolled back to preserve sample data.

BEGIN;

INSERT INTO aarrr.customers (
    external_user_id,
    source_id,
    signup_at
)
SELECT
    'TX-TEST-001',
    source_id,
    NOW()
FROM aarrr.acquisition_sources
WHERE source_code = 'organic';

CALL aarrr.process_growth_event(
    gen_random_uuid(),
    'TX-TEST-001',
    'activation',
    NOW(),
    NULL,
    NULL,
    0,
    NULL
);

ROLLBACK;

-- ---------------------------------------------------------------------------
-- SECURITY AND PERFORMANCE NOTES
-- ---------------------------------------------------------------------------

-- Production roles should receive minimum necessary permissions.
-- Application users should not own the schema or tables.
-- Event ingestion should use parameterized statements.
-- Avoid exposing external user identifiers in public reports.
-- Partition high-volume growth_events by event_at when justified.
-- Use retention policies for personally identifiable event properties.
-- Protect transaction and referral processing with database transactions.
-- Evaluate query plans with EXPLAIN (ANALYZE, BUFFERS).
-- The sample cohort report measures observed activity, not causal retention.
-- Referral rewards require separate fraud and eligibility controls.
