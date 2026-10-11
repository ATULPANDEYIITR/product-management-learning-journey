-- PostgreSQL 15+
-- Product requirements domain: discovery evidence, PRDs, requirements,
-- acceptance criteria, delivery traceability, change control, and release readiness.

BEGIN;

CREATE SCHEMA IF NOT EXISTS product_requirements;
SET search_path TO product_requirements, public;

CREATE TYPE requirement_type AS ENUM (
    'functional',
    'non_functional',
    'business',
    'constraint'
);

CREATE TYPE requirement_priority AS ENUM ('must', 'should', 'could', 'wont');

CREATE TYPE requirement_status AS ENUM (
    'proposed',
    'in_review',
    'approved',
    'implemented',
    'verified',
    'rejected'
);

CREATE TYPE stakeholder_role AS ENUM (
    'product_manager',
    'business_owner',
    'end_user',
    'engineering',
    'security',
    'compliance',
    'operations',
    'executive'
);

CREATE TYPE change_status AS ENUM ('pending', 'approved', 'deferred', 'rejected');

CREATE TABLE products (
    product_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_key text NOT NULL UNIQUE,
    name text NOT NULL,
    problem_statement text NOT NULL,
    target_users text[] NOT NULL DEFAULT '{}',
    assumptions text[] NOT NULL DEFAULT '{}',
    out_of_scope text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT product_key_format CHECK (product_key ~ '^[A-Z][A-Z0-9_-]{2,39}$'),
    CONSTRAINT product_name_nonempty CHECK (length(trim(name)) > 0),
    CONSTRAINT product_problem_nonempty CHECK (length(trim(problem_statement)) >= 20)
);

CREATE TABLE stakeholders (
    stakeholder_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_key text NOT NULL UNIQUE,
    display_name text NOT NULL,
    role stakeholder_role NOT NULL,
    influence smallint NOT NULL CHECK (influence BETWEEN 1 AND 5),
    interest smallint NOT NULL CHECK (interest BETWEEN 1 AND 5),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT stakeholder_name_nonempty CHECK (length(trim(display_name)) > 0)
);

CREATE TABLE stakeholder_goals (
    stakeholder_id bigint NOT NULL REFERENCES stakeholders(stakeholder_id)
        ON DELETE CASCADE,
    goal_key text NOT NULL,
    goal_description text NOT NULL,
    PRIMARY KEY (stakeholder_id, goal_key),
    CONSTRAINT goal_description_nonempty CHECK (length(trim(goal_description)) > 0)
);

CREATE TABLE discovery_findings (
    finding_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id bigint NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    stakeholder_id bigint NOT NULL REFERENCES stakeholders(stakeholder_id),
    problem_observed text NOT NULL,
    evidence text NOT NULL,
    desired_outcome text NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT finding_problem_nonempty CHECK (length(trim(problem_observed)) > 0),
    CONSTRAINT finding_evidence_nonempty CHECK (length(trim(evidence)) > 0),
    CONSTRAINT finding_outcome_nonempty CHECK (length(trim(desired_outcome)) > 0)
);

CREATE TABLE prds (
    prd_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id bigint NOT NULL REFERENCES products(product_id),
    version integer NOT NULL CHECK (version > 0),
    title text NOT NULL,
    executive_summary text NOT NULL,
    release_name text NOT NULL,
    owner_id bigint NOT NULL REFERENCES stakeholders(stakeholder_id),
    approved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (product_id, version),
    CONSTRAINT prd_title_nonempty CHECK (length(trim(title)) > 0),
    CONSTRAINT prd_summary_nonempty CHECK (length(trim(executive_summary)) >= 20),
    CONSTRAINT prd_approval_after_creation CHECK (
        approved_at IS NULL OR approved_at >= created_at
    )
);

CREATE TABLE requirements (
    requirement_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prd_id bigint NOT NULL REFERENCES prds(prd_id),
    requirement_key text NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    requirement_kind requirement_type NOT NULL,
    priority requirement_priority NOT NULL,
    status requirement_status NOT NULL DEFAULT 'proposed',
    owner_id bigint NOT NULL REFERENCES stakeholders(stakeholder_id),
    source_finding_id bigint REFERENCES discovery_findings(finding_id),
    rationale text NOT NULL,
    verification_method text NOT NULL,
    target_metric text,
    risk_level text NOT NULL DEFAULT 'medium'
        CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    version integer NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (prd_id, requirement_key),
    CONSTRAINT requirement_key_format CHECK (
        requirement_key ~ '^REQ-(FR|NFR|BR|CON)-[0-9]{3}$'
    ),
    CONSTRAINT requirement_title_nonempty CHECK (length(trim(title)) > 0),
    CONSTRAINT requirement_description_specific CHECK (
        length(trim(description)) >= 15
    ),
    CONSTRAINT requirement_rationale_nonempty CHECK (length(trim(rationale)) > 0),
    CONSTRAINT verification_method_nonempty CHECK (
        length(trim(verification_method)) > 0
    ),
    CONSTRAINT nfr_requires_target CHECK (
        requirement_kind <> 'non_functional'
        OR (target_metric IS NOT NULL AND length(trim(target_metric)) > 0)
    )
);

CREATE TABLE acceptance_criteria (
    criterion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    requirement_id bigint NOT NULL REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    criterion_key text NOT NULL,
    given_context text NOT NULL,
    when_action text NOT NULL,
    then_outcome text NOT NULL,
    automated_test_key text,
    UNIQUE (requirement_id, criterion_key),
    CONSTRAINT criterion_given_nonempty CHECK (length(trim(given_context)) > 0),
    CONSTRAINT criterion_when_nonempty CHECK (length(trim(when_action)) > 0),
    CONSTRAINT criterion_then_nonempty CHECK (length(trim(then_outcome)) > 0)
);

CREATE TABLE requirement_dependencies (
    requirement_id bigint NOT NULL REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    depends_on_requirement_id bigint NOT NULL REFERENCES requirements(requirement_id)
        ON DELETE RESTRICT,
    dependency_reason text NOT NULL,
    PRIMARY KEY (requirement_id, depends_on_requirement_id),
    CONSTRAINT no_self_dependency CHECK (
        requirement_id <> depends_on_requirement_id
    ),
    CONSTRAINT dependency_reason_nonempty CHECK (
        length(trim(dependency_reason)) > 0
    )
);

CREATE TABLE delivery_items (
    delivery_item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_key text NOT NULL UNIQUE,
    title text NOT NULL,
    item_type text NOT NULL CHECK (
        item_type IN ('story', 'task', 'test', 'defect', 'epic')
    ),
    delivery_status text NOT NULL DEFAULT 'open' CHECK (
        delivery_status IN ('open', 'in_progress', 'done', 'blocked')
    ),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE requirement_delivery_links (
    requirement_id bigint NOT NULL REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    delivery_item_id bigint NOT NULL REFERENCES delivery_items(delivery_item_id)
        ON DELETE RESTRICT,
    link_type text NOT NULL CHECK (
        link_type IN ('implements', 'tests', 'blocks', 'validates')
    ),
    PRIMARY KEY (requirement_id, delivery_item_id, link_type)
);

CREATE TABLE requirement_reviews (
    review_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    requirement_id bigint NOT NULL REFERENCES requirements(requirement_id)
        ON DELETE CASCADE,
    reviewer_id bigint NOT NULL REFERENCES stakeholders(stakeholder_id),
    reviewed_version integer NOT NULL CHECK (reviewed_version > 0),
    decision text NOT NULL CHECK (
        decision IN ('comment', 'request_changes', 'approve', 'reject')
    ),
    rationale text NOT NULL,
    reviewed_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (requirement_id, reviewer_id, reviewed_version),
    CONSTRAINT review_rationale_nonempty CHECK (length(trim(rationale)) > 0)
);

CREATE TABLE requirement_changes (
    change_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    change_key text NOT NULL UNIQUE,
    requirement_id bigint NOT NULL REFERENCES requirements(requirement_id),
    requester_id bigint NOT NULL REFERENCES stakeholders(stakeholder_id),
    description text NOT NULL,
    estimated_effort_days numeric(8,2) NOT NULL CHECK (estimated_effort_days > 0),
    impact_assessment text NOT NULL,
    status change_status NOT NULL DEFAULT 'pending',
    decision_maker_id bigint REFERENCES stakeholders(stakeholder_id),
    decision_reason text,
    requested_at timestamptz NOT NULL DEFAULT now(),
    decided_at timestamptz,
    CONSTRAINT change_description_nonempty CHECK (length(trim(description)) > 0),
    CONSTRAINT change_impact_nonempty CHECK (length(trim(impact_assessment)) > 0),
    CONSTRAINT change_decision_consistent CHECK (
        (status = 'pending' AND decided_at IS NULL)
        OR
        (status <> 'pending' AND decided_at IS NOT NULL
            AND decision_maker_id IS NOT NULL
            AND decision_reason IS NOT NULL
            AND length(trim(decision_reason)) > 0)
    )
);

CREATE TABLE success_metrics (
    metric_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id bigint NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    metric_key text NOT NULL,
    description text NOT NULL,
    target_value numeric NOT NULL,
    unit text NOT NULL,
    measurement_window text NOT NULL,
    UNIQUE (product_id, metric_key),
    CONSTRAINT metric_description_nonempty CHECK (length(trim(description)) > 0),
    CONSTRAINT metric_unit_nonempty CHECK (length(trim(unit)) > 0)
);

CREATE INDEX idx_requirements_prd_priority
    ON requirements(prd_id, priority, status);

CREATE INDEX idx_requirements_owner_status
    ON requirements(owner_id, status);

CREATE INDEX idx_findings_product_recorded
    ON discovery_findings(product_id, recorded_at DESC);

CREATE INDEX idx_dependency_reverse
    ON requirement_dependencies(depends_on_requirement_id);

CREATE INDEX idx_reviews_requirement_version
    ON requirement_reviews(requirement_id, reviewed_version, decision);

CREATE INDEX idx_changes_requirement_status
    ON requirement_changes(requirement_id, status);

CREATE INDEX idx_delivery_items_status
    ON delivery_items(delivery_status, item_type);

-- Enforce acceptance criteria for functional requirements at transaction time.
-- Deferred checking permits a requirement and its criteria to be inserted in one transaction.
CREATE OR REPLACE FUNCTION assert_functional_criteria()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    checked_requirement_id bigint;
    checked_kind requirement_type;
    criterion_count bigint;
BEGIN
    checked_requirement_id := COALESCE(NEW.requirement_id, OLD.requirement_id);

    SELECT requirement_kind
      INTO checked_kind
      FROM requirements
     WHERE requirement_id = checked_requirement_id;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    IF checked_kind = 'functional' THEN
        SELECT count(*)
          INTO criterion_count
          FROM acceptance_criteria
         WHERE requirement_id = checked_requirement_id;

        IF criterion_count = 0 THEN
            RAISE EXCEPTION
                'Functional requirement % must have acceptance criteria',
                checked_requirement_id
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER functional_requirement_needs_criteria
AFTER INSERT OR UPDATE OF requirement_kind ON requirements
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION assert_functional_criteria();

CREATE CONSTRAINT TRIGGER criterion_change_preserves_functional_rule
AFTER INSERT OR UPDATE OR DELETE ON acceptance_criteria
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION assert_functional_criteria();

-- Insert a realistic product baseline and discovery evidence.
INSERT INTO products (
    product_key, name, problem_statement, target_users, assumptions, out_of_scope
) VALUES (
    'PROCUREFLOW',
    'ProcureFlow Supplier Portal',
    'Email-based supplier onboarding causes incomplete submissions, repeated follow-ups, and poor status visibility.',
    ARRAY[
        'Supplier representatives',
        'Procurement analysts',
        'Compliance officers'
    ],
    ARRAY[
        'Suppliers have access to a modern browser',
        'Administrators maintain category-specific document checklists'
    ],
    ARRAY[
        'Automated credit decisions',
        'International tax filing',
        'Contract negotiation'
    ]
);

INSERT INTO stakeholders (
    external_key, display_name, role, influence, interest
) VALUES
    ('ST-MAYA', 'Maya Rao', 'product_manager', 4, 5),
    ('ST-ARJUN', 'Arjun Sen', 'compliance', 5, 4),
    ('ST-DEV', 'Dev Mehta', 'engineering', 4, 3),
    ('ST-OPS', 'Nisha Kapoor', 'operations', 3, 5);

INSERT INTO stakeholder_goals (stakeholder_id, goal_key, goal_description)
SELECT stakeholder_id, 'reduce_rework', 'Reduce incomplete supplier submissions'
FROM stakeholders WHERE external_key = 'ST-MAYA';

INSERT INTO stakeholder_goals (stakeholder_id, goal_key, goal_description)
SELECT stakeholder_id, 'audit_evidence', 'Preserve compliance decisions and their rationale'
FROM stakeholders WHERE external_key = 'ST-ARJUN';

INSERT INTO discovery_findings (
    product_id, stakeholder_id, problem_observed, evidence, desired_outcome
)
SELECT
    p.product_id,
    s.stakeholder_id,
    'Supplier submissions frequently omit required documents',
    'The intake review found repeated requests for tax and registration evidence',
    'Validate document completeness before final submission'
FROM products p
JOIN stakeholders s ON s.external_key = 'ST-MAYA'
WHERE p.product_key = 'PROCUREFLOW';

INSERT INTO prds (
    product_id, version, title, executive_summary, release_name, owner_id
)
SELECT
    p.product_id,
    1,
    'Supplier onboarding PRD',
    'Defines supplier application intake, document validation, compliance decisions, and measurable operational targets.',
    'Release 1',
    s.stakeholder_id
FROM products p
JOIN stakeholders s ON s.external_key = 'ST-MAYA'
WHERE p.product_key = 'PROCUREFLOW';

INSERT INTO requirements (
    prd_id, requirement_key, title, description, requirement_kind, priority,
    owner_id, source_finding_id, rationale, verification_method, target_metric,
    risk_level
)
SELECT
    prd.prd_id,
    'REQ-FR-001',
    'Create supplier application',
    'Authenticated suppliers can create a draft with legal identity, registration country, tax identifier, and contact details.',
    'functional',
    'must',
    owner.stakeholder_id,
    finding.finding_id,
    'A structured intake replaces untracked email submissions.',
    'Integration tests',
    NULL,
    'high'
FROM prds prd
JOIN products p ON p.product_id = prd.product_id
JOIN stakeholders owner ON owner.external_key = 'ST-MAYA'
JOIN discovery_findings finding ON finding.product_id = p.product_id
WHERE p.product_key = 'PROCUREFLOW' AND prd.version = 1;

INSERT INTO requirements (
    prd_id, requirement_key, title, description, requirement_kind, priority,
    owner_id, source_finding_id, rationale, verification_method, target_metric,
    risk_level
)
SELECT
    prd.prd_id,
    'REQ-FR-002',
    'Validate document completeness',
    'The portal checks submitted documents against the published checklist for the supplier category.',
    'functional',
    'must',
    owner.stakeholder_id,
    finding.finding_id,
    'Early validation reduces compliance rework and incomplete submissions.',
    'Integration tests',
    NULL,
    'high'
FROM prds prd
JOIN products p ON p.product_id = prd.product_id
JOIN stakeholders owner ON owner.external_key = 'ST-ARJUN'
JOIN discovery_findings finding ON finding.product_id = p.product_id
WHERE p.product_key = 'PROCUREFLOW' AND prd.version = 1;

INSERT INTO requirements (
    prd_id, requirement_key, title, description, requirement_kind, priority,
    owner_id, source_finding_id, rationale, verification_method, target_metric,
    risk_level
)
SELECT
    prd.prd_id,
    'REQ-NFR-001',
    'Application read latency',
    'Application reads meet the defined latency target under the agreed concurrent-user workload.',
    'non_functional',
    'must',
    owner.stakeholder_id,
    NULL,
    'Predictable response times support supplier and analyst workflows.',
    'Load testing',
    'p95 < 300 ms at 500 concurrent users',
    'high'
FROM prds prd
JOIN products p ON p.product_id = prd.product_id
JOIN stakeholders owner ON owner.external_key = 'ST-DEV'
WHERE p.product_key = 'PROCUREFLOW' AND prd.version = 1;

INSERT INTO requirements (
    prd_id, requirement_key, title, description, requirement_kind, priority,
    owner_id, rationale, verification_method, target_metric, risk_level
)
SELECT
    prd.prd_id,
    'REQ-NFR-002',
    'Monthly service availability',
    'The production portal meets the agreed monthly availability objective outside approved maintenance windows.',
    'non_functional',
    'must',
    owner.stakeholder_id,
    'Unavailable intake blocks supplier onboarding.',
    'Service monitoring and incident review',
    'monthly availability >= 99.9%',
    'critical'
FROM prds prd
JOIN products p ON p.product_id = prd.product_id
JOIN stakeholders owner ON owner.external_key = 'ST-OPS'
WHERE p.product_key = 'PROCUREFLOW' AND prd.version = 1;

INSERT INTO requirements (
    prd_id, requirement_key, title, description, requirement_kind, priority,
    owner_id, rationale, verification_method, target_metric, risk_level
)
SELECT
    prd.prd_id,
    'REQ-CON-001',
    'Retain compliance decision evidence',
    'The portal retains supplier compliance decisions and supporting rationale for seven years under the approved retention policy.',
    'constraint',
    'must',
    owner.stakeholder_id,
    'Records retention is a binding compliance obligation.',
    'Retention-policy integration test',
    NULL,
    'critical'
FROM prds prd
JOIN products p ON p.product_id = prd.product_id
JOIN stakeholders owner ON owner.external_key = 'ST-ARJUN'
WHERE p.product_key = 'PROCUREFLOW' AND prd.version = 1;

INSERT INTO acceptance_criteria (
    requirement_id, criterion_key, given_context, when_action, then_outcome,
    automated_test_key
)
SELECT requirement_id, 'AC-001',
       'The supplier is authenticated',
       'The supplier submits valid required fields',
       'The portal creates a draft and returns its reference',
       'test_supplier_draft_creation'
FROM requirements WHERE requirement_key = 'REQ-FR-001';

INSERT INTO acceptance_criteria (
    requirement_id, criterion_key, given_context, when_action, then_outcome,
    automated_test_key
)
SELECT requirement_id, 'AC-002',
       'A tax identifier is already registered for the legal entity',
       'The supplier submits another application',
       'The portal rejects the duplicate without exposing another supplier data',
       'test_duplicate_supplier_rejected'
FROM requirements WHERE requirement_key = 'REQ-FR-001';

INSERT INTO acceptance_criteria (
    requirement_id, criterion_key, given_context, when_action, then_outcome,
    automated_test_key
)
SELECT requirement_id, 'AC-001',
       'A published category checklist exists',
       'The supplier attempts final submission',
       'The portal reports missing documents and blocks final submission',
       'test_missing_documents_block_submission'
FROM requirements WHERE requirement_key = 'REQ-FR-002';

INSERT INTO requirement_dependencies (
    requirement_id, depends_on_requirement_id, dependency_reason
)
SELECT dependent.requirement_id, prerequisite.requirement_id,
       'An application must exist before its documents can be validated.'
FROM requirements dependent
JOIN requirements prerequisite ON prerequisite.requirement_key = 'REQ-FR-001'
WHERE dependent.requirement_key = 'REQ-FR-002';

INSERT INTO delivery_items (external_key, title, item_type, delivery_status)
VALUES
    ('SUP-101', 'Implement supplier application intake', 'story', 'done'),
    ('SUP-110', 'Validate required supplier documents', 'story', 'in_progress'),
    ('OPS-40', 'Measure application read latency', 'test', 'done'),
    ('OPS-41', 'Configure availability monitoring', 'task', 'open'),
    ('DATA-18', 'Implement retention controls', 'task', 'open');

INSERT INTO requirement_delivery_links (
    requirement_id, delivery_item_id, link_type
)
SELECT r.requirement_id, d.delivery_item_id, 'implements'
FROM requirements r
JOIN delivery_items d ON
    (r.requirement_key = 'REQ-FR-001' AND d.external_key = 'SUP-101')
    OR
    (r.requirement_key = 'REQ-FR-002' AND d.external_key = 'SUP-110')
    OR
    (r.requirement_key = 'REQ-NFR-001' AND d.external_key = 'OPS-40')
    OR
    (r.requirement_key = 'REQ-NFR-002' AND d.external_key = 'OPS-41')
    OR
    (r.requirement_key = 'REQ-CON-001' AND d.external_key = 'DATA-18');

INSERT INTO success_metrics (
    product_id, metric_key, description, target_value, unit, measurement_window
)
SELECT product_id, 'first_submission_completeness',
       'Percentage of supplier applications complete on first submission',
       95, 'percent', 'Monthly after launch'
FROM products WHERE product_key = 'PROCUREFLOW';

INSERT INTO success_metrics (
    product_id, metric_key, description, target_value, unit, measurement_window
)
SELECT product_id, 'median_onboarding_days',
       'Median number of business days from application start to completion',
       5, 'business_days', 'First quarter after launch'
FROM products WHERE product_key = 'PROCUREFLOW';

-- Reviews are version-specific. A new requirement version needs a fresh decision.
INSERT INTO requirement_reviews (
    requirement_id, reviewer_id, reviewed_version, decision, rationale
)
SELECT r.requirement_id, s.stakeholder_id, 1, 'approve',
       'Acceptance criteria are testable and cover duplicate intake.'
FROM requirements r
JOIN stakeholders s ON s.external_key = 'ST-MAYA'
WHERE r.requirement_key = 'REQ-FR-001';

INSERT INTO requirement_reviews (
    requirement_id, reviewer_id, reviewed_version, decision, rationale
)
SELECT r.requirement_id, s.stakeholder_id, 1, 'request_changes',
       'Clarify how a supplier-category change affects mandatory documents.'
FROM requirements r
JOIN stakeholders s ON s.external_key = 'ST-ARJUN'
WHERE r.requirement_key = 'REQ-FR-002';

INSERT INTO requirement_changes (
    change_key, requirement_id, requester_id, description,
    estimated_effort_days, impact_assessment, status
)
SELECT
    'CR-014',
    r.requirement_id,
    s.stakeholder_id,
    'Add notifications before supplier documents expire',
    4.0,
    'Requires scheduling, notification preferences, and monitoring.',
    'pending'
FROM requirements r
JOIN stakeholders s ON s.external_key = 'ST-ARJUN'
WHERE r.requirement_key = 'REQ-FR-002';

-- Product-level PRD coverage, useful for detecting requirements with no implementation link.
CREATE VIEW requirement_traceability AS
SELECT
    p.product_key,
    prd.version AS prd_version,
    r.requirement_key,
    r.title,
    r.requirement_kind,
    r.priority,
    r.status,
    owner.display_name AS requirement_owner,
    COUNT(DISTINCT ac.criterion_id) AS acceptance_criteria_count,
    COUNT(DISTINCT rdl.delivery_item_id) AS delivery_link_count,
    COUNT(DISTINCT rv.review_id) AS review_count
FROM requirements r
JOIN prds prd ON prd.prd_id = r.prd_id
JOIN products p ON p.product_id = prd.product_id
JOIN stakeholders owner ON owner.stakeholder_id = r.owner_id
LEFT JOIN acceptance_criteria ac ON ac.requirement_id = r.requirement_id
LEFT JOIN requirement_delivery_links rdl
    ON rdl.requirement_id = r.requirement_id
LEFT JOIN requirement_reviews rv ON rv.requirement_id = r.requirement_id
GROUP BY
    p.product_key, prd.version, r.requirement_id, r.requirement_key,
    r.title, r.requirement_kind, r.priority, r.status, owner.display_name;

-- Detect missing delivery links and missing acceptance criteria.
CREATE VIEW requirement_quality_gaps AS
SELECT
    r.requirement_key,
    r.title,
    CASE
        WHEN r.requirement_kind = 'functional'
         AND NOT EXISTS (
             SELECT 1 FROM acceptance_criteria ac
             WHERE ac.requirement_id = r.requirement_id
         )
        THEN 'missing acceptance criteria'
        WHEN NOT EXISTS (
             SELECT 1 FROM requirement_delivery_links rdl
             WHERE rdl.requirement_id = r.requirement_id
         )
        THEN 'missing delivery trace'
        WHEN r.requirement_kind = 'non_functional'
         AND r.target_metric IS NULL
        THEN 'missing measurable target'
        ELSE 'no detected gap'
    END AS gap
FROM requirements r;

-- Mandatory requirements that have not been verified block release readiness.
CREATE VIEW release_readiness AS
SELECT
    prd.prd_id,
    p.product_key,
    prd.version,
    COUNT(r.requirement_id) FILTER (
        WHERE r.priority = 'must' AND r.status <> 'rejected'
    ) AS mandatory_requirements,
    COUNT(r.requirement_id) FILTER (
        WHERE r.priority = 'must'
          AND r.status <> 'rejected'
          AND r.status = 'verified'
    ) AS verified_mandatory_requirements,
    COUNT(r.requirement_id) FILTER (
        WHERE r.priority = 'must'
          AND r.status <> 'rejected'
          AND r.status <> 'verified'
    ) AS unverified_mandatory_requirements
FROM prds prd
JOIN products p ON p.product_id = prd.product_id
LEFT JOIN requirements r ON r.prd_id = prd.prd_id
GROUP BY prd.prd_id, p.product_key, prd.version;

-- Discovery coverage exposes products whose requirements lack stakeholder evidence.
CREATE VIEW discovery_coverage AS
SELECT
    p.product_key,
    COUNT(DISTINCT r.requirement_id) AS requirement_count,
    COUNT(DISTINCT r.requirement_id) FILTER (
        WHERE r.source_finding_id IS NOT NULL
    ) AS evidence_linked_requirements
FROM products p
JOIN prds prd ON prd.product_id = p.product_id
LEFT JOIN requirements r ON r.prd_id = prd.prd_id
GROUP BY p.product_key;

COMMIT;

-- Review the traceability baseline.
SELECT *
FROM requirement_traceability
ORDER BY requirement_key;

-- Find incomplete requirements and their specific quality gaps.
SELECT requirement_key, title, gap
FROM requirement_quality_gaps
WHERE gap <> 'no detected gap'
ORDER BY requirement_key;

-- Check whether the mandatory baseline is ready for release.
SELECT *
FROM release_readiness
ORDER BY product_key, version;

-- Compare stakeholder evidence coverage.
SELECT *
FROM discovery_coverage
ORDER BY product_key;

-- Inspect the implementation dependency graph.
SELECT
    dependent.requirement_key AS dependent_requirement,
    prerequisite.requirement_key AS prerequisite_requirement,
    dependency.dependency_reason
FROM requirement_dependencies dependency
JOIN requirements dependent
    ON dependent.requirement_id = dependency.requirement_id
JOIN requirements prerequisite
    ON prerequisite.requirement_id = dependency.depends_on_requirement_id
ORDER BY dependent.requirement_key;

-- Rank only optional features using RICE. Mandatory requirements remain obligations.
WITH optional_features AS (
    SELECT
        'Document expiry reminders'::text AS feature,
        500::numeric AS reach,
        1.5::numeric AS impact,
        0.80::numeric AS confidence,
        4.0::numeric AS effort_days
    UNION ALL
    SELECT
        'Supplier dashboard export',
        350::numeric,
        1.0::numeric,
        0.90::numeric,
        2.0::numeric
    UNION ALL
    SELECT
        'Custom portal themes',
        80::numeric,
        0.5::numeric,
        0.70::numeric,
        3.0::numeric
)
SELECT
    feature,
    round(reach * impact * confidence / NULLIF(effort_days, 0), 2) AS rice_score
FROM optional_features
WHERE reach >= 0
  AND impact >= 0
  AND confidence BETWEEN 0 AND 1
  AND effort_days > 0
ORDER BY rice_score DESC;

-- Example of atomic change-decision handling. The pending change is deferred with
-- a named decision maker and a reason, keeping the original requirement unchanged.
BEGIN;

UPDATE requirement_changes
SET status = 'deferred',
    decision_maker_id = (
        SELECT stakeholder_id
        FROM stakeholders
        WHERE external_key = 'ST-MAYA'
    ),
    decision_reason = 'Defer until release capacity and notification policy are approved.',
    decided_at = now()
WHERE change_key = 'CR-014'
  AND status = 'pending';

COMMIT;

SELECT change_key, status, decision_reason, decided_at
FROM requirement_changes
WHERE change_key = 'CR-014';
