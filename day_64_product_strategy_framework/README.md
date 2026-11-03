# Repository Development and Governance Framework

## Scope

This project models repository-level development governance through five executable implementations.

The central relationship is:

Repository
→ Branches
→ Commits
→ Pull Requests
→ Reviews
→ Review Comments
→ Conversations
→ Status Checks
→ Branch Protection Policies
→ Approval Requirements
→ Merge Eligibility
→ Merge

The implementations deliberately separate four related mechanisms:

| Mechanism | Primary responsibility |
|---|---|
| Pull Request | Proposes a set of changes from a source branch toward a target branch |
| Code Review | Evaluates the proposed changes |
| Approvals | Records reviewer decisions about the proposed changes |
| Branch Protection | Enforces repository-level conditions before a protected branch can be modified |

These mechanisms interact, but they are not interchangeable.

## Pull Request Lifecycle

A Pull Request represents a proposed integration of changes.

A typical lifecycle is:

`draft → open → review → checks → eligible → merged`

Alternative terminal paths are:

`open → closed`

and:

`closed → reopened → open`

A draft Pull Request is visible as work in progress but is not treated as ready for normal merge processing.

An open Pull Request represents a proposed changeset. The proposed changes are represented independently from the current state of the target branch.

The source branch determines the branch from which the proposed changes originate.

The target branch determines where those changes are intended to be integrated.

The Pull Request therefore contains two important pieces of state:

1. The proposed changes.
2. The branch relationship against which those changes are evaluated.

A new commit modifies the proposed changeset. A change to the target branch changes the comparison context.

## Proposed Changes Versus Branch State

The source branch and target branch are mutable repository objects.

The Pull Request captures the proposed relationship between them.

A useful distinction is:

| Concept | Meaning |
|---|---|
| Source branch | Current branch containing the proposed work |
| Target branch | Branch intended to receive the work |
| Commit | Immutable change object |
| Changeset | Set of commits proposed by the Pull Request |
| Base state | Target-branch state against which the proposal is evaluated |
| Review | Human evaluation of the proposal |
| Status check | Automated evaluation of repository or application conditions |
| Merge eligibility | Final policy decision about whether integration is allowed |

A Pull Request is therefore not itself a branch and not itself a review.

## Pull Request Mechanics

The Python implementation models a Pull Request as a stateful domain object.

It records:

- source branch
- target branch
- author
- proposed commits
- requested reviewers
- reviews
- status checks
- base branch state
- lifecycle state

The JavaScript implementation uses `Map` and `Set` collections to model status checks and reviewer sets.

The C++ implementation uses STL containers to represent repository state and merge policy.

The Java implementation separates domain objects from the merge-eligibility service.

The PostgreSQL implementation represents each relationship through foreign keys and normalized tables.

## Synchronizing the Base Branch

A Pull Request can become stale relative to its target branch.

For example:

`main: A → B`

A feature Pull Request proposes:

`A → B → C`

If another Pull Request merges `D` into `main`, the target branch becomes:

`A → B → D`

The original Pull Request is now evaluated against a different target state.

The Python and JavaScript models explicitly track the target head captured when the Pull Request is created.

Synchronization updates that base reference.

Approvals may become stale after synchronization because reviewers previously evaluated a different comparison context.

## Merge Conflicts

A merge conflict occurs when the proposed changes and the current target branch cannot be safely combined under the selected merge operation.

The implementations intentionally do not implement a complete textual three-way merge engine. Instead, they model the governance boundary around conflict handling.

A production merge engine would need to compare:

`merge base + source changes + target changes`

and determine whether the resulting tree is unambiguous.

The governance layer should not treat a conflict as an approval problem. A reviewer can approve a change while the repository is still unable to integrate it automatically.

## Reopening and Closing Pull Requests

Closing a Pull Request ends the active proposal without integrating it.

The Python model supports reopening a closed Pull Request.

A merged Pull Request is treated differently because integration has already occurred.

This distinction prevents an already integrated change from being incorrectly returned to an ordinary open state.

## Merge Strategies

Three strategies are represented:

| Strategy | Repository effect |
|---|---|
| Merge commit | Creates a merge commit joining histories |
| Squash | Creates one resulting commit representing the Pull Request |
| Rebase | Replays the proposed commits onto the target history |

Branch protection can restrict which strategies are permitted.

A linear-history policy can reject merge commits because a merge commit introduces a non-linear graph structure.

The implementation therefore treats merge strategy as a governance input rather than merely a presentation preference.

## Code Review

Code Review evaluates the proposed changes.

It is distinct from the Pull Request itself.

A Pull Request provides the workflow container. Code Review provides an evaluation mechanism inside that workflow.

The review model supports:

- reviewer identity
- review state
- inline comments
- requested changes
- approval
- dismissal
- stale approval state
- resolved conversations

Review comments identify a file, line, reviewer, and discussion body.

A resolved conversation indicates that the associated discussion no longer requires active remediation under the configured policy.

## Review States

The supported review states are:

| State | Meaning |
|---|---|
| Commented | Reviewer provided feedback without approving or blocking |
| Approved | Reviewer accepts the proposed changes from a review perspective |
| Changes requested | Reviewer considers additional changes necessary |
| Dismissed | Previously recorded review decision is no longer active |

A review decision is separate from repository merge eligibility.

A reviewer can approve a Pull Request while required automated checks remain incomplete.

A reviewer can request changes while all automated checks are passing.

The final merge decision combines these independent signals.

## Review Quality and Scope

A review should evaluate the proposed changes rather than the entire repository indiscriminately.

The sample implementations demonstrate review scope through inline comments tied to specific files and line numbers.

Useful review criteria include:

- correctness
- security
- maintainability
- compatibility
- test coverage
- failure handling
- data integrity
- performance impact
- operational risk

The governance engine should not attempt to determine whether a code change is intellectually good. It should enforce objective repository rules and represent reviewer decisions.

## Review Failure Modes

The models account for several review-related failures:

- self-review
- unresolved conversations
- stale approvals
- dismissed approvals
- requested changes
- reviewers who are not requested
- insufficient independent approvals

The separation between reviewer identity and reviewer eligibility is important.

An arbitrary user submitting an approval should not automatically satisfy a protected-branch approval requirement.

## Approvals

An approval represents a review decision.

It does not represent unrestricted permission to modify the repository.

An approval is considered valid for merge eligibility only when the configured rules are satisfied.

The implementations consider:

- reviewer identity
- reviewer eligibility
- requested reviewer status
- approval state
- stale state
- dismissal state
- approval count

For example, if two approvals are required:

`valid approvals = 2`

is different from:

`total reviews = 2`

Two comments do not constitute two approvals.

One approval followed by a new commit may also become insufficient if the policy invalidates stale approvals.

## Stale Approvals

A significant governance rule is that a new changeset can invalidate a previous approval.

The implementations demonstrate:

`approved`
→ `new commit`
→ `stale approval`

This protects against a situation in which a reviewer approves one version of the proposed changes while a materially different version is later submitted.

The stale state is not the same as rejection.

It means that the previous approval cannot be counted as an active approval under the configured merge policy.

## Approval Eligibility

Approval requirements can be expressed as:

`active eligible approvals >= required approvals`

The PostgreSQL function calculates distinct reviewers rather than counting arbitrary review rows.

This prevents duplicate review records from artificially satisfying the approval threshold.

The model also prevents the Pull Request author from acting as their own reviewer.

## Branch Protection

Branch Protection is a repository-level enforcement mechanism.

It controls what conditions must be satisfied before a protected branch can receive changes.

The examples model:

- protected branches
- required approvals
- required status checks
- direct-push restrictions
- force-push restrictions
- branch deletion restrictions
- resolved-conversation requirements
- linear-history requirements
- allowed merge strategies
- administrator bypass configuration

Branch Protection is therefore broader than Code Review.

Code Review evaluates proposed changes.

Branch Protection decides which repository conditions must be satisfied before integration.

## Required Status Checks

Status checks represent automated conditions.

Examples include:

- unit tests
- security scans
- integration tests
- build validation

A status check can be:

`pending`

`passed`

`failed`

A protected branch can require specific checks.

The merge-eligibility algorithm verifies that every required check exists and has passed.

A passing reviewer approval cannot compensate for a failed required security scan when the repository policy requires that scan.

## Direct Push Restrictions

A protected branch can prohibit direct pushes.

This forces changes through a controlled integration path.

The governance relationship is:

`developer`
→ `source branch`
→ `Pull Request`
→ `review`
→ `status checks`
→ `branch protection`
→ `merge`

Direct-push restrictions protect the target branch from bypassing this workflow.

## Force-Push Restrictions

Force pushes can rewrite branch history.

On protected branches, this can destroy or replace history that other developers rely upon.

The data model therefore represents force-push permissions independently from direct-push permissions.

These are separate controls.

A repository can allow ordinary pushes while prohibiting history rewriting.

## Branch Deletion Restrictions

Branch deletion is also modeled independently.

The lifecycle of a feature branch can be:

`created → used by Pull Request → merged → optionally deleted`

A governance policy may prohibit branch deletion for protected branches even after a Pull Request is merged.

## Administrator Bypass

Administrator bypass is represented as an explicit policy.

It should not be inferred from administrator identity alone.

The policy controls whether administrators can bypass ordinary merge conditions.

This distinction makes bypass behavior auditable and configurable.

A secure governance system should record bypass operations because bypasses can weaken normal controls.

## Merge Eligibility

Merge eligibility is the intersection of independent conditions.

Conceptually:

`Merge Eligibility = PR State`
`AND Proposed Changes Exist`
`AND Valid Approvals`
`AND Required Checks Pass`
`AND Conversations Resolved`
`AND No Active Blocking Review`
`AND Permitted Merge Strategy`
`AND Branch Protection Conditions`

The C++ implementation explicitly produces a list of blocking reasons.

The Java implementation represents the decision through an immutable `MergeDecision` record.

The Python implementation returns a Boolean decision plus human-readable failure reasons.

The JavaScript implementation produces an evaluation object containing eligibility and reasons.

The PostgreSQL function returns relational rows describing eligibility and blocking conditions.

## Repository Domain Model

The complete conceptual model is:

`Repository`
→ `Branch`
→ `Commit`

`Repository`
→ `Pull Request`
→ `Review`
→ `Review Comment`

`Pull Request`
→ `Status Check`

`Protected Branch`
→ `Branch Protection Policy`
→ `Approval Requirements`
→ `Required Status Checks`

`Pull Request + Review State + Checks + Protection Policy`
→ `Merge Eligibility`

`Merge Eligibility`
→ `Merge Event`

This structure separates immutable change objects from mutable governance decisions.

## Python Implementation

The Python implementation uses dataclasses and enums for explicit domain modeling.

Important objects include:

- `Commit`
- `Branch`
- `ReviewComment`
- `Review`
- `StatusCheck`
- `BranchProtection`
- `PullRequest`
- `Repository`

The `Repository.merge_eligibility()` method combines review, approval, status-check, conversation, and branch-protection conditions.

The implementation also demonstrates approval invalidation when a new commit is added.

Exceptions are used for invalid state transitions such as modifying a merged Pull Request or attempting self-review.

## JavaScript Implementation

The JavaScript implementation uses a different engineering model.

`Map` is used for status checks and repository collections.

`Set` is used for:

- requested reviewers
- valid approvers
- required status checks
- allowed merge strategies

The implementation is event-oriented in structure because state changes are represented through explicit operations such as adding commits, adding reviews, setting checks, synchronizing the base, and merging.

Validation errors are represented through a custom `ValidationError` class.

The JavaScript implementation is executable in a Node.js environment without third-party packages.

## C++17 Implementation

The C++ implementation models the governance engine using:

- structs
- enums
- `std::map`
- `std::set`
- `std::vector`
- exception-based validation

The `MergeDecision` structure provides a deterministic list of merge blockers.

The C++ implementation emphasizes explicit state ownership and efficient lookup.

Reviewer membership and required checks use sets for efficient membership testing.

Repository objects use maps for direct lookup by branch or Pull Request identifier.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented service architecture.

Domain types include:

- `Commit`
- `Branch`
- `PullRequest`
- `Review`
- `ReviewComment`
- `StatusCheck`
- `BranchProtectionPolicy`

The `MergeEligibilityService` isolates policy evaluation from repository storage.

Java records are used for immutable value-oriented objects such as:

- `ReviewComment`
- `StatusCheck`
- `BranchProtectionPolicy`
- `MergeDecision`

The separation supports a service architecture in which persistence, policy evaluation, and workflow orchestration can evolve independently.

## PostgreSQL Implementation

The PostgreSQL model normalizes repository governance into relational entities.

Core tables include:

- `repositories`
- `repository_users`
- `branches`
- `commits`
- `branch_commits`
- `pull_requests`
- `pull_request_commits`
- `review_requests`
- `reviews`
- `review_comments`
- `status_checks`
- `branch_protection_policies`
- `required_status_checks`
- `merge_events`

Foreign keys enforce relationships.

Check constraints enforce valid numeric values and basic domain invariants.

Unique constraints prevent duplicate branch names, commit identifiers, Pull Request numbers, status checks, and requested reviewers.

## Database Integrity

The database contains triggers for important invariants.

Self-review is prevented by checking the Pull Request author before inserting or updating a review.

The same restriction is applied to review requests.

When a new Pull Request commit is recorded, existing approvals are marked stale.

This demonstrates an important distinction between:

`stored review history`

and:

`currently valid approval state`

The database therefore does not rely entirely on application code to maintain governance invariants.

## SQL Merge Evaluation

The `merge_eligibility()` PostgreSQL function evaluates:

- Pull Request state
- existence of proposed commits
- permitted merge strategy
- active eligible approvals
- required status checks
- unresolved conversations
- linear-history requirements
- active change requests

It returns both the Boolean eligibility result and a reason.

This structure supports reporting as well as application-level decision making.

## Transaction Handling

The SQL workflow uses a transaction for merge processing.

The intended sequence is:

`BEGIN`
→ evaluate eligibility
→ perform merge operation
→ record merge event
→ update Pull Request state
→ `COMMIT`

If an integrity or policy failure occurs, the transaction can be rolled back.

The merge event provides an audit record connecting the Pull Request, actor, strategy, and timestamp.

## Performance Considerations

The implementations use direct lookup structures where appropriate.

Python dictionaries provide average constant-time key lookup.

JavaScript `Map` and `Set` provide efficient key and membership operations.

C++ `std::map` and `std::set` provide logarithmic lookup and ordered storage.

Java `HashMap` and `HashSet` provide average constant-time lookup for normal workloads.

PostgreSQL indexes target common governance queries:

- Pull Requests by target branch and state
- reviews by Pull Request and state
- status checks by Pull Request
- unresolved comments
- branch commit ordering

The database model is normalized to avoid duplicating reviewer, branch, commit, and repository attributes across every governance record.

## Security Considerations

Repository governance is a security control as well as a development workflow.

Important controls include:

- no self-approval
- protected target branches
- required reviews
- required automated checks
- restricted direct pushes
- restricted force pushes
- resolved-review requirements
- explicit administrator bypass
- auditable merge events
- stale-approval handling

A policy engine should fail closed when a required control cannot be verified.

A missing required status check is treated as unsatisfied rather than assumed to be successful.

## Failure Handling

Representative failure states include:

| Failure | Expected behavior |
|---|---|
| Unknown branch | Reject Pull Request creation |
| Same source and target | Reject Pull Request creation |
| Self-review | Reject review |
| No proposed commits | Block merge |
| Insufficient approvals | Block merge |
| Stale approvals | Do not count stale approvals |
| Failed status check | Block merge |
| Missing status check | Block merge |
| Unresolved conversation | Block merge when required |
| Active change request | Block merge |
| Prohibited strategy | Block merge |
| Non-linear merge under linear policy | Block merge |
| Closed Pull Request | Reject ordinary merge |
| Merged Pull Request modification | Reject mutation |

## Distinguishing the Four Governance Areas

The four mechanisms can be represented as a control chain:

`Pull Request`
`    ↓`
`Proposes changes`

`Code Review`
`    ↓`
`Evaluates changes`

`Approval`
`    ↓`
`Records review decision`

`Branch Protection`
`    ↓`
`Enforces repository conditions`

`Merge Eligibility`
`    ↓`
`Determines whether integration is permitted`

A Pull Request can exist without an approval.

A review can exist without approval.

An approval can exist while merge eligibility is false.

Branch Protection can require conditions that are unrelated to human review, such as automated security checks or linear history.

This separation is essential for reliable repository governance.

## Practical Workflow

A realistic protected-branch workflow is:

`Developer`
→ creates feature branch
→ commits changes
→ opens Pull Request
→ requests reviewers
→ reviewers inspect changes
→ discussions are resolved
→ automated checks execute
→ approvals are collected
→ branch protection evaluates requirements
→ merge eligibility is calculated
→ permitted merge strategy is selected
→ merge event is recorded

If a new commit is added after approval:

`New commit`
→ changes proposed changeset
→ previous approval may become stale
→ review may be required again
→ status checks may run again
→ merge eligibility is recalculated

This prevents the repository from treating an older review decision as unconditional permission for a newer changeset.

## Limitations

The source implementations model governance rather than a complete version-control system.

They do not implement:

- complete Git object storage
- textual three-way merge algorithms
- binary conflict resolution
- network authentication
- repository hosting
- distributed event delivery
- signed commit verification
- cryptographic identity verification
- full CI/CD orchestration

The PostgreSQL model stores governance state and relationships but does not attempt to reproduce the complete internal data model of Git.

These limitations are deliberate because repository governance and source-control mechanics are separate technical layers.

## Educational Focus

The implementations demonstrate how the same governance model can be represented through different engineering paradigms.

| Implementation | Primary perspective |
|---|---|
| Python | Domain simulation and explicit workflow state |
| JavaScript | Collection-driven and event-oriented policy evaluation |
| C++17 | Explicit governance engine with STL data structures |
| Java 17 | Enterprise domain model and policy service separation |
| PostgreSQL | Relational integrity, workflow queries, triggers, and policy evaluation |

The common domain model allows the implementations to be compared without requiring them to be mechanically identical.

The key technical lesson is that proposed changes, review decisions, approvals, automated checks, repository policy, and final merge eligibility are separate states that must be combined deliberately rather than treated as one concept.
