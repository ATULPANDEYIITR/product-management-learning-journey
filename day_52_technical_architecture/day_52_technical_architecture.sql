-- PostgreSQL 14+ technical architecture model.
--
-- The schema represents a service-oriented order platform.
-- Customer data belongs to the customer service.
-- Order data belongs to the order service.
-- The database records service boundaries, cache observations, queue events,
-- consumer attempts, and architecture-level merge-independent workflow state.
--
-- PostgreSQL-specific features used:
--   identity columns, enums, CHECK constraints, partial indexes, JSONB,
--   triggers, PL/pgSQL functions, CTEs, transactions, and views.

DROP SCHEMA IF EXISTS technical_architecture CASCADE;
CREATE SCHEMA technical_architecture;
SET search_path TO technical_architecture;

CREATE TYPE service_status AS ENUM (
    'healthy',
    'degraded',
    'down'
);

CREATE TYPE architecture_style AS ENUM (
    'monolith',
    'microservices'
);

CREATE TYPE customer_tier AS ENUM (
    'standard',
    'premium',
    'enterprise'
);

CREATE TYPE order_status AS ENUM (
    'created',
    'processing',
    'completed',
    'failed'
);

CREATE TYPE event_status AS ENUM (
    'pending',
    'processed',
    'dead_letter'
);

CREATE TABLE architecture (
    architecture_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE,
    style architecture_style NOT NULL,
    description text NOT NULL,
    CHECK (length(trim(name)) > 0),
    CHECK (length(trim(description)) > 0)
);

CREATE TABLE service (
    service_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    architecture_id bigint NOT NULL
        REFERENCES architecture(architecture_id),
    service_name text NOT NULL,
    status service_status NOT NULL DEFAULT 'healthy',
    owns_database boolean NOT NULL DEFAULT false,
    synchronous_dependency_allowed boolean NOT NULL DEFAULT true,
    UNIQUE (architecture_id, service_name),
    CHECK (length(trim(service_name)) > 0)
);

CREATE TABLE database_instance (
    database_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_id bigint NOT NULL
        REFERENCES service(service_id),
    database_name text NOT NULL UNIQUE,
    available boolean NOT NULL DEFAULT true,
    read_count bigint NOT NULL DEFAULT 0,
    write_count bigint NOT NULL DEFAULT 0,
    CHECK (read_count >= 0),
    CHECK (write_count >= 0)
);

CREATE TABLE cache_policy (
    cache_policy_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_id bigint NOT NULL
        REFERENCES service(service_id),
    cache_name text NOT NULL,
    capacity_entries integer NOT NULL,
    ttl_seconds integer NOT NULL,
    eviction_policy text NOT NULL DEFAULT 'fifo',
    cache_aside boolean NOT NULL DEFAULT true,
    UNIQUE (service_id, cache_name),
    CHECK (capacity_entries > 0),
    CHECK (ttl_seconds > 0),
    CHECK (eviction_policy IN ('fifo', 'lru', 'lfu')),
    CHECK (cache_aside = true OR cache_aside = false)
);

CREATE TABLE customer (
    customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_service_id bigint NOT NULL
        REFERENCES service(service_id),
    customer_name text NOT NULL,
    tier customer_tier NOT NULL DEFAULT 'standard',
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (length(trim(customer_name)) > 0)
);

CREATE TABLE customer_cache_observation (
    observation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cache_policy_id bigint NOT NULL
        REFERENCES cache_policy(cache_policy_id),
    customer_id bigint NOT NULL
        REFERENCES customer(customer_id),
    cache_key text NOT NULL,
    hit boolean NOT NULL,
    observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (cache_policy_id, cache_key, observed_at)
);

CREATE TABLE repository_request (
    request_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    architecture_id bigint NOT NULL
        REFERENCES architecture(architecture_id),
    request_type text NOT NULL,
    customer_id bigint
        REFERENCES customer(customer_id),
    amount numeric(14,2),
    accepted boolean NOT NULL,
    failure_reason text,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (amount IS NULL OR amount > 0),
    CHECK (
        (accepted = true AND failure_reason IS NULL)
        OR
        (accepted = false AND failure_reason IS NOT NULL)
    )
);

CREATE TABLE customer_order (
    order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_service_id bigint NOT NULL
        REFERENCES service(service_id),
    customer_id bigint NOT NULL
        REFERENCES customer(customer_id),
    amount numeric(14,2) NOT NULL,
    status order_status NOT NULL DEFAULT 'created',
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (amount > 0)
);

CREATE TABLE queue (
    queue_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_id bigint NOT NULL
        REFERENCES service(service_id),
    queue_name text NOT NULL,
    max_retries integer NOT NULL DEFAULT 3,
    available boolean NOT NULL DEFAULT true,
    UNIQUE (service_id, queue_name),
    CHECK (max_retries > 0)
);

CREATE TABLE queue_event (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    queue_id bigint NOT NULL
        REFERENCES queue(queue_id),
    event_type text NOT NULL,
    aggregate_id bigint,
    payload jsonb NOT NULL,
    status event_status NOT NULL DEFAULT 'pending',
    attempts integer NOT NULL DEFAULT 0,
    published_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    processed_at timestamptz,
    CHECK (length(trim(event_type)) > 0),
    CHECK (attempts >= 0),
    CHECK (
        status <> 'processed'
        OR processed_at IS NOT NULL
    ),
    CHECK (
        status <> 'pending'
        OR processed_at IS NULL
    )
);

CREATE TABLE queue_failure (
    failure_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id bigint NOT NULL
        REFERENCES queue_event(event_id),
    attempt_number integer NOT NULL,
    error_message text NOT NULL,
    failed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (attempt_number > 0),
    CHECK (length(trim(error_message)) > 0)
);

CREATE INDEX idx_customer_service
    ON customer(customer_service_id);

CREATE INDEX idx_order_customer_status
    ON customer_order(customer_id, status);

CREATE INDEX idx_queue_event_pending
    ON queue_event(queue_id, published_at)
    WHERE status = 'pending';

CREATE INDEX idx_request_architecture_time
    ON repository_request(architecture_id, created_at);

CREATE INDEX idx_cache_observation_customer_time
    ON customer_cache_observation(customer_id, observed_at);

CREATE OR REPLACE FUNCTION touch_order_timestamp()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = clock_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_touch_order_timestamp
BEFORE UPDATE ON customer_order
FOR EACH ROW
EXECUTE FUNCTION touch_order_timestamp();

CREATE OR REPLACE FUNCTION validate_order_service_ownership()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    customer_owner bigint;
BEGIN
    SELECT customer_service_id
    INTO customer_owner
    FROM customer
    WHERE customer_id = NEW.customer_id;

    IF customer_owner IS NULL THEN
        RAISE EXCEPTION
            'Customer % does not exist',
            NEW.customer_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_order_customer
BEFORE INSERT OR UPDATE ON customer_order
FOR EACH ROW
EXECUTE FUNCTION validate_order_service_ownership();

CREATE OR REPLACE FUNCTION create_order_event(
    p_order_id bigint,
    p_customer_id bigint,
    p_amount numeric
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_queue_id bigint;
    v_event_id bigint;
BEGIN
    SELECT q.queue_id
    INTO v_queue_id
    FROM queue q
    JOIN service s
      ON s.service_id = q.service_id
    WHERE q.queue_name = 'order-events'
      AND s.service_name = 'order-service'
      AND q.available = true
    LIMIT 1;

    IF v_queue_id IS NULL THEN
        RAISE EXCEPTION
            'Order event queue is unavailable';
    END IF;

    INSERT INTO queue_event (
        queue_id,
        event_type,
        aggregate_id,
        payload
    )
    VALUES (
        v_queue_id,
        'order.created',
        p_order_id,
        jsonb_build_object(
            'order_id', p_order_id,
            'customer_id', p_customer_id,
            'amount', p_amount
        )
    )
    RETURNING event_id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

CREATE OR REPLACE FUNCTION service_can_accept_requests(
    p_service_id bigint
)
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT status IN ('healthy', 'degraded')
    FROM service
    WHERE service_id = p_service_id;
$$;

CREATE OR REPLACE FUNCTION record_cache_observation(
    p_cache_policy_id bigint,
    p_customer_id bigint,
    p_hit boolean
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO customer_cache_observation (
        cache_policy_id,
        customer_id,
        cache_key,
        hit
    )
    VALUES (
        p_cache_policy_id,
        p_customer_id,
        'customer:' || p_customer_id,
        p_hit
    );
END;
$$;

INSERT INTO architecture (
    name,
    style,
    description
)
VALUES
(
    'Commerce Monolith',
    'monolith',
    'Single deployable application with a shared database boundary.'
),
(
    'Commerce Services',
    'microservices',
    'Customer and order domains use independent service and database ownership.'
);

INSERT INTO service (
    architecture_id,
    service_name,
    status,
    owns_database,
    synchronous_dependency_allowed
)
SELECT
    architecture_id,
    'monolith-application',
    'healthy',
    true,
    true
FROM architecture
WHERE name = 'Commerce Monolith';

INSERT INTO service (
    architecture_id,
    service_name,
    status,
    owns_database,
    synchronous_dependency_allowed
)
SELECT
    architecture_id,
    'customer-service',
    'healthy',
    true,
    true
FROM architecture
WHERE name = 'Commerce Services';

INSERT INTO service (
    architecture_id,
    service_name,
    status,
    owns_database,
    synchronous_dependency_allowed
)
SELECT
    architecture_id,
    'order-service',
    'healthy',
    true,
    true
FROM architecture
WHERE name = 'Commerce Services';

INSERT INTO database_instance (
    service_id,
    database_name
)
SELECT
    service_id,
    service_name || '-db'
FROM service
WHERE owns_database = true;

INSERT INTO cache_policy (
    service_id,
    cache_name,
    capacity_entries,
    ttl_seconds,
    eviction_policy
)
SELECT
    service_id,
    'customer-cache',
    10000,
    60,
    'lru'
FROM service
WHERE service_name = 'customer-service';

INSERT INTO queue (
    service_id,
    queue_name,
    max_retries
)
SELECT
    service_id,
    'order-events',
    3
FROM service
WHERE service_name = 'order-service';

INSERT INTO customer (
    customer_service_id,
    customer_name,
    tier
)
SELECT
    service_id,
    x.customer_name,
    x.tier::customer_tier
FROM service
CROSS JOIN (
    VALUES
        ('Asha', 'premium'),
        ('Ravi', 'standard'),
        ('Meera', 'enterprise')
) AS x(customer_name, tier)
WHERE service_name = 'customer-service';

-- Cache observations deliberately contain both hits and misses so that
-- reporting can distinguish cache effectiveness from database traffic.
SELECT record_cache_observation(
    cp.cache_policy_id,
    c.customer_id,
    false
)
FROM cache_policy cp
JOIN customer c ON c.customer_name = 'Asha'
WHERE cp.cache_name = 'customer-cache';

SELECT record_cache_observation(
    cp.cache_policy_id,
    c.customer_id,
    true
)
FROM cache_policy cp
JOIN customer c ON c.customer_name = 'Asha'
WHERE cp.cache_name = 'customer-cache';

SELECT record_cache_observation(
    cp.cache_policy_id,
    c.customer_id,
    false
)
FROM cache_policy cp
JOIN customer c ON c.customer_name = 'Ravi'
WHERE cp.cache_name = 'customer-cache';

BEGIN;

WITH selected_customer AS (
    SELECT customer_id
    FROM customer
    WHERE customer_name = 'Asha'
      AND active = true
)
INSERT INTO customer_order (
    order_service_id,
    customer_id,
    amount,
    status
)
SELECT
    s.service_id,
    c.customer_id,
    2499.50,
    'created'
FROM service s
CROSS JOIN selected_customer c
WHERE s.service_name = 'order-service';

COMMIT;

-- The event is created in the same transaction as a persisted order.
-- This models the database-side part of an outbox-style workflow.
BEGIN;

WITH latest_order AS (
    SELECT
        order_id,
        customer_id,
        amount
    FROM customer_order
    ORDER BY order_id DESC
    LIMIT 1
)
SELECT create_order_event(
    order_id,
    customer_id,
    amount
)
FROM latest_order;

COMMIT;

-- Simulate a second order with a different customer tier.
BEGIN;

INSERT INTO customer_order (
    order_service_id,
    customer_id,
    amount
)
SELECT
    s.service_id,
    c.customer_id,
    8500.00
FROM service s
JOIN customer c
  ON c.customer_name = 'Meera'
WHERE s.service_name = 'order-service';

COMMIT;

-- Record a failed request caused by a service outage.
UPDATE service
SET status = 'down'
WHERE service_name = 'customer-service';

INSERT INTO repository_request (
    architecture_id,
    request_type,
    customer_id,
    amount,
    accepted,
    failure_reason
)
SELECT
    a.architecture_id,
    'create-order',
    c.customer_id,
    500.00,
    false,
    'customer-service unavailable'
FROM architecture a
JOIN customer c
  ON c.customer_name = 'Asha'
WHERE a.name = 'Commerce Services';

UPDATE service
SET status = 'healthy'
WHERE service_name = 'customer-service';

-- Simulate queue processing. A failed event is retried and eventually
-- moved to a dead-letter state after reaching the retry policy.
WITH target_event AS (
    SELECT event_id, queue_id
    FROM queue_event
    WHERE event_type = 'order.created'
    ORDER BY event_id DESC
    LIMIT 1
)
UPDATE queue_event qe
SET
    attempts = 1,
    status = 'pending'
FROM target_event te
WHERE qe.event_id = te.event_id;

WITH target_event AS (
    SELECT event_id
    FROM queue_event
    WHERE event_type = 'order.created'
    ORDER BY event_id DESC
    LIMIT 1
)
INSERT INTO queue_failure (
    event_id,
    attempt_number,
    error_message
)
SELECT
    event_id,
    1,
    'Downstream notification provider timeout'
FROM target_event;

WITH target_event AS (
    SELECT event_id
    FROM queue_event
    WHERE event_type = 'order.created'
    ORDER BY event_id DESC
    LIMIT 1
)
UPDATE queue_event qe
SET
    attempts = 3,
    status = 'dead_letter'
FROM target_event te
WHERE qe.event_id = te.event_id;

CREATE OR REPLACE VIEW architecture_service_inventory AS
SELECT
    a.name AS architecture,
    a.style,
    s.service_name,
    s.status,
    s.owns_database,
    d.database_name,
    cp.cache_name,
    cp.ttl_seconds,
    q.queue_name,
    q.max_retries
FROM architecture a
JOIN service s
  ON s.architecture_id = a.architecture_id
LEFT JOIN database_instance d
  ON d.service_id = s.service_id
LEFT JOIN cache_policy cp
  ON cp.service_id = s.service_id
LEFT JOIN queue q
  ON q.service_id = s.service_id;

CREATE OR REPLACE VIEW cache_performance AS
SELECT
    cp.cache_name,
    COUNT(*) AS observations,
    COUNT(*) FILTER (WHERE o.hit) AS hits,
    COUNT(*) FILTER (WHERE NOT o.hit) AS misses,
    ROUND(
        (
            COUNT(*) FILTER (WHERE o.hit)::numeric
            / NULLIF(COUNT(*), 0)
        ),
        4
    ) AS hit_ratio
FROM cache_policy cp
JOIN customer_cache_observation o
  ON o.cache_policy_id = cp.cache_policy_id
GROUP BY cp.cache_name;

CREATE OR REPLACE VIEW queue_health AS
SELECT
    q.queue_name,
    COUNT(e.event_id) AS total_events,
    COUNT(*) FILTER (
        WHERE e.status = 'pending'
    ) AS pending_events,
    COUNT(*) FILTER (
        WHERE e.status = 'processed'
    ) AS processed_events,
    COUNT(*) FILTER (
        WHERE e.status = 'dead_letter'
    ) AS dead_letter_events,
    MAX(e.attempts) AS max_attempts
FROM queue q
LEFT JOIN queue_event e
  ON e.queue_id = q.queue_id
GROUP BY q.queue_name;

CREATE OR REPLACE VIEW order_service_report AS
WITH status_counts AS (
    SELECT
        status,
        COUNT(*) AS order_count,
        SUM(amount) AS total_value
    FROM customer_order
    GROUP BY status
)
SELECT
    status,
    order_count,
    COALESCE(total_value, 0) AS total_value
FROM status_counts
ORDER BY status;

-- Service availability evaluation.
SELECT
    service_name,
    status,
    service_can_accept_requests(service_id)
        AS can_accept_requests
FROM service
ORDER BY service_name;

-- Architecture inventory.
SELECT *
FROM architecture_service_inventory
ORDER BY architecture, service_name;

-- Cache effectiveness.
SELECT *
FROM cache_performance;

-- Queue operational state.
SELECT *
FROM queue_health;

-- Order aggregation.
SELECT *
FROM order_service_report;

-- CTE-based customer workload report.
WITH customer_orders AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.tier,
        COUNT(o.order_id) AS order_count,
        COALESCE(SUM(o.amount), 0) AS total_value
    FROM customer c
    LEFT JOIN customer_order o
      ON o.customer_id = c.customer_id
    GROUP BY
        c.customer_id,
        c.customer_name,
        c.tier
)
SELECT
    customer_name,
    tier,
    order_count,
    total_value,
    CASE
        WHEN order_count = 0 THEN 'no orders'
        WHEN total_value >= 5000 THEN 'high-value'
        ELSE 'normal'
    END AS workload_class
FROM customer_orders
ORDER BY total_value DESC, customer_name;

-- Integrity test that intentionally fails if uncommented:
-- INSERT INTO customer_order (
--     order_service_id,
--     customer_id,
--     amount
-- )
-- VALUES (999999, 999999, -10.00);
--
-- The primary/foreign-key and CHECK constraints prevent the invalid record.
