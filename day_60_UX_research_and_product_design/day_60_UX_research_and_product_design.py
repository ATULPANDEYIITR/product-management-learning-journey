#!/usr/bin/env python3
"""Research synthesis and product-design quality workflow.

Standard-library implementation covering research evidence, theme synthesis,
wireframe validation, prototype testing, design critique, and design-system
conformance.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    """Raised when a research or design artifact violates domain rules."""


class ProjectPhase(str, Enum):
    DISCOVERY = "discovery"
    SYNTHESIZED = "synthesized"
    DESIGN = "design"
    VALIDATED = "validated"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ResearchEvidence:
    evidence_id: str
    participant_ref: str
    observation: str
    severity: int
    confidence: float
    method: str

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValidationError("Evidence identifier cannot be empty.")
        if not self.participant_ref.strip():
            raise ValidationError("Use a pseudonymous participant reference.")
        if not self.observation.strip() or len(self.observation) > 600:
            raise ValidationError("Observation must contain 1 to 600 characters.")
        if not 1 <= self.severity <= 5:
            raise ValidationError("Severity must be between 1 and 5.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValidationError("Confidence must be between 0 and 1.")
        if self.method not in {"interview", "survey", "observation", "usability_test"}:
            raise ValidationError("Unsupported research method.")


@dataclass(frozen=True)
class ResearchTheme:
    theme_id: str
    name: str
    evidence_ids: tuple[str, ...]
    effort_hours: float

    def __post_init__(self) -> None:
        if not self.theme_id.strip() or not self.name.strip():
            raise ValidationError("Theme identifier and name are required.")
        if not self.evidence_ids:
            raise ValidationError("A theme must reference at least one evidence item.")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValidationError("A theme cannot contain duplicate evidence references.")
        if self.effort_hours <= 0:
            raise ValidationError("Estimated effort must be greater than zero.")


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    interactive: bool
    keyboard_accessible: bool
    accessible_description: str


@dataclass(frozen=True)
class WireframeScreen:
    screen_id: str
    title: str
    component_order: tuple[str, ...]
    keyboard_order: tuple[str, ...]
    required_tokens: tuple[str, ...]
    accessible_name: str


@dataclass(frozen=True)
class UsabilityResult:
    participant_ref: str
    task_name: str
    screen_id: str
    succeeded: bool
    duration_seconds: float
    critical_errors: int = 0


@dataclass(frozen=True)
class CritiqueIssue:
    issue_id: str
    screen_id: str
    heuristic: str
    severity: Severity
    description: str
    recommendation: str
    resolved: bool = False


def _rgb(hex_color: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", hex_color):
        raise ValidationError(f"Invalid hexadecimal color: {hex_color}")
    value = hex_color[1:]
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _luminance(hex_color: str) -> float:
    channels = []
    for channel in _rgb(hex_color):
        normalized = channel / 255.0
        channels.append(
            normalized / 12.92
            if normalized <= 0.04045
            else ((normalized + 0.055) / 1.055) ** 2.4
        )
    return (
        0.2126 * channels[0]
        + 0.7152 * channels[1]
        + 0.0722 * channels[2]
    )


def contrast_ratio(foreground: str, background: str) -> float:
    """Calculate the WCAG relative-luminance contrast ratio."""
    first = _luminance(foreground)
    second = _luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


class DesignSystem:
    def __init__(
        self,
        tokens: dict[str, str],
        components: dict[str, ComponentSpec],
        contrast_pairs: tuple[tuple[str, str], ...],
    ) -> None:
        self.tokens = dict(tokens)
        self.components = dict(components)
        self.contrast_pairs = contrast_pairs

    def validate(self) -> list[str]:
        errors: list[str] = []
        for foreground, background in self.contrast_pairs:
            if foreground not in self.tokens or background not in self.tokens:
                errors.append(f"Missing contrast token pair: {foreground}/{background}")
                continue
            try:
                ratio = contrast_ratio(
                    self.tokens[foreground], self.tokens[background]
                )
                if ratio < 4.5:
                    errors.append(
                        f"Insufficient text contrast for {foreground}/{background}: "
                        f"{ratio:.2f}:1"
                    )
            except ValidationError as exc:
                errors.append(str(exc))
        return errors

    def validate_screen(self, screen: WireframeScreen) -> list[str]:
        errors: list[str] = []

        if not screen.accessible_name.strip():
            errors.append(f"{screen.screen_id}: accessible screen name is required.")

        if len(set(screen.component_order)) != len(screen.component_order):
            errors.append(f"{screen.screen_id}: duplicate component in layout.")

        interactive: list[str] = []
        for name in screen.component_order:
            component = self.components.get(name)
            if component is None:
                errors.append(f"{screen.screen_id}: unknown component '{name}'.")
                continue
            if component.interactive:
                interactive.append(name)
            if not component.keyboard_accessible:
                errors.append(
                    f"{screen.screen_id}: component '{name}' is not keyboard accessible."
                )
            if not component.accessible_description.strip():
                errors.append(
                    f"{screen.screen_id}: component '{name}' lacks an accessible description."
                )

        if tuple(interactive) != screen.keyboard_order:
            errors.append(
                f"{screen.screen_id}: keyboard order must match interactive layout order."
            )

        for token in screen.required_tokens:
            if token not in self.tokens:
                errors.append(f"{screen.screen_id}: missing design token '{token}'.")

        return errors


class UXProject:
    def __init__(self, name: str, design_system: DesignSystem) -> None:
        if not name.strip():
            raise ValidationError("Project name is required.")

        self.name = name
        self.design_system = design_system
        self.phase = ProjectPhase.DISCOVERY
        self.evidence: dict[str, ResearchEvidence] = {}
        self.themes: dict[str, ResearchTheme] = {}
        self.screens: dict[str, WireframeScreen] = {}
        self.usability_results: list[UsabilityResult] = []
        self.critique_issues: dict[str, CritiqueIssue] = {}

    def add_evidence(self, item: ResearchEvidence) -> None:
        if self.phase != ProjectPhase.DISCOVERY:
            raise ValidationError("Research evidence cannot be changed after synthesis.")
        if item.evidence_id in self.evidence:
            raise ValidationError(f"Duplicate evidence ID: {item.evidence_id}")
        self.evidence[item.evidence_id] = item

    def add_theme(self, theme: ResearchTheme) -> None:
        if self.phase != ProjectPhase.DISCOVERY:
            raise ValidationError("Themes can only be defined during discovery.")
        if theme.theme_id in self.themes:
            raise ValidationError(f"Duplicate theme ID: {theme.theme_id}")

        missing = set(theme.evidence_ids) - self.evidence.keys()
        if missing:
            raise ValidationError(f"Unknown evidence references: {sorted(missing)}")

        self.themes[theme.theme_id] = theme

    def theme_metrics(self, theme: ResearchTheme) -> dict[str, float | int | str]:
        linked = [self.evidence[item] for item in theme.evidence_ids]
        count = len(linked)
        average_severity = sum(item.severity for item in linked) / count
        average_confidence = sum(item.confidence for item in linked) / count

        # A transparent prioritization heuristic, not a statistical inference.
        priority = (
            count * average_severity * average_confidence / theme.effort_hours
        )
        return {
            "theme_id": theme.theme_id,
            "name": theme.name,
            "evidence_count": count,
            "average_severity": round(average_severity, 2),
            "average_confidence": round(average_confidence, 2),
            "effort_hours": theme.effort_hours,
            "priority_score": round(priority, 3),
        }

    def synthesize(self) -> list[dict[str, Any]]:
        if self.phase != ProjectPhase.DISCOVERY:
            raise ValidationError("Synthesis is only available from discovery.")
        if len(self.evidence) < 3 or len(self.themes) < 2:
            raise ValidationError(
                "Synthesis requires at least three evidence items and two themes."
            )

        metrics = [
            self.theme_metrics(theme) for theme in self.themes.values()
        ]
        metrics.sort(key=lambda item: item["priority_score"], reverse=True)
        self.phase = ProjectPhase.SYNTHESIZED
        return metrics

    def start_design(self) -> None:
        if self.phase != ProjectPhase.SYNTHESIZED:
            raise ValidationError("Design work requires completed synthesis.")
        self.phase = ProjectPhase.DESIGN

    def add_screen(self, screen: WireframeScreen) -> None:
        if self.phase != ProjectPhase.DESIGN:
            raise ValidationError("Screens can only be added during design.")
        if screen.screen_id in self.screens:
            raise ValidationError(f"Duplicate screen ID: {screen.screen_id}")

        errors = self.design_system.validate_screen(screen)
        if errors:
            raise ValidationError("; ".join(errors))
        self.screens[screen.screen_id] = screen

    def record_usability_result(self, result: UsabilityResult) -> None:
        if self.phase != ProjectPhase.DESIGN:
            raise ValidationError("Usability results require an active design phase.")
        if result.screen_id not in self.screens:
            raise ValidationError("Test result references an unknown screen.")
        if not result.participant_ref.strip() or not result.task_name.strip():
            raise ValidationError("Participant reference and task name are required.")
        if result.duration_seconds <= 0:
            raise ValidationError("Task duration must be positive.")
        if result.critical_errors < 0:
            raise ValidationError("Critical error count cannot be negative.")

        self.usability_results.append(result)

    def add_critique(self, issue: CritiqueIssue) -> None:
        if issue.screen_id not in self.screens:
            raise ValidationError("Critique references an unknown screen.")
        if issue.issue_id in self.critique_issues:
            raise ValidationError("Duplicate critique issue ID.")
        if not issue.description.strip() or not issue.recommendation.strip():
            raise ValidationError("Critique needs a description and recommendation.")
        self.critique_issues[issue.issue_id] = issue

    def resolve_critique(self, issue_id: str) -> None:
        issue = self.critique_issues.get(issue_id)
        if issue is None:
            raise ValidationError(f"Unknown critique issue: {issue_id}")

        self.critique_issues[issue_id] = CritiqueIssue(
            issue_id=issue.issue_id,
            screen_id=issue.screen_id,
            heuristic=issue.heuristic,
            severity=issue.severity,
            description=issue.description,
            recommendation=issue.recommendation,
            resolved=True,
        )

    def evaluate_readiness(self) -> dict[str, Any]:
        if self.phase != ProjectPhase.DESIGN:
            raise ValidationError("Readiness evaluation requires the design phase.")

        blockers: list[str] = []
        for screen in self.screens.values():
            blockers.extend(self.design_system.validate_screen(screen))
        blockers.extend(self.design_system.validate())

        if len(self.screens) < 2:
            blockers.append("At least two validated screens are required.")
        if len(self.usability_results) < 5:
            blockers.append("At least five usability task results are required.")

        total = len(self.usability_results)
        successful = sum(item.succeeded for item in self.usability_results)
        success_rate = successful / total if total else 0.0
        critical_errors = sum(
            item.critical_errors for item in self.usability_results
        )

        if success_rate < 0.80:
            blockers.append("Task success rate is below the 80% project threshold.")
        if critical_errors:
            blockers.append(f"Prototype tests recorded {critical_errors} critical errors.")

        open_critical = [
            item.issue_id
            for item in self.critique_issues.values()
            if item.severity == Severity.CRITICAL and not item.resolved
        ]
        if open_critical:
            blockers.append(
                "Unresolved critical critique issues: " + ", ".join(open_critical)
            )

        if not blockers:
            self.phase = ProjectPhase.VALIDATED

        durations = [
            item.duration_seconds for item in self.usability_results
        ]
        return {
            "project": self.name,
            "phase": self.phase.value,
            "eligible": not blockers,
            "blockers": blockers,
            "screens": len(self.screens),
            "usability_tasks": total,
            "task_success_rate": round(success_rate, 3),
            "average_task_duration_seconds": (
                round(sum(durations) / len(durations), 1) if durations else None
            ),
            "critical_errors": critical_errors,
            "open_critical_issues": len(open_critical),
        }

    def export_report(self, destination: Path) -> None:
        """Export aggregate results, excluding participant observations and quotes."""
        report = {
            "project": self.name,
            "phase": self.phase.value,
            "themes": [
                self.theme_metrics(theme) for theme in self.themes.values()
            ],
            "readiness": (
                self.evaluate_readiness()
                if self.phase == ProjectPhase.DESIGN
                else {"phase": self.phase.value}
            ),
        }
        destination.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def build_example_project() -> UXProject:
    design_system = DesignSystem(
        tokens={
            "color.text": "#17212B",
            "color.surface": "#FFFFFF",
            "color.action": "#1247A8",
            "space.medium": "16px",
        },
        components={
            "SearchField": ComponentSpec(
                "SearchField", True, True, "Origin and destination input"
            ),
            "PrimaryButton": ComponentSpec(
                "PrimaryButton", True, True, "Submit the route search"
            ),
            "RouteCard": ComponentSpec(
                "RouteCard", True, True, "Selectable public transport route"
            ),
        },
        contrast_pairs=(
            ("color.text", "color.surface"),
            ("color.action", "color.surface"),
        ),
    )

    project = UXProject("City Transit Companion", design_system)

    evidence = [
        ResearchEvidence("E01", "P-001", "Users are unsure whether a transfer is required.", 5, 0.95, "interview"),
        ResearchEvidence("E02", "P-002", "The route result does not clearly identify transfer points.", 4, 0.90, "observation"),
        ResearchEvidence("E03", "P-003", "Participants compare routes by total journey time.", 3, 0.85, "interview"),
        ResearchEvidence("E04", "P-004", "Users cannot find the complete fare before selecting a route.", 5, 0.95, "interview"),
        ResearchEvidence("E05", "P-005", "Fare information is displayed inconsistently across route options.", 4, 0.90, "survey"),
        ResearchEvidence("E06", "P-006", "Participants want to distinguish discounted and standard fares.", 3, 0.85, "observation"),
    ]
    for item in evidence:
        project.add_evidence(item)

    project.add_theme(
        ResearchTheme("T01", "Transfer uncertainty", ("E01", "E02", "E03"), 8)
    )
    project.add_theme(
        ResearchTheme("T02", "Fare transparency", ("E04", "E05", "E06"), 5)
    )

    return project


def run_example() -> UXProject:
    project = build_example_project()
    print("PROJECT:", project.name)

    print("\nRESEARCH SYNTHESIS")
    for item in project.synthesize():
        print(json.dumps(item, ensure_ascii=False))

    project.start_design()

    project.add_screen(
        WireframeScreen(
            screen_id="S01",
            title="Route search",
            component_order=("SearchField", "PrimaryButton"),
            keyboard_order=("SearchField", "PrimaryButton"),
            required_tokens=("color.text", "color.surface", "color.action"),
            accessible_name="Search for a public transport journey",
        )
    )
    project.add_screen(
        WireframeScreen(
            screen_id="S02",
            title="Route results",
            component_order=("RouteCard", "PrimaryButton"),
            keyboard_order=("RouteCard", "PrimaryButton"),
            required_tokens=("color.text", "color.surface", "color.action"),
            accessible_name="Available journey options",
        )
    )

    project.add_critique(
        CritiqueIssue(
            "C01",
            "S02",
            "Visibility of system status",
            Severity.MEDIUM,
            "The selected route does not have a persistent selection indicator.",
            "Add a visible selected state and an accessible state announcement.",
        )
    )
    project.add_critique(
        CritiqueIssue(
            "C02",
            "S01",
            "Error prevention",
            Severity.CRITICAL,
            "The origin field accepts an empty value in an early prototype.",
            "Require a valid origin before route calculation.",
            resolved=True,
        )
    )

    test_data = [
        UsabilityResult("P-007", "Find the fastest route", "S01", True, 62),
        UsabilityResult("P-008", "Compare two journey options", "S02", True, 75),
        UsabilityResult("P-009", "Identify transfer points", "S02", True, 81),
        UsabilityResult("P-010", "Find the complete fare", "S02", False, 110),
        UsabilityResult("P-011", "Search for a return journey", "S01", True, 69),
    ]
    for result in test_data:
        project.record_usability_result(result)

    print("\nDESIGN READINESS")
    print(json.dumps(project.evaluate_readiness(), indent=2))

    return project


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the UX research and product-design case study."
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Optional path for an aggregate JSON report.",
    )
    args = parser.parse_args()

    try:
        project = run_example()

        # Basic domain assertions exercise important validation boundaries.
        assert project.phase == ProjectPhase.VALIDATED
        assert len(project.evidence) == 6
        assert len(project.themes) == 2
        assert len(project.screens) == 2

        if args.export:
            project.export_report(args.export)
            print(f"\nAggregate report written to: {args.export}")

    except (ValidationError, OSError) as exc:
        raise SystemExit(f"Workflow failed: {exc}") from exc


if __name__ == "__main__":
    main()
