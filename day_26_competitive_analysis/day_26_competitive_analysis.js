"use strict";

/*
Competitive Analysis
====================

This executable JavaScript study demonstrates:
- Competitive sets
- Direct and indirect competition
- Feature comparison
- Weighted scoring
- Positioning
- Price-value analysis
- Feature-gap analysis
- Similarity and positioning vectors
- Sensitivity analysis
- Validation and error handling
- JavaScript-specific data structures and functional patterns

Run with:
    node competitive_analysis.js
*/

// ============================================================================
// 1. DATA MODEL
// ============================================================================

const CompetitionType = Object.freeze({
    DIRECT: "Direct",
    INDIRECT: "Indirect",
    POTENTIAL: "Potential"
});

const FeatureStatus = Object.freeze({
    ABSENT: "Absent",
    BASIC: "Basic",
    STRONG: "Strong",
    DIFFERENTIATED: "Differentiated"
});

const statusStrength = Object.freeze({
    [FeatureStatus.ABSENT]: 0,
    [FeatureStatus.BASIC]: 1,
    [FeatureStatus.STRONG]: 2,
    [FeatureStatus.DIFFERENTIATED]: 3
});

const features = [
    {
        name: "Task Management",
        category: "Core",
        description: "Create, assign, prioritize, and track work."
    },
    {
        name: "Workflow Automation",
        category: "Automation",
        description: "Automate repetitive business processes."
    },
    {
        name: "Analytics",
        category: "Insights",
        description: "Measure performance and operational outcomes."
    },
    {
        name: "AI Assistance",
        category: "Intelligence",
        description: "Support planning and work execution with intelligent features."
    },
    {
        name: "Integrations",
        category: "Platform",
        description: "Connect the product to external systems."
    },
    {
        name: "Enterprise Security",
        category: "Security",
        description: "Support governance, access control, and auditing."
    }
];

const criteria = [
    {
        name: "Ease of Use",
        weight: 0.15,
        description: "How quickly customers can understand the product."
    },
    {
        name: "Task Management",
        weight: 0.15,
        description: "Quality of core work management."
    },
    {
        name: "Workflow Automation",
        weight: 0.15,
        description: "Ability to automate recurring processes."
    },
    {
        name: "Analytics",
        weight: 0.10,
        description: "Quality of operational insight."
    },
    {
        name: "AI Assistance",
        weight: 0.10,
        description: "Usefulness of intelligent assistance."
    },
    {
        name: "Integrations",
        weight: 0.10,
        description: "Breadth and usefulness of integrations."
    },
    {
        name: "Enterprise Security",
        weight: 0.10,
        description: "Security and governance capabilities."
    },
    {
        name: "Price Value",
        weight: 0.15,
        description: "Customer value relative to price."
    }
];

const competitors = [
    {
        name: "TaskFlow",
        type: CompetitionType.DIRECT,
        targetSegment: "SMB project teams",
        pricePerUser: 12,
        scores: {
            "Ease of Use": 4.7,
            "Task Management": 4.6,
            "Workflow Automation": 4.1,
            "Analytics": 3.7,
            "AI Assistance": 3.6,
            "Integrations": 4.2,
            "Enterprise Security": 3.5,
            "Price Value": 4.5
        },
        featureStatus: {
            "Task Management": FeatureStatus.STRONG,
            "Workflow Automation": FeatureStatus.STRONG,
            "Analytics": FeatureStatus.STRONG,
            "AI Assistance": FeatureStatus.BASIC,
            "Integrations": FeatureStatus.STRONG,
            "Enterprise Security": FeatureStatus.BASIC
        },
        positioning: "Simple project management for growing teams."
    },
    {
        name: "EnterpriseSuite",
        type: CompetitionType.DIRECT,
        targetSegment: "Large enterprises",
        pricePerUser: 30,
        scores: {
            "Ease of Use": 3.0,
            "Task Management": 4.5,
            "Workflow Automation": 4.7,
            "Analytics": 4.8,
            "AI Assistance": 4.2,
            "Integrations": 4.8,
            "Enterprise Security": 5.0,
            "Price Value": 3.0
        },
        featureStatus: {
            "Task Management": FeatureStatus.STRONG,
            "Workflow Automation": FeatureStatus.DIFFERENTIATED,
            "Analytics": FeatureStatus.DIFFERENTIATED,
            "AI Assistance": FeatureStatus.STRONG,
            "Integrations": FeatureStatus.DIFFERENTIATED,
            "Enterprise Security": FeatureStatus.DIFFERENTIATED
        },
        positioning: "Enterprise-grade work management at scale."
    },
    {
        name: "SpreadsheetPro",
        type: CompetitionType.INDIRECT,
        targetSegment: "Small teams and individuals",
        pricePerUser: 8,
        scores: {
            "Ease of Use": 4.2,
            "Task Management": 3.0,
            "Workflow Automation": 2.5,
            "Analytics": 3.6,
            "AI Assistance": 3.0,
            "Integrations": 3.9,
            "Enterprise Security": 3.0,
            "Price Value": 4.8
        },
        featureStatus: {
            "Task Management": FeatureStatus.BASIC,
            "Workflow Automation": FeatureStatus.BASIC,
            "Analytics": FeatureStatus.STRONG,
            "AI Assistance": FeatureStatus.BASIC,
            "Integrations": FeatureStatus.STRONG,
            "Enterprise Security": FeatureStatus.BASIC
        },
        positioning: "Flexible spreadsheet-based business analysis."
    },
    {
        name: "EmailWorkflow",
        type: CompetitionType.INDIRECT,
        targetSegment: "Small service businesses",
        pricePerUser: 5,
        scores: {
            "Ease of Use": 4.8,
            "Task Management": 2.4,
            "Workflow Automation": 2.0,
            "Analytics": 1.8,
            "AI Assistance": 2.2,
            "Integrations": 3.5,
            "Enterprise Security": 3.2,
            "Price Value": 4.9
        },
        featureStatus: {
            "Task Management": FeatureStatus.ABSENT,
            "Workflow Automation": FeatureStatus.BASIC,
            "Analytics": FeatureStatus.ABSENT,
            "AI Assistance": FeatureStatus.BASIC,
            "Integrations": FeatureStatus.BASIC,
            "Enterprise Security": FeatureStatus.BASIC
        },
        positioning: "Use familiar communication tools to coordinate work."
    }
];


// ============================================================================
// 2. VALIDATION
// ============================================================================

function validateWeights(criteriaList) {
    if (!Array.isArray(criteriaList) || criteriaList.length === 0) {
        throw new Error("At least one criterion is required.");
    }

    for (const criterion of criteriaList) {
        if (!criterion.name || typeof criterion.name !== "string") {
            throw new Error("Every criterion requires a name.");
        }

        if (
            typeof criterion.weight !== "number" ||
            !Number.isFinite(criterion.weight) ||
            criterion.weight < 0
        ) {
            throw new Error(
                `Invalid weight for criterion '${criterion.name}'.`
            );
        }
    }
}

function normalizeCriteria(criteriaList) {
    validateWeights(criteriaList);

    const total = criteriaList.reduce(
        (sum, criterion) => sum + criterion.weight,
        0
    );

    if (total <= 0) {
        throw new Error("Total criterion weight must be greater than zero.");
    }

    return criteriaList.map(criterion => ({
        ...criterion,
        weight: criterion.weight / total
    }));
}

function validateCompetitor(competitor, criteriaList) {
    if (!competitor.name.trim()) {
        throw new Error("Competitor name cannot be empty.");
    }

    if (
        typeof competitor.pricePerUser !== "number" ||
        competitor.pricePerUser < 0
    ) {
        throw new Error(
            `${competitor.name}: price must be a non-negative number.`
        );
    }

    for (const criterion of criteriaList) {
        const score = competitor.scores[criterion.name];

        if (typeof score !== "number" || !Number.isFinite(score)) {
            throw new Error(
                `${competitor.name}: missing score for ${criterion.name}.`
            );
        }

        if (score < 1 || score > 5) {
            throw new Error(
                `${competitor.name}: score for ${criterion.name} must be 1-5.`
            );
        }
    }
}


// ============================================================================
// 3. COMPETITIVE SCORING
// ============================================================================

function weightedScore(competitor, criteriaList) {
    return criteriaList.reduce(
        (total, criterion) =>
            total + competitor.scores[criterion.name] * criterion.weight,
        0
    );
}

function rankByScore(competitorList, criteriaList) {
    /*
    Array.prototype.sort mutates arrays. Copying with [...competitorList]
    avoids accidentally changing the original dataset.
    */
    return [...competitorList]
        .map(competitor => ({
            competitor,
            score: weightedScore(competitor, criteriaList)
        }))
        .sort((a, b) => b.score - a.score);
}

function printScoreTable(competitorList, criteriaList) {
    console.log("\nWEIGHTED COMPETITIVE COMPARISON");
    console.log("-".repeat(70));

    for (const item of rankByScore(competitorList, criteriaList)) {
        console.log(
            `${item.competitor.name.padEnd(20)} ` +
            `${item.competitor.type.padEnd(12)} ` +
            `${item.score.toFixed(2)}`
        );
    }
}


// ============================================================================
// 4. DIRECT VS INDIRECT COMPETITION
// ============================================================================

function explainCompetitionType(competitor, targetCustomer, need) {
    if (competitor.type === CompetitionType.DIRECT) {
        return (
            `${competitor.name} directly targets ${targetCustomer} with ` +
            `a substantially similar solution to ${need}.`
        );
    }

    if (competitor.type === CompetitionType.INDIRECT) {
        return (
            `${competitor.name} addresses part of the same need through ` +
            `a different solution category.`
        );
    }

    return (
        `${competitor.name} could become relevant if its capabilities ` +
        `are redirected toward the target need.`
    );
}

function printCompetitionClassification(competitorList) {
    console.log("\nCOMPETITION CLASSIFICATION");
    console.log("-".repeat(70));

    for (const competitor of competitorList) {
        console.log(`\n${competitor.name}`);
        console.log(`Type: ${competitor.type}`);
        console.log(`Target segment: ${competitor.targetSegment}`);
        console.log(
            explainCompetitionType(
                competitor,
                "growing operations teams",
                "repeatable operational work"
            )
        );
        console.log(`Positioning: ${competitor.positioning}`);
    }
}


// ============================================================================
// 5. FEATURE MATRIX
// ============================================================================

function featureComparison(featureName, competitorList) {
    return Object.fromEntries(
        competitorList.map(competitor => [
            competitor.name,
            competitor.featureStatus[featureName] ?? FeatureStatus.ABSENT
        ])
    );
}

function printFeatureMatrix(featureList, competitorList) {
    console.log("\nFEATURE COMPARISON MATRIX");
    console.log("-".repeat(110));

    console.log(
        "Feature".padEnd(25) +
        competitorList.map(c => c.name.padEnd(20)).join("")
    );

    for (const feature of featureList) {
        const row = competitorList
            .map(
                competitor =>
                    (
                        competitor.featureStatus[feature.name] ??
                        FeatureStatus.ABSENT
                    ).padEnd(20)
            )
            .join("");

        console.log(feature.name.padEnd(25) + row);
    }
}


// ============================================================================
// 6. FEATURE GAP ANALYSIS
// ============================================================================

function featureGaps(focalProductFeatures, competitor) {
    return Object.entries(competitor.featureStatus)
        .filter(([featureName, competitorStatus]) => {
            const focalStatus =
                focalProductFeatures[featureName] ??
                FeatureStatus.ABSENT;

            return (
                statusStrength[competitorStatus] >
                statusStrength[focalStatus]
            );
        })
        .map(([featureName, competitorStatus]) => ({
            featureName,
            competitorStatus,
            focalStatus:
                focalProductFeatures[featureName] ??
                FeatureStatus.ABSENT
        }));
}

function printFeatureGaps(focalProductFeatures, competitorList) {
    console.log("\nFOCAL PRODUCT FEATURE GAPS");
    console.log("-".repeat(70));

    for (const competitor of competitorList) {
        console.log(`\nAgainst ${competitor.name}:`);

        const gaps = featureGaps(focalProductFeatures, competitor);

        if (gaps.length === 0) {
            console.log("  No stronger feature status detected.");
            continue;
        }

        for (const gap of gaps) {
            console.log(
                `  ${gap.featureName}: ` +
                `focal=${gap.focalStatus}, ` +
                `competitor=${gap.competitorStatus}`
            );
        }
    }
}


// ============================================================================
// 7. PRICE-VALUE ANALYSIS
// ============================================================================

function pricePerValuePoint(competitor, criteriaList) {
    const score = weightedScore(competitor, criteriaList);

    if (score === 0) {
        return Infinity;
    }

    return competitor.pricePerUser / score;
}

function printPriceValue(competitorList, criteriaList) {
    console.log("\nPRICE-VALUE ANALYSIS");
    console.log("-".repeat(70));

    for (const competitor of competitorList) {
        const score = weightedScore(competitor, criteriaList);
        const ratio = pricePerValuePoint(competitor, criteriaList);

        console.log(
            `${competitor.name.padEnd(20)} ` +
            `$${competitor.pricePerUser.toFixed(2).padStart(7)} ` +
            `score=${score.toFixed(2).padStart(5)} ` +
            `price/point=$${ratio.toFixed(2)}`
        );
    }

    console.log(
        "\nThe price-per-point metric is descriptive, not a universal measure " +
        "of customer value."
    );
}


// ============================================================================
// 8. POSITIONING MAP
// ============================================================================

function positioningVectors(competitorList, xDimension, yDimension) {
    return competitorList.map(competitor => ({
        name: competitor.name,
        x: competitor.scores[xDimension],
        y: competitor.scores[yDimension]
    }));
}

function printPositioningMap(
    competitorList,
    xDimension,
    yDimension
) {
    console.log(
        `\nPOSITIONING MAP: ${xDimension} vs. ${yDimension}`
    );
    console.log("-".repeat(70));

    for (const point of positioningVectors(
        competitorList,
        xDimension,
        yDimension
    )) {
        console.log(
            `${point.name.padEnd(20)} ` +
            `x=${point.x.toFixed(2)} ` +
            `y=${point.y.toFixed(2)}`
        );
    }
}


// ============================================================================
// 9. VECTOR SIMILARITY
// ============================================================================

function euclideanDistance(vectorA, vectorB) {
    if (vectorA.length !== vectorB.length) {
        throw new Error("Vectors must have equal dimensions.");
    }

    return Math.sqrt(
        vectorA.reduce(
            (sum, value, index) =>
                sum + (value - vectorB[index]) ** 2,
            0
        )
    );
}

function competitorVector(competitor, dimensions) {
    return dimensions.map(
        dimension => competitor.scores[dimension]
    );
}

function similarityToReference(
    referenceCompetitor,
    competitorList,
    dimensions
) {
    const referenceVector = competitorVector(
        referenceCompetitor,
        dimensions
    );

    return competitorList
        .filter(c => c.name !== referenceCompetitor.name)
        .map(competitor => ({
            name: competitor.name,
            distance: euclideanDistance(
                referenceVector,
                competitorVector(competitor, dimensions)
            )
        }))
        .sort((a, b) => a.distance - b.distance);
}


// ============================================================================
// 10. SENSITIVITY ANALYSIS
// ============================================================================

function sensitivityAnalysis(
    competitorList,
    baseCriteria,
    changedCriterion,
    newWeight
) {
    if (newWeight < 0 || newWeight > 1) {
        throw new Error("New weight must be between 0 and 1.");
    }

    const modifiedCriteria = baseCriteria.map(criterion =>
        criterion.name === changedCriterion
            ? { ...criterion, weight: newWeight }
            : { ...criterion }
    );

    const normalized = normalizeCriteria(modifiedCriteria);

    return rankByScore(competitorList, normalized);
}

function printSensitivityAnalysis(competitorList, criteriaList) {
    console.log("\nSENSITIVITY ANALYSIS");
    console.log("-".repeat(70));

    const scenarios = [
        ["Ease of Use", 0.30],
        ["Enterprise Security", 0.30],
        ["Price Value", 0.30]
    ];

    for (const [criterion, weight] of scenarios) {
        console.log(`\nScenario: ${criterion} weight = ${weight}`);

        const result = sensitivityAnalysis(
            competitorList,
            criteriaList,
            criterion,
            weight
        );

        for (const item of result) {
            console.log(
                `  ${item.competitor.name.padEnd(20)} ` +
                `${item.score.toFixed(2)}`
            );
        }
    }
}


// ============================================================================
// 11. POSITIONING PROFILE
// ============================================================================

const focusFlow = {
    productName: "FocusFlow",
    targetCustomer:
        "Growing operations teams with 20-200 employees",
    primaryNeed:
        "Coordinating repeatable operational work without enterprise-level complexity",
    keyDifference:
        "Simple workflow automation combined with actionable operational analytics",
    valueProposition:
        "FocusFlow helps growing teams standardize recurring work, " +
        "automate routine steps, and understand operational performance " +
        "without requiring a large enterprise implementation.",
    features: {
        "Task Management": FeatureStatus.STRONG,
        "Workflow Automation": FeatureStatus.DIFFERENTIATED,
        "Analytics": FeatureStatus.DIFFERENTIATED,
        "AI Assistance": FeatureStatus.STRONG,
        "Integrations": FeatureStatus.STRONG,
        "Enterprise Security": FeatureStatus.BASIC
    }
};

function printPositioningProfile(profile) {
    console.log("\nFOCUSFLOW POSITIONING");
    console.log("-".repeat(70));

    console.log(`Product: ${profile.productName}`);
    console.log(`Target: ${profile.targetCustomer}`);
    console.log(`Need: ${profile.primaryNeed}`);
    console.log(`Difference: ${profile.keyDifference}`);
    console.log(`Value proposition: ${profile.valueProposition}`);
}


// ============================================================================
// 12. ANALYTICAL PRINCIPLES
// ============================================================================

function printPrinciples() {
    console.log("\nANALYTICAL PRINCIPLES");
    console.log("-".repeat(70));

    const principles = [
        [
            "Competitive set",
            "Include realistic customer alternatives, not merely similar products."
        ],
        [
            "Direct competition",
            "A substantially similar solution addresses the same customer need."
        ],
        [
            "Indirect competition",
            "A different solution can still consume the same customer budget or solve the same underlying problem."
        ],
        [
            "Feature comparison",
            "A feature matrix describes capability; it does not establish customer importance."
        ],
        [
            "Positioning",
            "Positioning describes the intended place of a product in a customer's mental and competitive frame."
        ],
        [
            "Differentiation",
            "A differentiator should be meaningful to customers and credible in the market."
        ],
        [
            "Weighted scoring",
            "A composite score makes assumptions explicit but remains dependent on the chosen criteria and weights."
        ],
        [
            "Sensitivity",
            "Large score changes after small weight changes indicate assumption sensitivity."
        ]
    ];

    for (const [name, explanation] of principles) {
        console.log(`${name}: ${explanation}`);
    }
}


// ============================================================================
// 13. ERROR HANDLING DEMONSTRATION
// ============================================================================

function demonstrateValidation() {
    console.log("\nVALIDATION AND EDGE CASES");
    console.log("-".repeat(70));

    try {
        validateWeights([
            {
                name: "Invalid",
                weight: -0.5
            }
        ]);
    } catch (error) {
        console.log(`Caught invalid weight: ${error.message}`);
    }

    try {
        euclideanDistance([1, 2], [1]);
    } catch (error) {
        console.log(`Caught invalid vector: ${error.message}`);
    }

    try {
        validateCompetitor(
            {
                name: "BrokenProduct",
                type: CompetitionType.DIRECT,
                targetSegment: "Example",
                pricePerUser: -2,
                scores: {},
                featureStatus: {}
            },
            criteria
        );
    } catch (error) {
        console.log(`Caught invalid competitor: ${error.message}`);
    }
}


// ============================================================================
// 14. BUILT-IN TESTS
// ============================================================================

function runTests(competitorList, normalizedCriteria) {
    console.log("\nBUILT-IN TESTS");
    console.log("-".repeat(70));

    if (Math.abs(
        normalizedCriteria.reduce(
            (sum, criterion) => sum + criterion.weight,
            0
        ) - 1
    ) > 1e-9) {
        throw new Error("Criteria weights do not sum to one.");
    }

    for (const competitor of competitorList) {
        validateCompetitor(competitor, normalizedCriteria);

        const score = weightedScore(
            competitor,
            normalizedCriteria
        );

        if (score < 1 || score > 5) {
            throw new Error("Weighted score is outside the expected range.");
        }
    }

    if (
        Math.abs(euclideanDistance(
            [1, 2, 3],
            [4, 6, 3]
        ) - 5) > 1e-9
    ) {
        throw new Error("Distance calculation failed.");
    }

    console.log("All tests passed.");
}


// ============================================================================
// 15. MAIN PROGRAM
// ============================================================================

function main() {
    const normalizedCriteria = normalizeCriteria(criteria);

    for (const competitor of competitors) {
        validateCompetitor(
            competitor,
            normalizedCriteria
        );
    }

    printPositioningProfile(focusFlow);
    printCompetitionClassification(competitors);
    printScoreTable(competitors, normalizedCriteria);
    printFeatureMatrix(features, competitors);

    printFeatureGaps(
        focusFlow.features,
        competitors
    );

    printPriceValue(
        competitors,
        normalizedCriteria
    );

    printPositioningMap(
        competitors,
        "Ease of Use",
        "Workflow Automation"
    );

    const dimensions = [
        "Ease of Use",
        "Workflow Automation",
        "Analytics",
        "Enterprise Security"
    ];

    const reference = competitors[0];

    console.log(
        `\nSIMILARITY TO ${reference.name.toUpperCase()}`
    );
    console.log("-".repeat(70));

    for (const item of similarityToReference(
        reference,
        competitors,
        dimensions
    )) {
        console.log(
            `${item.name.padEnd(20)} distance=${item.distance.toFixed(2)}`
        );
    }

    printSensitivityAnalysis(
        competitors,
        normalizedCriteria
    );

    printPrinciples();
    demonstrateValidation();
    runTests(competitors, normalizedCriteria);

    console.log("\nIMPLEMENTATION CONSIDERATIONS");
    console.log("-".repeat(70));
    console.log(
        "Use immutable data patterns when possible. The spread operator " +
        "is used before sorting so the source competitor array is not mutated."
    );
    console.log(
        "For production systems, scores should be traceable to evidence " +
        "rather than entered as unsupported assumptions."
    );
    console.log(
        "Do not expose confidential competitive intelligence in client-side " +
        "JavaScript. Browser code is observable by users."
    );
}

main();
