#!/usr/bin/env python3
"""Product backlog engineering: refinement, prioritization, dependencies, and technical debt."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Iterable


class BacklogError(ValueError):
    """Raised when a backlog operation violates a domain rule."""


class ItemType(str, Enum):
    FEATURE = "feature"
    BUG = "bug"
    TECHNICAL_DEBT = "technical_debt"
    SPIKE = "spike"
    SECURITY = "security"


class ItemStatus(str, Enum):
    PROPOSED = "proposed"
    REFINING = "refining"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    REJECTED = "rejected"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BacklogItem:
    item_id: str
    title: str
    item_type: ItemType
    description: str
    business_value: int
    urgency: int
    risk_reduction: int
    effort: int
    status: ItemStatus = ItemStatus.PROPOSED
    dependencies: set[str] = field(default_factory=set)
    acceptance_criteria: list[str] = field(default_factory=list)
    owner: str | None = None
    created_on: date = field(default_factory=date.today)
    target_release: str | None = None
    debt_interest_per_sprint: float = 0.0
    debt_principal: float = 0.0

    def __post_init__(self) -> None:
        self.item_id = self.item_id.strip().upper()
        self.title = self.title.strip()
        if not self.item_id or not self.title or not self.description.strip():
            raise BacklogError("ID, title, and description are required.")
        for name in ("business_value", "urgency", "risk_reduction"):
            value = getattr(self, name)
            if not 1 <= value <= 10:
                raise BacklogError(f"{name} must be between 1 and 10.")
        if not 1 <= self.effort <= 100:
            raise BacklogError("Effort must be between 1 and 100.")
        if self.debt_principal < 0 or self.debt_interest_per_sprint < 0:
            raise BacklogError("Technical debt values cannot be negative.")
        self.acceptance_criteria = [
            criterion.strip()
            for criterion in self.acceptance_criteria
            if criterion.strip()
        ]


class ProductBacklog:
    """Maintains backlog integrity and computes transparent priority signals."""

    def __init__(self, name: str, capacity_per_sprint: int = 20) -> None:
        if capacity_per_sprint < 1:
            raise BacklogError("Sprint capacity must be positive.")
        self.name = name
        self.capacity_per_sprint = capacity_per_sprint
        self.items: dict[str, BacklogItem] = {}

    def add(self, item: BacklogItem) -> None:
        if item.item_id in self.items:
            raise BacklogError(f"Duplicate backlog ID: {item.item_id}")
        if item.item_id in item.dependencies:
            raise BacklogError("An item cannot depend on itself.")
        missing = item.dependencies - self.items.keys()
        if missing:
            raise BacklogError(f"Unknown dependencies: {sorted(missing)}")
        self.items[item.item_id] = item
        try:
            self._assert_acyclic()
        except BacklogError:
            del self.items[item.item_id]
            raise

    def add_dependency(self, item_id: str, dependency_id: str) -> None:
        item = self.get(item_id)
        self.get(dependency_id)
        if item_id == dependency_id:
            raise BacklogError("Self-dependencies are forbidden.")
        if item.status in (ItemStatus.IN_PROGRESS, ItemStatus.DONE):
            raise BacklogError("Dependencies cannot be changed after work starts.")
        item.dependencies.add(dependency_id)
        try:
            self._assert_acyclic()
        except BacklogError:
            item.dependencies.remove(dependency_id)
            raise

    def get(self, item_id: str) -> BacklogItem:
        try:
            return self.items[item_id.strip().upper()]
        except KeyError as exc:
            raise BacklogError(f"Unknown backlog item: {item_id}") from exc

    def _assert_acyclic(self) -> None:
        # Three-color depth-first search detects circular dependency chains.
        state: dict[str, int] = {}

        def visit(item_id: str) -> None:
            if state.get(item_id) == 1:
                raise BacklogError(f"Circular dependency involving {item_id}")
            if state.get(item_id) == 2:
                return
            state[item_id] = 1
            for dependency in self.items[item_id].dependencies:
                if dependency not in self.items:
                    raise BacklogError(f"Missing dependency: {dependency}")
                visit(dependency)
            state[item_id] = 2

        for item_id in self.items:
            visit(item_id)

    def dependency_closure(self, item_id: str) -> set[str]:
        """Return every transitive prerequisite, excluding the requested item."""
        self.get(item_id)
        found: set[str] = set()
        pending = list(self.get(item_id).dependencies)
        while pending:
            current = pending.pop()
            if current in found:
                continue
            found.add(current)
            pending.extend(self.get(current).dependencies)
        return found

    def blockers(self, item_id: str) -> list[str]:
        # Only unfinished direct prerequisites block immediate execution.
        item = self.get(item_id)
        return sorted(
            dependency
            for dependency in item.dependencies
            if self.get(dependency).status != ItemStatus.DONE
        )

    def transition(self, item_id: str, new_status: ItemStatus) -> None:
        item = self.get(item_id)
        allowed = {
            ItemStatus.PROPOSED: {ItemStatus.REFINING, ItemStatus.REJECTED},
            ItemStatus.REFINING: {
                ItemStatus.PROPOSED, ItemStatus.READY, ItemStatus.REJECTED
            },
            ItemStatus.READY: {
                ItemStatus.REFINING, ItemStatus.IN_PROGRESS, ItemStatus.REJECTED
            },
            ItemStatus.IN_PROGRESS: {
                ItemStatus.BLOCKED, ItemStatus.DONE, ItemStatus.READY
            },
            ItemStatus.BLOCKED: {ItemStatus.IN_PROGRESS, ItemStatus.READY},
            ItemStatus.DONE: set(),
            ItemStatus.REJECTED: {ItemStatus.REFINING},
        }
        if new_status not in allowed[item.status]:
            raise BacklogError(
                f"Invalid transition for {item_id}: "
                f"{item.status.value} -> {new_status.value}"
            )
        if new_status == ItemStatus.READY:
            if not item.acceptance_criteria:
                raise BacklogError("Ready items require acceptance criteria.")
            if self.blockers(item_id):
                raise BacklogError("Ready items cannot have unfinished dependencies.")
        if new_status == ItemStatus.IN_PROGRESS and self.blockers(item_id):
            raise BacklogError("Blocked dependencies must be completed first.")
        if new_status == ItemStatus.DONE and item.status != ItemStatus.IN_PROGRESS:
            raise BacklogError("Only in-progress work can be completed.")
        item.status = new_status

    @staticmethod
    def priority_score(item: BacklogItem) -> float:
        """A transparent WSJF-inspired heuristic, not an objective truth."""
        cost_of_delay = (
            item.business_value * 0.5
            + item.urgency * 0.3
            + item.risk_reduction * 0.2
        )
        return cost_of_delay / item.effort

    @staticmethod
    def priority_band(item: BacklogItem) -> Priority:
        if item.item_type in (ItemType.SECURITY, ItemType.BUG):
            if item.urgency >= 9 or item.risk_reduction >= 9:
                return Priority.CRITICAL
        score = ProductBacklog.priority_score(item)
        if score >= 3.5:
            return Priority.HIGH
        if score >= 1.8:
            return Priority.MEDIUM
        return Priority.LOW

    def prioritize(self) -> list[BacklogItem]:
        # Stable ID tie-breaking makes reports reproducible.
        return sorted(
            (item for item in self.items.values()
             if item.status not in (ItemStatus.DONE, ItemStatus.REJECTED)),
            key=lambda item: (
                self.priority_band(item).value != Priority.CRITICAL.value,
                -self.priority_score(item),
                item.item_id,
            ),
        )

    def ready_for_refinement(self) -> list[BacklogItem]:
        return [
            item for item in self.items.values()
            if item.status in (ItemStatus.PROPOSED, ItemStatus.REFINING)
        ]

    def debt_report(self, projected_sprints: int = 4) -> list[dict[str, float | str]]:
        if projected_sprints < 0:
            raise BacklogError("Projected sprints cannot be negative.")
        report = []
        for item in self.items.values():
            if item.item_type != ItemType.TECHNICAL_DEBT:
                continue
            projected_cost = (
                item.debt_principal
                + item.debt_interest_per_sprint * projected_sprints
            )
            report.append({
                "id": item.item_id,
                "principal": item.debt_principal,
                "interest": item.debt_interest_per_sprint * projected_sprints,
                "projected_cost": projected_cost,
            })
        return sorted(report, key=lambda row: -float(row["projected_cost"]))

    def plan_sprint(self) -> list[BacklogItem]:
        """Greedy feasible selection that respects prerequisites and capacity."""
        selected: list[BacklogItem] = []
        completed_or_selected = {
            item.item_id for item in self.items.values()
            if item.status == ItemStatus.DONE
        }
        used_capacity = 0
        candidates = self.prioritize()

        while True:
            feasible = [
                item for item in candidates
                if item.item_id not in completed_or_selected
                and item.status == ItemStatus.READY
                and item.dependencies <= completed_or_selected
                and used_capacity + item.effort <= self.capacity_per_sprint
            ]
            if not feasible:
                break
            chosen = feasible[0]
            selected.append(chosen)
            completed_or_selected.add(chosen.item_id)
            used_capacity += chosen.effort
        return selected


def demonstrate_failure(label: str, operation) -> None:
    try:
        operation()
    except BacklogError as exc:
        print(f"{label}: correctly rejected ({exc})")


def build_example_backlog() -> ProductBacklog:
    backlog = ProductBacklog("Service Reliability Platform", capacity_per_sprint=13)
    items = [
        BacklogItem(
            "PLAT-101", "Add request correlation IDs", ItemType.FEATURE,
            "Propagate a request identifier across API and worker logs.",
            8, 7, 7, 3,
            acceptance_criteria=[
                "Every accepted request has a correlation ID",
                "The ID appears in API and worker logs",
            ],
        ),
        BacklogItem(
            "PLAT-102", "Introduce structured error responses", ItemType.FEATURE,
            "Return stable machine-readable error codes from the API.",
            8, 8, 5, 5,
            acceptance_criteria=[
                "Validation errors include a stable code",
                "Internal stack traces are never returned to clients",
            ],
        ),
        BacklogItem(
            "PLAT-103", "Instrument request latency", ItemType.FEATURE,
            "Record latency histograms for API requests.",
            7, 7, 8, 5,
            acceptance_criteria=[
                "Latency is recorded by route and outcome",
                "Sensitive request payloads are not metric labels",
            ],
        ),
        BacklogItem(
            "PLAT-104", "Remove duplicate database queries", ItemType.TECHNICAL_DEBT,
            "Replace repeated per-record queries with batched retrieval.",
            6, 5, 8, 5,
            debt_principal=13_000, debt_interest_per_sprint=1_800,
            acceptance_criteria=[
                "Query count remains bounded as result size grows",
                "Returned records preserve existing ordering",
            ],
        ),
        BacklogItem(
            "PLAT-105", "Rotate exposed staging credentials", ItemType.SECURITY,
            "Replace a staging credential and audit access logs.",
            9, 10, 10, 2,
            acceptance_criteria=[
                "Old credential is rejected",
                "Access logs show no unexplained use",
            ],
        ),
        BacklogItem(
            "PLAT-106", "Add retry backoff to workers", ItemType.FEATURE,
            "Use bounded exponential backoff for transient failures.",
            8, 8, 7, 5,
            acceptance_criteria=[
                "Retries have a maximum attempt count",
                "Permanent failures are not retried",
            ],
        ),
    ]
    for item in items:
        backlog.add(item)

    backlog.add_dependency("PLAT-103", "PLAT-101")
    backlog.add_dependency("PLAT-106", "PLAT-102")

    for item in items:
        backlog.transition(item.item_id, ItemStatus.REFINING)
        backlog.transition(item.item_id, ItemStatus.READY)
    return backlog


def main() -> None:
    print("PRODUCT BACKLOG ENGINEERING")
    print("=" * 72)

    backlog = build_example_backlog()

    print("\nPriority assessment")
    print(f"{'ID':<12} {'Band':<10} {'Score':>7} {'Effort':>7} {'Title'}")
    for item in backlog.prioritize():
        print(
            f"{item.item_id:<12} {backlog.priority_band(item).value:<10} "
            f"{backlog.priority_score(item):>7.2f} {item.effort:>7} {item.title}"
        )

    print("\nDependency analysis")
    for item in backlog.items.values():
        if item.dependencies:
            print(
                f"{item.item_id} depends on {sorted(item.dependencies)}; "
                f"transitive prerequisites={sorted(backlog.dependency_closure(item.item_id))}; "
                f"blockers={backlog.blockers(item.item_id)}"
            )

    print("\nTechnical debt forecast")
    for row in backlog.debt_report(projected_sprints=4):
        print(
            f"{row['id']}: principal={row['principal']:.0f}, "
            f"projected interest={row['interest']:.0f}, "
            f"forecast cost={row['projected_cost']:.0f}"
        )

    print("\nSprint selection")
    selected = backlog.plan_sprint()
    for item in selected:
        print(f"{item.item_id}: {item.title} ({item.effort} effort units)")
    print(f"Total planned effort: {sum(item.effort for item in selected)}")

    print("\nValidation and failure handling")
    demonstrate_failure(
        "Missing acceptance criteria",
        lambda: ProductBacklog("Validation").transition(
            "MISSING", ItemStatus.READY
        ),
    )
    demonstrate_failure(
        "Circular dependency",
        lambda: backlog.add_dependency("PLAT-101", "PLAT-103"),
    )
    demonstrate_failure(
        "Invalid completion",
        lambda: backlog.transition("PLAT-101", ItemStatus.DONE),
    )

    print("\nCompleting a prerequisite")
    backlog.transition("PLAT-105", ItemStatus.IN_PROGRESS)
    backlog.transition("PLAT-105", ItemStatus.DONE)
    print(f"PLAT-105 status: {backlog.get('PLAT-105').status.value}")

    demonstrate_failure(
        "Invalid effort",
        lambda: BacklogItem(
            "BAD-001", "Invalid item", ItemType.FEATURE, "Invalid estimate",
            5, 5, 5, 0,
        ),
    )

    print("\nEngineering notes")
    print("Priority scores support discussion; they do not replace product judgment.")
    print("A sprint plan is a greedy heuristic, not a globally optimal knapsack solution.")
    print("Dependency cycles are rejected before the backlog is modified.")
    print("Technical debt forecasts are estimates and must be calibrated against evidence.")


if __name__ == "__main__":
    main()
