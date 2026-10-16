-- PostgreSQL 15+
-- Product backlog management with refinement, prioritization,
-- dependencies, technical-debt forecasting, and sprint selection.

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_delivery;
SET search_path TO product_delivery, public;

CREATE TYPE work_item_type AS ENUM (
    'feature', 'bug', 'security', 'technical_debt', 'spike'
);

CREATE TYPE backlog_status AS ENUM (
    'proposed', 'refining', 'ready', 'in_progress',
    'blocked', 'done', 'rejected'
);

CREATE TYPE priority_band AS ENUM ('critical', 'high', 'medium', 'low');

CREATE TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    sprint_capacity INTEGER NOT NULL CHECK (sprint_capacity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (btrim(product_key) <> ''),
    CHECK (btrim(name) <> '')
);

CREATE TABLE backlog_items (
    item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    item_key TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    item_type work_item_type NOT NULL,
    status backlog_status NOT NULL DEFAULT 'proposed',
    business_value SMALLINT NOT NULL CHECK (business_value BETWEEN 1 AND 10),
    urgency SMALLINT NOT NULL CHECK (urgency BETWEEN 1 AND 10),
    risk_reduction SMALLINT NOT NULL CHECK (risk_reduction BETWEEN 1 AND 10),
    effort INTEGER NOT NULL CHECK (effort BETWEEN 1 AND 100),
    debt_principal NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (debt_principal >= 0),
    debt_interest_per_sprint NUMERIC(14,2) NOT NULL DEFAULT 0
        CHECK (debt_interest_per_sprint >= 0),
    owner TEXT,
    target_release TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (product_id, item_key),
    CHECK (btrim(item_key) <> ''),
    CHECK (btrim(title) <> ''),
    CHECK (btrim(description) <> ''),
    CHECK (
        item_type = 'technical_debt'
        OR (debt_principal = 0 AND debt_interest_per_sprint = 0)
    )
);

CREATE TABLE acceptance_criteria (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id) ON DELETE CASCADE,
    criterion_text TEXT NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    UNIQUE (item_id, criterion_text),
    CHECK (btrim(criterion_text) <> ''),
    CHECK (
        (is_verified AND verified_at IS NOT NULL)
        OR (NOT is_verified AND verified_at IS NULL)
    )
);

CREATE TABLE item_dependencies (
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id) ON DELETE CASCADE,
    depends_on_item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (item_id, depends_on_item_id),
    CHECK (item_id <> depends_on_item_id)
);

CREATE TABLE refinement_sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    facilitator TEXT NOT NULL,
    session_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    outcome TEXT NOT NULL CHECK (
        outcome IN ('clarified', 'reestimated', 'split', 'deferred', 'rejected')
    ),
    notes TEXT NOT NULL,
    previous_effort INTEGER CHECK (previous_effort BETWEEN 1 AND 100),
    revised_effort INTEGER CHECK (revised_effort BETWEEN 1 AND 100),
    CHECK (btrim(facilitator) <> ''),
    CHECK (btrim(notes) <> '')
);

CREATE TABLE sprint_plans (
    sprint_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    sprint_name TEXT NOT NULL,
    starts_on DATE NOT NULL,
    ends_on DATE NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    UNIQUE (product_id, sprint_name),
    CHECK (ends_on >= starts_on)
);

CREATE TABLE sprint_items (
    sprint_id BIGINT NOT NULL REFERENCES sprint_plans(sprint_id) ON DELETE CASCADE,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    planned_effort INTEGER NOT NULL CHECK (planned_effort BETWEEN 1 AND 100),
    selection_reason TEXT NOT NULL,
    PRIMARY KEY (sprint_id, item_id),
    CHECK (btrim(selection_reason) <> '')
);

CREATE TABLE backlog_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES backlog_items(item_id),
    changed_by TEXT NOT NULL,
    event_type TEXT NOT NULL,
    old_status backlog_status,
    new_status backlog_status,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_backlog_status_priority
    ON backlog_items (product_id, status, urgency DESC, business_value DESC);

CREATE INDEX idx_backlog_item_type
    ON backlog_items (product_id, item_type);

CREATE INDEX idx_dependencies_prerequisite
    ON item_dependencies (depends_on_item_id, item_id);

CREATE INDEX idx_unverified_criteria
    ON acceptance_criteria (item_id)
    WHERE is_verified = FALSE;

CREATE INDEX idx_audit_item_time
    ON backlog_audit (item_id, occurred_at DESC);

-- A recursive trigger rejects dependency cycles and dependencies on completed
-- or rejected items are evaluated separately by workflow services.
CREATE FUNCTION reject_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_found BOOLEAN;
BEGIN
    IF NEW.item_id = NEW.depends_on_item_id THEN
        RAISE EXCEPTION 'An item cannot depend on itself';
    END IF;

    WITH RECURSIVE reachable(item_id) AS (
        SELECT NEW.depends_on_item_id
        UNION
        SELECT dependency.depends_on_item_id
        FROM item_dependencies AS dependency
        JOIN reachable AS prior
          ON dependency.item_id = prior.item_id
    )
    SELECT EXISTS (
        SELECT 1 FROM reachable WHERE item_id = NEW.item_id
    ) INTO cycle_found;

    IF cycle_found THEN
        RAISE EXCEPTION 'Dependency cycle detected for item %', NEW.item_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_reject_dependency_cycle
BEFORE INSERT OR UPDATE ON item_dependencies
FOR EACH ROW EXECUTE FUNCTION reject_dependency_cycle();

-- PostgreSQL constraints enforce row-level integrity. Cross-row workflow
-- requirements are enforced by this transition function and transactional
-- application workflows rather than by a misleading CHECK constraint.
CREATE FUNCTION transition_backlog_item(
    p_item_id BIGINT,
    p_next_status backlog_status,
    p_actor TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    current_status backlog_status;
    criteria_count BIGINT;
    blocker_count BIGINT;
    transition_allowed BOOLEAN := FALSE;
BEGIN
    SELECT status INTO current_status
    FROM backlog_items
    WHERE item_id = p_item_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown backlog item %', p_item_id;
    END IF;

    transition_allowed := CASE current_status
        WHEN 'proposed' THEN p_next_status IN ('refining', 'rejected')
        WHEN 'refining' THEN p_next_status IN ('proposed', 'ready', 'rejected')
        WHEN 'ready' THEN p_next_status IN ('refining', 'in_progress', 'rejected')
        WHEN 'in_progress' THEN p_next_status IN ('blocked', 'done', 'ready')
        WHEN 'blocked' THEN p_next_status IN ('in_progress', 'ready')
        WHEN 'done' THEN FALSE
        WHEN 'rejected' THEN p_next_status = 'refining'
        ELSE FALSE
    END;

    IF NOT transition_allowed THEN
        RAISE EXCEPTION 'Invalid status transition: % -> %',
            current_status, p_next_status;
    END IF;

    IF p_next_status = 'ready' THEN
        SELECT count(*) INTO criteria_count
        FROM acceptance_criteria
        WHERE item_id = p_item_id;

        IF criteria_count = 0 THEN
            RAISE EXCEPTION 'Ready item % requires acceptance criteria', p_item_id;
        END IF;
    END IF;

    IF p_next_status IN ('ready', 'in_progress') THEN
        SELECT count(*) INTO blocker_count
        FROM item_dependencies AS dependency
        JOIN backlog_items AS prerequisite
          ON prerequisite.item_id = dependency.depends_on_item_id
        WHERE dependency.item_id = p_item_id
          AND prerequisite.status <> 'done';

        IF blocker_count > 0 THEN
            RAISE EXCEPTION 'Item % has % unfinished prerequisites',
                p_item_id, blocker_count;
        END IF;
    END IF;

    UPDATE backlog_items
    SET status = p_next_status,
        version = version + 1,
        updated_at = now()
    WHERE item_id = p_item_id;

    INSERT INTO backlog_audit (
        item_id, changed_by, event_type, old_status, new_status
    )
    VALUES (
        p_item_id, p_actor, 'status_transition',
        current_status, p_next_status
    );
END;
$$;

CREATE VIEW prioritized_backlog AS
WITH scored AS (
    SELECT
        item.*,
        (
            item.business_value * 0.5
            + item.urgency * 0.3
            + item.risk_reduction * 0.2
        )::NUMERIC / item.effort AS priority_score,
        CASE
            WHEN item.item_type IN ('security', 'bug')
                 AND (item.urgency >= 9 OR item.risk_reduction >= 9)
                THEN 'critical'::priority_band
            WHEN (
                item.business_value * 0.5
                + item.urgency * 0.3
                + item.risk_reduction * 0.2
            ) / item.effort >= 3.5 THEN 'high'::priority_band
            WHEN (
                item.business_value * 0.5
                + item.urgency * 0.3
                + item.risk_reduction * 0.2
            ) / item.effort >= 1.8 THEN 'medium'::priority_band
            ELSE 'low'::priority_band
        END AS priority
    FROM backlog_items AS item
    WHERE item.status NOT IN ('done', 'rejected')
)
SELECT * FROM scored;

CREATE VIEW dependency_readiness AS
SELECT
    item.item_id,
    item.item_key,
    item.status,
    count(dependency.depends_on_item_id) FILTER (
        WHERE prerequisite.status <> 'done'
    ) AS unfinished_dependencies,
    count(criterion.criterion_id) AS acceptance_criteria_count,
    count(criterion.criterion_id) FILTER (
        WHERE criterion.is_verified
    ) AS verified_criteria_count
FROM backlog_items AS item
LEFT JOIN item_dependencies AS dependency
    ON dependency.item_id = item.item_id
LEFT JOIN backlog_items AS prerequisite
    ON prerequisite.item_id = dependency.depends_on_item_id
LEFT JOIN acceptance_criteria AS criterion
    ON criterion.item_id = item.item_id
GROUP BY item.item_id, item.item_key, item.status;

CREATE VIEW technical_debt_forecast AS
SELECT
    item.item_id,
    item.item_key,
    item.title,
    item.debt_principal,
    item.debt_interest_per_sprint,
    item.debt_principal + item.debt_interest_per_sprint * 4
        AS projected_cost_four_sprints
FROM backlog_items AS item
WHERE item.item_type = 'technical_debt';

INSERT INTO products (product_key, name, sprint_capacity)
VALUES ('PAYMENTS', 'Payments Reliability Platform', 12);

INSERT INTO backlog_items (
    product_id, item_key, title, description, item_type,
    business_value, urgency, risk_reduction, effort,
    debt_principal, debt_interest_per_sprint
)
SELECT product_id, item_key, title, description, item_type,
       business_value, urgency, risk_reduction, effort,
       debt_principal, debt_interest_per_sprint
FROM products
CROSS JOIN (
    VALUES
    (
        'PAY-501', 'Introduce idempotent payment requests',
        'Prevent duplicate payment execution after network retries.',
        'feature'::work_item_type, 10, 9, 10, 4, 0::NUMERIC, 0::NUMERIC
    ),
    (
        'PAY-502', 'Emit settlement audit events',
        'Record settlement outcomes without exposing payment secrets.',
        'feature'::work_item_type, 8, 7, 9, 4, 0::NUMERIC, 0::NUMERIC
    ),
    (
        'PAY-503', 'Replace inefficient reconciliation queries',
        'Batch reconciliation reads to reduce database contention.',
        'technical_debt'::work_item_type, 7, 6, 8, 3, 15000::NUMERIC, 1800::NUMERIC
    ),
    (
        'PAY-504', 'Fix cross-account authorization defect',
        'Prevent users from reading payments belonging to other accounts.',
        'security'::work_item_type, 10, 10, 10, 2, 0::NUMERIC, 0::NUMERIC
    ),
    (
        'PAY-505', 'Add settlement latency metrics',
        'Measure settlement duration by outcome and region.',
        'feature'::work_item_type, 7, 6, 6, 4, 0::NUMERIC, 0::NUMERIC
    )
) AS sample(
    item_key, title, description, item_type,
    business_value, urgency, risk_reduction, effort,
    debt_principal, debt_interest_per_sprint
)
WHERE products.product_key = 'PAYMENTS';

INSERT INTO acceptance_criteria (item_id, criterion_text)
SELECT item.item_id, criterion.criterion_text
FROM backlog_items AS item
JOIN (
    VALUES
    ('PAY-501', 'Repeated idempotency keys cannot execute a payment twice.'),
    ('PAY-501', 'Key retention behavior is covered by integration tests.'),
    ('PAY-502', 'Every successful settlement creates one audit event.'),
    ('PAY-502', 'Sensitive credentials are excluded from audit payloads.'),
    ('PAY-503', 'Query count stays bounded as reconciliation volume grows.'),
    ('PAY-503', 'Reconciliation output matches the previous implementation.'),
    ('PAY-504', 'Cross-account reads are denied and audited.'),
    ('PAY-504', 'Authorization regression tests cover account boundaries.'),
    ('PAY-505', 'Metrics distinguish settlement outcomes and regions.'),
    ('PAY-505', 'Customer identifiers are not used as metric labels.')
) AS criterion(item_key, criterion_text)
    ON criterion.item_key = item.item_key;

INSERT INTO item_dependencies (item_id, depends_on_item_id)
SELECT dependent.item_id, prerequisite.item_id
FROM backlog_items AS dependent
JOIN backlog_items AS prerequisite
  ON prerequisite.item_key = 'PAY-501'
WHERE dependent.item_key = 'PAY-502';

INSERT INTO item_dependencies (item_id, depends_on_item_id)
SELECT dependent.item_id, prerequisite.item_id
FROM backlog_items AS dependent
JOIN backlog_items AS prerequisite
  ON prerequisite.item_key = 'PAY-502'
WHERE dependent.item_key = 'PAY-505';

-- Record refinement outcomes separately from status transitions so that
-- estimate changes remain auditable.
INSERT INTO refinement_sessions (
    item_id, facilitator, outcome, notes, previous_effort, revised_effort
)
SELECT item_id, 'Product Owner', 'reestimated',
       'Reduced estimate after identifying reusable idempotency middleware.',
       6, 4
FROM backlog_items
WHERE item_key = 'PAY-501';

-- Move items through the same validation function used by application calls.
DO $$
DECLARE
    item_id_value BIGINT;
    item_key_value TEXT;
BEGIN
    FOR item_key_value IN
        SELECT item_key
        FROM backlog_items
        WHERE item_key IN ('PAY-501', 'PAY-502', 'PAY-503', 'PAY-504', 'PAY-505')
        ORDER BY item_key
    LOOP
        SELECT item_id INTO item_id_value
        FROM backlog_items
        WHERE item_key = item_key_value;

        PERFORM transition_backlog_item(item_id_value, 'refining', 'seed-workflow');

        IF item_key_value <> 'PAY-502' AND item_key_value <> 'PAY-505' THEN
            IF item_key_value IN ('PAY-501', 'PAY-503', 'PAY-504') THEN
                PERFORM transition_backlog_item(item_id_value, 'ready', 'seed-workflow');
            END IF;
        END IF;
    END LOOP;
END;
$$;

-- Priority ranking is a decision aid. Security urgency is explicitly elevated,
-- while dependency feasibility remains a separate condition.
SELECT
    item_key,
    title,
    priority,
    round(priority_score, 2) AS score,
    effort,
    status
FROM prioritized_backlog
ORDER BY
    CASE priority
        WHEN 'critical' THEN 0
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END,
    priority_score DESC,
    item_key;

-- Refinement readiness is not identical to priority: prerequisites and
-- acceptance criteria determine whether work can start.
SELECT
    item_key,
    status,
    unfinished_dependencies,
    acceptance_criteria_count,
    verified_criteria_count
FROM dependency_readiness
ORDER BY item_key;

SELECT * FROM technical_debt_forecast
ORDER BY projected_cost_four_sprints DESC;

-- Aggregate backlog composition to expose work-type and status imbalance.
SELECT
    item_type,
    status,
    count(*) AS item_count,
    sum(effort) AS estimated_effort,
    round(avg(business_value), 2) AS mean_business_value
FROM backlog_items
GROUP BY item_type, status
ORDER BY item_type, status;

-- A transaction can safely reject invalid changes without leaving partial data.
SAVEPOINT before_invalid_dependency;
DO $$
DECLARE
    first_item BIGINT;
    second_item BIGINT;
BEGIN
    SELECT item_id INTO first_item
    FROM backlog_items WHERE item_key = 'PAY-501';

    SELECT item_id INTO second_item
    FROM backlog_items WHERE item_key = 'PAY-502';

    BEGIN
        INSERT INTO item_dependencies (item_id, depends_on_item_id)
        VALUES (first_item, second_item);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid dependency correctly rejected: %', SQLERRM;
    END;
END;
$$;
RELEASE SAVEPOINT before_invalid_dependency;

COMMIT;
