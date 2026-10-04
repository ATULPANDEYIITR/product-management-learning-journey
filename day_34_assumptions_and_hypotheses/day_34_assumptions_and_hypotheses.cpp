#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Repository Governance Investment Case Study
 * --------------------------------------------
 *
 * A product organization is deciding whether an automated operational
 * monitoring capability should move from pilot to production.
 *
 * The governance engine treats four uncertainty dimensions separately:
 *
 *   Desirability  -> Is the outcome valuable enough for users?
 *   Viability     -> Can the operating/commercial model sustain the capability?
 *   Feasibility   -> Can the organization reliably build and operate it?
 *   Risk          -> What happens if a critical assumption is wrong?
 *
 * The program demonstrates:
 *   - explicit assumption mapping
 *   - falsifiable hypotheses
 *   - evidence strength
 *   - impact/uncertainty exposure
 *   - experiment prioritization
 *   - threshold-based hypothesis evaluation
 *   - validation failures
 *   - C++17 data structures and algorithms
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic assumptions_hypotheses.cpp -o assumptions_hypotheses
 */

enum class Dimension {
    Desirability,
    Viability,
    Feasibility,
    Risk
};

enum class EvidenceType {
    Interview,
    Survey,
    Prototype,
    FinancialModel,
    TechnicalSpike,
    ProductionData
};

enum class HypothesisStatus {
    Untested,
    Testing,
    Supported,
    Refuted,
    Inconclusive
};

std::string toString(Dimension dimension) {
    switch (dimension) {
        case Dimension::Desirability: return "desirability";
        case Dimension::Viability: return "viability";
        case Dimension::Feasibility: return "feasibility";
        case Dimension::Risk: return "risk";
    }

    throw std::logic_error("Unknown dimension");
}

std::string toString(EvidenceType type) {
    switch (type) {
        case EvidenceType::Interview: return "interview";
        case EvidenceType::Survey: return "survey";
        case EvidenceType::Prototype: return "prototype";
        case EvidenceType::FinancialModel: return "financial_model";
        case EvidenceType::TechnicalSpike: return "technical_spike";
        case EvidenceType::ProductionData: return "production_data";
    }

    throw std::logic_error("Unknown evidence type");
}

std::string toString(HypothesisStatus status) {
    switch (status) {
        case HypothesisStatus::Untested: return "untested";
        case HypothesisStatus::Testing: return "testing";
        case HypothesisStatus::Supported: return "supported";
        case HypothesisStatus::Refuted: return "refuted";
        case HypothesisStatus::Inconclusive: return "inconclusive";
    }

    throw std::logic_error("Unknown hypothesis status");
}

void requireUnitInterval(double value, const std::string& field) {
    if (!std::isfinite(value) || value < 0.0 || value > 1.0) {
        throw std::invalid_argument(
            field + " must be a finite value between 0 and 1"
        );
    }
}

void requireText(const std::string& value, const std::string& field) {
    if (value.empty()) {
        throw std::invalid_argument(field + " cannot be empty");
    }
}

struct Evidence {
    std::string source;
    EvidenceType type;
    double strength;
    bool supports;
    std::string observation;

    Evidence(
        std::string source_,
        EvidenceType type_,
        double strength_,
        bool supports_,
        std::string observation_
    )
        : source(std::move(source_)),
          type(type_),
          strength(strength_),
          supports(supports_),
          observation(std::move(observation_)) {
        requireText(source, "Evidence source");
        requireText(observation, "Evidence observation");
        requireUnitInterval(strength, "Evidence strength");
    }
};

struct Assumption {
    std::string id;
    std::string statement;
    Dimension dimension;
    double confidence;
    double impact;
    double uncertainty;
    std::string owner;
    std::string rationale;
    std::vector<Evidence> evidence;

    double exposure() const {
        /*
         * Exposure is deliberately separate from confidence.
         * A low-confidence assumption with low impact may be less urgent
         * than a low-confidence assumption whose failure threatens the system.
         */
        return impact * uncertainty;
    }

    double evidenceConfidence() const {
        if (evidence.empty()) {
            return 0.0;
        }

        double signedStrength = 0.0;
        double totalStrength = 0.0;

        for (const auto& item : evidence) {
            signedStrength += item.supports
                ? item.strength
                : -item.strength;

            totalStrength += item.strength;
        }

        if (totalStrength == 0.0) {
            return 0.0;
        }

        const double normalized =
            (signedStrength / totalStrength + 1.0) / 2.0;

        return std::clamp(normalized, 0.0, 1.0);
    }
};

struct Hypothesis {
    std::string id;
    std::string assumptionId;
    std::string statement;
    std::string metric;
    double threshold;
    bool atLeast;
    std::size_t sampleRequirement;
    HypothesisStatus status = HypothesisStatus::Untested;
    std::optional<double> observedValue;

    Hypothesis(
        std::string id_,
        std::string assumptionId_,
        std::string statement_,
        std::string metric_,
        double threshold_,
        bool atLeast_,
        std::size_t sampleRequirement_
    )
        : id(std::move(id_)),
          assumptionId(std::move(assumptionId_)),
          statement(std::move(statement_)),
          metric(std::move(metric_)),
          threshold(threshold_),
          atLeast(atLeast_),
          sampleRequirement(sampleRequirement_) {
        requireText(id, "Hypothesis ID");
        requireText(assumptionId, "Hypothesis assumption ID");
        requireText(statement, "Hypothesis statement");
        requireText(metric, "Hypothesis metric");

        if (!std::isfinite(threshold)) {
            throw std::invalid_argument(
                "Hypothesis threshold must be finite"
            );
        }

        if (sampleRequirement == 0) {
            throw std::invalid_argument(
                "Hypothesis sample requirement must be positive"
            );
        }
    }

    HypothesisStatus evaluate(double observed) {
        if (!std::isfinite(observed)) {
            throw std::invalid_argument(
                "Observed hypothesis value must be finite"
            );
        }

        observedValue = observed;

        const bool passes = atLeast
            ? observed >= threshold
            : observed <= threshold;

        status = passes
            ? HypothesisStatus::Supported
            : HypothesisStatus::Refuted;

        return status;
    }
};

struct Experiment {
    std::string id;
    std::string hypothesisId;
    std::string method;
    double cost;
    int durationDays;
    double informationGain;

    Experiment(
        std::string id_,
        std::string hypothesisId_,
        std::string method_,
        double cost_,
        int durationDays_,
        double informationGain_
    )
        : id(std::move(id_)),
          hypothesisId(std::move(hypothesisId_)),
          method(std::move(method_)),
          cost(cost_),
          durationDays(durationDays_),
          informationGain(informationGain_) {
        requireText(id, "Experiment ID");
        requireText(hypothesisId, "Experiment hypothesis ID");
        requireText(method, "Experiment method");

        if (!std::isfinite(cost) || cost < 0.0) {
            throw std::invalid_argument(
                "Experiment cost must be non-negative"
            );
        }

        if (durationDays <= 0) {
            throw std::invalid_argument(
                "Experiment duration must be positive"
            );
        }

        requireUnitInterval(
            informationGain,
            "Experiment information gain"
        );
    }
};

struct ExperimentScore {
    const Experiment* experiment;
    const Hypothesis* hypothesis;
    const Assumption* assumption;
    double priority;
};

class ValidationEngine {
private:
    std::map<std::string, Assumption> assumptions_;
    std::map<std::string, Hypothesis> hypotheses_;
    std::map<std::string, Experiment> experiments_;

public:
    void addAssumption(Assumption assumption) {
        if (assumptions_.contains(assumption.id)) {
            throw std::invalid_argument(
                "Duplicate assumption: " + assumption.id
            );
        }

        requireUnitInterval(
            assumption.confidence,
            "Assumption confidence"
        );
        requireUnitInterval(
            assumption.impact,
            "Assumption impact"
        );
        requireUnitInterval(
            assumption.uncertainty,
            "Assumption uncertainty"
        );

        assumptions_.emplace(
            assumption.id,
            std::move(assumption)
        );
    }

    void addHypothesis(Hypothesis hypothesis) {
        if (!assumptions_.contains(hypothesis.assumptionId)) {
            throw std::invalid_argument(
                "Unknown assumption referenced by hypothesis: " +
                hypothesis.assumptionId
            );
        }

        if (hypotheses_.contains(hypothesis.id)) {
            throw std::invalid_argument(
                "Duplicate hypothesis: " + hypothesis.id
            );
        }

        hypotheses_.emplace(
            hypothesis.id,
            std::move(hypothesis)
        );
    }

    void addExperiment(Experiment experiment) {
        if (!hypotheses_.contains(experiment.hypothesisId)) {
            throw std::invalid_argument(
                "Unknown hypothesis referenced by experiment: " +
                experiment.hypothesisId
            );
        }

        if (experiments_.contains(experiment.id)) {
            throw std::invalid_argument(
                "Duplicate experiment: " + experiment.id
            );
        }

        experiments_.emplace(
            experiment.id,
            std::move(experiment)
        );
    }

    void attachEvidence(
        const std::string& assumptionId,
        Evidence evidence
    ) {
        auto iterator = assumptions_.find(assumptionId);

        if (iterator == assumptions_.end()) {
            throw std::out_of_range(
                "Unknown assumption: " + assumptionId
            );
        }

        iterator->second.evidence.push_back(std::move(evidence));
    }

    HypothesisStatus evaluateHypothesis(
        const std::string& hypothesisId,
        double observedValue
    ) {
        auto iterator = hypotheses_.find(hypothesisId);

        if (iterator == hypotheses_.end()) {
            throw std::out_of_range(
                "Unknown hypothesis: " + hypothesisId
            );
        }

        return iterator->second.evaluate(observedValue);
    }

    const std::map<std::string, Assumption>& assumptions() const {
        return assumptions_;
    }

    const std::map<std::string, Hypothesis>& hypotheses() const {
        return hypotheses_;
    }

    const std::map<std::string, Experiment>& experiments() const {
        return experiments_;
    }

    std::vector<const Assumption*> rankAssumptions(
        std::optional<Dimension> filter = std::nullopt
    ) const {
        std::vector<const Assumption*> result;

        for (const auto& [id, assumption] : assumptions_) {
            if (!filter.has_value() ||
                assumption.dimension == filter.value()) {
                result.push_back(&assumption);
            }
        }

        std::sort(
            result.begin(),
            result.end(),
            [](const Assumption* left, const Assumption* right) {
                return left->exposure() > right->exposure();
            }
        );

        return result;
    }

    std::vector<ExperimentScore> rankExperiments() const {
        std::vector<ExperimentScore> scores;

        for (const auto& [id, experiment] : experiments_) {
            const auto hypothesisIterator =
                hypotheses_.find(experiment.hypothesisId);

            if (hypothesisIterator == hypotheses_.end()) {
                continue;
            }

            const Hypothesis& hypothesis = hypothesisIterator->second;

            const auto assumptionIterator =
                assumptions_.find(hypothesis.assumptionId);

            if (assumptionIterator == assumptions_.end()) {
                continue;
            }

            const Assumption& assumption = assumptionIterator->second;

            /*
             * This is a portfolio-prioritization heuristic, not a statistical
             * probability. It rewards experiments that reduce high-impact
             * uncertainty efficiently.
             */
            const double informationPerCost =
                experiment.informationGain /
                std::max(experiment.cost, 1.0);

            const double priority =
                assumption.exposure() *
                informationPerCost *
                (1.0 - assumption.evidenceConfidence());

            scores.push_back({
                &experiment,
                &hypothesis,
                &assumption,
                priority
            });
        }

        std::sort(
            scores.begin(),
            scores.end(),
            [](const ExperimentScore& left, const ExperimentScore& right) {
                return left.priority > right.priority;
            }
        );

        return scores;
    }
};

void printHeading(const std::string& title) {
    std::cout << "\n"
              << std::string(78, '=')
              << "\n"
              << title
              << "\n"
              << std::string(78, '=')
              << "\n";
}

void populateCaseStudy(ValidationEngine& engine) {
    engine.addAssumption({
        "A-DES-201",
        "Operations managers value automated exception monitoring enough to change their current workflow.",
        Dimension::Desirability,
        0.35,
        0.85,
        0.80,
        "Product Research",
        "Interviews reveal workflow pain, but actual priority and behavioral adoption are uncertain."
    });

    engine.addAssumption({
        "A-VIA-201",
        "Customers will pay recurring fees that cover infrastructure, support, and operational costs.",
        Dimension::Viability,
        0.30,
        0.90,
        0.85,
        "Commercial",
        "The economic benefit appears plausible, but willingness to pay has not been validated."
    });

    engine.addAssumption({
        "A-FEA-201",
        "The event-processing platform can meet the latency target under production-shaped peak traffic.",
        Dimension::Feasibility,
        0.60,
        0.80,
        0.50,
        "Engineering",
        "Moderate-load technical tests are positive, but peak distribution and contention remain unknown."
    });

    engine.addAssumption({
        "A-RISK-201",
        "False-positive alerts will not reach a level that causes customers to disable monitoring.",
        Dimension::Risk,
        0.25,
        0.95,
        0.85,
        "Risk",
        "Pilot telemetry suggests alert fatigue can undermine otherwise valuable monitoring."
    });

    engine.addHypothesis({
        "H-DES-201",
        "A-DES-201",
        "At least 65% of qualified managers will rank automated exception monitoring among their top three workflow improvements.",
        "priority selection rate",
        0.65,
        true,
        30
    });

    engine.addHypothesis({
        "H-VIA-201",
        "A-VIA-201",
        "At least 40% of qualified prospects will accept the proposed recurring price.",
        "price acceptance rate",
        0.40,
        true,
        15
    });

    engine.addHypothesis({
        "H-FEA-201",
        "A-FEA-201",
        "The event processor will maintain p95 evaluation latency at or below 250 milliseconds under representative peak load.",
        "p95 latency milliseconds",
        250.0,
        false,
        10000
    });

    engine.addHypothesis({
        "H-RISK-201",
        "A-RISK-201",
        "Fewer than 8% of active users will disable monitoring after false-positive exposure.",
        "monitoring disablement rate",
        0.08,
        false,
        50
    });

    engine.addExperiment({
        "E-DES-201",
        "H-DES-201",
        "Structured interviews followed by a priority-ranking prototype test",
        800.0,
        10,
        0.85
    });

    engine.addExperiment({
        "E-VIA-201",
        "H-VIA-201",
        "Price-sensitivity interviews with a purchasing commitment question",
        1000.0,
        14,
        0.90
    });

    engine.addExperiment({
        "E-FEA-201",
        "H-FEA-201",
        "Production-shaped load test capturing the complete latency distribution",
        1500.0,
        5,
        0.95
    });

    engine.addExperiment({
        "E-RISK-201",
        "H-RISK-201",
        "Controlled false-positive exposure with retention and disablement tracking",
        900.0,
        21,
        0.88
    });

    engine.attachEvidence(
        "A-DES-201",
        {
            source: "Operations interviews",
            type: EvidenceType::Interview,
            strength: 0.70,
            supports: true,
            observation: "Managers consistently described manual exception monitoring as a significant burden."
        }
    );

    engine.attachEvidence(
        "A-VIA-201",
        {
            source: "Customer discovery",
            type: EvidenceType::Interview,
            strength: 0.60,
            supports: false,
            observation: "Prospects valued the capability but several resisted the proposed recurring price."
        }
    );

    engine.attachEvidence(
        "A-FEA-201",
        {
            source: "Engineering technical spike",
            type: EvidenceType::TechnicalSpike,
            strength: 0.75,
            supports: true,
            observation: "The processor stayed within target latency under moderate load."
        }
    );

    engine.attachEvidence(
        "A-RISK-201",
        {
            source: "Pilot production telemetry",
            type: EvidenceType::ProductionData,
            strength: 0.70,
            supports: false,
            observation: "False-positive notifications correlated with increased monitoring disablement."
        }
    );
}

void printExposureAnalysis(const ValidationEngine& engine) {
    printHeading("Assumption mapping and exposure");

    for (Dimension dimension : {
        Dimension::Desirability,
        Dimension::Viability,
        Dimension::Feasibility,
        Dimension::Risk
    }) {
        std::cout << "\n"
                  << toString(dimension)
                  << "\n";

        for (const Assumption* assumption :
             engine.rankAssumptions(dimension)) {
            std::cout << "  "
                      << assumption->id
                      << " | exposure="
                      << std::fixed
                      << std::setprecision(3)
                      << assumption->exposure()
                      << " | evidence="
                      << assumption->evidenceConfidence()
                      << "\n";

            std::cout << "    "
                      << assumption->statement
                      << "\n";
        }
    }
}

void evaluateCaseStudy(ValidationEngine& engine) {
    printHeading("Hypothesis outcomes");

    const std::map<std::string, double> observations = {
        {"H-DES-201", 0.72},
        {"H-VIA-201", 0.27},
        {"H-FEA-201", 235.0},
        {"H-RISK-201", 0.11}
    };

    for (const auto& [hypothesisId, value] : observations) {
        const auto status =
            engine.evaluateHypothesis(hypothesisId, value);

        const auto& hypothesis =
            engine.hypotheses().at(hypothesisId);

        std::cout << hypothesisId
                  << " | "
                  << hypothesis.metric
                  << "="
                  << value
                  << " | "
                  << toString(status)
                  << "\n";
    }
}

void printExperimentPortfolio(const ValidationEngine& engine) {
    printHeading("Experiment prioritization");

    for (const auto& score : engine.rankExperiments()) {
        std::cout << score.experiment->id
                  << " | priority="
                  << std::fixed
                  << std::setprecision(6)
                  << score.priority
                  << " | "
                  << toString(score.hypothesis->status)
                  << "\n";

        std::cout << "  Method: "
                  << score.experiment->method
                  << "\n";

        std::cout << "  Cost: "
                  << score.experiment->cost
                  << " | Duration: "
                  << score.experiment->durationDays
                  << " days"
                  << " | Information gain: "
                  << score.experiment->informationGain
                  << "\n";
    }
}

void printStatusDistribution(const ValidationEngine& engine) {
    printHeading("Hypothesis status distribution");

    std::map<HypothesisStatus, std::size_t> counts;

    for (const auto& [id, hypothesis] : engine.hypotheses()) {
        ++counts[hypothesis.status];
    }

    for (const auto& [status, count] : counts) {
        std::cout << toString(status)
                  << ": "
                  << count
                  << "\n";
    }
}

void demonstrateFailureConditions(ValidationEngine& engine) {
    printHeading("Validation and failure conditions");

    try {
        engine.evaluateHypothesis(
            "H-DES-201",
            std::numeric_limits<double>::quiet_NaN()
        );
    } catch (const std::exception& error) {
        std::cout << "Rejected non-finite measurement: "
                  << error.what()
                  << "\n";
    }

    try {
        engine.addHypothesis({
            "H-BAD",
            "DOES-NOT-EXIST",
            "This intentionally references an unknown assumption.",
            "invalid metric",
            0.5,
            true,
            10
        });
    } catch (const std::exception& error) {
        std::cout << "Rejected broken assumption relationship: "
                  << error.what()
                  << "\n";
    }

    try {
        engine.addExperiment({
            "E-BAD",
            "H-DES-201",
            "This experiment intentionally has an invalid negative cost.",
            -10.0,
            5,
            0.5
        });
    } catch (const std::exception& error) {
        std::cout << "Rejected invalid experiment economics: "
                  << error.what()
                  << "\n";
    }
}

void printDecisionInterpretation(const ValidationEngine& engine) {
    printHeading("Decision interpretation");

    const auto rankedExperiments = engine.rankExperiments();

    if (!rankedExperiments.empty()) {
        const ExperimentScore& highest = rankedExperiments.front();

        std::cout << "Highest information-priority experiment: "
                  << highest.experiment->id
                  << "\n";

        std::cout << "It targets assumption "
                  << highest.assumption->id
                  << " in the "
                  << toString(highest.assumption->dimension)
                  << " dimension."
                  << "\n";
    }

    std::size_t supported = 0;
    std::size_t refuted = 0;

    for (const auto& [id, hypothesis] : engine.hypotheses()) {
        if (hypothesis.status == HypothesisStatus::Supported) {
            ++supported;
        } else if (hypothesis.status == HypothesisStatus::Refuted) {
            ++refuted;
        }
    }

    const std::size_t evaluated = supported + refuted;

    if (evaluated > 0) {
        const double supportRate =
            static_cast<double>(supported) /
            static_cast<double>(evaluated);

        std::cout << "Supported hypotheses among evaluated claims: "
                  << std::fixed
                  << std::setprecision(1)
                  << supportRate * 100.0
                  << "%\n";
    }

    std::cout
        << "A refuted hypothesis does not automatically mean the initiative "
        << "must be abandoned. It identifies a specific assumption whose "
        << "current formulation or threshold failed empirical testing.\n";
}

int main() {
    try {
        std::cout
            << "Assumptions & Hypotheses Decision Engine\n"
            << "----------------------------------------\n";

        ValidationEngine engine;

        populateCaseStudy(engine);
        printExposureAnalysis(engine);
        evaluateCaseStudy(engine);
        printExperimentPortfolio(engine);
        printStatusDistribution(engine);
        demonstrateFailureConditions(engine);
        printDecisionInterpretation(engine);

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
