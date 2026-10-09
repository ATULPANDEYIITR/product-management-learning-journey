# Prototype Fidelity: Low, Medium, and High Fidelity

## Purpose and scope

Prototyping is the practice of constructing a representation of a proposed product or interaction so that specific design assumptions can be examined before the full product is implemented. A prototype may represent screen layout, navigation, task sequence, interaction feedback, or increasingly realistic system behavior.

This project uses an enterprise expense-management workflow as a consistent design context. Employees need to locate the expense submission action, enter a description and amount, select a category, submit the form, and understand whether the operation succeeded. The examples examine how different prototype fidelity levels support different research questions.

Fidelity is the degree to which a prototype represents selected characteristics of the intended product. It is not a single measure of quality. A prototype can closely resemble the intended visual design while inaccurately representing its business rules. Another can look like a paper sketch while providing strong evidence about task sequence and information architecture.

## Fidelity as a design decision

Low, medium, and high fidelity describe different levels of representation. They are not mandatory stages that every project must follow in a fixed order. A team may return to a low-fidelity sketch after usability testing reveals a structural problem, or maintain a high-fidelity interaction model while exploring alternative visual layouts.

| Dimension | Low fidelity | Medium fidelity | High fidelity |
|---|---|---|---|
| Primary representation | Sketches, paper screens, rough layout | Structured screens with representative navigation and interactions | Detailed visuals and realistic interaction feedback |
| Typical research question | Is the task flow understandable? | Can users navigate and complete the task? | Do detailed states and feedback support correct behavior? |
| Visual detail | Minimal | Moderate | Usually high |
| Interaction behavior | Often simulated manually | Selected controls and transitions work | Many visible states and interactions behave realistically |
| Data behavior | Illustrative | Often simulated | Can include realistic local data and validation |
| Revision cost | Usually low | Moderate | Often higher |
| Important limitation | Cannot establish detailed interaction usability | May omit production behavior | Can create false confidence if backend and operational behavior remain simulated |

The correct fidelity depends on the uncertainty being investigated. Increasing visual detail before resolving a confusing task flow can consume time without improving the quality of the design decision.

## Low-fidelity prototyping

A low-fidelity prototype prioritizes structure, content hierarchy, and the sequence of actions. It may consist of paper screens, rough diagrams, or simple wireframes. Its primary value is the ability to change the proposed interface rapidly.

In the Python implementation, `LowFidelityPrototype` represents an expense dashboard, form, and confirmation screen using text. The representation makes the intended navigation and field placement visible without claiming to implement a working interface. The `PrototypeArtifact` data model separately records low-fidelity screens and elements, allowing the artifact to be inspected and compared with the more interactive alternatives.

The C++ case study also represents a paper sketch using elements that are explicitly non-interactive. This distinction matters because an element drawn on paper is not equivalent to a working control. Its appearance can help a researcher investigate whether a participant recognizes the primary action, but it cannot establish whether a real button handles clicks correctly.

A low-fidelity study should focus on questions such as whether employees recognize the submission action, understand the relationship between the dashboard and form, and expect to see a confirmation after submission. Participants can explain their intended actions while the facilitator changes paper screens.

Low fidelity is less appropriate when the research question depends on timing, error recovery, precise visual hierarchy, realistic loading states, or detailed input behavior. A paper form cannot demonstrate whether an asynchronous request disables a submit button or whether an inline error is understandable.

## Medium-fidelity prototyping

A medium-fidelity prototype provides a more structured representation of screens and selected interactions. It often includes representative typography, spacing, controls, navigation, and simplified form behavior without reproducing every production detail.

The Python `MediumFidelityPrototype` maintains a current screen, an editable form, navigation rules, and submission feedback. It allows the experiment to distinguish between a successful path and a failed attempt. Submitting from the wrong screen is rejected, and invalid amounts produce validation feedback rather than creating an expense.

The JavaScript implementation approaches medium fidelity through a configurable `DesignPrototype` and an event-driven `InteractivePrototype`. Its `navigate` method validates screen transitions, while `setField` checks whether the requested field exists and whether the form is currently open. These checks make interaction behavior explicit instead of assuming that every action is valid.

Medium fidelity is useful for testing whether users can complete a multi-screen task, recognize field labels, understand form order, and recover from common entry mistakes. It can reveal navigation problems that a static sketch cannot expose.

Its limitations depend on the interactions that have been implemented. A clickable prototype may navigate correctly while using simplified validation, fake network responses, or local state instead of a real server. Researchers must document those boundaries so that a successful demonstration is not mistaken for evidence that the production system is complete.

## High-fidelity prototyping

A high-fidelity prototype represents the intended interface and interaction behavior in greater detail. It may include realistic visual styling, loading indicators, confirmation messages, field-level validation, representative data, and detailed error states.

The Python `HighFidelityPrototype` exposes a view model containing the current screen, loading state, expenses, total amount, and recent messages. Its submission method simulates a bounded delay and resets the loading state in a `finally` block. That state reset is important because a validation failure must not leave the interface permanently indicating that a request is in progress.

The JavaScript version uses `EventEmitter` to expose events such as `loadingChanged`, `submitted`, and `validationFailed`. These events provide observable evidence about state transitions. The implementation also rejects a second submission while the first request is pending. This behavior supports an experiment about duplicate actions and loading feedback.

The Java program uses an explicit `SUBMITTING` screen state and an immutable `Expense` record. Its `PrototypeSession` moves to confirmation only when the expense service accepts the input. When validation fails, the session returns to the form and records an error message.

The C++ implementation models the same design concern through `PrototypeSession`. Its state transition to `Loading` is temporary, and invalid input returns the session to the editable form. The example also uses integer cents internally when calculating the ledger total, avoiding the accumulation of ordinary binary floating-point rounding errors.

High fidelity is valuable when the research question concerns detailed feedback, realistic interaction timing, error presentation, or visual hierarchy. It does not establish that the application is production-ready. A realistic front end backed by an in-memory service does not prove that authentication, persistence, network failure recovery, accessibility, concurrency, or operational monitoring will behave correctly in a deployed system.

## Choosing fidelity from the research question

Fidelity should follow the uncertainty under investigation rather than the amount of visual detail a team can produce.

| Research uncertainty | Suitable starting point | Evidence to collect |
|---|---|---|
| Users cannot identify the main action | Low | First action, task interpretation, navigation expectations |
| Users understand the screen but cannot complete the workflow | Medium | Completion, misdirected actions, form errors, recovery attempts |
| Users complete the workflow but misunderstand its status | High | Interpretation of loading and confirmation, repeated submissions, confidence |
| Users cannot understand an unclear field label | Low or medium | Interpretation of the label and expected value |
| Users struggle with detailed validation messages | Medium or high | Error recognition, correction behavior, time to recovery |
| Users report that the interface looks complete but behaves inconsistently | High, with explicit behavior coverage | State transitions, failure feedback, consistency across screens |

These choices are not exclusive. A research program may use paper screens to establish the task sequence, clickable screens to examine navigation, and a realistic interaction model to evaluate feedback. Each experiment should answer a defined question and record the evidence that supports its findings.

## Python implementation

The Python script combines prototype modeling with executable workflow experiments. It uses dataclasses to represent screens, artifacts, tasks, and observations. Enums constrain fidelity and lifecycle values, while custom exceptions distinguish invalid prototype transitions from invalid user interactions.

`build_prototypes` creates three distinct artifacts. Their screens and interactive elements provide inspectable structural evidence about fidelity. `compare_fidelity` counts screens and interactive elements without claiming that those counts are a universal measure of quality.

`ExpenseWorkflow` models the domain behavior used by the interactive examples. It validates descriptions, categories, and amounts before recording an expense. `MediumFidelityPrototype` handles navigation and form editing, while `HighFidelityPrototype` adds loading state, simulated latency, messages, and a view model.

`UsabilityReport` calculates completion rate, average task duration, total errors, and mean confidence from explicit participant observations. These measurements are descriptive rather than proof of statistical significance. Small convenience samples are useful for finding obvious usability problems, but stronger product decisions require a study design appropriate to the question.

The lifecycle methods distinguish drafts, testable artifacts, and retired artifacts. A published prototype can be revised while it remains active, but a retired artifact cannot be silently returned to use. This helps keep experiment history understandable.

Run the program with `python prototyping.py`. It requires Python 3.10 or later and uses only the standard library.

## JavaScript implementation

The JavaScript file emphasizes event-driven interactions and asynchronous state. `DesignPrototype` validates screen definitions, stores them in a `Map`, tracks lifecycle changes, and emits events when an artifact is published, revised, or retired.

`ExpenseService` uses private class fields for its in-memory ledger. It validates inputs before storing an immutable record and returns copies when listing records. Its asynchronous submission method uses a bounded timer to simulate latency. The timer supports controlled experiments with loading indicators and repeated submissions; it is not a network service.

`InteractivePrototype` emits state-related events and keeps the current screen, form values, pending state, and recent messages. The `finally` block in `submit` ensures that both success and failure clear the loading state. `TaskRecorder` validates usability observations and calculates metrics from the recorded attempts.

The assertions in `main` verify important invariants, including the number of stored records, the final total, duplicate-submission rejection, and loading-state transitions. They make the demonstration self-checking rather than relying entirely on printed output.

Run the file using `node prototype.js` on Node.js 18 or later. No npm packages are required.

## C++ case study

The C++ program treats prototype evaluation as a small, structured experiment for an expense-management product.

`PrototypeArtifact` stores a research question, fidelity level, and screen definitions. Its constructor checks screen and element identifiers, while its inspection methods count screens and interactive elements. The data model makes it possible to compare representations without conflating a non-interactive paper element with a working control.

`ExpenseLedger` performs domain validation and stores expense records. Amounts are converted to integer cents for accumulation, reducing errors associated with repeated binary floating-point addition. The interface accepts a floating-point amount for demonstration purposes, so a production financial system would need an explicit decimal-input and rounding policy at the boundary as well.

`PrototypeSession` models screen transitions with a map of allowed destinations. The `submit` operation transitions through a loading state, creates a ledger entry on success, and returns to the editable form on validation failure. Its `optional` receipt indicates that a successful submission may produce a reference, while failure does not fabricate one.

`UsabilityStudy` stores observations containing task outcomes, duration, error count, and participant confidence. It reports aggregate metrics and flags conditions that merit investigation. The sample is intentionally small and illustrates the calculation, not a claim about the usability of an actual product.

The case study demonstrates why prototype fidelity, domain correctness, interaction state, and research evidence should be modeled separately. A realistic screen can still fail if its state transitions or domain validation are incorrect.

Compile and run the program with a C++17-compatible compiler:

    g++ -std=c++17 -Wall -Wextra -pedantic prototype_case.cpp -o prototype_case
    ./prototype_case

## Java implementation

The Java program uses explicit domain types to separate artifact configuration, lifecycle, interaction state, expense records, and research evidence.

The `Fidelity`, `Lifecycle`, `Screen`, and `Outcome` enums constrain important domain values. `DesignElement`, `ScreenDefinition`, `Expense`, and `UsabilityObservation` are records with compact constructors that validate their invariants. Collections are copied when stored or returned, preventing callers from accidentally modifying an artifact's screen list or the expense service's result list.

`PrototypeArtifact` tracks revisions and enforces its lifecycle rules. Its research question identifies the uncertainty being examined, while its screen definitions represent the structure and interaction coverage of the prototype.

`ExpenseService` creates immutable expense records only after validating the submitted data. `PrototypeSession` coordinates navigation and submission state. It rejects invalid navigation, prevents submissions from inappropriate screens, and restores the form after validation failures.

`UsabilityReport` uses Java streams to calculate completion rate, mean duration, error totals, and confidence. The report keeps measurements separate from the decision to revise the design. Thresholds are explicit experiment rules rather than universal usability standards.

The enterprise-oriented model is deliberately independent of a GUI framework. This allows state transitions and validation to be tested without tying the experiment to a specific rendering technology. A deployed application would still need to connect these domain rules to actual controls, persistence, authorization, and failure handling.

Compile and run the program with Java 17 or later:

    javac PrototypeGovernance.java
    java PrototypeGovernance

## SQL data model

The PostgreSQL script stores prototype artifacts and their research evidence in related tables.

| Table | Responsibility |
|---|---|
| `prototypes` | Identifies the artifact, fidelity, lifecycle, target users, research question, and current revision |
| `prototype_screens` | Stores screen definitions and their order within an artifact |
| `prototype_elements` | Records visual elements, interaction capability, and structured properties |
| `prototype_revisions` | Records the rationale and evidence behind design changes |
| `research_tasks` | Defines the user task and its expected outcome |
| `usability_observations` | Stores participant outcomes, time, errors, and confidence |
| `prototype_decisions` | Records whether evidence supports iteration, advancement, holding, or retirement |

Primary keys identify records. Foreign keys preserve relationships between artifacts, screens, elements, tasks, and observations. Unique constraints prevent duplicate screen keys within a prototype and duplicate participant observations for the same task. Check constraints enforce valid amounts of data, non-empty identifiers, allowed element types, and confidence scores from one through five.

The `prototype_elements.properties` column uses PostgreSQL `JSONB` for structured attributes such as required fields, validation limits, currency, and feedback behavior. Relational columns remain responsible for relationships and commonly queried dimensions.

Partial indexing on interactive elements supports queries that focus on working controls instead of all visual elements. Other indexes support fidelity filtering, ordered screen retrieval, task-level outcome analysis, and recent decision retrieval.

The `enforce_prototype_lifecycle` trigger rejects invalid lifecycle changes and fills publication or retirement timestamps when the corresponding transition occurs. This enforcement applies to direct SQL updates as well as ordinary application updates. The trigger does not attempt to enforce every possible research policy; application-level workflow rules may still be necessary.

The `task_usability_metrics` view aggregates participant observations into task completion rates, average duration, error totals, confidence, and successful attempts within a defined time threshold. The `fidelity_evaluation` view compares the number of screens and interactive elements with the observed task completion rate.

These views keep two different kinds of information separate: what the prototype contains and how participants performed. More interactive elements do not necessarily produce better task outcomes.

The SQL script includes sample observations for valid completion, abandonment, and recovery from invalid input. A guarded validation experiment verifies that a confidence score outside the permitted range is rejected. The surrounding transaction keeps the schema, sample data, and demonstration operations together.

Run the script in a PostgreSQL 15 or later environment with permission to create the objects in the current schema. It drops objects with the names used by the demonstration before recreating them, so it should be run only in a dedicated learning database or schema.

## Interpreting usability evidence

The implementations record several useful measures, but each measure answers a different question.

- **Task completion rate** measures the proportion of observed attempts that reached the specified outcome. The outcome must be defined before testing; reaching a confirmation screen is not sufficient if the task required the user to verify the submitted details.
- **Task duration** helps reveal friction when compared across participants and prototypes. Time measurements should account for facilitator assistance, interruptions, and tasks that participants abandon.
- **Observed errors** capture incorrect actions, invalid entries, and recovery attempts according to a documented observation protocol. A higher error count may reflect confusing controls, weak feedback, or unrealistic prototype behavior.
- **Confidence ratings** capture a participant's reported confidence. They complement observed behavior but do not replace evidence of successful task completion.
- **Threshold-based completion** indicates whether an attempt met a predefined time target. Such thresholds should reflect the task's importance and context rather than being treated as universal usability requirements.

Aggregate metrics can conceal important differences between participants and tasks. A researcher should inspect individual observations and qualitative notes before deciding which design change to make. A failed attempt may arise from unclear terminology, a missing interaction, a facilitator instruction, or a limitation in the prototype itself.

## Design iteration and evidence quality

A prototype is an experimental representation, so its assumptions and limitations should be recorded alongside the interface. When a participant fails, the team should determine whether the failure is evidence of a design problem or an artifact of an incomplete simulation.

For example, a paper sketch can reveal that employees do not understand where to begin. A medium-fidelity prototype can show that users select the wrong screen transition. A high-fidelity interaction model can reveal that a user interprets a loading indicator as a completed submission. These are related observations, but they require different evidence and may lead to different changes.

The revision records in the SQL model and the lifecycle methods in the language implementations provide basic mechanisms for preserving the rationale behind a change. A revision should identify the observed problem and the expected improvement. A subsequent usability session should test whether the change addresses that problem without introducing another one.

Research quality also depends on participant selection. Employees who regularly submit expenses may behave differently from new employees or finance reviewers. Task wording can influence performance, and facilitators can unintentionally guide participants toward a preferred answer. Consistent task instructions, clearly defined completion criteria, and separate recording of assistance reduce these risks.

## Common implementation and interpretation errors

**Treating fidelity as a maturity score.** High fidelity describes representation and behavior, not the amount of validated knowledge. A low-fidelity sketch can provide decisive evidence about an information-architecture problem.

**Building visual detail before validating task structure.** Detailed styling may make an incorrect workflow more expensive to change. Start with the uncertainty that presents the greatest design risk.

**Simulating interactions without documenting their boundaries.** A prototype may show a success message without persisting data. The demonstration should make clear which behavior is real, simulated, or omitted.

**Ignoring failed states.** A successful path alone does not show whether users can recover from invalid input or understand a delayed response. Failure and recovery states should be included when they matter to the research question.

**Confusing an observation with a causal explanation.** A participant's slow completion is evidence of friction, not proof that a particular label or control caused it. Follow-up questions and targeted experiments help isolate the cause.

**Overinterpreting small samples.** The included observations illustrate measurement and decision rules. They do not establish statistical significance or generalize to all employees.

**Using inconsistent completion definitions.** Completion criteria should be set before the session. Otherwise, task success can be reported differently across participants or fidelity levels.

**Allowing prototype state to contradict feedback.** A failed submission should not show a success confirmation. A loading state should end after both successful and unsuccessful operations, and a record should not be created before validation succeeds.

## Limitations and production considerations

These implementations are educational models of prototype design and evaluation, not deployed expense-management systems. Their in-memory services do not provide persistent storage, authentication, authorization, accounting integration, or network-level failure recovery. Simulated delays do not reproduce real latency distributions, and local validation cannot establish server-side integrity.

The SQL model records artifact structure and usability observations, but it does not implement a complete research-consent, participant-identity, or access-control system. Participant codes are used in place of personal identities. Real research records may require additional privacy controls, retention policies, and access restrictions.

The examples also do not constitute a complete accessibility evaluation. Visual similarity and successful mouse interactions do not establish keyboard accessibility, screen-reader compatibility, color contrast, readable error messages, or usability across assistive technologies. These concerns require explicit research and appropriate evaluation methods.

A prototype's value comes from the quality of the decision it supports. The appropriate level of fidelity is the least costly representation that can credibly answer the current design question, with sufficient behavioral realism and evidence to justify the resulting decision.
