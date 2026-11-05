from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4
import json
import statistics


class IndicatorType(Enum):
    LEADING = "leading"
    LAGGING = "lagging"


class ObjectiveStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OKRError(Exception):
    pass


@dataclass
class KeyResult:
    title: str
    target: float
    current: float
    unit: str
    indicator_type: IndicatorType
    baseline: float = 0.0
    weight: float = 1.0
    higher_is_better: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Key result title cannot be empty.")
        if self.target == self.baseline:
            raise ValueError("Target must differ from baseline.")
        if self.weight <= 0:
            raise ValueError("Weight must be positive.")
        if self.target < self.baseline and self.higher_is_better:
            raise ValueError("Target must exceed baseline for this metric.")
        if self.target > self.baseline and not self.higher_is_better:
            raise ValueError("Target must be below baseline for this metric.")

    @property
    def progress(self) -> float:
        denominator = self.target - self.baseline
        value = (self.current - self.baseline) / denominator
        return max(0.0, min(1.0, value))

    def update(self, value: float, note: str = ""):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Current value must be numeric.")
        if not -1e12 <= value <= 1e12:
            raise ValueError("Value is outside the supported range.")

        self.current = float(value)
        self.history.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "value": self.current,
            "note": note[:500]
        })

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "baseline": self.baseline,
            "current": self.current,
            "target": self.target,
            "unit": self.unit,
            "indicator_type": self.indicator_type.value,
            "weight": self.weight,
            "progress": round(self.progress, 4),
            "history": self.history
        }


@dataclass
class Objective:
    title: str
    owner: str
    department: str
    period: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ObjectiveStatus = ObjectiveStatus.DRAFT
    parent_id: Optional[str] = None
    key_results: list[KeyResult] = field(default_factory=list)

    def add_key_result(self, kr: KeyResult):
        if any(existing.title == kr.title for existing in self.key_results):
            raise OKRError("Duplicate key result in objective.")
        self.key_results.append(kr)

    def activate(self):
        if not self.key_results:
            raise OKRError("An objective requires at least one key result.")
        if self.status not in (ObjectiveStatus.DRAFT, ObjectiveStatus.ACTIVE):
            raise OKRError("This objective cannot be activated.")
        self.status = ObjectiveStatus.ACTIVE

    @property
    def progress(self) -> float:
        if not self.key_results:
            return 0.0
        total_weight = sum(kr.weight for kr in self.key_results)
        return sum(
            kr.progress * kr.weight for kr in self.key_results
        ) / total_weight

    @property
    def leading_progress(self) -> Optional[float]:
        results = [
            kr for kr in self.key_results
            if kr.indicator_type == IndicatorType.LEADING
        ]
        if not results:
            return None
        return statistics.mean(kr.progress for kr in results)

    @property
    def lagging_progress(self) -> Optional[float]:
        results = [
            kr for kr in self.key_results
            if kr.indicator_type == IndicatorType.LAGGING
        ]
        if not results:
            return None
        return statistics.mean(kr.progress for kr in results)

    def evaluate(self):
        if self.status in (ObjectiveStatus.CANCELLED, ObjectiveStatus.COMPLETED):
            return self.status

        if self.progress >= 1.0:
            self.status = ObjectiveStatus.COMPLETED
        elif self.progress < 0.4:
            self.status = ObjectiveStatus.AT_RISK
        else:
            self.status = ObjectiveStatus.ACTIVE

        return self.status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "owner": self.owner,
            "department": self.department,
            "period": self.period,
            "description": self.description,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "progress": round(self.progress, 4),
            "leading_progress": self.leading_progress,
            "lagging_progress": self.lagging_progress,
            "key_results": [kr.to_dict() for kr in self.key_results]
        }


class OKRManager:
    """Maintains objectives, alignment, updates, and reporting."""

    def __init__(self):
        self.objectives: dict[str, Objective] = {}
        self.events: list[dict] = []

    def add_objective(self, objective: Objective):
        if objective.id in self.objectives:
            raise OKRError("Objective ID already exists.")

        if objective.parent_id is not None:
            if objective.parent_id not in self.objectives:
                raise OKRError("Parent objective does not exist.")
            parent = self.objectives[objective.parent_id]
            if parent.period != objective.period:
                raise OKRError("Aligned objectives must share a period.")

        self.objectives[objective.id] = objective
        self._log("objective_created", objective.id)

    def activate(self, objective_id: str):
        objective = self._get(objective_id)
        objective.activate()
        self._log("objective_activated", objective_id)

    def update_key_result(
        self,
        objective_id: str,
        key_result_id: str,
        value: float,
        note: str = ""
    ):
        objective = self._get(objective_id)

        if objective.status not in (
            ObjectiveStatus.ACTIVE,
            ObjectiveStatus.AT_RISK
        ):
            raise OKRError("Only active objectives can receive updates.")

        key_result = next(
            (kr for kr in objective.key_results if kr.id == key_result_id),
            None
        )

        if key_result is None:
            raise OKRError("Key result not found.")

        previous = key_result.current
        key_result.update(value, note)
        status = objective.evaluate()

        self._log(
            "key_result_updated",
            objective_id,
            key_result_id=key_result_id,
            previous=previous,
            current=value,
            status=status.value
        )

    def _get(self, objective_id: str) -> Objective:
        try:
            return self.objectives[objective_id]
        except KeyError:
            raise OKRError("Objective not found.") from None

    def _log(self, event_type: str, objective_id: str, **details):
        self.events.append({
            "event": event_type,
            "objective_id": objective_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "details": details
        })

    def alignment_tree(self, objective_id: str):
        objective = self._get(objective_id)
        children = [
            item for item in self.objectives.values()
            if item.parent_id == objective.id
        ]
        return {
            "objective": objective.title,
            "progress": round(objective.progress, 3),
            "children": [
                self.alignment_tree(child.id) for child in children
            ]
        }

    def report(self):
        result = []
        for objective in self.objectives.values():
            objective.evaluate()
            result.append({
                "objective": objective.title,
                "owner": objective.owner,
                "department": objective.department,
                "status": objective.status.value,
                "progress": round(objective.progress * 100, 2),
                "leading_progress": (
                    None if objective.leading_progress is None
                    else round(objective.leading_progress * 100, 2)
                ),
                "lagging_progress": (
                    None if objective.lagging_progress is None
                    else round(objective.lagging_progress * 100, 2)
                )
            })
        return result

    def save(self, filename: str):
        data = {
            "objectives": [
                objective.to_dict()
                for objective in self.objectives.values()
            ],
            "events": self.events
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def export_csv(self, filename: str):
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "objective", "owner", "department",
                    "status", "progress", "leading_progress",
                    "lagging_progress"
                ]
            )
            writer.writeheader()
            writer.writerows(self.report())


def demonstrate():
    manager = OKRManager()

    company = Objective(
        title="Become the preferred digital banking platform",
        owner="Chief Executive Officer",
        department="Executive",
        period="2026-Q4"
    )

    company.add_key_result(KeyResult(
        title="Customer satisfaction score",
        baseline=70,
        current=76,
        target=90,
        unit="points",
        indicator_type=IndicatorType.LAGGING,
        weight=2
    ))

    company.add_key_result(KeyResult(
        title="Monthly active customers",
        baseline=100000,
        current=125000,
        target=200000,
        unit="customers",
        indicator_type=IndicatorType.LAGGING
    ))

    manager.add_objective(company)

    product = Objective(
        title="Improve mobile banking adoption",
        owner="Product Director",
        department="Product",
        period="2026-Q4",
        parent_id=company.id
    )

    product.add_key_result(KeyResult(
        title="Weekly usability tests completed",
        baseline=0,
        current=12,
        target=20,
        unit="tests",
        indicator_type=IndicatorType.LEADING
    ))

    product.add_key_result(KeyResult(
        title="Mobile onboarding completion rate",
        baseline=40,
        current=55,
        target=80,
        unit="percent",
        indicator_type=IndicatorType.LAGGING
    ))

    manager.add_objective(product)

    manager.activate(company.id)
    manager.activate(product.id)

    kr = product.key_results[0]

    manager.update_key_result(
        product.id,
        kr.id,
        16,
        "Completed additional usability sessions."
    )

    print("OKR PERFORMANCE REPORT")
    print("=" * 65)

    for row in manager.report():
        print(json.dumps(row, indent=2))

    print("\nALIGNMENT TREE")
    print(json.dumps(manager.alignment_tree(company.id), indent=2))

    print("\nEVENT AUDIT")
    print(f"Recorded events: {len(manager.events)}")

    manager.save("okr_report.json")
    manager.export_csv("okr_report.csv")

    print("\nFiles created: okr_report.json, okr_report.csv")

    # Edge-case checks.
    assert 0 <= product.progress <= 1
    assert product.leading_progress is not None
    assert product.lagging_progress is not None

    try:
        manager.update_key_result(
            product.id, "invalid-id", 100
        )
    except OKRError as error:
        print("Expected validation:", error)


if __name__ == "__main__":
    demonstrate()
