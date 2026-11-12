# Kano Model: Customer Needs and Satisfaction Analysis

## Project Overview

The Kano Model is a product development and customer satisfaction framework that classifies product features according to their relationship with customer satisfaction.

It helps product managers distinguish between essential requirements, measurable performance improvements, unexpected benefits, and features that have little effect on customer satisfaction.

This project implements the Kano Model through five independent technical implementations:

| File | Implementation | Main responsibility |
|---|---|---|
| `kano_model.py` | Python | Questionnaire processing and feature analysis |
| `kano_model.js` | JavaScript | Event-driven customer response management |
| `kano_model.cpp` | C++17 | Feature classification and analytical processing |
| `KanoEnterprise.java` | Java 17 | Enterprise feature lifecycle and policy management |
| `kano_model.sql` | PostgreSQL | Relational storage, classification, reporting and decisions |

## 1. Kano Model Fundamentals

The Kano Model distinguishes customer requirements according to their impact on satisfaction.

### 1.1 Basic Needs (Must-be Requirements)

Basic needs are essential product characteristics.

Customers generally assume these requirements will be fulfilled. Their presence does not necessarily create additional satisfaction, but their absence produces significant dissatisfaction.

Examples:

- Secure account authentication.
- Reliable payment processing.
- Protection of customer information.
- Availability of essential product functionality.
- Accurate transaction records.

Product management implication:

Basic requirements should receive priority because failure to provide them can damage customer trust and product acceptance.

### 1.2 Performance Needs (One-dimensional Requirements)

Performance needs have a proportional relationship with customer satisfaction.

Improving performance generally increases satisfaction. Poor performance generally decreases it.

Examples:

- Application response time.
- Processing speed.
- Battery life.
- Delivery time.
- Storage capacity.

Product management implication:

These requirements should be measured through performance indicators and competitive benchmarking.

### 1.3 Excitement Needs (Attractive Requirements)

Excitement needs are unexpected features that can create positive customer experiences.

Customers may not expect these features. Their absence generally does not produce significant dissatisfaction, but their presence can increase satisfaction.

Examples:

- Personalized recommendations.
- Predictive product assistance.
- Intelligent notifications.
- Innovative dashboard capabilities.
- Additional convenience features.

Product management implication:

Excitement requirements provide opportunities for differentiation and innovation.

### 1.4 Indifferent Requirements

Indifferent requirements have little effect on customer satisfaction.

Customers generally neither value nor object to these characteristics.

Examples:

- Unused interface customization options.
- Features with limited practical relevance.
- Technical capabilities that do not affect customer workflows.

Product management implication:

Avoid investing substantial development resources in features that customers do not value.

### 1.5 Reverse Requirements

Reverse requirements describe characteristics that some customers actively dislike.

Providing these features may decrease satisfaction.

Examples:

- Excessive notifications.
- Unwanted personalization.
- Complicated interface changes.
- Unnecessary automated interactions.

Product management implication:

Investigate customer segments before implementing features that may negatively affect particular groups.

### 1.6 Questionable Responses

Questionable responses arise from inconsistent or potentially misunderstood questionnaire answers.

They may indicate:

- Misunderstood questions.
- Incorrect survey completion.
- Respondent inattention.
- Questionnaire design problems.

They should be investigated rather than included in ordinary satisfaction calculations.

## 2. Kano Questionnaire Design

The Kano Model typically uses two questions for every product feature.

The questions examine the same characteristic under two different conditions.

**Functional question**

How would you feel if the product included this feature?

**Dysfunctional question**

How would you feel if the product did not include this feature?

Both questions use five response options:

| Response | Meaning |
|---|---|
| Like | I would like it |
| Expect | I expect it |
| Neutral | I am neutral |
| Tolerate | I can tolerate it |
| Dislike | I would dislike it |

The combination of these responses determines the Kano classification.

## 3. Kano Evaluation Matrix

The classification matrix uses functional responses as rows and dysfunctional responses as columns.

| Functional / Dysfunctional | Like | Expect | Neutral | Tolerate | Dislike |
|---|---|---|---|---|---|
| Like | Q | R | R | R | M |
| Expect | A | I | I | I | M |
| Neutral | P | I | I | I | M |
| Tolerate | P | I | I | I | M |
| Dislike | P | P | P | P | Q |

Legend:

- M: Must-be
- P: Performance
- A: Attractive
- I: Indifferent
- R: Reverse
- Q: Questionable

The classification is based on the combination of both responses rather than either response independently.

## 4. Customer Satisfaction Coefficients

The Kano Model can be extended using satisfaction and dissatisfaction coefficients.

These coefficients help compare customer reactions across different product features.

### 4.1 Satisfaction Coefficient

\[
S=\frac{A+P}{A+P+M+I}
\]

Where:

- \(A\) = Attractive responses
- \(P\) = Performance responses
- \(M\) = Must-be responses
- \(I\) = Indifferent responses

The coefficient ranges from 0 to 1.

A higher value indicates greater potential to increase satisfaction when the feature is implemented.

### 4.2 Dissatisfaction Coefficient

\[
D=-\frac{P+M}{A+P+M+I}
\]

The coefficient ranges from -1 to 0.

A value closer to -1 indicates a stronger potential for dissatisfaction when the feature is absent.

A value closer to zero indicates a weaker negative effect.

Questionable and reverse responses are excluded from these standard coefficient calculations.

### 4.3 Interpretation

| Satisfaction | Dissatisfaction | Interpretation |
|---|---|---|
| High | Strongly negative | Important performance improvement |
| Low | Strongly negative | Essential requirement |
| High | Weakly negative | Potential excitement feature |
| Low | Weakly negative | Potentially indifferent feature |

These coefficients should be interpreted together with the dominant Kano category, customer segments, sample size and business context.

They are not direct measurements of revenue, retention or absolute satisfaction.

## 5. Feature Prioritization

The Kano Model supports product prioritization by distinguishing the different ways features influence satisfaction.

A practical product development approach is:

| Category | Product management approach |
|---|---|
| Must-be | Establish minimum acceptable functionality |
| Performance | Improve measurable product performance |
| Attractive | Evaluate differentiation and innovation opportunities |
| Indifferent | Defer unless other strategic factors justify investment |
| Reverse | Investigate negative customer preferences |
| Questionable | Review questionnaire quality and collect better responses |

A feature should not be prioritized solely by its Kano classification.

Other considerations include:

- Implementation cost.
- Technical feasibility.
- Security requirements.
- Regulatory obligations.
- Business strategy.
- Customer segment importance.
- Competitive positioning.
- Development dependencies.

## 6. Python Implementation

The Python implementation provides a structured analytical model.

### Core components

**Response**

An enumeration containing the five questionnaire response options.

**KanoCategory**

Represents the six possible Kano classifications.

**KanoResponse**

Stores an individual customer's functional and dysfunctional responses.

**Feature**

Maintains customer responses for a product feature and calculates classification counts.

**KanoAnalyzer**

Coordinates feature registration, response collection, classification, reporting and export.

### Analytical mechanisms

The implementation provides:

- Kano matrix evaluation.
- Duplicate customer response detection.
- Dominant category calculation.
- Satisfaction coefficient calculation.
- Dissatisfaction coefficient calculation.
- Questionable response monitoring.
- CSV export.
- JSON export.

The feature classification is determined by the highest substantive response count. Questionable responses are excluded from the dominant category calculation.

Ties are resolved by the ordering of the category enumeration, so tied classifications should be examined before making product decisions.

### Execution

Run:

`python kano_model.py`

The program generates:

- `kano_analysis.csv`
- `kano_analysis.json`

Only the Python standard library is required.

## 7. JavaScript Implementation

The JavaScript implementation focuses on event-driven processing.

### Core components

**KanoResponse**

Validates customer questionnaire responses and evaluates the Kano matrix.

**Feature**

Uses a `Map` to maintain unique customer responses.

**KanoEngine**

Extends `EventEmitter` to publish events when features are registered and responses are submitted.

### Event-driven workflow

`Feature Registration → Response Submission → Validation → Classification → Event Publication → Report Generation`

The implementation separates response processing from reporting.

This makes it possible for other application components to subscribe to response events.

### Asynchronous reporting

Node.js file operations use asynchronous promises.

The implementation exports a JSON report without blocking the event loop during file writing.

### Execution

Run:

`node kano_model.js`

The implementation requires Node.js and uses built-in modules only.

## 8. C++17 Implementation

The C++ implementation emphasizes structured domain modeling and efficient in-memory processing.

### Core components

| Component | Responsibility |
|---|---|
| `Response` | Questionnaire response enumeration |
| `Category` | Kano classification enumeration |
| `CustomerResponse` | Customer response representation |
| `Feature` | Feature-level response management |
| `Coefficients` | Satisfaction and dissatisfaction results |
| `GovernanceEngine` | Feature registration and reporting |

### Implementation decisions

The Kano evaluation matrix uses a fixed-size array.

This provides constant-time classification:

\[
O(1)
\]

The `map` container maintains feature records and category counts.

The `vector` container stores customer responses.

Duplicate detection uses an algorithmic search over the feature's response collection.

For a feature with \(n\) responses:

- Adding a response requires \(O(n)\) duplicate detection.
- Calculating category counts requires \(O(n)\).
- Classification of an individual response requires \(O(1)\).

For larger workloads, an additional hash-based customer identifier index could reduce duplicate detection to average \(O(1)\).

### Compilation

Compile using:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic kano_model.cpp -o kano_model`

Run:

`./kano_model`

On Windows:

`.\kano_model.exe`

No external libraries are required.

## 9. Java 17 Enterprise Implementation

The Java implementation introduces an enterprise-oriented domain model.

### Domain components

**CustomerResponse**

A Java record representing immutable questionnaire data.

**KanoFeature**

Maintains feature information, customer responses and lifecycle status.

**KanoService**

Coordinates registration, response processing and reporting.

**Analysis**

Represents a feature's analytical result.

**FeatureStatus**

Defines the product feature lifecycle.

### Feature lifecycle

The implementation models the following transitions:

`PROPOSED → UNDER_RESEARCH → APPROVED → IN_DEVELOPMENT → RELEASED`

A feature may also transition to `REJECTED` from the proposed, research or approved stages.

Invalid transitions are rejected through validation exceptions.

### Enterprise considerations

The implementation provides:

- Immutable response records.
- Explicit domain types.
- Feature lifecycle enforcement.
- Duplicate response protection.
- Stream-based analysis.
- Custom validation exceptions.
- Centralized service operations.

The lifecycle model is separate from the Kano classification.

A feature being classified as attractive does not automatically mean that it should be approved or released.

## 10. PostgreSQL Database Architecture

The PostgreSQL implementation provides a relational foundation for storing customer research and product decisions.

### Database relationships

`Products → Features → Kano Responses`

`Customers → Kano Responses`

`Surveys → Kano Responses`

`Features → Feature Decisions`

### Tables

| Table | Purpose |
|---|---|
| `products` | Product information |
| `features` | Product feature definitions |
| `customers` | Customer records |
| `surveys` | Survey configuration |
| `kano_responses` | Functional and dysfunctional responses |
| `feature_decisions` | Product prioritization decisions |

### Classification function

The `classify_kano()` function implements the Kano evaluation matrix.

It accepts two response values and returns one classification.

The function is immutable because its result depends only on its input parameters.

### Classification trigger

The `set_kano_classification()` trigger automatically calculates the classification when questionnaire responses are inserted or updated.

This prevents applications from independently supplying an inconsistent classification.

### Reporting view

The `feature_kano_analysis` view calculates:

- Response counts.
- Dominant Kano category.
- Satisfaction coefficient.
- Dissatisfaction coefficient.
- Questionable response count.
- Questionable response rate.

PostgreSQL aggregate filters are used to calculate category-specific counts.

### Prioritization function

The `get_feature_priorities()` function ranks analyzed features using dissatisfaction and satisfaction coefficients.

Features with stronger negative dissatisfaction coefficients receive earlier positions in the ranking.

This ranking is an analytical aid rather than an automatic development decision.

### Stored procedure

The `record_feature_decision()` procedure records product decisions.

It validates the feature identifier, decision rationale and decision owner.

The feature record is locked during decision insertion to coordinate concurrent operations involving the same feature.

### Integrity controls

The database implements:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Non-empty field validation.
- Enumerated response types.
- Survey date validation.
- Automatic classification.
- Feature lifecycle validation.
- Transaction handling.
- Reporting indexes.

## 11. Integrated Product Development Workflow

The five implementations represent different ways to manage the same customer research problem.

The complete business workflow is:

`Product Definition`

↓

`Feature Identification`

↓

`Customer Segment Selection`

↓

`Functional Questionnaire`

↓

`Dysfunctional Questionnaire`

↓

`Response Validation`

↓

`Kano Classification`

↓

`Category Aggregation`

↓

`Satisfaction Coefficient Calculation`

↓

`Dissatisfaction Coefficient Calculation`

↓

`Feature Prioritization`

↓

`Product Decision`

↓

`Development and Release`

Customer feedback should be collected continuously because customer expectations and product preferences can change over time.

## 12. Validation and Failure Handling

The implementations address several common operational problems.

| Failure condition | Handling |
|---|---|
| Empty customer identifier | Reject response |
| Unknown feature identifier | Reject submission |
| Invalid questionnaire option | Reject response |
| Duplicate customer response | Reject duplicate |
| Feature without responses | Exclude from reports or reject individual analysis |
| Questionable response | Track separately |
| Zero coefficient denominator | Return zero coefficients |
| Invalid lifecycle transition | Reject transition |
| Duplicate feature registration | Reject registration |
| Invalid decision rationale | Reject decision |

Questionnaire quality is particularly important because classification accuracy depends on customers understanding both questions consistently.

## 13. Performance and Scalability

The implementations use different data structures to address the same analytical workload.

| Operation | Typical complexity |
|---|---|
| Kano matrix lookup | O(1) |
| Category aggregation | O(n) |
| Dominant classification | O(1) after aggregation |
| Coefficient calculation | O(1) after aggregation |
| Python customer duplicate detection | O(n) |
| JavaScript Map lookup | Average O(1) |
| C++ vector duplicate detection | O(n) |
| Java HashMap duplicate detection | Average O(1) |
| SQL indexed feature lookup | Index-dependent |

Here, \(n\) represents the number of responses being evaluated for a feature.

For large customer research datasets, useful improvements include:

- Batch response ingestion.
- Indexed customer and feature identifiers.
- Survey-level partitioning.
- Incremental category aggregation.
- Customer segment reporting.
- Historical survey comparisons.
- Controlled access to customer information.

The reporting view performs aggregation over stored responses. Large production datasets may benefit from materialized reporting tables or precomputed aggregates.

## 14. Security and Data Governance

Customer feedback may contain commercially sensitive information and identifiable customer references.

Appropriate controls include:

- Pseudonymizing customer identifiers.
- Restricting access to raw questionnaire records.
- Separating survey administration from reporting permissions.
- Validating application inputs.
- Using parameterized SQL queries.
- Encrypting database connections.
- Protecting exported CSV and JSON files.
- Applying data retention policies.
- Recording product decisions with accountable ownership.
- Avoiding unnecessary exposure of customer-level responses.

The sample implementations demonstrate domain-level validation. They do not constitute a complete authenticated production survey platform.

## 15. Limitations and Interpretation

The Kano Model is a classification framework, not a complete product investment methodology.

Its results depend on:

1. Questionnaire design.
2. Customer sample quality.
3. Customer segment representation.
4. Response consistency.
5. Interpretation of category distributions.
6. Changes in customer expectations.

A dominant category may hide differences between customer segments.

For example, a feature may be attractive to enterprise customers but indifferent to retail customers.

The standard satisfaction coefficients also omit reverse and questionable responses. Reverse responses therefore require separate investigation rather than being treated as ordinary dissatisfaction observations.

A feature classified as attractive today may become a performance requirement as customer expectations evolve.

Repeated surveys can help identify such changes.

## 16. Cross-Language Implementation Comparison

| Technical dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Domain modeling | Dataclasses and enums | Classes and objects | Structs and classes | Records and classes | Relational tables |
| Classification | Dictionary matrix | Object matrix | Fixed-size array | Two-dimensional array | SQL function |
| Response storage | Lists and dictionaries | Maps | Vectors and maps | HashMaps | Relational tables |
| Validation | Exceptions | Custom errors | Exceptions | Custom exceptions | Constraints and triggers |
| Reporting | CSV and JSON | Asynchronous JSON | Console reporting | Stream-based reporting | Views and functions |
| State management | Feature objects | Event-driven engine | Governance engine | Lifecycle service | Status constraints |
| Main emphasis | Analytical processing | Event handling | Efficient processing | Enterprise domain management | Data integrity |

## 17. Practical Product Management Application

Consider an enterprise customer platform with four proposed features:

| Feature | Customer need | Potential product treatment |
|---|---|---|
| Account Security | Basic need | Ensure minimum acceptable security |
| Application Speed | Performance need | Improve processing and response time |
| AI Recommendations | Excitement need | Assess differentiation and adoption |
| Custom Dashboard | Indifferent need | Evaluate demand before investing |

The classification must be established through actual customer questionnaire responses rather than assigned in advance based on assumptions.

Product managers can combine Kano analysis with development cost, strategic importance, feasibility and customer segment requirements to make more informed decisions.

The central distinction is that the Kano Model explains how individual product characteristics influence customer satisfaction, while product prioritization determines which characteristics should receive development investment.
