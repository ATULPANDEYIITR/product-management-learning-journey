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

struct Commit {
    std::string sha;
    std::string message;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::vector<std::string> comments;
};

struct StatusCheck {
    std::string name;
    bool passed;
};

struct BranchProtection {
    int requiredApprovals = 2;
    std::set<std::string> requiredChecks;
    bool requireResolvedConversations = true;
    bool allowDirectPush = false;
    bool allowForcePush = false;
    bool allowBranchDeletion = false;
    bool requireLinearHistory = true;
};

class PullRequest {
private:
    int number_;
    std::string title_;
    std::string author_;
    std::string sourceBranch_;
    std::string targetBranch_;
    PRState state_ = PRState::Draft;

    std::vector<Commit> commits_;
    std::map<std::string, Review> reviews_;
    std::map<std::string, bool> statusChecks_;
    std::set<std::string> requestedReviewers_;

    int unresolvedConversations_ = 0;
    bool mergeConflicts_ = false;
    bool synchronizedWithBase_ = true;

public:
    PullRequest(
        int number,
        std::string title,
        std::string author,
        std::string sourceBranch,
        std::string targetBranch
    )
        : number_(number),
          title_(std::move(title)),
          author_(std::move(author)),
          sourceBranch_(std::move(sourceBranch)),
          targetBranch_(std::move(targetBranch)) {

        if (number <= 0 || sourceBranch_.empty() || targetBranch_.empty()) {
            throw std::invalid_argument("Invalid Pull Request identity.");
        }

        if (sourceBranch_ == targetBranch_) {
            throw std::invalid_argument("Source and target branches must differ.");
        }
    }

    void addCommit(Commit commit) {
        if (state_ == PRState::Merged || state_ == PRState::Closed) {
            throw std::logic_error("Cannot modify a closed or merged Pull Request.");
        }

        if (commit.sha.empty() || commit.message.empty()) {
            throw std::invalid_argument("Commit SHA and message are required.");
        }

        commits_.push_back(std::move(commit));

        // A new changeset may no longer represent the exact base-branch state.
        synchronizedWithBase_ = false;
    }

    void open() {
        if (state_ != PRState::Draft) {
            throw std::logic_error("Only draft Pull Requests can be opened.");
        }

        if (commits_.empty()) {
            throw std::logic_error("A Pull Request needs at least one commit.");
        }

        state_ = PRState::Open;
    }

    void requestReview(const std::string& reviewer) {
        if (state_ != PRState::Open) {
            throw std::logic_error("Reviewer requests require an open Pull Request.");
        }

        if (reviewer.empty() || reviewer == author_) {
            throw std::invalid_argument("Invalid reviewer.");
        }

        requestedReviewers_.insert(reviewer);
    }

    void submitReview(Review review) {
        if (state_ != PRState::Open) {
            throw std::logic_error("Only open Pull Requests can receive reviews.");
        }

        if (!requestedReviewers_.contains(review.reviewer)) {
            throw std::logic_error("Reviewer was not requested.");
        }

        if (review.reviewer == author_) {
            throw std::logic_error("Self-review is prohibited.");
        }

        reviews_[review.reviewer] = std::move(review);
    }

    void setStatusCheck(const std::string& name, bool passed) {
        if (name.empty()) {
            throw std::invalid_argument("Status check name cannot be empty.");
        }

        statusChecks_[name] = passed;
    }

    void addUnresolvedConversation() {
        ++unresolvedConversations_;
    }

    void resolveConversation() {
        if (unresolvedConversations_ == 0) {
            throw std::logic_error("No unresolved conversations exist.");
        }

        --unresolvedConversations_;
    }

    void resolveConflicts() {
        mergeConflicts_ = false;
        synchronizedWithBase_ = false;
    }

    void synchronizeWithBase() {
        if (mergeConflicts_) {
            throw std::logic_error("Conflicts must be resolved first.");
        }

        synchronizedWithBase_ = true;
    }

    void introduceConflict() {
        mergeConflicts_ = true;
        synchronizedWithBase_ = false;
    }

    void markMerged() {
        state_ = PRState::Merged;
    }

    int approvals() const {
        int count = 0;

        for (const auto& [reviewer, review] : reviews_) {
            if (review.state == ReviewState::Approved) {
                ++count;
            }
        }

        return count;
    }

    PRState state() const {
        return state_;
    }

    bool hasConflicts() const {
        return mergeConflicts_;
    }

    bool isSynchronized() const {
        return synchronizedWithBase_;
    }

    int unresolvedConversations() const {
        return unresolvedConversations_;
    }

    const std::map<std::string, bool>& checks() const {
        return statusChecks_;
    }

    const std::string& targetBranch() const {
        return targetBranch_;
    }
};

struct Evaluation {
    bool eligible;
    std::vector<std::string> failures;
};

class GovernanceEngine {
private:
    BranchProtection policy_;

public:
    explicit GovernanceEngine(BranchProtection policy)
        : policy_(std::move(policy)) {}

    Evaluation evaluate(const PullRequest& pr) const {
        std::vector<std::string> failures;

        if (pr.state() != PRState::Open) {
            failures.push_back("Pull Request is not open.");
        }

        if (pr.hasConflicts()) {
            failures.push_back("Merge conflicts exist.");
        }

        if (!pr.isSynchronized()) {
            failures.push_back("Pull Request is not synchronized with the base branch.");
        }

        if (
            policy_.requireResolvedConversations &&
            pr.unresolvedConversations() > 0
        ) {
            failures.push_back("Unresolved review conversations remain.");
        }

        if (pr.approvals() < policy_.requiredApprovals) {
            failures.push_back(
                "Insufficient independent approvals."
            );
        }

        for (const auto& check : policy_.requiredChecks) {
            auto iterator = pr.checks().find(check);

            if (iterator == pr.checks().end() || !iterator->second) {
                failures.push_back(
                    "Required status check failed or is missing: " + check
                );
            }
        }

        return {
            failures.empty(),
            std::move(failures)
        };
    }

    void merge(PullRequest& pr) const {
        Evaluation evaluation = evaluate(pr);

        if (!evaluation.eligible) {
            std::string message = "Merge blocked:";

            for (const auto& failure : evaluation.failures) {
                message += " " + failure;
            }

            throw std::runtime_error(message);
        }

        pr.markMerged();
    }
};

void printEvaluation(const Evaluation& evaluation) {
    std::cout << "Merge eligible: "
              << (evaluation.eligible ? "yes" : "no") << '\n';

    for (const auto& failure : evaluation.failures) {
        std::cout << "  Blocker: " << failure << '\n';
    }
}

int main() {
    try {
        BranchProtection protection;
        protection.requiredApprovals = 2;
        protection.requiredChecks = {"build", "tests", "security"};
        protection.requireResolvedConversations = true;
        protection.allowDirectPush = false;
        protection.allowForcePush = false;
        protection.allowBranchDeletion = false;
        protection.requireLinearHistory = true;

        GovernanceEngine governance(protection);

        PullRequest pr(
            314,
            "Harden payment authorization",
            "alice",
            "feature/payment-auth",
            "main"
        );

        pr.addCommit({"a001", "Validate payment authorization token"});
        pr.addCommit({"a002", "Reject unauthorized payment requests"});
        pr.open();

        pr.requestReview("bob");
        pr.requestReview("carol");

        pr.submitReview({
            "bob",
            ReviewState::Approved,
            {"Authorization boundary is correctly enforced."}
        });

        pr.submitReview({
            "carol",
            ReviewState::Approved,
            {"Failure handling is explicit."}
        });

        pr.setStatusCheck("build", true);
        pr.setStatusCheck("tests", true);
        pr.setStatusCheck("security", true);

        pr.addUnresolvedConversation();

        Evaluation first = governance.evaluate(pr);
        printEvaluation(first);

        pr.resolveConversation();
        pr.synchronizeWithBase();

        Evaluation second = governance.evaluate(pr);
        printEvaluation(second);

        governance.merge(pr);

        std::cout << "Pull Request successfully merged.\n";

        try {
            pr.addCommit({"a003", "Illegal post-merge modification"});
        } catch (const std::exception& error) {
            std::cout << "Expected failure: "
                      << error.what() << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
