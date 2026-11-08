-- ============================================================
-- ROADMAP COMMUNICATION MANAGEMENT SYSTEM
-- PostgreSQL 15+
--
-- Domain:
--   Executive roadmaps
--   Engineering roadmaps
--   Sales roadmaps
--   Customer roadmaps
--
-- Includes:
--   Relational domain model
--   Audience-specific publication
--   Milestones and dependencies
--   Versioned roadmap snapshots
--   Risks and progress metrics
--   Approval workflow
--   Publication audit
--   Functions, procedures, views and triggers
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS roadmap;

SET search_path TO roadmap, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE roadmap.audience_type AS ENUM (
    'executive',
    'engineering',
    'sales',
    'customer'
);

CREATE TYPE roadmap.item_status AS ENUM (
    'planned',
    'in_progress',
    'blocked',
    'at_risk',
    'completed',
    'cancelled'
);

CREATE TYPE roadmap.priority_level AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);

CREATE TYPE roadmap.confidence_level AS ENUM (
    'high',
    'medium',
    'low'
);

CREATE TYPE roadmap.approval_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);

CREATE TYPE roadmap.publication_status AS ENUM (
    'draft',
    'under_review',
    'approved',
    'published',
    'withdrawn'
);

-- ============================================================
-- 2. ORGANIZATIONAL USERS
-- ============================================================

CREATE TABLE roadmap.users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roadmap.roadmaps (
    roadmap_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    roadmap_name VARCHAR(200) NOT NULL,
    owner_id BIGINT NOT NULL
        REFERENCES roadmap.users(user_id),
    description TEXT NOT NULL,
    planning_start DATE NOT NULL,
    planning_end DATE NOT NULL,
    current_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_roadmap_period
        CHECK (planning_end >= planning_start),

    CONSTRAINT valid_roadmap_version
        CHECK (current_version >= 1),

    CONSTRAINT unique_roadmap_name
        UNIQUE (roadmap_name)
);

-- ============================================================
-- 3. ROADMAP ITEMS
-- ============================================================

CREATE TABLE roadmap.roadmap_items (
    item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    roadmap_id BIGINT NOT NULL
        REFERENCES roadmap.roadmaps(roadmap_id)
        ON DELETE CASCADE,

    item_code VARCHAR(30) NOT NULL,
    title VARCHAR(250) NOT NULL,
    description TEXT NOT NULL,

    owner_id BIGINT NOT NULL
        REFERENCES roadmap.users(user_id),

    strategic_objective TEXT NOT NULL,
    business_value TEXT NOT NULL,
    engineering_details TEXT,
    sales_message TEXT,
    customer_impact TEXT,

    priority roadmap.priority_level NOT NULL,
    status roadmap.item_status NOT NULL DEFAULT 'planned',
    confidence roadmap.confidence_level NOT NULL DEFAULT 'medium',

    start_date DATE NOT NULL,
    target_date DATE NOT NULL,

    completion_percentage NUMERIC(5,2) NOT NULL DEFAULT 0,

    risk_description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_item_code
        UNIQUE (roadmap_id, item_code),

    CONSTRAINT valid_item_dates
        CHECK (target_date >= start_date),

    CONSTRAINT valid_completion
        CHECK (
            completion_percentage BETWEEN 0 AND 100
        ),

    CONSTRAINT planned_progress_consistency
        CHECK (
            status <> 'planned'
            OR completion_percentage = 0
        ),

    CONSTRAINT completed_progress_consistency
        CHECK (
            status <> 'completed'
            OR completion_percentage = 100
        )
);

CREATE INDEX idx_items_roadmap_status
    ON roadmap.roadmap_items(roadmap_id, status);

CREATE INDEX idx_items_owner
    ON roadmap.roadmap_items(owner_id);

CREATE INDEX idx_items_target_date
    ON roadmap.roadmap_items(target_date);

CREATE INDEX idx_items_risk
    ON roadmap.roadmap_items(roadmap_id, priority)
    WHERE status IN ('blocked', 'at_risk');

-- ============================================================
-- 4. DEPENDENCIES
-- ============================================================

CREATE TABLE roadmap.item_dependencies (
    item_id BIGINT NOT NULL
        REFERENCES roadmap.roadmap_items(item_id)
        ON DELETE CASCADE,

    dependency_item_id BIGINT NOT NULL
        REFERENCES roadmap.roadmap_items(item_id)
        ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (item_id, dependency_item_id),

    CONSTRAINT no_self_dependency
        CHECK (item_id <> dependency_item_id)
);

CREATE INDEX idx_dependencies_reverse
    ON roadmap.item_dependencies(dependency_item_id);

-- Prevent dependency cycles using recursive traversal.
CREATE OR REPLACE FUNCTION roadmap.prevent_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
    different_roadmaps BOOLEAN;
BEGIN
    SELECT
        source.roadmap_id <> dependency.roadmap_id
    INTO different_roadmaps
    FROM roadmap.roadmap_items source
    JOIN roadmap.roadmap_items dependency
        ON dependency.item_id = NEW.dependency_item_id
    WHERE source.item_id = NEW.item_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Roadmap item does not exist.';
    END IF;

    IF different_roadmaps THEN
        RAISE EXCEPTION
            'Dependencies must belong to the same roadmap.';
    END IF;

    WITH RECURSIVE dependency_tree(item_id) AS (
        SELECT NEW.dependency_item_id

        UNION

        SELECT d.dependency_item_id
        FROM roadmap.item_dependencies d
        JOIN dependency_tree tree
            ON d.item_id = tree.item_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_tree
        WHERE item_id = NEW.item_id
    )
    INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION 'Circular dependency detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_dependency_cycle
BEFORE INSERT OR UPDATE
ON roadmap.item_dependencies
FOR EACH ROW
EXECUTE FUNCTION roadmap.prevent_dependency_cycle();

-- ============================================================
-- 5. MILESTONES
-- ============================================================

CREATE TABLE roadmap.milestones (
    milestone_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    item_id BIGINT NOT NULL
        REFERENCES roadmap.roadmap_items(item_id)
        ON DELETE CASCADE,

    milestone_name VARCHAR(200) NOT NULL,
    description TEXT,

    target_date DATE NOT NULL,

    status roadmap.item_status NOT NULL DEFAULT 'planned',

    completion_percentage NUMERIC(5,2) NOT NULL DEFAULT 0,

    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_milestone_progress
        CHECK (completion_percentage BETWEEN 0 AND 100),

    CONSTRAINT milestone_completed_progress
        CHECK (
            status <> 'completed'
            OR completion_percentage = 100
        )
);

CREATE INDEX idx_milestone_item
    ON roadmap.milestones(item_id, target_date);

-- ============================================================
-- 6. AUDIENCE-SPECIFIC COMMUNICATION
-- ============================================================

CREATE TABLE roadmap.audience_messages (
    message_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    item_id BIGINT NOT NULL
        REFERENCES roadmap.roadmap_items(item_id)
        ON DELETE CASCADE,

    audience roadmap.audience_type NOT NULL,

    message_title VARCHAR(250) NOT NULL,
    message_body TEXT NOT NULL,

    visibility_level VARCHAR(30) NOT NULL DEFAULT 'internal',

    created_by BIGINT NOT NULL
        REFERENCES roadmap.users(user_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_visibility
        CHECK (
            visibility_level IN (
                'internal',
                'restricted',
                'public'
            )
        ),

    CONSTRAINT unique_audience_message
        UNIQUE (item_id, audience)
);

CREATE INDEX idx_messages_audience
    ON roadmap.audience_messages(audience, created_at DESC);

-- ============================================================
-- 7. ROADMAP VERSIONING
-- ============================================================

CREATE TABLE roadmap.roadmap_versions (
    version_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    roadmap_id BIGINT NOT NULL
        REFERENCES roadmap.roadmaps(roadmap_id)
        ON DELETE CASCADE,

    version_number INTEGER NOT NULL,

    change_summary TEXT NOT NULL,

    snapshot JSONB NOT NULL,

    created_by BIGINT NOT NULL
        REFERENCES roadmap.users(user_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_version_number
        CHECK (version_number >= 1),

    CONSTRAINT unique_roadmap_version
        UNIQUE (roadmap_id, version_number)
);

CREATE INDEX idx_versions_history
    ON roadmap.roadmap_versions(
        roadmap_id,
        version_number DESC
    );

-- ============================================================
-- 8. COMMUNICATION APPROVAL
-- ============================================================

CREATE TABLE roadmap.communication_approvals (
    approval_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    roadmap_id BIGINT NOT NULL
        REFERENCES roadmap.roadmaps(roadmap_id)
        ON DELETE CASCADE,

    version_number INTEGER NOT NULL,

    audience roadmap.audience_type NOT NULL,

    reviewer_id BIGINT NOT NULL
        REFERENCES roadmap.users(user_id),

    status roadmap.approval_status NOT NULL DEFAULT 'pending',

    comments TEXT,

    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_version_reviewer
        UNIQUE (
            roadmap_id,
            version_number,
            audience,
            reviewer_id
        )
);

CREATE INDEX idx_approval_workflow
    ON roadmap.communication_approvals(
        roadmap_id,
        version_number,
        audience,
        status
    );

-- ============================================================
-- 9. PUBLICATION RECORDS
-- ============================================================

CREATE TABLE roadmap.publications (
    publication_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    roadmap_id BIGINT NOT NULL
        REFERENCES roadmap.roadmaps(roadmap_id)
        ON DELETE CASCADE,

    version_number INTEGER NOT NULL,

    audience roadmap.audience_type NOT NULL,

    status roadmap.publication_status NOT NULL DEFAULT 'draft',

    published_by BIGINT
        REFERENCES roadmap.users(user_id),

    published_at TIMESTAMPTZ,

    content JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_publication
        UNIQUE (roadmap_id, version_number, audience)
);

CREATE INDEX idx_publication_audience
    ON roadmap.publications(audience, status);

-- ============================================================
-- 10. AUDIT LOG
-- ============================================================

CREATE TABLE roadmap.audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT NOT NULL,

    action VARCHAR(80) NOT NULL,

    performed_by BIGINT
        REFERENCES roadmap.users(user_id),

    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    performed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_entity
    ON roadmap.audit_log(entity_type, entity_id, performed_at DESC);

-- ============================================================
-- 11. UPDATE TIMESTAMPS
-- ============================================================

CREATE OR REPLACE FUNCTION roadmap.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_roadmap_updated
BEFORE UPDATE ON roadmap.roadmaps
FOR EACH ROW
EXECUTE FUNCTION roadmap.set_updated_at();

CREATE TRIGGER trg_item_updated
BEFORE UPDATE ON roadmap.roadmap_items
FOR EACH ROW
EXECUTE FUNCTION roadmap.set_updated_at();

-- ============================================================
-- 12. PROGRESS CALCULATION
-- ============================================================

CREATE OR REPLACE FUNCTION roadmap.calculate_progress(
    p_roadmap_id BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(
        ROUND(AVG(completion_percentage), 2),
        0
    )
    FROM roadmap.roadmap_items
    WHERE roadmap_id = p_roadmap_id
      AND status <> 'cancelled';
$$;

-- ============================================================
-- 13. DEPENDENCY READINESS
-- ============================================================

CREATE OR REPLACE FUNCTION roadmap.dependencies_ready(
    p_item_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM roadmap.item_dependencies d
        JOIN roadmap.roadmap_items dependency
            ON dependency.item_id = d.dependency_item_id
        WHERE d.item_id = p_item_id
          AND dependency.status <> 'completed'
    );
$$;

-- ============================================================
-- 14. SNAPSHOT CREATION
-- ============================================================

CREATE OR REPLACE FUNCTION roadmap.create_snapshot(
    p_roadmap_id BIGINT,
    p_user_id BIGINT,
    p_change_summary TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    next_version INTEGER;
    snapshot_data JSONB;
    result_id BIGINT;
BEGIN
    PERFORM 1
    FROM roadmap.roadmaps
    WHERE roadmap_id = p_roadmap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Roadmap does not exist.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM roadmap.users
        WHERE user_id = p_user_id
          AND active = TRUE
    ) THEN
        RAISE EXCEPTION 'Active snapshot creator required.';
    END IF;

    SELECT current_version + 1
    INTO next_version
    FROM roadmap.roadmaps
    WHERE roadmap_id = p_roadmap_id;

    SELECT jsonb_build_object(
        'roadmap_id', p_roadmap_id,
        'version', next_version,
        'created_at', CURRENT_TIMESTAMP,
        'items',
        COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'item_code', i.item_code,
                    'title', i.title,
                    'status', i.status,
                    'priority', i.priority,
                    'progress', i.completion_percentage,
                    'target_date', i.target_date,
                    'confidence', i.confidence,
                    'risk', i.risk_description
                )
                ORDER BY i.target_date
            ),
            '[]'::jsonb
        )
    )
    INTO snapshot_data
    FROM roadmap.roadmap_items i
    WHERE i.roadmap_id = p_roadmap_id;

    INSERT INTO roadmap.roadmap_versions (
        roadmap_id,
        version_number,
        change_summary,
        snapshot,
        created_by
    )
    VALUES (
        p_roadmap_id,
        next_version,
        p_change_summary,
        snapshot_data,
        p_user_id
    )
    RETURNING version_id INTO result_id;

    UPDATE roadmap.roadmaps
    SET current_version = next_version
    WHERE roadmap_id = p_roadmap_id;

    INSERT INTO roadmap.audit_log (
        entity_type,
        entity_id,
        action,
        performed_by,
        details
    )
    VALUES (
        'roadmap',
        p_roadmap_id,
        'SNAPSHOT_CREATED',
        p_user_id,
        jsonb_build_object(
            'version', next_version,
            'summary', p_change_summary
        )
    );

    RETURN result_id;
END;
$$;

-- ============================================================
-- 15. PUBLICATION ELIGIBILITY
-- ============================================================

CREATE OR REPLACE FUNCTION roadmap.publication_eligible(
    p_roadmap_id BIGINT,
    p_version INTEGER,
    p_audience roadmap.audience_type
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    approval_count INTEGER;
BEGIN
    -- Require one active approval for each audience publication.
    SELECT COUNT(*)
    INTO approval_count
    FROM roadmap.communication_approvals a
    JOIN roadmap.users u
        ON u.user_id = a.reviewer_id
    WHERE a.roadmap_id = p_roadmap_id
      AND a.version_number = p_version
      AND a.audience = p_audience
      AND a.status = 'approved'
      AND u.active = TRUE;

    RETURN approval_count >= 1
       AND EXISTS (
            SELECT 1
            FROM roadmap.roadmap_versions v
            WHERE v.roadmap_id = p_roadmap_id
              AND v.version_number = p_version
       );
END;
$$;

-- ============================================================
-- 16. PUBLICATION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE roadmap.publish_roadmap(
    p_roadmap_id BIGINT,
    p_version INTEGER,
    p_audience roadmap.audience_type,
    p_user_id BIGINT,
    p_content JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_publication_status roadmap.publication_status;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM roadmap.users
        WHERE user_id = p_user_id
          AND active = TRUE
    ) THEN
        RAISE EXCEPTION 'Active publisher required.';
    END IF;

    IF NOT roadmap.publication_eligible(
        p_roadmap_id,
        p_version,
        p_audience
    ) THEN
        RAISE EXCEPTION
            'Publication requires an approved roadmap version.';
    END IF;

    SELECT status
    INTO current_publication_status
    FROM roadmap.publications
    WHERE roadmap_id = p_roadmap_id
      AND version_number = p_version
      AND audience = p_audience
    FOR UPDATE;

    IF FOUND AND current_publication_status = 'published' THEN
        RAISE EXCEPTION 'Publication is already published.';
    END IF;

    INSERT INTO roadmap.publications (
        roadmap_id,
        version_number,
        audience,
        status,
        published_by,
        published_at,
        content
    )
    VALUES (
        p_roadmap_id,
        p_version,
        p_audience,
        'published',
        p_user_id,
        CURRENT_TIMESTAMP,
        p_content
    )
    ON CONFLICT (
        roadmap_id,
        version_number,
        audience
    )
    DO UPDATE SET
        status = 'published',
        published_by = EXCLUDED.published_by,
        published_at = EXCLUDED.published_at,
        content = EXCLUDED.content;

    INSERT INTO roadmap.audit_log (
        entity_type,
        entity_id,
        action,
        performed_by,
        details
    )
    VALUES (
        'publication',
        p_roadmap_id,
        'ROADMAP_PUBLISHED',
        p_user_id,
        jsonb_build_object(
            'version', p_version,
            'audience', p_audience
        )
    );
END;
$$;

-- ============================================================
-- 17. COMMUNICATION VIEWS
-- ============================================================

-- Executive view: strategic value, status and risk.
CREATE VIEW roadmap.executive_roadmap_view AS
SELECT
    r.roadmap_name,
    i.item_code,
    i.title,
    i.strategic_objective,
    i.business_value,
    i.status,
    i.priority,
    i.confidence,
    i.target_date,
    i.completion_percentage,
    i.risk_description,
    u.full_name AS accountable_owner
FROM roadmap.roadmap_items i
JOIN roadmap.roadmaps r
    ON r.roadmap_id = i.roadmap_id
JOIN roadmap.users u
    ON u.user_id = i.owner_id;

-- Engineering view: technical scope and dependencies.
CREATE VIEW roadmap.engineering_roadmap_view AS
SELECT
    i.item_id,
    i.item_code,
    i.title,
    i.engineering_details,
    i.status,
    i.priority,
    i.completion_percentage,
    i.target_date,
    u.full_name AS technical_owner,
    COALESCE(
        jsonb_agg(d.dependency_item_id)
            FILTER (WHERE d.dependency_item_id IS NOT NULL),
        '[]'::jsonb
    ) AS dependencies
FROM roadmap.roadmap_items i
JOIN roadmap.users u
    ON u.user_id = i.owner_id
LEFT JOIN roadmap.item_dependencies d
    ON d.item_id = i.item_id
GROUP BY
    i.item_id,
    i.item_code,
    i.title,
    i.engineering_details,
    i.status,
    i.priority,
    i.completion_percentage,
    i.target_date,
    u.full_name;

-- Sales view: commercial positioning.
CREATE VIEW roadmap.sales_roadmap_view AS
SELECT
    item_code,
    title,
    business_value,
    sales_message,
    status,
    confidence,
    target_date
FROM roadmap.roadmap_items
WHERE status <> 'cancelled';

-- Customer view: customer-safe information only.
CREATE VIEW roadmap.customer_roadmap_view AS
SELECT
    item_code,
    title,
    customer_impact,
    status,
    target_date
FROM roadmap.roadmap_items
WHERE status NOT IN ('blocked', 'cancelled');

-- ============================================================
-- 18. SAMPLE ORGANIZATIONAL DATA
-- ============================================================

INSERT INTO roadmap.users (
    full_name,
    email,
    department
)
VALUES
(
    'Ananya Sharma',
    'ananya.sharma@example.com',
    'Product Management'
),
(
    'Rahul Verma',
    'rahul.verma@example.com',
    'Engineering'
),
(
    'Priya Singh',
    'priya.singh@example.com',
    'Sales'
),
(
    'Amit Kumar',
    'amit.kumar@example.com',
    'Customer Success'
),
(
    'Neha Gupta',
    'neha.gupta@example.com',
    'Executive Management'
);

INSERT INTO roadmap.roadmaps (
    roadmap_name,
    owner_id,
    description,
    planning_start,
    planning_end
)
VALUES (
    'Enterprise Product Platform 2027',
    1,
    'Enterprise platform strategic and delivery roadmap.',
    DATE '2026-10-01',
    DATE '2027-12-31'
);

INSERT INTO roadmap.roadmap_items (
    roadmap_id,
    item_code,
    title,
    description,
    owner_id,
    strategic_objective,
    business_value,
    engineering_details,
    sales_message,
    customer_impact,
    priority,
    status,
    confidence,
    start_date,
    target_date,
    completion_percentage,
    risk_description
)
VALUES
(
    1,
    'RM-001',
    'Identity Management',
    'Centralized enterprise authentication.',
    2,
    'Improve enterprise security.',
    'Reduce access-management risks.',
    'OIDC, OAuth 2.0 and RBAC implementation.',
    'Enterprise identity controls are available.',
    'Improved account security.',
    'critical',
    'completed',
    'high',
    DATE '2026-10-01',
    DATE '2026-12-15',
    100,
    NULL
),
(
    1,
    'RM-002',
    'Analytics Dashboard',
    'Interactive operational analytics.',
    2,
    'Increase decision visibility.',
    'Faster operational decisions.',
    'Event ingestion, aggregation APIs and dashboard UI.',
    'Advanced operational analytics.',
    'Improved business performance visibility.',
    'high',
    'in_progress',
    'medium',
    DATE '2026-11-01',
    DATE '2027-02-15',
    55,
    NULL
),
(
    1,
    'RM-003',
    'Automated Reporting',
    'Scheduled enterprise reporting.',
    2,
    'Standardize reporting.',
    'Reduce manual reporting effort.',
    'Scheduled jobs and report export APIs.',
    'Automated business reporting.',
    'Consistent scheduled reports.',
    'high',
    'at_risk',
    'low',
    DATE '2026-11-15',
    DATE '2027-03-15',
    20,
    'Data integration capacity constraints.'
),
(
    1,
    'RM-004',
    'Customer Self-Service Portal',
    'Customer account and service portal.',
    2,
    'Improve customer autonomy.',
    'Reduce support workload.',
    'Frontend portal and customer API integration.',
    'Self-service portal is planned.',
    'Simplified account management.',
    'medium',
    'planned',
    'high',
    DATE '2027-01-01',
    DATE '2027-04-30',
    0,
    NULL
);

INSERT INTO roadmap.item_dependencies (
    item_id,
    dependency_item_id
)
VALUES
(2, 1),
(3, 2),
(4, 1);

INSERT INTO roadmap.milestones (
    item_id,
    milestone_name,
    description,
    target_date,
    status,
    completion_percentage,
    completed_at
)
VALUES
(
    1,
    'Authentication service',
    'Core authentication implementation.',
    DATE '2026-11-15',
    'completed',
    100,
    CURRENT_TIMESTAMP
),
(
    2,
    'Data ingestion',
    'Initial data ingestion service.',
    DATE '2026-12-15',
    'completed',
    100,
    CURRENT_TIMESTAMP
),
(
    2,
    'Dashboard integration',
    'Dashboard frontend integration.',
    DATE '2027-01-30',
    'in_progress',
    40,
    NULL
),
(
    3,
    'Reporting integration',
    'Reporting data-source integration.',
    DATE '2027-02-15',
    'at_risk',
    20,
    NULL
);

-- ============================================================
-- 19. AUDIENCE MESSAGES
-- ============================================================

INSERT INTO roadmap.audience_messages (
    item_id,
    audience,
    message_title,
    message_body,
    visibility_level,
    created_by
)
VALUES
(
    1,
    'executive',
    'Identity Management Delivered',
    'Centralized identity controls have been completed.',
    'internal',
    1
),
(
    2,
    'engineering',
    'Analytics Engineering Scope',
    'Event ingestion and dashboard integration remain active.',
    'internal',
    2
),
(
    3,
    'sales',
    'Reporting Availability',
    'Automated reporting remains under development.',
    'restricted',
    3
),
(
    4,
    'customer',
    'Self-Service Portal',
    'Customer account self-service is planned.',
    'public',
    4
);

-- ============================================================
-- 20. CREATE INITIAL VERSION
-- ============================================================

SELECT roadmap.create_snapshot(
    1,
    1,
    'Initial enterprise roadmap baseline.'
);

-- ============================================================
-- 21. APPROVALS
-- ============================================================

INSERT INTO roadmap.communication_approvals (
    roadmap_id,
    version_number,
    audience,
    reviewer_id,
    status,
    comments,
    reviewed_at
)
VALUES
(
    1,
    2,
    'executive',
    5,
    'approved',
    'Strategic direction reviewed.',
    CURRENT_TIMESTAMP
),
(
    1,
    2,
    'engineering',
    2,
    'approved',
    'Engineering scope reviewed.',
    CURRENT_TIMESTAMP
),
(
    1,
    2,
    'sales',
    3,
    'pending',
    'Awaiting commercial review.',
    NULL
),
(
    1,
    2,
    'customer',
    4,
    'approved',
    'Customer communication reviewed.',
    CURRENT_TIMESTAMP
);

-- ============================================================
-- 22. REPORTING QUERIES
-- ============================================================

-- Query A: Retrieve executive roadmap.
SELECT *
FROM roadmap.executive_roadmap_view
ORDER BY target_date;

-- Query B: Retrieve engineering delivery details.
SELECT *
FROM roadmap.engineering_roadmap_view
ORDER BY target_date;

-- Query C: Retrieve sales roadmap.
SELECT *
FROM roadmap.sales_roadmap_view
ORDER BY target_date;

-- Query D: Retrieve customer-safe roadmap.
SELECT *
FROM roadmap.customer_roadmap_view
ORDER BY target_date;

-- Query E: Calculate portfolio progress.
SELECT
    roadmap.calculate_progress(1) AS portfolio_progress;

-- Query F: Evaluate dependency readiness.
SELECT
    i.item_code,
    i.title,
    roadmap.dependencies_ready(i.item_id) AS dependencies_ready
FROM roadmap.roadmap_items i
WHERE i.roadmap_id = 1;

-- Query G: Risk aggregation.
SELECT
    status,
    COUNT(*) AS item_count,
    ROUND(AVG(completion_percentage), 2) AS average_progress
FROM roadmap.roadmap_items
WHERE roadmap_id = 1
  AND status IN ('blocked', 'at_risk')
GROUP BY status;

-- Query H: Priority distribution.
SELECT
    priority,
    COUNT(*) AS total_items
FROM roadmap.roadmap_items
WHERE roadmap_id = 1
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;

-- Query I: Milestone tracking.
SELECT
    i.item_code,
    i.title,
    m.milestone_name,
    m.target_date,
    m.status,
    m.completion_percentage
FROM roadmap.milestones m
JOIN roadmap.roadmap_items i
    ON i.item_id = m.item_id
ORDER BY m.target_date;

-- Query J: Identify delayed or at-risk initiatives.
SELECT
    item_code,
    title,
    target_date,
    status,
    risk_description
FROM roadmap.roadmap_items
WHERE status IN ('blocked', 'at_risk')
   OR (
       target_date < CURRENT_DATE
       AND status <> 'completed'
       AND status <> 'cancelled'
   );

-- Query K: CTE-based dependency reporting.
WITH RECURSIVE dependency_tree AS (
    SELECT
        item_id,
        dependency_item_id,
        1 AS dependency_depth
    FROM roadmap.item_dependencies

    UNION ALL

    SELECT
        d.item_id,
        tree.dependency_item_id,
        tree.dependency_depth + 1
    FROM roadmap.item_dependencies d
    JOIN dependency_tree tree
        ON d.dependency_item_id = tree.item_id
)
SELECT
    source.item_code AS dependent_item,
    dependency.item_code AS prerequisite_item,
    MAX(tree.dependency_depth) AS dependency_depth
FROM dependency_tree tree
JOIN roadmap.roadmap_items source
    ON source.item_id = tree.item_id
JOIN roadmap.roadmap_items dependency
    ON dependency.item_id = tree.dependency_item_id
GROUP BY source.item_code, dependency.item_code
ORDER BY source.item_code, dependency.item_code;

-- Query L: Audience approval evaluation.
SELECT
    a.audience,
    COUNT(*) FILTER (
        WHERE a.status = 'approved'
          AND u.active = TRUE
    ) AS approved_reviews,
    COUNT(*) FILTER (
        WHERE a.status = 'pending'
    ) AS pending_reviews
FROM roadmap.communication_approvals a
JOIN roadmap.users u
    ON u.user_id = a.reviewer_id
WHERE a.roadmap_id = 1
  AND a.version_number = 2
GROUP BY a.audience;

-- Query M: Version history.
SELECT
    version_number,
    change_summary,
    created_at,
    snapshot
FROM roadmap.roadmap_versions
WHERE roadmap_id = 1
ORDER BY version_number DESC;

-- ============================================================
-- 23. VALIDATION AND FAILURE DEMONSTRATIONS
-- ============================================================

-- The following statements are intentionally isolated in
-- exception-handling blocks so the complete script can run.

DO $$
BEGIN
    BEGIN
        INSERT INTO roadmap.roadmap_items (
            roadmap_id,
            item_code,
            title,
            description,
            owner_id,
            strategic_objective,
            business_value,
            priority,
            status,
            start_date,
            target_date,
            completion_percentage
        )
        VALUES (
            1,
            'INVALID-001',
            'Invalid date example',
            'This insert should fail.',
            2,
            'Test validation.',
            'No business value.',
            'low',
            'planned',
            DATE '2027-05-01',
            DATE '2027-01-01',
            0
        );

        RAISE EXCEPTION
            'Validation failure was not detected.';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Invalid date correctly rejected.';
    END;

    BEGIN
        INSERT INTO roadmap.roadmap_items (
            roadmap_id,
            item_code,
            title,
            description,
            owner_id,
            strategic_objective,
            business_value,
            priority,
            status,
            start_date,
            target_date,
            completion_percentage
        )
        VALUES (
            1,
            'INVALID-002',
            'Invalid planned progress',
            'This insert should fail.',
            2,
            'Test validation.',
            'No business value.',
            'low',
            'planned',
            DATE '2027-01-01',
            DATE '2027-02-01',
            50
        );

        RAISE EXCEPTION
            'Planned progress validation was not detected.';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Invalid planned progress correctly rejected.';
    END;

    BEGIN
        INSERT INTO roadmap.item_dependencies (
            item_id,
            dependency_item_id
        )
        VALUES (1, 3);

        RAISE EXCEPTION
            'Circular dependency validation was not detected.';
    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM =
                'Circular dependency validation was not detected.'
            THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Circular dependency correctly rejected.';
    END;
END;
$$;

-- ============================================================
-- 24. TRANSACTIONAL PUBLICATION EXAMPLE
-- ============================================================

-- Publish only the approved executive version.
-- Sales remains pending and therefore cannot be published.

DO $$
BEGIN
    BEGIN
        CALL roadmap.publish_roadmap(
            1,
            2,
            'executive',
            5,
            jsonb_build_object(
                'title', 'Executive Product Roadmap 2027',
                'progress', roadmap.calculate_progress(1),
                'audience', 'executive'
            )
        );

        RAISE NOTICE 'Executive roadmap published.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Executive publication failed: %', SQLERRM;
    END;

    BEGIN
        CALL roadmap.publish_roadmap(
            1,
            2,
            'sales',
            3,
            jsonb_build_object(
                'title', 'Sales Product Roadmap 2027'
            )
        );

        RAISE NOTICE 'Sales roadmap published.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Sales publication correctly restricted: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 25. FINAL PUBLICATION REPORT
-- ============================================================

SELECT
    p.publication_id,
    r.roadmap_name,
    p.version_number,
    p.audience,
    p.status,
    u.full_name AS publisher,
    p.published_at
FROM roadmap.publications p
JOIN roadmap.roadmaps r
    ON r.roadmap_id = p.roadmap_id
LEFT JOIN roadmap.users u
    ON u.user_id = p.published_by
ORDER BY p.published_at DESC;

SELECT
    entity_type,
    action,
    performed_by,
    details,
    performed_at
FROM roadmap.audit_log
ORDER BY performed_at DESC;

COMMIT;

-- ============================================================
-- SECURITY AND PRODUCTION NOTES
-- ============================================================
--
-- 1. Restrict access to internal roadmap tables.
-- 2. Grant customer users access only to approved customer views.
-- 3. Use separate database roles for authors, reviewers,
--    publishers and reporting consumers.
-- 4. Apply row-level security where tenant isolation is needed.
-- 5. Restrict publication procedures to authorized publishers.
-- 6. Store immutable version snapshots for auditability.
-- 7. Use parameterized queries from application services.
-- 8. Review approval freshness when a new version is created.
-- 9. Configure backup and retention policies.
-- 10. Monitor long-running recursive dependency queries.
--
-- The database stores roadmap governance and publication state.
-- It does not replace an external authentication provider.
-- ============================================================
