"""
Product Opportunity Analysis Engine

This executable case study models three connected product-management activities:

- Opportunity identification: detecting unmet needs from structured customer evidence.
- Opportunity sizing: estimating the addressable opportunity using explicit assumptions.
- Opportunity scoring: comparing opportunities with a transparent weighted model.

The implementation intentionally keeps these activities distinct. Identification produces
candidate opportunities from evidence. Sizing estimates economic or user impact. Scoring
uses evidence and sizing results to support prioritization without pretending that a score
is a substitute for product judgment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import ceil
from statistics import mean, median
from typing import Iterable


class OpportunityType(Enum):
    """Product opportunity categories used by the case study."""

    ACQUISITION = "acquisition"
    ACTIVATION = "activation"
    RETENTION = "retention"
    MONETIZATION = "monetization"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"


@dataclass(frozen=True)
class CustomerSignal:
    """
    A piece of customer or business evidence.

    Signals are kept separate from opportunities so identification can be audited.
    A high-severity signal does not automatically mean the resulting opportunity
    deserves the highest priority.
    """

    signal_id: str
    source: str
    description: str
    affected_users: int
    frequency_per_month: float
    severity: float
    evidence_confidence: float
    category: OpportunityType

    def __post_init__(self) -> None:
        if self.affected_users < 0:
            raise ValueError("affected_users cannot be negative")
        if self.frequency_per_month < 0:
            raise ValueError("frequency_per_month cannot be negative")
        for name, value in (
            ("severity", self.severity),
            ("evidence_confidence", self.evidence_confidence),
        ):
            if not 0 <= value <= 10:
                raise ValueError(f"{name} must be between 0 and 10")


@dataclass
class ProductOpportunity:
    """
    A synthesized product opportunity.

    Identification fields describe the customer problem. Sizing fields describe
    potential scale. Scoring fields describe prioritization criteria.
    """

    opportunity_id: str
    title: str
    problem_statement: str
    customer_segment: str
    category: OpportunityType
    signals: list[CustomerSignal] = field(default_factory=list)

    # Explicit sizing assumptions.
    target_population: int = 0
    annual_value_per_affected_user: float = 0.0
    reachable_share: float = 0.0
    adoption_rate: float = 0.0

    # Product prioritization inputs.
    strategic_alignment: float = 0.0
    customer_value: float = 0.0
    confidence: float = 0.0
    effort: float = 0.0
    time_to_value: float = 0.0
    risk: float = 0.0

    # Derived values.
    tam_value: float = 0.0
    sam_value: float = 0.0
    expected_value: float = 0.0
    score: float = 0.0

    def add_signal(self, signal: CustomerSignal) -> None:
        if signal.category != self.category:
            raise ValueError(
                f"Signal {signal.signal_id} belongs to {signal.category.value}, "
                f"not {self.category.value}"
            )
        self.signals.append(signal)

    @property
    def signal_count(self) -> int:
        return len(self.signals)

    @property
    def evidence_strength(self) -> float:
        """
        Weighted evidence strength.

        Severity captures the magnitude of the problem while confidence captures
        how trustworthy the observation is. Multiplying them prevents weak evidence
        from looking equivalent to well-supported severe evidence.
        """
        if not self.signals:
            return 0.0

        weighted = [
            signal.severity * signal.evidence_confidence
            for signal in self.signals
        ]
        return min(10.0, mean(weighted))

    def validate_sizing_inputs(self) -> None:
        if self.target_population < 0:
            raise ValueError("target_population cannot be negative")
        if self.annual_value_per_affected_user < 0:
            raise ValueError("annual_value_per_affected_user cannot be negative")
        if not 0 <= self.reachable_share <= 1:
            raise ValueError("reachable_share must be between 0 and 1")
        if not 0 <= self.adoption_rate <= 1:
            raise ValueError("adoption_rate must be between 0 and 1")

    def validate_scoring_inputs(self) -> None:
        for name, value in (
            ("strategic_alignment", self.strategic_alignment),
            ("customer_value", self.customer_value),
            ("confidence", self.confidence),
            ("effort", self.effort),
            ("time_to_value", self.time_to_value),
            ("risk", self.risk),
        ):
            if not 0 <= value <= 10:
                raise ValueError(f"{name} must be between 0 and 10")


@dataclass(frozen=True)
class ScoreWeights:
    """Weights for a transparent weighted opportunity score."""

    customer_value: float
    strategic_alignment: float
    confidence: float
    effort: float
    time_to_value: float
    risk: float

    def __post_init__(self) -> None:
        values = (
            self.customer_value,
            self.strategic_alignment,
            self.confidence,
            self.effort,
            self.time_to_value,
            self.risk,
        )
        if any(value < 0 for value in values):
            raise ValueError("Score weights cannot be negative")
        if sum(values) == 0:
            raise ValueError("At least one score weight must be positive")

    @property
    def normalized(self) -> dict[str, float]:
        total = (
            self.customer_value
            + self.strategic_alignment
            + self.confidence
            + self.effort
            + self.time_to_value
            + self.risk
        )
        return {
            "customer_value": self.customer_value / total,
            "strategic_alignment": self.strategic_alignment / total,
            "confidence": self.confidence / total,
            "effort": self.effort / total,
            "time_to_value": self.time_to_value / total,
            "risk": self.risk / total,
        }


def identify_opportunities(
    signals: Iterable[CustomerSignal],
    *,
    minimum_signals: int = 1,
    minimum_evidence_strength: float = 2.0,
) -> list[ProductOpportunity]:
    """
    Synthesize customer signals into candidate opportunities.

    Signals are grouped by product problem category. In a real product discovery
    system, clustering would normally combine qualitative research, analytics,
    support data, interviews, surveys, and behavioral evidence. This deterministic
    implementation makes the synthesis auditable.
    """

    if minimum_signals < 1:
        raise ValueError("minimum_signals must be at least 1")

    grouped: dict[OpportunityType, list[CustomerSignal]] = {}

    for signal in signals:
        grouped.setdefault(signal.category, []).append(signal)

    opportunities: list[ProductOpportunity] = []

    titles = {
        OpportunityType.ACQUISITION: (
            "Reduce acquisition friction",
            "Prospective customers encounter avoidable friction before reaching product value.",
        ),
        OpportunityType.ACTIVATION: (
            "Improve first-value activation",
            "New users struggle to reach a meaningful first outcome quickly.",
        ),
        OpportunityType.RETENTION: (
            "Reduce recurring workflow friction",
            "Existing customers encounter repeated problems that can weaken continued usage.",
        ),
        OpportunityType.MONETIZATION: (
            "Improve monetization experience",
            "Customers experience friction around paid value, packaging, or conversion.",
        ),
        OpportunityType.OPERATIONAL_EFFICIENCY: (
            "Reduce operational product friction",
            "Internal or customer-facing workflows consume unnecessary time and effort.",
        ),
    }

    for category, category_signals in grouped.items():
        candidate = ProductOpportunity(
            opportunity_id=f"OPP-{len(opportunities) + 1:03d}",
            title=titles[category][0],
            problem_statement=titles[category][1],
            customer_segment="Observed segment",
            category=category,
            signals=category_signals,
        )

        if (
            candidate.signal_count >= minimum_signals
            and candidate.evidence_strength >= minimum_evidence_strength
        ):
            opportunities.append(candidate)

    return opportunities


def calculate_tam_sam_expected_value(opportunity: ProductOpportunity) -> None:
    """
    Calculate a simple opportunity-sizing model.

    TAM represents the theoretical value if every member of the target population
    experienced the modeled annual value.

    SAM narrows TAM by the portion the product can realistically reach.

    Expected value narrows SAM by the assumed adoption rate.

    These figures are scenario estimates, not guaranteed revenue forecasts.
    """

    opportunity.validate_sizing_inputs()

    opportunity.tam_value = (
        opportunity.target_population
        * opportunity.annual_value_per_affected_user
    )

    opportunity.sam_value = opportunity.tam_value * opportunity.reachable_share

    opportunity.expected_value = opportunity.sam_value * opportunity.adoption_rate


def calculate_opportunity_score(
    opportunity: ProductOpportunity,
    weights: ScoreWeights,
) -> float:
    """
    Calculate a weighted score from 0 to 10.

    Effort and risk are inverted because lower effort and lower risk are favorable.
    Confidence combines explicit product judgment with measured evidence strength.
    """

    opportunity.validate_scoring_inputs()

    normalized = weights.normalized

    evidence_adjusted_confidence = (
        opportunity.confidence * 0.6
        + opportunity.evidence_strength * 0.4
    )

    components = {
        "customer_value": opportunity.customer_value,
        "strategic_alignment": opportunity.strategic_alignment,
        "confidence": evidence_adjusted_confidence,
        "effort": 10.0 - opportunity.effort,
        "time_to_value": opportunity.time_to_value,
        "risk": 10.0 - opportunity.risk,
    }

    score = sum(
        components[name] * weight
        for name, weight in normalized.items()
    )

    opportunity.score = round(score, 3)
    return opportunity.score


def sensitivity_analysis(
    opportunity: ProductOpportunity,
    weights: ScoreWeights,
    adoption_rates: Iterable[float],
) -> list[dict[str, float]]:
    """
    Show how sizing changes when adoption assumptions change.

    The prioritization score is intentionally not changed by adoption scenarios;
    this separates opportunity size from the qualitative/strategic score.
    """

    opportunity.validate_sizing_inputs()
    results: list[dict[str, float]] = []

    for adoption in adoption_rates:
        if not 0 <= adoption <= 1:
            raise ValueError("Each adoption scenario must be between 0 and 1")

        expected = opportunity.sam_value * adoption
        results.append(
            {
                "adoption_rate": adoption,
                "expected_value": round(expected, 2),
                "current_score": opportunity.score,
            }
        )

    return results


def evidence_summary(opportunity: ProductOpportunity) -> dict[str, object]:
    """Return an auditable evidence summary for product discovery."""

    sources = sorted({signal.source for signal in opportunity.signals})
    affected_users = sum(signal.affected_users for signal in opportunity.signals)

    return {
        "opportunity": opportunity.title,
        "category": opportunity.category.value,
        "signals": opportunity.signal_count,
        "sources": sources,
        "observed_affected_users": affected_users,
        "evidence_strength": round(opportunity.evidence_strength, 2),
    }


def print_opportunity(opportunity: ProductOpportunity) -> None:
    """Print a compact but decision-useful opportunity record."""

    print(f"\n{opportunity.opportunity_id}: {opportunity.title}")
    print(f"  Category: {opportunity.category.value}")
    print(f"  Problem: {opportunity.problem_statement}")
    print(f"  Evidence strength: {opportunity.evidence_strength:.2f}/10")
    print(f"  TAM: ${opportunity.tam_value:,.0f}")
    print(f"  SAM: ${opportunity.sam_value:,.0f}")
    print(f"  Expected value: ${opportunity.expected_value:,.0f}")
    print(f"  Score: {opportunity.score:.3f}/10")


def demonstrate_basic_identification() -> list[ProductOpportunity]:
    """Demonstrate opportunity identification from heterogeneous product evidence."""

    print("=== Opportunity identification ===")

    signals = [
        CustomerSignal(
            signal_id="SUP-101",
            source="support",
            description="Users cannot quickly determine which onboarding step is blocking progress.",
            affected_users=420,
            frequency_per_month=120,
            severity=7.5,
            evidence_confidence=0.90,
            category=OpportunityType.ACTIVATION,
        ),
        CustomerSignal(
            signal_id="INT-205",
            source="customer_interviews",
            description="New administrators report that the initial setup requires too many decisions.",
            affected_users=35,
            frequency_per_month=1,
            severity=8.0,
            evidence_confidence=0.85,
            category=OpportunityType.ACTIVATION,
        ),
        CustomerSignal(
            signal_id="ANA-311",
            source="product_analytics",
            description="A large share of newly registered accounts never complete the core setup action.",
            affected_users=1800,
            frequency_per_month=1,
            severity=8.5,
            evidence_confidence=0.95,
            category=OpportunityType.ACTIVATION,
        ),
        CustomerSignal(
            signal_id="SUP-404",
            source="support",
            description="Returning customers repeatedly export reports manually before monthly reviews.",
            affected_users=700,
            frequency_per_month=700,
            severity=6.5,
            evidence_confidence=0.88,
            category=OpportunityType.OPERATIONAL_EFFICIENCY,
        ),
        CustomerSignal(
            signal_id="INT-410",
            source="customer_interviews",
            description="Operations teams spend substantial time preparing the same management report.",
            affected_users=50,
            frequency_per_month=1,
            severity=7.0,
            evidence_confidence=0.82,
            category=OpportunityType.OPERATIONAL_EFFICIENCY,
        ),
        CustomerSignal(
            signal_id="BILL-520",
            source="billing_analytics",
            description="Users who reach the paid feature page frequently abandon before selecting a plan.",
            affected_users=950,
            frequency_per_month=1,
            severity=7.2,
            evidence_confidence=0.92,
            category=OpportunityType.MONETIZATION,
        ),
        CustomerSignal(
            signal_id="INT-525",
            source="sales_interviews",
            description="Prospects report uncertainty about which paid tier matches their use case.",
            affected_users=75,
            frequency_per_month=1,
            severity=6.8,
            evidence_confidence=0.78,
            category=OpportunityType.MONETIZATION,
        ),
    ]

    opportunities = identify_opportunities(
        signals,
        minimum_signals=2,
        minimum_evidence_strength=2.0,
    )

    for opportunity in opportunities:
        print(evidence_summary(opportunity))

    return opportunities


def configure_sizing(opportunities: list[ProductOpportunity]) -> None:
    """
    Apply opportunity-specific sizing assumptions.

    Each category receives different assumptions because the unit of value differs:
    activation affects conversion to productive use, operational efficiency affects
    labor time, and monetization affects paid conversion.
    """

    assumptions = {
        OpportunityType.ACTIVATION: {
            "segment": "New business accounts",
            "population": 24000,
            "annual_value": 480.0,
            "reachable": 0.70,
            "adoption": 0.28,
        },
        OpportunityType.OPERATIONAL_EFFICIENCY: {
            "segment": "Operations-heavy business accounts",
            "population": 9000,
            "annual_value": 850.0,
            "reachable": 0.65,
            "adoption": 0.22,
        },
        OpportunityType.MONETIZATION: {
            "segment": "Qualified product users",
            "population": 18000,
            "annual_value": 1200.0,
            "reachable": 0.75,
            "adoption": 0.18,
        },
    }

    for opportunity in opportunities:
        values = assumptions[opportunity.category]
        opportunity.customer_segment = values["segment"]
        opportunity.target_population = values["population"]
        opportunity.annual_value_per_affected_user = values["annual_value"]
        opportunity.reachable_share = values["reachable"]
        opportunity.adoption_rate = values["adoption"]
        calculate_tam_sam_expected_value(opportunity)


def configure_scores(opportunities: list[ProductOpportunity]) -> ScoreWeights:
    """
    Configure scores according to a product strategy that values customer impact,
    strategic alignment, confidence, speed, and manageable delivery risk.
    """

    weights = ScoreWeights(
        customer_value=0.30,
        strategic_alignment=0.20,
        confidence=0.15,
        effort=0.10,
        time_to_value=0.10,
        risk=0.15,
    )

    score_inputs = {
        OpportunityType.ACTIVATION: {
            "strategic_alignment": 9.0,
            "customer_value": 9.0,
            "confidence": 8.5,
            "effort": 5.0,
            "time_to_value": 8.0,
            "risk": 3.0,
        },
        OpportunityType.OPERATIONAL_EFFICIENCY: {
            "strategic_alignment": 7.0,
            "customer_value": 8.0,
            "confidence": 8.0,
            "effort": 6.5,
            "time_to_value": 6.5,
            "risk": 4.0,
        },
        OpportunityType.MONETIZATION: {
            "strategic_alignment": 8.5,
            "customer_value": 7.5,
            "confidence": 7.5,
            "effort": 4.5,
            "time_to_value": 7.5,
            "risk": 4.5,
        },
    }

    for opportunity in opportunities:
        values = score_inputs[opportunity.category]
        for attribute, value in values.items():
            setattr(opportunity, attribute, value)

        calculate_opportunity_score(opportunity, weights)

    return weights


def demonstrate_sensitivity(opportunity: ProductOpportunity) -> None:
    """Demonstrate why opportunity sizing should expose assumptions."""

    print(f"\n=== Sizing sensitivity: {opportunity.title} ===")

    scenarios = [0.10, 0.20, 0.30, 0.40, 0.50]

    for scenario in sensitivity_analysis(
        opportunity,
        ScoreWeights(
            customer_value=1,
            strategic_alignment=1,
            confidence=1,
            effort=1,
            time_to_value=1,
            risk=1,
        ),
        scenarios,
    ):
        print(
            f"  Adoption {scenario['adoption_rate']:.0%}"
            f" -> expected annual value ${scenario['expected_value']:,.0f}"
        )


def validate_edge_cases() -> None:
    """Exercise failure conditions that commonly corrupt opportunity models."""

    print("\n=== Validation and edge cases ===")

    try:
        ProductOpportunity(
            opportunity_id="BAD-001",
            title="Invalid sizing",
            problem_statement="Invalid assumption",
            customer_segment="Test",
            category=OpportunityType.ACTIVATION,
            target_population=100,
            annual_value_per_affected_user=500,
            reachable_share=1.2,
            adoption_rate=0.2,
        ).validate_sizing_inputs()
    except ValueError as exc:
        print(f"  Rejected invalid reachability: {exc}")

    try:
        ScoreWeights(
            customer_value=-1,
            strategic_alignment=1,
            confidence=1,
            effort=1,
            time_to_value=1,
            risk=1,
        )
    except ValueError as exc:
        print(f"  Rejected negative scoring weight: {exc}")

    try:
        CustomerSignal(
            signal_id="BAD-002",
            source="analytics",
            description="Invalid confidence",
            affected_users=10,
            frequency_per_month=2,
            severity=5,
            evidence_confidence=12,
            category=OpportunityType.ACTIVATION,
        )
    except ValueError as exc:
        print(f"  Rejected invalid evidence confidence: {exc}")


def compare_sizing_and_scoring(opportunities: list[ProductOpportunity]) -> None:
    """
    Show why opportunity sizing and scoring are different dimensions.

    A large estimated opportunity can have low confidence or high implementation
    effort. A score therefore should not simply be an alias for market size.
    """

    print("\n=== Sizing versus prioritization ===")

    for opportunity in sorted(
        opportunities,
        key=lambda item: item.expected_value,
        reverse=True,
    ):
        print(
            f"  {opportunity.title:<35}"
            f" expected=${opportunity.expected_value:>12,.0f}"
            f" score={opportunity.score:>5.2f}"
        )


def demonstrate_product_management_workflow() -> None:
    """
    Run the complete product-opportunity analysis.

    The flow intentionally preserves the distinction between:
    evidence -> opportunity -> sizing assumptions -> prioritization score.
    """

    opportunities = demonstrate_basic_identification()
    configure_sizing(opportunities)
    configure_scores(opportunities)

    print("\n=== Opportunity portfolio ===")

    for opportunity in opportunities:
        print_opportunity(opportunity)

    ranked = sorted(
        opportunities,
        key=lambda item: item.score,
        reverse=True,
    )

    print("\n=== Score ordering for analysis ===")
    for position, opportunity in enumerate(ranked, start=1):
        print(
            f"  {position}. {opportunity.opportunity_id}"
            f" | score={opportunity.score:.3f}"
            f" | expected value=${opportunity.expected_value:,.0f}"
        )

    if opportunities:
        demonstrate_sensitivity(opportunities[0])

    compare_sizing_and_scoring(opportunities)
    validate_edge_cases()


def main() -> None:
    """Program entry point."""

    demonstrate_product_management_workflow()

    print("\n=== Practical interpretation ===")
    print(
        "Opportunity identification converts observed customer evidence into a "
        "defined problem. Opportunity sizing quantifies scale using explicit "
        "assumptions. Opportunity scoring combines product judgment and evidence "
        "to make prioritization criteria visible and reviewable."
    )
    print(
        "The model deliberately exposes assumptions so that product teams can "
        "challenge the evidence, population, reachable share, adoption rate, "
        "customer value, effort, timing, and risk independently."
    )


if __name__ == "__main__":
    main()
