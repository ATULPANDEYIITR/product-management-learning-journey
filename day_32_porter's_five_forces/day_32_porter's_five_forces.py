"""
Porter's Five Forces: Competition, Suppliers, Buyers, Substitutes, New Entrants

A self-contained educational implementation of Porter's Five Forces framework.

The program models an industry using five distinct forces:
- Competitive rivalry
- Supplier bargaining power
- Buyer bargaining power
- Threat of substitutes
- Threat of new entrants

It progresses from a simple industry model to:
- structured evidence
- weighted force scoring
- validation
- scenario analysis
- sensitivity analysis
- strategic interpretation
- JSON persistence
- comparative industry analysis

The scores are analytical inputs, not objective measurements. A score should
always be supported by observable industry evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import math
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional


class Force(str, Enum):
    """The five forces in Porter's industry-structure framework."""

    RIVALRY = "Competitive Rivalry"
    SUPPLIERS = "Supplier Bargaining Power"
    BUYERS = "Buyer Bargaining Power"
    SUBSTITUTES = "Threat of Substitutes"
    ENTRANTS = "Threat of New Entrants"


FORCE_ORDER = [
    Force.RIVALRY,
    Force.SUPPLIERS,
    Force.BUYERS,
    Force.SUBSTITUTES,
    Force.ENTRANTS,
]


@dataclass
class Evidence:
    """
    Evidence supporting a force assessment.

    direction:
        positive means the evidence increases pressure from the force.
        negative means the evidence reduces pressure.
        neutral means the evidence is contextual rather than directional.
    """

    statement: str
    source: str
    direction: int = 1
    strength: float = 1.0

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Evidence statement cannot be empty.")
        if not self.source.strip():
            raise ValueError("Evidence source cannot be empty.")
        if self.direction not in (-1, 0, 1):
            raise ValueError("Evidence direction must be -1, 0, or 1.")
        if not 0 < self.strength <= 1:
            raise ValueError("Evidence strength must be between 0 and 1.")


@dataclass
class ForceAssessment:
    """
    Assessment for one force.

    score is normalized to 0..10:
        0 = very weak pressure
        10 = very strong pressure
    """

    force: Force
    score: float
    rationale: str
    evidence: List[Evidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 10:
            raise ValueError(f"{self.force.value} score must be between 0 and 10.")
        if not self.rationale.strip():
            raise ValueError("A force assessment requires a rationale.")

    @property
    def pressure_level(self) -> str:
        if self.score < 3:
            return "Low"
        if self.score < 5:
            return "Moderate-Low"
        if self.score < 7:
            return "Moderate-High"
        return "High"


@dataclass
class IndustryModel:
    """A complete Five Forces model for one industry."""

    industry: str
    market_definition: str
    geography: str
    time_horizon: str
    assessments: Dict[Force, ForceAssessment]

    def __post_init__(self) -> None:
        if not self.industry.strip():
            raise ValueError("Industry name cannot be empty.")
        if not self.market_definition.strip():
            raise ValueError("Market definition cannot be empty.")
        if not self.geography.strip():
            raise ValueError("Geography cannot be empty.")
        missing = set(FORCE_ORDER) - set(self.assessments)
        if missing:
            raise ValueError(
                "Industry model is missing forces: "
                + ", ".join(force.value for force in missing)
            )

    @property
    def average_pressure(self) -> float:
        return mean(self.assessments[force].score for force in FORCE_ORDER)

    @property
    def structural_pressure(self) -> str:
        """
        A descriptive interpretation of the average force pressure.

        This is not a profitability prediction. It describes the modeled
        intensity of industry pressures.
        """
        average = self.average_pressure
        if average < 3:
            return "Low structural pressure"
        if average < 5:
            return "Moderate-low structural pressure"
        if average < 7:
            return "Moderate-high structural pressure"
        return "High structural pressure"

    def strongest_force(self) -> ForceAssessment:
        return max(
            (self.assessments[force] for force in FORCE_ORDER),
            key=lambda assessment: assessment.score,
        )

    def weakest_force(self) -> ForceAssessment:
        return min(
            (self.assessments[force] for force in FORCE_ORDER),
            key=lambda assessment: assessment.score,
        )


def score_label(score: float) -> str:
    """Convert a numeric force score into a readable category."""
    if not 0 <= score <= 10:
        raise ValueError("Score must be between 0 and 10.")
    if score < 3:
        return "Low"
    if score < 5:
        return "Moderate-Low"
    if score < 7:
        return "Moderate-High"
    return "High"


def weighted_force_score(
    base_score: float,
    factors: Iterable[tuple[float, float]],
) -> float:
    """
    Calculate a weighted force score.

    Each factor is (impact, weight).
    impact must be in -10..10.
    weight must be positive.

    The result is bounded to 0..10 so that a scenario cannot produce an
    invalid force score.
    """
    if not 0 <= base_score <= 10:
        raise ValueError("Base score must be between 0 and 10.")

    weighted_delta = 0.0
    total_weight = 0.0

    for impact, weight in factors:
        if not -10 <= impact <= 10:
            raise ValueError("Scenario impact must be between -10 and 10.")
        if weight <= 0:
            raise ValueError("Scenario weights must be positive.")
        weighted_delta += impact * weight
        total_weight += weight

    if total_weight == 0:
        return base_score

    adjustment = weighted_delta / total_weight
    return max(0.0, min(10.0, base_score + adjustment))


def build_force(
    force: Force,
    score: float,
    rationale: str,
    evidence: List[Evidence],
) -> ForceAssessment:
    """Create an assessment while keeping construction explicit."""
    return ForceAssessment(
        force=force,
        score=score,
        rationale=rationale,
        evidence=evidence,
    )


def print_force_assessment(assessment: ForceAssessment) -> None:
    """Print one force with its supporting evidence."""
    print(f"\n{assessment.force.value}")
    print(f"Score: {assessment.score:.1f}/10 ({assessment.pressure_level})")
    print(f"Rationale: {assessment.rationale}")

    if assessment.evidence:
        print("Evidence:")
        for item in assessment.evidence:
            direction = {
                1: "increases pressure",
                -1: "reduces pressure",
                0: "contextual",
            }[item.direction]
            print(
                f"  - {item.statement} "
                f"[{item.source}; {direction}; strength={item.strength:.1f}]"
            )


def print_model(model: IndustryModel) -> None:
    """Display a complete Five Forces analysis."""
    print("=" * 78)
    print(f"PORTER'S FIVE FORCES: {model.industry}")
    print("=" * 78)
    print(f"Market definition: {model.market_definition}")
    print(f"Geography: {model.geography}")
    print(f"Time horizon: {model.time_horizon}")

    for force in FORCE_ORDER:
        print_force_assessment(model.assessments[force])

    print("\nStructural pressure")
    print(f"Average force pressure: {model.average_pressure:.2f}/10")
    print(f"Interpretation: {model.structural_pressure}")
    print(f"Highest modeled pressure: {model.strongest_force().force.value}")
    print(f"Lowest modeled pressure: {model.weakest_force().force.value}")


def force_driver_matrix() -> Dict[Force, List[str]]:
    """
    Return force-specific analytical drivers.

    The drivers are intentionally different because each force represents a
    different source of competitive pressure.
    """
    return {
        Force.RIVALRY: [
            "Number and relative size of competitors",
            "Industry growth rate",
            "Product differentiation",
            "Fixed-cost intensity",
            "Capacity expansion",
            "Exit barriers",
            "Frequency of price competition",
        ],
        Force.SUPPLIERS: [
            "Supplier concentration",
            "Availability of alternative suppliers",
            "Switching costs",
            "Uniqueness of supplier inputs",
            "Importance of the buyer to the supplier",
            "Possibility of supplier forward integration",
        ],
        Force.BUYERS: [
            "Buyer concentration",
            "Purchase volume",
            "Product differentiation",
            "Buyer switching costs",
            "Availability of information",
            "Buyer sensitivity to price",
            "Possibility of buyer backward integration",
        ],
        Force.SUBSTITUTES: [
            "Availability of alternative solutions",
            "Relative price-performance",
            "Customer switching costs",
            "Customer willingness to substitute",
            "Technological change",
            "Difference in convenience or quality",
        ],
        Force.ENTRANTS: [
            "Economies of scale",
            "Capital requirements",
            "Brand and customer loyalty",
            "Access to distribution",
            "Regulatory requirements",
            "Network effects",
            "Incumbent cost advantages",
        ],
    }


def demonstrate_beginner_model() -> IndustryModel:
    """
    Build a concrete analysis for a fictional but realistic B2B cloud
    accounting software market.

    The example is deliberately bounded to a market definition. Five Forces
    analysis becomes less meaningful when 'the software industry' is treated
    as one undifferentiated market.
    """
    return IndustryModel(
        industry="B2B Cloud Accounting Software for Small Businesses",
        market_definition=(
            "Subscription accounting, invoicing, expense tracking, and "
            "financial reporting software sold to small businesses"
        ),
        geography="India",
        time_horizon="2026-2030",
        assessments={
            Force.RIVALRY: build_force(
                Force.RIVALRY,
                7.2,
                (
                    "Several established products compete on price, integrations, "
                    "ease of use, automation, and accountant workflows."
                ),
                [
                    Evidence(
                        "Customers can compare several subscription products before purchase.",
                        "Market observation",
                        1,
                        0.9,
                    ),
                    Evidence(
                        "Cloud delivery lowers the friction of product comparison and switching.",
                        "Business-model analysis",
                        1,
                        0.8,
                    ),
                    Evidence(
                        "Accounting workflows can create meaningful switching friction.",
                        "Customer workflow analysis",
                        -1,
                        0.7,
                    ),
                ],
            ),
            Force.SUPPLIERS: build_force(
                Force.SUPPLIERS,
                4.6,
                (
                    "Cloud infrastructure and payment providers matter, but "
                    "software firms can generally use multiple infrastructure "
                    "and service providers."
                ),
                [
                    Evidence(
                        "Cloud infrastructure has multiple large providers.",
                        "Supplier landscape analysis",
                        -1,
                        0.8,
                    ),
                    Evidence(
                        "Payment and banking integrations can create dependency on specialized providers.",
                        "Integration analysis",
                        1,
                        0.7,
                    ),
                ],
            ),
            Force.BUYERS: build_force(
                Force.BUYERS,
                6.8,
                (
                    "Small-business customers are numerous, but many have low "
                    "switching tolerance and can compare prices and features."
                ),
                [
                    Evidence(
                        "Subscription buyers can compare plans before signing up.",
                        "Purchasing-process analysis",
                        1,
                        0.9,
                    ),
                    Evidence(
                        "Historical financial records increase migration effort.",
                        "Workflow analysis",
                        -1,
                        0.8,
                    ),
                    Evidence(
                        "Standard accounting functions are available from multiple vendors.",
                        "Product-category analysis",
                        1,
                        0.8,
                    ),
                ],
            ),
            Force.SUBSTITUTES: build_force(
                Force.SUBSTITUTES,
                5.9,
                (
                    "Spreadsheets, desktop accounting systems, outsourced bookkeeping, "
                    "and internal processes can perform parts of the same job."
                ),
                [
                    Evidence(
                        "Spreadsheets can handle basic bookkeeping for very small firms.",
                        "Alternative-solution analysis",
                        1,
                        0.8,
                    ),
                    Evidence(
                        "Integrated cloud workflows provide automation unavailable in basic spreadsheets.",
                        "Product capability analysis",
                        -1,
                        0.8,
                    ),
                ],
            ),
            Force.ENTRANTS: build_force(
                Force.ENTRANTS,
                6.1,
                (
                    "Software development is accessible, but trust, integrations, "
                    "distribution, compliance, and customer migration create barriers."
                ),
                [
                    Evidence(
                        "Cloud software can be developed without physical manufacturing assets.",
                        "Entry-structure analysis",
                        1,
                        0.9,
                    ),
                    Evidence(
                        "Accounting integrations and regulatory requirements raise entry complexity.",
                        "Implementation analysis",
                        -1,
                        0.9,
                    ),
                    Evidence(
                        "Established customer relationships can slow customer acquisition by entrants.",
                        "Distribution analysis",
                        -1,
                        0.8,
                    ),
                ],
            ),
        },
    )


def demonstrate_scenario_analysis(model: IndustryModel) -> IndustryModel:
    """
    Model an industry change caused by stronger automation and easier
    integration standards.

    Scenario analysis changes the underlying force pressures rather than
    pretending the original scores are permanent.
    """
    original = model.assessments

    updated: Dict[Force, ForceAssessment] = {}

    updated[Force.RIVALRY] = build_force(
        Force.RIVALRY,
        weighted_force_score(
            original[Force.RIVALRY].score,
            [(1.0, 0.8), (0.5, 0.4)],
        ),
        "Automation lowers differentiation from basic features while increasing competition around workflow quality.",
        original[Force.RIVALRY].evidence,
    )

    updated[Force.SUPPLIERS] = build_force(
        Force.SUPPLIERS,
        weighted_force_score(
            original[Force.SUPPLIERS].score,
            [(-0.8, 0.8)],
        ),
        "More standardized integrations reduce dependence on individual infrastructure and service providers.",
        original[Force.SUPPLIERS].evidence,
    )

    updated[Force.BUYERS] = build_force(
        Force.BUYERS,
        weighted_force_score(
            original[Force.BUYERS].score,
            [(0.7, 0.9)],
        ),
        "Improved product comparison and easier migration can increase buyer leverage.",
        original[Force.BUYERS].evidence,
    )

    updated[Force.SUBSTITUTES] = build_force(
        Force.SUBSTITUTES,
        weighted_force_score(
            original[Force.SUBSTITUTES].score,
            [(0.9, 1.0)],
        ),
        "Automation makes alternative software and automated spreadsheet workflows more capable.",
        original[Force.SUBSTITUTES].evidence,
    )

    updated[Force.ENTRANTS] = build_force(
        Force.ENTRANTS,
        weighted_force_score(
            original[Force.ENTRANTS].score,
            [(0.8, 0.9), (-0.4, 0.7)],
        ),
        "Development becomes easier while trust, distribution, and domain-specific integration barriers remain.",
        original[Force.ENTRANTS].evidence,
    )

    return IndustryModel(
        industry=model.industry,
        market_definition=model.market_definition,
        geography=model.geography,
        time_horizon=model.time_horizon,
        assessments=updated,
    )


def sensitivity_analysis(
    model: IndustryModel,
    percentage_change: float = 0.10,
) -> Dict[Force, tuple[float, float]]:
    """
    Measure how much the average pressure changes when each force changes.

    This helps identify which assumptions materially influence the aggregate
    model. It does not establish causality or predict profitability.
    """
    if not 0 < percentage_change < 1:
        raise ValueError("Percentage change must be between 0 and 1.")

    results: Dict[Force, tuple[float, float]] = {}

    for force in FORCE_ORDER:
        baseline = model.average_pressure
        original_score = model.assessments[force].score

        upward = min(10.0, original_score * (1 + percentage_change))
        downward = max(0.0, original_score * (1 - percentage_change))

        delta_up = (upward - original_score) / len(FORCE_ORDER)
        delta_down = (downward - original_score) / len(FORCE_ORDER)

        results[force] = (baseline + delta_down, baseline + delta_up)

    return results


def serialize_model(model: IndustryModel) -> str:
    """Serialize the model to JSON without losing force names."""
    payload = {
        "industry": model.industry,
        "market_definition": model.market_definition,
        "geography": model.geography,
        "time_horizon": model.time_horizon,
        "assessments": {
            force.value: {
                "score": assessment.score,
                "rationale": assessment.rationale,
                "evidence": [asdict(item) for item in assessment.evidence],
            }
            for force, assessment in model.assessments.items()
        },
    }
    return json.dumps(payload, indent=2)


def save_model(model: IndustryModel, path: Path) -> None:
    """Persist a model safely as UTF-8 JSON."""
    path.write_text(serialize_model(model), encoding="utf-8")


def load_model(path: Path) -> IndustryModel:
    """Load a previously saved model and validate its structure."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    assessments: Dict[Force, ForceAssessment] = {}

    for force in FORCE_ORDER:
        payload = raw["assessments"][force.value]
        evidence = [
            Evidence(
                statement=item["statement"],
                source=item["source"],
                direction=item["direction"],
                strength=item["strength"],
            )
            for item in payload["evidence"]
        ]
        assessments[force] = ForceAssessment(
            force=force,
            score=float(payload["score"]),
            rationale=payload["rationale"],
            evidence=evidence,
        )

    return IndustryModel(
        industry=raw["industry"],
        market_definition=raw["market_definition"],
        geography=raw["geography"],
        time_horizon=raw["time_horizon"],
        assessments=assessments,
    )


def compare_industries(models: List[IndustryModel]) -> None:
    """
    Compare industries without treating the framework as a universal
    profitability score.
    """
    if not models:
        raise ValueError("At least one industry model is required.")

    print("\n" + "=" * 78)
    print("INDUSTRY STRUCTURE COMPARISON")
    print("=" * 78)

    header = f"{'Industry':45} " + " ".join(
        f"{force.name[:6]:>9}" for force in FORCE_ORDER
    )
    print(header)
    print("-" * len(header))

    for model in models:
        values = " ".join(
            f"{model.assessments[force].score:>9.1f}" for force in FORCE_ORDER
        )
        print(f"{model.industry[:45]:45} {values}")


def demonstrate_force_distinction() -> None:
    """
    Show why similar observations can belong to different forces.

    A low switching cost can affect buyers and substitutes, but it represents
    different mechanisms:
    - buyers gain leverage when switching makes it easier to demand concessions;
    - substitutes become stronger when customers can move to a different
      solution rather than another supplier in the same industry.
    """
    print("\n" + "=" * 78)
    print("WHY THE FIVE FORCES MUST REMAIN DISTINCT")
    print("=" * 78)

    examples = {
        Force.RIVALRY: "Two existing accounting vendors repeatedly cut subscription prices.",
        Force.SUPPLIERS: "A specialized banking API provider raises integration fees.",
        Force.BUYERS: "Large accounting firms negotiate lower prices because they buy many licenses.",
        Force.SUBSTITUTES: "A business replaces accounting software with outsourced bookkeeping.",
        Force.ENTRANTS: "A new cloud accounting company enters after obtaining distribution partnerships.",
    }

    for force in FORCE_ORDER:
        print(f"{force.value}: {examples[force]}")


def main() -> None:
    print("Porter's Five Forces analytical model")
    print("------------------------------------")

    drivers = force_driver_matrix()
    print("\nForce-specific drivers")
    for force in FORCE_ORDER:
        print(f"\n{force.value}")
        for driver in drivers[force]:
            print(f"  - {driver}")

    baseline = demonstrate_beginner_model()
    print_model(baseline)

    print("\n" + "=" * 78)
    print("SCENARIO ANALYSIS")
    print("=" * 78)
    scenario = demonstrate_scenario_analysis(baseline)
    print_model(scenario)

    print("\n" + "=" * 78)
    print("SENSITIVITY ANALYSIS")
    print("=" * 78)

    sensitivity = sensitivity_analysis(baseline)

    for force, (lower, upper) in sensitivity.items():
        print(
            f"{force.value}: "
            f"average pressure could move from {lower:.2f} "
            f"to {upper:.2f} when this force changes by ±10%."
        )

    print("\n" + "=" * 78)
    print("PERSISTENCE TEST")
    print("=" * 78)

    output_path = Path("five_forces_model.json")
    save_model(baseline, output_path)
    restored = load_model(output_path)

    print(f"Saved model to: {output_path.resolve()}")
    print(
        f"Restored model average pressure: "
        f"{restored.average_pressure:.2f}/10"
    )

    # Clean up the demonstration artifact so normal execution does not leave
    # an unexpected file in the working directory.
    output_path.unlink(missing_ok=True)

    second_model = IndustryModel(
        industry="Enterprise Data Storage Services",
        market_definition=(
            "Managed cloud and enterprise storage services sold to medium "
            "and large organizations"
        ),
        geography="Global",
        time_horizon="2026-2030",
        assessments={
            Force.RIVALRY: build_force(
                Force.RIVALRY,
                6.9,
                "Large providers compete through price, reliability, performance, and integrated services.",
                [],
            ),
            Force.SUPPLIERS: build_force(
                Force.SUPPLIERS,
                5.8,
                "Hardware, networking, energy, and specialized technology suppliers influence service economics.",
                [],
            ),
            Force.BUYERS: build_force(
                Force.BUYERS,
                6.4,
                "Large enterprise customers can negotiate contracts and compare providers.",
                [],
            ),
            Force.SUBSTITUTES: build_force(
                Force.SUBSTITUTES,
                4.8,
                "On-premises infrastructure and alternative architectures can replace parts of managed storage demand.",
                [],
            ),
            Force.ENTRANTS: build_force(
                Force.ENTRANTS,
                4.1,
                "Capital requirements, infrastructure scale, reliability expectations, and enterprise trust create substantial entry barriers.",
                [],
            ),
        },
    )

    compare_industries([baseline, second_model])
    demonstrate_force_distinction()

    print("\nCompleted without external dependencies.")


if __name__ == "__main__":
    main()
