#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class Status {
    Backlog,
    Ready,
    InProgress,
    Review,
    Done
};

string statusName(Status status) {
    switch (status) {
        case Status::Backlog: return "Backlog";
        case Status::Ready: return "Ready";
        case Status::InProgress: return "In Progress";
        case Status::Review: return "Review";
        case Status::Done: return "Done";
    }
    throw logic_error("Unknown work status.");
}

struct WorkItem {
    string id;
    string title;
    int businessValue;
    int effort;
    vector<string> acceptanceCriteria;
    vector<string> dependencies;
    Status status = Status::Backlog;
    int deliveredIteration = 0;
};

struct Release {
    int iteration;
    string goal;
    vector<string> deliveredItemIds;
    int deliveredValue = 0;
};

class DeliveryTeam {
private:
    map<string, WorkItem> backlog;
    vector<Release> releases;

    WorkItem& requireItem(const string& id) {
        auto it = backlog.find(id);
        if (it == backlog.end()) {
            throw invalid_argument("Unknown work item: " + id);
        }
        return it->second;
    }

    bool dependencySatisfied(
        const string& dependencyId,
        const set<string>& planned
    ) const {
        auto it = backlog.find(dependencyId);
        if (it == backlog.end()) {
            throw invalid_argument("Missing dependency: " + dependencyId);
        }

        // A dependency is valid when already delivered or included in the
        // same iteration plan. This does not by itself enforce execution order.
        return it->second.status == Status::Done ||
               planned.count(dependencyId) > 0;
    }

public:
    void addItem(WorkItem item) {
        if (item.id.empty() || item.title.empty()) {
            throw invalid_argument("Work item ID and title are required.");
        }
        if (item.businessValue <= 0 || item.effort <= 0) {
            throw invalid_argument("Value and effort must be positive.");
        }
        if (item.acceptanceCriteria.empty()) {
            throw invalid_argument("Acceptance criteria cannot be empty.");
        }
        if (backlog.count(item.id)) {
            throw invalid_argument("Duplicate work item ID: " + item.id);
        }

        backlog.emplace(item.id, move(item));
    }

    vector<WorkItem> prioritizeBacklog() const {
        vector<WorkItem> items;
        for (const auto& [id, item] : backlog) {
            if (item.status != Status::Done) {
                items.push_back(item);
            }
        }

        // This is a transparent heuristic. It ignores risk and dependencies,
        // which must also be considered during actual refinement.
        sort(items.begin(), items.end(), [](const WorkItem& a, const WorkItem& b) {
            const long long left =
                1LL * a.businessValue * b.effort;
            const long long right =
                1LL * b.businessValue * a.effort;
            if (left != right) return left > right;
            return a.id < b.id;
        });
        return items;
    }

    vector<string> planIteration(
        int iterationNumber,
        int capacity,
        const vector<string>& requestedIds,
        const string& goal
    ) {
        if (iterationNumber < 1 || capacity < 1 || goal.empty()) {
            throw invalid_argument("Invalid iteration configuration.");
        }
        if (requestedIds.empty()) {
            throw invalid_argument("An iteration requires planned work.");
        }

        set<string> planned;
        int totalEffort = 0;

        for (const string& id : requestedIds) {
            if (!planned.insert(id).second) {
                throw invalid_argument("Duplicate item in iteration plan.");
            }

            const WorkItem& item = requireItem(id);
            if (item.status != Status::Backlog &&
                item.status != Status::Ready) {
                throw invalid_argument("Item is not available: " + id);
            }

            totalEffort += item.effort;
        }

        if (totalEffort > capacity) {
            throw invalid_argument("Iteration commitment exceeds capacity.");
        }

        for (const string& id : requestedIds) {
            const WorkItem& item = requireItem(id);
            for (const string& dependency : item.dependencies) {
                if (!dependencySatisfied(dependency, planned)) {
                    throw invalid_argument(
                        "Unsatisfied dependency for " + id + ": " + dependency
                    );
                }
            }
        }

        // Validate the complete plan before changing any item. This avoids
        // partially applied plans when a late validation fails.
        for (const string& id : requestedIds) {
            backlog.at(id).status = Status::Ready;
        }

        cout << "\nIteration " << iterationNumber
             << " goal: " << goal << "\n";
        cout << "Committed effort: " << totalEffort
             << " / " << capacity << "\n";

        return requestedIds;
    }

    void transition(const string& id, Status next) {
        WorkItem& item = requireItem(id);
        bool allowed = false;

        switch (item.status) {
            case Status::Backlog:
                allowed = next == Status::Ready;
                break;
            case Status::Ready:
                allowed = next == Status::InProgress;
                break;
            case Status::InProgress:
                allowed = next == Status::Review;
                break;
            case Status::Review:
                allowed = next == Status::InProgress ||
                          next == Status::Done;
                break;
            case Status::Done:
                allowed = false;
                break;
        }

        if (!allowed) {
            throw logic_error(
                "Invalid transition for " + id + ": " +
                statusName(item.status) + " -> " + statusName(next)
            );
        }

        item.status = next;
        cout << id << " -> " << statusName(next) << "\n";
    }

    Release publishIncrement(int iterationNumber, const string& goal) {
        Release release{iterationNumber, goal, {}, 0};

        for (const auto& [id, item] : backlog) {
            if (item.status == Status::Done &&
                item.deliveredIteration == iterationNumber) {
                release.deliveredItemIds.push_back(id);
                release.deliveredValue += item.businessValue;
            }
        }

        releases.push_back(release);
        cout << "\nPublished increment " << iterationNumber << "\n";
        cout << "Delivered stories: " << release.deliveredItemIds.size()
             << "\nDelivered business value: " << release.deliveredValue
             << "\n";

        return release;
    }

    void markDelivered(const string& id, int iterationNumber) {
        WorkItem& item = requireItem(id);
        if (item.status != Status::Done) {
            throw logic_error("Only accepted work can be delivered.");
        }
        if (iterationNumber < 1) {
            throw invalid_argument("Invalid delivery iteration.");
        }
        item.deliveredIteration = iterationNumber;
    }

    void printBacklog() const {
        cout << "\nPrioritized backlog\n";
        for (const WorkItem& item : prioritizeBacklog()) {
            cout << item.id << " | " << item.title
                 << " | value=" << item.businessValue
                 << " | effort=" << item.effort
                 << " | " << statusName(item.status) << "\n";
        }
    }
};

int main() {
    try {
        DeliveryTeam team;

        team.addItem({
            "OPS-301",
            "View incident queue",
            10,
            3,
            {"Authorized staff can view incidents", "Status is visible"},
            {}
        });

        team.addItem({
            "OPS-302",
            "Record incident details",
            9,
            5,
            {"Staff can record a description", "Required fields are validated"},
            {}
        });

        team.addItem({
            "OPS-303",
            "Filter incident queue",
            7,
            2,
            {"Staff can filter incidents by status"},
            {"OPS-301"}
        });

        team.addItem({
            "OPS-304",
            "Export incident history",
            5,
            5,
            {"Export respects user permissions"},
            {"OPS-301"}
        });

        team.printBacklog();

        // This release delivers queue visibility and status filtering.
        // The dependent filter can be planned with its prerequisite.
        const auto iterationOne = team.planIteration(
            1,
            6,
            {"OPS-301", "OPS-303"},
            "Provide visibility into active incidents"
        );

        for (const string& id : iterationOne) {
            team.transition(id, Status::InProgress);
            team.transition(id, Status::Review);
            team.transition(id, Status::Done);
            team.markDelivered(id, 1);
        }

        team.publishIncrement(
            1,
            "Provide visibility into active incidents"
        );

        cout << "\nStakeholder feedback: Incident managers need editable "
                "incident details.\n";

        // Feedback is represented as a refined backlog item. It can be
        // prioritized for a later iteration without changing the released
        // increment.
        team.addItem({
            "OPS-305",
            "Edit incident details",
            8,
            3,
            {"Changes are validated", "Edits record the acting user"},
            {"OPS-302"}
        });

        team.printBacklog();

        // An invalid workflow operation is caught without terminating the
        // demonstration.
        try {
            team.transition("OPS-305", Status::Done);
        } catch (const exception& error) {
            cout << "\nExpected validation error: " << error.what() << "\n";
        }

    } catch (const exception& error) {
        cerr << "Delivery planning failed: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
