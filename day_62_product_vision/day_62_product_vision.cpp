#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

enum class VisionStatus {
    Draft,
    Validated,
    Approved,
    Active,
    Retired
};

enum class Horizon {
    Now,
    Next,
    Future
};

std::string statusName(VisionStatus status) {
    switch (status) {
        case VisionStatus::Draft: return "draft";
        case VisionStatus::Validated: return "validated";
        case VisionStatus::Approved: return "approved";
        case VisionStatus::Active: return "active";
        case VisionStatus::Retired: return "retired";
    }
    return "unknown";
}

std::string horizonName(Horizon horizon) {
    switch (horizon) {
        case Horizon::Now: return "0-12 months";
        case Horizon::Next: return "1-3 years";
        case Horizon::Future: return "3-5 years";
    }
    return "unknown";
}

struct CustomerSegment {
    std::string name;
    std::set<std::string> needs;
    std::set<std::string> painPoints;
};

struct Vision {
    std::string product;
    std::string statement;
    std::string customerValue;
    std::string futureState;
    std::vector<std::string> strategicDirection;
    std::vector<std::string> evidence;
    Horizon horizon;
    VisionStatus status = VisionStatus::Draft;
};

class VisionError : public std::runtime_error {
public:
    explicit VisionError(const std::string& message)
        : std::runtime_error(message) {}
};

class VisionValidator {
public:
    static std::vector<std::string> validate(const Vision& vision) {
        std::vector<std::string> errors;

        if (vision.product.empty()) {
            errors.push_back("Product name is required.");
        }

        if (vision.statement.size() < 30) {
            errors.push_back("Vision statement is too short.");
        }

        if (vision.customerValue.empty()) {
            errors.push_back("Customer value is required.");
        }

        if (vision.futureState.empty()) {
            errors.push_back("Future state is required.");
        }

        if (vision.strategicDirection.empty()) {
            errors.push_back("Strategic direction is required.");
        }

        if (vision.evidence.empty()) {
            errors.push_back("Evidence is required.");
        }

        const std::vector<std::string> implementationTerms{
            "button",
            "database table",
            "screen",
            "api endpoint"
        };

        for (const auto& term : implementationTerms) {
            if (vision.statement.find(term) != std::string::npos) {
                errors.push_back(
                    "Vision must describe outcomes rather than implementation."
                );
                break;
            }
        }

        return errors;
    }
};

class GovernanceEngine {
private:
    std::map<std::string, Vision> visions;

    Vision& find(const std::string& product) {
        auto it = visions.find(product);

        if (it == visions.end()) {
            throw VisionError("Vision not found: " + product);
        }

        return it->second;
    }

public:
    void registerVision(const Vision& vision) {
        auto errors = VisionValidator::validate(vision);

        if (!errors.empty()) {
            throw VisionError(errors.front());
        }

        if (visions.contains(vision.product)) {
            throw VisionError("A vision already exists for this product.");
        }

        visions.emplace(vision.product, vision);
    }

    void validate(const std::string& product) {
        Vision& vision = find(product);

        if (vision.status != VisionStatus::Draft) {
            throw VisionError("Only draft visions can be validated.");
        }

        const auto errors = VisionValidator::validate(vision);

        if (!errors.empty()) {
            throw VisionError(errors.front());
        }

        vision.status = VisionStatus::Validated;
    }

    void approve(const std::string& product) {
        Vision& vision = find(product);

        if (vision.status != VisionStatus::Validated) {
            throw VisionError("Only validated visions can be approved.");
        }

        vision.status = VisionStatus::Approved;
    }

    void activate(const std::string& product) {
        Vision& vision = find(product);

        if (vision.status != VisionStatus::Approved) {
            throw VisionError("Only approved visions can become active.");
        }

        vision.status = VisionStatus::Active;
    }

    void retire(const std::string& product) {
        Vision& vision = find(product);

        if (vision.status != VisionStatus::Active) {
            throw VisionError("Only active visions can be retired.");
        }

        vision.status = VisionStatus::Retired;
    }

    const Vision& get(const std::string& product) const {
        auto it = visions.find(product);

        if (it == visions.end()) {
            throw VisionError("Vision not found: " + product);
        }

        return it->second;
    }
};

class AlignmentEngine {
public:
    static double calculate(
        const Vision& vision,
        const std::set<std::string>& strategicPriorities,
        const std::vector<CustomerSegment>& customers
    ) {
        if (strategicPriorities.empty()) {
            return 0.0;
        }

        std::size_t directionMatches = 0;

        for (const auto& direction : vision.strategicDirection) {
            if (strategicPriorities.contains(direction)) {
                ++directionMatches;
            }
        }

        const double strategyScore =
            static_cast<double>(directionMatches) /
            static_cast<double>(strategicPriorities.size());

        std::set<std::string> customerTerms;

        for (const auto& customer : customers) {
            customerTerms.insert(
                customer.needs.begin(),
                customer.needs.end()
            );
            customerTerms.insert(
                customer.painPoints.begin(),
                customer.painPoints.end()
            );
        }

        std::size_t customerMatches = 0;

        for (const auto& direction : vision.strategicDirection) {
            if (customerTerms.contains(direction)) {
                ++customerMatches;
            }
        }

        // Strategic alignment is deliberately weighted more heavily than
        // textual customer-term overlap because a vision is strategic rather
        // than a keyword-matching exercise.
        const double customerScore =
            static_cast<double>(customerMatches) /
            static_cast<double>(
                std::max<std::size_t>(vision.strategicDirection.size(), 1)
            );

        return (strategyScore * 0.7 + customerScore * 0.3) * 100.0;
    }
};

void printReport(
    const Vision& vision,
    double alignmentScore
) {
    std::cout << "\nPRODUCT VISION GOVERNANCE REPORT\n";
    std::cout << std::string(70, '=') << '\n';
    std::cout << "Product: " << vision.product << '\n';
    std::cout << "Status: " << statusName(vision.status) << '\n';
    std::cout << "Horizon: " << horizonName(vision.horizon) << '\n';
    std::cout << "Vision: " << vision.statement << '\n';
    std::cout << "Customer value: " << vision.customerValue << '\n';
    std::cout << "Future state: " << vision.futureState << '\n';
    std::cout << "Strategic alignment: "
              << std::fixed << std::setprecision(2)
              << alignmentScore << "%\n";
}

int main() {
    try {
        Vision vision{
            "Operations Intelligence Platform",
            "Enable operations teams to make faster, more reliable decisions from a unified understanding of operational conditions.",
            "Customers gain visibility, reduce decision delays, and improve operational reliability.",
            "Operations become measurable and predictable, allowing teams to identify problems early and coordinate action.",
            {
                "customer trust",
                "operational efficiency",
                "data-driven decisions",
                "scalable growth"
            },
            {
                "Customer interviews identify fragmented operational information.",
                "Pilot users report delays caused by manual consolidation.",
                "Managers require consistent operational indicators."
            },
            Horizon::Next
        };

        std::vector<CustomerSegment> customers{
            {
                "Operations teams",
                {"visibility", "speed", "reliability"},
                {"manual work", "decision delays"}
            },
            {
                "Managers",
                {"control", "insight", "predictability"},
                {"unclear priorities", "slow reporting"}
            }
        };

        std::set<std::string> priorities{
            "customer trust",
            "operational efficiency",
            "data-driven decisions",
            "scalable growth"
        };

        GovernanceEngine engine;
        engine.registerVision(vision);
        engine.validate(vision.product);
        engine.approve(vision.product);
        engine.activate(vision.product);

        const Vision& activeVision = engine.get(vision.product);

        const double score = AlignmentEngine::calculate(
            activeVision,
            priorities,
            customers
        );

        printReport(activeVision, score);

        // An invalid state is deliberately tested to verify transition
        // enforcement rather than silently correcting an inconsistent state.
        try {
            engine.activate(vision.product);
        } catch (const VisionError& error) {
            std::cout << "\nExpected transition failure: "
                      << error.what() << '\n';
        }

        Vision invalid{
            "Invalid Product",
            "Add a button and database table.",
            "",
            "",
            {},
            {},
            Horizon::Now
        };

        const auto errors = VisionValidator::validate(invalid);

        std::cout << "Invalid vision errors: "
                  << errors.size() << '\n';

        if (errors.empty()) {
            throw VisionError(
                "Invalid vision unexpectedly passed validation."
            );
        }

    } catch (const VisionError& error) {
        std::cerr << "Governance failure: "
                  << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Unexpected failure: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
