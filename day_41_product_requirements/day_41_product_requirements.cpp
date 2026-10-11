#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

enum class RequirementType {
    Functional,
    NonFunctional,
    Business,
    Constraint
};

enum class Priority {
    Must,
    Should,
    Could,
    Wont
};

enum class Status {
    Draft,
    UnderReview,
    Approved,
    Implemented,
    Verified,
    Rejected
};

enum class ReviewDecision {
    Comment,
    RequestChanges,
    Approve
};

std::string toString(Priority value) {
    switch (value) {
        case Priority::Must: return "MUST";
        case Priority::Should: return "SHOULD";
        case Priority::Could: return "COULD";
        case Priority::Wont: return "WONT";
    }
    throw std::logic_error("Unknown priority");
}

std::string toString(Status value) {
    switch (value) {
        case Status::Draft: return "DRAFT";
        case Status::UnderReview: return "UNDER_REVIEW";
        case Status::Approved: return "APPROVED";
        case Status::Implemented: return "IMPLEMENTED";
        case Status::Verified: return "VERIFIED";
        case Status::Rejected: return "REJECTED";
    }
    throw std::logic_error("Unknown status");
}

struct AcceptanceCriterion {
    std::string given;
    std::string when;
    std::string then;

    void validate() const {
        if (given.empty() || when.empty() || then.empty()) {
            throw std::invalid_argument("Acceptance criteria must be complete");
        }
    }
};

struct Requirement {
    std::string id;
    std::string title;
    std::string description;
    RequirementType type;
    Priority priority;
    Status status = Status::Draft;
    std::string owner;
    std::string source;
    std::string metric;
    std::vector<AcceptanceCriterion> criteria;
    std::set<std::string> dependencies;
    std::set<std::string> deliveryTickets;
    int version = 1;

    void validate() const {
        if (id.empty() || title.empty() || description.size() < 15 ||
            owner.empty() || source.empty()) {
            throw std::invalid_argument(
                "Requirement identity, description, owner, and source are required"
            );
        }
        if (type == RequirementType::Functional && criteria.empty()) {
            throw std::invalid_argument(
                id + ": functional requirement needs acceptance criteria"
            );
        }
        if (type == RequirementType::NonFunctional && metric.empty()) {
            throw std::invalid_argument(
                id + ": non-functional requirement needs a measurable target"
            );
        }
        for (const auto& criterion : criteria) {
            criterion.validate();
        }
    }
};

struct Review {
    std::string reviewer;
    ReviewDecision decision;
    std::string comment;
    bool resolved = true;
};

struct PullRequest {
    std::string id;
    std::string sourceBranch;
    std::string targetBranch;
    std::set<std::string> requirementIds;
    std::set<std::string> commits;
    std::vector<Review> reviews;
    std::map<std::string, bool> checks;
    bool draft = false;
    bool open = true;
    bool baseSynchronized = true;
    bool hasConflicts = false;
    bool conversationsResolved = true;
    bool approved = false;
    std::size_t headVersion = 1;
    std::size_t approvedHeadVersion = 0;
};

struct BranchProtection {
    std::string branch;
    int requiredApprovals = 1;
    std::set<std::string> requiredChecks;
    bool blockDirectPush = true;
    bool prohibitForcePush = true;
    bool prohibitDeletion = true;
    bool requireConversationResolution = true;
    bool requireLinearHistory = true;
    bool dismissStaleApprovals = true;
    std::set<std::string> allowedMergeMethods = {"squash", "merge"};
    std::set<std::string> bypassActors;
};

struct MergeEvaluation {
    bool eligible = false;
    std::vector<std::string> blockers;
};

class RepositoryGovernance {
private:
    std::map<std::string, Requirement> requirements_;
    std::map<std::string, PullRequest> pullRequests_;
    std::map<std::string, BranchProtection> protections_;
    std::set<std::string> eligibleReviewers_;
    std::set<std::string> maintainers_;

    int countCurrentApprovals(const PullRequest& pr) const {
        // Only approvals for the current head count when stale reviews are dismissed.
        std::set<std::string> approvingReviewers;
        for (const auto& review : pr.reviews) {
            if (eligibleReviewers_.count(review.reviewer) == 0) {
                continue;
            }
            if (review.decision == ReviewDecision::Approve &&
                review.resolved &&
                review.comment.empty() == false &&
                pr.approvedHeadVersion == pr.headVersion) {
                approvingReviewers.insert(review.reviewer);
            }
        }
        return static_cast<int>(approvingReviewers.size());
    }

public:
    void addReviewer(const std::string& reviewer) {
        if (reviewer.empty()) {
            throw std::invalid_argument("Reviewer name cannot be empty");
        }
        eligibleReviewers_.insert(reviewer);
    }

    void addMaintainer(const std::string& actor) {
        if (actor.empty()) {
            throw std::invalid_argument("Maintainer name cannot be empty");
        }
        maintainers_.insert(actor);
    }

    void addRequirement(Requirement requirement) {
        requirement.validate();
        if (requirements_.count(requirement.id)) {
            throw std::invalid_argument("Duplicate requirement ID: " + requirement.id);
        }
        requirements_.emplace(requirement.id, std::move(requirement));
    }

    void protectBranch(BranchProtection policy) {
        if (policy.branch.empty() || policy.requiredApprovals < 0) {
            throw std::invalid_argument("Invalid branch protection policy");
        }
        protections_[policy.branch] = std::move(policy);
    }

    void openPullRequest(PullRequest pr) {
        if (pr.id.empty() || pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            throw std::invalid_argument("Pull Request identity and branches are required");
        }
        if (pr.sourceBranch == pr.targetBranch) {
            throw std::invalid_argument("Source and target branches must differ");
        }
        if (pr.requirementIds.empty()) {
            throw std::invalid_argument("Pull Request must link at least one requirement");
        }
        for (const auto& id : pr.requirementIds) {
            if (requirements_.count(id) == 0) {
                throw std::invalid_argument("Unknown requirement: " + id);
            }
        }
        if (pullRequests_.count(pr.id)) {
            throw std::invalid_argument("Duplicate Pull Request ID: " + pr.id);
        }
        pullRequests_.emplace(pr.id, std::move(pr));
    }

    void submitReview(
        const std::string& prId,
        const std::string& reviewer,
        ReviewDecision decision,
        const std::string& comment
    ) {
        auto it = pullRequests_.find(prId);
        if (it == pullRequests_.end()) {
            throw std::invalid_argument("Unknown Pull Request");
        }
        PullRequest& pr = it->second;
        if (!pr.open) {
            throw std::logic_error("Cannot review a closed Pull Request");
        }
        if (eligibleReviewers_.count(reviewer) == 0) {
            throw std::invalid_argument("Reviewer is not eligible");
        }
        if (comment.empty()) {
            throw std::invalid_argument(
                "Reviews require a meaningful rationale or review record"
            );
        }

        pr.reviews.push_back({reviewer, decision, comment, true});
        if (decision == ReviewDecision::Approve) {
            pr.approved = true;
            pr.approvedHeadVersion = pr.headVersion;
        } else if (decision == ReviewDecision::RequestChanges) {
            pr.approved = false;
            pr.approvedHeadVersion = 0;
        }
    }

    void pushNewCommit(const std::string& prId, const std::string& commit) {
        auto it = pullRequests_.find(prId);
        if (it == pullRequests_.end()) {
            throw std::invalid_argument("Unknown Pull Request");
        }
        PullRequest& pr = it->second;
        if (!pr.open || commit.empty()) {
            throw std::logic_error("Cannot update this Pull Request");
        }
        pr.commits.insert(commit);
        ++pr.headVersion;
        pr.baseSynchronized = false;
        pr.approved = false;

        // Review decisions refer to a specific changeset. The policy can require
        // fresh approval after the source branch changes.
        const auto protection = protections_.find(pr.targetBranch);
        if (protection != protections_.end() &&
            protection->second.dismissStaleApprovals) {
            pr.approvedHeadVersion = 0;
        }
    }

    void synchronizeBase(const std::string& prId, bool conflictsRemain) {
        auto it = pullRequests_.find(prId);
        if (it == pullRequests_.end()) {
            throw std::invalid_argument("Unknown Pull Request");
        }
        it->second.hasConflicts = conflictsRemain;
        it->second.baseSynchronized = !conflictsRemain;
    }

    MergeEvaluation evaluate(
        const std::string& prId,
        const std::string& mergeMethod
    ) const {
        const auto it = pullRequests_.find(prId);
        if (it == pullRequests_.end()) {
            throw std::invalid_argument("Unknown Pull Request");
        }

        const PullRequest& pr = it->second;
        MergeEvaluation result;
        const auto policyIt = protections_.find(pr.targetBranch);

        if (policyIt == protections_.end()) {
            result.blockers.push_back("No branch protection policy is configured");
            result.eligible = false;
            return result;
        }

        const BranchProtection& policy = policyIt->second;

        if (!pr.open) result.blockers.push_back("Pull Request is closed");
        if (pr.draft) result.blockers.push_back("Draft Pull Request cannot be merged");
        if (pr.commits.empty()) result.blockers.push_back("No commits are present");
        if (pr.hasConflicts) result.blockers.push_back("Merge conflicts remain");
        if (!pr.baseSynchronized) result.blockers.push_back("Base branch is not synchronized");
        if (policy.requireConversationResolution && !pr.conversationsResolved) {
            result.blockers.push_back("Review conversations remain unresolved");
        }
        if (policy.allowedMergeMethods.count(mergeMethod) == 0) {
            result.blockers.push_back("Merge method is not permitted");
        }
        if (policy.requireLinearHistory && mergeMethod == "merge") {
            result.blockers.push_back("Merge commit violates linear-history policy");
        }

        for (const auto& check : policy.requiredChecks) {
            const auto checkIt = pr.checks.find(check);
            if (checkIt == pr.checks.end() || !checkIt->second) {
                result.blockers.push_back("Required check failed or missing: " + check);
            }
        }

        const int approvals = countCurrentApprovals(pr);
        if (approvals < policy.requiredApprovals) {
            result.blockers.push_back(
                "Insufficient current eligible approvals: " +
                std::to_string(approvals) + "/" +
                std::to_string(policy.requiredApprovals)
            );
        }

        result.eligible = result.blockers.empty();
        return result;
    }

    void merge(
        const std::string& prId,
        const std::string& mergeMethod,
        const std::string& actor
    ) {
        auto it = pullRequests_.find(prId);
        if (it == pullRequests_.end()) {
            throw std::invalid_argument("Unknown Pull Request");
        }
        const auto policy = protections_.find(it->second.targetBranch);
        if (policy == protections_.end()) {
            throw std::logic_error("Target branch is not governed");
        }
        if (policy->second.bypassActors.count(actor) != 0) {
            // Bypass is explicit, named, and limited to a configured identity.
            it->second.open = false;
            std::cout << actor << " used the configured governance bypass.\n";
            return;
        }

        const MergeEvaluation evaluation = evaluate(prId, mergeMethod);
        if (!evaluation.eligible) {
            throw std::logic_error("Merge rejected by repository governance");
        }
        it->second.open = false;
        for (const auto& id : it->second.requirementIds) {
            requirements_.at(id).status = Status::Verified;
        }
        std::cout << "Merged " << prId << " using " << mergeMethod << ".\n";
    }

    void printEvaluation(
        const std::string& prId,
        const std::string& mergeMethod
    ) const {
        const auto result = evaluate(prId, mergeMethod);
        std::cout << "\nGovernance evaluation for " << prId << '\n';
        std::cout << "Eligible: " << std::boolalpha << result.eligible << '\n';
        for (const auto& blocker : result.blockers) {
            std::cout << "  Blocker: " << blocker << '\n';
        }
        if (result.blockers.empty()) {
            std::cout << "  All merge conditions are satisfied.\n";
        }
    }
};

int main() {
    try {
        RepositoryGovernance governance;
        governance.addReviewer("maya.rao");
        governance.addReviewer("arjun.sen");
        governance.addMaintainer("release.bot");

        BranchProtection protection;
        protection.branch = "main";
        protection.requiredApprovals = 2;
        protection.requiredChecks = {"unit-tests", "security-scan"};
        protection.blockDirectPush = true;
        protection.prohibitForcePush = true;
        protection.prohibitDeletion = true;
        protection.requireConversationResolution = true;
        protection.requireLinearHistory = true;
        protection.dismissStaleApprovals = true;
        protection.allowedMergeMethods = {"squash", "rebase"};
        governance.protectBranch(protection);

        Requirement requirement;
        requirement.id = "REQ-FR-042";
        requirement.title = "Validate supplier documents";
        requirement.description =
            "The portal checks required supplier documents before final submission.";
        requirement.type = RequirementType::Functional;
        requirement.priority = Priority::Must;
        requirement.owner = "Product manager";
        requirement.source = "Compliance workshop";
        requirement.criteria.push_back({
            "A published checklist exists",
            "The supplier submits an application",
            "The system reports missing documents and blocks final submission"
        });
        requirement.deliveryTickets.insert("SUP-110");
        governance.addRequirement(requirement);

        PullRequest pr;
        pr.id = "PR-284";
        pr.sourceBranch = "feature/supplier-validation";
        pr.targetBranch = "main";
        pr.requirementIds.insert("REQ-FR-042");
        pr.commits.insert("a8f12cd");
        pr.checks["unit-tests"] = true;
        pr.checks["security-scan"] = true;
        pr.conversationsResolved = true;
        pr.baseSynchronized = true;
        governance.openPullRequest(pr);

        governance.submitReview(
            "PR-284", "maya.rao", ReviewDecision::Approve,
            "Acceptance criteria and error handling are verified."
        );
        governance.printEvaluation("PR-284", "squash");

        governance.submitReview(
            "PR-284", "arjun.sen", ReviewDecision::Approve,
            "Supplier data authorization and audit requirements are satisfied."
        );
        governance.printEvaluation("PR-284", "squash");

        // A new commit invalidates approvals when the protected branch policy
        // requires dismissal of stale approvals.
        governance.pushNewCommit("PR-284", "b72de19");
        governance.synchronizeBase("PR-284", false);
        governance.printEvaluation("PR-284", "squash");

        governance.submitReview(
            "PR-284", "maya.rao", ReviewDecision::Approve,
            "Reviewed the updated changeset and regression tests."
        );
        governance.submitReview(
            "PR-284", "arjun.sen", ReviewDecision::Approve,
            "Revalidated supplier access boundaries."
        );
        governance.printEvaluation("PR-284", "squash");
        governance.merge("PR-284", "squash", "release.manager");

        std::cout << "\nRICE prioritization example\n";
        const double reach = 900.0;
        const double impact = 1.5;
        const double confidence = 0.8;
        const double effort = 3.0;
        if (effort <= 0.0 || confidence < 0.0 || confidence > 1.0) {
            throw std::invalid_argument("Invalid RICE inputs");
        }
        const double score = reach * impact * confidence / effort;
        std::cout << std::fixed << std::setprecision(2)
                  << "Document expiry reminders: " << score << '\n';
    } catch (const std::exception& error) {
        std::cerr << "Governance failure: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
