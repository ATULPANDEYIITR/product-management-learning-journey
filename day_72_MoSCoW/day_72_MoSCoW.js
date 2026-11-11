"use strict";

/*
 * MoSCoW Requirements Prioritization
 * Runtime: Node.js 18+
 *
 * Provides:
 * - Event-driven requirement management.
 * - Four MoSCoW priority categories.
 * - Dependency validation.
 * - Release capacity evaluation.
 * - Immutable change events.
 * - Asynchronous JSON persistence.
 * - Automated validation tests.
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const EventEmitter = require("node:events");

const Priority = Object.freeze({
    MUST: "Must-have",
    SHOULD: "Should-have",
    COULD: "Could-have",
    WONT: "Won't-have"
});

const Status = Object.freeze({
    PROPOSED: "Proposed",
    APPROVED: "Approved",
    IN_PROGRESS: "In progress",
    COMPLETED: "Completed",
    DEFERRED: "Deferred"
});

const VALID_PRIORITIES = new Set(Object.values(Priority));
const VALID_STATUSES = new Set(Object.values(Status));

class PrioritizationError extends Error {}

class RequirementNotFoundError extends PrioritizationError {}

function validateRequirement(input) {
    if (!input || typeof input !== "object") {
        throw new TypeError("Requirement must be an object.");
    }

    const {
        id,
        title,
        description = "",
        priority,
        businessValue,
        effort,
        owner,
        dependencies = [],
        status = Status.PROPOSED
    } = input;

    if (typeof id !== "string" || !id.trim()) {
        throw new TypeError("A valid requirement ID is required.");
    }

    if (typeof title !== "string" || !title.trim()) {
        throw new TypeError("A valid title is required.");
    }

    if (!VALID_PRIORITIES.has(priority)) {
        throw new TypeError("Invalid MoSCoW priority.");
    }

    if (!Number.isInteger(businessValue) ||
        businessValue < 1 || businessValue > 10) {
        throw new RangeError("Business value must be 1-10.");
    }

    if (!Number.isInteger(effort) || effort < 1 || effort > 100) {
        throw new RangeError("Effort must be 1-100.");
    }

    if (typeof owner !== "string" || !owner.trim()) {
        throw new TypeError("A requirement owner is required.");
    }

    if (!Array.isArray(dependencies) ||
        dependencies.some(d => typeof d !== "string") ||
        new Set(dependencies).size !== dependencies.length) {
        throw new TypeError("Dependencies must be unique string IDs.");
    }

    if (!VALID_STATUSES.has(status)) {
        throw new TypeError("Invalid requirement status.");
    }

    return {
        id: id.trim(),
        title: title.trim(),
        description: String(description),
        priority,
        businessValue,
        effort,
        owner: owner.trim(),
        dependencies: [...dependencies],
        status,
        createdAt: new Date().toISOString()
    };
}

class MoSCoWEngine extends EventEmitter {
    #requirements = new Map();
    #history = [];

    get history() {
        return this.#history.map(event => ({ ...event }));
    }

    get requirements() {
        return [...this.#requirements.values()]
            .map(item => structuredClone(item));
    }

    add(input) {
        const requirement = validateRequirement(input);

        if (this.#requirements.has(requirement.id)) {
            throw new PrioritizationError(
                `Duplicate requirement: ${requirement.id}`
            );
        }

        if (requirement.dependencies.includes(requirement.id)) {
            throw new PrioritizationError(
                "Self-dependencies are prohibited."
            );
        }

        this.#requirements.set(requirement.id, requirement);

        try {
            this.#validateGraph();
        } catch (error) {
            this.#requirements.delete(requirement.id);
            throw error;
        }

        this.emit("requirement:added", {
            id: requirement.id,
            priority: requirement.priority
        });

        return structuredClone(requirement);
    }

    get(id) {
        const requirement = this.#requirements.get(id);

        if (!requirement) {
            throw new RequirementNotFoundError(
                `Requirement ${id} was not found.`
            );
        }

        return structuredClone(requirement);
    }

    updatePriority(id, priority, actor, reason) {
        const requirement = this.#requirements.get(id);

        if (!requirement) {
            throw new RequirementNotFoundError(id);
        }

        if (!VALID_PRIORITIES.has(priority)) {
            throw new TypeError("Invalid priority.");
        }

        if (!actor?.trim() || !reason?.trim()) {
            throw new TypeError(
                "Actor and change reason are required."
            );
        }

        if (requirement.priority === priority) return;

        const event = Object.freeze({
            requirementId: id,
            oldPriority: requirement.priority,
            newPriority: priority,
            actor,
            reason,
            timestamp: new Date().toISOString()
        });

        requirement.priority = priority;
        this.#history.push(event);

        this.emit("priority:changed", event);
    }

    updateStatus(id, status) {
        const requirement = this.#requirements.get(id);

        if (!requirement) {
            throw new RequirementNotFoundError(id);
        }

        if (!VALID_STATUSES.has(status)) {
            throw new TypeError("Invalid status.");
        }

        if (requirement.priority === Priority.WONT &&
            [Status.IN_PROGRESS, Status.COMPLETED].includes(status)) {
            throw new PrioritizationError(
                "Won't-have requirements cannot enter delivery."
            );
        }

        requirement.status = status;

        this.emit("status:changed", {
            requirementId: id,
            status
        });
    }

    #validateGraph() {
        const visited = new Set();
        const active = new Set();

        for (const requirement of this.#requirements.values()) {
            for (const dependency of requirement.dependencies) {
                if (!this.#requirements.has(dependency)) {
                    throw new PrioritizationError(
                        `Unknown dependency: ${dependency}`
                    );
                }
            }
        }

        const visit = id => {
            if (active.has(id)) {
                throw new PrioritizationError(
                    "Circular dependency detected."
                );
            }

            if (visited.has(id)) return;

            active.add(id);

            for (const dependency of
                this.#requirements.get(id).dependencies) {
                visit(dependency);
            }

            active.delete(id);
            visited.add(id);
        };

        for (const id of this.#requirements.keys()) visit(id);
    }

    dependenciesReady(id) {
        const requirement = this.get(id);

        return requirement.dependencies.every(dependency =>
            this.#requirements.get(dependency).status === Status.COMPLETED
        );
    }

    evaluateRelease(capacity) {
        if (!Number.isInteger(capacity) || capacity < 0) {
            throw new RangeError("Capacity must be a nonnegative integer.");
        }

        const mandatory = [];
        const optional = [];

        for (const requirement of this.#requirements.values()) {
            if (requirement.priority === Priority.WONT ||
                requirement.status === Status.COMPLETED) continue;

            if (requirement.priority === Priority.MUST) {
                mandatory.push(requirement);
            } else {
                optional.push(requirement);
            }
        }

        mandatory.sort((a, b) => a.id.localeCompare(b.id));

        optional.sort((a, b) =>
            (b.businessValue / b.effort) -
            (a.businessValue / a.effort)
        );

        let remaining = capacity;
        const selected = [];
        const selectedIds = new Set();

        for (const requirement of [...mandatory, ...optional]) {
            const dependenciesReady = requirement.dependencies.every(
                dependency =>
                    selectedIds.has(dependency) ||
                    this.#requirements.get(dependency).status ===
                        Status.COMPLETED
            );

            if (dependenciesReady && requirement.effort <= remaining) {
                selected.push(structuredClone(requirement));
                selectedIds.add(requirement.id);
                remaining -= requirement.effort;
            }
        }

        return {
            selected,
            remainingCapacity: remaining,
            mandatoryShortfall: mandatory.reduce(
                (sum, item) => sum + item.effort, 0
            ) > capacity
        };
    }

    report() {
        const categories = {};

        for (const priority of VALID_PRIORITIES) {
            const items = [...this.#requirements.values()]
                .filter(r => r.priority === priority);

            categories[priority] = {
                count: items.length,
                effort: items.reduce((s, r) => s + r.effort, 0),
                businessValue: items.reduce(
                    (s, r) => s + r.businessValue, 0
                )
            };
        }

        return {
            total: this.#requirements.size,
            categories,
            completed: [...this.#requirements.values()]
                .filter(r => r.status === Status.COMPLETED).length,
            changes: this.#history.length
        };
    }

    async save(filename) {
        const data = {
            requirements: this.requirements,
            history: this.history
        };

        const destination = path.resolve(filename);
        const temporary = `${destination}.tmp`;

        await fs.mkdir(path.dirname(destination), {
            recursive: true
        });

        await fs.writeFile(
            temporary,
            JSON.stringify(data, null, 2),
            { encoding: "utf8", mode: 0o600 }
        );

        await fs.rename(temporary, destination);
    }

    async load(filename) {
        const data = JSON.parse(
            await fs.readFile(filename, "utf8")
        );

        if (!Array.isArray(data.requirements) ||
            !Array.isArray(data.history)) {
            throw new PrioritizationError("Invalid persistence format.");
        }

        const temporary = new MoSCoWEngine();

        for (const requirement of data.requirements) {
            temporary.add(requirement);
        }

        for (const event of data.history) {
            if (!event.requirementId ||
                !event.actor ||
                !event.reason) {
                throw new PrioritizationError(
                    "Invalid priority history record."
                );
            }
        }

        this.#requirements = temporary.#requirements;
        this.#history = data.history;
    }
}

function createDemo(engine) {
    const examples = [
        {
            id: "R001",
            title: "User Authentication",
            priority: Priority.MUST,
            businessValue: 10,
            effort: 8,
            owner: "Security Team"
        },
        {
            id: "R002",
            title: "Payment Processing",
            priority: Priority.MUST,
            businessValue: 10,
            effort: 13,
            owner: "Payments Team",
            dependencies: ["R001"]
        },
        {
            id: "R003",
            title: "Audit Logging",
            priority: Priority.MUST,
            businessValue: 9,
            effort: 5,
            owner: "Platform Team"
        },
        {
            id: "R004",
            title: "Business Analytics",
            priority: Priority.SHOULD,
            businessValue: 8,
            effort: 8,
            owner: "Analytics Team"
        },
        {
            id: "R005",
            title: "Email Notifications",
            priority: Priority.SHOULD,
            businessValue: 7,
            effort: 5,
            owner: "Communications Team"
        },
        {
            id: "R006",
            title: "Custom Themes",
            priority: Priority.COULD,
            businessValue: 4,
            effort: 3,
            owner: "Frontend Team"
        },
        {
            id: "R007",
            title: "Animated Backgrounds",
            priority: Priority.WONT,
            businessValue: 2,
            effort: 5,
            owner: "Frontend Team"
        }
    ];

    examples.forEach(item => engine.add(item));
}

async function runTests() {
    const engine = new MoSCoWEngine();

    createDemo(engine);

    if (engine.requirements.length !== 7) {
        throw new Error("Requirement registration failed.");
    }

    if (engine.dependenciesReady("R002")) {
        throw new Error("Dependency validation failed.");
    }

    engine.updateStatus("R001", Status.COMPLETED);

    if (!engine.dependenciesReady("R002")) {
        throw new Error("Completed dependency was not recognized.");
    }

    engine.updatePriority(
        "R006",
        Priority.SHOULD,
        "Product Owner",
        "Customer demand increased."
    );

    let rejected = false;

    try {
        engine.updateStatus("R007", Status.IN_PROGRESS);
    } catch (error) {
        rejected = error instanceof PrioritizationError;
    }

    if (!rejected) throw new Error("Won't-have validation failed.");

    console.log("All JavaScript tests passed.");
}

async function main() {
    const engine = new MoSCoWEngine();

    engine.on("requirement:added", event =>
        console.log("Added:", event.id)
    );

    engine.on("priority:changed", event =>
        console.log(
            "Priority changed:",
            event.requirementId,
            event.oldPriority,
            "->",
            event.newPriority
        )
    );

    createDemo(engine);

    console.log("\nMOSCOW REPORT");
    console.log(JSON.stringify(engine.report(), null, 2));

    const release = engine.evaluateRelease(30);

    console.log("\nRELEASE PLAN");

    release.selected.forEach(item =>
        console.log(
            `${item.id} | ${item.title} | ${item.priority} | ${item.effort}`
        )
    );

    console.log("Remaining capacity:", release.remainingCapacity);
    console.log("Mandatory shortfall:", release.mandatoryShortfall);

    await engine.save("moscow_data.json");

    await runTests();
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
