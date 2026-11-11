#!/usr/bin/env python3
"""
MoSCoW Prioritization Framework
A complete requirements prioritization and decision-management system.

Categories:
    MUST_HAVE   - Essential requirements.
    SHOULD_HAVE - Important requirements that can tolerate limited delay.
    COULD_HAVE  - Desirable requirements with lower business impact.
    WONT_HAVE   - Explicitly excluded from the current delivery scope.

Features:
    - Requirement registration and validation.
    - Priority classification.
    - Business-value and effort assessment.
    - Capacity-aware prioritization.
    - Scope management and reporting.
    - Priority-change history.
    - JSON persistence.
    - Dependency validation.
    - Automated tests.
"""

from __future__ import annotations

import json
import logging
import argparse
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("moscow")


class Priority(str, Enum):
    MUST_HAVE = "Must-have"
    SHOULD_HAVE = "Should-have"
    COULD_HAVE = "Could-have"
    WONT_HAVE = "Won't-have"


class RequirementStatus(str, Enum):
    PROPOSED = "Proposed"
    APPROVED = "Approved"
    IN_PROGRESS = "In progress"
    COMPLETED = "Completed"
    DEFERRED = "Deferred"


class PrioritizationError(Exception):
    """Base exception for prioritization failures."""


class RequirementNotFoundError(PrioritizationError):
    pass


class CapacityExceededError(PrioritizationError):
    pass


@dataclass
class Requirement:
    requirement_id: str
    title: str
    description: str
    priority: Priority
    business_value: int
    effort: int
    owner: str
    dependencies: list[str] = field(default_factory=list)
    status: RequirementStatus = RequirementStatus.PROPOSED
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self):
        self.requirement_id = self.requirement_id.strip()
        self.title = self.title.strip()
        self.description = self.description.strip()
        self.owner = self.owner.strip()

        if not self.requirement_id:
            raise ValueError("Requirement ID cannot be empty.")

        if not self.title:
            raise ValueError("Requirement title cannot be empty.")

        if not self.owner:
            raise ValueError("Requirement owner cannot be empty.")

        if not 1 <= self.business_value <= 10:
            raise ValueError("Business value must be between 1 and 10.")

        if not 1 <= self.effort <= 100:
            raise ValueError("Effort must be between 1 and 100.")

        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("Duplicate dependencies are not allowed.")

    @property
    def value_effort_ratio(self) -> float:
        return round(self.business_value / self.effort, 3)


@dataclass
class PriorityChange:
    requirement_id: str
    old_priority: str
    new_priority: str
    changed_by: str
    reason: str
    changed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class MoSCoWManager:

    def __init__(self):
        self.requirements: dict[str, Requirement] = {}
        self.history: list[PriorityChange] = []

    def add_requirement(self, requirement: Requirement):
        if requirement.requirement_id in self.requirements:
            raise ValueError("Requirement ID already exists.")

        for dependency in requirement.dependencies:
            if dependency == requirement.requirement_id:
                raise ValueError("A requirement cannot depend on itself.")

        self.requirements[requirement.requirement_id] = requirement
        self._validate_dependency_graph()

        logger.info("Added requirement %s", requirement.requirement_id)

    def get_requirement(self, requirement_id: str) -> Requirement:
        try:
            return self.requirements[requirement_id]
        except KeyError:
            raise RequirementNotFoundError(
                f"Requirement {requirement_id} does not exist."
            )

    def update_priority(
        self,
        requirement_id: str,
        new_priority: Priority,
        changed_by: str,
        reason: str
    ):
        requirement = self.get_requirement(requirement_id)

        if not changed_by.strip() or not reason.strip():
            raise ValueError("Change owner and reason are required.")

        old_priority = requirement.priority

        if old_priority == new_priority:
            return

        requirement.priority = new_priority

        self.history.append(
            PriorityChange(
                requirement_id=requirement_id,
                old_priority=old_priority.value,
                new_priority=new_priority.value,
                changed_by=changed_by,
                reason=reason
            )
        )

        logger.info(
            "Priority changed: %s: %s -> %s",
            requirement_id,
            old_priority.value,
            new_priority.value
        )

    def update_status(
        self,
        requirement_id: str,
        status: RequirementStatus
    ):
        requirement = self.get_requirement(requirement_id)

        if (
            requirement.priority == Priority.WONT_HAVE
            and status in {
                RequirementStatus.IN_PROGRESS,
                RequirementStatus.COMPLETED
            }
        ):
            raise PrioritizationError(
                "Won't-have requirements cannot enter delivery."
            )

        requirement.status = status

    def _validate_dependency_graph(self):
        """Validate dependency existence and detect cycles."""

        for requirement in self.requirements.values():
            for dependency in requirement.dependencies:
                if dependency not in self.requirements:
                    raise ValueError(
                        f"Unknown dependency: {dependency}"
                    )

        visited = set()
        active = set()

        def visit(requirement_id):
            if requirement_id in active:
                raise ValueError("Circular dependency detected.")

            if requirement_id in visited:
                return

            active.add(requirement_id)

            for dependency in self.get_requirement(
                requirement_id
            ).dependencies:
                visit(dependency)

            active.remove(requirement_id)
            visited.add(requirement_id)

        for requirement_id in self.requirements:
            visit(requirement_id)

    def evaluate_dependencies(self, requirement_id: str) -> bool:
        requirement = self.get_requirement(requirement_id)

        return all(
            self.get_requirement(dependency).status
            == RequirementStatus.COMPLETED
            for dependency in requirement.dependencies
        )

    def plan_release(self, capacity: int) -> list[Requirement]:
        """
        Select requirements within effort capacity.

        Must-have requirements are considered first.
        Should-have and Could-have requirements are ranked
        by business value per effort unit.
        """

        if capacity < 0:
            raise ValueError("Capacity cannot be negative.")

        eligible = [
            requirement
            for requirement in self.requirements.values()
            if requirement.priority != Priority.WONT_HAVE
            and requirement.status != RequirementStatus.COMPLETED
        ]

        selected = []
        remaining = capacity
        selected_ids = set()

        mandatory = sorted(
            (
                r for r in eligible
                if r.priority == Priority.MUST_HAVE
            ),
            key=lambda r: r.requirement_id
        )

        optional = sorted(
            (
                r for r in eligible
                if r.priority != Priority.MUST_HAVE
            ),
            key=lambda r: (
                -r.value_effort_ratio,
                r.requirement_id
            )
        )

        for requirement in mandatory + optional:
            dependencies_ready = all(
                dependency in selected_ids
                or self.get_requirement(dependency).status
                == RequirementStatus.COMPLETED
                for dependency in requirement.dependencies
            )

            if dependencies_ready and requirement.effort <= remaining:
                selected.append(requirement)
                selected_ids.add(requirement.requirement_id)
                remaining -= requirement.effort

        mandatory_total = sum(r.effort for r in mandatory)

        if mandatory_total > capacity:
            logger.warning(
                "Mandatory requirements exceed capacity by %d units.",
                mandatory_total - capacity
            )

        return selected

    def report(self) -> dict:
        summary = {}

        for priority in Priority:
            items = [
                r for r in self.requirements.values()
                if r.priority == priority
            ]

            summary[priority.value] = {
                "count": len(items),
                "total_effort": sum(r.effort for r in items),
                "average_business_value": round(
                    sum(r.business_value for r in items) / len(items),
                    2
                ) if items else 0
            }

        return {
            "total_requirements": len(self.requirements),
            "categories": summary,
            "completed": sum(
                r.status == RequirementStatus.COMPLETED
                for r in self.requirements.values()
            ),
            "priority_changes": len(self.history)
        }

    def save(self, filepath: str):
        data = {
            "requirements": [
                {
                    **asdict(r),
                    "priority": r.priority.value,
                    "status": r.status.value
                }
                for r in self.requirements.values()
            ],
            "history": [
                asdict(change) for change in self.history
            ]
        }

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
        temporary.replace(path)

    @classmethod
    def load(cls, filepath: str):
        data = json.loads(
            Path(filepath).read_text(encoding="utf-8")
        )

        manager = cls()

        for item in data.get("requirements", []):
            item["priority"] = Priority(item["priority"])
            item["status"] = RequirementStatus(item["status"])
            manager.add_requirement(Requirement(**item))

        manager.history = [
            PriorityChange(**item)
            for item in data.get("history", [])
        ]

        return manager


def build_demo() -> MoSCoWManager:
    manager = MoSCoWManager()

    requirements = [
        Requirement(
            "R001",
            "User Authentication",
            "Secure login and session management.",
            Priority.MUST_HAVE,
            10,
            8,
            "Security Team"
        ),
        Requirement(
            "R002",
            "Payment Processing",
            "Process customer payments securely.",
            Priority.MUST_HAVE,
            10,
            13,
            "Payments Team",
            ["R001"]
        ),
        Requirement(
            "R003",
            "Audit Logging",
            "Maintain security and operational audit records.",
            Priority.MUST_HAVE,
            9,
            5,
            "Platform Team"
        ),
        Requirement(
            "R004",
            "Advanced Analytics",
            "Provide detailed business dashboards.",
            Priority.SHOULD_HAVE,
            8,
            8,
            "Analytics Team"
        ),
        Requirement(
            "R005",
            "Email Notifications",
            "Send transactional email notifications.",
            Priority.SHOULD_HAVE,
            7,
            5,
            "Communications Team"
        ),
        Requirement(
            "R006",
            "Custom Themes",
            "Allow users to customize application themes.",
            Priority.COULD_HAVE,
            4,
            3,
            "Frontend Team"
        ),
        Requirement(
            "R007",
            "Animated Backgrounds",
            "Provide decorative animated backgrounds.",
            Priority.WONT_HAVE,
            2,
            5,
            "Frontend Team"
        )
    ]

    for requirement in requirements:
        manager.add_requirement(requirement)

    return manager


def run_tests():
    manager = build_demo()

    assert len(manager.requirements) == 7

    assert manager.evaluate_dependencies("R002") is False

    manager.update_status("R001", RequirementStatus.COMPLETED)

    assert manager.evaluate_dependencies("R002") is True

    manager.update_priority(
        "R006",
        Priority.SHOULD_HAVE,
        "Product Owner",
        "Increased customer demand."
    )

    assert len(manager.history) == 1

    try:
        manager.update_status(
            "R007",
            RequirementStatus.IN_PROGRESS
        )
        raise AssertionError("Expected validation failure.")
    except PrioritizationError:
        pass

    try:
        manager.add_requirement(
            Requirement(
                "R008",
                "Circular Dependency",
                "Invalid dependency example.",
                Priority.COULD_HAVE,
                5,
                3,
                "Developer",
                ["R008"]
            )
        )
        raise AssertionError("Expected circular dependency failure.")
    except ValueError:
        manager.requirements.pop("R008", None)

    assert manager.report()["total_requirements"] == 7

    print("All tests passed.")


def main():
    parser = argparse.ArgumentParser(
        description="MoSCoW Requirements Prioritization"
    )

    parser.add_argument(
        "--capacity",
        type=int,
        default=30
    )

    parser.add_argument(
        "--save",
        default="moscow_data.json"
    )

    args = parser.parse_args()

    if args.capacity < 0:
        parser.error("Capacity cannot be negative.")

    manager = build_demo()

    print("\nMoSCoW REQUIREMENTS REPORT")
    print("=" * 55)

    print(json.dumps(manager.report(), indent=2))

    print("\nRELEASE PLAN")
    print("=" * 55)

    for requirement in manager.plan_release(args.capacity):
        print(
            f"{requirement.requirement_id}: "
            f"{requirement.title} | "
            f"{requirement.priority.value} | "
            f"Effort: {requirement.effort}"
        )

    manager.save(args.save)
    print(f"\nData saved to {args.save}")

    run_tests()


if __name__ == "__main__":
    main()
