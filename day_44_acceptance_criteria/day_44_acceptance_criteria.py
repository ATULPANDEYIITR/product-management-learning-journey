"""Acceptance criteria engineering toolkit.

Models Given-When-Then acceptance criteria, validation rules, boundary
conditions, expected outcomes, and traceability for a repository feature.

Run with: python acceptance_criteria.py
Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
import unittest
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class Priority(str, Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"


class CriterionStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    VERIFIED = "verified"
    FAILED = "failed"


class Severity(str, Enum):
    BLOCKER = "blocker"
    MAJOR = "major"
    MINOR = "minor"


@dataclass(frozen=True)
class Scenario:
    """A testable behavior expressed through Given-When-Then."""

    given: str
    when: str
    then: str
    expected: str
    tags: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors = []
        for name, value in (
            ("Given", self.given),
            ("When", self.when),
            ("Then", self.then),
            ("Expected behavior", self.expected),
        ):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{name} must be non-empty.")
            elif len(value.strip()) < 8:
                errors.append(f"{name} must provide meaningful detail.")
        if not self.tags:
            errors.append("At least one scenario tag is required.")
        return errors


@dataclass
class AcceptanceCriterion:
    criterion_id: str
    title: str
    description: str
    priority: Priority
    owner: str
    scenarios: list[Scenario] = field(default_factory=list)
    status: CriterionStatus = CriterionStatus.DRAFT
    evidence: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors = []
        if not re.fullmatch(r"AC-[A-Z]{2,8}-\d{3}", self.criterion_id):
            errors.append("ID must match AC-AREA-001.")
        if not self.title.strip():
            errors.append("Title is required.")
        if len(self.description.strip()) < 15:
            errors.append("Description must explain the business behavior.")
        if not self.owner.strip():
            errors.append("An accountable owner is required.")
        if not self.scenarios:
            errors.append("At least one Given-When-Then scenario is required.")

        for index, scenario in enumerate(self.scenarios, start=1):
            errors.extend(
                f"Scenario {index}: {error}"
                for error in scenario.validate()
            )

        return errors

    def mark_ready(self) -> None:
        errors = self.validate()
        if errors:
            raise ValueError("; ".join(errors))
        self.status = CriterionStatus.READY

    def record_result(self, passed: bool, evidence: str) -> None:
        if self.status not in (CriterionStatus.READY, CriterionStatus.VERIFIED,
                               CriterionStatus.FAILED):
            raise ValueError("Only ready or previously tested criteria can be tested.")
        if not evidence.strip():
            raise ValueError("Test evidence cannot be empty.")

        self.evidence.append(evidence.strip())
        self.status = CriterionStatus.VERIFIED if passed else CriterionStatus.FAILED


@dataclass(frozen=True)
class ValidationRule:
    name: str
    predicate: Callable[[Any], bool]
    message: str

    def check(self, value: Any) -> bool:
        try:
            return bool(self.predicate(value))
        except (TypeError, ValueError, KeyError, AttributeError):
            return False


def validate_feature_input(data: dict[str, Any]) -> list[str]:
    """Validate a proposed feature request before criteria are approved."""
    rules = [
        ValidationRule(
            "title",
            lambda value: isinstance(value.get("title"), str)
            and 5 <= len(value["title"].strip()) <= 120,
            "Title must contain 5 to 120 characters.",
        ),
        ValidationRule(
            "priority",
            lambda value: value.get("priority") in {p.value for p in Priority},
            "Priority must be must, should, or could.",
        ),
        ValidationRule(
            "scenarios",
            lambda value: isinstance(value.get("scenarios"), list)
            and len(value["scenarios"]) > 0,
            "At least one scenario is required.",
        ),
    ]
    return [rule.message for rule in rules if not rule.check(data)]


def scenario_from_dict(data: dict[str, Any]) -> Scenario:
    required = {"given", "when", "then", "expected"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing scenario fields: {', '.join(sorted(missing))}")

    tags = data.get("tags", ["functional"])
    if not isinstance(tags, list) or not all(
        isinstance(tag, str) and tag.strip() for tag in tags
    ):
        raise ValueError("Tags must be a list of non-empty strings.")

    scenario = Scenario(
        given=data["given"],
        when=data["when"],
        then=data["then"],
        expected=data["expected"],
        tags=tuple(tag.strip() for tag in tags),
    )
    errors = scenario.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return scenario


def criterion_to_dict(criterion: AcceptanceCriterion) -> dict[str, Any]:
    data = asdict(criterion)
    data["priority"] = criterion.priority.value
    data["status"] = criterion.status.value
    return data


def save_criteria(
    criteria: list[AcceptanceCriterion],
    destination: Path,
) -> None:
    """Write a complete JSON document, replacing the destination atomically."""
    payload = [criterion_to_dict(item) for item in criteria]
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")

    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def build_demo_criteria() -> list[AcceptanceCriterion]:
    return [
        AcceptanceCriterion(
            criterion_id="AC-PR-001",
            title="Reject incomplete pull request criteria",
            description=(
                "A feature request must define its observable behavior "
                "before the team treats its acceptance criteria as ready."
            ),
            priority=Priority.MUST,
            owner="Engineering",
            scenarios=[
                Scenario(
                    given="A feature request has no acceptance scenarios",
                    when="The request is submitted for readiness validation",
                    then="The request is rejected",
                    expected=(
                        "Readiness remains blocked until at least one "
                        "complete Given-When-Then scenario is provided."
                    ),
                    tags=("validation", "negative"),
                ),
                Scenario(
                    given="A scenario contains Given, When, Then, and expected behavior",
                    when="The owner validates the acceptance criterion",
                    then="The criterion becomes ready",
                    expected=(
                        "The criterion is ready only when all required fields "
                        "and every scenario pass validation."
                    ),
                    tags=("validation", "positive"),
                ),
            ],
        ),
        AcceptanceCriterion(
            criterion_id="AC-PR-002",
            title="Require approval before a protected merge",
            description=(
                "A pull request targeting a protected branch must satisfy "
                "review and automated status-check policies before merging."
            ),
            priority=Priority.MUST,
            owner="Repository Maintainer",
            scenarios=[
                Scenario(
                    given="A protected branch requires one eligible approval",
                    when="A pull request has no qualifying approval",
                    then="The merge is blocked",
                    expected=(
                        "A passing status check cannot substitute for "
                        "the required independent review approval."
                    ),
                    tags=("branch-protection", "negative"),
                ),
                Scenario(
                    given="An eligible reviewer approved the latest changes and all required checks passed",
                    when="The merge service evaluates the pull request",
                    then="The policy permits merging if no other rule blocks it",
                    expected=(
                        "Approval, current review state, and required checks "
                        "are evaluated independently."
                    ),
                    tags=("approval", "positive"),
                ),
            ],
        ),
    ]


class AcceptanceCriteriaTests(unittest.TestCase):
    def test_valid_criterion_becomes_ready(self):
        criterion = build_demo_criteria()[0]
        criterion.mark_ready()
        self.assertEqual(criterion.status, CriterionStatus.READY)

    def test_missing_scenarios_block_readiness(self):
        criterion = AcceptanceCriterion(
            "AC-PR-003",
            "Validate review policy",
            "Review policy behavior must be explicit.",
            Priority.MUST,
            "Maintainer",
        )
        with self.assertRaises(ValueError):
            criterion.mark_ready()

    def test_invalid_identifier_is_rejected(self):
        criterion = build_demo_criteria()[0]
        criterion.criterion_id = "invalid-id"
        self.assertTrue(any("ID must match" in error for error in criterion.validate()))

    def test_blank_evidence_is_rejected(self):
        criterion = build_demo_criteria()[0]
        criterion.mark_ready()
        with self.assertRaises(ValueError):
            criterion.record_result(True, " ")

    def test_failed_execution_is_recorded(self):
        criterion = build_demo_criteria()[0]
        criterion.mark_ready()
        criterion.record_result(False, "CI run 184: required approval missing")
        self.assertEqual(criterion.status, CriterionStatus.FAILED)

    def test_input_validation_detects_invalid_priority(self):
        errors = validate_feature_input({
            "title": "Merge protection",
            "priority": "urgent",
            "scenarios": [{"given": "x"}],
        })
        self.assertTrue(any("Priority" in error for error in errors))

    def test_scenario_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            scenario_from_dict({"given": "A protected branch exists"})


def main() -> None:
    criteria = build_demo_criteria()

    print("Acceptance Criteria Engineering")
    print("=" * 36)

    for criterion in criteria:
        errors = criterion.validate()
        print(f"\n{criterion.criterion_id}: {criterion.title}")
        print(f"Priority: {criterion.priority.value}")
        print(f"Status: {criterion.status.value}")
        print(f"Scenarios: {len(criterion.scenarios)}")
        print(f"Validation: {'PASS' if not errors else 'FAIL'}")
        for scenario in criterion.scenarios:
            print(f"  Given: {scenario.given}")
            print(f"  When:  {scenario.when}")
            print(f"  Then:  {scenario.then}")
            print(f"  Expected: {scenario.expected}")
        if errors:
            for error in errors:
                print(f"  Error: {error}")
        else:
            criterion.mark_ready()

    print("\nFeature input validation")
    valid_input = {
        "title": "Protected branch merge eligibility",
        "priority": "must",
        "scenarios": [{"given": "A pull request exists"}],
    }
    print(validate_feature_input(valid_input) or "PASS")

    output = Path("acceptance_criteria.json")
    save_criteria(criteria, output)
    print(f"\nSaved criteria to {output.resolve()}")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        AcceptanceCriteriaTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
