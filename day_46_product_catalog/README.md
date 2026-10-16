# Product Backlog Engineering: Refinement, Prioritization, Dependencies, and Technical Debt

## Purpose and scope

A product backlog is an evolving, ordered collection of work that may contribute to a product's outcomes. It is not simply a list of features or a collection of tickets. Effective backlog management connects customer value, operational urgency, engineering risk, implementation effort, prerequisite relationships, and the capacity available to deliver changes.

This repository models backlog management through five complementary implementations. Python emphasizes a compact domain model and executable workflow simulation. JavaScript explores event-driven change records and optimistic concurrency during refinement. C++ models a capacity-constrained engineering planning system. Java separates enterprise domain types, workflow rules, prioritization, and sprint planning. PostgreSQL demonstrates relational integrity, dependency validation, workflow enforcement, and analytical queries.

The examples use realistic service-platform scenarios involving reliability, payment processing, authorization, telemetry, and database performance.

## The backlog as a product decision system

A backlog item represents a proposed change, defect, investigation, security correction, or engineering improvement. An item becomes useful when its purpose, boundaries, expected outcome, and dependencies are sufficiently clear to support a delivery decision.

A practical backlog separates several questions:

| Concern | Question answered | Evidence |
|---|---|---|
| Product value | Why should this work be done? | User outcomes, business impact, operational needs |
| Refinement | Is the work sufficiently understood? | Clear description, acceptance criteria, estimate |
| Prioritization | Why should this work precede alternatives? | Value, urgency, risk, opportunity cost |
| Dependencies | What must be completed first? | Explicit prerequisite relationships |
| Capacity | What can reasonably fit in the delivery period? | Effort estimates and team capacity |
| Technical debt | What future cost does the current implementation create? | Rework, operational drag, accumulated maintenance cost |

These concerns are related but not interchangeable. A high-value item may be impossible to start because a prerequisite remains unfinished. A well-refined item may not be the most urgent item. A low-visibility security correction may deserve immediate attention even when a simple value-to-effort ratio places it below a customer-facing feature.

## Refinement and readiness

Refinement is the process of reducing uncertainty so that the team can make informed decisions about scope, effort, and implementation. It can change an item's description, acceptance criteria, estimate, dependencies, or delivery assumptions.

A refined item should make its intended result observable. For example, "improve payment reliability" is too broad to verify directly. "Repeated requests with the same idempotency key cannot execute the same payment twice" expresses a testable behavior.

Acceptance criteria provide evidence that the intended behavior has been implemented. They should describe observable outcomes rather than prescribe unnecessary internal implementation details.

Readiness is a workflow decision, not a synonym for importance. The implementations require acceptance criteria and completed prerequisites before an item can enter the ready state. These rules are deliberately stricter than a simple priority ranking.

The state model distinguishes proposed, refining, ready, in-progress, blocked, done, and rejected work. Explicit transitions prevent invalid operations, such as completing work that never started or reopening completed work through an ordinary status change.

A production organization may adopt a different transition policy. The important design property is that transitions are explicit, validated, and auditable rather than inferred from arbitrary status assignments.

## Prioritization under uncertainty

The examples use a transparent weighted cost-of-delay heuristic:

\[
C = 0.5V + 0.3U + 0.2R
\]

\[
S = \frac{C}{E}
\]

where:

- \(V\) is business value, rated from 1 to 10.
- \(U\) is urgency, rated from 1 to 10.
- \(R\) is risk reduction, rated from 1 to 10.
- \(E\) is estimated effort, represented by a positive integer.
- \(C\) is the weighted cost-of-delay signal.
- \(S\) is the resulting score.

The weights and rating scales are illustrative policy choices. They are not universal industry standards, and the resulting score is not a calibrated monetary estimate.

The implementations also elevate certain urgent security items and defects into a critical priority band. This prevents a simple ratio from obscuring work whose delay may create unacceptable exposure.

A priority band and a numeric score answer different questions. The band communicates a decision category. The score helps compare items within a category. Neither establishes delivery feasibility or removes the need for product judgment.

### Limits of ratio-based prioritization

A ratio can favor a small improvement over a larger investment with greater strategic value. Scores also depend on estimation quality and stakeholder judgment. If value and urgency ratings are inconsistent across teams, numerical precision can conceal rather than resolve disagreement.

A mature process records the reasons behind an ordering decision, reviews assumptions when circumstances change, and treats the ranking as a decision aid rather than an immutable schedule.

## Dependencies and feasible ordering

A dependency states that one item requires another item to be completed first. For example, settlement latency metrics may depend on the availability of a reliable settlement event model.

Dependencies form a directed graph. Each edge points from a dependent item to its prerequisite. The graph must remain acyclic because a cycle creates a situation in which no item in that cycle can satisfy all its prerequisites.

The Python, C++, and JavaScript models use depth-first traversal to detect cycles. A node currently being explored indicates a potential cycle if traversal encounters it again. Completed nodes are recorded so that shared prerequisites do not need to be processed repeatedly.

The PostgreSQL implementation validates dependency changes using a recursive common table expression in a trigger. This moves cycle prevention closer to the stored relationships rather than relying exclusively on a client application.

The Java model separates repository integrity from workflow transitions. This allows the domain service to reject missing prerequisites and circular relationships before they affect planning.

### Direct blockers and transitive prerequisites

A direct blocker is an unfinished immediate prerequisite. A transitive prerequisite lies earlier in the dependency chain.

Suppose item C depends on item B, and item B depends on item A. Item A is a transitive prerequisite of C even though it is not directly connected to C. A dependency closure is useful for impact analysis, while direct blockers are useful for explaining why an item cannot currently start.

Dependency validation should also account for the status of prerequisites. An item with a complete description and strong business value is not ready for execution when its required foundation remains incomplete.

## Technical debt as an explicit investment

Technical debt describes an engineering choice or existing implementation condition that creates future maintenance, delivery, reliability, or operational costs. It should not be treated as a label for every undesirable task.

Examples in these implementations include inefficient reconciliation queries, repeated permission evaluation, and retry behavior that amplifies failures. These items are engineering investments with identifiable consequences.

The debt forecast uses a simplified model:

\[
D_n = P + nI
\]

where \(P\) represents an estimated current remediation or debt principal, \(I\) represents estimated additional cost per sprint, and \(n\) is the projection horizon.

This model is deliberately simple. Real technical debt can compound nonlinearly, affect several teams, or create risks that cannot be expressed in a single monetary value. The estimate should be calibrated against query counts, incident frequency, maintenance effort, delivery delays, or other relevant evidence.

A useful debt item explains the current constraint, its observed consequence, the proposed engineering change, and the behavior that must remain unchanged. For example, batching database reads should reduce query amplification without changing authorization outcomes or the ordering of returned records.

Security exposure and reliability risks may justify prioritization independently of their projected financial cost.

## Python implementation

The Python program uses dataclasses and enumerations to represent backlog items, work types, workflow states, and priority categories. `ProductBacklog` centralizes item lookup, dependency validation, state transitions, prioritization, debt forecasting, and sprint selection.

The dependency graph is represented by sets of item identifiers. This prevents duplicate dependency edges and makes membership checks efficient. The dictionary of backlog items provides direct lookup by stable identifier.

The transition method validates the current state before changing it. A ready item must contain acceptance criteria and have no unfinished direct prerequisites. An in-progress item cannot start while its dependencies remain incomplete.

The priority method combines weighted value, urgency, and risk reduction with estimated effort. The sprint planner repeatedly chooses the highest-ranked feasible ready item that fits the remaining capacity. It accounts for prerequisites satisfied by earlier selections in the same proposed sprint.

This greedy strategy is easy to inspect, but it is not guaranteed to find the globally optimal combination of work. More sophisticated planning may use optimization algorithms, explicit dependency scheduling, or multiple capacity dimensions.

The debt report separates principal from projected interest. Its output can support a discussion about whether an engineering investment is becoming more expensive to defer.

The executable demonstration also exercises invalid transitions, duplicate or missing identifiers, invalid estimates, and circular dependencies. Expected failures are caught and displayed instead of terminating the complete demonstration.

## JavaScript implementation

The JavaScript version models the backlog as an event-emitting service. It uses a private `Map` for the internal item collection and exposes a copied map for inspection. The collection copy prevents callers from directly adding or removing items through the returned map, although the item objects themselves remain mutable domain objects.

`EventEmitter` publishes status-change and refinement events. Each recorded event includes an identifier, timestamp, item version, and structured details. This demonstrates how an application can expose backlog changes to an audit consumer or a downstream workflow.

The refinement method accepts an expected version. If the current version differs, the operation rejects the stale update. This is an optimistic concurrency check: it detects that another operation has changed the item since the caller read it.

Refinement validation uses a reconstructed item to verify the proposed result. If validation fails, the previous editable fields are restored. A production implementation should also validate dependency changes, use immutable snapshots or transactional persistence, and avoid exposing mutable internal objects.

The example uses Node.js built-in modules for event handling and unique event identifiers. It does not require an npm dependency.

The event log is an in-memory demonstration, not durable audit storage. A restart loses its records. A production service would persist events and item changes transactionally, apply authorization to mutations, and define retention and access rules for audit data.

## C++ case study: capacity-constrained engineering planning

The C++ program models a service-platform backlog containing identity propagation, distributed tracing, database lookup optimization, and a tenant-isolation defect.

The `WorkItem` structure contains domain estimates, state, dependencies, and acceptance criteria. The `Backlog` class owns the item collection and provides methods for validating dependencies, computing priority, transitioning states, and planning a sprint.

A `map` provides ordered identifier lookup. Sets represent dependency relationships without duplicate entries. The dependency validation routine uses a three-color depth-first traversal, while the planning routine repeatedly evaluates ready items against both capacity and prerequisite completion.

The case study elevates urgent security work above ordinary ratio-based comparisons. It also demonstrates why dependency integrity should be checked before accepting a changed relationship.

The implementation validates effort and scoring ranges at construction time. It rejects a ready-state transition when acceptance criteria are missing, and it prevents an ordinary transition out of the done state.

The planning routine uses a greedy strategy and reports the resulting effort against capacity. This is appropriate for an inspectable example, but it does not prove that the selected set maximizes business value. A globally optimal plan can require a knapsack-style optimization model combined with dependency constraints.

The program uses only standard C++17 facilities. Compile it with a command such as `g++ -std=c++17 -Wall -Wextra -pedantic product_backlog.cpp -o product_backlog`.

## Java implementation: enterprise domain services

The Java program separates backlog persistence behavior, workflow rules, prioritization, debt forecasting, and sprint planning into distinct classes.

`WorkItem` holds the business state and validates score and effort ranges. Enums represent work types, workflow states, and priority bands, reducing the ambiguity that would arise from unvalidated status strings.

`BacklogRepository` provides identifier-based lookup and rejects missing prerequisites and dependency cycles. It removes a newly inserted item if graph validation fails, avoiding a partially accepted repository change.

`WorkflowService` defines allowed transitions explicitly. It checks acceptance criteria and unfinished dependencies before permitting readiness or execution. Its refinement operation requires an expected version and refuses to overwrite an item whose state has changed since the caller last inspected it.

`PrioritizationService` produces immutable assessment records and calculates debt forecasts. The Java record types make returned assessment data explicit and prevent callers from modifying the record components after construction.

`SprintPlanner` coordinates these services to select work within capacity while respecting prerequisite completion. Its immutable `SprintPlan` copies the list of selected identifiers, preventing later changes to the original mutable list from altering the reported plan.

This separation supports unit testing and makes policy boundaries visible. In a production system, the repository would normally be backed by transactional storage, while authorization, audit persistence, and cross-request concurrency would need enforcement beyond an in-memory version counter.

Compile and run with Java 17:

`javac ProductBacklogGovernance.java`

`java ProductBacklogGovernance`

## PostgreSQL data model

The SQL implementation stores the backlog as related relational entities rather than as a serialized application object.

| Relation | Responsibility |
|---|---|
| `products` | Identifies the product and its sprint capacity |
| `backlog_items` | Stores descriptions, estimates, work type, status, and debt values |
| `acceptance_criteria` | Stores verifiable completion conditions |
| `item_dependencies` | Represents prerequisite relationships |
| `refinement_sessions` | Preserves estimates and outcomes from refinement meetings |
| `sprint_plans` | Defines delivery periods and available capacity |
| `sprint_items` | Records selected work and planned effort |
| `backlog_audit` | Records workflow changes and associated actors |

Primary keys provide stable row identity. Foreign keys preserve referential integrity between products, items, criteria, dependencies, and sprint plans. Unique constraints prevent duplicate product keys, item keys within a product, and repeated criteria for the same item.

Check constraints validate numeric ranges, positive capacity, non-negative debt estimates, and valid date intervals. Partial indexing on unverified acceptance criteria supports a common readiness query without indexing every criterion row in the same way.

The schema uses PostgreSQL enumerated types for work type and status. These types restrict stored values, but they do not automatically enforce valid transitions. The `transition_backlog_item` function performs transition validation, checks readiness requirements, locks the target row, updates the version, and writes an audit record in the same transaction.

The dependency trigger uses a recursive query to detect whether adding an edge would make the graph cyclic. The foreign keys ensure that dependency endpoints exist. The application should still coordinate concurrent dependency mutations carefully because graph-wide integrity is more complex than single-row validation.

### Analytical views

`prioritized_backlog` computes the weighted score and priority band for active items. It provides a consistent basis for ordering and filtering the backlog.

`dependency_readiness` reports unfinished prerequisites alongside the number of acceptance criteria and the number already verified. It distinguishes dependency feasibility from documentation quality.

`technical_debt_forecast` calculates the four-sprint projected cost using the stored principal and per-sprint interest estimate. The projection horizon is fixed in this view to keep the example straightforward.

The aggregation query groups work by type and status, making it possible to detect a backlog dominated by one category or containing too much unfinished work.

### Transactional behavior and limitations

The workflow function uses `SELECT ... FOR UPDATE` to serialize competing transitions on the same item row. The update and audit insert execute within the caller's transaction, so a transaction rollback removes both changes.

The dependency trigger is a useful integrity safeguard, but complex concurrent graph updates may require stronger transaction coordination, such as serializable transactions or a dedicated dependency-management service. A single trigger does not eliminate every possible race condition across concurrent transactions.

The schema also does not enforce every business rule automatically. Sprint membership, total planned effort, and the requirement that all prerequisites appear earlier in a schedule are cross-row conditions. These require a transactional planning operation, additional triggers, or application-level validation with appropriate locking.

The sample uses savepoints and exception handling to demonstrate rejection of an invalid dependency without leaving a partially applied change.

Execute the script against a PostgreSQL database using a role authorized to create schemas, tables, types, functions, and triggers. The script is intended for a dedicated learning database; it creates objects in the `product_delivery` schema and is not designed to be rerun unchanged after its initial successful execution.

## Operational and governance considerations

A reliable backlog process needs consistent identifiers, explicit ownership, a clear definition of readiness, and a record of why decisions were made. Without these controls, estimates and priority scores become difficult to compare, and teams can lose the reasoning behind earlier decisions.

Refinement should reduce uncertainty rather than merely increase the number of fields attached to an item. Acceptance criteria must remain testable, estimates should reflect the actual scope, and dependencies should be recorded only when there is a genuine ordering constraint.

Sprint capacity is a planning boundary, not a promise that every selected item will finish. Interruptions, incidents, review delays, and unexpected engineering work can change the feasible set. Security corrections may require immediate reprioritization rather than waiting for a routine planning cycle.

Technical debt should be discussed using observable consequences. Query amplification, excessive retry load, repeated manual intervention, fragile deployment behavior, and recurring incidents provide more useful evidence than a generic debt label.

For production use, the domain rules illustrated in the source files should be supplemented with access control, durable audit events, transactional updates, concurrency protection, monitoring, backup procedures, and explicit policies for exceptional work. The objective is to make backlog decisions traceable and technically feasible while preserving the distinction between business priority, readiness, dependency constraints, delivery capacity, and engineering risk.
