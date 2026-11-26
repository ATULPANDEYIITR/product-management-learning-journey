# Experimentation: Experimental Design, Hypotheses, Control and Treatment

## 1. Experimental Research

Experimentation is a structured method of investigating whether a defined intervention causes a measurable change in an outcome.

An experiment begins with a research question, translates that question into testable hypotheses, establishes an experimental design, assigns subjects to groups, collects observations, and evaluates the resulting evidence.

A controlled experiment attempts to isolate the effect of an independent variable while controlling other factors that could influence the dependent variable.

Consider an e-commerce organization investigating whether a redesigned checkout interface increases purchase conversion.

The organization establishes two groups:

- Control: Participants receive the existing checkout interface.
- Treatment: Participants receive the redesigned checkout interface.

Both groups are measured using the same purchase-conversion definition and observation period.

The difference in their outcomes provides evidence about the intervention.

## 2. Research Questions and Hypotheses

A research question identifies the problem that an experiment intends to investigate.

A hypothesis expresses a testable prediction about the relationship between variables.

### 2.1 Research question

Example:

Does a redesigned checkout interface increase the percentage of customers who complete purchases?

A useful research question should identify:

- The population being investigated.
- The intervention being evaluated.
- The outcome being measured.
- The relevant experimental conditions.

### 2.2 Null hypothesis

The null hypothesis, denoted by H0, represents the absence of an effect or difference under the specified statistical model.

For the checkout experiment:

H0: The redesigned checkout does not change purchase conversion.

For a comparison of two population conversion proportions:

H0: pT = pC

Where:

- pT represents the treatment population conversion probability.
- pC represents the control population conversion probability.

### 2.3 Alternative hypothesis

The alternative hypothesis, denoted by H1 or Ha, represents the effect that the research intends to investigate.

For the checkout experiment:

H1: The redesigned checkout increases purchase conversion.

Mathematically:

H1: pT > pC

Hypotheses can use different directional structures.

| Hypothesis | Mathematical representation | Research purpose |
|---|---|---|
| Two-sided | pT ≠ pC | Detect any difference |
| Right-tailed | pT > pC | Detect an increase |
| Left-tailed | pT < pC | Detect a decrease |

The statistical test must be consistent with the hypothesis specified before the experiment begins.

### 2.4 Hypothesis quality

A useful hypothesis should be:

- Specific enough to be tested.
- Connected to measurable variables.
- Relevant to the research question.
- Defined before observing experimental outcomes.
- Supported by a clearly specified research design.

A hypothesis should not be rewritten after observing results merely to make an experiment appear successful.

## 3. Variables in Experimental Research

Variables represent measurable or controllable characteristics of an experiment.

| Variable | Meaning | Checkout example |
|---|---|---|
| Independent variable | Factor manipulated by the researcher | Checkout design |
| Dependent variable | Measured outcome | Purchase conversion |
| Control variables | Conditions maintained consistently | Observation period and eligibility criteria |
| Confounding variable | External factor associated with the intervention and outcome | Seasonal purchasing patterns |
| Mediating variable | Mechanism through which an intervention influences an outcome | Reduction in checkout friction |
| Moderating variable | Factor that changes the strength or direction of an effect | Mobile versus desktop usage |

### 3.1 Independent variable

The independent variable is the factor whose effect is being investigated.

In the checkout experiment, checkout design has two conditions:

- Existing interface.
- Redesigned interface.

The researcher deliberately assigns these conditions to experimental participants.

### 3.2 Dependent variable

The dependent variable represents the outcome measured after exposure to the experimental condition.

Purchase conversion can be defined as:

Conversion Rate = Number of Completed Purchases / Number of Eligible Participants

The definition must remain consistent across experimental groups.

### 3.3 Confounding variables

A confounder can produce a misleading association between an intervention and an outcome.

Examples include:

- Different participant characteristics.
- Different observation periods.
- Marketing campaigns.
- Changes in product pricing.
- Unequal exposure to the intervention.
- External economic conditions.

Randomization helps distribute both observed and unobserved participant characteristics across groups in expectation.

It does not guarantee that every possible confounder will be perfectly balanced in a particular sample.

## 4. Experimental Design

Experimental design determines how participants, treatments, measurements, and analysis procedures are organized.

A well-defined design establishes the conditions under which evidence will be collected and interpreted.

### 4.1 Core design components

| Component | Purpose |
|---|---|
| Research question | Defines the investigation |
| Hypotheses | Defines the predicted relationship |
| Population | Identifies the target group |
| Eligibility criteria | Defines participant inclusion |
| Independent variable | Specifies the intervention |
| Dependent variable | Specifies the outcome |
| Control group | Establishes the comparison condition |
| Treatment group | Receives the intervention |
| Randomization | Reduces systematic allocation bias |
| Sample size | Determines the planned number of observations |
| Measurement protocol | Standardizes data collection |
| Statistical analysis | Evaluates experimental evidence |
| Guardrails | Identify unacceptable side effects |

### 4.2 Randomized controlled experiments

A randomized controlled experiment allocates eligible participants to experimental groups using a random assignment procedure.

The allocation process should be established before outcomes are measured.

A basic workflow is:

Research Question
    |
    v
Hypothesis Formulation
    |
    v
Experimental Design
    |
    v
Participant Eligibility
    |
    v
Random Assignment
    |
    +--------------------+
    |                    |
    v                    v
Control Group       Treatment Group
    |                    |
    v                    v
Existing Design     New Intervention
    |                    |
    v                    v
Outcome Measurement and Validation
    |
    v
Statistical Analysis
    |
    v
Interpretation and Decision

Random assignment is different from random sampling.

- Random sampling concerns how subjects are selected from a population.
- Random assignment concerns how selected subjects are allocated to experimental conditions.

An experiment can use randomized assignment without having a representative random sample of the entire population.

### 4.3 Control group

The control group establishes the reference condition.

It normally receives the existing system, standard procedure, or an appropriate comparison condition.

In the checkout experiment, participants assigned to the control group use the existing checkout interface.

The control group helps establish what would have happened without the proposed intervention, subject to the assumptions and limitations of the research design.

### 4.4 Treatment group

The treatment group receives the intervention being investigated.

For the checkout experiment, participants use the redesigned interface.

The treatment should be sufficiently defined to allow consistent implementation.

Uncontrolled changes to the treatment during execution can make the experimental results difficult to interpret.

### 4.5 Randomization and allocation

Randomization reduces systematic differences between experimental groups.

Common approaches include:

- Simple randomization.
- Block randomization.
- Stratified randomization.
- Cluster randomization.

Simple randomization assigns participants independently using a random process.

Block randomization helps maintain approximate group-size balance.

Stratified randomization allocates participants within predefined categories, such as device type or geographical region.

Cluster randomization assigns groups of related subjects, such as hospitals or schools, rather than individual subjects.

The appropriate technique depends on the research question, population, operational constraints, and risk of contamination between participants.

## 5. Sample Size, Statistical Power and Effect Size

Sample size influences the precision and reliability of experimental estimates.

An experiment with too few participants may fail to detect a practically meaningful effect.

An unnecessarily large experiment may consume resources and expose more participants to an intervention than required.

### 5.1 Minimum detectable effect

The minimum detectable effect, or MDE, represents the smallest effect that the experiment is designed to detect with specified statistical power and significance level.

For example:

- Baseline conversion: 10%.
- Expected treatment conversion: 12.5%.
- Absolute expected improvement: 2.5 percentage points.

The relative improvement is:

(12.5% - 10%) / 10% = 25%

Absolute and relative effects must not be confused.

### 5.2 Statistical significance level

The significance level, denoted by alpha, specifies the probability threshold used for rejecting the null hypothesis under the assumptions of the statistical test.

A conventional choice is:

α = 0.05

This is associated with a 5% Type I error rate under the null hypothesis and the specified testing procedure.

### 5.3 Statistical power

Statistical power is the probability of rejecting the null hypothesis when a specified alternative effect is true.

Power is represented by:

Power = 1 - β

Where β is the Type II error probability.

A conventional design may use 80% or 90% statistical power.

### 5.4 Sample-size calculation

For a two-sided comparison of independent proportions, an approximate per-group sample-size calculation is:

n = [Zα/2 × √(2p̄(1-p̄)) + Zβ × √(p1(1-p1)+p2(1-p2))]² / (p2-p1)²

Where:

- n is the required sample size per group.
- p1 is the baseline conversion probability.
- p2 is the expected treatment conversion probability.
- p̄ is the average of the two proportions.
- Zα/2 is the normal critical value associated with the significance level.
- Zβ is the normal critical value associated with the desired power.

This approximation assumes independent observations and a conventional two-group proportion comparison.

Production sample-size planning may also need to account for:

- Multiple comparisons.
- Repeated measurements.
- Cluster correlation.
- Participant attrition.
- Unequal allocation.
- Noncompliance.
- Sequential testing.
- Multiple primary outcomes.

The implemented sample-size estimators use approximate normal critical values and are intended for conventional educational examples, not a replacement for a validated statistical planning procedure.

## 6. Experiment Execution and Measurement

Experiment execution converts the approved design into a controlled operational process.

The principal stages are:

1. Register the experiment.
2. Validate its hypotheses and design.
3. Define eligible participants.
4. Start the experiment.
5. Randomize participant allocation.
6. Deliver the assigned intervention.
7. Record exposure and outcomes.
8. Validate observations.
9. Evaluate primary and guardrail metrics.
10. Complete statistical analysis.
11. Record the decision and supporting evidence.

### 6.1 Intention-to-treat principle

Intention-to-treat analysis evaluates participants according to their originally assigned groups.

It preserves the randomized comparison even when some participants do not fully comply with their assigned intervention.

Excluding participants solely because they did not respond as expected can introduce selection bias.

The supplied implementations simulate assigned-group outcomes. They do not implement a complete intention-to-treat versus per-protocol comparison.

### 6.2 Metric definition

Metrics must have explicit measurement rules.

For example, purchase conversion should specify:

- The eligible participant population.
- The event representing a completed purchase.
- The attribution window.
- The treatment of duplicate transactions.
- The handling of missing observations.
- The treatment of refunded or cancelled purchases.

A change in metric definition during an experiment can undermine comparability.

### 6.3 Guardrail metrics

A guardrail metric detects an undesirable side effect of an intervention.

A redesigned checkout might improve conversion but also increase transaction failures.

Relevant guardrails include:

- Payment failure rate.
- Application error rate.
- Customer complaints.
- Refund rate.
- Processing latency.
- Accessibility failures.

A favorable primary outcome does not automatically justify deployment if important guardrails deteriorate.

## 7. Statistical Hypothesis Testing

Statistical testing evaluates whether the observed evidence is sufficiently inconsistent with the null hypothesis under a specified model.

### 7.1 Pooled proportion

For two independent groups, the pooled conversion estimate under the null hypothesis is:

p̂ = (xC + xT) / (nC + nT)

Where:

- xC is the number of control conversions.
- xT is the number of treatment conversions.
- nC is the control sample size.
- nT is the treatment sample size.

### 7.2 Standard error

The pooled standard error for the difference in proportions is:

SE = √[p̂(1-p̂)(1/nC + 1/nT)]

### 7.3 Z-statistic

The test statistic is:

Z = (p̂T - p̂C) / SE

The magnitude of the Z-statistic indicates how far the observed difference lies from the null value relative to the estimated standard error.

### 7.4 P-value

For a two-sided Z-test:

p-value = 2 × P(Zstandard ≥ |Zobserved|)

A small p-value indicates that the observed result would be relatively unusual under the null hypothesis and the assumptions of the test.

A p-value is not:

- The probability that the null hypothesis is true.
- The probability that the experiment will fail.
- The size of the treatment effect.
- The probability that the result will replicate.

### 7.5 Confidence intervals

A confidence interval communicates the uncertainty associated with an estimated effect.

For the difference between two independent proportions, an approximate unpooled Wald interval is:

Difference ± 1.96 × SEunpooled

A 95% confidence interval describes a procedure that covers the true parameter in approximately 95% of repeated samples under its assumptions.

The interval provides information about both the direction and magnitude of the effect.

Wald intervals can perform poorly with small samples or proportions near zero and one. More robust methods, such as Wilson-based intervals or Newcombe intervals, may be preferable.

### 7.6 Interpreting results

| Result | Interpretation |
|---|---|
| p-value below alpha and favorable direction | Evidence supports the specified alternative |
| p-value at or above alpha | Insufficient evidence to reject the null |
| Significant result in the opposite direction | Evidence of an effect opposite to the expected direction |
| Failed guardrail | Positive rollout decision is blocked |
| Insufficient observations | Statistical analysis should not proceed |

Failure to reject the null hypothesis does not establish that the null hypothesis is true.

Statistical significance also does not establish business importance.

An improvement can be statistically significant but too small to justify implementation costs.

## 8. Distinguishing Experimental Design Approaches

Different research designs address different research questions.

| Design | Characteristics | Typical application |
|---|---|---|
| Randomized controlled experiment | Random allocation to control and treatment | Evaluating causal effects |
| A/B testing | Comparison of two experimental variants | Website and application changes |
| Multivariate testing | Evaluation of multiple factors or combinations | Interface component optimization |
| Factorial design | Multiple factors studied simultaneously | Evaluating interactions |
| Quasi-experiment | Intervention without full random assignment | Policy and organizational research |
| Observational study | Variables observed without assigned intervention | Market and behavioral research |
| Before-and-after study | Outcomes compared across time periods | Operational process changes |
| Crossover design | Participants receive multiple treatments in different periods | Selected clinical and behavioral studies |

These designs are not interchangeable.

A/B testing is a specific practical application of controlled experimentation.

A quasi-experiment attempts to estimate intervention effects when random assignment is unavailable, but requires additional assumptions and careful handling of confounding.

Observational associations alone do not establish causality.

## 9. Python Implementation

The Python program implements a complete simulated two-arm experimentation workflow.

### 9.1 Domain model

The implementation uses:

- `Hypothesis` to represent the research question and testable predictions.
- `ExperimentDesign` to store statistical and operational parameters.
- `Experiment` to manage experiment state and execution.
- `Participant` to record randomized allocation.
- `ExperimentResult` to represent the analysis outcome.

Dataclasses provide structured domain records, while enumerations restrict valid experiment states and group types.

### 9.2 Sample-size estimation

The `estimate_sample_size()` method estimates the required number of participants per group using a normal approximation for independent proportions.

The calculation incorporates:

- Baseline conversion probability.
- Expected treatment conversion.
- Significance level.
- Statistical power.
- Minimum group-size restrictions.

### 9.3 Randomized execution

The simulation creates participant assignments using a seeded random generator.

The seed makes the demonstration reproducible.

The experiment generates binary conversion outcomes according to the conversion probability associated with each assigned group.

The resulting dataset can be exported to CSV.

### 9.4 Analysis and validation

The analysis method:

- Calculates group sizes.
- Counts conversions.
- Computes conversion rates.
- Calculates absolute and relative effects.
- Computes the pooled Z-statistic.
- Estimates the p-value.
- Calculates an approximate confidence interval.
- Evaluates guardrail status.
- Records the final decision.

The implementation rejects insufficient sample sizes and zero-variance situations.

### 9.5 Export

The Python implementation produces:

- `experiment_participants.csv`
- `experiment_report.json`

The CSV file contains participant-level assignment and outcome data.

The JSON file contains aggregated statistical results.

Participant identifiers in the demonstration are synthetic. A production system should use controlled identifiers and appropriate data-access restrictions.

## 10. JavaScript Implementation

The JavaScript implementation emphasizes asynchronous execution, event-driven processing, and explicit experiment lifecycle management.

### 10.1 Event-driven architecture

The `ExperimentService` extends Node.js `EventEmitter`.

It publishes events for:

- Experiment state changes.
- Participant allocation.
- Observation collection.
- Processing progress.
- Statistical analysis.
- Audit recording.

This allows monitoring and reporting components to subscribe to experiment activity without being embedded in the core analysis logic.

### 10.2 Deterministic randomization

The `RandomGenerator` class provides seeded random values and array shuffling.

The same seed produces a reproducible assignment sequence.

Reproducibility is useful for testing, debugging, and educational simulations.

A production assignment service must also consider concurrent assignment requests, persistent allocation records, and unpredictable assignment mechanisms where required.

### 10.3 Asynchronous processing

The `execute()` method processes participants asynchronously.

It periodically yields control to the Node.js event loop.

This supports other event-loop tasks during longer simulation runs.

It does not make CPU-intensive statistical calculations parallel.

### 10.4 Guardrail policy

`GuardrailPolicy` evaluates whether the treatment group's error-rate increase exceeds an allowed threshold.

This separates operational acceptance criteria from primary statistical testing.

### 10.5 Audit and export

The service maintains a chronological audit history and exports a JSON report.

The export operation uses exclusive file creation to avoid silently overwriting an existing report.

Production systems should use authenticated access, secure storage, and restricted export permissions.

## 11. C++17 Implementation

The C++17 program uses a strongly typed domain model and separates statistical utilities, allocation, execution, validation, and analysis.

### 11.1 Domain modeling

The program defines:

- `Hypothesis`
- `ExperimentConfig`
- `Participant`
- `Observation`
- `GroupMetrics`
- `AnalysisResult`

Enumerations represent experiment states, group membership, hypothesis direction, and statistical decisions.

### 11.2 Experiment engine

`ExperimentEngine` owns the experiment configuration and execution data.

Its methods enforce lifecycle transitions.

Participants cannot be allocated before an experiment starts.

Execution cannot occur without assigned participants.

Repeated execution is rejected.

### 11.3 Data integrity

The engine validates:

- Participant identifier uniqueness.
- Observation count.
- Participant-to-group consistency.
- Duplicate observations.
- Assignment and observation correspondence.

This prevents certain forms of accidental data corruption from entering the analysis stage.

### 11.4 Statistical implementation

The `Statistics` class provides:

- Normal cumulative distribution calculations.
- Two-sided p-value estimation.
- Sample-size estimation.

The `GuardrailPolicy` class independently evaluates operational risk.

The implementation uses STL containers and algorithms, including `vector`, `map`, `shuffle`, and `bernoulli_distribution`.

### 11.5 Performance considerations

Let N represent the number of participants.

| Operation | Expected complexity |
|---|---|
| Participant allocation | O(N log N) |
| Participant simulation | O(N) |
| Metric aggregation | O(N) |
| Assignment validation | O(N log N) |
| Observation validation | O(N log N) |
| Statistical analysis after aggregation | O(1) |

The map-based validation approach provides straightforward uniqueness and correspondence checks.

For larger datasets, a hash-based validation structure or streaming aggregation may reduce processing overhead.

## 12. Java 17 Enterprise Implementation

The Java program represents an enterprise-oriented experimentation service.

It emphasizes immutable records, explicit contracts, policy objects, and lifecycle enforcement.

### 12.1 Immutable domain records

Java 17 records model:

- Hypotheses.
- Experiment policies.
- Experiment definitions.
- Participants.
- Observations.
- Group metrics.
- Confidence intervals.
- Analysis results.
- Audit events.

Records reduce mutable state and provide concise domain representations.

### 12.2 Allocation strategy

`AllocationStrategy` defines an interface for participant allocation.

`RandomizedAllocation` implements the strategy using seeded randomization.

This separation allows the allocation mechanism to evolve without changing the experiment analysis service.

Alternative strategies could include block or stratified allocation.

### 12.3 Policy-driven design

`ExperimentPolicy` centralizes:

- Significance level.
- Statistical power.
- Minimum group size.
- Maximum allowed guardrail deterioration.

The experiment service applies these policies during execution and evaluation.

### 12.4 Lifecycle management

The service supports:

- Draft.
- Running.
- Completed.
- Cancelled.

Invalid state transitions raise domain exceptions.

The service also records audit events for important operations.

### 12.5 Enterprise considerations

The Java design separates domain types from operational services.

In a production implementation, this separation can support:

- Persistent experiment repositories.
- Role-based permissions.
- Concurrent execution.
- Transactional observation storage.
- Independent metric services.
- Experiment scheduling.
- Monitoring and alerting.

The demonstration uses in-memory collections and is not a distributed experimentation platform.

## 13. PostgreSQL Relational Implementation

The SQL implementation represents experimentation as a relational workflow.

It separates research definitions, participant allocation, experimental observations, and analysis records.

### 13.1 Entity relationships

The principal relationships are:

Researchers
    |
    v
Experiments
    |
    +----------------------+
    |                      |
    v                      v
Experiment Variants    Analysis Results
    |
    v
Assignments
    |
    +----------------------+
    |                      |
    v                      v
Participants         Observations
                           |
                           v
                    Metric Definitions

Experiment audit records provide a separate historical record of operational events.

### 13.2 Core tables

| Table | Responsibility |
|---|---|
| `researchers` | Experiment ownership |
| `experiments` | Research questions and experiment configuration |
| `experiment_variants` | Control and treatment definitions |
| `participants` | Participant eligibility and consent |
| `assignments` | Participant allocation |
| `metric_definitions` | Metric metadata and guardrail rules |
| `observations` | Recorded participant outcomes |
| `analysis_results` | Statistical analysis records |
| `experiment_audit` | Experiment activity history |

### 13.3 Referential integrity

Primary keys identify individual records.

Foreign keys establish relationships between experiments, variants, assignments, participants, and observations.

Unique constraints prevent duplicate experiment codes, participant assignments within the same experiment, and repeated metric observations for the same assignment.

Check constraints validate probability parameters, allocation weights, and statistical result ranges.

### 13.4 Lifecycle triggers

The experiment transition trigger verifies that a valid control and treatment configuration exists before execution.

It also prevents unsupported lifecycle transitions.

The assignment trigger checks:

- Variant ownership.
- Experiment state.
- Participant consent.
- Participant eligibility.

The observation trigger requires an active experiment assignment.

These database-level controls reduce dependence on application-only validation.

### 13.5 Randomized allocation procedure

`assign_participants()` performs randomized assignment using PostgreSQL ordering.

It validates participant identifiers and uses the two configured variants.

The procedure records assignment activity in the audit table.

The demonstration balances group sizes approximately.

Its use of database randomness does not provide a persistent, independently reproducible randomization sequence. A production system should use a controlled randomization mechanism, preserve the allocation seed or assignment evidence, and protect against concurrent allocation conflicts.

### 13.6 Metric aggregation

`experiment_group_metrics` aggregates observations by:

- Experiment.
- Variant.
- Metric.

It provides observation counts, mean metric values, and total metric values.

The view supports analytical reporting without duplicating aggregation logic across queries.

### 13.7 Statistical analysis

`analyze_conversion_experiment()` performs a two-group conversion comparison.

It validates the active experiment, metric definition, sample sizes, and binary outcome counts.

It calculates:

- Control conversion rate.
- Treatment conversion rate.
- Absolute effect.
- Relative effect.
- Pooled standard error.
- Z-statistic.
- Approximate p-value.
- Statistical decision.

The supplied SQL function uses a simplified normal-tail approximation for the p-value. Its output is suitable for demonstrating database workflow mechanics, not formal statistical reporting.

The SQL example does not implement a validated confidence-interval procedure or comprehensive sequential-testing correction.

### 13.8 Transaction management

The script uses an explicit transaction.

The invalid experiment demonstration uses a savepoint and rolls back the invalid records.

This illustrates how database operations can be tested without retaining invalid demonstration data.

Production execution should also use appropriate transaction isolation and locking when multiple workers can allocate participants or record observations concurrently.

## 14. Comparing the Five Implementations

| Dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Primary focus | Experiment simulation | Event-driven execution | Strongly typed experiment engine | Enterprise domain services | Relational workflow |
| Hypothesis modeling | Dataclass | Configuration class | Struct | Record | Relational columns |
| Randomization | Seeded random | Custom seeded generator | STL random facilities | Allocation interface | Randomized SQL procedure |
| Participant storage | List | Map | Vector | Immutable list | Relational table |
| State management | Enum | State machine | Enum | Service-controlled states | Enum and trigger |
| Statistical evaluation | Proportion Z-test | Proportion Z-test | Proportion Z-test | Proportion Z-test | SQL function |
| Guardrails | Analysis parameter | Policy class | Policy class | Policy object | Metric definitions |
| Reporting | CSV and JSON | JSON | Console | Console and audit records | Views and queries |

The implementations address the same experimental domain through different engineering approaches.

The Python implementation emphasizes scientific simulation and data export.

The JavaScript implementation emphasizes event processing and asynchronous execution.

The C++ implementation emphasizes explicit domain modeling and efficient execution.

The Java implementation emphasizes service boundaries and immutable enterprise records.

The PostgreSQL implementation emphasizes persistence, relational integrity, and analytical queries.

## 15. Experimental Validity and Failure Modes

A statistically significant result is not sufficient evidence of a well-conducted experiment.

Experimental validity depends on the quality of the design, execution, measurement, and analysis.

### 15.1 Selection bias

Selection bias occurs when the allocation or inclusion process creates systematic differences between groups.

Random assignment and predefined eligibility rules reduce this risk.

### 15.2 Measurement bias

Measurement bias occurs when outcome collection differs systematically between groups.

For example, a redesigned checkout might record successful purchases differently from the existing checkout.

A common measurement definition is necessary.

### 15.3 Attrition bias

Attrition occurs when participants leave an experiment or stop generating observations.

Differential attrition between groups can distort comparisons.

### 15.4 Contamination

Contamination occurs when participants receive conditions other than their assigned treatment.

For example, a participant assigned to the control group may access the redesigned checkout through another device.

Exposure monitoring and consistent assignment mechanisms help identify this problem.

### 15.5 Peeking and repeated testing

Repeatedly checking significance and stopping immediately when a favorable p-value appears can increase the Type I error rate.

Experiment duration and analysis procedures should be defined before execution.

Sequential experimentation requires an appropriate statistical procedure.

### 15.6 Multiple comparisons

Testing numerous metrics, segments, or treatment variations increases the probability of false-positive findings.

Appropriate corrections or predefined primary outcomes may be necessary.

### 15.7 Low statistical power

Insufficient sample size can produce inconclusive results even when a practically meaningful effect exists.

Sample-size planning should account for the expected effect and variability.

### 15.8 Practical significance

An experiment may produce a statistically significant improvement that is operationally unimportant.

Decision-making should consider:

- Absolute improvement.
- Relative improvement.
- Implementation cost.
- Operational risk.
- Customer impact.
- Long-term sustainability.

## 16. Security, Privacy and Operational Governance

Experimentation systems may collect behavioral, commercial, or personal information.

Appropriate governance should be established before participant recruitment and data collection.

Important controls include:

- Participant consent where required.
- Data minimization.
- Pseudonymous participant identifiers.
- Restricted access to participant-level observations.
- Encryption during transmission and storage.
- Controlled data exports.
- Audit logging.
- Retention and deletion policies.
- Protection against unauthorized assignment changes.
- Separation of experimental data from unrelated business records.

Sensitive attributes should not be collected merely because they might be useful for segmentation.

Where experimentation involves regulated or high-impact decisions, additional independent review and domain-specific safeguards may be required.

## 17. Limitations of the Demonstrations

The five implementations are educational, executable models of conventional two-group experimentation.

They use simulated or deterministic data rather than live participant systems.

Their statistical procedures use normal approximations and do not cover every research design.

The examples do not implement:

- Production-grade experiment scheduling.
- Distributed participant allocation.
- Full intention-to-treat analysis.
- Cluster-adjusted standard errors.
- Repeated-measures models.
- Bayesian experimental analysis.
- Factorial experimental analysis.
- Sequential hypothesis testing.
- Comprehensive multiple-testing correction.
- Advanced missing-data handling.
- Validated power calculations for every outcome type.
- Full regulatory or clinical research governance.

The SQL implementation uses a simplified statistical approximation and should not be treated as an authoritative statistical analysis package.

The simulation also assumes independent participant outcomes. Real experiments may violate this assumption through shared households, organizations, devices, locations, or other clustering mechanisms.

## 18. Practical Interpretation

A defensible experiment connects a clearly defined research question to a controlled intervention and a measurable outcome.

The complete reasoning process is:

Research Question
    |
    v
Testable Hypothesis
    |
    v
Independent and Dependent Variables
    |
    v
Experimental Design
    |
    v
Population and Eligibility
    |
    v
Sample Size and Randomization
    |
    v
Control and Treatment Execution
    |
    v
Outcome and Guardrail Measurement
    |
    v
Data Quality Validation
    |
    v
Statistical Analysis
    |
    v
Effect Size and Confidence Interval
    |
    v
Scientific and Operational Interpretation

The central distinction is between observing an outcome and establishing evidence about the effect of an intervention.

A well-designed experiment attempts to make that distinction through randomization, controlled measurement, predefined hypotheses, adequate sample size, and appropriate statistical analysis.

The final decision should reflect the combined evidence from statistical results, experimental validity, operational constraints, and potential adverse effects.
