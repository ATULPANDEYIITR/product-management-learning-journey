# Agile Fundamentals: Iterative and Incremental Software Delivery

## Purpose and scope

Agile is an approach to product development that emphasizes frequent delivery, collaboration with stakeholders, adaptation to new evidence, and continuous improvement. It is not a single project-management method or a fixed sequence of ceremonies.

This learning artifact models Agile delivery for a civic service portal. The team must deliver secure authentication, prevent duplicate submissions, expose service-request status, and maintain a reliable testing process.

The six files approach the subject from different technical perspectives:

- **Python** implements a product backlog, work-item state machine, sprint planning, acceptance checks, capacity calculations, delivery reporting, and executable validation tests.
- **JavaScript** models asynchronous stakeholder feedback, event-driven delivery, increment acceptance, release events, and retrospective actions.
- **C++** implements a delivery-governance engine with explicit state transitions, dependency validation, sprint commitments, capacity, and delivery history.
- **Java** models enterprise-oriented delivery through domain classes, immutable value objects, explicit iteration states, acceptance authority, dependency checks, and retrospective actions.
- **PostgreSQL** represents the workflow relationally, using constraints, foreign keys, triggers, views, indexes, and realistic sample data.

The implementations are educational domain models, not complete replacements for production project-management systems. Each deliberately enforces selected workflow rules so that important Agile principles can be observed through executable behavior.

## The Agile mindset

The Agile Manifesto describes four value preferences:

- Individuals and interactions over processes and tools.
- Working software over comprehensive documentation.
- Customer collaboration over contract negotiation.
- Responding to change over following a plan.

These preferences do not mean that processes, documentation, contracts, or plans have no value. They emphasize that such mechanisms should support useful outcomes rather than become ends in themselves.

The civic service team applies these values by validating real user outcomes, reviewing working increments with stakeholders, making unfinished work visible, and changing its approach when testing exposes a problem.

Agile also recognizes that requirements, implementation risks, and stakeholder priorities evolve. A delivery plan is therefore a forecast based on current evidence, not a guarantee that every original assumption will remain correct.

### Empirical process control

An empirical approach makes decisions using observed results rather than relying entirely on predictions.

The delivery workflow uses three related activities:

- **Transparency:** The backlog, work states, acceptance evidence, blockers, and unfinished commitments remain visible.
- **Inspection:** The team checks the increment against acceptance criteria and examines delivery results.
- **Adaptation:** The team revises implementation decisions, backlog priorities, testing practices, or team working agreements in response to evidence.

A failed acceptance check is useful information. It indicates that the increment does not yet meet the required outcome. Hiding the failure or declaring the item complete would undermine the feedback mechanism.

## Iterative development and incremental delivery

Iteration and increment describe different aspects of delivery.

**Iterative development** improves a solution through repeated cycles of implementation, feedback, and refinement. An early design or workflow may be revised after users discover usability problems or tests reveal an incorrect assumption.

**Incremental delivery** adds usable capabilities to the product over time. Each increment expands what users can do, provided it meets the relevant quality and acceptance requirements.

A team can iterate on a feature without releasing it immediately. It can also deliver a small, independently useful increment during an iteration. The concepts are related but not interchangeable.

For the civic portal, an iterative cycle might improve authentication after a failed invalid-credential test. An incremental release might deliver secure sign-in first, followed by request-status visibility after its dependency becomes available.

A sprint or iteration is a planning and feedback interval. Its existence does not guarantee that all committed work will be released by the end. The delivery report must distinguish completed increments from unfinished items.

## Product backlog and refinement

The product backlog is an ordered collection of work that may contribute to the product's goals. It can contain customer-facing features, defects, technical enablers, and research activities.

A backlog item should describe a meaningful outcome and provide enough information for the team to evaluate and implement it. The examples use:

- A stable work-item identifier.
- A concise title and outcome.
- An effort estimate expressed in story points.
- A business-value estimate.
- Acceptance criteria.
- Dependencies on other work where necessary.

Story points are relative estimates used by a team to discuss effort, complexity, and uncertainty. They are not a standard unit of elapsed time and should not be compared mechanically across different teams.

### Refinement

Backlog refinement improves shared understanding before work is selected for an iteration. It can expose missing acceptance criteria, oversized work, unresolved dependencies, technical uncertainty, or an inadequate definition of the expected outcome.

The Python and C++ models prevent backlog items from moving directly into implementation without refinement. The JavaScript and Java implementations likewise require a ready state before planning.

The PostgreSQL data model stores acceptance criteria separately from backlog items so that individual criteria can be verified and queried.

### Prioritization

The examples calculate business value divided by story points as a simple prioritization aid. A high ratio can help initiate a discussion about relative value and effort.

This ratio is not an objective business truth. It does not adequately represent regulatory deadlines, dependencies, risk reduction, strategic importance, accessibility obligations, or uncertainty. A product owner and delivery team must consider those factors before ordering the backlog.

## Sprint planning and capacity

Sprint planning connects a delivery goal with a feasible selection of work.

The team considers:

- The outcome that the iteration should support.
- The availability of team members.
- Previously observed delivery performance.
- The readiness of proposed backlog items.
- Dependencies and technical constraints.
- The acceptance evidence required for each increment.

### Capacity and velocity are different

**Capacity** estimates the time available to perform work. The examples calculate effective working days by multiplying each member's available days by an assumed focus factor.

A focus factor approximates the proportion of available time that can be spent on planned delivery work after accounting for interruptions and other responsibilities. It is a planning assumption, not a performance score.

**Velocity** records how many story points a team completed during an iteration, according to its agreed completion policy. It can help the same team forecast future work when historical conditions remain reasonably comparable.

Neither capacity nor velocity is a promise. The examples keep working-day capacity separate from story-point commitments to prevent an incorrect conversion between the two measures.

A production team should use a consistent definition of completed work and interpret historical data alongside changes in team membership, work type, uncertainty, and operational interruptions.

## The delivery workflow

The implementations use explicit states to prevent a work item from being treated as complete merely because someone has started or submitted it.

| State | Meaning |
|---|---|
| Backlog | The item has been identified but is not ready for implementation. |
| Ready | The item has sufficient detail for planning under the team's working agreement. |
| In progress | Implementation is underway. |
| In review | The work is being examined before testing or acceptance. |
| Testing | The increment is undergoing verification. |
| Accepted | The required acceptance criteria have been verified and an authorized stakeholder has accepted the increment where the model requires it. |
| Released | The capability has been designated as part of a release. |
| Blocked | Progress is stopped by a recorded impediment. |

These states represent a teaching model rather than a universal Agile workflow. Scrum does not prescribe this exact set of item states. A team may use different labels and still apply sound Agile principles.

### Acceptance criteria

Acceptance criteria describe observable conditions that an increment must satisfy. They make completion decisions more concrete and help the team distinguish an implemented feature from a verified outcome.

For authentication, the examples require valid credentials to establish a session and invalid credentials to be rejected. For duplicate submission protection, the criteria distinguish retries of an existing request from genuinely new requests.

The Python, C++, Java, and SQL implementations prevent acceptance while required criteria remain unverified. JavaScript asynchronously evaluates stakeholder decisions and returns rejected work to active implementation. The Java implementation also requires a named acceptance authority.

In production, acceptance criteria should be supported by suitable evidence, such as automated tests, exploratory testing, accessibility checks, security tests, or operational validation. A boolean field alone does not establish that the underlying test was correctly performed.

### Dependencies

Some increments depend on other capabilities. The civic portal's request-status display depends on secure access being available.

The examples keep that dependent item out of the initial iteration. After authentication is released, the status-display item becomes eligible for a subsequent plan.

The Python, JavaScript, C++, and Java models check dependency readiness during planning. The SQL model records dependencies in a separate relationship table and validates dependency completion before acceptance.

These checks demonstrate a policy, not a claim that every dependency must always be implemented in a separate iteration. A team may deliver dependent work together when it can manage the implementation and acceptance sequence safely.

## Python implementation

The Python script uses dataclasses and enumerations to define work items, acceptance criteria, team members, sprints, and retrospective actions.

`AgileBoard` coordinates the backlog and iteration workflow. Its transition table defines which state changes are permitted. Invalid transitions raise exceptions instead of silently altering the board.

The script demonstrates several concrete behaviors:

- Refinement changes a backlog item into a ready item only after its essential planning information is present.
- Sprint planning rejects duplicate commitments, non-ready items, and items whose dependencies are not complete.
- Team capacity is calculated in effective working days.
- Completion requires all acceptance criteria to be verified.
- A blocked item must have a recorded reason.
- Sprint reporting separates committed points from completed points and identifies unfinished work.
- Velocity is calculated from recorded completed points rather than the original sprint estimate.

The script also contains `unittest` checks for invalid estimates, premature implementation, incomplete acceptance evidence, successful completion, missing blocker reasons, and duplicate item identifiers.

The example deliberately leaves the accessibility item unfinished. This illustrates why an iteration report should present actual delivery rather than claiming that the entire commitment was completed.

Run the program using Python 3.10 or later. It uses only the standard library.

## JavaScript implementation

The JavaScript file emphasizes event-driven behavior and asynchronous stakeholder feedback.

`ProductBacklog` validates item definitions and maintains work-item history. `DeliveryTeam` calculates effective capacity from member availability and focus assumptions. `Iteration` manages planning, work transitions, acceptance requests, release events, and delivery reporting.

The implementation uses Node.js's `EventEmitter` to publish events such as iteration starts, blocked work, acceptance requests, and released increments. Event consumers can maintain audit records or update a user interface without placing those responsibilities inside every domain method.

The `accept` method is asynchronous. It evaluates each criterion through a supplied validation function and waits for the results. If a required criterion fails, the increment returns to active work and the rejection is recorded. Acceptance is not inferred merely from the submission of an increment.

This model illustrates why asynchronous workflows must handle failure explicitly. Stakeholder feedback, external test services, and validation operations may complete later than the request that initiated them.

The program uses Node.js built-in modules and can be executed without installing npm dependencies. It includes assertions for acceptance rejection and duplicate sprint commitments.

## C++ case study

The C++ program implements a delivery engine for a public-service application.

`WorkItem` represents a deliverable capability and includes its identifier, estimated effort, business value, acceptance criteria, dependencies, and optional blocker. `TeamMember` models effective working-day capacity. `Sprint` stores the goal, duration, committed item identifiers, and execution state.

`DeliveryEngine` coordinates the workflow using ordered maps, vectors, sets, and explicit validation methods. The implementation demonstrates how a strongly typed state machine can prevent invalid operations before changing the model.

The case study includes:

- Backlog refinement and priority calculation.
- Capacity aggregation across team members.
- Dependency-aware sprint planning.
- Rejection of commitments that exceed the agreed point budget.
- Validation of legal state transitions.
- Acceptance safeguards for incomplete criteria.
- Blocker recording and resolution.
- Sprint completion reporting based on released items.
- Average velocity based on recorded iteration results.

The program uses standard-library containers and algorithms rather than external dependencies. Ordered maps support predictable lookup and display behavior, while sets make duplicate identifiers and dependency membership checks explicit.

For a backlog of \(n\) items, sorting by value per point takes \(O(n \log n)\) time. Looking up an item in the ordered map takes \(O(\log n)\) time. These costs are appropriate for a small educational model; production systems may require pagination, indexed persistence, and separate query optimization for large work collections.

The engine records workflow events, but its event history is an in-memory list rather than a durable audit log. A production implementation would require persistence, authorization, transactional state changes, and protection against concurrent updates.

## Java enterprise model

The Java implementation emphasizes explicit domain boundaries and validation.

`AcceptanceCriterion` is a record representing a criterion description. `WorkItem` holds delivery state, dependency identifiers, verification results, release information, and a timestamped audit trail. `ProductBacklog` provides item lookup and value-based prioritization. `Iteration` controls planning and the execution lifecycle.

The model uses immutable collections at important boundaries. For example, work-item criteria and dependency sets are copied when the item is constructed, reducing the risk that callers can change the definition without passing through domain logic.

State transitions use an `EnumSet` policy to identify allowed next states. Acceptance requires all criteria to be verified, dependencies to be released, and a named acceptance authority to be provided.

The distinction between an accepted increment and a released increment is deliberate. Acceptance establishes that the increment meets its required conditions. Release marks it as available through a named release in the model.

`Retrospective` stores observations and improvement actions. An action includes an owner and a success measure, turning a general discussion into a change that can be evaluated later.

The program compiles with Java 17 or later. Its in-memory audit trail illustrates domain history but does not replace durable logging, authorization, persistence, or transaction management in an enterprise service.

## PostgreSQL data model

The SQL script uses the `agile_fundamentals` schema to model product delivery relationally.

### Main entities and relationships

| Table | Purpose |
|---|---|
| `products`
