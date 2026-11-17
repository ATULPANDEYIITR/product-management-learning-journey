# Product Metrics: North Star, Input, Output and Guardrail Metrics

## 1. Product Metrics Framework

Product metrics are quantitative measurements used to understand how a product creates customer value, how users interact with its capabilities, how the business performs, and whether product growth introduces unacceptable operational or customer risks.

A product metrics framework connects four distinct categories:

1. **North Star Metric:** Represents the primary value delivered to customers.
2. **Input Metrics:** Measure the activities and behaviours that contribute to the North Star Metric.
3. **Output Metrics:** Measure the resulting product and business outcomes.
4. **Guardrail Metrics:** Monitor conditions that must remain acceptable while pursuing growth.

The four categories serve different management purposes. They should be evaluated together rather than treated as interchangeable performance indicators.

## 2. Product Scenario

The implementations use a subscription-based digital learning platform.

The platform provides online lessons, tracks learning activities, supports recurring subscriptions, and measures customer engagement.

The product team wants to increase meaningful learning activity without compromising application reliability or customer experience.

The selected measurement framework is:

| Category | Metric | Target | Purpose |
|---|---|---:|---|
| North Star | Weekly Active Learners | 12,000 | Measure recurring customer value |
| Input | Activation Rate | 65% | Measure successful initial adoption |
| Input | Lesson Completion Rate | 75% | Measure learning progress |
| Input | Weekly Learning Sessions | 45,000 | Measure meaningful engagement |
| Output | Subscription Revenue | ₹15,00,000 | Measure commercial performance |
| Output | Retention Rate | 85% | Measure continued customer relationships |
| Guardrail | Application Error Rate | Maximum 1% target | Protect reliability |
| Guardrail | Page Load Time | Maximum 2 seconds target | Protect responsiveness |
| Guardrail | Support Complaint Rate | Maximum 2% target | Protect customer experience |

The targets represent the operating assumptions used by the demonstration implementations. They are not universal industry benchmarks.

## 3. North Star Metric

### 3.1 Definition

A North Star Metric is the primary measure of recurring customer value delivered by a product.

It provides a common direction for product, engineering, design, analytics, and business teams.

A useful North Star Metric should:

- Represent meaningful customer value.
- Reflect product usage rather than only commercial activity.
- Be measurable using reliable data.
- Connect with important customer behaviours.
- Support consistent evaluation over time.
- Be sufficiently understandable for cross-functional teams.

The selected North Star Metric is Weekly Active Learners.

It counts distinct users who complete at least one qualifying learning activity during a seven-day reporting window.

A qualifying activity might include completing a lesson or passing an assessment. Merely opening the application should not automatically qualify as meaningful learning activity.

### 3.2 Calculation

The North Star Metric is calculated as:

\[
NSM = \left|\text{Distinct users completing qualifying activity}\right|
\]

For example:

- Monday to Sunday qualifying learners: 12,400
- Previous week qualifying learners: 10,800

Percentage change:

\[
\frac{12,400-10,800}{10,800}\times100
=14.81\%
\]

The product experienced approximately 14.81% growth in its North Star Metric.

This result indicates increased meaningful activity. It does not independently establish why the increase occurred or whether the increase is profitable.

### 3.3 North Star Metric limitations

A North Star Metric is not a complete representation of product performance.

An increase may result from:

- More newly acquired users.
- Improved activation.
- Higher engagement frequency.
- Better retention.
- Seasonal demand.
- Marketing campaigns.
- Changes in measurement definitions.

It can also increase while customer experience deteriorates.

For this reason, the North Star Metric requires supporting input, output, and guardrail measurements.

## 4. Input Metrics

### 4.1 Definition

Input Metrics measure the product activities, behaviours, and operational factors that influence the North Star Metric.

They help product teams identify actionable opportunities for improvement.

Unlike the North Star Metric, input metrics usually describe the mechanisms that contribute to value creation.

### 4.2 Activation Rate

Activation measures the proportion of eligible new users who complete a predefined initial value-generating action.

\[
Activation\ Rate =
\frac{Activated\ New\ Users}
{Eligible\ New\ Users}
\times100
\]

Example:

- Eligible new users: 10,000
- Activated new users: 6,800

\[
Activation\ Rate = 68\%
\]

A higher activation rate indicates that a larger proportion of new users reach the defined activation milestone.

The activation event must be clearly specified. Account registration alone may not represent successful product adoption.

### 4.3 Lesson Completion Rate

This metric measures the proportion of started lessons that are completed.

\[
Completion\ Rate =
\frac{Completed\ Lessons}
{Started\ Lessons}
\times100
\]

Example:

- Started lessons: 10,000
- Completed lessons: 7,800

\[
Completion\ Rate = 78\%
\]

The denominator must be defined consistently. Repeated lesson attempts, abandoned sessions, and duplicate events require appropriate handling.

### 4.4 Weekly Learning Sessions

This metric measures qualifying learning sessions during a reporting week.

A session should follow an explicit definition involving meaningful activity rather than arbitrary application openings.

For example, a session may require a lesson interaction, assessment attempt, or meaningful learning action.

A session count can be affected by session timeout rules and event instrumentation. Therefore, changes to session definitions must be documented.

### 4.5 Relationship with the North Star Metric

The relationship can be represented as:

Product discovery  
→ Account registration  
→ Activation  
→ Meaningful learning sessions  
→ Lesson completion  
→ Recurring learning behaviour  
→ Weekly Active Learners

These activities form a measurement model, not a guaranteed causal sequence.

Improving an input metric does not necessarily improve the North Star Metric. The relationship should be validated using cohort analysis, experiments, and behavioural evidence.

## 5. Output Metrics

### 5.1 Definition

Output Metrics measure the resulting product or business outcomes.

They help determine whether increased product engagement translates into sustainable business performance.

Output metrics are generally lagging indicators because their values may change after underlying customer behaviours change.

### 5.2 Subscription Revenue

Subscription revenue measures recognized revenue during a defined reporting period.

A simplified representation is:

\[
Revenue =
\sum_{i=1}^{n} RecognizedSubscriptionRevenue_i
\]

Actual financial reporting must account for applicable recognition rules, refunds, discounts, cancellations, taxes, and subscription periods.

Revenue should not be confused with cash collected, bookings, or annual recurring revenue.

### 5.3 Retention Rate

Retention measures the proportion of eligible users who continue using the product after a defined interval.

A cohort-based formula is:

\[
Retention =
\frac{Users\ active\ at\ the\ defined\ return\ interval}
{Users\ in\ the\ original\ eligible\ cohort}
\times100
\]

For example:

- Original eligible cohort: 10,000 users
- Users returning during the specified interval: 8,600

\[
Retention = 86\%
\]

Retention measurement requires a consistent cohort definition and return interval.

Weekly retention, monthly retention, and subscription renewal retention are different measurements and should not be combined without an explicit analytical reason.

### 5.4 Input and Output Distinction

| Input Metrics | Output Metrics |
|---|---|
| Explain contributing behaviours | Describe resulting outcomes |
| Often operational and actionable | Often business-oriented |
| Activation | Revenue |
| Learning sessions | Retention |
| Lesson completion | Subscription growth |
| Help diagnose product changes | Help assess resulting performance |

Input metrics may change before output metrics. Output metrics should not be interpreted as direct evidence that a particular input caused the observed result.

## 6. Guardrail Metrics

### 6.1 Definition

Guardrail Metrics measure conditions that must remain within acceptable boundaries while the product team pursues its growth objectives.

They prevent teams from improving one performance indicator at the expense of product quality, user experience, security, or operational stability.

A growth initiative should not automatically be considered successful simply because its North Star Metric increases.

### 6.2 Application Error Rate

\[
Error\ Rate =
\frac{Failed\ Requests}
{Total\ Requests}
\times100
\]

Example:

- Failed requests: 2,400
- Total requests: 100,000

\[
Error\ Rate = 2.4\%
\]

The demonstration target is 1%, with a maximum valid operating boundary of 2%.

The observed 2.4% value breaches the permitted boundary.

### 6.3 Page Load Time

Page load time measures the duration required for a specified application experience to become available.

The implementation uses average page load time for demonstration purposes.

Production monitoring should generally examine percentiles such as:

- p50: Median performance.
- p75: Experience of users at the 75th percentile.
- p95: Slower experiences affecting a substantial minority.
- p99: Extreme latency behaviour.

An average can conceal serious performance problems affecting a smaller user group.

### 6.4 Support Complaint Rate

\[
Complaint\ Rate =
\frac{Users\ generating\ qualifying\ complaints}
{Eligible\ active\ users}
\times100
\]

The complaint definition should specify what constitutes a complaint, how duplicate complaints are handled, and which users belong in the denominator.

### 6.5 Guardrail Interpretation

The demonstration produces the following observations:

| Guardrail | Observed | Target | Result |
|---|---:|---:|---|
| Application Error Rate | 2.4% | 1% | Breach |
| Page Load Time | 2.2 seconds | 2 seconds | Target missed |
| Support Complaint Rate | 1.8% | 2% | Within target |

A product can therefore achieve higher engagement while experiencing deteriorating reliability.

The correct management response is to investigate the guardrail breaches rather than interpreting engagement growth as an unconditional success.

## 7. Relationship Between the Four Metric Categories

The complete measurement architecture is:

Product Activities  
→ Input Metrics  
→ North Star Metric  
→ Output Metrics

Guardrail Metrics monitor the entire process.

A more detailed representation:

- Input Metrics describe the behaviours that contribute to customer value.
- The North Star Metric measures recurring value delivered.
- Output Metrics measure the resulting commercial and customer outcomes.
- Guardrail Metrics constrain unacceptable trade-offs.

The relationship is conceptual. Real product systems may contain feedback loops, delayed effects, confounding variables, and interactions between metrics.

### 7.1 Metric Classification

| Question | Appropriate Category |
|---|---|
| Are users receiving recurring product value? | North Star |
| What behaviours contribute to that value? | Input |
| What business results follow? | Output |
| Are we damaging product quality while growing? | Guardrail |

A single metric should not be assigned to multiple categories merely because it is relevant to several business objectives. Its primary measurement role should be documented.

## 8. Python Implementation

File: `product_metrics.py`

The Python implementation provides a complete product analytics simulation.

### 8.1 Domain Model

The implementation uses:

| Component | Responsibility |
|---|---|
| `MetricCategory` | Defines the four metric categories |
| `Direction` | Specifies higher, lower, or range-based evaluation |
| `MetricDefinition` | Stores metric configuration and thresholds |
| `MetricObservation` | Represents a period-specific measurement |
| `MetricRegistry` | Maintains validated metric definitions |
| `MetricStore` | Stores observations |
| `MetricEvaluator` | Calculates performance and percentage change |
| `GuardrailMonitor` | Detects unacceptable operating conditions |
| `ProductAnalytics` | Produces product-level reports |

### 8.2 Metric Registration

Metric definitions are stored in a dictionary indexed by normalized metric names.

Duplicate registrations are rejected.

Metric configurations include:

- Name.
- Category.
- Unit.
- Direction.
- Target.
- Minimum.
- Maximum.
- Description.

This separation allows metric definitions to remain independent of their observations.

### 8.3 Observation Management

Observations contain:

- Metric name.
- Reporting period.
- Measured value.
- Sample size.
- Recording date.

The store rejects duplicate metric-period combinations and invalid observations.

### 8.4 Evaluation

The evaluator calculates:

\[
PercentageChange =
\frac{Current-Previous}{|Previous|}
\times100
\]

When the previous value is zero, percentage change is undefined and is returned as `None`.

The evaluator also determines whether a metric is on target.

### 8.5 Guardrail Monitoring

The guardrail monitor checks every active guardrail definition.

It identifies:

- Missing observations.
- Maximum threshold violations.
- Minimum threshold violations.

Critical breaches are represented as structured alerts.

### 8.6 Reporting

The reporting service produces:

- North Star performance.
- Metric classifications.
- Current and previous values.
- Percentage changes.
- Target achievement.
- Guardrail alerts.
- Product performance diagnosis.

The optional JSON export creates a machine-readable report.

### 8.7 Validation and Testing

The script includes assertions for:

- Percentage change calculations.
- Zero-denominator handling.
- North Star evaluation.
- Guardrail detection.
- Rejection of negative observations.

The implementation uses Python standard-library modules and does not require third-party packages.

## 9. JavaScript Implementation

File: `product_metrics.js`

The JavaScript implementation provides an event-driven metric processing architecture.

Its primary distinction is the separation between incoming measurement events, aggregation, and policy evaluation.

### 9.1 Event-Driven Architecture

The processing sequence is:

Metric Event  
→ Event Ledger  
→ Metric Aggregator  
→ Metric Policy  
→ Product Metrics Engine  
→ Dashboard or Alert

The architecture uses Node.js `EventEmitter` for notifications.

### 9.2 Event Ledger

Each event contains:

- Unique event identifier.
- Metric name.
- Reporting period.
- Value.
- Sample size.
- Timestamp.

Duplicate event identifiers are ignored.

This provides basic idempotency within the in-memory demonstration.

A production implementation should use persistent event identifiers and durable storage to preserve deduplication across restarts.

### 9.3 Weighted Aggregation

The implementation calculates weighted averages:

\[
WeightedAverage =
\frac{\sum_{i=1}^{n}(Value_i \times SampleSize_i)}
{\sum_{i=1}^{n}SampleSize_i}
\]

This prevents measurement batches with different sample sizes from receiving equal influence.

Weighted averaging is appropriate only when the observations represent compatible measurements. It should not replace proper numerator-denominator aggregation for rates when underlying counts are available.

### 9.4 Asynchronous Processing

The engine serializes ingestion operations using a Promise queue.

This provides ordered updates for the in-memory event ledger.

The implementation also emits:

- `metric:ingested`
- `guardrail:breach`
- `duplicate`

These events allow reporting and monitoring components to respond without being tightly coupled to the ingestion mechanism.

### 9.5 Experiment Comparison

The experiment analyzer compares control and treatment measurements.

Absolute lift:

\[
AbsoluteLift = Treatment-Control
\]

Relative lift:

\[
RelativeLift =
\frac{Treatment-Control}{|Control|}
\times100
\]

The implementation checks minimum sample-size requirements.

It does not calculate statistical significance or establish causal impact. A production experiment evaluation must account for experiment design, randomization, variance, confidence intervals, statistical power, and multiple comparisons where applicable.

## 10. C++17 Implementation

File: `product_metrics.cpp`

The C++ implementation focuses on strongly structured metric evaluation and operational monitoring.

### 10.1 Domain Types

The program defines:

- `MetricCategory`
- `Direction`
- `MetricStatus`
- `Severity`
- `MetricDefinition`
- `Observation`
- `MetricEvaluation`
- `Alert`

Enumerations prevent arbitrary category and status values.

`std::optional` represents missing targets and previous-period measurements without requiring artificial numeric defaults.

### 10.2 Registry and Observation Store

The metric registry uses `std::map` for deterministic lookup and reporting.

The observation store uses a composite key:

\[
(MetricName, Period)
\]

This provides efficient ordered lookup.

For a registry containing \(M\) metrics and \(O\) observations:

- Metric lookup: \(O(\log M)\).
- Observation lookup: \(O(\log O)\).
- Full metric evaluation: proportional to the number of metrics, excluding lookup costs.

### 10.3 Evaluation Engine

The evaluator determines performance using the metric direction.

Higher-is-better metrics are evaluated against minimum targets.

Lower-is-better metrics are evaluated against maximum targets.

Range-based metrics are evaluated against both boundaries.

### 10.4 Guardrail Engine

The guardrail engine examines operational thresholds independently of North Star growth.

It produces critical alerts for unacceptable measurements and warnings for missing observations.

This design prevents a positive product growth result from suppressing reliability concerns.

### 10.5 Experiment Analyzer

The experiment analyzer calculates absolute and relative lift.

It rejects groups with insufficient observations.

The minimum sample-size rule is a validation condition rather than a statistical significance test.

The program uses only C++17 standard-library components.

## 11. Java 17 Implementation

File: `ProductMetrics.java`

The Java implementation presents an enterprise-oriented domain and service architecture.

### 11.1 Immutable Domain Records

Java 17 records represent:

- `MetricDefinition`
- `Observation`
- `Evaluation`
- `Alert`
- `ExperimentGroup`
- `ExperimentResult`
- `ProductReport`

Records reduce unnecessary mutable state and provide clear domain boundaries.

### 11.2 Repository Layer

`MetricRepository` maintains:

- Metric definitions.
- Period-specific observations.
- Processed event identifiers.

Synchronized registration and observation methods protect the demonstration repository against concurrent modifications.

### 11.3 Policy Layer

`EvaluationPolicy` defines the metric evaluation contract.

`DefaultEvaluationPolicy` implements target-based performance evaluation.

`GuardrailPolicy` independently determines operational breaches.

This separates measurement rules from repository operations.

### 11.4 Service Layer

`ProductMetricsService` coordinates:

- Metric registration.
- Observation ingestion.
- Metric evaluation.
- North Star validation.
- Product report generation.

The service requires exactly one active North Star Metric.

### 11.5 Experiment Service

`ExperimentService` validates experiment groups and calculates absolute and relative lift.

The service uses explicit minimum sample-size rules.

The current implementation does not perform hypothesis testing.

### 11.6 Enterprise Design Considerations

The demonstration illustrates:

- Immutable domain records.
- Explicit business exceptions.
- Repository and service separation.
- Policy-based evaluation.
- Category-level aggregation.
- Duplicate-event protection.
- Controlled state changes.

A production deployment would normally introduce persistent repositories, transactional ingestion, authentication, authorization, audit logging, and distributed event processing.

## 12. PostgreSQL Database Implementation

File: `product_metrics.sql`

The PostgreSQL implementation models a relational product analytics workflow.

### 12.1 Relational Architecture

The principal relationships are:

Products  
→ Reporting Periods  
→ Metric Definitions  
→ Metric Observations  
→ Metric Evaluations

Additional relationships include:

Metric Definitions  
→ Metric Dependencies

Metric Definitions  
→ Guardrail Policies  
→ Guardrail Alerts

Products  
→ Experiments  
→ Experiment Results

### 12.2 Core Tables

| Table | Purpose |
|---|---|
| `products` | Identifies the products being measured |
| `reporting_periods` | Defines measurement windows |
| `metric_definitions` | Stores metric configurations |
| `metric_dependencies` | Records relationships between metrics |
| `metric_observations` | Stores measured values |
| `guardrail_policies` | Defines operating boundaries |
| `guardrail_alerts` | Records policy violations |
| `experiments` | Stores experiment definitions |
| `experiment_results` | Stores control and treatment results |
| `metric_evaluations` | Stores evaluated metric performance |

### 12.3 Database Integrity

The database uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Partial unique indexes.
- Performance-oriented indexes.
- Validation triggers.

A partial unique index ensures that a product has no more than one active North Star Metric.

The observation trigger validates that an observation belongs to the same product as its metric definition.

It also enforces the configured valid measurement boundaries.

### 12.4 Evaluation Function

The `evaluate_metric` function:

1. Retrieves the metric definition.
2. Retrieves the current observation.
3. Identifies the previous reporting period.
4. Retrieves the previous observation.
5. Calculates percentage change.
6. Determines target status.
7. Returns the evaluation result.

Missing current observations are represented using the `missing` status.

### 12.5 Processing Procedure

The `process_product_metrics` procedure processes all active metrics for a product and reporting period.

It updates existing evaluations through an `INSERT ... ON CONFLICT` operation.

This allows a reporting period to be reprocessed without creating duplicate evaluation records.

### 12.6 Guardrail Processing

The `evaluate_guardrails` function compares observations with configured operating boundaries.

It creates alerts only when the relevant policy is breached.

A unique constraint and conflict-handling clause prevent repeated alerts for the same policy and observation.

### 12.7 Reporting Views

The SQL implementation includes:

- `v_product_metric_dashboard`
- `v_north_star_performance`
- `v_guardrail_breaches`
- `v_category_performance`
- `v_experiment_lift`

These views provide reusable reporting structures without duplicating underlying measurement records.

### 12.8 Transaction Management

Sample data creation and metric processing are organized within database transactions.

The validation demonstration uses a nested PL/pgSQL exception block to reject an invalid observation without aborting the entire script.

## 13. Product Metrics and Product Management Decisions

Metrics are useful only when they support appropriate product decisions.

A measurement framework should connect product observations to investigation and action.

| Observation | Possible Investigation | Product Decision |
|---|---|---|
| Activation decreases | Registration friction, onboarding completion | Improve onboarding |
| Lesson completion decreases | Content difficulty, usability, lesson length | Investigate learning experience |
| Weekly sessions increase | Frequency, meaningful activity, duplicate events | Validate engagement quality |
| North Star increases | Acquisition, activation, retention, cohort composition | Identify contributing factors |
| Revenue increases | Conversion, pricing, subscriptions | Evaluate commercial sustainability |
| Retention decreases | Churn, product relevance, service quality | Investigate retention drivers |
| Error rate increases | Deployment changes, infrastructure failures | Prioritize reliability |
| Load time increases | Query performance, application latency | Optimize performance |
| Complaints increase | User experience, product defects, support delays | Address customer problems |

The metric framework should be used to identify problems, investigate causes, evaluate interventions, and monitor their consequences.

A metric movement alone is not sufficient evidence of causation.

## 14. Product Experiments and Metric Evaluation

Product experiments provide a structured way to evaluate proposed changes.

An experiment should specify:

- A clear hypothesis.
- An eligible population.
- A control group.
- A treatment group.
- A primary outcome metric.
- Supporting input metrics.
- Guardrail metrics.
- An appropriate experiment duration.
- A statistical analysis plan.

Example:

**Hypothesis:** Simplifying the learning onboarding experience will increase activation.

Primary metric: Activation Rate.

Supporting metric: Weekly Active Learners.

Output metric: Subscription Conversion and Revenue.

Guardrails: Application Error Rate, Page Load Time, and Support Complaint Rate.

An experiment should not be declared successful merely because its primary metric improves.

The team must also consider uncertainty, statistical significance, sample size, practical effect size, and guardrail outcomes.

## 15. Measurement Quality and Governance

Reliable product decisions depend on consistent metric definitions and trustworthy source data.

### 15.1 Metric Definition Documentation

Every production metric should specify:

- Business purpose.
- Category.
- Formula.
- Numerator.
- Denominator.
- Unit.
- Reporting interval.
- Eligible population.
- Exclusion rules.
- Source events.
- Data owner.
- Target.
- Guardrail boundary where applicable.

### 15.2 Data Quality Controls

Important controls include:

- Duplicate-event detection.
- Missing-event monitoring.
- Invalid-value rejection.
- Timestamp normalization.
- Consistent user identifiers.
- Time-zone handling.
- Bot and test-account exclusion.
- Late-arriving event handling.
- Cohort consistency.
- Version-controlled metric definitions.

### 15.3 Security and Privacy

Product analytics systems may contain sensitive behavioural information.

Appropriate controls include:

- Least-privilege database access.
- Pseudonymous identifiers.
- Data minimization.
- Retention policies.
- Access logging.
- Encryption in transit and at rest.
- Aggregation of reporting outputs.
- Restrictions on unnecessary personal data collection.

Product metrics should be designed around legitimate measurement needs rather than unrestricted user tracking.

## 16. Performance and Scalability Considerations

The five implementations use different storage and processing strategies.

| Implementation | Main Storage | Evaluation Approach |
|---|---|---|
| Python | Dictionaries | Direct period-based evaluation |
| JavaScript | Maps and event ledger | Serialized asynchronous ingestion |
| C++17 | Ordered STL maps | Structured metric evaluation |
| Java 17 | Repository collections | Policy and service-based evaluation |
| PostgreSQL | Relational tables | Indexed queries, functions, and views |

For larger product analytics environments, additional considerations include:

- Incremental aggregation.
- Time-based table partitioning.
- Materialized reporting views.
- Event streaming.
- Distributed processing.
- Data warehouse integration.
- Metric definition versioning.
- Historical backfills.
- Late-arriving event correction.
- Automated data-quality monitoring.

A production implementation should avoid repeatedly scanning an entire event history to calculate a small reporting window.

## 17. Limitations of the Demonstration

The implementations are educational reference systems rather than complete production analytics platforms.

Specific limitations include:

| Area | Limitation |
|---|---|
| Data persistence | Python, JavaScript, C++17, and Java examples use in-memory data |
| Event processing | JavaScript demonstrates serialized processing, not distributed event guarantees |
| Statistical analysis | Experiment comparisons calculate observed lift without significance testing |
| Metric aggregation | Demonstration inputs are already aggregated observations |
| Retention | Retention is represented as a supplied period-specific rate |
| Reliability | Average page load time does not capture latency distributions |
| Security | Authentication and production authorization are outside the demonstration scope |
| Causality | Metric relationships do not establish causal relationships |
| Database evaluation | PostgreSQL reporting uses period-level observations and configured metric definitions |

The implementations intentionally distinguish metric definition, observation, evaluation, and policy enforcement.

## 18. Execution Instructions

### Python

Requirements: Python 3.10 or later.

File: `product_metrics.py`

Execution:

`python product_metrics.py`

Optional JSON export:

`python product_metrics.py --json report.json`

### JavaScript

Requirements: Node.js 18 or later.

File: `product_metrics.js`

Execution:

`node product_metrics.js`

The implementation uses Node.js built-in modules and requires no external npm packages.

### C++17

Requirements: A C++17-compatible compiler.

File: `product_metrics.cpp`

Compilation:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic product_metrics.cpp -o product_metrics`

Execution:

`./product_metrics`

### Java 17

Requirements: JDK 17.

File: `ProductMetrics.java`

Compilation:

`javac ProductMetrics.java`

Execution:

`java ProductMetrics`

### PostgreSQL

Requirements: PostgreSQL 15 or later.

File: `product_metrics.sql`

Execution:

`psql -U postgres -d your_database -v ON_ERROR_STOP=1 -f product_metrics.sql`

The script creates the `product_analytics` schema and its associated database objects.

Use a dedicated development database when testing the complete script.

## 19. Technical Learning Outcomes

The implementations demonstrate how a product measurement framework can be represented across procedural, event-driven, systems-oriented, enterprise-oriented, and relational database architectures.

The central technical distinctions are:

- A North Star Metric measures recurring customer value.
- Input Metrics measure contributing product behaviours.
- Output Metrics measure resulting business and customer outcomes.
- Guardrail Metrics constrain unacceptable product and operational trade-offs.

A reliable product metrics system must maintain consistent definitions, validate observations, distinguish measurement from interpretation, preserve historical reporting, and connect performance evaluation with responsible product decisions.
