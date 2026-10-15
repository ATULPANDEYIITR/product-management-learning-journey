#!/usr/bin/env python3
"""
Epic and Feature Management: A Practical Product Delivery Model

Demonstrates:
- Epic -> Feature -> User Story -> Task hierarchy.
- Parent-child integrity and hierarchy validation.
- Story points, task estimates, ownership, and delivery status.
- Epic progress based on leaf-level work rather than duplicated estimates.
- Dependency validation and blocked work.
- Acceptance criteria, completion rules, and scope changes.
- Release readiness and delivery reporting.

Requires Python 3.10 or later. Uses only the standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Iterable
import json


class WorkType(str, Enum):
    EPIC = "epic"
    FEATURE = "feature"
    STORY = "story"
    TASK = "task"


class Status(str, Enum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


EXPECTED_PARENT = {
    WorkType.EPIC: None,
    WorkType.FEATURE: WorkType.EPIC,
    WorkType.STORY: WorkType.FEATURE,
    WorkType.TASK: WorkType.STORY,
}


class WorkItemError(ValueError):
    """Raised when a work item violates the delivery model."""


@dataclass
class WorkItem:
    item_id: str
    title: str
    work_type: WorkType
    parent_id: str | None = None
    status: Status = Status.BACKLOG
    priority: Priority = Priority.MEDIUM
    owner: str | None = None
    story_points: float | None = None
    estimate_hours: float | None = None
    acceptance_criteria: list[str] = field(default_factory=list)
    due_date: date | None = None
    labels: set[str] = field(default_factory=set)
    dependency_ids: set[str] = field(default_factory=set)
    version: int = 1

    def __post_init__(self) -> None:
        self.item_id = self.item_id.strip()
        self.title = self.title.strip()
        self.labels = {label.strip() for label in self.labels if label.strip()}
        self.acceptance_criteria = [
            criterion.strip()
            for criterion in self.acceptance_criteria
            if criterion.strip()
        ]

        if not self.item_id or not self.title:
            raise WorkItemError("Every work item needs an ID and a title.")

        if self.version < 1:
            raise WorkItemError("Version must be positive.")

        if self.story_points is not None and self.story_points < 0:
            raise WorkItemError("Story points cannot be negative.")

        if self.estimate_hours is not None and self.estimate_hours < 0:
            raise WorkItemError("Estimate hours cannot be negative.")

        if self.work_type != WorkType.STORY and self.story_points is not None:
            raise WorkItemError("Only user stories can carry story points.")

        if self.work_type != WorkType.TASK and self.estimate_hours is not None:
            raise WorkItemError("Only tasks can carry hour estimates.")

        if self.work_type == WorkType.STORY and not self.acceptance_criteria:
            raise WorkItemError(
                "A user story must define at least one acceptance criterion."
            )

        if self.item_id in self.dependency_ids:
            raise WorkItemError("An item cannot depend on itself.")


class WorkTracker:
    """Maintains a validated hierarchy and derives delivery metrics."""

    def __init__(self) -> None:
        self.items: dict[str, WorkItem] = {}

    def add(self, item: WorkItem) -> None:
        if item.item_id in self.items:
            raise WorkItemError(f"Duplicate work item ID: {item.item_id}")

        expected_parent = EXPECTED_PARENT[item.work_type]

        if expected_parent is None:
            if item.parent_id is not None:
                raise WorkItemError("An epic cannot have a parent.")
        else:
            if item.parent_id is None:
                raise WorkItemError(
                    f"{item.work_type.value} requires a "
                    f"{expected_parent.value} parent."
                )

            parent = self.items.get(item.parent_id)
            if parent is None:
                raise WorkItemError(
                    f"Parent {item.parent_id!r} must exist before adding "
                    f"{item.item_id!r}."
                )

            if parent.work_type != expected_parent:
                raise WorkItemError(
                    f"{item.work_type.value} must be directly beneath "
                    f"{expected_parent.value}, not {parent.work_type.value}."
                )

        for dependency_id in item.dependency_ids:
            if dependency_id not in self.items:
                raise WorkItemError(
                    f"Dependency {dependency_id!r} does not exist."
                )

        self.items[item.item_id] = item

        try:
            self._validate_dependency_graph()
        except Exception:
            del self.items[item.item_id]
            raise

    def get(self, item_id: str) -> WorkItem:
        try:
            return self.items[item_id]
        except KeyError as exc:
            raise WorkItemError(f"Unknown work item: {item_id}") from exc

    def children(self, parent_id: str) -> list[WorkItem]:
        return sorted(
            (
                item
                for item in self.items.values()
                if item.parent_id == parent_id
            ),
            key=lambda item: item.item_id,
        )

    def descendants(self, item_id: str) -> list[WorkItem]:
        result: list[WorkItem] = []
        stack = list(reversed(self.children(item_id)))

        while stack:
            item = stack.pop()
            result.append(item)
            stack.extend(reversed(self.children(item.item_id)))

        return result

    def _validate_dependency_graph(self) -> None:
        """Reject cycles so dependency ordering remains meaningful."""
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(item_id: str) -> None:
            if item_id in visiting:
                raise WorkItemError(
                    f"Dependency cycle detected at {item_id}."
                )

            if item_id in visited:
                return

            visiting.add(item_id)

            for dependency_id in self.get(item_id).dependency_ids:
                visit(dependency_id)

            visiting.remove(item_id)
            visited.add(item_id)

        for item_id in self.items:
            visit(item_id)

    def unmet_dependencies(self, item_id: str) -> list[str]:
        item = self.get(item_id)
        return sorted(
            dependency_id
            for dependency_id in item.dependency_ids
            if self.get(dependency_id).status != Status.DONE
        )

    def transition(self, item_id: str, new_status: Status) -> None:
        item = self.get(item_id)

        allowed = {
            Status.BACKLOG: {Status.READY, Status.CANCELLED},
            Status.READY: {
                Status.IN_PROGRESS,
                Status.BLOCKED,
                Status.CANCELLED,
            },
            Status.IN_PROGRESS: {
                Status.READY,
                Status.BLOCKED,
                Status.DONE,
                Status.CANCELLED,
            },
            Status.BLOCKED: {
                Status.READY,
                Status.IN_PROGRESS,
                Status.CANCELLED,
            },
            Status.DONE: {Status.READY},
            Status.CANCELLED: {Status.BACKLOG},
        }

        if new_status == item.status:
            return

        if new_status not in allowed[item.status]:
            raise WorkItemError(
                f"Invalid transition for {item_id}: "
                f"{item.status.value} -> {new_status.value}"
            )

        if new_status == Status.IN_PROGRESS:
            unmet = self.unmet_dependencies(item_id)
            if unmet:
                raise WorkItemError(
                    f"{item_id} cannot start; incomplete dependencies: "
                    f"{', '.join(unmet)}"
                )

        if new_status == Status.DONE:
            if item.work_type in {WorkType.EPIC, WorkType.FEATURE}:
                incomplete = [
                    child.item_id
                    for child in self.descendants(item_id)
                    if child.work_type in {WorkType.STORY, WorkType.TASK}
                    and child.status not in {Status.DONE, Status.CANCELLED}
                ]
                if incomplete:
                    raise WorkItemError(
                        f"{item_id} cannot complete; unfinished work: "
                        f"{', '.join(incomplete)}"
                    )

            if item.work_type == WorkType.STORY:
                incomplete_tasks = [
                    child.item_id
                    for child in self.children(item_id)
                    if child.status not in {Status.DONE, Status.CANCELLED}
                ]
                if incomplete_tasks:
                    raise WorkItemError(
                        f"{item_id} cannot complete; unfinished tasks: "
                        f"{', '.join(incomplete_tasks)}"
                    )

        item.status = new_status
        item.version += 1

    def update_acceptance_criteria(
        self,
        item_id: str,
        criteria: Iterable[str],
    ) -> None:
        item = self.get(item_id)

        if item.work_type != WorkType.STORY:
            raise WorkItemError(
                "Acceptance criteria belong to user stories."
            )

        normalized = list(dict.fromkeys(
            criterion.strip()
            for criterion in criteria
            if criterion.strip()
        ))

        if not normalized:
            raise WorkItemError(
                "A story cannot have an empty acceptance-criteria list."
            )

        item.acceptance_criteria = normalized
        item.version += 1

    def rollup(self, item_id: str) -> dict[str, float | int]:
        """
        Calculate progress from story points when present, otherwise task
        hours. Never add story points and task hours into one unit.
        """
        item = self.get(item_id)
        descendants = self.descendants(item_id)
        stories = [
            candidate
            for candidate in descendants
            if candidate.work_type == WorkType.STORY
            and candidate.status != Status.CANCELLED
        ]

        estimated_stories = [
            story for story in stories if story.story_points is not None
        ]

        if estimated_stories:
            total = sum(story.story_points or 0 for story in estimated_stories)
            completed = sum(
                story.story_points or 0
                for story in estimated_stories
                if story.status == Status.DONE
            )
            return {
                "unit": "story_points",
                "total": total,
                "completed": completed,
                "remaining": total - completed,
                "percent_complete": (
                    round(completed / total * 100, 2) if total else 0.0
                ),
                "unestimated_stories": sum(
                    story.story_points is None for story in stories
                ),
            }

        tasks = [
            candidate
            for candidate in descendants
            if candidate.work_type == WorkType.TASK
            and candidate.status != Status.CANCELLED
            and candidate.estimate_hours is not None
        ]
        total_hours = sum(task.estimate_hours or 0 for task in tasks)
        completed_hours = sum(
            task.estimate_hours or 0
            for task in tasks
            if task.status == Status.DONE
        )

        return {
            "unit": "task_hours",
            "total": total_hours,
            "completed": completed_hours,
            "remaining": total_hours - completed_hours,
            "percent_complete": (
                round(completed_hours / total_hours * 100, 2)
                if total_hours
                else 0.0
            ),
            "unestimated_stories": len(stories),
        }

    def release_readiness(self, epic_id: str) -> dict[str, object]:
        epic = self.get(epic_id)

        if epic.work_type != WorkType.EPIC:
            raise WorkItemError("Release readiness requires an epic.")

        descendants = self.descendants(epic_id)
        stories = [
            item for item in descendants
            if item.work_type == WorkType.STORY
            and item.status != Status.CANCELLED
        ]
        unfinished = [
            item.item_id
            for item in stories
            if item.status != Status.DONE
        ]
        blocked = [
            item.item_id
            for item in descendants
            if item.status == Status.BLOCKED
        ]
        missing_criteria = [
            item.item_id
            for item in stories
            if not item.acceptance_criteria
        ]

        return {
            "epic_id": epic_id,
            "story_count": len(stories),
            "unfinished_stories": unfinished,
            "blocked_items": blocked,
            "stories_missing_acceptance_criteria": missing_criteria,
            "ready": not unfinished and not blocked and not missing_criteria,
        }

    def tree(self, root_id: str) -> str:
        root = self.get(root_id)
        lines = [
            f"{root.item_id} [{root.work_type.value}] "
            f"{root.title} ({root.status.value})"
        ]

        def append_children(parent_id: str, depth: int) -> None:
            for child in self.children(parent_id):
                lines.append(
                    f"{'  ' * depth}- {child.item_id} "
                    f"[{child.work_type.value}] {child.title} "
                    f"({child.status.value})"
                )
                append_children(child.item_id, depth + 1)

        append_children(root_id, 1)
        return "\n".join(lines)

    def export_json(self) -> str:
        records = []

        for item in sorted(self.items.values(), key=lambda value: value.item_id):
            records.append({
                "id": item.item_id,
                "title": item.title,
                "type": item.work_type.value,
                "parent_id": item.parent_id,
                "status": item.status.value,
                "priority": item.priority.value,
                "owner": item.owner,
                "story_points": item.story_points,
                "estimate_hours": item.estimate_hours,
                "acceptance_criteria": item.acceptance_criteria,
                "due_date": item.due_date.isoformat() if item.due_date else None,
                "labels": sorted(item.labels),
                "dependencies": sorted(item.dependency_ids),
                "version": item.version,
            })

        return json.dumps(records, indent=2)


def create_example_tracker() -> WorkTracker:
    tracker = WorkTracker()

    tracker.add(WorkItem(
        "EP-100",
        "Customer Self-Service Platform",
        WorkType.EPIC,
        priority=Priority.CRITICAL,
        owner="Product Management",
        due_date=date(2026, 12, 15),
        labels={"customer-experience", "release-4"},
    ))

    tracker.add(WorkItem(
        "FE-110",
        "Secure Account Access",
        WorkType.FEATURE,
        parent_id="EP-100",
        priority=Priority.CRITICAL,
        owner="Identity Team",
    ))

    tracker.add(WorkItem(
        "ST-111",
        "As a customer, I can sign in securely",
        WorkType.STORY,
        parent_id="FE-110",
        priority=Priority.CRITICAL,
        owner="Identity Team",
        story_points=5,
        acceptance_criteria=[
            "Valid credentials create an authenticated session.",
            "Invalid credentials do not disclose which field was incorrect.",
            "Repeated failures trigger the configured rate limit.",
        ],
        labels={"authentication", "security"},
    ))

    tracker.add(WorkItem(
        "TS-111A",
        "Implement authentication endpoint",
        WorkType.TASK,
        parent_id="ST-111",
        owner="Backend Engineering",
        estimate_hours=8,
    ))

    tracker.add(WorkItem(
        "TS-111B",
        "Add rate-limit integration tests",
        WorkType.TASK,
        parent_id="ST-111",
        owner="Quality Engineering",
        estimate_hours=5,
        dependency_ids={"TS-111A"},
    ))

    tracker.add(WorkItem(
        "ST-112",
        "As a customer, I can reset my password",
        WorkType.STORY,
        parent_id="FE-110",
        owner="Identity Team",
        story_points=8,
        acceptance_criteria=[
            "Reset links expire after the configured lifetime.",
            "Reset tokens cannot be used more than once.",
            "Reset responses do not reveal whether an account exists.",
        ],
    ))

    tracker.add(WorkItem(
        "FE-120",
        "Order Visibility",
        WorkType.FEATURE,
        parent_id="EP-100",
        owner="Commerce Team",
    ))

    tracker.add(WorkItem(
        "ST-121",
        "As a customer, I can track an order",
        WorkType.STORY,
        parent_id="FE-120",
        owner="Commerce Team",
        story_points=5,
        acceptance_criteria=[
            "Customers can view only their own orders.",
            "Order status reflects the latest authorized update.",
        ],
    ))

    tracker.add(WorkItem(
        "TS-121A",
        "Implement order-status API",
        WorkType.TASK,
        parent_id="ST-121",
        owner="Backend Engineering",
        estimate_hours=10,
        dependency_ids={"TS-111A"},
    ))

    return tracker


def demonstrate_invalid_cases(tracker: WorkTracker) -> None:
    print("\nValidation examples")

    try:
        tracker.add(WorkItem(
            "ST-INVALID",
            "Story without acceptance criteria",
            WorkType.STORY,
            parent_id="FE-110",
            story_points=3,
        ))
    except WorkItemError as error:
        print(f"Rejected invalid story: {error}")

    try:
        tracker.add(WorkItem(
            "FE-INVALID",
            "Feature with wrong parent",
            WorkType.FEATURE,
            parent_id="ST-111",
        ))
    except WorkItemError as error:
        print(f"Rejected invalid hierarchy: {error}")

    try:
        tracker.transition("TS-111B", Status.IN_PROGRESS)
    except WorkItemError as error:
        print(f"Rejected premature work: {error}")

    try:
        tracker.transition("ST-111", Status.DONE)
    except WorkItemError as error:
        print(f"Rejected premature story completion: {error}")


def main() -> None:
    tracker = create_example_tracker()

    print("Epic and feature hierarchy")
    print(tracker.tree("EP-100"))

    print("\nEpic delivery metrics")
    print(json.dumps(tracker.rollup("EP-100"), indent=2))

    print("\nRelease readiness")
    print(json.dumps(tracker.release_readiness("EP-100"), indent=2))

    demonstrate_invalid_cases(tracker)

    print("\nExecuting valid delivery transitions")
    tracker.transition("TS-111A", Status.READY)
    tracker.transition("TS-111A", Status.IN_PROGRESS)
    tracker.transition("TS-111A", Status.DONE)
    tracker.transition("TS-111B", Status.READY)
    tracker.transition("TS-111B", Status.IN_PROGRESS)
    tracker.transition("TS-111B", Status.DONE)
    tracker.transition("ST-111", Status.READY)
    tracker.transition("ST-111", Status.IN_PROGRESS)
    tracker.transition("ST-111", Status.DONE)

    print(tracker.tree("FE-110"))
    print("\nUpdated feature metrics")
    print(json.dumps(tracker.rollup("FE-110"), indent=2))

    print("\nUpdated release readiness")
    print(json.dumps(tracker.release_readiness("EP-100"), indent=2))

    print("\nJSON export")
    print(tracker.export_json())


if __name__ == "__main__":
    main()
