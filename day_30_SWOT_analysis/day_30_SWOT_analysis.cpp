/*
    SWOT Analysis: Strategic Decision Support Engine

    C++17 case study:
    A manufacturing software company is evaluating a market expansion.
    The program models:

    - internal strengths and weaknesses
    - external opportunities and threats
    - evidence confidence
    - weighted strategic impact
    - SO/WO/ST/WT interactions
    - scenario sensitivity
    - validation
    - merge-like decision gating for a strategy proposal
    - deterministic reporting

    The program is intentionally designed as a coherent decision-support
    engine rather than as isolated C++ language demonstrations.

    Compile:
        g++ -std=c++17 -Wall -Wextra -pedantic swot_engine.cpp -o swot_engine
*/

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class Category {
    Strength,
    Weakness,
    Opportunity,
    Threat
};

std::string categoryName(Category category) {
    switch (category) {
        case Category::Strength:
            return "Strength";
        case Category::Weakness:
            return "Weakness";
        case Category::Opportunity:
            return "Opportunity";
        case Category::Threat:
            return "Threat";
    }

    throw std::logic_error("Unknown SWOT category.");
}

bool isPositive(Category category) {
    return category == Category::Strength ||
           category == Category::Opportunity;
}

struct Factor {
    std::string id;
    Category category;
    std::string title;
    std::string description;

    double importance;
    double impact;
    double confidence;

    std::vector<std::string> evidence;

    double weightedImpact() const {
        return importance * impact * confidence;
    }

    double signedScore() const {
        return isPositive(category)
            ? weightedImpact()
            : -weightedImpact();
    }
};

struct Scenario {
    std::string name;
    double opportunityMultiplier;
    double threatMultiplier;
    std::string description;
};

struct StrategicAction {
    std::string code;
    std::string title;
    std::string rationale;
    std::vector<std::string> factorIds;
    double priority;
};

class SwotEngine {
private:
    std::string name_;
    std::string objective_;
    std::vector<Factor> factors_;

    static void validateScore(double value, const std::string& field) {
        if (!std::isfinite(value) || value < 0.0 || value > 1.0) {
            throw std::invalid_argument(
                field + " must be between 0 and 1."
            );
        }
    }

public:
    SwotEngine(std::string name, std::string objective)
        : name_(std::move(name)),
          objective_(std::move(objective)) {}

    void addFactor(Factor factor) {
        validateScore(factor.importance, "importance");
        validateScore(factor.impact, "impact");
        validateScore(factor.confidence, "confidence");

        if (factor.id.empty() || factor.title.empty()) {
            throw std::invalid_argument(
                "Every SWOT factor requires an ID and title."
            );
        }

        const auto duplicate = std::find_if(
            factors_.begin(),
            factors_.end(),
            [&](const Factor& existing) {
                return existing.id == factor.id;
            }
        );

        if (duplicate != factors_.end()) {
            throw std::invalid_argument(
                "Duplicate SWOT factor ID: " + factor.id
            );
        }

        factors_.push_back(std::move(factor));
    }

    const std::vector<Factor>& factors() const {
        return factors_;
    }

    std::vector<const Factor*> factorsByCategory(Category category) const {
        std::vector<const Factor*> result;

        for (const auto& factor : factors_) {
            if (factor.category == category) {
                result.push_back(&factor);
            }
        }

        return result;
    }

    double categoryScore(Category category) const {
        const auto selected = factorsByCategory(category);

        return std::accumulate(
            selected.begin(),
            selected.end(),
            0.0,
            [](double total, const Factor* factor) {
                return total + factor->signedScore();
            }
        );
    }

    double totalScore() const {
        return std::accumulate(
            factors_.begin(),
            factors_.end(),
            0.0,
            [](double total, const Factor& factor) {
                return total + factor.signedScore();
            }
        );
    }

    std::vector<std::string> validate() const {
        std::vector<std::string> warnings;

        for (Category category : {
            Category::Strength,
            Category::Weakness,
            Category::Opportunity,
            Category::Threat
        }) {
            if (factorsByCategory(category).empty()) {
                warnings.push_back(
                    "No factors exist for " + categoryName(category) + "."
                );
            }
        }

        for (const auto& factor : factors_) {
            if (factor.evidence.empty()) {
                warnings.push_back(
                    factor.id + " has no evidence recorded."
                );
            }
        }

        return warnings;
    }

    const Factor& strongest(Category category) const {
        const auto selected = factorsByCategory(category);

        if (selected.empty()) {
            throw std::runtime_error(
                "Cannot identify strongest factor in an empty category."
            );
        }

        return **std::max_element(
            selected.begin(),
            selected.end(),
            [](const Factor* left, const Factor* right) {
                return left->weightedImpact() <
                       right->weightedImpact();
            }
        );
    }

    double scenarioScore(const Scenario& scenario) const {
        if (scenario.opportunityMultiplier < 0.0 ||
            scenario.threatMultiplier < 0.0) {
            throw std::invalid_argument(
                "Scenario multipliers cannot be negative."
            );
        }

        double score = 0.0;

        for (const auto& factor : factors_) {
            if (factor.category == Category::Opportunity) {
                score +=
                    factor.weightedImpact() *
                    scenario.opportunityMultiplier;
            } else if (factor.category == Category::Threat) {
                score -=
                    factor.weightedImpact() *
                    scenario.threatMultiplier;
            } else {
                score += factor.signedScore();
            }
        }

        return score;
    }

    StrategicAction createSOAction() const {
        const auto& strength = strongest(Category::Strength);
        const auto& opportunity = strongest(Category::Opportunity);

        return {
            "SO",
            "Apply core capability to the strongest market opportunity",
            strength.id + " provides the internal capability while " +
                opportunity.id +
                " identifies an external demand condition. The strategy " +
                "should connect the capability directly to that demand.",
            {strength.id, opportunity.id},
            strength.weightedImpact() *
                opportunity.weightedImpact()
        };
    }

    StrategicAction createWOAction() const {
        const auto& weakness = strongest(Category::Weakness);
        const auto& opportunity = strongest(Category::Opportunity);

        return {
            "WO",
            "Use market access opportunities to reduce capability constraints",
            weakness.id + " limits expansion while " +
                opportunity.id +
                " creates a condition that may justify investment in " +
                "distribution, staffing, or operational capability.",
            {weakness.id, opportunity.id},
            weakness.weightedImpact() *
                opportunity.weightedImpact()
        };
    }

    StrategicAction createSTAction() const {
        const auto& strength = strongest(Category::Strength);
        const auto& threat = strongest(Category::Threat);

        return {
            "ST",
            "Use differentiation to reduce competitive exposure",
            strength.id + " can be positioned against " +
                threat.id +
                " by emphasizing capabilities that are difficult to " +
                "replace with generic bundled functionality.",
            {strength.id, threat.id},
            strength.weightedImpact() *
                threat.weightedImpact()
        };
    }

    StrategicAction createWTAction() const {
        const auto& weakness = strongest(Category::Weakness);
        const auto& threat = strongest(Category::Threat);

        return {
            "WT",
            "Contain combined internal and external exposure",
            weakness.id + " and " +
                threat.id +
                " create a compound risk. The strategic response should " +
                "reduce exposure before aggressive expansion.",
            {weakness.id, threat.id},
            weakness.weightedImpact() *
                threat.weightedImpact()
        };
    }
};

class StrategyGate {
private:
    double minimumEvidenceConfidence_;

public:
    explicit StrategyGate(double minimumEvidenceConfidence)
        : minimumEvidenceConfidence_(minimumEvidenceConfidence) {
        if (minimumEvidenceConfidence < 0.0 ||
            minimumEvidenceConfidence > 1.0) {
            throw std::invalid_argument(
                "Strategy gate threshold must be between 0 and 1."
            );
        }
    }

    bool canAdvance(const SwotEngine& engine) const {
        const auto warnings = engine.validate();

        if (!warnings.empty()) {
            return false;
        }

        for (const auto& factor : engine.factors()) {
            if (factor.confidence < minimumEvidenceConfidence_) {
                return false;
            }
        }

        return true;
    }
};

void printFactor(const Factor& factor) {
    std::cout
        << std::left
        << std::setw(5) << factor.id
        << std::setw(14) << categoryName(factor.category)
        << std::setw(38) << factor.title
        << " weighted=" << std::fixed << std::setprecision(3)
        << factor.weightedImpact()
        << '\n';

    std::cout << "      " << factor.description << '\n';

    if (!factor.evidence.empty()) {
        std::cout << "      Evidence: ";

        for (std::size_t index = 0;
             index < factor.evidence.size();
             ++index) {
            if (index > 0) {
                std::cout << "; ";
            }

            std::cout << factor.evidence[index];
        }

        std::cout << '\n';
    }
}

void printActions(const std::vector<StrategicAction>& actions) {
    std::cout << "\nSTRATEGIC IMPLICATIONS\n";

    for (const auto& action : actions) {
        std::cout << action.code
                  << " | "
                  << action.title
                  << " | priority="
                  << std::fixed
                  << std::setprecision(3)
                  << action.priority
                  << '\n';

        std::cout << "  " << action.rationale << '\n';

        std::cout << "  Factors: ";

        for (std::size_t index = 0;
             index < action.factorIds.size();
             ++index) {
            if (index > 0) {
                std::cout << ", ";
            }

            std::cout << action.factorIds[index];
        }

        std::cout << '\n';
    }
}

void printScenarioAnalysis(
    const SwotEngine& engine,
    const std::vector<Scenario>& scenarios
) {
    std::cout << "\nSCENARIO SENSITIVITY\n";

    for (const auto& scenario : scenarios) {
        const double score = engine.scenarioScore(scenario);

        std::cout
            << std::left
            << std::setw(30)
            << scenario.name
            << " score="
            << std::fixed
            << std::setprecision(3)
            << score
            << '\n';

        std::cout << "  " << scenario.description << '\n';
    }
}

SwotEngine createCaseStudy() {
    SwotEngine engine(
        "ProcureSight Manufacturing Expansion",
        "Evaluate expansion of procurement analytics into mid-market manufacturing."
    );

    engine.addFactor({
        "S1",
        Category::Strength,
        "Procurement analytics depth",
        "The platform detects supplier concentration, anomalous purchases, "
        "and spend leakage.",
        0.92,
        0.86,
        0.90,
        {"Validated customer analyses", "Repeatable analytical workflows"}
    });

    engine.addFactor({
        "S2",
        Category::Strength,
        "Reusable data connectors",
        "Standardized connectors reduce repeated integration work during "
        "customer onboarding.",
        0.82,
        0.78,
        0.87,
        {"Connector library", "Implementation records"}
    });

    engine.addFactor({
        "S3",
        Category::Strength,
        "Procurement domain expertise",
        "The product team understands sourcing, supplier management, "
        "category structures, and procurement KPIs.",
        0.76,
        0.81,
        0.91,
        {"Subject-matter expertise"}
    });

    engine.addFactor({
        "W1",
        Category::Weakness,
        "Limited market recognition",
        "The company is less familiar to manufacturing procurement leaders "
        "than large enterprise software providers.",
        0.86,
        0.76,
        0.89,
        {"Customer discovery interviews"}
    });

    engine.addFactor({
        "W2",
        Category::Weakness,
        "Implementation capacity",
        "The current onboarding team may not support rapid customer growth "
        "without operational expansion.",
        0.84,
        0.83,
        0.90,
        {"Staffing capacity analysis"}
    });

    engine.addFactor({
        "W3",
        Category::Weakness,
        "Limited regional coverage",
        "Localization and regional support are less mature outside the "
        "initial market.",
        0.63,
        0.64,
        0.79,
        {"Current deployment footprint"}
    });

    engine.addFactor({
        "O1",
        Category::Opportunity,
        "Procurement visibility demand",
        "Manufacturers are seeking stronger visibility into supplier costs "
        "and purchasing patterns.",
        0.91,
        0.85,
        0.76,
        {"Customer discovery interviews", "Pipeline observations"}
    });

    engine.addFactor({
        "O2",
        Category::Opportunity,
        "Cloud procurement adoption",
        "Cloud-based procurement systems create standardized data sources "
        "for analytical products.",
        0.81,
        0.79,
        0.75,
        {"Technology adoption assessments"}
    });

    engine.addFactor({
        "O3",
        Category::Opportunity,
        "Consulting partner distribution",
        "Procurement and ERP consulting firms could distribute the product "
        "while supporting implementation.",
        0.77,
        0.76,
        0.71,
        {"Partner discussions"}
    });

    engine.addFactor({
        "T1",
        Category::Threat,
        "Bundled competitor analytics",
        "Large enterprise vendors can include procurement analytics in "
        "broader software agreements.",
        0.92,
        0.87,
        0.86,
        {"Competitive product monitoring"}
    });

    engine.addFactor({
        "T2",
        Category::Threat,
        "Long buying cycles",
        "Manufacturing organizations may require procurement, finance, IT, "
        "security, and executive approvals.",
        0.81,
        0.77,
        0.87,
        {"Observed sales-cycle data"}
    });

    engine.addFactor({
        "T3",
        Category::Threat,
        "Customer data quality variation",
        "Supplier, invoice, purchase-order, and category data can vary "
        "substantially across customers.",
        0.86,
        0.82,
        0.91,
        {"Historical integration incidents"}
    });

    return engine;
}

int main() {
    try {
        SwotEngine engine = createCaseStudy();

        std::cout << "SWOT STRATEGIC DECISION SUPPORT ENGINE\n";
        std::cout << "=====================================\n\n";

        std::cout << "Objective:\n";
        std::cout
            << "Evaluate expansion of procurement analytics into "
               "mid-market manufacturing.\n\n";

        std::cout << "SWOT FACTORS\n";

        for (Category category : {
            Category::Strength,
            Category::Weakness,
            Category::Opportunity,
            Category::Threat
        }) {
            std::cout << "\n[" << categoryName(category) << "]\n";

            for (const Factor* factor :
                 engine.factorsByCategory(category)) {
                printFactor(*factor);
            }
        }

        std::cout << "\nCATEGORY SCORES\n";

        for (Category category : {
            Category::Strength,
            Category::Weakness,
            Category::Opportunity,
            Category::Threat
        }) {
            std::cout
                << std::left
                << std::setw(16)
                << categoryName(category)
                << std::fixed
                << std::setprecision(3)
                << engine.categoryScore(category)
                << '\n';
        }

        std::cout << "\nNET SWOT SCORE: "
                  << std::fixed
                  << std::setprecision(3)
                  << engine.totalScore()
                  << '\n';

        std::cout << "\nVALIDATION\n";

        const auto warnings = engine.validate();

        if (warnings.empty()) {
            std::cout << "No structural validation warnings.\n";
        } else {
            for (const auto& warning : warnings) {
                std::cout << "Warning: " << warning << '\n';
            }
        }

        const std::vector<StrategicAction> actions = {
            engine.createSOAction(),
            engine.createWOAction(),
            engine.createSTAction(),
            engine.createWTAction()
        };

        printActions(actions);

        const std::vector<Scenario> scenarios = {
            {
                "Base environment",
                1.00,
                1.00,
                "Current external assumptions."
            },
            {
                "Demand acceleration",
                1.25,
                1.00,
                "Market demand develops more strongly than expected."
            },
            {
                "Competitive pressure",
                0.90,
                1.30,
                "Large vendors increase bundled competition."
            },
            {
                "Integration difficulty",
                0.95,
                1.20,
                "Customer data complexity increases delivery risk."
            }
        };

        printScenarioAnalysis(engine, scenarios);

        std::cout << "\nSTRATEGY GATE\n";

        /*
            The gate illustrates an important distinction between an analytical
            framework and an operational decision. A strategy should not be
            advanced merely because its SWOT score is positive. Evidence
            quality and structural completeness are explicit conditions.
        */
        StrategyGate gate(0.70);

        if (gate.canAdvance(engine)) {
            std::cout
                << "The analysis satisfies the configured evidence and "
                   "completeness gate.\n";
        } else {
            std::cout
                << "The analysis does not satisfy the configured evidence "
                   "and completeness gate.\n";
        }

        std::cout << "\nEDGE-CASE VALIDATION\n";

        try {
            engine.addFactor({
                "INVALID",
                Category::Strength,
                "Invalid importance",
                "This factor intentionally violates the score range.",
                1.5,
                0.8,
                0.8,
                {"Example evidence"}
            });
        } catch (const std::exception& error) {
            std::cout
                << "Invalid factor rejected: "
                << error.what()
                << '\n';
        }

        try {
            Scenario invalidScenario{
                "Invalid scenario",
                -0.5,
                1.0,
                "This scenario has an invalid multiplier."
            };

            std::cout
                << "Invalid scenario score: "
                << engine.scenarioScore(invalidScenario)
                << '\n';
        } catch (const std::exception& error) {
            std::cout
                << "Invalid scenario rejected: "
                << error.what()
                << '\n';
        }

        std::cout << "\nDECISION-SUPPORT PRINCIPLE\n";
        std::cout
            << "The SWOT model structures evidence and strategic reasoning. "
               "Its numerical score is an analytical aid, not a proof of "
               "strategy quality or future performance.\n";

        std::cout
            << "External scenarios are separated from internal capabilities "
               "so that changing market assumptions does not silently change "
               "the underlying organizational facts.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal SWOT engine error: "
            << error.what()
            << '\n';

        return 1;
    }
}
