#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
    Competitive Analysis: C++ Industry-Style Case Study
    ====================================================

    Scenario
    --------
    A fictional SaaS company is evaluating the competitive position of
    "FocusFlow", a workflow-management platform aimed at growing operations
    teams.

    The program models:
      1. Competitor classification
      2. Direct vs. indirect competition
      3. Feature comparison
      4. Weighted competitive scoring
      5. Price-value analysis
      6. Positioning dimensions
      7. Feature-gap analysis
      8. Similarity analysis using vectors
      9. Sensitivity analysis
     10. Validation and error handling
     11. Basic testing
     12. Complexity considerations

    Compile:
        g++ -std=c++17 -O2 -Wall -Wextra competitive_analysis.cpp -o competitive_analysis

    Run:
        ./competitive_analysis
*/

enum class CompetitionType {
    Direct,
    Indirect,
    Potential
};

enum class FeatureStatus {
    Absent,
    Basic,
    Strong,
    Differentiated
};

struct Criterion {
    std::string name;
    double weight;
    std::string description;
};

struct Competitor {
    std::string name;
    CompetitionType type;
    std::string targetSegment;
    double pricePerUser;

    // unordered_map gives average O(1) lookup by criterion or feature name.
    std::unordered_map<std::string, double> scores;
    std::unordered_map<std::string, FeatureStatus> featureStatus;

    std::string positioning;
};

struct PositioningProfile {
    std::string productName;
    std::string targetCustomer;
    std::string primaryNeed;
    std::string keyDifference;
    std::string valueProposition;
};

struct Feature {
    std::string name;
    std::string category;
    std::string description;
};


// ============================================================================
// 1. ENUMERATION HELPERS
// ============================================================================

std::string competitionTypeToString(CompetitionType type) {
    switch (type) {
        case CompetitionType::Direct:
            return "Direct";
        case CompetitionType::Indirect:
            return "Indirect";
        case CompetitionType::Potential:
            return "Potential";
    }

    throw std::logic_error("Unknown competition type.");
}

std::string featureStatusToString(FeatureStatus status) {
    switch (status) {
        case FeatureStatus::Absent:
            return "Absent";
        case FeatureStatus::Basic:
            return "Basic";
        case FeatureStatus::Strong:
            return "Strong";
        case FeatureStatus::Differentiated:
            return "Differentiated";
    }

    throw std::logic_error("Unknown feature status.");
}

int featureStrength(FeatureStatus status) {
    switch (status) {
        case FeatureStatus::Absent:
            return 0;
        case FeatureStatus::Basic:
            return 1;
        case FeatureStatus::Strong:
            return 2;
        case FeatureStatus::Differentiated:
            return 3;
    }

    throw std::logic_error("Unknown feature status.");
}


// ============================================================================
// 2. DATASET
// ============================================================================

std::vector<Criterion> buildCriteria() {
    return {
        {
            "Ease of Use",
            0.15,
            "How quickly customers can understand and use the product."
        },
        {
            "Task Management",
            0.15,
            "Quality of core project and work management."
        },
        {
            "Workflow Automation",
            0.15,
            "Ability to automate recurring processes."
        },
        {
            "Analytics",
            0.10,
            "Quality of reporting and operational insight."
        },
        {
            "AI Assistance",
            0.10,
            "Usefulness of intelligent assistance."
        },
        {
            "Integrations",
            0.10,
            "Breadth and usefulness of integrations."
        },
        {
            "Enterprise Security",
            0.10,
            "Security and governance capabilities."
        },
        {
            "Price Value",
            0.15,
            "Customer value relative to price."
        }
    };
}

std::vector<Feature> buildFeatures() {
    return {
        {
            "Task Management",
            "Core",
            "Create, assign, prioritize, and track work."
        },
        {
            "Workflow Automation",
            "Automation",
            "Automate repetitive business processes."
        },
        {
            "Analytics",
            "Insights",
            "Measure operational performance."
        },
        {
            "AI Assistance",
            "Intelligence",
            "Support planning and work execution."
        },
        {
            "Integrations",
            "Platform",
            "Connect external business systems."
        },
        {
            "Enterprise Security",
            "Security",
            "Support governance and controlled access."
        }
    };
}

std::vector<Competitor> buildCompetitors() {
    return {
        {
            "TaskFlow",
            CompetitionType::Direct,
            "SMB project teams",
            12.0,
            {
                {"Ease of Use", 4.7},
                {"Task Management", 4.6},
                {"Workflow Automation", 4.1},
                {"Analytics", 3.7},
                {"AI Assistance", 3.6},
                {"Integrations", 4.2},
                {"Enterprise Security", 3.5},
                {"Price Value", 4.5}
            },
            {
                {"Task Management", FeatureStatus::Strong},
                {"Workflow Automation", FeatureStatus::Strong},
                {"Analytics", FeatureStatus::Strong},
                {"AI Assistance", FeatureStatus::Basic},
                {"Integrations", FeatureStatus::Strong},
                {"Enterprise Security", FeatureStatus::Basic}
            },
            "Simple project management for growing teams."
        },
        {
            "EnterpriseSuite",
            CompetitionType::Direct,
            "Large enterprises",
            30.0,
            {
                {"Ease of Use", 3.0},
                {"Task Management", 4.5},
                {"Workflow Automation", 4.7},
                {"Analytics", 4.8},
                {"AI Assistance", 4.2},
                {"Integrations", 4.8},
                {"Enterprise Security", 5.0},
                {"Price Value", 3.0}
            },
            {
                {"Task Management", FeatureStatus::Strong},
                {"Workflow Automation", FeatureStatus::Differentiated},
                {"Analytics", FeatureStatus::Differentiated},
                {"AI Assistance", FeatureStatus::Strong},
                {"Integrations", FeatureStatus::Differentiated},
                {"Enterprise Security", FeatureStatus::Differentiated}
            },
            "Enterprise-grade work management at scale."
        },
        {
            "SpreadsheetPro",
            CompetitionType::Indirect,
            "Small teams and individuals",
            8.0,
            {
                {"Ease of Use", 4.2},
                {"Task Management", 3.0},
                {"Workflow Automation", 2.5},
                {"Analytics", 3.6},
                {"AI Assistance", 3.0},
                {"Integrations", 3.9},
                {"Enterprise Security", 3.0},
                {"Price Value", 4.8}
            },
            {
                {"Task Management", FeatureStatus::Basic},
                {"Workflow Automation", FeatureStatus::Basic},
                {"Analytics", FeatureStatus::Strong},
                {"AI Assistance", FeatureStatus::Basic},
                {"Integrations", FeatureStatus::Strong},
                {"Enterprise Security", FeatureStatus::Basic}
            },
            "Flexible spreadsheet-based business analysis."
        },
        {
            "EmailWorkflow",
            CompetitionType::Indirect,
            "Small service businesses",
            5.0,
            {
                {"Ease of Use", 4.8},
                {"Task Management", 2.4},
                {"Workflow Automation", 2.0},
                {"Analytics", 1.8},
                {"AI Assistance", 2.2},
                {"Integrations", 3.5},
                {"Enterprise Security", 3.2},
                {"Price Value", 4.9}
            },
            {
                {"Task Management", FeatureStatus::Absent},
                {"Workflow Automation", FeatureStatus::Basic},
                {"Analytics", FeatureStatus::Absent},
                {"AI Assistance", FeatureStatus::Basic},
                {"Integrations", FeatureStatus::Basic},
                {"Enterprise Security", FeatureStatus::Basic}
            },
            "Use familiar communication tools to coordinate work."
        }
    };
}


// ============================================================================
// 3. VALIDATION
// ============================================================================

void validateCriteria(const std::vector<Criterion>& criteria) {
    if (criteria.empty()) {
        throw std::invalid_argument("At least one criterion is required.");
    }

    double totalWeight = 0.0;

    for (const auto& criterion : criteria) {
        if (criterion.name.empty()) {
            throw std::invalid_argument(
                "Criterion name cannot be empty."
            );
        }

        if (criterion.weight < 0.0) {
            throw std::invalid_argument(
                "Criterion weight cannot be negative."
            );
        }

        totalWeight += criterion.weight;
    }

    if (totalWeight <= 0.0) {
        throw std::invalid_argument(
            "Total criterion weight must be positive."
        );
    }
}

void validateCompetitor(
    const Competitor& competitor,
    const std::vector<Criterion>& criteria
) {
    if (competitor.name.empty()) {
        throw std::invalid_argument(
            "Competitor name cannot be empty."
        );
    }

    if (competitor.pricePerUser < 0.0) {
        throw std::invalid_argument(
            competitor.name + ": price cannot be negative."
        );
    }

    for (const auto& criterion : criteria) {
        const auto iterator =
            competitor.scores.find(criterion.name);

        if (iterator == competitor.scores.end()) {
            throw std::invalid_argument(
                competitor.name +
                ": missing score for " +
                criterion.name
            );
        }

        if (iterator->second < 1.0 || iterator->second > 5.0) {
            throw std::invalid_argument(
                competitor.name +
                ": score for " +
                criterion.name +
                " must be between 1 and 5."
            );
        }
    }
}

void validateDataset(
    const std::vector<Competitor>& competitors,
    const std::vector<Criterion>& criteria
) {
    if (competitors.empty()) {
        throw std::invalid_argument(
            "At least one competitor is required."
        );
    }

    validateCriteria(criteria);

    for (const auto& competitor : competitors) {
        validateCompetitor(competitor, criteria);
    }
}


// ============================================================================
// 4. WEIGHTED SCORING
// ============================================================================

double weightedScore(
    const Competitor& competitor,
    const std::vector<Criterion>& criteria
) {
    double total = 0.0;

    for (const auto& criterion : criteria) {
        auto iterator =
            competitor.scores.find(criterion.name);

        if (iterator == competitor.scores.end()) {
            throw std::invalid_argument(
                "Missing score for " + criterion.name
            );
        }

        total += iterator->second * criterion.weight;
    }

    return total;
}

std::vector<std::pair<std::string, double>>
rankCompetitors(
    const std::vector<Competitor>& competitors,
    const std::vector<Criterion>& criteria
) {
    std::vector<std::pair<std::string, double>> results;

    for (const auto& competitor : competitors) {
        results.emplace_back(
            competitor.name,
            weightedScore(competitor, criteria)
        );
    }

    /*
        std::sort gives O(n log n) complexity for n competitors.
        The scoring itself is O(n*m), where m is the number of criteria.
    */
    std::sort(
        results.begin(),
        results.end(),
        [](const auto& first, const auto& second) {
            return first.second > second.second;
        }
    );

    return results;
}


// ============================================================================
// 5. FEATURE ANALYSIS
// ============================================================================

FeatureStatus getFeatureStatus(
    const Competitor& competitor,
    const std::string& featureName
) {
    const auto iterator =
        competitor.featureStatus.find(featureName);

    if (iterator == competitor.featureStatus.end()) {
        return FeatureStatus::Absent;
    }

    return iterator->second;
}

std::vector<std::string> featureGaps(
    const std::unordered_map<std::string, FeatureStatus>& focalProduct,
    const Competitor& competitor
) {
    std::vector<std::string> gaps;

    for (const auto& [featureName, competitorStatus] :
         competitor.featureStatus) {

        auto focalIterator =
            focalProduct.find(featureName);

        FeatureStatus focalStatus =
            focalIterator == focalProduct.end()
                ? FeatureStatus::Absent
                : focalIterator->second;

        if (
            featureStrength(competitorStatus) >
            featureStrength(focalStatus)
        ) {
            gaps.push_back(
                featureName +
                ": focal=" +
                featureStatusToString(focalStatus) +
                ", competitor=" +
                featureStatusToString(competitorStatus)
            );
        }
    }

    std::sort(gaps.begin(), gaps.end());
    return gaps;
}


// ============================================================================
// 6. PRICE-VALUE ANALYSIS
// ============================================================================

double pricePerValuePoint(
    const Competitor& competitor,
    const std::vector<Criterion>& criteria
) {
    const double score =
        weightedScore(competitor, criteria);

    if (score == 0.0) {
        return std::numeric_limits<double>::infinity();
    }

    return competitor.pricePerUser / score;
}


// ============================================================================
// 7. POSITIONING VECTORS
// ============================================================================

std::vector<double> buildVector(
    const Competitor& competitor,
    const std::vector<std::string>& dimensions
) {
    std::vector<double> vector;

    for (const auto& dimension : dimensions) {
        auto iterator =
            competitor.scores.find(dimension);

        if (iterator == competitor.scores.end()) {
            throw std::invalid_argument(
                "Missing positioning dimension: " + dimension
            );
        }

        vector.push_back(iterator->second);
    }

    return vector;
}

double euclideanDistance(
    const std::vector<double>& first,
    const std::vector<double>& second
) {
    if (first.size() != second.size()) {
        throw std::invalid_argument(
            "Vectors must have equal dimensions."
        );
    }

    double sum = 0.0;

    for (std::size_t index = 0; index < first.size(); ++index) {
        const double difference =
            first[index] - second[index];

        sum += difference * difference;
    }

    return std::sqrt(sum);
}

std::vector<std::pair<std::string, double>>
similarityToReference(
    const Competitor& reference,
    const std::vector<Competitor>& competitors,
    const std::vector<std::string>& dimensions
) {
    const auto referenceVector =
        buildVector(reference, dimensions);

    std::vector<std::pair<std::string, double>> results;

    for (const auto& competitor : competitors) {
        if (competitor.name == reference.name) {
            continue;
        }

        const auto vector =
            buildVector(competitor, dimensions);

        results.emplace_back(
            competitor.name,
            euclideanDistance(referenceVector, vector)
        );
    }

    std::sort(
        results.begin(),
        results.end(),
        [](const auto& first, const auto& second) {
            return first.second < second.second;
        }
    );

    return results;
}


// ============================================================================
// 8. SENSITIVITY ANALYSIS
// ============================================================================

std::vector<Criterion> changeWeight(
    const std::vector<Criterion>& criteria,
    const std::string& changedCriterion,
    double newWeight
) {
    if (newWeight < 0.0 || newWeight > 1.0) {
        throw std::invalid_argument(
            "New weight must be between 0 and 1."
        );
    }

    std::vector<Criterion> modified = criteria;

    bool found = false;

    for (auto& criterion : modified) {
        if (criterion.name == changedCriterion) {
            criterion.weight = newWeight;
            found = true;
            break;
        }
    }

    if (!found) {
        throw std::invalid_argument(
            "Criterion not found: " + changedCriterion
        );
    }

    const double total =
        std::accumulate(
            modified.begin(),
            modified.end(),
            0.0,
            [](double sum, const Criterion& criterion) {
                return sum + criterion.weight;
            }
        );

    if (total <= 0.0) {
        throw std::invalid_argument(
            "Modified weight total must be positive."
        );
    }

    for (auto& criterion : modified) {
        criterion.weight /= total;
    }

    return modified;
}


// ============================================================================
// 9. OUTPUT FUNCTIONS
// ============================================================================

void printHeader(const std::string& title) {
    std::cout << "\n"
              << std::string(78, '=')
              << "\n"
              << title
              << "\n"
              << std::string(78, '=')
              << "\n";
}

void printPositioningProfile(
    const PositioningProfile& profile
) {
    printHeader("FOCUSFLOW POSITIONING");

    std::cout << "Product: "
              << profile.productName
              << "\n";

    std::cout << "Target customer: "
              << profile.targetCustomer
              << "\n";

    std::cout << "Primary need: "
              << profile.primaryNeed
              << "\n";

    std::cout << "Key difference: "
              << profile.keyDifference
              << "\n";

    std::cout << "Value proposition: "
              << profile.valueProposition
              << "\n";
}

void printClassification(
    const std::vector<Competitor>& competitors
) {
    printHeader("DIRECT VS. INDIRECT COMPETITION");

    for (const auto& competitor : competitors) {
        std::cout << "\n"
                  << competitor.name
                  << "\n";

        std::cout << "  Type: "
                  << competitionTypeToString(competitor.type)
                  << "\n";

        std::cout << "  Target segment: "
                  << competitor.targetSegment
                  << "\n";

        if (competitor.type == CompetitionType::Direct) {
            std::cout
                << "  Reason: similar solution category and customer need.\n";
        } else if (competitor.type == CompetitionType::Indirect) {
            std::cout
                << "  Reason: different solution category addressing part "
                << "of the same underlying need.\n";
        } else {
            std::cout
                << "  Reason: could become relevant if capabilities are "
                << "redirected toward the need.\n";
        }

        std::cout << "  Positioning: "
                  << competitor.positioning
                  << "\n";
    }
}

void printWeightedScores(
    const std::vector<Competitor>& competitors,
    const std::vector<Criterion>& criteria
) {
    printHeader("WEIGHTED COMPETITIVE SCORES");

    const auto rankings =
        rankCompetitors(competitors, criteria);

    std::cout << std::left
              << std::setw(22)
              << "Competitor"
              << std::setw(14)
              << "Type"
              << std::setw(16)
              << "Score"
              << "\n";

    std::cout << std::string(52, '-')
              << "\n";

    for (const auto& [name, score] : rankings) {
        auto iterator = std::find_if(
            competitors.begin(),
            competitors.end(),
            [&](const Competitor& competitor) {
                return competitor.name == name;
            }
        );

        std::cout << std::left
                  << std::setw(22)
                  << name
                  << std::setw(14)
                  << competitionTypeToString(iterator->type)
                  << std::fixed
                  << std::setprecision(2)
                  << score
                  << "\n";
    }
}

void printFeatureMatrix(
    const std::vector<Feature>& features,
    const std::vector<Competitor>& competitors
) {
    printHeader("FEATURE COMPARISON MATRIX");

    std::cout << std::left
              << std::setw(25)
              << "Feature";

    for (const auto& competitor : competitors) {
        std::cout << std::setw(20)
                  << competitor.name;
    }

    std::cout << "\n"
              << std::string(
                    25 + competitors.size() * 20,
                    '-'
                 )
              << "\n";

    for (const auto& feature : features) {
        std::cout << std::left
                  << std::setw(25)
                  << feature.name;

        for (const auto& competitor : competitors) {
            std::cout << std::setw(20)
                      << featureStatusToString(
                             getFeatureStatus(
                                 competitor,
                                 feature.name
                             )
                         );
        }

        std::cout << "\n";
    }
}

void printFeatureGaps(
    const std::unordered_map<std::string, FeatureStatus>& focalProduct,
    const std::vector<Competitor>& competitors
) {
    printHeader("FOCAL PRODUCT FEATURE GAPS");

    for (const auto& competitor : competitors) {
        std::cout << "\nAgainst "
                  << competitor.name
                  << ":\n";

        const auto gaps =
            featureGaps(focalProduct, competitor);

        if (gaps.empty()) {
            std::cout
                << "  No stronger competitor feature status detected.\n";
        } else {
            for (const auto& gap : gaps) {
                std::cout
                    << "  - "
                    << gap
                    << "\n";
            }
        }
    }
}

void printPriceValue(
    const std::vector<Competitor>& competitors,
    const std::vector<Criterion>& criteria
) {
    printHeader("PRICE-VALUE ANALYSIS");

    for (const auto& competitor : competitors) {
        const double score =
            weightedScore(competitor, criteria);

        const double ratio =
            pricePerValuePoint(competitor, criteria);

        std::cout << std::left
                  << std::setw(20)
                  << competitor.name
                  << "price/user=$"
                  << std::fixed
                  << std::setprecision(2)
                  << competitor.pricePerUser
                  << " score="
                  << score
                  << " price/point=$"
                  << ratio
                  << "\n";
    }
}

void printSimilarity(
    const std::vector<Competitor>& competitors,
    const std::vector<std::string>& dimensions
) {
    printHeader("POSITIONING VECTOR SIMILARITY");

    const Competitor& reference = competitors.front();

    std::cout << "Reference competitor: "
              << reference.name
              << "\n";

    const auto results =
        similarityToReference(
            reference,
            competitors,
            dimensions
        );

    for (const auto& [name, distance] : results) {
        std::cout << std::left
                  << std::setw(22)
                  << name
                  << "distance="
                  << std::fixed
                  << std::setprecision(2)
                  << distance
                  << "\n";
    }

    std::cout
        << "\nSmaller distance means more similar on the selected dimensions. "
        << "It does not mean strategically superior.\n";
}

void printSensitivity(
    const std::vector<Competitor>& competitors,
    const std::vector<Criterion>& criteria
) {
    printHeader("SENSITIVITY ANALYSIS");

    const std::vector<std::pair<std::string, double>> scenarios = {
        {"Ease of Use", 0.30},
        {"Enterprise Security", 0.30},
        {"Price Value", 0.30}
    };

    for (const auto& [criterion, weight] : scenarios) {
        std::cout
            << "\nScenario: "
            << criterion
            << " weight changed to "
            << weight
            << "\n";

        const auto modified =
            changeWeight(
                criteria,
                criterion,
                weight
            );

        const auto rankings =
            rankCompetitors(
                competitors,
                modified
            );

        for (const auto& [name, score] : rankings) {
            std::cout
                << "  "
                << std::left
                << std::setw(22)
                << name
                << std::fixed
                << std::setprecision(2)
                << score
                << "\n";
        }
    }
}


// ============================================================================
// 10. TESTS
// ============================================================================

void runTests(
    const std::vector<Competitor>& competitors,
    const std::vector<Criterion>& criteria
) {
    printHeader("BUILT-IN TESTS");

    validateDataset(
        competitors,
        criteria
    );

    const double weightTotal =
        std::accumulate(
            criteria.begin(),
            criteria.end(),
            0.0,
            [](double sum, const Criterion& criterion) {
                return sum + criterion.weight;
            }
        );

    if (std::abs(weightTotal - 1.0) > 1e-9) {
        throw std::runtime_error(
            "Criterion weights do not sum to one."
        );
    }

    for (const auto& competitor : competitors) {
        const double score =
            weightedScore(
                competitor,
                criteria
            );

        if (score < 1.0 || score > 5.0) {
            throw std::runtime_error(
                "Weighted score is outside expected range."
            );
        }
    }

    const double distance =
        euclideanDistance(
            {1.0, 2.0, 3.0},
            {4.0, 6.0, 3.0}
        );

    if (std::abs(distance - 5.0) > 1e-9) {
        throw std::runtime_error(
            "Euclidean distance test failed."
        );
    }

    std::cout << "All built-in tests passed.\n";
}


// ============================================================================
// 11. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        const auto criteria = buildCriteria();
        const auto competitors = buildCompetitors();
        const auto features = buildFeatures();

        validateDataset(
            competitors,
            criteria
        );

        const PositioningProfile focusFlow{
            "FocusFlow",
            "Growing operations teams with 20-200 employees",
            "Coordinating repeatable operational work without "
            "enterprise-level complexity",
            "Simple workflow automation combined with actionable "
            "operational analytics",
            "FocusFlow helps growing teams standardize recurring work, "
            "automate routine steps, and understand operational "
            "performance without requiring a large enterprise implementation."
        };

        const std::unordered_map<std::string, FeatureStatus>
            focalProductFeatures = {
                {
                    "Task Management",
                    FeatureStatus::Strong
                },
                {
                    "Workflow Automation",
                    FeatureStatus::Differentiated
                },
                {
                    "Analytics",
                    FeatureStatus::Differentiated
                },
                {
                    "AI Assistance",
                    FeatureStatus::Strong
                },
                {
                    "Integrations",
                    FeatureStatus::Strong
                },
                {
                    "Enterprise Security",
                    FeatureStatus::Basic
                }
            };

        printPositioningProfile(focusFlow);
        printClassification(competitors);
        printWeightedScores(
            competitors,
            criteria
        );
        printFeatureMatrix(
            features,
            competitors
        );
        printFeatureGaps(
            focalProductFeatures,
            competitors
        );
        printPriceValue(
            competitors,
            criteria
        );

        printSimilarity(
            competitors,
            {
                "Ease of Use",
                "Workflow Automation",
                "Analytics",
                "Enterprise Security"
            }
        );

        printSensitivity(
            competitors,
            criteria
        );

        runTests(
            competitors,
            criteria
        );

        printHeader("ARCHITECTURAL AND PERFORMANCE NOTES");

        std::cout
            << "Competitor scoring is O(N*M), where N is competitors and "
            << "M is criteria.\n";

        std::cout
            << "Ranking is O(N log N) after scoring.\n";

        std::cout
            << "Feature-gap analysis is approximately O(N*F), where F is "
            << "the number of stored features per competitor.\n";

        std::cout
            << "unordered_map provides average O(1) key lookup but does "
            << "not preserve insertion order.\n";

        std::cout
            << "For small analytical datasets, correctness and traceability "
            << "are generally more important than micro-optimizations.\n";

        std::cout
            << "For production use, raw evidence should be stored separately "
            << "from analyst scores so every assessment can be audited.\n";

        std::cout
            << "A composite score should not be treated as an automatic "
            << "strategic decision. Customer importance, market segment, "
            << "cost, feasibility, differentiation, and defensibility "
            << "must be interpreted separately.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "ERROR: "
            << error.what()
            << "\n";

        return 1;
    }
}
