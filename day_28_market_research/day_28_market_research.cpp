/*
 * MARKET RESEARCH CASE STUDY
 *
 * Topic:
 *   Market size, trends, customer segments, industry structure,
 *   and demand analysis.
 *
 * Standard:
 *   C++17 or later
 *
 * Scenario:
 *   An analyst is evaluating an illustrative B2B cloud analytics market.
 *   The program models market definition, segment demand, TAM/SAM/SOM,
 *   historical trends, forecasting, competitive concentration, pricing
 *   elasticity, demand funnels, survey estimates, and scenarios.
 *
 * The implementation intentionally uses only the C++ standard library.
 */

#include <algorithm>
#include <cassert>
#include <cmath>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

// ============================================================================
// 1. BASIC DOMAIN TYPES
// ============================================================================

enum class SegmentType {
    Demographic,
    Geographic,
    Psychographic,
    Behavioral,
    Firmographic,
    NeedBased
};

string segmentTypeName(SegmentType type) {
    switch (type) {
        case SegmentType::Demographic:
            return "Demographic";
        case SegmentType::Geographic:
            return "Geographic";
        case SegmentType::Psychographic:
            return "Psychographic";
        case SegmentType::Behavioral:
            return "Behavioral";
        case SegmentType::Firmographic:
            return "Firmographic";
        case SegmentType::NeedBased:
            return "Need-based";
    }

    return "Unknown";
}

struct MarketDefinition {
    string name;
    string geography;
    string customerType;
    string productScope;
    string period;
    string currency;
};

struct CustomerSegment {
    string name;
    SegmentType type;
    double population;
    double penetration;
    double annualFrequency;
    double averageTransactionValue;
    double growthRate;

    void validate() const {
        if (population < 0) {
            throw invalid_argument("Segment population cannot be negative.");
        }

        if (penetration < 0 || penetration > 1) {
            throw invalid_argument("Segment penetration must be 0..1.");
        }

        if (annualFrequency < 0) {
            throw invalid_argument("Annual frequency cannot be negative.");
        }

        if (averageTransactionValue < 0) {
            throw invalid_argument(
                "Average transaction value cannot be negative."
            );
        }
    }

    double penetratedCustomers() const {
        validate();
        return population * penetration;
    }

    double annualDemandUnits() const {
        validate();
        return penetratedCustomers() * annualFrequency;
    }

    double annualMarketValue() const {
        validate();
        return annualDemandUnits() * averageTransactionValue;
    }
};

struct Competitor {
    string name;
    double marketShare;
    double annualRevenue;
    string positioning;

    void validate() const {
        if (marketShare < 0 || marketShare > 1) {
            throw invalid_argument("Market share must be 0..1.");
        }

        if (annualRevenue < 0) {
            throw invalid_argument("Revenue cannot be negative.");
        }
    }
};

struct HistoricalObservation {
    int year;
    double marketValue;
};

struct DemandObservation {
    double price;
    double quantity;
};

struct Scenario {
    string name;
    double population;
    double penetration;
    double annualSpend;
    double growthRate;

    double marketValue() const {
        if (population < 0) {
            throw invalid_argument("Population cannot be negative.");
        }

        if (penetration < 0 || penetration > 1) {
            throw invalid_argument("Penetration must be 0..1.");
        }

        if (annualSpend < 0) {
            throw invalid_argument("Annual spend cannot be negative.");
        }

        return population * penetration * annualSpend;
    }
};

// ============================================================================
// 2. MARKET SIZE FUNCTIONS
// ============================================================================

double calculateTopDownTAM(
    double totalPopulation,
    double targetPercentage,
    double annualSpendPerCustomer
) {
    if (totalPopulation < 0) {
        throw invalid_argument("Population cannot be negative.");
    }

    if (targetPercentage < 0 || targetPercentage > 1) {
        throw invalid_argument("Target percentage must be 0..1.");
    }

    if (annualSpendPerCustomer < 0) {
        throw invalid_argument("Annual spend cannot be negative.");
    }

    return totalPopulation *
           targetPercentage *
           annualSpendPerCustomer;
}

double calculateBottomUpTAM(
    const vector<CustomerSegment>& segments
) {
    double total = 0.0;

    for (const auto& segment : segments) {
        total += segment.annualMarketValue();
    }

    return total;
}

double calculateSAM(
    double tam,
    double geographicCoverage,
    double productFit
) {
    if (tam < 0) {
        throw invalid_argument("TAM cannot be negative.");
    }

    if (geographicCoverage < 0 || geographicCoverage > 1) {
        throw invalid_argument("Geographic coverage must be 0..1.");
    }

    if (productFit < 0 || productFit > 1) {
        throw invalid_argument("Product fit must be 0..1.");
    }

    return tam * geographicCoverage * productFit;
}

double calculateSOM(
    double sam,
    double achievableShare
) {
    if (sam < 0) {
        throw invalid_argument("SAM cannot be negative.");
    }

    if (achievableShare < 0 || achievableShare > 1) {
        throw invalid_argument("Achievable share must be 0..1.");
    }

    return sam * achievableShare;
}

// ============================================================================
// 3. MARKET TRENDS
// ============================================================================

double calculateCAGR(
    double beginningValue,
    double endingValue,
    int years
) {
    if (beginningValue <= 0 || endingValue <= 0) {
        throw invalid_argument("CAGR values must be positive.");
    }

    if (years <= 0) {
        throw invalid_argument("Years must be positive.");
    }

    return pow(
        endingValue / beginningValue,
        1.0 / static_cast<double>(years)
    ) - 1.0;
}

vector<double> yearOverYearGrowth(
    const vector<HistoricalObservation>& observations
) {
    vector<double> growth;

    if (observations.empty()) {
        return growth;
    }

    growth.push_back(numeric_limits<double>::quiet_NaN());

    for (size_t i = 1; i < observations.size(); ++i) {
        if (observations[i - 1].marketValue == 0) {
            growth.push_back(numeric_limits<double>::quiet_NaN());
        } else {
            growth.push_back(
                (observations[i].marketValue -
                 observations[i - 1].marketValue) /
                observations[i - 1].marketValue
            );
        }
    }

    return growth;
}

double forecastCompoundGrowth(
    double currentValue,
    double annualGrowthRate,
    int years
) {
    if (currentValue < 0) {
        throw invalid_argument("Current value cannot be negative.");
    }

    if (years < 0) {
        throw invalid_argument("Forecast years cannot be negative.");
    }

    return currentValue *
           pow(1.0 + annualGrowthRate, years);
}

// ============================================================================
// 4. INDUSTRY STRUCTURE
// ============================================================================

double calculateHHI(
    const vector<Competitor>& competitors
) {
    double totalShare = 0.0;
    double hhi = 0.0;

    for (const auto& competitor : competitors) {
        competitor.validate();
        totalShare += competitor.marketShare;
        hhi += competitor.marketShare *
               competitor.marketShare;
    }

    if (totalShare > 1.000001) {
        throw invalid_argument(
            "Identified market shares exceed 100%."
        );
    }

    return hhi;
}

double calculateCR4(
    const vector<Competitor>& competitors
) {
    vector<double> shares;

    for (const auto& competitor : competitors) {
        competitor.validate();
        shares.push_back(competitor.marketShare);
    }

    sort(shares.begin(), shares.end(), greater<double>());

    const size_t count = min<size_t>(4, shares.size());

    return accumulate(
        shares.begin(),
        shares.begin() + static_cast<long>(count),
        0.0
    );
}

string concentrationDescription(double hhiDecimal) {
    double hhi = hhiDecimal * 10000.0;

    if (hhi < 1500.0) {
        return "Lower concentration under conventional HHI bands";
    }

    if (hhi < 2500.0) {
        return "Moderate concentration under conventional HHI bands";
    }

    return "Higher concentration under conventional HHI bands";
}

// ============================================================================
// 5. DEMAND AND PRICE ELASTICITY
// ============================================================================

double arcPriceElasticity(
    double oldPrice,
    double newPrice,
    double oldQuantity,
    double newQuantity
) {
    if (oldPrice <= 0 || newPrice <= 0) {
        throw invalid_argument("Prices must be positive.");
    }

    if (oldQuantity < 0 || newQuantity < 0) {
        throw invalid_argument("Quantity cannot be negative.");
    }

    double averagePrice = (oldPrice + newPrice) / 2.0;
    double averageQuantity = (oldQuantity + newQuantity) / 2.0;

    if (averageQuantity == 0) {
        throw invalid_argument(
            "Average quantity cannot be zero."
        );
    }

    double percentagePriceChange =
        (newPrice - oldPrice) / averagePrice;

    double percentageQuantityChange =
        (newQuantity - oldQuantity) / averageQuantity;

    if (percentagePriceChange == 0) {
        throw invalid_argument(
            "Price must change to calculate elasticity."
        );
    }

    return percentageQuantityChange /
           percentagePriceChange;
}

string elasticityClassification(double elasticity) {
    const double magnitude = abs(elasticity);

    if (magnitude > 1.0) {
        return "Elastic";
    }

    if (magnitude < 1.0) {
        return "Inelastic";
    }

    return "Unit elastic";
}

double constantElasticityDemand(
    double baseQuantity,
    double basePrice,
    double newPrice,
    double elasticity
) {
    if (baseQuantity < 0) {
        throw invalid_argument("Base quantity cannot be negative.");
    }

    if (basePrice <= 0 || newPrice <= 0) {
        throw invalid_argument("Prices must be positive.");
    }

    return baseQuantity *
           pow(newPrice / basePrice, elasticity);
}

// ============================================================================
// 6. CUSTOMER FUNNEL
// ============================================================================

double conversionRate(
    int conversions,
    int opportunities
) {
    if (conversions < 0 || opportunities < 0) {
        throw invalid_argument(
            "Funnel counts cannot be negative."
        );
    }

    if (conversions > opportunities) {
        throw invalid_argument(
            "Conversions cannot exceed opportunities."
        );
    }

    if (opportunities == 0) {
        return 0.0;
    }

    return static_cast<double>(conversions) /
           static_cast<double>(opportunities);
}

// ============================================================================
// 7. SURVEY PROPORTION ESTIMATION
// ============================================================================

struct ConfidenceInterval {
    double estimate;
    double lower;
    double upper;
};

ConfidenceInterval proportionConfidenceInterval(
    int successes,
    int sampleSize,
    double zScore = 1.96
) {
    if (sampleSize <= 0) {
        throw invalid_argument(
            "Sample size must be positive."
        );
    }

    if (successes < 0 || successes > sampleSize) {
        throw invalid_argument(
            "Successes must be between zero and sample size."
        );
    }

    double p =
        static_cast<double>(successes) /
        static_cast<double>(sampleSize);

    double standardError =
        sqrt((p * (1.0 - p)) /
             static_cast<double>(sampleSize));

    double lower = max(
        0.0,
        p - zScore * standardError
    );

    double upper = min(
        1.0,
        p + zScore * standardError
    );

    return {p, lower, upper};
}

// ============================================================================
// 8. MARKET ESTIMATE TRIANGULATION
// ============================================================================

struct Estimate {
    string method;
    double value;
};

struct TriangulationResult {
    double mean;
    double median;
    double relativeRange;
};

TriangulationResult triangulate(
    vector<Estimate> estimates
) {
    if (estimates.empty()) {
        throw invalid_argument(
            "At least one estimate is required."
        );
    }

    vector<double> values;

    for (const auto& estimate : estimates) {
        if (estimate.value < 0) {
            throw invalid_argument(
                "Estimate cannot be negative."
            );
        }

        values.push_back(estimate.value);
    }

    double average =
        accumulate(values.begin(), values.end(), 0.0) /
        static_cast<double>(values.size());

    sort(values.begin(), values.end());

    double med;

    if (values.size() % 2 == 0) {
        size_t right = values.size() / 2;
        size_t left = right - 1;
        med = (values[left] + values[right]) / 2.0;
    } else {
        med = values[values.size() / 2];
    }

    double minimum = values.front();
    double maximum = values.back();

    double relativeRange =
        average == 0
            ? 0
            : (maximum - minimum) / average;

    return {average, med, relativeRange};
}

// ============================================================================
// 9. DISPLAY UTILITIES
// ============================================================================

void printCurrency(double value) {
    cout << "$"
         << fixed
         << setprecision(0)
         << value;
}

void printPercent(double value) {
    cout << fixed
         << setprecision(2)
         << value * 100.0
         << "%";
}

// ============================================================================
// 10. CASE STUDY
// ============================================================================

void runCaseStudy() {
    cout << string(78, '=') << '\n';
    cout << "MARKET RESEARCH CASE STUDY\n";
    cout << "Illustrative B2B Cloud Analytics Market\n";
    cout << string(78, '=') << "\n\n";

    MarketDefinition market{
        "Cloud Analytics Platforms",
        "Illustrative regional market",
        "Mid-sized and enterprise organizations",
        "Subscription-based analytics software",
        "2025-2030",
        "USD"
    };

    cout << "1. MARKET DEFINITION\n";
    cout << "Name: " << market.name << '\n';
    cout << "Geography: " << market.geography << '\n';
    cout << "Customer type: " << market.customerType << '\n';
    cout << "Product scope: " << market.productScope << '\n';
    cout << "Period: " << market.period << "\n\n";

    // ------------------------------------------------------------------------
    // Customer segments
    // ------------------------------------------------------------------------

    vector<CustomerSegment> segments{
        {
            "Mid-market technology firms",
            SegmentType::Firmographic,
            18000,
            0.42,
            1.0,
            2400,
            0.12
        },
        {
            "Professional services",
            SegmentType::Firmographic,
            12000,
            0.35,
            1.0,
            1800,
            0.09
        },
        {
            "Large enterprises",
            SegmentType::Firmographic,
            3000,
            0.70,
            1.0,
            18000,
            0.08
        }
    };

    cout << "2. CUSTOMER SEGMENTS\n";

    for (const auto& segment : segments) {
        cout << "\n" << segment.name << '\n';
        cout << "  Type: "
             << segmentTypeName(segment.type)
             << '\n';

        cout << "  Population: "
             << fixed
             << setprecision(0)
             << segment.population
             << '\n';

        cout << "  Penetrated customers: "
             << segment.penetratedCustomers()
             << '\n';

        cout << "  Annual demand units: "
             << segment.annualDemandUnits()
             << '\n';

        cout << "  Annual market value: ";
        printCurrency(segment.annualMarketValue());
        cout << '\n';

        cout << "  Growth assumption: ";
        printPercent(segment.growthRate);
        cout << '\n';
    }

    // ------------------------------------------------------------------------
    // TAM, SAM, SOM
    // ------------------------------------------------------------------------

    double bottomUpTAM =
        calculateBottomUpTAM(segments);

    double topDownTAM =
        calculateTopDownTAM(
            50000,
            0.45,
            5500
        );

    cout << "\n3. MARKET SIZE\n";

    cout << "Bottom-up TAM: ";
    printCurrency(bottomUpTAM);
    cout << '\n';

    cout << "Top-down TAM: ";
    printCurrency(topDownTAM);
    cout << '\n';

    TriangulationResult triangulation =
        triangulate({
            {"Bottom-up", bottomUpTAM},
            {"Top-down", topDownTAM}
        });

    cout << "Triangulation mean: ";
    printCurrency(triangulation.mean);
    cout << '\n';

    cout << "Triangulation median: ";
    printCurrency(triangulation.median);
    cout << '\n';

    cout << "Relative range: ";
    printPercent(triangulation.relativeRange);
    cout << '\n';

    double sam =
        calculateSAM(
            bottomUpTAM,
            0.65,
            0.80
        );

    double som =
        calculateSOM(
            sam,
            0.08
        );

    cout << "SAM: ";
    printCurrency(sam);
    cout << '\n';

    cout << "SOM: ";
    printCurrency(som);
    cout << "\n\n";

    // ------------------------------------------------------------------------
    // Historical trends
    // ------------------------------------------------------------------------

    cout << "4. MARKET TRENDS\n";

    vector<HistoricalObservation> history{
        {2022, 82000000},
        {2023, 91000000},
        {2024, 104000000},
        {2025, 119000000}
    };

    vector<double> growth =
        yearOverYearGrowth(history);

    for (size_t i = 0; i < history.size(); ++i) {
        cout << history[i].year << ": ";
        printCurrency(history[i].marketValue);
        cout << ", growth=";

        if (isnan(growth[i])) {
            cout << "N/A";
        } else {
            printPercent(growth[i]);
        }

        cout << '\n';
    }

    double cagr =
        calculateCAGR(
            history.front().marketValue,
            history.back().marketValue,
            3
        );

    cout << "2022-2025 CAGR: ";
    printPercent(cagr);
    cout << '\n';

    double forecast2030 =
        forecastCompoundGrowth(
            history.back().marketValue,
            cagr,
            5
        );

    cout << "Illustrative constant-CAGR 2030 scenario: ";
    printCurrency(forecast2030);
    cout << "\n\n";

    // ------------------------------------------------------------------------
    // Competitive structure
    // ------------------------------------------------------------------------

    cout << "5. INDUSTRY STRUCTURE\n";

    vector<Competitor> competitors{
        {
            "Alpha Analytics",
            0.28,
            33320000,
            "Enterprise suite"
        },
        {
            "Beta Data",
            0.21,
            24990000,
            "Mid-market platform"
        },
        {
            "Gamma Cloud",
            0.14,
            16660000,
            "Cloud-native platform"
        },
        {
            "Delta Systems",
            0.09,
            10710000,
            "Integrated software"
        },
        {
            "Other identified firms",
            0.16,
            19040000,
            "Fragmented"
        }
    };

    double identifiedShare =
        accumulate(
            competitors.begin(),
            competitors.end(),
            0.0,
            [](double total, const Competitor& competitor) {
                return total + competitor.marketShare;
            }
        );

    double residualShare =
        max(0.0, 1.0 - identifiedShare);

    double hhi =
        calculateHHI(competitors);

    double cr4 =
        calculateCR4(competitors);

    cout << "Identified share: ";
    printPercent(identifiedShare);
    cout << '\n';

    cout << "Residual share: ";
    printPercent(residualShare);
    cout << '\n';

    cout << "CR4: ";
    printPercent(cr4);
    cout << '\n';

    cout << "HHI: "
         << fixed
         << setprecision(0)
         << hhi * 10000.0
         << '\n';

    cout << "Descriptive concentration band: "
         << concentrationDescription(hhi)
         << "\n\n";

    // ------------------------------------------------------------------------
    // Demand and pricing
    // ------------------------------------------------------------------------

    cout << "6. DEMAND ANALYSIS\n";

    double elasticity =
        arcPriceElasticity(
            2000,
            2200,
            10000,
            9200
        );

    cout << "Arc price elasticity: "
         << fixed
         << setprecision(3)
         << elasticity
         << '\n';

    cout << "Elasticity classification: "
         << elasticityClassification(elasticity)
         << '\n';

    double modeledQuantity =
        constantElasticityDemand(
            10000,
            2000,
            2500,
            elasticity
        );

    cout << "Modeled quantity at $2,500: "
         << fixed
         << setprecision(0)
         << modeledQuantity
         << "\n\n";

    // ------------------------------------------------------------------------
    // Funnel
    // ------------------------------------------------------------------------

    cout << "7. DEMAND FUNNEL\n";

    const int leads = 5000;
    const int qualified = 1600;
    const int trials = 800;
    const int customers = 160;

    cout << "Lead -> qualified: ";
    printPercent(conversionRate(qualified, leads));
    cout << '\n';

    cout << "Qualified -> trial: ";
    printPercent(conversionRate(trials, qualified));
    cout << '\n';

    cout << "Trial -> customer: ";
    printPercent(conversionRate(customers, trials));
    cout << '\n';

    cout << "Lead -> customer: ";
    printPercent(conversionRate(customers, leads));
    cout << "\n\n";

    // ------------------------------------------------------------------------
    // Survey analysis
    // ------------------------------------------------------------------------

    cout << "8. SURVEY ESTIMATION\n";

    ConfidenceInterval interval =
        proportionConfidenceInterval(
            420,
            1000
        );

    cout << "Observed adoption: ";
    printPercent(interval.estimate);
    cout << '\n';

    cout << "Approximate 95% interval: ";
    printPercent(interval.lower);
    cout << " to ";
    printPercent(interval.upper);
    cout << "\n\n";

    // ------------------------------------------------------------------------
    // Scenario analysis
    // ------------------------------------------------------------------------

    cout << "9. SCENARIO ANALYSIS\n";

    vector<Scenario> scenarios{
        {
            "Conservative",
            30000,
            0.20,
            1500,
            0.05
        },
        {
            "Base",
            30000,
            0.30,
            2000,
            0.10
        },
        {
            "Expansion",
            30000,
            0.40,
            2500,
            0.15
        }
    };

    for (const auto& scenario : scenarios) {
        cout << scenario.name << ": ";
        printCurrency(scenario.marketValue());
        cout << ", growth=";
        printPercent(scenario.growthRate);
        cout << '\n';
    }

    // ------------------------------------------------------------------------
    // Failure conditions and edge cases
    // ------------------------------------------------------------------------

    cout << "\n10. EDGE CASE VALIDATION\n";

    try {
        calculateSAM(
            100000,
            1.2,
            0.8
        );
    } catch (const exception& error) {
        cout << "Invalid geographic coverage rejected: "
             << error.what()
             << '\n';
    }

    try {
        arcPriceElasticity(
            100,
            100,
            1000,
            900
        );
    } catch (const exception& error) {
        cout << "Unchanged price rejected: "
             << error.what()
             << '\n';
    }

    cout << "\nCase study complete.\n";
}

// ============================================================================
// 11. SELF-TESTS
// ============================================================================

void runSelfTests() {
    assert(
        abs(
            calculateTopDownTAM(
                1000,
                0.5,
                100
            ) - 50000.0
        ) < 1e-9
    );

    assert(
        abs(
            calculateSAM(
                100000,
                0.5,
                0.8
            ) - 40000.0
        ) < 1e-9
    );

    assert(
        abs(
            calculateSOM(
                40000,
                0.1
            ) - 4000.0
        ) < 1e-9
    );

    assert(
        abs(
            calculateCAGR(
                100,
                121,
                2
            ) - 0.10
        ) < 1e-9
    );

    vector<Competitor> testCompetitors{
        {"A", 0.50, 0, ""},
        {"B", 0.50, 0, ""}
    };

    assert(
        abs(
            calculateHHI(testCompetitors) - 0.50
        ) < 1e-9
    );

    assert(
        abs(
            calculateCR4(testCompetitors) - 1.0
        ) < 1e-9
    );

    assert(
        abs(
            conversionRate(20, 100) - 0.20
        ) < 1e-9
    );

    CustomerSegment segment{
        "Test",
        SegmentType::Behavioral,
        1000,
        0.20,
        2.0,
        50,
        0
    };

    assert(
        abs(
            segment.annualMarketValue() - 20000.0
        ) < 1e-9
    );

    cout << "All C++ self-tests passed.\n";
}

// ============================================================================
// 12. MAIN
// ============================================================================

int main() {
    try {
        runSelfTests();
        runCaseStudy();
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
