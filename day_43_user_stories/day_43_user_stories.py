"""
User Stories: From Beginner Concepts to Advanced Backlog Engineering

This executable module demonstrates:
- User story structure and user personas.
- User, need, and value relationships.
- Testable acceptance criteria using Given-When-Then.
- INVEST quality assessment.
- Story splitting, dependency handling, prioritization, estimation,
  backlog validation, and release readiness.

Run with:
    python user_stories.py

Only the Python standard library is required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable
import json
import re


class StoryStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class CriterionType(str, Enum):
    FUNCTIONAL = "functional"
    VALIDATION = "validation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    ERROR_HANDLING = "error_handling"


@dataclass(frozen=True)
class Persona:
    name: str
    role: str
    context: str
    primary_goal: str
    constraints: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors = []
        for attribute in ("name", "role", "context", "primary_goal"):
            if not getattr(self, attribute).strip():
                errors.append(f"Persona field '{attribute}' cannot be empty.")
        return errors


@dataclass(frozen=True)
class AcceptanceCriterion:
    given: str
    when: str
    then: str
    criterion_type: CriterionType = CriterionType.FUNCTIONAL

    def validate(self) -> list[str]:
        errors = []
        for attribute in ("given", "when", "then"):
            value = getattr(self, attribute).strip()
            if not value:
                errors.append(f"Acceptance criterion '{attribute}' is empty.")
            elif len(value) < 8:
                errors.append(
                    f"Acceptance criterion '{attribute}' needs more detail."
                )
        return errors

    def as_dict(self) -> dict[str, str]:
        return {
            "given": self.given,
            "when": self.when,
            "then": self.then,
            "type": self.criterion_type.value,
        }


@dataclass
class UserStory:
    story_id: str
    title: str
    persona: Persona
    need: str
    value: str
    acceptance_criteria: list[AcceptanceCriterion]
    story_points: int | None = None
    dependencies: set[str] = field(default_factory=set)
    status: StoryStatus = StoryStatus.DRAFT
    priority: int = 3
    independent: bool = True
    negotiable: bool = True
    valuable: bool = True
    estimable: bool = True
    small: bool = True
    testable: bool = True
    labels: set[str] = field(default_factory=set)

    def statement(self) -> str:
        return (
            f"As a {self.persona.role}, "
            f"I want {self.need}, "
            f"so that {self.value}."
        )

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not re.fullmatch(r"[A-Z]+-\d+", self.story_id):
            errors.append("Story ID must use a format such as PAY-101.")

        for attribute in ("title", "need", "value"):
            if not getattr(self, attribute).strip():
                errors.append(f"'{attribute}' cannot be empty.")

        errors.extend(self.persona.validate())

        if not self.acceptance_criteria:
            errors.append("At least one acceptance criterion is required.")

        for index, criterion in enumerate(self.acceptance_criteria, start=1):
            errors.extend(
                f"Criterion {index}: {error}"
                for error in criterion.validate()
            )

        if self.story_points is not None and self.story_points <= 0:
            errors.append("Story points must be positive when provided.")

        if not 1 <= self.priority <= 5:
            errors.append("Priority must be between 1 and 5.")

        if self.story_id in self.dependencies:
            errors.append("A story cannot depend on itself.")

        if self.status == StoryStatus.READY:
            if not all(self.invest_scores().values()):
                errors.append("Story is marked ready but fails INVEST.")
            if not self.acceptance_criteria:
                errors.append("Ready stories require acceptance criteria.")

        return errors

    def invest_scores(self) -> dict[str, bool]:
        return {
            "Independent": self.independent,
            "Negotiable": self.negotiable,
            "Valuable": self.valuable,
            "Estimable": self.estimable,
            "Small": self.small,
            "Testable": self.testable,
        }

    def invest_report(self) -> dict[str, bool]:
        return self.invest_scores()

    def is_ready(self) -> bool:
        return (
            not self.validate()
            and all(self.invest_scores().values())
            and self.status in {StoryStatus.DRAFT, StoryStatus.READY}
        )

    def to_dict(self) -> dict:
        return {
            "id": self.story_id,
            "title": self.title,
            "statement": self.statement(),
            "persona": {
                "name": self.persona.name,
                "role": self.persona.role,
                "context": self.persona.context,
                "primary_goal": self.persona.primary_goal,
            },
            "acceptance_criteria": [
                criterion.as_dict()
                for criterion in self.acceptance_criteria
            ],
            "story_points": self.story_points,
            "dependencies": sorted(self.dependencies),
            "status": self.status.value,
            "priority": self.priority,
            "invest": self.invest_report(),
            "validation_errors": self.validate(),
        }


def assess_invest(story: UserStory) -> dict[str, str]:
    """
    INVEST is a quality checklist, not a mathematical guarantee.
    Each result identifies the condition that needs attention.
    """
    descriptions = {
        "Independent": (
            "Can be delivered without requiring another story first."
        ),
        "Negotiable": (
            "Describes an outcome without prematurely prescribing implementation."
        ),
        "Valuable": (
            "Produces a meaningful outcome for a user or stakeholder."
        ),
        "Estimable": (
            "Has enough context and acceptance criteria for an estimate."
        ),
        "Small": (
            "Can be completed within the team's normal delivery window."
        ),
        "Testable": (
            "Provides observable outcomes that can be verified."
        ),
    }

    return {
        name: (
            f"PASS: {descriptions[name]}"
            if passed
            else f"REVIEW: {descriptions[name]}"
        )
        for name, passed in story.invest_scores().items()
    }


def dependency_order(stories: Iterable[UserStory]) -> list[str]:
    """
    Topological sorting detects cycles and returns dependencies before
    the stories that require them.
    """
    story_map = {story.story_id: story for story in stories}

    if not story_map:
        return []

    for story in story_map.values():
        unknown = story.dependencies - story_map.keys()
        if unknown:
            raise ValueError(
                f"{story.story_id} has unknown dependencies: {sorted(unknown)}"
            )

    indegree = {story_id: 0 for story_id in story_map}
    dependents = {story_id: [] for story_id in story_map}

    for story in story_map.values():
        indegree[story.story_id] = len(story.dependencies)
        for dependency in story.dependencies:
            dependents[dependency].append(story.story_id)

    ready = sorted(
        story_id for story_id, degree in indegree.items() if degree == 0
    )
    result = []

    while ready:
        current = ready.pop(0)
        result.append(current)

        for dependent in sorted(dependents[current]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
                ready.sort()

    if len(result) != len(story_map):
        raise ValueError("Dependency cycle detected in the story backlog.")

    return result


def split_story(
    parent_id: str,
    child_stories: list[UserStory],
    minimum_children: int = 2,
) -> None:
    """
    Splitting should produce independently understandable outcomes.
    This function validates the proposed child stories without assuming
    that splitting automatically improves their quality.
    """
    if len(child_stories) < minimum_children:
        raise ValueError("A split requires at least two child stories.")

    identifiers = [story.story_id for story in child_stories]

    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Child story IDs must be unique.")

    if parent_id in identifiers:
        raise ValueError("A child cannot reuse the parent story ID.")

    errors = {
        story.story_id: story.validate()
        for story in child_stories
        if story.validate()
    }

    if errors:
        raise ValueError(f"Invalid child stories: {errors}")


def prioritize(story: UserStory) -> tuple[int, int, str]:
    """
    Lower numeric priority means greater urgency.
    Story points are used only as a tie-breaker, not as business value.
    """
    size = story.story_points if story.story_points is not None else 10
    return story.priority, size, story.story_id


def backlog_report(stories: list[UserStory]) -> dict:
    identifiers = [story.story_id for story in stories]
    duplicate_ids = sorted(
        identifier
        for identifier in set(identifiers)
        if identifiers.count(identifier) > 1
    )

    report = {
        "story_count": len(stories),
        "duplicate_ids": duplicate_ids,
        "stories": [],
    }

    for story in sorted(stories, key=prioritize):
        report["stories"].append({
            "id": story.story_id,
            "title": story.title,
            "status": story.status.value,
            "priority": story.priority,
            "ready": story.is_ready(),
            "errors": story.validate(),
        })

    return report


def example_backlog() -> list[UserStory]:
    customer = Persona(
        name="Riya",
        role="registered customer",
        context="shopping through a mobile commerce application",
        primary_goal="complete a purchase with confidence",
        constraints=("limited mobile connectivity",),
    )

    support_agent = Persona(
        name="Kabir",
        role="customer support agent",
        context="investigating failed checkout attempts",
        primary_goal="identify why an order was not created",
    )

    address_story = UserStory(
        story_id="PAY-101",
        title="Validate the delivery address",
        persona=customer,
        need="save a delivery address with all required fields",
        value="my order can be delivered to the correct location",
        acceptance_criteria=[
            AcceptanceCriterion(
                given="I am entering a delivery address",
                when="I submit all required valid address fields",
                then="the address is saved and available at checkout",
                criterion_type=CriterionType.VALIDATION,
            ),
            AcceptanceCriterion(
                given="the postal code is missing",
                when="I attempt to save the address",
                then="the form identifies the missing field and saves nothing",
                criterion_type=CriterionType.ERROR_HANDLING,
            ),
        ],
        story_points=3,
        priority=1,
        status=StoryStatus.READY,
    )

    checkout_story = UserStory(
        story_id="PAY-102",
        title="Submit an order securely",
        persona=customer,
        need="confirm an order after reviewing the final amount",
        value="I know what I will pay before placing the order",
        acceptance_criteria=[
            AcceptanceCriterion(
                given="my cart and delivery address are valid",
                when="I confirm the order",
                then="one order is created and a confirmation is displayed",
            ),
            AcceptanceCriterion(
                given="the order submission is retried after a timeout",
                when="the same idempotency key is reused",
                then="the system returns the original order without duplication",
                criterion_type=CriterionType.SECURITY,
            ),
        ],
        story_points=5,
        dependencies={"PAY-101"},
        priority=1,
        status=StoryStatus.READY,
    )

    diagnostic_story = UserStory(
        story_id="PAY-103",
        title="Inspect failed checkout attempts",
        persona=support_agent,
        need="view a checkout failure reason using an order reference",
        value="I can resolve customer problems without guessing",
        acceptance_criteria=[
            AcceptanceCriterion(
                given="a checkout attempt failed",
                when="an authorized agent searches its reference",
                then="the system displays the recorded failure category",
            ),
            AcceptanceCriterion(
                given="an agent lacks permission to inspect checkout data",
                when="the agent requests a diagnostic record",
                then="access is denied and the attempt is audited",
                criterion_type=CriterionType.SECURITY,
            ),
        ],
        story_points=3,
        priority=2,
        status=StoryStatus.DRAFT,
    )

    return [address_story, checkout_story, diagnostic_story]


def demonstrate() -> None:
    stories = example_backlog()

    print("USER STORY STATEMENTS")
    for story in stories:
        print(f"\n{story.story_id}: {story.statement()}")

    print("\nINVEST ASSESSMENT")
    for story in stories:
        print(f"\n{story.story_id}")
        for criterion, result in assess_invest(story).items():
            print(f"  {criterion}: {result}")

    print("\nACCEPTANCE CRITERIA")
    for story in stories:
        print(f"\n{story.story_id}: {story.title}")
        for index, criterion in enumerate(story.acceptance_criteria, start=1):
            print(f"  Criterion {index}")
            print(f"    Given: {criterion.given}")
            print(f"    When:  {criterion.when}")
            print(f"    Then:  {criterion.then}")

    print("\nDEPENDENCY ORDER")
    for story_id in dependency_order(stories):
        print(f"  {story_id}")

    print("\nBACKLOG REPORT")
    print(json.dumps(backlog_report(stories), indent=2))

    # A dependency cycle is a structural backlog defect, not a valid order.
    cyclic_a = UserStory(
        "OPS-101", "A", stories[0].persona, "do A", "achieve A",
        [AcceptanceCriterion("valid state exists", "A is requested",
                             "A completes successfully")],
        dependencies={"OPS-102"},
    )
    cyclic_b = UserStory(
        "OPS-102", "B", stories[0].persona, "do B", "achieve B",
        [AcceptanceCriterion("valid state exists", "B is requested",
                             "B completes successfully")],
        dependencies={"OPS-101"},
    )

    try:
        dependency_order([cyclic_a, cyclic_b])
    except ValueError as error:
        print(f"\nExpected dependency validation: {error}")


if __name__ == "__main__":
    demonstrate()
