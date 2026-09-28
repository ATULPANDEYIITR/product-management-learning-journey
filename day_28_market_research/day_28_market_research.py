"""
Market Research: Market Size, Trends, Customer Segments, Industry Structure,
and Demand Analysis

A self-contained educational implementation that progresses from basic market
research concepts to a reproducible quantitative market-analysis workflow.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ============================================================================
# 1. FUNDAMENTAL CONCEPTS
# ============================================================================

class MarketLevel(Enum):
    TAM = "Total Addressable Market"
    SAM = "Serviceable Available Market"
    SOM = "Serviceable Obtainable Market"


class SegmentType(Enum):
    DEMOGRAPHIC = "Demographic"
    GEOGRAPHIC = "Geographic"
    PSYCHOGRAPHIC = "Psychographic"
    BEHAVIORAL = "Behavioral"
    FIRMOGRAPHIC = "Firmographic"
    NEED_BASED = "Need-based"


@dataclass
class MarketDefinition:
    """Defines the boundaries of a market before measuring it."""

    name: str
    geography: str
    customer_type: str
    product_scope: str
    time_period: str
    currency: str = "USD"

    def describe(self) -> str:
        return (
            f"{self.name}: {self.product_scope}; customers={self.customer_type}; "
            f"geography={self.geography}; period={self.time_period}"
        )


@dataclass
class MarketYear:
    year: int
    value: float

    @property
    def growth_from_previous(self) -> Optional[float]:
        return None


@dataclass
class Segment:
    name: str
    segment_type: SegmentType
    population: int
    penetration_rate: float
    annual_frequency: float
    average_transaction_value: float
    growth_rate: float = 0.0

    def validate(self) -> None:
        if self.population < 0:
            raise ValueError("Population cannot be negative.")
        if not 0 <= self.penetration_rate <= 1:
            raise ValueError("Penetration rate must be between 0 and 1.")
        if self.annual_frequency < 0:
            raise ValueError("Frequency cannot be negative.")
        if self.average_transaction_value < 0:
            raise ValueError("Transaction value cannot be negative.")

    def annual_demand_units(self) -> float:
        self.validate()
        return self.population * self.penetration_rate * self.annual_frequency

    def annual_market_value(self) -> float:
        return self.annual_demand_units() * self.average_transaction_value


@dataclass
class Competitor:
    name: str
    market_share: float
    annual_revenue: float
    positioning: str

    def validate(self) -> None:
        if not 0 <= self.market_share <= 1:
            raise ValueError("Market share must be between 0 and 1.")
        if self.annual_revenue < 0:
            raise ValueError("Revenue cannot be negative.")


@dataclass
class DemandObservation:
    period: str
    price: float
    quantity: float
    customer_count: int
    conversion_rate: float

    def validate(self) -> None:
        if self.price < 0 or self.quantity < 0:
            raise ValueError("Price and quantity cannot be negative.")
        if self.customer_count < 0:
            raise ValueError("Customer count cannot be negative.")
        if not 0 <= self.conversion_rate <= 1:
            raise ValueError("Conversion rate must be between 0 and 1.")


# ============================================================================
# 2. MARKET SIZE: TAM, SAM, SOM
# ============================================================================

def calculate_top_down_tam(
    total_population: int,
    percentage_in_target_market: float,
    annual_spend_per_customer: float,
) -> float:
    """
    Top-down TAM estimation.

    TAM = potentially relevant customers × annual spend/customer.

    This method is simple but depends heavily on the quality of the external
    market estimate and the assumptions used to define the population.
    """
    if total_population < 0:
        raise ValueError("Population cannot be negative.")
    if not 0 <= percentage_in_target_market <= 1:
        raise ValueError("Market percentage must be between 0 and 1.")
    if annual_spend_per_customer < 0:
        raise ValueError("Annual spend cannot be negative.")

    return (
        total_population
        * percentage_in_target_market
        * annual_spend_per_customer
    )


def calculate_bottom_up_tam(segments: Sequence[Segment]) -> float:
    """
    Bottom-up TAM.

    The market is constructed from identifiable customer groups rather than
    accepting one large external market number.
    """
    return sum(segment.annual_market_value() for segment in segments)


def calculate_sam(tam: float, geographic_coverage: float, product_fit: float) -> float:
    """
    SAM = TAM × geographic/service coverage × product fit.
    """
    if tam < 0:
        raise ValueError("TAM cannot be negative.")
    if not 0 <= geographic_coverage <= 1:
        raise ValueError("Geographic coverage must be between 0 and 1.")
    if not 0 <= product_fit <= 1:
        raise ValueError("Product fit must be between 0 and 1.")

    return tam * geographic_coverage * product_fit


def calculate_som(
    sam: float,
    achievable_share: float,
) -> float:
    """
    SOM = SAM × realistically achievable share.

    SOM is not simply the largest possible share. It should be grounded in
    capacity, distribution, competition, pricing, customer acquisition,
    retention, and time constraints.
    """
    if sam < 0:
        raise ValueError("SAM cannot be negative.")
    if not 0 <= achievable_share <= 1:
        raise ValueError("Achievable share must be between 0 and 1.")

    return sam * achievable_share


# ============================================================================
# 3. GROWTH, CAGR, AND MARKET TRENDS
# ============================================================================

def percentage_change(old_value: float, new_value: float) -> float:
    if old_value == 0:
        raise ValueError("Cannot calculate percentage change from zero.")
    return (new_value - old_value) / old_value


def calculate_cagr(start_value: float, end_value: float, years: int) -> float:
    """
    CAGR = (Ending value / Beginning value)^(1/years) - 1.

    CAGR describes a smoothed annual growth rate. It does not imply that the
    market actually grew at the same rate every year.
    """
    if start_value <= 0 or end_value <= 0:
        raise ValueError("CAGR values must be positive.")
    if years <= 0:
        raise ValueError("Years must be positive.")

    return (end_value / start_value) ** (1 / years) - 1


def calculate_year_over_year_growth(values: Sequence[float]) -> List[Optional[float]]:
    """Returns growth rates for consecutive observations."""
    if not values:
        return []

    growth = [None]
    for previous, current in zip(values, values[1:]):
        if previous == 0:
            growth.append(None)
        else:
            growth.append((current - previous) / previous)
    return growth


def forecast_market_value(
    current_value: float,
    annual_growth_rate: float,
    years: int,
) -> float:
    """
    Compound-growth forecast.

    This is a scenario model, not a prediction of what must happen.
    """
    if current_value < 0:
        raise ValueError("Current market value cannot be negative.")
    if years < 0:
        raise ValueError("Years cannot be negative.")
    return current_value * ((1 + annual_growth_rate) ** years)


def build_market_trend_table(values: Sequence[Tuple[int, float]]) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    previous = None

    for year, value in values:
        row: Dict[str, float] = {"year": year, "market_value": value}
        if previous is None or previous == 0:
            row["growth"] = float("nan")
        else:
            row["growth"] = (value - previous) / previous
        rows.append(row)
        previous = value

    return rows


# ============================================================================
# 4. CUSTOMER SEGMENTATION
# ============================================================================

def segment_attractiveness(
    market_size: float,
    growth_rate: float,
    margin: float,
    competitive_intensity: float,
) -> float:
    """
    A transparent analytical index.

    It is deliberately not a universal 'best segment' score. Analysts should
    define weights and assumptions according to the research question.
    """
    if market_size < 0:
        raise ValueError("Market size cannot be negative.")
    if margin < 0:
        raise ValueError("Margin cannot be negative.")
    if not 0 <= competitive_intensity <= 1:
        raise ValueError("Competitive intensity must be between 0 and 1.")

    # Log transformation prevents very large markets from overwhelming every
    # other factor. Competitive intensity reduces the resulting index.
    size_component = 0 if market_size == 0 else __import__("math").log10(market_size + 1)
    return (
        size_component
        * (1 + growth_rate)
        * (1 + margin)
        * (1 - competitive_intensity)
    )


def identify_segment_metrics(segments: Sequence[Segment]) -> List[Dict[str, float]]:
    """Creates comparable quantitative demand metrics for each segment."""
    result = []

    for segment in segments:
        segment.validate()
        result.append(
            {
                "segment": segment.name,
                "population": segment.population,
                "penetrated_customers": segment.population * segment.penetration_rate,
                "annual_units": segment.annual_demand_units(),
                "annual_value": segment.annual_market_value(),
                "growth_rate": segment.growth_rate,
            }
        )

    return result


# ============================================================================
# 5. INDUSTRY STRUCTURE
# ============================================================================

def calculate_herfindahl_hirschman_index(market_shares: Sequence[float]) -> float:
    """
    HHI = sum of squared market shares.

    Input shares are decimals. For example, 40% is represented as 0.40.

    The function validates that the supplied shares are plausible. A partial
    list of competitors can produce an incomplete concentration picture, so
    users should distinguish measured shares from estimated residual shares.
    """
    if any(share < 0 or share > 1 for share in market_shares):
        raise ValueError("Every market share must be between 0 and 1.")
    if sum(market_shares) > 1.000001:
        raise ValueError("Market shares cannot sum to more than 100%.")

    return sum(share ** 2 for share in market_shares)


def four_firm_concentration_ratio(market_shares: Sequence[float]) -> float:
    """CR4 = combined share of the four largest identified firms."""
    if any(share < 0 or share > 1 for share in market_shares):
        raise ValueError("Invalid market share.")

    return sum(sorted(market_shares, reverse=True)[:4])


def classify_concentration(hhi_decimal: float) -> str:
    """
    Descriptive classification using decimal-share HHI.

    This classification is intentionally presented as an analytical convention;
    legal competition assessments depend on jurisdiction, market definition,
    evidence, and applicable guidance.
    """
    hhi = hhi_decimal * 10_000

    if hhi < 1_500:
        return "Lower concentration under the conventional HHI bands"
    if hhi < 2_500:
        return "Moderate concentration under the conventional HHI bands"
    return "Higher concentration under the conventional HHI bands"


# ============================================================================
# 6. DEMAND ANALYSIS
# ============================================================================

def price_elasticity(
    old_price: float,
    new_price: float,
    old_quantity: float,
    new_quantity: float,
) -> float:
    """
    Midpoint (arc) elasticity.

    Elasticity = percentage change in quantity / percentage change in price.

    A negative result is common for ordinary demand relationships, although
    exceptions can occur in economic theory and real markets.
    """
    if old_price <= 0 or new_price <= 0:
        raise ValueError("Prices must be positive.")
    if old_quantity < 0 or new_quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    average_price = (old_price + new_price) / 2
    average_quantity = (old_quantity + new_quantity) / 2

    if average_price == 0 or average_quantity == 0:
        raise ValueError("Midpoint cannot be zero.")

    percentage_price_change = (new_price - old_price) / average_price
    percentage_quantity_change = (new_quantity - old_quantity) / average_quantity

    if percentage_price_change == 0:
        raise ValueError("Price did not change.")

    return percentage_quantity_change / percentage_price_change


def classify_elasticity(elasticity: float) -> str:
    magnitude = abs(elasticity)

    if magnitude > 1:
        return "Elastic demand"
    if magnitude < 1:
        return "Inelastic demand"
    return "Unit elastic demand"


def demand_from_price(
    base_quantity: float,
    base_price: float,
    new_price: float,
    elasticity: float,
) -> float:
    """
    Simple constant-elasticity approximation.

    Q2 = Q1 × (P2/P1)^elasticity

    This is an analytical model and should not be treated as a causal estimate
    without supporting research.
    """
    if base_quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    if base_price <= 0 or new_price <= 0:
        raise ValueError("Prices must be positive.")

    return base_quantity * (new_price / base_price) ** elasticity


# ============================================================================
# 7. SURVEY AND FUNNEL METRICS
# ============================================================================

def conversion_rate(conversions: int, opportunities: int) -> float:
    if conversions < 0 or opportunities < 0:
        raise ValueError("Counts cannot be negative.")
    if conversions > opportunities:
        raise ValueError("Conversions cannot exceed opportunities.")
    if opportunities == 0:
        return 0.0
    return conversions / opportunities


def weighted_average(values: Sequence[float], weights: Sequence[float]) -> float:
    if len(values) != len(weights) or not values:
        raise ValueError("Values and weights must have equal non-zero length.")
    if any(weight < 0 for weight in weights):
        raise ValueError("Weights cannot be negative.")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero.")

    return sum(value * weight for value, weight in zip(values, weights)) / total_weight


def confidence_interval_proportion(
    successes: int,
    sample_size: int,
    z_score: float = 1.96,
) -> Tuple[float, float]:
    """
    Approximate 95% confidence interval by default.

    This normal approximation is less reliable for very small samples or
    proportions near 0 or 1. It is shown here to teach the mechanics, not to
    replace statistical methodology.
    """
    if sample_size <= 0:
        raise ValueError("Sample size must be positive.")
    if not 0 <= successes <= sample_size:
        raise ValueError("Successes must be between zero and sample size.")

    p = successes / sample_size
    standard_error = sqrt(p * (1 - p) / sample_size)

    lower = max(0.0, p - z_score * standard_error)
    upper = min(1.0, p + z_score * standard_error)
    return lower, upper


# ============================================================================
# 8. SCENARIO ANALYSIS
# ============================================================================

@dataclass
class Scenario:
    name: str
    customer_count: int
    penetration: float
    annual_spend: float
    growth_rate: float

    def market_value(self) -> float:
        if self.customer_count < 0:
            raise ValueError("Customer count cannot be negative.")
        if not 0 <= self.penetration <= 1:
            raise ValueError("Penetration must be between 0 and 1.")
        if self.annual_spend < 0:
            raise ValueError("Annual spend cannot be negative.")

        return self.customer_count * self.penetration * self.annual_spend


def scenario_table(scenarios: Sequence[Scenario]) -> List[Dict[str, float | str]]:
    return [
        {
            "scenario": scenario.name,
            "market_value": scenario.market_value(),
            "growth_rate": scenario.growth_rate,
        }
        for scenario in scenarios
    ]


# ============================================================================
# 9. COMPETITOR AND INDUSTRY ANALYSIS
# ============================================================================

def reconcile_market_shares(competitors: Sequence[Competitor]) -> Dict[str, float]:
    """
    Checks whether identified competitor shares account for the whole market.

    The residual is not automatically assigned to one competitor; it may
    represent fragmented competitors, private firms, imports, substitutes,
    measurement error, or an incompletely defined competitive set.
    """
    for competitor in competitors:
        competitor.validate()

    identified_share = sum(c.market_share for c in competitors)

    return {
        "identified_share": identified_share,
        "residual_share": max(0.0, 1.0 - identified_share),
    }


def implied_market_size_from_revenue(
    company_revenue: float,
    company_market_share: float,
) -> float:
    """
    Market size implied by a company's revenue and market share.

    This is useful as a cross-check but inherits errors from both inputs.
    """
    if company_revenue < 0:
        raise ValueError("Revenue cannot be negative.")
    if not 0 < company_market_share <= 1:
        raise ValueError("Market share must be greater than 0 and at most 1.")

    return company_revenue / company_market_share


# ============================================================================
# 10. DATA QUALITY AND TRIANGULATION
# ============================================================================

@dataclass
class Estimate:
    source_name: str
    method: str
    value: float
    confidence: str
    notes: str = ""


def triangulate_estimates(estimates: Sequence[Estimate]) -> Dict[str, float | str]:
    """
    Compares independent estimates.

    No estimate is automatically treated as correct. Analysts should examine
    definitions, periods, geography, customer scope, methodology, and sources.
    """
    if not estimates:
        raise ValueError("At least one estimate is required.")

    values = [estimate.value for estimate in estimates]
    average_value = mean(values)
    median_value = median(values)

    if average_value == 0:
        dispersion = 0.0
    else:
        dispersion = (
            max(values) - min(values)
        ) / average_value

    return {
        "mean": average_value,
        "median": median_value,
        "relative_range": dispersion,
        "interpretation": (
            "Low dispersion" if dispersion < 0.10
            else "Moderate dispersion" if dispersion < 0.25
            else "High dispersion; investigate definitions and assumptions"
        ),
    }


# ============================================================================
# 11. COMPLETE MARKET RESEARCH CASE STUDY
# ============================================================================

def run_case_study() -> None:
    print("=" * 78)
    print("MARKET RESEARCH CASE STUDY")
    print("Illustrative B2B Cloud Analytics Market")
    print("=" * 78)

    market_definition = MarketDefinition(
        name="Cloud Analytics Platforms",
        geography="Illustrative regional market",
        customer_type="Mid-sized and enterprise organizations",
        product_scope="Subscription-based analytics software",
        time_period="2025-2030",
    )

    print("\n1. MARKET DEFINITION")
    print(market_definition.describe())

    # ------------------------------------------------------------------------
    # Segment-based bottom-up sizing
    # ------------------------------------------------------------------------
    segments = [
        Segment(
            name="Mid-market technology firms",
            segment_type=SegmentType.FIRMOGRAPHIC,
            population=18_000,
            penetration_rate=0.42,
            annual_frequency=1.0,
            average_transaction_value=2_400,
            growth_rate=0.12,
        ),
        Segment(
            name="Professional services",
            segment_type=SegmentType.FIRMOGRAPHIC,
            population=12_000,
            penetration_rate=0.35,
            annual_frequency=1.0,
            average_transaction_value=1_800,
            growth_rate=0.09,
        ),
        Segment(
            name="Large enterprises",
            segment_type=SegmentType.FIRMOGRAPHIC,
            population=3_000,
            penetration_rate=0.70,
            annual_frequency=1.0,
            average_transaction_value=18_000,
            growth_rate=0.08,
        ),
    ]

    print("\n2. CUSTOMER SEGMENTS")
    segment_metrics = identify_segment_metrics(segments)

    for row in segment_metrics:
        print(
            f"{row['segment']}: "
            f"customers={row['penetrated_customers']:,.0f}, "
            f"annual value=${row['annual_value']:,.0f}, "
            f"growth={row['growth_rate']:.1%}"
        )

    bottom_up_tam = calculate_bottom_up_tam(segments)
    print(f"\nBottom-up TAM: ${bottom_up_tam:,.0f}")

    # ------------------------------------------------------------------------
    # Top-down cross-check
    # ------------------------------------------------------------------------
    top_down_tam = calculate_top_down_tam(
        total_population=50_000,
        percentage_in_target_market=0.45,
        annual_spend_per_customer=5_500,
    )

    print(f"Top-down TAM:  ${top_down_tam:,.0f}")

    triangulation = triangulate_estimates(
        [
            Estimate(
                source_name="Bottom-up model",
                method="Segment population × penetration × spend",
                value=bottom_up_tam,
                confidence="Medium",
            ),
            Estimate(
                source_name="Top-down model",
                method="Target population × average annual spend",
                value=top_down_tam,
                confidence="Medium",
            ),
        ]
    )

    print(
        f"Triangulation mean: ${triangulation['mean']:,.0f}; "
        f"median: ${triangulation['median']:,.0f}; "
        f"relative range: {triangulation['relative_range']:.1%}"
    )

    # ------------------------------------------------------------------------
    # SAM and SOM
    # ------------------------------------------------------------------------
    sam = calculate_sam(
        tam=bottom_up_tam,
        geographic_coverage=0.65,
        product_fit=0.80,
    )
    som = calculate_som(
        sam=sam,
        achievable_share=0.08,
    )

    print(f"\nSAM: ${sam:,.0f}")
    print(f"SOM: ${som:,.0f}")

    # ------------------------------------------------------------------------
    # Historical trend
    # ------------------------------------------------------------------------
    trend = [
        (2022, 82_000_000),
        (2023, 91_000_000),
        (2024, 104_000_000),
        (2025, 119_000_000),
    ]

    print("\n3. MARKET TRENDS")
    trend_rows = build_market_trend_table(trend)

    for row in trend_rows:
        growth_text = "N/A" if row["growth"] != row["growth"] else f"{row['growth']:.1%}"
        print(
            f"{int(row['year'])}: "
            f"${row['market_value']:,.0f}; growth={growth_text}"
        )

    cagr = calculate_cagr(trend[0][1], trend[-1][1], 3)
    print(f"2022-2025 CAGR: {cagr:.2%}")

    forecast_2030 = forecast_market_value(
        current_value=trend[-1][1],
        annual_growth_rate=cagr,
        years=5,
    )
    print(f"Illustrative constant-CAGR 2030 scenario: ${forecast_2030:,.0f}")

    # ------------------------------------------------------------------------
    # Industry structure
    # ------------------------------------------------------------------------
    competitors = [
        Competitor("Alpha Analytics", 0.28, 33_320_000, "Enterprise suite"),
        Competitor("Beta Data", 0.21, 24_990_000, "Mid-market platform"),
        Competitor("Gamma Cloud", 0.14, 16_660_000, "Cloud-native platform"),
        Competitor("Delta Systems", 0.09, 10_710_000, "Integrated software"),
        Competitor("Other identified firms", 0.16, 19_040_000, "Fragmented"),
    ]

    print("\n4. INDUSTRY STRUCTURE")
    share_data = reconcile_market_shares(competitors)

    hhi = calculate_herfindahl_hirschman_index(
        [competitor.market_share for competitor in competitors]
    )
    cr4 = four_firm_concentration_ratio(
        [competitor.market_share for competitor in competitors]
    )

    print(f"Identified market share: {share_data['identified_share']:.1%}")
    print(f"Residual share: {share_data['residual_share']:.1%}")
    print(f"CR4: {cr4:.1%}")
    print(f"HHI: {hhi * 10_000:.0f}")
    print(f"Descriptive concentration band: {classify_concentration(hhi)}")

    # ------------------------------------------------------------------------
    # Demand and price analysis
    # ------------------------------------------------------------------------
    print("\n5. DEMAND ANALYSIS")

    elasticity = price_elasticity(
        old_price=2_000,
        new_price=2_200,
        old_quantity=10_000,
        new_quantity=9_200,
    )

    print(f"Estimated arc price elasticity: {elasticity:.3f}")
    print(f"Classification: {classify_elasticity(elasticity)}")

    modeled_quantity = demand_from_price(
        base_quantity=10_000,
        base_price=2_000,
        new_price=2_500,
        elasticity=elasticity,
    )
    print(f"Modeled quantity at $2,500: {modeled_quantity:,.0f}")

    # ------------------------------------------------------------------------
    # Funnel analysis
    # ------------------------------------------------------------------------
    leads = 5_000
    qualified = 1_600
    trials = 800
    customers = 160

    lead_to_qualified = conversion_rate(qualified, leads)
    qualified_to_trial = conversion_rate(trials, qualified)
    trial_to_customer = conversion_rate(customers, trials)

    print("\n6. CUSTOMER DEMAND FUNNEL")
    print(f"Lead → qualified: {lead_to_qualified:.1%}")
    print(f"Qualified → trial: {qualified_to_trial:.1%}")
    print(f"Trial → customer: {trial_to_customer:.1%}")
    print(f"Lead → customer: {conversion_rate(customers, leads):.1%}")

    # ------------------------------------------------------------------------
    # Survey estimation
    # ------------------------------------------------------------------------
    print("\n7. SURVEY ESTIMATION")

    lower, upper = confidence_interval_proportion(
        successes=420,
        sample_size=1_000,
    )
    print(f"Observed adoption: {420 / 1_000:.1%}")
    print(f"Approximate 95% interval: {lower:.1%} to {upper:.1%}")

    # ------------------------------------------------------------------------
    # Scenario analysis
    # ------------------------------------------------------------------------
    print("\n8. SCENARIO ANALYSIS")

    scenarios = [
        Scenario("Conservative", 30_000, 0.20, 1_500, 0.05),
        Scenario("Base", 30_000, 0.30, 2_000, 0.10),
        Scenario("Expansion", 30_000, 0.40, 2_500, 0.15),
    ]

    for row in scenario_table(scenarios):
        print(
            f"{row['scenario']}: "
            f"${row['market_value']:,.0f}, "
            f"growth={row['growth_rate']:.1%}"
        )

    # ------------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------------
    print("\n9. EDGE CASES AND VALIDATION")

    try:
        calculate_sam(tam=100_000, geographic_coverage=1.2, product_fit=0.8)
    except ValueError as error:
        print(f"Invalid coverage correctly rejected: {error}")

    try:
        price_elasticity(100, 100, 1_000, 900)
    except ValueError as error:
        print(f"Unchanged price correctly rejected: {error}")

    print("\nCase study complete.")


# ============================================================================
# 12. SELF-TESTS
# ============================================================================

def run_self_tests() -> None:
    assert calculate_top_down_tam(1_000, 0.5, 100) == 50_000
    assert calculate_sam(100_000, 0.5, 0.8) == 40_000
    assert calculate_som(40_000, 0.1) == 4_000
    assert round(calculate_cagr(100, 121, 2), 10) == round(0.1, 10)

    assert round(four_firm_concentration_ratio([0.4, 0.3, 0.2, 0.05, 0.05]), 5) == 0.95
    assert round(calculate_herfindahl_hirschman_index([0.5, 0.5]), 5) == 0.5

    assert conversion_rate(20, 100) == 0.2
    assert round(weighted_average([10, 20], [1, 3]), 5) == 17.5

    lower, upper = confidence_interval_proportion(50, 100)
    assert 0 < lower < 0.5 < upper < 1

    segment = Segment("Test", SegmentType.BEHAVIORAL, 1_000, 0.2, 2, 50)
    assert segment.annual_market_value() == 20_000

    print("All self-tests passed.")


# ============================================================================
# 13. ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run_self_tests()
    run_case_study()
