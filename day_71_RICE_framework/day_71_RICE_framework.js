'use strict';

/*
 * RICE Framework: Event-Driven Product Prioritization
 *
 * Features:
 * - Typed domain objects
 * - Map-based portfolio state
 * - EventEmitter-based change notifications
 * - Asynchronous evidence verification
 * - Policy-based scoring and eligibility
 * - Dependency validation
 * - Scenario simulation
 * - Budget-constrained portfolio selection
 * - JSON reporting
 *
 * RICE = Reach * Impact * Confidence / Effort
 */

const fs = require('node:fs/promises');
const { EventEmitter } = require('node:events');
const crypto = require('node:crypto');

const Impact = Object.freeze({
    MINIMAL: 0.25,
    LOW: 0.5,
    MEDIUM: 1,
    HIGH: 2,
    MASSIVE: 3
});

const Decision = Object.freeze({
    ACCEPT: 'ACCEPT',
    REVIEW: 'REVIEW',
    DEFER: 'DEFER'
});

const Status = Object.freeze({
    DRAFT: 'DRAFT',
    READY: 'READY',
    APPROVED: 'APPROVED',
    REJECTED: 'REJECTED'
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class RICEItem {
    constructor(data) {
        const {
            id,
            name,
            reach,
            impact,
            confidence,
            effort,
            category = 'Product',
            period = 'monthly',
            evidence = '',
            dependencies = [],
            strategicValue = 0
        } = data;

        if (typeof id !== 'string' || !id.trim()) {
            throw new ValidationError('Valid ID required.');
        }

        if (typeof name !== 'string' || !name.trim()) {
            throw new ValidationError('Valid name required.');
        }

        const numericFields = {
            reach,
            impact,
            confidence,
            effort,
            strategicValue
        };

        for (const [key, value] of Object.entries(numericFields)) {
            if (typeof value !== 'number' || !Number.isFinite(value)) {
                throw new ValidationError(`${key} must be finite.`);
            }
        }

        if (reach < 0 || impact <= 0 || effort <= 0) {
            throw new ValidationError(
                'Reach must be non-negative; impact and effort must be positive.'
            );
        }

        if (confidence < 0 || confidence > 100) {
            throw new ValidationError('Confidence must be 0-100.');
        }

        if (strategicValue < 0) {
            throw new ValidationError('Strategic value cannot be negative.');
        }

        if (!Array.isArray(dependencies)) {
            throw new ValidationError('Dependencies must be an array.');
        }

        if (new Set(dependencies).size !== dependencies.length) {
            throw new ValidationError('Duplicate dependencies are invalid.');
        }

        if (dependencies.includes(id)) {
            throw new ValidationError('Self-dependency is invalid.');
        }

        if (typeof period !== 'string' || !period.trim()) {
            throw new ValidationError('Measurement period required.');
        }

        this.id = id;
        this.name = name;
        this.reach = reach;
        this.impact = impact;
        this.confidence = confidence;
        this.effort = effort;
        this.category = category;
        this.period = period;
        this.evidence = evidence;
        this.dependencies = Object.freeze([...dependencies]);
        this.strategicValue = strategicValue;

        Object.freeze(this);
    }
}

class RICEPolicy {
    constructor({
        highThreshold = 100,
        mediumThreshold = 30,
        minimumConfidence = 40,
        requireEvidence = true
    } = {}) {
        if (
            !Number.isFinite(highThreshold) ||
            !Number.isFinite(mediumThreshold) ||
            highThreshold <= mediumThreshold ||
            mediumThreshold < 0
        ) {
            throw new ValidationError('Invalid scoring thresholds.');
        }

        if (
            !Number.isFinite(minimumConfidence) ||
            minimumConfidence < 0 ||
            minimumConfidence > 100
        ) {
            throw new ValidationError('Invalid confidence threshold.');
        }

        this.highThreshold = highThreshold;
        this.mediumThreshold = mediumThreshold;
        this.minimumConfidence = minimumConfidence;
        this.requireEvidence = requireEvidence;
        Object.freeze(this);
    }

    evaluate(item) {
        const score =
            item.reach *
            item.impact *
            (item.confidence / 100) /
            item.effort;

        const limitations = [];

        if (item.confidence < this.minimumConfidence) {
            limitations.push('Insufficient confidence');
        }

        if (item.reach === 0) {
            limitations.push('No measurable reach');
        }

        if (this.requireEvidence && !item.evidence.trim()) {
            limitations.push('Evidence is missing');
        }

        let decision;

        if (
            limitations.includes('Insufficient confidence') ||
            limitations.includes('Evidence is missing')
        ) {
            decision = Decision.REVIEW;
        } else if (score >= this.highThreshold) {
            decision = Decision.ACCEPT;
        } else if (score >= this.mediumThreshold) {
            decision = Decision.REVIEW;
        } else {
            decision = Decision.DEFER;
        }

        const priority =
            score >= this.highThreshold ? 'HIGH' :
            score >= this.mediumThreshold ? 'MEDIUM' : 'LOW';

        return Object.freeze({
            id: item.id,
            score,
            priority,
            decision,
            limitations: Object.freeze(limitations),
            efficiency: score / item.effort
        });
    }
}

class EvidenceService {
    constructor(verifier) {
        this.verifier = verifier;
    }

    async verify(item) {
        if (!item.evidence.trim()) {
            return {
                verified: false,
                reason: 'Evidence reference is missing'
            };
        }

        try {
            const verified = await this.verifier(item.evidence);

            return {
                verified: Boolean(verified),
                reason: verified ? 'Verified' : 'Evidence could not be verified'
            };
        } catch (error) {
            return {
                verified: false,
                reason: `Verification failed: ${error.message}`
            };
        }
    }
}

class Portfolio extends EventEmitter {
    #items = new Map();
    #results = new Map();
    #policy;
    #evidenceService;
    #revision = 0;

    constructor(policy, evidenceService) {
        super();
        this.#policy = policy;
        this.#evidenceService = evidenceService;
    }

    get revision() {
        return this.#revision;
    }

    add(data) {
        const item = data instanceof RICEItem ? data : new RICEItem(data);

        if (this.#items.has(item.id)) {
            throw new ValidationError(`Duplicate item: ${item.id}`);
        }

        this.#items.set(item.id, item);
        this.#revision++;

        this.emit('itemAdded', {
            id: item.id,
            revision: this.#revision
        });

        return item;
    }

    remove(id) {
        if (!this.#items.has(id)) {
            throw new ValidationError(`Unknown item: ${id}`);
        }

        this.#items.delete(id);
        this.#results.delete(id);
        this.#revision++;

        this.emit('itemRemoved', {
            id,
            revision: this.#revision
        });
    }

    get(id) {
        return this.#items.get(id);
    }

    list() {
        return [...this.#items.values()];
    }

    validateDependencies() {
        const issues = [];

        for (const item of this.#items.values()) {
            for (const dependency of item.dependencies) {
                if (!this.#items.has(dependency)) {
                    issues.push({
                        itemId: item.id,
                        dependency,
                        issue: 'Dependency does not exist'
                    });
                }
            }
        }

        const visiting = new Set();
        const visited = new Set();

        const visit = id => {
            if (visiting.has(id)) {
                issues.push({
                    itemId: id,
                    issue: 'Dependency cycle detected'
                });
                return;
            }

            if (visited.has(id)) return;

            visiting.add(id);

            const item = this.#items.get(id);

            for (const dependency of item.dependencies) {
                if (this.#items.has(dependency)) {
                    visit(dependency);
                }
            }

            visiting.delete(id);
            visited.add(id);
        };

        for (const id of this.#items.keys()) {
            visit(id);
        }

        return issues;
    }

    async evaluateAll() {
        const dependencyIssues = this.validateDependencies();

        if (dependencyIssues.length) {
            throw new ValidationError(
                JSON.stringify(dependencyIssues)
            );
        }

        // Concurrent evidence verification avoids serial network latency.
        const items = this.list();

        const evidenceResults = await Promise.all(
            items.map(async item => [
                item.id,
                await this.#evidenceService.verify(item)
            ])
        );

        const evidenceMap = new Map(evidenceResults);

        const evaluated = items.map(item => {
            const result = this.#policy.evaluate(item);
            const evidence = evidenceMap.get(item.id);

            const finalDecision =
                evidence.verified &&
                result.decision === Decision.ACCEPT
                    ? Decision.ACCEPT
                    : evidence.verified
                        ? result.decision
                        : Decision.REVIEW;

            const enriched = Object.freeze({
                ...result,
                evidence,
                decision: finalDecision
            });

            this.#results.set(item.id, enriched);

            return enriched;
        });

        evaluated.sort((a, b) =>
            b.score - a.score ||
            a.id.localeCompare(b.id)
        );

        const ranked = evaluated.map((result, index) =>
            Object.freeze({
                ...result,
                rank: index + 1
            })
        );

        this.emit('evaluationCompleted', {
            revision: this.#revision,
            count: ranked.length
        });

        return ranked;
    }

    selectPortfolio(results, budget) {
        if (!Number.isFinite(budget) || budget < 0) {
            throw new ValidationError('Invalid effort budget.');
        }

        const scale = 10;
        const capacity = Math.floor(budget * scale + 1e-9);

        if (capacity > 100000) {
            throw new ValidationError('Budget exceeds planner limit.');
        }

        const eligible = results.filter(result =>
            result.decision === Decision.ACCEPT
        );

        const dp = new Float64Array(capacity + 1);
        const selections = Array.from(
            { length: capacity + 1 },
            () => []
        );

        for (const result of eligible) {
            const item = this.#items.get(result.id);
            const weight = Math.ceil(item.effort * scale - 1e-12);

            for (let c = capacity; c >= weight; c--) {
                const candidate = dp[c - weight] + result.score;

                if (candidate > dp[c]) {
                    dp[c] = candidate;
                    selections[c] = [
                        ...selections[c - weight],
                        result.id
                    ];
                }
            }
        }

        return selections[capacity].map(id => ({
            item: this.#items.get(id),
            result: this.#results.get(id)
        }));
    }

    async exportJSON(results, filename) {
        const report = {
            generatedAt: new Date().toISOString(),
            revision: this.#revision,
            results
        };

        // Exclusive creation avoids accidentally overwriting existing reports.
        await fs.writeFile(
            filename,
            JSON.stringify(report, null, 2),
            {
                encoding: 'utf8',
                flag: 'wx',
                mode: 0o600
            }
        );
    }
}

class ScenarioAnalyzer {
    static score(item, factors = {}) {
        const {
            reach = 1,
            impact = 1,
            confidence = 1,
            effort = 1
        } = factors;

        for (const value of Object.values(factors)) {
            if (!Number.isFinite(value) || value <= 0) {
                throw new ValidationError(
                    'Scenario factors must be positive and finite.'
                );
            }
        }

        const adjustedReach = item.reach * reach;
        const adjustedImpact = item.impact * impact;
        const adjustedConfidence = Math.min(
            100,
            item.confidence * confidence
        );
        const adjustedEffort = item.effort * effort;

        return (
            adjustedReach *
            adjustedImpact *
            adjustedConfidence / 100 /
            adjustedEffort
        );
    }

    static analyze(item) {
        return {
            optimistic: this.score(item, {
                reach: 1.2,
                impact: 1.2,
                confidence: 1.1,
                effort: 0.9
            }),
            baseline: this.score(item),
            pessimistic: this.score(item, {
                reach: 0.8,
                impact: 0.8,
                confidence: 0.8,
                effort: 1.2
            })
        };
    }
}

async function main() {
    const policy = new RICEPolicy({
        highThreshold: 100,
        mediumThreshold: 30,
        minimumConfidence: 40,
        requireEvidence: true
    });

    const evidenceService = new EvidenceService(
        async reference => {
            // Demonstration verifier: production deployments should validate
            // evidence against an authenticated evidence repository.
            await Promise.resolve();
            return reference.length >= 5;
        }
    );

    const portfolio = new Portfolio(policy, evidenceService);

    portfolio.on('itemAdded', event => {
        console.log(`Added ${event.id}, revision ${event.revision}`);
    });

    portfolio.on('evaluationCompleted', event => {
        console.log(`Evaluated ${event.count} items.`);
    });

    const sampleItems = [
        {
            id: 'P001',
            name: 'Account recovery',
            reach: 12000,
            impact: 2,
            confidence: 90,
            effort: 3,
            category: 'Security',
            strategicValue: 8,
            evidence: 'support-ticket-study'
        },
        {
            id: 'P002',
            name: 'Dashboard redesign',
            reach: 8500,
            impact: 1,
            confidence: 85,
            effort: 4,
            evidence: 'customer-survey'
        },
        {
            id: 'P003',
            name: 'Incident notifications',
            reach: 15000,
            impact: 1.5,
            confidence: 95,
            effort: 2,
            category: 'Reliability',
            evidence: 'incident-log-analysis'
        },
        {
            id: 'P004',
            name: 'Recommendation engine',
            reach: 5000,
            impact: 3,
            confidence: 35,
            effort: 8,
            evidence: 'pilot-observations'
        },
        {
            id: 'P005',
            name: 'Accessibility improvements',
            reach: 6000,
            impact: 1.5,
            confidence: 95,
            effort: 2.5,
            evidence: 'accessibility-audit'
        }
    ];

    for (const item of sampleItems) {
        portfolio.add(item);
    }

    const results = await portfolio.evaluateAll();

    console.log('\nRICE RANKING');

    console.table(
        results.map(result => ({
            rank: result.rank,
            id: result.id,
            score: result.score.toFixed(2),
            priority: result.priority,
            decision: result.decision,
            evidenceVerified: result.evidence.verified
        }))
    );

    console.log('\nPORTFOLIO UNDER 12 PERSON-MONTHS');

    const selected = portfolio.selectPortfolio(results, 12);

    console.table(
        selected.map(entry => ({
            name: entry.item.name,
            effort: entry.item.effort,
            score: entry.result.score
        }))
    );

    console.log('\nSCENARIO ANALYSIS');

    for (const item of portfolio.list()) {
        console.log(
            item.name,
            ScenarioAnalyzer.analyze(item)
        );
    }

    // A random identifier prevents accidental collisions with previous reports.
    const reportName = `rice-${crypto.randomUUID()}.json`;

    await portfolio.exportJSON(results, reportName);

    console.log(`Report created: ${reportName}`);
}

if (require.main === module) {
    main().catch(error => {
        console.error('RICE execution failed:', error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    RICEItem,
    RICEPolicy,
    EvidenceService,
    Portfolio,
    ScenarioAnalyzer,
    Decision,
    Impact,
    Status,
    ValidationError
};
