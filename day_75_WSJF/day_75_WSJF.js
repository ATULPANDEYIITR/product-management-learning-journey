"use strict";

/*
 * Weighted Shortest Job First prioritization system.
 *
 * Cost of Delay = Business Value + Time Criticality + Risk Reduction
 * WSJF = Cost of Delay / Job Size
 *
 * This implementation uses an event-driven backlog, immutable work-item
 * snapshots, policy evaluation, asynchronous change processing,
 * dependency-aware scheduling, and scenario analysis.
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const path = require("node:path");
const { randomUUID } = require("node:crypto");

class ValidationError extends Error {}
class DependencyError extends Error {}
class SchedulingError extends Error {}

const Status = Object.freeze({
    BACKLOG: "BACKLOG",
    READY: "READY",
    IN_PROGRESS: "IN_PROGRESS",
    COMPLETED: "COMPLETED",
    BLOCKED: "BLOCKED"
});

function validateScore(value, name, allowZero = true) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value < 0 ||
        (!allowZero && value === 0)
    ) {
        throw new ValidationError(
            `${name} must be a finite ${allowZero ? "non-negative" : "positive"} number`
        );
    }

    return value;
}

function createWorkItem(input) {
    if (!input || typeof input !== "object") {
        throw new ValidationError("Work item must be an object");
    }

    const id = String(input.id ?? "").trim();
    const title = String(input.title ?? "").trim();

    if (!id || !title) {
        throw new ValidationError("ID and title are required");
    }

    const dependencies = Object.freeze(
        [...new Set(input.dependencies ?? [])].map(String)
    );

    if (dependencies.includes(id)) {
        throw new DependencyError("Self-dependency is prohibited");
    }

    const status = input.status ?? Status.READY;

    if (!Object.values(Status).includes(status)) {
        throw new ValidationError(`Invalid status: ${status}`);
    }

    return Object.freeze({
        id,
        title,
        businessValue: validateScore(
            input.businessValue,
            "Business value"
        ),
        timeCriticality: validateScore(
            input.timeCriticality,
            "Time criticality"
        ),
        riskReduction: validateScore(
            input.riskReduction,
            "Risk reduction"
        ),
        jobSize: validateScore(input.jobSize, "Job size", false),
        dependencies,
        status,
        owner: String(input.owner ?? "Unassigned")
    });
}

function calculateCostOfDelay(item) {
    return (
        item.businessValue +
        item.timeCriticality +
        item.riskReduction
    );
}

function calculateWSJF(item) {
    return calculateCostOfDelay(item) / item.jobSize;
}

class PrioritizationPolicy {
    constructor({
        minimumBusinessValue = 0,
        minimumRiskReduction = 0,
        maximumJobSize = Infinity,
        requireReadyStatus = true
    } = {}) {
        this.minimumBusinessValue = minimumBusinessValue;
        this.minimumRiskReduction = minimumRiskReduction;
        this.maximumJobSize = maximumJobSize;
        this.requireReadyStatus = requireReadyStatus;

        if (
            minimumBusinessValue < 0 ||
            minimumRiskReduction < 0 ||
            maximumJobSize <= 0
        ) {
            throw new ValidationError("Invalid policy thresholds");
        }

        Object.freeze(this);
    }

    evaluate(item) {
        const reasons = [];

        if (item.businessValue < this.minimumBusinessValue) {
            reasons.push("Business value below policy threshold");
        }

        if (item.riskReduction < this.minimumRiskReduction) {
            reasons.push("Risk reduction below policy threshold");
        }

        if (item.jobSize > this.maximumJobSize) {
            reasons.push("Job size exceeds policy limit");
        }

        if (
            this.requireReadyStatus &&
            item.status !== Status.READY
        ) {
            reasons.push("Work item is not READY");
        }

        return Object.freeze({
            eligible: reasons.length === 0,
            reasons
        });
    }
}

class Backlog extends EventEmitter {
    #items = new Map();
    #policy;

    constructor(policy = new PrioritizationPolicy()) {
        super();
        this.#policy = policy;
    }

    get size() {
        return this.#items.size;
    }

    get(id) {
        return this.#items.get(id);
    }

    values() {
        return [...this.#items.values()];
    }

    add(input) {
        const item = createWorkItem(input);

        if (this.#items.has(item.id)) {
            throw new ValidationError(
                `Duplicate item ID: ${item.id}`
            );
        }

        this.#items.set(item.id, item);
        this.#validateDependencies();

        this.emit("item:created", item);
        return item;
    }

    updateStatus(id, nextStatus) {
        const current = this.#items.get(id);

        if (!current) {
            throw new ValidationError(`Unknown item: ${id}`);
        }

        if (!Object.values(Status).includes(nextStatus)) {
            throw new ValidationError("Invalid target status");
        }

        const transitions = {
            BACKLOG: ["READY", "BLOCKED"],
            READY: ["IN_PROGRESS", "BLOCKED", "BACKLOG"],
            IN_PROGRESS: ["COMPLETED", "BLOCKED", "READY"],
            BLOCKED: ["READY", "BACKLOG"],
            COMPLETED: []
        };

        if (!transitions[current.status].includes(nextStatus)) {
            throw new SchedulingError(
                `Invalid transition ${current.status} -> ${nextStatus}`
            );
        }

        if (nextStatus === Status.READY) {
            const incomplete = current.dependencies.filter(id => {
                return this.#items.get(id).status !== Status.COMPLETED;
            });

            if (incomplete.length > 0) {
                throw new DependencyError(
                    `Incomplete dependencies: ${incomplete.join(", ")}`
                );
            }
        }

        const updated = createWorkItem({
            ...current,
            status: nextStatus
        });

        this.#items.set(id, updated);

        this.emit("item:status-changed", {
            id,
            previous: current.status,
            current: nextStatus
        });

        return updated;
    }

    #validateDependencies() {
        for (const item of this.#items.values()) {
            for (const dependency of item.dependencies) {
                if (!this.#items.has(dependency)) {
                    throw new DependencyError(
                        `${item.id} references missing dependency ${dependency}`
                    );
                }
            }
        }

        const visiting = new Set();
        const visited = new Set();

        const visit = id => {
            if (visiting.has(id)) {
                throw new DependencyError(
                    `Dependency cycle detected at ${id}`
                );
            }

            if (visited.has(id)) return;

            visiting.add(id);

            for (const dependency of this.#items.get(id).dependencies) {
                visit(dependency);
            }

            visiting.delete(id);
            visited.add(id);
        };

        for (const id of this.#items.keys()) {
            visit(id);
        }
    }

    ranking() {
        return this.values()
            .filter(item => {
                return this.#policy.evaluate(item).eligible;
            })
            .map(item => ({
                ...item,
                costOfDelay: calculateCostOfDelay(item),
                wsjf: calculateWSJF(item)
            }))
            .sort((a, b) =>
                b.wsjf - a.wsjf ||
                b.costOfDelay - a.costOfDelay ||
                a.jobSize - b.jobSize ||
                a.id.localeCompare(b.id)
            );
    }

    async schedule(capacity) {
        validateScore(capacity, "Capacity");

        const completed = new Set(
            this.values()
                .filter(item => item.status === Status.COMPLETED)
                .map(item => item.id)
        );

        const selected = [];
        let remaining = capacity;

        const candidates = this.ranking();

        // A dependency must already be completed or selected earlier.
        while (true) {
            const next = candidates.find(item => {
                return (
                    !selected.some(selectedItem => selectedItem.id === item.id) &&
                    item.jobSize <= remaining &&
                    item.dependencies.every(id => completed.has(id))
                );
            });

            if (!next) break;

            selected.push(next);
            completed.add(next.id);
            remaining -= next.jobSize;

            // Yield to the event loop between scheduling decisions.
            await new Promise(resolve => setImmediate(resolve));

            this.emit("item:selected", {
                id: next.id,
                remainingCapacity: remaining
            });
        }

        return Object.freeze({
            selected: Object.freeze(selected),
            usedCapacity: capacity - remaining,
            remainingCapacity: remaining
        });
    }

    scenario(itemId, changes = {}) {
        const item = this.#items.get(itemId);

        if (!item) {
            throw new ValidationError(`Unknown item: ${itemId}`);
        }

        const hypothetical = createWorkItem({
            ...item,
            businessValue:
                item.businessValue + (changes.businessValue ?? 0),
            timeCriticality:
                item.timeCriticality + (changes.timeCriticality ?? 0),
            riskReduction:
                item.riskReduction + (changes.riskReduction ?? 0),
            jobSize:
                item.jobSize + (changes.jobSize ?? 0)
        });

        return Object.freeze({
            id: item.id,
            currentWSJF: calculateWSJF(item),
            hypotheticalWSJF: calculateWSJF(hypothetical),
            change:
                calculateWSJF(hypothetical) - calculateWSJF(item)
        });
    }

    report() {
        return {
            generatedAt: new Date().toISOString(),
            formula:
                "(businessValue + timeCriticality + riskReduction) / jobSize",
            items: this.ranking()
        };
    }
}

async function saveReport(report, destination) {
    const resolved = path.resolve(destination);
    const temporary = `${resolved}.${randomUUID()}.tmp`;

    try {
        await fs.writeFile(
            temporary,
            JSON.stringify(report, null, 2),
            { encoding: "utf8", flag: "wx", mode: 0o600 }
        );

        await fs.rename(temporary, resolved);
    } catch (error) {
        await fs.rm(temporary, { force: true }).catch(() => {});
        throw error;
    }
}

async function main() {
    const policy = new PrioritizationPolicy({
        minimumBusinessValue: 3,
        minimumRiskReduction: 0,
        maximumJobSize: 20
    });

    const backlog = new Backlog(policy);

    backlog.on("item:created", item => {
        console.log(`Created: ${item.id} - ${item.title}`);
    });

    backlog.on("item:selected", event => {
        console.log(
            `Selected ${event.id}; remaining capacity: ${event.remainingCapacity}`
        );
    });

    const sampleItems = [
        {
            id: "WSJF-101",
            title: "Security vulnerability remediation",
            businessValue: 9,
            timeCriticality: 10,
            riskReduction: 10,
            jobSize: 3
        },
        {
            id: "WSJF-102",
            title: "Payment gateway modernization",
            businessValue: 9,
            timeCriticality: 10,
            riskReduction: 8,
            jobSize: 5
        },
        {
            id: "WSJF-103",
            title: "Database migration",
            businessValue: 7,
            timeCriticality: 6,
            riskReduction: 9,
            jobSize: 5
        },
        {
            id: "WSJF-104",
            title: "Automated regression testing",
            businessValue: 6,
            timeCriticality: 7,
            riskReduction: 8,
            jobSize: 3,
            dependencies: ["WSJF-103"]
        },
        {
            id: "WSJF-105",
            title: "Analytics dashboard",
            businessValue: 8,
            timeCriticality: 5,
            riskReduction: 3,
            jobSize: 8
        }
    ];

    for (const item of sampleItems) {
        backlog.add(item);
    }

    console.log("\nWSJF RANKING");

    for (const item of backlog.ranking()) {
        console.log(
            `${item.id.padEnd(12)} ` +
            `${item.title.padEnd(35)} ` +
            `CoD=${item.costOfDelay} ` +
            `Size=${item.jobSize} ` +
            `WSJF=${item.wsjf.toFixed(3)}`
        );
    }

    console.log("\nCAPACITY PLAN");
    const plan = await backlog.schedule(12);

    console.log(
        plan.selected.map(item => item.id).join(" -> ")
    );

    console.log("\nSCENARIO ANALYSIS");
    console.log(
        backlog.scenario("WSJF-105", {
            businessValue: 3,
            timeCriticality: 2
        })
    );

    const report = backlog.report();

    await saveReport(report, "wsjf_report.json");

    // Failure-handling examples.
    try {
        backlog.add({
            id: "INVALID",
            title: "Invalid zero-size task",
            businessValue: 5,
            timeCriticality: 5,
            riskReduction: 5,
            jobSize: 0
        });
    } catch (error) {
        console.log(`Expected validation failure: ${error.message}`);
    }

    console.log("\nReport saved successfully.");
}

main().catch(error => {
    console.error("WSJF execution failed:", error.message);
    process.exitCode = 1;
});
