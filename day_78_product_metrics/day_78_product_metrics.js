"use strict";

/**
 * PRODUCT METRICS EVENT-DRIVEN ENGINE
 *
 * Models product performance using:
 * 1. North Star Metric
 * 2. Input Metrics
 * 3. Output Metrics
 * 4. Guardrail Metrics
 *
 * Features:
 * - Event-driven metric updates
 * - Asynchronous event processing
 * - Metric dependency evaluation
 * - Guardrail policy enforcement
 * - Experiment comparison
 * - Rolling observation windows
 * - Duplicate-event protection
 * - Structured reporting
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const crypto = require("node:crypto");

const Category = Object.freeze({
    NORTH_STAR: "north_star",
    INPUT: "input",
    OUTPUT: "output",
    GUARDRAIL: "guardrail"
});

const Direction = Object.freeze({
    HIGHER: "higher",
    LOWER: "lower",
    RANGE: "range"
});

class ProductMetricError extends Error {
    constructor(message) {
        super(message);
        this.name = "ProductMetricError";
    }
}

class ValidationError extends ProductMetricError {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class MetricDefinition {
    constructor({
        name,
        category,
        unit,
        direction,
        target = null,
        minimum = null,
        maximum = null,
        description = ""
    }) {
        this.name = name;
        this.category = category;
        this.unit = unit;
        this.direction = direction;
        this.target = target;
        this.minimum = minimum;
        this.maximum = maximum;
        this.description = description;

        this.validate();
        Object.freeze(this);
    }

    validate() {
        if (typeof this.name !== "string" || !this.name.trim()) {
            throw new ValidationError("Metric name is required.");
        }

        if (!Object.values(Category).includes(this.category)) {
            throw new ValidationError("Invalid metric category.");
        }

        if (!Object.values(Direction).includes(this.direction)) {
            throw new ValidationError("Invalid metric direction.");
        }

        for (const value of [
            this.target,
            this.minimum,
            this.maximum
        ]) {
            if (
                value !== null &&
                (!Number.isFinite(value) || value < 0)
            ) {
                throw new ValidationError(
                    "Metric thresholds must be finite and non-negative."
                );
            }
        }

        if (
            this.minimum !== null &&
            this.maximum !== null &&
            this.minimum > this.maximum
        ) {
            throw new ValidationError("Invalid metric range.");
        }
    }
}

class MetricCatalog {
    #definitions = new Map();

    register(definition) {
        const key = definition.name.toLowerCase();

        if (this.#definitions.has(key)) {
            throw new ValidationError(
                `Duplicate metric: ${definition.name}`
            );
        }

        this.#definitions.set(key, definition);
    }

    get(name) {
        const definition = this.#definitions.get(name.toLowerCase());

        if (!definition) {
            throw new ValidationError(`Unknown metric: ${name}`);
        }

        return definition;
    }

    all() {
        return [...this.#definitions.values()];
    }

    category(category) {
        return this.all().filter(
            metric => metric.category === category
        );
    }
}

class EventLedger {
    #events = new Map();

    append(event) {
        if (!event.eventId || !event.metricName) {
            throw new ValidationError(
                "Event ID and metric name are required."
            );
        }

        if (!Number.isFinite(event.value) || event.value < 0) {
            throw new ValidationError("Invalid metric value.");
        }

        if (!Number.isInteger(event.sampleSize) || event.sampleSize <= 0) {
            throw new ValidationError("Invalid sample size.");
        }

        if (!event.period || !event.timestamp) {
            throw new ValidationError(
                "Period and timestamp are required."
            );
        }

        const key = event.eventId;

        if (this.#events.has(key)) {
            return false;
        }

        this.#events.set(key, Object.freeze({ ...event }));
        return true;
    }

    getAll() {
        return [...this.#events.values()];
    }

    query(metricName, period) {
        return this.getAll().filter(
            event =>
                event.metricName.toLowerCase() ===
                    metricName.toLowerCase() &&
                event.period === period
        );
    }
}

class MetricAggregator {
    constructor(catalog, ledger) {
        this.catalog = catalog;
        this.ledger = ledger;
    }

    aggregate(metricName, period) {
        const definition = this.catalog.get(metricName);

        const events = this.ledger.query(
            metricName,
            period
        );

        if (events.length === 0) {
            return null;
        }

        // Weighted average prevents small event batches from
        // receiving the same influence as large event batches.
        const totalSamples = events.reduce(
            (sum, event) => sum + event.sampleSize,
            0
        );

        const weightedValue = events.reduce(
            (sum, event) =>
                sum + event.value * event.sampleSize,
            0
        ) / totalSamples;

        return {
            metricName: definition.name,
            category: definition.category,
            value: Number(weightedValue.toFixed(4)),
            sampleSize: totalSamples,
            eventCount: events.length,
            period
        };
    }
}

class MetricPolicy {
    evaluate(definition, observation) {
        if (!observation) {
            return {
                status: "missing",
                acceptable: false
            };
        }

        const value = observation.value;
        let acceptable = true;
        let status = "on_track";

        if (definition.direction === Direction.HIGHER) {
            if (definition.target !== null) {
                acceptable = value >= definition.target;
            }
        }

        if (definition.direction === Direction.LOWER) {
            if (definition.target !== null) {
                acceptable = value <= definition.target;
            }
        }

        if (definition.direction === Direction.RANGE) {
            acceptable =
                (definition.minimum === null ||
                    value >= definition.minimum) &&
                (definition.maximum === null ||
                    value <= definition.maximum);
        }

        if (!acceptable) {
            status = "outside_target";
        }

        if (
            definition.category === Category.GUARDRAIL &&
            !acceptable
        ) {
            status = "guardrail_breach";
        }

        return {
            status,
            acceptable,
            observed: value,
            target: definition.target
        };
    }
}

class ProductMetricsEngine extends EventEmitter {
    constructor(productName) {
        super();

        this.productName = productName;
        this.catalog = new MetricCatalog();
        this.ledger = new EventLedger();
        this.aggregator = new MetricAggregator(
            this.catalog,
            this.ledger
        );
        this.policy = new MetricPolicy();

        this.queue = Promise.resolve();
        this.processed = 0;
    }

    defineMetric(configuration) {
        const definition = new MetricDefinition(configuration);
        this.catalog.register(definition);
        return definition;
    }

    ingest(event) {
        // Serialize updates so concurrent producers cannot race
        // when updating the in-memory ledger.
        this.queue = this.queue.then(async () => {
            const definition = this.catalog.get(event.metricName);

            if (
                definition.minimum !== null &&
                event.value < definition.minimum
            ) {
                throw new ValidationError(
                    `${definition.name} below valid minimum.`
                );
            }

            if (
                definition.maximum !== null &&
                event.value > definition.maximum
            ) {
                throw new ValidationError(
                    `${definition.name} above valid maximum.`
                );
            }

            const inserted = this.ledger.append(event);

            if (!inserted) {
                this.emit("duplicate", event);
                return false;
            }

            this.processed++;

            this.emit("metric:ingested", {
                metricName: event.metricName,
                value: event.value,
                period: event.period
            });

            const aggregate = this.aggregator.aggregate(
                event.metricName,
                event.period
            );

            const result = this.policy.evaluate(
                definition,
                aggregate
            );

            if (definition.category === Category.GUARDRAIL) {
                if (!result.acceptable) {
                    this.emit("guardrail:breach", {
                        metricName: event.metricName,
                        result
                    });
                }
            }

            return true;
        });

        return this.queue;
    }

    async evaluatePeriod(period) {
        await this.queue;

        const report = [];

        for (const definition of this.catalog.all()) {
            const observation = this.aggregator.aggregate(
                definition.name,
                period
            );

            report.push({
                definition,
                observation,
                policy: this.policy.evaluate(
                    definition,
                    observation
                )
            });
        }

        return report;
    }

    async getNorthStar(period) {
        const definitions = this.catalog.category(
            Category.NORTH_STAR
        );

        if (definitions.length !== 1) {
            throw new ProductMetricError(
                "Exactly one North Star Metric is required."
            );
        }

        return this.aggregator.aggregate(
            definitions[0].name,
            period
        );
    }

    async comparePeriods(currentPeriod, previousPeriod) {
        await this.queue;

        return this.catalog.all().map(definition => {
            const current = this.aggregator.aggregate(
                definition.name,
                currentPeriod
            );

            const previous = this.aggregator.aggregate(
                definition.name,
                previousPeriod
            );

            let changePercent = null;

            if (
                current &&
                previous &&
                previous.value !== 0
            ) {
                changePercent = Number(
                    (
                        (current.value - previous.value) /
                        Math.abs(previous.value) *
                        100
                    ).toFixed(2)
                );
            }

            return {
                metricName: definition.name,
                category: definition.category,
                current: current?.value ?? null,
                previous: previous?.value ?? null,
                changePercent
            };
        });
    }

    async exportReport(period, outputPath) {
        const [metrics, northStar] = await Promise.all([
            this.evaluatePeriod(period),
            this.getNorthStar(period)
        ]);

        const report = {
            product: this.productName,
            generatedAt: new Date().toISOString(),
            period,
            northStar,
            metrics: metrics.map(item => ({
                metricName: item.definition.name,
                category: item.definition.category,
                observation: item.observation,
                policy: item.policy
            })),
            eventCount: this.processed
        };

        if (outputPath) {
            await fs.writeFile(
                outputPath,
                JSON.stringify(report, null, 2),
                { encoding: "utf8", flag: "w" }
            );
        }

        return report;
    }
}

class ExperimentAnalyzer {
    static compare({
        control,
        treatment,
        minimumSampleSize = 30
    }) {
        for (const group of [control, treatment]) {
            if (
                !Number.isFinite(group.value) ||
                group.value < 0 ||
                !Number.isInteger(group.sampleSize) ||
                group.sampleSize < minimumSampleSize
            ) {
                throw new ValidationError(
                    "Experiment group has insufficient or invalid data."
                );
            }
        }

        const absoluteLift = treatment.value - control.value;

        const relativeLift =
            control.value === 0
                ? null
                : Number(
                    (
                        absoluteLift /
                        Math.abs(control.value) *
                        100
                    ).toFixed(2)
                );

        return {
            control: control.value,
            treatment: treatment.value,
            absoluteLift,
            relativeLift,
            sampleSizes: {
                control: control.sampleSize,
                treatment: treatment.sampleSize
            },
            interpretation:
                absoluteLift > 0
                    ? "Treatment has a higher observed value."
                    : absoluteLift < 0
                        ? "Treatment has a lower observed value."
                        : "No observed difference."
        };
    }
}

async function createDemo() {
    const engine = new ProductMetricsEngine(
        "Digital Learning Platform"
    );

    engine.defineMetric({
        name: "Weekly Active Learners",
        category: Category.NORTH_STAR,
        unit: "users",
        direction: Direction.HIGHER,
        target: 12000
    });

    engine.defineMetric({
        name: "Activation Rate",
        category: Category.INPUT,
        unit: "%",
        direction: Direction.HIGHER,
        target: 65,
        minimum: 0,
        maximum: 100
    });

    engine.defineMetric({
        name: "Lesson Completion Rate",
        category: Category.INPUT,
        unit: "%",
        direction: Direction.HIGHER,
        target: 75,
        minimum: 0,
        maximum: 100
    });

    engine.defineMetric({
        name: "Subscription Revenue",
        category: Category.OUTPUT,
        unit: "INR",
        direction: Direction.HIGHER,
        target: 1500000
    });

    engine.defineMetric({
        name: "Retention Rate",
        category: Category.OUTPUT,
        unit: "%",
        direction: Direction.HIGHER,
        target: 85,
        minimum: 0,
        maximum: 100
    });

    engine.defineMetric({
        name: "Application Error Rate",
        category: Category.GUARDRAIL,
        unit: "%",
        direction: Direction.LOWER,
        target: 1,
        minimum: 0,
        maximum: 2
    });

    engine.defineMetric({
        name: "Page Load Time",
        category: Category.GUARDRAIL,
        unit: "seconds",
        direction: Direction.LOWER,
        target: 2,
        minimum: 0,
        maximum: 3
    });

    engine.on("guardrail:breach", event => {
        console.error(
            "GUARDRAIL ALERT:",
            event.metricName,
            event.result
        );
    });

    engine.on("duplicate", event => {
        console.warn("Duplicate event ignored:", event.eventId);
    });

    const previous = {
        "Weekly Active Learners": 10800,
        "Activation Rate": 62,
        "Lesson Completion Rate": 72,
        "Subscription Revenue": 1380000,
        "Retention Rate": 84,
        "Application Error Rate": 0.8,
        "Page Load Time": 1.8
    };

    const current = {
        "Weekly Active Learners": 12400,
        "Activation Rate": 68,
        "Lesson Completion Rate": 78,
        "Subscription Revenue": 1570000,
        "Retention Rate": 86,
        "Application Error Rate": 2.4,
        "Page Load Time": 2.2
    };

    for (const [period, values] of Object.entries({
        previous,
        current
    })) {
        for (const [metricName, value] of Object.entries(values)) {
            await engine.ingest({
                eventId: crypto.randomUUID(),
                metricName,
                period,
                value,
                sampleSize: 10000,
                timestamp: new Date().toISOString()
            });
        }
    }

    const duplicateEvent = {
        eventId: "fixed-event-001",
        metricName: "Activation Rate",
        period: "current",
        value: 68,
        sampleSize: 100,
        timestamp: new Date().toISOString()
    };

    await engine.ingest(duplicateEvent);
    await engine.ingest(duplicateEvent);

    const report = await engine.exportReport(
        "current",
        null
    );

    const comparison = await engine.comparePeriods(
        "current",
        "previous"
    );

    const experiment = ExperimentAnalyzer.compare({
        control: {
            value: 65,
            sampleSize: 500
        },
        treatment: {
            value: 70,
            sampleSize: 520
        }
    });

    console.log("\nPRODUCT METRICS REPORT");
    console.log(JSON.stringify(report, null, 2));

    console.log("\nPERIOD COMPARISON");
    console.table(comparison);

    console.log("\nEXPERIMENT ANALYSIS");
    console.log(JSON.stringify(experiment, null, 2));

    const northStar = await engine.getNorthStar("current");

    if (northStar.value !== 12400) {
        throw new Error("North Star validation failed.");
    }

    return engine;
}

createDemo().catch(error => {
    console.error("Product metrics processing failed:", error.message);
    process.exitCode = 1;
});
