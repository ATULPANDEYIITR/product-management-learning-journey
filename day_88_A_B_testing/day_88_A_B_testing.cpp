#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

enum class ExperimentState {
    Draft,
    Running,
    Completed,
    Stopped
};

enum class Group {
    Control,
    Treatment
};

struct Participant {
    string id;
    Group group;
    bool converted;
};

struct GroupMetrics {
    size_t total = 0;
    size_t conversions = 0;

    double conversionRate() const {
        if (total == 0) {
            return 0.0;
        }

        return static_cast<double>(conversions) / total;
    }
};

struct StatisticalResult {
    double controlRate;
    double treatmentRate;
    double absoluteLift;
    double relativeLift;
    double zScore;
    double pValue;
    double confidenceLow;
    double confidenceHigh;
    bool significant;
};

struct GovernancePolicy {
    double significanceLevel = 0.05;
    double minimumEffect = 0.01;
    size_t minimumGroupSize = 100;
};

class Randomizer {
private:
    mt19937_64 engine;

public:
    explicit Randomizer(uint64_t seed) : engine(seed) {}

    Group assign(double controlRatio) {
        bernoulli_distribution distribution(controlRatio);

        return distribution(engine)
            ? Group::Control
            : Group::Treatment;
    }

    bool convert(double probability) {
        bernoulli_distribution distribution(probability);
        return distribution(engine);
    }
};

class ABTestEngine {
private:
    string experimentName;
    ExperimentState state;
    double controlProbability;
    double treatmentProbability;
    double allocationRatio;
    GovernancePolicy policy;

    Randomizer randomizer;

    vector<Participant> participants;
    unordered_set<string> participantIds;

    GroupMetrics controlMetrics;
    GroupMetrics treatmentMetrics;

    static double normalCDF(double x) {
        return 0.5 * erfc(-x / sqrt(2.0));
    }

    static double twoSidedPValue(double z) {
        return erfc(abs(z) / sqrt(2.0));
    }

    void validateProbability(double value, const string& name) const {
        if (!isfinite(value) || value <= 0.0 || value >= 1.0) {
            throw invalid_argument(name + " must be between 0 and 1.");
        }
    }

public:
    ABTestEngine(
        string name,
        double controlRate,
        double treatmentRate,
        double allocation,
        GovernancePolicy governance,
        uint64_t seed
    )
        : experimentName(move(name)),
          state(ExperimentState::Draft),
          controlProbability(controlRate),
          treatmentProbability(treatmentRate),
          allocationRatio(allocation),
          policy(governance),
          randomizer(seed) {

        if (experimentName.empty()) {
            throw invalid_argument("Experiment name is required.");
        }

        validateProbability(controlRate, "Control probability");
        validateProbability(treatmentRate, "Treatment probability");
        validateProbability(allocation, "Allocation ratio");
        validateProbability(
            governance.significanceLevel,
            "Significance level"
        );

        if (governance.minimumEffect < 0.0 ||
            governance.minimumGroupSize == 0) {
            throw invalid_argument("Invalid governance policy.");
        }
    }

    void start() {
        if (state != ExperimentState::Draft) {
            throw logic_error("Experiment cannot be started.");
        }

        state = ExperimentState::Running;
    }

    Participant assign(const string& id) {
        if (state != ExperimentState::Running) {
            throw logic_error("Experiment is not running.");
        }

        if (id.empty()) {
            throw invalid_argument("Participant ID is required.");
        }

        if (participantIds.count(id)) {
            throw invalid_argument("Duplicate participant assignment.");
        }

        Group group = randomizer.assign(allocationRatio);

        double probability =
            group == Group::Control
            ? controlProbability
            : treatmentProbability;

        Participant participant{
            id,
            group,
            randomizer.convert(probability)
        };

        participants.push_back(participant);
        participantIds.insert(id);

        GroupMetrics& metrics =
            group == Group::Control
            ? controlMetrics
            : treatmentMetrics;

        metrics.total++;

        if (participant.converted) {
            metrics.conversions++;
        }

        return participant;
    }

    StatisticalResult evaluate() const {
        if (
            state != ExperimentState::Running &&
            state != ExperimentState::Completed &&
            state != ExperimentState::Stopped
        ) {
            throw logic_error("Experiment has not started.");
        }

        if (
            controlMetrics.total == 0 ||
            treatmentMetrics.total == 0
        ) {
            throw logic_error("Both groups require participants.");
        }

        const double p1 = controlMetrics.conversionRate();
        const double p2 = treatmentMetrics.conversionRate();

        const double pooled =
            static_cast<double>(
                controlMetrics.conversions +
                treatmentMetrics.conversions
            ) /
            (controlMetrics.total + treatmentMetrics.total);

        const double pooledSE = sqrt(
            pooled * (1.0 - pooled) *
            (
                1.0 / controlMetrics.total +
                1.0 / treatmentMetrics.total
            )
        );

        const double z =
            pooledSE == 0.0 ? 0.0 : (p2 - p1) / pooledSE;

        const double pValue =
            pooledSE == 0.0 ? 1.0 : twoSidedPValue(z);

        const double difference = p2 - p1;

        const double unpooledSE = sqrt(
            p1 * (1.0 - p1) / controlMetrics.total +
            p2 * (1.0 - p2) / treatmentMetrics.total
        );

        // Two-sided 95% normal confidence interval.
        constexpr double critical = 1.959963984540054;

        return {
            p1,
            p2,
            difference,
            p1 == 0.0 ? 0.0 : difference / p1,
            z,
            pValue,
            difference - critical * unpooledSE,
            difference + critical * unpooledSE,
            pValue < policy.significanceLevel
        };
    }

    string decision() const {
        if (
            controlMetrics.total < policy.minimumGroupSize ||
            treatmentMetrics.total < policy.minimumGroupSize
        ) {
            return "INSUFFICIENT_SAMPLE";
        }

        const auto result = evaluate();

        if (!result.significant) {
            return "INCONCLUSIVE";
        }

        if (
            result.absoluteLift > 0.0 &&
            result.absoluteLift >= policy.minimumEffect
        ) {
            return "TREATMENT_WINS";
        }

        if (result.absoluteLift < 0.0) {
            return "CONTROL_WINS";
        }

        return "SIGNIFICANT_WITHOUT_PRACTICAL_WIN";
    }

    void complete() {
        if (state != ExperimentState::Running) {
            throw logic_error("Only running experiments can complete.");
        }

        state = ExperimentState::Completed;
    }

    void stop() {
        if (state != ExperimentState::Running) {
            throw logic_error("Only running experiments can stop.");
        }

        state = ExperimentState::Stopped;
    }

    void printReport() const {
        const auto result = evaluate();

        cout << "\n========================================\n";
        cout << "A/B TESTING GOVERNANCE REPORT\n";
        cout << "========================================\n";

        cout << "Experiment: " << experimentName << '\n';

        cout << fixed << setprecision(4);

        cout << "\nCONTROL GROUP\n";
        cout << "Participants: " << controlMetrics.total << '\n';
        cout << "Conversions: " << controlMetrics.conversions << '\n';
        cout << "Conversion rate: "
             << result.controlRate * 100.0 << "%\n";

        cout << "\nTREATMENT GROUP\n";
        cout << "Participants: " << treatmentMetrics.total << '\n';
        cout << "Conversions: " << treatmentMetrics.conversions << '\n';
        cout << "Conversion rate: "
             << result.treatmentRate * 100.0 << "%\n";

        cout << "\nSTATISTICAL EVALUATION\n";
        cout << "Absolute lift: "
             << result.absoluteLift * 100.0 << "%\n";

        cout << "Relative lift: "
             << result.relativeLift * 100.0 << "%\n";

        cout << "Z-score: " << result.zScore << '\n';
        cout << "P-value: " << result.pValue << '\n';

        cout << "95% confidence interval: ["
             << result.confidenceLow * 100.0 << "%, "
             << result.confidenceHigh * 100.0 << "%]\n";

        cout << "Statistically significant: "
             << (result.significant ? "YES" : "NO") << '\n';

        cout << "Decision: " << decision() << '\n';
    }

    const vector<Participant>& getParticipants() const {
        return participants;
    }
};

size_t requiredSampleSize(
    double baseline,
    double effect,
    double alpha = 0.05,
    double power = 0.80
) {
    if (
        baseline <= 0.0 ||
        baseline >= 1.0 ||
        effect <= 0.0 ||
        baseline + effect >= 1.0 ||
        alpha <= 0.0 ||
        alpha >= 1.0 ||
        power <= 0.0 ||
        power >= 1.0
    ) {
        throw invalid_argument("Invalid sample-size parameters.");
    }

    // Bisection-based inverse standard normal CDF.
    auto inverseNormal = [](double p) {
        double low = -8.0;
        double high = 8.0;

        for (int i = 0; i < 120; ++i) {
            double mid = (low + high) / 2.0;
            double cdf = 0.5 * erfc(-mid / sqrt(2.0));

            if (cdf < p) {
                low = mid;
            } else {
                high = mid;
            }
        }

        return (low + high) / 2.0;
    };

    const double p2 = baseline + effect;
    const double average = (baseline + p2) / 2.0;

    const double za = inverseNormal(1.0 - alpha / 2.0);
    const double zb = inverseNormal(power);

    const double numerator = pow(
        za * sqrt(2.0 * average * (1.0 - average)) +
        zb * sqrt(
            baseline * (1.0 - baseline) +
            p2 * (1.0 - p2)
        ),
        2
    );

    return static_cast<size_t>(
        ceil(numerator / (effect * effect))
    );
}

void runTests() {
    GovernancePolicy policy;
    policy.minimumGroupSize = 1;

    ABTestEngine experiment(
        "Validation",
        0.10,
        0.12,
        0.50,
        policy,
        123
    );

    experiment.start();

    experiment.assign("participant-1");

    try {
        experiment.assign("participant-1");
        throw runtime_error("Duplicate assignment was accepted.");
    } catch (const invalid_argument&) {
        // Expected validation behavior.
    }

    const size_t sample = requiredSampleSize(0.10, 0.02);

    if (sample == 0) {
        throw runtime_error("Sample-size calculation failed.");
    }

    bool invalidRejected = false;

    try {
        ABTestEngine invalid(
            "Invalid",
            1.5,
            0.12,
            0.50,
            policy,
            42
        );
    } catch (const invalid_argument&) {
        invalidRejected = true;
    }

    if (!invalidRejected) {
        throw runtime_error("Invalid configuration was accepted.");
    }

    cout << "All C++17 validation tests passed.\n";
}

int main() {
    try {
        runTests();

        GovernancePolicy policy;
        policy.significanceLevel = 0.05;
        policy.minimumEffect = 0.01;
        policy.minimumGroupSize = 100;

        ABTestEngine experiment(
            "E-Commerce Checkout Experiment",
            0.10,
            0.12,
            0.50,
            policy,
            2026
        );

        experiment.start();

        for (int i = 1; i <= 20000; ++i) {
            experiment.assign("user-" + to_string(i));
        }

        experiment.complete();
        experiment.printReport();

        cout << "\nSAMPLE SIZE PLANNING\n";
        cout << "Required participants per group: "
             << requiredSampleSize(0.10, 0.02)
             << '\n';

    } catch (const exception& error) {
        cerr << "Experiment error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
