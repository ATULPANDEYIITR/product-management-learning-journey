/*
 * Competitive Intelligence: Industry-Style C++ Case Study
 *
 * Scenario
 * --------
 * A fictional software company is building a competitive-intelligence
 * monitoring platform for business customers.
 *
 * The system collects structured competitor information, analyzes:
 * - competitor type
 * - product capabilities
 * - pricing
 * - customer reviews
 * - website traffic indicators
 * - traffic growth
 * - evidence quality
 * - capability gaps
 * - strategic opportunities
 *
 * The program uses only the C++17 standard library.
 *
 * All company names and numeric values are fictional demonstration data.
 *
 * Compile:
 *   g++ -std=c++17 -O2 competitive_intelligence.cpp -o competitive_intelligence
 *
 * Run:
 *   ./competitive_intelligence
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
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;


// ============================================================================
// 1. ENUMERATIONS
// ============================================================================

enum class CompetitorType {
    Direct,
    Indirect,
    Potential
};

enum class EvidenceQuality {
    High,
    Medium,
    Low
};

string toString(CompetitorType type) {
    switch (type) {
        case CompetitorType::Direct:
            return "Direct";
        case CompetitorType::Indirect:
            return "Indirect";
        case CompetitorType::Potential:
            return "Potential";
    }

    return "Unknown";
}

string toString(EvidenceQuality quality) {
    switch (quality) {
        case EvidenceQuality::High:
            return "High";
        case EvidenceQuality::Medium:
            return "Medium";
        case EvidenceQuality::Low:
            return "Low";
    }

    return "Unknown";
}

double reliabilityWeight(EvidenceQuality quality) {
    switch (quality) {
        case EvidenceQuality::High:
            return 1.0;
        case EvidenceQuality::Medium:
            return 0.7;
        case EvidenceQuality::Low:
            return 0.4;
    }

    return 0.0;
}


// ============================================================================
// 2. DOMAIN OBJECTS
// ============================================================================

struct Evidence {
    string source;
    string observation;
    EvidenceQuality quality;
    string collectedDate;
};

struct Review {
    double rating;
    string text;
    string source;
};

struct PricingPlan {
    string name;
    double monthlyPrice;
    double annualDiscount;
    int includedUnits;

    double annualEffectiveMonthlyPrice() const {
        return monthlyPrice * (1.0 - annualDiscount);
    }
};

struct Competitor {
    string name;
    CompetitorType type;
    string segment;
    string targetCustomer;
    string positioning;

    double websiteVisitsMillions;
    double trafficGrowthPercent;

    double estimatedFundingMillions;
    int employeeCount;

    vector<PricingPlan> plans;
    map<string, double> features;
    vector<Review> reviews;
    vector<Evidence> evidence;

    double entryPrice() const {
        if (plans.empty()) {
            return 0.0;
        }

        double result = numeric_limits<double>::max();

        for (const auto& plan : plans) {
            result = min(result, plan.monthlyPrice);
        }

        return result;
    }

    double averageRating() const {
        if (reviews.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& review : reviews) {
            total += review.rating;
        }

        return total / static_cast<double>(reviews.size());
    }

    double averageFeatureScore() const {
        if (features.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& [feature, score] : features) {
            total += score;
        }

        return total / static_cast<double>(features.size());
    }

    double evidenceScore() const {
        if (evidence.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& item : evidence) {
            total += reliabilityWeight(item.quality);
        }

        return 100.0 * total / static_cast<double>(evidence.size());
    }
};


// ============================================================================
// 3. DATA CONSTRUCTION
// ============================================================================

Competitor makeMarketPilot() {
    return {
        "MarketPilot",
        CompetitorType::Direct,
        "SMB intelligence",
        "Small and medium businesses",
        "Affordable competitive monitoring",
        4.8,
        12.0,
        18.0,
        95,
        {
            {"Starter", 49.0, 0.15, 5},
            {"Growth", 129.0, 0.20, 20},
            {"Enterprise", 399.0, 0.25, 100}
        },
        {
            {"competitor_tracking", 9},
            {"pricing_monitoring", 8},
            {"review_analysis", 6},
            {"market_reports", 7},
            {"alerts", 9},
            {"api", 5}
        },
        {
            {4.5, "Easy monitoring and helpful alerts", "ReviewSite"},
            {4.0, "Good pricing but reporting is limited", "ReviewSite"},
            {3.5, "Simple interface but API is confusing", "ReviewSite"}
        },
        {
            {"Company website", "Three commercial tiers", EvidenceQuality::High, "2026-09-27"},
            {"Traffic intelligence", "Growing website traffic", EvidenceQuality::Medium, "2026-09-27"}
        }
    };
}

Competitor makeInsightForge() {
    return {
        "InsightForge",
        CompetitorType::Direct,
        "Enterprise intelligence",
        "Large organizations",
        "Deep enterprise competitive intelligence",
        7.2,
        6.0,
        65.0,
        310,
        {
            {"Professional", 299.0, 0.10, 25},
            {"Enterprise", 899.0, 0.15, 150}
        },
        {
            {"competitor_tracking", 10},
            {"pricing_monitoring", 9},
            {"review_analysis", 8},
            {"market_reports", 10},
            {"alerts", 8},
            {"api", 9}
        },
        {
            {4.3, "Powerful reports but expensive", "ReviewSite"},
            {4.1, "Excellent data but complex setup", "ReviewSite"},
            {3.8, "Useful enterprise features but difficult", "ReviewSite"}
        },
        {
            {"Company website", "Enterprise-oriented plans", EvidenceQuality::High, "2026-09-27"},
            {"Company database", "Substantial funding reported", EvidenceQuality::Medium, "2026-09-27"}
        }
    };
}

Competitor makeReviewLens() {
    return {
        "ReviewLens",
        CompetitorType::Indirect,
        "Customer intelligence",
        "Consumer brands",
        "Customer-review analytics",
        3.1,
        19.0,
        11.0,
        72,
        {
            {"Basic", 39.0, 0.10, 10},
            {"Pro", 99.0, 0.15, 40}
        },
        {
            {"competitor_tracking", 5},
            {"pricing_monitoring", 4},
            {"review_analysis", 10},
            {"market_reports", 6},
            {"alerts", 7},
            {"api", 6}
        },
        {
            {4.6, "Excellent review analysis and easy interface", "ReviewSite"},
            {4.4, "Fast and useful customer insights", "ReviewSite"},
            {4.2, "Great product but missing market reports", "ReviewSite"}
        },
        {
            {"Company website", "Review-centric product", EvidenceQuality::High, "2026-09-27"}
        }
    };
}

Competitor makeDataAtlas() {
    return {
        "DataAtlas",
        CompetitorType::Potential,
        "Business data",
        "Technology companies",
        "Large-scale company and market data",
        9.4,
        3.0,
        120.0,
        620,
        {
            {"Data", 499.0, 0.10, 50},
            {"Enterprise", 1499.0, 0.20, 300}
        },
        {
            {"competitor_tracking", 8},
            {"pricing_monitoring", 5},
            {"review_analysis", 3},
            {"market_reports", 9},
            {"alerts", 6},
            {"api", 10}
        },
        {
            {4.0, "Powerful data but expensive", "ReviewSite"},
            {3.9, "Excellent API but complex", "ReviewSite"},
            {4.1, "Reliable datasets", "ReviewSite"}
        },
        {
            {"Company database", "Large business-data provider", EvidenceQuality::Medium, "2026-09-27"}
        }
    };
}

vector<Competitor> createCompetitors() {
    return {
        makeMarketPilot(),
        makeInsightForge(),
        makeReviewLens(),
        makeDataAtlas()
    };
}


// ============================================================================
// 4. VALIDATION LAYER
// ============================================================================

vector<string> validateCompetitor(const Competitor& competitor) {
    vector<string> errors;

    if (competitor.websiteVisitsMillions < 0) {
        errors.push_back("Website traffic cannot be negative.");
    }

    if (competitor.trafficGrowthPercent < -100) {
        errors.push_back("Traffic growth cannot be below -100%.");
    }

    if (competitor.estimatedFundingMillions < 0) {
        errors.push_back("Funding cannot be negative.");
    }

    if (competitor.employeeCount < 0) {
        errors.push_back("Employee count cannot be negative.");
    }

    for (const auto& plan : competitor.plans) {
        if (plan.monthlyPrice < 0) {
            errors.push_back("Negative price in plan: " + plan.name);
        }

        if (plan.annualDiscount < 0 || plan.annualDiscount > 1) {
            errors.push_back(
                "Invalid annual discount in plan: " + plan.name
            );
        }

        if (plan.includedUnits < 0) {
            errors.push_back(
                "Negative included units in plan: " + plan.name
            );
        }
    }

    for (const auto& review : competitor.reviews) {
        if (review.rating < 0 || review.rating > 5) {
            errors.push_back(
                "Review rating outside 0-5 range."
            );
        }
    }

    for (const auto& [feature, score] : competitor.features) {
        if (score < 0 || score > 10) {
            errors.push_back(
                "Feature score outside 0-10 range: " + feature
            );
        }
    }

    return errors;
}

bool validateAll(const vector<Competitor>& competitors) {
    bool valid = true;

    cout << "\nDATA VALIDATION\n";
    cout << string(80, '-') << "\n";

    for (const auto& competitor : competitors) {
        const auto errors = validateCompetitor(competitor);

        if (errors.empty()) {
            cout << competitor.name << ": OK\n";
        } else {
            valid = false;
            cout << competitor.name << ": FAILED\n";

            for (const auto& error : errors) {
                cout << "  ERROR: " << error << "\n";
            }
        }
    }

    return valid;
}


// ============================================================================
// 5. MARKET CLASSIFICATION
// ============================================================================

void printMarketMap(const vector<Competitor>& competitors) {
    cout << "\nMARKET MAP\n";
    cout << string(100, '-') << "\n";

    cout
        << left
        << setw(18) << "Company"
        << setw(12) << "Type"
        << setw(25) << "Segment"
        << "Positioning\n";

    cout << string(100, '-') << "\n";

    for (const auto& competitor : competitors) {
        cout
            << left
            << setw(18) << competitor.name
            << setw(12) << toString(competitor.type)
            << setw(25) << competitor.segment
            << competitor.positioning
            << "\n";
    }
}


// ============================================================================
// 6. PRICING ANALYSIS
// ============================================================================

void printPricing(const vector<Competitor>& competitors) {
    cout << "\nPRICING INTELLIGENCE\n";
    cout << string(90, '-') << "\n";

    for (const auto& competitor : competitors) {
        cout << "\n" << competitor.name << "\n";

        for (const auto& plan : competitor.plans) {
            cout
                << "  "
                << left
                << setw(14) << plan.name
                << "Monthly $" << fixed << setprecision(2)
                << setw(8) << plan.monthlyPrice
                << " Annual-effective $" << setw(8)
                << plan.annualEffectiveMonthlyPrice()
                << " Units " << plan.includedUnits
                << "\n";
        }
    }
}


// ============================================================================
// 7. FEATURE ANALYSIS
// ============================================================================

void printFeatureMatrix(const vector<Competitor>& competitors) {
    const vector<string> features = {
        "competitor_tracking",
        "pricing_monitoring",
        "review_analysis",
        "market_reports",
        "alerts",
        "api"
    };

    cout << "\nFEATURE MATRIX\n";
    cout << string(110, '-') << "\n";

    cout << left << setw(18) << "Company";

    for (const auto& feature : features) {
        cout << setw(20) << feature;
    }

    cout << "\n";

    for (const auto& competitor : competitors) {
        cout << left << setw(18) << competitor.name;

        for (const auto& feature : features) {
            auto iterator = competitor.features.find(feature);

            double score =
                iterator == competitor.features.end()
                    ? 0.0
                    : iterator->second;

            cout << setw(20) << fixed << setprecision(1) << score;
        }

        cout << "\n";
    }
}


// ============================================================================
// 8. REVIEW ANALYSIS
// ============================================================================

set<string> tokenize(const string& text) {
    set<string> words;
    string current;

    for (char character : text) {
        if (isalpha(static_cast<unsigned char>(character))) {
            current += static_cast<char>(
                tolower(static_cast<unsigned char>(character))
            );
        } else if (!current.empty()) {
            words.insert(current);
            current.clear();
        }
    }

    if (!current.empty()) {
        words.insert(current);
    }

    return words;
}

string classifyReviewSentiment(const Review& review) {
    const set<string> positiveWords = {
        "easy", "fast", "excellent", "helpful", "simple",
        "great", "reliable", "useful", "intuitive", "good", "powerful"
    };

    const set<string> negativeWords = {
        "slow", "expensive", "confusing", "difficult", "poor",
        "limited", "buggy", "complex", "missing", "bad"
    };

    const auto words = tokenize(review.text);

    int positive = 0;
    int negative = 0;

    for (const auto& word : words) {
        if (positiveWords.count(word)) {
            ++positive;
        }

        if (negativeWords.count(word)) {
            ++negative;
        }
    }

    if (positive > negative) {
        return "positive";
    }

    if (negative > positive) {
        return "negative";
    }

    return "neutral";
}

void printReviewAnalysis(const vector<Competitor>& competitors) {
    cout << "\nCUSTOMER REVIEW ANALYSIS\n";
    cout << string(90, '-') << "\n";

    for (const auto& competitor : competitors) {
        int positive = 0;

        for (const auto& review : competitor.reviews) {
            if (classifyReviewSentiment(review) == "positive") {
                ++positive;
            }
        }

        double ratio =
            competitor.reviews.empty()
                ? 0.0
                : static_cast<double>(positive)
                    / static_cast<double>(competitor.reviews.size());

        cout
            << left
            << setw(18) << competitor.name
            << "Rating " << fixed << setprecision(2)
            << competitor.averageRating()
            << "  Positive ratio "
            << setprecision(1)
            << ratio * 100.0
            << "%\n";

        for (const auto& review : competitor.reviews) {
            cout
                << "  "
                << review.rating
                << "/5 "
                << classifyReviewSentiment(review)
                << ": "
                << review.text
                << "\n";
        }
    }
}


// ============================================================================
// 9. NORMALIZATION
// ============================================================================

vector<double> minMaxNormalize(const vector<double>& values) {
    if (values.empty()) {
        return {};
    }

    auto [minimumIterator, maximumIterator] =
        minmax_element(values.begin(), values.end());

    const double minimum = *minimumIterator;
    const double maximum = *maximumIterator;

    if (minimum == maximum) {
        return vector<double>(values.size(), 50.0);
    }

    vector<double> normalized;

    normalized.reserve(values.size());

    for (double value : values) {
        normalized.push_back(
            100.0 * (value - minimum) / (maximum - minimum)
        );
    }

    return normalized;
}


// ============================================================================
// 10. POSITIONING ANALYSIS
// ============================================================================

void printPositioning(const vector<Competitor>& competitors) {
    vector<double> featureScores;
    vector<double> prices;

    for (const auto& competitor : competitors) {
        featureScores.push_back(competitor.averageFeatureScore());
        prices.push_back(competitor.entryPrice());
    }

    const auto normalizedFeatures =
        minMaxNormalize(featureScores);

    const auto normalizedPrices =
        minMaxNormalize(prices);

    cout << "\nPOSITIONING MATRIX\n";
    cout << string(70, '-') << "\n";

    cout
        << left
        << setw(18) << "Company"
        << setw(20) << "Feature Index"
        << setw(20) << "Price Index"
        << "\n";

    for (size_t index = 0; index < competitors.size(); ++index) {
        cout
            << left
            << setw(18) << competitors[index].name
            << setw(20) << fixed << setprecision(2)
            << normalizedFeatures[index]
            << setw(20)
            << normalizedPrices[index]
            << "\n";
    }
}


// ============================================================================
// 11. OPPORTUNITY GAP ANALYSIS
// ============================================================================

struct Opportunity {
    string capability;
    double averageCapability;
    double gap;
    double strategicImportance;
    double evidenceStrength;
    double score;
};

vector<Opportunity> calculateOpportunities(
    const vector<Competitor>& competitors
) {
    const vector<string> capabilities = {
        "competitor_tracking",
        "pricing_monitoring",
        "review_analysis",
        "market_reports",
        "alerts",
        "api"
    };

    const map<string, double> importance = {
        {"competitor_tracking", 0.90},
        {"pricing_monitoring", 1.00},
        {"review_analysis", 0.90},
        {"market_reports", 0.80},
        {"alerts", 0.70},
        {"api", 0.85}
    };

    vector<Opportunity> opportunities;

    double evidenceStrength = 0.0;

    for (const auto& competitor : competitors) {
        evidenceStrength += competitor.evidenceScore();
    }

    if (!competitors.empty()) {
        evidenceStrength /= competitors.size();
        evidenceStrength /= 100.0;
    }

    for (const auto& capability : capabilities) {
        double total = 0.0;

        for (const auto& competitor : competitors) {
            auto iterator = competitor.features.find(capability);

            if (iterator != competitor.features.end()) {
                total += iterator->second;
            }
        }

        const double average =
            competitors.empty()
                ? 0.0
                : total / static_cast<double>(competitors.size());

        const double gap = max(0.0, 10.0 - average);

        const double score =
            gap * importance.at(capability) * evidenceStrength;

        opportunities.push_back({
            capability,
            average,
            gap,
            importance.at(capability),
            evidenceStrength,
            score
        });
    }

    sort(
        opportunities.begin(),
        opportunities.end(),
        [](const Opportunity& first, const Opportunity& second) {
            return first.score > second.score;
        }
    );

    return opportunities;
}

void printOpportunities(const vector<Opportunity>& opportunities) {
    cout << "\nCAPABILITY GAP ANALYSIS\n";
    cout << string(100, '-') << "\n";

    cout
        << left
        << setw(24) << "Capability"
        << setw(14) << "Average"
        << setw(12) << "Gap"
        << setw(14) << "Importance"
        << setw(14) << "Evidence"
        << "Model Score\n";

    for (const auto& opportunity : opportunities) {
        cout
            << left
            << setw(24) << opportunity.capability
            << setw(14) << fixed << setprecision(2)
            << opportunity.averageCapability
            << setw(12) << opportunity.gap
            << setw(14) << opportunity.strategicImportance
            << setw(14) << opportunity.evidenceStrength
            << opportunity.score
            << "\n";
    }
}


// ============================================================================
// 12. CORRELATION
// ============================================================================

double pearsonCorrelation(
    const vector<double>& x,
    const vector<double>& y
) {
    if (x.size() != y.size() || x.size() < 2) {
        return 0.0;
    }

    const double xMean =
        accumulate(x.begin(), x.end(), 0.0) / x.size();

    const double yMean =
        accumulate(y.begin(), y.end(), 0.0) / y.size();

    double numerator = 0.0;
    double xVariance = 0.0;
    double yVariance = 0.0;

    for (size_t index = 0; index < x.size(); ++index) {
        const double xDifference = x[index] - xMean;
        const double yDifference = y[index] - yMean;

        numerator += xDifference * yDifference;
        xVariance += xDifference * xDifference;
        yVariance += yDifference * yDifference;
    }

    const double denominator =
        sqrt(xVariance * yVariance);

    if (denominator == 0.0) {
        return 0.0;
    }

    return numerator / denominator;
}


// ============================================================================
// 13. SCENARIO MODEL
// ============================================================================

double projectTraffic(
    const Competitor& competitor,
    int years
) {
    const double rate =
        competitor.trafficGrowthPercent / 100.0;

    return competitor.websiteVisitsMillions *
        pow(1.0 + rate, years);
}

void printScenarioAnalysis(
    const vector<Competitor>& competitors,
    int years
) {
    cout << "\nTRAFFIC SCENARIO MODEL\n";
    cout << string(90, '-') << "\n";

    for (const auto& competitor : competitors) {
        const double projected =
            projectTraffic(competitor, years);

        cout
            << left
            << setw(18) << competitor.name
            << "Current "
            << fixed << setprecision(2)
            << setw(8)
            << competitor.websiteVisitsMillions
            << "M  Growth assumption "
            << setw(7)
            << competitor.trafficGrowthPercent
            << "%  "
            << years
            << "-year scenario "
            << projected
            << "M\n";
    }

    cout
        << "\nThe projection is a mathematical scenario, not a forecast.\n";
}


// ============================================================================
// 14. RESEARCH QUALITY AND ETHICAL BOUNDARIES
// ============================================================================

void printResearchRules() {
    cout << "\nCI DATA GOVERNANCE RULES\n";
    cout << string(90, '-') << "\n";

    const vector<string> rules = {
        "Use public, licensed, or explicitly authorized information.",
        "Respect access controls, contractual restrictions, and applicable law.",
        "Do not acquire passwords, confidential documents, or trade secrets.",
        "Do not impersonate people to obtain restricted information.",
        "Record the source and collection date for material observations.",
        "Distinguish observed facts, estimates, assumptions, and interpretation.",
        "Protect internal research data and credentials.",
        "Treat third-party estimates as estimates rather than verified facts."
    };

    for (const auto& rule : rules) {
        cout << "- " << rule << "\n";
    }
}


// ============================================================================
// 15. COMPETITIVE MONITORING SYSTEM
// ============================================================================

class CompetitiveMonitoringSystem {
private:
    vector<Competitor> competitors;

public:
    explicit CompetitiveMonitoringSystem(
        vector<Competitor> input
    )
        : competitors(std::move(input)) {}

    void run() const {
        if (!validateAll(competitors)) {
            throw runtime_error(
                "Input validation failed. Analysis was stopped."
            );
        }

        printMarketMap(competitors);
        printPricing(competitors);
        printFeatureMatrix(competitors);
        printReviewAnalysis(competitors);
        printPositioning(competitors);

        const auto opportunities =
            calculateOpportunities(competitors);

        printOpportunities(opportunities);

        vector<double> traffic;
        vector<double> growth;

        for (const auto& competitor : competitors) {
            traffic.push_back(
                competitor.websiteVisitsMillions
            );

            growth.push_back(
                competitor.trafficGrowthPercent
            );
        }

        cout << "\nSTATISTICAL ANALYSIS\n";
        cout << string(70, '-') << "\n";

        cout
            << "Traffic/growth Pearson correlation: "
            << fixed << setprecision(3)
            << pearsonCorrelation(traffic, growth)
            << "\n";

        cout
            << "Interpretation: this coefficient describes association "
            << "within the supplied sample and does not prove causation.\n";

        printScenarioAnalysis(competitors, 3);
        printResearchRules();
    }
};


// ============================================================================
// 16. EDGE-CASE TESTS
// ============================================================================

void runEdgeCaseTests() {
    cout << "\nEDGE-CASE TESTS\n";
    cout << string(70, '-') << "\n";

    PricingPlan plan{
        "Test",
        100.0,
        0.20,
        10
    };

    if (abs(plan.annualEffectiveMonthlyPrice() - 80.0) < 0.000001) {
        cout << "Annual pricing calculation: PASS\n";
    } else {
        cout << "Annual pricing calculation: FAIL\n";
    }

    const vector<double> identicalValues = {
        5.0,
        5.0,
        5.0
    };

    const auto normalized =
        minMaxNormalize(identicalValues);

    const bool normalizationPassed =
        normalized.size() == 3 &&
        normalized[0] == 50.0 &&
        normalized[1] == 50.0 &&
        normalized[2] == 50.0;

    cout
        << "Constant-value normalization: "
        << (normalizationPassed ? "PASS" : "FAIL")
        << "\n";

    const vector<double> empty;

    const auto emptyResult =
        minMaxNormalize(empty);

    cout
        << "Empty normalization: "
        << (emptyResult.empty() ? "PASS" : "FAIL")
        << "\n";

    Review review{
        4.5,
        "Excellent and easy product",
        "Test"
    };

    cout
        << "Review sentiment: "
        << classifyReviewSentiment(review)
        << "\n";
}


// ============================================================================
// 17. MAIN
// ============================================================================

int main() {
    try {
        cout
            << string(90, '=')
            << "\nCOMPETITIVE INTELLIGENCE INDUSTRY CASE STUDY\n"
            << string(90, '=')
            << "\n";

        auto competitors = createCompetitors();

        runEdgeCaseTests();

        CompetitiveMonitoringSystem system(
            std::move(competitors)
        );

        system.run();

        cout
            << "\nCASE STUDY COMPLETED\n";

        return 0;
    }
    catch (const exception& error) {
        cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
