#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

/*
 * Advanced Prioritization and Portfolio Governance Engine
 *
 * C++17 engineering perspective:
 * - Explicit domain modeling
 * - Deterministic scoring
 * - Dependency graph validation
 * - Economic opportunity evaluation
 * - Strategic fit assessment
 * - Risk-adjusted prioritization
 * - Budget-constrained portfolio optimization
 * - Branch-and-bound-style exhaustive portfolio search
 *   implemented as dynamic programming over a bounded budget.
 *
 * No external libraries.
 */

enum class PriorityTier {
    Critical,
    High,
    Medium,
    Low
};

enum class DecisionStatus {
    Proposed,
    Evaluated,
    Selected,
    Deferred
};

struct Opportunity {
    std::string id;
    std::string name;

    double strategicFit{};
    double expectedBenefit{};
    double implementationCost{};

    double customerValue{};
    double urgency{};
    double feasibility{};
    double risk{};
    double confidence{};

    double costOfDelay{};
    double effort{};

    std::vector<std::string> dependencies;

    bool mandatory{false};

    DecisionStatus status{DecisionStatus::Proposed};
};

struct Weights {
    double strategicFit{0.25};
    double economicValue{0.25};
    double customerValue{0.15};
    double urgency{0.15};
    double feasibility{0.10};
    double riskAdjustment{0.10};

    void validate() const {
        const double values[] = {
            strategicFit,
            economicValue,
            customerValue,
            urgency,
            feasibility,
            riskAdjustment
        };

        double total = 0.0;

        for (double value : values) {
            if (!std::isfinite(value) || value < 0.0) {
                throw std::invalid_argument(
                    "Weights must be finite and non-negative."
                );
            }

            total += value;
        }

        if (std::abs(total - 1.0) > 1e-9) {
            throw std::invalid_argument(
                "Weights must sum to 1."
            );
        }
    }
};

struct Score {
    std::string id;
    std::string name;

    double weighted{};
    double adjusted{};
    double netValue{};
    double roi{};
    double wsjf{};

    PriorityTier tier{PriorityTier::Low};
    int rank{};
};

struct PortfolioResult {
    double budget{};
    double allocated{};
    double expectedBenefit{};
    double netValue{};

    std::vector<std::string> selected;
};

class PrioritizationEngine {
private:
    std::map<std::string, Opportunity> opportunities;
    std::map<std::string, Score> scores;
    Weights weights;

    static bool validRange(double value) {
        return std::isfinite(value) &&
               value >= 0.0 &&
               value <= 100.0;
    }

    static PriorityTier classify(double score) {
        if (score >= 85.0) return PriorityTier::Critical;
        if (score >= 70.0) return PriorityTier::High;
        if (score >= 50.0) return PriorityTier::Medium;
        return PriorityTier::Low;
    }

    static std::string tierName(PriorityTier tier) {
        switch (tier) {
            case PriorityTier::Critical: return "CRITICAL";
            case PriorityTier::High: return "HIGH";
            case PriorityTier::Medium: return "MEDIUM";
            case PriorityTier::Low: return "LOW";
        }

        return "UNKNOWN";
    }

    void validateOpportunity(const Opportunity& o) const {
        if (o.id.empty() || o.name.empty()) {
            throw std::invalid_argument(
                "Opportunity ID and name are required."
            );
        }

        const double bounded[] = {
            o.strategicFit,
            o.customerValue,
            o.urgency,
            o.feasibility,
            o.risk,
            o.confidence
        };

        for (double value : bounded) {
            if (!validRange(value)) {
                throw std::invalid_argument(
                    "Bounded scores must be between 0 and 100."
                );
            }
        }

        const double nonNegative[] = {
            o.expectedBenefit,
            o.implementationCost,
            o.costOfDelay,
            o.effort
        };

        for (double value : nonNegative) {
            if (!std::isfinite(value) || value < 0.0) {
                throw std::invalid_argument(
                    "Economic inputs must be non-negative."
                );
            }
        }

        if (o.implementationCost <= 0.0 || o.effort <= 0.0) {
            throw std::invalid_argument(
                "Cost and effort must be positive."
            );
        }

        std::set<std::string> unique(
            o.dependencies.begin(),
            o.dependencies.end()
        );

        if (unique.size() != o.dependencies.size()) {
            throw std::invalid_argument(
                "Duplicate dependencies are prohibited."
            );
        }

        if (unique.count(o.id)) {
            throw std::invalid_argument(
                "Self-dependency is prohibited."
            );
        }
    }

    void visit(
        const std::string& id,
        std::unordered_set<std::string>& visiting,
        std::unordered_set<std::string>& visited
    ) const {
        if (visiting.count(id)) {
            throw std::runtime_error(
                "Circular dependency detected."
            );
        }

        if (visited.count(id)) return;

        auto iterator = opportunities.find(id);

        if (iterator == opportunities.end()) {
            throw std::runtime_error(
                "Unknown dependency: " + id
            );
        }

        visiting.insert(id);

        for (const auto& dependency :
             iterator->second.dependencies) {
            visit(dependency, visiting, visited);
        }

        visiting.erase(id);
        visited.insert(id);
    }

    std::set<std::string> dependencyClosure(
        const std::string& id
    ) const {
        std::set<std::string> result;

        auto add = [&](auto&& self, const std::string& current)
            -> void {
            if (result.count(current)) return;

            result.insert(current);

            for (const auto& dependency :
                 opportunities.at(current).dependencies) {
                self(self, dependency);
            }
        };

        add(add, id);
        return result;
    }

public:
    explicit PrioritizationEngine(Weights configuredWeights = {})
        : weights(configuredWeights) {
        weights.validate();
    }

    void addOpportunity(const Opportunity& opportunity) {
        validateOpportunity(opportunity);

        if (opportunities.count(opportunity.id)) {
            throw std::invalid_argument(
                "Duplicate opportunity ID."
            );
        }

        opportunities.emplace(
            opportunity.id,
            opportunity
        );
    }

    void validateDependencies() const {
        std::unordered_set<std::string> visiting;
        std::unordered_set<std::string> visited;

        for (const auto& [id, opportunity] : opportunities) {
            visit(id, visiting, visited);
        }
    }

    Score evaluate(const Opportunity& o) const {
        const double expected =
            o.expectedBenefit * o.confidence / 100.0;

        const double net =
            expected - o.implementationCost;

        const double roi =
            net / o.implementationCost * 100.0;

        const double economic = std::clamp(
            50.0 + 50.0 * (
                net / o.implementationCost
            ),
            0.0,
            100.0
        );

        const double weighted =
            o.strategicFit * weights.strategicFit +
            economic * weights.economicValue +
            o.customerValue * weights.customerValue +
            o.urgency * weights.urgency +
            o.feasibility * weights.feasibility +
            (100.0 - o.risk) * weights.riskAdjustment;

        const double adjusted =
            weighted * o.confidence / 100.0;

        return Score{
            o.id,
            o.name,
            weighted,
            adjusted,
            net,
            roi,
            o.costOfDelay / o.effort,
            classify(adjusted),
            0
        };
    }

    std::vector<Score> rank() {
        validateDependencies();

        std::vector<Score> result;
        result.reserve(opportunities.size());

        for (const auto& [id, opportunity] : opportunities) {
            result.push_back(evaluate(opportunity));
        }

        std::sort(
            result.begin(),
            result.end(),
            [](const Score& a, const Score& b) {
                if (a.adjusted != b.adjusted) {
                    return a.adjusted > b.adjusted;
                }

                if (a.wsjf != b.wsjf) {
                    return a.wsjf > b.wsjf;
                }

                return a.id < b.id;
            }
        );

        scores.clear();

        for (std::size_t i = 0; i < result.size(); ++i) {
            result[i].rank = static_cast<int>(i + 1);
            scores[result[i].id] = result[i];
        }

        return result;
    }

    PortfolioResult optimizePortfolio(double budget) {
        if (!std::isfinite(budget) || budget < 0.0) {
            throw std::invalid_argument("Invalid budget.");
        }

        validateDependencies();
        rank();

        /*
         * Dynamic programming state:
         * dp[cost] stores the best benefit for that exact cost.
         *
         * Each opportunity is treated as a bundle containing
         * its not-yet-selected dependency closure.
         *
         * A bitmask records the selected opportunity set.
         *
         * Exact optimization is restricted to 22 opportunities
         * to bound memory and execution time.
         */

        if (opportunities.size() > 22) {
            throw std::runtime_error(
                "Exact portfolio optimization supports "
                "at most 22 opportunities."
            );
        }

        const int n = static_cast<int>(opportunities.size());

        std::vector<std::string> ids;
        std::unordered_map<std::string, int> index;

        for (const auto& [id, opportunity] : opportunities) {
            index[id] = static_cast<int>(ids.size());
            ids.push_back(id);
        }

        const long long states = 1LL << n;

        std::vector<double> costs(states, 0.0);
        std::vector<double> benefits(states, 0.0);

        std::vector<bool> valid(states, false);

        valid[0] = true;

        const double epsilon = 1e-9;

        for (long long mask = 0; mask < states; ++mask) {
            if (!valid[mask]) continue;

            std::set<std::string> selected;

            for (int i = 0; i < n; ++i) {
                if (mask & (1LL << i)) {
                    selected.insert(ids[i]);
                }
            }

            for (int i = 0; i < n; ++i) {
                if (mask & (1LL << i)) continue;

                const auto& opportunity =
                    opportunities.at(ids[i]);

                auto required = dependencyClosure(ids[i]);

                std::set<std::string> missing;

                std::set_difference(
                    required.begin(),
                    required.end(),
                    selected.begin(),
                    selected.end(),
                    std::inserter(
                        missing,
                        missing.begin()
                    )
                );

                long long nextMask = mask;
                double additionalCost = 0.0;
                double additionalBenefit = 0.0;

                for (const auto& item : missing) {
                    const int position = index.at(item);
                    nextMask |= (1LL << position);

                    const auto& dependency =
                        opportunities.at(item);

                    additionalCost +=
                        dependency.implementationCost;

                    additionalBenefit +=
                        dependency.expectedBenefit *
                        dependency.confidence / 100.0;
                }

                const double nextCost =
                    costs[mask] + additionalCost;

                if (nextCost > budget + epsilon) {
                    continue;
                }

                const double nextBenefit =
                    benefits[mask] + additionalBenefit;

                if (
                    !valid[nextMask] ||
                    nextBenefit > benefits[nextMask]
                ) {
                    valid[nextMask] = true;
                    costs[nextMask] = nextCost;
                    benefits[nextMask] = nextBenefit;
                }

                (void)opportunity;
            }
        }

        long long bestMask = 0;
        double bestUtility =
            -std::numeric_limits<double>::infinity();

        for (long long mask = 0; mask < states; ++mask) {
            if (!valid[mask]) continue;

            bool mandatorySatisfied = true;

            for (int i = 0; i < n; ++i) {
                if (
                    opportunities.at(ids[i]).mandatory &&
                    !(mask & (1LL << i))
                ) {
                    mandatorySatisfied = false;
                    break;
                }
            }

            if (!mandatorySatisfied) continue;

            const double utility = benefits[mask];

            if (utility > bestUtility) {
                bestUtility = utility;
                bestMask = mask;
            }
        }

        if (!std::isfinite(bestUtility)) {
            throw std::runtime_error(
                "No feasible portfolio satisfies mandatory items."
            );
        }

        PortfolioResult result;
        result.budget = budget;
        result.allocated = costs[bestMask];
        result.expectedBenefit = benefits[bestMask];
        result.netValue =
            result.expectedBenefit - result.allocated;

        for (int i = 0; i < n; ++i) {
            if (bestMask & (1LL << i)) {
                result.selected.push_back(ids[i]);
            }
        }

        return result;
    }

    std::vector<std::string> paretoFrontier() const {
        std::vector<std::string> result;

        for (const auto& [id, candidate] : opportunities) {
            bool dominated = false;

            for (const auto& [otherId, other] : opportunities) {
                if (id == otherId) continue;

                const bool atLeastEqual =
                    other.expectedBenefit >=
                        candidate.expectedBenefit &&
                    other.strategicFit >=
                        candidate.strategicFit &&
                    other.feasibility >=
                        candidate.feasibility;

                const bool strictlyBetter =
                    other.expectedBenefit >
                        candidate.expectedBenefit ||
                    other.strategicFit >
                        candidate.strategicFit ||
                    other.feasibility >
                        candidate.feasibility;

                if (atLeastEqual && strictlyBetter) {
                    dominated = true;
                    break;
                }
            }

            if (!dominated) result.push_back(id);
        }

        return result;
    }

    void printRanking(const std::vector<Score>& ranking) const {
        std::cout << "\nOPPORTUNITY PRIORITIZATION\n";

        std::cout << std::left
                  << std::setw(7) << "Rank"
                  << std::setw(12) << "ID"
                  << std::setw(35) << "Opportunity"
                  << std::right
                  << std::setw(12) << "Weighted"
                  << std::setw(12) << "Adjusted"
                  << std::setw(12) << "ROI %"
                  << std::setw(12) << "WSJF"
                  << std::setw(12) << "Tier"
                  << '\n';

        for (const auto& item : ranking) {
            std::cout << std::left
                      << std::setw(7) << item.rank
                      << std::setw(12) << item.id
                      << std::setw(35)
                      << item.name.substr(0, 33)
                      << std::right
                      << std::fixed
                      << std::setprecision(2)
                      << std::setw(12) << item.weighted
                      << std::setw(12) << item.adjusted
                      << std::setw(12) << item.roi
                      << std::setw(12) << item.wsjf
                      << std::setw(12)
                      << tierName(item.tier)
                      << '\n';
        }
    }
};

Opportunity makeOpportunity(
    std::string id,
    std::string name,
    double strategic,
    double benefit,
    double cost,
    double customer,
    double urgency,
    double feasibility,
    double risk,
    double confidence,
    double delay,
    double effort,
    std::vector<std::string> dependencies = {},
    bool mandatory = false
) {
    return Opportunity{
        std::move(id),
        std::move(name),
        strategic,
        benefit,
        cost,
        customer,
        urgency,
        feasibility,
        risk,
        confidence,
        delay,
        effort,
        std::move(dependencies),
        mandatory
    };
}

int main() {
    try {
        PrioritizationEngine engine;

        engine.addOpportunity(makeOpportunity(
            "OP-001",
            "Customer Analytics Platform",
            95, 900000, 250000,
            90, 85, 80, 25, 85,
            120000, 12
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-002",
            "Cloud Cost Optimization",
            85, 600000, 150000,
            65, 75, 90, 15, 90,
            85000, 8
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-003",
            "Security Monitoring Modernization",
            100, 750000, 300000,
            80, 95, 75, 20, 90,
            180000, 15,
            {},
            true
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-004",
            "Mobile Experience Improvement",
            75, 450000, 120000,
            95, 70, 85, 15, 80,
            70000, 7,
            {"OP-001"}
        ));

        engine.addOpportunity(makeOpportunity(
            "OP-005",
            "Reporting Automation",
            60, 180000, 80000,
            50, 45, 95, 10, 95,
            20000, 5
        ));

        const auto ranking = engine.rank();

        engine.printRanking(ranking);

        std::cout << "\nPARETO FRONTIER\n";

        for (const auto& id : engine.paretoFrontier()) {
            std::cout << id << '\n';
        }

        const double budget = 700000;

        const auto portfolio =
            engine.optimizePortfolio(budget);

        std::cout << "\nOPTIMIZED PORTFOLIO\n";

        std::cout << "Budget: "
                  << portfolio.budget << '\n';

        std::cout << "Allocated: "
                  << portfolio.allocated << '\n';

        std::cout << "Expected benefit: "
                  << portfolio.expectedBenefit << '\n';

        std::cout << "Net value: "
                  << portfolio.netValue << '\n';

        std::cout << "Selected opportunities:\n";

        for (const auto& id : portfolio.selected) {
            std::cout << "  " << id << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Prioritization error: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
