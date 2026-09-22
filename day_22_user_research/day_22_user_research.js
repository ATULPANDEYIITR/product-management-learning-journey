/*
 * USER RESEARCH
 * =============
 *
 * A complete JavaScript study file demonstrating practical user-research
 * concepts from beginner to advanced level.
 *
 * The examples are designed to run in Node.js without external packages.
 *
 * Topics:
 * - Research planning
 * - Research questions
 * - Participant screening
 * - Interviews
 * - Qualitative coding
 * - Thematic analysis
 * - Usability testing
 * - Survey analysis
 * - Cross-tabulation
 * - NPS
 * - Bias
 * - Triangulation
 * - Research quality
 * - Ethics and privacy
 * - Async research-data processing
 * - Validation
 * - Error handling
 * - Performance considerations
 * - Evidence-based findings
 * - End-to-end research workflow
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. BASIC OUTPUT HELPERS
// -----------------------------------------------------------------------------

function section(title) {
    console.log("\n" + "=".repeat(80));
    console.log(title.toUpperCase());
    console.log("=".repeat(80));
}

function subsection(title) {
    console.log(`\n--- ${title} ---`);
}


// -----------------------------------------------------------------------------
// 2. FOUNDATIONS
// -----------------------------------------------------------------------------

function demonstrateFoundations() {
    section("1. User Research Foundations");

    const concepts = new Map([
        [
            "User research",
            "Systematic study of users, behavior, needs, goals, expectations, and experiences."
        ],
        [
            "Qualitative research",
            "Research focused on meanings, motivations, experiences, explanations, and context."
        ],
        [
            "Quantitative research",
            "Research focused on measurable quantities, frequencies, distributions, and relationships."
        ],
        [
            "Research question",
            "A specific question the study is designed to answer."
        ],
        [
            "Research hypothesis",
            "A testable expectation about an outcome or relationship."
        ],
        [
            "Finding",
            "An observation supported by collected evidence."
        ],
        [
            "Insight",
            "An interpretation that explains why an important pattern may exist."
        ]
    ]);

    for (const [term, definition] of concepts) {
        console.log(`${term}: ${definition}`);
    }
}


// -----------------------------------------------------------------------------
// 3. RESEARCH PLAN
// -----------------------------------------------------------------------------

class ResearchPlan {
    constructor({
        problem,
        objective,
        population,
        questions,
        methods
    }) {
        if (!problem || !objective || !population) {
            throw new Error("Research plan requires problem, objective, and population.");
        }

        this.problem = problem;
        this.objective = objective;
        this.population = population;
        this.questions = questions;
        this.methods = methods;
    }

    display() {
        section("2. Research Plan");

        console.log(`Problem: ${this.problem}`);
        console.log(`Objective: ${this.objective}`);
        console.log(`Population: ${this.population}`);

        subsection("Research Questions");

        this.questions.forEach((question, index) => {
            console.log(`${index + 1}. ${question.question}`);
            console.log(`   Method: ${question.method}`);
            console.log(`   Evidence: ${question.evidence}`);
        });

        subsection("Methods");

        for (const method of this.methods) {
            console.log(`- ${method}`);
        }
    }
}

const researchPlan = new ResearchPlan({
    problem: "Users struggle to complete an online service request.",
    objective: "Understand the source, frequency, and consequences of workflow friction.",
    population: "Adults who have used similar online services recently.",
    questions: [
        {
            question: "Where do users experience the greatest friction?",
            method: "Usability testing",
            evidence: "Behavior, errors, completion, and time."
        },
        {
            question: "Why does this friction occur?",
            method: "Semi-structured interviews",
            evidence: "Mental models, expectations, motivations, explanations."
        },
        {
            question: "How common are the reported problems?",
            method: "Survey",
            evidence: "Frequencies and distributions."
        }
    ],
    methods: [
        "Screening",
        "Interviews",
        "Usability testing",
        "Survey",
        "Qualitative analysis",
        "Quantitative analysis",
        "Triangulation"
    ]
});


// -----------------------------------------------------------------------------
// 4. PARTICIPANT SCREENING
// -----------------------------------------------------------------------------

class Participant {
    constructor(id, age, experience, usageFrequency, goal, consented = true) {
        this.id = id;
        this.age = age;
        this.experience = experience;
        this.usageFrequency = usageFrequency;
        this.goal = goal;
        this.consented = consented;
    }
}

function isEligible(participant) {
    return (
        participant.consented &&
        participant.age >= 18 &&
        participant.age <= 70 &&
        participant.usageFrequency >= 1 &&
        ["beginner", "intermediate", "advanced"].includes(participant.experience)
    );
}

function demonstrateScreening() {
    section("3. Participant Screening");

    const participants = [
        new Participant("P01", 24, "beginner", 2, "submit request"),
        new Participant("P02", 31, "intermediate", 8, "track request"),
        new Participant("P03", 45, "advanced", 12, "submit request"),
        new Participant("P04", 17, "beginner", 5, "submit request", false),
        new Participant("P05", 38, "intermediate", 4, "find information")
    ];

    const eligible = participants.filter(isEligible);

    console.log(`Candidates: ${participants.length}`);
    console.log(`Eligible: ${eligible.length}`);

    eligible.forEach(participant => {
        console.log(
            `${participant.id}: age=${participant.age}, ` +
            `experience=${participant.experience}, ` +
            `frequency=${participant.usageFrequency}`
        );
    });

    return eligible;
}


// -----------------------------------------------------------------------------
// 5. INTERVIEW DATA
// -----------------------------------------------------------------------------

const interviewExcerpts = [
    {
        participantId: "P01",
        text: "I did not know which button would actually submit the request.",
        context: "submission"
    },
    {
        participantId: "P02",
        text: "The status page uses words that I do not normally use.",
        context: "status"
    },
    {
        participantId: "P03",
        text: "I expected the next step to be visible after I uploaded the document.",
        context: "upload"
    },
    {
        participantId: "P05",
        text: "I kept checking whether the file had really been uploaded.",
        context: "upload"
    },
    {
        participantId: "P01",
        text: "The form asks for information I thought the organization already had.",
        context: "form"
    }
];

function tokenize(text) {
    return text
        .toLowerCase()
        .match(/[a-zA-Z']+/g) ?? [];
}

function calculateWordFrequency(excerpts) {
    const stopWords = new Set([
        "the", "a", "an", "i", "to", "and", "of", "that", "was",
        "is", "it", "for", "after", "my", "had", "would", "be",
        "what", "did", "not", "which", "have"
    ]);

    const frequencies = new Map();

    for (const excerpt of excerpts) {
        for (const word of tokenize(excerpt.text)) {
            if (stopWords.has(word)) {
                continue;
            }

            frequencies.set(
                word,
                (frequencies.get(word) ?? 0) + 1
            );
        }
    }

    return frequencies;
}

function demonstrateInterviewAnalysis() {
    section("4. Interview Analysis");

    interviewExcerpts.forEach(excerpt => {
        console.log(
            `${excerpt.participantId} [${excerpt.context}]: ${excerpt.text}`
        );
    });

    subsection("Keyword Frequency");

    const frequencies = calculateWordFrequency(interviewExcerpts);

    [...frequencies.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .forEach(([word, count]) => {
            console.log(`${word}: ${count}`);
        });

    console.log(
        "\nKeyword frequency is descriptive. It is not equivalent to thematic analysis."
    );
}


// -----------------------------------------------------------------------------
// 6. QUALITATIVE CODING
// -----------------------------------------------------------------------------

const codeRules = {
    unclear_call_to_action: ["which button", "submit the request"],
    unclear_status_language: ["status page", "words that i do not"],
    missing_system_feedback: ["whether the file", "really been uploaded"],
    unclear_next_step: ["next step", "after i uploaded"],
    unnecessary_data_request: ["information i thought", "already had"]
};

function codeInterviewExcerpt(excerpt) {
    const text = excerpt.text.toLowerCase();
    const codes = [];

    for (const [code, patterns] of Object.entries(codeRules)) {
        if (patterns.some(pattern => text.includes(pattern))) {
            codes.push(code);
        }
    }

    return {
        ...excerpt,
        codes
    };
}

function performThematicAnalysis(excerpts) {
    const themes = new Map();

    for (const excerpt of excerpts) {
        const coded = codeInterviewExcerpt(excerpt);

        for (const code of coded.codes) {
            if (!themes.has(code)) {
                themes.set(code, []);
            }

            themes.get(code).push(coded.participantId);
        }
    }

    return themes;
}

function demonstrateThematicAnalysis() {
    section("5. Thematic Analysis");

    const themes = performThematicAnalysis(interviewExcerpts);

    for (const [theme, participants] of themes) {
        console.log(
            `${theme}: ${participants.length} evidence item(s), ` +
            `participants=${[...new Set(participants)].join(", ")}`
        );
    }
}


// -----------------------------------------------------------------------------
// 7. USABILITY TESTING
// -----------------------------------------------------------------------------

const usabilityResults = [
    {
        participantId: "P01",
        task: "Submit Request",
        completed: true,
        timeSeconds: 145,
        errors: 2,
        satisfaction: 4
    },
    {
        participantId: "P02",
        task: "Submit Request",
        completed: true,
        timeSeconds: 102,
        errors: 1,
        satisfaction: 4
    },
    {
        participantId: "P03",
        task: "Submit Request",
        completed: true,
        timeSeconds: 88,
        errors: 0,
        satisfaction: 5
    },
    {
        participantId: "P05",
        task: "Submit Request",
        completed: false,
        timeSeconds: 240,
        errors: 4,
        satisfaction: 2
    }
];

function average(numbers) {
    if (numbers.length === 0) {
        return 0;
    }

    return numbers.reduce((sum, value) => sum + value, 0) / numbers.length;
}

function calculateTaskSuccessRate(results) {
    if (results.length === 0) {
        return 0;
    }

    return results.filter(result => result.completed).length / results.length;
}

function demonstrateUsabilityMetrics() {
    section("6. Usability Testing Metrics");

    const times = usabilityResults.map(result => result.timeSeconds);
    const errors = usabilityResults.map(result => result.errors);

    console.log(
        `Task success rate: ${(calculateTaskSuccessRate(usabilityResults) * 100).toFixed(1)}%`
    );
    console.log(`Average task time: ${average(times).toFixed(1)} seconds`);
    console.log(`Average errors: ${average(errors).toFixed(2)}`);

    usabilityResults.forEach(result => {
        console.log(
            `${result.participantId}: completed=${result.completed}, ` +
            `time=${result.timeSeconds}s, errors=${result.errors}`
        );
    });
}


// -----------------------------------------------------------------------------
// 8. SURVEY ANALYSIS
// -----------------------------------------------------------------------------

const surveyResponses = [
    {
        id: "S01",
        ageGroup: "18-29",
        satisfaction: 3,
        ease: 3,
        recommendation: 6,
        uploadProblem: true,
        statusProblem: true
    },
    {
        id: "S02",
        ageGroup: "30-44",
        satisfaction: 4,
        ease: 4,
        recommendation: 8,
        uploadProblem: false,
        statusProblem: true
    },
    {
        id: "S03",
        ageGroup: "45-59",
        satisfaction: 2,
        ease: 2,
        recommendation: 4,
        uploadProblem: true,
        statusProblem: true
    },
    {
        id: "S04",
        ageGroup: "30-44",
        satisfaction: 5,
        ease: 5,
        recommendation: 9,
        uploadProblem: false,
        statusProblem: false
    },
    {
        id: "S05",
        ageGroup: "18-29",
        satisfaction: 3,
        ease: 3,
        recommendation: 7,
        uploadProblem: true,
        statusProblem: false
    },
    {
        id: "S06",
        ageGroup: "45-59",
        satisfaction: 2,
        ease: 2,
        recommendation: 5,
        uploadProblem: true,
        statusProblem: true
    },
    {
        id: "S07",
        ageGroup: "30-44",
        satisfaction: 4,
        ease: 4,
        recommendation: 8,
        uploadProblem: false,
        statusProblem: true
    },
    {
        id: "S08",
        ageGroup: "60+",
        satisfaction: 3,
        ease: 3,
        recommendation: 6,
        uploadProblem: true,
        statusProblem: true
    }
];

function calculateNPS(responses) {
    if (responses.length === 0) {
        return 0;
    }

    const promoters = responses.filter(r => r.recommendation >= 9).length;
    const detractors = responses.filter(r => r.recommendation <= 6).length;

    return (
        (promoters / responses.length) * 100 -
        (detractors / responses.length) * 100
    );
}

function demonstrateSurveyAnalysis() {
    section("7. Survey Analysis");

    const satisfaction = surveyResponses.map(r => r.satisfaction);
    const ease = surveyResponses.map(r => r.ease);

    const uploadRate =
        surveyResponses.filter(r => r.uploadProblem).length /
        surveyResponses.length;

    const statusRate =
        surveyResponses.filter(r => r.statusProblem).length /
        surveyResponses.length;

    console.log(`Responses: ${surveyResponses.length}`);
    console.log(`Mean satisfaction: ${average(satisfaction).toFixed(2)}/5`);
    console.log(`Mean ease of use: ${average(ease).toFixed(2)}/5`);
    console.log(`Upload-problem rate: ${(uploadRate * 100).toFixed(1)}%`);
    console.log(`Status-problem rate: ${(statusRate * 100).toFixed(1)}%`);
    console.log(`NPS: ${calculateNPS(surveyResponses).toFixed(1)}`);
}


// -----------------------------------------------------------------------------
// 9. CROSS-TABULATION
// -----------------------------------------------------------------------------

function crossTabulate(data, categoryKey, booleanKey) {
    const table = new Map();

    for (const row of data) {
        const category = row[categoryKey];

        if (!table.has(category)) {
            table.set(category, {
                participants: 0,
                affected: 0
            });
        }

        const record = table.get(category);

        record.participants += 1;

        if (row[booleanKey]) {
            record.affected += 1;
        }
    }

    for (const record of table.values()) {
        record.rate =
            record.participants === 0
                ? 0
                : record.affected / record.participants;
    }

    return table;
}

function demonstrateCrossTabulation() {
    section("8. Cross-Tabulation");

    const table = crossTabulate(
        surveyResponses,
        "ageGroup",
        "uploadProblem"
    );

    for (const [group, result] of table) {
        console.log(
            `${group}: participants=${result.participants}, ` +
            `affected=${result.affected}, ` +
            `rate=${(result.rate * 100).toFixed(1)}%`
        );
    }
}


// -----------------------------------------------------------------------------
// 10. ASYNCHRONOUS RESEARCH DATA PROCESSING
// -----------------------------------------------------------------------------

function loadResearchDataset() {
    /*
     * Real research systems often retrieve data from APIs, databases,
     * survey platforms, or secure storage. This Promise simulates I/O
     * without requiring an external service.
     */
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(surveyResponses);
        }, 20);
    });
}

async function performAsyncResearchAnalysis() {
    section("9. Asynchronous Research Data Processing");

    const data = await loadResearchDataset();

    const averageSatisfaction = average(
        data.map(response => response.satisfaction)
    );

    console.log(`Loaded ${data.length} survey responses asynchronously.`);
    console.log(`Average satisfaction: ${averageSatisfaction.toFixed(2)}`);
}


// -----------------------------------------------------------------------------
// 11. VALIDATION
// -----------------------------------------------------------------------------

function validateSurveyResponse(response) {
    const errors = [];

    if (typeof response.satisfaction !== "number") {
        errors.push("satisfaction must be numeric");
    } else if (response.satisfaction < 1 || response.satisfaction > 5) {
        errors.push("satisfaction must be between 1 and 5");
    }

    if (typeof response.recommendation !== "number") {
        errors.push("recommendation must be numeric");
    } else if (
        response.recommendation < 0 ||
        response.recommendation > 10
    ) {
        errors.push("recommendation must be between 0 and 10");
    }

    return {
        valid: errors.length === 0,
        errors
    };
}

function demonstrateValidation() {
    section("10. Research Data Validation");

    const validResponse = {
        satisfaction: 4,
        recommendation: 8
    };

    const invalidResponse = {
        satisfaction: 9,
        recommendation: -2
    };

    console.log("Valid response:", validateSurveyResponse(validResponse));
    console.log("Invalid response:", validateSurveyResponse(invalidResponse));
}


// -----------------------------------------------------------------------------
// 12. RESEARCH BIAS
// -----------------------------------------------------------------------------

function demonstrateBias() {
    section("11. Research Bias");

    const risks = [
        {
            name: "Selection bias",
            mechanism: "The sample differs systematically from the target population.",
            mitigation: "Use explicit population and recruitment criteria."
        },
        {
            name: "Leading-question bias",
            mechanism: "Question wording encourages a particular response.",
            mitigation: "Use neutral, open-ended wording."
        },
        {
            name: "Confirmation bias",
            mechanism: "Researchers disproportionately notice supporting evidence.",
            mitigation: "Record contradictory evidence and test alternative explanations."
        },
        {
            name: "Recall bias",
            mechanism: "Participants do not accurately remember previous behavior.",
            mitigation: "Ask about recent concrete experiences where possible."
        }
    ];

    risks.forEach(risk => {
        console.log(`\n${risk.name}`);
        console.log(`Mechanism: ${risk.mechanism}`);
        console.log(`Mitigation: ${risk.mitigation}`);
    });
}


// -----------------------------------------------------------------------------
// 13. TRIANGULATION
// -----------------------------------------------------------------------------

function demonstrateTriangulation() {
    section("12. Triangulation");

    const evidence = [
        {
            method: "Interview",
            observation: "Participants describe uncertainty after uploading files."
        },
        {
            method: "Usability test",
            observation: "Participants repeatedly check upload status."
        },
        {
            method: "Survey",
            observation: "Several respondents report upload problems."
        }
    ];

    evidence.forEach(item => {
        console.log(`${item.method}: ${item.observation}`);
    });

    console.log(
        "\nThe evidence converges around uncertainty after upload, " +
        "but each method measures a different aspect of the problem."
    );
}


// -----------------------------------------------------------------------------
// 14. RESEARCH REPOSITORY
// -----------------------------------------------------------------------------

class ResearchRepository {
    constructor() {
        this.artifacts = new Map();
    }

    add(artifact) {
        if (!artifact.id || !artifact.type || !artifact.content) {
            throw new Error("Research artifact requires id, type, and content.");
        }

        if (this.artifacts.has(artifact.id)) {
            throw new Error(`Artifact '${artifact.id}' already exists.`);
        }

        this.artifacts.set(artifact.id, artifact);
    }

    findByTag(tag) {
        return [...this.artifacts.values()]
            .filter(artifact => artifact.tags?.includes(tag));
    }

    countByType() {
        const counts = new Map();

        for (const artifact of this.artifacts.values()) {
            counts.set(
                artifact.type,
                (counts.get(artifact.type) ?? 0) + 1
            );
        }

        return counts;
    }
}

function demonstrateRepository() {
    section("13. Research Repository");

    const repository = new ResearchRepository();

    repository.add({
        id: "INT-001",
        type: "interview",
        content: "Participant describes upload uncertainty.",
        tags: ["upload", "feedback"]
    });

    repository.add({
        id: "UT-001",
        type: "usability",
        content: "Participant checks upload status repeatedly.",
        tags: ["upload", "behavior"]
    });

    repository.add({
        id: "SUR-001",
        type: "survey",
        content: "Participant reports upload problem.",
        tags: ["upload", "quantitative"]
    });

    console.log("Counts by type:", Object.fromEntries(repository.countByType()));

    console.log("Upload-related evidence:");

    for (const artifact of repository.findByTag("upload")) {
        console.log(`- ${artifact.id}: ${artifact.content}`);
    }

    try {
        repository.add({
            id: "INT-001",
            type: "interview",
            content: "Duplicate artifact."
        });
    } catch (error) {
        console.log(`Handled expected error: ${error.message}`);
    }
}


// -----------------------------------------------------------------------------
// 15. EVIDENCE STRENGTH
// -----------------------------------------------------------------------------

function calculateEvidenceStrength({
    directObservation,
    methodologicalAlignment,
    triangulation,
    sampleAdequacy
}) {
    /*
     * This is an illustrative heuristic, not a scientifically universal
     * scoring system. Research quality should not be reduced to one number.
     */
    return (
        directObservation * 0.30 +
        methodologicalAlignment * 0.25 +
        triangulation * 0.25 +
        sampleAdequacy * 0.20
    );
}

function demonstrateEvidenceAssessment() {
    section("14. Evidence Assessment");

    const strength = calculateEvidenceStrength({
        directObservation: 0.9,
        methodologicalAlignment: 0.8,
        triangulation: 0.85,
        sampleAdequacy: 0.65
    });

    console.log(
        `Illustrative evidence-strength heuristic: ${(strength * 100).toFixed(1)}%`
    );

    console.log(
        "The score is a teaching device rather than a replacement for methodological judgment."
    );
}


// -----------------------------------------------------------------------------
// 16. EDGE CASES
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    section("15. Edge Cases");

    console.log(
        `Empty success-rate dataset: ${calculateTaskSuccessRate([])}`
    );

    console.log(
        `Empty average: ${average([])}`
    );

    try {
        validateSurveyResponse({
            satisfaction: "high",
            recommendation: 15
        });
    } catch (error) {
        console.log(`Unexpected validation failure: ${error.message}`);
    }

    console.log(
        "Important real-world edge cases include missing responses, duplicate "
        + "participants, participant withdrawal, inconsistent answers, incomplete "
        + "sessions, invalid timestamps, and contradictory qualitative evidence."
    );
}


// -----------------------------------------------------------------------------
// 17. ADVANCED RESEARCH METHODS
// -----------------------------------------------------------------------------

function demonstrateAdvancedMethods() {
    section("16. Advanced Research Methods");

    const methods = [
        [
            "Diary study",
            "Collects participant-recorded experiences over time."
        ],
        [
            "Contextual inquiry",
            "Studies users in their natural environment while examining work context."
        ],
        [
            "Card sorting",
            "Examines how users group and label information."
        ],
        [
            "Tree testing",
            "Evaluates information findability within an information hierarchy."
        ],
        [
            "Longitudinal study",
            "Observes change over an extended period."
        ],
        [
            "Concept testing",
            "Evaluates reactions to proposed concepts."
        ],
        [
            "A/B testing",
            "Compares variants using a defined outcome under controlled assignment."
        ],
        [
            "Mixed-method research",
            "Combines qualitative and quantitative evidence intentionally."
        ]
    ];

    methods.forEach(([name, definition]) => {
        console.log(`${name}: ${definition}`);
    });
}


// -----------------------------------------------------------------------------
// 18. JAVASCRIPT-SPECIFIC FUNCTIONAL DATA PROCESSING
// -----------------------------------------------------------------------------

function groupBy(data, keyFunction) {
    return data.reduce((groups, item) => {
        const key = keyFunction(item);

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(item);
        return groups;
    }, new Map());
}

function demonstrateFunctionalProcessing() {
    section("17. Functional Data Processing");

    const byAgeGroup = groupBy(
        surveyResponses,
        response => response.ageGroup
    );

    for (const [group, responses] of byAgeGroup) {
        const satisfaction = average(
            responses.map(response => response.satisfaction)
        );

        console.log(
            `${group}: n=${responses.length}, ` +
            `mean satisfaction=${satisfaction.toFixed(2)}`
        );
    }
}


// -----------------------------------------------------------------------------
// 19. PERFORMANCE
// -----------------------------------------------------------------------------

function demonstratePerformance() {
    section("18. Performance Considerations");

    const observations = Array.from(
        { length: 100000 },
        (_, index) => ({
            id: index,
            code: ["upload", "status", "navigation", "form"][index % 4]
        })
    );

    console.time("Counting 100,000 observations");

    const counts = new Map();

    for (const observation of observations) {
        counts.set(
            observation.code,
            (counts.get(observation.code) ?? 0) + 1
        );
    }

    console.timeEnd("Counting 100,000 observations");

    console.log("Code frequencies:", Object.fromEntries(counts));

    console.log(
        "For larger datasets, streaming, indexed databases, efficient serialization, "
        + "pagination, and server-side aggregation may reduce memory and processing cost."
    );
}


// -----------------------------------------------------------------------------
// 20. ETHICS AND PRIVACY
// -----------------------------------------------------------------------------

function demonstrateEthics() {
    section("19. Ethics and Privacy");

    const principles = [
        "Obtain informed consent.",
        "Explain the purpose and scope of data collection.",
        "Collect only necessary personal information.",
        "Protect research data using appropriate access controls.",
        "Separate identity from analytical data when possible.",
        "Define retention and deletion policies.",
        "Avoid unnecessary deception.",
        "Report contradictory evidence honestly.",
        "Do not fabricate or manipulate research results."
    ];

    principles.forEach(principle => console.log(`- ${principle}`));
}


// -----------------------------------------------------------------------------
// 21. END-TO-END REPORT
// -----------------------------------------------------------------------------

function generateResearchReport() {
    const successRate = calculateTaskSuccessRate(usabilityResults);
    const meanTime = average(
        usabilityResults.map(result => result.timeSeconds)
    );

    const uploadProblemRate =
        surveyResponses.filter(response => response.uploadProblem).length /
        surveyResponses.length;

    return {
        researchObjective:
            "Understand friction in an online service-request workflow.",

        behavioralEvidence: {
            taskSuccessRate: successRate,
            meanTaskTimeSeconds: meanTime
        },

        surveyEvidence: {
            uploadProblemRate
        },

        qualitativeEvidence: [
            "Uncertainty about upload completion",
            "Unclear status terminology",
            "Unclear next steps",
            "Concern about navigation"
        ],

        interpretation:
            "Multiple evidence sources indicate a potential workflow-feedback problem.",

        limitation:
            "The dataset is simulated and cannot be treated as representative evidence."
    };
}

function demonstrateReport() {
    section("20. Research Report");

    const report = generateResearchReport();

    console.log(JSON.stringify(report, null, 2));
}


// -----------------------------------------------------------------------------
// 22. MAIN
// -----------------------------------------------------------------------------

async function main() {
    demonstrateFoundations();

    researchPlan.display();

    demonstrateScreening();
    demonstrateInterviewAnalysis();
    demonstrateThematicAnalysis();

    demonstrateUsabilityMetrics();
    demonstrateSurveyAnalysis();
    demonstrateCrossTabulation();

    await performAsyncResearchAnalysis();

    demonstrateValidation();
    demonstrateBias();
    demonstrateTriangulation();

    demonstrateRepository();
    demonstrateEvidenceAssessment();
    demonstrateEdgeCases();

    demonstrateAdvancedMethods();
    demonstrateFunctionalProcessing();
    demonstratePerformance();

    demonstrateEthics();
    demonstrateReport();

    section("Research Study Complete");
    console.log(
        "The program demonstrated an end-to-end user-research workflow "
        + "using executable JavaScript examples."
    );
}

main().catch(error => {
    console.error("Research program failed:", error);
    process.exitCode = 1;
});
