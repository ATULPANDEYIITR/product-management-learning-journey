#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class MetricType {
    PRIMARY,
    SECONDARY,
    GUARDRAIL
};

enum class ExperimentState {
    DRAFT,
    RUNNING,
    COMPLETED,
    INVALID
};

enum class Decision {
    SHIP,
    DO_NOT_SHIP,
    INCONCLUSIVE
};

string toString(Decision decision) {
    switch (decision) {
        case Decision::SHIP: return "SHIP";
        case Decision::DO_NOT_SHIP: return "DO_NOT_SHIP";
        case Decision::INCONCLUSIVE: return "INCONCLUSIVE";
    }
    throw runtime_error("Unknown decision");
}

struct MetricDefinition {
    string name;
    MetricType type;
    string unit;
    bool higherIsBetter;
};

struct ExperimentConfig {
    string id;
    string name;
    double baselineConversion;
    double relativeMDE;
    double alpha = 0.05;
    double power = 0.80;
    size_t minimumSampleSize = 100;
    size_t maximumSampleSize = 1000000;

    void validate() const {
        if (id.empty() || name.empty()) {
            throw invalid_argument("Experiment identity is required");
        }

        if (!(baselineConversion > 0 && baselineConversion < 1)) {
            throw invalid_argument("Invalid baseline conversion");
        }

        if (!(relativeMDE > 0 && relativeMDE < 1)) {
            throw invalid_argument("Invalid MDE");
        }

        if (!(alpha > 0 && alpha < 1)) {
            throw invalid_argument("Invalid significance level");
        }

        if (!(power > 0 && power < 1)) {
            throw invalid_argument("Invalid statistical power");
        }

        if (minimumSampleSize < 2 ||
            maximumSampleSize < minimumSampleSize) {
            throw invalid_argument("Invalid sample-size limits");
        }

        if (baselineConversion * (1 + relativeMDE) >= 1) {
            throw invalid_argument("Treatment probability exceeds 1");
        }
    }
};

struct UserObservation {
    string userId;
    bool converted = false;
    double revenue = 0;
    bool refunded = false;
    double latency = 0;
};

struct ExperimentGroup {
    string name;
    vector<UserObservation> observations;

    size_t users() const {
        return observations.size();
    }

    size_t conversions() const {
        return count_if(
            observations.begin(),
            observations.end(),
            [](const auto& item) {
                return item.converted;
            }
        );
    }

    size_t refunds() const {
        return count_if(
            observations.begin(),
            observations.end(),
            [](const auto& item) {
                return item.refunded;
            }
        );
    }

    vector<double> revenue() const {
        vector<double> values;

        for (const auto& item : observations) {
            if (item.converted) {
                values.push_back(item.revenue);
            }
        }

        return values;
    }

    vector<double> latency() const {
        vector<double> values;

        for (const auto& item : observations) {
            values.push_back(item.latency);
        }

        return values;
    }

    double conversionRate() const {
        if (users() == 0) {
            throw runtime_error("Empty experiment group");
        }

        return static_cast<double>(conversions()) / users();
    }

    double refundRate() const {
        if (conversions() == 0) {
            return 0;
        }

        return static_cast<double>(refunds()) / conversions();
    }
};

class SampleSizeCalculator {
public:
    static double inverseNormal(double p) {
        if (!(p > 0 && p < 1)) {
            throw invalid_argument("Invalid probability");
        }

        const double a[] = {
            -39.6968302866538, 220.946098424521,
            -275.928510446969, 138.357751867269,
            -30.6647980661472, 2.50662827745924
        };

        const double b[] = {
            -54.4760987982241, 161.585836858041,
            -155.698979859887, 66.8013118877197,
            -13.2806815528857
        };

        const double c[] = {
            -0.00778489400243029, -0.322396458041136,
            -2.40075827716184, -2.54973253934373,
            4.37466414146497, 2.93816398269878
        };

        const double d[] = {
            0.00778469570904146, 0.32246712907004,
            2.445134137143, 3.75440866190742
        };

        if (p < 0.02425) {
            double q = sqrt(-2 * log(p));

            return (((((c[0] * q + c[1]) * q + c[2]) * q +
                c[3]) * q + c[4]) * q + c[5]) /
                ((((d[0] * q + d[1]) * q + d[2]) * q +
                    d[3]) * q + 1);
        }

        if (p > 0.97575) {
            return -inverseNormal(1 - p);
        }

        double q = p - 0.5;
        double r = q * q;

        return (((((a[0] * r + a[1]) * r + a[2]) * r +
            a[3]) * r + a[4]) * r + a[5]) * q /
            (((((b[0] * r + b[1]) * r + b[2]) * r +
                b[3]) * r + b[4]) * r) + 1);
    }

    static size_t calculate(const ExperimentConfig& config) {
        config.validate();

        double p1 = config.baselineConversion;
        double p2 = p1 * (1 + config.relativeMDE);
        double pooled = (p1 + p2) / 2;
        double difference = p2 - p1;

        double zAlpha = inverseNormal(1 - config.alpha / 2);
        double zPower = inverseNormal(config.power);

        double numerator = pow(
            zAlpha * sqrt(2 * pooled * (1 - pooled)) +
            zPower * sqrt(
                p1 * (1 - p1) + p2 * (1 - p2)
            ),
            2
        );

        size_t required = static_cast<size_t>(
            ceil(numerator / (difference * difference))
        );

        return min(
            max(required, config.minimumSampleSize),
            config.maximumSampleSize
        );
    }
};

class StatisticalAnalyzer {
public:
    static double normalCDF(double z) {
        return 0.5 * erfc(-z / sqrt(2.0));
    }

    static double proportionPValue(
        size_t x1,
        size_t n1,
        size_t x2,
        size_t n2
    ) {
        if (n1 == 0 || n2 == 0 ||
            x1 > n1 || x2 > n2) {
            throw invalid_argument("Invalid proportion inputs");
        }

        double p1 = static_cast<double>(x1) / n1;
        double p2 = static_cast<double>(x2) / n2;

        double pooled = static_cast<double>(x1 + x2) /
                        (n1 + n2);

        double se = sqrt(
            pooled * (1 - pooled) *
            (1.0 / n1 + 1.0 / n2)
        );

        if (se == 0) {
            return p1 == p2 ? 1.0 : 0.0;
        }

        double z = (p2 - p1) / se;

        return 2 * (1 - normalCDF(abs(z)));
    }

    static double mean(const vector<double>& values) {
        if (values.empty()) {
            return 0;
        }

        return accumulate(
            values.begin(), values.end(), 0.0
        ) / values.size();
    }

    static double percentile(
        vector<double> values,
        double fraction
    ) {
        if (values.empty() ||
            fraction < 0 || fraction > 1) {
            throw invalid_argument("Invalid percentile input");
        }

        sort(values.begin(), values.end());

        double position = fraction * (values.size() - 1);
        size_t lower = static_cast<size_t>(floor(position));
        size_t upper = static_cast<size_t>(ceil(position));

        double weight = position - lower;

        return values[lower] * (1 - weight) +
               values[upper] * weight;
    }

    static double welchNormalPValue(
        const vector<double>& a,
        const vector<double>& b
    ) {
        if (a.size() < 2 || b.size() < 2) {
            return -1;
        }

        auto variance = [](const vector<double>& values) {
            double average = mean(values);
            double sum = 0;

            for (double value : values) {
                sum += pow(value - average, 2);
            }

            return sum / (values.size() - 1);
        };

        double difference = mean(b) - mean(a);

        double se = sqrt(
            variance(a) / a.size() +
            variance(b) / b.size()
        );

        if (se == 0) {
            return difference == 0 ? 1.0 : 0.0;
        }

        double z = difference / se;

        return 2 * (1 - normalCDF(abs(z)));
    }
};

class TrafficAllocator {
    string experimentId;

public:
    explicit TrafficAllocator(string id)
        : experimentId(std::move(id)) {}

    string assign(const string& userId) const {
        if (userId.empty()) {
            throw invalid_argument("User ID cannot be empty");
        }

        // FNV-1a provides deterministic allocation for this simulation.
        // Production assignment should use a stable cryptographic hash.
        uint64_t hash = 14695981039346656037ULL;

        string input = experimentId + ":" + userId;

        for (unsigned char character : input) {
            hash ^= character;
            hash *= 1099511628211ULL;
        }

        return hash % 2 == 0 ? "control" : "treatment";
    }
};

class ExperimentSimulator {
public:
    static pair<ExperimentGroup, ExperimentGroup> simulate(
        const ExperimentConfig& config,
        size_t totalUsers,
        unsigned seed = 42
    ) {
        config.validate();

        if (totalUsers < 2) {
            throw invalid_argument("Insufficient users");
        }

        mt19937 generator(seed);

        uniform_real_distribution<double> uniform(0, 1);
        normal_distribution<double> normal(0, 1);
        lognormal_distribution<double> revenue(3.5, 0.6);

        TrafficAllocator allocator(config.id);

        ExperimentGroup control{"control", {}};
        ExperimentGroup treatment{"treatment", {}};

        for (size_t i = 0; i < totalUsers; ++i) {
            string userId = "user-" + to_string(i);

            string variant = allocator.assign(userId);

            ExperimentGroup& group =
                variant == "control" ? control : treatment;

            double probability =
                variant == "control"
                ? config.baselineConversion
                : config.baselineConversion *
                  (1 + config.relativeMDE);

            bool converted = uniform(generator) < probability;

            double generatedRevenue =
                converted ? revenue(generator) : 0;

            bool refunded =
                converted && uniform(generator) < 0.035;

            double baseLatency =
                variant == "control" ? 180 : 190;

            double latency = max(
                1.0,
                baseLatency + normal(generator) * 25
            );

            group.observations.push_back({
                userId,
                converted,
                generatedRevenue,
                refunded,
                latency
            });
        }

        return {control, treatment};
    }
};

struct EvaluationPolicy {
    double minimumConversionImprovement = 0;
    double maximumRefundIncrease = 0.02;
    double maximumP95LatencyIncrease = 40;
    double alpha = 0.05;
};

struct EvaluationReport {
    Decision decision;
    double controlConversion;
    double treatmentConversion;
    double pValue;
    double revenueControl;
    double revenueTreatment;
    double controlRefundRate;
    double treatmentRefundRate;
    double controlP95;
    double treatmentP95;
    bool sampleSufficient;
    bool refundGuardrail;
    bool latencyGuardrail;
};

class GovernanceEngine {
    EvaluationPolicy policy;

public:
    explicit GovernanceEngine(EvaluationPolicy p)
        : policy(p) {
        if (!(p.alpha > 0 && p.alpha < 1) ||
            p.maximumRefundIncrease < 0 ||
            p.maximumP95LatencyIncrease < 0) {
            throw invalid_argument("Invalid evaluation policy");
        }
    }

    EvaluationReport evaluate(
        const ExperimentGroup& control,
        const ExperimentGroup& treatment,
        size_t requiredPerGroup
    ) const {
        if (control.users() == 0 || treatment.users() == 0) {
            throw runtime_error("Empty experiment group");
        }

        double cRate = control.conversionRate();
        double tRate = treatment.conversionRate();

        double pValue = StatisticalAnalyzer::proportionPValue(
            control.conversions(),
            control.users(),
            treatment.conversions(),
            treatment.users()
        );

        double cRefund = control.refundRate();
        double tRefund = treatment.refundRate();

        double cP95 = StatisticalAnalyzer::percentile(
            control.latency(), 0.95
        );

        double tP95 = StatisticalAnalyzer::percentile(
            treatment.latency(), 0.95
        );

        double cRevenue = StatisticalAnalyzer::mean(
            control.revenue()
        );

        double tRevenue = StatisticalAnalyzer::mean(
            treatment.revenue()
        );

        bool sufficient =
            control.users() >= requiredPerGroup &&
            treatment.users() >= requiredPerGroup;

        bool refundPass =
            tRefund - cRefund <= policy.maximumRefundIncrease;

        bool latencyPass =
            tP95 - cP95 <= policy.maximumP95LatencyIncrease;

        Decision decision;

        if (!sufficient) {
            decision = Decision::INCONCLUSIVE;
        } else if (!refundPass || !latencyPass) {
            decision = Decision::DO_NOT_SHIP;
        } else if (
            pValue < policy.alpha &&
            tRate - cRate >
            policy.minimumConversionImprovement
        ) {
            decision = Decision::SHIP;
        } else {
            decision = Decision::INCONCLUSIVE;
        }

        return {
            decision,
            cRate,
            tRate,
            pValue,
            cRevenue,
            tRevenue,
            cRefund,
            tRefund,
            cP95,
            tP95,
            sufficient,
            refundPass,
            latencyPass
        };
    }
};

class ExperimentLifecycle {
    ExperimentState state = ExperimentState::DRAFT;

public:
    void transition(ExperimentState next) {
        bool valid = false;

        switch (state) {
            case ExperimentState::DRAFT:
                valid = next == ExperimentState::RUNNING ||
                        next == ExperimentState::INVALID;
                break;

            case ExperimentState::RUNNING:
                valid = next == ExperimentState::COMPLETED ||
                        next == ExperimentState::INVALID;
                break;

            case ExperimentState::COMPLETED:
            case ExperimentState::INVALID:
                valid = false;
                break;
        }

        if (!valid) {
            throw logic_error("Invalid experiment transition");
        }

        state = next;
    }

    ExperimentState current() const {
        return state;
    }
};

int main() {
    try {
        ExperimentConfig config{
            "EXP-001",
            "Checkout Redesign",
            0.10,
            0.10,
            0.05,
            0.80,
            100,
            1000000
        };

        config.validate();

        size_t required = SampleSizeCalculator::calculate(config);

        cout << fixed << setprecision(4);

        cout << "EXPERIMENT CONFIGURATION\n";
        cout << "------------------------\n";
        cout << "Name: " << config.name << '\n';
        cout << "Baseline conversion: "
             << config.baselineConversion * 100 << "%\n";
        cout << "Relative MDE: "
             << config.relativeMDE * 100 << "%\n";
        cout << "Alpha: " << config.alpha << '\n';
        cout << "Power: " << config.power << '\n';
        cout << "Required users per group: " << required << "\n\n";

        ExperimentLifecycle lifecycle;
        lifecycle.transition(ExperimentState::RUNNING);

        auto groups = ExperimentSimulator::simulate(
            config,
            required * 2,
            42
        );

        EvaluationPolicy policy{
            0.0,
            0.02,
            40.0,
            config.alpha
        };

        GovernanceEngine engine(policy);

        EvaluationReport report = engine.evaluate(
            groups.first,
            groups.second,
            required
        );

        cout << "EXPERIMENT RESULTS\n";
        cout << "------------------\n";

        cout << "Control users: "
             << groups.first.users() << '\n';

        cout << "Treatment users: "
             << groups.second.users() << '\n';

        cout << "Control conversion: "
             << report.controlConversion * 100 << "%\n";

        cout << "Treatment conversion: "
             << report.treatmentConversion * 100 << "%\n";

        cout << "Absolute improvement: "
             << (report.treatmentConversion -
                 report.controlConversion) * 100
             << " percentage points\n";

        cout << "P-value: " << report.pValue << '\n';

        cout << "\nSECONDARY METRIC\n";
        cout << "Control revenue per conversion: "
             << report.revenueControl << '\n';

        cout << "Treatment revenue per conversion: "
             << report.revenueTreatment << '\n';

        cout << "\nGUARDRAILS\n";

        cout << "Refund rate control: "
             << report.controlRefundRate * 100 << "%\n";

        cout << "Refund rate treatment: "
             << report.treatmentRefundRate * 100 << "%\n";

        cout << "Refund guardrail: "
             << (report.refundGuardrail ? "PASS" : "FAIL")
             << '\n';

        cout << "Control p95 latency: "
             << report.controlP95 << " ms\n";

        cout << "Treatment p95 latency: "
             << report.treatmentP95 << " ms\n";

        cout << "Latency guardrail: "
             << (report.latencyGuardrail ? "PASS" : "FAIL")
             << '\n';

        cout << "\nFINAL DECISION\n";
        cout << toString(report.decision) << '\n';

        lifecycle.transition(ExperimentState::COMPLETED);

        cout << "Lifecycle: COMPLETED\n";

        // Validate edge cases.
        if (SampleSizeCalculator::calculate(config) == 0) {
            throw runtime_error("Invalid calculated sample size");
        }

        if (abs(
            TrafficAllocator(config.id).assign("user-1") ==
            TrafficAllocator(config.id).assign("user-1")
            ? 1 : 0
        ) != 1) {
            throw runtime_error("Assignment consistency failed");
        }

        cout << "\nValidation completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Experiment error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
