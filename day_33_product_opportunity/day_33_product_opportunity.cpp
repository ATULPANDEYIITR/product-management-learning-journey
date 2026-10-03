#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Product Opportunity Governance Engine
 *
 * Case study:
 * A B2B SaaS product team has collected customer evidence and must turn it
 * into structured product opportunities. The governance engine:
 *
 *   evidence -> opportunity definition -> opportunity sizing -> scoring
 *
 * The program intentionally separates these activities. Evidence describes
 * observed problems. Sizing estimates potential scale from explicit assumptions.
 * Scoring applies a prioritization policy. No stage silently replaces another.
 *
 * C++17 or later.
 */

enum class OpportunityCategory {
    Acquisition,
    Activation,
    Retention,
    Monetization,
    OperationalEfficiency
};

std::string toString(OpportunityCategory category) {
    switch (category) {
        case OpportunityCategory::Acquisition:
            return "acquisition";
        case OpportunityCategory::Activation:
            return "activation";
        case OpportunityCategory::Retention:
            return "retention";
        case OpportunityCategory::Monetization:
            return "monetization";
        case OpportunityCategory::OperationalEfficiency:
            return "operational-efficiency";
    }

    throw std::logic_error("Unknown opportunity category");
}

struct CustomerSignal {
    std::string id;
    std::string source;
    std::string description;
    OpportunityCategory category;
    int affectedUsers{};
    double frequencyPerMonth{};
    double severity{};
    double confidence{};

    double evidenceStrength() const {
        return severity * confidence;
    }

    void validate() const {
        if (id.empty() || source.empty() || description.empty()) {
            throw std::invalid_argument(
                "A customer signal requires id, source, and description"
            );
        }

        if (affectedUsers < 0) {
            throw std::invalid_argument(
                "affectedUsers cannot be negative"
            );
        }

        if (frequencyPerMonth < 0) {
            throw std::invalid_argument(
                "frequencyPerMonth cannot be negative"
            );
        }

        if (severity < 0 || severity > 10) {
            throw std::invalid_argument(
                "severity must be between 0 and 10"
            );
        }

        if (confidence < 0 || confidence > 1) {
            throw std::invalid_argument(
                "confidence must be between 0 and 1"
            );
        }
    }
};

struct ScoreWeights {
    double customerValue{};
    double strategicAlignment{};
    double confidence{};
    double effort{};
    double timeToValue{};
    double risk{};

    double total() const {
        return customerValue
             + strategicAlignment
             + confidence
             + effort
             + timeToValue
             + risk;
    }

    void validate() const {
        if (customerValue < 0 ||
            strategicAlignment < 0 ||
            confidence < 0 ||
            effort < 0 ||
            timeToValue < 0 ||
            risk < 0) {
            throw std::invalid_argument(
                "Scoring weights cannot be negative"
            );
        }

        if (total() <= 0) {
            throw std::invalid_argument(
                "At least one scoring weight must be positive"
            );
        }
    }
};

struct SizingModel {
    long long targetPopulation{};
    double annualValuePerUser{};
    double reachableShare{};
    double adoptionRate{};

    double tam() const {
        return static_cast<double>(targetPopulation)
             * annualValuePerUser;
    }

    double sam() const {
        return tam() * reachableShare;
    }

    double expectedValue() const {
        return sam() * adoptionRate;
    }

    void validate() const {
        if (targetPopulation < 0) {
            throw std::invalid_argument(
                "targetPopulation cannot be negative"
            );
        }

        if (annualValuePerUser < 0) {
            throw std::invalid_argument(
                "annualValuePerUser cannot be negative"
            );
        }

        if (reachableShare < 0 || reachableShare > 1) {
            throw std::invalid_argument(
                "reachableShare must be between 0 and 1"
            );
        }

        if (adoptionRate < 0 || adoptionRate > 1) {
            throw std::invalid_argument(
                "adoptionRate must be between 0 and 1"
            );
        }
    }
};

struct OpportunityCriteria {
    double customerValue{};
    double strategicAlignment{};
    double confidence{};
    double effort{};
    double timeToValue{};
    double risk{};

    void validate() const {
        const std::vector<std::pair<std::string, double>> values{
            {"customerValue", customerValue},
            {"strategicAlignment", strategicAlignment},
            {"confidence", confidence},
            {"effort", effort},
            {"timeToValue", timeToValue},
            {"risk", risk}
        };

        for (const auto& [name, value] : values) {
            if (value < 0 || value > 10) {
                throw std::invalid_argument(
                    name + " must be between 0 and 10"
                );
            }
        }
    }
};

class ProductOpportunity {
private:
    std::vector<CustomerSignal> signals_;

public:
    std::string id;
    std::string title;
    std::string problemStatement;
    std::string customerSegment;
    OpportunityCategory category;
    SizingModel sizing;
    OpportunityCriteria criteria;

    double tamValue{};
    double samValue{};
    double expectedValue{};
    double score{};

    ProductOpportunity(
        std::string opportunityId,
        std::string opportunityTitle,
        std::string problem,
        std::string segment,
        OpportunityCategory opportunityCategory,
        SizingModel sizingModel,
        OpportunityCriteria scoringCriteria
    )
        : id(std::move(opportunityId)),
          title(std::move(opportunityTitle)),
          problemStatement(std::move(problem)),
          customerSegment(std::move(segment)),
          category(opportunityCategory),
          sizing(std::move(sizingModel)),
          criteria(std::move(scoringCriteria)) {}

    void addSignal(const CustomerSignal& signal) {
        signal.validate();

        if (signal.category != category) {
            throw std::invalid_argument(
                "Signal " + signal.id +
                " does not belong to opportunity category " +
                toString(category)
            );
        }

        signals_.push_back(signal);
    }

    const std::vector<CustomerSignal>& signals() const {
        return signals_;
    }

    double evidenceStrength() const {
        if (signals_.empty()) {
            return 0;
        }

        double total = 0;

        for (const auto& signal : signals_) {
            total += signal.evidenceStrength();
        }

        return std::min(10.0, total / signals_.size());
    }

    void calculateSize() {
        sizing.validate();

        tamValue = sizing.tam();
        samValue = sizing.sam();
        expectedValue = sizing.expectedValue();
    }

    void calculateScore(const ScoreWeights& weights) {
        weights.validate();
        criteria.validate();

        /*
         * Effort and risk are inverse criteria. A score of 8 for effort means
         * relatively difficult delivery, so its favorable contribution is 2.
         * This avoids treating "high effort" as a positive outcome.
         */
        const double effectiveConfidence =
            criteria.confidence * 0.6
            + evidenceStrength() * 0.4;

        const double totalWeight = weights.total();

        score =
            (
                criteria.customerValue * weights.customerValue
                + criteria.strategicAlignment * weights.strategicAlignment
                + effectiveConfidence * weights.confidence
                + (10 - criteria.effort) * weights.effort
                + criteria.timeToValue * weights.timeToValue
                + (10 - criteria.risk) * weights.risk
            ) / totalWeight;
    }
};

class OpportunityRepository {
private:
    std::map<std::string, ProductOpportunity> opportunities_;

public:
    void add(ProductOpportunity opportunity) {
        const auto [iterator, inserted] =
            opportunities_.emplace(opportunity.id, std::move(opportunity));

        if (!inserted) {
            throw std::invalid_argument(
                "Duplicate opportunity id: " + iterator->first
            );
        }
    }

    ProductOpportunity& get(const std::string& id) {
        auto iterator = opportunities_.find(id);

        if (iterator == opportunities_.end()) {
            throw std::out_of_range(
                "Opportunity does not exist: " + id
            );
        }

        return iterator->second;
    }

    const std::map<std::string, ProductOpportunity>& all() const {
        return opportunities_;
    }
};

struct AdoptionScenario {
    double adoptionRate{};
    double expectedValue{};
};

std::vector<AdoptionScenario> runAdoptionSensitivity(
    const ProductOpportunity& opportunity,
    const std::vector<double>& rates
) {
    std::vector<AdoptionScenario> scenarios;

    for (double rate : rates) {
        if (rate < 0 || rate > 1) {
            throw std::invalid_argument(
                "Sensitivity adoption rate must be between 0 and 1"
            );
        }

        scenarios.push_back({
            rate,
            opportunity.samValue * rate
        });
    }

    return scenarios;
}

void printCurrency(double value) {
    std::cout
        << "$"
        << std::fixed
        << std::setprecision(0)
        << value;
}

void printOpportunity(const ProductOpportunity& opportunity) {
    std::cout << "\n" << opportunity.id
              << " | " << opportunity.title << "\n";

    std::cout << "  Category: "
              << toString(opportunity.category) << "\n";

    std::cout << "  Segment: "
              << opportunity.customerSegment << "\n";

    std::cout << "  Problem: "
              << opportunity.problemStatement << "\n";

    std::cout << "  Evidence signals: "
              << opportunity.signals().size() << "\n";

    std::cout << "  Evidence strength: "
              << std::fixed
              << std::setprecision(2)
              << opportunity.evidenceStrength()
              << "/10\n";

    std::cout << "  TAM: ";
    printCurrency(opportunity.tamValue);
    std::cout << "\n";

    std::cout << "  SAM: ";
    printCurrency(opportunity.samValue);
    std::cout << "\n";

    std::cout << "  Expected value: ";
    printCurrency(opportunity.expectedValue);
    std::cout << "\n";

    std::cout << "  Score: "
              << std::fixed
              << std::setprecision(3)
              << opportunity.score
              << "/10\n";
}

std::vector<CustomerSignal> createSignals() {
    return {
        {
            "ANA-101",
            "product-analytics",
            "New accounts frequently stop before completing the first meaningful workflow.",
            OpportunityCategory::Activation,
            1800,
            1,
            8.5,
            0.96
        },
        {
            "INT-102",
            "customer-interviews",
            "Administrators report uncertainty about the first setup decision.",
            OpportunityCategory::Activation,
            70,
            1,
            8.0,
            0.86
        },
        {
            "SUP-201",
            "support",
            "Customers repeatedly recreate the same operational report.",
            OpportunityCategory::OperationalEfficiency,
            600,
            600,
            7.0,
            0.91
        },
        {
            "INT-202",
            "customer-interviews",
            "Operations teams describe recurring reporting as manual preparation rather than analysis.",
            OpportunityCategory::OperationalEfficiency,
            50,
            1,
            7.5,
            0.82
        },
        {
            "BIL-301",
            "billing-analytics",
            "Qualified users abandon the paid plan selection stage.",
            OpportunityCategory::Monetization,
            900,
            1,
            7.3,
            0.94
        },
        {
            "SAL-302",
            "sales-interviews",
            "Prospects cannot easily connect plan differences to their intended usage.",
            OpportunityCategory::Monetization,
            75,
            1,
            6.8,
            0.80
        }
    };
}

void attachSignals(
    OpportunityRepository& repository,
    const std::vector<CustomerSignal>& signals
) {
    for (const auto& signal : signals) {
        bool attached = false;

        for (const auto& [id, opportunity] : repository.all()) {
            if (opportunity.category == signal.category) {
                repository.get(id).addSignal(signal);
                attached = true;
                break;
            }
        }

        if (!attached) {
            std::cerr
                << "Warning: no opportunity exists for signal "
                << signal.id << "\n";
        }
    }
}

void configureOpportunities(OpportunityRepository& repository) {
    repository.add(ProductOpportunity(
        "OPP-001",
        "Shorten the path to first value",
        "New administrators need too much guidance before reaching a meaningful outcome.",
        "New business accounts",
        OpportunityCategory::Activation,
        {
            24000,
            480,
            0.70,
            0.28
        },
        {
            9.0,
            9.0,
            8.5,
            5.0,
            8.0,
            3.0
        }
    ));

    repository.add(ProductOpportunity(
        "OPP-002",
        "Automate recurring operational reporting",
        "Operations teams spend recurring time preparing reports instead of analyzing them.",
        "Operations-heavy customers",
        OpportunityCategory::OperationalEfficiency,
        {
            9000,
            850,
            0.65,
            0.22
        },
        {
            8.0,
            7.0,
            8.0,
            6.5,
            6.5,
            4.0
        }
    ));

    repository.add(ProductOpportunity(
        "OPP-003",
        "Clarify paid plan selection",
        "Qualified users need clearer connections between plan capabilities and use cases.",
        "Qualified product users",
        OpportunityCategory::Monetization,
        {
            18000,
            1200,
            0.75,
            0.18
        },
        {
            7.5,
            8.5,
            7.5,
            4.5,
            7.5,
            4.5
        }
    ));
}

void calculatePortfolio(
    OpportunityRepository& repository,
    const ScoreWeights& weights
) {
    for (const auto& [id, opportunity] : repository.all()) {
        auto& mutableOpportunity = repository.get(id);

        mutableOpportunity.calculateSize();
        mutableOpportunity.calculateScore(weights);
    }
}

void printEvidenceDetail(
    const OpportunityRepository& repository
) {
    std::cout << "\n=== Evidence traceability ===\n";

    for (const auto& [id, opportunity] : repository.all()) {
        std::cout << "\n" << id << " | "
                  << opportunity.title << "\n";

        for (const auto& signal : opportunity.signals()) {
            std::cout
                << "  " << signal.id
                << " | source=" << signal.source
                << " | affected=" << signal.affectedUsers
                << " | severity=" << signal.severity
                << " | confidence=" << signal.confidence
                << " | strength=" << signal.evidenceStrength()
                << "\n";
        }
    }
}

void printSizingSensitivity(
    const OpportunityRepository& repository
) {
    std::cout << "\n=== Sizing sensitivity ===\n";

    const std::vector<double> adoptionRates{
        0.10, 0.20, 0.30, 0.40, 0.50
    };

    for (const auto& [id, opportunity] : repository.all()) {
        std::cout << "\n"
                  << opportunity.title << "\n";

        const auto scenarios =
            runAdoptionSensitivity(opportunity, adoptionRates);

        for (const auto& scenario : scenarios) {
            std::cout
                << "  adoption="
                << std::fixed
                << std::setprecision(0)
                << scenario.adoptionRate * 100
                << "% -> ";

            printCurrency(scenario.expectedValue);

            std::cout << "\n";
        }
    }
}

void printScoreAnalysis(
    const OpportunityRepository& repository
) {
    std::vector<const ProductOpportunity*> ordered;

    for (const auto& [id, opportunity] : repository.all()) {
        ordered.push_back(&opportunity);
    }

    /*
     * The score ordering is an analysis view. It does not encode feasibility
     * review, strategic constraints, dependencies, qualitative evidence, or
     * unknowns that may sit outside the model.
     */
    std::sort(
        ordered.begin(),
        ordered.end(),
        [](const auto* left, const auto* right) {
            return left->score > right->score;
        }
    );

    std::cout << "\n=== Score analysis ===\n";

    for (const auto* opportunity : ordered) {
        std::cout
            << opportunity->id
            << " | score="
            << std::fixed
            << std::setprecision(3)
            << opportunity->score
            << " | expected=";

        printCurrency(opportunity->expectedValue);

        std::cout << "\n";
    }
}

void demonstrateValidationFailure() {
    std::cout << "\n=== Validation failure demonstration ===\n";

    try {
        SizingModel invalidSizing{
            10000,
            500,
            1.25,
            0.20
        };

        invalidSizing.validate();
    } catch (const std::exception& error) {
        std::cout
            << "Rejected invalid sizing assumption: "
            << error.what()
            << "\n";
    }

    try {
        CustomerSignal invalidSignal{
            "BAD-001",
            "analytics",
            "Impossible confidence value",
            OpportunityCategory::Activation,
            100,
            2,
            7,
            1.5
        };

        invalidSignal.validate();
    } catch (const std::exception& error) {
        std::cout
            << "Rejected invalid evidence: "
            << error.what()
            << "\n";
    }
}

int main() {
    try {
        std::cout
            << "=== Product Opportunity Governance Engine ===\n";

        OpportunityRepository repository;
        configureOpportunities(repository);

        const auto signals = createSignals();
        attachSignals(repository, signals);

        const ScoreWeights weights{
            0.30,
            0.20,
            0.15,
            0.10,
            0.10,
            0.15
        };

        calculatePortfolio(repository, weights);

        std::cout << "\n=== Opportunity portfolio ===\n";

        for (const auto& [id, opportunity] : repository.all()) {
            printOpportunity(opportunity);
        }

        printEvidenceDetail(repository);
        printSizingSensitivity(repository);
        printScoreAnalysis(repository);
        demonstrateValidationFailure();

        std::cout << "\n=== Model interpretation ===\n";
        std::cout
            << "Identification converts observed customer evidence into a "
               "defined problem. Sizing estimates potential scale from explicit "
               "population, value, reach, and adoption assumptions. Scoring "
               "applies a separate prioritization policy.\n";

        std::cout
            << "The implementation keeps these dimensions separate so a large "
               "theoretical opportunity cannot hide weak evidence, excessive "
               "delivery effort, or high risk.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
