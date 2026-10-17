"use strict";

/*
 * Agile Fundamentals through an event-driven delivery board.
 * Run with Node.js 18 or later.
 *
 * This example emphasizes immutable event records, stakeholder feedback,
 * incremental releases, and the difference between iteration commitment
 * and verified delivery.
 */

const { randomUUID } = require("node:crypto");

const StoryState = Object.freeze({
  BACKLOG: "BACKLOG",
  READY: "READY",
  IN_PROGRESS: "IN_PROGRESS",
  REVIEW: "REVIEW",
  DONE: "DONE",
});

class AgileBoard {
  #stories = new Map();
  #events = [];
  #listeners = new Map();

  on(eventType, listener) {
    if (typeof listener !== "function") {
      throw new TypeError("A listener must be a function.");
    }
    const listeners = this.#listeners.get(eventType) ?? [];
    listeners.push(listener);
    this.#listeners.set(eventType, listeners);

    // Return an unsubscribe function to avoid unnecessary retained listeners.
    return () => {
      const current = this.#listeners.get(eventType) ?? [];
      this.#listeners.set(
        eventType,
        current.filter((candidate) => candidate !== listener),
      );
    };
  }

  #emit(eventType, payload) {
    const event = Object.freeze({
      eventId: randomUUID(),
      eventType,
      occurredAt: new Date().toISOString(),
      payload: Object.freeze({ ...payload }),
    });

    this.#events.push(event);
    for (const listener of this.#listeners.get(eventType) ?? []) {
      listener(event);
    }
    for (const listener of this.#listeners.get("*") ?? []) {
      listener(event);
    }
  }

  addStory({
    id,
    title,
    value,
    effort,
    acceptanceCriteria,
    dependencies = [],
  }) {
    if (!id || !title?.trim()) {
      throw new Error("A story requires an ID and a title.");
    }
    if (this.#stories.has(id)) {
      throw new Error(`Duplicate story ID: ${id}`);
    }
    if (!Number.isInteger(value) || value < 1) {
      throw new Error("Business value must be a positive integer.");
    }
    if (!Number.isInteger(effort) || effort < 1) {
      throw new Error("Effort must be a positive integer.");
    }
    if (!Array.isArray(acceptanceCriteria) || acceptanceCriteria.length === 0) {
      throw new Error("Acceptance criteria are mandatory.");
    }

    const story = {
      id,
      title: title.trim(),
      value,
      effort,
      acceptanceCriteria: [...acceptanceCriteria],
      dependencies: [...dependencies],
      state: StoryState.BACKLOG,
      iteration: null,
      feedback: [],
    };

    this.#stories.set(id, story);
    this.#emit("story.created", { id, title: story.title });
    return story;
  }

  getStory(id) {
    const story = this.#stories.get(id);
    if (!story) throw new Error(`Unknown story: ${id}`);

    // Do not expose mutable internal arrays to callers.
    return {
      ...story,
      acceptanceCriteria: [...story.acceptanceCriteria],
      dependencies: [...story.dependencies],
      feedback: [...story.feedback],
    };
  }

  listBacklog() {
    return [...this.#stories.values()]
      .filter((story) => story.state !== StoryState.DONE)
      .map((story) => ({
        ...this.getStory(story.id),
        priorityScore: story.value / story.effort,
      }))
      .sort((a, b) => b.priorityScore - a.priorityScore);
  }

  planIteration(iterationNumber, capacity, storyIds) {
    if (!Number.isInteger(iterationNumber) || iterationNumber < 1) {
      throw new Error("Iteration number must be positive.");
    }
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new Error("Capacity must be a positive integer.");
    }
    if (!Array.isArray(storyIds) || storyIds.length === 0) {
      throw new Error("An iteration needs at least one candidate story.");
    }
    if (new Set(storyIds).size !== storyIds.length) {
      throw new Error("A story cannot be planned twice in one iteration.");
    }

    const stories = storyIds.map((id) => this.#stories.get(id));
    if (stories.some((story) => !story)) {
      throw new Error("The iteration contains an unknown story.");
    }

    let usedCapacity = 0;
    const plannedIds = new Set(storyIds);

    for (const story of stories) {
      if (![StoryState.BACKLOG, StoryState.READY].includes(story.state)) {
        throw new Error(`${story.id} is not available for planning.`);
      }

      // Dependencies can be satisfied by earlier delivery or by this plan.
      for (const dependencyId of story.dependencies) {
        const dependency = this.#stories.get(dependencyId);
        if (!dependency) {
          throw new Error(`${story.id} has an unknown dependency.`);
        }

        const dependencyReady =
          dependency.state === StoryState.DONE ||
          plannedIds.has(dependencyId);

        if (!dependencyReady) {
          throw new Error(`${story.id} has an unsatisfied dependency.`);
        }
      }

      usedCapacity += story.effort;
    }

    if (usedCapacity > capacity) {
      throw new Error(
        `Planned effort ${usedCapacity} exceeds capacity ${capacity}.`,
      );
    }

    for (const story of stories) {
      story.state = StoryState.READY;
      story.iteration = iterationNumber;
    }

    this.#emit("iteration.planned", {
      iterationNumber,
      capacity,
      usedCapacity,
      storyIds: [...storyIds],
    });

    return {
      iterationNumber,
      capacity,
      usedCapacity,
      storyIds: [...storyIds],
    };
  }

  transition(id, nextState) {
    const story = this.#stories.get(id);
    if (!story) throw new Error(`Unknown story: ${id}`);

    const allowed = {
      [StoryState.BACKLOG]: [StoryState.READY],
      [StoryState.READY]: [StoryState.IN_PROGRESS],
      [StoryState.IN_PROGRESS]: [StoryState.REVIEW],
      [StoryState.REVIEW]: [StoryState.IN_PROGRESS, StoryState.DONE],
      [StoryState.DONE]: [],
    };

    if (!allowed[story.state]?.includes(nextState)) {
      throw new Error(
        `Invalid transition for ${id}: ${story.state} -> ${nextState}`,
      );
    }

    const previousState = story.state;
    story.state = nextState;

    this.#emit("story.transitioned", {
      id,
      previousState,
      nextState,
      iteration: story.iteration,
    });
  }

  recordFeedback(id, comment) {
    const story = this.#stories.get(id);
    if (!story) throw new Error(`Unknown story: ${id}`);
    if (typeof comment !== "string" || !comment.trim()) {
      throw new Error("Feedback must contain meaningful text.");
    }

    story.feedback.push({
      comment: comment.trim(),
      recordedAt: new Date().toISOString(),
    });
    this.#emit("feedback.recorded", { id, comment: comment.trim() });
  }

  release(iterationNumber) {
    const delivered = [...this.#stories.values()].filter(
      (story) =>
        story.iteration === iterationNumber &&
        story.state === StoryState.DONE,
    );

    const release = {
      iterationNumber,
      releasedAt: new Date().toISOString(),
      stories: delivered.map((story) => ({
        id: story.id,
        title: story.title,
        acceptanceCriteria: [...story.acceptanceCriteria],
      })),
    };

    this.#emit("increment.released", {
      iterationNumber,
      storyIds: delivered.map((story) => story.id),
    });

    return release;
  }

  get events() {
    return this.#events.map((event) => ({
      ...event,
      payload: { ...event.payload },
    }));
  }
}

function demonstrateAgileWorkflow() {
  const board = new AgileBoard();

  board.on("*", (event) => {
    console.log(`[EVENT] ${event.eventType}`, event.payload);
  });

  board.addStory({
    id: "SUP-201",
    title: "Submit a support request",
    value: 10,
    effort: 5,
    acceptanceCriteria: [
      "A valid subject and description can be submitted.",
      "Invalid requests receive a clear validation message.",
    ],
  });

  board.addStory({
    id: "SUP-202",
    title: "View submitted requests",
    value: 9,
    effort: 3,
    acceptanceCriteria: [
      "Customers can see their own requests.",
      "Each request displays its status.",
    ],
  });

  board.addStory({
    id: "SUP-203",
    title: "Search request history",
    value: 6,
    effort: 3,
    dependencies: ["SUP-202"],
    acceptanceCriteria: [
      "Search matches request subjects.",
      "No-match results are explained.",
    ],
  });

  console.log("\nPrioritized backlog:");
  for (const story of board.listBacklog()) {
    console.log(
      `${story.id}: ${story.title}, score=${story.priorityScore.toFixed(2)}`,
    );
  }

  const iteration = board.planIteration(1, 8, ["SUP-202", "SUP-203"]);
  console.log("\nIteration commitment:", iteration);

  for (const id of iteration.storyIds) {
    board.transition(id, StoryState.READY);
    board.transition(id, StoryState.IN_PROGRESS);
    board.transition(id, StoryState.REVIEW);
    board.transition(id, StoryState.DONE);
  }

  const release = board.release(1);
  console.log("\nUsable increment:", JSON.stringify(release, null, 2));

  board.recordFeedback(
    "SUP-202",
    "Customers need the last update time to understand recent activity.",
  );
  console.log("\nFeedback:", board.getStory("SUP-202").feedback);

  board.addStory({
    id: "SUP-204",
    title: "Display last update time",
    value: 8,
    effort: 2,
    dependencies: ["SUP-202"],
    acceptanceCriteria: [
      "The latest update time is visible.",
      "The timestamp uses a documented time zone.",
    ],
  });

  console.log("\nBacklog after feedback:");
  for (const story of board.listBacklog()) {
    console.log(`${story.id}: ${story.title}`);
  }

  // A failed transition demonstrates explicit workflow validation.
  try {
    board.transition("SUP-204", StoryState.DONE);
  } catch (error) {
    console.log("\nExpected workflow rejection:", error.message);
  }
}

demonstrateAgileWorkflow();
