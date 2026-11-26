#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * EXPERIMENTATION AND CONTROLLED TESTING ENGINE
 *
 * C++17 implementation of an experiment governance system.
 *
 * Implements:
 * - Experiment domain modeling
 * - Hypothesis specification
 * - Randomized assignment
 * - Control and treatment groups
 * - Immutable experiment configuration
 * - Participant observations
 * - Statistical analysis
 * - Guardrail policies
 * - Merge-free experiment lifecycle
 * - Decision and reporting engine
 */

enum class ExperimentState {
    Draft,
    Running,
    Completed,
    Cancelled
};

enum class Group {
    Control,
    Treatment
};

enum class HypothesisDirection {
    Increase,
    Decrease,
    Different
};

enum class Decision {
    Supported,
    Inconclusive,
    Invalid
};


// ---------------------------------------------------------
// 1. DOMAIN STRUCTURES
// ---------------------------------------------------------

struct Hypothesis {
    string researchQuestion;
    string nullHypothesis;
    string alternativeHypothesis;
    string metric;
    HypothesisDirection direction;

    void validate() const {
        if (
            researchQuestion.empty() ||
            nullHypothesis.empty() ||
            alternativeHypothesis.empty() ||
            metric.empty()
        ) {
            throw invalid_argument(
                "Hypothesis fields cannot be empty."
            );
        }
    }
};

struct ExperimentConfig {
    string name;
    Hypothesis hypothesis;

    double alpha = 0.05;
    double power = 0.80;
    double baselineRate = 0.10;
    double treatmentRate = 0.125;

    size_t minimumGroupSize = 30;
    unsigned int seed = 42;

    void validate() const {
        hypothesis.validate();

        if (name.empty()) {
            throw invalid_argument("Experiment name is required.");
        }

        if (!(alpha > 0 && alpha < 1)) {
            throw invalid_argument("Invalid significance level.");
        }

        if (!(power > 0 && power < 1)) {
            throw invalid_argument("Invalid statistical power.");
        }

        if (
            baselineRate < 0 || baselineRate > 1 ||
            treatmentRate < 0 || treatmentRate > 1
        ) {
            throw invalid_argument("Invalid conversion probability.");
        }

        if (baselineRate == 0 || baselineRate == 1) {
            throw invalid_argument(
                "Baseline rate must be strictly between 0 and 1."
            );
        }

        if (minimumGroupSize < 2) {
            throw invalid_argument("Invalid minimum group size.");
        }
    }
};

struct Participant {
    string id;
    Group group;
};

struct Observation {
    string participantId;
    Group group;
    bool converted;
};

struct GroupMetrics {
    size_t participants = 0;
    size_t conversions = 0;
    double conversionRate = 0.0;
};

struct AnalysisResult {
    GroupMetrics control;
    GroupMetrics treatment;

    double absoluteEffect = 0;
    double relativeEffect = 0;
    double zScore = 0;
    double pValue = 0;

    double confidenceLower = 0;
    double confidenceUpper = 0;

    Decision decision = Decision::Inconclusive;
    bool guardrailPassed = true;
};


// ---------------------------------------------------------
// 2. STATISTICAL UTILITIES
// ---------------------------------------------------------

class Statistics {
public:

    static double normalCDF(double x) {
        return 0.5 * erfc(-x / sqrt(2.0));
    }

    static double twoSidedPValue(double z) {
        return erfc(abs(z) / sqrt(2.0));
    }

    static double normalQuantile95() {
        return 1.959963984540054;
    }

    static size_t sampleSize(
        double p1,
        double p2,
        double alpha,
        double power
    ) {
        if (
            p1 <= 0 || p1 >= 1 ||
            p2 <= 0 || p2 >= 1 ||
            p1 == p2
        ) {
            throw invalid_argument(
                "Invalid sample size inputs."
            );
        }

        if (!(alpha > 0 && alpha < 1)) {
            throw invalid_argument("Invalid alpha.");
        }

        if (!(power > 0 && power < 1)) {
            throw invalid_argument("Invalid power.");
        }

        // Common critical values for conventional designs.
        const double zAlpha =
            abs(alpha - 0.05) < 1e-9
                ? 1.959964
                : 2.575829;

        const double zBeta =
            power >= 0.90 ? 1.281552 : 0.841621;

        const double pooled = (p1 + p2) / 2.0;

        const double numerator = pow(
            zAlpha * sqrt(2 * pooled * (1 - pooled))
            + zBeta * sqrt(
                p1 * (1 - p1) + p2 * (1 - p2)
            ),
            2
        );

        return static_cast<size_t>(
            ceil(numerator / pow(p2 - p1, 2))
        );
    }
};


// ---------------------------------------------------------
// 3. GUARDRAIL POLICY
// ---------------------------------------------------------

class GuardrailPolicy {
private:
    double maximumErrorIncrease;

public:
    explicit GuardrailPolicy(double maximumIncrease)
        : maximumErrorIncrease(maximumIncrease) {

        if (maximumIncrease < 0) {
            throw invalid_argument(
                "Guardrail threshold cannot be negative."
            );
        }
    }

    bool evaluate(
        double controlErrorRate,
        double treatmentErrorRate
    ) const {
        if (
            controlErrorRate < 0 || controlErrorRate > 1 ||
            treatmentErrorRate < 0 || treatmentErrorRate > 1
        ) {
            throw invalid_argument("Invalid error rate.");
        }

        return treatmentErrorRate - controlErrorRate
            <= maximumErrorIncrease;
    }
};


// ---------------------------------------------------------
// 4. EXPERIMENT ENGINE
// ---------------------------------------------------------

class ExperimentEngine {
private:
    ExperimentConfig config;
    ExperimentState state = ExperimentState::Draft;

    vector<Participant> participants;
    vector<Observation> observations;

    mt19937 generator;

    GroupMetrics calculateMetrics(Group group) const {
        GroupMetrics metrics;

        for (const auto& observation : observations) {
            if (observation.group != group) {
                continue;
            }

            metrics.participants++;

            if (observation.converted) {
                metrics.conversions++;
            }
        }

        if (metrics.participants > 0) {
            metrics.conversionRate =
                static_cast<double>(metrics.conversions)
                / metrics.participants;
        }

        return metrics;
    }

public:
    explicit ExperimentEngine(ExperimentConfig configuration)
        : config(move(configuration)),
          generator(config.seed) {

        config.validate();
    }

    void start() {
        if (state != ExperimentState::Draft) {
            throw logic_error(
                "Only draft experiments can start."
            );
        }

        state = ExperimentState::Running;
    }

    void cancel() {
        if (
            state != ExperimentState::Draft &&
            state != ExperimentState::Running
        ) {
            throw logic_error(
                "Experiment cannot be cancelled."
            );
        }

        state = ExperimentState::Cancelled;
    }

    size_t estimateSampleSize() const {
        return Statistics::sampleSize(
            config.baselineRate,
            config.treatmentRate,
            config.alpha,
            config.power
        );
    }

    // -----------------------------------------------------
    // 5. RANDOMIZATION
    // -----------------------------------------------------

    void randomizeParticipants(size_t total) {
        if (state != ExperimentState::Running) {
            throw logic_error("Experiment is not running.");
        }

        if (total < 2) {
            throw invalid_argument(
                "At least two participants are required."
            );
        }

        if (!participants.empty()) {
            throw logic_error(
                "Participants have already been assigned."
            );
        }

        vector<Group> assignments;

        assignments.reserve(total);

        for (size_t i = 0; i < total / 2; ++i) {
            assignments.push_back(Group::Control);
            assignments.push_back(Group::Treatment);
        }

        if (total % 2 != 0) {
            uniform_int_distribution<int> distribution(0, 1);

            assignments.push_back(
                distribution(generator) == 0
                    ? Group::Control
                    : Group::Treatment
            );
        }

        shuffle(
            assignments.begin(),
            assignments.end(),
            generator
        );

        for (size_t i = 0; i < total; ++i) {
            participants.push_back({
                "USER-" + to_string(i + 1),
                assignments[i]
            });
        }
    }

    // -----------------------------------------------------
    // 6. EXPERIMENT EXECUTION
    // -----------------------------------------------------

    void execute() {
        if (state != ExperimentState::Running) {
            throw logic_error("Experiment is not running.");
        }

        if (participants.empty()) {
            throw logic_error(
                "No participants have been assigned."
            );
        }

        if (!observations.empty()) {
            throw logic_error(
                "Experiment has already been executed."
            );
        }

        bernoulli_distribution controlDistribution(
            config.baselineRate
        );

        bernoulli_distribution treatmentDistribution(
            config.treatmentRate
        );

        for (const auto& participant : participants) {
            bool converted =
                participant.group == Group::Control
                    ? controlDistribution(generator)
                    : treatmentDistribution(generator);

            observations.push_back({
                participant.id,
                participant.group,
                converted
            });
        }
    }

    // -----------------------------------------------------
    // 7. INTEGRITY VALIDATION
    // -----------------------------------------------------

    bool validateAssignments() const {
        map<string, bool> identifiers;

        for (const auto& participant : participants) {
            if (participant.id.empty()) {
                return false;
            }

            if (identifiers.count(participant.id)) {
                return false;
            }

            identifiers[participant.id] = true;
        }

        return true;
    }

    bool validateObservations() const {
        if (observations.size() != participants.size()) {
            return false;
        }

        map<string, Group> assigned;

        for (const auto& participant : participants) {
            assigned[participant.id] = participant.group;
        }

        map<string, bool> observed;

        for (const auto& observation : observations) {
            auto found = assigned.find(
                observation.participantId
            );

            if (
                found == assigned.end() ||
                found->second != observation.group ||
                observed.count(observation.participantId)
            ) {
                return false;
            }

            observed[observation.participantId] = true;
        }

        return true;
    }

    // -----------------------------------------------------
    // 8. MERGE-FREE STATISTICAL ANALYSIS
    // -----------------------------------------------------

    AnalysisResult analyze(
        const GuardrailPolicy& guardrail,
        double controlErrorRate,
        double treatmentErrorRate
    ) {
        if (state != ExperimentState::Running) {
            throw logic_error(
                "Only running experiments can be analyzed."
            );
        }

        if (
            !validateAssignments() ||
            !validateObservations()
        ) {
            throw logic_error(
                "Experiment data integrity validation failed."
            );
        }

        AnalysisResult result;

        result.control = calculateMetrics(Group::Control);
        result.treatment = calculateMetrics(Group::Treatment);

        if (
            result.control.participants < config.minimumGroupSize ||
            result.treatment.participants < config.minimumGroupSize
        ) {
            throw runtime_error("Insufficient group size.");
        }

        const double p1 = result.control.conversionRate;
        const double p2 = result.treatment.conversionRate;

        const double pooled =
            static_cast<double>(
                result.control.conversions +
                result.treatment.conversions
            ) /
            (
                result.control.participants +
                result.treatment.participants
            );

        const double standardError = sqrt(
            pooled * (1 - pooled) *
            (
                1.0 / result.control.participants +
                1.0 / result.treatment.participants
            )
        );

        if (standardError <= 0) {
            throw runtime_error(
                "Cannot calculate statistical significance."
            );
        }

        result.absoluteEffect = p2 - p1;

        result.relativeEffect = p1 > 0
            ? result.absoluteEffect / p1
            : 0;

        result.zScore =
            result.absoluteEffect / standardError;

        result.pValue =
            Statistics::twoSidedPValue(result.zScore);

        const double confidenceError =
            Statistics::normalQuantile95() * sqrt(
                p1 * (1 - p1) / result.control.participants
                + p2 * (1 - p2) / result.treatment.participants
            );

        result.confidenceLower =
            result.absoluteEffect - confidenceError;

        result.confidenceUpper =
            result.absoluteEffect + confidenceError;

        result.guardrailPassed = guardrail.evaluate(
            controlErrorRate,
            treatmentErrorRate
        );

        bool favorable = false;

        switch (config.hypothesis.direction) {
            case HypothesisDirection::Increase:
                favorable = result.absoluteEffect > 0;
                break;

            case HypothesisDirection::Decrease:
                favorable = result.absoluteEffect < 0;
                break;

            case HypothesisDirection::Different:
                favorable = true;
                break;
        }

        if (!result.guardrailPassed) {
            result.decision = Decision::Invalid;
        } else if (
            result.pValue < config.alpha && favorable
        ) {
            result.decision = Decision::Supported;
        } else {
            result.decision = Decision::Inconclusive;
        }

        state = ExperimentState::Completed;

        return result;
    }

    ExperimentState getState() const {
        return state;
    }

    const vector<Participant>& getParticipants() const {
        return participants;
    }
};


// ---------------------------------------------------------
// 9. REPORTING
// ---------------------------------------------------------

string decisionName(Decision decision) {
    switch (decision) {
        case Decision::Supported:
            return "REJECT_NULL_HYPOTHESIS";

        case Decision::Inconclusive:
            return "FAIL_TO_REJECT_NULL";

        case Decision::Invalid:
            return "INVALID_EXPERIMENT";
    }

    return "UNKNOWN";
}

void printReport(const AnalysisResult& result) {
    cout << fixed << setprecision(6);

    cout << "\nEXPERIMENT REPORT\n";
    cout << "-----------------\n";

    cout << "Control participants: "
         << result.control.participants << '\n';

    cout << "Treatment participants: "
         << result.treatment.participants << '\n';

    cout << "Control conversion rate: "
         << result.control.conversionRate << '\n';

    cout << "Treatment conversion rate: "
         << result.treatment.conversionRate << '\n';

    cout << "Absolute effect: "
         << result.absoluteEffect << '\n';

    cout << "Relative effect: "
         << result.relativeEffect << '\n';

    cout << "Z-score: "
         << result.zScore << '\n';

    cout << "P-value: "
         << result.pValue << '\n';

    cout << "95% confidence interval: ["
         << result.confidenceLower << ", "
         << result.confidenceUpper << "]\n";

    cout << "Guardrail passed: "
         << boolalpha << result.guardrailPassed << '\n';

    cout << "Decision: "
         << decisionName(result.decision) << '\n';
}


// ---------------------------------------------------------
// 10. MAIN
// ---------------------------------------------------------

int main() {
    try {
        Hypothesis hypothesis{
            "Does a redesigned checkout improve purchases?",
            "The redesigned checkout does not change conversion.",
            "The redesigned checkout increases conversion.",
            "purchase_conversion",
            HypothesisDirection::Increase
        };

        ExperimentConfig config{
            "Checkout Optimization",
            hypothesis,
            0.05,
            0.80,
            0.10,
            0.125,
            30,
            42
        };

        ExperimentEngine engine(config);

        cout << "EXPERIMENT: " << config.name << '\n';

        cout << "Estimated sample size per group: "
             << engine.estimateSampleSize() << '\n';

        engine.start();

        engine.randomizeParticipants(2000);

        engine.execute();

        GuardrailPolicy policy(0.01);

        AnalysisResult result = engine.analyze(
            policy,
            0.02,
            0.021
        );

        printReport(result);

        cout << "\nExperiment state: "
             << (
                 engine.getState() == ExperimentState::Completed
                     ? "COMPLETED"
                     : "NOT COMPLETED"
             )
             << '\n';

        // Edge case: invalid configuration.
        try {
            ExperimentConfig invalid = config;
            invalid.alpha = 2.0;
            invalid.validate();
        } catch (const exception& error) {
            cout << "\nValidation test: "
                 << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Experiment failure: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
