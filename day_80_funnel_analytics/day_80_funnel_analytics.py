"""
Funnel Analytics
----------------
Implements event collection, funnel construction, conversion rates,
drop-off analysis, time-window validation, segmentation, and reporting.

Runtime: Python 3.10+
Dependencies: Python standard library only.
"""

from __future__ import annotations

import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("funnel_analytics")


class FunnelError(Exception):
    """Base exception for funnel analytics."""


class ValidationError(FunnelError):
    """Raised when event or funnel input is invalid."""


class FunnelStepType(Enum):
    VISIT = "visit"
    PRODUCT_VIEW = "product_view"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT = "checkout"
    PURCHASE = "purchase"


@dataclass(frozen=True)
class Event:
    event_id: str
    user_id: str
    event_name: str
    timestamp: datetime
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.event_id.strip():
            raise ValidationError("Event ID cannot be empty.")

        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty.")

        if not self.event_name.strip():
            raise ValidationError("Event name cannot be empty.")

        if self.timestamp.tzinfo is None:
            raise ValidationError("Timestamp must include timezone information.")

        if not isinstance(self.properties, dict):
            raise ValidationError("Event properties must be a dictionary.")


@dataclass(frozen=True)
class FunnelDefinition:
    name: str
    steps: tuple[str, ...]
    conversion_window_hours: int = 168

    def __post_init__(self):
        if not self.name.strip():
            raise ValidationError("Funnel name cannot be empty.")

        if len(self.steps) < 2:
            raise ValidationError("A funnel requires at least two steps.")

        if len(set(self.steps)) != len(self.steps):
            raise ValidationError("Funnel steps must be unique.")

        if any(not step.strip() for step in self.steps):
            raise ValidationError("Funnel step names cannot be empty.")

        if self.conversion_window_hours <= 0:
            raise ValidationError("Conversion window must be positive.")


@dataclass
class StepMetrics:
    step_name: str
    users: int
    previous_users: int
    conversion_rate: float
    drop_off_rate: float
    dropped_users: int


@dataclass
class FunnelReport:
    funnel_name: str
    total_users: int
    converted_users: int
    overall_conversion_rate: float
    steps: list[StepMetrics]

    def display(self) -> None:
        print(f"\nFUNNEL REPORT: {self.funnel_name}")
        print("=" * 78)
        print(f"Initial users: {self.total_users}")
        print(f"Completed users: {self.converted_users}")
        print(f"Overall conversion: {self.overall_conversion_rate:.2f}%")
        print("-" * 78)

        print(
            f"{'Step':<20}{'Users':>10}{'Conversion':>15}"
            f"{'Drop-off':>15}{'Dropped':>12}"
        )

        for step in self.steps:
            print(
                f"{step.step_name:<20}"
                f"{step.users:>10}"
                f"{step.conversion_rate:>14.2f}%"
                f"{step.drop_off_rate:>14.2f}%"
                f"{step.dropped_users:>12}"
            )


class EventStore:
    """Stores unique events and supports efficient user-level retrieval."""

    def __init__(self):
        self._events: dict[str, Event] = {}
        self._user_events: dict[str, list[Event]] = defaultdict(list)

    def add(self, event: Event) -> None:
        if event.event_id in self._events:
            raise ValidationError(
                f"Duplicate event ID: {event.event_id}"
            )

        self._events[event.event_id] = event
        self._user_events[event.user_id].append(event)

    def add_many(self, events: Iterable[Event]) -> None:
        # Validate the complete batch before modifying the store.
        batch = list(events)
        incoming_ids = [event.event_id for event in batch]

        if len(incoming_ids) != len(set(incoming_ids)):
            raise ValidationError("Duplicate event IDs within batch.")

        if any(event_id in self._events for event_id in incoming_ids):
            raise ValidationError("Batch contains an existing event ID.")

        for event in batch:
            self.add(event)

    def get_user_events(self, user_id: str) -> list[Event]:
        return sorted(
            self._user_events.get(user_id, []),
            key=lambda event: event.timestamp
        )

    def all_events(self) -> list[Event]:
        return sorted(
            self._events.values(),
            key=lambda event: event.timestamp
        )

    def count(self) -> int:
        return len(self._events)


class FunnelAnalyzer:
    """Analyzes ordered, user-level funnel progression."""

    def __init__(self, store: EventStore):
        self.store = store

    def _first_valid_progression(
        self,
        events: list[Event],
        funnel: FunnelDefinition
    ) -> dict[str, Optional[datetime]]:
        """
        Find the first sequential progression through the funnel.

        Repeated events do not create additional users.
        Events must occur within the configured conversion window.
        """
        progression: dict[str, Optional[datetime]] = {
            step: None for step in funnel.steps
        }

        step_index = 0
        first_timestamp: Optional[datetime] = None

        for event in events:
            if event.event_name != funnel.steps[step_index]:
                continue

            if first_timestamp is None:
                first_timestamp = event.timestamp

            if (
                event.timestamp - first_timestamp
                > timedelta(hours=funnel.conversion_window_hours)
            ):
                break

            progression[funnel.steps[step_index]] = event.timestamp
            step_index += 1

            if step_index == len(funnel.steps):
                break

        return progression

    def analyze(
        self,
        funnel: FunnelDefinition,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        segment: Optional[dict[str, Any]] = None
    ) -> FunnelReport:
        """
        Construct a funnel using distinct users.

        Cohort membership is determined by the first-step event.
        Segment attributes are evaluated against that event.
        """
        if start and start.tzinfo is None:
            raise ValidationError("Start time must be timezone-aware.")

        if end and end.tzinfo is None:
            raise ValidationError("End time must be timezone-aware.")

        if start and end and start > end:
            raise ValidationError("Start time cannot exceed end time.")

        segment = segment or {}

        users: dict[str, list[Event]] = defaultdict(list)

        for event in self.store.all_events():
            users[event.user_id].append(event)

        step_counts = [0] * len(funnel.steps)

        for user_id, events in users.items():
            first_events = [
                event for event in events
                if event.event_name == funnel.steps[0]
                and (start is None or event.timestamp >= start)
                and (end is None or event.timestamp <= end)
            ]

            if not first_events:
                continue

            entry_event = min(
                first_events,
                key=lambda event: event.timestamp
            )

            # Apply segmentation to the cohort-entry event.
            matches_segment = all(
                entry_event.properties.get(key) == value
                for key, value in segment.items()
            )

            if not matches_segment:
                continue

            eligible_events = [
                event for event in events
                if event.timestamp >= entry_event.timestamp
            ]

            progression = self._first_valid_progression(
                eligible_events,
                funnel
            )

            for index, step in enumerate(funnel.steps):
                if progression[step] is not None:
                    step_counts[index] += 1
                else:
                    # Progression must remain sequential.
                    break

        total_users = step_counts[0]

        metrics: list[StepMetrics] = []

        for index, step_name in enumerate(funnel.steps):
            current = step_counts[index]

            previous = (
                total_users if index == 0
                else step_counts[index - 1]
            )

            conversion = (
                current / previous * 100
                if previous else 0.0
            )

            dropped = max(0, previous - current)

            drop_off = (
                dropped / previous * 100
                if previous else 0.0
            )

            metrics.append(
                StepMetrics(
                    step_name=step_name,
                    users=current,
                    previous_users=previous,
                    conversion_rate=conversion,
                    drop_off_rate=drop_off,
                    dropped_users=dropped
                )
            )

        converted = step_counts[-1]

        overall = (
            converted / total_users * 100
            if total_users else 0.0
        )

        return FunnelReport(
            funnel_name=funnel.name,
            total_users=total_users,
            converted_users=converted,
            overall_conversion_rate=overall,
            steps=metrics
        )


class SegmentAnalyzer:
    """Compares conversion performance across event properties."""

    def __init__(self, analyzer: FunnelAnalyzer):
        self.analyzer = analyzer

    def compare(
        self,
        funnel: FunnelDefinition,
        property_name: str
    ) -> dict[str, FunnelReport]:
        if not property_name.strip():
            raise ValidationError("Segment property cannot be empty.")

        values = {
            event.properties[property_name]
            for event in self.analyzer.store.all_events()
            if (
                event.event_name == funnel.steps[0]
                and property_name in event.properties
            )
        }

        reports = {}

        for value in sorted(values, key=str):
            reports[str(value)] = self.analyzer.analyze(
                funnel,
                segment={property_name: value}
            )

        return reports


def create_sample_data() -> EventStore:
    store = EventStore()

    base = datetime(2026, 11, 1, 9, 0, tzinfo=timezone.utc)

    user_journeys = {
        "U001": [
            "visit", "product_view", "add_to_cart",
            "checkout", "purchase"
        ],
        "U002": [
            "visit", "product_view", "add_to_cart", "checkout"
        ],
        "U003": [
            "visit", "product_view"
        ],
        "U004": [
            "visit", "product_view", "add_to_cart",
            "checkout", "purchase"
        ],
        "U005": [
            "visit", "product_view", "add_to_cart"
        ],
        "U006": [
            "visit"
        ],
        "U007": [
            "visit", "product_view", "add_to_cart",
            "checkout", "purchase"
        ],
        "U008": [
            "visit", "product_view", "checkout"
        ],
    }

    channels = [
        "organic", "paid", "organic", "paid",
        "referral", "organic", "paid", "referral"
    ]

    devices = [
        "mobile", "desktop", "mobile", "desktop",
        "mobile", "desktop", "mobile", "desktop"
    ]

    events = []

    counter = 1

    for user_index, (user_id, journey) in enumerate(
        user_journeys.items()
    ):
        for step_index, event_name in enumerate(journey):
            timestamp = base + timedelta(
                minutes=user_index * 15 + step_index * 3
            )

            properties = {
                "channel": channels[user_index],
                "device": devices[user_index],
                "country": "IN" if user_index % 2 == 0 else "US",
                "campaign": "winter_2026"
            }

            events.append(
                Event(
                    event_id=f"E{counter:04d}",
                    user_id=user_id,
                    event_name=event_name,
                    timestamp=timestamp,
                    properties=properties
                )
            )

            counter += 1

    store.add_many(events)

    return store


def export_report(
    report: FunnelReport,
    filename: str = "funnel_report.json"
) -> None:
    data = {
        "funnel_name": report.funnel_name,
        "total_users": report.total_users,
        "converted_users": report.converted_users,
        "overall_conversion_rate": report.overall_conversion_rate,
        "steps": [
            {
                "step": metric.step_name,
                "users": metric.users,
                "previous_users": metric.previous_users,
                "conversion_rate": metric.conversion_rate,
                "drop_off_rate": metric.drop_off_rate,
                "dropped_users": metric.dropped_users
            }
            for metric in report.steps
        ]
    }

    Path(filename).write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )


def validate_funnel_invariants(report: FunnelReport) -> None:
    counts = [metric.users for metric in report.steps]

    assert all(
        counts[index] >= counts[index + 1]
        for index in range(len(counts) - 1)
    ), "Funnel counts must be monotonically non-increasing."

    assert 0 <= report.overall_conversion_rate <= 100

    for metric in report.steps:
        assert 0 <= metric.conversion_rate <= 100
        assert 0 <= metric.drop_off_rate <= 100


def run_tests() -> None:
    store = create_sample_data()

    funnel = FunnelDefinition(
        name="E-commerce Purchase Funnel",
        steps=(
            "visit",
            "product_view",
            "add_to_cart",
            "checkout",
            "purchase"
        ),
        conversion_window_hours=24
    )

    analyzer = FunnelAnalyzer(store)
    report = analyzer.analyze(funnel)

    assert report.total_users == 8
    assert report.converted_users == 3
    assert report.steps[1].users == 7
    assert report.steps[2].users == 5
    assert report.steps[3].users == 4
    assert report.steps[4].users == 3

    validate_funnel_invariants(report)

    # Verify duplicate event protection.
    try:
        store.add(store.all_events()[0])
        raise AssertionError("Duplicate event was accepted.")
    except ValidationError:
        pass

    # Verify empty-cohort handling.
    empty_report = analyzer.analyze(
        funnel,
        start=datetime(2030, 1, 1, tzinfo=timezone.utc)
    )

    assert empty_report.total_users == 0
    assert empty_report.overall_conversion_rate == 0

    print("All funnel analytics tests passed.")


def main() -> None:
    print("FUNNEL ANALYTICS ENGINE")
    print("=" * 50)

    store = create_sample_data()

    funnel = FunnelDefinition(
        name="E-commerce Purchase Funnel",
        steps=(
            "visit",
            "product_view",
            "add_to_cart",
            "checkout",
            "purchase"
        ),
        conversion_window_hours=24
    )

    analyzer = FunnelAnalyzer(store)

    report = analyzer.analyze(funnel)
    report.display()

    print("\nCHANNEL SEGMENTATION")
    print("=" * 50)

    segments = SegmentAnalyzer(analyzer).compare(
        funnel,
        "channel"
    )

    for channel, segment_report in segments.items():
        print(
            f"{channel}: "
            f"{segment_report.converted_users}/"
            f"{segment_report.total_users} users, "
            f"{segment_report.overall_conversion_rate:.2f}% conversion"
        )

    print("\nDEVICE SEGMENTATION")
    print("=" * 50)

    device_segments = SegmentAnalyzer(analyzer).compare(
        funnel,
        "device"
    )

    for device, segment_report in device_segments.items():
        print(
            f"{device}: "
            f"{segment_report.overall_conversion_rate:.2f}%"
        )

    export_report(report)
    print("\nReport exported to funnel_report.json")

    run_tests()


if __name__ == "__main__":
    try:
        main()
    except (FunnelError, OSError, ValueError) as error:
        logger.exception("Funnel analytics execution failed: %s", error)
        raise SystemExit(1)
