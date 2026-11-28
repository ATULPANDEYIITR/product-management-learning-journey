"use strict";

/**
 * Experiment Metrics Engine
 *
 * Node.js 18+
 *
 * Event-driven experiment evaluation:
 * - Metric registration
 * - Primary, secondary and guardrail classification
 * - Stable traffic assignment
 * - Sample-size estimation
 * - Conversion significance testing
 * - Revenue and latency analysis
 * - Guardrail policy enforcement
 * - Immutable experiment decisions
 */

const crypto = require("node:crypto");
const { EventEmitter } = require("node:events");

const MetricType = Object.freeze({
    PRIMARY: "primary",
    SECONDARY: "secondary",
    GUARDRAIL: "guardrail"
});

const ExperimentState = Object.freeze({
    DRAFT: "draft",
    RUNNING: "running",
    COMPLETED: "completed",
    INVALID: "invalid"
});

const Decision = Object.freeze({
    SHIP: "ship",
    DO_NOT_SHIP: "do_not_ship",
    INCONCLUSIVE: "inconclusive"
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class Experiment {
    constructor({
        id,
        name,
        baselineConversion,
        relativeMDE,
        alpha = 0.05,
        power = 0.80,
        allocation = 1
    }) {
        this.id = id;
        this.name = name;
        this.baselineConversion = baselineConversion;
        this.relativeMDE = relativeMDE;
        this.alpha = alpha;
        this.power = power;
        this.allocation = allocation;
        this.state = ExperimentState.DRAFT;
        this.createdAt = new Date().toISOString();

        this.validate();
    }

    validate() {
        if (!this.id || !this.name) {
            throw new ValidationError(
                "Experiment ID and name are required"
            );
        }

        if (
            !(this.baselineConversion > 0 &&
              this.baselineConversion < 1)
        ) {
            throw new ValidationError(
                "Baseline conversion must be between 0 and 1"
            );
        }

        if (!(this.relativeMDE > 0 && this.relativeMDE < 1)) {
            throw new ValidationError("Invalid relative MDE");
        }

        if (!(this.alpha > 0 && this.alpha < 1)) {
            throw new ValidationError("Invalid significance level");
        }

        if (!(this.power > 0 && this.power < 1)) {
            throw new ValidationError("Invalid statistical power");
        }

        if (!(this.allocation > 0 && this.allocation <= 1)) {
            throw new ValidationError("Invalid traffic allocation");
        }
    }

    transition(next) {
        const allowed = {
            draft: ["running", "invalid"],
            running: ["completed", "invalid"],
            completed: [],
            invalid: []
        };

        if (!allowed[this.state].includes(next)) {
            throw new Error(
                `Invalid state transition: ${this.state} -> ${next}`
            );
        }

        this.state = next;
    }
}

class MetricRegistry {
    #metrics = new Map();

    register(metric) {
        if (!metric.name || !Object.values(MetricType).includes(metric.type)) {
            throw new ValidationError("Invalid metric definition");
        }

        if (this.#metrics.has(metric.name)) {
            throw new ValidationError(
                `Metric already registered: ${metric.name}`
            );
        }

        this.#metrics.set(
            metric.name,
            Object.freeze({ ...metric })
        );
    }

    get(name) {
        const metric = this.#metrics.get(name);

        if (!metric) {
            throw new ValidationError(`Unknown metric: ${name}`);
        }

        return metric;
    }

    byType(type) {
        return [...this.#metrics.values()].filter(
            metric => metric.type === type
        );
    }
}

class TrafficAllocator {
    constructor(experimentId) {
        this.experimentId = experimentId;
    }

    assign(userId) {
        if (typeof userId !== "string" || !userId.trim()) {
            throw new ValidationError("Invalid user ID");
        }

        const digest = crypto
            .createHash("sha256")
            .update(`${this.experimentId}:${userId}`)
            .digest();

        return digest.readUInt32BE(0) % 2 === 0
            ? "control"
            : "treatment";
    }
}

class SampleSizeService {
    static inverseNormal(p) {
        const a = [
            -39.6968302866538, 220.946098424521,
            -275.928510446969, 138.357751867269,
            -30.6647980661472, 2.50662827745924
        ];

        const b = [
            -54.4760987982241, 161.585836858041,
            -155.698979859887, 66.8013118877197,
            -13.2806815528857
        ];

        const c = [
            -0.00778489400243029, -0.322396458041136,
            -2.40075827716184, -2.54973253934373,
            4.37466414146497, 2.93816398269878
        ];

        const d = [
            0.00778469570904146, 0.32246712907004,
            2.445134137143, 3.75440866190742
        ];

        if (!(p > 0 && p < 1)) {
            throw new ValidationError("Invalid probability");
        }

        if (p < 0.02425) {
            const q = Math.sqrt(-2 * Math.log(p));

            return (((((c[0] * q + c[1]) * q + c[2]) * q +
                c[3]) * q + c[4]) * q + c[5]) /
                ((((d[0] * q + d[1]) * q + d[2]) * q +
                    d[3]) * q + 1);
        }

        if (p > 0.97575) {
            return -this.inverseNormal(1 - p);
        }

        const q = p - 0.5;
        const r = q * q;

        return (((((a[0] * r + a[1]) * r + a[2]) * r +
            a[3]) * r + a[4]) * r + a[5]) * q /
            (((((b[0] * r + b[1]) * r + b[2]) * r +
                b[3]) * r + b[4]) * r) + 1);
    }

    static calculate(experiment) {
        const p1 = experiment.baselineConversion;
        const p2 = p1 * (1 + experiment.relativeMDE);

        if (p2 >= 1) {
            throw new ValidationError(
                "Expected conversion rate must be below 1"
            );
        }

        const pooled = (p1 + p2) / 2;
        const delta = p2 - p1;

        const zAlpha = this.inverseNormal(
            1 - experiment.alpha / 2
        );

        const zPower = this.inverseNormal(experiment.power);

        const numerator = Math.pow(
            zAlpha * Math.sqrt(2 * pooled * (1 - pooled)) +
            zPower * Math.sqrt(
                p1 * (1 - p1) + p2 * (1 - p2)
            ),
            2
        );

        return Math.ceil(numerator / (delta * delta));
    }
}

class StatisticalTests {
    static normalCDF(z) {
        // Abramowitz-Stegun approximation.
        const sign = z < 0 ? -1 : 1;
        const x = Math.abs(z) / Math.sqrt(2);
        const t = 1 / (1 + 0.3275911 * x);

        const erf = 1 -
            (((((1.061405429 * t - 1.453152027) * t +
                1.421413741) * t - 0.284496736) * t +
                0.254829592) * t) * Math.exp(-x * x);

        return 0.5 * (1 + sign * erf);
    }

    static proportionTest(x1, n1, x2, n2) {
        if (
            n1 <= 0 || n2 <= 0 ||
            x1 < 0 || x2 < 0 ||
            x1 > n1 || x2 > n2
        ) {
            throw new ValidationError("Invalid proportion inputs");
        }

        const p1 = x1 / n1;
        const p2 = x2 / n2;
        const pooled = (x1 + x2) / (n1 + n2);

        const se = Math.sqrt(
            pooled * (1 - pooled) * (1 / n1 + 1 / n2)
        );

        if (se === 0) {
            return p1 === p2 ? 1 : 0;
        }

        const z = (p2 - p1) / se;

        return 2 * (1 - this.normalCDF(Math.abs(z)));
    }

    static mean(values) {
        if (!values.length) {
            throw new ValidationError("Empty metric observations");
        }

        return values.reduce((sum, value) => sum + value, 0) /
            values.length;
    }

    static percentile(values, percentile) {
        if (!values.length) {
            throw new ValidationError("Empty percentile dataset");
        }

        const sorted = [...values].sort((a, b) => a - b);
        const index = (sorted.length - 1) * percentile;

        const lower = Math.floor(index);
        const upper = Math.ceil(index);

        return sorted[lower] +
            (sorted[upper] - sorted[lower]) *
            (index - lower);
    }

    static welchNormalApproximation(a, b) {
        if (a.length < 2 || b.length < 2) {
            return null;
        }

        const meanA = this.mean(a);
        const meanB = this.mean(b);

        const variance = values => {
            const mean = this.mean(values);

            return values.reduce(
                (sum, value) => sum + Math.pow(value - mean, 2),
                0
            ) / (values.length - 1);
        };

        const se = Math.sqrt(
            variance(a) / a.length + variance(b) / b.length
        );

        if (se === 0) {
            return meanA === meanB ? 1 : 0;
        }

        const z = (meanB - meanA) / se;

        return 2 * (1 - this.normalCDF(Math.abs(z)));
    }
}

class ExperimentEventBus extends EventEmitter {
    publish(event, payload) {
        this.emit(event, Object.freeze({ ...payload }));
    }
}

class ExperimentEvaluator {
    constructor(policy = {}) {
        this.policy = {
            minimumConversionImprovement: 0,
            maximumRefundIncrease: 0.02,
            maximumP95LatencyIncrease: 40,
            ...policy
        };

        this.validatePolicy();
    }

    validatePolicy() {
        for (const value of Object.values(this.policy)) {
            if (!Number.isFinite(value)) {
                throw new ValidationError("Invalid evaluation policy");
            }
        }

        if (
            this.policy.maximumRefundIncrease < 0 ||
            this.policy.maximumP95LatencyIncrease < 0
        ) {
            throw new ValidationError(
                "Guardrail thresholds cannot be negative"
            );
        }
    }

    evaluate(data, requiredPerGroup, alpha = 0.05) {
        const {
            control,
            treatment
        } = data;

        if (
            control.users <= 0 ||
            treatment.users <= 0 ||
            control.conversions > control.users ||
            treatment.conversions > treatment.users
        ) {
            throw new ValidationError("Invalid experiment data");
        }

        const controlRate = control.conversions / control.users;
        const treatmentRate = treatment.conversions / treatment.users;

        const pValue = StatisticalTests.proportionTest(
            control.conversions,
            control.users,
            treatment.conversions,
            treatment.users
        );

        const significant = pValue < alpha;

        const refundRate = bucket =>
            bucket.conversions > 0
                ? bucket.refunds / bucket.conversions
                : 0;

        const revenueMean = bucket =>
            bucket.revenue.length
                ? StatisticalTests.mean(bucket.revenue)
                : 0;

        const controlRefund = refundRate(control);
        const treatmentRefund = refundRate(treatment);

        const controlP95 = StatisticalTests.percentile(
            control.latency, 0.95
        );

        const treatmentP95 = StatisticalTests.percentile(
            treatment.latency, 0.95
        );

        const sufficient =
            control.users >= requiredPerGroup &&
            treatment.users >= requiredPerGroup;

        const guardrails = {
            refundRate:
                treatmentRefund - controlRefund <=
                this.policy.maximumRefundIncrease,

            p95Latency:
                treatmentP95 - controlP95 <=
                this.policy.maximumP95LatencyIncrease
        };

        let decision;

        if (!sufficient) {
            decision = Decision.INCONCLUSIVE;
        } else if (!Object.values(guardrails).every(Boolean)) {
            decision = Decision.DO_NOT_SHIP;
        } else if (
            significant &&
            treatmentRate - controlRate >
            this.policy.minimumConversionImprovement
        ) {
            decision = Decision.SHIP;
        } else {
            decision = Decision.INCONCLUSIVE;
        }

        return Object.freeze({
            decision,
            primary: Object.freeze({
                name: "conversion_rate",
                control: controlRate,
                treatment: treatmentRate,
                absoluteChange: treatmentRate - controlRate,
                relativeChange: controlRate
                    ? (treatmentRate - controlRate) / controlRate * 100
                    : null,
                pValue,
                significant
            }),
            secondary: Object.freeze({
                revenuePerConversion: {
                    control: revenueMean(control),
                    treatment: revenueMean(treatment),
                    pValue: StatisticalTests.welchNormalApproximation(
                        control.revenue,
                        treatment.revenue
                    )
                }
            }),
            guardrails: Object.freeze(guardrails),
            sampleSufficient: sufficient
        });
    }
}

class ExperimentService {
    constructor() {
        this.experiments = new Map();
        this.events = new ExperimentEventBus();

        this.events.on("experiment.started", event => {
            console.log(`[EVENT] Started: ${event.id}`);
        });

        this.events.on("experiment.evaluated", event => {
            console.log(
                `[EVENT] Evaluation: ${event.id} => ${event.decision}`
            );
        });
    }

    create(config) {
        const experiment = new Experiment(config);

        if (this.experiments.has(experiment.id)) {
            throw new ValidationError("Duplicate experiment ID");
        }

        this.experiments.set(experiment.id, experiment);

        return experiment;
    }

    start(id) {
        const experiment = this.experiments.get(id);

        if (!experiment) {
            throw new ValidationError("Experiment not found");
        }

        experiment.transition(ExperimentState.RUNNING);

        this.events.publish("experiment.started", {
            id: experiment.id,
            name: experiment.name
        });
    }

    complete(id, report) {
        const experiment = this.experiments.get(id);

        if (!experiment) {
            throw new ValidationError("Experiment not found");
        }

        experiment.transition(ExperimentState.COMPLETED);

        this.events.publish("experiment.evaluated", {
            id,
            decision: report.decision
        });
    }
}

function generateData(experiment, totalUsers, seed = 42) {
    if (!Number.isInteger(totalUsers) || totalUsers < 2) {
        throw new ValidationError("Invalid total user count");
    }

    let state = seed >>> 0;

    function random() {
        state = (1664525 * state + 1013904223) >>> 0;
        return state / 4294967296;
    }

    function gaussian() {
        return Math.sqrt(-2 * Math.log(Math.max(random(), 1e-12))) *
            Math.cos(2 * Math.PI * random());
    }

    const buckets = {
        control: {
            users: 0,
            conversions: 0,
            refunds: 0,
            revenue: [],
            latency: []
        },
        treatment: {
            users: 0,
            conversions: 0,
            refunds: 0,
            revenue: [],
            latency: []
        }
    };

    const allocator = new TrafficAllocator(experiment.id);

    for (let i = 0; i < totalUsers; i++) {
        const bucketName = allocator.assign(`user-${i}`);
        const bucket = buckets[bucketName];

        bucket.users++;

        const probability = bucketName === "control"
            ? experiment.baselineConversion
            : experiment.baselineConversion *
                (1 + experiment.relativeMDE);

        const converted = random() < probability;

        if (converted) {
            bucket.conversions++;

            bucket.revenue.push(
                Math.exp(3.5 + gaussian() * 0.6)
            );

            if (random() < 0.035) {
                bucket.refunds++;
            }
        }

        const baseLatency = bucketName === "control" ? 180 : 190;

        bucket.latency.push(
            Math.max(1, baseLatency + gaussian() * 25)
        );
    }

    return buckets;
}

async function main() {
    const registry = new MetricRegistry();

    registry.register({
        name: "conversion_rate",
        type: MetricType.PRIMARY,
        unit: "percentage",
        higherIsBetter: true
    });

    registry.register({
        name: "revenue_per_conversion",
        type: MetricType.SECONDARY,
        unit: "currency",
        higherIsBetter: true
    });

    registry.register({
        name: "refund_rate",
        type: MetricType.GUARDRAIL,
        unit: "percentage",
        higherIsBetter: false
    });

    registry.register({
        name: "p95_latency",
        type: MetricType.GUARDRAIL,
        unit: "milliseconds",
        higherIsBetter: false
    });

    const service = new ExperimentService();

    const experiment = service.create({
        id: "EXP-001",
        name: "Checkout Redesign",
        baselineConversion: 0.10,
        relativeMDE: 0.10,
        alpha: 0.05,
        power: 0.80
    });

    const required = SampleSizeService.calculate(experiment);

    console.log("\nEXPERIMENT CONFIGURATION");
    console.log("------------------------");
    console.log("Name:", experiment.name);
    console.log("Required sample per group:", required);
    console.log("Primary metrics:", registry.byType(MetricType.PRIMARY).length);
    console.log("Secondary metrics:", registry.byType(MetricType.SECONDARY).length);
    console.log("Guardrails:", registry.byType(MetricType.GUARDRAIL).length);

    service.start(experiment.id);

    const observations = generateData(
        experiment,
        required * 2,
        42
    );

    const evaluator = new ExperimentEvaluator({
        minimumConversionImprovement: 0,
        maximumRefundIncrease: 0.02,
        maximumP95LatencyIncrease: 40
    });

    const report = evaluator.evaluate(
        observations,
        required,
        experiment.alpha
    );

    console.log("\nEVALUATION REPORT");
    console.log("-----------------");
    console.log("Decision:", report.decision);
    console.log("Primary:", report.primary);
    console.log("Secondary:", report.secondary);
    console.log("Guardrails:", report.guardrails);
    console.log("Sample sufficient:", report.sampleSufficient);

    service.complete(experiment.id, report);
}

main().catch(error => {
    console.error("Experiment execution failed:", error.message);
    process.exitCode = 1;
});
