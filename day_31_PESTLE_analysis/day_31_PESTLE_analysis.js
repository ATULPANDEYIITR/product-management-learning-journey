/**
 * PESTLE Analysis Event-Driven Model
 *
 * This Node.js-compatible file complements the Python implementation by
 * modeling PESTLE assessment as an event-driven workflow.
 *
 * The implementation focuses on:
 * - category-specific factor objects
 * - immutable-style factor updates
 * - event emission when assessments change
 * - policy-driven severity evaluation
 * - scenario recalculation
 * - review queues
 * - JSON serialization
 * - asynchronous workflow processing
 *
 * The six PESTLE dimensions remain distinct:
 * Political, Economic, Social, Technological, Legal, Environmental.
 */

"use strict";

const PESTLE_CATEGORIES = Object.freeze([
    "Political",
    "Economic",
    "Social",
    "Technological",
    "Legal",
    "Environmental",
]);

const DIRECTIONS = Object.freeze(["opportunity", "threat"]);
const HORIZONS = Object.freeze(["short", "medium", "long"]);

/**
 * A small event bus demonstrates a JavaScript-specific way to decouple
 * assessment changes from reporting and monitoring components.
 */
class EventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(listener);

        return () => this.listeners.get(eventName)?.delete(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) ?? [];

        for (const listener of listeners) {
            listener(payload);
        }
    }
}

function assertRange(name, value, minimum, maximum) {
    if (!Number.isInteger(value) || value < minimum || value > maximum) {
        throw new RangeError(
            `${name} must be an integer from ${minimum} to ${maximum}.`
        );
    }
}

function normalizeCategory(category) {
    if (typeof category !== "string") {
        throw new TypeError("Category must be a string.");
    }

    const normalized = category.trim().toLowerCase();

    const match = PESTLE_CATEGORIES.find(
        (item) => item.toLowerCase() === normalized
    );

    if (!match) {
        throw new RangeError(`Unsupported PESTLE category: ${category}`);
    }

    return match;
}

function createFactor(data) {
    const category = normalizeCategory(data.category);
    const direction = String(data.direction).toLowerCase();
    const horizon = String(data.horizon).toLowerCase();

    if (!DIRECTIONS.includes(direction)) {
        throw new RangeError(`Unsupported direction: ${direction}`);
    }

    if (!HORIZONS.includes(horizon)) {
        throw new RangeError(`Unsupported time horizon: ${horizon}`);
    }

    if (!data.id || !data.title || !data.description || !data.evidence) {
        throw new Error(
            "A factor requires id, title, description, and evidence."
        );
    }

    assertRange("likelihood", data.likelihood, 1, 5);
    assertRange("impact", data.impact, 1, 5);
    assertRange("confidence", data.confidence, 1, 5);

    return Object.freeze({
        id: String(data.id),
        category,
        title: String(data.title),
        description: String(data.description),
        direction,
        likelihood: data.likelihood,
        impact: data.impact,
        confidence: data.confidence,
        horizon,
        trend: String(data.trend ?? "stable"),
        evidence: String(data.evidence),
        affectedAreas: Object.freeze([
            ...(data.affectedAreas ?? [])
        ]),
    });
}

function rawScore(factor) {
    return factor.likelihood * factor.impact;
}

function confidenceAdjustedScore(factor) {
    const signed =
        factor.direction === "opportunity"
            ? rawScore(factor)
            : -rawScore(factor);

    return signed * (factor.confidence / 5);
}

/**
 * A repository-like PESTLE workspace is represented as a Map. The Map gives
 * efficient direct access by factor ID while preserving insertion order for
 * deterministic reports.
 */
class PESTLEWorkspace {
    constructor(organization, eventBus = new EventBus()) {
        if (!organization?.trim()) {
            throw new Error("Organization is required.");
        }

        this.organization = organization.trim();
        this.factors = new Map();
        this.events = eventBus;
    }

    addFactor(factor) {
        if (this.factors.has(factor.id)) {
            throw new Error(`Factor ${factor.id} already exists.`);
        }

        this.factors.set(factor.id, factor);

        this.events.emit("factor-added", {
            organization: this.organization,
            factor,
        });
    }

    updateFactor(id, changes) {
        const existing = this.factors.get(id);

        if (!existing) {
            throw new Error(`Unknown factor: ${id}`);
        }

        /**
         * Rebuilding the object rather than mutating it keeps factor records
         * predictable for listeners and prevents accidental partial updates.
         */
        const updated = createFactor({
            ...existing,
            ...changes,
            id: existing.id,
        });

        this.factors.set(id, updated);

        this.events.emit("factor-updated", {
            organization: this.organization,
            previous: existing,
            factor: updated,
        });
    }

    getFactors(category = null) {
        if (category === null) {
            return [...this.factors.values()];
        }

        const normalized = normalizeCategory(category);

        return [...this.factors.values()].filter(
            (factor) => factor.category === normalized
        );
    }

    categoryScore(category) {
        return this.getFactors(category).reduce(
            (total, factor) => total + confidenceAdjustedScore(factor),
            0
        );
    }

    netScore() {
        return this.getFactors().reduce(
            (total, factor) => total + confidenceAdjustedScore(factor),
            0
        );
    }

    rankBySignificance() {
        return this.getFactors().sort(
            (a, b) =>
                Math.abs(confidenceAdjustedScore(b)) -
                Math.abs(confidenceAdjustedScore(a))
        );
    }

    priorityQueue(minimumScore = 16) {
        return this.getFactors()
            .filter((factor) => rawScore(factor) >= minimumScore)
            .sort((a, b) => rawScore(b) - rawScore(a));
    }

    scenario({ likelihoodMultiplier = 1, impactMultiplier = 1 } = {}) {
        if (likelihoodMultiplier < 0 || impactMultiplier < 0) {
            throw new RangeError("Scenario multipliers cannot be negative.");
        }

        return this.getFactors().reduce((total, factor) => {
            const likelihood = Math.min(
                5,
                factor.likelihood * likelihoodMultiplier
            );

            const impact = Math.min(
                5,
                factor.impact * impactMultiplier
            );

            let score = likelihood * impact;

            if (factor.direction === "threat") {
                score *= -1;
            }

            return total + score * (factor.confidence / 5);
        }, 0);
    }

    reviewQueue() {
        /**
         * PESTLE assessment is evidence-driven. A factor with low confidence
         * should be revisited even when its mathematical score is moderate.
         */
        return this.getFactors()
            .filter(
                (factor) =>
                    factor.confidence <= 2 ||
                    factor.trend === "volatile"
            )
            .sort(
                (a, b) =>
                    confidenceAdjustedScore(a) -
                    confidenceAdjustedScore(b)
            );
    }

    categoryProfile() {
        return Object.fromEntries(
            PESTLE_CATEGORIES.map((category) => {
                const factors = this.getFactors(category);

                const opportunities = factors.filter(
                    (factor) => factor.direction === "opportunity"
                );

                const threats = factors.filter(
                    (factor) => factor.direction === "threat"
                );

                return [
                    category,
                    {
                        count: factors.length,
                        opportunities: opportunities.length,
                        threats: threats.length,
                        score: this.categoryScore(category),
                    },
                ];
            })
        );
    }

    toJSON() {
        return {
            organization: this.organization,
            factors: this.getFactors(),
            netScore: this.netScore(),
            categoryProfile: this.categoryProfile(),
        };
    }
}

/**
 * A policy engine evaluates an assessment against explicit decision rules.
 * The rules are not PESTLE factors themselves. They operationalize an
 * organization's governance thresholds.
 */
class PESTLEPolicyEngine {
    constructor({
        maximumHighImpactThreats = 2,
        minimumEvidenceConfidence = 3,
        requireLegalReview = true,
    } = {}) {
        this.maximumHighImpactThreats = maximumHighImpactThreats;
        this.minimumEvidenceConfidence = minimumEvidenceConfidence;
        this.requireLegalReview = requireLegalReview;
    }

    evaluate(workspace) {
        const factors = workspace.getFactors();

        const highImpactThreats = factors.filter(
            (factor) =>
                factor.direction === "threat" &&
                rawScore(factor) >= 16
        );

        const weakEvidence = factors.filter(
            (factor) => factor.confidence < this.minimumEvidenceConfidence
        );

        const legalThreats = factors.filter(
            (factor) =>
                factor.category === "Legal" &&
                factor.direction === "threat" &&
                rawScore(factor) >= 12
        );

        const issues = [];

        if (
            highImpactThreats.length >
            this.maximumHighImpactThreats
        ) {
            issues.push(
                "High-impact threat exposure exceeds the configured threshold."
            );
        }

        if (weakEvidence.length > 0) {
            issues.push(
                `${weakEvidence.length} factor(s) require stronger evidence.`
            );
        }

        if (this.requireLegalReview && legalThreats.length > 0) {
            issues.push(
                "Material legal threats require explicit legal review."
            );
        }

        return {
            eligible:
                issues.length === 0 &&
                highImpactThreats.length <=
                    this.maximumHighImpactThreats,
            issues,
            highImpactThreats,
            weakEvidence,
            legalThreats,
        };
    }
}

function buildWorkspace() {
    const workspace = new PESTLEWorkspace("Northstar Analytics");

    workspace.events.on("factor-added", ({ factor }) => {
        console.log(
            `[event] added ${factor.category}: ${factor.title}`
        );
    });

    workspace.events.on("factor-updated", ({ factor }) => {
        console.log(
            `[event] updated ${factor.id}: confidence=${factor.confidence}`
        );
    });

    const factors = [
        {
            id: "P-01",
            category: "Political",
            title: "Public digital infrastructure investment",
            description:
                "Government investment may increase demand for enterprise data platforms.",
            direction: "opportunity",
            likelihood: 4,
            impact: 4,
            confidence: 4,
            horizon: "medium",
            trend: "rising",
            evidence:
                "Market planning identifies public digital infrastructure as a target demand driver.",
            affectedAreas: ["public-sector sales"],
        },
        {
            id: "P-02",
            category: "Political",
            title: "Geopolitical procurement uncertainty",
            description:
                "International relations can alter procurement and technology-partner decisions.",
            direction: "threat",
            likelihood: 3,
            impact: 4,
            confidence: 3,
            horizon: "medium",
            trend: "volatile",
            evidence:
                "International expansion creates exposure to cross-border procurement conditions.",
            affectedAreas: ["international sales"],
        },
        {
            id: "E-01",
            category: "Economic",
            title: "Enterprise analytics spending",
            description:
                "Higher enterprise technology budgets can expand demand for analytics subscriptions.",
            direction: "opportunity",
            likelihood: 4,
            impact: 5,
            confidence: 4,
            horizon: "medium",
            trend: "rising",
            evidence:
                "Customer planning indicates increased data-modernization expenditure.",
            affectedAreas: ["subscription revenue"],
        },
        {
            id: "E-02",
            category: "Economic",
            title: "Currency volatility",
            description:
                "Currency movement can change imported infrastructure costs and foreign revenue value.",
            direction: "threat",
            likelihood: 4,
            impact: 3,
            confidence: 4,
            horizon: "short",
            trend: "volatile",
            evidence:
                "The operating model has both domestic costs and foreign-currency contracts.",
            affectedAreas: ["margin", "pricing"],
        },
        {
            id: "S-01",
            category: "Social",
            title: "Growth in data literacy",
            description:
                "Business users increasingly expect accessible evidence-based decision support.",
            direction: "opportunity",
            likelihood: 5,
            impact: 4,
            confidence: 4,
            horizon: "medium",
            trend: "rising",
            evidence:
                "Customer research identifies self-service analytics as a growing expectation.",
            affectedAreas: ["product adoption", "UX"],
        },
        {
            id: "S-02",
            category: "Social",
            title: "Resistance to analytics-driven workflow changes",
            description:
                "Employees may resist changes perceived as surveillance or job displacement.",
            direction: "threat",
            likelihood: 3,
            impact: 3,
            confidence: 3,
            horizon: "short",
            trend: "stable",
            evidence:
                "Enterprise implementation teams report change-management concerns.",
            affectedAreas: ["implementation"],
        },
        {
            id: "T-01",
            category: "Technological",
            title: "Real-time analytics capability",
            description:
                "Streaming infrastructure enables near-real-time operational decision support.",
            direction: "opportunity",
            likelihood: 5,
            impact: 5,
            confidence: 5,
            horizon: "medium",
            trend: "rising",
            evidence:
                "The product architecture supports event-based ingestion and incremental processing.",
            affectedAreas: ["product capability"],
        },
        {
            id: "T-02",
            category: "Technological",
            title: "Rapid platform obsolescence",
            description:
                "Fast technology cycles can increase engineering cost and architectural churn.",
            direction: "threat",
            likelihood: 4,
            impact: 4,
            confidence: 4,
            horizon: "long",
            trend: "rising",
            evidence:
                "The technology roadmap depends on rapidly evolving data infrastructure.",
            affectedAreas: ["engineering", "architecture"],
        },
        {
            id: "L-01",
            category: "Legal",
            title: "Data-protection obligations",
            description:
                "Personal-data processing creates obligations for lawful processing and security.",
            direction: "threat",
            likelihood: 4,
            impact: 5,
            confidence: 5,
            horizon: "short",
            trend: "rising",
            evidence:
                "Customer datasets may contain identifiable information.",
            affectedAreas: ["privacy", "security", "contracts"],
        },
        {
            id: "L-02",
            category: "Legal",
            title: "Contract standardization",
            description:
                "Consistent enterprise clauses can reduce negotiation effort and ambiguity.",
            direction: "opportunity",
            likelihood: 4,
            impact: 3,
            confidence: 4,
            horizon: "short",
            trend: "rising",
            evidence:
                "Commercial operations are adopting standardized enterprise agreements.",
            affectedAreas: ["sales cycle"],
        },
        {
            id: "EN-01",
            category: "Environmental",
            title: "Analytics compute energy demand",
            description:
                "Compute-heavy workloads can increase energy consumption and sustainability exposure.",
            direction: "threat",
            likelihood: 4,
            impact: 4,
            confidence: 4,
            horizon: "medium",
            trend: "rising",
            evidence:
                "Forecast workloads include continuous and compute-intensive analytics.",
            affectedAreas: ["operating cost"],
        },
        {
            id: "EN-02",
            category: "Environmental",
            title: "Sustainability analytics demand",
            description:
                "Customers may need platforms that consolidate environmental performance data.",
            direction: "opportunity",
            likelihood: 4,
            impact: 4,
            confidence: 3,
            horizon: "medium",
            trend: "rising",
            evidence:
                "Enterprise customers increasingly request environmental metrics.",
            affectedAreas: ["product modules", "sales"],
        },
    ];

    for (const data of factors) {
        workspace.addFactor(createFactor(data));
    }

    return workspace;
}

/**
 * Asynchronous execution makes the model suitable for later replacement of
 * synchronous in-memory data with database or API-backed factor sources.
 */
async function runAssessment() {
    const workspace = buildWorkspace();

    console.log("\nCATEGORY PROFILE");
    console.table(workspace.categoryProfile());

    console.log("\nTOP FACTORS");

    const topFactors = workspace.rankBySignificance().slice(0, 6);

    console.table(
        topFactors.map((factor) => ({
            category: factor.category,
            direction: factor.direction,
            score: rawScore(factor),
            adjusted: confidenceAdjustedScore(factor).toFixed(2),
            title: factor.title,
        }))
    );

    console.log("\nSCENARIOS");

    const scenarios = {
        baseline: {
            likelihoodMultiplier: 1,
            impactMultiplier: 1,
        },
        elevatedPressure: {
            likelihoodMultiplier: 1.2,
            impactMultiplier: 1.2,
        },
        lowerPressure: {
            likelihoodMultiplier: 0.8,
            impactMultiplier: 0.9,
        },
    };

    for (const [name, configuration] of Object.entries(scenarios)) {
        console.log(
            `${name}: ${workspace.scenario(configuration).toFixed(2)}`
        );
    }

    console.log("\nREVIEW QUEUE");

    for (const factor of workspace.reviewQueue()) {
        console.log(
            `${factor.category}: ${factor.title} ` +
            `(confidence=${factor.confidence}, trend=${factor.trend})`
        );
    }

    console.log("\nPOLICY EVALUATION");

    const policy = new PESTLEPolicyEngine({
        maximumHighImpactThreats: 2,
        minimumEvidenceConfidence: 3,
        requireLegalReview: true,
    });

    const evaluation = policy.evaluate(workspace);

    console.log(`Eligible under policy: ${evaluation.eligible}`);

    for (const issue of evaluation.issues) {
        console.log(`Policy issue: ${issue}`);
    }

    console.log("\nEVENT-DRIVEN UPDATE");

    workspace.updateFactor("EN-02", {
        confidence: 4,
        impact: 5,
    });

    console.log("\nSERIALIZED MODEL");

    console.log(
        JSON.stringify(workspace.toJSON(), null, 2)
    );

    return workspace;
}

runAssessment().catch((error) => {
    console.error("PESTLE assessment failed:", error.message);
    process.exitCode = 1;
});
