#!/usr/bin/env python3
"""
Assumptions & Hypotheses
------------------------
A self-contained technical learning implementation for mapping assumptions and
hypotheses across desirability, viability, feasibility, and risk.

The program models an assumption registry, converts assumptions into testable
hypotheses, scores them, records evidence, evaluates confidence, and produces
an experiment portfolio.

The implementation deliberately distinguishes:
- Assumption: something believed to be true but not yet sufficiently evidenced.
- Hypothesis: a falsifiable statement derived from an assumption.
- Desirability: whether users or stakeholders want the proposed outcome.
- Viability: whether the outcome can support a sustainable business or operating model.
- Feasibility: whether the organization can technically and operationally deliver it.
- Risk: uncertainty that could materially damage the initiative if the assumption is wrong.

Run:
    python assumptions_hypotheses.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import json
import math
import tempfile
from pathlib import Path


class Dimension(str, Enum):
    DESIRABILITY = "desirability"
    VIABILITY = "viability"
    FEASIBILITY = "feasibility"
    RISK = "risk"


class EvidenceType(str, Enum):
    INTERVIEW = "interview"
    SURVEY = "survey"
    EXPERIMENT = "experiment"
    PROTOTYPE = "prototype"
    FINANCIAL_MODEL = "financial_model"
    TECHNICAL_SPIKE = "technical_spike"
    PRODUCTION_DATA = "production_data"
    DOCUMENT_REVIEW = "document_review"


class HypothesisStatus(str, Enum):
    UNTESTED = "untested"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class Evidence:
    source: str
    evidence_type: EvidenceType
    strength: float
    supports: bool
    observation: str

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("Evidence source cannot be empty.")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("Evidence strength must be between 0 and 1.")
        if not self.observation.strip():
            raise ValueError("Evidence observation cannot be empty.")


@dataclass
class Assumption:
    assumption_id: str
    statement: str
    dimension: Dimension
    confidence: float
    impact: float
    uncertainty: float
    owner: str
    rationale: str
    evidence: List[Evidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.assumption_id.strip():
            raise ValueError("Assumption ID cannot be empty.")
        if not self.statement.strip():
            raise ValueError("Assumption statement cannot be empty.")
        if not self.owner.strip():
            raise ValueError("Assumption owner cannot be empty.")

        for name, value in (
            ("confidence", self.confidence),
            ("impact", self.impact),
            ("uncertainty", self.uncertainty),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1.")

    @property
    def exposure(self) -> float:
        """Risk exposure rises with impact and uncertainty."""
        return self.impact * self.uncertainty

    @property
    def evidence_confidence(self) -> float:
        """
        Estimate confidence from directional evidence.

        Evidence is weighted by strength. Supporting evidence contributes
        positively, contradictory evidence contributes negatively.
        """
        if not self.evidence:
            return 0.0

        weighted_support = sum(
            item.strength if item.supports else -item.strength
            for item in self.evidence
        )
        total_weight = sum(item.strength for item in self.evidence)

        if total_weight == 0:
            return 0.0

        normalized = (weighted_support / total_weight + 1.0) / 2.0
        return max(0.0, min(1.0, normalized))


@dataclass
class Hypothesis:
    hypothesis_id: str
    assumption_id: str
    statement: str
    metric: str
    threshold: float
    direction: str
    sample_requirement: int
    status: HypothesisStatus = HypothesisStatus.UNTESTED
    observed_value: Optional[float] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError("Hypothesis ID cannot be empty.")
        if not self.assumption_id.strip():
            raise ValueError("Hypothesis must reference an assumption.")
        if not self.statement.strip():
            raise ValueError("Hypothesis statement cannot be empty.")
        if not self.metric.strip():
            raise ValueError("Hypothesis metric cannot be empty.")
        if self.direction not in {"at_least", "at_most"}:
            raise ValueError("Direction must be 'at_least' or 'at_most'.")
        if self.sample_requirement <= 0:
            raise ValueError("Sample requirement must be positive.")

    def evaluate(self, observed_value: float) -> HypothesisStatus:
        """Evaluate a measured result against the predefined falsification rule."""
        if not math.isfinite(observed_value):
            raise ValueError("Observed value must be finite.")

        self.observed_value = observed_value

        if self.direction == "at_least":
            passed = observed_value >= self.threshold
        else:
            passed = observed_value <= self.threshold

        self.status = (
            HypothesisStatus.SUPPORTED
            if passed
            else HypothesisStatus.REFUTED
        )
        return self.status


@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    hypothesis_id: str
    method: str
    cost: float
    duration_days: int
    expected_information_gain: float

    def __post_init__(self) -> None:
        if self.cost < 0:
            raise ValueError("Experiment cost cannot be negative.")
        if self.duration_days <= 0:
            raise ValueError("Experiment duration must be positive.")
        if not 0.0 <= self.expected_information_gain <= 1.0:
            raise ValueError("Information gain must be between 0 and 1.")


class AssumptionRegistry:
    """Central registry for assumptions, hypotheses, evidence, and experiments."""

    def __init__(self) -> None:
        self.assumptions: Dict[str, Assumption] = {}
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.experiments: Dict[str, Experiment] = {}

    def add_assumption(self, assumption: Assumption) -> None:
        if assumption.assumption_id in self.assumptions:
            raise ValueError(
                f"Assumption '{assumption.assumption_id}' already exists."
            )
        self.assumptions[assumption.assumption_id] = assumption

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        if hypothesis.hypothesis_id in self.hypotheses:
            raise ValueError(
                f"Hypothesis '{hypothesis.hypothesis_id}' already exists."
            )
        if hypothesis.assumption_id not in self.assumptions:
            raise KeyError(
                f"Unknown assumption '{hypothesis.assumption_id}'."
            )
        self.hypotheses[hypothesis.hypothesis_id] = hypothesis

    def add_experiment(self, experiment: Experiment) -> None:
        if experiment.experiment_id in self.experiments:
            raise ValueError(
                f"Experiment '{experiment.experiment_id}' already exists."
            )
        if experiment.hypothesis_id not in self.hypotheses:
            raise KeyError(
                f"Unknown hypothesis '{experiment.hypothesis_id}'."
            )
        self.experiments[experiment.experiment_id] = experiment

    def attach_evidence(
        self,
        assumption_id: str,
        evidence: Evidence,
    ) -> None:
        if assumption_id not in self.assumptions:
            raise KeyError(f"Unknown assumption '{assumption_id}'.")
        self.assumptions[assumption_id].evidence.append(evidence)

    def evaluate_hypothesis(
        self,
        hypothesis_id: str,
        observed_value: float,
    ) -> HypothesisStatus:
        if hypothesis_id not in self.hypotheses:
            raise KeyError(f"Unknown hypothesis '{hypothesis_id}'.")
        return self.hypotheses[hypothesis_id].evaluate(observed_value)

    def highest_exposure(
        self,
        dimension: Optional[Dimension] = None,
    ) -> List[Assumption]:
        candidates = self.assumptions.values()

        if dimension is not None:
            candidates = (
                item for item in candidates
                if item.dimension == dimension
            )

        return sorted(
            candidates,
            key=lambda item: item.exposure,
            reverse=True,
        )

    def experiment_priority(self, hypothesis_id: str) -> float:
        """
        Prioritize experiments using uncertainty, impact, information gain,
        and cost.

        The score is intentionally a decision aid rather than a statistical
        probability. It helps allocate limited validation resources.
        """
        hypothesis = self.hypotheses[hypothesis_id]
        assumption = self.assumptions[hypothesis.assumption_id]

        related = [
            experiment
            for experiment in self.experiments.values()
            if experiment.hypothesis_id == hypothesis_id
        ]

        if not related:
            return 0.0

        best_experiment = max(
            related,
            key=lambda item: item.expected_information_gain / max(item.cost, 1.0),
        )

        value_density = (
            best_experiment.expected_information_gain
            / max(best_experiment.cost, 1.0)
        )

        return (
            assumption.exposure
            * value_density
            * (1.0 - assumption.evidence_confidence)
        )

    def decision_snapshot(self) -> Dict[str, object]:
        """Return structured information suitable for dashboards or APIs."""
        return {
            "assumption_count": len(self.assumptions),
            "hypothesis_count": len(self.hypotheses),
            "experiment_count": len(self.experiments),
            "by_dimension": {
                dimension.value: sum(
                    1
                    for item in self.assumptions.values()
                    if item.dimension == dimension
                )
                for dimension in Dimension
            },
            "hypothesis_status": {
                status.value: sum(
                    1
                    for item in self.hypotheses.values()
                    if item.status == status
                )
                for status in HypothesisStatus
            },
        }

    def to_json(self) -> str:
        """Serialize the registry without relying on third-party packages."""
        payload = {
            "assumptions": [
                {
                    "id": item.assumption_id,
                    "statement": item.statement,
                    "dimension": item.dimension.value,
                    "confidence": item.confidence,
                    "impact": item.impact,
                    "uncertainty": item.uncertainty,
                    "owner": item.owner,
                    "rationale": item.rationale,
                    "evidence_confidence": item.evidence_confidence,
                    "exposure": item.exposure,
                }
                for item in self.assumptions.values()
            ],
            "hypotheses": [
                {
                    "id": item.hypothesis_id,
                    "assumption_id": item.assumption_id,
                    "statement": item.statement,
                    "metric": item.metric,
                    "threshold": item.threshold,
                    "direction": item.direction,
                    "sample_requirement": item.sample_requirement,
                    "status": item.status.value,
                    "observed_value": item.observed_value,
                    "notes": item.notes,
                }
                for item in self.hypotheses.values()
            ],
            "experiments": [
                {
                    "id": item.experiment_id,
                    "hypothesis_id": item.hypothesis_id,
                    "method": item.method,
                    "cost": item.cost,
                    "duration_days": item.duration_days,
                    "expected_information_gain": item.expected_information_gain,
                }
                for item in self.experiments.values()
            ],
        }

        return json.dumps(payload, indent=2)


def print_heading(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def demonstrate_fundamentals() -> None:
    print_heading("Assumption and hypothesis fundamentals")

    assumption = Assumption(
        assumption_id="A-DES-001",
        statement="Target users experience enough friction in manual status reporting to value automated reporting.",
        dimension=Dimension.DESIRABILITY,
        confidence=0.35,
        impact=0.80,
        uncertainty=0.75,
        owner="Product Research",
        rationale="The problem has been observed informally, but willingness to change behavior is unverified.",
    )

    hypothesis = Hypothesis(
        hypothesis_id="H-DES-001",
        assumption_id=assumption.assumption_id,
        statement="At least 60% of qualified interview participants will rank automated status reporting as a high-priority problem.",
        metric="high-priority response rate",
        threshold=0.60,
        direction="at_least",
        sample_requirement=20,
    )

    print(f"Assumption: {assumption.statement}")
    print(f"Dimension: {assumption.dimension.value}")
    print(f"Risk exposure: {assumption.exposure:.2f}")
    print(f"Hypothesis: {hypothesis.statement}")

    result = hypothesis.evaluate(0.65)
    print(f"Observed rate: {hypothesis.observed_value:.2f}")
    print(f"Evaluation: {result.value}")


def build_realistic_registry() -> AssumptionRegistry:
    registry = AssumptionRegistry()

    registry.add_assumption(
        Assumption(
            assumption_id="A-DES-001",
            statement="Operations managers will adopt automated exception alerts because manual monitoring delays response.",
            dimension=Dimension.DESIRABILITY,
            confidence=0.40,
            impact=0.85,
            uncertainty=0.80,
            owner="Product",
            rationale="Operational interviews indicate monitoring pain, but adoption intent has not been measured.",
        )
    )

    registry.add_assumption(
        Assumption(
            assumption_id="A-DES-002",
            statement="Users will trust an alerting interface if every alert includes evidence explaining why it was generated.",
            dimension=Dimension.DESIRABILITY,
            confidence=0.45,
            impact=0.70,
            uncertainty=0.65,
            owner="UX Research",
            rationale="Trust is expected to depend on explainability, especially for high-impact exceptions.",
        )
    )

    registry.add_assumption(
        Assumption(
            assumption_id="A-VIA-001",
            statement="Customers will pay enough for automated monitoring to cover hosting, support, and operating costs.",
            dimension=Dimension.VIABILITY,
            confidence=0.30,
            impact=0.90,
            uncertainty=0.85,
            owner="Commercial",
            rationale="The proposed value is clear, but willingness to pay and acquisition economics are unknown.",
        )
    )

    registry.add_assumption(
        Assumption(
            assumption_id="A-VIA-002",
            statement="The expected reduction in manual monitoring time creates measurable economic value for customers.",
            dimension=Dimension.VIABILITY,
            confidence=0.50,
            impact=0.75,
            uncertainty=0.55,
            owner="Finance",
            rationale="Time savings have been estimated but not measured in a controlled customer workflow.",
        )
    )

    registry.add_assumption(
        Assumption(
            assumption_id="A-FEA-001",
            statement="The existing event-processing architecture can evaluate incoming events within the operational latency target.",
            dimension=Dimension.FEASIBILITY,
            confidence=0.65,
            impact=0.80,
            uncertainty=0.45,
            owner="Engineering",
            rationale="A small technical prototype indicates sufficient throughput, but peak load remains untested.",
        )
    )

    registry.add_assumption(
        Assumption(
            assumption_id="A-FEA-002",
            statement="The system can preserve tenant isolation while processing alerts for multiple customer organizations.",
            dimension=Dimension.FEASIBILITY,
            confidence=0.55,
            impact=0.95,
            uncertainty=0.50,
            owner="Platform Engineering",
            rationale="The architecture supports tenant identifiers, but isolation needs adversarial testing.",
        )
    )

    registry.add_assumption(
        Assumption(
            assumption_id="A-RISK-001",
            statement="A small percentage of false alerts will not cause customers to disable the monitoring feature.",
            dimension=Dimension.RISK,
            confidence=0.35,
            impact=0.90,
            uncertainty=0.80,
            owner="Risk",
            rationale="Alert fatigue can undermine adoption even when the underlying detection capability is useful.",
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-DES-001",
            assumption_id="A-DES-001",
            statement="At least 65% of qualified operations managers will select automated exception monitoring as a top-three workflow improvement.",
            metric="top-three selection rate",
            threshold=0.65,
            direction="at_least",
            sample_requirement=30,
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-DES-002",
            assumption_id="A-DES-002",
            statement="Providing evidence with each alert will produce a task-confidence score of at least 4.0 on a five-point scale.",
            metric="mean confidence score",
            threshold=4.0,
            direction="at_least",
            sample_requirement=25,
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-VIA-001",
            assumption_id="A-VIA-001",
            statement="At least 40% of qualified design partners will accept a proposed monthly price of 1200 monetary units.",
            metric="price acceptance rate",
            threshold=0.40,
            direction="at_least",
            sample_requirement=15,
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-VIA-002",
            assumption_id="A-VIA-002",
            statement="Automated monitoring will reduce manual exception-review time by at least 35% in a representative workflow.",
            metric="time reduction rate",
            threshold=0.35,
            direction="at_least",
            sample_requirement=10,
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-FEA-001",
            assumption_id="A-FEA-001",
            statement="The event processor will maintain p95 alert-evaluation latency at or below 250 milliseconds under representative peak load.",
            metric="p95 latency milliseconds",
            threshold=250.0,
            direction="at_most",
            sample_requirement=10000,
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-FEA-002",
            assumption_id="A-FEA-002",
            statement="Unauthorized cross-tenant reads will remain at zero across a controlled authorization test suite.",
            metric="cross-tenant read count",
            threshold=0.0,
            direction="at_most",
            sample_requirement=1000,
        )
    )

    registry.add_hypothesis(
        Hypothesis(
            hypothesis_id="H-RISK-001",
            assumption_id="A-RISK-001",
            statement="Fewer than 8% of active users will disable alerts after experiencing false-positive notifications.",
            metric="alert-disablement rate",
            threshold=0.08,
            direction="at_most",
            sample_requirement=50,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-DES-001",
            hypothesis_id="H-DES-001",
            method="Structured workflow interviews followed by a forced-priority prototype test",
            cost=800.0,
            duration_days=10,
            expected_information_gain=0.85,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-DES-002",
            hypothesis_id="H-DES-002",
            method="Prototype comparison with explanation-present and explanation-absent alert variants",
            cost=1200.0,
            duration_days=14,
            expected_information_gain=0.80,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-VIA-001",
            hypothesis_id="H-VIA-001",
            method="Price-sensitivity interviews using a controlled purchasing commitment question",
            cost=1000.0,
            duration_days=14,
            expected_information_gain=0.90,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-VIA-002",
            hypothesis_id="H-VIA-002",
            method="Before-and-after time study using identical exception-review workloads",
            cost=600.0,
            duration_days=7,
            expected_information_gain=0.75,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-FEA-001",
            hypothesis_id="H-FEA-001",
            method="Load test with production-shaped event distributions and latency measurement",
            cost=1500.0,
            duration_days=5,
            expected_information_gain=0.95,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-FEA-002",
            hypothesis_id="H-FEA-002",
            method="Automated authorization matrix and adversarial cross-tenant access test",
            cost=1800.0,
            duration_days=7,
            expected_information_gain=0.95,
        )
    )

    registry.add_experiment(
        Experiment(
            experiment_id="E-RISK-001",
            hypothesis_id="H-RISK-001",
            method="Controlled false-positive exposure with alert-disablement and retention tracking",
            cost=900.0,
            duration_days=21,
            expected_information_gain=0.88,
        )
    )

    return registry


def attach_realistic_evidence(registry: AssumptionRegistry) -> None:
    registry.attach_evidence(
        "A-DES-001",
        Evidence(
            source="Operations manager interviews",
            evidence_type=EvidenceType.INTERVIEW,
            strength=0.70,
            supports=True,
            observation="Managers consistently described manual exception monitoring as time-consuming.",
        ),
    )

    registry.attach_evidence(
        "A-DES-002",
        Evidence(
            source="Prototype usability session",
            evidence_type=EvidenceType.PROTOTYPE,
            strength=0.65,
            supports=True,
            observation="Participants reported greater confidence when alerts included evidence.",
        ),
    )

    registry.attach_evidence(
        "A-VIA-001",
        Evidence(
            source="Early customer discovery",
            evidence_type=EvidenceType.INTERVIEW,
            strength=0.55,
            supports=False,
            observation="Several prospects valued the capability but resisted the proposed price.",
        ),
    )

    registry.attach_evidence(
        "A-VIA-002",
        Evidence(
            source="Internal time study",
            evidence_type=EvidenceType.DOCUMENT_REVIEW,
            strength=0.60,
            supports=True,
            observation="Manual review consumed a substantial portion of the monitored workflow.",
        ),
    )

    registry.attach_evidence(
        "A-FEA-001",
        Evidence(
            source="Prototype load test",
            evidence_type=EvidenceType.TECHNICAL_SPIKE,
            strength=0.75,
            supports=True,
            observation="The processor remained within the target latency at moderate load.",
        ),
    )

    registry.attach_evidence(
        "A-FEA-002",
        Evidence(
            source="Authorization test suite",
            evidence_type=EvidenceType.TECHNICAL_SPIKE,
            strength=0.80,
            supports=True,
            observation="The current authorization matrix blocked tested cross-tenant requests.",
        ),
    )

    registry.attach_evidence(
        "A-RISK-001",
        Evidence(
            source="Pilot telemetry",
            evidence_type=EvidenceType.PRODUCTION_DATA,
            strength=0.70,
            supports=False,
            observation="False-positive alerts caused a noticeable increase in notification muting.",
        ),
    )


def evaluate_initial_results(registry: AssumptionRegistry) -> None:
    observations = {
        "H-DES-001": 0.72,
        "H-DES-002": 4.2,
        "H-VIA-001": 0.27,
        "H-VIA-002": 0.41,
        "H-FEA-001": 235.0,
        "H-FEA-002": 0.0,
        "H-RISK-001": 0.11,
    }

    print_heading("Hypothesis evaluation")

    for hypothesis_id, observed_value in observations.items():
        status = registry.evaluate_hypothesis(hypothesis_id, observed_value)
        hypothesis = registry.hypotheses[hypothesis_id]
        print(
            f"{hypothesis_id}: {hypothesis.metric}={observed_value} "
            f"=> {status.value}"
        )


def show_exposure_analysis(registry: AssumptionRegistry) -> None:
    print_heading("Assumption exposure by dimension")

    for dimension in Dimension:
        print(f"\n{dimension.value.upper()}")
        for assumption in registry.highest_exposure(dimension)[:3]:
            print(
                f"  {assumption.assumption_id} | "
                f"exposure={assumption.exposure:.3f} | "
                f"evidence={assumption.evidence_confidence:.3f}"
            )
            print(f"    {assumption.statement}")


def show_experiment_priorities(registry: AssumptionRegistry) -> None:
    print_heading("Experiment portfolio")

    ranked = sorted(
        registry.hypotheses,
        key=registry.experiment_priority,
        reverse=True,
    )

    for hypothesis_id in ranked:
        hypothesis = registry.hypotheses[hypothesis_id]
        score = registry.experiment_priority(hypothesis_id)
        print(
            f"{hypothesis_id} | priority={score:.5f} | "
            f"status={hypothesis.status.value}"
        )
        print(f"  {hypothesis.statement}")


def demonstrate_validation_rules() -> None:
    print_heading("Validation and failure handling")

    invalid_cases = [
        (
            "confidence outside allowed range",
            lambda: Assumption(
                assumption_id="BAD-001",
                statement="Invalid confidence example",
                dimension=Dimension.DESIRABILITY,
                confidence=1.5,
                impact=0.5,
                uncertainty=0.5,
                owner="Validation",
                rationale="Demonstrates input validation.",
            ),
        ),
        (
            "empty evidence observation",
            lambda: Evidence(
                source="Test",
                evidence_type=EvidenceType.SURVEY,
                strength=0.5,
                supports=True,
                observation="",
            ),
        ),
        (
            "invalid hypothesis direction",
            lambda: Hypothesis(
                hypothesis_id="BAD-H",
                assumption_id="A-DES-001",
                statement="Invalid direction",
                metric="rate",
                threshold=0.5,
                direction="equal",
                sample_requirement=10,
            ),
        ),
    ]

    for description, operation in invalid_cases:
        try:
            operation()
        except (ValueError, KeyError) as exc:
            print(f"{description}: correctly rejected -> {exc}")


def demonstrate_edge_cases(registry: AssumptionRegistry) -> None:
    print_heading("Edge cases")

    untested = registry.hypotheses["H-DES-001"]
    untested.status = HypothesisStatus.TESTING
    print(
        f"A hypothesis can be explicitly marked testing before measurement: "
        f"{untested.hypothesis_id} -> {untested.status.value}"
    )

    no_evidence = Assumption(
        assumption_id="A-EDGE-001",
        statement="A newly proposed operating assumption has no evidence yet.",
        dimension=Dimension.VIABILITY,
        confidence=0.20,
        impact=0.60,
        uncertainty=1.00,
        owner="Strategy",
        rationale="New assumptions begin with uncertainty rather than fabricated evidence.",
    )
    print(
        f"Untested evidence confidence={no_evidence.evidence_confidence:.2f}; "
        f"exposure={no_evidence.exposure:.2f}"
    )

    try:
        registry.evaluate_hypothesis("H-DES-001", float("nan"))
    except ValueError as exc:
        print(f"Non-finite measurements are rejected: {exc}")


def save_snapshot(registry: AssumptionRegistry) -> Path:
    """
    Demonstrate file handling with a temporary output file.

    A production implementation would normally use controlled storage and
    explicit access permissions for commercially sensitive assumptions.
    """
    output_dir = Path(tempfile.gettempdir())
    output_path = output_dir / "assumption_hypothesis_snapshot.json"
    output_path.write_text(registry.to_json(), encoding="utf-8")
    return output_path


def demonstrate_aggregate_metrics(registry: AssumptionRegistry) -> None:
    print_heading("Portfolio metrics")

    exposures = [item.exposure for item in registry.assumptions.values()]
    evidence_scores = [
        item.evidence_confidence
        for item in registry.assumptions.values()
    ]

    print(f"Mean assumption exposure: {mean(exposures):.3f}")
    print(f"Mean evidence confidence: {mean(evidence_scores):.3f}")

    supported = sum(
        item.status == HypothesisStatus.SUPPORTED
        for item in registry.hypotheses.values()
    )
    refuted = sum(
        item.status == HypothesisStatus.REFUTED
        for item in registry.hypotheses.values()
    )

    total_evaluated = supported + refuted
    if total_evaluated:
        print(
            f"Supported among evaluated hypotheses: "
            f"{supported / total_evaluated:.1%}"
        )

    print(
        "Interpretation: a supported hypothesis reduces uncertainty for the "
        "specific claim tested; it does not prove every related assumption."
    )


def demonstrate_json_round_trip(registry: AssumptionRegistry) -> None:
    print_heading("Structured output")

    serialized = registry.to_json()
    parsed = json.loads(serialized)

    print(
        f"Serialized {len(parsed['assumptions'])} assumptions, "
        f"{len(parsed['hypotheses'])} hypotheses, and "
        f"{len(parsed['experiments'])} experiments."
    )

    print("First assumption record:")
    print(json.dumps(parsed["assumptions"][0], indent=2))


def main() -> None:
    print_heading("Assumptions & Hypotheses Decision System")

    demonstrate_fundamentals()

    registry = build_realistic_registry()
    attach_realistic_evidence(registry)

    evaluate_initial_results(registry)
    show_exposure_analysis(registry)
    show_experiment_priorities(registry)
    demonstrate_validation_rules()
    demonstrate_edge_cases(registry)
    demonstrate_aggregate_metrics(registry)
    demonstrate_json_round_trip(registry)

    snapshot_path = save_snapshot(registry)
    print_heading("Persistence")
    print(f"JSON snapshot written to: {snapshot_path}")

    print_heading("Decision snapshot")
    print(json.dumps(registry.decision_snapshot(), indent=2))


if __name__ == "__main__":
    main()
