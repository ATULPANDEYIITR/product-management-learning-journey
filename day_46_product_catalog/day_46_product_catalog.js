"use strict";

/*
 * Product backlog workflow model for a Node.js runtime.
 * Focus: refinement events, dependency-aware ordering, prioritization,
 * acceptance criteria, and technical-debt forecasting.
 */

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");

class BacklogError extends Error {
  constructor(message) {
    super(message);
    this.name = "BacklogError";
  }
}

const Status = Object.freeze({
  PROPOSED: "proposed",
  REFINING: "refining",
  READY: "ready",
  IN_PROGRESS: "in_progress",
  BLOCKED: "blocked",
  DONE: "done",
  REJECTED: "rejected"
});

const Type = Object.freeze({
  FEATURE: "feature",
  BUG: "bug",
  DEBT: "technical_debt",
  SPIKE: "spike",
  SECURITY: "security"
});

class BacklogItem {
  constructor({
    id,
    title,
    type,
    description,
    value,
    urgency,
    riskReduction,
    effort,
    acceptanceCriteria = [],
    dependencies = [],
    status = Status.PROPOSED,
    debtPrincipal = 0,
    debtInterestPerSprint = 0
  }) {
    this.id = String(id ?? "").trim().toUpperCase();
    this.title = String(title ?? "").trim();
    this.type = type;
    this.description = String(description ?? "").trim();
    this.value = value;
    this.urgency = urgency;
    this.riskReduction = riskReduction;
    this.effort = effort;
    this.acceptanceCriteria = [...acceptanceCriteria];
    this.dependencies = new Set(dependencies.map(id => String(id).toUpperCase()));
    this.status = status;
    this.debtPrincipal = debtPrincipal;
    this.debtInterestPerSprint = debtInterestPerSprint;
    this.version = 1;

    if (!this.id || !this.title || !this.description) {
      throw new BacklogError("An ID, title, and description are required.");
    }
    for (const [field, score] of Object.entries({
      value, urgency, riskReduction
    })) {
      if (!Number.isInteger(score) || score < 1 || score > 10) {
        throw new BacklogError(`${field} must be an integer from 1 to 10.`);
      }
    }
    if (!Number.isInteger(effort) || effort < 1 || effort > 100) {
      throw new BacklogError("Effort must be an integer from 1 to 100.");
    }
    if (debtPrincipal < 0 || debtInterestPerSprint < 0) {
      throw new BacklogError("Debt estimates cannot be negative.");
    }
  }
}

class ProductBacklog extends EventEmitter {
  #items = new Map();

  constructor({ name, capacity, clock = () => new Date().toISOString() }) {
    super();
    if (!name || !Number.isInteger(capacity) || capacity < 1) {
      throw new BacklogError("A name and positive integer capacity are required.");
    }
    this.name = name;
    this.capacity = capacity;
    this.clock = clock;
    this.audit = [];
  }

  get items() {
    // Expose a snapshot so external callers cannot mutate the internal Map.
    return new Map(this.#items);
  }

  get(id) {
    const item = this.#items.get(String(id).toUpperCase());
    if (!item) throw new BacklogError(`Unknown backlog item: ${id}`);
    return item;
  }

  #record(event, item, details = {}) {
    const record = Object.freeze({
      eventId: randomUUID(),
      timestamp: this.clock(),
      event,
      itemId: item.id,
      itemVersion: item.version,
      details: Object.freeze({ ...details })
    });
    this.audit.push(record);
    this.emit(event, record);
  }

  add(item) {
    if (!(item instanceof BacklogItem)) {
      throw new BacklogError("Only validated BacklogItem instances can be added.");
    }
    if (this.#items.has(item.id)) {
      throw new BacklogError(`Duplicate item: ${item.id}`);
    }
    if (item.dependencies.has(item.id)) {
      throw new BacklogError("An item cannot depend on itself.");
    }
    for (const dependency of item.dependencies) {
      if (!this.#items.has(dependency)) {
        throw new BacklogError(`Dependency ${dependency} must exist first.`);
      }
    }

    this.#items.set(item.id, item);
    try {
      this.#assertAcyclic();
    } catch (error) {
      this.#items.delete(item.id);
      throw error;
    }
    this.#record("item-added", item);
  }

  #assertAcyclic() {
    const visiting = new Set();
    const visited = new Set();

    const visit = id => {
      if (visiting.has(id)) {
        throw new BacklogError(`Dependency cycle detected at ${id}.`);
      }
      if (visited.has(id)) return;

      visiting.add(id);
      for (const dependency of this.get(id).dependencies) visit(dependency);
      visiting.delete(id);
      visited.add(id);
    };

    for (const id of this.#items.keys()) visit(id);
  }

  blockers(id) {
    return [...this.get(id).dependencies].filter(
      dependency => this.get(dependency).status !== Status.DONE
    );
  }

  score(item) {
    const costOfDelay =
      item.value * 0.5 + item.urgency * 0.3 + item.riskReduction * 0.2;
    return costOfDelay / item.effort;
  }

  priorityBand(item) {
    if (
      [Type.SECURITY, Type.BUG].includes(item.type) &&
      (item.urgency >= 9 || item.riskReduction >= 9)
    ) return "critical";

    const score = this.score(item);
    if (score >= 3.5) return "high";
    if (score >= 1.8) return "medium";
    return "low";
  }

  prioritize() {
    const bandOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return [...this.#items.values()]
      .filter(item => ![Status.DONE, Status.REJECTED].includes(item.status))
      .sort((a, b) =>
        bandOrder[this.priorityBand(a)] - bandOrder[this.priorityBand(b)] ||
        this.score(b) - this.score(a) ||
        a.id.localeCompare(b.id)
      );
  }

  transition(id, nextStatus) {
    const item = this.get(id);
    const allowed = {
      [Status.PROPOSED]: [Status.REFINING, Status.REJECTED],
      [Status.REFINING]: [Status.PROPOSED, Status.READY, Status.REJECTED],
      [Status.READY]: [Status.REFINING, Status.IN_PROGRESS, Status.REJECTED],
      [Status.IN_PROGRESS]: [Status.BLOCKED, Status.DONE, Status.READY],
      [Status.BLOCKED]: [Status.IN_PROGRESS, Status.READY],
      [Status.DONE]: [],
      [Status.REJECTED]: [Status.REFINING]
    };

    if (!allowed[item.status]?.includes(nextStatus)) {
      throw new BacklogError(
        `Invalid transition ${item.status} -> ${nextStatus} for ${item.id}.`
      );
    }
    if (nextStatus === Status.READY) {
      if (item.acceptanceCriteria.length === 0) {
        throw new BacklogError("Ready items require acceptance criteria.");
      }
      if (this.blockers(id).length > 0) {
        throw new BacklogError("Dependencies must be complete before readiness.");
      }
    }
    if (nextStatus === Status.IN_PROGRESS && this.blockers(id).length > 0) {
      throw new BacklogError("An item with unfinished dependencies cannot start.");
    }
    item.status = nextStatus;
    item.version += 1;
    this.#record("status-changed", item, { nextStatus });
  }

  refine(id, patch, expectedVersion) {
    const item = this.get(id);
    // Optimistic concurrency prevents one refinement session from silently
    // overwriting another session's more recent changes.
    if (expectedVersion !== item.version) {
      throw new BacklogError(
        `Stale refinement: expected version ${expectedVersion}, actual ${item.version}.`
      );
    }
    if (![Status.PROPOSED, Status.REFINING, Status.READY].includes(item.status)) {
      throw new BacklogError("Only unstarted items may be refined.");
    }

    const previous = {
      title: item.title,
      description: item.description,
      acceptanceCriteria: item.acceptanceCriteria,
      value: item.value,
      urgency: item.urgency,
      riskReduction: item.riskReduction,
      effort: item.effort
    };

    try {
      if (patch.title !== undefined) item.title = String(patch.title).trim();
      if (patch.description !== undefined) {
        item.description = String(patch.description).trim();
      }
      if (patch.acceptanceCriteria !== undefined) {
        item.acceptanceCriteria = [...patch.acceptanceCriteria];
      }
      for (const field of ["value", "urgency", "riskReduction", "effort"]) {
        if (patch[field] !== undefined) item[field] = patch[field];
      }
      // Reconstructing validates the resulting estimates and required fields.
      new BacklogItem({
        id: item.id,
        title: item.title,
        type: item.type,
        description: item.description,
        value: item.value,
        urgency: item.urgency,
        riskReduction: item.riskReduction,
        effort: item.effort,
        acceptanceCriteria: item.acceptanceCriteria,
        dependencies: [...item.dependencies],
        status: item.status,
        debtPrincipal: item.debtPrincipal,
        debtInterestPerSprint: item.debtInterestPerSprint
      });
    } catch (error) {
      Object.assign(item, previous);
      throw error;
    }

    item.version += 1;
    this.#record("item-refined", item, { changedFields: Object.keys(patch) });
  }

  planSprint() {
    const planned = [];
    const satisfied = new Set(
      [...this.#items.values()]
        .filter(item => item.status === Status.DONE)
        .map(item => item.id)
    );
    let effortUsed = 0;

    // Greedy selection respects dependencies and capacity, but is not a
    // globally optimal schedule when dependencies and effort interact.
    while (true) {
      const next = this.prioritize().find(item =>
        item.status === Status.READY &&
        !satisfied.has(item.id) &&
        [...item.dependencies].every(id => satisfied.has(id)) &&
        effortUsed + item.effort <= this.capacity
      );
      if (!next) break;
      planned.push(next);
      satisfied.add(next.id);
      effortUsed += next.effort;
    }
    return { items: planned, effortUsed, capacity: this.capacity };
  }

  forecastDebt(sprints) {
    if (!Number.isInteger(sprints) || sprints < 0) {
      throw new BacklogError("Sprint horizon must be a non-negative integer.");
    }
    return [...this.#items.values()]
      .filter(item => item.type === Type.DEBT)
      .map(item => ({
        id: item.id,
        principal: item.debtPrincipal,
        projectedInterest: item.debtInterestPerSprint * sprints,
        forecastCost: item.debtPrincipal + item.debtInterestPerSprint * sprints
      }))
      .sort((a, b) => b.forecastCost - a.forecastCost);
  }
}

function buildBacklog() {
  const backlog = new ProductBacklog({
    name: "Payments Reliability",
    capacity: 12
  });

  backlog.on("status-changed", event => {
    console.log(
      `[audit] ${event.itemId}: status changed to ${event.details.nextStatus}`
    );
  });
  backlog.on("item-refined", event => {
    console.log(`[audit] ${event.itemId}: refinement version ${event.itemVersion}`);
  });

  const records = [
    new BacklogItem({
      id: "PAY-201", title: "Add idempotency keys", type: Type.FEATURE,
      description: "Prevent duplicate payment execution after client retries.",
      value: 10, urgency: 9, riskReduction: 10, effort: 5,
      acceptanceCriteria: [
        "Repeated keys do not execute a payment twice",
        "Key retention policy is documented and tested"
      ]
    }),
    new BacklogItem({
      id: "PAY-202", title: "Add payment audit events", type: Type.FEATURE,
      description: "Record immutable business events without sensitive payloads.",
      value: 8, urgency: 7, riskReduction: 9, effort: 4,
      dependencies: ["PAY-201"],
      acceptanceCriteria: [
        "Each successful payment produces one audit event",
        "Card secrets and authentication tokens are excluded"
      ]
    }),
    new BacklogItem({
      id: "PAY-203", title: "Reduce retry amplification", type: Type.DEBT,
      description: "Replace unbounded retry behavior with capped backoff.",
      value: 7, urgency: 8, riskReduction: 9, effort: 3,
      debtPrincipal: 18000, debtInterestPerSprint: 2200,
      acceptanceCriteria: [
        "Retry count is bounded",
        "Permanent failures are not retried"
      ]
    }),
    new BacklogItem({
      id: "PAY-204", title: "Patch authorization bypass", type: Type.SECURITY,
      description: "Enforce ownership checks on payment retrieval endpoints.",
      value: 9, urgency: 10, riskReduction: 10, effort: 2,
      acceptanceCriteria: [
        "Unauthorized cross-account reads return a denial",
        "Regression tests cover owner and non-owner requests"
      ]
    }),
    new BacklogItem({
      id: "PAY-205", title: "Instrument settlement latency", type: Type.FEATURE,
      description: "Measure settlement duration by outcome and region.",
      value: 7, urgency: 6, riskReduction: 6, effort: 4,
      dependencies: ["PAY-202"],
      acceptanceCriteria: [
        "Successful and failed settlements have separate metrics",
        "Identifiers containing customer data are not metric labels"
      ]
    })
  ];

  records.forEach(item => backlog.add(item));
  backlog.transition("PAY-201", Status.REFINING);
  backlog.transition("PAY-201", Status.READY);
  backlog.transition("PAY-202", Status.REFINING);
  backlog.transition("PAY-203", Status.REFINING);
  backlog.transition("PAY-203", Status.READY);
  backlog.transition("PAY-204", Status.REFINING);
  backlog.transition("PAY-204", Status.READY);
  backlog.transition("PAY-205", Status.REFINING);

  return backlog;
}

function main() {
  const backlog = buildBacklog();

  console.log("\nPrioritized product backlog");
  for (const item of backlog.prioritize()) {
    console.log(
      `${item.id.padEnd(9)} ${backlog.priorityBand(item).padEnd(8)} ` +
      `score=${backlog.score(item).toFixed(2)} effort=${item.effort} ` +
      `blockers=${backlog.blockers(item).join(",") || "none"}`
    );
  }

  console.log("\nDependency-aware sprint proposal");
  const plan = backlog.planSprint();
  for (const item of plan.items) {
    console.log(`${item.id}: ${item.title}`);
  }
  console.log(`Capacity used: ${plan.effortUsed}/${plan.capacity}`);

  console.log("\nTechnical debt forecast");
  console.table(backlog.forecastDebt(6));

  console.log("\nRefinement concurrency check");
  const currentVersion = backlog.get("PAY-205").version;
  backlog.refine("PAY-205", {
    acceptanceCriteria: [
      "Settlement metrics include outcome and region",
      "No customer identifiers are exposed as metric labels"
    ]
  }, currentVersion);

  try {
    backlog.refine("PAY-205", { effort: 3 }, currentVersion);
  } catch (error) {
    console.log(`Expected stale-write rejection: ${error.message}`);
  }

  console.log("\nDependency transition validation");
  try {
    backlog.transition("PAY-205", Status.READY);
  } catch (error) {
    console.log(`Expected readiness rejection: ${error.message}`);
  }

  console.log(`\nRecorded audit events: ${backlog.audit.length}`);
}

main();
