"use strict";

/**
 * Roadmap Communication Engine
 *
 * Audience-specific communication using:
 * - Event-driven roadmap updates
 * - Map and Set collections
 * - Dependency evaluation
 * - Communication policies
 * - Asynchronous report generation
 * - Version-controlled snapshots
 * - Node.js JSON file operations
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only
 */

const fs = require("node:fs/promises");
const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");

const Audience = Object.freeze({
    EXECUTIVE: "executive",
    ENGINEERING: "engineering",
    SALES: "sales",
    CUSTOMER: "customer"
});

const Status = Object.freeze({
    PLANNED: "planned",
    IN_PROGRESS: "in_progress",
    BLOCKED: "blocked",
    AT_RISK: "at_risk",
    COMPLETED: "completed",
    CANCELLED: "cancelled"
});

const Priority = Object.freeze({
    CRITICAL: "critical",
    HIGH: "high",
    MEDIUM: "medium",
    LOW: "low"
});

const Confidence = Object.freeze({
    HIGH: "high",
    MEDIUM: "medium",
    LOW: "low"
});

const VALID_STATUSES = new Set(Object.values(Status));
const VALID_PRIORITIES = new Set(Object.values(Priority));
const VALID_CONFIDENCE = new Set(Object.values(Confidence));

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class RoadmapError extends Error {
    constructor(message) {
        super(message);
        this.name = "RoadmapError";
    }
}

function validateDate(value, field) {
    if (typeof value !== "string" ||
        !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        throw new ValidationError(`${field} must use YYYY-MM-DD.`);
    }

    const parsed = new Date(`${value}T00:00:00Z`);

    if (Number.isNaN(parsed.getTime()) ||
        parsed.toISOString().slice(0, 10) !== value) {
        throw new ValidationError(`${field} is not a valid calendar date.`);
    }
}

function validateText(value, field) {
    if (typeof value !== "string" || !value.trim()) {
        throw new ValidationError(`${field} cannot be empty.`);
    }
}

class RoadmapItem {
    constructor(data) {
        validateText(data.id, "ID");
        validateText(data.title, "Title");
        validateText(data.owner, "Owner");
        validateText(data.objective, "Objective");

        if (!VALID_STATUSES.has(data.status)) {
            throw new ValidationError("Invalid roadmap status.");
        }

        if (!VALID_PRIORITIES.has(data.priority)) {
            throw new ValidationError("Invalid priority.");
        }

        if (!VALID_CONFIDENCE.has(data.confidence)) {
            throw new ValidationError("Invalid confidence.");
        }

        validateDate(data.startDate, "Start date");
        validateDate(data.targetDate, "Target date");

        if (data.targetDate < data.startDate) {
            throw new ValidationError("Target date precedes start date.");
        }

        const progress = data.progress ?? 0;

        if (!Number.isFinite(progress) || progress < 0 || progress > 100) {
            throw new ValidationError("Progress must be between 0 and 100.");
        }

        if (data.status === Status.PLANNED && progress > 0) {
            throw new ValidationError(
                "Planned items cannot have implementation progress."
            );
        }

        this.id = data.id;
        this.title = data.title;
        this.description = data.description ?? "";
        this.owner = data.owner;
        this.objective = data.objective;
        this.businessValue = data.businessValue ?? "";
        this.engineeringDetails = data.engineeringDetails ?? "";
        this.salesMessage = data.salesMessage ?? "";
        this.customerImpact = data.customerImpact ?? "";
        this.startDate = data.startDate;
        this.targetDate = data.targetDate;
        this.priority = data.priority;
        this.status = data.status;
        this.confidence = data.confidence;
        this.progress = data.status === Status.COMPLETED ? 100 : progress;
        this.risk = data.risk ?? null;
        this.dependencies = new Set(data.dependencies ?? []);
        this.milestones = Object.freeze([...(data.milestones ?? [])]);
    }
}

class RoadmapEngine extends EventEmitter {
    #items = new Map();
    #version = 1;
    #history = [];

    constructor(name, owner) {
        super();

        validateText(name, "Roadmap name");
        validateText(owner, "Roadmap owner");

        this.name = name;
        this.owner = owner;
    }

    get version() {
        return this.#version;
    }

    get items() {
        return [...this.#items.values()];
    }

    addItem(data) {
        const item = data instanceof RoadmapItem
            ? data
            : new RoadmapItem(data);

        if (this.#items.has(item.id)) {
            throw new ValidationError(`Duplicate ID: ${item.id}`);
        }

        this.#items.set(item.id, item);

        try {
            this.#validateDependencies();
        } catch (error) {
            this.#items.delete(item.id);
            throw error;
        }

        this.#record("ITEM_ADDED", item.id);
        return item;
    }

    getItem(id) {
        const item = this.#items.get(id);

        if (!item) {
            throw new RoadmapError(`Roadmap item ${id} not found.`);
        }

        return item;
    }

    updateStatus(id, newStatus, progress) {
        const item = this.getItem(id);

        if (!VALID_STATUSES.has(newStatus)) {
            throw new ValidationError("Invalid status transition target.");
        }

        if (item.status === Status.CANCELLED) {
            throw new RoadmapError("Cancelled items are immutable.");
        }

        if (item.status === Status.COMPLETED &&
            newStatus !== Status.COMPLETED) {
            throw new RoadmapError(
                "Completed items require a correction workflow."
            );
        }

        const newProgress = progress ?? item.progress;

        if (!Number.isFinite(newProgress) ||
            newProgress < 0 || newProgress > 100) {
            throw new ValidationError("Invalid progress.");
        }

        if (newStatus === Status.PLANNED && newProgress > 0) {
            throw new ValidationError(
                "Planned items cannot have implementation progress."
            );
        }

        const previous = {
            status: item.status,
            progress: item.progress
        };

        item.status = newStatus;
        item.progress = newStatus === Status.COMPLETED ? 100 : newProgress;

        this.#record("STATUS_UPDATED", id, previous);
        return item;
    }

    #record(event, itemId, previous = null) {
        this.#version++;

        const record = Object.freeze({
            event,
            itemId,
            previous,
            version: this.#version,
            timestamp: new Date().toISOString()
        });

        this.#history.push(record);
        this.emit("roadmapChanged", record);
    }

    #validateDependencies() {
        const visited = new Set();
        const active = new Set();

        const visit = (id) => {
            if (active.has(id)) {
                throw new ValidationError("Circular dependency detected.");
            }

            if (visited.has(id)) return;

            const item = this.getItem(id);
            active.add(id);

            for (const dependency of item.dependencies) {
                if (!this.#items.has(dependency)) {
                    throw new ValidationError(
                        `Unknown dependency: ${dependency}`
                    );
                }

                visit(dependency);
            }

            active.delete(id);
            visited.add(id);
        };

        for (const id of this.#items.keys()) {
            visit(id);
        }
    }

    dependenciesReady(id) {
        const item = this.getItem(id);

        return [...item.dependencies].every(
            dependency =>
                this.getItem(dependency).status === Status.COMPLETED
        );
    }

    calculateProgress() {
        const active = this.items.filter(
            item => item.status !== Status.CANCELLED
        );

        if (active.length === 0) return 0;

        return active.reduce(
            (sum, item) => sum + item.progress,
            0
        ) / active.length;
    }

    getRisks() {
        return this.items.filter(
            item =>
                item.status === Status.BLOCKED ||
                item.status === Status.AT_RISK ||
                item.risk !== null
        );
    }

    generate(audience) {
        const renderers = {
            [Audience.EXECUTIVE]: this.#executive.bind(this),
            [Audience.ENGINEERING]: this.#engineering.bind(this),
            [Audience.SALES]: this.#sales.bind(this),
            [Audience.CUSTOMER]: this.#customer.bind(this)
        };

        if (!Object.hasOwn(renderers, audience)) {
            throw new ValidationError("Unsupported audience.");
        }

        return renderers[audience]();
    }

    #executive() {
        const lines = [
            `EXECUTIVE ROADMAP: ${this.name}`,
            `Accountable owner: ${this.owner}`,
            `Portfolio progress: ${this.calculateProgress().toFixed(1)}%`,
            "",
            "STRATEGIC INITIATIVES"
        ];

        for (const item of this.items) {
            lines.push(
                `${item.title} | ${item.status}`,
                `Objective: ${item.objective}`,
                `Business value: ${item.businessValue}`,
                `Target: ${item.targetDate}`,
                `Confidence: ${item.confidence}`,
                `Risk: ${item.risk ?? "None reported"}`,
                ""
            );
        }

        lines.push("DECISION ATTENTION");

        for (const item of this.getRisks()) {
            lines.push(
                `${item.title}: ${item.risk ?? item.status}`
            );
        }

        return lines.join("\n");
    }

    #engineering() {
        const lines = [
            `ENGINEERING ROADMAP: ${this.name}`,
            ""
        ];

        for (const item of this.items) {
            lines.push(
                `INITIATIVE: ${item.title}`,
                `Owner: ${item.owner}`,
                `Priority: ${item.priority}`,
                `Status: ${item.status}`,
                `Implementation: ${item.engineeringDetails}`,
                `Progress: ${item.progress}%`,
                `Dependencies: ${[...item.dependencies].join(", ") || "None"}`,
                `Dependency readiness: ${this.dependenciesReady(item.id)}`,
                `Target: ${item.targetDate}`,
                `Risk: ${item.risk ?? "None"}`,
                ""
            );
        }

        return lines.join("\n");
    }

    #sales() {
        const lines = [`SALES ROADMAP: ${this.name}`, ""];

        for (const item of this.items) {
            if (item.status === Status.CANCELLED) continue;

            lines.push(
                `FEATURE: ${item.title}`,
                `Customer value: ${item.businessValue}`,
                `Positioning: ${item.salesMessage}`,
                `Availability: ${item.status}`,
                `Target date: ${item.targetDate}`,
                `Confidence: ${item.confidence}`,
                ""
            );
        }

        lines.push(
            "Only released capabilities may be represented as currently available."
        );

        return lines.join("\n");
    }

    #customer() {
        const lines = [`CUSTOMER ROADMAP: ${this.name}`, ""];

        for (const item of this.items) {
            if ([Status.BLOCKED, Status.CANCELLED].includes(item.status)) {
                continue;
            }

            const statusMap = {
                [Status.PLANNED]: "Planned",
                [Status.IN_PROGRESS]: "In development",
                [Status.AT_RISK]: "Under review",
                [Status.COMPLETED]: "Completed"
            };

            lines.push(
                `FEATURE: ${item.title}`,
                `Status: ${statusMap[item.status]}`,
                `Customer impact: ${item.customerImpact || item.businessValue}`,
                `Target: ${item.targetDate}`,
                ""
            );
        }

        lines.push(
            "Target dates are estimates and may change as delivery conditions evolve."
        );

        return lines.join("\n");
    }

    async generateReport(audience, filepath) {
        const content = this.generate(audience);

        // Restrict generated report paths to local JSON/TXT output.
        if (![".txt", ".json"].includes(
            require("node:path").extname(filepath).toLowerCase()
        )) {
            throw new ValidationError("Only TXT and JSON reports are supported.");
        }

        await fs.writeFile(filepath, content, {
            encoding: "utf8",
            flag: "w"
        });

        return {
            filepath,
            audience,
            version: this.#version,
            checksum: crypto
                .createHash("sha256")
                .update(content)
                .digest("hex")
        };
    }

    exportData() {
        return {
            name: this.name,
            owner: this.owner,
            version: this.#version,
            items: this.items.map(item => ({
                ...item,
                dependencies: [...item.dependencies]
            }))
        };
    }

    getHistory() {
        return [...this.#history];
    }
}

async function main() {
    const roadmap = new RoadmapEngine(
        "Enterprise Platform 2027",
        "Product Management Office"
    );

    roadmap.on("roadmapChanged", event => {
        console.log(
            `[EVENT] ${event.event}: ${event.itemId}, version ${event.version}`
        );
    });

    roadmap.addItem({
        id: "RM-001",
        title: "Identity Management",
        owner: "Platform Engineering",
        objective: "Improve enterprise security.",
        businessValue: "Centralized authentication.",
        engineeringDetails: "OIDC, OAuth 2.0 and RBAC.",
        salesMessage: "Enterprise identity controls.",
        customerImpact: "Improved account protection.",
        startDate: "2026-10-01",
        targetDate: "2026-12-15",
        priority: Priority.CRITICAL,
        status: Status.COMPLETED,
        progress: 100,
        confidence: Confidence.HIGH
    });

    roadmap.addItem({
        id: "RM-002",
        title: "Analytics Dashboard",
        owner: "Data Engineering",
        objective: "Improve decision visibility.",
        businessValue: "Faster operational decisions.",
        engineeringDetails: "Event ingestion and analytics APIs.",
        salesMessage: "Operational analytics capabilities.",
        customerImpact: "Business performance visibility.",
        startDate: "2026-11-01",
        targetDate: "2027-02-15",
        priority: Priority.HIGH,
        status: Status.IN_PROGRESS,
        progress: 55,
        confidence: Confidence.MEDIUM,
        dependencies: ["RM-001"]
    });

    roadmap.addItem({
        id: "RM-003",
        title: "Automated Reporting",
        owner: "BI Team",
        objective: "Standardize reporting.",
        businessValue: "Reduced manual reporting.",
        engineeringDetails: "Scheduled jobs and report exports.",
        salesMessage: "Scheduled business reports.",
        customerImpact: "Consistent reporting.",
        startDate: "2026-11-15",
        targetDate: "2027-03-15",
        priority: Priority.HIGH,
        status: Status.AT_RISK,
        progress: 20,
        confidence: Confidence.LOW,
        risk: "Data integration capacity constraints.",
        dependencies: ["RM-002"]
    });

    console.log("\nPORTFOLIO PROGRESS");
    console.log(`${roadmap.calculateProgress().toFixed(2)}%`);

    for (const audience of Object.values(Audience)) {
        console.log("\n" + "=".repeat(65));
        console.log(roadmap.generate(audience));
    }

    const report = await roadmap.generateReport(
        Audience.EXECUTIVE,
        "executive-roadmap.txt"
    );

    await fs.writeFile(
        "roadmap-data.json",
        JSON.stringify(roadmap.exportData(), null, 2),
        { encoding: "utf8" }
    );

    console.log("\nREPORT GENERATED");
    console.log(report);

    console.log("\nEVENT HISTORY");
    console.log(roadmap.getHistory().length);

    console.log("\nVALIDATION TESTS");

    if (!roadmap.dependenciesReady("RM-002")) {
        throw new Error("Completed dependency should be ready.");
    }

    if (roadmap.dependenciesReady("RM-003")) {
        throw new Error("Incomplete dependency must not be ready.");
    }

    try {
        roadmap.addItem({
            id: "RM-004",
            title: "Invalid Feature",
            owner: "Testing",
            objective: "Test validation",
            startDate: "2027-05-01",
            targetDate: "2027-01-01",
            priority: Priority.LOW,
            status: Status.PLANNED
        });

        throw new Error("Invalid dates were accepted.");
    } catch (error) {
        if (!(error instanceof ValidationError)) throw error;
        console.log("Invalid date correctly rejected.");
    }

    console.log("All tests passed.");
}

main().catch(error => {
    console.error("Roadmap processing failed:", error.message);
    process.exitCode = 1;
});
