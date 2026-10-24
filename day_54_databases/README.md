# Relational Databases and Repository Governance

## Scope

This project uses relational database concepts to model a realistic software repository workflow. The database subject remains distinct from repository governance:

- relational databases define structured data, keys, relationships, constraints, and queries
- a Pull Request represents a proposed set of changes
- code review evaluates the proposed changes
- approvals represent review decisions
- branch protection enforces repository-level conditions
- merge eligibility combines the relevant conditions before a change reaches a protected branch

The implementations use repository governance as a practical domain for demonstrating relational modeling, state management, validation, and SQL.

## Core Relational Database Concepts

A relational database stores data in tables whose rows represent records and whose columns represent attributes.

The central design principle is to avoid storing unrelated concepts in one large record. Repository information, branches, commits, reviews, comments, status checks, users, and policies have different lifecycles and relationships, so they are modeled separately.

The resulting relationship structure is:

    Repository
        |
        +---- Branch
        |       |
        |       +---- Commit
        |
        +---- Pull Request
        |       |
        |       +---- Commit
        |       +---- Review
        |               |
        |               +---- Review Comment
        |
        +---- Status Check
        |
        +---- Branch Protection Policy
                |
                +---- Required Status Check
                +---- Allowed Merge Strategy
                +---- Bypass User

This structure prevents unrelated facts from being duplicated across rows and gives each entity a clear ownership boundary.

## Tables

The PostgreSQL implementation contains tables representing the major entities and relationships.

| Table | Purpose | Key relationship |
|---|---|---|
| `repositories` | Repository identity and default branch | Parent of branches and pull requests |
| `users` | Authors, reviewers, and merge actors | Referenced by reviews, commits, and merges |
| `teams` | Reviewer groups | Connected to users through `team_members` |
| `branches` | Repository branches | Belong to repositories |
| `commits` | Immutable changesets | Belong to repositories |
| `branch_commits` | Branch-to-commit association | Many-to-many relationship |
| `pull_requests` | Proposed changes | Connect source and target branches |
| `pull_request_commits` | Commits belonging to a PR | Many-to-many relationship |
| `reviews` | Review decisions | Belong to pull requests and reviewers |
| `review_comments` | Discussion attached to a review | Belong to reviews |
| `status_checks` | Automated validation results | Belong to pull requests |
| `branch_protection_policies` | Protected-branch enforcement | One policy per protected branch |
| `policy_required_status_checks` | Required automated checks | Many checks per policy |
| `policy_allowed_merge_strategies` | Permitted merge modes | Many strategies per policy |
| `policy_bypass_users` | Explicit bypass identities | Many users per policy |
| `merges` | Successful merge events | One merge per pull request |

## Keys

Primary keys uniquely identify rows.

Examples include:

- `repository_id`
- `user_id`
- `branch_id`
- `commit_id`
- `pull_request_id`
- `review_id`

The PostgreSQL implementation uses identity-generated numeric primary keys for database relationships. A commit also has a repository-specific unique `commit_sha`, which represents its external identity.

Foreign keys connect records while preserving referential integrity.

For example:

    pull_requests.author_user_id
        -> users.user_id

and:

    reviews.pull_request_id
        -> pull_requests.pull_request_id

A foreign key prevents a review from referencing a nonexistent pull request.

## One-to-Many Relationships

A repository can contain many branches:

    repositories 1 ---- N branches

A pull request can contain multiple reviews:

    pull_requests 1 ---- N reviews

A review can contain multiple comments:

    reviews 1 ---- N review_comments

These relationships are represented by foreign keys on the child tables.

## Many-to-Many Relationships

Some relationships cannot be represented correctly with a single foreign key.

A commit can exist on multiple branches, and a branch can contain multiple commits:

    branches N ---- N commits

The `branch_commits` table resolves this relationship.

Similarly, a pull request can contain multiple commits and a commit can participate in different pull-request histories. The `pull_request_commits` table resolves that relationship.

These junction tables contain their own primary keys and sequencing information where ordering matters.

## Constraints

The PostgreSQL model uses several forms of database constraints.

### Primary keys

Primary keys prevent duplicate identities.

### Foreign keys

Foreign keys enforce valid relationships between entities.

### Unique constraints

Examples include:

- repository names
- usernames
- branch names within a repository
- commit SHA values within a repository
- pull request numbers within a repository
- status-check names within a pull request

### Check constraints

Examples include:

- positive pull request numbers
- valid commit SHA formats
- nonempty names and messages
- positive comment line numbers
- nonnegative review requirements

### Enumerated states

PostgreSQL enums restrict workflow values to known states.

`pull_request_state` contains:

- `draft`
- `open`
- `closed`
- `merged`

`review_state` contains:

- `commented`
- `approved`
- `changes_requested`
- `dismissed`

This prevents arbitrary strings from entering state columns.

## Pull Request Lifecycle

A Pull Request is modeled as a stateful proposal.

The principal lifecycle is:

    Draft
      |
      v
    Open
      |
      +----> Closed
      |
      v
    Merged

A draft is not yet presented as a ready proposal. An open Pull Request can receive commits, reviews, comments, and status checks.

Closing stops the normal merge workflow. Reopening a closed Pull Request returns it to the open state when the repository workflow permits that transition.

Merging is different from closing. A merged Pull Request represents a completed integration into the target branch.

The source branch and target branch are stored separately. This is important because branch identity and proposed changes are different concepts.

## Source and Target Branches

The source branch contains the proposed changes.

The target branch is the branch that would receive the changes.

For example:

    feature/relational-schema
                |
                | Pull Request
                v
              main

The source and target branches must be distinct.

Branch state is independent of the Pull Request record. A new commit can change the source branch after a Pull Request has been created, which means the Pull Request must synchronize its effective changeset.

## Changesets and Commits

A commit represents a changeset.

A Pull Request is not itself a commit. It is a workflow object that groups changes and records review and validation state around those changes.

This distinction is represented by the relationship:

    Pull Request
        |
        +---- Commit
        +---- Commit
        +---- Commit

The implementations also treat review decisions as related to specific commits.

This permits stale-review detection. If a reviewer approved commit `b2c3d4e` and a new commit is later added, the previous approval can no longer automatically represent review of the new changes.

## Code Review

Code Review is the evaluation of proposed changes.

The model separates review data from the Pull Request itself.

A review contains:

- reviewer identity
- review state
- reviewed commit
- dismissal state

Review comments are separate records because one review can contain multiple comments.

The relationship is:

    Pull Request
        |
        +---- Review
                |
                +---- Comment
                +---- Comment

An inline comment identifies a file path and optionally a line number. Its conversation can be open or resolved.

Review quality depends on scope and evidence. A useful review checks correctness, data integrity, maintainability, security implications, and whether the proposed implementation satisfies the intended behavior.

A review should not be treated as equivalent to approval. A reviewer may comment without approving, or request changes without providing approval.

## Review States

The model distinguishes four review outcomes.

| State | Meaning |
|---|---|
| `commented` | Feedback was provided without an approval decision |
| `approved` | The reviewer accepts the reviewed changes |
| `changes_requested` | The reviewer requires changes |
| `dismissed` | The previous review decision no longer participates in approval evaluation |

A review is tied to a commit. This makes review state dependent on the changes that were actually examined.

## Review Discussions

A review comment can create an unresolved conversation.

When conversation resolution is required by branch protection, an unresolved comment blocks merge eligibility.

The relevant relationship is:

    Review
      |
      +---- Review Comment
                |
                +---- Conversation State

Resolving a discussion does not itself create an approval. It only changes whether that discussion remains a blocking condition.

This keeps review discussion state separate from approval semantics.

## Approvals

An approval is a specific review decision.

It should not be confused with:

- the existence of a reviewer
- a review comment
- a successful status check
- branch protection itself

Approval eligibility can depend on reviewer identity, reviewer activity, policy requirements, and the commit that was reviewed.

The implementations count distinct eligible reviewers rather than counting every approval record. This prevents repeated reviews from the same reviewer from artificially satisfying a required-review count.

## Stale Approvals

A stale approval occurs when a reviewer approved one version of a Pull Request and the Pull Request later changes.

The model handles this by associating a review with a specific commit.

The effective test is conceptually:

    Is the reviewed commit still part of the current Pull Request changeset?

If not, the approval is ignored for current merge eligibility.

This is a database relationship rather than merely a display attribute. The review references a commit, while the Pull Request references its current commits.

## Dismissed Approvals

A dismissed review remains historical information but does not count as an active approval.

This distinction preserves auditability:

    historical review record
              |
              +---- dismissed
                       |
                       +---- not counted for merge eligibility

Deleting a review would lose useful historical information. Marking it dismissed retains the event while changing its current policy effect.

## Reviewer Eligibility

The model contains explicit users and teams.

A reviewer can be inactive. Inactive reviewers are not counted toward current approval requirements.

This separates identity from eligibility.

The database can therefore answer different questions:

- Who submitted the review?
- What decision did they make?
- Are they currently active?
- Did their review target the current changes?
- Does repository policy require their approval?

These are different predicates and should not be collapsed into a single field.

## Branch Protection

Branch Protection is repository-level enforcement.

It is distinct from Code Review because a review expresses an evaluation, while branch protection specifies conditions that must be satisfied before integration.

A protected branch can require:

- a minimum number of approvals
- successful status checks
- resolved conversations
- restricted merge strategies
- linear history
- disabled direct pushes
- disabled force pushes
- disabled branch deletion
- explicit bypass identities

The relationship is:

    Protected Branch
          |
          v
    Protection Policy
          |
          +---- Review Requirements
          +---- Status Requirements
          +---- Merge Restrictions
          +---- Bypass Rules

The policy belongs to the branch rather than to an individual Pull Request.

## Status Checks

Automated status checks provide machine-generated validation.

Examples in the PostgreSQL dataset are:

- `sql-tests`
- `integration-tests`

A status check is not a review and does not count as an approval.

The distinction is:

    Review       -> human evaluation
    Approval     -> human decision
    Status Check -> automated validation

Branch protection can require successful status checks before merge.

## Merge Eligibility

Merge eligibility is a derived result.

It is not simply a stored Boolean because its inputs can change.

A simplified decision model is:

    Pull Request open
            |
            v
    Required approvals satisfied?
            |
            v
    No active requested changes?
            |
            v
    Conversations resolved?
            |
            v
    Required checks passed?
            |
            v
    Merge strategy permitted?
            |
            v
        MERGE ELIGIBLE

Each condition represents a different rule.

The PostgreSQL function `get_merge_eligibility` calculates this result from current relational data rather than trusting a manually maintained eligibility flag.

## Merge Strategies

The implementations distinguish three strategies:

| Strategy | Modelled behavior |
|---|---|
| Merge commit | Integrates the Pull Request as a separate merge history |
| Squash | Represents the Pull Request as one resulting commit |
| Rebase | Reuses the Pull Request commits on the target history |

Branch protection can restrict which strategies are permitted.

The Python, JavaScript, C++, and Java implementations default to squash for the sample protected branch because it provides a compact merge result while still demonstrating strategy enforcement.

## Direct Push and Force Push

Direct-push and force-push restrictions are branch-level governance controls.

They are not Pull Request states.

A Pull Request can be open while direct pushes to the target branch remain prohibited.

Force-push restrictions protect branch history from destructive rewriting.

The PostgreSQL policy stores both controls explicitly so they can be queried independently.

## Administrator and Bypass Behavior

Bypass behavior is modeled explicitly through `policy_bypass_users`.

This prevents bypass access from being implied by ordinary reviewer eligibility.

The distinction is important:

    reviewer eligibility
        !=
    protection bypass authority

A user may be a valid reviewer without being permitted to bypass branch protection.

A bypass operation is still represented as a merge event in the relational model.

## Python Implementation

The Python program provides an object-oriented repository workflow simulation.

Important domain classes include:

- `Repository`
- `Branch`
- `Commit`
- `PullRequest`
- `Reviewer`
- `Review`
- `ReviewComment`
- `StatusCheck`
- `BranchProtection`

Python `dataclass` objects provide explicit domain records.

Enums constrain workflow states and merge strategies.

The `Repository.evaluate_merge` method calculates merge eligibility. It checks Pull Request state, commits, review activity, stale approvals, requested changes, unresolved comments, status checks, and permitted merge strategies.

The `merge_pull_request` method then changes the Pull Request state and updates target-branch history.

Validation raises exceptions for invalid branch names, duplicate records, missing branches, invalid Pull Request transitions, and invalid reviews.

The JSON output provides a compact view of final repository state.

## JavaScript Implementation

The JavaScript implementation uses an event-oriented Node.js-compatible design.

`Map` structures represent entity collections, while `Set` objects represent teams, approvals, required checks, and bypass users.

The implementation provides methods for:

- branch creation
- commit creation
- reviewer registration
- branch protection
- Pull Request creation
- draft-to-open transition
- review submission
- comment creation
- comment resolution
- review dismissal
- status-check updates
- Pull Request synchronization
- merge evaluation
- merge execution

The `evaluateMerge` method returns structured eligibility information rather than immediately throwing an error. This is useful for interactive applications because a user interface can display each blocking reason.

The implementation treats reviews as commit-specific, so adding new commits can make previous approvals stale.

## C++17 Implementation

The C++ implementation models repository governance as a strongly typed merge engine.

The main class is `RepositoryGovernance`.

Supporting structures include:

- `Commit`
- `Branch`
- `Reviewer`
- `Review`
- `ReviewComment`
- `StatusCheck`
- `BranchProtection`
- `PullRequest`

C++17 containers provide efficient lookup and membership operations.

`std::map` stores repository entities by identity.

`std::set` handles reviewer teams, required checks, approvals, and bypass identities.

`std::vector` preserves ordered commits and review records.

The merge evaluator returns a pair containing an eligibility flag and a list of blocking reasons.

This makes failure handling explicit rather than encoding only success or failure.

The design also demonstrates the value of separating immutable-style commit information from mutable workflow state.

## Java 17 Implementation

The Java implementation uses an enterprise-oriented domain model.

Java records represent immutable value objects such as:

- `Commit`
- `ReviewComment`
- `BranchProtectionPolicy`
- `MergeDecision`

Mutable workflow objects are represented by classes such as:

- `Repository`
- `Branch`
- `PullRequest`
- `Review`
- `Reviewer`

Enums provide explicit workflow states and merge strategies.

The `Repository.evaluateMerge` service method separates policy evaluation from merge execution.

The `MergeDecision` record makes the result explicit:

    eligible
    reasons

This structure is suitable for service-layer applications because a caller can present multiple policy violations instead of receiving only the first failure.

The model also separates reviewer activity from reviewer identity and distinguishes dismissed reviews from active reviews.

## PostgreSQL Implementation

The PostgreSQL implementation provides the strongest relational representation.

It creates a dedicated `repository_governance` schema and defines tables, enums, keys, foreign keys, unique constraints, check constraints, indexes, triggers, functions, transactions, and sample data.

The relational model avoids storing complex structures as JSON when the data has stable relationships that benefit from relational integrity.

For example, required status checks are stored in `policy_required_status_checks` rather than as a comma-separated column.

Allowed merge strategies are stored in `policy_allowed_merge_strategies`.

Team membership is stored in `team_members`.

These junction tables preserve normalization and make individual relationships queryable.

## SQL Queries and CTEs

The SQL script includes queries for:

- Pull Request retrieval
- approval aggregation
- requested-change counts
- status-check validation
- branch protection inspection
- merge eligibility
- final merge history

The `WITH protection AS (...)` query demonstrates a Common Table Expression for building a reusable intermediate relational result.

CTEs improve readability when a query contains a meaningful logical stage.

## Views, Functions, and Triggers

The PostgreSQL design uses functions for reusable business logic.

`get_merge_eligibility` evaluates the current state of a Pull Request against its target branch policy.

`merge_pull_request` performs the merge operation transactionally and records the merge event.

Triggers maintain workflow-related integrity.

The Pull Request timestamp trigger updates `updated_at` whenever the row changes.

The protection-consistency trigger prevents a branch with an existing protection policy from being silently marked unprotected.

The merge-state trigger ensures that inserting a merge event transitions an open Pull Request to `merged`.

These mechanisms place important integrity rules close to the data.

## Transactions

The sample merge workflow uses:

    BEGIN
        eligibility and merge operation
    COMMIT

The merge function locks the Pull Request row before creating the merge record.

This is important because two concurrent processes should not independently treat the same Pull Request as available for merging.

Transactions therefore protect the relationship between:

    Pull Request state
        |
        +---- Merge record

The database should not end with a successful merge record while the corresponding Pull Request remains open.

## Normalization

The schema follows normalization principles by separating independent facts.

For example, storing:

    reviewer_name
    reviewer_team
    review_state
    comment_body

inside the Pull Request table would create repeated and inconsistent data.

Instead:

    users
       |
       +---- team_members ---- teams

    pull_requests
       |
       +---- reviews
                |
                +---- review_comments

This reduces duplication and improves update consistency.

## Referential Integrity

Foreign keys ensure that dependent records cannot reference missing parents.

Examples include:

    review -> pull_request
    review -> reviewer
    comment -> review
    status_check -> pull_request
    merge -> pull_request
    merge -> user

The deletion rules are intentionally different depending on the relationship.

Review comments are removed with their review because they have no independent lifecycle in this model.

User records are not automatically deleted when reviews exist because review history should remain referentially valid.

## Failure Cases

The implementations deliberately handle invalid conditions.

Examples include:

- duplicate branches
- duplicate commits
- invalid branch names
- missing source or target branches
- empty Pull Request titles
- reviews from unknown users
- inactive reviewers
- dismissed reviews
- stale approvals
- requested changes
- unresolved discussions
- failed required status checks
- unsupported merge strategies
- attempts to merge closed Pull Requests
- attempts to merge without required approvals
- invalid database foreign-key references

These failures demonstrate why validation belongs at multiple layers.

Application code can provide user-friendly errors, while database constraints protect persisted data.

## Security Considerations

Repository governance has authorization implications.

The model treats the following as security-sensitive controls:

- direct-push restrictions
- force-push restrictions
- protected branches
- reviewer eligibility
- approval requirements
- bypass permissions
- merge strategy restrictions

The database separates bypass users from reviewers so that ordinary review membership does not automatically grant enforcement bypass rights.

Input validation reduces malformed data.

Parameterized database functions and constrained values reduce the risk of storing arbitrary workflow states.

In a production system, authentication and authorization would also be enforced outside these in-memory examples and database functions.

## Performance Considerations

The implementations use appropriate collection types for their respective environments.

Python dictionaries and sets provide average constant-time membership lookup for major entity collections.

JavaScript `Map` and `Set` provide efficient keyed and membership access.

C++ uses `std::map` and `std::set`, providing logarithmic ordered lookup and deterministic iteration.

Java uses `HashMap` and `HashSet` for average constant-time lookup.

The PostgreSQL schema indexes common access paths:

- repository-to-branch lookups
- repository commit history
- target-branch Pull Request state
- Pull Request review state
- status checks
- unresolved comments

Indexes should correspond to actual query patterns. Excessive indexing would increase write cost without improving useful workloads.

## Relationship Between the Four Governance Areas

The four areas form a dependency chain but remain different concepts.

    Pull Request
        |
        | proposes
        v
    Code Review
        |
        | produces
        v
    Approval Decision
        |
        | evaluated against
        v
    Branch Protection
        |
        | determines
        v
    Merge Eligibility
        |
        v
      Merge

A Pull Request is the workflow container for proposed changes.

Code Review is the evaluation of those changes.

Approvals are specific review decisions that can satisfy policy requirements.

Branch Protection defines repository-level enforcement rules.

Merge eligibility is the derived result of evaluating the current Pull Request against those rules.

Treating these as separate entities prevents confusing a reviewer comment with an approval, an approval with a branch policy, or a Pull Request with a merge.

## Practical Relational Design Decisions

The project makes several deliberate database design choices.

| Decision | Reason |
|---|---|
| Separate repository and branch tables | A repository contains multiple branches |
| Separate commits from branches | A commit can participate in multiple branch histories |
| Junction table for PR commits | A Pull Request contains an ordered changeset |
| Separate reviews and comments | One review can contain multiple discussions |
| Separate status checks | Automated validation has different semantics from human review |
| Separate protection policy | Policy belongs to the protected branch |
| Junction tables for policy requirements | Policies can contain multiple independent requirements |
| Store merge events separately | Merge history should be auditable |
| Use enums for controlled states | Invalid workflow values should be rejected |
| Use functions for merge evaluation | Eligibility is derived from current relational state |

## Limitations of the Model

This project intentionally models the essential relational and governance concepts rather than the entire behavior of a production Git hosting platform.

The examples do not implement:

- complete Git object graphs
- commit parent DAG traversal
- real repository storage
- authentication protocols
- organization-wide identity providers
- distributed event delivery
- webhook processing
- repository hosting infrastructure
- cryptographic signature verification
- production-grade authorization policies

The simplified commit representation is sufficient for demonstrating relational relationships, stale-review behavior, branch policy evaluation, and merge eligibility.

A production system would require stronger concurrency controls, audit logging, authentication, authorization, operational monitoring, and integration with actual version-control infrastructure.
