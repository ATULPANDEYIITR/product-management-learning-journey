# Prioritization Fundamentals

## 1. Conceptual Foundation

Prioritization is the structured process of deciding which activities, projects, investments, requirements, or initiatives should receive limited resources first.

Organizations usually have more opportunities than available resources. Their constraints include:

- Limited employee availability.
- Fixed financial budgets.
- Technical dependencies.
- Delivery deadlines.
- Regulatory obligations.
- Operational capacity.
- Uncertainty about expected outcomes.
- Competing strategic objectives.

Prioritization establishes a defensible relationship between organizational objectives, expected benefits, implementation costs, and resource availability.

It is not simply the process of ranking tasks from most important to least important. A ranked list does not establish whether the selected initiatives can actually be delivered within the available budget and capacity.

A useful prioritization decision therefore answers four questions:

1. What creates the greatest relevant value?
2. What constraints limit implementation?
3. What must be sacrificed when one opportunity is selected?
4. Which combination of initiatives produces the best feasible portfolio?

## 2. Why Prioritization Matters

### Resource allocation

Resources are finite. Selecting one project consumes resources that could otherwise support another project.

A portfolio with 100 available effort units cannot automatically accommodate initiatives requiring 150 effort units.

A prioritization process makes this limitation explicit.

### Strategic alignment

Organizations need to distinguish between activities that are merely desirable and activities that advance strategic objectives.

For example, a technology division may consider:

- Security compliance.
- Infrastructure optimization.
- Customer analytics.
- Operational reporting.
- Mobile application redesign.
- Disaster recovery.

Each initiative can produce value, but their contributions to organizational objectives differ.

Strategic alignment prevents attractive but weakly relevant projects from dominating the portfolio.

### Decision consistency

Without an established decision framework, project selection may depend excessively on personal preferences, organizational hierarchy, recent requests, or subjective perceptions.

Defined evaluation criteria make decisions more transparent and repeatable.

### Risk management

An initiative with moderate commercial value may be essential because it reduces regulatory, operational, financial, or cybersecurity risk.

A purely financial ranking can therefore produce an inappropriate portfolio.

### Opportunity recognition

Prioritization identifies which opportunities should receive resources now, which should wait, and which should not proceed.

This distinction helps prevent excessive work in progress and resource fragmentation.

## 3. Fundamental Terminology

| Term | Meaning |
|---|---|
| Priority | Relative importance assigned to an initiative |
| Value | Expected contribution to an organizational objective |
| Impact | Magnitude of the expected outcome |
| Reach | Number of people, users, processes, or transactions affected |
| Confidence | Degree of certainty associated with estimates |
| Effort | Work required to implement an initiative |
| Cost | Financial resources required |
| Urgency | Importance of completing work within a particular timeframe |
| Risk reduction | Expected reduction in exposure to adverse events |
| Strategic alignment | Relationship between an initiative and organizational objectives |
| Capacity | Resources available during a defined period |
| Dependency | A prerequisite that must be completed before another initiative can proceed |
| Opportunity cost | Value of the best alternative sacrificed by a decision |
| Trade-off | A decision involving competing benefits, costs, or constraints |
| Portfolio | A collection of initiatives evaluated and managed together |
| Sensitivity analysis | Examination of how decisions change when assumptions or evaluation criteria change |

## 4. Prioritization and Opportunity Cost

Opportunity cost is the value of the best alternative that is not selected.

Suppose an organization has sufficient resources for only one of two initiatives.

| Initiative | Expected business value | Required effort |
|---|---:|---:|
| Customer analytics | 90 | 12 |
| Infrastructure optimization | 75 | 8 |

Selecting customer analytics means giving up the opportunity to implement infrastructure optimization with the same constrained resources.

The opportunity cost is not necessarily the total value of every rejected initiative. It is the value of the best feasible alternative under the decision conditions.

For a complete portfolio, opportunity cost is more complicated because initiatives can compete for different resources and may depend on one another.

The implementations use a practical approximation: the sum of framework scores assigned to deferred initiatives. This provides an exclusion indicator, not a formal economic measurement of marginal opportunity cost.

A more rigorous economic analysis would compare alternative feasible portfolios and their total expected benefits.

### Practical implications

Opportunity-cost analysis is useful when:

- Selecting between competing investments.
- Deciding whether to hire additional employees.
- Choosing between product features.
- Allocating research budgets.
- Scheduling infrastructure upgrades.
- Deciding whether to accelerate an existing project.
- Comparing immediate delivery with long-term investment.

## 5. Constraints in Prioritization

Constraints define the boundaries within which decisions must remain feasible.

### Resource constraints

Effort represents the work required to complete an initiative.

It may be expressed in:

- Person-days.
- Person-weeks.
- Engineering hours.
- Team capacity units.
- Project delivery points.

The implementations treat effort as a normalized resource unit.

### Financial constraints

A project may have a high expected benefit but require more money than the available budget.

Budget and effort must be evaluated independently.

A portfolio can satisfy its effort limit while exceeding its financial limit.

### Time constraints

Time-sensitive initiatives may become less valuable if implementation is delayed.

Examples include:

- Regulatory deadlines.
- Security vulnerabilities.
- Contractual commitments.
- Seasonal business opportunities.
- Market-entry windows.

Time-criticality is explicitly represented in WSJF and weighted scoring.

### Dependency constraints

Some initiatives cannot be completed independently.

For example:

Customer analytics may require security compliance and data infrastructure work.

A selection mechanism must therefore consider prerequisite initiatives when evaluating the requested initiative.

The implementations use dependency closure to identify all prerequisites before consuming capacity.

### Mandatory constraints

Certain initiatives are not discretionary.

Examples include legally required compliance activities and critical security remediation.

A mandatory initiative is processed before optional work. If mandatory work cannot fit within available resources, the system reports a capacity failure rather than silently discarding the requirement.

This distinction is important: a mandatory classification does not create additional resources.

## 6. Decision Frameworks

Different prioritization frameworks answer different decision questions. They should not be treated as interchangeable scoring formulas.

### 6.1 RICE

RICE represents:

- Reach.
- Impact.
- Confidence.
- Effort.

The scoring equation is:

\[
RICE =
\frac{Reach \times Impact \times Confidence}{Effort}
\]

Reach estimates the number of affected users or units within a defined period.

Impact measures the expected effect on each affected unit.

Confidence represents certainty about the estimates.

Effort measures the resources needed for implementation.

**Example**

| Factor | Value |
|---|---:|
| Reach | 5,000 |
| Impact | 8 |
| Confidence | 0.80 |
| Effort | 10 |

\[
RICE = \frac{5000 \times 8 \times 0.80}{10}
\]

\[
RICE = 3200
\]

A higher score indicates a stronger estimated return relative to effort under the chosen assumptions.

**Appropriate applications**

- Product feature selection.
- Customer-facing improvements.
- Product roadmaps.
- Growth initiatives.
- Comparative feature evaluation.

**Limitations**

RICE depends on consistent reach and impact definitions. Scores from unrelated measurement periods or different impact scales should not be compared directly.

A high RICE score does not automatically establish strategic necessity or legal compliance.

### 6.2 Weighted Scoring

Weighted scoring evaluates multiple criteria using explicitly assigned importance weights.

The implementation uses:

\[
S =
0.30B +
0.30A +
0.15U +
0.15R +
0.10C
\]

Where:

- \(B\) = Business value.
- \(A\) = Strategic alignment.
- \(U\) = Urgency.
- \(R\) = Risk reduction.
- \(C\) = Confidence expressed on a 0–10 scale.

The weights sum to 1.

| Criterion | Weight |
|---|---:|
| Business value | 30% |
| Strategic alignment | 30% |
| Urgency | 15% |
| Risk reduction | 15% |
| Confidence | 10% |

**Advantages**

- Supports multiple organizational objectives.
- Makes evaluation criteria explicit.
- Allows management to adjust strategic emphasis.
- Produces an understandable comparative score.

**Limitations**

Weights are judgment-based. A small change in weight allocation can alter project rankings.

Weighted scoring can also conceal important trade-offs when a high score on one criterion compensates for a critical weakness on another.

Hard constraints should therefore remain separate from weighted scores.

### 6.3 WSJF

Weighted Shortest Job First is used to sequence work according to the economic importance of delaying it relative to its duration or size.

The simplified implementation uses:

\[
WSJF =
\frac{Cost\ of\ Delay}{Job\ Size}
\]

Cost of Delay is represented by:

\[
Cost\ of\ Delay =
Business\ Value +
Time\ Criticality +
Risk\ Reduction
\]

Job Size is represented by estimated effort.

**Example**

| Criterion | Value |
|---|---:|
| Business value | 8 |
| Time criticality | 9 |
| Risk reduction | 7 |
| Effort | 6 |

\[
WSJF = \frac{8+9+7}{6}
\]

\[
WSJF = 4
\]

Higher WSJF scores indicate greater relative cost of delay per unit of effort.

**Appropriate applications**

- Agile portfolio management.
- Product development sequencing.
- Time-sensitive delivery.
- Incremental investment decisions.
- Competing implementation requests.

**Limitations**

The simplified formula uses normalized inputs. Actual Cost of Delay and job-size measurements require consistent organizational definitions.

### 6.4 MoSCoW

MoSCoW is a classification framework rather than a numerical scoring model.

| Category | Interpretation |
|---|---|
| Must | Essential requirement |
| Should | Important but not essential for the immediate delivery |
| Could | Desirable if resources permit |
| Won't | Explicitly excluded from the current scope |

MoSCoW is useful for scope management and stakeholder discussions.

It does not independently calculate resource consumption, opportunity cost, or financial return.

A Must classification should be supported by a clear requirement or justification. Excessive use of Must creates unrealistic delivery commitments.

## 7. Comparing Decision Frameworks

| Dimension | RICE | Weighted scoring | WSJF | MoSCoW |
|---|---|---|---|---|
| Main purpose | Estimate relative impact per effort | Compare multiple strategic criteria | Sequence by cost of delay | Classify requirement importance |
| Numerical score | Yes | Yes | Yes | No |
| Uses confidence | Yes | Yes | Not in the implemented formula | No |
| Uses effort | Yes | Indirectly, through the weighted criteria selected | Yes | No |
| Considers urgency | Indirectly | Yes | Yes | Through classification discussions |
| Handles mandatory requirements | Not inherently | Not inherently | Not inherently | Must category |
| Best application | Product features | Portfolio decisions | Delivery sequencing | Scope definition |

A mature prioritization process can use multiple frameworks for different purposes.

For example:

1. MoSCoW identifies mandatory and discretionary scope.
2. Weighted scoring compares strategic contribution.
3. RICE evaluates product opportunities.
4. WSJF sequences time-sensitive work.
5. Capacity analysis determines the feasible portfolio.

## 8. From Ranking to Portfolio Selection

Ranking and allocation are separate operations.

Ranking answers:

Which initiatives have the strongest relative scores?

Allocation answers:

Which combination of initiatives can be implemented within available resources?

Consider:

| Initiative | Score | Effort | Budget |
|---|---:|---:|---:|
| A | 95 | 12 | 20,000 |
| B | 88 | 8 | 15,000 |
| C | 80 | 5 | 8,000 |
| D | 70 | 4 | 5,000 |

Available capacity:

- Effort: 17 units.
- Budget: 25,000.

A simple ranking does not establish the best combination.

Selecting A alone uses 12 effort units and 20,000 budget units.

Selecting B and C uses 13 effort units and 23,000 budget units.

Selecting B, C, and D exceeds both constraints.

The optimal combination depends on the objective, mandatory requirements, and dependencies.

The allocation engines in these implementations use deterministic greedy selection rather than claiming to solve the general optimization problem exactly.

For larger portfolios, integer linear programming or other constrained optimization methods may be more appropriate.

## 9. Dependency Management

Dependencies create relationships between initiatives.

Example:

Customer analytics depends on security compliance.

The relationship is:

Security compliance → Customer analytics

Selecting customer analytics therefore requires security compliance to be selected or already completed.

The implementations model dependency closure.

For an initiative \(I\), its dependency closure is the complete set of prerequisite initiatives reachable through dependency relationships, including the initiative itself.

A dependency graph must be validated for:

- Missing initiatives.
- Self-dependencies.
- Circular dependencies.
- Cross-portfolio dependencies.
- Capacity implications.

Circular dependencies prevent a valid prerequisite ordering.

For example:

A → B → C → A

This configuration is rejected.

The Python, JavaScript, C++ and Java implementations detect cycles through depth-first traversal. PostgreSQL validates dependency relationships using a recursive query.

## 10. Python Implementation

**File:** `prioritization.py`

The Python implementation provides a complete portfolio simulation.

### Main components

| Component | Responsibility |
|---|---|
| `Initiative` | Stores initiative attributes |
| `Priority` | Represents priority levels |
| `Status` | Tracks decision outcomes |
| `Framework` | Identifies scoring methods |
| `Capacity` | Represents available resources |
| `PrioritizationEngine` | Evaluates and allocates initiatives |
| `Decision` | Records individual allocation outcomes |
| `PortfolioResult` | Stores portfolio-level results |

### Important mechanisms

The engine uses dictionaries to index initiatives by identifier, reducing repeated lookup operations.

Sets are used for dependency closure and duplicate prevention.

Dataclasses provide structured domain records.

Enums restrict classification and workflow states.

The scoring methods calculate RICE, WSJF, and weighted scores independently.

The allocation process:

1. Validates initiative attributes.
2. Checks dependency existence.
3. Detects circular dependencies.
4. Calculates framework scores.
5. Processes mandatory initiatives.
6. Evaluates optional initiatives.
7. Accounts for dependency effort and cost.
8. Applies capacity restrictions.
9. Records selected and deferred decisions.
10. Calculates opportunity-cost indicators.

The history exporter uses a temporary file followed by replacement to reduce the possibility of leaving a partially written decision file.

The included tests verify scoring, resource limits, mandatory work, invalid effort, missing dependencies, and circular dependencies.

## 11. JavaScript Implementation

**File:** `prioritization.js`

The JavaScript implementation focuses on event-driven decision processing.

### Main components

| Component | Responsibility |
|---|---|
| `ScoringStrategy` | Calculates framework scores |
| `PortfolioPolicy` | Enforces allocation rules |
| `PrioritizationEngine` | Coordinates evaluation and selection |
| `ValidationError` | Reports invalid inputs |
| `AllocationError` | Reports allocation failures |

### Event-driven behavior

The engine extends Node.js `EventEmitter`.

It emits:

- `initiative:evaluated`
- `portfolio:allocated`

This allows other application components to observe evaluation and allocation events without being directly embedded in the scoring logic.

### Asynchronous processing

The evaluation method is asynchronous.

It permits consumers to integrate the engine into workflows involving asynchronous reporting, persistence, or notification systems.

An allocation-in-progress guard prevents overlapping allocations on the same engine instance.

### State management

A private `Map` stores initiatives.

A private `Set` tracks selected and rejected identifiers.

The engine exposes snapshots rather than its mutable internal collection.

The allocation history receives unique identifiers and timestamps.

The file exporter uses restrictive file permissions and temporary-file replacement.

The implementation is suitable as a foundation for an event-driven prioritization service.

## 12. C++17 Implementation

**File:** `prioritization.cpp`

The C++ implementation emphasizes deterministic portfolio governance and explicit resource accounting.

### Domain structures

| Structure | Responsibility |
|---|---|
| `Initiative` | Initiative attributes and dependencies |
| `Capacity` | Effort and budget limits |
| `Decision` | Selection outcome |
| `AllocationResult` | Portfolio allocation report |
| `PrioritizationEngine` | Validation, scoring and selection |

The implementation uses:

- `std::map` for deterministic initiative indexing.
- `std::set` for dependency and selection tracking.
- `std::vector` for ranking and reporting.
- STL algorithms for deterministic ordering.
- Exceptions for validation and capacity failures.
- `std::function` for recursive dependency traversal.

The engine checks mandatory work before optional initiatives.

Dependency closure is computed before resource consumption.

A prerequisite selected by an earlier initiative is not charged again.

The allocation process checks both effort and budget before accepting additional work.

### Engineering considerations

The dependency graph is validated before allocation.

This avoids repeatedly checking structural correctness during portfolio selection.

The implementation uses an epsilon when comparing floating-point resource values.

This reduces problems caused by floating-point representation differences.

The approach is appropriate for moderately sized portfolios where deterministic ranking and explainable decisions are important.

## 13. Java 17 Implementation

**File:** `PrioritizationFundamentals.java`

The Java implementation emphasizes enterprise domain modeling and service separation.

### Architectural components

| Component | Responsibility |
|---|---|
| `Initiative` | Immutable initiative record |
| `Capacity` | Immutable resource limits |
| `Score` | Framework evaluation result |
| `Decision` | Recorded decision |
| `Allocation` | Immutable portfolio outcome |
| `ScoringStrategy` | Scoring interface |
| `RiceStrategy` | RICE implementation |
| `WsjfStrategy` | WSJF implementation |
| `WeightedStrategy` | Weighted evaluation |
| `PrioritizationPolicy` | Eligibility rules |
| `PrioritizationService` | Portfolio decision orchestration |

Java records provide immutable data structures for core domain objects.

The `ScoringStrategy` interface separates scoring behavior from allocation logic.

An `EnumMap` registers framework implementations.

The service validates dependencies and maintains an audit history.

The policy object evaluates minimum confidence, strategic alignment, and classification consistency.

The service returns immutable allocation records.

The implementation demonstrates a separation between:

- Domain validation.
- Scoring strategies.
- Policy evaluation.
- Resource allocation.
- Decision reporting.

This separation is useful in enterprise systems where scoring rules and business policies change independently.

## 14. PostgreSQL Implementation

**File:** `prioritization.sql`

The database implementation models prioritization as a relational workflow.

### Database relationship

    Organization
        |
        v
    Portfolio
        |
        +----------------------+
        |                      |
        v                      v
    Initiatives          Scoring Configurations
        |
        v
    Initiative Dependencies
        |
        v
    Allocation Runs
        |
        v
    Initiative Decisions
        |
        v
    Portfolio Reports

### Relational entities

| Table | Purpose |
|---|---|
| `organizations` | Organizational ownership |
| `portfolios` | Resource and policy boundaries |
| `initiatives` | Initiative attributes |
| `initiative_dependencies` | Prerequisite relationships |
| `scoring_configurations` | Framework configuration |
| `allocation_runs` | Allocation execution history |
| `initiative_decisions` | Individual decisions |

### Integrity enforcement

Primary keys identify records.

Foreign keys enforce relationships between organizational entities.

Unique constraints prevent duplicate initiative codes within a portfolio.

Check constraints validate numerical ranges and prohibit invalid mandatory classifications.

The dependency trigger checks cross-portfolio relationships and circular dependencies.

Indexes support portfolio filtering, decision retrieval, dependency traversal, and historical reporting.

### Scoring function

`calculate_initiative_score()` implements the three scoring methods.

Keeping score calculations in a database function allows SQL queries and allocation procedures to use the same definitions.

### Allocation procedure

`allocate_portfolio()` performs portfolio allocation.

It:

1. Locks the portfolio record.
2. Validates the portfolio.
3. Creates an allocation run.
4. Processes mandatory initiatives.
5. Calculates dependency closures.
6. Checks resource consumption.
7. Evaluates optional initiatives.
8. Calculates opportunity-cost indicators.
9. Records initiative decisions.
10. Updates initiative statuses.
11. Completes the allocation run.

The portfolio-level row lock serializes allocation attempts against the same portfolio when callers follow this procedure.

### Reporting

The SQL script provides:

- Initiative ranking.
- Framework comparison.
- Allocation reports.
- Selected and deferred initiative counts.
- Capacity utilization.
- Opportunity-cost indicators.
- Confidence validation.
- Mandatory initiative validation.
- Historical allocation comparison.

The sample data executes two allocation runs, one using weighted scoring and another using WSJF.

## 15. Decision Governance

A prioritization score should support a decision, not replace organizational accountability.

A practical governance process separates the following activities:

| Stage | Responsibility |
|---|---|
| Proposal | Identify the initiative and expected outcome |
| Validation | Check the quality and completeness of estimates |
| Evaluation | Apply the selected decision framework |
| Constraint analysis | Assess capacity, cost and dependencies |
| Decision | Select, defer or reject the initiative |
| Authorization | Confirm the decision with the responsible authority |
| Monitoring | Compare expected and actual outcomes |
| Reassessment | Update the portfolio when assumptions change |

A score is not an approval.

An initiative can receive a high score and still be unsuitable because of regulatory restrictions, technical dependencies, financial limitations, or unacceptable risk.

Similarly, a mandatory initiative can require implementation despite a relatively low discretionary scoring result.

The distinction between scoring and governance is essential for reliable decisions.

## 16. Sensitivity Analysis

Sensitivity analysis evaluates whether portfolio decisions remain stable when assumptions change.

The implementations compare three frameworks:

- RICE.
- WSJF.
- Weighted scoring.

Suppose an initiative ranks first under RICE but lower under WSJF.

This difference can indicate that the initiative has substantial reach and impact but a relatively weak cost-of-delay position.

A portfolio manager can investigate:

- Whether reach estimates are realistic.
- Whether impact assumptions are consistent.
- Whether effort estimates are accurate.
- Whether urgency has been underestimated.
- Whether risk reduction should receive greater weight.
- Whether a mandatory constraint has been overlooked.

A framework that produces a different ranking is not necessarily incorrect. It may be answering a different decision question.

Sensitivity analysis should examine the reasons behind ranking changes rather than simply choosing the framework that produces a preferred outcome.

## 17. Edge Cases and Failure Conditions

| Condition | Expected handling |
|---|---|
| Duplicate initiative identifier | Reject the portfolio |
| Negative effort | Reject the initiative |
| Zero effort | Reject the initiative |
| Invalid confidence | Reject the initiative |
| Missing dependency | Reject the dependency graph |
| Circular dependency | Reject the dependency graph |
| Self-dependency | Reject the initiative |
| Mandatory work exceeds capacity | Report allocation failure |
| Optional work exceeds budget | Defer the initiative |
| Low-confidence initiative | Apply policy restrictions |
| Zero strategic alignment | Apply configured policy |
| Empty portfolio | Reject allocation |
| Invalid framework | Report validation failure |
| Repeated dependency | Account for its resources once |
| Unused capacity | Report remaining resources |

A production system should also address:

- Changing initiative estimates during allocation.
- Concurrent portfolio modifications.
- Currency conversion and financial rounding.
- Multi-period capacity planning.
- Resource specialization.
- Risk-adjusted benefit estimates.
- Dependencies across organizational portfolios.
- Historical decision reproducibility.
- Authorization and audit access.
- Allocation rollback and recovery.

## 18. Performance Considerations

The implementations use maps, sets, and indexed relationships to avoid repeatedly scanning entire collections for every lookup.

For a portfolio containing \(n\) initiatives and \(e\) dependency relationships:

| Operation | Approximate complexity |
|---|---|
| Initiative indexing | \(O(n)\) |
| Ranking | \(O(n \log n)\) |
| Dependency validation | \(O(n+e)\) |
| Dependency traversal | \(O(n+e)\) in the complete graph |
| Set-based selection | Average \(O(1)\) membership |
| Portfolio reporting | Depends on the number of stored decisions |

The greedy allocation process can revisit dependency closures for multiple initiatives. Its practical cost depends on the graph structure and the number of candidates.

For larger portfolios, dependency closures can be cached after graph validation.

PostgreSQL indexes improve retrieval and reporting, while recursive CTEs provide dependency traversal.

The allocation procedure serializes access at the portfolio level. This improves consistency but can reduce throughput when many allocations target the same portfolio.

## 19. Limitations and Methodological Considerations

These implementations provide practical prioritization models, not universal decision rules.

Important limitations include:

1. Greedy allocation does not guarantee a globally optimal portfolio.
2. Weighted scores depend on subjective criteria and weights.
3. RICE results depend on consistent reach and impact definitions.
4. WSJF results depend on reliable cost-of-delay and effort estimates.
5. MoSCoW does not independently calculate economic value.
6. Opportunity-cost indicators based on deferred scores are approximations.
7. Effort is represented as a single resource dimension.
8. Different types of employee skills are not modeled separately.
9. Multi-period scheduling is not implemented.
10. Uncertainty is represented through confidence scores rather than full probability distributions.
11. The PostgreSQL scoring configuration table stores framework weights, while the sample scoring function uses the documented fixed weighted-scoring formula.
12. The SQL allocation procedure assumes portfolio-level allocation is the authoritative workflow; direct concurrent modifications to initiative records should be restricted through database permissions or stronger transaction controls.

For complex portfolios, mathematical optimization can provide a stronger allocation method.

A binary decision variable can represent whether initiative \(i\) is selected:

\[
x_i \in \{0,1\}
\]

An effort constraint can be expressed as:

\[
\sum_{i=1}^{n} E_i x_i \leq E_{\max}
\]

A budget constraint can be expressed as:

\[
\sum_{i=1}^{n} C_i x_i \leq B_{\max}
\]

For a dependency between initiative \(i\) and prerequisite \(j\):

\[
x_i \leq x_j
\]

An objective function can maximize the total estimated value:

\[
\max \sum_{i=1}^{n} V_i x_i
\]

This formulation illustrates the distinction between ranking initiatives individually and optimizing a portfolio of interdependent investments.

## 20. Execution

### Python

File: `prioritization.py`

Runtime: Python 3.10 or later.

Execution: `python prioritization.py`

The script prints framework rankings, allocation decisions, sensitivity results, and validation-test outcomes.

### JavaScript

File: `prioritization.js`

Runtime: Node.js 18 or later.

Execution: `node prioritization.js`

The program demonstrates asynchronous evaluation, event notifications, allocation, and audit-history export.

### C++17

File: `prioritization.cpp`

Compilation with GCC:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic prioritization.cpp -o prioritization`

Execution: `./prioritization`

The program reports framework rankings, resource consumption, selected initiatives, and validation results.

### Java 17

File: `PrioritizationFundamentals.java`

Compilation:

`javac --release 17 PrioritizationFundamentals.java`

Execution:

`java PrioritizationFundamentals`

The program demonstrates immutable records, scoring strategies, service-based allocation, and sensitivity analysis.

### PostgreSQL

File: `prioritization.sql`

Execute using:

`psql -d database_name -v ON_ERROR_STOP=1 -f prioritization.sql`

The database must support PostgreSQL 15 or later.

The script creates a dedicated schema, domain types, tables, constraints, indexes, functions, procedures, triggers, sample records, allocation runs, and reports.

The entire script runs within a transaction. A failed statement prevents partial application of the schema and sample workflow.

## 21. Learning Outcomes

The five implementations demonstrate how prioritization develops from a simple comparative scoring exercise into a constrained portfolio decision process.

The central distinction is between:

- **Importance:** How significant an initiative appears.
- **Scoring:** How an initiative performs against defined criteria.
- **Priority:** Its relative position among competing initiatives.
- **Feasibility:** Whether the organization can implement it.
- **Opportunity cost:** What the organization sacrifices by selecting it.
- **Allocation:** Which feasible combination receives resources.
- **Governance:** Who is responsible for authorizing and reviewing the resulting decision.

Reliable prioritization requires all these dimensions to be considered together. A high numerical score is useful evidence, but a defensible decision must also account for strategic objectives, constraints, dependencies, uncertainty, mandatory commitments, and the value of alternative opportunities.
