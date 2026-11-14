#!/usr/bin/env python3
"""
Weighted Shortest Job First (WSJF) Prioritization Engine

WSJF = Cost of Delay / Job Size

Cost of Delay = Business Value + Time Criticality + Risk Reduction
WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size

The implementation includes:
- Validated work-item modeling
- WSJF calculation and ranking
- Tie-breaking rules
- Dependency validation
- Capacity-constrained prioritization
- Scenario analysis
- JSON export
- Unit-style assertions
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Iterable


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("wsjf")


class WorkStatus(str, Enum):
    BACKLOG = "BACKLOG"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class PrioritizationError(Exception):
    """Base exception for prioritization failures."""


class ValidationError(PrioritizationError):
    """Raised when work-item data is invalid."""


class DependencyError(PrioritizationError):
    """Raised when dependencies are invalid."""


def decimal_value(value: object, field_name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f"{field_name} must be numeric")

    if not result.is_finite():
        raise ValidationError(f"{field_name} must be finite")

    return result


@dataclass
class WorkItem:
    item_id: str
    title: str
    business_value: Decimal
    time_criticality: Decimal
    risk_reduction: Decimal
    job_size: Decimal
    status: WorkStatus = WorkStatus.READY
    dependencies: set[str] = field(default_factory=set)
    owner: str = "Unassigned"

    def __post_init__(self) -> None:
        self.item_id = self.item_id.strip()
        self.title = self.title.strip()
        self.owner = self.owner.strip()

        if not self.item_id or not self.title:
            raise ValidationError("Item ID and title are required")

        for name in (
            "business_value",
            "time_criticality",
            "risk_reduction",
            "job_size"
        ):
            value = decimal_value(getattr(self, name), name)
            object.__setattr__(self, name, value)

        if self.job_size <= 0:
            raise ValidationError("Job size must be greater than zero")

        for name in (
            "business_value",
            "time_criticality",
            "risk_reduction"
        ):
            if getattr(self, name) < 0:
                raise ValidationError(f"{name} cannot be negative")

        if self.item_id in self.dependencies:
            raise DependencyError("An item cannot depend on itself")

    @property
    def cost_of_delay(self) -> Decimal:
        return (
            self.business_value
            + self.time_criticality
            + self.risk_reduction
        )

    @property
    def wsjf(self) -> Decimal:
        return self.cost_of_delay / self.job_size

    def to_dict(self) -> dict:
        result = asdict(self)
        for key in (
            "business_value",
            "time_criticality",
            "risk_reduction",
            "job_size"
        ):
            result[key] = str(result[key])

        result["cost_of_delay"] = str(self.cost_of_delay)
        result["wsjf"] = str(self.wsjf)
        result["status"] = self.status.value
        result["dependencies"] = sorted(self.dependencies)
        return result


class WSJFEngine:
    def __init__(self, items: Iterable[WorkItem]):
        self.items: dict[str, WorkItem] = {}

        for item in items:
            self.add_item(item)

        self.validate_dependencies()

    def add_item(self, item: WorkItem) -> None:
        if item.item_id in self.items:
            raise ValidationError(
                f"Duplicate work-item ID: {item.item_id}"
            )

        self.items[item.item_id] = item

    def validate_dependencies(self) -> None:
        for item in self.items.values():
            missing = item.dependencies - self.items.keys()

            if missing:
                raise DependencyError(
                    f"{item.item_id} references missing dependencies: "
                    f"{sorted(missing)}"
                )

        # Detect dependency cycles using depth-first search.
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(item_id: str) -> None:
            if item_id in visiting:
                raise DependencyError(
                    f"Dependency cycle detected at {item_id}"
                )

            if item_id in visited:
                return

            visiting.add(item_id)

            for dependency in self.items[item_id].dependencies:
                visit(dependency)

            visiting.remove(item_id)
            visited.add(item_id)

        for item_id in self.items:
            visit(item_id)

    def rank(
        self,
        include_blocked: bool = False
    ) -> list[WorkItem]:

        candidates = [
            item for item in self.items.values()
            if item.status not in (
                WorkStatus.COMPLETED,
                WorkStatus.IN_PROGRESS
            )
            and (
                include_blocked
                or item.status != WorkStatus.BLOCKED
            )
        ]

        # Deterministic ordering for equal WSJF values.
        return sorted(
            candidates,
            key=lambda item: (
                -item.wsjf,
                -item.cost_of_delay,
                item.job_size,
                item.item_id
            )
        )

    def dependency_ready(self, item: WorkItem) -> bool:
        return all(
            self.items[dependency].status == WorkStatus.COMPLETED
            for dependency in item.dependencies
        )

    def capacity_plan(
        self,
        capacity: Decimal
    ) -> list[WorkItem]:

        capacity = decimal_value(capacity, "capacity")

        if capacity < 0:
            raise ValidationError("Capacity cannot be negative")

        selected: list[WorkItem] = []
        remaining = capacity
        completed_in_plan: set[str] = {
            item.item_id
            for item in self.items.values()
            if item.status == WorkStatus.COMPLETED
        }

        candidates = self.rank()

        # Repeatedly select the highest-ranked dependency-ready item
        # that fits the remaining capacity.
        while True:
            eligible = [
                item for item in candidates
                if item.item_id not in completed_in_plan
                and item not in selected
                and item.job_size <= remaining
                and all(
                    dependency in completed_in_plan
                    for dependency in item.dependencies
                )
            ]

            if not eligible:
                break

            chosen = eligible[0]
            selected.append(chosen)
            completed_in_plan.add(chosen.item_id)
            remaining -= chosen.job_size

        return selected

    def scenario_analysis(
        self,
        item_id: str,
        business_value_change: Decimal = Decimal("0"),
        time_criticality_change: Decimal = Decimal("0"),
        risk_reduction_change: Decimal = Decimal("0"),
        job_size_change: Decimal = Decimal("0")
    ) -> dict:

        if item_id not in self.items:
            raise ValidationError(f"Unknown item: {item_id}")

        item = self.items[item_id]

        changes = {
            "business_value": business_value_change,
            "time_criticality": time_criticality_change,
            "risk_reduction": risk_reduction_change,
            "job_size": job_size_change
        }

        updated = {}

        for name, change in changes.items():
            value = getattr(item, name) + decimal_value(change, name)

            if name == "job_size" and value <= 0:
                raise ValidationError(
                    "Scenario job size must remain positive"
                )

            if name != "job_size" and value < 0:
                raise ValidationError(
                    f"Scenario {name} cannot become negative"
                )

            updated[name] = value

        cost_of_delay = (
            updated["business_value"]
            + updated["time_criticality"]
            + updated["risk_reduction"]
        )

        return {
            "item_id": item_id,
            "original_wsjf": str(item.wsjf),
            "scenario_cost_of_delay": str(cost_of_delay),
            "scenario_job_size": str(updated["job_size"]),
            "scenario_wsjf": str(
                cost_of_delay / updated["job_size"]
            )
        }

    def export_json(self, destination: Path) -> None:
        payload = {
            "formula": (
                "(business_value + time_criticality + "
                "risk_reduction) / job_size"
            ),
            "items": [
                item.to_dict()
                for item in sorted(
                    self.items.values(),
                    key=lambda item: item.item_id
                )
            ],
            "ranking": [
                item.item_id for item in self.rank()
            ]
        }

        # Exclusive file permissions are not a substitute for
        # operating-system access controls.
        destination.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8"
        )


def create_sample_items() -> list[WorkItem]:
    return [
        WorkItem(
            "P-101",
            "Payment gateway modernization",
            Decimal("9"),
            Decimal("10"),
            Decimal("8"),
            Decimal("5"),
            dependencies=set()
        ),
        WorkItem(
            "P-102",
            "Security vulnerability remediation",
            Decimal("8"),
            Decimal("10"),
            Decimal("10"),
            Decimal("3")
        ),
        WorkItem(
            "P-103",
            "Customer analytics dashboard",
            Decimal("8"),
            Decimal("5"),
            Decimal("3"),
            Decimal("8")
        ),
        WorkItem(
            "P-104",
            "Database migration foundation",
            Decimal("7"),
            Decimal("6"),
            Decimal("9"),
            Decimal("5")
        ),
        WorkItem(
            "P-105",
            "Automated regression testing",
            Decimal("6"),
            Decimal("7"),
            Decimal("8"),
            Decimal("3"),
            dependencies={"P-104"}
        ),
        WorkItem(
            "P-106",
            "User interface refinement",
            Decimal("5"),
            Decimal("3"),
            Decimal("2"),
            Decimal("5")
        ),
        WorkItem(
            "P-107",
            "Compliance audit preparation",
            Decimal("8"),
            Decimal("9"),
            Decimal("10"),
            Decimal("4")
        )
    ]


def run_tests(engine: WSJFEngine) -> None:
    assert engine.items["P-101"].cost_of_delay == Decimal("27")
    assert engine.items["P-101"].wsjf == Decimal("27") / Decimal("5")

    assert engine.items["P-102"].wsjf == Decimal("28") / Decimal("3")

    assert engine.dependency_ready(
        engine.items["P-104"]
    )

    assert not engine.dependency_ready(
        engine.items["P-105"]
    )

    assert engine.scenario_analysis(
        "P-101",
        business_value_change=Decimal("3")
    )["scenario_wsjf"] == "6"

    try:
        WorkItem(
            "INVALID",
            "Invalid task",
            Decimal("5"),
            Decimal("5"),
            Decimal("5"),
            Decimal("0")
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Zero job size must be rejected")

    logger.info("All validation assertions passed")


def main() -> None:
    engine = WSJFEngine(create_sample_items())

    run_tests(engine)

    print("\nWSJF PRIORITIZATION REPORT")
    print("=" * 90)
    print(
        f"{'ID':<10}{'WORK ITEM':<36}"
        f"{'CoD':>10}{'SIZE':>10}{'WSJF':>12}"
    )
    print("-" * 90)

    for item in engine.rank():
        print(
            f"{item.item_id:<10}"
            f"{item.title:<36}"
            f"{item.cost_of_delay:>10}"
            f"{item.job_size:>10}"
            f"{item.wsjf:>12.3f}"
        )

    print("\nCAPACITY-CONSTRAINED PLAN")
    print("-" * 60)

    plan = engine.capacity_plan(Decimal("12"))

    for position, item in enumerate(plan, start=1):
        print(
            f"{position}. {item.item_id}: "
            f"{item.title} | WSJF={item.wsjf:.3f}"
        )

    print("\nSCENARIO ANALYSIS")
    print("-" * 60)

    scenario = engine.scenario_analysis(
        "P-103",
        business_value_change=Decimal("3"),
        time_criticality_change=Decimal("2")
    )

    print(json.dumps(scenario, indent=2))

    output = Path("wsjf_report.json")
    engine.export_json(output)
    print(f"\nReport exported to {output.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except (PrioritizationError, OSError) as error:
        logger.error("Execution failed: %s", error)
        raise SystemExit(1)
