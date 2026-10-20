#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class Priority {
    Critical = 4,
    High = 3,
    Medium = 2,
    Low = 1
};

enum class ItemState {
    Discovery,
    Ready,
    InProgress,
    Done
};

enum class ReviewDecision {
    Comment,
    Accepted,
    Rejected
};

struct ProductGoal {
    string id;
    string statement;
    string metric;
    double target;
};

struct RoadmapOutcome {
    string id;
    string statement;
    string productGoalId;
    int targetSprint;
};

struct BacklogItem {
    string id;
    string title;
    string problem;
    int value;
    int effort;
    Priority priority;
    ItemState state;
    set<string> evidence;

    double score() const {
        if (effort <= 0) {
            throw invalid_argument("Backlog effort must be positive");
        }
        return static_cast<double>(value * static_cast<int>(priority)) / effort;
    }
};

struct StatusCheck {
    string name;
    bool passed;
    bool required;
};

struct DiscoveryFinding {
    string experimentId;
    string hypothesis;
    double observedRate;
    double threshold;

    bool supportsHypothesis() const {
        return observedRate >= threshold;
    }
};

struct Sprint {
    string id;
    int goalNumber;
    string goalStatement;
    int capacity;
    vector<string> selectedItems;
};

struct GovernancePolicy {
    int requiredItems;
    bool requireEvidence;
    bool requireDiscoveryValidation;
};

class ProductGovernanceEngine {
private:
    map<string, ProductGoal> goals;
    map<string, RoadmapOutcome> roadmap;
    map<string, BacklogItem> backlog;
    map<string, Sprint> sprints;
    vector<StatusCheck> checks;
    vector<DiscoveryFinding> findings;
    GovernancePolicy policy;

    static bool validText(const string& value) {
        return !value.empty();
    }

public:
    explicit ProductGovernanceEngine(GovernancePolicy p)
        : policy(p) {}

    void addGoal(const ProductGoal& goal) {
        if (!validText(goal.id) || !validText(goal.statement) ||
            !validText(goal.metric)) {
            throw invalid_argument("Invalid product goal");
        }

        if (goal.target < 0.0 || goal.target > 1.0) {
            throw invalid_argument("Product goal target must be between 0 and 1");
        }

        if (goals.contains(goal.id)) {
            throw invalid_argument("Duplicate product goal");
        }

        goals.emplace(goal.id, goal);
    }

    void addRoadmapOutcome(const RoadmapOutcome& outcome) {
        if (!goals.contains(outcome.productGoalId)) {
            throw invalid_argument("Roadmap outcome references unknown goal");
        }

        if (outcome.targetSprint < 1) {
            throw invalid_argument("Roadmap target sprint must be positive");
        }

        roadmap.emplace(outcome.id, outcome);
    }

    void addBacklogItem(const BacklogItem& item) {
        if (!validText(item.id) || !validText(item.title) ||
            !validText(item.problem)) {
            throw invalid_argument("Backlog item requires descriptive fields");
        }

        if (item.value < 1 || item.value > 100 ||
            item.effort < 1 || item.effort > 100) {
            throw invalid_argument("Backlog value and effort must be 1..100");
        }

        if (policy.requireEvidence && item.evidence.empty()) {
            throw invalid_argument("Backlog item requires discovery evidence");
        }

        if (backlog.contains(item.id)) {
            throw invalid_argument("Duplicate backlog item");
        }

        backlog.emplace(item.id, item);
    }

    void addDiscoveryFinding(const DiscoveryFinding& finding) {
        if (finding.threshold < 0 || finding.threshold > 1 ||
            finding.observedRate < 0 || finding.observedRate > 1) {
            throw invalid_argument("Discovery rates must be between 0 and 1");
        }

        findings.push_back(finding);
    }

    void addStatusCheck(const StatusCheck& check) {
        checks.push_back(check);
    }

    vector<reference_wrapper<BacklogItem>> rankedBacklog() {
        vector<reference_wrapper<BacklogItem>> ranked;

        for (auto& [id, item] : backlog) {
            if (item.state == ItemState::Ready ||
                item.state == ItemState::Discovery) {
                ranked.push_back(item);
            }
        }

        sort(ranked.begin(), ranked.end(),
             [](const auto& left, const auto& right) {
                 return left.get().score() > right.get().score();
             });

        return ranked;
    }

    void createSprint(const Sprint& sprint) {
        if (sprint.capacity <= 0) {
            throw invalid_argument("Sprint capacity must be positive");
        }

        if (sprints.contains(sprint.id)) {
            throw invalid_argument("Duplicate sprint");
        }

        Sprint actual = sprint;
        int remaining = sprint.capacity;

        for (auto itemRef : rankedBacklog()) {
            BacklogItem& item = itemRef.get();

            if (item.effort <= remaining) {
                item.state = ItemState::InProgress;
                actual.selectedItems.push_back(item.id);
                remaining -= item.effort;
            }
        }

        if (actual.selectedItems.empty()) {
            throw invalid_argument("Sprint cannot be created without selected work");
        }

        sprints.emplace(actual.id, actual);
    }

    void completeItem(const string& itemId, const string& sprintId) {
        auto itemIt = backlog.find(itemId);
        auto sprintIt = sprints.find(sprintId);

        if (itemIt == backlog.end() || sprintIt == sprints.end()) {
            throw invalid_argument("Unknown item or sprint");
        }

        const auto& selected = sprintIt->second.selectedItems;

        if (find(selected.begin(), selected.end(), itemId) == selected.end()) {
            throw invalid_argument("Item was not selected for this sprint");
        }

        if (itemIt->second.state != ItemState::InProgress) {
            throw invalid_argument("Only in-progress items can be completed");
        }

        itemIt->second.state = ItemState::Done;
    }

    bool sprintGoalHasProductGoal(const Sprint& sprint) const {
        return goals.contains(
            roadmap.at("RO-01").productGoalId
        );
    }

    bool mergeLikeDeliveryEligibility(const string& sprintId) const {
        /*
         * This method uses a delivery-gate perspective: product work is not
         * considered complete merely because an item exists. The selected
         * scope must satisfy the sprint's capacity and governance rules.
         */
        auto sprintIt = sprints.find(sprintId);
        if (sprintIt == sprints.end()) {
            return false;
        }

        const Sprint& sprint = sprintIt->second;

        if (sprint.selectedItems.empty()) {
            return false;
        }

        for (const string& id : sprint.selectedItems) {
            auto itemIt = backlog.find(id);
            if (itemIt == backlog.end()) {
                return false;
            }

            if (itemIt->second.state != ItemState::Done) {
                return false;
            }
        }

        if (policy.requireDiscoveryValidation) {
            bool validated = any_of(
                findings.begin(),
                findings.end(),
                [](const DiscoveryFinding& finding) {
                    return finding.supportsHypothesis();
                }
            );

            if (!validated) {
                return false;
            }
        }

        for (const StatusCheck& check : checks) {
            if (check.required && !check.passed) {
                return false;
            }
        }

        return true;
    }

    void printReport() {
        cout << fixed << setprecision(2);
        cout << "PRODUCT MANAGEMENT ENGINE\n\n";

        cout << "Product goals: " << goals.size() << '\n';
        cout << "Roadmap outcomes: " << roadmap.size() << '\n';
        cout << "Backlog items: " << backlog.size() << '\n';
        cout << "Sprints: " << sprints.size() << "\n\n";

        cout << "Prioritized backlog:\n";

        for (auto itemRef : rankedBacklog()) {
            const BacklogItem& item = itemRef.get();

            cout << "  " << item.id
                 << " | score=" << item.score()
                 << " | effort=" << item.effort
                 << " | evidence=" << item.evidence.size()
                 << '\n';
        }

        cout << "\nDiscovery findings:\n";

        for (const auto& finding : findings) {
            cout << "  " << finding.experimentId
                 << " | observed=" << finding.observedRate
                 << " | threshold=" << finding.threshold
                 << " | supported="
                 << (finding.supportsHypothesis() ? "yes" : "no")
                 << '\n';
        }
    }
};

int main() {
    try {
        GovernancePolicy policy{
            2,
            true,
            true
        };

        ProductGovernanceEngine engine(policy);

        engine.addGoal({
            "PG-01",
            "Increase successful first-week activation.",
            "activation_rate",
            0.65
        });

        engine.addRoadmapOutcome({
            "RO-01",
            "Reduce onboarding friction before first value.",
            "PG-01",
            2
        });

        engine.addBacklogItem({
            "PB-101",
            "Simplify first-run setup",
            "Users abandon setup before first value.",
            90,
            8,
            Priority::Critical,
            ItemState::Ready,
            {"funnel_analysis", "user_interviews"}
        });

        engine.addBacklogItem({
            "PB-102",
            "Add contextual onboarding checklist",
            "Users cannot identify their next useful action.",
            82,
            5,
            Priority::High,
            ItemState::Ready,
            {"support_tickets", "interviews"}
        });

        engine.addBacklogItem({
            "PB-103",
            "Improve report navigation",
            "Existing users spend too long finding recurring reports.",
            60,
            13,
            Priority::Medium,
            ItemState::Ready,
            {"navigation_analytics"}
        });

        engine.addDiscoveryFinding({
            "EXP-01",
            "Guided setup improves first-value completion.",
            0.73,
            0.70
        });

        engine.addStatusCheck({
            "product-analytics-validation",
            true,
            true
        });

        engine.addStatusCheck({
            "security-validation",
            true,
            true
        });

        engine.createSprint({
            "SPR-01",
            1,
            "Improve the path from account creation to first value.",
            13,
            {}
        });

        engine.printReport();

        engine.completeItem("PB-101", "SPR-01");
        engine.completeItem("PB-102", "SPR-01");

        cout << "\nDelivery eligibility: "
             << (engine.mergeLikeDeliveryEligibility("SPR-01") ? "eligible" : "blocked")
             << '\n';

        /*
         * Complexity:
         * - Backlog ranking: O(n log n).
         * - Sprint selection: O(n log n) because ranking dominates.
         * - State lookup: O(log n) using std::map.
         *
         * The model uses deterministic validation and value/effort ranking.
         * In a production system, prioritization should incorporate product
         * strategy, dependencies, risk, confidence, and empirical evidence
         * rather than treating one numeric score as an automatic decision.
         */
    } catch (const exception& error) {
        cerr << "Product management workflow failed: "
             << error.what() << '\n';
        return 1;
    }

    return 0;
}
