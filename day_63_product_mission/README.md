# Product Mission

## Scope

This project models **Product Mission** as a distinct strategic concept within an organization.

The central distinction is:

- **Organizational mission** defines the broad purpose the organization exists to serve.
- **Product mission** translates that purpose into a specific product-level commitment.
- **Organizational purpose** explains why the organization performs its work.
- **Product purpose** explains why a particular product exists and what customer problem it addresses.
- A product mission should be specific enough to guide product decisions while remaining connected to organizational direction.

The implementations use the same domain relationship but apply different engineering approaches:

| Implementation | Primary perspective | Main mechanism |
|---|---|---|
| Python | Domain modeling and validation | Dataclasses, enums, persistence, assertions |
| JavaScript | Event-driven product evaluation | Classes, Maps, Sets, event listeners, async file operations |
| C++17 | Governance engine | STL sets, algorithms, typed domain structures, audit output |
| Java 17 | Enterprise domain service | Records, interfaces, policy objects, generics, immutable collections |
| PostgreSQL | Relational governance model | Constraints, triggers, functions, CTEs, reporting queries |

## Product Mission Model

The domain separates organizational direction from product-level purpose.

Plain-text relationship:

Organization
→ Organizational Mission
→ Strategic Themes
→ Product
→ Product Purpose
→ Product Mission
→ Product Metrics
→ Mission Evaluation

The product mission is not a replacement for the organizational mission. It operationalizes organizational intent at product scope.

### Organizational Mission

An organizational mission describes the durable purpose of the organization.

In the implemented scenario, the organization seeks to make important digital customer interactions simpler, reliable, and trustworthy.

Its strategic themes are:

- customer trust
- simplicity
- reliability

### Product Mission

The product mission narrows that organizational direction to a concrete product responsibility.

The example payment product is responsible for enabling everyday payments that are:

- quick
- clear
- reliable

The product mission retains the organizational themes of trust, simplicity, and reliability rather than introducing an unrelated strategic direction.

### Organizational Purpose

Organizational purpose answers the question:

> Why does the organization exist?

The example purpose is expressed around delivering dependable services that solve important customer problems.

It is broader than any single product.

### Product Purpose

Product purpose answers the narrower question:

> Why does this product exist?

The payment product exists to reduce friction in everyday transactions while preserving customer trust and reliability.

Product purpose therefore provides a bridge between customer need and the product mission.

## Strategic Alignment

Strategic alignment is implemented as an explicit relationship rather than an assumption.

A product mission is considered aligned when:

1. The parent mission is an organizational mission.
2. The product mission is classified as a product mission.
3. Both missions belong to the same organization.
4. At least one strategic theme is shared.

The shared-theme model prevents a product from being considered aligned merely because both missions contain similar prose.

For example:

| Organizational theme | Product theme | Alignment |
|---|---|---|
| customer trust | customer trust | Yes |
| simplicity | simplicity | Yes |
| reliability | reliability | Yes |
| cost efficiency | not present | No |

The PostgreSQL implementation enforces organization ownership at the database level. The application implementations validate the same rule in their domain models.

## Python Implementation

The Python program uses `dataclass` models for `Mission` and `Product`.

`MissionType` and `MissionStatus` are represented with enums so that mission classification and lifecycle state are not arbitrary strings.

The validation layer checks:

- non-empty mission names
- non-empty mission statements
- non-empty purpose statements
- maximum mission-statement length
- duplicate strategic themes
- correct organizational versus product mission types
- strategic-theme alignment

The `Product` object exposes two important operations.

`validate_alignment()` identifies the strategic themes shared between the organizational and product missions.

`score_purpose_clarity()` provides a simple lexical measure based on meaningful words shared between the product mission statement and its purpose. It is an implementation metric rather than a claim that mission quality can be completely measured by word overlap.

The program also persists its evaluation to `product_mission_evaluation.json` and reads the file back. This demonstrates a small but complete persistence cycle without requiring an external package.

Assertions verify important invariants after evaluation.

The invalid mission example exercises the validation failure path.

## JavaScript Implementation

The JavaScript implementation treats mission evaluation as an event-driven process.

`Mission` encapsulates mission validation. `ProductMissionModel` performs strategic alignment and purpose-clarity evaluation.

JavaScript-specific structures are used deliberately:

- `Set` stores unique strategic themes.
- `Map` stores product metrics.
- `MissionEventBus` provides event registration and dispatch.
- asynchronous filesystem functions persist and retrieve the evaluation.
- `try/catch` separates validation failures from unexpected execution errors.

The event flow is:

Mission data
→ validation
→ product evaluation
→ `mission:evaluated` event
→ audit persistence
→ persisted result reload

The event bus demonstrates how a product-governance component can notify other application components without embedding those consumers directly into the evaluation logic.

The program uses only Node.js standard-library modules.

## C++17 Implementation

The C++ implementation focuses on a typed governance engine.

`Mission` is a structured domain object containing:

- name
- statement
- purpose
- mission type
- lifecycle status
- strategic themes

`GovernanceEngine` contains policy-oriented operations rather than placing all behavior inside the data structure.

`std::set` is used for strategic themes because uniqueness and set intersection are central to the alignment decision.

The standard algorithm `std::set_intersection` calculates the shared strategic themes.

The same mechanism is used to calculate purpose alignment by comparing meaningful word sets.

The example product also contains operational metrics. Mission alignment and operational health remain separate concerns:

- mission alignment determines strategic consistency
- operational health evaluates measurable product performance

The program writes a human-readable audit file and handles filesystem and validation failures with exceptions.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented service and policy design.

`Mission` is a Java record, providing immutable domain data with explicit validation.

`MissionPolicy` defines the policy contract. `StrategicAlignmentPolicy` implements the rule that determines whether a product mission aligns with its organizational mission.

`ProductMissionService` coordinates:

- mission validation
- strategic alignment
- shared-theme calculation
- purpose-clarity evaluation

This separates policy from orchestration.

`MetricRegistry<T extends Number>` demonstrates a generic metric container while preserving type safety.

The model uses immutable collections when exposing mission themes and metric values. This prevents callers from changing domain state through returned collection references.

The enterprise workflow is:

Organization mission
→ policy evaluation
→ product mission decision
→ service-level assessment
→ audit generation

The explicit `MissionDecision` enum distinguishes aligned, misaligned, and invalid outcomes.

## PostgreSQL Implementation

The PostgreSQL implementation represents the domain relationally.

The primary entities are:

| Table | Responsibility |
|---|---|
| `organizations` | Organizational ownership |
| `missions` | Organizational and product missions |
| `products` | Product identity and purpose |
| `product_missions` | Product-to-mission relationship |
| `strategic_themes` | Organization-level strategic themes |
| `mission_themes` | Mission-to-theme association |
| `product_metrics` | Product performance measurements |
| `mission_evaluations` | Recorded mission decisions |

The schema uses PostgreSQL enum types for controlled lifecycle and classification values.

Foreign keys ensure that relationships cannot reference nonexistent organizations, products, or missions.

Check constraints protect important domain invariants such as:

- non-empty names
- bounded mission-statement length
- valid product lifecycle values
- non-negative metrics
- valid evaluation scores

## Database-Level Validation

The `validate_product_mission()` trigger performs a rule that should not depend solely on application code.

Before a product mission relationship is inserted or updated, PostgreSQL verifies:

- the product exists
- the mission exists
- both belong to the same organization
- the referenced mission is a product mission

This protects the relational model even when data is modified outside an application service.

The `touch_updated_at()` trigger maintains mission modification timestamps automatically.

## Mission Evaluation Function

`calculate_purpose_clarity()` computes a simple lexical relationship between a product mission statement and its purpose.

The function:

1. converts text to lowercase
2. separates words
3. removes non-alphanumeric characters
4. ignores very short words
5. removes duplicates
6. finds shared words
7. normalizes the result against the larger word set

The result is a bounded percentage.

This is deliberately a narrow analytical measure. It should not be interpreted as a complete assessment of strategic quality, customer value, or product-market fit.

`evaluate_product_mission()` combines mission ownership, strategic-theme overlap, and purpose clarity into an explicit alignment result.

## Data Integrity

The relational model distinguishes several different kinds of state.

### Mission state

A mission can be:

- `draft`
- `active`
- `retired`

### Product state

A product can be:

- `planned`
- `active`
- `retired`

### Metric state

A product metric can be:

- `healthy`
- `warning`
- `critical`

These states should not be collapsed into a single generic status because they describe different business objects.

## Metrics and Mission

Mission establishes direction. Metrics provide observable evidence about product performance.

The example payment product records:

- successful transaction rate
- payment completion time
- customer satisfaction

These metrics do not define the mission itself. They provide operational evidence that can be evaluated alongside the mission.

This distinction prevents a mission from becoming a list of performance indicators.

## Workflow

The implemented workflow is:

`organization`
→ `organizational mission`
→ `strategic themes`
→ `product`
→ `product purpose`
→ `product mission`
→ `product metrics`
→ `mission evaluation`
→ `eligibility decision`

The evaluation process separates strategic alignment from operational performance.

A product can have strong operational metrics but still be strategically misaligned.

A product can also be strategically aligned while having poor operational metrics.

Those are different management conditions and require different responses.

## Edge Cases

The implementations handle several failure conditions.

### Empty mission content

Empty names, statements, or purposes are rejected.

### Excessively long mission statement

The implementations enforce a 300-character limit for the modeled mission statement.

### Incorrect mission type

An organizational mission cannot be used as the product mission.

### Cross-organization relationship

A product cannot reference a mission owned by another organization.

The PostgreSQL trigger enforces this directly.

### No shared strategic themes

A product mission without a shared strategic theme is classified as misaligned rather than silently accepted.

### Missing metrics

The application implementations do not assume that performance metrics are always present.

The C++ operational-health evaluation returns an attention-required state when essential metrics are missing.

### Invalid persisted data

The Python and JavaScript implementations treat invalid persisted data as an execution failure rather than silently continuing with corrupted state.

## Design Distinctions

The four central concepts have separate responsibilities.

| Concept | Primary question | Scope |
|---|---|---|
| Organizational mission | What enduring purpose guides the organization? | Organization |
| Organizational purpose | Why does the organization exist? | Organization |
| Product mission | What product-level commitment supports that direction? | Product |
| Product purpose | Why does this product exist for its users? | Product |

The mission provides directional intent.

Purpose provides the underlying reason for existence.

The organizational versions establish broad direction.

The product versions translate that direction into product-specific responsibility.

## Performance Considerations

The application implementations use set-based operations for strategic-theme comparison.

For a mission with `n` organizational themes and `m` product themes:

- Python set intersection is approximately `O(n + m)` on average.
- JavaScript `Set` membership provides approximately constant-time average lookup.
- C++ `std::set_intersection` operates linearly over the sorted sets.
- Java uses `Set` operations for direct theme comparison.
- PostgreSQL uses indexed relationship tables for theme joins.

The relational indexes target actual access paths:

- organization and mission status
- product metrics ordered by measurement time
- mission-theme relationships by theme

The model avoids adding indexes to every column because unnecessary indexes increase storage and write overhead.

## Security and Governance Considerations

Mission data can influence product decisions, so governance should protect both integrity and traceability.

Important controls represented by the model include:

- foreign-key ownership
- database-level validation
- controlled status values
- immutable-style domain objects in Java
- explicit validation before evaluation
- persisted evaluation records
- separation of strategic decisions from operational metrics

In a production system, access control should restrict who can create, activate, retire, or replace organizational and product missions.

Mission versioning is represented in PostgreSQL through the `version` field. This permits historical mission states to be retained rather than overwriting the complete strategic record.

## Practical Decision Model

The implemented eligibility query uses the following conditions:

`aligned`
+ at least one shared strategic theme
+ purpose clarity score of at least 20%
→ `eligible`

This threshold is a demonstration of an explicit decision rule, not a universal product-management standard.

The important engineering principle is that eligibility conditions are represented as explicit rules rather than implicit judgments hidden inside application code.

## Files

| File | Implemented concern |
|---|---|
| `product_mission.py` | Mission domain model, validation, evaluation, persistence |
| `product_mission.js` | Event-driven mission evaluation and asynchronous persistence |
| `ProductMissionGovernance.cpp` | Typed governance engine and audit generation |
| `ProductMissionGovernance.java` | Enterprise policy and service architecture |
| `product_mission.sql` | Relational model, constraints, triggers, functions, evaluation, reporting |
| `README.md` | Technical model and implementation documentation |

## Execution Model

The Python program runs with the Python standard library.

The JavaScript program runs with Node.js and uses only Node.js built-in modules.

The C++ program requires a C++17-compatible compiler and uses the C++ standard library.

The Java program requires Java 17 or later and uses the Java standard library.

The PostgreSQL script requires a PostgreSQL database capable of supporting the defined schema, enum types, PL/pgSQL functions, triggers, CTEs, and window functions.
