/**
 * Ideation Techniques
 *
 * This Node.js program demonstrates five distinct techniques:
 *
 * Brainstorming
 *   Group-based divergent generation followed by delayed evaluation.
 *
 * Crazy 8s
 *   Eight rapid directions generated under deliberately different prompts.
 *
 * SCAMPER
 *   Transformation of an existing concept through seven structured lenses.
 *
 * Mind Mapping
 *   Hierarchical representation of a problem and its related dimensions.
 *
 * Reverse Brainstorming
 *   Deliberate creation of failure conditions followed by inversion into
 *   countermeasures.
 *
 * The scenario is customer support operations: reducing response time
 * without damaging resolution quality.
 */

'use strict';

// ---------------------------------------------------------------------------
// Shared idea model
// ---------------------------------------------------------------------------

class Idea {
    constructor({
        title,
        description,
        source,
        novelty = 3,
        feasibility = 3,
        impact = 3,
        confidence = 3,
        tags = []
    }) {
        this.title = title;
        this.description = description;
        this.source = source;
        this.novelty = novelty;
        this.feasibility = feasibility;
        this.impact = impact;
        this.confidence = confidence;
        this.tags = [...tags];
        this.validate();
    }

    score() {
        return (
            this.novelty * 0.25 +
            this.feasibility * 0.25 +
            this.impact * 0.35 +
            this.confidence * 0.15
        );
    }

    validate() {
        if (!this.title?.trim()) {
            throw new Error('Idea title cannot be empty.');
        }

        if (!this.description?.trim()) {
            throw new Error('Idea description cannot be empty.');
        }

        for (const [name, value] of Object.entries({
            novelty: this.novelty,
            feasibility: this.feasibility,
            impact: this.impact,
            confidence: this.confidence
        })) {
            if (!Number.isInteger(value) || value < 1 || value > 5) {
                throw new RangeError(
                    `${name} must be an integer between 1 and 5.`
                );
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Event-driven ideation workflow
// ---------------------------------------------------------------------------

class IdeationEngine {
    #ideas = [];
    #listeners = new Map();

    on(eventName, listener) {
        if (!this.#listeners.has(eventName)) {
            this.#listeners.set(eventName, []);
        }

        this.#listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        for (const listener of this.#listeners.get(eventName) ?? []) {
            listener(payload);
        }
    }

    addIdea(idea) {
        if (!(idea instanceof Idea)) {
            throw new TypeError('Only Idea instances can be added.');
        }

        this.#ideas.push(idea);
        this.emit('ideaCreated', idea);
        return idea;
    }

    get ideas() {
        return [...this.#ideas];
    }

    evaluate() {
        const ranked = [...this.#ideas]
            .sort((a, b) => b.score() - a.score())
            .map((idea, index) => ({
                rank: index + 1,
                idea,
                score: Number(idea.score().toFixed(2))
            }));

        this.emit('evaluationCompleted', ranked);
        return ranked;
    }
}

// ---------------------------------------------------------------------------
// Brainstorming
// ---------------------------------------------------------------------------

class BrainstormingWorkshop {
    constructor(problem, participants) {
        if (!problem?.trim()) {
            throw new Error('Brainstorming problem is required.');
        }

        if (!Array.isArray(participants) || participants.length === 0) {
            throw new Error('At least one participant is required.');
        }

        this.problem = problem;
        this.participants = participants;
    }

    async run(engine) {
        /*
         * Promise.all models parallel contribution collection. The point is
         * not that human participants literally execute concurrently, but
         * that the software does not force one contribution to depend on
         * another participant's completed operation.
         */
        const contributions = await Promise.all(
            this.participants.map((participant) =>
                this.generateContribution(participant)
            )
        );

        for (const contribution of contributions) {
            engine.addIdea(contribution);
        }

        return contributions;
    }

    async generateContribution(participant) {
        const ideas = {
            customer: 'Provide visible response-time estimates and proactive updates.',
            support: 'Surface similar resolved cases while an agent is composing a response.',
            operations: 'Escalate aging cases using queue-age thresholds instead of ticket count alone.',
            technology: 'Classify incoming requests automatically before assignment.',
            quality: 'Measure response speed together with reopening and resolution quality.'
        };

        const description =
            ideas[participant.perspective] ??
            'Remove a measurable bottleneck from the support workflow.';

        return new Idea({
            title: `${participant.name} perspective`,
            description,
            source: 'Brainstorming',
            novelty: participant.perspective === 'technology' ? 5 : 4,
            feasibility: 4,
            impact: 4,
            confidence: 4,
            tags: [participant.perspective, 'divergent']
        });
    }
}

// ---------------------------------------------------------------------------
// Crazy 8s
// ---------------------------------------------------------------------------

class Crazy8sWorkshop {
    constructor(challenge) {
        if (!challenge?.trim()) {
            throw new Error('Crazy 8s challenge is required.');
        }

        this.challenge = challenge;
    }

    generate(engine) {
        /*
         * Array.map is useful here because the technique has exactly eight
         * deliberately distinct prompts. The fixed size is part of the
         * method rather than arbitrary data duplication.
         */
        const prompts = [
            ['Remove', 'Remove manual triage for predictable request types.'],
            ['Automate', 'Automatically classify requests before assignment.'],
            ['Self-service', 'Guide customers through verified troubleshooting.'],
            ['Reverse', 'Let workload determine assignment instead of fixed queues.'],
            ['Personalize', 'Adapt resolution paths to customer context.'],
            ['Visualize', 'Show response windows and case progress.'],
            ['Combine', 'Combine intake with knowledge retrieval.'],
            ['Extreme', 'Create a near-zero-touch path for highly predictable cases.']
        ];

        return prompts.map(([prompt, description], index) =>
            engine.addIdea(
                new Idea({
                    title: `Crazy 8 ${index + 1}: ${prompt}`,
                    description,
                    source: 'Crazy 8s',
                    novelty: Math.min(5, 3 + Math.floor(index / 3)),
                    feasibility: [0, 1, 5, 6].includes(index) ? 4 : 3,
                    impact: [1, 2, 3, 6, 7].includes(index) ? 5 : 4,
                    confidence: 3,
                    tags: ['rapid', prompt.toLowerCase()]
                })
            )
        );
    }
}

// ---------------------------------------------------------------------------
// SCAMPER
// ---------------------------------------------------------------------------

const SCAMPER = Object.freeze({
    SUBSTITUTE: 'Substitute',
    COMBINE: 'Combine',
    ADAPT: 'Adapt',
    MODIFY: 'Modify',
    PUT_TO_ANOTHER_USE: 'Put to another use',
    ELIMINATE: 'Eliminate',
    REVERSE: 'Reverse/Rearrange'
});

class ScamperWorkshop {
    constructor(existingConcept) {
        if (!existingConcept?.trim()) {
            throw new Error('SCAMPER requires an existing concept.');
        }

        this.existingConcept = existingConcept;
    }

    transform(operator) {
        const transformations = {
            [SCAMPER.SUBSTITUTE]:
                'Replace first-come-first-served routing with skill and urgency routing.',
            [SCAMPER.COMBINE]:
                'Combine intake, classification, and knowledge retrieval.',
            [SCAMPER.ADAPT]:
                'Adapt emergency-dispatch queueing principles for severe cases.',
            [SCAMPER.MODIFY]:
                'Make intake questions adaptive so irrelevant questions disappear.',
            [SCAMPER.PUT_TO_ANOTHER_USE]:
                'Use support history to detect recurring product defects.',
            [SCAMPER.ELIMINATE]:
                'Eliminate supervisor handoffs for low-risk known resolutions.',
            [SCAMPER.REVERSE]:
                'Push case updates proactively instead of waiting for customer requests.'
        };

        const description = transformations[operator];

        if (!description) {
            throw new Error(`Unknown SCAMPER operator: ${operator}`);
        }

        return new Idea({
            title: `${operator}: ${this.existingConcept}`,
            description,
            source: 'SCAMPER',
            novelty: 5,
            feasibility: [SCAMPER.SUBSTITUTE, SCAMPER.MODIFY, SCAMPER.ELIMINATE].includes(operator)
                ? 4
                : 3,
            impact: [SCAMPER.COMBINE, SCAMPER.PUT_TO_ANOTHER_USE, SCAMPER.REVERSE].includes(operator)
                ? 5
                : 4,
            confidence: 4,
            tags: ['transformation', operator.toLowerCase()]
        });
    }

    generate(engine) {
        return Object.values(SCAMPER).map((operator) =>
            engine.addIdea(this.transform(operator))
        );
    }
}

// ---------------------------------------------------------------------------
// Mind mapping
// ---------------------------------------------------------------------------

class MindMapNode {
    constructor(label, relationship) {
        this.label = label;
        this.relationship = relationship;
        this.children = [];
    }

    addChild(label, relationship) {
        const child = new MindMapNode(label, relationship);
        this.children.push(child);
        return child;
    }

    traverse(callback, depth = 0) {
        callback(this, depth);

        for (const child of this.children) {
            child.traverse(callback, depth + 1);
        }
    }

    depth() {
        if (this.children.length === 0) {
            return 1;
        }

        return 1 + Math.max(...this.children.map((child) => child.depth()));
    }
}

class MindMap {
    constructor(problem) {
        if (!problem?.trim()) {
            throw new Error('Mind map central problem is required.');
        }

        this.root = new MindMapNode(problem, 'central problem');
    }

    build() {
        const customer = this.root.addChild(
            'Customer experience',
            'dimension'
        );

        customer.addChild('Response expectations', 'concern');
        customer.addChild('Self-service', 'opportunity');
        customer.addChild('Progress visibility', 'opportunity');

        const workflow = this.root.addChild(
            'Workflow',
            'dimension'
        );

        const routing = workflow.addChild('Routing', 'process');
        routing.addChild('Skill matching', 'mechanism');
        routing.addChild('Urgency classification', 'mechanism');

        workflow.addChild('Handoffs', 'bottleneck');
        workflow.addChild('Queue aging', 'metric');

        const knowledge = this.root.addChild(
            'Knowledge',
            'dimension'
        );

        knowledge.addChild('Search quality', 'capability');
        knowledge.addChild('Reusable resolutions', 'capability');
        knowledge.addChild('Missing documentation', 'root cause');

        return this;
    }

    toIdeas(engine) {
        const generated = [];

        this.root.traverse((node, depth) => {
            if (depth === 0) {
                return;
            }

            generated.push(
                engine.addIdea(
                    new Idea({
                        title: node.label,
                        description: `${node.relationship} connected to the central support-response problem.`,
                        source: 'Mind Mapping',
                        novelty: 4,
                        feasibility: 4,
                        impact: 4,
                        confidence: 3,
                        tags: ['association', node.relationship]
                    })
                )
            );
        });

        return generated;
    }

    print() {
        this.root.traverse((node, depth) => {
            console.log(
                `${'  '.repeat(depth)}- ${node.label} [${node.relationship}]`
            );
        });
    }
}

// ---------------------------------------------------------------------------
// Reverse brainstorming
// ---------------------------------------------------------------------------

class ReverseBrainstormingWorkshop {
    constructor(desiredOutcome) {
        if (!desiredOutcome?.trim()) {
            throw new Error('Desired outcome is required.');
        }

        this.desiredOutcome = desiredOutcome;
    }

    generateFailures() {
        return [
            'Send every request to the same queue regardless of skill.',
            'Hide response expectations from customers.',
            'Require manager approval for every request.',
            'Copy customer information manually at every handoff.',
            'Measure closure count while ignoring reopened cases.',
            'Allow aging cases to remain mixed with new cases.'
        ];
    }

    invert(failure) {
        const countermeasures = new Map([
            [
                'Send every request to the same queue regardless of skill.',
                'Route by skill, urgency, and current workload.'
            ],
            [
                'Hide response expectations from customers.',
                'Expose realistic response windows and progress updates.'
            ],
            [
                'Require manager approval for every request.',
                'Reserve approval for exceptions and high-risk cases.'
            ],
            [
                'Copy customer information manually at every handoff.',
                'Maintain one shared case record through the workflow.'
            ],
            [
                'Measure closure count while ignoring reopened cases.',
                'Measure response speed together with resolution quality.'
            ],
            [
                'Allow aging cases to remain mixed with new cases.',
                'Create explicit aging thresholds and escalation paths.'
            ]
        ]);

        return countermeasures.get(failure) ??
            `Prevent the failure mechanism: ${failure}`;
    }

    generate(engine) {
        return this.generateFailures().map((failure) =>
            engine.addIdea(
                new Idea({
                    title: 'Countermeasure from reverse brainstorming',
                    description: this.invert(failure),
                    source: 'Reverse Brainstorming',
                    novelty: 4,
                    feasibility: 4,
                    impact: 5,
                    confidence: 4,
                    tags: ['failure-analysis', 'countermeasure']
                })
            )
        );
    }
}

// ---------------------------------------------------------------------------
// Synthesis and analysis
// ---------------------------------------------------------------------------

function deduplicateIdeas(ideas) {
    const seen = new Set();
    const unique = [];

    for (const idea of ideas) {
        const key = idea.description.trim().toLowerCase();

        if (!seen.has(key)) {
            seen.add(key);
            unique.push(idea);
        }
    }

    return unique;
}

function calculateDiversity(ideas) {
    if (ideas.length === 0) {
        return 0;
    }

    const signatures = new Set(
        ideas.map((idea) => [...idea.tags].sort().join('|'))
    );

    return Number(
        Math.min(100, (signatures.size / ideas.length) * 100).toFixed(1)
    );
}

function printIdeas(title, ideas, limit = ideas.length) {
    console.log(`\n${title}`);
    console.log('-'.repeat(title.length));

    ideas.slice(0, limit).forEach((idea, index) => {
        console.log(
            `${index + 1}. ${idea.title}\n` +
            `   ${idea.description}\n` +
            `   score=${idea.score().toFixed(2)} | ` +
            `novelty=${idea.novelty} | ` +
            `feasibility=${idea.feasibility} | ` +
            `impact=${idea.impact}`
        );
    });
}

function groupBySource(ideas) {
    return ideas.reduce((groups, idea) => {
        if (!groups.has(idea.source)) {
            groups.set(idea.source, []);
        }

        groups.get(idea.source).push(idea);
        return groups;
    }, new Map());
}

function selectPortfolio(ideas, limit = 6) {
    const unique = deduplicateIdeas(ideas);

    const selected = [];

    const highestImpact = [...unique]
        .sort((a, b) => b.impact - a.impact)[0];

    const highestFeasibility = [...unique]
        .sort((a, b) => b.feasibility - a.feasibility)[0];

    const highestNovelty = [...unique]
        .sort((a, b) => b.novelty - a.novelty)[0];

    for (const idea of [
        highestImpact,
        highestFeasibility,
        highestNovelty
    ]) {
        if (idea && !selected.includes(idea)) {
            selected.push(idea);
        }
    }

    unique
        .sort((a, b) => b.score() - a.score())
        .forEach((idea) => {
            if (selected.length < limit && !selected.includes(idea)) {
                selected.push(idea);
            }
        });

    return selected.slice(0, limit);
}

// ---------------------------------------------------------------------------
// Main workflow
// ---------------------------------------------------------------------------

async function main() {
    const problem =
        'Reduce customer support response time without reducing resolution quality.';

    const engine = new IdeationEngine();

    engine.on('ideaCreated', (idea) => {
        console.log(`[event] ideaCreated -> ${idea.source}: ${idea.title}`);
    });

    engine.on('evaluationCompleted', (ranked) => {
        console.log(
            `[event] evaluationCompleted -> ${ranked.length} ideas ranked`
        );
    });

    const participants = [
        { name: 'Asha', perspective: 'customer' },
        { name: 'Ravi', perspective: 'support' },
        { name: 'Meera', perspective: 'operations' },
        { name: 'Kabir', perspective: 'technology' },
        { name: 'Nisha', perspective: 'quality' }
    ];

    console.log('IDEATION WORKFLOW');
    console.log('=================');
    console.log(`Challenge: ${problem}`);

    const brainstorming = new BrainstormingWorkshop(
        problem,
        participants
    );

    await brainstorming.run(engine);

    const crazy8s = new Crazy8sWorkshop(
        'Reduce support response time without adding permanent headcount.'
    );

    crazy8s.generate(engine);

    const scamper = new ScamperWorkshop(
        'A conventional manually triaged support queue'
    );

    scamper.generate(engine);

    const mindMap = new MindMap(
        'Slow customer support response'
    ).build();

    console.log('\nMind map');
    console.log('--------');
    mindMap.print();
    console.log(`Map depth: ${mindMap.root.depth()}`);

    mindMap.toIdeas(engine);

    const reverse = new ReverseBrainstorming(
        'Fast and reliable support response'
    );

    console.log('\nReverse brainstorming failure mechanisms');
    console.log('----------------------------------------');

    for (const failure of reverse.generateFailures()) {
        console.log(`- ${failure}`);
    }

    reverse.generate(engine);

    const allIdeas = engine.ideas;

    const ranked = engine.evaluate();

    printIdeas(
        'Highest-scoring concepts after divergent generation',
        ranked.map((item) => item.idea),
        10
    );

    const groups = groupBySource(allIdeas);

    console.log('\nTechnique profile');
    console.log('-----------------');

    for (const [source, ideas] of groups) {
        const average = ideas.reduce(
            (sum, idea) => sum + idea.score(),
            0
        ) / ideas.length;

        console.log(
            `${source.padEnd(24)} ` +
            `ideas=${String(ideas.length).padStart(2)} ` +
            `average-score=${average.toFixed(2)}`
        );
    }

    const uniqueIdeas = deduplicateIdeas(allIdeas);

    console.log(
        `\nUnique ideas: ${uniqueIdeas.length}` +
        `\nIdea-tag diversity: ${calculateDiversity(uniqueIdeas)}%`
    );

    const portfolio = selectPortfolio(uniqueIdeas);

    printIdeas(
        'Balanced concept portfolio',
        portfolio
    );

    console.log('\nTechnique distinctions');
    console.log('----------------------');
    console.log(
        'Brainstorming creates a broad pool through participant contribution. ' +
        'Crazy 8s uses rapid prompts to force eight different directions. ' +
        'SCAMPER transforms an existing concept through explicit operators. ' +
        'Mind mapping exposes relationships and hierarchy around a central ' +
        'problem. Reverse brainstorming starts with failure mechanisms and ' +
        'turns them into countermeasures.'
    );

    // Demonstrate JavaScript-specific validation and error handling.
    console.log('\nValidation behavior');
    console.log('-------------------');

    try {
        new Idea({
            title: '',
            description: 'Invalid idea',
            source: 'Validation'
        });
    } catch (error) {
        console.log(`Rejected invalid idea: ${error.message}`);
    }

    try {
        new ScamperWorkshop('');
    } catch (error) {
        console.log(`Rejected invalid SCAMPER input: ${error.message}`);
    }
}

main().catch((error) => {
    console.error(`Workflow failed: ${error.message}`);
    process.exitCode = 1;
});
