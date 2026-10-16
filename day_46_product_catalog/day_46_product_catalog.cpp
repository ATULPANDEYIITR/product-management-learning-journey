#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class WorkType { Feature, Defect, Security, TechnicalDebt, Investigation };
enum class State { Proposed, Refining, Ready, InProgress, Blocked, Done, Rejected };

string toString(WorkType type) {
    switch (type) {
        case WorkType::Feature: return "Feature";
        case WorkType::Defect: return "Defect";
        case WorkType::Security: return "Security";
        case WorkType::TechnicalDebt: return "Technical debt";
        case WorkType::Investigation: return "Investigation";
    }
    throw logic_error("Unknown work type");
}

string toString(State state) {
    switch (state) {
        case State::Proposed: return "Proposed";
        case State::Refining: return "Refining";
        case State::Ready: return "Ready";
        case State::InProgress: return "In progress";
        case State::Blocked: return "Blocked";
        case State::Done: return "Done";
        case State::Rejected: return "Rejected";
    }
    throw logic_error("Unknown state");
}

struct WorkItem {
    string id;
    string title;
    WorkType type;
    State state;
    int value;
    int urgency;
    int riskReduction;
    int effort;
    double debtPrincipal;
    double debtInterestPerSprint;
    set<string> dependencies;
    vector<string> acceptanceCriteria;

    WorkItem(
        string itemId, string itemTitle, WorkType itemType,
        int businessValue, int itemUrgency, int risk, int itemEffort,
        double principal = 0, double interest = 0
    ) : id(std::move(itemId)),
        title(std::move(itemTitle)),
        type(itemType),
        state(State::Proposed),
        value(businessValue),
        urgency(itemUrgency),
        riskReduction(risk),
        effort(itemEffort),
        debtPrincipal(principal),
        debtInterestPerSprint(interest) {
        if (id.empty() || title.empty()) {
            throw invalid_argument("Work item ID and title are required");
        }
        if (value < 1 || value > 10 || urgency < 1 || urgency > 10 ||
            riskReduction < 1 || riskReduction > 10) {
            throw invalid_argument("Business scores must be between 1 and 10");
        }
        if (effort < 1 || effort > 100 || principal < 0 || interest < 0) {
            throw invalid_argument("Invalid effort or debt estimate");
        }
    }
};

class Backlog {
private:
    map<string, WorkItem> items;
    int capacity;

    void visit(
        const string& id, map<string, int>& color
    ) const {
        if (color[id] == 1) {
            throw invalid_argument("Circular dependency detected at " + id);
        }
        if (color[id] == 2) return;

        color[id] = 1;
        for (const string& dependency : items.at(id).dependencies) {
            if (!items.count(dependency)) {
                throw invalid_argument("Unknown dependency: " + dependency);
            }
            visit(dependency, color);
        }
        color[id] = 2;
    }

    void validateAcyclic() const {
        map<string, int> color;
        for (const auto& entry : items) visit(entry.first, color);
    }

public:
    explicit Backlog(int sprintCapacity) : capacity(sprintCapacity) {
        if (capacity < 1) {
            throw invalid_argument("Sprint capacity must be positive");
        }
    }

    const WorkItem& get(const string& id) const {
        auto found = items.find(id);
        if (found == items.end()) throw out_of_range("Unknown item: " + id);
        return found->second;
    }

    void add(WorkItem item) {
        if (items.count(item.id)) {
            throw invalid_argument("Duplicate item ID: " + item.id);
        }
        if (item.dependencies.count(item.id)) {
            throw invalid_argument("An item cannot depend on itself");
        }
        for (const string& dependency : item.dependencies) {
            if (!items.count(dependency)) {
                throw invalid_argument("Add prerequisites before dependent items");
            }
        }
        const string id = item.id;
        items.emplace(id, std::move(item));
        try {
            validateAcyclic();
        } catch (...) {
            items.erase(id);
            throw;
        }
    }

    void addDependency(const string& id, const string& dependency) {
        WorkItem& item = items.at(id);
        if (!items.count(dependency)) {
            throw out_of_range("Unknown prerequisite: " + dependency);
        }
        if (id == dependency) throw invalid_argument("Self-dependency rejected");
        if (item.state == State::InProgress || item.state == State::Done) {
            throw invalid_argument("Cannot change dependencies after work starts");
        }

        item.dependencies.insert(dependency);
        try {
            validateAcyclic();
        } catch (...) {
            item.dependencies.erase(dependency);
            throw;
        }
    }

    double score(const WorkItem& item) const {
        const double costOfDelay =
            item.value * 0.5 + item.urgency * 0.3 +
            item.riskReduction * 0.2;
        return costOfDelay / item.effort;
    }

    int priorityBand(const WorkItem& item) const {
        if ((item.type == WorkType::Security || item.type == WorkType::Defect) &&
            (item.urgency >= 9 || item.riskReduction >= 9)) return 0;
        const double value = score(item);
        if (value >= 3.5) return 1;
        if (value >= 1.8) return 2;
        return 3;
    }

    vector<string> blockers(const string& id) const {
        vector<string> result;
        for (const string& dependency : get(id).dependencies) {
            if (get(dependency).state != State::Done) result.push_back(dependency);
        }
        return result;
    }

    void transition(const string& id, State next) {
        WorkItem& item = items.at(id);
        bool allowed = false;
        switch (item.state) {
            case State::Proposed:
                allowed = next == State::Refining || next == State::Rejected;
                break;
            case State::Refining:
                allowed = next == State::Proposed || next == State::Ready ||
                          next == State::Rejected;
                break;
            case State::Ready:
                allowed = next == State::Refining || next == State::InProgress ||
                          next == State::Rejected;
                break;
            case State::InProgress:
                allowed = next == State::Blocked || next == State::Done ||
                          next == State::Ready;
                break;
            case State::Blocked:
                allowed = next == State::InProgress || next == State::Ready;
                break;
            case State::Done:
                allowed = false;
                break;
            case State::Rejected:
                allowed = next == State::Refining;
                break;
        }

        if (!allowed) {
            throw invalid_argument(
                "Invalid transition " + toString(item.state) + " -> " +
                toString(next) + " for " + id
            );
        }
        if (next == State::Ready && item.acceptanceCriteria.empty()) {
            throw invalid_argument("Ready work requires acceptance criteria");
        }
        if ((next == State::Ready || next == State::InProgress) &&
            !blockers(id).empty()) {
            throw invalid_argument("Unfinished prerequisites block this transition");
        }
        item.state = next;
    }

    vector<string> prioritize() const {
        vector<string> ids;
        for (const auto& entry : items) {
            if (entry.second.state != State::Done &&
                entry.second.state != State::Rejected) {
                ids.push_back(entry.first);
            }
        }
        sort(ids.begin(), ids.end(), [this](const string& a, const string& b) {
            const WorkItem& first = items.at(a);
            const WorkItem& second = items.at(b);
            if (priorityBand(first) != priorityBand(second)) {
                return priorityBand(first) < priorityBand(second);
            }
            if (abs(score(first) - score(second)) > 1e-9) {
                return score(first) > score(second);
            }
            return a < b;
        });
        return ids;
    }

    vector<string> planSprint() const {
        vector<string> plan;
        set<string> satisfied;
        for (const auto& entry : items) {
            if (entry.second.state == State::Done) satisfied.insert(entry.first);
        }

        int used = 0;
        while (true) {
            bool added = false;
            for (const string& id : prioritize()) {
                const WorkItem& item = items.at(id);
                if (item.state != State::Ready || satisfied.count(id)) continue;

                bool dependenciesSatisfied = true;
                for (const string& dependency : item.dependencies) {
                    if (!satisfied.count(dependency)) {
                        dependenciesSatisfied = false;
                        break;
                    }
                }
                if (!dependenciesSatisfied || used + item.effort > capacity) continue;

                plan.push_back(id);
                satisfied.insert(id);
                used += item.effort;
                added = true;
                break;
            }
            if (!added) break;
        }
        return plan;
    }

    void printDebtForecast(int sprints) const {
        if (sprints < 0) throw invalid_argument("Sprint horizon cannot be negative");
        vector<pair<double, string>> forecast;
        for (const auto& entry : items) {
            const WorkItem& item = entry.second;
            if (item.type == WorkType::TechnicalDebt) {
                const double projected = item.debtPrincipal +
                    item.debtInterestPerSprint * sprints;
                forecast.emplace_back(projected, item.id);
            }
        }
        sort(forecast.rbegin(), forecast.rend());

        cout << "\nTechnical debt forecast over " << sprints << " sprints\n";
        for (const auto& row : forecast) {
            const WorkItem& item = items.at(row.second);
            cout << item.id << ": principal=" << item.debtPrincipal
                 << ", projected cost=" << fixed << setprecision(2)
                 << row.first << '\n';
        }
    }

    void printPriorities() const {
        cout << "\nPrioritized backlog\n";
        cout << left << setw(12) << "ID" << setw(20) << "Type"
             << setw(10) << "Score" << setw(10) << "Effort"
             << "Title\n";
        for (const string& id : prioritize()) {
            const WorkItem& item = items.at(id);
            cout << left << setw(12) << item.id << setw(20) << toString(item.type)
                 << setw(10) << fixed << setprecision(2) << score(item)
                 << setw(10) << item.effort << item.title << '\n';
        }
    }
};

int main() {
    try {
        Backlog backlog(12);

        WorkItem foundation(
            "OPS-301", "Standardize service identity",
            WorkType::Feature, 9, 8, 8, 4
        );
        foundation.acceptanceCriteria = {
            "Every service has a stable identity",
            "Identity propagation is covered by integration tests"
        };
        backlog.add(foundation);

        WorkItem telemetry(
            "OPS-302", "Correlate distributed traces",
            WorkType::Feature, 8, 7, 8, 4
        );
        telemetry.dependencies.insert("OPS-301");
        telemetry.acceptanceCriteria = {
            "Trace identifiers cross service boundaries",
            "Identifiers are not derived from customer secrets"
        };
        backlog.add(telemetry);

        WorkItem debt(
            "OPS-303", "Replace inefficient permission lookups",
            WorkType::TechnicalDebt, 7, 6, 8, 3, 12000, 1600
        );
        debt.acceptanceCriteria = {
            "Lookup cost does not grow linearly with repeated requests",
            "Authorization decisions remain unchanged"
        };
        backlog.add(debt);

        WorkItem security(
            "OPS-304", "Correct tenant isolation defect",
            WorkType::Security, 10, 10, 10, 2
        );
        security.acceptanceCriteria = {
            "A tenant cannot retrieve another tenant's data",
            "Negative authorization tests pass"
        };
        backlog.add(security);

        for (const string& id : {"OPS-301", "OPS-302", "OPS-303", "OPS-304"}) {
            backlog.transition(id, State::Refining);
            backlog.transition(id, State::Ready);
        }

        backlog.printPriorities();
        backlog.printDebtForecast(6);

        cout << "\nDependency-aware sprint plan\n";
        int used = 0;
        for (const string& id : backlog.planSprint()) {
            const WorkItem& item = backlog.get(id);
            cout << id << ": " << item.title << '\n';
            used += item.effort;
        }
        cout << "Planned effort: " << used << "/12\n";

        cout << "\nTesting dependency-cycle rejection\n";
        try {
            backlog.addDependency("OPS-301", "OPS-302");
        } catch (const exception& error) {
            cout << "Rejected as expected: " << error.what() << '\n';
        }

        cout << "\nTesting readiness requirements\n";
        try {
            WorkItem incomplete(
                "OPS-305", "Unrefined reporting request",
                WorkType::Feature, 4, 4, 3, 2
            );
            backlog.add(incomplete);
            backlog.transition("OPS-305", State::Refining);
            backlog.transition("OPS-305", State::Ready);
        } catch (const exception& error) {
            cout << "Rejected as expected: " << error.what() << '\n';
        }

        cout << "\nTesting immutable completion state\n";
        try {
            backlog.transition("OPS-304", State::InProgress);
            backlog.transition("OPS-304", State::Done);
            backlog.transition("OPS-304", State::Ready);
        } catch (const exception& error) {
            cout << "Rejected as expected: " << error.what() << '\n';
        }
    } catch (const exception& error) {
        cerr << "Fatal backlog error: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
