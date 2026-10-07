# Ideation Techniques: Brainstorming, Crazy 8s, SCAMPER, Mind Mapping, and Reverse Brainstorming

## Scope

This learning artifact models five related but distinct ideation techniques around one realistic operations challenge:

> Reduce customer support response time without reducing resolution quality.

The five techniques are deliberately separated because they solve different ideation problems.

**Brainstorming** expands the search space through participant contributions while delaying evaluation.

**Crazy 8s** introduces a strict rapid-generation constraint. Its purpose is not simply to produce eight ordinary ideas. The eight directions force the participant to leave the first comfortable solution path.

**SCAMPER** transforms an existing concept rather than starting from an empty problem space. Each operator asks a different transformation question.

**Mind Mapping** represents relationships and hierarchy. It is useful when the problem contains multiple dimensions, causes, opportunities, constraints, and measurements that need to be connected.

**Reverse Brainstorming** approaches the problem from the failure side. Instead of asking how to achieve the desired outcome, it asks how to make the outcome worse. The resulting failure mechanisms are then converted into countermeasures.

The implementations use the same operational scenario so that the differences between the techniques remain visible.

---

## The central distinction between the techniques

Ideation is not one algorithm. Different techniques manipulate the search process in different ways.

| Technique | Primary mechanism | Starting point | Main output |
|---|---|---|---|
| Brainstorming | Participant-driven divergence | A problem or opportunity | Independent and combined ideas |
| Crazy 8s | Rapid constrained divergence | A challenge | Eight directional concepts |
| SCAMPER | Structured transformation | An existing concept | Modified versions of the concept |
| Mind Mapping | Associative organization | A central problem | Hierarchical relationships |
| Reverse Brainstorming | Failure-first exploration | A desired outcome | Failure mechanisms and countermeasures |

These distinctions matter during facilitation.

A brainstorming session can produce a wide range of independent proposals. Crazy 8s is more intentionally restrictive because the participant must keep generating under a rapid constraint. SCAMPER is transformation-oriented, so an existing service, product, process, or concept is required. A mind map does not require every node to be a complete solution because relationships and dimensions are themselves useful outputs. Reverse brainstorming deliberately creates negative scenarios so that hidden weaknesses become visible.

---

## Brainstorming

### Mechanism

Brainstorming separates **generation** from **evaluation**.

During divergence, participants are encouraged to produce ideas without immediately rejecting them. The key mechanism is protection of the search space from premature criticism.

The Python implementation represents contributors using `Participant` objects. Each participant has a perspective and an expertise set. The `BrainstormingSession.generate()` method collects contributions before the separate `evaluate_after_divergence()` operation ranks them.

This separation is important. If every contribution is immediately scored, participants can begin optimizing for feasibility too early. That can remove unusual but potentially valuable directions.

The example includes customer, support-agent, operations, technology, and quality perspectives. Each perspective sees the response-time problem differently.

A customer-oriented idea focuses on response expectations and visibility. A support-agent idea can focus on knowledge retrieval. An operations perspective can focus on queue aging. A technology perspective can focus on classification. A quality perspective can protect resolution quality from being sacrificed for speed.

### Building on an idea

The brainstorming implementation also demonstrates synthesis.

`build_on_existing()` takes an existing contribution and creates a more integrated concept involving classification and duplicate detection.

This demonstrates an important distinction between merely collecting ideas and using another participant's idea as a starting point for a new direction.

### Evaluation

The examples use four dimensions:

- **Novelty** measures how different the idea is from conventional approaches.
- **Feasibility** represents practical implementability under the current constraints.
- **Impact** represents the potential effect on the problem.
- **Confidence** represents confidence in the initial assessment.

The weighted score is:

`novelty × 0.25 + feasibility × 0.25 + impact × 0.35 + confidence × 0.15`

The implementation does not treat this score as an objective measure of creativity. It is an explicit evaluation mechanism used after divergence.

---

## Crazy 8s

### Why the constraint matters

Crazy 8s is intentionally time-constrained and quantity-oriented.

The implementation represents eight distinct prompts:

- removing a manual step
- automating classification
- creating guided self-service
- reversing normal assignment
- personalizing the resolution path
- making queue state visible
- combining intake and knowledge retrieval
- imagining an extreme low-touch path

The eight positions are not eight variations of the same sentence. They deliberately force different transformation directions.

This is important because ordinary brainstorming can become anchored around the first plausible solution. A participant might generate several increasingly detailed versions of automation. Crazy 8s instead creates pressure to change direction.

### Implementation behavior

The Python implementation stores the eight prompts in `PROMPTS`.

The JavaScript implementation represents them as an array of prompt-description pairs. JavaScript's array transformation methods are appropriate because each prompt produces one structured idea.

The SQL implementation models the constraint directly through `crazy8_round` and `crazy8_prompt`. The `slot` column is restricted to values from 1 through 8 and forms part of the primary key.

That means the database can enforce that a round cannot contain the same slot twice.

A validation query counts the slots and reports whether a round contains all eight positions.

### Quality consideration

Eight ideas do not automatically mean eight useful ideas.

The value of the technique comes from the combination of:

- rapid generation
- forced directional change
- delayed detailed evaluation
- explicit time pressure
- reduced attachment to the first solution

The implementation therefore treats the eight concepts as divergent inputs rather than automatically selecting the eighth or highest-scoring idea.

---

## SCAMPER

SCAMPER is structurally different from brainstorming and Crazy 8s because it requires an existing concept.

The case study starts with:

`A conventional manually triaged support queue`

The seven operators are modeled explicitly.

### Substitute

The question is what component can be replaced.

The implementation substitutes first-come-first-served routing with skill- and urgency-based routing.

The transformation changes the routing rule rather than merely adding another feature.

### Combine

Combination asks which separate capabilities could become one workflow.

The example combines intake, classification, and knowledge retrieval.

The value comes from reducing fragmentation between activities that currently occur as separate steps.

### Adapt

Adaptation transfers a mechanism from another context.

The example adapts emergency-dispatch queueing principles to severe customer-support cases.

The key consideration is not copying an unrelated system literally. The mechanism is transferred and adjusted for the new domain.

### Modify

Modification changes the form, scale, sequence, or behavior of an existing component.

The example makes intake questions adaptive. Instead of asking every customer the same set of questions, later questions depend on earlier answers.

### Put to another use

This operator changes the purpose of an existing information source or capability.

Historical support data is used not only to resolve customer cases but also to identify recurring product defects.

This is distinct from ordinary feature improvement because the same information is given a different operational purpose.

### Eliminate

Elimination asks which part of the existing process is unnecessary.

The example removes supervisor handoffs for low-risk, known resolutions.

Elimination is particularly useful when response time is affected by process overhead rather than by the complexity of the actual problem.

### Reverse or rearrange

The example reverses the timing of customer communication.

Instead of waiting for the customer to ask for an update, the system proactively provides status information.

The technique is therefore changing the direction or sequence of an existing behavior.

### Why SCAMPER should not be confused with brainstorming

Brainstorming asks for possibilities around a problem.

SCAMPER asks how an existing concept can be deliberately transformed.

That difference affects facilitation. SCAMPER becomes much more precise when the starting object is clearly defined.

---

## Mind Mapping

Mind mapping represents relationships rather than simply collecting independent ideas.

The central node in the case study is:

`Slow customer support response`

The map branches into:

- Customer experience
- Workflow
- Knowledge

Those branches then contain more specific concepts.

For example, Workflow contains Routing, Handoffs, and Queue aging. Routing contains Skill matching and Urgency classification.

This creates a hierarchy:

`Slow customer support response`

→ `Workflow`

→ `Routing`

→ `Skill matching`

This relationship is different from a flat idea list.

### Why hierarchy matters

A flat list can contain both symptoms and interventions without showing how they relate.

A mind map can distinguish:

- a dimension
- a concern
- a bottleneck
- a capability
- a root cause
- a metric
- a mechanism
- an opportunity

The Python implementation uses recursive `MindMapNode` objects. The C++ implementation uses `std::unique_ptr` to model ownership of child nodes. The Java implementation uses a dedicated `MindMapNode` domain class.

The SQL implementation uses a self-referencing `mind_map_node` table. `parent_node_id` points back to another node, allowing the relational model to represent a tree.

### Tree processing

The implementations include depth calculation.

This is a small but meaningful algorithmic example because the mind map is not merely displayed. Its structure can be traversed programmatically.

Recursive traversal has a natural relationship to tree-shaped ideation structures.

For a map containing `n` nodes, a full traversal is O(n).

---

## Reverse Brainstorming

Reverse brainstorming changes the direction of the question.

Instead of asking:

> How can we make support faster?

the technique asks:

> How could we deliberately make support slower and less reliable?

The case study produces failure mechanisms such as:

- route every request to one queue
- hide response expectations
- require approval for every decision
- manually copy information at every handoff
- measure closure count while ignoring reopening
- allow aging cases to remain mixed with new cases

Each failure mechanism is then inverted into a countermeasure.

For example:

`Route every request to one queue regardless of skill`

becomes:

`Route according to skill, urgency, and workload.`

This method is useful because operational problems are often easier to diagnose through failure modes than through abstract improvement questions.

### Failure-first reasoning

Reverse brainstorming is especially useful when the team already understands the desired outcome but cannot identify why the current system repeatedly fails.

It can expose:

- unnecessary approvals
- hidden bottlenecks
- poor information flow
- inappropriate routing
- weak measurements
- missing escalation mechanisms

The failure list should not be treated as the final solution. It is diagnostic material that must be converted into prevention or improvement actions.

---

## Python implementation

The Python program is the broadest simulation.

The `Idea` dataclass provides a shared representation for generated concepts. It validates scores and calculates a weighted evaluation score.

`BrainstormingSession` demonstrates participant-driven divergence and delayed evaluation.

`Crazy8sSession` contains eight deliberately different prompts.

`ScamperWorkshop` uses an enum for the seven SCAMPER operators and maps each operator to a distinct transformation.

`MindMapNode` creates a recursive hierarchy and supports depth calculation and tree flattening.

`ReverseBrainstorming` separates failure generation from failure inversion.

The program then combines outputs from the techniques, removes exact duplicate descriptions, examines tag distribution, evaluates diversity, identifies cross-technique combinations, and constructs a balanced concept portfolio.

This makes the Python file useful as both a technique demonstration and a small ideation-analysis engine.

### Python edge cases

The program rejects:

- an empty problem statement
- an empty participant set
- empty idea titles
- empty descriptions
- evaluation values outside the 1-to-5 range
- non-positive Crazy 8s or portfolio limits

The validation is intentionally located near the data or operation it protects.

---

## JavaScript implementation

The JavaScript implementation emphasizes event-driven behavior.

`IdeationEngine` maintains the generated ideas and emits `ideaCreated` and `evaluationCompleted` events.

This provides a useful event-oriented model for an interactive ideation application. A browser interface or Node.js service could react to these events without requiring the generation component to know how the interface displays them.

The brainstorming service uses asynchronous contribution collection with `Promise.all()`. This models independent participant contributions as concurrently collectible work.

The Crazy 8s implementation uses an array containing eight prompt-description pairs.

SCAMPER is represented through an immutable object of operators.

The mind map uses recursive `MindMapNode` objects and provides a traversal operation.

Reverse brainstorming uses a `Map` to associate failure mechanisms with countermeasures.

The JavaScript implementation therefore adds an event-driven and asynchronous perspective instead of simply reproducing the Python data structures.

---

## C++ case study

The C++ implementation treats the problem as a small ideation engine.

The `Technique` enum class makes the five techniques explicit domain values rather than unrestricted strings.

`Idea` contains evaluation dimensions and performs validation.

`IdeationEngine` owns the generated idea collection and provides ranking.

### Data structures

The case study uses:

- `std::vector` for ordered idea collections
- `std::set` for tags
- `std::map` for SCAMPER transformations
- `std::unordered_map` for participant-specific brainstorming contributions
- `std::unique_ptr` for mind-map ownership
- `std::array` for fixed-size Crazy 8s prompts
- enum classes for techniques and SCAMPER operators

The use of `std::unique_ptr` is important in the mind map because each parent node owns its child nodes. The ownership model avoids manual `delete` operations.

### Algorithmic behavior

Ranking uses sorting, giving O(n log n) time for `n` ideas.

Mind-map traversal is O(n) for `n` nodes.

The portfolio selection logic uses repeated duplicate checking. This is acceptable for the relatively small collections normally produced by an ideation session. A very large automated idea-generation system would use hashed identifiers or normalized descriptions to avoid repeated linear searches.

### Case-study design

The C++ program treats the five techniques as different producers of ideas, then places their outputs into one evaluation pipeline.

This allows the system to answer two different questions:

- Which ideas have the highest evaluation scores?
- Which ideas provide a balanced portfolio across different ideation mechanisms?

That distinction matters because selecting only the highest-scoring concepts can eliminate diversity.

---

## Java implementation

The Java implementation models the same domain using enterprise-oriented types and immutable records.

`Idea` is a Java record. Its compact constructor performs validation when an instance is created.

This means an invalid idea cannot silently enter the domain model.

`Participant` is also immutable and associates a person with a `Perspective` and expertise set.

### Explicit domain rules

The implementation uses enums for:

- `Technique`
- `Perspective`
- `ScamperOperator`

The `switch` expressions in the services map each domain value to a technique-specific behavior.

This is preferable to scattered string comparisons because invalid values are rejected at the type level.

### Service boundaries

The implementation separates responsibilities into services:

`BrainstormingService` handles participant-driven generation.

`Crazy8sService` owns the eight-direction generation rule.

`ScamperService` owns concept transformation.

`MindMapService` builds and traverses the hierarchical model.

`ReverseBrainstormingService` handles failure mechanisms and countermeasures.

`EvaluationService` handles deduplication, ranking, technique-level averages, and portfolio selection.

This separation makes the implementation closer to a small enterprise domain service model than to a single procedural script.

### Evaluation portfolio

The `balancedPortfolio()` method first gives representation to different techniques before filling remaining positions using ranked ideas.

The reason is methodological rather than merely technical: a portfolio containing only high-scoring ideas from one technique may have less conceptual diversity than a slightly lower-scoring portfolio containing independent directions from multiple techniques.

---

## SQL data model

The SQL implementation models ideation as a relational workflow.

### Workshop

`workshop` represents the problem-solving session.

Its `status` constraint limits the workflow to:

`DIVERGING`

`ORGANIZING`

`EVALUATING`

`SELECTED`

`CLOSED`

This represents an important process distinction. Generation and evaluation are not the same stage.

### Participants

`participant` stores the perspective of each participant.

`workshop_participant` implements the many-to-many relationship between workshops and participants.

This allows one participant to contribute to multiple workshops and one workshop to contain multiple participants.

### Ideas

`idea` is the central concept table.

It references:

- the workshop
- the technique
- optionally the participant
- optionally a parent idea

The parent relationship supports synthesis and derivation.

The database enforces score ranges with `CHECK` constraints.

That means an application cannot insert a novelty score of 9 into a field that is defined as a 1-to-5 evaluation.

### Idea scoring

The `idea_scored` view calculates the weighted score dynamically.

Keeping the score in a view instead of storing it as a permanent value prevents stale scores when evaluation weights change.

### Crazy 8s

The Crazy 8s structure is represented through:

- `crazy8_round`
- `crazy8_prompt`

The prompt slot is restricted to 1 through 8.

The primary key on `(crazy8_id, slot)` prevents duplicate positions inside one round.

A validation query checks whether all eight positions exist.

### SCAMPER

The `existing_concept` table stores the starting concept.

`scamper_transformation` stores the transformation operator and resulting description.

A uniqueness constraint on `(concept_id, operator)` prevents the same SCAMPER transformation from being accidentally duplicated for one concept.

### Mind mapping

The mind map is represented by:

`mind_map`

and

`mind_map_node`

The self-reference from `parent_node_id` to `node_id` represents parent-child relationships.

This is the relational equivalent of the tree used in the Python, C++, and Java implementations.

### Reverse brainstorming

`reverse_brainstorm` stores the desired outcome.

`failure_mechanism` stores both the deliberately negative mechanism and its countermeasure.

Keeping these two values together is useful because the transformation from failure to improvement is part of the method.

### Evaluation

`idea_evaluation` separates assessment from generation.

An evaluator can mark an idea as:

- `PENDING`
- `ACCEPTED`
- `REJECTED`
- `NEEDS_RESEARCH`

The `selected_concept` table records the final selection separately from the evaluation decision.

This separation prevents the database from treating an evaluated idea as automatically selected.

---

## Transactional selection

The SQL script performs the selection stage inside a transaction.

The transaction:

- evaluates ideas
- classifies them
- inserts accepted concepts
- updates the workshop state
- commits the complete state change

This matters because the selection process changes several related tables.

If an error occurs before the commit, PostgreSQL can roll back the transaction rather than leaving the workshop partially updated.

The database therefore provides integrity protection in addition to the validation performed by application code.

---

## Evaluation criteria

Ideation and evaluation should remain conceptually distinct.

The examples use:

| Criterion | Meaning |
|---|---|
| Novelty | Degree to which the concept differs from familiar approaches |
| Feasibility | Practical difficulty under current constraints |
| Impact | Potential effect on the target problem |
| Confidence | Confidence in the initial assessment |

The sample weighted model gives the greatest weight to impact.

That weighting is not a universal creativity formula. It is an explicit decision model for the case study.

A different organization might weight feasibility more strongly when resources are severely constrained.

---

## Common failure modes in ideation

### Evaluating too early

Immediate criticism can narrow the search space before unusual directions are explored.

The implementations therefore separate generation and evaluation.

### Confusing quantity with diversity

Generating twenty versions of the same idea is not equivalent to exploring twenty directions.

Crazy 8s addresses this by forcing different prompts.

The diversity diagnostics in the Python and JavaScript implementations use tags and technique sources to expose homogeneous outputs.

### Using SCAMPER without a clear starting concept

SCAMPER becomes vague when there is no specific object to transform.

The case study explicitly starts from a manually triaged support queue.

### Treating a mind map as a flat checklist

The value of a mind map is partly in the relationships between nodes.

The implementations therefore preserve parent-child relationships instead of flattening everything into independent ideas.

### Stopping after identifying failures

Reverse brainstorming is incomplete if the team records only negative scenarios.

The failure mechanism must be inverted into a countermeasure.

### Selecting only the highest numerical score

A ranking can be useful but can also suppress diversity.

The portfolio-selection implementations therefore consider technique representation in addition to individual scores.

---

## Practical facilitation workflow

A practical session can use the techniques sequentially without treating them as interchangeable.

Begin with brainstorming when the team needs a broad pool from different perspectives.

Use Crazy 8s when the team appears anchored to the first few ideas and needs rapid directional expansion.

Apply SCAMPER when there is already a recognizable product, service, workflow, or process that can be deliberately transformed.

Use mind mapping when the problem has many connected causes, dimensions, constraints, or opportunities and the team needs to understand their relationships.

Use reverse brainstorming when failure modes, bottlenecks, or hidden weaknesses are difficult to expose through positive questioning.

After divergence and exploration, evaluation can compare the resulting concepts using explicit criteria.

The techniques therefore operate as complementary search mechanisms rather than as five names for the same activity.

---

## Edge cases represented in the implementations

The artifacts explicitly handle invalid inputs such as empty problem statements, empty idea titles, missing participants, invalid evaluation scores, and incomplete technique configuration.

The SQL schema adds database-level protection through:

- foreign keys
- unique constraints
- check constraints
- primary keys
- indexed query paths

The Crazy 8s model prevents duplicate slots within a round.

The SCAMPER model prevents duplicate operators for the same starting concept.

The mind-map models protect parent-child relationships through foreign keys.

The evaluation model prevents duplicate evaluator records for the same idea through a composite uniqueness rule.

---

## Security and production considerations

Ideation systems may contain commercially sensitive information such as product concepts, operational weaknesses, customer pain points, and internal process ideas.

A production implementation should therefore treat idea descriptions as potentially sensitive business data.

Database permissions should follow least privilege. Users who can view ideas do not necessarily need permission to modify workshop state or delete historical ideas.

Input validation should remain active at both application and database layers. Application validation improves user feedback, while database constraints protect integrity when multiple clients or services write to the same database.

Audit history is also important in a production system. The educational SQL model stores creation and evaluation timestamps but does not attempt to implement a complete immutable audit ledger.

Evaluation scores should be treated as decision support rather than objective measurements of creativity.

The weighted score used in the examples is intentionally transparent so that teams can inspect and change the assumptions.

---

## Relationship between the implementations

The six artifacts are deliberately complementary.

The Python program provides the broadest simulation and combines generation, validation, analysis, diversity diagnostics, and portfolio selection.

The JavaScript program emphasizes event-driven processing and asynchronous participant contribution collection, which is suitable for an interactive ideation application.

The C++ program presents the domain as a strongly typed case-study engine with explicit ownership and STL-based algorithms.

The Java program emphasizes immutable domain objects, explicit enterprise service boundaries, enums, validation, and portfolio rules.

The SQL script models persistent workshop state, relationships, constraints, analytical queries, and transactional selection.

The README explains the same domain without reproducing the source files.

The five ideation techniques remain distinct across all implementations: brainstorming generates broadly, Crazy 8s forces rapid variety, SCAMPER transforms an existing concept, mind mapping organizes relationships, and reverse brainstorming exposes failure mechanisms before converting them into countermeasures.
