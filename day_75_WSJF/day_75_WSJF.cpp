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

/*
 * C++17 WSJF governance and scheduling engine.
 *
 * Cost of Delay = Business Value + Time Criticality + Risk Reduction
 * WSJF = Cost of Delay / Job Size
 *
 * Supports:
 * - Strongly typed work-item states
 * - Backlog validation
 * - Dependency graph validation
 * - Reviewable prioritization results
 * - Repository and operational risk scoring
 * - Capacity-constrained scheduling
 * - Deterministic ranking
 */

enum class Status {
    BACKLOG,
    READY,
    IN_PROGRESS,
    BLOCKED,
    COMPLETED
};

string statusName(Status status) {
    switch (status) {
        case Status::BACKLOG: return "BACKLOG";
        case Status::READY: return "READY";
        case Status::IN_PROGRESS: return "IN_PROGRESS";
        case Status::BLOCKED: return "BLOCKED";
        case Status::COMPLETED: return "COMPLETED";
    }

    throw logic_error("Unknown status");
}

struct WorkItem {
    string id;
    string title;
    double businessValue;
    double timeCriticality;
    double riskReduction;
    double jobSize;
    Status status = Status::READY;
    set<string> dependencies;

    double costOfDelay() const {
        return businessValue + timeCriticality + riskReduction;
    }

    double wsjf() const {
        return costOfDelay() / jobSize;
    }
};

struct RankedItem {
    WorkItem item;
    double costOfDelay;
    double score;
};

struct Schedule {
    vector<WorkItem> selected;
    double usedCapacity = 0.0;
    double remainingCapacity = 0.0;
};

class WSJFEngine {
private:
    map<string, WorkItem> items;

    static void validateNumber(
        double value,
        const string& field,
        bool allowZero = true
    ) {
        if (!isfinite(value) ||
            value < 0 ||
            (!allowZero && value <= 0)) {
            throw invalid_argument("Invalid " + field);
        }
    }

    void validateDependencyGraph() const {
        enum class Mark {
            UNVISITED,
            VISITING,
            VISITED
        };

        map<string, Mark> marks;

        for (const auto& [id, item] : items) {
            marks[id] = Mark::UNVISITED;
        }

        function<void(const string&)> visit =
            [&](const string& id) {

            if (marks[id] == Mark::VISITING) {
                throw invalid_argument(
                    "Dependency cycle at " + id
                );
            }

            if (marks[id] == Mark::VISITED) {
                return;
            }

            marks[id] = Mark::VISITING;

            for (const string& dependency :
                 items.at(id).dependencies) {

                if (items.find(dependency) == items.end()) {
                    throw invalid_argument(
                        "Missing dependency: " + dependency
                    );
                }

                visit(dependency);
            }

            marks[id] = Mark::VISITED;
        };

        for (const auto& [id, item] : items) {
            visit(id);
        }
    }

public:
    void addWorkItem(const WorkItem& item) {
        if (item.id.empty() || item.title.empty()) {
            throw invalid_argument("ID and title are required");
        }

        validateNumber(item.businessValue, "business value");
        validateNumber(item.timeCriticality, "time criticality");
        validateNumber(item.riskReduction, "risk reduction");
        validateNumber(item.jobSize, "job size", false);

        if (item.dependencies.count(item.id)) {
            throw invalid_argument("Self-dependency is prohibited");
        }

        if (items.count(item.id)) {
            throw invalid_argument("Duplicate item ID: " + item.id);
        }

        items.emplace(item.id, item);

        try {
            validateDependencyGraph();
        } catch (...) {
            items.erase(item.id);
            throw;
        }
    }

    void changeStatus(
        const string& id,
        Status nextStatus
    ) {
        if (!items.count(id)) {
            throw invalid_argument("Unknown item: " + id);
        }

        WorkItem& item = items.at(id);
        Status current = item.status;

        map<Status, set<Status>> transitions = {
            {Status::BACKLOG,
             {Status::READY, Status::BLOCKED}},
            {Status::READY,
             {Status::BACKLOG, Status::IN_PROGRESS, Status::BLOCKED}},
            {Status::IN_PROGRESS,
             {Status::READY, Status::BLOCKED, Status::COMPLETED}},
            {Status::BLOCKED,
             {Status::READY, Status::BACKLOG}},
            {Status::COMPLETED, {}}
        };

        if (!transitions[current].count(nextStatus)) {
            throw invalid_argument(
                "Invalid status transition: " +
                statusName(current) + " -> " +
                statusName(nextStatus)
            );
        }

        if (nextStatus == Status::READY) {
            for (const string& dependency : item.dependencies) {
                if (items.at(dependency).status != Status::COMPLETED) {
                    throw invalid_argument(
                        "Incomplete dependency: " + dependency
                    );
                }
            }
        }

        item.status = nextStatus;
    }

    vector<RankedItem> ranking() const {
        vector<RankedItem> result;

        for (const auto& [id, item] : items) {
            if (item.status == Status::COMPLETED ||
                item.status == Status::IN_PROGRESS ||
                item.status == Status::BLOCKED) {
                continue;
            }

            result.push_back({
                item,
                item.costOfDelay(),
                item.wsjf()
            });
        }

        sort(
            result.begin(),
            result.end(),
            [](const RankedItem& a, const RankedItem& b) {
                if (a.score != b.score) {
                    return a.score > b.score;
                }

                if (a.costOfDelay != b.costOfDelay) {
                    return a.costOfDelay > b.costOfDelay;
                }

                if (a.item.jobSize != b.item.jobSize) {
                    return a.item.jobSize < b.item.jobSize;
                }

                return a.item.id < b.item.id;
            }
        );

        return result;
    }

    Schedule buildSchedule(double capacity) const {
        validateNumber(capacity, "capacity");

        Schedule schedule;
        schedule.remainingCapacity = capacity;

        set<string> completed;

        for (const auto& [id, item] : items) {
            if (item.status == Status::COMPLETED) {
                completed.insert(id);
            }
        }

        vector<RankedItem> candidates = ranking();
        set<string> selectedIDs;

        bool progress = true;

        while (progress) {
            progress = false;

            for (const RankedItem& ranked : candidates) {
                const WorkItem& item = ranked.item;

                if (selectedIDs.count(item.id)) {
                    continue;
                }

                if (item.jobSize > schedule.remainingCapacity) {
                    continue;
                }

                bool dependenciesReady = all_of(
                    item.dependencies.begin(),
                    item.dependencies.end(),
                    [&](const string& dependency) {
                        return completed.count(dependency) > 0;
                    }
                );

                if (!dependenciesReady) {
                    continue;
                }

                schedule.selected.push_back(item);
                selectedIDs.insert(item.id);
                completed.insert(item.id);

                schedule.remainingCapacity -= item.jobSize;
                schedule.usedCapacity += item.jobSize;

                progress = true;
                break;
            }
        }

        return schedule;
    }

    double hypotheticalWSJF(
        const string& id,
        double businessChange,
        double timeChange,
        double riskChange,
        double sizeChange
    ) const {
        if (!items.count(id)) {
            throw invalid_argument("Unknown work item");
        }

        const WorkItem& item = items.at(id);

        double business = item.businessValue + businessChange;
        double time = item.timeCriticality + timeChange;
        double risk = item.riskReduction + riskChange;
        double size = item.jobSize + sizeChange;

        validateNumber(business, "scenario business value");
        validateNumber(time, "scenario time criticality");
        validateNumber(risk, "scenario risk reduction");
        validateNumber(size, "scenario job size", false);

        return (business + time + risk) / size;
    }

    void printReport() const {
        cout << "\nWSJF PRIORITIZATION REPORT\n";
        cout << string(95, '-') << "\n";

        cout << left
             << setw(13) << "ID"
             << setw(38) << "WORK ITEM"
             << right
             << setw(12) << "CoD"
             << setw(12) << "SIZE"
             << setw(12) << "WSJF"
             << "\n";

        cout << string(95, '-') << "\n";

        for (const RankedItem& ranked : ranking()) {
            cout << left
                 << setw(13) << ranked.item.id
                 << setw(38) << ranked.item.title
                 << right
                 << setw(12) << fixed << setprecision(2)
                 << ranked.costOfDelay
                 << setw(12) << ranked.item.jobSize
                 << setw(12) << ranked.score
                 << "\n";
        }
    }
};

int main() {
    try {
        WSJFEngine engine;

        engine.addWorkItem({
            "WSJF-201",
            "Security vulnerability remediation",
            9, 10, 10, 3
        });

        engine.addWorkItem({
            "WSJF-202",
            "Payment gateway modernization",
            9, 10, 8, 5
        });

        engine.addWorkItem({
            "WSJF-203",
            "Database migration foundation",
            7, 6, 9, 5
        });

        engine.addWorkItem({
            "WSJF-204",
            "Automated regression testing",
            6, 7, 8, 3,
            Status::READY,
            {"WSJF-203"}
        });

        engine.addWorkItem({
            "WSJF-205",
            "Customer analytics dashboard",
            8, 5, 3, 8
        });

        engine.addWorkItem({
            "WSJF-206",
            "Infrastructure monitoring",
            7, 8, 7, 4
        });

        engine.printReport();

        cout << "\nCAPACITY-CONSTRAINED SCHEDULE\n";

        Schedule schedule = engine.buildSchedule(12);

        for (size_t i = 0; i < schedule.selected.size(); ++i) {
            const WorkItem& item = schedule.selected[i];

            cout << i + 1 << ". "
                 << item.id << " - "
                 << item.title
                 << " | WSJF: "
                 << fixed << setprecision(3)
                 << item.wsjf()
                 << "\n";
        }

        cout << "Used capacity: "
             << schedule.usedCapacity << "\n";

        cout << "Remaining capacity: "
             << schedule.remainingCapacity << "\n";

        cout << "\nSCENARIO ANALYSIS\n";

        cout << "Current WSJF: "
             << engine.hypotheticalWSJF(
                 "WSJF-205", 0, 0, 0, 0
             )
             << "\n";

        cout << "Scenario WSJF: "
             << engine.hypotheticalWSJF(
                 "WSJF-205", 3, 2, 0, 0
             )
             << "\n";

        // A dependency must be completed before its dependent item
        // can transition into READY from another state.
        engine.changeStatus("WSJF-203", Status::IN_PROGRESS);
        engine.changeStatus("WSJF-203", Status::COMPLETED);

        cout << "\nDatabase migration completed.\n";

        // Input validation demonstration.
        try {
            engine.addWorkItem({
                "INVALID",
                "Invalid zero-size task",
                5, 5, 5, 0
            });
        } catch (const invalid_argument& error) {
            cout << "Expected validation failure: "
                 << error.what() << "\n";
        }

    } catch (const exception& error) {
        cerr << "WSJF engine failure: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
