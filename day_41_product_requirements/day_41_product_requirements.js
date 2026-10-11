"use strict";

/*
 * Product requirements lifecycle and event-driven PRD workspace.
 * Run with Node.js 18 or later. No npm packages are required.
 */

const { EventEmitter } = require("node:events");
const { writeFile } = require("node:fs/promises");
const { randomUUID } = require("node:crypto");

const RequirementType = Object.freeze({
  FUNCTIONAL: "functional",
  NON_FUNCTIONAL: "non_functional",
  BUSINESS: "business",
  CONSTRAINT: "constraint",
});

const Priority = Object.freeze({
  MUST: "must",
  SHOULD: "should",
  COULD: "could",
  WONT: "wont",
});

const RequirementStatus = Object.freeze({
  DRAFT: "draft",
  IN_REVIEW: "in_review",
  APPROVED: "approved",
  IMPLEMENTED: "implemented",
  VERIFIED: "verified",
  REJECTED: "rejected",
});

class RequirementError extends Error {
  constructor(message, requirementId = null) {
    super(message);
    this.name = "RequirementError";
    this.requirementId = requirementId;
  }
}

class Requirement {
  constructor({
    id,
    title,
    description,
    type,
    priority,
    owner,
    source,
    criteria = [],
    metric = null,
    dependencies = [],
    storyIds = [],
  }) {
    this.id = id;
    this.title = title;
    this.description = description;
    this.type = type;
    this.priority = priority;
    this.owner = owner;
    this.source = source;
    this.criteria = criteria.map((criterion) => Object.freeze({ ...criterion }));
    this.metric = metric;
    this.dependencies = new Set(dependencies);
    this.storyIds = new Set(storyIds);
    this.status = RequirementStatus.DRAFT;
    this.version = 1;
    this.reviews = [];
    this.changeHistory = [];
    this.validate();
  }

  validate() {
    if (!/^REQ-(FR|NFR|BR|CON)-\d{3}$/.test(this.id)) {
      throw new RequirementError(`Invalid ID: ${this.id}`, this.id);
    }
    if (![...Object.values(RequirementType)].includes(this.type)) {
      throw new RequirementError(`Invalid type: ${this.type}`, this.id);
    }
    if (![...Object.values(Priority)].includes(this.priority)) {
      throw new RequirementError(`Invalid priority: ${this.priority}`, this.id);
    }
    for (const [field, value] of Object.entries({
      title: this.title,
      description: this.description,
      owner: this.owner,
      source: this.source,
    })) {
      if (typeof value !== "string" || !value.trim()) {
        throw new RequirementError(`${field} is required`, this.id);
      }
    }
    if (this.type === RequirementType.FUNCTIONAL && this.criteria.length === 0) {
      throw new RequirementError(
        "Functional requirements need testable acceptance criteria",
        this.id,
      );
    }
    for (const criterion of this.criteria) {
      if (!criterion.given?.trim() || !criterion.when?.trim() || !criterion.then?.trim()) {
        throw new RequirementError("Incomplete acceptance criterion", this.id);
      }
    }
    if (this.type === RequirementType.NON_FUNCTIONAL && !this.metric?.trim()) {
      throw new RequirementError(
        "Non-functional requirements need a measurable target",
        this.id,
      );
    }
  }

  transition(nextStatus, actor) {
    const allowed = {
      [RequirementStatus.DRAFT]: [
        RequirementStatus.IN_REVIEW,
        RequirementStatus.REJECTED,
      ],
      [RequirementStatus.IN_REVIEW]: [
        RequirementStatus.DRAFT,
        RequirementStatus.APPROVED,
        RequirementStatus.REJECTED,
      ],
      [RequirementStatus.APPROVED]: [
        RequirementStatus.IN_REVIEW,
        RequirementStatus.IMPLEMENTED,
      ],
      [RequirementStatus.IMPLEMENTED]: [RequirementStatus.VERIFIED],
      [RequirementStatus.VERIFIED]: [RequirementStatus.IN_REVIEW],
      [RequirementStatus.REJECTED]: [RequirementStatus.DRAFT],
    };

    if (!allowed[this.status]?.includes(nextStatus)) {
      throw new RequirementError(
        `Invalid transition ${this.status} -> ${nextStatus}`,
        this.id,
      );
    }
    if (!actor?.trim()) {
      throw new RequirementError("A named actor is required for state changes", this.id);
    }

    const previousStatus = this.status;
    this.status = nextStatus;
    this.changeHistory.push({
      actor,
      previousStatus,
      nextStatus,
      at: new Date().toISOString(),
      version: this.version,
    });
  }

  revise(actor, changes) {
    if (![RequirementStatus.DRAFT, RequirementStatus.IN_REVIEW].includes(this.status)) {
      throw new RequirementError(
        "Revise an approved requirement through controlled change management",
        this.id,
      );
    }

    const previous = {
      title: this.title,
      description: this.description,
      criteria: this.criteria,
      metric: this.metric,
    };
    Object.assign(this, changes);
    try {
      this.validate();
    } catch (error) {
      Object.assign(this, previous);
      throw error;
    }

    this.version += 1;
    this.changeHistory.push({
      actor,
      event: "requirement_revised",
      version: this.version,
      at: new Date().toISOString(),
    });
  }

  toJSON() {
    return {
      ...this,
      dependencies: [...this.dependencies],
      storyIds: [...this.storyIds],
    };
  }
}

class RequirementsWorkspace extends EventEmitter {
  #requirements = new Map();
  #stakeholders = new Map();
  #changeRequests = new Map();

  constructor(productName) {
    super();
    if (!productName?.trim()) {
      throw new RequirementError("Product name is required");
    }
    this.productName = productName;
  }

  addStakeholder({ id, name, role, influence, interest }) {
    if (!id || !name?.trim() || !role?.trim()) {
      throw new RequirementError("Stakeholder identity and role are required");
    }
    if (!Number.isInteger(influence) || influence < 1 || influence > 5) {
      throw new RequirementError("Influence must be an integer from 1 to 5");
    }
    if (!Number.isInteger(interest) || interest < 1 || interest > 5) {
      throw new RequirementError("Interest must be an integer from 1 to 5");
    }
    if (this.#stakeholders.has(id)) {
      throw new RequirementError(`Duplicate stakeholder: ${id}`);
    }
    const stakeholder = Object.freeze({
      id,
      name,
      role,
      influence,
      interest,
    });
    this.#stakeholders.set(id, stakeholder);
    this.emit("stakeholder:added", stakeholder);
    return stakeholder;
  }

  addRequirement(requirement) {
    if (!(requirement instanceof Requirement)) {
      throw new RequirementError("Expected a validated Requirement instance");
    }
    if (this.#requirements.has(requirement.id)) {
      throw new RequirementError(`Duplicate requirement: ${requirement.id}`);
    }
    this.#requirements.set(requirement.id, requirement);
    this.emit("requirement:created", {
      requirementId: requirement.id,
      version: requirement.version,
    });
    return requirement;
  }

  getRequirement(id) {
    const requirement = this.#requirements.get(id);
    if (!requirement) {
      throw new RequirementError(`Unknown requirement: ${id}`, id);
    }
    return requirement;
  }

  traceabilityReport() {
    return [...this.#requirements.values()].map((requirement) => ({
      requirementId: requirement.id,
      status: requirement.status,
      sourcesPresent: Boolean(requirement.source),
      ownerPresent: Boolean(requirement.owner),
      acceptanceCriteriaCount: requirement.criteria.length,
      implementationLinks: requirement.storyIds.size,
      gaps: [
        ...(!requirement.source ? ["source"] : []),
        ...(!requirement.owner ? ["owner"] : []),
        ...(requirement.type === RequirementType.FUNCTIONAL &&
        requirement.criteria.length === 0
          ? ["acceptance criteria"]
          : []),
        ...(requirement.type === RequirementType.NON_FUNCTIONAL && !requirement.metric
          ? ["measurable target"]
          : []),
        ...(requirement.storyIds.size === 0 ? ["implementation trace"] : []),
      ],
    }));
  }

  dependencyOrder() {
    // Kahn's algorithm returns a valid implementation order or reports a cycle.
    const requirements = this.#requirements;
    const indegree = new Map([...requirements.keys()].map((id) => [id, 0]));
    const dependents = new Map([...requirements.keys()].map((id) => [id, []]));

    for (const requirement of requirements.values()) {
      for (const dependency of requirement.dependencies) {
        if (!requirements.has(dependency)) {
          throw new RequirementError(
            `${requirement.id} depends on missing ${dependency}`,
            requirement.id,
          );
        }
        indegree.set(requirement.id, indegree.get(requirement.id) + 1);
        dependents.get(dependency).push(requirement.id);
      }
    }

    const queue = [...indegree]
      .filter(([, degree]) => degree === 0)
      .map(([id]) => id)
      .sort();
    const order = [];

    while (queue.length) {
      const id = queue.shift();
      order.push(id);
      for (const dependent of dependents.get(id)) {
        indegree.set(dependent, indegree.get(dependent) - 1);
        if (indegree.get(dependent) === 0) {
          queue.push(dependent);
          queue.sort();
        }
      }
    }

    if (order.length !== requirements.size) {
      throw new RequirementError("Circular requirement dependencies detected");
    }
    return order;
  }

  evaluateRelease() {
    const mandatory = [...this.#requirements.values()].filter(
      (requirement) =>
        requirement.priority === Priority.MUST &&
        requirement.status !== RequirementStatus.REJECTED,
    );
    const unverified = mandatory
      .filter((requirement) => requirement.status !== RequirementStatus.VERIFIED)
      .map((requirement) => requirement.id);
    const gaps = this.traceabilityReport().filter((item) => item.gaps.length > 0);

    let dependencyOrder = [];
    let dependencyError = null;
    try {
      dependencyOrder = this.dependencyOrder();
    } catch (error) {
      dependencyError = error.message;
    }

    return {
      ready:
        unverified.length === 0 &&
        gaps.length === 0 &&
        dependencyError === null,
      mandatoryCount: mandatory.length,
      unverified,
      traceabilityGapIds: gaps.map((item) => item.requirementId),
      dependencyOrder,
      dependencyError,
    };
  }

  requestChange({
    requirementId,
    requester,
    description,
    effortDays,
    impact,
  }) {
    this.getRequirement(requirementId);
    if (!requester?.trim() || !description?.trim() || !impact?.trim()) {
      throw new RequirementError("Change request details cannot be empty");
    }
    if (!Number.isFinite(effortDays) || effortDays <= 0) {
      throw new RequirementError("Effort must be a positive finite number");
    }

    const request = {
      id: `CR-${randomUUID()}`,
      requirementId,
      requester,
      description,
      effortDays,
      impact,
      state: "pending",
      decision: null,
      createdAt: new Date().toISOString(),
    };
    this.#changeRequests.set(request.id, request);
    this.emit("change:requested", { ...request });
    return { ...request };
  }

  decideChange(changeId, { approved, decisionMaker, reason }) {
    const request = this.#changeRequests.get(changeId);
    if (!request) throw new RequirementError(`Unknown change: ${changeId}`);
    if (request.state !== "pending") {
      throw new RequirementError("A decided change cannot be decided again");
    }
    if (typeof approved !== "boolean" || !decisionMaker?.trim() || !reason?.trim()) {
      throw new RequirementError("Decision, decision maker, and reason are required");
    }

    request.state = approved ? "approved" : "deferred";
    request.decision = { approved, decisionMaker, reason };
    this.emit("change:decided", { ...request });
    return { ...request };
  }

  toJSON() {
    return {
      productName: this.productName,
      stakeholders: [...this.#stakeholders.values()],
      requirements: [...this.#requirements.values()].map((item) => item.toJSON()),
      traceability: this.traceabilityReport(),
      releaseAssessment: this.evaluateRelease(),
    };
  }
}

async function run() {
  const workspace = new RequirementsWorkspace("ProcureFlow Supplier Portal");

  workspace.on("requirement:created", (event) => {
    console.log(`Event: ${event.requirementId} created at version ${event.version}`);
  });
  workspace.on("change:requested", (event) => {
    console.log(`Event: change requested for ${event.requirementId}`);
  });

  workspace.addStakeholder({
    id: "ST-001",
    name: "Maya Rao",
    role: "Procurement analyst",
    influence: 4,
    interest: 5,
  });

  workspace.addStakeholder({
    id: "ST-002",
    name: "Arjun Sen",
    role: "Compliance officer",
    influence: 5,
    interest: 4,
  });

  const intake = workspace.addRequirement(
    new Requirement({
      id: "REQ-FR-001",
      title: "Create supplier application",
      description:
        "Authenticated supplier representatives can create a draft application with legal identity and contact details.",
      type: RequirementType.FUNCTIONAL,
      priority: Priority.MUST,
      owner: "Product manager",
      source: "Supplier interviews",
      criteria: [
        {
          given: "The supplier is authenticated",
          when: "Valid required fields are submitted",
          then: "The system creates a draft and returns a reference",
        },
        {
          given: "The tax identifier is already registered",
          when: "A duplicate application is submitted",
          then: "The system rejects the duplicate without disclosing another supplier's data",
        },
      ],
      storyIds: ["SUP-101"],
    }),
  );

  const completeness = workspace.addRequirement(
    new Requirement({
      id: "REQ-FR-002",
      title: "Validate document completeness",
      description:
        "The portal checks submitted documents against the published checklist for the supplier category.",
      type: RequirementType.FUNCTIONAL,
      priority: Priority.MUST,
      owner: "Product manager",
      source: "Compliance workshop",
      criteria: [
        {
          given: "A published checklist exists",
          when: "The supplier attempts final submission",
          then: "Missing mandatory documents are reported and submission is blocked",
        },
      ],
      dependencies: ["REQ-FR-001"],
      storyIds: ["SUP-110"],
    }),
  );

  workspace.addRequirement(
    new Requirement({
      id: "REQ-NFR-001",
      title: "Application read latency",
      description:
        "Supplier application reads meet the response-time target under the agreed concurrent-user workload.",
      type: RequirementType.NON_FUNCTIONAL,
      priority: Priority.MUST,
      owner: "Engineering lead",
      source: "Performance review",
      metric: "p95 below 300 ms at 500 concurrent users",
      storyIds: ["OPS-40"],
    }),
  );

  // State transitions are explicit, and invalid transitions fail rather than
  // silently changing the requirements baseline.
  intake.transition(RequirementStatus.IN_REVIEW, "Maya Rao");
  intake.transition(RequirementStatus.APPROVED, "Product review board");
  intake.transition(RequirementStatus.IMPLEMENTED, "Engineering lead");
  intake.transition(RequirementStatus.VERIFIED, "QA lead");

  completeness.transition(RequirementStatus.IN_REVIEW, "Arjun Sen");
  completeness.transition(RequirementStatus.APPROVED, "Compliance review board");

  const change = workspace.requestChange({
    requirementId: "REQ-FR-002",
    requester: "Arjun Sen",
    description: "Notify suppliers before compliance documents expire",
    effortDays: 4,
    impact: "Requires notification scheduling and preference handling",
  });

  workspace.decideChange(change.id, {
    approved: false,
    decisionMaker: "Product review board",
    reason: "Defer until notification capacity and policy are approved",
  });

  console.log("\nImplementation order:", workspace.dependencyOrder());
  console.log("\nTraceability:", JSON.stringify(workspace.traceabilityReport(), null, 2));
  console.log("\nRelease assessment:", workspace.evaluateRelease());

  try {
    completeness.transition(RequirementStatus.VERIFIED, "QA lead");
  } catch (error) {
    console.log("Expected workflow rejection:", error.message);
  }

  try {
    riceScore(100, 2, 0.8, 0);
  } catch (error) {
    console.log("Expected prioritization rejection:", error.message);
  }

  const output = workspace.toJSON();
  await writeFile("procureflow_requirements.json", JSON.stringify(output, null, 2), {
    encoding: "utf8",
    mode: 0o600,
  });
  console.log("\nRequirements workspace exported.");
}

function riceScore(reach, impact, confidence, effort) {
  if (![reach, impact, confidence, effort].every(Number.isFinite)) {
    throw new RequirementError("RICE inputs must be finite numbers");
  }
  if (reach < 0 || impact < 0 || confidence < 0 || confidence > 1 || effort <= 0) {
    throw new RequirementError("Invalid RICE input range");
  }
  return (reach * impact * confidence) / effort;
}

run().catch((error) => {
  console.error("Requirements workflow failed:", error.message);
  process.exitCode = 1;
});
