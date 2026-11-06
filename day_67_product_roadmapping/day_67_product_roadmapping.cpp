#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

enum class InitiativeStatus {
    Proposed,
    Planned,
    InProgress,
    Blocked,
    Completed
};

string statusName(InitiativeStatus status) {
    switch (status) {
        case InitiativeStatus::Proposed: return "Proposed";
        case InitiativeStatus::Planned: return "Planned";
        case InitiativeStatus::InProgress: return "In Progress";
        case InitiativeStatus::Blocked: return "Blocked";
        case InitiativeStatus::Completed: return "Completed";
    }
    return "Unknown";
}

struct Theme {
    string id;
    string name;
    string strategicObjective;
};

struct Outcome {
    string id;
    string description;
    double baseline;
    double target;
    double current;
    string unit;

    double progress() const {
        if (target == baseline) {
            return current == target ? 100.0 : 0.0;
        }

        double value =
            (current - baseline) / (target - baseline) * 100.0;

        return max(0.0, min(100.0, value));
    }

    bool achieved() const {
        return target >= baseline
            ? current >= target
            : current <= target;
    }
};

struct Initiative {
    string id;
    string name;
    string themeId;
    string outcomeId;

    int startDay;
    int endDay;
    int effort;

    double impact;
    double confidence;
    double alignment;

    vector<string> dependencies;
    InitiativeStatus status = InitiativeStatus::Proposed;

    double priorityScore() const {
        return impact * confidence * alignment / effort;
    }
};

class RoadmapEngine {
private:
    string productName;
    int planningStart;
    int planningEnd;
    int sprintCapacity;

    unordered_map<string, Theme> themes;
    unordered_map<string, Outcome> outcomes;
    unordered_map<string, Initiative> initiatives;

    void validateScore(double value) const {
        if (!isfinite(value) || value < 0 || value > 10) {
            throw invalid_argument("Scores must be between 0 and 10.");
        }
    }

    void dfs(
        const string& id,
        unordered_set<string>& visiting,
        unordered_set<string>& visited,
        vector<string>& order
    ) const {
        if (visiting.count(id)) {
            throw runtime_error("Circular dependency detected.");
        }

        if (visited.count(id)) return;

        auto it = initiatives.find(id);

        if (it == initiatives.end()) {
            throw runtime_error("Unknown initiative dependency: " + id);
        }

        visiting.insert(id);

        for (const string& dependency : it->second.dependencies) {
            dfs(dependency, visiting, visited, order);
        }

        visiting.erase(id);
        visited.insert(id);
        order.push_back(id);
    }

public:
    RoadmapEngine(
        string product,
        int start,
        int end,
        int capacity
    ) : productName(move(product)),
        planningStart(start),
        planningEnd(end),
        sprintCapacity(capacity) {

        if (productName.empty()) {
            throw invalid_argument("Product name is required.");
        }

        if (start > end || capacity <= 0) {
            throw invalid_argument("Invalid planning configuration.");
        }
    }

    void addTheme(const Theme& theme) {
        if (theme.id.empty() || theme.name.empty()) {
            throw invalid_argument("Theme fields cannot be empty.");
        }

        if (!themes.emplace(theme.id, theme).second) {
            throw invalid_argument("Duplicate theme.");
        }
    }

    void addOutcome(const Outcome& outcome) {
        if (outcome.id.empty() || outcome.description.empty()) {
            throw invalid_argument("Invalid outcome identity.");
        }

        if (
            !isfinite(outcome.baseline) ||
            !isfinite(outcome.target) ||
            !isfinite(outcome.current) ||
            outcome.baseline == outcome.target
        ) {
            throw invalid_argument("Invalid outcome measurements.");
        }

        if (!outcomes.emplace(outcome.id, outcome).second) {
            throw invalid_argument("Duplicate outcome.");
        }
    }

    void addInitiative(const Initiative& item) {
        if (item.id.empty() || item.name.empty()) {
            throw invalid_argument("Initiative identity is required.");
        }

        if (!themes.count(item.themeId)) {
            throw invalid_argument("Unknown strategic theme.");
        }

        if (!outcomes.count(item.outcomeId)) {
            throw invalid_argument("Unknown outcome.");
        }

        if (
            item.startDay < planningStart ||
            item.endDay > planningEnd ||
            item.startDay > item.endDay ||
            item.effort <= 0
        ) {
            throw invalid_argument("Invalid initiative constraints.");
        }

        validateScore(item.impact);
        validateScore(item.confidence);
        validateScore(item.alignment);

        if (
            item.confidence > 1.0 ||
            item.alignment > 1.0
        ) {
            throw invalid_argument(
                "Confidence and alignment must be normalized to [0,1]."
            );
        }

        if (item.dependencies.size() !=
            unordered_set<string>(
                item.dependencies.begin(),
                item.dependencies.end()
            ).size()) {
            throw invalid_argument("Duplicate dependencies.");
        }

        if (!initiatives.emplace(item.id, item).second) {
            throw invalid_argument("Duplicate initiative.");
        }
    }

    vector<string> dependencyOrder() const {
        unordered_set<string> visiting;
        unordered_set<string> visited;
        vector<string> order;

        for (const auto& entry : initiatives) {
            dfs(entry.first, visiting, visited, order);
        }

        reverse(order.begin(), order.end());

        return order;
    }

    void validateTimelines() const {
        dependencyOrder();

        for (const auto& entry : initiatives) {
            const Initiative& item = entry.second;

            for (const string& dependencyId : item.dependencies) {
                const Initiative& dependency =
                    initiatives.at(dependencyId);

                if (dependency.endDay >= item.startDay) {
                    throw runtime_error(
                        item.id + " starts before its dependency finishes."
                    );
                }
            }
        }
    }

    void updateStatus(
        const string& id,
        InitiativeStatus next
    ) {
        auto it = initiatives.find(id);

        if (it == initiatives.end()) {
            throw runtime_error("Initiative not found.");
        }

        Initiative& item = it->second;
        InitiativeStatus current = item.status;

        bool valid = false;

        switch (current) {
            case InitiativeStatus::Proposed:
                valid = next == InitiativeStatus::Planned;
                break;

            case InitiativeStatus::Planned:
                valid =
                    next == InitiativeStatus::InProgress ||
                    next == InitiativeStatus::Blocked;
                break;

            case InitiativeStatus::InProgress:
                valid =
                    next == InitiativeStatus::Blocked ||
                    next == InitiativeStatus::Completed;
                break;

            case InitiativeStatus::Blocked:
                valid =
                    next == InitiativeStatus::Planned ||
                    next == InitiativeStatus::InProgress;
                break;

            case InitiativeStatus::Completed:
                valid = false;
                break;
        }

        if (!valid) {
            throw runtime_error("Invalid initiative state transition.");
        }

        if (next == InitiativeStatus::InProgress) {
            for (const string& dependency : item.dependencies) {
                if (
                    initiatives.at(dependency).status
                    != InitiativeStatus::Completed
                ) {
                    throw runtime_error(
                        "Initiative has unfinished dependencies."
                    );
                }
            }
        }

        item.status = next;
    }

    vector<Initiative> prioritized() const {
        vector<Initiative> result;

        for (const auto& entry : initiatives) {
            result.push_back(entry.second);
        }

        sort(
            result.begin(),
            result.end(),
            [](const Initiative& a, const Initiative& b) {
                if (a.priorityScore() != b.priorityScore()) {
                    return a.priorityScore() > b.priorityScore();
                }
                return a.id < b.id;
            }
        );

        return result;
    }

    vector<string> readyInitiatives() const {
        vector<string> ready;

        for (const auto& entry : initiatives) {
            const Initiative& item = entry.second;

            if (item.status != InitiativeStatus::Planned) continue;

            bool dependenciesComplete = all_of(
                item.dependencies.begin(),
                item.dependencies.end(),
                [&](const string& id) {
                    return initiatives.at(id).status
                        == InitiativeStatus::Completed;
                }
            );

            if (dependenciesComplete) {
                ready.push_back(item.id);
            }
        }

        return ready;
    }

    struct CriticalPathResult {
        int duration;
        vector<string> path;
    };

    CriticalPathResult criticalPath() const {
        vector<string> order = dependencyOrder();

        unordered_map<string, int> longest;
        unordered_map<string, string> predecessor;

        int maximumDuration = 0;
        string finalId;

        for (const string& id : order) {
            const Initiative& item = initiatives.at(id);

            int best = 0;
            string bestPredecessor;

            for (const string& dependency : item.dependencies) {
                if (longest[dependency] > best) {
                    best = longest[dependency];
                    bestPredecessor = dependency;
                }
            }

            int duration = item.endDay - item.startDay + 1;
            longest[id] = best + duration;
            predecessor[id] = bestPredecessor;

            if (longest[id] > maximumDuration) {
                maximumDuration = longest[id];
                finalId = id;
            }
        }

        vector<string> path;

        while (!finalId.empty()) {
            path.push_back(finalId);
            finalId = predecessor[finalId];
        }

        reverse(path.begin(), path.end());

        return {maximumDuration, path};
    }

    map<int, int> capacityReport() const {
        map<int, int> report;

        for (const auto& entry : initiatives) {
            const Initiative& item = entry.second;

            if (item.status == InitiativeStatus::Proposed) {
                continue;
            }

            int firstSprint =
                (item.startDay - planningStart) / 14;

            int lastSprint =
                (item.endDay - planningStart) / 14;

            for (
                int sprint = firstSprint;
                sprint <= lastSprint;
                ++sprint
            ) {
                report[sprint] += item.effort;
            }
        }

        return report;
    }

    void printReport() const {
        cout << "\nPRODUCT ROADMAP: " << productName << "\n";
        cout << string(75, '=') << "\n";

        cout << "\nSTRATEGIC THEMES\n";

        for (const auto& entry : themes) {
            cout << entry.second.id << " | "
                 << entry.second.name << " | "
                 << entry.second.strategicObjective << "\n";
        }

        cout << "\nINITIATIVE PRIORITY\n";

        for (const Initiative& item : prioritized()) {
            cout << fixed << setprecision(2)
                 << item.id << " | "
                 << item.name << " | Score: "
                 << item.priorityScore()
                 << " | Effort: " << item.effort
                 << " | Status: " << statusName(item.status)
                 << "\n";
        }

        cout << "\nOUTCOME PERFORMANCE\n";

        for (const auto& entry : outcomes) {
            const Outcome& outcome = entry.second;

            cout << outcome.id << " | "
                 << outcome.description
                 << " | Current: " << outcome.current
                 << " | Target: " << outcome.target
                 << " | Progress: " << outcome.progress()
                 << "% | Achieved: "
                 << (outcome.achieved() ? "Yes" : "No")
                 << "\n";
        }

        cout << "\nSPRINT CAPACITY\n";

        for (const auto& entry : capacityReport()) {
            cout << "Sprint " << entry.first + 1
                 << ": " << entry.second
                 << "/" << sprintCapacity
                 << " | Overloaded: "
                 << (entry.second > sprintCapacity ? "Yes" : "No")
                 << "\n";
        }

        CriticalPathResult critical = criticalPath();

        cout << "\nCRITICAL DEPENDENCY PATH\n";
        cout << "Duration: " << critical.duration << " days\n";

        for (size_t i = 0; i < critical.path.size(); ++i) {
            if (i) cout << " -> ";
            cout << critical.path[i];
        }

        cout << "\n";
    }
};

int main() {
    try {
        RoadmapEngine roadmap(
            "Enterprise Commerce Platform",
            0,
            89,
            40
        );

        roadmap.addTheme({
            "T1",
            "Customer Experience",
            "Increase checkout conversion."
        });

        roadmap.addTheme({
            "T2",
            "Platform Reliability",
            "Improve infrastructure availability."
        });

        roadmap.addTheme({
            "T3",
            "Revenue Growth",
            "Increase digital sales."
        });

        roadmap.addOutcome({
            "O1",
            "Checkout conversion",
            65,
            85,
            72,
            "%"
        });

        roadmap.addOutcome({
            "O2",
            "System availability",
            99,
            99.9,
            99.5,
            "%"
        });

        roadmap.addInitiative({
            "I1",
            "Payment Infrastructure Upgrade",
            "T2",
            "O2",
            0,
            19,
            30,
            9,
            0.9,
            1.0,
            {},
            InitiativeStatus::Planned
        });

        roadmap.addInitiative({
            "I2",
            "Checkout Optimization",
            "T1",
            "O1",
            20,
            40,
            25,
            8,
            0.85,
            0.9,
            {"I1"},
            InitiativeStatus::Planned
        });

        roadmap.addInitiative({
            "I3",
            "One-Click Checkout",
            "T1",
            "O1",
            41,
            65,
            40,
            10,
            0.8,
            1.0,
            {"I2"},
            InitiativeStatus::Planned
        });

        roadmap.addInitiative({
            "I4",
            "Product Recommendations",
            "T3",
            "O1",
            10,
            35,
            20,
            8,
            0.75,
            0.8,
            {},
            InitiativeStatus::Proposed
        });

        roadmap.validateTimelines();
        roadmap.printReport();

        cout << "\nREADY INITIATIVES\n";

        for (const string& id : roadmap.readyInitiatives()) {
            cout << id << "\n";
        }

        roadmap.updateStatus(
            "I1",
            InitiativeStatus::Completed
        );

        roadmap.updateStatus(
            "I2",
            InitiativeStatus::InProgress
        );

        cout << "\nDEPENDENCY-VALIDATED STATUS UPDATE\n";
        cout << "I2: In Progress\n";

        // A proposed initiative cannot start without planning approval.
        try {
            roadmap.updateStatus(
                "I4",
                InitiativeStatus::InProgress
            );
        } catch (const exception& error) {
            cout << "\nEXPECTED POLICY ERROR: "
                 << error.what() << "\n";
        }

    } catch (const exception& error) {
        cerr << "Roadmap failure: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
