#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Case study: Scrum delivery for an online banking platform.
 *
 * The model represents backlog prioritization, sprint capacity, state
 * transitions, Increment inspection, and retrospective improvement.
 * It is a teaching simulation rather than a complete Scrum implementation.
 */

enum class WorkState {
    Todo,
    InProgress,
    Done
};

string stateName(WorkState state) {
    switch (state) {
        case WorkState::Todo: return "To Do";
        case WorkState::InProgress: return "In Progress";
        case WorkState::Done: return "Done";
    }
    throw logic_error("Unknown work state.");
}

struct BacklogItem {
    string id;
    string title;
    int priority;
    int estimate;
    vector<string> acceptanceCriteria;
    WorkState state = WorkState::Todo;
    bool accepted = false;
};

struct SprintGoal {
    string statement;
};

struct Sprint {
    int number;
    int durationDays;
    int capacity;
    SprintGoal goal;
    vector<BacklogItem*> selected;
    vector<string> impediments;
    bool reviewCompleted = false;
    bool retrospectiveCompleted = false;
    bool closed = false;

    int plannedPoints() const {
        int total = 0;
        for (const auto* item : selected) total += item->estimate;
        return total;
    }

    int acceptedPoints() const {
        int total = 0;
        for (const auto* item : selected) {
            if (item->accepted) total += item->estimate;
        }
        return total;
    }
};

class BankingScrumBoard {
private:
    string productName;
    string productOwner;
    string scrumMaster;
    vector<string> developers;
    vector<BacklogItem> productBacklog;
    vector<BacklogItem*> increment;
    vector<string> eventLog;
    vector<string> improvementActions;
    Sprint* activeSprint = nullptr;

    void requireActiveSprint() const {
        if (activeSprint == nullptr || activeSprint->closed) {
            throw logic_error("There is no active sprint.");
        }
    }

    BacklogItem& findSelectedItem(const string& id) {
        requireActiveSprint();
        for (BacklogItem* item : activeSprint->selected) {
            if (item->id == id) return *item;
        }
        throw out_of_range("Item is not part of the Sprint Backlog: " + id);
    }

    void record(const string& message) {
        eventLog.push_back(message);
        cout << "[Scrum event] " << message << '\n';
    }

public:
    BankingScrumBoard(
        string product,
        string owner,
        string master,
        vector<string> team,
        vector<BacklogItem> items
    ) : productName(move(product)),
        productOwner(move(owner)),
        scrumMaster(move(master)),
        developers(move(team)),
        productBacklog(move(items)) {

        if (productName.empty() || productOwner.empty() || scrumMaster.empty()) {
            throw invalid_argument("Product and accountability names are required.");
        }
        if (developers.empty()) {
            throw invalid_argument("At least one Developer is required.");
        }

        set<string> memberNames{productOwner, scrumMaster};
        for (const string& developer : developers) {
            if (developer.empty() || !memberNames.insert(developer).second) {
                throw invalid_argument("Team member names must be unique and non-empty.");
            }
        }

        set<string> itemIds;
        for (const auto& item : productBacklog) {
            if (item.id.empty() || item.title.empty() ||
                item.priority < 1 || item.estimate < 0 ||
                item.acceptanceCriteria.empty()) {
                throw invalid_argument("Invalid Product Backlog Item.");
            }
            if (!itemIds.insert(item.id).second) {
                throw invalid_argument("Duplicate backlog item ID: " + item.id);
            }
        }
    }

    void refineBacklog() {
        // References are created only after the vector has been fully built.
        // Sorting the vector before selecting items avoids pointer invalidation.
        sort(productBacklog.begin(), productBacklog.end(),
             [](const BacklogItem& a, const BacklogItem& b) {
                 if (a.priority != b.priority) return a.priority < b.priority;
                 return a.id < b.id;
             });

        cout << "\nPrioritized Product Backlog\n";
        for (const auto& item : productBacklog) {
            cout << item.id << " | " << item.title
                 << " | priority=" << item.priority
                 << " | estimate=" << item.estimate << '\n';
        }
    }

    Sprint& planSprint(int number, int durationDays, int capacity, string goal) {
        if (activeSprint != nullptr && !activeSprint->closed) {
            throw logic_error("The existing sprint must be closed first.");
        }
        if (number < 1 || durationDays < 1 || durationDays > 30 || capacity < 0) {
            throw invalid_argument("Invalid sprint number, duration, or capacity.");
        }
        if (goal.empty()) {
            throw invalid_argument("The Sprint Goal must not be empty.");
        }

        // Sprint is allocated on the heap so its selected item references remain
        // stable until the board and sprint have finished their lifecycle.
        activeSprint = new Sprint{
            number, durationDays, capacity, SprintGoal{move(goal)}
        };

        int remaining = capacity;
        for (auto& item : productBacklog) {
            if (item.state != WorkState::Todo) continue;
            if (item.estimate <= remaining) {
                activeSprint->selected.push_back(&item);
                remaining -= item.estimate;
            }
        }

        record("Sprint " + to_string(number) + " planned: " +
               activeSprint->goal.statement);
        cout << "Capacity=" << capacity
             << ", selected=" << activeSprint->plannedPoints()
             << ", remaining=" << remaining << " points\n";

        return *activeSprint;
    }

    void changeState(const string& id, WorkState next) {
        BacklogItem& item = findSelectedItem(id);
        bool allowed = false;

        if (item.state == WorkState::Todo && next == WorkState::InProgress) {
            allowed = true;
        } else if (item.state == WorkState::InProgress &&
                   (next == WorkState::Done || next == WorkState::Todo)) {
            allowed = true;
        }

        if (!allowed) {
            throw logic_error("Invalid state transition for " + id + ": " +
                              stateName(item.state) + " -> " + stateName(next));
        }

        item.state = next;
        record(id + " changed to " + stateName(next));
    }

    void dailyScrum(const vector<string>& newImpediments) {
        requireActiveSprint();

        for (const string& impediment : newImpediments) {
            if (!impediment.empty() &&
                find(activeSprint->impediments.begin(),
                     activeSprint->impediments.end(), impediment) ==
                    activeSprint->impediments.end()) {
                activeSprint->impediments.push_back(impediment);
            }
        }

        int done = 0;
        for (const auto* item : activeSprint->selected) {
            if (item->state == WorkState::Done) ++done;
        }

        record("Daily Scrum: " + to_string(done) + "/" +
               to_string(activeSprint->selected.size()) +
               " selected items implemented.");

        for (const string& impediment : activeSprint->impediments) {
            cout << "Impediment: " << impediment << '\n';
        }
    }

    void sprintReview(const vector<string>& stakeholderFeedback) {
        requireActiveSprint();
        if (activeSprint->reviewCompleted) {
            throw logic_error("Sprint Review has already been completed.");
        }

        for (BacklogItem* item : activeSprint->selected) {
            if (item->state == WorkState::Done) {
                // A completed item enters the simulated Increment only when
                // its acceptance conditions have been confirmed.
                item->accepted = true;
                increment.push_back(item);
            } else {
                // Unfinished work returns to the Product Backlog, not the Increment.
                item->state = WorkState::Todo;
                item->accepted = false;
            }
        }

        activeSprint->reviewCompleted = true;
        record("Sprint Review inspected the Increment.");
        cout << "Accepted points: " << activeSprint->acceptedPoints() << '\n';

        for (const string& feedback : stakeholderFeedback) {
            cout << "Stakeholder feedback: " << feedback << '\n';
        }
    }

    void retrospective(const vector<string>& actions) {
        requireActiveSprint();
        if (!activeSprint->reviewCompleted) {
            throw logic_error("Review must be completed before the retrospective.");
        }
        if (activeSprint->retrospectiveCompleted) {
            throw logic_error("Retrospective already completed.");
        }

        for (const string& action : actions) {
            if (!action.empty()) improvementActions.push_back(action);
        }
        activeSprint->retrospectiveCompleted = true;
        record("Retrospective recorded improvement actions.");

        for (const string& action : actions) {
            if (!action.empty()) cout << "Improvement: " << action << '\n';
        }
    }

    void closeSprint() {
        requireActiveSprint();
        if (!activeSprint->reviewCompleted ||
            !activeSprint->retrospectiveCompleted) {
            throw logic_error("Review and retrospective are required for closure.");
        }
        activeSprint->closed = true;
        record("Sprint closed.");
    }

    void report() const {
        cout << "\nDelivery Report\n"
             << "Product: " << productName << '\n'
             << "Product Owner: " << productOwner << '\n'
             << "Scrum Master: " << scrumMaster << '\n'
             << "Developers: " << developers.size() << '\n'
             << "Product Backlog Items: " << productBacklog.size() << '\n'
             << "Increment Items: " << increment.size() << '\n'
             << "Events Recorded: " << eventLog.size() << '\n'
             << "Improvement Actions: " << improvementActions.size() << '\n';
    }

    ~BankingScrumBoard() {
        delete activeSprint;
    }

    BankingScrumBoard(const BankingScrumBoard&) = delete;
    BankingScrumBoard& operator=(const BankingScrumBoard&) = delete;
};

int main() {
    try {
        vector<BacklogItem> items{
            {"BANK-301", "Validate transfer requests", 1, 5,
             {"Reject invalid beneficiary", "Validate transfer amount"}},
            {"BANK-302", "Record transfer audit trail", 2, 8,
             {"Record transfer outcome", "Include correlation ID"}},
            {"BANK-303", "Display transfer status", 3, 3,
             {"Authorized customers can view status"}},
            {"BANK-304", "Expose retry diagnostics", 4, 5,
             {"Operators can inspect failed retries"}}
        };

        BankingScrumBoard board(
            "Digital Banking Reliability",
            "Maya",
            "Arjun",
            {"Neha", "Kabir", "Sara"},
            move(items)
        );

        board.refineBacklog();

        Sprint& sprint = board.planSprint(
            1, 10, 16,
            "Make transfers safer through validation and traceability."
        );

        if (!sprint.selected.empty()) {
            const string firstId = sprint.selected.front()->id;
            board.changeState(firstId, WorkState::InProgress);
            board.changeState(firstId, WorkState::Done);
        }

        board.dailyScrum({
            "Payment integration test data is incomplete."
        });

        board.sprintReview({
            "Validate rejection behavior with representative failure cases."
        });

        board.retrospective({
            "Prepare integration test fixtures before development.",
            "Clarify audit requirements during backlog refinement."
        });

        board.closeSprint();
        board.report();

        try {
            board.changeState("UNKNOWN", WorkState::InProgress);
        } catch (const exception& error) {
            cout << "Expected validation failure: " << error.what() << '\n';
        }
    } catch (const exception& error) {
        cerr << "Scrum simulation failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
