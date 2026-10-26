# Git and Software Workflow Governance

## Scope

This project models Git repository development as a controlled workflow from a proposed code change to an eligible merge.

The four central areas are deliberately separated:

| Area | Responsibility |
|---|---|
| Pull Request | Proposes a changeset from a source branch toward a target branch |
| Code Review | Evaluates the proposed changes through reviews and discussions |
| Approvals | Records explicit reviewer decisions and determines whether review requirements are satisfied |
| Branch Protection | Enforces repository-level conditions before changes can enter a protected branch |

The relationship is:

`Repository → Branches → Commits → Pull Requests → Reviews → Review Comments → Conversations → Status Checks → Protection Policies → Merge Eligibility → Merge`

A Pull Request is the workflow container. Code Review evaluates its content. Approvals are review decisions tied to a particular revision. Branch Protection supplies repository governance rules that determine whether the Pull Request can be merged.

## Pull Request Lifecycle

A Pull Request connects a source branch with a target branch.

Typical state transitions are:

`Draft → Open → Merged`

or:

`Draft → Open → Closed → Open → Merged`

A Pull Request can also remain closed without being merged.

The implementations model these important mechanics:

- Source and target branches are explicitly stored.
- The Pull Request author is separate from reviewers.
- Commits are associated with the proposed changeset.
- Draft Pull Requests can be converted into ready Pull Requests.
- Synchronization records whether the Pull Request reflects the current source branch.
- A Pull Request can contain review conversations and automated status checks.
- Merge strategy is selected only after merge conditions are evaluated.
- Closing and reopening are distinct state transitions.
- A new source commit can invalidate the synchronized state and requires re-evaluation.

A Pull Request is therefore not itself an approval. It is the object through which a proposed branch change moves through review and repository governance.

### Branch Synchronization

The source branch may change while a Pull Request is under review.

The Python, JavaScript, C++17, and Java 17 implementations represent synchronization explicitly. The PostgreSQL model stores `head_sha` and `synchronized` so eligibility can be evaluated against a known revision.

This distinction matters because an approval for one revision should not automatically authorize an unrelated later revision.

### Merge Strategies

The implementations model three common strategies:

| Strategy | Effect |
|---|---|
| Merge | Preserves source commits and creates a merge-oriented integration |
| Squash | Represents the Pull Request as a consolidated target-branch commit |
| Rebase | Represents source commits as being reapplied in a linear history |

Branch protection can restrict which strategies are permitted.

## Code Review

Code Review is the evaluation process applied to the proposed changes.

The review model contains four review states:

| Review state | Meaning |
|---|---|
| Commented | Reviewer has feedback without approving or blocking the change |
| Approved | Reviewer accepts the current revision |
| Changes requested | Reviewer identifies a condition that must be addressed |
| Dismissed | A previous review decision is no longer active |

Review comments are associated with individual reviews. A requested-change review requires meaningful review text in the implementations.

Review quality is represented through:

- reviewer identity
- exact Pull Request revision
- review state
- review comments
- discussion resolution
- reviewer eligibility
- current versus stale decisions

The model prevents the Pull Request author from approving the author's own change.

A review should be interpreted in the context of the revision that was reviewed. If the Pull Request head changes, a previous approval can become stale.

### Review Discussions

A discussion represents an unresolved review issue.

The governance model counts unresolved conversations separately from approval decisions. This is important because a Pull Request can have sufficient approvals while still failing a policy that requires every review conversation to be resolved.

The workflow therefore distinguishes:

`Review decision ≠ Conversation resolution`

A reviewer can approve the current revision while a separate discussion remains unresolved.

## Approvals

Approvals represent explicit review decisions, not the existence of a Pull Request.

The examples use two required approvals for the protected `main` branch.

An approval is associated with:

- reviewer
- Pull Request
- reviewed commit SHA
- submission time
- review state

The merge evaluator considers the latest review from each reviewer. A newer review can supersede an older decision.

For example:

`Approved at SHA A → new commit B → approval for SHA A is stale`

The PostgreSQL implementation explicitly demonstrates this by comparing `reviews.commit_sha` with `pull_requests.head_sha`.

### Stale Approvals

Stale approvals are important because the code being merged may differ from the code that was approved.

The implementations therefore count approvals only when:

`reviewed SHA = current Pull Request head SHA`

This prevents an old approval from satisfying a policy after a new revision is submitted.

### Dismissed Approvals

A dismissed review does not count as an approval.

The review state is retained for audit purposes rather than deleted. This preserves the historical decision while preventing it from satisfying the current merge policy.

### Reviewer Eligibility

The examples enforce a basic reviewer rule:

`Pull Request author cannot approve the author's own Pull Request`

Enterprise systems can extend this with repository membership, team ownership, path-based ownership, separation-of-duty requirements, and role-based approval rules.

## Branch Protection

Branch Protection is repository-level governance applied to a target branch.

It is distinct from Code Review because it does not itself evaluate the quality of the code. It defines conditions that must be satisfied before the branch accepts a merge.

The examples model:

- required approvals
- required status checks
- required conversation resolution
- direct-push restrictions
- force-push restrictions
- branch-deletion restrictions
- linear-history requirements
- permitted merge strategies

A protected branch can therefore require:

`2 approvals + tests passed + security scan passed + discussions resolved + permitted merge strategy`

before a Pull Request becomes merge-eligible.

### Required Status Checks

Status checks are automated signals attached to a specific Pull Request revision.

Examples include:

- unit tests
- security scans

A status check is valid for merge evaluation only when it applies to the current Pull Request head.

This prevents a successful test result for an older revision from being treated as evidence about newer code.

### Direct Push Restrictions

A protected branch can prohibit direct modification outside the Pull Request workflow.

This establishes a governance boundary:

`Developer change → Pull Request → Review → Required checks → Approval → Protected merge`

The policy is stored separately from the Pull Request itself.

### Force-Push Restrictions

Force pushes can rewrite branch history. A protected branch can therefore prohibit them to preserve review and audit continuity.

The domain model stores `allow_force_push` or its equivalent so the restriction is explicit rather than implied.

### Branch Deletion Restrictions

A protected branch may also prohibit deletion. This prevents accidental removal of important integration branches such as `main` or release branches.

### Linear History

A branch policy can require linear history.

This affects which merge strategies are acceptable and can be represented separately from approval requirements. A Pull Request can satisfy review requirements while still failing a history policy.

## Python Implementation

The Python program provides a complete in-memory repository workflow model.

Its main domain objects are:

- `Repository`
- `Branch`
- `Commit`
- `PullRequest`
- `Review`
- `StatusCheck`
- `BranchProtection`

Python `Enum` classes represent workflow states and merge strategies.

The `Repository` service manages branch creation, commits, Pull Requests, reviews, checks, synchronization, conversation resolution, eligibility evaluation, closing, reopening, and merging.

The merge evaluator performs several independent checks:

1. Pull Request state
2. Presence of commits
3. Source synchronization
4. Current requested changes
5. Current approvals
6. Required status checks
7. Conversation resolution
8. Permitted merge strategy

The example first creates a blocked Pull Request and then satisfies the missing conditions before performing a squash merge.

The implementation uses SHA-like identifiers for commit tracking. The identifiers are sufficient for the simulation but are not intended to reproduce Git's complete object model.

## JavaScript Implementation

The JavaScript implementation uses an event-driven repository model.

`EventEmitter` publishes events such as:

- branch creation
- commit creation
- Pull Request creation
- review submission
- status-check updates
- Pull Request synchronization
- Pull Request merge

This separates workflow state mutation from audit processing.

JavaScript `Map` and `Set` structures provide efficient lookup for repositories, branches, users, reviews, required checks, and permitted strategies.

The asynchronous workflow uses `setImmediate` to represent non-blocking event processing. The example remains dependency-free and can run in a standard Node.js environment.

The policy evaluator computes current approvals using the latest review per reviewer. It also binds approvals and checks to the current Pull Request head.

## C++17 Implementation

The C++17 program treats merge eligibility as a repository-governance engine.

The domain uses:

- `struct` records for commits, reviews, branches, checks, and policies
- `enum class` for workflow states
- `std::map` for indexed repository objects
- `std::set` for users and required checks
- `std::optional` for an optional merge strategy
- exceptions for invalid state transitions

The `RepositoryGovernance` class centralizes policy enforcement.

The eligibility engine evaluates:

- Pull Request state
- synchronization
- current review decisions
- approval count
- required checks
- unresolved conversations
- allowed merge strategies

The program intentionally performs eligibility evaluation before changing the protected branch. This provides a clear transactional boundary at the application level.

For a review collection of size `R` and status-check collection of size `S`, one eligibility evaluation is approximately `O(R + S)` in the straightforward in-memory implementation.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented domain model.

Java records represent immutable historical values such as:

- `Commit`
- `Review`
- `StatusCheck`
- `ProtectionPolicy`

The `RepositoryService` coordinates repository operations, while `ReviewPolicy` separates reviewer eligibility from Pull Request state management.

The `MergeEligibility` value object keeps policy results separate from mutation operations.

The workflow explicitly represents:

`Draft → Open → Merged`

and prevents operations such as review submission on non-open Pull Requests.

Java streams are used for approval and status-check evaluation, while mutable collections remain encapsulated inside domain services.

The enterprise design emphasizes separation of responsibilities:

| Component | Responsibility |
|---|---|
| `Branch` | Stores branch commit state |
| `PullRequest` | Stores proposed-change state |
| `ReviewPolicy` | Determines reviewer eligibility and review blocking |
| `ProtectionPolicy` | Defines target-branch governance |
| `RepositoryService` | Coordinates workflow operations |
| `MergeEligibility` | Carries policy evaluation results |

## PostgreSQL Model

The PostgreSQL implementation provides a relational representation of the complete workflow.

The core relationships are:

`repositories`
→ `branches`
→ `commits`

and:

`pull_requests`
→ `pull_request_commits`
→ `reviews`
→ `review_comments`

with:

`pull_requests`
→ `status_checks`

and:

`branches`
→ `branch_protection_policies`
→ `required_status_checks`
→ `allowed_merge_strategies`

Primary keys and foreign keys enforce entity relationships.

Unique constraints prevent duplicate repository names, branch names within a repository, commit identifiers within a repository, and duplicate required checks or merge strategies.

Check constraints enforce valid quantities and non-empty values.

## PostgreSQL Merge Evaluation

The `evaluate_merge_eligibility` function performs policy evaluation inside PostgreSQL.

It evaluates:

- Pull Request state
- current head SHA
- synchronization
- latest reviewer decisions
- approval requirements
- requested changes
- required status checks
- unresolved conversations
- allowed merge strategies

The query uses `DISTINCT ON` to identify the latest review for each reviewer.

This is particularly important for approval semantics because a reviewer can submit a new decision after a previous approval.

The result is returned as rows containing:

| Column | Meaning |
|---|---|
| `eligible` | Whether the condition is satisfied |
| `reason` | Explanation for a failed or successful evaluation |

## PostgreSQL Transactional Merge

The `merge_pull_request` function checks eligibility before changing the Pull Request state.

The sample execution wraps the operation in:

`BEGIN → merge_pull_request(...) → COMMIT`

If the merge function raises an exception, PostgreSQL can roll back the transaction.

This separates policy evaluation from successful state mutation and protects against partially applied workflow changes.

## Failure Conditions

The implementations intentionally model common failure conditions.

| Failure | Effect |
|---|---|
| Unknown branch | Operation rejected |
| Unknown reviewer | Review rejected |
| Self-approval | Approval rejected |
| Empty commit message | Commit rejected |
| Draft PR review | Review rejected |
| Requested changes without explanation | Review rejected |
| Stale approval | Does not satisfy current approval count |
| Missing required check | Merge blocked |
| Failed required check | Merge blocked |
| Unresolved conversation | Merge blocked when required |
| Unauthorized merge strategy | Merge blocked |
| Unsynchronized source branch | Merge blocked |
| Missing commits | Merge blocked |

These failures distinguish workflow correctness from merely storing repository data.

## Security Considerations

Repository governance should be enforced at the authoritative repository service rather than relying on client-side checks.

Important controls represented by the model include:

- protected-branch restrictions
- reviewer eligibility
- prevention of self-approval
- commit-specific approval decisions
- required automated checks
- restricted merge strategies
- force-push restrictions
- branch-deletion restrictions
- auditable review records

Real deployments should also protect credentials, enforce authentication and authorization, retain immutable audit events, and ensure that policy changes themselves are permission-controlled.

No credentials or access tokens are stored in these examples.

## Performance Considerations

The in-memory implementations use hash-based collections for branch, Pull Request, user, and policy lookup.

The PostgreSQL implementation adds indexes where query patterns justify them:

- target branch and Pull Request state
- reviews by Pull Request and commit
- status checks by Pull Request and commit
- unresolved review comments

The review evaluation scans the current Pull Request's review history and required checks. For very large repositories, review and check histories should be indexed and queried by Pull Request and revision.

The database model avoids indiscriminate indexing because every additional index increases write and storage costs.

## Practical Workflow

A representative protected-branch workflow is:

`Developer creates branch`
        |
        v
`Commits changes`
        |
        v
`Opens Draft Pull Request`
        |
        v
`Marks Pull Request ready`
        |
        v
`Code Review`
        |
        +----> `Changes requested`
        |             |
        |             v
        |       `New commit / revision`
        |             |
        |             v
        |       `Re-review`
        |
        v
`Required status checks`
        |
        v
`Required approvals`
        |
        v
`Conversations resolved`
        |
        v
`Branch protection evaluation`
        |
        v
`Merge`
        |
        v
`Protected target branch`

The key control point is merge eligibility. A Pull Request can exist without being mergeable, a review can exist without being an approval, an approval can exist without satisfying the required count, and all approvals can exist while branch protection still blocks the merge.

## Distinctions

| Mechanism | Primary question |
|---|---|
| Pull Request | What changes are being proposed, from which branch, and toward which branch? |
| Code Review | What do reviewers think about the proposed changes? |
| Approval | Has an eligible reviewer explicitly accepted the current revision? |
| Status Check | Did an automated validation succeed for the current revision? |
| Branch Protection | What repository conditions must be satisfied before the target branch accepts the change? |
| Merge Eligibility | Are all current workflow and governance conditions satisfied? |
| Merge | Has the accepted changeset actually been integrated into the target branch? |

Keeping these concepts separate prevents a common governance error: treating the existence of a Pull Request or an approval as equivalent to permission to merge.

## Educational Focus

The five implementations approach the same repository-governance domain from different engineering perspectives:

| Implementation | Primary perspective |
|---|---|
| Python | In-memory workflow simulation and validation |
| JavaScript | Event-driven policy evaluation and audit events |
| C++17 | Explicit governance engine and algorithmic state evaluation |
| Java 17 | Enterprise domain modeling and policy services |
| PostgreSQL | Relational integrity, database-level policy evaluation, and transactions |

The implementations share the same conceptual domain while deliberately using different structures and execution models.

The resulting model treats Git workflow as a sequence of controlled state transitions rather than as a collection of unrelated commands.
