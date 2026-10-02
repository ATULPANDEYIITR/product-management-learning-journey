/*
    Porter's Five Forces: Repository-Style Industry Governance Case Study

    Scenario:
    A strategy team is evaluating a regional cloud accounting market before
    committing resources to a new product. The system represents the industry
    as a structured analytical model and evaluates the five forces independently.

    This C++17 case study demonstrates:
    - typed domain modeling with enum classes
    - evidence records
    - force-specific drivers
    - validation
    - weighted analytical scoring
    - scenario changes
    - merge-like transactional evaluation of an analysis revision
    - audit history
    - algorithmic comparison
    - defensive input validation
    - deterministic reporting

    The numerical scores are analyst inputs. They are not empirical facts and
    should not be interpreted as a universal profitability formula.
*/

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

enum class Force {
    Rivalry,
    Suppliers,
    Buyers,
    Substitutes,
    Entrants
};

std::string forceName(Force force) {
    switch (force) {
        case Force::Rivalry:
            return "Competitive Rivalry";
        case Force::Suppliers:
            return "Supplier Bargaining Power";
        case Force::Buyers:
            return "Buyer Bargaining Power";
        case Force::Substitutes:
            return "Threat of Substitutes";
        case Force::Entrants:
            return "Threat of New Entrants";
    }

    throw std::invalid_argument("Unknown force.");
}

const std::vector<Force> FORCE_ORDER{
    Force::Rivalry,
    Force::Suppliers,
    Force::Buyers,
    Force::Substitutes,
    Force::Entrants
};

std::string pressureLevel(double score) {
    if (score < 0.0 || score > 10.0) {
        throw std::out_of_range("Force score must be between 0 and 10.");
    }

    if (score < 3.0) {
        return "Low";
    }

    if (score < 5.0) {
        return "Moderate-Low";
    }

    if (score < 7.0) {
        return "Moderate-High";
    }

    return "High";
}

struct Evidence {
    std::string statement;
    std::string source;
    int direction{};
    double strength{};

    Evidence(
        std::string statement_,
        std::string source_,
        int direction_,
        double strength_
    )
        : statement(std::move(statement_)),
          source(std::move(source_)),
          direction(direction_),
          strength(strength_) {

        if (statement.empty()) {
            throw std::invalid_argument("Evidence statement cannot be empty.");
        }

        if (source.empty()) {
            throw std::invalid_argument("Evidence source cannot be empty.");
        }

        if (direction < -1 || direction > 1) {
            throw std::invalid_argument(
                "Evidence direction must be -1, 0, or 1."
            );
        }

        if (strength <= 0.0 || strength > 1.0) {
            throw std::invalid_argument(
                "Evidence strength must be greater than 0 and at most 1."
            );
        }
    }
};

struct ForceAssessment {
    Force force;
    double score;
    std::string rationale;
    std::vector<Evidence> evidence;

    ForceAssessment(
        Force force_,
        double score_,
        std::string rationale_,
        std::vector<Evidence> evidence_
    )
        : force(force_),
          score(score_),
          rationale(std::move(rationale_)),
          evidence(std::move(evidence_)) {

        if (score < 0.0 || score > 10.0) {
            throw std::out_of_range(
                "Force assessment score must be between 0 and 10."
            );
        }

        if (rationale.empty()) {
            throw std::invalid_argument(
                "Force assessment requires a rationale."
            );
        }
    }
};

struct ScenarioChange {
    Force force;
    double delta;
    std::string reason;
};

struct AuditEntry {
    std::string event;
    Force force;
    double previousScore;
    double newScore;
    std::string reason;
};

class IndustryModel {
private:
    std::string industry_;
    std::string marketDefinition_;
    std::string geography_;
    std::string horizon_;
    std::map<Force, ForceAssessment> assessments_;

public:
    IndustryModel(
        std::string industry,
        std::string marketDefinition,
        std::string geography,
        std::string horizon,
        std::vector<ForceAssessment> assessments
    )
        : industry_(std::move(industry)),
          marketDefinition_(std::move(marketDefinition)),
          geography_(std::move(geography)),
          horizon_(std::move(horizon)) {

        if (industry_.empty() || marketDefinition_.empty()) {
            throw std::invalid_argument(
                "Industry and market definition are required."
            );
        }

        for (auto& assessment : assessments) {
            const auto [iterator, inserted] =
                assessments_.emplace(assessment.force, std::move(assessment));

            if (!inserted) {
                throw std::invalid_argument(
                    "Duplicate force assessment."
                );
            }
        }

        for (Force force : FORCE_ORDER) {
            if (!assessments_.contains(force)) {
                throw std::invalid_argument(
                    "Industry model does not contain all five forces."
                );
            }
        }
    }

    const ForceAssessment& assessment(Force force) const {
        auto iterator = assessments_.find(force);

        if (iterator == assessments_.end()) {
            throw std::out_of_range("Requested force does not exist.");
        }

        return iterator->second;
    }

    ForceAssessment& mutableAssessment(Force force) {
        auto iterator = assessments_.find(force);

        if (iterator == assessments_.end()) {
            throw std::out_of_range("Requested force does not exist.");
        }

        return iterator->second;
    }

    double averagePressure() const {
        double total = 0.0;

        for (Force force : FORCE_ORDER) {
            total += assessment(force).score;
        }

        return total / static_cast<double>(FORCE_ORDER.size());
    }

    Force highestPressureForce() const {
        return *std::max_element(
            FORCE_ORDER.begin(),
            FORCE_ORDER.end(),
            [this](Force left, Force right) {
                return assessment(left).score < assessment(right).score;
            }
        );
    }

    Force lowestPressureForce() const {
        return *std::min_element(
            FORCE_ORDER.begin(),
            FORCE_ORDER.end(),
            [this](Force left, Force right) {
                return assessment(left).score < assessment(right).score;
            }
        );
    }

    const std::string& industry() const {
        return industry_;
    }

    const std::string& marketDefinition() const {
        return marketDefinition_;
    }

    const std::string& geography() const {
        return geography_;
    }

    const std::string& horizon() const {
        return horizon_;
    }
};

/*
    A separate governance layer owns changes to the analytical model.

    This is useful because a strategy model should not allow arbitrary callers
    to modify force scores without recording why the score changed.
*/
class AnalysisGovernance {
private:
    IndustryModel model_;
    std::vector<AuditEntry> auditLog_;

public:
    explicit AnalysisGovernance(IndustryModel model)
        : model_(std::move(model)) {}

    /*
        Applying a scenario is transactional from the caller's perspective:
        all changes are validated first, then committed together.

        If a proposed scenario contains an invalid resulting score, no partial
        update is committed.
    */
    void applyScenario(
        const std::string& scenarioName,
        const std::vector<ScenarioChange>& changes
    ) {
        std::map<Force, double> proposedScores;

        for (Force force : FORCE_ORDER) {
            proposedScores[force] = model_.assessment(force).score;
        }

        for (const auto& change : changes) {
            if (!proposedScores.contains(change.force)) {
                throw std::invalid_argument(
                    "Scenario references an unknown force."
                );
            }

            const double proposed =
                proposedScores[change.force] + change.delta;

            if (proposed < 0.0 || proposed > 10.0) {
                throw std::out_of_range(
                    "Scenario would create a force score outside 0..10."
                );
            }

            proposedScores[change.force] = proposed;
        }

        /*
            Validation has succeeded for the complete scenario. The mutations
            now occur, which prevents an invalid later change from leaving the
            model half-updated.
        */
        for (const auto& change : changes) {
            const double previous =
                model_.mutableAssessment(change.force).score;

            const double updated = proposedScores[change.force];

            model_.mutableAssessment(change.force).score = updated;

            model_.mutableAssessment(change.force).rationale =
                scenarioName + ": " + change.reason;

            auditLog_.push_back({
                scenarioName,
                change.force,
                previous,
                updated,
                change.reason
            });
        }
    }

    const IndustryModel& model() const {
        return model_;
    }

    const std::vector<AuditEntry>& auditLog() const {
        return auditLog_;
    }
};

void printEvidence(const std::vector<Evidence>& evidence) {
    for (const auto& item : evidence) {
        std::string direction;

        if (item.direction > 0) {
            direction = "increases pressure";
        } else if (item.direction < 0) {
            direction = "reduces pressure";
        } else {
            direction = "contextual";
        }

        std::cout
            << "    - " << item.statement
            << " [" << item.source
            << "; " << direction
            << "; strength=" << std::fixed
            << std::setprecision(1) << item.strength << "]\n";
    }
}

void printModel(const IndustryModel& model, const std::string& title) {
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << title << "\n";
    std::cout << std::string(80, '=') << "\n";

    std::cout << "Industry: " << model.industry() << "\n";
    std::cout << "Market: " << model.marketDefinition() << "\n";
    std::cout << "Geography: " << model.geography() << "\n";
    std::cout << "Time horizon: " << model.horizon() << "\n";

    for (Force force : FORCE_ORDER) {
        const auto& assessment = model.assessment(force);

        std::cout << "\n" << forceName(force) << "\n";
        std::cout << "  Score: "
                  << std::fixed << std::setprecision(1)
                  << assessment.score << "/10 ("
                  << pressureLevel(assessment.score) << ")\n";
        std::cout << "  Rationale: "
                  << assessment.rationale << "\n";

        printEvidence(assessment.evidence);
    }

    std::cout << "\nAverage modeled pressure: "
              << std::fixed << std::setprecision(2)
              << model.averagePressure() << "/10\n";

    std::cout << "Highest modeled pressure: "
              << forceName(model.highestPressureForce()) << "\n";

    std::cout << "Lowest modeled pressure: "
              << forceName(model.lowestPressureForce()) << "\n";
}

std::vector<ScenarioChange> automationScenario() {
    return {
        {
            Force::Rivalry,
            0.8,
            "Automation makes basic features easier to reproduce, increasing competition around price and workflow depth."
        },
        {
            Force::Suppliers,
            -0.5,
            "Standardized integrations reduce dependence on individual service providers."
        },
        {
            Force::Buyers,
            0.6,
            "Improved comparison and migration tooling increase buyer negotiating leverage."
        },
        {
            Force::Substitutes,
            0.9,
            "Automated alternatives become more capable of performing parts of the accounting job."
        },
        {
            Force::Entrants,
            0.5,
            "Development becomes easier while trust, distribution, and domain-specific barriers remain."
        }
    };
}

void printSensitivity(const IndustryModel& model) {
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "SENSITIVITY ANALYSIS\n";
    std::cout << std::string(80, '=') << "\n";

    /*
        Changing one force by ±10% changes the average by one-fifth of that
        force's change because the model uses five equally weighted forces.
        This is a mathematical sensitivity calculation, not a forecast.
    */
    for (Force force : FORCE_ORDER) {
        const double current = model.assessment(force).score;
        const double lower = std::max(0.0, current * 0.90);
        const double upper = std::min(10.0, current * 1.10);

        const double lowerAverage =
            (model.averagePressure() * 5.0 - current + lower) / 5.0;

        const double upperAverage =
            (model.averagePressure() * 5.0 - current + upper) / 5.0;

        std::cout << std::left << std::setw(32)
                  << forceName(force)
                  << " average range: "
                  << std::fixed << std::setprecision(2)
                  << lowerAverage << " - "
                  << upperAverage << "\n";
    }
}

void printAuditLog(const AnalysisGovernance& governance) {
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "ANALYSIS CHANGE AUDIT LOG\n";
    std::cout << std::string(80, '=') << "\n";

    for (const auto& entry : governance.auditLog()) {
        std::cout
            << entry.event
            << " | " << forceName(entry.force)
            << " | "
            << std::fixed << std::setprecision(1)
            << entry.previousScore
            << " -> "
            << entry.newScore
            << "\n"
            << "  Reason: "
            << entry.reason
            << "\n";
    }
}

void demonstrateForceSeparation() {
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "FORCE-SPECIFIC MECHANISMS\n";
    std::cout << std::string(80, '=') << "\n";

    const std::vector<std::pair<Force, std::string>> examples{
        {
            Force::Rivalry,
            "Two established firms reduce subscription prices to defend share."
        },
        {
            Force::Suppliers,
            "A specialized financial-data provider increases API charges."
        },
        {
            Force::Buyers,
            "A high-volume customer negotiates lower prices using purchasing scale."
        },
        {
            Force::Substitutes,
            "A customer replaces software with outsourced bookkeeping."
        },
        {
            Force::Entrants,
            "A new provider enters after securing capital and distribution access."
        }
    };

    for (const auto& [force, explanation] : examples) {
        std::cout << forceName(force) << ": "
                  << explanation << "\n";
    }
}

IndustryModel createAccountingModel() {
    return IndustryModel(
        "B2B Cloud Accounting Software",
        "Subscription accounting, invoicing, expense management, and financial reporting for small businesses",
        "India",
        "2026-2030",
        {
            ForceAssessment(
                Force::Rivalry,
                7.2,
                "Several established vendors compete through pricing, integrations, automation, and workflow design.",
                {
                    Evidence(
                        "Customers can compare several cloud accounting products.",
                        "Market observation",
                        1,
                        0.9
                    ),
                    Evidence(
                        "Migration of accounting records can create switching friction.",
                        "Workflow analysis",
                        -1,
                        0.8
                    )
                }
            ),

            ForceAssessment(
                Force::Suppliers,
                4.6,
                "Infrastructure and specialist integration providers create dependencies, but alternative suppliers exist.",
                {
                    Evidence(
                        "Multiple cloud infrastructure providers are available.",
                        "Supplier landscape",
                        -1,
                        0.8
                    ),
                    Evidence(
                        "Specialized financial APIs may have fewer alternatives.",
                        "Integration analysis",
                        1,
                        0.7
                    )
                }
            ),

            ForceAssessment(
                Force::Buyers,
                6.8,
                "Customers can compare prices and features, while migration effort reduces some switching flexibility.",
                {
                    Evidence(
                        "Subscription plans make price comparison straightforward.",
                        "Purchasing analysis",
                        1,
                        0.9
                    ),
                    Evidence(
                        "Historical financial records create migration effort.",
                        "Customer workflow analysis",
                        -1,
                        0.8
                    )
                }
            ),

            ForceAssessment(
                Force::Substitutes,
                5.8,
                "Spreadsheets, desktop systems, and outsourced bookkeeping can perform parts of the same customer job.",
                {
                    Evidence(
                        "Very small businesses can perform basic accounting using spreadsheets.",
                        "Alternative-solution analysis",
                        1,
                        0.8
                    ),
                    Evidence(
                        "Cloud automation connects accounting to broader business workflows.",
                        "Capability analysis",
                        -1,
                        0.8
                    )
                }
            ),

            ForceAssessment(
                Force::Entrants,
                6.1,
                "Software development has modest physical capital requirements, but trust, distribution, integrations, and compliance create barriers.",
                {
                    Evidence(
                        "Cloud products can be launched without physical retail infrastructure.",
                        "Entry analysis",
                        1,
                        0.8
                    ),
                    Evidence(
                        "Established customer relationships create distribution barriers.",
                        "Go-to-market analysis",
                        -1,
                        0.8
                    )
                }
            )
        }
    );
}

int main() {
    try {
        IndustryModel baseline = createAccountingModel();

        printModel(
            baseline,
            "BASELINE: CLOUD ACCOUNTING INDUSTRY STRUCTURE"
        );

        AnalysisGovernance governance(std::move(baseline));

        std::cout << "\n" << std::string(80, '=') << "\n";
        std::cout << "STRUCTURAL SCENARIO TRANSACTION\n";
        std::cout << std::string(80, '=') << "\n";

        /*
            The governance layer validates the complete scenario before
            committing changes. This models a useful discipline in strategic
            analysis: assumptions should change through traceable revisions,
            not through undocumented score edits.
        */
        governance.applyScenario(
            "Automation and Integration Scenario",
            automationScenario()
        );

        printModel(
            governance.model(),
            "AFTER AUTOMATION AND INTEGRATION SCENARIO"
        );

        printSensitivity(governance.model());
        printAuditLog(governance);
        demonstrateForceSeparation();

        std::cout << "\n" << std::string(80, '=') << "\n";
        std::cout << "CASE STUDY COMPLETE\n";
        std::cout << std::string(80, '=') << "\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr << "Analysis failed: "
                  << error.what()
                  << "\n";
        return 1;
    }
}
