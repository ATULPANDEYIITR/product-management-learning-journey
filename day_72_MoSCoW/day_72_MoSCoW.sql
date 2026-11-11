-- ============================================================
-- MoSCoW REQUIREMENTS PRIORITIZATION SYSTEM
-- PostgreSQL 15+
--
-- Features:
--   1. Four MoSCoW priority categories.
--   2. Product and release management.
--   3. Requirement ownership.
--   4. Dependency management.
--   5. Priority decision history.
--   6. Capacity-aware release planning.
--   7. Reporting and aggregation.
--   8. Validation triggers.
--   9. Transaction-safe priority changes.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS moscow;

SET search_path TO moscow, public;

-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

CREATE TYPE requirement_priority AS ENUM (
    'MUST_HAVE',
    'SHOULD_HAVE',
    'COULD_HAVE',
    'WONT_HAVE'
);

CREATE TYPE requirement_status AS ENUM (
    'PROPOSED',
    'APPROVED',
    'IN_PROGRESS',
    'COMPLETED',
    'DEFERRED'
);

CREATE TYPE release_status AS ENUM (
    'PLANNING',
    'ACTIVE',
    'COMPLETED',
    'CANCELLED'
);

-- ============================================================
-- 2. USERS
-- ============================================================

CREATE TABLE team_members (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role_name VARCHAR(80) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. PRODUCTS
-- ============================================================

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    product_owner BIGINT NOT NULL REFERENCES team_members(member_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 4. RELEASES
-- ============================================================

CREATE TABLE releases (
    release_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    release_name VARCHAR(120) NOT NULL,
    capacity_points INTEGER NOT NULL CHECK (capacity_points >= 0),
    status release_status NOT NULL DEFAULT 'PLANNING',
    planned_start DATE,
    planned_end DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(product_id, release_name),

    CHECK (
        planned_end IS NULL
        OR planned_start IS NULL
        OR planned_end >= planned_start
    )
);

-- ============================================================
-- 5. REQUIREMENTS
-- ============================================================

CREATE TABLE requirements (
    requirement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    release_id BIGINT REFERENCES releases(release_id),
    requirement_code VARCHAR(30) NOT NULL,
    title VARCHAR(250) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority requirement_priority NOT NULL,
    status requirement_status NOT NULL DEFAULT 'PROPOSED',
    business_value INTEGER NOT NULL
        CHECK (business_value BETWEEN 1 AND 10),
    effort_points INTEGER NOT NULL
        CHECK (effort_points BETWEEN 1 AND 100),
    owner_id BIGINT NOT NULL REFERENCES team_members(member_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(product_id, requirement_code)
);

CREATE INDEX idx_requirements_product_priority
    ON requirements(product_id, priority);

CREATE INDEX idx_requirements_release_status
    ON requirements(release_id, status);

CREATE INDEX idx_requirements_owner
    ON requirements(owner_id);

CREATE INDEX idx_requirements_value_effort
    ON requirements(
        business_value DESC,
        effort_points ASC
    );

-- ============================================================
-- 6. REQUIREMENT DEPENDENCIES
-- ============================================================

CREATE TABLE requirement_dependencies (
    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,

    depends_on_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id)
        ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY(requirement_id, depends_on_id),

    CHECK(requirement_id <> depends_on_id)
);

CREATE INDEX idx_dependencies_reverse
    ON requirement_dependencies(depends_on_id);

-- ============================================================
-- 7. PRIORITY CHANGE HISTORY
-- ============================================================

CREATE TABLE priority_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id),

    old_priority requirement_priority NOT NULL,
    new_priority requirement_priority NOT NULL,

    changed_by BIGINT NOT NULL
        REFERENCES team_members(member_id),

    change_reason TEXT NOT NULL
        CHECK (LENGTH(TRIM(change_reason)) > 0),

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK(old_priority <> new_priority)
);

CREATE INDEX idx_priority_history_requirement
    ON priority_history(requirement_id, changed_at DESC);

-- ============================================================
-- 8. RELEASE EVALUATION RESULTS
-- ============================================================

CREATE TABLE release_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    release_id BIGINT NOT NULL
        REFERENCES releases(release_id),

    evaluated_by BIGINT NOT NULL
        REFERENCES team_members(member_id),

    available_capacity INTEGER NOT NULL
        CHECK (available_capacity >= 0),

    mandatory_effort INTEGER NOT NULL DEFAULT 0
        CHECK (mandatory_effort >= 0),

    planned_effort INTEGER NOT NULL DEFAULT 0
        CHECK (planned_effort >= 0),

    mandatory_shortfall BOOLEAN NOT NULL DEFAULT FALSE,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 9. RELEASE ALLOCATION
-- ============================================================

CREATE TABLE release_allocations (
    evaluation_id BIGINT NOT NULL
        REFERENCES release_evaluations(evaluation_id)
        ON DELETE CASCADE,

    requirement_id BIGINT NOT NULL
        REFERENCES requirements(requirement_id),

    allocated_effort INTEGER NOT NULL
        CHECK (allocated_effort > 0),

    PRIMARY KEY(evaluation_id, requirement_id)
);

-- ============================================================
-- 10. REQUIREMENT VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_requirement()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.priority = 'WONT_HAVE'
       AND NEW.status IN ('IN_PROGRESS', 'COMPLETED') THEN

        RAISE EXCEPTION
            'Won''t-have requirements cannot enter delivery.';
    END IF;

    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_requirement
BEFORE INSERT OR UPDATE ON requirements
FOR EACH ROW
EXECUTE FUNCTION validate_requirement();

-- ============================================================
-- 11. PRODUCT AND RELEASE CONSISTENCY
-- ============================================================

CREATE OR REPLACE FUNCTION validate_requirement_release()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    release_product BIGINT;
BEGIN
    IF NEW.release_id IS NOT NULL THEN

        SELECT product_id
        INTO release_product
        FROM releases
        WHERE release_id = NEW.release_id;

        IF release_product IS NULL THEN
            RAISE EXCEPTION 'Release does not exist.';
        END IF;

        IF release_product <> NEW.product_id THEN
            RAISE EXCEPTION
                'Requirement and release must belong to the same product.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_requirement_release
BEFORE INSERT OR UPDATE OF release_id, product_id
ON requirements
FOR EACH ROW
EXECUTE FUNCTION validate_requirement_release();

-- ============================================================
-- 12. DEPENDENCY CYCLE VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    IF NEW.requirement_id = NEW.depends_on_id THEN
        RAISE EXCEPTION 'Self-dependency is prohibited.';
    END IF;

    WITH RECURSIVE dependency_path(node_id) AS (
        SELECT NEW.depends_on_id

        UNION

        SELECT d.depends_on_id
        FROM requirement_dependencies d
        JOIN dependency_path p
          ON d.requirement_id = p.node_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE node_id = NEW.requirement_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION 'Circular dependency detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_dependency_cycle
BEFORE INSERT OR UPDATE
ON requirement_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_cycle();

-- ============================================================
-- 13. PRIORITY CHANGE AUDIT
-- ============================================================

CREATE OR REPLACE FUNCTION record_priority_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    actor_id BIGINT;
    reason_text TEXT;
BEGIN
    IF OLD.priority IS DISTINCT FROM NEW.priority THEN

        actor_id := NULLIF(
            current_setting('moscow.actor_id', TRUE),
            ''
        )::BIGINT;

        reason_text := NULLIF(
            current_setting('moscow.change_reason', TRUE),
            ''
        );

        IF actor_id IS NULL OR reason_text IS NULL THEN
            RAISE EXCEPTION
                'Priority changes require an actor and reason.';
        END IF;

        INSERT INTO priority_history (
            requirement_id,
            old_priority,
            new_priority,
            changed_by,
            change_reason
        )
        VALUES (
            NEW.requirement_id,
            OLD.priority,
            NEW.priority,
            actor_id,
            reason_text
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_priority_audit
AFTER UPDATE OF priority
ON requirements
FOR EACH ROW
EXECUTE FUNCTION record_priority_change();

-- ============================================================
-- 14. DEPENDENCY READINESS FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION dependencies_ready(
    p_requirement_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM requirement_dependencies d
        JOIN requirements r
          ON r.requirement_id = d.depends_on_id
        WHERE d.requirement_id = p_requirement_id
          AND r.status <> 'COMPLETED'
    );
$$;

-- ============================================================
-- 15. PRIORITY SUMMARY VIEW
-- ============================================================

CREATE OR REPLACE VIEW priority_summary AS
SELECT
    p.product_id,
    p.product_name,
    r.priority,
    COUNT(r.requirement_id) AS requirement_count,
    COALESCE(SUM(r.effort_points), 0) AS total_effort,
    COALESCE(SUM(r.business_value), 0) AS total_business_value,
    ROUND(
        AVG(r.business_value)::NUMERIC,
        2
    ) AS average_business_value
FROM products p
LEFT JOIN requirements r
    ON r.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    r.priority;

-- ============================================================
-- 16. RELEASE CAPACITY REPORT
-- ============================================================

CREATE OR REPLACE VIEW release_capacity_report AS
SELECT
    rel.release_id,
    rel.release_name,
    rel.capacity_points,

    COALESCE(
        SUM(
            CASE
                WHEN req.priority = 'MUST_HAVE'
                 AND req.status <> 'COMPLETED'
                THEN req.effort_points
                ELSE 0
            END
        ), 0
    ) AS mandatory_effort,

    COALESCE(
        SUM(
            CASE
                WHEN req.priority <> 'WONT_HAVE'
                 AND req.status <> 'COMPLETED'
                THEN req.effort_points
                ELSE 0
            END
        ), 0
    ) AS proposed_effort,

    COALESCE(
        SUM(
            CASE
                WHEN req.priority = 'MUST_HAVE'
                 AND req.status <> 'COMPLETED'
                THEN req.effort_points
                ELSE 0
            END
        ), 0
    ) > rel.capacity_points AS mandatory_shortfall

FROM releases rel
LEFT JOIN requirements req
    ON req.release_id = rel.release_id
GROUP BY
    rel.release_id,
    rel.release_name,
    rel.capacity_points;

-- ============================================================
-- 17. RELEASE CANDIDATE EVALUATION FUNCTION
--
-- Must-have requirements are ranked first.
-- Other requirements are ranked by value/effort ratio.
-- Dependencies must be completed or selected.
-- ============================================================

CREATE OR REPLACE FUNCTION evaluate_release(
    p_release_id BIGINT
)
RETURNS TABLE (
    requirement_id BIGINT,
    requirement_code VARCHAR,
    title VARCHAR,
    priority requirement_priority,
    effort INTEGER,
    selected BOOLEAN,
    reason TEXT
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE candidates AS (
        SELECT
            r.requirement_id,
            r.requirement_code,
            r.title,
            r.priority,
            r.effort_points,
            r.business_value,
            ROW_NUMBER() OVER (
                ORDER BY
                    CASE r.priority
                        WHEN 'MUST_HAVE' THEN 1
                        WHEN 'SHOULD_HAVE' THEN 2
                        WHEN 'COULD_HAVE' THEN 3
                        ELSE 4
                    END,
                    CASE
                        WHEN r.priority = 'MUST_HAVE'
                        THEN 0
                        ELSE
                            r.business_value::NUMERIC /
                            r.effort_points
                    END DESC,
                    r.requirement_code
            ) AS position
        FROM requirements r
        WHERE r.release_id = p_release_id
          AND r.status <> 'COMPLETED'
          AND r.priority <> 'WONT_HAVE'
    ),
    allocation AS (
        SELECT
            c.*,
            SUM(c.effort_points) OVER (
                ORDER BY c.position
            ) AS cumulative_effort
        FROM candidates c
    )
    SELECT
        a.requirement_id,
        a.requirement_code::VARCHAR,
        a.title::VARCHAR,
        a.priority,
        a.effort_points,
        a.cumulative_effort <= rel.capacity_points,
        CASE
            WHEN a.cumulative_effort <= rel.capacity_points
            THEN 'Within estimated capacity'
            ELSE 'Capacity exceeded'
        END
    FROM allocation a
    CROSS JOIN releases rel
    WHERE rel.release_id = p_release_id
    ORDER BY a.position;
$$;

-- ============================================================
-- 18. SAMPLE DATA
-- ============================================================

INSERT INTO team_members (
    full_name, email, role_name
)
VALUES
    ('Product Owner', 'product@example.com', 'PRODUCT_OWNER'),
    ('Security Lead', 'security@example.com', 'SECURITY'),
    ('Payments Lead', 'payments@example.com', 'ENGINEERING'),
    ('Platform Lead', 'platform@example.com', 'ENGINEERING'),
    ('Analytics Lead', 'analytics@example.com', 'ENGINEERING'),
    ('Frontend Lead', 'frontend@example.com', 'ENGINEERING');

INSERT INTO products (
    product_name,
    description,
    product_owner
)
VALUES (
    'Enterprise Commerce Platform',
    'A secure enterprise commerce application.',
    1
);

INSERT INTO releases (
    product_id,
    release_name,
    capacity_points,
    status,
    planned_start,
    planned_end
)
VALUES (
    1,
    'Release 1.0',
    30,
    'PLANNING',
    '2026-12-01',
    '2026-12-31'
);

INSERT INTO requirements (
    product_id,
    release_id,
    requirement_code,
    title,
    description,
    priority,
    business_value,
    effort_points,
    owner_id
)
VALUES
(
    1, 1, 'R001',
    'User Authentication',
    'Secure login and session management.',
    'MUST_HAVE', 10, 8, 2
),
(
    1, 1, 'R002',
    'Payment Processing',
    'Secure payment transaction processing.',
    'MUST_HAVE', 10, 13, 3
),
(
    1, 1, 'R003',
    'Audit Logging',
    'Maintain operational and security audit records.',
    'MUST_HAVE', 9, 5, 4
),
(
    1, 1, 'R004',
    'Business Analytics',
    'Provide business performance dashboards.',
    'SHOULD_HAVE', 8, 8, 5
),
(
    1, 1, 'R005',
    'Email Notifications',
    'Send transactional email notifications.',
    'SHOULD_HAVE', 7, 5, 3
),
(
    1, 1, 'R006',
    'Custom Themes',
    'Allow users to select visual themes.',
    'COULD_HAVE', 4, 3, 6
),
(
    1, 1, 'R007',
    'Animated Backgrounds',
    'Provide decorative animated backgrounds.',
    'WONT_HAVE', 2, 5, 6
);

-- Payment processing depends on authentication.
INSERT INTO requirement_dependencies (
    requirement_id,
    depends_on_id
)
VALUES (2, 1);

-- ============================================================
-- 19. PRIORITY CHANGE TRANSACTION
-- ============================================================

BEGIN;

SELECT set_config('moscow.actor_id', '1', TRUE);

SELECT set_config(
    'moscow.change_reason',
    'Customer demand increased.',
    TRUE
);

UPDATE requirements
SET priority = 'SHOULD_HAVE'
WHERE requirement_code = 'R006';

COMMIT;

-- ============================================================
-- 20. RETRIEVAL
-- ============================================================

SELECT
    requirement_code,
    title,
    priority,
    status,
    business_value,
    effort_points
FROM requirements
ORDER BY
    CASE priority
        WHEN 'MUST_HAVE' THEN 1
        WHEN 'SHOULD_HAVE' THEN 2
        WHEN 'COULD_HAVE' THEN 3
        WHEN 'WONT_HAVE' THEN 4
    END,
    requirement_code;

-- ============================================================
-- 21. PRIORITY AGGREGATION
-- ============================================================

SELECT
    priority,
    COUNT(*) AS requirement_count,
    SUM(effort_points) AS total_effort,
    ROUND(AVG(business_value), 2) AS average_value
FROM requirements
GROUP BY priority
ORDER BY priority;

-- ============================================================
-- 22. DEPENDENCY VALIDATION
-- ============================================================

SELECT
    r.requirement_code,
    r.title,
    dependencies_ready(r.requirement_id) AS ready
FROM requirements r
ORDER BY r.requirement_code;

-- ============================================================
-- 23. DEPENDENCY REPORT
-- ============================================================

SELECT
    dependent.requirement_code AS requirement,
    dependency.requirement_code AS depends_on,
    dependency.status AS dependency_status
FROM requirement_dependencies d
JOIN requirements dependent
    ON dependent.requirement_id = d.requirement_id
JOIN requirements dependency
    ON dependency.requirement_id = d.depends_on_id;

-- ============================================================
-- 24. RELEASE CAPACITY EVALUATION
-- ============================================================

SELECT *
FROM release_capacity_report
WHERE release_id = 1;

SELECT *
FROM evaluate_release(1);

-- ============================================================
-- 25. PRIORITY CHANGE AUDIT REPORT
-- ============================================================

SELECT
    r.requirement_code,
    h.old_priority,
    h.new_priority,
    m.full_name AS changed_by,
    h.change_reason,
    h.changed_at
FROM priority_history h
JOIN requirements r
    ON r.requirement_id = h.requirement_id
JOIN team_members m
    ON m.member_id = h.changed_by
ORDER BY h.changed_at DESC;

-- ============================================================
-- 26. RELEASE ELIGIBILITY REPORT
-- ============================================================

SELECT
    r.requirement_code,
    r.title,
    r.priority,
    r.status,
    r.effort_points,
    CASE
        WHEN r.priority = 'WONT_HAVE'
            THEN 'EXCLUDED'
        WHEN r.status = 'COMPLETED'
            THEN 'ALREADY COMPLETED'
        WHEN NOT dependencies_ready(r.requirement_id)
            THEN 'BLOCKED BY DEPENDENCY'
        WHEN r.priority = 'MUST_HAVE'
            THEN 'MANDATORY CANDIDATE'
        ELSE 'OPTIONAL CANDIDATE'
    END AS eligibility
FROM requirements r
WHERE r.release_id = 1
ORDER BY r.requirement_code;

-- ============================================================
-- 27. COMPLETION REPORT
-- ============================================================

SELECT
    priority,
    COUNT(*) AS total,
    COUNT(*) FILTER (
        WHERE status = 'COMPLETED'
    ) AS completed,
    COUNT(*) FILTER (
        WHERE status = 'IN_PROGRESS'
    ) AS in_progress,
    COUNT(*) FILTER (
        WHERE status = 'DEFERRED'
    ) AS deferred
FROM requirements
GROUP BY priority
ORDER BY priority;

-- ============================================================
-- END OF MOSCOW PRIORITIZATION SYSTEM
-- ============================================================
