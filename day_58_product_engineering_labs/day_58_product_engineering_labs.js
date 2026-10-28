'use strict';

/*
 * Product-engineering collaboration model.
 *
 * This implementation uses an event-driven workflow so that changes to
 * requirements, estimates, architecture decisions, and readiness can be
 * observed without coupling the domain objects to a user interface.
 */

const { EventEmitter } = require('node:events');

class ValidationError extends Error {}
class StateTransitionError extends Error {}

const Priority = Object.freeze({
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
});

const WorkState = Object.freeze({
  PROPOSED: 'proposed',
  DISCOVERY: 'discovery',
  ESTIMATED: 'estimated',
  READY: 'ready',
  BLOCKED: 'blocked',
  IN_PROGRESS: 'in_progress',
  DONE: 'done'
});

const DecisionStatus = Object.freeze({
  PROPOSED: 'proposed',
  ACCEPTED: 'accepted',
  REJECTED: 'rejected'
});

const TradeOff = Object.freeze({
  SPEED: 'speed',
  COST: 'cost',
  QUALITY: 'quality',
  SECURITY: 'security',
  SCALABILITY: 'scalability',
  MAINTAINABILITY: 'maintainability'
});

function assert(condition, message) {
  if (!condition) {
    throw new ValidationError(message);
  }
}

class Estimate {
  constructor(storyPoints, engineeringDays, confidence) {
    assert(Number.isInteger(storyPoints) && storyPoints > 0,
      'Story points must be a positive integer.');
    assert(Number.isFinite(engineeringDays) && engineeringDays > 0,
      'Engineering days must be positive.');
    assert(Number.isFinite(confidence) && confidence > 0 && confidence <= 1,
      'Confidence must be in the range (0, 1].');

    this.storyPoints = storyPoints;
    this.engineeringDays = engineeringDays;
    this.confidence = confidence;
    Object.freeze(this);
  }
}

class Requirement {
  constructor({
    key,
    title,
    description,
    acceptanceCriteria,
    priority,
    dependencies = [],
    risks = []
  }) {
    assert(/^[A-Z]{2,8}-\d{1,6}$/.test(key),
      'Requirement key is invalid.');
    assert(title.trim().length > 0, 'Requirement title is required.');
    assert(description.trim().length > 0,
      'Requirement description is required.');
    assert(Array.isArray(acceptanceCriteria) &&
      acceptanceCriteria.length > 0,
      'At least one acceptance criterion is required.');
    assert(acceptanceCriteria.every(item =>
      typeof item === 'string' && item.trim().length > 0),
      'Acceptance criteria must contain text.');
    assert(Object.values(Priority).includes(priority),
      'Unknown priority.');

    this.key = key;
    this.title = title;
    this.description = description;
    this.acceptanceCriteria = [...acceptanceCriteria];
    this.priority = priority;
    this.dependencies = new Set(dependencies);
    this.risks = [...risks];
    this.estimate = null;
    this.state = WorkState.PROPOSED;
  }
}

class ArchitectureOption {
  constructor({
    name,
    description,
    deliveryDays,
    monthlyCost,
    scalability,
    maintainability,
    security,
    complexity
  }) {
    assert(name.trim().length > 0, 'Architecture name is required.');
    assert(deliveryDays > 0, 'Delivery time must be positive.');
    assert(monthlyCost >= 0, 'Monthly cost cannot be negative.');

    for (const [label, value] of Object.entries({
      scalability,
      maintainability,
      security,
      complexity
    })) {
      assert(Number.isInteger(value) && value >= 1 && value <= 5,
        `${label} must be an integer from 1 to 5.`);
    }

    this.name = name;
    this.description = description;
    this.deliveryDays = deliveryDays;
    this.monthlyCost = monthlyCost;
    this.scalability = scalability;
    this.maintainability = maintainability;
    this.security = security;
    this.complexity = complexity;
  }
}

class Decision {
  constructor(id, title, chosenOption, rationale, tradeOffs) {
    assert(id.trim().length > 0, 'Decision ID is required.');
    assert(title.trim().length > 0, 'Decision title is required.');
    assert(chosenOption.trim().length > 0,
      'Chosen architecture option is required.');
    assert(rationale.trim().length > 0, 'Decision rationale is required.');

    this.id = id;
    this.title = title;
    this.chosenOption = chosenOption;
    this.rationale = rationale;
    this.tradeOffs = [...tradeOffs];
    this.status = DecisionStatus.ACCEPTED;
  }
}

class ArchitectureEvaluator {
  constructor(weights) {
    const entries = Object.entries(weights);
    assert(entries.length > 0, 'At least one weight is required.');
    assert(entries.every(([, value]) =>
      Number.isFinite(value) && value >= 0),
    'Weights must be non-negative.');
    assert(entries.some(([, value]) => value > 0),
      'At least one weight must be positive.');

    this.weights = { ...weights };
  }

  score(option) {
    const weight = key => this.weights[key] ?? 0;

    return (
      weight(TradeOff.SPEED) * (1 / option.deliveryDays) +
      weight(TradeOff.COST) * (1 / Math.max(option.monthlyCost, 1)) +
      weight(TradeOff.SCALABILITY) * option.scalability +
      weight(TradeOff.MAINTAINABILITY) * option.maintainability +
      weight(TradeOff.SECURITY) * option.security +
      weight(TradeOff.QUALITY) * (6 - option.complexity)
    );
  }

  rank(options) {
    return [...options]
      .map(option => ({
        option,
        score: this.score(option)
      }))
      .sort((a, b) => b.score - a.score);
  }
}

class CollaborationWorkflow extends EventEmitter {
  constructor(requirement) {
    super();
    this.requirement = requirement;
    this.options = new Map();
    this.decisions = new Map();
  }

  transition(nextState) {
    const allowed = {
      [WorkState.PROPOSED]: [WorkState.DISCOVERY],
      [WorkState.DISCOVERY]: [WorkState.ESTIMATED, WorkState.BLOCKED],
      [WorkState.ESTIMATED]: [WorkState.READY, WorkState.BLOCKED],
      [WorkState.READY]: [WorkState.IN_PROGRESS, WorkState.BLOCKED],
      [WorkState.BLOCKED]: [WorkState.DISCOVERY, WorkState.READY],
      [WorkState.IN_PROGRESS]: [WorkState.DONE, WorkState.BLOCKED],
      [WorkState.DONE]: []
    };

    if (!allowed[this.requirement.state].includes(nextState)) {
      throw new StateTransitionError(
        `Cannot move from ${this.requirement.state} to ${nextState}.`
      );
    }

    if (nextState === WorkState.READY) {
      this.assertReady();
    }

    const previous = this.requirement.state;
    this.requirement.state = nextState;
    this.emit('stateChanged', {
      requirement: this.requirement.key,
      previous,
      next: nextState
    });
  }

  setEstimate(estimate) {
    this.requirement.estimate = estimate;
    if (this.requirement.state === WorkState.DISCOVERY ||
        this.requirement.state === WorkState.PROPOSED) {
      this.requirement.state = WorkState.ESTIMATED;
    }

    this.emit('estimateChanged', {
      requirement: this.requirement.key,
      estimate
    });
  }

  addOption(option) {
    if (this.options.has(option.name)) {
      throw new ValidationError(
        `Architecture option already exists: ${option.name}`
      );
    }
    this.options.set(option.name, option);
    this.emit('architectureAdded', {
      requirement: this.requirement.key,
      option: option.name
    });
  }

  addDecision(decision) {
    this.decisions.set(decision.id, decision);
    this.emit('decisionAccepted', {
      requirement: this.requirement.key,
      decision: decision.id
    });
  }

  assertReady() {
    assert(this.requirement.estimate !== null,
      'An estimate is required before readiness.');
    assert(this.requirement.estimate.confidence >= 0.6,
      'Estimate confidence is too low.');
    assert(this.options.size > 0,
      'At least one architecture option is required.');

    const accepted = [...this.decisions.values()]
      .filter(decision => decision.status === DecisionStatus.ACCEPTED);

    assert(accepted.length > 0,
      'At least one accepted architecture decision is required.');

    const blockedDependencies = [...this.requirement.dependencies]
      .filter(dependency => dependency.startsWith('BLOCKED:'));

    assert(blockedDependencies.length === 0,
      `Blocked dependencies: ${blockedDependencies.join(', ')}`);
  }
}

function buildScenario() {
  const requirement = new Requirement({
    key: 'CAT-204',
    title: 'Introduce personalized product recommendations',
    description:
      'Expose ranked recommendations using customer activity while preserving '
      + 'response-time and privacy requirements.',
    acceptanceCriteria: [
      'Recommendations are returned within the agreed latency budget.',
      'Customers without history receive a deterministic fallback.',
      'Sensitive customer attributes are excluded from ranking inputs.',
      'The recommendation service can be disabled through a feature flag.'
    ],
    priority: Priority.HIGH,
    dependencies: ['CAT-180'],
    risks: [
      'Cold-start customers require a fallback.',
      'Additional ranking computation can increase latency.'
    ]
  });

  const workflow = new CollaborationWorkflow(requirement);

  workflow.on('stateChanged', event =>
    console.log(
      `[event] state ${event.previous} -> ${event.next}`
    )
  );

  workflow.on('decisionAccepted', event =>
    console.log(`[event] decision accepted: ${event.decision}`)
  );

  workflow.transition(WorkState.DISCOVERY);

  workflow.addOption(new ArchitectureOption({
    name: 'Precomputed recommendation tables',
    description: 'Generate ranked recommendations asynchronously.',
    deliveryDays: 7,
    monthlyCost: 220,
    scalability: 5,
    maintainability: 5,
    security: 5,
    complexity: 2
  }));

  workflow.addOption(new ArchitectureOption({
    name: 'Synchronous ranking service',
    description: 'Calculate ranking during the request.',
    deliveryDays: 4,
    monthlyCost: 380,
    scalability: 4,
    maintainability: 3,
    security: 5,
    complexity: 4
  }));

  workflow.addOption(new ArchitectureOption({
    name: 'Client-side ranking',
    description: 'Send ranking inputs to the client for computation.',
    deliveryDays: 3,
    monthlyCost: 90,
    scalability: 3,
    maintainability: 2,
    security: 1,
    complexity: 4
  }));

  const evaluator = new ArchitectureEvaluator({
    [TradeOff.SPEED]: 0.15,
    [TradeOff.COST]: 0.05,
    [TradeOff.SCALABILITY]: 0.20,
    [TradeOff.MAINTAINABILITY]: 0.20,
    [TradeOff.SECURITY]: 0.30,
    [TradeOff.QUALITY]: 0.10
  });

  const ranking = evaluator.rank([...workflow.options.values()]);
  const selected = ranking[0].option;

  workflow.addDecision(new Decision(
    'ADR-021',
    'Recommendation computation strategy',
    selected.name,
    'Precomputed rankings provide stronger latency predictability, '
      + 'good scalability, and a clear privacy boundary.',
    [
      'Data may be slightly stale between refreshes.',
      'A background computation pipeline must be operated.'
    ]
  ));

  workflow.setEstimate(new Estimate(8, 7, 0.84));
  workflow.transition(WorkState.READY);

  return { workflow, ranking };
}

function runValidationChecks() {
  try {
    new Estimate(0, 2, 0.8);
    throw new Error('Invalid estimate was accepted.');
  } catch (error) {
    if (!(error instanceof ValidationError)) throw error;
  }

  const requirement = new Requirement({
    key: 'CAT-1',
    title: 'Test',
    description: 'Test requirement',
    acceptanceCriteria: ['It works'],
    priority: Priority.LOW
  });

  const workflow = new CollaborationWorkflow(requirement);

  try {
    workflow.transition(WorkState.READY);
    throw new Error('Illegal transition was accepted.');
  } catch (error) {
    if (!(error instanceof StateTransitionError)) throw error;
  }
}

function main() {
  runValidationChecks();

  const { workflow, ranking } = buildScenario();

  console.log('\nPRODUCT-ENGINEERING COLLABORATION');
  console.log('=================================');
  console.log(`Requirement: ${workflow.requirement.key}`);
  console.log(`Title: ${workflow.requirement.title}`);
  console.log(`Priority: ${workflow.requirement.priority}`);
  console.log(`State: ${workflow.requirement.state}`);

  console.log('\nArchitecture ranking:');
  ranking.forEach((entry, index) => {
    console.log(
      `${index + 1}. ${entry.option.name} | `
      + `score=${entry.score.toFixed(4)} | `
      + `delivery=${entry.option.deliveryDays}d | `
      + `monthlyCost=$${entry.option.monthlyCost}`
    );
  });

  const decisions = [...workflow.decisions.values()];
  console.log('\nAccepted decision:');
  for (const decision of decisions) {
    console.log(`${decision.id}: ${decision.chosenOption}`);
    console.log(`Rationale: ${decision.rationale}`);
  }

  console.log('\nOperational state:');
  console.log(JSON.stringify({
    requirement: workflow.requirement.key,
    state: workflow.requirement.state,
    estimate: workflow.requirement.estimate,
    architectureOptions: workflow.options.size,
    acceptedDecisions: decisions.length
  }, null, 2));
}

try {
  main();
} catch (error) {
  console.error(`Failure: ${error.message}`);
  process.exitCode = 1;
}
