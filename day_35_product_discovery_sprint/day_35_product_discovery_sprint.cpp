/*
    Product Discovery Sprint
    ------------------------
    C++17 case study: a repository-independent discovery evidence engine for
    a B2B procurement product.

    The system evaluates a discovery portfolio rather than simply calculating
    a feature score. Evidence flows through:

        research evidence
            -> opportunity themes
            -> opportunities
            -> concepts
            -> validation experiments
            -> decision

    The implementation emphasizes C++ domain modeling, unordered containers,
    algorithms, validation, deterministic ranking, and explicit decision rules.

    Compile:
        g++ -std=c++17 -Wall -Wextra -pedantic product_discovery_sprint.cpp -o discovery

    Run:
        ./discovery
*/

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
#include <utility>
#include <vector>

enum class EvidenceType {
    Interview,
    Observation,
    Survey,
    Analytics,
    Support
};

enum class ValidationDecision {
    Continue,
    Iterate,
    Stop
};

std::string to_string(EvidenceType type) {
    switch (type) {
        case EvidenceType::Interview: return "interview";
        case EvidenceType::Observation: return "observation";
        case EvidenceType::Survey: return "survey";
        case EvidenceType::Analytics: return "analytics";
        case EvidenceType::Support: return "support";
    }
    return "unknown";
}

std::string to_string(ValidationDecision decision) {
    switch (decision) {
        case ValidationDecision::Continue: return "continue";
        case ValidationDecision::Iterate: return "iterate";
        case ValidationDecision::Stop: return "stop";
    }
    return "unknown";
}

struct ResearchEvidence {
    std::string id;
    std::string source;
    EvidenceType type;
    std::string participant;
    std::string statement;
    double severity;
    int frequency;
    std::set<std::string> tags;

    double signal() const {
        // Logarithmic frequency prevents a repeated support-ticket observation
        // from completely dominating a high-severity qualitative observation.
        return severity * std::log1p(static_cast<double>(frequency));
    }
};

struct OpportunityTheme {
    std::string id;
    std::string name;
    std::string description;
    std::set<std::string> requiredTags;
    double userImpact;
    double strategicFit;
    std::vector<std::string> evidenceIds;

    double score() const {
        return userImpact * 0.55 + strategicFit * 0.45;
    }
};

struct Opportunity {
    std::string id;
    std::string themeId;
    std::string statement;
    std::string targetBehavior;
    double evidenceStrength;
    double businessValue;
    double feasibility;

    double score() const {
        return evidenceStrength * 0.4
             + businessValue * 0.35
             + feasibility * 0.25;
    }
};

struct Concept {
    std::string id;
    std::string opportunityId;
    std::string name;
    std::string mechanism;
    double confidence;
    double effort;
    double reach;

    double score() const {
        return confidence * reach / std::max(effort, 0.1);
    }
};

struct Experiment {
    std::string id;
    std::string conceptId;
    std::string metric;
    int participants;
    double baseline;
    double observed;
    double threshold;
    double qualitativeSignal;
    ValidationDecision decision;

    double lift() const {
        if (baseline == 0.0) {
            return std::numeric_limits<double>::quiet_NaN();
        }
        return (observed - baseline) / baseline;
    }
};

class DiscoveryEngine {
private:
    std::vector<ResearchEvidence> evidence_;
    std::vector<OpportunityTheme> themes_;
    std::vector<Opportunity> opportunities_;
    std::vector<Concept> concepts_;
    std::vector<Experiment> experiments_;

    static void validate_probability(double value, const std::string& name) {
        if (!std::isfinite(value) || value < 0.0 || value > 1.0) {
            throw std::invalid_argument(name + " must be between 0 and 1");
        }
    }

    static bool hasAnyTag(
        const std::set<std::string>& evidenceTags,
        const std::set<std::string>& requestedTags
    ) {
        for (const auto& tag : requestedTags) {
            if (evidenceTags.count(tag) > 0) {
                return true;
            }
        }
        return false;
    }

public:
    void addEvidence(ResearchEvidence item) {
        if (item.id.empty() || item.source.empty() || item.statement.empty()) {
            throw std::invalid_argument("Evidence requires id, source, and statement");
        }

        validate_probability(item.severity, "severity");

        if (item.frequency <= 0) {
            throw std::invalid_argument("Evidence frequency must be positive");
        }

        evidence_.push_back(std::move(item));
    }

    void addTheme(
        std::string id,
        std::string name,
        std::string description,
        std::set<std::string> tags,
        double userImpact,
        double strategicFit
    ) {
        if (id.empty() || name.empty() || description.empty() || tags.empty()) {
            throw std::invalid_argument("Theme metadata cannot be empty");
        }

        if (userImpact < 0 || userImpact > 10 ||
            strategicFit < 0 || strategicFit > 10) {
            throw std::invalid_argument("Theme scores must be within 0-10");
        }

        OpportunityTheme theme{
            std::move(id),
            std::move(name),
            std::move(description),
            std::move(tags),
            userImpact,
            strategicFit,
            {}
        };

        for (const auto& observation : evidence_) {
            if (hasAnyTag(observation.tags, theme.requiredTags)) {
                theme.evidenceIds.push_back(observation.id);
            }
        }

        if (theme.evidenceIds.empty()) {
            throw std::logic_error(
                "A discovery theme cannot be created without supporting evidence"
            );
        }

        themes_.push_back(std::move(theme));
    }

    Opportunity& addOpportunity(
        std::string id,
        std::string themeId,
        std::string statement,
        std::string targetBehavior,
        double evidenceStrength,
        double businessValue,
        double feasibility
    ) {
        auto themeIt = std::find_if(
            themes_.begin(),
            themes_.end(),
            [&](const auto& theme) { return theme.id == themeId; }
        );

        if (themeIt == themes_.end()) {
            throw std::invalid_argument("Opportunity references an unknown theme");
        }

        if (statement.empty() || targetBehavior.empty()) {
            throw std::invalid_argument("Opportunity must define a problem and behavior");
        }

        if (evidenceStrength < 0 || evidenceStrength > 10 ||
            businessValue < 0 || businessValue > 10 ||
            feasibility < 0 || feasibility > 10) {
            throw std::invalid_argument("Opportunity scores must be within 0-10");
        }

        opportunities_.push_back({
            std::move(id),
            std::move(themeId),
            std::move(statement),
            std::move(targetBehavior),
            evidenceStrength,
            businessValue,
            feasibility
        });

        return opportunities_.back();
    }

    Concept& addConcept(
        std::string id,
        std::string opportunityId,
        std::string name,
        std::string mechanism,
        double confidence,
        double effort,
        double reach
    ) {
        const bool exists = std::any_of(
            opportunities_.begin(),
            opportunities_.end(),
            [&](const auto& opportunity) {
                return opportunity.id == opportunityId;
            }
        );

        if (!exists) {
            throw std::invalid_argument("Concept references an unknown opportunity");
        }

        validate_probability(confidence, "concept confidence");

        if (effort <= 0.0 || reach < 0.0 || reach > 10.0) {
            throw std::invalid_argument("Invalid concept effort or reach");
        }

        concepts_.push_back({
            std::move(id),
            std::move(opportunityId),
            std::move(name),
            std::move(mechanism),
            confidence,
            effort,
            reach
        });

        return concepts_.back();
    }

    Experiment& validateConcept(
        std::string id,
        std::string conceptId,
        std::string metric,
        int participants,
        double baseline,
        double observed,
        double threshold,
        double qualitativeSignal
    ) {
        const bool conceptExists = std::any_of(
            concepts_.begin(),
            concepts_.end(),
            [&](const auto& concept) { return concept.id == conceptId; }
        );

        if (!conceptExists) {
            throw std::invalid_argument("Experiment references an unknown concept");
        }

        if (participants < 5) {
            throw std::invalid_argument(
                "This discovery model requires at least five validation participants"
            );
        }

        validate_probability(baseline, "baseline");
        validate_probability(observed, "observed");
        validate_probability(threshold, "threshold");
        validate_probability(qualitativeSignal, "qualitative signal");

        ValidationDecision decision;

        const bool quantitativePass = observed >= threshold;
        const bool qualitativePass = qualitativeSignal >= 0.65;

        if (quantitativePass && qualitativePass) {
            decision = ValidationDecision::Continue;
        } else if (quantitativePass || qualitativePass) {
            decision = ValidationDecision::Iterate;
        } else {
            decision = ValidationDecision::Stop;
        }

        experiments_.push_back({
            std::move(id),
            std::move(conceptId),
            std::move(metric),
            participants,
            baseline,
            observed,
            threshold,
            qualitativeSignal,
            decision
        });

        return experiments_.back();
    }

    std::vector<OpportunityTheme> rankedThemes() const {
        auto result = themes_;
        std::sort(
            result.begin(),
            result.end(),
            [](const auto& left, const auto& right) {
                return left.score() > right.score();
            }
        );
        return result;
    }

    std::vector<Opportunity> rankedOpportunities() const {
        auto result = opportunities_;
        std::sort(
            result.begin(),
            result.end(),
            [](const auto& left, const auto& right) {
                return left.score() > right.score();
            }
        );
        return result;
    }

    std::vector<Concept> rankedConcepts() const {
        auto result = concepts_;
        std::sort(
            result.begin(),
            result.end(),
            [](const auto& left, const auto& right) {
                return left.score() > right.score();
            }
        );
        return result;
    }

    const std::vector<Experiment>& experiments() const {
        return experiments_;
    }

    void printEvidence() const {
        std::cout << "\n=== RESEARCH EVIDENCE ===\n";

        std::map<EvidenceType, int> counts;

        for (const auto& item : evidence_) {
            counts[item.type]++;
        }

        for (const auto& [type, count] : counts) {
            std::cout << std::setw(12)
                      << to_string(type)
                      << " : " << count << '\n';
        }

        std::vector<const ResearchEvidence*> ranked;
        for (const auto& item : evidence_) {
            ranked.push_back(&item);
        }

        std::sort(
            ranked.begin(),
            ranked.end(),
            [](const auto* left, const auto* right) {
                return left->signal() > right->signal();
            }
        );

        std::cout << "\nHighest-signal observations:\n";
        for (const auto* item : ranked) {
            std::cout << "  " << item->id
                      << " | signal=" << std::fixed << std::setprecision(2)
                      << item->signal()
                      << " | " << item->statement << '\n';
        }
    }

    void printThemes() const {
        std::cout << "\n=== OPPORTUNITY THEMES ===\n";

        for (const auto& theme : rankedThemes()) {
            std::cout << theme.id
                      << " | " << theme.name
                      << " | score=" << std::fixed
                      << std::setprecision(2)
                      << theme.score() << '\n';

            std::cout << "  " << theme.description << '\n';
            std::cout << "  Supporting evidence: "
                      << theme.evidenceIds.size() << '\n';
        }
    }

    void printOpportunities() const {
        std::cout << "\n=== OPPORTUNITIES ===\n";

        for (const auto& opportunity : rankedOpportunities()) {
            std::cout << opportunity.id
                      << " | score=" << std::fixed
                      << std::setprecision(2)
                      << opportunity.score() << '\n';

            std::cout << "  " << opportunity.statement << '\n';
            std::cout << "  Desired behavior: "
                      << opportunity.targetBehavior << '\n';
        }
    }

    void printConcepts() const {
        std::cout << "\n=== CONCEPTS ===\n";

        for (const auto& concept : rankedConcepts()) {
            std::cout << concept.id
                      << " | " << concept.name
                      << " | score=" << std::fixed
                      << std::setprecision(2)
                      << concept.score() << '\n';

            std::cout << "  Mechanism: "
                      << concept.mechanism << '\n';
        }
    }

    void printValidation() const {
        std::cout << "\n=== VALIDATION ===\n";

        for (const auto& experiment : experiments_) {
            std::cout << experiment.id
                      << " | concept=" << experiment.conceptId
                      << " | decision="
                      << to_string(experiment.decision)
                      << '\n';

            std::cout << "  Metric: " << experiment.metric
                      << " | observed=" << std::fixed
                      << std::setprecision(1)
                      << experiment.observed * 100.0 << "%"
                      << " | threshold="
                      << experiment.threshold * 100.0 << "%";

            if (std::isnan(experiment.lift())) {
                std::cout << " | lift=undefined";
            } else {
                std::cout << " | lift="
                          << experiment.lift() * 100.0 << "%";
            }

            std::cout << '\n';
        }
    }
};

void loadCaseStudy(DiscoveryEngine& engine) {
    engine.addEvidence({
        "OBS-001",
        "INT-001",
        EvidenceType::Interview,
        "P-001",
        "I compare supplier lead time, MOQ, certification, and price in my own spreadsheet.",
        0.90,
        5,
        {"comparison", "spreadsheet", "manual"}
    });

    engine.addEvidence({
        "OBS-002",
        "OBS-001",
        EvidenceType::Observation,
        "P-001",
        "Buyer opens four supplier pages and copies attributes into a comparison sheet.",
        0.93,
        4,
        {"comparison", "manual"}
    });

    engine.addEvidence({
        "OBS-003",
        "INT-002",
        EvidenceType::Interview,
        "P-002",
        "Urgent requests cause me to reuse known suppliers because verification takes too long.",
        0.84,
        4,
        {"time", "qualification", "existing-supplier"}
    });

    engine.addEvidence({
        "OBS-004",
        "INT-003",
        EvidenceType::Interview,
        "P-003",
        "A low price is irrelevant when certification cannot be verified.",
        0.95,
        3,
        {"qualification", "trust", "evidence"}
    });

    engine.addEvidence({
        "OBS-005",
        "SUP-2026-09",
        EvidenceType::Support,
        "",
        "Support requests repeatedly ask where supplier qualification evidence is stored.",
        0.72,
        18,
        {"qualification", "trust", "evidence"}
    });

    engine.addEvidence({
        "OBS-006",
        "AN-2026-Q3",
        EvidenceType::Analytics,
        "",
        "Supplier pages have repeat visits but low shortlist conversion.",
        0.70,
        1,
        {"discovery", "shortlist"}
    });

    engine.addTheme(
        "THEME-001",
        "Manual comparison burden",
        "Buyers reconstruct comparable supplier information in personal spreadsheets.",
        {"comparison", "manual", "spreadsheet"},
        8.9,
        8.7
    );

    engine.addTheme(
        "THEME-002",
        "Qualification evidence gap",
        "Fragmented qualification evidence slows supplier trust decisions.",
        {"qualification", "trust", "evidence"},
        9.4,
        9.3
    );
}

void runCaseStudy(DiscoveryEngine& engine) {
    auto& comparisonOpportunity = engine.addOpportunity(
        "OPP-001",
        "THEME-001",
        "Procurement managers need comparable supplier evidence without manually reconstructing it.",
        "complete supplier comparisons using normalized evidence",
        8.8,
        8.9,
        7.8
    );

    auto& qualificationOpportunity = engine.addOpportunity(
        "OPP-002",
        "THEME-002",
        "Procurement managers need qualification evidence attached to supplier decisions.",
        "verify qualification before committing research time",
        9.2,
        9.1,
        7.0
    );

    auto& comparisonConcept = engine.addConcept(
        "CON-001",
        comparisonOpportunity.id,
        "Evidence comparison workspace",
        "Normalize supplier attributes and retain the source evidence beside each field.",
        0.82,
        5.0,
        8.5
    );

    auto& qualificationConcept = engine.addConcept(
        "CON-002",
        qualificationOpportunity.id,
        "Qualification evidence ledger",
        "Expose qualification claims with verification state and evidence provenance.",
        0.76,
        6.0,
        8.0
    );

    engine.validateConcept(
        "EXP-001",
        comparisonConcept.id,
        "supplier comparison task completion",
        8,
        0.45,
        0.875,
        0.75,
        0.84
    );

    engine.validateConcept(
        "EXP-002",
        qualificationConcept.id,
        "qualification verification task completion",
        8,
        0.50,
        0.625,
        0.75,
        0.71
    );
}

void demonstrateFailureHandling() {
    std::cout << "\n=== FAILURE HANDLING ===\n";

    DiscoveryEngine isolatedEngine;

    try {
        isolatedEngine.addTheme(
            "THEME-BAD",
            "Unsupported theme",
            "This theme has no evidence.",
            {"unknown-tag"},
            8.0,
            8.0
        );
    } catch (const std::exception& error) {
        std::cout
            << "Theme rejected because evidence traceability is missing: "
            << error.what() << '\n';
    }

    try {
        isolatedEngine.validateConcept(
            "EXP-BAD",
            "CON-UNKNOWN",
            "invalid experiment",
            3,
            0.5,
            0.8,
            0.7,
            0.8
        );
    } catch (const std::exception& error) {
        std::cout
            << "Experiment rejected: "
            << error.what() << '\n';
    }
}

int main() {
    try {
        DiscoveryEngine engine;

        std::cout << "=== PRODUCT DISCOVERY SPRINT ===\n";
        std::cout << "Case study: B2B supplier discovery for procurement teams\n";
        std::cout
            << "Business outcome: reduce comparison effort without reducing trust\n";

        loadCaseStudy(engine);

        std::cout << "\nResearch synthesis is complete. "
                     "Opportunities remain distinct from solutions.\n";

        runCaseStudy(engine);

        engine.printEvidence();
        engine.printThemes();
        engine.printOpportunities();
        engine.printConcepts();
        engine.printValidation();

        demonstrateFailureHandling();

        std::cout << "\n=== DECISION INTERPRETATION ===\n";

        for (const auto& experiment : engine.experiments()) {
            std::cout << experiment.conceptId << ": ";

            switch (experiment.decision) {
                case ValidationDecision::Continue:
                    std::cout
                        << "continue because both quantitative and qualitative "
                           "signals cleared the validation rule.\n";
                    break;

                case ValidationDecision::Iterate:
                    std::cout
                        << "iterate because only one evidence dimension "
                           "cleared the threshold.\n";
                    break;

                case ValidationDecision::Stop:
                    std::cout
                        << "stop because the tested behavior did not clear "
                           "the required evidence threshold.\n";
                    break;
            }
        }

        std::cout << "\n=== TECHNICAL CHARACTERISTICS ===\n";
        std::cout
            << "Evidence clustering: tag intersection over research records\n"
            << "Theme ranking: weighted user impact and strategic fit\n"
            << "Opportunity ranking: evidence, business value, feasibility\n"
            << "Concept ranking: confidence multiplied by reach divided by effort\n"
            << "Validation: quantitative threshold plus qualitative evidence\n"
            << "Complexity: ranking is O(n log n); evidence-theme matching is O(E*T)\n";
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal discovery engine error: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
