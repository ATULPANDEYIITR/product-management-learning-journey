#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

enum class DebtCategory {
    Code,
    Test,
    Architecture,
    Security,
    Infrastructure,
    Documentation
};

enum class DebtStatus {
    Open,
    Planned,
    InProgress,
    Resolved,
    Accepted
};

enum class ReviewState {
    Pending,
    Approved,
    ChangesRequested,
    Commented,
    Dismissed
};

struct Commit {
    std::string sha;
    std::string message;
    std::string author;
    int changedFiles{};
    int additions{};
    int deletions{};
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::vector<std::string> comments;
};

struct StatusCheck {
    std::string name;
    bool passed{};
    bool required{};
};

class TechnicalDebt {
public:
    int id;
    std::string title;
    DebtCategory category;
    DebtStatus status;
    std::string owner;
    double principalHours;
    double remediationHours;
    double monthlyInterestHours;
    int impact;
    double probability;
    int urgency;
    int securityExposure;
    std::set<std::string> affectedComponents;

    TechnicalDebt(
        int id_,
        std::string title_,
        DebtCategory category_,
        std::string owner_,
        double principalHours_,
        double remediationHours_,
        double monthlyInterestHours_,
        int impact_,
        double probability_,
        int urgency_,
        int securityExposure_,
        std::set<std::string> components)
        : id(id_),
          title(std::move(title_)),
          category(category_),
          status(DebtStatus::Open),
          owner(std::move(owner_)),
          principalHours(principalHours_),
          remediationHours(remediationHours_),
          monthlyInterestHours(monthlyInterestHours_),
          impact(impact_),
          probability(probability_),
          urgency(urgency_),
          securityExposure(securityExposure_),
          affectedComponents(std::move(components)) {
        validate();
    }

    void validate() const {
        if (id <= 0) throw std::invalid_argument("Debt ID must be positive.");
        if (title.empty() || owner.empty())
            throw std::invalid_argument("Debt title and owner are required.");
        if (principalHours <= 0 || remediationHours <= 0)
            throw std::invalid_argument("Effort estimates must be positive.");
        if (monthlyInterestHours < 0)
            throw std::invalid_argument("Interest cannot be negative.");
        if (impact < 1 || impact > 10)
            throw std::invalid_argument("Impact must be 1..10.");
        if (probability < 0 || probability > 1)
            throw std::invalid_argument("Probability must be 0..1.");
        if (urgency < 1 || urgency > 10)
            throw std::invalid_argument("Urgency must be 1..10.");
        if (securityExposure < 0 || securityExposure > 10)
            throw std::invalid_argument("Security exposure must be 0..10.");
    }

    double riskScore() const {
        return impact * probability * 10.0
             + urgency * 2.0
             + securityExposure * 3.0;
    }

    double priorityScore() const {
        return (
            monthlyInterestHours * 4.0
            + riskScore() * 2.0
            + securityExposure * 5.0
        ) / std::max(remediationHours, 1.0);
    }
};

struct PullRequest {
    int number{};
    std::string title;
    std::string author;
    std::string sourceBranch;
    std::string targetBranch;
    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    std::set<int> debtIds;
    bool draft{false};
    bool open{true};
    bool synchronized{true};
    bool conflicts{false};
    int unresolvedConversations{0};

    int approvals() const {
        return static_cast<int>(std::count_if(
            reviews.begin(),
            reviews.end(),
            [](const Review& review) {
                return review.state == ReviewState::Approved;
            }));
    }

    bool hasChangeRequest() const {
        return std::any_of(
            reviews.begin(),
            reviews.end(),
            [](const Review& review) {
                return review.state == ReviewState::ChangesRequested;
            });
    }

    bool requiredChecksPass() const {
        return std::all_of(
            checks.begin(),
            checks.end(),
            [](const StatusCheck& check) {
                return !check.required || check.passed;
            });
    }
};

struct BranchProtection {
    std::string branch;
    int requiredReviews{};
    std::set<std::string> requiredChecks;
    bool requireConversationResolution{};
    bool restrictDirectPush{};
    bool restrictForcePush{};
    bool restrictDeletion{};
    bool requireLinearHistory{};
    bool allowAdminBypass{};
    double maxDebtScore{};
};

struct MergeDecision {
    bool eligible{};
    std::vector<std::string> reasons;
};

class RepositoryGovernanceEngine {
private:
    std::string name_;
    std::set<std::string> branches_;
    std::map<int, TechnicalDebt> debt_;
    std::map<int, PullRequest> pullRequests_;
    std::map<std::string, BranchProtection> policies_;
    int nextDebtId_{1};
    int nextPrNumber_{1};

public:
    explicit RepositoryGovernanceEngine(std::string name)
        : name_(std::move(name)) {
        if (name_.empty()) {
            throw std::invalid_argument("Repository name is required.");
        }
    }

    void addBranch(const std::string& branch) {
        if (branch.empty() || branches_.contains(branch)) {
            throw std::invalid_argument("Invalid or duplicate branch.");
        }
        branches_.insert(branch);
    }

    void addDebt(TechnicalDebt item) {
        if (item.id != nextDebtId_) {
            throw std::invalid_argument("Debt IDs must be sequential.");
        }
        debt_.emplace(item.id, std::move(item));
        ++nextDebtId_;
    }

    void protectBranch(BranchProtection policy) {
        if (!branches_.contains(policy.branch)) {
            throw std::invalid_argument("Cannot protect an unknown branch.");
        }
        policies_[policy.branch] = std::move(policy);
    }

    PullRequest& createPullRequest(
        std::string title,
        std::string author,
        std::string source,
        std::string target,
        std::vector<Commit> commits,
        std::set<int> debtIds,
        bool draft = false) {

        if (!branches_.contains(source) || !branches_.contains(target)) {
            throw std::invalid_argument("Pull Request references unknown branch.");
        }
        if (source == target) {
            throw std::invalid_argument("Source and target branches must differ.");
        }
        for (int id : debtIds) {
            if (!debt_.contains(id)) {
                throw std::invalid_argument("Pull Request references unknown debt.");
            }
        }

        PullRequest pr;
        pr.number = nextPrNumber_++;
        pr.title = std::move(title);
        pr.author = std::move(author);
        pr.sourceBranch = std::move(source);
        pr.targetBranch = std::move(target);
        pr.commits = std::move(commits);
        pr.debtIds = std::move(debtIds);
        pr.draft = draft;

        auto [iterator, inserted] =
            pullRequests_.emplace(pr.number, std::move(pr));

        if (!inserted) {
            throw std::runtime_error("Pull Request number collision.");
        }

        return iterator->second;
    }

    double debtScore(const PullRequest& pr) const {
        double score = 0.0;
        for (int id : pr.debtIds) {
            score += debt_.at(id).priorityScore();
        }
        return score;
    }

    MergeDecision evaluate(
        const PullRequest& pr,
        bool administrator,
        const std::string& actor) const {

        MergeDecision decision{true, {}};

        auto block = [&](const std::string& reason) {
            decision.eligible = false;
            decision.reasons.push_back(reason);
        };

        if (!pr.open) block("Pull Request is closed.");
        if (pr.draft) block("Draft Pull Request cannot be merged.");
        if (pr.conflicts) block("Merge conflicts are unresolved.");
        if (!pr.synchronized) block("Source branch is stale.");

        auto policyIt = policies_.find(pr.targetBranch);
        if (policyIt == policies_.end()) {
            return decision;
        }

        const BranchProtection& policy = policyIt->second;

        if (pr.approvals() < policy.requiredReviews) {
            block("Required independent approvals are missing.");
        }

        if (pr.hasChangeRequest()) {
            block("A reviewer has requested changes.");
        }

        if (!pr.requiredChecksPass()) {
            block("A required status check has failed.");
        }

        std::set<std::string> passedChecks;
        for (const auto& check : pr.checks) {
            if (check.passed) passedChecks.insert(check.name);
        }

        for (const auto& required : policy.requiredChecks) {
            if (!passedChecks.contains(required)) {
                block("Required status check missing or failed: " + required);
            }
        }

        if (policy.requireConversationResolution &&
            pr.unresolvedConversations > 0) {
            block("Review conversations remain unresolved.");
        }

        const double score = debtScore(pr);
        if (score > policy.maxDebtScore) {
            block(
                "Technical debt score " + std::to_string(score)
                + " exceeds branch threshold."
            );
        }

        if (actor == pr.author && policy.requiredReviews > 0) {
            block("Pull Request author cannot provide all required approvals.");
        }

        // An administrator bypass is intentionally narrow. It does not erase
        // failed security checks or unresolved technical debt controls here.
        if (administrator && policy.allowAdminBypass) {
            decision.reasons.erase(
                std::remove_if(
                    decision.reasons.begin(),
                    decision.reasons.end(),
                    [](const std::string& reason) {
                        return reason.find("approvals") != std::string::npos;
                    }),
                decision.reasons.end());
            decision.eligible =
                std::all_of(
                    decision.reasons.begin(),
                    decision.reasons.end(),
                    [](const std::string&) { return false; })
                ? true
                : decision.eligible;
        }

        return decision;
    }

    std::vector<std::reference_wrapper<const TechnicalDebt>>
    prioritizedDebt() const {
        std::vector<std::reference_wrapper<const TechnicalDebt>> result;
        for (const auto& [id, item] : debt_) {
            if (item.status != DebtStatus::Resolved &&
                item.status != DebtStatus::Accepted) {
                result.emplace_back(item);
            }
        }

        std::sort(
            result.begin(),
            result.end(),
            [](const auto& a, const auto& b) {
                return a.get().priorityScore() > b.get().priorityScore();
            });

        return result;
    }

    std::vector<int> selectDebtForCapacity(double capacity, double ratio) const {
        if (capacity <= 0) {
            throw std::invalid_argument("Capacity must be positive.");
        }
        if (ratio < 0 || ratio > 1) {
            throw std::invalid_argument("Debt allocation ratio must be 0..1.");
        }

        double budget = capacity * ratio;
        std::vector<int> selected;

        for (const auto& itemRef : prioritizedDebt()) {
            const TechnicalDebt& item = itemRef.get();
            if (item.remediationHours <= budget) {
                selected.push_back(item.id);
                budget -= item.remediationHours;
            }
        }

        return selected;
    }

    void printDebtRanking() const {
        std::cout << "\nTechnical debt priority ranking\n";
        std::cout << std::string(78, '-') << '\n';

        for (const auto& itemRef : prioritizedDebt()) {
            const auto& item = itemRef.get();
            std::cout << std::fixed << std::setprecision(2)
                      << "#" << std::setw(2) << item.id
                      << " score=" << std::setw(7) << item.priorityScore()
                      << " risk=" << std::setw(6) << item.riskScore()
                      << " interest=" << std::setw(5)
                      << item.monthlyInterestHours << "h/month "
                      << item.title << '\n';
        }
    }
};

int main() {
    try {
        RepositoryGovernanceEngine engine("payments-platform");

        for (const std::string& branch :
             {"main", "develop", "feature/payment-refactor"}) {
            engine.addBranch(branch);
        }

        engine.addDebt(TechnicalDebt(
            1,
            "Duplicated payment validation",
            DebtCategory::Code,
            "payments-team",
            12,
            20,
            8,
            8,
            0.80,
            8,
            4,
            {"payments", "checkout"}
        ));

        engine.addDebt(TechnicalDebt(
            2,
            "Missing payment failure tests",
            DebtCategory::Test,
            "quality-team",
            8,
            16,
            6,
            7,
            0.70,
            7,
            3,
            {"payments"}
        ));

        engine.addDebt(TechnicalDebt(
            3,
            "Static integration credential",
            DebtCategory::Security,
            "security-team",
            3,
            6,
            2,
            10,
            0.50,
            10,
            10,
            {"integration-tests"}
        ));

        engine.addDebt(TechnicalDebt(
            4,
            "Manual deployment sequence",
            DebtCategory::Infrastructure,
            "platform-team",
            5,
            10,
            3,
            6,
            0.60,
            5,
            2,
            {"deployment"}
        ));

        engine.protectBranch(BranchProtection{
            "main",
            2,
            {"unit-tests", "security-scan", "integration-tests"},
            true,
            true,
            true,
            true,
            true,
            false,
            85.0
        });

        std::vector<Commit> commits{
            {"abc12345", "refactor payment validation", "nina", 7, 180, 110},
            {"def67890", "add payment failure tests", "nina", 5, 130, 12}
        };

        PullRequest& pr = engine.createPullRequest(
            "Refactor payment validation",
            "nina",
            "feature/payment-refactor",
            "main",
            commits,
            {1, 2}
        );

        pr.checks = {
            {"unit-tests", true, true},
            {"security-scan", true, true},
            {"integration-tests", false, true}
        };

        pr.reviews = {
            {"omar", ReviewState::Approved, {"Validation boundary improved."}},
            {"priya", ReviewState::ChangesRequested,
             {"Cover duplicate payment requests."}}
        };

        pr.unresolvedConversations = 1;

        engine.printDebtRanking();

        const MergeDecision decision =
            engine.evaluate(pr, false, "nina");

        std::cout << "\nMerge eligibility: "
                  << (decision.eligible ? "ELIGIBLE" : "BLOCKED")
                  << '\n';

        for (const auto& reason : decision.reasons) {
            std::cout << "- " << reason << '\n';
        }

        const auto selected = engine.selectDebtForCapacity(80.0, 0.30);

        std::cout << "\nDebt items selected within 30% capacity budget:\n";
        for (int id : selected) {
            std::cout << "- #" << id << '\n';
        }

        if (decision.eligible) {
            throw std::runtime_error(
                "Sample Pull Request unexpectedly became mergeable."
            );
        }

        if (selected.empty()) {
            throw std::runtime_error(
                "Priority allocation should select at least one item."
            );
        }

        std::cout << "\nValidation checks passed.\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Execution failed: " << ex.what() << '\n';
        return 1;
    }
}
