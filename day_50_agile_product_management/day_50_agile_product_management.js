"use strict";

/*
 * Agile Product Management model.
 *
 * Product goal:
 *   Defines the measurable product outcome.
 *
 * Roadmap:
 *   Expresses directional outcomes and timing without becoming a detailed
 *   delivery promise.
 *
 * Product backlog:
 *   Holds validated opportunities and delivery candidates.
 *
 * Sprint goal:
 *   Defines the short-term outcome that gives a sprint a coherent purpose.
 *
 * Continuous discovery:
 *   Produces evidence that can change backlog priority before implementation.
 */

class ValidationError extends Error {}

const BacklogState = Object.freeze({
  DISCOVERY: "discovery",
  READY: "ready",
  IN_PROGRESS: "in_progress",
  DONE: "done"
});

const Priority = Object.freeze({
  CRITICAL: 4,
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1
});

class ProductGoal {
  constructor({ id, statement, metric, target, deadline }) {
    if (!id || !statement || !metric) {
      throw new ValidationError("Product goal requires id, statement, and metric");
    }
    if (!Number.isFinite(target) || target < 0 || target > 1) {
      throw new ValidationError("Product goal target must be between 0 and 1");
    }

    this.id = id;
    this.statement = statement;
    this.metric = metric;
    this.target = target;
    this.deadline = new Date(deadline);

    if (Number.isNaN(this.deadline.getTime())) {
      throw new ValidationError("Invalid product-goal deadline");
    }
  }
}

class BacklogItem {
  constructor({
    id,
    title,
    problem,
    value,
    effort,
    priority,
    state = BacklogState.DISCOVERY,
    evidence = []
  }) {
    if (!id || !title || !problem) {
      throw new ValidationError("Backlog item requires id, title, and problem");
    }
    if (!Number.isInteger(value) || value < 1 || value > 100) {
      throw new ValidationError("Backlog value must be an integer from 1 to 100");
    }
    if (!Number.isInteger(effort) || effort < 1 || effort > 100) {
      throw new ValidationError("Backlog effort must be an integer from 1 to 100");
    }
    if (!(priority in Priority)) {
      throw new ValidationError(`Unknown priority: ${priority}`);
    }
    if (!Array.isArray(evidence) || evidence.length === 0) {
      throw new ValidationError("Backlog item requires discovery evidence");
    }

    this.id = id;
    this.title = title;
    this.problem = problem;
    this.value = value;
    this.effort = effort;
    this.priority = priority;
    this.state = state;
    this.evidence = [...evidence];
  }

  score() {
    return (this.value * Priority[this.priority]) / this.effort;
  }
}

class RoadmapOutcome {
  constructor({ id, statement, targetDate, productGoalId }) {
    if (!id || !statement || !productGoalId) {
      throw new ValidationError("Roadmap outcome has missing required fields");
    }

    const parsedDate = new Date(targetDate);
    if (Number.isNaN(parsedDate.getTime())) {
      throw new ValidationError("Invalid roadmap target date");
    }

    this.id = id;
    this.statement = statement;
    this.targetDate = parsedDate;
    this.productGoalId = productGoalId;
  }
}

class DiscoveryExperiment {
  constructor({ id, hypothesis, method, threshold }) {
    if (!id || !hypothesis || !method) {
      throw new ValidationError("Discovery experiment requires all descriptive fields");
    }
    if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
      throw new ValidationError("Experiment threshold must be between 0 and 1");
    }

    this.id = id;
    this.hypothesis = hypothesis;
    this.method = method;
    this.threshold = threshold;
    this.observations = [];
  }

  recordObservation(value) {
    if (!Number.isFinite(value) || value < 0 || value > 1) {
      throw new ValidationError("Observation must be between 0 and 1");
    }
    this.observations.push(value);
  }

  result() {
    if (this.observations.length === 0) {
      return null;
    }
    return this.observations.reduce((sum, value) => sum + value, 0) /
      this.observations.length;
  }

  supportsHypothesis() {
    const result = this.result();
    return result !== null && result >= this.threshold;
  }
}

class Sprint {
  constructor({ id, start, end, goal }) {
    if (!id || !goal) {
      throw new ValidationError("Sprint requires id and goal");
    }

    this.id = id;
    this.start = new Date(start);
    this.end = new Date(end);
    this.goal = goal;
    this.items = [];

    if (Number.isNaN(this.start.getTime()) || Number.isNaN(this.end.getTime())) {
      throw new ValidationError("Sprint dates are invalid");
    }
    if (this.start > this.end) {
      throw new ValidationError("Sprint start cannot be after sprint end");
    }
  }

  addItem(item) {
    if (item.state !== BacklogState.READY &&
        item.state !== BacklogState.DISCOVERY) {
      throw new ValidationError(`Cannot select item ${item.id} in state ${item.state}`);
    }

    item.state = BacklogState.IN_PROGRESS;
    this.items.push(item.id);
  }
}

class ProductManagementEngine {
  constructor() {
    this.goals = new Map();
    this.backlog = new Map();
    this.roadmap = new Map();
    this.sprints = new Map();
    this.experiments = new Map();
    this.events = [];
  }

  addGoal(goal) {
    if (this.goals.has(goal.id)) {
      throw new ValidationError(`Duplicate goal ${goal.id}`);
    }
    this.goals.set(goal.id, goal);
    this.events.push({ type: "goal_created", id: goal.id });
  }

  addBacklogItem(item) {
    if (this.backlog.has(item.id)) {
      throw new ValidationError(`Duplicate backlog item ${item.id}`);
    }
    this.backlog.set(item.id, item);
    this.events.push({ type: "backlog_item_added", id: item.id });
  }

  addRoadmapOutcome(outcome) {
    if (!this.goals.has(outcome.productGoalId)) {
      throw new ValidationError("Roadmap outcome references an unknown goal");
    }
    if (this.roadmap.has(outcome.id)) {
      throw new ValidationError(`Duplicate roadmap outcome ${outcome.id}`);
    }
    this.roadmap.set(outcome.id, outcome);
  }

  addExperiment(experiment) {
    if (this.experiments.has(experiment.id)) {
      throw new ValidationError(`Duplicate experiment ${experiment.id}`);
    }
    this.experiments.set(experiment.id, experiment);
  }

  prioritizedBacklog() {
    return [...this.backlog.values()]
      .filter(item =>
        item.state === BacklogState.READY ||
        item.state === BacklogState.DISCOVERY
      )
      .sort((a, b) =>
        b.score() - a.score() ||
        Priority[b.priority] - Priority[a.priority]
      );
  }

  createSprint({ id, start, end, goalId, statement, capacity }) {
    if (!Number.isInteger(capacity) || capacity <= 0) {
      throw new ValidationError("Sprint capacity must be positive");
    }
    if (!this.goals.has(goalId)) {
      throw new ValidationError("Sprint goal references an unknown product goal");
    }
    if (this.sprints.has(id)) {
      throw new ValidationError(`Duplicate sprint ${id}`);
    }

    const sprint = new Sprint({
      id,
      start,
      end,
      goal: { productGoalId: goalId, statement }
    });

    let remaining = capacity;

    for (const item of this.prioritizedBacklog()) {
      if (item.effort <= remaining) {
        sprint.addItem(item);
        remaining -= item.effort;
      }
    }

    if (sprint.items.length === 0) {
      throw new ValidationError("No backlog item fits sprint capacity");
    }

    this.sprints.set(id, sprint);
    this.events.push({
      type: "sprint_created",
      id,
      selectedItems: [...sprint.items]
    });

    return sprint;
  }

  completeItem(itemId, sprintId) {
    const item = this.backlog.get(itemId);
    const sprint = this.sprints.get(sprintId);

    if (!item || !sprint) {
      throw new ValidationError("Unknown backlog item or sprint");
    }
    if (!sprint.items.includes(itemId)) {
      throw new ValidationError("Item does not belong to the sprint");
    }
    if (item.state !== BacklogState.IN_PROGRESS) {
      throw new ValidationError("Only in-progress items can be completed");
    }

    item.state = BacklogState.DONE;
    this.events.push({
      type: "backlog_item_completed",
      itemId,
      sprintId
    });
  }

  report() {
    return {
      productGoals: this.goals.size,
      roadmapOutcomes: this.roadmap.size,
      backlogItems: this.backlog.size,
      sprints: this.sprints.size,
      experiments: this.experiments.size,
      prioritizedBacklog: this.prioritizedBacklog().map(item => ({
        id: item.id,
        score: Number(item.score().toFixed(2)),
        state: item.state
      })),
      discovery: [...this.experiments.values()].map(experiment => ({
        id: experiment.id,
        result: experiment.result(),
        supportsHypothesis: experiment.supportsHypothesis()
      }))
    };
  }
}

function createDemo() {
  const engine = new ProductManagementEngine();

  engine.addGoal(new ProductGoal({
    id: "PG-01",
    statement: "Increase successful first-week activation.",
    metric: "activation_rate",
    target: 0.65,
    deadline: "2027-01-18"
  }));

  engine.addRoadmapOutcome(new RoadmapOutcome({
    id: "RO-01",
    statement: "Reduce onboarding friction before first value.",
    targetDate: "2026-12-04",
    productGoalId: "PG-01"
  }));

  engine.addBacklogItem(new BacklogItem({
    id: "PB-101",
    title: "Simplify first-run setup",
    problem: "New users abandon setup before reaching first value.",
    value: 90,
    effort: 8,
    priority: "CRITICAL",
    state: BacklogState.READY,
    evidence: ["funnel data", "user interviews"]
  }));

  engine.addBacklogItem(new BacklogItem({
    id: "PB-102",
    title: "Add contextual onboarding checklist",
    problem: "Users cannot identify their next useful action.",
    value: 82,
    effort: 5,
    priority: "HIGH",
    state: BacklogState.READY,
    evidence: ["support tickets", "interviews"]
  }));

  engine.addBacklogItem(new BacklogItem({
    id: "PB-103",
    title: "Improve recurring report navigation",
    problem: "Existing users spend too long locating reports.",
    value: 65,
    effort: 13,
    priority: "MEDIUM",
    state: BacklogState.READY,
    evidence: ["navigation analytics"]
  }));

  const experiment = new DiscoveryExperiment({
    id: "EXP-01",
    hypothesis: "A guided setup improves first-value completion.",
    method: "Prototype usability test",
    threshold: 0.70
  });

  [0.72, 0.76, 0.68, 0.74].forEach(value =>
    experiment.recordObservation(value)
  );

  engine.addExperiment(experiment);

  engine.createSprint({
    id: "SPR-01",
    start: "2026-10-20",
    end: "2026-11-02",
    goalId: "PG-01",
    statement: "Improve the path from account creation to first value.",
    capacity: 13
  });

  return engine;
}

async function run() {
  // The async boundary models how a real product system could receive
  // discovery events, analytics results, or backlog changes from services.
  await Promise.resolve();

  const engine = createDemo();
  console.log(JSON.stringify(engine.report(), null, 2));

  const sprint = engine.sprints.get("SPR-01");
  if (sprint && sprint.items.length > 0) {
    engine.completeItem(sprint.items[0], sprint.id);
  }

  console.log("\nAfter completion:");
  console.log(JSON.stringify(engine.report(), null, 2));

  console.log("\nEvent stream:");
  for (const event of engine.events) {
    console.log(`${event.type}: ${JSON.stringify(event)}`);
  }
}

run().catch(error => {
  console.error(`Product management workflow failed: ${error.message}`);
  process.exitCode = 1;
});
