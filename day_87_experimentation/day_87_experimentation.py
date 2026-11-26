#!/usr/bin/env python3
"""
EXPERIMENTATION: EXPERIMENT DESIGN, HYPOTHESES, CONTROL AND TREATMENT

A self-contained experimentation framework implementing:
- Research questions and testable hypotheses
- Independent and dependent variables
- Control and treatment groups
- Randomized participant assignment
- Reproducible experiment execution
- Sample-size estimation
- Conversion-rate measurement
- Statistical hypothesis testing
- Guardrail metrics
- Experiment validity checks
- Decision-making and reporting

Python standard library only.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------
# 1. DOMAIN TYPES
# ---------------------------------------------------------

class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GroupType(str, Enum):
    CONTROL = "control"
    TREATMENT = "treatment"


class Decision(str, Enum):
    ACCEPT_ALTERNATIVE = "reject_null_hypothesis"
    FAIL_TO_REJECT = "fail_to_reject_null_hypothesis"
    INVALID = "invalid_experiment"


@dataclass(frozen=True)
class Hypothesis:
    research_question: str
    null_hypothesis: str
    alternative_hypothesis: str
    metric: str
    expected_direction: str = "increase"

    def validate(self) -> None:
        if not all([
            self.research_question.strip(),
            self.null_hypothesis.strip(),
            self.alternative_hypothesis.strip(),
            self.metric.strip()
        ]):
            raise ValueError("Hypothesis fields cannot be empty.")

        if self.expected_direction not in {
            "increase", "decrease", "different"
        }:
            raise ValueError("Unsupported hypothesis direction.")


@dataclass(frozen=True)
class ExperimentDesign:
    name: str
    hypothesis: Hypothesis
    significance_level: float = 0.05
    statistical_power: float = 0.80
    minimum_detectable_effect: float = 0.05
    baseline_rate: float = 0.10
    random_seed: int = 42
    minimum_group_size: int = 30

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Experiment name is required.")

        self.hypothesis.validate()

        if not 0 < self.significance_level < 1:
            raise ValueError("Significance level must be between 0 and 1.")

        if not 0 < self.statistical_power < 1:
            raise ValueError("Statistical power must be between 0 and 1.")

        if not 0 < self.minimum_detectable_effect < 1:
            raise ValueError("Invalid minimum detectable effect.")

        if not 0 < self.baseline_rate < 1:
            raise ValueError("Baseline rate must be between 0 and 1.")

        if self.minimum_group_size < 2:
            raise ValueError("Minimum group size must be at least 2.")


@dataclass
class Participant:
    participant_id: str
    group: GroupType
    converted: bool
    exposure_time: str


@dataclass
class ExperimentResult:
    experiment_id: str
    control_size: int
    treatment_size: int
    control_conversions: int
    treatment_conversions: int
    control_rate: float
    treatment_rate: float
    absolute_effect: float
    relative_effect: Optional[float]
    z_score: float
    p_value: float
    confidence_interval: tuple[float, float]
    decision: Decision
    guardrail_passed: bool
    interpretation: str


# ---------------------------------------------------------
# 2. EXPERIMENT DESIGN
# ---------------------------------------------------------

class Experiment:
    def __init__(self, design: ExperimentDesign):
        design.validate()

        self.design = design
        self.experiment_id = str(uuid.uuid4())
        self.status = ExperimentStatus.DRAFT
        self.participants: list[Participant] = []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def estimate_sample_size(self) -> int:
        """
        Approximate per-group sample size for a two-sided
        comparison of independent proportions.

        Uses the normal approximation.
        """

        from statistics import NormalDist

        p1 = self.design.baseline_rate
        p2 = min(
            1.0,
            p1 + self.design.minimum_detectable_effect
        )

        pooled = (p1 + p2) / 2

        z_alpha = NormalDist().inv_cdf(
            1 - self.design.significance_level / 2
        )

        z_beta = NormalDist().inv_cdf(
            self.design.statistical_power
        )

        numerator = (
            z_alpha * math.sqrt(2 * pooled * (1 - pooled))
            + z_beta * math.sqrt(
                p1 * (1 - p1) + p2 * (1 - p2)
            )
        ) ** 2

        denominator = (p2 - p1) ** 2

        return max(
            self.design.minimum_group_size,
            math.ceil(numerator / denominator)
        )

    def start(self) -> None:
        if self.status != ExperimentStatus.DRAFT:
            raise RuntimeError("Only draft experiments can start.")

        self.status = ExperimentStatus.RUNNING

    # -----------------------------------------------------
    # 3. RANDOMIZED ASSIGNMENT AND EXECUTION
    # -----------------------------------------------------

    def run_simulation(
        self,
        participants: int,
        treatment_rate: float,
        control_rate: Optional[float] = None
    ) -> None:

        if self.status != ExperimentStatus.RUNNING:
            raise RuntimeError("Experiment is not running.")

        if participants < 2:
            raise ValueError("At least two participants are required.")

        if not 0 <= treatment_rate <= 1:
            raise ValueError("Invalid treatment conversion rate.")

        if control_rate is None:
            control_rate = self.design.baseline_rate

        if not 0 <= control_rate <= 1:
            raise ValueError("Invalid control conversion rate.")

        if self.participants:
            raise RuntimeError("Experiment execution already exists.")

        rng = random.Random(self.design.random_seed)

        # Random assignment prevents systematic group selection.
        group_assignments = [
            GroupType.CONTROL,
            GroupType.TREATMENT
        ] * (participants // 2)

        if participants % 2:
            group_assignments.append(
                rng.choice(list(GroupType))
            )

        rng.shuffle(group_assignments)

        for index, group in enumerate(group_assignments):
            probability = (
                control_rate
                if group == GroupType.CONTROL
                else treatment_rate
            )

            converted = rng.random() < probability

            self.participants.append(
                Participant(
                    participant_id=f"P-{index + 1:06d}",
                    group=group,
                    converted=converted,
                    exposure_time=datetime.now(
                        timezone.utc
                    ).isoformat()
                )
            )

    # -----------------------------------------------------
    # 4. METRIC CALCULATION
    # -----------------------------------------------------

    def group_metrics(self, group: GroupType) -> tuple[int, int, float]:
        members = [
            p for p in self.participants if p.group == group
        ]

        total = len(members)
        conversions = sum(p.converted for p in members)

        rate = conversions / total if total else 0.0

        return total, conversions, rate

    # -----------------------------------------------------
    # 5. STATISTICAL EVALUATION
    # -----------------------------------------------------

    @staticmethod
    def normal_cdf(value: float) -> float:
        return (
            1 + math.erf(value / math.sqrt(2))
        ) / 2

    def analyze(
        self,
        guardrail_passed: bool = True
    ) -> ExperimentResult:

        if self.status != ExperimentStatus.RUNNING:
            raise RuntimeError("Only running experiments can be analyzed.")

        control_n, control_x, control_rate = self.group_metrics(
            GroupType.CONTROL
        )

        treatment_n, treatment_x, treatment_rate = self.group_metrics(
            GroupType.TREATMENT
        )

        minimum = self.design.minimum_group_size

        if min(control_n, treatment_n) < minimum:
            raise ValueError(
                f"Insufficient participants. Each group requires {minimum}."
            )

        if control_rate == 0 and treatment_rate == 0:
            raise ValueError("Both groups have zero observed conversions.")

        pooled = (
            (control_x + treatment_x)
            / (control_n + treatment_n)
        )

        standard_error = math.sqrt(
            pooled * (1 - pooled)
            * (1 / control_n + 1 / treatment_n)
        )

        if standard_error == 0:
            raise ValueError("Statistical variance is zero.")

        effect = treatment_rate - control_rate
        z_score = effect / standard_error

        # Two-sided normal approximation.
        p_value = 2 * (
            1 - self.normal_cdf(abs(z_score))
        )

        # Unpooled Wald confidence interval for the difference.
        unpooled_se = math.sqrt(
            control_rate * (1 - control_rate) / control_n
            + treatment_rate * (1 - treatment_rate) / treatment_n
        )

        critical_value = 1.959963984540054

        lower = effect - critical_value * unpooled_se
        upper = effect + critical_value * unpooled_se

        relative_effect = (
            effect / control_rate
            if control_rate > 0
            else None
        )

        alpha = self.design.significance_level

        if not guardrail_passed:
            decision = Decision.INVALID
            interpretation = (
                "Guardrail failure prevents a positive rollout decision."
            )

        elif p_value < alpha:
            if self.design.hypothesis.expected_direction == "increase":
                favorable = effect > 0
            elif self.design.hypothesis.expected_direction == "decrease":
                favorable = effect < 0
            else:
                favorable = True

            if favorable:
                decision = Decision.ACCEPT_ALTERNATIVE
                interpretation = (
                    "Statistically significant evidence supports "
                    "the alternative hypothesis."
                )
            else:
                decision = Decision.FAIL_TO_REJECT
                interpretation = (
                    "A statistically significant effect was observed "
                    "in the direction opposite to the expected direction."
                )
        else:
            decision = Decision.FAIL_TO_REJECT
            interpretation = (
                "Insufficient evidence to reject the null hypothesis."
            )

        self.status = ExperimentStatus.COMPLETED

        return ExperimentResult(
            experiment_id=self.experiment_id,
            control_size=control_n,
            treatment_size=treatment_n,
            control_conversions=control_x,
            treatment_conversions=treatment_x,
            control_rate=control_rate,
            treatment_rate=treatment_rate,
            absolute_effect=effect,
            relative_effect=relative_effect,
            z_score=z_score,
            p_value=p_value,
            confidence_interval=(lower, upper),
            decision=decision,
            guardrail_passed=guardrail_passed,
            interpretation=interpretation
        )

    # -----------------------------------------------------
    # 6. DATA EXPORT
    # -----------------------------------------------------

    def export_participants(self, filename: str) -> None:
        path = Path(filename)

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "participant_id",
                    "group",
                    "converted",
                    "exposure_time"
                ]
            )

            writer.writeheader()

            for participant in self.participants:
                writer.writerow({
                    "participant_id": participant.participant_id,
                    "group": participant.group.value,
                    "converted": participant.converted,
                    "exposure_time": participant.exposure_time
                })

    @staticmethod
    def export_report(result: ExperimentResult, filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(asdict(result), file, indent=4)


# ---------------------------------------------------------
# 7. EXPERIMENT VALIDATION
# ---------------------------------------------------------

def validate_randomization(experiment: Experiment) -> bool:
    control = sum(
        p.group == GroupType.CONTROL
        for p in experiment.participants
    )

    treatment = sum(
        p.group == GroupType.TREATMENT
        for p in experiment.participants
    )

    return abs(control - treatment) <= 1


def validate_unique_participants(experiment: Experiment) -> bool:
    identifiers = [
        participant.participant_id
        for participant in experiment.participants
    ]

    return len(identifiers) == len(set(identifiers))


# ---------------------------------------------------------
# 8. EXECUTABLE EXAMPLE
# ---------------------------------------------------------

def main() -> None:

    hypothesis = Hypothesis(
        research_question=(
            "Does a redesigned checkout page improve purchases?"
        ),
        null_hypothesis=(
            "The redesigned checkout page does not change conversion."
        ),
        alternative_hypothesis=(
            "The redesigned checkout page increases conversion."
        ),
        metric="purchase_conversion",
        expected_direction="increase"
    )

    design = ExperimentDesign(
        name="Checkout Optimization Experiment",
        hypothesis=hypothesis,
        significance_level=0.05,
        statistical_power=0.80,
        minimum_detectable_effect=0.05,
        baseline_rate=0.10,
        random_seed=42,
        minimum_group_size=30
    )

    experiment = Experiment(design)

    print("\nEXPERIMENT DESIGN")
    print("-----------------")
    print("Name:", design.name)
    print("Research question:", hypothesis.research_question)
    print("Null hypothesis:", hypothesis.null_hypothesis)
    print("Alternative hypothesis:", hypothesis.alternative_hypothesis)

    required_sample = experiment.estimate_sample_size()

    print("Estimated sample size per group:", required_sample)

    experiment.start()

    experiment.run_simulation(
        participants=2000,
        control_rate=0.10,
        treatment_rate=0.125
    )

    assert validate_randomization(experiment)
    assert validate_unique_participants(experiment)

    result = experiment.analyze(
        guardrail_passed=True
    )

    print("\nEXPERIMENT RESULTS")
    print("------------------")
    print("Control participants:", result.control_size)
    print("Treatment participants:", result.treatment_size)
    print("Control conversion:", round(result.control_rate, 4))
    print("Treatment conversion:", round(result.treatment_rate, 4))
    print("Absolute effect:", round(result.absolute_effect, 4))
    print("Relative effect:", result.relative_effect)
    print("Z-score:", round(result.z_score, 4))
    print("P-value:", round(result.p_value, 6))
    print("95% confidence interval:", result.confidence_interval)
    print("Decision:", result.decision.value)
    print("Interpretation:", result.interpretation)

    experiment.export_participants("experiment_participants.csv")
    experiment.export_report(result, "experiment_report.json")

    print("\nFiles exported successfully.")

    # Demonstrate input validation.
    try:
        invalid_design = ExperimentDesign(
            name="Invalid Experiment",
            hypothesis=hypothesis,
            significance_level=1.5
        )
        invalid_design.validate()
    except ValueError as error:
        print("Validation test:", error)


if __name__ == "__main__":
    main()
