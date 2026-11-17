#!/usr/bin/env python3
"""
PRODUCT METRICS ENGINE
North Star Metric, Input Metrics, Output Metrics, and Guardrail Metrics.

A self-contained product analytics simulation featuring:
- Product metric classification
- North Star Metric calculation
- Input and output metric evaluation
- Guardrail monitoring
- Cohort and period comparisons
- Metric validation
- Growth diagnosis
- Alert generation
- Product experiment evaluation
- JSON reporting
- Unit-style assertions

Run:
    python product_metrics.py

Optional:
    python product_metrics.py --json report.json
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("product_metrics")


class MetricCategory(Enum):
    NORTH_STAR = "north_star"
    INPUT = "input"
    OUTPUT = "output"
    GUARDRAIL = "guardrail"


class Direction(Enum):
    HIGHER = "higher"
    LOWER = "lower"
    RANGE = "range"


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricError(Exception):
    """Base exception for metric processing."""


class MetricValidationError(MetricError):
    """Raised when metric data violates validation rules."""


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    category: MetricCategory
    unit: str
    direction: Direction
    target: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    description: str = ""

    def validate(self) -> None:
        if not self.name.strip():
            raise MetricValidationError("Metric name cannot be empty.")

        if self.target is not None and self.target < 0:
            raise MetricValidationError("Target cannot be negative.")

        if self.minimum is not None and self.maximum is not None:
            if self.minimum > self.maximum:
                raise MetricValidationError(
                    "Minimum cannot exceed maximum."
                )


@dataclass(frozen=True)
class MetricObservation:
    metric_name: str
    period: str
    value: float
    sample_size: int
    recorded_at: date

    def validate(self) -> None:
        if not self.metric_name.strip():
            raise MetricValidationError("Metric name is required.")

        if not self.period.strip():
            raise MetricValidationError("Period is required.")

        if self.sample_size <= 0:
            raise MetricValidationError(
                "Sample size must be greater than zero."
            )

        if self.value < 0:
            raise MetricValidationError(
                f"Negative observation: {self.metric_name}"
            )


@dataclass
class MetricResult:
    metric_name: str
    category: str
    current: float
    previous: float | None
    target: float | None
    change_percent: float | None
    target_achievement_percent: float | None
    status: str


@dataclass
class Alert:
    metric_name: str
    severity: Severity
    message: str
    observed_value: float


@dataclass
class ProductReport:
    product_name: str
    reporting_period: str
    north_star: dict[str, Any]
    metrics: list[dict[str, Any]]
    alerts: list[dict[str, Any]]
    diagnosis: list[str]


class MetricRegistry:
    """Stores validated metric definitions."""

    def __init__(self) -> None:
        self._definitions: dict[str, MetricDefinition] = {}

    def register(self, definition: MetricDefinition) -> None:
        definition.validate()

        key = definition.name.lower()

        if key in self._definitions:
            raise MetricValidationError(
                f"Metric already registered: {definition.name}"
            )

        self._definitions[key] = definition

    def get(self, name: str) -> MetricDefinition:
        try:
            return self._definitions[name.lower()]
        except KeyError as exc:
            raise MetricValidationError(
                f"Unknown metric: {name}"
            ) from exc

    def all(self) -> list[MetricDefinition]:
        return list(self._definitions.values())

    def by_category(
        self,
        category: MetricCategory
    ) -> list[MetricDefinition]:
        return [
            item for item in self._definitions.values()
            if item.category == category
        ]


class MetricStore:
    """Stores observations and prevents duplicate period entries."""

    def __init__(self, registry: MetricRegistry) -> None:
        self.registry = registry
        self._observations: dict[
            tuple[str, str], MetricObservation
        ] = {}

    def record(self, observation: MetricObservation) -> None:
        observation.validate()
        definition = self.registry.get(observation.metric_name)

        if definition.minimum is not None:
            if observation.value < definition.minimum:
                raise MetricValidationError(
                    f"{observation.metric_name} is below its valid range."
                )

        if definition.maximum is not None:
            if observation.value > definition.maximum:
                raise MetricValidationError(
                    f"{observation.metric_name} exceeds its valid range."
                )

        key = (observation.metric_name.lower(), observation.period)

        if key in self._observations:
            raise MetricValidationError(
                f"Duplicate observation: {key}"
            )

        self._observations[key] = observation

    def get(
        self,
        metric_name: str,
        period: str
    ) -> MetricObservation | None:
        return self._observations.get(
            (metric_name.lower(), period)
        )

    def periods(self, metric_name: str) -> list[str]:
        return sorted(
            observation.period
            for (name, _), observation in self._observations.items()
            if name == metric_name.lower()
        )


class MetricEvaluator:
    def __init__(
        self,
        registry: MetricRegistry,
        store: MetricStore
    ) -> None:
        self.registry = registry
        self.store = store

    @staticmethod
    def percentage_change(
        current: float,
        previous: float | None
    ) -> float | None:
        if previous is None or previous == 0:
            return None

        return round(
            ((current - previous) / abs(previous)) * 100,
            2
        )

    def evaluate(
        self,
        metric_name: str,
        period: str,
        previous_period: str | None = None
    ) -> MetricResult:
        definition = self.registry.get(metric_name)
        current = self.store.get(metric_name, period)

        if current is None:
            raise MetricValidationError(
                f"Missing current observation: {metric_name}"
            )

        previous = (
            self.store.get(metric_name, previous_period)
            if previous_period else None
        )

        change = self.percentage_change(
            current.value,
            previous.value if previous else None
        )

        achievement = None

        if definition.target is not None and definition.target != 0:
            achievement = round(
                current.value / definition.target * 100,
                2
            )

        status = "on_track"

        if definition.direction == Direction.HIGHER:
            if definition.target is not None:
                status = (
                    "on_track"
                    if current.value >= definition.target
                    else "below_target"
                )

        elif definition.direction == Direction.LOWER:
            if definition.target is not None:
                status = (
                    "on_track"
                    if current.value <= definition.target
                    else "above_limit"
                )

        elif definition.direction == Direction.RANGE:
            if (
                definition.minimum is not None
                and current.value < definition.minimum
            ):
                status = "below_range"
            elif (
                definition.maximum is not None
                and current.value > definition.maximum
            ):
                status = "above_range"

        return MetricResult(
            metric_name=definition.name,
            category=definition.category.value,
            current=current.value,
            previous=previous.value if previous else None,
            target=definition.target,
            change_percent=change,
            target_achievement_percent=achievement,
            status=status
        )


class GuardrailMonitor:
    """Detects product quality and user experience deterioration."""

    def __init__(
        self,
        registry: MetricRegistry,
        store: MetricStore
    ) -> None:
        self.registry = registry
        self.store = store

    def inspect(self, period: str) -> list[Alert]:
        alerts: list[Alert] = []

        for definition in self.registry.by_category(
            MetricCategory.GUARDRAIL
        ):
            observation = self.store.get(
                definition.name,
                period
            )

            if observation is None:
                alerts.append(
                    Alert(
                        definition.name,
                        Severity.WARNING,
                        "Guardrail observation is missing.",
                        0
                    )
                )
                continue

            if (
                definition.maximum is not None
                and observation.value > definition.maximum
            ):
                alerts.append(
                    Alert(
                        definition.name,
                        Severity.CRITICAL,
                        f"Value exceeds maximum of "
                        f"{definition.maximum} {definition.unit}.",
                        observation.value
                    )
                )

            elif (
                definition.minimum is not None
                and observation.value < definition.minimum
            ):
                alerts.append(
                    Alert(
                        definition.name,
                        Severity.CRITICAL,
                        f"Value is below minimum of "
                        f"{definition.minimum} {definition.unit}.",
                        observation.value
                    )
                )

        return alerts


class ProductAnalytics:
    def __init__(
        self,
        product_name: str,
        registry: MetricRegistry,
        store: MetricStore
    ) -> None:
        self.product_name = product_name
        self.registry = registry
        self.store = store
        self.evaluator = MetricEvaluator(registry, store)
        self.guardrails = GuardrailMonitor(registry, store)

    def diagnose(
        self,
        period: str,
        previous_period: str
    ) -> list[str]:
        findings: list[str] = []

        north_star = self.registry.by_category(
            MetricCategory.NORTH_STAR
        )

        for definition in north_star:
            result = self.evaluator.evaluate(
                definition.name,
                period,
                previous_period
            )

            if result.change_percent is not None:
                if result.change_percent > 0:
                    findings.append(
                        f"{definition.name} increased by "
                        f"{result.change_percent}%."
                    )
                elif result.change_percent < 0:
                    findings.append(
                        f"{definition.name} declined by "
                        f"{abs(result.change_percent)}%."
                    )

        for definition in self.registry.by_category(
            MetricCategory.INPUT
        ):
            result = self.evaluator.evaluate(
                definition.name,
                period,
                previous_period
            )

            if result.status != "on_track":
                findings.append(
                    f"Input metric {definition.name} is below target."
                )

        for alert in self.guardrails.inspect(period):
            findings.append(
                f"Guardrail issue: {alert.metric_name}: "
                f"{alert.message}"
            )

        return findings

    def generate_report(
        self,
        period: str,
        previous_period: str
    ) -> ProductReport:
        results: list[dict[str, Any]] = []

        for definition in self.registry.all():
            observation = self.store.get(
                definition.name,
                period
            )

            if observation is None:
                continue

            result = self.evaluator.evaluate(
                definition.name,
                period,
                previous_period
            )
            results.append(asdict(result))

        north_star_definitions = self.registry.by_category(
            MetricCategory.NORTH_STAR
        )

        if len(north_star_definitions) != 1:
            raise MetricValidationError(
                "Exactly one North Star Metric must be registered."
            )

        north_star_result = self.evaluator.evaluate(
            north_star_definitions[0].name,
            period,
            previous_period
        )

        alerts = self.guardrails.inspect(period)

        return ProductReport(
            product_name=self.product_name,
            reporting_period=period,
            north_star=asdict(north_star_result),
            metrics=results,
            alerts=[
                {
                    **asdict(alert),
                    "severity": alert.severity.value
                }
                for alert in alerts
            ],
            diagnosis=self.diagnose(period, previous_period)
        )


def build_demo() -> ProductAnalytics:
    registry = MetricRegistry()

    definitions = [
        MetricDefinition(
            "Weekly Active Learners",
            MetricCategory.NORTH_STAR,
            "learners",
            Direction.HIGHER,
            target=12000,
            description="Users completing meaningful learning activity."
        ),
        MetricDefinition(
            "New User Activation Rate",
            MetricCategory.INPUT,
            "%",
            Direction.HIGHER,
            target=65,
            minimum=0,
            maximum=100
        ),
        MetricDefinition(
            "Weekly Learning Sessions",
            MetricCategory.INPUT,
            "sessions",
            Direction.HIGHER,
            target=45000
        ),
        MetricDefinition(
            "Lesson Completion Rate",
            MetricCategory.INPUT,
            "%",
            Direction.HIGHER,
            target=75,
            minimum=0,
            maximum=100
        ),
        MetricDefinition(
            "Subscription Revenue",
            MetricCategory.OUTPUT,
            "INR",
            Direction.HIGHER,
            target=1500000
        ),
        MetricDefinition(
            "Customer Retention Rate",
            MetricCategory.OUTPUT,
            "%",
            Direction.HIGHER,
            target=85,
            minimum=0,
            maximum=100
        ),
        MetricDefinition(
            "Application Error Rate",
            MetricCategory.GUARDRAIL,
            "%",
            Direction.LOWER,
            target=1,
            minimum=0,
            maximum=2
        ),
        MetricDefinition(
            "Average Page Load Time",
            MetricCategory.GUARDRAIL,
            "seconds",
            Direction.LOWER,
            target=2,
            minimum=0,
            maximum=3
        ),
        MetricDefinition(
            "Support Complaint Rate",
            MetricCategory.GUARDRAIL,
            "%",
            Direction.LOWER,
            target=2,
            minimum=0,
            maximum=3
        )
    ]

    for definition in definitions:
        registry.register(definition)

    store = MetricStore(registry)

    data = {
        "previous": {
            "Weekly Active Learners": 10800,
            "New User Activation Rate": 62,
            "Weekly Learning Sessions": 41000,
            "Lesson Completion Rate": 72,
            "Subscription Revenue": 1380000,
            "Customer Retention Rate": 84,
            "Application Error Rate": 0.8,
            "Average Page Load Time": 1.8,
            "Support Complaint Rate": 1.5
        },
        "current": {
            "Weekly Active Learners": 12400,
            "New User Activation Rate": 68,
            "Weekly Learning Sessions": 47000,
            "Lesson Completion Rate": 78,
            "Subscription Revenue": 1570000,
            "Customer Retention Rate": 86,
            "Application Error Rate": 2.4,
            "Average Page Load Time": 2.2,
            "Support Complaint Rate": 1.8
        }
    }

    base_date = date.today()

    for period, observations in data.items():
        recorded = (
            base_date - timedelta(days=7)
            if period == "previous"
            else base_date
        )

        for name, value in observations.items():
            store.record(
                MetricObservation(
                    metric_name=name,
                    period=period,
                    value=value,
                    sample_size=10000,
                    recorded_at=recorded
                )
            )

    return ProductAnalytics(
        "Learning Platform",
        registry,
        store
    )


def run_tests(analytics: ProductAnalytics) -> None:
    evaluator = analytics.evaluator

    assert evaluator.percentage_change(120, 100) == 20.0
    assert evaluator.percentage_change(100, 0) is None

    result = evaluator.evaluate(
        "Weekly Active Learners",
        "current",
        "previous"
    )

    assert result.current == 12400
    assert result.status == "on_track"

    alerts = analytics.guardrails.inspect("current")

    assert any(
        alert.metric_name == "Application Error Rate"
        and alert.severity == Severity.CRITICAL
        for alert in alerts
    )

    try:
        MetricObservation(
            "Invalid",
            "test",
            -1,
            10,
            date.today()
        ).validate()
    except MetricValidationError:
        pass
    else:
        raise AssertionError("Negative values must be rejected.")

    logger.info("All validation assertions passed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Product Metrics Analytics Engine"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON report output path."
    )

    args = parser.parse_args()

    analytics = build_demo()
    run_tests(analytics)

    report = analytics.generate_report(
        "current",
        "previous"
    )

    output = json.dumps(
        asdict(report),
        indent=2,
        default=str
    )

    print("\nPRODUCT METRICS REPORT")
    print("=" * 65)
    print(output)

    if args.json:
        args.json.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        args.json.write_text(output, encoding="utf-8")
        logger.info("Report saved to %s", args.json)


if __name__ == "__main__":
    main()
