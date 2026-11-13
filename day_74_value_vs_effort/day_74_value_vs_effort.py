#!/usr/bin/env python3
"""
VALUE VS EFFORT: PRIORITIZATION AND OPPORTUNITY MATRIX

Models product and repository-development opportunities using:
- Value estimation
- Effort estimation
- Weighted scoring
- Value-versus-effort opportunity classification
- Confidence and risk adjustments
- Capacity-constrained prioritization
- Sensitivity analysis
- Scenario comparison
- CSV reporting and validation

Python 3.10+
Uses only the Python standard library.
"""

from __future__ import annotations

import csv
import json
import logging
import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("opportunity_matrix")


class Priority(Enum):
    QUICK_WIN = "Quick Win"
    STRATEGIC = "Strategic Investment"
    FILL_IN = "Fill-In"
    LOW_PRIORITY = "Low Priority"


class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass(frozen=True)
class Estimation:
    """Represents an estimate with explicit uncertainty."""

    low: float
    expected: float
    high: float

    def __post_init__(self):
        values = (self.low, self.expected, self.high)

        if any(not math.isfinite(value) for value in values):
            raise ValueError("Estimates must be finite.")

        if self.low < 0 or not self.low <= self.expected <= self.high:
            raise ValueError("Expected ordering: 0 <= low <= expected <= high.")

    @property
    def triangular_mean(self) -> float:
        return (self.low + self.expected + self.high) / 3

    @property
    def uncertainty(self) -> float:
        if self.expected == 0:
            return 0.0
        return (self.high - self.low) / self.expected


@dataclass
class Opportunity:
    opportunity_id: str
    name: str
    description: str
    customer_impact: float
    strategic_alignment: float
    revenue_impact: float
    urgency: float
    value_confidence: float
    effort: Estimation
    effort_confidence: float
    risk: RiskLevel = RiskLevel.MEDIUM
    dependencies: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.opportunity_id.strip() or not self.name.strip():
            raise ValueError("Opportunity ID and name are required.")

        scores = [
            self.customer_impact,
            self.strategic_alignment,
            self.revenue_impact,
            self.urgency,
            self.value_confidence,
            self.effort_confidence,
        ]

        if any(
            not math.isfinite(value) or not 1 <= value <= 5
            for value in scores
        ):
            raise ValueError("All rating and confidence scores must be 1-5.")

        if self.effort.expected <= 0:
            raise ValueError("Expected effort must be greater than zero.")

        if self.opportunity_id in self.dependencies:
            raise ValueError("An opportunity cannot depend on itself.")


@dataclass(frozen=True)
class Evaluation:
    opportunity_id: str
    name: str
    estimated_value: float
    adjusted_value: float
    estimated_effort: float
    value_effort_ratio: float
    confidence: float
    priority: Priority
    risk: RiskLevel


class PrioritizationEngine:
    """
    Uses weighted value scoring and effort normalization.

    Value is estimated on a 0-100 scale.
    Confidence and risk reduce the usable value.
    The ratio is adjusted value divided by estimated effort.
    """

    WEIGHTS = {
        "customer_impact": 0.35,
        "strategic_alignment": 0.30,
        "revenue_impact": 0.20,
        "urgency": 0.15,
    }

    RISK_FACTORS = {
        RiskLevel.LOW: 1.00,
        RiskLevel.MEDIUM: 0.85,
        RiskLevel.HIGH: 0.65,
    }

    def __init__(
        self,
        quick_win_threshold: float = 20.0,
        strategic_threshold: float = 8.0,
    ):
        if quick_win_threshold <= strategic_threshold:
            raise ValueError("Quick-win threshold must exceed strategic threshold.")

        self.quick_win_threshold = quick_win_threshold
        self.strategic_threshold = strategic_threshold

    def estimate_value(self, item: Opportunity) -> float:
        weighted_score = sum(
            getattr(item, dimension) * weight
            for dimension, weight in self.WEIGHTS.items()
        )

        return weighted_score / 5 * 100

    def evaluate(self, item: Opportunity) -> Evaluation:
        item.validate()

        value = self.estimate_value(item)
        confidence = min(
            item.value_confidence,
            item.effort_confidence
        ) / 5

        adjusted_value = (
            value
            * confidence
            * self.RISK_FACTORS[item.risk]
        )

        effort = item.effort.triangular_mean

        ratio = adjusted_value / effort

        if ratio >= self.quick_win_threshold:
            priority = Priority.QUICK_WIN
        elif ratio >= self.strategic_threshold:
            priority = Priority.STRATEGIC
        elif adjusted_value >= 25:
            priority = Priority.FILL_IN
        else:
            priority = Priority.LOW_PRIORITY

        return Evaluation(
            opportunity_id=item.opportunity_id,
            name=item.name,
            estimated_value=round(value, 2),
            adjusted_value=round(adjusted_value, 2),
            estimated_effort=round(effort, 2),
            value_effort_ratio=round(ratio, 2),
            confidence=round(confidence, 2),
            priority=priority,
            risk=item.risk,
        )

    def rank(
        self,
        opportunities: Iterable[Opportunity]
    ) -> list[Evaluation]:
        results = [self.evaluate(item) for item in opportunities]

        return sorted(
            results,
            key=lambda result: (
                result.value_effort_ratio,
                result.adjusted_value,
            ),
            reverse=True,
        )


class DependencyManager:
    """Validates dependency references and detects circular dependencies."""

    @staticmethod
    def validate(items: list[Opportunity]) -> None:
        lookup = {item.opportunity_id: item for item in items}

        if len(lookup) != len(items):
            raise ValueError("Duplicate opportunity IDs.")

        for item in items:
            item.validate()

            for dependency in item.dependencies:
                if dependency not in lookup:
                    raise ValueError(
                        f"Unknown dependency {dependency} for {item.name}"
                    )

        visited: set[str] = set()
        active: set[str] = set()

        def visit(identifier: str) -> None:
            if identifier in active:
                raise ValueError("Circular dependency detected.")

            if identifier in visited:
                return

            active.add(identifier)

            for dependency in lookup[identifier].dependencies:
                visit(dependency)

            active.remove(identifier)
            visited.add(identifier)

        for identifier in lookup:
            visit(identifier)


def capacity_plan(
    items: list[Opportunity],
    evaluations: list[Evaluation],
    capacity: float,
) -> list[Evaluation]:
    """
    Selects opportunities using a dependency-aware greedy strategy.

    This is a practical heuristic, not an exact knapsack optimizer.
    Every selected dependency must also be selected.
    """

    if not math.isfinite(capacity) or capacity < 0:
        raise ValueError("Capacity must be a finite non-negative number.")

    lookup = {item.opportunity_id: item for item in items}
    evaluated = {result.opportunity_id: result for result in evaluations}

    selected: set[str] = set()
    remaining = capacity

    def bundle(identifier: str) -> set[str]:
        result = {identifier}

        for dependency in lookup[identifier].dependencies:
            result |= bundle(dependency)

        return result

    ranked = sorted(
        evaluations,
        key=lambda result: result.value_effort_ratio,
        reverse=True,
    )

    for result in ranked:
        if result.opportunity_id in selected:
            continue

        required = bundle(result.opportunity_id)
        new_items = required - selected

        required_effort = sum(
            lookup[identifier].effort.triangular_mean
            for identifier in new_items
        )

        if required_effort <= remaining:
            selected.update(new_items)
            remaining -= required_effort

    return sorted(
        [evaluated[identifier] for identifier in selected],
        key=lambda result: result.value_effort_ratio,
        reverse=True,
    )


def sensitivity_analysis(
    item: Opportunity,
    engine: PrioritizationEngine
) -> dict:
    """Shows how value and effort uncertainty affect prioritization."""

    original_effort = item.effort

    scenarios = {
        "optimistic": (
            item.effort.low,
            5,
        ),
        "expected": (
            item.effort.expected,
            5,
        ),
        "pessimistic": (
            item.effort.high,
            5,
        ),
    }

    results = {}

    for scenario, (effort, _) in scenarios.items():
        adjusted = Opportunity(
            **{
                **asdict(item),
                "effort": Estimation(
                    effort,
                    effort,
                    effort,
                ),
            }
        )

        results[scenario] = engine.evaluate(adjusted).value_effort_ratio

    item.effort = original_effort
    return results


def export_csv(
    evaluations: list[Evaluation],
    destination: Path
) -> None:
    """Writes reports without exposing unnecessary internal data."""

    fields = list(Evaluation.__dataclass_fields__.keys())

    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for result in evaluations:
            row = asdict(result)
            row["priority"] = result.priority.value
            row["risk"] = result.risk.value
            writer.writerow(row)


def create_sample_opportunities() -> list[Opportunity]:
    return [
        Opportunity(
            "OP-101",
            "Automated Deployment Validation",
            "Automate deployment verification.",
            5, 5, 4, 5, 5,
            Estimation(2, 3, 5),
            5,
            RiskLevel.LOW,
        ),
        Opportunity(
            "OP-102",
            "Dashboard Redesign",
            "Improve operational reporting.",
            4, 3, 3, 3, 4,
            Estimation(5, 8, 12),
            4,
            RiskLevel.MEDIUM,
        ),
        Opportunity(
            "OP-103",
            "Security Audit Automation",
            "Automate recurring security checks.",
            5, 5, 4, 5, 4,
            Estimation(4, 6, 10),
            4,
            RiskLevel.LOW,
        ),
        Opportunity(
            "OP-104",
            "Documentation Refresh",
            "Improve technical documentation.",
            2, 3, 1, 2, 5,
            Estimation(2, 3, 4),
            5,
            RiskLevel.LOW,
        ),
        Opportunity(
            "OP-105",
            "Data Integration Platform",
            "Connect operational data sources.",
            5, 5, 5, 4, 3,
            Estimation(12, 18, 25),
            3,
            RiskLevel.HIGH,
            ["OP-104"],
        ),
    ]


def main() -> None:
    opportunities = create_sample_opportunities()

    DependencyManager.validate(opportunities)

    engine = PrioritizationEngine()
    evaluations = engine.rank(opportunities)

    print("\nVALUE VS EFFORT OPPORTUNITY MATRIX")
    print("=" * 90)

    print(
        f"{'Opportunity':30} {'Value':>9} {'Adjusted':>10} "
        f"{'Effort':>9} {'Ratio':>9} {'Priority':>23}"
    )

    for result in evaluations:
        print(
            f"{result.name[:30]:30} "
            f"{result.estimated_value:9.2f} "
            f"{result.adjusted_value:10.2f} "
            f"{result.estimated_effort:9.2f} "
            f"{result.value_effort_ratio:9.2f} "
            f"{result.priority.value:>23}"
        )

    selected = capacity_plan(
        opportunities,
        evaluations,
        capacity=15,
    )

    print("\nCAPACITY-CONSTRAINED PORTFOLIO")
    print("-" * 60)

    for result in selected:
        print(f"{result.name}: {result.estimated_effort:.2f} effort units")

    print("\nSENSITIVITY ANALYSIS")
    print("-" * 60)

    for item in opportunities:
        scenarios = sensitivity_analysis(item, engine)
        print(item.name, json.dumps(scenarios))

    output = Path("opportunity_report.csv")
    export_csv(evaluations, output)
    logger.info("Report exported to %s", output.resolve())

    # Basic correctness checks.
    assert len(evaluations) == len(opportunities)
    assert all(result.value_effort_ratio >= 0 for result in evaluations)
    assert sum(
        item.effort.triangular_mean for item in opportunities
        if item.opportunity_id in {r.opportunity_id for r in selected}
    ) <= 15

    print("\nValidation passed.")


if __name__ == "__main__":
    main()
