# Repository Change Governance: Pull Requests, Code Review, Approvals, and Branch Protection

This project models four related but distinct mechanisms used to govern changes in a software repository:

| Area | Primary purpose | Decision represented |
|---|---|---|
| Pull Request | Propose and manage a changeset between branches | Whether a proposed change is active, closed, or merged |
| Code Review | Evaluate the technical quality and correctness of a changeset | Reviewer feedback and review state |
| Approvals | Record positive review decisions from eligible reviewers | Whether required reviewers have approved |
| Branch Protection | Enforce repository-level merge conditions | Whether the repository permits the protected branch to receive the change |

The relationship is:

`source branch → Pull Request → Code Review → Approval decisions → Branch Protection evaluation → Merge`

These mechanisms interact, but they are not interchangeable. A Pull Request is the change workflow. Code Review is the evaluation activity. An approval is a particular review decision. Branch Protection is the repository policy that determines which conditions must be satisfied before a protected branch can be modified.

## Pull Request Mechanics

A Pull Request connects a source branch containing proposed changes to a target branch that will receive those changes.

The model uses:

- source and target branches
- commits associated with the changeset
- draft and open states
- requested reviewers
- status checks
- review conversations
- base-branch synchronization
- merge conflicts
- closing and merging
- merge eligibility

A draft Pull Request represents work that has been opened for collaboration but is not yet ready for formal review. Opening it for review requires an actual changeset.

A new commit can invalidate assumptions about synchronization with the target branch. The implementations therefore track `synchronized_with_base` separately from the existence of commits.

A Pull Request can become blocked for reasons such as:

- merge conflicts
- missing synchronization
- failed required checks
- insufficient approvals
- unresolved conversations
- an invalid lifecycle state

Closing and merging are terminal states in the supplied models. A closed Pull Request cannot simply be modified as though it were still active, and a merged Pull Request cannot receive a new commit through the modeled workflow.

### Base-branch synchronization

A Pull Request may begin with a clean relationship to its target branch and later become stale as the target branch changes.

Conceptually:

`feature branch → Pull Request → target branch`

If the target branch advances or the Pull Request changes in a way that invalidates the current comparison, the model requires synchronization before merge eligibility is restored.

Merge conflicts are treated separately from synchronization. A Pull Request can require synchronization without currently containing a conflict, while an actual conflict prevents synchronization until it is resolved.

### Merge behavior

The implementations distinguish merge eligibility from the act of merging.

The evaluator first asks:

`Is the Pull Request eligible?`

Only after every applicable policy condition passes does it transition to:

`merged`

The Java implementation also models merge strategies:

- `MERGE_COMMIT`
- `SQUASH`
- `REBASE`

The selected strategy is a merge operation, not a review decision.

## Code Review

Code Review evaluates the proposed changeset. It is concerned with technical correctness, maintainability, defects, security implications, tests, and implementation quality.

The review model supports these states:

| Review state | Meaning |
|---|---|
| `commented` | Reviewer has provided observations without granting approval |
| `approved` | Reviewer accepts the reviewed changes |
| `changes_requested` | Reviewer considers modification necessary |
| `dismissed` | Previous review decision is no longer active |

A review belongs to a particular Pull Request and reviewer. The Python, JavaScript, C++, and Java implementations prevent the author from acting as an independent reviewer.

The SQL model adds review requests and review records separately. Requesting a review establishes who is expected to evaluate the change; submitting a review records the evaluation itself.

### Inline review discussions

Review comments are attached to a file and line in the PostgreSQL model.

This provides a concrete distinction between:

- the Pull Request containing a changeset
- the review evaluating it
- the comment discussing a specific implementation detail

A conversation can remain unresolved even when the review itself exists. The repository policy may require those conversations to be resolved before merge.

### Review quality

A useful review should remain within the scope of the proposed change. Relevant criteria include:

- correctness
- security boundaries
- error handling
- test coverage
- API compatibility
- maintainability
- performance implications
- unintended behavior

A reviewer should distinguish defects that require modification from optional improvements that do not justify blocking the change.

A common failure mode is treating every comment as an approval or treating approval as evidence that every discussion is resolved. The models intentionally keep these concepts separate.

## Approvals

An approval is a review decision with the `approved` state.

It is not equivalent to a Pull Request being mergeable.

For example, a Pull Request can have two approvals while still being blocked by:

- a failed security check
- an unresolved conversation
- a merge conflict
- stale synchronization
- another branch-protection condition

The governance relationship is therefore:

`reviewer evaluation → approval decision → policy evaluation`

### Reviewer eligibility

The examples require reviewers to be explicitly requested and prohibit self-review.

The SQL trigger enforces this at the database level. The application implementations enforce equivalent rules through validation and exceptions.

In a production repository, eligibility may depend on additional organization rules such as ownership of sensitive components, team membership, required expertise, or separation of duties.

### Stale and dismissed approvals

An approval is a decision about a particular reviewed state of a changeset. If significant changes are introduced afterward, a governance system may require the previous approval to be reconsidered.

The models represent the underlying concept by separating commits, review records, synchronization state, and policy evaluation.

A dismissed approval should not be counted as an active approval. Likewise, a review marked `changes_requested` is not an approval.

This distinction prevents the simple existence of a historical review record from being interpreted as current authorization to merge.

## Branch Protection

Branch Protection operates at repository policy level.

It does not create the Pull Request and does not perform the technical review. Instead, it defines conditions that must be satisfied before a protected branch can accept a change.

The examples configure the `main` branch with:

- two required approvals
- required `build`, `tests`, and `security` checks
- resolved review conversations
- linear-history requirements
- no direct pushes
- no force pushes
- no branch deletion

### Protected branches

The SQL schema associates protection rules with a specific branch rather than with an individual Pull Request.

This is important because the same repository policy can govern many Pull Requests targeting `main`.

The Pull Request evaluator obtains the target branch and evaluates the policy associated with that branch.

### Required status checks

Status checks are independent signals produced by automated validation.

The model treats a missing required check as a failure rather than assuming that absence means success.

For example:

`build = passed`

`tests = passed`

`security = missing`

results in a blocked merge when all three are required.

This fail-closed behavior is important for repository governance because an unavailable security check should not silently become equivalent to a successful security check.

### Required reviews

Branch Protection can require a minimum number of approvals.

The number alone does not constitute a complete review policy. The underlying reviews still need to satisfy reviewer eligibility rules.

The governance engine therefore counts active approval decisions rather than simply counting review records.

### Conversation requirements

A protected branch may require all relevant review conversations to be resolved.

This creates an important distinction:

`approved review ≠ all discussions resolved`

A Pull Request can contain an approval while a separate inline discussion remains unresolved.

The policy evaluator checks both conditions independently.

### Direct pushes and force pushes

Direct-push restrictions prevent users from bypassing the Pull Request workflow for a protected branch.

Force-push restrictions protect branch history from destructive rewriting.

These controls address repository governance rather than review quality. A technically correct code review does not justify bypassing the repository's protected-branch policy.

### Branch deletion

Deletion restrictions protect the existence of important integration branches.

The database stores branch deletion policy separately from Pull Request state because branch lifecycle is a repository concern rather than a review concern.

### Linear history

The policy model includes a linear-history requirement because some repositories require integration history to avoid merge commits or other non-linear structures.

The selected merge strategy remains a separate concern. A governance engine can require a linear history while the actual repository integration mechanism determines how that history is produced.

### Administrator and bypass behavior

The examples deliberately model ordinary enforcement rather than treating administrative privilege as an automatic bypass.

In a production system, bypass rules should be explicit, auditable, and narrowly scoped. A bypass should produce an auditable governance event rather than silently ignoring protection.

## Python Implementation

The Python implementation models the repository workflow using dataclasses, enumerations, dictionaries, sets, lists, validation, and explicit exceptions.

`PullRequest` owns the lifecycle and changeset behavior. It tracks commits, requested reviewers, reviews, status checks, conversations, conflicts, and synchronization.

`BranchProtection` contains repository policy.

`MergeEvaluator` evaluates policy without mixing the policy definition with the Pull Request's internal state.

The scenario deliberately creates an initially blocked merge because one review conversation remains unresolved. Resolving that conversation makes the Pull Request eligible.

The final attempted post-merge commit demonstrates an immutable terminal state.

## JavaScript Implementation

The JavaScript implementation uses an event-driven design built around Node.js `EventEmitter`.

Events such as:

- `opened`
- `commitAdded`
- `reviewRequested`
- `reviewSubmitted`
- `statusChanged`
- `conversationResolved`
- `synchronized`
- `merged`

represent changes in repository workflow state.

This design is useful for systems that need to react to repository events rather than repeatedly polling an entire object.

`Map` stores reviews and checks, while `Set` represents requested reviewers and unresolved conversations.

The governance policy is independent of the Pull Request. This separation allows one policy object to evaluate multiple Pull Requests targeting the same protected branch.

## C++ Implementation

The C++ implementation treats merge eligibility as a repository governance engine.

The central objects are:

- `PullRequest`
- `Review`
- `BranchProtection`
- `GovernanceEngine`
- `Evaluation`

The engine returns an explicit collection of blocking conditions instead of only returning a boolean. This makes policy failures observable and suitable for administrative tooling.

The implementation uses standard-library containers:

| Container | Purpose |
|---|---|
| `vector` | Ordered commits and review comments |
| `map` | Reviews and status-check results |
| `set` | Requested reviewers and required checks |

The C++ implementation also models conflict introduction and resolution independently from base synchronization. This reflects the fact that conflict resolution and branch synchronization are related operations but not identical state properties.

Exceptions provide fail-fast behavior for invalid lifecycle operations such as modifying a merged Pull Request.

## Java Implementation

The Java implementation uses explicit domain types to model enterprise repository governance.

Java records represent immutable value-oriented objects such as:

- `Commit`
- `Review`
- `StatusCheck`
- `BranchProtectionPolicy`
- `MergeDecision`

The `PullRequest` class represents mutable workflow state.

The `MergeEligibilityService` separates policy evaluation from the domain object. This is useful in enterprise applications where multiple repository workflows may share the same governance service.

Java streams are used to count active approvals:

`approved reviews → approval count → branch-protection evaluation`

The implementation also models merge strategies with an enum rather than representing them as unrestricted strings.

Failure states use exceptions so invalid operations such as modifying a merged Pull Request or merging with unresolved policy blockers cannot silently succeed.

## PostgreSQL Model

The PostgreSQL implementation persists the governance model relationally.

The core relationships are:

`repository → branch`

`repository → pull_request`

`pull_request → pull_request_commit → commit`

`pull_request → review_request`

`pull_request → review → review_comment`

`pull_request → status_check`

`branch → branch_protection → required_status_check`

This structure prevents different concepts from being collapsed into one large table.

### Database-level enforcement

The database enforces several rules directly:

- unique repository names
- unique developer usernames and email addresses
- unique branches within a repository
- unique Pull Request numbers within a repository
- valid Pull Request states
- valid review states
- positive comment line numbers
- non-negative unresolved conversation counts
- valid commit SHA format
- prevention of self-review
- prevention of reviews from unrequested reviewers
- merge eligibility through a database trigger

The `merge_eligibility()` function uses CTEs to evaluate policy conditions as a database operation.

The merge trigger prevents an application from bypassing the database's governance rules simply by updating a Pull Request to `merged`.

### Transactional behavior

The final SQL transaction synchronizes the Pull Request, clears the modeled unresolved-conversation condition, performs the protected merge, and records a merge event.

The transaction ensures these changes are treated as one unit of database work.

If the protected merge fails, PostgreSQL can roll back the transaction rather than leaving a partially updated governance state.

## Merge Eligibility Model

The implementations converge on the following policy model without treating its components as identical:

| Condition | Owned by |
|---|---|
| Source and target branches | Pull Request |
| Changeset commits | Pull Request |
| Reviewer evaluation | Code Review |
| Positive reviewer decision | Approval |
| Minimum approval count | Branch Protection |
| Required automated checks | Branch Protection |
| Conversation-resolution requirement | Branch Protection |
| Conflict state | Pull Request / integration state |
| Protected target branch | Branch Protection |
| Final merge authorization | Branch Protection evaluation |

A simplified decision model is:

`Merge = Open + Valid Changeset + No Conflict + Synchronized + Required Approvals + Required Checks + Required Conversations Resolved + Protected-Branch Rules Satisfied`

Failure of any mandatory condition blocks the merge.

## Failure and Edge-Case Handling

The examples intentionally cover conditions that commonly cause governance errors:

- Pull Request without commits
- self-review
- reviewer not explicitly requested
- failed status check
- missing status check
- insufficient approvals
- unresolved conversations
- merge conflicts
- stale base synchronization
- modifying a closed Pull Request
- modifying a merged Pull Request
- invalid branch relationships
- invalid commit identifiers
- invalid review states
- negative approval requirements
- duplicate relational identifiers

The implementations favor explicit failure rather than silently accepting invalid repository state.

## Security and Governance Considerations

Repository governance is a security control as well as a development workflow.

Important controls include:

- least-privilege branch access
- mandatory independent review
- protected default branches
- required security checks
- immutable or restricted history
- prevention of unauthorized direct pushes
- controlled force-push permissions
- auditable merge events
- separation between authorship and approval
- database-level integrity enforcement

Approval should not be treated as proof that a change is safe in every respect. It is one decision within a broader governance process.

Likewise, passing automated checks does not replace human review where organizational policy requires it.

## Performance and Design Trade-offs

The in-memory implementations use direct dictionary, map, and set lookups for reviewers, reviews, and checks. These structures avoid repeatedly scanning unrelated records.

The SQL schema indexes the access paths used by governance queries, particularly Pull Request state, review state, status checks, and Pull Request-to-commit relationships.

Excessive indexing would increase write cost without necessarily improving governance queries, so indexes are limited to meaningful lookup paths.

The policy evaluator intentionally returns all detected blockers in the application implementations rather than stopping after the first failure. This improves diagnostics at the cost of evaluating multiple conditions.

The PostgreSQL implementation places critical merge enforcement inside the database. This improves integrity when multiple applications can access the same repository data, although database policy logic must then be maintained consistently with application-level policy behavior.

## Repository Governance State Model

Plain-text state flow:

`DRAFT`
`  ↓`
`OPEN`
`  ├── review requested`
`  ├── code review`
`  ├── approval decisions`
`  ├── status checks`
`  ├── conversation resolution`
`  ├── base synchronization`
`  ├── conflict resolution`
`  ↓`
`MERGE ELIGIBILITY`
`  ├── blocked → remain OPEN`
`  └── eligible → MERGED`

An alternative terminal path is:

`OPEN → CLOSED`

A closed Pull Request is not treated as a mergeable changeset.

The model therefore keeps workflow state, review decisions, and repository policy distinct while allowing them to participate in one controlled merge decision.
