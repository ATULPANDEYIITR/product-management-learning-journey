# Jobs To Be Done: JTBD Framework, Functional Jobs, Emotional Jobs, Social Jobs, and Job Stories

## Topic introduction

Jobs To Be Done (JTBD) is a framework for understanding why people use, adopt, replace, or reject products and other solutions.

The central unit of analysis is the **job** a person is trying to accomplish in a particular **circumstance**. The job is not necessarily the product, feature, task, or demographic identity of the person performing it.

A customer may use a spreadsheet, notebook, mobile application, colleague, physical tool, existing process, or memory to accomplish the same underlying job. This makes the framework useful for product discovery because it shifts attention from the solution that already exists toward the progress the customer is trying to make.

A useful analytical question is:

> What progress is the person trying to make, under what circumstances, and what evidence shows that the current ways of making that progress are insufficient?

The three implementations in this repository approach the topic from different technical perspectives:

- Python provides a readable analytical model suitable for education, experimentation, validation, and structured research analysis.
- JavaScript demonstrates object-oriented modeling, collections, asynchronous workflows, and application-oriented processing.
- C++ implements a more structured case study with classes, validation, repositories, analytical services, algorithms, and explicit complexity considerations.

The examples use an examination-preparation scenario because it contains several distinct circumstances, competing solutions, desired outcomes, emotional concerns, and measurable trade-offs.

---

## Core JTBD concept

A job represents the progress a person is trying to make.

For example:

A feature-oriented statement is:

`I need a dashboard.`

A job-oriented statement is:

`When I have several subjects to revise before an examination, I want to identify which topics require the most attention, so I can allocate my limited study time effectively.`

The dashboard may be one possible solution. It is not the job itself.

This distinction is fundamental because starting with a feature can cause a product team to optimize an assumed solution before understanding the underlying customer problem.

---

## Fundamental terminology

### Job

A **job** is the progress a person is trying to make in a specific circumstance.

A job should generally describe what the person is trying to accomplish rather than the product they intend to use.

Example:

`Prepare effectively for an important examination when study time is limited.`

The statement does not require a particular application, interface, device, or technology.

### Circumstance

A **circumstance** describes the situation in which the job becomes relevant.

Examples include:

- an examination is approaching
- several assignments have overlapping deadlines
- a production system has failed
- a customer must make an important purchase
- a manager must explain a technical issue to a non-technical stakeholder

The circumstance matters because the same person can have different jobs in different situations.

### Functional job

A **functional job** describes the practical work the person is trying to accomplish.

Examples:

- organize information
- identify important items
- solve a problem
- compare alternatives
- reduce processing time
- make a decision
- complete a task

In the examination example, the functional job is:

`Determine what to study, in what order, and whether preparation is sufficient.`

### Emotional job

An **emotional job** describes how the person wants to feel while performing the job or after making progress.

Examples include:

- feel confident
- reduce uncertainty
- feel in control
- avoid frustration
- feel prepared
- reduce anxiety

The examination example includes:

`Reduce uncertainty and feel in control of preparation.`

The emotional dimension can influence adoption even when the functional result appears adequate.

### Social job

A **social job** describes how the person wants to be perceived by other people or how the activity supports a social role.

Examples include:

- appear competent
- appear reliable
- demonstrate expertise
- maintain reputation
- satisfy social expectations

The examination example includes:

`Demonstrate reliable preparation when discussing academic progress.`

Functional, emotional, and social dimensions can coexist within the same broader job.

---

## Job stories

A job story expresses the relationship among circumstance, motivation, and expected outcome.

A common structure is:

`When <circumstance>, I want to <motivation>, so I can <outcome>.`

For example:

`When I have several subjects to revise before an examination, I want to identify which topics require the most attention, so I can allocate my limited study time effectively.`

The three components are:

| Component | Meaning |
|---|---|
| When | The circumstance or trigger |
| I want to | The motivation or intended progress |
| So I can | The desired result |

A job story is different from a conventional feature request.

Feature request:

`I want a dashboard.`

Job story:

`When I have many topics to revise and limited time, I want to identify high-priority topics, so I can spend my time effectively.`

The second formulation leaves the solution open for investigation.

---

## Job versus task versus feature versus persona

These concepts are related but should not be treated as interchangeable.

| Concept | Meaning | Example |
|---|---|---|
| Persona | Representation of a user group or archetype | University student |
| Task | An activity performed by a person | Read lecture notes |
| Feature | Capability provided by a product | Searchable notes |
| Job | Progress the person is trying to make | Prepare efficiently for an examination |
| Job story | Structured expression of circumstance, motivation, and outcome | When an exam approaches... |
| Desired outcome | Improvement the person wants while performing the job | Minimize time required to identify weak topics |

A persona can be useful for communication and segmentation, but a persona does not automatically explain the job.

A single person can perform many unrelated jobs.

The same job can also be performed by people from very different demographic groups.

---

## Job decomposition

Complex jobs can be decomposed into stages.

For examination preparation, an illustrative job map can contain:

1. Define the target
2. Locate relevant material
3. Prepare the study environment
4. Confirm the selected approach
5. Execute study activities
6. Monitor progress
7. Modify the plan
8. Conclude whether readiness is sufficient

The stages help identify where difficulty occurs.

A product team should avoid confusing a stage with the entire job.

For example:

`Track study progress`

may be one supporting activity.

It is not necessarily equivalent to:

`Prepare effectively for an important examination.`

---

## Desired outcomes

A desired outcome describes what the person wants to improve while performing the job.

Useful outcome statements can focus on:

- minimizing time
- minimizing effort
- minimizing likelihood of failure
- increasing confidence
- increasing predictability
- increasing control
- increasing accuracy
- reducing uncertainty

Examples from the implementations include:

- `Minimize the time needed to identify high-priority topics.`
- `Minimize the likelihood of overlooking an important topic.`
- `Increase confidence that preparation is sufficient.`
- `Minimize effort required to update the study plan.`
- `Increase the likelihood of remembering difficult concepts.`

A weak outcome might be:

`Make studying better.`

A more useful formulation identifies a specific dimension of progress.

---

## Opportunity scoring

The examples implement an illustrative opportunity calculation:

`Opportunity = Importance + max(Importance - Satisfaction, 0)`

For an outcome with importance `9` and satisfaction `4`:

`9 + max(9 - 4, 0) = 14`

The calculation demonstrates how an important outcome with relatively low satisfaction can receive a high opportunity value.

The Python, JavaScript, and C++ implementations validate importance and satisfaction values on a `0-10` scale.

The numerical result should not be interpreted as an objective truth about the market. A score is only as useful as the research, measurement method, sample, wording, and assumptions behind it.

Quantitative prioritization should therefore complement qualitative evidence rather than replace it.

---

## Research evidence

JTBD analysis benefits from studying actual situations rather than relying exclusively on hypothetical preferences.

A question such as:

`Would you use an application that automatically prioritizes your study topics?`

asks for a prediction.

A question such as:

`Tell me about the last time you had to decide what to study first.`

focuses attention on an actual event.

Useful research evidence can include:

- circumstance
- behavior
- previous solution
- difficulty or friction
- trigger
- desired result
- workaround
- switching event
- constraints

The example interviews contain structured evidence such as:

`An examination was two weeks away.`

`Created a spreadsheet of topics and marked weak areas.`

`Maintaining the list became tedious.`

`Know which topics deserve attention first.`

This structure makes it possible to distinguish observed or reported behavior from later interpretation.

---

## Qualitative coding

Qualitative coding organizes recurring themes in research material.

Suppose several participants describe:

- identifying weak chapters
- deciding what to revise first
- avoiding guesses about what matters

These statements may be coded under a broader cluster such as:

`Prioritize knowledge gaps`

Another set of statements might involve:

- tracking deadlines
- deciding which assignment comes first

These can be clustered as:

`Manage commitments`

Coding does not turn qualitative research into objective mathematical truth. It provides a systematic method for organizing evidence and identifying recurring patterns.

The Python, JavaScript, and C++ implementations demonstrate grouping evidence by cluster.

---

## Competing solutions

A central JTBD concept is that the customer may be hiring many different solutions to accomplish the same job.

For the job:

`Prepare effectively for an examination`

possible solutions include:

- notebook
- spreadsheet
- calendar
- textbook
- peer advice
- specialized application
- memory

This means the relevant competitive set can be broader than direct commercial competitors.

For another job such as:

`Track personal expenses accurately`

possible alternatives could include:

- spreadsheet
- notebook
- banking application
- budgeting application
- exported transaction file
- another person
- memory

The key question is not simply:

`Which product competes with our product?`

It is:

`What does the person use to make the desired progress today?`

---

## Switching and forces of progress

Switching behavior can involve several forces.

The implementations model four useful dimensions:

| Force | Meaning |
|---|---|
| Push | Problems with the existing approach |
| Pull | Attraction toward the new approach |
| Anxiety | Concerns about changing |
| Habit | Inertia associated with the existing approach |

Consider a learner moving from a spreadsheet to a specialized study-planning system.

Push:

`Maintaining and updating the spreadsheet consumed too much time.`

Pull:

`Automatic prioritization could reduce manual work.`

Anxiety:

`The learner is concerned that automated prioritization might be wrong.`

Habit:

`The spreadsheet is familiar and contains historical information.`

A new solution can therefore be attractive while still facing significant adoption resistance.

---

## Job map

The job-map concept decomposes the broader job into stages.

The C++ implementation models:

| Stage | Example |
|---|---|
| Define | Clarify what must be achieved |
| Locate | Find relevant material |
| Prepare | Arrange material and conditions |
| Confirm | Check whether the approach is appropriate |
| Execute | Perform the core activity |
| Monitor | Observe progress |
| Modify | Adjust the approach |
| Conclude | Determine whether the desired result was achieved |

This decomposition can reveal opportunities that are invisible when a product team only studies the final result.

For example, a learner may not have difficulty performing practice questions but may have difficulty deciding which questions are worth practicing.

The opportunity may therefore exist before the execution stage.

---

## Python implementation

The Python implementation is designed as a standalone study and experimentation file.

### Core structures

The main structures include:

- `Job`
- `JobStory`
- `DesiredOutcome`
- `JobEvidence`
- `InterviewQuote`
- `SwitchingEvent`
- `JTBDAnalysis`

The `Job` class separates:

- circumstance
- functional job
- emotional job
- social job
- desired outcome

The `JobStory` class provides a reusable representation of the job-story format.

The `DesiredOutcome` class validates numerical ratings and calculates the illustrative opportunity score.

### Python validation

The Python implementation checks:

- empty job fields
- invalid ratings
- missing outcomes
- invalid job stories
- malformed analytical structures

The use of explicit validation demonstrates an important implementation principle: analytical data should be validated at the boundary rather than silently accepted.

### Python research workflow

The script demonstrates:

- structured interview records
- qualitative coding
- clustering
- job decomposition
- competing solution analysis
- opportunity prioritization
- job-story construction
- edge-case testing

It also contains self-tests that verify opportunity calculations, job-story rendering, analysis behavior, and invalid input handling.

### Python performance

For `k` desired outcomes:

- one opportunity calculation is `O(1)`
- finding the highest opportunity is `O(k)`
- calculating the average is `O(k)`
- sorting outcomes is `O(k log k)`

Evidence clustering using a dictionary is approximately `O(n)` for `n` records when dictionary operations are treated as expected constant-time operations.

The implementation intentionally uses standard-library data structures so that it remains self-contained.

---

## JavaScript implementation

The JavaScript implementation emphasizes application-level behavior and asynchronous processing.

### Object-oriented modeling

The JavaScript file contains:

- `Job`
- `JobStory`
- `DesiredOutcome`
- `SwitchingEvent`
- `InterviewEvidence`
- `JTBDAnalysis`

The classes demonstrate encapsulation of validation and behavior.

For example, `DesiredOutcome` owns its opportunity calculation rather than requiring every caller to reimplement the formula.

### Collections

The implementation uses JavaScript collections such as:

- arrays
- `Map`
- `Set`

`Map` is used for evidence clustering.

`Set` is used to identify unique previous solutions.

These structures are useful when a JTBD research system grows beyond a few manually maintained records.

### Asynchronous research workflow

JavaScript also demonstrates an asynchronous research pipeline.

The example uses:

`Promise.all()`

to represent multiple research batches being collected concurrently.

The code does not require an external API. The artificial delay exists to demonstrate asynchronous application behavior.

A real implementation could use similar patterns for:

- browser applications
- backend APIs
- research databases
- survey systems
- transcript processing
- analytics pipelines

Error handling is included with `try/catch` and promise rejection handling.

### JavaScript-specific relevance

JavaScript is particularly suitable for JTBD applications where research analysis must interact with:

- web forms
- browser interfaces
- dashboards
- APIs
- asynchronous data sources
- interactive filtering
- client-side visualization

The conceptual JTBD framework remains language-independent. JavaScript demonstrates how the framework can become part of an application.

---

## C++ case study

The C++ implementation treats the JTBD problem as a small industry-style analytical system.

The modeled scenario is:

`Study Progress Management Under Examination Time Pressure`

The system begins with the customer job rather than with a predefined feature list.

### Major components

#### `JobStory`

Stores:

- circumstance
- motivation
- outcome

The `render()` function produces a standard job-story representation.

#### `DesiredOutcome`

Stores:

- outcome statement
- importance
- satisfaction

It validates its values and calculates opportunity.

#### `JobAnalysis`

Represents a complete JTBD analysis containing:

- job name
- circumstance
- functional job
- emotional job
- social job
- desired outcomes
- alternatives
- barriers

It can calculate:

- average opportunity
- highest-opportunity outcome
- complete analysis reports

#### `InterviewEvidence`

Represents structured research evidence:

- participant identifier
- circumstance
- behavior
- previous solution
- pain
- desired result

#### `ResearchRepository`

Provides a basic persistence abstraction inside the program.

It stores:

- interviews
- coded evidence

A production implementation could replace this in-memory repository with a database-backed implementation without changing the conceptual model.

#### `JTBDAnalysisService`

Contains reusable analytical operations such as:

- sorting outcomes by opportunity
- extracting unique previous solutions

Separating these operations from the data objects demonstrates a service-oriented design approach.

#### `SolutionEvaluation`

Models alternative approaches to the same job using dimensions such as:

- speed
- effort
- confidence
- flexibility

The resulting composite score is explicitly illustrative.

---

## C++ algorithms and complexity

For `k` desired outcomes:

| Operation | Complexity |
|---|---:|
| Opportunity calculation | `O(1)` |
| Average opportunity | `O(k)` |
| Highest opportunity | `O(k)` |
| Sorting outcomes | `O(k log k)` |

Evidence grouping uses an ordered `std::map`.

For `n` evidence records and `g` clusters, the grouping operation is approximately:

`O(n log g)`

The actual runtime characteristics are less important than the architectural distinction between raw research records and analytical transformations.

For real research systems, data quality, privacy, persistence, access control, auditability, and research governance may be more important than micro-optimizing these operations.

---

## Important distinctions

### Job versus feature

`A dashboard` is a solution component.

`Know which topics deserve attention first` describes a desired progress.

A product team should avoid treating the first as the second.

### Job versus task

A task is usually an activity.

A job describes the broader progress the person is trying to make.

For example:

`Read lecture notes`

is a task.

`Prepare effectively for an examination with limited time`

is a broader job.

### Job versus persona

A persona describes who a user is or is represented as being.

A job describes what the person is trying to accomplish under particular circumstances.

A student persona does not automatically tell the product team which job is currently important.

### Job versus outcome

The job describes the progress being pursued.

The desired outcome describes how the person wants that progress to improve.

Example:

Job:

`Prepare effectively for an examination.`

Desired outcome:

`Minimize the time required to identify weak topics.`

---

## Common mistakes

### Starting with features

A team may begin with:

- dashboard
- mobile application
- notifications
- artificial intelligence
- charts

This can lock the research process into a particular solution too early.

JTBD analysis begins by understanding the job and circumstance.

### Defining the job as the product

Incorrect:

`The job is to use a study-planning application.`

The application is a possible solution.

A stronger formulation is:

`Prepare effectively for an examination when time is limited.`

### Defining the job only by demographic group

Incorrect:

`Students need this application.`

This does not identify the circumstance or desired progress.

A more useful statement identifies the actual situation and intended result.

### Making the job excessively broad

Statements such as:

`Be successful in life.`

are too broad to guide product discovery.

A useful job should be sufficiently specific to identify circumstances, constraints, and progress.

### Asking only hypothetical questions

Questions such as:

`Would you buy this?`

can produce opinions rather than evidence of actual behavior.

Past events, workarounds, existing solutions, switching events, and actual constraints are generally more informative for JTBD research.

### Ignoring non-product alternatives

A spreadsheet, notebook, manual process, or colleague may be a genuine competing solution.

Ignoring these alternatives can produce an incomplete understanding of the job.

### Treating opportunity scores as facts

A numerical score should not replace qualitative evidence.

The quality of the conclusion depends on the quality of the underlying research and measurement.

---

## Edge cases

JTBD analysis has several important edge cases.

### Empty job statements

An empty circumstance or outcome cannot provide meaningful analysis.

The implementations reject empty required fields.

### Invalid ratings

The example implementations use a `0-10` range for importance and satisfaction.

Values below `0` or above `10` are rejected.

### No desired outcomes

An analysis can technically exist without outcomes, but its average opportunity is defined as `0` in the examples because there is no numerical evidence to aggregate.

This is an implementation convention rather than a JTBD principle.

### Duplicate evidence

Multiple statements may express the same underlying job.

Rather than treating every sentence as a unique job, researchers can cluster related statements and inspect the evidence supporting the cluster.

### Solution-loaded job statements

A statement such as:

`I need an automated dashboard to track my progress`

contains a proposed implementation.

The analytical task is to ask what progress the dashboard is expected to support.

---

## Limitations

JTBD is an analytical framework, not a guarantee of product-market success.

Several limitations should be considered.

### Research interpretation

Interview evidence requires interpretation.

Different researchers can code the same statement differently.

### Measurement quality

Opportunity scores depend on how importance and satisfaction are measured.

Poorly designed questions can produce misleading numbers.

### Context dependence

A job can change as circumstances change.

A person's priorities during an emergency may differ from their priorities during routine work.

### Multiple simultaneous jobs

People can perform several related jobs at once.

For example, an examination candidate may simultaneously:

- understand difficult material
- manage deadlines
- reduce uncertainty
- maintain motivation
- demonstrate preparation

The analytical model should avoid forcing all of these into a single undifferentiated statement.

### Social and emotional complexity

Emotional and social jobs can be difficult to observe directly.

Researchers should distinguish explicit participant evidence from assumptions.

---

## Best practices

A rigorous JTBD analysis should:

- start from real circumstances
- investigate actual behavior
- identify existing solutions
- distinguish jobs from features
- distinguish jobs from personas
- capture functional, emotional, and social dimensions
- document desired outcomes
- preserve evidence supporting interpretations
- separate observations from assumptions
- use quantitative scoring carefully
- examine switching barriers
- consider non-product alternatives
- validate statements against research
- keep sensitive research data protected

A useful job statement should remain understandable without requiring knowledge of the proposed product.

---

## Performance considerations

The computational requirements of basic JTBD analysis are usually modest.

The examples operate on small in-memory datasets.

For larger systems, the engineering requirements may shift toward:

- database indexing
- pagination
- search
- evidence deduplication
- version control
- transcript processing
- distributed analysis
- access management
- audit logging
- data retention

For example, sorting a few hundred desired outcomes is computationally insignificant compared with processing thousands of interview transcripts, storing multimedia research evidence, or supporting concurrent researchers.

The software architecture should therefore be designed around the actual workload rather than premature optimization.

---

## Security and privacy considerations

JTBD research may contain behavioral, personal, organizational, financial, or other sensitive information.

A production system should consider:

- informed consent
- data minimization
- authorization
- encryption in transit
- encryption at rest
- secure credentials
- controlled transcript access
- pseudonymous participant identifiers
- retention limits
- deletion procedures
- audit logging
- secure backups
- separation of research identifiers from personal identity

The research system should collect only information that is necessary for the research objective.

A participant identifier such as `P01` is preferable to exposing unnecessary personally identifying information in analytical datasets.

The C++ example intentionally stores simplified fictional evidence rather than real personal data.

---

## Implementation considerations

A production JTBD system could separate the architecture into:

### Research collection layer

Responsible for:

- interview capture
- survey collection
- event recording
- participant identifiers
- research consent

### Evidence layer

Responsible for:

- transcripts
- observations
- quotations
- behavioral events
- supporting documentation

### Coding layer

Responsible for:

- tags
- themes
- job clusters
- outcome categories
- evidence relationships

### Analysis layer

Responsible for:

- job stories
- job maps
- desired outcomes
- opportunity calculations
- competing solution analysis

### Product discovery layer

Responsible for translating validated research into:

- product requirements
- experiments
- solution concepts
- prioritization decisions

The analytical layer should not automatically assume that a job requires a particular product feature.

---

## Python, JavaScript, and C++ comparison

| Dimension | Python | JavaScript | C++ |
|---|---|---|---|
| Educational readability | High | High | Moderate |
| Data analysis | Strong | Strong | Strong |
| Web application integration | Moderate | Very strong | Limited compared with JavaScript |
| Asynchronous application workflows | Strong | Very strong | Strong |
| Explicit memory control | Limited | Automatic | Strong |
| Performance control | Moderate | Moderate | Very strong |
| Rapid experimentation | Very strong | Strong | Moderate |
| Systems programming | Limited | Limited | Very strong |
| Object-oriented modeling | Strong | Strong | Strong |
| Standard-library-only implementation | Practical | Practical | Practical |

The JTBD framework itself does not depend on any programming language.

The language changes the engineering representation rather than the underlying product-discovery principle.

Python is particularly useful for research analysis and experimentation.

JavaScript is particularly useful when the research system is integrated into a browser-based product or asynchronous application.

C++ is useful when the system requires explicit control over data structures, memory, performance, or integration into larger systems software.

---

## Practical applications

JTBD can be applied to many product and service contexts.

Examples include:

- education platforms
- banking applications
- financial planning systems
- enterprise software
- cybersecurity products
- healthcare services
- productivity software
- e-commerce
- transportation
- cloud infrastructure
- developer tools
- customer-support systems
- public services
- professional services

The specific job changes with the circumstance.

For example, in an enterprise environment:

`When a production incident occurs, I want to identify the likely source quickly, so I can restore service and communicate the situation accurately.`

The corresponding functional, emotional, and social dimensions may include:

Functional:

`Identify the source of the incident.`

Emotional:

`Reduce uncertainty during the incident.`

Social:

`Demonstrate reliable incident management to stakeholders.`

The same structure can be applied without assuming that the solution must be a particular monitoring platform or dashboard.

---

## Real-world relevance

JTBD is particularly useful when a product team faces questions such as:

- Why are customers switching?
- Why does an existing product remain popular despite known limitations?
- Why do people use workarounds?
- Why does a feature receive little adoption?
- Which customer problems are insufficiently served?
- What circumstances trigger adoption?
- What prevents switching?
- Which desired outcomes are important but poorly satisfied?
- Which solutions compete with the proposed product?
- Which product requirements represent genuine customer progress rather than assumed features?

The framework is most useful when these questions are connected to evidence about actual behavior and circumstances.

---

## Repository file relationship

The four deliverables correspond as follows:

| File | Purpose |
|---|---|
| Python script | Comprehensive educational JTBD model and research-analysis demonstrations |
| JavaScript file | Application-oriented JTBD model with collections and asynchronous processing |
| C++ program | Structured industry-style study-planning JTBD case study |
| README.md | Conceptual and technical explanation corresponding to all three implementations |

The implementations intentionally use the same conceptual scenario while emphasizing different programming techniques.

The shared concepts include:

- job
- circumstance
- functional job
- emotional job
- social job
- job story
- desired outcome
- opportunity
- switching forces
- competing solutions
- qualitative evidence
- evidence clustering
- job mapping
- validation
- product discovery

This correspondence makes it possible to compare how the same JTBD concepts can be represented using different programming paradigms and data structures.
