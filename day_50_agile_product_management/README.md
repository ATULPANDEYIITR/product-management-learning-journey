# Agile Product Management: Outcomes, Flow, and Continuous Discovery

## Purpose

This artifact models Agile product management as a connected product operating system rather than as a collection of ceremonies.

The four central mechanisms are deliberately separated:

| Mechanism | Primary purpose | Main question |
|---|---|---|
| Product backlog | Maintain and order product opportunities and delivery candidates | What should the product team consider doing? |
| Product roadmap | Communicate directional outcomes and timing | Where is the product expected to create value? |
| Sprint goal | Establish short-term product focus | What meaningful outcome should this sprint pursue? |
| Continuous discovery | Reduce uncertainty through evidence | What have we learned, and should that change the plan? |

The implementations model these mechanisms as stateful systems with validation, prioritization, evidence, state transitions, capacity constraints, and outcome evaluation.

## Product Goals

A product goal represents a desired product outcome rather than a list of implementation tasks.

The model uses:

- A stable goal identifier
- An outcome statement
- A measurable metric
- A target value
- A target date

The example goal is to increase successful first-week activation. This creates a strategic reference point for backlog decisions, roadmap outcomes, and sprint goals.

A useful distinction is:

`Product goal -> measurable outcome`

rather than:

`Product goal -> collection of features`

This distinction prevents delivery activity from becoming the definition of product success.

## Product Backlog

The backlog contains opportunities and delivery candidates connected to identifiable customer problems.

Each item contains:

- A business or customer problem
- Value
- Effort
- Priority
- Lifecycle state
- Discovery evidence

The Python, JavaScript, C++, and Java implementations use a value-to-effort prioritization score:

`score = value × priority weight / effort`

The score is intentionally a decision-support mechanism rather than an automatic product decision. Real product prioritization may also require dependencies, confidence, risk, strategic alignment, regulatory constraints, technical uncertainty, and opportunity cost.

The SQL implementation reinforces the same principle by exposing prioritization through a view instead of permanently storing a calculated ranking.

### Backlog States

The implementations use a constrained lifecycle:

`DISCOVERY -> READY -> IN_PROGRESS -> DONE`

The states have different meanings.

**Discovery** indicates that an opportunity is still being understood.

**Ready** indicates that sufficient information exists for delivery consideration.

**In progress** indicates that the item has entered active implementation.

**Done** indicates that the delivery work has reached its defined completion state.

The state model prevents an unvalidated idea from being treated as equivalent to prepared delivery work.

## Roadmap

The roadmap implementation represents outcomes rather than a feature inventory.

A roadmap outcome contains:

- An outcome statement
- A target date
- A relationship to a product goal

For example:

`Increase activation -> Reduce onboarding friction -> Improve first-value path`

The roadmap therefore provides directional alignment between product strategy and delivery decisions.

It does not automatically dictate every backlog item. A roadmap outcome can be supported by multiple backlog items, experiments, technical changes, or changes in product behavior.

This distinction reduces the risk of interpreting a roadmap as an immutable sequence of implementation promises.

## Sprint Goals

A sprint goal connects a short delivery period to a product outcome.

The example sprint goal is:

`Improve the path from account creation to first value.`

The sprint then selects backlog items whose combined effort fits the available capacity.

The Python, JavaScript, C++, and Java implementations explicitly model:

- Sprint start and end
- Product-goal relationship
- Sprint goal statement
- Capacity
- Selected backlog items
- State transition into active work

Capacity is treated as a constraint rather than a target for filling with arbitrary work.

A sprint containing many unrelated tasks can have high activity but weak product coherence. A sprint goal gives the selected work a common outcome-oriented direction.

## Continuous Discovery

Continuous discovery is modeled separately from delivery.

The example hypothesis is:

`Guided setup improves first-value completion.`

The experiment records observed completion rates and compares their average against a predefined threshold.

This creates a simple evidence loop:

`Hypothesis -> Experiment -> Observation -> Evaluation -> Product decision`

A validated hypothesis can increase confidence in a backlog direction. An invalidated hypothesis can prevent unnecessary implementation effort.

Discovery therefore influences the backlog instead of becoming a documentation exercise performed after a delivery decision has already been made.

## Python Implementation

The Python implementation uses dataclasses, enums, dictionaries, sets, validation methods, exceptions, sorting, and explicit domain objects.

`BacklogItem` owns value, effort, priority, evidence, and state. Its scoring method provides deterministic prioritization.

`ProductGoal`, `RoadmapOutcome`, and `SprintGoal` use immutable-style dataclass definitions where appropriate.

`ProductManagementModel` acts as the application service coordinating:

- Product goals
- Roadmap outcomes
- Backlog entries
- Sprint creation
- Discovery experiments
- Delivery state transitions

The sprint planner ranks eligible backlog items and selects work while capacity remains.

The demonstration also completes a selected item to show that the model is stateful rather than merely calculating a static backlog report.

## JavaScript Implementation

The JavaScript implementation uses classes, immutable constant objects, maps, event records, validation exceptions, and an asynchronous execution boundary.

The `ProductManagementEngine` maintains the domain state and produces event records when important product-management changes occur.

This creates an event-oriented perspective:

`Goal created -> Backlog added -> Experiment evaluated -> Sprint created -> Item completed`

The implementation does not require an npm package. It can run directly in a Node.js environment.

The asynchronous boundary is intentionally small but meaningful. A production implementation could replace the resolved promise with asynchronous analytics, experiment, backlog, or product-data services without changing the domain concepts.

The event stream also provides a foundation for auditability.

## C++ Implementation

The C++ implementation treats product management as a constrained governance engine.

It uses:

- `std::map` for deterministic keyed domain storage
- `std::set` for discovery evidence
- `std::vector` for ordered collections
- Enums for product-management states
- References for ranked backlog manipulation
- Explicit exceptions for invalid operations

The engine evaluates backlog items through a value, priority, and effort model.

It then constructs a sprint within a capacity constraint.

The delivery-eligibility method adds a separate governance layer. A sprint cannot be considered eligible until:

- Selected work exists
- Selected work is complete
- Discovery validation exists when policy requires it
- Required validation checks have passed

This separates product prioritization from execution governance.

The program also documents the main computational characteristics:

- Backlog ranking is `O(n log n)`
- Sprint selection is dominated by ranking
- Keyed lookup uses logarithmic `std::map` access

The numeric score is deliberately not treated as a replacement for product judgment.

## Java Enterprise Model

The Java 17 implementation uses records for immutable domain values and a service class for workflow behavior.

Important domain types include:

- `ProductGoal`
- `RoadmapOutcome`
- `BacklogItem`
- `SprintGoal`
- `Sprint`
- `DiscoveryExperiment`

The `ProductGovernanceService` owns the state transitions and validates relationships between entities.

The Java implementation explicitly rejects invalid transitions such as:

`DONE -> IN_PROGRESS`

or:

`DISCOVERY -> DONE`

This makes the lifecycle a domain rule instead of a convention.

Java streams are used for backlog ranking and discovery aggregation. `EnumMap` maintains state counts efficiently for the finite `BacklogState` domain.

The enterprise-oriented structure separates immutable data representation from services that perform mutations and policy checks.

## PostgreSQL Model

The PostgreSQL implementation represents the same product-management concepts relationally.

Core relationships include:

`product_goals -> roadmap_outcomes`

`product_goals -> sprints`

`backlog_items -> backlog_evidence`

`sprints -> sprint_backlog -> backlog_items`

`discovery_experiments -> experiment_observations`

`backlog_items -> product_decisions`

Foreign keys enforce relationship integrity.

Check constraints enforce valid priority, lifecycle states, numeric ranges, and dates.

The `backlog_priority_score` function calculates the decision-support score inside PostgreSQL.

The `backlog_prioritization` view provides a reusable ranking query.

The `discovery_results` view calculates experiment averages and determines whether the observed result reaches the configured threshold.

The `sprint_consumed_capacity` function provides capacity accounting.

The `sprint_is_outcome_aligned` function evaluates whether all selected sprint items have reached the completed state.

## Database-Level Integrity

The SQL model deliberately pushes important rules into the database.

A backlog item entering `ready`, `in_progress`, or `done` must have discovery evidence.

A completed item cannot move backward.

A discovery item cannot skip directly to completion.

These rules are implemented with PostgreSQL triggers rather than relying exclusively on application code.

This matters because multiple applications could write to the same database. Database constraints and triggers provide a common integrity boundary.

## Transactional Sprint Planning

Sprint selection occurs inside a transaction.

The transaction inserts the selected backlog items into `sprint_backlog` and then transitions their states to `in_progress`.

If an integrity error occurs before the transaction commits, PostgreSQL can roll the operation back rather than leaving a partially committed sprint assignment.

This is important for product systems because sprint scope and backlog state represent a single business operation.

## Relationship Between the Mechanisms

The four primary concepts have different responsibilities.

    Product Goal
         |
         v
    Roadmap Outcome
         |
         v
    Continuous Discovery
         |
         v
    Product Backlog
         |
         v
    Sprint Goal
         |
         v
    Selected Work
         |
         v
    Observed Product Result
         |
         +------> New Discovery Evidence

The flow is not strictly linear in practice.

Discovery can invalidate a roadmap assumption.

New evidence can change backlog ordering.

A sprint can reveal technical or customer information that changes future backlog decisions.

A product goal can remain stable while individual roadmap outcomes or backlog items change.

## Edge Cases and Failure Conditions

The implementations validate several failure conditions:

- Duplicate identifiers
- Missing customer problems
- Invalid value or effort ranges
- Zero or negative effort
- Missing discovery evidence
- Invalid product-goal references
- Invalid sprint dates
- Zero or negative sprint capacity
- No backlog item fitting available capacity
- Completion of an item not selected for the sprint
- Invalid backlog state transitions
- Discovery observations outside the valid measurement range
- Experiments without valid thresholds
- Roadmap outcomes referencing unknown goals

These failures are treated as domain errors instead of silently producing inconsistent state.

## Product Decision Quality

A numerical prioritization score is useful for ordering candidates, but it has limits.

A high-scoring item can still be a poor product decision when:

- The underlying customer evidence is weak
- The problem is strategically irrelevant
- The solution has unacceptable operational risk
- A dependency is missing
- The expected outcome is not measurable
- Discovery has invalidated the underlying assumption
- Another opportunity has substantially greater strategic importance

The model therefore keeps discovery evidence, product goals, roadmap outcomes, and backlog attributes as separate concepts.

## Performance and Scaling Considerations

The in-memory implementations are appropriate for educational simulation and small product-planning tools.

Backlog ranking requires sorting and therefore has `O(n log n)` complexity.

Maps provide efficient keyed access for product goals, backlog items, sprints, experiments, and roadmap outcomes.

The PostgreSQL design adds indexes only where repeated relationship and filtering queries justify them.

For a larger product organization, additional concerns would include concurrent backlog edits, optimistic locking, audit histories, authorization, tenant isolation, immutable decision records, event publication, analytics pipelines, and more sophisticated prioritization models.

## Security and Governance Considerations

Product-management data can contain sensitive customer research, commercial assumptions, experiment results, and strategic plans.

A production system should therefore enforce:

- Authenticated access
- Role-based authorization
- Least-privilege database permissions
- Audit trails for important decisions
- Controlled modification of product goals
- Protection of customer research data
- Validation of externally supplied metrics
- Transactional consistency for multi-step changes

The examples validate domain input but do not attempt to implement a complete identity and access-control system.

## Practical Distinctions

The artifacts intentionally avoid collapsing product management into a single backlog.

A backlog answers what opportunities and work are available.

A roadmap communicates directional outcomes and timing.

A sprint goal establishes short-term focus.

Continuous discovery tests whether assumptions deserve continued investment.

These mechanisms work together because each resolves a different type of uncertainty:

| Concern | Primary mechanism |
|---|---|
| Strategic outcome | Product goal |
| Direction and timing | Roadmap |
| Available product work | Backlog |
| Short-term focus | Sprint goal |
| Customer and solution uncertainty | Continuous discovery |
| Evidence-based adjustment | Product decision |

The implementations preserve these distinctions while connecting them through explicit relationships, state transitions, capacity constraints, validation rules, and measurable outcomes.
