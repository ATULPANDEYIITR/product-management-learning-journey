"use strict";

/*
 * Event-driven UX research and product-design workspace.
 * Runtime: Node.js 18 or later. Dependencies: Node.js standard library.
 *
 * The model uses events to connect research intake, synthesis, screen review,
 * prototype telemetry, critique management, and readiness evaluation.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class DomainError extends Error {
    constructor(message) {
        super(message);
        this.name = "DomainError";
    }
}

const PHASE = Object.freeze({
    DISCOVERY: "discovery",
    SYNTHESIZED: "synthesized",
    DESIGN: "design",
    VALIDATED: "validated"
});

const SEVERITY = Object.freeze({
    LOW: "low",
    MEDIUM: "medium",
    HIGH: "high",
    CRITICAL: "critical"
});

function requireText(value, field) {
    if (typeof value !== "string" || value.trim().length === 0) {
        throw new DomainError(`${field} must be a non-empty string.`);
    }
}

function validateEvidence(item) {
    requireText(item.id, "Evidence ID");
    requireText(item.participantRef, "Participant reference");
    requireText(item.observation, "Observation");
    requireText(item.method, "Research method");

    if (item.observation.length > 600) {
        throw new DomainError("Observation exceeds 600 characters.");
    }
    if (!Number.isInteger(item.severity) || item.severity < 1 || item.severity > 5) {
        throw new DomainError("Severity must be an integer from 1 to 5.");
    }
    if (!Number.isFinite(item.confidence) || item.confidence < 0 || item.confidence > 1) {
        throw new DomainError("Confidence must be between 0 and 1.");
    }
    if (!["interview", "survey", "observation", "usability_test"].includes(item.method)) {
        throw new DomainError("Unsupported research method.");
    }
}

function relativeLuminance(hex) {
    if (!/^#[0-9a-fA-F]{6}$/.test(hex)) {
        throw new DomainError(`Invalid color value: ${hex}`);
    }

    const values = [1, 3, 5].map(index => parseInt(hex.slice(index, index + 2), 16));
    const channels = values.map(channel => {
        const value = channel / 255;
        return value <= 0.04045
            ? value / 12.92
            : ((value + 0.055) / 1.055) ** 2.4;
    });

    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function contrastRatio(foreground, background) {
    const first = relativeLuminance(foreground);
    const second = relativeLuminance(background);
    return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
}

class UXStudio extends EventEmitter {
    constructor(projectName, designSystem) {
        super();
        requireText(projectName, "Project name");

        this.projectName = projectName;
        this.designSystem = designSystem;
        this.phase = PHASE.DISCOVERY;

        this.evidence = new Map();
        this.themes = new Map();
        this.screens = new Map();
        this.tasks = [];
        this.critiques = new Map();
        this.events = [];
        this.eventIds = new Set();
    }

    recordEvent(event) {
        requireText(event.eventId, "Event ID");
        requireText(event.type, "Event type");

        // Event identifiers prevent duplicate telemetry from inflating metrics.
        if (this.eventIds.has(event.eventId)) {
            throw new DomainError(`Duplicate telemetry event: ${event.eventId}`);
        }

        this.eventIds.add(event.eventId);
        this.events.push(Object.freeze({ ...event, recordedAt: new Date().toISOString() }));
        this.emit("telemetry", event);
    }

    addEvidence(item) {
        if (this.phase !== PHASE.DISCOVERY) {
            throw new DomainError("Evidence intake is closed after synthesis.");
        }
        validateEvidence(item);

        if (this.evidence.has(item.id)) {
            throw new DomainError(`Duplicate evidence ID: ${item.id}`);
        }

        this.evidence.set(item.id, Object.freeze({ ...item }));
        this.recordEvent({
            eventId: `evidence:${item.id}`,
            type: "evidence-added",
            subjectId: item.id
        });
    }

    addTheme(theme) {
        if (this.phase !== PHASE.DISCOVERY) {
            throw new DomainError("Themes can only be defined during discovery.");
        }

        requireText(theme.id, "Theme ID");
        requireText(theme.name, "Theme name");

        if (this.themes.has(theme.id)) {
            throw new DomainError(`Duplicate theme ID: ${theme.id}`);
        }
        if (!Array.isArray(theme.evidenceIds) || theme.evidenceIds.length === 0) {
            throw new DomainError("A theme must reference evidence.");
        }
        if (new Set(theme.evidenceIds).size !== theme.evidenceIds.length) {
            throw new DomainError("Duplicate evidence references in a theme.");
        }
        if (!Number.isFinite(theme.effortHours) || theme.effortHours <= 0) {
            throw new DomainError("Theme effort must be positive.");
        }

        for (const id of theme.evidenceIds) {
            if (!this.evidence.has(id)) {
                throw new DomainError(`Theme references missing evidence: ${id}`);
            }
        }

        this.themes.set(theme.id, Object.freeze({
            ...theme,
            evidenceIds: Object.freeze([...theme.evidenceIds])
        }));
    }

    async synthesize() {
        if (this.phase !== PHASE.DISCOVERY) {
            throw new DomainError("Synthesis requires the discovery phase.");
        }
        if (this.evidence.size < 3 || this.themes.size < 2) {
            throw new DomainError("Synthesis requires three evidence items and two themes.");
        }

        // Independent theme computations can run concurrently.
        const scores = await Promise.all(
            [...this.themes.values()].map(async theme => {
                const linked = theme.evidenceIds.map(id => this.evidence.get(id));
                const severity = linked.reduce((sum, item) => sum + item.severity, 0) / linked.length;
                const confidence = linked.reduce((sum, item) => sum + item.confidence, 0) / linked.length;
                const score = linked.length * severity * confidence / theme.effortHours;

                return {
                    themeId: theme.id,
                    name: theme.name,
                    evidenceCount: linked.length,
                    averageSeverity: Number(severity.toFixed(2)),
                    averageConfidence: Number(confidence.toFixed(2)),
                    effortHours: theme.effortHours,
                    priorityScore: Number(score.toFixed(3))
                };
            })
        );

        scores.sort((a, b) => b.priorityScore - a.priorityScore);
        this.phase = PHASE.SYNTHESIZED;
        this.emit("synthesis-completed", scores);
        return scores;
    }

    startDesign() {
        if (this.phase !== PHASE.SYNTHESIZED) {
            throw new DomainError("Design requires completed research synthesis.");
        }
        this.phase = PHASE.DESIGN;
        this.emit("design-started", { project: this.projectName });
    }

    validateDesignSystem() {
        const errors = [];

        for (const pair of this.designSystem.contrastPairs) {
            const foreground = this.designSystem.tokens[pair.foreground];
            const background = this.designSystem.tokens[pair.background];

            if (!foreground || !background) {
                errors.push(`Missing contrast token pair: ${pair.foreground}/${pair.background}`);
                continue;
            }

            try {
                const ratio = contrastRatio(foreground, background);
                if (ratio < 4.5) {
                    errors.push(`Contrast ${ratio.toFixed(2)}:1 is below 4.5:1.`);
                }
            } catch (error) {
                errors.push(error.message);
            }
        }

        return errors;
    }

    validateScreen(screen) {
        const errors = [];
        requireText(screen.id, "Screen ID");
        requireText(screen.accessibleName, "Accessible screen name");

        if (!Array.isArray(screen.components) || screen.components.length === 0) {
            errors.push(`${screen.id}: screen must contain components.`);
            return errors;
        }

        const interactive = [];
        for (const name of screen.components) {
            const component = this.designSystem.components[name];

            if (!component) {
                errors.push(`${screen.id}: unknown component ${name}.`);
                continue;
            }
            if (component.interactive) {
                interactive.push(name);
            }
            if (!component.keyboardAccessible) {
                errors.push(`${screen.id}: ${name} is not keyboard accessible.`);
            }
            if (!component.accessibleDescription) {
                errors.push(`${screen.id}: ${name} lacks an accessible description.`);
            }
        }

        if (JSON.stringify(interactive) !== JSON.stringify(screen.keyboardOrder)) {
            errors.push(`${screen.id}: keyboard order does not match interactive layout order.`);
        }

        for (const token of screen.requiredTokens) {
            if (!(token in this.designSystem.tokens)) {
                errors.push(`${screen.id}: missing design token ${token}.`);
            }
        }

        return errors;
    }

    addScreen(screen) {
        if (this.phase !== PHASE.DESIGN) {
            throw new DomainError("Screens can only be registered during design.");
        }
        if (this.screens.has(screen.id)) {
            throw new DomainError(`Duplicate screen ID: ${screen.id}`);
        }

        const errors = this.validateScreen(screen);
        if (errors.length > 0) {
            throw new DomainError(errors.join(" "));
        }

        this.screens.set(screen.id, Object.freeze({
            ...screen,
            components: Object.freeze([...screen.components]),
            keyboardOrder: Object.freeze([...screen.keyboardOrder]),
            requiredTokens: Object.freeze([...screen.requiredTokens])
        }));
        this.emit("screen-registered", { screenId: screen.id });
    }

    recordTask(result) {
        if (this.phase !== PHASE.DESIGN) {
            throw new DomainError("Prototype testing requires the design phase.");
        }
        requireText(result.participantRef, "Participant reference");
        requireText(result.taskName, "Task name");

        if (!this.screens.has(result.screenId)) {
            throw new DomainError(`Unknown screen: ${result.screenId}`);
        }
        if (!Number.isFinite(result.durationSeconds) || result.durationSeconds <= 0) {
            throw new DomainError("Task duration must be positive.");
        }
        if (!Number.isInteger(result.criticalErrors) || result.criticalErrors < 0) {
            throw new DomainError("Critical error count must be a non-negative integer.");
        }

        this.tasks.push(Object.freeze({ ...result }));
        this.recordEvent({
            eventId: `task:${this.tasks.length}:${result.participantRef}`,
            type: "usability-task-recorded",
            subjectId: result.screenId
        });
    }

    addCritique(issue) {
        requireText(issue.id, "Critique ID");
        requireText(issue.heuristic, "Heuristic");
        requireText(issue.description, "Critique description");
        requireText(issue.recommendation, "Critique recommendation");

        if (!this.screens.has(issue.screenId)) {
            throw new DomainError("Critique references an unknown screen.");
        }
        if (!Object.values(SEVERITY).includes(issue.severity)) {
            throw new DomainError("Invalid critique severity.");
        }
        if (this.critiques.has(issue.id)) {
            throw new DomainError(`Duplicate critique ID: ${issue.id}`);
        }

        this.critiques.set(issue.id, { ...issue, resolved: Boolean(issue.resolved) });
        this.emit("critique-added", { issueId: issue.id, severity: issue.severity });
    }

    resolveCritique(issueId) {
        const issue = this.critiques.get(issueId);
        if (!issue) {
            throw new DomainError(`Unknown critique ID: ${issueId}`);
        }

        issue.resolved = true;
        this.emit("critique-resolved", { issueId });
    }

    async evaluateReadiness() {
        if (this.phase !== PHASE.DESIGN) {
            throw new DomainError("Readiness evaluation requires the design phase.");
        }

        const [systemErrors, screenErrors] = await Promise.all([
            Promise.resolve(this.validateDesignSystem()),
            Promise.resolve(
                [...this.screens.values()].flatMap(screen => this.validateScreen(screen))
            )
        ]);

        const blockers = [...systemErrors, ...screenErrors];

        if (this.screens.size < 2) {
            blockers.push("At least two screens are required.");
        }
        if (this.tasks.length < 5) {
            blockers.push("At least five usability task results are required.");
        }

        const successCount = this.tasks.filter(task => task.succeeded).length;
        const successRate = this.tasks.length ? successCount / this.tasks.length : 0;
        const criticalErrors = this.tasks.reduce((sum, task) => sum + task.criticalErrors, 0);

        if (successRate < 0.8) {
            blockers.push("Task success rate is below 80%.");
        }
        if (criticalErrors > 0) {
            blockers.push(`Prototype testing recorded ${criticalErrors} critical errors.`);
        }

        const unresolvedCritical = [...this.critiques.values()].filter(
            issue => issue.severity === SEVERITY.CRITICAL && !issue.resolved
        );

        if (unresolvedCritical.length > 0) {
            blockers.push(
                `Unresolved critical critiques: ${unresolvedCritical.map(issue => issue.id).join(", ")}`
            );
        }

        const durationTotal = this.tasks.reduce(
            (sum, task) => sum + task.durationSeconds, 0
        );
        const report = {
            project: this.projectName,
            phase: this.phase,
            eligible: blockers.length === 0,
            blockers,
            screenCount: this.screens.size,
            taskCount: this.tasks.length,
            taskSuccessRate: Number(successRate.toFixed(3)),
            averageDurationSeconds: this.tasks.length
                ? Number((durationTotal / this.tasks.length).toFixed(1))
                : null,
            criticalErrors,
            telemetryEvents: this.events.length
        };

        if (report.eligible) {
            this.phase = PHASE.VALIDATED;
            report.phase = this.phase;
        }

        this.emit("readiness-evaluated", report);
        return report;
    }
}

function createExampleStudio() {
    const studio = new UXStudio("City Transit Companion", {
        tokens: {
            "color.text": "#17212B",
            "color.surface": "#FFFFFF",
            "color.action": "#1247A8",
            "space.medium": "16px"
        },
        contrastPairs: [
            { foreground: "color.text", background: "color.surface" },
            { foreground: "color.action", background: "color.surface" }
        ],
        components: {
            SearchField: {
                interactive: true,
                keyboardAccessible: true,
                accessibleDescription: "Origin and destination input"
            },
            PrimaryButton: {
                interactive: true,
                keyboardAccessible: true,
                accessibleDescription: "Submit route search"
            },
            RouteCard: {
                interactive: true,
                keyboardAccessible: true,
                accessibleDescription: "Selectable journey option"
            }
        }
    });

    const evidence = [
        { id: "E01", participantRef: "P-001", observation: "Transfer requirements are unclear.", severity: 5, confidence: 0.95, method: "interview" },
        { id: "E02", participantRef: "P-002", observation: "Transfer points are difficult to identify.", severity: 4, confidence: 0.90, method: "observation" },
        { id: "E03", participantRef: "P-003", observation: "Users compare journeys by total time.", severity: 3, confidence: 0.85, method: "interview" },
        { id: "E04", participantRef: "P-004", observation: "The full fare is difficult to locate.", severity: 5, confidence: 0.95, method: "interview" },
        { id: "E05", participantRef: "P-005", observation: "Fare presentation is inconsistent.", severity: 4, confidence: 0.90, method: "survey" },
        { id: "E06", participantRef: "P-006", observation: "Users need to compare fare categories.", severity: 3, confidence: 0.85, method: "observation" }
    ];

    for (const item of evidence) {
        studio.addEvidence(item);
    }

    studio.addTheme({
        id: "T01",
        name: "Transfer uncertainty",
        evidenceIds: ["E01", "E02", "E03"],
        effortHours: 8
    });

    studio.addTheme({
        id: "T02",
        name: "Fare transparency",
        evidenceIds: ["E04", "E05", "E06"],
        effortHours: 5
    });

    return studio;
}

async function main() {
    const studio = createExampleStudio();

    studio.on("synthesis-completed", themes => {
        console.log("\nSYNTHESIS EVENT");
        for (const theme of themes) {
            console.log(`${theme.name}: priority ${theme.priorityScore}`);
        }
    });

    studio.on("readiness-evaluated", report => {
        console.log("\nREADINESS EVENT");
        console.log(JSON.stringify(report, null, 2));
    });

    const synthesis = await studio.synthesize();
    assert.equal(synthesis.length, 2);

    studio.startDesign();

    studio.addScreen({
        id: "S01",
        accessibleName: "Search for a public transport journey",
        components: ["SearchField", "PrimaryButton"],
        keyboardOrder: ["SearchField", "PrimaryButton"],
        requiredTokens: ["color.text", "color.surface", "color.action"]
    });

    studio.addScreen({
        id: "S02",
        accessibleName: "Available journey options",
        components: ["RouteCard", "PrimaryButton"],
        keyboardOrder: ["RouteCard", "PrimaryButton"],
        requiredTokens: ["color.text", "color.surface", "color.action"]
    });

    studio.addCritique({
        id: "C01",
        screenId: "S02",
        heuristic: "Visibility of system status",
        severity: SEVERITY.MEDIUM,
        description: "Selected route state is not persistent.",
        recommendation: "Use a visible selected state and accessible announcement."
    });

    studio.addCritique({
        id: "C02",
        screenId: "S01",
        heuristic: "Error prevention",
        severity: SEVERITY.CRITICAL,
        description: "The initial prototype accepts an empty origin.",
        recommendation: "Validate the origin before calculating a route."
    });
    studio.resolveCritique("C02");

    const testResults = [
        { participantRef: "P-007", taskName: "Find fastest route", screenId: "S01", succeeded: true, durationSeconds: 62, criticalErrors: 0 },
        { participantRef: "P-008", taskName: "Compare journey options", screenId: "S02", succeeded: true, durationSeconds: 75, criticalErrors: 0 },
        { participantRef: "P-009", taskName: "Identify transfers", screenId: "S02", succeeded: true, durationSeconds: 81, criticalErrors: 0 },
        { participantRef: "P-010", taskName: "Find complete fare", screenId: "S02", succeeded: false, durationSeconds: 110, criticalErrors: 0 },
        { participantRef: "P-011", taskName: "Search return journey", screenId: "S01", succeeded: true, durationSeconds: 69, criticalErrors: 0 }
    ];

    for (const result of testResults) {
        studio.recordTask(result);
    }

    studio.recordEvent({
        eventId: "prototype:v1:published",
        type: "prototype-published",
        subjectId: "prototype-v1"
    });

    const readiness = await studio.evaluateReadiness();
    assert.equal(readiness.eligible, true);
    assert.equal(studio.phase, PHASE.VALIDATED);

    // Duplicate telemetry is rejected rather than counted twice.
    assert.throws(
        () => studio.recordEvent({
            eventId: "prototype:v1:published",
            type: "prototype-published",
            subjectId: "prototype-v1"
        }),
        DomainError
    );
}

main().catch(error => {
    console.error(`UX workflow failed: ${error.message}`);
    process.exitCode = 1;
});
