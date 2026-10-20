from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set


class BacklogStatus(Enum):
    DISCOVERY = "discovery"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class BacklogItem:
    item_id: str
    title: str
    customer_problem: str
    value: int
    effort: int
    priority: Priority
    status: BacklogStatus = BacklogStatus.DISCOVERY
    evidence: List[str] = field(default_factory=list)

    def score(self) -> float:
        if self.effort <= 0:
            raise ValueError(f"Invalid effort for {self.item_id}")
        return (self.value * self.priority_weight()) / self.effort

    def priority_weight(self) -> float:
        return {
            Priority.CRITICAL: 4.0,
            Priority.HIGH: 3.0,
            Priority.MEDIUM: 2.0,
            Priority.LOW: 1.0,
        }[self.priority]

    def validate(self) -> None:
        if not self.item_id.strip():
            raise ValueError("Backlog item requires an identifier")
        if not self.title.strip():
            raise ValueError(f"{self.item_id}: title cannot be empty")
        if not self.customer_problem.strip():
            raise ValueError(f"{self.item_id}: customer problem is required")
        if not 1 <= self.value <= 100:
            raise ValueError(f"{self.item_id}: value must be 1..100")
        if not 1 <= self.effort <= 100:
            raise ValueError(f"{self.item_id}: effort must be 1..100")
        if not self.evidence:
            raise ValueError(f"{self.item_id}: discovery evidence is required")


@dataclass(frozen=True)
class ProductGoal:
    goal_id: str
    statement: str
    outcome_metric: str
    target: float
    deadline: date

    def is_valid(self) -> bool:
        return bool(
            self.goal_id.strip()
            and self.statement.strip()
            and self.outcome_metric.strip()
            and self.target >= 0
        )


@dataclass(frozen=True)
class SprintGoal:
    sprint_id: str
    statement: str
    product_goal_id: str


@dataclass
class Sprint:
    sprint_id: str
    start: date
    end: date
    goal: SprintGoal
    selected_items: List[str] = field(default_factory=list)

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end


@dataclass
class DiscoveryExperiment:
    experiment_id: str
    hypothesis: str
    method: str
    success_threshold: float
    observations: List[float] = field(default_factory=list)

    def result(self) -> Optional[float]:
        if not self.observations:
            return None
        return sum(self.observations) / len(self.observations)

    def supports_hypothesis(self) -> bool:
        result = self.result()
        return result is not None and result >= self.success_threshold


@dataclass
class RoadmapOutcome:
    outcome_id: str
    statement: str
    target_date: date
    product_goal_id: str
    linked_backlog_items: Set[str] = field(default_factory=set)


class ProductManagementModel:
    """
    A compact product-management simulation.

    The model deliberately separates:
    - Product goals: desired product outcomes.
    - Roadmap: directional outcomes and timing.
    - Backlog: actionable opportunities and delivery candidates.
    - Sprint goals: short-term focus for a fixed iteration.
    - Continuous discovery: evidence collection before committing to solutions.
    """

    def __init__(self) -> None:
        self.backlog: Dict[str, BacklogItem] = {}
        self.product_goals: Dict[str, ProductGoal] = {}
        self.roadmap: Dict[str, RoadmapOutcome] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.experiments: Dict[str, DiscoveryExperiment] = {}

    def add_product_goal(self, goal: ProductGoal) -> None:
        if not goal.is_valid():
            raise ValueError("Invalid product goal")
        if goal.goal_id in self.product_goals:
            raise ValueError(f"Duplicate product goal: {goal.goal_id}")
        self.product_goals[goal.goal_id] = goal

    def add_backlog_item(self, item: BacklogItem) -> None:
        item.validate()
        if item.item_id in self.backlog:
            raise ValueError(f"Duplicate backlog item: {item.item_id}")
        self.backlog[item.item_id] = item

    def add_roadmap_outcome(self, outcome: RoadmapOutcome) -> None:
        if outcome.product_goal_id not in self.product_goals:
            raise ValueError("Roadmap outcome references an unknown product goal")
        if outcome.target_date < date.today():
            raise ValueError("Roadmap outcome cannot start with a past target date")
        if not outcome.statement.strip():
            raise ValueError("Roadmap outcome requires a statement")
        if outcome.outcome_id in self.roadmap:
            raise ValueError(f"Duplicate roadmap outcome: {outcome.outcome_id}")
        self.roadmap[outcome.outcome_id] = outcome

    def prioritize_backlog(self) -> List[BacklogItem]:
        for item in self.backlog.values():
            item.validate()
        return sorted(
            self.backlog.values(),
            key=lambda item: (-item.score(), item.priority.value, item.item_id),
        )

    def create_sprint(
        self,
        sprint_id: str,
        start: date,
        end: date,
        goal: SprintGoal,
        capacity: int,
    ) -> Sprint:
        if start > end:
            raise ValueError("Sprint start must not exceed sprint end")
        if capacity <= 0:
            raise ValueError("Sprint capacity must be positive")
        if goal.product_goal_id not in self.product_goals:
            raise ValueError("Sprint goal must support an existing product goal")
        if sprint_id in self.sprints:
            raise ValueError(f"Duplicate sprint: {sprint_id}")

        candidates = [
            item for item in self.prioritize_backlog()
            if item.status in {BacklogStatus.READY, BacklogStatus.DISCOVERY}
        ]

        selected: List[str] = []
        remaining = capacity

        for item in candidates:
            if item.effort <= remaining:
                selected.append(item.item_id)
                remaining -= item.effort
                item.status = BacklogStatus.IN_PROGRESS

        if not selected:
            raise ValueError("No backlog item fits the sprint capacity")

        sprint = Sprint(
            sprint_id=sprint_id,
            start=start,
            end=end,
            goal=goal,
            selected_items=selected,
        )
        self.sprints[sprint_id] = sprint
        return sprint

    def complete_item(self, item_id: str, sprint_id: str) -> None:
        item = self.backlog.get(item_id)
        sprint = self.sprints.get(sprint_id)

        if item is None:
            raise KeyError(f"Unknown backlog item: {item_id}")
        if sprint is None:
            raise KeyError(f"Unknown sprint: {sprint_id}")
        if item_id not in sprint.selected_items:
            raise ValueError("Item was not selected for this sprint")
        if item.status != BacklogStatus.IN_PROGRESS:
            raise ValueError("Only in-progress items can be completed")

        item.status = BacklogStatus.DONE

    def add_experiment(self, experiment: DiscoveryExperiment) -> None:
        if experiment.experiment_id in self.experiments:
            raise ValueError("Duplicate discovery experiment")
        if not experiment.hypothesis.strip() or not experiment.method.strip():
            raise ValueError("Discovery experiment requires hypothesis and method")
        if not 0 <= experiment.success_threshold <= 1:
            raise ValueError("Success threshold must be between 0 and 1")
        self.experiments[experiment.experiment_id] = experiment

    def report(self) -> str:
        lines = [
            "PRODUCT MANAGEMENT REPORT",
            f"Product goals: {len(self.product_goals)}",
            f"Roadmap outcomes: {len(self.roadmap)}",
            f"Backlog items: {len(self.backlog)}",
            f"Sprints: {len(self.sprints)}",
            f"Discovery experiments: {len(self.experiments)}",
            "",
            "Prioritized backlog:",
        ]

        for item in self.prioritize_backlog():
            lines.append(
                f"  {item.item_id}: score={item.score():.2f}, "
                f"priority={item.priority.name}, status={item.status.value}"
            )

        lines.append("")
        lines.append("Discovery evidence:")
        for experiment in self.experiments.values():
            result = experiment.result()
            outcome = "supported" if experiment.supports_hypothesis() else "not supported"
            result_text = "no observations" if result is None else f"{result:.2f}"
            lines.append(
                f"  {experiment.experiment_id}: result={result_text}, {outcome}"
            )

        return "\n".join(lines)


def build_demo() -> ProductManagementModel:
    model = ProductManagementModel()

    goal = ProductGoal(
        goal_id="PG-01",
        statement="Increase successful first-week activation for new customers.",
        outcome_metric="activation_rate",
        target=0.65,
        deadline=date.today() + timedelta(days=90),
    )
    model.add_product_goal(goal)

    model.add_roadmap_outcome(
        RoadmapOutcome(
            outcome_id="RO-01",
            statement="Reduce onboarding friction and improve first-value discovery.",
            target_date=date.today() + timedelta(days=45),
            product_goal_id="PG-01",
        )
    )

    items = [
        BacklogItem(
            "PB-101",
            "Simplify first-run setup",
            "New users abandon setup before reaching first value.",
            90,
            8,
            Priority.CRITICAL,
            BacklogStatus.READY,
            ["session interviews", "funnel analysis"],
        ),
        BacklogItem(
            "PB-102",
            "Add contextual onboarding checklist",
            "Users cannot identify the next useful action.",
            80,
            5,
            Priority.HIGH,
            BacklogStatus.READY,
            ["customer interviews", "support tickets"],
        ),
        BacklogItem(
            "PB-103",
            "Redesign reporting dashboard",
            "Existing users need faster access to recurring reports.",
            65,
            13,
            Priority.MEDIUM,
            BacklogStatus.READY,
            ["usage analytics"],
        ),
        BacklogItem(
            "PB-104",
            "Explore guided setup experiment",
            "A guided workflow may improve first-value completion.",
            75,
            3,
            Priority.HIGH,
            BacklogStatus.DISCOVERY,
            ["prototype interviews"],
        ),
    ]

    for item in items:
        model.add_backlog_item(item)

    model.add_experiment(
        DiscoveryExperiment(
            experiment_id="EXP-01",
            hypothesis="A guided setup will improve first-value completion.",
            method="Prototype usability test",
            success_threshold=0.70,
            observations=[0.72, 0.76, 0.68, 0.74],
        )
    )

    sprint_goal = SprintGoal(
        sprint_id="SPR-01",
        statement="Improve the path from account creation to first value.",
        product_goal_id="PG-01",
    )

    model.create_sprint(
        sprint_id="SPR-01",
        start=date.today(),
        end=date.today() + timedelta(days=13),
        goal=sprint_goal,
        capacity=13,
    )

    return model


if __name__ == "__main__":
    product = build_demo()

    print(product.report())

    # Complete one selected item to demonstrate an explicit delivery state transition.
    sprint = product.sprints["SPR-01"]
    if sprint.selected_items:
        product.complete_item(sprint.selected_items[0], sprint.sprint_id)

    print("\nAfter delivery transition:")
    print(product.report())
