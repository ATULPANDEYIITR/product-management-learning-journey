#!/usr/bin/env python3
"""
Experiment Metrics: Statistical Evaluation and Experiment Decision Engine

Implements:
- Primary and secondary metrics
- Guardrail metrics
- Sample-size estimation
- Deterministic A/B assignment
- Conversion-rate analysis
- Revenue and latency analysis
- Statistical significance
- Experiment validity checks
- Automated decision reporting

Python 3.10+
Uses only the Python standard library.
"""

from __future__ import annotations

import hashlib
import math
import random
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class MetricType(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    GUARDRAIL = "guardrail"


class ExperimentStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    INVALID = "invalid"


class Decision(Enum):
    SHIP = "ship"
    DO_NOT_SHIP = "do_not_ship"
    INCONCLUSIVE = "inconclusive"
    INVALID = "invalid"


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    metric_type: MetricType
    description: str
    unit: str
    minimum: float | None = None
    maximum: float | None = None
    higher_is_better: bool = True

    def validate(self, value: float) -> None:
        if not math.isfinite(value):
            raise ValueError(f"{self.name}: value must be finite")

        if self.minimum is not None and value < self.minimum:
            raise ValueError(f"{self.name}: value below minimum")

        if self.maximum is not None and value > self.maximum:
            raise ValueError(f"{self.name}: value above maximum")


@dataclass
class ExperimentConfig:
    name: str
    baseline_conversion: float
    minimum_detectable_effect: float
    alpha: float = 0.05
    power: float = 0.80
    traffic_allocation: float = 1.0
    minimum_sample_size: int = 100
    maximum_sample_size: int = 1_000_000

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Experiment name cannot be empty")

        if not 0 < self.baseline_conversion < 1:
            raise ValueError("Baseline conversion must be between 0 and 1")

        if not 0 < self.minimum_detectable_effect < 1:
            raise ValueError("MDE must be a positive relative effect below 1")

        if not 0 < self.alpha < 1:
            raise ValueError("Alpha must be between 0 and 1")

        if not 0 < self.power < 1:
            raise ValueError("Power must be between 0 and 1")

        if not 0 < self.traffic_allocation <= 1:
            raise ValueError("Traffic allocation must be between 0 and 1")

        if self.minimum_sample_size < 2:
            raise ValueError("Minimum sample size must be at least 2")

        if self.maximum_sample_size < self.minimum_sample_size:
            raise ValueError("Maximum sample size is too small")


@dataclass
class ExperimentResult:
    experiment_name: str
    control_users: int
    treatment_users: int
    control_conversions: int
    treatment_conversions: int
    control_revenue: list[float]
    treatment_revenue: list[float]
    control_latency: list[float]
    treatment_latency: list[float]
    control_refunds: int
    treatment_refunds: int


@dataclass
class MetricAnalysis:
    name: str
    control_value: float
    treatment_value: float
    absolute_change: float
    relative_change: float
    p_value: float | None = None
    significant: bool | None = None


@dataclass
class EvaluationReport:
    decision: Decision
    primary_metric: MetricAnalysis
    secondary_metrics: list[MetricAnalysis]
    guardrails: dict[str, bool]
    sample_size_sufficient: bool
    observations: list[str] = field(default_factory=list)


class SampleSizeCalculator:
    """Calculate equal-sized groups for a two-sided proportion test."""

    @staticmethod
    def normal_quantile(p: float) -> float:
        """Acklam inverse-normal approximation."""

        if not 0 < p < 1:
            raise ValueError("Probability must be between 0 and 1")

        a = [
            -39.6968302866538, 220.946098424521,
            -275.928510446969, 138.357751867269,
            -30.6647980661472, 2.50662827745924
        ]
        b = [
            -54.4760987982241, 161.585836858041,
            -155.698979859887, 66.8013118877197,
            -13.2806815528857
        ]
        c = [
            -0.00778489400243029, -0.322396458041136,
            -2.40075827716184, -2.54973253934373,
            4.37466414146497, 2.93816398269878
        ]
        d = [
            0.00778469570904146, 0.32246712907004,
            2.445134137143, 3.75440866190742
        ]

        low = 0.02425
        high = 1 - low

        if p < low:
            q = math.sqrt(-2 * math.log(p))
            return (((((c[0] * q + c[1]) * q + c[2]) * q +
                      c[3]) * q + c[4]) * q + c[5]) / (
                ((((d[0] * q + d[1]) * q + d[2]) * q +
                  d[3]) * q) + 1
            )

        if p > high:
            return -SampleSizeCalculator.normal_quantile(1 - p)

        q = p - 0.5
        r = q * q

        return (((((a[0] * r + a[1]) * r + a[2]) * r +
                  a[3]) * r + a[4]) * r + a[5]) * q / (
            (((((b[0] * r + b[1]) * r + b[2]) * r +
               b[3]) * r + b[4]) * r) + 1
        )

    @classmethod
    def calculate(cls, config: ExperimentConfig) -> int:
        config.validate()

        p1 = config.baseline_conversion
        p2 = p1 * (1 + config.minimum_detectable_effect)

        if p2 >= 1:
            raise ValueError("MDE produces an invalid treatment conversion rate")

        pooled = (p1 + p2) / 2
        difference = abs(p2 - p1)

        z_alpha = cls.normal_quantile(1 - config.alpha / 2)
        z_power = cls.normal_quantile(config.power)

        numerator = (
            z_alpha * math.sqrt(2 * pooled * (1 - pooled))
            + z_power * math.sqrt(
                p1 * (1 - p1) + p2 * (1 - p2)
            )
        ) ** 2

        required = math.ceil(numerator / difference**2)

        return min(
            max(required, config.minimum_sample_size),
            config.maximum_sample_size
        )


class ExperimentAnalyzer:
    """Analyze binary, continuous and operational metrics."""

    @staticmethod
    def conversion_rate(successes: int, users: int) -> float:
        if users <= 0:
            raise ValueError("User count must be positive")

        if not 0 <= successes <= users:
            raise ValueError("Invalid conversion count")

        return successes / users

    @staticmethod
    def two_proportion_test(
        x1: int,
        n1: int,
        x2: int,
        n2: int
    ) -> float:
        """Two-sided pooled two-proportion z-test."""

        if min(n1, n2) <= 0:
            raise ValueError("Sample sizes must be positive")

        if not (0 <= x1 <= n1 and 0 <= x2 <= n2):
            raise ValueError("Invalid success counts")

        p1 = x1 / n1
        p2 = x2 / n2
        pooled = (x1 + x2) / (n1 + n2)

        se = math.sqrt(
            pooled * (1 - pooled) * (1 / n1 + 1 / n2)
        )

        if se == 0:
            return 1.0 if p1 == p2 else 0.0

        z = (p2 - p1) / se

        # Two-sided normal approximation.
        return math.erfc(abs(z) / math.sqrt(2))

    @staticmethod
    def welch_test(
        control: list[float],
        treatment: list[float]
    ) -> float | None:
        """Welch's t-test with a normal approximation to its tail."""

        if len(control) < 2 or len(treatment) < 2:
            return None

        mean1 = statistics.mean(control)
        mean2 = statistics.mean(treatment)

        var1 = statistics.variance(control)
        var2 = statistics.variance(treatment)

        se_squared = var1 / len(control) + var2 / len(treatment)

        if se_squared == 0:
            return 1.0 if mean1 == mean2 else 0.0

        z = (mean2 - mean1) / math.sqrt(se_squared)

        return math.erfc(abs(z) / math.sqrt(2))

    @staticmethod
    def metric(
        name: str,
        control: float,
        treatment: float,
        p_value: float | None = None,
        alpha: float = 0.05
    ) -> MetricAnalysis:
        absolute = treatment - control

        relative = (
            absolute / abs(control) * 100
            if control != 0 else 0.0
        )

        return MetricAnalysis(
            name=name,
            control_value=control,
            treatment_value=treatment,
            absolute_change=absolute,
            relative_change=relative,
            p_value=p_value,
            significant=(
                p_value < alpha if p_value is not None else None
            )
        )


class ExperimentSimulator:
    """Generate reproducible user-level A/B experiment data."""

    @staticmethod
    def assign_variant(
        user_id: str,
        experiment_name: str
    ) -> str:
        # Stable hashing avoids assignment changes between executions.
        digest = hashlib.sha256(
            f"{experiment_name}:{user_id}".encode()
        ).hexdigest()

        return "treatment" if int(digest[:8], 16) % 2 else "control"

    @classmethod
    def simulate(
        cls,
        config: ExperimentConfig,
        sample_size: int,
        seed: int = 42
    ) -> ExperimentResult:
        config.validate()

        if sample_size < 2:
            raise ValueError("Sample size must be at least two")

        rng = random.Random(seed)

        data = {
            "control": {
                "users": 0, "conversions": 0,
                "revenue": [], "latency": [], "refunds": 0
            },
            "treatment": {
                "users": 0, "conversions": 0,
                "revenue": [], "latency": [], "refunds": 0
            }
        }

        for index in range(sample_size):
            user_id = f"user-{index:08d}"
            variant = cls.assign_variant(user_id, config.name)
            bucket = data[variant]

            bucket["users"] += 1

            conversion_probability = (
                config.baseline_conversion
                if variant == "control"
                else config.baseline_conversion *
                (1 + config.minimum_detectable_effect)
            )

            converted = rng.random() < conversion_probability

            if converted:
                bucket["conversions"] += 1
                bucket["revenue"].append(
                    round(rng.lognormvariate(3.5, 0.6), 2)
                )

                if rng.random() < (
                    0.035 if variant == "control" else 0.04
                ):
                    bucket["refunds"] += 1

            latency = rng.gauss(
                180 if variant == "control" else 190,
                25
            )

            bucket["latency"].append(max(1, latency))

        c = data["control"]
        t = data["treatment"]

        return ExperimentResult(
            experiment_name=config.name,
            control_users=c["users"],
            treatment_users=t["users"],
            control_conversions=c["conversions"],
            treatment_conversions=t["conversions"],
            control_revenue=c["revenue"],
            treatment_revenue=t["revenue"],
            control_latency=c["latency"],
            treatment_latency=t["latency"],
            control_refunds=c["refunds"],
            treatment_refunds=t["refunds"]
        )


class ExperimentEvaluator:
    """Apply sample-size, primary-metric and guardrail policies."""

    def __init__(
        self,
        alpha: float = 0.05,
        minimum_conversion_improvement: float = 0.0,
        maximum_refund_increase: float = 0.02,
        maximum_p95_latency_increase: float = 40.0
    ):
        self.alpha = alpha
        self.minimum_conversion_improvement = (
            minimum_conversion_improvement
        )
        self.maximum_refund_increase = maximum_refund_increase
        self.maximum_p95_latency_increase = (
            maximum_p95_latency_increase
        )

    def evaluate(
        self,
        result: ExperimentResult,
        required_per_group: int
    ) -> EvaluationReport:

        if min(
            result.control_users,
            result.treatment_users
        ) == 0:
            raise ValueError("Both experiment groups must contain users")

        analyzer = ExperimentAnalyzer()

        control_rate = analyzer.conversion_rate(
            result.control_conversions,
            result.control_users
        )

        treatment_rate = analyzer.conversion_rate(
            result.treatment_conversions,
            result.treatment_users
        )

        p_value = analyzer.two_proportion_test(
            result.control_conversions,
            result.control_users,
            result.treatment_conversions,
            result.treatment_users
        )

        primary = analyzer.metric(
            "conversion_rate",
            control_rate,
            treatment_rate,
            p_value,
            self.alpha
        )

        control_revenue = (
            statistics.mean(result.control_revenue)
            if result.control_revenue else 0.0
        )

        treatment_revenue = (
            statistics.mean(result.treatment_revenue)
            if result.treatment_revenue else 0.0
        )

        revenue_p = analyzer.welch_test(
            result.control_revenue,
            result.treatment_revenue
        )

        secondary = [
            analyzer.metric(
                "revenue_per_conversion",
                control_revenue,
                treatment_revenue,
                revenue_p,
                self.alpha
            )
        ]

        control_refund_rate = (
            result.control_refunds /
            result.control_conversions
            if result.control_conversions else 0.0
        )

        treatment_refund_rate = (
            result.treatment_refunds /
            result.treatment_conversions
            if result.treatment_conversions else 0.0
        )

        control_p95 = statistics.quantiles(
            result.control_latency, n=100
        )[94]

        treatment_p95 = statistics.quantiles(
            result.treatment_latency, n=100
        )[94]

        guardrails = {
            "refund_rate": (
                treatment_refund_rate - control_refund_rate
                <= self.maximum_refund_increase
            ),
            "p95_latency": (
                treatment_p95 - control_p95
                <= self.maximum_p95_latency_increase
            )
        }

        sample_sufficient = (
            result.control_users >= required_per_group
            and result.treatment_users >= required_per_group
        )

        observations = []

        if not sample_sufficient:
            observations.append("Required sample size not reached")

        if not primary.significant:
            observations.append(
                "Primary metric is not statistically significant"
            )

        if primary.absolute_change <= self.minimum_conversion_improvement:
            observations.append(
                "Primary metric does not meet the minimum improvement"
            )

        for name, passed in guardrails.items():
            if not passed:
                observations.append(
                    f"Guardrail violation: {name}"
                )

        if not sample_sufficient:
            decision = Decision.INCONCLUSIVE
        elif not all(guardrails.values()):
            decision = Decision.DO_NOT_SHIP
        elif (
            primary.significant
            and primary.absolute_change >
            self.minimum_conversion_improvement
        ):
            decision = Decision.SHIP
        else:
            decision = Decision.INCONCLUSIVE

        return EvaluationReport(
            decision=decision,
            primary_metric=primary,
            secondary_metrics=secondary,
            guardrails=guardrails,
            sample_size_sufficient=sample_sufficient,
            observations=observations
        )


def print_report(
    report: EvaluationReport,
    required_per_group: int
) -> None:
    print("\nEXPERIMENT EVALUATION")
    print("=" * 55)

    print(f"Decision: {report.decision.value.upper()}")
    print(f"Sample sufficient: {report.sample_size_sufficient}")
    print(f"Required users per group: {required_per_group}")

    primary = report.primary_metric

    print("\nPRIMARY METRIC")
    print(f"Metric: {primary.name}")
    print(f"Control: {primary.control_value:.4%}")
    print(f"Treatment: {primary.treatment_value:.4%}")
    print(f"Absolute change: {primary.absolute_change:.4%}")
    print(f"Relative change: {primary.relative_change:.2f}%")
    print(f"P-value: {primary.p_value:.6f}")
    print(f"Significant: {primary.significant}")

    print("\nSECONDARY METRICS")

    for metric in report.secondary_metrics:
        print(
            f"{metric.name}: "
            f"{metric.control_value:.2f} -> "
            f"{metric.treatment_value:.2f}"
        )

    print("\nGUARDRAILS")

    for name, passed in report.guardrails.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")

    print("\nOBSERVATIONS")

    for observation in report.observations:
        print(f"- {observation}")


def run_tests() -> None:
    config = ExperimentConfig(
        name="checkout-redesign",
        baseline_conversion=0.10,
        minimum_detectable_effect=0.10
    )

    config.validate()

    assert 0 < SampleSizeCalculator.calculate(config)
    assert ExperimentSimulator.assign_variant(
        "user-1", "experiment"
    ) == ExperimentSimulator.assign_variant(
        "user-1", "experiment"
    )

    assert ExperimentAnalyzer.conversion_rate(10, 100) == 0.1

    assert ExperimentAnalyzer.two_proportion_test(
        50, 500, 100, 500
    ) < 0.05

    try:
        ExperimentAnalyzer.conversion_rate(10, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Zero sample size was not rejected")

    print("All validation tests passed.")


def main() -> None:
    run_tests()

    config = ExperimentConfig(
        name="checkout-redesign",
        baseline_conversion=0.10,
        minimum_detectable_effect=0.10,
        alpha=0.05,
        power=0.80,
        traffic_allocation=1.0,
        minimum_sample_size=100,
        maximum_sample_size=100_000
    )

    required = SampleSizeCalculator.calculate(config)

    print("\nEXPERIMENT CONFIGURATION")
    print(f"Experiment: {config.name}")
    print(f"Baseline conversion: {config.baseline_conversion:.2%}")
    print(f"Relative MDE: {config.minimum_detectable_effect:.2%}")
    print(f"Significance level: {config.alpha}")
    print(f"Statistical power: {config.power:.2%}")
    print(f"Required sample per group: {required}")

    # Simulate twice the required per-group sample size.
    result = ExperimentSimulator.simulate(
        config,
        sample_size=required * 2,
        seed=42
    )

    evaluator = ExperimentEvaluator(
        alpha=config.alpha,
        minimum_conversion_improvement=0.0,
        maximum_refund_increase=0.02,
        maximum_p95_latency_increase=40.0
    )

    report = evaluator.evaluate(result, required)

    print_report(report, required)


if __name__ == "__main__":
    main()
