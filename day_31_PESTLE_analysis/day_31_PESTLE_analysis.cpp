/*
    PESTLE Governance and Decision-Assessment Engine
    =================================================

    C++17 case study:
    An enterprise technology company is evaluating market expansion while
    maintaining a structured PESTLE governance process.

    The program demonstrates a realistic assessment engine that:
    - stores distinct Political, Economic, Social, Technological, Legal,
      and Environmental factors
    - validates assessment records
    - calculates likelihood-impact exposure
    - adjusts scores for evidence confidence
    - evaluates category-specific governance rules
    - detects material legal exposure
    - evaluates scenario sensitivity
    - produces a management decision packet
    - keeps PESTLE categories separate rather than treating them as one
      undifferentiated risk list

    Build:
        g++ -std=c++17 -O2 -Wall -Wextra -pedantic pestle_governance.cpp -o pestle_governance

    Run:
        ./pestle_governance
*/

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

enum class Category {
    Political,
    Economic,
    Social,
    Technological,
    Legal,
    Environmental
};

enum class Direction {
    Opportunity,
    Threat
};

enum class Horizon {
    Short,
    Medium,
    Long
};

std::string toString(Category category) {
    switch (category) {
        case Category::Political:
            return "Political";
        case Category::Economic:
            return "Economic";
        case Category::Social:
            return "Social";
        case Category::Technological:
            return "Technological";
        case Category::Legal:
            return "Legal";
        case Category::Environmental:
            return "Environmental";
    }

    throw std::logic_error("Unknown category.");
}

std::string toString(Direction direction) {
    return direction == Direction::Opportunity
        ? "Opportunity"
        : "Threat";
}

std::string toString(Horizon horizon) {
    switch (horizon) {
        case Horizon::Short:
            return "Short";
        case Horizon::Medium:
            return "Medium";
        case Horizon::Long:
            return "Long";
    }

    throw std::logic_error("Unknown horizon.");
}

struct PESTLEFactor {
    std::string id;
    Category category;
    std::string title;
    std::string description;
    Direction direction;
    int likelihood;
    int impact;
    int confidence;
    Horizon horizon;
    std::string evidence;
    std::vector<std::string> affectedAreas;

    int rawScore() const {
        return likelihood * impact;
    }

    double signedScore() const {
        const double score =
            static_cast<double>(rawScore()) *
            (static_cast<double>(confidence) / 5.0);

        return direction == Direction::Opportunity
            ? score
            : -score;
    }
};

struct CategoryResult {
    int factorCount = 0;
    int opportunities = 0;
    int threats = 0;
    double netScore = 0.0;
};

class AssessmentValidator {
public:
    static void validate(const PESTLEFactor& factor) {
        if (factor.id.empty()) {
            throw std::invalid_argument("Factor ID cannot be empty.");
        }

        if (factor.title.empty()) {
            throw std::invalid_argument("Factor title cannot be empty.");
        }

        if (factor.description.empty()) {
            throw std::invalid_argument(
                "Factor description cannot be empty."
            );
        }

        if (factor.evidence.empty()) {
            throw std::invalid_argument(
                "Evidence cannot be empty."
            );
        }

        validateRange("likelihood", factor.likelihood);
        validateRange("impact", factor.impact);
        validateRange("confidence", factor.confidence);
    }

private:
    static void validateRange(const std::string& field, int value) {
        if (value < 1 || value > 5) {
            throw std::invalid_argument(
                field + " must be between 1 and 5."
            );
        }
    }
};

class PESTLEGovernanceEngine {
public:
    explicit PESTLEGovernanceEngine(std::string organization)
        : organization_(std::move(organization)) {
        if (organization_.empty()) {
            throw std::invalid_argument(
                "Organization name cannot be empty."
            );
        }
    }

    void addFactor(const PESTLEFactor& factor) {
        AssessmentValidator::validate(factor);

        const auto duplicate = std::find_if(
            factors_.begin(),
            factors_.end(),
            [&](const PESTLEFactor& existing) {
                return existing.id == factor.id;
            }
        );

        if (duplicate != factors_.end()) {
            throw std::invalid_argument(
                "Duplicate factor ID: " + factor.id
            );
        }

        factors_.push_back(factor);
    }

    const std::vector<PESTLEFactor>& factors() const {
        return factors_;
    }

    std::vector<PESTLEFactor> byCategory(Category category) const {
        std::vector<PESTLEFactor> result;

        for (const auto& factor : factors_) {
            if (factor.category == category) {
                result.push_back(factor);
            }
        }

        return result;
    }

    double netScore() const {
        double total = 0.0;

        for (const auto& factor : factors_) {
            total += factor.signedScore();
        }

        return total;
    }

    CategoryResult summarizeCategory(Category category) const {
        const auto selected = byCategory(category);

        CategoryResult result;
        result.factorCount =
            static_cast<int>(selected.size());

        for (const auto& factor : selected) {
            result.netScore += factor.signedScore();

            if (factor.direction == Direction::Opportunity) {
                ++result.opportunities;
            } else {
                ++result.threats;
            }
        }

        return result;
    }

    std::vector<PESTLEFactor> highExposureThreats(
        int minimumRawScore
    ) const {
        std::vector<PESTLEFactor> result;

        for (const auto& factor : factors_) {
            if (
                factor.direction == Direction::Threat &&
                factor.rawScore() >= minimumRawScore
            ) {
                result.push_back(factor);
            }
        }

        std::sort(
            result.begin(),
            result.end(),
            [](const PESTLEFactor& left, const PESTLEFactor& right) {
                return left.rawScore() > right.rawScore();
            }
        );

        return result;
    }

    std::vector<PESTLEFactor> weakEvidence() const {
        std::vector<PESTLEFactor> result;

        for (const auto& factor : factors_) {
            if (factor.confidence <= 2) {
                result.push_back(factor);
            }
        }

        return result;
    }

    double scenarioScore(
        double likelihoodMultiplier,
        double impactMultiplier
    ) const {
        if (
            likelihoodMultiplier < 0.0 ||
            impactMultiplier < 0.0
        ) {
            throw std::invalid_argument(
                "Scenario multipliers cannot be negative."
            );
        }

        double total = 0.0;

        for (const auto& factor : factors_) {
            const double scenarioLikelihood = std::min(
                5.0,
                factor.likelihood * likelihoodMultiplier
            );

            const double scenarioImpact = std::min(
                5.0,
                factor.impact * impactMultiplier
            );

            double score =
                scenarioLikelihood *
                scenarioImpact *
                (static_cast<double>(factor.confidence) / 5.0);

            if (factor.direction == Direction::Threat) {
                score *= -1.0;
            }

            total += score;
        }

        return total;
    }

private:
    std::string organization_;
    std::vector<PESTLEFactor> factors_;
};

class GovernancePolicy {
public:
    GovernancePolicy(
        int maximumHighExposureThreats,
        int minimumConfidenceForDecision,
        bool requireLegalReview
    )
        : maximumHighExposureThreats_(
              maximumHighExposureThreats
          ),
          minimumConfidenceForDecision_(
              minimumConfidenceForDecision
          ),
          requireLegalReview_(requireLegalReview) {}

    bool canProceed(
        const PESTLEGovernanceEngine& engine,
        std::vector<std::string>& reasons
    ) const {
        bool allowed = true;

        const auto highThreats =
            engine.highExposureThreats(16);

        if (
            static_cast<int>(highThreats.size()) >
            maximumHighExposureThreats_
        ) {
            allowed = false;

            reasons.push_back(
                "High-exposure threat count exceeds the governance threshold."
            );
        }

        for (const auto& factor : engine.factors()) {
            if (
                factor.direction == Direction::Threat &&
                factor.confidence < minimumConfidenceForDecision_
            ) {
                allowed = false;

                reasons.push_back(
                    "A material threat lacks sufficient evidence confidence: " +
                    factor.title
                );
            }

            if (
                requireLegalReview_ &&
                factor.category == Category::Legal &&
                factor.direction == Direction::Threat &&
                factor.rawScore() >= 12
            ) {
                allowed = false;

                reasons.push_back(
                    "Material legal exposure requires explicit legal review: " +
                    factor.title
                );
            }
        }

        return allowed;
    }

private:
    int maximumHighExposureThreats_;
    int minimumConfidenceForDecision_;
    bool requireLegalReview_;
};

PESTLEGovernanceEngine buildCaseStudy() {
    PESTLEGovernanceEngine engine(
        "Northstar Analytics"
    );

    engine.addFactor({
        "P-001",
        Category::Political,
        "Public digital infrastructure investment",
        "Government digital investment may expand demand for analytics.",
        Direction::Opportunity,
        4,
        4,
        4,
        Horizon::Medium,
        "Market planning identifies public digital infrastructure as a demand driver.",
        {"public-sector sales"}
    });

    engine.addFactor({
        "P-002",
        Category::Political,
        "Geopolitical procurement uncertainty",
        "International conditions can change procurement and partnership decisions.",
        Direction::Threat,
        3,
        4,
        3,
        Horizon::Medium,
        "International expansion creates cross-border procurement exposure.",
        {"international sales"}
    });

    engine.addFactor({
        "E-001",
        Category::Economic,
        "Enterprise technology spending",
        "Higher enterprise technology budgets can increase analytics demand.",
        Direction::Opportunity,
        4,
        5,
        4,
        Horizon::Medium,
        "Customer planning indicates increased data-modernization expenditure.",
        {"subscription revenue"}
    });

    engine.addFactor({
        "E-002",
        Category::Economic,
        "Currency volatility",
        "Currency movement can affect imported costs and foreign revenue.",
        Direction::Threat,
        4,
        3,
        4,
        Horizon::Short,
        "The operating model has domestic expenses and foreign-currency contracts.",
        {"margin", "pricing"}
    });

    engine.addFactor({
        "S-001",
        Category::Social,
        "Increasing data literacy",
        "Business users increasingly expect accessible data-driven decision support.",
        Direction::Opportunity,
        5,
        4,
        4,
        Horizon::Medium,
        "Customer discovery identifies demand for self-service analytics.",
        {"product adoption", "UX"}
    });

    engine.addFactor({
        "S-002",
        Category::Social,
        "Resistance to workflow change",
        "Employees may resist analytics-driven changes to established processes.",
        Direction::Threat,
        3,
        3,
        3,
        Horizon::Short,
        "Enterprise implementations contain change-management exposure.",
        {"implementation"}
    });

    engine.addFactor({
        "T-001",
        Category::Technological,
        "Real-time analytics infrastructure",
        "Streaming technology enables near-real-time operational analytics.",
        Direction::Opportunity,
        5,
        5,
        5,
        Horizon::Medium,
        "The architecture supports event-based ingestion and incremental processing.",
        {"product capability"}
    });

    engine.addFactor({
        "T-002",
        Category::Technological,
        "Rapid analytics-platform change",
        "Fast technology cycles can increase engineering cost and architectural churn.",
        Direction::Threat,
        4,
        4,
        4,
        Horizon::Long,
        "The roadmap depends on rapidly changing data infrastructure.",
        {"engineering", "architecture"}
    });

    engine.addFactor({
        "L-001",
        Category::Legal,
        "Data-protection obligations",
        "Personal-data processing creates privacy and security obligations.",
        Direction::Threat,
        4,
        5,
        5,
        Horizon::Short,
        "Customer datasets may contain identifiable information.",
        {"privacy", "security", "contracts"}
    });

    engine.addFactor({
        "L-002",
        Category::Legal,
        "Contract standardization",
        "Standard enterprise clauses can reduce negotiation effort.",
        Direction::Opportunity,
        4,
        3,
        4,
        Horizon::Short,
        "Commercial operations are adopting repeatable enterprise agreements.",
        {"sales cycle"}
    });

    engine.addFactor({
        "EN-001",
        Category::Environmental,
        "Data-center energy demand",
        "Compute-heavy analytics can increase energy consumption.",
        Direction::Threat,
        4,
        4,
        4,
        Horizon::Medium,
        "Forecast workloads include continuous analytics processing.",
        {"operating cost"}
    });

    engine.addFactor({
        "EN-002",
        Category::Environmental,
        "Sustainability analytics demand",
        "Customers may need analytics for environmental performance reporting.",
        Direction::Opportunity,
        4,
        4,
        3,
        Horizon::Medium,
        "Target customers increasingly request environmental metrics.",
        {"product modules", "enterprise sales"}
    });

    return engine;
}

void printCategoryProfile(
    const PESTLEGovernanceEngine& engine
) {
    std::cout << "\nCATEGORY PROFILE\n";

    const std::vector<Category> categories = {
        Category::Political,
        Category::Economic,
        Category::Social,
        Category::Technological,
        Category::Legal,
        Category::Environmental
    };

    std::cout
        << std::left
        << std::setw(18) << "Category"
        << std::setw(10) << "Factors"
        << std::setw(15) << "Opportunities"
        << std::setw(10) << "Threats"
        << "Net Score\n";

    std::cout << std::string(70, '-') << '\n';

    for (const auto category : categories) {
        const auto result =
            engine.summarizeCategory(category);

        std::cout
            << std::left
            << std::setw(18) << toString(category)
            << std::setw(10) << result.factorCount
            << std::setw(15) << result.opportunities
            << std::setw(10) << result.threats
            << std::fixed
            << std::setprecision(2)
            << result.netScore
            << '\n';
    }
}

void printMaterialThreats(
    const PESTLEGovernanceEngine& engine
) {
    std::cout << "\nMATERIAL THREATS\n";

    const auto threats =
        engine.highExposureThreats(16);

    if (threats.empty()) {
        std::cout << "No material threats meet the threshold.\n";
        return;
    }

    for (const auto& factor : threats) {
        std::cout
            << factor.id
            << " | "
            << toString(factor.category)
            << " | "
            << factor.title
            << " | raw score="
            << factor.rawScore()
            << " | adjusted="
            << std::fixed
            << std::setprecision(2)
            << factor.signedScore()
            << '\n';
    }
}

void printScenarioAnalysis(
    const PESTLEGovernanceEngine& engine
) {
    struct Scenario {
        std::string name;
        double likelihood;
        double impact;
    };

    const std::vector<Scenario> scenarios = {
        {"Baseline", 1.0, 1.0},
        {"Elevated external pressure", 1.2, 1.2},
        {"Lower external pressure", 0.8, 0.9},
        {"High-impact disruption", 1.1, 1.4}
    };

    std::cout << "\nSCENARIO ANALYSIS\n";

    for (const auto& scenario : scenarios) {
        const double score = engine.scenarioScore(
            scenario.likelihood,
            scenario.impact
        );

        std::cout
            << std::left
            << std::setw(28)
            << scenario.name
            << std::fixed
            << std::setprecision(2)
            << score
            << '\n';
    }
}

void printFactorRelationships(
    const PESTLEGovernanceEngine& engine
) {
    std::cout << "\nCATEGORY-SPECIFIC GOVERNANCE SIGNALS\n";

    /*
        These messages demonstrate that category interpretation matters.

        Political: watch policy and geopolitical exposure.
        Economic: examine demand and cost sensitivity.
        Social: monitor adoption and workforce behavior.
        Technological: monitor capability and obsolescence.
        Legal: escalate enforceable obligations.
        Environmental: examine ecological impact and resource exposure.
    */
    const std::vector<Category> categories = {
        Category::Political,
        Category::Economic,
        Category::Social,
        Category::Technological,
        Category::Legal,
        Category::Environmental
    };

    for (const auto category : categories) {
        const auto factors = engine.byCategory(category);

        std::cout
            << "\n"
            << toString(category)
            << ":\n";

        for (const auto& factor : factors) {
            std::cout
                << "  "
                << factor.title
                << " -> "
                << toString(factor.direction)
                << ", horizon="
                << toString(factor.horizon)
                << '\n';
        }
    }
}

void demonstrateValidationFailure() {
    std::cout << "\nVALIDATION TEST\n";

    PESTLEFactor invalid{
        "INVALID",
        Category::Legal,
        "Invalid assessment",
        "This factor intentionally violates the scoring rule.",
        Direction::Threat,
        7,
        4,
        4,
        Horizon::Short,
        "Validation test.",
        {"governance"}
    };

    try {
        AssessmentValidator::validate(invalid);
        std::cout << "Unexpected validation success.\n";
    } catch (const std::exception& error) {
        std::cout
            << "Validation correctly rejected the record: "
            << error.what()
            << '\n';
    }
}

int main() {
    try {
        const auto engine = buildCaseStudy();

        std::cout
            << "PESTLE GOVERNANCE ENGINE\n"
            << "Organization: Northstar Analytics\n"
            << "Factors: "
            << engine.factors().size()
            << '\n';

        printCategoryProfile(engine);

        std::cout
            << "\nBASELINE NET SCORE: "
            << std::fixed
            << std::setprecision(2)
            << engine.netScore()
            << '\n';

        printMaterialThreats(engine);
        printScenarioAnalysis(engine);
        printFactorRelationships(engine);
        demonstrateValidationFailure();

        std::vector<std::string> policyReasons;

        const GovernancePolicy policy(
            2,
            3,
            true
        );

        const bool permitted =
            policy.canProceed(engine, policyReasons);

        std::cout
            << "\nGOVERNANCE DECISION\n"
            << "Policy conditions satisfied: "
            << std::boolalpha
            << permitted
            << '\n';

        if (!permitted) {
            std::cout
                << "Decision requires resolution of these governance conditions:\n";

            for (const auto& reason : policyReasons) {
                std::cout
                    << "  - "
                    << reason
                    << '\n';
            }
        }

        /*
            Complexity:
            - Category filtering is O(n) for each category.
            - Net score is O(n).
            - Material-threat extraction is O(n) plus O(k log k) sorting,
              where k is the number of selected threats.
            - The vector is intentionally used because PESTLE assessments are
              normally small enough that straightforward sequential analysis
              is preferable to complicated indexing structures.
        */

        std::cout
            << "\nCASE STUDY COMPLETED\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal assessment error: "
            << error.what()
            << '\n';

        return 1;
    }
}
