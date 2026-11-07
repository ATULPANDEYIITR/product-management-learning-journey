#!/usr/bin/env python3
"""
ROADMAP TYPES
Feature Roadmap, Outcome Roadmap, Theme Roadmap, Now-Next-Later Roadmap.

A self-contained roadmap management system supporting:
- Multiple roadmap models.
- Feature prioritization and delivery tracking.
- Outcome-based planning and metric evaluation.
- Strategic theme alignment.
- Now-Next-Later planning.
- Dependency validation and cycle detection.
- Ownership, risk, status, and progress tracking.
- Roadmap comparison and reporting.
- JSON persistence and automated tests.

Python 3.10+
"""

from __future__ import annotations

import json
import logging
import uuid

from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("roadmap")


class RoadmapError(Exception):
    """Base exception for roadmap operations."""


class ValidationError(RoadmapError):
    pass


class DependencyError(RoadmapError):
    pass


class RoadmapType(str, Enum):
    FEATURE = "feature"
    OUTCOME = "outcome"
    THEME = "theme"
    NOW_NEXT_LATER = "now_next_later"


class ItemStatus(str, Enum):
    PROPOSED = "proposed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Horizon(str, Enum):
    NOW = "now"
    NEXT = "next"
    LATER = "later"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Metric:
    name: str
    baseline: float
    target: float
    current: float
    unit: str = ""

    def __post_init__(self):
        if not self.name.strip():
            raise ValidationError("Metric name cannot be empty.")

        if self.target < 0 or self.baseline < 0:
            raise ValidationError("Metric values cannot be negative.")

    @property
    def progress(self) -> float:
        difference = self.target - self.baseline

        if difference == 0:
            return 100.0 if self.current == self.target else 0.0

        value = (
            (self.current - self.baseline) / difference
        ) * 100

        return round(max(0.0, min(100.0, value)), 2)


@dataclass
class RoadmapItem:
    title: str
    description: str
    owner: str
    roadmap_type: RoadmapType
    priority: Priority = Priority.MEDIUM
    status: ItemStatus = ItemStatus.PROPOSED
    item_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    horizon: Optional[Horizon] = None
    theme_id: Optional[str] = None
    metric: Optional[Metric] = None
    dependencies: set[str] = field(default_factory=set)
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    confidence: float = 0.8
    progress: float = 0.0
    tags: set[str] = field(default_factory=set)

    def validate(self):
        if not self.title.strip():
            raise ValidationError("Item title cannot be empty.")

        if not self.owner.strip():
            raise ValidationError("Item owner is required.")

        if not 0 <= self.progress <= 100:
            raise ValidationError("Progress must be between 0 and 100.")

        if not 0 <= self.confidence <= 1:
            raise ValidationError("Confidence must be between 0 and 1.")

        if self.start_date and self.target_date:
            if self.start_date > self.target_date:
                raise ValidationError(
                    "Start date cannot exceed target date."
                )

        if (
            self.roadmap_type == RoadmapType.NOW_NEXT_LATER
            and self.horizon is None
        ):
            raise ValidationError(
                "Now-Next-Later items require a horizon."
            )

        if (
            self.roadmap_type == RoadmapType.OUTCOME
            and self.metric is None
        ):
            raise ValidationError(
                "Outcome roadmap items require a metric."
            )


@dataclass
class Theme:
    name: str
    strategic_objective: str
    theme_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    owner: str = ""
    items: set[str] = field(default_factory=set)


class Roadmap:
    def __init__(
        self,
        name: str,
        roadmap_type: RoadmapType
    ):
        if not name.strip():
            raise ValidationError("Roadmap name is required.")

        self.name = name
        self.roadmap_type = roadmap_type
        self.items: dict[str, RoadmapItem] = {}
        self.themes: dict[str, Theme] = {}
        self.created_at = datetime.now().isoformat()

    def add_theme(self, theme: Theme):
        if theme.theme_id in self.themes:
            raise ValidationError("Duplicate theme identifier.")

        self.themes[theme.theme_id] = theme

    def add_item(self, item: RoadmapItem):
        item.validate()

        if item.roadmap_type != self.roadmap_type:
            raise ValidationError(
                "Item roadmap type does not match roadmap."
            )

        if item.item_id in self.items:
            raise ValidationError("Duplicate roadmap item.")

        if item.item_id in item.dependencies:
            raise DependencyError("An item cannot depend on itself.")

        if item.theme_id:
            if item.theme_id not in self.themes:
                raise ValidationError("Unknown theme identifier.")

            self.themes[item.theme_id].items.add(item.item_id)

        self.items[item.item_id] = item

        try:
            self.validate_dependencies()
        except Exception:
            del self.items[item.item_id]

            if item.theme_id:
                self.themes[item.theme_id].items.discard(
                    item.item_id
                )

            raise

    def validate_dependencies(self):
        graph = defaultdict(list)

        for item in self.items.values():
            for dependency in item.dependencies:
                if dependency not in self.items:
                    raise DependencyError(
                        f"Unknown dependency: {dependency}"
                    )

                graph[item.item_id].append(dependency)

        # Three-color DFS detects dependency cycles in O(V + E).
        state = {}

        def visit(node):
            if state.get(node) == 1:
                raise DependencyError(
                    "Circular roadmap dependency detected."
                )

            if state.get(node) == 2:
                return

            state[node] = 1

            for neighbor in graph[node]:
                visit(neighbor)

            state[node] = 2

        for item_id in self.items:
            visit(item_id)

    def update_status(
        self,
        item_id: str,
        status: ItemStatus
    ):
        item = self.get_item(item_id)

        if item.status in {
            ItemStatus.COMPLETED,
            ItemStatus.CANCELLED
        }:
            raise ValidationError(
                "Terminal items cannot be reopened through this operation."
            )

        if status == ItemStatus.IN_PROGRESS:
            for dependency in item.dependencies:
                if self.items[dependency].status != ItemStatus.COMPLETED:
                    raise DependencyError(
                        "All dependencies must be completed first."
                    )

        item.status = status

        if status == ItemStatus.COMPLETED:
            item.progress = 100.0

        logger.info(
            "Updated %s to %s",
            item.title,
            status.value
        )

    def update_progress(self, item_id: str, progress: float):
        item = self.get_item(item_id)

        if item.status in {
            ItemStatus.COMPLETED,
            ItemStatus.CANCELLED
        }:
            raise ValidationError(
                "Cannot update progress of a terminal item."
            )

        if not 0 <= progress <= 100:
            raise ValidationError("Invalid progress value.")

        item.progress = progress

    def update_metric(self, item_id: str, current: float):
        item = self.get_item(item_id)

        if item.metric is None:
            raise ValidationError("Item has no outcome metric.")

        if current < 0:
            raise ValidationError("Metric cannot be negative.")

        item.metric.current = current

    def get_item(self, item_id: str) -> RoadmapItem:
        try:
            return self.items[item_id]
        except KeyError:
            raise ValidationError(
                f"Roadmap item not found: {item_id}"
            )

    def prioritized_items(self):
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }

        return sorted(
            self.items.values(),
            key=lambda item: (
                priority_order[item.priority],
                -item.confidence,
                item.target_date or date.max
            )
        )

    def outcome_report(self):
        report = []

        for item in self.items.values():
            if item.metric:
                report.append({
                    "item": item.title,
                    "metric": item.metric.name,
                    "baseline": item.metric.baseline,
                    "target": item.metric.target,
                    "current": item.metric.current,
                    "progress": item.metric.progress
                })

        return report

    def horizon_report(self):
        report = {
            Horizon.NOW.value: [],
            Horizon.NEXT.value: [],
            Horizon.LATER.value: []
        }

        for item in self.items.values():
            if item.horizon:
                report[item.horizon.value].append(item.title)

        return report

    def summary(self):
        counts = defaultdict(int)

        for item in self.items.values():
            counts[item.status.value] += 1

        total = len(self.items)

        completed = counts[ItemStatus.COMPLETED.value]

        return {
            "roadmap": self.name,
            "type": self.roadmap_type.value,
            "total_items": total,
            "completed": completed,
            "completion_percentage": round(
                completed / total * 100, 2
            ) if total else 0,
            "status_counts": dict(counts)
        }

    def export_json(self, filepath: str):
        data = {
            "name": self.name,
            "type": self.roadmap_type.value,
            "created_at": self.created_at,
            "themes": [
                {
                    "theme_id": theme.theme_id,
                    "name": theme.name,
                    "objective": theme.strategic_objective,
                    "owner": theme.owner,
                    "items": sorted(theme.items)
                }
                for theme in self.themes.values()
            ],
            "items": [
                self._serialize_item(item)
                for item in self.items.values()
            ]
        }

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        temporary = path.with_suffix(path.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8"
            )
            temporary.replace(path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    @staticmethod
    def _serialize_item(item):
        data = asdict(item)

        data["roadmap_type"] = item.roadmap_type.value
        data["priority"] = item.priority.value
        data["status"] = item.status.value
        data["horizon"] = (
            item.horizon.value if item.horizon else None
        )
        data["start_date"] = (
            item.start_date.isoformat()
            if item.start_date else None
        )
        data["target_date"] = (
            item.target_date.isoformat()
            if item.target_date else None
        )
        data["dependencies"] = sorted(item.dependencies)
        data["tags"] = sorted(item.tags)

        return data


def demonstrate_feature_roadmap():
    roadmap = Roadmap(
        "Customer Platform Delivery",
        RoadmapType.FEATURE
    )

    authentication = RoadmapItem(
        title="Multi-factor authentication",
        description="Introduce secure second-factor login.",
        owner="Security Team",
        roadmap_type=RoadmapType.FEATURE,
        priority=Priority.CRITICAL,
        status=ItemStatus.PLANNED
    )

    dashboard = RoadmapItem(
        title="Customer analytics dashboard",
        description="Provide customer usage analytics.",
        owner="Product Team",
        roadmap_type=RoadmapType.FEATURE,
        priority=Priority.HIGH,
        dependencies={authentication.item_id}
    )

    roadmap.add_item(authentication)
    roadmap.add_item(dashboard)

    roadmap.update_status(
        authentication.item_id,
        ItemStatus.IN_PROGRESS
    )

    authentication.progress = 60

    roadmap.update_status(
        authentication.item_id,
        ItemStatus.COMPLETED
    )

    roadmap.update_status(
        dashboard.item_id,
        ItemStatus.IN_PROGRESS
    )

    return roadmap


def demonstrate_outcome_roadmap():
    roadmap = Roadmap(
        "Customer Experience Outcomes",
        RoadmapType.OUTCOME
    )

    item = RoadmapItem(
        title="Reduce customer onboarding time",
        description="Simplify onboarding processes.",
        owner="Product Operations",
        roadmap_type=RoadmapType.OUTCOME,
        priority=Priority.HIGH,
        metric=Metric(
            name="Average onboarding time",
            baseline=10,
            target=4,
            current=7,
            unit="days"
        )
    )

    roadmap.add_item(item)
    roadmap.update_metric(item.item_id, 5)

    return roadmap


def demonstrate_theme_roadmap():
    roadmap = Roadmap(
        "Annual Strategic Themes",
        RoadmapType.THEME
    )

    theme = Theme(
        name="Trust and Security",
        strategic_objective="Improve platform security.",
        owner="Chief Technology Office"
    )

    roadmap.add_theme(theme)

    item = RoadmapItem(
        title="Centralized audit logging",
        description="Create unified audit visibility.",
        owner="Platform Engineering",
        roadmap_type=RoadmapType.THEME,
        theme_id=theme.theme_id,
        priority=Priority.HIGH
    )

    roadmap.add_item(item)

    return roadmap


def demonstrate_now_next_later():
    roadmap = Roadmap(
        "Product Investment Horizons",
        RoadmapType.NOW_NEXT_LATER
    )

    examples = [
        ("Fix payment failures", Horizon.NOW, Priority.CRITICAL),
        ("Improve reporting", Horizon.NEXT, Priority.HIGH),
        ("Introduce predictive analytics", Horizon.LATER, Priority.MEDIUM)
    ]

    for title, horizon, priority in examples:
        roadmap.add_item(
            RoadmapItem(
                title=title,
                description=f"Planning item: {title}",
                owner="Product Team",
                roadmap_type=RoadmapType.NOW_NEXT_LATER,
                horizon=horizon,
                priority=priority
            )
        )

    return roadmap


def run_tests():
    roadmap = demonstrate_feature_roadmap()

    assert len(roadmap.items) == 2

    assert roadmap.summary()["completed"] == 1

    outcome = demonstrate_outcome_roadmap()

    assert outcome.outcome_report()[0]["current"] == 5

    themes = demonstrate_theme_roadmap()

    assert len(themes.themes) == 1

    horizons = demonstrate_now_next_later()

    assert len(horizons.horizon_report()["now"]) == 1

    # A missing dependency must be rejected.
    invalid = Roadmap("Invalid", RoadmapType.FEATURE)

    item = RoadmapItem(
        title="Invalid dependency",
        description="Validation test",
        owner="Engineering",
        roadmap_type=RoadmapType.FEATURE,
        dependencies={"missing-item"}
    )

    try:
        invalid.add_item(item)
        raise AssertionError("Missing dependency was accepted.")
    except DependencyError:
        pass

    # Circular dependencies must be rejected.
    cyclic = Roadmap("Cycle Test", RoadmapType.FEATURE)

    first = RoadmapItem(
        title="First",
        description="First dependency",
        owner="Engineering",
        roadmap_type=RoadmapType.FEATURE
    )

    second = RoadmapItem(
        title="Second",
        description="Second dependency",
        owner="Engineering",
        roadmap_type=RoadmapType.FEATURE,
        dependencies={first.item_id}
    )

    cyclic.add_item(first)
    cyclic.add_item(second)

    first.dependencies.add(second.item_id)

    try:
        cyclic.validate_dependencies()
        raise AssertionError("Circular dependency was accepted.")
    except DependencyError:
        pass

    print("All roadmap tests passed.")


def main():
    feature = demonstrate_feature_roadmap()
    outcome = demonstrate_outcome_roadmap()
    theme = demonstrate_theme_roadmap()
    horizon = demonstrate_now_next_later()

    print("\nFEATURE ROADMAP")
    print(json.dumps(feature.summary(), indent=2))

    print("\nOUTCOME ROADMAP")
    print(json.dumps(outcome.outcome_report(), indent=2))

    print("\nTHEME ROADMAP")
    print(json.dumps(theme.summary(), indent=2))

    print("\nNOW-NEXT-LATER ROADMAP")
    print(json.dumps(horizon.horizon_report(), indent=2))

    feature.export_json("roadmaps/feature_roadmap.json")

    run_tests()


if __name__ == "__main__":
    main()
