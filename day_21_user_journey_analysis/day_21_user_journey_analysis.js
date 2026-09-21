/*
USER JOURNEY ANALYSIS
=====================

Topic:
Touchpoints, pain points, moments of truth, friction, emotions, opportunities

This file demonstrates user journey analysis with JavaScript-specific
patterns including objects, classes, arrays, higher-order functions,
validation, aggregation, immutable transformations, error handling,
serialization, and lightweight analytical calculations.

The example models a digital banking journey.
*/


// ============================================================================
// 1. CORE DATA MODEL
// ============================================================================

const Emotion = Object.freeze({
    VERY_NEGATIVE: -2,
    NEGATIVE: -1,
    NEUTRAL: 0,
    POSITIVE: 1,
    VERY_POSITIVE: 2
});

const JourneyStage = Object.freeze({
    AWARENESS: "Awareness",
    CONSIDERATION: "Consideration",
    SIGNUP: "Signup",
    ONBOARDING: "Onboarding",
    FIRST_USE: "First Use",
    SUPPORT: "Support"
});


class Touchpoint {
    constructor({
        name,
        channel,
        action,
        effortMinutes,
        emotion,
        painScore,
        frictionScore,
        importance,
        momentOfTruth = false,
        evidence = []
    }) {
        this.name = name;
        this.channel = channel;
        this.action = action;
        this.effortMinutes = effortMinutes;
        this.emotion = emotion;
        this.painScore = painScore;
        this.frictionScore = frictionScore;
        this.importance = importance;
        this.momentOfTruth = momentOfTruth;
        this.evidence = evidence;

        this.validate();
    }

    validate() {
        if (!this.name?.trim()) {
            throw new Error("Touchpoint name is required.");
        }

        if (this.effortMinutes < 0) {
            throw new Error("Effort cannot be negative.");
        }

        for (const [name, value] of [
            ["painScore", this.painScore],
            ["frictionScore", this.frictionScore],
            ["importance", this.importance]
        ]) {
            if (!Number.isFinite(value) || value < 0 || value > 10) {
                throw new Error(`${name} must be between 0 and 10.`);
            }
        }
    }
}


class JourneyStageData {
    constructor({
        stage,
        userGoal,
        userActions,
        expectations,
        touchpoints
    }) {
        this.stage = stage;
        this.userGoal = userGoal;
        this.userActions = userActions;
        this.expectations = expectations;
        this.touchpoints = touchpoints;

        if (!userGoal?.trim()) {
            throw new Error("A journey stage requires a user goal.");
        }
    }
}


class Journey {
    constructor({ persona, goal, stages }) {
        this.persona = persona;
        this.goal = goal;
        this.stages = stages;

        if (!persona?.trim()) {
            throw new Error("Persona is required.");
        }

        if (!stages.length) {
            throw new Error("At least one journey stage is required.");
        }
    }

    getAllTouchpoints() {
        return this.stages.flatMap(stage => stage.touchpoints);
    }
}


// ============================================================================
// 2. CREATE THE JOURNEY
// ============================================================================

function createBankingJourney() {
    return new Journey({
        persona: "First-time digital banking customer",
        goal: "Open an account and complete the first transaction",
        stages: [
            new JourneyStageData({
                stage: JourneyStage.AWARENESS,
                userGoal: "Find a trustworthy account.",
                userActions: [
                    "Searches online",
                    "Reviews product information",
                    "Checks fees"
                ],
                expectations: [
                    "Clear pricing",
                    "Simple eligibility",
                    "Trust"
                ],
                touchpoints: [
                    new Touchpoint({
                        name: "Search result",
                        channel: "Search",
                        action: "Opens product page",
                        effortMinutes: 2,
                        emotion: Emotion.POSITIVE,
                        painScore: 2,
                        frictionScore: 1,
                        importance: 5,
                        evidence: ["Search analytics"]
                    }),
                    new Touchpoint({
                        name: "Pricing page",
                        channel: "Website",
                        action: "Reviews fees",
                        effortMinutes: 5,
                        emotion: Emotion.NEUTRAL,
                        painScore: 5,
                        frictionScore: 5,
                        importance: 7,
                        momentOfTruth: true,
                        evidence: [
                            "Users struggle to locate fee information"
                        ]
                    })
                ]
            }),

            new JourneyStageData({
                stage: JourneyStage.CONSIDERATION,
                userGoal: "Decide whether the account is suitable.",
                userActions: [
                    "Reads FAQs",
                    "Checks eligibility",
                    "Compares benefits"
                ],
                expectations: [
                    "Accurate information",
                    "Easy comparison"
                ],
                touchpoints: [
                    new Touchpoint({
                        name: "Eligibility FAQ",
                        channel: "Website",
                        action: "Checks requirements",
                        effortMinutes: 7,
                        emotion: Emotion.NEUTRAL,
                        painScore: 4,
                        frictionScore: 4,
                        importance: 6,
                        evidence: ["FAQ search behavior"]
                    })
                ]
            }),

            new JourneyStageData({
                stage: JourneyStage.SIGNUP,
                userGoal: "Start the application.",
                userActions: [
                    "Enters information",
                    "Accepts terms",
                    "Submits form"
                ],
                expectations: [
                    "Few unnecessary fields",
                    "Visible progress"
                ],
                touchpoints: [
                    new Touchpoint({
                        name: "Signup form",
                        channel: "Web application",
                        action: "Completes registration",
                        effortMinutes: 8,
                        emotion: Emotion.POSITIVE,
                        painScore: 3,
                        frictionScore: 3,
                        importance: 8,
                        evidence: ["Form completion analytics"]
                    })
                ]
            }),

            new JourneyStageData({
                stage: JourneyStage.ONBOARDING,
                userGoal: "Complete identity verification.",
                userActions: [
                    "Uploads document",
                    "Corrects errors",
                    "Waits for confirmation"
                ],
                expectations: [
                    "Clear instructions",
                    "Fast verification",
                    "Secure handling"
                ],
                touchpoints: [
                    new Touchpoint({
                        name: "Identity verification",
                        channel: "Mobile app",
                        action: "Uploads identity document",
                        effortMinutes: 15,
                        emotion: Emotion.NEGATIVE,
                        painScore: 8,
                        frictionScore: 8,
                        importance: 10,
                        momentOfTruth: true,
                        evidence: [
                            "High abandonment",
                            "Repeated upload attempts"
                        ]
                    })
                ]
            }),

            new JourneyStageData({
                stage: JourneyStage.FIRST_USE,
                userGoal: "Make the first successful transaction.",
                userActions: [
                    "Adds funds",
                    "Selects recipient",
                    "Confirms transfer"
                ],
                expectations: [
                    "Clear confirmation",
                    "Immediate status"
                ],
                touchpoints: [
                    new Touchpoint({
                        name: "First transaction",
                        channel: "Mobile app",
                        action: "Completes transfer",
                        effortMinutes: 4,
                        emotion: Emotion.VERY_POSITIVE,
                        painScore: 1,
                        frictionScore: 1,
                        importance: 10,
                        momentOfTruth: true,
                        evidence: ["Transaction success rate"]
                    })
                ]
            }),

            new JourneyStageData({
                stage: JourneyStage.SUPPORT,
                userGoal: "Resolve a problem.",
                userActions: [
                    "Opens help",
                    "Searches articles",
                    "Contacts support"
                ],
                expectations: [
                    "Fast answer",
                    "No repeated information"
                ],
                touchpoints: [
                    new Touchpoint({
                        name: "Support chatbot",
                        channel: "In-app support",
                        action: "Searches for transaction help",
                        effortMinutes: 10,
                        emotion: Emotion.NEGATIVE,
                        painScore: 7,
                        frictionScore: 7,
                        importance: 8,
                        momentOfTruth: true,
                        evidence: ["Support transcripts"]
                    })
                ]
            })
        ]
    });
}


// ============================================================================
// 3. GENERIC ANALYTICAL HELPERS
// ============================================================================

const average = values =>
    values.length === 0
        ? 0
        : values.reduce((sum, value) => sum + value, 0) / values.length;


const clamp = (value, minimum, maximum) =>
    Math.min(Math.max(value, minimum), maximum);


function painPriority(touchpoint) {
    return (
        touchpoint.painScore *
        touchpoint.frictionScore *
        touchpoint.importance
    ) / 100;
}


function emotionalScore(touchpoint) {
    return touchpoint.emotion;
}


function customerEffort(touchpoints) {
    if (!touchpoints.length) {
        return 0;
    }

    const scores = touchpoints.map(point => {
        const timeComponent =
            clamp(point.effortMinutes / 20, 0, 1) * 5;

        const frictionComponent =
            point.frictionScore / 10 * 5;

        return timeComponent + frictionComponent;
    });

    return average(scores);
}


// ============================================================================
// 4. JOURNEY MAP OUTPUT
// ============================================================================

function printJourneyMap(journey) {
    console.log("\n" + "=".repeat(78));
    console.log("JOURNEY MAP");
    console.log("=".repeat(78));

    journey.stages.forEach((stage, index) => {
        console.log(`\n${index + 1}. ${stage.stage}`);
        console.log(`Goal: ${stage.userGoal}`);

        console.log("Actions:");
        stage.userActions.forEach(action =>
            console.log(`  - ${action}`)
        );

        console.log("Touchpoints:");
        stage.touchpoints.forEach(point => {
            console.log(
                `  - ${point.name} | ` +
                `channel=${point.channel} | ` +
                `pain=${point.painScore}/10 | ` +
                `friction=${point.frictionScore}/10 | ` +
                `emotion=${point.emotion}`
            );
        });
    });
}


// ============================================================================
// 5. PAIN AND FRICTION PRIORITIZATION
// ============================================================================

function rankPainPoints(journey) {
    return journey
        .getAllTouchpoints()
        .filter(
            point =>
                point.painScore >= 5 ||
                point.frictionScore >= 5
        )
        .map(point => ({
            name: point.name,
            pain: point.painScore,
            friction: point.frictionScore,
            importance: point.importance,
            priority: painPriority(point)
        }))
        .sort((a, b) => b.priority - a.priority);
}


function printPainPoints(journey) {
    console.log("\n" + "=".repeat(78));
    console.log("PAIN POINT PRIORITIZATION");
    console.log("=".repeat(78));

    rankPainPoints(journey).forEach(item => {
        console.log(
            `${item.name.padEnd(25)} | ` +
            `pain=${item.pain} | ` +
            `friction=${item.friction} | ` +
            `importance=${item.importance} | ` +
            `priority=${item.priority.toFixed(2)}`
        );
    });
}


// ============================================================================
// 6. MOMENTS OF TRUTH
// ============================================================================

function getMomentsOfTruth(journey) {
    return journey
        .getAllTouchpoints()
        .filter(point => point.momentOfTruth);
}


function printMomentsOfTruth(journey) {
    console.log("\n" + "=".repeat(78));
    console.log("MOMENTS OF TRUTH");
    console.log("=".repeat(78));

    getMomentsOfTruth(journey).forEach(point => {
        console.log(
            `${point.name} | ` +
            `emotion=${point.emotion} | ` +
            `importance=${point.importance}/10`
        );
    });
}


// ============================================================================
// 7. EMOTIONAL CURVE
// ============================================================================

function printEmotionalCurve(journey) {
    console.log("\n" + "=".repeat(78));
    console.log("EMOTIONAL CURVE");
    console.log("=".repeat(78));

    journey.stages.forEach(stage => {
        const score = average(
            stage.touchpoints.map(emotionalScore)
        );

        const bars = "█".repeat(Math.max(0, Math.round((score + 2) * 5)));

        console.log(
            `${stage.stage.padEnd(18)} | ` +
            `${score.toFixed(2).padStart(5)} | ${bars}`
        );
    });
}


// ============================================================================
// 8. CHANNEL ANALYSIS USING MAP
// ============================================================================

function analyzeChannels(journey) {
    const channels = new Map();

    journey.getAllTouchpoints().forEach(point => {
        if (!channels.has(point.channel)) {
            channels.set(point.channel, []);
        }

        channels.get(point.channel).push(point);
    });

    console.log("\n" + "=".repeat(78));
    console.log("CHANNEL ANALYSIS");
    console.log("=".repeat(78));

    for (const [channel, points] of channels) {
        console.log(
            `${channel.padEnd(20)} | ` +
            `count=${String(points.length).padStart(2)} | ` +
            `pain=${average(points.map(p => p.painScore)).toFixed(2)} | ` +
            `friction=${average(points.map(p => p.frictionScore)).toFixed(2)} | ` +
            `effort=${average(points.map(p => p.effortMinutes)).toFixed(2)} min`
        );
    }
}


// ============================================================================
// 9. FUNNEL ANALYSIS
// ============================================================================

function analyzeFunnel(stages) {
    console.log("\n" + "=".repeat(78));
    console.log("FUNNEL ANALYSIS");
    console.log("=".repeat(78));

    stages.forEach(stage => {
        const completion =
            stage.entered === 0
                ? 0
                : stage.completed / stage.entered;

        const abandonment = 1 - completion;

        console.log(
            `${stage.name.padEnd(24)} | ` +
            `entered=${String(stage.entered).padStart(6)} | ` +
            `completed=${String(stage.completed).padStart(6)} | ` +
            `completion=${(completion * 100).toFixed(1)}% | ` +
            `abandonment=${(abandonment * 100).toFixed(1)}%`
        );
    });
}


// ============================================================================
// 10. SEGMENTATION
// ============================================================================

function analyzeSegments() {
    const segmentData = {
        "First-time users": [4, 5, 3, 4, 5],
        "Returning users": [8, 9, 7, 8, 9],
        "Mobile users": [6, 5, 7, 6, 5],
        "Desktop users": [7, 6, 5, 7, 6]
    };

    console.log("\n" + "=".repeat(78));
    console.log("SEGMENT ANALYSIS");
    console.log("=".repeat(78));

    Object.entries(segmentData).forEach(([segment, scores]) => {
        console.log(
            `${segment.padEnd(20)} | ` +
            `mean=${average(scores).toFixed(2)} | ` +
            `min=${Math.min(...scores)} | ` +
            `max=${Math.max(...scores)}`
        );
    });
}


// ============================================================================
// 11. OPPORTUNITY DISCOVERY
// ============================================================================

function generateOpportunities(journey) {
    return journey
        .getAllTouchpoints()
        .filter(
            point =>
                point.painScore >= 5 ||
                point.frictionScore >= 5
        )
        .map(point => {
            let direction;

            if (point.name === "Identity verification") {
                direction =
                    "Add format guidance, examples, immediate validation, " +
                    "progress feedback, and recovery paths.";
            } else if (point.name === "Support chatbot") {
                direction =
                    "Improve intent recognition, contextual responses, " +
                    "and human escalation.";
            } else if (point.name === "Pricing page") {
                direction =
                    "Make important fees and conditions visible in plain language.";
            } else {
                direction =
                    "Investigate the root cause before selecting a solution.";
            }

            const impact = point.importance;
            const confidence = point.evidence.length ? 0.8 : 0.4;
            const effort = 5;

            return {
                problem: point.name,
                userNeed: "Complete the task with less uncertainty and effort.",
                direction,
                impact,
                confidence,
                effort,
                score: impact * confidence / effort
            };
        })
        .sort((a, b) => b.score - a.score);
}


function printOpportunities(journey) {
    console.log("\n" + "=".repeat(78));
    console.log("OPPORTUNITIES");
    console.log("=".repeat(78));

    generateOpportunities(journey).forEach(opportunity => {
        console.log(`\nProblem: ${opportunity.problem}`);
        console.log(`Need: ${opportunity.userNeed}`);
        console.log(`Direction: ${opportunity.direction}`);
        console.log(`Priority aid: ${opportunity.score.toFixed(3)}`);
    });
}


// ============================================================================
// 12. SERVICE BLUEPRINT
// ============================================================================

function buildServiceBlueprint() {
    return [
        {
            stage: "Signup",
            customerAction: "Submits registration",
            frontstage: "Form validates data",
            backstage: "Identity service processes data",
            support: "Database and validation services",
            risk: 3
        },
        {
            stage: "Verification",
            customerAction: "Uploads document",
            frontstage: "App displays status",
            backstage: "Verification service processes document",
            support: "Storage, OCR, verification provider",
            risk: 8
        },
        {
            stage: "Transaction",
            customerAction: "Confirms transfer",
            frontstage: "App shows transaction status",
            backstage: "Payment service updates ledger",
            support: "Fraud and transaction systems",
            risk: 6
        }
    ];
}


function printBlueprint(blueprint) {
    console.log("\n" + "=".repeat(78));
    console.log("SERVICE BLUEPRINT");
    console.log("=".repeat(78));

    blueprint.forEach(step => {
        console.log(`\n${step.stage}`);
        console.log(`  Customer: ${step.customerAction}`);
        console.log(`  Frontstage: ${step.frontstage}`);
        console.log(`  Backstage: ${step.backstage}`);
        console.log(`  Support: ${step.support}`);
        console.log(`  Failure risk: ${step.risk}/10`);
    });
}


// ============================================================================
// 13. ROOT-CAUSE ANALYSIS
// ============================================================================

function fiveWhys(problem, causes) {
    console.log("\n" + "=".repeat(78));
    console.log("FIVE WHYS");
    console.log("=".repeat(78));
    console.log(`Observed problem: ${problem}`);

    causes.slice(0, 5).forEach((cause, index) => {
        console.log(`Why ${index + 1}: ${cause}`);
    });
}


// ============================================================================
// 14. EXPECTATION GAP
// ============================================================================

function expectationGap(expected, perceived) {
    return perceived - expected;
}


function demonstrateExpectationGaps() {
    console.log("\n" + "=".repeat(78));
    console.log("EXPECTATION GAPS");
    console.log("=".repeat(78));

    const scenarios = [
        ["Verification", 8, 4],
        ["First transaction", 8, 9],
        ["Support", 7, 3],
        ["Pricing clarity", 7, 5]
    ];

    scenarios.forEach(([name, expected, perceived]) => {
        const gap = expectationGap(expected, perceived);

        console.log(
            `${name.padEnd(20)} | ` +
            `expected=${expected} | ` +
            `perceived=${perceived} | ` +
            `gap=${gap > 0 ? "+" : ""}${gap}`
        );
    });
}


// ============================================================================
// 15. JOURNEY VARIABILITY
// ============================================================================

function standardDeviation(values) {
    if (values.length === 0) {
        return 0;
    }

    const averageValue = average(values);
    const variance = average(
        values.map(value => (value - averageValue) ** 2)
    );

    return Math.sqrt(variance);
}


function calculateFrictionVariability(journey) {
    const frictionScores =
        journey.getAllTouchpoints().map(point => point.frictionScore);

    return standardDeviation(frictionScores);
}


// ============================================================================
// 16. STRUCTURED EXPORT
// ============================================================================

function exportJourney(journey) {
    /*
    JSON.stringify is useful when journey-analysis data needs to move from a
    JavaScript application to a server, analytics pipeline, or stored file.
    */
    return JSON.stringify(journey, null, 2);
}


// ============================================================================
// 17. ERROR HANDLING
// ============================================================================

function demonstrateValidationFailure() {
    console.log("\n" + "=".repeat(78));
    console.log("VALIDATION AND ERROR HANDLING");
    console.log("=".repeat(78));

    try {
        new Touchpoint({
            name: "Invalid touchpoint",
            channel: "Test",
            action: "Test",
            effortMinutes: -5,
            emotion: Emotion.NEUTRAL,
            painScore: 5,
            frictionScore: 5,
            importance: 5
        });
    } catch (error) {
        console.log(`Expected validation error: ${error.message}`);
    }

    try {
        new Touchpoint({
            name: "Invalid score",
            channel: "Test",
            action: "Test",
            effortMinutes: 1,
            emotion: Emotion.NEUTRAL,
            painScore: 15,
            frictionScore: 5,
            importance: 5
        });
    } catch (error) {
        console.log(`Expected validation error: ${error.message}`);
    }
}


// ============================================================================
// 18. ASYNCHRONOUS JOURNEY DATA SIMULATION
// ============================================================================

function loadJourneyEvidence() {
    /*
    Real products often retrieve journey evidence from APIs. Promise-based
    code models that asynchronous behavior without requiring an external
    service.
    */
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                source: "analytics-service",
                verificationAbandonment: 0.42,
                supportEscalation: 0.28,
                transactionSuccess: 0.81
            });
        }, 10);
    });
}


async function demonstrateAsyncEvidence() {
    const evidence = await loadJourneyEvidence();

    console.log("\n" + "=".repeat(78));
    console.log("ASYNC EVIDENCE");
    console.log("=".repeat(78));

    console.log(
        `Verification abandonment: ` +
        `${(evidence.verificationAbandonment * 100).toFixed(1)}%`
    );

    console.log(
        `Support escalation: ` +
        `${(evidence.supportEscalation * 100).toFixed(1)}%`
    );

    console.log(
        `Transaction success: ` +
        `${(evidence.transactionSuccess * 100).toFixed(1)}%`
    );
}


// ============================================================================
// 19. PERFORMANCE CONSIDERATIONS
// ============================================================================

function benchmarkTouchpointAggregation(journey) {
    /*
    flatMap creates a convenient flattened collection. For very large
    datasets, streaming or incremental aggregation can reduce memory usage.
    */
    const start = performance.now();

    let totalPain = 0;

    for (const point of journey.getAllTouchpoints()) {
        totalPain += point.painScore;
    }

    const elapsed = performance.now() - start;

    console.log("\n" + "=".repeat(78));
    console.log("PERFORMANCE");
    console.log("=".repeat(78));
    console.log(`Total pain: ${totalPain.toFixed(2)}`);
    console.log(`Aggregation time: ${elapsed.toFixed(4)} ms`);
    console.log(
        "For large production datasets, database-side aggregation, "
        + "streaming, indexing, and pre-aggregation may be preferable."
    );
}


// ============================================================================
// 20. RESEARCH AND EXPERIMENT DESIGN
// ============================================================================

function createExperiment() {
    return {
        hypothesis:
            "Clearer document guidance will increase verification completion.",
        change:
            "Show accepted formats, examples, validation, and progress.",
        primaryMetric:
            "Verification completion rate",
        guardrailMetric:
            "Verification error rate",
        successCondition:
            "Completion increases without a material increase in errors."
    };
}


function printExperiment(experiment) {
    console.log("\n" + "=".repeat(78));
    console.log("EXPERIMENT DESIGN");
    console.log("=".repeat(78));

    Object.entries(experiment).forEach(([key, value]) => {
        console.log(`${key}: ${value}`);
    });
}


// ============================================================================
// 21. MAIN
// ============================================================================

async function main() {
    const journey = createBankingJourney();

    printJourneyMap(journey);
    printPainPoints(journey);
    printMomentsOfTruth(journey);
    printEmotionalCurve(journey);
    analyzeChannels(journey);

    console.log("\n" + "=".repeat(78));
    console.log("CUSTOMER EFFORT");
    console.log("=".repeat(78));
    console.log(
        `Effort index: ${customerEffort(journey.getAllTouchpoints()).toFixed(2)}/10`
    );

    printOpportunities(journey);

    analyzeFunnel([
        { name: "Product page", entered: 10000, completed: 7200 },
        { name: "Application start", entered: 7200, completed: 5900 },
        { name: "Verification start", entered: 5900, completed: 3400 },
        { name: "Verification complete", entered: 3400, completed: 2950 },
        { name: "First transaction", entered: 2950, completed: 2400 }
    ]);

    analyzeSegments();

    printBlueprint(buildServiceBlueprint());

    fiveWhys(
        "Users abandon verification",
        [
            "Some uploads fail.",
            "Accepted formats are unclear.",
            "Validation occurs too late.",
            "Recovery paths are weak.",
            "Failure scenarios were not sufficiently represented in design."
        ]
    );

    demonstrateExpectationGaps();

    console.log("\n" + "=".repeat(78));
    console.log("FRICTION VARIABILITY");
    console.log("=".repeat(78));
    console.log(
        `Standard deviation: ${calculateFrictionVariability(journey).toFixed(2)}`
    );

    console.log("\n" + "=".repeat(78));
    console.log("JSON EXPORT");
    console.log("=".repeat(78));
    console.log(exportJourney(journey).slice(0, 2500));

    demonstrateValidationFailure();
    await demonstrateAsyncEvidence();
    benchmarkTouchpointAggregation(journey);
    printExperiment(createExperiment());

    console.log("\n" + "=".repeat(78));
    console.log("END OF USER JOURNEY ANALYSIS");
    console.log("=".repeat(78));
}


main().catch(error => {
    console.error("Application error:", error.message);
    process.exitCode = 1;
});
