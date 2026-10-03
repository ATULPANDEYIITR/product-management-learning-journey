# Product Opportunity: Identification, Sizing, and Scoring

## Purpose

Product opportunity analysis converts evidence about customer problems and business conditions into structured opportunities that can be evaluated consistently.

Three activities are central to the model:

- **Opportunity identification** determines what meaningful problem or unmet need exists and whether there is enough evidence to describe it as an opportunity.
- **Opportunity sizing** estimates how much population, customer value, or business impact could be associated with the opportunity under explicit assumptions.
- **Opportunity scoring** applies a defined prioritization model to dimensions such as customer value, strategic alignment, confidence, effort, speed, and risk.

These activities are related but should not be collapsed into a single number. An opportunity can have a large theoretical market and still have weak evidence. A well-supported problem can still require excessive effort. A modest opportunity can be attractive when it is highly aligned with strategy and can reach value quickly.

The implementations in this repository model those distinctions directly.

---

## Opportunity Identification

Identification begins with evidence rather than a solution.

Useful evidence can come from product analytics, support cases, customer interviews, sales conversations, research, surveys, operational data, or observed workflow behavior. Each source answers a different question.

Product analytics can reveal where users abandon a workflow. Support data can reveal recurring friction. Interviews can explain why the friction occurs. Sales evidence can expose obstacles before purchase. Combining these sources produces a stronger opportunity definition than relying on a single observation.

A useful opportunity statement identifies:

- the affected customer or user segment;
- the recurring problem;
- the context in which the problem occurs;
- evidence that the problem actually occurs;
- the scale or frequency of the problem;
- the consequence of leaving the problem unresolved.

The Python implementation represents evidence with `CustomerSignal`. Each signal records its source, category, affected population, frequency, severity, and confidence. Signals are then grouped into candidate opportunities.

The JavaScript implementation uses `CustomerEvidence` and an event-driven workflow. Evidence can be ingested asynchronously, which models a realistic product environment where analytics events, support records, or external research inputs arrive at different times.

The C++ case study stores evidence directly inside `ProductOpportunity` and preserves the evidence traceability needed to inspect why an opportunity received its evidence strength.

### Evidence strength

The implementations use a simplified evidence-strength calculation:

`severity × confidence`

Severity represents the observed magnitude of the problem. Confidence represents how strongly the evidence supports the observation.

This is deliberately not treated as statistical significance. It is an auditable product-analysis heuristic. A support complaint with high severity but uncertain representativeness should not automatically be treated as equivalent to a large behavioral dataset showing the same problem.

Identification should therefore preserve the underlying signals rather than only retaining an aggregated score.

---

## Opportunity Sizing

Sizing answers a different question from identification:

> If this problem were addressed successfully, how much relevant value could exist?

A simple scenario model used by the implementations is:

`TAM = target population × annual value per affected user`

`SAM = TAM × reachable share`

`Expected value = SAM × adoption rate`

These terms are assumptions, not guarantees.

### Target population

The target population describes the users or accounts that could plausibly experience the problem.

A population should have a defined boundary. For example, "all internet users" is usually less useful than "business accounts using the product's operational reporting workflow."

### Annual value per affected user

This converts an affected user into a value estimate.

The value might represent:

- revenue potential;
- avoided operational cost;
- time saved;
- increased conversion value;
- retained customer value;
- productivity improvement.

The correct unit depends on the opportunity. A reporting automation opportunity may be modeled using avoided labor cost, while a monetization opportunity may use incremental annual customer value.

### Reachable share

The theoretical population is rarely equivalent to the population the product can actually reach.

Reachability can be constrained by:

- geography;
- product availability;
- customer segment;
- existing distribution;
- technical eligibility;
- sales coverage;
- regulatory restrictions;
- product capabilities.

The implementations therefore distinguish TAM from SAM rather than treating the entire target population as immediately addressable.

### Adoption rate

Adoption represents the portion of the reachable population expected to use or accept the proposed value.

It is often the most assumption-sensitive part of a simple opportunity model.

For that reason, all three implementations expose adoption sensitivity. The examples calculate expected value at multiple adoption rates rather than presenting a single assumption as a fact.

A scenario with 10% adoption and a scenario with 50% adoption can produce materially different opportunity values even when population and annual value remain unchanged.

---

## Opportunity Scoring

Scoring addresses prioritization rather than market measurement.

The example model evaluates:

- customer value;
- strategic alignment;
- confidence;
- effort;
- time to value;
- risk.

The weighted score is normalized to a 0–10 scale.

Effort and risk are inverted because lower values are favorable. If effort is represented as 8/10, the favorable contribution becomes `10 - 8 = 2`.

Confidence combines explicit product judgment with evidence strength. This prevents an unsupported confidence score from completely ignoring the quality of the evidence used to identify the opportunity.

The score is therefore a structured decision aid rather than a measurement of objective product truth.

A representative calculation is:

`weighted score = Σ(criteria × normalized weight)`

The weights used by the implementations are:

| Criterion | Weight |
| --- | ---: |
| Customer value | 30% |
| Strategic alignment | 20% |
| Confidence | 15% |
| Effort | 10% |
| Time to value | 10% |
| Risk | 15% |

The weights are intentionally explicit. A product organization can change them when its strategy changes without rewriting the opportunity-identification or sizing logic.

---

## Relationship Between Identification, Sizing, and Scoring

The workflow is:

**Evidence → Opportunity → Sizing assumptions → Scoring policy → Analysis**

Identification asks whether a meaningful product problem exists.

Sizing asks how large the potential value could be.

Scoring asks how the opportunity compares against other opportunities according to a defined set of product criteria.

The distinction matters because the three stages answer different questions.

For example, an opportunity can have:

- strong customer evidence but a small reachable population;
- a large theoretical population but uncertain adoption;
- high customer value but substantial implementation effort;
- moderate economic value but exceptional strategic alignment;
- strong evidence but significant product or delivery risk.

A single raw metric cannot represent all of those conditions accurately.

---

## Python Implementation

The Python program provides the most explicit analytical model.

`CustomerSignal` captures the evidence used during identification. Validation prevents impossible values such as negative affected users or confidence outside the allowed range.

`ProductOpportunity` keeps identification, sizing, and scoring data together while preserving their conceptual separation. Signals remain attached to the opportunity so the resulting score can be traced back to the evidence.

`identify_opportunities()` groups signals by opportunity category and creates candidate opportunities only when the evidence satisfies configurable thresholds.

`calculate_tam_sam_expected_value()` performs the sizing model using explicit population, value, reach, and adoption assumptions.

`calculate_opportunity_score()` applies the weighted prioritization policy. It also adjusts confidence using the calculated evidence strength.

` sensitivity_analysis()` demonstrates how expected value changes when adoption assumptions change without modifying the qualitative prioritization score.

The script also includes validation failures for invalid reachability, negative scoring weights, and invalid evidence confidence.

The separation between sizing and scoring is especially important in this implementation. Expected economic value is not used as a direct replacement for the product score.

---

## JavaScript Implementation

The JavaScript program models product opportunity analysis as an event-driven workflow.

`CustomerEvidence` validates evidence as it enters the system. JavaScript's `Object.freeze()` is used for category and weight configuration where mutation would make the workflow harder to reason about.

`ProductOpportunity` uses a private `#evidence` field. This demonstrates a useful JavaScript encapsulation pattern: external code can retrieve a copy of the evidence collection but cannot directly replace the private array.

`OpportunityRepository` uses a `Map` to index opportunities by ID. This gives the workflow direct lookup without repeatedly scanning the entire collection.

`OpportunityWorkflow` extends Node.js's `EventEmitter`. Evidence ingestion, sizing, and scoring emit events that represent observable workflow transitions.

The asynchronous evidence ingestion function uses `setImmediate()` to model an event boundary. A production implementation could connect the same architectural pattern to webhook processing, a message queue, or an analytics ingestion service.

The JavaScript program also serializes the final opportunity portfolio into a JSON payload. This reflects a practical integration boundary where a product-analysis engine could expose opportunity records to a dashboard or API.

---

## C++ Case Study

The C++ implementation models a repository-like product governance engine.

The scenario contains three opportunities:

- shortening the path to first value for new business accounts;
- automating recurring operational reporting;
- clarifying paid plan selection for qualified users.

Each opportunity has a different value mechanism. Activation is associated with reaching productive use. Operational efficiency is associated with reducing recurring work. Monetization is associated with improving the conversion experience around paid value.

`CustomerSignal` represents evidence and validates source, population, frequency, severity, and confidence.

`SizingModel` isolates the quantitative assumptions used to calculate TAM, SAM, and expected value. This separation makes the economic assumptions independently inspectable.

`OpportunityCriteria` stores the qualitative prioritization dimensions and validates their 0–10 ranges.

`ProductOpportunity` owns its signals and calculates both evidence strength and the resulting score. The `addSignal()` method rejects evidence belonging to another opportunity category, preventing accidental cross-category aggregation.

`OpportunityRepository` uses `std::map` for deterministic ID-based storage and lookup.

The score calculation uses normalized weights and explicitly reverses effort and risk because lower effort and lower risk represent more favorable conditions.

The case study also includes adoption sensitivity analysis. The same opportunity can produce different expected values under different adoption assumptions while its underlying qualitative criteria remain unchanged.

---

## Distinguishing the Three Activities

| Activity | Primary question | Main input | Main output |
| --- | --- | --- | --- |
| Opportunity identification | What meaningful problem exists? | Customer and business evidence | Defined opportunity |
| Opportunity sizing | How much potential value exists? | Population, value, reach, adoption assumptions | TAM, SAM, expected value |
| Opportunity scoring | How should the opportunity be evaluated against criteria? | Value, strategy, confidence, effort, timing, risk | Weighted score |

The distinction prevents a common analytical mistake: treating market size as synonymous with priority.

A large opportunity is not automatically a high-confidence opportunity. A high-confidence opportunity is not automatically inexpensive to deliver. A low-effort opportunity is not automatically strategically important.

---

## Opportunity Identification Failure Modes

### Mistaking a feature request for an opportunity

A request such as "add automated reporting" is a proposed solution.

The underlying opportunity may be "operations teams spend recurring time preparing the same management information."

The latter is more useful for discovery because several solutions could address the problem.

### Treating one loud complaint as broad demand

A severe individual complaint can be important without representing the entire customer base.

The implementations retain affected population, frequency, source, and confidence so that isolated observations are distinguishable from broader behavioral evidence.

### Combining unrelated problems

Two signals should not be grouped merely because they appear in the same product area.

The Python and C++ models enforce category consistency when signals are attached to opportunities. This helps prevent a portfolio from becoming a collection of unrelated symptoms under one broad label.

### Losing evidence traceability

An opportunity should remain connected to the evidence that produced it.

Without traceability, later reviewers cannot determine whether a score reflects current customer evidence, an outdated assumption, or unsupported product judgment.

---

## Sizing Failure Modes

### Treating TAM as a forecast

TAM is a theoretical scale calculation. It does not account for every practical constraint.

A product team should not interpret:

`population × annual value`

as guaranteed revenue.

### Hiding adoption assumptions

A large SAM can still generate a small expected value if adoption is low.

The sensitivity calculations make this dependency visible.

### Mixing value units

Revenue, cost savings, time saved, and customer retention are different value concepts.

A sizing model should state what the monetary value represents rather than silently combining incompatible units.

### Double counting customers

If multiple opportunities target the same customer population, their expected values should not automatically be added together. Customers can experience several problems, but the economic effects may overlap.

The sample implementation evaluates each opportunity independently and does not claim that portfolio values are additive.

---

## Scoring Failure Modes

### Using arbitrary precision

A score such as `8.347` can appear more scientific than the underlying assumptions justify.

The implementations retain three decimal places for computational transparency, but the underlying criteria remain judgment-based inputs.

### Treating the score as an objective answer

A weighted score represents the selected model and its weights.

Changing the weights changes the result. Adding a new criterion can also change the relative positions of opportunities.

The score should therefore be treated as a transparent decision framework rather than an independent measurement of product truth.

### Confusing confidence with certainty

Confidence is an assessment of evidence quality or belief in the assumptions. It does not eliminate uncertainty.

An opportunity can have high confidence in the existence of a problem while still having uncertain adoption or implementation economics.

---

## Practical Review Workflow

A robust product opportunity review can preserve the following sequence:

**Evidence review → Problem definition → Evidence quality assessment → Opportunity sizing → Assumption review → Scoring → Sensitivity analysis → Product discussion**

The important control is that each stage exposes its inputs.

A reviewer should be able to ask:

- Which observations support this opportunity?
- Which customer segment is actually affected?
- How frequently does the problem occur?
- What makes the evidence credible?
- What population is included in the sizing model?
- What does annual value mean in this context?
- Why is the reachable share set at this level?
- What evidence supports the adoption assumption?
- Why are these scoring criteria weighted this way?
- Which parts of the score are measured and which are judgment?
- How sensitive is the expected value to the assumptions?

This makes disagreements productive because reviewers can challenge a specific assumption rather than debating an opaque final number.

---

## Performance and Data Design

The examples use in-memory structures because their purpose is to demonstrate the analytical mechanics.

For larger product organizations, opportunity data may be persisted in a database with separate entities for:

- opportunities;
- evidence records;
- customer segments;
- sizing assumptions;
- scoring criteria;
- scoring policies;
- historical score snapshots.

Separating evidence from opportunities is especially useful because the same evidence record may need to be referenced during later research or reassessment.

The Python implementation uses dictionaries and lists for straightforward analytical access. The JavaScript implementation uses `Map` for opportunity lookup. The C++ implementation uses `std::map` for deterministic keyed storage.

The dominant operations in the examples are small enough that simple in-memory structures are appropriate. At larger scale, indexes should be introduced around opportunity IDs, categories, customer segments, evidence sources, and time periods rather than repeatedly scanning every record.

---

## Security and Governance Considerations

Product opportunity systems can contain commercially sensitive information.

Customer interviews, support records, conversion analytics, and revenue assumptions may reveal confidential customer behavior or business strategy.

A production implementation should therefore control:

- who can access raw customer evidence;
- which users can change sizing assumptions;
- who can change scoring weights;
- whether historical scores are immutable;
- whether sensitive customer identifiers are stored;
- whether exported opportunity data contains confidential information;
- whether changes to strategic assumptions are auditable.

Scoring-policy changes are particularly important to audit. If a product portfolio suddenly changes ordering because the weighting policy changed, reviewers should be able to distinguish a genuine change in opportunity conditions from a change in the evaluation model.

---

## Production Considerations

A production opportunity-management system would normally preserve historical versions of both evidence and assumptions.

For example, an opportunity may initially have:

`target population = 20,000`

and later be revised to:

`target population = 28,000`

The system should preserve both versions and the reason for the change.

The same principle applies to adoption, reachability, annual value, confidence, and scoring weights.

This enables longitudinal analysis such as:

- whether customer evidence became stronger;
- whether assumptions became more conservative;
- whether the opportunity grew or contracted;
- whether the scoring framework changed;
- whether expected value changed because of customer evidence or because of model assumptions.

Such history prevents current values from obscuring how the product organization arrived at its present understanding.

---

## Limitations of the Example Model

The examples intentionally use a simplified quantitative model.

They do not attempt to estimate:

- probabilistic revenue distributions;
- cohort-specific retention curves;
- customer lifetime value from observed retention data;
- cannibalization between opportunities;
- implementation dependencies between initiatives;
- capacity-constrained roadmaps;
- experimental uplift confidence intervals;
- Monte Carlo simulations;
- causal effects from controlled experiments.

Those capabilities can be added to a production analytical system, but they would change the model substantially.

The central design principle remains the same: keep observed evidence, opportunity definition, sizing assumptions, and prioritization criteria distinguishable so each can be examined independently.
