"use strict";

/*
 * Customer Interviews: Practical JavaScript Study
 *
 * This file complements the Python study by demonstrating customer interview
 * concepts with JavaScript data structures, validation, functional processing,
 * classes, event-driven interaction, asynchronous simulation, and analytical
 * utilities.
 *
 * No external packages are required.
 */

// -----------------------------------------------------------------------------
// 1. BASIC DATA MODEL
// -----------------------------------------------------------------------------

class Participant {
    constructor(id, role, companySize, relevantExperience) {
        this.id = id;
        this.role = role;
        this.companySize = companySize;
        this.relevantExperience = relevantExperience;
    }

    isEligible(criteria) {
        if (!criteria || typeof criteria !== "object") {
            throw new TypeError("Eligibility criteria must be an object.");
        }

        if (criteria.role && this.role.toLowerCase() !== criteria.role.toLowerCase()) {
            return false;
        }

        if (
            criteria.companySize &&
            this.companySize.toLowerCase() !== criteria.companySize.toLowerCase()
        ) {
            return false;
        }

        return true;
    }
}


// -----------------------------------------------------------------------------
// 2. QUESTION DESIGN
// -----------------------------------------------------------------------------

const questionBank = [
    {
        text: "Tell me about the last time you followed up on an overdue invoice.",
        type: "behavioral",
        quality: "strong"
    },
    {
        text: "What happened after you contacted the customer?",
        type: "sequence",
        quality: "strong"
    },
    {
        text: "Don't you think automated reminders would save time?",
        type: "leading",
        quality: "weak"
    },
    {
        text: "Would you use an application that automatically sends reminders?",
        type: "hypothetical",
        quality: "limited"
    },
    {
        text: "How easy and fast was the process?",
        type: "double-barreled",
        quality: "weak"
    }
];

function inspectQuestion(question) {
    if (typeof question !== "string" || question.trim() === "") {
        throw new Error("A non-empty question is required.");
    }

    const lower = question.toLowerCase();
    const risks = [];

    if (
        lower.includes("don't you think") ||
        lower.includes("wouldn't you") ||
        lower.includes("would you agree") ||
        lower.includes("isn't it")
    ) {
        risks.push("leading wording");
    }

    if (
        lower.includes("would you use") ||
        lower.includes("would you buy") ||
        lower.includes("would you pay")
    ) {
        risks.push("hypothetical behavior");
    }

    if (lower.includes(" and ") || lower.includes(" or ")) {
        risks.push("possibly double-barreled");
    }

    if (question.trim().split(/\s+/).length > 30) {
        risks.push("long or complex wording");
    }

    return {
        question,
        risks,
        neutral: risks.length === 0
    };
}

function demonstrateQuestionDesign() {
    console.log("\n=== QUESTION DESIGN ===");

    for (const item of questionBank) {
        const result = inspectQuestion(item.text);

        console.log(`\nQuestion: ${item.text}`);
        console.log(`Type: ${item.type}`);
        console.log(`Risks: ${result.risks.length ? result.risks.join(", ") : "none detected"}`);
    }
}


// -----------------------------------------------------------------------------
// 3. QUESTION REWRITING
// -----------------------------------------------------------------------------

function rewriteLeadingQuestion(question) {
    const lower = question.toLowerCase();

    if (lower.includes("don't you think")) {
        return "What is your experience with this process?";
    }

    if (lower.includes("would you use")) {
        return "How do you currently handle this task?";
    }

    if (lower.includes("would you buy")) {
        return "How have you handled this problem in the past?";
    }

    return question;
}

function demonstrateRewriting() {
    console.log("\n=== NEUTRAL REWRITING ===");

    const examples = [
        "Don't you think automated reminders would save time?",
        "Would you use an application that automatically sends reminders?",
        "What do you currently do when an invoice becomes overdue?"
    ];

    for (const question of examples) {
        console.log(`Original: ${question}`);
        console.log(`Revision: ${rewriteLeadingQuestion(question)}`);
    }
}


// -----------------------------------------------------------------------------
// 4. INTERVIEW GUIDE
// -----------------------------------------------------------------------------

function createInterviewGuide(topic, behavior) {
    if (!topic || !behavior) {
        throw new Error("Both topic and behavior are required.");
    }

    return [
        `Can you tell me about your role in ${topic}?`,
        `When was the last time you ${behavior}?`,
        "Can you walk me through what happened?",
        "What happened next?",
        "What was difficult about that?",
        "What did you do when that happened?",
        "How often does this occur?",
        "What alternatives have you tried?",
        "Why did you keep or abandon those alternatives?",
        "What important part of this process have I not asked about?"
    ];
}

function demonstrateInterviewGuide() {
    console.log("\n=== INTERVIEW GUIDE ===");

    const guide = createInterviewGuide(
        "invoice management",
        "follow up on an overdue invoice"
    );

    guide.forEach((question, index) => {
        console.log(`${index + 1}. ${question}`);
    });
}


// -----------------------------------------------------------------------------
// 5. PROBING
// -----------------------------------------------------------------------------

const probeLibrary = {
    clarification: [
        "What do you mean by that?",
        "Can you give me a specific example?"
    ],
    sequence: [
        "What happened next?",
        "What happened immediately before that?"
    ],
    frequency: [
        "How often does that happen?",
        "When did this last happen?"
    ],
    impact: [
        "What effect did that have?",
        "What did you do because of that?"
    ],
    cause: [
        "What makes that difficult?",
        "Why is that important?"
    ]
};

function chooseProbe(answer) {
    const lower = answer.toLowerCase();

    if (lower.includes("usually") || lower.includes("often")) {
        return probeLibrary.frequency[1];
    }

    if (lower.includes("difficult") || lower.includes("problem")) {
        return probeLibrary.impact[0];
    }

    if (lower.includes("then") || lower.includes("after")) {
        return probeLibrary.sequence[0];
    }

    return probeLibrary.clarification[0];
}

function demonstrateProbing() {
    console.log("\n=== PROBING ===");

    const answers = [
        "Usually I check it once a week.",
        "The biggest problem is that customers forget.",
        "Then I send an email and wait.",
        "It is complicated."
    ];

    answers.forEach(answer => {
        console.log(`Participant: ${answer}`);
        console.log(`Probe: ${chooseProbe(answer)}\n`);
    });
}


// -----------------------------------------------------------------------------
// 6. EVIDENCE CLASSIFICATION
// -----------------------------------------------------------------------------

function classifyEvidence(statement) {
    if (typeof statement !== "string" || !statement.trim()) {
        throw new TypeError("Statement must be a non-empty string.");
    }

    const lower = statement.toLowerCase();

    if (
        lower.includes("yesterday") ||
        lower.includes("last week") ||
        lower.includes("last month")
    ) {
        return {
            statement,
            type: "concrete past behavior",
            strength: "high"
        };
    }

    if (
        lower.startsWith("i think") ||
        lower.startsWith("i believe") ||
        lower.startsWith("i feel")
    ) {
        return {
            statement,
            type: "stated opinion",
            strength: "medium"
        };
    }

    if (lower.includes("would") || lower.includes("might")) {
        return {
            statement,
            type: "hypothetical intention",
            strength: "low"
        };
    }

    return {
        statement,
        type: "general statement",
        strength: "medium"
    };
}

function demonstrateEvidenceClassification() {
    console.log("\n=== EVIDENCE CLASSIFICATION ===");

    const statements = [
        "Last week I spent forty minutes reconciling three invoices.",
        "I think automation would be useful.",
        "I would probably use a mobile application.",
        "I usually check invoices on Fridays."
    ];

    statements.forEach(statement => {
        console.log(classifyEvidence(statement));
    });
}


// -----------------------------------------------------------------------------
// 7. INTERVIEW RECORD
// -----------------------------------------------------------------------------

class InterviewRecord {
    constructor(participantId) {
        this.participantId = participantId;
        this.notes = [];
    }

    addNote(observation, quote = null, interpretation = null) {
        if (!observation || typeof observation !== "string") {
            throw new Error("An observation is required.");
        }

        this.notes.push({
            observation,
            quote,
            interpretation,
            timestamp: new Date().toISOString()
        });
    }

    getObservations() {
        return this.notes.map(note => note.observation);
    }

    getQuotes() {
        return this.notes
            .filter(note => note.quote)
            .map(note => note.quote);
    }
}

function demonstrateInterviewRecord() {
    console.log("\n=== INTERVIEW RECORD ===");

    const record = new InterviewRecord("P01");

    record.addNote(
        "Participant opened a spreadsheet.",
        "I keep everything in this spreadsheet.",
        "The spreadsheet appears central to the workflow."
    );

    record.addNote(
        "Participant described manually marking reminders.",
        "I add a note after sending the email.",
        "The participant has created a manual tracking workaround."
    );

    console.log("Observations:", record.getObservations());
    console.log("Quotes:", record.getQuotes());
}


// -----------------------------------------------------------------------------
// 8. THEMATIC ANALYSIS
// -----------------------------------------------------------------------------

const stopWords = new Set([
    "the", "a", "an", "and", "or", "to", "of", "in", "on",
    "for", "is", "it", "i", "we", "this", "that", "with",
    "my", "our", "was", "are"
]);

function tokenize(text) {
    return text
        .toLowerCase()
        .match(/[a-zA-Z']+/g)
        ?.filter(word => word.length > 2 && !stopWords.has(word)) || [];
}

function wordFrequency(texts) {
    const frequencies = new Map();

    for (const text of texts) {
        for (const word of tokenize(text)) {
            frequencies.set(word, (frequencies.get(word) || 0) + 1);
        }
    }

    return new Map(
        [...frequencies.entries()].sort((a, b) => b[1] - a[1])
    );
}

function demonstrateThematicAnalysis() {
    console.log("\n=== THEMATIC ANALYSIS ===");

    const transcripts = [
        "I use a spreadsheet because the accounting system is difficult to search.",
        "I check the spreadsheet every Friday before sending reminders.",
        "The accounting system contains payment information but reconciliation still takes time.",
        "I use calendar reminders when an invoice becomes overdue."
    ];

    const frequencies = wordFrequency(transcripts);

    console.log([...frequencies.entries()].slice(0, 12));
}


// -----------------------------------------------------------------------------
// 9. THEME GROUPING
// -----------------------------------------------------------------------------

function groupByTheme(findings) {
    const groups = new Map();

    for (const finding of findings) {
        if (!groups.has(finding.theme)) {
            groups.set(finding.theme, []);
        }

        groups.get(finding.theme).push(finding);
    }

    return groups;
}

function demonstrateThemeGrouping() {
    console.log("\n=== THEME GROUPING ===");

    const findings = [
        {
            participant: "P01",
            theme: "manual work",
            statement: "Uses a spreadsheet to track invoice status."
        },
        {
            participant: "P02",
            theme: "manual work",
            statement: "Copies payment information into a spreadsheet."
        },
        {
            participant: "P03",
            theme: "reminders",
            statement: "Uses calendar reminders."
        },
        {
            participant: "P04",
            theme: "manual work",
            statement: "Reconciles payment data manually."
        }
    ];

    const grouped = groupByTheme(findings);

    for (const [theme, items] of grouped.entries()) {
        console.log(`\nTheme: ${theme}`);

        for (const item of items) {
            console.log(`  ${item.participant}: ${item.statement}`);
        }
    }
}


// -----------------------------------------------------------------------------
// 10. CONTRADICTIONS
// -----------------------------------------------------------------------------

function findContradictions(statements) {
    const positive = [];
    const negative = [];

    for (const statement of statements) {
        const lower = statement.text.toLowerCase();

        if (
            lower.includes("works well") ||
            lower.includes("sufficient") ||
            lower.includes("easy")
        ) {
            positive.push(statement);
        }

        if (
            lower.includes("slow") ||
            lower.includes("difficult") ||
            lower.includes("problem")
        ) {
            negative.push(statement);
        }
    }

    return { positive, negative };
}

function demonstrateContradictions() {
    console.log("\n=== CONTRADICTORY EVIDENCE ===");

    const statements = [
        {
            participant: "P01",
            text: "The spreadsheet is slow when there are many invoices."
        },
        {
            participant: "P02",
            text: "The spreadsheet works well for our current volume."
        },
        {
            participant: "P03",
            text: "The process becomes difficult as the business grows."
        }
    ];

    const result = findContradictions(statements);

    console.log("Positive/sufficient statements:", result.positive);
    console.log("Difficulty/problem statements:", result.negative);
}


// -----------------------------------------------------------------------------
// 11. ASYNCHRONOUS INTERVIEW SIMULATION
// -----------------------------------------------------------------------------

function delay(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function conductSimulatedInterview(participant, questions) {
    if (!participant || !Array.isArray(questions)) {
        throw new TypeError("Participant and questions are required.");
    }

    const responses = [];

    for (const question of questions) {
        await delay(50);

        const answer = participant.responses[question] ||
            "I do not have a specific example for that.";

        responses.push({
            question,
            answer,
            capturedAt: new Date().toISOString()
        });
    }

    return responses;
}

async function demonstrateAsyncInterview() {
    console.log("\n=== ASYNCHRONOUS INTERVIEW SIMULATION ===");

    const participant = {
        id: "P01",
        role: "Small-business owner",
        responses: {
            "recent event":
                "Last Tuesday I checked overdue invoices and sent three reminders.",
            "difficulty":
                "The difficult part is remembering which customers already received reminders.",
            "workaround":
                "I add a note in the spreadsheet after sending an email."
        }
    };

    const questions = ["recent event", "difficulty", "workaround"];

    const responses = await conductSimulatedInterview(
        participant,
        questions
    );

    for (const response of responses) {
        console.log(`Question: ${response.question}`);
        console.log(`Answer: ${response.answer}`);
    }
}


// -----------------------------------------------------------------------------
// 12. EVENT-DRIVEN INTERVIEW LOGGER
// -----------------------------------------------------------------------------

class InterviewEventEmitter {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("Listener must be a function.");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) || [];

        for (const listener of listeners) {
            listener(payload);
        }
    }
}

function demonstrateEventDrivenLogging() {
    console.log("\n=== EVENT-DRIVEN INTERVIEW LOGGING ===");

    const emitter = new InterviewEventEmitter();

    emitter.on("answer", payload => {
        console.log(
            `Captured answer from ${payload.participantId}: ${payload.answer}`
        );
    });

    emitter.on("probe", payload => {
        console.log(`Probe generated: ${payload.question}`);
    });

    emitter.emit("answer", {
        participantId: "P01",
        answer: "I use a spreadsheet every Friday."
    });

    emitter.emit("probe", {
        question: "What happened the last time you used the spreadsheet?"
    });
}


// -----------------------------------------------------------------------------
// 13. VALIDATION
// -----------------------------------------------------------------------------

function validateInterviewData(interview) {
    const errors = [];

    if (!interview || typeof interview !== "object") {
        return ["Interview must be an object."];
    }

    if (!interview.participantId) {
        errors.push("Missing participant ID.");
    }

    if (!Array.isArray(interview.questions)) {
        errors.push("Questions must be an array.");
    }

    if (!Array.isArray(interview.answers)) {
        errors.push("Answers must be an array.");
    }

    if (
        Array.isArray(interview.questions) &&
        Array.isArray(interview.answers) &&
        interview.questions.length !== interview.answers.length
    ) {
        errors.push("Question and answer counts must match.");
    }

    return errors;
}

function demonstrateValidation() {
    console.log("\n=== VALIDATION ===");

    const validInterview = {
        participantId: "P01",
        questions: ["What happened?"],
        answers: ["I checked the spreadsheet."]
    };

    const invalidInterview = {
        participantId: "",
        questions: ["What happened?", "What happened next?"],
        answers: ["I checked the spreadsheet."]
    };

    console.log("Valid record:", validateInterviewData(validInterview));
    console.log("Invalid record:", validateInterviewData(invalidInterview));
}


// -----------------------------------------------------------------------------
// 14. INTERVIEW QUALITY REVIEW
// -----------------------------------------------------------------------------

function reviewInterviewQuality(interview) {
    const questions = interview.questions || [];
    const answers = interview.answers || [];

    const hypotheticalQuestions = questions.filter(question =>
        /would you|would you use|would you buy|would you pay/i.test(question)
    );

    const shortAnswers = answers.filter(answer =>
        answer.trim().split(/\s+/).length < 5
    );

    return {
        totalQuestions: questions.length,
        hypotheticalQuestionCount: hypotheticalQuestions.length,
        shortAnswerCount: shortAnswers.length,
        warning:
            hypotheticalQuestions.length > 0
                ? "Review hypothetical questions and consider behavior-focused alternatives."
                : "No common hypothetical wording detected."
    };
}

function demonstrateQualityReview() {
    console.log("\n=== QUALITY REVIEW ===");

    const interview = {
        questions: [
            "Tell me about the last time you followed up.",
            "Would you use automatic reminders?",
            "What happened next?"
        ],
        answers: [
            "I followed up last Tuesday.",
            "Probably.",
            "Then I sent an email."
        ]
    };

    console.log(reviewInterviewQuality(interview));
}


// -----------------------------------------------------------------------------
// 15. RESEARCH HYPOTHESIS
// -----------------------------------------------------------------------------

class ResearchHypothesis {
    constructor(statement) {
        this.statement = statement;
        this.supportingEvidence = [];
        this.contradictingEvidence = [];
    }

    addSupport(evidence) {
        this.supportingEvidence.push(evidence);
    }

    addContradiction(evidence) {
        this.contradictingEvidence.push(evidence);
    }

    evidenceState() {
        const support = this.supportingEvidence.length;
        const contradiction = this.contradictingEvidence.length;

        if (support === 0 && contradiction === 0) {
            return "No recorded evidence";
        }

        if (contradiction > 0 && support > 0) {
            return "Mixed evidence";
        }

        if (contradiction > support) {
            return "Substantial contradiction";
        }

        return "Supporting evidence recorded";
    }
}

function demonstrateHypothesisTesting() {
    console.log("\n=== HYPOTHESIS TESTING ===");

    const hypothesis = new ResearchHypothesis(
        "Small businesses struggle with invoice follow-up."
    );

    hypothesis.addSupport("P01 described manual tracking.");
    hypothesis.addSupport("P03 reported missed reminders.");
    hypothesis.addContradiction(
        "P02 said the current workflow is sufficient."
    );

    console.log("Statement:", hypothesis.statement);
    console.log("Evidence state:", hypothesis.evidenceState());
    console.log("Supporting:", hypothesis.supportingEvidence);
    console.log("Contradicting:", hypothesis.contradictingEvidence);
}


// -----------------------------------------------------------------------------
// 16. INTERVIEW CHECKLIST
// -----------------------------------------------------------------------------

function createInterviewChecklist() {
    return [
        "Research objective is defined.",
        "Participant criteria are defined.",
        "Questions are mostly open and behavior-focused.",
        "Leading questions have been reviewed.",
        "Hypothetical questions are minimized.",
        "Double-barreled questions are separated.",
        "A recent concrete event is explored.",
        "Important answers receive follow-up probes.",
        "Observations and interpretations are separated.",
        "Contradictory evidence is preserved.",
        "Privacy and consent requirements are considered.",
        "Notes are stored consistently."
    ];
}

function demonstrateChecklist() {
    console.log("\n=== INTERVIEW CHECKLIST ===");

    createInterviewChecklist().forEach((item, index) => {
        console.log(`[ ] ${index + 1}. ${item}`);
    });
}


// -----------------------------------------------------------------------------
// 17. END-TO-END ANALYSIS PIPELINE
// -----------------------------------------------------------------------------

function analyzeInterviewSet(interviews) {
    if (!Array.isArray(interviews)) {
        throw new TypeError("Interviews must be an array.");
    }

    const allStatements = interviews.flatMap(interview =>
        interview.answers.map(answer => ({
            participantId: interview.participantId,
            text: answer
        }))
    );

    const classified = allStatements.map(statement => ({
        ...statement,
        evidence: classifyEvidence(statement.text)
    }));

    const concreteBehaviorCount = classified.filter(
        item => item.evidence.type === "concrete past behavior"
    ).length;

    const hypotheticalCount = classified.filter(
        item => item.evidence.type === "hypothetical intention"
    ).length;

    return {
        interviewCount: interviews.length,
        statementCount: classified.length,
        concreteBehaviorCount,
        hypotheticalCount,
        classified
    };
}

function demonstrateEndToEndAnalysis() {
    console.log("\n=== END-TO-END ANALYSIS ===");

    const interviews = [
        {
            participantId: "P01",
            answers: [
                "Last week I checked the spreadsheet.",
                "I think automation would help."
            ]
        },
        {
            participantId: "P02",
            answers: [
                "Last month I reconciled payments manually.",
                "I would probably try another system."
            ]
        }
    ];

    console.log(analyzeInterviewSet(interviews));
}


// -----------------------------------------------------------------------------
// 18. PRACTICAL CAPSTONE
// -----------------------------------------------------------------------------

function runCapstone() {
    console.log("\n=== PRACTICAL CAPSTONE ===");

    const researchQuestion =
        "How do small businesses manage overdue invoice follow-up?";

    const behavioralQuestions = [
        "Tell me about the last overdue invoice you handled.",
        "What did you do?",
        "How did you know it was overdue?",
        "What happened after you contacted the customer?",
        "What happens when a follow-up is missed?",
        "What tools are involved?",
        "How often does this occur?",
        "What workaround do you use?",
        "Have you tried changing the process?",
        "What important issue have I not asked about?"
    ];

    console.log("Research question:", researchQuestion);
    console.log("\nInterview sequence:");

    behavioralQuestions.forEach((question, index) => {
        console.log(`${index + 1}. ${question}`);
    });

    console.log(
        "\nThe sequence deliberately investigates current behavior before introducing a proposed solution."
    );
}


// -----------------------------------------------------------------------------
// 19. MAIN
// -----------------------------------------------------------------------------

async function main() {
    console.log("CUSTOMER INTERVIEWS: JAVASCRIPT PRACTICAL STUDY");

    demonstrateQuestionDesign();
    demonstrateRewriting();
    demonstrateInterviewGuide();
    demonstrateProbing();
    demonstrateEvidenceClassification();
    demonstrateInterviewRecord();
    demonstrateThematicAnalysis();
    demonstrateThemeGrouping();
    demonstrateContradictions();
    await demonstrateAsyncInterview();
    demonstrateEventDrivenLogging();
    demonstrateValidation();
    demonstrateQualityReview();
    demonstrateHypothesisTesting();
    demonstrateChecklist();
    demonstrateEndToEndAnalysis();
    runCapstone();

    console.log("\nStudy complete.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
