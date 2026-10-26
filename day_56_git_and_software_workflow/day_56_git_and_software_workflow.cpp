#include <algorithm>
#include <chrono>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

enum class PRState { Draft, Open, Closed, Merged };
enum class ReviewState { Commented, Approved, ChangesRequested, Dismissed };
enum class CheckState { Pending, Passed, Failed };
enum class MergeStrategy { Merge, Squash, Rebase };

std::string to_string(PRState state) {
    switch (state) {
        case PRState::Draft: return "draft";
        case PRState::Open: return "open";
        case PRState::Closed: return "closed";
        case PRState::Merged: return "merged";
    }
    return "unknown";
}

std::string to_string(ReviewState state) {
    switch (state) {
        case ReviewState::Commented: return "commented";
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes_requested";
        case ReviewState::Dismissed: return "dismissed";
    }
    return "unknown";
}

std::string to_string(MergeStrategy strategy) {
    switch (strategy) {
        case MergeStrategy::Merge: return "merge";
        case MergeStrategy::Squash: return "squash";
        case MergeStrategy::Rebase: return "rebase";
    }
    return "unknown";
}

struct Commit {
    std::string sha;
    std::string author;
    std::string message;
    long long timestamp;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
    std::vector<std::string> comments;
};

struct StatusCheck {
    std::string name;
    CheckState state;
    std::string commitSha;
};

struct Branch {
    std::string name;
    std::vector<Commit> commits;
};

struct BranchProtection {
    int requiredApprovals{1};
    std::set<std::string> requiredChecks;
    bool requireResolvedConversations{true};
    bool allowDirectPush{false};
    bool allowForcePush{false};
    bool allowDeletion{false};
    bool requireLinearHistory{false};
    std::set<MergeStrategy> allowedStrategies{
        MergeStrategy::Squash,
        MergeStrategy::Rebase
    };
};

struct PullRequest {
    int number{};
    std::string source;
    std::string target;
    std::string author;
    PRState state{PRState::Open};
    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    int unresolvedConversations{};
    bool synchronized{true};
    std::optional<MergeStrategy> strategy;
};

class GovernanceError : public std::runtime_error {
public:
    explicit GovernanceError(const std::string& message)
        : std::runtime_error(message) {}
};

class RepositoryGovernance {
private:
    std::string name;
    std::set<std::string> users;
    std::map<std::string, Branch> branches;
    std::map<std::string, BranchProtection> protection;
    std::map<int, PullRequest> pullRequests;
    int nextPr{1};

    void requireBranch(const std::string& name) const {
        if (!branches.contains(name)) {
            throw GovernanceError("Unknown branch: " + name);
        }
    }

    static long long now() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count();
    }

    static std::string makeSha(
        const std::string& previous,
        const std::string& author,
        const std::string& message
    ) {
        std::hash<std::string> hash;
        std::stringstream stream;
        stream << std::hex << hash(previous + author + message + std::to_string(now()));
        return stream.str().substr(0, 12);
    }

public:
    explicit RepositoryGovernance(std::string repository)
        : name(std::move(repository)) {
        if (name.empty()) {
            throw GovernanceError("Repository name cannot be empty");
        }
    }

    void addUser(const std::string& user) {
        if (user.empty()) {
            throw GovernanceError("Username cannot be empty");
        }
        users.insert(user);
    }

    void createBranch(const std::string& branch) {
        if (branches.contains(branch)) {
            throw GovernanceError("Branch already exists");
        }
        branches.emplace(branch, Branch{branch, {}});
    }

    void protectBranch(const std::string& branch, BranchProtection policy) {
        requireBranch(branch);
        if (policy.requiredApprovals < 0) {
            throw GovernanceError("Approval requirement cannot be negative");
        }
        protection[branch] = std::move(policy);
    }

    Commit commit(
        const std::string& branch,
        const std::string& author,
        const std::string& message
    ) {
        requireBranch(branch);
        if (!users.contains(author)) {
            throw GovernanceError("Unknown commit author");
        }
        if (message.empty()) {
            throw GovernanceError("Commit message cannot be empty");
        }

        auto& target = branches.at(branch);
        std::string previous =
            target.commits.empty() ? "root" : target.commits.back().sha;

        Commit result{
            makeSha(previous, author, message),
            author,
            message,
            now()
        };

        target.commits.push_back(result);
        return result;
    }

    int createPullRequest(
        const std::string& source,
        const std::string& target,
        const std::string& author,
        bool draft
    ) {
        requireBranch(source);
        requireBranch(target);

        if (source == target) {
            throw GovernanceError("Source and target must differ");
        }
        if (!users.contains(author)) {
            throw GovernanceError("Unknown PR author");
        }

        PullRequest pr;
        pr.number = nextPr++;
        pr.source = source;
        pr.target = target;
        pr.author = author;
        pr.state = draft ? PRState::Draft : PRState::Open;
        pr.commits = branches.at(source).commits;

        pullRequests.emplace(pr.number, std::move(pr));
        return nextPr - 1;
    }

    PullRequest& pr(int number) {
        auto it = pullRequests.find(number);
        if (it == pullRequests.end()) {
            throw GovernanceError("Unknown Pull Request");
        }
        return it->second;
    }

    void markReady(int number) {
        auto& request = pr(number);
        if (request.state != PRState::Draft) {
            throw GovernanceError("Only draft PRs can become ready");
        }
        request.state = PRState::Open;
    }

    void synchronize(int number) {
        auto& request = pr(number);
        request.commits = branches.at(request.source).commits;
        request.synchronized = true;
    }

    void addReview(
        int number,
        const std::string& reviewer,
        ReviewState state,
        std::vector<std::string> comments = {}
    ) {
        auto& request = pr(number);

        if (!users.contains(reviewer)) {
            throw GovernanceError("Unknown reviewer");
        }
        if (reviewer == request.author) {
            throw GovernanceError("Author cannot review own PR");
        }
        if (request.state != PRState::Open) {
            throw GovernanceError("PR is not open");
        }
        if (state == ReviewState::ChangesRequested && comments.empty()) {
            throw GovernanceError("Requested changes require comments");
        }

        std::string head =
            request.commits.empty() ? "" : request.commits.back().sha;

        request.reviews.push_back(
            Review{reviewer, state, head, std::move(comments)}
        );
    }

    void addCheck(int number, std::string name, CheckState state) {
        auto& request = pr(number);
        if (request.commits.empty()) {
            throw GovernanceError("PR has no commits");
        }

        request.checks.push_back(
            StatusCheck{
                std::move(name),
                state,
                request.commits.back().sha
            }
        );
    }

    void addConversation(int number) {
        ++pr(number).unresolvedConversations;
    }

    void resolveConversation(int number) {
        auto& request = pr(number);
        if (request.unresolvedConversations == 0) {
            throw GovernanceError("No unresolved conversation");
        }
        --request.unresolvedConversations;
    }

    std::vector<std::string> eligibility(
        int number,
        MergeStrategy strategy
    ) const {
        const auto& request = pullRequests.at(number);
        std::vector<std::string> errors;

        if (request.state != PRState::Open) {
            errors.push_back("PR is not open");
        }
        if (request.commits.empty()) {
            errors.push_back("PR contains no commits");
        }
        if (!request.synchronized) {
            errors.push_back("PR is not synchronized");
        }

        auto policyIt = protection.find(request.target);
        if (policyIt == protection.end()) {
            return errors;
        }

        const auto& policy = policyIt->second;
        const std::string head = request.commits.back().sha;

        // Latest review per reviewer determines the current decision.
        std::map<std::string, Review> latest;
        for (const auto& review : request.reviews) {
            latest[review.reviewer] = review;
        }

        int approvals = 0;
        for (const auto& [reviewer, review] : latest) {
            if (
                review.state == ReviewState::ChangesRequested &&
                review.commitSha == head
            ) {
                errors.push_back(
                    "Current requested changes from " + reviewer
                );
            }

            if (
                review.state == ReviewState::Approved &&
                review.commitSha == head
            ) {
                ++approvals;
            }
        }

        if (approvals < policy.requiredApprovals) {
            errors.push_back(
                "Approvals " + std::to_string(approvals) +
                "/" + std::to_string(policy.requiredApprovals)
            );
        }

        for (const auto& required : policy.requiredChecks) {
            bool passed = false;
            for (const auto& check : request.checks) {
                if (
                    check.name == required &&
                    check.state == CheckState::Passed &&
                    check.commitSha == head
                ) {
                    passed = true;
                    break;
                }
            }
            if (!passed) {
                errors.push_back("Required check failed: " + required);
            }
        }

        if (
            policy.requireResolvedConversations &&
            request.unresolvedConversations > 0
        ) {
            errors.push_back("Unresolved conversations remain");
        }

        if (!policy.allowedStrategies.contains(strategy)) {
            errors.push_back(
                "Merge strategy is prohibited: " + to_string(strategy)
            );
        }

        return errors;
    }

    void merge(int number, MergeStrategy strategy) {
        auto errors = eligibility(number, strategy);
        if (!errors.empty()) {
            std::ostringstream message;
            message << "Merge blocked:";
            for (const auto& error : errors) {
                message << " [" << error << "]";
            }
            throw GovernanceError(message.str());
        }

        auto& request = pr(number);
        auto& target = branches.at(request.target);
        const auto& source = branches.at(request.source);

        if (strategy == MergeStrategy::Squash) {
            std::string head = source.commits.back().sha;
            target.commits.push_back(
                Commit{
                    makeSha("squash", request.author, head),
                    request.author,
                    "Squash PR #" + std::to_string(number),
                    now()
                }
            );
        } else {
            target.commits.insert(
                target.commits.end(),
                source.commits.begin(),
                source.commits.end()
            );
        }

        request.strategy = strategy;
        request.state = PRState::Merged;
    }

    const Branch& getBranch(const std::string& name) const {
        requireBranch(name);
        return branches.at(name);
    }
};

void printEligibility(
    const std::vector<std::string>& errors
) {
    if (errors.empty()) {
        std::cout << "MERGE ELIGIBLE\n";
        return;
    }

    std::cout << "MERGE BLOCKED\n";
    for (const auto& error : errors) {
        std::cout << " - " << error << '\n';
    }
}

int main() {
    try {
        RepositoryGovernance repository("inventory-service");

        for (const std::string& user : {"alice", "bob", "carol"}) {
            repository.addUser(user);
        }

        repository.createBranch("main");
        repository.createBranch("feature/inventory-validation");

        BranchProtection protection;
        protection.requiredApprovals = 2;
        protection.requiredChecks = {"unit-tests", "security-scan"};
        protection.requireResolvedConversations = true;
        protection.allowDirectPush = false;
        protection.allowForcePush = false;
        protection.allowDeletion = false;
        protection.requireLinearHistory = true;

        repository.protectBranch("main", protection);

        repository.commit("main", "alice", "Initialize inventory service");
        repository.commit(
            "feature/inventory-validation",
            "alice",
            "Validate inventory quantities"
        );

        const int pr = repository.createPullRequest(
            "feature/inventory-validation",
            "main",
            "alice",
            true
        );

        repository.markReady(pr);
        repository.synchronize(pr);
        repository.addConversation(pr);

        repository.addReview(
            pr,
            "bob",
            ReviewState::Commented,
            {"Check negative inventory values."}
        );

        repository.addReview(
            pr,
            "carol",
            ReviewState::ChangesRequested,
            {"Reject negative quantities."}
        );

        repository.addCheck(pr, "unit-tests", CheckState::Passed);
        repository.addCheck(pr, "security-scan", CheckState::Passed);

        std::cout << "Initial evaluation:\n";
        printEligibility(
            repository.eligibility(pr, MergeStrategy::Squash)
        );

        repository.resolveConversation(pr);

        repository.addReview(pr, "bob", ReviewState::Approved);
        repository.addReview(pr, "carol", ReviewState::Approved);

        std::cout << "\nFinal evaluation:\n";
        printEligibility(
            repository.eligibility(pr, MergeStrategy::Squash)
        );

        repository.merge(pr, MergeStrategy::Squash);

        std::cout << "\nPR state: "
                  << to_string(repository.pr(pr).state) << '\n';
        std::cout << "main HEAD: "
                  << repository.getBranch("main").commits.back().sha
                  << '\n';

        /*
         * Security and performance design:
         * - Policy checks occur before mutating the protected branch.
         * - Review decisions are tied to the exact PR head SHA.
         * - Maps provide efficient branch/PR lookup.
         * - The in-memory model is O(R + C + S) for one eligibility check,
         *   where R is reviews, C is required checks, and S is submitted checks.
         */
    } catch (const std::exception& error) {
        std::cerr << "Governance failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
