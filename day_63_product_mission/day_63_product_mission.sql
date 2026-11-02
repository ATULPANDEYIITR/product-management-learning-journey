DROP SCHEMA IF EXISTS product_strategy CASCADE;

CREATE SCHEMA product_strategy;

SET search_path TO product_strategy, public;

CREATE TYPE mission_type AS ENUM (
    'organizational',
    'product'
);

CREATE TYPE mission_status AS ENUM (
    'draft',
    'active',
    'retired'
);

CREATE TYPE metric_status AS ENUM (
    'healthy',
    'warning',
    'critical'
);

CREATE TABLE organizations (
    organization_id BIGSERIAL PRIMARY KEY,
    organization_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(organization_name) <> '')
);

CREATE TABLE missions (
    mission_id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,
    mission_type mission_type NOT NULL,
    mission_name TEXT NOT NULL,
    mission_statement TEXT NOT NULL,
    organizational_purpose TEXT NOT NULL,
    status mission_status NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(mission_name) <> ''),
    CHECK (btrim(mission_statement) <> ''),
    CHECK (btrim(organizational_purpose) <> ''),
    CHECK (char_length(mission_statement) <= 300),
    CHECK (version > 0),
    UNIQUE (
        organization_id,
        mission_type,
        mission_name,
        version
    )
);

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    product_purpose TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(product_name) <> ''),
    CHECK (btrim(product_purpose) <> ''),
    CHECK (
        lifecycle_status IN ('planned', 'active', 'retired')
    ),
    UNIQUE (organization_id, product_name)
);

CREATE TABLE product_missions (
    product_id BIGINT PRIMARY KEY
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    mission_id BIGINT NOT NULL
        REFERENCES missions(mission_id)
        ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, mission_id)
);

CREATE TABLE strategic_themes (
    theme_id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,
    theme_name TEXT NOT NULL,
    UNIQUE (organization_id, theme_name),
    CHECK (btrim(theme_name) <> '')
);

CREATE TABLE mission_themes (
    mission_id BIGINT NOT NULL
        REFERENCES missions(mission_id)
        ON DELETE CASCADE,
    theme_id BIGINT NOT NULL
        REFERENCES strategic_themes(theme_id)
        ON DELETE CASCADE,
    PRIMARY KEY (mission_id, theme_id)
);

CREATE TABLE product_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(14,4) NOT NULL,
    target_value NUMERIC(14,4),
    status metric_status NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(metric_name) <> ''),
    CHECK (metric_value >= 0),
    CHECK (target_value IS NULL OR target_value >= 0),
    UNIQUE (product_id, metric_name, measured_at)
);

CREATE TABLE mission_evaluations (
    evaluation_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    organizational_mission_id BIGINT NOT NULL
        REFERENCES missions(mission_id)
        ON DELETE RESTRICT,
    product_mission_id BIGINT NOT NULL
        REFERENCES missions(mission_id)
        ON DELETE RESTRICT,
    decision TEXT NOT NULL,
    shared_theme_count INTEGER NOT NULL DEFAULT 0,
    purpose_clarity_score NUMERIC(6,2) NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        decision IN ('aligned', 'misaligned', 'invalid')
    ),
    CHECK (shared_theme_count >= 0),
    CHECK (
        purpose_clarity_score BETWEEN 0 AND 100
    )
);

CREATE INDEX idx_missions_org_status
    ON missions (organization_id, status);

CREATE INDEX idx_product_metrics_product_time
    ON product_metrics (product_id, measured_at DESC);

CREATE INDEX idx_mission_themes_theme
    ON mission_themes (theme_id, mission_id);

CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER missions_touch_updated_at
BEFORE UPDATE ON missions
FOR EACH ROW
EXECUTE FUNCTION touch_updated_at();

CREATE OR REPLACE FUNCTION validate_product_mission()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    product_org BIGINT;
    mission_org BIGINT;
    mission_kind mission_type;
BEGIN
    SELECT organization_id
    INTO product_org
    FROM products
    WHERE product_id = NEW.product_id;

    SELECT organization_id, mission_type
    INTO mission_org, mission_kind
    FROM missions
    WHERE mission_id = NEW.mission_id;

    IF product_org IS NULL OR mission_org IS NULL THEN
        RAISE EXCEPTION
            'Product or mission does not exist';
    END IF;

    IF product_org <> mission_org THEN
        RAISE EXCEPTION
            'Product mission must belong to the same organization';
    END IF;

    IF mission_kind <> 'product' THEN
        RAISE EXCEPTION
            'Linked mission must be a product mission';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER product_mission_validation
BEFORE INSERT OR UPDATE ON product_missions
FOR EACH ROW
EXECUTE FUNCTION validate_product_mission();

CREATE OR REPLACE FUNCTION calculate_purpose_clarity(
    p_product_id BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
AS $$
    WITH product_mission_text AS (
        SELECT
            lower(m.mission_statement) AS statement_text,
            lower(m.organizational_purpose) AS purpose_text
        FROM product_missions pm
        JOIN missions m
          ON m.mission_id = pm.mission_id
        WHERE pm.product_id = p_product_id
    ),
    statement_words AS (
        SELECT DISTINCT regexp_replace(word, '[^a-z0-9]', '', 'g') AS word
        FROM product_mission_text,
             regexp_split_to_table(statement_text, '\s+') AS word
        WHERE length(word) > 3
    ),
    purpose_words AS (
        SELECT DISTINCT regexp_replace(word, '[^a-z0-9]', '', 'g') AS word
        FROM product_mission_text,
             regexp_split_to_table(purpose_text, '\s+') AS word
        WHERE length(word) > 3
    ),
    counts AS (
        SELECT
            (SELECT count(*) FROM statement_words) AS statement_count,
            (SELECT count(*) FROM purpose_words) AS purpose_count,
            (
                SELECT count(*)
                FROM statement_words s
                JOIN purpose_words p USING (word)
            ) AS shared_count
    )
    SELECT CASE
        WHEN GREATEST(statement_count, purpose_count) = 0
            THEN 0::NUMERIC
        ELSE ROUND(
            shared_count * 100.0
            / GREATEST(statement_count, purpose_count),
            2
        )
    END
    FROM counts;
$$;

CREATE OR REPLACE FUNCTION evaluate_product_mission(
    p_product_id BIGINT
)
RETURNS TABLE (
    product_name TEXT,
    decision TEXT,
    shared_theme_count BIGINT,
    purpose_clarity_score NUMERIC
)
LANGUAGE sql
AS $$
    WITH product_context AS (
        SELECT
            p.product_id,
            p.product_name,
            om.mission_id AS organizational_mission_id,
            pm.mission_id AS product_mission_id
        FROM products p
        JOIN product_missions pm
          ON pm.product_id = p.product_id
        JOIN missions product_mission
          ON product_mission.mission_id = pm.mission_id
         AND product_mission.mission_type = 'product'
        JOIN missions om
          ON om.organization_id = p.organization_id
         AND om.mission_type = 'organizational'
         AND om.status = 'active'
    ),
    shared_themes AS (
        SELECT DISTINCT
            pc.product_id,
            st.theme_id
        FROM product_context pc
        JOIN mission_themes mt_product
          ON mt_product.mission_id = pc.product_mission_id
        JOIN mission_themes mt_org
          ON mt_org.theme_id = mt_product.theme_id
         AND mt_org.mission_id = pc.organizational_mission_id
        JOIN strategic_themes st
          ON st.theme_id = mt_product.theme_id
    )
    SELECT
        pc.product_name,
        CASE
            WHEN count(st.theme_id) > 0
                THEN 'aligned'
            ELSE 'misaligned'
        END AS decision,
        count(st.theme_id) AS shared_theme_count,
        calculate_purpose_clarity(pc.product_id)
    FROM product_context pc
    LEFT JOIN shared_themes st
      ON st.product_id = pc.product_id
    GROUP BY
        pc.product_id,
        pc.product_name;
$$;

INSERT INTO organizations (organization_name)
VALUES ('Acme Digital Services');

INSERT INTO missions (
    organization_id,
    mission_type,
    mission_name,
    mission_statement,
    organizational_purpose,
    status
)
SELECT
    organization_id,
    'organizational',
    'Acme Organizational Mission',
    'Improve access to trustworthy digital services by making essential customer interactions simpler and more reliable.',
    'Deliver dependable services that solve important customer problems.',
    'active'
FROM organizations
WHERE organization_name = 'Acme Digital Services';

INSERT INTO products (
    organization_id,
    product_name,
    product_purpose
)
SELECT
    organization_id,
    'Acme Pay',
    'Reduce friction in everyday digital payments while preserving customer trust.'
FROM organizations
WHERE organization_name = 'Acme Digital Services';

INSERT INTO strategic_themes (
    organization_id,
    theme_name
)
SELECT
    organization_id,
    theme_name
FROM organizations
CROSS JOIN (
    VALUES
        ('customer trust'),
        ('simplicity'),
        ('reliability'),
        ('cost efficiency'),
        ('operational resilience')
) AS themes(theme_name)
WHERE organization_name = 'Acme Digital Services';

INSERT INTO missions (
    organization_id,
    mission_type,
    mission_name,
    mission_statement,
    organizational_purpose,
    status
)
SELECT
    organization_id,
    'product',
    'Payments Product Mission',
    'Enable customers to complete everyday payments quickly, clearly, and reliably.',
    'Reduce friction in everyday transactions while preserving customer trust and reliability.',
    'active'
FROM organizations
WHERE organization_name = 'Acme Digital Services';

INSERT INTO product_missions (
    product_id,
    mission_id
)
SELECT
    p.product_id,
    m.mission_id
FROM products p
JOIN missions m
  ON m.organization_id = p.organization_id
 AND m.mission_type = 'product'
 AND m.mission_name = 'Payments Product Mission'
WHERE p.product_name = 'Acme Pay';

INSERT INTO mission_themes (mission_id, theme_id)
SELECT
    m.mission_id,
    t.theme_id
FROM missions m
JOIN strategic_themes t
  ON t.organization_id = m.organization_id
 AND t.theme_name IN (
     'customer trust',
     'simplicity',
     'reliability'
 )
WHERE m.mission_name IN (
    'Acme Organizational Mission',
    'Payments Product Mission'
);

INSERT INTO product_metrics (
    product_id,
    metric_name,
    metric_value,
    target_value,
    status
)
SELECT
    product_id,
    metric_name,
    metric_value,
    target_value,
    status::metric_status
FROM products
CROSS JOIN (
    VALUES
        (
            'successful_transaction_rate',
            99.2::NUMERIC,
            98.0::NUMERIC,
            'healthy'
        ),
        (
            'payment_completion_time_seconds',
            18.5::NUMERIC,
            25.0::NUMERIC,
            'healthy'
        ),
        (
            'customer_satisfaction',
            91.4::NUMERIC,
            80.0::NUMERIC,
            'healthy'
        )
) AS metrics(
    metric_name,
    metric_value,
    target_value,
    status
)
WHERE product_name = 'Acme Pay';

INSERT INTO mission_evaluations (
    product_id,
    organizational_mission_id,
    product_mission_id,
    decision,
    shared_theme_count,
    purpose_clarity_score
)
SELECT
    p.product_id,
    om.mission_id,
    pm.mission_id,
    e.decision,
    e.shared_theme_count,
    e.purpose_clarity_score
FROM products p
JOIN missions om
  ON om.organization_id = p.organization_id
 AND om.mission_type = 'organizational'
 AND om.status = 'active'
JOIN product_missions pm
  ON pm.product_id = p.product_id
JOIN LATERAL evaluate_product_mission(p.product_id) e
  ON TRUE
WHERE p.product_name = 'Acme Pay';

-- Retrieval: product mission and its organizational parent.
SELECT
    p.product_name,
    om.mission_statement AS organizational_mission,
    pmn.mission_statement AS product_mission,
    p.product_purpose
FROM products p
JOIN product_missions pml
  ON pml.product_id = p.product_id
JOIN missions pmn
  ON pmn.mission_id = pml.mission_id
JOIN missions om
  ON om.organization_id = p.organization_id
 AND om.mission_type = 'organizational'
 AND om.status = 'active';

-- Validation: identify themes shared by organizational and product missions.
WITH active_missions AS (
    SELECT
        p.product_id,
        om.mission_id AS organizational_mission_id,
        pm.mission_id AS product_mission_id
    FROM products p
    JOIN product_missions pml
      ON pml.product_id = p.product_id
    JOIN missions pm
      ON pm.mission_id = pml.mission_id
     AND pm.mission_type = 'product'
    JOIN missions om
      ON om.organization_id = p.organization_id
     AND om.mission_type = 'organizational'
     AND om.status = 'active'
)
SELECT
    p.product_name,
    t.theme_name
FROM active_missions am
JOIN products p
  ON p.product_id = am.product_id
JOIN mission_themes product_theme
  ON product_theme.mission_id = am.product_mission_id
JOIN mission_themes organization_theme
  ON organization_theme.mission_id = am.organizational_mission_id
 AND organization_theme.theme_id = product_theme.theme_id
JOIN strategic_themes t
  ON t.theme_id = product_theme.theme_id
ORDER BY p.product_name, t.theme_name;

-- Aggregation: latest metric state by product.
WITH ranked_metrics AS (
    SELECT
        p.product_name,
        pm.metric_name,
        pm.metric_value,
        pm.target_value,
        pm.status,
        row_number() OVER (
            PARTITION BY pm.product_id, pm.metric_name
            ORDER BY pm.measured_at DESC
        ) AS rn
    FROM product_metrics pm
    JOIN products p
      ON p.product_id = pm.product_id
)
SELECT
    product_name,
    metric_name,
    metric_value,
    target_value,
    status
FROM ranked_metrics
WHERE rn = 1
ORDER BY product_name, metric_name;

-- Evaluation: determine mission alignment and purpose clarity.
SELECT *
FROM evaluate_product_mission(
    (
        SELECT product_id
        FROM products
        WHERE product_name = 'Acme Pay'
    )
);

-- Reporting: mission evaluations with current operational metrics.
SELECT
    p.product_name,
    me.decision,
    me.shared_theme_count,
    me.purpose_clarity_score,
    count(pm.metric_id) AS metric_records,
    count(*) FILTER (
        WHERE pm.status = 'healthy'
    ) AS healthy_metric_records
FROM mission_evaluations me
JOIN products p
  ON p.product_id = me.product_id
LEFT JOIN product_metrics pm
  ON pm.product_id = p.product_id
GROUP BY
    p.product_name,
    me.decision,
    me.shared_theme_count,
    me.purpose_clarity_score;

-- Workflow-state query: active organizational and product missions.
SELECT
    o.organization_name,
    m.mission_type,
    m.mission_name,
    m.status,
    m.version,
    m.updated_at
FROM organizations o
JOIN missions m
  ON m.organization_id = o.organization_id
WHERE m.status = 'active'
ORDER BY
    o.organization_name,
    m.mission_type,
    m.mission_name;

-- Eligibility decision:
-- a product is strategically eligible when it has an active product
-- mission, an active organizational mission, at least one shared theme,
-- and a purpose clarity score of at least 20%.
WITH evaluations AS (
    SELECT *
    FROM mission_evaluations
)
SELECT
    p.product_name,
    CASE
        WHEN e.decision = 'aligned'
         AND e.shared_theme_count >= 1
         AND e.purpose_clarity_score >= 20
            THEN 'eligible'
        ELSE 'not_eligible'
    END AS mission_eligibility,
    e.decision,
    e.shared_theme_count,
    e.purpose_clarity_score
FROM products p
JOIN evaluations e
  ON e.product_id = p.product_id;
