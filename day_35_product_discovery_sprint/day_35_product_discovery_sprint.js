/**
 * Product Discovery Sprint
 * ------------------------
 * A Node.js implementation of a discovery workflow using event-driven
 * lifecycle processing.
 *
 * The JavaScript perspective emphasizes:
 * - immutable event records
 * - EventEmitter-based workflow events
 * - asynchronous research collection
 * - hypothesis and experiment state
 * - evidence-weighted opportunity prioritization
 * - validation decisions
 *
 * Run:
 *   node product-discovery-sprint.js
 */

"use strict";

const { EventEmitter } = require("node:events");
const crypto = require("node:crypto");

const SprintState = Object.freeze({
  PLANNED: "planned",
  RESEARCHING: "researching",
  SYNTHESIZING: "synthesizing",
  IDEATING: "ideating",
  VALIDATING: "validating",
  DECIDED: "decided",
});

const ExperimentDecision = Object.freeze({
  CONTINUE: "continue",
  ITERATE: "iterate",
  STOP: "stop",
});

const EvidenceType = Object.freeze({
  INTERVIEW: "interview",
  OBSERVATION: "observation",
  ANALYTICS: "analytics",
  SUPPORT: "support",
  SURVEY: "survey",
});

function createId(prefix) {
  return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
}

function assertRange(value, min, max, fieldName) {
  if (!Number.isFinite(value) || value < min || value > max) {
    throw new RangeError(`${fieldName} must be between ${min} and ${max}.`);
  }
}

function normalizeText(value, fieldName) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new TypeError(`${fieldName} must be a non-empty string.`);
  }
  return value.trim();
}

class DiscoverySprint extends EventEmitter {
  #state = SprintState.PLANNED;
  #events = [];

  constructor({ productArea, targetSegment, businessOutcome, durationDays }) {
    super();

    this.productArea = normalizeText(productArea, "productArea");
    this.targetSegment = normalizeText(targetSegment, "targetSegment");
    this.businessOutcome = normalizeText(businessOutcome, "businessOutcome");

    if (!Number.isInteger(durationDays) || durationDays < 5 || durationDays > 30) {
      throw new RangeError("Discovery sprint duration must be 5-30 days.");
    }

    this.durationDays = durationDays;
    this.researchQuestions = [];
    this.evidence = [];
    this.themes = [];
    this.opportunities = [];
    this.concepts = [];
    this.experiments = [];
  }

  get state() {
    return this.#state;
  }

  get eventHistory() {
    return [...this.#events];
  }

  transition(nextState) {
    const transitions = {
      [SprintState.PLANNED]: [SprintState.RESEARCHING],
      [SprintState.RESEARCHING]: [SprintState.SYNTHESIZING],
      [SprintState.SYNTHESIZING]: [SprintState.IDEATING],
      [SprintState.IDEATING]: [SprintState.VALIDATING],
      [SprintState.VALIDATING]: [SprintState.DECIDED],
    };

    const allowed = transitions[this.#state] || [];

    if (!allowed.includes(nextState)) {
      throw new Error(
        `Invalid sprint transition: ${this.#state} -> ${nextState}`
      );
    }

    const previous = this.#state;
    this.#state = nextState;

    const event = Object.freeze({
      id: createId("EVT"),
      type: "SPRINT_STATE_CHANGED",
      timestamp: new Date().toISOString(),
      previous,
      current: nextState,
    });

    this.#events.push(event);
    this.emit("stateChanged", event);
    return event;
  }

  addResearchQuestion(question) {
    this.researchQuestions.push(normalizeText(question, "question"));
  }

  addEvidence(record) {
    if (!Object.values(EvidenceType).includes(record.type)) {
      throw new Error(`Unsupported evidence type: ${record.type}`);
    }

    assertRange(record.severity, 0, 1, "severity");

    if (!Number.isInteger(record.frequency) || record.frequency < 1) {
      throw new RangeError("frequency must be a positive integer.");
    }

    const evidence = Object.freeze({
      id: createId("OBS"),
      sourceId: normalizeText(record.sourceId, "sourceId"),
      type: record.type,
      participantId: record.participantId ?? null,
      statement: normalizeText(record.statement, "statement"),
      severity: record.severity,
      frequency: record.frequency,
      tags: new Set(record.tags || []),
    });

    this.evidence.push(evidence);
    this.emit("evidenceAdded", evidence);
    return evidence;
  }

  calculateEvidenceSignal(evidence) {
    return evidence.severity * Math.log1p(evidence.frequency);
  }

  synthesizeTheme(name, description, tagSet, strategicFit) {
    assertRange(strategicFit, 0, 10, "strategicFit");

    const tags = new Set(tagSet);
    const supportingEvidence = this.evidence.filter((item) =>
      [...tags].some((tag) => item.tags.has(tag))
    );

    if (supportingEvidence.length === 0) {
      throw new Error(`Theme "${name}" has no supporting evidence.`);
    }

    const signal = supportingEvidence.reduce(
      (total, item) => total + this.calculateEvidenceSignal(item),
      0
    );

    const impact =
      supportingEvidence.reduce((total, item) => total + item.severity, 0) /
      supportingEvidence.length;

    const theme = Object.freeze({
      id: createId("THEME"),
      name: normalizeText(name, "theme name"),
      description: normalizeText(description, "theme description"),
      evidenceIds: supportingEvidence.map((item) => item.id),
      evidenceSignal: Number(signal.toFixed(2)),
      userImpact: Number((impact * 10).toFixed(2)),
      strategicFit,
    });

    this.themes.push(theme);
    this.emit("themeSynthesized", theme);
    return theme;
  }

  createOpportunity(themeId, statement, behavior, businessValue, feasibility) {
    const theme = this.themes.find((item) => item.id === themeId);
    if (!theme) {
      throw new Error(`Unknown theme: ${themeId}`);
    }

    assertRange(businessValue, 0, 10, "businessValue");
    assertRange(feasibility, 0, 10, "feasibility");

    const evidenceStrength = Math.min(10, theme.evidenceSignal * 1.5);

    const opportunity = Object.freeze({
      id: createId("OPP"),
      themeId,
      statement: normalizeText(statement, "statement"),
      targetBehavior: normalizeText(behavior, "behavior"),
      evidenceStrength: Number(evidenceStrength.toFixed(2)),
      businessValue,
      feasibility,
    });

    this.opportunities.push(opportunity);
    this.emit("opportunityCreated", opportunity);
    return opportunity;
  }

  createConcept(
    opportunityId,
    name,
    mechanism,
    behaviorChange,
    confidence,
    effort,
    reach
  ) {
    if (!this.opportunities.some((item) => item.id === opportunityId)) {
      throw new Error(`Unknown opportunity: ${opportunityId}`);
    }

    assertRange(confidence, 0, 1, "confidence");
    assertRange(reach, 0, 10, "reach");

    if (!Number.isFinite(effort) || effort <= 0) {
      throw new RangeError("effort must be greater than zero.");
    }

    const concept = Object.freeze({
      id: createId("CON"),
      opportunityId,
      name: normalizeText(name, "concept name"),
      mechanism: normalizeText(mechanism, "mechanism"),
      behaviorChange: normalizeText(behaviorChange, "behaviorChange"),
      confidence,
      effort,
      reach,
    });

    this.concepts.push(concept);
    this.emit("conceptCreated", concept);
    return concept;
  }

  async runExperiment(conceptId, config) {
    const concept = this.concepts.find((item) => item.id === conceptId);
    if (!concept) {
      throw new Error(`Unknown concept: ${conceptId}`);
    }

    const {
      participants,
      baseline,
      observed,
      threshold,
      qualitativeSignal,
      type,
      metric,
    } = config;

    if (!Number.isInteger(participants) || participants < 5) {
      throw new RangeError("Validation needs at least five participants in this model.");
    }

    [baseline, observed, threshold, qualitativeSignal].forEach((value, index) =>
      assertRange(
        value,
        0,
        1,
        ["baseline", "observed", "threshold", "qualitativeSignal"][index]
      )
    );

    // Promise-based execution represents an asynchronous research operation.
    // A real system could replace this delay with a research platform API,
    // telemetry query, or prototype-testing service.
    await new Promise((resolve) => setTimeout(resolve, 25));

    const quantitativePass = observed >= threshold;
    const qualitativePass = qualitativeSignal >= 0.65;

    let decision;
    if (quantitativePass && qualitativePass) {
      decision = ExperimentDecision.CONTINUE;
    } else if (quantitativePass || qualitativePass) {
      decision = ExperimentDecision.ITERATE;
    } else {
      decision = ExperimentDecision.STOP;
    }

    const experiment = Object.freeze({
      id: createId("EXP"),
      conceptId,
      type,
      participants,
      metric,
      baseline,
      observed,
      threshold,
      qualitativeSignal,
      quantitativeLift:
        baseline === 0 ? null : Number(((observed - baseline) / baseline).toFixed(4)),
      decision,
      timestamp: new Date().toISOString(),
    });

    this.experiments.push(experiment);
    this.emit("experimentCompleted", experiment);
    return experiment;
  }
}

async function collectEvidence(sprint) {
  sprint.addEvidence({
    type: EvidenceType.INTERVIEW,
    sourceId: "INT-101",
    participantId: "P-101",
    statement:
      "I compare supplier lead time, minimum order quantity, certification, and price in my own spreadsheet.",
    severity: 0.89,
    frequency: 5,
    tags: ["comparison", "manual-work", "spreadsheet"],
  });

  sprint.addEvidence({
    type: EvidenceType.OBSERVATION,
    sourceId: "OBS-201",
    participantId: "P-101",
    statement:
      "The buyer opened four supplier pages and copied values into a comparison sheet.",
    severity: 0.92,
    frequency: 4,
    tags: ["comparison", "manual-work"],
  });

  sprint.addEvidence({
    type: EvidenceType.INTERVIEW,
    sourceId: "INT-102",
    participantId: "P-102",
    statement:
      "I avoid new suppliers when the request is urgent because verifying qualification takes too long.",
    severity: 0.87,
    frequency: 4,
    tags: ["qualification", "time", "trust"],
  });

  sprint.addEvidence({
    type: EvidenceType.SUPPORT,
    sourceId: "SUP-2026-09",
    statement:
      "Users repeatedly ask support where supplier qualification evidence is stored.",
    severity: 0.73,
    frequency: 20,
    tags: ["qualification", "trust", "evidence"],
  });

  sprint.addEvidence({
    type: EvidenceType.ANALYTICS,
    sourceId: "AN-2026-Q3",
    statement:
      "Supplier detail pages receive repeat visits but relatively few sessions create a shortlist.",
    severity: 0.71,
    frequency: 1,
    tags: ["discovery", "shortlist"],
  });
}

function registerAuditLogging(sprint) {
  sprint.on("stateChanged", (event) => {
    console.log(
      `[AUDIT] state ${event.previous} -> ${event.current} at ${event.timestamp}`
    );
  });

  sprint.on("evidenceAdded", (evidence) => {
    console.log(
      `[EVIDENCE] ${evidence.type} ${evidence.id} from ${evidence.sourceId}`
    );
  });

  sprint.on("themeSynthesized", (theme) => {
    console.log(
      `[SYNTHESIS] ${theme.name} supported by ${theme.evidenceIds.length} evidence items`
    );
  });

  sprint.on("experimentCompleted", (experiment) => {
    console.log(
      `[VALIDATION] ${experiment.id} => ${experiment.decision}`
    );
  });
}

function rankConcepts(sprint) {
  return [...sprint.concepts]
    .map((concept) => ({
      ...concept,
      score:
        concept.confidence *
        concept.reach /
        Math.max(concept.effort, 1),
    }))
    .sort((a, b) => b.score - a.score);
}

function buildDiscoveryReport(sprint) {
  const themes = [...sprint.themes].sort(
    (a, b) =>
      b.userImpact + b.strategicFit -
      (a.userImpact + a.strategicFit)
  );

  const concepts = rankConcepts(sprint);

  return {
    sprint: {
      productArea: sprint.productArea,
      targetSegment: sprint.targetSegment,
      businessOutcome: sprint.businessOutcome,
      state: sprint.state,
    },
    evidence: {
      count: sprint.evidence.length,
      types: [...new Set(sprint.evidence.map((item) => item.type))],
    },
    themes: themes.map((theme) => ({
      name: theme.name,
      evidenceCount: theme.evidenceIds.length,
      userImpact: theme.userImpact,
      strategicFit: theme.strategicFit,
    })),
    concepts: concepts.map((concept) => ({
      name: concept.name,
      score: Number(concept.score.toFixed(2)),
    })),
    validation: sprint.experiments.map((experiment) => ({
      conceptId: experiment.conceptId,
      decision: experiment.decision,
      metric: experiment.metric,
      observed: experiment.observed,
    })),
  };
}

async function main() {
  const sprint = new DiscoverySprint({
    productArea: "B2B supplier discovery",
    targetSegment: "Procurement managers in manufacturing",
    businessOutcome:
      "Reduce manual effort while preserving supplier qualification confidence",
    durationDays: 10,
  });

  registerAuditLogging(sprint);

  sprint.addResearchQuestion(
    "Where does supplier discovery consume unnecessary manual effort?"
  );
  sprint.addResearchQuestion(
    "What evidence is required before a supplier can be trusted?"
  );
  sprint.addResearchQuestion(
    "Which workarounds reveal unmet workflow needs?"
  );

  sprint.transition(SprintState.RESEARCHING);
  await collectEvidence(sprint);

  sprint.transition(SprintState.SYNTHESIZING);

  const comparisonTheme = sprint.synthesizeTheme(
    "Manual comparison burden",
    "Buyers reconstruct supplier information manually to make unlike supplier pages comparable.",
    ["comparison", "manual-work", "spreadsheet"],
    8.7
  );

  const qualificationTheme = sprint.synthesizeTheme(
    "Qualification evidence gap",
    "Qualification information is fragmented enough to slow trust decisions.",
    ["qualification", "trust", "evidence"],
    9.2
  );

  sprint.transition(SprintState.IDEATING);

  const comparisonOpportunity = sprint.createOpportunity(
    comparisonTheme.id,
    "Procurement managers need comparable supplier evidence without reconstructing it manually.",
    "complete supplier comparisons using normalized evidence",
    8.9,
    7.8
  );

  const qualificationOpportunity = sprint.createOpportunity(
    qualificationTheme.id,
    "Procurement managers need qualification evidence attached to supplier decisions.",
    "verify supplier qualification before committing research time",
    9.2,
    7.0
  );

  const comparisonConcept = sprint.createConcept(
    comparisonOpportunity.id,
    "Evidence comparison workspace",
    "Normalize supplier attributes into a decision matrix and keep source evidence beside each attribute.",
    "Buyer completes a comparison task without repeatedly switching to source pages.",
    0.81,
    5,
    8.6
  );

  const qualificationConcept = sprint.createConcept(
    qualificationOpportunity.id,
    "Qualification evidence ledger",
    "Represent certification claims with source, verification date, and evidence status.",
    "Buyer verifies eligibility without searching separate documents.",
    0.77,
    6,
    8.1
  );

  sprint.transition(SprintState.VALIDATING);

  await sprint.runExperiment(comparisonConcept.id, {
    participants: 8,
    baseline: 0.45,
    observed: 0.875,
    threshold: 0.75,
    qualitativeSignal: 0.82,
    type: "usability",
    metric: "supplier comparison task completion",
  });

  await sprint.runExperiment(qualificationConcept.id, {
    participants: 8,
    baseline: 0.50,
    observed: 0.625,
    threshold: 0.75,
    qualitativeSignal: 0.71,
    type: "prototype",
    metric: "qualification verification task completion",
  });

  sprint.transition(SprintState.DECIDED);

  const report = buildDiscoveryReport(sprint);

  console.log("\n=== PRODUCT DISCOVERY REPORT ===");
  console.log(JSON.stringify(report, null, 2));

  console.log("\n=== VALIDATION INTERPRETATION ===");
  for (const experiment of sprint.experiments) {
    const interpretation =
      experiment.decision === ExperimentDecision.CONTINUE
        ? "The tested behavior has enough evidence to justify another product validation stage."
        : experiment.decision === ExperimentDecision.ITERATE
          ? "The signal is meaningful but incomplete; refine the mechanism and retest."
          : "The tested mechanism did not meet the evidence threshold.";

    console.log(`${experiment.conceptId}: ${interpretation}`);
  }

  console.log("\n=== EVENT HISTORY ===");
  for (const event of sprint.eventHistory) {
    console.log(`${event.type}: ${event.previous ?? "-"} -> ${event.current ?? "-"}`);
  }
}

main().catch((error) => {
  console.error(`Discovery sprint failed: ${error.message}`);
  process.exitCode = 1;
});
