#!/usr/bin/env python3
"""
Product Requirements Document (PRD) engineering toolkit.

Demonstrates how to define, validate, prioritize, review, version, and export
a PRD covering the problem, goals, users, scope, requirements, acceptance
criteria, risks, dependencies, and release readiness.

Run:
    python prd_toolkit.py
    python prd_toolkit.py --output prd.json
    python prd_toolkit.py --format markdown --output prd.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unittest
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any


class Priority(str, Enum):
    MUST = "Must"
    SHOULD = "Should"
    COULD = "Could"
    WONT = "Won't"


class RequirementType(str, Enum):
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-functional"
    BUSINESS = "Business"
    TECHNICAL = "Technical"
    COMPLIANCE = "Compliance"


class RiskSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RequirementStatus(str, Enum):
    DRAFT = "Draft"
    REVIEW = "In Review"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"
    VERIFIED = "Verified"


@dataclass
class UserPersona:
    name: str
    description: str
    needs: list[str]
    pain_points: list[str]

    def validate(self) -> list[str]:
        errors = []
        if not self.name.strip():
            errors.append("Persona name cannot be empty.")
        if not self.description.strip():
            errors.append(f"{self.name}: description is required.")
        if not self.needs:
            errors.append(f"{self.name}: at least one user need is required.")
        return errors


@dataclass
class AcceptanceCriterion:
    criterion_id: str
    given: str
    when: str
    then: str
    testable: bool = True

    def validate(self) -> list[str]:
        errors = []
        for field_name in ("criterion_id", "given", "when", "then"):
            if not getattr(self, field_name).strip():
                errors.append(f"Acceptance criterion {field_name} is required.")
        if not self.testable:
            errors.append(
                f"{self.criterion_id}: acceptance criterion must be testable."
            )
        return errors


@dataclass
class Requirement:
    requirement_id: str
    title: str
    description: str
    requirement_type: RequirementType
    priority: Priority
    rationale: str
    acceptance_criteria: list[AcceptanceCriterion]
    status: RequirementStatus = RequirementStatus.DRAFT
    owner: str = "Product"
    dependencies: list[str] = field(default_factory=list)
    source: str = "Product discovery"
    estimate_points: int = 3

    def validate(self) -> list[str]:
        errors = []
        if not re.fullmatch(r"REQ-[A-Z0-9-]+", self.requirement_id):
            errors.append(f"Invalid requirement ID: {self.requirement_id}")
        for name in ("title", "description", "rationale", "owner"):
            if not getattr(self, name).strip():
                errors.append(f"{self.requirement_id}: {name} is required.")
        if self.estimate_points < 0:
            errors.append(f"{self.requirement_id}: estimate cannot be negative.")
        if not self.acceptance_criteria:
            errors.append(
                f"{self.requirement_id}: at least one acceptance criterion is required."
            )
        for criterion in self.acceptance_criteria:
            errors.extend(criterion.validate())
        return errors


@dataclass
class Risk:
    risk_id: str
    description: str
    probability: int
    impact: int
    mitigation: str
    owner: str
    contingency: str

    @property
    def score(self) -> int:
        return self.probability * self.impact

    @property
    def severity(self) -> RiskSeverity:
        if self.score >= 20:
            return RiskSeverity.CRITICAL
        if self.score >= 12:
            return RiskSeverity.HIGH
        if self.score >= 6:
            return RiskSeverity.MEDIUM
        return RiskSeverity.LOW

    def validate(self) -> list[str]:
        errors = []
        if not 1 <= self.probability <= 5:
            errors.append(f"{self.risk_id}: probability must be between 1 and 5.")
        if not 1 <= self.impact <= 5:
            errors.append(f"{self.risk_id}: impact must be between 1 and 5.")
        for name in ("description", "mitigation", "owner", "contingency"):
            if not getattr(self, name).strip():
                errors.append(f"{self.risk_id}: {name} is required.")
        return errors


@dataclass
class PRD:
    product_name: str
    version: str
    status: str
    author: str
    created_date: str
    problem_statement: str
    evidence: list[str]
    goals: dict[str, str]
    non_goals: list[str]
    personas: list[UserPersona]
    in_scope: list[str]
    out_of_scope: list[str]
    requirements: list[Requirement]
    risks: list[Risk]
    dependencies: list[str]
    assumptions: list[str]
    open_questions: list[str]
    release_criteria: list[str]

    def validate(self) -> list[str]:
        errors: list[str] = []

        required_text = (
            "product_name",
            "version",
            "status",
            "author",
            "problem_statement",
        )
        for name in required_text:
            if not getattr(self, name).strip():
                errors.append(f"PRD field '{name}' is required.")

        try:
            date.fromisoformat(self.created_date)
        except ValueError:
            errors.append("created_date must use YYYY-MM-DD format.")

        if not self.evidence:
            errors.append("The problem statement needs supporting evidence.")
        if not self.goals:
            errors.append("At least one measurable product goal is required.")
        if not self.personas:
            errors.append("At least one user persona is required.")
        if not self.in_scope:
            errors.append("The product scope must contain at least one item.")
        if not self.requirements:
            errors.append("At least one product requirement is required.")
        if not self.release_criteria:
            errors.append("Release criteria must be defined.")

        for key, goal in self.goals.items():
            if not key.strip() or not goal.strip():
                errors.append("Goal names and measurable target descriptions are required.")

        persona_names = [p.name.casefold() for p in self.personas]
        if len(persona_names) != len(set(persona_names)):
            errors.append("Persona names must be unique.")

        requirement_ids = [r.requirement_id for r in self.requirements]
        if len(requirement_ids) != len(set(requirement_ids)):
            errors.append("Requirement IDs must be unique.")

        known_ids = set(requirement_ids)
        for requirement in self.requirements:
            errors.extend(requirement.validate())
            for dependency in requirement.dependencies:
                if dependency not in known_ids:
                    errors.append(
                        f"{requirement.requirement_id}: unknown dependency {dependency}."
                    )
                if dependency == requirement.requirement_id:
                    errors.append(
                        f"{requirement.requirement_id}: cannot depend on itself."
                    )

        graph = {
            r.requirement_id: r.dependencies
            for r in self.requirements
        }
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(requirement_id: str) -> None:
            if requirement_id in visiting:
                errors.append(
                    f"Requirement dependency cycle detected at {requirement_id}."
                )
                return
            if requirement_id in visited:
                return
            visiting.add(requirement_id)
            for dependency in graph.get(requirement_id, []):
                if dependency in graph:
                    visit(dependency)
            visiting.remove(requirement_id)
            visited.add(requirement_id)

        for requirement_id in graph:
            visit(requirement_id)

        risk_ids = [risk.risk_id for risk in self.risks]
        if len(risk_ids) != len(set(risk_ids)):
            errors.append("Risk IDs must be unique.")
        for risk in self.risks:
            errors.extend(risk.validate())

        return errors

    def readiness_report(self) -> dict[str, Any]:
        errors = self.validate()
        priorities = {
            priority.value: sum(
                req.priority == priority for req in self.requirements
            )
            for priority in Priority
        }
        statuses = {
            status.value: sum(
                req.status == status for req in self.requirements
            )
            for status in RequirementStatus
        }
        return {
            "product": self.product_name,
            "valid": not errors,
            "validation_errors": errors,
            "requirement_count": len(self.requirements),
            "priority_distribution": priorities,
            "requirement_status_distribution": statuses,
            "critical_or_high_risks": [
                {
                    "id": risk.risk_id,
                    "score": risk.score,
                    "severity": risk.severity.value,
                }
                for risk in sorted(
                    self.risks,
                    key=lambda item: item.score,
                    reverse=True,
                )
                if risk.severity in (RiskSeverity.CRITICAL, RiskSeverity.HIGH)
            ],
            "release_ready": not errors
            and all(
                requirement.status in (
                    RequirementStatus.APPROVED,
                    RequirementStatus.IMPLEMENTED,
                    RequirementStatus.VERIFIED,
                )
                for requirement in self.requirements
                if requirement.priority == Priority.MUST
            ),
        }


def build_sample_prd() -> PRD:
    """Build a realistic PRD for an internal procurement request portal."""

    submit_request = Requirement(
        requirement_id="REQ-PORTAL-001",
        title="Submit a procurement request",
        description=(
            "An authenticated employee can submit a purchase request with "
            "a business justification, cost center, requested amount, and "
            "supporting documentation."
        ),
        requirement_type=RequirementType.FUNCTIONAL,
        priority=Priority.MUST,
        rationale="Structured requests reduce missing information and manual follow-up.",
        acceptance_criteria=[
            AcceptanceCriterion(
                "AC-001-A",
                "an authenticated employee has completed all mandatory fields",
                "the employee submits a valid request",
                "the system creates one request with a unique identifier and Pending Review status",
            ),
            AcceptanceCriterion(
                "AC-001-B",
                "a request has a missing cost center",
                "the employee attempts submission",
                "the system rejects submission and identifies the missing field",
            ),
        ],
        owner="Procurement Product Owner",
        estimate_points=5,
    )

    approval_routing = Requirement(
        requirement_id="REQ-PORTAL-002",
        title="Route requests for approval",
        description=(
            "The portal routes requests according to amount thresholds "
            "and the approval matrix assigned to the cost center."
        ),
        requirement_type=RequirementType.FUNCTIONAL,
        priority=Priority.MUST,
        rationale="Consistent routing reduces unauthorized expenditure.",
        acceptance_criteria=[
            AcceptanceCriterion(
                "AC-002-A",
                "a submitted request matches an active approval policy",
                "the workflow evaluates the request amount and cost center",
                "the request is assigned to the required approver group and an audit event is recorded",
            ),
            AcceptanceCriterion(
                "AC-002-B",
                "no active approval policy matches the request",
                "the workflow attempts routing",
                "the request is held for authorized administrative resolution and is not auto-approved",
            ),
        ],
        owner="Procurement Workflow Lead",
        dependencies=["REQ-PORTAL-001"],
        estimate_points=8,
    )

    status_visibility = Requirement(
        requirement_id="REQ-PORTAL-003",
        title="Display request status",
        description=(
            "Requesters can view the current state, assigned approval stage, "
            "and recorded decision history for their own requests."
        ),
        requirement_type=RequirementType.FUNCTIONAL,
        priority=Priority.SHOULD,
        rationale="Transparent status reduces status enquiries.",
        acceptance_criteria=[
            AcceptanceCriterion(
                "AC-003-A",
                "a requester owns a submitted request",
                "the requester opens the request details",
                "the current status and authorized decision history are displayed",
            ),
            AcceptanceCriterion(
                "AC-003-B",
                "a user does not own a request and lacks an authorized procurement role",
                "the user requests its details",
                "the service denies access without exposing request contents",
            ),
        ],
        owner="Product Manager",
        dependencies=["REQ-PORTAL-001"],
        estimate_points=3,
    )

    security_requirement = Requirement(
        requirement_id="REQ-PORTAL-004",
        title="Enforce request access controls",
        description=(
            "The API verifies user identity and request-level authorization "
            "for every read and write operation."
        ),
        requirement_type=RequirementType.SECURITY if hasattr(
            RequirementType, "SECURITY"
        ) else RequirementType.TECHNICAL,
        priority=Priority.MUST,
        rationale="Procurement requests contain commercially sensitive information.",
        acceptance_criteria=[
            AcceptanceCriterion(
                "AC-004-A",
                "a user has no permission to access a request",
                "the user calls the request API",
                "the API denies access and records a security event without returning protected data",
            ),
            AcceptanceCriterion(
                "AC-004-B",
                "a session has expired",
                "the user submits a protected API request",
                "the API returns an authentication failure and performs no state change",
            ),
        ],
        owner="Security Lead",
        estimate_points=5,
    )

    return PRD(
        product_name="Procurement Request Portal",
        version="1.0.0",
        status="Draft",
        author="Product Management",
        created_date=date.today().isoformat(),
        problem_statement=(
            "Employees submit purchase requests through email and spreadsheets. "
            "Incomplete submissions, inconsistent approval routing, and limited "
            "status visibility increase processing time and weaken auditability."
        ),
        evidence=[
            "Discovery interviews report repeated requests for missing fields.",
            "Procurement teams manually identify approvers from separate spreadsheets.",
            "Requesters cannot reliably determine the current approval stage.",
        ],
        goals={
            "submission_completeness": "At least 95% of submitted requests pass initial completeness validation.",
            "routing_accuracy": "At least 99% of requests are assigned to the correct approval path.",
            "status_enquiries": "Reduce manual request-status enquiries by 40% within three months of launch.",
        },
        non_goals=[
            "Replace the organization's enterprise resource planning system.",
            "Execute supplier payments.",
            "Automatically approve purchases without an authorized policy.",
        ],
        personas=[
            UserPersona(
                "Employee Requester",
                "An employee purchasing goods or services for an approved business need.",
                [
                    "Submit a complete request without learning procurement terminology.",
                    "See the current status and outstanding action.",
                ],
                [
                    "Repeatedly supplying missing information.",
                    "Uncertainty about approval progress.",
                ],
            ),
            UserPersona(
                "Procurement Approver",
                "An authorized employee responsible for reviewing purchases within delegated limits.",
                [
                    "Receive requests that contain sufficient evidence.",
                    "Record a traceable approval or rejection decision.",
                ],
                [
                    "Unclear ownership.",
                    "Inconsistent approval information.",
                ],
            ),
            UserPersona(
                "Procurement Administrator",
                "An authorized operator who maintains routing policies and investigates exceptions.",
                [
                    "Maintain effective-dated approval rules.",
                    "Investigate exceptions through an audit trail.",
                ],
                [
                    "Conflicting policy records.",
                    "Insufficient information for compliance investigations.",
                ],
            ),
        ],
        in_scope=[
            "Authenticated request submission and field validation.",
            "Approval routing using authorized policy rules.",
            "Request status and decision history.",
            "Request-level authorization and audit events.",
        ],
        out_of_scope=[
            "Supplier contract negotiation.",
            "Payment execution and accounting reconciliation.",
            "Automated supplier selection.",
        ],
        requirements=[
            submit_request,
            approval_routing,
            status_visibility,
            security_requirement,
        ],
        risks=[
            Risk(
                "RISK-001",
                "Approval matrix data may be outdated or contradictory.",
                4,
                5,
                "Validate policy ownership, effective dates, and overlapping thresholds before rollout.",
                "Procurement Operations",
                "Hold unmatched requests for authorized manual resolution.",
            ),
            Risk(
                "RISK-002",
                "Employees may submit commercially sensitive documents.",
                3,
                5,
                "Apply access controls, encryption, retention rules, and security logging.",
                "Security Lead",
                "Disable affected access, investigate exposure, and follow the incident response procedure.",
            ),
            Risk(
                "RISK-003",
                "Employees may continue using email instead of the portal.",
                3,
                3,
                "Pilot the workflow with representative teams and measure adoption.",
                "Product Manager",
                "Retain a documented exception process during the transition.",
            ),
        ],
        dependencies=[
            "Corporate identity provider",
            "Authoritative cost-center directory",
            "Maintained procurement approval matrix",
            "Approved document storage service",
        ],
        assumptions=[
            "Employees have corporate accounts.",
            "Procurement policy owners can provide an authoritative approval matrix.",
            "A request can be identified independently of its current workflow state.",
        ],
        open_questions=[
            "Which monetary thresholds require additional finance approval?",
            "What retention period applies to supporting documents?",
            "Which roles may reopen a rejected request?",
        ],
        release_criteria=[
            "All Must requirements are approved and verified against acceptance criteria.",
            "No unresolved critical security defect remains.",
            "Approval-routing tests cover threshold boundaries and unmatched policies.",
            "Access-control and audit-trail tests pass.",
            "Business owners sign off on the operational acceptance test.",
        ],
    )


def to_json_compatible(value: Any) -> Any:
    """Convert nested dataclasses and enums into JSON-compatible values."""
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: to_json_compatible(item)
            for key, item in asdict(value).items()
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {
            str(key): to_json_compatible(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [to_json_compatible(item) for item in value]
    return value


def render_markdown(prd: PRD) -> str:
    """Export the structured PRD without losing traceability."""
    lines = [
        f"# {prd.product_name}",
        "",
        f"- **Version:** {prd.version}",
        f"- **Status:** {prd.status}",
        f"- **Author:** {prd.author}",
        f"- **Created:** {prd.created_date}",
        "",
        "## Problem Statement",
        "",
        prd.problem_statement,
        "",
        "### Supporting Evidence",
        "",
    ]
    lines.extend(f"- {item}" for item in prd.evidence)
    lines.extend(["", "## Goals", ""])
    for name, target in prd.goals.items():
        lines.append(f"- **{name.replace('_', ' ').title()}:** {target}")

    for heading, items in (
        ("Non-goals", prd.non_goals),
        ("In Scope", prd.in_scope),
        ("Out of Scope", prd.out_of_scope),
        ("Dependencies", prd.dependencies),
        ("Assumptions", prd.assumptions),
        ("Open Questions", prd.open_questions),
        ("Release Criteria", prd.release_criteria),
    ):
        lines.extend(["", f"## {heading}", ""])
        lines.extend(f"- {item}" for item in items)

    lines.extend(["", "## User Personas", ""])
    for persona in prd.personas:
        lines.extend([
            f"### {persona.name}",
            "",
            persona.description,
            "",
            "**Needs**",
            "",
        ])
        lines.extend(f"- {item}" for item in persona.needs)
        lines.extend(["", "**Pain points**", ""])
        lines.extend(f"- {item}" for item in persona.pain_points)

    lines.extend(["", "## Requirements", ""])
    for requirement in prd.requirements:
        lines.extend([
            f"### {requirement.requirement_id}: {requirement.title}",
            "",
            f"- **Type:** {requirement.requirement_type.value}",
            f"- **Priority:** {requirement.priority.value}",
            f"- **Status:** {requirement.status.value}",
            f"- **Owner:** {requirement.owner}",
            f"- **Estimate:** {requirement.estimate_points} points",
            f"- **Dependencies:** {', '.join(requirement.dependencies) or 'None'}",
            "",
            requirement.description,
            "",
            f"**Rationale:** {requirement.rationale}",
            "",
            "**Acceptance Criteria**",
            "",
        ])
        for criterion in requirement.acceptance_criteria:
            lines.extend([
                f"- **{criterion.criterion_id}**",
                f"  - Given: {criterion.given}",
                f"  - When: {criterion.when}",
                f"  - Then: {criterion.then}",
            ])

    lines.extend(["", "## Risk Register", ""])
    lines.append(
        "| ID | Risk | Probability | Impact | Score | Severity | Owner | Mitigation |"
    )
    lines.append(
        "|---|---|---:|---:|---:|---|---|---|"
    )
    for risk in sorted(prd.risks, key=lambda item: item.score, reverse=True):
        description = risk.description.replace("|", "\\|")
        mitigation = risk.mitigation.replace("|", "\\|")
        lines.append(
            f"| {risk.risk_id} | {description} | {risk.probability} | "
            f"{risk.impact} | {risk.score} | {risk.severity.value} | "
            f"{risk.owner} | {mitigation} |"
        )

    return "\n".join(lines) + "\n"


def demonstrate_requirement_prioritization(prd: PRD) -> None:
    """Show the difference between priority and implementation status."""
    print("\nRequirement prioritization")
    for requirement in sorted(
        prd.requirements,
        key=lambda item: (
            list(Priority).index(item.priority),
            item.requirement_id,
        ),
    ):
        print(
            f"{requirement.requirement_id}: "
            f"{requirement.priority.value:6} | "
            f"{requirement.status.value:8} | "
            f"{requirement.title}"
        )


def demonstrate_risk_analysis(prd: PRD) -> None:
    """Use a simple probability-impact matrix for risk triage."""
    print("\nRisk analysis")
    for risk in sorted(prd.risks, key=lambda item: item.score, reverse=True):
        print(
            f"{risk.risk_id}: score={risk.score:2}, "
            f"severity={risk.severity.value:8}, "
            f"owner={risk.owner}"
        )


class PRDTests(unittest.TestCase):
    def test_sample_prd_is_valid(self) -> None:
        self.assertEqual(build_sample_prd().validate(), [])

    def test_duplicate_requirement_ids_are_rejected(self) -> None:
        prd = build_sample_prd()
        prd.requirements.append(prd.requirements[0])
        self.assertTrue(
            any("Requirement IDs must be unique" in error for error in prd.validate())
        )

    def test_unknown_dependency_is_rejected(self) -> None:
        prd = build_sample_prd()
        prd.requirements[0].dependencies.append("REQ-DOES-NOT-EXIST")
        self.assertTrue(
            any("unknown dependency" in error for error in prd.validate())
        )

    def test_dependency_cycle_is_detected(self) -> None:
        prd = build_sample_prd()
        prd.requirements[0].dependencies.append("REQ-PORTAL-002")
        errors = prd.validate()
        self.assertTrue(any("cycle detected" in error for error in errors))

    def test_risk_scoring(self) -> None:
        risk = Risk("RISK-TEST", "Example", 5, 5, "Mitigate", "Owner", "Contain")
        self.assertEqual(risk.score, 25)
        self.assertEqual(risk.severity, RiskSeverity.CRITICAL)

    def test_release_readiness_requires_valid_prd_and_must_approval(self) -> None:
        prd = build_sample_prd()
        self.assertFalse(prd.readiness_report()["release_ready"])
        for requirement in prd.requirements:
            if requirement.priority == Priority.MUST:
                requirement.status = RequirementStatus.APPROVED
        self.assertTrue(prd.readiness_report()["release_ready"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate, analyze, test, and export a product requirements document."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for the generated PRD.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Export format.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the built-in tests.",
    )
    args = parser.parse_args()

    if args.test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(PRDTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            return 1

    prd = build_sample_prd()
    errors = prd.validate()

    print(f"PRD: {prd.product_name} v{prd.version}")
    print(f"Validation: {'PASS' if not errors else 'FAIL'}")
    for error in errors:
        print(f"ERROR: {error}")

    demonstrate_requirement_prioritization(prd)
    demonstrate_risk_analysis(prd)

    report = prd.readiness_report()
    print("\nReadiness report")
    print(json.dumps(report, indent=2))

    if args.output:
        if errors:
            print("Export blocked because validation failed.", file=sys.stderr)
            return 2

        content = (
            json.dumps(to_json_compatible(prd), indent=2)
            if args.format == "json"
            else render_markdown(prd)
        )
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + ("" if content.endswith("\n") else "\n"),
                                   encoding="utf-8")
        except OSError as exc:
            print(f"Could not write output: {exc}", file=sys.stderr)
            return 3
        print(f"\nExported validated PRD to {args.output}")

    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
