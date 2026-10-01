"""
PESTLE Analysis Engine
======================

A self-contained implementation for analyzing Political, Economic, Social,
Technological, Legal, and Environmental factors.

The program demonstrates:
- Structured PESTLE factor modeling
- Factor validation and normalization
- Positive/negative impact assessment
- Likelihood and impact scoring
- Weighted risk/opportunity scoring
- Category-level aggregation
- Scenario analysis
- Time-horizon comparison
- Trend tracking
- SWOT-style interpretation derived from PESTLE evidence
- JSON persistence using only the Python standard library
- CSV reporting
- Policy threshold evaluation
- A practical business expansion case study

The implementation intentionally keeps PESTLE categories distinct. Political
factors describe government and geopolitical conditions; economic factors
describe economic conditions; social factors describe demographic and cultural
conditions; technological factors describe technology capabilities and change;
legal factors describe laws and regulatory obligations; environmental factors
describe ecological and climate conditions.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


CATEGORIES = (
    "Political",
    "Economic",
    "Social",
    "Technological",
    "Legal",
    "Environmental",
)

DIRECTIONS = ("opportunity", "threat")
TIME_HORIZONS = ("short", "medium", "long")


@dataclass
class PESTLEFactor:
    """Represents one external factor and its assessed business effect."""

    factor_id: str
    category: str
    title: str
    description: str
    direction: str
    likelihood: int
    impact: int
    time_horizon: str
    evidence: str
    affected_areas: List[str] = field(default_factory=list)
    confidence: int = 3
    trend: str = "stable"

    def __post_init__(self) -> None:
        self.category = self.category.title()
        self.direction = self.direction.lower()
        self.time_horizon = self.time_horizon.lower()
        self.trend = self.trend.lower()

        if self.category not in CATEGORIES:
            raise ValueError(
                f"Invalid PESTLE category: {self.category}. "
                f"Expected one of {CATEGORIES}."
            )

        if self.direction not in DIRECTIONS:
            raise ValueError(
                f"Invalid direction: {self.direction}. "
                f"Expected 'opportunity' or 'threat'."
            )

        if self.time_horizon not in TIME_HORIZONS:
            raise ValueError(
                f"Invalid time horizon: {self.time_horizon}."
            )

        for name, value in (
            ("likelihood", self.likelihood),
            ("impact", self.impact),
            ("confidence", self.confidence),
        ):
            if not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"{name} must be an integer from 1 to 5.")

        if not self.title.strip():
            raise ValueError("Factor title cannot be empty.")

        if not self.description.strip():
            raise ValueError("Factor description cannot be empty.")

        if not self.evidence.strip():
            raise ValueError("Evidence must explain the basis of the assessment.")

    @property
    def raw_score(self) -> int:
        """Combines likelihood and impact on a 1-25 scale."""
        return self.likelihood * self.impact

    @property
    def signed_score(self) -> int:
        """Makes opportunities positive and threats negative."""
        return self.raw_score if self.direction == "opportunity" else -self.raw_score

    @property
    def confidence_adjusted_score(self) -> float:
        """
        Reduces the influence of uncertain assessments.

        Confidence is mapped from 1..5 to 0.2..1.0 instead of allowing a
        poorly evidenced factor to carry the same weight as a well-supported
        factor.
        """
        confidence_multiplier = self.confidence / 5
        return self.signed_score * confidence_multiplier


class PESTLEAnalysis:
    """Stores, validates, analyzes, and reports a PESTLE assessment."""

    def __init__(self, organization: str, analysis_date: Optional[str] = None):
        self.organization = organization.strip()
        if not self.organization:
            raise ValueError("Organization name cannot be empty.")

        self.analysis_date = analysis_date or date.today().isoformat()
        self.factors: Dict[str, PESTLEFactor] = {}

    def add_factor(self, factor: PESTLEFactor) -> None:
        """Add or replace a factor by its stable identifier."""
        if factor.factor_id in self.factors:
            raise ValueError(
                f"Factor ID '{factor.factor_id}' already exists."
            )
        self.factors[factor.factor_id] = factor

    def remove_factor(self, factor_id: str) -> None:
        """Remove a factor while reporting a useful error for unknown IDs."""
        if factor_id not in self.factors:
            raise KeyError(f"No factor exists with ID '{factor_id}'.")
        del self.factors[factor_id]

    def get_category(self, category: str) -> List[PESTLEFactor]:
        """Return factors belonging only to the requested PESTLE category."""
        normalized = category.title()
        if normalized not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        return [
            factor
            for factor in self.factors.values()
            if factor.category == normalized
        ]

    def score(self) -> float:
        """Return the net confidence-adjusted external pressure/opportunity."""
        return sum(
            factor.confidence_adjusted_score
            for factor in self.factors.values()
        )

    def category_score(self, category: str) -> float:
        """Aggregate only one PESTLE dimension."""
        return sum(
            factor.confidence_adjusted_score
            for factor in self.get_category(category)
        )

    def category_statistics(self, category: str) -> Dict[str, float]:
        """Calculate descriptive statistics for one PESTLE dimension."""
        factors = self.get_category(category)

        if not factors:
            return {
                "factor_count": 0,
                "opportunities": 0,
                "threats": 0,
                "average_likelihood": 0.0,
                "average_impact": 0.0,
                "net_score": 0.0,
            }

        opportunities = sum(
            factor.direction == "opportunity" for factor in factors
        )
        threats = len(factors) - opportunities

        return {
            "factor_count": len(factors),
            "opportunities": opportunities,
            "threats": threats,
            "average_likelihood": statistics.mean(
                factor.likelihood for factor in factors
            ),
            "average_impact": statistics.mean(
                factor.impact for factor in factors
            ),
            "net_score": self.category_score(category),
        }

    def rank_factors(
        self,
        category: Optional[str] = None,
        descending: bool = True,
    ) -> List[PESTLEFactor]:
        """Rank factors by absolute confidence-adjusted significance."""
        factors = (
            self.get_category(category)
            if category
            else list(self.factors.values())
        )

        return sorted(
            factors,
            key=lambda factor: abs(factor.confidence_adjusted_score),
            reverse=descending,
        )

    def filter_by_horizon(self, horizon: str) -> List[PESTLEFactor]:
        """Select factors relevant to a specific planning horizon."""
        horizon = horizon.lower()
        if horizon not in TIME_HORIZONS:
            raise ValueError(f"Unknown horizon: {horizon}")

        return [
            factor
            for factor in self.factors.values()
            if factor.time_horizon == horizon
        ]

    def category_balance(self) -> Dict[str, Dict[str, float]]:
        """Return a separate opportunity/threat balance for every category."""
        result: Dict[str, Dict[str, float]] = {}

        for category in CATEGORIES:
            factors = self.get_category(category)
            opportunity_score = sum(
                factor.confidence_adjusted_score
                for factor in factors
                if factor.direction == "opportunity"
            )
            threat_score = sum(
                abs(factor.confidence_adjusted_score)
                for factor in factors
                if factor.direction == "threat"
            )

            result[category] = {
                "opportunity_score": opportunity_score,
                "threat_score": threat_score,
                "net_score": opportunity_score - threat_score,
            }

        return result

    def high_priority_factors(
        self,
        minimum_raw_score: int = 16,
    ) -> List[PESTLEFactor]:
        """
        Identify factors with substantial likelihood-impact exposure.

        A raw score of 16 means combinations such as 4x4, 4x5, or 5x4.
        """
        if not 1 <= minimum_raw_score <= 25:
            raise ValueError("minimum_raw_score must be between 1 and 25.")

        return [
            factor
            for factor in self.factors.values()
            if factor.raw_score >= minimum_raw_score
        ]

    def scenario_score(
        self,
        likelihood_multiplier: float = 1.0,
        impact_multiplier: float = 1.0,
    ) -> float:
        """
        Recalculate the portfolio under a scenario.

        Multipliers simulate changed external conditions without modifying the
        underlying evidence record.
        """
        if likelihood_multiplier < 0 or impact_multiplier < 0:
            raise ValueError("Scenario multipliers cannot be negative.")

        total = 0.0

        for factor in self.factors.values():
            scenario_likelihood = min(
                5.0, factor.likelihood * likelihood_multiplier
            )
            scenario_impact = min(
                5.0, factor.impact * impact_multiplier
            )

            scenario_score = scenario_likelihood * scenario_impact
            if factor.direction == "threat":
                scenario_score *= -1

            total += scenario_score * (factor.confidence / 5)

        return total

    def export_json(self, path: Path) -> None:
        """Persist the analysis in a portable JSON representation."""
        payload = {
            "organization": self.organization,
            "analysis_date": self.analysis_date,
            "factors": [asdict(factor) for factor in self.factors.values()],
        }

        path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def export_csv(self, path: Path) -> None:
        """Export factor-level records for spreadsheet or BI processing."""
        fields = [
            "factor_id",
            "category",
            "title",
            "description",
            "direction",
            "likelihood",
            "impact",
            "raw_score",
            "confidence",
            "confidence_adjusted_score",
            "time_horizon",
            "trend",
            "evidence",
            "affected_areas",
        ]

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            for factor in self.factors.values():
                writer.writerow(
                    {
                        "factor_id": factor.factor_id,
                        "category": factor.category,
                        "title": factor.title,
                        "description": factor.description,
                        "direction": factor.direction,
                        "likelihood": factor.likelihood,
                        "impact": factor.impact,
                        "raw_score": factor.raw_score,
                        "confidence": factor.confidence,
                        "confidence_adjusted_score":
                            round(factor.confidence_adjusted_score, 2),
                        "time_horizon": factor.time_horizon,
                        "trend": factor.trend,
                        "evidence": factor.evidence,
                        "affected_areas": "; ".join(factor.affected_areas),
                    }
                )

    def text_report(self) -> str:
        """Produce a concise executive report from the underlying records."""
        lines = [
            f"PESTLE ANALYSIS: {self.organization}",
            f"Analysis date: {self.analysis_date}",
            f"Factors assessed: {len(self.factors)}",
            f"Net confidence-adjusted score: {self.score():.2f}",
            "",
            "CATEGORY PROFILE",
        ]

        for category in CATEGORIES:
            stats = self.category_statistics(category)
            lines.append(
                f"{category:15} "
                f"factors={stats['factor_count']:2.0f} "
                f"opportunities={stats['opportunities']:2.0f} "
                f"threats={stats['threats']:2.0f} "
                f"avg-impact={stats['average_impact']:.2f} "
                f"net={stats['net_score']:.2f}"
            )

        lines.extend(["", "HIGH-PRIORITY FACTORS"])

        for factor in self.high_priority_factors():
            lines.append(
                f"[{factor.category}] {factor.title}: "
                f"{factor.direction}, raw={factor.raw_score}, "
                f"confidence-adjusted={factor.confidence_adjusted_score:.2f}"
            )

        return "\n".join(lines)


def build_case_study() -> PESTLEAnalysis:
    """
    Build a realistic PESTLE assessment for an Indian technology company
    evaluating expansion of an enterprise analytics platform.
    """
    analysis = PESTLEAnalysis(
        organization="Northstar Analytics",
        analysis_date="2026-10-01",
    )

    # Political factors concern government decisions, geopolitical conditions,
    # public policy, and government-market relationships.
    analysis.add_factor(
        PESTLEFactor(
            factor_id="P001",
            category="Political",
            title="Government digital-infrastructure spending",
            description=(
                "Public investment in digital infrastructure can increase "
                "enterprise demand for analytics, cloud, and data services."
            ),
            direction="opportunity",
            likelihood=4,
            impact=4,
            time_horizon="medium",
            confidence=4,
            trend="rising",
            evidence=(
                "Planning assumption based on the company's target market "
                "exposure to public-sector and infrastructure customers."
            ),
            affected_areas=["public-sector sales", "enterprise analytics"],
        )
    )

    analysis.add_factor(
        PESTLEFactor(
            factor_id="P002",
            category="Political",
            title="Cross-border geopolitical uncertainty",
            description=(
                "Changes in international relations can affect procurement "
                "decisions, market access, and technology partnerships."
            ),
            direction="threat",
            likelihood=3,
            impact=4,
            time_horizon="medium",
            confidence=3,
            trend="volatile",
            evidence=(
                "Risk register identifies international procurement and "
                "partnership exposure in prospective markets."
            ),
            affected_areas=["international sales", "partnerships"],
        )
    )

    # Economic factors concern purchasing power, inflation, rates, currency,
    # employment, investment, and broader economic conditions.
    analysis.add_factor(
        PESTLEFactor(
            factor_id="E001",
            category="Economic",
            title="Enterprise technology budget growth",
            description=(
                "Higher technology investment can increase demand for "
                "analytics subscriptions and implementation services."
            ),
            direction="opportunity",
            likelihood=4,
            impact=5,
            time_horizon="medium",
            confidence=4,
            trend="rising",
            evidence=(
                "Sales planning assumes increasing enterprise allocation "
                "toward data modernization."
            ),
            affected_areas=["subscription revenue", "consulting"],
        )
    )

    analysis.add_factor(
        PESTLEFactor(
            factor_id="E002",
            category="Economic",
            title="Currency volatility",
            description=(
                "Exchange-rate movement can affect imported infrastructure "
                "costs and international revenue when contracts are priced "
                "in different currencies."
            ),
            direction="threat",
            likelihood=4,
            impact=3,
            time_horizon="short",
            confidence=4,
            trend="volatile",
            evidence=(
                "The operating model contains both domestic expenses and "
                "foreign-currency customer contracts."
            ),
            affected_areas=["gross margin", "pricing", "cash flow"],
        )
    )

    # Social factors concern population structure, behavior, culture,
    # workforce expectations, trust, and changing customer behavior.
    analysis.add_factor(
        PESTLEFactor(
            factor_id="S001",
            category="Social",
            title="Growing data-literacy expectations",
            description=(
                "Customers increasingly expect business teams to make "
                "decisions using dashboards and measurable evidence."
            ),
            direction="opportunity",
            likelihood=5,
            impact=4,
            time_horizon="medium",
            confidence=4,
            trend="rising",
            evidence=(
                "Customer discovery indicates increased demand for "
                "self-service analytics among non-technical teams."
            ),
            affected_areas=["product adoption", "training", "UX"],
        )
    )

    analysis.add_factor(
        PESTLEFactor(
            factor_id="S002",
            category="Social",
            title="Employee resistance to analytics-driven workflows",
            description=(
                "Changes to established decision processes can create "
                "adoption barriers when employees perceive analytics as "
                "monitoring or replacement rather than decision support."
            ),
            direction="threat",
            likelihood=3,
            impact=3,
            time_horizon="short",
            confidence=3,
            trend="stable",
            evidence=(
                "Implementation teams have identified change-management "
                "risk during enterprise deployments."
            ),
            affected_areas=["implementation", "customer success"],
        )
    )

    # Technological factors concern technology capability, infrastructure,
    # innovation cycles, interoperability, automation, and obsolescence.
    analysis.add_factor(
        PESTLEFactor(
            factor_id="T001",
            category="Technological",
            title="Real-time analytics infrastructure",
            description=(
                "Improved streaming and cloud data infrastructure enables "
                "near-real-time analytics products and faster decision cycles."
            ),
            direction="opportunity",
            likelihood=5,
            impact=5,
            time_horizon="medium",
            confidence=5,
            trend="rising",
            evidence=(
                "Product architecture already supports event-based ingestion "
                "and incremental analytical processing."
            ),
            affected_areas=["product capability", "customer value"],
        )
    )

    analysis.add_factor(
        PESTLEFactor(
            factor_id="T002",
            category="Technological",
            title="Rapid analytics-platform obsolescence",
            description=(
                "Fast changes in cloud, data, and analytics tooling can "
                "increase engineering costs and shorten product assumptions."
            ),
            direction="threat",
            likelihood=4,
            impact=4,
            time_horizon="long",
            confidence=4,
            trend="rising",
            evidence=(
                "The technical roadmap contains dependencies on rapidly "
                "changing data-processing infrastructure."
            ),
            affected_areas=["engineering cost", "architecture"],
        )
    )

    # Legal factors concern enforceable obligations such as privacy,
    # contracts, licensing, employment rules, and sector regulation.
    analysis.add_factor(
        PESTLEFactor(
            factor_id="L001",
            category="Legal",
            title="Data-protection compliance obligations",
            description=(
                "Personal-data processing creates obligations around lawful "
                "processing, security controls, retention, and data rights."
            ),
            direction="threat",
            likelihood=4,
            impact=5,
            time_horizon="short",
            confidence=5,
            trend="rising",
            evidence=(
                "The product processes customer datasets that may contain "
                "personal or identifiable information."
            ),
            affected_areas=["privacy", "security", "contracts"],
        )
    )

    analysis.add_factor(
        PESTLEFactor(
            factor_id="L002",
            category="Legal",
            title="Contractual standardization",
            description=(
                "Standardized enterprise contracts can reduce negotiation "
                "time when liability, service levels, data handling, and "
                "termination provisions are consistently defined."
            ),
            direction="opportunity",
            likelihood=4,
            impact=3,
            time_horizon="short",
            confidence=4,
            trend="rising",
            evidence=(
                "Commercial operations are moving toward repeatable "
                "enterprise contracting patterns."
            ),
            affected_areas=["sales cycle", "legal operations"],
        )
    )

    # Environmental factors concern ecological effects, climate exposure,
    # resource use, energy demand, waste, and environmental expectations.
    analysis.add_factor(
        PESTLEFactor(
            factor_id="EN001",
            category="Environmental",
            title="Data-center energy consumption",
            description=(
                "Growth in compute-intensive analytics can increase energy "
                "consumption and expose customers to sustainability concerns."
            ),
            direction="threat",
            likelihood=4,
            impact=4,
            time_horizon="medium",
            confidence=4,
            trend="rising",
            evidence=(
                "Forecast workloads include continuous analytics and "
                "increased compute-intensive processing."
            ),
            affected_areas=["operating cost", "sustainability reporting"],
        )
    )

    analysis.add_factor(
        PESTLEFactor(
            factor_id="EN002",
            category="Environmental",
            title="Demand for measurable sustainability reporting",
            description=(
                "Organizations seeking environmental transparency can need "
                "analytics systems that consolidate energy, emissions, and "
                "resource data."
            ),
            direction="opportunity",
            likelihood=4,
            impact=4,
            time_horizon="medium",
            confidence=3,
            trend="rising",
            evidence=(
                "Target customers increasingly request environmental metrics "
                "as part of operational reporting."
            ),
            affected_areas=["product modules", "enterprise sales"],
        )
    )

    return analysis


def demonstrate_factor_matrix(analysis: PESTLEAnalysis) -> None:
    """Show how likelihood and impact create the PESTLE priority matrix."""
    print("\nLIKELIHOOD-IMPACT MATRIX")

    matrix: Dict[int, List[str]] = {score: [] for score in range(1, 26)}

    for factor in analysis.factors.values():
        matrix[factor.raw_score].append(
            f"{factor.category}: {factor.title}"
        )

    for score in range(25, 0, -1):
        if matrix[score]:
            print(f"Score {score:2}:")
            for title in matrix[score]:
                print(f"  {title}")


def demonstrate_horizons(analysis: PESTLEAnalysis) -> None:
    """Compare short-, medium-, and long-horizon external pressures."""
    print("\nTIME-HORIZON EXPOSURE")

    for horizon in TIME_HORIZONS:
        factors = analysis.filter_by_horizon(horizon)
        score = sum(
            factor.confidence_adjusted_score for factor in factors
        )

        print(
            f"{horizon.title():8} "
            f"factors={len(factors):2} "
            f"net-score={score:7.2f}"
        )


def demonstrate_scenarios(analysis: PESTLEAnalysis) -> None:
    """
    Evaluate alternative external conditions without changing the baseline.

    This is useful because a PESTLE assessment is not a forecast. Scenario
    multipliers let decision makers examine sensitivity to changed assumptions.
    """
    scenarios = {
        "Baseline": (1.0, 1.0),
        "Higher external pressure": (1.2, 1.2),
        "Lower external pressure": (0.8, 0.9),
        "High-impact disruption": (1.1, 1.4),
    }

    print("\nSCENARIO ANALYSIS")

    for name, (likelihood_multiplier, impact_multiplier) in scenarios.items():
        score = analysis.scenario_score(
            likelihood_multiplier,
            impact_multiplier,
        )
        print(f"{name:28} {score:8.2f}")


def demonstrate_control_mapping(analysis: PESTLEAnalysis) -> None:
    """
    Map external observations to response types.

    The response is deliberately not called a mitigation plan for every
    factor: opportunities require capability investment, while threats may
    require controls, contingency planning, or monitoring.
    """
    print("\nRESPONSE MAPPING")

    for factor in analysis.high_priority_factors():
        if factor.direction == "threat":
            response = "control / contingency / monitoring"
        else:
            response = "capability investment / market action"

        print(
            f"{factor.category:15} | "
            f"{factor.title:45} | "
            f"{response}"
        )


def demonstrate_validation() -> None:
    """Exercise validation failures so incorrect assessments fail early."""
    print("\nVALIDATION EXAMPLES")

    invalid_cases = [
        {
            "factor_id": "BAD-1",
            "category": "Financial",
            "title": "Invalid category",
            "description": "This should fail validation.",
            "direction": "threat",
            "likelihood": 3,
            "impact": 3,
            "time_horizon": "short",
            "evidence": "Validation test.",
        },
        {
            "factor_id": "BAD-2",
            "category": "Political",
            "title": "Invalid likelihood",
            "description": "This should fail validation.",
            "direction": "threat",
            "likelihood": 8,
            "impact": 3,
            "time_horizon": "short",
            "evidence": "Validation test.",
        },
        {
            "factor_id": "BAD-3",
            "category": "Legal",
            "title": "Missing evidence",
            "description": "This should fail validation.",
            "direction": "threat",
            "likelihood": 3,
            "impact": 3,
            "time_horizon": "short",
            "evidence": "",
        },
    ]

    for values in invalid_cases:
        try:
            PESTLEFactor(**values)
        except ValueError as exc:
            print(f"Rejected invalid factor: {exc}")


def demonstrate_json_round_trip(analysis: PESTLEAnalysis) -> None:
    """
    Persist the analysis and read it back.

    The round trip validates that the model is suitable for simple reporting
    pipelines and that JSON contains structured factor-level information.
    """
    output_directory = Path("pestle_output")
    output_directory.mkdir(exist_ok=True)

    json_path = output_directory / "pestle_analysis.json"
    csv_path = output_directory / "pestle_analysis.csv"

    analysis.export_json(json_path)
    analysis.export_csv(csv_path)

    loaded = json.loads(json_path.read_text(encoding="utf-8"))

    print("\nPERSISTENCE")
    print(f"JSON written: {json_path}")
    print(f"CSV written:  {csv_path}")
    print(f"Loaded organization: {loaded['organization']}")
    print(f"Loaded factors: {len(loaded['factors'])}")


def print_top_factors(analysis: PESTLEAnalysis) -> None:
    """Display the highest-significance external factors."""
    print("\nMOST SIGNIFICANT FACTORS")

    for factor in analysis.rank_factors()[:6]:
        print(
            f"{factor.category:15} "
            f"{factor.direction:11} "
            f"{factor.raw_score:2} "
            f"{factor.title}"
        )


def main() -> None:
    analysis = build_case_study()

    print(analysis.text_report())

    print_top_factors(analysis)
    demonstrate_factor_matrix(analysis)
    demonstrate_horizons(analysis)
    demonstrate_scenarios(analysis)
    demonstrate_control_mapping(analysis)
    demonstrate_validation()
    demonstrate_json_round_trip(analysis)

    print("\nCATEGORY BALANCE")

    for category, balance in analysis.category_balance().items():
        print(
            f"{category:15} "
            f"opportunity={balance['opportunity_score']:7.2f} "
            f"threat={balance['threat_score']:7.2f} "
            f"net={balance['net_score']:7.2f}"
        )

    print("\nPROGRAMMATIC ACCESS EXAMPLE")

    legal_factors = analysis.get_category("Legal")
    for factor in legal_factors:
        print(
            f"Legal factor: {factor.title}; "
            f"impact={factor.impact}; "
            f"confidence={factor.confidence}"
        )

    print("\nPESTLE analysis completed successfully.")


if __name__ == "__main__":
    main()
