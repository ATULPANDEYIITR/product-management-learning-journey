# Product Strategy for Governed Software Delivery

## Scope

This project models Product Strategy as a structured system connecting product intent with engineering delivery controls.

The central product problem is repository governance. A software product needs a clear reason for using Pull Requests, code review, approvals, automated checks, and protected branches. These mechanisms are related, but they perform different jobs.

The implementations use one coherent scenario: a payment-platform engineering repository whose product strategy requires predictable, reviewable, and policy-compliant changes to the production branch.

The strategic hierarchy is:

Product Vision
|
+-- Mission
|
+-- Strategic Choices
|
+-- Goals and Metrics
|
+-- Delivery Workflow
    |
    +-- Pull Request
        |
        +-- Code Review
        |
        +-- Approval Decisions
        |
        +-- Automated Status Checks
        |
        +-- Branch Protection
        |
        +-- Merge Eligibility
        |
        +-- Merge

## Product Strategy Model

Product strategy answers five distinct questions:

| Element | Role in the implementation |
|---|---|
| Vision | Defines the desired long-term product direction |
| Mission | Defines the operational purpose of the product |
| Strategic choices | Establish explicit decisions about how the product will achieve its purpose |
| Goals | Convert strategy into measurable outcomes |
| Objectives and metrics | Provide evidence for whether strategic choices are producing the intended result |

The implemented strategy uses the following vision:

`Make repository change management predictable, reviewable, and safe.`

The mission is:

`Connect product intent with controlled engineering delivery.`

The strategy then chooses Pull Requests as the controlled entry point for repository changes, separates human review from repository enforcement, ties approvals to the exact reviewed commit, uses automated checks as objective evidence, and protects critical branches from uncontrolled writes.

This structure prevents a common product-strategy failure in which a collection of engineering controls exists without a clear relationship to product outcomes.

## Product Goals

The implementations track measurable goals rather than treating strategy as a collection of statements.

Example goals include:

| Goal | Metric | Target | Current |
|---|---|---:|---:|
| Review coverage | Production PRs reviewed | 95% | 92% |
| Compliant merges | Policy-compliant merges | 90% | 94% |
| Unresolved conversations | Unresolved conversations on merged PRs | 1% | 0.5% |

A strategy score is calculated by normalizing each current value against its target and capping individual contributions at `1.0`.

This is deliberately simple. It provides a consistent portfolio-level signal without pretending that unrelated product metrics have identical business meaning.

## Product Strategy and Engineering Governance

The four governance areas have separate responsibilities.

| Area | Primary question | Main mechanism |
|---|---|---|
| Pull Request | How is a proposed change introduced and managed? | Source branch, target branch, commits, lifecycle |
| Code Review | What do reviewers conclude about the proposed change? | Comments, review states, discussions |
| Approvals | Which eligible reviewers have accepted the reviewed change? | Commit-specific approval decisions |
| Branch Protection | What repository conditions must be satisfied before merge? | Required reviews, checks, restrictions and merge rules |

The relationship is:

`Pull Request -> Code Review -> Approval -> Branch Protection -> Merge Eligibility -> Merge`

A Pull Request is the workflow container.

Code Review evaluates the change.

Approvals represent specific review decisions.

Branch Protection enforces repository-level conditions.

Merge Eligibility combines those conditions into a final decision.

## Pull Request Lifecycle

A Pull Request proposes a change from a source branch into a target branch.

The implementation represents:

- Source branch
- Target branch
- Pull Request number
- Author
- Title
- Commit sequence
- Draft state
- Open state
- Closed state
- Merged state
- Base synchronization
- Merge strategy

The normal lifecycle is:

`Draft -> Open -> Review -> Approved/Changes Requested -> Eligible -> Merged`

A Pull Request can also move from `Open` to `Closed` without merging and can later be reopened according to repository workflow rules.

### Source and Target Branches

The source branch contains the proposed work.

The target branch receives the change if all merge requirements are satisfied.

The implementations prevent a Pull Request from using the same branch as both source and target.

The PostgreSQL model represents these relationships through foreign keys rather than storing branch names as unrestricted text inside the Pull Request record.

### Changesets and Commits

A Pull Request contains an ordered changeset.

The implementations associate Pull Requests with commits and identify the latest commit as the current head.

This is important for approval semantics because an approval against an earlier commit cannot automatically be assumed to approve a later version of the change.

### Draft Pull Requests

A draft Pull Request represents work that is visible but not ready for merge.

The Python, JavaScript, and Java models explicitly prevent a draft Pull Request from satisfying merge eligibility.

The database model stores the draft state using `is_draft`.

### Base-Branch Synchronization

A Pull Request can become stale relative to its target branch.

The JavaScript model explicitly tracks synchronization time and state. The database stores `base_synchronized_at`.

Synchronization is distinct from approval. Updating a branch relationship does not itself constitute human acceptance of the changes.

### Merge Conflicts

A merge conflict is a failure to produce a clean merge from the current branch state.

The governance models do not pretend that branch protection resolves textual conflicts. Merge eligibility is evaluated after the change is in a state that can be merged under the repository's selected strategy.

This distinction prevents mergeability from being confused with review approval.

### Reopening and Closing

Closing a Pull Request terminates its active workflow without necessarily merging it.

Reopening restores an active proposal subject to the current repository state.

A merged Pull Request is treated as a terminal state in the source implementations. This avoids silently changing historical merge records.

## Code Review

Code Review is the evaluation mechanism applied to the changes proposed by a Pull Request.

It is distinct from the Pull Request itself.

The review model supports:

- Commented reviews
- Approved reviews
- Changes requested
- Dismissed reviews
- Reviewer identity
- Reviewed commit
- Review timestamp
- Inline comments
- Review conversations

### Review Quality

A review should evaluate the actual change rather than merely confirm that a Pull Request exists.

The model records the exact commit reviewed. This allows the system to determine whether a later commit changed the object that was previously evaluated.

Review quality can involve:

- Correctness
- Security
- Maintainability
- Product-policy alignment
- Test adequacy
- Operational risk
- Scope control

These criteria are represented as domain concepts rather than as generic programming-language examples.

### Inline Comments

The PostgreSQL model stores:

- File path
- Line number
- Comment body
- Associated review
- Associated commit

This permits comments to remain associated with the exact version of the code under discussion.

### Review Discussions

A discussion is represented separately from a review decision.

This matters because a reviewer may raise a question without requesting changes, and a discussion may remain open even after a reviewer submits an approval.

The model therefore does not infer that an approval automatically means every conversation is resolved.

### Requested Changes

`changes_requested` is a substantive review state.

The governance engines treat outstanding requested changes as a merge blocker.

This prevents a second reviewer approval from accidentally being interpreted as cancellation of an unresolved negative review.

### Resolving Discussions

The PostgreSQL model gives conversations their own state:

`open`

or

`resolved`

This allows branch protection to require all conversations to be resolved without changing the historical review decision itself.

## Approvals

An approval is a specific review decision.

It is not equivalent to the existence of a reviewer, a comment, or a Pull Request.

The implementations model approval using:

`reviewer + review state + reviewed commit`

This creates an important distinction between a current approval and a stale approval.

### Eligible Reviewers

A reviewer must be active before submitting a review in the PostgreSQL implementation.

The database contains a reviewer table with:

- Username
- Active status
- Administrator status

The enterprise Java model also treats reviewer identity as part of the domain rather than accepting arbitrary strings during policy evaluation.

### Required Reviews

Branch protection determines the number of required approvals.

For the example protected `main` branch, two approvals are required.

The merge engine counts distinct eligible approval decisions associated with the current Pull Request head.

### Stale Approvals

Suppose a reviewer approves commit `11111111`.

The author then pushes commit `22222222`.

The second commit changes the reviewed changeset.

The implementations therefore do not count the approval for `11111111` when evaluating the Pull Request whose current head is `22222222`.

This rule appears in all five implementations.

It is one of the most important relationships between code review and merge governance.

### Dismissed Approvals

A dismissed review is not counted as an approval.

The review remains part of the historical record but no longer contributes to current approval satisfaction.

This separates audit history from current merge eligibility.

### Approval and Merge Eligibility

Approval is one input to merge eligibility.

It is not sufficient by itself.

A Pull Request can have two valid approvals and still be blocked because:

- A required status check failed
- A required status check has not completed
- A review requested changes
- A conversation remains unresolved
- The Pull Request is still a draft
- The Pull Request is not open
- The target branch has a stronger protection rule

## Branch Protection

Branch Protection represents repository-level enforcement.

It answers:

`What conditions must be satisfied before this branch accepts a merge?`

The example `main` branch requires:

- Two current approvals
- Passing unit tests
- Passing security scanning
- Passing product-policy validation
- Resolved review conversations
- No direct pushes
- No force pushes
- No branch deletion
- Linear history

The policy is intentionally stronger than simply requiring an approval.

## Required Status Checks

Automated checks provide machine-generated evidence about the proposed change.

The PostgreSQL model records:

- Check name
- Pass/fail result
- Pull Request
- Commit evaluated
- Completion time

The current commit association is important.

A passing security scan for an older commit should not automatically satisfy a policy requiring the latest commit to be checked.

The merge view therefore compares status checks against the latest Pull Request commit.

## Direct Push Restrictions

A protected production branch should not accept uncontrolled direct writes when the product strategy requires review before delivery.

The PostgreSQL trigger rejects direct commit insertion into a protected branch when `allow_direct_push` is false.

This demonstrates database-level enforcement.

The application layer can provide the preferred Pull Request workflow, while the database still protects an important invariant.

## Force-Push Restrictions

Force pushes can rewrite branch history.

The branch-protection model records `allow_force_push`.

For a critical production branch, the example sets this value to false.

This is a governance decision rather than merely a Git command preference because history integrity affects auditability, review traceability, and operational confidence.

## Branch Deletion Restrictions

The policy also records whether the protected branch can be deleted.

The example production branch cannot be deleted.

The database stores this policy even though branch deletion itself is outside the simplified relational workflow.

This keeps repository governance data explicit instead of hiding policy assumptions in application code.

## Linear History

The example requires linear history.

This means the product's repository governance strategy prefers a history without merge commits that introduce unnecessary branching structure into the protected branch.

The selected Pull Request merge strategy is `squash`.

The implementations keep merge strategy separate from approval requirements because these are different decisions:

- Approval determines whether people accepted the change.
- Merge strategy determines how accepted changes are represented in repository history.

## Administrator Behavior and Bypass

The branch-protection model includes an administrator bypass field.

The example sets it to false.

A bypass mechanism should be explicit because a hidden administrative override can undermine the meaning of repository policy.

The data model therefore records the policy choice even though the sample workflow does not exercise an emergency bypass.

## Python Implementation

The Python implementation is a complete in-memory repository governance simulator.

### Domain Model

The main domain types are:

- `ProductStrategy`
- `ProductGoal`
- `Repository`
- `PullRequest`
- `Commit`
- `Review`
- `BranchProtection`

Enums distinguish:

- Product stages
- Pull Request states
- Review states
- Merge strategies

Dataclasses provide explicit state containers and validation boundaries.

### Merge Evaluation

`MergeEligibility` evaluates:

1. Target branch availability
2. Branch protection
3. Pull Request state
4. Draft status
5. Commit existence
6. Current approvals
7. Requested changes
8. Required status checks
9. Open conversations

The method returns both the decision and blocking reasons.

This makes failure handling observable rather than returning only a Boolean value.

### Edge Cases

The script demonstrates:

- A valid merge
- Stale approvals
- Required status checks
- Requested-change detection
- Unresolved conversation handling
- Empty-commit rejection

The implementation has no external dependencies and runs with the Python standard library.

## JavaScript Implementation

The JavaScript implementation uses an event-driven repository model.

`Repository` extends `EventEmitter`.

Events are emitted when:

- A Pull Request is created
- A Pull Request is merged

This provides a complementary perspective to the Python simulation.

The model uses:

- `Map` for Pull Requests and status checks
- `Set` for branches, reviewers, approvals, and conversations
- Classes for repository entities
- Promises-ready event-oriented structure
- Explicit validation errors

The policy engine calculates current approvals from the Pull Request head rather than trusting the historical existence of an approval.

This prevents an old review from silently satisfying a current policy.

## C++17 Implementation

The C++17 program treats repository governance as a policy engine.

The architecture separates:

- Product strategy
- Repository state
- Pull Request state
- Branch protection
- Review state
- Merge evaluation

STL containers provide:

- `std::vector` for ordered commits and reviews
- `std::map` for status checks and repository objects
- `std::set` for required checks and unique approvals

`GovernanceEngine` returns a structured `MergeEvaluation` containing:

- Eligibility
- Blocking reasons

This makes policy evaluation deterministic and suitable for a command-line governance service.

The C++ implementation also explicitly demonstrates exception handling for invalid repositories, missing branches, invalid Pull Requests, and absent commits.

## Java 17 Implementation

The Java implementation models repository governance as an enterprise domain service.

Java records represent immutable value-oriented objects such as:

- `ProductGoal`
- `Commit`
- `Review`
- `ProductStrategy`
- `BranchProtection`
- `Eligibility`

The mutable Pull Request aggregate owns state transitions and validates changes.

`MergeEligibilityService` is the domain service responsible for determining whether a Pull Request can be merged.

The design separates:

- Domain entities
- Immutable policy values
- Repository storage
- Merge eligibility logic
- Product strategy

This separation is useful when the same governance rules must later be exposed through multiple enterprise interfaces.

## PostgreSQL Implementation

The PostgreSQL implementation provides a relational representation of the complete governance model.

The schema includes:

- Repositories
- Strategic choices
- Product goals
- Branches
- Commits
- Pull Requests
- Pull Request commits
- Reviewers
- Reviews
- Review comments
- Conversations
- Status checks
- Branch protection policies
- Required status checks

### Referential Integrity

Foreign keys enforce relationships between repository objects.

For example:

`repository -> branch -> commit`

and:

`pull_request -> review -> reviewer`

This prevents orphaned governance records.

### Constraints

The schema uses:

- Primary keys
- Unique constraints
- Foreign keys
- Check constraints
- Partial indexes
- Enum types

These controls prevent invalid domain states at the database boundary.

### Triggers

The database uses triggers for important invariants.

The protected-branch trigger rejects direct commits when direct pushes are disabled.

The review trigger prevents inactive reviewers from submitting reviews and prevents reviews from referencing commits outside the Pull Request.

The merge trigger validates:

- Required approvals
- Current reviewed commit
- Requested changes
- Open conversations
- Required status checks

This makes merge policy enforceable independently of a particular application implementation.

## Merge Eligibility

Merge eligibility is the intersection of multiple independent conditions.

A simplified decision model is:

`Eligible = Open`
`AND Not Draft`
`AND Current Approvals >= Required Approvals`
`AND Required Checks Pass`
`AND Requested Changes = 0`
`AND Open Conversations = 0`
`AND Protected Branch Policy Exists`

This is deliberately different from:

`Eligible = Approvals Exist`

Approvals are evidence of human review.

Branch protection determines which evidence and conditions are mandatory.

## Failure Modes

The implementations cover several realistic failure conditions.

| Failure | Reason for blocking |
|---|---|
| No commits | There is no changeset to merge |
| Draft PR | The proposal is not ready |
| Stale approval | Approval refers to an earlier commit |
| Requested changes | Review has identified unresolved issues |
| Missing check | Required automated evidence is absent |
| Failed check | Automated validation rejected the current commit |
| Open conversation | Required discussion has not been resolved |
| Unprotected target | Repository policy is undefined |
| Direct protected-branch commit | Governance policy forbids uncontrolled writes |

These failure modes are represented as explicit state or policy conditions rather than generic errors.

## Security Considerations

Repository governance is a security control as well as a development workflow.

The model addresses:

- Protection against uncontrolled production writes
- Force-push restrictions
- Review accountability
- Approval freshness
- Automated security checks
- Reviewer activity status
- Auditability of review decisions
- Separation of administrator capability from normal developer workflow

A particularly important control is commit-specific approval.

Without it, a developer could obtain approval for one changeset and then modify the code after approval while retaining the apparent approval count.

The implementations prevent that interpretation by requiring approvals to match the current Pull Request head.

## Performance Considerations

The in-memory implementations use sets and maps for operations that require membership checks.

Typical governance operations are approximately:

- Branch lookup: `O(1)` average in hash-based implementations
- Status-check lookup: `O(1)` average
- Approval collection: `O(R)` where `R` is the number of reviews
- Merge evaluation: `O(R + C + K)` where `R` is reviews, `C` is conversations, and `K` is required checks

The PostgreSQL implementation uses indexes on frequently evaluated relationships such as Pull Request state, reviewer state, conversations, and status checks.

The database view uses grouped and windowed queries to identify current commits and current approvals.

For large repositories, historical review records would normally require pagination, archival strategy, and carefully selected indexes.

## Security and Product Trade-Offs

Strong branch protection reduces the risk of uncontrolled changes but can increase delivery friction.

For example:

| Control | Benefit | Trade-off |
|---|---|---|
| Two approvals | Reduces single-reviewer risk | Slower small changes |
| Required security scan | Detects automated security failures | Can delay delivery when infrastructure fails |
| Resolved conversations | Preserves review accountability | Can block technically safe changes over unresolved discussion |
| No direct push | Forces controlled workflow | Makes emergency changes slower |
| No force push | Preserves history | Limits some advanced history-repair operations |
| Linear history | Simplifies production history | Restricts some merge workflows |

Product strategy determines which trade-offs are acceptable.

Technical controls implement those choices.

## Distinguishing Product Strategy from Repository Policy

Product Strategy should not become a list of technical settings.

The strategic layer defines why repository governance matters and what outcomes the product should produce.

The repository policy layer defines enforceable conditions.

The workflow layer manages proposed changes.

The review layer evaluates those changes.

The approval layer records decisions.

The database layer preserves and enforces state.

The resulting separation is:

`Strategy -> Policy -> Workflow -> Evidence -> Enforcement`

This prevents technical controls from becoming disconnected configuration.

## Practical Repository Scenario

A product team plans a security-sensitive release.

A developer creates:

`feature/product-strategy`

The branch proposes changes to:

`main`

A Pull Request is opened.

Two eligible reviewers examine the current commit.

Automated checks execute:

- `unit-tests`
- `security-scan`
- `product-policy`

Review conversations are resolved.

The two approvals reference the current Pull Request head.

The protected `main` branch requires two approvals and all three checks.

Only then does merge eligibility become true.

The final merge is recorded using the selected merge strategy.

If the developer adds another commit after approval, the previous approvals no longer satisfy the current-head requirement.

The review process must therefore evaluate the new changeset.

## File Responsibilities

| File | Primary responsibility |
|---|---|
| Python | In-memory product strategy and repository workflow simulation |
| JavaScript | Event-driven repository policy evaluation |
| C++17 | Repository governance and merge-eligibility engine |
| Java 17 | Enterprise domain model and merge eligibility service |
| PostgreSQL | Persistent relational governance model and database-level enforcement |
| README.md | Technical description of the complete product strategy and governance model |

## Execution Model

### Python

The Python file uses only the standard library.

Run it with:

`python product_strategy.py`

### JavaScript

The JavaScript file uses Node.js built-in functionality.

Run it with:

`node product_strategy.js`

### C++17

Compile with:

`g++ -std=c++17 -O2 -Wall -Wextra product_strategy.cpp -o product_strategy`

Run with:

`./product_strategy`

### Java 17

Compile with:

`javac ProductStrategyGovernance.java`

Run with:

`java ProductStrategyGovernance`

### PostgreSQL

Execute the SQL file against a PostgreSQL database with sufficient schema-creation privileges.

The script creates its own schema, inserts a complete example repository, builds governance policies, evaluates Pull Requests, and performs a transactionally guarded merge.

## Data Relationship

The relational structure is:

`Repository`
`  -> Strategic Choices`
`  -> Product Goals`
`  -> Branches`
`      -> Commits`
`  -> Pull Requests`
`      -> Reviews`
`          -> Review Comments`
`              -> Conversations`
`      -> Status Checks`
`  -> Branch Protection`
`      -> Required Status Checks`

Merge eligibility joins these structures rather than storing a permanent Boolean that could become stale.

This is an important design decision: eligibility is derived from current repository state.

## Limitations

The implementations intentionally model governance rather than implementing the complete Git protocol or a production hosting platform.

They do not provide:

- Network synchronization with a remote Git service
- Actual Git object storage
- Distributed locking
- Identity-provider integration
- Full merge-conflict computation
- Complete repository permission inheritance
- Enterprise audit-log infrastructure
- Production deployment orchestration

The examples instead concentrate on the product-strategy relationship between proposed changes, review decisions, approval freshness, automated evidence, repository policy, and final merge eligibility.

The resulting model is small enough to inspect directly while retaining the important distinctions required for repository governance.
