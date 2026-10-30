# UX Research and Product Design

## Project scope

This project models a product-design workflow for a public transport journey-planning application. It connects user research with design decisions, wireframe structures, interactive prototypes, usability testing, design critique, and design-system governance.

The implementations use the same domain scenario while applying different engineering approaches:

- Python models the complete research and design lifecycle with validated domain objects.
- JavaScript provides an event-driven workspace for research intake, telemetry, synthesis, and design evaluation.
- C++17 implements a structured design-quality evaluation engine.
- Java 17 models an enterprise design workflow through domain types, lifecycle transitions, and policy services.
- PostgreSQL maintains relational traceability and enforces data integrity across research and design artifacts.

The project distinguishes five related but separate areas of work.

| Area | Primary purpose | Main output |
|---|---|---|
| UX research | Understand user behavior, needs, goals, and problems | Research evidence |
| Research synthesis | Organize evidence into recurring patterns and opportunities | Themes and priorities |
| Wireframing and prototyping | Represent information architecture and interaction behavior | Screens and prototype versions |
| Design critique and usability evaluation | Identify usability problems and test design decisions | Critique records and test results |
| Design systems | Maintain reusable components, tokens, and consistency rules | Component specifications and design tokens |

## Domain scenario

Passengers using a public transport application need to find suitable journeys, understand transfers, compare journey duration, and review complete fare information.

The research scenario identifies two recurring themes:

1. **Transfer uncertainty:** passengers have difficulty understanding interchange requirements and route structure.
2. **Fare transparency:** passengers cannot consistently locate and compare total fare information.

The design response includes a route-search screen, a route-results screen, reusable interface components, and a prototype evaluated through task-based usability testing.

The scenario is deliberately based on pseudonymous participants. The example data does not contain participant names, contact details, or other direct identifiers.

## Research methodology and evidence model

### Research evidence

Research evidence is the recorded observation or finding obtained from a research activity. It is not the same as a design decision or a generalized assumption about all users.

Each evidence record includes:

| Attribute | Meaning |
|---|---|
| Evidence identifier | Unique reference for the observation |
| Participant reference | Pseudonymous participant identifier |
| Observation | Concise description of the observed behavior or problem |
| Severity | Relative importance of the identified issue, scored from 1 to 5 |
| Confidence | Researcher's confidence in the interpretation, from 0 to 1 |
| Method | Interview, survey, observation, or usability test |

Severity represents the perceived importance of an issue. Confidence represents the strength of the research interpretation. Neither is a substitute for statistical significance.

The implementations validate these values before accepting research evidence. Duplicate evidence identifiers, empty observations, unsupported research methods, invalid confidence values, and out-of-range severity scores are rejected.

### Research synthesis

Research synthesis organizes individual observations into broader themes. A theme should have traceable evidence rather than being introduced as an unsupported assumption.

The example theme-prioritization formula is:

`Priority = (Evidence Count × Average Severity × Average Confidence) / Estimated Effort`

The score supports comparative planning. It is an explicit project heuristic, not a validated predictive model or a statistical measure of population-level demand.

Theme records retain their associated evidence identifiers. This makes it possible to examine why a theme exists and which observations support a design decision.

The synthesis workflow follows this structure:

- Collect observations from interviews, surveys, or contextual research.
- Assign severity and confidence to each observation.
- Connect observations to one or more research themes.
- Calculate comparative priority scores.
- Identify design opportunities from the strongest evidence.
- Preserve the relationship between evidence, themes, and decisions.

### Research traceability

A research finding should remain connected to its source observation. A theme should not become an isolated label without evidence.

The PostgreSQL model preserves this relationship through `research_observations`, `research_themes`, and `theme_evidence`. The two linking identifiers are constrained by foreign keys, and the rationale field records why an observation contributes to a theme.

This structure supports evidence review, synthesis revisions, and auditing of design decisions.

## Wireframes and prototypes

### Wireframes

A wireframe represents the structure and organization of an interface without requiring full visual styling or production behavior.

The project uses screen records that describe:

- Screen identifiers and accessible screen names.
- Ordered component placement.
- Keyboard navigation order.
- Required design tokens.
- Structural layout information.

The route-search screen contains an input field and a primary action. The route-results screen contains selectable route cards and an action component.

The implementation validates component references before registering screens. A screen cannot reference an unknown component or an unavailable design token.

Interactive elements must have a coherent keyboard order. This checks the relationship between component arrangement and keyboard navigation, rather than simply checking whether an element exists.

These data structures represent wireframe specifications. They do not render graphical wireframes or provide a visual editor.

### Interactive prototypes

A prototype represents an interaction model that can be evaluated before a production implementation is complete.

The example workflow uses task-based testing. Participants are asked to complete activities such as:

- Finding the fastest journey.
- Comparing journey options.
- Identifying transfer points.
- Finding the complete fare.
- Searching for a return journey.

Each usability result stores the participant reference, task, screen, success state, duration, and critical-error count.

This separates task performance from subjective design critique. A screen may satisfy a structural review but still perform poorly during usability testing.

### Usability metrics

The implementations calculate task success rate as:

`Task Success Rate = Successful Tasks / Total Recorded Tasks`

Average task duration is calculated from the recorded task durations.

Critical errors are counted separately. A successful task rate does not automatically indicate that a design is safe or usable if critical errors remain.

The example contains nine PostgreSQL task outcomes, with eight successful outcomes. The programming-language examples use five attempts, with four successful outcomes.

These sample sizes are illustrative. They are not sufficient to establish broad statistical generalizability.

## Design critique

Design critique is a structured evaluation of an interface against usability principles, interaction expectations, and product requirements.

Each critique record includes:

| Attribute | Purpose |
|---|---|
| Critique identifier | Unique reference for the issue |
| Screen | Interface location being evaluated |
| Heuristic | Principle or criterion used in evaluation |
| Severity | Importance of the issue |
| Description | Observed design problem |
| Recommendation | Proposed correction |
| Resolution state | Whether the issue has been addressed |

The scenario includes two types of critique:

- A medium-severity issue involving the visibility of the selected route.
- A critical issue involving acceptance of an empty origin value in an early prototype.

Resolving a critique changes its workflow state. It does not erase the original issue or its recommended correction.

The readiness policies distinguish critical issues from lower-severity observations. An unresolved critical issue blocks validation. A medium-severity issue remains visible for design review but does not automatically prevent the project from passing the example quality gate.

The distinction avoids treating every critique as an equally serious release blocker.

## Design systems

A design system provides reusable interface definitions and shared visual or interaction rules.

The example design system contains:

- Color tokens for text, surfaces, and actions.
- A spacing token.
- Search-field specifications.
- Primary-button specifications.
- Route-card specifications.

### Design tokens

A design token gives a reusable name to a design value. For example, `color.text` identifies the main text color and `space.medium` identifies a standard spacing value.

Tokens support consistent changes across multiple screens. A component can refer to a token by name rather than embedding an unrelated value in each screen.

The PostgreSQL model stores token names, values, types, and descriptions. The design-system implementations use maps or dictionaries to resolve token references during validation.

### Component specifications

A component specification describes reusable interface behavior and requirements.

The project records whether a component:

- Is interactive.
- Supports keyboard access.
- Has an accessible description.
- Meets the configured contrast requirement.
- Has a documented component specification.

The `SearchField`, `PrimaryButton`, and `RouteCard` components are shared between the example screens.

The model verifies that every referenced component exists and that its interaction and accessibility properties satisfy the configured rules.

### Contrast validation

The code implementations calculate relative luminance from hexadecimal RGB color values and compare foreground and background colors.

The contrast ratio is:

`(Lighter Relative Luminance + 0.05) / (Darker Relative Luminance + 0.05)`

The example quality rule uses a minimum ratio of 4.5:1 for the configured text-color pairs.

This check concerns the supplied foreground and background values. It does not prove that an entire interface meets accessibility requirements. Typography, non-text contrast, focus visibility, semantic structure, assistive-technology behavior, and real interaction testing require separate evaluation.

## Design-quality workflow

The implementations use explicit project phases:

`DISCOVERY → SYNTHESIZED → DESIGN → VALIDATED`

Each transition requires the outputs of the previous phase.

| Phase | Main activity | Transition condition |
|---|---|---|
| Discovery | Record user evidence and define themes | Sufficient evidence and themes |
| Synthesized | Calculate theme strength and compare opportunities | Synthesis completed |
| Design | Create screens, register components, and conduct testing | Design artifacts are available |
| Validated | Evaluate accessibility, critique, and usability results | No configured quality blockers |

The readiness model combines structural, behavioral, and critique checks.

The example gate requires:

- At least five research observations.
- At least two research themes.
- At least two non-retired screens.
- At least three usability test runs.
- At least five task results.
- A minimum task success rate of 80%.
- No critical task errors.
- No unresolved critical critique issues.
- Valid component references and keyboard-accessibility properties.
- Valid configured text-contrast pairs.

These are project-specific acceptance thresholds. They are not universal UX research standards.

## Python implementation

**File:** `ux_research_product_design.py`

The Python implementation models the complete project lifecycle with standard-library data structures.

### Domain objects

Frozen dataclasses represent evidence, themes, components, wireframe screens, usability results, and critique issues. This keeps individual records immutable after construction.

The `UXProject` class maintains mutable project state through dictionaries and lists. Dictionaries provide direct lookup by evidence, theme, screen, and critique identifier.

The `ProjectPhase` and `Severity` enums prevent lifecycle and severity values from being represented as arbitrary strings throughout the application.

### Research synthesis

The `theme_metrics()` method calculates the evidence count, average severity, average confidence, estimated effort, and priority score.

The `synthesize()` method checks the evidence and theme requirements, orders themes by priority, and advances the project state.

### Screen validation

`DesignSystem.validate_screen()` verifies registered components, token references, accessible descriptions, keyboard accessibility, and interactive component order.

Color contrast is calculated using helper functions based on relative luminance.

### Readiness evaluation

`evaluate_readiness()` combines structural checks, usability metrics, and unresolved critical critique issues.

A project changes to `VALIDATED` only if the configured checks pass.

The optional `--export` argument writes aggregate JSON results. The export intentionally excludes participant observations and research excerpts.

Run the implementation using:

`python ux_research_product_design.py`

To create an aggregate report:

`python ux_research_product_design.py --export ux_report.json`

## JavaScript implementation

**File:** `ux_research_product_design.js`

The JavaScript implementation emphasizes event-driven workflow management and prototype telemetry.

### Event-driven workspace

`UXStudio` extends Node.js `EventEmitter`. It publishes events when evidence is added, synthesis is completed, design begins, screens are registered, critique issues change, telemetry is recorded, and readiness is evaluated.

Consumers can subscribe to these events without placing all workflow behavior inside a single function.

This approach separates domain operations from reporting and monitoring.

### Structured collections

The implementation uses `Map` for evidence, themes, screens, and critique records. A `Set` tracks telemetry identifiers so duplicate events cannot inflate the recorded event count.

Objects are copied and frozen when accepted as research or test records. This reduces unintended changes to stored evidence.

### Asynchronous synthesis

The `synthesize()` method uses `Promise.all()` to evaluate themes independently. This provides an asynchronous extension point for larger research workspaces where synthesis calculations or external processing may be performed separately.

The example remains self-contained and does not require a remote service.

### Prototype telemetry

`recordEvent()` accepts uniquely identified events. Duplicate event identifiers are rejected.

`recordTask()` stores task outcomes and connects them to registered screens.

This separates interaction telemetry from the final design decision. A recorded event is evidence of an interaction, not automatic proof of a usability problem.

Run the implementation using:

`node ux_research_product_design.js`

## C++17 implementation

**File:** `ux_research_product_design.cpp`

The C++ implementation treats UX readiness as a structured quality-engineering problem.

### Domain representation

The program uses structs for evidence, themes, components, screens, usability attempts, and critique issues.

Enums represent critique severity. Maps provide identifier-based lookup, sets detect repeated component references, and vectors retain ordered records such as keyboard navigation and usability attempts.

### Quality engine

`UXQualityEngine` owns the core project records and evaluates the requirements for design readiness.

It performs validation during record insertion, which prevents invalid evidence and unknown screen references from entering the evaluation model.

The engine checks:

- Evidence sufficiency.
- Theme availability.
- Screen structure.
- Component and token references.
- Keyboard accessibility.
- Color contrast.
- Usability task performance.
- Critical task errors.
- Unresolved critical critique issues.

### Design-system calculations

The implementation calculates WCAG-style contrast ratios using hexadecimal RGB values and relative luminance.

Invalid color values are converted into validation errors. A contrast failure becomes a readiness blocker rather than being silently ignored.

### Complexity considerations

Let:

- `E` represent research evidence records.
- `T` represent research themes.
- `S` represent registered screens.
- `U` represent usability attempts.
- `C` represent design components.

Evidence insertion uses ordered-map lookup and insertion, generally `O(log E)`. Theme synthesis processes linked evidence and sorts the resulting theme scores, approximately `O(E + T log T)` for the supplied linking structure. Readiness evaluation examines the stored records, approximately `O(E + T + S × C + U)` under the implementation's validation approach.

A production system with large evidence collections would benefit from indexed identifier lookup and more selective validation.

Compile and run:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic ux_research_product_design.cpp -o ux_design`

`./ux_design`

## Java 17 implementation

**File:** `UxResearchProductDesign.java`

The Java implementation models a controlled enterprise workflow using explicit domain types and policy objects.

### Immutable domain records

Java records represent evidence, themes, theme scores, components, screens, usability results, critique issues, and readiness reports.

Collection values are copied into immutable snapshots using `List.copyOf()` and `Set.copyOf()`. This reduces accidental mutation of domain records after they have been accepted.

The `UXProject` class owns the mutable lifecycle state and the collections of project artifacts.

### Lifecycle transitions

The project uses an explicit `ProjectPhase` enum. Operations require the appropriate phase:

- Evidence and theme registration occur during discovery.
- Synthesis transitions the project into the synthesized phase.
- Screen registration and usability testing occur during design.
- Governance evaluation can transition a passing project into validation.

Invalid transitions raise `DomainException`.

### Policy-based governance

`ReadinessPolicy` defines the contract for readiness evaluation.

`DefaultReadinessPolicy` combines structural validation, usability checks, and critical critique evaluation.

`GovernanceService` applies the policy and produces an immutable `ReadinessReport`.

This separation makes it possible to introduce different governance rules for different products without rewriting project storage and lifecycle behavior.

### Stream-based calculations

Java streams calculate theme averages, order themes by priority, count successful task results, and identify unresolved critical critiques.

The implementation keeps policy decisions separate from report formatting.

Compile and run:

`javac UxResearchProductDesign.java`

`java UxResearchProductDesign`

## PostgreSQL implementation

**File:** `ux_research_product_design.sql`

The database implementation maintains persistent relationships between research, design artifacts, and testing records.

### Relational model

The schema uses the following primary entities:

| Table | Purpose |
|---|---|
| `projects` | Product-design project and lifecycle stage |
| `research_studies` | Research method, goal, and study status |
| `participants` | Pseudonymous participant references and consent |
| `research_sessions` | Individual research-session records |
| `research_observations` | Evidence collected during research |
| `research_tags` | Controlled research tags |
| `observation_tags` | Many-to-many observation tagging |
| `research_themes` | Synthesized findings |
| `theme_evidence` | Traceability from themes to observations |
| `design_decisions` | Decisions and their research rationale |
| `design_tokens` | Reusable design values |
| `design_components` | Component specifications and accessibility properties |
| `wireframe_screens` | Screen structure and keyboard order |
| `screen_components` | Ordered components within screens |
| `prototypes` | Versioned prototype artifacts |
| `prototype_screens` | Screens included in a prototype |
| `usability_test_runs` | Participant-level prototype test sessions |
| `usability_task_results` | Task-level outcomes and errors |
| `critique_issues` | Design-review findings and resolution status |

### Relational integrity

Primary keys identify individual records. Foreign keys enforce the relationships between projects, studies, participants, observations, themes, screens, and prototypes.

Composite foreign keys ensure that linked research and design records belong to the same project.

Check constraints validate severity ranges, confidence values, lifecycle states, task durations, consent records, and critique-resolution consistency.

For example, the database prevents a participant record without affirmative consent and prevents a task result from referencing a test run in another project.

### Theme reporting

`v_theme_strength` calculates evidence counts and theme-priority scores.

The view connects themes to observations through `theme_evidence`. It preserves a relational audit trail rather than storing a manually entered aggregate count.

### Readiness function

`fn_design_readiness(project_id)` calculates project readiness and returns:

- Eligibility.
- Blocker descriptions.
- Observation count.
- Theme count.
- Screen count.
- Test-run count.
- Task success rate.
- Critical error count.
- Unresolved critical issue count.

The calculation combines information from multiple relational areas.

The `trg_enforce_validated_stage` trigger prevents a project from moving into the `validated` stage while readiness blockers remain.

### Transactions and indexing

Sample records are inserted in a transaction so that the dataset is not left partially populated if an insertion fails.

Indexes support project-level observation lookup, session reporting, reverse theme-evidence retrieval, usability reporting, task-result retrieval, and unresolved critical critique checks.

The partial critique index contains only unresolved critical issues because these are the records most relevant to the readiness evaluation.

### Database execution

Execute the complete script with:

`psql -d your_database -f ux_research_product_design.sql`

The script drops and recreates the isolated `ux_lab` schema. It should therefore be executed only in a database where replacing that schema is acceptable.

The SQL model demonstrates application-level quality governance through relational data and database constraints. It is not a complete multi-tenant production deployment. A production deployment should define appropriate database roles, schema permissions, data-retention controls, and privacy policies.

## Cross-language implementation comparison

| Engineering concern | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Research evidence | Frozen dataclasses | Validated objects | Structs | Records | Relational tables |
| Theme synthesis | Dictionaries and scoring methods | Maps and asynchronous processing | Maps and algorithms | Streams and domain services | Aggregate view |
| Project state | Enum | Frozen phase constants | Engine-controlled operations | Enum and service transitions | Constrained stage field |
| Wireframes | Screen dataclasses | Screen objects | Screen structs | Screen records | Screen tables |
| Design-system validation | Component registry | Component maps | Component maps | Immutable component registry | Component and token constraints |
| Usability evaluation | Result collections | Event-driven task collection | Quality engine | Policy service | Aggregate queries and function |
| Design critique | Issue dictionary | Event-emitting issue registry | Critique vector | Critique records | Critique table |
| Readiness | Project method | Asynchronous gate evaluation | Quality report | Governance policy | Stored function and trigger |
| Persistence | Optional aggregate JSON | In-memory event records | In-memory evaluation | In-memory project model | Relational database |

## Failure handling and operational limitations

### Research quality

The theme-priority score depends on the evidence supplied by researchers. Inconsistent coding, biased sampling, duplicate observations, or unsupported confidence assessments can affect the result.

Automated aggregation does not replace qualitative analysis. Researchers must retain the context and limitations of the original observations.

### Wireframe and prototype limitations

The screen structures are metadata representations. They do not generate visual wireframes, browser prototypes, animation sequences, or production interface components.

Actual prototypes require visual and interaction artifacts that can be inspected by participants and evaluated in their intended runtime environment.

### Accessibility limitations

The implementations validate selected design-system properties, including configured contrast pairs, component descriptions, and keyboard-order consistency.

These checks do not demonstrate complete accessibility conformance. A real product requires additional evaluation of semantic structure, focus management, screen-reader behavior, responsive layouts, zoom, touch targets, and user testing with relevant accessibility needs.

### Usability measurement limitations

Task success and completion time are quantitative indicators. They should be interpreted alongside observed behavior, task difficulty, participant characteristics, and qualitative feedback.

An average success rate can conceal a severe problem affecting a particular user segment. Segmented reporting is required before using the result to make high-impact product decisions.

### Design-system governance

A component being registered does not establish that every instance is implemented correctly. Production governance should include version management, component ownership, change history, usage documentation, and automated verification of actual interface implementations.

### Security and privacy

Research records can contain sensitive personal information even when direct identifiers are omitted.

The example schema stores pseudonymous references and does not include participant contact details. Real deployments should also implement informed-consent procedures, controlled access, data minimization, retention limits, deletion workflows, audit logging, and secure handling of exported research material.

The readiness rules in this project are a transparent example of design governance. They provide consistent checks for the modeled artifacts without claiming that a single numerical score can establish the complete quality of a user experience.
