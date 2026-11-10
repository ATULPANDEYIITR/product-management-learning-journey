#!/usr/bin/env python3
"""
RICE Framework: Product Prioritization and Decision Engine

Implements:
- Reach, Impact, Confidence, Effort
- RICE scoring and ranking
- Confidence-adjusted prioritization
- Data validation and uncertainty handling
- Scenario analysis and sensitivity testing
- Portfolio constraints and effort budgets
- CSV/JSON reporting
- Automated tests and edge-case handling

RICE Score = (Reach * Impact * Confidence) / Effort

Reach: Number of users or events affected during a defined period.
Impact: Relative effect on each affected user.
Confidence: Evidence-based confidence percentage.
Effort: Total person-months required.
"""

from __future__ import annotations

import csv
import json
import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("rice")


class ImpactLevel(Enum):
    MINIMAL = 0.25
    LOW = 0.5
    MEDIUM = 1.0
    HIGH = 2.0
    MASSIVE = 3.0


class Priority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Decision(Enum):
    ACCEPT = "Accept"
    REVIEW = "Review"
    DEFER = "Defer"


@dataclass(frozen=True)
class RICEItem:
    item_id: str
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float
    period: str = "monthly"
    category: str = "Product"
    strategic_value: float = 0.0
    evidence: str = ""
    dependencies: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.item_id.strip():
            raise ValueError("Item ID cannot be empty.")

        if not self.name.strip():
            raise ValueError("Item name cannot be empty.")

        values = {
            "reach": self.reach,
            "impact": self.impact,
            "confidence": self.confidence,
            "effort": self.effort,
            "strategic_value": self.strategic_value,
        }

        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite.")

        if self.reach < 0:
            raise ValueError("Reach cannot be negative.")

        if self.impact <= 0:
            raise ValueError("Impact must be greater than zero.")

        if not 0 <= self.confidence <= 100:
            raise ValueError("Confidence must be between 0 and 100.")

        if self.effort <= 0:
            raise ValueError("Effort must be greater than zero.")

        if self.strategic_value < 0:
            raise ValueError("Strategic value cannot be negative.")

        if not self.period.strip():
            raise ValueError("Measurement period cannot be empty.")

        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("Duplicate dependencies are not allowed.")

        if self.item_id in self.dependencies:
            raise ValueError("An item cannot depend on itself.")

    @property
    def confidence_fraction(self) -> float:
        return self.confidence / 100.0


@dataclass
class RICEResult:
    item: RICEItem
    score: float
    priority: Priority
    decision: Decision
    effort_efficiency: float
    adjusted_score: float
    rank: int = 0
    limitations: list[str] = field(default_factory=list)


class RICEEngine:
    """Calculates and evaluates RICE prioritization scores."""

    def __init__(
        self,
        high_threshold: float = 100,
        medium_threshold: float = 30,
        minimum_confidence: float = 40,
    ):
        if high_threshold <= medium_threshold:
            raise ValueError("High threshold must exceed medium threshold.")

        if medium_threshold < 0:
            raise ValueError("Thresholds cannot be negative.")

        if not 0 <= minimum_confidence <= 100:
            raise ValueError("Invalid minimum confidence.")

        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self.minimum_confidence = minimum_confidence

    @staticmethod
    def calculate_score(item: RICEItem) -> float:
        return (
            item.reach
            * item.impact
            * item.confidence_fraction
            / item.effort
        )

    @staticmethod
    def classify(score: float) -> Priority:
        if score >= 100:
            return Priority.HIGH
        if score >= 30:
            return Priority.MEDIUM
        return Priority.LOW

    def evaluate(self, item: RICEItem) -> RICEResult:
        score = self.calculate_score(item)

        limitations = []

        if item.confidence < self.minimum_confidence:
            limitations.append("Evidence confidence is below policy threshold.")

        if item.reach == 0:
            limitations.append("No measurable reach.")

        if not item.evidence.strip():
            limitations.append("Supporting evidence is not documented.")

        if item.strategic_value > 0:
            limitations.append(
                "Strategic value is reported separately from the RICE score."
            )

        if item.dependencies:
            limitations.append("Dependencies require separate scheduling validation.")

        if item.confidence < self.minimum_confidence:
            decision = Decision.REVIEW
        elif score >= self.high_threshold:
            decision = Decision.ACCEPT
        elif score >= self.medium_threshold:
            decision = Decision.REVIEW
        else:
            decision = Decision.DEFER

        return RICEResult(
            item=item,
            score=score,
            priority=self.classify(score),
            decision=decision,
            effort_efficiency=score / item.effort,
            adjusted_score=score,
            limitations=limitations,
        )

    def rank(
        self,
        items: Iterable[RICEItem]
    ) -> list[RICEResult]:

        items = list(items)
        identifiers = [item.item_id for item in items]

        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Item IDs must be unique.")

        results = [self.evaluate(item) for item in items]

        results.sort(
            key=lambda result: (
                -result.score,
                -result.item.strategic_value,
                result.item.item_id,
            )
        )

        for rank, result in enumerate(results, start=1):
            result.rank = rank

        return results


class PortfolioPlanner:
    """Selects a portfolio under a total effort budget."""

    @staticmethod
    def select(
        results: list[RICEResult],
        effort_budget: float,
    ) -> list[RICEResult]:

        if not math.isfinite(effort_budget) or effort_budget < 0:
            raise ValueError("Effort budget must be finite and non-negative.")

        # Exact 0/1 knapsack dynamic programming with discretized effort.
        # This planner uses one effort unit per month at 0.1-month resolution.
        scale = 10
        capacity = int(round(effort_budget * scale))

        if capacity > 100000:
            raise ValueError("Budget is too large for the configured DP planner.")

        eligible = [
            result for result in results
            if result.decision != Decision.REVIEW
            and result.item.confidence > 0
        ]

        # dp[c] stores the maximum total RICE score for capacity c.
        dp = [0.0] * (capacity + 1)
        choices: list[list[int]] = [[] for _ in range(capacity + 1)]

        for index, result in enumerate(eligible):
            weight = math.ceil(result.item.effort * scale - 1e-12)

            if weight > capacity:
                continue

            for current in range(capacity, weight - 1, -1):
                candidate = dp[current - weight] + result.score

                if candidate > dp[current]:
                    dp[current] = candidate
                    choices[current] = choices[current - weight] + [index]

        selected_indices = set(choices[capacity])

        return [
            result for index, result in enumerate(eligible)
            if index in selected_indices
        ]


class SensitivityAnalyzer:
    """Tests how uncertain assumptions influence prioritization."""

    @staticmethod
    def vary(
        item: RICEItem,
        reach_factor: float = 1.0,
        impact_factor: float = 1.0,
        confidence_factor: float = 1.0,
        effort_factor: float = 1.0,
    ) -> float:

        factors = (
            reach_factor,
            impact_factor,
            confidence_factor,
            effort_factor,
        )

        if any(not math.isfinite(factor) or factor <= 0 for factor in factors):
            raise ValueError("Sensitivity factors must be positive and finite.")

        confidence = min(
            100.0,
            item.confidence * confidence_factor
        )

        scenario = RICEItem(
            item_id=item.item_id,
            name=item.name,
            reach=item.reach * reach_factor,
            impact=item.impact * impact_factor,
            confidence=confidence,
            effort=item.effort * effort_factor,
            period=item.period,
            category=item.category,
            strategic_value=item.strategic_value,
            evidence=item.evidence,
            dependencies=item.dependencies,
        )

        return RICEEngine.calculate_score(scenario)

    @staticmethod
    def range_analysis(item: RICEItem) -> dict:
        return {
            "optimistic": SensitivityAnalyzer.vary(
                item, 1.2, 1.2, 1.1, 0.9
            ),
            "baseline": RICEEngine.calculate_score(item),
            "pessimistic": SensitivityAnalyzer.vary(
                item, 0.8, 0.8, 0.8, 1.2
            ),
        }


class ReportManager:
    """Exports reproducible prioritization reports."""

    @staticmethod
    def export_json(
        results: list[RICEResult],
        destination: Path
    ) -> None:

        payload = []

        for result in results:
            payload.append({
                "rank": result.rank,
                "item": asdict(result.item),
                "score": round(result.score, 4),
                "priority": result.priority.value,
                "decision": result.decision.value,
                "effort_efficiency": round(result.effort_efficiency, 4),
                "limitations": result.limitations,
            })

        destination.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8"
        )

    @staticmethod
    def export_csv(
        results: list[RICEResult],
        destination: Path
    ) -> None:

        fields = [
            "rank", "item_id", "name", "reach", "impact",
            "confidence", "effort", "score", "priority",
            "decision", "category",
        ]

        with destination.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            for result in results:
                writer.writerow({
                    "rank": result.rank,
                    "item_id": result.item.item_id,
                    "name": result.item.name,
                    "reach": result.item.reach,
                    "impact": result.item.impact,
                    "confidence": result.item.confidence,
                    "effort": result.item.effort,
                    "score": round(result.score, 4),
                    "priority": result.priority.value,
                    "decision": result.decision.value,
                    "category": result.item.category,
                })


def build_portfolio() -> list[RICEItem]:
    return [
        RICEItem(
            "P001",
            "Self-service account recovery",
            12000, 2.0, 90, 3.0,
            category="Security",
            strategic_value=8,
            evidence="Support-ticket analysis and usability interviews",
        ),
        RICEItem(
            "P002",
            "Mobile dashboard redesign",
            8500, 1.0, 85, 4.0,
            evidence="Product analytics and customer survey",
        ),
        RICEItem(
            "P003",
            "Automated incident notifications",
            15000, 1.5, 95, 2.0,
            category="Reliability",
            strategic_value=9,
            evidence="Incident frequency and operational logs",
        ),
        RICEItem(
            "P004",
            "Advanced analytics export",
            3000, 2.0, 70, 5.0,
            evidence="Enterprise customer interviews",
        ),
        RICEItem(
            "P005",
            "Experimental recommendation engine",
            5000, 3.0, 35, 8.0,
            category="Experiment",
            evidence="Limited pilot observations",
        ),
        RICEItem(
            "P006",
            "Accessibility improvements",
            6000, 1.5, 95, 2.5,
            category="Accessibility",
            evidence="Accessibility audit",
        ),
        RICEItem(
            "P007",
            "Legacy reporting migration",
            0, 1.0, 80, 3.0,
            evidence="No current measurable user reach",
        ),
    ]


def run_tests() -> None:
    engine = RICEEngine()

    sample = RICEItem(
        "TEST01", "Test feature", 1000, 2, 80, 4,
        evidence="Verified evidence"
    )

    assert math.isclose(
        engine.calculate_score(sample),
        400.0
    )

    zero_reach = RICEItem(
        "TEST02", "Zero reach", 0, 1, 100, 2
    )

    assert engine.calculate_score(zero_reach) == 0

    assert SensitivityAnalyzer.vary(
        sample, 1.0, 1.0, 1.0, 2.0
    ) == 200.0

    results = engine.rank([sample, zero_reach])

    assert results[0].item.item_id == "TEST01"

    try:
        RICEItem("BAD", "Invalid", -1, 1, 80, 2)
        raise AssertionError("Negative reach should fail.")
    except ValueError:
        pass

    try:
        RICEItem("BAD2", "Invalid", 1, 1, 101, 2)
        raise AssertionError("Invalid confidence should fail.")
    except ValueError:
        pass

    try:
        RICEEngine(30, 100)
        raise AssertionError("Invalid thresholds should fail.")
    except ValueError:
        pass

    logger.info("All automated assertions passed.")


def main() -> None:
    run_tests()

    engine = RICEEngine(
        high_threshold=100,
        medium_threshold=30,
        minimum_confidence=40,
    )

    items = build_portfolio()
    results = engine.rank(items)

    print("\nRICE PRIORITIZATION REPORT")
    print("=" * 90)

    print(
        f"{'Rank':<6}{'ID':<9}{'Feature':<38}"
        f"{'Score':>10}{'Priority':>12}{'Decision':>12}"
    )

    for result in results:
        print(
            f"{result.rank:<6}"
            f"{result.item.item_id:<9}"
            f"{result.item.name:<38}"
            f"{result.score:>10.2f}"
            f"{result.priority.value:>12}"
            f"{result.decision.value:>12}"
        )

    print("\nUNCERTAINTY ANALYSIS")
    print("=" * 70)

    for item in items:
        scenarios = SensitivityAnalyzer.range_analysis(item)

        print(
            f"{item.name}: "
            f"Optimistic={scenarios['optimistic']:.2f}, "
            f"Baseline={scenarios['baseline']:.2f}, "
            f"Pessimistic={scenarios['pessimistic']:.2f}"
        )

    selected = PortfolioPlanner.select(
        results,
        effort_budget=12.0
    )

    print("\nPORTFOLIO UNDER 12 PERSON-MONTHS")
    print("=" * 70)

    for result in selected:
        print(
            f"{result.item.name}: "
            f"{result.item.effort:.1f} months, "
            f"score {result.score:.2f}"
        )

    print(
        "Selected effort:",
        sum(result.item.effort for result in selected)
    )

    ReportManager.export_json(
        results,
        Path("rice_report.json")
    )

    ReportManager.export_csv(
        results,
        Path("rice_report.csv")
    )

    print("\nReports written to rice_report.json and rice_report.csv")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        logger.error("Execution failed: %s", error)
        raise SystemExit(1)
