# Scrum: Roles, Events, Artifacts, and Sprint Execution

## Purpose and scope

Scrum is a lightweight framework for developing and sustaining products through iterative work, frequent inspection, and adaptation. A Scrum Team works toward a Product Goal, establishes a Sprint Goal for each Sprint, and creates a usable Increment that meets the Definition of Done.

Scrum is not simply a sequence of meetings. Its accountabilities, events, and artifacts form a connected system. The Product Owner establishes product priorities, the Scrum Master supports the effectiveness of Scrum, and Developers create the Increment. Events provide opportunities to inspect progress and adapt the work. Artifacts make the work and its current state visible.

This repository models a payment and banking reliability product. The examples cover Product Backlog refinement, Sprint Planning, daily coordination, stakeholder inspection, retrospective improvement, and delivery-state validation.

## Scrum accountabilities

| Accountability | Primary responsibility | Practical application |
|---|---|---|
| Product Owner | Maximizes product value and is accountable for effective Product Backlog management. | Orders payment-validation, audit-trail, and transaction-status work according to product needs. |
| Scrum Master | Establishes Scrum as defined in the Scrum Guide and supports team and organizational effectiveness. | Helps address impediments and improves the team's use of Scrum. |
| Developers | Create a usable Increment each Sprint and are accountable for planning and adapting their work. | Implement, test, integrate, and verify the payment-reliability functionality. |

These are accountabilities, not necessarily separate job titles. A Scrum Team is cross-functional and self-managing. Developers determine how to turn selected work into an Increment, while the Product Owner remains accountable for Product Backlog ordering.

The Scrum Master does not function as a conventional project manager who assigns every task. Likewise, the Product Owner does not unilaterally prescribe every technical implementation decision.

## The five Scrum events

The Sprint is the container for all other Scrum events. Each event has a distinct purpose, and the events should not be treated as interchangeable status meetings.

| Event | Purpose | Typical output or adaptation |
|---|---|---|
| Sprint | Creates a consistent period for achieving the Sprint Goal and producing an Increment. | A usable Increment and evidence about progress toward the Product Goal. |
| Sprint Planning | Establishes why the Sprint is valuable, what can be done, and how the selected work will be accomplished. | Sprint Goal and Sprint Backlog. |
| Daily Scrum | Gives Developers an opportunity to inspect progress toward the Sprint Goal and adapt their plan. | An updated plan for the next day's work. |
| Sprint Review | Inspects the Sprint outcome with stakeholders and considers changes to the product's future direction. | Feedback and potential Product Backlog adaptations. |
| Sprint Retrospective | Identifies ways to improve quality and effectiveness. | Concrete improvement actions. |

The simulation uses a ten-day Sprint and records each event. Its event ordering is a simplified implementation choice, not a claim that every real-world Scrum activity must occur in a fixed database transaction or that all discussions are limited to a single meeting.

### Sprint Planning

Sprint Planning addresses three connected questions:

- **Why is this Sprint valuable?** The Sprint Goal describes the outcome the team intends to achieve.
- **What can be done this Sprint?** Developers collaborate with the Product Owner to select appropriate Product Backlog Items.
- **How will the selected work get done?** Developers plan the work required to create an Increment that meets the Definition of Done.

The sample programs use estimated effort points and a capacity limit to demonstrate feasible selection. Their selection algorithms are teaching aids. They are not substitutes for team judgment, historical evidence, dependencies, uncertainty, or discussion of the Sprint Goal.

A capacity estimate does not guarantee delivery. If work remains incomplete at the end of a Sprint, it does not automatically become part of the Increment. The Product Owner and Developers reconsider the remaining work in the context of the Product Backlog and future planning.

### Daily Scrum

The Daily Scrum is a 15-minute event for Developers. Its purpose is to inspect progress toward the Sprint Goal and adapt the Sprint Backlog as necessary.

It is not required to use a fixed round-robin format in which every participant answers the same three questions. Developers can choose a structure that helps them coordinate and identify the most useful next actions.

The code records item-state changes and impediments. In practice, an impediment might be an unavailable test environment, missing payment-provider credentials, unclear acceptance conditions, or a dependency that prevents integration. Recording an impediment makes it visible, but recording alone does not resolve it.

### Sprint Review

The Sprint Review is a working session in which the Scrum Team and stakeholders inspect the outcome of the Sprint and discuss adaptations. It is not merely a presentation or a formal sign-off meeting.

For the banking scenario, stakeholders might inspect how malformed payment requests are rejected, whether audit events contain the necessary information, and whether the delivered functionality supports operational needs. Their feedback may change the ordering or content of the Product Backlog.

The simulation uses an explicit acceptance flag to illustrate the distinction between implemented work and work included in its modeled Increment. This is a simplified domain rule. In Scrum, the Definition of Done establishes the required state of the Increment, and the Sprint Review is not a gate that makes an otherwise incomplete Increment usable.

### Sprint Retrospective

The Sprint Retrospective focuses on improving quality and effectiveness. The team examines its interactions, processes, tools, assumptions, and working practices.

The sample improvements are deliberately specific:

- Prepare representative payment-failure test fixtures before development.
- Clarify audit-event acceptance criteria during backlog refinement.
- Identify integration dependencies before they block delivery.

A useful improvement action has an observable effect on how the team works. Recording an action without assigning appropriate ownership, reviewing progress, or checking its effect can reduce the retrospective to documentation rather than adaptation.

## The three Scrum artifacts

Scrum defines three artifacts, each with a commitment that supports transparency and focus.

| Artifact | Commitment | Meaning |
|---|---|---|
| Product Backlog | Product Goal | An ordered, evolving list of work needed to improve the product. |
| Sprint Backlog | Sprint Goal | The Sprint Goal, selected Product Backlog Items, and an actionable plan for delivering the Increment. |
| Increment | Definition of Done | A usable, integrated step toward the Product Goal that meets the Definition of Done. |

### Product Backlog

The Product Backlog is the single source of work undertaken by the Scrum Team. Its ordering changes as the team and stakeholders learn more about product value, risk, dependencies, and feasibility.

The sample items are `PAY-501`, `PAY-502`, and `PAY-503` in the SQL model. They represent payment validation, audit persistence, and transaction-status retrieval. Priority is used to demonstrate ordering, while estimates represent the team's relative assessment of effort.

Product Backlog refinement is an ongoing activity rather than a separate formal Scrum event. The team may clarify descriptions, break down items, identify dependencies, and improve acceptance conditions. The SQL acceptance-criterion table represents testable item-level conditions; it does not replace the team's Definition of Done.

### Sprint Backlog

The Sprint Backlog belongs to the Developers and evolves throughout the Sprint. It combines the Sprint Goal, selected Product Backlog Items, and the Developers' plan for delivering the work.

The code stores selected items and tracks states such as `TO_DO`, `IN_PROGRESS`, and `DONE`. These states are a simplified workflow model. Scrum itself does not prescribe these exact status names.

The Sprint Backlog is not a fixed contract that prevents adaptation. Developers can update their plan as they learn more, provided that changes do not endanger the Sprint Goal. The scope may be clarified and renegotiated with the Product Owner as necessary.

### Increment and Definition of Done

An Increment is a concrete step toward the Product Goal. It must be usable and meet the Definition of Done. Multiple Increments may be created during a Sprint, and the value of an Increment is not limited to the Sprint Review.

The simulation keeps completed work separate from the modeled accepted Increment. This supports a useful engineering distinction: code marked complete in a work tracker is not automatically proof that the product is integrated, tested, secure, and usable.

The Definition of Done should make required quality conditions explicit. For payment functionality, these might include automated tests, appropriate authorization checks, audit behavior, integration verification, and deployment readiness. The precise requirements depend on the product and its operational environment.

## Python implementation

The Python script models Scrum with dataclasses and enumerated work states.

`TeamMember` stores accountability information. `ProductBacklogItem` validates item identifiers, estimates, priorities, and acceptance criteria. `Sprint` stores its goal, duration, selected items, impediments, and event-completion state. `ScrumArtifacts` keeps the Product Backlog, Sprint Backlog, and modeled Increment distinct.

The `ScrumTeam` class provides operations for refinement, Sprint Planning, work transitions, Daily Scrum updates, Sprint Review, retrospective actions, and closure. The capacity-based selection logic considers ordered items and includes an item only when its estimate fits the remaining capacity.

The program also validates invalid state transitions and prevents a second Sprint from being planned while the current Sprint remains open. Unfinished selected items return to the Product Backlog state in this simplified model rather than being treated as completed delivery.

The simulation demonstrates partial delivery, a recorded impediment, stakeholder feedback, and improvement actions. It can be run with the standard Python runtime without third-party packages.

## JavaScript implementation

The JavaScript file models an event-driven Scrum board. `ScrumEventBus` separates event publication from event handling, allowing consumers to subscribe to Scrum events without coupling each listener to the core workflow.

`BacklogItem` validates the data required for a work item. `ScrumBoard` coordinates selection, work-state transitions, event recording, review behavior, and retrospective actions. Private methods restrict access to internal validation operations.

The implementation validates all requested Daily Scrum state changes before applying them. This reduces the chance of applying only part of a batch when one transition is invalid. Event listeners receive frozen event payload objects, and listeners are copied before dispatch so changes to the subscription list do not modify the current iteration.

This event-driven approach is useful when Scrum workflow events must be observed by dashboards, audit logging, or other application components. The demonstration remains an in-memory simulation: it does not provide durable event storage, distributed delivery guarantees, or concurrency control.

## C++ case study: banking delivery board

The C++ program models an online banking team delivering safer transfer functionality. The board stores team information, a Product Backlog, the modeled Increment, an event log, and improvement actions.

`BacklogItem` and `Sprint` represent the core domain. The board uses a vector to store backlog items, sorts that vector before selecting work, and keeps references to selected items for the active Sprint. The implementation deletes copying of the board to avoid accidental duplication of the owned Sprint pointer.

The work-transition operation permits only defined state changes. It rejects unknown items and attempts to move completed work into an invalid state. Sprint Review separates unfinished work from the Increment, while the closure operation checks that both the review and retrospective have been recorded.

The program illustrates several implementation trade-offs. A pointer-based simulation can avoid copying large work items, but it requires careful lifetime management. Sorting a vector after creating pointers into it could invalidate assumptions about item identity, so the example sorts before selecting references. A production implementation might use stable identifiers and value-based repositories instead of raw pointers.

The model has no persistent storage, authentication, distributed event processing, or transactional concurrency control. Its purpose is to demonstrate the domain behavior in a compiled C++17 program.

## Java implementation: enterprise Scrum service

The Java program uses explicit domain types and a service layer to model Scrum workflow for digital banking reliability.

`TeamMember`, `SprintGoal`, and `ScrumEvent` are records. `ProductBacklogItem` manages its own state and acceptance status. The `Sprint` class calculates planned and accepted points, while `ScrumService` coordinates team validation, backlog ordering, work transitions, event history, and Sprint lifecycle operations.

The constructor checks that the supplied members hold the expected accountabilities and that team names and backlog identifiers are unique. The service prevents Sprint Planning while an earlier Sprint remains open, checks event dates against the Sprint duration, and rejects review or retrospective operations that violate the modeled lifecycle.

The service uses defensive copies for developer lists and acceptance criteria. This protects the domain model from accidental external modification of those collections, although the model remains mutable through its explicit workflow methods.

For a production enterprise system, persistence, authorization, concurrent updates, audit retention, and integration with delivery pipelines would require additional design. The sample focuses on explicit domain rules and state transitions rather than framework configuration.

## PostgreSQL data model

The SQL implementation uses the `scrum_demo` schema to represent the same broad domain relationally.

| Table | Responsibility |
|---|---|
| `product` | Identifies the product whose backlog and team are being managed. |
| `team_member` | Stores team membership and Scrum accountabilities. |
| `sprint` | Records dates, duration, Sprint Goal, status, and event-completion flags. |
| `product_backlog_item` | Stores ordered work, estimates, and current workflow state. |
| `acceptance_criterion` | Stores item-specific testable conditions. |
| `sprint_backlog_item` | Associates selected items with a Sprint. |
| `increment_item` | Records the modeled Increment membership and acceptance notes. |
| `scrum_event` | Maintains a timeline of Scrum events. |
| `impediment` | Tracks impediments and their resolution. |
| `retrospective_action` | Records process-improvement actions and completion status. |

Primary keys identify records, foreign keys preserve relationships, and check constraints reject invalid estimates, priorities, dates, and empty names. Unique constraints prevent duplicate item keys within a product and duplicate Sprint numbers for the same product.

The partial unique indexes enforce one active Product Owner and one active Scrum Master per product in this teaching schema. They allow multiple Developers. A trigger validates that a Sprint Backlog Item and its Sprint belong to the same product because separate foreign keys would not enforce that cross-table rule by themselves.

The Increment trigger rejects work that is not marked `DONE` and requires all recorded acceptance criteria to be satisfied. The Sprint-closure trigger prevents a Sprint from entering the `CLOSED` state unless its review and retrospective flags are set.

These database rules are intentionally stricter than an unstructured work tracker. They illustrate how a database can prevent inconsistent states, but they do not establish a complete Definition of Done or guarantee that all Scrum activities were performed meaningfully.

The planning query uses a recursive common table expression to select a priority-ordered sequence of items that fits a points capacity. The query is a demonstration of capacity-aware selection, not an optimal planning algorithm. Greedy selection may leave capacity unused even when a different combination of items would fit better.

The reporting queries distinguish selected work from Increment membership, list remaining Product Backlog Items, identify unresolved impediments, and expose retrospective actions that still need attention.

## Important distinctions

### Scrum is not synonymous with Agile

Agile is a broad set of values and principles. Scrum is a specific framework that defines accountabilities, events, artifacts, and commitments. A team can use Agile practices without implementing Scrum, and calling a recurring meeting a Daily Scrum does not by itself establish that the team is following Scrum.

### Scrum roles and events serve different purposes

The Product Owner, Scrum Master, and Developers have different accountabilities. Sprint Planning, Daily Scrum, Sprint Review, and Sprint Retrospective have different purposes. Treating every event as a generic progress meeting removes the inspection and adaptation each event is intended to support.

### Completion and Increment readiness are different

A work item's tracker status is not the same as an Increment's readiness. An item can be coded but not integrated, tested, or compliant with the Definition of Done. The Increment should reflect the actual required quality state, not merely a label in a board.

### Capacity is not a delivery guarantee

Estimates and capacity help Developers create a realistic plan. They do not provide certainty about the Sprint outcome. Unexpected defects, dependencies, operational incidents, and new learning can change the amount of work completed.

## Edge cases and production considerations

- **Empty or malformed backlog items:** The examples reject missing identifiers, invalid priorities, negative estimates, and missing acceptance criteria. Real systems should also define how to handle changes to an item's estimate or acceptance conditions after planning.
- **Work that does not fit capacity:** A selection algorithm should not silently exceed the stated limit. A greedy algorithm is easy to understand but does not optimize every possible combination.
- **Incomplete work:** Work that does not meet the Definition of Done should not be represented as part of the Increment. It remains visible for subsequent Product Backlog ordering.
- **Repeated events:** The sample services reject duplicate reviews and retrospectives. Production audit systems should also define idempotency behavior for repeated network requests.
- **Concurrent updates:** In-memory state transitions are not sufficient for multiple users updating the same item simultaneously. A persistent service may need transactions, row locking, or optimistic version checks.
- **Event durability:** An in-memory event list is lost when the program terminates. A production system should store event history durably and define retention and access controls.
- **Acceptance criteria:** The examples validate recorded criteria, but a real system must establish who can verify them and how test evidence is captured. Acceptance criteria and the Definition of Done serve related but distinct purposes.
- **Retrospective actions:** Recording an improvement is not evidence that it was completed or effective. Follow-up should make ownership, due dates, and outcomes visible without turning the retrospective into an administrative checklist.

## Performance and integrity

The in-memory implementations use straightforward list or vector scans to locate items and order backlogs. These choices are appropriate for small demonstrations, but lookup and sorting costs grow with backlog size.

The PostgreSQL indexes support common access patterns such as ordering backlog items by priority, reading events chronologically, finding unresolved impediments, and listing unfinished retrospective actions. Indexes have storage and write-maintenance costs, so they should correspond to actual query patterns.

Database constraints and triggers protect integrity at the persistence boundary. Application validation still matters because it can produce clearer error messages and reject invalid requests before a database operation. The two layers serve complementary purposes.

For a real Scrum-support system, workflow rules should be reviewed against the team's actual policies and the Scrum framework. The application should preserve transparency and enable adaptation rather than force every team into an inflexible sequence of task statuses.
