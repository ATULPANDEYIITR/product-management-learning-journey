# UX Fundamentals: UX, UI, Usability, Accessibility, Interaction Design, and Information Architecture

## Scope

This learning artifact models UX as a system of related but distinct concerns:

- **UX** concerns the quality of the complete user experience, including task success, clarity, efficiency, accessibility, and perceived control.
- **UI** concerns the concrete interface presentation and control vocabulary through which users interact with a product.
- **Usability** evaluates whether users can accomplish intended tasks effectively, efficiently, and with an acceptable error rate.
- **Accessibility** ensures that interaction and information remain available to users with different abilities and interaction methods.
- **Interaction design** defines how controls behave, how users move through states, and how actions produce understandable results.
- **Information architecture** organizes content, navigation, labels, hierarchy, and relationships so users can locate and understand information.

The implementations use a common domain:

`User → Screen → Information Structure → Controls → Interaction → Accessibility → Usability Evidence → UX Evaluation`

The concepts are related, but they are not interchangeable. A visually attractive interface can have poor usability. A usable mouse-driven interface can fail keyboard accessibility. A technically accessible screen can still have confusing information architecture.

## Conceptual Model

A practical UX evaluation separates several layers:

| Layer | Primary question | Evidence |
|---|---|---|
| UX | Does the experience support the user's intended outcome? | Task results, errors, efficiency, accessibility, consistency |
| UI | Can users understand and operate the visible interface? | Labels, controls, visual hierarchy, contrast |
| Usability | Can users complete tasks successfully and efficiently? | Completion rate, duration, errors, observations |
| Accessibility | Can users with different access needs operate and understand the interface? | Keyboard access, accessible names, contrast |
| Interaction design | Are actions, states, feedback, and transitions understandable? | Focus order, primary actions, state behavior |
| Information architecture | Can users find and understand information? | Navigation, grouping, headings, labels |

A useful evaluation sequence is:

`Information structure → Interface controls → Interaction behavior → Accessibility → Task testing → Release decision`

## Information Architecture

Information architecture defines how information is grouped and exposed.

The implementations represent this through:

- screens
- navigation items
- content sections
- headings
- primary actions
- unique labels
- navigation breadth

A dashboard with eight unrelated top-level navigation destinations is treated as a possible information-architecture problem. The issue is not that eight items are universally invalid. The concern is that excessive breadth can increase scanning and decision cost.

The PostgreSQL model stores navigation position explicitly. This allows queries to identify screens with unusually broad navigation without embedding the rule only in application code.

The Python implementation evaluates navigation directly from `Screen` objects. The JavaScript implementation uses a policy rule and emits evaluation events. The C++ implementation uses an explicit governance engine. Java separates information-architecture validation into an `InformationArchitectureRule`.

## UI Fundamentals

UI is represented through concrete interface controls rather than abstract visual descriptions.

The domain includes:

- buttons
- links
- inputs
- checkboxes
- selects
- accessible names
- primary actions
- contrast tokens
- visibility
- focus reachability

A primary action represents the intended main task of a screen. The implementations validate that the declared primary action corresponds to an actual interactive control.

This prevents a common modeling error where a design specification says an action exists but the actual interface model contains no corresponding control.

UI consistency is also treated separately from information architecture. For example, a product that alternates between `Save`, `Confirm`, and `Submit` for the same semantic operation may introduce unnecessary interpretation cost.

Consistency does not mean every action should use the same label. Labels should reflect the user's intended result. The important requirement is semantic consistency.

## Usability

Usability is measured through observed task behavior rather than visual preference alone.

The implementations record:

- task name
- completion state
- duration
- number of steps
- errors
- notes

The primary metrics are:

### Completion Rate

`completed tasks / total tasks`

A high completion rate indicates that users can accomplish the evaluated tasks, but it does not prove that the experience is efficient or accessible.

### Average Task Time

`sum of task durations / number of tasks`

Task duration can expose unnecessary navigation, unclear controls, or repeated decision points.

### Error Rate

`total errors / total task steps`

Error rate provides a normalized measure of interaction difficulty. It should be interpreted with the task design and error severity rather than treated as a universal quality score.

The sample sessions intentionally contain successful and unsuccessful tasks so the metrics show meaningful variation.

## Accessibility

Accessibility is implemented as an explicit validation layer.

The examples check three important conditions:

1. Interactive controls have accessible names.
2. Interactive controls are keyboard reachable.
3. Contrast ratios meet the modeled normal-text threshold.

The sample settings screen deliberately contains a control without an accessible name and a control that cannot be reached from the keyboard. These are represented as separate findings because they represent different accessibility failures.

The accessibility model does not assume that accessibility is only a visual concern. Keyboard interaction and semantic naming are behavioral and structural requirements.

The contrast model uses a `4.5:1` threshold for normal text as a practical WCAG AA-oriented validation rule. Real production systems must also consider text size, graphical objects, focus indicators, non-text contrast, states, and the exact applicable accessibility conformance criteria.

## Interaction Design

Interaction design concerns what happens when users operate the interface.

The implementations model interaction through:

- primary actions
- focus order
- keyboard reachability
- control state
- task sequences
- validation
- event publication
- policy evaluation

A primary action that does not correspond to an actual control is treated as an interaction defect.

Keyboard focus is modeled explicitly because visual order and interaction order can diverge. A screen may appear correct while still presenting a confusing or inaccessible keyboard sequence.

The JavaScript implementation adds an event-driven layer. Screen evaluation produces `screen:evaluated` events, making the model suitable for applications where UX evaluation results need to be observed by other components.

## Python Implementation

The Python implementation is a self-contained UX workbench.

### Domain structures

`dataclass` models represent:

- users
- screens
- UX issues
- usability task results
- usability sessions

`Enum` types provide controlled values for issue types and severity levels.

### Validation

`UXValidationError` is used for invalid domain states such as:

- duplicate screen identifiers
- missing screen titles
- invalid task duration
- invalid task step counts
- error counts greater than step counts

### Audit engine

`UXWorkbench` provides separate checks for:

- information architecture
- accessibility
- interaction design
- UI consistency

This keeps the different UX dimensions analytically distinct.

### Usability measurement

`UXSession` calculates completion rate, average task time, and error rate.

### Reporting

The Python program writes `ux_audit_report.json`. The exported report contains screen information and detected UX issues.

### Testing

Executable assertions verify core invariants after the example workflow runs.

## JavaScript Implementation

The JavaScript implementation uses an event-driven policy architecture.

### Event model

`UXEventBus` extends Node.js `EventEmitter`.

When a screen is evaluated, the system publishes a `screen:evaluated` event containing:

- screen identifier
- issue count
- evaluation timestamp

This demonstrates how UX evaluation can become part of a larger application workflow rather than being limited to a synchronous report.

### Policy engine

`UXPolicyEngine` stores independent evaluation rules:

- navigation breadth
- accessible names
- keyboard focus
- contrast
- content structure
- primary action validity

Each rule returns structured issues.

### Usability session

`UsabilitySession` records participant task measurements and calculates:

- completion rate
- average duration
- normalized error rate

### Persistence

The Node.js program writes `ux_policy_report.json`.

The file contains both policy findings and usability measurements, allowing qualitative and quantitative evidence to be examined together.

## C++17 Implementation

The C++ implementation treats UX evaluation as a governance engine.

### Domain model

The program uses:

- `struct` for domain records
- `enum class` for controlled states
- STL containers for collections
- exceptions for invalid domain state
- explicit evaluation methods

The main engine is `UXGovernanceEngine`.

### Evaluation separation

The engine has separate methods for:

- information architecture
- accessibility
- interaction
- UI consistency

This design avoids collapsing every defect into a generic UX error.

### Release gate

The program counts critical accessibility issues.

If a critical accessibility issue remains, the release gate is reported as blocked.

This is a deliberate governance rule rather than a universal UX law. Production systems should establish release criteria based on organizational risk, applicable accessibility requirements, product context, and defect severity.

### Performance

The engine uses hash-based screen storage through `std::unordered_map`. Audit operations iterate through registered screens and their controls.

For `n` screens with `m` total controls, the principal validation work is approximately `O(n + m)` for the basic screen and control checks, excluding container lookup costs.

## Java 17 Implementation

The Java implementation models UX evaluation as an enterprise domain service.

### Domain types

Java records provide immutable representations for:

- controls
- screens
- UX issues
- task results
- usability metrics

This reduces accidental mutation of domain values.

### Policy objects

The `UXRule` interface establishes a policy abstraction.

Separate implementations handle:

- accessibility
- information architecture
- interaction
- usability

`UXPolicy` composes these rules and evaluates a screen through streams.

### Service layer

`UXService` manages registered screens and exposes:

- screen registration
- UX auditing
- usability measurement

This structure resembles an enterprise service layer where domain policies are kept separate from application orchestration.

### Validation

Domain constructors reject:

- blank identifiers
- missing control data
- invalid task measurements
- negative durations
- invalid error counts

The model therefore prevents invalid task measurements from entering the evaluation pipeline.

## PostgreSQL Implementation

The PostgreSQL implementation models UX as relational evidence.

### Core relational model

The main relationships are:

`Users → Usability Sessions → Usability Tasks`

and

`Screens → Navigation Items`

`Screens → Content Sections`

`Screens → Controls → Focus Order`

`Screens → Contrast Tokens`

`Screens → UX Issues → Issue Events`

This structure distinguishes interface structure from observed user behavior and evaluation findings.

### Constraints

Database constraints enforce:

- primary-key identity
- foreign-key relationships
- unique screen identifiers
- unique navigation positions
- unique control identifiers
- valid task durations
- valid task steps
- error counts within task-step limits
- controlled issue states

This prevents invalid records from being accepted merely because application code failed to validate them.

### Triggers

The primary-action trigger verifies that a screen's declared primary action exists as a control.

The focus-order trigger prevents duplicate focus positions.

The issue-event trigger records the creation of an issue.

These controls demonstrate why important domain invariants can sometimes belong at the database layer.

### Views

The database provides reporting views for:

- accessibility findings
- contrast findings
- navigation breadth
- usability metrics

The views make recurring evaluation queries reusable without duplicating their SQL definitions.

## Workflow

A practical UX evaluation workflow represented by these implementations is:

`Define information structure`
        |
        v
`Define interface controls`
        |
        v
`Define interaction and focus behavior`
        |
        v
`Validate accessibility`
        |
        v
`Test realistic user tasks`
        |
        v
`Measure completion, time, and errors`
        |
        v
`Classify findings`
        |
        v
`Apply release criteria`

Each stage produces different evidence.

A navigation defect should not automatically be described as an accessibility defect. A missing accessible name should not be classified as a generic usability preference. A failed task may indicate several possible causes and should be investigated using observations and system behavior.

## Distinguishing the Major Areas

| Area | What it controls | Example failure |
|---|---|---|
| UX | Quality of the complete experience | Users complete a task but encounter excessive errors and confusion |
| UI | Visible and operable interface | Ambiguous button labels |
| Usability | Task effectiveness and efficiency | Users repeatedly fail to locate a required action |
| Accessibility | Access across different abilities and interaction methods | A button cannot be reached with the keyboard |
| Interaction design | Action behavior and state transitions | Primary action does not produce understandable feedback |
| Information architecture | Organization and discoverability | Too many unrelated top-level destinations |

These categories should be used diagnostically. A single observed problem can have several contributing causes, but the causes should be separated before selecting a corrective action.

## Edge Cases

The implementations deliberately handle several failure conditions.

### Missing accessible name

A control without an accessible name is reported independently from keyboard accessibility.

### Keyboard-inaccessible control

A control that cannot be reached by keyboard is treated as a critical accessibility finding in the example release policy.

### Low contrast

Contrast values below the modeled threshold are reported as accessibility findings.

### Excessive navigation breadth

Navigation with more than seven top-level destinations is flagged as a potential information-architecture problem.

### Invalid task measurements

Negative duration, zero steps, negative errors, or more errors than steps are rejected.

### Missing primary action

A declared primary action that does not exist as a control is rejected as an interaction-design defect.

### Empty information structure

A screen without content grouping is reported as a usability problem because users lack a modeled hierarchy for the presented information.

## Security and Privacy Considerations

UX measurement can contain user-related information. Production implementations should avoid collecting unnecessary personal data.

The sample systems use synthetic participant identifiers and behavioral measurements rather than sensitive personal information.

A production UX telemetry system should consider:

- data minimization
- access control
- retention limits
- audit logging
- aggregation before reporting
- separation of identity from behavioral measurements
- protection of exported reports
- secure handling of session data

Accessibility testing also requires care when collecting information about user needs. Such data should only be collected when necessary for the stated evaluation purpose.

## Performance Considerations

The examples intentionally use in-memory collections for application-side evaluation and relational indexes for database-side reporting.

Useful performance decisions include:

- `dict` and `Map` lookups for screen identifiers
- `unordered_map` for C++ screen storage
- immutable Java records for predictable domain values
- database indexes on screen relationships and issue status
- aggregation queries for usability metrics
- views for reusable reporting logic

Performance should not be optimized by removing validation that protects domain correctness. In UX systems, incorrect evaluation data can be more damaging than modest computation overhead.

## Practical Limitations

These implementations are evaluation models, not complete browser accessibility engines or production design systems.

They do not automatically determine:

- whether a visual layout is aesthetically appropriate
- whether copy is culturally appropriate
- whether a real user's mental model matches the information architecture
- whether a color combination works for every visual condition
- whether a task is intrinsically valuable
- whether an interaction satisfies every applicable accessibility criterion
- whether a user research finding is statistically representative

Automated checks are most useful when combined with human review, realistic task scenarios, and observed user behavior.

## Technical Relationship Between the Implementations

| File | Primary perspective |
|---|---|
| Python | Object-oriented UX audit and usability measurement |
| JavaScript | Event-driven policy evaluation and structured reporting |
| C++17 | Explicit UX governance and release-gate engine |
| Java 17 | Enterprise domain model with policy objects and immutable records |
| PostgreSQL | Relational representation, constraints, triggers, and analytical reporting |

The five implementations use the same conceptual domain while deliberately emphasizing different engineering techniques.

The common model is:

`Information Architecture`
→ `UI Controls`
→ `Interaction Behavior`
→ `Accessibility`
→ `Usability Evidence`
→ `UX Decision`

The separation is important because each layer answers a different engineering question and requires different forms of evidence.
