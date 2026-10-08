from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json
import math


class HypothesisStatus(str, Enum):
    PROPOSED = "proposed"
    VALIDATED = "validated"
    REJECTED = "rejected"


class ConstraintType(str, Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    REGULATORY = "regulatory"


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    SELECTED = "selected"
    REJECTED = "rejected"


@dataclass
class SolutionHypothesis:
    identifier: str
    statement: str
    evidence_required: str
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: float = 0.5

    def validate(self, evidence_quality: float, observed_value: float,
                 expected_min: float) -> None:
        if not 0 <= evidence_quality <= 1:
            raise ValueError("Evidence quality must be between 0 and 1.")
        if observed_value >= expected_min:
            self.status = HypothesisStatus.VALIDATED
            self.confidence = min(1.0, 0.5 + 0.5 * evidence_quality)
        else:
            self.status = HypothesisStatus.REJECTED
            self.confidence = max(0.0, 0.5 * (1 - evidence_quality))


@dataclass
class Constraint:
    identifier: str
    description: str
    constraint_type: ConstraintType
    hard: bool = True


@dataclass
class Alternative:
    name: str
    description: str
    delivery_cost: float
    operating_cost: float
    expected_value: float
    implementation_risk: float
    scalability: float
    maintainability: float
    reversibility: float
    constraint_penalty: float = 0.0

    def score(self) -> float:
        # Value is rewarded. Cost, risk, and constraint violations reduce the score.
        return (
            self.expected_value
            + 0.20 * self.scalability
            + 0.15 * self.maintainability
            + 0.10 * self.reversibility
            - 0.35 * self.implementation_risk
            - 0.15 * self.delivery_cost
            - 0.10 * self.operating_cost
            - self.constraint_penalty
        )


@dataclass
class TradeOff:
    criterion: str
    preferred: str
    rationale: str


@dataclass
class SolutionDecision:
    selected: Alternative
    rejected: List[Alternative]
    trade_offs: List[TradeOff]
    assumptions: List[str] = field(default_factory=list)


class SolutionDesign:
    """
    A small decision engine for a realistic design problem.

    Scenario:
    A service receives operational events from several systems. The design
    team must choose between:
      - a direct synchronous API,
      - a queue-backed asynchronous architecture,
      - a managed event-streaming architecture.

    The engine separates:
      hypotheses -> constraints -> alternatives -> trade-offs -> decision.
    """

    def __init__(self, name: str):
        self.name = name
        self.hypotheses: Dict[str, SolutionHypothesis] = {}
        self.constraints: Dict[str, Constraint] = {}
        self.alternatives: Dict[str, Alternative] = {}

    def add_hypothesis(self, hypothesis: SolutionHypothesis) -> None:
        if hypothesis.identifier in self.hypotheses:
            raise ValueError(f"Duplicate hypothesis: {hypothesis.identifier}")
        self.hypotheses[hypothesis.identifier] = hypothesis

    def add_constraint(self, constraint: Constraint) -> None:
        if constraint.identifier in self.constraints:
            raise ValueError(f"Duplicate constraint: {constraint.identifier}")
        self.constraints[constraint.identifier] = constraint

    def add_alternative(self, alternative: Alternative) -> None:
        if alternative.name in self.alternatives:
            raise ValueError(f"Duplicate alternative: {alternative.name}")
        self.alternatives[alternative.name] = alternative

    def validate_required_hypotheses(self) -> None:
        unresolved = [
            h.identifier
            for h in self.hypotheses.values()
            if h.status == HypothesisStatus.PROPOSED
        ]
        if unresolved:
            raise RuntimeError(
                "Design contains unresolved hypotheses: " + ", ".join(unresolved)
            )

    def evaluate_alternatives(self) -> List[Tuple[str, float]]:
        self.validate_required_hypotheses()
        return sorted(
            ((a.name, a.score()) for a in self.alternatives.values()),
            key=lambda item: item[1],
            reverse=True,
        )

    def choose(self) -> SolutionDecision:
        rankings = self.evaluate_alternatives()
        if not rankings:
            raise RuntimeError("No solution alternatives have been defined.")

        selected_name = rankings[0][0]
        selected = self.alternatives[selected_name]
        rejected = [
            self.alternatives[name]
            for name, _ in rankings[1:]
        ]

        trade_offs = [
            TradeOff(
                "Latency",
                "Queue-backed asynchronous architecture",
                "It accepts work quickly while allowing consumers to process "
                "events independently."
            ),
            TradeOff(
                "Operational simplicity",
                "Direct synchronous API",
                "It has fewer moving parts and is easier to debug initially."
            ),
            TradeOff(
                "High-throughput event distribution",
                "Managed event-streaming architecture",
                "Partitioned streams provide stronger throughput and replay "
                "characteristics, at the cost of greater operational complexity."
            ),
        ]

        return SolutionDecision(
            selected=selected,
            rejected=rejected,
            trade_offs=trade_offs,
            assumptions=[
                "Traffic is bursty rather than perfectly uniform.",
                "Some operations can complete asynchronously.",
                "The system needs durable processing rather than best-effort delivery.",
            ],
        )


def demonstrate_hypothesis_testing() -> None:
    print("\n=== Solution hypotheses ===")

    hypothesis = SolutionHypothesis(
        identifier="H-ASYNC",
        statement="Asynchronous processing can absorb traffic bursts without "
                  "blocking the requesting client.",
        evidence_required="Load-test latency and queue-depth measurements.",
    )

    print("Before evidence:", hypothesis.status.value, hypothesis.confidence)

    # A measured p95 latency improvement of 0.91 means the hypothesis met
    # the expected minimum improvement of 0.80.
    hypothesis.validate(
        evidence_quality=0.90,
        observed_value=0.91,
        expected_min=0.80,
    )

    print("After evidence:", hypothesis.status.value, hypothesis.confidence)


def build_design() -> SolutionDesign:
    design = SolutionDesign("Operational Event Intake")

    design.add_hypothesis(
        SolutionHypothesis(
            "H-ASYNC",
            "Asynchronous processing reduces client-visible latency during bursts.",
            "Load-test measurements of p95 latency and queue depth.",
        )
    )
    design.add_hypothesis(
        SolutionHypothesis(
            "H-DURABLE",
            "Durable buffering prevents transient downstream failures from "
            "causing data loss.",
            "Failure-injection test showing recoverable messages after consumer failure.",
        )
    )
    design.add_hypothesis(
        SolutionHypothesis(
            "H-REPLAY",
            "Replay is valuable when downstream transformations change.",
            "Operational incidents demonstrating the need to reprocess historical events.",
        )
    )

    # Evidence converts assumptions into explicit design inputs.
    design.hypotheses["H-ASYNC"].validate(0.90, 0.91, 0.80)
    design.hypotheses["H-DURABLE"].validate(0.95, 0.98, 0.90)
    design.hypotheses["H-REPLAY"].validate(0.75, 0.86, 0.70)

    design.add_constraint(Constraint(
        "C-LATENCY",
        "The client-facing acknowledgement should normally complete within 300 ms.",
        ConstraintType.NON_FUNCTIONAL,
    ))
    design.add_constraint(Constraint(
        "C-DURABILITY",
        "Accepted events must survive a consumer restart.",
        ConstraintType.TECHNICAL,
    ))
    design.add_constraint(Constraint(
        "C-BUDGET",
        "Initial infrastructure and operational cost must remain moderate.",
        ConstraintType.BUSINESS,
    ))
    design.add_constraint(Constraint(
        "C-AUDIT",
        "Processing outcomes must be traceable for operational investigation.",
        ConstraintType.REGULATORY,
    ))

    design.add_alternative(Alternative(
        name="Direct synchronous API",
        description="Client calls the processing service and waits for completion.",
        delivery_cost=2.0,
        operating_cost=2.0,
        expected_value=6.0,
        implementation_risk=2.0,
        scalability=4.0,
        maintainability=7.0,
        reversibility=8.0,
        constraint_penalty=3.0,
    ))

    design.add_alternative(Alternative(
        name="Queue-backed asynchronous architecture",
        description="API validates and persists the event, then acknowledges it "
                    "while workers consume durable queue messages.",
        delivery_cost=4.0,
        operating_cost=4.0,
        expected_value=9.0,
        implementation_risk=3.0,
        scalability=8.0,
        maintainability=8.0,
        reversibility=8.0,
        constraint_penalty=0.0,
    ))

    design.add_alternative(Alternative(
        name="Managed event-streaming architecture",
        description="Events are published to partitioned streams with replayable "
                    "consumer groups.",
        delivery_cost=7.0,
        operating_cost=6.0,
        expected_value=9.5,
        implementation_risk=5.0,
        scalability=10.0,
        maintainability=6.0,
        reversibility=5.0,
        constraint_penalty=1.5,
    ))

    return design


def print_decision(decision: SolutionDecision) -> None:
    print("\n=== Solution decision ===")
    print("Selected:", decision.selected.name)
    print("Score:", round(decision.selected.score(), 3))
    print("\nRejected alternatives:")
    for alternative in decision.rejected:
        print(f"  {alternative.name}: {alternative.score():.3f}")

    print("\nTrade-offs:")
    for tradeoff in decision.trade_offs:
        print(f"  {tradeoff.criterion}: {tradeoff.preferred}")
        print(f"    {tradeoff.rationale}")

    print("\nExplicit assumptions:")
    for assumption in decision.assumptions:
        print(" ", assumption)


def run_sensitivity_analysis(design: SolutionDesign) -> None:
    print("\n=== Sensitivity analysis ===")

    original = design.alternatives["Queue-backed asynchronous architecture"]

    scenarios = {
        "Lower traffic": {"scalability": -2.0, "delivery_cost": -1.0},
        "Higher traffic": {"scalability": +2.0},
        "Tighter budget": {"delivery_cost": +2.0, "operating_cost": +1.0},
        "Replay becomes mandatory": {"constraint_penalty": -1.5},
    }

    for scenario_name, changes in scenarios.items():
        modified = Alternative(**vars(original))
        for field_name, delta in changes.items():
            setattr(modified, field_name, getattr(modified, field_name) + delta)

        print(
            f"{scenario_name}: "
            f"baseline={original.score():.3f}, "
            f"scenario={modified.score():.3f}"
        )


def export_decision(design: SolutionDesign, decision: SolutionDecision) -> str:
    result = {
        "solution": design.name,
        "selected": {
            "name": decision.selected.name,
            "score": round(decision.selected.score(), 3),
        },
        "hypotheses": {
            key: {
                "status": value.status.value,
                "confidence": round(value.confidence, 3),
            }
            for key, value in design.hypotheses.items()
        },
        "constraints": [
            {
                "id": c.identifier,
                "type": c.constraint_type.value,
                "hard": c.hard,
                "description": c.description,
            }
            for c in design.constraints.values()
        ],
        "alternatives": [
            {
                "name": a.name,
                "score": round(a.score(), 3),
                "risk": a.implementation_risk,
            }
            for a in design.alternatives.values()
        ],
    }
    return json.dumps(result, indent=2)


def main() -> None:
    demonstrate_hypothesis_testing()

    design = build_design()

    print("\n=== Design constraints ===")
    for constraint in design.constraints.values():
        print(
            f"{constraint.identifier} [{constraint.constraint_type.value}] "
            f"{'HARD' if constraint.hard else 'SOFT'}: "
            f"{constraint.description}"
        )

    print("\n=== Alternative ranking ===")
    for name, score in design.evaluate_alternatives():
        print(f"{name}: {score:.3f}")

    decision = design.choose()
    print_decision(decision)
    run_sensitivity_analysis(design)

    print("\n=== Machine-readable decision record ===")
    print(export_decision(design, decision))


if __name__ == "__main__":
    main()
