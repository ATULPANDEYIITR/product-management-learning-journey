"use strict";

/*
 * Solution Design Decision Engine
 *
 * This implementation focuses on event-driven design exploration.
 * It separates:
 *   hypotheses -> constraints -> alternatives -> trade-offs -> decision
 *
 * Run with:
 *   node solution-design.js
 */

class Hypothesis {
    constructor(id, statement, evidenceRequired) {
        this.id = id;
        this.statement = statement;
        this.evidenceRequired = evidenceRequired;
        this.status = "proposed";
        this.confidence = 0.5;
    }

    evaluate(evidenceQuality, observedValue, requiredValue) {
        if (
            !Number.isFinite(evidenceQuality) ||
            evidenceQuality < 0 ||
            evidenceQuality > 1
        ) {
            throw new RangeError("Evidence quality must be between 0 and 1.");
        }

        if (observedValue >= requiredValue) {
            this.status = "validated";
            this.confidence = Math.min(
                1,
                0.5 + 0.5 * evidenceQuality
            );
        } else {
            this.status = "rejected";
            this.confidence = Math.max(
                0,
                0.5 * (1 - evidenceQuality)
            );
        }
    }
}

class Constraint {
    constructor(id, type, description, hard = true) {
        this.id = id;
        this.type = type;
        this.description = description;
        this.hard = hard;
    }
}

class Alternative {
    constructor({
        name,
        description,
        expectedValue,
        deliveryCost,
        operatingCost,
        implementationRisk,
        scalability,
        maintainability,
        reversibility,
        constraintPenalty = 0
    }) {
        this.name = name;
        this.description = description;
        this.expectedValue = expectedValue;
        this.deliveryCost = deliveryCost;
        this.operatingCost = operatingCost;
        this.implementationRisk = implementationRisk;
        this.scalability = scalability;
        this.maintainability = maintainability;
        this.reversibility = reversibility;
        this.constraintPenalty = constraintPenalty;
    }

    score() {
        return (
            this.expectedValue +
            0.20 * this.scalability +
            0.15 * this.maintainability +
            0.10 * this.reversibility -
            0.35 * this.implementationRisk -
            0.15 * this.deliveryCost -
            0.10 * this.operatingCost -
            this.constraintPenalty
        );
    }
}

class SolutionDesign {
    constructor(name) {
        this.name = name;
        this.hypotheses = new Map();
        this.constraints = new Map();
        this.alternatives = new Map();
        this.events = [];
    }

    addHypothesis(hypothesis) {
        if (this.hypotheses.has(hypothesis.id)) {
            throw new Error(`Duplicate hypothesis: ${hypothesis.id}`);
        }
        this.hypotheses.set(hypothesis.id, hypothesis);
        this.emit("hypothesis.added", hypothesis);
    }

    addConstraint(constraint) {
        if (this.constraints.has(constraint.id)) {
            throw new Error(`Duplicate constraint: ${constraint.id}`);
        }
        this.constraints.set(constraint.id, constraint);
        this.emit("constraint.added", constraint);
    }

    addAlternative(alternative) {
        if (this.alternatives.has(alternative.name)) {
            throw new Error(`Duplicate alternative: ${alternative.name}`);
        }
        this.alternatives.set(alternative.name, alternative);
        this.emit("alternative.added", alternative);
    }

    on(eventName, listener) {
        if (!this.listeners) {
            this.listeners = new Map();
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        this.events.push({
            eventName,
            timestamp: new Date().toISOString()
        });

        if (!this.listeners?.has(eventName)) {
            return;
        }

        for (const listener of this.listeners.get(eventName)) {
            listener(payload);
        }
    }

    assertHypothesesResolved() {
        const unresolved = [...this.hypotheses.values()]
            .filter(h => h.status === "proposed")
            .map(h => h.id);

        if (unresolved.length > 0) {
            throw new Error(
                `Unresolved hypotheses: ${unresolved.join(", ")}`
            );
        }
    }

    rankAlternatives() {
        this.assertHypothesesResolved();

        return [...this.alternatives.values()]
            .map(alternative => ({
                alternative,
                score: alternative.score()
            }))
            .sort((a, b) => b.score - a.score);
    }

    decide() {
        const ranking = this.rankAlternatives();

        if (ranking.length === 0) {
            throw new Error("No solution alternatives are available.");
        }

        const selected = ranking[0].alternative;

        this.emit("decision.selected", selected);

        return {
            selected,
            rejected: ranking.slice(1).map(item => item.alternative),
            ranking,
            tradeOffs: [
                {
                    criterion: "Latency",
                    preferred: "Queue-backed asynchronous architecture",
                    rationale:
                        "The client can receive an acknowledgement before "
                        + "downstream processing completes."
                },
                {
                    criterion: "Operational simplicity",
                    preferred: "Direct synchronous API",
                    rationale:
                        "The direct model has fewer infrastructure components "
                        + "and fewer asynchronous failure states."
                },
                {
                    criterion: "Replay and throughput",
                    preferred: "Managed event streaming",
                    rationale:
                        "Partitioned durable streams support high throughput "
                        + "and replay but increase platform complexity."
                }
            ]
        };
    }
}

function createDesign() {
    const design = new SolutionDesign("Operational Event Intake");

    design.on("decision.selected", alternative => {
        console.log(`Decision event: ${alternative.name}`);
    });

    const asyncHypothesis = new Hypothesis(
        "H-ASYNC",
        "Asynchronous processing absorbs bursts while keeping acknowledgement latency low.",
        "Load-test p95 latency and queue-depth measurements."
    );

    const durableHypothesis = new Hypothesis(
        "H-DURABLE",
        "Durable buffering preserves accepted events through consumer failures.",
        "Failure-injection and restart testing."
    );

    const replayHypothesis = new Hypothesis(
        "H-REPLAY",
        "Historical replay provides operational value when transformations change.",
        "Incident and reprocessing evidence."
    );

    asyncHypothesis.evaluate(0.90, 0.91, 0.80);
    durableHypothesis.evaluate(0.95, 0.98, 0.90);
    replayHypothesis.evaluate(0.75, 0.86, 0.70);

    design.addHypothesis(asyncHypothesis);
    design.addHypothesis(durableHypothesis);
    design.addHypothesis(replayHypothesis);

    design.addConstraint(new Constraint(
        "C-LATENCY",
        "non-functional",
        "Normal client acknowledgement should remain below 300 ms."
    ));

    design.addConstraint(new Constraint(
        "C-DURABILITY",
        "technical",
        "Accepted events must survive downstream consumer restarts."
    ));

    design.addConstraint(new Constraint(
        "C-BUDGET",
        "business",
        "Infrastructure and operating cost must remain moderate."
    ));

    design.addConstraint(new Constraint(
        "C-AUDIT",
        "regulatory",
        "Processing decisions must be traceable."
    ));

    design.addAlternative(new Alternative({
        name: "Direct synchronous API",
        description: "The request waits for downstream processing.",
        expectedValue: 6,
        deliveryCost: 2,
        operatingCost: 2,
        implementationRisk: 2,
        scalability: 4,
        maintainability: 7,
        reversibility: 8,
        constraintPenalty: 3
    }));

    design.addAlternative(new Alternative({
        name: "Queue-backed asynchronous architecture",
        description:
            "The API validates and accepts an event while workers process "
            + "durable messages independently.",
        expectedValue: 9,
        deliveryCost: 4,
        operatingCost: 4,
        implementationRisk: 3,
        scalability: 8,
        maintainability: 8,
        reversibility: 8
    }));

    design.addAlternative(new Alternative({
        name: "Managed event-streaming architecture",
        description:
            "Partitioned streams provide durable, replayable event distribution.",
        expectedValue: 9.5,
        deliveryCost: 7,
        operatingCost: 6,
        implementationRisk: 5,
        scalability: 10,
        maintainability: 6,
        reversibility: 5,
        constraintPenalty: 1.5
    }));

    return design;
}

function demonstrateFailureHandling() {
    console.log("\n=== Validation failure example ===");

    try {
        const invalid = new Hypothesis(
            "H-INVALID",
            "Invalid evidence input should be rejected.",
            "Validated measurement."
        );

        invalid.evaluate(1.4, 0.9, 0.8);
    } catch (error) {
        console.log(`Rejected invalid evidence: ${error.message}`);
    }
}

function printDesign(design, decision) {
    console.log("\n=== Hypotheses ===");
    for (const hypothesis of design.hypotheses.values()) {
        console.log(
            `${hypothesis.id}: ${hypothesis.status}, `
            + `confidence=${hypothesis.confidence.toFixed(2)}`
        );
    }

    console.log("\n=== Constraints ===");
    for (const constraint of design.constraints.values()) {
        console.log(
            `${constraint.id} [${constraint.type}] ${constraint.description}`
        );
    }

    console.log("\n=== Alternative ranking ===");
    for (const item of decision.ranking) {
        console.log(
            `${item.alternative.name}: ${item.score.toFixed(3)}`
        );
    }

    console.log("\n=== Selected solution ===");
    console.log(decision.selected.name);

    console.log("\n=== Trade-offs ===");
    for (const tradeOff of decision.tradeOffs) {
        console.log(
            `${tradeOff.criterion}: ${tradeOff.preferred}\n`
            + `  ${tradeOff.rationale}`
        );
    }

    console.log("\n=== Event history ===");
    console.log(JSON.stringify(design.events, null, 2));
}

function main() {
    const design = createDesign();
    const decision = design.decide();

    printDesign(design, decision);
    demonstrateFailureHandling();
}

main();
