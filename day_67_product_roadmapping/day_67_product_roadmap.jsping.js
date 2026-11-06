"use strict";

/*
 * Product Roadmapping
 * Event-driven roadmap planning with:
 * - Strategic themes and measurable outcomes
 * - Initiative prioritization
 * - Dependency management
 * - Timeline validation
 * - Capacity policies
 * - Event history
 * - Asynchronous initiative execution
 * - Scenario changes
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

const Status = Object.freeze({
    PROPOSED: "proposed",
    PLANNED: "planned",
    IN_PROGRESS: "in_progress",
    BLOCKED: "blocked",
    COMPLETED: "completed"
});

class RoadmapError extends Error {
    constructor(message) {
        super(message);
        this.name = "RoadmapError";
    }
}

function validateDate(value, field) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        throw new RoadmapError(`${field} must use YYYY-MM-DD.`);
    }

    const parsed = new Date(`${value}T00:00:00Z`);

    if (
        Number.isNaN(parsed.getTime()) ||
        parsed.toISOString().slice(0, 10) !== value
    ) {
        throw new RoadmapError(`${field} is not a valid date.`);
    }

    return parsed;
}

function dateDifference(start, end) {
    return Math.floor(
        (validateDate(end, "end") - validateDate(start, "start"))
        / 86400000
    );
}

class RoadmapEngine extends EventEmitter {
    constructor({ product, start, end, sprintCapacity }) {
        super();

        if (!product || product.trim().length === 0) {
            throw new RoadmapError("Product name is required.");
        }

        if (dateDifference(start, end) < 0) {
            throw new RoadmapError("Invalid planning period.");
        }

        if (!Number.isInteger(sprintCapacity) || sprintCapacity <= 0) {
            throw new RoadmapError("Invalid sprint capacity.");
        }

        this.product = product;
        this.start = start;
        this.end = end;
        this.sprintCapacity = sprintCapacity;

        this.themes = new Map();
        this.outcomes = new Map();
        this.initiatives = new Map();
        this.events = [];
    }

    record(type, details) {
        const event = Object.freeze({
            sequence: this.events.length + 1,
            type,
            timestamp: new Date().toISOString(),
            details: structuredClone(details)
        });

        this.events.push(event);
        this.emit(type, event);
    }

    addTheme(theme) {
        if (!theme.id || !theme.name || !theme.objective) {
            throw new RoadmapError("Incomplete strategic theme.");
        }

        if (this.themes.has(theme.id)) {
            throw new RoadmapError("Duplicate theme.");
        }

        this.themes.set(theme.id, Object.freeze({ ...theme }));
        this.record("theme-added", theme);
    }

    addOutcome(outcome) {
        const numbers = [
            outcome.baseline,
            outcome.target,
            outcome.current
        ];

        if (
            !outcome.id ||
            !outcome.description ||
            numbers.some(value => !Number.isFinite(value))
        ) {
            throw new RoadmapError("Invalid outcome.");
        }

        if (outcome.target === outcome.baseline) {
            throw new RoadmapError("Target must differ from baseline.");
        }

        if (this.outcomes.has(outcome.id)) {
            throw new RoadmapError("Duplicate outcome.");
        }

        this.outcomes.set(outcome.id, { ...outcome });
        this.record("outcome-added", outcome);
    }

    addInitiative(initiative) {
        if (!initiative.id || !initiative.name) {
            throw new RoadmapError("Initiative identity is required.");
        }

        if (this.initiatives.has(initiative.id)) {
            throw new RoadmapError("Duplicate initiative.");
        }

        if (!this.themes.has(initiative.themeId)) {
            throw new RoadmapError("Unknown strategic theme.");
        }

        if (!this.outcomes.has(initiative.outcomeId)) {
            throw new RoadmapError("Unknown outcome.");
        }

        const duration = dateDifference(
            initiative.start,
            initiative.end
        );

        if (
            duration < 0 ||
            dateDifference(this.start, initiative.start) < 0 ||
            dateDifference(initiative.end, this.end) < 0
        ) {
            throw new RoadmapError("Initiative timeline is invalid.");
        }

        if (
            !Number.isInteger(initiative.effort) ||
            initiative.effort <= 0
        ) {
            throw new RoadmapError("Effort must be a positive integer.");
        }

        for (const field of ["impact", "confidence", "alignment"]) {
            if (
                !Number.isFinite(initiative[field]) ||
                initiative[field] < 0 ||
                initiative[field] > 10
            ) {
                throw new RoadmapError(`Invalid ${field}.`);
            }
        }

        if (!Object.values(Status).includes(initiative.status)) {
            throw new RoadmapError("Unknown initiative status.");
        }

        const item = {
            ...initiative,
            dependencies: [...new Set(initiative.dependencies || [])]
        };

        this.initiatives.set(item.id, item);
        this.record("initiative-added", item);
    }

    score(item) {
        // Weighted value score adjusted for confidence and effort.
        return (
            item.impact *
            item.confidence *
            item.alignment /
            item.effort
        );
    }

    prioritized() {
        return [...this.initiatives.values()]
            .sort((a, b) => this.score(b) - this.score(a));
    }

    validateDependencies() {
        const visiting = new Set();
        const visited = new Set();

        const visit = id => {
            if (visiting.has(id)) {
                throw new RoadmapError("Circular dependency detected.");
            }

            if (visited.has(id)) return;

            const item = this.initiatives.get(id);

            if (!item) {
                throw new RoadmapError(`Unknown initiative: ${id}`);
            }

            visiting.add(id);

            for (const dependencyId of item.dependencies) {
                const dependency = this.initiatives.get(dependencyId);

                if (!dependency) {
                    throw new RoadmapError(
                        `Missing dependency: ${dependencyId}`
                    );
                }

                if (dateDifference(
                    dependency.end,
                    item.start
                ) <= 0) {
                    throw new RoadmapError(
                        `${id} must start after ${dependencyId} finishes.`
                    );
                }

                visit(dependencyId);
            }

            visiting.delete(id);
            visited.add(id);
        };

        for (const id of this.initiatives.keys()) {
            visit(id);
        }

        return true;
    }

    transition(id, nextStatus) {
        const item = this.initiatives.get(id);

        if (!item) {
            throw new RoadmapError("Initiative not found.");
        }

        if (!Object.values(Status).includes(nextStatus)) {
            throw new RoadmapError("Invalid status.");
        }

        const allowed = {
            [Status.PROPOSED]: [Status.PLANNED],
            [Status.PLANNED]: [Status.IN_PROGRESS, Status.BLOCKED],
            [Status.IN_PROGRESS]: [
                Status.BLOCKED,
                Status.COMPLETED
            ],
            [Status.BLOCKED]: [
                Status.PLANNED,
                Status.IN_PROGRESS
            ],
            [Status.COMPLETED]: []
        };

        if (!allowed[item.status].includes(nextStatus)) {
            throw new RoadmapError(
                `Transition ${item.status} -> ${nextStatus} rejected.`
            );
        }

        if (nextStatus === Status.IN_PROGRESS) {
            const incomplete = item.dependencies.filter(
                dependencyId =>
                    this.initiatives.get(dependencyId)?.status
                    !== Status.COMPLETED
            );

            if (incomplete.length) {
                throw new RoadmapError(
                    `Unfinished dependencies: ${incomplete.join(", ")}`
                );
            }
        }

        const previous = item.status;
        item.status = nextStatus;

        this.record("status-changed", {
            initiativeId: id,
            previous,
            next: nextStatus
        });
    }

    capacityAnalysis() {
        const sprints = new Map();

        for (const item of this.initiatives.values()) {
            if (item.status === Status.PROPOSED) continue;

            const start = validateDate(item.start, "start");
            const end = validateDate(item.end, "end");

            for (
                let current = new Date(start);
                current <= end;
                current.setUTCDate(current.getUTCDate() + 14)
            ) {
                const sprint = current.toISOString().slice(0, 10);

                if (!sprints.has(sprint)) {
                    sprints.set(sprint, {
                        effort: 0,
                        initiatives: []
                    });
                }

                const entry = sprints.get(sprint);
                entry.effort += item.effort;
                entry.initiatives.push(item.id);
            }
        }

        return [...sprints.entries()].map(([sprint, data]) => ({
            sprint,
            ...data,
            capacity: this.sprintCapacity,
            overloaded: data.effort > this.sprintCapacity
        }));
    }

    updateOutcome(id, current) {
        const outcome = this.outcomes.get(id);

        if (!outcome || !Number.isFinite(current)) {
            throw new RoadmapError("Invalid outcome update.");
        }

        const previous = outcome.current;
        outcome.current = current;

        this.record("outcome-updated", {
            outcomeId: id,
            previous,
            current
        });
    }

    outcomeMetrics() {
        return [...this.outcomes.values()].map(outcome => {
            const progress =
                (outcome.current - outcome.baseline) /
                (outcome.target - outcome.baseline) * 100;

            return {
                id: outcome.id,
                description: outcome.description,
                progress: Math.max(0, Math.min(100, progress)),
                achieved:
                    outcome.target > outcome.baseline
                        ? outcome.current >= outcome.target
                        : outcome.current <= outcome.target
            };
        });
    }

    async executeReadyInitiatives(executor) {
        this.validateDependencies();

        const ready = [...this.initiatives.values()].filter(
            item =>
                item.status === Status.PLANNED &&
                item.dependencies.every(
                    id =>
                        this.initiatives.get(id).status
                        === Status.COMPLETED
                )
        );

        // Execute independent work concurrently.
        const results = await Promise.allSettled(
            ready.map(async item => {
                this.transition(item.id, Status.IN_PROGRESS);

                try {
                    const result = await executor(item);
                    this.transition(item.id, Status.COMPLETED);
                    return { id: item.id, result };
                } catch (error) {
                    this.transition(item.id, Status.BLOCKED);
                    throw error;
                }
            })
        );

        return results;
    }

    snapshot() {
        return {
            product: this.product,
            planningPeriod: {
                start: this.start,
                end: this.end
            },
            themes: [...this.themes.values()],
            outcomes: this.outcomeMetrics(),
            initiatives: this.prioritized().map(item => ({
                ...item,
                score: Number(this.score(item).toFixed(2))
            })),
            capacity: this.capacityAnalysis(),
            events: [...this.events]
        };
    }

    async saveReport(filename) {
        const content = JSON.stringify(this.snapshot(), null, 2);

        // Use a controlled output path and avoid accepting untrusted filenames
        // from external clients in a production deployment.
        await fs.writeFile(filename, content, {
            encoding: "utf8",
            flag: "w"
        });
    }
}

async function main() {
    const roadmap = new RoadmapEngine({
        product: "Enterprise Commerce Platform",
        start: "2027-01-01",
        end: "2027-03-31",
        sprintCapacity: 40
    });

    roadmap.on("status-changed", event => {
        console.log(
            `[EVENT ${event.sequence}]`,
            event.details.initiativeId,
            event.details.previous,
            "->",
            event.details.next
        );
    });

    roadmap.addTheme({
        id: "T1",
        name: "Customer Experience",
        objective: "Increase checkout completion."
    });

    roadmap.addTheme({
        id: "T2",
        name: "Platform Reliability",
        objective: "Improve availability."
    });

    roadmap.addOutcome({
        id: "O1",
        description: "Checkout completion percentage",
        baseline: 65,
        target: 85,
        current: 72
    });

    roadmap.addOutcome({
        id: "O2",
        description: "Platform availability percentage",
        baseline: 99,
        target: 99.9,
        current: 99.5
    });

    roadmap.addInitiative({
        id: "I1",
        name: "Payment Infrastructure Upgrade",
        themeId: "T2",
        outcomeId: "O2",
        start: "2027-01-01",
        end: "2027-01-20",
        effort: 30,
        impact: 9,
        confidence: 0.9,
        alignment: 10,
        status: Status.PLANNED
    });

    roadmap.addInitiative({
        id: "I2",
        name: "Checkout Performance Optimization",
        themeId: "T1",
        outcomeId: "O1",
        start: "2027-01-21",
        end: "2027-02-10",
        effort: 25,
        impact: 8,
        confidence: 0.85,
        alignment: 9,
        dependencies: ["I1"],
        status: Status.PLANNED
    });

    roadmap.addInitiative({
        id: "I3",
        name: "One-Click Checkout",
        themeId: "T1",
        outcomeId: "O1",
        start: "2027-02-11",
        end: "2027-03-10",
        effort: 40,
        impact: 10,
        confidence: 0.8,
        alignment: 10,
        dependencies: ["I2"],
        status: Status.PROPOSED
    });

    roadmap.validateDependencies();

    console.log("\nPRIORITY RANKING");

    for (const item of roadmap.prioritized()) {
        console.log(item.id, item.name, roadmap.score(item).toFixed(2));
    }

    console.log("\nOUTCOME METRICS");
    console.table(roadmap.outcomeMetrics());

    console.log("\nCAPACITY");
    console.table(roadmap.capacityAnalysis());

    // Execute an independent initiative using an asynchronous work handler.
    const results = await roadmap.executeReadyInitiatives(
        async item => {
            await Promise.resolve();
            return `${item.name} completed successfully`;
        }
    );

    console.log("\nEXECUTION RESULTS");
    console.log(results);

    console.log("\nROADMAP SNAPSHOT");
    console.log(JSON.stringify(roadmap.snapshot(), null, 2));

    await roadmap.saveReport("product-roadmap-report.json");

    // Basic failure test.
    try {
        roadmap.addInitiative({
            id: "I4",
            name: "Invalid Initiative",
            themeId: "UNKNOWN",
            outcomeId: "O1",
            start: "2027-01-01",
            end: "2027-01-10",
            effort: 10,
            impact: 5,
            confidence: 0.8,
            alignment: 8,
            status: Status.PROPOSED
        });
    } catch (error) {
        console.log("\nEXPECTED VALIDATION ERROR:", error.message);
    }
}

main().catch(error => {
    console.error("Roadmap execution failed:", error.message);
    process.exitCode = 1;
});
