/*
 * USER PERSONAS
 *
 * A practical JavaScript study of:
 * - Persona creation
 * - Demographics
 * - Behaviors
 * - Goals
 * - Frustrations
 * - Jobs
 * - Motivations
 * - Evidence
 * - Segmentation
 * - Scenario modeling
 * - Feature relevance
 * - Validation
 * - Serialization
 *
 * Run with:
 *   node user-personas.js
 *
 * The examples use standard JavaScript only.
 */

"use strict";


// ---------------------------------------------------------------------------
// 1. BASIC PERSONA OBJECT
// ---------------------------------------------------------------------------

const learnerPersona = {
    name: "Aarav",
    archetype: "Time-Constrained Learner",

    description:
        "A learner who wants practical technical knowledge while balancing " +
        "academic and professional responsibilities.",

    demographics: {
        ageRange: "20-28",
        location: "Urban India",
        occupation: "Graduate student / early-career professional",
        education: "Undergraduate or postgraduate"
    },

    behaviors: [
        "Searches for practical explanations before starting a task.",
        "Compares options before selecting a tool.",
        "Uses a laptop for structured work.",
        "Uses a phone for quick research.",
        "Returns to products that reduce repetitive work."
    ],

    goals: [
        "Complete technical tasks accurately.",
        "Learn concepts efficiently.",
        "Build evidence of practical competence."
    ],

    frustrations: [
        {
            description: "Unclear instructions",
            severity: 8,
            frequency: 8
        },
        {
            description: "Unnecessary workflow complexity",
            severity: 7,
            frequency: 6
        }
    ],

    jobs: [
        {
            type: "functional",
            description: "Understand a concept well enough to apply it.",
            importance: 9,
            frequency: 8
        },
        {
            type: "emotional",
            description: "Feel confident that the result is correct.",
            importance: 8,
            frequency: 7
        }
    ],

    motivations: [
        {
            category: "mastery",
            description: "Develop demonstrable competence.",
            strength: 9
        },
        {
            category: "convenience",
            description: "Reduce unnecessary effort.",
            strength: 8
        }
    ],

    evidence: [
        {
            source: "Interview study",
            level: "reported",
            statement: "Participants requested practical examples.",
            sampleSize: 18
        },
        {
            source: "Usage analytics",
            level: "observed",
            statement: "Long workflows correlated with abandonment.",
            sampleSize: 1200
        }
    ],

    technologyComfort: 8,
    priceSensitivity: 7
};

console.log("PERSONA");
console.log(JSON.stringify(learnerPersona, null, 2));


// ---------------------------------------------------------------------------
// 2. SIMPLE PERSONA VALIDATION
// ---------------------------------------------------------------------------

function validatePersona(persona) {
    const errors = [];

    if (!persona.name || !persona.name.trim()) {
        errors.push("Persona name is required.");
    }

    if (!persona.archetype || !persona.archetype.trim()) {
        errors.push("Persona archetype is required.");
    }

    if (!Array.isArray(persona.behaviors) || persona.behaviors.length === 0) {
        errors.push("At least one behavioral observation is required.");
    }

    if (!Array.isArray(persona.goals) || persona.goals.length === 0) {
        errors.push("At least one goal is required.");
    }

    if (!Array.isArray(persona.jobs) || persona.jobs.length === 0) {
        errors.push("At least one job is required.");
    }

    if (
        typeof persona.technologyComfort !== "number" ||
        persona.technologyComfort < 1 ||
        persona.technologyComfort > 10
    ) {
        errors.push("Technology comfort must be between 1 and 10.");
    }

    return errors;
}

console.log("\nVALIDATION");
console.log(validatePersona(learnerPersona));


// ---------------------------------------------------------------------------
// 3. GOAL CLASSIFICATION
// ---------------------------------------------------------------------------

function classifyGoal(goal) {
    const text = goal.toLowerCase();

    if (/\b(learn|understand|master)\b/.test(text)) {
        return "learning";
    }

    if (/\b(save|faster|efficient|time)\b/.test(text)) {
        return "efficiency";
    }

    if (/\b(career|job|income|professional)\b/.test(text)) {
        return "career";
    }

    if (/\b(safe|security|risk)\b/.test(text)) {
        return "security";
    }

    return "general";
}

console.log("\nGOAL CLASSIFICATION");

for (const goal of learnerPersona.goals) {
    console.log(`${goal} -> ${classifyGoal(goal)}`);
}


// ---------------------------------------------------------------------------
// 4. FRUSTRATION IMPACT
// ---------------------------------------------------------------------------

function frustrationImpact(frustration) {
    /*
     * A simple prioritization heuristic:
     *
     * impact = severity × frequency
     *
     * This does not prove which pain point matters most. It creates a
     * transparent quantitative hypothesis for further research.
     */
    return frustration.severity * frustration.frequency;
}

function rankFrustrations(persona) {
    return [...persona.frustrations]
        .map(item => ({
            ...item,
            impact: frustrationImpact(item)
        }))
        .sort((a, b) => b.impact - a.impact);
}

console.log("\nFRUSTRATION PRIORITIES");

for (const frustration of rankFrustrations(learnerPersona)) {
    console.log(
        `${frustration.description}: impact=${frustration.impact}`
    );
}


// ---------------------------------------------------------------------------
// 5. JOB PRIORITY
// ---------------------------------------------------------------------------

function jobPriority(job) {
    return job.importance * job.frequency;
}

console.log("\nJOB PRIORITIES");

for (const job of learnerPersona.jobs) {
    console.log(
        `[${job.type}] ${job.description} -> ${jobPriority(job)}`
    );
}


// ---------------------------------------------------------------------------
// 6. MOTIVATION ANALYSIS
// ---------------------------------------------------------------------------

function averageMotivation(persona) {
    if (persona.motivations.length === 0) {
        return 0;
    }

    const total = persona.motivations.reduce(
        (sum, motivation) => sum + motivation.strength,
        0
    );

    return total / persona.motivations.length;
}

console.log(
    "\nAverage motivation strength:",
    averageMotivation(learnerPersona).toFixed(2)
);


// ---------------------------------------------------------------------------
// 7. EVIDENCE QUALITY
// ---------------------------------------------------------------------------

const evidenceScores = {
    observed: 1.0,
    reported: 0.85,
    inferred: 0.55,
    assumed: 0.20
};

function evidenceStrength(persona) {
    if (persona.evidence.length === 0) {
        return 0;
    }

    const total = persona.evidence.reduce(
        (sum, evidence) =>
            sum + (evidenceScores[evidence.level] ?? 0),
        0
    );

    return total / persona.evidence.length;
}

console.log(
    "Evidence strength:",
    evidenceStrength(learnerPersona).toFixed(3)
);


// ---------------------------------------------------------------------------
// 8. BEHAVIORAL KEYWORD EXTRACTION
// ---------------------------------------------------------------------------

function extractKeywords(behaviors) {
    const stopWords = new Set([
        "with",
        "that",
        "this",
        "from",
        "they",
        "their",
        "when",
        "uses",
        "user",
        "often"
    ]);

    const keywords = new Set();

    for (const behavior of behaviors) {
        const words = behavior
            .toLowerCase()
            .match(/[a-z]{4,}/g) ?? [];

        for (const word of words) {
            if (!stopWords.has(word)) {
                keywords.add(word);
            }
        }
    }

    return keywords;
}

function jaccardSimilarity(firstSet, secondSet) {
    const union = new Set([...firstSet, ...secondSet]);

    if (union.size === 0) {
        return 1;
    }

    let intersection = 0;

    for (const value of firstSet) {
        if (secondSet.has(value)) {
            intersection += 1;
        }
    }

    return intersection / union.size;
}

console.log(
    "\nBehavior keyword set:",
    [...extractKeywords(learnerPersona.behaviors)]
);


// ---------------------------------------------------------------------------
// 9. SECOND PERSONA
// ---------------------------------------------------------------------------

const managerPersona = {
    name: "Meera",
    archetype: "Decision-Focused Manager",

    demographics: {
        ageRange: "30-45",
        occupation: "Product manager",
        location: "Large metropolitan area",
        education: "Graduate education"
    },

    behaviors: [
        "Reviews dashboards before weekly meetings.",
        "Requests evidence when metrics conflict.",
        "Delegates data preparation but validates key numbers."
    ],

    goals: [
        "Make decisions using reliable information.",
        "Reduce time spent preparing recurring reports."
    ],

    frustrations: [
        {
            description: "Fragmented information",
            severity: 9,
            frequency: 7
        },
        {
            description: "Manual reporting",
            severity: 8,
            frequency: 8
        }
    ],

    jobs: [
        {
            type: "functional",
            description: "Turn fragmented information into a decision-ready view.",
            importance: 10,
            frequency: 8
        },
        {
            type: "emotional",
            description: "Feel confident when explaining decisions.",
            importance: 9,
            frequency: 7
        },
        {
            type: "social",
            description: "Demonstrate disciplined decision-making.",
            importance: 7,
            frequency: 6
        }
    ],

    motivations: [
        {
            category: "achievement",
            description: "Wants measurable outcomes.",
            strength: 9
        },
        {
            category: "security",
            description: "Wants defensible decisions.",
            strength: 8
        }
    ],

    evidence: [
        {
            source: "Interview research",
            level: "reported",
            statement: "Managers described evidence verification as important.",
            sampleSize: 22
        }
    ],

    technologyComfort: 7,
    priceSensitivity: 5
};

console.log("\nSECOND PERSONA");
console.log(managerPersona.name);


// ---------------------------------------------------------------------------
// 10. PERSONA COMPARISON
// ---------------------------------------------------------------------------

function comparePersonas(first, second) {
    const firstKeywords = extractKeywords(first.behaviors);
    const secondKeywords = extractKeywords(second.behaviors);

    return {
        names: [first.name, second.name],

        goalCounts: [
            first.goals.length,
            second.goals.length
        ],

        jobPriority: [
            first.jobs.reduce((sum, job) => sum + jobPriority(job), 0),
            second.jobs.reduce((sum, job) => sum + jobPriority(job), 0)
        ],

        frustrationImpact: [
            first.frustrations.reduce(
                (sum, item) => sum + frustrationImpact(item),
                0
            ),
            second.frustrations.reduce(
                (sum, item) => sum + frustrationImpact(item),
                0
            )
        ],

        behavioralSimilarity: jaccardSimilarity(
            firstKeywords,
            secondKeywords
        ),

        technologyComfort: [
            first.technologyComfort,
            second.technologyComfort
        ],

        priceSensitivity: [
            first.priceSensitivity,
            second.priceSensitivity
        ]
    };
}

console.log(
    "\nPERSONA COMPARISON"
);

console.log(
    JSON.stringify(
        comparePersonas(learnerPersona, managerPersona),
        null,
        2
    )
);


// ---------------------------------------------------------------------------
// 11. RAW USER OBSERVATIONS
// ---------------------------------------------------------------------------

const researchObservations = [
    {
        id: "U001",
        behaviors: ["search", "compare", "practice"],
        goals: ["learn", "complete_task"],
        frustrations: ["unclear_instructions"],
        technologyComfort: 9,
        priceSensitivity: 8
    },
    {
        id: "U002",
        behaviors: ["search", "documentation", "practice"],
        goals: ["learn"],
        frustrations: ["time"],
        technologyComfort: 8,
        priceSensitivity: 8
    },
    {
        id: "U003",
        behaviors: ["dashboard", "reporting", "compare"],
        goals: ["decision", "save_time"],
        frustrations: ["fragmented_data"],
        technologyComfort: 7,
        priceSensitivity: 5
    },
    {
        id: "U004",
        behaviors: ["search", "compare", "documentation"],
        goals: ["learn", "complete_task"],
        frustrations: ["complexity"],
        technologyComfort: 9,
        priceSensitivity: 7
    }
];


// ---------------------------------------------------------------------------
// 12. RESEARCH AGGREGATION
// ---------------------------------------------------------------------------

function frequencyTable(records, property) {
    const table = new Map();

    for (const record of records) {
        for (const item of record[property]) {
            table.set(item, (table.get(item) ?? 0) + 1);
        }
    }

    return [...table.entries()]
        .sort((a, b) => b[1] - a[1]);
}

function aggregateResearch(records) {
    if (records.length === 0) {
        return {
            userCount: 0,
            commonBehaviors: [],
            commonGoals: [],
            commonFrustrations: []
        };
    }

    return {
        userCount: records.length,

        commonBehaviors: frequencyTable(records, "behaviors"),

        commonGoals: frequencyTable(records, "goals"),

        commonFrustrations: frequencyTable(
            records,
            "frustrations"
        ),

        averageTechnologyComfort:
            records.reduce(
                (sum, record) => sum + record.technologyComfort,
                0
            ) / records.length,

        averagePriceSensitivity:
            records.reduce(
                (sum, record) => sum + record.priceSensitivity,
                0
            ) / records.length
    };
}

console.log(
    "\nRESEARCH AGGREGATION"
);

console.log(
    JSON.stringify(
        aggregateResearch(researchObservations),
        null,
        2
    )
);


// ---------------------------------------------------------------------------
// 13. TRANSPARENT SEGMENTATION
// ---------------------------------------------------------------------------

function assignSegment(record) {
    /*
     * Transparent rules are useful for teaching and prototyping.
     * Production segmentation may use statistical methods, but the resulting
     * segments still require interpretation and validation.
     */

    if (
        record.goals.includes("decision") ||
        record.behaviors.includes("dashboard")
    ) {
        return "decision_oriented";
    }

    if (record.goals.includes("learn")) {
        return "learning_oriented";
    }

    return "other";
}

const segmentCounts = new Map();

for (const record of researchObservations) {
    const segment = assignSegment(record);

    segmentCounts.set(
        segment,
        (segmentCounts.get(segment) ?? 0) + 1
    );
}

console.log("\nSEGMENT COUNTS");

for (const [segment, count] of segmentCounts) {
    console.log(`${segment}: ${count}`);
}


// ---------------------------------------------------------------------------
// 14. PRODUCT FEATURES
// ---------------------------------------------------------------------------

const productFeatures = [
    {
        name: "Guided workflow",
        solves: [
            "unclear instructions",
            "complexity",
            "learn"
        ]
    },
    {
        name: "Saved workspace",
        solves: [
            "time",
            "save_time",
            "repetitive work"
        ]
    },
    {
        name: "Evidence panel",
        solves: [
            "uncertainty",
            "decision",
            "complete_task"
        ]
    }
];

function normalizedText(persona) {
    return [
        ...persona.behaviors,
        ...persona.goals,
        ...persona.frustrations.map(item => item.description),
        ...persona.jobs.map(job => job.description)
    ]
        .join(" ")
        .toLowerCase();
}

function featureRelevance(persona, feature) {
    const text = normalizedText(persona);

    let matches = 0;

    for (const solution of feature.solves) {
        if (text.includes(solution.toLowerCase())) {
            matches += 1;
        }
    }

    return matches / Math.max(1, feature.solves.length);
}

console.log("\nFEATURE RELEVANCE");

for (const feature of productFeatures) {
    console.log(
        `${feature.name}: ` +
        featureRelevance(learnerPersona, feature).toFixed(3)
    );
}


// ---------------------------------------------------------------------------
// 15. SCENARIO SIMULATION
// ---------------------------------------------------------------------------

function simulateScenario(persona, scenario, features) {
    const featureHypotheses = features
        .map(feature => ({
            feature: feature.name,
            relevance: featureRelevance(persona, feature)
        }))
        .sort((a, b) => b.relevance - a.relevance);

    return {
        persona: persona.name,
        scenario,
        goals: persona.goals,
        frustrations: rankFrustrations(persona)
            .map(item => item.description),
        featureHypotheses
    };
}

console.log("\nSCENARIO");

console.log(
    JSON.stringify(
        simulateScenario(
            learnerPersona,
            "The learner must complete a technical task under time pressure.",
            productFeatures
        ),
        null,
        2
    )
);


// ---------------------------------------------------------------------------
// 16. PERSONA QUALITY RISKS
// ---------------------------------------------------------------------------

function detectPersonaRisks(persona) {
    const risks = [];

    if (evidenceStrength(persona) < 0.5) {
        risks.push(
            "Evidence strength is weak; research validation is needed."
        );
    }

    if (persona.evidence.length < 2) {
        risks.push("Few evidence records are documented.");
    }

    if (persona.frustrations.length === 0) {
        risks.push("No frustrations are documented.");
    }

    if (persona.motivations.length === 0) {
        risks.push("No motivations are documented.");
    }

    return risks;
}

console.log("\nPERSONA RISKS");

console.log(
    detectPersonaRisks(learnerPersona)
);


// ---------------------------------------------------------------------------
// 17. ASSUMPTION DETECTION
// ---------------------------------------------------------------------------

function identifyAssumptions(persona) {
    return persona.evidence
        .filter(
            evidence =>
                evidence.level === "assumed" ||
                evidence.level === "inferred"
        )
        .map(evidence => evidence.statement);
}

console.log("\nASSUMPTIONS");

console.log(
    identifyAssumptions(learnerPersona)
);


// ---------------------------------------------------------------------------
// 18. PERSONA REPORT
// ---------------------------------------------------------------------------

function renderPersonaReport(persona) {
    const lines = [];

    lines.push(`PERSONA: ${persona.name}`);
    lines.push(`Archetype: ${persona.archetype}`);
    lines.push(`Description: ${persona.description}`);

    lines.push("");
    lines.push("DEMOGRAPHICS");

    for (const [key, value] of Object.entries(persona.demographics)) {
        lines.push(`- ${key}: ${value}`);
    }

    lines.push("");
    lines.push("BEHAVIORS");

    for (const behavior of persona.behaviors) {
        lines.push(`- ${behavior}`);
    }

    lines.push("");
    lines.push("GOALS");

    for (const goal of persona.goals) {
        lines.push(`- ${goal}`);
    }

    lines.push("");
    lines.push("FRUSTRATIONS");

    for (const frustration of persona.frustrations) {
        lines.push(
            `- ${frustration.description} ` +
            `(severity=${frustration.severity}, ` +
            `frequency=${frustration.frequency})`
        );
    }

    lines.push("");
    lines.push("JOBS");

    for (const job of persona.jobs) {
        lines.push(
            `- [${job.type}] ${job.description}`
        );
    }

    lines.push("");
    lines.push("MOTIVATIONS");

    for (const motivation of persona.motivations) {
        lines.push(
            `- [${motivation.category}] ${motivation.description} ` +
            `(strength=${motivation.strength}/10)`
        );
    }

    return lines.join("\n");
}

console.log("\nPERSONA REPORT");
console.log(renderPersonaReport(learnerPersona));


// ---------------------------------------------------------------------------
// 19. FACTORY FUNCTION
// ---------------------------------------------------------------------------

function createPersona({
    name,
    archetype,
    description,
    demographics = {},
    behaviors = [],
    goals = [],
    frustrations = [],
    jobs = [],
    motivations = [],
    evidence = [],
    technologyComfort = 5,
    priceSensitivity = 5
}) {
    return {
        name,
        archetype,
        description,
        demographics,
        behaviors,
        goals,
        frustrations,
        jobs,
        motivations,
        evidence,
        technologyComfort,
        priceSensitivity
    };
}

const generatedPersona = createPersona({
    name: "Operations Analyst",
    archetype: "Efficiency-Seeking Professional",
    description:
        "A professional who repeatedly transforms operational data into reports.",
    behaviors: [
        "Checks dashboards daily.",
        "Exports data for recurring reports.",
        "Uses shortcuts to reduce repetitive work."
    ],
    goals: [
        "Reduce reporting time.",
        "Avoid preventable data errors."
    ],
    jobs: [
        {
            type: "functional",
            description: "Prepare a reliable operational report.",
            importance: 9,
            frequency: 9
        }
    ],
    motivations: [
        {
            category: "convenience",
            description: "Reduce repetitive effort.",
            strength: 9
        }
    ]
});

console.log("\nFACTORY-CREATED PERSONA");
console.log(generatedPersona.name);


// ---------------------------------------------------------------------------
// 20. EDGE CASES
// ---------------------------------------------------------------------------

console.log("\nEDGE CASES");

console.log(
    "Empty Jaccard similarity:",
    jaccardSimilarity(new Set(), new Set())
);

console.log(
    "Empty motivation average:",
    averageMotivation({
        motivations: []
    })
);

console.log(
    "Empty research aggregation:",
    aggregateResearch([])
);

console.log(
    "Invalid persona:",
    validatePersona({
        name: "",
        archetype: "",
        behaviors: [],
        goals: [],
        jobs: [],
        technologyComfort: 12
    })
);


// ---------------------------------------------------------------------------
// 21. SERIALIZATION
// ---------------------------------------------------------------------------

const serializedPersona = JSON.stringify(
    learnerPersona,
    null,
    2
);

const restoredPersona = JSON.parse(serializedPersona);

console.log(
    "\nSERIALIZATION CHECK:",
    restoredPersona.name
);


// ---------------------------------------------------------------------------
// 22. INDUSTRY-STYLE CASE STUDY
// ---------------------------------------------------------------------------

const learningResearch = [
    {
        id: "L001",
        behaviors: ["search", "compare", "practice"],
        goals: ["learn", "career"],
        frustrations: ["time", "unclear_instructions"],
        technologyComfort: 9,
        priceSensitivity: 8
    },
    {
        id: "L002",
        behaviors: ["search", "practice", "documentation"],
        goals: ["learn", "complete_task"],
        frustrations: ["complexity"],
        technologyComfort: 8,
        priceSensitivity: 9
    },
    {
        id: "L003",
        behaviors: ["search", "compare", "practice"],
        goals: ["learn", "career"],
        frustrations: ["complexity"],
        technologyComfort: 9,
        priceSensitivity: 7
    },
    {
        id: "L004",
        behaviors: ["search", "documentation", "practice"],
        goals: ["learn", "complete_task"],
        frustrations: ["unclear_instructions"],
        technologyComfort: 8,
        priceSensitivity: 8
    }
];

const learningResearchSummary =
    aggregateResearch(learningResearch);

console.log("\nLEARNING PLATFORM CASE STUDY");

console.log(
    JSON.stringify(
        learningResearchSummary,
        null,
        2
    )
);


// ---------------------------------------------------------------------------
// 23. HYPOTHESIS GENERATION
// ---------------------------------------------------------------------------

function generateProductHypotheses(persona) {
    const hypotheses = [];

    for (const frustration of persona.frustrations) {
        hypotheses.push(
            `Reducing "${frustration.description}" may improve ` +
            `task completion for ${persona.name}.`
        );
    }

    for (const goal of persona.goals) {
        hypotheses.push(
            `A workflow supporting "${goal}" should be tested with ` +
            `${persona.name}.`
        );
    }

    return hypotheses;
}

console.log("\nPRODUCT HYPOTHESES");

for (const hypothesis of generateProductHypotheses(learnerPersona)) {
    console.log("-", hypothesis);
}


// ---------------------------------------------------------------------------
// 24. PRIVACY AND RESPONSIBLE PERSONA DESIGN
// ---------------------------------------------------------------------------

console.log(`
RESPONSIBLE PERSONA DESIGN

Use only product-relevant personal information.
Prefer ranges when exact values are unnecessary.
Do not treat demographic categories as deterministic predictors.
Separate observed evidence from assumptions.
Avoid fabricated quotations.
Protect raw research data.
Use aggregated information when individual-level detail is unnecessary.
Review whether persona attributes could create unfair exclusion.
`);


// ---------------------------------------------------------------------------
// 25. FINAL QUALITY REPORT
// ---------------------------------------------------------------------------

function qualityReport(persona) {
    const errors = validatePersona(persona);

    return {
        validStructure: errors.length === 0,
        errors,
        evidenceStrength: Number(
            evidenceStrength(persona).toFixed(3)
        ),
        behaviorCount: persona.behaviors.length,
        goalCount: persona.goals.length,
        frustrationCount: persona.frustrations.length,
        jobCount: persona.jobs.length,
        motivationCount: persona.motivations.length,
        assumptionCount: identifyAssumptions(persona).length
    };
}

console.log("\nFINAL QUALITY REPORT");

console.log(
    JSON.stringify(
        qualityReport(learnerPersona),
        null,
        2
    )
);
