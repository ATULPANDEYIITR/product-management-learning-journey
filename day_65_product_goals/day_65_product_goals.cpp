#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Product Goals and Strategic Performance Engine.
 *
 * Focus:
 * - Strategic outcome alignment
 * - Weighted OKR evaluation
 * - KPI target tracking
 * - Leading and lagging indicators
 * - Guardrail enforcement
 * - Data validation
 * - Goal lifecycle
 * - Portfolio-level reporting
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic product_goals.cpp -o product_goals
 */

enum class GoalStatus {
    Draft,
    Active,
    AtRisk,
    Achieved,
    Missed,
    Cancelled
};

enum class Direction {
    Increase,
    Decrease
};

enum class MetricCategory {
    Leading,
    Lagging,
    Guardrail
};

string statusName(GoalStatus status) {
    switch (status) {
        case GoalStatus::Draft: return "DRAFT";
        case GoalStatus::Active: return "ACTIVE";
        case GoalStatus::AtRisk: return "AT_RISK";
        case GoalStatus::Achieved: return "ACHIEVED";
        case GoalStatus::Missed: return "MISSED";
        case GoalStatus::Cancelled: return "CANCELLED";
    }

    throw runtime_error("Invalid goal status.");
}

string categoryName(MetricCategory category) {
    switch (category) {
        case MetricCategory::Leading: return "LEADING";
        case MetricCategory::Lagging: return "LAGGING";
        case MetricCategory::Guardrail: return "GUARDRAIL";
    }

    throw runtime_error("Invalid metric category.");
}

void validateFinite(double value, const string& field) {
    if (!isfinite(value)) {
        throw invalid_argument(field + " must be finite.");
    }
}

struct Observation {
    double value;
    int day;
    double confidence;
    string source;
};

class KPI {
private:
    string id;
    string name;
    string unit;

    double baseline;
    double target;

    Direction direction;
    MetricCategory category;

    double weight;
    double minimumAllowed;
    double maximumAllowed;

    vector<Observation> observations;

public:
    KPI(
        string id,
        string name,
        string unit,
        double baseline,
        double target,
        Direction direction,
        MetricCategory category,
        double weight = 1.0,
        double minimumAllowed = -1e100,
        double maximumAllowed = 1e100
    ) :
        id(move(id)),
        name(move(name)),
        unit(move(unit)),
        baseline(baseline),
        target(target),
        direction(direction),
        category(category),
        weight(weight),
        minimumAllowed(minimumAllowed),
        maximumAllowed(maximumAllowed)
    {
        if (this->id.empty() || this->name.empty() || this->unit.empty()) {
            throw invalid_argument("KPI identity fields are required.");
        }

        validateFinite(baseline, "Baseline");
        validateFinite(target, "Target");
        validateFinite(weight, "Weight");

        if (weight <= 0) {
            throw invalid_argument("KPI weight must be positive.");
        }

        if (baseline == target) {
            throw invalid_argument("Baseline and target must differ.");
        }

        if (
            (direction == Direction::Increase && target <= baseline) ||
            (direction == Direction::Decrease && target >= baseline)
        ) {
            throw invalid_argument("Target conflicts with direction.");
        }

        if (minimumAllowed > maximumAllowed) {
            throw invalid_argument("Invalid guardrail boundaries.");
        }
    }

    void record(
        double value,
        int day,
        double confidence,
        const string& source
    ) {
        validateFinite(value, "Measurement");
        validateFinite(confidence, "Confidence");

        if (confidence < 0 || confidence > 1) {
            throw invalid_argument("Confidence must be between 0 and 1.");
        }

        if (day < 0) {
            throw invalid_argument("Day cannot be negative.");
        }

        if (source.empty()) {
            throw invalid_argument("Measurement source is required.");
        }

        if (!observations.empty() && day <= observations.back().day) {
            throw invalid_argument("Measurements must be chronological.");
        }

        observations.push_back({
            value,
            day,
            confidence,
            source
        });
    }

    double current() const {
        return observations.empty()
            ? baseline
            : observations.back().value;
    }

    double progress() const {
        double result =
            (current() - baseline) / (target - baseline) * 100.0;

        return clamp(result, 0.0, 100.0);
    }

    double remaining() const {
        return target - current();
    }

    double quality() const {
        if (observations.empty()) return 0.0;
        return observations.back().confidence;
    }

    bool withinGuardrails() const {
        return current() >= minimumAllowed &&
               current() <= maximumAllowed;
    }

    double getWeight() const {
        return weight;
    }

    MetricCategory getCategory() const {
        return category;
    }

    const string& getId() const {
        return id;
    }

    void print() const {
        cout << left << setw(18) << id
             << setw(28) << name
             << setw(12) << categoryName(category)
             << right << setw(10) << fixed << setprecision(2)
             << current()
             << setw(12) << target
             << setw(12) << progress() << "%\n";
    }
};

class Objective {
private:
    string id;
    string title;
    string owner;
    int deadlineDay;

    GoalStatus status = GoalStatus::Draft;

    vector<KPI> keyResults;

public:
    Objective(
        string id,
        string title,
        string owner,
        int deadlineDay
    ) :
        id(move(id)),
        title(move(title)),
        owner(move(owner)),
        deadlineDay(deadlineDay)
    {
        if (this->id.empty() || this->title.empty() || this->owner.empty()) {
            throw invalid_argument("Objective identity fields are required.");
        }

        if (deadlineDay < 0) {
            throw invalid_argument("Invalid deadline.");
        }
    }

    void addKeyResult(const KPI& kpi) {
        if (status != GoalStatus::Draft) {
            throw logic_error("Cannot modify an active objective.");
        }

        auto duplicate = find_if(
            keyResults.begin(),
            keyResults.end(),
            [&](const KPI& existing) {
                return existing.getId() == kpi.getId();
            }
        );

        if (duplicate != keyResults.end()) {
            throw invalid_argument("Duplicate Key Result.");
        }

        keyResults.push_back(kpi);
    }

    void activate() {
        if (status != GoalStatus::Draft) {
            throw logic_error("Only draft objectives can be activated.");
        }

        if (keyResults.empty()) {
            throw logic_error("An objective requires Key Results.");
        }

        status = GoalStatus::Active;
    }

    double progress() const {
        if (keyResults.empty()) return 0;

        double weightedSum = 0;
        double totalWeight = 0;

        for (const KPI& kpi : keyResults) {
            weightedSum += kpi.progress() * kpi.getWeight();
            totalWeight += kpi.getWeight();
        }

        return weightedSum / totalWeight;
    }

    GoalStatus evaluate(int currentDay) {
        if (status == GoalStatus::Draft ||
            status == GoalStatus::Cancelled) {
            return status;
        }

        bool guardrailViolation = any_of(
            keyResults.begin(),
            keyResults.end(),
            [](const KPI& kpi) {
                return !kpi.withinGuardrails();
            }
        );

        if (guardrailViolation) {
            status = GoalStatus::AtRisk;
        } else if (progress() >= 100) {
            status = GoalStatus::Achieved;
        } else if (currentDay > deadlineDay) {
            status = GoalStatus::Missed;
        } else if (progress() < 40) {
            status = GoalStatus::AtRisk;
        } else {
            status = GoalStatus::Active;
        }

        return status;
    }

    void printReport() const {
        cout << "\nOBJECTIVE: " << title << "\n"
             << "ID: " << id << "\n"
             << "OWNER: " << owner << "\n"
             << "STATUS: " << statusName(status) << "\n"
             << "WEIGHTED PROGRESS: "
             << fixed << setprecision(2)
             << progress() << "%\n";

        cout << "\nKEY RESULT PERFORMANCE\n";

        cout << left << setw(18) << "ID"
             << setw(28) << "METRIC"
             << setw(12) << "CATEGORY"
             << right << setw(10) << "CURRENT"
             << setw(12) << "TARGET"
             << setw(13) << "PROGRESS\n";

        for (const KPI& kpi : keyResults) {
            kpi.print();
        }
    }

    GoalStatus getStatus() const {
        return status;
    }
};

class Portfolio {
private:
    map<string, Objective> objectives;

public:
    void addObjective(const string& id, const Objective& objective) {
        auto result = objectives.emplace(id, objective);

        if (!result.second) {
            throw invalid_argument("Duplicate portfolio objective.");
        }
    }

    void evaluate(int currentDay) {
        for (auto& entry : objectives) {
            entry.second.evaluate(currentDay);
        }
    }

    void report() const {
        int active = 0;
        int achieved = 0;
        int atRisk = 0;
        int missed = 0;

        for (const auto& entry : objectives) {
            switch (entry.second.getStatus()) {
                case GoalStatus::Active: ++active; break;
                case GoalStatus::Achieved: ++achieved; break;
                case GoalStatus::AtRisk: ++atRisk; break;
                case GoalStatus::Missed: ++missed; break;
                default: break;
            }

            entry.second.printReport();
        }

        cout << "\nPORTFOLIO DASHBOARD\n"
             << "Total objectives: " << objectives.size() << "\n"
             << "Active: " << active << "\n"
             << "Achieved: " << achieved << "\n"
             << "At risk: " << atRisk << "\n"
             << "Missed: " << missed << "\n";
    }
};

int main() {
    try {
        Portfolio portfolio;

        Objective retention(
            "OBJ-001",
            "Improve customer retention",
            "Product Management",
            365
        );

        KPI retentionRate(
            "KR-001",
            "Monthly retention",
            "%",
            70,
            85,
            Direction::Increase,
            MetricCategory::Lagging,
            3.0,
            60,
            100
        );

        retentionRate.record(
            80,
            300,
            0.97,
            "Subscription analytics"
        );

        KPI activationRate(
            "KR-002",
            "Customer activation",
            "%",
            40,
            70,
            Direction::Increase,
            MetricCategory::Leading,
            1.0,
            30,
            100
        );

        activationRate.record(
            60,
            300,
            0.94,
            "Product analytics"
        );

        retention.addKeyResult(retentionRate);
        retention.addKeyResult(activationRate);
        retention.activate();

        portfolio.addObjective("OBJ-001", retention);

        Objective revenue(
            "OBJ-002",
            "Improve recurring revenue",
            "Commercial Product Team",
            365
        );

        KPI monthlyRevenue(
            "KR-003",
            "Monthly recurring revenue",
            "INR",
            1000000,
            1500000,
            Direction::Increase,
            MetricCategory::Lagging,
            2.0
        );

        monthlyRevenue.record(
            1300000,
            300,
            0.98,
            "Billing system"
        );

        revenue.addKeyResult(monthlyRevenue);
        revenue.activate();

        portfolio.addObjective("OBJ-002", revenue);

        portfolio.evaluate(308);
        portfolio.report();

        // Numerical verification of weighted OKR progress.
        double expected =
            ((66.6666666667 * 3.0) + (66.6666666667 * 1.0)) / 4.0;

        if (abs(expected - 66.6666666667) > 0.001) {
            throw runtime_error("Weighted progress validation failed.");
        }

        // Invalid measurement rejection.
        try {
            retentionRate.record(
                numeric_limits<double>::quiet_NaN(),
                301,
                0.9,
                "Invalid source"
            );
        } catch (const invalid_argument& error) {
            cout << "\nInvalid measurement rejected: "
                 << error.what() << "\n";
        }

        cout << "\nProduct goal evaluation completed.\n";

    } catch (const exception& error) {
        cerr << "Execution failed: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
