/*
    Product Discovery: Industry-Style Technical Case Study

    Scenario
    -------
    StudyFlow is a hypothetical B2B/B2C learning-product company investigating
    whether it should build an adaptive study-planning product for working
    professionals.

    The program models an end-to-end discovery system:

        raw observations
            -> validated problem evidence
            -> customer segmentation
            -> market estimation
            -> alternatives
            -> opportunity scoring
            -> hypothesis prioritization
            -> experiment design
            -> decision gate

    The case study demonstrates C++17 data structures, classes, validation,
    algorithms, sorting, exception handling, file-independent data processing,
    and complexity considerations.

    Compile:
        g++ -std=c++17 -O2 product_discovery.cpp -o product_discovery

    Run:
        ./product_discovery
*/

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. DOMAIN MODELS
// ============================================================================

enum class EvidenceType {
    Opinion,
    Intent,
    Behavior,
    Commitment,
    Outcome
};

string toString(EvidenceType type) {
    switch (type) {
        case EvidenceType::Opinion:
            return "Opinion";
        case EvidenceType::Intent:
            return "Intent";
        case EvidenceType::Behavior:
            return "Behavior";
        case EvidenceType::Commitment:
            return "Commitment";
        case EvidenceType::Outcome:
            return "Outcome";
    }

    return "Unknown";
}

struct ProblemObservation {
    string customerId;
    string situation;
    string behavior;
    string consequence;
    double frequencyPerMonth{};
    double severity{};
    string currentAlternative;
};

struct Customer {
    string id;
    string role;
    string segment;
    bool buyingAuthority{};
    double willingnessToPay{};
};

struct Evidence {
    EvidenceType type;
    string description;
    double strength{};
};

struct Opportunity {
    string name;
    double customerValue{};
    double marketPotential{};
    double strategicFit{};
    double feasibility{};
    double confidence{};

    double score() const {
        return customerValue *
               marketPotential *
               strategicFit *
               feasibility *
               confidence;
    }
};

struct Experiment {
    string name;
    string hypothesis;
    double cost{};
    double expectedInformationGain{};
    double decisionImpact{};

    double informationValuePerCost() const {
        if (cost <= 0.0) {
            return 0.0;
        }

        return expectedInformationGain *
               decisionImpact /
               cost;
    }
};

struct DecisionGate {
    double problemEvidence{};
    double customerEvidence{};
    double marketEvidence{};
    double opportunityEvidence{};
    double solutionEvidence{};

    double readiness() const {
        return (
            problemEvidence +
            customerEvidence +
            marketEvidence +
            opportunityEvidence +
            solutionEvidence
        ) / 5.0;
    }

    string decision() const {
        const double score = readiness();

        if (score >= 8.0) {
            return "Proceed with strong evidence";
        }

        if (score >= 6.0) {
            return "Proceed with targeted validation";
        }

        if (score >= 4.0) {
            return "Continue discovery";
        }

        return "Reconsider the opportunity";
    }
};


// ============================================================================
// 2. VALIDATION
// ============================================================================

class ValidationError : public runtime_error {
public:
    explicit ValidationError(const string& message)
        : runtime_error(message) {}
};

void validateObservation(const ProblemObservation& observation) {
    if (observation.customerId.empty()) {
        throw ValidationError("Customer ID cannot be empty.");
    }

    if (observation.situation.empty()) {
        throw ValidationError("Situation cannot be empty.");
    }

    if (observation.frequencyPerMonth < 0.0) {
        throw ValidationError(
            "Problem frequency cannot be negative."
        );
    }

    if (observation.severity < 0.0 ||
        observation.severity > 10.0) {
        throw ValidationError(
            "Problem severity must be between 0 and 10."
        );
    }
}


// ============================================================================
// 3. DISCOVERY REPOSITORY
// ============================================================================

class DiscoveryRepository {
private:
    vector<ProblemObservation> observations;
    vector<Customer> customers;
    vector<Evidence> evidence;
    vector<Opportunity> opportunities;
    vector<Experiment> experiments;

public:
    void addObservation(const ProblemObservation& observation) {
        validateObservation(observation);
        observations.push_back(observation);
    }

    void addCustomer(const Customer& customer) {
        if (customer.id.empty()) {
            throw ValidationError(
                "Customer ID cannot be empty."
            );
        }

        if (customer.willingnessToPay < 0.0 ||
            customer.willingnessToPay > 10.0) {
            throw ValidationError(
                "Willingness to pay must be between 0 and 10."
            );
        }

        customers.push_back(customer);
    }

    void addEvidence(const Evidence& item) {
        if (item.description.empty()) {
            throw ValidationError(
                "Evidence description cannot be empty."
            );
        }

        if (item.strength < 0.0 ||
            item.strength > 10.0) {
            throw ValidationError(
                "Evidence strength must be between 0 and 10."
            );
        }

        evidence.push_back(item);
    }

    void addOpportunity(const Opportunity& opportunity) {
        opportunities.push_back(opportunity);
    }

    void addExperiment(const Experiment& experiment) {
        if (experiment.cost < 0.0) {
            throw ValidationError(
                "Experiment cost cannot be negative."
            );
        }

        experiments.push_back(experiment);
    }

    const vector<ProblemObservation>& getObservations() const {
        return observations;
    }

    const vector<Customer>& getCustomers() const {
        return customers;
    }

    const vector<Evidence>& getEvidence() const {
        return evidence;
    }

    const vector<Opportunity>& getOpportunities() const {
        return opportunities;
    }

    const vector<Experiment>& getExperiments() const {
        return experiments;
    }
};


// ============================================================================
// 4. ANALYTICS ENGINE
// ============================================================================

class DiscoveryAnalytics {
public:
    static double averageFrequency(
        const vector<ProblemObservation>& observations
    ) {
        if (observations.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& observation : observations) {
            total += observation.frequencyPerMonth;
        }

        return total / observations.size();
    }

    static double averageSeverity(
        const vector<ProblemObservation>& observations
    ) {
        if (observations.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& observation : observations) {
            total += observation.severity;
        }

        return total / observations.size();
    }

    static map<string, int> segmentCounts(
        const vector<Customer>& customers
    ) {
        map<string, int> result;

        for (const auto& customer : customers) {
            ++result[customer.segment];
        }

        return result;
    }

    static optional<Opportunity> bestOpportunity(
        const vector<Opportunity>& opportunities
    ) {
        if (opportunities.empty()) {
            return nullopt;
        }

        return *max_element(
            opportunities.begin(),
            opportunities.end(),
            [](const Opportunity& left,
               const Opportunity& right) {
                return left.score() < right.score();
            }
        );
    }

    static optional<Experiment> bestExperiment(
        const vector<Experiment>& experiments
    ) {
        if (experiments.empty()) {
            return nullopt;
        }

        return *max_element(
            experiments.begin(),
            experiments.end(),
            [](const Experiment& left,
               const Experiment& right) {
                return left.informationValuePerCost() <
                       right.informationValuePerCost();
            }
        );
    }
};


// ============================================================================
// 5. MARKET MODEL
// ============================================================================

struct MarketEstimate {
    long long totalCustomers{};
    double annualPrice{};
    double addressableRate{};
    double reachableRate{};

    double tam() const {
        return static_cast<double>(totalCustomers) *
               annualPrice;
    }

    double sam() const {
        return tam() * addressableRate;
    }

    double som() const {
        return sam() * reachableRate;
    }
};

class MarketAnalyzer {
public:
    static MarketEstimate estimate(
        long long population,
        double annualPrice,
        double addressableRate,
        double reachableRate
    ) {
        if (population < 0) {
            throw ValidationError(
                "Population cannot be negative."
            );
        }

        if (annualPrice < 0.0) {
            throw ValidationError(
                "Annual price cannot be negative."
            );
        }

        if (addressableRate < 0.0 ||
            addressableRate > 1.0 ||
            reachableRate < 0.0 ||
            reachableRate > 1.0) {
            throw ValidationError(
                "Market rates must be between 0 and 1."
            );
        }

        return {
            population,
            annualPrice,
            addressableRate,
            reachableRate
        };
    }

    static double topDown(
        long long population,
        double relevantRate,
        double annualSpend
    ) {
        return static_cast<double>(population) *
               relevantRate *
               annualSpend;
    }

    static double bottomUp(
        long long accounts,
        double customersPerAccount,
        double annualRevenuePerCustomer
    ) {
        return static_cast<double>(accounts) *
               customersPerAccount *
               annualRevenuePerCustomer;
    }
};


// ============================================================================
// 6. HYPOTHESIS MANAGEMENT
// ============================================================================

struct Hypothesis {
    string statement;
    double importance{};
    double confidence{};

    double uncertainty() const {
        return max(0.0, 1.0 - confidence);
    }

    double risk() const {
        return importance * uncertainty();
    }
};

class HypothesisManager {
private:
    vector<Hypothesis> hypotheses;

public:
    void add(const Hypothesis& hypothesis) {
        if (hypothesis.importance < 0.0 ||
            hypothesis.importance > 1.0 ||
            hypothesis.confidence < 0.0 ||
            hypothesis.confidence > 1.0) {
            throw ValidationError(
                "Importance and confidence must be between 0 and 1."
            );
        }

        hypotheses.push_back(hypothesis);
    }

    optional<Hypothesis> highestRisk() const {
        if (hypotheses.empty()) {
            return nullopt;
        }

        return *max_element(
            hypotheses.begin(),
            hypotheses.end(),
            [](const Hypothesis& left,
               const Hypothesis& right) {
                return left.risk() < right.risk();
            }
        );
    }

    const vector<Hypothesis>& all() const {
        return hypotheses;
    }
};


// ============================================================================
// 7. EVIDENCE ENGINE
// ============================================================================

class EvidenceEngine {
public:
    static double averageStrength(
        const vector<Evidence>& evidence
    ) {
        if (evidence.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& item : evidence) {
            total += item.strength;
        }

        return total / evidence.size();
    }

    static double typeWeight(EvidenceType type) {
        switch (type) {
            case EvidenceType::Opinion:
                return 1.0;
            case EvidenceType::Intent:
                return 2.0;
            case EvidenceType::Behavior:
                return 4.0;
            case EvidenceType::Commitment:
                return 5.0;
            case EvidenceType::Outcome:
                return 6.0;
        }

        return 0.0;
    }

    static double weightedEvidence(
        const vector<Evidence>& evidence
    ) {
        if (evidence.empty()) {
            return 0.0;
        }

        double weightedTotal = 0.0;
        double weightTotal = 0.0;

        for (const auto& item : evidence) {
            const double weight = typeWeight(item.type);

            weightedTotal += item.strength * weight;
            weightTotal += weight;
        }

        return weightTotal == 0.0
            ? 0.0
            : weightedTotal / weightTotal;
    }
};


// ============================================================================
// 8. DISCOVERY DECISION SYSTEM
// ============================================================================

class DiscoveryDecisionSystem {
private:
    DecisionGate gate;

public:
    explicit DiscoveryDecisionSystem(
        const DecisionGate& decisionGate
    )
        : gate(decisionGate) {}

    void printDecision() const {
        cout << "\nDecision gate\n";
        cout << "-------------\n";
        cout << fixed << setprecision(2);
        cout << "Problem evidence:      "
             << gate.problemEvidence << "/10\n";
        cout << "Customer evidence:     "
             << gate.customerEvidence << "/10\n";
        cout << "Market evidence:       "
             << gate.marketEvidence << "/10\n";
        cout << "Opportunity evidence:  "
             << gate.opportunityEvidence << "/10\n";
        cout << "Solution evidence:     "
             << gate.solutionEvidence << "/10\n";
        cout << "Readiness:             "
             << gate.readiness() << "/10\n";
        cout << "Decision:              "
             << gate.decision() << "\n";
    }
};


// ============================================================================
// 9. DISCOVERY CASE STUDY
// ============================================================================

void loadCaseStudyData(DiscoveryRepository& repository) {
    repository.addObservation({
        "C01",
        "After work",
        "Studies inconsistently",
        "Course completion is delayed",
        18,
        7,
        "Calendar reminders"
    });

    repository.addObservation({
        "C02",
        "After work",
        "Saves videos but rarely schedules study",
        "Knowledge remains incomplete",
        12,
        8,
        "Notes application"
    });

    repository.addObservation({
        "C03",
        "Weekend",
        "Attempts large study sessions",
        "Feels overwhelmed and stops",
        8,
        9,
        "Spreadsheet"
    });

    repository.addObservation({
        "C04",
        "Commute",
        "Watches short lessons",
        "Cannot maintain course sequence",
        20,
        6,
        "Video application"
    });

    repository.addCustomer({
        "C01",
        "Data Analyst",
        "Working professionals",
        true,
        8
    });

    repository.addCustomer({
        "C02",
        "Product Manager",
        "Working professionals",
        true,
        7
    });

    repository.addCustomer({
        "C03",
        "Engineer",
        "Working professionals",
        true,
        9
    });

    repository.addCustomer({
        "C04",
        "University Student",
        "University students",
        false,
        4
    });

    repository.addEvidence({
        EvidenceType::Behavior,
        "Customers repeatedly create manual study schedules.",
        8.5
    });

    repository.addEvidence({
        EvidenceType::Behavior,
        "Customers abandon courses after schedule disruptions.",
        8.0
    });

    repository.addEvidence({
        EvidenceType::Intent,
        "Customers say adaptive planning sounds useful.",
        5.0
    });

    repository.addEvidence({
        EvidenceType::Commitment,
        "A small group agrees to test a concierge planning service.",
        7.5
    });

    repository.addOpportunity({
        "Adaptive daily study planning",
        9,
        8,
        9,
        8,
        0.75
    });

    repository.addOpportunity({
        "Course marketplace",
        6,
        10,
        5,
        5,
        0.40
    });

    repository.addOpportunity({
        "Human tutoring marketplace",
        8,
        9,
        6,
        4,
        0.55
    });

    repository.addOpportunity({
        "Corporate learning analytics",
        7,
        7,
        8,
        7,
        0.65
    });

    repository.addExperiment({
        "Customer interviews",
        "Determine whether schedule disruption is recurring and severe.",
        10,
        0.30,
        0.70
    });

    repository.addExperiment({
        "Prototype test",
        "Measure whether an adaptive plan improves study consistency.",
        100,
        0.60,
        0.90
    });

    repository.addExperiment({
        "Paid pre-order",
        "Test willingness to make a financial commitment.",
        30,
        0.80,
        1.00
    });

    repository.addExperiment({
        "Large survey",
        "Estimate prevalence across a broader population.",
        200,
        0.35,
        0.50
    });
}


// ============================================================================
// 10. REPORTING
// ============================================================================

void printProblemAnalysis(
    const DiscoveryRepository& repository
) {
    const auto& observations =
        repository.getObservations();

    cout << "\nProblem discovery\n";
    cout << "-----------------\n";
    cout << fixed << setprecision(2);

    cout << "Observed customers: "
         << observations.size() << "\n";

    cout << "Average monthly frequency: "
         << DiscoveryAnalytics::averageFrequency(observations)
         << "\n";

    cout << "Average severity: "
         << DiscoveryAnalytics::averageSeverity(observations)
         << "/10\n";

    cout << "\nObservation details:\n";

    for (const auto& observation : observations) {
        cout
            << observation.customerId << " | "
            << observation.situation << " | "
            << observation.behavior << " | severity="
            << observation.severity << " | frequency="
            << observation.frequencyPerMonth << "\n";
    }
}

void printCustomerAnalysis(
    const DiscoveryRepository& repository
) {
    cout << "\nCustomer discovery\n";
    cout << "------------------\n";

    const auto segments =
        DiscoveryAnalytics::segmentCounts(
            repository.getCustomers()
        );

    for (const auto& [segment, count] : segments) {
        cout << segment << ": "
             << count << " customers\n";
    }

    cout << "\nCustomer records:\n";

    for (const auto& customer :
         repository.getCustomers()) {
        cout
            << customer.id << " | "
            << customer.role << " | "
            << customer.segment << " | buying authority="
            << (customer.buyingAuthority ? "yes" : "no")
            << " | willingness="
            << customer.willingnessToPay
            << "/10\n";
    }
}

void printMarketAnalysis() {
    cout << "\nMarket discovery\n";
    cout << "----------------\n";

    const auto market =
        MarketAnalyzer::estimate(
            5'000'000,
            120.0,
            0.25,
            0.02
        );

    cout << fixed << setprecision(2);

    cout << "TAM: $" << market.tam() << "\n";
    cout << "SAM: $" << market.sam() << "\n";
    cout << "SOM: $" << market.som() << "\n";

    const double topDown =
        MarketAnalyzer::topDown(
            100'000'000,
            0.05,
            120.0
        );

    const double bottomUp =
        MarketAnalyzer::bottomUp(
            20'000,
            100.0,
            120.0
        );

    cout << "\nTop-down estimate: $"
         << topDown << "\n";

    cout << "Bottom-up estimate: $"
         << bottomUp << "\n";
}

void printOpportunityAnalysis(
    const DiscoveryRepository& repository
) {
    cout << "\nOpportunity discovery\n";
    cout << "---------------------\n";
    cout << fixed << setprecision(2);

    vector<Opportunity> sorted =
        repository.getOpportunities();

    sort(
        sorted.begin(),
        sorted.end(),
        [](const Opportunity& left,
           const Opportunity& right) {
            return left.score() > right.score();
        }
    );

    for (const auto& opportunity : sorted) {
        cout
            << opportunity.name
            << " | score="
            << opportunity.score()
            << "\n";
    }

    const auto best =
        DiscoveryAnalytics::bestOpportunity(
            repository.getOpportunities()
        );

    if (best.has_value()) {
        cout << "\nHighest-scoring opportunity: "
             << best->name << "\n";
    }
}

void printExperimentAnalysis(
    const DiscoveryRepository& repository
) {
    cout << "\nExperiment analysis\n";
    cout << "-------------------\n";
    cout << fixed << setprecision(4);

    vector<Experiment> sorted =
        repository.getExperiments();

    sort(
        sorted.begin(),
        sorted.end(),
        [](const Experiment& left,
           const Experiment& right) {
            return left.informationValuePerCost() >
                   right.informationValuePerCost();
        }
    );

    for (const auto& experiment : sorted) {
        cout
            << experiment.name
            << " | value/cost="
            << experiment.informationValuePerCost()
            << " | cost=$"
            << experiment.cost
            << "\n";
    }

    const auto best =
        DiscoveryAnalytics::bestExperiment(
            repository.getExperiments()
        );

    if (best.has_value()) {
        cout << "\nHighest information value per cost: "
             << best->name << "\n";
    }
}


// ============================================================================
// 11. ADVANCED: ENTROPY
// ============================================================================

double binaryEntropy(double probability) {
    if (probability <= 0.0 ||
        probability >= 1.0) {
        return 0.0;
    }

    return -(
        probability * log2(probability) +
        (1.0 - probability) *
            log2(1.0 - probability)
    );
}

double expectedInformationGain(
    double prior,
    const vector<pair<double, double>>& outcomes
) {
    /*
        Each pair represents:
            posterior probability
            probability of observing that outcome

        Information gain =
            prior entropy - expected posterior entropy
    */

    const double priorEntropy =
        binaryEntropy(prior);

    double expectedPosteriorEntropy = 0.0;

    for (const auto& [posterior, outcomeProbability] :
         outcomes) {
        expectedPosteriorEntropy +=
            outcomeProbability *
            binaryEntropy(posterior);
    }

    return priorEntropy -
           expectedPosteriorEntropy;
}


// ============================================================================
// 12. ADVANCED: BAYESIAN UPDATE
// ============================================================================

double bayesianUpdate(
    double prior,
    double likelihoodIfTrue,
    double likelihoodIfFalse
) {
    const double numerator =
        likelihoodIfTrue * prior;

    const double evidenceProbability =
        likelihoodIfTrue * prior +
        likelihoodIfFalse * (1.0 - prior);

    if (evidenceProbability == 0.0) {
        return 0.0;
    }

    return numerator /
           evidenceProbability;
}


// ============================================================================
// 13. ADVANCED: SIMPLE BOOTSTRAP
// ============================================================================

vector<double> bootstrapMeans(
    const vector<double>& values,
    int repetitions
) {
    if (values.empty()) {
        throw ValidationError(
            "Bootstrap requires at least one observation."
        );
    }

    if (repetitions <= 0) {
        throw ValidationError(
            "Bootstrap repetitions must be positive."
        );
    }

    /*
        Bootstrap resampling approximates the sampling distribution of a
        statistic by repeatedly sampling observations with replacement.

        This is useful in discovery analytics when the underlying distribution
        is uncertain and the sample is not large enough for simplistic
        normal-theory reasoning.
    */

    vector<double> means;
    means.reserve(repetitions);

    unsigned seed = 42;
    std::mt19937 generator(seed);

    uniform_int_distribution<size_t> distribution(
        0,
        values.size() - 1
    );

    for (int repetition = 0;
         repetition < repetitions;
         ++repetition) {
        double total = 0.0;

        for (size_t i = 0;
             i < values.size();
             ++i) {
            total += values[distribution(generator)];
        }

        means.push_back(
            total /
            static_cast<double>(values.size())
        );
    }

    return means;
}


// ============================================================================
// 14. ADVANCED: DISCOVERY PIPELINE
// ============================================================================

class DiscoveryPipeline {
private:
    DiscoveryRepository repository;
    HypothesisManager hypothesisManager;

public:
    void load() {
        loadCaseStudyData(repository);

        hypothesisManager.add({
            "Customers frequently struggle with course continuity.",
            0.95,
            0.35
        });

        hypothesisManager.add({
            "Customers will pay for adaptive study planning.",
            0.90,
            0.20
        });

        hypothesisManager.add({
            "Existing calendars do not solve course-specific planning.",
            0.60,
            0.50
        });
    }

    void run() const {
        printProblemAnalysis(repository);
        printCustomerAnalysis(repository);
        printMarketAnalysis();
        printOpportunityAnalysis(repository);
        printExperimentAnalysis(repository);

        cout << "\nHypothesis analysis\n";
        cout << "--------------------\n";

        const auto highestRisk =
            hypothesisManager.highestRisk();

        if (highestRisk.has_value()) {
            cout
                << "Highest-risk hypothesis: "
                << highestRisk->statement << "\n"
                << "Risk score: "
                << highestRisk->risk()
                << "\n";
        }

        const double informationGain =
            expectedInformationGain(
                0.5,
                {
                    {0.8, 0.5},
                    {0.2, 0.5}
                }
            );

        cout << "\nInformation gain: "
             << informationGain
             << " bits\n";

        const double posterior =
            bayesianUpdate(
                0.30,
                0.80,
                0.20
            );

        cout << "Bayesian posterior: "
             << posterior
             << "\n";

        const DecisionGate gate{
            8.5,
            8.0,
            7.5,
            8.2,
            5.5
        };

        DiscoveryDecisionSystem decisionSystem(gate);
        decisionSystem.printDecision();
    }
};


// ============================================================================
// 15. INTERACTIVE INPUT
// ============================================================================

optional<double> parseNonNegativeNumber(
    const string& input
) {
    try {
        size_t position = 0;
        const double value =
            stod(input, &position);

        if (position != input.size()) {
            return nullopt;
        }

        if (!isfinite(value) ||
            value < 0.0) {
            return nullopt;
        }

        return value;
    }
    catch (...) {
        return nullopt;
    }
}

void demonstrateInputValidation() {
    cout << "\nInput validation example\n";
    cout << "------------------------\n";

    const vector<string> inputs = {
        "8.5",
        "-2",
        "abc",
        "10"
    };

    for (const auto& input : inputs) {
        const auto parsed =
            parseNonNegativeNumber(input);

        if (parsed.has_value()) {
            cout << input
                 << " -> valid value "
                 << *parsed
                 << "\n";
        }
        else {
            cout << input
                 << " -> invalid input\n";
        }
    }
}


// ============================================================================
// 16. COMPLEXITY DISCUSSION
// ============================================================================

void printComplexityNotes() {
    cout << "\nComplexity considerations\n";
    cout << "-------------------------\n";

    cout << "Observation averaging: O(n)\n";
    cout << "Customer segmentation: O(n log k) approximately, "
         << "where k is the number of segments.\n";
    cout << "Finding maximum opportunity: O(n)\n";
    cout << "Sorting opportunities: O(n log n)\n";
    cout << "Bootstrap simulation: O(R * n), where R is repetitions.\n";

    cout << "\nMemory considerations:\n";
    cout << "Repository storage: O(n + m + p + e), "
         << "where each term represents a stored collection.\n";

    cout << "\nTrade-off:\n";
    cout << "Sorting produces a complete ranking but costs more than "
         << "finding only the best opportunity.\n";
}


// ============================================================================
// 17. SECURITY AND DATA GOVERNANCE
// ============================================================================

void printSecurityConsiderations() {
    cout << "\nSecurity and research-data considerations\n";
    cout << "------------------------------------------\n";

    const vector<string> rules = {
        "Collect only information necessary for the discovery objective.",
        "Avoid storing unnecessary personal identifiers.",
        "Restrict access to interview recordings and research notes.",
        "Separate customer identity from analytical datasets where practical.",
        "Do not treat sensitive personal information as ordinary product analytics.",
        "Document consent and permitted uses for research data.",
        "Validate imported data before analytical processing.",
        "Do not expose raw customer research in public dashboards."
    };

    for (const auto& rule : rules) {
        cout << "- " << rule << "\n";
    }
}


// ============================================================================
// 18. EDGE CASES AND FAILURE CONDITIONS
// ============================================================================

void demonstrateEdgeCases() {
    cout << "\nEdge cases\n";
    cout << "----------\n";

    try {
        ProblemObservation invalid{
            "",
            "",
            "behavior",
            "impact",
            -1,
            12,
            "none"
        };

        validateObservation(invalid);
    }
    catch (const ValidationError& error) {
        cout << "Caught validation error: "
             << error.what()
             << "\n";
    }

    try {
        MarketAnalyzer::estimate(
            1'000,
            120,
            1.2,
            0.2
        );
    }
    catch (const ValidationError& error) {
        cout << "Caught market validation error: "
             << error.what()
             << "\n";
    }

    try {
        bootstrapMeans({}, 100);
    }
    catch (const ValidationError& error) {
        cout << "Caught bootstrap error: "
             << error.what()
             << "\n";
    }
}


// ============================================================================
// 19. MAIN
// ============================================================================

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cout << "============================================================\n";
    cout << "PRODUCT DISCOVERY CASE STUDY\n";
    cout << "============================================================\n";

    cout << "\nScenario:\n";
    cout << "StudyFlow is evaluating whether to build an adaptive study "
         << "planning product for working professionals.\n";

    cout << "\nThe discovery question is not:\n";
    cout << "\"Can we build an adaptive planner?\"\n";

    cout << "\nThe primary discovery question is:\n";
    cout << "\"Is there a meaningful, recurring, valuable problem that "
         << "justifies solving, for a sufficiently attractive customer "
         << "segment and market?\"\n";

    try {
        DiscoveryPipeline pipeline;
        pipeline.load();
        pipeline.run();

        demonstrateInputValidation();
        printComplexityNotes();
        printSecurityConsiderations();
        demonstrateEdgeCases();

        cout << "\n============================================================\n";
        cout << "CASE STUDY COMPLETED\n";
        cout << "============================================================\n";
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
