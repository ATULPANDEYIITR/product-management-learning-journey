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

enum class IndicatorType {
    Leading,
    Lagging
};

enum class ObjectiveStatus {
    Draft,
    Active,
    AtRisk,
    Completed,
    Cancelled
};

string toString(IndicatorType type) {
    return type == IndicatorType::Leading ? "Leading" : "Lagging";
}

string toString(ObjectiveStatus status) {
    switch (status) {
        case ObjectiveStatus::Draft: return "Draft";
        case ObjectiveStatus::Active: return "Active";
        case ObjectiveStatus::AtRisk: return "At Risk";
        case ObjectiveStatus::Completed: return "Completed";
        case ObjectiveStatus::Cancelled: return "Cancelled";
    }
    return "Unknown";
}

void validateText(const string& value, const string& field) {
    if (value.empty() ||
        value.find_first_not_of(" \t\n\r") == string::npos) {
        throw invalid_argument(field + " cannot be empty.");
    }
}

void validateNumber(double value, const string& field) {
    if (!isfinite(value) || abs(value) > 1e12) {
        throw invalid_argument(field + " must be finite and within limits.");
    }
}

struct KeyResult {
    int id;
    string title;
    double baseline;
    double current;
    double target;
    string unit;
    IndicatorType indicator;
    double weight;
    bool higherIsBetter;

    vector<double> history;

    KeyResult(
        int id,
        string title,
        double baseline,
        double current,
        double target,
        string unit,
        IndicatorType indicator,
        double weight = 1.0,
        bool higherIsBetter = true
    ) :
        id(id),
        title(move(title)),
        baseline(baseline),
        current(current),
        target(target),
        unit(move(unit)),
        indicator(indicator),
        weight(weight),
        higherIsBetter(higherIsBetter) {

        validateText(this->title, "Key result title");
        validateText(this->unit, "Unit");
        validateNumber(baseline, "Baseline");
        validateNumber(current, "Current value");
        validateNumber(target, "Target");
        validateNumber(weight, "Weight");

        if (baseline == target) {
            throw invalid_argument("Baseline and target cannot match.");
        }

        if (weight <= 0) {
            throw invalid_argument("Weight must be positive.");
        }

        if (higherIsBetter ? target <= baseline : target >= baseline) {
            throw invalid_argument("Target direction is invalid.");
        }

        history.push_back(current);
    }

    double progress() const {
        return clamp(
            (current - baseline) / (target - baseline),
            0.0,
            1.0
        );
    }

    void update(double value) {
        validateNumber(value, "Updated value");
        current = value;
        history.push_back(value);
    }
};

class Objective {
private:
    int id;
    string title;
    string owner;
    string department;
    string period;
    int parentId;
    ObjectiveStatus status;
    vector<KeyResult> results;

public:
    Objective(
        int id,
        string title,
        string owner,
        string department,
        string period,
        int parentId = -1
    ) :
        id(id),
        title(move(title)),
        owner(move(owner)),
        department(move(department)),
        period(move(period)),
        parentId(parentId),
        status(ObjectiveStatus::Draft) {

        if (id <= 0) {
            throw invalid_argument("Objective ID must be positive.");
        }

        validateText(this->title, "Objective title");
        validateText(this->owner, "Owner");
        validateText(this->department, "Department");
        validateText(this->period, "Period");
    }

    int getId() const { return id; }
    int getParentId() const { return parentId; }
    string getPeriod() const { return period; }
    string getTitle() const { return title; }
    string getOwner() const { return owner; }
    ObjectiveStatus getStatus() const { return status; }

    const vector<KeyResult>& getResults() const {
        return results;
    }

    void addKeyResult(const KeyResult& result) {
        auto duplicate = find_if(
            results.begin(),
            results.end(),
            [&](const KeyResult& existing) {
                return existing.id == result.id ||
                       existing.title == result.title;
            }
        );

        if (duplicate != results.end()) {
            throw invalid_argument("Duplicate key result.");
        }

        if (status != ObjectiveStatus::Draft) {
            throw logic_error("Results cannot be added after activation.");
        }

        results.push_back(result);
    }

    void activate() {
        if (status != ObjectiveStatus::Draft &&
            status != ObjectiveStatus::Active) {
            throw logic_error("Invalid objective state transition.");
        }

        if (results.empty()) {
            throw logic_error("Objective requires at least one result.");
        }

        status = ObjectiveStatus::Active;
    }

    double progress() const {
        if (results.empty()) return 0.0;

        double weightedProgress = 0.0;
        double totalWeight = 0.0;

        for (const auto& result : results) {
            weightedProgress += result.progress() * result.weight;
            totalWeight += result.weight;
        }

        return weightedProgress / totalWeight;
    }

    double indicatorProgress(IndicatorType type) const {
        double total = 0.0;
        int count = 0;

        for (const auto& result : results) {
            if (result.indicator == type) {
                total += result.progress();
                ++count;
            }
        }

        return count == 0 ? -1.0 : total / count;
    }

    void updateResult(int resultId, double value) {
        if (status != ObjectiveStatus::Active &&
            status != ObjectiveStatus::AtRisk) {
            throw logic_error("Objective is not accepting updates.");
        }

        auto it = find_if(
            results.begin(),
            results.end(),
            [&](const KeyResult& result) {
                return result.id == resultId;
            }
        );

        if (it == results.end()) {
            throw out_of_range("Key result not found.");
        }

        it->update(value);
        evaluate();
    }

    void evaluate() {
        if (status == ObjectiveStatus::Cancelled ||
            status == ObjectiveStatus::Completed) {
            return;
        }

        double score = progress();

        if (score >= 1.0) {
            status = ObjectiveStatus::Completed;
        } else if (score < 0.4) {
            status = ObjectiveStatus::AtRisk;
        } else {
            status = ObjectiveStatus::Active;
        }
    }

    void printReport() const {
        cout << "\nObjective: " << title << '\n';
        cout << "Owner: " << owner << '\n';
        cout << "Department: " << department << '\n';
        cout << "Period: " << period << '\n';
        cout << "Status: " << toString(status) << '\n';

        cout << fixed << setprecision(2);
        cout << "Weighted progress: " << progress() * 100 << "%\n";

        double leading = indicatorProgress(IndicatorType::Leading);
        double lagging = indicatorProgress(IndicatorType::Lagging);

        cout << "Leading progress: ";
        if (leading < 0) cout << "N/A\n";
        else cout << leading * 100 << "%\n";

        cout << "Lagging progress: ";
        if (lagging < 0) cout << "N/A\n";
        else cout << lagging * 100 << "%\n";

        cout << "Key results:\n";

        for (const auto& result : results) {
            cout << "  - " << result.title
                 << ": " << result.current << " " << result.unit
                 << " / " << result.target
                 << " (" << result.progress() * 100 << "%)"
                 << " [" << toString(result.indicator) << "]\n";
        }
    }
};

class OKRGovernance {
private:
    map<int, Objective> objectives;

public:
    void addObjective(const Objective& objective) {
        if (objectives.count(objective.getId())) {
            throw invalid_argument("Duplicate objective ID.");
        }

        if (objective.getParentId() != -1) {
            auto parent = objectives.find(objective.getParentId());

            if (parent == objectives.end()) {
                throw invalid_argument("Parent objective not found.");
            }

            if (parent->second.getPeriod() != objective.getPeriod()) {
                throw invalid_argument("Objective periods do not match.");
            }
        }

        objectives.emplace(objective.getId(), objective);
    }

    Objective& getObjective(int id) {
        auto it = objectives.find(id);

        if (it == objectives.end()) {
            throw out_of_range("Objective not found.");
        }

        return it->second;
    }

    void activate(int id) {
        getObjective(id).activate();
    }

    void update(int objectiveId, int resultId, double value) {
        getObjective(objectiveId).updateResult(resultId, value);
    }

    void printOrganizationReport() {
        cout << "\n========== ORGANIZATION OKR REPORT ==========\n";

        for (auto& [id, objective] : objectives) {
            objective.evaluate();
            objective.printReport();
        }
    }

    void printAlignment(int parentId, int depth = 0) const {
        auto it = objectives.find(parentId);

        if (it == objectives.end()) return;

        cout << string(depth * 2, ' ')
             << it->second.getTitle()
             << " (" << it->second.progress() * 100 << "%)\n";

        for (const auto& [id, child] : objectives) {
            if (child.getParentId() == parentId) {
                printAlignment(id, depth + 1);
            }
        }
    }
};

int main() {
    try {
        OKRGovernance organization;

        Objective company(
            1,
            "Increase digital banking competitiveness",
            "Chief Executive Officer",
            "Executive",
            "2026-Q4"
        );

        company.addKeyResult(KeyResult(
            101,
            "Customer retention rate",
            70, 76, 90,
            "%",
            IndicatorType::Lagging,
            2.0
        ));

        company.addKeyResult(KeyResult(
            102,
            "Monthly active customers",
            100000, 125000, 200000,
            "customers",
            IndicatorType::Lagging
        ));

        organization.addObjective(company);

        Objective product(
            2,
            "Improve mobile onboarding",
            "Product Director",
            "Product",
            "2026-Q4",
            1
        );

        product.addKeyResult(KeyResult(
            201,
            "Usability tests completed",
            0, 10, 20,
            "tests",
            IndicatorType::Leading
        ));

        product.addKeyResult(KeyResult(
            202,
            "Onboarding completion rate",
            40, 55, 80,
            "%",
            IndicatorType::Lagging
        ));

        organization.addObjective(product);

        organization.activate(1);
        organization.activate(2);

        organization.update(2, 201, 16);

        organization.printOrganizationReport();

        cout << "\n========== OBJECTIVE ALIGNMENT ==========\n";
        organization.printAlignment(1);

        cout << "\n========== EDGE CASE VALIDATION ==========\n";

        try {
            organization.update(2, 999, 50);
        } catch (const exception& error) {
            cout << "Expected failure: " << error.what() << '\n';
        }

        try {
            KeyResult invalid(
                300, "Invalid weight",
                0, 5, 10,
                "units",
                IndicatorType::Leading,
                -1
            );
        } catch (const exception& error) {
            cout << "Expected failure: " << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
