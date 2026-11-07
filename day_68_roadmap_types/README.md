# Roadmap Types: Feature, Outcome, Theme, and Now-Next-Later

## 1. Overview

A product roadmap communicates the direction, priorities, and intended progression of a product or strategic initiative.

Different roadmap types answer different management questions. A feature roadmap describes planned capabilities, an outcome roadmap describes measurable improvements, a theme roadmap organizes investment around strategic objectives, and a Now-Next-Later roadmap communicates priorities through relative planning horizons.

These approaches are not interchangeable. Their usefulness depends on the planning decision, organizational maturity, uncertainty, and level of detail required.

The five implementation files demonstrate how roadmap information can be represented, validated, prioritized, evaluated, and stored.

## 2. Roadmap Domain Model

The implementations use a common conceptual structure.

| Entity | Responsibility |
|---|---|
| Roadmap | Defines the planning model and its scope |
| Roadmap item | Represents a feature, outcome, theme-aligned initiative, or horizon commitment |
| Theme | Represents a strategic investment area |
| Metric | Measures an intended outcome |
| Dependency | Represents an execution relationship |
| Owner | Identifies delivery or strategic accountability |
| Priority | Represents relative importance |
| Status | Represents the lifecycle state |
| Horizon | Represents relative planning proximity |
| Confidence | Represents confidence in the current assessment |

A roadmap item has a stable identifier, title, description, owner, priority, and status.

Its additional attributes depend on the roadmap type.

For example:

- A feature item describes a product capability.
- An outcome item requires a measurable metric.
- A theme item can be associated with a strategic theme.
- A Now-Next-Later item requires a planning horizon.

The implementations enforce these distinctions through validation rules rather than treating all roadmap entries as identical records.

## 3. Feature Roadmap

### 3.1 Definition

A feature roadmap organizes planned product capabilities and functional improvements.

It communicates what product capabilities are expected to be delivered and how those capabilities relate to one another.

A feature roadmap commonly contains:

- Feature names.
- Functional descriptions.
- Product areas.
- Priority levels.
- Owners.
- Dependencies.
- Delivery status.
- Target dates.
- Release associations.

### 3.2 Example

| Feature | Priority | Owner | Status |
|---|---|---|---|
| Multi-factor authentication | Critical | Security | Completed |
| Customer analytics dashboard | High | Product | In progress |
| Notification preferences | Medium | Product | Proposed |

The example represents a customer platform undergoing capability development.

Authentication is a prerequisite for the analytics dashboard in the sample dependency model.

The dependency relationship means that analytics cannot enter execution until authentication is completed.

### 3.3 Feature roadmap workflow

The typical workflow is:

1. Identify a product capability.
2. Describe its intended functionality.
3. Assign an accountable owner.
4. Assess priority and dependencies.
5. Add the capability to the roadmap.
6. Track its status and progress.
7. Update delivery information as circumstances change.
8. Evaluate whether the capability remains strategically relevant.

A feature roadmap is particularly useful when stakeholders need visibility into product scope and delivery coordination.

### 3.4 Limitations

Feature completion does not establish product success.

A feature may be delivered successfully without improving customer experience, reducing operating costs, or increasing business value.

Feature roadmaps can also create premature delivery commitments when estimates and release dates are uncertain.

For these reasons, feature progress should not be treated as a substitute for outcome measurement.

## 4. Outcome Roadmap

### 4.1 Definition

An outcome roadmap organizes product investments around measurable changes in customer or business performance.

Rather than beginning with a list of requested features, it begins with the improvement that the organization intends to achieve.

Typical outcome categories include:

- Customer satisfaction.
- Customer retention.
- Revenue improvement.
- Operational efficiency.
- Reduced service response time.
- Increased adoption.
- Reduced failure rates.
- Improved employee productivity.

### 4.2 Outcome and output distinction

An output is something an organization delivers.

An outcome is the measurable effect of that delivery.

| Dimension | Output | Outcome |
|---|---|---|
| Focus | Delivered capability | Achieved improvement |
| Example | Onboarding automation | Reduced onboarding duration |
| Measurement | Features completed | Average processing time |
| Accountability | Delivery progress | Business or customer impact |
| Evidence | Release records | Metric observations |

Delivering onboarding automation does not automatically establish that onboarding has become faster.

The outcome must be measured independently.

### 4.3 Metric structure

The implementations represent outcome metrics using four principal values:

| Field | Meaning |
|---|---|
| Baseline | Starting measurement |
| Target | Desired measurement |
| Current | Latest observed measurement |
| Unit | Measurement unit |

Example:

| Attribute | Value |
|---|---:|
| Metric | Average onboarding duration |
| Baseline | 10 days |
| Target | 4 days |
| Current | 5 days |
| Progress | 83.33% |

The progress calculation is:

\[
Progress =
\frac{Current-Baseline}{Target-Baseline}
\times 100
\]

For a metric where lower values are better, such as processing time, this formula still correctly measures movement from the baseline toward the target.

The implementation limits reported progress to the interval from 0% to 100%.

This is a planning indicator, not a complete statistical assessment of business performance.

### 4.4 Metric edge cases

Several cases require special handling:

- Baseline and target are identical.
- Current performance is worse than baseline.
- Current performance exceeds the target.
- A metric has not yet been measured.
- A measurement is missing or invalid.
- The target changes during the planning period.

The Python, JavaScript, C++, and Java implementations validate metric values and handle zero-distance targets.

The PostgreSQL implementation uses numeric types and database constraints to prevent negative measurements.

### 4.5 Outcome evaluation

An outcome roadmap should be evaluated through periodic measurement.

A useful operational cycle is:

**Baseline → Target → Intervention → Measurement → Evaluation → Adjustment**

The metric records should preserve measurement dates and, in a production implementation, should be extended with historical observations.

A single current-value field cannot independently establish the trend, seasonality, attribution, or statistical significance of an improvement.

## 5. Theme Roadmap

### 5.1 Definition

A theme roadmap organizes initiatives around strategic areas of investment.

A theme expresses a broad organizational direction rather than a specific feature or delivery commitment.

Examples include:

- Trust and Security.
- Operational Excellence.
- Customer Experience.
- Platform Modernization.
- Data Accessibility.
- Reliability and Resilience.

Themes allow several initiatives to contribute toward a shared strategic objective.

### 5.2 Theme hierarchy

The relationship is:

Strategic objective
  |
  +-- Strategic theme
        |
        +-- Initiative A
        |
        +-- Initiative B
        |
        +-- Initiative C

Example:

| Strategic theme | Objective | Initiative |
|---|---|---|
| Trust and Security | Improve platform security | Centralized audit logging |
| Operational Excellence | Improve operational efficiency | Process automation |

The theme describes the strategic investment area.

The initiatives describe the work undertaken to support it.

### 5.3 Theme governance

A theme should have:

- A clearly defined name.
- A strategic objective.
- An accountable owner.
- Associated initiatives.
- A lifecycle state.
- A method of evaluating strategic contribution.

A theme should not become an unrestricted category for grouping unrelated tasks.

The PostgreSQL implementation associates each theme with a roadmap and prevents an item from referencing a theme belonging to another roadmap.

It also distinguishes active, paused, and retired themes.

### 5.4 Strategic alignment

Theme alignment helps portfolio managers understand how resources are distributed across strategic priorities.

Useful reporting questions include:

- How many initiatives support each theme?
- How many initiatives have been completed?
- Which themes contain blocked initiatives?
- Which strategic areas have excessive investment?
- Which themes lack measurable evidence of contribution?

A theme with many completed initiatives is not necessarily successful. Its strategic objective must still be evaluated.

## 6. Now-Next-Later Roadmap

### 6.1 Definition

A Now-Next-Later roadmap organizes priorities into three relative planning horizons.

It is designed to communicate direction without requiring every initiative to have a fixed delivery date.

| Horizon | Meaning | Planning characteristics |
|---|---|---|
| Now | Current priority | Active focus and near-term execution |
| Next | Upcoming priority | Expected to follow current work |
| Later | Future opportunity | Requires further discovery or prioritization |

### 6.2 Example

| Now | Next | Later |
|---|---|---|
| Resolve payment failures | Improve business reporting | Predictive capacity planning |
| Stabilize authentication | Improve customer analytics | Advanced automation |
| Fix critical defects | Simplify onboarding | New platform capabilities |

The columns describe relative planning proximity, not guaranteed calendar dates.

### 6.3 Planning rules

A well-managed horizon roadmap should follow several principles:

- The Now column should contain a manageable amount of active work.
- Next should represent the most relevant upcoming priorities.
- Later should contain opportunities that may require discovery.
- Items should move between horizons as evidence and capacity change.
- Horizon placement should not imply a fixed release date.
- Changes should be communicated to affected stakeholders.

### 6.4 Horizon movement

The sample implementations support moving items between horizons.

For example:

**Now → Next**

A payment initiative may move from Now to Next when a dependency or external constraint changes its execution priority.

The movement is a planning decision. It does not mean that the underlying feature has been completed or that its business outcome has been achieved.

### 6.5 Advantages and limitations

Advantages:

- Simple stakeholder communication.
- Reduced emphasis on speculative delivery dates.
- Easier reprioritization.
- Useful for uncertain product environments.
- Clear distinction between current and future focus.

Limitations:

- Horizon definitions can become inconsistent.
- Large Now columns weaken prioritization.
- Stakeholders may interpret horizons as commitments.
- Dependencies can complicate movement.
- Relative ordering does not establish delivery capacity.

## 7. Distinguishing the Four Roadmap Types

| Dimension | Feature | Outcome | Theme | Now-Next-Later |
|---|---|---|---|---|
| Primary focus | Capabilities | Measurable impact | Strategic direction | Relative priority |
| Main question | What will be built? | What will improve? | Why are we investing? | When is work relatively prioritized? |
| Main unit | Feature | Outcome | Theme | Horizon |
| Measurement | Delivery status | Performance metrics | Strategic contribution | Horizon distribution |
| Typical audience | Product and engineering | Business and product leadership | Portfolio leadership | Cross-functional stakeholders |
| Main risk | Feature completion mistaken for success | Weak measurement | Vague strategic alignment | Implied date commitments |

The four models can coexist within an organization.

A strategic theme may contain several desired outcomes, each supported by multiple features. Those features can subsequently be organized into Now, Next, and Later horizons.

A conceptual relationship is:

Strategic theme
  |
  +-- Desired outcome
        |
        +-- Supporting feature A
        +-- Supporting feature B
        +-- Supporting feature C

Planning horizons can then organize the timing and relative priority of those features.

This relationship describes complementary planning perspectives, not a mandatory hierarchy.

## 8. Shared Roadmap Lifecycle

The implementations use a common lifecycle:

**Proposed → Planned → In Progress → Completed**

An item can also become Blocked or Cancelled.

| Status | Meaning |
|---|---|
| Proposed | Identified but not formally committed |
| Planned | Accepted into the planning process |
| In Progress | Execution has started |
| Blocked | A constraint prevents progress |
| Completed | Defined delivery work has finished |
| Cancelled | The initiative has been discontinued |

The lifecycle is distinct from outcome measurement and planning horizons.

For example, an item can be:

- In progress and assigned to Now.
- Planned and assigned to Next.
- Proposed and assigned to Later.
- Completed while its associated outcome remains below target.

The implementations prevent terminal items from being changed through ordinary status operations.

A production system may introduce explicit reopening, cancellation approval, and archival workflows with separate permissions.

## 9. Dependencies and Execution Control

### 9.1 Dependency model

A dependency identifies a prerequisite relationship between roadmap items.

If item B depends on item A, item A must be completed before item B enters execution.

A dependency graph can be represented as:

Authentication
      |
      v
Customer analytics
      |
      v
Advanced reporting

The Python, JavaScript, C++, and Java programs implement graph traversal using depth-first search.

A three-state traversal identifies:

- Unvisited nodes.
- Nodes currently being explored.
- Fully explored nodes.

Reaching a node that is already being explored indicates a cycle.

### 9.2 Complexity

For a dependency graph containing V items and E dependency relationships:

\[
Time = O(V+E)
\]

\[
Space = O(V+E)
\]

This is appropriate for ordinary product roadmap dependency graphs.

The SQL implementation uses recursive common table expressions to detect circular dependency paths.

### 9.3 Execution eligibility

An item is eligible for execution when:

- It exists.
- It is not completed.
- It is not cancelled.
- All prerequisite items are completed.

The PostgreSQL `item_is_eligible` function evaluates these conditions.

This eligibility check is not equivalent to a full resource-capacity or business-priority assessment.

## 10. Prioritization and Confidence

Priority communicates relative importance.

The implementations define four levels:

| Priority | Meaning |
|---|---|
| Critical | Essential or urgent |
| High | Strong strategic or operational importance |
| Medium | Meaningful but not urgent |
| Low | Lower relative priority |

Confidence represents how strongly the organization believes in the current assessment.

The Java implementation demonstrates a policy-based prioritization mechanism:

\[
Score = PriorityWeight \times Confidence
\]

The Python, C++, and JavaScript implementations also sort using priority and confidence.

This is a simplified decision-support mechanism.

It does not replace a complete prioritization framework involving customer value, strategic alignment, implementation effort, cost of delay, dependencies, risk, and available capacity.

A production scoring policy should define consistent measurement scales and prevent false precision.

## 11. Python Implementation

### 11.1 Architecture

The Python implementation uses dataclasses and enums to represent the roadmap domain.

| Component | Responsibility |
|---|---|
| `RoadmapItem` | Represents a roadmap initiative |
| `Metric` | Stores outcome measurements |
| `Theme` | Stores strategic alignment |
| `Roadmap` | Manages roadmap state |
| `RoadmapType` | Distinguishes roadmap models |
| `ItemStatus` | Represents lifecycle states |
| `Horizon` | Represents planning proximity |
| `Priority` | Represents relative importance |

### 11.2 Implemented mechanisms

The script includes:

- Item creation and validation.
- Dependency graph validation.
- Cycle detection.
- Status transitions.
- Dependency-aware execution.
- Progress updates.
- Outcome metric evaluation.
- Feature prioritization.
- Strategic theme relationships.
- Now-Next-Later reporting.
- JSON export.
- Automated assertions.

The `defaultdict` data structure supports graph traversal and status aggregation.

The `set` data structure prevents duplicate dependency identifiers.

The JSON export writes to a temporary file before replacing the destination file, reducing the risk of leaving a partially written export.

### 11.3 Execution

Requirements:

- Python 3.10 or later.
- Standard library only.

The program can be executed directly as a Python script.

It creates a JSON export under the `roadmaps` directory and executes validation tests.

## 12. JavaScript Implementation

### 12.1 Architecture

The JavaScript implementation uses Node.js standard-library features and an event-driven architecture.

| Component | Responsibility |
|---|---|
| `RoadmapEngine` | Manages roadmap state |
| `RoadmapItem` | Validates and represents items |
| `Map` | Maintains indexed entities |
| `Set` | Maintains dependencies and tags |
| `EventEmitter` | Publishes roadmap lifecycle events |
| `Promise.all` | Executes independent metric evaluations concurrently |
| `crypto.randomUUID()` | Generates item identifiers |
| `fs/promises` | Provides asynchronous persistence |

### 12.2 Event-driven behavior

The engine emits events such as:

- `item:created`
- `item:status-changed`
- `item:horizon-changed`
- `metric:updated`
- `theme:created`

An external application can subscribe to these events to update dashboards, generate audit messages, or notify stakeholders.

Event listeners should be designed to handle failures independently. A production event architecture may require durable event storage and retry handling.

### 12.3 Optimistic concurrency

Every roadmap item maintains a version.

An update can provide the version originally retrieved.

If another operation changes the item before the update is applied, the version check rejects the stale operation.

This prevents silent overwriting in concurrent editing scenarios within the engine's in-memory state.

It does not provide distributed locking or durable concurrency control across multiple application instances.

### 12.4 Asynchronous evaluation

Outcome evaluation uses promises.

Independent metric evaluations can execute concurrently instead of being evaluated sequentially.

The engine also uses asynchronous file operations to persist JSON records.

### 12.5 Execution

Requirements:

- Node.js 18 or later.
- No npm packages required.

Run the JavaScript file using Node.js.

The application writes a JSON roadmap export to the `roadmaps` directory.

## 13. C++17 Implementation

### 13.1 Architecture

The C++ implementation emphasizes domain modeling, explicit validation, and efficient in-memory operations.

| Component | Responsibility |
|---|---|
| `Roadmap` | Manages the planning domain |
| `RoadmapItem` | Represents individual initiatives |
| `Metric` | Represents an outcome measurement |
| `Theme` | Represents a strategic theme |
| `unordered_map` | Provides indexed item lookup |
| `set` | Stores unique dependencies and tags |
| `vector` | Stores sortable roadmap records |
| `optional` | Represents attributes that may not apply |

### 13.2 Design decisions

`optional` distinguishes between absent values and actual values.

For example, a feature item does not require an outcome metric.

An outcome item requires a metric.

A Now-Next-Later item requires a horizon.

The implementation uses references for item updates and value-based domain structures for straightforward state management.

The dependency validator uses DFS with a three-state traversal.

Sorting uses the STL algorithm library.

### 13.3 Performance

Average item lookup in `unordered_map` is O(1).

Sorting N items takes O(N log N).

Dependency validation takes O(V + E).

The implementation uses standard C++17 facilities and requires no third-party libraries.

### 13.4 Execution

Compile with a C++17-compatible compiler.

The program includes sample feature, outcome, theme, and horizon roadmaps, along with validation tests.

## 14. Java 17 Implementation

### 14.1 Enterprise architecture

The Java implementation separates domain entities, policies, reporting structures, and service operations.

| Component | Responsibility |
|---|---|
| `RoadmapService` | Manages roadmap operations |
| `RoadmapItem` | Immutable roadmap record |
| `Metric` | Outcome metric record |
| `Theme` | Strategic theme record |
| `PrioritizationPolicy` | Defines prioritization behavior |
| `WeightedPrioritizationPolicy` | Provides a concrete scoring policy |
| `RoadmapReport` | Represents aggregated reporting data |

### 14.2 Records and immutability

Java 17 records provide concise domain representations.

The implementation uses immutable records and creates replacement records when status, metric, or horizon values change.

This reduces accidental mutation and makes state transitions explicit.

Collections are copied when records are constructed, preventing callers from modifying their internal dependency and tag sets through shared mutable references.

### 14.3 Policy-based prioritization

The `PrioritizationPolicy` interface separates scoring logic from roadmap management.

This allows alternative prioritization strategies to be introduced without rewriting the service.

Possible enterprise scoring dimensions include:

- Strategic alignment.
- Customer value.
- Operational risk.
- Delivery effort.
- Cost of delay.
- Confidence.
- Regulatory importance.

The included implementation deliberately uses a small, deterministic policy.

### 14.4 State transitions

The service checks the expected item version before changing status.

It also validates dependencies before allowing an item to enter execution.

This supports explicit state management and provides a foundation for connecting the domain model to a transactional persistence layer.

### 14.5 Execution

Requirements:

- Java 17.
- No external dependencies.

Compile the file using the Java 17 compiler and execute the resulting class.

## 15. PostgreSQL Implementation

### 15.1 Relational architecture

The database implementation provides persistent relational storage for roadmap planning.

| Table | Purpose |
|---|---|
| `roadmap_users` | Stores owners and organizational identities |
| `roadmaps` | Stores roadmap definitions |
| `strategic_themes` | Stores strategic investment themes |
| `roadmap_items` | Stores roadmap initiatives |
| `outcome_metrics` | Stores measurable outcome values |
| `item_dependencies` | Stores prerequisite relationships |
| `roadmap_tags` | Stores roadmap-level tags |
| `item_tags` | Associates tags with items |
| `roadmap_audit` | Records lifecycle and progress changes |

### 15.2 Referential integrity

Primary keys provide stable identifiers.

Foreign keys enforce relationships between roadmaps, users, themes, items, and metrics.

Unique constraints prevent duplicate email addresses, theme names within a roadmap, and item titles within a roadmap.

Check constraints enforce:

- Nonempty names.
- Valid progress values.
- Valid confidence values.
- Nonnegative metrics.
- Valid date ordering.
- No direct self-dependencies.

### 15.3 Type-specific validation

The `validate_roadmap_item` trigger checks the parent roadmap type.

It prevents horizon values from being assigned to incompatible roadmap types and requires horizons for Now-Next-Later items.

It also validates theme membership.

The `validate_outcome_metric` trigger ensures that outcome metrics are attached only to outcome roadmap items.

### 15.4 Dependency integrity

The `item_dependencies` table stores prerequisite relationships.

The `validate_dependency_cycle` trigger uses a recursive CTE to determine whether a proposed dependency introduces a cycle.

The same trigger verifies that both items belong to the same roadmap.

### 15.5 Lifecycle governance

The `validate_status_transition` trigger:

- Prevents ordinary reopening of completed or cancelled items.
- Checks prerequisite completion.
- Sets progress to 100 when an item is completed.
- Updates timestamps.
- Increments the item version.

The audit trigger records status and progress changes.

### 15.6 Reporting

The SQL file creates three views:

- `roadmap_item_details`
- `outcome_progress_report`
- `roadmap_completion_report`

These provide reusable reporting structures without repeating the same joins in every application query.

The script also demonstrates:

- Recursive dependency evaluation.
- Outcome progress calculation.
- Priority scoring.
- Horizon distribution.
- Theme alignment.
- Execution eligibility.
- Transactional workflow processing.
- Expected foreign-key failure handling.

### 15.7 Indexing decisions

Indexes support common query patterns.

The implementation indexes:

- Roadmap ownership.
- Roadmap type and active state.
- Items by roadmap and status.
- Priority and confidence.
- Planning horizon.
- Item ownership.
- Dependency reverse lookup.
- Metric measurement dates.
- Audit history by item and timestamp.

Indexes improve retrieval but add storage and write-maintenance costs.

Index selection should be validated against actual query plans and data volume.

### 15.8 Production considerations

The SQL implementation is an executable teaching database rather than a complete multi-tenant enterprise application.

A production deployment should consider:

- Database roles and least-privilege permissions.
- Row-level security where tenant isolation is required.
- Explicit actor identity in audit records.
- Controlled status-transition permissions.
- Serializable or appropriately isolated transactions for concurrent dependency changes.
- Protection against concurrent dependency-cycle insertion.
- Historical metric observations.
- Data-retention requirements.
- Backup and recovery procedures.
- Application-level authorization.

The database triggers enforce important integrity conditions, but authorization must not rely solely on client-side validation.

## 16. Cross-Language Implementation Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Domain modeling | Dataclasses | Classes | Structs | Records | Relational tables |
| Roadmap types | Enums | Frozen objects | Enums | Enums | Enum types |
| Dependency storage | Sets | Sets | Sets | Sets | Junction table |
| Dependency validation | DFS | DFS | DFS | DFS | Recursive CTE |
| Outcome metrics | Metric class | Metric object | Struct | Record | Metric table |
| Prioritization | Sorting | Sorting | STL algorithms | Policy interface | SQL scoring |
| Lifecycle control | Methods | Event-driven methods | Class methods | Service methods | Triggers and procedures |
| Reporting | Dictionaries | Objects | Maps | Records and streams | Views and aggregates |
| Persistence | JSON | JSON | In-memory example | In-memory example | Relational database |
| Concurrency control | Not implemented | Optimistic item versions | Not implemented | Optimistic item versions | Transactional operations |

The implementations share the same core planning concepts but use different engineering approaches.

Python emphasizes rapid domain modeling and automation.

JavaScript emphasizes asynchronous operations and event-driven integration.

C++ emphasizes explicit data structures and efficient in-memory processing.

Java emphasizes immutable domain models and replaceable business policies.

PostgreSQL emphasizes persistent data integrity and database-enforced relationships.

## 17. Validation and Failure Scenarios

| Scenario | Expected behavior |
|---|---|
| Empty roadmap name | Reject creation |
| Missing owner | Reject item creation |
| Duplicate item identifier | Reject insertion |
| Invalid priority | Reject item creation |
| Invalid progress | Reject update |
| Negative metric | Reject metric |
| Outcome item without metric | Reject creation |
| Horizon item without horizon | Reject creation |
| Unknown dependency | Reject insertion |
| Self-dependency | Reject insertion |
| Circular dependency | Reject relationship |
| Incomplete prerequisite | Prevent execution |
| Invalid horizon transition | Reject update |
| Terminal item modification | Reject ordinary update |
| Stale item version | Reject concurrent update |
| Invalid theme relationship | Reject association |

Validation should occur at more than one layer.

Application-level checks provide immediate feedback.

Database constraints and triggers protect persistent records against invalid writes from different application clients.

## 18. Security and Operational Considerations

Roadmap information may contain sensitive business priorities, unreleased capabilities, strategic investments, and operational dependencies.

A production roadmap system should implement:

- Role-based access control.
- Authentication and authorization.
- Ownership verification.
- Least-privilege database access.
- Audit logging.
- Secure API communication.
- Input validation.
- Export access restrictions.
- Backup and retention policies.
- Concurrent update protection.

JSON exports should be written to controlled directories with appropriate filesystem permissions.

Database users should not receive unrestricted access to strategic planning tables.

Audit records should identify the authenticated actor rather than relying on an unverified client-supplied identity.

Roadmap visibility should be based on organizational responsibility and information sensitivity.

## 19. Practical Roadmap Selection

| Planning requirement | Suitable roadmap |
|---|---|
| Communicate planned product functionality | Feature roadmap |
| Track customer or business improvement | Outcome roadmap |
| Organize investment around strategic objectives | Theme roadmap |
| Communicate relative priorities under uncertainty | Now-Next-Later roadmap |
| Coordinate delivery dependencies | Feature roadmap with dependency tracking |
| Evaluate measurable product impact | Outcome roadmap |
| Communicate portfolio direction | Theme roadmap |
| Maintain flexible near-term planning | Now-Next-Later roadmap |

A mature product planning process can use multiple roadmap perspectives simultaneously.

The choice should be driven by the decision that stakeholders need to make, rather than by a preference for one presentation format.
