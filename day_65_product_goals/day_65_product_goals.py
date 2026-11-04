#!/usr/bin/env python3
"""
Product Goals: Outcome Goals, OKRs, KPIs, Strategic Metrics, and Measurable Outcomes.

A self-contained product performance management system supporting:
- Strategic objectives
- Objectives and Key Results (OKRs)
- Key Performance Indicators (KPIs)
- Baselines and measurable targets
- Metric aggregation and progress evaluation
- Confidence and data-quality validation
- Goal ownership and accountability
- Outcome measurement and reporting
- Historical observations
- Risk identification and goal status transitions
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class GoalError(Exception):
    """Base exception for product goal management."""


class ValidationError(GoalError):
    """Raised when goal or measurement data is invalid."""


class DuplicateGoalError(GoalError):
    """Raised when a duplicate goal is registered."""


class GoalType(str, Enum):
    STRATEGIC = "strategic"
    OUTCOME = "outcome"
    OKR = "okr"
    KPI = "kpi"


class Direction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


class GoalStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    AT_RISK = "at_risk"
    ACHIEVED = "achieved"
    MISSED = "missed"
    CANCELLED = "cancelled"


@dataclass
class Measurement:
    value: float
    recorded_at: str
    source: str
    confidence: float = 1.0

    def __post_init__(self):
        if not math.isfinite(self.value):
            raise ValidationError("Measurement must be finite.")

        if not 0 <= self.confidence <= 1:
            raise ValidationError("Confidence must be between 0 and 1.")

        if not self.source.strip():
            raise ValidationError("Measurement source is required.")

        try:
            datetime.fromisoformat(self.recorded_at)
        except ValueError as exc:
            raise ValidationError("Invalid measurement timestamp.") from exc


@dataclass
class KeyResult:
    id: str
    title: str
    baseline: float
    target: float
    direction: Direction
    unit: str
    weight: float = 1.0
    measurements: list[Measurement] = field(default_factory=list)

    def __post_init__(self):
        if not self.id.strip() or not self.title.strip():
            raise ValidationError("Key Result ID and title are required.")

        if not math.isfinite(self.baseline) or not math.isfinite(self.target):
            raise ValidationError("Baseline and target must be finite.")

        if not math.isfinite(self.weight) or self.weight <= 0:
            raise ValidationError("Weight must be positive and finite.")

        if self.baseline == self.target:
            raise ValidationError("Baseline and target must differ.")

        if self.direction == Direction.INCREASE and self.target <= self.baseline:
            raise ValidationError("Increase goals require a higher target.")

        if self.direction == Direction.DECREASE and self.target >= self.baseline:
            raise ValidationError("Decrease goals require a lower target.")

        if self.direction == Direction.MAINTAIN:
            raise ValidationError("Use an outcome target different from baseline.")

    @property
    def current_value(self) -> float:
        if not self.measurements:
            return self.baseline

        return max(
            self.measurements,
            key=lambda m: datetime.fromisoformat(m.recorded_at)
        ).value

    @property
    def progress(self) -> float:
        difference = self.target - self.baseline

        raw = (
            (self.current_value - self.baseline) / difference
        ) * 100

        return max(0.0, min(100.0, raw))

    @property
    def remaining(self) -> float:
        return self.target - self.current_value

    @property
    def latest_confidence(self) -> float:
        if not self.measurements:
            return 0.0

        latest = max(
            self.measurements,
            key=lambda m: datetime.fromisoformat(m.recorded_at)
        )
        return latest.confidence

    def record(self, measurement: Measurement) -> None:
        if self.measurements:
            latest = max(
                datetime.fromisoformat(m.recorded_at)
                for m in self.measurements
            )
            incoming = datetime.fromisoformat(measurement.recorded_at)

            if incoming <= latest:
                raise ValidationError(
                    "New measurements must have a later timestamp."
                )

        self.measurements.append(measurement)


@dataclass
class ProductGoal:
    id: str
    title: str
    description: str
    goal_type: GoalType
    owner: str
    start_date: date
    end_date: date
    key_results: list[KeyResult] = field(default_factory=list)
    status: GoalStatus = GoalStatus.DRAFT
    parent_id: Optional[str] = None

    def __post_init__(self):
        if not all([
            self.id.strip(),
            self.title.strip(),
            self.owner.strip()
        ]):
            raise ValidationError("Goal ID, title, and owner are required.")

        if self.end_date <= self.start_date:
            raise ValidationError("End date must follow start date.")

        if self.goal_type == GoalType.OKR and not self.key_results:
            raise ValidationError("An OKR requires at least one Key Result.")

        ids = [kr.id for kr in self.key_results]

        if len(ids) != len(set(ids)):
            raise ValidationError("Duplicate Key Result IDs.")

    @property
    def progress(self) -> float:
        if not self.key_results:
            return 0.0

        total_weight = sum(kr.weight for kr in self.key_results)

        return sum(
            kr.progress * kr.weight
            for kr in self.key_results
        ) / total_weight

    @property
    def average_confidence(self) -> float:
        if not self.key_results:
            return 0.0

        return statistics.mean(
            kr.latest_confidence for kr in self.key_results
        )

    def activate(self) -> None:
        if self.status != GoalStatus.DRAFT:
            raise GoalError("Only draft goals can be activated.")

        self.status = GoalStatus.ACTIVE

    def evaluate(self, today: date) -> GoalStatus:
        if self.status in (GoalStatus.CANCELLED, GoalStatus.DRAFT):
            return self.status

        if self.progress >= 100:
            self.status = GoalStatus.ACHIEVED

        elif today > self.end_date:
            self.status = GoalStatus.MISSED

        elif self.progress < 40:
            self.status = GoalStatus.AT_RISK

        else:
            self.status = GoalStatus.ACTIVE

        return self.status


class ProductGoalManager:
    def __init__(self):
        self.goals: dict[str, ProductGoal] = {}

    def add_goal(self, goal: ProductGoal) -> None:
        if goal.id in self.goals:
            raise DuplicateGoalError(f"Goal already exists: {goal.id}")

        if goal.parent_id and goal.parent_id not in self.goals:
            raise ValidationError("Parent goal does not exist.")

        if goal.parent_id == goal.id:
            raise ValidationError("A goal cannot be its own parent.")

        self.goals[goal.id] = goal

    def record_measurement(
        self,
        goal_id: str,
        key_result_id: str,
        measurement: Measurement
    ) -> None:
        goal = self.goals[goal_id]

        key_result = next(
            (
                kr for kr in goal.key_results
                if kr.id == key_result_id
            ),
            None
        )

        if key_result is None:
            raise ValidationError("Key Result not found.")

        if goal.status != GoalStatus.ACTIVE:
            raise GoalError("Measurements require an active goal.")

        key_result.record(measurement)

    def evaluate_all(self, today: date) -> dict[str, str]:
        return {
            goal.id: goal.evaluate(today).value
            for goal in self.goals.values()
        }

    def strategic_alignment(self, parent_id: str) -> list[ProductGoal]:
        return [
            goal for goal in self.goals.values()
            if goal.parent_id == parent_id
        ]

    def report(self) -> dict:
        results = []

        for goal in self.goals.values():
            results.append({
                "id": goal.id,
                "title": goal.title,
                "type": goal.goal_type.value,
                "owner": goal.owner,
                "status": goal.status.value,
                "progress_percent": round(goal.progress, 2),
                "confidence": round(goal.average_confidence, 2),
                "key_results": [
                    {
                        "id": kr.id,
                        "title": kr.title,
                        "baseline": kr.baseline,
                        "current": kr.current_value,
                        "target": kr.target,
                        "unit": kr.unit,
                        "progress_percent": round(kr.progress, 2),
                        "remaining": round(kr.remaining, 2)
                    }
                    for kr in goal.key_results
                ]
            })

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "goal_count": len(results),
            "goals": results
        }

    def save(self, filename: str) -> None:
        # JSON output contains only explicitly selected reporting fields.
        Path(filename).write_text(
            json.dumps(self.report(), indent=2),
            encoding="utf-8"
        )


def demonstrate() -> None:
    manager = ProductGoalManager()

    strategic = ProductGoal(
        id="STR-001",
        title="Improve digital product experience",
        description="Increase product value through better usability.",
        goal_type=GoalType.STRATEGIC,
        owner="Product Director",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31)
    )

    manager.add_goal(strategic)
    strategic.activate()

    okr = ProductGoal(
        id="OKR-001",
        title="Improve customer retention",
        description="Reduce customer churn and improve retention.",
        goal_type=GoalType.OKR,
        owner="Product Manager",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        parent_id="STR-001",
        key_results=[
            KeyResult(
                id="KR-001",
                title="Increase monthly retention",
                baseline=70,
                target=85,
                direction=Direction.INCREASE,
                unit="percent",
                weight=2
            ),
            KeyResult(
                id="KR-002",
                title="Reduce monthly churn",
                baseline=8,
                target=4,
                direction=Direction.DECREASE,
                unit="percent",
                weight=1
            )
        ]
    )

    manager.add_goal(okr)
    okr.activate()

    manager.record_measurement(
        "OKR-001",
        "KR-001",
        Measurement(
            value=80,
            recorded_at="2026-11-01T10:00:00+00:00",
            source="Customer analytics",
            confidence=0.95
        )
    )

    manager.record_measurement(
        "OKR-001",
        "KR-002",
        Measurement(
            value=5,
            recorded_at="2026-11-01T10:00:00+00:00",
            source="Subscription analytics",
            confidence=0.98
        )
    )

    manager.evaluate_all(date(2026, 11, 4))

    report = manager.report()

    print("PRODUCT GOAL PERFORMANCE REPORT")
    print(json.dumps(report, indent=2))

    print("\nSTRATEGIC ALIGNMENT")
    for child in manager.strategic_alignment("STR-001"):
        print(f"{child.id}: {child.title}")

    # Verify progress calculations.
    assert round(
        manager.goals["OKR-001"].key_results[0].progress, 2
    ) == 66.67

    assert manager.goals["OKR-001"].status == GoalStatus.ACTIVE

    # Verify invalid measurements are rejected.
    try:
        Measurement(
            value=float("nan"),
            recorded_at="2026-11-04T10:00:00+00:00",
            source="Invalid source"
        )
    except ValidationError:
        print("\nInvalid measurement correctly rejected.")

    manager.save("product_goals_report.json")
    print("\nReport saved to product_goals_report.json")


if __name__ == "__main__":
    demonstrate()
