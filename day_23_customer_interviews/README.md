# Customer Interviews

Customer interviews are a qualitative research method used to understand how people experience a problem, perform a task, make decisions, use existing solutions, and respond to constraints.

A well-designed interview is not primarily a conversation for collecting opinions. It is a structured method for obtaining evidence about real experiences and behavior.

This repository contains three complementary implementations:

* Python: a comprehensive educational implementation covering the complete interview-research workflow.
* JavaScript: an application-oriented implementation using objects, classes, validation, functional processing, asynchronous behavior, and event-driven patterns.
* C++: an industry-style customer research case study modeling participants, interview questions, evidence, probing, thematic analysis, contradictions, validation, and reporting.

The examples use a fictional research scenario involving small businesses and overdue invoice management.

## Research objective

The central case-study question is:

> How do small businesses currently manage overdue invoices?

The research focuses on:

* Current workflows
* Recent real-world behavior
* Frequency of activities
* Pain points
* Workarounds
* Consequences of missed or delayed actions
* Differences between participants
* Contradictory evidence

The implementations deliberately avoid treating a proposed product feature as the starting point of the investigation.

For example, asking whether someone would use automatic invoice reminders produces a reaction to a hypothetical solution. Asking what the person did the last time an invoice became overdue produces evidence about the existing workflow.

## Fundamental concept

A customer interview is a research conversation designed to collect information from a participant about their experiences, behaviors, goals, constraints, and decision-making processes.

The interviewer has two responsibilities:

1. Obtain useful evidence.
2. Avoid unnecessarily distorting that evidence.

The second responsibility is important because the interviewer can influence the conversation through wording, assumptions, question order, reactions, interruptions, body language, and expectations.

The interviewer should therefore seek evidence before interpretation.

## Behavior, opinion, experience, and intention

Interview statements can have different evidentiary characteristics.

### Behavior

Behavior describes something the participant actually did.

Example:

`Last week I checked overdue invoices in my spreadsheet.`

This is valuable because it refers to a specific event.

### Experience

Experience describes what happened during an event.

Example:

`The difficult part was remembering which customers had already received reminders.`

This provides information about friction in the workflow.

### Opinion

Opinion describes what the participant believes.

Example:

`I think automation would help.`

Opinions can be useful, but they should not automatically be treated as evidence that a person will behave differently.

### Hypothetical intention

Hypothetical intention describes what a participant says they might do.

Example:

`I would probably use an automatic reminder system.`

This is weaker evidence about future behavior than observing or discussing an actual behavior.

A useful interview progression is therefore:

`recent event → behavior → sequence → difficulty → workaround → consequence → frequency → alternatives`

rather than:

`proposed feature → opinion → willingness to use`

## Research objectives

A research objective should define the information that needs to be learned.

A useful objective contains:

* A research question
* The relevant population
* The behavior or experience under investigation
* The evidence required
* Important boundaries

The Python and C++ implementations represent the objective explicitly.

The case study requires evidence about:

* Current tools
* Recent examples
* Frequency
* Workarounds
* Consequences
* Operational difficulties

It explicitly keeps proposed-product reactions outside the primary research scope.

This prevents the interview from becoming a disguised sales conversation.

## Participant selection

Participant selection affects what conclusions can reasonably be drawn.

A participant should be selected because their experience is relevant to the research question.

The C++ implementation models participants with:

* Participant ID
* Name
* Role
* Company size
* Relevant experience

The implementation includes an eligibility check based on participant characteristics.

A person who does not perform the relevant workflow may still provide useful contextual information, but they should not automatically be treated as direct evidence about the workflow.

For example, a designer who never manages invoices cannot provide the same type of evidence as an owner or accountant who performs invoice follow-up regularly.

## Interview preparation

Preparation should establish:

1. Research objective
2. Participant criteria
3. Interview structure
4. Question guide
5. Note-taking method
6. Privacy considerations
7. Evidence standards
8. Analysis method

Preparation should not become an attempt to predict the participant's answers.

A guide is a navigation system, not a script that must be followed mechanically.

If a participant introduces an important experience, the interviewer should investigate it rather than immediately returning to the next prepared question.

## Interview structure

A practical structure contains several stages.

### Opening

Explain the purpose of the discussion and establish appropriate expectations.

### Context

Understand the participant's role and relationship to the workflow.

### Recent experience

Ask about a specific recent event.

### Deep dive

Investigate what happened, what the participant did, what was difficult, and what happened afterward.

### Contrast

Explore previous approaches, alternatives, changes, and workarounds.

### Closing

Ask whether there is anything important that was not covered.

This structure moves from broad context toward concrete evidence and then toward interpretation.

## Question design

A strong question is:

* Clear
* Relevant
* Neutral
* Understandable
* Appropriate for the participant
* Focused on one meaningful subject

The most useful questions often ask participants to reconstruct an actual event.

Examples include:

`Tell me about the last time you followed up on an overdue invoice.`

`What happened next?`

`What did you do when that happened?`

`How often does this occur?`

`What did you use before your current process?`

`Why did you change that approach?`

These questions are useful because they ask about context and behavior rather than merely asking participants to predict future behavior.

## Open questions

Open questions allow participants to construct an answer in their own words.

Example:

`What happened the last time you encountered this problem?`

A closed question would be:

`Did this problem cause a delay?`

Closed questions can be appropriate when confirming a specific fact, but relying on them exclusively can constrain the participant's response.

## Behavioral questions

Behavioral questions ask about actions.

Examples:

`What did you do?`

`What happened after that?`

`Which tool did you open first?`

`How did you decide what to do?`

`When did you last perform this task?`

These questions are particularly useful when the goal is to understand a current workflow.

## Hypothetical questions

Hypothetical questions ask participants to predict future behavior.

Examples:

`Would you use this product?`

`Would you pay for this?`

`Would you switch from your current system?`

These questions can provide useful reactions, especially during concept research, but they should not be treated as equivalent to evidence of actual behavior.

The Python, JavaScript, and C++ implementations identify hypothetical wording as a distinct evidence category.

## Leading questions

A leading question contains wording that pushes the participant toward a particular response.

Example:

`Don't you think automatic reminders would save time?`

The question contains an assumption that automatic reminders are useful.

A more neutral alternative is:

`How do you currently handle reminders?`

Another alternative is:

`What happens when an invoice becomes overdue?`

Neutral wording does not mean the interviewer must avoid all difficult questions. It means the interviewer should avoid embedding the expected answer into the question.

## Double-barreled questions

A double-barreled question asks about two separate dimensions at once.

Example:

`How easy and fast was the process?`

Ease and speed are different characteristics.

A participant could consider the process easy but slow.

The questions should therefore be separated:

`How easy was the process?`

`How long did it take?`

This produces clearer evidence.

## Loaded wording

Loaded wording embeds an evaluation.

Example:

`Why did you fail to complete the process?`

The word `fail` assumes that the participant failed.

A neutral alternative is:

`What happened when you tried to complete the process?`

The revised question allows the participant to explain the event without accepting the interviewer's characterization.

## Bias in customer interviews

Interview bias is not limited to poorly written questions.

Important sources include:

* Leading questions
* Confirmation bias
* Selection bias
* Recall bias
* Social desirability bias
* Acquiescence bias
* Interviewer effects
* Order effects
* Framing effects
* Hypothetical bias
* Survivorship bias

### Confirmation bias

Confirmation bias occurs when an interviewer gives greater attention to evidence supporting an existing belief and less attention to evidence that contradicts it.

Suppose the research team believes:

`Customers cannot manage invoices without automation.`

A participant says:

`Our spreadsheet works well for our current volume.`

That statement should not be discarded merely because it conflicts with the research team's expectation.

The C++ implementation explicitly preserves contradictory evidence.

### Selection bias

Selection bias can occur when participants are recruited in a way that systematically excludes relevant groups.

For example, interviewing only highly technical customers may produce a different picture from interviewing the full target population.

### Recall bias

Participants may not remember past events accurately.

Specific recent events generally provide better recall opportunities than vague questions about behavior over many years.

Compare:

`How do you normally manage invoices?`

with:

`Tell me about the last overdue invoice you handled.`

The second question provides a concrete event to reconstruct.

### Social desirability bias

Participants may give answers that appear socially acceptable or that they believe the interviewer wants to hear.

This is one reason neutral wording and non-judgmental reactions matter.

## Probing

Probing means following an answer to obtain deeper or clearer evidence.

A probe should usually be connected to something the participant has already said.

Useful probe categories include:

### Clarification

`What do you mean by that?`

`Can you give me an example?`

### Sequence

`What happened next?`

`What happened immediately before that?`

### Frequency

`How often does that happen?`

`When did this last happen?`

### Impact

`What effect did that have?`

`What did you do because of that?`

### Cause

`What makes that difficult?`

`Why is that important to you?`

A probe should not automatically introduce a new assumption.

Weak probe:

`What other features would you want?`

Evidence-oriented probe:

`You mentioned that you created a spreadsheet workaround. When did you start doing that?`

The second probe investigates an existing behavior.

## Active listening

Active listening means paying attention to the participant's meaning and using that information to guide the next question.

It involves:

* Listening without prematurely interpreting
* Allowing participants to finish
* Not filling every pause
* Reflecting important statements
* Asking relevant follow-up questions
* Not defending the product
* Not correcting the participant unnecessarily
* Distinguishing statements from assumptions

An interviewer should not treat silence as a problem that must immediately be filled.

A participant may need time to reconstruct a sequence of events.

## Observation versus interpretation

Research notes should distinguish what happened from what the researcher thinks it means.

Observation:

`Participant opened a spreadsheet while explaining the workflow.`

Quote:

`I keep everything in this spreadsheet.`

Interpretation:

`The spreadsheet appears central to the workflow.`

The observation and quote are evidence. The interpretation is an analytical statement.

Keeping these layers separate makes later review more reliable.

The Python implementation models all three.

## Evidence classification

The implementations classify statements into categories such as:

* Concrete behavior
* Stated opinion
* Hypothetical intention
* General statement

This is not a universal scientific scoring system.

It is a practical organizational mechanism.

For example:

`Last week I spent forty minutes reconciling three invoices.`

This describes a concrete past behavior.

`I think automation would be useful.`

This is a stated opinion.

`I would probably use a mobile application.`

This is a hypothetical intention.

The classification helps researchers avoid accidentally treating different types of evidence as equivalent.

## Note-taking

Useful interview notes can contain:

* Participant ID
* Observation
* Direct quote
* Interpretation
* Evidence strength
* Relevant context

The Python and C++ implementations explicitly separate these concepts.

A direct quote should remain distinguishable from paraphrasing.

Interpretations should remain distinguishable from participant statements.

This distinction becomes increasingly important when multiple researchers analyze the same interview set.

## Thematic analysis

After interviews have been conducted, researchers need to organize the evidence.

Thematic analysis identifies recurring concepts or meaningful patterns.

Possible themes in the invoice case study include:

* Manual work
* Reminders
* Reconciliation
* Pain points
* Workarounds
* Tool limitations

The Python implementation groups findings by theme.

The JavaScript implementation demonstrates grouping through `Map`.

The C++ implementation uses `std::map` to associate themes with evidence records.

## Frequency is not importance

A common analytical error is to treat the most frequently mentioned problem as automatically the most important problem.

Consider:

* Problem A occurs every day and costs two minutes.
* Problem B occurs once a year but can cause a major financial loss.

Frequency alone does not determine importance.

Other dimensions can include:

* Severity
* Consequence
* Frequency
* Duration
* Cost
* Number of affected people
* Recoverability
* Risk
* Dependency
* Workaround availability

The implementations therefore preserve evidence rather than converting every finding into a simplistic ranking.

## Contradictory evidence

Good research preserves disagreement.

Suppose one participant says:

`Our spreadsheet works well for our current volume.`

Another says:

`The spreadsheet becomes slow when we have many invoices.`

These statements are not necessarily mutually exclusive.

The difference may be explained by:

* Company size
* Transaction volume
* Process complexity
* Staff expertise
* Number of customers
* Integration requirements

A useful synthesis might therefore identify a segmentation condition rather than declaring that spreadsheets are universally good or bad.

The C++ case study includes a contradiction-analysis component for this purpose.

## Hypothesis testing

A research hypothesis is a statement that can be examined using evidence.

Example:

`Small businesses struggle with invoice follow-up.`

Evidence supporting the statement:

`P01 described manual tracking.`

`P03 reported missed reminders.`

Contradictory evidence:

`P02 said the existing workflow is sufficient at the current business volume.`

The appropriate response is not to erase the contradiction.

The contradiction may suggest that the original hypothesis is too broad.

A more precise research statement might distinguish businesses by transaction volume or workflow complexity.

## Sample size and saturation

There is no universal number of interviews that guarantees a complete understanding of a customer population.

Relevant factors include:

* Research objective
* Population diversity
* Number of relevant segments
* Research risk
* Interview depth
* Complexity of the problem
* Frequency of new themes
* Importance of rare cases

Saturation refers to a situation in which additional interviews produce relatively little new information for the specific research objective.

Saturation is a methodological judgment rather than a fixed number.

The Python implementation demonstrates cumulative theme tracking to illustrate the concept.

## Interviewer effects

The interviewer can influence the participant through:

* Tone
* Facial expression
* Approval
* Disapproval
* Interruptions
* Question wording
* Leading statements
* Knowledge of the expected outcome
* Reactions to surprising answers

An interviewer who repeatedly responds positively to certain answers may unintentionally teach participants which answers appear desirable.

Neutral reactions help reduce this effect.

Instead of:

`That's great. Exactly what we expected.`

A neutral response is:

`Can you tell me more about that?`

## Question order

Question order can influence responses.

If the interviewer introduces a proposed solution before asking about the current workflow, the participant may begin interpreting the current workflow through the proposed solution.

A behavior-first structure reduces this risk:

1. Context
2. Recent event
3. Current behavior
4. Problems
5. Workarounds
6. Consequences
7. Alternatives
8. Concept reaction, if needed

The sequence is particularly important when the research objective is to understand an existing problem.

## Concept testing versus problem discovery

Problem discovery and concept testing are different activities.

### Problem discovery

The objective is to understand the existing situation.

Typical questions:

`What happened?`

`What did you do?`

`Why did you do that?`

`What happened next?`

### Concept testing

The objective is to understand reactions to a proposed solution.

Typical questions may include:

`What is your first reaction to this concept?`

`What would you expect this to do?`

`What concerns would you have?`

Concept testing should not be confused with evidence that the proposed solution will succeed in actual use.

## Python implementation

The Python script is designed as a complete study file.

It demonstrates:

* Research-objective modeling
* Participant modeling
* Question inspection
* Bias detection
* Probing
* Active listening
* Evidence classification
* Note-taking
* Theme grouping
* Keyword analysis
* Contradiction preservation
* Interview guide generation
* Interview simulation
* Evidence matrices
* Hypothesis testing
* Saturation concepts
* Privacy considerations
* Interview-quality review
* Common mistakes
* An end-to-end workflow

The implementation uses Python classes and dataclasses to make research concepts explicit.

For example, `ResearchObjective` separates the primary research question from the evidence required and the subjects that are out of scope.

`InterviewQuestion` stores question text, purpose, and detected risk flags.

`Evidence` distinguishes different forms of participant statements.

`InterviewNote` separates observation, quote, interpretation, and evidence strength.

The script intentionally uses standard-library functionality so that it can run without external packages.

## JavaScript implementation

The JavaScript implementation emphasizes application-level behavior.

It demonstrates:

* Classes
* Objects
* Arrays
* Maps
* Sets
* Validation
* Functional processing
* Asynchronous operations
* Event-driven behavior
* Error handling
* Interview-record storage
* Question inspection
* Evidence classification
* Theme grouping
* Contradiction analysis
* End-to-end analysis

The `InterviewRecord` class demonstrates how interview data can be represented as an application object.

The `InterviewEventEmitter` demonstrates an event-driven pattern in which application components can react to events such as captured answers and generated probes.

The asynchronous simulation demonstrates how an application might process a sequence of interview events without blocking the JavaScript event loop.

The JavaScript implementation is therefore useful for connecting customer research concepts to web and application development.

## C++ case study

The C++ implementation models a more structured research system.

The scenario is an internal research application for a software company investigating overdue invoice management.

The system contains:

* `ResearchObjective`
* `Participant`
* `InterviewQuestion`
* `InterviewRecord`
* `Evidence`
* `ProbeEngine`
* `ThemeAnalyzer`
* `ResearchReport`

### Research objective

`ResearchObjective` stores:

* Primary research question
* Required evidence
* Out-of-scope subjects

This prevents the research process from becoming disconnected from the original research decision.

### Participant model

`Participant` stores participant characteristics and includes eligibility checking.

The case study includes an owner, accountant, and designer to demonstrate why participant relevance matters.

### Interview question model

`InterviewQuestion` stores:

* Question text
* Question type
* Purpose

The model also performs deterministic checks for common wording risks.

### Interview record

`InterviewRecord` stores:

* Participant
* Questions
* Answers
* Notes

It also validates that questions and answers are structurally consistent.

### Evidence model

`Evidence` stores:

* Participant ID
* Statement
* Evidence type
* Evidence strength
* Rationale

The classification distinguishes concrete behavior from opinion and hypothetical intention.

### Probe engine

`ProbeEngine` chooses a follow-up question based on terms in the participant's answer.

This is deliberately deterministic.

It demonstrates the programming structure of a probing mechanism without pretending that simple keyword matching can fully understand human language.

### Theme analyzer

`ThemeAnalyzer` provides:

* Keyword-frequency analysis
* Theme grouping

The theme rules are intentionally simple and inspectable.

A production research system would require more sophisticated analytical controls if automated classification were used for important decisions.

### Research report

`ResearchReport` combines the objective and evidence and produces a structured textual report.

The report includes:

* Evidence counts
* Evidence categories
* Evidence details
* Themes
* Contradiction indicators

## Important distinctions

### Question versus hypothesis

A question requests information.

A hypothesis proposes an explanation that evidence can support or contradict.

### Evidence versus interpretation

Evidence is what the participant said or did.

Interpretation is what the researcher thinks that evidence means.

### Frequency versus importance

Frequency describes how often something occurs.

Importance may also depend on severity, cost, risk, consequence, or affected population.

### Opinion versus behavior

Opinion describes what a participant believes.

Behavior describes what the participant actually did.

### Concept reaction versus product-market evidence

A participant saying that a feature sounds useful is not equivalent to evidence that they will adopt it.

### Participant statement versus researcher conclusion

A participant may say:

`The system is terrible.`

The researcher should investigate what happened rather than automatically adopting the statement as a verified description of the system.

## Edge cases

Customer interviews contain many situations that require careful handling.

### Participant cannot remember

Use a narrower timeframe or ask about a recent event.

### Participant gives very short answers

Use clarification and example-based probes.

### Participant gives extremely long answers

Identify the relevant point and return to the research objective without interrupting prematurely.

### Participant changes the subject

Determine whether the new subject contains relevant evidence before redirecting.

### Participant contradicts an earlier statement

Clarify the difference instead of assuming dishonesty.

### Participant does not perform the workflow

Record that limitation and avoid treating the participant as direct evidence about the workflow.

### Participant describes an extremely rare event

Preserve the evidence while distinguishing frequency from severity.

### Participant gives a hypothetical answer

Record it as hypothetical rather than converting it into observed behavior.

### Participants disagree

Preserve the disagreement and investigate potential segmentation factors.

## Common mistakes

### Asking only what people want

Customers may describe attractive features without describing the actual problem.

### Selling during research

Defending the product can suppress negative evidence.

### Asking too many questions

A long questionnaire leaves less time for meaningful probing.

### Interrupting every pause

Participants may need time to reconstruct an event.

### Treating every quote as proof

A quote is evidence of what a participant said. It is not automatically proof that the statement represents the entire market.

### Ignoring negative cases

Contradictory cases can reveal segmentation and boundary conditions.

### Overgeneralizing from a small sample

Qualitative interviews provide detailed evidence but do not automatically produce population-level statistical estimates.

### Mixing observation and interpretation

When the two are written as though they were the same thing, later researchers cannot easily determine what actually happened.

## Privacy and research ethics

Customer interviews may contain:

* Personal information
* Business information
* Financial information
* Customer records
* Internal processes
* Confidential documents
* Proprietary systems

Research systems should therefore minimize unnecessary data collection.

Appropriate controls may include:

* Informed consent where applicable
* Clear explanation of recording
* Secure storage
* Access control
* Data minimization
* Separation of identifiers
* Appropriate retention periods
* Removal of unnecessary personal information
* Careful handling of quotations

The research purpose should determine what information is collected.

## Security considerations

An interview-management application may become a repository of sensitive information.

Relevant security controls include:

* Authentication
* Authorization
* Encryption in transit
* Encryption at rest where appropriate
* Secure credential handling
* Audit logging
* Input validation
* Access separation
* Secure backups
* Appropriate data retention
* Protection against accidental disclosure

The C++ case study does not implement a network security layer because its purpose is to demonstrate the research workflow rather than build a production data-storage service.

## Validation considerations

Validation should operate at several levels.

### Input validation

Questions, participant IDs, and answers should not be silently accepted when required fields are missing.

### Structural validation

The number of questions and answers should be consistent.

### Semantic validation

A technically valid sentence may still be poor research evidence.

For example, a perfectly valid answer such as:

`Yes.`

may provide little useful information.

The interviewer needs to determine whether a follow-up probe is necessary.

## Performance considerations

For ordinary interview datasets, the operations in these examples are computationally inexpensive.

Question validation is approximately linear in the length of the question for each set of pattern checks.

Evidence classification is approximately linear in the length of each statement.

Keyword analysis is approximately linear in the total number of processed tokens when using hash-based counting.

Theme grouping is approximately linear in the number of evidence records when each record is processed using a fixed set of rules.

The largest practical performance constraint in a research system is often not the text-processing algorithm itself. It can be data storage, transcription volume, indexing, search, access control, or human analysis.

## Limitations of automated analysis

The implementations deliberately use transparent deterministic rules.

This has advantages:

* Easy to inspect
* Easy to test
* Predictable
* No external dependencies
* Simple debugging
* Reproducible results

It also has limitations.

Keyword rules cannot reliably understand:

* Sarcasm
* Context
* Complex negation
* Subtle emotion
* Domain-specific meanings
* Ambiguous statements
* Long-range conversational relationships
* Contradictory statements that require broader context

Therefore, automated classification should not silently replace research judgment.

## Testing considerations

Useful tests for a production customer-interview system would include:

* Empty participant IDs
* Missing questions
* Missing answers
* Mismatched question and answer counts
* Leading questions
* Neutral questions
* Hypothetical questions
* Long questions
* Empty statements
* Contradictory evidence
* Duplicate evidence
* Unrecognized themes
* Participants outside the target population

Testing should verify both correct behavior and appropriate failure behavior.

## Implementation comparison

| Area                        | Python                             | JavaScript                          | C++                                                |
| --------------------------- | ---------------------------------- | ----------------------------------- | -------------------------------------------------- |
| Educational readability     | Strong                             | Strong                              | Moderate                                           |
| Data modeling               | Dataclasses and classes            | Classes and objects                 | Structs and classes                                |
| Text processing             | Standard library                   | Built-in string and collection APIs | Standard library                                   |
| Async behavior              | Not central to this implementation | Demonstrated explicitly             | Not central to this case study                     |
| Event-driven programming    | Limited in this implementation     | Demonstrated with an event emitter  | Not central to the case study                      |
| Validation                  | Demonstrated                       | Demonstrated                        | Demonstrated                                       |
| Thematic analysis           | Demonstrated                       | Demonstrated                        | Demonstrated                                       |
| Industry-style architecture | Demonstrated conceptually          | Demonstrated at application level   | Demonstrated explicitly                            |
| Memory control              | Managed by runtime                 | Managed by runtime                  | More explicit control through C++ object semantics |
| External dependencies       | None                               | None                                | None                                               |

## Why the three languages are useful

Python is particularly suitable for educational research tooling because its syntax is compact and its data structures are convenient for manipulating qualitative evidence.

JavaScript is useful when customer research becomes part of a web application, browser workflow, interactive dashboard, interview tool, or event-driven system.

C++ is useful for demonstrating explicit data structures, type modeling, validation, algorithmic complexity, and systems-oriented implementation decisions.

The research methodology itself does not depend on a programming language. The languages demonstrate different ways of implementing supporting software.

## Practical applications

Customer interview techniques can support research into:

* Software products
* Mobile applications
* Banking services
* E-commerce
* Education
* Healthcare services
* Enterprise software
* Developer tools
* Financial workflows
* Customer support
* Internal business processes
* Public services
* Industrial systems

The underlying method remains similar:

`define objective → recruit relevant participants → investigate behavior → probe → document → analyze → preserve contradictions`

The specific questions depend on the domain.

## Production implementation considerations

A production research platform would typically need more than the educational components demonstrated here.

Potential system components include:

* Participant management
* Interview scheduling
* Consent tracking
* Recording management
* Transcript storage
* Search
* Tagging
* Coding
* Theme management
* Research-project permissions
* Audit history
* Data retention controls
* Export functionality
* Structured research reports

The research methodology should remain visible within the system rather than being hidden behind automated classification.

## End-to-end method

A disciplined customer interview workflow can be represented as:

1. Define the decision the research must inform.
2. Convert the decision into research questions.
3. Identify the relevant participant population.
4. Define recruiting criteria.
5. Prepare a flexible discussion guide.
6. Review questions for bias and ambiguity.
7. Conduct the interview.
8. Ask about concrete recent experiences.
9. Probe important statements.
10. Separate observation from interpretation.
11. Classify and organize evidence.
12. Identify themes.
13. Preserve contradictions and negative cases.
14. Compare relevant participant segments.
15. Assess evidence strength and uncertainty.
16. Document the research findings.
17. Use the findings as evidence for subsequent product or service decisions.

This process keeps the interview centered on learning from participants rather than steering them toward a predetermined answer.
