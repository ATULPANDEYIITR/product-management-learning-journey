#!/usr/bin/env python3
"""
Product Analytics Engine
========================
Implements event collection, property validation, user identity,
sessionization, event analysis, conversion funnels, retention cohorts,
and JSONL persistence using the Python standard library.

Run:
    python product_analytics.py

Optional:
    python product_analytics.py --output analytics_events.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import uuid

from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("product_analytics")


# ============================================================
# 1. Domain types
# ============================================================

class EventType(str, Enum):
    SIGNUP = "signup"
    LOGIN = "login"
    PAGE_VIEW = "page_view"
    PRODUCT_VIEW = "product_view"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT_STARTED = "checkout_started"
    PURCHASE = "purchase"
    LOGOUT = "logout"


class AnalyticsError(Exception):
    """Base exception for analytics operations."""


class ValidationError(AnalyticsError):
    """Invalid analytics input."""


class DuplicateEventError(AnalyticsError):
    """An event with an existing identifier was submitted."""


@dataclass(frozen=True)
class User:
    user_id: str
    anonymous_id: str | None = None
    country: str = "IN"
    plan: str = "free"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True)
class Event:
    event_id: str
    user_id: str
    event_name: str
    timestamp: datetime
    properties: dict[str, Any]
    session_id: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValidationError("Event ID cannot be empty.")

        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty.")

        if not self.event_name.strip():
            raise ValidationError("Event name cannot be empty.")

        if self.timestamp.tzinfo is None:
            raise ValidationError("Timestamp must include timezone.")

        if not isinstance(self.properties, dict):
            raise ValidationError("Properties must be a dictionary.")

        if len(self.properties) > 50:
            raise ValidationError("Too many event properties.")

        for key, value in self.properties.items():
            if not isinstance(key, str) or not key.strip():
                raise ValidationError("Property names must be nonempty.")

            if isinstance(value, (dict, list)):
                raise ValidationError(
                    f"Nested property is not supported: {key}"
                )

            if isinstance(value, float) and not __import__("math").isfinite(value):
                raise ValidationError(f"Non-finite numeric property: {key}")

            if value is not None and not isinstance(
                value, (str, int, float, bool)
            ):
                raise ValidationError(
                    f"Unsupported property type: {key}"
                )


@dataclass
class Session:
    session_id: str
    user_id: str
    started_at: datetime
    last_event_at: datetime
    events: list[Event] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return max(
            0.0,
            (self.last_event_at - self.started_at).total_seconds()
        )


@dataclass
class FunnelResult:
    name: str
    steps: list[str]
    counts: list[int]
    conversion_rates: list[float]
    overall_conversion: float


@dataclass
class CohortResult:
    cohort_month: str
    users: int
    retained_by_month: dict[int, int]
    retention_rates: dict[int, float]


# ============================================================
# 2. Input validation and event storage
# ============================================================

class EventStore:

    def __init__(self) -> None:
        self.events: list[Event] = []
        self.event_ids: set[str] = set()
        self.users: dict[str, User] = {}

    def register_user(self, user: User) -> None:
        if user.user_id in self.users:
            existing = self.users[user.user_id]

            if existing != user:
                raise ValidationError(
                    f"Conflicting user registration: {user.user_id}"
                )
            return

        self.users[user.user_id] = user

    def add_event(self, event: Event) -> None:
        if event.event_id in self.event_ids:
            raise DuplicateEventError(event.event_id)

        if event.user_id not in self.users:
            raise ValidationError(
                f"Unknown user: {event.user_id}"
            )

        self.event_ids.add(event.event_id)
        self.events.append(event)

    def add_events(self, events: Iterable[Event]) -> int:
        batch = list(events)
        seen = set()

        for event in batch:
            if event.event_id in self.event_ids or event.event_id in seen:
                raise DuplicateEventError(event.event_id)

            if event.user_id not in self.users:
                raise ValidationError(
                    f"Unknown user: {event.user_id}"
                )

            seen.add(event.event_id)

        self.events.extend(batch)
        self.event_ids.update(seen)
        return len(batch)

    def get_events(
        self,
        user_id: str | None = None,
        event_name: str | None = None,
    ) -> list[Event]:

        return [
            event
            for event in self.events
            if (user_id is None or event.user_id == user_id)
            and (event_name is None or event.event_name == event_name)
        ]


# ============================================================
# 3. Event tracking API
# ============================================================

class AnalyticsTracker:

    def __init__(self, store: EventStore) -> None:
        self.store = store

    def track(
        self,
        user_id: str,
        event_name: str | EventType,
        properties: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
        session_id: str | None = None,
        event_id: str | None = None,
    ) -> Event:

        if isinstance(event_name, EventType):
            event_name = event_name.value

        if not event_name or len(event_name) > 100:
            raise ValidationError("Invalid event name.")

        event = Event(
            event_id=event_id or str(uuid.uuid4()),
            user_id=user_id,
            event_name=event_name,
            timestamp=timestamp or datetime.now(timezone.utc),
            properties=properties or {},
            session_id=session_id,
        )

        self.store.add_event(event)
        return event


# ============================================================
# 4. Sessionization
# ============================================================

class Sessionizer:

    def __init__(self, inactivity_minutes: int = 30) -> None:
        if inactivity_minutes <= 0:
            raise ValueError("Inactivity threshold must be positive.")

        self.timeout = timedelta(minutes=inactivity_minutes)

    def build_sessions(
        self,
        events: Iterable[Event],
    ) -> list[Session]:

        grouped: dict[str, list[Event]] = defaultdict(list)

        for event in events:
            grouped[event.user_id].append(event)

        sessions: list[Session] = []

        for user_id, user_events in grouped.items():
            ordered = sorted(
                user_events,
                key=lambda event: (event.timestamp, event.event_id),
            )

            current: Session | None = None

            for event in ordered:
                new_session = (
                    current is None
                    or event.timestamp - current.last_event_at > self.timeout
                    or (
                        event.session_id is not None
                        and current.session_id != event.session_id
                    )
                )

                if new_session:
                    current = Session(
                        session_id=(
                            event.session_id or str(uuid.uuid4())
                        ),
                        user_id=user_id,
                        started_at=event.timestamp,
                        last_event_at=event.timestamp,
                    )
                    sessions.append(current)

                current.events.append(event)

                if event.timestamp > current.last_event_at:
                    current.last_event_at = event.timestamp

        return sessions


# ============================================================
# 5. Event and property analytics
# ============================================================

class EventAnalytics:

    def __init__(self, store: EventStore) -> None:
        self.store = store

    def event_counts(self) -> dict[str, int]:
        return dict(
            Counter(event.event_name for event in self.store.events)
        )

    def active_users(self) -> int:
        return len({
            event.user_id for event in self.store.events
        })

    def unique_users_per_event(self) -> dict[str, int]:
        result: dict[str, set[str]] = defaultdict(set)

        for event in self.store.events:
            result[event.event_name].add(event.user_id)

        return {
            name: len(users)
            for name, users in result.items()
        }

    def property_distribution(
        self,
        event_name: str,
        property_name: str,
    ) -> dict[str, int]:

        values = Counter(
            str(event.properties[property_name])
            for event in self.store.events
            if event.event_name == event_name
            and property_name in event.properties
        )

        return dict(values)

    def revenue(self) -> float:
        return round(
            sum(
                float(event.properties.get("amount", 0))
                for event in self.store.events
                if event.event_name == EventType.PURCHASE.value
            ),
            2,
        )

    def average_order_value(self) -> float:
        purchases = [
            float(event.properties["amount"])
            for event in self.store.events
            if event.event_name == EventType.PURCHASE.value
            and isinstance(event.properties.get("amount"), (int, float))
        ]

        if not purchases:
            return 0.0

        return round(statistics.mean(purchases), 2)


# ============================================================
# 6. Conversion funnel
# ============================================================

class FunnelAnalyzer:

    def analyze(
        self,
        events: Iterable[Event],
        steps: list[str],
        name: str = "Product Conversion",
        conversion_window_hours: int = 168,
    ) -> FunnelResult:

        if len(steps) < 2:
            raise ValidationError("A funnel requires at least two steps.")

        if len(set(steps)) != len(steps):
            raise ValidationError("Funnel steps must be unique.")

        if conversion_window_hours <= 0:
            raise ValidationError("Invalid conversion window.")

        grouped: dict[str, list[Event]] = defaultdict(list)

        for event in events:
            grouped[event.user_id].append(event)

        counts = [0] * len(steps)

        for user_events in grouped.values():
            ordered = sorted(
                user_events,
                key=lambda event: event.timestamp,
            )

            cursor = 0
            first_timestamp: datetime | None = None
            converted = 0

            for event in ordered:
                if event.event_name != steps[cursor]:
                    continue

                if first_timestamp is None:
                    first_timestamp = event.timestamp

                elif (
                    event.timestamp - first_timestamp
                    > timedelta(hours=conversion_window_hours)
                ):
                    break

                converted += 1
                counts[cursor] += 1
                cursor += 1

                if cursor == len(steps):
                    break

        rates = [
            round(counts[i] / counts[i - 1] * 100, 2)
            if i > 0 and counts[i - 1] > 0 else (
                100.0 if i == 0 and counts[i] > 0 else 0.0
            )
            for i in range(len(steps))
        ]

        overall = (
            round(counts[-1] / counts[0] * 100, 2)
            if counts[0] else 0.0
        )

        return FunnelResult(
            name=name,
            steps=steps,
            counts=counts,
            conversion_rates=rates,
            overall_conversion=overall,
        )


# ============================================================
# 7. Cohort and retention analysis
# ============================================================

class CohortAnalyzer:

    @staticmethod
    def month_difference(start: datetime, end: datetime) -> int:
        return (
            (end.year - start.year) * 12
            + end.month - start.month
        )

    def analyze(
        self,
        users: dict[str, User],
        events: Iterable[Event],
    ) -> list[CohortResult]:

        activity: dict[str, set[str]] = defaultdict(set)

        for event in events:
            month = event.timestamp.strftime("%Y-%m")
            activity[event.user_id].add(month)

        cohorts: dict[str, set[str]] = defaultdict(set)

        for user in users.values():
            cohorts[user.created_at.strftime("%Y-%m")].add(
                user.user_id
            )

        results: list[CohortResult] = []

        for cohort_month, user_ids in sorted(cohorts.items()):
            cohort_date = datetime.strptime(
                cohort_month, "%Y-%m"
            ).replace(tzinfo=timezone.utc)

            retained: dict[int, int] = defaultdict(int)

            for user_id in user_ids:
                for active_month in activity[user_id]:
                    active_date = datetime.strptime(
                        active_month, "%Y-%m"
                    ).replace(tzinfo=timezone.utc)

                    offset = self.month_difference(
                        cohort_date, active_date
                    )

                    if offset >= 0:
                        retained[offset] += 1

            retained[0] = len(user_ids)

            rates = {
                month: round(count / len(user_ids) * 100, 2)
                for month, count in retained.items()
            }

            results.append(
                CohortResult(
                    cohort_month=cohort_month,
                    users=len(user_ids),
                    retained_by_month=dict(sorted(retained.items())),
                    retention_rates=dict(sorted(rates.items())),
                )
            )

        return results


# ============================================================
# 8. Persistence
# ============================================================

class JsonlRepository:

    @staticmethod
    def save(events: Iterable[Event], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        temporary = path.with_suffix(path.suffix + ".tmp")

        try:
            with temporary.open("w", encoding="utf-8") as file:
                for event in events:
                    record = {
                        **asdict(event),
                        "timestamp": event.timestamp.isoformat(),
                    }
                    file.write(json.dumps(record) + "\n")

            temporary.replace(path)

        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    @staticmethod
    def load(path: Path) -> list[dict[str, Any]]:
        records = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValidationError(
                        f"Invalid JSON on line {line_number}"
                    ) from exc

        return records


# ============================================================
# 9. Reporting
# ============================================================

class AnalyticsReport:

    @staticmethod
    def print_report(
        event_analytics: EventAnalytics,
        sessions: list[Session],
        funnel: FunnelResult,
        cohorts: list[CohortResult],
    ) -> None:

        print("\n" + "=" * 65)
        print("PRODUCT ANALYTICS REPORT")
        print("=" * 65)

        print("\nEVENT COUNTS")

        for name, count in sorted(
            event_analytics.event_counts().items()
        ):
            print(f"{name:25} {count}")

        print("\nUSER METRICS")
        print("Active users:", event_analytics.active_users())
        print("Revenue:", event_analytics.revenue())
        print(
            "Average order value:",
            event_analytics.average_order_value(),
        )

        print("\nSESSION METRICS")
        print("Total sessions:", len(sessions))

        if sessions:
            average_duration = statistics.mean(
                session.duration_seconds for session in sessions
            )
            print("Average duration:", round(average_duration, 2))

        print("\nFUNNEL:", funnel.name)

        for step, count, rate in zip(
            funnel.steps,
            funnel.counts,
            funnel.conversion_rates,
        ):
            print(f"{step:25} users={count:3} rate={rate:6.2f}%")

        print(
            "Overall conversion:",
            f"{funnel.overall_conversion:.2f}%",
        )

        print("\nCOHORT RETENTION")

        for cohort in cohorts:
            print(
                cohort.cohort_month,
                "users=", cohort.users,
                "retention=", cohort.retention_rates,
            )


# ============================================================
# 10. Demonstration and verification
# ============================================================

def create_demo_data() -> EventStore:
    store = EventStore()

    base = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)

    demo_users = [
        User("U001", country="IN", plan="free", created_at=base),
        User(
            "U002",
            country="IN",
            plan="premium",
            created_at=base + timedelta(hours=2),
        ),
        User(
            "U003",
            country="US",
            plan="free",
            created_at=base + timedelta(days=1),
        ),
        User(
            "U004",
            country="IN",
            plan="premium",
            created_at=base + timedelta(days=30),
        ),
        User(
            "U005",
            country="GB",
            plan="free",
            created_at=base + timedelta(days=31),
        ),
    ]

    for user in demo_users:
        store.register_user(user)

    tracker = AnalyticsTracker(store)

    journeys = {
        "U001": [
            ("signup", 0, {}),
            ("login", 1, {}),
            ("product_view", 5, {"product_id": "P100"}),
            ("add_to_cart", 10, {"product_id": "P100"}),
            ("checkout_started", 15, {}),
            ("purchase", 20, {"amount": 1499.0, "currency": "INR"}),
            ("page_view", 31 * 24 * 60, {"page": "/dashboard"}),
        ],
        "U002": [
            ("signup", 0, {}),
            ("login", 1, {}),
            ("product_view", 3, {"product_id": "P200"}),
            ("add_to_cart", 5, {"product_id": "P200"}),
            ("checkout_started", 8, {}),
            ("purchase", 12, {"amount": 2499.0, "currency": "INR"}),
            ("page_view", 32 * 24 * 60, {"page": "/pricing"}),
        ],
        "U003": [
            ("signup", 0, {}),
            ("login", 2, {}),
            ("product_view", 4, {"product_id": "P100"}),
            ("add_to_cart", 6, {"product_id": "P100"}),
            ("page_view", 31 * 24 * 60, {"page": "/products"}),
        ],
        "U004": [
            ("signup", 0, {}),
            ("login", 1, {}),
            ("product_view", 3, {"product_id": "P300"}),
            ("page_view", 31 * 24 * 60, {"page": "/dashboard"}),
        ],
        "U005": [
            ("signup", 0, {}),
            ("login", 1, {}),
            ("product_view", 2, {"product_id": "P100"}),
            ("add_to_cart", 4, {"product_id": "P100"}),
            ("checkout_started", 6, {}),
            ("purchase", 9, {"amount": 799.0, "currency": "GBP"}),
        ],
    }

    for user_id, journey in journeys.items():
        user = store.users[user_id]

        for index, (name, offset, properties) in enumerate(journey):
            timestamp = user.created_at + timedelta(minutes=offset)

            tracker.track(
                user_id=user_id,
                event_name=name,
                properties=properties,
                timestamp=timestamp,
                session_id=f"{user_id}-SESSION-1",
                event_id=f"{user_id}-EVENT-{index + 1}",
            )

    return store


def run_tests() -> None:
    store = create_demo_data()

    assert len(store.events) == 30
    assert len(store.users) == 5

    analytics = EventAnalytics(store)

    assert analytics.active_users() == 5
    assert analytics.revenue() == 4797.0

    sessions = Sessionizer().build_sessions(store.events)
    assert len(sessions) >= 5

    funnel = FunnelAnalyzer().analyze(
        store.events,
        [
            "signup",
            "product_view",
            "add_to_cart",
            "checkout_started",
            "purchase",
        ],
    )

    assert funnel.counts[0] == 5
    assert funnel.counts[-1] == 3

    cohorts = CohortAnalyzer().analyze(
        store.users,
        store.events,
    )

    assert len(cohorts) >= 2

    try:
        AnalyticsTracker(store).track(
            "UNKNOWN",
            "page_view",
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Unknown user was accepted.")

    try:
        store.add_event(store.events[0])
    except DuplicateEventError:
        pass
    else:
        raise AssertionError("Duplicate event was accepted.")

    logger.info("All analytics validation tests passed.")

    return store, sessions, funnel, cohorts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Product Analytics Engine"
    )

    parser.add_argument(
        "--output",
        default="product_analytics_events.jsonl",
        help="JSONL output path",
    )

    args = parser.parse_args()

    store, sessions, funnel, cohorts = run_tests()

    analytics = EventAnalytics(store)

    AnalyticsReport.print_report(
        analytics,
        sessions,
        funnel,
        cohorts,
    )

    JsonlRepository.save(
        store.events,
        Path(args.output),
    )

    print("\nPersisted events:", args.output)
    print("Total persisted records:", len(store.events))


if __name__ == "__main__":
    main()
