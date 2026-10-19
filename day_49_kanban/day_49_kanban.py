from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
from statistics import mean
from typing import Deque, Dict, List, Optional, Set, Tuple


class Column(str, Enum):
    BACKLOG = "Backlog"
    READY = "Ready"
    DEVELOPMENT = "Development"
    REVIEW = "Review"
    TESTING = "Testing"
    DONE = "Done"


@dataclass
class WorkItem:
    key: str
    title: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    column: Column = Column.BACKLOG
    history: List[Tuple[datetime, Column]] = field(default_factory=list)

    def move_to(self, column: Column, when: datetime) -> None:
        if self.column == column:
            return
        self.column = column
        self.history.append((when, column))
        if self.started_at is None and column in {
            Column.DEVELOPMENT,
            Column.REVIEW,
            Column.TESTING,
        }:
            self.started_at = when
        if column == Column.DONE:
            self.completed_at = when


@dataclass
class KanbanPolicy:
    wip_limits: Dict[Column, int]
    expedite_limit: int = 1

    def allows_entry(self, column: Column, current_count: int) -> bool:
        limit = self.wip_limits.get(column)
        return limit is None or current_count < limit


class KanbanBoard:
    """
    A pull-based board.

    WIP limits apply to work already occupying a constrained column. A move
    into a full column is rejected instead of pushing work through by force.
    """

    def __init__(self, policy: KanbanPolicy):
        self.policy = policy
        self.items: Dict[str, WorkItem] = {}
        self.completed: List[WorkItem] = []
        self.event_log: List[str] = []

    def add_item(self, item: WorkItem) -> None:
        if item.key in self.items:
            raise ValueError(f"Duplicate work item: {item.key}")
        self.items[item.key] = item
        item.history.append((item.created_at, item.column))

    def count(self, column: Column) -> int:
        return sum(item.column == column for item in self.items.values())

    def move(self, key: str, destination: Column, when: datetime) -> None:
        if key not in self.items:
            raise KeyError(f"Unknown work item: {key}")

        item = self.items[key]
        if item.column == destination:
            return

        if not self.policy.allows_entry(destination, self.count(destination)):
            raise RuntimeError(
                f"WIP limit prevents {key} entering {destination.value}"
            )

        item.move_to(destination, when)
        self.event_log.append(
            f"{when.isoformat()} {key}: {item.history[-2][1].value}"
            f" -> {destination.value}"
        )

        if destination == Column.DONE and item not in self.completed:
            self.completed.append(item)

    def pull_next(
        self, source: Column, destination: Column, when: datetime
    ) -> Optional[WorkItem]:
        candidates = [
            item
            for item in self.items.values()
            if item.column == source
        ]
        if not candidates or not self.policy.allows_entry(
            destination, self.count(destination)
        ):
            return None

        # Lower priority number means more urgent. Creation time breaks ties.
        candidates.sort(key=lambda item: (item.priority, item.created_at))
        selected = candidates[0]
        self.move(selected.key, destination, when)
        return selected

    def snapshot(self) -> Dict[str, int]:
        return {column.value: self.count(column) for column in Column}

    def blocked_columns(self) -> List[Column]:
        result = []
        for column, limit in self.policy.wip_limits.items():
            if self.count(column) >= limit:
                result.append(column)
        return result


class FlowMetrics:
    @staticmethod
    def cycle_time(item: WorkItem) -> Optional[timedelta]:
        if item.started_at is None or item.completed_at is None:
            return None
        return item.completed_at - item.started_at

    @staticmethod
    def lead_time(item: WorkItem) -> Optional[timedelta]:
        if item.completed_at is None:
            return None
        return item.completed_at - item.created_at

    @staticmethod
    def throughput(
        completed: List[WorkItem],
        start: datetime,
        end: datetime,
    ) -> int:
        return sum(
            1
            for item in completed
            if item.completed_at is not None
            and start <= item.completed_at < end
        )

    @staticmethod
    def average_cycle_time(completed: List[WorkItem]) -> Optional[timedelta]:
        values = [
            FlowMetrics.cycle_time(item)
            for item in completed
            if FlowMetrics.cycle_time(item) is not None
        ]
        return sum(values, timedelta()) / len(values) if values else None


class KanbanSimulator:
    """
    Simulates a small engineering workflow to expose the relationship between
    WIP, bottlenecks, cycle time, and throughput.
    """

    def __init__(self) -> None:
        self.clock = datetime(2026, 10, 19, 9, 0)
        self.board = KanbanBoard(
            KanbanPolicy(
                wip_limits={
                    Column.DEVELOPMENT: 3,
                    Column.REVIEW: 2,
                    Column.TESTING: 2,
                }
            )
        )

    def seed(self) -> None:
        titles = [
            ("API pagination", 2),
            ("Authentication audit", 1),
            ("Cache invalidation", 3),
            ("Database index review", 2),
            ("Observability dashboard", 4),
            ("Export reliability", 3),
            ("Rate-limit policy", 2),
        ]

        for index, (title, priority) in enumerate(titles, start=1):
            created = self.clock - timedelta(hours=12 - index)
            self.board.add_item(
                WorkItem(
                    key=f"ENG-{index:03d}",
                    title=title,
                    priority=priority,
                    created_at=created,
                )
            )

    def run(self) -> None:
        self.seed()

        print("Initial board:", self.board.snapshot())

        # Pull only as much development work as the development WIP limit allows.
        for _ in range(3):
            self.board.pull_next(
                Column.BACKLOG,
                Column.DEVELOPMENT,
                self.clock,
            )

        print("After pulling development:", self.board.snapshot())

        # A fourth item cannot be started while Development is full.
        blocked = self.board.pull_next(
            Column.BACKLOG,
            Column.DEVELOPMENT,
            self.clock + timedelta(hours=1),
        )
        print("Fourth development pull:", blocked)

        # Moving work downstream creates capacity upstream.
        first_dev = next(
            item
            for item in self.board.items.values()
            if item.column == Column.DEVELOPMENT
        )
        self.board.move(
            first_dev.key,
            Column.REVIEW,
            self.clock + timedelta(hours=2),
        )

        self.board.pull_next(
            Column.BACKLOG,
            Column.DEVELOPMENT,
            self.clock + timedelta(hours=2),
        )

        print("After downstream pull:", self.board.snapshot())

        # Review becomes a bottleneck when its WIP limit is reached.
        development_items = [
            item
            for item in self.board.items.values()
            if item.column == Column.DEVELOPMENT
        ]
        for item in development_items[:2]:
            try:
                self.board.move(
                    item.key,
                    Column.REVIEW,
                    self.clock + timedelta(hours=3),
                )
            except RuntimeError as exc:
                print("Blocked movement:", exc)

        print("Bottleneck snapshot:", self.board.snapshot())
        print(
            "Constrained columns at capacity:",
            [column.value for column in self.board.blocked_columns()],
        )

        # Complete a review item through testing and done.
        review_item = next(
            item
            for item in self.board.items.values()
            if item.column == Column.REVIEW
        )
        self.board.move(
            review_item.key,
            Column.TESTING,
            self.clock + timedelta(hours=4),
        )
        self.board.move(
            review_item.key,
            Column.DONE,
            self.clock + timedelta(hours=5),
        )

        print("After completion:", self.board.snapshot())

        window_start = self.clock
        window_end = self.clock + timedelta(hours=6)
        throughput = FlowMetrics.throughput(
            self.board.completed,
            window_start,
            window_end,
        )
        print("Throughput in window:", throughput)

        for item in self.board.completed:
            print(
                item.key,
                "cycle=",
                FlowMetrics.cycle_time(item),
                "lead=",
                FlowMetrics.lead_time(item),
            )

    def demonstrate_policy_validation(self) -> None:
        try:
            for _ in range(4):
                self.board.pull_next(
                    Column.BACKLOG,
                    Column.DEVELOPMENT,
                    self.clock,
                )
        except RuntimeError as exc:
            print("Expected policy failure:", exc)


def estimate_little_law_cycle_time(
    average_wip: float,
    throughput_per_day: float,
) -> float:
    """
    Little's Law: WIP = throughput * cycle time.

    Returns cycle time in days when throughput is measured as completed items/day.
    """
    if average_wip < 0 or throughput_per_day <= 0:
        raise ValueError("WIP must be non-negative and throughput must be positive")
    return average_wip / throughput_per_day


def demonstrate_flow_math() -> None:
    wip = 6.0
    throughput = 2.0
    estimated_cycle = estimate_little_law_cycle_time(wip, throughput)
    print(
        f"Little's Law estimate: WIP={wip}, "
        f"throughput={throughput}/day, "
        f"cycle time={estimated_cycle:.2f} days"
    )


def demonstrate_aging_work() -> None:
    now = datetime(2026, 10, 19, 17, 0)
    items = [
        WorkItem(
            "OPS-101",
            "Incident runbook correction",
            1,
            now - timedelta(days=4),
            column=Column.REVIEW,
        ),
        WorkItem(
            "OPS-102",
            "Metrics label cleanup",
            3,
            now - timedelta(days=1),
            column=Column.DEVELOPMENT,
        ),
    ]

    for item in items:
        age = now - item.created_at
        print(f"{item.key}: age={age}, state={item.column.value}")

    # Aging work is a flow signal. Priority alone should not hide an item
    # that has remained in progress unusually long.
    oldest = max(items, key=lambda item: now - item.created_at)
    print("Oldest active item:", oldest.key)


def main() -> None:
    print("=== Kanban workflow visualization ===")
    simulator = KanbanSimulator()
    simulator.run()

    print("\n=== Flow measurement ===")
    demonstrate_flow_math()

    print("\n=== Aging work ===")
    demonstrate_aging_work()

    print("\n=== Operational principles ===")
    print("Pull work when downstream capacity exists.")
    print("Treat WIP limits as flow-control constraints, not target numbers.")
    print("Measure throughput and cycle time from completed work.")
    print("Investigate persistent full columns as possible bottlenecks.")
    print("Use explicit policies to make blocked movement visible.")


if __name__ == "__main__":
    main()
