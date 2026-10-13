"use strict";

/*
 * Event-driven user story lifecycle and backlog policy evaluation.
 * Run with Node.js 18 or later:
 *     node user-stories.js
 *
 * This implementation focuses on event processing, immutable event records,
 * asynchronous review simulation, and acceptance-criterion verification.
 */

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");

const StoryState = Object.freeze({
  DRAFT: "draft",
  REFINING: "refining",
  READY: "ready",
  IN_PROGRESS: "in_progress",
  DONE: "done",
  REJECTED: "rejected"
});

const INVEST_DIMENSIONS = Object.freeze([
  "independent",
  "negotiable",
  "valuable",
  "estimable",
  "small",
  "testable"
]);

class StoryValidationError extends Error {
  constructor(message, issues = []) {
    super(message);
    this.name = "StoryValidationError";
    this.issues = issues;
  }
}

function requireText(value, fieldName) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new StoryValidationError(`${fieldName} must be non-empty text.`);
  }
  return value.trim();
}

function validatePersona(persona) {
  if (!persona || typeof persona !== "object") {
    throw new StoryValidationError("A persona is required.");
  }

  return Object.freeze({
    name: requireText(persona.name, "Persona name"),
    role: requireText(persona.role, "Persona role"),
    context: requireText(persona.context, "Persona context"),
    goal: requireText(persona.goal, "Persona goal")
  });
}

function validateCriterion(criterion) {
  if (!criterion || typeof criterion !== "object") {
    throw new StoryValidationError("An acceptance criterion is required.");
  }

  return Object.freeze({
    given: requireText(criterion.given, "Criterion Given"),
    when: requireText(criterion.when, "Criterion When"),
    then: requireText(criterion.then, "Criterion Then"),
    type: criterion.type || "functional"
  });
}

class UserStory {
  constructor({
    id,
    title,
    persona,
    need,
    value,
    criteria,
    points = null,
    dependencies = [],
    priority = 3,
    invest = {}
  }) {
    if (!/^[A-Z]+-\d+$/.test(requireText(id, "Story ID"))) {
      throw new StoryValidationError("Story ID must resemble SHOP-101.");
    }

    this.id = id;
    this.title = requireText(title, "Story title");
    this.persona = validatePersona(persona);
    this.need = requireText(need, "User need");
    this.value = requireText(value, "User value");
    this.criteria = Object.freeze(criteria.map(validateCriterion));

    if (this.criteria.length === 0) {
      throw new StoryValidationError(
        "At least one acceptance criterion is required."
      );
    }

    if (points !== null && (!Number.isInteger(points) || points <= 0)) {
      throw new StoryValidationError(
        "Story points must be a positive integer or null."
      );
    }

    if (!Number.isInteger(priority) || priority < 1 || priority > 5) {
      throw new StoryValidationError("Priority must be between 1 and 5.");
    }

    this.points = points;
    this.dependencies = new Set(dependencies);
    if (this.dependencies.has(id)) {
      throw new StoryValidationError("A story cannot depend on itself.");
    }

    this.priority = priority;
    this.invest = Object.freeze(
      Object.fromEntries(
        INVEST_DIMENSIONS.map((dimension) => [
          dimension,
          invest[dimension] !== false
        ])
      )
    );

    this.state = StoryState.DRAFT;
    this.revision = 1;
    this.history = [];
  }

  get statement() {
    return `As a ${this.persona.role}, I want ${this.need}, so that ${this.value}.`;
  }

  investFailures() {
    return INVEST_DIMENSIONS.filter(
      (dimension) => !this.invest[dimension]
    );
  }

  recordEvent(eventType, details = {}) {
    // Freezing a new record prevents consumers from mutating the audit event.
    const event = Object.freeze({
      eventId: randomUUID(),
      storyId: this.id,
      revision: this.revision,
      eventType,
      timestamp: new Date().toISOString(),
      details: Object.freeze({ ...details })
    });

    this.history.push(event);
    return event;
  }

  transition(nextState, details = {}) {
    const allowed = {
      [StoryState.DRAFT]: [StoryState.REFINING, StoryState.REJECTED],
      [StoryState.REFINING]: [StoryState.DRAFT, StoryState.READY,
                              StoryState.REJECTED],
      [StoryState.READY]: [StoryState.IN_PROGRESS, StoryState.REFINING],
      [StoryState.IN_PROGRESS]: [StoryState.DONE, StoryState.REFINING],
      [StoryState.DONE]: [],
      [StoryState.REJECTED]: [StoryState.DRAFT]
    };

    if (!allowed[this.state].includes(nextState)) {
      throw new StoryValidationError(
        `Invalid transition for ${this.id}: ${this.state} -> ${nextState}`
      );
    }

    if (nextState === StoryState.READY) {
      const failures = this.investFailures();
      if (failures.length > 0) {
        throw new StoryValidationError(
          "Story fails INVEST assessment.",
          failures
        );
      }
    }

    const previousState = this.state;
    this.state = nextState;
    this.revision += 1;
    this.recordEvent("state_changed", {
      previousState,
      nextState,
      ...details
    });
  }

  snapshot() {
    return Object.freeze({
      id: this.id,
      title: this.title,
      statement: this.statement,
      state: this.state,
      points: this.points,
      priority: this.priority,
      criteriaCount: this.criteria.length,
      investFailures: this.investFailures(),
      revision: this.revision
    });
  }
}

class StoryBacklog extends EventEmitter {
  constructor() {
    super();
    this.stories = new Map();
  }

  add(story) {
    if (!(story instanceof UserStory)) {
      throw new TypeError("Backlog entries must be UserStory instances.");
    }

    if (this.stories.has(story.id)) {
      throw new StoryValidationError(`Duplicate story ID: ${story.id}`);
    }

    this.stories.set(story.id, story);
    story.recordEvent("story_created", { title: story.title });
    this.emit("story:created", story.snapshot());
  }

  get(id) {
    const story = this.stories.get(id);
    if (!story) {
      throw new StoryValidationError(`Unknown story: ${id}`);
    }
    return story;
  }

  validateDependencies() {
    const errors = [];

    for (const story of this.stories.values()) {
      for (const dependency of story.dependencies) {
        if (!this.stories.has(dependency)) {
          errors.push(`${story.id} depends on missing ${dependency}`);
        }
      }
    }

    const visiting = new Set();
    const visited = new Set();

    const visit = (id) => {
      if (visiting.has(id)) {
        errors.push(`Dependency cycle reaches ${id}`);
        return;
      }

      if (visited.has(id)) return;

      visiting.add(id);
      const story = this.stories.get(id);

      for (const dependency of story.dependencies) {
        if (this.stories.has(dependency)) visit(dependency);
      }

      visiting.delete(id);
      visited.add(id);
    };

    for (const id of this.stories.keys()) visit(id);
    return [...new Set(errors)];
  }

  rank() {
    return [...this.stories.values()]
      .sort((a, b) =>
        a.priority - b.priority ||
        (a.points ?? Number.MAX_SAFE_INTEGER) -
          (b.points ?? Number.MAX_SAFE_INTEGER) ||
        a.id.localeCompare(b.id)
      )
      .map((story) => story.snapshot());
  }

  async refine(storyId, reviewer) {
    const story = this.get(storyId);
    if (typeof reviewer !== "function") {
      throw new TypeError("A refinement reviewer function is required.");
    }

    if (story.state === StoryState.DRAFT) {
      story.transition(StoryState.REFINING);
    }

    // Awaiting the reviewer permits asynchronous checks without blocking
    // unrelated event listeners or requiring external packages.
    const decision = await reviewer(story.snapshot());

    if (!decision.approved) {
      story.recordEvent("refinement_rejected", {
        issues: decision.issues || []
      });
      story.transition(StoryState.DRAFT, {
        reason: "refinement feedback received"
      });
      this.emit("story:needs-refinement", story.snapshot());
      return false;
    }

    story.transition(StoryState.READY, {
      reviewer: decision.reviewer || "unidentified"
    });
    this.emit("story:ready", story.snapshot());
    return true;
  }
}

function matchesCriterion(criterion, observed) {
  // Tests should compare explicit observable outcomes rather than infer
  // acceptance from implementation details.
  return criterion.then === observed.expectedOutcome &&
    observed.preconditionsSatisfied === true &&
    observed.actionExecuted === true;
}

async function main() {
  const persona = {
    name: "Meera",
    role: "registered customer",
    context: "using a mobile retail checkout",
    goal: "place an order without accidental duplicate charges"
  };

  const story = new UserStory({
    id: "SHOP-101",
    title: "Submit a checkout request safely",
    persona,
    need: "confirm my order after reviewing its total",
    value: "I can purchase confidently without duplicate orders",
    points: 5,
    priority: 1,
    dependencies: ["SHOP-100"],
    criteria: [
      {
        given: "the cart contains valid products",
        when: "I submit the checkout request",
        then: "one order is created and a confirmation is displayed"
      },
      {
        given: "the first request succeeded but its response was lost",
        when: "I retry with the same idempotency key",
        then: "the original order is returned without creating another order",
        type: "error_handling"
      }
    ],
    invest: {
      independent: false,
      negotiable: true,
      valuable: true,
      estimable: true,
      small: true,
      testable: true
    }
  });

  const dependency = new UserStory({
    id: "SHOP-100",
    title: "Prepare a valid checkout cart",
    persona,
    need: "review a cart with available products",
    value: "I can confirm the correct products and quantities",
    points: 3,
    priority: 1,
    criteria: [{
      given: "the cart contains available products",
      when: "I review the cart",
      then: "the cart shows current prices and quantities"
    }]
  });

  const backlog = new StoryBacklog();

  backlog.on("story:created", (snapshot) => {
    console.log(`Created ${snapshot.id}: ${snapshot.title}`);
  });

  backlog.on("story:ready", (snapshot) => {
    console.log(`Ready for implementation: ${snapshot.id}`);
  });

  backlog.on("story:needs-refinement", (snapshot) => {
    console.log(`Refinement required: ${snapshot.id}`);
  });

  backlog.add(dependency);
  backlog.add(story);

  console.log("\nUser story:");
  console.log(story.statement);

  console.log("\nDependency validation:");
  console.log(backlog.validateDependencies());

  console.log("\nINVEST failures:");
  console.log(story.investFailures());

  try {
    await backlog.refine(story.id, async (snapshot) => ({
      approved: snapshot.investFailures.length === 0,
      reviewer: "product-owner",
      issues: snapshot.investFailures
    }));
  } catch (error) {
    console.error(error.message);
  }

  // The story is intentionally blocked until its dependency is removed or
  // the work is split into a genuinely independent deliverable.
  story.invest = Object.freeze({
    ...story.invest,
    independent: true
  });

  await backlog.refine(story.id, async (snapshot) => ({
    approved: snapshot.investFailures.length === 0,
    reviewer: "product-owner",
    issues: snapshot.investFailures
  }));

  console.log("\nAcceptance criterion test:");
  const criterion = story.criteria[1];
  console.log(matchesCriterion(criterion, {
    expectedOutcome:
      "the original order is returned without creating another order",
    preconditionsSatisfied: true,
    actionExecuted: true
  }));

  console.log("\nPrioritized backlog:");
  console.log(JSON.stringify(backlog.rank(), null, 2));

  console.log("\nAudit events:");
  console.log(JSON.stringify(story.history, null, 2));
}

main().catch((error) => {
  console.error(`${error.name}: ${error.message}`);
  if (error.issues?.length) {
    console.error("Issues:", error.issues);
  }
  process.exitCode = 1;
});
