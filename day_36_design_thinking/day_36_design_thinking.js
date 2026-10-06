"use strict";

/*
 * Design Thinking workflow model.
 * This implementation uses JavaScript's event-driven model to represent
 * evidence collection, synthesis, ideation, prototyping, testing, and iteration.
 */

const DesignStage = Object.freeze({
  EMPATHIZE: "Empathize",
  DEFINE: "Define",
  IDEATE: "Ideate",
  PROTOTYPE: "Prototype",
  TEST: "Test"
});

class DesignProject {
  constructor(name) {
    this.name = name;
    this.stage = DesignStage.EMPATHIZE;
    this.users = [];
    this.observations = [];
    this.insights = [];
    this.problemStatements = [];
    this.ideas = [];
    this.prototype = null;
    this.testResults = [];
    this.events = [];
  }

  transitionTo(nextStage) {
    const order = [
      DesignStage.EMPATHIZE,
      DesignStage.DEFINE,
      DesignStage.IDEATE,
      DesignStage.PROTOTYPE,
      DesignStage.TEST
    ];

    const currentIndex = order.indexOf(this.stage);
    const nextIndex = order.indexOf(nextStage);

    if (nextIndex < 0) {
      throw new Error(`Unknown design stage: ${nextStage}`);
    }

    // Design thinking is iterative, so moving backward is allowed after evidence.
    if (nextIndex > currentIndex + 1 && this.stage !== DesignStage.TEST) {
      throw new Error(
        `Cannot skip from ${this.stage} directly to ${nextStage}.`
      );
    }

    this.stage = nextStage;
    this.events.push({
      type: "stage-transition",
      stage: nextStage,
      timestamp: new Date().toISOString()
    });
  }

  addObservation(observation) {
    if (!observation.userId || !observation.behavior || !observation.painPoint) {
      throw new Error("An observation requires userId, behavior, and painPoint.");
    }

    if (
      typeof observation.evidenceStrength !== "number" ||
      observation.evidenceStrength < 0 ||
      observation.evidenceStrength > 1
    ) {
      throw new Error("Evidence strength must be between 0 and 1.");
    }

    this.observations.push(Object.freeze({ ...observation }));
  }

  addIdea(idea) {
    const requiredFields = [
      "name",
      "description",
      "userValue",
      "feasibility",
      "desirability",
      "risk"
    ];

    for (const field of requiredFields) {
      if (!(field in idea)) {
        throw new Error(`Idea is missing field: ${field}`);
      }
    }

    this.ideas.push({
      ...idea,
      score:
        idea.userValue * 0.4 +
        idea.feasibility * 0.25 +
        idea.desirability * 0.25 -
        idea.risk * 0.1
    });
  }

  recordTest(result) {
    if (!result.participantId || !result.task) {
      throw new Error("A test requires a participant and task.");
    }

    if (result.timeSeconds <= 0 || result.errors < 0) {
      throw new Error("Test time must be positive and errors cannot be negative.");
    }

    if (result.satisfaction < 1 || result.satisfaction > 5) {
      throw new Error("Satisfaction must be between 1 and 5.");
    }

    this.testResults.push({ ...result });
  }

  emit(eventName, payload) {
    this.events.push({
      type: eventName,
      payload,
      timestamp: new Date().toISOString()
    });
  }
}

class DesignEventBus {
  constructor() {
    this.handlers = new Map();
  }

  on(eventName, handler) {
    if (!this.handlers.has(eventName)) {
      this.handlers.set(eventName, []);
    }
    this.handlers.get(eventName).push(handler);
  }

  emit(eventName, payload) {
    for (const handler of this.handlers.get(eventName) ?? []) {
      handler(payload);
    }
  }
}

function average(values) {
  if (values.length === 0) {
    throw new Error("Cannot calculate an average from an empty collection.");
  }
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function synthesizeInsights(project) {
  const grouped = new Map();

  for (const observation of project.observations) {
    if (!grouped.has(observation.painPoint)) {
      grouped.set(observation.painPoint, []);
    }
    grouped.get(observation.painPoint).push(observation);
  }

  for (const [painPoint, observations] of grouped.entries()) {
    project.insights.push({
      painPoint,
      confidence: average(
        observations.map((observation) => observation.evidenceStrength)
      ),
      evidenceCount: observations.length,
      statement:
        `Users experience "${painPoint}" repeatedly in their real workflow, ` +
        `indicating that the issue should be addressed at the experience level.`
    });
  }
}

function defineProblem(project) {
  const strongestInsight = [...project.insights].sort(
    (a, b) => b.confidence - a.confidence
  )[0];

  if (!strongestInsight) {
    throw new Error("A problem cannot be defined without synthesized evidence.");
  }

  project.problemStatements.push({
    user: "Employees processing internal requests",
    need: "A contextual workflow that exposes state, evidence, and next action",
    insight: strongestInsight.statement,
    outcome: "Reduce processing time without reducing decision quality"
  });
}

function createPrototype(project) {
  const selectedIdea = [...project.ideas].sort(
    (a, b) => b.score - a.score
  )[0];

  if (!selectedIdea) {
    throw new Error("Cannot prototype without an idea.");
  }

  project.prototype = {
    ideaName: selectedIdea.name,
    fidelity: "medium",
    screens: [
      "Request queue",
      "Request context",
      "Decision panel",
      "Blocking explanation"
    ],
    assumptions: [
      "Users can identify the next action without leaving the request view.",
      "Approvers can understand the decision context from one screen.",
      "Blocked requests explain the missing information."
    ]
  };
}

async function runUsabilitySession(project, participant, tasks) {
  /*
   * Promise-based execution models a realistic asynchronous test session.
   * The timeout is intentionally small because it represents an event boundary,
   * not the actual duration of a human task.
   */
  await new Promise((resolve) => setTimeout(resolve, 5));

  for (const task of tasks) {
    project.recordTest({
      participantId: participant.id,
      task: task.name,
      completed: task.completed,
      timeSeconds: task.timeSeconds,
      errors: task.errors,
      satisfaction: task.satisfaction,
      observation: task.observation
    });
  }

  project.emit("test-completed", {
    participantId: participant.id,
    taskCount: tasks.length
  });
}

function analyzeTests(project) {
  if (project.testResults.length === 0) {
    throw new Error("No usability results are available.");
  }

  const completionRate = average(
    project.testResults.map((result) => Number(result.completed))
  );

  const times = project.testResults
    .map((result) => result.timeSeconds)
    .sort((a, b) => a - b);

  const medianTime = times[Math.floor(times.length / 2)];

  return {
    completionRate,
    medianTime,
    averageErrors: average(project.testResults.map((r) => r.errors)),
    averageSatisfaction: average(
      project.testResults.map((r) => r.satisfaction)
    )
  };
}

async function main() {
  const project = new DesignProject(
    "Internal Request Processing Experience"
  );

  const eventBus = new DesignEventBus();

  eventBus.on("test-completed", (event) => {
    console.log(
      `Test event received for ${event.participantId}: ${event.taskCount} task(s).`
    );
  });

  project.users.push(
    {
      id: "U01",
      name: "Anika",
      role: "Operations Analyst",
      context: "Handles a high volume of internal requests."
    },
    {
      id: "U02",
      name: "Ravi",
      role: "Finance Analyst",
      context: "Approves requests while working across applications."
    },
    {
      id: "U03",
      name: "Meera",
      role: "Team Manager",
      context: "Monitors blocked work and queue health."
    }
  );

  project.addObservation({
    userId: "U01",
    behavior: "Copies queue information into a separate spreadsheet.",
    quote: "I need my own sheet to understand what is waiting.",
    painPoint: "Request state is difficult to see.",
    evidenceStrength: 0.95
  });

  project.addObservation({
    userId: "U01",
    behavior: "Switches between several applications before processing.",
    quote: "I check multiple places before I can start.",
    painPoint: "Information is fragmented.",
    evidenceStrength: 0.9
  });

  project.addObservation({
    userId: "U02",
    behavior: "Delays approval when evidence is incomplete.",
    quote: "I need enough context to make the decision.",
    painPoint: "Decision context is incomplete.",
    evidenceStrength: 0.92
  });

  project.addObservation({
    userId: "U03",
    behavior: "Contacts analysts to discover why requests are blocked.",
    quote: "The count tells me something is wrong, not why.",
    painPoint: "Metrics do not explain blockers.",
    evidenceStrength: 0.88
  });

  console.log(`Stage: ${project.stage}`);
  synthesizeInsights(project);

  project.transitionTo(DesignStage.DEFINE);
  defineProblem(project);

  project.transitionTo(DesignStage.IDEATE);

  project.addIdea({
    name: "Contextual Request Workspace",
    description:
      "A unified queue with request state, evidence, history, and next action.",
    userValue: 9,
    feasibility: 8,
    desirability: 9,
    risk: 3
  });

  project.addIdea({
    name: "Decision Summary Panel",
    description:
      "A focused approval surface exposing purpose, amount, evidence, and exceptions.",
    userValue: 8,
    feasibility: 9,
    desirability: 8,
    risk: 2
  });

  project.addIdea({
    name: "Blocker Explanation Engine",
    description:
      "A workflow view that identifies the exact condition preventing progress.",
    userValue: 8,
    feasibility: 7,
    desirability: 7,
    risk: 5
  });

  console.table(
    project.ideas.map(({ name, score }) => ({
      name,
      score: score.toFixed(2)
    }))
  );

  project.transitionTo(DesignStage.PROTOTYPE);
  createPrototype(project);

  console.log("Prototype:", project.prototype);

  project.transitionTo(DesignStage.TEST);

  await runUsabilitySession(
    project,
    project.users[0],
    [
      {
        name: "Find the next processable request",
        completed: true,
        timeSeconds: 38,
        errors: 1,
        satisfaction: 4,
        observation: "The state filter was easy to find."
      }
    ]
  );

  await runUsabilitySession(
    project,
    project.users[1],
    [
      {
        name: "Approve a request using available evidence",
        completed: true,
        timeSeconds: 46,
        errors: 0,
        satisfaction: 5,
        observation: "The decision panel supplied sufficient context."
      }
    ]
  );

  await runUsabilitySession(
    project,
    project.users[2],
    [
      {
        name: "Identify why a request is blocked",
        completed: false,
        timeSeconds: 71,
        errors: 3,
        satisfaction: 2,
        observation:
          "The blocked state was visible, but the missing field was not explicit."
      }
    ]
  );

  for (const event of project.events) {
    if (event.type === "test-completed") {
      eventBus.emit(event.type, event.payload);
    }
  }

  const metrics = analyzeTests(project);

  console.log("\nTest metrics:");
  console.table({
    completionRate: `${(metrics.completionRate * 100).toFixed(1)}%`,
    medianTimeSeconds: metrics.medianTime,
    averageErrors: metrics.averageErrors.toFixed(2),
    averageSatisfaction: metrics.averageSatisfaction.toFixed(2)
  });

  if (metrics.completionRate < 1) {
    /*
     * The failed task is evidence for another design iteration.
     * The appropriate response is not to declare the user wrong; it is to
     * modify the prototype assumption and test the revised behavior.
     */
    project.prototype.assumptions.push(
      "Blocked requests must expose the exact missing information and recovery action."
    );

    console.log(
      "\nIteration triggered: prototype must expose the blocking condition directly."
    );
  }

  console.log("\nDesign thinking workflow completed with test evidence.");
}

main().catch((error) => {
  console.error(`Design workflow failed: ${error.message}`);
  process.exitCode = 1;
});
