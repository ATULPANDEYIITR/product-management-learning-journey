#include <algorithm>
#include <cmath>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

enum class Priority {
    Low,
    Medium,
    High,
    Critical
};

enum class WorkState {
    Proposed,
    Discovery,
    Estimated,
    Ready,
    Blocked,
    InProgress,
    Done
};

enum class ReviewDecision {
    Proposed,
    Accepted,
    Rejected
};

enum class TradeOff {
    Speed,
    Cost,
    Quality,
    Security,
    Scalability,
    Maintainability
};

std::string to_string(Priority priority) {
    switch (priority) {
        case Priority::Low: return "low";
        case Priority::Medium: return "medium";
        case Priority::High: return "high";
        case Priority::Critical: return "critical";
    }
    return "unknown";
}

std::string to_string(WorkState state) {
    switch (state) {
        case WorkState::Proposed: return "proposed";
        case WorkState::Discovery: return "discovery";
        case WorkState::Estimated: return "estimated";
        case WorkState::Ready: return "ready";
        case WorkState::Blocked: return "blocked";
        case WorkState::InProgress: return "in_progress";
        case WorkState::Done: return "done";
    }
    return "unknown";
}

class CollaborationError : public std::runtime_error {
public:
    explicit CollaborationError(const std::string& message)
        : std::runtime_error(message) {}
};

class ValidationError : public CollaborationError {
public:
    explicit ValidationError(const std::string& message)
        : CollaborationError(message) {}
};

class StateTransitionError : public CollaborationError {
public:
    explicit StateTransitionError(const std::string& message)
        : CollaborationError(message) {}
};

struct Estimate {
    int storyPoints;
    double engineeringDays;
    double confidence;

    Estimate(int points, double days, double confidenceValue)
        : storyPoints(points),
          engineeringDays(days),
          confidence(confidenceValue) {
        if (points <= 0 || days <= 0.0 ||
            confidenceValue <= 0.0 || confidenceValue > 1.0) {
            throw ValidationError("Invalid engineering estimate.");
        }
    }
};

struct Requirement {
    std::string key;
    std::string title;
    std::string description;
    std::vector<std::string> acceptanceCriteria;
    Priority priority;
    std::set<std::string> dependencies;
    std::vector<std::string> risks;
    std::optional<Estimate> estimate;
    WorkState state = WorkState::Proposed;

    void validate() const {
        if (key.empty() || title.empty() || description.empty()) {
            throw ValidationError("Requirement identity and description are required.");
        }

        if (acceptanceCriteria.empty()) {
            throw ValidationError("Acceptance criteria cannot be empty.");
        }

        for (const auto& criterion : acceptanceCriteria) {
            if (criterion.empty()) {
                throw ValidationError("Acceptance criteria cannot contain empty text.");
            }
        }
    }
};

struct ArchitectureOption {
    std::string name;
    std::string description;
    double deliveryDays;
    double monthlyCost;
    int scalability;
    int maintainability;
    int security;
    int complexity;

    ArchitectureOption(
        std::string optionName,
        std::string optionDescription,
        double delivery,
        double cost,
        int scale,
        int maintain,
        int secure,
        int complex)
        : name(std::move(optionName)),
          description(std::move(optionDescription)),
          deliveryDays(delivery),
          monthlyCost(cost),
          scalability(scale),
          maintainability(maintain),
          security(secure),
          complexity(complex) {
        if (name.empty() || deliveryDays <= 0 || monthlyCost < 0) {
            throw ValidationError("Invalid architecture option.");
        }

        for (int value : {scalability, maintainability, security, complexity}) {
            if (value < 1 || value > 5) {
                throw ValidationError("Architecture scores must be 1..5.");
            }
        }
    }
};

struct Decision {
    std::string id;
    std::string title;
    std::string chosenOption;
    std::string rationale;
    std::vector<std::string> tradeOffs;
    ReviewDecision status = ReviewDecision::Accepted;
};

class ArchitectureEngine {
private:
    std::map<TradeOff, double> weights_;

public:
    explicit ArchitectureEngine(std::map<TradeOff, double> weights)
        : weights_(std::move(weights)) {
        if (weights_.empty()) {
            throw ValidationError("Architecture weights cannot be empty.");
        }

        double total = 0.0;
        for (const auto& [key, weight] : weights_) {
            if (weight < 0.0) {
                throw ValidationError("Architecture weights cannot be negative.");
            }
            total += weight;
        }

        if (total <= 0.0) {
            throw ValidationError("At least one architecture weight must be positive.");
        }
    }

    double score(const ArchitectureOption& option) const {
        const auto get = [&](TradeOff key) {
            auto it = weights_.find(key);
            return it == weights_.end() ? 0.0 : it->second;
        };

        return
            get(TradeOff::Speed) * (1.0 / option.deliveryDays) +
            get(TradeOff::Cost) * (1.0 / std::max(option.monthlyCost, 1.0)) +
            get(TradeOff::Scalability) * option.scalability +
            get(TradeOff::Maintainability) * option.maintainability +
            get(TradeOff::Security) * option.security +
            get(TradeOff::Quality) * (6 - option.complexity);
    }

    std::vector<std::pair<const ArchitectureOption*, double>>
    rank(const std::vector<ArchitectureOption>& options) const {
        std::vector<std::pair<const ArchitectureOption*, double>> result;

        for (const auto& option : options) {
            result.emplace_back(&option, score(option));
        }

        std::sort(
            result.begin(),
            result.end(),
            [](const auto& left, const auto& right) {
                return left.second > right.second;
            }
        );

        return result;
    }
};

class GovernanceEngine {
private:
    Requirement requirement_;
    std::vector<ArchitectureOption> options_;
    std::vector<Decision> decisions_;

    bool isAllowed(WorkState from, WorkState to) const {
        switch (from) {
            case WorkState::Proposed:
                return to == WorkState::Discovery;
            case WorkState::Discovery:
                return to == WorkState::Estimated || to == WorkState::Blocked;
            case WorkState::Estimated:
                return to == WorkState::Ready || to == WorkState::Blocked;
            case WorkState::Ready:
                return to == WorkState::InProgress || to == WorkState::Blocked;
            case WorkState::Blocked:
                return to == WorkState::Discovery || to == WorkState::Ready;
            case WorkState::InProgress:
                return to == WorkState::Done || to == WorkState::Blocked;
            case WorkState::Done:
                return false;
        }
        return false;
    }

public:
    explicit GovernanceEngine(Requirement requirement)
        : requirement_(std::move(requirement)) {
        requirement_.validate();
    }

    void transition(WorkState next) {
        if (!isAllowed(requirement_.state, next)) {
            throw StateTransitionError(
                "Illegal state transition from " +
                to_string(requirement_.state) + " to " +
                to_string(next)
            );
        }

        if (next == WorkState::Ready) {
            assertReady();
        }

        requirement_.state = next;
    }

    void setEstimate(Estimate estimate) {
        requirement_.estimate = estimate;

        if (requirement_.state == WorkState::Discovery ||
            requirement_.state == WorkState::Proposed) {
            requirement_.state = WorkState::Estimated;
        }
    }

    void addOption(ArchitectureOption option) {
        auto duplicate = std::find_if(
            options_.begin(),
            options_.end(),
            [&](const auto& existing) {
                return existing.name == option.name;
            }
        );

        if (duplicate != options_.end()) {
            throw ValidationError("Duplicate architecture option.");
        }

        options_.push_back(std::move(option));
    }

    void addDecision(Decision decision) {
        if (decision.id.empty() ||
            decision.title.empty() ||
            decision.chosenOption.empty() ||
            decision.rationale.empty()) {
            throw ValidationError("Decision fields are incomplete.");
        }

        auto optionExists = std::any_of(
            options_.begin(),
            options_.end(),
            [&](const auto& option) {
                return option.name == decision.chosenOption;
            }
        );

        if (!optionExists) {
            throw ValidationError("Decision refers to an unknown architecture option.");
        }

        decisions_.push_back(std::move(decision));
    }

    void assertReady() const {
        if (!requirement_.estimate.has_value()) {
            throw ValidationError("An estimate is required.");
        }

        if (requirement_.estimate->confidence < 0.60) {
            throw ValidationError("Estimate confidence is below the readiness threshold.");
        }

        if (options_.empty()) {
            throw ValidationError("Architecture options are required.");
        }

        const bool acceptedDecision = std::any_of(
            decisions_.begin(),
            decisions_.end(),
            [](const Decision& decision) {
                return decision.status == ReviewDecision::Accepted;
            }
        );

        if (!acceptedDecision) {
            throw ValidationError("An accepted architecture decision is required.");
        }

        for (const auto& dependency : requirement_.dependencies) {
            if (dependency.rfind("BLOCKED:", 0) == 0) {
                throw ValidationError(
                    "Requirement has a blocked dependency: " + dependency
                );
            }
        }
    }

    const Requirement& requirement() const {
        return requirement_;
    }

    const std::vector<ArchitectureOption>& options() const {
        return options_;
    }

    const std::vector<Decision>& decisions() const {
        return decisions_;
    }
};

GovernanceEngine buildScenario() {
    Requirement requirement{
        "OBS-307",
        "Add audit-friendly administrative export",
        "Allow authorized administrators to export operational records "
        "without exposing secrets or unrestricted customer data.",
        {
            "Only authorized administrators can request exports.",
            "Exported records exclude secret credentials.",
            "Every export request creates an audit event.",
            "Large exports are processed asynchronously."
        },
        Priority::High,
        {"OBS-290"},
        {
            "Large exports can consume significant resources.",
            "Authorization mistakes could expose sensitive data."
        }
    };

    GovernanceEngine engine(requirement);
    engine.transition(WorkState::Discovery);

    engine.addOption(ArchitectureOption(
        "Asynchronous object export",
        "Create a job and produce an access-controlled export artifact.",
        6.0,
        260.0,
        5,
        5,
        5,
        3
    ));

    engine.addOption(ArchitectureOption(
        "Synchronous API export",
        "Generate the complete export during the request.",
        3.0,
        180.0,
        2,
        3,
        4,
        4
    ));

    engine.addOption(ArchitectureOption(
        "Direct database access",
        "Expose a restricted database reporting interface.",
        4.0,
        100.0,
        2,
        2,
        2,
        5
    ));

    ArchitectureEngine evaluator({
        {TradeOff::Speed, 0.10},
        {TradeOff::Cost, 0.05},
        {TradeOff::Scalability, 0.20},
        {TradeOff::Maintainability, 0.20},
        {TradeOff::Security, 0.35},
        {TradeOff::Quality, 0.10}
    });

    const auto ranking = evaluator.rank(engine.options());
    const std::string chosen = ranking.front().first->name;

    engine.addDecision(Decision{
        "ADR-033",
        "Administrative export architecture",
        chosen,
        "The asynchronous export creates a clear authorization boundary, "
        "supports large datasets, and provides an auditable job lifecycle.",
        {
            "Implementation takes longer than a synchronous endpoint.",
            "The platform must retain and protect generated artifacts."
        }
    });

    engine.setEstimate(Estimate(8, 6.0, 0.88));
    engine.transition(WorkState::Ready);

    return engine;
}

void validationTests() {
    try {
        Estimate invalid(0, 1.0, 0.5);
        throw std::logic_error("Invalid estimate accepted.");
    } catch (const ValidationError&) {
        // Expected failure.
    }

    Requirement requirement{
        "TEST-1",
        "State transition test",
        "Valid test requirement.",
        {"A test criterion exists."},
        Priority::Low
    };

    GovernanceEngine engine(requirement);

    try {
        engine.transition(WorkState::Ready);
        throw std::logic_error("Illegal transition accepted.");
    } catch (const StateTransitionError&) {
        // Expected failure.
    }
}

int main() {
    try {
        validationTests();

        GovernanceEngine engine = buildScenario();

        ArchitectureEngine evaluator({
            {TradeOff::Speed, 0.10},
            {TradeOff::Scalability, 0.20},
            {TradeOff::Maintainability, 0.20},
            {TradeOff::Security, 0.40},
            {TradeOff::Quality, 0.10}
        });

        const auto ranking = evaluator.rank(engine.options());

        std::cout << "PRODUCT-ENGINEERING GOVERNANCE ENGINE\n";
        std::cout << "====================================\n";
        std::cout << "Requirement: " << engine.requirement().key << '\n';
        std::cout << "Title: " << engine.requirement().title << '\n';
        std::cout << "Priority: " << to_string(engine.requirement().priority) << '\n';
        std::cout << "State: " << to_string(engine.requirement().state) << '\n';

        if (engine.requirement().estimate.has_value()) {
            const auto& estimate = *engine.requirement().estimate;
            std::cout << std::fixed << std::setprecision(2);
            std::cout << "Estimate: " << estimate.storyPoints
                      << " points, " << estimate.engineeringDays
                      << " days, confidence=" << estimate.confidence * 100
                      << "%\n";
        }

        std::cout << "\nArchitecture ranking:\n";
        for (std::size_t i = 0; i < ranking.size(); ++i) {
            std::cout << i + 1 << ". "
                      << ranking[i].first->name
                      << " | score=" << ranking[i].second
                      << " | delivery=" << ranking[i].first->deliveryDays
                      << " days\n";
        }

        std::cout << "\nAccepted decisions:\n";
        for (const auto& decision : engine.decisions()) {
            if (decision.status == ReviewDecision::Accepted) {
                std::cout << decision.id << ": "
                          << decision.chosenOption << '\n';
                std::cout << "Rationale: "
                          << decision.rationale << '\n';
            }
        }

        std::cout << "\nMerge/implementation readiness: APPROVED\n";
        return 0;
    } catch (const CollaborationError& error) {
        std::cerr << "Domain failure: " << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Unexpected failure: " << error.what() << '\n';
        return 2;
    }
}
