"use strict";

/*
 * Event-driven PRD workflow for a product team.
 *
 * Run with Node.js:
 *   node prd_workflow.js
 *
 * This implementation emphasizes immutable workflow events, requirement
 * traceability, review gates, and acceptance-criterion verification.
 */

const { randomUUID } = require("node:crypto");
const { writeFile } = require("node:fs/promises");

const Priority = Object.freeze({
  MUST: "Must",
  SHOULD: "Should",
  COULD: "Could",
  WONT: "Won't",
});

const RequirementState = Object.freeze({
  DRAFT: "Draft",
  REVIEW: "In Review",
  APPROVED: "Approved",
  IMPLEMENTED: "Implemented",
  VERIFIED: "Verified",
  REJECTED: "Rejected",
});

const ALLOWED_TRANSITIONS = Object.freeze({
  [RequirementState.DRAFT]: [RequirementState.REVIEW],
  [RequirementState.REVIEW]: [
    RequirementState.DRAFT,
    RequirementState.APPROVED,
    RequirementState.REJECTED,
  ],
  [RequirementState.APPROVED]: [
    RequirementState.REVIEW,
    RequirementState.IMPLEMENTED,
  ],
  [RequirementState.IMPLEMENTED]: [
    RequirementState.REVIEW,
    RequirementState.VERIFIED,
  ],
  [RequirementState.VERIFIED]: [RequirementState.REVIEW],
  [RequirementState.REJECTED]: [RequirementState.DRAFT],
});

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
  }
}

class PolicyError extends Error {
  constructor(message) {
    super(message);
    this.name = "PolicyError";
  }
}

function requireText(value, fieldName) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new ValidationError(`${fieldName} must be a non-empty string.`);
  }
}

function validateCriterion(criterion) {
  for (const field of ["id", "given", "when", "then"]) {
    requireText(criterion[field], `criterion.${field}`);
  }
  return Object.freeze({ ...criterion });
}

function createRequirement(input) {
  requireText(input.id, "requirement.id");
  requireText(input.title, "requirement.title");
  requireText(input.description, "requirement.description");
  requireText(input.rationale, "requirement.rationale");
  requireText(input.owner, "requirement.owner");

  if (!Object.values(Priority).includes(input.priority)) {
    throw new ValidationError(`Unknown priority: ${input.priority}`);
  }

  if (!Array.isArray(input.acceptanceCriteria) ||
      input.acceptanceCriteria.length === 0) {
    throw new ValidationError(
      `${input.id} requires at least one acceptance criterion.`,
    );
  }

  const estimate = input.estimatePoints ?? 3;
  if (!Number.isInteger(estimate) || estimate < 0) {
    throw new ValidationError("Estimate must be a non-negative integer.");
  }

  return Object.freeze({
    id: input.id,
    title: input.title,
    description: input.description,
    rationale: input.rationale,
    owner: input.owner,
    priority: input.priority,
    estimatePoints: estimate,
    dependencies: Object.freeze([...(input.dependencies ?? [])]),
    acceptanceCriteria: Object.freeze(
      input.acceptanceCriteria.map(validateCriterion),
    ),
  });
}

class EventJournal {
  #events = [];

  append(event) {
    // Timestamps and generated identifiers are assigned by the journal,
    // not by callers, so workflow events have a consistent audit format.
    const recorded = Object.freeze({
      eventId: randomUUID(),
      occurredAt: new Date().toISOString(),
      ...event,
    });
    this.#events.push(recorded);
    return recorded;
  }

  get events() {
    return this.#events.map((event) => ({ ...event }));
  }
}

class RequirementWorkflow {
  #requirements = new Map();
  #states = new Map();
  #journal = new EventJournal();
  #reviewers = new Map();

  constructor({ productName, owner }) {
    requireText(productName, "productName");
    requireText(owner, "owner");
    this.productName = productName;
    this.owner = owner;
  }

  addRequirement(input) {
    const requirement = createRequirement(input);
    if (this.#requirements.has(requirement.id)) {
      throw new ValidationError(`Duplicate requirement ID: ${requirement.id}`);
    }

    this.#requirements.set(requirement.id, requirement);
    this.#states.set(requirement.id, RequirementState.DRAFT);
    this.#journal.append({
      type: "REQUIREMENT_CREATED",
      requirementId: requirement.id,
      actor: this.owner,
      state: RequirementState.DRAFT,
    });
  }

  requestReview(requirementId, actor) {
    requireText(actor, "actor");
    const requirement = this.#getRequirement(requirementId);
    this.#assertDependenciesApproved(requirement);

    this.#transition(
      requirementId,
      RequirementState.REVIEW,
      actor,
      "Review requested",
    );
  }

  recordReview(requirementId, reviewer, decision, comment) {
    requireText(reviewer, "reviewer");
    requireText(comment, "comment");

    if (!["approve", "request_changes", "reject"].includes(decision)) {
      throw new ValidationError(`Unsupported review decision: ${decision}`);
    }

    if (reviewer === this.#requirements.get(requirementId)?.owner) {
      throw new PolicyError("A requirement owner cannot approve their own requirement.");
    }

    const requirement = this.#getRequirement(requirementId);
    const state = this.#states.get(requirementId);

    if (state !== RequirementState.REVIEW) {
      throw new PolicyError("Reviews can only be recorded while in review.");
    }

    const previous = this.#reviewers.get(requirementId) ?? new Map();
    const updated = new Map(previous);
    updated.set(reviewer, decision);
    this.#reviewers.set(requirementId, updated);

    this.#journal.append({
      type: "REVIEW_RECORDED",
      requirementId,
      reviewer,
      decision,
      comment,
    });

    if (decision === "reject") {
      this.#transition(
        requirementId,
        RequirementState.REJECTED,
        reviewer,
        "Reviewer rejected the requirement",
      );
    } else if (decision === "request_changes") {
      this.#transition(
        requirementId,
        RequirementState.DRAFT,
        reviewer,
        "Reviewer requested changes",
      );
    } else {
      // The configured policy requires two distinct approvers. One approval
      // is not enough to approve a high-impact product requirement.
      const approvals = [...updated.entries()]
        .filter(([, value]) => value === "approve")
        .map(([name]) => name);

      if (approvals.length >= 2) {
        this.#transition(
          requirementId,
          RequirementState.APPROVED,
          reviewer,
          `Approved by ${approvals.length} distinct reviewers`,
        );
      }
    }
  }

  markImplemented(requirementId, actor) {
    this.#transition(
      requirementId,
      RequirementState.IMPLEMENTED,
      actor,
      "Implementation reported complete",
    );
  }

  verifyAcceptanceCriteria(requirementId, results, actor) {
    const requirement = this.#getRequirement(requirementId);
    const state = this.#states.get(requirementId);

    if (state !== RequirementState.IMPLEMENTED) {
      throw new PolicyError(
        "Acceptance criteria can only be verified after implementation.",
      );
    }

    const expectedIds = requirement.acceptanceCriteria.map((criterion) => criterion.id);
    const resultIds = Object.keys(results);

    if (expectedIds.some((id) => !Object.hasOwn(results, id))) {
      throw new ValidationError("Every acceptance criterion needs a test result.");
    }

    if (resultIds.some((id) => !expectedIds.includes(id))) {
      throw new ValidationError("Test results contain an unknown criterion ID.");
    }

    const failures = expectedIds.filter((id) => results[id] !== true);

    this.#journal.append({
      type: "ACCEPTANCE_TESTS_EXECUTED",
      requirementId,
      actor,
      results: { ...results },
      failures,
    });

    if (failures.length > 0) {
      throw new PolicyError(
        `Acceptance verification failed: ${failures.join(", ")}`,
      );
    }

    this.#transition(
      requirementId,
      RequirementState.VERIFIED,
      actor,
      "All acceptance criteria passed",
    );
  }

  #assertDependenciesApproved(requirement) {
    for (const dependencyId of requirement.dependencies) {
      if (!this.#requirements.has(dependencyId)) {
        throw new ValidationError(
          `${requirement.id} depends on unknown requirement ${dependencyId}.`,
        );
      }
      if (this.#states.get(dependencyId) !== RequirementState.APPROVED &&
          this.#states.get(dependencyId) !== RequirementState.IMPLEMENTED &&
          this.#states.get(dependencyId) !== RequirementState.VERIFIED) {
        throw new PolicyError(
          `Dependency ${dependencyId} must be approved before ${requirement.id} enters review.`,
        );
      }
    }
  }

  #getRequirement(requirementId) {
    const requirement = this.#requirements.get(requirementId);
    if (!requirement) {
      throw new ValidationError(`Unknown requirement: ${requirementId}`);
    }
    return requirement;
  }

  #transition(requirementId, nextState, actor, reason) {
    requireText(actor, "actor");
    const currentState = this.#states.get(requirementId);

    if (!currentState) {
      throw new ValidationError(`Unknown requirement: ${requirementId}`);
    }

    if (!ALLOWED_TRANSITIONS[currentState].includes(nextState)) {
      throw new PolicyError(
        `Invalid transition for ${requirementId}: ${currentState} -> ${nextState}`,
      );
    }

    this.#states.set(requirementId, nextState);
    this.#journal.append({
      type: "STATE_CHANGED",
      requirementId,
      actor,
      from: currentState,
      to: nextState,
      reason,
    });
  }

  snapshot() {
    return {
      productName: this.productName,
      owner: this.owner,
      requirements: [...this.#requirements.values()].map((requirement) => ({
        ...requirement,
        dependencies: [...requirement.dependencies],
        acceptanceCriteria: requirement.acceptanceCriteria.map((item) => ({ ...item })),
        state: this.#states.get(requirement.id),
        reviews: Object.fromEntries(this.#reviewers.get(requirement.id) ?? []),
      })),
      events: this.#journal.events,
    };
  }
}

async function main() {
  const workflow = new RequirementWorkflow({
    productName: "Procurement Request Portal",
    owner: "Product Manager",
  });

  workflow.addRequirement({
    id: "REQ-101",
    title: "Validate purchase requests",
    description: "Reject requests missing a cost center or business justification.",
    rationale: "Incomplete requests delay approval.",
    owner: "Product Manager",
    priority: Priority.MUST,
    acceptanceCriteria: [
      {
        id: "AC-101-A",
        given: "A request has all mandatory fields",
        when: "The requester submits it",
        then: "The service accepts the request and creates an identifier",
      },
      {
        id: "AC-101-B",
        given: "A request has no cost center",
        when: "The requester submits it",
        then: "The service rejects it with a field-specific validation error",
      },
    ],
  });

  workflow.addRequirement({
    id: "REQ-102",
    title: "Route requests for approval",
    description: "Route a valid request using its amount and cost center.",
    rationale: "Approval routing must follow delegated financial authority.",
    owner: "Procurement Lead",
    priority: Priority.MUST,
    dependencies: ["REQ-101"],
    acceptanceCriteria: [
      {
        id: "AC-102-A",
        given: "A valid request matches an active approval policy",
        when: "The routing engine evaluates it",
        then: "The request is assigned to the configured approver group",
      },
    ],
  });

  workflow.requestReview("REQ-101", "Product Manager");
  workflow.recordReview(
    "REQ-101",
    "Procurement Lead",
    "approve",
    "Mandatory fields and validation behavior are clear.",
  );
  workflow.recordReview(
    "REQ-101",
    "Security Lead",
    "approve",
    "The request validation does not replace server-side authorization.",
  );

  workflow.markImplemented("REQ-101", "Engineering Lead");
  workflow.verifyAcceptanceCriteria(
    "REQ-101",
    { "AC-101-A": true, "AC-101-B": true },
    "QA Lead",
  );

  workflow.requestReview("REQ-102", "Procurement Lead");
  workflow.recordReview(
    "REQ-102",
    "Finance Lead",
    "approve",
    "The financial approval dependency is explicitly represented.",
  );
  workflow.recordReview(
    "REQ-102",
    "Security Lead",
    "approve",
    "Unmatched policies must fail closed.",
  );

  const snapshot = workflow.snapshot();

  console.log("PRD requirement workflow");
  for (const requirement of snapshot.requirements) {
    console.log(
      `${requirement.id}: ${requirement.state} | ${requirement.title}`,
    );
  }
  console.log(`Recorded audit events: ${snapshot.events.length}`);

  const outputPath = process.argv[2];
  if (outputPath) {
    await writeFile(outputPath, JSON.stringify(snapshot, null, 2), "utf8");
    console.log(`Workflow exported to ${outputPath}`);
  }
}

main().catch((error) => {
  console.error(`${error.name}: ${error.message}`);
  process.exitCode = 1;
});
