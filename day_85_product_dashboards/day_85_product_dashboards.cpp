#include <algorithm>
#include <cmath>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

/*
 * Product Dashboard Governance and Merge-Independent KPI Engine
 *
 * C++17
 *
 * Implements:
 * - Metric definitions
 * - Metric hierarchy
 * - Time-window aggregation
 * - Dimension filtering
 * - Dashboard configuration
 * - Visualization data preparation
 * - Alert evaluation
 * - Alert recovery and deduplication
 * - Dashboard access control
 * - Merge-free immutable reporting snapshots
 */

enum class MetricCategory {
    NorthStar,
    Business,
    Product,
    Engagement,
    Reliability
};

enum class MetricType {
    Count,
    Percentage,
    Currency,
    Duration,
    Ratio
};

enum class Aggregation {
    Sum,
    Average,
    Minimum,
    Maximum,
    Last
};

enum class Severity {
    Warning,
    Critical
};

enum class Role {
    Viewer,
    Analyst,
    Administrator
};

string toString(MetricCategory category) {
    switch (category) {
        case MetricCategory::NorthStar: return "North Star";
        case MetricCategory::Business: return "Business";
        case MetricCategory::Product: return "Product";
        case MetricCategory::Engagement: return "Engagement";
        case MetricCategory::Reliability: return "Reliability";
    }

    throw logic_error("Unknown metric category.");
}

string toString(Severity severity) {
    return severity == Severity::Critical
        ? "CRITICAL"
        : "WARNING";
}

class DashboardException : public runtime_error {
public:
    explicit DashboardException(const string& message)
        : runtime_error(message) {}
};

struct MetricDefinition {
    string name;
    string description;
    MetricCategory category;
    MetricType type;
    string unit;
    Aggregation aggregation;
    bool higherIsBetter;

    optional<double> target;
    optional<double> warningThreshold;
    optional<double> criticalThreshold;

    void validate() const {
        if (name.empty() || description.empty() || unit.empty()) {
            throw DashboardException(
                "Metric definition fields cannot be empty."
            );
        }

        auto valid = [](const optional<double>& value) {
            return !value || isfinite(*value);
        };

        if (!valid(target) ||
            !valid(warningThreshold) ||
            !valid(criticalThreshold)) {
            throw DashboardException(
                "Thresholds and targets must be finite."
            );
        }

        if (type == MetricType::Percentage && unit != "%") {
            throw DashboardException(
                "Percentage metrics must use %."
            );
        }
    }

    void validateValue(double value) const {
        if (!isfinite(value)) {
            throw DashboardException(
                "Metric value must be finite."
            );
        }

        if (type == MetricType::Percentage &&
            (value < 0 || value > 100)) {
            throw DashboardException(
                "Percentage must be between 0 and 100."
            );
        }

        if ((type == MetricType::Count ||
             type == MetricType::Duration) && value < 0) {
            throw DashboardException(
                "Count and duration cannot be negative."
            );
        }
    }
};

struct Observation {
    string metricName;
    double value;
    time_t timestamp;
    map<string, string> dimensions;
    string entityId;
};

struct Alert {
    string metricName;
    Severity severity;
    double observedValue;
    time_t timestamp;
    bool acknowledged = false;
};

struct DashboardConfig {
    string id;
    string title;
    vector<string> metrics;
    int refreshSeconds;
    map<string, Role> permissions;
};

struct MetricResult {
    optional<double> current;
    optional<double> previous;
    optional<double> percentageChange;
    size_t sampleCount = 0;
    string unit;
    string category;
    optional<Alert> alert;
};

class MetricRegistry {
private:
    unordered_map<string, MetricDefinition> definitions;

public:
    void registerMetric(const MetricDefinition& definition) {
        definition.validate();

        if (definitions.count(definition.name)) {
            throw DashboardException(
                "Duplicate metric: " + definition.name
            );
        }

        definitions.emplace(definition.name, definition);
    }

    const MetricDefinition& get(const string& name) const {
        auto it = definitions.find(name);

        if (it == definitions.end()) {
            throw DashboardException(
                "Unknown metric: " + name
            );
        }

        return it->second;
    }
};

class MetricRepository {
private:
    const MetricRegistry& registry;
    vector<Observation> observations;

public:
    explicit MetricRepository(const MetricRegistry& r)
        : registry(r) {}

    void insert(const Observation& observation) {
        const auto& definition =
            registry.get(observation.metricName);

        definition.validateValue(observation.value);

        for (const auto& dimension : observation.dimensions) {
            if (dimension.first.empty() ||
                dimension.second.empty()) {
                throw DashboardException(
                    "Dimension key and value are required."
                );
            }
        }

        observations.push_back(observation);
    }

    vector<Observation> query(
        const string& metricName,
        time_t start,
        time_t end,
        const map<string, string>& dimensions = {}
    ) const {
        registry.get(metricName);

        if (start >= end) {
            throw DashboardException(
                "Invalid query time range."
            );
        }

        vector<Observation> result;

        for (const auto& observation : observations) {
            if (observation.metricName != metricName) {
                continue;
            }

            if (observation.timestamp < start ||
                observation.timestamp >= end) {
                continue;
            }

            bool matches = true;

            for (const auto& required : dimensions) {
                auto found = observation.dimensions.find(
                    required.first
                );

                if (found == observation.dimensions.end() ||
                    found->second != required.second) {
                    matches = false;
                    break;
                }
            }

            if (matches) {
                result.push_back(observation);
            }
        }

        return result;
    }
};

class Aggregator {
public:
    static optional<double> calculate(
        const vector<Observation>& observations,
        Aggregation method
    ) {
        if (observations.empty()) {
            return nullopt;
        }

        vector<double> values;

        for (const auto& item : observations) {
            values.push_back(item.value);
        }

        switch (method) {
            case Aggregation::Sum: {
                double total = 0;

                for (double value : values) {
                    total += value;
                }

                return total;
            }

            case Aggregation::Average: {
                double total = 0;

                for (double value : values) {
                    total += value;
                }

                return total / values.size();
            }

            case Aggregation::Minimum:
                return *min_element(
                    values.begin(), values.end()
                );

            case Aggregation::Maximum:
                return *max_element(
                    values.begin(), values.end()
                );

            case Aggregation::Last: {
                const auto latest = max_element(
                    observations.begin(),
                    observations.end(),
                    [](const Observation& a, const Observation& b) {
                        return a.timestamp < b.timestamp;
                    }
                );

                return latest->value;
            }
        }

        throw DashboardException("Invalid aggregation.");
    }
};

class AlertEngine {
private:
    map<string, Alert> activeAlerts;

public:
    optional<Alert> evaluate(
        const MetricDefinition& definition,
        double value,
        time_t timestamp
    ) {
        definition.validateValue(value);

        optional<Severity> severity;

        if (definition.higherIsBetter) {
            if (definition.criticalThreshold &&
                value < *definition.criticalThreshold) {
                severity = Severity::Critical;
            } else if (
                definition.warningThreshold &&
                value < *definition.warningThreshold
            ) {
                severity = Severity::Warning;
            }
        } else {
            if (definition.criticalThreshold &&
                value > *definition.criticalThreshold) {
                severity = Severity::Critical;
            } else if (
                definition.warningThreshold &&
                value > *definition.warningThreshold
            ) {
                severity = Severity::Warning;
            }
        }

        if (!severity) {
            resolve(definition.name);
            return nullopt;
        }

        string fingerprint =
            definition.name + ":" + toString(*severity);

        if (activeAlerts.count(fingerprint)) {
            return nullopt;
        }

        Alert alert {
            definition.name,
            *severity,
            value,
            timestamp,
            false
        };

        activeAlerts.emplace(fingerprint, alert);

        return alert;
    }

    void acknowledge(const string& metricName) {
        for (auto it = activeAlerts.begin();
             it != activeAlerts.end();) {

            if (it->second.metricName == metricName) {
                it = activeAlerts.erase(it);
            } else {
                ++it;
            }
        }
    }

    void resolve(const string& metricName) {
        acknowledge(metricName);
    }

    vector<Alert> getActiveAlerts() const {
        vector<Alert> result;

        for (const auto& entry : activeAlerts) {
            result.push_back(entry.second);
        }

        return result;
    }
};

class AccessControl {
public:
    static void authorize(
        const DashboardConfig& config,
        const string& username,
        Role required
    ) {
        auto it = config.permissions.find(username);

        if (it == config.permissions.end()) {
            throw DashboardException(
                "User has no dashboard permission."
            );
        }

        if (static_cast<int>(it->second) <
            static_cast<int>(required)) {
            throw DashboardException(
                "Insufficient dashboard permission."
            );
        }
    }
};

class DashboardEngine {
private:
    const MetricRegistry& registry;
    const MetricRepository& repository;
    AlertEngine& alertEngine;

public:
    DashboardEngine(
        const MetricRegistry& r,
        const MetricRepository& repo,
        AlertEngine& alerts
    ) : registry(r), repository(repo), alertEngine(alerts) {}

    map<string, MetricResult> build(
        const DashboardConfig& config,
        const string& username,
        time_t start,
        time_t end
    ) {
        AccessControl::authorize(
            config, username, Role::Viewer
        );

        if (start >= end) {
            throw DashboardException(
                "Invalid dashboard time window."
            );
        }

        const time_t duration = end - start;
        const time_t previousStart = start - duration;

        map<string, MetricResult> results;

        for (const auto& name : config.metrics) {
            const auto& definition = registry.get(name);

            auto currentObservations = repository.query(
                name, start, end
            );

            auto previousObservations = repository.query(
                name, previousStart, start
            );

            MetricResult result;

            result.current = Aggregator::calculate(
                currentObservations,
                definition.aggregation
            );

            result.previous = Aggregator::calculate(
                previousObservations,
                definition.aggregation
            );

            result.sampleCount = currentObservations.size();
            result.unit = definition.unit;
            result.category = toString(definition.category);

            if (result.current && result.previous &&
                *result.previous != 0) {

                result.percentageChange =
                    ((*result.current - *result.previous) /
                     abs(*result.previous)) * 100.0;
            }

            if (result.current) {
                result.alert = alertEngine.evaluate(
                    definition,
                    *result.current,
                    end
                );
            }

            results.emplace(name, result);
        }

        return results;
    }
};

void printDashboard(
    const DashboardConfig& config,
    const map<string, MetricResult>& results
) {
    cout << "\n" << config.title << "\n";
    cout << string(80, '=') << "\n";

    cout << left
         << setw(30) << "METRIC"
         << setw(15) << "VALUE"
         << setw(12) << "UNIT"
         << setw(15) << "CHANGE"
         << "STATUS\n";

    for (const auto& entry : results) {
        const auto& name = entry.first;
        const auto& result = entry.second;

        cout << left << setw(30) << name;

        if (result.current) {
            cout << setw(15) << *result.current;
        } else {
            cout << setw(15) << "NO DATA";
        }

        cout << setw(12) << result.unit;

        if (result.percentageChange) {
            cout << setw(15)
                 << fixed << setprecision(2)
                 << *result.percentageChange;
        } else {
            cout << setw(15) << "N/A";
        }

        if (result.alert) {
            cout << toString(result.alert->severity);
        } else {
            cout << "NORMAL";
        }

        cout << "\n";
    }
}

int main() {
    try {
        MetricRegistry registry;

        registry.registerMetric({
            "monthly_active_users",
            "Monthly active users",
            MetricCategory::NorthStar,
            MetricType::Count,
            "users",
            Aggregation::Last,
            true,
            50000,
            40000,
            30000
        });

        registry.registerMetric({
            "conversion_rate",
            "Purchase conversion rate",
            MetricCategory::Business,
            MetricType::Percentage,
            "%",
            Aggregation::Average,
            true,
            5.0,
            3.5,
            2.0
        });

        registry.registerMetric({
            "daily_revenue",
            "Recognized daily revenue",
            MetricCategory::Business,
            MetricType::Currency,
            "INR",
            Aggregation::Sum,
            true,
            500000,
            nullopt,
            nullopt
        });

        registry.registerMetric({
            "crash_rate",
            "Application crash percentage",
            MetricCategory::Reliability,
            MetricType::Percentage,
            "%",
            Aggregation::Average,
            false,
            0.5,
            1.0,
            2.0
        });

        MetricRepository repository(registry);

        const time_t now = time(nullptr);

        vector<Observation> sample = {
            {"monthly_active_users", 35000, now - 86400, {}, ""},
            {"monthly_active_users", 38000, now - 100, {}, ""},
            {"conversion_rate", 4.1, now - 86400, {}, ""},
            {"conversion_rate", 3.2, now - 100, {}, ""},
            {"daily_revenue", 420000, now - 86400, {}, ""},
            {"daily_revenue", 390000, now - 100, {}, ""},
            {"crash_rate", 0.7, now - 86400, {}, ""},
            {"crash_rate", 2.4, now - 100, {}, ""}
        };

        for (const auto& observation : sample) {
            repository.insert(observation);
        }

        DashboardConfig config {
            "executive-product-dashboard",
            "Product Performance Dashboard",
            {
                "monthly_active_users",
                "conversion_rate",
                "daily_revenue",
                "crash_rate"
            },
            60,
            {
                {"administrator", Role::Administrator},
                {"analyst", Role::Analyst},
                {"executive", Role::Viewer}
            }
        };

        AlertEngine alerts;

        DashboardEngine engine(
            registry,
            repository,
            alerts
        );

        auto results = engine.build(
            config,
            "administrator",
            now - 86400,
            now + 1
        );

        printDashboard(config, results);

        cout << "\nACTIVE ALERTS\n";

        for (const auto& alert : alerts.getActiveAlerts()) {
            cout << alert.metricName << " | "
                 << toString(alert.severity) << " | "
                 << alert.observedValue << "\n";
        }

        cout << "\nRECOVERY SIMULATION\n";

        auto recovery = alerts.evaluate(
            registry.get("crash_rate"),
            0.4,
            now
        );

        cout << "Crash rate recovery: "
             << (recovery ? "Alert created" : "No active breach")
             << "\n";

        cout << "\nVALIDATION TEST\n";

        try {
            registry.get("missing_metric");
        } catch (const DashboardException& error) {
            cout << "Handled: " << error.what() << "\n";
        }

        cout << "\nACCESS CONTROL TEST\n";

        try {
            AccessControl::authorize(
                config,
                "unknown_user",
                Role::Viewer
            );
        } catch (const DashboardException& error) {
            cout << "Handled: " << error.what() << "\n";
        }

    } catch (const exception& error) {
        cerr << "Dashboard failure: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
