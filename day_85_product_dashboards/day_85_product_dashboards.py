#!/usr/bin/env python3
"""
Product Dashboard Engineering System

Demonstrates:
- Metric hierarchy and KPI definitions
- Dashboard aggregation and visualization-ready data
- Metric validation and dimensional analysis
- Alert thresholds, severity and deduplication
- Time-window comparisons
- Dashboard access control
- JSON export and automated tests

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import logging
import statistics
import unittest

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s"
)

logger = logging.getLogger("product_dashboard")


class DashboardError(Exception):
    """Base dashboard exception."""


class ValidationError(DashboardError):
    """Raised when metric data is invalid."""


class PermissionDenied(DashboardError):
    """Raised when a user cannot access a dashboard."""


class MetricType(Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DURATION = "duration"
    RATIO = "ratio"


class MetricCategory(Enum):
    NORTH_STAR = "north_star"
    BUSINESS = "business"
    PRODUCT = "product"
    ENGAGEMENT = "engagement"
    RELIABILITY = "reliability"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DashboardRole(Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class Aggregation(Enum):
    SUM = "sum"
    AVERAGE = "average"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    LAST = "last"


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    description: str
    metric_type: MetricType
    category: MetricCategory
    unit: str
    aggregation: Aggregation
    higher_is_better: bool
    target: float | None = None
    warning_threshold: float | None = None
    critical_threshold: float | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Metric name cannot be empty.")

        if self.target is not None and not isinstance(
            self.target, (int, float)
        ):
            raise ValidationError("Target must be numeric.")

        if self.warning_threshold is not None and (
            self.critical_threshold is not None
            and self.warning_threshold == self.critical_threshold
        ):
            raise ValidationError(
                "Warning and critical thresholds must differ."
            )

        if self.metric_type == MetricType.PERCENTAGE:
            if self.unit != "%":
                raise ValidationError(
                    "Percentage metrics must use % as their unit."
                )


@dataclass(frozen=True)
class MetricObservation:
    metric_name: str
    value: float
    timestamp: datetime
    dimensions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.metric_name:
            raise ValidationError("Metric name is required.")

        if isinstance(self.value, bool) or not isinstance(
            self.value, (int, float)
        ):
            raise ValidationError("Metric value must be numeric.")

        if not __import__("math").isfinite(self.value):
            raise ValidationError("Metric value must be finite.")

        if self.timestamp.tzinfo is None:
            raise ValidationError("Timestamp must include a timezone.")


@dataclass
class Alert:
    metric_name: str
    severity: AlertSeverity
    observed_value: float
    message: str
    timestamp: datetime
    fingerprint: str
    acknowledged: bool = False


@dataclass
class Dashboard:
    dashboard_id: str
    title: str
    description: str
    metric_names: list[str]
    refresh_interval_seconds: int = 60
    users: dict[str, DashboardRole] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.refresh_interval_seconds < 5:
            raise ValidationError(
                "Refresh interval must be at least five seconds."
            )

        if not self.dashboard_id or not self.title:
            raise ValidationError(
                "Dashboard ID and title are required."
            )


class MetricRegistry:
    """Central registry for consistent metric definitions."""

    def __init__(self) -> None:
        self._definitions: dict[str, MetricDefinition] = {}

    def register(self, definition: MetricDefinition) -> None:
        if definition.name in self._definitions:
            raise ValidationError(
                f"Metric already registered: {definition.name}"
            )

        self._definitions[definition.name] = definition

    def get(self, name: str) -> MetricDefinition:
        try:
            return self._definitions[name]
        except KeyError:
            raise ValidationError(f"Unknown metric: {name}") from None

    def all(self) -> list[MetricDefinition]:
        return list(self._definitions.values())


class MetricStore:
    """Stores observations and provides bounded time-window queries."""

    def __init__(self, registry: MetricRegistry) -> None:
        self.registry = registry
        self._observations: dict[
            str, list[MetricObservation]
        ] = defaultdict(list)

    def add(self, observation: MetricObservation) -> None:
        definition = self.registry.get(observation.metric_name)

        if (
            definition.metric_type == MetricType.PERCENTAGE
            and not 0 <= observation.value <= 100
        ):
            raise ValidationError(
                f"{observation.metric_name} must be between 0 and 100."
            )

        if (
            definition.metric_type in (
                MetricType.COUNT,
                MetricType.DURATION,
            )
            and observation.value < 0
        ):
            raise ValidationError(
                f"{observation.metric_name} cannot be negative."
            )

        dimensions = dict(observation.dimensions)

        if len(dimensions) != len(observation.dimensions):
            raise ValidationError("Duplicate observation dimensions.")

        if any(not k or not v for k, v in dimensions.items()):
            raise ValidationError("Dimension names and values are required.")

        self._observations[observation.metric_name].append(observation)

        # Keep data ordered for predictable range queries.
        self._observations[observation.metric_name].sort(
            key=lambda item: item.timestamp
        )

    def query(
        self,
        metric_name: str,
        start: datetime,
        end: datetime,
        dimensions: dict[str, str] | None = None,
    ) -> list[MetricObservation]:

        self.registry.get(metric_name)

        if start.tzinfo is None or end.tzinfo is None:
            raise ValidationError("Time boundaries must be timezone-aware.")

        if start >= end:
            raise ValidationError("Start must precede end.")

        expected = dimensions or {}

        return [
            observation
            for observation in self._observations[metric_name]
            if start <= observation.timestamp < end
            and all(
                dict(observation.dimensions).get(key) == value
                for key, value in expected.items()
            )
        ]


class MetricAggregator:
    """Converts raw observations into dashboard-ready KPI values."""

    @staticmethod
    def aggregate(
        observations: Iterable[MetricObservation],
        method: Aggregation,
    ) -> float | None:

        values = [item.value for item in observations]

        if not values:
            return None

        if method == Aggregation.SUM:
            return sum(values)

        if method == Aggregation.AVERAGE:
            return statistics.fmean(values)

        if method == Aggregation.MINIMUM:
            return min(values)

        if method == Aggregation.MAXIMUM:
            return max(values)

        if method == Aggregation.LAST:
            return values[-1]

        raise ValidationError("Unsupported aggregation method.")


class AlertEngine:
    """Evaluates metric thresholds and suppresses duplicate alerts."""

    def __init__(self) -> None:
        self._active_fingerprints: set[str] = set()

    def evaluate(
        self,
        definition: MetricDefinition,
        value: float,
        timestamp: datetime,
    ) -> Alert | None:

        if not __import__("math").isfinite(value):
            raise ValidationError("Alert value must be finite.")

        warning = definition.warning_threshold
        critical = definition.critical_threshold

        if definition.higher_is_better:
            severity = (
                AlertSeverity.CRITICAL
                if critical is not None and value < critical
                else AlertSeverity.WARNING
                if warning is not None and value < warning
                else None
            )
        else:
            severity = (
                AlertSeverity.CRITICAL
                if critical is not None and value > critical
                else AlertSeverity.WARNING
                if warning is not None and value > warning
                else None
            )

        if severity is None:
            return None

        fingerprint = f"{definition.name}:{severity.value}"

        if fingerprint in self._active_fingerprints:
            return None

        self._active_fingerprints.add(fingerprint)

        return Alert(
            metric_name=definition.name,
            severity=severity,
            observed_value=value,
            message=(
                f"{definition.name} breached its "
                f"{severity.value} threshold."
            ),
            timestamp=timestamp,
            fingerprint=fingerprint,
        )

    def acknowledge(self, alert: Alert) -> None:
        alert.acknowledged = True
        self._active_fingerprints.discard(alert.fingerprint)


class DashboardService:
    """Builds dashboards after checking authorization and data quality."""

    def __init__(
        self,
        registry: MetricRegistry,
        store: MetricStore,
        alert_engine: AlertEngine,
    ) -> None:
        self.registry = registry
        self.store = store
        self.alert_engine = alert_engine

    @staticmethod
    def authorize(
        dashboard: Dashboard,
        username: str,
        required_role: DashboardRole,
    ) -> None:

        role = dashboard.users.get(username)

        hierarchy = {
            DashboardRole.VIEWER: 1,
            DashboardRole.ANALYST: 2,
            DashboardRole.ADMIN: 3,
        }

        if role is None or hierarchy[role] < hierarchy[required_role]:
            raise PermissionDenied(
                f"{username} lacks {required_role.value} access."
            )

    def build(
        self,
        dashboard: Dashboard,
        username: str,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:

        self.authorize(
            dashboard,
            username,
            DashboardRole.VIEWER,
        )

        output: dict[str, Any] = {
            "dashboard_id": dashboard.dashboard_id,
            "title": dashboard.title,
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
            "metrics": {},
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        for metric_name in dashboard.metric_names:
            definition = self.registry.get(metric_name)

            observations = self.store.query(
                metric_name,
                start,
                end,
            )

            value = MetricAggregator.aggregate(
                observations,
                definition.aggregation,
            )

            previous_duration = end - start
            previous_start = start - previous_duration

            previous_observations = self.store.query(
                metric_name,
                previous_start,
                start,
            )

            previous_value = MetricAggregator.aggregate(
                previous_observations,
                definition.aggregation,
            )

            change = None

            if previous_value is not None and previous_value != 0:
                change = (
                    (value - previous_value)
                    / abs(previous_value)
                ) * 100 if value is not None else None

            alert = None

            if value is not None:
                alert = self.alert_engine.evaluate(
                    definition,
                    value,
                    end,
                )

            output["metrics"][metric_name] = {
                "value": value,
                "unit": definition.unit,
                "category": definition.category.value,
                "target": definition.target,
                "previous_period_value": previous_value,
                "change_percentage": change,
                "observations": len(observations),
                "alert": (
                    {
                        "severity": alert.severity.value,
                        "message": alert.message,
                    }
                    if alert else None
                ),
            }

        return output


class DashboardExporter:
    """Exports dashboard data atomically."""

    @staticmethod
    def export_json(
        dashboard_data: dict[str, Any],
        output_path: str,
    ) -> Path:

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        temporary = destination.with_suffix(
            destination.suffix + ".tmp"
        )

        try:
            temporary.write_text(
                json.dumps(
                    dashboard_data,
                    indent=2,
                    allow_nan=False,
                ),
                encoding="utf-8",
            )

            temporary.replace(destination)

        except OSError:
            temporary.unlink(missing_ok=True)
            raise

        return destination


def build_sample_system() -> tuple[
    DashboardService,
    Dashboard,
    MetricStore,
    AlertEngine,
]:
    registry = MetricRegistry()

    definitions = [
        MetricDefinition(
            "monthly_active_users",
            "Distinct users active during the reporting period.",
            MetricType.COUNT,
            MetricCategory.NORTH_STAR,
            "users",
            Aggregation.LAST,
            True,
            target=50000,
            warning_threshold=40000,
            critical_threshold=30000,
        ),
        MetricDefinition(
            "conversion_rate",
            "Percentage of visitors completing a purchase.",
            MetricType.PERCENTAGE,
            MetricCategory.BUSINESS,
            "%",
            Aggregation.AVERAGE,
            True,
            target=5.0,
            warning_threshold=3.5,
            critical_threshold=2.0,
        ),
        MetricDefinition(
            "daily_revenue",
            "Daily recognized revenue.",
            MetricType.CURRENCY,
            MetricCategory.BUSINESS,
            "INR",
            Aggregation.SUM,
            True,
            target=500000,
        ),
        MetricDefinition(
            "crash_rate",
            "Percentage of sessions ending in a crash.",
            MetricType.PERCENTAGE,
            MetricCategory.RELIABILITY,
            "%",
            Aggregation.AVERAGE,
            False,
            target=0.5,
            warning_threshold=1.0,
            critical_threshold=2.0,
        ),
        MetricDefinition(
            "average_session_duration",
            "Average session duration in seconds.",
            MetricType.DURATION,
            MetricCategory.ENGAGEMENT,
            "seconds",
            Aggregation.AVERAGE,
            True,
            target=300,
        ),
    ]

    for definition in definitions:
        registry.register(definition)

    store = MetricStore(registry)
    alert_engine = AlertEngine()

    now = datetime.now(timezone.utc).replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    # Insert two reporting periods to enable comparison.
    sample_values = {
        "monthly_active_users": (35000, 38000),
        "conversion_rate": (4.1, 3.2),
        "daily_revenue": (420000, 390000),
        "crash_rate": (0.7, 2.4),
        "average_session_duration": (280, 250),
    }

    for metric_name, (previous, current) in sample_values.items():
        for index, value in enumerate((previous, current)):
            timestamp = now - timedelta(days=1 - index)

            store.add(
                MetricObservation(
                    metric_name=metric_name,
                    value=value,
                    timestamp=timestamp,
                    dimensions=(("platform", "all"),),
                )
            )

    dashboard = Dashboard(
        dashboard_id="product-executive-001",
        title="Product Performance Dashboard",
        description="Executive view of product health and performance.",
        metric_names=[
            item.name for item in definitions
        ],
        refresh_interval_seconds=60,
        users={
            "admin": DashboardRole.ADMIN,
            "analyst": DashboardRole.ANALYST,
            "viewer": DashboardRole.VIEWER,
        },
    )

    service = DashboardService(
        registry,
        store,
        alert_engine,
    )

    return service, dashboard, store, alert_engine


class DashboardTests(unittest.TestCase):

    def setUp(self) -> None:
        (
            self.service,
            self.dashboard,
            self.store,
            self.alert_engine,
        ) = build_sample_system()

    def test_metric_validation(self) -> None:
        with self.assertRaises(ValidationError):
            self.store.add(
                MetricObservation(
                    "conversion_rate",
                    120,
                    datetime.now(timezone.utc),
                )
            )

    def test_dashboard_access(self) -> None:
        with self.assertRaises(PermissionDenied):
            self.service.authorize(
                self.dashboard,
                "unknown",
                DashboardRole.VIEWER,
            )

    def test_aggregation(self) -> None:
        observations = [
            MetricObservation(
                "monthly_active_users",
                10,
                datetime.now(timezone.utc),
            ),
            MetricObservation(
                "monthly_active_users",
                20,
                datetime.now(timezone.utc),
            ),
        ]

        self.assertEqual(
            MetricAggregator.aggregate(
                observations,
                Aggregation.SUM,
            ),
            30,
        )

    def test_alert_deduplication(self) -> None:
        definition = MetricDefinition(
            "test_metric",
            "Test metric",
            MetricType.COUNT,
            MetricCategory.PRODUCT,
            "items",
            Aggregation.LAST,
            True,
            warning_threshold=50,
            critical_threshold=20,
        )

        timestamp = datetime.now(timezone.utc)

        first = self.alert_engine.evaluate(
            definition, 10, timestamp
        )

        second = self.alert_engine.evaluate(
            definition, 10, timestamp
        )

        self.assertIsNotNone(first)
        self.assertIsNone(second)


def main() -> None:
    service, dashboard, store, _ = build_sample_system()

    now = datetime.now(timezone.utc).replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    result = service.build(
        dashboard,
        "admin",
        now - timedelta(days=1),
        now + timedelta(hours=1),
    )

    print("\nPRODUCT DASHBOARD")
    print("=" * 55)

    for name, metric in result["metrics"].items():
        print(
            f"{name:30} "
            f"{str(metric['value']):12} "
            f"{metric['unit']:10} "
            f"alert={metric['alert']}"
        )

    print("\nDashboard JSON export:")
    print(json.dumps(result, indent=2))

    try:
        path = DashboardExporter.export_json(
            result,
            "output/product_dashboard.json",
        )
        logger.info("Exported dashboard to %s", path)

    except OSError as error:
        logger.error("Export failed: %s", error)

    print("\nRUNNING AUTOMATED TESTS")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        DashboardTests
    )
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)

    if not outcome.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
