"use strict";

/**
 * Acceptance criteria workflow engine.
 *
 * Models requirement validation, Given-When-Then scenarios, execution
 * evidence, and event-driven status transitions.
 *
 * Run with: node acceptance-criteria.js
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

const PRIORITIES = Object.freeze(["must", "should", "could"]);
const STATUSES = Object.freeze([
  "draft",
  "ready",
  "verified",
  "failed",
]);

class ValidationError extends Error {
  constructor(message, details = []) {
    super(message);
    this.name = "ValidationError";
    this.details = details;
  }
}

class InvalidTransitionError extends Error {
  constructor(from, to) {
    super(`Transition from ${from} to ${to} is not permitted.`);
    this.name = "InvalidTransitionError";
  }
}

function validateScenario(scenario) {
  const errors = [];

  for (const field of ["given", "when", "then", "expected"]) {
    if (typeof scenario[field] !== "string" ||
        scenario[field].trim().length < 8) {
      errors.push(`${field} must contain meaningful text.`);
    }
  }

  if (!Array.isArray(scenario.tags) ||
      scenario.tags.length === 0 ||
      !scenario.tags.every(
        tag => typeof tag === "string" && tag.trim().length > 0
      )) {
    errors.push("At least one non-empty scenario tag is required.");
  }

  return errors;
}

class AcceptanceCriterion {
  constructor({
    id,
    title,
    description,
    priority,
    owner,
    scenarios,
  }) {
    this.id = id;
    this.title = title;
    this.description = description;
    this.priority = priority;
    this.owner = owner;
    this.scenarios = scenarios;
    this.status = "draft";
    this.evidence = [];
    this.revision = 0;
  }

  validate() {
    const errors = [];

    if (!/^AC-[A-Z]{2,8}-\d{3}$/.test(this.id)) {
      errors.push("Identifier must match AC-AREA-001.");
    }
    if (typeof this.title !== "string" ||
        this.title.trim().length < 5 ||
        this.title.trim().length > 120) {
      errors.push("Title must contain 5 to 120 characters.");
    }
    if (typeof this.description !== "string" ||
        this.description.trim().length < 15) {
      errors.push("Description must explain the behavior.");
    }
    if (!PRIORITIES.includes(this.priority)) {
      errors.push("Unknown priority.");
    }
    if (typeof this.owner !== "string" || !this.owner.trim()) {
      errors.push("An owner is required.");
    }
    if (!Array.isArray(this.scenarios) || this.scenarios.length === 0) {
      errors.push("At least one scenario is required.");
    } else {
      this.scenarios.forEach((scenario, index) => {
        errors.push(
          ...validateScenario(scenario).map(
            error => `Scenario ${index + 1}: ${error}`
          )
        );
      });
    }

    return errors;
  }

  transition(nextStatus) {
    if (!STATUSES.includes(nextStatus)) {
      throw new ValidationError(`Unknown status: ${nextStatus}`);
    }

    const permitted = {
      draft: ["ready"],
      ready: ["verified", "failed"],
      verified: ["ready", "failed"],
      failed: ["ready", "verified"],
    };

    if (!permitted[this.status].includes(nextStatus)) {
      throw new InvalidTransitionError(this.status, nextStatus);
    }

    if (nextStatus === "ready") {
      const errors = this.validate();
      if (errors.length) {
        throw new ValidationError("Criterion is not ready.", errors);
      }
    }

    this.status = nextStatus;
    this.revision += 1;
  }

  recordExecution({ passed, evidence, commitSha }) {
    if (this.status !== "ready") {
      throw new InvalidTransitionError(this.status, "execution");
    }
    if (typeof passed !== "boolean") {
      throw new ValidationError("Execution result must be boolean.");
    }
    if (typeof evidence !== "string" || !evidence.trim()) {
      throw new ValidationError("Execution evidence is required.");
    }
    if (!/^[a-f0-9]{7,40}$/i.test(commitSha)) {
      throw new ValidationError("A valid commit SHA is required.");
    }

    this.evidence.push(Object.freeze({
      passed,
      evidence: evidence.trim(),
      commitSha: commitSha.toLowerCase(),
      revision: this.revision,
    }));

    this.transition(passed ? "verified" : "failed");
  }

  toJSON() {
    return {
      id: this.id,
      title: this.title,
      priority: this.priority,
      status: this.status,
      revision: this.revision,
      scenarios: this.scenarios,
      evidence: this.evidence,
    };
  }
}

class AcceptanceCriteriaService extends EventEmitter {
  #criteria = new Map();

  register(criterion) {
    if (!(criterion instanceof AcceptanceCriterion)) {
      throw new TypeError("Expected an AcceptanceCriterion.");
    }
    if (this.#criteria.has(criterion.id)) {
      throw new ValidationError(`Duplicate criterion: ${criterion.id}`);
    }

    this.#criteria.set(criterion.id, criterion);
    this.emit("criterion:registered", criterion.toJSON());
  }

  get(id) {
    const criterion = this.#criteria.get(id);
    if (!criterion) {
      throw new ValidationError(`Criterion not found: ${id}`);
    }
    return criterion;
  }

  markReady(id) {
    const criterion = this.get(id);
    criterion.transition("ready");
    this.emit("criterion:ready", criterion.toJSON());
  }

  execute(id, result) {
    const criterion = this.get(id);
    criterion.recordExecution(result);
    this.emit(`criterion:${criterion.status}`, criterion.toJSON());
  }

  report() {
    return [...this.#criteria.values()].map(item => item.toJSON());
  }
}

function createProtectedBranchCriterion() {
  return new AcceptanceCriterion({
    id: "AC-GOV-001",
    title: "Enforce protected branch merge criteria",
    description:
      "A pull request targeting a protected branch must meet review, " +
      "approval, and required-check conditions before merging.",
    priority: "must",
    owner: "Repository Maintainer",
    scenarios: [
      {
        given: "A protected branch requires one eligible approval",
        when: "A pull request has no eligible approval",
        then: "The merge is blocked",
        expected:
          "Passing automated checks do not replace the independent " +
          "approval required by repository policy.",
        tags: ["approval", "negative"],
      },
      {
        given:
          "The latest revision has approval and all required checks pass",
        when: "The merge service evaluates repository policy",
        then: "The request is eligible if no other rule blocks it",
        expected:
          "The eligibility decision uses current review and check states.",
        tags: ["branch-protection", "positive"],
      },
    ],
  });
}

function runTests() {
  const criterion = createProtectedBranchCriterion();
  assert.deepEqual(criterion.validate(), []);

  const service = new AcceptanceCriteriaService();
  const events = [];

  service.on("criterion:registered", item => events.push(item.status));
  service.on("criterion:ready", item => events.push(item.status));
  service.on("criterion:verified", item => events.push(item.status));

  service.register(criterion);
  service.markReady(criterion.id);

  assert.equal(criterion.status, "ready");

  service.execute(criterion.id, {
    passed: true,
    evidence: "CI checks and independent review policy test passed",
    commitSha: "a1b2c3d",
  });

  assert.equal(criterion.status, "verified");
  assert.deepEqual(events, ["draft", "ready", "verified"]);

  assert.throws(
    () => criterion.transition("draft"),
    InvalidTransitionError
  );

  assert.throws(
    () => service.get("AC-GOV-999"),
    ValidationError
  );

  assert.throws(
    () => service.execute(criterion.id, {
      passed: true,
      evidence: "Another execution",
      commitSha: "a1b2c3d",
    }),
    InvalidTransitionError
  );

  const invalid = createProtectedBranchCriterion();
  invalid.scenarios = [];
  assert.throws(() => invalid.transition("ready"), ValidationError);

  console.log("All acceptance criteria tests passed.");
  console.log(JSON.stringify(service.report(), null, 2));
}

if (require.main === module) {
  runTests();
}

module.exports = {
  AcceptanceCriterion,
  AcceptanceCriteriaService,
  ValidationError,
  InvalidTransitionError,
  validateScenario,
};
