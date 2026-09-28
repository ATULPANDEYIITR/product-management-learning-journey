/*
 * Market Research
 *
 * Self-contained JavaScript study file covering:
 * - market definition
 * - TAM, SAM, SOM
 * - bottom-up and top-down sizing
 * - trends and CAGR
 * - customer segmentation
 * - industry structure
 * - HHI and CR4
 * - demand and price elasticity
 * - funnel analysis
 * - survey proportions
 * - scenario analysis
 * - validation and edge cases
 *
 * Run with:
 *   node market_research.js
 */

"use strict";

// ============================================================================
// 1. BASIC MARKET DEFINITION
// ============================================================================

class MarketDefinition {
    constructor({
        name,
        geography,
        customerType,
        productScope,
        timePeriod,
        currency = "USD"
    }) {
        this.name = name;
        this.geography = geography;
        this.customerType = customerType;
        this.productScope = productScope;
        this.timePeriod = timePeriod;
        this.currency = currency;
    }

    describe() {
        return [
            `${this.name}`,
            `Product scope: ${this.productScope}`,
            `Customers: ${this.customerType}`,
            `Geography: ${this.geography}`,
            `Period: ${this.timePeriod}`,
            `Currency: ${this.currency}`
        ].join("\n");
    }
}

// ============================================================================
// 2. VALIDATION HELPERS
// ============================================================================

function assertNonNegative(value, name) {
    if (!Number.isFinite(value) || value < 0) {
        throw new Error(`${name} must be a finite non-negative number.`);
    }
}

function assertRate(rate, name) {
    if (!Number.isFinite(rate) || rate < 0 || rate > 1) {
        throw new Error(`${name} must be between 0 and 1.`);
    }
}

// ============================================================================
// 3. MARKET SIZE
// ============================================================================

function calculateTopDownTAM(totalPopulation, targetPercentage, annualSpend) {
    assertNonNegative(totalPopulation, "Population");
    assertRate(targetPercentage, "Target percentage");
    assertNonNegative(annualSpend, "Annual spend");

    return totalPopulation * targetPercentage * annualSpend;
}

function calculateBottomUpTAM(segments) {
    return segments.reduce(
        (total, segment) => total + calculateSegmentMarketValue(segment),
        0
    );
}

function calculateSegmentMarketValue(segment) {
    assertNonNegative(segment.population, "Population");
    assertRate(segment.penetration, "Penetration");
    assertNonNegative(segment.frequency, "Frequency");
    assertNonNegative(segment.averageTransactionValue, "Transaction value");

    return (
        segment.population *
        segment.penetration *
        segment.frequency *
        segment.averageTransactionValue
    );
}

function calculateSAM(tam, geographicCoverage, productFit) {
    assertNonNegative(tam, "TAM");
    assertRate(geographicCoverage, "Geographic coverage");
    assertRate(productFit, "Product fit");

    return tam * geographicCoverage * productFit;
}

function calculateSOM(sam, achievableShare) {
    assertNonNegative(sam, "SAM");
    assertRate(achievableShare, "Achievable share");

    return sam * achievableShare;
}

// ============================================================================
// 4. TRENDS AND FORECASTING
// ============================================================================

function percentageChange(oldValue, newValue) {
    if (!Number.isFinite(oldValue) || oldValue === 0) {
        throw new Error("Old value must be finite and non-zero.");
    }

    return (newValue - oldValue) / oldValue;
}

function calculateCAGR(startValue, endValue, years) {
    if (startValue <= 0 || endValue <= 0) {
        throw new Error("CAGR values must be positive.");
    }

    if (!Number.isInteger(years) || years <= 0) {
        throw new Error("Years must be a positive integer.");
    }

    return Math.pow(endValue / startValue, 1 / years) - 1;
}

function buildTrendTable(observations) {
    const sorted = [...observations].sort((a, b) => a.year - b.year);

    return sorted.map((observation, index) => {
        const previous = sorted[index - 1];

        return {
            year: observation.year,
            value: observation.value,
            growth: previous
                ? percentageChange(previous.value, observation.value)
                : null
        };
    });
}

function forecastCompoundGrowth(currentValue, annualGrowthRate, years) {
    assertNonNegative(currentValue, "Current value");

    if (!Number.isInteger(years) || years < 0) {
        throw new Error("Years must be a non-negative integer.");
    }

    return currentValue * Math.pow(1 + annualGrowthRate, years);
}

// ============================================================================
// 5. CUSTOMER SEGMENTATION
// ============================================================================

const SegmentType = Object.freeze({
    DEMOGRAPHIC: "Demographic",
    GEOGRAPHIC: "Geographic",
    PSYCHOGRAPHIC: "Psychographic",
    BEHAVIORAL: "Behavioral",
    FIRMOGRAPHIC: "Firmographic",
    NEED_BASED: "Need-based"
});

function calculateSegmentMetrics(segments) {
    return segments.map(segment => {
        const annualValue = calculateSegmentMarketValue(segment);
        const customers = segment.population * segment.penetration;

        return {
            name: segment.name,
            type: segment.type,
            potentialCustomers: customers,
            annualUnits: customers * segment.frequency,
            annualValue,
            growthRate: segment.growthRate ?? 0
        };
    });
}

// A transparent analytical index is useful for comparing assumptions.
// It is not a universal ranking mechanism and does not replace research.
function segmentAnalysisIndex({
    marketSize,
    growthRate,
    margin,
    competitiveIntensity
}) {
    assertNonNegative(marketSize, "Market size");
    assertNonNegative(margin, "Margin");
    assertRate(competitiveIntensity, "Competitive intensity");

    const sizeComponent = marketSize === 0
        ? 0
        : Math.log10(marketSize + 1);

    return (
        sizeComponent *
        (1 + growthRate) *
        (1 + margin) *
        (1 - competitiveIntensity)
    );
}

// ============================================================================
// 6. INDUSTRY STRUCTURE
// ============================================================================

function calculateHHI(marketShares) {
    if (!Array.isArray(marketShares) || marketShares.length === 0) {
        throw new Error("At least one market share is required.");
    }

    marketShares.forEach((share, index) => {
        assertRate(share, `Market share ${index + 1}`);
    });

    const totalShare = marketShares.reduce((sum, share) => sum + share, 0);

    if (totalShare > 1.000001) {
        throw new Error("Market shares cannot exceed 100% in total.");
    }

    return marketShares.reduce(
        (hhi, share) => hhi + share * share,
        0
    );
}

function calculateCR4(marketShares) {
    marketShares.forEach((share, index) => {
        assertRate(share, `Market share ${index + 1}`);
    });

    return [...marketShares]
        .sort((a, b) => b - a)
        .slice(0, 4)
        .reduce((sum, share) => sum + share, 0);
}

function concentrationDescription(hhiDecimal) {
    const hhi = hhiDecimal * 10000;

    if (hhi < 1500) {
        return "Lower concentration under conventional HHI bands";
    }

    if (hhi < 2500) {
        return "Moderate concentration under conventional HHI bands";
    }

    return "Higher concentration under conventional HHI bands";
}

// ============================================================================
// 7. DEMAND ANALYSIS
// ============================================================================

function arcPriceElasticity(oldPrice, newPrice, oldQuantity, newQuantity) {
    if (oldPrice <= 0 || newPrice <= 0) {
        throw new Error("Prices must be positive.");
    }

    assertNonNegative(oldQuantity, "Old quantity");
    assertNonNegative(newQuantity, "New quantity");

    const averagePrice = (oldPrice + newPrice) / 2;
    const averageQuantity = (oldQuantity + newQuantity) / 2;

    if (averageQuantity === 0) {
        throw new Error("Average quantity cannot be zero.");
    }

    const priceChange = (newPrice - oldPrice) / averagePrice;
    const quantityChange = (newQuantity - oldQuantity) / averageQuantity;

    if (priceChange === 0) {
        throw new Error("Price must change.");
    }

    return quantityChange / priceChange;
}

function classifyElasticity(elasticity) {
    const magnitude = Math.abs(elasticity);

    if (magnitude > 1) {
        return "Elastic";
    }

    if (magnitude < 1) {
        return "Inelastic";
    }

    return "Unit elastic";
}

function constantElasticityDemand(
    baseQuantity,
    basePrice,
    newPrice,
    elasticity
) {
    assertNonNegative(baseQuantity, "Base quantity");

    if (basePrice <= 0 || newPrice <= 0) {
        throw new Error("Prices must be positive.");
    }

    return baseQuantity * Math.pow(newPrice / basePrice, elasticity);
}

// ============================================================================
// 8. FUNNEL AND SURVEY METRICS
// ============================================================================

function conversionRate(conversions, opportunities) {
    if (!Number.isFinite(conversions) || !Number.isFinite(opportunities)) {
        throw new Error("Counts must be finite numbers.");
    }

    if (conversions < 0 || opportunities < 0) {
        throw new Error("Counts cannot be negative.");
    }

    if (conversions > opportunities) {
        throw new Error("Conversions cannot exceed opportunities.");
    }

    return opportunities === 0 ? 0 : conversions / opportunities;
}

function confidenceIntervalProportion(
    successes,
    sampleSize,
    zScore = 1.96
) {
    if (
        !Number.isInteger(successes) ||
        !Number.isInteger(sampleSize) ||
        sampleSize <= 0 ||
        successes < 0 ||
        successes > sampleSize
    ) {
        throw new Error("Invalid survey counts.");
    }

    const p = successes / sampleSize;
    const standardError = Math.sqrt(
        (p * (1 - p)) / sampleSize
    );

    return {
        estimate: p,
        lower: Math.max(0, p - zScore * standardError),
        upper: Math.min(1, p + zScore * standardError)
    };
}

// ============================================================================
// 9. MARKET ESTIMATE TRIANGULATION
// ============================================================================

function mean(values) {
    if (!values.length) {
        throw new Error("At least one value is required.");
    }

    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function median(values) {
    if (!values.length) {
        throw new Error("At least one value is required.");
    }

    const sorted = [...values].sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);

    return sorted.length % 2 === 0
        ? (sorted[middle - 1] + sorted[middle]) / 2
        : sorted[middle];
}

function triangulateEstimates(estimates) {
    if (!estimates.length) {
        throw new Error("At least one estimate is required.");
    }

    const values = estimates.map(estimate => estimate.value);
    const average = mean(values);
    const middle = median(values);

    const minimum = Math.min(...values);
    const maximum = Math.max(...values);

    return {
        mean: average,
        median: middle,
        relativeRange: average === 0
            ? 0
            : (maximum - minimum) / average
    };
}

// ============================================================================
// 10. SCENARIO MODEL
// ============================================================================

class MarketScenario {
    constructor(name, population, penetration, annualSpend, growthRate) {
        this.name = name;
        this.population = population;
        this.penetration = penetration;
        this.annualSpend = annualSpend;
        this.growthRate = growthRate;
    }

    marketValue() {
        return calculateTopDownTAM(
            this.population,
            this.penetration,
            this.annualSpend
        );
    }
}

// ============================================================================
// 11. ASYNCHRONOUS DEMAND COLLECTION DEMONSTRATION
// ============================================================================

function simulatedDemandSurvey(segmentName, observations) {
    // Promise-based code models how real applications can asynchronously
    // retrieve survey, CRM, web-analytics, or research-provider data.
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                segment: segmentName,
                observations
            });
        }, 20);
    });
}

async function collectDemandEvidence() {
    const datasets = await Promise.all([
        simulatedDemandSurvey("Technology", [
            { intent: 0.72, conversion: 0.18 },
            { intent: 0.64, conversion: 0.14 }
        ]),
        simulatedDemandSurvey("Professional Services", [
            { intent: 0.61, conversion: 0.12 },
            { intent: 0.58, conversion: 0.11 }
        ])
    ]);

    return datasets;
}

// ============================================================================
// 12. COMPLETE CASE STUDY
// ============================================================================

async function runCaseStudy() {
    console.log("=".repeat(78));
    console.log("MARKET RESEARCH CASE STUDY");
    console.log("Illustrative B2B Cloud Analytics Market");
    console.log("=".repeat(78));

    const market = new MarketDefinition({
        name: "Cloud Analytics Platforms",
        geography: "Illustrative regional market",
        customerType: "Mid-sized and enterprise organizations",
        productScope: "Subscription-based analytics software",
        timePeriod: "2025-2030"
    });

    console.log("\n1. MARKET DEFINITION");
    console.log(market.describe());

    const segments = [
        {
            name: "Mid-market technology firms",
            type: SegmentType.FIRMOGRAPHIC,
            population: 18000,
            penetration: 0.42,
            frequency: 1,
            averageTransactionValue: 2400,
            growthRate: 0.12
        },
        {
            name: "Professional services",
            type: SegmentType.FIRMOGRAPHIC,
            population: 12000,
            penetration: 0.35,
            frequency: 1,
            averageTransactionValue: 1800,
            growthRate: 0.09
        },
        {
            name: "Large enterprises",
            type: SegmentType.FIRMOGRAPHIC,
            population: 3000,
            penetration: 0.70,
            frequency: 1,
            averageTransactionValue: 18000,
            growthRate: 0.08
        }
    ];

    console.log("\n2. CUSTOMER SEGMENTS");

    const segmentMetrics = calculateSegmentMetrics(segments);

    segmentMetrics.forEach(segment => {
        console.log(
            `${segment.name}: ` +
            `customers=${segment.potentialCustomers.toLocaleString()}, ` +
            `annual value=$${segment.annualValue.toLocaleString()}, ` +
            `growth=${(segment.growthRate * 100).toFixed(1)}%`
        );
    });

    const bottomUpTAM = calculateBottomUpTAM(segments);

    const topDownTAM = calculateTopDownTAM(
        50000,
        0.45,
        5500
    );

    console.log(`\nBottom-up TAM: $${bottomUpTAM.toLocaleString()}`);
    console.log(`Top-down TAM: $${topDownTAM.toLocaleString()}`);

    const triangulation = triangulateEstimates([
        { value: bottomUpTAM, method: "Bottom-up" },
        { value: topDownTAM, method: "Top-down" }
    ]);

    console.log(
        `Triangulation mean: $${triangulation.mean.toLocaleString()}`
    );
    console.log(
        `Triangulation median: $${triangulation.median.toLocaleString()}`
    );
    console.log(
        `Relative range: ${(triangulation.relativeRange * 100).toFixed(1)}%`
    );

    const sam = calculateSAM(bottomUpTAM, 0.65, 0.80);
    const som = calculateSOM(sam, 0.08);

    console.log(`\nSAM: $${sam.toLocaleString()}`);
    console.log(`SOM: $${som.toLocaleString()}`);

    console.log("\n3. MARKET TRENDS");

    const historical = [
        { year: 2022, value: 82000000 },
        { year: 2023, value: 91000000 },
        { year: 2024, value: 104000000 },
        { year: 2025, value: 119000000 }
    ];

    const trends = buildTrendTable(historical);

    trends.forEach(row => {
        const growth = row.growth === null
            ? "N/A"
            : `${(row.growth * 100).toFixed(1)}%`;

        console.log(
            `${row.year}: $${row.value.toLocaleString()}, growth=${growth}`
        );
    });

    const cagr = calculateCAGR(
        historical[0].value,
        historical[historical.length - 1].value,
        3
    );

    console.log(`2022-2025 CAGR: ${(cagr * 100).toFixed(2)}%`);

    const forecast = forecastCompoundGrowth(
        historical[historical.length - 1].value,
        cagr,
        5
    );

    console.log(
        `Illustrative constant-CAGR 2030 scenario: $${forecast.toLocaleString()}`
    );

    console.log("\n4. INDUSTRY STRUCTURE");

    const competitors = [
        { name: "Alpha Analytics", share: 0.28 },
        { name: "Beta Data", share: 0.21 },
        { name: "Gamma Cloud", share: 0.14 },
        { name: "Delta Systems", share: 0.09 },
        { name: "Other identified firms", share: 0.16 }
    ];

    const shares = competitors.map(company => company.share);
    const hhi = calculateHHI(shares);
    const cr4 = calculateCR4(shares);

    console.log(`CR4: ${(cr4 * 100).toFixed(1)}%`);
    console.log(`HHI: ${(hhi * 10000).toFixed(0)}`);
    console.log(`Concentration: ${concentrationDescription(hhi)}`);

    console.log("\n5. DEMAND ANALYSIS");

    const elasticity = arcPriceElasticity(
        2000,
        2200,
        10000,
        9200
    );

    console.log(`Arc price elasticity: ${elasticity.toFixed(3)}`);
    console.log(`Classification: ${classifyElasticity(elasticity)}`);

    const modeledQuantity = constantElasticityDemand(
        10000,
        2000,
        2500,
        elasticity
    );

    console.log(
        `Modeled quantity at $2,500: ${modeledQuantity.toFixed(0)}`
    );

    console.log("\n6. CUSTOMER DEMAND FUNNEL");

    const leads = 5000;
    const qualified = 1600;
    const trials = 800;
    const customers = 160;

    console.log(
        `Lead → qualified: ${(conversionRate(qualified, leads) * 100).toFixed(1)}%`
    );
    console.log(
        `Qualified → trial: ${(conversionRate(trials, qualified) * 100).toFixed(1)}%`
    );
    console.log(
        `Trial → customer: ${(conversionRate(customers, trials) * 100).toFixed(1)}%`
    );
    console.log(
        `Lead → customer: ${(conversionRate(customers, leads) * 100).toFixed(1)}%`
    );

    console.log("\n7. SURVEY ESTIMATION");

    const interval = confidenceIntervalProportion(420, 1000);

    console.log(
        `Observed adoption: ${(interval.estimate * 100).toFixed(1)}%`
    );
    console.log(
        `Approximate 95% interval: ` +
        `${(interval.lower * 100).toFixed(1)}% to ` +
        `${(interval.upper * 100).toFixed(1)}%`
    );

    console.log("\n8. SCENARIO ANALYSIS");

    const scenarios = [
        new MarketScenario("Conservative", 30000, 0.20, 1500, 0.05),
        new MarketScenario("Base", 30000, 0.30, 2000, 0.10),
        new MarketScenario("Expansion", 30000, 0.40, 2500, 0.15)
    ];

    scenarios.forEach(scenario => {
        console.log(
            `${scenario.name}: ` +
            `$${scenario.marketValue().toLocaleString()}, ` +
            `growth=${(scenario.growthRate * 100).toFixed(1)}%`
        );
    });

    console.log("\n9. ASYNCHRONOUS RESEARCH EVIDENCE");

    const surveyData = await collectDemandEvidence();

    surveyData.forEach(dataset => {
        const averageIntent = dataset.observations.reduce(
            (sum, item) => sum + item.intent,
            0
        ) / dataset.observations.length;

        const averageConversion = dataset.observations.reduce(
            (sum, item) => sum + item.conversion,
            0
        ) / dataset.observations.length;

        console.log(
            `${dataset.segment}: ` +
            `average intent=${(averageIntent * 100).toFixed(1)}%, ` +
            `average conversion=${(averageConversion * 100).toFixed(1)}%`
        );
    });

    console.log("\n10. EDGE CASE VALIDATION");

    try {
        calculateSAM(100000, 1.2, 0.8);
    } catch (error) {
        console.log(`Invalid coverage rejected: ${error.message}`);
    }

    try {
        arcPriceElasticity(100, 100, 1000, 900);
    } catch (error) {
        console.log(`Unchanged price rejected: ${error.message}`);
    }

    console.log("\nCase study complete.");
}

// ============================================================================
// 13. SELF-TESTS
// ============================================================================

function runSelfTests() {
    if (calculateTopDownTAM(1000, 0.5, 100) !== 50000) {
        throw new Error("TAM test failed.");
    }

    if (calculateSAM(100000, 0.5, 0.8) !== 40000) {
        throw new Error("SAM test failed.");
    }

    if (calculateSOM(40000, 0.1) !== 4000) {
        throw new Error("SOM test failed.");
    }

    if (Math.abs(calculateCAGR(100, 121, 2) - 0.10) > 1e-10) {
        throw new Error("CAGR test failed.");
    }

    if (Math.abs(calculateCR4([0.4, 0.3, 0.2, 0.05, 0.05]) - 0.95) > 1e-10) {
        throw new Error("CR4 test failed.");
    }

    if (Math.abs(calculateHHI([0.5, 0.5]) - 0.5) > 1e-10) {
        throw new Error("HHI test failed.");
    }

    if (conversionRate(20, 100) !== 0.2) {
        throw new Error("Conversion test failed.");
    }

    console.log("All self-tests passed.");
}

// ============================================================================
// 14. ENTRY POINT
// ============================================================================

async function main() {
    runSelfTests();
    await runCaseStudy();
}

main().catch(error => {
    console.error("Program failed:", error.message);
    process.exitCode = 1;
});
