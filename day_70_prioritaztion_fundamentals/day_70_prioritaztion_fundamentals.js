'use strict';

/**
 * Prioritization Fundamentals
 *
 * Event-driven portfolio prioritization using:
 * - RICE
 * - WSJF
 * - Weighted scoring
 * - MoSCoW classification
 * - Resource and budget constraints
 * - Dependency resolution
 * - Opportunity-cost analysis
 * - Policy evaluation
 *
 * Runtime: Node.js 18+
 * Dependencies: None
 */

const { EventEmitter } = require('node:events');
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');


class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}


class AllocationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'AllocationError';
    }
}


const Priority = Object.freeze({
    CRITICAL: 'critical',
    HIGH: 'high',
    MEDIUM: 'medium',
    LOW: 'low'
});


const MoSCoW = Object.freeze({
    MUST: 'must',
    SHOULD: 'should',
    COULD: 'could',
    WONT: 'wont'
});


const Framework = Object.freeze({
    RICE: 'rice',
    WSJF: 'wsjf',
    WEIGHTED: 'weighted'
});


const Status = Object.freeze({
    PROPOSED: 'proposed',
    EVALUATED: 'evaluated',
    SELECTED: 'selected',
    DEFERRED: 'deferred'
});


function finiteNumber(value, name, minimum = 0, maximum = Infinity) {
    if (
        typeof value !== 'number' ||
        !Number.isFinite(value) ||
        value < minimum ||
        value > maximum
    ) {
        throw new ValidationError(
            `${name} must be a finite number between ${minimum} and ${maximum}.`
        );
    }

    return value;
}


function normalizeInitiative(raw) {
    const item = {
        id: raw.id,
        name: raw.name,
        description: raw.description ?? '',
        reach: finiteNumber(raw.reach, 'reach'),
        impact: finiteNumber(raw.impact, 'impact', 0, 10),
        confidence: finiteNumber(raw.confidence, 'confidence', 0, 1),
        effort: finiteNumber(raw.effort, 'effort', Number.MIN_VALUE),
        businessValue: finiteNumber(
            raw.businessValue,
            'businessValue',
            0,
            10
        ),
        urgency: finiteNumber(raw.urgency, 'urgency', 0, 10),
        riskReduction: finiteNumber(
            raw.riskReduction,
            'riskReduction',
            0,
            10
        ),
        strategicAlignment: finiteNumber(
            raw.strategicAlignment,
            'strategicAlignment',
            0,
            10
        ),
        cost: finiteNumber(raw.cost, 'cost'),
        mandatory: Boolean(raw.mandatory),
        priority: raw.priority ?? Priority.MEDIUM,
        classification: raw.classification ?? MoSCoW.COULD,
        dependencies: new Set(raw.dependencies ?? []),
        status: Status.PROPOSED
    };

    if (typeof item.id !== 'string' || !item.id.trim()) {
        throw new ValidationError('Initiative ID is required.');
    }

    if (typeof item.name !== 'string' || !item.name.trim()) {
        throw new ValidationError('Initiative name is required.');
    }

    if (item.dependencies.has(item.id)) {
        throw new ValidationError('Self-dependency is prohibited.');
    }

    if (!Object.values(Priority).includes(item.priority)) {
        throw new ValidationError('Unknown priority.');
    }

    if (!Object.values(MoSCoW).includes(item.classification)) {
        throw new ValidationError('Unknown MoSCoW classification.');
    }

    return item;
}


class ScoringStrategy {
    static rice(item) {
        return (
            item.reach *
            item.impact *
            item.confidence /
            item.effort
        );
    }

    static wsjf(item) {
        const costOfDelay =
            item.businessValue +
            item.urgency +
            item.riskReduction;

        return costOfDelay / item.effort;
    }

    static weighted(item, weights = {
        businessValue: 0.30,
        strategicAlignment: 0.30,
        urgency: 0.15,
        riskReduction: 0.15,
        confidence: 0.10
    }) {
        const totalWeight = Object.values(weights).reduce(
            (sum, value) => sum + value,
            0
        );

        if (Math.abs(totalWeight - 1) > 1e-9) {
            throw new ValidationError(
                'Scoring weights must sum to 1.'
            );
        }

        return (
            item.businessValue * weights.businessValue +
            item.strategicAlignment * weights.strategicAlignment +
            item.urgency * weights.urgency +
            item.riskReduction * weights.riskReduction +
            item.confidence * 10 * weights.confidence
        );
    }

    static evaluate(item, framework) {
        const strategies = {
            [Framework.RICE]: this.rice,
            [Framework.WSJF]: this.wsjf,
            [Framework.WEIGHTED]: this.weighted
        };

        const strategy = strategies[framework];

        if (!strategy) {
            throw new ValidationError(
                `Unsupported framework: ${framework}`
            );
        }

        const score = strategy(item);

        if (!Number.isFinite(score)) {
            throw new ValidationError(
                `Invalid calculated score for ${item.id}.`
            );
        }

        return score;
    }
}


class PortfolioPolicy {
    constructor({
        effortCapacity,
        budgetCapacity,
        minimumConfidence = 0,
        requireStrategicAlignment = false,
        allowMandatoryOverCapacity = false
    }) {
        this.effortCapacity = finiteNumber(
            effortCapacity,
            'effortCapacity'
        );

        this.budgetCapacity = finiteNumber(
            budgetCapacity,
            'budgetCapacity'
        );

        this.minimumConfidence = finiteNumber(
            minimumConfidence,
            'minimumConfidence',
            0,
            1
        );

        this.requireStrategicAlignment = requireStrategicAlignment;
        this.allowMandatoryOverCapacity = allowMandatoryOverCapacity;
    }

    validate(item) {
        if (item.confidence < this.minimumConfidence) {
            return 'Confidence threshold not satisfied.';
        }

        if (
            this.requireStrategicAlignment &&
            item.strategicAlignment === 0
        ) {
            return 'Strategic alignment requirement not satisfied.';
        }

        return null;
    }
}


class PrioritizationEngine extends EventEmitter {

    #initiatives = new Map();
    #history = [];
    #allocationInProgress = false;

    constructor(rawInitiatives, policy) {
        super();

        if (!Array.isArray(rawInitiatives) || rawInitiatives.length === 0) {
            throw new ValidationError(
                'At least one initiative is required.'
            );
        }

        if (!(policy instanceof PortfolioPolicy)) {
            throw new ValidationError('A valid policy is required.');
        }

        this.policy = policy;

        for (const raw of rawInitiatives) {
            const item = normalizeInitiative(raw);

            if (this.#initiatives.has(item.id)) {
                throw new ValidationError(
                    `Duplicate initiative ID: ${item.id}`
                );
            }

            this.#initiatives.set(item.id, item);
        }

        this.#validateDependencies();
    }

    #validateDependencies() {
        for (const item of this.#initiatives.values()) {
            for (const dependency of item.dependencies) {
                if (!this.#initiatives.has(dependency)) {
                    throw new ValidationError(
                        `${item.id} references missing dependency ${dependency}.`
                    );
                }
            }
        }

        const visiting = new Set();
        const visited = new Set();

        const visit = id => {
            if (visiting.has(id)) {
                throw new ValidationError(
                    'Circular dependency detected.'
                );
            }

            if (visited.has(id)) return;

            visiting.add(id);

            for (const dependency of this.#initiatives.get(id).dependencies) {
                visit(dependency);
            }

            visiting.delete(id);
            visited.add(id);
        };

        for (const id of this.#initiatives.keys()) {
            visit(id);
        }
    }

    #dependencyClosure(id) {
        const result = new Set();
        const stack = [id];

        while (stack.length) {
            const current = stack.pop();

            if (result.has(current)) continue;

            result.add(current);

            for (const dependency of this.#initiatives.get(current).dependencies) {
                stack.push(dependency);
            }
        }

        return result;
    }

    async evaluate(framework = Framework.WEIGHTED) {
        // Yield between evaluations so asynchronous consumers can observe events.
        const evaluations = [];

        for (const item of this.#initiatives.values()) {
            const policyFailure = this.policy.validate(item);

            const score = ScoringStrategy.evaluate(item, framework);

            const evaluation = Object.freeze({
                id: item.id,
                name: item.name,
                score,
                framework,
                eligible: policyFailure === null,
                reason: policyFailure ?? 'Policy requirements satisfied.'
            });

            evaluations.push(evaluation);

            this.emit('initiative:evaluated', evaluation);

            await Promise.resolve();
        }

        evaluations.sort((a, b) => {
            const itemA = this.#initiatives.get(a.id);
            const itemB = this.#initiatives.get(b.id);

            if (itemA.mandatory !== itemB.mandatory) {
                return itemA.mandatory ? -1 : 1;
            }

            return b.score - a.score || a.id.localeCompare(b.id);
        });

        return evaluations;
    }

    async allocate(framework = Framework.WEIGHTED) {
        if (this.#allocationInProgress) {
            throw new AllocationError(
                'An allocation is already running.'
            );
        }

        this.#allocationInProgress = true;

        try {
            const evaluations = await this.evaluate(framework);

            const selected = new Set();
            const rejected = new Set();

            let effortUsed = 0;
            let budgetUsed = 0;

            const include = (id, mandatory = false) => {
                const closure = this.#dependencyClosure(id);

                const additions = [...closure].filter(
                    key => !selected.has(key)
                );

                for (const key of additions) {
                    const failure = this.policy.validate(
                        this.#initiatives.get(key)
                    );

                    if (failure && !mandatory) {
                        return {
                            accepted: false,
                            reason: failure
                        };
                    }
                }

                const effort = additions.reduce(
                    (sum, key) =>
                        sum + this.#initiatives.get(key).effort,
                    0
                );

                const budget = additions.reduce(
                    (sum, key) =>
                        sum + this.#initiatives.get(key).cost,
                    0
                );

                const exceedsCapacity =
                    effortUsed + effort > this.policy.effortCapacity ||
                    budgetUsed + budget > this.policy.budgetCapacity;

                if (
                    exceedsCapacity &&
                    !(mandatory && this.policy.allowMandatoryOverCapacity)
                ) {
                    return {
                        accepted: false,
                        reason: 'Capacity or budget exceeded.'
                    };
                }

                selected.add(...[]);
                for (const key of additions) {
                    selected.add(key);
                }

                effortUsed += effort;
                budgetUsed += budget;

                return { accepted: true };
            };

            // Mandatory work is handled before optional work.
            for (const evaluation of evaluations) {
                const item = this.#initiatives.get(evaluation.id);

                if (!item.mandatory) continue;

                const result = include(item.id, true);

                if (!result.accepted) {
                    throw new AllocationError(
                        `Mandatory initiative ${item.id} failed: ${result.reason}`
                    );
                }
            }

            for (const evaluation of evaluations) {
                const item = this.#initiatives.get(evaluation.id);

                if (selected.has(item.id) || item.mandatory) {
                    continue;
                }

                if (!evaluation.eligible) {
                    rejected.add(item.id);
                    continue;
                }

                const result = include(item.id);

                if (!result.accepted) {
                    rejected.add(item.id);
                }
            }

            const deferred = new Set(
                [...this.#initiatives.keys()].filter(
                    id => !selected.has(id)
                )
            );

            const totalBusinessValue = [...selected].reduce(
                (sum, id) =>
                    sum + this.#initiatives.get(id).businessValue,
                0
            );

            const opportunityCost = [...deferred].reduce(
                (sum, id) => {
                    const item = this.#initiatives.get(id);
                    return sum + ScoringStrategy.evaluate(item, framework);
                },
                0
            );

            for (const item of this.#initiatives.values()) {
                item.status = selected.has(item.id)
                    ? Status.SELECTED
                    : Status.DEFERRED;
            }

            const result = Object.freeze({
                framework,
                selected: Object.freeze([...selected].sort()),
                deferred: Object.freeze([...deferred].sort()),
                rejected: Object.freeze([...rejected].sort()),
                effortUsed,
                budgetUsed,
                effortRemaining: this.policy.effortCapacity - effortUsed,
                budgetRemaining: this.policy.budgetCapacity - budgetUsed,
                totalBusinessValue,
                opportunityCost,
                evaluations: Object.freeze(evaluations)
            });

            const event = Object.freeze({
                id: crypto.randomUUID(),
                timestamp: new Date().toISOString(),
                result
            });

            this.#history.push(event);

            this.emit('portfolio:allocated', result);

            return result;

        } finally {
            this.#allocationInProgress = false;
        }
    }

    async sensitivityAnalysis() {
        const results = {};

        for (const framework of Object.values(Framework)) {
            results[framework] = await this.allocate(framework);
        }

        return results;
    }

    getSnapshot() {
        return [...this.#initiatives.values()].map(item => ({
            id: item.id,
            name: item.name,
            status: item.status,
            mandatory: item.mandatory
        }));
    }

    getHistory() {
        return structuredClone(this.#history);
    }

    async exportHistory(filePath) {
        const absolutePath = path.resolve(filePath);
        const directory = path.dirname(absolutePath);

        await fs.mkdir(directory, { recursive: true });

        const temporary = `${absolutePath}.${crypto.randomUUID()}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(this.#history, null, 2),
                { encoding: 'utf8', flag: 'wx', mode: 0o600 }
            );

            await fs.rename(temporary, absolutePath);

        } catch (error) {
            await fs.rm(temporary, { force: true });
            throw error;
        }
    }
}


const sampleInitiatives = [
    {
        id: 'P001',
        name: 'Regulatory security compliance',
        reach: 100,
        impact: 10,
        confidence: 0.99,
        effort: 8,
        businessValue: 10,
        urgency: 10,
        riskReduction: 10,
        strategicAlignment: 10,
        cost: 12000,
        mandatory: true,
        priority: Priority.CRITICAL,
        classification: MoSCoW.MUST
    },
    {
        id: 'P002',
        name: 'Customer intelligence platform',
        reach: 8000,
        impact: 8,
        confidence: 0.85,
        effort: 13,
        businessValue: 9,
        urgency: 7,
        riskReduction: 4,
        strategicAlignment: 9,
        cost: 18000,
        dependencies: ['P001'],
        classification: MoSCoW.SHOULD
    },
    {
        id: 'P003',
        name: 'Infrastructure cost reduction',
        reach: 5000,
        impact: 7,
        confidence: 0.95,
        effort: 5,
        businessValue: 8,
        urgency: 8,
        riskReduction: 6,
        strategicAlignment: 8,
        cost: 7000,
        classification: MoSCoW.MUST
    },
    {
        id: 'P004',
        name: 'Operations reporting dashboard',
        reach: 2000,
        impact: 5,
        confidence: 0.90,
        effort: 4,
        businessValue: 5,
        urgency: 3,
        riskReduction: 2,
        strategicAlignment: 6,
        cost: 4000,
        classification: MoSCoW.COULD
    },
    {
        id: 'P005',
        name: 'Disaster recovery improvement',
        reach: 1000,
        impact: 9,
        confidence: 0.90,
        effort: 7,
        businessValue: 9,
        urgency: 9,
        riskReduction: 10,
        strategicAlignment: 9,
        cost: 10000,
        classification: MoSCoW.MUST
    },
    {
        id: 'P006',
        name: 'Mobile interface redesign',
        reach: 6000,
        impact: 6,
        confidence: 0.75,
        effort: 10,
        businessValue: 7,
        urgency: 5,
        riskReduction: 3,
        strategicAlignment: 8,
        cost: 14000,
        classification: MoSCoW.WONT
    }
];


async function main() {
    const policy = new PortfolioPolicy({
        effortCapacity: 35,
        budgetCapacity: 45000,
        minimumConfidence: 0.60,
        requireStrategicAlignment: true
    });

    const engine = new PrioritizationEngine(
        sampleInitiatives,
        policy
    );

    engine.on('initiative:evaluated', evaluation => {
        console.log(
            `EVALUATED | ${evaluation.id} | ` +
            `${evaluation.framework} | ${evaluation.score.toFixed(2)}`
        );
    });

    engine.on('portfolio:allocated', result => {
        console.log(
            `ALLOCATED | ${result.selected.length} initiatives | ` +
            `Value ${result.totalBusinessValue}`
        );
    });

    console.log('\nPRIORITIZATION FUNDAMENTALS');
    console.log('===========================');

    const result = await engine.allocate(Framework.WEIGHTED);

    console.log('\nPORTFOLIO DECISION');
    console.log(JSON.stringify(result, null, 2));

    console.log('\nSENSITIVITY ANALYSIS');

    const sensitivity = await engine.sensitivityAnalysis();

    for (const [framework, allocation] of Object.entries(sensitivity)) {
        console.log(
            `${framework}: ${allocation.selected.join(', ')} | ` +
            `Value: ${allocation.totalBusinessValue}`
        );
    }

    console.log('\nAUDIT HISTORY');
    console.log(`Decisions recorded: ${engine.getHistory().length}`);

    await engine.exportHistory(
        path.join(process.cwd(), 'prioritization-history.json')
    );

    console.log('Audit history exported.');
}


if (require.main === module) {
    main().catch(error => {
        console.error(`${error.name}: ${error.message}`);
        process.exitCode = 1;
    });
}


module.exports = {
    PrioritizationEngine,
    PortfolioPolicy,
    ScoringStrategy,
    ValidationError,
    AllocationError,
    Framework,
    Priority,
    MoSCoW
};
