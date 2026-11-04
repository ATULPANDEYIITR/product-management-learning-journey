"use strict";

/*
 * Product Goals: Event-driven product metrics and OKR evaluation.
 *
 * Features:
 * - Strategic goal hierarchy
 * - Outcome-based objectives
 * - KPI definitions and metric aggregation
 * - OKR progress calculation
 * - Event-driven measurement ingestion
 * - Metric freshness and quality validation
 * - Leading and lagging indicators
 * - Threshold-based risk detection
 * - Performance reporting
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class ProductError extends Error {}

class ValidationError extends ProductError {}

const GoalStatus = Object.freeze({
    DRAFT: "draft",
    ACTIVE: "active",
    AT_RISK: "at_risk",
    ACHIEVED: "achieved",
    MISSED: "missed",
    CANCELLED: "cancelled"
});

const MetricType = Object.freeze({
    KPI: "kpi",
    LEADING: "leading",
    LAGGING: "lagging",
    GUARDRAIL: "guardrail"
});

const Direction = Object.freeze({
    INCREASE: "increase",
    DECREASE: "decrease"
});

function validateNumber(value, field) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new ValidationError(`${field} must be a finite number.`);
    }
}

function validateDate(value, field) {
    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
        throw new ValidationError(`${field} is invalid.`);
    }

    return parsed;
}

class MetricDefinition {
    constructor({
        id,
        name,
        type,
        unit,
        baseline,
        target,
        direction,
        aggregation = "latest",
        freshnessHours = 168,
        lowerGuardrail = null,
        upperGuardrail = null
    }) {
        if (!id || !name || !unit) {
            throw new ValidationError("Metric identity fields are required.");
        }

        if (!Object.values(MetricType).includes(type)) {
            throw new ValidationError("Invalid metric type.");
        }

        if (!Object.values(Direction).includes(direction)) {
            throw new ValidationError("Invalid metric direction.");
        }

        validateNumber(baseline, "Baseline");
        validateNumber(target, "Target");

        if (baseline === target) {
            throw new ValidationError("Baseline and target must differ.");
        }

        if (
            direction === Direction.INCREASE && target <= baseline ||
            direction === Direction.DECREASE && target >= baseline
        ) {
            throw new ValidationError("Target conflicts with metric direction.");
        }

        if (!["latest", "average", "sum"].includes(aggregation)) {
            throw new ValidationError("Unsupported aggregation method.");
        }

        if (!Number.isInteger(freshnessHours) || freshnessHours <= 0) {
            throw new ValidationError("Freshness must be a positive integer.");
        }

        this.id = id;
        this.name = name;
        this.type = type;
        this.unit = unit;
        this.baseline = baseline;
        this.target = target;
        this.direction = direction;
        this.aggregation = aggregation;
        this.freshnessHours = freshnessHours;
        this.lowerGuardrail = lowerGuardrail;
        this.upperGuardrail = upperGuardrail;

        this.observations = [];
    }

    addObservation({ value, timestamp, source, quality = 1 }) {
        validateNumber(value, "Observation value");
        validateNumber(quality, "Observation quality");

        if (quality < 0 || quality > 1) {
            throw new ValidationError("Quality must be between 0 and 1.");
        }

        if (!source || !source.trim()) {
            throw new ValidationError("Observation source is required.");
        }

        const recordedAt = validateDate(timestamp, "Timestamp");

        if (
            this.observations.length > 0 &&
            recordedAt <= this.observations[this.observations.length - 1].timestamp
        ) {
            throw new ValidationError(
                "Observation timestamps must be strictly increasing."
            );
        }

        const observation = Object.freeze({
            value,
            timestamp: recordedAt,
            source,
            quality
        });

        this.observations.push(observation);

        return observation;
    }

    getCurrentValue() {
        if (this.observations.length === 0) {
            return this.baseline;
        }

        const values = this.observations.map(item => item.value);

        switch (this.aggregation) {
            case "latest":
                return values[values.length - 1];

            case "average":
                return values.reduce((a, b) => a + b, 0) / values.length;

            case "sum":
                return values.reduce((a, b) => a + b, 0);

            default:
                throw new ProductError("Unknown aggregation method.");
        }
    }

    getProgress() {
        const current = this.getCurrentValue();

        const progress =
            ((current - this.baseline) / (this.target - this.baseline)) * 100;

        return Math.max(0, Math.min(100, progress));
    }

    isFresh(now = new Date()) {
        if (this.observations.length === 0) {
            return false;
        }

        const latest = this.observations[this.observations.length - 1];

        const ageHours =
            (now.getTime() - latest.timestamp.getTime()) / 3600000;

        return ageHours >= 0 && ageHours <= this.freshnessHours;
    }

    isWithinGuardrails() {
        const current = this.getCurrentValue();

        if (
            this.lowerGuardrail !== null &&
            current < this.lowerGuardrail
        ) {
            return false;
        }

        if (
            this.upperGuardrail !== null &&
            current > this.upperGuardrail
        ) {
            return false;
        }

        return true;
    }

    getQuality() {
        if (this.observations.length === 0) return 0;

        return this.observations[
            this.observations.length - 1
        ].quality;
    }

    report() {
        return {
            id: this.id,
            name: this.name,
            type: this.type,
            unit: this.unit,
            baseline: this.baseline,
            current: this.getCurrentValue(),
            target: this.target,
            progress: Number(this.getProgress().toFixed(2)),
            quality: this.getQuality(),
            fresh: this.isFresh(),
            withinGuardrails: this.isWithinGuardrails()
        };
    }
}

class Objective {
    constructor({ id, title, owner, deadline, parentId = null }) {
        if (!id || !title || !owner) {
            throw new ValidationError("Objective identity is incomplete.");
        }

        this.id = id;
        this.title = title;
        this.owner = owner;
        this.deadline = validateDate(deadline, "Deadline");
        this.parentId = parentId;
        this.status = GoalStatus.DRAFT;
        this.results = new Map();
        this.history = [];
    }

    addKeyResult(metric, weight = 1) {
        if (this.status !== GoalStatus.DRAFT) {
            throw new ProductError("Key Results cannot change after activation.");
        }

        validateNumber(weight, "Weight");

        if (weight <= 0) {
            throw new ValidationError("Weight must be positive.");
        }

        if (this.results.has(metric.id)) {
            throw new ValidationError("Duplicate Key Result.");
        }

        this.results.set(metric.id, { metric, weight });
    }

    activate() {
        if (this.status !== GoalStatus.DRAFT) {
            throw new ProductError("Only draft objectives can be activated.");
        }

        if (this.results.size === 0) {
            throw new ValidationError("Objective requires at least one Key Result.");
        }

        this.status = GoalStatus.ACTIVE;
        this.history.push({
            event: "activated",
            timestamp: new Date().toISOString()
        });
    }

    getProgress() {
        if (this.results.size === 0) return 0;

        let weightedProgress = 0;
        let totalWeight = 0;

        for (const { metric, weight } of this.results.values()) {
            weightedProgress += metric.getProgress() * weight;
            totalWeight += weight;
        }

        return weightedProgress / totalWeight;
    }

    evaluate(now = new Date()) {
        if (
            this.status === GoalStatus.DRAFT ||
            this.status === GoalStatus.CANCELLED
        ) {
            return this.status;
        }

        const progress = this.getProgress();

        const metrics = [...this.results.values()].map(
            result => result.metric
        );

        if (metrics.some(metric => !metric.isWithinGuardrails())) {
            this.status = GoalStatus.AT_RISK;
        } else if (progress >= 100) {
            this.status = GoalStatus.ACHIEVED;
        } else if (now > this.deadline) {
            this.status = GoalStatus.MISSED;
        } else if (progress < 40) {
            this.status = GoalStatus.AT_RISK;
        } else {
            this.status = GoalStatus.ACTIVE;
        }

        return this.status;
    }

    report() {
        return {
            id: this.id,
            title: this.title,
            owner: this.owner,
            status: this.status,
            progress: Number(this.getProgress().toFixed(2)),
            deadline: this.deadline.toISOString(),
            keyResults: [...this.results.values()].map(
                item => ({
                    weight: item.weight,
                    ...item.metric.report()
                })
            )
        };
    }
}

class ProductGoalEngine extends EventEmitter {
    constructor() {
        super();
        this.objectives = new Map();
        this.metrics = new Map();

        this.on("measurement", event => {
            this.processMeasurement(event);
        });
    }

    registerMetric(metric) {
        if (!(metric instanceof MetricDefinition)) {
            throw new ValidationError("Invalid metric object.");
        }

        if (this.metrics.has(metric.id)) {
            throw new ValidationError("Metric already registered.");
        }

        this.metrics.set(metric.id, metric);
    }

    registerObjective(objective) {
        if (!(objective instanceof Objective)) {
            throw new ValidationError("Invalid objective.");
        }

        if (this.objectives.has(objective.id)) {
            throw new ValidationError("Objective already registered.");
        }

        if (
            objective.parentId &&
            !this.objectives.has(objective.parentId)
        ) {
            throw new ValidationError("Parent objective does not exist.");
        }

        this.objectives.set(objective.id, objective);
    }

    processMeasurement(event) {
        const metric = this.metrics.get(event.metricId);

        if (!metric) {
            throw new ValidationError("Unknown metric.");
        }

        const observation = metric.addObservation(event);

        this.emit("metric.updated", {
            metricId: metric.id,
            value: observation.value,
            progress: metric.getProgress()
        });
    }

    publishMeasurement(event) {
        // EventEmitter listeners execute synchronously.
        // Invalid measurements throw before the method returns.
        this.emit("measurement", event);
    }

    evaluateAll(now = new Date()) {
        const reports = [];

        for (const objective of this.objectives.values()) {
            objective.evaluate(now);
            reports.push(objective.report());
        }

        return reports;
    }

    portfolioReport() {
        const objectives = [...this.objectives.values()];
        const active = objectives.filter(
            objective => objective.status === GoalStatus.ACTIVE
        ).length;

        const achieved = objectives.filter(
            objective => objective.status === GoalStatus.ACHIEVED
        ).length;

        return {
            generatedAt: new Date().toISOString(),
            totalObjectives: objectives.length,
            activeObjectives: active,
            achievedObjectives: achieved,
            objectives: objectives.map(objective => objective.report())
        };
    }

    async exportReport(filename) {
        const data = JSON.stringify(this.portfolioReport(), null, 2);

        await fs.writeFile(filename, data, {
            encoding: "utf8",
            mode: 0o600
        });
    }
}

async function main() {
    const engine = new ProductGoalEngine();

    engine.on("metric.updated", event => {
        console.log(
            `Metric ${event.metricId}: ${event.value}, ` +
            `progress ${event.progress.toFixed(2)}%`
        );
    });

    const retention = new MetricDefinition({
        id: "KPI-RETENTION",
        name: "Monthly customer retention",
        type: MetricType.LAGGING,
        unit: "percent",
        baseline: 70,
        target: 85,
        direction: Direction.INCREASE,
        freshnessHours: 168
    });

    const activation = new MetricDefinition({
        id: "KPI-ACTIVATION",
        name: "New customer activation",
        type: MetricType.LEADING,
        unit: "percent",
        baseline: 40,
        target: 70,
        direction: Direction.INCREASE,
        freshnessHours: 72
    });

    const satisfaction = new MetricDefinition({
        id: "KPI-CSAT",
        name: "Customer satisfaction",
        type: MetricType.GUARDRAIL,
        unit: "score",
        baseline: 4.2,
        target: 4.7,
        direction: Direction.INCREASE,
        lowerGuardrail: 3.8
    });

    engine.registerMetric(retention);
    engine.registerMetric(activation);
    engine.registerMetric(satisfaction);

    const objective = new Objective({
        id: "OBJ-001",
        title: "Improve customer retention",
        owner: "Product Management",
        deadline: "2026-12-31T23:59:59Z"
    });

    objective.addKeyResult(retention, 3);
    objective.addKeyResult(activation, 1);

    engine.registerObjective(objective);
    objective.activate();

    engine.publishMeasurement({
        metricId: "KPI-RETENTION",
        value: 80,
        timestamp: "2026-11-01T10:00:00Z",
        source: "Subscription analytics",
        quality: 0.97
    });

    engine.publishMeasurement({
        metricId: "KPI-ACTIVATION",
        value: 60,
        timestamp: "2026-11-01T10:00:00Z",
        source: "Product analytics",
        quality: 0.94
    });

    engine.publishMeasurement({
        metricId: "KPI-CSAT",
        value: 4.3,
        timestamp: "2026-11-01T10:00:00Z",
        source: "Customer survey",
        quality: 0.91
    });

    engine.evaluateAll(new Date("2026-11-04T10:00:00Z"));

    console.log("\nPRODUCT GOAL PORTFOLIO");
    console.log(JSON.stringify(engine.portfolioReport(), null, 2));

    if (Math.abs(retention.getProgress() - 66.6666667) > 0.01) {
        throw new ProductError("Retention progress assertion failed.");
    }

    if (!retention.isWithinGuardrails()) {
        throw new ProductError("Unexpected retention guardrail failure.");
    }

    try {
        engine.publishMeasurement({
            metricId: "KPI-RETENTION",
            value: Infinity,
            timestamp: "2026-11-05T10:00:00Z",
            source: "Invalid source"
        });
    } catch (error) {
        console.log("\nInvalid event rejected:", error.message);
    }

    await engine.exportReport("product_goals_report.json");

    console.log("\nReport exported successfully.");
}

main().catch(error => {
    console.error("Product goal execution failed:", error.message);
    process.exitCode = 1;
});
