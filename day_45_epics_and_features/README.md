# Epic and Feature Management

## Purpose and domain model

Epics and features organize product work at different levels of abstraction. An epic describes a significant business outcome that usually requires several related capabilities. A feature describes a specific capability that contributes to that outcome and can be planned, implemented, tested, and delivered.

A useful hierarchy connects strategic intent to verifiable delivery:

- **Epic:** A broad outcome, such as reducing the time required to onboard enterprise customers.
- **Feature:** A meaningful capability, such as identity verification, customer profile capture, eligibility assessment, or an auditable decision trail.
- **Acceptance criteria:** Testable statements defining the conditions under which a feature is acceptable.
- **Dependency:** A relationship indicating that one feature requires another capability to be available first.
- **Release:** A delivery window with a target date and a finite amount of implementation capacity.
- **Priority:** A relative business ordering used to guide decisions when time, capacity, or resources are constrained.

An epic should express a business outcome rather than merely collect unrelated tasks. A feature should describe a capability with a clear owner and observable acceptance conditions. An implementation team may further decompose features into stories and technical tasks, but those lower-level items are not required to represent the relationship between epics and features in these programs.

## How epics differ from features

| Dimension | Epic | Feature |
|---|---|---|
| Primary purpose | Organize a substantial business outcome | Deliver a defined product capability |
| Scope | Spans multiple capabilities or delivery increments | Has a more bounded implementation scope |
| Ownership | Accountable product or business owner | Product, engineering, or specialist delivery owner |
| Planning | Outcome, broad schedule, and investment | Estimate, acceptance criteria, dependencies, and release |
| Progress | Aggregated from child features | Determined by its own lifecycle and completion evidence |
| Completion | Requires all child features to reach a terminal state | Requires satisfied dependencies and validated acceptance criteria |
| Change management | Reassesses scope and the intended outcome | Reassesses capability boundaries, estimates, and dependencies |

The distinction is structural, not merely a difference in title. An epic can remain strategically valuable while individual features change, split, move to a later release, or become unnecessary. Feature completion does not automatically establish that the overall business outcome has been achieved. The outcome metric must still be measured against its baseline and target.

## Feature decomposition and business traceability

Consider an enterprise customer-onboarding program. Its intended outcome is to reduce manual onboarding effort without weakening identity and eligibility controls.

The epic can contain these related capabilities:

| Feature | Purpose | Dependency |
|---|---|---|
| Identity verification | Validate customer identity using approved evidence | None |
| Customer profile capture | Collect and validate required customer information | Identity verification |
| Eligibility assessment | Apply documented eligibility rules to the application | Customer profile capture |
| Decision audit trail | Record decision inputs, outcomes, and accountable ownership | Eligibility assessment |

The dependency chain defines an implementation order. It does not mean that every feature must be delivered in the same release. A feature can be planned for a later release, provided the release plan accounts for prerequisites and avoids committing a capability whose required foundation will not be available.

Each feature should have a named owner, a non-negative estimate, a target date where applicable, and acceptance criteria that can be evaluated independently. For example, a criterion for eligibility assessment might state that incomplete applications cannot be approved. The criterion is meaningful because a test can establish whether the system enforces that rule.

## Lifecycle and progress semantics

The implementations use a controlled work-item lifecycle:

| State | Meaning |
|---|---|
| `proposed` | The work item has been identified but is not yet planned |
| `planned` | The work item has been accepted into the delivery plan |
| `in_progress` | Implementation or validation is underway |
| `blocked` | Progress is prevented by a dependency or another impediment |
| `done` | Required completion conditions have been satisfied |
| `cancelled` | The work item will not be delivered in its current form |

Transitions are restricted to valid paths. A proposed feature can become planned or cancelled. A planned feature can start or be cancelled. An active feature can become blocked, complete, or cancelled. A blocked feature can resume or be cancelled. Completed and cancelled items are terminal in these examples.

These rules prevent invalid lifecycle changes, such as moving a completed feature back into active development without an explicit reopening policy. Real organizations may introduce a separate reopening workflow, but it should be intentional and audited rather than silently bypassing completion rules.

An epic's progress can be calculated by counting completed features or by weighting completed work using estimates. These calculations answer different questions.

Feature-count progress treats a small capability and a large capability equally. Point-weighted progress estimates the share of planned effort represented by completed features:

`weighted progress = completed feature points / total feature points × 100`

Neither measure proves business value has been realized. Both are delivery indicators, and both can be misleading if estimates are inconsistent, scope changes without recalculation, or cancelled features remain in the denominator. Production reporting should explicitly define how cancellations, scope changes, and unestimated features affect the calculation.

## Python implementation

The Python program implements an in-memory planning portfolio using `Epic`, `Feature`, `WorkItem`, and `Portfolio` classes.

### Domain representation

`WorkItem` contains the common identity, ownership, priority, status, schedule, and estimate fields. `Feature` adds acceptance criteria, dependency identifiers, and release assignment. `Epic` adds a business outcome and a collection of child features.

The dataclasses provide readable domain structures, while enumerations constrain priorities and lifecycle states. Constructor validation rejects missing identifiers, empty titles, missing owners, negative estimates, and invalid date ranges.

The portfolio maintains separate dictionaries for epics and features. A parent mapping records which epic contains each feature. Keeping these structures separate makes it possible to validate globally unique identifiers and perform direct feature lookups without repeatedly scanning every epic.

### Dependency validation

`Portfolio.set_dependencies()` checks that each referenced feature exists and that the proposed graph remains acyclic. Its depth-first search tracks both the current traversal path and previously visited nodes. Encountering a node already on the current path identifies a cycle.

Dependency updates are transactional at the application level: the previous dependency set is restored if validation fails. This prevents an invalid proposed relationship from leaving the in-memory model inconsistent.

### Planning and reporting

`progress()` calculates feature-count and point-weighted completion. `ready_features()` identifies active features whose direct prerequisites are complete. `prioritize()` orders work by priority, target date, and identifier. `release_capacity()` selects eligible release candidates within a point budget.

Capacity allocation is a planning heuristic rather than an optimal scheduling algorithm. Priority ordering and a simple fit check do not solve every scheduling problem involving team availability, parallel work, deadlines, risk, and dependencies. The distinction matters when converting a planning demonstration into a production planning system.

### Persistence and tests

`to_json()` serializes the portfolio with a schema version, parent relationships, dependency references, and audit events. `save()` writes a temporary file and replaces the destination only after the complete content has been written. This reduces the risk of leaving a partially written destination file, although filesystem durability and concurrent-writer coordination require additional controls in production.

The embedded unit tests cover weighted progress, dependency readiness, cycle rejection, terminal-state enforcement, unknown dependencies, negative capacity, duplicate identifiers, and JSON validity. The executable test suite makes the domain rules verifiable rather than leaving them as comments.

Run the program with `python epic_feature_management.py`. It uses only the Python standard library.

## JavaScript implementation

The JavaScript program focuses on an event-driven planning board rather than duplicating the Python portfolio design.

### Event-driven work-item changes

`PlanningBoard` extends Node.js's `EventEmitter`. It emits domain events when epics and features are created, dependencies change, lifecycle states change, or release candidates are excluded. Each event contains a sequence number, timestamp, event type, and payload.

Consumers can use these events to update a dashboard, produce an audit stream, or notify another service. In this in-memory implementation, event listeners run within the process. Emitting an event is not equivalent to reliably publishing it to an external message broker, and listener failures or process termination can affect delivery guarantees.

### Revision checks and asynchronous policies

Each feature carries a revision counter. A transition supplies the revision observed by the caller. If the current revision differs, the transition fails with a `REVISION_CONFLICT` error.

This is an optimistic concurrency pattern: callers can work from snapshots without acquiring a long-lived lock, but stale updates are rejected. The example demonstrates the rule inside a single Node.js process. A multi-instance service needs atomic revision checks in a shared database or another concurrency-control mechanism.

The asynchronous `evaluateRelease()` function accepts a policy callback. This separates release eligibility from the board's data structures. The caller can check prerequisites or other business rules without embedding every policy inside the planning model.

### Dependency ordering

`DependencyGraph` represents prerequisites as directed edges and uses depth-first traversal to detect cycles and compute a topological order. The resulting order places dependencies before their dependents.

The graph order is useful for reasoning about execution, but it does not determine which work a team should prioritize. The release evaluator separately applies priority ordering, capacity limits, and a supplied policy. Dependency feasibility and capacity feasibility remain distinct checks.

The program uses built-in Node.js modules only. Run it with `node epic_feature_management.js`.

## C++ case study: Utility account modernization

The C++ program models a utility provider's account-modernization initiative. The epic represents the intended business outcome, while features represent identity verification, digital application handling, eligibility decisions, and the audit trail.

### Architecture and data structures

`WorkItem`, `Feature`, `Epic`, and `ReleasePlan` represent the domain. `PlanningEngine` centralizes identifier validation, lifecycle transitions, dependency management, release allocation, and progress reporting.

The implementation uses `std::map` for predictable key-based access, `std::set` for unique dependency identifiers, and `std::vector` for ordered feature collections and release decisions. These standard containers avoid external dependencies and make the data model explicit.

The engine rejects duplicate identifiers, missing parent epics, empty acceptance criteria, negative estimates, and dependencies that reference unknown features. A feature cannot be marked complete while its prerequisites remain unfinished.

### Graph algorithm and complexity

Dependency-cycle validation uses depth-first search. With an adjacency-list representation, graph traversal takes `O(V + E)` time, where `V` is the number of features and `E` is the number of dependency edges. The visited-state map prevents repeated traversal of already processed nodes.

The implementation temporarily applies a proposed dependency set, validates the complete graph, and restores the previous set if a cycle is detected. This keeps a failed planning operation from corrupting the existing dependency structure.

The release planner filters features by release and lifecycle state, sorts them by priority and identifier, and attempts to fit them within a point budget. Sorting costs `O(F log F)` for `F` candidate features, while the subsequent allocation pass is linear.

This greedy allocation is deterministic, but it is not guaranteed to maximize the total number of points or business value delivered. It is appropriate as a transparent baseline for planning discussions, not as a substitute for an optimization model when scheduling constraints become complex.

### Failure handling and relevance

Invalid operations throw `std::invalid_argument`, while the executable catches exceptions at the application boundary and reports a controlled failure. The case study also checks that cyclic dependencies and premature epic completion are rejected.

A production implementation would typically persist changes in a transaction, record who made each change, distinguish delivery commitments from proposals, and account for release-specific compliance requirements. The program demonstrates the domain logic without claiming to provide distributed persistence or a multi-user planning service.

Compile with a C++17-compatible compiler using `g++ -std=c++17 -Wall -Wextra -pedantic`.

## Java implementation: Enterprise planning service

The Java program emphasizes explicit domain types and a service boundary suitable for enterprise application design.

### Domain abstractions

`WorkItem` represents the common properties shared by epics and features. `Epic` holds a `BusinessOutcome` and a collection of child features. `Feature` owns a capability description, immutable acceptance criteria, dependencies, and a release identifier.

The `AcceptanceCriterion`, `BusinessOutcome`, `Progress`, `ReleaseDecision`, and `AuditEntry` records make specific concepts explicit. Records are useful for values that should not expose arbitrary mutation. The mutable lifecycle state remains encapsulated within `WorkItem`.

The use of `List.copyOf()` and `Set.copyOf()` protects collection boundaries from direct modification by callers. This does not make the entire object graph deeply immutable: `Feature` still refers to a mutable `WorkItem`. The design deliberately separates immutable descriptive data from mutable lifecycle state.

### Policy and state management

`WorkflowPolicy` defines valid status transitions independently of `PlanningService`. The service checks the proposed transition and verifies that feature prerequisites have been completed before allowing the feature to reach `DONE`.

`PlanningService` owns the epic and feature registries, validates cross-item references, detects dependency cycles, calculates progress, evaluates release candidates, and records audit events. It also refuses to complete an epic while active child features remain.

The release evaluator combines prerequisite checks, a supplied compliance predicate, and remaining capacity. Every candidate receives an explicit eligibility decision and reason. This makes rejected candidates explainable instead of returning only a list of selected features.

### Exceptions and enterprise boundaries

`PlanningException` represents domain-level failures such as unknown work items, invalid transitions, and incomplete prerequisites. Constructor validation uses `IllegalArgumentException` for malformed values.

The audit trail records lifecycle events in memory with timestamps. In a deployed service, audit records should be durable and protected from unauthorized alteration. Database transactions should coordinate changes to feature state, dependency records, and audit history so that partial updates cannot be mistaken for successful completion.

Compile and run with Java 17 or later:

- `javac EpicFeatureManagement.java`
- `java EpicFeatureManagement`

## PostgreSQL data model

The SQL implementation uses the `product_planning` schema to represent the relationships between organizational ownership, epics, features, acceptance criteria, dependencies, releases, and lifecycle history.

### Relational structure

| Table | Responsibility |
|---|---|
| `teams` | Identifies delivery teams |
| `product_owners` | Associates accountable people with teams |
| `releases` | Defines release windows and point capacity |
| `epics` | Stores business outcomes, target metrics, ownership, and epic status |
| `features` | Stores capabilities, estimates, priorities, release assignments, and parent epics |
| `acceptance_criteria` | Stores testable feature requirements and their verification evidence |
| `feature_dependencies` | Models prerequisite relationships between features |
| `work_item_history` | Records lifecycle changes for audit and analysis |

Surrogate identity keys provide stable relational references. Human-readable keys such as `EP-ONBOARD` and `FEAT-IDENTITY` provide recognizable business identifiers. Unique constraints prevent duplicate keys, foreign keys enforce valid references, and check constraints reject invalid estimates, empty required text, and reversed date ranges.

The foreign key from `features.epic_id` ensures every feature belongs to an existing epic. The separate dependency table supports many-to-many relationships: one feature can require several prerequisites, and a feature can be a prerequisite for several other features.

### Acceptance criteria and completion integrity

The `acceptance_criteria` table stores criteria individually instead of placing them in a single unstructured field. Its verification columns require a verifier and timestamp when a criterion is marked verified.

The `enforce_feature_completion()` trigger prevents a feature from entering `done` if it has no acceptance criteria, has unverified criteria, or depends on an unfinished feature. This moves an important integrity rule into the database so that a direct SQL update cannot bypass the completion requirement.

A check constraint alone cannot establish whether all rows related to a feature have been verified. The trigger is needed because completion depends on related records rather than only the updated feature row.

### Dependency integrity and recursive queries

A self-referencing foreign key establishes that a prerequisite exists, but it cannot guarantee that the dependency graph is acyclic. The `prevent_feature_dependency_cycle()` trigger uses a recursive common table expression to test whether a proposed edge would create a path back to the dependent feature.

The cycle check prevents straightforward cyclic inserts and updates. Concurrent transactions modifying different edges can still create race conditions unless graph updates are serialized or coordinated with appropriate locking or transaction isolation. A production implementation must address that concurrency case explicitly.

The recursive `dependency_closure` query calculates indirect prerequisites. This is important because a release candidate can be blocked by a transitive dependency even when its direct prerequisite appears complete or is incorrectly modeled.

### Progress and release planning

The `epic_progress` view aggregates feature counts and estimates for each epic. `weighted_completion_percent` measures completed estimated effort against total estimated effort. `NULLIF` prevents division by zero, while `COALESCE` ensures empty aggregates return usable numeric values.

The `feature_readiness` view reports whether dependencies are satisfied for active features. It separates prerequisite readiness from acceptance verification and release capacity.

The release-planning query filters unfinished R1 features, excludes candidates with incomplete prerequisite chains, and uses a window function to calculate cumulative estimated effort in priority order. The `fits_capacity` column indicates which ranked candidates fit within the release's point budget.

This query is a planning report rather than a complete scheduling optimizer. A feature that does not fit the cumulative budget might still fit a different allocation. Release commitments should also account for team availability, delivery risk, business value, and dependencies.

### Triggers, audit history, and transactions

The status-history triggers insert lifecycle records whenever an epic or feature is created or changes status. The audit rows preserve the previous state, new state, item identifier, and timestamp.

The epic completion trigger rejects completion while any child feature remains active. Together, the completion triggers and history table provide database-level enforcement and traceability.

The script uses a transaction to create the schema objects, insert sample data, evaluate the model, demonstrate rejection of a cyclic dependency, and commit the valid changes. The deliberately invalid dependency is caught inside a PL/pgSQL exception block and rolled back to a savepoint.

The trigger-based history table records state transitions, not every possible change to a title, estimate, owner, priority, or description. Full change-data auditing would require additional triggers or a separate audit mechanism. The history table also references work items by type and numeric identifier rather than using a single foreign key, so its integrity depends on controlled write paths and appropriate audit-retention practices.

Execute the SQL script in a PostgreSQL environment. It creates objects in the dedicated `product_planning` schema.

## Dependency management and release feasibility

A dependency answers whether a capability requires another capability. Priority answers which work is more important. Capacity answers how much estimated work a release can accommodate. These are separate planning dimensions.

A critical feature may be blocked by a prerequisite. A low-priority feature may still be required for a release's compliance obligations. A feature can be technically ready but excluded because the release lacks capacity. A feature can fit the budget but remain inappropriate for delivery if its acceptance conditions have not been met.

Effective release planning evaluates these constraints independently and explains the reason for every exclusion. The planning examples use deterministic heuristics to make those decisions visible. Complex portfolios may require dependency-aware scheduling, multiple delivery teams, skill constraints, risk-adjusted estimates, and explicit business-value scoring.

## Data integrity and operational limitations

The implementations demonstrate domain validation, lifecycle control, dependency-cycle detection, progress reporting, release-capacity checks, and audit events. Their persistence and concurrency guarantees differ.

- The Python and JavaScript programs maintain in-memory state. Their audit records disappear when the process ends unless exported or connected to durable storage.
- The C++ program uses in-memory standard containers and exception-based validation. It does not provide multi-user transactions or persistent recovery.
- The Java program separates domain types, workflow policies, and service operations, but its registries and audit trail are also in memory.
- The PostgreSQL model persists relationships and enforces selected cross-record rules through constraints and triggers. Its cycle validation and audit design still require careful transaction and permission management in production.

Estimates should be treated as planning measurements rather than objective measures of developer productivity. A feature's completion should be based on explicit acceptance evidence, not a status update alone. Epics should be evaluated against their business outcomes even when all planned features are complete, because delivering capabilities and realizing the intended business benefit are related but distinct events.
