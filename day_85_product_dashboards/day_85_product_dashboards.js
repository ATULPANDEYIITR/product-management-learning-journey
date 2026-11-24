"use strict";

/*
 * Product Dashboard Event and Policy Engine
 *
 * Node.js 18+
 * No external dependencies.
 *
 * Focus:
 * - Event-driven metric ingestion
 * - KPI hierarchy
 * - Rolling-window aggregation
 * - Dashboard configuration
 * - Alert policies and deduplication
 * - Subscription-based updates
 * - Authorization
 * - Async export
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const EventEmitter = require("node:events");

class DashboardError extends Error {}
class ValidationError extends DashboardError {}
class AuthorizationError extends DashboardError {}

const MetricCategory = Object.freeze({
    NORTH_STAR: "north_star",
    BUSINESS: "business",
    PRODUCT: "product",
    ENGAGEMENT: "engagement",
    RELIABILITY: "reliability"
});

const Severity = Object.freeze({
    INFO: "info",
    WARNING: "warning",
    CRITICAL: "critical"
});

const Aggregation = Object.freeze({
    SUM: "sum",
    AVG: "average",
    MIN: "minimum",
    MAX: "maximum",
    LAST: "last",
    DISTINCT: "distinct"
});

const RoleLevel = Object.freeze({
    viewer: 1,
    analyst: 2,
    admin: 3
});

function requireString(value, field) {
    if (typeof value !== "string" || !value.trim()) {
        throw new ValidationError(`${field} must be a non-empty string.`);
    }
}

function requireFiniteNumber(value, field) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new ValidationError(`${field} must be a finite number.`);
    }
}

function validateTimestamp(timestamp) {
    if (!(timestamp instanceof Date) ||
        Number.isNaN(timestamp.getTime())) {
        throw new ValidationError("Invalid timestamp.");
    }
}

class MetricDefinition {
    constructor({
        name,
        description,
        category,
        unit,
        aggregation,
        higherIsBetter,
        target = null,
        warningThreshold = null,
        criticalThreshold = null,
        type = "number"
    }) {
        requireString(name, "Metric name");
        requireString(description, "Metric description");
        requireString(unit, "Metric unit");

        if (!Object.values(MetricCategory).includes(category)) {
            throw new ValidationError("Invalid metric category.");
        }

        if (!Object.values(Aggregation).includes(aggregation)) {
            throw new ValidationError("Invalid aggregation.");
        }

        for (const [label, value] of Object.entries({
            target,
            warningThreshold,
            criticalThreshold
        })) {
            if (value !== null) {
                requireFiniteNumber(value, label);
            }
        }

        if (typeof higherIsBetter !== "boolean") {
            throw new ValidationError(
                "higherIsBetter must be boolean."
            );
        }

        if (type === "percentage" && unit !== "%") {
            throw new ValidationError(
                "Percentage metrics require % units."
            );
        }

        this.name = name;
        this.description = description;
        this.category = category;
        this.unit = unit;
        this.aggregation = aggregation;
        this.higherIsBetter = higherIsBetter;
        this.target = target;
        this.warningThreshold = warningThreshold;
        this.criticalThreshold = criticalThreshold;
        this.type = type;

        Object.freeze(this);
    }

    validateValue(value) {
        requireFiniteNumber(value, this.name);

        if (this.type === "percentage" &&
            (value < 0 || value > 100)) {
            throw new ValidationError(
                `${this.name} must be between 0 and 100.`
            );
        }

        if (this.type === "count" && value < 0) {
            throw new ValidationError(
                `${this.name} cannot be negative.`
            );
        }
    }
}

class MetricRegistry {
    #definitions = new Map();

    register(definition) {
        if (!(definition instanceof MetricDefinition)) {
            throw new ValidationError("Invalid metric definition.");
        }

        if (this.#definitions.has(definition.name)) {
            throw new ValidationError(
                `Duplicate metric: ${definition.name}`
            );
        }

        this.#definitions.set(definition.name, definition);
    }

    get(name) {
        const definition = this.#definitions.get(name);

        if (!definition) {
            throw new ValidationError(`Unknown metric: ${name}`);
        }

        return definition;
    }

    values() {
        return [...this.#definitions.values()];
    }
}

class MetricEvent {
    constructor({
        metricName,
        value,
        timestamp = new Date(),
        dimensions = {},
        entityId = null
    }) {
        requireString(metricName, "Metric name");
        requireFiniteNumber(value, "Metric value");
        validateTimestamp(timestamp);

        if (
            dimensions === null ||
            typeof dimensions !== "object" ||
            Array.isArray(dimensions)
        ) {
            throw new ValidationError("Invalid dimensions.");
        }

        for (const [key, dimensionValue] of Object.entries(dimensions)) {
            requireString(key, "Dimension key");
            if (
                typeof dimensionValue !== "string" ||
                !dimensionValue.trim()
            ) {
                throw new ValidationError("Invalid dimension value.");
            }
        }

        this.metricName = metricName;
        this.value = value;
        this.timestamp = new Date(timestamp);
        this.dimensions = Object.freeze({ ...dimensions });
        this.entityId = entityId;
        Object.freeze(this);
    }
}

class MetricStream extends EventEmitter {
    #registry;
    #events = [];
    #maximumEvents;

    constructor(registry, maximumEvents = 100000) {
        super();

        if (!Number.isInteger(maximumEvents) ||
            maximumEvents < 1) {
            throw new ValidationError("Invalid event capacity.");
        }

        this.#registry = registry;
        this.#maximumEvents = maximumEvents;
    }

    ingest(event) {
        if (!(event instanceof MetricEvent)) {
            throw new ValidationError("Invalid metric event.");
        }

        const definition = this.#registry.get(event.metricName);
        definition.validateValue(event.value);

        if (this.#events.length >= this.#maximumEvents) {
            this.#events.shift();
        }

        this.#events.push(event);

        this.emit("metric", event);

        return event;
    }

    query({
        metricName,
        start,
        end,
        dimensions = {}
    }) {
        this.#registry.get(metricName);
        validateTimestamp(start);
        validateTimestamp(end);

        if (start >= end) {
            throw new ValidationError("Invalid time range.");
        }

        return this.#events.filter(event => {
            if (event.metricName !== metricName) return false;

            const timestamp = event.timestamp.getTime();

            if (
                timestamp < start.getTime() ||
                timestamp >= end.getTime()
            ) {
                return false;
            }

            return Object.entries(dimensions).every(
                ([key, value]) => event.dimensions[key] === value
            );
        });
    }
}

class AggregationEngine {
    static calculate(events, aggregation) {
        if (!events.length) return null;

        const values = events.map(event => event.value);

        switch (aggregation) {
            case Aggregation.SUM:
                return values.reduce((sum, value) => sum + value, 0);

            case Aggregation.AVG:
                return values.reduce(
                    (sum, value) => sum + value, 0
                ) / values.length;

            case Aggregation.MIN:
                return Math.min(...values);

            case Aggregation.MAX:
                return Math.max(...values);

            case Aggregation.LAST:
                return events.reduce(
                    (latest, current) =>
                        current.timestamp > latest.timestamp
                            ? current
                            : latest
                ).value;

            case Aggregation.DISTINCT:
                return new Set(
                    events.map(event => event.entityId)
                        .filter(id => id !== null)
                ).size;

            default:
                throw new ValidationError(
                    "Unsupported aggregation."
                );
        }
    }
}

class AlertPolicy {
    constructor({
        metricName,
        warningThreshold,
        criticalThreshold,
        higherIsBetter
    }) {
        requireString(metricName, "Alert metric");

        requireFiniteNumber(
            warningThreshold,
            "Warning threshold"
        );

        requireFiniteNumber(
            criticalThreshold,
            "Critical threshold"
        );

        if (warningThreshold === criticalThreshold) {
            throw new ValidationError(
                "Alert thresholds must differ."
            );
        }

        this.metricName = metricName;
        this.warningThreshold = warningThreshold;
        this.criticalThreshold = criticalThreshold;
        this.higherIsBetter = higherIsBetter;

        Object.freeze(this);
    }

    evaluate(value) {
        requireFiniteNumber(value, "Alert value");

        if (this.higherIsBetter) {
            if (value < this.criticalThreshold) {
                return Severity.CRITICAL;
            }

            if (value < this.warningThreshold) {
                return Severity.WARNING;
            }
        } else {
            if (value > this.criticalThreshold) {
                return Severity.CRITICAL;
            }

            if (value > this.warningThreshold) {
                return Severity.WARNING;
            }
        }

        return null;
    }
}

class AlertManager extends EventEmitter {
    #active = new Map();
    #policies = new Map();

    register(policy) {
        if (!(policy instanceof AlertPolicy)) {
            throw new ValidationError("Invalid alert policy.");
        }

        this.#policies.set(policy.metricName, policy);
    }

    evaluate(metricName, value, timestamp = new Date()) {
        validateTimestamp(timestamp);

        const policy = this.#policies.get(metricName);

        if (!policy) return null;

        const severity = policy.evaluate(value);
        const fingerprint = `${metricName}:${severity}`;

        if (!severity) {
            for (const [key, alert] of this.#active) {
                if (alert.metricName === metricName) {
                    this.#active.delete(key);
                    this.emit("resolved", alert);
                }
            }

            return null;
        }

        if (this.#active.has(fingerprint)) {
            return null;
        }

        const alert = Object.freeze({
            id: crypto.randomUUID(),
            metricName,
            severity,
            value,
            timestamp: new Date(timestamp),
            fingerprint
        });

        this.#active.set(fingerprint, alert);
        this.emit("alert", alert);

        return alert;
    }

    acknowledge(fingerprint) {
        const alert = this.#active.get(fingerprint);

        if (!alert) return false;

        this.#active.delete(fingerprint);
        this.emit("acknowledged", alert);

        return true;
    }

    activeAlerts() {
        return [...this.#active.values()];
    }
}

class DashboardConfig {
    constructor({
        id,
        title,
        metrics,
        refreshIntervalMs = 60000,
        permissions = {}
    }) {
        requireString(id, "Dashboard ID");
        requireString(title, "Dashboard title");

        if (!Array.isArray(metrics) || metrics.length === 0) {
            throw new ValidationError(
                "A dashboard needs at least one metric."
            );
        }

        if (!Number.isInteger(refreshIntervalMs) ||
            refreshIntervalMs < 5000) {
            throw new ValidationError(
                "Refresh interval must be at least 5000ms."
            );
        }

        this.id = id;
        this.title = title;
        this.metrics = Object.freeze([...metrics]);
        this.refreshIntervalMs = refreshIntervalMs;
        this.permissions = Object.freeze({ ...permissions });

        Object.freeze(this);
    }
}

class AccessControl {
    static authorize(config, username, requiredRole = "viewer") {
        const actual = config.permissions[username];
        const requiredLevel = RoleLevel[requiredRole];
        const actualLevel = RoleLevel[actual];

        if (
            !requiredLevel ||
            !actualLevel ||
            actualLevel < requiredLevel
        ) {
            throw new AuthorizationError(
                `Insufficient access for ${username}.`
            );
        }
    }
}

class ProductDashboardService {
    constructor(registry, stream, alertManager) {
        this.registry = registry;
        this.stream = stream;
        this.alertManager = alertManager;
    }

    build(config, username, start, end) {
        AccessControl.authorize(config, username);

        validateTimestamp(start);
        validateTimestamp(end);

        if (start >= end) {
            throw new ValidationError("Invalid dashboard window.");
        }

        const duration = end.getTime() - start.getTime();
        const previousStart = new Date(
            start.getTime() - duration
        );

        const metrics = {};

        for (const metricName of config.metrics) {
            const definition = this.registry.get(metricName);

            const currentEvents = this.stream.query({
                metricName,
                start,
                end
            });

            const previousEvents = this.stream.query({
                metricName,
                start: previousStart,
                end: start
            });

            const current = AggregationEngine.calculate(
                currentEvents,
                definition.aggregation
            );

            const previous = AggregationEngine.calculate(
                previousEvents,
                definition.aggregation
            );

            const change = (
                current !== null &&
                previous !== null &&
                previous !== 0
            )
                ? ((current - previous) / Math.abs(previous)) * 100
                : null;

            const alert = current === null
                ? null
                : this.alertManager.evaluate(
                    metricName,
                    current,
                    end
                );

            metrics[metricName] = {
                value: current,
                unit: definition.unit,
                category: definition.category,
                target: definition.target,
                previousValue: previous,
                changePercentage: change,
                sampleCount: currentEvents.length,
                alert
            };
        }

        return Object.freeze({
            id: config.id,
            title: config.title,
            period: {
                start: start.toISOString(),
                end: end.toISOString()
            },
            metrics,
            activeAlerts: this.alertManager.activeAlerts(),
            generatedAt: new Date().toISOString()
        });
    }
}

class DashboardExporter {
    static async exportJSON(data, outputPath) {
        const destination = path.resolve(outputPath);
        const temporary = `${destination}.${crypto.randomUUID()}.tmp`;

        try {
            await fs.mkdir(path.dirname(destination), {
                recursive: true
            });

            await fs.writeFile(
                temporary,
                JSON.stringify(data, null, 2),
                {
                    encoding: "utf8",
                    flag: "wx",
                    mode: 0o600
                }
            );

            await fs.rename(temporary, destination);

            return destination;
        } catch (error) {
            await fs.rm(temporary, { force: true });
            throw error;
        }
    }
}

async function main() {
    const registry = new MetricRegistry();

    const definitions = [
        new MetricDefinition({
            name: "monthly_active_users",
            description: "Monthly active users",
            category: MetricCategory.NORTH_STAR,
            unit: "users",
            aggregation: Aggregation.LAST,
            higherIsBetter: true,
            target: 50000,
            warningThreshold: 40000,
            criticalThreshold: 30000,
            type: "count"
        }),

        new MetricDefinition({
            name: "conversion_rate",
            description: "Visitor-to-customer conversion rate",
            category: MetricCategory.BUSINESS,
            unit: "%",
            aggregation: Aggregation.AVG,
            higherIsBetter: true,
            target: 5,
            type: "percentage"
        }),

        new MetricDefinition({
            name: "daily_revenue",
            description: "Recognized daily revenue",
            category: MetricCategory.BUSINESS,
            unit: "INR",
            aggregation: Aggregation.SUM,
            higherIsBetter: true,
            target: 500000
        }),

        new MetricDefinition({
            name: "crash_rate",
            description: "Sessions ending in application crashes",
            category: MetricCategory.RELIABILITY,
            unit: "%",
            aggregation: Aggregation.AVG,
            higherIsBetter: false,
            target: 0.5,
            warningThreshold: 1,
            criticalThreshold: 2,
            type: "percentage"
        })
    ];

    definitions.forEach(definition => registry.register(definition));

    const stream = new MetricStream(registry);
    const alerts = new AlertManager();

    alerts.register(new AlertPolicy({
        metricName: "monthly_active_users",
        warningThreshold: 40000,
        criticalThreshold: 30000,
        higherIsBetter: true
    }));

    alerts.register(new AlertPolicy({
        metricName: "crash_rate",
        warningThreshold: 1,
        criticalThreshold: 2,
        higherIsBetter: false
    }));

    alerts.on("alert", alert => {
        console.log(
            `[ALERT] ${alert.severity}: ${alert.metricName}`
        );
    });

    stream.on("metric", event => {
        console.log(
            `[INGEST] ${event.metricName} = ${event.value}`
        );
    });

    const now = new Date();
    const hour = 60 * 60 * 1000;

    const sample = [
        ["monthly_active_users", 35000, 2],
        ["monthly_active_users", 38000, 1],
        ["conversion_rate", 4.2, 2],
        ["conversion_rate", 3.2, 1],
        ["daily_revenue", 420000, 2],
        ["daily_revenue", 390000, 1],
        ["crash_rate", 0.7, 2],
        ["crash_rate", 2.4, 1]
    ];

    for (const [metricName, value, hoursAgo] of sample) {
        stream.ingest(new MetricEvent({
            metricName,
            value,
            timestamp: new Date(now.getTime() - hoursAgo * hour),
            dimensions: {
                platform: "all",
                region: "india"
            }
        }));
    }

    const config = new DashboardConfig({
        id: "product-executive-dashboard",
        title: "Product Performance Dashboard",
        metrics: definitions.map(item => item.name),
        refreshIntervalMs: 60000,
        permissions: {
            executive: "viewer",
            analyst: "analyst",
            administrator: "admin"
        }
    });

    const service = new ProductDashboardService(
        registry,
        stream,
        alerts
    );

    const dashboard = service.build(
        config,
        "administrator",
        new Date(now.getTime() - 2 * hour),
        new Date(now.getTime() + 1)
    );

    console.log("\nDASHBOARD RESULT");
    console.log(JSON.stringify(dashboard, null, 2));

    const destination = await DashboardExporter.exportJSON(
        dashboard,
        "output/product-dashboard.json"
    );

    console.log(`Exported to ${destination}`);

    // A recovery event clears an existing crash-rate alert.
    const recovery = new MetricEvent({
        metricName: "crash_rate",
        value: 0.4,
        timestamp: new Date(now.getTime() + 1000)
    });

    stream.ingest(recovery);

    console.log(
        "Active alerts:",
        alerts.activeAlerts().length
    );

    try {
        AccessControl.authorize(config, "unknown", "viewer");
    } catch (error) {
        console.log("Authorization test:", error.message);
    }

    try {
        registry.get("unknown_metric");
    } catch (error) {
        console.log("Validation test:", error.message);
    }
}

main().catch(error => {
    console.error("Dashboard execution failed:", error.message);
    process.exitCode = 1;
});
