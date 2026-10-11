# Product Requirements Engineering: PRDs, Requirements Gathering, and Specification Quality

## Purpose and scope

Product requirements engineering converts business problems, user needs, operating constraints, and measurable product goals into a controlled specification that engineering, design, testing, security, and business teams can use.

The implementations in this repository model a supplier onboarding portal called ProcureFlow. Procurement teams currently collect supplier information through email and spreadsheets. Incomplete documents cause repeated follow-ups, compliance decisions are difficult to trace, and stakeholders have limited visibility into onboarding progress.

The example is deliberately grounded in this domain. Requirements cover application intake, document completeness, compliance decisions, response time, service availability, information security, and records retention.

Three related areas must remain distinct:

- **Product Requirements Documents (PRDs)** establish the product problem, target users, intended outcomes, release scope, assumptions, success metrics, and the relationship between business objectives and product behavior.
- **Requirements gathering** establishes what stakeholders need and why. It uses interviews, workshops, observed workflows, operational evidence, constraints, and validation to identify and resolve competing needs.
- **Functional and non-functional requirements** specify what the product must do and the quality levels or operational conditions under which it must do it.

A PRD organizes the product decision. Requirements gathering supplies evidence for that decision. Functional and non-functional requirements make the decision precise enough to implement and verify.

## The PRD as a product decision record

A PRD is more than a feature list. It explains the problem being solved, the people affected, the boundaries of the proposed solution, and the evidence that will establish whether the product succeeds.

For ProcureFlow, the problem statement identifies incomplete supplier submissions and repeated manual follow-ups. The target users include supplier representatives, procurement analysts, and compliance officers. The first release explicitly excludes automatic credit decisions, international tax filing, and contract negotiation.

These boundaries prevent a local solution to document collection from silently expanding into a much larger procurement platform.

### Product outcomes and success metrics

Product outcomes describe business improvements rather than implementation tasks.

| Product outcome | Example measure | Interpretation |
|---|---|---|
| Reduce onboarding delays | Median completion time of five business days or less | Measures the complete business process rather than a single page or API. |
| Improve submission quality | At least 95% complete on first submission | Measures whether document guidance prevents avoidable rework. |
| Improve responsiveness | 95th percentile read latency below 300 ms under a specified workload | Connects an operational quality requirement to a reproducible test. |
| Maintain service continuity | At least 99.9% monthly availability | Establishes an operational objective that requires monitoring and incident management. |

Each metric needs a definition, measurement window, data source, and accountable owner. A cycle-time metric must define its start and end events. Availability must define eligible service time and excluded maintenance. A latency target must specify the workload and percentile.

A target without a measurement method is an aspiration rather than an operationally testable requirement.

### Assumptions, constraints, and exclusions

Assumptions are conditions believed to hold but not necessarily verified. For example, the first release assumes suppliers can use a modern browser and that administrators maintain document checklists.

Constraints are binding conditions that restrict solution design. A seven-year compliance-record retention obligation may affect data architecture, auditability, deletion workflows, and storage cost.

Out-of-scope statements prevent stakeholders from treating adjacent capabilities as implied commitments. They should be explicit enough to guide roadmap and change-control decisions.

## Requirements gathering and evidence quality

Requirements gathering starts with stakeholder discovery, not immediate feature specification.

### Identify stakeholders and their interests

The example records stakeholder influence and interest separately. A compliance officer may have strong authority over retention and document-verification policies, while a supplier representative has direct experience with application usability.

Stakeholder mapping helps determine who must participate in discovery, who can approve policy decisions, and whose workflow must be observed. It does not mean that high influence automatically makes a stakeholder's preference more important than legal obligations or user evidence.

Typical discovery activities include:

- **Interviews:** establish individual goals, pain points, terminology, and decision rules.
- **Workflow observation:** reveal manual workarounds, duplicate data entry, handoffs, and hidden dependencies.
- **Document and policy analysis:** identify mandatory evidence, retention rules, approval boundaries, and contractual constraints.
- **Data analysis:** measure incomplete submissions, repeated requests, processing delays, and operational exceptions.
- **Cross-functional workshops:** expose conflicting interpretations and agree on terminology, boundaries, and decision ownership.

A useful discovery finding records the observed problem, supporting evidence, the stakeholder or source, and the desired outcome. The evidence should be retained so that later requirement changes can be evaluated against the original problem.

### From a finding to a requirement

Consider the finding that supplier applications frequently omit tax documents.

A weak requirement says that the portal should make onboarding easier. It provides no implementation boundary or verification method.

A stronger functional requirement states that the portal evaluates a supplier's documents against the published checklist for the supplier's category and blocks final submission when mandatory documents are missing.

The stronger version identifies the trigger, relevant policy, expected behavior, and observable result. It can be discussed with stakeholders and tested by engineering.

### Resolve ambiguity before approval

Words such as *fast*, *secure*, *simple*, *intuitive*, and *reliable* can describe stakeholder intent, but they are not sufficient specifications by themselves.

For each ambiguous statement, determine:

- The actor, event, or operating condition to which it applies.
- The expected behavior or quality attribute.
- The relevant boundary conditions and exceptions.
- The evidence required to verify the result.
- The person authorized to resolve disagreements.

Conflicting requirements should be documented as conflicts, not silently combined into vague language. For example, an immediate deletion preference may conflict with a binding retention policy. The product team must establish the applicable authority, scope, and lawful handling rules before implementation.

## Functional requirements

A functional requirement defines behavior the product must provide. It describes a capability, rule, response, or state change in the domain.

### Supplier application intake

`REQ-FR-001` requires authenticated supplier representatives to create a draft application containing legal identity, registration country, tax identifier, and contact details.

Its acceptance criteria distinguish successful submission from duplicate submission. A valid request creates a draft and returns a reference. A duplicate tax identifier is rejected without disclosing another supplier's private information.

This requirement connects multiple implementation concerns:

- Identity and authorization determine whether the actor may create an application.
- Input validation ensures required values are present and valid.
- Duplicate detection protects data integrity.
- The response contract gives the user a stable reference.
- Authorization-aware error handling prevents cross-supplier information disclosure.

The requirement describes externally observable product behavior without unnecessarily prescribing the database schema or framework.

### Document completeness

`REQ-FR-002` requires document validation against the checklist published for a supplier category.

The rule implies that checklist versions, category changes, required-document status, and submission attempts must have defined behavior. A supplier should receive an actionable list of missing documents rather than an unexplained rejection.

The dependency on application intake is explicit: document validation cannot operate on an application that does not exist. Dependency relationships help engineering order work and expose architectural prerequisites.

### Compliance decisions

A compliance decision is more than a status label. It requires an authorized reviewer, a decision outcome, a timestamp, and a reason when rejecting an application.

The requirement also implies an audit history. Replacing the previous decision without preserving the event would weaken accountability. The exact retention and immutability rules should be defined by the applicable policy rather than inferred from the user interface.

### Acceptance criteria

Acceptance criteria translate a requirement into conditions that can be demonstrated. The Given/When/Then structure identifies the context, triggering action, and expected outcome.

A good criterion is observable, bounded, and repeatable. It avoids implementation assumptions unless those assumptions are part of the product contract.

Functional acceptance criteria should address normal behavior and relevant exceptions, including invalid inputs, duplicate submissions, missing documents, unauthorized actors, repeated requests, and partial failures.

The Python, JavaScript, and Java programs validate that functional requirements have acceptance criteria. The PostgreSQL script uses a deferred constraint trigger so that a functional requirement and its criteria can be inserted within the same transaction, while a committed functional requirement without criteria is rejected.

## Non-functional requirements

A non-functional requirement defines a quality attribute, operating limit, or system-wide condition. It affects how the product behaves across many functional paths.

Non-functional requirements should be measurable wherever practical. They frequently influence architecture, testing strategy, hosting cost, monitoring, and operational procedures.

### Performance

`REQ-NFR-001` specifies a 95th percentile read latency below 300 milliseconds with 500 concurrent users.

The percentile matters. Average latency can conceal a poor experience for a substantial minority of users. A valid performance test must also define the request mix, test duration, dataset size, cache conditions, environment, and error-rate limits.

The requirement does not mean every request must complete within 300 milliseconds. A separate maximum-latency or timeout requirement would be necessary if that guarantee were intended.

### Availability

`REQ-NFR-002` specifies monthly availability of at least 99.9%, subject to an explicitly defined maintenance policy.

Availability is an operational property, not merely a deployment setting. It depends on health monitoring, dependency reliability, recovery procedures, incident response, and the accuracy of the measurement method.

The specification must clarify which endpoints count as available, how partial failures are measured, and which maintenance periods are excluded. Otherwise, teams can report different results from the same service.

### Security and privacy

Supplier information may contain registration and tax details. Requirements must establish authenticated access, authorization boundaries, protected transport, and isolation between suppliers.

Security requirements need negative tests as well as successful-path tests. An authenticated supplier must not be able to retrieve another supplier's documents by changing a record identifier. Compliance personnel may need access to records that suppliers cannot view, while administrators should receive only the permissions necessary for their duties.

Encryption alone does not establish a secure product. Identity lifecycle, authorization, auditability, secrets handling, retention, backup access, and incident response may all require separate requirements.

### Reliability and operational quality

Availability, reliability, recoverability, performance, and observability are related but different qualities.

A system can be fast when operating but unavailable during a dependency outage. It can meet its availability objective while losing recent data after recovery. It can recover successfully without generating sufficient diagnostic information to identify the failure.

Quality requirements should therefore be decomposed into independently testable targets where the risk warrants it.

## Requirement classification and prioritization

The implementations distinguish functional, non-functional, business, and constraint requirements.

| Type | Purpose | ProcureFlow example |
|---|---|---|
| Functional | Defines product behavior | Create supplier applications and validate required documents. |
| Non-functional | Defines measurable quality or operating conditions | Meet a specified latency and availability objective. |
| Business | Defines an intended organizational outcome | Reduce median onboarding completion time. |
| Constraint | Records a binding limitation or obligation | Retain compliance decision evidence for seven years. |

These categories serve different decision needs. A business outcome explains why a capability matters. A functional requirement defines the behavior used to support that outcome. A non-functional requirement establishes the quality conditions under which that behavior must operate. A constraint limits acceptable solutions.

### MoSCoW prioritization

The implementations use `MUST`, `SHOULD`, `COULD`, and `WONT` classifications.

- **Must:** required for the defined release or binding compliance baseline.
- **Should:** important, but an explicitly agreed and justified exception may be possible.
- **Could:** useful when capacity remains and higher-priority work is protected.
- **Wont:** excluded from the current scope, without implying that the capability can never be considered.

Priority labels need documented decision authority. A mandatory security obligation should not become optional merely because a discretionary feature has a higher numerical score.

### RICE for optional capabilities

The Python, JavaScript, and Java implementations include a RICE calculation:

`RICE = Reach × Impact × Confidence / Effort`

Reach estimates the number of affected users or instances over a defined period. Impact estimates the benefit per affected user or instance. Confidence represents confidence in those estimates. Effort measures delivery work in consistent units.

The calculation is useful for comparing optional candidates, such as document-expiry reminders and dashboard exports. It is not an objective truth: its result depends on assumptions, estimation quality, and the definition of impact.

The examples validate non-negative reach and impact, confidence between zero and one, and strictly positive effort. Mandatory policy obligations are evaluated separately rather than traded against optional-feature scores.

## PRD review, baseline management, and change control

A PRD changes as evidence improves. Controlled revision is necessary because changes to requirements can alter design decisions, estimates, acceptance tests, release commitments, and compliance exposure.

The JavaScript and Java implementations model requirement states such as draft, in review, approved, implemented, verified, and rejected. Invalid transitions are rejected rather than silently accepted.

For example, an implemented requirement cannot jump directly back to draft. A defect or changed policy affecting an approved requirement should pass through a controlled review or change process.

The Python and JavaScript programs record change requests independently from the original requirement. The example change to add expiry reminders is deferred pending capacity and notification-policy review. Deferral does not rewrite the baseline or pretend that the feature has been implemented.

A sound change decision records the requester, affected requirement, requested behavior, estimated effort, expected impact, decision maker, rationale, and outcome. Approved changes should update the relevant specification version and preserve traceability to the prior baseline.

## Traceability and verification

Traceability connects a product requirement to its origin and delivery evidence.

A useful chain is:

`Stakeholder evidence → PRD requirement → Acceptance criteria → Delivery item → Verification evidence → Product outcome`

Each link answers a different question. Stakeholder evidence explains why the requirement exists. Acceptance criteria define observable behavior. Delivery items show where work is planned or implemented. Verification evidence demonstrates whether the requirement is satisfied. Product metrics establish whether the delivered capability achieves the intended business outcome.

Traceability is not complete merely because a requirement has an identifier. A requirement without an evidence source may be based on an untested assumption. A functional requirement without acceptance criteria is difficult to verify consistently. A requirement without delivery links may have no accountable implementation path.

### Dependency management

The Python implementation detects missing dependencies and cycles using graph traversal. The JavaScript implementation uses Kahn's topological-sorting algorithm to calculate a possible implementation order.

If requirement B depends on requirement A, A must be available before B can be completed. If A depends on B and B depends on A, the dependency graph contains a cycle. Such a cycle may indicate incorrectly decomposed requirements or a missing architectural boundary.

The PostgreSQL schema represents dependencies through a self-referencing junction table. Foreign keys prevent references to nonexistent requirements, and a check constraint prevents direct self-dependency. General multi-record dependency cycles require graph validation beyond an ordinary foreign key or check constraint.

### Release readiness

The examples evaluate mandatory requirements against verification status and traceability conditions.

A readiness assessment identifies unverified mandatory requirements, missing delivery links, incomplete acceptance criteria, invalid dependencies, and unresolved specification gaps.

The assessment is deliberately conservative. A production release gate may also require test evidence, operational sign-off, security approval, migration validation, rollback readiness, and policy-specific authorization. The exact gate must be defined for the product rather than assumed to be identical across organizations.

## Python implementation

The Python script implements a complete, executable requirements workflow using the standard library.

### Domain representation

`Requirement` stores the identifier, title, description, category, priority, owner, source, state, acceptance criteria, dependencies, delivery links, risk, and verification details. Enums constrain categories and states to recognized values.

`AcceptanceCriterion` validates the Given/When/Then fields. Functional requirements require at least one criterion, while non-functional requirements require a measurable target. These rules reject incomplete specifications before they enter the PRD collection.

### PRD operations

`ProductRequirementsDocument` maintains requirements, stakeholders, change requests, product outcomes, assumptions, and scope exclusions. Duplicate requirement identifiers are rejected.

Its dependency checks distinguish missing references from circular dependencies. Traceability analysis identifies absent evidence, ownership, acceptance criteria, measurable targets, and delivery links. The release assessment checks mandatory requirement status and specification integrity.

`export_json` serializes the document and writes through a temporary file before replacing the destination. This avoids exposing a partially written JSON file to readers during a normal successful write. It is not a complete multi-process locking or crash-durability protocol.

### Discovery, prioritization, and tests

`collect_requirements` normalizes interview findings and rejects records that lack a problem, evidence, or desired outcome. `rice_score` validates inputs before computing a score. `detect_conflicting_requirements` demonstrates a deliberately narrow, explicit tag-based conflict check; it does not claim to infer every semantic contradiction in natural language.

The `unittest` cases exercise duplicate identifiers, missing dependencies, cycles, incomplete acceptance criteria, missing non-functional targets, and invalid prioritization inputs.

Run the script with Python 3.10 or later:

`python product_requirements.py`

The program writes `procureflow_prd.json`, prints traceability and readiness diagnostics, and runs its validation tests.

## JavaScript implementation

The JavaScript program emphasizes event-driven requirements management and controlled state changes.

### Encapsulated workspace

`RequirementsWorkspace` uses private class fields to protect the internal maps of requirements, stakeholders, and change requests. Consumers retrieve validated objects through methods instead of modifying the workspace's internal collections directly.

`Requirement` validates its identity, category, priority, and acceptance criteria. It records a version and rejects direct revisions after approval. Changes to an approved baseline must use a controlled change request.

### State transitions and events

The explicit transition map prevents invalid workflow operations. For example, verification is not permitted directly from the review state.

`EventEmitter` publishes events when requirements are created and changes are requested or decided. These events can support downstream integrations such as notifications, audit logging, analytics, and delivery tracking without embedding those concerns into the core requirement object.

Event emission in this example is synchronous. Production listeners should avoid long-running work in the event handler and should use durable messaging or a transactional outbox when delivery guarantees are required.

### Dependency ordering and export

The dependency-ordering method uses Kahn's algorithm. It first calculates the number of unresolved prerequisites for each requirement, then releases dependent requirements as prerequisites become available. If the number of emitted nodes is smaller than the requirement count, a cycle exists.

The change request is created with a unique identifier, validated effort estimate, impact description, and pending state. The decision method requires a named decision maker and a reason, and it prevents a second decision on an already decided request.

Run the file with Node.js 18 or later:

`node product_requirements.js`

The program writes `procureflow_requirements.json`. The example uses a local file for demonstration; a production workspace would also need authentication, persistent storage, access control, and a durable audit trail.

## C++ case study

The C++ program models requirements for a procurement portal where specification quality must be evaluated alongside implementation traceability.

Its architecture separates `Requirement`, `AcceptanceCriterion`, `Review`, `PullRequest`, `BranchProtection`, and `RepositoryGovernance`. These types represent distinct responsibilities rather than one oversized structure.

The requirement object validates mandatory identity, ownership, source, acceptance criteria, and non-functional targets. The governance service maintains requirements and evaluates whether proposed implementation changes satisfy configured repository conditions.

Although the central scenario concerns product requirements, repository governance is included only as a delivery control that can protect requirement-linked changes. A PRD defines expected product behavior; a pull request proposes code changes; repository rules determine whether those changes may enter a protected branch. These artifacts must not be treated as interchangeable.

### Merge-eligibility evaluation

The case study checks whether a proposed change is open, non-draft, conflict-free, synchronized with the base branch, associated with commits, supported by required successful checks, and approved by enough eligible reviewers.

A source-branch update increments the modeled head version. When stale approvals must be dismissed, approvals associated with the earlier changeset no longer satisfy the gate. Fresh reviews are required before merging.

The example uses a protected `main` branch with two required approvals, unit tests, a security scan, conversation resolution, and linear-history enforcement. A squash merge is permitted while a merge commit is rejected by the linear-history policy.

These are separate delivery conditions. Acceptance criteria determine whether the implemented behavior meets the specification; repository checks and review rules determine whether the changeset satisfies the configured integration policy.

The program compiles with C++17 or later:

`g++ -std=c++17 -Wall -Wextra -pedantic requirements_governance.cpp -o requirements_governance`

Run it with `./requirements_governance` or the equivalent executable name on the operating system.

The model is an educational governance engine, not a complete implementation of a hosting provider's permission system. Production integrations would need authoritative identities, protected-branch configuration retrieval, durable review history, and race-safe merge operations.

## Java implementation

The Java program provides an enterprise-oriented domain model using records, enums, collections, explicit state transitions, and a service boundary.

### Domain model and immutability

`Stakeholder`, `AcceptanceCriterion`, `ReviewRecord`, `ChangeRequest`, and `ReleaseAssessment` are records. Their compact constructors validate incoming values, and collection-bearing records defensively copy their collections.

`Requirement` is a controlled mutable aggregate. It owns acceptance criteria, dependencies, delivery links, review history, a state, and a version. Methods enforce which modifications are allowed in draft or in-review states.

This separation makes the domain rules visible and limits accidental mutation. It also makes it easier to test the requirement lifecycle without running a web server or database.

### Review decisions

`RequirementsService` records reviews against a requirement in the in-review state. An approval transitions the requirement to approved, while a request for changes returns it to draft. Each review stores the reviewer, decision, rationale, timestamp, and requirement version.

Versioned reviews preserve the context in which a decision was made. If a requirement changes, an earlier decision may no longer establish that the current version has been accepted. A production policy must define whether and when those decisions become stale.

The sample treats registered stakeholders as eligible requirement reviewers. Real enterprises generally need a separate authorization policy, because being a stakeholder does not automatically confer authority to approve security, compliance, architecture, or commercial decisions.

### Release assessment

The service detects nonexistent dependency references and circular dependencies, then evaluates mandatory requirement verification and traceability.

The result is a structured `ReleaseAssessment` rather than a single unexplained boolean. It carries the specific unverified requirements, traceability gaps, and dependency errors that prevent readiness.

Run with Java 17 or later:

`java ProductRequirementsApp.java`

The example uses only standard Java APIs. Persistent storage, authentication, concurrent updates, and organization-specific approval policies are outside the in-memory model.

## PostgreSQL data model

The SQL implementation provides a relational model for maintaining product specifications and their evidence.

### Core relationships

The schema represents these relationships:

- `products` contains the product problem statement, target users, assumptions, and exclusions.
- `stakeholders` records people involved in discovery and specification decisions. `stakeholder_goals` captures their individual goals.
- `discovery_findings` links observed problems and evidence to a product and stakeholder.
- `prds` stores versioned documents associated with a product.
- `requirements` belongs to a PRD version and references an accountable owner and, where available, a discovery finding.
- `acceptance_criteria` stores testable Given/When/Then conditions for requirements.
- `requirement_dependencies` records prerequisite relationships.
- `delivery_items` and `requirement_delivery_links` connect requirements to implementation work and verification artifacts.
- `requirement_reviews` records version-specific specification decisions.
- `requirement_changes` records requested scope changes and their decisions.
- `success_metrics` stores measurable product outcomes.

The model uses foreign keys to preserve referential integrity and uniqueness constraints to prevent duplicate product keys, PRD versions, requirement keys within a PRD, criterion keys within a requirement, and duplicate dependency links.

### Database-level validation

Check constraints enforce positive effort, valid influence and interest ranges, non-empty text, valid enumerated values, and required metric targets for non-functional requirements.

The `assert_functional_criteria` function and its deferred constraint triggers enforce the relationship between functional requirements and acceptance criteria at transaction completion. Deferral allows a requirement and its criteria to be inserted in one transaction without requiring an intermediate incomplete state to be valid at every statement boundary.

The database also prevents a requirement from directly depending on itself. Foreign keys ensure that both ends of a dependency exist. Longer cycles require additional graph validation.

### Indexes and operational queries

Indexes support common access patterns: filtering requirements by PRD, priority, and status; retrieving an owner's workload; locating recent discovery findings; finding dependents of a prerequisite; and inspecting reviews or pending change requests.

`requirement_traceability` aggregates acceptance criteria, delivery links, and review counts. `requirement_quality_gaps` identifies incomplete specification records. `release_readiness` counts mandatory requirements and identifies those not verified. `discovery_coverage` measures the proportion of requirements linked to discovery evidence.

These views provide useful operational diagnostics, but they are not a complete release authorization mechanism. In particular, an aggregate readiness view cannot prove that test evidence is valid or that a policy owner has granted a required external sign-off.

The change-decision example runs inside a transaction and updates the change state, decision maker, rationale, and timestamp together. A production application should additionally restrict who may make each transition and should preserve an append-only audit record when policy requires one.

Execute the SQL file against a PostgreSQL database with permission to create the `product_requirements` schema and its objects. The script creates sample records and then queries the resulting traceability, quality, dependency, prioritization, and release data.

## Cross-cutting engineering considerations

### Requirement quality

A high-quality requirement has a clear source, a named owner, a specific statement, a defensible priority, relevant acceptance criteria, and an appropriate verification method.

Functional requirements need observable behavior. Non-functional requirements need measurable quality targets and defined operating conditions. Business requirements need a meaningful outcome measure. Constraints need an authoritative source and clear applicability.

These criteria reduce disagreement during design, implementation, testing, and acceptance.

### Security and privacy

Requirements records may themselves contain commercially sensitive information, personal data, security findings, or compliance obligations.

A production requirements platform should enforce role-based access, validate permissions on every write, protect stored data and transport, minimize unnecessary sensitive content, and audit approval and change operations. Export files must inherit the access controls and retention rules appropriate to the data they contain.

Input validation is not authorization. A valid requirement identifier or stakeholder name does not establish that the current actor may approve the record.

### Concurrency and version integrity

The examples are local simulations. They do not implement multi-user locking or transactional persistence for every operation.

A collaborative production system must handle two reviewers or editors acting on the same requirement concurrently. Optimistic concurrency control can reject a revision when its expected version no longer matches the stored version. Database transactions can ensure that a baseline update and its audit event commit together. Idempotency keys can prevent retried API requests from creating duplicate change requests.

Review decisions should be associated with the version they evaluated. Otherwise, an approval for an earlier specification can be incorrectly reused after a material change.

### Verification and debugging

A failed readiness check should identify the affected requirement and the exact missing evidence rather than report only that the release is not ready.

Useful diagnostics include missing acceptance criteria, absent measurable targets, unresolved dependencies, missing delivery links, unverified mandatory requirements, invalid state transitions, and incomplete change decisions.

Validation should occur at multiple layers. Domain code provides actionable feedback, service-layer authorization enforces organizational policy, and database constraints protect integrity even when records are written by another client.

### Performance and scale

In-memory maps and sets provide efficient identifier lookups for these small examples. Their behavior does not address persistence, cross-process coordination, or large-scale queries.

The relational model uses targeted indexes for known access patterns. Indexes improve reads at the cost of storage and write overhead, so production indexing should follow observed query plans and workload measurements.

For a large requirements repository, dependency traversal and cycle detection should be bounded and monitored. Incremental validation can reduce repeated work, but it must still detect changes that introduce cycles or invalidate downstream requirements.

## Practical acceptance standard

A product specification is ready for implementation when the relevant stakeholders agree on the problem and boundaries, the requirements have accountable owners and evidence, functional behavior has testable acceptance criteria, non-functional requirements have measurable targets, constraints have authoritative sources, dependencies are understood, and the change process is explicit.

A release is ready only when its mandatory requirements have satisfied the defined verification conditions and the required operational, security, and governance checks have passed. Specification completeness and product delivery are connected, but they are not the same milestone.
