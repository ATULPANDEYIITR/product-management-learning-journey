"use strict";

/*
 * Prototype fidelity workshop.
 *
 * Node.js 18+; no third-party dependencies.
 *
 * This implementation focuses on event-driven design experiments, observable
 * UI states, task instrumentation, asynchronous interactions, and the
 * differences between schematic, structural, and realistic prototypes.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

const Fidelity = Object.freeze({
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
});

class PrototypeConfigurationError extends Error {}
class InvalidPrototypeStateError extends Error {}

class DesignPrototype extends EventEmitter {
  constructor({ id, fidelity, question, screens, interactions = [] }) {
    super();

    if (!id || !question || !Object.values(Fidelity).includes(fidelity)) {
      throw new PrototypeConfigurationError(
        "A prototype needs an ID, a design question, and a valid fidelity."
      );
    }
    if (!Array.isArray(screens) || screens.length === 0) {
      throw new PrototypeConfigurationError(
        "At least one screen definition is required."
      );
    }

    this.id = id;
    this.fidelity = fidelity;
    this.question = question;
    this.screens = new Map();
    this.interactions = new Set(interactions);
    this.state = "draft";
    this.revision = 1;

    for (const screen of screens) {
      if (!screen.id || this.screens.has(screen.id)) {
        throw new PrototypeConfigurationError(
          "Screen IDs must be present and unique."
        );
      }
      this.screens.set(screen.id, Object.freeze({ ...screen }));
    }
  }

  publish() {
    if (this.state !== "draft") {
      throw new InvalidPrototypeStateError(
        `Cannot publish from state '${this.state}'.`
      );
    }
    this.state = "testable";
    this.emit("published", { id: this.id, revision: this.revision });
  }

  revise(reason) {
    if (this.state === "retired") {
      throw new InvalidPrototypeStateError(
        "A retired prototype cannot be revised."
      );
    }
    if (typeof reason !== "string" || !reason.trim()) {
      throw new TypeError("A revision requires an evidence-based reason.");
    }
    this.revision += 1;
    this.emit("revised", {
      id: this.id,
      revision: this.revision,
      reason: reason.trim(),
    });
  }

  retire() {
    if (this.state === "retired") {
      throw new InvalidPrototypeStateError("Prototype already retired.");
    }
    this.state = "retired";
    this.emit("retired", { id: this.id });
  }

  supports(action) {
    return this.interactions.has(action);
  }

  describe() {
    return {
      id: this.id,
      fidelity: this.fidelity,
      state: this.state,
      revision: this.revision,
      screenCount: this.screens.size,
      interactions: [...this.interactions],
      question: this.question,
    };
  }
}

function createFidelitySet() {
  return [
    new DesignPrototype({
      id: "expense-paper",
      fidelity: Fidelity.LOW,
      question: "Can an employee find the expense submission path?",
      screens: [
        { id: "dashboard", elements: ["expense summary", "submit button"] },
        { id: "form", elements: ["description", "amount", "category"] },
      ],
    }),
    new DesignPrototype({
      id: "expense-clickable",
      fidelity: Fidelity.MEDIUM,
      question: "Can an employee navigate and complete the expense form?",
      screens: [
        { id: "dashboard", elements: ["navigation", "expense summary"] },
        { id: "form", elements: ["description", "amount", "category", "submit"] },
        { id: "confirmation", elements: ["submission status"] },
      ],
      interactions: ["navigate", "edit-field", "submit"],
    }),
    new DesignPrototype({
      id: "expense-realistic",
      fidelity: Fidelity.HIGH,
      question: "Does realistic feedback prevent duplicate submissions?",
      screens: [
        { id: "dashboard", elements: ["summary", "recent expenses"] },
        { id: "form", elements: ["validated fields", "loading submit button"] },
        { id: "confirmation", elements: ["receipt ID", "success message"] },
      ],
      interactions: [
        "navigate",
        "edit-field",
        "submit",
        "show-loading",
        "show-error",
        "show-receipt",
      ],
    }),
  ];
}

class ExpenseService {
  #records = [];
  #nextId = 1;

  async submit(input, latencyMs = 0) {
    if (!input || typeof input !== "object" || Array.isArray(input)) {
      throw new TypeError("Expense input must be an object.");
    }

    const description =
      typeof input.description === "string" ? input.description.trim() : "";
    const category =
      typeof input.category === "string" ? input.category.trim() : "";
    const amount = input.amount;

    if (!description) throw new Error("Description is required.");
    if (!category) throw new Error("Category is required.");
    if (typeof amount !== "number" || !Number.isFinite(amount)) {
      throw new Error("Amount must be a finite number.");
    }
    if (amount <= 0 || amount > 1_000_000) {
      throw new Error("Amount must be between 0.01 and 1,000,000.");
    }
    if (!Number.isInteger(latencyMs) || latencyMs < 0 || latencyMs > 5000) {
      throw new RangeError("Simulated latency must be 0 to 5000 milliseconds.");
    }

    // The timer simulates network delay for testing loading and duplicate-submit
    // behavior. It does not represent a real payment or accounting backend.
    if (latencyMs > 0) {
      await new Promise((resolve) => setTimeout(resolve, latencyMs));
    }

    const record = Object.freeze({
      id: this.#nextId++,
      description,
      amount: Math.round(amount * 100) / 100,
      category,
      status: "submitted",
      submittedAt: new Date().toISOString(),
    });

    this.#records.push(record);
    return record;
  }

  list() {
    return this.#records.map((record) => ({ ...record }));
  }

  total() {
    return Math.round(
      this.#records.reduce((sum, record) => sum + record.amount, 0) * 100
    ) / 100;
  }
}

class InteractivePrototype extends EventEmitter {
  constructor(service, fidelity) {
    super();
    if (!(service instanceof ExpenseService)) {
      throw new TypeError("A valid expense service is required.");
    }
    if (![Fidelity.MEDIUM, Fidelity.HIGH].includes(fidelity)) {
      throw new TypeError("Interactive mode requires medium or high fidelity.");
    }

    this.service = service;
    this.fidelity = fidelity;
    this.screen = "dashboard";
    this.pending = false;
    this.form = { description: "", amount: "", category: "" };
    this.messages = [];
  }

  navigate(screen) {
    const routes = {
      dashboard: ["form", "history"],
      form: ["dashboard"],
      history: ["dashboard"],
      confirmation: ["dashboard", "history"],
    };

    if (!routes[this.screen]?.includes(screen)) {
      return { ok: false, message: `Invalid route: ${this.screen} -> ${screen}` };
    }

    this.screen = screen;
    this.emit("screenChanged", { screen });
    return { ok: true, screen };
  }

  setField(field, value) {
    if (this.screen !== "form") {
      return { ok: false, message: "Open the form before editing fields." };
    }
    if (!Object.hasOwn(this.form, field)) {
      return { ok: false, message: `Unknown field: ${field}` };
    }
    this.form[field] = value;
    this.emit("fieldChanged", { field });
    return { ok: true };
  }

  async submit(latencyMs = 0) {
    if (this.screen !== "form") {
      return { ok: false, message: "The expense form is not open." };
    }
    if (this.pending) {
      return { ok: false, message: "Submission is already in progress." };
    }

    this.pending = true;
    this.emit("loadingChanged", { loading: true });

    try {
      const amount = Number(this.form.amount);
      if (this.form.amount === "" || !Number.isFinite(amount)) {
        throw new Error("Enter a valid numeric amount.");
      }

      const record = await this.service.submit(
        {
          description: this.form.description,
          amount,
          category: this.form.category,
        },
        latencyMs
      );

      this.screen = "confirmation";
      this.messages.push(`Expense ${record.id} submitted.`);
      this.form = { description: "", amount: "", category: "" };

      this.emit("submitted", { id: record.id, screen: this.screen });
      return { ok: true, record };
    } catch (error) {
      this.messages.push(error.message);
      this.emit("validationFailed", { message: error.message });
      return { ok: false, message: error.message };
    } finally {
      // The state reset must run for both successful and failed submissions.
      this.pending = false;
      this.emit("loadingChanged", { loading: false });
    }
  }

  viewModel() {
    return {
      fidelity: this.fidelity,
      screen: this.screen,
      pending: this.pending,
      expenses: this.service.list(),
      total: this.service.total(),
      messages: this.messages.slice(-3),
    };
  }
}

class TaskRecorder {
  constructor() {
    this.observations = [];
  }

  record({ participant, task, completed, durationMs, errors, confidence }) {
    if (!participant || !task) {
      throw new TypeError("Participant and task identifiers are required.");
    }
    if (!Number.isFinite(durationMs) || durationMs < 0) {
      throw new RangeError("Duration must be a non-negative finite number.");
    }
    if (!Number.isInteger(errors) || errors < 0) {
      throw new RangeError("Error count must be a non-negative integer.");
    }
    if (!Number.isInteger(confidence) || confidence < 1 || confidence > 5) {
      throw new RangeError("Confidence must be an integer from 1 to 5.");
    }

    this.observations.push({
      participant,
      task,
      completed: Boolean(completed),
      durationMs,
      errors,
      confidence,
    });
  }

  report() {
    if (this.observations.length === 0) {
      throw new Error("Cannot calculate metrics without observations.");
    }

    const records = this.observations;
    const completed = records.filter((item) => item.completed).length;
    const sum = (key) => records.reduce((total, item) => total + item[key], 0);

    return {
      taskAttempts: records.length,
      completionRate: completed / records.length,
      averageDurationMs: sum("durationMs") / records.length,
      errorCount: sum("errors"),
      averageConfidence: sum("confidence") / records.length,
    };
  }
}

async function main() {
  const prototypes = createFidelitySet();

  console.log("Prototype artifact comparison");
  for (const prototype of prototypes) {
    prototype.on("published", (event) => {
      console.log(`Published ${event.id}, revision ${event.revision}`);
    });
    console.log(JSON.stringify(prototype.describe(), null, 2));
  }

  const medium = prototypes.find((item) => item.fidelity === Fidelity.MEDIUM);
  medium.publish();
  medium.revise("Testers could not identify the amount field's currency.");
  console.log("Revised medium-fidelity artifact:", medium.describe());

  const service = new ExpenseService();
  const prototype = new InteractivePrototype(service, Fidelity.HIGH);
  const eventCounts = { submitted: 0, failures: 0, loadingTransitions: 0 };

  prototype.on("submitted", () => eventCounts.submitted++);
  prototype.on("validationFailed", () => eventCounts.failures++);
  prototype.on("loadingChanged", () => eventCounts.loadingTransitions++);

  prototype.navigate("form");
  prototype.setField("description", "Regional client travel");
  prototype.setField("amount", "2450.75");
  prototype.setField("category", "Travel");

  // A concurrent second submission is rejected rather than duplicating the
  // same interaction while the simulated request is still in flight.
  const firstSubmission = prototype.submit(40);
  const duplicateSubmission = await prototype.submit(0);
  assert.equal(duplicateSubmission.ok, false);

  const completedSubmission = await firstSubmission;
  assert.equal(completedSubmission.ok, true);
  assert.equal(prototype.pending, false);

  prototype.navigate("dashboard");
  prototype.navigate("form");
  prototype.setField("description", "Office supplies");
  prototype.setField("amount", "-25");
  prototype.setField("category", "Operations");
  const invalidSubmission = await prototype.submit();
  assert.equal(invalidSubmission.ok, false);
  assert.equal(prototype.pending, false);

  console.log("\nHigh-fidelity view model");
  console.log(JSON.stringify(prototype.viewModel(), null, 2));
  console.log("Event instrumentation:", eventCounts);

  const recorder = new TaskRecorder();
  recorder.record({
    participant: "employee-01",
    task: "submit-expense",
    completed: true,
    durationMs: 24000,
    errors: 0,
    confidence: 5,
  });
  recorder.record({
    participant: "employee-02",
    task: "submit-expense",
    completed: false,
    durationMs: 60000,
    errors: 3,
    confidence: 2,
  });
  recorder.record({
    participant: "employee-03",
    task: "submit-expense",
    completed: true,
    durationMs: 39000,
    errors: 1,
    confidence: 4,
  });

  console.log("\nUsability evidence");
  console.log(JSON.stringify(recorder.report(), null, 2));

  // Invariants are executable safeguards against misleading demonstrations.
  assert.equal(service.list().length, 1);
  assert.equal(service.total(), 2450.75);
  assert.equal(eventCounts.submitted, 1);
  assert.equal(eventCounts.failures, 1);
  assert.equal(eventCounts.loadingTransitions, 4);

  console.log("Prototype invariants passed.");
}

main().catch((error) => {
  console.error("Prototype experiment failed:", error.message);
  process.exitCode = 1;
});
