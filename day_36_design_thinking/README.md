# Design Thinking: Empathize, Define, Ideate, Prototype, Test

## Scope

This learning artifact implements the five-stage Design Thinking process as an evidence-driven product and service design workflow:

**Empathize → Define → Ideate → Prototype → Test → Iterate**

The implementations use a common scenario: improving the experience of employees who process internal requests. The scenario is intentionally operational rather than abstract. Users struggle with fragmented information, unclear request state, incomplete decision context, and weak explanations of blocked work.

The five stages are related, but they perform different reasoning functions.

- **Empathize** establishes evidence about people, behavior, context, and pain points.
- **Define** converts synthesized evidence into a focused problem worth solving.
- **Ideate** creates and evaluates multiple possible responses before implementation.
- **Prototype** makes selected assumptions tangible at an appropriate fidelity.
- **Test** observes people interacting with the prototype and produces evidence for another design iteration.

Design Thinking is therefore not simply a five-step checklist. The stages form a learning loop in which evidence can cause the team to revise an earlier decision.

---

## The Design Thinking Model

### Empathize

Empathy in this implementation means understanding users through observed behavior and contextual evidence rather than beginning with a proposed feature.

The Python program records:

- the user's role and working context;
- observable behavior;
- user language or quotes;
- pain points;
- evidence strength.

The evidence deliberately distinguishes what a person does from what the design team assumes the person needs. For example, repeatedly copying queue information into a spreadsheet is observable behavior. The conclusion that visibility is inadequate is an interpretation that must be supported by additional evidence.

The JavaScript implementation extends this idea through immutable observation records and validation. An observation without a user, behavior, or pain point is rejected because it cannot provide a useful unit of evidence.

The SQL model represents observations as first-class relational records. A foreign key connects each observation to both a project and a user, preserving traceability between evidence and its source.

### Define

Definition is the transition from scattered observations to a meaningful problem frame.

The implementations use a problem statement containing:

- the user group;
- the unmet need;
- the evidence-backed insight;
- a measurable outcome.

This separation prevents a common design error: defining a solution before defining the problem.

For example, "build a dashboard" is a solution proposal. "Employees need a contextual workflow that exposes request state, evidence, and next action" is a problem-oriented need. The latter leaves room for multiple solutions during ideation.

The programs select high-confidence insights from the empathy evidence before constructing the problem statement. This creates an explicit relationship between observation, synthesis, and problem framing.

### Ideate

Ideation deliberately introduces alternatives.

The case study evaluates three principal concepts:

| Concept | Purpose | Design distinction |
| --- | --- | --- |
| Contextual Request Workspace | Unify state, evidence, history, and next action | Addresses fragmented workflow context |
| Decision Summary Panel | Present decision-relevant evidence | Addresses approval decision context |
| Blocker Explanation Engine | Explain why work cannot proceed | Addresses diagnosability of blocked work |

The scoring model considers user value, feasibility, desirability, and risk. The score is not a substitute for human judgment. It provides a transparent mechanism for comparing alternatives and documenting why one concept was selected for prototyping.

The Python, C++, and Java implementations calculate the same type of weighted decision score, while the JavaScript version stores the calculated score directly with each idea.

The SQL implementation exposes the calculation through the `idea_evaluation` view so that concept comparison can be performed at the database layer.

### Prototype

A prototype converts assumptions into something that can be inspected or interacted with.

The selected prototype is a medium-fidelity representation of a contextual request workspace. Its interactions include filtering a queue, opening request context, inspecting evidence, identifying blockers, and performing the next action.

The prototype does not attempt to represent an entire production system. Its purpose is to test important assumptions cheaply.

The implementations explicitly store assumptions such as:

- users should be able to identify the next action without changing screens;
- decision evidence should be available at the point of decision;
- blocked requests should expose the information required for recovery.

These assumptions are important because a prototype is useful only when the team knows what it is trying to learn from it.

### Test

Testing in the case study focuses on observable behavior.

Each usability test records:

- participant;
- task;
- completion outcome;
- task time;
- error count;
- satisfaction score;
- qualitative observation.

The three example tests expose a meaningful pattern. Two participants complete their tasks successfully, while the manager fails to identify why one request is blocked.

That failure is treated as design evidence rather than as a failure of the participant.

The prototype therefore generates a new requirement: a blocked request should explicitly expose the missing information and the recovery action.

This is the iterative nature of Design Thinking. Testing can return the process to prototyping, problem definition, or even empathy research when the evidence shows that an earlier assumption was incorrect.

---

## Evidence, Insight, and Problem Are Different

A strong Design Thinking workflow maintains a distinction between observation and interpretation.

An observation such as:

> A user copies request information into a separate spreadsheet.

is evidence.

An insight such as:

> Users experience uncertainty because request state is difficult to see.

is a synthesis of evidence.

A problem statement such as:

> Employees need a contextual workflow that exposes state, evidence, and next action.

is a design framing decision.

These three levels should not be collapsed into one statement. Doing so makes it difficult to determine whether a conclusion is supported by research or merely assumed by the design team.

The Python implementation preserves this distinction through separate `Observation`, `Insight`, and `ProblemStatement` structures. The SQL implementation enforces the same separation through separate tables and relationships.

---

## Python Implementation

The Python program is a complete executable simulation of the design process.

Its domain model includes:

- `User` for participant context;
- `Observation` for empirical evidence;
- `Insight` for synthesized findings;
- `ProblemStatement` for problem framing;
- `Idea` for alternative concepts;
- `Prototype` for explicit assumptions and interactions;
- `TestResult` for usability evidence;
- `DesignThinkingProject` for the complete project state.

The `collect_empathy` function establishes realistic user evidence. `synthesize_insights` groups observations by pain point and calculates evidence confidence. `define_problem` constructs the problem frame from synthesized insights.

The `ideate` function evaluates alternative concepts using a weighted score. `build_prototype` selects the strongest concept and converts it into a testable prototype. `run_usability_test` records behavioral evidence, while `analyze_test_results` converts the observations into measurable test metrics.

The program also validates test data and persists the complete design evidence temporarily as JSON. This demonstrates an important production consideration: design decisions should be traceable to the evidence that produced them.

The final iteration step adds a new prototype assumption after a usability failure. This prevents the five stages from being treated as a rigid one-way pipeline.

---

## JavaScript Implementation

The JavaScript program models Design Thinking as an event-driven workflow.

The `DesignProject` class owns project state and validates observations, ideas, and test results. Its `transitionTo` method prevents arbitrary stage skipping while still allowing iterative movement back to earlier stages when new evidence requires it.

JavaScript's asynchronous execution model is used for usability sessions. `runUsabilitySession` returns a Promise, representing a test session that may involve asynchronous events such as user interaction, browser activity, telemetry, or external data collection.

The `DesignEventBus` provides a lightweight event-driven mechanism. A completed test emits an event that another component can consume without coupling the test implementation directly to reporting logic.

The implementation also uses JavaScript-specific structures such as `Map`, `Object.freeze`, `Promise`, `async/await`, and `console.table`.

The prototype is revised when the test completion rate is below 100 percent. The revised assumption explicitly addresses the observed blocker problem.

---

## C++ Case Study

The C++ program models a repository-independent enterprise design engine for an internal request-processing experience.

Its central class, `GovernanceExperienceEngine`, owns users, observations, insights, ideas, the problem statement, the prototype, and usability results.

The implementation uses:

- `enum class` for strongly typed design stages;
- `struct` for domain records;
- `std::vector` for ordered project evidence;
- `std::map` for grouping observations by pain point;
- `std::optional` for problem and prototype state that may not yet exist;
- standard algorithms for ranking ideas and finding failed tests;
- explicit exceptions for invalid workflow state.

The case study separates design-stage transitions from design artifacts. A project cannot create a prototype without ideas, cannot define a problem without insights, and cannot evaluate usability without test results.

The idea-ranking algorithm uses a weighted score:

`user value × 0.40 + feasibility × 0.25 + desirability × 0.25 − risk × 0.10`

The complexity of ranking depends on the number of candidate ideas. Sorting the candidate ideas is `O(n log n)`, while selecting a single maximum concept can be performed in `O(n)`.

The test-analysis operation scans all recorded tests and therefore runs in `O(n)` time apart from sorting when a median is calculated.

The important architectural decision is that test failures are not converted into automatic product requirements. The engine identifies the failed task and surfaces it as an iteration trigger. Human interpretation remains responsible for deciding what the evidence means.

---

## Java Enterprise Model

The Java implementation uses explicit domain types to represent an enterprise design workflow.

Java records provide immutable representations for users, observations, insights, problem statements, ideas, prototypes, and test results.

The `DesignRepository` manages the accumulated project evidence, while `DesignService` owns workflow behavior such as stage transitions, insight synthesis, problem definition, prototype selection, and test evaluation.

The separation between repository and service reflects a useful enterprise design distinction:

- the repository represents stored design evidence;
- the service represents rules that transform and evaluate that evidence.

The `Idea` record contains a domain-level `score()` method, keeping the scoring rule close to the data it evaluates.

The service prevents skipping design stages. The model also represents failures explicitly through `TestOutcome`, allowing a failed usability task to remain distinguishable from a successful task with a low satisfaction score.

Java streams are used for grouping, ranking, filtering failed tests, and calculating aggregate metrics. Immutable lists returned by the repository reduce accidental modification of stored design evidence.

---

## SQL Data Model

The PostgreSQL implementation treats Design Thinking evidence as relational data.

The principal entities are:

- `design_projects` represents a design initiative and its current stage.
- `users` represents people participating in research or testing.
- `observations` stores observed behavior and pain points.
- `insights` stores synthesized findings.
- `insight_evidence` links insights back to observations.
- `problem_statements` stores the defined design problem.
- `ideas` stores alternative concepts and their evaluation dimensions.
- `prototypes` identifies the concept being tested.
- `prototype_interactions` stores interactions represented by the prototype.
- `prototype_assumptions` records assumptions that testing is intended to examine.
- `usability_tests` stores behavioral test results.

Foreign keys preserve relationships between these entities. For example, an insight cannot reference an observation that does not exist, and a prototype cannot reference a nonexistent idea.

Check constraints enforce domain rules at the database level. Evidence strength must remain between zero and one. Idea dimensions must remain between zero and ten. Satisfaction must remain between one and five. Task time must be positive, and error counts cannot be negative.

The `idea_evaluation` view calculates concept scores. The `project_test_metrics` view calculates completion rate, average time, error rate, and satisfaction.

Indexes are placed on common analytical access paths such as project and pain-point combinations, idea evaluation fields, and test outcomes.

The SQL script also demonstrates a transaction for modifying the prototype after usability evidence identifies a problem. The revised assumption is stored as part of the prototype rather than being left only in an informal report.

---

## Relationships Between the Five Stages

The stages have different responsibilities and should not be treated as interchangeable.

**Empathize produces evidence.**

The team observes people in context and records behavior, pain points, and relevant statements.

**Define produces a problem frame.**

Evidence is synthesized into insights and converted into a focused need and measurable outcome.

**Ideate produces alternatives.**

The team generates multiple possible responses instead of prematurely committing to the first plausible solution.

**Prototype produces a testable representation.**

The selected concept is expressed at a fidelity appropriate to the questions being investigated.

**Test produces behavioral evidence.**

Users interact with the prototype, and the team measures completion, errors, time, satisfaction, and qualitative observations.

The output of testing can become input to another iteration. A test failure may indicate that the prototype is inadequate, that the problem was framed incorrectly, or that the team misunderstood the user's context.

---

## Design Decisions Demonstrated by the Case Study

### Evidence strength

Evidence strength is represented as a value between zero and one. It is not a universal statistical confidence interval. It is a project-level representation of how strongly the available observation supports an insight.

Using such a value makes the example computationally useful while preserving the distinction between design evidence and formal statistical inference.

### Weighted idea evaluation

The idea score balances user value, feasibility, desirability, and risk.

A high user-value idea can still lose to another concept if it is substantially less feasible or carries considerably higher risk.

The score is therefore a prioritization mechanism rather than proof that one concept is objectively superior.

### Medium-fidelity prototyping

Medium fidelity is selected because the scenario requires users to evaluate workflow behavior, information visibility, and decision context.

A low-fidelity sketch may be insufficient to test interaction sequencing, while a production implementation would introduce unnecessary engineering cost before the critical assumptions are validated.

### Behavioral testing

The test dataset combines quantitative and qualitative evidence.

Completion rate shows whether participants can perform the task. Task time indicates effort. Error count exposes friction or misunderstanding. Satisfaction provides a subjective measure. The qualitative observation explains what happened.

None of these measures is sufficient by itself.

---

## Edge Cases and Failure Conditions

The implementations explicitly reject several invalid states.

An observation without a participant, behavior, or pain point cannot be useful research evidence.

Evidence strength outside the allowed range is rejected.

An idea with scores outside the defined scoring scale is invalid.

A prototype cannot be created when no idea exists.

A problem cannot be defined before insights have been synthesized.

A usability result with a non-positive task duration is rejected.

Negative error counts are rejected.

Satisfaction values outside the one-to-five range are rejected.

A design workflow cannot silently skip from Empathize to Prototype because doing so would remove the Define and Ideate reasoning stages.

A failed usability task does not automatically mean that the entire product is invalid. It is an evidence signal that must be interpreted and converted into an appropriate design change.

---

## Common Design Errors Addressed

### Starting with a solution

Building a dashboard, application, or automation before understanding the user's actual context can produce a technically polished response to the wrong problem.

The workflow therefore places problem definition before solution selection.

### Treating opinions as observations

"I think users need a dashboard" is an assumption.

"A user manually copies request status into a separate spreadsheet" is an observation.

The distinction matters because design decisions should be traceable to evidence.

### Selecting the first idea

Ideation creates alternatives so that the team can compare different responses to the same need.

The example deliberately evaluates a workspace, decision panel, and blocker explanation mechanism.

### Building too much before testing

The prototype represents only the interactions required to test important assumptions. This keeps learning cheaper than production implementation.

### Testing only satisfaction

A participant may report high satisfaction while still failing a task.

The example therefore records completion, time, errors, satisfaction, and qualitative observations together.

### Treating the process as strictly linear

A failed test produces a new prototype assumption. This illustrates that Design Thinking is iterative rather than a one-way sequence.

---

## Performance and Production Considerations

The computational operations in these examples are intentionally small, but the underlying design principles remain relevant for larger systems.

Grouping observations by pain point can be implemented with hash-based structures for approximately linear expected performance.

Ranking a large idea set requires sorting when a complete ordered ranking is needed, resulting in `O(n log n)` complexity.

Aggregating test metrics is naturally a linear operation over the test dataset.

In a production environment, design evidence should be immutable or versioned where auditability is important. Changes to problem statements, assumptions, prototypes, and research findings should preserve historical context rather than silently overwriting previous conclusions.

Sensitive user research should also be protected. Real research records may contain personal information, workplace behavior, interview transcripts, or other sensitive material. Access control, minimization, retention rules, and appropriate anonymization should be applied before using such data in shared systems.

Database constraints should enforce basic structural validity, while application services should enforce higher-level workflow rules.

---

## Security and Privacy Considerations

Design research frequently contains information about real people. A production implementation should avoid storing unnecessary identifying information when participant identity is not required.

The example uses short synthetic user identifiers. This makes relationships between observations and participants possible without requiring real personal data.

A production system should distinguish between:

- participant identity;
- research evidence;
- analytical findings;
- prototype artifacts;
- test results.

Access to raw observations may need stricter controls than access to aggregated insights.

Audit records can be valuable when design decisions influence operational systems because they allow a team to determine which evidence supported a particular decision.

---

## Debugging and Decision Traceability

The implementations make debugging easier by separating the stages and their artifacts.

If an idea is weak, the team can inspect its scoring dimensions.

If a problem statement appears unsupported, its originating insights and observations can be examined.

If a prototype performs poorly, the relevant assumptions can be inspected.

If a usability metric deteriorates, individual task records can reveal whether the change is caused by longer completion time, more errors, lower completion, or lower satisfaction.

The SQL relationship between `insights`, `insight_evidence`, and `observations` is particularly useful for tracing an insight back to its empirical source.

This traceability reduces the risk of turning an undocumented assumption into an apparently authoritative design requirement.

---

## Practical Interpretation of the Case Study

The central finding in the example is not simply that users want a better dashboard.

The evidence indicates several related problems:

- request state is difficult to see;
- information is distributed;
- decision context is incomplete;
- blocked work lacks useful explanation.

The ideation stage therefore considers different intervention points rather than treating all problems as one interface problem.

The selected contextual workspace becomes a prototype because it addresses several observed workflow problems while remaining testable without implementing the entire production system.

Testing then reveals a narrower usability problem: the blocked state communicates that something is wrong but does not clearly identify what the user needs to do.

The next design iteration consequently changes the prototype assumption rather than merely recording a low satisfaction score.

That sequence demonstrates the central value of the method: **evidence changes the design**.
