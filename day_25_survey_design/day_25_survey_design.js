"use strict";

/*
 * Survey Design: Practical JavaScript Study
 *
 * This file complements the Python implementation by demonstrating:
 * - Survey schemas
 * - Question validation
 * - Conditional logic
 * - Browser-oriented form behavior
 * - Event-driven validation
 * - Response-quality checks
 * - Likert and NPS calculations
 * - Data cleaning
 * - Cross-tabulation
 * - Asynchronous submission simulation
 * - Debouncing
 * - Object-oriented survey modeling
 * - Functional data-processing patterns
 * - Performance and security considerations
 *
 * The file runs in Node.js without external packages.
 *
 * It also contains browser-compatible functions. In a browser, the
 * DOM-dependent examples can be connected to HTML form controls.
 */

// =============================================================================
// 1. BASIC SURVEY CONCEPTS
// =============================================================================

console.log("=".repeat(78));
console.log("SURVEY DESIGN WITH JAVASCRIPT");
console.log("=".repeat(78));

const surveyObjective = {
    id: "OBJ-01",
    description: "Measure customer satisfaction with an online service.",
    metric: "Mean satisfaction score on a 1-5 scale",
    population: "Customers who used the service during the last 90 days"
};

console.log("\nObjective:");
console.log(surveyObjective);


// =============================================================================
// 2. QUESTION TYPES AND SCHEMAS
// =============================================================================

class SurveyQuestion {
    constructor({
        id,
        text,
        type,
        required = false,
        options = [],
        min = null,
        max = null
    }) {
        this.id = id;
        this.text = text;
        this.type = type;
        this.required = required;
        this.options = options;
        this.min = min;
        this.max = max;
    }

    validate(answer) {
        if (
            this.required &&
            (answer === null ||
                answer === undefined ||
                answer === "")
        ) {
            return {
                valid: false,
                message: "This question is required."
            };
        }

        if (
            answer === null ||
            answer === undefined ||
            answer === ""
        ) {
            return {
                valid: true,
                message: "No answer provided."
            };
        }

        if (this.type === "singleChoice") {
            if (!this.options.includes(answer)) {
                return {
                    valid: false,
                    message: "Invalid option."
                };
            }
        }

        if (this.type === "multipleChoice") {
            if (!Array.isArray(answer)) {
                return {
                    valid: false,
                    message: "Expected an array of choices."
                };
            }

            const invalid = answer.filter(
                choice => !this.options.includes(choice)
            );

            if (invalid.length > 0) {
                return {
                    valid: false,
                    message: `Invalid choices: ${invalid.join(", ")}`
                };
            }
        }

        if (this.type === "scale") {
            if (
                typeof answer !== "number" ||
                !Number.isFinite(answer)
            ) {
                return {
                    valid: false,
                    message: "Scale response must be numeric."
                };
            }

            if (
                this.min !== null &&
                answer < this.min
            ) {
                return {
                    valid: false,
                    message: `Value must be at least ${this.min}.`
                };
            }

            if (
                this.max !== null &&
                answer > this.max
            ) {
                return {
                    valid: false,
                    message: `Value must be at most ${this.max}.`
                };
            }
        }

        if (this.type === "text") {
            if (typeof answer !== "string") {
                return {
                    valid: false,
                    message: "Text response must be a string."
                };
            }
        }

        return {
            valid: true,
            message: "Valid response."
        };
    }
}

const questions = [
    new SurveyQuestion({
        id: "Q1",
        text: "Which plan do you use?",
        type: "singleChoice",
        required: true,
        options: [
            "Free",
            "Basic",
            "Professional",
            "Enterprise"
        ]
    }),

    new SurveyQuestion({
        id: "Q2",
        text: "Which features have you used?",
        type: "multipleChoice",
        options: [
            "Dashboard",
            "Reports",
            "Automation",
            "API"
        ]
    }),

    new SurveyQuestion({
        id: "Q3",
        text: "How satisfied are you?",
        type: "scale",
        required: true,
        min: 1,
        max: 5
    }),

    new SurveyQuestion({
        id: "Q4",
        text: "What should we improve?",
        type: "text"
    })
];


// =============================================================================
// 3. RESPONSE VALIDATION
// =============================================================================

function validateSurveyResponse(questionList, answers) {
    const errors = [];

    for (const question of questionList) {
        const result = question.validate(answers[question.id]);

        if (!result.valid) {
            errors.push({
                questionId: question.id,
                message: result.message
            });
        }
    }

    return errors;
}

const sampleAnswers = {
    Q1: "Professional",
    Q2: ["Dashboard", "API"],
    Q3: 4,
    Q4: "Improve reporting speed."
};

console.log("\nSample validation:");
console.log(validateSurveyResponse(questions, sampleAnswers));


// =============================================================================
// 4. CONDITIONAL LOGIC
// =============================================================================

class BranchRule {
    constructor(sourceQuestionId, expectedValue, destinationQuestionId) {
        this.sourceQuestionId = sourceQuestionId;
        this.expectedValue = expectedValue;
        this.destinationQuestionId = destinationQuestionId;
    }

    matches(answers) {
        return answers[this.sourceQuestionId] === this.expectedValue;
    }
}

const branchRules = [
    new BranchRule("Q1", "Enterprise", "Q_ENTERPRISE"),
    new BranchRule("Q1", "Free", "Q_UPGRADE")
];

function determineNextQuestion(rules, answers) {
    for (const rule of rules) {
        if (rule.matches(answers)) {
            return rule.destinationQuestionId;
        }
    }

    return null;
}

console.log(
    "\nNext question:",
    determineNextQuestion(branchRules, sampleAnswers)
);


// =============================================================================
// 5. LIKERT SCALE ANALYSIS
// =============================================================================

function mean(values) {
    if (values.length === 0) {
        throw new Error("Cannot calculate mean of an empty array.");
    }

    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function median(values) {
    if (values.length === 0) {
        throw new Error("Cannot calculate median of an empty array.");
    }

    const sorted = [...values].sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);

    if (sorted.length % 2 === 0) {
        return (sorted[middle - 1] + sorted[middle]) / 2;
    }

    return sorted[middle];
}

function frequencyDistribution(values) {
    const frequencies = new Map();

    for (const value of values) {
        frequencies.set(
            value,
            (frequencies.get(value) || 0) + 1
        );
    }

    return Object.fromEntries(frequencies);
}

function likertSummary(values) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new Error("A non-empty array is required.");
    }

    return {
        n: values.length,
        mean: mean(values),
        median: median(values),
        minimum: Math.min(...values),
        maximum: Math.max(...values),
        distribution: frequencyDistribution(values)
    };
}

const satisfactionScores = [4, 5, 3, 4, 4, 2, 5, 4, 3, 5];

console.log("\nLikert summary:");
console.log(likertSummary(satisfactionScores));


// =============================================================================
// 6. NPS
// =============================================================================

function calculateNPS(scores) {
    if (!Array.isArray(scores) || scores.length === 0) {
        throw new Error("At least one NPS score is required.");
    }

    if (
        scores.some(
            score =>
                !Number.isInteger(score) ||
                score < 0 ||
                score > 10
        )
    ) {
        throw new Error("NPS scores must be integers from 0 to 10.");
    }

    const promoters = scores.filter(score => score >= 9).length;
    const detractors = scores.filter(score => score <= 6).length;

    return (
        (promoters / scores.length) * 100 -
        (detractors / scores.length) * 100
    );
}

const npsScores = [10, 9, 8, 7, 6, 9, 10, 5, 8, 9];

console.log("\nNPS:", calculateNPS(npsScores));


// =============================================================================
// 7. RANKING DATA
// =============================================================================

function averageRankings(rankings) {
    const rankMap = new Map();

    for (const ranking of rankings) {
        ranking.forEach((item, index) => {
            if (!rankMap.has(item)) {
                rankMap.set(item, []);
            }

            rankMap.get(item).push(index + 1);
        });
    }

    const result = {};

    for (const [item, ranks] of rankMap.entries()) {
        result[item] = mean(ranks);
    }

    return result;
}

const rankings = [
    ["Speed", "Price", "Support", "Design"],
    ["Support", "Speed", "Design", "Price"],
    ["Speed", "Design", "Support", "Price"]
];

console.log("\nAverage rankings:");
console.log(averageRankings(rankings));


// =============================================================================
// 8. CROSS-TABULATION
// =============================================================================

function crossTabulate(rowValues, columnValues) {
    if (rowValues.length !== columnValues.length) {
        throw new Error(
            "Both arrays must have the same number of observations."
        );
    }

    const table = new Map();

    rowValues.forEach((rowValue, index) => {
        const columnValue = columnValues[index];

        if (!table.has(rowValue)) {
            table.set(rowValue, new Map());
        }

        const row = table.get(rowValue);
        row.set(
            columnValue,
            (row.get(columnValue) || 0) + 1
        );
    });

    const objectTable = {};

    for (const [rowValue, columns] of table.entries()) {
        objectTable[rowValue] = Object.fromEntries(columns);
    }

    return objectTable;
}

console.log("\nCross-tabulation:");

console.log(
    crossTabulate(
        [
            "Free",
            "Free",
            "Basic",
            "Basic",
            "Professional",
            "Professional"
        ],
        [
            "Satisfied",
            "Neutral",
            "Satisfied",
            "Dissatisfied",
            "Satisfied",
            "Neutral"
        ]
    )
);


// =============================================================================
// 9. DATA CLEANING
// =============================================================================

function cleanText(value) {
    if (value === null || value === undefined) {
        return null;
    }

    const normalized = String(value)
        .trim()
        .replace(/\s+/g, " ");

    return normalized === "" ? null : normalized;
}

function removeDuplicateRespondents(responses) {
    const seen = new Set();

    return responses.filter(response => {
        const id = response.respondentId;

        if (seen.has(id)) {
            return false;
        }

        seen.add(id);
        return true;
    });
}

const rawResponses = [
    {
        respondentId: "R1",
        Q3: 5,
        comment: "  Excellent    service  "
    },
    {
        respondentId: "R2",
        Q3: 4,
        comment: "Good"
    },
    {
        respondentId: "R1",
        Q3: 5,
        comment: "Duplicate"
    }
];

console.log("\nCleaned text:");
console.log(cleanText(rawResponses[0].comment));

console.log("\nDeduplicated responses:");
console.log(removeDuplicateRespondents(rawResponses));


// =============================================================================
// 10. RESPONSE QUALITY
// =============================================================================

function flagResponseQuality(response, minimumSeconds = 30) {
    const flags = [];

    if (response.completionSeconds < minimumSeconds) {
        flags.push("Unusually fast completion.");
    }

    if (!response.attentionCheckPassed) {
        flags.push("Attention check failed.");
    }

    if (response.duplicate) {
        flags.push("Potential duplicate.");
    }

    return flags;
}

const responseQualityExample = {
    respondentId: "R-001",
    completionSeconds: 17,
    attentionCheckPassed: true,
    duplicate: false
};

console.log(
    "\nResponse-quality flags:",
    flagResponseQuality(responseQualityExample)
);


// =============================================================================
// 11. SURVEY CLASS
// =============================================================================

class Survey {
    constructor({ title, purpose, population, questions }) {
        this.title = title;
        this.purpose = purpose;
        this.population = population;
        this.questions = questions;
    }

    validateResponse(answers) {
        return validateSurveyResponse(
            this.questions,
            answers
        );
    }

    requiredQuestionIds() {
        return this.questions
            .filter(question => question.required)
            .map(question => question.id);
    }

    getQuestion(id) {
        return this.questions.find(
            question => question.id === id
        ) || null;
    }
}

const customerSurvey = new Survey({
    title: "Customer Experience Survey",
    purpose: "Measure recent customer experience.",
    population: "Customers who used the service in the last 90 days.",
    questions
});

console.log(
    "\nRequired question IDs:",
    customerSurvey.requiredQuestionIds()
);


// =============================================================================
// 12. ASYNCHRONOUS SUBMISSION
// =============================================================================

function simulateServerSubmission(payload) {
    /*
     * A Promise models asynchronous network behavior without requiring a
     * real server. In a production application this could be replaced with
     * fetch() to an authenticated HTTPS endpoint.
     */
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (!payload || typeof payload !== "object") {
                reject(new Error("Invalid submission payload."));
                return;
            }

            resolve({
                success: true,
                submissionId: `SUB-${Date.now()}`,
                receivedAt: new Date().toISOString()
            });
        }, 50);
    });
}

async function submitSurvey(survey, answers) {
    const errors = survey.validateResponse(answers);

    if (errors.length > 0) {
        throw new Error(
            `Validation failed: ${JSON.stringify(errors)}`
        );
    }

    const result = await simulateServerSubmission({
        survey: survey.title,
        answers
    });

    return result;
}


// =============================================================================
// 13. BROWSER-SIDE EVENT HANDLING
// =============================================================================

function attachFormValidation(formElement, questionList) {
    /*
     * This function is intentionally safe to call only when a browser DOM
     * exists. It demonstrates event-driven validation used by web forms.
     */
    if (!formElement || typeof formElement.addEventListener !== "function") {
        throw new TypeError("A valid form element is required.");
    }

    formElement.addEventListener("submit", event => {
        const formData = new FormData(formElement);
        const answers = {};

        for (const question of questionList) {
            if (question.type === "multipleChoice") {
                answers[question.id] = formData.getAll(question.id);
            } else {
                answers[question.id] = formData.get(question.id);
            }
        }

        const errors = validateSurveyResponse(
            questionList,
            answers
        );

        if (errors.length > 0) {
            event.preventDefault();

            console.error(
                "Survey validation errors:",
                errors
            );
        }
    });
}

if (typeof document !== "undefined") {
    /*
     * Browser-only code is guarded so that Node.js execution remains valid.
     */
    const form = document.querySelector("#survey-form");

    if (form) {
        attachFormValidation(form, questions);
    }
}


// =============================================================================
// 14. DEBOUNCING
// =============================================================================

function debounce(callback, delayMilliseconds) {
    let timerId = null;

    return function debouncedFunction(...args) {
        clearTimeout(timerId);

        timerId = setTimeout(() => {
            callback.apply(this, args);
        }, delayMilliseconds);
    };
}

const debouncedSearch = debounce(query => {
    console.log("Searching survey metadata for:", query);
}, 100);

debouncedSearch("customer");
debouncedSearch("customer satisfaction");


// =============================================================================
// 15. OBJECTIVE -> QUESTION TRACEABILITY
// =============================================================================

const traceabilityMatrix = [
    {
        objective: "Measure satisfaction",
        questions: ["Q3"]
    },
    {
        objective: "Identify feature usage",
        questions: ["Q2"]
    },
    {
        objective: "Collect improvement suggestions",
        questions: ["Q4"]
    }
];

console.log("\nTraceability matrix:");
console.table(traceabilityMatrix);


// =============================================================================
// 16. MISSING DATA
// =============================================================================

function missingRate(values) {
    if (!Array.isArray(values) || values.length === 0) {
        return 0;
    }

    const missingCount = values.filter(
        value => value === null || value === undefined || value === ""
    ).length;

    return (missingCount / values.length) * 100;
}

console.log(
    "\nMissing rate:",
    missingRate([5, 4, null, 3, null, 5])
);


// =============================================================================
// 17. SAMPLE SIZE
// =============================================================================

function approximateSampleSize({
    z,
    marginOfError,
    proportion = 0.5
}) {
    if (z <= 0) {
        throw new Error("z must be positive.");
    }

    if (!(marginOfError > 0 && marginOfError < 1)) {
        throw new Error(
            "marginOfError must be between 0 and 1."
        );
    }

    if (!(proportion > 0 && proportion < 1)) {
        throw new Error(
            "proportion must be between 0 and 1."
        );
    }

    const variance = proportion * (1 - proportion);

    return Math.ceil(
        (z * z * variance) /
        (marginOfError * marginOfError)
    );
}

console.log(
    "\nApproximate sample size:",
    approximateSampleSize({
        z: 1.96,
        marginOfError: 0.05
    })
);


// =============================================================================
// 18. CONFIDENCE INTERVAL
// =============================================================================

function proportionConfidenceInterval(
    proportion,
    sampleSize,
    z = 1.96
) {
    if (
        proportion < 0 ||
        proportion > 1 ||
        sampleSize <= 0
    ) {
        throw new Error("Invalid proportion or sample size.");
    }

    const standardError = Math.sqrt(
        (proportion * (1 - proportion)) /
        sampleSize
    );

    const margin = z * standardError;

    return {
        lower: Math.max(0, proportion - margin),
        upper: Math.min(1, proportion + margin)
    };
}

console.log(
    "\nApproximate confidence interval:",
    proportionConfidenceInterval(0.60, 400)
);


// =============================================================================
// 19. DESIGN EFFECT
// =============================================================================

function designEffect(clusterSize, intraclassCorrelation) {
    if (clusterSize < 1) {
        throw new Error("Cluster size must be at least 1.");
    }

    if (
        intraclassCorrelation < 0 ||
        intraclassCorrelation > 1
    ) {
        throw new Error("ICC must be between 0 and 1.");
    }

    return (
        1 +
        (clusterSize - 1) *
        intraclassCorrelation
    );
}

console.log(
    "\nCluster design effect:",
    designEffect(10, 0.10)
);


// =============================================================================
// 20. RESPONSE RATE
// =============================================================================

function responseRate(completed, eligibleInvited) {
    if (eligibleInvited <= 0) {
        throw new Error(
            "Eligible invited count must be positive."
        );
    }

    if (
        completed < 0 ||
        completed > eligibleInvited
    ) {
        throw new Error(
            "Completed responses are invalid."
        );
    }

    return (completed / eligibleInvited) * 100;
}

console.log(
    "\nResponse rate:",
    responseRate(320, 1000).toFixed(1) + "%"
);


// =============================================================================
// 21. COMPLETE CASE STUDY
// =============================================================================

const caseStudyQuestions = [
    new SurveyQuestion({
        id: "S1",
        text: "Have you used the service during the last 30 days?",
        type: "singleChoice",
        required: true,
        options: ["Yes", "No"]
    }),

    new SurveyQuestion({
        id: "S2",
        text: "How satisfied are you?",
        type: "scale",
        required: true,
        min: 1,
        max: 5
    }),

    new SurveyQuestion({
        id: "S3",
        text: "Which areas need improvement?",
        type: "multipleChoice",
        options: [
            "Speed",
            "Reliability",
            "Support",
            "Pricing",
            "Features"
        ]
    }),

    new SurveyQuestion({
        id: "S4",
        text: "How likely are you to recommend the service?",
        type: "scale",
        required: true,
        min: 0,
        max: 10
    }),

    new SurveyQuestion({
        id: "S5",
        text: "What is the most important improvement?",
        type: "text"
    })
];

const caseStudySurvey = new Survey({
    title: "Service Experience Study",
    purpose: "Measure recent customer experience.",
    population: "Customers who used the service during the last 30 days.",
    questions: caseStudyQuestions
});

const caseStudyResponses = [
    {
        respondentId: "R1",
        S1: "Yes",
        S2: 5,
        S3: ["Speed"],
        S4: 10,
        S5: "Keep the service fast."
    },
    {
        respondentId: "R2",
        S1: "Yes",
        S2: 4,
        S3: ["Support", "Reliability"],
        S4: 8,
        S5: "Improve support response time."
    },
    {
        respondentId: "R3",
        S1: "No",
        S2: null,
        S3: [],
        S4: 4,
        S5: "Improve onboarding."
    },
    {
        respondentId: "R4",
        S1: "Yes",
        S2: 3,
        S3: ["Pricing"],
        S4: 6,
        S5: "Make pricing clearer."
    }
];

console.log("\nCase-study validation:");

for (const response of caseStudyResponses) {
    console.log(
        response.respondentId,
        caseStudySurvey.validateResponse(response)
    );
}


// =============================================================================
// 22. CASE STUDY ANALYSIS
// =============================================================================

const recentUsers = caseStudyResponses.filter(
    response => response.S1 === "Yes"
);

const caseSatisfaction = recentUsers
    .map(response => response.S2)
    .filter(value => typeof value === "number");

const caseNPS = caseStudyResponses
    .map(response => response.S4)
    .filter(value => typeof value === "number");

const improvementFrequency = {};

for (const response of recentUsers) {
    for (const area of response.S3) {
        improvementFrequency[area] =
            (improvementFrequency[area] || 0) + 1;
    }
}

console.log("\nCase-study mean satisfaction:");
console.log(mean(caseSatisfaction));

console.log("\nCase-study NPS:");
console.log(calculateNPS(caseNPS));

console.log("\nImprovement frequency:");
console.log(improvementFrequency);


// =============================================================================
// 23. SECURITY CONSIDERATIONS
// =============================================================================

const securityPrinciples = [
    "Use HTTPS for survey submission.",
    "Do not store authentication secrets in survey responses.",
    "Collect only necessary personal information.",
    "Avoid exposing raw respondent records to public browser code.",
    "Validate data on both client and server sides.",
    "Treat client-side validation as a usability feature, not a security boundary.",
    "Sanitize or safely encode respondent-entered text before rendering it as HTML.",
    "Apply access controls to administrative survey data.",
    "Define data retention and deletion policies.",
    "Review third-party form-platform privacy and data-processing settings."
];

console.log("\nSecurity principles:");

for (const principle of securityPrinciples) {
    console.log("-", principle);
}


// =============================================================================
// 24. GOOGLE FORMS / TYPEFORM DESIGN MAPPING
// =============================================================================

const platformDesignMapping = {
    "Google Forms": [
        "Required questions",
        "Sections",
        "Multiple-choice questions",
        "Checkboxes",
        "Linear scales",
        "Grid questions",
        "Response collection",
        "Spreadsheet-oriented analysis workflows"
    ],

    "Typeform": [
        "One-question-at-a-time interaction",
        "Conditional logic",
        "Branching",
        "Question piping",
        "Interactive form flows",
        "Personalized respondent paths"
    ]
};

console.log("\nPlatform design mapping:");
console.dir(platformDesignMapping, { depth: null });


// =============================================================================
// 25. RUN ASYNC SUBMISSION EXAMPLE
// =============================================================================

async function main() {
    console.log("\nSubmitting validated survey response...");

    try {
        const result = await submitSurvey(
            customerSurvey,
            sampleAnswers
        );

        console.log("Submission result:", result);
    } catch (error) {
        console.error("Submission failed:", error.message);
    }

    console.log("\nCore design principles:");

    const principles = [
        "Start with measurable research objectives.",
        "Define the target population and eligibility criteria.",
        "Choose sampling based on the intended inference.",
        "Use one clear concept per question.",
        "Avoid leading and double-barreled wording.",
        "Use appropriate measurement scales.",
        "Pilot test before full deployment.",
        "Monitor response quality and nonresponse.",
        "Document cleaning and analysis rules.",
        "Protect respondent privacy.",
        "Interpret results within design limitations."
    ];

    principles.forEach(
        (principle, index) =>
            console.log(`${index + 1}. ${principle}`)
    );
}

main().catch(error => {
    console.error("Unexpected application error:", error);
    process.exitCode = 1;
});
