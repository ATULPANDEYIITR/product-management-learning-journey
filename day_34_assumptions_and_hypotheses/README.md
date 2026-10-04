# Assumptions & Hypotheses: Assumption Mapping, Desirability, Viability, Feasibility, and Risk

## Scope

This repository models an evidence-driven approach to evaluating uncertain decisions. The central distinction is between an **assumption** and a **hypothesis**.

An assumption is a belief required for a proposed decision, product, operating model, or technical solution to work. It may be informed by experience, observation, research, historical data, or expert judgment, but it remains uncertain until evidence is collected.

A hypothesis turns that uncertainty into a falsifiable statement. It specifies what should be observed, which metric will be used, what threshold constitutes support, and what evidence would cause the claim to be rejected.

The implementations organize assumptions across four distinct dimensions:

| Dimension | Core question | Typical evidence |
|---|---|---|
| Desirability | Do users or stakeholders value the proposed outcome strongly enough to change behavior? | Interviews, surveys, prototype tests, behavioral observations |
| Viability | Can the proposed outcome produce sustainable economic or operating value? | Price tests, financial models, cost analysis, purchasing behavior |
| Feasibility | Can the organization technically and operationally deliver the outcome under realistic constraints? | Technical spikes, load tests, architecture experiments, security tests |
| Risk | What is the consequence if an important assumption is wrong, and how likely is that failure? | Production telemetry, failure analysis, controlled exposure, incident data |

These dimensions are related but should not be collapsed into a single generic confidence score.

## Assumptions and Hypotheses

An assumption describes an uncertain condition required for a decision.

For example:

`Operations managers value automated exception monitoring enough to change their current workflow.`

This is an assumption because it expresses a belief about behavior without specifying exactly how the belief will be tested.

A hypothesis makes the claim measurable:

`At least 65% of qualified managers will rank automated exception monitoring among their top three workflow improvements.`

The hypothesis defines:

- a population or sample,
- an observable metric,
- a threshold,
- a direction of acceptance,
- and a sample requirement.

The distinction prevents vague statements such as "customers will like it" from being treated as evidence-bearing conclusions.

## Assumption Mapping

The Python implementation uses the `Assumption` data structure to represent an assumption as a first-class decision object.

Each assumption contains:

- an identifier for traceability,
- the actual assumption statement,
- one of the four dimensions,
- an initial confidence estimate,
- impact if the assumption fails,
- uncertainty,
- an accountable owner,
- rationale,
- and accumulated evidence.

This creates a traceable relationship between a strategic belief and the evidence used to challenge it.

The implementation also calculates an **exposure** value:

`exposure = impact × uncertainty`

Exposure is intentionally different from confidence.

A highly consequential assumption can deserve immediate investigation even if the team currently believes it is probably true. Conversely, an uncertain assumption with negligible consequences may not justify an expensive experiment.

The registry maintains explicit relationships:

`Assumption → Hypothesis → Experiment → Observation → Evaluation`

That relationship is more useful than an unstructured list of assumptions because it shows how uncertainty is supposed to be reduced.

## Desirability

Desirability concerns whether a proposed outcome matters to the people expected to use, purchase, adopt, or support it.

The relevant uncertainty is behavioral rather than primarily technical.

The Python case study uses an assumption that operations managers value automated exception monitoring enough to change their workflow. Its associated hypothesis measures how many qualified managers rank that capability among their highest-priority improvements.

The corresponding experiment combines structured interviews with a priority-ranking prototype.

This distinction matters because positive statements during interviews are not equivalent to demonstrated priority. A participant can describe a problem as inconvenient while still refusing to change an established workflow.

Useful desirability evidence therefore focuses on behavior and decision relevance:

- whether the problem occurs frequently,
- whether the problem is sufficiently costly or frustrating,
- whether the proposed outcome addresses the actual problem,
- whether users prioritize it over competing needs,
- whether users are willing to change behavior,
- and whether the proposed interaction is understandable.

The JavaScript implementation uses event-driven evidence collection to show how new desirability evidence can update a centralized validation workflow without coupling the model to a user interface.

## Viability

Viability addresses whether the proposed outcome can operate within a sustainable economic or organizational model.

A desirable capability can still fail viability if customers will not pay enough, operating costs are too high, support requirements are excessive, acquisition costs are unsustainable, or the expected economic benefit is too small.

The case study deliberately treats willingness to pay as a hypothesis rather than a conclusion:

`At least 40% of qualified prospects will accept the proposed recurring price.`

The observed result is below the threshold. This produces a `refuted` status.

That result does not mean the underlying customer problem is necessarily undesirable. It means the specific economic claim failed the defined test.

This separation is important:

`Desirability ≠ Viability`

A customer can strongly want an outcome but still reject the proposed commercial model.

Viability experiments should therefore measure economic behavior rather than relying exclusively on statements about usefulness. Relevant measurements include accepted price, conversion behavior, cost-to-serve, savings generated, revenue contribution, gross margin, and operational effort.

## Feasibility

Feasibility concerns whether the proposed outcome can actually be delivered within the required technical, operational, resource, security, and performance constraints.

The C++ case study represents an event-processing system whose alert evaluation must remain within a defined latency boundary.

The hypothesis states that p95 evaluation latency must remain at or below 250 milliseconds under representative peak load.

The use of p95 rather than only an average is intentional. A system can have a good average latency while a meaningful portion of requests experiences unacceptable delays. Tail latency is often more informative for operational systems with user-facing or downstream processing requirements.

The feasibility model can be extended to constraints such as:

- throughput,
- memory usage,
- deployment capacity,
- recovery time,
- integration compatibility,
- authorization behavior,
- data isolation,
- operational staffing,
- and reliability targets.

A technical prototype provides useful evidence, but evidence from moderate load does not automatically establish production feasibility. The workload distribution, concurrency, failure behavior, dependencies, and operational environment must be sufficiently representative.

## Risk

Risk is different from desirability, viability, and feasibility.

Risk focuses on the consequence of uncertainty and the possibility that a failure will materially damage the initiative.

The case study models a specific operational risk:

`False-positive alerts will not reach a level that causes customers to disable monitoring.`

The associated hypothesis uses an explicit disablement threshold.

This captures an important relationship:

`Detection accuracy → user trust → continued usage`

A technically functioning monitoring system can still fail operationally if false-positive alerts create notification fatigue.

Risk analysis should therefore consider both probability and consequence. The implementation's exposure metric uses impact and uncertainty as a practical prioritization mechanism:

`Risk exposure = impact × uncertainty`

This is a decision heuristic rather than a claim that the resulting value represents a statistically calibrated probability.

## Evidence

Evidence is represented separately from the assumption itself.

The Python implementation supports evidence such as:

- interviews,
- surveys,
- experiments,
- prototypes,
- financial models,
- technical spikes,
- production data,
- and document reviews.

Each evidence item records a source, type, strength, direction, and observation.

The directional attribute matters because evidence can contradict an assumption. A validation system should not silently treat every new observation as supportive.

The implementation calculates an evidence-confidence estimate from the signed strength of accumulated evidence. This is useful for prioritization but should not be interpreted as a formal Bayesian posterior unless the evidence model has been explicitly designed and calibrated for that purpose.

## Hypothesis Design

A useful hypothesis should be falsifiable.

The implementations encode two basic threshold forms.

For an `at_least` hypothesis:

`observed value >= threshold`

For an `at_most` hypothesis:

`observed value <= threshold`

Examples include:

`priority selection rate >= 0.65`

`price acceptance rate >= 0.40`

`p95 latency <= 250`

`monitoring disablement rate <= 0.08`

This is more operationally useful than an ambiguous claim such as "latency should be acceptable."

The threshold should be established before interpreting the measurement whenever possible. Otherwise, teams can unconsciously move the target after seeing the result.

## Experiment Prioritization

The Python, JavaScript, and C++ implementations prioritize experiments using a practical information-value heuristic.

The basic idea is:

`priority ∝ exposure × information gain / cost × remaining uncertainty`

The implementation also reduces priority when existing evidence already provides stronger support.

This encourages early investigation of assumptions that are:

- consequential if wrong,
- materially uncertain,
- relatively inexpensive to test,
- and likely to produce useful information.

The score is not a replacement for professional judgment. For high-consequence decisions, legal, safety, security, regulatory, or architectural constraints may justify testing an assumption even when its numerical prioritization score is lower.

## Python Implementation

The Python program provides the most complete registry-oriented model.

`Assumption` represents uncertainty and calculates exposure and evidence confidence.

`Hypothesis` converts an assumption into a measurable claim and evaluates observations against an explicit threshold.

`Evidence` records whether an observation supports or contradicts the associated assumption.

`Experiment` connects a hypothesis to a concrete validation activity and records cost, duration, and expected information gain.

`AssumptionRegistry` maintains referential integrity between these objects. A hypothesis cannot be added unless its assumption exists, and an experiment cannot be added unless its hypothesis exists.

The program also demonstrates:

- dictionary-based indexing for fast identifier lookup,
- validation of numerical ranges,
- finite-number validation,
- structured JSON serialization,
- temporary-file persistence,
- exposure ranking,
- experiment prioritization,
- hypothesis status tracking,
- evidence aggregation,
- duplicate detection,
- and invalid relationship handling.

The JSON snapshot illustrates how the model could become an API or dashboard data structure without requiring a third-party serialization package.

## JavaScript Implementation

The JavaScript implementation approaches the same domain from an event-driven perspective rather than reproducing the Python registry line by line.

`ValidationWorkflow` extends Node.js `EventEmitter`.

Evidence collection emits an `evidence:added` event. Hypothesis evaluation emits `hypothesis:evaluated`. Experiment completion emits `experiment:completed`.

This demonstrates a useful architectural distinction: the validation domain can publish state changes without knowing whether the consumer is a dashboard, logging subsystem, persistence layer, notification service, or test harness.

The implementation also uses:

- JavaScript `Map` objects for indexed domain records,
- `Object.freeze` for immutable enumerations,
- Promises for asynchronous workflow orchestration,
- `Promise.all` for concurrent experiment completion,
- structured JSON serialization,
- asynchronous filesystem APIs,
- temporary file replacement,
- and explicit process failure handling.

The snapshot writer first writes a temporary file and then renames it into place. This reduces the likelihood of leaving a partially written final snapshot after an interrupted write.

The file mode is restricted when the temporary file is created because assumption registers can contain commercially sensitive planning information.

## C++ Case Study

The C++ program models a technical decision system for an automated operational monitoring platform.

The architecture is organized around four domain entities:

`Assumption` stores the uncertainty being managed.

`Hypothesis` defines the measurable claim and its threshold.

`Evidence` records observations that support or contradict an assumption.

`Experiment` describes the validation activity and its expected information value.

`ValidationEngine` owns these entities and maintains their relationships through `std::map`.

The case study uses a coherent operational scenario rather than isolated C++ syntax examples.

The feasibility hypothesis evaluates p95 event-processing latency. The risk hypothesis evaluates whether false-positive alerts cause customers to disable monitoring. The viability hypothesis evaluates willingness to pay. The desirability hypothesis evaluates whether the problem is sufficiently important to change workflow priorities.

The C++ implementation uses `std::optional` for measurements that may not yet exist, `std::vector` for evidence collections, `std::map` for keyed registries, `std::sort` for ranking, `std::clamp` for bounded values, and exceptions for invalid domain relationships.

The program compiles with C++17 and uses only the standard library.

## Relationship Between the Four Dimensions

The four dimensions should be analyzed as a connected system without treating them as interchangeable.

A typical chain may look like:

`Desirability → Viability → Feasibility → Risk`

But the relationship is not necessarily linear.

A capability can be desirable while economically unattractive.

A capability can be economically viable while technically infeasible.

A capability can be feasible while carrying unacceptable operational risk.

A capability can pass technical feasibility testing while still failing user desirability.

The purpose of mapping assumptions is to expose these dependencies explicitly.

For example:

`Users want automated monitoring`

does not imply:

`Users will pay for automated monitoring`

and neither implies:

`The system can provide automated monitoring within the required latency`

and none of these alone proves:

`Users will continue using the system when false-positive alerts occur`

Each claim requires its own evidence.

## Evidence and Decision States

The implementations use explicit hypothesis states:

- `untested` means no evaluation has been performed.
- `testing` indicates an experiment or validation activity is underway.
- `supported` means the observed result satisfies the predefined threshold.
- `refuted` means the observed result fails the predefined threshold.
- `inconclusive` is available for cases where the collected evidence cannot support a defensible decision.

A supported hypothesis should not be interpreted as absolute proof.

It means that the observed evidence satisfied the predefined decision rule.

Likewise, a refuted hypothesis should be interpreted narrowly. It means the tested claim failed under the stated conditions. The team may revise the underlying assumption, change the proposed solution, modify the threshold for a justified reason, or investigate whether the experiment was invalid.

## Edge Cases

A validation system must handle uncertainty without manufacturing confidence.

An assumption with no evidence receives an evidence-confidence value of zero in these implementations.

That does not mean the assumption is false. It means the registry has no recorded evidence supporting its evaluation.

Non-finite measurements such as `NaN` and infinity are rejected because they cannot provide meaningful threshold comparisons.

Duplicate identifiers are rejected because ambiguous identifiers break traceability between assumptions, hypotheses, and experiments.

Broken references are rejected. A hypothesis cannot point to an unknown assumption, and an experiment cannot point to an unknown hypothesis.

Evidence strength is bounded to the interval from zero to one. This prevents accidental values from distorting the evidence aggregation model.

## Common Analytical Mistakes

### Treating confidence as evidence

A team may say that it is "90% confident" about an assumption without explaining why. Confidence is a belief state. Evidence is an observed basis for changing that belief.

The data model keeps these concepts separate.

### Treating a desirable outcome as commercially viable

Positive user feedback does not establish willingness to pay or economic sustainability.

Viability requires its own measurable claims.

### Treating a prototype as proof of feasibility

A prototype can demonstrate that a mechanism works under selected conditions. It does not automatically establish production capacity, resilience, security, maintainability, or operational cost.

### Using averages when tail behavior matters

For latency-sensitive systems, average latency can hide severe tail behavior. The case study therefore uses p95 latency as the feasibility metric.

### Moving thresholds after observing results

Changing a threshold after seeing the data can introduce confirmation bias. Thresholds should normally be specified before the experiment.

### Treating contradictory evidence as noise

Negative evidence can be more valuable than supportive evidence because it exposes assumptions that require redesign or additional investigation.

### Combining unrelated uncertainty into one score

A single confidence number cannot explain whether the underlying issue is user demand, economics, technical capability, or consequence of failure. Dimension-specific mapping preserves the causal meaning of the uncertainty.

## Performance Considerations

The Python registry uses dictionaries for identifier-based access, giving expected constant-time lookup for normal dictionary operations.

The JavaScript implementation uses `Map` for the same purpose.

The C++ implementation uses `std::map`, which provides logarithmic lookup and deterministic key ordering. A production implementation with very large registries could consider `std::unordered_map` where deterministic ordering is not required.

Experiment ranking performs sorting over the number of experiments, giving the ranking operation approximately `O(E log E)` complexity.

Assumption ranking similarly sorts the selected assumptions, approximately `O(A log A)` for `A` candidate assumptions.

Evidence-confidence calculation is linear in the number of evidence records attached to an assumption.

These workloads are normally small compared with the cost of the real-world experiments being prioritized. The more important performance issue is therefore often the latency and reliability of the system under investigation rather than the computational cost of the validation registry itself.

## Security and Data Governance

Assumption registers can contain commercially sensitive information such as pricing hypotheses, customer research, product strategy, architecture constraints, and identified operational weaknesses.

The JavaScript persistence example restricts the temporary file permissions and avoids exposing the snapshot through a network interface.

A production implementation should also consider:

- access control,
- audit trails,
- encryption at rest,
- encryption in transit,
- separation of customer-identifiable research data from strategic assumptions,
- retention policies,
- protection of financial models,
- and controlled access to security-related feasibility findings.

Evidence should not be altered merely to make an assumption appear supported. Immutable or auditable evidence records can be important when validation decisions influence significant investments.

## Production Considerations

A production-grade implementation would usually separate the domain model from persistence, user interfaces, authentication, reporting, and experiment execution.

The core relationships should remain explicit:

`assumption_id → hypothesis → experiment → observation → decision`

Each experiment should retain its measurement conditions, sample definition, timestamp, source, threshold, and interpretation.

For regulated or high-consequence environments, the system should also preserve who approved the hypothesis, who conducted the experiment, what version of the proposed solution was tested, and what evidence was available when the decision was made.

The distinction between evidence and interpretation is particularly important. A raw observation should remain identifiable even if the team's interpretation changes later.

## Practical Decision Workflow

A disciplined workflow begins by stating what must be true for the proposed outcome to succeed.

Those assumptions are mapped to desirability, viability, feasibility, and risk according to the nature of the uncertainty.

High-exposure assumptions are converted into falsifiable hypotheses.

Each hypothesis receives a measurable threshold before testing.

Experiments are selected according to the expected value of reducing uncertainty relative to cost and effort.

Evidence is recorded as supporting or contradictory rather than silently incorporated into a confidence statement.

Results are evaluated against the predefined rule.

The decision is then made from the resulting evidence while preserving the distinction between what was measured and what remains uncertain.
