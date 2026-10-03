"use strict";

/*
 * Product Opportunity Event Model
 *
 * This Node.js program models product-opportunity work as an event-driven system.
 * It deliberately separates:
 *
 *   opportunity identification -> evidence aggregation
 *   opportunity sizing         -> scenario calculation
 *   opportunity scoring        -> prioritization policy
 *
 * JavaScript-specific behavior demonstrated here includes:
 *   - classes and private fields
 *   - Map-based indexing
 *   - event-driven workflow using EventEmitter
 *   - asynchronous evidence ingestion
 *   - immutable scoring policy objects
 *   - structured validation and error handling
 *   - JSON serialization for an API-style result
 *
 * Run with:
 *   node product-opportunity.js
 */

const { EventEmitter } = require("node:events");

const OpportunityCategory = Object.freeze({
  ACQUISITION: "acquisition",
  ACTIVATION: "activation",
  RETENTION: "retention",
  MONETIZATION: "monetization",
  EFFICIENCY: "operational-efficiency",
});

function assertRange(name, value, minimum, maximum) {
  if (!Number.isFinite(value) || value < minimum || value > maximum) {
    throw new RangeError(
      `${name} must be a finite number between ${minimum} and ${maximum}`
    );
  }
}

function assertNonNegative(name, value) {
  if (!Number.isFinite(value) || value < 0) {
    throw new RangeError(`${name} must be a non-negative number`);
  }
}

class CustomerEvidence {
  constructor({
    id,
    source,
    category,
    description,
    affectedUsers,
    frequency,
    severity,
    confidence,
  }) {
    if (!id || !source || !description) {
      throw new Error("Evidence requires an id, source, and description");
    }

    if (!Object.values(OpportunityCategory).includes(category)) {
      throw new Error(`Unknown opportunity category: ${category}`);
    }

    assertNonNegative("affectedUsers", affectedUsers);
    assertNonNegative("frequency", frequency);
    assertRange("severity", severity, 0, 10);
    assertRange("confidence", confidence, 0, 1);

    this.id = id;
    this.source = source;
    this.category = category;
    this.description = description;
    this.affectedUsers = affectedUsers;
    this.frequency = frequency;
    this.severity = severity;
    this.confidence = confidence;
  }

  get evidenceStrength() {
    return this.severity * this.confidence;
  }
}

class ProductOpportunity {
  #evidence = [];

  constructor({
    id,
    title,
    category,
    segment,
    problem,
    targetPopulation,
    annualValuePerUser,
    reachableShare,
    adoptionRate,
  }) {
    this.id = id;
    this.title = title;
    this.category = category;
    this.segment = segment;
    this.problem = problem;

    this.targetPopulation = targetPopulation;
    this.annualValuePerUser = annualValuePerUser;
    this.reachableShare = reachableShare;
    this.adoptionRate = adoptionRate;

    this.tam = 0;
    this.sam = 0;
    this.expectedValue = 0;

    this.criteria = {
      customerValue: 0,
      strategicAlignment: 0,
      confidence: 0,
      effort: 0,
      timeToValue: 0,
      risk: 0,
    };

    this.score = 0;
  }

  addEvidence(evidence) {
    if (evidence.category !== this.category) {
      throw new Error(
        `Evidence ${evidence.id} belongs to ${evidence.category}, ` +
          `but opportunity ${this.id} is ${this.category}`
      );
    }

    this.#evidence.push(evidence);
  }

  get evidence() {
    // Return a copy so external code cannot mutate private state.
    return [...this.#evidence];
  }

  get evidenceStrength() {
    if (this.#evidence.length === 0) {
      return 0;
    }

    const total = this.#evidence.reduce(
      (sum, evidence) => sum + evidence.evidenceStrength,
      0
    );

    return Math.min(10, total / this.#evidence.length);
  }

  calculateSize() {
    assertNonNegative("targetPopulation", this.targetPopulation);
    assertNonNegative(
      "annualValuePerUser",
      this.annualValuePerUser
    );
    assertRange("reachableShare", this.reachableShare, 0, 1);
    assertRange("adoptionRate", this.adoptionRate, 0, 1);

    this.tam = this.targetPopulation * this.annualValuePerUser;
    this.sam = this.tam * this.reachableShare;
    this.expectedValue = this.sam * this.adoptionRate;

    return {
      tam: this.tam,
      sam: this.sam,
      expectedValue: this.expectedValue,
    };
  }

  setCriteria(criteria) {
    for (const [name, value] of Object.entries(criteria)) {
      assertRange(name, value, 0, 10);
    }

    this.criteria = { ...this.criteria, ...criteria };
  }

  calculateScore(weights) {
    const totalWeight = Object.values(weights).reduce(
      (sum, value) => sum + value,
      0
    );

    if (totalWeight <= 0) {
      throw new Error("At least one scoring weight must be positive");
    }

    const normalized = Object.fromEntries(
      Object.entries(weights).map(([key, value]) => [
        key,
        value / totalWeight,
      ])
    );

    const effectiveConfidence =
      this.criteria.confidence * 0.6 +
      this.evidenceStrength * 0.4;

    const positiveCriteria = {
      customerValue: this.criteria.customerValue,
      strategicAlignment: this.criteria.strategicAlignment,
      confidence: effectiveConfidence,
      effort: 10 - this.criteria.effort,
      timeToValue: this.criteria.timeToValue,
      risk: 10 - this.criteria.risk,
    };

    this.score = Object.entries(normalized).reduce(
      (sum, [key, weight]) =>
        sum + positiveCriteria[key] * weight,
      0
    );

    this.score = Number(this.score.toFixed(3));
    return this.score;
  }

  toJSON() {
    return {
      id: this.id,
      title: this.title,
      category: this.category,
      segment: this.segment,
      problem: this.problem,
      evidenceCount: this.#evidence.length,
      evidenceStrength: Number(this.evidenceStrength.toFixed(2)),
      sizing: {
        tam: Math.round(this.tam),
        sam: Math.round(this.sam),
        expectedValue: Math.round(this.expectedValue),
      },
      criteria: this.criteria,
      score: this.score,
    };
  }
}

class OpportunityRepository {
  constructor() {
    this.opportunities = new Map();
  }

  save(opportunity) {
    if (this.opportunities.has(opportunity.id)) {
      throw new Error(`Opportunity ${opportunity.id} already exists`);
    }

    this.opportunities.set(opportunity.id, opportunity);
    return opportunity;
  }

  get(id) {
    const opportunity = this.opportunities.get(id);

    if (!opportunity) {
      throw new Error(`Opportunity ${id} does not exist`);
    }

    return opportunity;
  }

  all() {
    return [...this.opportunities.values()];
  }
}

class OpportunityWorkflow extends EventEmitter {
  constructor(repository) {
    super();
    this.repository = repository;

    this.on("evidence:accepted", (evidence) => {
      console.log(
        `[evidence] ${evidence.id} accepted from ${evidence.source}`
      );
    });

    this.on("opportunity:sized", (opportunity) => {
      console.log(
        `[sizing] ${opportunity.id} expected value = ` +
          `$${Math.round(opportunity.expectedValue).toLocaleString()}`
      );
    });

    this.on("opportunity:scored", (opportunity) => {
      console.log(
        `[scoring] ${opportunity.id} score = ${opportunity.score.toFixed(3)}`
      );
    });
  }

  ingestEvidence(evidence) {
    this.emit("evidence:accepted", evidence);
  }

  attachEvidence(opportunityId, evidence) {
    const opportunity = this.repository.get(opportunityId);
    opportunity.addEvidence(evidence);
  }

  sizeOpportunity(opportunityId) {
    const opportunity = this.repository.get(opportunityId);
    opportunity.calculateSize();
    this.emit("opportunity:sized", opportunity);
  }

  scoreOpportunity(opportunityId, weights) {
    const opportunity = this.repository.get(opportunityId);
    opportunity.calculateScore(weights);
    this.emit("opportunity:scored", opportunity);
  }
}

function buildEvidence() {
  return [
    new CustomerEvidence({
      id: "ANA-001",
      source: "product-analytics",
      category: OpportunityCategory.ACTIVATION,
      description:
        "Many new accounts stop before completing the first meaningful workflow.",
      affectedUsers: 1800,
      frequency: 1,
      severity: 8.5,
      confidence: 0.96,
    }),
    new CustomerEvidence({
      id: "INT-002",
      source: "customer-interviews",
      category: OpportunityCategory.ACTIVATION,
      description:
        "Administrators report uncertainty about the first setup decision.",
      affectedUsers: 70,
      frequency: 1,
      severity: 8.0,
      confidence: 0.86,
    }),
    new CustomerEvidence({
      id: "SUP-003",
      source: "support",
      category: OpportunityCategory.EFFICIENCY,
      description:
        "Customers repeatedly recreate the same operational report.",
      affectedUsers: 600,
      frequency: 600,
      severity: 7.0,
      confidence: 0.91,
    }),
    new CustomerEvidence({
      id: "BIL-004",
      source: "billing-analytics",
      category: OpportunityCategory.MONETIZATION,
      description:
        "Qualified users abandon the upgrade flow after reaching plan selection.",
      affectedUsers: 900,
      frequency: 1,
      severity: 7.3,
      confidence: 0.94,
    }),
  ];
}

function createOpportunities(repository) {
  const activation = repository.save(
    new ProductOpportunity({
      id: "OPP-001",
      title: "Shorten the path to first value",
      category: OpportunityCategory.ACTIVATION,
      segment: "New business accounts",
      problem:
        "New administrators need too much guidance before reaching a meaningful outcome.",
      targetPopulation: 24000,
      annualValuePerUser: 480,
      reachableShare: 0.7,
      adoptionRate: 0.28,
    })
  );

  const efficiency = repository.save(
    new ProductOpportunity({
      id: "OPP-002",
      title: "Automate recurring operational reporting",
      category: OpportunityCategory.EFFICIENCY,
      segment: "Operations-heavy customers",
      problem:
        "Recurring reports consume manual time that could be redirected to analysis.",
      targetPopulation: 9000,
      annualValuePerUser: 850,
      reachableShare: 0.65,
      adoptionRate: 0.22,
    })
  );

  const monetization = repository.save(
    new ProductOpportunity({
      id: "OPP-003",
      title: "Clarify paid plan selection",
      category: OpportunityCategory.MONETIZATION,
      segment: "Qualified product users",
      problem:
        "Users reaching the paid-value stage cannot confidently select the right plan.",
      targetPopulation: 18000,
      annualValuePerUser: 1200,
      reachableShare: 0.75,
      adoptionRate: 0.18,
    })
  );

  return { activation, efficiency, monetization };
}

async function ingestEvidenceAsynchronously(workflow, evidence) {
  /*
   * setImmediate represents asynchronous ingestion without requiring an npm
   * dependency. In production, the same event boundary could be backed by
   * a message queue, webhook consumer, or streaming system.
   */
  await new Promise((resolve) => setImmediate(resolve));
  workflow.ingestEvidence(evidence);
}

function configureCriteria(opportunities) {
  opportunities.activation.setCriteria({
    customerValue: 9,
    strategicAlignment: 9,
    confidence: 8.5,
    effort: 5,
    timeToValue: 8,
    risk: 3,
  });

  opportunities.efficiency.setCriteria({
    customerValue: 8,
    strategicAlignment: 7,
    confidence: 8,
    effort: 6.5,
    timeToValue: 6.5,
    risk: 4,
  });

  opportunities.monetization.setCriteria({
    customerValue: 7.5,
    strategicAlignment: 8.5,
    confidence: 7.5,
    effort: 4.5,
    timeToValue: 7.5,
    risk: 4.5,
  });
}

function adoptionSensitivity(opportunity) {
  return [0.10, 0.20, 0.30, 0.40, 0.50].map((adoptionRate) => ({
    adoptionRate,
    expectedValue: opportunity.sam * adoptionRate,
  }));
}

async function main() {
  console.log("=== Product Opportunity Event Model ===");

  const repository = new OpportunityRepository();
  const workflow = new OpportunityWorkflow(repository);

  const opportunities = createOpportunities(repository);
  configureCriteria(opportunities);

  const evidence = buildEvidence();

  /*
   * Evidence ingestion is asynchronous, but attaching evidence is deliberately
   * explicit. This prevents a signal from silently becoming an opportunity:
   * product discovery still requires synthesis and definition.
   */
  for (const item of evidence) {
    await ingestEvidenceAsynchronously(workflow, item);

    const matchingOpportunity = Object.values(opportunities).find(
      (opportunity) => opportunity.category === item.category
    );

    if (matchingOpportunity) {
      workflow.attachEvidence(matchingOpportunity.id, item);
    }
  }

  const weights = Object.freeze({
    customerValue: 0.30,
    strategicAlignment: 0.20,
    confidence: 0.15,
    effort: 0.10,
    timeToValue: 0.10,
    risk: 0.15,
  });

  for (const opportunity of repository.all()) {
    workflow.sizeOpportunity(opportunity.id);
    workflow.scoreOpportunity(opportunity.id, weights);
  }

  console.log("\n=== Opportunity portfolio ===");

  for (const opportunity of repository.all()) {
    console.log(
      JSON.stringify(opportunity.toJSON(), null, 2)
    );
  }

  console.log("\n=== Adoption sensitivity ===");

  for (const opportunity of repository.all()) {
    console.log(`\n${opportunity.title}`);

    for (const scenario of adoptionSensitivity(opportunity)) {
      console.log(
        `  ${Math.round(scenario.adoptionRate * 100)}% adoption -> ` +
          `$${Math.round(scenario.expectedValue).toLocaleString()}`
      );
    }
  }

  /*
   * Sorting is presented as an analysis view, not as a claim that the highest
   * score is automatically the correct product decision. Teams still need to
   * examine evidence quality, strategic constraints, feasibility, and unknowns.
   */
  const ordered = [...repository.all()].sort(
    (a, b) => b.score - a.score
  );

  console.log("\n=== Score analysis view ===");

  for (const opportunity of ordered) {
    console.log(
      `${opportunity.id} | ${opportunity.title} | ` +
        `score=${opportunity.score.toFixed(3)} | ` +
        `expected=$${Math.round(opportunity.expectedValue).toLocaleString()}`
    );
  }

  console.log("\n=== Serialized portfolio payload ===");

  const apiPayload = {
    generatedAt: new Date().toISOString(),
    opportunities: repository.all().map((opportunity) => opportunity.toJSON()),
  };

  console.log(JSON.stringify(apiPayload, null, 2));
}

main().catch((error) => {
  console.error(`Workflow failed: ${error.message}`);
  process.exitCode = 1;
});
