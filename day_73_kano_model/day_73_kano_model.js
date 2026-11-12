"use strict";

/*
 * Kano Model: Event-Driven Customer Feature Evaluation
 *
 * Features:
 * - Functional/dysfunctional questionnaire evaluation
 * - Kano classification
 * - Event-driven response collection
 * - Customer response validation
 * - Satisfaction and dissatisfaction coefficients
 * - Feature prioritization
 * - Asynchronous JSON reporting
 * - Event listeners and policy evaluation
 */

const fs = require("node:fs/promises");
const EventEmitter = require("node:events");

const Response = Object.freeze({
    LIKE: "like",
    EXPECT: "expect",
    NEUTRAL: "neutral",
    TOLERATE: "tolerate",
    DISLIKE: "dislike"
});

const Category = Object.freeze({
    MUST_BE: "Must-be",
    PERFORMANCE: "Performance",
    ATTRACTIVE: "Attractive",
    INDIFFERENT: "Indifferent",
    REVERSE: "Reverse",
    QUESTIONABLE: "Questionable"
});

const RESPONSES = Object.values(Response);

const MATRIX = {
    like: {
        like: "Questionable",
        expect: "Reverse",
        neutral: "Reverse",
        tolerate: "Reverse",
        dislike: "Must-be"
    },
    expect: {
        like: "Attractive",
        expect: "Indifferent",
        neutral: "Indifferent",
        tolerate: "Indifferent",
        dislike: "Must-be"
    },
    neutral: {
        like: "Performance",
        expect: "Indifferent",
        neutral: "Indifferent",
        tolerate: "Indifferent",
        dislike: "Must-be"
    },
    tolerate: {
        like: "Performance",
        expect: "Indifferent",
        neutral: "Indifferent",
        tolerate: "Indifferent",
        dislike: "Must-be"
    },
    dislike: {
        like: "Performance",
        expect: "Performance",
        neutral: "Performance",
        tolerate: "Performance",
        dislike: "Questionable"
    }
};

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class KanoResponse {
    constructor(customerId, functional, dysfunctional) {
        if (typeof customerId !== "string" ||
            customerId.trim().length === 0) {
            throw new ValidationError("Invalid customer ID.");
        }

        if (!RESPONSES.includes(functional) ||
            !RESPONSES.includes(dysfunctional)) {
            throw new ValidationError("Invalid questionnaire response.");
        }

        this.customerId = customerId;
        this.functional = functional;
        this.dysfunctional = dysfunctional;
        Object.freeze(this);
    }

    classify() {
        return MATRIX[this.functional][this.dysfunctional];
    }
}

class Feature {
    constructor(id, name, description) {
        if (!id || !name) {
            throw new ValidationError(
                "Feature ID and name are required."
            );
        }

        this.id = id;
        this.name = name;
        this.description = description;
        this.responses = new Map();
    }

    addResponse(response) {
        if (this.responses.has(response.customerId)) {
            throw new ValidationError(
                `Duplicate response: ${response.customerId}`
            );
        }

        this.responses.set(response.customerId, response);
    }

    analyze() {
        const counts = new Map(
            Object.values(Category).map(category => [category, 0])
        );

        for (const response of this.responses.values()) {
            const category = response.classify();
            counts.set(category, counts.get(category) + 1);
        }

        const validCategories = [
            Category.MUST_BE,
            Category.PERFORMANCE,
            Category.ATTRACTIVE,
            Category.INDIFFERENT,
            Category.REVERSE
        ];

        const validTotal = validCategories.reduce(
            (sum, category) => sum + counts.get(category), 0
        );

        const dominant = validTotal === 0
            ? Category.QUESTIONABLE
            : validCategories.reduce((best, category) =>
                counts.get(category) > counts.get(best)
                    ? category
                    : best
            );

        const attractive = counts.get(Category.ATTRACTIVE);
        const performance = counts.get(Category.PERFORMANCE);
        const mustBe = counts.get(Category.MUST_BE);
        const indifferent = counts.get(Category.INDIFFERENT);

        const denominator =
            attractive + performance + mustBe + indifferent;

        const satisfaction = denominator === 0
            ? 0
            : (attractive + performance) / denominator;

        const dissatisfaction = denominator === 0
            ? 0
            : -(performance + mustBe) / denominator;

        const questionableRate = this.responses.size === 0
            ? 0
            : counts.get(Category.QUESTIONABLE) /
              this.responses.size;

        return Object.freeze({
            featureId: this.id,
            feature: this.name,
            totalResponses: this.responses.size,
            classification: dominant,
            counts: Object.fromEntries(counts),
            satisfaction: Number(satisfaction.toFixed(4)),
            dissatisfaction: Number(dissatisfaction.toFixed(4)),
            questionableRate: Number(questionableRate.toFixed(4))
        });
    }
}

class KanoEngine extends EventEmitter {
    constructor() {
        super();
        this.features = new Map();
        this.auditLog = [];
    }

    registerFeature(feature) {
        if (this.features.has(feature.id)) {
            throw new ValidationError("Feature already registered.");
        }

        this.features.set(feature.id, feature);

        this.emit("featureRegistered", {
            featureId: feature.id,
            timestamp: new Date().toISOString()
        });
    }

    submitResponse(featureId, customerId, functional, dysfunctional) {
        const feature = this.features.get(featureId);

        if (!feature) {
            throw new ValidationError("Unknown feature.");
        }

        const response = new KanoResponse(
            customerId,
            functional,
            dysfunctional
        );

        feature.addResponse(response);

        const event = Object.freeze({
            featureId,
            customerId,
            category: response.classify(),
            timestamp: new Date().toISOString()
        });

        this.auditLog.push(event);
        this.emit("responseSubmitted", event);

        return event;
    }

    generateReport() {
        return [...this.features.values()]
            .filter(feature => feature.responses.size > 0)
            .map(feature => feature.analyze())
            .sort((a, b) =>
                a.dissatisfaction - b.dissatisfaction
            );
    }

    async exportReport(filename) {
        const report = this.generateReport();

        await fs.writeFile(
            filename,
            JSON.stringify(report, null, 2),
            { encoding: "utf8", flag: "w" }
        );

        return filename;
    }
}

async function main() {
    const engine = new KanoEngine();

    engine.on("featureRegistered", event => {
        console.log("Registered:", event.featureId);
    });

    engine.on("responseSubmitted", event => {
        console.log(
            `Response received: ${event.featureId} -> ${event.category}`
        );
    });

    const features = [
        new Feature("F001", "Account Security", "Secure authentication."),
        new Feature("F002", "Application Speed", "Fast processing."),
        new Feature("F003", "AI Recommendations", "Personalized suggestions."),
        new Feature("F004", "Custom Dashboard", "Configurable interface.")
    ];

    for (const feature of features) {
        engine.registerFeature(feature);
    }

    const records = {
        F001: [
            ["C001", "like", "dislike"],
            ["C002", "expect", "dislike"],
            ["C003", "like", "dislike"]
        ],
        F002: [
            ["C001", "like", "dislike"],
            ["C002", "like", "neutral"],
            ["C003", "like", "dislike"]
        ],
        F003: [
            ["C001", "expect", "dislike"],
            ["C002", "expect", "dislike"],
            ["C003", "like", "dislike"]
        ],
        F004: [
            ["C001", "neutral", "neutral"],
            ["C002", "expect", "neutral"],
            ["C003", "neutral", "tolerate"]
        ]
    };

    for (const [featureId, responses] of Object.entries(records)) {
        for (const [customerId, functional, dysfunctional] of responses) {
            engine.submitResponse(
                featureId,
                customerId,
                functional,
                dysfunctional
            );
        }
    }

    const report = engine.generateReport();

    console.log("\nKANO ANALYSIS");
    console.table(report.map(item => ({
        Feature: item.feature,
        Classification: item.classification,
        Satisfaction: item.satisfaction,
        Dissatisfaction: item.dissatisfaction
    })));

    await engine.exportReport("kano_analysis.json");

    console.log("\nReport exported.");

    // Boundary and classification checks.
    const test = new KanoResponse(
        "TEST001",
        Response.LIKE,
        Response.DISLIKE
    );

    if (test.classify() !== Category.MUST_BE) {
        throw new Error("Kano matrix validation failed.");
    }

    try {
        engine.submitResponse(
            "F001", "C001", "like", "dislike"
        );
        throw new Error("Duplicate validation failed.");
    } catch (error) {
        if (!(error instanceof ValidationError)) {
            throw error;
        }
    }

    console.log("Validation tests passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
