from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable
import json
import re
import statistics
import time


class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class IssueType(str, Enum):
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    INFORMATION_ARCHITECTURE = "information_architecture"
    INTERACTION = "interaction"
    UI = "ui"


@dataclass(frozen=True)
class User:
    user_id: str
    name: str
    keyboard_only: bool = False
    screen_reader: bool = False
    reduced_motion: bool = False
    low_vision: bool = False


@dataclass
class Screen:
    screen_id: str
    title: str
    primary_action: str
    navigation_items: list[str]
    headings: list[str]
    interactive_elements: list[str]
    labels: dict[str, str]
    focus_order: list[str]
    color_contrast: dict[str, float]
    motion_enabled: bool = True


@dataclass
class UXIssue:
    issue_id: str
    issue_type: IssueType
    severity: Severity
    screen_id: str
    description: str
    recommendation: str
    status: str = "open"


@dataclass
class TaskResult:
    task: str
    completed: bool
    duration_seconds: float
    errors: int
    steps: int
    notes: list[str] = field(default_factory=list)


@dataclass
class UXSession:
    user: User
    results: list[TaskResult] = field(default_factory=list)

    @property
    def completion_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.completed for r in self.results) / len(self.results)

    @property
    def average_time(self) -> float:
        if not self.results:
            return 0.0
        return statistics.mean(r.duration_seconds for r in self.results)

    @property
    def error_rate(self) -> float:
        if not self.results:
            return 0.0
        total_steps = sum(r.steps for r in self.results)
        return sum(r.errors for r in self.results) / max(total_steps, 1)


class UXValidationError(ValueError):
    pass


class UXWorkbench:
    """
    A small UX evaluation engine covering:
    - information architecture
    - interaction design
    - usability testing
    - accessibility checks
    - UI consistency
    - quantitative task metrics
    """

    WCAG_AA_CONTRAST_NORMAL = 4.5
    WCAG_AA_CONTRAST_LARGE = 3.0

    def __init__(self) -> None:
        self.screens: dict[str, Screen] = {}
        self.issues: list[UXIssue] = []

    def add_screen(self, screen: Screen) -> None:
        if not screen.screen_id.strip():
            raise UXValidationError("Screen ID cannot be empty.")
        if screen.screen_id in self.screens:
            raise UXValidationError(f"Duplicate screen: {screen.screen_id}")
        if not screen.headings:
            raise UXValidationError(f"{screen.screen_id} requires at least one heading.")
        if not screen.primary_action.strip():
            raise UXValidationError(f"{screen.screen_id} requires a primary action.")
        self.screens[screen.screen_id] = screen

    def check_information_architecture(self) -> list[UXIssue]:
        issues: list[UXIssue] = []

        for screen in self.screens.values():
            if len(screen.navigation_items) > 7:
                issues.append(
                    UXIssue(
                        issue_id=f"IA-{screen.screen_id}-01",
                        issue_type=IssueType.INFORMATION_ARCHITECTURE,
                        severity=Severity.MINOR,
                        screen_id=screen.screen_id,
                        description="Primary navigation contains more than seven top-level items.",
                        recommendation="Group related destinations and reduce top-level choices.",
                    )
                )

            if screen.primary_action not in screen.interactive_elements:
                issues.append(
                    UXIssue(
                        issue_id=f"IA-{screen.screen_id}-02",
                        issue_type=IssueType.INTERACTION,
                        severity=Severity.MAJOR,
                        screen_id=screen.screen_id,
                        description="The declared primary action is not represented as an interactive element.",
                        recommendation="Expose the primary action as a clearly identifiable control.",
                    )
                )

        return issues

    def check_accessibility(self) -> list[UXIssue]:
        issues: list[UXIssue] = []

        for screen in self.screens.values():
            interactive = set(screen.interactive_elements)

            missing_focus = interactive - set(screen.focus_order)
            if missing_focus:
                issues.append(
                    UXIssue(
                        issue_id=f"A11Y-{screen.screen_id}-01",
                        issue_type=IssueType.ACCESSIBILITY,
                        severity=Severity.CRITICAL,
                        screen_id=screen.screen_id,
                        description=f"Interactive elements missing from keyboard focus order: {sorted(missing_focus)}.",
                        recommendation="Make every interactive control keyboard reachable in a logical order.",
                    )
                )

            for element in interactive:
                label = screen.labels.get(element, "").strip()
                if not label:
                    issues.append(
                        UXIssue(
                            issue_id=f"A11Y-{screen.screen_id}-{element}-LABEL",
                            issue_type=IssueType.ACCESSIBILITY,
                            severity=Severity.MAJOR,
                            screen_id=screen.screen_id,
                            description=f"Interactive element '{element}' has no accessible name.",
                            recommendation="Provide a visible label or an equivalent accessible name.",
                        )
                    )

            for token, ratio in screen.color_contrast.items():
                if ratio < self.WCAG_AA_CONTRAST_NORMAL:
                    issues.append(
                        UXIssue(
                            issue_id=f"A11Y-{screen.screen_id}-CONTRAST-{token}",
                            issue_type=IssueType.ACCESSIBILITY,
                            severity=Severity.MAJOR,
                            screen_id=screen.screen_id,
                            description=(
                                f"Contrast ratio for '{token}' is {ratio:.2f}, "
                                f"below the 4.5:1 normal-text threshold."
                            ),
                            recommendation="Increase foreground/background contrast or use a compliant alternative.",
                        )
                    )

        return issues

    def check_interaction_design(self) -> list[UXIssue]:
        issues: list[UXIssue] = []

        for screen in self.screens.values():
            if len(screen.focus_order) != len(set(screen.focus_order)):
                issues.append(
                    UXIssue(
                        issue_id=f"IX-{screen.screen_id}-01",
                        issue_type=IssueType.INTERACTION,
                        severity=Severity.MAJOR,
                        screen_id=screen.screen_id,
                        description="Focus order contains duplicate controls.",
                        recommendation="Define a deterministic, non-repeating interaction sequence.",
                    )
                )

            if screen.motion_enabled:
                issues.append(
                    UXIssue(
                        issue_id=f"IX-{screen.screen_id}-02",
                        issue_type=IssueType.INTERACTION,
                        severity=Severity.INFO,
                        screen_id=screen.screen_id,
                        description="Motion is enabled by default.",
                        recommendation="Respect user preferences such as reduced-motion settings.",
                    )
                )

        return issues

    def check_ui_consistency(self) -> list[UXIssue]:
        issues: list[UXIssue] = []

        action_names = {
            screen.primary_action.strip().lower()
            for screen in self.screens.values()
            if screen.primary_action.strip()
        }

        if len(action_names) > 1 and any(
            name in {"save", "submit", "confirm", "continue"} for name in action_names
        ):
            issues.append(
                UXIssue(
                    issue_id="UI-CONSISTENCY-01",
                    issue_type=IssueType.UI,
                    severity=Severity.MINOR,
                    screen_id="*",
                    description="Primary-action terminology varies between screens.",
                    recommendation="Use a consistent action vocabulary based on the user's intended outcome.",
                )
            )

        return issues

    def run_audit(self) -> list[UXIssue]:
        self.issues = (
            self.check_information_architecture()
            + self.check_accessibility()
            + self.check_interaction_design()
            + self.check_ui_consistency()
        )
        return self.issues

    @staticmethod
    def validate_task_result(result: TaskResult) -> None:
        if result.duration_seconds < 0:
            raise UXValidationError("Task duration cannot be negative.")
        if result.errors < 0 or result.steps <= 0:
            raise UXValidationError("Errors must be non-negative and steps must be positive.")
        if result.errors > result.steps:
            raise UXValidationError("Errors cannot exceed task steps.")

    def evaluate_session(self, session: UXSession) -> dict[str, float]:
        for result in session.results:
            self.validate_task_result(result)

        return {
            "completion_rate": round(session.completion_rate * 100, 2),
            "average_time_seconds": round(session.average_time, 2),
            "error_rate_percent": round(session.error_rate * 100, 2),
        }

    def export_report(self, path: str) -> None:
        report = {
            "screens": [
                {
                    "screen_id": s.screen_id,
                    "title": s.title,
                    "primary_action": s.primary_action,
                }
                for s in self.screens.values()
            ],
            "issues": [
                {
                    "id": i.issue_id,
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "screen": i.screen_id,
                    "description": i.description,
                    "recommendation": i.recommendation,
                    "status": i.status,
                }
                for i in self.issues
            ],
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=2)


def build_example_workbench() -> UXWorkbench:
    workbench = UXWorkbench()

    workbench.add_screen(
        Screen(
            screen_id="dashboard",
            title="Project Dashboard",
            primary_action="Create project",
            navigation_items=[
                "Projects",
                "Reports",
                "Teams",
                "Settings",
                "Activity",
                "Integrations",
                "Billing",
                "Help",
            ],
            headings=["Projects"],
            interactive_elements=[
                "Create project",
                "Open project",
                "Search",
                "Account menu",
            ],
            labels={
                "Create project": "Create project",
                "Open project": "Open project",
                "Search": "Search projects",
                "Account menu": "Account menu",
            },
            focus_order=[
                "Search",
                "Create project",
                "Open project",
                "Account menu",
            ],
            color_contrast={
                "body-text": 7.1,
                "muted-text": 3.4,
                "primary-button": 4.8,
            },
        )
    )

    workbench.add_screen(
        Screen(
            screen_id="project",
            title="Project Details",
            primary_action="Save",
            navigation_items=["Projects", "Reports", "Settings"],
            headings=["Project details", "Activity"],
            interactive_elements=[
                "Project name",
                "Save",
                "Archive",
            ],
            labels={
                "Project name": "Project name",
                "Save": "Save project",
                "Archive": "Archive project",
            },
            focus_order=[
                "Project name",
                "Save",
                "Archive",
            ],
            color_contrast={
                "body-text": 8.2,
                "primary-button": 5.1,
            },
            motion_enabled=False,
        )
    )

    return workbench


def build_test_session() -> UXSession:
    user = User(
        user_id="u-101",
        name="Keyboard Test User",
        keyboard_only=True,
        reduced_motion=True,
    )

    return UXSession(
        user=user,
        results=[
            TaskResult(
                task="Find an existing project",
                completed=True,
                duration_seconds=18.4,
                errors=0,
                steps=5,
                notes=["Search was discovered immediately."],
            ),
            TaskResult(
                task="Create a new project",
                completed=True,
                duration_seconds=31.7,
                errors=1,
                steps=7,
                notes=["Primary action was visually prominent."],
            ),
            TaskResult(
                task="Archive a project",
                completed=False,
                duration_seconds=44.2,
                errors=3,
                steps=8,
                notes=["Destructive-action confirmation was unclear."],
            ),
        ],
    )


def print_report(workbench: UXWorkbench, session: UXSession) -> None:
    print("=== UX FUNDAMENTALS WORKBENCH ===")

    print("\nScreens:")
    for screen in workbench.screens.values():
        print(
            f"- {screen.screen_id}: {screen.title}; "
            f"primary action='{screen.primary_action}'"
        )

    issues = workbench.run_audit()

    print(f"\nAudit issues: {len(issues)}")
    for issue in issues:
        print(
            f"[{issue.severity.value.upper()}] "
            f"{issue.issue_type.value}: {issue.description}"
        )
        print(f"  Recommendation: {issue.recommendation}")

    metrics = workbench.evaluate_session(session)

    print("\nUsability test:")
    print(f"- Completion rate: {metrics['completion_rate']}%")
    print(f"- Average task time: {metrics['average_time_seconds']} seconds")
    print(f"- Error rate: {metrics['error_rate_percent']}%")

    critical = sum(
        issue.severity == Severity.CRITICAL for issue in issues
    )
    major = sum(issue.severity == Severity.MAJOR for issue in issues)

    print("\nPrioritization:")
    print(f"- Critical issues: {critical}")
    print(f"- Major issues: {major}")

    print(
        "\nProduction rule: accessibility failures affecting keyboard access "
        "or accessible names should be resolved before release."
    )


def main() -> None:
    workbench = build_example_workbench()
    session = build_test_session()
    print_report(workbench, session)

    output_file = "ux_audit_report.json"
    workbench.export_report(output_file)
    print(f"\nAudit report written to {output_file}")

    # Lightweight executable assertions provide regression protection.
    assert len(workbench.screens) == 2
    assert session.completion_rate == 2 / 3
    assert session.average_time > 0
    assert all(issue.status == "open" for issue in workbench.issues)

    # Avoid an unused import warning in environments that lint strictly.
    assert re.fullmatch(r"[A-Za-z0-9_-]+", "ux-workbench")
    assert isinstance(time.time(), float)


if __name__ == "__main__":
    main()
