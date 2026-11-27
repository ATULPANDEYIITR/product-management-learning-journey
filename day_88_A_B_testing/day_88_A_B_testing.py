#!/usr/bin/env python3
"""
A/B Testing: Randomization, Control Groups, Treatment Groups,
Statistical Significance, and Experiment Evaluation.

Python 3.10+
Standard-library implementation.

The program:
1. Defines experiments and experimental groups.
2. Randomly assigns participants.
3. Prevents duplicate participant assignment.
4. Simulates binary conversion outcomes.
5. Calculates conversion rates and confidence intervals.
6. Performs a two-proportion z-test.
7. Calculates statistical significance and p-values.
8. Evaluates practical significance and guardrail metrics.
9. Produces an experiment report.
"""

from __future__ import annotations

import json
import math
import random
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ExperimentStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"


class Group(Enum):
    CONTROL = "control"
    TREATMENT = "treatment"


class Decision(Enum):
    INCONCLUSIVE = "inconclusive"
    STATISTICALLY_SIGNIFICANT = "statistically_significant"
    TREATMENT_WINS = "treatment_wins"
    CONTROL_WINS = "control_wins"


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    control_probability: float = 0.10
    treatment_probability: float = 0.12
    allocation_ratio: float = 0.50
    significance_level: float = 0.05
    minimum_detectable_effect: float = 0.01
    random_seed: int = 42

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Experiment name cannot be empty.")

        for probability in (
            self.control_probability,
            self.treatment_probability,
            self.allocation_ratio,
            self.significance_level,
        ):
            if not 0 < probability < 1:
                raise ValueError("Probabilities must be between 0 and 1.")

        if self.minimum_detectable_effect < 0:
            raise ValueError("Minimum detectable effect cannot be negative.")


@dataclass
class Participant:
    participant_id: str
    group: Group
    converted: bool
    assigned_at: str


@dataclass
class GroupStatistics:
    group: str
    participants: int
    conversions: int
    conversion_rate: float


@dataclass
class ExperimentReport:
    experiment_name: str
    control: GroupStatistics
    treatment: GroupStatistics
    absolute_lift: float
    relative_lift: Optional[float]
    z_score: float
    p_value: float
    confidence_interval: tuple[float, float]
    statistically_significant: bool
    practical_significance: bool
    decision: str


def normal_cdf(value: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def two_sided_p_value(z_score: float) -> float:
    return 2.0 * (1.0 - normal_cdf(abs(z_score)))


def group_statistics(
    group: Group,
    participants: list[Participant],
) -> GroupStatistics:

    members = [p for p in participants if p.group == group]
    total = len(members)

    if total == 0:
        raise ValueError(f"No participants in {group.value} group.")

    conversions = sum(p.converted for p in members)

    return GroupStatistics(
        group=group.value,
        participants=total,
        conversions=conversions,
        conversion_rate=conversions / total,
    )


def two_proportion_test(
    control_conversions: int,
    control_total: int,
    treatment_conversions: int,
    treatment_total: int,
) -> tuple[float, float]:

    if control_total <= 0 or treatment_total <= 0:
        raise ValueError("Both groups require participants.")

    if not 0 <= control_conversions <= control_total:
        raise ValueError("Invalid control conversion count.")

    if not 0 <= treatment_conversions <= treatment_total:
        raise ValueError("Invalid treatment conversion count.")

    p_control = control_conversions / control_total
    p_treatment = treatment_conversions / treatment_total

    pooled = (
        control_conversions + treatment_conversions
    ) / (control_total + treatment_total)

    standard_error = math.sqrt(
        pooled * (1 - pooled)
        * (1 / control_total + 1 / treatment_total)
    )

    if standard_error == 0:
        return 0.0, 1.0

    z_score = (p_treatment - p_control) / standard_error

    return z_score, two_sided_p_value(z_score)


def confidence_interval(
    control_rate: float,
    treatment_rate: float,
    control_total: int,
    treatment_total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:

    if control_total <= 0 or treatment_total <= 0:
        raise ValueError("Sample sizes must be positive.")

    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between zero and one.")

    # Normal approximation for the difference in independent proportions.
    z_critical = 1.959963984540054

    if confidence != 0.95:
        # Inverse normal approximation using binary search.
        tail = (1 - confidence) / 2
        low, high = 0.0, 8.0

        for _ in range(100):
            mid = (low + high) / 2
            if normal_cdf(mid) < 1 - tail:
                low = mid
            else:
                high = mid

        z_critical = (low + high) / 2

    difference = treatment_rate - control_rate

    se = math.sqrt(
        control_rate * (1 - control_rate) / control_total
        + treatment_rate * (1 - treatment_rate) / treatment_total
    )

    return (
        difference - z_critical * se,
        difference + z_critical * se,
    )


def required_sample_size(
    baseline_rate: float,
    minimum_detectable_effect: float,
    significance_level: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    Approximate equal-sized sample requirement for a two-sided
    comparison of independent proportions.

    Uses a normal approximation and the baseline variance.
    """

    if not 0 < baseline_rate < 1:
        raise ValueError("Baseline rate must be between 0 and 1.")

    if minimum_detectable_effect <= 0:
        raise ValueError("Effect size must be positive.")

    if not 0 < significance_level < 1:
        raise ValueError("Invalid significance level.")

    if not 0 < power < 1:
        raise ValueError("Power must be between zero and one.")

    p2 = baseline_rate + minimum_detectable_effect

    if not 0 < p2 < 1:
        raise ValueError("Expected treatment rate must be between 0 and 1.")

    def inverse_normal(probability: float) -> float:
        low, high = -8.0, 8.0

        for _ in range(120):
            mid = (low + high) / 2
            if normal_cdf(mid) < probability:
                low = mid
            else:
                high = mid

        return (low + high) / 2

    alpha_z = inverse_normal(1 - significance_level / 2)
    power_z = inverse_normal(power)

    average = (baseline_rate + p2) / 2

    numerator = (
        alpha_z * math.sqrt(2 * average * (1 - average))
        + power_z * math.sqrt(
            baseline_rate * (1 - baseline_rate)
            + p2 * (1 - p2)
        )
    ) ** 2

    return math.ceil(
        numerator / (minimum_detectable_effect ** 2)
    )


@dataclass
class Experiment:
    config: ExperimentConfig
    status: ExperimentStatus = ExperimentStatus.DRAFT
    participants: list[Participant] = field(default_factory=list)
    participant_ids: set[str] = field(default_factory=set)
    rng: random.Random = field(init=False, repr=False)

    def __post_init__(self):
        self.rng = random.Random(self.config.random_seed)

    def start(self):
        if self.status != ExperimentStatus.DRAFT:
            raise RuntimeError("Only draft experiments can be started.")

        self.status = ExperimentStatus.RUNNING

    def assign(
        self,
        participant_id: str,
        outcome_probability: Optional[dict[Group, float]] = None,
    ) -> Participant:

        if self.status != ExperimentStatus.RUNNING:
            raise RuntimeError("Experiment is not running.")

        participant_id = participant_id.strip()

        if not participant_id:
            raise ValueError("Participant ID cannot be empty.")

        if participant_id in self.participant_ids:
            raise ValueError("Participant already assigned.")

        # Independent random assignment with a configured allocation ratio.
        group = (
            Group.CONTROL
            if self.rng.random() < self.config.allocation_ratio
            else Group.TREATMENT
        )

        probabilities = outcome_probability or {
            Group.CONTROL: self.config.control_probability,
            Group.TREATMENT: self.config.treatment_probability,
        }

        probability = probabilities[group]

        if not 0 <= probability <= 1:
            raise ValueError("Outcome probability must be between 0 and 1.")

        converted = self.rng.random() < probability

        participant = Participant(
            participant_id=participant_id,
            group=group,
            converted=converted,
            assigned_at=datetime.now(timezone.utc).isoformat(),
        )

        self.participants.append(participant)
        self.participant_ids.add(participant_id)

        return participant

    def stop(self):
        if self.status != ExperimentStatus.RUNNING:
            raise RuntimeError("Only running experiments can be stopped.")

        self.status = ExperimentStatus.STOPPED

    def complete(self):
        if self.status != ExperimentStatus.RUNNING:
            raise RuntimeError("Only running experiments can be completed.")

        self.status = ExperimentStatus.COMPLETED

    def evaluate(self) -> ExperimentReport:
        if self.status not in (
            ExperimentStatus.RUNNING,
            ExperimentStatus.COMPLETED,
            ExperimentStatus.STOPPED,
        ):
            raise RuntimeError("Experiment has not started.")

        control = group_statistics(
            Group.CONTROL, self.participants
        )

        treatment = group_statistics(
            Group.TREATMENT, self.participants
        )

        z_score, p_value = two_proportion_test(
            control.conversions,
            control.participants,
            treatment.conversions,
            treatment.participants,
        )

        lift = (
            treatment.conversion_rate - control.conversion_rate
        )

        relative_lift = (
            lift / control.conversion_rate
            if control.conversion_rate > 0
            else None
        )

        ci = confidence_interval(
            control.conversion_rate,
            treatment.conversion_rate,
            control.participants,
            treatment.participants,
        )

        significant = p_value < self.config.significance_level

        practical = (
            lift >= self.config.minimum_detectable_effect
        )

        if not significant:
            decision = Decision.INCONCLUSIVE
        elif lift > 0 and practical:
            decision = Decision.TREATMENT_WINS
        elif lift < 0:
            decision = Decision.CONTROL_WINS
        else:
            decision = Decision.STATISTICALLY_SIGNIFICANT

        return ExperimentReport(
            experiment_name=self.config.name,
            control=control,
            treatment=treatment,
            absolute_lift=lift,
            relative_lift=relative_lift,
            z_score=z_score,
            p_value=p_value,
            confidence_interval=ci,
            statistically_significant=significant,
            practical_significance=practical,
            decision=decision.value,
        )

    def export_json(self, report: ExperimentReport, filename: str):
        """Write a report without exposing individual participant records."""
        payload = asdict(report)

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)


def run_demo():
    config = ExperimentConfig(
        name="Checkout Button Experiment",
        control_probability=0.10,
        treatment_probability=0.12,
        allocation_ratio=0.50,
        significance_level=0.05,
        minimum_detectable_effect=0.01,
        random_seed=42,
    )

    experiment = Experiment(config)
    experiment.start()

    for index in range(20_000):
        experiment.assign(f"user-{index + 1}")

    experiment.complete()

    report = experiment.evaluate()

    print("\nA/B TESTING EXPERIMENT REPORT")
    print("=" * 55)
    print(f"Experiment: {report.experiment_name}")

    for stats in (report.control, report.treatment):
        print(f"\n{stats.group.upper()} GROUP")
        print(f"Participants: {stats.participants}")
        print(f"Conversions: {stats.conversions}")
        print(f"Conversion rate: {stats.conversion_rate:.4%}")

    print("\nSTATISTICAL EVALUATION")
    print(f"Absolute lift: {report.absolute_lift:.4%}")

    if report.relative_lift is not None:
        print(f"Relative lift: {report.relative_lift:.2%}")
    else:
        print("Relative lift: undefined (zero control conversion rate)")

    print(f"Z-score: {report.z_score:.4f}")
    print(f"P-value: {report.p_value:.8f}")
    print(
        "95% confidence interval: "
        f"[{report.confidence_interval[0]:.4%}, "
        f"{report.confidence_interval[1]:.4%}]"
    )

    print(f"Statistically significant: {report.statistically_significant}")
    print(f"Practically significant: {report.practical_significance}")
    print(f"Decision: {report.decision}")

    print("\nSAMPLE SIZE PLANNING")
    sample = required_sample_size(
        baseline_rate=0.10,
        minimum_detectable_effect=0.02,
    )
    print(f"Approximate participants per group: {sample}")

    experiment.export_json(report, "ab_test_report.json")
    print("\nReport saved to ab_test_report.json")


def run_tests():
    assert abs(normal_cdf(0) - 0.5) < 1e-10
    assert abs(two_sided_p_value(0) - 1.0) < 1e-10

    z, p = two_proportion_test(100, 1000, 100, 1000)
    assert z == 0
    assert p == 1

    size = required_sample_size(0.10, 0.02)
    assert size > 0

    config = ExperimentConfig("Validation Test")
    experiment = Experiment(config)
    experiment.start()

    participant = experiment.assign("user-1")
    assert participant.group in (Group.CONTROL, Group.TREATMENT)

    try:
        experiment.assign("user-1")
        raise AssertionError("Duplicate assignment was not rejected.")
    except ValueError:
        pass

    print("All validation tests passed.")


if __name__ == "__main__":
    run_tests()
    run_demo()
