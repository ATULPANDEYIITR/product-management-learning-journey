DROP SCHEMA IF EXISTS product_api CASCADE;
CREATE SCHEMA product_api;
SET search_path TO product_api;

-- The model separates an API resource from the operational policies
-- governing access to that resource. This is useful for product managers
-- because endpoint behavior can be inspected independently from data.

CREATE TYPE http_method AS ENUM (
    'GET',
    'POST',
    'PATCH',
    'DELETE'
);

CREATE TYPE user_role AS ENUM (
    'product_manager',
    'administrator',
    'read_only'
);

CREATE TYPE product_state AS ENUM (
    'active',
    'inactive'
);

CREATE TABLE api_users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    role user_role NOT NULL,
    api_key_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    owner_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE api_endpoints (
    endpoint_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    method http_method NOT NULL,
    path_template TEXT NOT NULL,
    description TEXT NOT NULL,
    UNIQUE (repository_id, method, path_template)
);

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    product_name TEXT NOT NULL
        CHECK (length(trim(product_name)) >= 2),
    category TEXT NOT NULL
        CHECK (length(trim(category)) >= 2),
    price NUMERIC(12, 2) NOT NULL
        CHECK (price >= 0),
    state product_state NOT NULL DEFAULT 'active',
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version > 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE endpoint_permissions (
    endpoint_id BIGINT NOT NULL
        REFERENCES api_endpoints(endpoint_id)
        ON DELETE CASCADE,
    role user_role NOT NULL,
    PRIMARY KEY (endpoint_id, role)
);

CREATE TABLE api_requests (
    request_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT
        REFERENCES api_users(user_id),
    endpoint_id BIGINT
        REFERENCES api_endpoints(endpoint_id),
    method http_method NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL
        CHECK (status_code BETWEEN 100 AND 599),
    request_received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    response_time_ms INTEGER
        CHECK (response_time_ms >= 0)
);

CREATE TABLE api_status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    request_id BIGINT
        REFERENCES api_requests(request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rate_limit_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    endpoint_id BIGINT NOT NULL UNIQUE
        REFERENCES api_endpoints(endpoint_id)
        ON DELETE CASCADE,
    requests_per_window INTEGER NOT NULL
        CHECK (requests_per_window > 0),
    window_seconds INTEGER NOT NULL
        CHECK (window_seconds > 0)
);

CREATE TABLE api_documentation (
    documentation_id BIGSERIAL PRIMARY KEY,
    endpoint_id BIGINT NOT NULL UNIQUE
        REFERENCES api_endpoints(endpoint_id)
        ON DELETE CASCADE,
    request_description TEXT NOT NULL,
    response_description TEXT NOT NULL,
    authentication_required BOOLEAN NOT NULL DEFAULT true,
    last_reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_repository_category
    ON products (repository_id, category);

CREATE INDEX idx_api_requests_received_at
    ON api_requests (request_received_at);

CREATE INDEX idx_api_status_checks_request
    ON api_status_checks (request_id);

INSERT INTO api_users
    (username, role, api_key_hash)
VALUES
    (
        'product_manager',
        'product_manager',
        md5('pm-demo-key')
    ),
    (
        'api_admin',
        'administrator',
        md5('admin-demo-key')
    ),
    (
        'analyst',
        'read_only',
        md5('read-demo-key')
    );

INSERT INTO repositories
    (repository_name, owner_name)
VALUES
    ('product-catalog-api', 'Platform Product Team');

INSERT INTO api_endpoints
    (repository_id, method, path_template, description)
VALUES
    (
        1,
        'GET',
        '/api/v1/products',
        'List products with filtering and pagination'
    ),
    (
        1,
        'POST',
        '/api/v1/products',
        'Create a product'
    ),
    (
        1,
        'GET',
        '/api/v1/products/{id}',
        'Retrieve one product'
    ),
    (
        1,
        'PATCH',
        '/api/v1/products/{id}',
        'Partially update a product'
    ),
    (
        1,
        'DELETE',
        '/api/v1/products/{id}',
        'Delete a product'
    );

INSERT INTO endpoint_permissions
    (endpoint_id, role)
SELECT
    endpoint_id,
    'read_only'
FROM api_endpoints
WHERE method = 'GET';

INSERT INTO endpoint_permissions
    (endpoint_id, role)
SELECT
    endpoint_id,
    'product_manager'
FROM api_endpoints
WHERE method IN ('GET', 'POST', 'PATCH');

INSERT INTO endpoint_permissions
    (endpoint_id, role)
SELECT
    endpoint_id,
    'administrator'
FROM api_endpoints;

INSERT INTO rate_limit_policies
    (endpoint_id, requests_per_window, window_seconds)
SELECT
    endpoint_id,
    CASE
        WHEN method = 'GET' THEN 100
        WHEN method = 'POST' THEN 20
        ELSE 30
    END,
    60
FROM api_endpoints;

INSERT INTO api_documentation
    (
        endpoint_id,
        request_description,
        response_description,
        authentication_required
    )
SELECT
    endpoint_id,
    CASE method
        WHEN 'GET' THEN
            'Optional category filter and pagination parameters.'
        WHEN 'POST' THEN
            'JSON object containing name, category and price.'
        WHEN 'PATCH' THEN
            'Partial JSON object plus an If-Match ETag.'
        WHEN 'DELETE' THEN
            'No request body; administrator authorization required.'
    END,
    CASE method
        WHEN 'GET' THEN
            '200 response containing product resources.'
        WHEN 'POST' THEN
            '201 response with Location and ETag headers.'
        WHEN 'PATCH' THEN
            '200 response containing the updated resource and new ETag.'
        WHEN 'DELETE' THEN
            '204 response with no response body.'
    END,
    true
FROM api_endpoints;

INSERT INTO products
    (
        repository_id,
        product_name,
        category,
        price,
        state,
        version
    )
VALUES
    (
        1,
        'Analytics Pro',
        'analytics',
        49.99,
        'active',
        1
    ),
    (
        1,
        'Team Workspace',
        'collaboration',
        19.99,
        'active',
        1
    ),
    (
        1,
        'Legacy Reports',
        'analytics',
        9.99,
        'inactive',
        3
    );

-- A trigger maintains resource-version semantics and prevents an update
-- from leaving the API representation with an old timestamp.

CREATE OR REPLACE FUNCTION maintain_product_version()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.product_name IS DISTINCT FROM OLD.product_name
       OR NEW.category IS DISTINCT FROM OLD.category
       OR NEW.price IS DISTINCT FROM OLD.price
       OR NEW.state IS DISTINCT FROM OLD.state THEN

        NEW.version := OLD.version + 1;
        NEW.updated_at := now();
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_product_version
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION maintain_product_version();

-- Database-level validation for a product mutation. The application can
-- return a friendly API error while PostgreSQL remains the final integrity
-- boundary.

CREATE OR REPLACE FUNCTION validate_product_change(
    p_product_id BIGINT,
    p_expected_version INTEGER,
    p_new_price NUMERIC
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    current_version INTEGER;
BEGIN
    SELECT version
    INTO current_version
    FROM products
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF current_version IS NULL THEN
        RAISE EXCEPTION
            'Product % does not exist',
            p_product_id
            USING ERRCODE = 'P0002';
    END IF;

    IF current_version <> p_expected_version THEN
        RAISE EXCEPTION
            'Stale product version: expected %, current %',
            p_expected_version,
            current_version
            USING ERRCODE = '40001';
    END IF;

    IF p_new_price < 0 THEN
        RAISE EXCEPTION
            'Product price cannot be negative'
            USING ERRCODE = '23514';
    END IF;

    RETURN true;
END;
$$;

-- Endpoint inventory for API documentation and product planning.

SELECT
    e.method,
    e.path_template,
    e.description,
    array_agg(ep.role ORDER BY ep.role) AS permitted_roles
FROM api_endpoints e
LEFT JOIN endpoint_permissions ep
    ON ep.endpoint_id = e.endpoint_id
GROUP BY
    e.endpoint_id,
    e.method,
    e.path_template,
    e.description
ORDER BY
    e.endpoint_id;

-- API usability query: documentation completeness.

SELECT
    e.method,
    e.path_template,
    d.authentication_required,
    d.request_description,
    d.response_description,
    d.last_reviewed_at
FROM api_endpoints e
JOIN api_documentation d
    ON d.endpoint_id = e.endpoint_id
ORDER BY e.endpoint_id;

-- Example request telemetry.

INSERT INTO api_requests
    (
        user_id,
        endpoint_id,
        method,
        path,
        status_code,
        response_time_ms
    )
VALUES
    (
        1,
        1,
        'GET',
        '/api/v1/products?category=analytics',
        200,
        24
    ),
    (
        1,
        2,
        'POST',
        '/api/v1/products',
        201,
        47
    ),
    (
        3,
        2,
        'POST',
        '/api/v1/products',
        403,
        8
    ),
    (
        2,
        3,
        'GET',
        '/api/v1/products/9999',
        404,
        11
    ),
    (
        1,
        4,
        'PATCH',
        '/api/v1/products/1',
        412,
        13
    );

INSERT INTO api_status_checks
    (
        request_id,
        check_name,
        passed
    )
SELECT
    request_id,
    CASE
        WHEN status_code < 400
            THEN 'request-contract'
        ELSE 'error-contract'
    END,
    status_code < 400
FROM api_requests;

-- Identify endpoints whose requests frequently fail.

SELECT
    e.method,
    e.path_template,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (
        WHERE r.status_code >= 400
    ) AS failed_requests,
    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE r.status_code >= 400)
        / NULLIF(COUNT(*), 0),
        2
    ) AS failure_percentage
FROM api_requests r
JOIN api_endpoints e
    ON e.endpoint_id = r.endpoint_id
GROUP BY
    e.endpoint_id,
    e.method,
    e.path_template
ORDER BY
    failure_percentage DESC;

-- Check whether a role can call a specific endpoint.

SELECT EXISTS (
    SELECT 1
    FROM endpoint_permissions ep
    JOIN api_endpoints e
        ON e.endpoint_id = ep.endpoint_id
    WHERE e.method = 'POST'
      AND e.path_template = '/api/v1/products'
      AND ep.role = 'product_manager'
) AS product_manager_can_create_products;

-- CTE for an operational API quality report.

WITH endpoint_stats AS (
    SELECT
        endpoint_id,
        COUNT(*) AS request_count,
        AVG(response_time_ms) AS average_latency_ms,
        COUNT(*) FILTER (
            WHERE status_code >= 400
        ) AS error_count
    FROM api_requests
    GROUP BY endpoint_id
)
SELECT
    e.method,
    e.path_template,
    COALESCE(s.request_count, 0) AS request_count,
    ROUND(COALESCE(s.average_latency_ms, 0)::numeric, 2)
        AS average_latency_ms,
    COALESCE(s.error_count, 0) AS error_count
FROM api_endpoints e
LEFT JOIN endpoint_stats s
    ON s.endpoint_id = e.endpoint_id
ORDER BY
    average_latency_ms DESC;

-- Transactional optimistic-concurrency example.
-- The expected version is deliberately current for product 1.

BEGIN;

SELECT validate_product_change(
    1,
    1,
    54.99
);

UPDATE products
SET price = 54.99
WHERE product_id = 1
  AND version = 1;

COMMIT;

-- Verify that the trigger advanced the version and timestamp.

SELECT
    product_id,
    product_name,
    price,
    version,
    updated_at
FROM products
WHERE product_id = 1;

-- Demonstrate an atomic creation transaction.

BEGIN;

WITH inserted_product AS (
    INSERT INTO products
        (
            repository_id,
            product_name,
            category,
            price,
            state
        )
    VALUES
        (
            1,
            'Customer Insights',
            'analytics',
            79.00,
            'active'
        )
    RETURNING product_id
)
INSERT INTO api_requests
    (
        user_id,
        endpoint_id,
        method,
        path,
        status_code,
        response_time_ms
    )
SELECT
    1,
    2,
    'POST',
    '/api/v1/products',
    201,
    32
FROM inserted_product;

COMMIT;

-- Product-manager-oriented reporting:
-- distinguish authentication failures, authorization failures,
-- validation failures, missing resources and server-independent conflicts.

SELECT
    CASE
        WHEN status_code = 401 THEN 'authentication'
        WHEN status_code = 403 THEN 'authorization'
        WHEN status_code = 400 THEN 'validation'
        WHEN status_code = 404 THEN 'resource-not-found'
        WHEN status_code IN (409, 412) THEN 'concurrency'
        WHEN status_code = 429 THEN 'rate-limit'
        WHEN status_code BETWEEN 200 AND 299 THEN 'success'
        ELSE 'other'
    END AS outcome_class,
    COUNT(*) AS occurrences
FROM api_requests
GROUP BY outcome_class
ORDER BY occurrences DESC;
