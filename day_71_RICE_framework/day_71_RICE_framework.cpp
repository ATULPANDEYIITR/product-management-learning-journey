#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

/*
 * RICE Repository: Product Portfolio Governance Engine
 *
 * Implements a repository-independent prioritization engine.
 *
 * RICE Score = Reach * Impact * Confidence / Effort
 *
 * The engine evaluates:
 * - Product opportunities
 * - Evidence quality
 * - Confidence thresholds
 * - Portfolio budget
 * - Dependencies
 * - Scenario uncertainty
 * - Merge-like approval gates for prioritization decisions
 */

enum class Decision {
    ACCEPT,
    REVIEW,
    DEFER
};

enum class Priority {
    HIGH,
    MEDIUM,
    LOW
};

enum class EvidenceState {
    VERIFIED,
    UNVERIFIED,
    MISSING
};

struct RICEItem {
    std::string id;
    std::string name;
    double reach;
    double impact;
    double confidence;
    double effort;
    double strategicValue;
    EvidenceState evidence;
    std::vector<std::string> dependencies;
};

struct Evaluation {
    RICEItem item;
    double score;
    double efficiency;
    Priority priority;
    Decision decision;
    std::vector<std::string> limitations;
    std::size_t rank = 0;
};

struct Policy {
    double highThreshold = 100.0;
    double mediumThreshold = 30.0;
    double minimumConfidence = 40.0;
    bool requireVerifiedEvidence = true;
};

class ValidationError : public std::runtime_error {
public:
    explicit ValidationError(const std::string& message)
        : std::runtime_error(message) {}
};

class RICEEngine {
private:
    Policy policy_;

    static bool finite(double value) {
        return std::isfinite(value);
    }

    static Priority classify(double score, const Policy& policy) {
        if (score >= policy.highThreshold) {
            return Priority::HIGH;
        }

        if (score >= policy.mediumThreshold) {
            return Priority::MEDIUM;
        }

        return Priority::LOW;
    }

    void validate(const RICEItem& item) const {
        if (item.id.empty() || item.name.empty()) {
            throw ValidationError("ID and name are required.");
        }

        if (
            !finite(item.reach) ||
            !finite(item.impact) ||
            !finite(item.confidence) ||
            !finite(item.effort) ||
            !finite(item.strategicValue)
        ) {
            throw ValidationError("Numeric values must be finite.");
        }

        if (
            item.reach < 0 ||
            item.impact <= 0 ||
            item.effort <= 0 ||
            item.strategicValue < 0
        ) {
            throw ValidationError("Invalid RICE input values.");
        }

        if (item.confidence < 0 || item.confidence > 100) {
            throw ValidationError("Confidence must be between 0 and 100.");
        }

        std::unordered_set<std::string> uniqueDependencies;

        for (const auto& dependency : item.dependencies) {
            if (dependency == item.id) {
                throw ValidationError("Self-dependency is invalid.");
            }

            if (!uniqueDependencies.insert(dependency).second) {
                throw ValidationError("Duplicate dependency.");
            }
        }
    }

public:
    explicit RICEEngine(Policy policy = {})
        : policy_(policy) {

        if (
            !finite(policy_.highThreshold) ||
            !finite(policy_.mediumThreshold) ||
            policy_.highThreshold <= policy_.mediumThreshold ||
            policy_.mediumThreshold < 0 ||
            policy_.minimumConfidence < 0 ||
            policy_.minimumConfidence > 100
        ) {
            throw ValidationError("Invalid RICE policy.");
        }
    }

    static double calculateScore(const RICEItem& item) {
        return (
            item.reach *
            item.impact *
            (item.confidence / 100.0) /
            item.effort
        );
    }

    Evaluation evaluate(const RICEItem& item) const {
        validate(item);

        const double score = calculateScore(item);

        std::vector<std::string> limitations;

        if (item.confidence < policy_.minimumConfidence) {
            limitations.push_back("Confidence below policy threshold.");
        }

        if (item.reach == 0) {
            limitations.push_back("Zero measurable reach.");
        }

        if (item.evidence == EvidenceState::MISSING) {
            limitations.push_back("Evidence reference missing.");
        }

        if (item.evidence == EvidenceState::UNVERIFIED) {
            limitations.push_back("Evidence has not been verified.");
        }

        if (!item.dependencies.empty()) {
            limitations.push_back("Dependency scheduling required.");
        }

        Decision decision;

        if (
            item.confidence < policy_.minimumConfidence ||
            item.evidence == EvidenceState::MISSING ||
            (
                policy_.requireVerifiedEvidence &&
                item.evidence != EvidenceState::VERIFIED
            )
        ) {
            decision = Decision::REVIEW;
        } else if (score >= policy_.highThreshold) {
            decision = Decision::ACCEPT;
        } else if (score >= policy_.mediumThreshold) {
            decision = Decision::REVIEW;
        } else {
            decision = Decision::DEFER;
        }

        return {
            item,
            score,
            score / item.effort,
            classify(score, policy_),
            decision,
            limitations,
            0
        };
    }

    std::vector<Evaluation> evaluateAll(
        const std::vector<RICEItem>& items
    ) const {

        std::unordered_set<std::string> identifiers;

        for (const auto& item : items) {
            if (!identifiers.insert(item.id).second) {
                throw ValidationError("Duplicate item identifier.");
            }
        }

        std::unordered_map<std::string, const RICEItem*> index;

        for (const auto& item : items) {
            index[item.id] = &item;
        }

        // Validate dependencies and detect cycles using DFS.
        std::unordered_set<std::string> visiting;
        std::unordered_set<std::string> visited;

        std::function<void(const std::string&)> visit =
            [&](const std::string& id) {

                if (visiting.count(id)) {
                    throw ValidationError("Dependency cycle detected.");
                }

                if (visited.count(id)) {
                    return;
                }

                visiting.insert(id);

                for (const auto& dependency : index.at(id)->dependencies) {
                    if (!index.count(dependency)) {
                        throw ValidationError(
                            "Missing dependency: " + dependency
                        );
                    }

                    visit(dependency);
                }

                visiting.erase(id);
                visited.insert(id);
            };

        for (const auto& item : items) {
            visit(item.id);
        }

        std::vector<Evaluation> results;

        results.reserve(items.size());

        for (const auto& item : items) {
            results.push_back(evaluate(item));
        }

        std::sort(
            results.begin(),
            results.end(),
            [](const Evaluation& a, const Evaluation& b) {
                if (a.score != b.score) {
                    return a.score > b.score;
                }

                if (a.item.strategicValue != b.item.strategicValue) {
                    return a.item.strategicValue > b.item.strategicValue;
                }

                return a.item.id < b.item.id;
            }
        );

        for (std::size_t i = 0; i < results.size(); ++i) {
            results[i].rank = i + 1;
        }

        return results;
    }
};

class PortfolioOptimizer {
private:
    static constexpr int SCALE = 10;

public:
    static std::vector<Evaluation> optimize(
        const std::vector<Evaluation>& results,
        double budget
    ) {

        if (!std::isfinite(budget) || budget < 0) {
            throw ValidationError("Invalid effort budget.");
        }

        if (budget > 10000) {
            throw ValidationError("Budget exceeds optimizer limit.");
        }

        const int capacity = static_cast<int>(
            std::floor(budget * SCALE + 1e-9)
        );

        std::vector<Evaluation> eligible;

        for (const auto& result : results) {
            if (result.decision == Decision::ACCEPT) {
                eligible.push_back(result);
            }
        }

        std::vector<double> dp(capacity + 1, 0.0);

        std::vector<std::vector<int>> selected(capacity + 1);

        for (std::size_t i = 0; i < eligible.size(); ++i) {
            const int weight = static_cast<int>(
                std::ceil(eligible[i].item.effort * SCALE - 1e-12)
            );

            if (weight > capacity) {
                continue;
            }

            for (int c = capacity; c >= weight; --c) {
                const double candidate =
                    dp[c - weight] + eligible[i].score;

                if (candidate > dp[c]) {
                    dp[c] = candidate;
                    selected[c] = selected[c - weight];
                    selected[c].push_back(static_cast<int>(i));
                }
            }
        }

        std::vector<Evaluation> chosen;

        for (int index : selected[capacity]) {
            chosen.push_back(eligible[index]);
        }

        return chosen;
    }
};

class ScenarioAnalyzer {
public:
    static double calculate(
        const RICEItem& item,
        double reachFactor,
        double impactFactor,
        double confidenceFactor,
        double effortFactor
    ) {

        const double factors[] = {
            reachFactor,
            impactFactor,
            confidenceFactor,
            effortFactor
        };

        for (double factor : factors) {
            if (!std::isfinite(factor) || factor <= 0) {
                throw ValidationError("Invalid scenario factor.");
            }
        }

        const double adjustedConfidence = std::min(
            100.0,
            item.confidence * confidenceFactor
        );

        return (
            item.reach * reachFactor *
            item.impact * impactFactor *
            adjustedConfidence / 100.0 /
            (item.effort * effortFactor)
        );
    }

    static void report(const RICEItem& item) {
        std::cout << item.name << '\n';

        std::cout << "  Optimistic: "
                  << calculate(item, 1.2, 1.2, 1.1, 0.9)
                  << '\n';

        std::cout << "  Baseline: "
                  << RICEEngine::calculateScore(item)
                  << '\n';

        std::cout << "  Pessimistic: "
                  << calculate(item, 0.8, 0.8, 0.8, 1.2)
                  << '\n';
    }
};

static std::string decisionName(Decision decision) {
    switch (decision) {
        case Decision::ACCEPT: return "ACCEPT";
        case Decision::REVIEW: return "REVIEW";
        case Decision::DEFER: return "DEFER";
    }

    return "UNKNOWN";
}

static std::string priorityName(Priority priority) {
    switch (priority) {
        case Priority::HIGH: return "HIGH";
        case Priority::MEDIUM: return "MEDIUM";
        case Priority::LOW: return "LOW";
    }

    return "UNKNOWN";
}

int main() {
    try {
        Policy policy;
        policy.highThreshold = 100;
        policy.mediumThreshold = 30;
        policy.minimumConfidence = 40;
        policy.requireVerifiedEvidence = true;

        RICEEngine engine(policy);

        std::vector<RICEItem> items = {
            {
                "P001",
                "Account recovery",
                12000, 2.0, 90, 3.0, 8,
                EvidenceState::VERIFIED,
                {}
            },
            {
                "P002",
                "Dashboard redesign",
                8500, 1.0, 85, 4.0, 2,
                EvidenceState::VERIFIED,
                {}
            },
            {
                "P003",
                "Incident notifications",
                15000, 1.5, 95, 2.0, 9,
                EvidenceState::VERIFIED,
                {}
            },
            {
                "P004",
                "Recommendation engine",
                5000, 3.0, 35, 8.0, 5,
                EvidenceState::UNVERIFIED,
                {}
            },
            {
                "P005",
                "Accessibility improvements",
                6000, 1.5, 95, 2.5, 7,
                EvidenceState::VERIFIED,
                {}
            },
            {
                "P006",
                "Legacy reporting",
                0, 1.0, 80, 3.0, 1,
                EvidenceState::MISSING,
                {}
            }
        };

        auto results = engine.evaluateAll(items);

        std::cout << std::fixed << std::setprecision(2);

        std::cout << "\nRICE PRIORITIZATION\n";
        std::cout << "------------------------------------------------------------\n";

        for (const auto& result : results) {
            std::cout
                << result.rank << ". "
                << result.item.name
                << " | Score: " << result.score
                << " | Priority: " << priorityName(result.priority)
                << " | Decision: " << decisionName(result.decision)
                << '\n';

            for (const auto& limitation : result.limitations) {
                std::cout << "    - " << limitation << '\n';
            }
        }

        std::cout << "\nPORTFOLIO OPTIMIZATION\n";

        const double budget = 12.0;

        const auto selected = PortfolioOptimizer::optimize(
            results,
            budget
        );

        double totalEffort = 0;

        for (const auto& result : selected) {
            std::cout
                << result.item.name
                << " | Effort: "
                << result.item.effort
                << " | Score: "
                << result.score
                << '\n';

            totalEffort += result.item.effort;
        }

        std::cout << "Total effort: " << totalEffort
                  << " / " << budget << '\n';

        std::cout << "\nSCENARIO ANALYSIS\n";

        for (const auto& item : items) {
            ScenarioAnalyzer::report(item);
        }

        // Verify the fundamental RICE formula.
        RICEItem test {
            "TEST",
            "Test feature",
            1000, 2, 80, 4, 0,
            EvidenceState::VERIFIED,
            {}
        };

        if (
            std::abs(
                RICEEngine::calculateScore(test) - 400.0
            ) > 1e-9
        ) {
            throw std::runtime_error("RICE calculation test failed.");
        }

        std::cout << "\nValidation tests passed.\n";

    } catch (const std::exception& error) {
        std::cerr << "Execution error: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
