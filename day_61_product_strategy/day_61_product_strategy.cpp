#include <algorithm>
#include <chrono>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

enum class ProductStage {
    Discovery,
    Validation,
    Delivery,
    Scale
};

enum class PullRequestState {
    Draft,
    Open,
    Closed,
    Merged
};

enum class ReviewState {
    Commented,
    Approved,
    ChangesRequested,
    Dismissed
};

enum class MergeStrategy {
    MergeCommit,
    Squash,
    Rebase
};

struct ProductGoal {
    std::string name;
    std::string metric;
    double target;
    double current;

    bool achieved() const {
        return current >= target;
    }
};

struct ProductStrategy {
    std::string vision;
    std::string mission;
    std::vector<std::string> strategicChoices;
    std::vector<ProductGoal> goals;

    double score() const {
        if (goals.empty()) {
            return 0.0;
        }

        double total = 0.0;
        for (const auto& goal : goals) {
            total += std::min(goal.current / goal.target, 1.0);
        }
        return total / static_cast<double>(goals.size());
    }
};

struct Commit {
    std::string sha;
    std::string message;
    std::string author;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string reviewedCommit;
};

struct PullRequest {
    int number{};
    std::string title;
    std::string author;
    std::string sourceBranch;
    std::string targetBranch;
    PullRequestState state{PullRequestState::Open};
    MergeStrategy strategy{MergeStrategy::Squash};

    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::map<std::string, bool> statusChecks;
    std::set<std::string> openConversations;

    std::string headCommit() const {
        if (commits.empty()) {
            throw std::runtime_error("Pull Request has no commits.");
        }
        return commits.back().sha;
    }
};

struct BranchProtection {
    std::string branch;
    std::size_t requiredApprovals{};
    std::set<std::string> requiredChecks;
    bool requireResolvedConversations{true};
    bool allowDirectPush{false};
    bool allowForcePush{false};
    bool allowDeletion{false};
    bool requireLinearHistory{false};
    bool allowAdministratorBypass{false};
};

class Repository {
private:
    std::string name_;
    std::set<std::string> branches_;
    std::map<int, PullRequest> pullRequests_;
    std::map<std::string, BranchProtection> protections_;

public:
    explicit Repository(std::string name) : name_(std::move(name)) {
        if (name_.empty()) {
            throw std::invalid_argument("Repository name cannot be empty.");
        }
    }

    void addBranch(const std::string& branch) {
        if (branch.empty()) {
            throw std::invalid_argument("Branch name cannot be empty.");
        }
        branches_.insert(branch);
    }

    void protect(const BranchProtection& policy) {
        if (!branches_.count(policy.branch)) {
            throw std::invalid_argument(
                "Cannot protect a branch that does not exist."
            );
        }

        if (policy.requiredApprovals > 100) {
            throw std::invalid_argument("Approval requirement is unreasonable.");
        }

        protections_[policy.branch] = policy;
    }

    void addPullRequest(PullRequest pr) {
        if (!branches_.count(pr.targetBranch)) {
            throw std::invalid_argument("Target branch does not exist.");
        }

        if (pullRequests_.count(pr.number)) {
            throw std::invalid_argument("Pull Request number already exists.");
        }

        pullRequests_.emplace(pr.number, std::move(pr));
    }

    PullRequest& pullRequest(int number) {
        auto it = pullRequests_.find(number);
        if (it == pullRequests_.end()) {
            throw std::out_of_range("Pull Request does not exist.");
        }
        return it->second;
    }

    const BranchProtection& protectionFor(const std::string& branch) const {
        auto it = protections_.find(branch);
        if (it == protections_.end()) {
            throw std::runtime_error("Branch is not protected.");
        }
        return it->second;
    }
};

struct MergeEvaluation {
    bool eligible{false};
    std::vector<std::string> reasons;
};

class GovernanceEngine {
public:
    MergeEvaluation evaluate(const PullRequest& pr,
                              const BranchProtection& policy) const {
        MergeEvaluation result;

        if (pr.state != PullRequestState::Open) {
            result.reasons.push_back("Pull Request is not open.");
        }

        if (pr.commits.empty()) {
            result.reasons.push_back("Pull Request contains no commits.");
            result.eligible = false;
            return result;
        }

        const std::string head = pr.headCommit();

        std::set<std::string> approvals;
        std::set<std::string> requestedChanges;

        for (const auto& review : pr.reviews) {
            if (review.state == ReviewState::Approved &&
                review.reviewedCommit == head) {
                approvals.insert(review.reviewer);
            }

            if (review.state == ReviewState::ChangesRequested) {
                requestedChanges.insert(review.reviewer);
            }
        }

        if (!requestedChanges.empty()) {
            result.reasons.push_back("Requested changes remain.");
        }

        if (approvals.size() < policy.requiredApprovals) {
            std::ostringstream message;
            message << "Current approvals: " << approvals.size()
                    << "; required: " << policy.requiredApprovals << ".";
            result.reasons.push_back(message.str());
        }

        for (const auto& required : policy.requiredChecks) {
            auto check = pr.statusChecks.find(required);

            if (check == pr.statusChecks.end() || !check->second) {
                result.reasons.push_back(
                    "Required status check failed or is missing: " + required
                );
            }
        }

        if (policy.requireResolvedConversations &&
            !pr.openConversations.empty()) {
            result.reasons.push_back(
                "Unresolved review conversations remain."
            );
        }

        result.eligible = result.reasons.empty();
        return result;
    }

    std::string merge(Repository& repository, int number) const {
        PullRequest& pr = repository.pullRequest(number);
        const BranchProtection& policy =
            repository.protectionFor(pr.targetBranch);

        MergeEvaluation evaluation = evaluate(pr, policy);

        if (!evaluation.eligible) {
            std::ostringstream output;
            output << "MERGE BLOCKED\n";

            for (const auto& reason : evaluation.reasons) {
                output << "- " << reason << '\n';
            }

            return output.str();
        }

        pr.state = PullRequestState::Merged;

        std::string strategy;
        switch (pr.strategy) {
            case MergeStrategy::MergeCommit:
                strategy = "merge commit";
                break;
            case MergeStrategy::Squash:
                strategy = "squash";
                break;
            case MergeStrategy::Rebase:
                strategy = "rebase";
                break;
        }

        return "MERGED PR #" + std::to_string(pr.number) +
               " using " + strategy + ".";
    }
};

ProductStrategy createStrategy() {
    return {
        "Make repository change management predictable, reviewable, and safe.",
        "Connect product intent with controlled engineering delivery.",
        {
            "Use Pull Requests as the controlled change-entry workflow.",
            "Separate human review decisions from repository enforcement.",
            "Tie approvals to the exact commit being evaluated.",
            "Use automated checks as objective evidence.",
            "Protect critical branches from uncontrolled writes."
        },
        {
            {"review_coverage", "production PRs reviewed", 95.0, 92.0},
            {"compliant_merges", "policy-compliant merges", 90.0, 94.0},
            {"unresolved_conversations",
             "unresolved conversations on merged PRs",
             1.0,
             0.5}
        }
    };
}

PullRequest createHealthyPullRequest() {
    PullRequest pr;
    pr.number = 142;
    pr.title = "Introduce product strategy governance metrics";
    pr.author = "atul";
    pr.sourceBranch = "feature/product-strategy";
    pr.targetBranch = "main";

    pr.commits.push_back({
        "a1b2c3d4",
        "Implement product strategy model",
        "atul"
    });

    pr.commits.push_back({
        "e5f6a7b8",
        "Address review findings",
        "atul"
    });

    pr.reviews.push_back({
        "maya",
        ReviewState::Approved,
        "e5f6a7b8"
    });

    pr.reviews.push_back({
        "rohan",
        ReviewState::Approved,
        "e5f6a7b8"
    });

    pr.statusChecks["unit-tests"] = true;
    pr.statusChecks["security-scan"] = true;
    pr.statusChecks["product-policy"] = true;

    return pr;
}

PullRequest createStaleApprovalPullRequest() {
    PullRequest pr;
    pr.number = 143;
    pr.title = "Change product governance policy";
    pr.author = "atul";
    pr.sourceBranch = "feature/product-strategy";
    pr.targetBranch = "main";

    pr.commits.push_back({
        "11111111",
        "Initial governance policy",
        "atul"
    });

    pr.commits.push_back({
        "22222222",
        "Modify governance policy after review",
        "atul"
    });

    // Approvals belong to the previous commit and are therefore stale.
    pr.reviews.push_back({
        "maya",
        ReviewState::Approved,
        "11111111"
    });

    pr.reviews.push_back({
        "rohan",
        ReviewState::Approved,
        "11111111"
    });

    pr.statusChecks["unit-tests"] = true;
    pr.statusChecks["security-scan"] = true;
    pr.statusChecks["product-policy"] = true;

    return pr;
}

int main() {
    try {
        ProductStrategy strategy = createStrategy();

        std::cout << "PRODUCT STRATEGY\n";
        std::cout << "===============================\n";
        std::cout << "Vision: " << strategy.vision << '\n';
        std::cout << "Mission: " << strategy.mission << '\n';
        std::cout << std::fixed << std::setprecision(1);
        std::cout << "Strategy score: "
                  << strategy.score() * 100.0 << "%\n\n";

        Repository repository("payment-platform");

        repository.addBranch("main");
        repository.addBranch("feature/product-strategy");

        BranchProtection policy;
        policy.branch = "main";
        policy.requiredApprovals = 2;
        policy.requiredChecks = {
            "unit-tests",
            "security-scan",
            "product-policy"
        };
        policy.requireResolvedConversations = true;
        policy.allowDirectPush = false;
        policy.allowForcePush = false;
        policy.allowDeletion = false;
        policy.requireLinearHistory = true;

        repository.protect(policy);
        repository.addPullRequest(createHealthyPullRequest());
        repository.addPullRequest(createStaleApprovalPullRequest());

        GovernanceEngine engine;

        std::cout << "HEALTHY PULL REQUEST\n";
        std::cout << "===============================\n";

        MergeEvaluation healthy = engine.evaluate(
            repository.pullRequest(142),
            repository.protectionFor("main")
        );

        std::cout << "Eligible: "
                  << (healthy.eligible ? "true" : "false") << '\n';

        for (const auto& reason : healthy.reasons) {
            std::cout << "- " << reason << '\n';
        }

        std::cout << engine.merge(repository, 142) << "\n\n";

        std::cout << "STALE APPROVAL CASE\n";
        std::cout << "===============================\n";

        MergeEvaluation stale = engine.evaluate(
            repository.pullRequest(143),
            repository.protectionFor("main")
        );

        std::cout << "Eligible: "
                  << (stale.eligible ? "true" : "false") << '\n';

        for (const auto& reason : stale.reasons) {
            std::cout << "- " << reason << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
