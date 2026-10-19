"use strict";

/*
 * Event-driven Kanban model.
 *
 * This implementation emphasizes JavaScript's event and asynchronous behavior:
 * a work item emits events when it enters or leaves a column, while an
 * asynchronous worker simulates downstream capacity becoming available.
 */

const Column = Object.freeze({
  BACKLOG: "Backlog",
  READY: "Ready",
  DEVELOPMENT: "Development",
  REVIEW: "Review",
  TESTING: "Testing",
  DONE: "Done"
});

class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(eventName, listener) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }
    this.listeners.get(eventName).add(listener);
    return () => this.listeners.get(eventName)?.delete(listener);
  }

  emit(eventName, payload) {
    for (const listener of this.listeners.get(eventName) ?? []) {
      listener(payload);
    }
  }
}

class KanbanBoard {
  constructor({ wipLimits, bus = new EventBus() }) {
    this.wipLimits = new Map(Object.entries(wipLimits));
    this.bus = bus;
    this.items = new Map();
  }

  addItem(item) {
    if (this.items.has(item.id)) {
      throw new Error(`Duplicate item ${item.id}`);
    }

    this.items.set(item.id, {
      ...item,
      column: item.column ?? Column.BACKLOG,
      history: [
        {
          at: new Date(),
          column: item.column ?? Column.BACKLOG
        }
      ]
    });

    this.bus.emit("itemAdded", this.items.get(item.id));
  }

  count(column) {
    let count = 0;
    for (const item of this.items.values()) {
      if (item.column === column) count++;
    }
    return count;
  }

  canEnter(column) {
    const limit = this.wipLimits.get(column);
    return limit === undefined || this.count(column) < limit;
  }

  move(id, destination, reason = "pull") {
    const item = this.items.get(id);
    if (!item) {
      throw new Error(`Unknown item: ${id}`);
    }

    if (item.column === destination) {
      return false;
    }

    if (!this.canEnter(destination)) {
      this.bus.emit("blocked", {
        id,
        destination,
        reason: "wip-limit"
      });
      return false;
    }

    const previous = item.column;
    item.column = destination;
    item.history.push({
      at: new Date(),
      column: destination
    });

    if (destination === Column.DEVELOPMENT && !item.startedAt) {
      item.startedAt = new Date();
    }

    if (destination === Column.DONE) {
      item.completedAt = new Date();
    }

    this.bus.emit("moved", {
      id,
      from: previous,
      to: destination,
      reason
    });

    return true;
  }

  pullOldest(source, destination) {
    if (!this.canEnter(destination)) return null;

    const candidates = [...this.items.values()]
      .filter((item) => item.column === source)
      .sort(
        (a, b) =>
          a.priority - b.priority ||
          a.createdAt.getTime() - b.createdAt.getTime()
      );

    if (candidates.length === 0) return null;

    const selected = candidates[0];
    return this.move(selected.id, destination, "pull");
  }

  snapshot() {
    return Object.fromEntries(
      Object.values(Column).map((column) => [column, this.count(column)])
    );
  }

  agingReport(now = new Date()) {
    return [...this.items.values()]
      .filter((item) => item.column !== Column.DONE)
      .map((item) => ({
        id: item.id,
        column: item.column,
        ageHours: (now - item.createdAt) / 3_600_000
      }))
      .sort((a, b) => b.ageHours - a.ageHours);
  }
}

function cycleTimeHours(item) {
  if (!item.startedAt || !item.completedAt) return null;
  return (item.completedAt - item.startedAt) / 3_600_000;
}

function throughput(items, start, end) {
  return items.filter(
    (item) =>
      item.completedAt &&
      item.completedAt >= start &&
      item.completedAt < end
  ).length;
}

function validateWipLimit(limit) {
  if (!Number.isInteger(limit) || limit < 1) {
    throw new TypeError("A WIP limit must be a positive integer");
  }
}

function createBoard() {
  const wipLimits = {
    [Column.DEVELOPMENT]: 2,
    [Column.REVIEW]: 1,
    [Column.TESTING]: 2
  };

  for (const limit of Object.values(wipLimits)) {
    validateWipLimit(limit);
  }

  const bus = new EventBus();

  bus.on("moved", (event) => {
    console.log(
      `[FLOW] ${event.id}: ${event.from} -> ${event.to} (${event.reason})`
    );
  });

  bus.on("blocked", (event) => {
    console.log(
      `[BLOCKED] ${event.id} cannot enter ${event.destination}: WIP limit`
    );
  });

  return new KanbanBoard({ wipLimits, bus });
}

function seedBoard(board) {
  const now = new Date();

  const work = [
    ["WEB-41", "Checkout latency", 1, 5],
    ["WEB-42", "Search relevance", 2, 4],
    ["WEB-43", "Audit logging", 1, 3],
    ["WEB-44", "API documentation", 4, 2],
    ["WEB-45", "Cache metrics", 3, 1]
  ];

  for (const [id, title, priority, ageDays] of work) {
    board.addItem({
      id,
      title,
      priority,
      createdAt: new Date(
        now.getTime() - ageDays * 86_400_000
      ),
      column: Column.READY
    });
  }
}

function moveCompletedItem(board, source, destination) {
  const candidate = [...board.items.values()].find(
    (item) => item.column === source
  );

  if (!candidate) {
    return false;
  }

  return board.move(candidate.id, destination, "downstream-pull");
}

async function waitForCapacity(board, source, destination, delayMs) {
  await new Promise((resolve) => setTimeout(resolve, delayMs));

  if (board.canEnter(destination)) {
    return board.pullOldest(source, destination);
  }

  return null;
}

async function main() {
  const board = createBoard();
  seedBoard(board);

  console.log("Initial state:");
  console.table(board.snapshot());

  // The development limit is two, so only two ready items can be pulled.
  board.pullOldest(Column.READY, Column.DEVELOPMENT);
  board.pullOldest(Column.READY, Column.DEVELOPMENT);
  board.pullOldest(Column.READY, Column.DEVELOPMENT);

  console.log("Development is full:");
  console.table(board.snapshot());

  // Freeing downstream capacity creates a pull opportunity upstream.
  moveCompletedItem(
    board,
    Column.DEVELOPMENT,
    Column.REVIEW
  );

  await waitForCapacity(
    board,
    Column.READY,
    Column.DEVELOPMENT,
    50
  );

  // Review has a limit of one. The next development item cannot enter
  // Review until that downstream bottleneck is cleared.
  moveCompletedItem(
    board,
    Column.DEVELOPMENT,
    Column.REVIEW
  );

  moveCompletedItem(
    board,
    Column.REVIEW,
    Column.TESTING
  );

  moveCompletedItem(
    board,
    Column.TESTING,
    Column.DONE
  );

  await waitForCapacity(
    board,
    Column.DEVELOPMENT,
    Column.REVIEW,
    50
  );

  console.log("Current state:");
  console.table(board.snapshot());

  console.log("Aging work:");
  console.table(board.agingReport());

  const completed = [...board.items.values()].filter(
    (item) => item.column === Column.DONE
  );

  for (const item of completed) {
    console.log(
      `${item.id}: cycle time = ${cycleTimeHours(item)?.toFixed(2)} hours`
    );
  }

  const now = new Date();
  const dayStart = new Date(now.getTime() - 86_400_000);

  console.log(
    "24-hour throughput:",
    throughput(completed, dayStart, now)
  );

  console.log(
    "Little's Law estimate with WIP=4 and throughput=2/day:",
    `${(4 / 2).toFixed(2)} days cycle time`
  );
}

main().catch((error) => {
  console.error("Kanban simulation failed:", error.message);
  process.exitCode = 1;
});
