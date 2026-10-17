"""
Agile Fundamentals: Principles, Iterative Development, and Incremental Delivery.

A self-contained simulation of an Agile software delivery team building a
customer-support platform. The implementation demonstrates Agile principles,
backlog prioritization, iteration planning, incremental delivery, feedback,
acceptance criteria, and retrospective improvement.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class WorkStatus(Enum):
    BACKLOG = "Backlog"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"


@dataclass
class UserStory:
    story_id: str
    title: str
    user_value: int
    effort: int
    acceptance_criteria: list[str]
    dependencies: list[str] = field(default_factory=list)
    status: WorkStatus = WorkStatus.BACKLOG
    delivered_iteration: int | None = None
    feedback: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.story_id.strip() or not self.title.strip():
            raise ValueError("Story ID and title cannot be empty.")
        if self.user_value < 1 or self.effort < 1:
            raise ValueError("Value and effort must be positive.")
        if not self.acceptance_criteria:
            raise ValueError("Every story requires acceptance criteria.")

    @property
    def priority_score(self) -> float:
        """A simple planning heuristic, not a substitute for team judgment."""
        return self.user_value / self.effort

    def accept(self, iteration: int) -> None:
        if self.status not in {WorkStatus.REVIEW, WorkStatus.IN_PROGRESS}:
            raise ValueError(f"Cannot accept a story in {self.status.value}.")
        self.status = WorkStatus.DONE
        self.delivered_iteration = iteration

    def add_feedback(self, comment: str) -> None:
        comment = comment.strip()
        if not comment:
            raise ValueError("Feedback cannot be empty.")
        self.feedback.append(comment)


@dataclass
class Iteration:
    number: int
    goal: str
    capacity: int
    planned_stories: list[UserStory] = field(default_factory=list)
    completed_stories: list[UserStory] = field(default_factory=list)
    committed_effort: int = 0

    def plan(self, candidates: Iterable[UserStory]) -> list[UserStory]:
        """Select work within capacity while respecting dependencies."""
        if self.planned_stories:
            raise ValueError("An iteration can only be planned once.")

        selected_ids: set[str] = set()
        candidates = list(candidates)

        # Higher value-to-effort stories are considered first.
        ordered = sorted(
            candidates,
            key=lambda story: (story.priority_score, story.user_value),
            reverse=True,
        )

        for story in ordered:
            if story.status not in {WorkStatus.BACKLOG, WorkStatus.READY}:
                continue

            dependencies_satisfied = all(
                dependency in selected_ids
                or any(
                    item.story_id == dependency
                    and item.status == WorkStatus.DONE
                    for item in candidates
                )
                for dependency in story.dependencies
            )
            if not dependencies_satisfied:
                continue

            if self.committed_effort + story.effort > self.capacity:
                continue

            self.planned_stories.append(story)
            self.committed_effort += story.effort
            selected_ids.add(story.story_id)
            story.status = WorkStatus.READY

        return self.planned_stories

    def start_story(self, story_id: str) -> UserStory:
        story = self._find_planned(story_id)
        if story.status != WorkStatus.READY:
            raise ValueError("Only ready stories can start.")
        story.status = WorkStatus.IN_PROGRESS
        return story

    def submit_for_review(self, story_id: str) -> UserStory:
        story = self._find_planned(story_id)
        if story.status != WorkStatus.IN_PROGRESS:
            raise ValueError("Only in-progress stories can enter review.")
        story.status = WorkStatus.REVIEW
        return story

    def complete_story(self, story_id: str) -> UserStory:
        story = self._find_planned(story_id)
        story.accept(self.number)
        self.completed_stories.append(story)
        return story

    def _find_planned(self, story_id: str) -> UserStory:
        for story in self.planned_stories:
            if story.story_id == story_id:
                return story
        raise KeyError(f"Story {story_id} is not in this iteration.")

    @property
    def completion_rate(self) -> float:
        if not self.planned_stories:
            return 0.0
        return len(self.completed_stories) / len(self.planned_stories) * 100


class AgileTeam:
    def __init__(self, stories: Iterable[UserStory]) -> None:
        self.stories = {story.story_id: story for story in stories}
        if len(self.stories) != len(list(self.stories.values())):
            raise ValueError("Story IDs must be unique.")
        self.iterations: list[Iteration] = []

    def create_iteration(self, goal: str, capacity: int) -> Iteration:
        if capacity < 1:
            raise ValueError("Iteration capacity must be positive.")
        iteration = Iteration(len(self.iterations) + 1, goal, capacity)
        self.iterations.append(iteration)
        return iteration

    def add_story_from_feedback(
        self, story: UserStory, source_story_id: str
    ) -> None:
        if story.story_id in self.stories:
            raise ValueError("Story ID already exists.")
        if source_story_id not in self.stories:
            raise KeyError("Feedback source story does not exist.")
        self.stories[source_story_id].add_feedback(
            f"Created follow-up story: {story.title}"
        )
        self.stories[story.story_id] = story

    def backlog_report(self) -> None:
        print("\nPRODUCT BACKLOG")
        print("-" * 76)
        for story in sorted(
            self.stories.values(),
            key=lambda item: item.priority_score,
            reverse=True,
        ):
            print(
                f"{story.story_id:5} | {story.title:34} | "
                f"value={story.user_value:2} | effort={story.effort:2} | "
                f"score={story.priority_score:.2f} | {story.status.value}"
            )

    def delivery_report(self) -> None:
        print("\nITERATION DELIVERY")
        print("-" * 76)
        for iteration in self.iterations:
            delivered_value = sum(
                story.user_value for story in iteration.completed_stories
            )
            print(
                f"Iteration {iteration.number}: {iteration.goal}\n"
                f"  Planned effort: {iteration.committed_effort}/"
                f"{iteration.capacity}\n"
                f"  Completed: {len(iteration.completed_stories)}/"
                f"{len(iteration.planned_stories)}\n"
                f"  Completion rate: {iteration.completion_rate:.1f}%\n"
                f"  Delivered value points: {delivered_value}"
            )


def demonstrate_agile_delivery() -> None:
    stories = [
        UserStory(
            "US-101",
            "View support requests",
            9,
            3,
            ["A customer sees their own requests", "Requests show current status"],
        ),
        UserStory(
            "US-102",
            "Submit a support request",
            10,
            5,
            ["A customer can submit a subject and description"],
        ),
        UserStory(
            "US-103",
            "Search support requests",
            6,
            3,
            ["Search matches request subject", "Empty results show a clear message"],
            dependencies=["US-101"],
        ),
        UserStory(
            "US-104",
            "Receive request confirmation",
            8,
            2,
            ["A confirmation appears after successful submission"],
            dependencies=["US-102"],
        ),
        UserStory(
            "US-105",
            "Filter requests by status",
            7,
            3,
            ["Customers can filter open and resolved requests"],
            dependencies=["US-101"],
        ),
        UserStory(
            "US-106",
            "Export support history",
            4,
            5,
            ["Authorized staff can export request history"],
        ),
    ]

    team = AgileTeam(stories)
    team.backlog_report()

    first = team.create_iteration(
        "Give customers visibility into their support requests", capacity=8
    )
    first.plan(team.stories.values())

    print(f"\nIteration {first.number}: {first.goal}")
    for story in first.planned_stories:
        print(f"  Planned: {story.story_id} - {story.title}")

    # Simulate actual delivery instead of treating a plan as completed work.
    for story in first.planned_stories:
        first.start_story(story.story_id)
        first.submit_for_review(story.story_id)
        first.complete_story(story.story_id)

    delivered = team.stories["US-101"]
    delivered.add_feedback(
        "Customers want a clear indication of recently updated requests."
    )
    print("\nCustomer feedback:", delivered.feedback[-1])

    follow_up = UserStory(
        "US-107",
        "Show last updated time",
        8,
        2,
        ["Each request displays its latest update time"],
        dependencies=["US-101"],
    )
    team.add_story_from_feedback(follow_up, "US-101")

    second = team.create_iteration(
        "Improve request submission and provide timely feedback", capacity=8
    )
    second.plan(
        story
        for story in team.stories.values()
        if story.status in {WorkStatus.BACKLOG, WorkStatus.READY}
    )

    print(f"\nIteration {second.number}: {second.goal}")
    for story in second.planned_stories:
        print(f"  Planned: {story.story_id} - {story.title}")

    # A dependency may be satisfied by work delivered in an earlier iteration.
    for story in second.planned_stories:
        second.start_story(story.story_id)
        second.submit_for_review(story.story_id)
        second.complete_story(story.story_id)

    team.delivery_report()
    team.backlog_report()

    print("\nRETROSPECTIVE")
    print("-" * 76)
    print("Observation: Completed work produced usable customer functionality.")
    print("Feedback: Customer observations changed backlog priorities.")
    print("Improvement: Estimate work with the team and reserve capacity for")
    print("testing, review, integration, and unexpected complexity.")
    print(
        "Caution: Value divided by effort is a planning aid, not a universal "
        "prioritization formula."
    )


if __name__ == "__main__":
    demonstrate_agile_delivery()
