-- PostgreSQL 15+
-- Relational PRD management and governance workflow.
--
-- The schema separates the product document from requirements, acceptance
-- criteria, user personas, review decisions, risk records, and release gates.
-- Constraints enforce local invariants; triggers enforce selected workflow rules.

BEGIN;

DROP SCHEMA IF EXISTS prd_governance CASCADE;
CREATE SCHEMA prd_governance;
SET search_path TO prd_governance, public;

CREATE TYPE document_status AS ENUM (
    'Draft', 'In Review', 'Approved', 'Released', 'Archived'
);

CREATE TYPE requirement_priority AS ENUM (
    'Must', 'Should', 'Could', 'Won''t'
);

CREATE TYPE requirement_type AS ENUM (
    'Functional', 'Non-functional', 'Business', 'Technical', 'Compliance'
);

CREATE TYPE requirement_status AS ENUM (
    'Draft', 'In Review', 'Approved', 'Implemented', 'Verified', 'Rejected'
);

CREATE TYPE review_decision AS ENUM (
    'Approve', 'Request Changes', 'Reject'
);

CREATE TYPE risk_severity AS ENUM (
    'Low', 'Medium', 'High', 'Critical'
);

CREATE TABLE product_documents (
    document_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name TEXT NOT NULL CHECK (btrim(product_name) <> ''),
    version TEXT NOT NULL CHECK (version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),
    status document_status NOT NULL DEFAULT 'Draft',
    author TEXT NOT NULL CHECK (btrim(author) <> ''),
    created_on DATE NOT NULL DEFAULT CURRENT_DATE,
    problem_statement TEXT NOT NULL CHECK (btrim(problem_statement) <> ''),
    UNIQUE (product_name, version)
);

CREATE TABLE problem_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    evidence_type TEXT NOT NULL CHECK (btrim(evidence_type) <> ''),
    description TEXT NOT NULL CHECK (btrim(description) <> ''),
    source_reference TEXT,
    observed_on DATE
);

CREATE TABLE product_goals (
    goal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    goal_name TEXT NOT NULL CHECK (btrim(goal_name) <> ''),
    metric_name TEXT NOT NULL CHECK (btrim(metric_name) <> ''),
    baseline_value NUMERIC,
    target_value NUMERIC NOT NULL,
    unit TEXT NOT NULL CHECK (btrim(unit) <> ''),
    measurement_window TEXT NOT NULL CHECK (btrim(measurement_window) <> ''),
    UNIQUE (document_id, goal_name),
    CHECK (baseline_value IS NULL OR baseline_value >= 0),
    CHECK (target_value >= 0)
);

CREATE TABLE user_personas (
    persona_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    persona_name TEXT NOT NULL CHECK (btrim(persona_name) <> ''),
    description TEXT NOT NULL CHECK (btrim(description) <> ''),
    UNIQUE (document_id, persona_name)
);

CREATE TABLE persona_needs (
    need_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    persona_id BIGINT NOT NULL REFERENCES user_personas(persona_id)
        ON DELETE CASCADE,
    need_description TEXT NOT NULL CHECK (btrim(need_description) <> ''),
    priority requirement_priority NOT NULL DEFAULT 'Should'
);

CREATE TABLE persona_pain_points (
    pain_point_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    persona_id BIGINT NOT NULL REFERENCES user_personas(persona_id)
        ON DELETE CASCADE,
    description TEXT NOT NULL CHECK (btrim(description) <> '')
);

CREATE TABLE scope_items (
    scope_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    item_description TEXT NOT NULL CHECK (btrim(item_description) <> ''),
    included BOOLEAN NOT NULL,
    rationale TEXT NOT NULL CHECK (btrim(rationale) <> ''),
    UNIQUE (document_id, item_description)
);

CREATE TABLE product_requirements (
    requirement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    requirement_key TEXT NOT NULL CHECK (
        requirement_key ~ '^REQ-[A-Z0-9-]+$'
    ),
    title TEXT NOT NULL CHECK (btrim(title) <> ''),
    description TEXT NOT NULL CHECK (btrim(description) <> ''),
    rationale TEXT NOT NULL CHECK (btrim(rationale) <> ''),
    type requirement_type NOT NULL,
    priority requirement_priority NOT NULL,
    status requirement_status NOT NULL DEFAULT 'Draft',
    owner TEXT NOT NULL CHECK (btrim(owner) <> ''),
    estimate_points INTEGER NOT NULL DEFAULT 3 CHECK (estimate_points >= 0),
    source TEXT NOT NULL DEFAULT 'Product discovery',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, requirement_key)
);

CREATE TABLE requirement_dependencies (
    requirement_id BIGINT NOT NULL REFERENCES product_requirements(requirement_id)
        ON DELETE CASCADE,
    depends_on_requirement_id BIGINT NOT NULL
        REFERENCES product_requirements(requirement_id) ON DELETE RESTRICT,
    dependency_reason TEXT NOT NULL CHECK (btrim(dependency_reason) <> ''),
    PRIMARY KEY (requirement_id, depends_on_requirement_id),
    CHECK (requirement_id <> depends_on_requirement_id)
);

CREATE TABLE acceptance_criteria (
    criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    requirement_id BIGINT NOT NULL REFERENCES product_requirements(requirement_id)
        ON DELETE CASCADE,
    criterion_key TEXT NOT NULL CHECK (
        criterion_key ~ '^AC-[A-Z0-9-]+$'
    ),
    given_condition TEXT NOT NULL CHECK (btrim(given_condition) <> ''),
    when_action TEXT NOT NULL CHECK (btrim(when_action) <> ''),
    then_outcome TEXT NOT NULL CHECK (btrim(then_outcome) <> ''),
    verification_method TEXT NOT NULL CHECK (btrim(verification_method) <> ''),
    UNIQUE (requirement_id, criterion_key)
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name TEXT NOT NULL CHECK (btrim(display_name) <> ''),
    role_name TEXT NOT NULL CHECK (btrim(role_name) <> ''),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (display_name, role_name)
);

CREATE TABLE requirement_reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    requirement_id BIGINT NOT NULL REFERENCES product_requirements(requirement_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id)
        ON DELETE RESTRICT,
    decision review_decision NOT NULL,
    rationale TEXT NOT NULL CHECK (btrim(rationale) <> ''),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    superseded_at TIMESTAMPTZ,
    UNIQUE (requirement_id, reviewer_id, recorded_at),
    CHECK (superseded_at IS NULL OR superseded_at >= recorded_at)
);

CREATE TABLE requirement_review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES requirement_reviews(review_id)
        ON DELETE CASCADE,
    criterion_id BIGINT REFERENCES acceptance_criteria(criterion_id)
        ON DELETE SET NULL,
    comment_text TEXT NOT NULL CHECK (btrim(comment_text) <> ''),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolution_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    CHECK (
        (resolved = FALSE AND resolved_at IS NULL)
        OR (resolved = TRUE AND resolved_at IS NOT NULL)
    )
);

CREATE TABLE requirement_test_results (
    test_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    criterion_id BIGINT NOT NULL REFERENCES acceptance_criteria(criterion_id)
        ON DELETE CASCADE,
    test_run_key TEXT NOT NULL CHECK (btrim(test_run_key) <> ''),
    passed BOOLEAN NOT NULL,
    tester TEXT NOT NULL CHECK (btrim(tester) <> ''),
    details TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (criterion_id, test_run_key)
);

CREATE TABLE requirement_risks (
    risk_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    risk_key TEXT NOT NULL CHECK (risk_key ~ '^RISK-[A-Z0-9-]+$'),
    description TEXT NOT NULL CHECK (btrim(description) <> ''),
    probability INTEGER NOT NULL CHECK (probability BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 5),
    mitigation TEXT NOT NULL CHECK (btrim(mitigation) <> ''),
    contingency TEXT NOT NULL CHECK (btrim(contingency) <> ''),
    owner TEXT NOT NULL CHECK (btrim(owner) <> ''),
    UNIQUE (document_id, risk_key)
);

CREATE TABLE release_criteria (
    release_criterion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES product_documents(document_id)
        ON DELETE CASCADE,
    description TEXT NOT NULL CHECK (btrim(description) <> ''),
    required BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (document_id, description)
);

CREATE TABLE document_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT REFERENCES product_documents(document_id)
        ON DELETE SET NULL,
    requirement_id BIGINT REFERENCES product_requirements(requirement_id)
        ON DELETE SET NULL,
    actor TEXT NOT NULL CHECK (btrim(actor) <> ''),
    event_type TEXT NOT NULL CHECK (btrim(event_type) <> ''),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_requirements_document_priority
    ON product_requirements(document_id, priority, status);

CREATE INDEX idx_requirements_status_updated
    ON product_requirements(status, updated_at DESC);

CREATE INDEX idx_dependencies_reverse
    ON requirement_dependencies(depends_on_requirement_id);

CREATE INDEX idx_reviews_current
    ON requirement_reviews(requirement_id, reviewer_id, recorded_at DESC)
    WHERE superseded_at IS NULL;

CREATE INDEX idx_open_review_comments
    ON requirement_review_comments(review_id, created_at)
    WHERE resolved = FALSE;

CREATE INDEX idx_risks_document_score
    ON requirement_risks(document_id, probability, impact);

CREATE INDEX idx_audit_document_time
    ON document_audit_log(document_id, occurred_at DESC);

-- A current review is the latest unsuperseded decision from a reviewer.
-- The application can supersede a previous record instead of erasing history.
CREATE VIEW current_requirement_reviews AS
SELECT DISTINCT ON (rr.requirement_id, rr.reviewer_id)
       rr.review_id,
       rr.requirement_id,
       rr.reviewer_id,
       rv.display_name AS reviewer_name,
       rv.role_name,
       rr.decision,
       rr.rationale,
       rr.recorded_at
FROM requirement_reviews rr
JOIN reviewers rv ON rv.reviewer_id = rr.reviewer_id
WHERE rr.superseded_at IS NULL
ORDER BY rr.requirement_id, rr.reviewer_id, rr.recorded_at DESC;

CREATE VIEW requirement_approval_summary AS
SELECT
    r.requirement_id,
    r.requirement_key,
    r.priority,
    r.status,
    COUNT(DISTINCT cr.reviewer_id)
        FILTER (WHERE cr.decision = 'Approve') AS approval_count,
    COUNT(DISTINCT cr.reviewer_id)
        FILTER (WHERE cr.decision = 'Request Changes') AS change_request_count,
    COUNT(DISTINCT cr.reviewer_id)
        FILTER (WHERE cr.decision = 'Reject') AS rejection_count
FROM product_requirements r
LEFT JOIN current_requirement_reviews cr
    ON cr.requirement_id = r.requirement_id
GROUP BY r.requirement_id, r.requirement_key, r.priority, r.status;

CREATE VIEW requirement_acceptance_summary AS
SELECT
    r.requirement_id,
    r.requirement_key,
    COUNT(DISTINCT ac.criterion_id) AS criterion_count,
    COUNT(DISTINCT ac.criterion_id)
        FILTER (WHERE latest.passed = TRUE) AS passed_criterion_count,
    COUNT(DISTINCT ac.criterion_id)
        FILTER (WHERE latest.passed = FALSE) AS failed_criterion_count
FROM product_requirements r
LEFT JOIN acceptance_criteria ac
    ON ac.requirement_id = r.requirement_id
LEFT JOIN LATERAL (
    SELECT tr.passed
    FROM requirement_test_results tr
    WHERE tr.criterion_id = ac.criterion_id
    ORDER BY tr.executed_at DESC, tr.test_result_id DESC
    LIMIT 1
) latest ON TRUE
GROUP BY r.requirement_id, r.requirement_key;

-- Prevent dependency cycles before a new edge is inserted.
CREATE FUNCTION prevent_requirement_dependency_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.requirement_id = NEW.depends_on_requirement_id THEN
        RAISE EXCEPTION 'A requirement cannot depend on itself';
    END IF;

    IF EXISTS (
        WITH RECURSIVE dependency_walk(node_id) AS (
            SELECT NEW.depends_on_requirement_id
            UNION
            SELECT rd.depends_on_requirement_id
            FROM requirement_dependencies rd
            JOIN dependency_walk dw
              ON rd.requirement_id = dw.node_id
        )
        SELECT 1
        FROM dependency_walk
        WHERE node_id = NEW.requirement_id
    ) THEN
        RAISE EXCEPTION
            'Dependency edge would create a cycle: % -> %',
            NEW.requirement_id, NEW.depends_on_requirement_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_dependency_cycle
BEFORE INSERT OR UPDATE OF requirement_id, depends_on_requirement_id
ON requirement_dependencies
FOR EACH ROW
EXECUTE FUNCTION prevent_requirement_dependency_cycle();

-- A requirement cannot be marked Verified until every criterion has a latest
-- successful test result. Empty criteria are rejected at the transition too.
CREATE FUNCTION enforce_requirement_verification()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    total_criteria INTEGER;
    passing_criteria INTEGER;
BEGIN
    IF NEW.status = 'Verified' AND OLD.status <> 'Verified' THEN
        SELECT COUNT(*)
        INTO total_criteria
        FROM acceptance_criteria
        WHERE requirement_id = NEW.requirement_id;

        IF total_criteria = 0 THEN
            RAISE EXCEPTION
                'Requirement % has no acceptance criteria',
                NEW.requirement_key;
        END IF;

        SELECT COUNT(*)
        INTO passing_criteria
        FROM acceptance_criteria ac
        WHERE ac.requirement_id = NEW.requirement_id
          AND EXISTS (
              SELECT 1
              FROM requirement_test_results tr
              WHERE tr.criterion_id = ac.criterion_id
                AND tr.passed = TRUE
                AND tr.executed_at = (
                    SELECT MAX(tr2.executed_at)
                    FROM requirement_test_results tr2
                    WHERE tr2.criterion_id = ac.criterion_id
                )
          );

        IF passing_criteria <> total_criteria THEN
            RAISE EXCEPTION
                'Requirement % has % passing criteria out of %',
                NEW.requirement_key, passing_criteria, total_criteria;
        END IF;
    END IF;

    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_requirement_verification
BEFORE UPDATE OF status
ON product_requirements
FOR EACH ROW
EXECUTE FUNCTION enforce_requirement_verification();

-- Approval decisions must come from active reviewers and must not be made
-- by the requirement owner. The review itself does not automatically approve
-- a requirement; the configured workflow controls the state transition.
CREATE FUNCTION validate_requirement_review()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    reviewer_is_active BOOLEAN;
    requirement_owner TEXT;
    current_status requirement_status;
BEGIN
    SELECT active, display_name
    INTO reviewer_is_active, requirement_owner
    FROM reviewers
    WHERE reviewer_id = NEW.reviewer_id;

    IF NOT FOUND OR reviewer_is_active IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'Reviewer must exist and be active';
    END IF;

    SELECT owner, status
    INTO requirement_owner, current_status
    FROM product_requirements
    WHERE requirement_id = NEW.requirement_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Requirement does not exist';
    END IF;

    IF current_status <> 'In Review' THEN
        RAISE EXCEPTION 'Requirement must be In Review before a review is recorded';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM reviewers
        WHERE reviewer_id = NEW.reviewer_id
          AND display_name = requirement_owner
    ) THEN
        RAISE EXCEPTION 'Requirement owners cannot review their own requirement';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_requirement_review
BEFORE INSERT ON requirement_reviews
FOR EACH ROW
EXECUTE FUNCTION validate_requirement_review();

-- Insert a realistic procurement portal PRD.
INSERT INTO product_documents (
    product_name, version, status, author, problem_statement
) VALUES (
    'Procurement Request Portal',
    '1.0.0',
    'Draft',
    'Product Management',
    'Email-based purchase requests are incomplete, difficult to track, and hard to audit.'
);

INSERT INTO problem_evidence (
    document_id, evidence_type, description, source_reference, observed_on
)
SELECT document_id, 'Discovery interview',
       'Employees repeatedly receive requests to supply missing cost centers.',
       'PROC-DISCOVERY-01', CURRENT_DATE
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO problem_evidence (
    document_id, evidence_type, description, source_reference, observed_on
)
SELECT document_id, 'Workflow observation',
       'Approvers are identified using manually maintained spreadsheets.',
       'PROC-WORKFLOW-02', CURRENT_DATE
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO product_goals (
    document_id, goal_name, metric_name, baseline_value,
    target_value, unit, measurement_window
)
SELECT document_id, 'Submission completeness',
       'Requests passing initial validation', 72, 95, 'percent',
       'First three months after launch'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO product_goals (
    document_id, goal_name, metric_name, baseline_value,
    target_value, unit, measurement_window
)
SELECT document_id, 'Approval routing accuracy',
       'Requests assigned to the correct approval path', 90, 99, 'percent',
       'Monthly after launch'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO user_personas (document_id, persona_name, description)
SELECT document_id, 'Employee Requester',
       'Employee who submits a purchase request and tracks its progress.'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO user_personas (document_id, persona_name, description)
SELECT document_id, 'Procurement Approver',
       'Authorized employee who evaluates a request within delegated authority.'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO persona_needs (persona_id, need_description, priority)
SELECT persona_id, 'Submit a complete request with clear validation feedback.', 'Must'
FROM user_personas WHERE persona_name = 'Employee Requester';

INSERT INTO persona_needs (persona_id, need_description, priority)
SELECT persona_id, 'Receive requests with sufficient evidence and clear ownership.', 'Must'
FROM user_personas WHERE persona_name = 'Procurement Approver';

INSERT INTO persona_pain_points (persona_id, description)
SELECT persona_id, 'Repeatedly supplying missing request information.'
FROM user_personas WHERE persona_name = 'Employee Requester';

INSERT INTO scope_items (document_id, item_description, included, rationale)
SELECT document_id, 'Authenticated purchase-request submission', TRUE,
       'Provides a consistent entry point for procurement requests.'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO scope_items (document_id, item_description, included, rationale)
SELECT document_id, 'Supplier payment execution', FALSE,
       'Payment execution remains within the financial system.'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO product_requirements (
    document_id, requirement_key, title, description, rationale,
    type, priority, owner, estimate_points
)
SELECT document_id, 'REQ-401',
       'Validate purchase requests',
       'Reject submissions missing mandatory fields and provide field-specific errors.',
       'Complete submissions reduce manual rework.',
       'Functional', 'Must', 'Product Manager', 5
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO product_requirements (
    document_id, requirement_key, title, description, rationale,
    type, priority, owner, estimate_points
)
SELECT document_id, 'REQ-402',
       'Route requests using approval policy',
       'Assign requests according to the active amount and cost-center approval matrix.',
       'Routing must follow delegated financial authority.',
       'Functional', 'Must', 'Procurement Lead', 8
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO product_requirements (
    document_id, requirement_key, title, description, rationale,
    type, priority, owner, estimate_points
)
SELECT document_id, 'REQ-403',
       'Display request status',
       'Allow requesters to see their request state and authorized decision history.',
       'Status visibility reduces manual enquiries.',
       'Functional', 'Should', 'Product Manager', 3
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO requirement_dependencies (
    requirement_id, depends_on_requirement_id, dependency_reason
)
SELECT downstream.requirement_id, upstream.requirement_id,
       'Request routing requires a validated request record.'
FROM product_requirements downstream
JOIN product_requirements upstream
  ON downstream.document_id = upstream.document_id
WHERE downstream.requirement_key = 'REQ-402'
  AND upstream.requirement_key = 'REQ-401';

INSERT INTO acceptance_criteria (
    requirement_id, criterion_key, given_condition,
    when_action, then_outcome, verification_method
)
SELECT requirement_id, 'AC-401-A',
       'All mandatory fields are present',
       'The requester submits the form',
       'The system creates a uniquely identified request',
       'Integration test'
FROM product_requirements WHERE requirement_key = 'REQ-401';

INSERT INTO acceptance_criteria (
    requirement_id, criterion_key, given_condition,
    when_action, then_outcome, verification_method
)
SELECT requirement_id, 'AC-401-B',
       'The cost center is missing',
       'The requester submits the form',
       'The system rejects submission with a field-specific validation error',
       'Negative integration test'
FROM product_requirements WHERE requirement_key = 'REQ-401';

INSERT INTO acceptance_criteria (
    requirement_id, criterion_key, given_condition,
    when_action, then_outcome, verification_method
)
SELECT requirement_id, 'AC-402-A',
       'An active approval policy matches the request',
       'The routing service evaluates the request',
       'The request is assigned to the configured approver group',
       'Policy-routing integration test'
FROM product_requirements WHERE requirement_key = 'REQ-402';

INSERT INTO reviewers (display_name, role_name) VALUES
    ('Procurement Lead', 'Procurement'),
    ('Finance Lead', 'Finance'),
    ('Security Lead', 'Security'),
    ('QA Lead', 'Quality Assurance');

INSERT INTO requirement_risks (
    document_id, risk_key, description, probability, impact,
    mitigation, contingency, owner
)
SELECT document_id, 'RISK-401',
       'Approval thresholds may be outdated or contradictory.',
       4, 5,
       'Validate policy ownership, effective dates, and threshold overlap.',
       'Hold unmatched requests for authorized manual resolution.',
       'Procurement Operations'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO requirement_risks (
    document_id, risk_key, description, probability, impact,
    mitigation, contingency, owner
)
SELECT document_id, 'RISK-402',
       'Supporting documents may expose confidential commercial information.',
       3, 5,
       'Enforce request-level authorization, encryption, and retention controls.',
       'Restrict access and follow the security incident response process.',
       'Security Lead'
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO release_criteria (document_id, description, required)
SELECT document_id, 'All Must requirements pass acceptance tests.', TRUE
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

INSERT INTO release_criteria (document_id, description, required)
SELECT document_id, 'No unresolved critical security defect remains.', TRUE
FROM product_documents
WHERE product_name = 'Procurement Request Portal' AND version = '1.0.0';

-- Record that the first requirement has entered review.
UPDATE product_requirements
SET status = 'In Review'
WHERE requirement_key = 'REQ-401';

INSERT INTO requirement_reviews (
    requirement_id, reviewer_id, decision, rationale
)
SELECT r.requirement_id, rv.reviewer_id, 'Approve',
       'Mandatory fields and field-specific validation are clearly defined.'
FROM product_requirements r
JOIN reviewers rv ON rv.display_name = 'Procurement Lead'
WHERE r.requirement_key = 'REQ-401';

INSERT INTO requirement_review_comments (
    review_id, criterion_id, comment_text, resolved, resolution_note, resolved_at
)
SELECT rr.review_id, ac.criterion_id,
       'Confirm that validation is enforced by the server, not only the browser.',
       TRUE,
       'Server-side validation is part of the API acceptance test.',
       now()
FROM requirement_reviews rr
JOIN product_requirements r ON r.requirement_id = rr.requirement_id
JOIN acceptance_criteria ac
  ON ac.requirement_id = r.requirement_id
 AND ac.criterion_key = 'AC-401-B'
WHERE r.requirement_key = 'REQ-401';

INSERT INTO requirement_test_results (
    criterion_id, test_run_key, passed, tester, details
)
SELECT criterion_id, 'RUN-401-A', TRUE, 'QA Lead',
       'A complete request created one request identifier.'
FROM acceptance_criteria WHERE criterion_key = 'AC-401-A';

INSERT INTO requirement_test_results (
    criterion_id, test_run_key, passed, tester, details
)
SELECT criterion_id, 'RUN-401-B', TRUE, 'QA Lead',
       'Submission without a cost center was rejected.'
FROM acceptance_criteria WHERE criterion_key = 'AC-401-B';

-- This is an executable read model for document completeness and readiness.
CREATE VIEW document_readiness AS
SELECT
    d.document_id,
    d.product_name,
    d.version,
    d.status AS document_status,
    (SELECT COUNT(*) FROM problem_evidence e
     WHERE e.document_id = d.document_id) AS evidence_count,
    (SELECT COUNT(*) FROM product_goals g
     WHERE g.document_id = d.document_id) AS goal_count,
    (SELECT COUNT(*) FROM user_personas p
     WHERE p.document_id = d.document_id) AS persona_count,
    (SELECT COUNT(*) FROM scope_items s
     WHERE s.document_id = d.document_id AND s.included = TRUE) AS in_scope_count,
    (SELECT COUNT(*) FROM product_requirements r
     WHERE r.document_id = d.document_id) AS requirement_count,
    (SELECT COUNT(*) FROM release_criteria rc
     WHERE rc.document_id = d.document_id AND rc.required = TRUE) AS release_gate_count
FROM product_documents d;

-- A Must requirement is release-verified only when its latest result passes
-- for every criterion. A separate document-level gate still needs to inspect
-- security findings, business sign-off, and any operational release conditions.
SELECT
    r.requirement_key,
    r.title,
    r.priority,
    r.status,
    a.criterion_count,
    a.passed_criterion_count,
    a.failed_criterion_count,
    CASE
        WHEN a.criterion_count > 0
         AND a.passed_criterion_count = a.criterion_count
         AND a.failed_criterion_count = 0
        THEN TRUE
        ELSE FALSE
    END AS acceptance_tests_pass
FROM product_requirements r
JOIN requirement_acceptance_summary a
  ON a.requirement_id = r.requirement_id
ORDER BY r.requirement_key;

SELECT
    risk_key,
    description,
    probability,
    impact,
    probability * impact AS risk_score,
    CASE
        WHEN probability * impact >= 20 THEN 'Critical'::risk_severity
        WHEN probability * impact >= 12 THEN 'High'::risk_severity
        WHEN probability * impact >= 6 THEN 'Medium'::risk_severity
        ELSE 'Low'::risk_severity
    END AS severity,
    owner,
    mitigation
FROM requirement_risks
ORDER BY probability * impact DESC, risk_key;

SELECT * FROM document_readiness;

SELECT
    r.requirement_key,
    r.title,
    d.requirement_key AS dependency_key,
    rd.dependency_reason
FROM requirement_dependencies rd
JOIN product_requirements r ON r.requirement_id = rd.requirement_id
JOIN product_requirements d
  ON d.requirement_id = rd.depends_on_requirement_id
ORDER BY r.requirement_key;

-- The attempted invalid self-dependency below is intentionally represented as
-- a commented negative test. Uncomment it to observe the CHECK constraint.
-- INSERT INTO requirement_dependencies
--     (requirement_id, depends_on_requirement_id, dependency_reason)
-- SELECT requirement_id, requirement_id, 'Invalid self-dependency'
-- FROM product_requirements WHERE requirement_key = 'REQ-401';

-- The trigger also rejects a Verified transition when acceptance evidence is
-- incomplete or failing. This transaction verifies the first Must requirement.
UPDATE product_requirements
SET status = 'Approved'
WHERE requirement_key = 'REQ-401';

UPDATE product_requirements
SET status = 'Implemented'
WHERE requirement_key = 'REQ-401';

UPDATE product_requirements
SET status = 'Verified'
WHERE requirement_key = 'REQ-401';

INSERT INTO document_audit_log (
    document_id, requirement_id, actor, event_type, details
)
SELECT
    d.document_id,
    r.requirement_id,
    'QA Lead',
    'REQUIREMENT_VERIFIED',
    jsonb_build_object(
        'requirement_key', r.requirement_key,
        'verification_method', 'Latest passing result for every acceptance criterion'
    )
FROM product_documents d
JOIN product_requirements r ON r.document_id = d.document_id
WHERE d.product_name = 'Procurement Request Portal'
  AND r.requirement_key = 'REQ-401';

COMMIT;
