#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

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

struct Commit {
    std::string sha;
    std::string message;
};

struct Branch {
    std::string name;
    bool protectedBranch{false};
    std::vector<std::string> commits;
};

struct Reviewer {
    std::string username;
    std::set<std::string> teams;
    bool active{true};
};

struct ReviewComment {
    std::string reviewer;
    std::string path;
    int line{0};
    std::string body;
    bool resolved{false};
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
    bool dismissed{false};
    std::vector<ReviewComment> comments;
};

struct StatusCheck {
    std::string name;
    bool passed{false};
};

struct BranchProtection {
    int requiredReviews{1};
    std::set<std::string> requiredChecks;
    bool requireConversationResolution{true};
    bool allowDirectPush{false};
    bool allowForcePush{false};
    bool allowBranchDeletion{false};
    bool requireLinearHistory{false};
    std::set<MergeStrategy> allowedStrategies{
        MergeStrategy::Squash
    };
    std::set<std::string> bypassUsers;
};

struct PullRequest {
    int number{};
    std::string sourceBranch;
    std::string targetBranch;
    std::string title;
    std::string author;
    PullRequestState state{PullRequestState::Open};
    std::vector<std::string> commits;
    std::vector<Review> reviews;
    std::vector<ReviewComment> comments;
    std::map<std::string, StatusCheck> checks;
    MergeStrategy mergeStrategy{MergeStrategy::Squash};
};

class RepositoryGovernance {
private:
    std::string name;
    std::map<std::string, Branch> branches;
    std::map<std::string, Commit> commits;
    std::map<std::string, Reviewer> reviewers;
    std::map<int, PullRequest> pullRequests;
    std::map<std::string, BranchProtection> protections;

    static std::string strategyName(MergeStrategy strategy) {
        switch (strategy) {
            case MergeStrategy::MergeCommit:
                return "merge-commit";
            case MergeStrategy::Squash:
                return "squash";
            case MergeStrategy::Rebase:
                return "rebase";
        }
        return "unknown";
    }

public:
    explicit RepositoryGovernance(std::string repositoryName)
        : name(std::move(repositoryName)) {
        if (name.empty()) {
            throw std::invalid_argument("Repository name cannot be empty.");
        }
    }

    void addBranch(const std::string& branchName, bool protectedBranch = false) {
        if (branchName.empty()) {
            throw std::invalid_argument("Branch name cannot be empty.");
        }

        if (branches.contains(branchName)) {
            throw std::invalid_argument("Branch already exists.");
        }

        branches.emplace(
            branchName,
            Branch{branchName, protectedBranch, {}}
        );
    }

    void addCommit(
        const std::string& sha,
        const std::string& message,
        const std::string& branchName
    ) {
        if (sha.size() < 7 || sha.size() > 40) {
            throw std::invalid_argument("Commit SHA must contain 7-40 characters.");
        }

        if (message.empty()) {
            throw std::invalid_argument("Commit message cannot be empty.");
        }

        if (!branches.contains(branchName)) {
            throw std::invalid_argument("Target branch does not exist.");
        }

        if (commits.contains(sha)) {
            throw std::invalid_argument("Commit already exists.");
        }

        commits.emplace(sha, Commit{sha, message});
        branches.at(branchName).commits.push_back(sha);
    }

    void addReviewer(
        const std::string& username,
        const std::set<std::string>& teams
    ) {
        if (username.empty()) {
            throw std::invalid_argument("Reviewer username cannot be empty.");
        }

        if (reviewers.contains(username)) {
            throw std::invalid_argument("Reviewer already exists.");
        }

        reviewers.emplace(
            username,
            Reviewer{username, teams, true}
        );
    }

    void protectBranch(
        const std::string& branchName,
        const BranchProtection& policy
    ) {
        if (!branches.contains(branchName)) {
            throw std::invalid_argument("Unknown branch.");
        }

        if (policy.requiredReviews < 0) {
            throw std::invalid_argument("Required review count cannot be negative.");
        }

        branches.at(branchName).protectedBranch = true;
        protections[branchName] = policy;
    }

    PullRequest& createPullRequest(
        int number,
        const std::string& sourceBranch,
        const std::string& targetBranch,
        const std::string& title,
        const std::string& author
    ) {
        if (pullRequests.contains(number)) {
            throw std::invalid_argument("Pull request number already exists.");
        }

        if (!branches.contains(sourceBranch) ||
            !branches.contains(targetBranch)) {
            throw std::invalid_argument("Source and target branches must exist.");
        }

        if (sourceBranch == targetBranch) {
            throw std::invalid_argument("Source and target branches must differ.");
        }

        if (title.empty()) {
            throw std::invalid_argument("Pull request title cannot be empty.");
        }

        PullRequest pr;
        pr.number = number;
        pr.sourceBranch = sourceBranch;
        pr.targetBranch = targetBranch;
        pr.title = title;
        pr.author = author;
        pr.state = PullRequestState::Open;
        pr.commits = branches.at(sourceBranch).commits;

        auto [iterator, inserted] = pullRequests.emplace(number, std::move(pr));

        if (!inserted) {
            throw std::runtime_error("Unable to create pull request.");
        }

        return iterator->second;
    }

    void addReview(int number, const Review& review) {
        auto& pr = pullRequests.at(number);

        if (pr.state != PullRequestState::Open) {
            throw std::invalid_argument("Review requires an open pull request.");
        }

        if (!reviewers.contains(review.reviewer)) {
            throw std::invalid_argument("Reviewer is not registered.");
        }

        pr.reviews.push_back(review);
    }

    void addComment(int number, const ReviewComment& comment) {
        auto& pr = pullRequests.at(number);

        if (pr.state != PullRequestState::Open) {
            throw std::invalid_argument("Comment requires an open pull request.");
        }

        if (comment.body.empty()) {
            throw std::invalid_argument("Comment body cannot be empty.");
        }

        pr.comments.push_back(comment);
    }

    void setCheck(
        int number,
        const std::string& name,
        bool passed
    ) {
        auto& pr = pullRequests.at(number);
        pr.checks[name] = StatusCheck{name, passed};
    }

    std::pair<bool, std::vector<std::string>>
    evaluateMerge(int number) const {
        const auto& pr = pullRequests.at(number);
        std::vector<std::string> reasons;

        if (pr.state != PullRequestState::Open) {
            reasons.push_back("Pull request is not open.");
        }

        if (pr.commits.empty()) {
            reasons.push_back("Pull request contains no commits.");
        }

        const auto protectionIterator = protections.find(pr.targetBranch);

        if (protectionIterator == protections.end()) {
            return {reasons.empty(), reasons};
        }

        const auto& policy = protectionIterator->second;

        if (!policy.allowedStrategies.contains(pr.mergeStrategy)) {
            reasons.push_back("Selected merge strategy is prohibited.");
        }

        if (policy.requireConversationResolution) {
            const bool unresolved = std::any_of(
                pr.comments.begin(),
                pr.comments.end(),
                [](const ReviewComment& comment) {
                    return !comment.resolved;
                }
            );

            if (unresolved) {
                reasons.push_back("Unresolved review conversation exists.");
            }
        }

        std::set<std::string> approvals;
        std::set<std::string> requestedChanges;

        for (const auto& review : pr.reviews) {
            if (review.dismissed ||
                review.state == ReviewState::Dismissed) {
                continue;
            }

            const auto reviewerIterator = reviewers.find(review.reviewer);

            if (reviewerIterator == reviewers.end() ||
                !reviewerIterator->second.active) {
                continue;
            }

            /*
             * The review must reference a commit still contained by the PR.
             * A new commit therefore makes an older approval stale.
             */
            if (std::find(
                    pr.commits.begin(),
                    pr.commits.end(),
                    review.commitSha
                ) == pr.commits.end()) {
                continue;
            }

            if (review.state == ReviewState::Approved) {
                approvals.insert(review.reviewer);
            }

            if (review.state == ReviewState::ChangesRequested) {
                requestedChanges.insert(review.reviewer);
            }
        }

        if (!requestedChanges.empty()) {
            reasons.push_back("A reviewer has requested changes.");
        }

        if (static_cast<int>(approvals.size()) < policy.requiredReviews) {
            reasons.push_back(
                "Insufficient eligible approvals: " +
                std::to_string(approvals.size()) +
                "/" +
                std::to_string(policy.requiredReviews)
            );
        }

        for (const auto& requiredCheck : policy.requiredChecks) {
            const auto checkIterator = pr.checks.find(requiredCheck);

            if (checkIterator == pr.checks.end() ||
                !checkIterator->second.passed) {
                reasons.push_back(
                    "Required status check failed or is missing: " +
                    requiredCheck
                );
            }
        }

        return {reasons.empty(), reasons};
    }

    void mergePullRequest(int number, const std::string& actor) {
        auto& pr = pullRequests.at(number);
        const auto protectionIterator = protections.find(pr.targetBranch);

        bool bypass = false;

        if (protectionIterator != protections.end()) {
            bypass = protectionIterator->second.bypassUsers.contains(actor);
        }

        if (!bypass) {
            const auto [eligible, reasons] = evaluateMerge(number);

            if (!eligible) {
                std::string message = "Merge blocked:";

                for (const auto& reason : reasons) {
                    message += "\n - " + reason;
                }

                throw std::runtime_error(message);
            }
        }

        auto& target = branches.at(pr.targetBranch);

        if (pr.mergeStrategy == MergeStrategy::Squash) {
            target.commits.push_back("squash-" + std::to_string(pr.number));
        } else {
            target.commits.insert(
                target.commits.end(),
                pr.commits.begin(),
                pr.commits.end()
            );
        }

        pr.state = PullRequestState::Merged;

        std::cout
            << "PR #" << number
            << " merged into " << pr.targetBranch
            << " using " << strategyName(pr.mergeStrategy)
            << ".\n";
    }

    void printState() const {
        std::cout << "\nRepository: " << name << "\n";

        for (const auto& [branchName, branch] : branches) {
            std::cout
                << "Branch " << branchName
                << " protected=" << std::boolalpha
                << branch.protectedBranch
                << " commits=" << branch.commits.size()
                << "\n";
        }

        for (const auto& [number, pr] : pullRequests) {
            std::cout
                << "PR #" << number
                << " " << pr.title
                << " commits=" << pr.commits.size()
                << "\n";
        }
    }
};

int main() {
    try {
        RepositoryGovernance repository("inventory-platform");

        repository.addBranch("main", true);
        repository.addBranch("feature/relational-schema");

        repository.addCommit(
            "a1b2c3d",
            "Create warehouse table",
            "main"
        );

        repository.addCommit(
            "b2c3d4e",
            "Add inventory foreign key",
            "feature/relational-schema"
        );

        repository.addReviewer(
            "maya",
            {"database-reviewers"}
        );

        repository.addReviewer(
            "rahul",
            {"application-reviewers"}
        );

        BranchProtection policy;
        policy.requiredReviews = 1;
        policy.requiredChecks = {
            "sql-tests",
            "integration-tests"
        };
        policy.requireConversationResolution = true;
        policy.allowDirectPush = false;
        policy.allowForcePush = false;
        policy.allowBranchDeletion = false;
        policy.requireLinearHistory = true;
        policy.allowedStrategies = {MergeStrategy::Squash};

        repository.protectBranch("main", policy);

        PullRequest& pr = repository.createPullRequest(
            42,
            "feature/relational-schema",
            "main",
            "Add relational inventory schema",
            "atul"
        );

        pr.mergeStrategy = MergeStrategy::Squash;

        repository.addComment(
            42,
            ReviewComment{
                "maya",
                "schema.sql",
                32,
                "The inventory table should reference warehouse.",
                true
            }
        );

        repository.addReview(
            42,
            Review{
                "maya",
                ReviewState::Approved,
                "b2c3d4e",
                false,
                {}
            }
        );

        repository.setCheck(42, "sql-tests", true);
        repository.setCheck(42, "integration-tests", true);

        const auto [eligible, reasons] = repository.evaluateMerge(42);

        std::cout
            << "Merge eligible: "
            << std::boolalpha
            << eligible
            << "\n";

        for (const auto& reason : reasons) {
            std::cout << "Blocking reason: " << reason << "\n";
        }

        if (eligible) {
            repository.mergePullRequest(42, "atul");
        }

        repository.printState();
    } catch (const std::exception& exception) {
        std::cerr << "Error: " << exception.what() << "\n";
        return 1;
    }

    return 0;
}
