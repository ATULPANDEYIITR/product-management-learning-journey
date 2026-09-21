# User Journey Analysis

## Topic

User Journey Analysis is a structured method for understanding how a person experiences a product, service, process, or organization while attempting to achieve a specific goal.

A useful journey analysis does not merely list screens or organizational departments. It examines the user's goals, actions, expectations, interactions, effort, emotions, pain points, friction, important decision points, failures, and opportunities for improvement.

The implementations in this repository use a digital banking account-opening journey as a common case study. The Python implementation focuses on comprehensive analytical modeling, the JavaScript implementation demonstrates application-oriented and asynchronous analysis, and the C++ implementation develops an industry-style technical case study with explicit domain structures and performance considerations.

---

## What user journey analysis examines

A journey can be represented as:

`User goal → Stage → User action → Touchpoint → Experience → Outcome`

For example:

`Open bank account → Verification → Upload document → Identity verification screen → Frustration → Abandonment`

This representation becomes more useful when additional dimensions are attached:

- User goal
- User action
- Touchpoint
- Channel
- Expectation
- Emotion
- Pain
- Friction
- Effort
- Moment of truth
- Evidence
- Outcome
- Opportunity
- Operational cause

The purpose is not to create a visually attractive map. The purpose is to create a useful model of the experience that can support investigation, prioritization, experimentation, and service improvement.

---

## Fundamental terminology

### User

The person experiencing or attempting to use the product or service.

A journey analysis should specify which users are being studied. A first-time customer may have very different problems from an experienced customer.

### Persona or segment

A defined user group with sufficiently similar characteristics or behavior for analysis.

Examples include:

- First-time users
- Returning users
- Mobile users
- Desktop users
- High-frequency users
- Users requiring accessibility support
- Users interacting through assisted channels

A journey map that combines substantially different populations can hide important problems.

### Goal

The outcome the user is attempting to achieve.

A product's business objective and the user's goal are not necessarily identical.

For the case study:

`User goal = Open an account and successfully make the first transaction`

The goal gives the journey a boundary and prevents analysis from becoming an unstructured list of interactions.

### Journey stage

A meaningful phase of the user's experience.

The case study contains:

- Awareness
- Consideration
- Signup
- Onboarding
- First Use
- Support

Stages should represent meaningful progress from the user's perspective rather than simply reproducing internal departments.

### Touchpoint

A specific interaction between the user and an organization, product, service, employee, system, or communication channel.

Examples include:

- Search result
- Website page
- Pricing page
- Application form
- Mobile screen
- Email
- Phone call
- Chatbot
- Branch visit
- Transaction confirmation

A stage can contain multiple touchpoints.

### Pain point

A problem that negatively affects the user's experience or ability to achieve a goal.

Pain can involve:

- Confusion
- Delay
- Repetition
- Unexpected cost
- Lack of information
- Errors
- Lack of trust
- Poor support
- Inaccessible interfaces
- Failed transactions

### Friction

Friction is the effort, uncertainty, complexity, delay, or resistance introduced into the journey.

Friction can be:

- Physical
- Cognitive
- Procedural
- Technical
- Emotional
- Financial
- Organizational

Pain and friction are related but not identical.

A user may experience substantial effort without strong negative emotion. A short interaction may create substantial anxiety if it involves money, identity, privacy, or another high-risk decision.

### Moment of truth

A moment of truth is an interaction where the user's perception, confidence, trust, or decision can change substantially.

Examples include:

- Seeing unexpected fees
- Receiving an identity-verification failure
- Making the first successful transaction
- Contacting support after a failed transaction
- Receiving confirmation that an important task has succeeded

The case study explicitly marks several touchpoints as moments of truth.

### Emotion

Emotion describes the user's reported or inferred emotional state at a particular point.

The implementation represents emotions numerically:

- `-2` = Very Negative
- `-1` = Negative
- `0` = Neutral
- `1` = Positive
- `2` = Very Positive

This representation is useful for computation, but emotional values should not be treated as objective measurements unless they come from an appropriate research method.

### Opportunity

An opportunity is an improvement area derived from evidence about a problem, unmet need, friction, expectation gap, or undesirable outcome.

An opportunity should not automatically be treated as a feature request.

The analytical sequence should normally be:

`Evidence → Problem → User need → Root cause → Opportunity → Experiment → Measurement`

---

## Journey mapping structure

A practical journey map can contain columns such as:

| Dimension | Purpose |
|---|---|
| Stage | Identifies the phase of the journey |
| User goal | Defines what the user wants |
| Actions | Records what the user does |
| Touchpoints | Identifies interactions |
| Channel | Shows where the interaction occurs |
| Expectations | Describes what the user expects |
| Emotion | Captures the experience state |
| Pain | Describes problems |
| Friction | Describes unnecessary effort |
| Moment of truth | Identifies high-impact interactions |
| Evidence | Records supporting observations |
| Opportunity | Identifies potential improvements |

The Python, JavaScript, and C++ programs model many of these fields directly.

---

## The difference between a journey map and a process map

A process map normally focuses on how work moves through a system.

A journey map focuses on how the user experiences that system.

For example, an internal process might be:

`Receive document → Run OCR → Verify identity → Update account`

The user journey might be:

`Select document → Upload → Wait → See progress → Receive result → Recover from failure`

Both views are useful, but they answer different questions.

A journey analysis should not replace operational analysis. It should connect user experience to operational reality.

---

## Touchpoint analysis

Every touchpoint should be considered in context.

The same interaction can have different importance depending on the user's situation.

For example:

`Pricing page`

may be a low-emotion informational interaction for one person but a major trust decision for another.

Useful touchpoint questions include:

- What is the user trying to accomplish?
- What information does the user need?
- What does the user expect?
- What does the system require?
- How much effort is required?
- What can go wrong?
- What happens after an error?
- What emotion is reported?
- Does the interaction affect trust?
- Does the interaction determine whether the user continues?
- What evidence supports the interpretation?

The Python model represents these properties with the `Touchpoint` class.

---

## Pain-point analysis

The Python implementation calculates a simple pain-priority value:

`pain × friction × importance / 100`

The JavaScript and C++ implementations use the same basic model.

This calculation is intentionally illustrative rather than universal.

A production prioritization model may also include:

- Number of affected users
- Frequency of occurrence
- Revenue impact
- Conversion impact
- Regulatory risk
- Security risk
- Accessibility impact
- Operational cost
- Strategic importance
- Evidence confidence
- Technical complexity
- Time to implement
- Reversibility

A numeric score should make assumptions visible rather than create artificial certainty.

---

## Friction analysis

Friction can originate from different sources.

### Cognitive friction

The user does not understand what to do.

Examples:

- Unclear instructions
- Ambiguous terminology
- Poor information hierarchy
- Confusing choices

### Interaction friction

The interface requires unnecessary actions.

Examples:

- Too many clicks
- Repeated data entry
- Poor navigation
- Difficult controls

### Procedural friction

The user must complete a process that contains unnecessary steps.

Examples:

- Re-entering information
- Repeated verification
- Multiple approvals
- Unnecessary waiting

### Technical friction

The system itself causes failures or delays.

Examples:

- Upload errors
- Timeouts
- Broken links
- Slow response
- Inconsistent state

### Emotional friction

The user experiences uncertainty, anxiety, distrust, or fear.

This is particularly important for banking, healthcare, identity, security, and other high-consequence services.

### Necessary friction

Not all friction should be removed.

Authentication, fraud controls, consent, identity verification, legal disclosures, and confirmation steps may be necessary.

The correct question is not:

`How can every step be eliminated?`

It is:

`How can necessary protection remain effective while unnecessary user effort is reduced?`

---

## Effort

The implementations use a simplified effort index combining time and friction.

The conceptual model is:

`Effort = time component + friction component`

The Python implementation normalizes time against a 20-minute reference and combines it with a normalized friction score.

This is an analytical demonstration, not a standardized customer-effort measurement.

In real research, perceived effort can be measured through:

- Observed completion time
- Number of attempts
- Number of errors
- Abandonment
- Repeated contacts
- User interviews
- Structured questionnaires
- Task-success rates

Different measures capture different aspects of effort.

---

## Emotional journey

An emotional curve represents how the user's emotional state changes across the journey.

For the case study:

- Awareness is relatively positive.
- Pricing introduces uncertainty.
- Signup is manageable.
- Identity verification becomes strongly negative.
- The first successful transaction becomes strongly positive.
- Support can become negative when problem resolution is difficult.

An emotional curve is valuable because average satisfaction can hide local failures.

A user can finish a journey successfully and still remember one highly negative interaction.

---

## Moments of truth

The case study identifies:

- Pricing
- Identity verification
- First transaction
- Support

as important moments of truth.

These interactions have different characteristics.

### Pricing

The user evaluates transparency and expected cost.

### Identity verification

The user evaluates effort, trust, security, and progress.

### First transaction

The user receives direct evidence about whether the service actually works.

### Support

The user evaluates whether the organization can recover from failure.

Moments of truth deserve special attention because they can disproportionately affect confidence and continued use.

---

## Expectation gaps

Experience is often evaluated relative to expectation.

A simple expectation-gap model is:

`Perceived experience - Expected experience`

A negative value indicates that perceived performance fell below expectation.

For example:

`Expected = 8`

`Perceived = 4`

`Gap = -4`

The size of an expectation gap does not automatically identify the cause.

A low score could result from:

- Poor interface design
- Poor communication
- Unrealistic expectations
- Operational delay
- Technical failure
- External circumstances

The analyst must investigate the underlying cause.

---

## Funnel analysis

The implementations include a journey funnel.

Example:

| Stage | Entered | Completed |
|---|---:|---:|
| Product page | 10,000 | 7,200 |
| Application start | 7,200 | 5,900 |
| Verification start | 5,900 | 3,400 |
| Verification complete | 3,400 | 2,950 |
| First transaction | 2,950 | 2,400 |

Completion rate is:

`completed / entered`

Abandonment rate is:

`1 - completion rate`

The largest numerical drop can identify where investigation is needed.

A funnel does not by itself explain why users leave.

A high abandonment rate at identity verification could result from:

- Document failures
- Unclear requirements
- Privacy concerns
- Long processing time
- Technical errors
- Eligibility issues
- Fraud prevention rules
- Users changing their minds

Behavioral data identifies where to investigate. Qualitative research helps explain why.

---

## Cohort and segment analysis

Averages can conceal meaningful differences.

The implementations compare groups such as:

- First-time users
- Returning users
- Mobile users
- Desktop users

A problem affecting first-time users may be invisible when first-time and returning users are averaged together.

Useful segmentation dimensions can include:

- Experience level
- Device
- Geography
- Product tier
- Customer type
- Acquisition channel
- Accessibility needs
- Task frequency
- Journey outcome

Segmentation should be based on a meaningful analytical question rather than performed merely because the data allows it.

---

## Evidence quality

Journey analysis should distinguish evidence from interpretation.

The Python example demonstrates:

`Analytics → high confidence`

`Interview → moderate confidence`

`Team assumption → low confidence`

This does not mean analytics is always superior to qualitative research.

Different methods answer different questions.

Analytics can show:

`42% of users abandoned verification.`

An interview may reveal:

`Users did not understand which documents were accepted.`

An assumption may say:

`Users probably dislike the screen.`

The first is a behavioral observation.

The second is a reported explanation that requires appropriate interpretation.

The third is an unverified hypothesis.

A strong journey analysis makes these distinctions explicit.

---

## Qualitative and quantitative evidence

### Quantitative evidence

Examples:

- Completion rate
- Conversion rate
- Abandonment rate
- Time to completion
- Error rate
- Number of retries
- Support contacts
- Transaction success rate

Quantitative data is useful for identifying scale and frequency.

### Qualitative evidence

Examples:

- Interviews
- Usability sessions
- Support transcripts
- Open-ended survey responses
- Field observation
- Diary studies

Qualitative evidence helps explain motivations, expectations, confusion, and context.

A mature analysis combines both.

---

## Root-cause analysis

The implementations demonstrate the Five Whys technique.

Example:

`Users abandon identity verification.`

Why?

`Some document uploads fail.`

Why?

`Accepted formats are unclear.`

Why?

`Validation occurs too late.`

Why?

`Recovery paths are weak.`

Why?

`Failure scenarios were not sufficiently represented in design.`

The Five Whys technique helps move from symptom toward possible causes.

It does not prove causality.

A root-cause hypothesis should be checked against:

- User research
- Product analytics
- System logs
- Support records
- Operational processes
- Technical architecture
- Policy requirements

---

## Symptoms versus causes

A symptom might be:

`Users abandon verification.`

A possible cause might be:

`Document upload failures.`

A deeper cause might be:

`Accepted file types are not clearly communicated.`

An organizational cause could be:

`The verification process was designed around successful submissions without sufficient recovery scenarios.`

The journey analyst should avoid immediately converting symptoms into product features.

For example:

`Users abandon verification → build a new screen`

is not sufficient analysis.

The important question is:

`What evidence explains the abandonment, and which intervention addresses the underlying problem?`

---

## Opportunity identification

The case study converts evidence into opportunities.

For identity verification, the proposed direction includes:

- Clear format guidance
- Examples
- Immediate validation
- Progress feedback
- Recovery paths

For support, the proposed direction includes:

- Better intent recognition
- Contextual responses
- Human escalation

For pricing, the proposed direction includes:

- Visible fees
- Clear conditions
- Plain-language explanation

These are directions rather than automatically approved solutions.

The appropriate implementation should be determined after validating the problem and constraints.

---

## Impact and effort

A basic prioritization model can compare:

`Impact`

against:

`Effort`

The Python and JavaScript implementations calculate an opportunity score using impact, confidence, and effort.

A more complete production model may include:

`Priority = impact × affected population × confidence × strategic relevance / implementation cost`

The exact formula should be chosen according to the organization's decision context.

Numeric prioritization should not conceal uncertainty.

If impact is based on a weak assumption, the confidence value should reflect that limitation.

---

## Service blueprint

A journey map can be extended into a service blueprint.

The blueprint separates:

### Customer action

What the user does.

### Frontstage

What the user directly sees.

### Backstage

Internal processes the user normally does not see.

### Supporting systems

Technology, vendors, databases, APIs, employees, or infrastructure supporting the service.

For identity verification:

`Customer: Uploads document`

`Frontstage: App displays verification status`

`Backstage: Verification service processes document`

`Support system: Storage, OCR, verification provider`

This structure helps connect experience problems to operational causes.

---

## Frontstage and backstage relationships

A poor user experience can originate outside the visible interface.

For example:

`Slow verification screen`

may be caused by:

- Slow external provider
- Queueing
- Database contention
- Manual review
- Network problems
- Incomplete API design
- Retry behavior

Changing the interface without addressing the underlying service may only disguise the problem.

Journey analysis therefore benefits from technical and operational investigation.

---

## JavaScript implementation

The JavaScript file uses classes to model:

- `Touchpoint`
- `JourneyStageData`
- `Journey`

The `Touchpoint` constructor validates analytical values immediately.

This demonstrates a useful application-level principle:

`Invalid domain data should be rejected close to its source.`

The JavaScript implementation also demonstrates:

- `Object.freeze`
- Arrays
- `flatMap`
- `map`
- `filter`
- `reduce`
- `sort`
- `Map`
- `Object.entries`
- Classes
- Exceptions
- Promises
- `async` and `await`
- JSON serialization
- Performance measurement

### Functional transformations

Methods such as `map`, `filter`, and `sort` are useful for analytical pipelines.

For example:

`touchpoints.filter(...).map(...).sort(...)`

can express:

1. Select relevant touchpoints.
2. Transform them into analytical records.
3. Rank them.

This style is useful for application-side analytics and data transformation.

### Asynchronous analysis

The JavaScript implementation simulates asynchronous evidence retrieval with a Promise.

In a real application, this could correspond to:

- Analytics APIs
- Customer data services
- Support APIs
- Experiment platforms
- Backend services

The example intentionally does not depend on an external service.

---

## Python implementation

The Python implementation provides the most comprehensive analytical study model.

Important classes include:

- `Touchpoint`
- `JourneyStageData`
- `Journey`
- `Opportunity`
- `FunnelStage`
- `Evidence`
- `BlueprintStep`

The script demonstrates:

- Enumerations
- Dataclasses
- Type hints
- Validation
- Collections
- Aggregation
- Ranking
- JSON serialization
- CSV generation
- Edge-case handling
- Funnel analysis
- Cohort analysis
- Emotional analysis
- Opportunity analysis
- Root-cause analysis
- Experiment design

Python is particularly useful for journey analysis because structured research data can be manipulated concisely and analytical logic can be expressed clearly.

---

## C++ implementation

The C++ program develops the same domain into a technical case study.

The main domain structures are:

- `Touchpoint`
- `JourneyStage`
- `Journey`
- `Opportunity`
- `FunnelStage`
- `BlueprintStep`

The implementation demonstrates explicit data modeling, validation, vector-based storage, unordered channel aggregation, sorting, numerical calculations, exception handling, and complexity discussion.

C++ is useful when journey analysis becomes part of a high-performance analytical, simulation, embedded, large-scale processing, or systems-oriented application.

---

## Why three languages are useful

The three implementations deliberately emphasize different characteristics.

| Language | Primary emphasis |
|---|---|
| Python | Research-oriented analysis and data modeling |
| JavaScript | Application-side processing and asynchronous behavior |
| C++ | Explicit system modeling, algorithms, and performance |

The analytical concepts remain language-independent.

A journey remains a journey whether its data is represented in Python objects, JavaScript classes, or C++ structures.

The implementation techniques differ because the languages have different execution models, ecosystems, type systems, and typical application environments.

---

## Performance considerations

For `T` touchpoints, a simple traversal is approximately:

`O(T)`

Pain-point ranking requires sorting the relevant touchpoints:

`O(T log T)`

Channel aggregation with a hash map has approximately constant average insertion and lookup behavior, making the aggregation approximately:

`O(T)`

The C++ implementation explicitly uses `unordered_map` for channel aggregation.

For small research datasets, these differences are usually insignificant.

For large production datasets containing millions of journey events, architecture becomes more important.

Potential approaches include:

- Database-side aggregation
- Indexed queries
- Pre-aggregated metrics
- Streaming pipelines
- Batch processing
- Columnar storage
- Partitioning
- Caching
- Incremental calculations

The appropriate design depends on data volume, latency requirements, query patterns, and operational constraints.

---

## Journey events versus journey models

A production system may store raw events such as:

- Page viewed
- Form submitted
- Upload attempted
- Upload failed
- Verification completed
- Transaction initiated
- Transaction completed
- Support contacted

The journey map is a higher-level analytical model derived from those events.

This distinction is important.

Raw event data answers:

`What happened?`

Journey analysis attempts to answer:

`What experience did the user encounter, where did it become difficult, and where might improvement be valuable?`

The latter requires interpretation and context.

---

## Data quality

Journey analytics is highly sensitive to data quality.

Potential problems include:

- Missing events
- Duplicate events
- Incorrect timestamps
- Inconsistent user identifiers
- Cross-device identity problems
- Bot traffic
- Sampling bias
- Tracking failures
- Offline interactions not being recorded
- Changes in instrumentation

A sudden drop in completion rate may represent a real experience problem or a broken analytics event.

Instrumentation should therefore be treated as part of the analytical system.

---

## Edge cases

The implementations explicitly handle several edge cases.

### Empty data

An empty collection should not cause division-by-zero errors.

### Negative effort

Negative effort has no meaningful interpretation and is rejected.

### Out-of-range scores

Pain, friction, and importance are constrained to `0–10`.

### Missing evidence

An opportunity without evidence should not automatically receive the same confidence as one supported by observed data.

### Small samples

A small qualitative sample can provide valuable insight but should not automatically be generalized to an entire population.

### Extreme users

Average behavior can conceal users who experience severe problems.

### Multiple journeys

A user may have several journeys with the same product. Account opening, payment, dispute handling, and account closure are different journeys.

---

## Common mistakes

### Mapping the organization instead of the user

A map containing departments such as Marketing, Sales, Operations, and IT may be useful as an internal process map, but it is not necessarily a user journey.

### Treating every touchpoint equally

A minor informational interaction should not automatically receive the same attention as a failed transaction.

### Inventing emotions

An analyst should not assign emotional states without appropriate evidence.

### Confusing pain with friction

A long process can be inconvenient without being emotionally negative.

### Confusing symptoms with causes

Abandonment is an observation. It does not automatically explain why abandonment occurred.

### Building solutions too early

A pain point should first be understood before selecting a solution.

### Ignoring segmentation

Averages can hide serious problems for particular user groups.

### Ignoring operational causes

A front-end problem may be caused by a backend process or organizational policy.

### Removing necessary controls

Security, identity, fraud prevention, consent, and compliance controls may create intentional friction.

### Using artificial precision

A score such as `7.43` can appear highly precise even when it is based on subjective judgment.

The precision of the calculation does not guarantee precision of the underlying evidence.

---

## Security considerations

Journey analysis frequently handles sensitive behavioral information.

Potential data may include:

- Account activity
- Identity-verification events
- Support interactions
- Financial behavior
- Device information
- Authentication events

Production systems should apply appropriate controls for:

- Authentication
- Authorization
- Data minimization
- Encryption
- Access logging
- Retention
- Anonymization or pseudonymization where appropriate
- Secure analytics pipelines
- Protection against unauthorized data export

Journey analytics should not require collecting personal information that is unnecessary for the analytical objective.

The safest dataset is often the one that does not contain unnecessary sensitive information in the first place.

---

## Privacy considerations

Journey data can reveal behavioral patterns even when obvious identifiers are removed.

A robust analytical process should consider:

- What information is collected
- Why it is collected
- Who can access it
- How long it is retained
- Whether users are adequately informed
- Whether sensitive fields are necessary
- Whether aggregation can replace individual-level data

Privacy requirements vary by jurisdiction and application context, so implementation should follow the applicable legal and organizational requirements.

---

## Accessibility considerations

A journey should not assume that every user interacts with a product in the same way.

Accessibility-related friction can arise from:

- Screen-reader incompatibility
- Poor keyboard navigation
- Insufficient contrast
- Small controls
- Inaccessible documents
- Timing constraints
- Captcha challenges
- Complex authentication
- Audio-only instructions
- Poor error messaging

Accessibility should be treated as part of the journey rather than as a separate visual-interface checklist.

---

## Experimentation

Journey analysis becomes more useful when it leads to measurable experiments.

A basic experiment structure is:

`Hypothesis → Change → Primary metric → Guardrail metric → Success condition`

The case study uses:

`Hypothesis: clearer document guidance will increase verification completion.`

Possible primary metric:

`Verification completion rate`

Possible guardrail:

`Verification error rate`

A guardrail is important because improving one metric can damage another.

For example, making verification easier by weakening validation could increase completion while also increasing invalid submissions or security risk.

---

## Metrics

Useful journey metrics include:

### Behavioral metrics

- Completion rate
- Abandonment rate
- Conversion rate
- Time to completion
- Retry count
- Error rate
- Support contact rate

### Experience metrics

- Satisfaction
- Perceived effort
- Confidence
- Trust
- Reported frustration

### Operational metrics

- Processing time
- Queue time
- Resolution time
- Escalation rate
- Failure rate

### Business metrics

- Activation
- Retention
- Revenue
- Cost to serve
- Churn

Metrics should be connected to a specific analytical question.

A large dashboard does not automatically produce better journey understanding.

---

## Opportunity validation

An opportunity becomes more credible when multiple forms of evidence converge.

For example:

`Analytics: high verification abandonment`

plus

`Support data: repeated document-format questions`

plus

`Research: users cannot identify accepted formats`

provides stronger evidence than any single observation alone.

Evidence triangulation is useful because different methods have different strengths and weaknesses.

---

## Production architecture

A production journey-analysis platform could contain:

`Event collection`

→ `Event validation`

→ `Data storage`

→ `Identity/session resolution`

→ `Aggregation`

→ `Segmentation`

→ `Journey reconstruction`

→ `Experience analysis`

→ `Opportunity management`

→ `Experimentation`

→ `Monitoring`

The examples in this repository intentionally keep everything self-contained. A production system would normally separate these responsibilities into independently testable components.

---

## Implementation considerations

A production implementation should distinguish at least four layers:

### Domain layer

Defines:

- Journey
- Stage
- Touchpoint
- Evidence
- Opportunity

### Data layer

Handles:

- Event storage
- Querying
- Persistence
- Data quality

### Analysis layer

Calculates:

- Funnel metrics
- Friction
- Pain
- Emotional patterns
- Segments
- Opportunity priorities

### Presentation layer

Displays:

- Journey maps
- Reports
- Dashboards
- Charts
- Research findings

This separation makes analytical logic easier to test and maintain.

---

## Testing considerations

Important tests include:

- Empty journey handling
- Invalid scores
- Negative effort
- Missing evidence
- Zero-user funnel stages
- Duplicate events
- Incorrect event ordering
- Very large datasets
- Unexpected channel names
- Missing optional fields

Analytical calculations should be tested with known inputs and expected outputs.

For example:

`completed = 75`

`entered = 100`

should produce:

`completion rate = 75%`

The test should not depend on manually inspecting printed output alone.

---

## Practical applications

User Journey Analysis can be applied to:

- Banking
- Insurance
- E-commerce
- Healthcare
- Education
- SaaS
- Telecommunications
- Government services
- Travel
- Logistics
- Automotive services
- Enterprise software
- Customer support
- Subscription services

The terminology changes slightly between industries, but the underlying analytical structure remains similar.

---

## Important distinctions

| Concept | Meaning |
|---|---|
| Journey | Complete user experience toward a goal |
| Stage | Meaningful phase of that journey |
| Touchpoint | Specific interaction |
| Pain point | Problem experienced by the user |
| Friction | Effort, uncertainty, delay, or resistance |
| Moment of truth | High-impact interaction |
| Emotion | User's experience state |
| Evidence | Information supporting an observation |
| Root cause | Possible underlying source of a problem |
| Opportunity | Potential area for improvement |
| Service blueprint | User journey connected to operational delivery |

---

## Python, JavaScript, and C++ correspondence

### Python

The Python implementation emphasizes analytical depth.

Important components include:

- `Journey`
- `JourneyStageData`
- `Touchpoint`
- `Opportunity`
- `FunnelStage`
- `Evidence`
- `BlueprintStep`

It also demonstrates structured serialization, CSV processing, validation, prioritization, and research-oriented calculations.

### JavaScript

The JavaScript implementation emphasizes application behavior.

Important components include:

- JavaScript classes
- Functional collection operations
- `Map`
- JSON serialization
- Validation
- Promise-based asynchronous evidence loading
- `async` and `await`
- Performance timing

This is appropriate for browser or application environments where journey information may be displayed, collected, transformed, or retrieved asynchronously.

### C++

The C++ implementation emphasizes explicit technical design.

Important components include:

- Structures
- Enumerations
- Vectors
- Hash maps
- Sorting
- Exception handling
- Numerical analysis
- Domain validation
- Complexity discussion

The case study shows how journey analysis can be implemented as a strongly structured analytical component within a larger technical system.

---

## C++ case study architecture

The C++ scenario models a digital banking customer who wants to open an account and complete the first transaction.

The journey contains:

`Awareness → Consideration → Signup → Onboarding → First Use → Support`

Each stage contains touchpoints.

Each touchpoint contains:

- Name
- Channel
- Action
- Effort
- Emotion
- Pain
- Friction
- Importance
- Moment-of-truth flag
- Evidence

The program then derives analytical information from this model.

---

## C++ algorithms and data structures

### Vector

`vector` stores ordered journey stages and touchpoints.

This is appropriate because journey order is meaningful.

### Unordered map

`unordered_map` groups touchpoints by channel.

This supports efficient average-case lookup and insertion.

### Sorting

Pain points and opportunities are sorted by calculated priority.

Sorting produces:

`O(T log T)`

time complexity for `T` relevant touchpoints.

### Numeric aggregation

The program calculates:

- Means
- Standard deviation
- Completion rates
- Abandonment rates
- Priority scores

These operations demonstrate how a journey model can become a computational analysis rather than a static document.

---

## Limitations of quantitative journey scoring

A score is a simplification.

For example:

`Pain = 8`

does not tell us:

- Why the pain exists
- How many users experience it
- Whether the pain is intentional
- Whether it affects business outcomes
- Whether the problem can be solved cheaply
- Whether solving it introduces another risk

Therefore, scores should support investigation rather than replace it.

---

## Limitations of journey maps

Journey maps can become misleading when:

- The journey boundary is arbitrary.
- User segments are mixed.
- Evidence is weak.
- Emotions are invented.
- Organizational assumptions replace user observations.
- Operational causes are ignored.
- The map becomes outdated.
- The map is treated as a permanent truth.
- Important offline interactions are excluded.

A journey map is a model that should change when evidence changes.

---

## Best practices

1. Define the user and goal clearly.
2. Define the start and end of the journey.
3. Separate stages from touchpoints.
4. Record actual user actions.
5. Document expectations.
6. Distinguish pain from friction.
7. Identify moments of truth.
8. Use evidence to support emotional claims.
9. Separate observations from interpretations.
10. Segment users when meaningful differences exist.
11. Investigate transitions between stages.
12. Connect frontstage problems to backstage causes.
13. Prioritize opportunities using explicit criteria.
14. Preserve necessary security and compliance controls.
15. Consider accessibility.
16. Test improvement hypotheses.
17. Track both primary and guardrail metrics.
18. Revisit the journey as behavior and systems change.

---

## A practical analytical workflow

A disciplined workflow is:

`Define`

→ Identify the user segment and goal.

`Collect`

→ Gather behavioral, qualitative, operational, and outcome evidence.

`Map`

→ Structure stages, actions, touchpoints, expectations, and outcomes.

`Diagnose`

→ Identify pain, friction, emotional changes, moments of truth, and failure points.

`Investigate`

→ Test possible root causes.

`Prioritize`

→ Compare opportunities using impact, evidence, effort, and risk.

`Experiment`

→ Test a clearly defined intervention.

`Measure`

→ Evaluate outcomes and guardrails.

`Update`

→ Revise the journey model as new evidence becomes available.

---

## Real-world relevance

User Journey Analysis connects product management, user research, service design, analytics, operations, engineering, customer support, and business strategy.

A product team may use it to investigate onboarding abandonment.

A service team may use it to understand support failures.

An operations team may use it to connect customer pain with backstage processes.

An analytics team may use it to reconstruct journeys from event data.

An engineering team may use it to identify technical failures affecting important touchpoints.

A product manager may use the resulting evidence to frame opportunities and define measurable experiments.

The value comes from connecting these perspectives around the user's actual goal and experience.
