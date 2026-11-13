# Value vs Effort: Opportunity Estimation and Prioritization

## Project Overview

Value vs Effort is a quantitative decision-making framework for comparing competing opportunities under limited resources.

Organizations routinely evaluate product improvements, software engineering initiatives, security enhancements, infrastructure upgrades, and operational changes. These opportunities differ in their expected benefits, implementation costs, uncertainty, risk, and strategic importance.

A value-versus-effort opportunity matrix provides a structured way to compare these initiatives rather than selecting work based only on intuition, urgency, or stakeholder influence.

This project implements a complete prioritization model across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover estimation, confidence adjustment, risk assessment, opportunity classification, dependency validation, capacity allocation, reporting, and repository-governance integration.

## Core Concepts

### Value Estimation

Value estimation measures the expected benefit of implementing an opportunity.

The model considers four dimensions:

| Dimension | Weight | Interpretation |
|---|---:|---|
| Customer impact | 35% | Improvement in customer experience or outcomes |
| Strategic alignment | 30% | Contribution to organizational objectives |
| Revenue impact | 20% | Potential financial contribution |
| Urgency | 15% | Importance of addressing the opportunity promptly |

Each dimension receives a score from 1 to 5.

The weighted value score is:

\[
V = \frac{100}{5}
(0.35C+0.30S+0.20R+0.15U)
\]

Where:

- \(C\) represents customer impact.
- \(S\) represents strategic alignment.
- \(R\) represents revenue impact.
- \(U\) represents urgency.

The resulting value ranges from 20 to 100 because every rating has a minimum value of 1.

A score of 100 represents the maximum possible weighted assessment.

Value is an estimated relative score, not a guaranteed financial return.

### Effort Estimation

Effort represents the resources required to implement an opportunity.

The project uses three-point estimation:

- Optimistic estimate: minimum reasonable effort.
- Expected estimate: most likely effort.
- Pessimistic estimate: maximum reasonable effort.

The triangular expected estimate is:

\[
E = \frac{E_{low}+E_{expected}+E_{high}}{3}
\]

This method makes estimation uncertainty visible rather than treating a single estimate as certain.

Effort can represent person-days, person-weeks, engineering points, or another consistently defined resource unit.

The unit must remain consistent across opportunities being compared.

A person-week should not be compared directly with a monetary cost or an uncalibrated story-point estimate.

### Confidence Adjustment

An estimate may be uncertain because of incomplete requirements, limited historical data, unknown dependencies, or technical complexity.

The implementation uses value and effort confidence scores.

\[
C_f = \frac{\min(C_v,C_e)}{5}
\]

Where:

- \(C_v\) is value confidence.
- \(C_e\) is effort confidence.
- \(C_f\) is the combined confidence factor.

The lower confidence score controls the adjustment.

This conservative approach prevents a high-confidence value estimate from hiding a poorly understood implementation effort.

### Risk Adjustment

Technical, operational, security, regulatory, and delivery risks can reduce the expected usable value.

The model uses the following illustrative risk factors:

| Risk | Factor |
|---|---:|
| Low | 1.00 |
| Medium | 0.85 |
| High | 0.65 |

Adjusted value is:

\[
V_a = V \times C_f \times R_f
\]

Where:

- \(V_a\) is adjusted value.
- \(V\) is estimated value.
- \(C_f\) is confidence.
- \(R_f\) is the risk factor.

These factors are configurable assumptions, not universal industry standards.

Risk should be reassessed when new technical or operational evidence becomes available.

### Value-to-Effort Ratio

The central comparison is:

\[
R_{VE} = \frac{V_a}{E}
\]

A higher ratio indicates more adjusted value per unit of estimated effort.

For example, an opportunity with adjusted value 80 and effort 4 has a ratio of 20.

An opportunity with adjusted value 90 and effort 18 has a ratio of 5.

The second opportunity has a higher absolute value, but the first provides a better value-to-effort ratio.

This distinction is important when resources are constrained.

The ratio should not be interpreted as a complete investment decision because it does not independently capture dependencies, mandatory work, strategic constraints, or portfolio balance.

## Opportunity Matrix

The opportunity matrix groups initiatives according to estimated value and required effort.

| Category | Value and effort characteristics | Typical treatment |
|---|---|---|
| Quick Win | High adjusted value relative to low effort | Prioritize when dependencies and constraints permit |
| Strategic Investment | Attractive value relative to effort | Schedule as a planned investment |
| Fill-In | Moderate or limited value relative to effort | Use available capacity selectively |
| Low Priority | Weak adjusted value relative to effort | Defer or reassess |

The implemented numerical classification is:

| Category | Rule |
|---|---|
| Quick Win | Ratio at least 20 |
| Strategic | Ratio at least 8 and below 20 |
| Fill-In | Ratio below 8 and adjusted value at least 25 |
| Low Priority | Ratio below 8 and adjusted value below 25 |

These thresholds are configurable decision rules.

They should be calibrated against the organization's historical delivery data and resource constraints.

The matrix is a prioritization aid, not an automatic substitute for management judgment.

## Estimation Uncertainty and Sensitivity Analysis

Three-point estimation exposes the difference between optimistic, expected, and pessimistic effort.

The Python implementation evaluates the ratio under all three effort assumptions.

For a fixed adjusted value:

\[
R_{optimistic} = \frac{V_a}{E_{low}}
\]

\[
R_{expected} = \frac{V_a}{E_{expected}}
\]

\[
R_{pessimistic} = \frac{V_a}{E_{high}}
\]

This allows decision-makers to identify opportunities whose attractiveness depends heavily on optimistic assumptions.

An opportunity that remains attractive under pessimistic effort is generally more robust than one that becomes unattractive after a small estimation change.

A more advanced organizational implementation can extend the model with Monte Carlo simulation, empirical estimation distributions, confidence intervals, and scenario-specific resource constraints.

## Dependency Management

Opportunities frequently depend on other initiatives.

For example:

- A data integration platform may require documentation and interface specifications.
- A security automation initiative may require infrastructure access.
- A deployment improvement may require CI/CD pipeline standardization.

The project models dependencies as directed relationships.

An opportunity cannot be selected independently if its required dependencies are omitted.

The dependency model validates:

- Missing dependency identifiers.
- Duplicate dependencies.
- Self-dependencies.
- Circular dependency chains.

Cycle detection uses depth-first traversal.

The expected graph-validation complexity is:

\[
O(V+E)
\]

Where \(V\) represents opportunities and \(E\) represents dependency relationships.

## Capacity-Constrained Prioritization

A ranked list does not automatically produce a feasible delivery plan.

An organization may have only 15 person-weeks available even when the combined estimated effort of all opportunities is considerably higher.

The implementations therefore include capacity allocation.

The allocation process:

1. Sorts opportunities by value-to-effort ratio.
2. Resolves each opportunity's dependency bundle.
3. Calculates the total additional effort required.
4. Selects the complete bundle if capacity permits.
5. Updates the remaining capacity.
6. Returns the selected portfolio.

The implemented allocation strategy is a dependency-aware greedy heuristic.

It is computationally practical, but it does not guarantee the globally optimal portfolio.

An exact optimization approach may use integer programming or a dependency-constrained knapsack model.

The distinction matters when the number of opportunities, resource constraints, or dependencies becomes large.

## Python Implementation

**File role:** Repository-independent prioritization and simulation.

The Python program uses:

| Component | Purpose |
|---|---|
| `Estimation` | Validates three-point estimates |
| `Opportunity` | Stores opportunity attributes |
| `RiskLevel` | Represents risk classifications |
| `Priority` | Represents matrix classifications |
| `PrioritizationEngine` | Calculates value, confidence, risk, and ratios |
| `DependencyManager` | Validates dependency relationships |
| `capacity_plan()` | Selects dependency-aware opportunity bundles |
| `sensitivity_analysis()` | Evaluates effort scenarios |
| `export_csv()` | Exports the ranking report |

The implementation uses dataclasses to structure estimation and opportunity data.

Immutable estimation objects prevent accidental modification of individual estimate values.

Validation rejects non-finite numbers, invalid rating ranges, zero expected effort, duplicate identifiers, missing dependencies, and circular dependency chains.

The program also contains assertions that verify basic portfolio and capacity conditions.

### Python Execution

Requirements:

- Python 3.10 or newer.
- Standard library only.

Run the file using `python filename.py`.

The execution produces:

- Opportunity ranking.
- Adjusted value calculations.
- Capacity allocation.
- Sensitivity analysis.
- `opportunity_report.csv`.

The CSV report provides a structured output for subsequent analysis.

## JavaScript Implementation

**File role:** Event-driven opportunity evaluation.

The JavaScript implementation emphasizes application behavior and asynchronous state management.

Its main components are:

| Component | Responsibility |
|---|---|
| `Opportunity` | Validates opportunity records |
| `OpportunityEngine` | Manages the portfolio |
| `EventEmitter` | Publishes registration and evaluation events |
| `evaluate()` | Performs asynchronous estimation |
| `evaluateAll()` | Calculates the portfolio concurrently |
| `validateDependencies()` | Detects missing and circular dependencies |
| `allocateCapacity()` | Produces a capacity-constrained selection |
| `exportReport()` | Writes a CSV report |

### Event-Driven Processing

The implementation uses Node.js `EventEmitter`.

Opportunity registration publishes an event.

Portfolio evaluation publishes another event after all estimates have completed.

This separates business operations from consumers that need to react to changes.

For example, a reporting service could subscribe to portfolio evaluation events without modifying the prioritization engine.

### Asynchronous Evaluation

`Promise.all()` evaluates opportunities concurrently.

The implementation also tracks a portfolio revision.

If the underlying opportunity data changes while evaluation is in progress, the result is rejected rather than being applied to a different portfolio state.

This protects against stale calculation results.

The current implementation uses an in-process revision check. A distributed application would require persistent versioning or transaction-based concurrency control.

### Audit History

Each significant operation records:

- Action type.
- Opportunity identifier.
- Portfolio revision.
- Timestamp.
- Additional details.

This provides a lightweight execution history.

A production application should persist audit events in a database and enforce appropriate access controls.

## C++17 Implementation

**File role:** Repository governance and merge-eligibility evaluation integrated with portfolio prioritization.

The C++ program provides a strongly typed model for opportunity evaluation and repository merge conditions.

It implements:

- Opportunity domain structures.
- Three-point effort estimates.
- Risk and priority enumerations.
- Dependency graph validation.
- Weighted value calculations.
- Capacity allocation.
- Pull Request state evaluation.
- Reviewer eligibility.
- Approval counting.
- Status-check validation.
- Branch protection requirements.
- Merge blocker reporting.

### Repository Governance Model

The governance model distinguishes the following objects:

| Object | Responsibility |
|---|---|
| `Opportunity` | Represents a proposed investment |
| `PullRequest` | Represents a proposed repository change |
| `Review` | Represents a reviewer's decision |
| `BranchProtection` | Defines repository-level merge restrictions |
| `CheckStatus` | Represents automated validation results |
| `MergeDecision` | Reports merge eligibility and blockers |

### Merge Eligibility

A Pull Request is eligible only when its relevant workflow and governance conditions are satisfied.

The C++ implementation checks:

- Pull Request remains open.
- It is not a draft.
- Source and target branches are distinct.
- Source branch is synchronized.
- Merge conflicts are absent.
- Review conversations are resolved.
- Required eligible approvals exist.
- No active changes-requested review exists.
- Required automated status checks have passed.

The evaluation returns a collection of blockers instead of stopping after the first failed condition.

This is useful because developers can identify all currently detectable merge restrictions in one evaluation.

### Data Structures and Complexity

The implementation uses:

- `unordered_map` for opportunity lookup.
- `vector` for opportunity and review collections.
- `set` for unique dependencies and reviewer tracking.
- `map` for status-check state.
- STL sorting algorithms for ranking.

Dependency validation is \(O(V+E)\).

Sorting \(N\) opportunities requires \(O(N\log N)\).

The greedy capacity planner has additional dependency-resolution and selection costs.

The program is an in-memory governance simulation. Actual repository authorization, Git operations, protected-branch enforcement, and remote status-check verification must be implemented by a repository hosting platform or its authenticated API.

## Java 17 Implementation

**File role:** Enterprise-oriented opportunity and repository governance.

The Java implementation uses explicit domain types and service boundaries.

### Domain Types

| Type | Responsibility |
|---|---|
| `EffortEstimate` | Validated effort range |
| `Opportunity` | Immutable opportunity representation |
| `Evaluation` | Calculated prioritization result |
| `Review` | Reviewer decision |
| `ProtectionPolicy` | Merge-governance configuration |
| `PullRequest` | Repository change lifecycle |
| `EstimationService` | Value and effort calculations |
| `PortfolioService` | Registration, validation, and allocation |
| `GovernanceService` | Merge-eligibility decisions |

Java records represent immutable data structures.

Enums restrict domain states to recognized values.

Collections and streams support ranking, aggregation, dependency handling, and reporting.

### Enterprise Policy Separation

The implementation separates estimation policy from repository governance policy.

The estimation service calculates opportunity attractiveness.

The portfolio service manages opportunity registration and resource allocation.

The governance service determines whether a Pull Request satisfies its applicable merge requirements.

This separation makes it possible to change estimation weights without changing repository merge rules.

### Pull Request Lifecycle

The Java implementation models the following states:

- `DRAFT`
- `OPEN`
- `MERGED`
- `CLOSED`

A Pull Request must be open before it can be merged.

A closed, unmerged Pull Request can be reopened.

A merged Pull Request cannot be closed as an ordinary unmerged change.

These transitions represent application-level domain rules. They are not a complete implementation of a Git hosting platform's lifecycle.

### Approval Semantics

An approval is a review decision.

It is not a direct instruction to merge a Pull Request.

The governance service considers:

- Reviewer eligibility.
- Review staleness.
- Review state.
- Required approval count.
- Changes-requested decisions.
- Required automated checks.
- Conversation resolution.
- Source synchronization.
- Linear-history requirements.

The example demonstrates how review decisions influence merge eligibility without treating them as interchangeable with branch-protection policy.

## PostgreSQL Implementation

**File role:** Relational persistence, reporting, dependency processing, and transactional governance.

The SQL script creates the `prioritization` schema and models two connected domains:

1. Opportunity and resource prioritization.
2. Repository and Pull Request governance.

### Relational Structure

The principal portfolio relationships are:

    Prioritization Policy
            |
            v
       Opportunities
            |
            v
    Opportunity Dependencies
            |
            v
     Opportunity Matrix
            |
            v
    Capacity Allocation

The repository relationships are:

    Repository
        |
        +---- Repository Members
        |
        +---- Branches
        |         |
        |         +---- Commits
        |
        +---- Pull Requests
                  |
                  +---- Pull Request Commits
                  |
                  +---- Reviews
                  |       |
                  |       +---- Review Comments
                  |
                  +---- Status Checks
                  |
                  +---- Branch Protection
                  |       |
                  |       +---- Required Status Checks
                  |
                  +---- Merge Eligibility
                          |
                          +---- Merge Audit

### Database Objects

| Database object | Purpose |
|---|---|
| `opportunities` | Stores value and effort estimates |
| `opportunity_dependencies` | Stores dependency relationships |
| `prioritization_policies` | Stores scoring weights and thresholds |
| `evaluate_opportunity()` | Calculates an opportunity score |
| `opportunity_matrix` | Exposes evaluated opportunities |
| `allocate_opportunities()` | Performs dependency-aware allocation |
| `repositories` | Stores repository identity |
| `repository_members` | Stores repository roles |
| `branches` | Stores source and target branches |
| `commits` | Stores commit metadata |
| `pull_requests` | Stores proposed changes and lifecycle state |
| `reviews` | Stores review decisions |
| `review_comments` | Stores inline discussions |
| `status_checks` | Stores automated check outcomes |
| `branch_protection_policies` | Stores enforcement requirements |
| `required_status_checks` | Stores mandatory check names |
| `merge_audit` | Records eligibility and merge decisions |

### Constraints and Integrity

The schema uses primary keys, foreign keys, unique constraints, and check constraints.

These protect important data relationships.

Examples include:

- An opportunity cannot have negative effort.
- Expected effort cannot exceed pessimistic effort.
- A dependency cannot reference the same opportunity.
- A branch belongs to one repository.
- A Pull Request cannot use identical source and target branches.
- A Pull Request merge record must contain a merge timestamp, strategy, and commit.
- A status check cannot be marked pending with a completion timestamp.

A recursive trigger detects circular opportunity dependencies.

This prevents invalid dependency graphs from entering the portfolio.

### Approval Calculation

The `eligible_approval_count()` function evaluates the latest review decision from each reviewer.

An approval counts only when the reviewer:

- Is an active repository member.
- Has an eligible review.
- Is assigned an allowed repository role.
- Has a non-stale approval.
- Has not subsequently replaced that approval with a different review state.

This prevents multiple historical approvals from the same reviewer from being counted as separate independent approvals.

The `has_active_change_request()` function independently identifies current changes-requested decisions.

### Merge Eligibility

The `evaluate_merge_eligibility()` function checks repository-level conditions against the Pull Request and target branch policy.

It evaluates:

- Pull Request state.
- Draft restrictions.
- Source synchronization.
- Merge conflicts.
- Review conversation resolution.
- Required approvals.
- Active changes-requested decisions.
- Required status checks.
- Linear-history restrictions.

A status check must have passed for the current source branch head commit represented in the database.

This prevents an earlier successful check from automatically satisfying the requirement after the source branch changes.

### Transactional Merge

The `merge_pull_request()` procedure:

1. Locks the Pull Request.
2. Verifies that it is open.
3. Locks the associated branches in a stable order.
4. Re-evaluates merge eligibility.
5. Verifies the merge commit belongs to the same repository.
6. Updates the Pull Request to merged.
7. Updates the target branch head.
8. Writes a merge audit record.

The transaction ensures that database changes are committed together or rolled back together.

Database row locking helps prevent concurrent merge attempts from modifying the same Pull Request simultaneously.

The example SQL includes a deliberately blocked transaction to demonstrate failure handling.

The successful merge procedure is provided as an explicit, commented operation so that sample data remains available for governance evaluation.

### Indexing

The database creates indexes for common access patterns.

Examples include:

- Repository and Pull Request state.
- Target branch and Pull Request state.
- Reviewer history.
- Unresolved review comments.
- Status-check retrieval.
- Reverse dependency lookup.
- Recent merge audit records.

Indexes improve lookup performance but introduce additional storage and write overhead.

Index selection should be reviewed against actual query plans and production data volume.

## Distinctions Between the Four Governance Areas

The opportunity-prioritization model and repository governance model serve related but different decision-making purposes.

The following four repository concepts must remain distinct.

### Pull Requests

A Pull Request is the workflow mechanism for proposing changes from a source branch into a target branch.

It represents a proposed changeset, not an automatic modification of either branch.

Its lifecycle includes:

- Creation.
- Draft development.
- Review requests.
- Discussion.
- Status-check execution.
- Synchronization with the target branch.
- Conflict resolution.
- Merge or closure.
- Reopening when permitted.

A Pull Request may contain multiple commits.

Its proposed changes can evolve as new commits are pushed to the source branch.

The target branch remains unchanged until an authorized merge operation updates it.

Merge strategies include:

| Strategy | Behavior |
|---|---|
| Merge commit | Preserves branch history with a merge commit |
| Squash | Combines proposed changes into one target-branch commit |
| Rebase | Replays commits onto a different base |

The choice affects commit history and repository traceability.

### Code Review

Code Review evaluates the technical quality of proposed changes.

Its purpose is to identify defects, improve maintainability, validate design decisions, and examine security and operational implications.

Reviewers may assess:

- Correctness.
- Readability.
- Test coverage.
- Error handling.
- Security controls.
- Performance.
- Compatibility.
- Maintainability.
- Scope of changes.

Inline comments attach discussion to particular files or lines.

Review conversations may contain multiple responses.

Resolving a discussion indicates that the conversation has been addressed according to the review workflow. It does not independently establish that all repository merge conditions are satisfied.

Typical review outcomes include:

- Approval.
- Changes requested.
- Informational comments.
- Dismissal.

A technically correct review should focus on the actual changeset rather than unrelated stylistic preferences.

### Approvals

Approval represents a formal review decision.

It indicates that an eligible reviewer accepts the proposed changes according to the applicable review process.

An approval does not independently authorize merging.

Approval requirements may include:

- A minimum number of reviews.
- Eligible reviewer roles.
- Code-owner approval.
- Independent reviewer requirements.
- Fresh approvals after relevant changes.
- Review dismissal rules.

Stale approvals may no longer represent the current changeset.

Dismissed approvals must not be counted as active approval decisions.

The actual effect of an approval depends on the repository's configured governance requirements.

### Branch Protection

Branch Protection enforces repository-level conditions before changes can be merged into a protected branch.

It establishes the rules that repository operations must satisfy.

Common restrictions include:

| Restriction | Purpose |
|---|---|
| Required reviews | Enforces minimum review conditions |
| Required status checks | Requires successful automated validation |
| Direct-push restrictions | Prevents unauthorized direct changes |
| Force-push restrictions | Protects existing branch history |
| Branch deletion restrictions | Prevents accidental removal |
| Conversation requirements | Requires review discussions to be resolved |
| Linear-history requirements | Enforces an approved commit-history structure |
| Administrator restrictions | Determines whether administrators must follow normal controls |
| Bypass permissions | Defines authorized exceptions |

Branch protection is a repository enforcement mechanism.

It does not perform the technical review itself.

It does not create approvals.

It evaluates whether the conditions established by repository governance have been satisfied.

## Relationship Between Repository Governance Mechanisms

The four areas form a coordinated development workflow:

    Pull Request
         |
         v
    Proposed Changeset
         |
         v
    Code Review
         |
         v
    Review Decisions
         |
         v
    Approval Requirements
         |
         v
    Automated Status Checks
         |
         v
    Branch Protection Evaluation
         |
         v
    Merge Eligibility
         |
         v
    Authorized Merge

The responsibilities are distinct:

| Mechanism | Primary responsibility |
|---|---|
| Pull Request | Proposes changes |
| Code Review | Evaluates proposed changes |
| Approvals | Records formal review decisions |
| Branch Protection | Enforces repository-level conditions |
| Merge Eligibility | Determines whether merging is permitted |
| Merge | Applies approved changes to the target branch |

A Pull Request can be open without being approved.

It can have approvals while required checks are failing.

It can pass all automated checks while review conversations remain unresolved.

It can receive technically sound reviews while failing branch-protection requirements.

Merge eligibility is determined by the combination of applicable conditions, not by any single successful event.

## Practical Decision-Making Applications

### Product Management

Product managers can use the opportunity matrix to compare:

- Feature development.
- Customer experience improvements.
- Platform modernization.
- Technical debt reduction.
- Security improvements.
- Operational automation.

Value estimation should incorporate customer outcomes and strategic objectives.

Effort estimation should reflect engineering capacity and technical dependencies.

### Software Engineering

Engineering teams can prioritize:

- Build pipeline improvements.
- Automated testing.
- Infrastructure upgrades.
- API modernization.
- Performance optimization.
- Code quality initiatives.

Dependencies should be included before capacity is committed.

### Cybersecurity

Security initiatives may have high strategic importance even when their direct revenue contribution is limited.

Examples include:

- Vulnerability remediation.
- Access-control improvements.
- Dependency scanning.
- Security testing automation.
- Audit logging.
- Secrets management.

Mandatory security and compliance requirements must not be discarded merely because their value-to-effort ratio is lower than that of optional features.

Such requirements should be represented as portfolio constraints or mandatory work.

### Enterprise Portfolio Management

An enterprise can use the model to compare competing initiatives across departments.

The decision process should consider:

- Strategic objectives.
- Budget.
- Available personnel.
- Delivery deadlines.
- Risk exposure.
- Dependencies.
- Regulatory obligations.
- Operational constraints.

A high-scoring opportunity is not automatically the best organizational decision.

Portfolio-level trade-offs remain necessary.

## Limitations and Design Considerations

### Subjective Scoring

The 1-5 rating scale introduces judgment.

Different evaluators may assign different scores to the same opportunity.

Organizations should define rating criteria and periodically calibrate evaluators.

### Relative Rather Than Absolute Value

The weighted value score is a normalized assessment.

It does not represent net present value, ROI, or guaranteed revenue.

A financial investment decision requires appropriate financial measures.

### Effort Unit Consistency

Comparisons are meaningful only when effort is measured consistently.

Different teams should not combine incompatible effort units without normalization.

### Risk Simplification

The model uses three broad risk levels.

Real-world risk assessment may require separate dimensions for security, delivery, technical complexity, regulatory exposure, and operational continuity.

### Greedy Capacity Allocation

The dependency-aware greedy method is efficient for relatively small planning exercises.

It is not guaranteed to find the optimal combination of opportunities.

More complex portfolios may require mathematical optimization.

### Governance Simulation

The C++ and Java implementations simulate repository-governance decisions.

They do not connect to a remote Git hosting platform.

The SQL implementation models repository records and database-side governance rules, but it does not replace hosting-platform authorization, webhook validation, or actual Git operations.

Production systems should also enforce:

- Authentication.
- Role-based access control.
- Immutable audit records.
- Commit identity verification.
- Atomic state transitions.
- Concurrency controls.
- Secure API integration.
- Periodic policy review.

## Execution Requirements

| Implementation | Runtime | Dependencies |
|---|---|---|
| Python | Python 3.10+ | Standard library |
| JavaScript | Node.js 18+ | Node.js standard library |
| C++17 | C++17 compiler | Standard library |
| Java | Java 17 | Java standard library |
| PostgreSQL | PostgreSQL 15+ | PostgreSQL database |

Each source file provides an independent executable implementation of its respective domain responsibilities.

The PostgreSQL script creates the schema, inserts representative records, defines calculation and governance functions, and provides retrieval, aggregation, allocation, evaluation, and audit queries.

## Technical Learning Outcomes

The implemented system demonstrates the relationship between quantitative prioritization and software delivery governance.

The main technical concepts include:

- Weighted multi-criteria decision analysis.
- Three-point effort estimation.
- Confidence-adjusted valuation.
- Risk-adjusted opportunity scoring.
- Value-to-effort ratio analysis.
- Opportunity matrix classification.
- Sensitivity analysis.
- Dependency graph validation.
- Capacity-constrained selection.
- Event-driven state management.
- Asynchronous portfolio evaluation.
- Strongly typed domain modeling.
- Enterprise policy separation.
- Relational integrity enforcement.
- Recursive SQL queries.
- Transactional merge processing.
- Reviewer eligibility.
- Approval-state evaluation.
- Automated status-check enforcement.
- Repository branch protection.
- Audit-oriented decision recording.

The central distinction is that **Value vs Effort determines which opportunities deserve attention, while repository governance determines whether proposed software changes satisfy the conditions required for controlled integration.**
