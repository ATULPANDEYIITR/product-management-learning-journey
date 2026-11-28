# Experiment Metrics: Statistical Measurement and Decision Engineering

## 1. Domain Overview

Experiment metrics provide a quantitative framework for evaluating changes to a product, service, application, operational process, or business workflow.

An experiment compares outcomes between groups exposed to different conditions. In a conventional A/B experiment:

- Control receives the existing experience.
- Treatment receives the proposed change.
- Participants are assigned to groups according to an allocation policy.
- Outcomes are measured using predefined metrics.
- Statistical analysis estimates the effect of the intervention.
- Guardrail evaluation determines whether the improvement introduces unacceptable operational or business consequences.

The four principal components of an experiment measurement framework are:

| Component | Purpose | Example |
|---|---|---|
| Primary metric | Measures the principal experiment objective | Checkout conversion rate |
| Secondary metrics | Provide additional performance information | Revenue per conversion |
| Guardrail metrics | Detect unacceptable adverse effects | Refund rate and p95 latency |
| Sample size | Determines the observations required for the planned statistical test | Number of users per group |

These components have different responsibilities. A secondary metric does not automatically replace the primary metric, and a favorable primary result does not override a failed guardrail.

## 2. Primary Metrics

A primary metric is the predefined principal outcome used to evaluate whether an experiment achieves its objective.

For a checkout redesign, conversion rate is an appropriate primary metric.

Conversion rate is:

\[
CR = \frac{\text{Converted Users}}{\text{Assigned Users}}
\]

Suppose the experiment produces the following results:

| Group | Assigned users | Conversions | Conversion rate |
|---|---:|---:|---:|
| Control | 1,000 | 100 | 10% |
| Treatment | 1,000 | 120 | 12% |

The absolute improvement is:

\[
\Delta = CR_T - CR_C
\]

\[
\Delta = 12\%-10\%=2
\]

The improvement is two percentage points.

The relative improvement is:

\[
Relative\ Improvement =
\frac{CR_T-CR_C}{CR_C}\times100
\]

\[
Relative\ Improvement=20\%
\]

These measurements are not interchangeable.

A two-percentage-point absolute increase corresponds to a 20% relative increase when the baseline conversion rate is 10%.

### Primary metric selection

An effective primary metric should:

- Directly represent the experiment objective.
- Have a clearly defined numerator and denominator.
- Be measurable consistently across both groups.
- Be sensitive to the expected intervention.
- Have a predefined direction of improvement.
- Avoid unnecessary dependence on external factors.
- Be defined before examining experiment outcomes.

Only one primary metric is permitted per experiment in the supplied implementations.

This restriction prevents retrospective selection of whichever metric happens to produce the most favorable result.

## 3. Secondary Metrics

Secondary metrics provide supporting information about the consequences of an intervention.

They help explain the primary outcome and identify business effects that a single metric cannot represent.

The checkout experiment uses revenue per conversion as a secondary metric.

\[
RevenuePerConversion =
\frac{TotalRevenue}{ConvertedUsers}
\]

Example:

| Metric | Control | Treatment |
|---|---:|---:|
| Conversion rate | 10% | 12% |
| Revenue per conversion | ₹500 | ₹520 |

The conversion improvement indicates that more users complete checkout.

The revenue improvement indicates that converted users generate more revenue on average.

These observations provide different information.

A secondary metric can be statistically significant without establishing that the experiment should be deployed. Its interpretation depends on the primary objective, business context, and predefined decision policy.

### Metric hierarchy

The implementations distinguish metrics through explicit classifications:

| Classification | Evaluation responsibility |
|---|---|
| Primary | Main hypothesis evaluation |
| Secondary | Supporting business and operational analysis |
| Guardrail | Constraint enforcement |

In Python, this distinction uses an enumeration and immutable metric definitions.

In JavaScript, the metric registry uses a `Map` to enforce unique metric names.

In C++, metric categories use enumerated domain types.

In Java, metric definitions are immutable records.

PostgreSQL stores the classifications in an enumerated column and enforces one primary metric per experiment using a partial unique index.

## 4. Guardrail Metrics

Guardrail metrics measure conditions that must remain within acceptable limits.

An experiment may improve conversion while introducing problems elsewhere.

For example, a redesigned checkout might increase purchases but also increase payment failures, refund rates, or server response times.

The implementation evaluates two guardrails.

### 4.1 Refund rate

\[
RefundRate =
\frac{RefundedConversions}{TotalConversions}
\]

Suppose:

| Group | Conversions | Refunds | Refund rate |
|---|---:|---:|---:|
| Control | 100 | 3 | 3% |
| Treatment | 120 | 6 | 5% |

The absolute increase is:

\[
5\%-3\%=2\ percentage\ points
\]

The experiment policy allows a maximum absolute increase of two percentage points.

A larger increase fails the refund guardrail.

The denominator must be defined consistently. This implementation calculates refunds per converted user rather than refunds per assigned user.

### 4.2 P95 latency

Latency measures the time required for a system operation.

The 95th percentile identifies the latency below which approximately 95% of observations fall.

Unlike average latency, p95 latency helps expose slower experiences affecting a portion of users.

Example:

| Group | P95 latency |
|---|---:|
| Control | 205 ms |
| Treatment | 230 ms |

The increase is:

\[
230-205=25ms
\]

If the maximum permitted increase is 40 milliseconds, the guardrail passes.

### Guardrail decision logic

The decision engine applies these conditions:

| Condition | Result |
|---|---|
| Refund increase within threshold | Pass |
| Refund increase above threshold | Fail |
| P95 latency increase within threshold | Pass |
| P95 latency increase above threshold | Fail |
| Any required guardrail fails | Do not ship |

Guardrail thresholds are policy constraints, not statistical significance thresholds.

A guardrail may be evaluated using a statistical confidence interval or non-inferiority test in a more advanced implementation. The supplied programs use observed differences and deterministic thresholds.

## 5. Sample Size Determination

Sample size is the number of independent experimental units required in each group.

It should be calculated before the experiment starts.

Insufficient observations can make a real improvement difficult to distinguish from random variation.

Four parameters determine the sample-size calculation:

| Parameter | Meaning | Example |
|---|---|---:|
| Baseline conversion | Expected control conversion rate | 10% |
| Minimum detectable effect | Smallest relative improvement worth detecting | 10% |
| Significance level | Type I error probability | 5% |
| Statistical power | Probability of detecting the specified effect when it exists | 80% |

### 5.1 Minimum Detectable Effect

The minimum detectable effect, or MDE, represents the smallest effect the experiment is designed to identify with the selected statistical power and significance level.

For a baseline conversion of 10% and a relative MDE of 10%:

\[
p_1=0.10
\]

\[
p_2=0.10(1+0.10)=0.11
\]

The absolute difference is:

\[
\delta=0.01
\]

The experiment is designed to detect a change from 10% to 11%.

A smaller MDE generally requires a larger sample.

### 5.2 Significance Level

The significance level is commonly represented by alpha.

\[
\alpha=0.05
\]

For a two-sided test, this corresponds to a 5% Type I error threshold under the assumptions of the statistical test.

A p-value below alpha indicates that the observed result is statistically significant under the specified null hypothesis and test assumptions.

It does not establish that the treatment is economically valuable or operationally safe.

### 5.3 Statistical Power

Statistical power is:

\[
Power=1-\beta
\]

A power of 80% means that the design aims for an 80% probability of detecting the specified effect when that effect is present, subject to the model assumptions.

Increasing power generally increases the required sample size.

### 5.4 Sample-size formula

For an equal-sized two-group comparison of independent proportions, the implementations use the normal approximation:

\[
n=
\frac{
\left[
z_{1-\alpha/2}\sqrt{2\bar p(1-\bar p)}
+
z_{1-\beta}\sqrt{p_1(1-p_1)+p_2(1-p_2)}
\right]^2
}{
(p_2-p_1)^2
}
\]

Where:

- \(n\) is the required sample per group.
- \(p_1\) is the baseline conversion rate.
- \(p_2\) is the expected treatment conversion rate.
- \(\bar p\) is the average of the two expected conversion rates.
- \(z\) represents the corresponding standard-normal quantile.
- \(\alpha\) is the significance level.
- \(\beta\) is the Type II error probability.

The result is rounded upward.

This calculation assumes independent observations, equal group allocation, and a two-sided comparison of proportions.

It does not automatically account for clustering, repeated observations, unequal allocation, attrition, multiple comparisons, or sequential testing.

## 6. Experiment Assignment and Traffic Allocation

Random assignment helps reduce systematic differences between experiment groups.

The implementations use deterministic hash-based allocation.

The general mechanism is:

Experiment ID + Participant ID
        |
        v
Stable Hash Function
        |
        v
Numeric Bucket
        |
        +----> Control
        |
        +----> Treatment

Stable allocation provides several advantages:

- A participant receives a consistent variant.
- Assignment can be reproduced.
- Application restarts do not require maintaining an in-memory assignment table.
- Assignment logic can be tested independently.

The Python and JavaScript implementations use SHA-256.

The Java implementation also uses SHA-256.

The C++ implementation uses FNV-1a for its local simulation. FNV-1a is not a cryptographic hash and should not be used for security-sensitive allocation.

The PostgreSQL implementation uses SHA-256 through `pgcrypto`.

Production systems should also address:

- Participant identity normalization.
- Anonymous and authenticated identity transitions.
- Experiment-specific salt management.
- Allocation changes.
- Cross-device consistency.
- Exposure logging.
- Concurrent assignment requests.
- Traffic allocation outside the experiment.
- Repeated participation and duplicate events.

A stable hash assignment is not itself proof of statistical randomization quality. Assignment balance and possible population bias should be monitored.

## 7. Statistical Evaluation

The primary metric in the example is a binary conversion outcome.

The implementation uses a two-proportion z-test.

### Null hypothesis

\[
H_0:p_T=p_C
\]

The null hypothesis states that the population conversion rates are equal.

### Alternative hypothesis

\[
H_1:p_T\neq p_C
\]

The alternative hypothesis states that the population conversion rates differ.

The pooled proportion is:

\[
\hat p=
\frac{x_C+x_T}{n_C+n_T}
\]

The standard error is:

\[
SE=
\sqrt{
\hat p(1-\hat p)
\left(
\frac{1}{n_C}+\frac{1}{n_T}
\right)
}
\]

The test statistic is:

\[
z=\frac{\hat p_T-\hat p_C}{SE}
\]

The programs calculate a two-sided p-value from the standard-normal distribution.

### Interpretation

| P-value | Interpretation |
|---|---|
| Below 0.05 | Statistically significant at the 5% level |
| Equal to 0.05 | Not below the predefined threshold |
| Above 0.05 | Not statistically significant |

Statistical significance is not equivalent to practical significance.

An experiment can produce a statistically significant improvement that is too small to justify deployment.

A statistically nonsignificant result does not prove that the treatment has no effect.

### Continuous secondary metrics

Revenue is analyzed using the difference between group means.

The Python, JavaScript, C++, and Java programs implement Welch-style variance calculations with a normal approximation for the p-value.

Welch's t-test is preferable to an equal-variance t-test when group variances may differ.

The implementations do not provide an exact Student-t distribution calculation. For small samples or highly skewed revenue distributions, a production analysis should use an appropriately validated statistical method, potentially including bootstrap confidence intervals or a robust estimator.

## 8. Experiment Decision Framework

The final decision combines statistical evidence, sample sufficiency, and guardrail compliance.

The implemented policy is:

| Condition | Decision |
|---|---|
| Required sample not reached | Inconclusive |
| Sample sufficient, guardrail failed | Do not ship |
| Sample sufficient, guardrails passed, significant positive primary effect | Ship |
| Sample sufficient, no significant positive primary effect | Inconclusive |

The decision hierarchy is:

Sample Sufficiency
        |
        v
Guardrail Evaluation
        |
        v
Primary Metric Evaluation
        |
        v
Final Decision

The distinction between an inconclusive result and a failed experiment is important.

An inconclusive result indicates insufficient evidence for the deployment decision under the predefined rules.

A failed guardrail indicates that the treatment violates an operational or business constraint.

Neither outcome should be interpreted as proof that every aspect of the treatment is ineffective.

The example decision engine evaluates observed guardrail differences. It does not implement confidence-bound-based safety tests or a complete non-inferiority framework.

## 9. Python Implementation

File: `experiment_metrics.py`

The Python implementation provides an integrated experiment simulation and analysis workflow.

### Architecture

| Component | Responsibility |
|---|---|
| `MetricType` | Defines metric categories |
| `ExperimentConfig` | Stores and validates experiment parameters |
| `MetricDefinition` | Defines metric metadata and limits |
| `SampleSizeCalculator` | Calculates required observations |
| `ExperimentSimulator` | Generates synthetic user-level observations |
| `ExperimentAnalyzer` | Performs metric and statistical calculations |
| `ExperimentEvaluator` | Applies experiment decision policies |
| `EvaluationReport` | Stores the final evaluation |

### Important implementation decisions

Dataclasses provide structured experiment configuration and result objects.

Enums prevent arbitrary metric classifications and decision labels.

Dictionaries organize user observations by experiment variant.

Lists preserve individual revenue and latency measurements.

SHA-256 assignment makes participant allocation reproducible.

The standard library supplies random-number generation, statistics, hashing, and numerical calculations.

The script includes assertions for sample-size calculation, deterministic assignment, conversion calculations, and invalid input handling.

### Execution

Requirements:

- Python 3.10 or later.
- No external dependencies.

Run:

`python experiment_metrics.py`

The script executes validation tests, calculates the required sample size, generates a synthetic experiment, evaluates the results, and prints a decision report.

## 10. JavaScript Implementation

File: `experiment_metrics.js`

The JavaScript implementation provides an event-driven architecture suitable for application services and asynchronous experiment workflows.

### Architecture

| Component | Responsibility |
|---|---|
| `Experiment` | Validates experiment configuration and lifecycle |
| `MetricRegistry` | Maintains registered metric definitions |
| `TrafficAllocator` | Assigns participants to variants |
| `SampleSizeService` | Calculates sample requirements |
| `StatisticalTests` | Evaluates proportions and continuous metrics |
| `ExperimentEventBus` | Publishes lifecycle and evaluation events |
| `ExperimentEvaluator` | Applies measurement policies |
| `ExperimentService` | Coordinates experiment execution |

### Event-driven workflow

The service publishes:

- `experiment.started`
- `experiment.evaluated`

Event listeners receive structured event payloads.

This design separates lifecycle coordination from monitoring and reporting.

JavaScript private fields protect the internal metric registry.

`Map` supports efficient metric lookup.

`Object.freeze` prevents accidental modification of returned configuration and report objects at the top level.

Promises and asynchronous execution are supported by the executable entry point.

The implementation uses Node.js built-in cryptography and event-emitter facilities without npm dependencies.

### Execution

Requirements:

- Node.js 18 or later.
- No third-party packages.

Run:

`node experiment_metrics.js`

## 11. C++17 Implementation

File: `experiment_metrics.cpp`

The C++ implementation focuses on a strongly typed governance and evaluation engine.

### Architecture

| Component | Responsibility |
|---|---|
| `ExperimentConfig` | Validates experiment parameters |
| `MetricDefinition` | Defines metric classification |
| `ExperimentGroup` | Aggregates participant observations |
| `TrafficAllocator` | Deterministic variant assignment |
| `SampleSizeCalculator` | Statistical planning |
| `StatisticalAnalyzer` | Statistical calculations |
| `ExperimentSimulator` | Generates synthetic data |
| `GovernanceEngine` | Applies deployment conditions |
| `ExperimentLifecycle` | Controls experiment state transitions |

### Important implementation decisions

STL vectors store individual observations.

Enums represent metric types, lifecycle states, and decisions.

Structures separate user-level observations from aggregate experiment results.

The simulator uses the standard random-number facilities in C++.

The governance engine receives an explicit evaluation policy instead of relying on hidden global settings.

Exceptions handle invalid experiment configurations, insufficient observations, and illegal state transitions.

The simulation uses a seeded random generator to provide reproducible execution.

### Execution

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic experiment_metrics.cpp -o experiment_metrics`

Run:

`./experiment_metrics`

On Windows:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic experiment_metrics.cpp -o experiment_metrics.exe`

`experiment_metrics.exe`

## 12. Java 17 Implementation

File: `ExperimentMetrics.java`

The Java implementation uses an enterprise-oriented domain model with explicit configuration, lifecycle, policy, and evaluation services.

### Architecture

| Component | Responsibility |
|---|---|
| `ExperimentConfig` | Immutable experiment configuration |
| `MetricDefinition` | Immutable metric definition |
| `EvaluationPolicy` | Defines business and operational thresholds |
| `ExperimentLifecycle` | Enforces valid state transitions |
| `MetricRegistry` | Maintains metric definitions |
| `TrafficAllocator` | Stable participant allocation |
| `SampleSizeCalculator` | Calculates required sample size |
| `ExperimentGroup` | Manages participant observations |
| `Simulator` | Generates reproducible experiment data |
| `StatisticalAnalyzer` | Performs statistical calculations |
| `EvaluationService` | Produces the final experiment decision |

### Enterprise design characteristics

Java records represent immutable domain values.

Collections maintain experiment groups and metric definitions.

Streams support filtering, aggregation, and reporting.

The lifecycle service rejects invalid state transitions.

The evaluation policy separates configurable thresholds from statistical implementation.

Custom exceptions distinguish invalid experiment data from general runtime failures.

The Java implementation is designed to demonstrate how an experiment evaluation service can be organized around explicit domain responsibilities.

### Execution

Requirements:

- Java 17.
- No external dependencies.

Compile:

`javac ExperimentMetrics.java`

Run:

`java ExperimentMetrics`

## 13. PostgreSQL Implementation

File: `experiment_metrics.sql`

The database implementation models experiment configuration, participant assignment, metric observations, evaluation history, and audit information.

### Relational model

experiments
    |
    +---- metric_definitions
    |
    +---- experiment_variants
    |          |
    |          +---- experiment_assignments
    |                       |
    |                       +---- metric_observations
    |
    +---- experiment_evaluations
    |
    +---- experiment_audit_log

### Main tables

| Table | Purpose |
|---|---|
| `experiments` | Stores experiment configuration and lifecycle |
| `metric_definitions` | Defines primary, secondary, and guardrail metrics |
| `experiment_variants` | Stores control and treatment variants |
| `experiment_assignments` | Stores participant allocation |
| `metric_observations` | Stores user-level metric measurements |
| `experiment_evaluations` | Stores experiment decisions and statistical results |
| `experiment_audit_log` | Records lifecycle changes |

### Integrity enforcement

Primary keys identify records.

Foreign keys maintain relationships between experiments, metrics, assignments, and observations.

Unique constraints prevent duplicate participant assignments and duplicate observations for the same metric and participant.

Check constraints validate numerical ranges and thresholds.

A partial unique index enforces one primary metric per experiment.

Triggers enforce experiment lifecycle transitions and validate observation values.

The audit trigger records status changes.

### Sample-size planning

`calculate_sample_size` calculates the required number of participants per group.

`plan_experiment` stores the calculated requirement.

`start_experiment` validates metric configuration and variant allocation before starting the experiment.

### Assignment

`assign_experiment_variant` uses deterministic SHA-256-based allocation and prevents duplicate assignment.

The database function returns an existing assignment when the participant has already been assigned.

### Reporting

The following views provide analytical access:

- `v_experiment_metric_summary`
- `v_sample_size_progress`
- `v_guardrail_evaluation`

These views support metric aggregation, sample-size monitoring, and operational constraint evaluation.

### Statistical analysis boundary

PostgreSQL stores observations and evaluation results.

The example deliberately does not treat an ordinary SQL average as a statistical significance test.

A validated statistical analysis service should calculate the p-value and confidence intervals before the results are stored in `experiment_evaluations`.

### Execution

Requirements:

- PostgreSQL 14 or later.
- `pgcrypto` extension.

Execute:

`psql -U postgres -d experiment_db -f experiment_metrics.sql`

The script creates its schema, types, tables, indexes, functions, procedures, triggers, views, and demonstration records.

## 14. Edge Cases and Failure Handling

The implementations address several common experiment failures.

| Failure condition | Expected handling |
|---|---|
| Empty experiment name | Reject configuration |
| Baseline conversion outside valid range | Reject configuration |
| Invalid MDE | Reject sample-size calculation |
| Invalid alpha | Reject statistical configuration |
| Invalid power | Reject statistical configuration |
| Treatment conversion reaches or exceeds 100% | Reject experiment configuration |
| Zero sample size | Reject evaluation |
| Conversions exceed assigned users | Reject observations |
| Duplicate metric registration | Reject registration |
| Duplicate participant assignment | Prevent duplicate database assignment |
| Missing primary metric | Prevent experiment activation |
| Incorrect lifecycle transition | Reject transition |
| Missing guardrail data | Require explicit data-quality handling |
| Guardrail failure | Do not ship |
| Insufficient sample | Inconclusive |

A production implementation should distinguish between a genuine zero metric value and missing observations.

For example, an absent latency measurement should not automatically be interpreted as zero latency.

Missingness can itself be a source of experiment bias.

## 15. Performance Considerations

### Participant allocation

Hash-based assignment requires constant-time work per participant.

The participant assignment table uses a composite uniqueness condition on experiment and participant identity.

### Metric retrieval

The PostgreSQL index on experiment, metric, and observation time supports common analytical filters.

The assignment index supports variant-based aggregation.

### Aggregation

For \(N\) observations:

- Counting is approximately \(O(N)\).
- Mean calculation is \(O(N)\).
- Variance calculation is \(O(N)\).
- Exact percentile calculation generally requires sorting, approximately \(O(N\log N)\).

For very large experiments, approximate quantile algorithms can reduce memory and computational requirements.

### Memory management

The Python, JavaScript, C++, and Java demonstrations retain observations in memory.

A production measurement pipeline should process events incrementally or use an analytical storage system when experiment volume exceeds application memory limits.

## 16. Security and Data Governance

Experiment metrics frequently involve participant identifiers, product behavior, payment activity, and operational telemetry.

A production deployment should enforce:

- Pseudonymization of participant identifiers.
- Access control for experiment configuration.
- Restricted access to raw user-level observations.
- Encryption in transit and at rest.
- Retention and deletion policies.
- Audit logging of experiment decisions.
- Protection against unauthorized metric modification.
- Validation of incoming measurement events.
- Separation of experiment configuration and reporting permissions.
- Protection against duplicate and replayed events.

Participant identifiers should not be treated as anonymous merely because they are hashed.

A stable hash of a predictable identifier can remain linkable to an individual.

The PostgreSQL demonstration uses database constraints and audit logging but does not establish a complete production authorization model. Database roles, row-level security, backup protection, and controlled administrative privileges must be configured separately.

## 17. Important Statistical Limitations

The implementations are educational statistical engines, not complete experimentation platforms.

Several assumptions require attention before operational use.

### Independent observations

The sample-size and significance calculations assume independent observations.

Repeated measurements from the same user can violate this assumption.

### Randomization quality

Hash-based assignment provides stable allocation, but assignment balance should be checked against important pre-experiment characteristics.

### Multiple testing

Testing many secondary metrics increases the probability of false-positive findings.

A production analysis should define a multiple-comparison strategy, such as Holm correction or a predefined false-discovery-rate procedure.

### Repeated significance testing

Repeatedly checking p-values and stopping as soon as significance appears can inflate the Type I error rate.

Sequential experiments require an appropriate sequential testing framework.

### Novelty and seasonality

User behavior may change because of novelty effects, weekday patterns, promotions, or seasonal conditions.

Experiment duration and participant exposure should account for these effects.

### Sample ratio mismatch

The observed control-to-treatment assignment ratio should be compared with the expected allocation ratio.

Unexpected imbalance may indicate allocation errors, identity problems, filtering issues, or instrumentation failures.

### Metric quality

A statistically significant metric can still be misleading when event definitions, attribution windows, or data collection are inconsistent.

Metric definitions should remain stable throughout an experiment.

## 18. Unified Experiment Workflow

The complete workflow implemented across the five source files is:

1. Define the experiment objective.
2. Select one primary metric.
3. Define secondary metrics.
4. Establish guardrail thresholds.
5. Specify the baseline conversion rate.
6. Set the minimum detectable effect.
7. Choose alpha and statistical power.
8. Calculate the required sample size.
9. Register control and treatment variants.
10. Start the experiment.
11. Assign participants consistently.
12. Collect user-level observations.
13. Validate observation quality.
14. Calculate primary and secondary outcomes.
15. Evaluate guardrail conditions.
16. Check sample-size sufficiency.
17. Calculate statistical significance.
18. Apply the predefined decision policy.
19. Record the final decision.
20. Preserve evaluation and audit information.

The resulting decision should be based on the combination of experimental design, observed effects, statistical evidence, data quality, and operational constraints.
