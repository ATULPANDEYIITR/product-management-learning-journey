#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <iomanip>

using namespace std;

enum class Priority {
    MUST_HAVE,
    SHOULD_HAVE,
    COULD_HAVE,
    WONT_HAVE
};

enum class Status {
    PROPOSED,
    APPROVED,
    IN_PROGRESS,
    COMPLETED,
    DEFERRED
};

string priorityName(Priority priority) {
    switch (priority) {
        case Priority::MUST_HAVE: return "Must-have";
        case Priority::SHOULD_HAVE: return "Should-have";
        case Priority::COULD_HAVE: return "Could-have";
        case Priority::WONT_HAVE: return "Won't-have";
    }
    throw invalid_argument("Unknown priority.");
}

string statusName(Status status) {
    switch (status) {
        case Status::PROPOSED: return "Proposed";
        case Status::APPROVED: return "Approved";
        case Status::IN_PROGRESS: return "In progress";
        case Status::COMPLETED: return "Completed";
        case Status::DEFERRED: return "Deferred";
    }
    throw invalid_argument("Unknown status.");
}

struct Requirement {
    string id;
    string title;
    string description;
    Priority priority;
    int businessValue;
    int effort;
    string owner;
    vector<string> dependencies;
    Status status = Status::PROPOSED;

    double valueEffortRatio() const {
        return static_cast<double>(businessValue) / effort;
    }
};

struct ReviewDecision {
    string requirementId;
    Priority oldPriority;
    Priority newPriority;
    string actor;
    string reason;
};

struct ReleaseResult {
    vector<Requirement> selected;
    int remainingCapacity;
    bool mandatoryShortfall;
};

class PrioritizationEngine {
private:
    map<string, Requirement> requirements;
    vector<ReviewDecision> history;

    void validateGraph() const {
        set<string> visited;
        set<string> active;

        for (const auto& entry : requirements) {
            for (const string& dependency :
                 entry.second.dependencies) {
                if (requirements.find(dependency) == requirements.end()) {
                    throw invalid_argument(
                        "Unknown dependency: " + dependency
                    );
                }
            }
        }

        function<void(const string&)> visit =
            [&](const string& id) {
                if (active.count(id)) {
                    throw invalid_argument(
                        "Circular dependency detected."
                    );
                }

                if (visited.count(id)) return;

                active.insert(id);

                for (const string& dependency :
                     requirements.at(id).dependencies) {
                    visit(dependency);
                }

                active.erase(id);
                visited.insert(id);
            };

        for (const auto& entry : requirements) {
            visit(entry.first);
        }
    }

public:
    void addRequirement(const Requirement& requirement) {
        if (requirement.id.empty() ||
            requirement.title.empty() ||
            requirement.owner.empty()) {
            throw invalid_argument(
                "ID, title and owner are required."
            );
        }

        if (requirement.businessValue < 1 ||
            requirement.businessValue > 10) {
            throw invalid_argument(
                "Business value must be between 1 and 10."
            );
        }

        if (requirement.effort < 1 ||
            requirement.effort > 100) {
            throw invalid_argument(
                "Effort must be between 1 and 100."
            );
        }

        if (requirements.count(requirement.id)) {
            throw invalid_argument("Duplicate requirement ID.");
        }

        if (find(
            requirement.dependencies.begin(),
            requirement.dependencies.end(),
            requirement.id
        ) != requirement.dependencies.end()) {
            throw invalid_argument("Self-dependency is prohibited.");
        }

        requirements.emplace(requirement.id, requirement);

        try {
            validateGraph();
        } catch (...) {
            requirements.erase(requirement.id);
            throw;
        }
    }

    const Requirement& getRequirement(const string& id) const {
        auto it = requirements.find(id);

        if (it == requirements.end()) {
            throw out_of_range("Requirement not found: " + id);
        }

        return it->second;
    }

    void updatePriority(
        const string& id,
        Priority newPriority,
        const string& actor,
        const string& reason
    ) {
        auto it = requirements.find(id);

        if (it == requirements.end()) {
            throw out_of_range("Requirement not found.");
        }

        if (actor.empty() || reason.empty()) {
            throw invalid_argument(
                "Actor and reason are required."
            );
        }

        Priority oldPriority = it->second.priority;

        if (oldPriority == newPriority) return;

        it->second.priority = newPriority;

        history.push_back({
            id,
            oldPriority,
            newPriority,
            actor,
            reason
        });
    }

    void updateStatus(const string& id, Status newStatus) {
        auto it = requirements.find(id);

        if (it == requirements.end()) {
            throw out_of_range("Requirement not found.");
        }

        if (it->second.priority == Priority::WONT_HAVE &&
            (newStatus == Status::IN_PROGRESS ||
             newStatus == Status::COMPLETED)) {
            throw invalid_argument(
                "Won't-have requirements cannot enter delivery."
            );
        }

        it->second.status = newStatus;
    }

    bool dependenciesReady(const string& id) const {
        const Requirement& requirement = getRequirement(id);

        for (const string& dependency :
             requirement.dependencies) {
            if (getRequirement(dependency).status != Status::COMPLETED) {
                return false;
            }
        }

        return true;
    }

    ReleaseResult evaluateRelease(int capacity) const {
        if (capacity < 0) {
            throw invalid_argument("Capacity cannot be negative.");
        }

        vector<Requirement> mandatory;
        vector<Requirement> optional;

        int mandatoryEffort = 0;

        for (const auto& entry : requirements) {
            const Requirement& r = entry.second;

            if (r.status == Status::COMPLETED ||
                r.priority == Priority::WONT_HAVE) {
                continue;
            }

            if (r.priority == Priority::MUST_HAVE) {
                mandatory.push_back(r);
                mandatoryEffort += r.effort;
            } else {
                optional.push_back(r);
            }
        }

        sort(mandatory.begin(), mandatory.end(),
            [](const Requirement& a, const Requirement& b) {
                return a.id < b.id;
            }
        );

        sort(optional.begin(), optional.end(),
            [](const Requirement& a, const Requirement& b) {
                if (a.valueEffortRatio() != b.valueEffortRatio()) {
                    return a.valueEffortRatio() >
                           b.valueEffortRatio();
                }
                return a.id < b.id;
            }
        );

        vector<Requirement> selected;
        set<string> selectedIds;
        int remaining = capacity;

        vector<Requirement> candidates = mandatory;

        candidates.insert(
            candidates.end(),
            optional.begin(),
            optional.end()
        );

        for (const Requirement& r : candidates) {
            bool ready = true;

            for (const string& dependency : r.dependencies) {
                if (selectedIds.count(dependency)) continue;

                if (getRequirement(dependency).status !=
                    Status::COMPLETED) {
                    ready = false;
                    break;
                }
            }

            if (ready && r.effort <= remaining) {
                selected.push_back(r);
                selectedIds.insert(r.id);
                remaining -= r.effort;
            }
        }

        return {
            selected,
            remaining,
            mandatoryEffort > capacity
        };
    }

    void printReport() const {
        map<Priority, vector<Requirement>> groups;

        for (const auto& entry : requirements) {
            groups[entry.second.priority].push_back(entry.second);
        }

        cout << "\nMOSCOW PRIORITIZATION REPORT\n";
        cout << string(65, '=') << '\n';

        for (Priority p : {
            Priority::MUST_HAVE,
            Priority::SHOULD_HAVE,
            Priority::COULD_HAVE,
            Priority::WONT_HAVE
        }) {
            const auto& items = groups[p];

            int effort = 0;
            int value = 0;

            for (const auto& r : items) {
                effort += r.effort;
                value += r.businessValue;
            }

            cout << "\n" << priorityName(p)
                 << "\nCount: " << items.size()
                 << "\nEffort: " << effort
                 << "\nBusiness value: " << value
                 << "\n";
        }

        cout << "\nTotal requirements: "
             << requirements.size() << '\n';

        cout << "Priority changes: "
             << history.size() << '\n';
    }

    size_t size() const {
        return requirements.size();
    }
};

Requirement makeRequirement(
    string id,
    string title,
    Priority priority,
    int value,
    int effort,
    string owner,
    vector<string> dependencies = {}
) {
    return {
        id,
        title,
        "Requirement for the current product release.",
        priority,
        value,
        effort,
        owner,
        dependencies,
        Status::PROPOSED
    };
}

void runTests() {
    PrioritizationEngine engine;

    engine.addRequirement(makeRequirement(
        "T001", "Authentication",
        Priority.MUST_HAVE, 10, 8, "Security"
    ));

    engine.addRequirement(makeRequirement(
        "T002", "Payments",
        Priority.MUST_HAVE, 10, 13, "Payments",
        {"T001"}
    ));

    if (engine.size() != 2) {
        throw runtime_error("Registration test failed.");
    }

    if (engine.dependenciesReady("T002")) {
        throw runtime_error("Dependency test failed.");
    }

    engine.updateStatus("T001", Status::COMPLETED);

    if (!engine.dependenciesReady("T002")) {
        throw runtime_error("Completion test failed.");
    }

    bool rejected = false;

    try {
        engine.addRequirement(makeRequirement(
            "T003", "Invalid cycle",
            Priority.COULD_HAVE, 5, 3, "Engineering",
            {"T003"}
        ));
    } catch (const invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Cycle validation failed.");
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        PrioritizationEngine engine;

        engine.addRequirement(makeRequirement(
            "R001", "User Authentication",
            Priority::MUST_HAVE, 10, 8, "Security Team"
        ));

        engine.addRequirement(makeRequirement(
            "R002", "Payment Processing",
            Priority::MUST_HAVE, 10, 13, "Payments Team",
            {"R001"}
        ));

        engine.addRequirement(makeRequirement(
            "R003", "Audit Logging",
            Priority::MUST_HAVE, 9, 5, "Platform Team"
        ));

        engine.addRequirement(makeRequirement(
            "R004", "Business Analytics",
            Priority::SHOULD_HAVE, 8, 8, "Analytics Team"
        ));

        engine.addRequirement(makeRequirement(
            "R005", "Email Notifications",
            Priority::SHOULD_HAVE, 7, 5, "Communications Team"
        ));

        engine.addRequirement(makeRequirement(
            "R006", "Custom Themes",
            Priority::COULD_HAVE, 4, 3, "Frontend Team"
        ));

        engine.addRequirement(makeRequirement(
            "R007", "Animated Backgrounds",
            Priority::WONT_HAVE, 2, 5, "Frontend Team"
        ));

        engine.printReport();

        const int capacity = 30;

        ReleaseResult release = engine.evaluateRelease(capacity);

        cout << "\nRELEASE PLAN\n";
        cout << string(65, '-') << '\n';

        for (const auto& r : release.selected) {
            cout << r.id << " | "
                 << r.title << " | "
                 << priorityName(r.priority) << " | Effort: "
                 << r.effort << '\n';
        }

        cout << "\nRemaining capacity: "
             << release.remainingCapacity << '\n';

        cout << "Mandatory shortfall: "
             << boolalpha << release.mandatoryShortfall << '\n';

        runTests();

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
