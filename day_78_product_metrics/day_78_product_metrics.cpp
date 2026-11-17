#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * PRODUCT METRICS GOVERNANCE AND EVALUATION ENGINE
 *
 * Implements:
 * - North Star Metric evaluation
 * - Input and output metric classification
 * - Guardrail threshold enforcement
 * - Metric observation validation
 * - Period comparisons
 * - Product growth diagnosis
 * - Data quality checks
 * - Experiment lift calculation
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic product_metrics.cpp -o product_metrics
 *
 * Run:
 * ./product_metrics
 */

enum class MetricCategory {
    NorthStar,
    Input,
    Output,
    Guardrail
};

enum class Direction {
    Higher,
    Lower,
    Range
};

enum class MetricStatus {
    OnTrack,
    BelowTarget,
    AboveLimit,
    BelowRange,
    AboveRange,
    Missing
};

enum class Severity {
    Info,
    Warning,
    Critical
};

std::string toString(MetricCategory category) {
    switch (category) {
        case MetricCategory::NorthStar: return "North Star";
        case MetricCategory::Input: return "Input";
        case MetricCategory::Output: return "Output";
        case MetricCategory::Guardrail: return "Guardrail";
    }
    throw std::logic_error("Unknown metric category");
}

std::string toString(MetricStatus status) {
    switch (status) {
        case MetricStatus::OnTrack: return "ON TRACK";
        case MetricStatus::BelowTarget: return "BELOW TARGET";
        case MetricStatus::AboveLimit: return "ABOVE LIMIT";
        case MetricStatus::BelowRange: return "BELOW RANGE";
        case MetricStatus::AboveRange: return "ABOVE RANGE";
        case MetricStatus::Missing: return "MISSING";
    }
    throw std::logic_error("Unknown metric status");
}

struct MetricDefinition {
    std::string name;
    MetricCategory category;
    std::string unit;
    Direction direction;

    std::optional<double> target;
    std::optional<double> minimum;
    std::optional<double> maximum;

    void validate() const {
        if (name.empty()) {
            throw std::invalid_argument("Metric name cannot be empty");
        }

        for (const auto& value : {
            target, minimum, maximum
        }) {
            if (value.has_value()) {
                if (!std::isfinite(*value) || *value < 0) {
                    throw std::invalid_argument(
                        "Threshold must be finite and non-negative"
                    );
                }
            }
        }

        if (
            minimum.has_value() &&
            maximum.has_value() &&
            *minimum > *maximum
        ) {
            throw std::invalid_argument(
                "Minimum exceeds maximum"
            );
        }
    }
};

struct Observation {
    std::string metricName;
    std::string period;
    double value;
    std::size_t sampleSize;
};

struct MetricEvaluation {
    MetricDefinition definition;
    double current;
    std::optional<double> previous;
    std::optional<double> changePercent;
    MetricStatus status;
};

struct Alert {
    std::string metricName;
    Severity severity;
    std::string message;
};

class MetricRegistry {
private:
    std::map<std::string, MetricDefinition> definitions;

public:
    void registerMetric(const MetricDefinition& definition) {
        definition.validate();

        if (definitions.count(definition.name)) {
            throw std::invalid_argument(
                "Duplicate metric: " + definition.name
            );
        }

        definitions.emplace(definition.name, definition);
    }

    const MetricDefinition& get(
        const std::string& name
    ) const {
        auto it = definitions.find(name);

        if (it == definitions.end()) {
            throw std::invalid_argument(
                "Unknown metric: " + name
            );
        }

        return it->second;
    }

    std::vector<MetricDefinition> all() const {
        std::vector<MetricDefinition> result;

        for (const auto& [name, definition] : definitions) {
            result.push_back(definition);
        }

        return result;
    }

    std::vector<MetricDefinition> byCategory(
        MetricCategory category
    ) const {
        std::vector<MetricDefinition> result;

        for (const auto& [name, definition] : definitions) {
            if (definition.category == category) {
                result.push_back(definition);
            }
        }

        return result;
    }
};

class ObservationStore {
private:
    std::map<
        std::pair<std::string, std::string>,
        Observation
    > observations;

    const MetricRegistry& registry;

public:
    explicit ObservationStore(const MetricRegistry& registry)
        : registry(registry) {}

    void add(const Observation& observation) {
        if (
            !std::isfinite(observation.value) ||
            observation.value < 0
        ) {
            throw std::invalid_argument(
                "Observation must be finite and non-negative"
            );
        }

        if (observation.sampleSize == 0) {
            throw std::invalid_argument(
                "Sample size must be positive"
            );
        }

        if (observation.period.empty()) {
            throw std::invalid_argument(
                "Observation period is required"
            );
        }

        const auto& definition = registry.get(
            observation.metricName
        );

        if (
            definition.minimum &&
            observation.value < *definition.minimum
        ) {
            throw std::invalid_argument(
                "Observation below valid range: " +
                observation.metricName
            );
        }

        if (
            definition.maximum &&
            observation.value > *definition.maximum
        ) {
            throw std::invalid_argument(
                "Observation above valid range: " +
                observation.metricName
            );
        }

        auto key = std::make_pair(
            observation.metricName,
            observation.period
        );

        if (observations.count(key)) {
            throw std::invalid_argument(
                "Duplicate observation for metric and period"
            );
        }

        observations.emplace(key, observation);
    }

    std::optional<Observation> find(
        const std::string& metric,
        const std::string& period
    ) const {
        auto it = observations.find({metric, period});

        if (it == observations.end()) {
            return std::nullopt;
        }

        return it->second;
    }
};

class MetricEvaluator {
private:
    const MetricRegistry& registry;
    const ObservationStore& store;

    static std::optional<double> calculateChange(
        double current,
        std::optional<double> previous
    ) {
        if (!previous.has_value() || *previous == 0) {
            return std::nullopt;
        }

        return (
            (current - *previous) /
            std::abs(*previous)
        ) * 100.0;
    }

    static MetricStatus determineStatus(
        const MetricDefinition& definition,
        double value
    ) {
        if (definition.direction == Direction::Higher) {
            if (
                definition.target &&
                value < *definition.target
            ) {
                return MetricStatus::BelowTarget;
            }
        }

        if (definition.direction == Direction::Lower) {
            if (
                definition.target &&
                value > *definition.target
            ) {
                return MetricStatus::AboveLimit;
            }
        }

        if (definition.direction == Direction::Range) {
            if (
                definition.minimum &&
                value < *definition.minimum
            ) {
                return MetricStatus::BelowRange;
            }

            if (
                definition.maximum &&
                value > *definition.maximum
            ) {
                return MetricStatus::AboveRange;
            }
        }

        return MetricStatus::OnTrack;
    }

public:
    MetricEvaluator(
        const MetricRegistry& registry,
        const ObservationStore& store
    ) : registry(registry), store(store) {}

    MetricEvaluation evaluate(
        const std::string& metricName,
        const std::string& currentPeriod,
        const std::string& previousPeriod
    ) const {
        const auto& definition = registry.get(metricName);

        auto current = store.find(
            metricName,
            currentPeriod
        );

        if (!current) {
            throw std::runtime_error(
                "Current observation is missing: " + metricName
            );
        }

        auto previous = store.find(
            metricName,
            previousPeriod
        );

        std::optional<double> previousValue;

        if (previous) {
            previousValue = previous->value;
        }

        return {
            definition,
            current->value,
            previousValue,
            calculateChange(
                current->value,
                previousValue
            ),
            determineStatus(
                definition,
                current->value
            )
        };
    }
};

class GuardrailEngine {
private:
    const MetricRegistry& registry;
    const ObservationStore& store;

public:
    GuardrailEngine(
        const MetricRegistry& registry,
        const ObservationStore& store
    ) : registry(registry), store(store) {}

    std::vector<Alert> inspect(
        const std::string& period
    ) const {
        std::vector<Alert> alerts;

        for (const auto& definition :
            registry.byCategory(MetricCategory::Guardrail)) {

            auto observation = store.find(
                definition.name,
                period
            );

            if (!observation) {
                alerts.push_back({
                    definition.name,
                    Severity::Warning,
                    "Missing guardrail observation"
                });
                continue;
            }

            if (
                definition.direction == Direction::Lower &&
                definition.target &&
                observation->value > *definition.target
            ) {
                alerts.push_back({
                    definition.name,
                    Severity::Critical,
                    "Lower-is-better target breached"
                });
            }

            if (
                definition.maximum &&
                observation->value > *definition.maximum
            ) {
                alerts.push_back({
                    definition.name,
                    Severity::Critical,
                    "Maximum permitted threshold breached"
                });
            }

            if (
                definition.minimum &&
                observation->value < *definition.minimum
            ) {
                alerts.push_back({
                    definition.name,
                    Severity::Critical,
                    "Minimum permitted threshold breached"
                });
            }
        }

        return alerts;
    }
};

struct ExperimentGroup {
    std::string name;
    double metricValue;
    std::size_t sampleSize;
};

struct ExperimentResult {
    double absoluteLift;
    std::optional<double> relativeLift;
    std::string interpretation;
};

class ExperimentAnalyzer {
public:
    static ExperimentResult compare(
        const ExperimentGroup& control,
        const ExperimentGroup& treatment
    ) {
        if (
            control.sampleSize < 30 ||
            treatment.sampleSize < 30
        ) {
            throw std::invalid_argument(
                "Each experiment group requires at least 30 observations"
            );
        }

        if (
            !std::isfinite(control.metricValue) ||
            !std::isfinite(treatment.metricValue) ||
            control.metricValue < 0 ||
            treatment.metricValue < 0
        ) {
            throw std::invalid_argument(
                "Invalid experiment metric values"
            );
        }

        const double absoluteLift =
            treatment.metricValue - control.metricValue;

        std::optional<double> relativeLift;

        if (control.metricValue != 0) {
            relativeLift =
                absoluteLift /
                std::abs(control.metricValue) * 100.0;
        }

        std::string interpretation;

        if (absoluteLift > 0) {
            interpretation = "Treatment shows positive observed lift";
        } else if (absoluteLift < 0) {
            interpretation = "Treatment shows negative observed lift";
        } else {
            interpretation = "No observed lift";
        }

        return {
            absoluteLift,
            relativeLift,
            interpretation
        };
    }
};

class ProductMetricsEngine {
private:
    MetricRegistry registry;
    ObservationStore store;

public:
    ProductMetricsEngine() : store(registry) {}

    void initializeDefinitions() {
        registry.registerMetric({
            "Weekly Active Learners",
            MetricCategory::NorthStar,
            "users",
            Direction::Higher,
            12000,
            std::nullopt,
            std::nullopt
        });

        registry.registerMetric({
            "Activation Rate",
            MetricCategory::Input,
            "%",
            Direction::Higher,
            65,
            0,
            100
        });

        registry.registerMetric({
            "Lesson Completion Rate",
            MetricCategory::Input,
            "%",
            Direction::Higher,
            75,
            0,
            100
        });

        registry.registerMetric({
            "Weekly Learning Sessions",
            MetricCategory::Input,
            "sessions",
            Direction::Higher,
            45000,
            std::nullopt,
            std::nullopt
        });

        registry.registerMetric({
            "Subscription Revenue",
            MetricCategory::Output,
            "INR",
            Direction::Higher,
            1500000,
            std::nullopt,
            std::nullopt
        });

        registry.registerMetric({
            "Retention Rate",
            MetricCategory::Output,
            "%",
            Direction::Higher,
            85,
            0,
            100
        });

        registry.registerMetric({
            "Application Error Rate",
            MetricCategory::Guardrail,
            "%",
            Direction::Lower,
            1,
            0,
            2
        });

        registry.registerMetric({
            "Page Load Time",
            MetricCategory::Guardrail,
            "seconds",
            Direction::Lower,
            2,
            0,
            3
        });

        registry.registerMetric({
            "Support Complaint Rate",
            MetricCategory::Guardrail,
            "%",
            Direction::Lower,
            2,
            0,
            3
        });
    }

    void initializeObservations() {
        const std::map<
            std::string,
            std::pair<double, double>
        > data = {
            {"Weekly Active Learners", {10800, 12400}},
            {"Activation Rate", {62, 68}},
            {"Lesson Completion Rate", {72, 78}},
            {"Weekly Learning Sessions", {41000, 47000}},
            {"Subscription Revenue", {1380000, 1570000}},
            {"Retention Rate", {84, 86}},
            {"Application Error Rate", {0.8, 2.4}},
            {"Page Load Time", {1.8, 2.2}},
            {"Support Complaint Rate", {1.5, 1.8}}
        };

        for (const auto& [name, values] : data) {
            store.add({
                name,
                "previous",
                values.first,
                10000
            });

            store.add({
                name,
                "current",
                values.second,
                12000
            });
        }
    }

    void run() const {
        MetricEvaluator evaluator(registry, store);
        GuardrailEngine guardrails(registry, store);

        std::cout << "\nPRODUCT METRICS DASHBOARD\n";
        std::cout << std::string(85, '=') << "\n";

        std::cout
            << std::left
            << std::setw(32) << "METRIC"
            << std::setw(15) << "CATEGORY"
            << std::setw(14) << "CURRENT"
            << std::setw(14) << "CHANGE"
            << "STATUS\n";

        std::cout << std::string(85, '-') << "\n";

        for (const auto& definition : registry.all()) {
            auto result = evaluator.evaluate(
                definition.name,
                "current",
                "previous"
            );

            std::cout
                << std::left
                << std::setw(32) << definition.name
                << std::setw(15) << toString(definition.category)
                << std::setw(14) << result.current;

            if (result.changePercent) {
                std::cout
                    << std::setw(14)
                    << (std::to_string(*result.changePercent) + "%");
            } else {
                std::cout << std::setw(14) << "N/A";
            }

            std::cout << toString(result.status) << "\n";
        }

        std::cout << "\nGUARDRAIL ALERTS\n";

        auto alerts = guardrails.inspect("current");

        if (alerts.empty()) {
            std::cout << "No guardrail breaches.\n";
        }

        for (const auto& alert : alerts) {
            std::cout
                << "[CRITICAL] "
                << alert.metricName
                << ": "
                << alert.message
                << "\n";
        }

        std::cout << "\nPRODUCT GROWTH DIAGNOSIS\n";

        auto northStar = evaluator.evaluate(
            "Weekly Active Learners",
            "current",
            "previous"
        );

        std::cout
            << "North Star growth: "
            << std::fixed
            << std::setprecision(2)
            << *northStar.changePercent
            << "%\n";

        for (const auto& definition :
            registry.byCategory(MetricCategory::Input)) {

            auto result = evaluator.evaluate(
                definition.name,
                "current",
                "previous"
            );

            if (result.status != MetricStatus::OnTrack) {
                std::cout
                    << "Input issue: "
                    << definition.name
                    << "\n";
            }
        }
    }

    const MetricRegistry& getRegistry() const {
        return registry;
    }

    const ObservationStore& getStore() const {
        return store;
    }
};

void runAssertions() {
    auto result = ExperimentAnalyzer::compare(
        {"Control", 65, 500},
        {"Treatment", 70, 520}
    );

    if (std::abs(result.absoluteLift - 5.0) > 1e-9) {
        throw std::runtime_error("Experiment calculation failed");
    }

    if (
        !result.relativeLift ||
        std::abs(*result.relativeLift - 7.69230769) > 0.001
    ) {
        throw std::runtime_error("Relative lift calculation failed");
    }

    bool rejected = false;

    try {
        ExperimentAnalyzer::compare(
            {"Control", 65, 10},
            {"Treatment", 70, 500}
        );
    } catch (const std::invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw std::runtime_error(
            "Insufficient experiment sample was not rejected"
        );
    }

    std::cout << "All assertions passed.\n";
}

int main() {
    try {
        runAssertions();

        ProductMetricsEngine engine;

        engine.initializeDefinitions();
        engine.initializeObservations();
        engine.run();

    } catch (const std::exception& exception) {
        std::cerr
            << "ERROR: "
            << exception.what()
            << "\n";

        return 1;
    }

    return 0;
}
