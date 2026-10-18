"use strict";

/*
 * Scrum workflow simulator for a payment reliability product.
 * Run with: node scrum.js
 *
 * This implementation uses JavaScript event-driven state transitions,
 * immutable role definitions, backlog ordering, and explicit validation.
 */

const Role = Object.freeze({
  PRODUCT_OWNER: "Product Owner",
  SCRUM_MASTER: "Scrum Master",
  DEVELOPER: "Developer",
});

const Status = Object.freeze({
  TODO: "To Do",
  IN_PROGRESS: "In Progress",
  DONE: "Done",
});

const EventName = Object.freeze({
  PLANNING: "Sprint Planning",
  DAILY: "Daily Scrum",
  REVIEW: "Sprint Review",
  RETROSPECTIVE: "Sprint Retrospective",
});

class ScrumError extends Error {
  constructor(message) {
    super(message);
    this.name = "ScrumError";
  }
}

class BacklogItem {
  constructor({ id, title, priority, estimate, criteria }) {
    if (!id?.trim() || !title?.trim()) {
      throw new ScrumError("Item ID and title are required.");
    }
    if (!Number.isInteger(priority) || priority < 1) {
      throw new ScrumError("Priority must be a positive integer.");
    }
    if (!Number.isInteger(estimate) || estimate < 0) {
      throw new ScrumError("Estimate must be a non-negative integer.");
    }
    if (!Array.isArray(criteria) || criteria.length === 0) {
      throw new ScrumError("Acceptance criteria are required.");
    }

    this.id = id;
    this.title = title;
    this.priority = priority;
    this.estimate = estimate;
    this.criteria = [...criteria];
    this.status = Status.TODO;
    this.accepted = false;
  }
}

class ScrumEventBus {
  #listeners = new Map();

  on(eventName, listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function.");
    }
    const listeners = this.#listeners.get(eventName) ?? [];
    listeners.push(listener);
    this.#listeners.set(eventName, listeners);
  }

  emit(eventName, payload) {
    // Snapshot listeners so subscription changes during dispatch do not
    // modify the current iteration.
    const listeners = [...(this.#listeners.get(eventName) ?? [])];
    for (const listener of listeners) {
      listener(Object.freeze({ ...payload }));
    }
  }
}

class ScrumBoard {
  constructor({ product, productOwner, scrumMaster, developers, backlog }) {
    if (!product?.trim()) {
      throw new ScrumError("Product name is required.");
    }
    if (!productOwner?.trim() || !scrumMaster?.trim()) {
      throw new ScrumError("Product Owner and Scrum Master are required.");
    }
    if (!Array.isArray(developers) || developers.length === 0) {
      throw new ScrumError("At least one Developer is required.");
    }
    if (new Set([productOwner, scrumMaster, ...developers]).size !==
        2 + developers.length) {
      throw new ScrumError("Each member must have a distinct name.");
    }

    const ids = backlog.map((item) => item.id);
    if (new Set(ids).size !== ids.length) {
      throw new ScrumError("Backlog item IDs must be unique.");
    }

    this.product = product;
    this.roles = Object.freeze({
      productOwner,
      scrumMaster,
      developers: Object.freeze([...developers]),
    });
    this.productBacklog = [...backlog];
    this.sprintBacklog = [];
    this.increment = [];
    this.currentSprint = null;
    this.events = [];
    this.bus = new ScrumEventBus();

    this.bus.on("scrum:event", (event) => {
      this.events.push(event);
      console.log(`[${event.type}] ${event.message}`);
    });
  }

  record(type, message, details = {}) {
    this.bus.emit("scrum:event", {
      type,
      message,
      details,
      timestamp: new Date().toISOString(),
    });
  }

  refineBacklog() {
    // sort() mutates its receiver, so sort a copy to preserve the original
    // array reference when other components are observing it.
    this.productBacklog = [...this.productBacklog].sort(
      (a, b) => a.priority - b.priority || a.id.localeCompare(b.id),
    );
  }

  planSprint({ number, startDate, durationDays, goal, capacity }) {
    if (this.currentSprint && !this.currentSprint.closed) {
      throw new ScrumError("The previous sprint must be closed.");
    }
    if (!Number.isInteger(number) || number < 1) {
      throw new ScrumError("Sprint number must be positive.");
    }
    if (!Number.isInteger(durationDays) || durationDays < 1 ||
        durationDays > 30) {
      throw new ScrumError("Sprint duration must be between 1 and 30 days.");
    }
    if (!(startDate instanceof Date) || Number.isNaN(startDate.getTime())) {
      throw new ScrumError("A valid start date is required.");
    }
    if (!goal?.trim()) {
      throw new ScrumError("The Sprint Goal cannot be empty.");
    }
    if (!Number.isInteger(capacity) || capacity < 0) {
      throw new ScrumError("Capacity must be a non-negative integer.");
    }

    let remaining = capacity;
    const selected = [];

    for (const item of this.productBacklog) {
      if (item.status !== Status.TODO) continue;
      if (item.estimate <= remaining) {
        selected.push(item);
        remaining -= item.estimate;
      }
    }

    this.sprintBacklog = [...selected];
    this.currentSprint = {
      number,
      startDate: new Date(startDate),
      durationDays,
      goal,
      selected,
      impediments: [],
      reviewCompleted: false,
      retrospectiveCompleted: false,
      closed: false,
    };

    this.record(
      EventName.PLANNING,
      `Sprint ${number}: ${goal}; ${selected.length} items selected.`,
      { capacity, remainingCapacity: remaining },
    );
    return this.currentSprint;
  }

  #activeSprint() {
    if (!this.currentSprint || this.currentSprint.closed) {
      throw new ScrumError("No active sprint.");
    }
    return this.currentSprint;
  }

  #item(id) {
    const sprint = this.#activeSprint();
    const item = sprint.selected.find((candidate) => candidate.id === id);
    if (!item) throw new ScrumError(`${id} is not in the Sprint Backlog.`);
    return item;
  }

  updateStatus(id, nextStatus) {
    const item = this.#item(id);
    const validTransitions = {
      [Status.TODO]: [Status.IN_PROGRESS],
      [Status.IN_PROGRESS]: [Status.DONE, Status.TODO],
      [Status.DONE]: [],
    };

    if (!validTransitions[item.status].includes(nextStatus)) {
      throw new ScrumError(
        `Invalid transition for ${id}: ${item.status} -> ${nextStatus}`,
      );
    }

    item.status = nextStatus;
    this.record(EventName.DAILY, `${id} changed to ${nextStatus}.`);
  }

  dailyScrum(date, updates = {}, impediments = []) {
    const sprint = this.#activeSprint();
    if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
      throw new ScrumError("Daily Scrum requires a valid date.");
    }

    const endDate = new Date(sprint.startDate);
    endDate.setDate(endDate.getDate() + sprint.durationDays - 1);
    if (date < sprint.startDate || date > endDate) {
      throw new ScrumError("Daily Scrum must occur within the sprint.");
    }

    // Validate every requested transition before applying any update,
    // avoiding a partially applied daily update when one item is invalid.
    const transitions = Object.entries(updates).map(([id, status]) => {
      const item = this.#item(id);
      const allowed = {
        [Status.TODO]: [Status.IN_PROGRESS],
        [Status.IN_PROGRESS]: [Status.DONE, Status.TODO],
        [Status.DONE]: [],
      };
      if (!allowed[item.status].includes(status)) {
        throw new ScrumError(`Invalid transition for ${id}.`);
      }
      return { item, status };
    });

    for (const { item, status } of transitions) {
      item.status = status;
    }
    for (const impediment of impediments) {
      if (typeof impediment === "string" && impediment.trim() &&
          !sprint.impediments.includes(impediment)) {
        sprint.impediments.push(impediment);
      }
    }

    this.record(
      EventName.DAILY,
      `${date.toISOString().slice(0, 10)}: inspect progress toward the Sprint Goal.`,
      { updates, impediments: [...sprint.impediments] },
    );
  }

  sprintReview(feedback = []) {
    const sprint = this.#activeSprint();
    if (sprint.reviewCompleted) {
      throw new ScrumError("Sprint Review already completed.");
    }

    for (const item of sprint.selected) {
      if (item.status === Status.DONE) {
        item.accepted = true;
        this.increment.push(item);
      } else {
        // Incomplete work is not part of the Increment. It returns to
        // the Product Backlog for reordering rather than being carried over.
        item.status = Status.TODO;
        item.accepted = false;
      }
    }

    sprint.reviewCompleted = true;
    this.record(EventName.REVIEW, "Stakeholders inspected the Increment.", {
      acceptedItems: this.increment.map((item) => item.id),
      feedback: [...feedback],
    });
  }

  retrospective(actions) {
    const sprint = this.#activeSprint();
    if (!sprint.reviewCompleted) {
      throw new ScrumError("Sprint Review must precede this simulation's retrospective.");
    }
    if (sprint.retrospectiveCompleted) {
      throw new ScrumError("Retrospective already completed.");
    }

    const validActions = actions.filter(
      (action) => typeof action === "string" && action.trim(),
    );
    sprint.retrospectiveCompleted = true;
    this.record(EventName.RETROSPECTIVE, "Team identified process improvements.", {
      actions: validActions,
    });
  }

  closeSprint() {
    const sprint = this.#activeSprint();
    if (!sprint.reviewCompleted || !sprint.retrospectiveCompleted) {
      throw new ScrumError("Review and retrospective must be recorded.");
    }
    sprint.closed = true;
    this.record("Sprint Closed", `Sprint ${sprint.number} closed.`);
  }

  report() {
    const acceptedPoints = this.increment.reduce(
      (total, item) => total + item.estimate,
      0,
    );
    return {
      product: this.product,
      productOwner: this.roles.productOwner,
      scrumMaster: this.roles.scrumMaster,
      developers: [...this.roles.developers],
      productBacklogCount: this.productBacklog.length,
      sprintBacklogCount: this.sprintBacklog.length,
      incrementCount: this.increment.length,
      acceptedPoints,
      eventCount: this.events.length,
    };
  }
}

function createBacklog() {
  return [
    new BacklogItem({
      id: "PAY-201",
      title: "Validate payment request schema",
      priority: 1,
      estimate: 5,
      criteria: ["Reject malformed payloads", "Return actionable errors"],
    }),
    new BacklogItem({
      id: "PAY-202",
      title: "Persist payment audit events",
      priority: 2,
      estimate: 8,
      criteria: ["Record outcome", "Include a correlation identifier"],
    }),
    new BacklogItem({
      id: "PAY-203",
      title: "Expose transaction status",
      priority: 3,
      estimate: 3,
      criteria: ["Authorized clients can query transaction state"],
    }),
  ];
}

function main() {
  const board = new ScrumBoard({
    product: "Payment Reliability Platform",
    productOwner: "Maya",
    scrumMaster: "Arjun",
    developers: ["Neha", "Kabir", "Sara"],
    backlog: createBacklog(),
  });

  board.bus.on(EventName.REVIEW, (event) => {
    console.log("Review event received:", event.message);
  });

  board.refineBacklog();

  const sprint = board.planSprint({
    number: 1,
    startDate: new Date("2026-10-19T00:00:00Z"),
    durationDays: 10,
    goal: "Make payment validation dependable.",
    capacity: 16,
  });

  if (sprint.selected.length > 0) {
    const first = sprint.selected[0];
    board.updateStatus(first.id, Status.IN_PROGRESS);
    board.dailyScrum(
      new Date("2026-10-19T00:00:00Z"),
      { [first.id]: Status.DONE },
      ["Test environment needs representative failure fixtures"],
    );
  }

  board.sprintReview(["Validate malformed payment payloads with stakeholders."]);
  board.retrospective([
    "Create failure fixtures before development begins.",
    "Review acceptance criteria earlier.",
  ]);
  board.closeSprint();

  console.log("\nDelivery report");
  console.log(JSON.stringify(board.report(), null, 2));

  try {
    board.updateStatus("UNKNOWN", Status.IN_PROGRESS);
  } catch (error) {
    console.log("Expected validation failure:", error.message);
  }
}

main();
