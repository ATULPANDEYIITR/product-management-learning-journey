#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

enum class PRState {
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

enum class CheckState {
    Pending,
    Passed,
    Failed
};

enum class MergeStrategy {
    MergeCommit,
    Squash,
    Rebase
};

struct Commit {
    std::string sha;
    std::string message;
    std::string author;
};

struct ReviewComment {
    std::string reviewer;
    std::string filePath;
    int line;
    std::string body;
    bool resolved;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::vector<ReviewComment> comments;
    bool stale = false;
    bool dismissed = false;
};

struct StatusCheck {
    std::string name;
    CheckState state;
};

struct BranchProtection {
    int requiredApprovals = 1;
    std::set<std::string> requiredChecks;
    bool requireConversationsResolved = true;
    bool requireLinearHistory = false;
    bool allowDirectPush = false;
    bool allowForcePush = false;
    bool allowBranchDeletion = false;
    bool allowAdminBypass = false;
    std::set<MergeStrategy> allowedMergeStrategies;
};

struct PullRequest {
    int number;
    std::string title;
    std::string sourceBranch;
    std::string targetBranch;
    std::string author;
    PRState state;
    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::map<std::string, StatusCheck> checks;
    std::set<std::string> requestedReviewers;
    std::string baseHeadAtCreation;

    void requestReview(const std::string& reviewer) {
        if (reviewer == author) {
            throw std::invalid_argument("Author cannot review their own Pull Request.");
        }
        requestedReviewers.insert(reviewer);
    }

    void addCommit(const Commit& commit) {
        if (state != PRState::Open && state != PRState::Draft) {
            throw std::runtime_error("Cannot modify a closed or merged Pull Request.");
        }

        commits.push_back(commit);

        for (auto& review : reviews) {
            if (review.state == ReviewState::Approved) {
                review.stale = true;
            }
        }
    }

    void addReview(const Review& review) {
        if (review.reviewer == author) {
            throw std::invalid_argument("Self-review is not permitted.");
        }
        reviews.push_back(review);
    }

    void setCheck(const StatusCheck& check) {
        checks[check.name] = check;
    }
};

struct MergeDecision {
    bool eligible;
    std::vector<std::string> reasons;
};

class Repository {
private:
    std::string name;
    std::map<std::string, BranchProtection> protections;
    std::map<int, PullRequest> pullRequests;
    int nextPR = 1;

public:
    struct Branch {
        std::string name;
        std::vector<Commit> commits;
        bool protectedBranch = false;

        std::string head() const {
            if (commits.empty()) return "";
            return commits.back().sha;
        }
    };

private:
    std::map<std::string, Branch> branches;

public:
    explicit Repository(std::string repositoryName)
        : name(std::move(repositoryName)) {}

    void addBranch(const Branch& branch) {
        if (branches.count(branch.name)) {
            throw std::invalid_argument("Branch already exists.");
        }
        branches.emplace(branch.name, branch);
    }

    void protectBranch(
        const std::string& branchName,
        const BranchProtection& policy
    ) {
        auto it = branches.find(branchName);
        if (it == branches.end()) {
            throw std::invalid_argument("Unknown branch.");
        }

        it->second.protectedBranch = true;
        protections[branchName] = policy;
    }

    PullRequest& createPullRequest(
        const std::string& title,
        const std::string& source,
        const std::string& target,
        const std::string& author,
        bool draft = false
    ) {
        auto sourceIt = branches.find(source);
        auto targetIt = branches.find(target);

        if (sourceIt == branches.end() || targetIt == branches.end()) {
            throw std::invalid_argument("Source and target branches must exist.");
        }

        if (source == target) {
            throw std::invalid_argument("Source and target branches must differ.");
        }

        PullRequest pr{
            nextPR++,
            title,
            source,
            target,
            author,
            draft ? PRState::Draft : PRState::Open,
            sourceIt->second.commits,
            {},
            {},
            {},
            targetIt->second.head()
        };

        auto [it, inserted] = pullRequests.emplace(pr.number, std::move(pr));
        if (!inserted) {
            throw std::runtime_error("Unable to create Pull Request.");
        }

        return it->second;
    }

    MergeDecision evaluateMerge(
        int prNumber,
        MergeStrategy strategy,
        bool administrator = false
    ) const {
        auto prIt = pullRequests.find(prNumber);
        if (prIt == pullRequests.end()) {
            throw std::invalid_argument("Unknown Pull Request.");
        }

        const PullRequest& pr = prIt->second;
        std::vector<std::string> reasons;

        if (pr.state != PRState::Open) {
            reasons.push_back("Pull Request is not open.");
        }

        if (pr.commits.empty()) {
            reasons.push_back("Pull Request has no proposed changes.");
        }

        auto policyIt = protections.find(pr.targetBranch);

        if (policyIt != protections.end()) {
            const BranchProtection& policy = policyIt->second;

            if (!policy.allowedMergeStrategies.count(strategy)) {
                reasons.push_back("Selected merge strategy is not allowed.");
            }

            std::set<std::string> validApprovals;

            for (const auto& review : pr.reviews) {
                if (
                    review.state == ReviewState::Approved &&
                    !review.stale &&
                    !review.dismissed &&
                    pr.requestedReviewers.count(review.reviewer)
                ) {
                    validApprovals.insert(review.reviewer);
                }
            }

            if (
                static_cast<int>(validApprovals.size()) <
                policy.requiredApprovals
            ) {
                reasons.push_back(
                    "Required approval count has not been reached."
                );
            }

            for (const auto& required : policy.requiredChecks) {
                auto checkIt = pr.checks.find(required);

                if (
                    checkIt == pr.checks.end() ||
                    checkIt->second.state != CheckState::Passed
                ) {
                    reasons.push_back(
                        "Required status check is missing or failed: " + required
                    );
                }
            }

            if (policy.requireConversationsResolved) {
                bool unresolved = false;

                for (const auto& review : pr.reviews) {
                    for (const auto& comment : review.comments) {
                        if (!comment.resolved) {
                            unresolved = true;
                        }
                    }
                }

                if (unresolved) {
                    reasons.push_back("Unresolved review conversations remain.");
                }
            }

            if (
                policy.requireLinearHistory &&
                strategy == MergeStrategy::MergeCommit
            ) {
                reasons.push_back(
                    "Merge commits violate the linear-history requirement."
                );
            }

            if (administrator && policy.allowAdminBypass) {
                return {true, {}};
            }
        }

        for (const auto& review : pr.reviews) {
            if (
                review.state == ReviewState::ChangesRequested &&
                !review.dismissed
            ) {
                reasons.push_back("A reviewer has requested changes.");
                break;
            }
        }

        return {reasons.empty(), reasons};
    }

    void merge(
        int prNumber,
        const std::string& actor,
        MergeStrategy strategy,
        bool administrator = false
    ) {
        MergeDecision decision =
            evaluateMerge(prNumber, strategy, administrator);

        if (!decision.eligible) {
            std::string message = "Merge blocked:";
            for (const auto& reason : decision.reasons) {
                message += " " + reason;
            }
            throw std::runtime_error(message);
        }

        PullRequest& pr = pullRequests.at(prNumber);
        Branch& target = branches.at(pr.targetBranch);

        if (strategy == MergeStrategy::Squash) {
            target.commits.push_back({
                "squash-" + std::to_string(pr.number),
                pr.title,
                actor
            });
        } else if (strategy == MergeStrategy::MergeCommit) {
            target.commits.push_back({
                "merge-" + std::to_string(pr.number),
                "Merge Pull Request #" + std::to_string(pr.number),
                actor
            });
        } else {
            target.commits.insert(
                target.commits.end(),
                pr.commits.begin(),
                pr.commits.end()
            );
        }

        pr.state = PRState::Merged;
    }

    Branch& branch(const std::string& name) {
        return branches.at(name);
    }
};

int main() {
    Repository repository("payments-platform");

    Repository::Branch mainBranch{
        "main",
        {
            {"c001", "Initial release", "alice"},
            {"c002", "Payment service", "alice"}
        },
        false
    };

    Repository::Branch featureBranch{
        "feature/refunds",
        {
            {"c001", "Initial release", "alice"},
            {"c002", "Payment service", "alice"},
            {"c003", "Add refund API", "bob"}
        },
        false
    };

    repository.addBranch(mainBranch);
    repository.addBranch(featureBranch);

    BranchProtection policy;
    policy.requiredApprovals = 2;
    policy.requiredChecks = {"unit-tests", "security-scan"};
    policy.requireConversationsResolved = true;
    policy.requireLinearHistory = true;
    policy.allowDirectPush = false;
    policy.allowForcePush = false;
    policy.allowBranchDeletion = false;
    policy.allowedMergeStrategies = {
        MergeStrategy::Squash,
        MergeStrategy::Rebase
    };

    repository.protectBranch("main", policy);

    PullRequest& pr = repository.createPullRequest(
        "Implement refund API",
        "feature/refunds",
        "main",
        "bob"
    );

    pr.requestReview("alice");
    pr.requestReview("carol");

    pr.addReview({
        "alice",
        ReviewState::Approved,
        {
            {
                "alice",
                "refund.cpp",
                42,
                "Validate refund amount against the original order.",
                true
            }
        },
        false,
        false
    });

    pr.addReview({
        "carol",
        ReviewState::Approved,
        {},
        false,
        false
    });

    pr.setCheck({"unit-tests", CheckState::Passed});
    pr.setCheck({"security-scan", CheckState::Passed});

    MergeDecision decision =
        repository.evaluateMerge(pr.number, MergeStrategy::Squash);

    std::cout << "PR #" << pr.number
              << " merge eligible: "
              << (decision.eligible ? "yes" : "no") << '\n';

    for (const auto& reason : decision.reasons) {
        std::cout << "BLOCKED: " << reason << '\n';
    }

    repository.merge(
        pr.number,
        "release-manager",
        MergeStrategy::Squash
    );

    std::cout << "PR state: merged\n";
    std::cout << "main HEAD: "
              << repository.branch("main").head() << '\n';

    // Demonstrate stale approval handling.
    PullRequest& second =
        repository.createPullRequest(
            "Improve refund validation",
            "feature/refunds",
            "main",
            "david"
        );

    second.requestReview("alice");
    second.addReview({
        "alice",
        ReviewState::Approved,
        {},
        false,
        false
    });

    second.setCheck({"unit-tests", CheckState::Passed});
    second.setCheck({"security-scan", CheckState::Passed});

    second.addCommit({
        "c004",
        "Fix invalid refund handling",
        "david"
    });

    MergeDecision stale =
        repository.evaluateMerge(
            second.number,
            MergeStrategy::Squash
        );

    std::cout << "PR #" << second.number
              << " eligible after new commit: "
              << (stale.eligible ? "yes" : "no") << '\n';

    for (const auto& reason : stale.reasons) {
        std::cout << "BLOCKED: " << reason << '\n';
    }

    return 0;
}
