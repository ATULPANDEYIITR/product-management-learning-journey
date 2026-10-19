# Kanban: Principles, Workflow Visualization, WIP Limits, and Throughput

## Topic Scope

Kanban is a flow-management method built around visualizing work, limiting work in progress, pulling work when capacity exists, and measuring how work moves through a system.

These four areas are closely related but represent different mechanisms:

- **Kanban principles** define how work should be managed as a flow system. The central operational idea in these implementations is to make current work visible, control how much is active, and improve flow from observed evidence.
- **Workflow visualization** represents the actual states through which work moves. The examples use stages such as `Backlog`, `Ready`, `Development`, `Review`, `Testing`, and `Done`.
- **WIP limits** constrain the amount of active work occupying selected stages. A full downstream stage prevents additional work from being pulled into it.
- **Throughput** measures completed work over a defined period. It is different from the amount of work currently in progress.

The implementations deliberately use different perspectives. Python provides a teaching-oriented flow simulator, JavaScript models event-driven movement, C++ implements a governance-style flow engine, Java models an enterprise domain, and PostgreSQL represents the same operational concepts as relational data and database constraints.

## Core Kanban Model

A Kanban system can be viewed as a sequence of states:

`Backlog → Ready → Development → Review → Testing → Done`

The exact columns are not universal. They represent a workflow in which work changes state as it progresses toward completion.

The important property is that a column represents a meaningful state of the work rather than merely a category used for reporting.

For example, `Development` indicates that implementation work is active. `Review` indicates that the implementation has reached a review stage. `Testing` indicates that the work is being validated. `Done` represents completed flow.

The distinction matters because WIP limits and flow metrics operate on these states.

## Kanban Principles Demonstrated

The programs model several practical principles directly.

### Visualize the workflow

The board stores the current stage of every work item. A board snapshot therefore represents the current distribution of work rather than a static task list.

The Python `KanbanBoard.snapshot()` method returns the number of items in every column. The JavaScript implementation exposes the same operational state through `snapshot()`, while the SQL `current_wip` view produces a database representation of column occupancy.

### Manage flow rather than maximize activity

Starting additional work is not automatically productive. When a downstream stage is full, pushing another item into the system can increase WIP without increasing completion capacity.

The implementations therefore use pull behavior. A new item is selected only when the destination stage has available capacity.

This is particularly visible when `Development` has room but `Review` has reached its WIP limit. The review stage becomes a flow constraint rather than a reason to start unlimited additional development work.

### Make blocked flow visible

A rejected movement is useful operational information.

The Python simulator raises a policy error when a destination WIP limit is full. JavaScript emits a `blocked` event. C++ reports the blocked transition directly. Java represents the same condition as a failed service operation.

This is preferable to silently accepting additional work and hiding the resulting queue.

### Improve using flow evidence

Cycle time, throughput, WIP, and aging work provide measurable evidence about system behavior.

An increase in WIP without corresponding throughput growth can indicate congestion. A consistently full review column can indicate a review bottleneck. A rapidly aging item can indicate blocked work even when the total WIP appears acceptable.

## Workflow Visualization

The board is not simply a visual checklist. Its columns represent states and its transitions represent movement through the workflow.

A useful interpretation of the example workflow is:

`Backlog`
→ work has been identified but is not yet ready to enter active flow.

`Ready`
→ work is eligible for selection when downstream capacity becomes available.

`Development`
→ implementation is actively consuming development capacity.

`Review`
→ completed implementation work is waiting for or undergoing review.

`Testing`
→ the work is being validated before completion.

`Done`
→ the work has completed the modeled workflow.

The distinction between `Ready` and `Development` is important. Ready work does not consume development WIP. Moving an item into Development starts active cycle time in the supplied implementations.

The Python `WorkItem` records transitions in a history list. JavaScript records timestamps for each movement. Java uses immutable `Transition` records. PostgreSQL stores transitions in `work_item_transitions`.

This makes the board auditable rather than merely representing the latest state.

## Pull-Based Movement

A pull system starts work because a downstream stage can accept it.

The Python `pull_next()` method checks destination capacity before selecting the highest-priority eligible item. The JavaScript `pullOldest()` method uses the same principle but expresses movement through event-driven operations. C++ performs selection through `pull()`. Java implements the operation through `KanbanBoard.pull()`.

The important distinction is between **selection** and **capacity**.

A work item may be the highest-priority item in `Ready`, yet remain there if the destination is full.

That behavior prevents priority from overriding physical or operational capacity.

## WIP Limits

WIP means work in progress.

A WIP limit applies to a workflow stage and specifies how many items may occupy that stage at once.

For example, the Python simulation uses:

- Development: 3
- Review: 2
- Testing: 2

The JavaScript model deliberately makes Review tighter with a limit of 1 so that downstream congestion is easy to observe.

A WIP limit is not a target that teams should try to fill constantly. It is a constraint on active work.

When a stage is full, the correct response is generally to address the constraint or pull work elsewhere rather than treating the limit as something to ignore.

### WIP and bottlenecks

Suppose Development has capacity for another item but Review is full.

Starting another development item can increase the number of active items without increasing the rate at which work reaches Done.

The system can therefore exhibit:

`More Development WIP → Full Review → Longer queues → Higher cycle time`

The implementations expose this relationship through explicit movement failures.

## Throughput

Throughput is the rate at which work reaches completion.

A simple definition is:

`Throughput = completed work / observation period`

The Python implementation counts items whose `completed_at` timestamps fall inside a measurement window.

The C++ implementation reports completed items over a seven-day observation model.

The PostgreSQL `daily_throughput` view groups completed work by completion day.

This avoids a common measurement mistake: counting started work as delivered work.

If ten items are started but only four reach `Done`, throughput for the period is based on four completed items.

## Cycle Time and Lead Time

The Python implementation distinguishes two useful measurements.

**Lead time** is measured from item creation to completion.

**Cycle time** is measured from entry into active work to completion.

The distinction is important because an item can spend significant time waiting before active work begins.

For example:

`Created → Ready → Development → Review → Testing → Done`

Lead time covers the entire interval from creation to Done.

Cycle time begins when the item enters Development in these examples.

A team can therefore reduce cycle time while still having a long lead time if work spends substantial time waiting before entering active flow.

## Little's Law

The implementations use the relationship:

`WIP = Throughput × Cycle Time`

Rearranging gives:

`Cycle Time = WIP / Throughput`

The Python example uses an average WIP of 6 items and throughput of 2 items per day, producing an estimated cycle time of 3 days.

The C++ and Java programs also expose Little's Law as a calculation rather than treating it as a purely theoretical statement.

The relationship is most useful when the measurements describe a reasonably stable system over a meaningful observation period. It should not be interpreted as a guarantee that any individual work item will finish within the calculated average.

## Python Implementation

The Python implementation is a complete workflow simulator.

`WorkItem` stores identity, priority, timestamps, current stage, and transition history. `KanbanPolicy` stores WIP limits and determines whether a destination has capacity. `KanbanBoard` owns the work items and implements capacity-aware movement.

The `pull_next()` operation demonstrates the pull mechanism. It first checks the destination's WIP limit and then selects an eligible item using priority followed by creation time.

The simulator deliberately creates a full Development stage and attempts another pull. The blocked operation demonstrates that a WIP limit prevents additional active work.

It then moves an item downstream, creating Development capacity, and pulls another Ready item into Development.

`FlowMetrics` separates throughput, cycle time, and lead time. The implementation also reports blocked columns and aging work, which makes congestion visible rather than reducing Kanban to a board display.

## JavaScript Implementation

The JavaScript implementation emphasizes event-driven flow.

`EventBus` provides subscription and event publication. The board emits `moved`, `blocked`, and `itemAdded` events rather than requiring every caller to inspect state after every operation.

This is useful for a web application because a user interface can react to board events without tightly coupling rendering logic to the workflow engine.

The `waitForCapacity()` function uses asynchronous execution to model a downstream capacity opportunity becoming available later.

The implementation also separates `agingReport()` from ordinary board snapshots. A snapshot describes current WIP, while aging information identifies active items that may be accumulating excessive waiting or cycle time.

The JavaScript implementation therefore demonstrates a natural connection between Kanban flow and event-driven application architecture.

## C++ Case Study

The C++ program models a technical delivery board for services such as Payments, Observability, Database, and Security.

`GovernanceBoard` owns work items and WIP policy. Its `pull()` operation selects eligible work according to priority and creation time, while `move()` enforces destination capacity.

The program deliberately creates a Review bottleneck. Development is allowed to contain three items, while Review allows only two. Moving work into Review consumes downstream capacity and exposes the effect of a constrained stage.

The implementation uses `std::unordered_map` for direct item lookup and a temporary vector of pointers for selecting candidate work. Candidate selection is ordered by priority and then creation time.

The model uses `std::optional<TimePoint>` for timestamps that do not exist until an item enters active flow or reaches Done.

The case study also calculates a flow report and demonstrates Little's Law.

## Java Enterprise Model

The Java implementation uses explicit domain abstractions.

`Stage` represents workflow state and `Priority` represents selection urgency. `Transition` is a Java record that provides an immutable representation of a state movement.

`WorkItem` owns domain state and transition history. `WipPolicy` owns capacity rules, separating policy from the board itself.

`KanbanBoard` acts as the workflow service. It validates item identity, counts stage occupancy, performs capacity-aware moves, and exposes pull operations.

The `FlowMetric` interface allows metrics to be modeled as replaceable strategies. `AverageCycleTime` is one implementation that calculates active cycle duration from completed work.

This structure is useful in enterprise systems because domain policy does not have to be embedded into a large collection of unrelated conditional statements.

## Relational Data Model

The PostgreSQL implementation separates several concepts that are often incorrectly collapsed into one table.

`repositories` identifies the systems whose workflows are being managed.

`board_columns` defines the ordered workflow and its WIP policy.

`work_items` stores the current state and core timestamps.

`work_item_transitions` records historical movement.

`flow_observations` stores measured flow data for later analysis.

The relationship is therefore:

`Repository → Board Columns`

`Repository → Work Items`

`Work Item → Transition History`

`Repository → Flow Observations`

This separation allows current state and historical flow behavior to be queried independently.

## Database-Level Integrity

The SQL model uses PostgreSQL constraints to protect domain invariants.

The `CHECK` constraints prevent a completed timestamp from being associated with a non-`done` item and prevent completion from occurring before active work begins.

Foreign keys ensure that work items belong to existing repositories and that transition records refer to existing work items.

The unique constraint on `(repository_id, item_key)` prevents duplicate work identifiers within one repository.

These constraints are important because WIP and flow analytics become unreliable if the underlying state is internally inconsistent.

## SQL WIP Analysis

The `current_wip` view counts items in each workflow stage and joins those counts to configured WIP limits.

It exposes:

- current WIP
- configured WIP limit
- whether the stage is at capacity

The utilization query then calculates the percentage of a constrained stage that is occupied.

A Review column at 100% utilization is materially different from a Ready column containing many items. Ready work represents demand waiting for capacity, while a full Review stage represents a downstream constraint.

## SQL Transactions

The PostgreSQL script contains a transaction that attempts to pull `PAY-104` from Ready into Development.

The update is permitted only when the current Development count is below its configured limit.

This demonstrates an important database principle: an application can calculate capacity, but database-side conditions can also participate in protecting state changes.

For a production system with concurrent workers, this basic example would need stronger concurrency controls such as appropriate row locking or serializable transaction design. Otherwise two simultaneous transactions could make decisions from the same stale capacity observation.

## Flow History

Current state alone cannot explain how a work item reached that state.

For example, an item currently in Review could have entered Review immediately or could have spent several days in Development.

`work_item_transitions` therefore preserves movement history.

The same principle appears in the Python, JavaScript, and Java implementations through in-memory transition histories.

Historical transitions make it possible to calculate stage-specific waiting time, identify repeated movement, and investigate where work spends the most time.

## Aging Work

Aging is a useful signal for active items.

An item with high age may indicate:

- an external dependency;
- excessive queue time;
- insufficient downstream capacity;
- an unexpectedly large work item;
- repeated rework;
- a process constraint.

The Python and JavaScript implementations expose aging information directly.

Aging should not be confused with throughput. An old item is a property of current unfinished work, while throughput measures completed work.

## Bottleneck Behavior

A bottleneck is a stage whose effective capacity restricts the flow of the system.

If Review can process only one item while Development can produce three, Review can become the limiting stage.

The consequences can propagate upstream:

`Review capacity ↓`

`Development completion into Review ↓`

`Development remains occupied ↑`

`Ready queue grows ↑`

`Cycle time ↑`

This is why increasing the WIP limit of every column independently is not necessarily an improvement. Increasing WIP can hide the visible symptom while allowing more work to accumulate around the true constraint.

## Performance Considerations

The in-memory implementations use simple scans for counting WIP. This is appropriate for small teaching simulations but would become inefficient for very large boards.

The Python implementation uses dictionaries for direct item lookup but scans the items when counting stage occupancy.

The JavaScript implementation uses a `Map` for item lookup and scans active items for snapshots and aging reports.

The C++ implementation uses `unordered_map` for identity lookup and sorts candidate work during selection.

The SQL implementation uses indexes on repository and stage, completion timestamps, transition history, and observation timestamps because these columns support the principal flow queries.

For a production implementation, frequently requested WIP counts could be maintained incrementally or derived through carefully indexed queries depending on concurrency and consistency requirements.

## Common Mistakes

### Treating WIP limits as quotas

A WIP limit of three does not mean a team should always keep exactly three items in Development.

The limit represents the maximum active work allowed by the policy. If there is no suitable work, the correct WIP can be lower.

### Starting work whenever a person becomes available

Kanban focuses on system flow rather than local utilization.

A developer becoming free does not necessarily justify starting another item if Review or Testing is already saturated.

The available capacity may be better used to help clear the existing constraint.

### Measuring activity instead of delivery

The number of items moved into Development is not throughput.

Throughput requires completion.

### Ignoring aging

A board with acceptable total WIP can still contain an item that has been blocked for an unusually long time.

Age and cycle-time distributions provide information that a simple WIP count cannot.

### Changing WIP limits without examining flow

A limit should be treated as an operational control.

Increasing a limit can reduce visible blocking while increasing queues, cycle time, and unfinished work.

The effect should be evaluated using actual flow measurements.

## Practical Distinctions

| Concept | Primary question | Implementation representation |
|---|---|---|
| Kanban principles | How should work be managed as a flow system? | Pull behavior, visibility, explicit policy, flow measurement |
| Workflow visualization | Where is each work item now? | Board stages and transition history |
| WIP limits | How much active work may occupy a stage? | Capacity constraints per stage |
| Throughput | How much work is actually completing? | Completed items per observation period |
| Cycle time | How long does active work take? | Start-to-completion duration |
| Lead time | How long does demand wait from creation to completion? | Creation-to-completion duration |
| Aging | Which unfinished items may be stuck or slow? | Current age of active items |
| Bottleneck | Which stage constrains system flow? | Persistent capacity saturation and downstream blockage |

## Production Considerations

A production Kanban system needs reliable timestamps, durable transition history, explicit definitions for each workflow state, and carefully defined policies for exceptional work.

Expedited work should not silently bypass every flow rule. If expedited work is allowed, its capacity impact should be visible and measurable.

WIP limits should also be defined at the correct level. A team-wide limit may be insufficient when individual stages such as review or testing have materially different capacities.

Concurrent updates require special attention. Two workers attempting to pull work simultaneously must not both observe the same available capacity and then exceed a WIP limit. Database transactions, row locking, optimistic concurrency, or serialized workflow operations may be necessary depending on the architecture.

The most useful Kanban system is therefore not the one with the most columns or the most dashboard metrics. It is the one in which the workflow is visible, active work is deliberately constrained, blocked flow is observable, and throughput and cycle time provide evidence for improving the system.
