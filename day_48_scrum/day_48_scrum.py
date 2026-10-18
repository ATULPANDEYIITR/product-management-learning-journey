"""
Scrum: an executable model of roles, events, artifacts, and sprint execution.

Run with:
    python scrum.py

The simulation models a product team delivering a prioritized backlog,
planning a sprint, coordinating daily work, reviewing increments, and
conducting a retrospective.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class WorkStatus(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class EventType(str, Enum):
    SPRINT_PLANNING = "Sprint Planning"
    DAILY_SCRUM = "Daily Scrum"
    SPRINT_REVIEW = "Sprint Review"
    RETROSPECTIVE = "Sprint Retrospective"


@dataclass(frozen=True)
class TeamMember:
    name: str
    accountabilities: str
    capacity_points: int = 0


@dataclass
class ProductBacklogItem:
    item_id: str
    title: str
    description: str
    priority: int
    estimate: int
    acceptance_criteria: list[str]
    status: WorkStatus = WorkStatus.TODO
    accepted: bool = False

    def __post_init__(self) -> None:
        if not self.item_id.strip() or not self.title.strip():
            raise ValueError("Backlog item ID and title are required.")
        if self.priority < 1:
            raise ValueError("Priority must be a positive integer.")
        if self.estimate < 0:
            raise ValueError("Estimate cannot be negative.")
        if not self.acceptance_criteria:
            raise ValueError("At least one acceptance criterion is required.")


@dataclass
class SprintGoal:
    statement: str

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("A Sprint Goal cannot be empty.")


@dataclass
class Sprint:
    number: int
    start_date: date
    duration_days: int
    goal: Optional[SprintGoal] = None
    selected_items: list[ProductBacklogItem] = field(default_factory=list)
    impediments: list[str] = field(default_factory=list)
    daily_scrum_count: int = 0
    review_completed: bool = False
    retrospective_completed: bool = False
    closed: bool = False

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError("Sprint number must be positive.")
        if not 1 <= self.duration_days <= 30:
            raise ValueError("This simulation permits sprints of 1-30 days.")

    @property
    def end_date(self) -> date:
        return self.start_date + timedelta(days=self.duration_days - 1)

    @property
    def committed_points(self) -> int:
        return sum(item.estimate for item in self.selected_items)

    @property
    def completed_points(self) -> int:
        return sum(
            item.estimate
            for item in self.selected_items
            if item.status == WorkStatus.DONE and item.accepted
        )


@dataclass
class ScrumArtifacts:
    product_backlog: list[ProductBacklogItem]
    sprint_backlog: list[ProductBacklogItem] = field(default_factory=list)
    increment: list[ProductBacklogItem] = field(default_factory=list)


class ScrumTeam:
    """
    A small Scrum simulation.

    Accountabilities are kept distinct: the Product Owner maximizes
    product value, the Scrum Master supports Scrum effectiveness, and
    Developers create a usable Increment.
    """

    def __init__(
        self,
        product_owner: TeamMember,
        scrum_master: TeamMember,
        developers: list[TeamMember],
        product_name: str,
        backlog: list[ProductBacklogItem],
    ) -> None:
        if not product_name.strip():
            raise ValueError("Product name is required.")
        if not developers:
            raise ValueError("A Scrum Team needs Developers.")
        names = [
            product_owner.name,
            scrum_master.name,
            *(developer.name for developer in developers),
        ]
        if any(not name.strip() for name in names):
            raise ValueError("Team member names cannot be empty.")
        if len(set(names)) != len(names):
            raise ValueError("Each team member must have a distinct name.")
        if any(member.capacity_points < 0 for member in developers):
            raise ValueError("Developer capacity cannot be negative.")

        self.product_owner = product_owner
        self.scrum_master = scrum_master
        self.developers = developers
        self.product_name = product_name
        self.artifacts = ScrumArtifacts(product_backlog=backlog)
        self.current_sprint: Optional[Sprint] = None
        self.events: list[dict] = []
        self.retrospective_actions: list[str] = []

        ids = [item.item_id for item in backlog]
        if len(set(ids)) != len(ids):
            raise ValueError("Product backlog item IDs must be unique.")

    def log_event(self, event_type: EventType, details: str) -> None:
        self.events.append(
            {
                "event": event_type.value,
                "details": details,
                "date": date.today().isoformat(),
            }
        )

    def refine_backlog(self) -> None:
        """Keep the backlog ordered by priority, with lower values first."""
        self.artifacts.product_backlog.sort(
            key=lambda item: (item.priority, item.item_id)
        )
        print("\nProduct Backlog Refinement")
        for item in self.artifacts.product_backlog:
            print(
                f"{item.item_id}: {item.title} | "
                f"priority={item.priority} | estimate={item.estimate}"
            )

    def plan_sprint(
        self,
        sprint_number: int,
        start_date: date,
        duration_days: int,
        goal_text: str,
        available_capacity: Optional[int] = None,
    ) -> Sprint:
        """Select the highest-priority feasible work for a Sprint Goal."""
        if self.current_sprint and not self.current_sprint.closed:
            raise RuntimeError("Close the current sprint before planning another.")

        goal = SprintGoal(goal_text)
        sprint = Sprint(sprint_number, start_date, duration_days, goal)

        capacity = (
            sum(member.capacity_points for member in self.developers)
            if available_capacity is None
            else available_capacity
        )
        if capacity < 0:
            raise ValueError("Sprint capacity cannot be negative.")

        remaining = capacity
        candidates = sorted(
            (
                item
                for item in self.artifacts.product_backlog
                if item.status == WorkStatus.TODO
            ),
            key=lambda item: (item.priority, item.item_id),
        )

        # Selection is a planning aid, not a guarantee of delivery.
        for item in candidates:
            if item.estimate <= remaining:
                sprint.selected_items.append(item)
                remaining -= item.estimate

        self.current_sprint = sprint
        self.artifacts.sprint_backlog = list(sprint.selected_items)
        self.log_event(
            EventType.SPRINT_PLANNING,
            f"Goal: {goal.statement}; "
            f"selected {len(sprint.selected_items)} items.",
        )

        print(f"\nSprint {sprint.number} Planning")
        print(f"Goal: {goal.statement}")
        print(f"Dates: {sprint.start_date} to {sprint.end_date}")
        print(f"Capacity: {capacity} points")
        print(f"Selected: {sprint.committed_points} points")
        for item in sprint.selected_items:
            print(f"  {item.item_id}: {item.title} ({item.estimate} points)")
        return sprint

    def start_work(self, item_id: str) -> None:
        sprint = self._require_active_sprint()
        item = self._find_sprint_item(sprint, item_id)
        if item.status != WorkStatus.TODO:
            raise RuntimeError(f"{item_id} is not in the To Do state.")
        item.status = WorkStatus.IN_PROGRESS
        self.log_event(EventType.DAILY_SCRUM, f"Started {item_id}.")

    def complete_work(self, item_id: str) -> None:
        sprint = self._require_active_sprint()
        item = self._find_sprint_item(sprint, item_id)
        if item.status != WorkStatus.IN_PROGRESS:
            raise RuntimeError(f"{item_id} must be in progress before completion.")
        item.status = WorkStatus.DONE
        self.log_event(EventType.DAILY_SCRUM, f"Completed implementation of {item_id}.")

    def daily_scrum(
        self,
        date_of_event: date,
        progress: dict[str, str],
        impediments: Optional[list[str]] = None,
    ) -> None:
        """Inspect progress toward the Sprint Goal and adapt the plan."""
        sprint = self._require_active_sprint()
        if not sprint.start_date <= date_of_event <= sprint.end_date:
            raise ValueError("Daily Scrum date must fall within the sprint.")

        for item_id, action in progress.items():
            item = self._find_sprint_item(sprint, item_id)
            if action == "start":
                if item.status != WorkStatus.TODO:
                    raise RuntimeError(f"{item_id} cannot be started from {item.status}.")
                item.status = WorkStatus.IN_PROGRESS
            elif action == "finish":
                if item.status != WorkStatus.IN_PROGRESS:
                    raise RuntimeError(f"{item_id} must be in progress to finish.")
                item.status = WorkStatus.DONE
            elif action == "blocked":
                message = f"{item_id}: blocked"
                if message not in sprint.impediments:
                    sprint.impediments.append(message)
            else:
                raise ValueError(f"Unsupported action: {action}")

        sprint.daily_scrum_count += 1
        for impediment in impediments or []:
            if impediment.strip() and impediment not in sprint.impediments:
                sprint.impediments.append(impediment)

        done = sum(item.status == WorkStatus.DONE for item in sprint.selected_items)
        self.log_event(
            EventType.DAILY_SCRUM,
            f"{date_of_event}: {done}/{len(sprint.selected_items)} items implemented.",
        )
        print(
            f"Daily Scrum on {date_of_event}: "
            f"{done}/{len(sprint.selected_items)} items implemented."
        )
        if sprint.impediments:
            print("Impediments:", "; ".join(sprint.impediments))

    def sprint_review(self, stakeholder_feedback: list[str]) -> None:
        """Inspect the Increment with stakeholders and adapt the Product Backlog."""
        sprint = self._require_active_sprint()
        if sprint.review_completed:
            raise RuntimeError("Sprint Review has already been recorded.")

        for item in sprint.selected_items:
            if item.status == WorkStatus.DONE:
                item.accepted = True
                self.artifacts.increment.append(item)

        sprint.review_completed = True
        feedback = "; ".join(stakeholder_feedback) or "No additional feedback."
        self.log_event(
            EventType.SPRINT_REVIEW,
            f"Accepted {sprint.completed_points} points. Feedback: {feedback}",
        )

        print("\nSprint Review")
        print(f"Accepted work: {sprint.completed_points}/{sprint.committed_points} points")
        print(f"Stakeholder feedback: {feedback}")

        # Unfinished items remain in the Product Backlog for future ordering.
        for item in sprint.selected_items:
            if item.status != WorkStatus.DONE:
                item.status = WorkStatus.TODO
                item.accepted = False
                if item in self.artifacts.sprint_backlog:
                    self.artifacts.sprint_backlog.remove(item)

    def retrospective(self, actions: list[str]) -> None:
        """Inspect how the team worked and record specific improvements."""
        sprint = self._require_active_sprint()
        if not sprint.review_completed:
            raise RuntimeError("Conduct the Sprint Review before the retrospective.")
        if sprint.retrospective_completed:
            raise RuntimeError("Retrospective has already been recorded.")

        clean_actions = [action.strip() for action in actions if action.strip()]
        self.retrospective_actions.extend(clean_actions)
        sprint.retrospective_completed = True
        self.log_event(
            EventType.RETROSPECTIVE,
            "Improvement actions: " + "; ".join(clean_actions),
        )
        print("\nSprint Retrospective")
        for action in clean_actions:
            print(f"- {action}")

    def close_sprint(self) -> None:
        sprint = self._require_active_sprint()
        if not sprint.review_completed or not sprint.retrospective_completed:
            raise RuntimeError("Review and retrospective must be completed before closure.")
        sprint.closed = True
        print(
            f"\nSprint {sprint.number} closed. "
            f"Accepted: {sprint.completed_points} points."
        )

    def _require_active_sprint(self) -> Sprint:
        if self.current_sprint is None or self.current_sprint.closed:
            raise RuntimeError("No active sprint.")
        return self.current_sprint

    @staticmethod
    def _find_sprint_item(sprint: Sprint, item_id: str) -> ProductBacklogItem:
        for item in sprint.selected_items:
            if item.item_id == item_id:
                return item
        raise KeyError(f"{item_id} is not in the Sprint Backlog.")

    def report(self) -> None:
        print("\nProduct Delivery Report")
        print(f"Product: {self.product_name}")
        print(f"Product Owner: {self.product_owner.name}")
        print(f"Scrum Master: {self.scrum_master.name}")
        print("Developers:", ", ".join(d.name for d in self.developers))
        print(f"Backlog items: {len(self.artifacts.product_backlog)}")
        print(f"Increment items: {len(self.artifacts.increment)}")
        print(f"Recorded events: {len(self.events)}")


def demonstrate_invalid_operations(team: ScrumTeam) -> None:
    """Show how state validation prevents inconsistent work."""
    print("\nValidation Examples")
    try:
        team.start_work("UNKNOWN")
    except (KeyError, RuntimeError) as error:
        print(f"Expected validation failure: {error}")


def main() -> None:
    product_owner = TeamMember("Maya", "Maximize product value")
    scrum_master = TeamMember("Arjun", "Support Scrum effectiveness")
    developers = [
        TeamMember("Neha", "Develop a usable Increment", 8),
        TeamMember("Kabir", "Develop a usable Increment", 7),
        TeamMember("Sara", "Develop a usable Increment", 5),
    ]

    backlog = [
        ProductBacklogItem(
            "PAY-101",
            "Validate payment requests",
            "Reject malformed payment requests before processing.",
            1,
            5,
            ["Invalid account IDs are rejected", "Valid requests are accepted"],
        ),
        ProductBacklogItem(
            "PAY-102",
            "Record payment audit events",
            "Persist payment outcomes for audit investigation.",
            2,
            8,
            ["Successful payments are recorded", "Failures include a reason"],
        ),
        ProductBacklogItem(
            "PAY-103",
            "Expose transaction status",
            "Provide a customer-facing transaction status endpoint.",
            3,
            5,
            ["Authorized users can retrieve status"],
        ),
        ProductBacklogItem(
            "PAY-104",
            "Improve retry visibility",
            "Show retry attempts in operational monitoring.",
            4,
            3,
            ["Retry counts are visible to operators"],
        ),
    ]

    team = ScrumTeam(
        product_owner,
        scrum_master,
        developers,
        "Payment Reliability Platform",
        backlog,
    )

    team.refine_backlog()

    sprint = team.plan_sprint(
        sprint_number=1,
        start_date=date(2026, 10, 19),
        duration_days=10,
        goal_text="Make payment request validation reliable and auditable.",
    )

    if sprint.selected_items:
        first_item = sprint.selected_items[0]
        team.start_work(first_item.item_id)

        team.daily_scrum(
            date_of_event=sprint.start_date,
            progress={first_item.item_id: "finish"},
            impediments=["Integration test environment needs stable test data"],
        )

    # Simulate unfinished work and demonstrate realistic partial delivery.
    if len(sprint.selected_items) > 1:
        second_item = sprint.selected_items[1]
        team.start_work(second_item.item_id)

    team.sprint_review(
        [
            "Request validation meets the agreed acceptance criteria.",
            "Audit-event coverage should be checked for failure scenarios.",
        ]
    )

    demonstrate_invalid_operations(team)

    team.retrospective(
        [
            "Prepare representative payment failure fixtures before sprint work.",
            "Review audit-event acceptance criteria with stakeholders earlier.",
        ]
    )
    team.close_sprint()
    team.report()


if __name__ == "__main__":
    main()
