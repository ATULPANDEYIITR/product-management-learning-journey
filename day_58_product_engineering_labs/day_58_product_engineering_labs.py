#!/usr/bin/env python3
"""
Product-Engineering Collaboration Model

Models collaboration between product and engineering teams around:
- requirements
- estimation
- feasibility
- architecture decisions
- trade-offs
- risks
- decisions
- implementation readiness

The implementation is intentionally independent of any external service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple
import json
import math
import re
import sys


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkState(Enum):
    PROPOSED = "proposed"
    DISCOVERY = "discovery"
    ESTIMATED = "estimated"
    READY = "ready"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class DecisionStatus(Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TradeOffType(Enum):
    SPEED = "speed"
    QUALITY = "quality"
    COST = "cost"
    SCOPE = "scope"
    SECURITY = "security"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"


class CollaborationError(Exception):
    """Base domain exception."""


class ValidationError(CollaborationError):
    """Invalid domain input."""


class StateTransitionError(CollaborationError):
    """Illegal workflow transition."""


@dataclass(frozen=True)
class Estimate:
    story_points: int
    engineering_days: float
    confidence: float

    def __post_init__(self) -> None:
        if self.story_points <= 0:
            raise ValidationError("Story points must be positive.")
        if self.engineering_days <= 0:
            raise ValidationError("Engineering days must be positive.")
        if not 0 < self.confidence <= 1:
            raise ValidationError("Confidence must be between 0 and 1.")


@dataclass
class Requirement:
    key: str
    title: str
    description: str
    acceptance_criteria: List[str]
    priority: Priority
    dependencies: Set[str] = field(default_factory=set)
    estimate: Estimate | None = None
    state: WorkState = WorkState.PROPOSED
    risks: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Z]{2,8}-\d{1,6}", self.key):
            raise ValidationError(f"Invalid requirement key: {self.key}")
        if not self.title.strip():
            raise ValidationError("Requirement title cannot be empty.")
        if not self.description.strip():
            raise ValidationError("Requirement description cannot be empty.")
        if not self.acceptance_criteria:
            raise ValidationError("At least one acceptance criterion is required.")
        if any(not criterion.strip() for criterion in self.acceptance_criteria):
            raise ValidationError("Acceptance criteria cannot be empty.")


@dataclass(frozen=True)
class ArchitectureOption:
    name: str
    description: str
    delivery_days: float
    monthly_cost: float
    scalability_score: int
    maintainability_score: int
    security_score: int
    complexity_score: int

    def __post_init__(self) -> None:
        if self.delivery_days <= 0 or self.monthly_cost < 0:
            raise ValidationError("Architecture cost and delivery values are invalid.")
        scores = (
            self.scalability_score,
            self.maintainability_score,
            self.security_score,
            self.complexity_score,
        )
        if any(score < 1 or score > 5 for score in scores):
            raise ValidationError("Architecture scores must be between 1 and 5.")


@dataclass(frozen=True)
class Decision:
    decision_id: str
    title: str
    chosen_option: str
    rationale: str
    trade_offs: Tuple[str, ...]
    status: DecisionStatus = DecisionStatus.ACCEPTED

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.chosen_option.strip():
            raise ValidationError("Decision title and chosen option are required.")
        if not self.rationale.strip():
            raise ValidationError("Decision rationale is required.")


@dataclass
class CollaborationRecord:
    requirement: Requirement
    architecture_options: List[ArchitectureOption] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)

    def add_architecture_option(self, option: ArchitectureOption) -> None:
        if any(existing.name == option.name for existing in self.architecture_options):
            raise ValidationError(f"Duplicate architecture option: {option.name}")
        self.architecture_options.append(option)

    def add_decision(self, decision: Decision) -> None:
        self.decisions.append(decision)

    def set_estimate(self, estimate: Estimate) -> None:
        self.requirement.estimate = estimate
        if self.requirement.state in {
            WorkState.PROPOSED,
            WorkState.DISCOVERY,
        }:
            self.requirement.state = WorkState.ESTIMATED

    def transition(self, new_state: WorkState) -> None:
        allowed: Dict[WorkState, Set[WorkState]] = {
            WorkState.PROPOSED: {WorkState.DISCOVERY},
            WorkState.DISCOVERY: {WorkState.ESTIMATED, WorkState.BLOCKED},
            WorkState.ESTIMATED: {WorkState.READY, WorkState.BLOCKED},
            WorkState.READY: {WorkState.IN_PROGRESS, WorkState.BLOCKED},
            WorkState.BLOCKED: {WorkState.DISCOVERY, WorkState.READY},
            WorkState.IN_PROGRESS: {WorkState.DONE, WorkState.BLOCKED},
            WorkState.DONE: set(),
        }

        if new_state not in allowed[self.requirement.state]:
            raise StateTransitionError(
                f"Cannot transition {self.requirement.state.value} "
                f"to {new_state.value}."
            )

        if new_state == WorkState.READY:
            self.assert_ready()

        self.requirement.state = new_state

    def assert_ready(self) -> None:
        self.requirement.validate()

        if self.requirement.estimate is None:
            raise ValidationError("A requirement must be estimated before it is ready.")

        if self.requirement.estimate.confidence < 0.6:
            raise ValidationError("Estimate confidence is too low.")

        if not self.architecture_options:
            raise ValidationError("At least one architecture option is required.")

        accepted = [
            decision for decision in self.decisions
            if decision.status == DecisionStatus.ACCEPTED
        ]
        if not accepted:
            raise ValidationError("At least one architecture decision is required.")

        if self.requirement.dependencies:
            unresolved = {
                dependency
                for dependency in self.requirement.dependencies
                if dependency.startswith("BLOCKED:")
            }
            if unresolved:
                raise ValidationError(
                    f"Unresolved dependencies: {sorted(unresolved)}"
                )


class ArchitectureEvaluator:
    """Scores options using explicit product-engineering priorities."""

    def __init__(
        self,
        weights: Dict[TradeOffType, float],
    ) -> None:
        if not weights:
            raise ValidationError("At least one trade-off weight is required.")
        if any(weight < 0 for weight in weights.values()):
            raise ValidationError("Trade-off weights cannot be negative.")
        if sum(weights.values()) == 0:
            raise ValidationError("At least one trade-off weight must be positive.")
        self.weights = weights

    def score(self, option: ArchitectureOption) -> float:
        total = 0.0

        total += self.weights.get(TradeOffType.SPEED, 0) * (
            1 / option.delivery_days
        )
        total += self.weights.get(TradeOffType.COST, 0) * (
            1 / max(option.monthly_cost, 1)
        )
        total += self.weights.get(
            TradeOffType.SCALABILITY, 0
        ) * option.scalability_score
        total += self.weights.get(
            TradeOffType.MAINTAINABILITY, 0
        ) * option.maintainability_score
        total += self.weights.get(
            TradeOffType.SECURITY, 0
        ) * option.security_score
        total += self.weights.get(
            TradeOffType.QUALITY, 0
        ) * (6 - option.complexity_score)

        return total

    def rank(
        self,
        options: List[ArchitectureOption],
    ) -> List[Tuple[ArchitectureOption, float]]:
        return sorted(
            ((option, self.score(option)) for option in options),
            key=lambda item: item[1],
            reverse=True,
        )


def build_example() -> CollaborationRecord:
    requirement = Requirement(
        key="PAY-104",
        title="Add idempotent payment retry handling",
        description=(
            "Allow a failed payment request to be safely retried without "
            "creating duplicate charges."
        ),
        acceptance_criteria=[
            "Repeated requests with the same idempotency key produce one charge.",
            "A retry returns the original payment result when available.",
            "Concurrent duplicate requests cannot create two charges.",
            "Sensitive payment details are never written to application logs.",
        ],
        priority=Priority.CRITICAL,
        dependencies={"PAY-101"},
        risks=[
            "Concurrent retries may race.",
            "Persistent idempotency records increase storage usage.",
        ],
    )

    record = CollaborationRecord(requirement)

    record.transition(WorkState.DISCOVERY)

    options = [
        ArchitectureOption(
            name="Database-backed idempotency",
            description="Persist idempotency keys and results in PostgreSQL.",
            delivery_days=5,
            monthly_cost=180,
            scalability_score=4,
            maintainability_score=5,
            security_score=5,
            complexity_score=2,
        ),
        ArchitectureOption(
            name="Distributed cache",
            description="Use a shared cache with expiration for request keys.",
            delivery_days=3,
            monthly_cost=320,
            scalability_score=5,
            maintainability_score=3,
            security_score=4,
            complexity_score=4,
        ),
        ArchitectureOption(
            name="Process-local memory",
            description="Keep idempotency keys in application memory.",
            delivery_days=1,
            monthly_cost=20,
            scalability_score=1,
            maintainability_score=2,
            security_score=2,
            complexity_score=1,
        ),
    ]

    for option in options:
        record.add_architecture_option(option)

    evaluator = ArchitectureEvaluator(
        {
            TradeOffType.SPEED: 0.20,
            TradeOffType.COST: 0.05,
            TradeOffType.SCALABILITY: 0.20,
            TradeOffType.MAINTAINABILITY: 0.20,
            TradeOffType.SECURITY: 0.25,
            TradeOffType.QUALITY: 0.10,
        }
    )

    ranking = evaluator.rank(record.architecture_options)
    chosen = ranking[0][0]

    record.add_decision(
        Decision(
            decision_id="ADR-014",
            title="Payment retry architecture",
            chosen_option=chosen.name,
            rationale=(
                "The database-backed design provides concurrency control, "
                "durable state, strong security characteristics, and simpler "
                "operational ownership than the distributed-cache alternative."
            ),
            trade_offs=(
                "Slightly slower implementation than process-local memory.",
                "Additional database storage and write traffic.",
            ),
        )
    )

    record.set_estimate(Estimate(8, 5.0, 0.82))
    record.transition(WorkState.READY)
    return record


def serialize_record(record: CollaborationRecord) -> str:
    payload = {
        "requirement": {
            "key": record.requirement.key,
            "title": record.requirement.title,
            "priority": record.requirement.priority.value,
            "state": record.requirement.state.value,
            "estimate": {
                "story_points": record.requirement.estimate.story_points,
                "engineering_days": record.requirement.estimate.engineering_days,
                "confidence": record.requirement.estimate.confidence,
            } if record.requirement.estimate else None,
            "dependencies": sorted(record.requirement.dependencies),
            "risks": record.requirement.risks,
        },
        "architecture_options": [
            {
                "name": option.name,
                "delivery_days": option.delivery_days,
                "monthly_cost": option.monthly_cost,
                "scalability_score": option.scalability_score,
                "maintainability_score": option.maintainability_score,
                "security_score": option.security_score,
                "complexity_score": option.complexity_score,
            }
            for option in record.architecture_options
        ],
        "decisions": [
            {
                "decision_id": decision.decision_id,
                "title": decision.title,
                "chosen_option": decision.chosen_option,
                "status": decision.status.value,
                "trade_offs": list(decision.trade_offs),
            }
            for decision in record.decisions
        ],
    }
    return json.dumps(payload, indent=2)


def run_edge_case_checks() -> None:
    try:
        Estimate(0, 2, 0.8)
    except ValidationError:
        pass
    else:
        raise AssertionError("Invalid estimate was accepted.")

    try:
        record = build_example()
        record.transition(WorkState.DONE)
    except StateTransitionError:
        pass
    else:
        raise AssertionError("Invalid state transition was accepted.")

    try:
        bad_requirement = Requirement(
            key="invalid",
            title="",
            description="",
            acceptance_criteria=[],
            priority=Priority.HIGH,
        )
        bad_requirement.validate()
    except ValidationError:
        pass
    else:
        raise AssertionError("Invalid requirement was accepted.")


def main() -> int:
    run_edge_case_checks()

    record = build_example()
    evaluator = ArchitectureEvaluator(
        {
            TradeOffType.SPEED: 0.20,
            TradeOffType.SCALABILITY: 0.20,
            TradeOffType.MAINTAINABILITY: 0.20,
            TradeOffType.SECURITY: 0.30,
            TradeOffType.QUALITY: 0.10,
        }
    )

    ranking = evaluator.rank(record.architecture_options)

    print("PRODUCT-ENGINEERING COLLABORATION CASE")
    print("=" * 48)
    print(f"Requirement : {record.requirement.key}")
    print(f"Title       : {record.requirement.title}")
    print(f"Priority    : {record.requirement.priority.value}")
    print(f"State       : {record.requirement.state.value}")
    print(
        f"Estimate    : {record.requirement.estimate.story_points} points, "
        f"{record.requirement.estimate.engineering_days:.1f} days, "
        f"{record.requirement.estimate.confidence:.0%} confidence"
    )

    print("\nArchitecture ranking:")
    for index, (option, score) in enumerate(ranking, 1):
        print(
            f"{index}. {option.name}: score={score:.4f}, "
            f"delivery={option.delivery_days:.1f}d, "
            f"cost=${option.monthly_cost:.2f}/month"
        )

    print("\nAccepted decision:")
    for decision in record.decisions:
        print(f"{decision.decision_id}: {decision.chosen_option}")
        print(f"Rationale: {decision.rationale}")

    print("\nSerialized collaboration record:")
    print(serialize_record(record))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CollaborationError as exc:
        print(f"Domain error: {exc}", file=sys.stderr)
        raise SystemExit(1)
