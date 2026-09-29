/*
 * TAM / SAM / SOM
 * Total Addressable Market, Serviceable Available Market,
 * Serviceable Obtainable Market
 *
 * C++17 industry-style case study:
 * A hypothetical B2B SaaS analytics company estimates its market,
 * narrows the serviceable population, and calculates an obtainable
 * market under sales, implementation, and support constraints.
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic tam_sam_som.cpp -o tam_sam_som
 *
 * Run:
 *   ./tam_sam_som
 */

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// 1. BASIC UTILITIES
// -----------------------------------------------------------------------------

void requireFiniteNonNegative(double value, const string& name) {
    if (!isfinite(value) || value < 0.0) {
        throw invalid_argument(
            name + " must be finite and non-negative"
        );
    }
}

void requirePercentage(double value, const string& name) {
    if (!isfinite(value) || value < 0.0 || value > 100.0) {
        throw invalid_argument(
            name + " must be between 0 and 100"
        );
    }
}

string currency(double value) {
    ostringstream output;
    output << fixed << setprecision(2)
           << "$" << value;
    return output.str();
}

string compactValue(double value) {
    const double absolute = fabs(value);

    ostringstream output;
    output << fixed << setprecision(2);

    if (absolute >= 1e12) {
        output << value / 1e12 << "T";
    } else if (absolute >= 1e9) {
        output << value / 1e9 << "B";
    } else if (absolute >= 1e6) {
        output << value / 1e6 << "M";
    } else if (absolute >= 1e3) {
        output << value / 1e3 << "K";
    } else {
        output << value;
    }

    return output.str();
}

// -----------------------------------------------------------------------------
// 2. MARKET SIZE
// -----------------------------------------------------------------------------

struct MarketSize {
    double revenue;
    long long customers;

    MarketSize(double revenueValue, long long customerCount)
        : revenue(revenueValue),
          customers(customerCount) {

        requireFiniteNonNegative(
            revenue,
            "Market revenue"
        );

        if (customers < 0) {
            throw invalid_argument(
                "Customer count cannot be negative"
            );
        }
    }

    double revenuePerCustomer() const {
        if (customers == 0) {
            return 0.0;
        }

        return revenue /
               static_cast<double>(customers);
    }
};

// -----------------------------------------------------------------------------
// 3. MARKET SEGMENT
// -----------------------------------------------------------------------------

struct CustomerSegment {
    string name;
    long long customers;
    double annualPrice;
    double adoptionRate;

    MarketSize calculate() const {
        if (customers < 0) {
            throw invalid_argument(
                "Segment customers cannot be negative"
            );
        }

        requireFiniteNonNegative(
            annualPrice,
            "Segment annual price"
        );

        requirePercentage(
            adoptionRate,
            "Segment adoption rate"
        );

        const long long effectiveCustomers =
            static_cast<long long>(
                floor(
                    static_cast<double>(customers) *
                    adoptionRate / 100.0
                )
            );

        return MarketSize(
            static_cast<double>(effectiveCustomers) *
                annualPrice,
            effectiveCustomers
        );
    }
};

// -----------------------------------------------------------------------------
// 4. MARKET CONSTRAINT
// -----------------------------------------------------------------------------

struct MarketConstraint {
    string name;
    double eligibleShare;

    MarketConstraint(
        string constraintName,
        double share
    )
        : name(move(constraintName)),
          eligibleShare(share) {

        requirePercentage(
            eligibleShare,
            "Constraint eligibility"
        );
    }
};

// -----------------------------------------------------------------------------
// 5. CAPACITY MODEL
// -----------------------------------------------------------------------------

struct CapacityModel {
    long long salesRepresentatives;
    long long newCustomersPerRepPerYear;
    long long implementationCapacity;
    long long supportCapacity;

    long long salesCapacity() const {
        return
            salesRepresentatives *
            newCustomersPerRepPerYear;
    }

    long long effectiveCustomerCapacity() const {
        return min({
            salesCapacity(),
            implementationCapacity,
            supportCapacity
        });
    }
};

// -----------------------------------------------------------------------------
// 6. TOP-DOWN MARKET SIZE
// -----------------------------------------------------------------------------

double topDownMarketSize(
    double broadMarketRevenue,
    double segmentShare,
    double geographicShare,
    double productFitShare
) {
    requireFiniteNonNegative(
        broadMarketRevenue,
        "Broad market revenue"
    );

    requirePercentage(
        segmentShare,
        "Segment share"
    );

    requirePercentage(
        geographicShare,
        "Geographic share"
    );

    requirePercentage(
        productFitShare,
        "Product-fit share"
    );

    return
        broadMarketRevenue *
        segmentShare / 100.0 *
        geographicShare / 100.0 *
        productFitShare / 100.0;
}

// -----------------------------------------------------------------------------
// 7. BOTTOM-UP MARKET SIZE
// -----------------------------------------------------------------------------

MarketSize bottomUpMarketSize(
    long long targetCustomers,
    double annualPrice,
    double penetration
) {
    if (targetCustomers < 0) {
        throw invalid_argument(
            "Target customers cannot be negative"
        );
    }

    requireFiniteNonNegative(
        annualPrice,
        "Annual price"
    );

    requirePercentage(
        penetration,
        "Penetration"
    );

    const long long effectiveCustomers =
        static_cast<long long>(
            floor(
                static_cast<double>(targetCustomers) *
                penetration / 100.0
            )
        );

    return MarketSize(
        static_cast<double>(effectiveCustomers) *
            annualPrice,
        effectiveCustomers
    );
}

// -----------------------------------------------------------------------------
// 8. SEGMENTED MARKET
// -----------------------------------------------------------------------------

MarketSize segmentedMarketSize(
    const vector<CustomerSegment>& segments
) {
    long long totalCustomers = 0;
    double totalRevenue = 0.0;

    for (const auto& segment : segments) {
        const MarketSize market =
            segment.calculate();

        totalCustomers += market.customers;
        totalRevenue += market.revenue;
    }

    return MarketSize(
        totalRevenue,
        totalCustomers
    );
}

// -----------------------------------------------------------------------------
// 9. APPLY SAM CONSTRAINTS
// -----------------------------------------------------------------------------

MarketSize applyConstraints(
    const MarketSize& tam,
    const vector<MarketConstraint>& constraints
) {
    double estimatedCustomers =
        static_cast<double>(tam.customers);

    for (const auto& constraint : constraints) {
        /*
         * The percentages are interpreted as conditional eligibility
         * rates. If constraints overlap in reality, multiplying them
         * can be mathematically inappropriate.
         */
        estimatedCustomers *=
            constraint.eligibleShare / 100.0;
    }

    const long long samCustomers =
        static_cast<long long>(
            floor(estimatedCustomers)
        );

    return MarketSize(
        static_cast<double>(samCustomers) *
            tam.revenuePerCustomer(),
        samCustomers
    );
}

// -----------------------------------------------------------------------------
// 10. CAPACITY-CONSTRAINED SOM
// -----------------------------------------------------------------------------

MarketSize calculateSOM(
    const MarketSize& sam,
    const CapacityModel& capacity,
    double strategicShare
) {
    requirePercentage(
        strategicShare,
        "Strategic share"
    );

    const long long desiredCustomers =
        static_cast<long long>(
            floor(
                static_cast<double>(sam.customers) *
                strategicShare / 100.0
            )
        );

    const long long obtainableCustomers =
        min(
            desiredCustomers,
            capacity.effectiveCustomerCapacity()
        );

    return MarketSize(
        static_cast<double>(obtainableCustomers) *
            sam.revenuePerCustomer(),
        obtainableCustomers
    );
}

// -----------------------------------------------------------------------------
// 11. GROWTH PROJECTION
// -----------------------------------------------------------------------------

double compoundGrowth(
    double initialValue,
    double annualGrowthRate,
    int years
) {
    requireFiniteNonNegative(
        initialValue,
        "Initial value"
    );

    if (annualGrowthRate <= -100.0) {
        throw invalid_argument(
            "Growth rate must be above -100%"
        );
    }

    if (years < 0) {
        throw invalid_argument(
            "Years cannot be negative"
        );
    }

    return initialValue *
        pow(
            1.0 + annualGrowthRate / 100.0,
            years
        );
}

vector<double> projectMarket(
    double initialValue,
    double annualGrowthRate,
    int years
) {
    vector<double> result;

    for (int year = 0; year <= years; ++year) {
        result.push_back(
            compoundGrowth(
                initialValue,
                annualGrowthRate,
                year
            )
        );
    }

    return result;
}

// -----------------------------------------------------------------------------
// 12. UNIT ECONOMICS
// -----------------------------------------------------------------------------

struct UnitEconomics {
    double annualRevenuePerCustomer;
    double grossMargin;
    double annualCAC;
    double annualChurnRate;

    double annualGrossProfit() const {
        return
            annualRevenuePerCustomer *
            grossMargin / 100.0;
    }

    double estimatedLifetimeYears() const {
        if (annualChurnRate == 0.0) {
            return numeric_limits<double>::infinity();
        }

        return 1.0 /
               (annualChurnRate / 100.0);
    }

    double estimatedLTV() const {
        const double lifetime =
            estimatedLifetimeYears();

        if (!isfinite(lifetime)) {
            return numeric_limits<double>::infinity();
        }

        return annualGrossProfit() * lifetime;
    }

    double ltvToCAC() const {
        if (annualCAC == 0.0) {
            return numeric_limits<double>::infinity();
        }

        return estimatedLTV() / annualCAC;
    }
};

// -----------------------------------------------------------------------------
// 13. SENSITIVITY ANALYSIS
// -----------------------------------------------------------------------------

struct SensitivityResult {
    string parameter;
    double lowValue;
    double baseValue;
    double highValue;

    double lowOutput;
    double baseOutput;
    double highOutput;
};

template <typename Function>
SensitivityResult sensitivityAnalysis(
    const string& parameter,
    double lowValue,
    double baseValue,
    double highValue,
    Function calculation
) {
    if (!(lowValue <= baseValue &&
          baseValue <= highValue)) {
        throw invalid_argument(
            "Sensitivity values must satisfy "
            "low <= base <= high"
        );
    }

    return {
        parameter,
        lowValue,
        baseValue,
        highValue,
        calculation(lowValue),
        calculation(baseValue),
        calculation(highValue)
    };
}

// -----------------------------------------------------------------------------
// 14. MONTE CARLO SIMULATION
// -----------------------------------------------------------------------------

struct SimulationResult {
    vector<double> samples;
    double minimum;
    double p10;
    double median;
    double p90;
    double maximum;
    double average;
};

double percentile(
    const vector<double>& sortedValues,
    double percent
) {
    if (sortedValues.empty()) {
        throw invalid_argument(
            "Cannot calculate percentile of empty data"
        );
    }

    requirePercentage(
        percent,
        "Percentile"
    );

    const double position =
        (sortedValues.size() - 1) *
        percent / 100.0;

    const size_t lower =
        static_cast<size_t>(
            floor(position)
        );

    const size_t upper =
        static_cast<size_t>(
            ceil(position)
        );

    if (lower == upper) {
        return sortedValues[lower];
    }

    const double fraction =
        position -
        static_cast<double>(lower);

    return
        sortedValues[lower] +
        fraction *
        (
            sortedValues[upper] -
            sortedValues[lower]
        );
}

SimulationResult monteCarloMarketSize(
    int simulations,
    long long minCustomers,
    long long maxCustomers,
    double minPrice,
    double maxPrice,
    double minAdoption,
    double maxAdoption,
    unsigned int seed
) {
    if (simulations <= 0) {
        throw invalid_argument(
            "Simulations must be positive"
        );
    }

    if (minCustomers < 0 ||
        maxCustomers < minCustomers) {
        throw invalid_argument(
            "Invalid customer range"
        );
    }

    if (minPrice < 0 ||
        maxPrice < minPrice) {
        throw invalid_argument(
            "Invalid price range"
        );
    }

    requirePercentage(
        minAdoption,
        "Minimum adoption"
    );

    requirePercentage(
        maxAdoption,
        "Maximum adoption"
    );

    if (maxAdoption < minAdoption) {
        throw invalid_argument(
            "Invalid adoption range"
        );
    }

    mt19937 generator(seed);

    uniform_int_distribution<long long>
        customerDistribution(
            minCustomers,
            maxCustomers
        );

    uniform_real_distribution<double>
        priceDistribution(
            minPrice,
            maxPrice
        );

    uniform_real_distribution<double>
        adoptionDistribution(
            minAdoption,
            maxAdoption
        );

    vector<double> samples;
    samples.reserve(simulations);

    for (int i = 0; i < simulations; ++i) {
        const long long customers =
            customerDistribution(generator);

        const double price =
            priceDistribution(generator);

        const double adoption =
            adoptionDistribution(generator);

        const double market =
            static_cast<double>(customers) *
            price *
            adoption / 100.0;

        samples.push_back(market);
    }

    sort(
        samples.begin(),
        samples.end()
    );

    const double total =
        accumulate(
            samples.begin(),
            samples.end(),
            0.0
        );

    return {
        samples,
        samples.front(),
        percentile(samples, 10),
        percentile(samples, 50),
        percentile(samples, 90),
        samples.back(),
        total / static_cast<double>(
            samples.size()
        )
    };
}

// -----------------------------------------------------------------------------
// 15. REPORTING
// -----------------------------------------------------------------------------

void printSection(const string& title) {
    cout << "\n"
         << string(78, '=')
         << "\n"
         << title
         << "\n"
         << string(78, '=')
         << "\n";
}

void printMarket(
    const string& label,
    const MarketSize& market
) {
    cout << left
         << setw(5) << label
         << " | Customers: "
         << right
         << setw(10)
         << market.customers
         << " | Revenue: "
         << setw(18)
         << currency(market.revenue)
         << " | Revenue/customer: "
         << currency(
                market.revenuePerCustomer()
            )
         << "\n";
}

// -----------------------------------------------------------------------------
// 16. COMPLETE CASE STUDY
// -----------------------------------------------------------------------------

struct CaseStudyResult {
    MarketSize tam;
    MarketSize sam;
    MarketSize som;
};

CaseStudyResult runCaseStudy() {
    printSection(
        "INDUSTRY-STYLE B2B SAAS MARKET-SIZING CASE STUDY"
    );

    /*
     * Business scenario:
     *
     * A hypothetical B2B analytics platform sells annual subscriptions.
     *
     * TAM:
     *   All businesses included in the broad business definition.
     *
     * SAM:
     *   Businesses remaining after geographic, industry, and technology
     *   eligibility constraints.
     *
     * SOM:
     *   The subset that can be targeted and served given the planned
     *   commercial and operational capacity.
     */

    const vector<CustomerSegment> tamSegments = {
        {
            "Small business",
            80'000,
            900.0,
            100.0
        },
        {
            "Mid-market",
            20'000,
            4'000.0,
            100.0
        },
        {
            "Enterprise",
            5'000,
            15'000.0,
            100.0
        }
    };

    // Stage 1: Bottom-up TAM.
    const MarketSize tam =
        segmentedMarketSize(
            tamSegments
        );

    printMarket(
        "TAM",
        tam
    );

    /*
     * Stage 2: SAM.
     *
     * These rates are modeled as conditional eligibility assumptions.
     * In a production model, the analyst should verify whether the
     * constraints are actually independent.
     */
    const vector<MarketConstraint> constraints = {
        {
            "Target geography",
            50.0
        },
        {
            "Target industries",
            60.0
        },
        {
            "Compatible technology",
            70.0
        }
    };

    const MarketSize sam =
        applyConstraints(
            tam,
            constraints
        );

    printMarket(
        "SAM",
        sam
    );

    // Stage 3: SOM through operational capacity.
    const CapacityModel capacity {
        15,
        80,
        1'100,
        1'500
    };

    cout << "\nOperational capacity:\n";
    cout << "Sales capacity: "
         << capacity.salesCapacity()
         << " customers/year\n";

    cout << "Implementation capacity: "
         << capacity.implementationCapacity
         << " customers/year\n";

    cout << "Support capacity: "
         << capacity.supportCapacity
         << " customers/year\n";

    cout << "Effective capacity: "
         << capacity.effectiveCustomerCapacity()
         << " customers/year\n";

    const MarketSize som =
        calculateSOM(
            sam,
            capacity,
            15.0
        );

    printMarket(
        "SOM",
        som
    );

    // Hierarchy validation is deliberately explicit.
    vector<string> warnings;

    if (sam.customers > tam.customers) {
        warnings.push_back(
            "SAM customers exceed TAM customers."
        );
    }

    if (som.customers > sam.customers) {
        warnings.push_back(
            "SOM customers exceed SAM customers."
        );
    }

    if (sam.revenue > tam.revenue) {
        warnings.push_back(
            "SAM revenue exceeds TAM revenue."
        );
    }

    if (som.revenue > sam.revenue) {
        warnings.push_back(
            "SOM revenue exceeds SAM revenue."
        );
    }

    if (warnings.empty()) {
        cout << "\nHierarchy validation: PASSED\n";
    } else {
        cout << "\nHierarchy validation warnings:\n";

        for (const auto& warning : warnings) {
            cout << "- " << warning << "\n";
        }
    }

    return {
        tam,
        sam,
        som
    };
}

// -----------------------------------------------------------------------------
// 17. TOP-DOWN CROSS-CHECK
// -----------------------------------------------------------------------------

void topDownExample() {
    printSection(
        "TOP-DOWN CROSS-CHECK"
    );

    const double broadMarket =
        5'000'000'000.0;

    const double estimate =
        topDownMarketSize(
            broadMarket,
            20.0,
            40.0,
            60.0
        );

    cout << "Broad market: "
         << currency(broadMarket)
         << "\n";

    cout << "Segment share: 20%\n";
    cout << "Geographic share: 40%\n";
    cout << "Product fit: 60%\n";

    cout << "Top-down estimate: "
         << currency(estimate)
         << "\n";

    cout << "\nA top-down estimate is useful as a cross-check, "
         << "but it depends heavily on the definitions and "
         << "quality of the source market.\n";
}

// -----------------------------------------------------------------------------
// 18. UNIT ECONOMICS
// -----------------------------------------------------------------------------

void unitEconomicsExample() {
    printSection(
        "UNIT ECONOMICS"
    );

    const UnitEconomics economics {
        3'000.0,
        80.0,
        1'500.0,
        10.0
    };

    cout << "Annual revenue/customer: "
         << currency(
                economics.annualRevenuePerCustomer
            )
         << "\n";

    cout << "Annual gross profit/customer: "
         << currency(
                economics.annualGrossProfit()
            )
         << "\n";

    cout << "Estimated lifetime: "
         << fixed << setprecision(2)
         << economics.estimatedLifetimeYears()
         << " years\n";

    cout << "Estimated LTV: "
         << currency(
                economics.estimatedLTV()
            )
         << "\n";

    cout << "LTV/CAC: "
         << fixed << setprecision(2)
         << economics.ltvToCAC()
         << "x\n";
}

// -----------------------------------------------------------------------------
// 19. SENSITIVITY
// -----------------------------------------------------------------------------

void sensitivityExample() {
    printSection(
        "SENSITIVITY ANALYSIS"
    );

    const long long customers = 10'000;
    const double adoption = 20.0;

    const auto result =
        sensitivityAnalysis(
            "Annual price",
            1'000.0,
            2'000.0,
            3'500.0,
            [&](double price) {
                return
                    static_cast<double>(customers) *
                    adoption / 100.0 *
                    price;
            }
        );

    cout << "Parameter: "
         << result.parameter
         << "\n";

    cout << "Low:  "
         << result.lowValue
         << " -> "
         << currency(result.lowOutput)
         << "\n";

    cout << "Base: "
         << result.baseValue
         << " -> "
         << currency(result.baseOutput)
         << "\n";

    cout << "High: "
         << result.highValue
         << " -> "
         << currency(result.highOutput)
         << "\n";
}

// -----------------------------------------------------------------------------
// 20. GROWTH PROJECTION
// -----------------------------------------------------------------------------

void growthExample() {
    printSection(
        "FIVE-YEAR MARKET PROJECTION"
    );

    const auto projection =
        projectMarket(
            50'000'000.0,
            12.0,
            5
        );

    for (size_t year = 0;
         year < projection.size();
         ++year) {

        cout << "Year "
             << year
             << ": "
             << currency(
                    projection[year]
                )
             << "\n";
    }
}

// -----------------------------------------------------------------------------
// 21. MONTE CARLO
// -----------------------------------------------------------------------------

void simulationExample() {
    printSection(
        "MONTE CARLO MARKET-SIZE SIMULATION"
    );

    const auto result =
        monteCarloMarketSize(
            5'000,
            8'000,
            15'000,
            1'500.0,
            3'500.0,
            10.0,
            30.0,
            42
        );

    cout << "Simulations: "
         << result.samples.size()
         << "\n";

    cout << "Minimum: "
         << currency(result.minimum)
         << "\n";

    cout << "P10: "
         << currency(result.p10)
         << "\n";

    cout << "Median: "
         << currency(result.median)
         << "\n";

    cout << "P90: "
         << currency(result.p90)
         << "\n";

    cout << "Maximum: "
         << currency(result.maximum)
         << "\n";

    cout << "Average: "
         << currency(result.average)
         << "\n";
}

// -----------------------------------------------------------------------------
// 22. EDGE CASES
// -----------------------------------------------------------------------------

void edgeCaseExample() {
    printSection(
        "EDGE CASES AND FAILURE CONDITIONS"
    );

    const MarketSize emptyMarket(
        0.0,
        0
    );

    printMarket(
        "ZERO",
        emptyMarket
    );

    try {
        MarketSize invalidMarket(
            -1.0,
            100
        );

        (void)invalidMarket;
    } catch (const exception& error) {
        cout << "Negative revenue rejected: "
             << error.what()
             << "\n";
    }

    try {
        auto invalidPenetration =
            bottomUpMarketSize(
                100,
                100.0,
                125.0
            );

        (void)invalidPenetration;
    } catch (const exception& error) {
        cout << "Invalid penetration rejected: "
             << error.what()
             << "\n";
    }

    try {
        auto invalidGrowth =
            compoundGrowth(
                100.0,
                -101.0,
                5
            );

        (void)invalidGrowth;
    } catch (const exception& error) {
        cout << "Invalid growth rejected: "
             << error.what()
             << "\n";
    }
}

// -----------------------------------------------------------------------------
// 23. TESTS
// -----------------------------------------------------------------------------

void runTests() {
    printSection("TESTS");

    const MarketSize market(
        1'000.0,
        100
    );

    if (market.revenuePerCustomer() != 10.0) {
        throw runtime_error(
            "Revenue per customer test failed"
        );
    }

    const MarketSize bottomUp =
        bottomUpMarketSize(
            100,
            10.0,
            50.0
        );

    if (bottomUp.customers != 50 ||
        bottomUp.revenue != 500.0) {
        throw runtime_error(
            "Bottom-up calculation test failed"
        );
    }

    const double topDown =
        topDownMarketSize(
            1'000.0,
            50.0,
            50.0,
            50.0
        );

    if (topDown != 125.0) {
        throw runtime_error(
            "Top-down calculation test failed"
        );
    }

    const auto hierarchy =
        calculateSOM(
            MarketSize(1'000.0, 100),
            CapacityModel {
                100,
                100,
                100,
                100
            },
            20.0
        );

    if (hierarchy.customers != 20) {
        throw runtime_error(
            "SOM calculation test failed"
        );
    }

    if (compoundGrowth(100.0, 10.0, 2) != 121.0) {
        throw runtime_error(
            "Growth calculation test failed"
        );
    }

    cout << "All tests passed.\n";
}

// -----------------------------------------------------------------------------
// 24. MAIN
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << string(78, '=')
             << "\n"
             << "TAM / SAM / SOM MARKET-SIZING CASE STUDY\n"
             << "Total Addressable Market | Serviceable Available Market |\n"
             << "Serviceable Obtainable Market\n"
             << string(78, '=')
             << "\n";

        const CaseStudyResult caseStudy =
            runCaseStudy();

        (void)caseStudy;

        topDownExample();
        unitEconomicsExample();
        sensitivityExample();
        growthExample();
        simulationExample();
        edgeCaseExample();
        runTests();

        printSection(
            "ENGINEERING AND MODELING PRINCIPLES"
        );

        const vector<string> principles = {
            "Define the market boundary before calculating its size.",
            "Keep customer population and revenue assumptions explicit.",
            "Use bottom-up sizing when identifiable customer data exists.",
            "Use top-down sizing as a cross-check rather than an unquestioned fact.",
            "Do not multiply overlapping constraints as if they were independent.",
            "Separate theoretical demand from operational capacity.",
            "Treat SOM as a constrained estimate for a defined planning period.",
            "Use sensitivity and scenario analysis when assumptions are uncertain.",
            "Keep market opportunity separate from company revenue forecasts.",
            "Validate units, time periods, population definitions, and segmentation.",
            "Use overflow-aware data types and validate numerical inputs.",
            "For production systems, preserve the source and date of every major assumption."
        };

        for (size_t index = 0;
             index < principles.size();
             ++index) {

            cout << setw(2)
                 << index + 1
                 << ". "
                 << principles[index]
                 << "\n";
        }

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
