"""
TAM / SAM / SOM
===============
Total Addressable Market, Serviceable Available Market, Serviceable Obtainable Market

A standalone study and implementation file covering:
- Market-sizing terminology and hierarchy
- Top-down, bottom-up, and value-theory approaches
- TAM, SAM, SOM calculations
- Revenue, customer-count, usage, and transaction models
- Percentage and constraint-based filtering
- Assumptions and scenario modeling
- Sensitivity analysis
- Growth and time-horizon analysis
- Validation and error handling
- Unit economics
- Capacity constraints
- Geographic, segment, product, channel, and regulatory constraints
- Double-counting risks
- Edge cases
- Monte Carlo simulation
- Confidence ranges
- A practical B2B SaaS market-sizing case study
- Testing and reporting

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import ceil, floor, isfinite
from random import Random
from statistics import mean, median, stdev
from typing import Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL TERMINOLOGY
# ---------------------------------------------------------------------------

class MarketLevel(Enum):
    """The three levels of the standard market-sizing hierarchy."""

    TAM = "Total Addressable Market"
    SAM = "Serviceable Available Market"
    SOM = "Serviceable Obtainable Market"


class SizingMethod(Enum):
    """Common market-sizing methods."""

    TOP_DOWN = "Top-down"
    BOTTOM_UP = "Bottom-up"
    VALUE_THEORY = "Value-theory"


@dataclass(frozen=True)
class MarketSize:
    """
    Represents a market size in currency and customer units.

    currency:
        Annual market revenue represented by the estimate.

    customers:
        Number of potential customers represented by the estimate.
    """

    currency: float
    customers: int

    def __post_init__(self) -> None:
        if not isfinite(self.currency) or self.currency < 0:
            raise ValueError("currency must be finite and non-negative")
        if self.customers < 0:
            raise ValueError("customers must be non-negative")

    @property
    def revenue_per_customer(self) -> float:
        """Average annual revenue represented by each customer."""
        if self.customers == 0:
            return 0.0
        return self.currency / self.customers

    def percentage_of(self, other: "MarketSize") -> float:
        """Return this market as a percentage of another market."""
        if other.currency == 0:
            return 0.0
        return self.currency / other.currency * 100.0


@dataclass(frozen=True)
class Assumption:
    """Documents an input used in a market-sizing calculation."""

    name: str
    value: float
    unit: str
    source: str = "Analyst assumption"
    confidence: str = "medium"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Assumption name cannot be empty")
        if not isfinite(self.value):
            raise ValueError("Assumption value must be finite")
        if self.confidence not in {"low", "medium", "high"}:
            raise ValueError("confidence must be low, medium, or high")


@dataclass
class MarketModel:
    """
    General-purpose market-sizing model.

    The model keeps customer and revenue assumptions separate. This is
    important because a customer-count estimate and a revenue estimate can
    fail independently if pricing or adoption assumptions are incorrect.
    """

    name: str
    customers: int
    annual_revenue_per_customer: float
    assumptions: list[Assumption] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.customers < 0:
            raise ValueError("customers cannot be negative")
        if self.annual_revenue_per_customer < 0:
            raise ValueError("revenue per customer cannot be negative")

    @property
    def annual_market_revenue(self) -> float:
        return self.customers * self.annual_revenue_per_customer

    def to_market_size(self) -> MarketSize:
        return MarketSize(
            currency=self.annual_market_revenue,
            customers=self.customers,
        )


# ---------------------------------------------------------------------------
# 2. BASIC TAM / SAM / SOM RELATIONSHIP
# ---------------------------------------------------------------------------

def calculate_market_hierarchy(
    tam: MarketSize,
    sam_customer_share: float,
    som_customer_share: float,
) -> tuple[MarketSize, MarketSize, MarketSize]:
    """
    Calculate SAM and SOM from customer-share constraints.

    Important:
        sam_customer_share is relative to TAM.
        som_customer_share is relative to SAM.

    Example:
        TAM = 100,000 customers
        SAM = 30% of TAM = 30,000
        SOM = 10% of SAM = 3,000
    """
    validate_percentage(sam_customer_share, "sam_customer_share")
    validate_percentage(som_customer_share, "som_customer_share")

    sam_customers = floor(tam.customers * sam_customer_share / 100)
    sam_revenue = tam.revenue_per_customer * sam_customers
    sam = MarketSize(sam_revenue, sam_customers)

    som_customers = floor(sam.customers * som_customer_share / 100)
    som_revenue = sam.revenue_per_customer * som_customers
    som = MarketSize(som_revenue, som_customers)

    return tam, sam, som


def validate_percentage(value: float, name: str = "percentage") -> None:
    """Validate a percentage expressed from 0 through 100."""
    if not isfinite(value) or not 0 <= value <= 100:
        raise ValueError(f"{name} must be between 0 and 100")


def percentage(value: float, percent: float) -> float:
    """Return a percentage of a value."""
    validate_percentage(percent)
    return value * percent / 100.0


def format_currency(value: float, currency: str = "$") -> str:
    """Format large market values for readable output."""
    return f"{currency}{value:,.2f}"


def format_market_value(value: float) -> str:
    """
    Human-readable market notation.

    This intentionally keeps the raw calculation available elsewhere.
    """
    absolute = abs(value)
    if absolute >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:.2f}"


# ---------------------------------------------------------------------------
# 3. TOP-DOWN MARKET SIZING
# ---------------------------------------------------------------------------

def top_down_market_size(
    broad_market_revenue: float,
    segment_share: float,
    geographic_share: float,
    product_fit_share: float,
) -> float:
    """
    Estimate a target market by progressively filtering a broad market.

    Formula:
        Broad Market
        × Segment %
        × Geography %
        × Product Fit %
        = Estimated Target Market

    Top-down calculations are fast but can become misleading when the
    percentages are arbitrary or when the source market definitions differ.
    """
    for name, value in (
        ("segment_share", segment_share),
        ("geographic_share", geographic_share),
        ("product_fit_share", product_fit_share),
    ):
        validate_percentage(value, name)

    if broad_market_revenue < 0:
        raise ValueError("broad_market_revenue cannot be negative")

    return broad_market_revenue * (
        segment_share / 100
    ) * (
        geographic_share / 100
    ) * (
        product_fit_share / 100
    )


# ---------------------------------------------------------------------------
# 4. BOTTOM-UP MARKET SIZING
# ---------------------------------------------------------------------------

def bottom_up_market_size(
    number_of_target_customers: int,
    annual_price_per_customer: float,
    expected_penetration: float = 100.0,
) -> MarketSize:
    """
    Estimate market size from identifiable customers and pricing.

    Formula:
        Target Customers
        × Price per Customer
        × Penetration
        = Revenue Estimate

    Bottom-up models are often easier to audit because each major input
    corresponds to a concrete operational quantity.
    """
    if number_of_target_customers < 0:
        raise ValueError("number_of_target_customers cannot be negative")
    if annual_price_per_customer < 0:
        raise ValueError("annual_price_per_customer cannot be negative")
    validate_percentage(expected_penetration, "expected_penetration")

    effective_customers = floor(
        number_of_target_customers * expected_penetration / 100
    )

    return MarketSize(
        currency=effective_customers * annual_price_per_customer,
        customers=effective_customers,
    )


# ---------------------------------------------------------------------------
# 5. USAGE-BASED MARKET SIZING
# ---------------------------------------------------------------------------

def usage_based_market_size(
    users: int,
    transactions_per_user_per_year: float,
    revenue_per_transaction: float,
) -> float:
    """
    Estimate annual market revenue from usage.

    Formula:
        Users × Transactions/User/Year × Revenue/Transaction
    """
    if users < 0:
        raise ValueError("users cannot be negative")
    if transactions_per_user_per_year < 0:
        raise ValueError("transactions cannot be negative")
    if revenue_per_transaction < 0:
        raise ValueError("revenue per transaction cannot be negative")

    return users * transactions_per_user_per_year * revenue_per_transaction


# ---------------------------------------------------------------------------
# 6. SEGMENTED BOTTOM-UP MODEL
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CustomerSegment:
    """A separately modeled customer segment."""

    name: str
    customers: int
    annual_price: float
    adoption_rate: float

    def market_size(self) -> MarketSize:
        return bottom_up_market_size(
            number_of_target_customers=self.customers,
            annual_price_per_customer=self.annual_price,
            expected_penetration=self.adoption_rate,
        )


def segmented_market_size(
    segments: Iterable[CustomerSegment],
) -> MarketSize:
    """
    Combine multiple mutually exclusive customer segments.

    A crucial modeling requirement is that segments must not overlap.
    """
    segments = list(segments)

    if not segments:
        return MarketSize(0.0, 0)

    sizes = [segment.market_size() for segment in segments]

    return MarketSize(
        currency=sum(size.currency for size in sizes),
        customers=sum(size.customers for size in sizes),
    )


# ---------------------------------------------------------------------------
# 7. FILTER-BASED SAM MODEL
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MarketConstraint:
    """
    A constraint used to convert TAM into SAM.

    Examples:
        geographic eligibility
        supported industry
        company size
        regulatory availability
        product compatibility
        distribution availability
    """

    name: str
    eligible_share: float

    def __post_init__(self) -> None:
        validate_percentage(self.eligible_share, self.name)


def apply_constraints(
    market: MarketSize,
    constraints: Sequence[MarketConstraint],
) -> MarketSize:
    """
    Apply independent multiplicative constraints.

    This assumes the constraints are modeled as conditional shares rather
    than raw percentages that can overlap.

    For correlated constraints, a simple multiplication can overstate or
    understate the market. In such cases, use a customer-level dataset or
    explicit segment intersections.
    """
    customers = float(market.customers)

    for constraint in constraints:
        customers *= constraint.eligible_share / 100.0

    final_customers = floor(customers)

    return MarketSize(
        currency=final_customers * market.revenue_per_customer,
        customers=final_customers,
    )


# ---------------------------------------------------------------------------
# 8. SOM WITH OPERATIONAL CAPACITY
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CapacityModel:
    """
    Operational limits that can constrain realistic obtainable revenue.
    """

    sales_representatives: int
    new_customers_per_rep_per_year: int
    implementation_capacity: int
    support_capacity: int

    @property
    def annual_customer_capacity(self) -> int:
        sales_capacity = (
            self.sales_representatives
            * self.new_customers_per_rep_per_year
        )
        return min(
            sales_capacity,
            self.implementation_capacity,
            self.support_capacity,
        )


def capacity_constrained_som(
    sam: MarketSize,
    capacity: CapacityModel,
    strategic_share_of_sam: float,
) -> MarketSize:
    """
    Estimate SOM while respecting operational capacity.

    SOM is not necessarily simply a percentage of SAM. A company may have
    sufficient demand but insufficient sales, implementation, support,
    capital, manufacturing, or distribution capacity.
    """
    validate_percentage(strategic_share_of_sam, "strategic_share_of_sam")

    desired_customers = floor(
        sam.customers * strategic_share_of_sam / 100
    )

    obtainable_customers = min(
        desired_customers,
        capacity.annual_customer_capacity,
    )

    return MarketSize(
        currency=obtainable_customers * sam.revenue_per_customer,
        customers=obtainable_customers,
    )


# ---------------------------------------------------------------------------
# 9. COMPOUND ANNUAL GROWTH
# ---------------------------------------------------------------------------

def compound_growth(
    initial_value: float,
    annual_growth_rate: float,
    years: int,
) -> float:
    """
    Project a market using compound growth.

    Example:
        1,000 × (1 + 0.10)^5
    """
    if initial_value < 0:
        raise ValueError("initial_value cannot be negative")
    if years < 0:
        raise ValueError("years cannot be negative")
    if annual_growth_rate <= -100:
        raise ValueError("annual_growth_rate must be above -100%")

    return initial_value * (
        1 + annual_growth_rate / 100
    ) ** years


def market_projection(
    initial_market: MarketSize,
    annual_growth_rate: float,
    years: int,
) -> list[MarketSize]:
    """Return year-by-year market projections."""
    if years < 0:
        raise ValueError("years cannot be negative")

    return [
        MarketSize(
            currency=compound_growth(
                initial_market.currency,
                annual_growth_rate,
                year,
            ),
            customers=round(
                compound_growth(
                    initial_market.customers,
                    annual_growth_rate,
                    year,
                )
            ),
        )
        for year in range(years + 1)
    ]


# ---------------------------------------------------------------------------
# 10. SENSITIVITY ANALYSIS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SensitivityResult:
    parameter: str
    low_value: float
    base_value: float
    high_value: float
    low_output: float
    base_output: float
    high_output: float


def sensitivity_analysis(
    parameter: str,
    low_value: float,
    base_value: float,
    high_value: float,
    calculation: Callable[[float], float],
) -> SensitivityResult:
    """
    Recalculate a market estimate at low, base, and high assumptions.

    This is useful for identifying which assumptions have the greatest
    influence on the market estimate.
    """
    if not low_value <= base_value <= high_value:
        raise ValueError("Expected low <= base <= high")

    return SensitivityResult(
        parameter=parameter,
        low_value=low_value,
        base_value=base_value,
        high_value=high_value,
        low_output=calculation(low_value),
        base_output=calculation(base_value),
        high_output=calculation(high_value),
    )


# ---------------------------------------------------------------------------
# 11. UNIT ECONOMICS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UnitEconomics:
    """Basic customer-level economics."""

    annual_revenue_per_customer: float
    gross_margin: float
    annual_customer_acquisition_cost: float
    annual_churn_rate: float

    def __post_init__(self) -> None:
        if self.annual_revenue_per_customer < 0:
            raise ValueError("revenue cannot be negative")
        if self.annual_customer_acquisition_cost < 0:
            raise ValueError("CAC cannot be negative")
        validate_percentage(self.gross_margin, "gross_margin")
        validate_percentage(self.annual_churn_rate, "annual_churn_rate")

    @property
    def annual_gross_profit(self) -> float:
        return self.annual_revenue_per_customer * self.gross_margin / 100

    @property
    def estimated_customer_lifetime_years(self) -> float:
        if self.annual_churn_rate == 0:
            return float("inf")
        return 1 / (self.annual_churn_rate / 100)

    @property
    def estimated_ltv(self) -> float:
        lifetime = self.estimated_customer_lifetime_years
        if lifetime == float("inf"):
            return float("inf")
        return self.annual_gross_profit * lifetime

    @property
    def ltv_to_cac(self) -> float:
        if self.annual_customer_acquisition_cost == 0:
            return float("inf")
        return self.estimated_ltv / self.annual_customer_acquisition_cost


# ---------------------------------------------------------------------------
# 12. VALUE-THEORY MODEL
# ---------------------------------------------------------------------------

def value_theory_price(
    economic_value_created: float,
    customer_value_capture_rate: float,
) -> float:
    """
    Estimate a price from customer economic value.

    This is not a claim about what the customer will actually pay.
    Willingness to pay, competition, switching costs, budget constraints,
    and procurement behavior must be validated independently.
    """
    if economic_value_created < 0:
        raise ValueError("economic_value_created cannot be negative")
    validate_percentage(
        customer_value_capture_rate,
        "customer_value_capture_rate",
    )
    return economic_value_created * customer_value_capture_rate / 100


# ---------------------------------------------------------------------------
# 13. MONTE CARLO MARKET ESTIMATION
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SimulationResult:
    """Statistics generated by a market-size simulation."""

    samples: tuple[float, ...]
    minimum: float
    p10: float
    p50: float
    p90: float
    maximum: float
    average: float


def percentile(sorted_values: Sequence[float], p: float) -> float:
    """Calculate a percentile using linear interpolation."""
    if not sorted_values:
        raise ValueError("Cannot calculate percentile of empty data")
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")

    position = (len(sorted_values) - 1) * p / 100
    lower = floor(position)
    upper = ceil(position)

    if lower == upper:
        return sorted_values[lower]

    fraction = position - lower
    return (
        sorted_values[lower]
        + fraction * (sorted_values[upper] - sorted_values[lower])
    )


def monte_carlo_market_size(
    simulations: int,
    customer_range: tuple[int, int],
    annual_price_range: tuple[float, float],
    adoption_range: tuple[float, float],
    seed: int = 42,
) -> SimulationResult:
    """
    Estimate a market distribution rather than a single point estimate.

    Uniform distributions are used here for teaching purposes. Production
    analysis should choose probability distributions based on evidence.
    """
    if simulations <= 0:
        raise ValueError("simulations must be positive")

    min_customers, max_customers = customer_range
    min_price, max_price = annual_price_range
    min_adoption, max_adoption = adoption_range

    if not 0 <= min_customers <= max_customers:
        raise ValueError("Invalid customer range")
    if not 0 <= min_price <= max_price:
        raise ValueError("Invalid price range")
    if not 0 <= min_adoption <= max_adoption <= 100:
        raise ValueError("Invalid adoption range")

    rng = Random(seed)
    values: list[float] = []

    for _ in range(simulations):
        customers = rng.randint(min_customers, max_customers)
        price = rng.uniform(min_price, max_price)
        adoption = rng.uniform(min_adoption, max_adoption)

        effective_customers = customers * adoption / 100
        values.append(effective_customers * price)

    values.sort()

    return SimulationResult(
        samples=tuple(values),
        minimum=values[0],
        p10=percentile(values, 10),
        p50=percentile(values, 50),
        p90=percentile(values, 90),
        maximum=values[-1],
        average=mean(values),
    )


# ---------------------------------------------------------------------------
# 14. CONSISTENCY CHECKS
# ---------------------------------------------------------------------------

def validate_hierarchy(
    tam: MarketSize,
    sam: MarketSize,
    som: MarketSize,
) -> list[str]:
    """
    Return structural warnings instead of silently accepting an invalid
    market hierarchy.
    """
    warnings: list[str] = []

    if sam.customers > tam.customers:
        warnings.append("SAM customers exceed TAM customers.")

    if som.customers > sam.customers:
        warnings.append("SOM customers exceed SAM customers.")

    if sam.currency > tam.currency:
        warnings.append("SAM revenue exceeds TAM revenue.")

    if som.currency > sam.currency:
        warnings.append("SOM revenue exceeds SAM revenue.")

    return warnings


# ---------------------------------------------------------------------------
# 15. PRINTING AND REPORTING
# ---------------------------------------------------------------------------

def print_market(label: str, market: MarketSize) -> None:
    """Print a consistent market-size report."""
    print(
        f"{label:<5} | "
        f"Customers: {market.customers:>10,} | "
        f"Revenue: {format_currency(market.currency):>18} | "
        f"Revenue/customer: {format_currency(market.revenue_per_customer)}"
    )


def print_separator(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# 16. BEGINNER EXAMPLE
# ---------------------------------------------------------------------------

def beginner_example() -> None:
    print_separator("BEGINNER EXAMPLE: SIMPLE TAM / SAM / SOM")

    tam = MarketSize(
        currency=10_000_000,
        customers=100_000,
    )

    _, sam, som = calculate_market_hierarchy(
        tam=tam,
        sam_customer_share=30,
        som_customer_share=10,
    )

    print_market("TAM", tam)
    print_market("SAM", sam)
    print_market("SOM", som)

    print(
        "\nInterpretation:"
        "\nTAM represents the broad theoretical market."
        "\nSAM represents the part that fits the defined service constraints."
        "\nSOM represents the portion modeled as obtainable under the chosen assumption."
    )


# ---------------------------------------------------------------------------
# 17. TOP-DOWN EXAMPLE
# ---------------------------------------------------------------------------

def top_down_example() -> None:
    print_separator("TOP-DOWN EXAMPLE")

    broad_market = 5_000_000_000

    target_market = top_down_market_size(
        broad_market_revenue=broad_market,
        segment_share=20,
        geographic_share=40,
        product_fit_share=60,
    )

    print(f"Broad market: {format_currency(broad_market)}")
    print(f"Segment share: 20%")
    print(f"Geographic share: 40%")
    print(f"Product-fit share: 60%")
    print(f"Estimated target market: {format_currency(target_market)}")


# ---------------------------------------------------------------------------
# 18. BOTTOM-UP EXAMPLE
# ---------------------------------------------------------------------------

def bottom_up_example() -> None:
    print_separator("BOTTOM-UP EXAMPLE")

    market = bottom_up_market_size(
        number_of_target_customers=25_000,
        annual_price_per_customer=2_400,
        expected_penetration=100,
    )

    print_market("TAM", market)

    obtainable = bottom_up_market_size(
        number_of_target_customers=25_000,
        annual_price_per_customer=2_400,
        expected_penetration=8,
    )

    print_market("SOM", obtainable)


# ---------------------------------------------------------------------------
# 19. SEGMENT EXAMPLE
# ---------------------------------------------------------------------------

def segmented_example() -> None:
    print_separator("SEGMENTED BOTTOM-UP EXAMPLE")

    segments = [
        CustomerSegment(
            name="Small businesses",
            customers=50_000,
            annual_price=600,
            adoption_rate=100,
        ),
        CustomerSegment(
            name="Mid-market businesses",
            customers=12_000,
            annual_price=3_000,
            adoption_rate=100,
        ),
        CustomerSegment(
            name="Enterprise businesses",
            customers=2_000,
            annual_price=18_000,
            adoption_rate=100,
        ),
    ]

    total = segmented_market_size(segments)

    for segment in segments:
        size = segment.market_size()
        print(
            f"{segment.name:<24} "
            f"{size.customers:>8,} customers | "
            f"{format_currency(size.currency):>16}"
        )

    print("-" * 78)
    print_market("TAM", total)


# ---------------------------------------------------------------------------
# 20. SAM CONSTRAINT EXAMPLE
# ---------------------------------------------------------------------------

def constraint_example() -> None:
    print_separator("SAM USING EXPLICIT CONSTRAINTS")

    tam = MarketSize(
        currency=100_000_000,
        customers=100_000,
    )

    constraints = [
        MarketConstraint("Supported geography", 60),
        MarketConstraint("Supported industry", 50),
        MarketConstraint("Product compatibility", 70),
    ]

    sam = apply_constraints(tam, constraints)

    print_market("TAM", tam)

    for constraint in constraints:
        print(
            f"{constraint.name:<28}: "
            f"{constraint.eligible_share:.1f}%"
        )

    print_market("SAM", sam)


# ---------------------------------------------------------------------------
# 21. CAPACITY-CONSTRAINED SOM EXAMPLE
# ---------------------------------------------------------------------------

def capacity_example() -> None:
    print_separator("CAPACITY-CONSTRAINED SOM")

    sam = MarketSize(
        currency=120_000_000,
        customers=20_000,
    )

    capacity = CapacityModel(
        sales_representatives=10,
        new_customers_per_rep_per_year=120,
        implementation_capacity=900,
        support_capacity=1_000,
    )

    som = capacity_constrained_som(
        sam=sam,
        capacity=capacity,
        strategic_share_of_sam=20,
    )

    print_market("SAM", sam)
    print(
        f"Sales capacity: {capacity.sales_representatives * capacity.new_customers_per_rep_per_year:,}"
    )
    print(f"Implementation capacity: {capacity.implementation_capacity:,}")
    print(f"Support capacity: {capacity.support_capacity:,}")
    print(f"Effective annual customer capacity: {capacity.annual_customer_capacity:,}")
    print_market("SOM", som)


# ---------------------------------------------------------------------------
# 22. UNIT ECONOMICS EXAMPLE
# ---------------------------------------------------------------------------

def unit_economics_example() -> None:
    print_separator("UNIT ECONOMICS")

    economics = UnitEconomics(
        annual_revenue_per_customer=3_000,
        gross_margin=80,
        annual_customer_acquisition_cost=1_500,
        annual_churn_rate=10,
    )

    print(f"Annual revenue/customer: {format_currency(economics.annual_revenue_per_customer)}")
    print(f"Gross profit/customer/year: {format_currency(economics.annual_gross_profit)}")
    print(f"Estimated lifetime: {economics.estimated_customer_lifetime_years:.2f} years")
    print(f"Estimated LTV: {format_currency(economics.estimated_ltv)}")
    print(f"LTV/CAC: {economics.ltv_to_cac:.2f}x")

    print(
        "\nMarket size describes opportunity; unit economics describe the economics"
        "\nof serving customers. A large market does not automatically imply an"
        "\nattractive business."
    )


# ---------------------------------------------------------------------------
# 23. VALUE-THEORY EXAMPLE
# ---------------------------------------------------------------------------

def value_theory_example() -> None:
    print_separator("VALUE-THEORY PRICING")

    economic_value = 20_000
    capture_rate = 15

    price = value_theory_price(
        economic_value_created=economic_value,
        customer_value_capture_rate=capture_rate,
    )

    print(f"Economic value created: {format_currency(economic_value)}")
    print(f"Illustrative value capture: {capture_rate}%")
    print(f"Illustrative annual price: {format_currency(price)}")


# ---------------------------------------------------------------------------
# 24. SENSITIVITY EXAMPLE
# ---------------------------------------------------------------------------

def sensitivity_example() -> None:
    print_separator("SENSITIVITY ANALYSIS")

    customers = 10_000
    adoption = 20

    result = sensitivity_analysis(
        parameter="Annual price",
        low_value=1_000,
        base_value=2_000,
        high_value=3_500,
        calculation=lambda price: (
            customers * adoption / 100 * price
        ),
    )

    print(f"Parameter: {result.parameter}")
    print(f"Low:  {result.low_value:,.0f} -> {format_currency(result.low_output)}")
    print(f"Base: {result.base_value:,.0f} -> {format_currency(result.base_output)}")
    print(f"High: {result.high_value:,.0f} -> {format_currency(result.high_output)}")


# ---------------------------------------------------------------------------
# 25. GROWTH PROJECTION EXAMPLE
# ---------------------------------------------------------------------------

def growth_example() -> None:
    print_separator("MARKET GROWTH PROJECTION")

    market = MarketSize(
        currency=50_000_000,
        customers=10_000,
    )

    projections = market_projection(
        initial_market=market,
        annual_growth_rate=12,
        years=5,
    )

    for year, projection in enumerate(projections):
        print(
            f"Year {year}: "
            f"{projection.customers:>8,} customers | "
            f"{format_currency(projection.currency):>18}"
        )


# ---------------------------------------------------------------------------
# 26. MONTE CARLO EXAMPLE
# ---------------------------------------------------------------------------

def simulation_example() -> None:
    print_separator("MONTE CARLO MARKET-SIZE SIMULATION")

    result = monte_carlo_market_size(
        simulations=5_000,
        customer_range=(8_000, 15_000),
        annual_price_range=(1_500, 3_500),
        adoption_range=(10, 30),
        seed=42,
    )

    print(f"Simulations: {len(result.samples):,}")
    print(f"Minimum:    {format_currency(result.minimum)}")
    print(f"P10:        {format_currency(result.p10)}")
    print(f"Median:     {format_currency(result.p50)}")
    print(f"P90:        {format_currency(result.p90)}")
    print(f"Maximum:    {format_currency(result.maximum)}")
    print(f"Mean:       {format_currency(result.average)}")


# ---------------------------------------------------------------------------
# 27. COMPLETE B2B SAAS CASE STUDY
# ---------------------------------------------------------------------------

def b2b_saas_case_study() -> tuple[MarketSize, MarketSize, MarketSize]:
    """
    A complete illustrative market-sizing workflow.

    Scenario:
        A hypothetical B2B analytics platform sells annual subscriptions
        to businesses.

    TAM:
        All businesses in the defined broad market that could theoretically
        buy the product.

    SAM:
        Businesses satisfying geography, industry, company-size, and
        technical compatibility requirements.

    SOM:
        Customers the company can realistically serve in the selected
        planning period, after considering go-to-market and implementation
        capacity.
    """
    print_separator("COMPLETE B2B SAAS CASE STUDY")

    # Step 1: Define TAM from a customer census.
    tam_segments = [
        CustomerSegment(
            name="Small business",
            customers=80_000,
            annual_price=900,
            adoption_rate=100,
        ),
        CustomerSegment(
            name="Mid-market",
            customers=20_000,
            annual_price=4_000,
            adoption_rate=100,
        ),
        CustomerSegment(
            name="Enterprise",
            customers=5_000,
            annual_price=15_000,
            adoption_rate=100,
        ),
    ]

    tam = segmented_market_size(tam_segments)

    # Step 2: Define SAM constraints as conditional filters.
    sam = apply_constraints(
        tam,
        [
            MarketConstraint("Target geography", 50),
            MarketConstraint("Target industries", 60),
            MarketConstraint("Compatible technology", 70),
        ],
    )

    # Step 3: Define SOM using both strategic penetration and capacity.
    capacity = CapacityModel(
        sales_representatives=15,
        new_customers_per_rep_per_year=80,
        implementation_capacity=1_100,
        support_capacity=1_500,
    )

    som = capacity_constrained_som(
        sam=sam,
        capacity=capacity,
        strategic_share_of_sam=15,
    )

    print_market("TAM", tam)
    print_market("SAM", sam)
    print_market("SOM", som)

    warnings = validate_hierarchy(tam, sam, som)

    if warnings:
        print("\nValidation warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("\nHierarchy validation: PASSED")

    print(
        "\nKey distinction:"
        "\nTAM answers how large the broad theoretical opportunity is."
        "\nSAM answers how much of that opportunity fits the service definition."
        "\nSOM answers how much can be targeted and operationally served in the model."
    )

    return tam, sam, som


# ---------------------------------------------------------------------------
# 28. EDGE CASES
# ---------------------------------------------------------------------------

def edge_case_examples() -> None:
    print_separator("EDGE CASES")

    zero_market = MarketSize(currency=0, customers=0)
    print_market("ZERO", zero_market)

    print(
        "\nZero customers are valid and produce zero revenue."
        "\nRevenue-per-customer safely returns 0 instead of dividing by zero."
    )

    try:
        MarketSize(currency=-1, customers=10)
    except ValueError as error:
        print(f"Negative revenue rejected: {error}")

    try:
        bottom_up_market_size(
            number_of_target_customers=100,
            annual_price_per_customer=100,
            expected_penetration=125,
        )
    except ValueError as error:
        print(f"Invalid penetration rejected: {error}")

    try:
        top_down_market_size(
            broad_market_revenue=100_000,
            segment_share=110,
            geographic_share=50,
            product_fit_share=50,
        )
    except ValueError as error:
        print(f"Invalid market share rejected: {error}")


# ---------------------------------------------------------------------------
# 29. MINI TEST SUITE
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Small executable test suite using only the Python standard library."""
    print_separator("TESTS")

    tam = MarketSize(1_000, 100)
    assert tam.revenue_per_customer == 10

    result = bottom_up_market_size(100, 10, 50)
    assert result.customers == 50
    assert result.currency == 500

    top_down = top_down_market_size(
        1_000,
        50,
        50,
        50,
    )
    assert top_down == 125

    segments = [
        CustomerSegment("A", 100, 10, 100),
        CustomerSegment("B", 50, 20, 100),
    ]
    segmented = segmented_market_size(segments)
    assert segmented.customers == 150
    assert segmented.currency == 2_000

    hierarchy = calculate_market_hierarchy(
        MarketSize(1_000, 100),
        50,
        20,
    )

    assert hierarchy[1].customers == 50
    assert hierarchy[2].customers == 10

    assert compound_growth(100, 10, 2) == 121

    print("All tests passed.")


# ---------------------------------------------------------------------------
# 30. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Execute the educational market-sizing workbook.

    The examples intentionally use fictional numbers. Real TAM/SAM/SOM
    analysis requires clearly defined populations, dates, sources,
    segmentation rules, pricing assumptions, and validation.
    """
    print("=" * 78)
    print("TAM / SAM / SOM MARKET-SIZING STUDY")
    print("Total Addressable Market | Serviceable Available Market |")
    print("Serviceable Obtainable Market")
    print("=" * 78)

    beginner_example()
    top_down_example()
    bottom_up_example()
    segmented_example()
    constraint_example()
    capacity_example()
    unit_economics_example()
    value_theory_example()
    sensitivity_example()
    growth_example()
    simulation_example()
    b2b_saas_case_study()
    edge_case_examples()
    run_tests()

    print_separator("IMPORTANT MODELING PRINCIPLES")
    principles = [
        "Define the market before calculating it.",
        "Keep TAM, SAM, and SOM definitions mutually clear.",
        "Document every material assumption.",
        "Avoid multiplying overlapping percentages as if they were independent.",
        "Prefer identifiable customer counts for bottom-up models.",
        "Separate theoretical demand from operational capacity.",
        "Use multiple scenarios when uncertainty is material.",
        "Validate market boundaries, geography, segment, pricing, and time period.",
        "Do not confuse market size with revenue the company will actually earn.",
        "Do not use SOM as a disguised growth target without operational evidence.",
        "Revisit assumptions when product scope, pricing, geography, or competition changes.",
    ]

    for number, principle in enumerate(principles, 1):
        print(f"{number:>2}. {principle}")


if __name__ == "__main__":
    main()
