/*
 * ROADMAP MANAGEMENT AND STRATEGIC PLANNING DATABASE
 *
 * PostgreSQL 15+
 *
 * Supports:
 * 1. Feature roadmaps.
 * 2. Outcome roadmaps.
 * 3. Theme roadmaps.
 * 4. Now-Next-Later roadmaps.
 *
 * Includes:
 * - Relational domain model.
 * - Referential integrity.
 * - Dependency validation and cycle detection.
 * - Metric tracking.
 * - Strategic theme alignment.
 * - Prioritization.
 * - Lifecycle management.
 * - Audit history.
 * - Reporting views.
 * - Transactional workflow operations.
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS roadmap;

SET search_path TO roadmap, public;

-- =========================================================
-- DOMAIN TYPES
-- =========================================================

CREATE TYPE roadmap_type AS ENUM (
    'feature',
    'outcome',
    'theme',
    'now_next_later'
);

CREATE TYPE item_status AS ENUM (
    'proposed',
    'planned',
    'in_progress',
    'blocked',
    'completed',
    'cancelled'
);

CREATE TYPE priority_level AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);

CREATE TYPE planning_horizon AS ENUM (
    'now',
    'next',
    'later'
);

CREATE TYPE theme_state AS ENUM (
    'active',
    'paused',
    'retired'
);

-- =========================================================
-- USERS AND ORGANIZATIONAL OWNERSHIP
-- =========================================================

CREATE TABLE roadmap_users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_email
        CHECK (POSITION('@' IN email) > 1)
);

-- =========================================================
-- ROADMAPS
-- =========================================================

CREATE TABLE roadmaps (
    roadmap_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    roadmap_type roadmap_type NOT NULL,
    owner_id BIGINT NOT NULL
        REFERENCES roadmap_users(user_id),
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_roadmap_name
        CHECK (LENGTH(TRIM(name)) > 0),

    CONSTRAINT positive_version
        CHECK (version > 0)
);

CREATE INDEX idx_roadmaps_owner
    ON roadmaps(owner_id);

CREATE INDEX idx_roadmaps_type_active
    ON roadmaps(roadmap_type, is_active);

-- =========================================================
-- STRATEGIC THEMES
-- =========================================================

CREATE TABLE strategic_themes (
    theme_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    roadmap_id BIGINT NOT NULL
        REFERENCES roadmaps(roadmap_id)
        ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    objective TEXT NOT NULL,
    owner_id BIGINT NOT NULL
        REFERENCES roadmap_users(user_id),
    state theme_state NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_theme_name
        UNIQUE (roadmap_id, name),

    CONSTRAINT valid_theme_name
        CHECK (LENGTH(TRIM(name)) > 0)
);

CREATE INDEX idx_themes_roadmap
    ON strategic_themes(roadmap_id, state);

-- =========================================================
-- ROADMAP ITEMS
-- =========================================================

CREATE TABLE roadmap_items (
    item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    roadmap_id BIGINT NOT NULL
        REFERENCES roadmaps(roadmap_id)
        ON DELETE CASCADE,

    theme_id BIGINT
        REFERENCES strategic_themes(theme_id),

    title VARCHAR(250) NOT NULL,
    description TEXT NOT NULL DEFAULT '',

    owner_id BIGINT NOT NULL
        REFERENCES roadmap_users(user_id),

    priority priority_level NOT NULL DEFAULT 'medium',
    status item_status NOT NULL DEFAULT 'proposed',

    horizon planning_horizon,

    start_date DATE,
    target_date DATE,

    progress NUMERIC(5,2) NOT NULL DEFAULT 0,
    confidence NUMERIC(4,3) NOT NULL DEFAULT 0.800,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    version INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT valid_item_title
        CHECK (LENGTH(TRIM(title)) > 0),

    CONSTRAINT valid_progress
        CHECK (progress BETWEEN 0 AND 100),

    CONSTRAINT valid_confidence
        CHECK (confidence BETWEEN 0 AND 1),

    CONSTRAINT valid_dates
        CHECK (
            start_date IS NULL
            OR target_date IS NULL
            OR start_date <= target_date
        ),

    CONSTRAINT positive_item_version
        CHECK (version > 0),

    CONSTRAINT unique_item_title
        UNIQUE (roadmap_id, title)
);

CREATE INDEX idx_items_roadmap_status
    ON roadmap_items(roadmap_id, status);

CREATE INDEX idx_items_priority
    ON roadmap_items(priority, confidence DESC);

CREATE INDEX idx_items_horizon
    ON roadmap_items(roadmap_id, horizon)
    WHERE horizon IS NOT NULL;

CREATE INDEX idx_items_owner
    ON roadmap_items(owner_id);

-- =========================================================
-- OUTCOME METRICS
-- =========================================================

CREATE TABLE outcome_metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    item_id BIGINT NOT NULL UNIQUE
        REFERENCES roadmap_items(item_id)
        ON DELETE CASCADE,

    metric_name VARCHAR(200) NOT NULL,
    baseline NUMERIC(18,4) NOT NULL,
    target NUMERIC(18,4) NOT NULL,
    current_value NUMERIC(18,4) NOT NULL,
    unit VARCHAR(50) NOT NULL DEFAULT '',

    measurement_date DATE NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT valid_metric_name
        CHECK (LENGTH(TRIM(metric_name)) > 0),

    CONSTRAINT nonnegative_metric_values
        CHECK (
            baseline >= 0
            AND target >= 0
            AND current_value >= 0
        )
);

CREATE INDEX idx_metrics_measurement
    ON outcome_metrics(measurement_date);

-- =========================================================
-- DEPENDENCY RELATIONSHIPS
-- =========================================================

CREATE TABLE item_dependencies (
    item_id BIGINT NOT NULL
        REFERENCES roadmap_items(item_id)
        ON DELETE CASCADE,

    depends_on_item_id BIGINT NOT NULL
        REFERENCES roadmap_items(item_id)
        ON DELETE CASCADE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (item_id, depends_on_item_id),

    CONSTRAINT no_self_dependency
        CHECK (item_id <> depends_on_item_id)
);

CREATE INDEX idx_dependencies_reverse
    ON item_dependencies(depends_on_item_id);

-- =========================================================
-- TAGS
-- =========================================================

CREATE TABLE roadmap_tags (
    tag_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    roadmap_id BIGINT NOT NULL
        REFERENCES roadmaps(roadmap_id)
        ON DELETE CASCADE,
    tag_name VARCHAR(80) NOT NULL,

    UNIQUE (roadmap_id, tag_name)
);

CREATE TABLE item_tags (
    item_id BIGINT NOT NULL
        REFERENCES roadmap_items(item_id)
        ON DELETE CASCADE,

    tag_id BIGINT NOT NULL
        REFERENCES roadmap_tags(tag_id)
        ON DELETE CASCADE,

    PRIMARY KEY (item_id, tag_id)
);

-- =========================================================
-- AUDIT HISTORY
-- =========================================================

CREATE TABLE roadmap_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL
        REFERENCES roadmap_items(item_id)
        ON DELETE CASCADE,

    previous_status item_status,
    new_status item_status,

    previous_progress NUMERIC(5,2),
    new_progress NUMERIC(5,2),

    changed_by BIGINT
        REFERENCES roadmap_users(user_id),

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_audit_item_date
    ON roadmap_audit(item_id, changed_at DESC);

-- =========================================================
-- ROADMAP TYPE INTEGRITY
-- =========================================================

CREATE OR REPLACE FUNCTION validate_roadmap_item()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_type roadmap_type;
BEGIN
    SELECT roadmap_type
    INTO parent_type
    FROM roadmaps
    WHERE roadmap_id = NEW.roadmap_id;

    IF parent_type IS NULL THEN
        RAISE EXCEPTION 'Parent roadmap does not exist';
    END IF;

    IF parent_type = 'now_next_later'
       AND NEW.horizon IS NULL THEN
        RAISE EXCEPTION
            'Now-Next-Later items require a horizon';
    END IF;

    IF parent_type <> 'now_next_later'
       AND NEW.horizon IS NOT NULL THEN
        RAISE EXCEPTION
            'Horizon is only valid for Now-Next-Later roadmaps';
    END IF;

    IF parent_type = 'outcome'
       AND NEW.status = 'completed'
       AND NOT EXISTS (
           SELECT 1
           FROM outcome_metrics m
           WHERE m.item_id = NEW.item_id
       ) THEN
        RAISE EXCEPTION
            'Outcome item requires a metric before completion';
    END IF;

    IF NEW.theme_id IS NOT NULL
       AND NOT EXISTS (
           SELECT 1
           FROM strategic_themes t
           WHERE t.theme_id = NEW.theme_id
             AND t.roadmap_id = NEW.roadmap_id
             AND t.state = 'active'
       ) THEN
        RAISE EXCEPTION
            'Theme must be active and belong to the same roadmap';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_roadmap_item
BEFORE INSERT OR UPDATE OF roadmap_id, theme_id, horizon, status
ON roadmap_items
FOR EACH ROW
EXECUTE FUNCTION validate_roadmap_item();

-- =========================================================
-- OUTCOME METRIC TYPE VALIDATION
-- =========================================================

CREATE OR REPLACE FUNCTION validate_outcome_metric()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_type roadmap_type;
BEGIN
    SELECT r.roadmap_type
    INTO parent_type
    FROM roadmap_items i
    JOIN roadmaps r
      ON r.roadmap_id = i.roadmap_id
    WHERE i.item_id = NEW.item_id;

    IF parent_type IS DISTINCT FROM 'outcome' THEN
        RAISE EXCEPTION
            'Metrics can only belong to outcome roadmap items';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_outcome_metric
BEFORE INSERT OR UPDATE
ON outcome_metrics
FOR EACH ROW
EXECUTE FUNCTION validate_outcome_metric();

-- =========================================================
-- DEPENDENCY CYCLE VALIDATION
-- =========================================================

CREATE OR REPLACE FUNCTION validate_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    creates_cycle BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM roadmap_items a
        JOIN roadmap_items b
          ON b.item_id = NEW.depends_on_item_id
        WHERE a.item_id = NEW.item_id
          AND a.roadmap_id = b.roadmap_id
    ) THEN
        RAISE EXCEPTION
            'Dependencies must belong to the same roadmap';
    END IF;

    WITH RECURSIVE dependency_path(node_id) AS (
        SELECT NEW.depends_on_item_id

        UNION

        SELECT d.depends_on_item_id
        FROM item_dependencies d
        JOIN dependency_path p
          ON d.item_id = p.node_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM dependency_path
        WHERE node_id = NEW.item_id
    )
    INTO creates_cycle;

    IF creates_cycle THEN
        RAISE EXCEPTION
            'Circular dependency is not allowed';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency_cycle
BEFORE INSERT OR UPDATE
ON item_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency_cycle();

-- =========================================================
-- STATUS TRANSITION VALIDATION
-- =========================================================

CREATE OR REPLACE FUNCTION validate_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    unfinished_count INTEGER;
BEGIN
    IF OLD.status IN ('completed', 'cancelled')
       AND NEW.status <> OLD.status THEN
        RAISE EXCEPTION
            'Terminal roadmap items cannot be reopened';
    END IF;

    IF NEW.status = 'in_progress'
       AND OLD.status <> 'in_progress' THEN

        SELECT COUNT(*)
        INTO unfinished_count
        FROM item_dependencies d
        JOIN roadmap_items dependency
          ON dependency.item_id = d.depends_on_item_id
        WHERE d.item_id = NEW.item_id
          AND dependency.status <> 'completed';

        IF unfinished_count > 0 THEN
            RAISE EXCEPTION
                'Uncompleted dependencies prevent execution';
        END IF;
    END IF;

    IF NEW.status = 'completed' THEN
        NEW.progress := 100;
    END IF;

    NEW.updated_at := NOW();
    NEW.version := OLD.version + 1;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_status_transition
BEFORE UPDATE OF status
ON roadmap_items
FOR EACH ROW
EXECUTE FUNCTION validate_status_transition();

-- =========================================================
-- AUDIT TRIGGER
-- =========================================================

CREATE OR REPLACE FUNCTION record_item_audit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status
       OR OLD.progress IS DISTINCT FROM NEW.progress THEN

        INSERT INTO roadmap_audit (
            item_id,
            previous_status,
            new_status,
            previous_progress,
            new_progress,
            reason
        )
        VALUES (
            NEW.item_id,
            OLD.status,
            NEW.status,
            OLD.progress,
            NEW.progress,
            'Automated roadmap lifecycle audit'
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_record_item_audit
AFTER UPDATE OF status, progress
ON roadmap_items
FOR EACH ROW
EXECUTE FUNCTION record_item_audit();

-- =========================================================
-- COMPLETION AND ELIGIBILITY FUNCTIONS
-- =========================================================

CREATE OR REPLACE FUNCTION item_is_eligible(
    requested_item_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM roadmap_items i
        WHERE i.item_id = requested_item_id
          AND i.status NOT IN ('completed', 'cancelled')
          AND NOT EXISTS (
              SELECT 1
              FROM item_dependencies d
              JOIN roadmap_items dependency
                ON dependency.item_id = d.depends_on_item_id
              WHERE d.item_id = i.item_id
                AND dependency.status <> 'completed'
          )
    );
$$;

CREATE OR REPLACE FUNCTION calculate_metric_progress(
    metric_id_input BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT CASE
        WHEN target = baseline THEN
            CASE
                WHEN current_value = target THEN 100
                ELSE 0
            END
        ELSE LEAST(
            100,
            GREATEST(
                0,
                ROUND(
                    (
                        (current_value - baseline)
                        / (target - baseline)
                    ) * 100,
                    2
                )
            )
        )
    END
    FROM outcome_metrics
    WHERE metric_id = metric_id_input;
$$;

-- =========================================================
-- VIEWS
-- =========================================================

CREATE OR REPLACE VIEW roadmap_item_details AS
SELECT
    r.roadmap_id,
    r.name AS roadmap_name,
    r.roadmap_type,
    i.item_id,
    i.title,
    i.description,
    i.priority,
    i.status,
    i.horizon,
    i.progress,
    i.confidence,
    u.full_name AS owner,
    t.name AS theme,
    i.target_date
FROM roadmaps r
JOIN roadmap_items i
  ON i.roadmap_id = r.roadmap_id
JOIN roadmap_users u
  ON u.user_id = i.owner_id
LEFT JOIN strategic_themes t
  ON t.theme_id = i.theme_id;

CREATE OR REPLACE VIEW outcome_progress_report AS
SELECT
    i.item_id,
    i.title,
    m.metric_name,
    m.baseline,
    m.target,
    m.current_value,
    m.unit,
    calculate_metric_progress(m.metric_id) AS metric_progress
FROM roadmap_items i
JOIN outcome_metrics m
  ON m.item_id = i.item_id;

CREATE OR REPLACE VIEW roadmap_completion_report AS
SELECT
    r.roadmap_id,
    r.name,
    r.roadmap_type,
    COUNT(i.item_id) AS total_items,
    COUNT(i.item_id) FILTER (
        WHERE i.status = 'completed'
    ) AS completed_items,
    ROUND(
        100.0 * COUNT(i.item_id) FILTER (
            WHERE i.status = 'completed'
        ) / NULLIF(COUNT(i.item_id), 0),
        2
    ) AS completion_percentage
FROM roadmaps r
LEFT JOIN roadmap_items i
  ON i.roadmap_id = r.roadmap_id
GROUP BY
    r.roadmap_id,
    r.name,
    r.roadmap_type;

-- =========================================================
-- WORKFLOW PROCEDURE
-- =========================================================

CREATE OR REPLACE PROCEDURE move_item_to_execution(
    requested_item_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE roadmap_items
    SET status = 'in_progress'
    WHERE item_id = requested_item_id
      AND status IN ('proposed', 'planned', 'blocked');

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Item cannot be moved to execution';
    END IF;
END;
$$;

-- =========================================================
-- SAMPLE USERS
-- =========================================================

INSERT INTO roadmap_users (
    full_name,
    email,
    department
)
VALUES
(
    'Aarav Sharma',
    'aarav@example.com',
    'Product Management'
),
(
    'Meera Singh',
    'meera@example.com',
    'Security Engineering'
),
(
    'Rohan Verma',
    'rohan@example.com',
    'Platform Engineering'
),
(
    'Ananya Rao',
    'ananya@example.com',
    'Business Operations'
);

-- =========================================================
-- SAMPLE ROADMAPS
-- =========================================================

INSERT INTO roadmaps (
    name,
    description,
    roadmap_type,
    owner_id
)
VALUES
(
    'Customer Platform Features',
    'Product capability delivery plan',
    'feature',
    1
),
(
    'Customer Experience Outcomes',
    'Measurable customer outcomes',
    'outcome',
    1
),
(
    'Annual Strategic Themes',
    'Strategic investment themes',
    'theme',
    3
),
(
    'Product Investment Horizons',
    'Near-term and future priorities',
    'now_next_later',
    1
);

-- =========================================================
-- SAMPLE THEMES
-- =========================================================

INSERT INTO strategic_themes (
    roadmap_id,
    name,
    objective,
    owner_id
)
VALUES
(
    3,
    'Trust and Security',
    'Improve platform security and governance',
    2
),
(
    3,
    'Operational Excellence',
    'Improve operational efficiency',
    3
);

-- =========================================================
-- SAMPLE FEATURE ITEMS
-- =========================================================

INSERT INTO roadmap_items (
    roadmap_id,
    title,
    description,
    owner_id,
    priority,
    status,
    progress,
    confidence
)
VALUES
(
    1,
    'Multi-factor authentication',
    'Introduce second-factor authentication',
    2,
    'critical',
    'planned',
    0,
    0.95
),
(
    1,
    'Customer analytics dashboard',
    'Provide customer usage analytics',
    1,
    'high',
    'proposed',
    0,
    0.85
),
(
    1,
    'Notification preferences',
    'Allow configurable notifications',
    1,
    'medium',
    'proposed',
    0,
    0.80
);

-- Analytics depends on authentication.
INSERT INTO item_dependencies (
    item_id,
    depends_on_item_id
)
SELECT
    analytics.item_id,
    authentication.item_id
FROM roadmap_items analytics
JOIN roadmap_items authentication
  ON authentication.roadmap_id = analytics.roadmap_id
WHERE analytics.title = 'Customer analytics dashboard'
  AND authentication.title = 'Multi-factor authentication';

-- =========================================================
-- SAMPLE OUTCOME ITEMS
-- =========================================================

INSERT INTO roadmap_items (
    roadmap_id,
    title,
    description,
    owner_id,
    priority,
    status
)
VALUES
(
    2,
    'Reduce onboarding time',
    'Improve customer onboarding efficiency',
    4,
    'high',
    'planned'
),
(
    2,
    'Improve customer retention',
    'Increase customer retention rate',
    1,
    'critical',
    'planned'
);

INSERT INTO outcome_metrics (
    item_id,
    metric_name,
    baseline,
    target,
    current_value,
    unit
)
SELECT
    item_id,
    'Average onboarding duration',
    10,
    4,
    6,
    'days'
FROM roadmap_items
WHERE title = 'Reduce onboarding time';

INSERT INTO outcome_metrics (
    item_id,
    metric_name,
    baseline,
    target,
    current_value,
    unit
)
SELECT
    item_id,
    'Customer retention',
    70,
    90,
    78,
    'percentage'
FROM roadmap_items
WHERE title = 'Improve customer retention';

-- =========================================================
-- SAMPLE THEME ITEMS
-- =========================================================

INSERT INTO roadmap_items (
    roadmap_id,
    theme_id,
    title,
    description,
    owner_id,
    priority,
    status
)
SELECT
    3,
    theme_id,
    'Centralized audit logging',
    'Unify platform audit records',
    3,
    'high',
    'planned'
FROM strategic_themes
WHERE name = 'Trust and Security';

INSERT INTO roadmap_items (
    roadmap_id,
    theme_id,
    title,
    description,
    owner_id,
    priority,
    status
)
SELECT
    3,
    theme_id,
    'Operational process automation',
    'Reduce repetitive operational work',
    3,
    'medium',
    'proposed'
FROM strategic_themes
WHERE name = 'Operational Excellence';

-- =========================================================
-- SAMPLE NOW-NEXT-LATER ITEMS
-- =========================================================

INSERT INTO roadmap_items (
    roadmap_id,
    title,
    description,
    owner_id,
    priority,
    status,
    horizon
)
VALUES
(
    4,
    'Resolve payment failures',
    'Improve payment transaction reliability',
    3,
    'critical',
    'in_progress',
    'now'
),
(
    4,
    'Improve business reporting',
    'Enhance reporting capabilities',
    1,
    'high',
    'planned',
    'next'
),
(
    4,
    'Predictive capacity planning',
    'Introduce forward-looking capacity planning',
    3,
    'medium',
    'proposed',
    'later'
);

-- =========================================================
-- SAMPLE TAGS
-- =========================================================

INSERT INTO roadmap_tags (roadmap_id, tag_name)
VALUES
(1, 'security'),
(1, 'analytics'),
(4, 'operational-priority');

INSERT INTO item_tags (item_id, tag_id)
SELECT i.item_id, t.tag_id
FROM roadmap_items i
JOIN roadmap_tags t
  ON t.roadmap_id = i.roadmap_id
WHERE i.title = 'Multi-factor authentication'
  AND t.tag_name = 'security';

-- =========================================================
-- RETRIEVAL QUERY
-- =========================================================

SELECT *
FROM roadmap_item_details
ORDER BY roadmap_id, priority, title;

-- =========================================================
-- OUTCOME EVALUATION
-- =========================================================

SELECT *
FROM outcome_progress_report
ORDER BY metric_progress DESC;

-- =========================================================
-- ROADMAP AGGREGATION
-- =========================================================

SELECT *
FROM roadmap_completion_report
ORDER BY roadmap_id;

-- =========================================================
-- HORIZON DISTRIBUTION
-- =========================================================

SELECT
    r.name AS roadmap,
    i.horizon,
    COUNT(*) AS item_count
FROM roadmap_items i
JOIN roadmaps r
  ON r.roadmap_id = i.roadmap_id
WHERE r.roadmap_type = 'now_next_later'
GROUP BY r.name, i.horizon
ORDER BY
    CASE i.horizon
        WHEN 'now' THEN 1
        WHEN 'next' THEN 2
        WHEN 'later' THEN 3
    END;

-- =========================================================
-- PRIORITIZATION QUERY
-- =========================================================

SELECT
    i.item_id,
    i.title,
    i.priority,
    i.confidence,
    (
        CASE i.priority
            WHEN 'critical' THEN 4
            WHEN 'high' THEN 3
            WHEN 'medium' THEN 2
            WHEN 'low' THEN 1
        END
    ) * i.confidence AS priority_score
FROM roadmap_items i
ORDER BY priority_score DESC;

-- =========================================================
-- DEPENDENCY ELIGIBILITY
-- =========================================================

SELECT
    item_id,
    title,
    item_is_eligible(item_id) AS eligible_for_execution
FROM roadmap_items
ORDER BY item_id;

-- =========================================================
-- THEME ALIGNMENT REPORT
-- =========================================================

SELECT
    t.name AS theme,
    t.objective,
    COUNT(i.item_id) AS aligned_items,
    COUNT(i.item_id) FILTER (
        WHERE i.status = 'completed'
    ) AS completed_items
FROM strategic_themes t
LEFT JOIN roadmap_items i
  ON i.theme_id = t.theme_id
GROUP BY t.theme_id, t.name, t.objective
ORDER BY t.name;

-- =========================================================
-- WORKFLOW PROCESSING
-- =========================================================

-- The authentication item has no dependencies.
-- It can safely transition to execution.
DO $$
DECLARE
    authentication_id BIGINT;
BEGIN
    SELECT item_id
    INTO authentication_id
    FROM roadmap_items
    WHERE title = 'Multi-factor authentication';

    IF item_is_eligible(authentication_id) THEN
        CALL move_item_to_execution(authentication_id);
    END IF;
END;
$$;

-- =========================================================
-- TRANSACTIONAL PROGRESS UPDATE
-- =========================================================

DO $$
DECLARE
    target_item BIGINT;
BEGIN
    SELECT item_id
    INTO target_item
    FROM roadmap_items
    WHERE title = 'Multi-factor authentication';

    UPDATE roadmap_items
    SET progress = 65
    WHERE item_id = target_item
      AND status = 'in_progress';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Progress update rejected because item is not active';
    END IF;
END;
$$;

-- =========================================================
-- AUDIT REPORT
-- =========================================================

SELECT
    a.audit_id,
    i.title,
    a.previous_status,
    a.new_status,
    a.previous_progress,
    a.new_progress,
    a.changed_at
FROM roadmap_audit a
JOIN roadmap_items i
  ON i.item_id = a.item_id
ORDER BY a.changed_at DESC;

-- =========================================================
-- VALIDATION: INVALID DEPENDENCY
-- =========================================================

-- This transaction deliberately attempts to introduce
-- a nonexistent dependency and rolls back its expected failure.

DO $$
DECLARE
    first_item BIGINT;
    nonexistent_item BIGINT := -999;
BEGIN
    SELECT item_id
    INTO first_item
    FROM roadmap_items
    WHERE title = 'Notification preferences';

    BEGIN
        INSERT INTO item_dependencies (
            item_id,
            depends_on_item_id
        )
        VALUES (
            first_item,
            nonexistent_item
        );
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE
                'Expected failure: nonexistent dependency rejected';
    END;
END;
$$;

-- =========================================================
-- FINAL REPORTING
-- =========================================================

SELECT
    r.name,
    r.roadmap_type,
    COUNT(i.item_id) AS total_items,
    COUNT(i.item_id) FILTER (
        WHERE i.status = 'completed'
    ) AS completed,
    COUNT(i.item_id) FILTER (
        WHERE i.status = 'blocked'
    ) AS blocked,
    COUNT(i.item_id) FILTER (
        WHERE i.status = 'in_progress'
    ) AS in_progress
FROM roadmaps r
LEFT JOIN roadmap_items i
  ON i.roadmap_id = r.roadmap_id
GROUP BY r.roadmap_id, r.name, r.roadmap_type
ORDER BY r.roadmap_id;

COMMIT;
