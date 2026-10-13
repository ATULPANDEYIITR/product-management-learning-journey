# User Stories: Product Requirements, Acceptance Criteria, and INVEST

## Purpose and scope

A user story is a concise description of a product capability from the perspective of a person who needs an outcome. It connects a user need to a reason for delivering that need. It is not a complete specification, a technical task, or a substitute for testing.

This repository models user stories as structured product requirements. The five implementations cover different aspects of story creation, refinement, validation, dependency management, and delivery readiness.

The central example is a retail or banking transaction workflow. Customers need to perform transactions safely, while support and compliance personnel need specific diagnostic or audit capabilities. Each story describes an outcome for a defined persona rather than prescribing the entire technical implementation.

## Anatomy of a user story

The conventional format is:

**As a [persona], I want [capability], so that [value].**

Each clause has a distinct purpose.

| Element | Meaning | Example |
|---|---|---|
| Persona | The person or role experiencing the need | A registered banking customer |
| Need | The capability or outcome required | Confirm a transfer after reviewing the amount |
| Value | The benefit that explains why the capability matters | Receive a traceable confirmation without duplicate transfers |

The persona is more than a job title. Its context, goals, and constraints help the team understand how the requirement will be used. A customer using a mobile application under unreliable network conditions may need safe retry behavior. A compliance analyst needs authorized access to transaction evidence. These users interact with the same product, but their goals and acceptance conditions differ.

The need should describe the required capability without unnecessarily prescribing its implementation. The value should identify a meaningful result, not repeat the need in different words.

For example, "I want a transfer button so that I can click the transfer button" does not establish meaningful value. "I want to confirm a transfer after reviewing the recipient and amount so that I can send money with a traceable confirmation" connects the interaction to an outcome.

The story statement is a communication device. Its quality depends on the supporting discussion, constraints, acceptance criteria, and decisions recorded during refinement.

## Personas and product context

A persona represents a meaningful user group with recognizable goals and constraints. It should be specific enough to guide product decisions without creating unnecessary character detail.

The implementations distinguish between a retail customer and a support specialist or compliance analyst.

A customer-facing story concerns a direct product outcome, such as confirming an order or transfer. A support-facing story concerns diagnosing a failed transaction. An audit-facing story concerns retrieving authorized evidence of a completed operation.

These stories should not share acceptance criteria merely because they relate to the same underlying transaction. A successful customer confirmation does not prove that support diagnostics are authorized, and an accessible audit record does not prove that the customer was protected against duplicate submissions.

Persona information must not be used as an informal replacement for authorization rules. In a production system, identity, permissions, and access to sensitive records must be verified by the application and its security controls.

## User value and scope

A user story should explain why the capability deserves implementation. Value can include reduced user effort, fewer errors, improved reliability, better accessibility, faster resolution, or stronger operational control.

Value should be considered alongside delivery cost, risk, dependencies, and strategic priorities. A high-value story is not automatically ready for development, and a small story is not automatically more important than a larger one.

Scope determines what the story promises. A story about submitting a transfer should not silently include transfer initiation, audit exports, reporting dashboards, and every possible payment failure. Combining unrelated outcomes makes estimation less reliable and acceptance testing harder.

When a story becomes too broad, split it around meaningful outcomes, workflow steps, business rules, or user groups. The resulting stories should each provide understandable value and have their own acceptance criteria.

## Acceptance criteria

Acceptance criteria define the observable conditions under which a story can be considered acceptable. They turn a broad user need into verifiable product behavior.

The implementations use the Given-When-Then structure:

- **Given** describes the relevant starting context.
- **When** describes the user action or triggering event.
- **Then** describes the observable expected outcome.

For a transaction workflow, a successful submission might require exactly one transaction record and a confirmation reference. A retry after a network timeout might require returning the original transaction instead of creating another one.

These are separate behaviors. A test that verifies a confirmation screen does not necessarily verify idempotency, and a test that verifies idempotency does not necessarily verify access control.

Acceptance criteria should describe observable outcomes, avoid contradictory conditions, and address relevant boundary and failure cases. A criterion such as "the application works correctly" cannot be tested reliably because it does not define the expected behavior.

### Functional and non-functional conditions

Functional criteria describe what the product must do. Validation criteria describe how invalid inputs are handled. Security criteria specify behavior such as authorization enforcement or protection against duplicate operations. Performance criteria define measurable response expectations when these matter to the requirement. Accessibility criteria cover observable interactions required for users with different access needs.

These categories may overlap within one story, but each criterion should identify a distinct condition. Sensitive workflows frequently need multiple criteria because functional success alone is insufficient.

### Acceptance criteria and automated tests

An acceptance criterion describes a required outcome. An automated test is one way to verify that outcome.

The Python and Java implementations represent criteria as structured objects. The JavaScript implementation evaluates a criterion against observed results. The SQL implementation records execution outcomes and allows queries to identify criteria whose latest recorded execution has not passed.

An automated test passing does not guarantee that every acceptance condition has been verified. Test coverage must be considered at the criterion level, including scenarios for invalid inputs, missing permissions, retries, and failure recovery.

## INVEST: assessing story quality

INVEST is a story-quality checklist:

| Attribute | Meaning | Practical question |
|---|---|---|
| Independent | The story can be delivered with limited dependence on other stories | Can the team complete it without waiting for another backlog item? |
| Negotiable | The story leaves room for discussion about implementation | Does it describe the outcome without unnecessarily fixing the design? |
| Valuable | The story provides a meaningful user or business benefit | Who benefits, and how? |
| Estimable | The team understands enough to estimate the work | Are the scope, constraints, and acceptance conditions sufficiently clear? |
| Small | The story fits a manageable delivery window | Can the team deliver and verify it without excessive coordination? |
| Testable | Its completion can be verified | Is there observable evidence of acceptance? |

INVEST is a refinement aid rather than a universal numerical scoring system. A story can have a clear user value but still be difficult to estimate. It can be testable yet too large for one delivery window. The attributes expose different weaknesses and should not be collapsed into a single vague quality judgment.

Independence does not mean that the product has no technical dependencies. It means that the story is shaped to minimize avoidable coupling between backlog items. Some dependencies are unavoidable and should be recorded explicitly.

Negotiability does not mean that legal, regulatory, security, or business constraints can be ignored. Those constraints must remain explicit even when implementation choices are open to discussion.

Valuable stories explain their intended outcome. Estimable stories provide enough context for a reasoned forecast. Small stories limit uncertainty and coordination. Testable stories specify evidence that distinguishes success from failure.

## Story refinement and lifecycle

Story refinement is the process of clarifying scope, reviewing value, examining dependencies, improving acceptance criteria, and assessing whether the team understands the work.

The implementations use a state model containing draft, refinement, ready, in-progress, done, and blocked states. A state transition represents a decision about the story's workflow, not proof that the delivered software is correct.

A draft story may enter refinement when the product owner and delivery team discuss its intended outcome. The team can return the story for changes if its criteria are ambiguous, its size is excessive, or its dependencies are unclear. A story should become ready only when the applicable quality requirements have been satisfied.

An in-progress story may return to refinement if implementation reveals an important unresolved requirement. A blocked story may resume refinement after the blocking issue is addressed. A completed story should not transition arbitrarily back into an earlier state; reopening completed work should follow an explicit team policy.

The Python implementation focuses on structured story data, validation, and dependency ordering. The JavaScript implementation uses event-driven processing and asynchronous refinement decisions. The C++ program models a governance engine with controlled state transitions. The Java program uses explicit domain types and a refinement decision model. The SQL script enforces state-transition rules within the database.

## Python implementation

The Python program defines `Persona`, `AcceptanceCriterion`, and `UserStory` as structured domain objects.

`UserStory.statement()` constructs the conventional user story sentence from the persona role, need, and value. `validate()` checks required information, identifier format, acceptance criteria, points, priority, and self-dependencies. `invest_scores()` exposes the six INVEST attributes separately so that a team can identify the exact dimension that needs attention.

`dependency_order()` performs a topological sort. It verifies that referenced dependencies exist and reports cycles rather than returning an invalid sequence. The ordering is useful when a team must understand which backlog items need to be completed before dependent items can be delivered.

`split_story()` validates a proposed group of child stories. It checks that the split contains enough distinct identifiers and that the proposed children are structurally valid. A production story-splitting process should also establish that the children represent meaningful outcomes and do not duplicate the same work.

`backlog_report()` provides a prioritized quality report without confusing priority with readiness. A story with high priority can still have missing acceptance criteria or an invalid dependency.

The script uses only the Python standard library. It is an executable domain model rather than a connection to a live product-management platform.

## JavaScript implementation

The JavaScript program emphasizes asynchronous refinement, event-driven behavior, and audit records.

`StoryBacklog` extends Node.js `EventEmitter` so that creation, readiness, and refinement outcomes can be observed by other parts of a system. This approach allows notifications, metrics, or downstream workflow handlers to respond to changes without embedding every behavior inside the story object.

The `refine()` method awaits a reviewer function. A reviewer can perform asynchronous checks, such as verifying required documentation or obtaining a product-owner decision. A rejected decision returns the story for further work rather than marking it ready.

Each event contains a unique identifier, story revision, timestamp, event type, and details. These records provide an audit trail for the in-memory example. They are not a durable audit log because process termination loses the records.

The `matchesCriterion()` function compares the expected outcome with observed test information. This makes the difference between an acceptance condition and a successful verification explicit.

The implementation also checks dependency references and cycles. Its story collection uses a `Map`, while individual dependency relationships use a `Set`. The event model is appropriate for applications that need to react to backlog changes, although production systems would also require persistence, authorization, event-delivery guarantees, and concurrency control.

## C++ case study: sprint readiness governance

The C++ program models a product team that manages retail checkout capabilities.

The `UserStory` structure combines the story statement, persona, acceptance criteria, INVEST assessment, priority, points, dependencies, and workflow state. `StoryGovernanceEngine` centralizes registration, transition validation, dependency ordering, and sprint eligibility.

The engine rejects duplicate identifiers and structurally invalid stories. Its transition rules prevent unsupported changes between states. Readiness checks also verify that INVEST has passed and that dependencies are complete.

Dependency ordering uses depth-first traversal. A visiting set detects cycles in the current traversal, while a visited set avoids repeating work for already processed stories. For a graph with \(V\) stories and \(E\) dependency relationships, traversal is \(O(V+E)\) under normal hash-based or ordered-set assumptions appropriate to the chosen containers.

The case study distinguishes three decisions:

- A story may be important because its priority is high.
- A story may be well refined because its acceptance criteria and INVEST assessment are satisfactory.
- A story may be eligible for a sprint only when its state and dependencies meet the modeled policy.

These decisions should not be conflated. A high-priority story with an unresolved dependency is not necessarily ready for implementation.

The example uses deterministic ordering for backlog reporting and explicit exceptions for invalid transitions. A production implementation would require stronger identifier validation, persistent history, controlled access to state mutation, and integration with the team's actual delivery process.

## Java implementation: enterprise domain modeling

The Java program represents a banking product with immutable records for personas, acceptance criteria, and refinement decisions.

`Persona` validates its required fields when constructed. `AcceptanceCriterion` records its Given-When-Then conditions and category. `UserStory` owns its state, quality assessment, dependencies, revision, and audit history.

The use of enums for states and INVEST dimensions avoids representing controlled domain values as arbitrary strings. `EnumMap` provides a direct mapping between each INVEST dimension and its result. Collections exposed by the model are copied or wrapped to prevent callers from modifying internal state accidentally.

The `Backlog` class handles identifier uniqueness and dependency traversal. The `transition()` method checks the allowed state graph and verifies that dependencies are complete before accepting the ready state.

`RefinementResult` captures the review decision, reviewer, and findings. A request for changes returns a story from refinement to draft. The model keeps refinement decisions separate from acceptance-test results because a story can be well defined before implementation has been tested.

This design is useful when domain rules need to be explicit and enforceable in an enterprise application. A production service would also need authorization, durable persistence, transaction boundaries, concurrent-update protection, and a clear policy for modifying completed stories.

## SQL implementation: relational backlog management

The PostgreSQL schema stores each part of the story-management domain in a table suited to its purpose.

| Table | Responsibility |
|---|---|
| `personas` | Stores user roles, context, goals, and constraints |
| `user_stories` | Stores the story statement components, priority, points, and state |
| `acceptance_criteria` | Stores independently identifiable Given-When-Then conditions |
| `invest_assessments` | Records the six quality attributes and assessment provenance |
| `story_dependencies` | Represents directed dependencies between stories |
| `refinement_reviews` | Records refinement decisions and findings |
| `acceptance_results` | Records test outcomes for individual acceptance criteria |

Foreign keys preserve the relationships between personas, stories, criteria, assessments, dependencies, reviews, and test results. Unique constraints prevent duplicate story keys and duplicate criterion keys within a story. Check constraints restrict priorities, workflow states, points, criterion categories, and decision values.

The dependency table uses a composite primary key to prevent duplicate dependency edges. Its self-dependency constraint prevents a story from directly depending on itself. More complex cycles require additional validation because ordinary foreign keys and check constraints do not prevent arbitrary cycles in a graph.

The `enforce_story_state_transition()` trigger checks state changes against an explicit transition policy. This protects the database against invalid transitions made by an application that bypasses the normal workflow. It does not, by itself, enforce every readiness condition.

The `story_quality` view combines story information, acceptance-criterion counts, and INVEST assessments. The `sprint_readiness` view evaluates whether a story is in the ready state, has acceptable refinement quality, and has completed dependencies.

The latest acceptance-result query uses a lateral join to select the most recent recorded execution for each criterion. This avoids treating an old passing result as the current result after a newer failed execution.

The recursive dependency query traces prerequisite chains while avoiding repeated nodes in the current path. It is intended for reporting and dependency inspection, not as a complete cycle-prevention mechanism.

The script uses a transaction to group schema creation and sample data operations. In a shared production database, schema ownership, concurrent writes, migration management, permissions, and audit retention require separate operational policies.

## Story splitting and dependencies

A large story can be difficult to estimate because it contains multiple outcomes, uncertain integration work, or too many independent acceptance conditions.

Useful splitting boundaries include distinct user outcomes, alternative workflows, permission levels, validation rules, and independently deliverable capabilities. A banking team might separate selecting an eligible funding account from submitting a transfer, provided each resulting story remains meaningful and the delivery sequence is clear.

Dependencies should express real prerequisites rather than coordination preferences. If a transfer requires an eligible funding account, the dependency should be recorded. If two stories can be implemented and tested independently, forcing an artificial dependency can slow delivery and make prioritization less flexible.

Dependency graphs must be checked for missing references and cycles. A cycle means that at least one story cannot be ordered before the other as currently modeled. Teams should reconsider the scope or identify the real prerequisite rather than simply suppressing the validation error.

## Estimation and prioritization

Story points are relative estimates of delivery effort, uncertainty, and complexity within a team's estimation practice. They are not hours, business value, or a direct measure of productivity.

Priority represents the relative urgency or importance of a backlog item. The Python, JavaScript, C++, and Java examples use priority first and story size as a tie-breaker to create deterministic displays. That is a demonstration policy, not a universal prioritization formula.

Real prioritization should account for user impact, risk reduction, dependencies, delivery cost, regulatory commitments, and opportunity cost. A smaller story should not automatically outrank a larger story with substantially greater user value.

An unestimated story should remain distinguishable from a story estimated at a small size. Missing information is not evidence that a story requires little work.

## Common refinement failures

**A persona is too broad.** A phrase such as "all users" often hides different goals and permissions. Define the user group relevant to the capability.

**The value merely repeats the need.** Explain the outcome that makes the capability useful.

**Acceptance criteria describe implementation details instead of behavior.** Preserve essential constraints but define the observable result the product must deliver.

**A criterion is not measurable.** Replace vague conditions such as "fast" or "secure" with observable expectations or explicit policy references.

**The story is too large.** Separate outcomes and review whether each resulting story can be estimated and verified independently.

**INVEST is treated as a score that overrides judgment.** Record the failing attribute and discuss the reason. A story with an unavoidable dependency may still be valid, but the dependency should be understood and managed.

**Readiness is confused with completion.** A ready story is prepared for implementation. A done story requires the team's agreed completion and verification conditions.

**Old test results are treated as current evidence.** Retain execution history and distinguish the latest result from historical passes.

## Security, reliability, and operational considerations

Stories involving financial transactions, personal information, or administrative diagnostics need explicit security and failure criteria. User-facing success criteria alone are insufficient for operations that can create financial or regulatory consequences.

A retry scenario should define whether the original request succeeded, whether the client can safely retry, and how the system prevents duplicate effects. A diagnostic story should define which role may access the record and what information may be displayed. An audit story should establish which events are recorded and who may retrieve the evidence.

The examples represent these requirements as acceptance criteria. They do not implement a payment processor, authorization service, or cryptographic audit mechanism.

For production use, the story-management service should persist state transitions and refinement decisions. State changes should be transactional, concurrent updates should be detected, and access to sensitive requirements should be controlled. Database constraints should enforce structural invariants, while application services enforce workflow rules that depend on multiple records or authorization context.

## Interpreting the six implementations

The implementations share a domain vocabulary but serve different technical purposes.

Python emphasizes validation, reports, and dependency ordering. JavaScript emphasizes asynchronous refinement and event-driven processing. C++ emphasizes a governance engine with controlled transitions and sprint-readiness checks. Java emphasizes explicit domain types, state modeling, and refinement decisions. SQL emphasizes relational integrity, queryable assessments, and database-enforced transitions.

The same story may therefore have a valid user statement but incomplete acceptance criteria, pass INVEST but remain blocked by a dependency, or be ready for implementation while still lacking successful acceptance-test results. These are distinct states of knowledge and delivery that should remain distinguishable in a reliable product backlog.
