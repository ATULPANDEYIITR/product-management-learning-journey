# Product-Engineering Collaboration

## Scope

This project models collaboration between product and engineering teams when a product requirement moves from an initial proposal toward implementation readiness.

The central workflow is:

Requirement
→ Discovery
→ Estimation
→ Architecture Options
→ Trade-off Evaluation
→ Decision
→ Validation
→ Ready for Implementation
→ Implementation

The four governance concepts represented in the broader engineering workflow remain distinct:

- A Pull Request proposes a concrete set of implementation changes.
- Code Review evaluates the quality, correctness, maintainability, and risk of those changes.
- Approvals represent explicit reviewer decisions.
- Branch Protection enforces repository-level conditions before a merge is permitted.

This project focuses primarily on the product-engineering decisions that should exist before and around implementation, while the PostgreSQL model connects those decisions to Pull Requests, reviews, approvals, status checks, and protected branches.

## Product-Engineering Collaboration Model

A product requirement is not treated as an isolated feature description. It contains:

- a stable requirement identifier
- a business or product objective
- acceptance criteria
- priority
- dependencies
- engineering ownership
- product ownership
- implementation risks
- an estimate
- architecture alternatives
- an explicit decision

The model distinguishes proposed changes from the engineering and governance conditions needed to implement them.

A useful lifecycle is:

`Proposed → Discovery → Estimated → Ready → In Progress → Done`

A requirement can also move into `Blocked` when a dependency, decision, technical uncertainty, or other constraint prevents progress.

Invalid state transitions are rejected rather than silently changing workflow state.

## Estimation

Estimation is represented as a structured value containing:

| Attribute | Meaning |
|---|---|
| Story points | Relative delivery size |
| Engineering days | Approximate implementation effort |
| Confidence | Confidence in the estimate |

The implementations reject invalid values such as zero or negative effort and confidence outside the range `(0, 1]`.

The model does not treat an estimate as a guarantee. Confidence is explicitly represented because feasibility discussions are affected by uncertainty.

A requirement cannot become implementation-ready when estimate confidence is below the defined threshold.

## Feasibility Analysis

Feasibility is evaluated through multiple architecture options rather than by assuming the first proposed design is the only possible implementation.

Each option records:

- expected delivery time
- operating cost
- scalability
- maintainability
- security
- implementation complexity

This makes trade-offs explicit.

For example, a synchronous design may reduce implementation time while increasing request-time computation and operational coupling. An asynchronous design may require more infrastructure while providing better scalability and predictable request latency.

The important engineering decision is not simply which option has the lowest cost. The decision depends on the product's priorities and technical constraints.

## Architecture Discussions

Architecture options are represented independently before a decision is recorded.

A decision contains:

- decision identifier
- title
- selected architecture
- rationale
- trade-offs
- decision status

This separates an architecture proposal from the final decision.

The rationale is important because the same architecture can be appropriate under one set of product constraints and inappropriate under another.

The implementations also prevent a decision from referencing an architecture option that does not exist.

## Trade-Off Evaluation

The scoring models use weighted factors.

Typical factors include:

| Factor | Engineering concern |
|---|---|
| Speed | Time required to deliver |
| Cost | Operational expenditure |
| Scalability | Ability to handle growth |
| Maintainability | Long-term engineering ownership |
| Security | Exposure and control quality |
| Quality | Complexity and reliability implications |

Weights allow the team to express priorities explicitly.

A security-sensitive feature can assign a greater weight to security. A prototype with a short delivery window can place greater weight on speed. A high-volume platform feature may emphasize scalability.

The score is a decision-support mechanism rather than an automatic replacement for engineering judgment.

## Python Implementation

The Python implementation provides a domain-oriented simulation.

It uses:

- `dataclass` models for immutable estimates and structured domain records
- enums for priority, state, decisions, and trade-off categories
- sets for dependency tracking
- dictionaries for weighted evaluation
- explicit domain exceptions
- state-transition validation
- serialization to JSON
- assertion-based validation checks

The `Requirement` class validates identifiers, descriptions, and acceptance criteria.

`CollaborationRecord` owns the workflow around a requirement and controls state transitions.

`ArchitectureEvaluator` ranks architecture options according to weighted product-engineering criteria.

The example scenario evaluates alternative approaches to idempotent payment retry handling. The selected design is chosen using delivery, cost, scalability, maintainability, security, and quality considerations.

The script also tests invalid estimates, invalid workflow transitions, and malformed requirements.

## JavaScript Implementation

The JavaScript implementation emphasizes event-driven collaboration.

The workflow extends Node.js `EventEmitter` and emits events when:

- the workflow state changes
- an estimate changes
- an architecture option is added
- a decision is accepted

This allows a future interface, audit system, or notification component to observe domain changes without embedding those concerns inside the core decision logic.

JavaScript `Map` objects store architecture options and decisions. `Set` objects store dependencies.

The scenario evaluates alternative recommendation architectures and selects an implementation strategy based on weighted criteria.

The implementation validates:

- requirement identifiers
- acceptance criteria
- estimate values
- architecture scores
- duplicate architecture options
- workflow transitions
- unresolved dependencies
- readiness conditions

The event-driven design provides a different perspective from the state-oriented Python implementation.

## C++17 Implementation

The C++17 program implements a repository-governance and merge-readiness case connected to product-engineering decisions.

Its domain includes:

- requirements
- architecture alternatives
- estimates
- architecture decisions
- repository-oriented governance
- readiness validation

The implementation uses:

- `struct` for value-oriented domain objects
- `class` for stateful services
- `enum class` for controlled states
- `std::vector` for ordered options
- `std::set` for dependencies
- `std::map` for weighted policies
- `std::optional` for estimates that may not yet exist
- exceptions for invalid domain operations
- STL algorithms for validation and ranking

The architecture engine evaluates an administrative export scenario where asynchronous object generation is compared with synchronous and direct-database alternatives.

The governance engine prevents a requirement from reaching `Ready` unless an estimate, architecture option, accepted decision, and valid dependencies are present.

This creates an explicit separation between architecture evaluation and workflow governance.

## Java 17 Implementation

The Java implementation represents an enterprise-oriented product-engineering service.

The domain uses:

- records for immutable estimates, architecture options, and decisions
- enums for controlled workflow and policy values
- interfaces for readiness policies
- collections for architecture and decision state
- streams for validation and ranking
- custom exceptions for domain failures
- a service class for workflow transitions

Three independent readiness policies are represented:

1. Estimate confidence policy
2. Architecture decision policy
3. Dependency policy

This separation is useful in enterprise systems because a workflow rule can evolve independently from the service coordinating the workflow.

The example concerns controlled feature rollout. It compares server-side feature flags, client-side configuration, and database configuration.

The selected architecture is then validated against readiness policies before the requirement enters the `READY` state.

## PostgreSQL Implementation

The PostgreSQL script models the collaboration process relationally.

The main relationship is:

`Repository`
→ `Branches`
→ `Commits`
→ `Pull Requests`
→ `Reviews`
→ `Review Comments`
→ `Status Checks`

Product-engineering planning is connected through:

`Repository`
→ `Requirements`
→ `Acceptance Criteria`
→ `Estimates`
→ `Architecture Options`
→ `Architecture Decisions`

Repository governance is represented through:

`Protected Branch`
→ `Branch Protection Policy`
→ `Approval Requirements`
→ `Status Checks`
→ `Conversation Resolution`
→ `Merge Eligibility`

### Requirements

Requirements store product and engineering ownership, priority, workflow state, and descriptions.

Acceptance criteria are stored separately so each criterion can be independently marked as satisfied.

Dependencies are modeled with a self-referencing relationship.

### Estimation

Estimates contain story points, engineering days, and confidence.

Database constraints prevent invalid estimates from entering the system.

### Architecture Options

Architecture options contain explicit trade-off dimensions:

- delivery time
- monthly cost
- scalability
- maintainability
- security
- complexity

The `architecture_tradeoff_report` view calculates a weighted score that can be used to compare alternatives.

### Architecture Decisions

An architecture decision references a specific architecture option.

The foreign key prevents a decision from selecting an architecture that is not recorded for the requirement.

### Pull Requests

The Pull Request model separates:

- repository
- requirement
- author
- source branch
- target branch
- commits
- draft state
- lifecycle state

This reflects the distinction between a product requirement and the concrete changes proposed to implement it.

### Code Review

Reviews are associated with Pull Requests and reviewers.

Review states distinguish reviewer decisions from the existence of a review itself.

Review comments are stored separately because a review can contain multiple discussions.

A comment can be resolved independently.

An unresolved comment therefore represents an outstanding discussion rather than merely an informational message.

### Approvals

Approvals are represented through accepted review decisions that have not been dismissed.

The merge eligibility function counts active approvals against the branch protection requirement.

An approval does not independently authorize a merge. It contributes one condition to the final repository-level decision.

### Branch Protection

Branch protection stores repository governance requirements such as:

- required review count
- required status checks
- conversation resolution
- direct-push restrictions
- force-push restrictions
- branch deletion restrictions
- linear-history requirements
- administrator bypass behavior

This is deliberately separate from code review and approval data.

A review expresses a reviewer's decision.

An approval expresses satisfaction of one review requirement.

Branch protection defines what the repository requires before merging.

## Pull Request Lifecycle

The repository model supports the practical Pull Request lifecycle:

`Draft → Open → Review → Checks → Eligible → Merge`

The source branch contains proposed changes.

The target branch identifies where those changes are intended to land.

The Pull Request references the commits that form its changeset.

The target branch may be protected by repository policy.

A draft Pull Request is explicitly rejected by the merge-eligibility function.

An open Pull Request can be evaluated after reviews, conversations, and automated checks are complete.

A closed Pull Request is not considered mergeable.

A merged Pull Request records the resulting merge state and commit.

## Code Review Mechanics

Code review is modeled around reviewer decisions and inline discussions.

A review can be:

- proposed
- accepted
- rejected

A review can also be dismissed without deleting its historical record.

Review comments contain:

- file path
- optional line number
- comment text
- resolution state
- associated review
- associated commit

This structure supports a practical review workflow:

`Review → Comment → Discussion → Resolution`

Review quality is not reduced to approval count. Unresolved technical or security discussions can prevent merge eligibility even when the required number of approvals exists.

## Approval Semantics

An approval is an explicit accepted review.

Active approvals are those that:

- belong to the Pull Request
- have an accepted decision
- have not been dismissed

The database therefore distinguishes an historical approval from a currently effective approval.

This is important when a review becomes stale or is dismissed after changes.

The merge-eligibility function compares active approvals against the protected branch's required review count.

## Branch Protection and Merge Eligibility

Merge eligibility is evaluated as a combined policy decision.

The PostgreSQL function checks:

1. Pull Request existence
2. Pull Request state
3. Draft status
4. Required approval count
5. Unresolved review conversations
6. Failed status checks
7. Pending status checks

The resulting decision contains both a Boolean eligibility result and a reason.

Conceptually:

`Pull Request`
→ `Review Requirements`
→ `Approval State`
→ `Conversation State`
→ `Status Checks`
→ `Branch Protection`
→ `Merge Eligibility`

This prevents individual mechanisms from being treated as interchangeable.

## Relationship Between the Four Governance Areas

The four areas have different responsibilities.

| Area | Primary responsibility |
|---|---|
| Pull Request | Propose and coordinate a set of implementation changes |
| Code Review | Evaluate implementation quality and discuss defects or risks |
| Approvals | Record explicit reviewer decisions |
| Branch Protection | Enforce repository-level merge conditions |

A Pull Request can exist without approval.

A code review can contain comments without approval.

An approval can exist without making a Pull Request mergeable.

Branch protection combines repository-level conditions before permitting the final merge.

This distinction is essential for reliable engineering governance.

## Failure Handling

The implementations deliberately reject invalid situations rather than silently producing a misleading result.

Examples include:

- invalid requirement identifiers
- empty acceptance criteria
- negative or zero estimates
- low-confidence estimates
- duplicate architecture options
- decisions referencing unknown architecture options
- blocked dependencies
- illegal workflow transitions
- invalid architecture scores
- draft Pull Requests
- insufficient approvals
- unresolved conversations
- failed status checks
- pending status checks
- inactive or unauthorized reviewers

The PostgreSQL model reinforces several rules at the database layer with primary keys, foreign keys, unique constraints, check constraints, triggers, and transactional operations.

## Security Considerations

Product-engineering collaboration has security implications even before deployment.

The scenarios explicitly consider:

- authorization boundaries
- protection of sensitive data
- secure reviewer eligibility
- security-specific reviews
- restricted repository operations
- protection of production branches
- auditability of decisions
- prevention of sensitive data exposure through logs or exports

The JavaScript and Python examples treat security as an explicit architecture trade-off rather than an afterthought.

The PostgreSQL model also validates that a reviewer belongs to the repository and is active before accepting a review.

## Performance Considerations

The implementations use structures appropriate to their workloads.

Python uses dictionaries and sets for direct lookup and dependency membership.

JavaScript uses `Map` and `Set` to avoid repeated linear searches for workflow state.

C++ uses STL containers and algorithms while keeping the architecture evaluator independent of the governance engine.

Java uses immutable records and streams for compact domain transformations.

PostgreSQL adds indexes where query patterns justify them, including:

- requirement state and priority
- Pull Request target branch and state
- review state
- status-check state
- unresolved review comments

The architecture scoring models are linear in the number of candidate architecture options.

The database merge-eligibility evaluation is bounded by the number of reviews, comments, and status checks associated with the selected Pull Request.

## Transactional Integrity

The PostgreSQL implementation demonstrates a transaction around merge eligibility and merge recording.

The transaction records a merge attempt and updates the Pull Request only when the eligibility query returns an eligible result.

This keeps the decision and state transition within one transactional unit.

The example also demonstrates that an unresolved review conversation can prevent a merge. Once that conversation is resolved, the same eligibility function can be evaluated again.

## Practical Workflow

A disciplined product-engineering discussion can be represented as:

`Product requirement`
        |
        v
`Acceptance criteria`
        |
        v
`Technical discovery`
        |
        v
`Estimate + confidence`
        |
        v
`Architecture alternatives`
        |
        v
`Trade-off evaluation`
        |
        v
`Architecture decision`
        |
        v
`Implementation`
        |
        v
`Pull Request`
        |
        v
`Code review + approvals`
        |
        v
`Status checks`
        |
        v
`Branch protection`
        |
        v
`Merge eligibility`

Each stage answers a different question.

- Product defines what problem should be solved.
- Engineering determines what is technically feasible.
- Estimation expresses expected effort and uncertainty.
- Architecture analysis evaluates possible implementations.
- Trade-off analysis makes competing constraints explicit.
- A decision records why one option was selected.
- The Pull Request proposes actual implementation changes.
- Code review evaluates those changes.
- Approvals record reviewer decisions.
- Branch protection enforces repository-level requirements.
- Merge eligibility determines whether the change can enter the protected branch.

## Limitations

The scoring models are deliberately simple decision-support mechanisms. Real architecture decisions may require capacity planning, load testing, threat modeling, regulatory analysis, operational cost modeling, and production telemetry.

The examples do not attempt to reproduce every feature of a commercial repository platform.

The PostgreSQL model captures important governance relationships but does not implement a complete source-control system.

The workflow states are intentionally explicit so that product and engineering decisions can be examined independently of any particular repository hosting implementation.

## File Structure

The six deliverables are designed as independent artifacts:

| File | Purpose |
|---|---|
| Python | Domain simulation and architecture evaluation |
| JavaScript | Event-driven collaboration workflow |
| C++17 | Governance and readiness engine |
| Java 17 | Enterprise policy-oriented domain model |
| PostgreSQL | Relational collaboration and repository-governance model |
| README.md | Technical description of the complete model |

## Execution Characteristics

The Python file requires only the Python standard library.

The JavaScript file uses Node.js built-in modules and requires no npm packages.

The C++ program requires a C++17-compatible compiler and uses only the standard library.

The Java program requires Java 17 or later and uses only the standard Java runtime.

The PostgreSQL script requires PostgreSQL features including enums, PL/pgSQL functions, triggers, views, CTEs, indexes, and transactional SQL.

All examples are self-contained and use deterministic sample scenarios so that workflow behavior and policy decisions can be inspected directly.
