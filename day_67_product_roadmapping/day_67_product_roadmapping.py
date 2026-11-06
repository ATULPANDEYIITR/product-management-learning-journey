#!/usr/bin/env python3
"""
Product Roadmapping
Demonstrates themes, outcomes, initiatives, prioritization, timelines,
dependencies, capacity planning, roadmap validation, and scenario analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class InitiativeStatus(Enum):
    PROPOSED = "proposed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class RoadmapError(Exception):
    pass


@dataclass
class Outcome:
    id: str
    description: str
    baseline: float
    target: float
    unit: str
    current: float

    def progress(self) -> float:
        if self.target == self.baseline:
            return 100.0 if self.current == self.target else 0.0

        progress = (
            (self.current - self.baseline)
            / (self.target - self.baseline)
        ) * 100

        return max(0.0, min(100.0, progress))

    def achieved(self) -> bool:
        if self.target >= self.baseline:
            return self.current >= self.target
        return self.current <= self.target


@dataclass
class Theme:
    id: str
    name: str
    strategic_goal: str


@dataclass
class Initiative:
    id: str
    name: str
    theme_id: str
    outcome_id: str
    start: date
    end: date
    effort: int
    impact: float
    confidence: float
    strategic_alignment: float
    dependencies: list[str] = field(default_factory=list)
    status: InitiativeStatus = InitiativeStatus.PROPOSED
    owner: str = "Product Team"

    def __post_init__(self):
        if self.end < self.start:
            raise RoadmapError("End date cannot precede start date.")

        if self.effort <= 0:
            raise RoadmapError("Effort must be positive.")

        for value in (
            self.impact,
            self.confidence,
            self.strategic_alignment,
        ):
            if not 0 <= value <= 10:
                raise RoadmapError("Scoring values must be between 0 and 10.")

    def duration_days(self) -> int:
        return (self.end - self.start).days + 1

    def rice_score(self) -> float:
        # Simplified RICE-style prioritization.
        return (
            self.impact
            * self.confidence
            * self.strategic_alignment
            / self.effort
        )


class ProductRoadmap:
    def __init__(
        self,
        product_name: str,
        planning_start: date,
        planning_end: date,
        capacity_per_sprint: int = 40,
    ):
        if planning_end < planning_start:
            raise RoadmapError("Invalid planning period.")

        if capacity_per_sprint <= 0:
            raise RoadmapError("Capacity must be positive.")

        self.product_name = product_name
        self.planning_start = planning_start
        self.planning_end = planning_end
        self.capacity_per_sprint = capacity_per_sprint

        self.themes: dict[str, Theme] = {}
        self.outcomes: dict[str, Outcome] = {}
        self.initiatives: dict[str, Initiative] = {}

    def add_theme(self, theme: Theme):
        if theme.id in self.themes:
            raise RoadmapError("Duplicate theme ID.")

        self.themes[theme.id] = theme

    def add_outcome(self, outcome: Outcome):
        if outcome.id in self.outcomes:
            raise RoadmapError("Duplicate outcome ID.")

        self.outcomes[outcome.id] = outcome

    def add_initiative(self, initiative: Initiative):
        if initiative.id in self.initiatives:
            raise RoadmapError("Duplicate initiative ID.")

        if initiative.theme_id not in self.themes:
            raise RoadmapError("Unknown strategic theme.")

        if initiative.outcome_id not in self.outcomes:
            raise RoadmapError("Unknown outcome.")

        if (
            initiative.start < self.planning_start
            or initiative.end > self.planning_end
        ):
            raise RoadmapError("Initiative outside planning period.")

        if initiative.id in initiative.dependencies:
            raise RoadmapError("An initiative cannot depend on itself.")

        self.initiatives[initiative.id] = initiative

    def validate_dependencies(self):
        """Validate references and detect dependency cycles."""

        for initiative in self.initiatives.values():
            for dependency in initiative.dependencies:
                if dependency not in self.initiatives:
                    raise RoadmapError(
                        f"Unknown dependency {dependency} "
                        f"for {initiative.id}."
                    )

        visiting = set()
        visited = set()

        def visit(initiative_id):
            if initiative_id in visiting:
                raise RoadmapError("Dependency cycle detected.")

            if initiative_id in visited:
                return

            visiting.add(initiative_id)

            for dependency in self.initiatives[
                initiative_id
            ].dependencies:
                visit(dependency)

            visiting.remove(initiative_id)
            visited.add(initiative_id)

        for initiative_id in self.initiatives:
            visit(initiative_id)

    def validate_timeline(self):
        self.validate_dependencies()

        for initiative in self.initiatives.values():
            for dependency_id in initiative.dependencies:
                dependency = self.initiatives[dependency_id]

                if dependency.end >= initiative.start:
                    raise RoadmapError(
                        f"{initiative.id} must start after "
                        f"{dependency.id} finishes."
                    )

    def prioritize(self):
        return sorted(
            self.initiatives.values(),
            key=lambda item: item.rice_score(),
            reverse=True,
        )

    def ready_initiatives(self):
        """Return initiatives whose dependencies are completed."""

        return [
            item
            for item in self.initiatives.values()
            if item.status == InitiativeStatus.PLANNED
            and all(
                self.initiatives[dependency].status
                == InitiativeStatus.COMPLETED
                for dependency in item.dependencies
            )
        ]

    def sprint_capacity_report(self):
        """Calculate effort assigned to each 14-day sprint."""

        report = {}
        sprint_start = self.planning_start
        sprint_number = 1

        while sprint_start <= self.planning_end:
            sprint_end = min(
                sprint_start + timedelta(days=13),
                self.planning_end,
            )

            assigned = sum(
                initiative.effort
                for initiative in self.initiatives.values()
                if initiative.status != InitiativeStatus.PROPOSED
                and initiative.start <= sprint_end
                and initiative.end >= sprint_start
            )

            report[sprint_number] = {
                "start": sprint_start,
                "end": sprint_end,
                "assigned_effort": assigned,
                "capacity": self.capacity_per_sprint,
                "available": max(
                    0,
                    self.capacity_per_sprint - assigned,
                ),
                "overloaded": assigned > self.capacity_per_sprint,
            }

            sprint_start += timedelta(days=14)
            sprint_number += 1

        return report

    def outcome_report(self):
        return [
            {
                "id": outcome.id,
                "description": outcome.description,
                "baseline": outcome.baseline,
                "current": outcome.current,
                "target": outcome.target,
                "progress_percent": round(
                    outcome.progress(), 2
                ),
                "achieved": outcome.achieved(),
            }
            for outcome in self.outcomes.values()
        ]

    def change_status(
        self,
        initiative_id: str,
        new_status: InitiativeStatus,
    ):
        if initiative_id not in self.initiatives:
            raise RoadmapError("Unknown initiative.")

        initiative = self.initiatives[initiative_id]

        if new_status == InitiativeStatus.IN_PROGRESS:
            unfinished = [
                dependency
                for dependency in initiative.dependencies
                if self.initiatives[dependency].status
                != InitiativeStatus.COMPLETED
            ]

            if unfinished:
                raise RoadmapError(
                    f"Unfinished dependencies: {unfinished}"
                )

        initiative.status = new_status

    def generate_report(self):
        print(f"\nPRODUCT ROADMAP: {self.product_name}")
        print("=" * 72)
        print(
            f"Planning period: {self.planning_start} "
            f"to {self.planning_end}"
        )

        print("\nSTRATEGIC THEMES")

        for theme in self.themes.values():
            print(f"\n{theme.name}: {theme.strategic_goal}")

        print("\nPRIORITIZED INITIATIVES")

        for initiative in self.prioritize():
            print(
                f"{initiative.id} | {initiative.name} | "
                f"Score: {initiative.rice_score():.2f} | "
                f"{initiative.start} to {initiative.end} | "
                f"Effort: {initiative.effort} | "
                f"Status: {initiative.status.value}"
            )

            if initiative.dependencies:
                print(
                    f"  Dependencies: "
                    f"{', '.join(initiative.dependencies)}"
                )

        print("\nOUTCOME PERFORMANCE")

        for outcome in self.outcome_report():
            print(
                f"{outcome['id']} | "
                f"{outcome['description']} | "
                f"Progress: {outcome['progress_percent']}% | "
                f"Achieved: {outcome['achieved']}"
            )

        print("\nSPRINT CAPACITY")

        for number, sprint in self.sprint_capacity_report().items():
            print(
                f"Sprint {number}: "
                f"{sprint['assigned_effort']}/"
                f"{sprint['capacity']} effort units | "
                f"Overloaded: {sprint['overloaded']}"
            )


def build_example():
    roadmap = ProductRoadmap(
        product_name="Enterprise Commerce Platform",
        planning_start=date(2027, 1, 1),
        planning_end=date(2027, 3, 31),
        capacity_per_sprint=40,
    )

    roadmap.add_theme(
        Theme(
            "T1",
            "Customer Experience",
            "Improve customer satisfaction and usability.",
        )
    )

    roadmap.add_theme(
        Theme(
            "T2",
            "Platform Reliability",
            "Improve system availability and operational stability.",
        )
    )

    roadmap.add_theme(
        Theme(
            "T3",
            "Revenue Growth",
            "Increase digital conversion and revenue.",
        )
    )

    roadmap.add_outcome(
        Outcome(
            "O1",
            "Checkout completion rate",
            65,
            85,
            "%",
            72,
        )
    )

    roadmap.add_outcome(
        Outcome(
            "O2",
            "Monthly platform availability",
            99.0,
            99.9,
            "%",
            99.5,
        )
    )

    roadmap.add_outcome(
        Outcome(
            "O3",
            "Average checkout processing time",
            8,
            3,
            "seconds",
            5,
        )
    )

    roadmap.add_initiative(
        Initiative(
            "I1",
            "Payment Infrastructure Upgrade",
            "T2",
            "O2",
            date(2027, 1, 1),
            date(2027, 1, 21),
            30,
            9,
            0.9,
            10,
            status=InitiativeStatus.PLANNED,
        )
    )

    roadmap.add_initiative(
        Initiative(
            "I2",
            "Checkout Performance Optimization",
            "T1",
            "O3",
            date(2027, 1, 22),
            date(2027, 2, 12),
            35,
            8,
            0.85,
            9,
            dependencies=["I1"],
            status=InitiativeStatus.PLANNED,
        )
    )

    roadmap.add_initiative(
        Initiative(
            "I3",
            "One-Click Checkout",
            "T1",
            "O1",
            date(2027, 2, 13),
            date(2027, 3, 10),
            45,
            10,
            0.8,
            10,
            dependencies=["I2"],
            status=InitiativeStatus.PLANNED,
        )
    )

    roadmap.add_initiative(
        Initiative(
            "I4",
            "Personalized Product Recommendations",
            "T3",
            "O1",
            date(2027, 1, 15),
            date(2027, 2, 15),
            25,
            8,
            0.75,
            8,
            status=InitiativeStatus.PROPOSED,
        )
    )

    return roadmap


def run_tests():
    roadmap = build_example()
    roadmap.validate_timeline()

    assert len(roadmap.themes) == 3
    assert len(roadmap.outcomes) == 3
    assert len(roadmap.initiatives) == 4

    assert roadmap.outcomes["O1"].progress() == 35.0
    assert roadmap.outcomes["O3"].achieved() is False

    # A dependent initiative cannot begin before its prerequisite finishes.
    try:
        roadmap.change_status("I2", InitiativeStatus.IN_PROGRESS)
        raise AssertionError("Dependency validation failed.")
    except RoadmapError:
        pass

    roadmap.change_status("I1", InitiativeStatus.COMPLETED)
    roadmap.change_status("I2", InitiativeStatus.IN_PROGRESS)

    assert roadmap.initiatives["I2"].status == (
        InitiativeStatus.IN_PROGRESS
    )

    # Detect a dependency cycle.
    roadmap.initiatives["I1"].dependencies.append("I3")

    try:
        roadmap.validate_dependencies()
        raise AssertionError("Cycle detection failed.")
    except RoadmapError:
        pass

    print("All roadmap validation tests passed.")


def main():
    roadmap = build_example()
    roadmap.validate_timeline()
    roadmap.generate_report()

    print("\nREADY INITIATIVES")

    for initiative in roadmap.ready_initiatives():
        print(initiative.name)

    run_tests()


if __name__ == "__main__":
    main()
