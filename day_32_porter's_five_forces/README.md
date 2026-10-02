# Porter's Five Forces: Industry Structure Analysis

## Scope

This repository models Porter's Five Forces as five related but distinct sources of competitive pressure:

- **Competitive rivalry** examines how strongly existing firms compete with one another.
- **Supplier bargaining power** examines how much leverage input providers have over firms in the industry.
- **Buyer bargaining power** examines how much leverage customers have when purchasing from firms in the industry.
- **Threat of substitutes** examines whether customers can satisfy the same underlying need through a different solution.
- **Threat of new entrants** examines how difficult it is for new firms to enter the industry and establish a competitive position.

The implementations use a fictional but realistic **B2B cloud accounting software market** as the main case. The market is deliberately defined by product category, customer segment, geography, and time horizon rather than treating an entire technology sector as one homogeneous industry.

The numerical values are analytical assumptions. A score such as `7.2/10` represents modeled pressure under the stated assumptions; it is not an objectively measured industry statistic.

---

## Why Industry Definition Matters

Five Forces analysis depends heavily on the boundaries chosen for the market.

The Python, JavaScript, and C++ implementations define the main case as subscription-based accounting, invoicing, expense management, and financial reporting software sold to small businesses in India over a 2026-2030 horizon.

That definition matters because the relevant forces change when the market boundary changes. A small-business accounting product does not necessarily face the same buyers, substitutes, suppliers, entry barriers, or competitive rivals as enterprise financial-management software.

A useful model therefore records:

- the industry or market name
- the precise market definition
- the geographic scope
- the time horizon
- the evidence supporting each force
- the assumptions behind each score

Without these boundaries, a Five Forces assessment can mix unrelated competitive conditions and produce misleading conclusions.

---

## The Five Forces as Different Mechanisms

The framework should not be treated as five labels for the same concept.

### Competitive Rivalry

Competitive rivalry concerns **existing firms already operating inside the defined industry**.

Relevant drivers include:

- number and relative size of competitors
- industry growth
- product differentiation
- fixed-cost intensity
- excess capacity
- frequency of price competition
- switching costs
- exit barriers
- similarity of competing offerings

In the cloud accounting case, rivalry is modeled as relatively strong because established providers can compete through subscription pricing, integrations, automation, workflow design, and service quality.

A price reduction by one established accounting vendor that causes another established vendor to respond is a rivalry mechanism.

This differs from new entry. A new accounting company entering the market is relevant to the threat of entrants, while competition between companies already operating in the market is rivalry.

### Supplier Bargaining Power

Supplier power concerns organizations that provide inputs needed by industry participants.

For cloud accounting software, relevant suppliers can include:

- cloud infrastructure providers
- payment-processing services
- banking APIs
- financial-data providers
- specialized software infrastructure
- security and identity services
- external technology components

Supplier power becomes stronger when suppliers are concentrated, their inputs are differentiated, switching is expensive, or they can credibly integrate forward into the customer's market.

The model therefore distinguishes a supplier raising its price from a competitor lowering its subscription price. The first changes supplier power; the second is evidence about rivalry.

### Buyer Bargaining Power

Buyer power concerns customers purchasing the industry's products or services.

Important drivers include:

- buyer concentration
- purchase volume
- price sensitivity
- availability of competing offerings
- information available to buyers
- switching costs
- product differentiation
- buyer ability to integrate backward

In the cloud accounting case, customers can compare subscription plans and product capabilities. This can increase buyer leverage.

At the same time, historical financial records, integrations, configuration, training, and workflow migration can make switching more costly. Those factors can reduce buyer leverage even when several alternatives exist.

Buyer power is therefore not equivalent to the number of buyers. A fragmented customer base can have limited individual purchasing volume while still exerting substantial collective pressure when products are easy to compare and switch between.

### Threat of Substitutes

A substitute is not simply another competitor in the same industry.

A substitute satisfies the customer's underlying need through a **different solution**.

For accounting software, possible substitutes include:

- spreadsheets
- desktop accounting systems
- outsourced bookkeeping
- internal accounting processes
- alternative workflow combinations that replace part of the software's function

The key question is not merely whether another product exists. The analysis considers whether customers can move to a different solution while still accomplishing the job they need done.

Relative price-performance is particularly important. A substitute with lower price but substantially worse functionality may exert limited pressure. A substitute that provides acceptable results at much lower total cost can exert stronger pressure.

### Threat of New Entrants

Threat of new entrants concerns organizations that are **not currently established competitors in the market but could enter it**.

Entry barriers can include:

- economies of scale
- capital requirements
- brand reputation
- customer trust
- distribution access
- regulatory requirements
- proprietary technology
- network effects
- switching costs
- incumbent cost advantages
- access to specialized expertise

Cloud software can reduce some traditional physical entry barriers because a new company does not necessarily need a large physical distribution network or manufacturing operation.

That does not mean entry is frictionless. An accounting product still needs customer trust, reliable integrations, domain expertise, compliance capabilities, distribution, and a credible migration path.

---

## Relationship Between the Forces

The forces interact, but they should remain analytically separate.

A customer having low switching costs can affect buyer bargaining power because the customer can more easily move between vendors.

The same switching behavior can strengthen substitutes when the customer can move away from the industry's product category entirely.

Those are different mechanisms.

Similarly:

- A large supplier increasing prices concerns supplier power.
- An existing competitor matching the price concerns rivalry.
- A new company entering the market concerns entrants.
- A customer negotiating a discount concerns buyer power.
- A customer abandoning the category for spreadsheets concerns substitutes.

The implementations preserve these distinctions through separate `Force` values and separate assessment records.

---

## Evidence-Based Scoring

A Five Forces score should not be treated as a measurement with false precision.

The implementations use a `0..10` scale to make assumptions explicit:

| Range | Interpretation |
| --- | --- |
| `0-2.99` | Low pressure |
| `3-4.99` | Moderate-Low pressure |
| `5-6.99` | Moderate-High pressure |
| `7-10` | High pressure |

A high score means that the corresponding force is modeled as exerting stronger competitive pressure.

The score does not automatically mean that the industry is unattractive, and the framework should not be reduced to a single profitability number.

Each assessment is paired with a rationale and, where appropriate, evidence. Evidence contains:

- a concrete observation
- a stated source or evidence origin
- a direction indicating whether it increases or reduces pressure
- a strength value representing confidence or relevance

This prevents the numerical score from becoming detached from the underlying reasoning.

---

## Force-Specific Drivers

The Python implementation exposes different analytical drivers for each force.

### Rivalry drivers

The model considers competitor concentration, industry growth, differentiation, fixed costs, capacity, exit barriers, and price competition.

### Supplier drivers

The model considers supplier concentration, alternative suppliers, switching costs, uniqueness of inputs, supplier dependence on the customer industry, and potential forward integration.

### Buyer drivers

The model considers buyer concentration, purchasing volume, differentiation, switching costs, information availability, price sensitivity, and possible backward integration.

### Substitute drivers

The model considers availability of alternative solutions, relative price-performance, switching costs, customer willingness to change the solution, technology changes, convenience, and quality differences.

### Entrant drivers

The model considers economies of scale, capital requirements, customer loyalty, distribution access, regulation, network effects, and incumbent cost advantages.

The separation matters because changing one driver does not necessarily change all five forces by the same amount.

---

## Python Implementation

The Python program is a complete analytical model built with standard-library components.

### Domain model

`Force` is an enumeration containing the five forces. `Evidence` stores supporting observations. `ForceAssessment` stores a score, rationale, and evidence for one force. `IndustryModel` groups the five assessments with the market definition, geography, and time horizon.

Validation occurs during object construction. Empty industry definitions, missing forces, invalid scores, invalid evidence directions, and invalid evidence-strength values are rejected.

### Baseline analysis

`demonstrate_beginner_model()` creates the cloud accounting case with force-specific rationales and evidence.

The model deliberately gives different rationales to the five forces. For example, competition between established vendors is represented under rivalry, while infrastructure-provider dependency is represented under supplier power.

### Scenario analysis

`demonstrate_scenario_analysis()` models a change caused by stronger automation and integration standards.

The scenario does not simply add the same number to every force. Different structural changes affect different forces through different mechanisms.

This illustrates an important analytical property of Five Forces: industry structure can change over time, so a historical assessment should not automatically be treated as a permanent condition.

### Sensitivity analysis

`sensitivity_analysis()` changes one force at a time and measures how the equal-weighted average pressure changes.

This identifies how sensitive the aggregate descriptive metric is to individual force assumptions.

It does not establish causality or forecast future performance.

### Persistence

The program serializes the model to JSON and then reconstructs it using `load_model()`.

This demonstrates how a Five Forces assessment can become structured data rather than remaining only in narrative form.

The temporary demonstration file is removed after the persistence test so execution does not unexpectedly leave an artifact in the working directory.

---

## JavaScript Implementation

The JavaScript implementation uses an event-driven design rather than reproducing the Python architecture line for line.

`FiveForcesModel` stores the five assessments in a JavaScript `Map`, providing explicit association between each force and its assessment.

The implementation also introduces `IndustryAnalysisBus`.

### Event-driven analysis

Industry structure can change as new observations arrive. An event such as `forceChanged` can notify audit, reporting, or user-interface components without requiring those components to directly manage the model's internal state.

The scenario processor uses a Promise and asynchronous scheduling to represent this type of event-driven workflow.

The scenario changes rivalry, supplier power, buyer power, substitutes, and entrants through different deltas and rationales.

### Validation

JavaScript-specific validation checks:

- force names
- numerical score ranges
- evidence statements
- evidence sources
- evidence direction
- evidence strength
- required industry information

Invalid state causes an exception instead of silently producing an incomplete model.

### Serialization

`toJSON()` converts the internal `Map` representation into an ordinary object suitable for JSON serialization.

This pattern is useful when a browser interface, API, or storage layer needs to exchange Five Forces data.

---

## C++ Case Study

The C++ program treats the Five Forces assessment as a controlled analytical system.

The case is the same broad cloud accounting market, but the implementation perspective is different: changes to the model pass through an `AnalysisGovernance` layer.

### Typed force model

`enum class Force` prevents force names from being treated as arbitrary strings throughout the core model.

`ForceAssessment` contains the score, rationale, and evidence associated with one force.

`IndustryModel` owns the complete set of assessments and validates that all five forces exist.

### Scenario governance

`AnalysisGovernance::applyScenario()` applies a collection of structural changes as a transaction.

The proposed scores are calculated first.

If any proposed score would fall outside the valid `0..10` range, the operation fails before the existing model is modified.

Only after all changes pass validation are the changes committed.

This is useful when analytical models are edited by multiple processes or when auditability matters.

### Audit history

Every committed scenario change produces an `AuditEntry`.

The record contains:

- scenario name
- affected force
- previous score
- new score
- reason for the change

This means the model retains a trace of why an assumption changed instead of only retaining the latest number.

### Algorithmic operations

The C++ implementation uses standard-library algorithms to identify the highest- and lowest-pressure forces.

Sensitivity analysis recalculates the aggregate descriptive pressure after changing one force by ten percent.

The computational work is small because only five forces exist. The core model therefore operates in effectively constant time with respect to the number of forces. Evidence processing grows with the amount of evidence attached to each assessment.

---

## A Practical Analysis Workflow

A disciplined Five Forces analysis can be represented as a chain of reasoning:

`Market Definition → Evidence Collection → Force Assessment → Scenario Changes → Sensitivity Analysis → Strategic Interpretation`

The market definition comes first because the identity of competitors, buyers, suppliers, substitutes, and potential entrants depends on the boundaries of the market.

Evidence then supports individual force assessments.

Scenario analysis tests how structural changes affect the forces.

Sensitivity analysis exposes assumptions that have a large effect on an aggregate descriptive metric.

Strategic interpretation should remain connected to the specific force mechanisms rather than collapsing the analysis into one unexplained score.

---

## Practical Example of Distinguishing Forces

Consider a cloud accounting company facing the following events.

**An existing competitor cuts its monthly subscription price.**

This is primarily a rivalry event because an existing industry participant is changing its competitive behavior.

**A banking API provider raises its access fees.**

This concerns supplier bargaining power because the provider controls an input required by the software company.

**A large accounting firm negotiates a volume discount.**

This concerns buyer bargaining power because the customer is using purchasing scale to obtain better terms.

**A small business replaces the accounting platform with spreadsheets.**

This is a substitute event because the customer is leaving the software solution category for another way of performing the underlying task.

**A new startup launches a competing accounting platform.**

This concerns threat of new entrants because a new participant is entering the defined market.

The events may influence one another, but their primary mechanisms remain distinct.

---

## Common Analytical Mistakes

### Treating all competitors as substitutes

A competitor in the same industry contributes to rivalry. A substitute provides a different solution to the underlying customer need.

### Treating suppliers as vendors in general

Supplier power is about inputs that industry participants require. A company's ordinary business relationship with every external vendor does not automatically create meaningful supplier power.

### Assuming many buyers means weak buyer power

Buyer power depends on concentration, purchasing volume, information, differentiation, switching costs, and other structural factors.

A fragmented buyer population can still exert pressure when products are standardized and switching is easy.

### Treating low entry cost as zero entry barriers

Software can be relatively easy to develop compared with capital-intensive industries, but customer trust, distribution, regulatory requirements, integrations, scale, and incumbent advantages can still create substantial barriers.

### Scoring without evidence

A numerical value without an explanation can hide assumptions. The implementations therefore associate scores with rationales and evidence.

### Using historical conditions as permanent conditions

Industry structure changes. Technology, regulation, consolidation, buyer behavior, supplier concentration, and business models can alter the forces.

The scenario-analysis portions of all three implementations make this change explicit.

### Combining the five forces too early

An average can be useful as a compact descriptive statistic, but it should not replace force-level analysis. Two industries with the same average can have very different structural profiles.

---

## Edge Cases and Validation

The implementations explicitly handle invalid analytical states.

A model cannot be created without all five forces.

Scores outside `0..10` are rejected.

Evidence requires a statement and source.

Evidence direction is restricted to `-1`, `0`, or `1`.

Evidence strength must be greater than zero and no greater than one.

Scenario changes are bounded so that they cannot silently create impossible scores.

The C++ governance layer validates a complete scenario before committing it, avoiding partial updates when a later proposed change is invalid.

The Python persistence layer validates reconstructed evidence and force assessments through the same domain classes used by newly created models.

---

## Performance Considerations

Five Forces itself has a very small fixed analytical structure because there are exactly five forces.

For a model with `F = 5` forces and `E` total evidence records:

- force traversal is `O(F)`, effectively constant
- average-pressure calculation is `O(F)`
- highest- or lowest-force selection is `O(F)`
- evidence reporting is `O(E)`
- scenario application is approximately `O(F + S)`, where `S` is the number of scenario changes
- JSON serialization is proportional to the number of assessments and evidence records

The limiting factor in a real analytical system is therefore unlikely to be the five-force calculation itself. Data collection, evidence quality, source validation, scenario maintenance, and interpretation are more significant operational concerns.

---

## Data and Evidence Quality

Five Forces is an analytical framework rather than a substitute for market research.

Useful evidence should be tied to the force being evaluated.

For rivalry, useful evidence may concern competitor concentration, pricing behavior, differentiation, capacity, or market growth.

For supplier power, useful evidence may concern supplier concentration, input uniqueness, switching costs, and alternative sources.

For buyer power, useful evidence may concern customer concentration, purchasing volume, price sensitivity, information, and switching costs.

For substitutes, useful evidence should address alternative ways of solving the customer's underlying problem and their relative price-performance.

For entrants, useful evidence should address barriers to entry such as capital, scale, distribution, regulation, technology, trust, and incumbent advantages.

The same market fact can sometimes affect multiple forces, but it should be mapped to each force through its specific mechanism rather than copied as identical reasoning.

---

## Scenario Analysis and Structural Change

Scenario analysis is particularly useful when an external change can affect several forces through different channels.

For example, improved automation can:

- increase rivalry by making basic features easier to reproduce
- reduce some supplier dependency through standardized integrations
- increase buyer power if comparison and migration become easier
- strengthen substitutes if alternative workflows become more capable
- reduce technical entry barriers for new providers

These effects do not have to move in the same direction.

This is why the implementations apply force-specific changes instead of treating a technology change as a universal positive or negative adjustment.

---

## Limitations

Five Forces describes competitive structure. It does not by itself provide a complete company strategy, operational plan, financial forecast, or valuation.

A force score also depends on:

- market definition
- evidence quality
- analyst assumptions
- time horizon
- geography
- customer segment
- degree of product differentiation
- interpretation of switching costs
- assumptions about future structural changes

The `0..10` scale is therefore best treated as a structured communication mechanism.

Two analysts can reasonably produce different scores from the same qualitative evidence if they use different assumptions about the strength or relevance of a driver.

The appropriate response is to make those assumptions explicit rather than treating the numerical score as objective truth.

---

## Security and Production Considerations

If a production application accepts Five Forces assessments from users or external systems, input validation should occur at the application boundary as well as inside domain objects.

Persisted evidence should be treated as untrusted data when it originates outside the application.

If source documents or URLs are stored, the production system should preserve source provenance and retrieval timestamps rather than storing only an unexplained score.

If multiple analysts can edit the same assessment, version history and optimistic concurrency controls can prevent silent overwrites.

Audit records should preserve who changed an assessment, what changed, when it changed, and why the change was made.

If scores are used by downstream decision systems, the application should retain the underlying evidence and assumptions so that a numerical output remains traceable to its analytical basis.

---

## Implementation Relationship

The three implementations intentionally use different technical perspectives.

| Implementation | Primary technical perspective | Main Five Forces contribution |
| --- | --- | --- |
| Python | Structured analytical model and persistence | Evidence-backed assessments, scenario modeling, sensitivity analysis, JSON persistence |
| JavaScript | Event-driven application model | Reactive force changes, validation, asynchronous scenario processing, JSON serialization |
| C++ | Governed analytical case study | Strong typing, transactional scenario updates, audit history, deterministic calculations |

The underlying framework remains the same, but the engineering choices demonstrate different ways of representing industry-structure analysis.

The key design principle across all three is the same: **competitive rivalry, supplier power, buyer power, substitutes, and entrants represent different economic mechanisms and should be analyzed separately before their relationships are considered.**
