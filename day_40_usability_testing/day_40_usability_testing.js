"use strict";

/*
 * Event-driven usability-testing workbench.
 *
 * Run with:
 *   node usability-testing.js
 *
 * This implementation focuses on session event processing, observer evidence,
 * asynchronous session execution, instrumented task transitions, and iterative
 * interface evaluation. It uses Node.js built-in modules only.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");
const { randomUUID } = require("node:crypto");

const Outcome = Object.freeze({
  SUCCESS: "success",
  PARTIAL: "partial",
  FAILURE: "failure",
  ABANDONED: "abandoned",
});

const Severity = Object.freeze({
  COSMETIC: 1,
  MINOR: 2,
  MAJOR: 3,
  CRITICAL: 4,
});

const ALLOWED_OUTCOMES = new Set(Object.values(Outcome));

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
  }
}

function requireNonEmptyString(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new ValidationError(`${label} must be a non-empty string.`);
  }
}

function requireFiniteNonNegative(value, label) {
  if (!Number.isFinite(value) || value < 0) {
    throw new ValidationError(`${label} must be a finite non-negative number.`);
  }
}

function deepFreeze(value) {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) {
      deepFreeze(child);
    }
  }
  return value;
}

class TaskDefinition {
  constructor({
    id,
    scenario,
    successCriteria,
    timeLimitSeconds,
    expectedOutcome,
  }) {
    requireNonEmptyString(id, "Task ID");
    requireNonEmptyString(scenario, "Scenario");
    requireNonEmptyString(expectedOutcome, "Expected outcome");

    if (!Array.isArray(successCriteria) || successCriteria.length === 0) {
      throw new ValidationError("Tasks require observable success criteria.");
    }
    if (!Number.isInteger(timeLimitSeconds) || timeLimitSeconds <= 0) {
      throw new ValidationError("Task time limit must be a positive integer.");
    }

    this.id = id;
    this.scenario = scenario;
    this.successCriteria = [...successCriteria];
    this.timeLimitSeconds = timeLimitSeconds;
    this.expectedOutcome = expectedOutcome;
    Object.freeze(this.successCriteria);
    Object.freeze(this);
  }
}

class EvidenceEvent {
  constructor({ taskId, elapsedMs, type, target, detail }) {
    requireNonEmptyString(taskId, "Event task ID");
    requireNonEmptyString(type, "Event type");
    requireNonEmptyString(target, "Event target");
    requireNonEmptyString(detail, "Event detail");
    requireFiniteNonNegative(elapsedMs, "Elapsed time");

    this.id = randomUUID();
    this.taskId = taskId;
    this.elapsedMs = elapsedMs;
    this.type = type;
    this.target = target;
    this.detail = detail;
    this.recordedAt = new Date().toISOString();
    Object.freeze(this);
  }
}

class SessionRecorder extends EventEmitter {
  #events = [];
  #lastElapsedMs = new Map();
  #closed = false;

  constructor({ participantId, task }) {
    super();
    requireNonEmptyString(participantId, "Participant ID");
    if (!(task instanceof TaskDefinition)) {
      throw new ValidationError("A session needs a valid task definition.");
    }

    this.participantId = participantId;
    this.task = task;
  }

  record(input) {
    if (this.#closed) {
      throw new Error("The session has already been finalized.");
    }

    const event = new EvidenceEvent({
      ...input,
      taskId: this.task.id,
    });

    const previous = this.#lastElapsedMs.get(event.taskId) ?? -1;
    if (event.elapsedMs < previous) {
      throw new ValidationError("Observation timestamps must be non-decreasing.");
    }

    this.#lastElapsedMs.set(event.taskId, event.elapsedMs);
    this.#events.push(event);

    // Observers receive immutable events. They cannot modify the stored record.
    this.emit("observation", event);
    return event;
  }

  close() {
    if (this.#closed) {
      throw new Error("The session is already closed.");
    }
    this.#closed = true;
    this.emit("sessionClosed", this.#events.length);
    return Object.freeze([...this.#events]);
  }
}

class TaskEvaluator {
  static evaluate({ task, events, outcome, durationSeconds, confidence }) {
    if (!(task instanceof TaskDefinition)) {
      throw new ValidationError("Evaluation requires a valid task.");
    }
    if (!ALLOWED_OUTCOMES.has(outcome)) {
      throw new ValidationError(`Unknown task outcome: ${outcome}`);
    }
    requireFiniteNonNegative(durationSeconds, "Duration");

    if (!Number.isInteger(confidence) || confidence < 1 || confidence > 5) {
      throw new ValidationError("Confidence must be an integer from 1 to 5.");
    }

    const mistakes = events.filter((event) =>
      ["invalid_action", "wrong_selection", "validation_error"].includes(event.type)
    );

    const assistance = events.filter((event) => event.type === "assistance");

    // A time limit is a study rule. Preserve the recorded outcome while
    // reporting the overrun separately so the data remains auditable.
    return deepFreeze({
      taskId: task.id,
      outcome,
      durationSeconds,
      timeLimitExceeded: durationSeconds > task.timeLimitSeconds,
      errors: mistakes.length,
      assistanceRequests: assistance.length,
      confidence,
      eventCount: events.length,
      observedActions: events.map((event) => ({
        type: event.type,
        target: event.target,
        elapsedMs: event.elapsedMs,
      })),
    });
  }
}

class ProblemRegister {
  #problems = new Map();

  add({
    id,
    title,
    description,
    severity,
    affectedTaskIds,
    frequency,
    impact,
    evidence,
    proposedChange,
  }) {
    requireNonEmptyString(id, "Problem ID");
    requireNonEmptyString(title, "Problem title");
    requireNonEmptyString(description, "Problem description");
    requireNonEmptyString(proposedChange, "Proposed change");

    if (this.#problems.has(id)) {
      throw new ValidationError(`Duplicate problem ID: ${id}`);
    }
    if (!Object.values(Severity).includes(severity)) {
      throw new ValidationError("Unknown severity.");
    }
    if (!Array.isArray(affectedTaskIds) || affectedTaskIds.length === 0) {
      throw new ValidationError("A problem must affect at least one task.");
    }
    if (!Number.isInteger(frequency) || frequency < 0) {
      throw new ValidationError("Frequency must be a non-negative integer.");
    }
    if (!Number.isFinite(impact) || impact < 0 || impact > 1) {
      throw new ValidationError("Impact must be between zero and one.");
    }
    if (!Array.isArray(evidence) || evidence.length === 0) {
      throw new ValidationError("Problem classification requires evidence.");
    }

    const problem = {
      id,
      title,
      description,
      severity,
      affectedTaskIds: [...new Set(affectedTaskIds)],
      frequency,
      impact,
      evidence: [...evidence],
      proposedChange,
      priorityScore: severity * Math.log1p(frequency) * impact,
      status: "open",
    };

    this.#problems.set(id, deepFreeze(problem));
    return problem;
  }

  prioritize() {
    return [...this.#problems.values()].sort(
      (a, b) =>
        b.priorityScore - a.priorityScore ||
        b.severity - a.severity ||
        a.id.localeCompare(b.id)
    );
  }
}

class IterationEvaluator {
  static compare(baseline, candidate) {
    const taskIds = new Set([
      ...Object.keys(baseline),
      ...Object.keys(candidate),
    ]);

    return [...taskIds].sort().map((taskId) => {
      const before = baseline[taskId];
      const after = candidate[taskId];

      if (!before || !after) {
        return {
          taskId,
          comparable: false,
          reason: "Task metrics are missing from one version.",
        };
      }

      const successDelta = after.successRate - before.successRate;
      const durationDelta =
        before.medianDurationSeconds == null ||
        after.medianDurationSeconds == null
          ? null
          : after.medianDurationSeconds - before.medianDurationSeconds;

      return {
        taskId,
        comparable: true,
        successDelta,
        durationDelta,
        interpretation:
          successDelta > 0 && (durationDelta === null || durationDelta <= 0)
            ? "Improvement on measured dimensions"
            : successDelta < 0
              ? "Investigate possible regression"
              : "Review alongside errors, confidence, and qualitative evidence",
      };
    });
  }
}

class UsabilityWorkbench {
  #tasks = new Map();
  #participants = new Map();
  #results = [];
  #events = [];

  constructor(studyId, objective) {
    requireNonEmptyString(studyId, "Study ID");
    requireNonEmptyString(objective, "Study objective");
    this.studyId = studyId;
    this.objective = objective;
  }

  addTask(task) {
    if (!(task instanceof TaskDefinition)) {
      throw new ValidationError("Expected a TaskDefinition.");
    }
    if (this.#tasks.has(task.id)) {
      throw new ValidationError(`Duplicate task ID: ${task.id}`);
    }
    this.#tasks.set(task.id, task);
  }

  addParticipant({ id, role, consented }) {
    requireNonEmptyString(id, "Participant ID");
    requireNonEmptyString(role, "Participant role");

    if (consented !== true) {
      throw new Error("Consent must be recorded before enrollment.");
    }
    if (this.#participants.has(id)) {
      throw new ValidationError(`Duplicate participant ID: ${id}`);
    }

    this.#participants.set(id, Object.freeze({ id, role }));
  }

  async runSession({ participantId, taskId, performTask }) {
    const participant = this.#participants.get(participantId);
    const task = this.#tasks.get(taskId);

    if (!participant) throw new Error(`Unknown participant: ${participantId}`);
    if (!task) throw new Error(`Unknown task: ${taskId}`);
    if (typeof performTask !== "function") {
      throw new ValidationError("A session requires a task execution function.");
    }

    const recorder = new SessionRecorder({ participantId, task });
    recorder.on("observation", (event) => this.#events.push(event));

    const start = process.hrtime.bigint();
    let execution;
    try {
      execution = await performTask(recorder);
    } catch (error) {
      recorder.record({
        elapsedMs: Number(process.hrtime.bigint() - start) / 1e6,
        type: "execution_error",
        target: "task_runner",
        detail: error instanceof Error ? error.message : String(error),
      });
      const events = recorder.close();
      this.#results.push({
        participantId,
        ...TaskEvaluator.evaluate({
          task,
          events,
          outcome: Outcome.FAILURE,
          durationSeconds: Number(process.hrtime.bigint() - start) / 1e9,
          confidence: 1,
        }),
      });
      return this.#results[this.#results.length - 1];
    }

    const elapsedSeconds = Number(process.hrtime.bigint() - start) / 1e9;
    const events = recorder.close();
    const evaluation = TaskEvaluator.evaluate({
      task,
      events,
      outcome: execution.outcome,
      durationSeconds: execution.durationSeconds ?? elapsedSeconds,
      confidence: execution.confidence,
    });

    const result = deepFreeze({
      participantId,
      role: participant.role,
      ...evaluation,
    });

    this.#results.push(result);
    return result;
  }

  metrics() {
    return [...this.#tasks.values()].map((task) => {
      const results = this.#results.filter((result) => result.taskId === task.id);
      const successful = results.filter(
        (result) => result.outcome === Outcome.SUCCESS
      );
      const durations = successful
        .map((result) => result.durationSeconds)
        .sort((a, b) => a - b);

      let medianDurationSeconds = null;
      if (durations.length > 0) {
        const middle = Math.floor(durations.length / 2);
        medianDurationSeconds =
          durations.length % 2
            ? durations[middle]
            : (durations[middle - 1] + durations[middle]) / 2;
      }

      return {
        taskId: task.id,
        participants: results.length,
        successRate: results.length ? successful.length / results.length : 0,
        medianDurationSeconds,
        meanErrors: results.length
          ? results.reduce((sum, result) => sum + result.errors, 0) /
            results.length
          : null,
      };
    });
  }

  exportRecord() {
    return deepFreeze({
      studyId: this.studyId,
      objective: this.objective,
      exportedAt: new Date().toISOString(),
      participants: [...this.#participants.values()],
      results: [...this.#results],
      observations: [...this.#events],
      metrics: this.metrics(),
    });
  }
}

function createTasks() {
  return [
    new TaskDefinition({
      id: "supplier-search",
      scenario:
        "Find an approved electrical supplier whose approval is currently active.",
      successCriteria: [
        "Supplier selected",
        "Active approval verified",
        "Correct category verified",
      ],
      expectedOutcome: "Identify an approved supplier",
      timeLimitSeconds: 240,
    }),
    new TaskDefinition({
      id: "quotation-comparison",
      scenario:
        "Identify the lowest-priced quotation that satisfies all required specifications.",
      successCriteria: [
        "Offers compared",
        "Compliance checked",
        "Compliant offer selected",
      ],
      expectedOutcome: "Select the lowest compliant quotation",
      timeLimitSeconds: 300,
    }),
    new TaskDefinition({
      id: "request-submission",
      scenario:
        "Submit a purchase request and verify its reference number and submitted state.",
      successCriteria: [
        "Correct quantity entered",
        "Request submitted",
        "Confirmation verified",
      ],
      expectedOutcome: "Submit a valid request",
      timeLimitSeconds: 360,
    }),
  ];
}

async function demonstrate() {
  const workbench = new UsabilityWorkbench(
    "PROC-UX-2026-02",
    "Evaluate supplier discovery, quotation comparison, and request submission."
  );

  for (const task of createTasks()) workbench.addTask(task);

  workbench.addParticipant({
    id: "P-101",
    role: "Procurement officer",
    consented: true,
  });
  workbench.addParticipant({
    id: "P-102",
    role: "Purchase analyst",
    consented: true,
  });

  await workbench.runSession({
    participantId: "P-101",
    taskId: "supplier-search",
    performTask: async (recorder) => {
      recorder.record({
        elapsedMs: 5000,
        type: "click",
        target: "supplier-filter",
        detail: "Opened supplier filter panel.",
      });
      recorder.record({
        elapsedMs: 12000,
        type: "filter_applied",
        target: "approval-status",
        detail: "Selected active approval status.",
      });
      recorder.record({
        elapsedMs: 26000,
        type: "task_success",
        target: "supplier-result",
        detail: "Selected a supplier with active approval.",
      });
      return {
        outcome: Outcome.SUCCESS,
        durationSeconds: 26,
        confidence: 5,
      };
    },
  });

  await workbench.runSession({
    participantId: "P-102",
    taskId: "supplier-search",
    performTask: async (recorder) => {
      recorder.record({
        elapsedMs: 4000,
        type: "click",
        target: "supplier-search",
        detail: "Started searching by supplier name.",
      });
      recorder.record({
        elapsedMs: 17000,
        type: "wrong_selection",
        target: "pending-supplier",
        detail: "Selected a supplier whose approval was pending.",
      });
      recorder.record({
        elapsedMs: 22000,
        type: "assistance",
        target: "moderator",
        detail: "Asked how to distinguish approval states.",
      });
      recorder.record({
        elapsedMs: 43000,
        type: "task_success",
        target: "supplier-result",
        detail: "Selected an actively approved supplier after assistance.",
      });
      return {
        outcome: Outcome.SUCCESS,
        durationSeconds: 43,
        confidence: 3,
      };
    },
  });

  await workbench.runSession({
    participantId: "P-101",
    taskId: "quotation-comparison",
    performTask: async (recorder) => {
      recorder.record({
        elapsedMs: 6000,
        type: "sort",
        target: "unit-price",
        detail: "Sorted quotations by raw unit price.",
      });
      recorder.record({
        elapsedMs: 12000,
        type: "invalid_action",
        target: "lowest-price-row",
        detail: "Selected a non-compliant quotation.",
      });
      recorder.record({
        elapsedMs: 25000,
        type: "comparison",
        target: "specification-column",
        detail: "Compared technical compliance.",
      });
      return {
        outcome: Outcome.PARTIAL,
        durationSeconds: 25,
        confidence: 3,
      };
    },
  });

  const register = new ProblemRegister();
  register.add({
    id: "UX-201",
    title: "Approval labels are ambiguous",
    description:
      "Users confuse pending supplier approval with active approval.",
    severity: Severity.CRITICAL,
    affectedTaskIds: ["supplier-search"],
    frequency: 1,
    impact: 0.95,
    evidence: [
      "Observed wrong selection",
      "Participant requested clarification",
    ],
    proposedChange:
      "Use explicit text labels and a visible approval date.",
  });
  register.add({
    id: "UX-202",
    title: "Raw price sorting obscures compliance",
    description:
      "The least expensive raw offer is not always a compliant offer.",
    severity: Severity.MAJOR,
    affectedTaskIds: ["quotation-comparison"],
    frequency: 1,
    impact: 0.85,
    evidence: [
      "Observed non-compliant selection",
      "Compliance checked after sorting",
    ],
    proposedChange:
      "Display compliance beside price and label the lowest compliant offer.",
  });

  console.log("SESSION METRICS");
  console.log(JSON.stringify(workbench.metrics(), null, 2));

  console.log("\nPRIORITIZED FINDINGS");
  console.log(JSON.stringify(register.prioritize(), null, 2));

  const baseline = {
    "supplier-search": {
      successRate: 0.6,
      medianDurationSeconds: 80,
    },
    "quotation-comparison": {
      successRate: 0.5,
      medianDurationSeconds: 140,
    },
  };
  const candidate = {
    "supplier-search": {
      successRate: 0.9,
      medianDurationSeconds: 60,
    },
    "quotation-comparison": {
      successRate: 0.8,
      medianDurationSeconds: 115,
    },
  };

  console.log("\nITERATION COMPARISON");
  console.log(JSON.stringify(IterationEvaluator.compare(baseline, candidate), null, 2));

  console.log("\nAUTOMATED CHECKS");
  assert.equal(workbench.metrics()[0].participants, 2);
  assert.equal(workbench.metrics()[0].successRate, 1);
  assert.equal(register.prioritize()[0].id, "UX-201");
  assert.throws(
    () => register.add({
      id: "UX-201",
      title: "Duplicate",
      description: "Duplicate finding",
      severity: Severity.MINOR,
      affectedTaskIds: ["supplier-search"],
      frequency: 1,
      impact: 0.2,
      evidence: ["Evidence"],
      proposedChange: "Change",
    }),
    ValidationError
  );
  assert.throws(
    () => new EvidenceEvent({
      taskId: "x",
      elapsedMs: -1,
      type: "click",
      target: "button",
      detail: "Invalid time",
    }),
    ValidationError
  );
  assert.throws(
    () => TaskEvaluator.evaluate({
      task: createTasks()[0],
      events: [],
      outcome: "unknown",
      durationSeconds: 1,
      confidence: 3,
    }),
    ValidationError
  );

  console.log("All assertions passed.");
  console.log("\nMACHINE-READABLE STUDY RECORD");
  console.log(JSON.stringify(workbench.exportRecord(), null, 2));
}

demonstrate().catch((error) => {
  console.error("Usability study failed:", error);
  process.exitCode = 1;
});
