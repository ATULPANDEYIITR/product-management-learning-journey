#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Repository-independent enterprise case study:
 * A retail platform team evaluates user stories before sprint commitment.
 *
 * The governance engine checks story semantics, measurable acceptance
 * criteria, INVEST attributes, dependencies, and sprint readiness.
 * It distinguishes product backlog quality from implementation completion.
 */

enum class StoryState {
    Draft,
    Refinement,
    Ready,
    InProgress,
    Done,
    Blocked
};

enum class CriterionKind {
    Functional,
    Validation,
    Security,
    Performance,
    Accessibility
};

struct Persona {
    string name;
    string role;
    string context;
    string goal;
};

struct AcceptanceCriterion {
    string given;
    string when;
    string then;
    CriterionKind kind;

    bool valid() const {
        return !given.empty() &&
               !when.empty() &&
               !then.empty() &&
               given.size() >= 8 &&
               when.size() >= 8 &&
               then.size() >= 8;
    }
};

struct InvestAssessment {
    bool independent = true;
    bool negotiable = true;
    bool valuable = true;
    bool estimable = true;
    bool small = true;
    bool testable = true;

    bool passes() const {
        return independent && negotiable && valuable &&
               estimable && small && testable;
    }

    vector<string> failures() const {
        vector<string> result;
        if (!independent) result.push_back("Independent");
        if (!negotiable) result.push_back("Negotiable");
        if (!valuable) result.push_back("Valuable");
        if (!estimable) result.push_back("Estimable");
        if (!small) result.push_back("Small");
        if (!testable) result.push_back("Testable");
        return result;
    }
};

struct UserStory {
    string id;
    string title;
    Persona persona;
    string need;
    string value;
    vector<AcceptanceCriterion> criteria;
    InvestAssessment invest;
    int priority = 3;
    int points = 0;
    set<string> dependencies;
    StoryState state = StoryState::Draft;

    string statement() const {
        return "As a " + persona.role +
               ", I want " + need +
               ", so that " + value + ".";
    }

    vector<string> validate() const {
        vector<string> errors;

        if (id.empty() || id.find('-') == string::npos) {
            errors.push_back("Story ID must contain a project prefix and number.");
        }

        if (title.empty()) errors.push_back("Story title is missing.");
        if (persona.name.empty()) errors.push_back("Persona name is missing.");
        if (persona.role.empty()) errors.push_back("Persona role is missing.");
        if (persona.context.empty()) errors.push_back("Persona context is missing.");
        if (persona.goal.empty()) errors.push_back("Persona goal is missing.");
        if (need.empty()) errors.push_back("User need is missing.");
        if (value.empty()) errors.push_back("User value is missing.");
        if (criteria.empty()) errors.push_back("Acceptance criteria are missing.");
        if (points < 0) errors.push_back("Story points cannot be negative.");
        if (priority < 1 || priority > 5) {
            errors.push_back("Priority must be between 1 and 5.");
        }

        for (size_t i = 0; i < criteria.size(); ++i) {
            if (!criteria[i].valid()) {
                errors.push_back(
                    "Acceptance criterion " + to_string(i + 1) +
                    " is incomplete or insufficiently specific."
                );
            }
        }

        if (dependencies.count(id)) {
            errors.push_back("A story cannot depend on itself.");
        }

        return errors;
    }
};

string stateName(StoryState state) {
    switch (state) {
        case StoryState::Draft: return "Draft";
        case StoryState::Refinement: return "Refinement";
        case StoryState::Ready: return "Ready";
        case StoryState::InProgress: return "In progress";
        case StoryState::Done: return "Done";
        case StoryState::Blocked: return "Blocked";
    }
    throw logic_error("Unknown story state.");
}

class StoryGovernanceEngine {
private:
    map<string, UserStory> stories;

    static bool allowedTransition(StoryState from, StoryState to) {
        switch (from) {
            case StoryState::Draft:
                return to == StoryState::Refinement ||
                       to == StoryState::Blocked;
            case StoryState::Refinement:
                return to == StoryState::Draft ||
                       to == StoryState::Ready ||
                       to == StoryState::Blocked;
            case StoryState::Ready:
                return to == StoryState::InProgress ||
                       to == StoryState::Refinement ||
                       to == StoryState::Blocked;
            case StoryState::InProgress:
                return to == StoryState::Done ||
                       to == StoryState::Blocked ||
                       to == StoryState::Refinement;
            case StoryState::Blocked:
                return to == StoryState::Refinement ||
                       to == StoryState::Ready;
            case StoryState::Done:
                return false;
        }
        return false;
    }

    bool visit(
        const string& id,
        set<string>& visiting,
        set<string>& visited,
        vector<string>& order
    ) const {
        if (visiting.count(id)) return false;
        if (visited.count(id)) return true;

        auto it = stories.find(id);
        if (it == stories.end()) return false;

        visiting.insert(id);

        for (const string& dependency : it->second.dependencies) {
            if (!stories.count(dependency)) return false;
            if (!visit(dependency, visiting, visited, order)) return false;
        }

        visiting.erase(id);
        visited.insert(id);
        order.push_back(id);
        return true;
    }

public:
    void addStory(const UserStory& story) {
        if (stories.count(story.id)) {
            throw invalid_argument("Duplicate story ID: " + story.id);
        }

        vector<string> errors = story.validate();
        if (!errors.empty()) {
            throw invalid_argument(
                "Cannot add invalid story " + story.id + ": " + errors.front()
            );
        }

        stories.emplace(story.id, story);
    }

    void transition(const string& id, StoryState next) {
        auto it = stories.find(id);
        if (it == stories.end()) {
            throw invalid_argument("Unknown story: " + id);
        }

        UserStory& story = it->second;

        if (!allowedTransition(story.state, next)) {
            throw logic_error(
                "Invalid transition: " + stateName(story.state) +
                " -> " + stateName(next)
            );
        }

        if (next == StoryState::Ready && !story.invest.passes()) {
            throw logic_error("Story fails INVEST assessment.");
        }

        if (next == StoryState::Ready) {
            for (const string& dependency : story.dependencies) {
                auto dep = stories.find(dependency);
                if (dep == stories.end() ||
                    dep->second.state != StoryState::Done) {
                    throw logic_error(
                        "Dependency " + dependency + " is not complete."
                    );
                }
            }
        }

        story.state = next;
    }

    vector<string> dependencyOrder() const {
        set<string> visiting;
        set<string> visited;
        vector<string> order;

        for (const auto& entry : stories) {
            if (!visit(entry.first, visiting, visited, order)) {
                throw logic_error(
                    "Missing dependency or cycle involving " + entry.first
                );
            }
        }

        return order;
    }

    bool sprintEligible(const string& id) const {
        auto it = stories.find(id);
        if (it == stories.end()) return false;

        const UserStory& story = it->second;
        if (story.state != StoryState::Ready ||
            !story.invest.passes() ||
            !story.validate().empty()) {
            return false;
        }

        for (const string& dependency : story.dependencies) {
            auto dep = stories.find(dependency);
            if (dep == stories.end() ||
                dep->second.state != StoryState::Done) {
                return false;
            }
        }

        return true;
    }

    void printBacklog() const {
        vector<const UserStory*> ordered;
        for (const auto& entry : stories) {
            ordered.push_back(&entry.second);
        }

        sort(ordered.begin(), ordered.end(),
            [](const UserStory* a, const UserStory* b) {
                if (a->priority != b->priority) {
                    return a->priority < b->priority;
                }
                if (a->points != b->points) {
                    return a->points < b->points;
                }
                return a->id < b->id;
            });

        for (const UserStory* story : ordered) {
            cout << "\n" << story->id << " - " << story->title << "\n";
            cout << story->statement() << "\n";
            cout << "State: " << stateName(story->state) << "\n";
            cout << "Sprint eligible: "
                 << (sprintEligible(story->id) ? "yes" : "no") << "\n";

            for (const string& failure : story->invest.failures()) {
                cout << "INVEST concern: " << failure << "\n";
            }
        }
    }
};

int main() {
    try {
        Persona customer{
            "Ananya",
            "registered customer",
            "mobile retail checkout",
            "place an order without duplicate submissions"
        };

        Persona support{
            "Rohan",
            "support specialist",
            "customer order investigation",
            "identify a failed checkout safely"
        };

        UserStory address{
            "SHOP-100",
            "Save a validated delivery address",
            customer,
            "save a complete delivery address",
            "my order reaches the correct destination",
            {
                {
                    "I am editing a delivery address",
                    "I submit all required valid fields",
                    "the address is saved and selectable at checkout",
                    CriterionKind::Validation
                }
            },
            {},
            1,
            3,
            {},
            StoryState::Draft
        };

        UserStory checkout{
            "SHOP-101",
            "Confirm a retail order",
            customer,
            "confirm my cart after reviewing the final price",
            "I know the amount before placing the order",
            {
                {
                    "my cart and delivery address are valid",
                    "I confirm the checkout request",
                    "one order is created and a receipt is displayed",
                    CriterionKind::Functional
                },
                {
                    "the first request succeeded but its response was lost",
                    "I retry using the same idempotency key",
                    "the original order is returned without duplication",
                    CriterionKind::Security
                }
            },
            {},
            1,
            5,
            {"SHOP-100"},
            StoryState::Draft
        };

        UserStory diagnostics{
            "SHOP-102",
            "Inspect a failed checkout",
            support,
            "view a failure category using an attempt reference",
            "I can resolve problems without exposing payment secrets",
            {
                {
                    "a checkout attempt has failed",
                    "an authorized agent opens its diagnostic record",
                    "the failure category is displayed and access is audited",
                    CriterionKind::Security
                }
            },
            {},
            2,
            3,
            {},
            StoryState::Draft
        };

        // This intentionally oversized story fails the Small INVEST criterion.
        diagnostics.invest.small = false;

        StoryGovernanceEngine engine;
        engine.addStory(address);
        engine.addStory(checkout);
        engine.addStory(diagnostics);

        cout << "Dependency order:\n";
        for (const string& id : engine.dependencyOrder()) {
            cout << "  " << id << "\n";
        }

        engine.transition("SHOP-100", StoryState::Refinement);
        engine.transition("SHOP-100", StoryState::Ready);
        engine.transition("SHOP-100", StoryState::InProgress);
        engine.transition("SHOP-100", StoryState::Done);

        engine.transition("SHOP-101", StoryState::Refinement);
        engine.transition("SHOP-101", StoryState::Ready);

        // A failed INVEST assessment prevents the diagnostic story becoming ready.
        engine.transition("SHOP-102", StoryState::Refinement);
        try {
            engine.transition("SHOP-102", StoryState::Ready);
        } catch (const logic_error& error) {
            cout << "\nExpected readiness rejection: "
                 << error.what() << "\n";
        }

        engine.printBacklog();

        // Cycles are rejected rather than producing a misleading execution order.
        cout << "\nA dependency cycle or missing dependency causes validation failure.\n";
    } catch (const exception& error) {
        cerr << "Governance error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
