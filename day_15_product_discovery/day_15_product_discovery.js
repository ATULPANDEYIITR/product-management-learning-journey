/**
 * Product Discovery
 *
 * A self-contained JavaScript study file covering:
 * - discovery fundamentals
 * - problem discovery
 * - customer discovery
 * - market discovery
 * - opportunity discovery
 * - experiments
 * - behavioral metrics
 * - prioritization
 * - evidence quality
 * - asynchronous discovery workflows
 *
 * The examples use a hypothetical product called StudyFlow.
 */

"use strict";

// ============================================================================
// 1. FUNDAMENTALS
// ============================================================================

const discoveryDefinition = {
  discovery:
    "A systematic process for reducing uncertainty about customers, problems, markets, opportunities, and possible solutions.",
  problemDiscovery:
    "Understanding the customer's undesirable situation and its consequences.",
  customerDiscovery:
    "Identifying who experiences the problem, under what circumstances, and how they behave.",
  marketDiscovery:
    "Understanding the population, segmentation, alternatives, economics, growth, and competitive conditions.",
  opportunityDiscovery:
    "Finding problem spaces that combine meaningful customer value with attractive strategic and economic potential."
};

console.log("PRODUCT DISCOVERY");
console.log(discoveryDefinition);


// ============================================================================
// 2. HYPOTHESES
// ============================================================================

class Hypothesis {
  constructor(statement, importance, confidence = 0) {
    if (!statement.trim()) {
      throw new Error("A hypothesis requires a statement.");
    }

    this.statement = statement;
    this.importance = importance;
    this.confidence = confidence;
  }

  get uncertainty() {
    return Math.max(0, 1 - this.confidence);
  }

  get risk() {
    return this.importance * this.uncertainty;
  }
}

const hypotheses = [
  new Hypothesis(
    "Working professionals struggle to maintain consistent course progress.",
    0.95,
    0.35
  ),
  new Hypothesis(
    "Customers will pay for adaptive study planning.",
    0.9,
    0.2
  ),
  new Hypothesis(
    "Existing calendars are insufficient for course planning.",
    0.6,
    0.5
  )
];

console.log("\nHypothesis risk:");
hypotheses
  .sort((a, b) => b.risk - a.risk)
  .forEach((hypothesis) => {
    console.log(
      hypothesis.risk.toFixed(2),
      hypothesis.statement
    );
  });


// ============================================================================
// 3. PROBLEM OBSERVATIONS
// ============================================================================

const observations = [
  {
    customerId: "C01",
    situation: "After work",
    behavior: "Studies inconsistently",
    consequence: "Course completion is delayed",
    frequencyPerMonth: 18,
    severity: 7,
    alternative: "Calendar reminders"
  },
  {
    customerId: "C02",
    situation: "After work",
    behavior: "Saves videos but rarely schedules study",
    consequence: "Knowledge remains incomplete",
    frequencyPerMonth: 12,
    severity: 8,
    alternative: "Notes application"
  },
  {
    customerId: "C03",
    situation: "Weekend",
    behavior: "Attempts large study sessions",
    consequence: "Feels overwhelmed",
    frequencyPerMonth: 8,
    severity: 9,
    alternative: "Spreadsheet"
  }
];

function average(values) {
  if (!Array.isArray(values) || values.length === 0) {
    return 0;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

const averageFrequency = average(
  observations.map((item) => item.frequencyPerMonth)
);

const averageSeverity = average(
  observations.map((item) => item.severity)
);

console.log("\nProblem evidence:");
console.log("Average frequency:", averageFrequency.toFixed(1));
console.log("Average severity:", averageSeverity.toFixed(1));


// ============================================================================
// 4. PROBLEM STATEMENT
// ============================================================================

function createProblemStatement(
  customer,
  situation,
  problem,
  consequence
) {
  return `${customer} in ${situation} struggle with ${problem}, resulting in ${consequence}.`;
}

const problemStatement = createProblemStatement(
  "Working professionals taking online courses",
  "an unpredictable work schedule",
  "maintaining consistent course progress",
  "incomplete courses and wasted subscriptions"
);

console.log("\nProblem statement:");
console.log(problemStatement);


// ============================================================================
// 5. CUSTOMER PROFILES
// ============================================================================

class CustomerProfile {
  constructor({
    id,
    role,
    goal,
    context,
    alternatives,
    pains,
    buyingAuthority,
    willingnessToPay
  }) {
    this.id = id;
    this.role = role;
    this.goal = goal;
    this.context = context;
    this.alternatives = alternatives;
    this.pains = pains;
    this.buyingAuthority = buyingAuthority;
    this.willingnessToPay = willingnessToPay;
  }
}

const customers = [
  new CustomerProfile({
    id: "C01",
    role: "Data analyst",
    goal: "Learn cloud computing",
    context: "Full-time job",
    alternatives: ["Calendar", "YouTube", "Spreadsheet"],
    pains: ["No consistent schedule", "Forgets where to resume"],
    buyingAuthority: true,
    willingnessToPay: 8
  }),
  new CustomerProfile({
    id: "C02",
    role: "Product manager",
    goal: "Improve SQL",
    context: "Full-time job",
    alternatives: ["Notes", "Calendar"],
    pains: ["Course feels too long"],
    buyingAuthority: true,
    willingnessToPay: 7
  }),
  new CustomerProfile({
    id: "C03",
    role: "Engineer",
    goal: "Learn machine learning",
    context: "Full-time job",
    alternatives: ["Notion", "Calendar", "Course platform"],
    pains: ["Too much content", "Loses momentum"],
    buyingAuthority: true,
    willingnessToPay: 9
  })
];

function segmentCustomer(customer) {
  if (customer.buyingAuthority && customer.willingnessToPay >= 8) {
    return "high-intent professionals";
  }

  if (customer.buyingAuthority) {
    return "moderate-intent professionals";
  }

  return "non-buying users";
}

console.log("\nCustomer segmentation:");
customers.forEach((customer) => {
  console.log(customer.id, segmentCustomer(customer));
});


// ============================================================================
// 6. USER, BUYER, CUSTOMER
// ============================================================================

const productRoles = {
  user: "Person directly using the product",
  customer: "Person or organization receiving product value",
  buyer: "Person responsible for purchasing",
  economicBuyer: "Person accountable for budget and economic outcome",
  decisionMaker: "Person who approves the decision",
  influencer: "Person who affects the decision",
  administrator: "Person who manages access or configuration"
};

console.log("\nProduct roles:");
console.table(productRoles);


// ============================================================================
// 7. INTERVIEW DESIGN
// ============================================================================

const interviewQuestions = [
  "Tell me about the last time you tried to complete an online course.",
  "What were you trying to accomplish?",
  "What happened when your schedule changed?",
  "What did you do next?",
  "What tools or workarounds did you use?",
  "How frequently does this happen?",
  "What is the consequence?",
  "What have you already tried?",
  "Have you paid to solve this problem?"
];

console.log("\nInterview questions:");
interviewQuestions.forEach((question) => console.log("-", question));


// ============================================================================
// 8. QUALITATIVE CODING
// ============================================================================

const interviewNotes = [
  "I have three courses open but forget which lesson comes next.",
  "My meetings move around, so fixed reminders become annoying.",
  "I already use a calendar, but it does not understand course progress.",
  "I save courses during sales and never finish them.",
  "When I miss two days, restarting feels difficult."
];

function codeInterviewNotes(notes) {
  const themes = new Map([
    ["planning", 0],
    ["continuity", 0],
    ["abandonment", 0],
    ["calendar", 0]
  ]);

  for (const note of notes) {
    const text = note.toLowerCase();

    if (
      text.includes("schedule") ||
      text.includes("calendar") ||
      text.includes("reminder")
    ) {
      themes.set("planning", themes.get("planning") + 1);
    }

    if (
      text.includes("next") ||
      text.includes("restart") ||
      text.includes("miss")
    ) {
      themes.set("continuity", themes.get("continuity") + 1);
    }

    if (
      text.includes("never finish") ||
      text.includes("forget")
    ) {
      themes.set("abandonment", themes.get("abandonment") + 1);
    }

    if (text.includes("calendar")) {
      themes.set("calendar", themes.get("calendar") + 1);
    }
  }

  return Object.fromEntries(themes);
}

console.log("\nQualitative themes:");
console.table(codeInterviewNotes(interviewNotes));


// ============================================================================
// 9. JOBS TO BE DONE
// ============================================================================

const jobToBeDone = {
  situation: "When my work schedule becomes unpredictable",
  motivation: "I want to continue making progress on my course",
  outcome: "I want a realistic plan that adapts to available time"
};

console.log("\nJTBD:");
console.log(
  `When ${jobToBeDone.situation.toLowerCase()}, ` +
  `I want to ${jobToBeDone.motivation.toLowerCase()}, ` +
  `so that ${jobToBeDone.outcome.toLowerCase()}.`
);


// ============================================================================
// 10. MARKET SIZING
// ============================================================================

function calculateMarketSize({
  population,
  annualPrice,
  relevantPercentage,
  reachablePercentage
}) {
  const tam = population * annualPrice;
  const sam = tam * relevantPercentage;
  const som = sam * reachablePercentage;

  return { tam, sam, som };
}

const market = calculateMarketSize({
  population: 5_000_000,
  annualPrice: 120,
  relevantPercentage: 0.25,
  reachablePercentage: 0.02
});

console.log("\nMarket sizing:");
console.log(
  Object.fromEntries(
    Object.entries(market).map(([key, value]) => [
      key,
      `$${value.toLocaleString()}`
    ])
  )
);


// ============================================================================
// 11. TOP-DOWN AND BOTTOM-UP
// ============================================================================

function topDownMarketSize(population, relevantRate, annualSpend) {
  return population * relevantRate * annualSpend;
}

function bottomUpMarketSize(
  accounts,
  customersPerAccount,
  annualRevenuePerCustomer
) {
  return accounts * customersPerAccount * annualRevenuePerCustomer;
}

console.log("\nMarket estimation methods:");
console.log(
  "Top-down:",
  topDownMarketSize(100_000_000, 0.05, 120)
);
console.log(
  "Bottom-up:",
  bottomUpMarketSize(20_000, 100, 120)
);


// ============================================================================
// 12. SEGMENT ATTRACTIVENESS
// ============================================================================

const segments = [
  {
    name: "Working professionals",
    population: 5_000_000,
    pain: 9,
    willingnessToPay: 8,
    accessibility: 8,
    strategicFit: 9
  },
  {
    name: "University students",
    population: 10_000_000,
    pain: 6,
    willingnessToPay: 4,
    accessibility: 9,
    strategicFit: 7
  },
  {
    name: "Corporate L&D",
    population: 50_000,
    pain: 8,
    willingnessToPay: 9,
    accessibility: 6,
    strategicFit: 10
  }
];

function segmentAttractiveness(segment) {
  return (
    segment.pain *
    segment.willingnessToPay *
    segment.accessibility *
    segment.strategicFit
  );
}

console.log("\nSegment attractiveness:");
segments
  .map((segment) => ({
    ...segment,
    score: segmentAttractiveness(segment)
  }))
  .sort((a, b) => b.score - a.score)
  .forEach((segment) => {
    console.log(segment.name, segment.score);
  });


// ============================================================================
// 13. ALTERNATIVES
// ============================================================================

const alternatives = [
  {
    name: "Calendar",
    price: 0,
    convenience: 8,
    effectiveness: 4
  },
  {
    name: "Spreadsheet",
    price: 0,
    convenience: 5,
    effectiveness: 6
  },
  {
    name: "Course platform",
    price: 100,
    convenience: 7,
    effectiveness: 7
  },
  {
    name: "Human coach",
    price: 600,
    convenience: 7,
    effectiveness: 9
  },
  {
    name: "Do nothing",
    price: 0,
    convenience: 10,
    effectiveness: 1
  }
];

console.log("\nAlternative analysis:");
console.table(alternatives);


// ============================================================================
// 14. OPPORTUNITY SCORING
// ============================================================================

class Opportunity {
  constructor(
    name,
    customerValue,
    marketPotential,
    strategicFit,
    feasibility,
    confidence
  ) {
    this.name = name;
    this.customerValue = customerValue;
    this.marketPotential = marketPotential;
    this.strategicFit = strategicFit;
    this.feasibility = feasibility;
    this.confidence = confidence;
  }

  score() {
    return (
      this.customerValue *
      this.marketPotential *
      this.strategicFit *
      this.feasibility *
      this.confidence
    );
  }
}

const opportunities = [
  new Opportunity(
    "Adaptive daily study planning",
    9,
    8,
    9,
    8,
    0.75
  ),
  new Opportunity(
    "Course marketplace",
    6,
    10,
    5,
    5,
    0.4
  ),
  new Opportunity(
    "Human tutoring marketplace",
    8,
    9,
    6,
    4,
    0.55
  ),
  new Opportunity(
    "Corporate learning analytics",
    7,
    7,
    8,
    7,
    0.65
  )
];

console.log("\nOpportunity scoring:");
opportunities
  .sort((a, b) => b.score() - a.score())
  .forEach((opportunity) => {
    console.log(
      opportunity.name,
      opportunity.score().toFixed(2)
    );
  });


// ============================================================================
// 15. DESIRABILITY, VIABILITY, FEASIBILITY
// ============================================================================

function dvfScore(desirability, viability, feasibility) {
  // The minimum dimension exposes a severe weakness that an average can hide.
  return Math.min(desirability, viability, feasibility);
}

console.log("\nDVF:");
console.log(
  "Constraint score:",
  dvfScore(8.5, 6.5, 8)
);


// ============================================================================
// 16. RICE PRIORITIZATION
// ============================================================================

class RiceItem {
  constructor(name, reach, impact, confidence, effort) {
    this.name = name;
    this.reach = reach;
    this.impact = impact;
    this.confidence = confidence;
    this.effort = effort;
  }

  score() {
    return (
      this.reach *
      this.impact *
      this.confidence /
      this.effort
    );
  }
}

const riceItems = [
  new RiceItem("Adaptive scheduling", 5000, 3, 0.8, 4),
  new RiceItem("Progress resume", 4000, 2, 0.9, 2),
  new RiceItem("Gamification", 3000, 1, 0.5, 5),
  new RiceItem("Corporate analytics", 500, 3, 0.7, 6)
];

console.log("\nRICE:");
riceItems
  .sort((a, b) => b.score() - a.score())
  .forEach((item) => {
    console.log(item.name, item.score().toFixed(2));
  });


// ============================================================================
// 17. EVIDENCE HIERARCHY
// ============================================================================

const evidenceStrength = {
  opinion: 1,
  intent: 2,
  behavior: 4,
  commitment: 5,
  outcome: 6
};

console.log("\nEvidence hierarchy:");
console.table(evidenceStrength);


// ============================================================================
// 18. EXPERIMENT RESULT
// ============================================================================

class ExperimentResult {
  constructor(participants, successes) {
    if (participants < 0 || successes < 0) {
      throw new Error("Experiment counts cannot be negative.");
    }

    if (successes > participants) {
      throw new Error("Successes cannot exceed participants.");
    }

    this.participants = participants;
    this.successes = successes;
  }

  conversionRate() {
    return this.participants === 0
      ? 0
      : this.successes / this.participants;
  }
}

const experimentResult = new ExperimentResult(100, 31);

console.log("\nExperiment result:");
console.log(
  "Conversion:",
  `${(experimentResult.conversionRate() * 100).toFixed(1)}%`
);


// ============================================================================
// 19. RETENTION COHORT
// ============================================================================

function retentionRates(startingUsers, retainedUsers) {
  if (startingUsers <= 0) {
    throw new Error("Starting users must be positive.");
  }

  return retainedUsers.map(
    (users) => users / startingUsers
  );
}

const retention = retentionRates(
  1000,
  [1000, 720, 560, 480, 430]
);

console.log("\nRetention:");
retention.forEach((rate, month) => {
  console.log(`Month ${month}: ${(rate * 100).toFixed(1)}%`);
});


// ============================================================================
// 20. FUNNEL
// ============================================================================

function calculateFunnel({
  visitors,
  signups,
  activated,
  retained,
  paid
}) {
  const ratio = (a, b) => (b === 0 ? 0 : a / b);

  return {
    visitorToSignup: ratio(signups, visitors),
    signupToActivation: ratio(activated, signups),
    activationToRetention: ratio(retained, activated),
    retentionToPaid: ratio(paid, retained)
  };
}

const funnel = calculateFunnel({
  visitors: 10_000,
  signups: 1_000,
  activated: 650,
  retained: 400,
  paid: 80
});

console.log("\nFunnel:");
console.table(funnel);


// ============================================================================
// 21. NPS
// ============================================================================

function calculateNPS(responses) {
  if (responses.length === 0) {
    return 0;
  }

  const promoters = responses.filter((score) => score >= 9).length;
  const detractors = responses.filter((score) => score <= 6).length;

  return (
    (promoters / responses.length) * 100 -
    (detractors / responses.length) * 100
  );
}

console.log(
  "\nNPS:",
  calculateNPS([9, 10, 8, 7, 6, 9, 10, 5, 8, 9])
);


// ============================================================================
// 22. CUSTOMER VALUE
// ============================================================================

function customerValue({
  benefit,
  painReduction,
  timeSaved,
  switchingCost
}) {
  return (
    0.4 * benefit +
    0.3 * painReduction +
    0.2 * timeSaved -
    0.1 * switchingCost
  );
}

console.log(
  "\nCustomer value:",
  customerValue({
    benefit: 9,
    painReduction: 8,
    timeSaved: 7,
    switchingCost: 4
  }).toFixed(2)
);


// ============================================================================
// 23. ASSUMPTION RISK
// ============================================================================

const assumptions = [
  {
    description: "Customers experience recurring scheduling problems",
    importance: 5,
    uncertainty: 4
  },
  {
    description: "Customers will pay",
    importance: 5,
    uncertainty: 5
  },
  {
    description: "Calendar integration is technically feasible",
    importance: 4,
    uncertainty: 3
  }
];

console.log("\nAssumption risk:");
assumptions
  .map((item) => ({
    ...item,
    risk: item.importance * item.uncertainty
  }))
  .sort((a, b) => b.risk - a.risk)
  .forEach((item) => console.log(item.risk, item.description));


// ============================================================================
// 24. BAYESIAN UPDATING
// ============================================================================

function bayesianUpdate(
  prior,
  likelihoodIfTrue,
  likelihoodIfFalse
) {
  const numerator = likelihoodIfTrue * prior;

  const evidenceProbability =
    likelihoodIfTrue * prior +
    likelihoodIfFalse * (1 - prior);

  if (evidenceProbability === 0) {
    return 0;
  }

  return numerator / evidenceProbability;
}

const posterior = bayesianUpdate(
  0.3,
  0.8,
  0.2
);

console.log(
  "\nBayesian update:",
  `${(posterior * 100).toFixed(1)}%`
);


// ============================================================================
// 25. INFORMATION GAIN
// ============================================================================

function binaryEntropy(probability) {
  if (probability <= 0 || probability >= 1) {
    return 0;
  }

  return -(
    probability * Math.log2(probability) +
    (1 - probability) *
      Math.log2(1 - probability)
  );
}

function expectedInformationGain(prior, outcomes) {
  const priorEntropy = binaryEntropy(prior);

  const posteriorEntropy = outcomes.reduce(
    (sum, outcome) =>
      sum +
      outcome.probability *
        binaryEntropy(outcome.posterior),
    0
  );

  return priorEntropy - posteriorEntropy;
}

console.log(
  "\nInformation gain:",
  expectedInformationGain(0.5, [
    { posterior: 0.8, probability: 0.5 },
    { posterior: 0.2, probability: 0.5 }
  ]).toFixed(3)
);


// ============================================================================
// 26. EXPERIMENT SELECTION
// ============================================================================

class DiscoveryExperiment {
  constructor(
    name,
    cost,
    expectedInformationGainValue,
    decisionImpact
  ) {
    this.name = name;
    this.cost = cost;
    this.expectedInformationGainValue =
      expectedInformationGainValue;
    this.decisionImpact = decisionImpact;
  }

  informationValuePerCost() {
    if (this.cost <= 0) {
      return 0;
    }

    return (
      this.expectedInformationGainValue *
      this.decisionImpact /
      this.cost
    );
  }
}

const experiments = [
  new DiscoveryExperiment("Interview", 10, 0.3, 0.7),
  new DiscoveryExperiment("Prototype test", 100, 0.6, 0.9),
  new DiscoveryExperiment("Paid pre-order", 30, 0.8, 1.0),
  new DiscoveryExperiment("Large survey", 200, 0.35, 0.5)
];

console.log("\nExperiment value:");
experiments
  .sort(
    (a, b) =>
      b.informationValuePerCost() -
      a.informationValuePerCost()
  )
  .forEach((experiment) => {
    console.log(
      experiment.name,
      experiment.informationValuePerCost().toFixed(4)
    );
  });


// ============================================================================
// 27. ASYNCHRONOUS DISCOVERY
// ============================================================================

function fetchMockCustomerObservation(customerId, delay = 100) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        customerId,
        problem:
          "Difficulty maintaining course progress",
        behavioralEvidence: true
      });
    }, delay);
  });
}

async function runAsyncDiscovery() {
  const customerIds = ["C01", "C02", "C03"];

  // Promise.all demonstrates parallel retrieval when the data sources
  // are independent.
  const observations = await Promise.all(
    customerIds.map((id) =>
      fetchMockCustomerObservation(id)
    )
  );

  return observations;
}


// ============================================================================
// 28. ERROR HANDLING
// ============================================================================

function validateObservation(observation) {
  const errors = [];

  if (!observation.customerId) {
    errors.push("Customer ID is required.");
  }

  if (observation.frequencyPerMonth < 0) {
    errors.push("Frequency cannot be negative.");
  }

  if (
    observation.severity < 0 ||
    observation.severity > 10
  ) {
    errors.push("Severity must be between 0 and 10.");
  }

  return errors;
}

const invalidObservation = {
  customerId: "",
  frequencyPerMonth: -2,
  severity: 12
};

console.log(
  "\nValidation:",
  validateObservation(invalidObservation)
);


// ============================================================================
// 29. DISCOVERY DECISION GATE
// ============================================================================

function discoveryReadiness(scores) {
  const values = Object.values(scores);

  if (values.length === 0) {
    return {
      score: 0,
      decision: "insufficient evidence"
    };
  }

  const score = average(values);

  let decision;

  if (score >= 8) {
    decision = "proceed with strong evidence";
  } else if (score >= 6) {
    decision = "proceed with targeted validation";
  } else if (score >= 4) {
    decision = "continue discovery";
  } else {
    decision = "reconsider opportunity";
  }

  return { score, decision };
}

console.log(
  "\nDecision gate:",
  discoveryReadiness({
    problem: 8.5,
    customer: 8,
    market: 7.5,
    opportunity: 8.2,
    solution: 5,
    business: 6
  })
);


// ============================================================================
// 30. PRACTICAL DISCOVERY ENGINE
// ============================================================================

class DiscoveryEngine {
  constructor() {
    this.hypotheses = [];
    this.evidence = [];
    this.experiments = [];
  }

  addHypothesis(hypothesis) {
    if (!(hypothesis instanceof Hypothesis)) {
      throw new TypeError(
        "Expected a Hypothesis instance."
      );
    }

    this.hypotheses.push(hypothesis);
  }

  addEvidence(evidence) {
    if (!evidence || !evidence.type) {
      throw new Error(
        "Evidence requires a type."
      );
    }

    this.evidence.push(evidence);
  }

  addExperiment(experiment) {
    if (!(experiment instanceof DiscoveryExperiment)) {
      throw new TypeError(
        "Expected a DiscoveryExperiment."
      );
    }

    this.experiments.push(experiment);
  }

  highestRiskHypothesis() {
    if (this.hypotheses.length === 0) {
      return null;
    }

    return [...this.hypotheses].sort(
      (a, b) => b.risk - a.risk
    )[0];
  }

  highestValueExperiment() {
    if (this.experiments.length === 0) {
      return null;
    }

    return [...this.experiments].sort(
      (a, b) =>
        b.informationValuePerCost() -
        a.informationValuePerCost()
    )[0];
  }

  report() {
    return {
      hypothesisCount: this.hypotheses.length,
      evidenceCount: this.evidence.length,
      experimentCount: this.experiments.length,
      highestRiskHypothesis:
        this.highestRiskHypothesis()?.statement ?? null,
      highestValueExperiment:
        this.highestValueExperiment()?.name ?? null
    };
  }
}

const engine = new DiscoveryEngine();

hypotheses.forEach((hypothesis) =>
  engine.addHypothesis(hypothesis)
);

experiments.forEach((experiment) =>
  engine.addExperiment(experiment)
);

engine.addEvidence({
  type: "behavior",
  description:
    "Customers repeatedly create manual study schedules."
});

console.log("\nDiscovery engine report:");
console.table(engine.report());


// ============================================================================
// 31. RUN ASYNC EXAMPLE
// ============================================================================

runAsyncDiscovery()
  .then((result) => {
    console.log("\nAsynchronous customer evidence:");
    console.table(result);
  })
  .catch((error) => {
    console.error(
      "Discovery data retrieval failed:",
      error.message
    );
  });


// ============================================================================
// 32. JAVASCRIPT-SPECIFIC DESIGN NOTES
// ============================================================================

console.log("\nJavaScript-specific mechanisms demonstrated:");
console.log("- classes and objects");
console.log("- arrays and higher-order functions");
console.log("- Map");
console.log("- destructuring");
console.log("- optional chaining");
console.log("- nullish coalescing");
console.log("- Promises");
console.log("- async/await");
console.log("- Promise.all");
console.log("- validation and exceptions");
console.log("- console.table for structured analysis");

console.log("\nDiscovery principles demonstrated:");
console.log("- Start from problems rather than features.");
console.log("- Prefer behavioral evidence to hypothetical intent.");
console.log("- Treat assumptions as risks.");
console.log("- Size markets using explicit assumptions.");
console.log("- Compare opportunities using consistent criteria.");
console.log("- Design experiments to reduce important uncertainty.");
