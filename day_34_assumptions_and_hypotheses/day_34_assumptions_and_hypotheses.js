'use strict';

/*
 * Assumptions & Hypotheses
 *
 * This Node.js program models a validation workflow in which assumptions are
 * separated into desirability, viability, feasibility, and risk. It uses
 * JavaScript-specific event-driven behavior to represent evidence collection,
 * hypothesis evaluation, and experiment completion.
 *
 * Run:
 *   node assumptions_hypotheses.js
 */

const { EventEmitter } = require('events');
const fs = require('fs/promises');
const os = require('os');
const path = require('path');

const Dimension = Object.freeze({
  DESIRABILITY: 'desirability',
  VIABILITY: 'viability',
  FEASIBILITY: 'feasibility',
  RISK: 'risk'
});

const HypothesisStatus = Object.freeze({
  UNTESTED: 'untested',
  TESTING: 'testing',
  SUPPORTED: 'supported',
  REFUTED: 'refuted',
  INCONCLUSIVE: 'inconclusive'
});

const EvidenceType = Object.freeze({
  INTERVIEW: 'interview',
  SURVEY: 'survey',
  PROTOTYPE: 'prototype',
  FINANCIAL_MODEL: 'financial_model',
  TECHNICAL_SPIKE: 'technical_spike',
  PRODUCTION_DATA: 'production_data'
});

function assertUnitInterval(value, fieldName) {
  if (!Number.isFinite(value) || value < 0 || value > 1) {
    throw new RangeError(`${fieldName} must be a finite number between 0 and 1`);
  }
}

function requireText(value, fieldName) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new TypeError(`${fieldName} must be a non-empty string`);
  }
}

class Evidence {
  constructor({
    source,
    type,
    strength,
    supports,
    observation
  }) {
    requireText(source, 'source');
    requireText(observation, 'observation');
    assertUnitInterval(strength, 'strength');

    if (!Object.values(EvidenceType).includes(type)) {
      throw new TypeError(`Unsupported evidence type: ${type}`);
    }

    this.source = source;
    this.type = type;
    this.strength = strength;
    this.supports = Boolean(supports);
    this.observation = observation;
  }
}

class Assumption {
  constructor({
    id,
    statement,
    dimension,
    confidence,
    impact,
    uncertainty,
    owner,
    rationale
  }) {
    requireText(id, 'id');
    requireText(statement, 'statement');
    requireText(owner, 'owner');
    requireText(rationale, 'rationale');

    if (!Object.values(Dimension).includes(dimension)) {
      throw new TypeError(`Unsupported dimension: ${dimension}`);
    }

    assertUnitInterval(confidence, 'confidence');
    assertUnitInterval(impact, 'impact');
    assertUnitInterval(uncertainty, 'uncertainty');

    this.id = id;
    this.statement = statement;
    this.dimension = dimension;
    this.confidence = confidence;
    this.impact = impact;
    this.uncertainty = uncertainty;
    this.owner = owner;
    this.rationale = rationale;
    this.evidence = [];
  }

  addEvidence(evidence) {
    if (!(evidence instanceof Evidence)) {
      throw new TypeError('Expected an Evidence object');
    }
    this.evidence.push(evidence);
  }

  get exposure() {
    return this.impact * this.uncertainty;
  }

  get evidenceConfidence() {
    if (this.evidence.length === 0) {
      return 0;
    }

    let signedStrength = 0;
    let totalStrength = 0;

    for (const item of this.evidence) {
      signedStrength += item.supports ? item.strength : -item.strength;
      totalStrength += item.strength;
    }

    if (totalStrength === 0) {
      return 0;
    }

    return Math.min(
      1,
      Math.max(0, (signedStrength / totalStrength + 1) / 2)
    );
  }
}

class Hypothesis {
  constructor({
    id,
    assumptionId,
    statement,
    metric,
    threshold,
    direction,
    sampleRequirement
  }) {
    requireText(id, 'id');
    requireText(assumptionId, 'assumptionId');
    requireText(statement, 'statement');
    requireText(metric, 'metric');

    if (!Number.isFinite(threshold)) {
      throw new TypeError('threshold must be finite');
    }

    if (!['at_least', 'at_most'].includes(direction)) {
      throw new TypeError('direction must be at_least or at_most');
    }

    if (!Number.isInteger(sampleRequirement) || sampleRequirement <= 0) {
      throw new RangeError('sampleRequirement must be a positive integer');
    }

    this.id = id;
    this.assumptionId = assumptionId;
    this.statement = statement;
    this.metric = metric;
    this.threshold = threshold;
    this.direction = direction;
    this.sampleRequirement = sampleRequirement;
    this.status = HypothesisStatus.UNTESTED;
    this.observedValue = null;
    this.notes = '';
  }

  evaluate(value) {
    if (!Number.isFinite(value)) {
      throw new TypeError('Observed value must be finite');
    }

    this.observedValue = value;

    const passes =
      this.direction === 'at_least'
        ? value >= this.threshold
        : value <= this.threshold;

    this.status = passes
      ? HypothesisStatus.SUPPORTED
      : HypothesisStatus.REFUTED;

    return this.status;
  }
}

class Experiment {
  constructor({
    id,
    hypothesisId,
    method,
    cost,
    durationDays,
    informationGain
  }) {
    requireText(id, 'id');
    requireText(hypothesisId, 'hypothesisId');
    requireText(method, 'method');

    if (!Number.isFinite(cost) || cost < 0) {
      throw new RangeError('cost must be non-negative');
    }

    if (!Number.isInteger(durationDays) || durationDays <= 0) {
      throw new RangeError('durationDays must be positive');
    }

    assertUnitInterval(informationGain, 'informationGain');

    this.id = id;
    this.hypothesisId = hypothesisId;
    this.method = method;
    this.cost = cost;
    this.durationDays = durationDays;
    this.informationGain = informationGain;
  }
}

class ValidationWorkflow extends EventEmitter {
  constructor() {
    super();
    this.assumptions = new Map();
    this.hypotheses = new Map();
    this.experiments = new Map();

    /*
     * EventEmitter makes state changes observable without coupling the model
     * to a particular UI, database, or HTTP framework.
     */
    this.on('evidence:added', ({ assumptionId }) => {
      console.log(`[event] evidence added to ${assumptionId}`);
    });

    this.on('hypothesis:evaluated', ({ hypothesisId, status }) => {
      console.log(`[event] ${hypothesisId} evaluated as ${status}`);
    });

    this.on('experiment:completed', ({ experimentId, hypothesisId }) => {
      console.log(
        `[event] experiment ${experimentId} completed for ${hypothesisId}`
      );
    });
  }

  addAssumption(assumption) {
    if (this.assumptions.has(assumption.id)) {
      throw new Error(`Duplicate assumption: ${assumption.id}`);
    }
    this.assumptions.set(assumption.id, assumption);
  }

  addHypothesis(hypothesis) {
    if (!this.assumptions.has(hypothesis.assumptionId)) {
      throw new Error(
        `Hypothesis references unknown assumption: ${hypothesis.assumptionId}`
      );
    }

    if (this.hypotheses.has(hypothesis.id)) {
      throw new Error(`Duplicate hypothesis: ${hypothesis.id}`);
    }

    this.hypotheses.set(hypothesis.id, hypothesis);
  }

  addExperiment(experiment) {
    if (!this.hypotheses.has(experiment.hypothesisId)) {
      throw new Error(
        `Experiment references unknown hypothesis: ${experiment.hypothesisId}`
      );
    }

    if (this.experiments.has(experiment.id)) {
      throw new Error(`Duplicate experiment: ${experiment.id}`);
    }

    this.experiments.set(experiment.id, experiment);
  }

  addEvidence(assumptionId, evidence) {
    const assumption = this.assumptions.get(assumptionId);

    if (!assumption) {
      throw new Error(`Unknown assumption: ${assumptionId}`);
    }

    assumption.addEvidence(evidence);

    this.emit('evidence:added', { assumptionId });
  }

  evaluateHypothesis(hypothesisId, observedValue) {
    const hypothesis = this.hypotheses.get(hypothesisId);

    if (!hypothesis) {
      throw new Error(`Unknown hypothesis: ${hypothesisId}`);
    }

    const status = hypothesis.evaluate(observedValue);

    this.emit('hypothesis:evaluated', {
      hypothesisId,
      status
    });

    return status;
  }

  completeExperiment(experimentId, observedValue) {
    const experiment = this.experiments.get(experimentId);

    if (!experiment) {
      throw new Error(`Unknown experiment: ${experimentId}`);
    }

    const status = this.evaluateHypothesis(
      experiment.hypothesisId,
      observedValue
    );

    this.emit('experiment:completed', {
      experimentId,
      hypothesisId: experiment.hypothesisId
    });

    return status;
  }

  rankAssumptions() {
    return [...this.assumptions.values()].sort(
      (a, b) => b.exposure - a.exposure
    );
  }

  rankExperiments() {
    return [...this.experiments.values()]
      .map((experiment) => {
        const hypothesis = this.hypotheses.get(experiment.hypothesisId);
        const assumption = this.assumptions.get(hypothesis.assumptionId);

        const informationPerCost =
          experiment.informationGain / Math.max(experiment.cost, 1);

        const priority =
          assumption.exposure *
          informationPerCost *
          (1 - assumption.evidenceConfidence);

        return {
          experiment,
          hypothesis,
          assumption,
          priority
        };
      })
      .sort((a, b) => b.priority - a.priority);
  }

  dashboardData() {
    const byDimension = Object.fromEntries(
      Object.values(Dimension).map((dimension) => [
        dimension,
        [...this.assumptions.values()].filter(
          (item) => item.dimension === dimension
        ).length
      ])
    );

    const byStatus = Object.fromEntries(
      Object.values(HypothesisStatus).map((status) => [
        status,
        [...this.hypotheses.values()].filter(
          (item) => item.status === status
        ).length
      ])
    );

    return {
      assumptions: this.assumptions.size,
      hypotheses: this.hypotheses.size,
      experiments: this.experiments.size,
      byDimension,
      byStatus
    };
  }
}

function createWorkflow() {
  const workflow = new ValidationWorkflow();

  workflow.addAssumption(
    new Assumption({
      id: 'A-DES-101',
      statement:
        'Operations managers want automated exception alerts because manual monitoring delays intervention.',
      dimension: Dimension.DESIRABILITY,
      confidence: 0.35,
      impact: 0.85,
      uncertainty: 0.80,
      owner: 'Product Research',
      rationale:
        'Problem interviews reveal monitoring friction, but priority and adoption behavior need measurement.'
    })
  );

  workflow.addAssumption(
    new Assumption({
      id: 'A-VIA-101',
      statement:
        'Customers will pay a recurring fee that exceeds the operating cost of automated monitoring.',
      dimension: Dimension.VIABILITY,
      confidence: 0.30,
      impact: 0.90,
      uncertainty: 0.85,
      owner: 'Commercial',
      rationale:
        'The economic value is plausible, but willingness to pay is not established.'
    })
  );

  workflow.addAssumption(
    new Assumption({
      id: 'A-FEA-101',
      statement:
        'The event pipeline can evaluate alerts within the required latency under peak workload.',
      dimension: Dimension.FEASIBILITY,
      confidence: 0.60,
      impact: 0.80,
      uncertainty: 0.50,
      owner: 'Engineering',
      rationale:
        'Moderate-load testing is positive, but production-shaped peak traffic remains unverified.'
    })
  );

  workflow.addAssumption(
    new Assumption({
      id: 'A-RISK-101',
      statement:
        'False-positive alerts will remain low enough that users do not disable monitoring.',
      dimension: Dimension.RISK,
      confidence: 0.25,
      impact: 0.90,
      uncertainty: 0.85,
      owner: 'Risk',
      rationale:
        'Early telemetry suggests false positives can create alert fatigue.'
    })
  );

  workflow.addHypothesis(
    new Hypothesis({
      id: 'H-DES-101',
      assumptionId: 'A-DES-101',
      statement:
        'At least 65% of qualified managers will rank exception monitoring among their top three workflow improvements.',
      metric: 'priority selection rate',
      threshold: 0.65,
      direction: 'at_least',
      sampleRequirement: 30
    })
  );

  workflow.addHypothesis(
    new Hypothesis({
      id: 'H-VIA-101',
      assumptionId: 'A-VIA-101',
      statement:
        'At least 40% of qualified prospects will accept the proposed recurring price.',
      metric: 'price acceptance rate',
      threshold: 0.40,
      direction: 'at_least',
      sampleRequirement: 15
    })
  );

  workflow.addHypothesis(
    new Hypothesis({
      id: 'H-FEA-101',
      assumptionId: 'A-FEA-101',
      statement:
        'The event processor will maintain p95 evaluation latency at or below 250 milliseconds.',
      metric: 'p95 latency',
      threshold: 250,
      direction: 'at_most',
      sampleRequirement: 10000
    })
  );

  workflow.addHypothesis(
    new Hypothesis({
      id: 'H-RISK-101',
      assumptionId: 'A-RISK-101',
      statement:
        'Fewer than 8% of active users will disable monitoring after false-positive exposure.',
      metric: 'disablement rate',
      threshold: 0.08,
      direction: 'at_most',
      sampleRequirement: 50
    })
  );

  workflow.addExperiment(
    new Experiment({
      id: 'E-DES-101',
      hypothesisId: 'H-DES-101',
      method: 'Structured interviews plus priority-ranking prototype',
      cost: 800,
      durationDays: 10,
      informationGain: 0.85
    })
  );

  workflow.addExperiment(
    new Experiment({
      id: 'E-VIA-101',
      hypothesisId: 'H-VIA-101',
      method: 'Price-sensitivity interviews with purchasing commitment questions',
      cost: 1000,
      durationDays: 14,
      informationGain: 0.90
    })
  );

  workflow.addExperiment(
    new Experiment({
      id: 'E-FEA-101',
      hypothesisId: 'H-FEA-101',
      method: 'Production-shaped load test with latency distribution capture',
      cost: 1500,
      durationDays: 5,
      informationGain: 0.95
    })
  );

  workflow.addExperiment(
    new Experiment({
      id: 'E-RISK-101',
      hypothesisId: 'H-RISK-101',
      method: 'False-positive exposure study with retention and disablement tracking',
      cost: 900,
      durationDays: 21,
      informationGain: 0.88
    })
  );

  return workflow;
}

function addEvidence(workflow) {
  workflow.addEvidence(
    'A-DES-101',
    new Evidence({
      source: 'Operations interviews',
      type: EvidenceType.INTERVIEW,
      strength: 0.70,
      supports: true,
      observation:
        'Managers repeatedly identified manual exception monitoring as a significant workflow burden.'
    })
  );

  workflow.addEvidence(
    'A-VIA-101',
    new Evidence({
      source: 'Early customer discovery',
      type: EvidenceType.INTERVIEW,
      strength: 0.60,
      supports: false,
      observation:
        'Prospects valued the capability but several rejected the proposed price.'
    })
  );

  workflow.addEvidence(
    'A-FEA-101',
    new Evidence({
      source: 'Technical spike',
      type: EvidenceType.TECHNICAL_SPIKE,
      strength: 0.75,
      supports: true,
      observation:
        'Moderate load remained within latency target.'
    })
  );

  workflow.addEvidence(
    'A-RISK-101',
    new Evidence({
      source: 'Pilot telemetry',
      type: EvidenceType.PRODUCTION_DATA,
      strength: 0.70,
      supports: false,
      observation:
        'False-positive notifications increased monitoring disablement behavior.'
    })
  );
}

async function evaluateExperiments(workflow) {
  /*
   * Promise.all models concurrent experiment completion. The underlying
   * workflow remains deterministic because each result is explicitly supplied.
   */
  const results = await Promise.all([
    Promise.resolve(workflow.completeExperiment('E-DES-101', 0.72)),
    Promise.resolve(workflow.completeExperiment('E-VIA-101', 0.27)),
    Promise.resolve(workflow.completeExperiment('E-FEA-101', 235)),
    Promise.resolve(workflow.completeExperiment('E-RISK-101', 0.11))
  ]);

  console.log('\nExperiment results:', results);
}

function printAnalysis(workflow) {
  console.log('\n=== Assumption exposure ===');

  for (const assumption of workflow.rankAssumptions()) {
    console.log(
      `${assumption.id} | ${assumption.dimension} | ` +
      `exposure=${assumption.exposure.toFixed(3)} | ` +
      `evidence=${assumption.evidenceConfidence.toFixed(3)}`
    );
  }

  console.log('\n=== Experiment priority ===');

  for (const item of workflow.rankExperiments()) {
    console.log(
      `${item.experiment.id} | priority=${item.priority.toFixed(6)} | ` +
      `${item.hypothesis.status}`
    );
    console.log(`  ${item.experiment.method}`);
  }

  console.log('\n=== Dashboard data ===');
  console.log(JSON.stringify(workflow.dashboardData(), null, 2));
}

async function persistSnapshot(workflow) {
  /*
   * Atomic replacement reduces the chance of leaving a partially written
   * snapshot if a process fails during persistence.
   */
  const directory = await fs.mkdtemp(
    path.join(os.tmpdir(), 'assumption-workflow-')
  );

  const finalPath = path.join(directory, 'snapshot.json');
  const temporaryPath = `${finalPath}.tmp`;

  const payload = {
    generatedAt: new Date().toISOString(),
    dashboard: workflow.dashboardData(),
    assumptions: [...workflow.assumptions.values()].map((item) => ({
      id: item.id,
      statement: item.statement,
      dimension: item.dimension,
      exposure: item.exposure,
      evidenceConfidence: item.evidenceConfidence
    })),
    hypotheses: [...workflow.hypotheses.values()].map((item) => ({
      id: item.id,
      assumptionId: item.assumptionId,
      status: item.status,
      observedValue: item.observedValue
    }))
  };

  await fs.writeFile(
    temporaryPath,
    JSON.stringify(payload, null, 2),
    { encoding: 'utf8', mode: 0o600 }
  );

  await fs.rename(temporaryPath, finalPath);

  console.log(`\nSnapshot persisted to ${finalPath}`);
}

async function demonstrateValidation(workflow) {
  console.log('\n=== Validation behavior ===');

  const invalidOperations = [
    () =>
      new Assumption({
        id: 'BAD',
        statement: 'Invalid confidence',
        dimension: Dimension.DESIRABILITY,
        confidence: 2,
        impact: 0.5,
        uncertainty: 0.5,
        owner: 'Test',
        rationale: 'Intentional validation test'
      }),
    () =>
      workflow.evaluateHypothesis('H-DES-101', Number.NaN),
    () =>
      new Experiment({
        id: 'BAD-E',
        hypothesisId: 'H-DES-101',
        method: 'Invalid cost example',
        cost: -10,
        durationDays: 3,
        informationGain: 0.5
      })
  ];

  for (const operation of invalidOperations) {
    try {
      operation();
    } catch (error) {
      console.log(`Rejected correctly: ${error.message}`);
    }
  }
}

async function main() {
  console.log('=== Assumptions & Hypotheses Validation Workflow ===');

  const workflow = createWorkflow();

  addEvidence(workflow);

  await evaluateExperiments(workflow);
  printAnalysis(workflow);
  await demonstrateValidation(workflow);
  await persistSnapshot(workflow);
}

main().catch((error) => {
  /*
   * A process-level failure is surfaced with a non-zero exit code so an
   * automation system can distinguish successful validation from failure.
   */
  console.error(`Fatal workflow error: ${error.message}`);
  process.exitCode = 1;
});
