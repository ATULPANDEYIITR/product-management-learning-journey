# A/B Testing: Randomization, Control Groups, Treatment Groups and Statistical Significance

## 1. Introduction

A/B testing is a controlled experimentation method used to determine whether a change in a product, service, interface, process, or business decision produces a measurable difference in an outcome.

An experiment compares two or more groups exposed to different conditions.

The standard two-group experiment contains:

- **Control group:** Participants exposed to the existing experience or baseline condition.
- **Treatment group:** Participants exposed to the proposed change.
- **Randomization:** Assignment of participants to groups using a random allocation mechanism.
- **Outcome metric:** A measurable variable used to evaluate the experiment.
- **Statistical significance:** Evidence against a specified statistical null hypothesis.
- **Practical significance:** Whether the observed effect is sufficiently large to matter operationally or commercially.

A representative experiment is an e-commerce checkout optimization.

The existing checkout interface is the control. A redesigned checkout interface is the treatment. The primary metric is the proportion of eligible participants completing a purchase.

The purpose is not simply to identify which group has a higher observed conversion rate. The purpose is to estimate the treatment effect while accounting for sampling variability and experimental design.

## 2. Conceptual Architecture

The experiment follows this relationship:

    Experiment Configuration
             |
             v
       Define Hypothesis
             |
             v
       Define Population
             |
             v
          Randomize
             |
        +----+----+
        |         |
        v         v
      Control  Treatment
        |         |
        v         v
      Observe   Observe
        |         |
        +----+----+
             |
             v
       Measure Outcomes
             |
             v
      Calculate Effect
             |
             v
       Statistical Test
             |
             v
      Practical Evaluation
             |
             v
       Experiment Decision

Each component has a separate responsibility. Randomization controls assignment, group definitions establish experimental conditions, outcome measurement captures observed behavior, and statistical analysis evaluates the evidence.

## 3. Experimental Hypothesis

An experiment should begin with a specific, testable hypothesis.

Example:

"The redesigned checkout button increases the purchase conversion rate compared with the existing checkout button."

The hypothesis should identify:

- The population being studied.
- The intervention being tested.
- The primary outcome.
- The comparison condition.
- The expected direction of the effect.
- The minimum effect that would justify implementation.

### 3.1 Null hypothesis

The null hypothesis states that the control and treatment conversion probabilities are equal.

\[
H_0:p_T=p_C
\]

Where:

- \(p_T\) is the treatment conversion probability.
- \(p_C\) is the control conversion probability.

### 3.2 Alternative hypothesis

For a two-sided experiment:

\[
H_1:p_T\neq p_C
\]

This allows the experiment to identify improvement or deterioration.

A directional hypothesis can also be specified when the experimental design and analysis justify a one-sided test. The implementations use a two-sided test.

## 4. Randomization

Randomization is the process of assigning eligible experimental units to groups using a probability-based mechanism.

It reduces systematic differences between groups and supports valid statistical comparisons.

For example, consider 10,000 eligible users.

With equal allocation:

\[
P(C)=0.5
\]

\[
P(T)=0.5
\]

The expected allocation is:

| Group | Allocation | Expected participants |
|---|---:|---:|
| Control | 50% | 5,000 |
| Treatment | 50% | 5,000 |

Actual group sizes may differ because random allocation does not guarantee perfectly equal counts.

### 4.1 Independent randomization

Each eligible participant is independently assigned to a group.

The Python and C++ implementations use seeded pseudorandom number generators.

The Java implementation separates assignment logic into an `AssignmentPolicy` interface, allowing different randomization strategies.

### 4.2 Deterministic assignment

In distributed systems, independently assigning a returning participant on every request can result in inconsistent experiences.

A deterministic assignment mechanism can use a keyed hash of:

- Experiment identifier.
- Participant identifier.
- Assignment secret.

The JavaScript implementation uses HMAC-SHA256 to derive a stable assignment bucket.

This is useful for consistent participant allocation across multiple application servers.

The secret must be protected. The hash should not be treated as a substitute for access control or participant privacy.

### 4.3 Stratified randomization

Simple randomization can produce imbalances in small samples.

Stratified randomization divides participants into meaningful categories before random assignment.

For example:

- Geographic region.
- Device category.
- Customer segment.
- Subscription type.

Each category receives its own allocation process.

This can improve balance on important baseline characteristics.

Stratification must be defined before examining experimental outcomes.

### 4.4 Allocation integrity

An experimental assignment should remain stable.

A participant must not receive the control experience on one request and the treatment experience on another unless the experiment explicitly uses a crossover design.

The implementations prevent duplicate assignment within an experiment.

The PostgreSQL schema enforces this using:

`UNIQUE (experiment_id, participant_id)`

This database constraint protects assignment integrity even when multiple application processes operate concurrently.

## 5. Control Group

The control group represents the comparison condition.

It generally receives:

- The existing product interface.
- The current business process.
- The existing service configuration.
- A baseline policy or intervention.

Example:

An online retailer currently uses a standard checkout button.

The control group continues using this interface throughout the experiment.

The control group establishes the reference conversion rate.

\[
p_C=\frac{x_C}{n_C}
\]

Where:

- \(x_C\) is the number of control conversions.
- \(n_C\) is the number of observed control participants.

If 500 out of 5,000 control participants purchase:

\[
p_C=\frac{500}{5000}=0.10
\]

The control conversion rate is 10%.

The control condition must remain consistent throughout the experiment. Unplanned changes to the control experience can compromise interpretation.

## 6. Treatment Group

The treatment group receives the intervention being evaluated.

Examples include:

- A redesigned checkout interface.
- A different pricing presentation.
- A modified recommendation algorithm.
- A revised notification policy.
- A different onboarding workflow.

The treatment conversion rate is:

\[
p_T=\frac{x_T}{n_T}
\]

If 600 out of 5,000 treatment participants purchase:

\[
p_T=\frac{600}{5000}=0.12
\]

The treatment conversion rate is 12%.

The treatment group must differ from the control group only in the intended experimental intervention, apart from unavoidable random variation.

Uncontrolled differences can introduce confounding effects.

## 7. Conversion Rate and Treatment Effect

The conversion rate is a proportion of eligible participants who achieve a defined outcome.

\[
CR=\frac{\text{Conversions}}{\text{Observed Participants}}
\]

For a binary conversion metric, each participant contributes one outcome:

- Converted.
- Not converted.

### 7.1 Absolute lift

Absolute lift is the difference between the treatment and control conversion rates.

\[
L_{absolute}=p_T-p_C
\]

For the example:

\[
L_{absolute}=0.12-0.10=0.02
\]

The absolute improvement is 2 percentage points.

### 7.2 Relative lift

Relative lift expresses the improvement relative to the control rate.

\[
L_{relative}=
\frac{p_T-p_C}{p_C}
\]

\[
L_{relative}=
\frac{0.12-0.10}{0.10}=0.20
\]

The relative lift is 20%.

These measurements are different.

A change from 10% to 12% represents:

- 2 percentage points of absolute lift.
- 20% relative lift.

Reporting only relative lift can exaggerate the perceived scale of a change.

When the control conversion rate is zero, relative lift is undefined.

## 8. Statistical Significance

Statistical significance evaluates whether the observed difference is sufficiently inconsistent with the null hypothesis under the selected statistical model.

For two independent proportions, a two-proportion z-test can be used when the sample-size conditions for the normal approximation are appropriate.

### 8.1 Pooled conversion rate

Under the null hypothesis, both groups are assumed to have the same conversion probability.

The pooled estimate is:

\[
\hat p=
\frac{x_C+x_T}{n_C+n_T}
\]

Where:

- \(x_C\) is control conversions.
- \(x_T\) is treatment conversions.
- \(n_C\) is control sample size.
- \(n_T\) is treatment sample size.

### 8.2 Standard error under the null hypothesis

\[
SE_0=
\sqrt{
\hat p(1-\hat p)
\left(
\frac{1}{n_C}+\frac{1}{n_T}
\right)
}
\]

### 8.3 Z-statistic

\[
Z=\frac{p_T-p_C}{SE_0}
\]

A large absolute z-statistic indicates that the observed difference is relatively far from zero under the null model.

### 8.4 P-value

For a two-sided test:

\[
p\text{-value}=2P(Z\geq |z|)
\]

The p-value represents the probability, assuming the null hypothesis and statistical model are correct, of observing a test statistic at least as extreme as the one obtained.

It does not represent:

- The probability that the null hypothesis is true.
- The probability that the treatment is successful.
- The probability that the observed effect will persist.
- The probability that the result is commercially valuable.

### 8.5 Significance threshold

The significance level is commonly denoted by \(\alpha\).

The implementations use:

\[
\alpha=0.05
\]

The conventional decision rule is:

| Condition | Interpretation |
|---|---|
| p-value below 0.05 | Reject the null hypothesis |
| p-value equal to or above 0.05 | Fail to reject the null hypothesis |

Failing to reject the null hypothesis does not establish that both treatments are equivalent.

A sufficiently powered equivalence or non-inferiority design is needed when that is the actual research question.

## 9. Confidence Intervals

A confidence interval provides an estimated range for the treatment effect.

For the difference between independent proportions, an approximate unpooled standard error is:

\[
SE_D=
\sqrt{
\frac{p_C(1-p_C)}{n_C}
+
\frac{p_T(1-p_T)}{n_T}
}
\]

The approximate 95% confidence interval is:

\[
(p_T-p_C)\pm1.96SE_D
\]

A confidence interval that excludes zero is consistent with statistical significance at the corresponding two-sided 5% level under the normal approximation.

The confidence interval communicates both the estimated effect and its uncertainty.

The Python, JavaScript, C++, and Java implementations calculate this interval using the normal approximation.

For small samples or rare conversion events, exact methods, score-based intervals, or other suitable statistical procedures may be preferable.

## 10. Statistical Significance Versus Practical Significance

These concepts must not be treated as interchangeable.

**Statistical significance** evaluates evidence against a statistical null hypothesis.

**Practical significance** evaluates whether the magnitude of the effect matters in the real application.

Consider two experiments:

| Experiment | Control | Treatment | Absolute lift |
|---|---:|---:|---:|
| A | 10.00% | 10.10% | 0.10 percentage points |
| B | 10.00% | 12.00% | 2.00 percentage points |

Experiment A may achieve statistical significance with a sufficiently large sample.

Its business value may still be negligible.

Experiment B may have a larger operational impact, depending on costs, revenue, implementation complexity, and risk.

The implementations introduce a minimum detectable effect or practical-effect threshold.

A treatment is classified as a practical winner only when:

1. The statistical test meets the selected significance threshold.
2. The observed absolute improvement meets the minimum practical threshold.
3. The required sample-size policy is satisfied.

A real production decision should also account for uncertainty, costs, guardrails, and operational constraints.

## 11. Sample-Size Planning

Sample-size planning determines how many participants are required before the experiment begins.

The required sample depends on:

- Baseline conversion rate.
- Minimum detectable effect.
- Significance level.
- Statistical power.
- Allocation ratio.
- Statistical test.

Statistical power is the probability of rejecting the null hypothesis when a specified alternative effect actually exists.

A common target is 80% power.

For equal-sized groups, a normal-approximation sample-size calculation is:

\[
n=
\frac{
\left[
z_{1-\alpha/2}
\sqrt{2\bar p(1-\bar p)}
+
z_{1-\beta}
\sqrt{
p_C(1-p_C)+p_T(1-p_T)
}
\right]^2
}{
(p_T-p_C)^2
}
\]

Where:

\[
\bar p=\frac{p_C+p_T}{2}
\]

And:

- \(\alpha\) is the significance level.
- \(1-\beta\) is statistical power.
- \(p_C\) is the baseline conversion rate.
- \(p_T\) is the expected treatment conversion rate.

The four implementations provide sample-size planning functions using this approximation.

The result is the approximate number of participants required in each group under equal allocation.

The calculation does not account automatically for participant attrition, repeated observations, clustering, multiple comparisons, or unequal allocation. These factors may require a larger sample or a different design.

## 12. Experiment Lifecycle

A controlled experiment should have explicit lifecycle states.

| State | Meaning |
|---|---|
| Draft | Configuration is being prepared |
| Running | Participants can be assigned and outcomes recorded |
| Completed | The experiment has reached its planned completion |
| Stopped | The experiment has been terminated before normal completion |

The normal lifecycle is:

    DRAFT
      |
      v
    RUNNING
      |
      +----------+
      |          |
      v          v
  COMPLETED    STOPPED

The implementations reject invalid state transitions.

For example, a completed experiment cannot be started again through the normal lifecycle.

The PostgreSQL triggers enforce lifecycle integrity at the database level.

A production experiment platform should separately record the reason for stopping, the operator, and the time of the intervention.

## 13. Implementation Architecture

### 13.1 Python: Experiment simulation and statistical analysis

The Python implementation provides a complete experimental simulation.

Important components:

| Component | Responsibility |
|---|---|
| `ExperimentConfig` | Stores experiment parameters |
| `Experiment` | Manages experiment state and participants |
| `Participant` | Represents an experimental unit |
| `GroupStatistics` | Stores group-level observations |
| `two_proportion_test()` | Calculates z-statistics and p-values |
| `confidence_interval()` | Estimates uncertainty in treatment lift |
| `required_sample_size()` | Plans experiment sample size |
| `ExperimentReport` | Produces structured evaluation output |

Python-specific design decisions include:

- Dataclasses for structured records.
- Enums for group and lifecycle definitions.
- Sets for duplicate participant detection.
- Seeded random-number generation for repeatable demonstrations.
- Type annotations for clearer interfaces.
- Exceptions for invalid configurations and operations.
- JSON export for experiment reporting.

The implementation stores participant outcomes in memory and calculates statistics from the recorded observations.

It is appropriate for educational simulations and small experiments, not a distributed production assignment service.

### 13.2 JavaScript: Event-driven experiment management

The JavaScript implementation focuses on an event-driven experiment engine.

It uses Node.js capabilities to separate experiment execution from reporting.

Important components:

| Component | Responsibility |
|---|---|
| `Experiment` | Owns experiment state |
| `EventEmitter` | Publishes lifecycle and measurement events |
| `Map` | Maintains participant assignments and outcomes |
| `crypto` | Provides stable HMAC-based assignment |
| `calculateStatistics()` | Evaluates the two-group comparison |
| `calculateRequiredSampleSize()` | Performs sample planning |
| `exportReport()` | Writes a structured JSON report |

Events include:

- `started`
- `assigned`
- `outcome`
- `evaluated`
- `completed`
- `stopped`

The separation between assignment and outcome measurement is important.

An assigned participant is not automatically equivalent to an observed participant.

This distinction helps identify missing exposure or outcome data.

The implementation uses asynchronous file writing with exclusive file creation to avoid accidentally replacing an existing report.

The HMAC assignment strategy is useful when multiple application servers must consistently assign returning participants.

The demonstration uses an in-memory store. A distributed deployment would require durable storage and concurrency controls.

### 13.3 C++17: Statistical and policy evaluation engine

The C++ implementation emphasizes computational structure and explicit governance rules.

Important components:

| Component | Responsibility |
|---|---|
| `Participant` | Represents an experimental participant |
| `GroupMetrics` | Maintains aggregate conversion statistics |
| `GovernancePolicy` | Defines significance and minimum sample rules |
| `Randomizer` | Assigns participants and generates outcomes |
| `ABTestEngine` | Manages the experiment |
| `StatisticalResult` | Stores statistical evaluation |

The implementation uses:

- `std::vector` for participant records.
- `std::unordered_set` for duplicate detection.
- `std::mt19937_64` for seeded pseudorandom generation.
- `std::bernoulli_distribution` for binary random outcomes.
- `std::erfc` for normal-tail probability calculations.
- Exceptions for invalid state and data.

The engine maintains group-level aggregate statistics while recording participant information.

This avoids repeatedly scanning every participant to calculate conversion counts.

The average assignment and update operations are expected to be constant-time for the hash-based membership check, while the complete statistical evaluation uses the maintained aggregate values.

### 13.4 Java 17: Enterprise experiment service

The Java implementation models experiment management through explicit domain types and service boundaries.

Important components:

| Component | Responsibility |
|---|---|
| `ExperimentConfig` | Immutable configuration record |
| `Participant` | Assignment record |
| `Outcome` | Conversion and revenue measurement |
| `GroupMetrics` | Aggregated group results |
| `AssignmentPolicy` | Randomization interface |
| `RandomAssignmentPolicy` | Concrete assignment strategy |
| `ExperimentService` | Experiment lifecycle and operations |
| `ExperimentReport` | Immutable evaluation output |

Java-specific design decisions include:

- Records for immutable domain data.
- Interfaces for replaceable assignment strategies.
- Enums for controlled domain states.
- Collections for assignment and outcome management.
- Synchronized methods for thread-safe operations within one service instance.
- Custom exceptions for validation and workflow failures.
- Separate statistical and business decision logic.

The implementation also captures revenue to illustrate a secondary business outcome.

The primary statistical test remains a binary conversion comparison. Revenue is reported separately and is not automatically treated as statistically significant.

Synchronization protects operations within a single JVM instance. It does not provide distributed locking or transaction guarantees across multiple application instances.

### 13.5 PostgreSQL: Relational experiment management

The PostgreSQL implementation provides persistent storage and database-enforced integrity.

The schema contains the following entities:

| Table | Purpose |
|---|---|
| `experiments` | Experiment configuration and lifecycle |
| `experiment_groups` | Control and treatment definitions |
| `participants` | Participant identities |
| `assignments` | Participant-to-experiment allocation |
| `exposure_events` | Records exposure to experimental conditions |
| `conversion_outcomes` | Stores conversion and revenue observations |
| `guardrail_measurements` | Stores operational metrics |
| `experiment_evaluations` | Stores statistical decisions |

The principal relationship is:

    experiments
        |
        v
    experiment_groups
        |
        v
    assignments
        |
        +-------------------+
        |                   |
        v                   v
    exposure_events   conversion_outcomes
                            |
                            v
                    experiment_evaluations

Participants can participate in multiple experiments, but the unique assignment constraint prevents duplicate assignment within the same experiment.

The group-membership trigger prevents an assignment from referencing a group belonging to a different experiment.

The outcome trigger validates the experiment lifecycle and prevents conversion timestamps from preceding participant assignment.

The evaluation function calculates:

- Control conversion rate.
- Treatment conversion rate.
- Absolute lift.
- Relative lift.
- Pooled standard error.
- Z-statistic.
- Two-sided p-value.
- Approximate confidence interval.
- Statistical significance.
- Practical significance.
- Experiment decision.

The script also demonstrates:

- Stored procedures.
- Database functions.
- Transaction boundaries.
- Referential integrity.
- Unique and check constraints.
- Reporting views.
- Aggregation.
- Conditional validation.
- Indexing.
- Failure handling.

The demonstration data is synthetic. It is intended to exercise the database workflow, not to establish an empirical treatment effect.

## 14. Exposure and Outcome Measurement

A critical experimental distinction is the difference between assignment and exposure.

**Assignment** records which group a participant belongs to.

**Exposure** records whether the participant actually encountered the assigned experience.

**Outcome measurement** records the participant's response after exposure.

These events should not be treated as interchangeable.

For example:

A customer may be assigned to the treatment group but never visit the checkout page.

That customer has an assignment but no checkout exposure.

A customer may encounter the redesigned checkout but fail to complete a purchase.

That customer has an exposure and a valid non-conversion outcome.

The PostgreSQL implementation separates assignments, exposure events, and conversion outcomes.

The application implementations also distinguish assigned participants from participants with recorded outcomes.

For a real experiment, the primary analysis should define the eligible population and outcome window in advance. An intention-to-treat analysis generally evaluates participants according to their original randomized assignment rather than excluding them based on post-randomization behavior.

## 15. Guardrail Metrics

Optimizing one metric can damage another.

A checkout redesign may improve conversion but increase page latency or payment errors.

Guardrail metrics identify these negative effects.

Common examples include:

| Guardrail | What it measures |
|---|---|
| Page latency | Application response performance |
| Error rate | Technical reliability |
| Refund rate | Post-purchase quality |
| Cancellation rate | Customer dissatisfaction |
| Average order value | Revenue quality |
| Customer complaints | Service impact |

A treatment should not be adopted solely because it increases conversion.

The decision must also account for operational safety and secondary business outcomes.

The JavaScript implementation records latency measurements.

The Java implementation records revenue.

The PostgreSQL implementation stores general guardrail measurements and demonstrates average and percentile reporting.

These examples demonstrate measurement infrastructure. They do not implement formal statistical tests for every guardrail.

Each guardrail requires an appropriate metric definition, threshold, analysis method, and decision rule.

## 16. Randomization Quality and Sample Ratio Mismatch

Randomization should produce group proportions reasonably consistent with the planned allocation.

For equal allocation, the expected ratio is 50:50.

An observed distribution such as 70:30 may indicate a problem.

Potential causes include:

- Incorrect assignment logic.
- Unequal participant eligibility.
- Duplicate exposure events.
- Missing assignment records.
- Participant filtering.
- Instrumentation errors.
- Incorrect experiment configuration.

This issue is commonly described as sample ratio mismatch.

It should be investigated before interpreting treatment outcomes.

The PostgreSQL reporting queries compare expected allocation with actual participant allocation.

A formal sample ratio mismatch test can use a chi-square goodness-of-fit test:

\[
\chi^2=
\sum_i
\frac{(O_i-E_i)^2}{E_i}
\]

Where:

- \(O_i\) represents observed group counts.
- \(E_i\) represents expected group counts.

A significant mismatch may indicate an implementation or data-quality problem.

It does not, by itself, identify the underlying cause.

## 17. Experimental Bias and Failure Conditions

Reliable experimental interpretation requires more than a statistically significant p-value.

### Selection bias

Occurs when participants enter groups through a process related to their characteristics or expected outcomes.

Random assignment helps reduce this problem.

### Selection after randomization

Removing participants based on their observed behavior can destroy the original comparability between groups.

Eligibility and exclusion criteria should be defined before examining results.

### Instrumentation bias

Occurs when conversion events are recorded differently across groups.

For example, the treatment interface may emit a conversion event twice.

### Novelty effects

Participants may initially respond differently to a new interface because it is unfamiliar.

Longer observation may be necessary to understand sustained effects.

### Contamination

Occurs when participants receive elements of both experimental conditions.

For example, a user may encounter a treatment experience on one device and a control experience on another.

### Time-related confounding

A promotion, holiday, pricing change, or external event can affect outcomes if experimental conditions are not administered concurrently.

### Attrition

Occurs when outcome measurements are missing for some participants.

Missing outcomes must be investigated rather than automatically interpreted as non-conversions.

### Repeated testing

Repeatedly evaluating the same experiment and stopping when the p-value becomes significant can increase the false-positive rate.

A fixed-horizon analysis should use a predetermined sample size and stopping rule.

Sequential experimentation requires an appropriate sequential statistical procedure.

## 18. Multiple Comparisons

Testing many variations or many metrics increases the probability of finding at least one apparently significant result by chance.

For example, testing 20 independent hypotheses at a 5% significance level produces a higher family-wise probability of at least one false-positive result than testing a single hypothesis.

Possible corrections include:

- Bonferroni correction.
- Holm correction.
- False discovery rate procedures.

The correct procedure depends on the experimental objectives and the relationship between the hypotheses.

Primary metrics should be distinguished from exploratory metrics.

The implementations perform one primary two-group conversion comparison. They do not automatically correct for multiple testing.

## 19. Performance and Scalability

Experiment management systems should separate assignment, measurement, and analysis.

### Assignment performance

Assignment is a frequent operation and should have low latency.

Hash-based assignment allows stable participant allocation without repeatedly querying random assignment state.

### Storage performance

A relational implementation should index:

- Experiment identifiers.
- Group identifiers.
- Participant identifiers.
- Outcome timestamps.
- Metric names.

The PostgreSQL schema includes indexes for common reporting and retrieval patterns.

### Statistical processing

Aggregate statistics are generally more efficient than repeatedly retrieving and processing individual participant records.

For very large experiments, analytical queries can be performed on partitioned or aggregated datasets.

### Concurrency

Concurrent assignment requests must not create multiple assignments for the same participant.

The database unique constraint provides an important integrity guarantee.

Application-level checks alone are insufficient because simultaneous requests can both pass an initial existence check.

### Data retention

Participant identifiers and experimental observations should be protected through:

- Access restrictions.
- Pseudonymization.
- Encryption.
- Retention policies.
- Audit logging.
- Data minimization.

Experimental datasets should not expose personally identifiable information in ordinary reports.

## 20. Security and Governance

A production experimentation platform should apply appropriate access controls.

Relevant roles include:

| Role | Responsibility |
|---|---|
| Experiment owner | Defines experiment objectives |
| Developer | Implements experimental variations |
| Analyst | Validates metrics and statistical results |
| Reviewer | Checks experiment design |
| Administrator | Controls platform configuration |

Important governance controls include:

- Authorization before starting or modifying experiments.
- Immutable records of assignment decisions.
- Auditable configuration changes.
- Restricted access to participant data.
- Controlled experiment completion.
- Reproducible statistical analysis.
- Explicit stopping conditions.
- Protection of deterministic assignment secrets.

The supplied implementations provide basic lifecycle and data-integrity controls. They are not a complete identity-management, authorization, or audit platform.

## 21. Reproducibility

Reproducibility means that an experiment's configuration, assignment procedure, data definitions, and analysis decisions can be examined and independently checked.

Important records include:

- Experiment identifier.
- Hypothesis.
- Primary metric.
- Eligibility criteria.
- Assignment ratio.
- Randomization method.
- Statistical significance threshold.
- Minimum detectable effect.
- Statistical power.
- Start and end timestamps.
- Data extraction time.
- Analysis version.
- Final decision.

Seeded random generators make the demonstrations repeatable under the same execution environment and random-number sequence.

A production experiment must also preserve the actual assignment records and measurement definitions. A random seed alone is not sufficient to reproduce an experiment when participant ordering or concurrent processing changes.

## 22. Limitations of the Statistical Implementations

The four source-code implementations use an approximate two-proportion z-test and normal-approximation confidence intervals.

These methods are appropriate for many sufficiently large independent binary-outcome experiments.

They have limitations:

1. Very small samples may violate normal approximation assumptions.
2. Rare conversion events may require alternative methods.
3. Clustered participants violate simple independence assumptions.
4. Repeated observations require suitable longitudinal or repeated-measures analysis.
5. Unequal allocation requires appropriate sample-size planning.
6. Missing outcomes can introduce bias.
7. Multiple metrics require multiplicity considerations.
8. Sequential monitoring requires a defined statistical procedure.

The sample-size calculations are approximate planning tools rather than guarantees of statistical power.

The demonstrations also use simulated outcomes, which should never be presented as real customer or business evidence.

## 23. Execution Requirements

### Python

- Python 3.10 or later.
- Standard library only.
- Run using the Python interpreter.
- Produces `ab_test_report.json`.

### JavaScript

- Node.js 18 or later.
- Standard library only.
- Uses `crypto`, `fs/promises`, and `events`.
- Produces `ab_test_report.json` when the destination does not already exist.

### C++17

- C++17-compatible compiler.
- Standard C++ library.
- Compile with the C++17 language standard.

### Java 17

- Java Development Kit 17.
- Standard Java APIs.
- Compile the source file as `ABTestingEnterprise.java`.

### PostgreSQL

- PostgreSQL 15 or later.
- Permission to create schemas, tables, functions, triggers, and procedures.
- Execute the SQL script in a database where the `ab_testing` schema is not already populated with incompatible objects.

The SQL demonstration uses transactions, synthetic data, and database-side randomization.

## 24. Technical Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Randomization | Seeded PRNG | HMAC assignment | Seeded PRNG | Assignment policy | Database random function |
| Group management | Lists and sets | Maps | STL containers | Collections | Relational tables |
| Experiment lifecycle | Enum | State machine | Enum | Enum | Enum and trigger |
| Duplicate prevention | Set | Map | Hash set | Map | Unique constraint |
| Outcome recording | Participant records | Separate observations | Aggregate metrics | Outcome records | Outcome table |
| Statistical test | Two-proportion z-test | Two-proportion z-test | Two-proportion z-test | Two-proportion z-test | SQL function |
| Confidence interval | Normal approximation | Normal approximation | Normal approximation | Normal approximation | Normal approximation |
| Sample planning | Implemented | Implemented | Implemented | Implemented | Not implemented |
| Guardrail measurement | Extensible | Latency | Extensible | Revenue | Dedicated table |
| Reporting | JSON | JSON | Console | Records | Views and tables |
| Persistence | JSON report | JSON report | No | No | Relational database |

## 25. Interpretation of an A/B Testing Result

A valid experiment decision requires a sequence of checks.

| Evaluation | Question |
|---|---|
| Assignment integrity | Were participants assigned correctly? |
| Exposure integrity | Did participants receive the intended experience? |
| Data quality | Were outcomes measured consistently? |
| Sample adequacy | Were the required sample sizes reached? |
| Statistical evaluation | Is there sufficient evidence against the null hypothesis? |
| Effect magnitude | Is the estimated improvement meaningful? |
| Guardrails | Did the intervention damage another important metric? |
| Operational review | Is the treatment suitable for implementation? |

A treatment conversion rate higher than the control conversion rate does not automatically establish success.

The final decision must be supported by experimental integrity, appropriate statistical evidence, meaningful effect size, and acceptable operational risk.
