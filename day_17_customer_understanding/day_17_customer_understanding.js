/*
 * Customer Understanding:
 * Customers, Users, Buyers, Decision-Makers, Influencers, Personas
 *
 * A self-contained JavaScript study file progressing from fundamental
 * customer-role modeling to segmentation, journey analysis, asynchronous
 * research aggregation, scoring, experimentation, validation, and privacy.
 *
 * Run with:
 *   node customer-understanding.js
 *
 * The file uses standard JavaScript and requires no external packages.
 */


// ============================================================================
// 1. FUNDAMENTAL CUSTOMER ROLES
// ============================================================================

console.log("=".repeat(78));
console.log("1. Fundamental customer roles");
console.log("=".repeat(78));

/*
 * Customer roles frequently overlap, but they are conceptually different.
 *
 * Customer: person or organization having the commercial/service relationship.
 * User: person who actually uses the product.
 * Buyer: person who purchases or initiates procurement.
 * Decision-maker: person with authority to approve or reject.
 * Influencer: person whose knowledge or opinion affects the decision.
 */

const customerRoles = Object.freeze({
    CUSTOMER: "customer",
    USER: "user",
    BUYER: "buyer",
    DECISION_MAKER: "decision-maker",
    INFLUENCER: "influencer"
});

const buyingTeam = [
    {
        name: "Asha",
        role: customerRoles.USER,
        department: "Operations",
        influence: 0.55,
        goals: ["fast reporting", "simple workflows"]
    },
    {
        name: "Rahul",
        role: customerRoles.BUYER,
        department: "Procurement",
        influence: 0.65,
        goals: ["commercial clarity"]
    },
    {
        name: "Meera",
        role: customerRoles.DECISION_MAKER,
        department: "Finance",
        influence: 0.95,
        goals: ["ROI", "cost control"]
    },
    {
        name: "Vikram",
        role: customerRoles.INFLUENCER,
        department: "IT",
        influence: 0.80,
        goals: ["security", "integration"]
    }
];

for (const participant of buyingTeam) {
    console.log(
        `${participant.name}: ${participant.role}, ` +
        `${participant.department}, influence=${participant.influence}`
    );
}


// ============================================================================
// 2. PERSONA MODEL
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("2. Evidence-based persona");
console.log("=".repeat(78));

class Persona {
    constructor({
        name,
        segment,
        goals,
        painPoints,
        behaviors,
        channels,
        objections,
        triggers,
        evidenceCount
    }) {
        this.name = name;
        this.segment = segment;
        this.goals = goals;
        this.painPoints = painPoints;
        this.behaviors = behaviors;
        this.channels = channels;
        this.objections = objections;
        this.triggers = triggers;
        this.evidenceCount = evidenceCount;
    }

    qualityCheck() {
        return {
            goals: this.goals.length > 0,
            painPoints: this.painPoints.length > 0,
            behaviors: this.behaviors.length > 0,
            channels: this.channels.length > 0,
            objections: this.objections.length > 0,
            triggers: this.triggers.length > 0,
            evidence: this.evidenceCount > 0
        };
    }
}

const operationsPersona = new Persona({
    name: "Operations Analyst",
    segment: "mid-market operations",
    goals: ["reduce manual reporting", "increase reliability"],
    painPoints: ["spreadsheet duplication", "slow reporting"],
    behaviors: ["daily report checks", "weekly data exports"],
    channels: ["email", "web application"],
    objections: ["migration effort", "training"],
    triggers: ["reporting errors", "compliance changes"],
    evidenceCount: 27
});

console.log(operationsPersona.name);
console.log(operationsPersona.qualityCheck());


// ============================================================================
// 3. NEEDS, PAINS, AND OUTCOMES
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("3. Customer needs and opportunity");
console.log("=".repeat(78));

function opportunityScore(importance, satisfaction) {
    if (importance < 0 || satisfaction < 0 || satisfaction > 10) {
        throw new RangeError("Importance must be non-negative and satisfaction must be 0-10.");
    }

    return importance * (10 - satisfaction);
}

const customerNeeds = [
    {
        need: "Reduce manual reporting",
        importance: 9,
        satisfaction: 3
    },
    {
        need: "Improve data visibility",
        importance: 8,
        satisfaction: 5
    },
    {
        need: "Reduce onboarding time",
        importance: 7,
        satisfaction: 4
    }
];

for (const item of customerNeeds) {
    console.log(
        item.need,
        "opportunity=",
        opportunityScore(item.importance, item.satisfaction).toFixed(2)
    );
}


// ============================================================================
// 4. BEHAVIORAL CUSTOMER DATA
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("4. Behavioral customer profiles");
console.log("=".repeat(78));

const customers = [
    {
        id: "C001",
        industry: "manufacturing",
        companySize: 450,
        annualValue: 120000,
        sessionsPerMonth: 38,
        supportTickets: 2,
        satisfaction: 8.4,
        adoptionRate: 0.87,
        decisionCycleDays: 45,
        primaryGoal: "efficiency"
    },
    {
        id: "C002",
        industry: "retail",
        companySize: 70,
        annualValue: 18000,
        sessionsPerMonth: 14,
        supportTickets: 8,
        satisfaction: 6.1,
        adoptionRate: 0.48,
        decisionCycleDays: 18,
        primaryGoal: "cost"
    },
    {
        id: "C003",
        industry: "finance",
        companySize: 1200,
        annualValue: 310000,
        sessionsPerMonth: 61,
        supportTickets: 1,
        satisfaction: 9.0,
        adoptionRate: 0.92,
        decisionCycleDays: 90,
        primaryGoal: "risk"
    },
    {
        id: "C004",
        industry: "education",
        companySize: 250,
        annualValue: 42000,
        sessionsPerMonth: 27,
        supportTickets: 5,
        satisfaction: 7.2,
        adoptionRate: 0.69,
        decisionCycleDays: 30,
        primaryGoal: "access"
    }
];

function sizeSegment(customer) {
    if (customer.companySize < 100) {
        return "small";
    }

    if (customer.companySize < 1000) {
        return "mid-market";
    }

    return "enterprise";
}

function adoptionSegment(customer) {
    if (customer.adoptionRate < 0.50) {
        return "low adoption";
    }

    if (customer.adoptionRate < 0.80) {
        return "moderate adoption";
    }

    return "high adoption";
}

for (const customer of customers) {
    console.log(
        customer.id,
        sizeSegment(customer),
        adoptionSegment(customer)
    );
}


// ============================================================================
// 5. CUSTOMER HEALTH SCORE
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("5. Customer health score");
console.log("=".repeat(78));

function customerHealthScore(customer) {
    const satisfaction = customer.satisfaction / 10;
    const adoption = customer.adoptionRate;
    const engagement = Math.min(customer.sessionsPerMonth / 60, 1);
    const supportQuality = 1 - Math.min(customer.supportTickets / 20, 1);

    return 100 * (
        0.30 * satisfaction +
        0.35 * adoption +
        0.20 * engagement +
        0.15 * supportQuality
    );
}

for (const customer of customers) {
    console.log(
        customer.id,
        "health=",
        customerHealthScore(customer).toFixed(1)
    );
}


// ============================================================================
// 6. CUSTOMER JOURNEY
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("6. Customer journey");
console.log("=".repeat(78));

const journey = [
    {
        stage: "awareness",
        channel: "search",
        action: "reads comparison article",
        emotion: "curious",
        friction: 2
    },
    {
        stage: "consideration",
        channel: "website",
        action: "reviews documentation",
        emotion: "interested",
        friction: 4
    },
    {
        stage: "evaluation",
        channel: "demo",
        action: "tests workflow",
        emotion: "uncertain",
        friction: 7
    },
    {
        stage: "purchase",
        channel: "sales",
        action: "reviews contract",
        emotion: "cautious",
        friction: 8
    },
    {
        stage: "onboarding",
        channel: "application",
        action: "imports data",
        emotion: "frustrated",
        friction: 9
    }
];

function frictionLevel(friction) {
    if (friction < 3) return "low";
    if (friction < 7) return "medium";
    return "high";
}

for (const point of journey) {
    console.log(
        point.stage,
        point.channel,
        "friction=",
        frictionLevel(point.friction)
    );
}


// ============================================================================
// 7. QUALITATIVE RESEARCH CODING
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("7. Qualitative research coding");
console.log("=".repeat(78));

const stopWords = new Set([
    "the", "a", "an", "and", "is", "to", "of", "for",
    "with", "we", "our", "it", "this", "that", "in", "on"
]);

function tokenize(text) {
    return text
        .toLowerCase()
        .match(/[a-z]+/g)
        ?.filter(word => !stopWords.has(word)) || [];
}

function wordFrequency(texts) {
    const counts = new Map();

    for (const text of texts) {
        for (const word of tokenize(text)) {
            counts.set(word, (counts.get(word) || 0) + 1);
        }
    }

    return [...counts.entries()]
        .sort((a, b) => b[1] - a[1]);
}

const interviews = [
    "The setup takes too long and our team needs simpler onboarding.",
    "We need reliable reports because manual reporting takes too long.",
    "Security approval is important before we can purchase the system.",
    "The reporting workflow is useful but configuration is difficult."
];

console.log(wordFrequency(interviews).slice(0, 10));


// ============================================================================
// 8. THEMATIC ANALYSIS
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("8. Thematic analysis");
console.log("=".repeat(78));

const themes = {
    onboarding: new Set(["setup", "onboarding", "configuration"]),
    reporting: new Set(["reports", "reporting", "workflow"]),
    security: new Set(["security", "approval"]),
    efficiency: new Set(["long", "manual", "simpler"])
};

function detectThemes(text) {
    const words = new Set(tokenize(text));
    const detected = {};

    for (const [theme, keywords] of Object.entries(themes)) {
        const count = [...keywords].filter(word => words.has(word)).length;

        if (count > 0) {
            detected[theme] = count;
        }
    }

    return detected;
}

for (const quote of interviews) {
    console.log(quote);
    console.log(detectThemes(quote));
}


// ============================================================================
// 9. RFM ANALYSIS
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("9. RFM customer analysis");
console.log("=".repeat(78));

const rfm = [
    { id: "C001", recencyDays: 7, frequency: 24, monetary: 120000 },
    { id: "C002", recencyDays: 64, frequency: 5, monetary: 18000 },
    { id: "C003", recencyDays: 3, frequency: 38, monetary: 310000 },
    { id: "C004", recencyDays: 21, frequency: 13, monetary: 42000 },
    { id: "C005", recencyDays: 10, frequency: 29, monetary: 220000 }
];

function percentileRank(values, value) {
    if (values.length === 0) {
        throw new Error("Values cannot be empty.");
    }

    return values.filter(candidate => candidate <= value).length / values.length;
}

function rfmScore(record, records) {
    const recency = records.map(item => -item.recencyDays);
    const frequency = records.map(item => item.frequency);
    const monetary = records.map(item => item.monetary);

    const score = values => Math.max(
        1,
        Math.min(5, Math.floor(percentileRank(values, values[0]) * 5))
    );

    const recencyValue = -record.recencyDays;

    return {
        r: Math.max(1, Math.min(5, Math.floor(
            percentileRank(recency, recencyValue) * 5
        ))),
        f: Math.max(1, Math.min(5, Math.floor(
            percentileRank(frequency, record.frequency) * 5
        ))),
        m: Math.max(1, Math.min(5, Math.floor(
            percentileRank(monetary, record.monetary) * 5
        )))
    };
}

for (const record of rfm) {
    console.log(record.id, rfmScore(record, rfm));
}


// ============================================================================
// 10. COSINE SIMILARITY
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("10. Persona similarity");
console.log("=".repeat(78));

function cosineSimilarity(a, b) {
    const keys = new Set([...Object.keys(a), ...Object.keys(b)]);

    let dot = 0;
    let normA = 0;
    let normB = 0;

    for (const key of keys) {
        const valueA = a[key] || 0;
        const valueB = b[key] || 0;

        dot += valueA * valueB;
        normA += valueA * valueA;
        normB += valueB * valueB;
    }

    if (normA === 0 || normB === 0) {
        return 0;
    }

    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

const personaVectorA = {
    efficiency: 1,
    reporting: 0.9,
    security: 0.2,
    cost: 0.4
};

const personaVectorB = {
    efficiency: 0.8,
    reporting: 0.7,
    security: 0.3,
    cost: 0.5
};

console.log(
    "Similarity:",
    cosineSimilarity(personaVectorA, personaVectorB).toFixed(3)
);


// ============================================================================
// 11. SIMPLE SEGMENT CLUSTERING
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("11. Nearest-centroid segmentation");
console.log("=".repeat(78));

function euclideanDistance(a, b) {
    if (a.length !== b.length) {
        throw new Error("Points must have the same dimensionality.");
    }

    return Math.sqrt(
        a.reduce((sum, value, index) => {
            return sum + Math.pow(value - b[index], 2);
        }, 0)
    );
}

function nearestCentroid(point, centroids) {
    if (centroids.length === 0) {
        throw new Error("At least one centroid is required.");
    }

    let bestIndex = 0;
    let bestDistance = Infinity;

    centroids.forEach((centroid, index) => {
        const distance = euclideanDistance(point, centroid);

        if (distance < bestDistance) {
            bestDistance = distance;
            bestIndex = index;
        }
    });

    return bestIndex;
}

const points = [
    [0.9, 0.8],
    [0.8, 0.7],
    [0.2, 0.3],
    [0.1, 0.2],
    [0.6, 0.7]
];

const centroids = [
    [0.8, 0.8],
    [0.2, 0.2]
];

for (const point of points) {
    console.log(
        point,
        "cluster=",
        nearestCentroid(point, centroids)
    );
}


// ============================================================================
// 12. SENTIMENT HEURISTIC
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("12. Feedback sentiment heuristic");
console.log("=".repeat(78));

const positiveWords = new Set([
    "easy", "useful", "fast", "reliable", "excellent",
    "helpful", "clear", "good", "valuable"
]);

const negativeWords = new Set([
    "slow", "difficult", "bad", "confusing", "frustrating",
    "expensive", "broken", "hard", "problem"
]);

function sentimentScore(text) {
    const words = tokenize(text);

    const positive = words.filter(word => positiveWords.has(word)).length;
    const negative = words.filter(word => negativeWords.has(word)).length;

    if (positive + negative === 0) {
        return 0;
    }

    return (positive - negative) / (positive + negative);
}

const feedback = [
    "The product is easy and useful but setup is difficult.",
    "Reports are reliable and fast.",
    "The workflow is confusing and slow."
];

for (const text of feedback) {
    console.log(
        sentimentScore(text).toFixed(2),
        text
    );
}


// ============================================================================
// 13. CUSTOMER VALUE
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("13. Customer lifetime value");
console.log("=".repeat(78));

function estimatedLifetimeValue(
    averageOrderValue,
    purchasesPerYear,
    expectedYears,
    grossMargin
) {
    if (
        averageOrderValue < 0 ||
        purchasesPerYear < 0 ||
        expectedYears < 0 ||
        grossMargin < 0
    ) {
        throw new RangeError("LTV inputs cannot be negative.");
    }

    return (
        averageOrderValue *
        purchasesPerYear *
        expectedYears *
        grossMargin
    );
}

console.log(
    "Estimated LTV:",
    estimatedLifetimeValue(1000, 6, 4, 0.70)
);


// ============================================================================
// 14. ASYNCHRONOUS CUSTOMER RESEARCH
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("14. Asynchronous research aggregation");
console.log("=".repeat(78));

/*
 * JavaScript is particularly useful when customer understanding is connected
 * to web applications, APIs, event streams, dashboards, and asynchronous
 * research systems.
 *
 * These functions simulate external sources without requiring network access.
 */

function delay(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function loadSurveyData() {
    await delay(20);

    return [
        { id: "C001", satisfaction: 8.4 },
        { id: "C002", satisfaction: 6.1 },
        { id: "C003", satisfaction: 9.0 }
    ];
}

async function loadUsageData() {
    await delay(10);

    return [
        { id: "C001", sessions: 38 },
        { id: "C002", sessions: 14 },
        { id: "C003", sessions: 61 }
    ];
}

async function loadSupportData() {
    await delay(15);

    return [
        { id: "C001", tickets: 2 },
        { id: "C002", tickets: 8 },
        { id: "C003", tickets: 1 }
    ];
}

async function buildUnifiedCustomerView() {
    /*
     * Promise.all executes independent data retrieval concurrently from the
     * perspective of the application. In a real system, these could be API
     * requests to separate services.
     */
    const [
        surveys,
        usage,
        support
    ] = await Promise.all([
        loadSurveyData(),
        loadUsageData(),
        loadSupportData()
    ]);

    const usageMap = new Map(
        usage.map(record => [record.id, record])
    );

    const supportMap = new Map(
        support.map(record => [record.id, record])
    );

    return surveys.map(survey => ({
        id: survey.id,
        satisfaction: survey.satisfaction,
        sessions: usageMap.get(survey.id)?.sessions ?? 0,
        tickets: supportMap.get(survey.id)?.tickets ?? 0
    }));
}


// ============================================================================
// 15. ERROR HANDLING AND VALIDATION
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("15. Validation and failure handling");
console.log("=".repeat(78));

function validateCustomer(customer) {
    const errors = [];

    if (!customer.id || customer.id.trim() === "") {
        errors.push("missing customer ID");
    }

    if (customer.companySize < 0) {
        errors.push("company size cannot be negative");
    }

    if (customer.annualValue < 0) {
        errors.push("annual value cannot be negative");
    }

    if (customer.satisfaction < 0 || customer.satisfaction > 10) {
        errors.push("satisfaction must be between 0 and 10");
    }

    if (customer.adoptionRate < 0 || customer.adoptionRate > 1) {
        errors.push("adoption rate must be between 0 and 1");
    }

    return errors;
}

for (const customer of customers) {
    console.log(customer.id, validateCustomer(customer));
}


// ============================================================================
// 16. EXPERIMENT ANALYSIS
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("16. Customer experiment analysis");
console.log("=".repeat(78));

function conversionRate(visitors, conversions) {
    if (visitors <= 0) {
        throw new RangeError("Visitors must be positive.");
    }

    if (conversions < 0 || conversions > visitors) {
        throw new RangeError("Conversions must be within visitor count.");
    }

    return conversions / visitors;
}

const control = conversionRate(5000, 450);
const variant = conversionRate(5000, 525);

const absoluteLift = variant - control;
const relativeLift = absoluteLift / control;

console.log("Control:", (control * 100).toFixed(2) + "%");
console.log("Variant:", (variant * 100).toFixed(2) + "%");
console.log(
    "Absolute lift:",
    (absoluteLift * 100).toFixed(2),
    "percentage points"
);
console.log(
    "Relative lift:",
    (relativeLift * 100).toFixed(2) + "%"
);


// ============================================================================
// 17. CUSTOMER SEGMENT AGGREGATION
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("17. Segment aggregation");
console.log("=".repeat(78));

function average(values) {
    if (values.length === 0) {
        return 0;
    }

    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function summarizeSegments(customerList) {
    const groups = new Map();

    for (const customer of customerList) {
        const segment = sizeSegment(customer);

        if (!groups.has(segment)) {
            groups.set(segment, []);
        }

        groups.get(segment).push(customer);
    }

    const result = {};

    for (const [segment, members] of groups) {
        result[segment] = {
            customers: members.length,
            averageValue: average(
                members.map(customer => customer.annualValue)
            ),
            averageSatisfaction: average(
                members.map(customer => customer.satisfaction)
            ),
            averageAdoption: average(
                members.map(customer => customer.adoptionRate)
            )
        };
    }

    return result;
}

console.log(
    JSON.stringify(
        summarizeSegments(customers),
        null,
        2
    )
);


// ============================================================================
// 18. PRIVACY-AWARE DATA CATALOG
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("18. Privacy-aware customer data catalog");
console.log("=".repeat(78));

const dataCatalog = [
    {
        field: "customerId",
        purpose: "account identification",
        sensitivity: "low",
        retentionDays: 3650
    },
    {
        field: "usageEvents",
        purpose: "product improvement",
        sensitivity: "medium",
        retentionDays: 730
    },
    {
        field: "supportTopic",
        purpose: "service improvement",
        sensitivity: "medium",
        retentionDays: 730
    },
    {
        field: "email",
        purpose: "account communication",
        sensitivity: "personal",
        retentionDays: 3650
    }
];

for (const field of dataCatalog) {
    console.log(
        field.field,
        "| purpose=",
        field.purpose,
        "| sensitivity=",
        field.sensitivity
    );
}


// ============================================================================
// 19. CUSTOMER INSIGHT OBJECT
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("19. Unified customer insight");
console.log("=".repeat(78));

class CustomerInsight {
    constructor(customer, primaryNeed, friction, evidenceCount) {
        this.customerId = customer.id;
        this.segment = `${sizeSegment(customer)} / ${adoptionSegment(customer)}`;
        this.healthScore = customerHealthScore(customer);
        this.primaryNeed = primaryNeed;
        this.friction = friction;
        this.evidenceCount = evidenceCount;
    }

    riskLevel() {
        if (this.healthScore < 40 || this.friction >= 8) {
            return "high";
        }

        if (this.healthScore < 70 || this.friction >= 5) {
            return "medium";
        }

        return "low";
    }
}

const insights = customers.slice(0, 3).map((customer, index) => {
    const needs = [
        "simpler reporting",
        "easier onboarding",
        "security controls"
    ];

    const friction = [4, 8.5, 3][index];

    return new CustomerInsight(
        customer,
        needs[index],
        friction,
        8 + index
    );
});

for (const insight of insights) {
    console.log({
        customerId: insight.customerId,
        segment: insight.segment,
        health: insight.healthScore.toFixed(1),
        need: insight.primaryNeed,
        risk: insight.riskLevel()
    });
}


// ============================================================================
// 20. PERFORMANCE CONSIDERATIONS
// ============================================================================

console.log("\n" + "=".repeat(78));
console.log("20. Performance considerations");
console.log("=".repeat(78));

/*
 * For large customer datasets:
 *
 * 1. Prefer Maps for repeated key-based lookups.
 * 2. Avoid repeatedly scanning an entire array inside another loop when an
 *    index can be built once.
 * 3. Process event streams incrementally when data cannot fit in memory.
 * 4. Use database-side aggregation when appropriate.
 * 5. Avoid storing unnecessary high-cardinality data in browser memory.
 * 6. Debounce expensive UI filtering and search operations.
 *
 * The following comparison demonstrates indexed lookup conceptually.
 */

const customerIndex = new Map(
    customers.map(customer => [customer.id, customer])
);

console.log(
    "Indexed lookup C003:",
    customerIndex.get("C003")
);


// ============================================================================
// 21. RUN ASYNCHRONOUS PIPELINE
// ============================================================================

async function main() {
    console.log("\n" + "=".repeat(78));
    console.log("21. Unified asynchronous customer pipeline");
    console.log("=".repeat(78));

    try {
        const unifiedData = await buildUnifiedCustomerView();

        for (const record of unifiedData) {
            console.log(
                record.id,
                "| satisfaction:",
                record.satisfaction,
                "| sessions:",
                record.sessions,
                "| tickets:",
                record.tickets
            );
        }

        console.log("\nCustomer understanding JavaScript examples completed.");
    } catch (error) {
        /*
         * Production systems should distinguish validation errors, network
         * failures, authorization failures, rate limits, and unexpected
         * programming errors rather than exposing raw error details to users.
         */
        console.error("Customer pipeline failed:", error.message);
        process.exitCode = 1;
    }
}

main();
