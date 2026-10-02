/**
 * Porter's Five Forces
 *
 * A self-contained Node.js implementation covering:
 * - competitive rivalry
 * - supplier bargaining power
 * - buyer bargaining power
 * - threat of substitutes
 * - threat of new entrants
 *
 * This implementation emphasizes JavaScript-specific event-driven modeling.
 * A Five Forces assessment is represented as a stream of domain events so
 * that changes in evidence, assumptions, and scenarios can be processed
 * without rebuilding the entire application state manually.
 */

"use strict";

const Force = Object.freeze({
  RIVALRY: "Competitive Rivalry",
  SUPPLIERS: "Supplier Bargaining Power",
  BUYERS: "Buyer Bargaining Power",
  SUBSTITUTES: "Threat of Substitutes",
  ENTRANTS: "Threat of New Entrants",
});

const FORCE_ORDER = Object.freeze([
  Force.RIVALRY,
  Force.SUPPLIERS,
  Force.BUYERS,
  Force.SUBSTITUTES,
  Force.ENTRANTS,
]);

function assertScore(score, fieldName = "score") {
  if (!Number.isFinite(score) || score < 0 || score > 10) {
    throw new RangeError(`${fieldName} must be a number between 0 and 10.`);
  }
}

function pressureLevel(score) {
  assertScore(score);

  if (score < 3) return "Low";
  if (score < 5) return "Moderate-Low";
  if (score < 7) return "Moderate-High";
  return "High";
}

function average(values) {
  if (!values.length) {
    throw new Error("Cannot calculate an average from an empty collection.");
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function validateEvidence(evidence) {
  if (!evidence || typeof evidence !== "object") {
    throw new TypeError("Evidence must be an object.");
  }

  if (!evidence.statement?.trim()) {
    throw new Error("Evidence requires a statement.");
  }

  if (!evidence.source?.trim()) {
    throw new Error("Evidence requires a source.");
  }

  if (![1, 0, -1].includes(evidence.direction)) {
    throw new RangeError("Evidence direction must be -1, 0, or 1.");
  }

  if (
    !Number.isFinite(evidence.strength) ||
    evidence.strength <= 0 ||
    evidence.strength > 1
  ) {
    throw new RangeError("Evidence strength must be greater than 0 and at most 1.");
  }
}

function createAssessment(force, score, rationale, evidence = []) {
  if (!FORCE_ORDER.includes(force)) {
    throw new Error(`Unknown force: ${force}`);
  }

  assertScore(score);

  if (!rationale?.trim()) {
    throw new Error(`A rationale is required for ${force}.`);
  }

  evidence.forEach(validateEvidence);

  return {
    force,
    score,
    rationale,
    evidence: evidence.map((item) => ({ ...item })),
    pressure: pressureLevel(score),
  };
}

class FiveForcesModel {
  constructor({ industry, marketDefinition, geography, horizon, assessments }) {
    if (!industry?.trim()) {
      throw new Error("Industry is required.");
    }

    if (!marketDefinition?.trim()) {
      throw new Error("Market definition is required.");
    }

    this.industry = industry;
    this.marketDefinition = marketDefinition;
    this.geography = geography;
    this.horizon = horizon;
    this.assessments = new Map();

    for (const force of FORCE_ORDER) {
      const assessment = assessments?.[force];

      if (!assessment) {
        throw new Error(`Missing assessment for ${force}.`);
      }

      this.assessments.set(
        force,
        createAssessment(
          force,
          assessment.score,
          assessment.rationale,
          assessment.evidence
        )
      );
    }
  }

  get averagePressure() {
    return average(
      FORCE_ORDER.map((force) => this.assessments.get(force).score)
    );
  }

  get highestPressure() {
    return FORCE_ORDER
      .map((force) => this.assessments.get(force))
      .reduce((highest, current) =>
        current.score > highest.score ? current : highest
      );
  }

  get lowestPressure() {
    return FORCE_ORDER
      .map((force) => this.assessments.get(force))
      .reduce((lowest, current) =>
        current.score < lowest.score ? current : lowest
      );
  }

  updateForce(force, score, rationale) {
    const current = this.assessments.get(force);

    if (!current) {
      throw new Error(`Cannot update unknown force: ${force}`);
    }

    this.assessments.set(
      force,
      createAssessment(force, score, rationale, current.evidence)
    );
  }

  toJSON() {
    const assessments = {};

    for (const force of FORCE_ORDER) {
      assessments[force] = this.assessments.get(force);
    }

    return {
      industry: this.industry,
      marketDefinition: this.marketDefinition,
      geography: this.geography,
      horizon: this.horizon,
      assessments,
      averagePressure: this.averagePressure,
    };
  }
}

/**
 * EventEmitter is useful here because an industry-analysis system can receive
 * separate events such as new competitor entry, supplier consolidation, or
 * buyer concentration changes. Listeners can audit or recompute the model.
 */
class IndustryAnalysisBus {
  constructor() {
    this.listeners = new Map();
  }

  on(eventName, listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Event listener must be a function.");
    }

    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, []);
    }

    this.listeners.get(eventName).push(listener);
  }

  emit(eventName, payload) {
    const listeners = this.listeners.get(eventName) ?? [];

    for (const listener of listeners) {
      listener(payload);
    }
  }
}

function createCloudAccountingModel() {
  return new FiveForcesModel({
    industry: "B2B Cloud Accounting Software",
    marketDefinition:
      "Subscription accounting, invoicing, expense management, and financial reporting for small businesses",
    geography: "India",
    horizon: "2026-2030",
    assessments: {
      [Force.RIVALRY]: {
        score: 7.2,
        rationale:
          "Existing vendors compete through subscription pricing, integrations, automation, workflow design, and customer support.",
        evidence: [
          {
            statement:
              "Customers can compare several cloud accounting products.",
            source: "Market observation",
            direction: 1,
            strength: 0.9,
          },
          {
            statement:
              "Accounting workflow migration can make switching more difficult.",
            source: "Workflow analysis",
            direction: -1,
            strength: 0.7,
          },
        ],
      },

      [Force.SUPPLIERS]: {
        score: 4.5,
        rationale:
          "Cloud infrastructure and specialist integrations create dependencies, but alternative providers exist for several components.",
        evidence: [
          {
            statement:
              "Multiple cloud infrastructure providers are available.",
            source: "Supplier landscape",
            direction: -1,
            strength: 0.8,
          },
          {
            statement:
              "Specialized financial APIs may have fewer direct alternatives.",
            source: "Integration analysis",
            direction: 1,
            strength: 0.7,
          },
        ],
      },

      [Force.BUYERS]: {
        score: 6.8,
        rationale:
          "Buyers can compare prices and features, while migration of historical records can reduce switching flexibility.",
        evidence: [
          {
            statement:
              "Subscription plans make price comparisons straightforward.",
            source: "Purchasing analysis",
            direction: 1,
            strength: 0.9,
          },
          {
            statement:
              "Historical financial data creates migration effort.",
            source: "Customer workflow analysis",
            direction: -1,
            strength: 0.8,
          },
        ],
      },

      [Force.SUBSTITUTES]: {
        score: 5.7,
        rationale:
          "Spreadsheets, desktop applications, and outsourced bookkeeping can perform portions of the same customer job.",
        evidence: [
          {
            statement:
              "Very small businesses can perform basic accounting with spreadsheets.",
            source: "Alternative-solution analysis",
            direction: 1,
            strength: 0.8,
          },
          {
            statement:
              "Cloud automation integrates accounting with other business workflows.",
            source: "Capability analysis",
            direction: -1,
            strength: 0.8,
          },
        ],
      },

      [Force.ENTRANTS]: {
        score: 6.0,
        rationale:
          "Software development has relatively low physical capital requirements, but trust, distribution, integrations, and regulatory complexity create barriers.",
        evidence: [
          {
            statement:
              "Cloud products can be launched without owning physical retail infrastructure.",
            source: "Entry analysis",
            direction: 1,
            strength: 0.8,
          },
          {
            statement:
              "Established accounting relationships can make distribution difficult.",
            source: "Go-to-market analysis",
            direction: -1,
            strength: 0.8,
          },
        ],
      },
    },
  });
}

function printModel(model, title = "Five Forces Analysis") {
  console.log(`\n${"=".repeat(78)}`);
  console.log(title);
  console.log("=".repeat(78));
  console.log(`Industry: ${model.industry}`);
  console.log(`Market: ${model.marketDefinition}`);
  console.log(`Geography: ${model.geography}`);
  console.log(`Horizon: ${model.horizon}`);

  for (const force of FORCE_ORDER) {
    const assessment = model.assessments.get(force);

    console.log(`\n${force}`);
    console.log(
      `Pressure: ${assessment.score.toFixed(1)}/10 (${assessment.pressure})`
    );
    console.log(`Rationale: ${assessment.rationale}`);

    for (const evidence of assessment.evidence) {
      const direction =
        evidence.direction === 1
          ? "increases pressure"
          : evidence.direction === -1
            ? "reduces pressure"
            : "contextual";

      console.log(
        `  • ${evidence.statement} | ${evidence.source} | ${direction}`
      );
    }
  }

  console.log(
    `\nAverage modeled pressure: ${model.averagePressure.toFixed(2)}/10`
  );
  console.log(`Highest modeled pressure: ${model.highestPressure.force}`);
  console.log(`Lowest modeled pressure: ${model.lowestPressure.force}`);
}

/**
 * Scenario processing is asynchronous to represent a realistic application
 * where market signals may arrive from separate services or data feeds.
 */
function applyScenario(model, bus) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const changes = [
        {
          force: Force.RIVALRY,
          delta: 0.8,
          rationale:
            "Standardized product features make basic differentiation weaker, increasing competition around price and workflow depth.",
        },
        {
          force: Force.SUPPLIERS,
          delta: -0.5,
          rationale:
            "Improved integration standards reduce dependence on individual service providers.",
        },
        {
          force: Force.BUYERS,
          delta: 0.6,
          rationale:
            "Better comparison tools and easier migration increase buyer negotiating leverage.",
        },
        {
          force: Force.SUBSTITUTES,
          delta: 0.9,
          rationale:
            "Improved automation increases the capability of alternative bookkeeping workflows.",
        },
        {
          force: Force.ENTRANTS,
          delta: 0.5,
          rationale:
            "Development tooling reduces technical entry friction, while trust and distribution barriers remain.",
        },
      ];

      for (const change of changes) {
        const oldScore = model.assessments.get(change.force).score;
        const newScore = Math.max(0, Math.min(10, oldScore + change.delta));

        model.updateForce(change.force, newScore, change.rationale);

        bus.emit("forceChanged", {
          force: change.force,
          oldScore,
          newScore,
          delta: change.delta,
        });
      }

      resolve(model);
    }, 25);
  });
}

function sensitivityAnalysis(model) {
  const results = [];

  for (const force of FORCE_ORDER) {
    const current = model.assessments.get(force).score;
    const low = Math.max(0, current * 0.9);
    const high = Math.min(10, current * 1.1);

    const lowAverage =
      (model.averagePressure * FORCE_ORDER.length - current + low) /
      FORCE_ORDER.length;

    const highAverage =
      (model.averagePressure * FORCE_ORDER.length - current + high) /
      FORCE_ORDER.length;

    results.push({
      force,
      lowerAverage: lowAverage,
      upperAverage: highAverage,
    });
  }

  return results;
}

function demonstrateDistinctForces() {
  console.log(`\n${"=".repeat(78)}`);
  console.log("DISTINCT FORCE MECHANISMS");
  console.log("=".repeat(78));

  const mechanisms = new Map([
    [
      Force.RIVALRY,
      "Two existing vendors lower prices to defend market share.",
    ],
    [
      Force.SUPPLIERS,
      "A specialized financial-data provider raises its API charges.",
    ],
    [
      Force.BUYERS,
      "A large customer uses purchase volume to negotiate contract terms.",
    ],
    [
      Force.SUBSTITUTES,
      "A customer replaces software with outsourced bookkeeping.",
    ],
    [
      Force.ENTRANTS,
      "A new vendor enters after securing capital and distribution access.",
    ],
  ]);

  for (const [force, mechanism] of mechanisms) {
    console.log(`${force}: ${mechanism}`);
  }
}

async function main() {
  const model = createCloudAccountingModel();

  printModel(model, "BASELINE INDUSTRY STRUCTURE");

  const bus = new IndustryAnalysisBus();

  bus.on("forceChanged", (event) => {
    console.log(
      `EVENT: ${event.force} changed from ${event.oldScore.toFixed(1)} ` +
      `to ${event.newScore.toFixed(1)} (${event.delta >= 0 ? "+" : ""}${event.delta.toFixed(1)})`
    );
  });

  console.log(`\n${"=".repeat(78)}`);
  console.log("EVENT-DRIVEN SCENARIO ANALYSIS");
  console.log("=".repeat(78));

  await applyScenario(model, bus);

  printModel(model, "AFTER STRUCTURAL SCENARIO");

  console.log(`\n${"=".repeat(78)}`);
  console.log("SENSITIVITY ANALYSIS");
  console.log("=".repeat(78));

  for (const result of sensitivityAnalysis(model)) {
    console.log(
      `${result.force}: average pressure range ` +
      `${result.lowerAverage.toFixed(2)} - ${result.upperAverage.toFixed(2)}`
    );
  }

  demonstrateDistinctForces();

  console.log(`\n${"=".repeat(78)}`);
  console.log("SERIALIZED MODEL");
  console.log("=".repeat(78));

  // JSON.stringify is useful when this analysis must cross an API boundary
  // or be stored in a document-oriented data store.
  console.log(JSON.stringify(model.toJSON(), null, 2));
}

main().catch((error) => {
  console.error(`Analysis failed: ${error.message}`);
  process.exitCode = 1;
});
