"use strict";

/*
 * Event-driven Epic and Feature Management.
 *
 * Focuses on JavaScript-specific event handling, immutable event records,
 * optimistic concurrency, dependency-aware transitions, and asynchronous
 * delivery reporting.
 *
 * Run with Node.js 18 or later. No npm packages are required.
 */

const WorkType = Object.freeze({
  EPIC: "epic",
  FEATURE: "feature",
  STORY: "story",
  TASK: "task",
});

const Status = Object.freeze({
  BACKLOG: "backlog",
  READY: "ready",
  IN_PROGRESS: "in_progress",
  BLOCKED: "blocked",
  DONE: "done",
  CANCELLED: "cancelled",
});

const Priority = Object.freeze({
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
});

const EXPECTED_PARENT = Object.freeze({
  [WorkType.EPIC]: null,
  [WorkType.FEATURE]: WorkType.EPIC,
  [WorkType.STORY]: WorkType.FEATURE,
  [WorkType.TASK]: WorkType.STORY,
});

const ALLOWED_TRANSITIONS = Object.freeze({
  [Status.BACKLOG]: [Status.READY, Status.CANCELLED],
  [Status.READY]: [
    Status.IN_PROGRESS,
    Status.BLOCKED,
    Status.CANCELLED,
  ],
  [Status.IN_PROGRESS]: [
    Status.READY,
    Status.BLOCKED,
    Status.DONE,
    Status.CANCELLED,
  ],
  [Status.BLOCKED]: [
    Status.READY,
    Status.IN_PROGRESS,
    Status.CANCELLED,
  ],
  [Status.DONE]: [Status.READY],
  [Status.CANCELLED]: [Status.BACKLOG],
});

class DomainError extends Error {
  constructor(message) {
    super(message);
    this.name = "DomainError";
  }
}

function requireNonEmptyString(value, fieldName) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new DomainError(`${fieldName} must be a non-empty string.`);
  }
  return value.trim();
}

function validateNonNegativeNumber(value, fieldName) {
  if (
    value !== undefined &&
    value !== null &&
    (!Number.isFinite(value) || value < 0)
  ) {
    throw new DomainError(`${fieldName} must be a finite non-negative number.`);
  }
}

class WorkItem {
  constructor({
    id,
    title,
    type,
    parentId = null,
    status = Status.BACKLOG,
    priority = Priority.MEDIUM,
    owner = null,
    storyPoints = null,
    estimateHours = null,
    acceptanceCriteria = [],
    dependencyIds = [],
    labels = [],
  }) {
    this.id = requireNonEmptyString(id, "id");
    this.title = requireNonEmptyString(title, "title");

    if (!Object.values(WorkType).includes(type)) {
      throw new DomainError(`Unsupported work type: ${type}`);
    }

    if (!Object.values(Status).includes(status)) {
      throw new DomainError(`Unsupported status: ${status}`);
    }

    if (!Object.values(Priority).includes(priority)) {
      throw new DomainError(`Unsupported priority: ${priority}`);
    }

    validateNonNegativeNumber(storyPoints, "storyPoints");
    validateNonNegativeNumber(estimateHours, "estimateHours");

    if (type !== WorkType.STORY && storyPoints !== null) {
      throw new DomainError("Story points are only valid on user stories.");
    }

    if (type !== WorkType.TASK && estimateHours !== null) {
      throw new DomainError("Hour estimates are only valid on tasks.");
    }

    const criteria = acceptanceCriteria
      .map((criterion) => requireNonEmptyString(criterion, "acceptance criterion"));

    if (type === WorkType.STORY && criteria.length === 0) {
      throw new DomainError("Every user story needs acceptance criteria.");
    }

    const dependencies = [...new Set(dependencyIds)];
    if (dependencies.includes(this.id)) {
      throw new DomainError("An item cannot depend on itself.");
    }

    this.parentId = parentId;
    this.status = status;
    this.priority = priority;
    this.owner = owner;
    this.storyPoints = storyPoints;
    this.estimateHours = estimateHours;
    this.acceptanceCriteria = Object.freeze(criteria);
    this.dependencyIds = Object.freeze(dependencies);
    this.labels = Object.freeze([...new Set(labels)]);
    this.version = 1;
  }

  snapshot() {
    return Object.freeze({
      id: this.id,
      title: this.title,
      type: this.type,
      parentId: this.parentId,
      status: this.status,
      priority: this.priority,
      owner: this.owner,
      storyPoints: this.storyPoints,
      estimateHours: this.estimateHours,
      acceptanceCriteria: this.acceptanceCriteria,
      dependencyIds: this.dependencyIds,
      labels: this.labels,
      version: this.version,
    });
  }
}

class WorkManagementService {
  #items = new Map();
  #events = [];
  #listeners = new Set();
  #eventSequence = 0;

  subscribe(listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function.");
    }

    this.#listeners.add(listener);
    return () => this.#listeners.delete(listener);
  }

  #publish(event) {
    const immutableEvent = Object.freeze({
      sequence: ++this.#eventSequence,
      occurredAt: new Date().toISOString(),
      ...event,
    });

    this.#events.push(immutableEvent);

    // Listener failures must not undo a committed domain transition.
    for (const listener of this.#listeners) {
      try {
        listener(immutableEvent);
      } catch (error) {
        console.error(`Event listener failed: ${error.message}`);
      }
    }
  }

  get events() {
    return this.#events.map((event) => ({ ...event }));
  }

  get(id) {
    const item = this.#items.get(id);
    if (!item) {
      throw new DomainError(`Unknown work item: ${id}`);
    }
    return item;
  }

  add(item) {
    if (!(item instanceof WorkItem)) {
      throw new TypeError("Expected a WorkItem instance.");
    }

    if (this.#items.has(item.id)) {
      throw new DomainError(`Duplicate work item: ${item.id}`);
    }

    const expectedParent = EXPECTED_PARENT[item.type];

    if (expectedParent === null) {
      if (item.parentId !== null) {
        throw new DomainError("An epic cannot have a parent.");
      }
    } else {
      const parent = this.#items.get(item.parentId);

      if (!parent) {
        throw new DomainError(`Parent ${item.parentId} does not exist.`);
      }

      if (parent.type !== expectedParent) {
        throw new DomainError(
          `${item.type} must be a child of ${expectedParent}.`,
        );
      }
    }

    for (const dependencyId of item.dependencyIds) {
      if (!this.#items.has(dependencyId)) {
        throw new DomainError(`Unknown dependency: ${dependencyId}`);
      }
    }

    this.#items.set(item.id, item);

    try {
      this.#assertAcyclicDependencies();
    } catch (error) {
      this.#items.delete(item.id);
      throw error;
    }

    this.#publish({
      kind: "work_item_created",
      itemId: item.id,
      workType: item.type,
    });
  }

  children(parentId) {
    return [...this.#items.values()]
      .filter((item) => item.parentId === parentId)
      .sort((left, right) => left.id.localeCompare(right.id));
  }

  descendants(rootId) {
    const result = [];
    const stack = [...this.children(rootId)].reverse();

    while (stack.length) {
      const item = stack.pop();
      result.push(item);
      stack.push(...this.children(item.id).reverse());
    }

    return result;
  }

  #assertAcyclicDependencies() {
    const visiting = new Set();
    const visited = new Set();

    const visit = (id) => {
      if (visiting.has(id)) {
        throw new DomainError(`Dependency cycle found at ${id}.`);
      }
      if (visited.has(id)) return;

      visiting.add(id);
      for (const dependencyId of this.get(id).dependencyIds) {
        visit(dependencyId);
      }
      visiting.delete(id);
      visited.add(id);
    };

    for (const id of this.#items.keys()) {
      visit(id);
    }
  }

  unmetDependencies(id) {
    return this.get(id).dependencyIds.filter(
      (dependencyId) => this.get(dependencyId).status !== Status.DONE,
    );
  }

  transition(id, nextStatus, expectedVersion) {
    const item = this.get(id);

    // A client holding an old version must reload before changing state.
    if (item.version !== expectedVersion) {
      throw new DomainError(
        `Stale update for ${id}: expected version ${expectedVersion}, ` +
        `current version is ${item.version}.`,
      );
    }

    if (!Object.values(Status).includes(nextStatus)) {
      throw new DomainError(`Unknown status: ${nextStatus}`);
    }

    if (item.status === nextStatus) {
      return item.snapshot();
    }

    if (!ALLOWED_TRANSITIONS[item.status].includes(nextStatus)) {
      throw new DomainError(
        `Invalid transition: ${item.status} -> ${nextStatus}`,
      );
    }

    if (nextStatus === Status.IN_PROGRESS) {
      const unmet = this.unmetDependencies(id);
      if (unmet.length) {
        throw new DomainError(
          `${id} has incomplete dependencies: ${unmet.join(", ")}`,
        );
      }
    }

    if (nextStatus === Status.DONE) {
      const unfinished = this.descendants(id).filter(
        (candidate) =>
          [WorkType.STORY, WorkType.TASK].includes(candidate.type) &&
          ![Status.DONE, Status.CANCELLED].includes(candidate.status),
      );

      if (
        [WorkType.EPIC, WorkType.FEATURE].includes(item.type) &&
        unfinished.length
      ) {
        throw new DomainError(
          `${id} has unfinished descendants: ` +
          unfinished.map((candidate) => candidate.id).join(", "),
        );
      }

      if (
        item.type === WorkType.STORY &&
        this.children(id).some(
          (child) => ![Status.DONE, Status.CANCELLED].includes(child.status),
        )
      ) {
        throw new DomainError(`${id} still has unfinished tasks.`);
      }
    }

    const previousStatus = item.status;
    item.status = nextStatus;
    item.version += 1;

    this.#publish({
      kind: "status_changed",
      itemId: id,
      previousStatus,
      nextStatus,
      version: item.version,
    });

    return item.snapshot();
  }

  progress(rootId) {
    const stories = this.descendants(rootId).filter(
      (item) => item.type === WorkType.STORY && item.status !== Status.CANCELLED,
    );

    const estimated = stories.filter((story) => story.storyPoints !== null);
    const unestimated = stories.length - estimated.length;
    const total = estimated.reduce((sum, story) => sum + story.storyPoints, 0);
    const completed = estimated
      .filter((story) => story.status === Status.DONE)
      .reduce((sum, story) => sum + story.storyPoints, 0);

    return {
      epicId: rootId,
      unit: "story_points",
      total,
      completed,
      remaining: total - completed,
      percentComplete: total ? Number((completed / total * 100).toFixed(2)) : 0,
      unestimatedStories: unestimated,
    };
  }

  readiness(epicId) {
    const stories = this.descendants(epicId).filter(
      (item) => item.type === WorkType.STORY && item.status !== Status.CANCELLED,
    );

    const unfinished = stories
      .filter((story) => story.status !== Status.DONE)
      .map((story) => story.id);

    const blocked = this.descendants(epicId)
      .filter((item) => item.status === Status.BLOCKED)
      .map((item) => item.id);

    return {
      epicId,
      ready: unfinished.length === 0 && blocked.length === 0,
      unfinishedStories: unfinished,
      blockedItems: blocked,
    };
  }

  async report(epicId) {
    // Promise-based reporting allows the model to be integrated into
    // asynchronous APIs without blocking event-loop execution.
    await Promise.resolve();

    return {
      generatedAt: new Date().toISOString(),
      progress: this.progress(epicId),
      readiness: this.readiness(epicId),
      eventCount: this.#events.length,
    };
  }
}

async function main() {
  const service = new WorkManagementService();

  service.subscribe((event) => {
    if (event.kind === "status_changed") {
      console.log(
        `[event ${event.sequence}] ${event.itemId}: ` +
        `${event.previousStatus} -> ${event.nextStatus}`,
      );
    }
  });

  service.add(new WorkItem({
    id: "EP-200",
    title: "Enterprise Subscription Management",
    type: WorkType.EPIC,
    priority: Priority.CRITICAL,
    owner: "Product Management",
  }));

  service.add(new WorkItem({
    id: "FE-210",
    title: "Subscription Lifecycle",
    type: WorkType.FEATURE,
    parentId: "EP-200",
    owner: "Platform Team",
  }));

  service.add(new WorkItem({
    id: "ST-211",
    title: "As an administrator, I can activate a subscription",
    type: WorkType.STORY,
    parentId: "FE-210",
    storyPoints: 5,
    owner: "Platform Team",
    acceptanceCriteria: [
      "Activation records the effective date.",
      "A subscription cannot be activated twice.",
    ],
  }));

  service.add(new WorkItem({
    id: "TS-211A",
    title: "Implement activation transaction",
    type: WorkType.TASK,
    parentId: "ST-211",
    estimateHours: 6,
  }));

  service.add(new WorkItem({
    id: "TS-211B",
    title: "Add activation integration tests",
    type: WorkType.TASK,
    parentId: "ST-211",
    estimateHours: 4,
    dependencyIds: ["TS-211A"],
  }));

  service.add(new WorkItem({
    id: "ST-212",
    title: "As an administrator, I can cancel a subscription",
    type: WorkType.STORY,
    parentId: "FE-210",
    storyPoints: 8,
    owner: "Platform Team",
    acceptanceCriteria: [
      "Cancellation records a reason.",
      "Repeated cancellation requests are idempotent.",
    ],
  }));

  console.log("\nInitial progress");
  console.log(JSON.stringify(service.progress("EP-200"), null, 2));

  try {
    service.transition("TS-211B", Status.IN_PROGRESS, 1);
  } catch (error) {
    console.log(`Expected dependency rejection: ${error.message}`);
  }

  const task = service.get("TS-211A");
  service.transition(task.id, Status.READY, task.version);
  service.transition(task.id, Status.IN_PROGRESS, service.get(task.id).version);
  service.transition(task.id, Status.DONE, service.get(task.id).version);

  const dependent = service.get("TS-211B");
  service.transition(dependent.id, Status.READY, dependent.version);
  service.transition(
    dependent.id,
    Status.IN_PROGRESS,
    service.get(dependent.id).version,
  );
  service.transition(
    dependent.id,
    Status.DONE,
    service.get(dependent.id).version,
  );

  const story = service.get("ST-211");
  service.transition(story.id, Status.READY, story.version);
  service.transition(
    story.id,
    Status.IN_PROGRESS,
    service.get(story.id).version,
  );
  service.transition(
    story.id,
    Status.DONE,
    service.get(story.id).version,
  );

  try {
    // The earlier version is stale because the story has transitioned.
    service.transition("ST-211", Status.READY, 1);
  } catch (error) {
    console.log(`Expected concurrency rejection: ${error.message}`);
  }

  console.log("\nFinal report");
  console.log(JSON.stringify(await service.report("EP-200"), null, 2));

  console.log("\nImmutable event history");
  console.log(JSON.stringify(service.events, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
