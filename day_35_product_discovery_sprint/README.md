# Product Discovery Sprint

## Scope

This repository models a product discovery sprint as an evidence-driven workflow rather than as a feature-planning exercise.

The scenario used across the implementations is a B2B procurement product serving procurement managers who need to discover, compare, qualify, and review suppliers.

The central discovery problem is specific:

> Procurement teams spend substantial effort reconstructing supplier information, verifying qualification evidence, and explaining why suppliers were placed on shortlists.

The sprint separates four distinct activities:

- **Discovery planning** defines the product question, target segment, business outcome, research questions, constraints, and sprint cadence.
- **Research** collects observations from interviews, workflow observation, analytics, support records, and survey-style evidence.
- **Synthesis** converts individual observations into evidence-backed themes and opportunity statements without prematurely selecting a solution.
- **Ideation** creates alternative mechanisms for addressing validated opportunities.
- **Validation** tests whether proposed mechanisms change observable behavior and produces an explicit continue, iterate, or stop decision.

The distinction matters because a discovery sprint should not move directly from a stakeholder request to a feature specification. The intermediate evidence and reasoning need to remain traceable.

## Discovery planning

The sprint begins with a defined business outcome:

`Reduce time spent identifying and comparing qualified suppliers`

That outcome does not prescribe a feature. It leaves room to investigate whether the real problem is comparison, supplier qualification, market coverage, shortlist review, or another part of the workflow.

The Python implementation represents the plan through `SprintPlan`. The plan contains research questions and explicit constraints. The Java implementation uses `ResearchQuestion` records and `SprintController` to make the progression of the sprint explicit.

A strong discovery question describes something that can be investigated.

For example:

`Where does supplier discovery break down during an active procurement request?`

is researchable.

By contrast:

`Should we build an AI supplier recommendation dashboard?`

already assumes the solution.

The sprint calendar separates research from synthesis and validation. This protects the team from selecting a concept before enough evidence exists.

Planning also establishes constraints such as anonymized research data, no production changes during discovery, and the requirement to validate the problem before validating the solution.

## Research design

Research evidence is deliberately mixed.

Interviews reveal participant reasoning, perceived friction, workarounds, and decision criteria.

Observation reveals behavior that participants may not mention. In the case study, a buyer says that supplier comparison is difficult, while observation shows the actual mechanism: opening several supplier pages and manually copying attributes into a spreadsheet.

Analytics provides behavioral evidence at a larger scale. The example uses repeat supplier-page visits combined with relatively low shortlist conversion.

Support evidence exposes recurring operational friction. Repeated requests about where qualification evidence is stored are useful because they represent actual workflow failure rather than a hypothetical preference.

Survey-style evidence can estimate prevalence, but a percentage alone does not establish causality. The Python model therefore keeps frequency and severity separate from confidence.

The evidence records contain:

- source identifier
- evidence type
- participant when applicable
- statement
- severity
- frequency
- confidence
- tags

This structure supports traceability from a synthesized theme back to its supporting observations.

## Evidence quality

Not all evidence has equal strength.

A participant saying that a feature would be useful is weaker than successfully completing a realistic task with a prototype. A single interview statement may reveal an important problem but does not establish how widespread it is.

The Python implementation calculates a transparent signal using severity, logarithmic frequency, and confidence:

`severity × log(1 + frequency) × confidence`

The logarithmic frequency treatment prevents repeated low-quality records from automatically dominating the analysis.

The C++ implementation uses a similar logarithmic signal. This is an explicit modeling choice rather than a claim that the formula is a universal research standard.

Evidence should remain inspectable. The SQL model therefore stores individual evidence records and connects them to themes through `theme_evidence`.

## Synthesis

Synthesis is the transition from individual observations to patterns.

The case study produces distinct themes:

### Manual comparison burden

Buyers reconstruct supplier attributes in spreadsheets because supplier sources do not provide a consistent comparison context.

The evidence includes direct interviews and workflow observation. This theme is specifically about the mechanics and effort of comparison.

### Qualification evidence gap

Procurement teams need to establish whether supplier claims and certifications can be trusted.

This theme is different from comparison friction. Its central question is evidence validity and verification rather than the effort required to put supplier attributes side by side.

### Shortlist verification friction

Procurement leads may receive a shortlist but still lack the evidence needed to understand why each supplier was recommended.

This is a review and decision-traceability problem rather than simply a supplier-search problem.

Keeping these themes distinct prevents the synthesis from collapsing every observation into an overly broad statement such as "supplier discovery is difficult."

## Opportunity framing

An opportunity describes an unmet user need or behavior without prematurely defining the implementation.

For example:

`Procurement managers need comparable supplier evidence without manually reconstructing equivalent fields.`

This describes the desired condition without saying that the product must use a table, dashboard, browser extension, or recommendation engine.

The opportunity also specifies a target behavior:

`Complete supplier comparisons using normalized evidence.`

That target behavior is useful during validation because the team can measure whether a proposed intervention actually changes the workflow.

The Python, C++, Java, and SQL implementations retain the relationship:

`theme -> opportunity`

This prevents an attractive concept from becoming detached from the evidence that originally justified investigation.

## Ideation

Ideation begins only after opportunities have been identified.

The examples deliberately use different mechanisms rather than renaming the same feature:

- `Evidence comparison workspace` normalizes supplier attributes and places source evidence beside each field.
- `Qualification evidence ledger` focuses on certification claims, verification state, source provenance, and evidence freshness.
- `Decision evidence packet` focuses on the evidence required to review a supplier shortlist.

These concepts address related problems but operate at different workflow points.

The concept model contains confidence, effort, and reach. The score used in the implementations is:

`confidence × reach ÷ effort`

This is a prioritization heuristic, not a replacement for research judgment. Its purpose in the code is to demonstrate how a team can make the assumptions behind prioritization explicit.

## Validation

Validation is based on behavior rather than enthusiasm.

The example experiments use metrics such as:

`Supplier comparison task completion`

and

`Qualification verification task completion`

A validation record stores:

- participant count
- baseline
- observed rate
- threshold
- qualitative signal
- decision
- interpretation

The decision policy used by the Python, JavaScript, C++, and Java implementations has three outcomes.

**Continue** is returned when both the quantitative and qualitative thresholds are met.

**Iterate** is returned when one evidence dimension passes but the other remains insufficient.

**Stop** is returned when neither dimension provides enough evidence.

This prevents a single favorable observation from being treated as proof.

The SQL implementation stores the same concept through `experiments` and `experiment_results`, allowing validation results to be queried independently of the application that generated them.

## Python implementation

The Python program is a complete discovery workflow simulator.

`SprintPlan` represents discovery planning. `Participant`, `ResearchObservation`, `Theme`, `Opportunity`, `Concept`, and `Experiment` form the domain model.

`collect_research_observations()` creates mixed-method evidence. The records include interviews, observations, support information, analytics, and survey-style evidence.

`synthesize_themes()` performs transparent tag-based qualitative clustering. It does not pretend that automated clustering is equivalent to expert qualitative research. The explicit mapping makes the reasoning auditable.

`build_opportunities()` translates themes into behavior-oriented opportunity statements.

`generate_concepts()` creates distinct mechanisms for the opportunities.

`create_experiments()` converts concepts into measurable validation tests.

`run_validation()` applies the decision policy.

`validate_discovery_integrity()` checks traceability between evidence, themes, opportunities, concepts, and experiments. This is important because discovery artifacts can look polished while containing broken evidence relationships.

The Python program also handles zero-baseline measurement, invalid sprint duration, missing evidence, invalid probability values, and small validation samples.

The statistical demonstration calculates an approximate interval around an observed completion rate. This reinforces that an observed proportion from a small sample is an estimate, not an exact representation of all users.

## JavaScript implementation

The JavaScript implementation takes an event-driven approach.

`DiscoverySprint` extends Node.js `EventEmitter`. State changes, evidence creation, synthesis, concept creation, and experiment completion generate events.

This is useful for discovery systems that need audit trails or asynchronous research operations. A user research platform could listen for experiment completion and persist results, update a research dashboard, or trigger another workflow.

The sprint state machine is explicit:

`planned -> researching -> synthesizing -> ideating -> validating -> decided`

Invalid transitions throw errors rather than silently allowing the workflow to become inconsistent.

`runExperiment()` is asynchronous. The example uses a short Promise delay to model an external research operation. A production implementation could replace that operation with a prototype-testing service, analytics query, or research system.

The JavaScript model also keeps evidence as immutable objects and uses `Set` for evidence tags. Concept ranking is implemented separately from research collection so that discovery data and prioritization logic remain distinct.

## C++ case study

The C++ implementation models a repository-independent discovery engine for a B2B procurement product.

`DiscoveryEngine` owns evidence, themes, opportunities, concepts, and experiments.

The engine enforces important relationships:

- A theme cannot be created without supporting evidence.
- An opportunity must reference an existing theme.
- A concept must reference an existing opportunity.
- An experiment must reference an existing concept.
- Validation probabilities must remain within the interval `[0, 1]`.
- Ten-point prioritization scores must remain within `[0, 10]`.
- Validation experiments require a minimum participant count in the modeled policy.

The C++ program uses `std::set` for tags and `std::vector` for ordered domain collections. Ranking uses standard-library sorting algorithms.

The case study also demonstrates a deliberate performance characteristic. Evidence-to-theme matching is approximately `O(E × T)` for evidence records `E` and themes `T` in the simple tag-intersection implementation. Ranking is `O(n log n)`.

For a small discovery sprint this is appropriate because transparency is more important than building a complex indexing layer. A production-scale research repository could use indexed tags or a database query engine rather than repeatedly scanning all evidence.

## Java implementation

The Java implementation uses an enterprise-oriented domain model.

Immutable Java records represent:

- `ResearchQuestion`
- `Participant`
- `Evidence`
- `Theme`
- `Opportunity`
- `Concept`
- `ExperimentResult`
- `Assumption`

The `DiscoveryRepository` provides in-memory persistence and enforces domain references between entities.

`ResearchService` owns synthesis behavior.

`ValidationService` owns experiment validation.

`ValidationPolicy` separates validation rules from experiment storage. `ThresholdValidationPolicy` implements the current policy.

The explicit policy abstraction is important because validation rules frequently change. A team might later require different quantitative thresholds by experiment type or introduce confidence intervals, task-level error rates, or segment-specific thresholds. The service should not have to be rewritten simply because the decision policy changes.

`SprintController` implements explicit phase transitions. The controller prevents a sprint from jumping from planning directly to validation.

The Java program also models failure states by rejecting an opportunity that references an unknown theme.

## SQL data model

The PostgreSQL schema represents the discovery domain relationally.

`discovery_sprints` stores sprint scope and business outcome.

`research_questions` stores questions tied to a sprint.

`participants` stores anonymized research participants.

`research_evidence` stores individual observations and supporting metadata.

`evidence_tags` provides many-to-many tagging without placing an arbitrary number of tags into a single text column.

`themes` stores synthesized patterns.

`theme_evidence` preserves the relationship between a theme and the observations that support it.

`opportunities` separates unmet needs from solutions.

`concepts` represents proposed mechanisms.

`experiments` defines the validation design.

`experiment_results` stores measured outcomes and explicit decisions.

`assumptions` records important uncertainties that may invalidate a direction.

Foreign keys prevent concepts from referencing nonexistent opportunities and experiments from referencing nonexistent concepts.

Check constraints prevent impossible values such as negative participant counts, probabilities above 1, and scores outside their intended range.

The SQL script also creates indexes for sprint-scoped evidence retrieval, evidence types, participants, tags, theme relationships, opportunities, concepts, experiments, and assumptions.

## SQL views

`evidence_signal_view` exposes a consistent evidence signal without duplicating the calculation in every query.

`theme_priority_view` ranks themes using user impact, frequency, and strategic fit.

`opportunity_priority_view` separates opportunity prioritization from concept prioritization.

`concept_priority_view` applies the concept confidence, reach, and effort model.

`validation_view` combines experiment configuration with measured results, relative lift, and the final decision.

`assumption_risk_view` identifies assumptions whose combination of importance, uncertainty, and weak evidence creates high discovery risk.

These views allow the database to answer questions such as:

- Which evidence is strongest?
- Which themes have the strongest evidence-backed opportunity?
- Which concepts have the best validation economics?
- Which experiments passed their thresholds?
- Which assumptions remain dangerous?

## Database integrity and transactions

The SQL script demonstrates a transaction around an invalid experiment insertion.

The experiment attempts to store a negative participant count. The database's `CHECK (participants >= 5)` rule prevents the invalid state.

This illustrates an important boundary.

Application code should validate input before submitting a transaction, but database constraints should still protect core relational invariants because applications can contain bugs, multiple clients may write to the same database, and data-import jobs can bypass normal UI validation.

The database should not attempt to encode every qualitative research judgment. Whether an observation represents a meaningful theme is a research interpretation. Whether a participant count can be negative is an objective integrity rule and belongs naturally in the database.

## Discovery traceability

The most important structural relationship in the implementation is:

`research question -> evidence -> theme -> opportunity -> concept -> experiment -> decision`

The chain allows a team to ask why a concept exists.

A concept should be traceable to an opportunity.

The opportunity should be traceable to a synthesized theme.

The theme should be supported by concrete evidence.

The experiment should test a meaningful behavior associated with the concept.

The final decision should therefore be connected to observed evidence rather than merely to stakeholder preference.

The SQL traceability queries expose these relationships directly. The Python validation function and Java repository enforce related relationships in application memory. The C++ engine rejects missing relationships during object creation.

## Discovery versus delivery

Product discovery is not the same as product delivery.

Discovery asks whether a problem is sufficiently important, whether the underlying behavior is understood, which opportunity is worth addressing, and whether a proposed mechanism changes behavior.

Delivery begins when the team has enough evidence to define and implement a product change with acceptable uncertainty.

A discovery sprint therefore should not be judged by the number of features produced.

In the case study, the useful output is not simply "build an evidence comparison workspace." The useful output includes the evidence that comparison is a problem, the specific behavior that needs to change, the assumptions behind the concept, the experiment used to test it, and the resulting decision.

## Common discovery failure modes

### Starting with the solution

A stakeholder request such as "build supplier recommendations" can bias research toward confirming that solution.

The implementations avoid this by defining research questions before concepts.

### Treating interviews as behavioral proof

Participants can accurately describe their experiences, but stated intention is not equivalent to observed behavior.

The case study combines interviews with workflow observation and validation tasks.

### Treating frequency as importance

A common low-impact issue may appear many times while a rare but high-risk qualification failure may deserve more attention.

The evidence model therefore retains severity and frequency as separate properties.

### Conflating opportunity and concept

"Buyers need comparable supplier evidence" is an opportunity.

"Build an evidence comparison workspace" is a concept.

Keeping these separate preserves the ability to explore alternative solutions.

### Using preference voting as validation

A concept can receive strong enthusiasm and still fail in actual use.

The validation models therefore use task completion and qualitative signals rather than a simple "would you use this?" vote.

### Ignoring contradictory evidence

One participant may prioritize speed while another prioritizes market coverage.

Contradictions are useful because they can reveal segmentation, contextual differences, or competing jobs. They should not automatically be averaged away.

### Treating a small sample as precise

Eight successful tasks out of eight is encouraging, but it does not prove universal behavior.

The Python program demonstrates uncertainty around observed proportions to reinforce this limitation.

## Prioritization considerations

Discovery prioritization should account for several dimensions.

**User impact** captures the severity of the unmet need.

**Evidence strength** captures how well the problem is supported.

**Business value** connects the opportunity to a meaningful product or organizational outcome.

**Feasibility** reflects whether the organization can realistically investigate or address the opportunity.

**Confidence** expresses how much evidence currently supports a concept.

**Effort** captures the cost of testing or implementing a concept.

**Reach** estimates how broadly the mechanism could affect the target behavior.

These dimensions are intentionally kept separate in the data model. Combining them into one score too early can hide why a concept ranks highly.

## Validation interpretation

The comparison workspace experiment observes an 87.5% task completion rate against a 75% threshold and produces a strong qualitative signal. The modeled decision is `continue`.

The qualification evidence ledger observes 62.5% completion against a 75% threshold while still producing a meaningful qualitative signal. The decision is `iterate`.

This distinction is important. Iteration does not mean that the opportunity was invalid. It means that the tested mechanism has not yet produced sufficient evidence.

A discovery team should preserve the failed or partial experiment rather than deleting it. It represents learned information and changes the uncertainty surrounding the concept.

## Assumption management

The implementations include assumptions because discovery decisions are usually constrained by uncertainty.

Examples include:

`Procurement managers will trust normalized supplier attributes only when important fields retain visible evidence provenance.`

and

`Supplier qualification evidence can remain sufficiently current to support decisions.`

The risk model uses:

`importance × uncertainty × (1 - evidence level)`

This highlights assumptions that are important, uncertain, and weakly supported.

A high-risk assumption can be a better target for the next experiment than a low-risk usability refinement.

## Security and privacy considerations

Research data can contain commercially sensitive information, participant statements, supplier information, and internal workflow details.

The examples use participant codes such as `P-001` instead of personal identities.

A production implementation should apply access controls to raw research records, separate participant identity from research content where appropriate, encrypt stored sensitive information, audit access to research data, and avoid exposing confidential supplier information in public analytics.

Qualitative evidence should also be treated carefully during synthesis. A research statement should not be transformed into an unsupported claim about an entire market segment.

The SQL schema provides relational integrity but is not itself a complete security architecture. Production deployments require database roles, least-privilege permissions, encrypted connections, backup controls, retention rules, and appropriate audit logging.

## Performance considerations

The discovery datasets used in a sprint are generally small, so transparent algorithms are preferable to unnecessary infrastructure.

The Python and C++ implementations scan evidence records during synthesis. This is easy to inspect and sufficient for hundreds or thousands of observations.

The SQL implementation uses indexes where recurring filtering and joins have a clear performance benefit.

At larger scale, research evidence could reach millions of records across multiple products and years. At that point, tag indexes, full-text search, partitioning, materialized views, analytical databases, or specialized research retrieval infrastructure may become appropriate.

The performance model should follow actual workload characteristics rather than being introduced merely because the dataset is technically large.

## Design boundaries

The implementations intentionally do not pretend that discovery can be reduced to a single mathematical formula.

Scoring functions make assumptions visible, but they do not replace product judgment.

Tag-based synthesis makes evidence traceable, but qualitative research still requires interpretation.

Threshold validation creates a repeatable decision rule, but thresholds must reflect experiment type, risk, sample size, and business context.

A discovery sprint is therefore best treated as a structured decision process in which evidence reduces uncertainty rather than as a machine that produces a guaranteed product answer.
