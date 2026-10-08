# Solution Design: Hypotheses, Constraints, Trade-offs, and Alternatives

## Purpose

Solution design converts an ambiguous problem into an explicit decision model. The central concern is not simply choosing an architecture or implementation. A sound design records why a solution is believed to work, which conditions it must satisfy, which alternatives were considered, and what is deliberately sacrificed in the selected option.

The implementations in this repository use a common scenario: designing an operational event-intake system for bursty traffic. Three architectural alternatives are compared:

- A direct synchronous API keeps the interaction simple but makes the client wait for downstream processing.
- A queue-backed asynchronous architecture separates request acknowledgement from processing and introduces durable buffering.
- A managed event-streaming architecture provides stronger throughput and replay characteristics while increasing cost and operational complexity.

The scenario is deliberately useful for demonstrating solution-design reasoning because no alternative is universally superior. The correct choice depends on evidence, constraints, priorities, and the consequences of each trade-off.

## Core Solution-Design Model

A solution hypothesis is an assumption that can influence architecture but should not automatically be treated as fact.

For example, the hypothesis `H-ASYNC` states that asynchronous processing can absorb bursts while keeping client-visible latency low. The design does not simply accept that statement. It associates the hypothesis with required evidence and evaluates an observed measurement against an expected threshold.

This distinction matters because assumptions become dangerous when they silently become architecture.

A constraint is different from a hypothesis. A constraint describes a condition that the solution must satisfy or a boundary within which the solution must operate.

The example includes:

| Constraint | Type | Design implication |
| --- | --- | --- |
| `C-LATENCY` | Non-functional | The acknowledgement path must remain responsive. |
| `C-DURABILITY` | Technical | Accepted events cannot disappear merely because a consumer restarts. |
| `C-BUDGET` | Business | Infrastructure and operating costs cannot grow without limit. |
| `C-AUDIT` | Regulatory | Decisions and processing outcomes must remain traceable. |

A solution alternative is a concrete approach that can be compared against the problem and its constraints. Alternatives should be sufficiently distinct to expose meaningful architectural choices.

A trade-off describes the consequence of choosing one property over another. It should not be hidden merely because a numerical score exists.

## Hypotheses and Evidence

The Python, JavaScript, C++, Java, and SQL implementations all preserve the distinction between an assumption and an evaluated design decision.

A hypothesis contains:

- an identifier;
- a statement;
- evidence that should be collected;
- a state such as proposed, validated, or rejected;
- a confidence value.

The Python implementation provides the most explicit evidence-evaluation mechanism. `SolutionHypothesis.validate()` compares observed evidence with an expected threshold and updates the hypothesis state.

The Java implementation represents the resulting state as an immutable record. This makes a hypothesis evaluation return a new domain value instead of silently mutating an existing object.

The SQL implementation stores evidence separately in `hypothesis_evidence`. This is important for auditability because a final confidence value alone does not explain where the decision came from.

Evidence does not automatically prove that a solution is correct. It reduces uncertainty about a particular assumption. A load test may support an asynchronous-latency hypothesis without proving that asynchronous processing is the best architecture for every operational requirement.

## Constraints

Constraints define the design boundary.

A hard constraint represents a condition that should invalidate an alternative when it cannot be satisfied. A soft constraint can influence preference without necessarily eliminating an option.

The implementations distinguish constraint categories because they have different origins:

- Functional constraints describe required behavior.
- Non-functional constraints describe qualities such as latency or capacity.
- Technical constraints arise from platform or integration requirements.
- Business constraints describe cost, organizational, or commercial boundaries.
- Regulatory constraints arise from governance, traceability, or compliance obligations.

This classification prevents a design discussion from treating every requirement as though it had the same decision semantics.

The SQL implementation goes further by representing alternative-to-constraint relationships explicitly. This allows queries to expose hard constraints that an alternative does not satisfy rather than burying all decisions in application code.

## Solution Alternatives

The example compares three fundamentally different processing models.

### Direct synchronous API

The client sends a request and waits while downstream processing completes.

Its strengths are simplicity, straightforward request tracing, and relatively low infrastructure complexity.

Its weakness is coupling between client latency and downstream processing. A downstream slowdown can directly become a client-facing slowdown. Burst traffic can therefore make response-time behavior difficult to control.

This alternative receives a penalty in the example because the latency and burst-handling constraints are less naturally satisfied.

### Queue-backed asynchronous architecture

The API validates and accepts work, places a durable message into a queue, and allows workers to process the message independently.

The important design mechanism is temporal decoupling. The client does not have to wait for the worker to finish.

The architecture introduces new concerns:

- duplicate delivery;
- consumer failure;
- retry behavior;
- dead-letter handling;
- idempotent processing;
- queue growth;
- observability across asynchronous boundaries.

The example selects this alternative because it provides a balanced combination of latency, durability, scalability, maintainability, and implementation cost.

### Managed event-streaming architecture

A partitioned event stream treats event distribution and replay as first-class capabilities.

This architecture is attractive when very high throughput, multiple independent consumers, ordering within partitions, or historical replay are central requirements.

Its disadvantages include greater platform complexity, higher operating cost, more sophisticated partitioning decisions, and additional operational knowledge.

The design therefore does not select it simply because its scalability score is highest. The alternative's cost, risk, maintainability, and reversibility affect the final decision.

## Trade-offs

A score is useful for comparing alternatives, but a score is not the same thing as a design rationale.

The implementations intentionally expose the trade-offs separately.

For latency, asynchronous processing is preferred because acknowledgement is decoupled from downstream completion.

For operational simplicity, synchronous processing is preferred because fewer components and fewer asynchronous failure states are easier to operate.

For replay, event streaming is preferred because durable partitioned streams naturally support historical consumption.

These statements can simultaneously be true. A design decision does not require one alternative to be objectively best across every dimension.

The selected solution is therefore a constrained preference, not a universal technical truth.

## Decision Scoring

The implementations use an explicit scoring function:

`score = expected value + scalability contribution + maintainability contribution + reversibility contribution - risk contribution - delivery cost contribution - operating cost contribution - constraint penalty`

The exact weights are illustrative. They demonstrate an important design principle: weighting criteria is itself a decision.

If cost becomes more important, cost weights should increase.

If replay becomes mandatory rather than desirable, replay should probably become a hard constraint rather than merely receiving a higher score.

If implementation risk becomes unacceptable, a hard constraint or risk threshold may be more appropriate than continuously subtracting points.

A numerical score should therefore support reasoning rather than replace it.

## Python Implementation

The Python program models the complete decision process with domain-oriented classes.

`SolutionHypothesis` represents evidence-backed assumptions. `Constraint` captures design boundaries. `Alternative` stores measurable decision criteria and calculates a transparent score. `SolutionDesign` coordinates hypotheses, constraints, alternatives, ranking, and selection.

The program also performs sensitivity analysis. It changes cost or scalability assumptions and recalculates the selected alternative's score. This demonstrates that a design decision depends on its inputs rather than being an immutable fact.

The JSON export provides a machine-readable representation of the design state. This is useful when a decision record must later be persisted, compared, or consumed by another system.

The Python program also rejects invalid evidence-quality values and refuses to select an alternative while hypotheses remain unresolved.

## JavaScript Implementation

The JavaScript implementation approaches the same design problem through event-driven behavior.

`SolutionDesign` maintains hypotheses, constraints, and alternatives and emits events when domain objects are added or a decision is selected.

This demonstrates an important JavaScript-specific design possibility: solution-design tooling can be integrated into event-driven applications where changes to assumptions or decisions trigger other processing.

The implementation also separates the ranking operation from the decision operation. Ranking produces an ordered evaluation, while decision-making selects the highest-ranked alternative only after unresolved hypotheses have been checked.

The validation example demonstrates failure handling for invalid evidence rather than silently accepting malformed decision inputs.

## C++ Case Study

The C++ program models a repository-independent governance engine for an operational event-intake architecture.

`GovernanceEngine` owns the design state and exposes operations for adding hypotheses, constraints, and alternatives. The engine refuses to make a decision when a hypothesis remains unresolved.

The case study emphasizes explicit value semantics and deterministic ranking. `Alternative::score()` contains the scoring model directly, making the decision calculation inspectable.

The program also performs budget sensitivity analysis by modifying delivery and operating cost for the selected architecture. This demonstrates why a solution should be tested against plausible changes in business conditions.

The C++ implementation uses standard containers and algorithms and compiles with C++17 or later. No external dependency is required.

## Java Enterprise Model

The Java implementation models the design as a small enterprise-oriented domain.

Enums represent domain states and constraint categories. Records represent immutable domain values such as `Hypothesis`, `Constraint`, `Alternative`, `TradeOff`, and `Decision`.

The immutable `Hypothesis.evaluate()` operation is significant. Rather than changing an existing hypothesis in place, it returns a new evaluated value. This reduces accidental state mutation and makes state transitions explicit.

`DesignRepository` acts as a domain service and coordinates:

- uniqueness validation;
- unresolved-hypothesis detection;
- alternative ranking;
- decision creation;
- trade-off representation.

This approach is useful when solution decisions must be treated as governed business-domain objects rather than as temporary print statements.

## SQL Data Model

The PostgreSQL implementation treats solution design as persistent decision data.

The `solution_case` table represents the problem being designed.

The `hypothesis` table stores assumptions and their states. `hypothesis_evidence` stores the measurements supporting those states. Keeping evidence separate makes the decision traceable.

The `design_constraint` table stores the boundaries of the solution.

The `alternative` table contains the candidate solutions and their evaluation dimensions.

`alternative_constraint` records whether a particular alternative satisfies a particular constraint. This relationship is important because two alternatives may have very different failure modes against the same constraint.

`trade_off` stores explicit design compromises rather than reconstructing them from numerical scores.

`decision` records the final selected or rejected state.

## Database Integrity

The SQL script uses PostgreSQL constraints to prevent invalid data at the persistence layer.

Foreign keys prevent orphaned hypotheses, alternatives, constraints, evidence, and decisions.

Unique constraints prevent duplicate hypothesis codes and alternative names within a solution case.

Check constraints prevent confidence, evidence quality, and cost values from entering invalid ranges.

Indexes support common access patterns such as retrieving hypotheses by solution case and state, alternatives for a solution case, and evidence belonging to a hypothesis.

The final decision is inserted inside a transaction. This ensures that the set of decision records is written atomically.

## Querying the Design

The SQL views expose the calculated alternative score without permanently storing a derived value.

Window functions rank alternatives within a solution case.

The hard-constraint query identifies alternatives that violate mandatory requirements. This is different from ordinary score ranking: an alternative can have a high score while still being unacceptable if it violates a hard constraint.

This distinction is central to good solution design.

A weighted score answers:

> Which alternative appears preferable under the selected evaluation model?

A hard constraint answers:

> Which alternatives are not acceptable regardless of their score?

Those questions should not be conflated.

## Architecture Selection Logic

The example follows this relationship:

`Problem -> Hypotheses -> Evidence -> Constraints -> Alternatives -> Evaluation -> Trade-offs -> Decision`

A hypothesis reduces uncertainty.

A constraint establishes a boundary.

An alternative represents a possible solution.

Evaluation compares alternatives against the stated decision criteria.

A trade-off records what is gained and sacrificed.

The decision records the resulting choice.

This structure prevents a common design failure in which an implementation is selected first and its justification is constructed afterward.

## Common Design Failure Modes

### Treating assumptions as requirements

An assumption such as "traffic will remain low" is not automatically a requirement. It should be identified and tested. If evidence later invalidates it, the solution architecture may need to change.

### Using scores without hard constraints

A high score cannot compensate for an alternative violating a mandatory regulatory or technical condition. Mandatory requirements need explicit enforcement.

### Listing alternatives that are not meaningfully different

Comparing three implementations that differ only in configuration does not provide useful architectural choice. Alternatives should expose genuinely different consequences.

### Hiding trade-offs

A design document that says an option is "best" without explaining cost, risk, complexity, reversibility, and operational consequences is incomplete.

### Confusing confidence with certainty

A confidence value represents the strength of current evidence. It does not mean the architecture has been proven universally correct.

### Optimizing one dimension

Selecting solely for performance can produce excessive cost or operational complexity. Selecting solely for low cost can create unacceptable reliability or scalability limits.

## Performance Considerations

The decision engine itself uses small in-memory collections, so its computational cost is dominated by alternative ranking.

For `n` alternatives, sorting requires approximately `O(n log n)` time. Hypothesis and constraint lookups use maps in the Python, JavaScript, and C++ implementations, providing efficient lookup by identifier.

The SQL model relies on indexes for frequently filtered relationships. For larger decision repositories, indexes should be selected based on actual query plans rather than added indiscriminately.

The real performance problem in the example is architectural rather than computational. The solution must manage burst traffic, downstream processing latency, buffering, and throughput. A fast scoring function does not make an unsuitable production architecture fast.

## Security and Governance Considerations

A solution-design system can contain commercially sensitive architecture decisions, operational constraints, risk assessments, and regulatory information.

Decision records should therefore have appropriate access control.

Evidence should preserve provenance so that measurements cannot be detached from their source or silently replaced.

Changes to important constraints and selected alternatives should be auditable.

Sensitive infrastructure information should not be embedded in unrestricted decision descriptions.

The design process should also distinguish an architecture decision from authorization to deploy that architecture. Selecting an alternative does not automatically grant production access.

## Debugging and Validation

The implementations deliberately fail fast when required design information is missing or invalid.

Examples include:

- evidence quality outside the valid range;
- duplicate identifiers;
- unresolved hypotheses;
- missing alternatives;
- invalid numeric cost values;
- hard constraints that are not satisfied.

These checks are important because design errors should be exposed near the decision boundary rather than discovered after implementation.

Sensitivity analysis is another validation technique. If a tiny change in one assumption completely changes the selected architecture, that assumption deserves additional investigation.

## Limitations

The scoring model is illustrative rather than a universal decision framework. Real organizations may use financial models, risk matrices, weighted decision matrices, architecture review boards, regulatory controls, or formal optimization methods.

The example also treats criteria as largely independent. Real systems can contain strong interactions. For example, higher scalability may increase operational complexity, and stronger durability may increase cost.

The implementation does not attempt to calculate total cost of ownership, probability distributions, Monte Carlo risk, capacity planning, or formal multi-objective optimization.

Those limitations are deliberate. The central purpose is to make the reasoning structure explicit: assumptions are tested, constraints are identified, alternatives are compared, trade-offs are recorded, and the resulting decision is made auditable.
