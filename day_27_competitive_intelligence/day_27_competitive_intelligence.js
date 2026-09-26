/*
 * Competitive Intelligence: Practical JavaScript Study
 *
 * This file demonstrates a browser/runtime-friendly competitive intelligence
 * workflow using synthetic data.
 *
 * Concepts:
 * - competitor discovery and classification
 * - structured research records
 * - pricing analysis
 * - feature comparison
 * - review sentiment
 * - evidence quality
 * - opportunity gaps
 * - normalization
 * - statistical correlation
 * - scenario modeling
 * - validation
 * - immutable transformations
 * - asynchronous research simulation
 * - JSON export
 *
 * The companies and numbers are fictional demonstration data.
 */

"use strict";

// ============================================================================
// 1. DATA MODEL
// ============================================================================

const CompetitorType = Object.freeze({
    DIRECT: "Direct",
    INDIRECT: "Indirect",
    POTENTIAL: "Potential"
});

const EvidenceQuality = Object.freeze({
    HIGH: "High",
    MEDIUM: "Medium",
    LOW: "Low"
});

class Evidence {
    constructor(source, observation, quality) {
        this.source = source;
        this.observation = observation;
        this.quality = quality;
        this.collectedDate = "2026-09-27";
    }

    reliabilityWeight() {
        return {
            [EvidenceQuality.HIGH]: 1.0,
            [EvidenceQuality.MEDIUM]: 0.7,
            [EvidenceQuality.LOW]: 0.4
        }[this.quality] ?? 0;
    }
}

class Review {
    constructor(rating, text, source) {
        this.rating = rating;
        this.text = text;
        this.source = source;
    }

    sentiment() {
        const positiveWords = new Set([
            "easy", "fast", "excellent", "helpful", "simple",
            "great", "reliable", "useful", "intuitive", "good", "powerful"
        ]);

        const negativeWords = new Set([
            "slow", "expensive", "confusing", "difficult", "poor",
            "limited", "buggy", "complex", "missing", "bad"
        ]);

        const words = this.text
            .toLowerCase()
            .match(/[a-z]+/g) ?? [];

        const positive = words.filter(word => positiveWords.has(word)).length;
        const negative = words.filter(word => negativeWords.has(word)).length;

        if (positive > negative) return "positive";
        if (negative > positive) return "negative";
        return "neutral";
    }
}

class PricingPlan {
    constructor(name, monthlyPrice, annualDiscount, includedUnits) {
        this.name = name;
        this.monthlyPrice = monthlyPrice;
        this.annualDiscount = annualDiscount;
        this.includedUnits = includedUnits;
    }

    effectiveAnnualMonthlyPrice() {
        return this.monthlyPrice * (1 - this.annualDiscount);
    }
}

class Competitor {
    constructor({
        name,
        type,
        segment,
        targetCustomer,
        positioning,
        websiteVisitsMillions,
        visitGrowthPercent,
        estimatedFundingMillions,
        employeeCount,
        plans,
        features,
        reviews,
        evidence
    }) {
        this.name = name;
        this.type = type;
        this.segment = segment;
        this.targetCustomer = targetCustomer;
        this.positioning = positioning;
        this.websiteVisitsMillions = websiteVisitsMillions;
        this.visitGrowthPercent = visitGrowthPercent;
        this.estimatedFundingMillions = estimatedFundingMillions;
        this.employeeCount = employeeCount;
        this.plans = plans;
        this.features = features;
        this.reviews = reviews;
        this.evidence = evidence;
    }

    averageRating() {
        if (this.reviews.length === 0) return 0;
        return this.reviews.reduce((sum, review) => sum + review.rating, 0)
            / this.reviews.length;
    }

    entryPrice() {
        if (this.plans.length === 0) return 0;
        return Math.min(...this.plans.map(plan => plan.monthlyPrice));
    }

    positiveReviewRatio() {
        if (this.reviews.length === 0) return 0;
        const positive = this.reviews
            .filter(review => review.sentiment() === "positive")
            .length;

        return positive / this.reviews.length;
    }

    averageFeatureScore() {
        const values = Object.values(this.features);
        if (values.length === 0) return 0;
        return values.reduce((sum, value) => sum + value, 0) / values.length;
    }
}


// ============================================================================
// 2. SYNTHETIC COMPETITOR DATABASE
// ============================================================================

function createCompetitors() {
    return [
        new Competitor({
            name: "MarketPilot",
            type: CompetitorType.DIRECT,
            segment: "SMB intelligence",
            targetCustomer: "Small and medium businesses",
            positioning: "Affordable competitive monitoring",
            websiteVisitsMillions: 4.8,
            visitGrowthPercent: 12,
            estimatedFundingMillions: 18,
            employeeCount: 95,
            plans: [
                new PricingPlan("Starter", 49, 0.15, 5),
                new PricingPlan("Growth", 129, 0.20, 20),
                new PricingPlan("Enterprise", 399, 0.25, 100)
            ],
            features: {
                competitorTracking: 9,
                pricingMonitoring: 8,
                reviewAnalysis: 6,
                marketReports: 7,
                alerts: 9,
                api: 5
            },
            reviews: [
                new Review(4.5, "Easy monitoring and helpful alerts", "ReviewSite"),
                new Review(4.0, "Good pricing but reporting is limited", "ReviewSite"),
                new Review(3.5, "Simple interface but API is confusing", "ReviewSite")
            ],
            evidence: [
                new Evidence(
                    "Company website",
                    "Three commercial tiers",
                    EvidenceQuality.HIGH
                ),
                new Evidence(
                    "Traffic intelligence",
                    "Growing website traffic",
                    EvidenceQuality.MEDIUM
                )
            ]
        }),

        new Competitor({
            name: "InsightForge",
            type: CompetitorType.DIRECT,
            segment: "Enterprise intelligence",
            targetCustomer: "Large organizations",
            positioning: "Deep enterprise competitive intelligence",
            websiteVisitsMillions: 7.2,
            visitGrowthPercent: 6,
            estimatedFundingMillions: 65,
            employeeCount: 310,
            plans: [
                new PricingPlan("Professional", 299, 0.10, 25),
                new PricingPlan("Enterprise", 899, 0.15, 150)
            ],
            features: {
                competitorTracking: 10,
                pricingMonitoring: 9,
                reviewAnalysis: 8,
                marketReports: 10,
                alerts: 8,
                api: 9
            },
            reviews: [
                new Review(4.3, "Powerful reports but expensive", "ReviewSite"),
                new Review(4.1, "Excellent data but complex setup", "ReviewSite"),
                new Review(3.8, "Useful enterprise features but difficult", "ReviewSite")
            ],
            evidence: [
                new Evidence(
                    "Company website",
                    "Enterprise-oriented plans",
                    EvidenceQuality.HIGH
                ),
                new Evidence(
                    "Company database",
                    "Substantial funding reported",
                    EvidenceQuality.MEDIUM
                )
            ]
        }),

        new Competitor({
            name: "ReviewLens",
            type: CompetitorType.INDIRECT,
            segment: "Customer intelligence",
            targetCustomer: "Consumer brands",
            positioning: "Customer-review analytics",
            websiteVisitsMillions: 3.1,
            visitGrowthPercent: 19,
            estimatedFundingMillions: 11,
            employeeCount: 72,
            plans: [
                new PricingPlan("Basic", 39, 0.10, 10),
                new PricingPlan("Pro", 99, 0.15, 40)
            ],
            features: {
                competitorTracking: 5,
                pricingMonitoring: 4,
                reviewAnalysis: 10,
                marketReports: 6,
                alerts: 7,
                api: 6
            },
            reviews: [
                new Review(4.6, "Excellent review analysis and easy interface", "ReviewSite"),
                new Review(4.4, "Fast and useful customer insights", "ReviewSite"),
                new Review(4.2, "Great product but missing market reports", "ReviewSite")
            ],
            evidence: [
                new Evidence(
                    "Company website",
                    "Review-centric product",
                    EvidenceQuality.HIGH
                )
            ]
        }),

        new Competitor({
            name: "DataAtlas",
            type: CompetitorType.POTENTIAL,
            segment: "Business data",
            targetCustomer: "Technology companies",
            positioning: "Large-scale company and market data",
            websiteVisitsMillions: 9.4,
            visitGrowthPercent: 3,
            estimatedFundingMillions: 120,
            employeeCount: 620,
            plans: [
                new PricingPlan("Data", 499, 0.10, 50),
                new PricingPlan("Enterprise", 1499, 0.20, 300)
            ],
            features: {
                competitorTracking: 8,
                pricingMonitoring: 5,
                reviewAnalysis: 3,
                marketReports: 9,
                alerts: 6,
                api: 10
            },
            reviews: [
                new Review(4.0, "Powerful data but expensive", "ReviewSite"),
                new Review(3.9, "Excellent API but complex", "ReviewSite"),
                new Review(4.1, "Reliable datasets", "ReviewSite")
            ],
            evidence: [
                new Evidence(
                    "Company database",
                    "Large business-data provider",
                    EvidenceQuality.MEDIUM
                )
            ]
        })
    ];
}


// ============================================================================
// 3. BASIC ANALYTICS
// ============================================================================

function groupByType(competitors) {
    return competitors.reduce((groups, competitor) => {
        if (!groups[competitor.type]) {
            groups[competitor.type] = [];
        }

        groups[competitor.type].push(competitor);
        return groups;
    }, {});
}

function minMaxNormalize(values) {
    if (values.length === 0) return [];

    const minimum = Math.min(...values);
    const maximum = Math.max(...values);

    if (minimum === maximum) {
        return values.map(() => 50);
    }

    return values.map(
        value => 100 * (value - minimum) / (maximum - minimum)
    );
}

function pricingAnalysis(competitors) {
    return competitors.map(competitor => ({
        company: competitor.name,
        entryPrice: competitor.entryPrice(),
        plans: competitor.plans.map(plan => ({
            name: plan.name,
            monthlyPrice: plan.monthlyPrice,
            annualEffectiveMonthlyPrice:
                plan.effectiveAnnualMonthlyPrice()
        }))
    }));
}

function featureMatrix(competitors) {
    const capabilities = [
        "competitorTracking",
        "pricingMonitoring",
        "reviewAnalysis",
        "marketReports",
        "alerts",
        "api"
    ];

    return competitors.map(competitor => {
        const row = { company: competitor.name };

        for (const capability of capabilities) {
            row[capability] = competitor.features[capability] ?? 0;
        }

        return row;
    });
}


// ============================================================================
// 4. REVIEW ANALYTICS
// ============================================================================

function extractReviewThemes(reviews) {
    const themeKeywords = {
        price: ["expensive", "pricing"],
        usability: ["easy", "simple", "confusing", "difficult"],
        performance: ["fast", "slow"],
        quality: ["excellent", "good", "great", "poor"],
        capability: ["powerful", "limited", "missing"],
        reliability: ["reliable", "buggy"]
    };

    const counts = Object.fromEntries(
        Object.keys(themeKeywords).map(theme => [theme, 0])
    );

    for (const review of reviews) {
        const words = new Set(
            review.text.toLowerCase().match(/[a-z]+/g) ?? []
        );

        for (const [theme, keywords] of Object.entries(themeKeywords)) {
            if (keywords.some(keyword => words.has(keyword))) {
                counts[theme]++;
            }
        }
    }

    return counts;
}


// ============================================================================
// 5. EVIDENCE QUALITY
// ============================================================================

function evidenceScore(competitor) {
    if (competitor.evidence.length === 0) return 0;

    const total = competitor.evidence
        .reduce((sum, evidence) => sum + evidence.reliabilityWeight(), 0);

    return 100 * total / competitor.evidence.length;
}


// ============================================================================
// 6. OPPORTUNITY-GAP ANALYSIS
// ============================================================================

function opportunityAnalysis(competitors) {
    const capabilities = [
        "competitorTracking",
        "pricingMonitoring",
        "reviewAnalysis",
        "marketReports",
        "alerts",
        "api"
    ];

    const importance = {
        competitorTracking: 0.90,
        pricingMonitoring: 1.00,
        reviewAnalysis: 0.90,
        marketReports: 0.80,
        alerts: 0.70,
        api: 0.85
    };

    return capabilities
        .map(capability => {
            const scores = competitors.map(
                competitor => competitor.features[capability] ?? 0
            );

            const average = scores.reduce(
                (sum, value) => sum + value,
                0
            ) / scores.length;

            const gap = Math.max(0, 10 - average);

            const evidence = competitors.reduce(
                (sum, competitor) => sum + evidenceScore(competitor),
                0
            ) / competitors.length / 100;

            return {
                capability,
                averageCapabilityScore: average,
                marketGap: gap,
                strategicImportance: importance[capability],
                evidenceStrength: evidence,
                opportunityScore:
                    gap * importance[capability] * evidence
            };
        })
        .sort((a, b) => b.opportunityScore - a.opportunityScore);
}


// ============================================================================
// 7. CORRELATION
// ============================================================================

function pearsonCorrelation(xs, ys) {
    if (xs.length !== ys.length || xs.length < 2) {
        return 0;
    }

    const xMean = xs.reduce((sum, x) => sum + x, 0) / xs.length;
    const yMean = ys.reduce((sum, y) => sum + y, 0) / ys.length;

    let numerator = 0;
    let xVariance = 0;
    let yVariance = 0;

    for (let index = 0; index < xs.length; index++) {
        const xDifference = xs[index] - xMean;
        const yDifference = ys[index] - yMean;

        numerator += xDifference * yDifference;
        xVariance += xDifference ** 2;
        yVariance += yDifference ** 2;
    }

    const denominator = Math.sqrt(xVariance * yVariance);

    return denominator === 0 ? 0 : numerator / denominator;
}


// ============================================================================
// 8. SCENARIO MODELING
// ============================================================================

function projectTraffic(competitor, years = 3) {
    const annualRate = competitor.visitGrowthPercent / 100;

    return competitor.websiteVisitsMillions *
        ((1 + annualRate) ** years);
}

function scenarioAnalysis(competitors) {
    return competitors.map(competitor => ({
        company: competitor.name,
        currentTraffic: competitor.websiteVisitsMillions,
        annualGrowthAssumption: competitor.visitGrowthPercent,
        threeYearScenario: projectTraffic(competitor)
    }));
}


// ============================================================================
// 9. VALIDATION
// ============================================================================

function validateCompetitor(competitor) {
    const errors = [];

    if (competitor.websiteVisitsMillions < 0) {
        errors.push("Website traffic cannot be negative.");
    }

    if (competitor.visitGrowthPercent < -100) {
        errors.push("Traffic decline cannot be below -100%.");
    }

    if (competitor.estimatedFundingMillions < 0) {
        errors.push("Funding cannot be negative.");
    }

    for (const plan of competitor.plans) {
        if (plan.monthlyPrice < 0) {
            errors.push(`Negative price in ${plan.name}.`);
        }

        if (plan.annualDiscount < 0 || plan.annualDiscount > 1) {
            errors.push(`Invalid annual discount in ${plan.name}.`);
        }
    }

    for (const review of competitor.reviews) {
        if (review.rating < 0 || review.rating > 5) {
            errors.push(`Invalid review rating: ${review.rating}.`);
        }
    }

    return errors;
}


// ============================================================================
// 10. ASYNCHRONOUS RESEARCH SIMULATION
// ============================================================================

function simulateExternalResearchSource(competitor) {
    /*
     * A real application could obtain authorized data from licensed APIs.
     * This demonstration uses a Promise to teach asynchronous control flow
     * without making network calls or requiring third-party packages.
     */
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                company: competitor.name,
                traffic: competitor.websiteVisitsMillions,
                trafficGrowth: competitor.visitGrowthPercent,
                source: "simulated-authorized-source"
            });
        }, 10);
    });
}

async function collectResearch(competitors) {
    /*
     * Promise.all allows independent research requests to execute concurrently.
     * In production, rate limits, retries, authentication, caching, timeouts,
     * and provider-specific API terms must be handled explicitly.
     */
    return Promise.all(
        competitors.map(competitor =>
            simulateExternalResearchSource(competitor)
        )
    );
}


// ============================================================================
// 11. JSON EXPORT
// ============================================================================

function buildExportObject(competitors) {
    return {
        generatedAt: new Date().toISOString(),
        dataType: "synthetic competitive-intelligence demonstration",
        competitors: competitors.map(competitor => ({
            name: competitor.name,
            type: competitor.type,
            segment: competitor.segment,
            targetCustomer: competitor.targetCustomer,
            positioning: competitor.positioning,
            websiteVisitsMillions: competitor.websiteVisitsMillions,
            visitGrowthPercent: competitor.visitGrowthPercent,
            entryPrice: competitor.entryPrice(),
            averageRating: competitor.averageRating(),
            positiveReviewRatio: competitor.positiveReviewRatio(),
            features: competitor.features
        }))
    };
}


// ============================================================================
// 12. DISPLAY UTILITIES
// ============================================================================

function printSection(title) {
    console.log(`\n${"=".repeat(80)}\n${title}\n${"=".repeat(80)}`);
}

function printMarketMap(competitors) {
    printSection("MARKET MAP");

    for (const competitor of competitors) {
        console.log(
            `${competitor.name.padEnd(18)} ` +
            `${competitor.type.padEnd(10)} ` +
            `${competitor.segment.padEnd(25)} ` +
            `${competitor.positioning}`
        );
    }
}

function printPricing(competitors) {
    printSection("PRICING ANALYSIS");

    for (const competitor of competitors) {
        console.log(`\n${competitor.name}`);

        for (const plan of competitor.plans) {
            console.log(
                `  ${plan.name.padEnd(14)} ` +
                `$${plan.monthlyPrice.toFixed(2)}/month ` +
                `annual-effective: $${plan.effectiveAnnualMonthlyPrice().toFixed(2)}`
            );
        }
    }
}

function printReviews(competitors) {
    printSection("REVIEW ANALYSIS");

    for (const competitor of competitors) {
        console.log(
            `${competitor.name.padEnd(18)} ` +
            `rating=${competitor.averageRating().toFixed(2)} ` +
            `positive=${(competitor.positiveReviewRatio() * 100).toFixed(1)}%`
        );

        console.log(
            "  themes:",
            extractReviewThemes(competitor.reviews)
        );
    }
}


// ============================================================================
// 13. COMPLETE PIPELINE
// ============================================================================

async function main() {
    const competitors = createCompetitors();

    printSection("COMPETITIVE INTELLIGENCE LEARNING LAB");

    printMarketMap(competitors);

    printSection("COMPETITOR CLASSIFICATION");
    console.log(groupByType(competitors));

    printSection("DATA QUALITY");

    for (const competitor of competitors) {
        const errors = validateCompetitor(competitor);

        console.log(
            `${competitor.name}: ${
                errors.length === 0
                    ? "OK"
                    : errors.join("; ")
            }`
        );
    }

    printPricing(competitors);
    printReviews(competitors);

    printSection("FEATURE MATRIX");
    console.table(featureMatrix(competitors));

    printSection("OPPORTUNITY GAP ANALYSIS");
    console.table(opportunityAnalysis(competitors));

    const traffic = competitors.map(
        competitor => competitor.websiteVisitsMillions
    );

    const growth = competitors.map(
        competitor => competitor.visitGrowthPercent
    );

    printSection("STATISTICAL ANALYSIS");
    console.log(
        "Traffic / growth correlation:",
        pearsonCorrelation(traffic, growth).toFixed(3)
    );
    console.log(
        "Correlation describes association, not causation."
    );

    printSection("SCENARIO ANALYSIS");
    console.table(scenarioAnalysis(competitors));

    printSection("ASYNC RESEARCH COLLECTION");
    const externalResearch = await collectResearch(competitors);
    console.table(externalResearch);

    printSection("JSON EXPORT");
    console.log(
        JSON.stringify(buildExportObject(competitors), null, 2)
    );

    printSection("ETHICAL CI BOUNDARIES");

    const rules = [
        "Use public, licensed, or explicitly authorized information.",
        "Respect access controls and applicable laws.",
        "Do not steal credentials, confidential information, or trade secrets.",
        "Do not impersonate people to obtain restricted information.",
        "Record source, date, methodology, and evidence quality.",
        "Separate observed facts from estimates and interpretation."
    ];

    rules.forEach(rule => console.log(`- ${rule}`));

    printSection("END");
}

main().catch(error => {
    console.error("Competitive intelligence pipeline failed:", error);
    process.exitCode = 1;
});
