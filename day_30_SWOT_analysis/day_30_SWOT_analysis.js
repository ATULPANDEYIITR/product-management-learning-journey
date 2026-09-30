/**
 * SWOT Analysis
 *
 * Complementary JavaScript implementation focused on:
 * - event-driven SWOT lifecycle
 * - immutable-style factor normalization
 * - strategic interaction processing
 * - evidence confidence
 * - policy-like validation of SWOT inputs
 * - scenario recalculation
 * - asynchronous persistence
 *
 * Runtime: Node.js 18+
 */

"use strict";

const SWOT = Object.freeze({
    STRENGTH: "Strength",
    WEAKNESS: "Weakness",
    OPPORTUNITY: "Opportunity",
    THREAT: "Threat"
});

const POSITIVE_CATEGORIES = new Set([
    SWOT.STRENGTH,
    SWOT.OPPORTUNITY
]);

class SwotFactor {
    constructor({
        id,
        category,
        title,
        description,
        importance,
        impact,
        confidence,
        evidence = []
    }) {
        if (!Object.values(SWOT).includes(category)) {
            throw new TypeError(`Unknown SWOT category: ${category}`);
        }

        for (const [name, value] of Object.entries({
            importance,
            impact,
            confidence
        })) {
            if (!Number.isFinite(value) || value < 0 || value > 1) {
                throw new RangeError(`${name} must be between 0 and 1`);
            }
        }

        if (!title?.trim() || !description?.trim()) {
            throw new TypeError("A factor requires title and description.");
        }

        if (!Array.isArray(evidence)) {
            throw new TypeError("Evidence must be an array.");
        }

        this.id = id;
        this.category = category;
        this.title = title;
        this.description = description;
        this.importance = importance;
        this.impact = impact;
        this.confidence = confidence;
        this.evidence = Object.freeze([...evidence]);
        Object.freeze(this);
    }

    weightedImpact() {
        return this.importance * this.impact * this.confidence;
    }

    signedScore() {
        const direction = POSITIVE_CATEGORIES.has(this.category) ? 1 : -1;
        return direction * this.weightedImpact();
    }

    toJSON() {
        return {
            id: this.id,
            category: this.category,
            title: this.title,
            description: this.description,
            importance: this.importance,
            impact: this.impact,
            confidence: this.confidence,
            evidence: [...this.evidence],
            weightedImpact: Number(this.weightedImpact().toFixed(6)),
            signedScore: Number(this.signedScore().toFixed(6))
        };
    }
}

class SwotAnalysis {
    constructor(name, objective) {
        this.name = name;
        this.objective = objective;
        this.factors = new Map();
    }

    addFactor(factor) {
        if (this.factors.has(factor.id)) {
            throw new Error(`Factor ${factor.id} already exists.`);
        }

        this.factors.set(factor.id, factor);
        return this;
    }

    getFactors(category = null) {
        const values = [...this.factors.values()];

        return category === null
            ? values
            : values.filter(factor => factor.category === category);
    }

    categoryScore(category) {
        return this.getFactors(category)
            .reduce((total, factor) => total + factor.signedScore(), 0);
    }

    totalScore() {
        return [...this.factors.values()]
            .reduce((total, factor) => total + factor.signedScore(), 0);
    }

    validate() {
        const warnings = [];
        const ids = [...this.factors.keys()];

        if (ids.length === 0) {
            warnings.push("The SWOT matrix contains no factors.");
        }

        for (const category of Object.values(SWOT)) {
            if (this.getFactors(category).length === 0) {
                warnings.push(`No ${category.toLowerCase()} factors exist.`);
            }
        }

        const titles = this.getFactors().map(
            factor => factor.title.trim().toLowerCase()
        );

        if (new Set(titles).size !== titles.length) {
            warnings.push("Duplicate factor titles detected.");
        }

        for (const factor of this.getFactors()) {
            if (factor.evidence.length === 0) {
                warnings.push(
                    `${factor.id} has no evidence recorded.`
                );
            }
        }

        return warnings;
    }

    rankedFactors() {
        return this.getFactors().sort(
            (a, b) => b.weightedImpact() - a.weightedImpact()
        );
    }

    interaction(type, firstCategory, secondCategory) {
        const first = this.getFactors(firstCategory);
        const second = this.getFactors(secondCategory);

        if (first.length === 0 || second.length === 0) {
            return null;
        }

        const firstFactor = first.reduce(
            (best, current) =>
                current.weightedImpact() > best.weightedImpact()
                    ? current
                    : best
        );

        const secondFactor = second.reduce(
            (best, current) =>
                current.weightedImpact() > best.weightedImpact()
                    ? current
                    : best
        );

        const priorities = {
            SO: firstFactor.weightedImpact() * secondFactor.weightedImpact(),
            WO: firstFactor.weightedImpact() * secondFactor.weightedImpact(),
            ST: firstFactor.weightedImpact() * secondFactor.weightedImpact(),
            WT: firstFactor.weightedImpact() * secondFactor.weightedImpact()
        };

        return {
            type,
            first: firstFactor,
            second: secondFactor,
            priority: priorities[type]
        };
    }

    strategicInteractions() {
        return [
            this.interaction("SO", SWOT.STRENGTH, SWOT.OPPORTUNITY),
            this.interaction("WO", SWOT.WEAKNESS, SWOT.OPPORTUNITY),
            this.interaction("ST", SWOT.STRENGTH, SWOT.THREAT),
            this.interaction("WT", SWOT.WEAKNESS, SWOT.THREAT)
        ].filter(Boolean);
    }

    scenarioScore({
        opportunityMultiplier = 1,
        threatMultiplier = 1
    } = {}) {
        if (
            opportunityMultiplier < 0 ||
            threatMultiplier < 0
        ) {
            throw new RangeError("Scenario multipliers cannot be negative.");
        }

        return this.getFactors().reduce((total, factor) => {
            const base = factor.weightedImpact();

            if (factor.category === SWOT.OPPORTUNITY) {
                return total + base * opportunityMultiplier;
            }

            if (factor.category === SWOT.THREAT) {
                return total - base * threatMultiplier;
            }

            return total + factor.signedScore();
        }, 0);
    }

    toJSON() {
        return {
            name: this.name,
            objective: this.objective,
            factors: this.getFactors().map(factor => factor.toJSON())
        };
    }
}

/**
 * Event-driven processing separates the SWOT data model from consumers.
 * A dashboard, audit logger, or strategy engine can subscribe to these
 * lifecycle events without changing the core analysis object.
 */
class SwotEventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, handler) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(handler);

        return () => {
            this.listeners.get(eventName)?.delete(handler);
        };
    }

    emit(eventName, payload) {
        const handlers = this.listeners.get(eventName) ?? [];

        for (const handler of handlers) {
            try {
                handler(payload);
            } catch (error) {
                console.error(
                    `Event handler for ${eventName} failed:`,
                    error.message
                );
            }
        }
    }
}

class SwotWorkflow {
    constructor(analysis) {
        this.analysis = analysis;
        this.events = new SwotEventBus();
        this.state = "draft";
    }

    submit() {
        const warnings = this.analysis.validate();

        if (warnings.some(warning => warning.includes("no factors"))) {
            throw new Error("An empty SWOT analysis cannot be submitted.");
        }

        this.state = "submitted";
        this.events.emit("submitted", {
            analysis: this.analysis,
            warnings
        });
    }

    revise() {
        if (this.state === "archived") {
            throw new Error("Archived SWOT analyses cannot be revised.");
        }

        this.state = "draft";
        this.events.emit("revised", {
            analysis: this.analysis
        });
    }

    archive() {
        if (this.state !== "submitted") {
            throw new Error(
                "Only a submitted SWOT analysis can be archived."
            );
        }

        this.state = "archived";
        this.events.emit("archived", {
            analysis: this.analysis
        });
    }
}

/**
 * Asynchronous persistence is represented using a Promise-based function.
 * In a production application, this could be replaced with a database or
 * authenticated API while preserving the calling contract.
 */
async function persistAnalysis(analysis) {
    await new Promise(resolve => setTimeout(resolve, 20));

    const serialized = JSON.stringify(analysis.toJSON(), null, 2);

    return {
        bytes: Buffer.byteLength(serialized, "utf8"),
        payload: serialized
    };
}

function createManufacturingAnalysis() {
    const analysis = new SwotAnalysis(
        "ProcureSight Mid-Market Expansion",
        "Evaluate expansion into mid-market manufacturing procurement analytics."
    );

    const factors = [
        new SwotFactor({
            id: "S1",
            category: SWOT.STRENGTH,
            title: "Procurement anomaly detection",
            description:
                "The platform identifies unusual purchasing and supplier patterns.",
            importance: 0.90,
            impact: 0.85,
            confidence: 0.90,
            evidence: ["Validated customer workflows"]
        }),

        new SwotFactor({
            id: "S2",
            category: SWOT.STRENGTH,
            title: "Standardized data connectors",
            description:
                "Reusable connectors reduce the work required to ingest procurement data.",
            importance: 0.82,
            impact: 0.76,
            confidence: 0.88,
            evidence: ["Connector implementation records"]
        }),

        new SwotFactor({
            id: "W1",
            category: SWOT.WEAKNESS,
            title: "Limited brand recognition",
            description:
                "The company is less familiar to procurement executives than major vendors.",
            importance: 0.86,
            impact: 0.76,
            confidence: 0.91,
            evidence: ["Market interview observations"]
        }),

        new SwotFactor({
            id: "W2",
            category: SWOT.WEAKNESS,
            title: "Implementation capacity constraint",
            description:
                "Customer growth could exceed the current onboarding team's capacity.",
            importance: 0.84,
            impact: 0.82,
            confidence: 0.87,
            evidence: ["Current staffing model"]
        }),

        new SwotFactor({
            id: "O1",
            category: SWOT.OPPORTUNITY,
            title: "Demand for supplier cost visibility",
            description:
                "Manufacturers are seeking stronger visibility into supplier costs and purchasing behavior.",
            importance: 0.92,
            impact: 0.84,
            confidence: 0.76,
            evidence: ["Customer discovery interviews"]
        }),

        new SwotFactor({
            id: "O2",
            category: SWOT.OPPORTUNITY,
            title: "Cloud system adoption",
            description:
                "Cloud procurement systems can make standardized analytics integrations easier.",
            importance: 0.80,
            impact: 0.78,
            confidence: 0.75,
            evidence: ["Customer technology assessments"]
        }),

        new SwotFactor({
            id: "T1",
            category: SWOT.THREAT,
            title: "Bundled competitor analytics",
            description:
                "Large software vendors may bundle procurement analytics into existing contracts.",
            importance: 0.91,
            impact: 0.86,
            confidence: 0.86,
            evidence: ["Competitive product monitoring"]
        }),

        new SwotFactor({
            id: "T2",
            category: SWOT.THREAT,
            title: "Procurement approval friction",
            description:
                "Enterprise-style buying processes can delay contracts and deployment.",
            importance: 0.78,
            impact: 0.74,
            confidence: 0.84,
            evidence: ["Observed sales-cycle data"]
        })
    ];

    for (const factor of factors) {
        analysis.addFactor(factor);
    }

    return analysis;
}

function printMatrix(analysis) {
    console.log(`\n=== ${analysis.name} ===`);
    console.log(analysis.objective);

    for (const category of Object.values(SWOT)) {
        console.log(`\n${category.toUpperCase()}`);

        for (const factor of analysis.getFactors(category)) {
            console.log(
                `${factor.id}: ${factor.title} | ` +
                `weighted impact=${factor.weightedImpact().toFixed(3)}`
            );
            console.log(`  ${factor.description}`);
        }
    }
}

function printInteractions(analysis) {
    console.log("\n=== STRATEGIC INTERACTIONS ===");

    for (const interaction of analysis.strategicInteractions()) {
        console.log(
            `${interaction.type}: ${interaction.first.id} + ` +
            `${interaction.second.id} | priority=${interaction.priority.toFixed(3)}`
        );

        const meanings = {
            SO: "Use an internal strength to capture an external opportunity.",
            WO: "Use an opportunity to reduce an internal weakness.",
            ST: "Use an internal strength to reduce exposure to a threat.",
            WT: "Reduce internal weakness while containing external threat exposure."
        };

        console.log(`  ${meanings[interaction.type]}`);
    }
}

function printScenarios(analysis) {
    const scenarios = [
        {
            name: "Base assumptions",
            opportunityMultiplier: 1,
            threatMultiplier: 1
        },
        {
            name: "Higher demand",
            opportunityMultiplier: 1.25,
            threatMultiplier: 1
        },
        {
            name: "Stronger competition",
            opportunityMultiplier: 0.9,
            threatMultiplier: 1.3
        },
        {
            name: "Difficult implementation environment",
            opportunityMultiplier: 0.95,
            threatMultiplier: 1.2
        }
    ];

    console.log("\n=== SCENARIO SENSITIVITY ===");

    for (const scenario of scenarios) {
        const score = analysis.scenarioScore(scenario);

        console.log(
            `${scenario.name}: ${score.toFixed(3)}`
        );
    }
}

async function main() {
    const analysis = createManufacturingAnalysis();

    const workflow = new SwotWorkflow(analysis);

    workflow.events.on("submitted", ({ warnings }) => {
        console.log(
            `\nWorkflow event: submitted with ${warnings.length} warning(s).`
        );
    });

    workflow.events.on("archived", () => {
        console.log("Workflow event: analysis archived.");
    });

    printMatrix(analysis);

    console.log("\n=== VALIDATION ===");
    const warnings = analysis.validate();

    if (warnings.length === 0) {
        console.log("No validation warnings.");
    } else {
        warnings.forEach(warning => console.log(`Warning: ${warning}`));
    }

    printInteractions(analysis);
    printScenarios(analysis);

    console.log("\n=== WORKFLOW ===");
    workflow.submit();
    workflow.archive();
    console.log(`Final workflow state: ${workflow.state}`);

    console.log("\n=== ASYNCHRONOUS PERSISTENCE ===");

    const persisted = await persistAnalysis(analysis);

    console.log(
        `Serialized analysis size: ${persisted.bytes} bytes`
    );

    const parsed = JSON.parse(persisted.payload);

    console.log(
        `Persisted factors: ${parsed.factors.length}`
    );

    console.log("\n=== EDGE CASE ===");

    try {
        new SwotFactor({
            id: "BAD",
            category: SWOT.THREAT,
            title: "Invalid confidence",
            description: "This factor should fail validation.",
            importance: 0.8,
            impact: 0.8,
            confidence: 1.5
        });
    } catch (error) {
        console.log(`Validation rejected invalid input: ${error.message}`);
    }

    console.log("\n=== ANALYTICAL CAUTION ===");
    console.log(
        "SWOT scores organize judgment and evidence; they do not establish " +
        "that a strategy will succeed."
    );
}

main().catch(error => {
    console.error("SWOT analysis execution failed:", error);
    process.exitCode = 1;
});
