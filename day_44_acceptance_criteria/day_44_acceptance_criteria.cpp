#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

enum class ReviewState {
    Pending,
    Approved,
    ChangesRequested,
    Commented,
    Dismissed
};

enum class CheckState {
    Pending,
    Passed,
    Failed
};

enum class MergeMethod {
    MergeCommit,
    Squash,
    Rebase
};

struct Scenario {
    string given;
    string when;
    string then;
    string expected;
    vector<string> tags;
};

struct AcceptanceCriterion {
    string id;
    string title;
    string description;
    string owner;
    string priority;
    vector<Scenario> scenarios;
};

struct Review {
    string reviewer;
    bool eligible;
    bool latestCommit;
    ReviewState state;
};

struct StatusCheck {
    string name;
    CheckState state;
    string commitSha;
};

struct BranchProtection {
    string branch;
    int requiredApprovals = 1;
    set<string> requiredChecks;
    bool requireConversationResolution = true;
    bool requireLinearHistory = false;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool requireLatestApproval = true;
};

struct PullRequest {
    int number;
    string sourceBranch;
    string targetBranch;
    string headSha;
    bool draft = false;
    bool open = true;
    bool mergeConflict = false;
    bool conversationsResolved = true;
    vector<string> commits;
    vector<Review> reviews;
    vector<StatusCheck> checks;
};

struct EligibilityResult {
    bool eligible;
    vector<string> blockers;
};

class AcceptanceCriteriaValidator {
public:
    static vector<string> validate(const AcceptanceCriterion& criterion) {
        vector<string> errors;

        if (criterion.id.size() < 7 ||
            criterion.id.rfind("AC-", 0) != 0) {
            errors.push_back("Criterion ID must start with AC-.");
        }

        if (criterion.title.size() < 5 || criterion.title.size() > 120) {
            errors.push_back("Title must contain 5 to 120 characters.");
        }

        if (criterion.description.size() < 15) {
            errors.push_back("Description must explain expected behavior.");
        }

        if (criterion.owner.empty()) {
            errors.push_back("Criterion owner is required.");
        }

        if (criterion.scenarios.empty()) {
            errors.push_back("At least one scenario is required.");
        }

        for (size_t i = 0; i < criterion.scenarios.size(); ++i) {
            const auto& scenario = criterion.scenarios[i];
            if (scenario.given.empty() || scenario.when.empty() ||
                scenario.then.empty() || scenario.expected.empty()) {
                errors.push_back(
                    "Scenario " + to_string(i + 1) +
                    " has an incomplete Given-When-Then definition."
                );
            }
            if (scenario.tags.empty()) {
                errors.push_back(
                    "Scenario " + to_string(i + 1) + " has no tags."
                );
            }
        }

        return errors;
    }
};

class RepositoryGovernance {
    map<string, BranchProtection> protections;

    static int effectiveApprovals(const PullRequest& pr) {
        set<string> approvedReviewers;

        for (const auto& review : pr.reviews) {
            if (review.eligible &&
                review.state == ReviewState::Approved &&
                review.latestCommit) {
                approvedReviewers.insert(review.reviewer);
            }
        }

        return static_cast<int>(approvedReviewers.size());
    }

public:
    void protect(const BranchProtection& protection) {
        if (protection.branch.empty()) {
            throw invalid_argument("Protected branch name cannot be empty.");
        }
        if (protection.requiredApprovals < 0) {
            throw invalid_argument("Approval requirement cannot be negative.");
        }
        protections[protection.branch] = protection;
    }

    EligibilityResult evaluate(const PullRequest& pr) const {
        vector<string> blockers;

        if (!pr.open) {
            blockers.push_back("Pull request is closed.");
        }

        if (pr.draft) {
            blockers.push_back("Draft pull requests cannot be merged.");
        }

        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            blockers.push_back("Source and target branches are required.");
        }

        if (pr.sourceBranch == pr.targetBranch) {
            blockers.push_back("Source and target branches must differ.");
        }

        if (pr.headSha.size() < 7) {
            blockers.push_back("Head commit SHA is missing or invalid.");
        }

        if (pr.mergeConflict) {
            blockers.push_back("Merge conflicts must be resolved.");
        }

        auto policyIt = protections.find(pr.targetBranch);
        if (policyIt == protections.end()) {
            return {!blockers.empty(), blockers};
        }

        const BranchProtection& policy = policyIt->second;

        if (effectiveApprovals(pr) < policy.requiredApprovals) {
            blockers.push_back(
                "Required eligible approvals are missing or stale."
            );
        }

        if (policy.requireConversationResolution &&
            !pr.conversationsResolved) {
            blockers.push_back("Review conversations remain unresolved.");
        }

        for (const auto& required : policy.requiredChecks) {
            bool passed = false;

            // Only a passing check attached to the current head commit counts.
            for (const auto& check : pr.checks) {
                if (check.name == required &&
                    check.commitSha == pr.headSha &&
                    check.state == CheckState::Passed) {
                    passed = true;
                    break;
                }
            }

            if (!passed) {
                blockers.push_back(
                    "Required check missing, pending, failed, or stale: " +
                    required
                );
            }
        }

        if (policy.requireLinearHistory && pr.commits.size() > 1) {
            blockers.push_back(
                "The submitted history must satisfy the linear-history policy."
            );
        }

        return {blockers.empty(), blockers};
    }

    bool canForcePush(const string& branch) const {
        auto it = protections.find(branch);
        return it == protections.end() || it->second.allowForcePush;
    }

    bool canDeleteBranch(const string& branch) const {
        auto it = protections.find(branch);
        return it == protections.end() || it->second.allowDeletion;
    }
};

static string toString(ReviewState state) {
    switch (state) {
        case ReviewState::Pending: return "pending";
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes requested";
        case ReviewState::Commented: return "commented";
        case ReviewState::Dismissed: return "dismissed";
    }
    throw logic_error("Unknown review state.");
}

int main() {
    AcceptanceCriterion criterion{
        "AC-GOV-001",
        "Protect production branch merges",
        "A pull request must satisfy repository review and check policies.",
        "Repository Maintainer",
        "must",
        {
            {
                "Production branch is protected",
                "A pull request has no eligible approval",
                "The merge is blocked",
                "Automated checks cannot replace independent approval.",
                {"approval", "negative"}
            },
            {
                "Latest commit has an eligible approval and passing checks",
                "The merge service evaluates current policy",
                "The request is eligible if no other restriction applies",
                "Only current, qualifying evidence satisfies the policy.",
                {"branch-protection", "positive"}
            }
        }
    };

    const auto criterionErrors =
        AcceptanceCriteriaValidator::validate(criterion);

    cout << "Acceptance criterion: " << criterion.id << '\n';
    if (criterionErrors.empty()) {
        cout << "Definition validation: PASS\n";
    } else {
        for (const auto& error : criterionErrors) {
            cout << "Definition error: " << error << '\n';
        }
    }

    RepositoryGovernance governance;

    BranchProtection policy;
    policy.branch = "main";
    policy.requiredApprovals = 2;
    policy.requiredChecks = {"unit-tests", "security-scan"};
    policy.requireConversationResolution = true;
    policy.requireLatestApproval = true;
    policy.allowForcePush = false;
    policy.allowDeletion = false;

    governance.protect(policy);

    PullRequest pr;
    pr.number = 184;
    pr.sourceBranch = "feature/session-timeout";
    pr.targetBranch = "main";
    pr.headSha = "f19a82c";
    pr.commits = {"aa12bc3", "f19a82c"};
    pr.reviews = {
        {"reviewer-alex", true, true, ReviewState::Approved},
        {"reviewer-sam", true, false, ReviewState::Approved},
        {"author", false, true, ReviewState::Approved}
    };
    pr.checks = {
        {"unit-tests", CheckState::Passed, "f19a82c"},
        {"security-scan", CheckState::Pending, "f19a82c"},
        {"security-scan", CheckState::Passed, "aa12bc3"}
    };
    pr.conversationsResolved = false;

    auto result = governance.evaluate(pr);

    cout << "\nPull request #" << pr.number << '\n';
    cout << pr.sourceBranch << " -> " << pr.targetBranch << '\n';
    cout << "Merge eligible: " << (result.eligible ? "YES" : "NO") << '\n';

    for (const auto& blocker : result.blockers) {
        cout << "Blocked: " << blocker << '\n';
    }

    // A new approval and successful checks must refer to the current revision.
    pr.reviews[1].latestCommit = true;
    pr.checks[1].state = CheckState::Passed;
    pr.conversationsResolved = true;

    result = governance.evaluate(pr);
    cout << "\nAfter review and check updates\n";
    cout << "Merge eligible: " << (result.eligible ? "YES" : "NO") << '\n';

    if (!governance.canForcePush("main")) {
        cout << "Direct force-push to main is prohibited.\n";
    }

    if (!governance.canDeleteBranch("main")) {
        cout << "Deletion of main is prohibited.\n";
    }

    // A draft request remains ineligible even when its technical checks pass.
    pr.draft = true;
    result = governance.evaluate(pr);
    cout << "\nDraft state merge eligible: "
         << (result.eligible ? "YES" : "NO") << '\n';

    for (const auto& blocker : result.blockers) {
        cout << "Blocked: " << blocker << '\n';
    }

    return criterionErrors.empty() ? 0 : 1;
}
