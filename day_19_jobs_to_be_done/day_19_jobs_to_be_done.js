/*
 * Jobs To Be Done (JTBD)
 * ======================
 *
 * A standalone JavaScript study program covering:
 *   - jobs and circumstances
 *   - functional, emotional, and social jobs
 *   - job stories
 *   - desired outcomes
 *   - opportunity scoring
 *   - switching forces
 *   - qualitative evidence
 *   - job clustering
 *   - job mapping
 *   - validation
 *   - a reusable JTBD analysis engine
 *   - an event-driven research workflow
 *
 * Run with:
 *   node jtbd.js
 */

"use strict";

// ---------------------------------------------------------------------------
// 1. BASIC OUTPUT HELPERS
// ---------------------------------------------------------------------------

function section(title) {
  console.log(`\n${"=".repeat(80)}\n${title}\n${"=".repeat(80)}`);
}

function subsection(title) {
  console.log(`\n--- ${title} ---`);
}

// ---------------------------------------------------------------------------
// 2. BASIC JTBD TERMINOLOGY
// ---------------------------------------------------------------------------

section("1. JTBD FUNDAMENTALS");

console.log(`
Jobs To Be Done examines the progress a person is trying to make in a
particular circumstance.

A feature describes what a product provides.
A job describes what the customer is trying to accomplish.

Example:

Feature:
  "Calendar notifications"

Job:
  "When several commitments compete for my attention, I want to know what
   requires action so I can avoid missing an important commitment."

The job can have functional, emotional, and social dimensions.
`);


// ---------------------------------------------------------------------------
// 3. JOB OBJECT
// ---------------------------------------------------------------------------

class Job {
    constructor({
        title,
        circumstance,
        functional,
        emotional,
        social,
        desiredOutcome
    }) {
        this.title = title;
        this.circumstance = circumstance;
        this.functional = functional;
        this.emotional = emotional;
        this.social = social;
        this.desiredOutcome = desiredOutcome;

        this.validate();
    }

    validate() {
        const fields = {
            title: this.title,
            circumstance: this.circumstance,
            functional: this.functional,
            emotional: this.emotional,
            social: this.social,
            desiredOutcome: this.desiredOutcome
        };

        for (const [name, value] of Object.entries(fields)) {
            if (typeof value !== "string" || value.trim() === "") {
                throw new Error(`${name} must be a non-empty string.`);
            }
        }
    }

    describe() {
        return [
            `Job: ${this.title}`,
            `Circumstance: ${this.circumstance}`,
            `Functional: ${this.functional}`,
            `Emotional: ${this.emotional}`,
            `Social: ${this.social}`,
            `Desired outcome: ${this.desiredOutcome}`
        ].join("\n");
    }
}

const studyJob = new Job({
    title: "Prepare for an examination",
    circumstance: "An important examination is approaching and time is limited.",
    functional: "Identify, prioritize, practice, and review important material.",
    emotional: "Feel prepared and reduce uncertainty.",
    social: "Demonstrate reliable preparation to relevant stakeholders.",
    desiredOutcome: "Improve readiness while reducing wasted effort."
});

console.log(studyJob.describe());


// ---------------------------------------------------------------------------
// 4. JOB STORIES
// ---------------------------------------------------------------------------

section("2. JOB STORIES");

class JobStory {
    constructor(circumstance, motivation, outcome) {
        if (![circumstance, motivation, outcome].every(
            value => typeof value === "string" && value.trim()
        )) {
            throw new Error("All job-story components must contain text.");
        }

        this.circumstance = circumstance;
        this.motivation = motivation;
        this.outcome = outcome;
    }

    render() {
        return (
            `When ${this.circumstance}, ` +
            `I want to ${this.motivation}, ` +
            `so I can ${this.outcome}.`
        );
    }
}

const story = new JobStory(
    "I have several subjects to revise before an examination",
    "identify which topics require the most attention",
    "allocate my limited study time effectively"
);

console.log(story.render());


// ---------------------------------------------------------------------------
// 5. DESIRED OUTCOMES AND OPPORTUNITY
// ---------------------------------------------------------------------------

section("3. DESIRED OUTCOMES");

class DesiredOutcome {
    constructor(statement, importance, satisfaction) {
        this.statement = statement;
        this.importance = importance;
        this.satisfaction = satisfaction;
        this.validate();
    }

    validate() {
        if (!this.statement || !this.statement.trim()) {
            throw new Error("Outcome statement cannot be empty.");
        }

        if (!Number.isFinite(this.importance) ||
            this.importance < 0 ||
            this.importance > 10) {
            throw new Error("Importance must be between 0 and 10.");
        }

        if (!Number.isFinite(this.satisfaction) ||
            this.satisfaction < 0 ||
            this.satisfaction > 10) {
            throw new Error("Satisfaction must be between 0 and 10.");
        }
    }

    opportunityScore() {
        return this.importance +
            Math.max(this.importance - this.satisfaction, 0);
    }
}

const outcomes = [
    new DesiredOutcome(
        "Minimize the time required to identify weak topics.",
        9,
        4
    ),
    new DesiredOutcome(
        "Increase confidence that important material is covered.",
        8,
        5
    ),
    new DesiredOutcome(
        "Minimize the effort required to monitor progress.",
        6,
        7
    ),
    new DesiredOutcome(
        "Increase the likelihood of remembering difficult concepts.",
        9,
        3
    )
];

for (const outcome of outcomes) {
    console.log(
        `${outcome.statement}\n` +
        `  importance=${outcome.importance}, ` +
        `satisfaction=${outcome.satisfaction}, ` +
        `opportunity=${outcome.opportunityScore().toFixed(1)}`
    );
}


// ---------------------------------------------------------------------------
// 6. FUNCTIONAL, EMOTIONAL, AND SOCIAL DIMENSIONS
// ---------------------------------------------------------------------------

section("4. JOB DIMENSIONS");

const dimensions = {
    functional: [
        "solve a practical problem",
        "organize information",
        "reduce time",
        "reduce effort",
        "make a decision"
    ],
    emotional: [
        "feel confident",
        "reduce uncertainty",
        "feel in control",
        "avoid frustration",
        "feel accomplished"
    ],
    social: [
        "appear reliable",
        "demonstrate competence",
        "maintain reputation",
        "fit a social expectation",
        "signal expertise"
    ]
};

for (const [dimension, examples] of Object.entries(dimensions)) {
    console.log(`\n${dimension.toUpperCase()}`);
    for (const example of examples) {
        console.log(`  - ${example}`);
    }
}


// ---------------------------------------------------------------------------
// 7. SWITCHING FORCES
// ---------------------------------------------------------------------------

section("5. SWITCHING FORCES");

class SwitchingEvent {
    constructor({
        previousSolution,
        newSolution,
        trigger,
        push,
        pull,
        anxiety,
        habit
    }) {
        this.previousSolution = previousSolution;
        this.newSolution = newSolution;
        this.trigger = trigger;
        this.push = push;
        this.pull = pull;
        this.anxiety = anxiety;
        this.habit = habit;
    }

    report() {
        return {
            previousSolution: this.previousSolution,
            newSolution: this.newSolution,
            trigger: this.trigger,
            forces: {
                push: this.push,
                pull: this.pull,
                anxiety: this.anxiety,
                habit: this.habit
            }
        };
    }
}

const switchingEvent = new SwitchingEvent({
    previousSolution: "Spreadsheet",
    newSolution: "Expense application",
    trigger: "Manual maintenance became difficult as transaction volume increased.",
    push: "Manual categorization consumed too much time.",
    pull: "Automatic categorization looked more efficient.",
    anxiety: "The user was concerned about privacy and classification errors.",
    habit: "The spreadsheet workflow was familiar."
});

console.log(JSON.stringify(switchingEvent.report(), null, 2));


// ---------------------------------------------------------------------------
// 8. RESEARCH EVIDENCE
// ---------------------------------------------------------------------------

section("6. RESEARCH EVIDENCE");

class InterviewEvidence {
    constructor({
        participantId,
        circumstance,
        behavior,
        previousSolution,
        pain,
        desiredResult
    }) {
        this.participantId = participantId;
        this.circumstance = circumstance;
        this.behavior = behavior;
        this.previousSolution = previousSolution;
        this.pain = pain;
        this.desiredResult = desiredResult;
    }
}

const interviews = [
    new InterviewEvidence({
        participantId: "P01",
        circumstance: "An exam was two weeks away.",
        behavior: "Created a spreadsheet of topics.",
        previousSolution: "Spreadsheet",
        pain: "Maintaining the list became tedious.",
        desiredResult: "Know which topics deserve attention first."
    }),
    new InterviewEvidence({
        participantId: "P02",
        circumstance: "Several assignments were due in one week.",
        behavior: "Used calendar reminders and handwritten notes.",
        previousSolution: "Calendar and notebook",
        pain: "Information was scattered.",
        desiredResult: "See priorities in one place."
    }),
    new InterviewEvidence({
        participantId: "P03",
        circumstance: "A difficult subject contained many formulas.",
        behavior: "Repeated practice problems.",
        previousSolution: "Textbook and notebook",
        pain: "Did not know which concepts were still weak.",
        desiredResult: "Obtain evidence of readiness."
    })
];

for (const interview of interviews) {
    console.log(`\n${interview.participantId}`);
    console.log(`  circumstance: ${interview.circumstance}`);
    console.log(`  behavior: ${interview.behavior}`);
    console.log(`  previous solution: ${interview.previousSolution}`);
    console.log(`  pain: ${interview.pain}`);
    console.log(`  desired result: ${interview.desiredResult}`);
}


// ---------------------------------------------------------------------------
// 9. JOB CLUSTERING
// ---------------------------------------------------------------------------

section("7. JOB CLUSTERING");

function clusterEvidence(evidence) {
    const clusters = new Map();

    for (const item of evidence) {
        if (!clusters.has(item.cluster)) {
            clusters.set(item.cluster, []);
        }

        clusters.get(item.cluster).push(item);
    }

    return clusters;
}

const codedEvidence = [
    {
        participantId: "P01",
        statement: "Identify weak chapters.",
        cluster: "Prioritize knowledge gaps"
    },
    {
        participantId: "P02",
        statement: "Know what to revise first.",
        cluster: "Prioritize knowledge gaps"
    },
    {
        participantId: "P03",
        statement: "Avoid guessing what matters.",
        cluster: "Prioritize knowledge gaps"
    },
    {
        participantId: "P04",
        statement: "Track deadlines.",
        cluster: "Manage commitments"
    },
    {
        participantId: "P05",
        statement: "Know which assignment comes first.",
        cluster: "Manage commitments"
    }
];

const clusters = clusterEvidence(codedEvidence);

for (const [clusterName, items] of clusters) {
    console.log(`\n${clusterName}`);

    for (const item of items) {
        console.log(`  ${item.participantId}: ${item.statement}`);
    }
}


// ---------------------------------------------------------------------------
// 10. REUSABLE JTBD ANALYSIS ENGINE
// ---------------------------------------------------------------------------

section("8. REUSABLE JTBD ANALYSIS ENGINE");

class JTBDAnalysis {
    constructor({
        name,
        circumstance,
        functionalJob,
        emotionalJob,
        socialJob,
        desiredOutcomes = [],
        alternatives = [],
        barriers = []
    }) {
        this.name = name;
        this.circumstance = circumstance;
        this.functionalJob = functionalJob;
        this.emotionalJob = emotionalJob;
        this.socialJob = socialJob;
        this.desiredOutcomes = desiredOutcomes;
        this.alternatives = alternatives;
        this.barriers = barriers;

        this.validate();
    }

    validate() {
        const required = {
            name: this.name,
            circumstance: this.circumstance,
            functionalJob: this.functionalJob,
            emotionalJob: this.emotionalJob,
            socialJob: this.socialJob
        };

        for (const [field, value] of Object.entries(required)) {
            if (typeof value !== "string" || value.trim() === "") {
                throw new Error(`${field} is required.`);
            }
        }

        if (!Array.isArray(this.desiredOutcomes)) {
            throw new Error("desiredOutcomes must be an array.");
        }

        for (const outcome of this.desiredOutcomes) {
            if (!(outcome instanceof DesiredOutcome)) {
                throw new Error("Each outcome must be a DesiredOutcome.");
            }
        }
    }

    averageOpportunity() {
        if (this.desiredOutcomes.length === 0) {
            return 0;
        }

        const total = this.desiredOutcomes.reduce(
            (sum, outcome) => sum + outcome.opportunityScore(),
            0
        );

        return total / this.desiredOutcomes.length;
    }

    highestOpportunity() {
        if (this.desiredOutcomes.length === 0) {
            return null;
        }

        return this.desiredOutcomes.reduce(
            (highest, current) =>
                current.opportunityScore() > highest.opportunityScore()
                    ? current
                    : highest
        );
    }

    report() {
        console.log(`JTBD analysis: ${this.name}`);
        console.log(`Circumstance: ${this.circumstance}`);
        console.log(`Functional job: ${this.functionalJob}`);
        console.log(`Emotional job: ${this.emotionalJob}`);
        console.log(`Social job: ${this.socialJob}`);
        console.log(`Alternatives: ${this.alternatives.join(", ")}`);
        console.log(`Barriers: ${this.barriers.join(", ")}`);

        console.log("Desired outcomes:");

        for (const outcome of this.desiredOutcomes) {
            console.log(
                `  - ${outcome.statement} ` +
                `(opportunity=${outcome.opportunityScore().toFixed(1)})`
            );
        }
    }
}

const analysis = new JTBDAnalysis({
    name: "Examination preparation",
    circumstance: "Several subjects must be revised before an important exam.",
    functionalJob: "Identify, prioritize, practice, and review knowledge gaps.",
    emotionalJob: "Feel prepared and reduce uncertainty.",
    socialJob: "Demonstrate reliable preparation.",
    desiredOutcomes: [
        new DesiredOutcome(
            "Minimize the time required to identify weak topics.",
            9,
            4
        ),
        new DesiredOutcome(
            "Increase confidence in examination readiness.",
            9,
            5
        ),
        new DesiredOutcome(
            "Minimize effort required to monitor revision progress.",
            7,
            6
        )
    ],
    alternatives: [
        "Notebook",
        "Spreadsheet",
        "Calendar",
        "Textbook",
        "Peer advice"
    ],
    barriers: [
        "Limited time",
        "Scattered information",
        "Unclear priorities"
    ]
});

analysis.report();


// ---------------------------------------------------------------------------
// 11. FEATURE LANGUAGE DETECTION
// ---------------------------------------------------------------------------

section("9. FEATURE LANGUAGE VERSUS JOB LANGUAGE");

const solutionTerms = new Set([
    "app",
    "dashboard",
    "button",
    "notification",
    "feature",
    "platform",
    "software",
    "screen"
]);

function likelyContainsSolutionLanguage(statement) {
    const words = statement
        .toLowerCase()
        .match(/[a-z]+/g) || [];

    return words.some(word => solutionTerms.has(word));
}

const candidateStatements = [
    "I need a dashboard.",
    "I need to prioritize work before the deadline.",
    "I want notifications.",
    "I want to reduce uncertainty before deciding."
];

for (const statement of candidateStatements) {
    console.log(
        `${statement.padEnd(60)} -> ` +
        `${likelyContainsSolutionLanguage(statement)
            ? "likely solution language"
            : "not obviously solution language"}`
    );
}


// ---------------------------------------------------------------------------
// 12. JOB MAP
// ---------------------------------------------------------------------------

section("10. JOB MAP");

const jobMap = new Map([
    ["Define", "Clarify what must be achieved."],
    ["Locate", "Find relevant information or resources."],
    ["Prepare", "Arrange inputs and conditions."],
    ["Confirm", "Check whether the approach is appropriate."],
    ["Execute", "Perform the core activity."],
    ["Monitor", "Observe progress and emerging problems."],
    ["Modify", "Adjust the approach when conditions change."],
    ["Conclude", "Determine whether the desired result was achieved."]
]);

for (const [stage, description] of jobMap) {
    console.log(`${stage.padEnd(10)}: ${description}`);
}


// ---------------------------------------------------------------------------
// 13. ASYNCHRONOUS RESEARCH WORKFLOW
// ---------------------------------------------------------------------------

section("11. EVENT-DRIVEN AND ASYNCHRONOUS JTBD WORKFLOW");

/*
 * JavaScript is useful for modeling browser and application workflows.
 * An asynchronous function can represent a research pipeline in which
 * evidence arrives from multiple sources.
 *
 * No external service is required here. The artificial delay merely
 * demonstrates asynchronous control flow.
 */

function delay(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function collectEvidence(sourceName, evidence) {
    await delay(20);

    return {
        sourceName,
        collectedAt: new Date().toISOString(),
        evidence
    };
}

async function runResearchPipeline() {
    const sources = await Promise.all([
        collectEvidence("Interview batch A", [
            "Users need to identify weak topics quickly.",
            "Manual tracking becomes tedious."
        ]),
        collectEvidence("Interview batch B", [
            "Users want confidence before an exam.",
            "Information is often scattered."
        ])
    ]);

    return sources;
}

runResearchPipeline()
    .then(results => {
        console.log("\nAsynchronous research results:");

        for (const result of results) {
            console.log(`\nSource: ${result.sourceName}`);
            console.log(`Collected: ${result.collectedAt}`);

            for (const item of result.evidence) {
                console.log(`  - ${item}`);
            }
        }
    })
    .catch(error => {
        console.error("Research pipeline failed:", error.message);
    });


// ---------------------------------------------------------------------------
// 14. PRODUCT DISCOVERY CASE
// ---------------------------------------------------------------------------

section("12. PRODUCT DISCOVERY CASE STUDY");

const productDiscovery = new JTBDAnalysis({
    name: "Study planning under time pressure",
    circumstance:
        "A learner has several subjects, limited time, and an upcoming assessment.",
    functionalJob:
        "Determine what to study, in what order, and whether preparation is sufficient.",
    emotionalJob:
        "Reduce uncertainty and feel in control of preparation.",
    socialJob:
        "Appear prepared and dependable when discussing academic progress.",
    desiredOutcomes: [
        new DesiredOutcome(
            "Minimize the time needed to identify high-priority topics.",
            10,
            3
        ),
        new DesiredOutcome(
            "Minimize the likelihood of overlooking an important topic.",
            10,
            4
        ),
        new DesiredOutcome(
            "Increase confidence that preparation is sufficient.",
            9,
            5
        ),
        new DesiredOutcome(
            "Minimize effort required to update the study plan.",
            7,
            6
        )
    ],
    alternatives: [
        "Notebook",
        "Spreadsheet",
        "Calendar",
        "Textbook",
        "Peer advice"
    ],
    barriers: [
        "Poor information organization",
        "Changing deadlines",
        "Limited time",
        "Unclear priorities"
    ]
});

productDiscovery.report();

const highest = productDiscovery.highestOpportunity();

if (highest) {
    console.log(
        `\nHighest opportunity in the illustrative dataset:\n` +
        `  ${highest.statement}\n` +
        `  Score: ${highest.opportunityScore().toFixed(1)}`
    );
}


// ---------------------------------------------------------------------------
// 15. EDGE CASES
// ---------------------------------------------------------------------------

section("13. EDGE CASES AND ERROR HANDLING");

try {
    new DesiredOutcome("Invalid importance", 12, 4);
} catch (error) {
    console.log(`Caught invalid rating: ${error.message}`);
}

try {
    new JobStory("", "prioritize work", "use time effectively");
} catch (error) {
    console.log(`Caught invalid job story: ${error.message}`);
}

const emptyOutcomeAnalysis = new JTBDAnalysis({
    name: "No outcomes",
    circumstance: "A valid circumstance.",
    functionalJob: "A valid functional job.",
    emotionalJob: "A valid emotional job.",
    socialJob: "A valid social job."
});

console.log(
    `Average opportunity with no outcomes: ` +
    `${emptyOutcomeAnalysis.averageOpportunity()}`
);


// ---------------------------------------------------------------------------
// 16. PERFORMANCE CONSIDERATIONS
// ---------------------------------------------------------------------------

section("14. PERFORMANCE CONSIDERATIONS");

console.log(`
For k desired outcomes:
  opportunity calculation for one outcome: O(1)
  average opportunity: O(k)
  highest opportunity: O(k)
  sorting outcomes: O(k log k)

For n evidence records:
  clustering using Map: approximately O(n)

JavaScript Map is useful for grouping evidence because lookup and insertion
are designed for efficient keyed access. For very large research systems,
persistent storage, indexing, pagination, and controlled data processing
would become more important.
`);


// ---------------------------------------------------------------------------
// 17. SECURITY AND PRIVACY
// ---------------------------------------------------------------------------

section("15. SECURITY AND PRIVACY");

console.log(`
JTBD interviews may contain personal or sensitive information.

A production implementation should consider:
  - data minimization
  - authorization
  - encryption
  - retention limits
  - removal of unnecessary identifiers
  - auditability
  - secure transcript storage
  - consent and appropriate research governance

The framework itself does not remove the need for responsible data handling.
`);


// ---------------------------------------------------------------------------
// 18. SELF-TESTS
// ---------------------------------------------------------------------------

section("16. SELF-TESTS");

function runTests() {
    const testOutcome = new DesiredOutcome("Test", 8, 3);

    if (testOutcome.opportunityScore() !== 13) {
        throw new Error("Opportunity calculation failed.");
    }

    const testStory = new JobStory(
        "a deadline is approaching",
        "prioritize important work",
        "use limited time effectively"
    );

    if (!testStory.render().includes("When")) {
        throw new Error("Job story rendering failed.");
    }

    const testAnalysis = new JTBDAnalysis({
        name: "Test",
        circumstance: "A circumstance",
        functionalJob: "A functional job",
        emotionalJob: "An emotional job",
        socialJob: "A social job",
        desiredOutcomes: [testOutcome]
    });

    if (testAnalysis.averageOpportunity() !== 13) {
        throw new Error("Average opportunity calculation failed.");
    }

    let validationWorked = false;

    try {
        new DesiredOutcome("Bad", -1, 5);
    } catch {
        validationWorked = true;
    }

    if (!validationWorked) {
        throw new Error("Validation test failed.");
    }

    console.log("All JavaScript self-tests passed.");
}

runTests();


// ---------------------------------------------------------------------------
// 19. COMPLETE WORKFLOW
// ---------------------------------------------------------------------------

section("17. COMPLETE JTBD WORKFLOW");

const workflow = [
    "Identify a meaningful circumstance.",
    "Investigate a real event and actual behavior.",
    "Describe the progress the person was trying to make.",
    "Separate the job from the current solution.",
    "Identify functional, emotional, and social dimensions.",
    "Examine previous solutions and workarounds.",
    "Identify switching triggers and barriers.",
    "Extract desired outcomes.",
    "Cluster recurring evidence.",
    "Validate the job against research evidence.",
    "Prioritize important outcomes using appropriate evidence.",
    "Design solutions against the job instead of assuming a feature is the job."
];

workflow.forEach((step, index) => {
    console.log(`${index + 1}. ${step}`);
});

console.log(`
Core analytical question:

What progress is the person trying to make, under what circumstances,
and what evidence shows that current ways of making that progress are
insufficient?
`);
