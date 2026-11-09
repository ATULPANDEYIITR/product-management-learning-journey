#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Prioritization Fundamentals
 *
 * A portfolio governance engine implementing:
 * - RICE, WSJF and weighted scoring
 * - Hard resource constraints
 * - Mandatory initiatives
 * - Dependency closure
 * - Opportunity-cost measurement
 * - Capacity-aware allocation
 * - Deterministic decision reporting
 *
 * Standard: C++17
 * Dependencies: Standard library only
 */

enum class Framework {
    RICE,
    WSJF,
    WEIGHTED
};

enum class Priority {
    CRITICAL,
    HIGH,
    MEDIUM,
    LOW
};

enum class DecisionStatus {
    SELECTED,
    DEFERRED,
    INELIGIBLE
};

struct Initiative {
    std::string id;
    std::string name;

    double reach = 0.0;
    double impact = 0.0;
    double confidence = 0.0;
    double effort = 0.0;

    double businessValue = 0.0;
    double urgency = 0.0;
    double riskReduction = 0.0;
    double strategicAlignment = 0.0;

    double cost = 0.0;

    bool mandatory = false;
    Priority priority = Priority::MEDIUM;

    std::set<std::string> dependencies;
};

struct Capacity {
    double effort = 0.0;
    double budget = 0.0;
};

struct Decision {
    std::string initiativeId;
    double score = 0.0;
    DecisionStatus status = DecisionStatus::DEFERRED;
    std::string reason;
};

struct AllocationResult {
    std::set<std::string> selected;
    std::set<std::string> deferred;

    double effortUsed = 0.0;
    double budgetUsed = 0.0;
    double businessValue = 0.0;
    double opportunityCost = 0.0;

    std::vector<Decision> decisions;
};


class PrioritizationEngine {
private:
    std::map<std::string, Initiative> initiatives;

    static bool finite(double value) {
        return std::isfinite(value);
    }

    void validateInitiative(const Initiative& item) const {
        if (item.id.empty() || item.name.empty()) {
            throw std::invalid_argument(
                "Initiative ID and name are required."
            );
        }

        const double values[] = {
            item.reach,
            item.impact,
            item.confidence,
            item.effort,
            item.businessValue,
            item.urgency,
            item.riskReduction,
            item.strategicAlignment,
            item.cost
        };

        for (double value : values) {
            if (!finite(value) || value < 0.0) {
                throw std::invalid_argument(
                    "Numeric initiative values must be finite and non-negative."
                );
            }
        }

        if (item.effort <= 0.0) {
            throw std::invalid_argument(
                "Effort must be greater than zero."
            );
        }

        if (item.confidence > 1.0) {
            throw std::invalid_argument(
                "Confidence must not exceed 1."
            );
        }

        if (
            item.impact > 10.0 ||
            item.businessValue > 10.0 ||
            item.urgency > 10.0 ||
            item.riskReduction > 10.0 ||
            item.strategicAlignment > 10.0
        ) {
            throw std::invalid_argument(
                "Normalized scoring factors must not exceed 10."
            );
        }

        if (item.dependencies.count(item.id)) {
            throw std::invalid_argument(
                "Self-dependency is prohibited."
            );
        }
    }

    void validateGraph() const {
        for (const auto& [id, item] : initiatives) {
            for (const auto& dependency : item.dependencies) {
                if (!initiatives.count(dependency)) {
                    throw std::invalid_argument(
                        "Missing dependency " + dependency +
                        " for " + id
                    );
                }
            }
        }

        std::set<std::string> visiting;
        std::set<std::string> visited;

        std::function<void(const std::string&)> visit =
            [&](const std::string& id) {

                if (visiting.count(id)) {
                    throw std::invalid_argument(
                        "Circular dependency detected."
                    );
                }

                if (visited.count(id)) {
                    return;
                }

                visiting.insert(id);

                for (const auto& dependency :
                     initiatives.at(id).dependencies) {
                    visit(dependency);
                }

                visiting.erase(id);
                visited.insert(id);
            };

        for (const auto& [id, item] : initiatives) {
            visit(id);
        }
    }

    std::set<std::string> dependencyClosure(
        const std::string& root
    ) const {
        std::set<std::string> closure;
        std::vector<std::string> stack{root};

        while (!stack.empty()) {
            std::string current = stack.back();
            stack.pop_back();

            if (!closure.insert(current).second) {
                continue;
            }

            for (const auto& dependency :
                 initiatives.at(current).dependencies) {
                stack.push_back(dependency);
            }
        }

        return closure;
    }

    double score(
        const Initiative& item,
        Framework framework
    ) const {

        switch (framework) {
            case Framework::RICE:
                return (
                    item.reach *
                    item.impact *
                    item.confidence /
                    item.effort
                );

            case Framework::WSJF:
                return (
                    item.businessValue +
                    item.urgency +
                    item.riskReduction
                ) / item.effort;

            case Framework::WEIGHTED:
                return (
                    item.businessValue * 0.30 +
                    item.strategicAlignment * 0.30 +
                    item.urgency * 0.15 +
                    item.riskReduction * 0.15 +
                    item.confidence * 10.0 * 0.10
                );
        }

        throw std::invalid_argument("Unsupported framework.");
    }

    std::vector<std::pair<std::string, double>> ranked(
        Framework framework
    ) const {
        std::vector<std::pair<std::string, double>> result;

        for (const auto& [id, item] : initiatives) {
            result.emplace_back(id, score(item, framework));
        }

        std::sort(
            result.begin(),
            result.end(),
            [&](const auto& left, const auto& right) {
                const auto& a = initiatives.at(left.first);
                const auto& b = initiatives.at(right.first);

                if (a.mandatory != b.mandatory) {
                    return a.mandatory;
                }

                if (left.second != right.second) {
                    return left.second > right.second;
                }

                return left.first < right.first;
            }
        );

        return result;
    }

public:
    explicit PrioritizationEngine(
        const std::vector<Initiative>& items
    ) {
        for (const auto& item : items) {
            validateInitiative(item);

            if (initiatives.count(item.id)) {
                throw std::invalid_argument(
                    "Duplicate initiative ID: " + item.id
                );
            }

            initiatives.emplace(item.id, item);
        }

        if (initiatives.empty()) {
            throw std::invalid_argument(
                "Portfolio cannot be empty."
            );
        }

        validateGraph();
    }

    AllocationResult allocate(
        const Capacity& capacity,
        Framework framework
    ) const {

        if (
            !finite(capacity.effort) ||
            !finite(capacity.budget) ||
            capacity.effort < 0 ||
            capacity.budget < 0
        ) {
            throw std::invalid_argument(
                "Invalid resource capacity."
            );
        }

        AllocationResult result;

        auto order = ranked(framework);

        std::map<std::string, double> scores;

        for (const auto& entry : order) {
            scores[entry.first] = entry.second;
        }

        // Include a dependency closure only once.
        auto include = [&](const std::string& id) -> bool {
            auto closure = dependencyClosure(id);

            double additionalEffort = 0.0;
            double additionalBudget = 0.0;

            for (const auto& key : closure) {
                if (result.selected.count(key)) {
                    continue;
                }

                const auto& item = initiatives.at(key);

                additionalEffort += item.effort;
                additionalBudget += item.cost;
            }

            const double epsilon = 1e-9;

            if (
                result.effortUsed + additionalEffort >
                    capacity.effort + epsilon ||
                result.budgetUsed + additionalBudget >
                    capacity.budget + epsilon
            ) {
                return false;
            }

            result.selected.insert(closure.begin(), closure.end());

            result.effortUsed += additionalEffort;
            result.budgetUsed += additionalBudget;

            return true;
        };

        // Mandatory initiatives cannot be silently discarded.
        for (const auto& [id, scoreValue] : order) {
            if (!initiatives.at(id).mandatory) {
                continue;
            }

            if (!include(id)) {
                throw std::runtime_error(
                    "Mandatory initiative " + id +
                    " exceeds available portfolio capacity."
                );
            }
        }

        // Evaluate optional initiatives using deterministic ranking.
        for (const auto& [id, scoreValue] : order) {
            if (result.selected.count(id)) {
                continue;
            }

            if (!include(id)) {
                result.deferred.insert(id);
            }
        }

        // Dependencies included with another initiative are also selected.
        for (const auto& [id, item] : initiatives) {
            if (!result.selected.count(id)) {
                result.deferred.insert(id);
            }
        }

        for (const auto& id : result.selected) {
            result.businessValue +=
                initiatives.at(id).businessValue;
        }

        for (const auto& id : result.deferred) {
            result.opportunityCost += scores.at(id);
        }

        for (const auto& [id, item] : initiatives) {
            Decision decision;

            decision.initiativeId = id;
            decision.score = scores.at(id);

            if (result.selected.count(id)) {
                decision.status = DecisionStatus::SELECTED;
                decision.reason = "Fits portfolio resource constraints.";
            } else {
                decision.status = DecisionStatus::DEFERRED;
                decision.reason =
                    "Excluded due to resource limits or lower ranking.";
            }

            result.decisions.push_back(decision);
        }

        return result;
    }

    void printRanking(Framework framework) const {
        std::cout << "\nRANKING\n";

        for (const auto& [id, value] : ranked(framework)) {
            std::cout << std::left
                      << std::setw(8) << id
                      << std::setw(35) << initiatives.at(id).name
                      << std::fixed << std::setprecision(2)
                      << value << '\n';
        }
    }
};


std::vector<Initiative> samplePortfolio() {
    return {
        {
            "I001", "Security compliance",
            100, 10, 0.99, 8,
            10, 10, 10, 10,
            12000, true, Priority::CRITICAL, {}
        },
        {
            "I002", "Customer analytics",
            8000, 8, 0.85, 13,
            9, 7, 4, 9,
            18000, false, Priority::HIGH, {"I001"}
        },
        {
            "I003", "Infrastructure optimization",
            5000, 7, 0.95, 5,
            8, 8, 6, 8,
            7000, false, Priority::HIGH, {}
        },
        {
            "I004", "Internal dashboard",
            2000, 5, 0.90, 4,
            5, 3, 2, 6,
            4000, false, Priority::MEDIUM, {}
        },
        {
            "I005", "Disaster recovery",
            1000, 9, 0.90, 7,
            9, 9, 10, 9,
            10000, false, Priority::HIGH, {}
        },
        {
            "I006", "Mobile redesign",
            6000, 6, 0.75, 10,
            7, 5, 3, 8,
            14000, false, Priority::LOW, {}
        }
    };
}


void runTests() {
    Initiative invalid{
        "BAD", "Invalid",
        1, 1, 1, 0,
        1, 1, 1, 1,
        1, false, Priority::LOW, {}
    };

    bool caught = false;

    try {
        PrioritizationEngine engine({invalid});
    } catch (const std::invalid_argument&) {
        caught = true;
    }

    if (!caught) {
        throw std::runtime_error(
            "Invalid effort validation test failed."
        );
    }

    caught = false;

    Initiative a{
        "A", "A",
        1, 1, 1, 1,
        1, 1, 1, 1,
        1, false, Priority::LOW, {"B"}
    };

    Initiative b{
        "B", "B",
        1, 1, 1, 1,
        1, 1, 1, 1,
        1, false, Priority::LOW, {"A"}
    };

    try {
        PrioritizationEngine engine({a, b});
    } catch (const std::invalid_argument&) {
        caught = true;
    }

    if (!caught) {
        throw std::runtime_error(
            "Circular dependency validation test failed."
        );
    }

    std::cout << "\nValidation tests passed.\n";
}


int main() {
    try {
        PrioritizationEngine engine(samplePortfolio());

        Capacity capacity{
            35.0,
            45000.0
        };

        std::cout << "PRIORITIZATION FUNDAMENTALS\n";
        std::cout << "===========================\n";

        engine.printRanking(Framework::RICE);
        engine.printRanking(Framework::WSJF);
        engine.printRanking(Framework::WEIGHTED);

        AllocationResult result = engine.allocate(
            capacity,
            Framework::WEIGHTED
        );

        std::cout << "\nPORTFOLIO ALLOCATION\n";

        std::cout << std::fixed << std::setprecision(2);

        std::cout << "Selected: ";

        for (const auto& id : result.selected) {
            std::cout << id << ' ';
        }

        std::cout << "\nDeferred: ";

        for (const auto& id : result.deferred) {
            std::cout << id << ' ';
        }

        std::cout << "\nEffort used: "
                  << result.effortUsed;

        std::cout << "\nBudget used: "
                  << result.budgetUsed;

        std::cout << "\nBusiness value: "
                  << result.businessValue;

        std::cout << "\nOpportunity cost: "
                  << result.opportunityCost;

        std::cout << "\nRemaining effort: "
                  << capacity.effort - result.effortUsed;

        std::cout << "\nRemaining budget: "
                  << capacity.budget - result.budgetUsed
                  << '\n';

        runTests();

    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
