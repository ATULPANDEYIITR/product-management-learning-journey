"use strict";

/*
 * EXPERIMENTATION ENGINE
 *
 * Event-driven experiment execution and evaluation.
 *
 * Features:
 * - Experiment configuration
 * - Hypothesis and metric definitions
 * - Control and treatment variants
 * - Deterministic participant assignment
 * - Asynchronous experiment execution
 * - Event-driven lifecycle management
 * - Sample-size estimation
 * - Conversion and guardrail evaluation
 * - Statistical significance
 * - Experiment audit history
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 */

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");
const fs = require("node:fs/promises");


const ExperimentState = Object.freeze({
    DRAFT: "DRAFT",
    RUNNING: "RUNNING",
    COMPLETED: "COMPLETED",
    CANCELLED: "CANCELLED"
});

const Group = Object.freeze({
    CONTROL: "CONTROL",
    TREATMENT: "TREATMENT"
});

const Decision = Object.freeze({
    SUPPORTED: "REJECT_NULL_HYPOTHESIS",
    INCONCLUSIVE: "FAIL_TO_REJECT_NULL",
    INVALID: "INVALID_EXPERIMENT"
});


// ---------------------------------------------------------
// 1. VALIDATION
// ---------------------------------------------------------

function assertProbability(value, name) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value < 0 ||
        value > 1
    ) {
        throw new RangeError(`${name} must be between 0 and 1.`);
    }
}

function assertPositiveInteger(value, name) {
    if (!Number.isSafeInteger(value) || value < 1) {
        throw new RangeError(`${name} must be a positive integer.`);
    }
}


// ---------------------------------------------------------
// 2. DETERMINISTIC RANDOM NUMBER GENERATOR
// ---------------------------------------------------------

class RandomGenerator {
    constructor(seed = 42) {
        this.state = seed >>> 0;
    }

    next() {
        // Mulberry32 provides reproducible simulation values.
        let t = this.state += 0x6D2B79F5;

        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);

        this.state = this.state >>> 0;

        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    shuffle(items) {
        const result = [...items];

        for (let i = result.length - 1; i > 0; i--) {
            const j = Math.floor(this.next() * (i + 1));

            [result[i], result[j]] = [result[j], result[i]];
        }

        return result;
    }
}


// ---------------------------------------------------------
// 3. EXPERIMENT CONFIGURATION
// ---------------------------------------------------------

class ExperimentConfiguration {
    constructor({
        name,
        researchQuestion,
        nullHypothesis,
        alternativeHypothesis,
        metric,
        baselineRate,
        treatmentRate,
        alpha = 0.05,
        power = 0.80,
        minimumGroupSize = 30,
        expectedDirection = "increase",
        seed = 42
    }) {
        if (!name || !researchQuestion || !metric) {
            throw new Error("Experiment identification fields are required.");
        }

        if (!nullHypothesis || !alternativeHypothesis) {
            throw new Error("Both hypotheses are required.");
        }

        assertProbability(baselineRate, "baselineRate");
        assertProbability(treatmentRate, "treatmentRate");

        if (baselineRate === 0 || baselineRate === 1) {
            throw new RangeError("Baseline rate must be between 0 and 1.");
        }

        if (!(alpha > 0 && alpha < 1)) {
            throw new RangeError("Alpha must be between 0 and 1.");
        }

        if (!(power > 0 && power < 1)) {
            throw new RangeError("Power must be between 0 and 1.");
        }

        if (!["increase", "decrease", "different"].includes(
            expectedDirection
        )) {
            throw new Error("Unsupported hypothesis direction.");
        }

        assertPositiveInteger(minimumGroupSize, "minimumGroupSize");

        this.name = name;
        this.researchQuestion = researchQuestion;
        this.nullHypothesis = nullHypothesis;
        this.alternativeHypothesis = alternativeHypothesis;
        this.metric = metric;
        this.baselineRate = baselineRate;
        this.treatmentRate = treatmentRate;
        this.alpha = alpha;
        this.power = power;
        this.minimumGroupSize = minimumGroupSize;
        this.expectedDirection = expectedDirection;
        this.seed = seed;
        Object.freeze(this);
    }
}


// ---------------------------------------------------------
// 4. EXPERIMENT SERVICE
// ---------------------------------------------------------

class ExperimentService extends EventEmitter {
    constructor(configuration) {
        super();

        if (!(configuration instanceof ExperimentConfiguration)) {
            throw new TypeError("Invalid experiment configuration.");
        }

        this.configuration = configuration;
        this.id = randomUUID();
        this.state = ExperimentState.DRAFT;
        this.participants = new Map();
        this.auditLog = [];
        this.startedAt = null;
        this.completedAt = null;
    }

    recordEvent(event, details = {}) {
        const entry = Object.freeze({
            timestamp: new Date().toISOString(),
            event,
            details: Object.freeze({ ...details })
        });

        this.auditLog.push(entry);
        this.emit("audit", entry);
    }

    transition(expected, next) {
        if (this.state !== expected) {
            throw new Error(
                `Invalid transition: ${this.state} to ${next}`
            );
        }

        this.state = next;

        this.recordEvent("STATE_CHANGED", {
            previous: expected,
            current: next
        });
    }

    start() {
        this.transition(
            ExperimentState.DRAFT,
            ExperimentState.RUNNING
        );

        this.startedAt = new Date().toISOString();

        this.recordEvent("EXPERIMENT_STARTED");
    }

    cancel(reason) {
        if (
            this.state !== ExperimentState.RUNNING &&
            this.state !== ExperimentState.DRAFT
        ) {
            throw new Error("Experiment cannot be cancelled.");
        }

        const previous = this.state;

        this.state = ExperimentState.CANCELLED;

        this.recordEvent("EXPERIMENT_CANCELLED", {
            previous,
            reason: String(reason || "Unspecified")
        });
    }

    assignParticipants(total) {
        if (this.state !== ExperimentState.RUNNING) {
            throw new Error("Experiment is not running.");
        }

        assertPositiveInteger(total, "total");

        if (total < 2) {
            throw new RangeError("At least two participants are required.");
        }

        if (this.participants.size > 0) {
            throw new Error("Assignments already exist.");
        }

        const rng = new RandomGenerator(this.configuration.seed);

        const groups = Array.from(
            { length: total },
            (_, index) =>
                index % 2 === 0 ? Group.CONTROL : Group.TREATMENT
        );

        const randomized = rng.shuffle(groups);

        randomized.forEach((group, index) => {
            const participant = Object.freeze({
                id: `USER-${String(index + 1).padStart(6, "0")}`,
                group
            });

            this.participants.set(participant.id, participant);
        });

        this.recordEvent("PARTICIPANTS_ASSIGNED", {
            total,
            control: randomized.filter(
                g => g === Group.CONTROL
            ).length,
            treatment: randomized.filter(
                g => g === Group.TREATMENT
            ).length
        });
    }

    async execute() {
        if (this.state !== ExperimentState.RUNNING) {
            throw new Error("Experiment must be running.");
        }

        const rng = new RandomGenerator(this.configuration.seed + 100);

        const observations = new Map();

        let processed = 0;

        for (const participant of this.participants.values()) {
            const probability =
                participant.group === Group.CONTROL
                    ? this.configuration.baselineRate
                    : this.configuration.treatmentRate;

            const converted = rng.next() < probability;

            observations.set(participant.id, Object.freeze({
                participantId: participant.id,
                group: participant.group,
                converted,
                observedAt: new Date().toISOString()
            }));

            processed++;

            // Yield periodically so other event-loop tasks can execute.
            if (processed % 250 === 0) {
                await new Promise(resolve => setImmediate(resolve));

                this.emit("progress", {
                    processed,
                    total: this.participants.size
                });

                if (this.state !== ExperimentState.RUNNING) {
                    throw new Error("Experiment execution was interrupted.");
                }
            }
        }

        this.recordEvent("OBSERVATIONS_RECORDED", {
            total: observations.size
        });

        return observations;
    }

    // -----------------------------------------------------
    // 5. METRIC AGGREGATION
    // -----------------------------------------------------

    aggregate(observations) {
        const groups = new Map([
            [Group.CONTROL, { total: 0, conversions: 0 }],
            [Group.TREATMENT, { total: 0, conversions: 0 }]
        ]);

        for (const observation of observations.values()) {
            const aggregate = groups.get(observation.group);

            if (!aggregate) {
                throw new Error("Unknown experimental group.");
            }

            aggregate.total++;

            if (observation.converted) {
                aggregate.conversions++;
            }
        }

        for (const [name, group] of groups) {
            if (group.total === 0) {
                throw new Error(`No participants in ${name}.`);
            }

            group.rate = group.conversions / group.total;
        }

        return groups;
    }

    // -----------------------------------------------------
    // 6. STATISTICAL ANALYSIS
    // -----------------------------------------------------

    static normalCDF(x) {
        const absolute = Math.abs(x);
        const t = 1 / (1 + 0.2316419 * absolute);

        const density =
            Math.exp(-0.5 * absolute * absolute) /
            Math.sqrt(2 * Math.PI);

        const polynomial =
            t * (
                0.319381530 +
                t * (
                    -0.356563782 +
                    t * (
                        1.781477937 +
                        t * (
                            -1.821255978 +
                            1.330274429 * t
                        )
                    )
                )
            );

        const probability = 1 - density * polynomial;

        return x >= 0 ? probability : 1 - probability;
    }

    analyze(observations, { guardrailPassed = true } = {}) {
        if (this.state !== ExperimentState.RUNNING) {
            throw new Error("Experiment cannot be analyzed.");
        }

        const groups = this.aggregate(observations);

        const control = groups.get(Group.CONTROL);
        const treatment = groups.get(Group.TREATMENT);

        if (
            control.total < this.configuration.minimumGroupSize ||
            treatment.total < this.configuration.minimumGroupSize
        ) {
            throw new Error("Insufficient sample size.");
        }

        const pooled =
            (control.conversions + treatment.conversions) /
            (control.total + treatment.total);

        const standardError = Math.sqrt(
            pooled * (1 - pooled) *
            (1 / control.total + 1 / treatment.total)
        );

        if (standardError === 0) {
            throw new Error("Zero statistical variance.");
        }

        const effect = treatment.rate - control.rate;

        const z = effect / standardError;

        const pValue = 2 * (
            1 - ExperimentService.normalCDF(Math.abs(z))
        );

        const confidenceError = 1.95996398454 * Math.sqrt(
            control.rate * (1 - control.rate) / control.total +
            treatment.rate * (1 - treatment.rate) / treatment.total
        );

        const direction = this.configuration.expectedDirection;

        const favorable =
            direction === "increase"
                ? effect > 0
                : direction === "decrease"
                    ? effect < 0
                    : true;

        let decision;

        if (!guardrailPassed) {
            decision = Decision.INVALID;
        } else if (pValue < this.configuration.alpha && favorable) {
            decision = Decision.SUPPORTED;
        } else {
            decision = Decision.INCONCLUSIVE;
        }

        const result = Object.freeze({
            experimentId: this.id,
            control,
            treatment,
            absoluteEffect: effect,
            relativeEffect: control.rate > 0
                ? effect / control.rate
                : null,
            zScore: z,
            pValue,
            confidenceInterval: [
                effect - confidenceError,
                effect + confidenceError
            ],
            alpha: this.configuration.alpha,
            guardrailPassed,
            decision
        });

        this.completedAt = new Date().toISOString();

        this.transition(
            ExperimentState.RUNNING,
            ExperimentState.COMPLETED
        );

        this.recordEvent("ANALYSIS_COMPLETED", {
            decision,
            pValue
        });

        return result;
    }

    // -----------------------------------------------------
    // 7. SAMPLE SIZE ESTIMATION
    // -----------------------------------------------------

    estimateSampleSize() {
        const { baselineRate, treatmentRate, alpha, power } =
            this.configuration;

        const p1 = baselineRate;
        const p2 = treatmentRate;

        if (p1 === p2) {
            throw new Error("Effect size cannot be zero.");
        }

        const zAlpha = alpha === 0.05 ? 1.959964 : 2.575829;
        const zBeta = power >= 0.90 ? 1.281552 : 0.841621;

        const pooled = (p1 + p2) / 2;

        const numerator = Math.pow(
            zAlpha * Math.sqrt(2 * pooled * (1 - pooled)) +
            zBeta * Math.sqrt(
                p1 * (1 - p1) + p2 * (1 - p2)
            ),
            2
        );

        const size = Math.ceil(
            numerator / Math.pow(p2 - p1, 2)
        );

        return Math.max(
            size,
            this.configuration.minimumGroupSize
        );
    }

    // -----------------------------------------------------
    // 8. AUDIT EXPORT
    // -----------------------------------------------------

    async export(filename, result) {
        if (this.state !== ExperimentState.COMPLETED) {
            throw new Error("Only completed experiments can be exported.");
        }

        const document = {
            experiment: {
                id: this.id,
                name: this.configuration.name,
                researchQuestion: this.configuration.researchQuestion,
                nullHypothesis: this.configuration.nullHypothesis,
                alternativeHypothesis:
                    this.configuration.alternativeHypothesis,
                metric: this.configuration.metric
            },
            result,
            auditLog: this.auditLog
        };

        // Avoid accepting arbitrary output paths in production services.
        if (
            typeof filename !== "string" ||
            filename.includes("\0")
        ) {
            throw new Error("Invalid export filename.");
        }

        await fs.writeFile(
            filename,
            JSON.stringify(document, null, 2),
            { encoding: "utf8", flag: "wx" }
        );
    }
}


// ---------------------------------------------------------
// 9. GUARDRAIL POLICY
// ---------------------------------------------------------

class GuardrailPolicy {
    static evaluate({
        controlErrorRate,
        treatmentErrorRate,
        maximumIncrease
    }) {
        assertProbability(controlErrorRate, "controlErrorRate");
        assertProbability(treatmentErrorRate, "treatmentErrorRate");

        if (maximumIncrease < 0) {
            throw new RangeError("maximumIncrease cannot be negative.");
        }

        return (
            treatmentErrorRate - controlErrorRate
            <= maximumIncrease
        );
    }
}


// ---------------------------------------------------------
// 10. EXECUTION
// ---------------------------------------------------------

async function main() {
    const configuration = new ExperimentConfiguration({
        name: "Digital Checkout Experiment",
        researchQuestion:
            "Does a redesigned checkout increase purchase conversion?",
        nullHypothesis:
            "The redesign does not change conversion.",
        alternativeHypothesis:
            "The redesign increases conversion.",
        metric: "purchase_conversion",
        baselineRate: 0.10,
        treatmentRate: 0.125,
        alpha: 0.05,
        power: 0.80,
        minimumGroupSize: 30,
        expectedDirection: "increase",
        seed: 42
    });

    const experiment = new ExperimentService(configuration);

    experiment.on("audit", event => {
        console.log("[AUDIT]", event.event);
    });

    experiment.on("progress", progress => {
        console.log(
            `Progress: ${progress.processed}/${progress.total}`
        );
    });

    console.log("\nEXPERIMENT:", configuration.name);
    console.log("ID:", experiment.id);

    console.log(
        "Estimated sample size per group:",
        experiment.estimateSampleSize()
    );

    experiment.start();

    experiment.assignParticipants(2000);

    const observations = await experiment.execute();

    const guardrailPassed = GuardrailPolicy.evaluate({
        controlErrorRate: 0.02,
        treatmentErrorRate: 0.021,
        maximumIncrease: 0.01
    });

    const result = experiment.analyze(
        observations,
        { guardrailPassed }
    );

    console.log("\nEXPERIMENT REPORT");
    console.log("-----------------");
    console.log(JSON.stringify(result, null, 2));

    await experiment.export(
        "javascript_experiment_report.json",
        result
    );

    console.log("\nExperiment completed and report exported.");
}

main().catch(error => {
    console.error("Experiment failed:", error.message);
    process.exitCode = 1;
});
