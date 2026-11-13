"use strict";

/*
 * VALUE VS EFFORT: EVENT-DRIVEN OPPORTUNITY MANAGEMENT
 *
 * Features:
 * - Opportunity registration and validation
 * - Asynchronous estimation
 * - Weighted value calculations
 * - Risk and confidence adjustments
 * - Opportunity matrix classification
 * - Event-driven recalculation
 * - Dependency validation
 * - Capacity allocation
 * - Audit history
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

const Risk = Object.freeze({
    LOW: "LOW",
    MEDIUM: "MEDIUM",
    HIGH: "HIGH"
});

const Category = Object.freeze({
    QUICK_WIN: "QUICK_WIN",
    STRATEGIC: "STRATEGIC",
    FILL_IN: "FILL_IN",
    LOW_PRIORITY: "LOW_PRIORITY"
});

const RISK_FACTOR = Object.freeze({
    LOW: 1.00,
    MEDIUM: 0.85,
    HIGH: 0.65
});

const WEIGHTS = Object.freeze({
    customerImpact: 0.35,
    strategicAlignment: 0.30,
    revenueImpact: 0.20,
    urgency: 0.15
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class Opportunity {
    constructor(data) {
        this.id = data.id;
        this.name = data.name;
        this.description = data.description ?? "";

        this.customerImpact = data.customerImpact;
        this.strategicAlignment = data.strategicAlignment;
        this.revenueImpact = data.revenueImpact;
        this.urgency = data.urgency;

        this.valueConfidence = data.valueConfidence;
        this.effortConfidence = data.effortConfidence;

        this.effort = Object.freeze({
            low: data.effort.low,
            expected: data.effort.expected,
            high: data.effort.high
        });

        this.risk = data.risk ?? Risk.MEDIUM;
        this.dependencies = Object.freeze([
            ...(data.dependencies ?? [])
        ]);

        Object.freeze(this);
        this.validate();
    }

    validate() {
        if (
            typeof this.id !== "string" ||
            !this.id.trim() ||
            typeof this.name !== "string" ||
            !this.name.trim()
        ) {
            throw new ValidationError("ID and name are required.");
        }

        const ratings = [
            this.customerImpact,
            this.strategicAlignment,
            this.revenueImpact,
            this.urgency,
            this.valueConfidence,
            this.effortConfidence
        ];

        if (!ratings.every(
            value => Number.isFinite(value) &&
                value >= 1 && value <= 5
        )) {
            throw new ValidationError(
                `Invalid rating in ${this.id}. Ratings must be 1-5.`
            );
        }

        const { low, expected, high } = this.effort;

        if (
            ![low, expected, high].every(Number.isFinite) ||
            low < 0 ||
            expected <= 0 ||
            low > expected ||
            expected > high
        ) {
            throw new ValidationError(
                `Invalid effort range in ${this.id}.`
            );
        }

        if (!Object.values(Risk).includes(this.risk)) {
            throw new ValidationError("Unknown risk level.");
        }

        if (
            new Set(this.dependencies).size !==
            this.dependencies.length
        ) {
            throw new ValidationError("Duplicate dependencies.");
        }

        if (this.dependencies.includes(this.id)) {
            throw new ValidationError("Self-dependency is prohibited.");
        }
    }
}

class OpportunityEngine extends EventEmitter {
    constructor() {
        super();

        this.opportunities = new Map();
        this.evaluations = new Map();
        this.audit = [];
        this.revision = 0;
    }

    register(data) {
        const opportunity = new Opportunity(data);

        if (this.opportunities.has(opportunity.id)) {
            throw new ValidationError("Duplicate opportunity ID.");
        }

        this.opportunities.set(opportunity.id, opportunity);
        this.revision++;

        this.record("REGISTERED", opportunity.id);
        this.emit("opportunity:registered", opportunity);

        return opportunity;
    }

    record(action, id, details = {}) {
        this.audit.push(Object.freeze({
            action,
            id,
            revision: this.revision,
            timestamp: new Date().toISOString(),
            details
        }));
    }

    validateDependencies() {
        const visiting = new Set();
        const visited = new Set();

        const visit = id => {
            if (visiting.has(id)) {
                throw new ValidationError(
                    `Dependency cycle involving ${id}.`
                );
            }

            if (visited.has(id)) return;

            const item = this.opportunities.get(id);

            if (!item) {
                throw new ValidationError(
                    `Missing opportunity: ${id}`
                );
            }

            visiting.add(id);

            for (const dependency of item.dependencies) {
                visit(dependency);
            }

            visiting.delete(id);
            visited.add(id);
        };

        for (const id of this.opportunities.keys()) {
            visit(id);
        }
    }

    estimateValue(item) {
        return Object.entries(WEIGHTS).reduce(
            (total, [field, weight]) =>
                total + item[field] * weight,
            0
        ) / 5 * 100;
    }

    async evaluate(item) {
        // Simulates an asynchronous external estimation service.
        await Promise.resolve();

        const value = this.estimateValue(item);
        const effort = (
            item.effort.low +
            item.effort.expected +
            item.effort.high
        ) / 3;

        const confidence = Math.min(
            item.valueConfidence,
            item.effortConfidence
        ) / 5;

        const adjustedValue =
            value * confidence * RISK_FACTOR[item.risk];

        const ratio = adjustedValue / effort;

        let category;

        if (ratio >= 20) {
            category = Category.QUICK_WIN;
        } else if (ratio >= 8) {
            category = Category.STRATEGIC;
        } else if (adjustedValue >= 25) {
            category = Category.FILL_IN;
        } else {
            category = Category.LOW_PRIORITY;
        }

        return Object.freeze({
            id: item.id,
            name: item.name,
            value: Number(value.toFixed(2)),
            adjustedValue: Number(adjustedValue.toFixed(2)),
            effort: Number(effort.toFixed(2)),
            ratio: Number(ratio.toFixed(2)),
            confidence,
            category,
            risk: item.risk
        });
    }

    async evaluateAll() {
        this.validateDependencies();

        const revisionAtStart = this.revision;

        const results = await Promise.all(
            [...this.opportunities.values()].map(
                item => this.evaluate(item)
            )
        );

        // Prevent applying stale calculations after state changes.
        if (revisionAtStart !== this.revision) {
            throw new Error(
                "Opportunity data changed during evaluation."
            );
        }

        this.evaluations.clear();

        for (const result of results) {
            this.evaluations.set(result.id, result);
        }

        results.sort((a, b) =>
            b.ratio - a.ratio ||
            b.adjustedValue - a.adjustedValue
        );

        this.record("EVALUATED", "PORTFOLIO", {
            count: results.length
        });

        this.emit("portfolio:evaluated", results);

        return results;
    }

    allocateCapacity(capacity) {
        if (!Number.isFinite(capacity) || capacity < 0) {
            throw new ValidationError("Invalid capacity.");
        }

        const selected = new Set();
        const ordered = [...this.evaluations.values()]
            .sort((a, b) => b.ratio - a.ratio);

        const resolveBundle = (id, result = new Set()) => {
            if (result.has(id)) return result;

            result.add(id);

            const item = this.opportunities.get(id);

            for (const dependency of item.dependencies) {
                resolveBundle(dependency, result);
            }

            return result;
        };

        let remaining = capacity;

        for (const result of ordered) {
            const bundle = resolveBundle(result.id);
            const pending = [...bundle].filter(
                id => !selected.has(id)
            );

            const requiredEffort = pending.reduce(
                (sum, id) =>
                    sum + this.evaluations.get(id).effort,
                0
            );

            if (requiredEffort <= remaining) {
                pending.forEach(id => selected.add(id));
                remaining -= requiredEffort;
            }
        }

        const allocation = [...selected].map(
            id => this.evaluations.get(id)
        );

        this.record("CAPACITY_ALLOCATED", "PORTFOLIO", {
            capacity,
            remaining: Number(remaining.toFixed(2)),
            selected: [...selected]
        });

        return {
            selected: allocation,
            used: Number((capacity - remaining).toFixed(2)),
            remaining: Number(remaining.toFixed(2))
        };
    }

    async exportReport(filename) {
        const rows = [...this.evaluations.values()];

        const header = [
            "id",
            "name",
            "value",
            "adjustedValue",
            "effort",
            "ratio",
            "category",
            "risk"
        ];

        const csv = [
            header.join(","),
            ...rows.map(row =>
                header.map(key =>
                    `"${String(row[key]).replace(/"/g, '""')}"`
                ).join(",")
            )
        ].join("\n");

        await fs.writeFile(filename, csv, {
            encoding: "utf8",
            flag: "w",
            mode: 0o600
        });
    }
}

async function main() {
    const engine = new OpportunityEngine();

    engine.on("opportunity:registered", item => {
        console.log(`Registered: ${item.name}`);
    });

    engine.on("portfolio:evaluated", results => {
        console.log(`Evaluated ${results.length} opportunities.`);
    });

    const samples = [
        {
            id: "OP-201",
            name: "Deployment Automation",
            customerImpact: 5,
            strategicAlignment: 5,
            revenueImpact: 4,
            urgency: 5,
            valueConfidence: 5,
            effortConfidence: 5,
            effort: { low: 2, expected: 3, high: 5 },
            risk: Risk.LOW
        },
        {
            id: "OP-202",
            name: "Analytics Dashboard",
            customerImpact: 4,
            strategicAlignment: 3,
            revenueImpact: 3,
            urgency: 3,
            valueConfidence: 4,
            effortConfidence: 4,
            effort: { low: 5, expected: 8, high: 12 },
            risk: Risk.MEDIUM
        },
        {
            id: "OP-203",
            name: "Security Automation",
            customerImpact: 5,
            strategicAlignment: 5,
            revenueImpact: 4,
            urgency: 5,
            valueConfidence: 4,
            effortConfidence: 4,
            effort: { low: 4, expected: 6, high: 10 },
            risk: Risk.LOW
        },
        {
            id: "OP-204",
            name: "Documentation Upgrade",
            customerImpact: 2,
            strategicAlignment: 3,
            revenueImpact: 1,
            urgency: 2,
            valueConfidence: 5,
            effortConfidence: 5,
            effort: { low: 2, expected: 3, high: 4 },
            risk: Risk.LOW
        },
        {
            id: "OP-205",
            name: "Data Integration",
            customerImpact: 5,
            strategicAlignment: 5,
            revenueImpact: 5,
            urgency: 4,
            valueConfidence: 3,
            effortConfidence: 3,
            effort: { low: 12, expected: 18, high: 25 },
            risk: Risk.HIGH,
            dependencies: ["OP-204"]
        }
    ];

    for (const item of samples) {
        engine.register(item);
    }

    const results = await engine.evaluateAll();

    console.log("\nOPPORTUNITY RANKING");

    console.table(results);

    const allocation = engine.allocateCapacity(15);

    console.log("\nCAPACITY ALLOCATION");
    console.table(allocation.selected);
    console.log(allocation);

    await engine.exportReport("opportunity_report.csv");

    console.log("\nAUDIT EVENTS:", engine.audit.length);
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
