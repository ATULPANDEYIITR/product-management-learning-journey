/*
 * TAM / SAM / SOM
 * Total Addressable Market, Serviceable Available Market,
 * Serviceable Obtainable Market
 *
 * This standalone JavaScript study demonstrates:
 * - Market-sizing terminology
 * - Top-down and bottom-up models
 * - Segmentation
 * - SAM constraints
 * - Capacity-constrained SOM
 * - Growth projections
 * - Sensitivity analysis
 * - Unit economics
 * - Scenario analysis
 * - Validation
 * - Monte Carlo simulation
 * - A practical B2B SaaS case study
 *
 * Runtime:
 *   Node.js 18+ recommended
 *
 * No external npm packages are required.
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. GENERAL VALIDATION AND FORMATTING
// -----------------------------------------------------------------------------

function assertFiniteNonNegative(value, name) {
    if (!Number.isFinite(value) || value < 0) {
        throw new Error(`${name} must be finite and non-negative`);
    }
}

function validatePercentage(value, name = "percentage") {
    if (!Number.isFinite(value) || value < 0 || value > 100) {
        throw new Error(`${name} must be between 0 and 100`);
    }
}

function formatCurrency(value, currency = "$") {
    return `${currency}${value.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

function formatCompact(value) {
    const absolute = Math.abs(value);

    if (absolute >= 1e12) return `${(value / 1e12).toFixed(2)}T`;
    if (absolute >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (absolute >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (absolute >= 1e3) return `${(value / 1e3).toFixed(2)}K`;

    return value.toFixed(2);
}

// -----------------------------------------------------------------------------
// 2. MARKET SIZE OBJECT
// -----------------------------------------------------------------------------

class MarketSize {
    constructor(currency, customers) {
        assertFiniteNonNegative(currency, "currency");

        if (!Number.isInteger(customers) || customers < 0) {
            throw new Error("customers must be a non-negative integer");
        }

        this.currency = currency;
        this.customers = customers;
    }

    get revenuePerCustomer() {
        if (this.customers === 0) {
            return 0;
        }

        return this.currency / this.customers;
    }

    percentageOf(otherMarket) {
        if (otherMarket.currency === 0) {
            return 0;
        }

        return (this.currency / otherMarket.currency) * 100;
    }

    toString() {
        return (
            `Customers: ${this.customers.toLocaleString()}, ` +
            `Revenue: ${formatCurrency(this.currency)}, ` +
            `Revenue/customer: ${formatCurrency(this.revenuePerCustomer)}`
        );
    }
}

// -----------------------------------------------------------------------------
// 3. BASIC TAM / SAM / SOM
// -----------------------------------------------------------------------------

function calculateMarketHierarchy(tam, samShare, somShare) {
    validatePercentage(samShare, "samShare");
    validatePercentage(somShare, "somShare");

    const samCustomers = Math.floor(
        tam.customers * samShare / 100
    );

    const sam = new MarketSize(
        samCustomers * tam.revenuePerCustomer,
        samCustomers
    );

    const somCustomers = Math.floor(
        sam.customers * somShare / 100
    );

    const som = new MarketSize(
        somCustomers * sam.revenuePerCustomer,
        somCustomers
    );

    return { tam, sam, som };
}

// -----------------------------------------------------------------------------
// 4. TOP-DOWN MARKET SIZING
// -----------------------------------------------------------------------------

function topDownMarketSize(
    broadMarketRevenue,
    segmentShare,
    geographicShare,
    productFitShare
) {
    assertFiniteNonNegative(
        broadMarketRevenue,
        "broadMarketRevenue"
    );

    validatePercentage(segmentShare, "segmentShare");
    validatePercentage(geographicShare, "geographicShare");
    validatePercentage(productFitShare, "productFitShare");

    return (
        broadMarketRevenue *
        segmentShare / 100 *
        geographicShare / 100 *
        productFitShare / 100
    );
}

// -----------------------------------------------------------------------------
// 5. BOTTOM-UP MARKET SIZING
// -----------------------------------------------------------------------------

function bottomUpMarketSize(
    targetCustomers,
    annualPrice,
    penetration = 100
) {
    if (!Number.isInteger(targetCustomers) || targetCustomers < 0) {
        throw new Error("targetCustomers must be a non-negative integer");
    }

    assertFiniteNonNegative(annualPrice, "annualPrice");
    validatePercentage(penetration, "penetration");

    const effectiveCustomers = Math.floor(
        targetCustomers * penetration / 100
    );

    return new MarketSize(
        effectiveCustomers * annualPrice,
        effectiveCustomers
    );
}

// -----------------------------------------------------------------------------
// 6. SEGMENTED MARKET
// -----------------------------------------------------------------------------

class CustomerSegment {
    constructor(name, customers, annualPrice, adoptionRate = 100) {
        if (!name || !name.trim()) {
            throw new Error("Segment name cannot be empty");
        }

        if (!Number.isInteger(customers) || customers < 0) {
            throw new Error("customers must be a non-negative integer");
        }

        assertFiniteNonNegative(annualPrice, "annualPrice");
        validatePercentage(adoptionRate, "adoptionRate");

        this.name = name;
        this.customers = customers;
        this.annualPrice = annualPrice;
        this.adoptionRate = adoptionRate;
    }

    marketSize() {
        return bottomUpMarketSize(
            this.customers,
            this.annualPrice,
            this.adoptionRate
        );
    }
}

function segmentedMarketSize(segments) {
    let customers = 0;
    let revenue = 0;

    for (const segment of segments) {
        const market = segment.marketSize();

        customers += market.customers;
        revenue += market.currency;
    }

    return new MarketSize(revenue, customers);
}

// -----------------------------------------------------------------------------
// 7. SAM CONSTRAINTS
// -----------------------------------------------------------------------------

class MarketConstraint {
    constructor(name, eligibleShare) {
        if (!name || !name.trim()) {
            throw new Error("Constraint name cannot be empty");
        }

        validatePercentage(eligibleShare, name);

        this.name = name;
        this.eligibleShare = eligibleShare;
    }
}

function applyConstraints(market, constraints) {
    let customerEstimate = market.customers;

    for (const constraint of constraints) {
        customerEstimate *= constraint.eligibleShare / 100;
    }

    const customers = Math.floor(customerEstimate);

    return new MarketSize(
        customers * market.revenuePerCustomer,
        customers
    );
}

// -----------------------------------------------------------------------------
// 8. CAPACITY-CONSTRAINED SOM
// -----------------------------------------------------------------------------

class CapacityModel {
    constructor({
        salesRepresentatives,
        newCustomersPerRepPerYear,
        implementationCapacity,
        supportCapacity
    }) {
        for (const [name, value] of Object.entries({
            salesRepresentatives,
            newCustomersPerRepPerYear,
            implementationCapacity,
            supportCapacity
        })) {
            if (!Number.isInteger(value) || value < 0) {
                throw new Error(`${name} must be a non-negative integer`);
            }
        }

        this.salesRepresentatives = salesRepresentatives;
        this.newCustomersPerRepPerYear = newCustomersPerRepPerYear;
        this.implementationCapacity = implementationCapacity;
        this.supportCapacity = supportCapacity;
    }

    get salesCapacity() {
        return (
            this.salesRepresentatives *
            this.newCustomersPerRepPerYear
        );
    }

    get annualCustomerCapacity() {
        return Math.min(
            this.salesCapacity,
            this.implementationCapacity,
            this.supportCapacity
        );
    }
}

function capacityConstrainedSom(
    sam,
    capacity,
    strategicShareOfSam
) {
    validatePercentage(
        strategicShareOfSam,
        "strategicShareOfSam"
    );

    const desiredCustomers = Math.floor(
        sam.customers * strategicShareOfSam / 100
    );

    const obtainableCustomers = Math.min(
        desiredCustomers,
        capacity.annualCustomerCapacity
    );

    return new MarketSize(
        obtainableCustomers * sam.revenuePerCustomer,
        obtainableCustomers
    );
}

// -----------------------------------------------------------------------------
// 9. USAGE-BASED MARKET
// -----------------------------------------------------------------------------

function usageBasedMarketSize(
    users,
    transactionsPerUserPerYear,
    revenuePerTransaction
) {
    assertFiniteNonNegative(users, "users");
    assertFiniteNonNegative(
        transactionsPerUserPerYear,
        "transactionsPerUserPerYear"
    );
    assertFiniteNonNegative(
        revenuePerTransaction,
        "revenuePerTransaction"
    );

    return (
        users *
        transactionsPerUserPerYear *
        revenuePerTransaction
    );
}

// -----------------------------------------------------------------------------
// 10. GROWTH MODEL
// -----------------------------------------------------------------------------

function compoundGrowth(initialValue, annualGrowthRate, years) {
    assertFiniteNonNegative(initialValue, "initialValue");

    if (!Number.isFinite(annualGrowthRate) ||
        annualGrowthRate <= -100) {
        throw new Error(
            "annualGrowthRate must be greater than -100%"
        );
    }

    if (!Number.isInteger(years) || years < 0) {
        throw new Error("years must be a non-negative integer");
    }

    return initialValue *
        Math.pow(1 + annualGrowthRate / 100, years);
}

function marketProjection(
    initialMarket,
    annualGrowthRate,
    years
) {
    const projections = [];

    for (let year = 0; year <= years; year++) {
        projections.push({
            year,
            customers: Math.round(
                compoundGrowth(
                    initialMarket.customers,
                    annualGrowthRate,
                    year
                )
            ),
            revenue: compoundGrowth(
                initialMarket.currency,
                annualGrowthRate,
                year
            )
        });
    }

    return projections;
}

// -----------------------------------------------------------------------------
// 11. SENSITIVITY ANALYSIS
// -----------------------------------------------------------------------------

function sensitivityAnalysis(
    parameter,
    lowValue,
    baseValue,
    highValue,
    calculation
) {
    if (!(lowValue <= baseValue && baseValue <= highValue)) {
        throw new Error(
            "Sensitivity values must satisfy low <= base <= high"
        );
    }

    return {
        parameter,
        lowValue,
        baseValue,
        highValue,
        lowOutput: calculation(lowValue),
        baseOutput: calculation(baseValue),
        highOutput: calculation(highValue)
    };
}

// -----------------------------------------------------------------------------
// 12. UNIT ECONOMICS
// -----------------------------------------------------------------------------

class UnitEconomics {
    constructor({
        annualRevenuePerCustomer,
        grossMargin,
        annualCAC,
        annualChurnRate
    }) {
        assertFiniteNonNegative(
            annualRevenuePerCustomer,
            "annualRevenuePerCustomer"
        );
        assertFiniteNonNegative(annualCAC, "annualCAC");

        validatePercentage(grossMargin, "grossMargin");
        validatePercentage(annualChurnRate, "annualChurnRate");

        this.annualRevenuePerCustomer =
            annualRevenuePerCustomer;
        this.grossMargin = grossMargin;
        this.annualCAC = annualCAC;
        this.annualChurnRate = annualChurnRate;
    }

    get annualGrossProfit() {
        return (
            this.annualRevenuePerCustomer *
            this.grossMargin / 100
        );
    }

    get estimatedLifetimeYears() {
        if (this.annualChurnRate === 0) {
            return Infinity;
        }

        return 1 / (this.annualChurnRate / 100);
    }

    get estimatedLTV() {
        if (!Number.isFinite(this.estimatedLifetimeYears)) {
            return Infinity;
        }

        return (
            this.annualGrossProfit *
            this.estimatedLifetimeYears
        );
    }

    get ltvToCAC() {
        if (this.annualCAC === 0) {
            return Infinity;
        }

        return this.estimatedLTV / this.annualCAC;
    }
}

// -----------------------------------------------------------------------------
// 13. VALUE-THEORY MODEL
// -----------------------------------------------------------------------------

function valueTheoryPrice(
    economicValueCreated,
    valueCaptureRate
) {
    assertFiniteNonNegative(
        economicValueCreated,
        "economicValueCreated"
    );

    validatePercentage(
        valueCaptureRate,
        "valueCaptureRate"
    );

    return (
        economicValueCreated *
        valueCaptureRate / 100
    );
}

// -----------------------------------------------------------------------------
// 14. DETERMINISTIC RANDOM NUMBER GENERATOR
// -----------------------------------------------------------------------------

class SeededRandom {
    /*
     * A deterministic generator makes educational simulations reproducible.
     * This is not intended for cryptographic security.
     */
    constructor(seed = 42) {
        this.state = seed >>> 0;
    }

    next() {
        this.state = (
            Math.imul(
                1664525,
                this.state
            ) + 1013904223
        ) >>> 0;

        return this.state / 4294967296;
    }

    between(min, max) {
        return min + this.next() * (max - min);
    }

    integer(min, max) {
        return Math.floor(
            this.between(min, max + 1)
        );
    }
}

// -----------------------------------------------------------------------------
// 15. PERCENTILE AND MONTE CARLO
// -----------------------------------------------------------------------------

function percentile(sortedValues, p) {
    if (sortedValues.length === 0) {
        throw new Error("Cannot calculate percentile of empty data");
    }

    if (p < 0 || p > 100) {
        throw new Error("Percentile must be between 0 and 100");
    }

    const position =
        (sortedValues.length - 1) * p / 100;

    const lower = Math.floor(position);
    const upper = Math.ceil(position);

    if (lower === upper) {
        return sortedValues[lower];
    }

    const fraction = position - lower;

    return (
        sortedValues[lower] +
        fraction *
        (sortedValues[upper] - sortedValues[lower])
    );
}

function monteCarloMarketSize({
    simulations,
    customerRange,
    annualPriceRange,
    adoptionRange,
    seed = 42
}) {
    if (!Number.isInteger(simulations) || simulations <= 0) {
        throw new Error("simulations must be positive");
    }

    const [minCustomers, maxCustomers] = customerRange;
    const [minPrice, maxPrice] = annualPriceRange;
    const [minAdoption, maxAdoption] = adoptionRange;

    if (minCustomers < 0 || maxCustomers < minCustomers) {
        throw new Error("Invalid customer range");
    }

    if (minPrice < 0 || maxPrice < minPrice) {
        throw new Error("Invalid price range");
    }

    validatePercentage(minAdoption, "minAdoption");
    validatePercentage(maxAdoption, "maxAdoption");

    if (maxAdoption < minAdoption) {
        throw new Error("Invalid adoption range");
    }

    const random = new SeededRandom(seed);
    const values = [];

    for (let i = 0; i < simulations; i++) {
        const customers = random.integer(
            minCustomers,
            maxCustomers
        );

        const price = random.between(
            minPrice,
            maxPrice
        );

        const adoption = random.between(
            minAdoption,
            maxAdoption
        );

        values.push(
            customers *
            price *
            adoption / 100
        );
    }

    values.sort((a, b) => a - b);

    const sum = values.reduce(
        (total, value) => total + value,
        0
    );

    return {
        samples: values,
        minimum: values[0],
        p10: percentile(values, 10),
        median: percentile(values, 50),
        p90: percentile(values, 90),
        maximum: values[values.length - 1],
        average: sum / values.length
    };
}

// -----------------------------------------------------------------------------
// 16. HIERARCHY VALIDATION
// -----------------------------------------------------------------------------

function validateHierarchy(tam, sam, som) {
    const warnings = [];

    if (sam.customers > tam.customers) {
        warnings.push(
            "SAM customers exceed TAM customers."
        );
    }

    if (som.customers > sam.customers) {
        warnings.push(
            "SOM customers exceed SAM customers."
        );
    }

    if (sam.currency > tam.currency) {
        warnings.push(
            "SAM revenue exceeds TAM revenue."
        );
    }

    if (som.currency > sam.currency) {
        warnings.push(
            "SOM revenue exceeds SAM revenue."
        );
    }

    return warnings;
}

// -----------------------------------------------------------------------------
// 17. REPORTING HELPERS
// -----------------------------------------------------------------------------

function printMarket(label, market) {
    console.log(
        `${label.padEnd(5)} | ` +
        `Customers: ${market.customers.toLocaleString().padStart(10)} | ` +
        `Revenue: ${formatCurrency(market.currency).padStart(18)} | ` +
        `Revenue/customer: ${formatCurrency(market.revenuePerCustomer)}`
    );
}

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

// -----------------------------------------------------------------------------
// 18. BEGINNER EXAMPLE
// -----------------------------------------------------------------------------

function beginnerExample() {
    printSection("BEGINNER TAM / SAM / SOM EXAMPLE");

    const tam = new MarketSize(
        10_000_000,
        100_000
    );

    const { sam, som } =
        calculateMarketHierarchy(tam, 30, 10);

    printMarket("TAM", tam);
    printMarket("SAM", sam);
    printMarket("SOM", som);

    console.log(
        "\nTAM is the broad theoretical opportunity."
    );
    console.log(
        "SAM applies defined service constraints."
    );
    console.log(
        "SOM models the portion treated as obtainable."
    );
}

// -----------------------------------------------------------------------------
// 19. TOP-DOWN EXAMPLE
// -----------------------------------------------------------------------------

function topDownExample() {
    printSection("TOP-DOWN MARKET SIZING");

    const broadMarket = 5_000_000_000;

    const result = topDownMarketSize(
        broadMarket,
        20,
        40,
        60
    );

    console.log(
        `Broad market: ${formatCurrency(broadMarket)}`
    );
    console.log("Segment: 20%");
    console.log("Geography: 40%");
    console.log("Product fit: 60%");
    console.log(
        `Estimated target market: ${formatCurrency(result)}`
    );
}

// -----------------------------------------------------------------------------
// 20. BOTTOM-UP EXAMPLE
// -----------------------------------------------------------------------------

function bottomUpExample() {
    printSection("BOTTOM-UP MARKET SIZING");

    const tam = bottomUpMarketSize(
        25_000,
        2_400,
        100
    );

    const som = bottomUpMarketSize(
        25_000,
        2_400,
        8
    );

    printMarket("TAM", tam);
    printMarket("SOM", som);
}

// -----------------------------------------------------------------------------
// 21. SEGMENT EXAMPLE
// -----------------------------------------------------------------------------

function segmentExample() {
    printSection("SEGMENTED BOTTOM-UP MODEL");

    const segments = [
        new CustomerSegment(
            "Small businesses",
            50_000,
            600
        ),
        new CustomerSegment(
            "Mid-market businesses",
            12_000,
            3_000
        ),
        new CustomerSegment(
            "Enterprise businesses",
            2_000,
            18_000
        )
    ];

    const total = segmentedMarketSize(segments);

    for (const segment of segments) {
        const market = segment.marketSize();

        console.log(
            `${segment.name.padEnd(24)} ` +
            `${market.customers.toLocaleString().padStart(8)} customers | ` +
            `${formatCurrency(market.currency).padStart(16)}`
        );
    }

    console.log("-".repeat(78));
    printMarket("TAM", total);
}

// -----------------------------------------------------------------------------
// 22. CONSTRAINT EXAMPLE
// -----------------------------------------------------------------------------

function constraintExample() {
    printSection("SAM USING EXPLICIT CONSTRAINTS");

    const tam = new MarketSize(
        100_000_000,
        100_000
    );

    const constraints = [
        new MarketConstraint(
            "Supported geography",
            60
        ),
        new MarketConstraint(
            "Supported industry",
            50
        ),
        new MarketConstraint(
            "Product compatibility",
            70
        )
    ];

    const sam = applyConstraints(
        tam,
        constraints
    );

    printMarket("TAM", tam);

    for (const constraint of constraints) {
        console.log(
            `${constraint.name.padEnd(28)} ` +
            `${constraint.eligibleShare}%`
        );
    }

    printMarket("SAM", sam);
}

// -----------------------------------------------------------------------------
// 23. CAPACITY EXAMPLE
// -----------------------------------------------------------------------------

function capacityExample() {
    printSection("CAPACITY-CONSTRAINED SOM");

    const sam = new MarketSize(
        120_000_000,
        20_000
    );

    const capacity = new CapacityModel({
        salesRepresentatives: 10,
        newCustomersPerRepPerYear: 120,
        implementationCapacity: 900,
        supportCapacity: 1_000
    });

    const som = capacityConstrainedSom(
        sam,
        capacity,
        20
    );

    printMarket("SAM", sam);
    console.log(
        `Sales capacity: ${capacity.salesCapacity.toLocaleString()}`
    );
    console.log(
        `Implementation capacity: ${capacity.implementationCapacity.toLocaleString()}`
    );
    console.log(
        `Support capacity: ${capacity.supportCapacity.toLocaleString()}`
    );
    console.log(
        `Effective capacity: ${capacity.annualCustomerCapacity.toLocaleString()}`
    );
    printMarket("SOM", som);
}

// -----------------------------------------------------------------------------
// 24. UNIT ECONOMICS EXAMPLE
// -----------------------------------------------------------------------------

function unitEconomicsExample() {
    printSection("UNIT ECONOMICS");

    const economics = new UnitEconomics({
        annualRevenuePerCustomer: 3_000,
        grossMargin: 80,
        annualCAC: 1_500,
        annualChurnRate: 10
    });

    console.log(
        `Annual revenue/customer: ${formatCurrency(
            economics.annualRevenuePerCustomer
        )}`
    );

    console.log(
        `Annual gross profit/customer: ${formatCurrency(
            economics.annualGrossProfit
        )}`
    );

    console.log(
        `Estimated lifetime: ${
            economics.estimatedLifetimeYears.toFixed(2)
        } years`
    );

    console.log(
        `Estimated LTV: ${formatCurrency(
            economics.estimatedLTV
        )}`
    );

    console.log(
        `LTV/CAC: ${economics.ltvToCAC.toFixed(2)}x`
    );
}

// -----------------------------------------------------------------------------
// 25. ASYNCHRONOUS SCENARIO PROCESSING
// -----------------------------------------------------------------------------

function calculateScenarioAsync(
    name,
    market,
    annualGrowthRate,
    years
) {
    /*
     * Promise-based processing demonstrates how market calculations can fit
     * into an event-driven JavaScript application.
     */
    return new Promise((resolve) => {
        setTimeout(() => {
            const projection = marketProjection(
                market,
                annualGrowthRate,
                years
            );

            resolve({
                name,
                projection
            });
        }, 0);
    });
}

async function scenarioComparisonExample() {
    printSection("ASYNC SCENARIO COMPARISON");

    const baseMarket = new MarketSize(
        50_000_000,
        10_000
    );

    const scenarios = await Promise.all([
        calculateScenarioAsync(
            "Conservative",
            baseMarket,
            5,
            5
        ),
        calculateScenarioAsync(
            "Base",
            baseMarket,
            12,
            5
        ),
        calculateScenarioAsync(
            "High growth",
            baseMarket,
            20,
            5
        )
    ]);

    for (const scenario of scenarios) {
        const finalYear =
            scenario.projection[
                scenario.projection.length - 1
            ];

        console.log(
            `${scenario.name.padEnd(16)} | ` +
            `Year 5 revenue: ${formatCurrency(finalYear.revenue)}`
        );
    }
}

// -----------------------------------------------------------------------------
// 26. MONTE CARLO EXAMPLE
// -----------------------------------------------------------------------------

function simulationExample() {
    printSection("MONTE CARLO MARKET-SIZE SIMULATION");

    const result = monteCarloMarketSize({
        simulations: 5_000,
        customerRange: [8_000, 15_000],
        annualPriceRange: [1_500, 3_500],
        adoptionRange: [10, 30],
        seed: 42
    });

    console.log(`Simulations: ${result.samples.length}`);
    console.log(`Minimum: ${formatCurrency(result.minimum)}`);
    console.log(`P10: ${formatCurrency(result.p10)}`);
    console.log(`Median: ${formatCurrency(result.median)}`);
    console.log(`P90: ${formatCurrency(result.p90)}`);
    console.log(`Maximum: ${formatCurrency(result.maximum)}`);
    console.log(`Average: ${formatCurrency(result.average)}`);
}

// -----------------------------------------------------------------------------
// 27. COMPLETE B2B SAAS CASE STUDY
// -----------------------------------------------------------------------------

function b2bSaaSCaseStudy() {
    printSection("COMPLETE B2B SAAS CASE STUDY");

    const tamSegments = [
        new CustomerSegment(
            "Small business",
            80_000,
            900
        ),
        new CustomerSegment(
            "Mid-market",
            20_000,
            4_000
        ),
        new CustomerSegment(
            "Enterprise",
            5_000,
            15_000
        )
    ];

    const tam = segmentedMarketSize(
        tamSegments
    );

    const sam = applyConstraints(
        tam,
        [
            new MarketConstraint(
                "Target geography",
                50
            ),
            new MarketConstraint(
                "Target industries",
                60
            ),
            new MarketConstraint(
                "Compatible technology",
                70
            )
        ]
    );

    const capacity = new CapacityModel({
        salesRepresentatives: 15,
        newCustomersPerRepPerYear: 80,
        implementationCapacity: 1_100,
        supportCapacity: 1_500
    });

    const som = capacityConstrainedSom(
        sam,
        capacity,
        15
    );

    printMarket("TAM", tam);
    printMarket("SAM", sam);
    printMarket("SOM", som);

    const warnings =
        validateHierarchy(tam, sam, som);

    if (warnings.length === 0) {
        console.log(
            "\nHierarchy validation: PASSED"
        );
    } else {
        console.log("\nValidation warnings:");

        for (const warning of warnings) {
            console.log(`- ${warning}`);
        }
    }

    return { tam, sam, som };
}

// -----------------------------------------------------------------------------
// 28. ERROR HANDLING AND EDGE CASES
// -----------------------------------------------------------------------------

function edgeCaseExample() {
    printSection("EDGE CASES AND ERROR HANDLING");

    const zeroMarket = new MarketSize(
        0,
        0
    );

    printMarket("ZERO", zeroMarket);

    try {
        new MarketSize(-1, 10);
    } catch (error) {
        console.log(
            `Negative market rejected: ${error.message}`
        );
    }

    try {
        bottomUpMarketSize(
            100,
            100,
            150
        );
    } catch (error) {
        console.log(
            `Invalid penetration rejected: ${error.message}`
        );
    }

    try {
        topDownMarketSize(
            100_000,
            110,
            50,
            50
        );
    } catch (error) {
        console.log(
            `Invalid share rejected: ${error.message}`
        );
    }
}

// -----------------------------------------------------------------------------
// 29. TESTS
// -----------------------------------------------------------------------------

function runTests() {
    printSection("TESTS");

    const market = new MarketSize(
        1_000,
        100
    );

    console.assert(
        market.revenuePerCustomer === 10,
        "Revenue/customer test failed"
    );

    const bottomUp =
        bottomUpMarketSize(100, 10, 50);

    console.assert(
        bottomUp.customers === 50,
        "Bottom-up customer test failed"
    );

    console.assert(
        bottomUp.currency === 500,
        "Bottom-up revenue test failed"
    );

    const topDown =
        topDownMarketSize(
            1_000,
            50,
            50,
            50
        );

    console.assert(
        topDown === 125,
        "Top-down calculation test failed"
    );

    const hierarchy =
        calculateMarketHierarchy(
            new MarketSize(1_000, 100),
            50,
            20
        );

    console.assert(
        hierarchy.sam.customers === 50,
        "SAM calculation test failed"
    );

    console.assert(
        hierarchy.som.customers === 10,
        "SOM calculation test failed"
    );

    console.assert(
        compoundGrowth(100, 10, 2) === 121,
        "Growth calculation test failed"
    );

    console.log("Tests passed.");
}

// -----------------------------------------------------------------------------
// 30. MAIN
// -----------------------------------------------------------------------------

async function main() {
    console.log("=".repeat(78));
    console.log("TAM / SAM / SOM MARKET-SIZING STUDY");
    console.log("Total Addressable Market | Serviceable Available Market |");
    console.log("Serviceable Obtainable Market");
    console.log("=".repeat(78));

    beginnerExample();
    topDownExample();
    bottomUpExample();
    segmentExample();
    constraintExample();
    capacityExample();
    unitEconomicsExample();
    await scenarioComparisonExample();
    simulationExample();
    b2bSaaSCaseStudy();
    edgeCaseExample();
    runTests();

    printSection("IMPORTANT MODELING PRINCIPLES");

    const principles = [
        "Define the market before calculating its size.",
        "Document the population, geography, segment, product, channel, and time period.",
        "Use bottom-up estimates when identifiable customer counts are available.",
        "Use top-down estimates as cross-checks rather than treating broad percentages as facts.",
        "Do not multiply overlapping constraints as though they were independent.",
        "Separate demand potential from operational capacity.",
        "Treat SOM as a constrained planning estimate, not merely an arbitrary percentage.",
        "Use scenarios and sensitivity analysis when assumptions are uncertain.",
        "Keep market size separate from company revenue forecasts.",
        "Revalidate assumptions when pricing, product scope, geography, or market structure changes."
    ];

    principles.forEach((principle, index) => {
        console.log(
            `${String(index + 1).padStart(2)}. ${principle}`
        );
    });
}

main().catch((error) => {
    console.error("Program failed:", error.message);
    process.exitCode = 1;
});
