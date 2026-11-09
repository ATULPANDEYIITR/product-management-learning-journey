#!/usr/bin/env python3
"""
Prioritization Fundamentals
---------------------------
A portfolio prioritization simulator covering:
- Why prioritization matters
- Limited resources and competing constraints
- Opportunity cost
- RICE, WSJF, MoSCoW, and weighted scoring
- Dependencies and mandatory initiatives
- Capacity-aware portfolio selection
- Sensitivity analysis
- Decision records and audit history

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import logging
import math
import tempfile
import unittest

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger("prioritization")


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    PROPOSED = "proposed"
    EVALUATED = "evaluated"
    SELECTED = "selected"
    DEFERRED = "deferred"
    REJECTED = "rejected"


class Framework(str, Enum):
    RICE = "rice"
    WSJF = "wsjf"
    WEIGHTED = "weighted"


@dataclass
class Initiative:
    initiative_id: str
    name: str
    description: str
    reach: float
    impact: float
    confidence: float
    effort: float
    business_value: float
    time_criticality: float
    risk_reduction: float
    strategic_alignment: float
    cost: float
    mandatory: bool = False
    priority: Priority = Priority.MEDIUM
    dependencies: set[str] = field(default_factory=set)
    status: Status = Status.PROPOSED

    def validate(self) -> None:
        if not self.initiative_id.strip():
            raise ValueError("Initiative ID cannot be empty.")

        if not self.name.strip():
            raise ValueError("Initiative name cannot be empty.")

        numeric_fields = {
            "reach": self.reach,
            "impact": self.impact,
            "confidence": self.confidence,
            "effort": self.effort,
            "business_value": self.business_value,
            "time_criticality": self.time_criticality,
            "risk_reduction": self.risk_reduction,
            "strategic_alignment": self.strategic_alignment,
            "cost": self.cost,
        }

        for field_name, value in numeric_fields.items():
            if not math.isfinite(value):
                raise ValueError(f"{field_name} must be finite.")

            if value < 0:
                raise ValueError(f"{field_name} cannot be negative.")

        if self.effort <= 0:
            raise ValueError("Effort must be greater than zero.")

        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1.")

        for field_name in (
            "impact",
            "business_value",
            "time_criticality",
            "risk_reduction",
            "strategic_alignment",
        ):
            if getattr(self, field_name) > 10:
                raise ValueError(f"{field_name} cannot exceed 10.")

        if self.initiative_id in self.dependencies:
            raise ValueError("An initiative cannot depend on itself.")


@dataclass(frozen=True)
class Capacity:
    available_effort: float
    available_budget: float

    def __post_init__(self):
        if not math.isfinite(self.available_effort):
            raise ValueError("Effort capacity must be finite.")

        if not math.isfinite(self.available_budget):
            raise ValueError("Budget capacity must be finite.")

        if self.available_effort < 0 or self.available_budget < 0:
            raise ValueError("Capacity cannot be negative.")


@dataclass
class Decision:
    initiative_id: str
    framework: str
    score: float
    status: Status
    reason: str
    opportunity_cost: float = 0.0


@dataclass
class PortfolioResult:
    selected: list[str]
    deferred: list[str]
    total_effort: float
    total_budget: float
    remaining_effort: float
    remaining_budget: float
    total_value: float
    decisions: list[Decision]


class PrioritizationEngine:

    def __init__(self, initiatives: list[Initiative]):
        self.initiatives = {
            item.initiative_id: item
            for item in initiatives
        }

        if len(self.initiatives) != len(initiatives):
            raise ValueError("Duplicate initiative IDs.")

        for initiative in initiatives:
            initiative.validate()

        self._validate_dependencies()

        self.history: list[dict] = []

    def _validate_dependencies(self) -> None:
        for initiative in self.initiatives.values():
            missing = initiative.dependencies - self.initiatives.keys()

            if missing:
                raise ValueError(
                    f"{initiative.initiative_id} has missing dependencies: "
                    f"{sorted(missing)}"
                )

        # Detect circular dependencies using depth-first traversal.
        visiting = set()
        visited = set()

        def visit(identifier: str):
            if identifier in visiting:
                raise ValueError("Circular dependency detected.")

            if identifier in visited:
                return

            visiting.add(identifier)

            for dependency in self.initiatives[identifier].dependencies:
                visit(dependency)

            visiting.remove(identifier)
            visited.add(identifier)

        for identifier in self.initiatives:
            visit(identifier)

    @staticmethod
    def rice(item: Initiative) -> float:
        return (
            item.reach
            * item.impact
            * item.confidence
            / item.effort
        )

    @staticmethod
    def wsjf(item: Initiative) -> float:
        cost_of_delay = (
            item.business_value
            + item.time_criticality
            + item.risk_reduction
        )
        return cost_of_delay / item.effort

    @staticmethod
    def weighted_score(item: Initiative) -> float:
        weights = {
            "business_value": 0.30,
            "strategic_alignment": 0.30,
            "time_criticality": 0.15,
            "risk_reduction": 0.15,
            "confidence": 0.10,
        }

        normalized = {
            "business_value": item.business_value / 10,
            "strategic_alignment": item.strategic_alignment / 10,
            "time_criticality": item.time_criticality / 10,
            "risk_reduction": item.risk_reduction / 10,
            "confidence": item.confidence,
        }

        return sum(
            normalized[key] * weight
            for key, weight in weights.items()
        ) * 100

    def score(
        self,
        item: Initiative,
        framework: Framework
    ) -> float:

        scorers: dict[Framework, Callable] = {
            Framework.RICE: self.rice,
            Framework.WSJF: self.wsjf,
            Framework.WEIGHTED: self.weighted_score,
        }

        return scorers[framework](item)

    def rank(
        self,
        framework: Framework = Framework.WEIGHTED
    ) -> list[tuple[Initiative, float]]:

        ranked = [
            (item, self.score(item, framework))
            for item in self.initiatives.values()
        ]

        # Mandatory work receives precedence over discretionary work.
        ranked.sort(
            key=lambda pair: (
                not pair[0].mandatory,
                -pair[1],
                pair[0].initiative_id,
            )
        )

        return ranked

    def _dependency_closure(self, identifier: str) -> set[str]:
        result = set()
        stack = [identifier]

        while stack:
            current = stack.pop()

            if current in result:
                continue

            result.add(current)
            stack.extend(
                self.initiatives[current].dependencies
            )

        return result

    def allocate(
        self,
        capacity: Capacity,
        framework: Framework = Framework.WEIGHTED,
    ) -> PortfolioResult:

        selected: set[str] = set()
        rejected: set[str] = set()

        total_effort = 0.0
        total_budget = 0.0
        total_value = 0.0

        scores = {
            identifier: self.score(item, framework)
            for identifier, item in self.initiatives.items()
        }

        decisions = []

        ranked = self.rank(framework)

        # Mandatory initiatives are evaluated before discretionary work.
        for item, _ in ranked:
            if not item.mandatory:
                continue

            closure = self._dependency_closure(item.initiative_id)
            new_items = closure - selected

            effort = sum(
                self.initiatives[key].effort
                for key in new_items
            )

            budget = sum(
                self.initiatives[key].cost
                for key in new_items
            )

            if (
                total_effort + effort > capacity.available_effort
                or total_budget + budget > capacity.available_budget
            ):
                raise ValueError(
                    f"Mandatory initiative {item.initiative_id} "
                    "cannot fit available capacity."
                )

            selected.update(new_items)

            total_effort += effort
            total_budget += budget

        # Greedy selection uses dependency closure and both resource limits.
        for item, score in ranked:

            if item.initiative_id in selected:
                continue

            if item.initiative_id in rejected:
                continue

            closure = self._dependency_closure(item.initiative_id)
            new_items = closure - selected

            effort = sum(
                self.initiatives[key].effort
                for key in new_items
            )

            budget = sum(
                self.initiatives[key].cost
                for key in new_items
            )

            if (
                total_effort + effort > capacity.available_effort
                or total_budget + budget > capacity.available_budget
            ):
                rejected.add(item.initiative_id)
                continue

            selected.update(new_items)
            total_effort += effort
            total_budget += budget

        # Calculate selected value independently of scoring framework.
        total_value = sum(
            self.initiatives[key].business_value
            for key in selected
        )

        deferred = set(self.initiatives) - selected

        # Estimate opportunity cost as the weighted value of excluded work.
        excluded_scores = sorted(
            (scores[key] for key in deferred),
            reverse=True
        )

        opportunity_cost = sum(excluded_scores)

        for identifier in self.initiatives:
            item = self.initiatives[identifier]
            is_selected = identifier in selected

            item.status = (
                Status.SELECTED if is_selected else Status.DEFERRED
            )

            reason = (
                "Included within available portfolio capacity."
                if is_selected
                else "Deferred because of resource constraints or ranking."
            )

            decisions.append(
                Decision(
                    initiative_id=identifier,
                    framework=framework.value,
                    score=scores[identifier],
                    status=item.status,
                    reason=reason,
                    opportunity_cost=(
                        opportunity_cost if not is_selected else 0.0
                    ),
                )
            )

        result = PortfolioResult(
            selected=sorted(selected),
            deferred=sorted(deferred),
            total_effort=total_effort,
            total_budget=total_budget,
            remaining_effort=capacity.available_effort - total_effort,
            remaining_budget=capacity.available_budget - total_budget,
            total_value=total_value,
            decisions=decisions,
        )

        self.history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework": framework.value,
            "capacity": asdict(capacity),
            "result": {
                "selected": result.selected,
                "deferred": result.deferred,
                "total_effort": result.total_effort,
                "total_budget": result.total_budget,
                "total_value": result.total_value,
            },
        })

        return result

    def sensitivity_analysis(
        self,
        capacity: Capacity,
        frameworks: Optional[list[Framework]] = None,
    ) -> dict:

        frameworks = frameworks or list(Framework)
        report = {}

        for framework in frameworks:
            result = self.allocate(capacity, framework)

            report[framework.value] = {
                "selected": result.selected,
                "deferred": result.deferred,
                "business_value": result.total_value,
            }

        return report

    def export_history(self, destination: Path) -> None:
        # Write to a temporary file and atomically replace the destination.
        destination.parent.mkdir(parents=True, exist_ok=True)

        temporary = destination.with_suffix(
            destination.suffix + ".tmp"
        )

        try:
            temporary.write_text(
                json.dumps(self.history, indent=2),
                encoding="utf-8",
            )

            temporary.replace(destination)

        except OSError:
            temporary.unlink(missing_ok=True)
            raise


def build_sample_portfolio() -> list[Initiative]:
    return [
        Initiative(
            "I001",
            "Security compliance",
            "Close a mandatory security compliance gap.",
            100, 10, 0.98, 8,
            10, 10, 10, 10,
            12000,
            mandatory=True,
            priority=Priority.CRITICAL,
        ),
        Initiative(
            "I002",
            "Customer analytics",
            "Develop customer usage analytics.",
            8000, 8, 0.85, 13,
            9, 7, 4, 9,
            18000,
            dependencies={"I001"},
        ),
        Initiative(
            "I003",
            "Infrastructure optimization",
            "Reduce cloud infrastructure expenditure.",
            5000, 7, 0.95, 5,
            8, 8, 6, 8,
            7000,
        ),
        Initiative(
            "I004",
            "Internal dashboard",
            "Improve internal operational reporting.",
            2000, 5, 0.90, 4,
            5, 3, 2, 6,
            4000,
        ),
        Initiative(
            "I005",
            "Disaster recovery",
            "Improve system recovery capabilities.",
            1000, 9, 0.90, 7,
            9, 9, 10, 9,
            10000,
        ),
        Initiative(
            "I006",
            "Mobile redesign",
            "Refresh the mobile application interface.",
            6000, 6, 0.75, 10,
            7, 5, 3, 8,
            14000,
        ),
    ]


class PrioritizationTests(unittest.TestCase):

    def setUp(self):
        self.engine = PrioritizationEngine(
            build_sample_portfolio()
        )

    def test_rice_score(self):
        item = self.engine.initiatives["I003"]
        self.assertAlmostEqual(
            self.engine.rice(item),
            6650,
        )

    def test_capacity_limits(self):
        result = self.engine.allocate(
            Capacity(available_effort=20, available_budget=25000)
        )

        self.assertLessEqual(result.total_effort, 20)
        self.assertLessEqual(result.total_budget, 25000)

    def test_mandatory_selection(self):
        result = self.engine.allocate(
            Capacity(30, 50000)
        )

        self.assertIn("I001", result.selected)

    def test_missing_dependency(self):
        with self.assertRaises(ValueError):
            PrioritizationEngine([
                Initiative(
                    "A", "A", "Example",
                    1, 1, 1, 1,
                    1, 1, 1, 1,
                    1,
                    dependencies={"MISSING"},
                )
            ])

    def test_invalid_effort(self):
        item = build_sample_portfolio()[0]
        item.effort = 0

        with self.assertRaises(ValueError):
            item.validate()

    def test_circular_dependency(self):
        a = Initiative(
            "A", "A", "A",
            1, 1, 1, 1,
            1, 1, 1, 1,
            1,
            dependencies={"B"},
        )

        b = Initiative(
            "B", "B", "B",
            1, 1, 1, 1,
            1, 1, 1, 1,
            1,
            dependencies={"A"},
        )

        with self.assertRaises(ValueError):
            PrioritizationEngine([a, b])


def main():
    engine = PrioritizationEngine(build_sample_portfolio())

    capacity = Capacity(
        available_effort=35,
        available_budget=45000,
    )

    print("\nPRIORITIZATION FUNDAMENTALS")
    print("=" * 65)

    for framework in Framework:
        print(f"\nFramework: {framework.value.upper()}")

        for item, score in engine.rank(framework):
            print(
                f"{item.initiative_id:6} "
                f"{item.name:30} "
                f"Score: {score:.2f}"
            )

    result = engine.allocate(capacity, Framework.WEIGHTED)

    print("\nPORTFOLIO ALLOCATION")
    print("=" * 65)
    print("Selected:", ", ".join(result.selected))
    print("Deferred:", ", ".join(result.deferred))
    print(f"Effort consumed: {result.total_effort:.2f}")
    print(f"Budget consumed: {result.total_budget:.2f}")
    print(f"Business value: {result.total_value:.2f}")
    print(f"Remaining effort: {result.remaining_effort:.2f}")
    print(f"Remaining budget: {result.remaining_budget:.2f}")

    print("\nSENSITIVITY ANALYSIS")

    analysis = engine.sensitivity_analysis(capacity)

    for framework, values in analysis.items():
        print(
            f"{framework:10} "
            f"Selected: {values['selected']} "
            f"Value: {values['business_value']:.2f}"
        )

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "decision_history.json"
        engine.export_history(path)

        print("\nDecision history exported:", path.name)

    print("\nRUNNING VALIDATION TESTS")

    unittest.main(argv=["prioritization"], exit=False)


if __name__ == "__main__":
    main()
