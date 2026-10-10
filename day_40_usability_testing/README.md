# Usability Testing: Planning, Observation, Problem Analysis, and Iteration

## Purpose and scope

Usability testing evaluates whether representative people can use an interface to accomplish realistic goals. It examines actual interaction behavior, task outcomes, errors, hesitation, assistance, and participant perceptions rather than relying exclusively on opinions about a design.

This project models a moderated usability study for an enterprise procurement portal. Procurement officers must locate approved suppliers, compare quotations, and submit purchase requests. These workflows are useful research scenarios because their interfaces can create materially different outcomes: selecting a supplier with pending approval, choosing a low-priced but non-compliant quotation, or submitting a request without receiving clear confirmation.

The six deliverables approach usability testing from complementary perspectives. Python provides a study-analysis workflow, JavaScript models event-driven observation and asynchronous sessions, C++ develops a performance-analysis case study, Java implements an enterprise domain model with controlled state transitions, PostgreSQL stores relational research evidence, and this README explains how their mechanisms relate.

The implementations use illustrative research data. Their measurements demonstrate analysis techniques, not statistically established findings about a real procurement product.

## Research planning

A usability study begins with a decision that the research must inform. A broad objective such as improving usability is insufficient to guide task selection, observation, or analysis.

The procurement study focuses on three questions:

| Research question | Observable behavior | Design decision supported |
|---|---|---|
| Can users identify a supplier with active approval? | Search terms, filter use, selected supplier, verification of approval status | Improve supplier discovery and distinguish approval states |
| Can users identify the lowest-priced compliant quotation? | Comparison actions, compliance checks, sorting, selected offer | Present compliance and cost together |
| Can users submit a request and verify its status? | Form completion, validation errors, submission actions, confirmation checks | Improve submission feedback and status visibility |

Each question connects a design uncertainty to evidence that can answer it. A research question that cannot be connected to observable behavior risks producing vague conclusions.

### Participant recruitment

Participant characteristics affect what the results can establish. A procurement application should be evaluated with people who understand the relevant work, including frequent and occasional system users when both groups represent the intended audience.

The examples distinguish participants by role and experience. These fields allow researchers to examine whether a problem appears across different user groups instead of treating all sessions as interchangeable.

Participant selection should follow the study's purpose. A small formative study can reveal important interaction problems without establishing population-wide prevalence. A formal quantitative comparison requires a sample and procedure appropriate to the statistical claim.

Consent is an enrollment condition in the implementations. A participant who has not consented must not be enrolled in the modeled study. Pseudonymous identifiers also help keep research records separate from unnecessary personal information.

### Task design

A usability task describes a realistic goal without prescribing the interface path.

For example, the participant is asked to find a supplier whose electrical-equipment category and approval status meet a purchasing requirement. The task does not tell the participant to open a particular menu, use a particular filter, or select a specific button. Those actions are the behavior under investigation.

Each task includes:

- A realistic scenario that supplies the participant's goal and relevant context.
- Observable success criteria that define what constitutes successful completion.
- An expected outcome that distinguishes a correct result from merely reaching the end of a screen.
- A time limit that provides a consistent boundary for the session.

The criteria are intentionally more precise than a vague instruction to find a supplier. Selecting a supplier is not sufficient if the selected supplier lacks active approval.

Time limits must also be interpreted carefully. Exceeding a limit can indicate difficulty, but a time-limit breach does not automatically prove that the final outcome was incorrect. The programs retain outcome and duration as separate measures.

## Conducting a session

### Moderated observation

In moderated testing, a facilitator introduces the task, observes the participant, and may ask neutral questions to understand the interaction. The facilitator should avoid giving instructions that solve the task.

A consistent session procedure improves comparability. Participants should receive equivalent task wording, environmental conditions, and opportunities for assistance. If a moderator intervenes, the intervention should be recorded because it affects the interpretation of task success.

Think-aloud methods can reveal expectations and confusion. They also change the interaction by asking participants to verbalize their reasoning, so the technique should be applied consistently and interpreted with that limitation in mind.

### Observation versus interpretation

The implementations distinguish observable evidence from interpretation.

An observation such as “selected a supplier whose approval was pending” describes a visible action and its outcome. An interpretation such as “the approval label was ambiguous” proposes an explanation for the behavior.

The interpretation may be plausible, but it should remain a hypothesis until supported by additional evidence. The participant may have overlooked the label, misunderstood the terminology, or been distracted by another element.

A strong finding connects the interpretation to recorded behavior and proposes a change that can be evaluated in a later study.

### Event records

The JavaScript and SQL implementations preserve event-oriented evidence. An event records a time, action type, target element, and description. Examples include applying a filter, selecting an unsuitable quotation, encountering validation, requesting help, and verifying a confirmation.

Event timing allows researchers to reconstruct the sequence of interaction. It can reveal that a participant sorted by price before checking compliance, even when the final task outcome alone does not explain the mistake.

The JavaScript recorder rejects negative timestamps and events recorded after a session has closed. It also checks that observation times do not move backward. These rules protect the internal consistency of a session record.

Events should remain descriptive. A click on a control does not prove that the participant understood it, and a long pause does not establish the participant's mental state without further evidence.

## Measuring task performance

Usability analysis combines quantitative measures with qualitative evidence. No single metric fully describes the quality of an interaction.

### Completion rate

Strict task completion rate is the proportion of participants who achieve the defined success criteria.

\[
\text{Success rate} =
\frac{\text{Successful task outcomes}}
{\text{Recorded task outcomes}}
\]

The denominator must be explicit. If participants abandon a task or fail to complete it, those outcomes should not silently disappear from the analysis.

Partial completion is tracked separately. The proportion of successful or partially completed tasks can help distinguish total failure from incomplete progress, but it must not be reported as the strict success rate.

### Time on task

Duration measures how long a task takes. The Python, C++, Java, and SQL implementations report successful-task duration or related duration statistics.

The median is useful when a small number of very long sessions would distort the mean. For example, several participants may complete supplier discovery quickly while one participant spends a long time exploring the filters. The median is less sensitive to that extreme observation.

Duration is meaningful only alongside task correctness. A fast selection of an unapproved supplier is not a successful usability outcome.

The treatment of failures also matters. Successful-task duration excludes failed attempts in several implementations, so it must not be interpreted as the average time required by every participant. Failure duration should remain available for analyses that specifically investigate time to failure or abandonment.

### Errors and assistance

Error counts capture predefined events such as incorrect selections and validation failures. Assistance counts capture interventions or help requests that reduce the independence of task completion.

Error definitions must be established before analysis. Repeatedly clicking a control, choosing the wrong quotation, and entering an invalid quantity represent different behaviors and may require separate event categories.

Assistance can also have different meanings. A request for clarification about the scenario is not necessarily an interface problem, while a request for help distinguishing approval states may indicate a design issue.

The event model makes these distinctions recordable instead of combining all difficulty into one score.

### Confidence ratings

The examples use a five-point confidence rating recorded after task completion. This measure captures the participant's reported certainty, not objective correctness.

A participant can complete a task successfully while remaining unsure whether the result is correct. Conversely, high confidence can accompany an incorrect selection. Confidence is therefore interpreted alongside observed behavior, completion, and errors.

## Identifying and prioritizing usability problems

A usability problem describes a barrier to successful interaction. It should include the affected task, supporting evidence, consequence, and a proposed design change.

The procurement case study includes three distinct findings.

| Finding | Observed problem | Proposed design change |
|---|---|---|
| Supplier approval | Participants confuse pending approval with active approval | Use explicit status labels, approval dates, and an approved-only filter |
| Quotation comparison | A low raw price attracts selection before compliance is checked | Display compliance beside total cost and identify the lowest compliant offer |
| Request submission | Ambiguous confirmation leads to repeated submission attempts | Display a persistent confirmation and unique request reference |

These problems require different interventions. Renaming an approval status will not solve the quotation comparison problem, and adding a price column will not clarify whether a purchase request has been submitted.

### Severity, frequency, and impact

The examples use a transparent prioritization score:

\[
P = S \times \ln(1+F) \times I
\]

where:

- \(S\) is the numerical weight associated with severity.
- \(F\) is the number of affected participants.
- \(I\) is an estimated impact between zero and one.

Severity distinguishes cosmetic problems from issues that prevent task completion or produce materially incorrect outcomes. Frequency estimates how often a problem occurs in the observed sample. Impact expresses its estimated consequence.

The logarithm reduces the influence of frequency as counts increase, while severity and impact preserve the importance of consequential problems.

This formula is an illustrative triage mechanism, not a validated universal usability scale. Its output depends on the definitions and judgments supplied by the research team. Two findings with similar scores may have different operational consequences, so the score should support discussion rather than replace judgment.

The implementations retain evidence and proposed changes with each finding. This helps prevent a numerical ranking from becoming detached from the behavior that justified the problem.

## Design iteration

Usability testing becomes an iterative engineering process when findings lead to specific interface changes and the revised interface is evaluated against comparable tasks.

A typical iteration proceeds through a traceable chain:

**Research question → task → observation → finding → design change → repeat test → comparison**

The relationship matters. A finding about approval labels should lead to a change in approval presentation or filtering. The next study should include a task that tests whether participants can now distinguish active and pending suppliers.

### Comparing versions

The examples compare a baseline version with a candidate design using task-level success rates, durations, errors, and assistance.

The SQL implementation stores iteration-specific task metrics in `iteration_task_metrics`. This allows comparisons even when the complete raw session data for every version is not yet in the database. The included candidate measurements are explicitly illustrative.

A positive change in success rate and a reduction in time may indicate improvement, but these measures do not prove that the design change caused the difference. Participant composition, familiarity with the task, session conditions, and other changes may explain part of the result.

For a meaningful comparison, keep task wording, success criteria, measurement definitions, and testing conditions as consistent as practical. When participant learning may influence results, account for the testing design rather than interpreting every improvement as a direct interface effect.

### Fixing versus verifying

A reported issue is not resolved merely because a developer changes the interface. The revised interface must be evaluated against the problem that motivated the change.

The Java program models this distinction through the finding lifecycle:

- `OPEN` identifies an issue requiring attention.
- `IN_PROGRESS` indicates that work on the issue has begun.
- `FIXED` records that an implementation change has been made.
- `VERIFIED` records that subsequent evidence supports the fix.
- `ACCEPTED_RISK` represents an explicit decision to retain the issue.

The Java and SQL implementations restrict state transitions. An open finding cannot move directly to verified, because implementation and verification are separate activities. A verified issue may return to in-progress if later evidence shows that the change is inadequate.

This lifecycle prevents an administrative status from being mistaken for evidence of improved usability.

## Python implementation

The Python script builds a complete in-memory study with `StudyPlan`, `ResearchQuestion`, `Task`, `Participant`, `Observation`, `TaskResult`, and `UsabilityProblem` objects.

`StudyPlan.validate()` checks the basic study structure, including unique task identifiers and the presence of research questions. `UsabilityStudy` then controls participant enrollment, result recording, problem registration, metric calculation, and JSON export.

The analysis methods distinguish strict success from partial-or-success completion. They calculate median duration, mean errors, assistance requests, and mean confidence for each task. Empty measurement sets are handled explicitly rather than producing misleading numerical results.

The example data contains six participants completing three tasks, providing enough variation to demonstrate successful completion, partial completion, failure, assistance, and confidence ratings. The data is constructed for the example and is not a claim about a real product.

`problem_frequency()` attempts to derive participant counts from linked observations. In this demonstration, the supplied finding frequency is retained when it exceeds the observed linked count. This is a useful reminder that a production analysis system should maintain explicit relationships between each finding and the evidence records supporting it. Searching free-text notes for a problem identifier is not a robust substitute for a normalized finding-evidence relationship.

`compare_iterations()` reports absolute changes in success rate and median duration. It identifies missing task measurements rather than silently treating missing data as zero.

`export_json()` produces a structured record that can be inspected or passed to another analysis process. The script uses a temporary directory in its demonstration so that running it does not leave an unexpected report in the working directory.

The built-in `unittest` suite covers consent enforcement, invalid task references, negative error counts, duplicate results, completion-rate semantics, empty duration sets, priority behavior, and JSON serialization.

## JavaScript implementation

The JavaScript file uses an event-driven architecture that suits interactive research tools.

`SessionRecorder` extends Node.js `EventEmitter`. When an observation is recorded, the recorder stores an immutable `EvidenceEvent` and emits an `observation` event. A workbench listener collects those events without coupling the observer interface directly to the analysis logic.

The recorder enforces session lifecycle rules. It rejects observations after closure and timestamps that move backward. These checks help ensure that event sequences remain usable for reconstructing participant behavior.

`UsabilityWorkbench.runSession()` accepts an asynchronous task-execution function. This allows the same structure to support a scripted demonstration or an adapter that observes a real interactive prototype. It measures elapsed time with Node.js high-resolution timing and records execution failures separately from ordinary task outcomes.

`TaskEvaluator` classifies errors using event types and calculates assistance requests from recorded evidence. It reports time-limit overruns without automatically rewriting a successful result as a failure.

The implementation also uses private class fields, immutable result records, validation errors, and assertions. Private fields prevent outside code from directly modifying the recorder's internal event collection. Immutable events reduce the risk that an observer or analysis listener accidentally changes stored evidence.

`ProblemRegister` assigns a transparent priority score to findings. `IterationEvaluator` compares baseline and candidate metrics while identifying tasks that cannot be compared because one version lacks data.

In a production system, event instrumentation would need to connect to actual interface interactions. Instrumentation should avoid collecting credentials, unnecessary personal information, or sensitive form contents. Observation records should also distinguish a failed action from an event that was never captured.

## C++ case study

The C++ program models a procurement usability study as a typed analytical workbench.

`TaskDefinition` contains the scenario, observable success criteria, and time limit. `Participant` records a pseudonymous identifier and experience category. `TaskResult` contains an outcome, duration, error count, assistance requests, optional confidence, and observations.

`GovernanceWorkbench` uses `std::map` for deterministic task, participant, and problem lookup. It rejects duplicate identifiers and task results referring to unknown participants or tasks. A participant cannot have multiple final results for the same task in this case-study model.

The metric calculation separates strict success from partial-or-success completion. It sorts successful-task durations to calculate a median, handles an even number of observations by averaging the two central values, and preserves the absence of successful durations as `std::nullopt`.

`UsabilityProblem` validates its affected task references and evidence before registration. Its priority score combines severity, frequency, and impact. The program sorts findings by that score and displays the proposed change alongside the problem.

The release-oriented example demonstrates how a research team can use measured task success and assistance to identify work that requires another design iteration. The illustrative threshold is not a universal release criterion. Organizations should set thresholds according to the consequences of an incorrect or incomplete task.

The program uses standard containers and sorting. If there are \(N\) task results, the current task metric method scans the result collection, giving an \(O(N)\) scan per task. Sorting \(K\) successful durations adds \(O(K \log K)\) work. This is suitable for a small study; larger research datasets would benefit from grouping results by task before repeated analysis.

C++ exceptions reject invalid data at the boundary of the workbench. The executable reports a controlled failure instead of continuing with invalid records.

## Java enterprise model

The Java program emphasizes domain modeling, immutable records, and controlled state transitions.

Records such as `ResearchQuestion`, `TaskDefinition`, `Participant`, `Observation`, `TaskResult`, and `ProblemEvidence` validate their own invariants. Lists and sets are defensively copied, preventing callers from changing the collections after a record has been created.

`StudyPlan` maps task identifiers to definitions. `StudyService` coordinates enrollment, result recording, findings, metrics, and release assessment. It checks participant enrollment before accepting a result and prevents duplicate final results for a participant-task pair.

The `UsabilityFinding` class owns its status transition rules. A finding cannot move from open directly to verified. It must move through implementation and then verification, unless the issue is explicitly accepted as a risk. Invalid transitions raise `IllegalStateException`.

`ReleasePolicy` expresses acceptance criteria as explicit values: minimum task success, maximum assistance, blocking severity levels, and whether critical findings must be verified. `evaluateRelease()` applies these rules to the available evidence.

The release result is a decision aid rather than a claim that the interface is universally usable. The study must still meet its recruitment, task coverage, and evidence-quality requirements. In particular, a metric calculated from very few participants may be too uncertain to justify a high-consequence release decision.

The model uses Java 17 language features and standard collections, streams, records, enums, and exception handling. It requires no external dependencies.

## PostgreSQL data model

The SQL script stores research data in related tables instead of keeping all observations and findings in a single JSON document.

| Table | Responsibility |
|---|---|
| `studies` | Defines the objective, environment, recruitment criteria, moderator script, and analysis plan |
| `research_questions` | Connects research uncertainties to the design decisions they support |
| `study_tasks` | Stores task scenarios, expected outcomes, success criteria, order, and time limits |
| `participants` | Stores pseudonymous participants, roles, experience levels, and consent status |
| `sessions` | Stores one participant's result for a task |
| `observations` | Records timestamped behavior and evidence classification |
| `usability_problems` | Tracks findings, severity, impact, proposed changes, and lifecycle status |
| `problem_tasks` | Associates findings with the tasks they affect |
| `problem_evidence` | Connects findings to observations or separately documented evidence |
| `design_iterations` | Identifies the interface versions evaluated |
| `iteration_task_metrics` | Stores comparable task measurements for each version |
| `design_decisions` | Records the decision, rationale, owner role, and due date |

Primary keys identify records, while foreign keys preserve relationships. Unique constraints prevent duplicate task codes within a study, duplicate pseudonyms within a study, and multiple final sessions for the same participant-task combination.

Check constraints reject invalid values such as negative error counts, out-of-range confidence ratings, non-positive time limits, and priority impacts outside the zero-to-one range.

The participant table requires consent to be recorded before enrollment. This is a simplified database-level control, not a substitute for a full consent-management process. A production system may need to model consent timestamps, consent versions, withdrawal, access controls, and retention requirements explicitly.

### Database-level consistency

The `validate_session_study_membership()` trigger prevents a session from combining a participant and task belonging to different studies. The `validate_problem_task_study()` trigger similarly prevents a finding from being linked to a task outside its study.

These relationships cannot be enforced by a simple foreign key alone because each record can reference individually valid rows from different studies. The triggers check the cross-record rule at write time.

The finding lifecycle trigger enforces legal transitions between open, in-progress, fixed, verified, and accepted-risk states. It prevents an open issue from being marked verified without first passing through the implementation stage.

These controls protect stored research consistency when records are written by different application components. Database constraints do not establish that the recorded observation is truthful, so evidence quality still depends on the study procedure.

### Analysis views

`task_performance` aggregates session outcomes and calculates strict completion, partial-or-success completion, successful-task duration, errors, assistance, and confidence.

The view uses PostgreSQL's filtered aggregate syntax to count each outcome without creating separate queries for success, failure, and abandonment. `NULLIF` prevents division by zero when a task has no sessions. Missing measurements remain null rather than being presented as zero success or zero duration.

`prioritized_problems` combines severity, impact, and linked evidence counts into a transparent ranking. The query counts distinct participants and evidence records to avoid treating repeated joins as additional independent participants.

The iteration comparison joins baseline and candidate measurements by task. It reports changes in success rate, median duration, and mean errors. It keeps each version's participant count in the denominator and does not assume that candidate measurements come from the same participants.

### Transactions and indexes

The SQL script runs its schema and sample-data operations inside a transaction. A failure can be surfaced by `psql` with `ON_ERROR_STOP` so that the setup does not silently continue through dependent operations.

The indexes support common access patterns: study and task outcome analysis, participant session history, chronological observation retrieval, problem triage, evidence lookup, and iteration comparison. Each index adds storage and write overhead, so a production schema should validate index usefulness against real query plans and data volume.

The script includes representative sessions and an illustrative candidate iteration. Candidate metrics are intentionally marked as illustrative in the surrounding documentation because the comparison should not be misrepresented as measured improvement from the baseline participants.

## Common analytical failure modes

**Treating task completion as proof of usability.** A participant may reach the correct result only after moderator assistance or repeated mistakes. Report assistance and errors alongside completion.

**Counting partial outcomes as strict success.** This inflates the apparent success rate when success criteria have not been met. Keep the outcome categories distinct.

**Equating speed with correctness.** Fast interaction may reflect familiarity or an incorrect shortcut. Interpret duration alongside the selected result and observed actions.

**Turning a hypothesis into a fact.** An observed mistake is evidence. Its explanation is a hypothesis that should be tested against other observations or follow-up questions.

**Prioritizing only by frequency.** A rarely encountered issue can still be critical if it causes a high-consequence error. Consider severity and impact as well as recurrence.

**Declaring a fix complete without verification.** A code change can leave the original interaction problem unresolved or introduce another problem. Verify the change using relevant tasks and evidence.

**Comparing incompatible studies.** Changes in participants, task wording, success criteria, or testing conditions can affect the metrics. Document these differences before drawing conclusions from iteration comparisons.

## Practical interpretation

The six implementations show how usability research can move from a planned question to observable evidence, measurable outcomes, prioritized findings, and verified design changes.

The essential relationship is between the decision under consideration and the evidence needed to support it. Task scenarios expose real interaction behavior; observations preserve the sequence and context of that behavior; analysis distinguishes successful outcomes from partial progress and failure; findings identify specific barriers; and iteration testing determines whether the proposed changes actually address those barriers.

The resulting study record is most useful when another researcher can trace a design decision back to the task, observation, finding, and subsequent validation that support it.
