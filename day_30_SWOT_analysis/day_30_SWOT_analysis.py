"""
SWOT Analysis: Strengths, Weaknesses, Opportunities, Threats,
and Strategic Implications

A self-contained implementation that teaches and demonstrates SWOT analysis
from basic concepts through weighted scoring, evidence management, scenario
analysis, prioritization, sensitivity testing, and strategic implication
generation.

The implementation uses a fictional but realistic product case: a cloud-based
procurement analytics platform entering the mid-market manufacturing sector.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from statistics import mean
from typing import Iterable
import csv
import json
import math


class SWOTCategory(str, Enum):
    """The four SWOT quadrants."""

    STRENGTH = "Strength"
    WEAKNESS = "Weakness"
    OPPORTUNITY = "Opportunity"
    THREAT = "Threat"


@dataclass(frozen=True)
class SWOTFactor:
    """
    A single SWOT factor.

    Importance represents how strategically important the factor is on a
    0.0-1.0 scale. Confidence represents confidence in the evidence supporting
    the factor. Impact represents the expected magnitude of the factor.
    """

    id: str
    category: SWOTCategory
    title: str
    description: str
    importance: float
    impact: float
    confidence: float
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name, value in (
            ("importance", self.importance),
            ("impact", self.impact),
            ("confidence", self.confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1.")

        if not self.title.strip():
            raise ValueError("A SWOT factor requires a title.")

        if not self.description.strip():
            raise ValueError("A SWOT factor requires a description.")

    @property
    def weighted_impact(self) -> float:
        """Combine importance, impact, and evidence confidence."""
        return self.importance * self.impact * self.confidence

    @property
    def signed_score(self) -> float:
        """
        Convert weighted impact into a directional value.

        Internal factors:
          Strengths contribute positively.
          Weaknesses contribute negatively.

        External factors:
          Opportunities contribute positively.
          Threats contribute negatively.
        """
        positive_categories = {
            SWOTCategory.STRENGTH,
            SWOTCategory.OPPORTUNITY,
        }
        direction = 1 if self.category in positive_categories else -1
        return direction * self.weighted_impact


@dataclass
class SWOTMatrix:
    """Container for factors belonging to one SWOT analysis."""

    name: str
    objective: str
    factors: list[SWOTFactor] = field(default_factory=list)

    def add_factor(self, factor: SWOTFactor) -> None:
        if any(existing.id == factor.id for existing in self.factors):
            raise ValueError(f"Duplicate factor ID: {factor.id}")
        self.factors.append(factor)

    def by_category(self, category: SWOTCategory) -> list[SWOTFactor]:
        return [factor for factor in self.factors if factor.category == category]

    def validate_balance(self) -> list[str]:
        """
        Detect common analytical problems without claiming that every SWOT
        must have equal numbers of factors.
        """
        warnings: list[str] = []

        for category in SWOTCategory:
            factors = self.by_category(category)
            if not factors:
                warnings.append(f"No factors have been recorded for {category.value}.")

        if len(self.factors) > 24:
            warnings.append(
                "The matrix contains many factors; prioritization may be needed "
                "to prevent a long but strategically weak SWOT."
            )

        titles = [factor.title.casefold() for factor in self.factors]
        if len(titles) != len(set(titles)):
            warnings.append("Duplicate or near-duplicate factor titles detected.")

        return warnings

    def total_score(self) -> float:
        return sum(factor.signed_score for factor in self.factors)

    def category_score(self, category: SWOTCategory) -> float:
        return sum(factor.signed_score for factor in self.by_category(category))

    def ranked_factors(self) -> list[SWOTFactor]:
        return sorted(
            self.factors,
            key=lambda factor: abs(factor.signed_score),
            reverse=True,
        )


@dataclass(frozen=True)
class StrategicAction:
    """
    A strategy derived from the interaction of two SWOT categories.

    The four interaction types have distinct meanings:

    SO: use strengths to capture opportunities.
    WO: use opportunities to reduce or overcome weaknesses.
    ST: use strengths to reduce exposure to threats.
    WT: reduce weaknesses and avoid or contain threats.
    """

    code: str
    title: str
    rationale: str
    supporting_factors: tuple[str, ...]
    priority: float


@dataclass(frozen=True)
class Scenario:
    """A possible external environment used for sensitivity analysis."""

    name: str
    opportunity_multiplier: float
    threat_multiplier: float
    description: str

    def __post_init__(self) -> None:
        if self.opportunity_multiplier < 0 or self.threat_multiplier < 0:
            raise ValueError("Scenario multipliers cannot be negative.")


def build_example_analysis() -> SWOTMatrix:
    """Build a realistic SWOT analysis for a procurement analytics product."""
    analysis = SWOTMatrix(
        name="ProcureSight Mid-Market Expansion",
        objective=(
            "Assess whether a cloud procurement analytics platform should "
            "expand into mid-market manufacturing organizations."
        ),
    )

    factors = [
        SWOTFactor(
            id="S1",
            category=SWOTCategory.STRENGTH,
            title="Strong procurement analytics engine",
            description=(
                "The product identifies spend leakage, supplier concentration, "
                "and purchasing anomalies from transaction data."
            ),
            importance=0.90,
            impact=0.85,
            confidence=0.90,
            evidence=(
                "Validated analytics workflows in existing customer deployments",
                "Repeatable anomaly-detection results",
            ),
        ),
        SWOTFactor(
            id="S2",
            category=SWOTCategory.STRENGTH,
            title="Fast implementation model",
            description=(
                "Standardized data connectors and templates reduce the time "
                "required to establish a first analytical baseline."
            ),
            importance=0.80,
            impact=0.75,
            confidence=0.85,
            evidence=("Existing implementation playbooks", "Connector library"),
        ),
        SWOTFactor(
            id="S3",
            category=SWOTCategory.STRENGTH,
            title="Domain-specific procurement expertise",
            description=(
                "The product team understands supplier management, spend "
                "classification, sourcing workflows, and procurement KPIs."
            ),
            importance=0.75,
            impact=0.80,
            confidence=0.90,
            evidence=("Procurement specialists on product team",),
        ),
        SWOTFactor(
            id="W1",
            category=SWOTCategory.WEAKNESS,
            title="Limited brand recognition",
            description=(
                "The company has substantially less market awareness than "
                "large enterprise software vendors."
            ),
            importance=0.85,
            impact=0.75,
            confidence=0.90,
            evidence=("Low unaided awareness in target segment",),
        ),
        SWOTFactor(
            id="W2",
            category=SWOTCategory.WEAKNESS,
            title="Small implementation team",
            description=(
                "A rapid increase in customer volume could create onboarding "
                "capacity constraints."
            ),
            importance=0.80,
            impact=0.80,
            confidence=0.85,
            evidence=("Current implementation staffing capacity",),
        ),
        SWOTFactor(
            id="W3",
            category=SWOTCategory.WEAKNESS,
            title="Limited international coverage",
            description=(
                "Localization, regional supplier data, and local support "
                "capabilities are less mature outside the home market."
            ),
            importance=0.65,
            impact=0.65,
            confidence=0.80,
            evidence=("Current deployment geography",),
        ),
        SWOTFactor(
            id="O1",
            category=SWOTCategory.OPPORTUNITY,
            title="Growing demand for procurement visibility",
            description=(
                "Manufacturers are seeking stronger visibility into supplier "
                "costs, purchasing patterns, and procurement savings."
            ),
            importance=0.90,
            impact=0.85,
            confidence=0.75,
            evidence=("Customer discovery interviews", "Pipeline observations"),
        ),
        SWOTFactor(
            id="O2",
            category=SWOTCategory.OPPORTUNITY,
            title="Expansion of cloud procurement systems",
            description=(
                "More organizations are adopting cloud systems that can "
                "provide standardized data access for analytics."
            ),
            importance=0.80,
            impact=0.80,
            confidence=0.75,
            evidence=("Observed technology adoption patterns",),
        ),
        SWOTFactor(
            id="O3",
            category=SWOTCategory.OPPORTUNITY,
            title="Partner-led distribution",
            description=(
                "ERP consultants and procurement advisory firms could provide "
                "distribution without requiring a large direct sales force."
            ),
            importance=0.75,
            impact=0.75,
            confidence=0.70,
            evidence=("Identified implementation partners",),
        ),
        SWOTFactor(
            id="T1",
            category=SWOTCategory.THREAT,
            title="Large software vendors bundling analytics",
            description=(
                "Established enterprise platforms may bundle procurement "
                "analytics into broader software contracts."
            ),
            importance=0.90,
            impact=0.85,
            confidence=0.85,
            evidence=("Competitive product announcements",),
        ),
        SWOTFactor(
            id="T2",
            category=SWOTCategory.THREAT,
            title="Long enterprise procurement cycles",
            description=(
                "Manufacturing organizations may require security, finance, "
                "procurement, and IT approvals before purchasing."
            ),
            importance=0.80,
            impact=0.75,
            confidence=0.85,
            evidence=("Observed sales-cycle durations",),
        ),
        SWOTFactor(
            id="T3",
            category=SWOTCategory.THREAT,
            title="Data integration and quality risk",
            description=(
                "Supplier, purchase-order, invoice, and category data may "
                "differ substantially between organizations."
            ),
            importance=0.85,
            impact=0.80,
            confidence=0.90,
            evidence=("Historical implementation issues",),
        ),
    ]

    for factor in factors:
        analysis.add_factor(factor)

    return analysis


def print_matrix(analysis: SWOTMatrix) -> None:
    """Display the four SWOT categories without mixing their meanings."""
    print(f"\nSWOT ANALYSIS: {analysis.name}")
    print(f"Objective: {analysis.objective}\n")

    descriptions = {
        SWOTCategory.STRENGTH: "Internal capabilities that create advantage.",
        SWOTCategory.WEAKNESS: "Internal limitations that reduce performance.",
        SWOTCategory.OPPORTUNITY: "External conditions that may create value.",
        SWOTCategory.THREAT: "External conditions that may create risk.",
    }

    for category in SWOTCategory:
        print(f"[{category.value.upper()}]")
        print(descriptions[category])
        for factor in analysis.by_category(category):
            print(
                f"  {factor.id}: {factor.title} "
                f"(weighted impact={factor.weighted_impact:.3f})"
            )
            print(f"      {factor.description}")
        print()


def calculate_internal_external_balance(
    analysis: SWOTMatrix,
) -> dict[str, float]:
    """
    Separate internal factors from external factors.

    This is important because internal capability and external environment
    should not be interpreted as the same type of evidence.
    """
    internal = (
        analysis.category_score(SWOTCategory.STRENGTH)
        + analysis.category_score(SWOTCategory.WEAKNESS)
    )

    external = (
        analysis.category_score(SWOTCategory.OPPORTUNITY)
        + analysis.category_score(SWOTCategory.THREAT)
    )

    return {
        "internal_net": internal,
        "external_net": external,
        "combined_net": internal + external,
    }


def generate_strategic_actions(analysis: SWOTMatrix) -> list[StrategicAction]:
    """
    Generate strategy implications from category interactions.

    The function deliberately uses different logic for each interaction:
    SO is growth-oriented, WO addresses capability gaps, ST uses defenses,
    and WT focuses on exposure reduction.
    """
    strengths = analysis.by_category(SWOTCategory.STRENGTH)
    weaknesses = analysis.by_category(SWOTCategory.WEAKNESS)
    opportunities = analysis.by_category(SWOTCategory.OPPORTUNITY)
    threats = analysis.by_category(SWOTCategory.THREAT)

    strongest = max(strengths, key=lambda factor: factor.weighted_impact)
    largest_weakness = max(weaknesses, key=lambda factor: factor.weighted_impact)
    strongest_opportunity = max(
        opportunities, key=lambda factor: factor.weighted_impact
    )
    strongest_threat = max(threats, key=lambda factor: factor.weighted_impact)

    return [
        StrategicAction(
            code="SO",
            title="Use the analytics engine to target procurement visibility demand",
            rationale=(
                f"{strongest.id} provides an internal capability that directly "
                f"supports {strongest_opportunity.id}. The strategic implication "
                "is to package the capability around measurable procurement "
                "visibility outcomes."
            ),
            supporting_factors=(strongest.id, strongest_opportunity.id),
            priority=(
                strongest.weighted_impact
                * strongest_opportunity.weighted_impact
            ),
        ),
        StrategicAction(
            code="WO",
            title="Use partner distribution to compensate for market coverage gaps",
            rationale=(
                f"{largest_weakness.id} constrains direct expansion while "
                f"{strongest_opportunity.id} creates demand. Partner-led "
                "distribution can reduce dependence on direct brand-building "
                "and implementation capacity."
            ),
            supporting_factors=(largest_weakness.id, "O3"),
            priority=largest_weakness.weighted_impact * 0.75,
        ),
        StrategicAction(
            code="ST",
            title="Differentiate through procurement-specific analytical depth",
            rationale=(
                f"{strongest_threat.id} creates competitive pressure. The "
                f"company can use {strongest.id} and domain expertise to "
                "differentiate on procurement-specific analytical workflows "
                "rather than competing only on bundled software breadth."
            ),
            supporting_factors=(strongest.id, "S3", strongest_threat.id),
            priority=strongest.weighted_impact * strongest_threat.weighted_impact,
        ),
        StrategicAction(
            code="WT",
            title="Control integration exposure before scaling customer volume",
            rationale=(
                "Data integration risk combined with limited implementation "
                "capacity can produce delivery failures during rapid expansion. "
                "Standardized onboarding gates, data-quality checks, and "
                "capacity limits reduce this combined exposure."
            ),
            supporting_factors=("W2", "T3"),
            priority=0.80 * 0.80,
        ),
    ]


def scenario_score(analysis: SWOTMatrix, scenario: Scenario) -> float:
    """
    Recalculate the SWOT score under a changed external environment.

    Internal factors remain unchanged. Opportunities and threats are adjusted
    because the scenario represents a change in external conditions.
    """
    total = 0.0

    for factor in analysis.factors:
        if factor.category == SWOTCategory.OPPORTUNITY:
            total += factor.weighted_impact * scenario.opportunity_multiplier
        elif factor.category == SWOTCategory.THREAT:
            total -= factor.weighted_impact * scenario.threat_multiplier
        else:
            total += factor.signed_score

    return total


def run_sensitivity_analysis(
    analysis: SWOTMatrix,
    scenarios: Iterable[Scenario],
) -> list[tuple[str, float]]:
    """Compare the analysis under several external scenarios."""
    results = []
    for scenario in scenarios:
        results.append((scenario.name, scenario_score(analysis, scenario)))
    return results


def factor_sensitivity(
    factor: SWOTFactor,
    importance_change: float = 0.10,
) -> tuple[float, float]:
    """
    Show how changing a factor's importance affects its contribution.

    Sensitivity analysis is useful because a SWOT factor is not an objective
    measurement merely because a numerical score has been assigned to it.
    """
    lower_importance = max(0.0, factor.importance - importance_change)
    upper_importance = min(1.0, factor.importance + importance_change)

    lower = lower_importance * factor.impact * factor.confidence
    upper = upper_importance * factor.impact * factor.confidence

    return lower, upper


def save_analysis_json(analysis: SWOTMatrix, path: Path) -> None:
    """Persist the analysis in a machine-readable format."""
    payload = {
        "name": analysis.name,
        "objective": analysis.objective,
        "factors": [
            {
                "id": factor.id,
                "category": factor.category.value,
                "title": factor.title,
                "description": factor.description,
                "importance": factor.importance,
                "impact": factor.impact,
                "confidence": factor.confidence,
                "weighted_impact": round(factor.weighted_impact, 6),
                "evidence": list(factor.evidence),
            }
            for factor in analysis.factors
        ],
    }

    path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def export_factor_csv(analysis: SWOTMatrix, path: Path) -> None:
    """Export factors for spreadsheet-based strategic analysis."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "id",
                "category",
                "title",
                "importance",
                "impact",
                "confidence",
                "weighted_impact",
                "signed_score",
            ]
        )

        for factor in analysis.factors:
            writer.writerow(
                [
                    factor.id,
                    factor.category.value,
                    factor.title,
                    factor.importance,
                    factor.impact,
                    factor.confidence,
                    round(factor.weighted_impact, 6),
                    round(factor.signed_score, 6),
                ]
            )


def demonstrate_validation(analysis: SWOTMatrix) -> None:
    """Demonstrate validation and a deliberate invalid-factor failure."""
    print("\nVALIDATION")

    warnings = analysis.validate_balance()
    if warnings:
        for warning in warnings:
            print(f"  Warning: {warning}")
    else:
        print("  No structural warnings detected.")

    try:
        SWOTFactor(
            id="INVALID",
            category=SWOTCategory.THREAT,
            title="Invalid factor",
            description="This factor demonstrates validation behavior.",
            importance=1.2,
            impact=0.5,
            confidence=0.5,
        )
    except ValueError as error:
        print(f"  Validation correctly rejected invalid data: {error}")


def demonstrate_edge_cases() -> None:
    """
    Demonstrate analytical edge cases.

    A zero-confidence factor has no weighted contribution. This is useful when
    an analyst records a hypothesis but has no evidence supporting it.
    """
    unverified = SWOTFactor(
        id="EDGE-1",
        category=SWOTCategory.OPPORTUNITY,
        title="Unverified market hypothesis",
        description="A possible market demand signal without sufficient evidence.",
        importance=0.90,
        impact=0.90,
        confidence=0.0,
    )

    print("\nEDGE CASES")
    print(
        f"  Unverified opportunity weighted impact: "
        f"{unverified.weighted_impact:.3f}"
    )
    print(
        "  Interpretation: the opportunity can remain visible in the matrix, "
        "but its unsupported claim does not receive quantitative weight."
    )


def print_priorities(analysis: SWOTMatrix) -> None:
    """Display factors whose combined importance, impact, and confidence are high."""
    print("\nPRIORITY FACTORS")

    for factor in analysis.ranked_factors()[:6]:
        print(
            f"  {factor.id} | {factor.category.value:<11} | "
            f"{factor.weighted_impact:.3f} | {factor.title}"
        )


def print_strategic_implications(actions: list[StrategicAction]) -> None:
    """Display SO, WO, ST, and WT strategic implications."""
    print("\nSTRATEGIC IMPLICATIONS")

    for action in actions:
        print(f"  {action.code}: {action.title}")
        print(f"     Priority: {action.priority:.3f}")
        print(f"     Rationale: {action.rationale}")
        print(
            f"     Supporting factors: "
            f"{', '.join(action.supporting_factors)}"
        )


def main() -> None:
    """Run the complete SWOT demonstration."""
    analysis = build_example_analysis()

    print_matrix(analysis)

    demonstrate_validation(analysis)

    balance = calculate_internal_external_balance(analysis)
    print("\nINTERNAL AND EXTERNAL BALANCE")
    for name, value in balance.items():
        print(f"  {name}: {value:.3f}")

    print_priorities(analysis)

    actions = generate_strategic_actions(analysis)
    print_strategic_implications(actions)

    scenarios = [
        Scenario(
            name="Base environment",
            opportunity_multiplier=1.0,
            threat_multiplier=1.0,
            description="Current assumptions remain unchanged.",
        ),
        Scenario(
            name="Faster demand growth",
            opportunity_multiplier=1.25,
            threat_multiplier=1.0,
            description="Addressable demand develops more strongly.",
        ),
        Scenario(
            name="Competitive pressure",
            opportunity_multiplier=0.90,
            threat_multiplier=1.30,
            description="Bundled competitors become more aggressive.",
        ),
        Scenario(
            name="Integration-heavy market",
            opportunity_multiplier=0.95,
            threat_multiplier=1.20,
            description="Data quality and implementation barriers increase.",
        ),
    ]

    print("\nSCENARIO SENSITIVITY")
    for name, score in run_sensitivity_analysis(analysis, scenarios):
        print(f"  {name:<25} net score={score:.3f}")

    key_factor = max(analysis.factors, key=lambda item: item.weighted_impact)
    lower, upper = factor_sensitivity(key_factor)

    print("\nFACTOR SENSITIVITY")
    print(f"  Factor: {key_factor.id} - {key_factor.title}")
    print(f"  Current contribution: {key_factor.weighted_impact:.3f}")
    print(f"  Contribution at lower importance: {lower:.3f}")
    print(f"  Contribution at higher importance: {upper:.3f}")

    demonstrate_edge_cases()

    output_directory = Path("swot_output")
    output_directory.mkdir(exist_ok=True)

    json_path = output_directory / "swot_analysis.json"
    csv_path = output_directory / "swot_factors.csv"

    save_analysis_json(analysis, json_path)
    export_factor_csv(analysis, csv_path)

    print("\nPERSISTENCE")
    print(f"  JSON written to: {json_path}")
    print(f"  CSV written to:  {csv_path}")

    print("\nANALYTICAL INTERPRETATION")
    print(
        f"  The matrix contains {len(analysis.factors)} factors across four "
        "distinct analytical categories."
    )
    print(
        "  Numerical scores prioritize discussion; they do not transform "
        "judgment-based SWOT inputs into objective measurements."
    )
    print(
        "  Strategic implications should be tested against evidence, "
        "resources, timing, risk tolerance, and alternatives before execution."
    )

    average_confidence = mean(
        factor.confidence for factor in analysis.factors
    )
    print(f"  Average evidence confidence: {average_confidence:.3f}")


if __name__ == "__main__":
    main()
