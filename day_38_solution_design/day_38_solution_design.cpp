#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

enum class HypothesisStatus {
    Proposed,
    Validated,
    Rejected
};

enum class ConstraintType {
    Functional,
    NonFunctional,
    Technical,
    Business,
    Regulatory
};

std::string toString(HypothesisStatus status) {
    switch (status) {
        case HypothesisStatus::Proposed: return "proposed";
        case HypothesisStatus::Validated: return "validated";
        case HypothesisStatus::Rejected: return "rejected";
    }
    return "unknown";
}

std::string toString(ConstraintType type) {
    switch (type) {
        case ConstraintType::Functional: return "functional";
        case ConstraintType::NonFunctional: return "non-functional";
        case ConstraintType::Technical: return "technical";
        case ConstraintType::Business: return "business";
        case ConstraintType::Regulatory: return "regulatory";
    }
    return "unknown";
}

struct Hypothesis {
    std::string id;
    std::string statement;
    std::string evidenceRequired;
    HypothesisStatus status = HypothesisStatus::Proposed;
    double confidence = 0.5;

    void evaluate(double evidenceQuality,
                  double observedValue,
                  double requiredValue) {
        if (evidenceQuality < 0.0 || evidenceQuality > 1.0) {
            throw std::invalid_argument(
                "Evidence quality must be between 0 and 1."
            );
        }

        if (observedValue >= requiredValue) {
            status = HypothesisStatus::Validated;
            confidence = std::min(1.0, 0.5 + 0.5 * evidenceQuality);
        } else {
            status = HypothesisStatus::Rejected;
            confidence = std::max(0.0, 0.5 * (1.0 - evidenceQuality));
        }
    }
};

struct Constraint {
    std::string id;
    ConstraintType type;
    std::string description;
    bool hard;
};

struct Alternative {
    std::string name;
    std::string description;
    double expectedValue;
    double deliveryCost;
    double operatingCost;
    double implementationRisk;
    double scalability;
    double maintainability;
    double reversibility;
    double constraintPenalty;

    double score() const {
        return expectedValue
            + 0.20 * scalability
            + 0.15 * maintainability
            + 0.10 * reversibility
            - 0.35 * implementationRisk
            - 0.15 * deliveryCost
            - 0.10 * operatingCost
            - constraintPenalty;
    }
};

struct Decision {
    Alternative selected;
    std::vector<Alternative> rejected;
};

class GovernanceEngine {
private:
    std::map<std::string, Hypothesis> hypotheses;
    std::map<std::string, Constraint> constraints;
    std::vector<Alternative> alternatives;

    void ensureHypothesesResolved() const {
        for (const auto& [id, hypothesis] : hypotheses) {
            if (hypothesis.status == HypothesisStatus::Proposed) {
                throw std::runtime_error(
                    "Cannot make a design decision while hypothesis "
                    + id + " remains unresolved."
                );
            }
        }
    }

public:
    void addHypothesis(const Hypothesis& hypothesis) {
        if (hypotheses.contains(hypothesis.id)) {
            throw std::invalid_argument("Duplicate hypothesis: " + hypothesis.id);
        }
        hypotheses.emplace(hypothesis.id, hypothesis);
    }

    void addConstraint(const Constraint& constraint) {
        if (constraints.contains(constraint.id)) {
            throw std::invalid_argument("Duplicate constraint: " + constraint.id);
        }
        constraints.emplace(constraint.id, constraint);
    }

    void addAlternative(const Alternative& alternative) {
        alternatives.push_back(alternative);
    }

    std::vector<std::pair<std::string, double>> rankings() const {
        ensureHypothesesResolved();

        std::vector<std::pair<std::string, double>> result;
        for (const auto& alternative : alternatives) {
            result.emplace_back(alternative.name, alternative.score());
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

    Decision choose() const {
        ensureHypothesesResolved();

        if (alternatives.empty()) {
            throw std::runtime_error("No design alternatives were supplied.");
        }

        std::vector<Alternative> ordered = alternatives;

        std::sort(
            ordered.begin(),
            ordered.end(),
            [](const Alternative& left, const Alternative& right) {
                return left.score() > right.score();
            }
        );

        Decision decision{ordered.front(), {}};

        for (std::size_t i = 1; i < ordered.size(); ++i) {
            decision.rejected.push_back(ordered[i]);
        }

        return decision;
    }

    void printConstraints() const {
        std::cout << "\n=== Constraints ===\n";

        for (const auto& [id, constraint] : constraints) {
            std::cout
                << id << " [" << toString(constraint.type) << "] "
                << (constraint.hard ? "HARD" : "SOFT")
                << ": " << constraint.description << '\n';
        }
    }

    void printHypotheses() const {
        std::cout << "\n=== Hypotheses ===\n";

        for (const auto& [id, hypothesis] : hypotheses) {
            std::cout
                << id << ": "
                << toString(hypothesis.status)
                << ", confidence="
                << std::fixed << std::setprecision(2)
                << hypothesis.confidence << '\n';
        }
    }
};

GovernanceEngine buildEngine() {
    GovernanceEngine engine;

    Hypothesis asynchronous{
        "H-ASYNC",
        "Asynchronous processing absorbs traffic bursts without blocking clients.",
        "Load-test latency and queue-depth measurements."
    };
    asynchronous.evaluate(0.90, 0.91, 0.80);
    engine.addHypothesis(asynchronous);

    Hypothesis durability{
        "H-DURABLE",
        "Durable buffering preserves accepted events across consumer failures.",
        "Failure-injection and restart testing."
    };
    durability.evaluate(0.95, 0.98, 0.90);
    engine.addHypothesis(durability);

    Hypothesis replay{
        "H-REPLAY",
        "Replay is operationally valuable when downstream transformations change.",
        "Reprocessing evidence from production incidents."
    };
    replay.evaluate(0.75, 0.86, 0.70);
    engine.addHypothesis(replay);

    engine.addConstraint({
        "C-LATENCY",
        ConstraintType::NonFunctional,
        "Client acknowledgement should normally remain below 300 ms.",
        true
    });

    engine.addConstraint({
        "C-DURABILITY",
        ConstraintType::Technical,
        "Accepted events must survive a consumer restart.",
        true
    });

    engine.addConstraint({
        "C-BUDGET",
        ConstraintType::Business,
        "Infrastructure and operating cost must remain moderate.",
        true
    });

    engine.addConstraint({
        "C-AUDIT",
        ConstraintType::Regulatory,
        "Processing decisions must remain traceable.",
        true
    });

    engine.addAlternative({
        "Direct synchronous API",
        "The request waits for processing to complete.",
        6.0, 2.0, 2.0, 2.0, 4.0, 7.0, 8.0, 3.0
    });

    engine.addAlternative({
        "Queue-backed asynchronous architecture",
        "The API accepts work and durable workers process it independently.",
        9.0, 4.0, 4.0, 3.0, 8.0, 8.0, 8.0, 0.0
    });

    engine.addAlternative({
        "Managed event-streaming architecture",
        "Partitioned durable streams provide throughput and replay.",
        9.5, 7.0, 6.0, 5.0, 10.0, 6.0, 5.0, 1.5
    });

    return engine;
}

void printDecision(const Decision& decision) {
    std::cout << "\n=== Selected solution ===\n";
    std::cout << decision.selected.name
              << "\nScore: "
              << std::fixed << std::setprecision(3)
              << decision.selected.score() << '\n';

    std::cout << "\n=== Rejected alternatives ===\n";
    for (const auto& alternative : decision.rejected) {
        std::cout << alternative.name
                  << " -> " << alternative.score() << '\n';
    }

    std::cout << "\n=== Explicit trade-offs ===\n";
    std::cout
        << "Latency: asynchronous buffering is preferred because "
           "acknowledgement does not wait for downstream processing.\n";

    std::cout
        << "Simplicity: direct synchronous processing has fewer components "
           "but does not handle burst absorption as well.\n";

    std::cout
        << "Replay: event streaming is strongest when historical "
           "reprocessing is a first-class requirement.\n";
}

int main() {
    try {
        GovernanceEngine engine = buildEngine();

        engine.printHypotheses();
        engine.printConstraints();

        std::cout << "\n=== Alternative ranking ===\n";
        for (const auto& [name, score] : engine.rankings()) {
            std::cout << std::left << std::setw(42)
                      << name << score << '\n';
        }

        Decision decision = engine.choose();
        printDecision(decision);

        // Sensitivity analysis demonstrates why a decision is not absolute.
        // Increasing the cost of the selected design models a tighter budget.
        Alternative budgetVariant = decision.selected;
        budgetVariant.deliveryCost += 2.0;
        budgetVariant.operatingCost += 1.0;

        std::cout << "\n=== Budget sensitivity ===\n";
        std::cout << "Baseline score: " << decision.selected.score() << '\n';
        std::cout << "Tighter-budget score: " << budgetVariant.score() << '\n';

    } catch (const std::exception& error) {
        std::cerr << "Design evaluation failed: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
