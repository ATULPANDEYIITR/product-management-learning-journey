# Problem definition

## Introduction

Problem definition is the disciplined process of describing an undesirable condition clearly enough that people can investigate it, measure it, establish boundaries around it, and make informed decisions about what should change.

A problem is not automatically a proposed solution. Statements such as `build a new application`, `replace the database`, `implement automation`, or `add artificial intelligence` describe possible interventions rather than the underlying problem.

A well-defined problem separates four questions:

1. What is happening?
2. Who or what is affected?
3. Why does the condition matter?
4. What evidence supports the description?

The implementations in this repository approach these questions from three programming perspectives. Python provides a broad educational model with reusable data structures and analytical functions. JavaScript demonstrates the same discipline in an application-oriented and event-driven environment. C++ develops the concept into a more structured technical case study involving an online examination submission system.

The central example used across the implementations is reliability of an online examination submission process. The purpose is not to prescribe a particular technology or solution. The purpose is to demonstrate how a technically complex situation can be converted into a bounded, measurable, evidence-based problem.

## Fundamental concepts

### Problem

A problem is an undesirable current condition that creates a meaningful gap between the present state and a required or desired state.

For example:

`Students sometimes cannot complete an online examination submission during peak traffic.`

This describes a condition.

A stronger version identifies evidence:

`During peak traffic, successful final submissions fall below the operational target and some attempts remain pending or fail.`

The second formulation provides a basis for measurement and investigation.

### Problem statement

A problem statement describes the current condition without prematurely selecting a solution.

A useful structure is:

`affected actor + current condition + measurable gap + consequence + evidence + scope`

For example:

`Online students experience failed or delayed examination submissions during peak traffic. Successful submission rate falls below the operational target, which creates a risk that legitimate work will not be recorded before the deadline.`

A strong statement should be specific enough to investigate while remaining independent of a particular implementation.

### Desired state

The desired state describes what should be true after the underlying problem has been addressed.

Examples include:

- students can complete valid submissions before the deadline;
- the submission service remains within an agreed latency threshold;
- duplicate submissions remain below a defined rate;
- support contacts remain below an operational target.

The desired state should be distinguishable from the solution. `Deploy a new server` is not a desired state. `Maintain successful submission reliability during peak demand` is.

### Problem gap

The gap is the difference between the observed current state and the desired state.

Suppose:

- baseline successful submission rate = 61%;
- target successful submission rate = 75%.

The measurable gap is 14 percentage points.

A second example may involve latency:

- baseline p95 latency = 8.4 seconds;
- target p95 latency = 3 seconds.

The direction of improvement matters. Lower latency is normally desirable, whereas higher successful-submission rate is desirable.

## Terminology

| Term | Meaning |
| --- | --- |
| Problem | An undesirable current condition that creates a meaningful gap |
| Problem statement | A concise description of the problem |
| Symptom | An observable manifestation of a problem |
| Cause | A factor that contributes to an observed condition |
| Root cause | A sufficiently fundamental causal factor whose correction materially reduces the problem |
| Causal hypothesis | A proposed explanation that still requires validation |
| Problem framing | The structured definition of the actor, current state, desired state, gap, context, assumptions, constraints, and boundaries |
| Boundary | The explicit definition of what belongs inside or outside the investigation |
| Constraint | A condition that limits the feasible set of actions |
| Assumption | A proposition treated as true temporarily for analysis |
| Evidence | Information used to support, challenge, or refine a problem definition |
| Baseline | The measured current condition against which change is evaluated |
| Target | The required or desired future measurement |
| Stakeholder | A person or group affected by, responsible for, or able to influence the problem |
| Hypothesis | A proposition that can be tested against evidence |
| Scope | The defined extent of the problem |
| Consequence | The effect produced by the problem |
| Intervention | A deliberate change intended to influence the problem |

## Core principles

### Define the condition before choosing the solution

A frequent mistake is to convert a preferred solution into the problem definition.

Weak:

`The university needs a new submission platform.`

Better:

`Students experience failed or delayed submissions during peak examination traffic.`

The first statement assumes that replacement is necessary. The second permits multiple possible explanations and interventions.

### Separate observation from interpretation

Consider these statements:

`The timeout rate increased from 2% to 5%.`

This is an observation when supported by valid measurement.

`The database is overloaded.`

This is an interpretation unless evidence has established that database capacity is responsible.

`Users are frustrated.`

This may be an observation if supported by interviews or behavioral evidence, but it should not automatically be treated as a measured causal explanation.

A disciplined investigation distinguishes:

- measured facts;
- observations;
- assumptions;
- hypotheses;
- opinions.

The Python and JavaScript implementations explicitly represent these categories.

### Define the affected actor

A problem without an affected actor can become unnecessarily abstract.

Compare:

`System reliability is poor.`

with:

`Students attempting final examination submission experience failed or delayed acknowledgements.`

The second statement identifies who experiences the condition.

The affected actor can be:

- a customer;
- employee;
- administrator;
- patient;
- student;
- operator;
- business unit;
- external partner;
- software service;
- physical system;
- regulatory organization.

A technical system can also be an affected entity when the problem is about system-to-system behavior.

### Quantify the gap

Words such as `slow`, `large`, `expensive`, `unreliable`, `bad`, `frequent`, and `many` are often insufficient by themselves.

A measurable definition might state:

`p95 response time is 8.4 seconds against a target of 3 seconds.`

Another might state:

`Successful submission rate is 61% against a target of 75%.`

Quantification makes the problem testable and creates a baseline for evaluating change.

## Problem framing

Problem framing creates a structured representation of the problem.

The implementations use the following fields:

- affected actor;
- desired outcome;
- current state;
- gap;
- context;
- constraints;
- assumptions;
- exclusions;
- success metrics.

### Actor

The actor is the person, group, process, or system affected by the condition.

Example:

`Students using an examination portal`

### Current state

The current state describes what is actually happening.

Example:

`Submissions sometimes fail or remain pending during peak traffic.`

### Desired outcome

The desired outcome describes what should happen.

Example:

`Students should be able to complete legitimate submissions before the deadline.`

### Gap

The gap expresses the measurable difference between current and desired states.

Example:

`Successful submission rate falls below the operational target during peak periods.`

### Context

Context explains the circumstances under which the problem occurs.

Example:

`Online examinations with concentrated submission activity`

Context can materially change diagnosis. A service that behaves correctly under normal traffic but fails under extreme concurrency does not have the same problem as a service that fails consistently at every traffic level.

### Constraints

Constraints reduce the set of feasible interventions.

Examples include:

- fixed deadlines;
- fixed budgets;
- regulatory obligations;
- privacy requirements;
- compatibility requirements;
- existing authentication dependencies;
- infrastructure restrictions;
- staffing limitations.

A constraint is not necessarily a cause.

For example:

`The identity provider cannot be replaced this year`

is a constraint.

It does not prove:

`The identity provider causes submission failures.`

### Assumptions

Assumptions are statements treated as true temporarily.

Examples:

- examination rules are correct;
- timestamps are accurate;
- student home internet is outside institutional control.

Assumptions should remain visible because an incorrect assumption can invalidate a problem frame.

### Exclusions

Exclusions prevent scope expansion.

Examples:

- changing examination policy;
- replacing the identity provider;
- diagnosing individual home networks.

An exclusion does not mean the excluded item is irrelevant. It means it is outside the responsibility or investigation boundary currently being defined.

## Symptoms versus root causes

A symptom is an observable manifestation of a problem.

Example:

`Average submission response time increased from 4 seconds to 18 seconds.`

That observation does not establish why the latency increased.

Potential causes could include:

- insufficient capacity;
- database contention;
- dependency latency;
- network problems;
- queue saturation;
- inefficient queries;
- synchronization problems;
- deployment defects.

A root cause should not be declared simply because it sounds technically plausible.

### One problem, multiple causes

A system may fail because several factors interact.

For example:

`Peak traffic causes queue growth, which increases request latency, which causes clients to retry, which further increases load.`

There may be a feedback loop rather than one isolated cause.

### One cause, multiple symptoms

A single dependency failure may produce:

- login failures;
- API errors;
- support tickets;
- lost transactions;
- delayed processing.

The visible symptoms may appear unrelated until the shared dependency is investigated.

## Five Whys

Five Whys is a structured questioning technique that repeatedly asks why an observed condition occurs.

Example:

1. Orders are shipped late.
2. Why? Warehouse picking starts later than planned.
3. Why? Picking waits for manual payment-status confirmation.
4. Why? Payment exceptions are checked in another system.
5. Why? The systems do not exchange exception status automatically.
6. Why? The integration was never designed for exception-state synchronization.

The final statement is a root-cause candidate.

Five Whys has limitations. It can produce a misleading single causal chain when a problem actually has several interacting causes. It also depends on the quality of the answers and the available evidence.

It should therefore be treated as a hypothesis-generation method rather than mathematical proof.

## Causal hypotheses

A causal hypothesis has a structure similar to:

`If X changes, Y should change because mechanism Z connects them.`

Example:

`Payment failures materially contribute to checkout abandonment.`

Possible test:

`Compare abandonment after payment errors with abandonment after successful authorization.`

Evidence can support or challenge the hypothesis.

Correlation alone does not necessarily establish causation. Other variables may explain the observed relationship.

Potential confounding variables include:

- traffic volume;
- user population;
- geography;
- device type;
- time of day;
- release version;
- external dependency state;
- measurement changes.

## Evidence quality

Evidence should be classified rather than treated as a single undifferentiated category.

### Measured fact

Example:

`Checkout abandonment was 39% in August.`

This should be traceable to a defined measurement system.

### Observation

Example:

`Customers report uncertainty about delivery charges.`

This can be supported by interviews, surveys, usability studies, or behavioral analysis.

### Hypothesis

Example:

`A new checkout page will solve abandonment.`

This has not been established.

### Opinion

Example:

`The checkout should look simpler.`

This may be useful input, but it is not equivalent to measured evidence.

## Problem boundaries

A problem boundary defines what the investigation considers part of the problem.

For the examination submission case, the internal boundary may include:

- portal validation;
- submission API;
- queueing;
- retry logic;
- database;
- monitoring.

External conditions may include:

- student home Wi-Fi;
- internet service providers;
- examination policy;
- student device hardware.

The boundary is important because uncontrolled external conditions can otherwise make a project impossible to complete.

### Inside the boundary

An item is inside when the project can reasonably investigate, measure, modify, or directly control it.

### Outside the boundary

An item is outside when it belongs to another organization, another responsibility, another project, or a broader environmental condition.

### Undefined

An undefined item has not yet been assigned.

It should not silently be treated as either inside or outside.

## Boundary failures

### Too broad

`Improve the entire university digital experience.`

This may encompass dozens of unrelated systems, policies, processes, and user groups.

### Too narrow

`Change the color of the submit button.`

This assumes a particular implementation detail before establishing the underlying problem.

### Solution disguised as a problem

`Build a new submission service.`

This is an intervention.

### Cause disguised as a problem

`The database is too slow.`

This is a causal hypothesis unless database behavior has already been demonstrated to be responsible.

### Unbounded responsibility

`Make sure no student ever has an internet problem.`

The institution cannot directly control every student's network.

A more practical boundary can address system behavior under network failures without claiming control over external infrastructure.

## Constraints versus boundaries

These concepts are related but different.

A boundary answers:

`What belongs to this problem or investigation?`

A constraint answers:

`What limits the possible actions?`

Example:

`The submission API is inside the problem boundary.`

`The identity provider must remain unchanged.`

The first defines scope. The second restricts solution choices.

## Stakeholder perspectives

Different stakeholders can describe the same underlying problem differently.

For the examination system:

| Stakeholder | Role | Primary concern |
| --- | --- | --- |
| Student | Primary user | Successful submission before deadline |
| Faculty | Assessment owner | Valid and traceable submissions |
| IT operations | System operator | Availability and maintainability |
| Security | Risk owner | Confidentiality and integrity |
| Finance | Budget owner | Controlled infrastructure cost |

The problem definition should preserve these perspectives without allowing any single preference to become an unsupported causal claim.

## Measurable success criteria

Success criteria should correspond to the problem.

Examples:

### Submission success rate

`successful final submissions / final submission attempts`

### p95 submission latency

The 95th percentile time required to acknowledge a submission.

Percentiles are useful because averages can hide poor experiences affecting a smaller but important group.

### Duplicate submission rate

`duplicate final submissions / 1,000 attempts`

This can reveal failure modes associated with retries, timeouts, idempotency, or ambiguous client acknowledgements.

A single metric should rarely define success for a complex system. Improving one metric can damage another.

For example:

`Reducing validation could improve response time while damaging data integrity.`

A good problem frame therefore uses several complementary measures.

## Python implementation

The Python program is designed as a broad educational study file.

It demonstrates:

- `ProblemStatement` as a structured problem representation;
- `CausalNode` for causal trees;
- `five_whys()` for causal questioning;
- `ProblemFrame` for complete problem framing;
- `Boundary` for inside/outside classification;
- `EvidenceItem` for evidence classification;
- `Metric` for baseline and target comparisons;
- Pareto-style analysis;
- stakeholder modeling;
- causal hypotheses;
- before-and-after validation;
- case-study data analysis;
- complexity considerations;
- security and privacy principles.

Python's dictionaries, lists, dataclasses, enumerations, functions, and exception handling make it useful for representing analytical concepts directly.

The case study uses daily examination submission records with:

- attempts;
- successful submissions;
- payment errors;
- validation errors;
- timeouts;
- duplicate submissions.

The program calculates aggregate success and failure rates with a single pass over the data.

## JavaScript implementation

The JavaScript implementation emphasizes application behavior and event-driven evidence collection.

It demonstrates:

- classes;
- objects;
- collections;
- event handlers;
- asynchronous investigation;
- `Promise.all`;
- data reduction;
- validation;
- problem boundaries;
- structured causal hypotheses.

The `DiagnosticEventBus` represents an event-driven mechanism. Events such as:

- `submission.attempt`;
- `submission.success`;
- `submission.payment_error`;
- `submission.validation_error`;
- `submission.timeout`;
- `submission.duplicate`;

are emitted and consumed by `SubmissionMonitor`.

This is useful because real application problems are frequently discovered through observable events rather than through a single database record.

The JavaScript implementation also includes an asynchronous investigation simulation. Multiple evidence sources can be investigated concurrently with `Promise.all`.

Concurrency should still be controlled in production. Unlimited concurrent work can introduce:

- rate-limit violations;
- resource exhaustion;
- database contention;
- excessive memory usage;
- dependency overload.

## C++ case study

The C++ program develops the problem-definition concept into an industry-style technical case study.

### Problem being modeled

The modeled system is an online examination submission service.

The central condition is:

`Successful final submissions fall below the operational target during concentrated traffic.`

The case study intentionally avoids declaring a specific technical component to be the root cause without evidence.

### Major components

The modeled internal system contains:

- portal;
- validation;
- submission API;
- queue;
- database;
- retry manager;
- monitoring.

External conditions include:

- student home networks;
- internet providers;
- examination policy.

### Data model

`ExaminationRecord` represents one observation period.

Each record contains:

- date;
- number of attempts;
- successful submissions;
- payment errors;
- validation errors;
- timeout events;
- duplicate submissions.

The class-like structure also provides `successRate()` and `failures()` methods.

### Aggregation

`AggregateAnalysis` combines the records.

The analysis calculates:

- total attempts;
- successful submissions;
- success rate;
- failure rate;
- payment error rate;
- validation error rate;
- timeout rate;
- duplicate rate.

Aggregation uses a linear scan.

For `n` records:

- time complexity: `O(n)`;
- additional aggregation space: `O(1)`.

### Pareto analysis

Cause categories can be sorted by frequency.

If there are `k` categories, sorting requires approximately:

`O(k log k)`

time.

Pareto analysis helps identify concentration but does not establish causality.

A frequently observed event can be:

- a root cause;
- a downstream symptom;
- a correlated event;
- a measurement artifact.

### Before-and-after validation

The C++ implementation calculates:

- before mean;
- after mean;
- absolute change;
- relative change.

A simple before-and-after comparison can be misleading when other variables changed simultaneously.

Potential confounders include:

- traffic changes;
- seasonality;
- new software releases;
- changes in user population;
- infrastructure changes;
- measurement changes.

More rigorous investigations may require controlled experiments, comparison groups, process tracing, or other causal methods.

## Important distinctions

### Problem versus solution

Problem:

`Students experience failed submissions during peak traffic.`

Solution:

`Deploy a new submission service.`

A problem can have multiple possible solutions.

### Symptom versus cause

Symptom:

`Submission latency increases.`

Possible cause:

`Queue saturation.`

The observed symptom does not prove the proposed cause.

### Cause versus root cause

A cause can be one contributing factor.

A root cause is a sufficiently fundamental causal factor whose correction materially reduces the observed problem.

Complex systems can have multiple root causes.

### Constraint versus cause

Constraint:

`The identity provider cannot be replaced.`

Cause:

`The identity provider introduces a failure that prevents successful submission.`

The first limits available interventions. The second proposes an explanation for the observed condition.

### Boundary versus constraint

Boundary:

`The project includes the submission API.`

Constraint:

`The existing authentication mechanism must remain unchanged.`

The first defines scope. The second restricts action.

### Evidence versus opinion

Evidence:

`The timeout rate increased from 2% to 5%.`

Opinion:

`The application feels unreliable.`

Both can be useful, but they should not carry the same evidentiary status.

## Edge cases

### Multiple root causes

A reliability problem can involve several interacting mechanisms.

For example:

`High traffic -> queue growth -> latency -> client retry -> additional traffic`

The causal structure is not necessarily a straight chain.

### One cause with many symptoms

A single failed dependency can cause:

- authentication errors;
- transaction failures;
- support contacts;
- delayed processing.

### Changing baseline

A metric can change because the measurement population changed.

Suppose the number of submissions increases dramatically. An absolute number of failures may increase even while the failure rate improves.

### Rare severe events

Average performance may appear healthy even when a low-frequency event has serious consequences.

Safety, security, compliance, and financial-loss problems often require attention to severity and tail behavior rather than only average performance.

### External causes

An external system can contribute to a problem even when it is outside the project's control.

The correct response is not necessarily to expand the project indefinitely. The project can define mitigation within its boundary.

### Unknown causes

A problem does not become invalid merely because its root cause is unknown.

A valid investigation can begin with:

`We observe X under conditions Y, with a measurable gap Z, but the causal mechanism is not yet established.`

This is more rigorous than inventing a root cause.

## Common mistakes

### Starting with technology

`We need PostgreSQL.`

Technology selection should follow requirements and constraints rather than replace problem definition.

### Starting with a preferred architecture

`We need microservices.`

Architecture is a design decision, not automatically a problem.

### Using vague language

`The application is bad.`

This provides little information about the condition, scope, or measurable gap.

### Confusing correlation with causation

Two variables changing together does not establish that one caused the other.

### Ignoring external factors

A project can fail if it assumes that every relevant variable is under internal control.

### Defining only technical metrics

A technical metric should connect to a meaningful operational, user, financial, safety, or compliance outcome.

### Optimizing one metric

Reducing latency may increase error rates.

Increasing automation may increase false positives.

Reducing support time may decrease resolution quality.

A problem definition should account for important trade-offs.

### Allowing scope creep

If every related issue is added to the problem, the investigation can become impossible to complete.

Explicit exclusions help preserve focus.

## Limitations

Problem definition is not itself a complete causal-analysis methodology.

A strong problem statement cannot guarantee that the underlying cause has been correctly identified.

Five Whys can oversimplify complex systems.

Pareto analysis identifies concentration rather than causation.

Before-and-after analysis can be confounded.

Stakeholder reports can contain bias, incomplete information, or inconsistent terminology.

Metrics can be incorrectly defined or manipulated.

Boundaries can become outdated when the system, organization, or external environment changes.

For these reasons, problem definition should be treated as an iterative process. Evidence can change the frame.

## Performance considerations

Problem-definition software can range from simple documentation to large-scale diagnostic systems.

For small datasets, straightforward lists, dictionaries, vectors, and maps are sufficient.

For large operational datasets, important considerations include:

- streaming aggregation;
- indexing;
- partitioning;
- sampling;
- memory usage;
- event retention;
- query cost;
- time-series storage;
- percentile calculation;
- distributed aggregation.

A single-pass aggregation is often preferable when only totals are required.

Sorting all observations may be unnecessary when only top categories are required.

For extremely large datasets, approximate algorithms may be appropriate for some metrics, but the approximation error must be understood.

## Security considerations

Problem definition can involve sensitive operational and personal information.

Examples include:

- student identities;
- examination records;
- customer transactions;
- employee information;
- authentication events;
- security logs.

Important practices include:

- least privilege;
- data minimization;
- access logging;
- appropriate retention;
- redaction;
- aggregation;
- controlled diagnostic environments;
- separation of operational and personal data.

A diagnostic dataset should not contain sensitive information simply because it is technically available.

Security problems should also be framed as problems rather than merely as technologies.

For example:

`The system exposes unauthorized examination data under a specific request pattern`

is a problem statement.

`Add encryption`

is a possible control.

## Implementation considerations

A practical problem-definition system should maintain traceability between:

`problem -> evidence -> hypotheses -> tests -> findings -> decisions`

This relationship reduces the risk that an untested assumption becomes accepted as fact.

A useful implementation may record:

- problem identifier;
- affected actors;
- baseline;
- target;
- evidence sources;
- assumptions;
- constraints;
- exclusions;
- causal hypotheses;
- validation status;
- scope;
- timestamps;
- ownership;
- review history.

For production systems, changes to the problem definition should themselves be auditable when the problem affects regulated, safety-critical, financial, or security-sensitive operations.

## Real-world relevance

Problem definition applies across technical and non-technical environments.

### Product management

A product team can distinguish:

`customers cannot complete checkout`

from:

`build a new checkout page`.

### Software engineering

An engineering team can distinguish:

`API latency exceeds the agreed p95 threshold during peak load`

from:

`rewrite the service`.

### Cybersecurity

A security team can distinguish:

`unauthorized users can access protected records`

from:

`install a new security product`.

### Data engineering

A data team can distinguish:

`daily reporting contains inconsistent customer totals`

from:

`replace the data warehouse`.

### Operations

An operations team can distinguish:

`orders are shipped after the promised delivery window`

from:

`hire more staff`.

### Finance

A finance team can distinguish:

`forecast error exceeds the accepted threshold`

from:

`buy a new forecasting platform`.

### Public-sector systems

A public service can distinguish:

`citizens experience repeated submission failures`

from:

`replace the entire portal`.

In each case, the problem definition should precede the choice of intervention.

## End-to-end workflow

A practical workflow is:

1. Observe the undesirable condition.
2. Identify affected actors.
3. Establish evidence and a baseline.
4. Define the desired condition.
5. State the measurable gap.
6. Document context.
7. Separate symptoms from causal hypotheses.
8. Investigate causes.
9. Define boundaries and exclusions.
10. Document constraints and assumptions.
11. Define success metrics.
12. Validate the framing.

This workflow is intentionally iterative. New evidence can change the suspected cause, the boundary, the metrics, or even the original problem statement.

## Implementation correspondence

| Concept | Python | JavaScript | C++ |
| --- | --- | --- | --- |
| Problem statement | `ProblemStatement` | `ProblemStatement` | `ProblemStatement` |
| Causal structure | `CausalNode` | `CausalNode` | `CausalNode` |
| Five Whys | `five_whys()` | `fiveWhys()` | `fiveWhys()` |
| Problem frame | `ProblemFrame` | `ProblemFrame` | `ProblemFrame` |
| Boundary | `Boundary` | `ProblemBoundary` | `ProblemBoundary` |
| Evidence | `EvidenceItem` | `EvidenceItem` | `EvidenceItem` |
| Metrics | `Metric` | `Metric` | `Metric` |
| Cause analysis | Pareto analysis | `paretoAnalysis()` | `paretoAnalysis()` |
| Case-study data | Dataclasses and lists | Objects and arrays | Structs and vectors |
| Event model | Analytical functions | `DiagnosticEventBus` | System component model |
| Async behavior | Not required | `Promise.all()` | Not required |
| Validation | Before/after comparison | Hypothesis inspection | Before/after comparison |
| Security | Diagnostic principles | Diagnostic principles | Diagnostic principles |
| Complexity | Linear aggregation | `reduce()` | Linear vector traversal |

## Why the three languages are different

Python is well suited to educational analytical modeling because its data structures are concise and its functions can directly express concepts such as evidence collections, metrics, causal trees, and validation.

JavaScript is particularly useful for demonstrating application behavior. The event bus illustrates how problem evidence can emerge from events in a running application. Its asynchronous functions show how multiple diagnostic operations can execute concurrently.

C++ exposes more implementation structure. Explicit types, vectors, maps, classes, and compilation requirements make it useful for demonstrating how a problem-definition model can become part of a structured technical system.

The goal is not to make the same implementation three times. Each language emphasizes a different aspect of the problem-definition process.

## Technical design principles demonstrated

### Separation of concerns

Problem description, evidence, causal reasoning, boundary management, and measurement are represented separately.

This prevents a single data structure from becoming responsible for unrelated concepts.

### Explicit state

Important concepts such as baseline, target, confidence, scope, and evidence type are stored explicitly.

Implicit assumptions are harder to validate.

### Validation before interpretation

The implementations validate required problem fields before treating a statement as sufficiently structured.

### Defensive handling

Empty datasets and invalid numeric conditions are considered.

The C++ implementation throws an exception for invalid before-and-after samples.

### Evidence-driven reasoning

The programs deliberately distinguish observed data from hypotheses.

This is central to responsible technical diagnosis.

## Practical problem-definition template

A useful generic structure is:

`[Affected actor] experiences [current condition].`

`The measurable gap is [baseline] compared with [target].`

`This matters because [consequence].`

`Evidence includes [evidence sources].`

`The investigation covers [scope].`

`The investigation excludes [exclusions].`

`Important constraints include [constraints].`

`The current causal hypotheses are [hypotheses].`

`Success will be measured using [metrics].`

This structure should be adapted to the actual problem rather than copied mechanically.

## Final practice example

A retail example can be framed as:

`Retail customers abandon carts before payment completion. Conversion is 58% while the agreed target is 70%, creating lost orders and expected revenue. Analytics show high exits on the payment step, payment-error sessions show higher abandonment, and the effect is concentrated during evening traffic peaks. The scope is the web purchase flow over the previous six weeks.`

This statement is intentionally different from:

`Build a better checkout.`

The first describes a measurable condition and provides evidence. The second immediately selects an intervention without establishing whether that intervention addresses the underlying cause.
