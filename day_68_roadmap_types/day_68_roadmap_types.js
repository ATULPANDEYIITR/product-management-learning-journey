"use strict";

/*
 * ROADMAP MANAGEMENT ENGINE
 *
 * JavaScript-specific implementation using:
 * - EventEmitter for roadmap lifecycle events.
 * - Map for indexed roadmap entities.
 * - Set for dependency and tag management.
 * - Async metric evaluation.
 * - Immutable snapshots.
 * - Optimistic version checks.
 * - Now-Next-Later planning.
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");

const RoadmapType = Object.freeze({
    FEATURE: "feature",
    OUTCOME: "outcome",
    THEME: "theme",
    HORIZON: "now_next_later"
});

const Status = Object.freeze({
    PROPOSED: "proposed",
    PLANNED: "planned",
    IN_PROGRESS: "in_progress",
    BLOCKED: "blocked",
    COMPLETED: "completed",
    CANCELLED: "cancelled"
});

const Horizon = Object.freeze({
    NOW: "now",
    NEXT: "next",
    LATER: "later"
});

const Priority = Object.freeze({
    CRITICAL: 1,
    HIGH: 2,
    MEDIUM: 3,
    LOW: 4
});

class RoadmapError extends Error {}

class ValidationError extends RoadmapError {}

class DependencyError extends RoadmapError {}

class VersionConflictError extends RoadmapError {}

function createId() {
    return crypto.randomUUID();
}

function requireText(value, field) {
    if (typeof value !== "string" || !value.trim()) {
        throw new ValidationError(`${field} is required.`);
    }
}

function validateMetric(metric) {
    if (!metric || typeof metric !== "object") {
        throw new ValidationError("Outcome metric is required.");
    }

    requireText(metric.name, "Metric name");

    for (const key of ["baseline", "target", "current"]) {
        if (!Number.isFinite(metric[key]) || metric[key] < 0) {
            throw new ValidationError(
                `Metric ${key} must be a non-negative number.`
            );
        }
    }
}

class RoadmapItem {
    constructor(data) {
        requireText(data.title, "Title");
        requireText(data.owner, "Owner");

        if (!Object.values(RoadmapType).includes(data.type)) {
            throw new ValidationError("Invalid roadmap type.");
        }

        if (
            !Object.values(Status).includes(
                data.status || Status.PROPOSED
            )
        ) {
            throw new ValidationError("Invalid status.");
        }

        this.id = data.id || createId();
        this.title = data.title.trim();
        this.description = data.description || "";
        this.owner = data.owner.trim();
        this.type = data.type;
        this.status = data.status || Status.PROPOSED;
        this.priority = data.priority || Priority.MEDIUM;
        this.horizon = data.horizon || null;
        this.themeId = data.themeId || null;
        this.metric = data.metric
            ? { ...data.metric }
            : null;

        this.dependencies = new Set(data.dependencies || []);
        this.tags = new Set(data.tags || []);

        this.progress = data.progress ?? 0;
        this.confidence = data.confidence ?? 0.8;

        this.version = 1;

        if (
            !Number.isFinite(this.progress) ||
            this.progress < 0 ||
            this.progress > 100
        ) {
            throw new ValidationError("Invalid progress.");
        }

        if (
            !Number.isFinite(this.confidence) ||
            this.confidence < 0 ||
            this.confidence > 1
        ) {
            throw new ValidationError("Invalid confidence.");
        }

        if (
            !Object.values(Priority).includes(this.priority)
        ) {
            throw new ValidationError("Invalid priority.");
        }

        if (
            this.type === RoadmapType.HORIZON &&
            !Object.values(Horizon).includes(this.horizon)
        ) {
            throw new ValidationError(
                "A valid planning horizon is required."
            );
        }

        if (this.type === RoadmapType.OUTCOME) {
            validateMetric(this.metric);
        }
    }

    snapshot() {
        return Object.freeze({
            ...this,
            dependencies: Object.freeze(
                [...this.dependencies]
            ),
            tags: Object.freeze([...this.tags]),
            metric: this.metric
                ? Object.freeze({ ...this.metric })
                : null
        });
    }
}

class RoadmapEngine extends EventEmitter {
    constructor(name, type) {
        super();

        requireText(name, "Roadmap name");

        if (!Object.values(RoadmapType).includes(type)) {
            throw new ValidationError("Invalid roadmap type.");
        }

        this.name = name;
        this.type = type;

        this.items = new Map();
        this.themes = new Map();

        this.revision = 0;
    }

    addTheme(theme) {
        requireText(theme.name, "Theme name");
        requireText(theme.objective, "Strategic objective");

        const id = theme.id || createId();

        if (this.themes.has(id)) {
            throw new ValidationError("Duplicate theme.");
        }

        this.themes.set(id, Object.freeze({
            id,
            name: theme.name,
            objective: theme.objective,
            owner: theme.owner || ""
        }));

        this.revision++;
        this.emit("theme:created", { id });
        return id;
    }

    addItem(data) {
        const item = new RoadmapItem(data);

        if (item.type !== this.type) {
            throw new ValidationError(
                "Item type differs from roadmap type."
            );
        }

        if (this.items.has(item.id)) {
            throw new ValidationError("Duplicate item.");
        }

        if (item.dependencies.has(item.id)) {
            throw new DependencyError(
                "Self-dependency is prohibited."
            );
        }

        if (item.themeId && !this.themes.has(item.themeId)) {
            throw new ValidationError("Unknown theme.");
        }

        for (const dependency of item.dependencies) {
            if (!this.items.has(dependency)) {
                throw new DependencyError(
                    `Unknown dependency: ${dependency}`
                );
            }
        }

        this.items.set(item.id, item);

        try {
            this.validateGraph();
        } catch (error) {
            this.items.delete(item.id);
            throw error;
        }

        this.revision++;

        this.emit("item:created", item.snapshot());

        return item.id;
    }

    validateGraph() {
        const state = new Map();

        const visit = (id) => {
            if (state.get(id) === 1) {
                throw new DependencyError(
                    "Circular dependency detected."
                );
            }

            if (state.get(id) === 2) {
                return;
            }

            state.set(id, 1);

            const item = this.items.get(id);

            for (const dependency of item.dependencies) {
                if (!this.items.has(dependency)) {
                    throw new DependencyError(
                        `Missing dependency: ${dependency}`
                    );
                }

                visit(dependency);
            }

            state.set(id, 2);
        };

        for (const id of this.items.keys()) {
            visit(id);
        }
    }

    getItem(id) {
        const item = this.items.get(id);

        if (!item) {
            throw new ValidationError("Item does not exist.");
        }

        return item;
    }

    updateStatus(id, nextStatus, expectedVersion) {
        const item = this.getItem(id);

        if (
            expectedVersion !== undefined &&
            item.version !== expectedVersion
        ) {
            throw new VersionConflictError(
                "Item changed since it was read."
            );
        }

        if (!Object.values(Status).includes(nextStatus)) {
            throw new ValidationError("Invalid target status.");
        }

        if (
            item.status === Status.COMPLETED ||
            item.status === Status.CANCELLED
        ) {
            throw new ValidationError(
                "Terminal item cannot be modified."
            );
        }

        if (nextStatus === Status.IN_PROGRESS) {
            for (const dependency of item.dependencies) {
                if (
                    this.getItem(dependency).status !==
                    Status.COMPLETED
                ) {
                    throw new DependencyError(
                        "Unfinished dependencies prevent execution."
                    );
                }
            }
        }

        const previousStatus = item.status;

        item.status = nextStatus;

        if (nextStatus === Status.COMPLETED) {
            item.progress = 100;
        }

        item.version++;
        this.revision++;

        this.emit("item:status-changed", {
            id,
            previousStatus,
            nextStatus,
            version: item.version
        });

        return item.snapshot();
    }

    updateMetric(id, current, expectedVersion) {
        const item = this.getItem(id);

        if (!item.metric) {
            throw new ValidationError(
                "Item does not contain an outcome metric."
            );
        }

        if (
            expectedVersion !== undefined &&
            item.version !== expectedVersion
        ) {
            throw new VersionConflictError(
                "Stale metric update."
            );
        }

        if (!Number.isFinite(current) || current < 0) {
            throw new ValidationError("Invalid metric value.");
        }

        item.metric.current = current;
        item.version++;
        this.revision++;

        this.emit("metric:updated", {
            id,
            current,
            progress: this.metricProgress(item.metric)
        });
    }

    metricProgress(metric) {
        const difference = metric.target - metric.baseline;

        if (difference === 0) {
            return metric.current === metric.target ? 100 : 0;
        }

        return Math.max(
            0,
            Math.min(
                100,
                ((metric.current - metric.baseline) /
                    difference) * 100
            )
        );
    }

    async evaluateOutcomes(evaluator) {
        if (typeof evaluator !== "function") {
            throw new ValidationError(
                "Evaluator must be a function."
            );
        }

        const outcomes = [...this.items.values()].filter(
            item => item.metric
        );

        // Independent metric evaluations can execute concurrently.
        return Promise.all(
            outcomes.map(async item => {
                const result = await evaluator({
                    item: item.snapshot(),
                    metric: { ...item.metric }
                });

                return {
                    id: item.id,
                    title: item.title,
                    evaluation: result,
                    progress: this.metricProgress(item.metric)
                };
            })
        );
    }

    moveHorizon(id, nextHorizon) {
        const item = this.getItem(id);

        if (item.type !== RoadmapType.HORIZON) {
            throw new ValidationError(
                "Only horizon roadmap items can be moved."
            );
        }

        if (!Object.values(Horizon).includes(nextHorizon)) {
            throw new ValidationError("Invalid horizon.");
        }

        const previous = item.horizon;
        item.horizon = nextHorizon;
        item.version++;
        this.revision++;

        this.emit("item:horizon-changed", {
            id,
            previous,
            next: nextHorizon
        });
    }

    prioritizedItems() {
        return [...this.items.values()]
            .sort((a, b) =>
                a.priority - b.priority ||
                b.confidence - a.confidence
            )
            .map(item => item.snapshot());
    }

    report() {
        const counts = Object.fromEntries(
            Object.values(Status).map(
                status => [status, 0]
            )
        );

        for (const item of this.items.values()) {
            counts[item.status]++;
        }

        const total = this.items.size;

        return Object.freeze({
            name: this.name,
            type: this.type,
            revision: this.revision,
            total,
            completed: counts[Status.COMPLETED],
            completionPercentage: total
                ? Number(
                    (
                        counts[Status.COMPLETED] /
                        total *
                        100
                    ).toFixed(2)
                )
                : 0,
            counts
        });
    }

    horizonReport() {
        const report = {
            now: [],
            next: [],
            later: []
        };

        for (const item of this.items.values()) {
            if (item.horizon) {
                report[item.horizon].push(item.title);
            }
        }

        return report;
    }

    async saveJSON(filePath) {
        const data = {
            name: this.name,
            type: this.type,
            revision: this.revision,
            themes: [...this.themes.values()],
            items: [...this.items.values()].map(item => ({
                ...item.snapshot()
            }))
        };

        const directory = path.dirname(filePath);

        await fs.mkdir(directory, { recursive: true });

        const temporary = `${filePath}.${process.pid}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(data, null, 2),
                { encoding: "utf8", flag: "wx" }
            );

            await fs.rename(temporary, filePath);
        } catch (error) {
            await fs.rm(temporary, { force: true });
            throw error;
        }
    }
}

async function main() {
    const feature = new RoadmapEngine(
        "Customer Platform",
        RoadmapType.FEATURE
    );

    feature.on("item:created", item => {
        console.log("Created:", item.title);
    });

    feature.on("item:status-changed", event => {
        console.log(
            `Status: ${event.previousStatus} -> ${event.nextStatus}`
        );
    });

    const securityId = feature.addItem({
        title: "Multi-factor authentication",
        owner: "Security",
        type: RoadmapType.FEATURE,
        priority: Priority.CRITICAL,
        status: Status.PLANNED
    });

    const analyticsId = feature.addItem({
        title: "Usage analytics",
        owner: "Product",
        type: RoadmapType.FEATURE,
        dependencies: [securityId],
        priority: Priority.HIGH
    });

    feature.updateStatus(
        securityId,
        Status.IN_PROGRESS
    );

    feature.updateStatus(
        securityId,
        Status.COMPLETED
    );

    feature.updateStatus(
        analyticsId,
        Status.IN_PROGRESS
    );

    console.log("\nFeature report:");
    console.log(feature.report());

    const outcomes = new RoadmapEngine(
        "Customer Experience",
        RoadmapType.OUTCOME
    );

    outcomes.addItem({
        title: "Reduce onboarding time",
        owner: "Operations",
        type: RoadmapType.OUTCOME,
        metric: {
            name: "Onboarding duration",
            baseline: 10,
            target: 4,
            current: 6,
            unit: "days"
        }
    });

    const evaluation = await outcomes.evaluateOutcomes(
        async ({ metric }) => ({
            achieved: metric.current <= metric.target,
            remaining: Math.abs(
                metric.current - metric.target
            )
        })
    );

    console.log("\nOutcome evaluation:");
    console.log(evaluation);

    const horizons = new RoadmapEngine(
        "Investment Horizons",
        RoadmapType.HORIZON
    );

    const nowId = horizons.addItem({
        title: "Resolve payment errors",
        owner: "Payments",
        type: RoadmapType.HORIZON,
        horizon: Horizon.NOW,
        priority: Priority.CRITICAL
    });

    horizons.addItem({
        title: "Improve reporting",
        owner: "Analytics",
        type: RoadmapType.HORIZON,
        horizon: Horizon.NEXT
    });

    horizons.addItem({
        title: "Predictive planning",
        owner: "Strategy",
        type: RoadmapType.HORIZON,
        horizon: Horizon.LATER
    });

    horizons.moveHorizon(nowId, Horizon.NEXT);

    console.log("\nHorizon report:");
    console.log(horizons.horizonReport());

    await feature.saveJSON(
        "roadmaps/feature-roadmap.json"
    );

    // Invalid operations are rejected without corrupting state.
    try {
        horizons.addItem({
            title: "Invalid item",
            owner: "Product",
            type: RoadmapType.HORIZON,
            horizon: "tomorrow"
        });
    } catch (error) {
        console.log("\nExpected validation failure:", error.message);
    }

    console.log("\nRoadmap engine execution completed.");
}

main().catch(error => {
    console.error("Roadmap engine failure:", error.message);
    process.exitCode = 1;
});
