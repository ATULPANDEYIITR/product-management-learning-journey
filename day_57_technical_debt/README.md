# Technical Debt: Measurement, Prioritization, and Repository Governance

## Scope

This project models technical debt as an engineering and management problem rather than as a synonym for bad code.

The implementations represent debt as a measurable liability with:

- a principal cost representing the work required to remediate it
- an interest cost representing recurring engineering friction
- business and operational impact
- probability of occurrence
- urgency
- security exposure
- affected software components
- an explicit owner
- a lifecycle state
- a remediation estimate
- a prioritization score

The repository-development domain provides the operational setting:

Repository → Branch → Commit → Pull Request → Review → Approval → Status Check → Branch Protection → Merge Eligibility

Technical debt is evaluated alongside this workflow because repository changes can introduce, document, or remediate debt.

The four governance concepts remain distinct:

| Area | Primary purpose |
|---|---|
| Pull Requests | Propose and integrate changes between branches |
| Code Review | Evaluate the quality, correctness, maintainability, and scope of proposed changes |
| Approvals | Record formal reviewer decisions that may satisfy review requirements |
| Branch Protection | Enforce repository-level conditions before protected branches can be changed |

A Pull Request provides the change workflow. Code Review evaluates the proposed work. Approvals express review decisions. Branch Protection enforces repository policy before merge. Technical debt is a separate engineering liability that can influence prioritization and, where an organization chooses, merge policy.

## Technical Debt Model

Technical debt is represented as a deliberate trade-off in which a team accepts present implementation cost or risk in exchange for another immediate benefit, such as faster delivery.

The model distinguishes debt from ordinary future work.

A normal feature request represents desired capability.

A technical debt item represents an existing condition that creates future cost, risk, or reduced engineering effectiveness.

Examples include:

- duplicated validation logic
- missing automated tests
- obsolete architecture
- temporary infrastructure
- undocumented operational procedures
- insecure legacy configuration
- compatibility workarounds
- obsolete dependencies
- manually repeated deployment steps

Technical debt is not automatically bad. A temporary shortcut can be rational when its business value exceeds its near-term remediation cost. The important requirement is that the trade-off is visible, owned, measured, and periodically reconsidered.

## Principal and Interest

The implementations use two important economic concepts.

### Principal

Principal is the estimated effort required to remove or substantially reduce the debt.

For example, if replacing a legacy validation layer requires 20 engineering hours, the remediation estimate is 20 hours.

Principal is normally a one-time remediation burden.

### Interest

Interest is the recurring cost created by leaving the debt unresolved.

Examples include:

- repeated debugging
- duplicated implementation effort
- slower feature development
- longer review cycles
- additional deployment work
- recurring production incidents
- increased testing effort
- security exposure
- architectural constraints

The Python, JavaScript, C++17, Java 17, and PostgreSQL implementations model monthly interest as engineering hours.

The model intentionally uses a simple linear projection rather than pretending that future debt cost can be predicted precisely.

## Causes of Technical Debt

The project distinguishes several causes.

| Cause | Typical mechanism | Resulting liability |
|---|---|---|
| Schedule pressure | A shortcut is accepted to meet a release date | Future remediation effort |
| Unclear requirements | Implementation is built around unstable assumptions | Rework |
| Architecture evolution | The system grows beyond its original structure | Structural constraints |
| Missing tests | Validation is deferred | Higher regression risk |
| Temporary workaround | A short-term solution becomes permanent | Maintenance burden |
| Knowledge gaps | A team chooses an unsuitable implementation | Refactoring requirement |
| Dependency aging | External libraries or infrastructure become obsolete | Upgrade and compatibility work |
| Organizational change | Ownership or operating models change | Documentation and operational debt |

The cause is recorded as context rather than used as the sole prioritization variable. A low-quality cause classification does not necessarily imply low business risk.

## Business Impact

Technical debt affects business performance through engineering systems.

A debt item can increase:

- feature lead time
- incident probability
- operational cost
- security exposure
- developer onboarding time
- review effort
- testing effort
- release risk
- infrastructure complexity

The relationship can be expressed as:

Business pressure
→ implementation shortcut
→ unresolved liability
→ recurring engineering interest
→ slower delivery or greater operational risk

The important distinction is that technical debt has a measurable consequence only when it affects future work, risk, cost, or system behavior.

## Prioritization Model

The source implementations calculate a decision score from several dimensions.

The risk component is:

`risk = impact × probability × 10 + urgency × 2 + security_exposure × 3`

The prioritization score is:

`priority = (monthly_interest × 4 + risk × 2 + security_exposure × 5) / remediation_hours`

This is a deliberately transparent heuristic.

It is not presented as a universal financial formula. An organization can change the weights to reflect its own economics and risk tolerance.

A high score means that unresolved debt produces substantial recurring cost or risk relative to the estimated remediation effort.

The model produces four operational priority levels:

| Score | Priority |
|---:|---|
| 0–19.99 | Low |
| 20–39.99 | Medium |
| 40–69.99 | High |
| 70+ | Critical |

Security exposure receives explicit weight because a small remediation effort can justify immediate action when the potential consequence is severe.

## Balancing Feature Work and Debt

A team cannot normally allocate all capacity to technical debt.

A realistic planning decision contains competing demands:

`Available Capacity = Feature Work + Technical Debt + Reliability + Operational Work`

The implementations demonstrate a configurable debt allocation ratio.

For example, with 80 engineering hours and a 30% debt allocation:

`Debt Capacity = 80 × 0.30 = 24 hours`

`Feature Capacity = 80 - 24 = 56 hours`

The allocation algorithm sorts debt by priority and selects complete remediation items that fit the available debt budget.

This is intentionally different from blindly selecting the oldest debt item.

Age can be useful context, but age alone does not measure business impact, security exposure, interest, or remediation value.

## Python Implementation

The Python program provides the most direct repository workflow simulation.

### Domain model

`TechnicalDebtItem` is a dataclass containing estimates, risk dimensions, ownership, lifecycle state, and affected components.

Enums make important states explicit:

- `DebtCategory`
- `DebtStatus`
- `Priority`
- `ReviewState`

`Repository` owns branches, debt records, Pull Requests, and branch protection policies.

`PullRequest` stores commits, reviews, status checks, synchronization state, conflicts, and associated debt.

### Validation

The Python implementation rejects:

- invalid effort estimates
- invalid impact or urgency values
- probabilities outside `0..1`
- invalid security exposure
- unknown branches
- duplicate branches
- unknown debt references
- invalid Pull Request source and target branches
- reviews against closed Pull Requests

This makes the domain model enforce its own invariants rather than relying only on callers.

### Merge evaluation

`evaluate_merge` combines workflow conditions with repository policy.

It checks:

- Pull Request state
- draft state
- merge conflicts
- base-branch synchronization
- required approvals
- requested changes
- required status checks
- unresolved conversations
- technical-debt thresholds
- author independence

The technical-debt threshold is a policy decision rather than a fundamental property of Pull Requests.

### Reporting

The Python implementation also writes a JSON report containing:

- portfolio metrics
- active item count
- principal hours
- remediation hours
- monthly interest
- weighted risk
- priority ranking

The report is written using standard-library file handling and validated after serialization.

## JavaScript Implementation

The JavaScript program emphasizes event-driven state changes.

`Repository` extends `EventEmitter` and publishes events when:

- debt is recorded
- a Pull Request is created
- a review is added
- a status check changes

This provides a useful architecture for systems where dashboards, audit logs, notifications, or policy services react to repository events.

### Maps and Sets

`Map` is used for:

- technical debt records
- Pull Requests
- status checks
- branch protection policies

`Set` is used for:

- branches
- affected components
- technical debt associated with a Pull Request
- required status checks

This provides efficient identifier-based lookups and prevents accidental duplicate membership.

### Asynchronous reporting

The report writer uses Node.js standard-library asynchronous file operations.

The generated JSON contains the calculated technical-debt ranking rather than a copy of internal object state.

The program removes the temporary report after validating it, keeping the demonstration self-contained.

### Policy evaluation

Merge eligibility is represented as a collection of explicit blocking reasons.

This is preferable to returning only a Boolean because engineering systems need to explain why an operation is blocked.

## C++17 Implementation

The C++17 implementation treats the repository as a governance engine.

`TechnicalDebt` encapsulates:

- financial-style principal
- recurring interest
- risk
- security exposure
- remediation effort
- priority calculation

`PullRequest` contains:

- commits
- reviews
- status checks
- associated debt
- synchronization state
- conflict state
- unresolved conversations

`BranchProtection` contains repository-level enforcement rules.

`RepositoryGovernanceEngine` coordinates the objects and evaluates merge eligibility.

### STL usage

The program uses:

- `std::vector` for ordered commits and reviews
- `std::map` for identifier-based domain storage
- `std::set` for unique branches and debt associations
- `std::sort` for priority ranking
- `std::count_if` for approvals
- `std::all_of` for required checks
- `std::reference_wrapper` for sorted references to stored debt items

The use of references for ranking avoids copying the complete debt objects.

### Failure handling

Invalid construction and invalid workflow operations raise standard exceptions.

The `main` function catches exceptions and returns a non-zero exit status.

This models a command-line governance service where invalid state should fail explicitly rather than silently producing a merge decision.

## Java 17 Implementation

The Java program uses an enterprise-oriented domain model.

Records represent immutable value objects such as:

- `Commit`
- `Review`
- `StatusCheck`
- `BranchProtectionPolicy`
- `MergeDecision`

`TechnicalDebtItem`, `PullRequest`, and service classes represent mutable domain state and business operations.

### Service separation

`RepositoryService` manages repository state and debt planning.

`MergeEligibilityService` evaluates whether a Pull Request satisfies configured merge conditions.

This separation prevents repository storage concerns from becoming mixed with policy evaluation.

### Explicit policies

Branch protection contains:

- required review count
- required status checks
- direct-push restrictions
- force-push restrictions
- deletion restrictions
- conversation requirements
- linear-history requirements
- administrator bypass policy
- technical-debt threshold

The program therefore treats policy as domain data rather than scattering Boolean conditions throughout the application.

### Immutable structures

Java records and defensive copies such as `List.copyOf` and `Set.copyOf` reduce accidental mutation of value objects.

Streams are used for:

- calculating approval counts
- identifying requested changes
- calculating debt rankings
- filtering active debt
- sorting remediation candidates

## PostgreSQL Implementation

The PostgreSQL script models the same domain as persistent relational data.

The schema contains separate entities for:

- repositories
- users
- branches
- commits
- technical debt
- debt components
- Pull Requests
- Pull Request commits
- Pull Request debt relationships
- reviews
- review comments
- conversations
- status checks
- branch protection policies
- approval requirements
- repository roles

This prevents the four governance areas from being collapsed into a single record.

### Relational relationships

The primary workflow is:

`Repository`
→ `Branches`
→ `Commits`
→ `Pull Requests`
→ `Reviews`
→ `Review Comments`

and:

`Pull Request`
→ `Status Checks`
→ `Conversations`
→ `Branch Protection`

Technical debt connects to the workflow through:

`Pull Request`
→ `Pull Request Debt`
→ `Technical Debt`
→ `Debt Components`

This allows a debt item to exist independently of any single Pull Request.

### Constraints

Database constraints enforce important invariants.

Examples include:

- unique repository names
- unique branch names within repositories
- unique commit SHAs within repositories
- positive effort estimates
- bounded impact
- bounded probability
- bounded urgency
- bounded security exposure
- valid Pull Request merge strategies
- valid review states
- valid debt categories
- valid lifecycle states

The database therefore rejects invalid values even when an application layer fails to validate them.

### Triggers

The debt-resolution trigger automatically maintains `resolved_at`.

The Pull Request branch trigger verifies that source and target branches belong to the same repository.

The Pull Request debt trigger prevents a Pull Request from referencing technical debt belonging to another repository.

These are integrity rules that are appropriate at the database boundary.

## Pull Request Lifecycle

A Pull Request is the mechanism used to propose changes.

Its lifecycle can include:

`Draft → Open → Review → Changes → Re-review → Eligible → Merged`

It can also transition from open to closed without merging and can be reopened according to repository workflow rules.

The model tracks:

- source branch
- target branch
- commits
- synchronization state
- conflicts
- status
- merge strategy
- associated debt

A Pull Request can remediate technical debt, introduce technical debt, or document a debt relationship.

This distinction is represented by `pull_request_debt.relationship`.

The available relationships are:

- `introduces`
- `remediates`
- `documents`

## Code Review

Code Review is the evaluation process applied to the proposed changes.

It is represented separately from Pull Request state.

A review has a reviewer and a state such as:

- pending
- approved
- changes requested
- commented
- dismissed

Review comments identify specific files and optional line numbers.

A discussion can remain unresolved even when a reviewer has otherwise expressed an approval.

This matters because approval and conversation resolution are separate controls.

### Review quality

A review should evaluate relevant technical properties such as:

- correctness
- maintainability
- test coverage
- security
- architectural consistency
- failure handling
- performance implications
- scope

Technical debt is relevant when a change increases or decreases future maintenance burden, but a review is not itself a debt record.

## Approvals

Approval represents a formal review decision.

The database and source implementations distinguish approval from general comments.

An approval can contribute toward a required review count.

Approval requirements can be affected by:

- reviewer eligibility
- required number of reviewers
- dismissed reviews
- stale review policy
- requested changes
- branch protection configuration

The important distinction is:

`Review = evaluation`

`Approval = formal positive decision`

A review comment does not automatically constitute approval.

A reviewer requesting changes does not become an approval simply because the Pull Request has otherwise passed automated checks.

## Stale and Dismissed Approvals

Approval state must be interpreted in relation to repository policy.

A change to the source branch can invalidate the assumptions behind an earlier approval. A governance system may therefore require re-review after significant changes.

The PostgreSQL model includes `dismissed_at` so an approval can remain historically auditable while no longer counting toward active merge eligibility.

This avoids deleting review history merely because a decision is no longer valid.

## Branch Protection

Branch Protection is repository-level enforcement.

It does not replace Pull Requests or Code Review.

The model includes controls for:

- required reviews
- required status checks
- direct-push restrictions
- force-push restrictions
- branch deletion restrictions
- conversation resolution
- linear history
- administrator bypass
- maximum permitted technical-debt score

A protected branch can therefore require conditions that an individual Pull Request must satisfy before merge.

### Governance boundary

The distinction is:

`Pull Request`
proposes a change.

`Code Review`
evaluates the change.

`Approval`
records a reviewer decision.

`Branch Protection`
enforces repository policy.

`Merge Eligibility`
combines the relevant workflow state and policy rules.

Technical debt can be one input into merge eligibility when an organization deliberately chooses to use debt thresholds as a governance control.

## Status Checks

Automated status checks represent machine-evaluated conditions.

The example uses:

- unit tests
- security scanning
- integration tests

A required failed check blocks merge.

This is different from code review because automated checks evaluate predefined machine-verifiable conditions, while reviewers evaluate broader technical and contextual properties.

## Merge Eligibility

Merge eligibility is not stored as an unconditional fact.

It is derived from current state.

A Pull Request can become ineligible after:

- a new commit
- a failed status check
- a new requested-change review
- an unresolved conversation
- a merge conflict
- loss of required approval
- branch-policy modification
- increased technical-debt exposure

The source implementations therefore evaluate eligibility from current state instead of treating a previous successful evaluation as permanent.

## Security Considerations

Technical debt can become a security liability when the debt affects credentials, dependencies, access controls, logging, cryptography, or deployment systems.

The examples explicitly model security exposure.

Security-related debt receives additional priority weight because the remediation value may be much larger than its raw engineering effort.

The repository governance model also separates administrator bypass from ordinary merge rules.

A bypass should be explicit, auditable, and narrowly scoped.

The examples do not treat administrative authority as permission to ignore every security or validation control.

## Performance Considerations

The in-memory implementations use hash-based collections where identifier lookup is common.

Priority ranking requires sorting active debt items:

`O(n log n)`

Direct lookup of a debt item or Pull Request through a map is approximately:

`O(1)` average case

The PostgreSQL implementation uses indexes for common access patterns such as:

- repository and debt status
- Pull Request target branch and status
- review state by Pull Request
- required status checks
- unresolved conversations

Indexes are not added indiscriminately. They correspond to expected filtering and reporting operations.

## Edge Cases

The implementations explicitly address several failure conditions.

### Invalid estimates

Negative or zero remediation effort is rejected.

### Invalid probability

Probability must remain within `0..1`.

### Unknown branch

Pull Requests cannot reference branches outside the repository.

### Same source and target

A Pull Request cannot merge a branch into itself.

### Unknown debt

A Pull Request cannot reference a non-existent debt item.

### Closed Pull Request

The Python and JavaScript models prevent new reviews from being added after closure.

### Merge conflicts

Conflicts block merge eligibility.

### Failed required check

A required failed status check blocks merge.

### Requested changes

An active change request blocks merge.

### Unresolved conversations

A branch policy can require all conversations to be resolved before merge.

### Excessive debt

A branch policy can reject a Pull Request whose associated debt exceeds the configured threshold.

## Technical Debt Lifecycle

The debt lifecycle used by the project is:

`Open → Planned → In Progress → Resolved`

An organization can also move an item to:

`Accepted`

Accepted debt is not the same as resolved debt.

Resolved means the underlying liability has been remediated.

Accepted means the organization has consciously decided to retain the liability under current conditions.

That distinction preserves governance history and prevents accepted debt from being confused with completed remediation.

## Failure Modes

Technical debt management can fail even when individual records are accurate.

Common failures include:

- recording debt without an owner
- assigning remediation estimates without evidence
- treating all debt as equally important
- prioritizing age instead of business risk
- allowing debt inventories to grow without review
- removing debt records when they become inconvenient
- counting a reviewer comment as an approval
- treating approval as permanent after source changes
- assuming passing tests means the repository has no technical debt
- using branch protection as a substitute for engineering judgment
- applying a fixed debt percentage without considering product risk

The implementations counter these problems through explicit ownership, scoring, lifecycle state, validation, and policy evaluation.

## Practical Decision Framework

A useful planning sequence is:

`Identify`
→ `Describe`
→ `Measure`
→ `Prioritize`
→ `Allocate`
→ `Remediate`
→ `Verify`
→ `Reassess`

Identification creates a visible debt item.

Description establishes what caused the liability and which components are affected.

Measurement estimates principal, interest, risk, and security exposure.

Prioritization compares the liability with available alternatives.

Allocation reserves realistic engineering capacity.

Remediation removes or reduces the underlying cause.

Verification confirms that the intended liability has actually been reduced.

Reassessment determines whether the remaining debt is still justified.

## Implementation Comparison

| Implementation | Primary engineering perspective | Main mechanisms |
|---|---|---|
| Python | Repository workflow simulation | Dataclasses, enums, validation, scoring, JSON reporting |
| JavaScript | Event-driven policy model | EventEmitter, Maps, Sets, asynchronous file handling |
| C++17 | Governance and merge engine | STL containers, algorithms, exceptions, explicit policy objects |
| Java 17 | Enterprise domain and service model | Records, immutable collections, services, streams, policy objects |
| PostgreSQL | Persistent relational governance model | Constraints, triggers, views, functions, indexes, transactions |

## Architectural Relationship

The complete model can be viewed as five connected layers:

`Repository State`
→ branches, commits, Pull Requests

`Human Evaluation`
→ reviews, comments, conversations, approvals

`Automated Evidence`
→ status checks

`Repository Policy`
→ branch protection and approval requirements

`Engineering Economics`
→ technical debt, risk, interest, remediation capacity

Merge eligibility is produced by the interaction of these layers rather than by any single object.

## Educational Focus

The source files are deliberately structured to show that technical debt is not merely a code-quality label.

The implementations connect software engineering economics with executable workflow behavior:

- debt is measurable
- risk can be quantified
- remediation consumes capacity
- Pull Requests provide change context
- reviews provide human evaluation
- approvals provide formal decisions
- status checks provide automated evidence
- branch protection enforces repository policy
- merge eligibility is derived from current state
- database constraints protect durable governance data

The result is a concrete model in which technical debt can be recorded, evaluated, prioritized, connected to development work, and incorporated into repository governance without confusing it with the distinct mechanisms of Pull Requests, Code Review, approvals, or branch protection.
