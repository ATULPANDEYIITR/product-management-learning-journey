"use strict";

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const crypto = require("node:crypto");

const IndicatorType = Object.freeze({
    LEADING: "leading",
    LAGGING: "lagging"
});

const Status = Object.freeze({
    DRAFT: "draft",
    ACTIVE: "active",
    AT_RISK: "at_risk",
    COMPLETED: "completed",
    CANCELLED: "cancelled"
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

function validateText(value, field) {
    if (typeof value !== "string" || !value.trim()) {
        throw new ValidationError(`${field} must be a non-empty string.`);
    }
}

function validateNumber(value, field) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        Math.abs(value) > 1e12
    ) {
        throw new ValidationError(`${field} must be a finite number.`);
    }
}

class KeyResult {
    constructor({
        title,
        baseline,
        current,
        target,
        unit,
        indicatorType,
        weight = 1,
        higherIsBetter = true
    }) {
        validateText(title, "Key result title");
        validateText(unit, "Unit");

        validateNumber(baseline, "Baseline");
        validateNumber(current, "Current value");
        validateNumber(target, "Target");
        validateNumber(weight, "Weight");

        if (baseline === target) {
            throw new ValidationError("Baseline and target cannot match.");
        }

        if (weight <= 0) {
            throw new ValidationError("Weight must be positive.");
        }

        if (!Object.values(IndicatorType).includes(indicatorType)) {
            throw new ValidationError("Invalid indicator type.");
        }

        if (higherIsBetter ? target <= baseline : target >= baseline) {
            throw new ValidationError("Target direction is inconsistent.");
        }

        this.id = crypto.randomUUID();
        this.title = title.trim();
        this.baseline = baseline;
        this.current = current;
        this.target = target;
        this.unit = unit;
        this.indicatorType = indicatorType;
        this.weight = weight;
        this.higherIsBetter = higherIsBetter;
        this.history = [];
    }

    get progress() {
        return Math.max(
            0,
            Math.min(
                1,
                (this.current - this.baseline) /
                (this.target - this.baseline)
            )
        );
    }

    update(value, note = "") {
        validateNumber(value, "Updated value");

        if (typeof note !== "string") {
            throw new ValidationError("Update note must be text.");
        }

        const previous = this.current;
        this.current = value;

        this.history.push(Object.freeze({
            timestamp: new Date().toISOString(),
            previous,
            current: value,
            note: note.slice(0, 500)
        }));

        return previous;
    }
}

class Objective {
    constructor({
        title,
        owner,
        department,
        period,
        parentId = null,
        description = ""
    }) {
        validateText(title, "Objective title");
        validateText(owner, "Owner");
        validateText(department, "Department");
        validateText(period, "Period");

        this.id = crypto.randomUUID();
        this.title = title.trim();
        this.owner = owner.trim();
        this.department = department.trim();
        this.period = period;
        this.parentId = parentId;
        this.description = description;
        this.status = Status.DRAFT;
        this.keyResults = [];
    }

    addKeyResult(keyResult) {
        if (!(keyResult instanceof KeyResult)) {
            throw new ValidationError("Expected a KeyResult instance.");
        }

        if (this.keyResults.some(kr => kr.title === keyResult.title)) {
            throw new ValidationError("Duplicate key result.");
        }

        this.keyResults.push(keyResult);
    }

    get progress() {
        if (this.keyResults.length === 0) return 0;

        const weight = this.keyResults.reduce(
            (sum, kr) => sum + kr.weight, 0
        );

        return this.keyResults.reduce(
            (sum, kr) => sum + kr.progress * kr.weight, 0
        ) / weight;
    }

    getIndicatorProgress(type) {
        const results = this.keyResults.filter(
            kr => kr.indicatorType === type
        );

        if (!results.length) return null;

        return results.reduce(
            (sum, kr) => sum + kr.progress, 0
        ) / results.length;
    }

    activate() {
        if (this.status !== Status.DRAFT && this.status !== Status.ACTIVE) {
            throw new ValidationError("Invalid activation transition.");
        }

        if (!this.keyResults.length) {
            throw new ValidationError(
                "An objective requires at least one key result."
            );
        }

        this.status = Status.ACTIVE;
    }

    evaluate() {
        if (
            this.status === Status.CANCELLED ||
            this.status === Status.COMPLETED
        ) {
            return this.status;
        }

        if (this.progress >= 1) {
            this.status = Status.COMPLETED;
        } else if (this.progress < 0.4) {
            this.status = Status.AT_RISK;
        } else {
            this.status = Status.ACTIVE;
        }

        return this.status;
    }
}

class OKREngine extends EventEmitter {
    constructor() {
        super();
        this.objectives = new Map();
        this.eventLog = [];
        this.revision = 0;
    }

    record(type, details) {
        const event = Object.freeze({
            type,
            revision: ++this.revision,
            timestamp: new Date().toISOString(),
            details
        });

        this.eventLog.push(event);
        this.emit(type, event);
        this.emit("change", event);
    }

    addObjective(objective) {
        if (!(objective instanceof Objective)) {
            throw new ValidationError("Invalid objective.");
        }

        if (this.objectives.has(objective.id)) {
            throw new ValidationError("Duplicate objective ID.");
        }

        if (objective.parentId) {
            const parent = this.objectives.get(objective.parentId);

            if (!parent) {
                throw new ValidationError("Parent objective not found.");
            }

            if (parent.period !== objective.period) {
                throw new ValidationError(
                    "Parent and child periods must match."
                );
            }
        }

        this.objectives.set(objective.id, objective);

        this.record("objective.created", {
            objectiveId: objective.id
        });

        return objective.id;
    }

    activate(objectiveId) {
        const objective = this.getObjective(objectiveId);
        objective.activate();

        this.record("objective.activated", {
            objectiveId
        });
    }

    getObjective(id) {
        const objective = this.objectives.get(id);

        if (!objective) {
            throw new ValidationError("Objective not found.");
        }

        return objective;
    }

    updateKeyResult(objectiveId, keyResultId, value, note = "") {
        const objective = this.getObjective(objectiveId);

        if (![Status.ACTIVE, Status.AT_RISK].includes(objective.status)) {
            throw new ValidationError(
                "Updates require an active objective."
            );
        }

        const keyResult = objective.keyResults.find(
            kr => kr.id === keyResultId
        );

        if (!keyResult) {
            throw new ValidationError("Key result not found.");
        }

        const previous = keyResult.update(value, note);
        const status = objective.evaluate();

        this.record("key-result.updated", {
            objectiveId,
            keyResultId,
            previous,
            current: value,
            status
        });
    }

    async updateWithAuthorization(
        objectiveId,
        keyResultId,
        value,
        actor,
        note = ""
    ) {
        validateText(actor, "Actor");

        // Simulates an asynchronous authorization boundary.
        const authorized = await Promise.resolve(
            actor === this.getObjective(objectiveId).owner
        );

        if (!authorized) {
            throw new ValidationError(
                "Only the objective owner may update this result."
            );
        }

        this.updateKeyResult(objectiveId, keyResultId, value, note);
    }

    alignmentTree(objectiveId) {
        const objective = this.getObjective(objectiveId);

        return {
            id: objective.id,
            title: objective.title,
            progress: objective.progress,
            children: [...this.objectives.values()]
                .filter(item => item.parentId === objectiveId)
                .map(item => this.alignmentTree(item.id))
        };
    }

    report() {
        return [...this.objectives.values()].map(objective => {
            objective.evaluate();

            return {
                objective: objective.title,
                owner: objective.owner,
                department: objective.department,
                status: objective.status,
                progress: Number(
                    (objective.progress * 100).toFixed(2)
                ),
                leadingProgress: objective.getIndicatorProgress(
                    IndicatorType.LEADING
                ),
                laggingProgress: objective.getIndicatorProgress(
                    IndicatorType.LAGGING
                )
            };
        });
    }

    async save(filename) {
        const data = {
            revision: this.revision,
            objectives: [...this.objectives.values()].map(objective => ({
                id: objective.id,
                title: objective.title,
                owner: objective.owner,
                department: objective.department,
                period: objective.period,
                parentId: objective.parentId,
                status: objective.status,
                progress: objective.progress,
                keyResults: objective.keyResults.map(kr => ({
                    id: kr.id,
                    title: kr.title,
                    baseline: kr.baseline,
                    current: kr.current,
                    target: kr.target,
                    indicatorType: kr.indicatorType,
                    progress: kr.progress,
                    history: kr.history
                }))
            })),
            events: this.eventLog
        };

        await fs.writeFile(
            filename,
            JSON.stringify(data, null, 2),
            { encoding: "utf8", flag: "w", mode: 0o600 }
        );
    }
}

async function main() {
    const engine = new OKREngine();

    engine.on("key-result.updated", event => {
        console.log("Update event:", event.details);
    });

    const company = new Objective({
        title: "Improve digital banking performance",
        owner: "CEO",
        department: "Executive",
        period: "2026-Q4"
    });

    company.addKeyResult(new KeyResult({
        title: "Customer retention rate",
        baseline: 70,
        current: 76,
        target: 90,
        unit: "%",
        indicatorType: IndicatorType.LAGGING,
        weight: 2
    }));

    company.addKeyResult(new KeyResult({
        title: "Monthly active customers",
        baseline: 100000,
        current: 125000,
        target: 200000,
        unit: "customers",
        indicatorType: IndicatorType.LAGGING
    }));

    engine.addObjective(company);

    const product = new Objective({
        title: "Improve mobile onboarding",
        owner: "Product Director",
        department: "Product",
        period: "2026-Q4",
        parentId: company.id
    });

    product.addKeyResult(new KeyResult({
        title: "Usability tests completed",
        baseline: 0,
        current: 10,
        target: 20,
        unit: "tests",
        indicatorType: IndicatorType.LEADING
    }));

    product.addKeyResult(new KeyResult({
        title: "Successful onboarding rate",
        baseline: 40,
        current: 55,
        target: 80,
        unit: "%",
        indicatorType: IndicatorType.LAGGING
    }));

    engine.addObjective(product);

    engine.activate(company.id);
    engine.activate(product.id);

    await engine.updateWithAuthorization(
        product.id,
        product.keyResults[0].id,
        16,
        "Product Director",
        "Additional usability sessions completed."
    );

    console.log("\nPERFORMANCE REPORT");
    console.table(engine.report());

    console.log("\nALIGNMENT TREE");
    console.log(JSON.stringify(
        engine.alignmentTree(company.id), null, 2
    ));

    await engine.save("okr-report.json");
    console.log("\nSaved okr-report.json");

    try {
        await engine.updateWithAuthorization(
            product.id,
            product.keyResults[0].id,
            18,
            "Unauthorized User"
        );
    } catch (error) {
        console.error("Expected authorization failure:", error.message);
    }
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
