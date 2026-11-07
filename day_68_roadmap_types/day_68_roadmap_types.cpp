#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * ROADMAP PLANNING AND PORTFOLIO ENGINE
 *
 * C++17 implementation of:
 * - Feature roadmaps.
 * - Outcome roadmaps.
 * - Theme roadmaps.
 * - Now-Next-Later roadmaps.
 *
 * Includes dependency graph validation, strategic alignment,
 * prioritization, metric evaluation, and execution controls.
 */

enum class RoadmapType {
    Feature,
    Outcome,
    Theme,
    NowNextLater
};

enum class Status {
    Proposed,
    Planned,
    InProgress,
    Blocked,
    Completed,
    Cancelled
};

enum class Priority {
    Critical = 1,
    High = 2,
    Medium = 3,
    Low = 4
};

enum class Horizon {
    Now,
    Next,
    Later
};

string toString(RoadmapType type) {
    switch (type) {
        case RoadmapType::Feature: return "Feature";
        case RoadmapType::Outcome: return "Outcome";
        case RoadmapType::Theme: return "Theme";
        case RoadmapType::NowNextLater: return "Now-Next-Later";
    }

    throw runtime_error("Invalid roadmap type");
}

string toString(Status status) {
    switch (status) {
        case Status::Proposed: return "Proposed";
        case Status::Planned: return "Planned";
        case Status::InProgress: return "In Progress";
        case Status::Blocked: return "Blocked";
        case Status::Completed: return "Completed";
        case Status::Cancelled: return "Cancelled";
    }

    throw runtime_error("Invalid status");
}

string toString(Horizon horizon) {
    switch (horizon) {
        case Horizon::Now: return "Now";
        case Horizon::Next: return "Next";
        case Horizon::Later: return "Later";
    }

    throw runtime_error("Invalid horizon");
}

struct Metric {
    string name;
    double baseline;
    double target;
    double current;
    string unit;

    Metric(
        string name,
        double baseline,
        double target,
        double current,
        string unit = ""
    ) : name(move(name)),
        baseline(baseline),
        target(target),
        current(current),
        unit(move(unit)) {

        if (this->name.empty()) {
            throw invalid_argument("Metric name is required");
        }

        if (
            baseline < 0 ||
            target < 0 ||
            current < 0
        ) {
            throw invalid_argument(
                "Metric values cannot be negative"
            );
        }
    }

    double progress() const {
        double difference = target - baseline;

        if (difference == 0) {
            return current == target ? 100.0 : 0.0;
        }

        double result =
            ((current - baseline) / difference) * 100.0;

        return max(0.0, min(100.0, result));
    }
};

struct Theme {
    string id;
    string name;
    string objective;
    string owner;
    set<string> itemIds;
};

struct RoadmapItem {
    string id;
    string title;
    string description;
    string owner;

    RoadmapType type;
    Status status;
    Priority priority;

    double progress;
    double confidence;

    optional<Metric> metric;
    optional<Horizon> horizon;
    optional<string> themeId;

    set<string> dependencies;
    set<string> tags;
};

class Roadmap {
private:
    string name;
    RoadmapType type;

    unordered_map<string, RoadmapItem> items;
    unordered_map<string, Theme> themes;

    static void validateText(
        const string& value,
        const string& field
    ) {
        if (value.empty()) {
            throw invalid_argument(field + " is required");
        }
    }

    void visit(
        const string& id,
        unordered_map<string, int>& state
    ) const {
        if (state[id] == 1) {
            throw runtime_error(
                "Circular dependency detected"
            );
        }

        if (state[id] == 2) {
            return;
        }

        state[id] = 1;

        const auto& item = items.at(id);

        for (const auto& dependency : item.dependencies) {
            if (!items.count(dependency)) {
                throw runtime_error(
                    "Unknown dependency: " + dependency
                );
            }

            visit(dependency, state);
        }

        state[id] = 2;
    }

public:
    Roadmap(string name, RoadmapType type)
        : name(move(name)), type(type) {

        validateText(this->name, "Roadmap name");
    }

    void addTheme(Theme theme) {
        validateText(theme.id, "Theme ID");
        validateText(theme.name, "Theme name");
        validateText(theme.objective, "Theme objective");

        if (themes.count(theme.id)) {
            throw invalid_argument("Duplicate theme");
        }

        themes.emplace(theme.id, move(theme));
    }

    void addItem(RoadmapItem item) {
        validateText(item.id, "Item ID");
        validateText(item.title, "Item title");
        validateText(item.owner, "Item owner");

        if (item.type != type) {
            throw invalid_argument(
                "Roadmap item type mismatch"
            );
        }

        if (item.progress < 0 || item.progress > 100) {
            throw invalid_argument("Invalid progress");
        }

        if (
            item.confidence < 0 ||
            item.confidence > 1
        ) {
            throw invalid_argument("Invalid confidence");
        }

        if (item.type == RoadmapType::Outcome && !item.metric) {
            throw invalid_argument(
                "Outcome item requires a metric"
            );
        }

        if (
            item.type == RoadmapType::NowNextLater &&
            !item.horizon
        ) {
            throw invalid_argument(
                "Horizon item requires a planning horizon"
            );
        }

        if (items.count(item.id)) {
            throw invalid_argument("Duplicate item ID");
        }

        if (item.dependencies.count(item.id)) {
            throw invalid_argument(
                "Self-dependency is prohibited"
            );
        }

        if (item.themeId && !themes.count(*item.themeId)) {
            throw invalid_argument("Unknown theme");
        }

        for (const auto& dependency : item.dependencies) {
            if (!items.count(dependency)) {
                throw runtime_error(
                    "Dependency must exist before insertion"
                );
            }
        }

        string id = item.id;
        optional<string> themeId = item.themeId;

        items.emplace(id, move(item));

        try {
            validateDependencies();
        } catch (...) {
            items.erase(id);
            throw;
        }

        if (themeId) {
            themes.at(*themeId).itemIds.insert(id);
        }
    }

    void validateDependencies() const {
        unordered_map<string, int> state;

        for (const auto& entry : items) {
            if (state[entry.first] == 0) {
                visit(entry.first, state);
            }
        }
    }

    RoadmapItem& getItem(const string& id) {
        auto it = items.find(id);

        if (it == items.end()) {
            throw out_of_range("Roadmap item not found");
        }

        return it->second;
    }

    const RoadmapItem& getItem(const string& id) const {
        auto it = items.find(id);

        if (it == items.end()) {
            throw out_of_range("Roadmap item not found");
        }

        return it->second;
    }

    void updateStatus(
        const string& id,
        Status nextStatus
    ) {
        auto& item = getItem(id);

        if (
            item.status == Status::Completed ||
            item.status == Status::Cancelled
        ) {
            throw runtime_error(
                "Cannot modify terminal item"
            );
        }

        if (nextStatus == Status::InProgress) {
            for (const auto& dependency : item.dependencies) {
                if (
                    getItem(dependency).status !=
                    Status::Completed
                ) {
                    throw runtime_error(
                        "Dependencies are not completed"
                    );
                }
            }
        }

        item.status = nextStatus;

        if (nextStatus == Status::Completed) {
            item.progress = 100;
        }
    }

    void updateMetric(
        const string& id,
        double current
    ) {
        auto& item = getItem(id);

        if (!item.metric) {
            throw runtime_error(
                "Item has no outcome metric"
            );
        }

        if (current < 0) {
            throw invalid_argument(
                "Metric value cannot be negative"
            );
        }

        item.metric->current = current;
    }

    void updateHorizon(
        const string& id,
        Horizon horizon
    ) {
        auto& item = getItem(id);

        if (item.type != RoadmapType::NowNextLater) {
            throw runtime_error(
                "Item is not part of a horizon roadmap"
            );
        }

        item.horizon = horizon;
    }

    vector<RoadmapItem> prioritizedItems() const {
        vector<RoadmapItem> result;

        for (const auto& entry : items) {
            result.push_back(entry.second);
        }

        sort(
            result.begin(),
            result.end(),
            [](const RoadmapItem& a, const RoadmapItem& b) {
                if (a.priority != b.priority) {
                    return static_cast<int>(a.priority) <
                           static_cast<int>(b.priority);
                }

                return a.confidence > b.confidence;
            }
        );

        return result;
    }

    map<string, vector<string>> horizonReport() const {
        map<string, vector<string>> report = {
            {"Now", {}},
            {"Next", {}},
            {"Later", {}}
        };

        for (const auto& entry : items) {
            const auto& item = entry.second;

            if (item.horizon) {
                report[toString(*item.horizon)].push_back(
                    item.title
                );
            }
        }

        return report;
    }

    void printReport() const {
        map<string, int> counts;

        int completed = 0;

        for (const auto& entry : items) {
            string status = toString(entry.second.status);

            counts[status]++;

            if (entry.second.status == Status::Completed) {
                completed++;
            }
        }

        double completion = items.empty()
            ? 0.0
            : 100.0 * completed / items.size();

        cout << "\nRoadmap: " << name << "\n";
        cout << "Type: " << toString(type) << "\n";
        cout << "Items: " << items.size() << "\n";

        cout << fixed << setprecision(2);
        cout << "Completion: " << completion << "%\n";

        for (const auto& entry : counts) {
            cout << entry.first << ": "
                 << entry.second << "\n";
        }
    }

    void printOutcomes() const {
        cout << "\nOUTCOME EVALUATION\n";

        for (const auto& entry : items) {
            const auto& item = entry.second;

            if (!item.metric) {
                continue;
            }

            cout << item.title << "\n";
            cout << "Metric: " << item.metric->name << "\n";
            cout << "Baseline: " << item.metric->baseline << "\n";
            cout << "Target: " << item.metric->target << "\n";
            cout << "Current: " << item.metric->current << "\n";
            cout << "Progress: "
                 << item.metric->progress() << "%\n";
        }
    }

    size_t size() const {
        return items.size();
    }
};

RoadmapItem makeItem(
    string id,
    string title,
    string owner,
    RoadmapType type,
    Priority priority = Priority::Medium
) {
    return RoadmapItem{
        move(id),
        move(title),
        "Roadmap delivery item",
        move(owner),
        type,
        Status::Proposed,
        priority,
        0.0,
        0.8,
        nullopt,
        nullopt,
        nullopt,
        {},
        {}
    };
}

void runTests() {
    Roadmap roadmap(
        "Feature Validation",
        RoadmapType::Feature
    );

    auto first = makeItem(
        "F1",
        "Authentication",
        "Security",
        RoadmapType::Feature,
        Priority::Critical
    );

    auto second = makeItem(
        "F2",
        "Analytics",
        "Product",
        RoadmapType::Feature,
        Priority::High
    );

    second.dependencies.insert("F1");

    roadmap.addItem(first);
    roadmap.addItem(second);

    roadmap.updateStatus("F1", Status::Completed);
    roadmap.updateStatus("F2", Status::InProgress);

    if (roadmap.getItem("F1").progress != 100) {
        throw runtime_error("Completion test failed");
    }

    if (roadmap.size() != 2) {
        throw runtime_error("Item count test failed");
    }

    Roadmap invalid(
        "Invalid Roadmap",
        RoadmapType::Outcome
    );

    auto invalidItem = makeItem(
        "O1",
        "Missing metric",
        "Operations",
        RoadmapType::Outcome
    );

    try {
        invalid.addItem(invalidItem);
        throw runtime_error("Metric validation failed");
    } catch (const invalid_argument&) {
        // Expected validation failure.
    }

    cout << "C++ tests passed.\n";
}

int main() {
    try {
        Roadmap features(
            "Customer Platform Features",
            RoadmapType::Feature
        );

        features.addItem(
            makeItem(
                "F001",
                "Multi-factor authentication",
                "Security Team",
                RoadmapType::Feature,
                Priority::Critical
            )
        );

        auto analytics = makeItem(
            "F002",
            "Usage analytics",
            "Product Team",
            RoadmapType::Feature,
            Priority::High
        );

        analytics.dependencies.insert("F001");

        features.addItem(analytics);

        features.updateStatus(
            "F001",
            Status::Completed
        );

        features.updateStatus(
            "F002",
            Status::InProgress
        );

        features.printReport();

        Roadmap outcomes(
            "Customer Experience Outcomes",
            RoadmapType::Outcome
        );

        auto outcome = makeItem(
            "O001",
            "Reduce onboarding duration",
            "Operations",
            RoadmapType::Outcome
        );

        outcome.metric = Metric(
            "Onboarding duration",
            10,
            4,
            6,
            "days"
        );

        outcomes.addItem(outcome);
        outcomes.updateMetric("O001", 5);
        outcomes.printOutcomes();

        Roadmap themes(
            "Strategic Investment Themes",
            RoadmapType::Theme
        );

        themes.addTheme(Theme{
            "T001",
            "Trust and Security",
            "Improve platform security",
            "Technology Office",
            {}
        });

        auto audit = makeItem(
            "TITEM001",
            "Centralized audit logging",
            "Platform Engineering",
            RoadmapType::Theme,
            Priority::High
        );

        audit.themeId = "T001";
        themes.addItem(audit);
        themes.printReport();

        Roadmap horizons(
            "Product Planning Horizons",
            RoadmapType::NowNextLater
        );

        auto payment = makeItem(
            "H001",
            "Resolve payment failures",
            "Payments",
            RoadmapType::NowNextLater,
            Priority::Critical
        );

        payment.horizon = Horizon::Now;

        auto reporting = makeItem(
            "H002",
            "Improve reporting",
            "Analytics",
            RoadmapType::NowNextLater
        );

        reporting.horizon = Horizon::Next;

        auto predictive = makeItem(
            "H003",
            "Predictive planning",
            "Strategy",
            RoadmapType::NowNextLater
        );

        predictive.horizon = Horizon::Later;

        horizons.addItem(payment);
        horizons.addItem(reporting);
        horizons.addItem(predictive);

        cout << "\nHORIZON ROADMAP\n";

        for (const auto& entry : horizons.horizonReport()) {
            cout << entry.first << ":\n";

            for (const auto& title : entry.second) {
                cout << "  - " << title << "\n";
            }
        }

        runTests();

    } catch (const exception& error) {
        cerr << "Roadmap failure: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
