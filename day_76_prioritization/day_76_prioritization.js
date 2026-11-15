"use strict";

/*
 * Advanced Opportunity Prioritization Engine
 *
 * Engineering perspective:
 * - Event-driven opportunity lifecycle
 * - Immutable scoring configurations
 * - Map-based opportunity registry
 * - Asynchronous evaluation
 * - Policy-based economic and strategic scoring
 * - Dependency-aware portfolio construction
 * - Budget allocation and sensitivity analysis
 * - Auditable decision events
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");

const Status = Object.freeze({
    PROPOSED: "PROPOSED",
    EVALUATED: "EVALUATED",
    APPROVED: "APPROVED",
    DEFERRED: "DEFERRED",
    REJECTED: "REJECTED"
});

const Tier = Object.freeze({
    CRITICAL: "CRITICAL",
    HIGH: "HIGH",
    MEDIUM: "MEDIUM",
    LOW: "LOW"
});

class PrioritizationError extends Error {
    constructor(message) {
        super(message);
        this.name = "PrioritizationError";
    }
}

class ValidationError extends PrioritizationError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class PolicyConflictError extends PrioritizationError {
    constructor(message) {
        super(message);
        this.name = "PolicyConflictError";
    }
}

const DEFAULT_WEIGHTS = Object.freeze({
    strategicFit: 0.25,
    economicValue: 0.25,
    customerValue: 0.15,
    urgency: 0.15,
    feasibility: 0.10,
    riskAdjustment: 0.10
});

function validateWeights(weights) {
    const entries = Object.entries(weights);

    if (entries.length !== Object.keys(DEFAULT_WEIGHTS).length) {
        throw new ValidationError("Unexpected scoring criteria.");
    }

    for (const [key, value] of entries) {
        if (!(key in DEFAULT_WEIGHTS)) {
            throw new ValidationError(`Unknown weight: ${key}`);
        }

        if (!Number.isFinite(value) || value < 0) {
            throw new ValidationError(`Invalid weight: ${key}`);
        }
    }

    const total = entries.reduce((sum, [, value]) => sum + value, 0);

    if (Math.abs(total - 1) > 1e-9) {
        throw new ValidationError("Weights must sum to 1.");
    }

    return Object.freeze({ ...weights });
}

function validateOpportunity(input) {
    if (!input || typeof input !== "object") {
        throw new ValidationError("Opportunity must be an object.");
    }

    const requiredStrings = [
        "id",
        "name",
        "description"
    ];

    for (const key of requiredStrings) {
        if (
            typeof input[key] !== "string" ||
            input[key].trim().length === 0
        ) {
            throw new ValidationError(`${key} is required.`);
        }
    }

    const bounded = [
        "strategicFit",
        "customerValue",
        "urgency",
        "feasibility",
        "risk",
        "confidence"
    ];

    for (const key of bounded) {
        if (
            !Number.isFinite(input[key]) ||
            input[key] < 0 ||
            input[key] > 100
        ) {
            throw new ValidationError(
                `${key} must be between 0 and 100.`
            );
        }
    }

    const nonNegative = [
        "expectedBenefit",
        "implementationCost",
        "costOfDelay",
        "implementationEffort"
    ];

    for (const key of nonNegative) {
        if (
            !Number.isFinite(input[key]) ||
            input[key] < 0
        ) {
            throw new ValidationError(
                `${key} must be finite and non-negative.`
            );
        }
    }

    if (
        input.implementationCost <= 0 ||
        input.implementationEffort <= 0
    ) {
        throw new ValidationError(
            "Cost and effort must be greater than zero."
        );
    }

    const dependencies = input.dependencies ?? [];

    if (
        !Array.isArray(dependencies) ||
        new Set(dependencies).size !== dependencies.length ||
        dependencies.some(
            item => typeof item !== "string" || !item.trim()
        )
    ) {
        throw new ValidationError("Invalid dependency list.");
    }

    if (dependencies.includes(input.id)) {
        throw new PolicyConflictError(
            "Self-dependency is prohibited."
        );
    }

    return Object.freeze({
        ...input,
        dependencies: Object.freeze([...dependencies]),
        mandatory: input.mandatory === true,
        status: input.status ?? Status.PROPOSED
    });
}

class EconomicPolicy {
    evaluate(opportunity) {
        const probability = opportunity.confidence / 100;

        const expectedBenefit =
            opportunity.expectedBenefit * probability;

        const netValue =
            expectedBenefit - opportunity.implementationCost;

        const roi =
            (netValue / opportunity.implementationCost) * 100;

        const economicScore = Math.max(
            0,
            Math.min(
                100,
                50 + 50 * (
                    netValue / opportunity.implementationCost
                )
            )
        );

        return Object.freeze({
            expectedBenefit,
            netValue,
            roi,
            economicScore
        });
    }

    wsjf(opportunity) {
        return (
            opportunity.costOfDelay /
            opportunity.implementationEffort
        );
    }
}

class StrategicPolicy {
    evaluate(opportunity) {
        return opportunity.strategicFit;
    }

    isAligned(opportunity, minimumFit = 60) {
        return opportunity.strategicFit >= minimumFit;
    }
}

class ScoringService {
    constructor(weights = DEFAULT_WEIGHTS) {
        this.weights = validateWeights(weights);
        this.economicPolicy = new EconomicPolicy();
        this.strategicPolicy = new StrategicPolicy();
    }

    score(opportunity) {
        const economic =
            this.economicPolicy.evaluate(opportunity);

        const components = {
            strategicFit:
                this.strategicPolicy.evaluate(opportunity),

            economicValue:
                economic.economicScore,

            customerValue:
                opportunity.customerValue,

            urgency:
                opportunity.urgency,

            feasibility:
                opportunity.feasibility,

            riskAdjustment:
                100 - opportunity.risk
        };

        const weightedScore = Object.entries(components)
            .reduce(
                (sum, [key, value]) =>
                    sum + value * this.weights[key],
                0
            );

        const adjustedScore =
            weightedScore * opportunity.confidence / 100;

        let tier = Tier.LOW;

        if (adjustedScore >= 85) {
            tier = Tier.CRITICAL;
        } else if (adjustedScore >= 70) {
            tier = Tier.HIGH;
        } else if (adjustedScore >= 50) {
            tier = Tier.MEDIUM;
        }

        return Object.freeze({
            id: opportunity.id,
            name: opportunity.name,
            components,
            weightedScore: Number(weightedScore.toFixed(2)),
            adjustedScore: Number(adjustedScore.toFixed(2)),
            expectedBenefit: economic.expectedBenefit,
            netValue: economic.netValue,
            roi: economic.roi,
            wsjf: this.economicPolicy.wsjf(opportunity),
            tier
        });
    }
}

class PortfolioPolicy {
    constructor(budget) {
        if (!Number.isFinite(budget) || budget < 0) {
            throw new ValidationError("Invalid portfolio budget.");
        }

        this.budget = budget;
    }

    select(opportunities, scores) {
        const registry = new Map(
            opportunities.map(item => [item.id, item])
        );

        const scoreMap = new Map(
            scores.map(item => [item.id, item])
        );

        const selected = new Set();
        const deferred = new Set();

        let remaining = this.budget;

        function dependencyClosure(id, result = new Set()) {
            if (result.has(id)) return result;

            const item = registry.get(id);

            if (!item) {
                throw new PolicyConflictError(
                    `Missing dependency: ${id}`
                );
            }

            result.add(id);

            for (const dependency of item.dependencies) {
                dependencyClosure(dependency, result);
            }

            return result;
        }

        const ordered = [...opportunities].sort((a, b) => {
            if (a.mandatory !== b.mandatory) {
                return Number(b.mandatory) - Number(a.mandatory);
            }

            const scoreDifference =
                scoreMap.get(b.id).adjustedScore -
                scoreMap.get(a.id).adjustedScore;

            return scoreDifference ||
                a.id.localeCompare(b.id);
        });

        for (const item of ordered) {
            const required = dependencyClosure(item.id);

            const missing = [...required].filter(
                id => !selected.has(id)
            );

            const cost = missing.reduce(
                (sum, id) =>
                    sum + registry.get(id).implementationCost,
                0
            );

            if (cost <= remaining) {
                missing.forEach(id => selected.add(id));
                remaining -= cost;
            } else if (item.mandatory) {
                throw new PolicyConflictError(
                    `Mandatory opportunity ${item.id} ` +
                    "cannot fit within the budget."
                );
            } else {
                deferred.add(item.id);
            }
        }

        const selectedItems = [...selected]
            .map(id => registry.get(id));

        return Object.freeze({
            budget: this.budget,
            allocated: this.budget - remaining,
            remaining,
            selected: [...selected].sort(),
            deferred: [...deferred].sort(),
            expectedBenefit: selectedItems.reduce(
                (sum, item) =>
                    sum + item.expectedBenefit *
                    item.confidence / 100,
                0
            ),
            netValue: selectedItems.reduce(
                (sum, item) =>
                    sum + item.expectedBenefit *
                    item.confidence / 100 -
                    item.implementationCost,
                0
            )
        });
    }
}

class OpportunityRegistry extends EventEmitter {
    #items = new Map();
    #scores = new Map();
    #scoringService;

    constructor(scoringService = new ScoringService()) {
        super();
        this.#scoringService = scoringService;
    }

    register(input) {
        const opportunity = validateOpportunity(input);

        if (this.#items.has(opportunity.id)) {
            throw new ValidationError(
                `Duplicate opportunity: ${opportunity.id}`
            );
        }

        this.#items.set(opportunity.id, opportunity);

        this.emit("opportunity:registered", {
            id: opportunity.id,
            timestamp: new Date().toISOString()
        });

        return opportunity.id;
    }

    validateDependencies() {
        const visiting = new Set();
        const visited = new Set();

        const visit = id => {
            if (visiting.has(id)) {
                throw new PolicyConflictError(
                    "Circular dependency detected."
                );
            }

            if (visited.has(id)) return;

            const item = this.#items.get(id);

            if (!item) {
                throw new PolicyConflictError(
                    `Unknown opportunity: ${id}`
                );
            }

            visiting.add(id);

            for (const dependency of item.dependencies) {
                if (!this.#items.has(dependency)) {
                    throw new PolicyConflictError(
                        `${id} depends on missing ${dependency}`
                    );
                }

                visit(dependency);
            }

            visiting.delete(id);
            visited.add(id);
        };

        for (const id of this.#items.keys()) {
            visit(id);
        }
    }

    async evaluateAll() {
        this.validateDependencies();

        // Parallel evaluation is safe because scoring policies are pure.
        const results = await Promise.all(
            [...this.#items.values()].map(async item => {
                await Promise.resolve();
                return this.#scoringService.score(item);
            })
        );

        results.sort((a, b) =>
            b.adjustedScore - a.adjustedScore ||
            b.wsjf - a.wsjf ||
            a.id.localeCompare(b.id)
        );

        this.#scores.clear();

        results.forEach((result, index) => {
            const ranked = Object.freeze({
                ...result,
                rank: index + 1
            });

            this.#scores.set(result.id, ranked);
        });

        this.emit("ranking:completed", {
            count: results.length,
            timestamp: new Date().toISOString()
        });

        return [...this.#scores.values()];
    }

    async buildPortfolio(budget) {
        if (this.#scores.size !== this.#items.size) {
            await this.evaluateAll();
        }

        const result = new PortfolioPolicy(budget).select(
            [...this.#items.values()],
            [...this.#scores.values()]
        );

        this.emit("portfolio:allocated", result);

        return result;
    }

    getScore(id) {
        return this.#scores.get(id) ?? null;
    }

    getAuditSnapshot() {
        return {
            opportunities: [...this.#items.values()],
            scores: [...this.#scores.values()]
        };
    }

    async saveReport(filename, portfolio) {
        const report = {
            generatedAt: new Date().toISOString(),
            scoringWeights: this.#scoringService.weights,
            ...this.getAuditSnapshot(),
            portfolio
        };

        const destination = path.resolve(filename);
        await fs.mkdir(path.dirname(destination), {
            recursive: true
        });

        const temporary =
            `${destination}.${crypto.randomUUID()}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(report, null, 2),
                { encoding: "utf8", flag: "wx" }
            );

            await fs.rename(temporary, destination);
        } catch (error) {
            await fs.rm(temporary, { force: true }).catch(() => {});
            throw error;
        }
    }
}

function sampleOpportunities() {
    return [
        {
            id: "OP-001",
            name: "Customer Analytics Platform",
            description: "Centralized customer intelligence.",
            strategicFit: 95,
            expectedBenefit: 900000,
            implementationCost: 250000,
            customerValue: 90,
            urgency: 85,
            feasibility: 80,
            risk: 25,
            confidence: 85,
            costOfDelay: 120000,
            implementationEffort: 12,
            dependencies: []
        },
        {
            id: "OP-002",
            name: "Cloud Cost Optimization",
            description: "Reduce cloud infrastructure expenditure.",
            strategicFit: 85,
            expectedBenefit: 600000,
            implementationCost: 150000,
            customerValue: 65,
            urgency: 75,
            feasibility: 90,
            risk: 15,
            confidence: 90,
            costOfDelay: 85000,
            implementationEffort: 8,
            dependencies: []
        },
        {
            id: "OP-003",
            name: "Security Monitoring Modernization",
            description: "Improve security detection capabilities.",
            strategicFit: 100,
            expectedBenefit: 750000,
            implementationCost: 300000,
            customerValue: 80,
            urgency: 95,
            feasibility: 75,
            risk: 20,
            confidence: 90,
            costOfDelay: 180000,
            implementationEffort: 15,
            dependencies: [],
            mandatory: true
        },
        {
            id: "OP-004",
            name: "Mobile Experience Improvement",
            description: "Improve customer mobile experience.",
            strategicFit: 75,
            expectedBenefit: 450000,
            implementationCost: 120000,
            customerValue: 95,
            urgency: 70,
            feasibility: 85,
            risk: 15,
            confidence: 80,
            costOfDelay: 70000,
            implementationEffort: 7,
            dependencies: ["OP-001"]
        },
        {
            id: "OP-005",
            name: "Reporting Automation",
            description: "Automate repetitive reporting processes.",
            strategicFit: 60,
            expectedBenefit: 180000,
            implementationCost: 80000,
            customerValue: 50,
            urgency: 45,
            feasibility: 95,
            risk: 10,
            confidence: 95,
            costOfDelay: 20000,
            implementationEffort: 5,
            dependencies: []
        }
    ];
}

async function main() {
    const registry = new OpportunityRegistry();

    registry.on("opportunity:registered", event => {
        console.log("Registered:", event.id);
    });

    registry.on("ranking:completed", event => {
        console.log(`Ranking completed: ${event.count} opportunities`);
    });

    registry.on("portfolio:allocated", event => {
        console.log(
            `Portfolio allocated: ${event.allocated.toFixed(2)}`
        );
    });

    for (const opportunity of sampleOpportunities()) {
        registry.register(opportunity);
    }

    const ranking = await registry.evaluateAll();

    console.log("\nOPPORTUNITY RANKING");

    console.table(ranking.map(item => ({
        Rank: item.rank,
        ID: item.id,
        Opportunity: item.name,
        Weighted: item.weightedScore,
        Adjusted: item.adjustedScore,
        ROI: item.roi.toFixed(2),
        WSJF: item.wsjf.toFixed(2),
        Tier: item.tier
    })));

    const portfolio = await registry.buildPortfolio(700000);

    console.log("\nPORTFOLIO DECISION");
    console.log(portfolio);

    await registry.saveReport(
        "./reports/opportunity-prioritization.json",
        portfolio
    );

    console.log("\nReport saved.");
}

main().catch(error => {
    console.error(`${error.name}: ${error.message}`);
    process.exitCode = 1;
});
