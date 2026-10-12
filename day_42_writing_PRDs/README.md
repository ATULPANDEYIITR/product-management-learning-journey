# Product Requirements Document Engineering and Governance

## Purpose and product context

A Product Requirements Document (PRD) defines the problem a product must solve, the users affected by that problem, the outcomes the organization expects, the work included in the proposed solution, and the conditions that establish whether the solution is acceptable.

A useful PRD is not simply a feature list. It connects evidence about a real problem to measurable goals, bounded scope, testable requirements, and explicit decisions about uncertainty. This repository models that process through a procurement request portal in which employees submit purchase requests, procurement teams route requests for approval, and authorized users inspect request status.

The example addresses a common operational problem: email-based purchasing workflows produce incomplete requests, require manual approval routing, and provide weak visibility into processing status. The proposed product introduces structured submission, policy-based routing, and request-level traceability.

The central relationship is:

**Problem evidence → Product goals → User needs → Scope decisions → Requirements → Acceptance criteria → Verification → Release decision**

Each stage constrains the next. A feature without a supported user need may be unnecessary. A requirement without acceptance criteria cannot be verified reliably. A measurable requirement that falls outside the agreed scope can introduce unauthorized work. A product with implemented features is not necessarily ready for release if mandatory acceptance or security conditions remain unmet.

## Problem definition and measurable goals

### Problem statements should describe a condition, not prescribe a solution

A useful problem statement identifies the current condition, the affected users, and the consequence. For the procurement portal, the problem is not simply that employees need a web form. The underlying problems are incomplete submissions, inconsistent routing, and limited status visibility.

The Python model records supporting evidence separately from the problem statement. This distinction matters because an observation from a discovery interview is evidence, while the interpretation of that observation is a product hypothesis. Recording the evidence makes the problem easier to challenge and revise as new information becomes available.

The SQL implementation stores evidence with its type, source reference, and observation date. This structure supports later investigation into whether a proposed solution remains justified.

### Goals describe observable outcomes

A goal should specify the outcome, the measure, and a target. The sample PRD defines submission completeness of at least 95%, approval-routing accuracy of at least 99%, and a reduction in manual status enquiries of 40% within three months of launch.

These values are illustrative targets, not measured product results. Their purpose is to demonstrate how a PRD turns broad intentions into measurable statements.

A target also needs an operational definition. For example, submission completeness must specify which fields are mandatory and whether the measurement includes rejected submissions. Routing accuracy needs an authoritative definition of the correct approval path. Without such definitions, two teams can report different results while using the same metric name.

The Java implementation stores goal descriptions as immutable document data, while the SQL schema separates goal names, metric names, baselines, targets, units, and measurement windows. The relational design makes the measurement structure explicit rather than treating the goal as an unstructured sentence.

## Users, needs, and scope boundaries

### User personas represent distinct responsibilities

The example uses three personas with different responsibilities.

- **Employee Requester:** Needs to submit a complete purchase request without learning internal procurement terminology. The main pain points are repeated requests for missing information and uncertainty about approval progress.
- **Procurement Approver:** Needs sufficient evidence, clear ownership, and a traceable decision process. The principal concern is whether a request can be evaluated against delegated financial authority.
- **Procurement Administrator:** Needs reliable policy maintenance, exception handling, and an audit trail. The administrator must distinguish a legitimate policy exception from a missing or contradictory configuration.

Personas are useful only when their needs influence product decisions. The request form addresses completeness, the approval workflow addresses delegated authority, and the status view addresses visibility. A persona that has no effect on requirements or scope is likely to be decorative rather than operationally useful.

The SQL model separates personas from their needs and pain points. This permits multiple needs and observations to be associated with a single persona without duplicating the persona record.

### Scope is a product decision

In-scope items describe work committed for the defined product boundary. Out-of-scope items explicitly identify work that the current product does not undertake.

The sample includes authenticated request submission, policy-based approval routing, status visibility, and request-level authorization. Supplier payment execution and contract negotiation remain outside the boundary.

This separation prevents an ambiguous requirement such as "support procurement end to end" from silently expanding into accounting, payment processing, supplier selection, and contract management.

A scope exclusion should identify the relevant boundary and, where necessary, the reason for it. Excluded functionality may belong to another system, require a separate policy decision, or exceed the current release objective.

## Requirements and traceability

### Requirements state what the product must do

A requirement includes a stable identifier, title, description, rationale, type, priority, owner, dependencies, and acceptance criteria.

The examples distinguish these requirement types:

| Type | Purpose in the procurement portal |
|---|---|
| Functional | Specifies behavior, such as submitting a request or routing it to an approver. |
| Non-functional | Defines measurable qualities, such as response-time or availability targets. |
| Business | Captures a business rule or outcome that supports procurement operations. |
| Technical | Defines a necessary technical constraint or integration behavior. |
| Compliance | Records a requirement arising from an applicable policy or regulatory obligation. |

The example implementation uses functional and technical requirements most directly. The type model also accommodates non-functional, business, and compliance requirements when a product team has sufficient detail to define them.

A requirement's rationale records why it exists. This makes later change analysis more reliable. If the rationale changes, the team can assess whether the requirement remains necessary.

### Priority is not implementation status

Priority expresses relative importance. Status expresses the current workflow state. A Must requirement can still be a Draft, and an implemented Should requirement does not become mandatory merely because work has started.

The examples use Must, Should, Could, and Won't to express prioritization. These labels do not replace a documented prioritization policy. The team must agree what each label means for the relevant release and who has authority to change it.

Stable requirement identifiers preserve traceability when titles or descriptions change. The dependency model makes sequencing explicit. Approval routing depends on a valid request record, so the routing requirement should not enter review until its dependency is approved.

The Python, C++, and Java implementations detect unknown dependencies and dependency cycles. The SQL schema uses foreign keys to prevent references to nonexistent requirements and a trigger to prevent a new dependency edge from creating a cycle.

Dependency validation matters because a set of individually understandable requirements can still describe an impossible delivery order. Cycle detection prevents circular prerequisites from silently entering the requirements model.

## Acceptance criteria and verification

Acceptance criteria define observable outcomes that determine whether a requirement has been satisfied. The implementations use a Given, When, Then structure to connect a precondition, an action, and an expected result.

For request validation, the positive case states that a complete submission receives a unique request identifier. The negative case states that a submission without a cost center is rejected with a field-specific error.

Both cases are necessary. Testing only the successful path does not establish whether the product handles invalid input safely.

Good acceptance criteria should be:

- **Observable:** A tester can determine whether the outcome occurred.
- **Specific:** The expected result does not depend on an unstated interpretation.
- **Relevant:** The test verifies the requirement rather than unrelated behavior.
- **Traceable:** The result can be associated with a stable requirement and criterion identifier.
- **Repeatable:** Another tester can execute the test under equivalent conditions and interpret the result consistently.

The examples distinguish requirement approval from acceptance verification. Review approval indicates that the requirement is sufficiently defined and accepted by authorized reviewers. Verification indicates that implemented behavior satisfies its acceptance criteria.

A requirement cannot legitimately become Verified just because its implementation has been marked complete. The Python model checks acceptance results before changing state. The C++ and Java models reject verification when criteria fail or the requirement is in the wrong state. The PostgreSQL trigger prevents a requirement from being marked Verified unless every criterion has a latest passing test result.

The SQL design retains individual test runs rather than storing only one mutable pass/fail field. That history makes it possible to inspect failed tests, subsequent fixes, and later verification results.

## Risk management and assumptions

A PRD contains uncertainty as well as requirements. Risks, assumptions, dependencies, and open questions should remain distinguishable.

- **Risk:** An uncertain event may affect delivery or product outcomes. An outdated approval matrix could route purchases incorrectly.
- **Assumption:** A condition is treated as true for planning purposes. The example assumes that employees have corporate accounts.
- **Dependency:** A capability or decision outside the immediate requirement must be available. Approval routing depends on authoritative cost-center data.
- **Open question:** A decision remains unresolved. The product team still needs to determine the retention period for supporting documents.

The Python, C++, Java, and SQL examples score risks using probability multiplied by impact, with each factor on a scale from one to five. A score of 20 or more is classified as Critical, while scores from 12 through 19 are classified as High.

This simple model helps order discussion, but it does not replace risk ownership or a mitigation plan. Two risks with the same score may have very different consequences. Each record therefore includes an owner and a mitigation or contingency.

For example, a missing approval policy should not cause automatic approval. The safer behavior is to hold the request for authorized resolution. That contingency converts a general risk statement into a concrete product behavior.

## Python implementation: structured PRD validation and export

The Python file builds a complete example PRD using dataclasses and enumerations. `PRD` aggregates personas, goals, requirements, risks, scope decisions, assumptions, dependencies, and release criteria.

Validation occurs at several levels. A persona needs a name, description, and user need. A requirement needs a valid identifier, rationale, owner, and acceptance criteria. A risk requires probability and impact values between one and five.

The document-level validator checks duplicate identifiers, unknown requirement dependencies, self-dependencies, and dependency cycles. Cycle detection uses depth-first traversal with separate visiting and visited sets. Encountering a node already on the active traversal path indicates a cycle.

`readiness_report()` distinguishes document validity from release readiness. A structurally valid PRD may still have Must requirements that are not approved, implemented, or verified.

The Markdown exporter produces a readable PRD with sections for problem evidence, goals, scope, personas, requirements, acceptance criteria, and a risk register. The JSON exporter preserves the nested data structure for use by other tools.

The built-in unit tests cover valid input, duplicate requirement identifiers, unknown dependencies, dependency cycles, risk scoring, and the relationship between Must approval and release readiness. The script uses only the Python standard library.

## JavaScript implementation: event-driven requirement workflow

The JavaScript file models a workflow rather than serving as a second document exporter. It emphasizes state transitions, reviewer decisions, acceptance-test results, and an audit journal.

`RequirementWorkflow` maintains requirements and their states in private class fields. The transition table prevents invalid state changes. For example, a Draft requirement cannot be marked Verified without passing through review, approval, and implementation.

The workflow uses an event journal to record requirement creation, review decisions, state changes, and acceptance-test execution. The journal assigns identifiers and timestamps when events are recorded, creating a consistent audit format.

Reviewers cannot approve their own requirements. The sample also requires two distinct approvals before a requirement enters the Approved state. A request for changes returns a requirement to Draft, while a rejection records a separate terminal review outcome that can be reopened through an explicit transition.

Acceptance-test verification requires a result for every declared criterion. Unknown criterion identifiers are rejected, and missing results do not count as successful tests. The implementation records the test attempt before reporting failed verification, preserving useful diagnostic history.

The workflow uses Node.js built-in modules only. An optional command-line argument exports the resulting snapshot as JSON.

## C++ case study: requirements governance engine

The C++ program presents a procurement governance engine with a separate requirement register, dependency graph, risk register, and audit log.

`RequirementsEngine` owns the requirement records in an unordered map, which provides average constant-time lookup by identifier. Each requirement stores its priority, workflow state, dependencies, and acceptance criteria.

The dependency-cycle detector uses depth-first search. Its time complexity is \(O(V + E)\), where \(V\) is the number of requirements and \(E\) is the number of dependency relationships. This is preferable to repeatedly enumerating dependency paths as a PRD grows.

The engine validates required fields before inserting a requirement and rejects duplicate IDs. It also checks dependencies before permitting a requirement to enter review. The transition function centralizes state rules so that callers cannot bypass the workflow by assigning an arbitrary state.

Risk analysis is a separate concern. The engine validates probability and impact values, calculates risk scores, and sorts the risk register by score. Requirement priority and risk severity remain separate because a high-priority feature is not necessarily a high operational risk.

The example intentionally fails verification for the approval-routing requirement. The expected failure demonstrates that implementation completion alone does not satisfy the release gate. The requirement remains unverified, and release readiness remains false.

The case study compiles with C++17 and uses standard-library containers and algorithms without external dependencies.

## Java implementation: enterprise domain model and approval policy

The Java program uses explicit domain classes for `ProductDocument`, `Requirement`, `AcceptanceCriterion`, `ReviewRecord`, `ApprovalPolicy`, and `Risk`. Enums constrain requirement types, priorities, workflow states, and reviewer decisions.

Collections are defensively copied when domain objects are created. This prevents callers from changing a requirement's dependency list or acceptance criteria by retaining a reference to the original mutable collection.

`ApprovalPolicy` defines the required approval quorum and the set of eligible reviewers. `ReviewService` checks reviewer eligibility, prevents self-approval, records review decisions, and moves requirements through permitted state transitions.

The approval count is based on distinct reviewers. A second approval is meaningful only when it comes from a different eligible person. The example therefore avoids treating repeated actions by one reviewer as independent approvals.

The service also checks dependency state before review and validates acceptance-test results against the exact set of criterion identifiers. Missing results and unexpected results are errors rather than implicit passes.

The Java model separates document validation from workflow decisions. A valid document may contain requirements that are not yet verified, and a requirement with an approval decision may still need implementation and acceptance testing.

The example uses Java 17 and standard library APIs. It does not require a database or third-party framework.

## SQL implementation: relational integrity and auditability

The PostgreSQL schema represents the PRD as related records rather than a single large document field.

`product_documents` stores product identity and version. `problem_evidence` and `product_goals` preserve the basis for product decisions. `user_personas`, `persona_needs`, and `persona_pain_points` model user research. `scope_items` records included and excluded work.

`product_requirements` stores each requirement's identifier, description, rationale, type, priority, owner, and status. `requirement_dependencies` links requirements to prerequisite requirements. `acceptance_criteria` stores independently identifiable test conditions and outcomes.

Review decisions, review comments, test results, risks, release criteria, and audit events have their own tables. This structure allows a query to answer specific questions, such as which requirements have failed acceptance tests or which risks have the highest scores.

### Database constraints

Primary keys establish record identity. Foreign keys prevent dependent records from referencing nonexistent parents. Unique constraints prevent duplicate requirement keys within a document, duplicate persona names within a document, and duplicate criterion keys within a requirement.

Check constraints enforce local rules such as non-empty descriptions, non-negative estimates, valid probability and impact ranges, and the prohibition on self-dependencies.

The recursive dependency trigger prevents a new dependency edge from creating a cycle. The review trigger requires an active reviewer and a requirement in review. The verification trigger rejects a transition to Verified when criteria are missing or their latest test results are not all passing.

These rules improve integrity even when more than one application accesses the database. Application validation remains important for useful error messages and policy orchestration, but database constraints protect stored records from invalid operations.

### Queries and operational reporting

The `current_requirement_reviews` view exposes current review decisions without deleting historical review records. The approval summary aggregates review decisions by requirement. The acceptance summary uses the latest test result for each criterion rather than treating an old passing run as proof that a later failing run does not exist.

Indexes support common access patterns, including document-level requirement prioritization, status-based reporting, reverse dependency lookup, current review retrieval, unresolved comments, and time-ordered audit inspection.

The sample transaction creates a procurement PRD, adds evidence and goals, defines personas and scope, inserts requirements and acceptance criteria, records a review and test results, and verifies one requirement. The transaction boundary keeps the demonstration's data changes together.

The SQL script is intended for PostgreSQL. It creates a dedicated schema and resets that schema before loading the demonstration data, so it should be executed only in a disposable learning database or an environment where resetting that schema is acceptable.

## Release readiness and decision authority

Release readiness is not the same as PRD completeness, requirement approval, or implementation progress.

A document can be structurally complete while a Must requirement remains unapproved. A requirement can be approved but not implemented. An implementation can exist while one acceptance criterion fails. A requirement can pass its acceptance tests while an independent security or operational release gate remains unresolved.

The example models these distinctions explicitly:

- Document validation checks whether the PRD has the information needed to be evaluated.
- Requirement review determines whether a requirement is sufficiently defined and accepted by the authorized reviewers.
- Acceptance verification checks whether implemented behavior meets the recorded criteria.
- Release readiness checks the applicable mandatory requirements and release conditions.

The code examples focus on the requirement-level gates and include illustrative release criteria for security and business acceptance. A production release service must also evaluate operational readiness, unresolved defects, data migration, monitoring, rollback capability, and any applicable compliance obligations. These conditions should be represented as explicit, owned gates rather than inferred from the existence of an approved PRD.

## Practical limitations and production considerations

The examples use compact approval policies, in-memory state, and illustrative risk scoring to make the governing mechanisms visible. They are not substitutes for an enterprise product-management platform.

A production implementation would need authenticated identities, role-based authorization, concurrency controls, durable event storage, controlled document revisions, retention policies, and access auditing. Approval quorum rules may vary by requirement type, business unit, financial exposure, or applicable regulation. The governing policy must define those variations explicitly.

The Python and JavaScript examples maintain state in memory unless an export is requested. The C++ and Java examples are likewise demonstrations rather than durable workflow services. The PostgreSQL schema provides persistent relational storage and integrity controls, but a production deployment would still require controlled migrations, least-privilege database roles, backups, monitoring, and a defined authorization model.

PRD changes should be traceable. Changing a requirement after approval may invalidate prior review decisions or acceptance evidence. A production system should record document revisions, identify the affected requirements, and determine which approvals and tests must be repeated.

The essential engineering distinction is that a PRD is a governed representation of product intent. Its quality depends not on document length, but on whether the problem is evidenced, goals are measurable, users and scope are clear, requirements are testable, risks have owners, and release decisions can be justified from recorded evidence.
