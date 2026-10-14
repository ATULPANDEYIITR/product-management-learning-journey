# Acceptance Criteria: Given-When-Then, Edge Cases, Validation Rules, and Expected Behavior

## Purpose and scope

Acceptance criteria define observable conditions that a software change must satisfy to be accepted. They translate a business requirement into behavior that a product owner, developer, reviewer, tester, and release system can evaluate consistently.

This implementation focuses on acceptance criteria for repository development and governance. Its examples address pull request readiness, review approval, automated status checks, and protected branch merge eligibility.

The central distinction is between **specifying expected behavior** and **proving that the behavior occurred**. A criterion describes what must happen. A Given-When-Then scenario makes that requirement testable. Validation determines whether the specification is sufficiently complete. Execution evidence records whether a particular implementation satisfied it. Repository policies determine whether the associated code change may be merged.

## Acceptance criteria and related terminology

| Term | Meaning in this implementation |
|---|---|
| Acceptance criterion | A business-facing condition that defines acceptable feature behavior. |
| Scenario | A concrete situation used to demonstrate one aspect of a criterion. |
| Given | The initial conditions, state, permissions, or data that must exist before an action. |
| When | The event or operation whose behavior is being evaluated. |
| Then | The observable result that must follow from the action. |
| Expected behavior | The precise outcome, including important restrictions and boundary conditions. |
| Validation rule | A condition that determines whether a criterion or scenario is sufficiently well-defined. |
| Edge case | A boundary or exceptional condition that may expose incorrect assumptions. |
| Execution evidence | A recorded test result, commit identifier, or other traceable proof of an evaluation. |
| Merge eligibility | The result of evaluating whether a pull request satisfies the repository's merge policies. |

A criterion can be syntactically complete yet insufficiently precise. For example, "the merge should be secure" does not define a measurable result. "A pull request targeting `main` cannot merge while the required security scan is pending" describes a condition and an observable outcome.

## Given-When-Then as an executable specification

Given-When-Then separates preconditions, actions, and outcomes.

Consider the requirement that a protected production branch must not accept a pull request without an eligible independent approval.

**Given:** The target branch requires an approval from an eligible reviewer.

**When:** A pull request has passing automated checks but no qualifying approval.

**Then:** The merge remains blocked.

**Expected behavior:** A successful CI run cannot substitute for the review decision required by repository policy.

This scenario is different from one in which the review exists but is stale. An approval against an earlier commit may no longer cover the changes being proposed. The second condition requires explicit evaluation of the reviewed commit against the current pull request head.

A useful scenario should establish enough state to make the result deterministic. Preconditions must identify relevant permissions, data, configuration, and current revision. The action should identify the operation being evaluated rather than merely saying that a user interacts with the system. The expected result should be externally observable through a returned decision, persisted state, API response, or test assertion.

### Multiple scenarios for one criterion

A single criterion may need several scenarios because normal behavior and failure behavior often differ.

| Scenario category | Protected-branch example | Expected result |
|---|---|---|
| Positive | Eligible approvals and all required checks are current and successful. | The request can pass the configured eligibility evaluation. |
| Negative | The required approval is absent. | The request is blocked. |
| Boundary | The approval count is exactly the required count. | The count requirement is satisfied, subject to every other rule. |
| Stale evidence | A check passed on an earlier commit. | The old result does not satisfy a requirement for the current head. |
| Invalid specification | A criterion has no scenarios. | The criterion cannot become ready. |
| State transition | A draft request is evaluated for merging. | The request remains ineligible until it leaves draft status. |

These scenarios are related but not interchangeable. Each exposes a different condition and should produce a separately observable result.

## Validation rules and readiness

Validation checks whether a criterion is sufficiently well-defined before implementation or test execution is treated as authoritative.

The Python, JavaScript, and Java programs validate criterion identifiers, titles, descriptions, owners, priorities, and scenarios. Each scenario must include meaningful Given, When, Then, and expected-behavior text. The programs reject an empty scenario collection and incomplete scenario definitions.

The PostgreSQL schema enforces corresponding rules through `NOT NULL`, `CHECK`, `UNIQUE`, and foreign-key constraints. These constraints protect persisted data even when a request does not originate from the expected application workflow.

Validation should distinguish between an invalid specification and an unsuccessful test:

- An invalid specification cannot be evaluated reliably because essential information is missing or malformed.
- A valid specification whose execution fails represents an implementation or environment problem that requires investigation.
- A valid specification whose execution passes has supporting evidence for the tested revision. It does not prove that every possible behavior has been tested.

The distinction matters because treating every failure as a specification error conceals defects, while treating incomplete requirements as ordinary test failures produces ambiguous work for the development team.

### Validation rules demonstrated by the code

| Rule | Invalid condition | Result |
|---|---|---|
| Identifier format | The criterion key does not follow `AC-AREA-001`. | Validation fails. |
| Title length | The title is blank or exceeds its permitted length. | Validation fails. |
| Description quality | The description is too short to express meaningful behavior. | Validation fails. |
| Scenario completeness | Given, When, Then, or expected behavior is absent. | The scenario is rejected. |
| Scenario coverage | No scenarios exist for the criterion. | Readiness is blocked. |
| Ownership | No accountable owner is assigned. | Validation fails. |
| Execution evidence | A test result lacks evidence. | The execution record is rejected. |
| Duplicate identity | A criterion key already exists within the repository. | The database rejects the duplicate. |

Character-count rules are only basic quality gates. They cannot determine whether the behavior is logically consistent, measurable, or complete. Human review remains necessary for ambiguous business rules and contradictory requirements.

## Edge cases and expected behavior

Edge cases should be selected from actual domain risks rather than added merely to increase test count.

### Boundary conditions

For a requirement that exactly two approvals are needed, test one approval, two approvals, and more than two distinct eligible reviewers. The decision should count distinct eligible reviewers, not review records. Repeated approvals by one reviewer must not satisfy a two-reviewer requirement.

For length validation, test the shortest accepted title, one character below that boundary, the maximum accepted title, and a title one character beyond the maximum. Test whitespace-only strings separately because they may have a nonzero raw length but no meaningful content.

### Stale approvals and status checks

A pull request may receive approval and pass CI, then acquire a new commit. The earlier approval and earlier status checks are evidence about the previous revision. When policy requires current evidence, neither should count toward the new revision until the relevant review and checks are updated.

The C++ and Java programs explicitly associate status checks with a commit SHA. The Java implementation also compares review commit identifiers when stale approvals must be dismissed. The SQL model stores the reviewed commit and the checked commit so queries can distinguish current evidence from outdated evidence.

### Missing, pending, and failed checks

A required status check has at least three meaningful non-success conditions:

- No result exists for the current commit.
- A result exists but remains pending.
- A result exists and has failed.

A cancelled check also cannot be treated as successful unless the repository has an explicitly different policy. A merge-eligibility decision must identify the missing or unsuccessful check by name so the developer can determine what remains blocked.

### Review discussions and requested changes

An unresolved review comment may represent a defect, a question, a design concern, or a request for clarification. The repository policy may require all relevant conversations to be resolved before merging, but resolving a discussion does not automatically mean the underlying implementation is correct.

Likewise, a review marked `changes_requested` is a review decision, not merely a comment. The system must retain that distinction. Dismissing a review, resolving a comment, and submitting a new approval are different operations and should not be represented by one generic completion flag.

### Invalid lifecycle transitions

A draft criterion cannot be marked ready while mandatory scenarios are missing. A criterion cannot be marked verified without an execution result. A closed pull request cannot be merged simply because its historical tests passed. A draft pull request remains ineligible even when its review and check data appear complete.

Explicit transition rules prevent accidental changes to workflow state. They also make failures easier to debug because the system can explain which transition was rejected and why.

## Python implementation

The Python file provides a self-contained specification and validation toolkit.

`Scenario` represents Given-When-Then behavior and validates each required text field and scenario tags. `AcceptanceCriterion` groups scenarios under a stable identifier, priority, owner, and lifecycle status.

The `mark_ready()` method rejects incomplete criteria before changing their state. The `record_result()` method requires a valid workflow state and non-empty execution evidence. It records the evidence and changes the status to either verified or failed.

`ValidationRule` separates a named predicate from its error message. This allows input checks to be expressed as reusable validation objects rather than scattering unrelated conditional statements throughout the application.

The JSON export serializes criteria and their scenarios into a machine-readable document. The temporary-file replacement reduces the chance of leaving a partially written output document when a write fails. It does not provide a complete crash-durability guarantee on every filesystem.

The `unittest` suite covers valid readiness, missing scenarios, invalid identifiers, blank evidence, failed execution, invalid priorities, and incomplete scenario input. These tests demonstrate the difference between validating a specification and evaluating its implementation.

## JavaScript implementation

The JavaScript file models acceptance criteria as an event-driven workflow.

`AcceptanceCriterion` owns the specification and its lifecycle. Its `transition()` method validates permitted state changes and requires successful validation before a criterion can become ready. `recordExecution()` records a result only when the criterion is ready and requires a commit SHA to connect evidence to a particular revision.

`AcceptanceCriteriaService` maintains criteria in a private `Map`. It emits registration, readiness, verification, and failure events. Other application components can subscribe to these events without taking ownership of the underlying lifecycle rules.

This event-driven model is useful when readiness changes must trigger test scheduling, dashboards, audit records, or release-policy reevaluation. Consumers should still make operations idempotent and avoid treating an emitted event as proof that a separate external operation completed successfully.

The implementation uses Node.js's built-in `EventEmitter` and `assert` modules, so it does not require third-party packages. Its tests exercise invalid transitions, missing records, incomplete specifications, and evidence validation.

## C++ case study: repository merge eligibility

The C++ program models a repository governance service evaluating a pull request for the protected `main` branch.

`AcceptanceCriterion` and `Scenario` validate the requirement definition separately from the repository decision. `BranchProtection` captures policy settings, while `PullRequest`, `Review`, and `StatusCheck` represent the current state being evaluated.

`RepositoryGovernance::evaluate()` returns an eligibility result containing a Boolean decision and a collection of explicit blockers. This is preferable to a single Boolean alone because a developer needs to know whether approval, a security scan, conversation resolution, or conflict resolution is outstanding.

The approval calculation counts distinct eligible reviewers whose approvals cover the current revision. The required-check evaluation matches check names and commit SHAs. A passing check associated with an earlier revision is therefore not sufficient when the current head requires a fresh result.

The case study also represents force-push and branch-deletion restrictions separately from pull request merge eligibility. These are branch-governance operations, not review outcomes. A repository can prohibit direct force pushes even when a particular pull request is otherwise eligible to merge.

The example is a policy model, not a complete Git hosting server. A production implementation must also account for concurrent updates, authorization at the time of the operation, branch ancestry, merge-base calculations, merge queues, policy changes during evaluation, and the atomicity of the final merge operation.

## Java implementation: enterprise domain model

The Java program uses records for immutable scenarios, reviews, checks, branch policies, and pull request snapshots. These types make the information required for policy evaluation explicit and prevent accidental mutation through returned collections.

`AcceptanceCriterion` owns readiness and execution state. Its validation method reports multiple errors in one pass, while its lifecycle methods prevent execution from being recorded against a criterion that is not ready.

`BranchProtection` captures approval thresholds, required check names, conversation-resolution policy, linear-history policy, force-push and deletion settings, and stale-approval behavior.

`MergeEligibilityService` evaluates a pull request against a supplied policy. It checks the target branch, lifecycle state, conflicts, conversations, qualifying reviewers, and current status-check results. Its `Eligibility` record returns both the decision and a list of blockers.

The service is intentionally separate from the domain records. This keeps policy evaluation testable without coupling it to a web framework, database, or external Git hosting provider.

The program uses Java 17 features and the standard library. It can serve as the basis for an enterprise policy service, but a production implementation would also require persistence, access control, concurrent-update handling, audit logging, and an atomic merge operation.

## PostgreSQL data model

The SQL script separates requirement definition, test evidence, review activity, branch policy, and merge events into related tables.

### Requirement definition and traceability

`acceptance_criterion` stores the identifier, title, description, priority, owner, and readiness status. A unique constraint prevents duplicate criterion keys within the same repository.

`acceptance_scenario` stores Given, When, Then, expected behavior, and scenario tags. Its foreign key connects each scenario to a criterion. `criterion_execution` stores test outcomes, commit identifiers, execution evidence, and the person who performed the test.

This structure makes it possible to query scenario coverage and execution history without embedding all acceptance criteria in a single unstructured text field.

### Pull requests and reviews

`pull_request` records source and target branches, current head and base revisions, draft and open states, conflict state, and conversation status. `pull_request_commit` retains the submitted commit sequence.

`pull_request_review` distinguishes review decisions and records the revision that was reviewed. `review_comment` stores inline or file-level discussion and resolution state. `pull_request_status_check` records the check name, revision, outcome, and optional details URL.

These tables preserve distinct facts. An approval is not a status check, and a resolved comment is not proof of successful CI.

### Branch protection

`branch_protection` represents the policy attached to a branch. It stores the required approval count, stale-approval behavior, conversation and linear-history requirements, direct force-push and deletion restrictions, administrator enforcement, and the configured merge method.

`required_status_check` stores the names of checks that must pass. Its composite primary key prevents the same check name from being registered twice for one policy.

The relational model separates policy configuration from pull request evidence. That separation allows the same eligibility query to evaluate different requests against the correct target-branch policy.

### Eligibility query

The `pull_request_merge_eligibility` view combines approval counts, required-check results, unresolved discussions, and pull request lifecycle state.

The approval calculation counts distinct eligible reviewers, excludes the author, and can reject stale approvals. The status-check calculation requires a passing result for the current head SHA. The unresolved-discussion count exposes remaining review work.

The view returns explanatory status values such as `draft`, `merge_conflict`, `insufficient_approvals`, `required_checks_incomplete`, and `unresolved_conversations`.

The view is a decision aid, not a complete merge authorization boundary. For example, it does not fully implement every possible code-owner rule, required-review dismissal policy, branch ancestry condition, merge-queue policy, or administrator bypass rule. Those behaviors must be enforced by the actual merge service if required by the repository.

### Transactions and database integrity

The example uses a transaction and row lock before recording a merge event. It rechecks eligibility before changing the pull request to a merged state. This illustrates why checking eligibility and recording the merge as unrelated operations can introduce race conditions.

In a production service, every policy-relevant mutation must coordinate with the merge transaction or an equivalent serialization mechanism. The transaction must also verify that the target branch has not advanced in a way that invalidates the evaluated state.

The SQL demonstration ends with `ROLLBACK` so the sample data and merge operation do not persist. Execute it in a dedicated PostgreSQL database or development environment because it creates a schema and database objects.

## How the six implementations fit together

| Layer | Responsibility | Evidence produced |
|---|---|---|
| Acceptance specification | Defines the required behavior and scenario boundaries. | Validated criterion and Given-When-Then scenarios. |
| Application validation | Rejects incomplete definitions and invalid state transitions. | Validation errors or a readiness decision. |
| Test execution | Evaluates the implementation against a scenario. | Pass or fail result tied to a revision. |
| Code review | Evaluates the correctness, safety, maintainability, and scope of a proposed change. | Comments and a review decision. |
| Approval policy | Determines whether eligible reviewers have supplied the required decision. | A qualifying approval count and current review state. |
| Branch protection | Enforces repository-level requirements before a change can be merged. | Merge blockers or policy eligibility. |
| Persistence and audit | Retains criteria, reviews, checks, and merge decisions. | Traceable relational records and execution history. |

The layers are connected but not interchangeable. A criterion can be valid while its test fails. A test can pass while review approval is missing. A pull request can have approval while a required security check remains pending. Branch protection combines the relevant policy conditions to decide whether merging is permitted.

## Common implementation mistakes

- **Treating a description as a testable requirement:** A statement such as "make the workflow robust" lacks an observable outcome. Specify the state, action, expected result, and relevant boundary.
- **Counting review records rather than distinct reviewers:** Multiple submissions by one person must not satisfy a policy that requires independent reviewers.
- **Accepting stale evidence:** Approval and CI results should be associated with the revision they evaluated. A new commit may invalidate previously accepted evidence.
- **Conflating review comments and review decisions:** A comment can identify a concern without representing approval or a formal request for changes.
- **Marking a criterion verified before execution:** Readiness establishes that the specification is testable. Verification requires recorded execution evidence.
- **Relying only on application validation:** Database constraints are needed for invariants that must survive alternate write paths, concurrent requests, or programming mistakes.
- **Checking eligibility only once:** A new commit, dismissed review, failed check, or policy change can invalidate an earlier decision. Re-evaluate conditions at the merge boundary.
- **Treating a successful eligibility query as a completed merge:** Eligibility is a decision about current state. The actual merge operation must also handle concurrency, authorization, branch updates, and atomic persistence.
- **Using text length as a substitute for requirement quality:** Minimum-length checks catch empty or trivial inputs, but cannot establish clarity, feasibility, or consistency.
- **Using unresolved discussion count as a universal review rule:** Whether every conversation must be resolved is a repository policy choice. It should be configured explicitly and applied consistently.

## Operational considerations

Acceptance criteria should be traceable from the business requirement to scenarios, automated tests, review evidence, and the resulting release decision. Stable criterion identifiers help link issue records, test reports, pull requests, and audit events.

The execution environment should retain the commit SHA, test outcome, relevant configuration, and evidence needed to reproduce a failure. Sensitive credentials, private tokens, and confidential source contents should not be copied into criterion text or public test logs.

A production governance system must enforce reviewer permissions on the server, protect policy changes, and audit any permitted bypass. Client-side validation improves usability but is not an authorization control. Database constraints protect data integrity but do not replace repository-level access controls or a secure merge implementation.

The objective is not to maximize the number of criteria. It is to make important behavior precise enough that different stakeholders can independently determine whether the implementation meets the stated requirement and can explain why an acceptance or merge decision was made.
