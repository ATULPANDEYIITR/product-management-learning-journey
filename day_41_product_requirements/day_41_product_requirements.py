#!/usr/bin/env python3
"""Executable product requirements engineering and PRD workflow.

Demonstrates stakeholder requirements gathering, functional requirements,
non-functional requirements, traceability, prioritization, conflict detection,
acceptance criteria, scope changes, and release-readiness evaluation.
Uses only the Python standard library.
"""

from __future__ import annotations

import json
import re
import statistics
import unittest
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable


class RequirementType(str, Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS = "business"
    CONSTRAINT = "constraint"


class Priority(str, Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    WONT = "wont"


class RequirementStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AcceptanceCriterion:
    """A testable condition for deciding whether a requirement is satisfied."""

    given: str
    when: str
    then: str

    def validate(self) -> None:
        for name, value in (
            ("given", self.given),
            ("when", self.when),
            ("then", self.then),
        ):
            if not value.strip():
                raise ValueError(f"Acceptance criterion {name} cannot be empty.")


@dataclass
class Requirement:
    requirement_id: str
    title: str
    description: str
    requirement_type: RequirementType
    priority: Priority
    owner: str
    source: str
    status: RequirementStatus = RequirementStatus.PROPOSED
    acceptance_criteria: list[AcceptanceCriterion] = field(default_factory=list)
    dependencies: set[str] = field(default_factory=set)
    related_stories: set[str] = field(default_factory=set)
    risk: RiskLevel = RiskLevel.MEDIUM
    rationale: str = ""
    verification_method: str = "test"
    target_metric: str | None = None

    def validate(self) -> None:
        if not re.fullmatch(r"REQ-[A-Z]+-\d{3}", self.requirement_id):
            raise ValueError(f"Invalid requirement ID: {self.requirement_id}")
        for name, value in (
            ("title", self.title),
            ("description", self.description),
            ("owner", self.owner),
            ("source", self.source),
        ):
            if not value.strip():
                raise ValueError(f"{self.requirement_id}: {name} is required.")
        if len(self.description.strip()) < 15:
            raise ValueError(
                f"{self.requirement_id}: description needs measurable detail."
            )
        if self.requirement_type == RequirementType.FUNCTIONAL:
            if not self.acceptance_criteria:
                raise ValueError(
                    f"{self.requirement_id}: functional requirements need "
                    "acceptance criteria."
                )
        for criterion in self.acceptance_criteria:
            criterion.validate()
        if self.requirement_type == RequirementType.NON_FUNCTIONAL:
            if not self.target_metric:
                raise ValueError(
                    f"{self.requirement_id}: non-functional requirements "
                    "need a measurable target."
                )


@dataclass(frozen=True)
class Stakeholder:
    name: str
    role: str
    influence: int
    interest: int
    goals: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 1 <= self.influence <= 5 or not 1 <= self.interest <= 5:
            raise ValueError("Influence and interest must be between 1 and 5.")


@dataclass
class ChangeRequest:
    change_id: str
    requirement_id: str
    description: str
    requested_by: str
    estimated_effort_days: float
    impact: str
    approved: bool = False
    decision_reason: str = ""


@dataclass
class ProductRequirementsDocument:
    product_name: str
    problem_statement: str
    target_users: list[str]
    success_metrics: dict[str, str]
    assumptions: list[str]
    out_of_scope: list[str]
    requirements: dict[str, Requirement] = field(default_factory=dict)
    stakeholders: list[Stakeholder] = field(default_factory=list)
    change_requests: list[ChangeRequest] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_requirement(self, requirement: Requirement) -> None:
        requirement.validate()
        if requirement.requirement_id in self.requirements:
            raise ValueError(
                f"Duplicate requirement ID: {requirement.requirement_id}"
            )
        self.requirements[requirement.requirement_id] = requirement

    def dependency_errors(self) -> list[str]:
        errors: list[str] = []
        for requirement in self.requirements.values():
            for dependency in requirement.dependencies:
                if dependency not in self.requirements:
                    errors.append(
                        f"{requirement.requirement_id} depends on missing "
                        f"{dependency}"
                    )
                elif dependency == requirement.requirement_id:
                    errors.append(
                        f"{requirement.requirement_id} depends on itself"
                    )
        return errors

    def dependency_cycles(self) -> list[list[str]]:
        """Depth-first traversal detects circular implementation dependencies."""
        state: dict[str, int] = {}
        stack: list[str] = []
        cycles: list[list[str]] = []

        def visit(node: str) -> None:
            state[node] = 1
            stack.append(node)
            requirement = self.requirements[node]
            for dependency in requirement.dependencies:
                if dependency not in self.requirements:
                    continue
                if state.get(dependency, 0) == 0:
                    visit(dependency)
                elif state.get(dependency) == 1:
                    start = stack.index(dependency)
                    cycle = stack[start:] + [dependency]
                    if cycle not in cycles:
                        cycles.append(cycle)
            stack.pop()
            state[node] = 2

        for requirement_id in self.requirements:
            if state.get(requirement_id, 0) == 0:
                visit(requirement_id)
        return cycles

    def traceability_gaps(self) -> dict[str, list[str]]:
        gaps: dict[str, list[str]] = {}
        for requirement in self.requirements.values():
            missing: list[str] = []
            if not requirement.source.strip():
                missing.append("stakeholder or evidence source")
            if not requirement.owner.strip():
                missing.append("accountable owner")
            if requirement.requirement_type == RequirementType.FUNCTIONAL:
                if not requirement.acceptance_criteria:
                    missing.append("acceptance criteria")
            if requirement.requirement_type == RequirementType.NON_FUNCTIONAL:
                if not requirement.target_metric:
                    missing.append("measurable target")
            if not requirement.related_stories:
                missing.append("implementation or delivery trace")
            if missing:
                gaps[requirement.requirement_id] = missing
        return gaps

    def release_readiness(self) -> dict[str, object]:
        required = [
            requirement
            for requirement in self.requirements.values()
            if requirement.priority == Priority.MUST
            and requirement.status != RequirementStatus.REJECTED
        ]
        verified = [
            requirement
            for requirement in required
            if requirement.status == RequirementStatus.VERIFIED
        ]
        return {
            "required_count": len(required),
            "verified_count": len(verified),
            "unverified_ids": [
                requirement.requirement_id
                for requirement in required
                if requirement.status != RequirementStatus.VERIFIED
            ],
            "ready": (
                len(verified) == len(required)
                and not self.dependency_errors()
                and not self.dependency_cycles()
                and not self.traceability_gaps()
            ),
        }

    def priority_summary(self) -> dict[str, int]:
        return {
            priority.value: sum(
                requirement.priority == priority
                for requirement in self.requirements.values()
            )
            for priority in Priority
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "product_name": self.product_name,
            "problem_statement": self.problem_statement,
            "target_users": self.target_users,
            "success_metrics": self.success_metrics,
            "assumptions": self.assumptions,
            "out_of_scope": self.out_of_scope,
            "created_at": self.created_at,
            "stakeholders": [asdict(item) for item in self.stakeholders],
            "requirements": [
                {
                    **asdict(requirement),
                    "requirement_type": requirement.requirement_type.value,
                    "priority": requirement.priority.value,
                    "status": requirement.status.value,
                    "risk": requirement.risk.value,
                    "dependencies": sorted(requirement.dependencies),
                    "related_stories": sorted(requirement.related_stories),
                }
                for requirement in self.requirements.values()
            ],
            "change_requests": [asdict(item) for item in self.change_requests],
            "priority_summary": self.priority_summary(),
            "dependency_errors": self.dependency_errors(),
            "dependency_cycles": self.dependency_cycles(),
            "traceability_gaps": self.traceability_gaps(),
            "release_readiness": self.release_readiness(),
        }

    def export_json(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        # Replace avoids exposing a partially written document to readers.
        temporary.replace(destination)


def rice_score(
    reach: float, impact: float, confidence: float, effort: float
) -> float:
    """Calculate RICE for optional features; it does not override mandatory policy."""
    if reach < 0 or effort <= 0:
        raise ValueError("Reach must be non-negative and effort must be positive.")
    if impact < 0 or not 0 <= confidence <= 1:
        raise ValueError("Impact must be non-negative; confidence must be 0..1.")
    return reach * impact * confidence / effort


def collect_requirements(
    stakeholder: Stakeholder,
    interview_answers: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    """Normalize interview notes into evidence-backed discovery records."""
    findings: list[dict[str, str]] = []
    for answer in interview_answers:
        problem = answer.get("problem", "").strip()
        evidence = answer.get("evidence", "").strip()
        desired_outcome = answer.get("outcome", "").strip()
        if not problem or not evidence or not desired_outcome:
            raise ValueError(
                f"Incomplete discovery response from {stakeholder.name}"
            )
        findings.append(
            {
                "stakeholder": stakeholder.name,
                "role": stakeholder.role,
                "problem": problem,
                "evidence": evidence,
                "desired_outcome": desired_outcome,
            }
        )
    return findings


def detect_conflicting_requirements(
    requirements: Iterable[Requirement],
) -> list[tuple[str, str, str]]:
    """Detect explicitly tagged policy conflicts without pretending NLP is infallible."""
    items = list(requirements)
    conflicts: list[tuple[str, str, str]] = []
    for index, left in enumerate(items):
        for right in items[index + 1:]:
            if left.requirement_id in right.dependencies:
                continue
            left_tags = set(re.findall(r"\bpolicy:([a-z_]+)", left.description))
            right_tags = set(re.findall(r"\bpolicy:([a-z_]+)", right.description))
            for tag in sorted(left_tags & right_tags):
                if (
                    left.requirement_type == RequirementType.CONSTRAINT
                    and right.requirement_type == RequirementType.CONSTRAINT
                    and left.priority == Priority.MUST
                    and right.priority == Priority.MUST
                    and left.description != right.description
                ):
                    conflicts.append(
                        (
                            left.requirement_id,
                            right.requirement_id,
                            f"Review incompatible mandatory policy:{tag} rules",
                        )
                    )
    return conflicts


def build_example_prd() -> ProductRequirementsDocument:
    prd = ProductRequirementsDocument(
        product_name="ProcureFlow Supplier Portal",
        problem_statement=(
            "Procurement teams use email and spreadsheets to onboard suppliers, "
            "causing incomplete submissions, slow reviews, and poor visibility."
        ),
        target_users=[
            "Supplier representatives",
            "Procurement analysts",
            "Compliance officers",
            "Procurement administrators",
        ],
        success_metrics={
            "onboarding_cycle_time": "Reduce median completion time from 10 to 5 business days",
            "submission_completeness": "At least 95% complete on first submission",
            "availability": "Monthly service availability of at least 99.9%",
            "page_latency": "95th percentile response time below 300 ms for normal reads",
        },
        assumptions=[
            "Suppliers have access to a modern browser and email.",
            "Procurement administrators maintain document requirements.",
            "The initial release serves one legal entity.",
        ],
        out_of_scope=[
            "Automatic supplier credit decisions",
            "International tax filing",
            "Automated contract negotiation",
        ],
    )

    prd.stakeholders.extend(
        [
            Stakeholder(
                "Maya Rao",
                "Procurement analyst",
                4,
                5,
                ("track applications", "reduce incomplete submissions"),
            ),
            Stakeholder(
                "Arjun Sen",
                "Compliance officer",
                5,
                4,
                ("verify documents", "maintain audit evidence"),
            ),
            Stakeholder(
                "Nisha Kapoor",
                "Supplier representative",
                3,
                5,
                ("submit documents", "understand missing items"),
            ),
            Stakeholder(
                "Dev Mehta",
                "Platform engineer",
                4,
                3,
                ("protect supplier data", "meet reliability targets"),
            ),
        ]
    )

    requirements = [
        Requirement(
            "REQ-FR-001",
            "Create supplier application",
            "The portal shall allow an authenticated supplier representative "
            "to create an application with legal name, registration country, "
            "tax identifier, and primary contact details.",
            RequirementType.FUNCTIONAL,
            Priority.MUST,
            "Product manager",
            "Supplier interviews and procurement workshop",
            acceptance_criteria=[
                AcceptanceCriterion(
                    "The representative is authenticated.",
                    "The representative submits valid required fields.",
                    "The system creates a draft application and returns its reference.",
                ),
                AcceptanceCriterion(
                    "A tax identifier is already registered for the same legal entity.",
                    "The representative submits another application.",
                    "The system reports the duplicate without exposing another supplier's private data.",
                ),
            ],
            related_stories={"SUP-101", "SUP-102"},
            risk=RiskLevel.HIGH,
            rationale="A traceable application replaces email-based intake.",
            verification_method="integration test",
        ),
        Requirement(
            "REQ-FR-002",
            "Validate document completeness",
            "The portal shall evaluate each submitted application against the "
            "document checklist configured for its supplier category.",
            RequirementType.FUNCTIONAL,
            Priority.MUST,
            "Product manager",
            "Compliance workshop",
            acceptance_criteria=[
                AcceptanceCriterion(
                    "A category has a published document checklist.",
                    "A supplier submits the application.",
                    "The portal identifies missing required documents and blocks final submission.",
                ),
            ],
            dependencies={"REQ-FR-001"},
            related_stories={"SUP-110"},
            risk=RiskLevel.HIGH,
            verification_method="integration test",
        ),
        Requirement(
            "REQ-FR-003",
            "Record compliance decisions",
            "The system shall record each compliance decision with reviewer identity, "
            "decision time, outcome, and a reason when rejecting an application.",
            RequirementType.FUNCTIONAL,
            Priority.MUST,
            "Compliance lead",
            "Compliance audit requirements",
            acceptance_criteria=[
                AcceptanceCriterion(
                    "A reviewer has permission to decide.",
                    "The reviewer records rejection.",
                    "The decision, identity, timestamp, and non-empty reason are retained in the audit history.",
                ),
            ],
            dependencies={"REQ-FR-002"},
            related_stories={"SUP-120"},
            risk=RiskLevel.CRITICAL,
            verification_method="integration and authorization tests",
        ),
        Requirement(
            "REQ-NFR-001",
            "Read performance",
            "The application shall serve supplier application reads with "
            "a 95th percentile latency below 300 milliseconds under 500 concurrent users.",
            RequirementType.NON_FUNCTIONAL,
            Priority.MUST,
            "Engineering lead",
            "Product performance workshop",
            related_stories={"SUP-130", "OPS-40"},
            risk=RiskLevel.HIGH,
            rationale="Slow status checks delay supplier onboarding.",
            verification_method="load test",
            target_metric="p95 latency < 300 ms at 500 concurrent users",
        ),
        Requirement(
            "REQ-NFR-002",
            "Service availability",
            "The production portal shall achieve at least 99.9 percent monthly "
            "availability, excluding approved maintenance windows defined in policy.",
            RequirementType.NON_FUNCTIONAL,
            Priority.MUST,
            "SRE lead",
            "Service-level objective review",
            related_stories={"OPS-41", "OPS-42"},
            risk=RiskLevel.HIGH,
            verification_method="availability monitoring",
            target_metric="monthly availability >= 99.9%",
        ),
        Requirement(
            "REQ-NFR-003",
            "Protect supplier information",
            "The portal shall encrypt network traffic, enforce role-based access "
            "control, and prevent one supplier from reading another supplier's documents.",
            RequirementType.NON_FUNCTIONAL,
            Priority.MUST,
            "Security lead",
            "Security threat assessment",
            related_stories={"SEC-11", "SEC-12"},
            risk=RiskLevel.CRITICAL,
            verification_method="security tests and penetration testing",
            target_metric="100% pass rate for mandatory cross-tenant access tests",
        ),
        Requirement(
            "REQ-BR-001",
            "Reduce onboarding delays",
            "The product shall reduce median supplier onboarding completion time "
            "to five business days or less within one quarter of launch.",
            RequirementType.BUSINESS,
            Priority.SHOULD,
            "Business owner",
            "Procurement operating review",
            related_stories={"ANALYTICS-20"},
            risk=RiskLevel.MEDIUM,
            verification_method="business KPI analysis",
            target_metric="median cycle time <= 5 business days",
        ),
        Requirement(
            "REQ-CON-001",
            "Retain decision evidence",
            "The system shall retain supplier compliance decision records for "
            "seven years according to the approved retention policy.",
            RequirementType.CONSTRAINT,
            Priority.MUST,
            "Compliance lead",
            "Records retention policy",
            related_stories={"DATA-18"},
            risk=RiskLevel.CRITICAL,
            verification_method="retention-policy integration test",
        ),
    ]

    for requirement in requirements:
        prd.add_requirement(requirement)

    return prd


def demonstrate_change_control(prd: ProductRequirementsDocument) -> None:
    """A scope change is recorded separately from the baseline requirement."""
    request = ChangeRequest(
        change_id="CR-014",
        requirement_id="REQ-FR-002",
        description=(
            "Add automated document expiry reminders before supplier documents expire."
        ),
        requested_by="Compliance officer",
        estimated_effort_days=4.0,
        impact="Adds notification scheduling, consent considerations, and monitoring.",
    )

    if request.requirement_id not in prd.requirements:
        request.decision_reason = "Rejected: referenced requirement does not exist."
    elif request.estimated_effort_days <= 0:
        request.decision_reason = "Rejected: effort estimate must be positive."
    else:
        # A change is accepted only after explicit scope and capacity review.
        request.approved = False
        request.decision_reason = (
            "Deferred to a later release pending capacity and notification-policy review."
        )
    prd.change_requests.append(request)


class RequirementsTests(unittest.TestCase):
    def test_rice_score(self) -> None:
        self.assertAlmostEqual(rice_score(1200, 2, 0.8, 6), 320.0)

    def test_rice_rejects_zero_effort(self) -> None:
        with self.assertRaises(ValueError):
            rice_score(100, 2, 0.8, 0)

    def test_duplicate_requirement_rejected(self) -> None:
        prd = build_example_prd()
        original = prd.requirements["REQ-FR-001"]
        with self.assertRaises(ValueError):
            prd.add_requirement(original)

    def test_missing_dependency_detected(self) -> None:
        prd = build_example_prd()
        prd.requirements["REQ-FR-001"].dependencies.add("REQ-FR-999")
        self.assertTrue(prd.dependency_errors())

    def test_dependency_cycle_detected(self) -> None:
        prd = build_example_prd()
        prd.requirements["REQ-FR-001"].dependencies.add("REQ-FR-002")
        self.assertTrue(prd.dependency_cycles())

    def test_non_functional_target_required(self) -> None:
        requirement = Requirement(
            "REQ-NFR-099",
            "Response time",
            "The service shall respond within an agreed time under a defined load.",
            RequirementType.NON_FUNCTIONAL,
            Priority.MUST,
            "Engineering lead",
            "Performance workshop",
        )
        with self.assertRaises(ValueError):
            requirement.validate()

    def test_empty_acceptance_criterion_rejected(self) -> None:
        requirement = Requirement(
            "REQ-FR-099",
            "Submit application",
            "The supplier shall submit a completed application for review.",
            RequirementType.FUNCTIONAL,
            Priority.MUST,
            "Product manager",
            "Supplier interview",
            acceptance_criteria=[AcceptanceCriterion("", "Submit", "Saved")],
        )
        with self.assertRaises(ValueError):
            requirement.validate()


def main() -> None:
    print("Product Requirements Engineering")
    prd = build_example_prd()

    discovery = collect_requirements(
        prd.stakeholders[0],
        [
            {
                "problem": "Supplier applications arrive with missing tax documents.",
                "evidence": "Recent intake audit found repeated email follow-ups.",
                "outcome": "Show missing documents before final submission.",
            }
        ],
    )
    print(json.dumps(discovery, indent=2))

    print("\nPriority distribution")
    print(json.dumps(prd.priority_summary(), indent=2))

    print("\nRICE comparison for optional capabilities")
    candidates = {
        "Expiry reminders": rice_score(500, 1.5, 0.8, 4),
        "Supplier dashboard export": rice_score(350, 1.0, 0.9, 2),
        "Custom portal themes": rice_score(80, 0.5, 0.7, 3),
    }
    for name, score in sorted(
        candidates.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"{name}: {score:.2f}")

    demonstrate_change_control(prd)

    print("\nDependency validation")
    print(prd.dependency_errors() or "No missing dependencies.")
    print("Dependency cycles:", prd.dependency_cycles() or "None")
    print("Traceability gaps:", json.dumps(prd.traceability_gaps(), indent=2))
    print("Release readiness:", json.dumps(prd.release_readiness(), indent=2))

    conflicts = detect_conflicting_requirements(prd.requirements.values())
    print("Explicit policy conflicts:", conflicts or "None detected.")

    output_path = Path("procureflow_prd.json")
    prd.export_json(output_path)
    print(f"PRD exported to {output_path.resolve()}")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RequirementsTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
