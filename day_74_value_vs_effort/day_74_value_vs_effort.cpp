#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

enum class Risk {
    Low,
    Medium,
    High
};

enum class Priority {
    QuickWin,
    Strategic,
    FillIn,
    LowPriority
};

enum class CheckStatus {
    Passed,
    Failed,
    Pending
};

struct Estimate {
    double low;
    double expected;
    double high;

    void validate() const {
        if (!isfinite(low) || !isfinite(expected) ||
            !isfinite(high) || low < 0 ||
            expected <= 0 || low > expected ||
            expected > high) {
            throw invalid_argument("Invalid effort estimate.");
        }
    }

    double mean() const {
        return (low + expected + high) / 3.0;
    }
};

struct Opportunity {
    string id;
    string name;

    double customerImpact;
    double strategicAlignment;
    double revenueImpact;
    double urgency;

    double valueConfidence;
    double effortConfidence;

    Estimate effort;
    Risk risk;

    vector<string> dependencies;

    void validate() const {
        if (id.empty() || name.empty()) {
            throw invalid_argument("ID and name are required.");
        }

        const vector<double> ratings = {
            customerImpact,
            strategicAlignment,
            revenueImpact,
            urgency,
            valueConfidence,
            effortConfidence
        };

        for (double rating : ratings) {
            if (!isfinite(rating) || rating < 1 || rating > 5) {
                throw invalid_argument("Ratings must be 1-5.");
            }
        }

        effort.validate();

        set<string> uniqueDependencies(
            dependencies.begin(),
            dependencies.end()
        );

        if (uniqueDependencies.size() != dependencies.size()) {
            throw invalid_argument("Duplicate dependency.");
        }

        if (uniqueDependencies.count(id)) {
            throw invalid_argument("Self-dependency.");
        }
    }
};

struct Review {
    string reviewer;
    bool eligible;
    bool dismissed;
    bool changesRequested;
    bool approved;
};

struct PullRequest {
    string id;
    string sourceBranch;
    string targetBranch;

    bool open = true;
    bool draft = false;
    bool conversationsResolved = true;

    bool sourceUpToDate = true;
    bool mergeConflict = false;

    vector<Review> reviews;
    map<string, CheckStatus> statusChecks;
};

struct BranchProtection {
    bool enabled = true;
    bool prohibitDirectPush = true;
    bool prohibitForcePush = true;
    bool prohibitDeletion = true;
    bool requireLinearHistory = true;

    int requiredApprovals = 2;

    set<string> requiredChecks = {
        "build",
        "tests",
        "security"
    };

    bool administratorBypass = false;
};

struct Evaluation {
    string id;
    string name;

    double value;
    double adjustedValue;
    double effort;
    double ratio;

    Priority priority;
};

struct MergeDecision {
    bool eligible;
    vector<string> blockers;
};

class RepositoryGovernanceEngine {
private:
    unordered_map<string, Opportunity> opportunities;
    unordered_map<string, Evaluation> evaluations;

    static double riskFactor(Risk risk) {
        switch (risk) {
            case Risk::Low: return 1.0;
            case Risk::Medium: return 0.85;
            case Risk::High: return 0.65;
        }
        return 0.0;
    }

    void visit(
        const string& id,
        set<string>& active,
        set<string>& visited
    ) const {
        if (active.count(id)) {
            throw invalid_argument("Dependency cycle detected.");
        }

        if (visited.count(id)) return;

        auto it = opportunities.find(id);

        if (it == opportunities.end()) {
            throw invalid_argument("Unknown dependency: " + id);
        }

        active.insert(id);

        for (const string& dependency : it->second.dependencies) {
            visit(dependency, active, visited);
        }

        active.erase(id);
        visited.insert(id);
    }

public:
    void addOpportunity(const Opportunity& item) {
        item.validate();

        if (opportunities.count(item.id)) {
            throw invalid_argument("Duplicate opportunity.");
        }

        opportunities.emplace(item.id, item);
    }

    void validateDependencies() const {
        set<string> active;
        set<string> visited;

        for (const auto& [id, item] : opportunities) {
            visit(id, active, visited);
        }
    }

    Evaluation evaluate(const Opportunity& item) const {
        item.validate();

        double value = (
            item.customerImpact * 0.35 +
            item.strategicAlignment * 0.30 +
            item.revenueImpact * 0.20 +
            item.urgency * 0.15
        ) / 5.0 * 100.0;

        double confidence = min(
            item.valueConfidence,
            item.effortConfidence
        ) / 5.0;

        double adjusted = value *
            confidence *
            riskFactor(item.risk);

        double effort = item.effort.mean();
        double ratio = adjusted / effort;

        Priority priority;

        if (ratio >= 20) {
            priority = Priority::QuickWin;
        } else if (ratio >= 8) {
            priority = Priority::Strategic;
        } else if (adjusted >= 25) {
            priority = Priority::FillIn;
        } else {
            priority = Priority::LowPriority;
        }

        return {
            item.id,
            item.name,
            value,
            adjusted,
            effort,
            ratio,
            priority
        };
    }

    vector<Evaluation> evaluatePortfolio() {
        validateDependencies();

        vector<Evaluation> results;

        for (const auto& [id, item] : opportunities) {
            Evaluation result = evaluate(item);
            evaluations[id] = result;
            results.push_back(result);
        }

        sort(
            results.begin(),
            results.end(),
            [](const Evaluation& a, const Evaluation& b) {
                if (a.ratio != b.ratio) {
                    return a.ratio > b.ratio;
                }
                return a.adjustedValue > b.adjustedValue;
            }
        );

        return results;
    }

    MergeDecision checkMergeEligibility(
        const PullRequest& pr,
        const BranchProtection& policy
    ) const {
        vector<string> blockers;

        if (!pr.open) {
            blockers.push_back("Pull Request is closed.");
        }

        if (pr.draft) {
            blockers.push_back("Draft Pull Request cannot merge.");
        }

        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            blockers.push_back("Source or target branch is missing.");
        }

        if (pr.sourceBranch == pr.targetBranch) {
            blockers.push_back("Source and target branches must differ.");
        }

        if (!pr.sourceUpToDate) {
            blockers.push_back("Source branch is not synchronized.");
        }

        if (pr.mergeConflict) {
            blockers.push_back("Merge conflicts exist.");
        }

        if (!pr.conversationsResolved) {
            blockers.push_back("Unresolved review conversations.");
        }

        if (policy.enabled) {
            int approvals = 0;

            bool changesRequested = false;

            set<string> countedReviewers;

            for (const Review& review : pr.reviews) {
                if (!review.eligible || review.dismissed) {
                    continue;
                }

                if (!countedReviewers.insert(review.reviewer).second) {
                    continue;
                }

                if (review.changesRequested) {
                    changesRequested = true;
                }

                if (review.approved && !review.changesRequested) {
                    approvals++;
                }
            }

            if (approvals < policy.requiredApprovals) {
                blockers.push_back(
                    "Insufficient eligible approvals."
                );
            }

            if (changesRequested) {
                blockers.push_back(
                    "An active reviewer requested changes."
                );
            }

            for (const string& required : policy.requiredChecks) {
                auto it = pr.statusChecks.find(required);

                if (it == pr.statusChecks.end() ||
                    it->second != CheckStatus::Passed) {
                    blockers.push_back(
                        "Required check not passed: " + required
                    );
                }
            }
        }

        return {
            blockers.empty(),
            blockers
        };
    }

    void printPortfolio(const vector<Evaluation>& results) const {
        cout << "\nVALUE VS EFFORT PORTFOLIO\n";

        cout << left
             << setw(24) << "Opportunity"
             << setw(12) << "Value"
             << setw(12) << "Adjusted"
             << setw(12) << "Effort"
             << setw(12) << "Ratio"
             << "Priority\n";

        cout << string(82, '-') << '\n';

        for (const Evaluation& result : results) {
            cout << left
                 << setw(24) << result.name
                 << setw(12) << fixed << setprecision(2) << result.value
                 << setw(12) << result.adjustedValue
                 << setw(12) << result.effort
                 << setw(12) << result.ratio
                 << priorityName(result.priority)
                 << '\n';
        }
    }

    static string priorityName(Priority priority) {
        switch (priority) {
            case Priority::QuickWin: return "Quick Win";
            case Priority::Strategic: return "Strategic";
            case Priority::FillIn: return "Fill-In";
            case Priority::LowPriority: return "Low Priority";
        }
        return "Unknown";
    }

    vector<Evaluation> allocateCapacity(double capacity) const {
        if (!isfinite(capacity) || capacity < 0) {
            throw invalid_argument("Invalid capacity.");
        }

        vector<Evaluation> ranked;

        for (const auto& [id, result] : evaluations) {
            ranked.push_back(result);
        }

        sort(
            ranked.begin(),
            ranked.end(),
            [](const Evaluation& a, const Evaluation& b) {
                return a.ratio > b.ratio;
            }
        );

        set<string> selected;
        vector<Evaluation> result;
        double remaining = capacity;

        for (const Evaluation& candidate : ranked) {
            set<string> bundle;

            function<void(const string&)> resolve =
                [&](const string& id) {
                    if (bundle.count(id)) return;

                    bundle.insert(id);

                    for (const string& dependency :
                         opportunities.at(id).dependencies) {
                        resolve(dependency);
                    }
                };

            resolve(candidate.id);

            double required = 0;

            for (const string& id : bundle) {
                if (!selected.count(id)) {
                    required += evaluations.at(id).effort;
                }
            }

            if (required <= remaining) {
                for (const string& id : bundle) {
                    if (selected.insert(id).second) {
                        result.push_back(evaluations.at(id));
                    }
                }

                remaining -= required;
            }
        }

        sort(
            result.begin(),
            result.end(),
            [](const Evaluation& a, const Evaluation& b) {
                return a.ratio > b.ratio;
            }
        );

        return result;
    }
};

Opportunity makeOpportunity(
    string id,
    string name,
    double customer,
    double strategy,
    double revenue,
    double urgency,
    double valueConfidence,
    double effortConfidence,
    Estimate effort,
    Risk risk,
    vector<string> dependencies = {}
) {
    return {
        move(id),
        move(name),
        customer,
        strategy,
        revenue,
        urgency,
        valueConfidence,
        effortConfidence,
        effort,
        risk,
        move(dependencies)
    };
}

int main() {
    try {
        RepositoryGovernanceEngine engine;

        engine.addOpportunity(makeOpportunity(
            "OP-301", "Deployment Automation",
            5, 5, 4, 5, 5, 5,
            {2, 3, 5}, Risk::Low
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-302", "Analytics Dashboard",
            4, 3, 3, 3, 4, 4,
            {5, 8, 12}, Risk::Medium
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-303", "Security Automation",
            5, 5, 4, 5, 4, 4,
            {4, 6, 10}, Risk::Low
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-304", "Documentation Upgrade",
            2, 3, 1, 2, 5, 5,
            {2, 3, 4}, Risk::Low
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-305", "Data Integration",
            5, 5, 5, 4, 3, 3,
            {12, 18, 25}, Risk::High,
            {"OP-304"}
        ));

        auto portfolio = engine.evaluatePortfolio();

        engine.printPortfolio(portfolio);

        cout << "\nCAPACITY PLAN (15 UNITS)\n";

        auto allocation = engine.allocateCapacity(15);

        for (const auto& item : allocation) {
            cout << item.name << " | "
                 << item.effort << " effort units\n";
        }

        cout << "\nREPOSITORY GOVERNANCE EVALUATION\n";

        PullRequest pr;

        pr.id = "PR-501";
        pr.sourceBranch = "feature/security";
        pr.targetBranch = "main";

        pr.reviews = {
            {"reviewer-1", true, false, false, true},
            {"reviewer-2", true, false, false, true}
        };

        pr.statusChecks = {
            {"build", CheckStatus::Passed},
            {"tests", CheckStatus::Passed},
            {"security", CheckStatus::Passed}
        };

        BranchProtection policy;
        policy.requiredApprovals = 2;

        auto decision = engine.checkMergeEligibility(pr, policy);

        if (decision.eligible) {
            cout << "Pull Request is eligible for merging.\n";
        } else {
            cout << "Merge blocked:\n";

            for (const string& blocker : decision.blockers) {
                cout << " - " << blocker << '\n';
            }
        }

        // Failure scenario: unresolved review conversations.
        pr.conversationsResolved = false;

        auto blocked = engine.checkMergeEligibility(pr, policy);

        if (!blocked.eligible) {
            cout << "\nExpected governance failure detected:\n";

            for (const string& blocker : blocked.blockers) {
                cout << " - " << blocker << '\n';
            }
        }

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
