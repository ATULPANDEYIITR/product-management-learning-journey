#include <algorithm>
#include <exception>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

enum class MissionType {
    Organizational,
    Product
};

enum class MissionStatus {
    Draft,
    Active,
    Retired
};

std::string toString(MissionType type) {
    switch (type) {
        case MissionType::Organizational:
            return "organizational";
        case MissionType::Product:
            return "product";
    }
    return "unknown";
}

std::string toString(MissionStatus status) {
    switch (status) {
        case MissionStatus::Draft:
            return "draft";
        case MissionStatus::Active:
            return "active";
        case MissionStatus::Retired:
            return "retired";
    }
    return "unknown";
}

class MissionValidationError : public std::runtime_error {
public:
    explicit MissionValidationError(const std::string& message)
        : std::runtime_error(message) {}
};

struct Mission {
    std::string name;
    std::string statement;
    std::string purpose;
    MissionType type;
    MissionStatus status;
    std::set<std::string> strategicThemes;

    void validate() const {
        if (name.empty()) {
            throw MissionValidationError("Mission name cannot be empty.");
        }

        if (statement.empty()) {
            throw MissionValidationError(
                "Mission statement cannot be empty."
            );
        }

        if (purpose.empty()) {
            throw MissionValidationError(
                "Mission purpose cannot be empty."
            );
        }

        if (statement.size() > 300) {
            throw MissionValidationError(
                "Mission statement exceeds 300 characters."
            );
        }

        if (strategicThemes.empty()) {
            throw MissionValidationError(
                "A mission requires at least one strategic theme."
            );
        }
    }
};

struct Product {
    std::string name;
    Mission organizationalMission;
    Mission productMission;
    std::map<std::string, double> metrics;
};

class GovernanceEngine {
public:
    static std::set<std::string> sharedThemes(
        const Mission& organization,
        const Mission& product
    ) {
        organization.validate();
        product.validate();

        if (organization.type != MissionType::Organizational) {
            throw MissionValidationError(
                "Parent mission must be organizational."
            );
        }

        if (product.type != MissionType::Product) {
            throw MissionValidationError(
                "Product mission must have product type."
            );
        }

        std::set<std::string> shared;

        std::set_intersection(
            organization.strategicThemes.begin(),
            organization.strategicThemes.end(),
            product.strategicThemes.begin(),
            product.strategicThemes.end(),
            std::inserter(shared, shared.begin())
        );

        if (shared.empty()) {
            throw MissionValidationError(
                "No shared strategic themes exist between "
                "the organizational and product missions."
            );
        }

        return shared;
    }

    static double purposeAlignment(
        const Mission& mission
    ) {
        std::istringstream statementStream(mission.statement);
        std::istringstream purposeStream(mission.purpose);

        std::set<std::string> statementWords;
        std::set<std::string> purposeWords;

        std::string word;

        while (statementStream >> word) {
            if (word.size() > 3) {
                statementWords.insert(word);
            }
        }

        while (purposeStream >> word) {
            if (word.size() > 3) {
                purposeWords.insert(word);
            }
        }

        if (statementWords.empty() || purposeWords.empty()) {
            return 0.0;
        }

        std::set<std::string> intersection;
        std::set_intersection(
            statementWords.begin(),
            statementWords.end(),
            purposeWords.begin(),
            purposeWords.end(),
            std::inserter(intersection, intersection.begin())
        );

        const double denominator = static_cast<double>(
            std::max(statementWords.size(), purposeWords.size())
        );

        return intersection.size() * 100.0 / denominator;
    }

    static bool isOperationallyHealthy(
        const Product& product
    ) {
        const auto rate = product.metrics.find(
            "successful_transaction_rate"
        );

        const auto satisfaction = product.metrics.find(
            "customer_satisfaction"
        );

        if (rate == product.metrics.end() ||
            satisfaction == product.metrics.end()) {
            return false;
        }

        return rate->second >= 98.0 &&
               satisfaction->second >= 80.0;
    }
};

void writeAuditFile(
    const std::string& filename,
    const Product& product,
    const std::set<std::string>& themes,
    double alignment
) {
    std::ofstream output(filename);

    if (!output) {
        throw std::runtime_error(
            "Unable to create audit file."
        );
    }

    output << "Product Mission Audit\n";
    output << "=====================\n";
    output << "Product: " << product.name << '\n';
    output << "Organizational mission: "
           << product.organizationalMission.statement << '\n';
    output << "Product mission: "
           << product.productMission.statement << '\n';

    output << "Shared themes: ";
    bool first = true;

    for (const auto& theme : themes) {
        if (!first) {
            output << ", ";
        }
        output << theme;
        first = false;
    }

    output << '\n';
    output << std::fixed << std::setprecision(2);
    output << "Purpose alignment: "
           << alignment << "%\n";
    output << "Operational health: "
           << (GovernanceEngine::isOperationallyHealthy(product)
                   ? "healthy"
                   : "attention-required")
           << '\n';
}

int main() {
    try {
        const Mission organizationalMission{
            "Acme Organizational Mission",
            "Improve access to trustworthy digital services by making "
            "essential customer interactions simpler and more reliable.",
            "Deliver dependable services that solve important customer "
            "problems.",
            MissionType::Organizational,
            MissionStatus::Active,
            {
                "customer trust",
                "reliability",
                "simplicity"
            }
        };

        const Mission productMission{
            "Payments Product Mission",
            "Enable customers to complete everyday payments quickly, "
            "clearly, and reliably.",
            "Reduce friction in everyday transactions while preserving "
            "customer trust and reliability.",
            MissionType::Product,
            MissionStatus::Active,
            {
                "customer trust",
                "reliability",
                "simplicity"
            }
        };

        Product payments{
            "Acme Pay",
            organizationalMission,
            productMission,
            {
                {"successful_transaction_rate", 99.2},
                {"payment_completion_time_seconds", 18.5},
                {"customer_satisfaction", 91.4}
            }
        };

        const auto themes = GovernanceEngine::sharedThemes(
            payments.organizationalMission,
            payments.productMission
        );

        const double alignment =
            GovernanceEngine::purposeAlignment(
                payments.productMission
            );

        std::cout << "PRODUCT MISSION GOVERNANCE\n";
        std::cout << "==========================\n";
        std::cout << "Product: " << payments.name << '\n';
        std::cout << "Mission type: "
                  << toString(payments.productMission.type)
                  << '\n';
        std::cout << "Mission status: "
                  << toString(payments.productMission.status)
                  << '\n';

        std::cout << "Shared strategic themes: ";
        for (const auto& theme : themes) {
            std::cout << theme << ' ';
        }
        std::cout << '\n';

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Purpose alignment: "
                  << alignment << "%\n";

        std::cout << "Operational health: "
                  << (GovernanceEngine::isOperationallyHealthy(payments)
                          ? "healthy"
                          : "attention-required")
                  << '\n';

        writeAuditFile(
            "product_mission_audit.txt",
            payments,
            themes,
            alignment
        );

        try {
            Mission invalid{
                "Invalid",
                "",
                "",
                MissionType::Product,
                MissionStatus::Draft,
                {"reliability"}
            };

            invalid.validate();
        } catch (const MissionValidationError& error) {
            std::cout << "\nValidation failure handled: "
                      << error.what() << '\n';
        }

        std::cout << "\nAudit written to product_mission_audit.txt\n";
    }
    catch (const std::exception& error) {
        std::cerr << "Execution failed: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
