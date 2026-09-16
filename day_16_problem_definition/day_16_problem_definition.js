"use strict";

/*
 * Problem Definition
 *
 * Topic coverage:
 * - problem statements
 * - symptoms versus root causes
 * - problem framing
 * - problem boundaries
 * - evidence and hypotheses
 * - constraints and assumptions
 * - measurable gaps
 * - causal investigation
 * - stakeholder perspectives
 * - validation
 * - an event-driven diagnostic example
 *
 * Run with:
 *     node problem_definition.js
 */

// -----------------------------------------------------------------------------
// 1. BASIC OUTPUT HELPERS
// -----------------------------------------------------------------------------

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function printSubsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}


// -----------------------------------------------------------------------------
// 2. PROBLEM STATEMENTS
// -----------------------------------------------------------------------------

class ProblemStatement {
    constructor({
        affectedActor,
        currentCondition,
        measurableGap,
        consequence,
        evidence = [],
        timeframe = null,
        scope = null
    }) {
        this.affectedActor = affectedActor;
        this.currentCondition = currentCondition;
        this.measurableGap = measurableGap;
        this.consequence = consequence;
        this.evidence = evidence;
        this.timeframe = timeframe;
        this.scope = scope;
    }

    validate() {
        const errors = [];

        if (!this.affectedActor?.trim()) {
            errors.push("Affected actor is missing.");
        }

        if (!this.currentCondition?.trim()) {
            errors.push("Current condition is missing.");
        }

        if (!this.measurableGap?.trim()) {
            errors.push("Measurable gap is missing.");
        }

        if (!this.consequence?.trim()) {
            errors.push("Consequence is missing.");
        }

        if (!Array.isArray(this.evidence) || this.evidence.length === 0) {
            errors.push("Evidence is missing.");
        }

        return errors;
    }

    toText() {
        const scopeText = this.scope ? ` Scope: ${this.scope}.` : "";
        const timeframeText = this.timeframe
            ? ` Timeframe: ${this.timeframe}.`
            : "";

        return (
            `${this.affectedActor} is experiencing ${this.currentCondition}. ` +
            `The measurable gap is ${this.measurableGap}. ` +
            `This matters because ${this.consequence}.` +
            `${scopeText}${timeframeText}`
        );
    }
}

function demonstrateProblemStatements() {
    printSection("1. Problem statement fundamentals");

    const weakStatement =
        "The website needs a better checkout system.";

    const strongStatement = new ProblemStatement({
        affectedActor: "Online customers",
        currentCondition: "abandon purchases during checkout",
        measurableGap:
            "checkout completion is 61% compared with a target of 75%",
        consequence:
            "completed orders are lost and support demand increases",
        evidence: [
            "Analytics show a 39% checkout abandonment rate.",
            "Session analysis shows repeated validation failures.",
            "Interviews indicate uncertainty about delivery charges."
        ],
        timeframe: "the last three months",
        scope: "the web checkout flow"
    });

    console.log("Weak statement:");
    console.log(weakStatement);

    console.log("\nStructured statement:");
    console.log(strongStatement.toText());

    console.log("\nValidation:");
    console.log(strongStatement.validate());
}


// -----------------------------------------------------------------------------
// 3. SYMPTOMS AND ROOT CAUSES
// -----------------------------------------------------------------------------

class CausalNode {
    constructor(name, kind) {
        this.name = name;
        this.kind = kind;
        this.children = [];
    }

    addChild(child) {
        this.children.push(child);
        return child;
    }
}

function printCausalTree(node, depth = 0) {
    console.log(
        `${"  ".repeat(depth)}- [${node.kind}] ${node.name}`
    );

    for (const child of node.children) {
        printCausalTree(child, depth + 1);
    }
}

function demonstrateSymptomsAndRootCauses() {
    printSection("2. Symptoms versus root causes");

    const problem = new CausalNode(
        "Customer support backlog increased",
        "observable problem"
    );

    const symptom = problem.addChild(
        new CausalNode(
            "Average response time increased from 6 to 21 hours",
            "symptom"
        )
    );

    const routingCause = symptom.addChild(
        new CausalNode(
            "Tickets are routed to incorrect queues",
            "contributing cause"
        )
    );

    const taxonomyCause = routingCause.addChild(
        new CausalNode(
            "Routing rules use an obsolete service taxonomy",
            "root cause candidate"
        )
    );

    taxonomyCause.addChild(
        new CausalNode(
            "No recurring process reviews routing accuracy",
            "systemic cause"
        )
    );

    printCausalTree(problem);

    console.log(
        "\nA symptom is an observable manifestation. A root cause is a factor " +
        "that explains the condition and can be validated through evidence. " +
        "There may be several interacting root causes."
    );
}


// -----------------------------------------------------------------------------
// 4. FIVE WHYS
// -----------------------------------------------------------------------------

function fiveWhys(initialProblem, answers) {
    const steps = [];
    let currentCondition = initialProblem;

    for (let index = 0; index < answers.length; index += 1) {
        steps.push({
            why: index + 1,
            question: `Why does this occur?`,
            condition: currentCondition,
            answer: answers[index]
        });

        currentCondition = answers[index];
    }

    return steps;
}

function demonstrateFiveWhys() {
    printSection("3. Five Whys");

    const steps = fiveWhys(
        "Orders are shipped late",
        [
            "Warehouse picking begins later than planned.",
            "Picking waits for manual payment-status confirmation.",
            "Payment exceptions are checked in another system.",
            "The systems do not exchange exception status automatically.",
            "The integration was never designed for exception-state synchronization."
        ]
    );

    for (const step of steps) {
        console.log(
            `Why ${step.why}: ${step.question} ` +
            `Because ${step.condition}.`
        );
        console.log(`Answer: ${step.answer}`);
    }

    console.log(
        "\nFive Whys generates a causal hypothesis. The final answer is not " +
        "automatically proven to be the root cause."
    );
}


// -----------------------------------------------------------------------------
// 5. PROBLEM FRAMING
// -----------------------------------------------------------------------------

class ProblemFrame {
    constructor({
        actor,
        desiredOutcome,
        currentState,
        gap,
        context,
        constraints = [],
        assumptions = [],
        exclusions = [],
        successMetrics = {}
    }) {
        this.actor = actor;
        this.desiredOutcome = desiredOutcome;
        this.currentState = currentState;
        this.gap = gap;
        this.context = context;
        this.constraints = constraints;
        this.assumptions = assumptions;
        this.exclusions = exclusions;
        this.successMetrics = successMetrics;
    }

    render() {
        const lines = [
            `Actor: ${this.actor}`,
            `Desired outcome: ${this.desiredOutcome}`,
            `Current state: ${this.currentState}`,
            `Gap: ${this.gap}`,
            `Context: ${this.context}`,
            "Constraints:"
        ];

        for (const item of this.constraints) {
            lines.push(`  - ${item}`);
        }

        lines.push("Assumptions:");

        for (const item of this.assumptions) {
            lines.push(`  - ${item}`);
        }

        lines.push("Exclusions:");

        for (const item of this.exclusions) {
            lines.push(`  - ${item}`);
        }

        lines.push("Success metrics:");

        for (const [name, definition] of Object.entries(this.successMetrics)) {
            lines.push(`  - ${name}: ${definition}`);
        }

        return lines.join("\n");
    }
}

function demonstrateProblemFraming() {
    printSection("4. Problem framing");

    const frame = new ProblemFrame({
        actor: "Students using an examination portal",
        desiredOutcome: "complete legitimate submissions before the deadline",
        currentState:
            "submissions sometimes fail or remain pending during peak traffic",
        gap:
            "successful submission rate falls below the operational target during peak periods",
        context:
            "online examinations with concentrated submission activity",
        constraints: [
            "Existing authentication must remain unchanged.",
            "Exam deadlines cannot be extended automatically.",
            "Student records must remain protected.",
            "Infrastructure spending is constrained."
        ],
        assumptions: [
            "Examination rules are correct.",
            "Student home internet is outside institutional control.",
            "Submission events are timestamped accurately."
        ],
        exclusions: [
            "Changing examination policy.",
            "Replacing the identity provider.",
            "Diagnosing individual home networks."
        ],
        successMetrics: {
            "submission success rate":
                "successful final submissions divided by final attempts",
            "p95 submission latency":
                "95th percentile time to acknowledge a submission",
            "duplicate submission rate":
                "duplicate final submissions per 1,000 attempts"
        }
    });

    console.log(frame.render());
    return frame;
}


// -----------------------------------------------------------------------------
// 6. PROBLEM BOUNDARIES
// -----------------------------------------------------------------------------

class ProblemBoundary {
    constructor(inside = [], outside = []) {
        this.inside = new Set(inside);
        this.outside = new Set(outside);
    }

    classify(item) {
        if (this.inside.has(item)) {
            return "INSIDE";
        }

        if (this.outside.has(item)) {
            return "OUTSIDE";
        }

        return "UNDEFINED";
    }

    print() {
        console.log("Inside:");
        for (const item of this.inside) {
            console.log(`  [IN]  ${item}`);
        }

        console.log("\nOutside:");
        for (const item of this.outside) {
            console.log(`  [OUT] ${item}`);
        }
    }
}

function demonstrateBoundaries() {
    printSection("5. Problem boundaries");

    const boundary = new ProblemBoundary(
        [
            "submission API",
            "submission database",
            "queueing mechanism",
            "retry logic",
            "portal validation"
        ],
        [
            "student home Wi-Fi",
            "examination policy",
            "internet service providers",
            "student device hardware"
        ]
    );

    boundary.print();

    console.log("\nClassification:");
    for (const item of [
        "submission API",
        "student home Wi-Fi",
        "examination policy",
        "unknown payment provider"
    ]) {
        console.log(`${item}: ${boundary.classify(item)}`);
    }

    return boundary;
}


// -----------------------------------------------------------------------------
// 7. EVIDENCE
// -----------------------------------------------------------------------------

class EvidenceItem {
    constructor(statement, type, confidence, source) {
        this.statement = statement;
        this.type = type;
        this.confidence = confidence;
        this.source = source;
    }

    isValid() {
        return (
            this.confidence >= 0 &&
            this.confidence <= 1 &&
            this.statement.trim().length > 0
        );
    }
}

function demonstrateEvidence() {
    printSection("6. Evidence, assumptions, hypotheses, and opinions");

    const evidence = [
        new EvidenceItem(
            "Checkout abandonment was 39% in August.",
            "measured fact",
            0.98,
            "analytics database"
        ),
        new EvidenceItem(
            "Customers are confused by delivery charges.",
            "interview observation",
            0.78,
            "20 customer interviews"
        ),
        new EvidenceItem(
            "A new checkout page will solve abandonment.",
            "hypothesis",
            0.35,
            "untested proposal"
        ),
        new EvidenceItem(
            "The checkout should look simpler.",
            "opinion",
            0.20,
            "stakeholder preference"
        )
    ];

    for (const item of evidence) {
        console.log(
            `[${item.type.toUpperCase()}] ${item.statement}`
        );
        console.log(
            `  confidence=${(item.confidence * 100).toFixed(0)}%, ` +
            `source=${item.source}, valid=${item.isValid()}`
        );
    }
}


// -----------------------------------------------------------------------------
// 8. METRICS
// -----------------------------------------------------------------------------

class Metric {
    constructor(name, baseline, target, unit, higherIsBetter) {
        this.name = name;
        this.baseline = baseline;
        this.target = target;
        this.unit = unit;
        this.higherIsBetter = higherIsBetter;
    }

    gap() {
        return this.target - this.baseline;
    }

    reached(actual) {
        return this.higherIsBetter
            ? actual >= this.target
            : actual <= this.target;
    }
}

function demonstrateMetrics() {
    printSection("7. Measurable problem gaps");

    const metrics = [
        new Metric(
            "checkout completion rate",
            0.61,
            0.75,
            "%",
            true
        ),
        new Metric(
            "p95 checkout latency",
            8.4,
            3.0,
            "seconds",
            false
        ),
        new Metric(
            "support contacts per 1,000 orders",
            92,
            55,
            "contacts",
            false
        )
    ];

    const actualValues = {
        "checkout completion rate": 0.77,
        "p95 checkout latency": 3.4,
        "support contacts per 1,000 orders": 51
    };

    for (const metric of metrics) {
        const actual = actualValues[metric.name];

        console.log(
            `${metric.name}: baseline=${metric.baseline}, ` +
            `target=${metric.target}, gap=${metric.gap().toFixed(2)}, ` +
            `actual=${actual}, ` +
            `status=${metric.reached(actual) ? "TARGET MET" : "TARGET NOT MET"}`
        );
    }
}


// -----------------------------------------------------------------------------
// 9. CAUSAL HYPOTHESES
// -----------------------------------------------------------------------------

class CausalHypothesis {
    constructor(statement, test, supporting = [], contradicting = []) {
        this.statement = statement;
        this.test = test;
        this.supporting = supporting;
        this.contradicting = contradicting;
    }

    status() {
        if (this.contradicting.length > 0) {
            return "requires revision";
        }

        if (this.supporting.length > 0) {
            return "supported but not proven";
        }

        return "untested";
    }
}

function demonstrateHypotheses() {
    printSection("8. Causal hypotheses");

    const hypothesis = new CausalHypothesis(
        "Payment failures materially contribute to checkout abandonment.",
        "Compare abandonment after payment errors with abandonment after successful authorization.",
        [
            "Payment-error sessions have much higher abandonment.",
            "The effect appears across several weeks."
        ]
    );

    console.log(`Statement: ${hypothesis.statement}`);
    console.log(`Test: ${hypothesis.test}`);
    console.log(`Status: ${hypothesis.status()}`);

    console.log("\nSupporting evidence:");

    for (const item of hypothesis.supporting) {
        console.log(`  + ${item}`);
    }

    console.log(
        "\nAssociation can support a hypothesis without proving causation."
    );
}


// -----------------------------------------------------------------------------
// 10. PARETO ANALYSIS
// -----------------------------------------------------------------------------

function paretoAnalysis(causes) {
    const entries = Object.entries(causes);
    const total = entries.reduce(
        (sum, [, count]) => sum + count,
        0
    );

    if (total <= 0) {
        return [];
    }

    entries.sort((a, b) => b[1] - a[1]);

    let cumulative = 0;

    return entries.map(([name, count]) => {
        cumulative += count;

        return {
            name,
            count,
            cumulativeShare: cumulative / total
        };
    });
}

function demonstratePareto() {
    printSection("9. Pareto-style cause analysis");

    const causes = {
        "payment failures": 410,
        "delivery-price confusion": 230,
        "slow response": 170,
        "validation errors": 110,
        "miscellaneous": 80
    };

    for (const item of paretoAnalysis(causes)) {
        console.log(
            `${item.name.padEnd(30)} ` +
            `${String(item.count).padStart(4)} incidents | ` +
            `cumulative=${(item.cumulativeShare * 100).toFixed(1)}%`
        );
    }

    console.log(
        "\nPareto concentration helps select investigation areas. " +
        "It does not prove which cause is fundamental."
    );
}


// -----------------------------------------------------------------------------
// 11. STAKEHOLDERS
// -----------------------------------------------------------------------------

class Stakeholder {
    constructor(name, role, concern, influence) {
        this.name = name;
        this.role = role;
        this.concern = concern;
        this.influence = influence;
    }
}

function demonstrateStakeholders() {
    printSection("10. Stakeholder perspectives");

    const stakeholders = [
        new Stakeholder(
            "Student",
            "primary user",
            "successful submission before deadline",
            "high"
        ),
        new Stakeholder(
            "Faculty",
            "assessment owner",
            "valid and traceable submissions",
            "high"
        ),
        new Stakeholder(
            "IT operations",
            "system operator",
            "availability and maintainability",
            "high"
        ),
        new Stakeholder(
            "Security",
            "risk owner",
            "confidentiality and integrity",
            "high"
        ),
        new Stakeholder(
            "Finance",
            "budget owner",
            "controlled infrastructure cost",
            "medium"
        )
    ];

    for (const stakeholder of stakeholders) {
        console.log(
            `${stakeholder.name.padEnd(18)} | ` +
            `${stakeholder.role.padEnd(20)} | ` +
            `${stakeholder.concern.padEnd(45)} | ` +
            `influence=${stakeholder.influence}`
        );
    }
}


// -----------------------------------------------------------------------------
// 12. EVENT-DRIVEN DIAGNOSTIC MODEL
// -----------------------------------------------------------------------------

class DiagnosticEventBus {
    constructor() {
        this.handlers = new Map();
    }

    on(eventName, handler) {
        if (!this.handlers.has(eventName)) {
            this.handlers.set(eventName, []);
        }

        this.handlers.get(eventName).push(handler);
    }

    emit(eventName, payload) {
        const handlers = this.handlers.get(eventName) || [];

        for (const handler of handlers) {
            handler(payload);
        }
    }
}

class SubmissionMonitor {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.counters = {
            attempts: 0,
            successes: 0,
            paymentErrors: 0,
            validationErrors: 0,
            timeouts: 0,
            duplicates: 0
        };

        this.eventBus.on("submission.attempt", () => {
            this.counters.attempts += 1;
        });

        this.eventBus.on("submission.success", () => {
            this.counters.successes += 1;
        });

        this.eventBus.on("submission.payment_error", () => {
            this.counters.paymentErrors += 1;
        });

        this.eventBus.on("submission.validation_error", () => {
            this.counters.validationErrors += 1;
        });

        this.eventBus.on("submission.timeout", () => {
            this.counters.timeouts += 1;
        });

        this.eventBus.on("submission.duplicate", () => {
            this.counters.duplicates += 1;
        });
    }

    report() {
        const attempts = this.counters.attempts;

        return {
            ...this.counters,
            successRate: attempts
                ? this.counters.successes / attempts
                : 0,
            failureRate: attempts
                ? 1 - this.counters.successes / attempts
                : 0
        };
    }
}

function demonstrateEventDrivenMonitoring() {
    printSection("11. Event-driven problem evidence collection");

    const eventBus = new DiagnosticEventBus();
    const monitor = new SubmissionMonitor(eventBus);

    const events = [
        "submission.attempt",
        "submission.success",
        "submission.attempt",
        "submission.payment_error",
        "submission.attempt",
        "submission.timeout",
        "submission.attempt",
        "submission.success",
        "submission.attempt",
        "submission.validation_error",
        "submission.attempt",
        "submission.duplicate"
    ];

    for (const eventName of events) {
        eventBus.emit(eventName, {
            timestamp: new Date().toISOString()
        });
    }

    console.log(monitor.report());

    console.log(
        "\nEvent-driven architecture is useful here because evidence can be " +
        "collected from observable system events without hard-coding the " +
        "problem definition into individual requests."
    );
}


// -----------------------------------------------------------------------------
// 13. BOUNDARY LEAKAGE
// -----------------------------------------------------------------------------

function demonstrateBoundaryLeakage() {
    printSection("12. Boundary leakage and responsibility");

    const boundary = {
        inside: new Set([
            "submission API",
            "submission database",
            "retry logic",
            "portal validation"
        ]),
        outside: new Set([
            "student home Wi-Fi",
            "internet provider",
            "examination policy"
        ])
    };

    const questions = [
        "Can the project directly change this component?",
        "Can the project measure its effect?",
        "Can the project mitigate the effect even if it cannot control the cause?",
        "Does including it make the problem unmanageably broad?"
    ];

    for (const question of questions) {
        console.log(`- ${question}`);
    }

    console.log("\nExamples:");

    for (const item of [
        "submission API",
        "student home Wi-Fi",
        "internet provider"
    ]) {
        const classification = boundary.inside.has(item)
            ? "inside"
            : boundary.outside.has(item)
                ? "outside"
                : "undefined";

        console.log(`${item}: ${classification}`);
    }
}


// -----------------------------------------------------------------------------
// 14. PROBLEM QUALITY CHECKS
// -----------------------------------------------------------------------------

function inspectProblemStatement(statement) {
    const issues = [];

    const text = statement.toText().toLowerCase();

    const solutionWords = [
        "build ",
        "implement ",
        "deploy ",
        "replace ",
        "automate ",
        "migrate "
    ];

    for (const word of solutionWords) {
        if (text.includes(word)) {
            issues.push(`Possible solution bias: "${word.trim()}"`);
        }
    }

    if (statement.evidence.length === 0) {
        issues.push("No evidence is attached.");
    }

    if (!/\d/.test(statement.measurableGap)) {
        issues.push(
            "The measurable gap does not appear to contain a numeric baseline or target."
        );
    }

    if (!statement.scope) {
        issues.push("Scope has not been explicitly bounded.");
    }

    return issues;
}

function demonstrateQualityChecks() {
    printSection("13. Debugging a weak problem definition");

    const weakStatement = new ProblemStatement({
        affectedActor: "The company",
        currentCondition: "has a bad application",
        measurableGap: "bad performance",
        consequence: "users are unhappy",
        evidence: []
    });

    console.log(weakStatement.toText());

    const issues = inspectProblemStatement(weakStatement);

    for (const issue of issues) {
        console.log(`- ${issue}`);
    }

    console.log(
        "\nThe purpose of a problem-definition review is to make the condition " +
        "observable, bounded, measurable, and testable."
    );
}


// -----------------------------------------------------------------------------
// 15. CASE STUDY DATA
// -----------------------------------------------------------------------------

const examinationRecords = [
    {
        date: "2026-08-01",
        attempts: 12000,
        successful: 11160,
        paymentErrors: 330,
        validationErrors: 210,
        timeouts: 240,
        duplicates: 18
    },
    {
        date: "2026-08-02",
        attempts: 12100,
        successful: 11253,
        paymentErrors: 340,
        validationErrors: 195,
        timeouts: 312,
        duplicates: 20
    },
    {
        date: "2026-08-03",
        attempts: 11900,
        successful: 11007,
        paymentErrors: 420,
        validationErrors: 180,
        timeouts: 293,
        duplicates: 19
    },
    {
        date: "2026-08-04",
        attempts: 12500,
        successful: 11375,
        paymentErrors: 510,
        validationErrors: 205,
        timeouts: 410,
        duplicates: 24
    },
    {
        date: "2026-08-05",
        attempts: 12800,
        successful: 11456,
        paymentErrors: 570,
        validationErrors: 220,
        timeouts: 554,
        duplicates: 28
    },
    {
        date: "2026-08-06",
        attempts: 13000,
        successful: 11570,
        paymentErrors: 610,
        validationErrors: 230,
        timeouts: 590,
        duplicates: 31
    },
    {
        date: "2026-08-07",
        attempts: 13200,
        successful: 11616,
        paymentErrors: 640,
        validationErrors: 245,
        timeouts: 699,
        duplicates: 35
    }
];

function analyzeExaminationRecords(records) {
    const totals = records.reduce(
        (accumulator, record) => {
            accumulator.attempts += record.attempts;
            accumulator.successful += record.successful;
            accumulator.paymentErrors += record.paymentErrors;
            accumulator.validationErrors += record.validationErrors;
            accumulator.timeouts += record.timeouts;
            accumulator.duplicates += record.duplicates;

            return accumulator;
        },
        {
            attempts: 0,
            successful: 0,
            paymentErrors: 0,
            validationErrors: 0,
            timeouts: 0,
            duplicates: 0
        }
    );

    const rate = (value) =>
        totals.attempts === 0 ? 0 : value / totals.attempts;

    return {
        ...totals,
        successRate: rate(totals.successful),
        failureRate: 1 - rate(totals.successful),
        paymentErrorRate: rate(totals.paymentErrors),
        validationErrorRate: rate(totals.validationErrors),
        timeoutRate: rate(totals.timeouts),
        duplicateRate: rate(totals.duplicates)
    };
}

function demonstrateCaseStudy() {
    printSection(
        "14. Industry-style case study: examination submission reliability"
    );

    const analysis = analyzeExaminationRecords(examinationRecords);

    console.log(analysis);

    console.log("\nDaily observations:");

    for (const record of examinationRecords) {
        console.log(
            `${record.date}: ` +
            `success=${((record.successful / record.attempts) * 100).toFixed(2)}%, ` +
            `payment=${record.paymentErrors}, ` +
            `validation=${record.validationErrors}, ` +
            `timeouts=${record.timeouts}, ` +
            `duplicates=${record.duplicates}`
        );
    }

    console.log(
        "\nInterpretation:\n" +
        "The data establishes an observed reliability problem. It does not by " +
        "itself establish whether payment failures, timeouts, validation, " +
        "traffic volume, or interactions among them are the root cause."
    );
}


// -----------------------------------------------------------------------------
// 16. ASYNCHRONOUS INVESTIGATION SIMULATION
// -----------------------------------------------------------------------------

function delay(milliseconds) {
    return new Promise((resolve) => {
        setTimeout(resolve, milliseconds);
    });
}

async function investigateHypothesis(name, evidenceSource) {
    await delay(20);

    return {
        name,
        evidenceSource,
        result: evidenceSource.includes("correlation")
            ? "association detected; causality remains unproven"
            : "evidence collected"
    };
}

async function demonstrateAsyncInvestigation() {
    printSection("15. Asynchronous investigation workflow");

    const hypotheses = [
        ["Payment errors contribute to abandonment", "correlation in payment logs"],
        ["Timeouts increase duplicate submissions", "event sequence analysis"],
        ["Validation messages cause user exits", "session replay analysis"]
    ];

    // Promise.all demonstrates concurrent evidence collection. In real systems,
    // concurrency must respect rate limits, data access controls, and resource limits.
    const results = await Promise.all(
        hypotheses.map(([name, source]) =>
            investigateHypothesis(name, source)
        )
    );

    for (const result of results) {
        console.log(
            `${result.name}: ${result.result} [source=${result.evidenceSource}]`
        );
    }
}


// -----------------------------------------------------------------------------
// 17. EDGE CASES
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    printSection("16. Edge cases");

    const cases = [
        {
            name: "Multiple root causes",
            description:
                "Capacity limits, deployment defects, dependency failures, and weak monitoring may interact."
        },
        {
            name: "One cause, multiple symptoms",
            description:
                "One identity-service failure may produce login failures, API errors, and support tickets."
        },
        {
            name: "Changing baseline",
            description:
                "A metric can change because the user population, traffic, or measurement definition changed."
        },
        {
            name: "Rare severe failure",
            description:
                "Averages can hide low-frequency events whose consequences are unacceptable."
        },
        {
            name: "External cause",
            description:
                "The root cause may be outside the project boundary even when mitigation is inside it."
        },
        {
            name: "Unknown cause",
            description:
                "A problem can be valid and measurable before its root cause is known."
        },
        {
            name: "Metric optimization conflict",
            description:
                "Improving latency can reduce validation and damage data integrity."
        }
    ];

    for (const item of cases) {
        console.log(`${item.name}: ${item.description}`);
    }
}


// -----------------------------------------------------------------------------
// 18. COMPLEXITY
// -----------------------------------------------------------------------------

function demonstrateComplexity() {
    printSection("17. Performance and computational considerations");

    const data = examinationRecords;

    // reduce performs one pass: O(n) time and O(1) auxiliary state.
    const totalAttempts = data.reduce(
        (sum, record) => sum + record.attempts,
        0
    );

    console.log(`Total attempts: ${totalAttempts.toLocaleString()}`);

    const causes = [
        ["payment", 3420],
        ["timeouts", 3098],
        ["validation", 1485],
        ["duplicates", 175]
    ];

    // Sorting causes costs O(k log k), where k is the number of categories.
    causes.sort((a, b) => b[1] - a[1]);

    console.log("Sorted causes:");

    for (const [name, count] of causes) {
        console.log(`  ${name}: ${count}`);
    }
}


// -----------------------------------------------------------------------------
// 19. SECURITY AND PRIVACY
// -----------------------------------------------------------------------------

function demonstrateSecurity() {
    printSection("18. Security and privacy considerations");

    const rules = [
        "Collect only evidence necessary to define and investigate the problem.",
        "Avoid exposing personal identifiers in diagnostic output.",
        "Use least privilege for sensitive operational data.",
        "Record access to protected evidence.",
        "Redact identifiers when aggregate information is sufficient.",
        "Treat manipulated metrics as a possible governance or security issue.",
        "Do not define a security problem only by describing a technical symptom."
    ];

    for (const rule of rules) {
        console.log(`- ${rule}`);
    }
}


// -----------------------------------------------------------------------------
// 20. PRACTICAL TRANSFORMATIONS
// -----------------------------------------------------------------------------

function demonstrateTransformations() {
    printSection("19. Weak-to-strong problem transformations");

    const transformations = [
        [
            "The app is slow.",
            "Mobile users experience 6.8-second p95 latency on order history, above the 2.5-second target."
        ],
        [
            "Customers hate support.",
            "First-contact resolution is 54%, causing 46% of support cases to require another interaction."
        ],
        [
            "The database needs replacement.",
            "Order queries exceed the latency target during peak load; investigation must distinguish query design, indexing, locking, capacity, and architecture."
        ],
        [
            "Build an AI fraud detector.",
            "Fraud losses increased while manual review capacity stayed fixed; the problem is to identify preventable losses and the transaction patterns associated with them."
        ]
    ];

    for (const [weak, strong] of transformations) {
        console.log(`Weak:   ${weak}`);
        console.log(`Strong: ${strong}\n`);
    }
}


// -----------------------------------------------------------------------------
// 21. COMPLETE WORKFLOW
// -----------------------------------------------------------------------------

function problemDefinitionWorkflow() {
    return [
        "Observe the undesirable condition",
        "Identify affected actors",
        "Establish evidence and baseline",
        "Define the desired condition",
        "State the measurable gap",
        "Document context",
        "Separate symptoms from causal hypotheses",
        "Investigate causes",
        "Define boundaries and exclusions",
        "Document constraints and assumptions",
        "Define success metrics",
        "Validate the framing"
    ];
}

function demonstrateWorkflow() {
    printSection("20. End-to-end problem-definition workflow");

    problemDefinitionWorkflow().forEach(
        (stage, index) => console.log(`${index + 1}. ${stage}`)
    );
}


// -----------------------------------------------------------------------------
// 22. MAIN
// -----------------------------------------------------------------------------

async function main() {
    printSection("PROBLEM DEFINITION STUDY PROGRAM");

    console.log(
        "Topic: problem statements, symptoms versus root causes, " +
        "problem framing, and problem boundaries"
    );

    demonstrateProblemStatements();
    demonstrateSymptomsAndRootCauses();
    demonstrateFiveWhys();
    demonstrateProblemFraming();
    demonstrateBoundaries();
    demonstrateEvidence();
    demonstrateMetrics();
    demonstrateHypotheses();
    demonstratePareto();
    demonstrateStakeholders();
    demonstrateEventDrivenMonitoring();
    demonstrateBoundaryLeakage();
    demonstrateQualityChecks();
    demonstrateCaseStudy();
    await demonstrateAsyncInvestigation();
    demonstrateEdgeCases();
    demonstrateComplexity();
    demonstrateSecurity();
    demonstrateTransformations();
    demonstrateWorkflow();

    printSection("FINAL PRACTICE PROBLEM");

    const practice = new ProblemStatement({
        affectedActor: "Retail customers",
        currentCondition: "abandon carts before payment completion",
        measurableGap:
            "conversion is 58% while the agreed target is 70%",
        consequence:
            "orders and expected revenue are lost",
        evidence: [
            "Analytics show high exits on the payment step.",
            "Payment-error sessions show higher abandonment.",
            "The effect is concentrated during evening traffic peaks."
        ],
        timeframe: "the previous six weeks",
        scope: "the web purchase flow"
    });

    console.log(practice.toText());
    console.log("Validation:", practice.validate());

    console.log(
        "\nCore discipline: define what is happening before deciding why it " +
        "is happening, and investigate why it is happening before selecting " +
        "what should be changed."
    );
}

main().catch((error) => {
    console.error("Program failed:", error.message);
    process.exitCode = 1;
});
