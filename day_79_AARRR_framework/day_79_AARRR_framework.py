#!/usr/bin/env python3
"""
AARRR Framework: Product Growth Analytics and Experimentation Engine

Implements:
- Acquisition
- Activation
- Retention
- Revenue
- Referral

Includes event validation, customer lifecycle tracking, cohort analysis,
conversion funnels, revenue calculations, referral attribution, experiments,
CSV reporting, and automated integrity checks.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import csv
import json
import logging
import statistics
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("aarrr")


class Stage(str, Enum):
    ACQUISITION = "acquisition"
    ACTIVATION = "activation"
    RETENTION = "retention"
    REVENUE = "revenue"
    REFERRAL = "referral"


class EventType(str, Enum):
    VISIT = "visit"
    SIGNUP = "signup"
    ACTIVATION = "activation"
    LOGIN = "login"
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"
    REFERRAL_SENT = "referral_sent"
    REFERRAL_CONVERTED = "referral_converted"
    CANCELLATION = "cancellation"


@dataclass(frozen=True)
class GrowthEvent:
    event_id: str
    user_id: str
    event_type: EventType
    timestamp: datetime
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    user_id: str
    acquisition_source: str
    signup_date: date
    activated: bool = False
    activation_date: Optional[date] = None
    referred_by: Optional[str] = None
    revenue: float = 0.0
    purchases: int = 0
    active_dates: set[date] = field(default_factory=set)
    cancelled: bool = False


@dataclass(frozen=True)
class FunnelMetrics:
    visitors: int
    signups: int
    activated: int
    retained: int
    paying: int
    referred: int

    @staticmethod
    def percentage(numerator: int, denominator: int) -> float:
        return round(numerator / denominator * 100, 2) if denominator else 0.0

    def report(self) -> dict[str, Any]:
        return {
            "acquisition_visitors": self.visitors,
            "signups": self.signups,
            "activation": self.activated,
            "retained": self.retained,
            "paying_customers": self.paying,
            "referring_customers": self.referred,
            "visitor_to_signup_pct": self.percentage(
                self.signups, self.visitors
            ),
            "signup_to_activation_pct": self.percentage(
                self.activated, self.signups
            ),
            "activation_to_retention_pct": self.percentage(
                self.retained, self.activated
            ),
            "activation_to_revenue_pct": self.percentage(
                self.paying, self.activated
            ),
            "referral_rate_pct": self.percentage(
                self.referred, self.activated
            ),
        }


class GrowthError(Exception):
    """Base exception for growth analytics."""


class ValidationError(GrowthError):
    """Invalid event or customer data."""


class DuplicateEventError(GrowthError):
    """Event has already been processed."""


class GrowthEngine:
    def __init__(self, activation_window_days: int = 7):
        if activation_window_days < 0:
            raise ValueError("Activation window cannot be negative.")

        self.users: dict[str, User] = {}
        self.events: list[GrowthEvent] = []
        self.event_ids: set[str] = set()
        self.visitors: dict[str, set[str]] = defaultdict(set)
        self.daily_active: dict[date, set[str]] = defaultdict(set)
        self.activation_window_days = activation_window_days

    @staticmethod
    def _money(value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError("Revenue must be numeric.")

        if value <= 0:
            raise ValidationError("Revenue must be positive.")

        if value > 100_000_000:
            raise ValidationError("Revenue exceeds the permitted limit.")

        return round(float(value), 2)

    def _record(self, user_id: str, event_type: EventType,
                timestamp: datetime, properties: Optional[dict] = None):
        if not user_id or len(user_id) > 100:
            raise ValidationError("Invalid user identifier.")

        if timestamp.tzinfo is None:
            raise ValidationError("Timestamp must include a timezone.")

        event_id = str(uuid4())

        event = GrowthEvent(
            event_id=event_id,
            user_id=user_id,
            event_type=event_type,
            timestamp=timestamp.astimezone(timezone.utc),
            properties=properties or {}
        )

        self.events.append(event)
        self.event_ids.add(event_id)
        return event

    def process(self, event: GrowthEvent) -> None:
        """Process an externally supplied event exactly once."""

        if event.event_id in self.event_ids:
            raise DuplicateEventError(event.event_id)

        if event.timestamp.tzinfo is None:
            raise ValidationError("Timezone-aware timestamp required.")

        if len(event.user_id) == 0 or len(event.user_id) > 100:
            raise ValidationError("Invalid user identifier.")

        user = self.users.get(event.user_id)
        event_date = event.timestamp.date()
        properties = event.properties

        if event.event_type == EventType.VISIT:
            source = properties.get("source", "direct")
            if not isinstance(source, str) or not source.strip():
                raise ValidationError("Invalid acquisition source.")
            self.visitors[source].add(event.user_id)

        elif event.event_type == EventType.SIGNUP:
            if user is not None:
                raise ValidationError("User has already registered.")

            source = properties.get("source", "direct")
            if not isinstance(source, str) or not source.strip():
                raise ValidationError("Invalid acquisition source.")

            referrer = properties.get("referred_by")

            if referrer is not None:
                if referrer == event.user_id or referrer not in self.users:
                    raise ValidationError("Invalid referral attribution.")

            self.users[event.user_id] = User(
                user_id=event.user_id,
                acquisition_source=source,
                signup_date=event_date,
                referred_by=referrer
            )

        else:
            if user is None:
                raise ValidationError("User must register before this event.")

            if event.event_type == EventType.ACTIVATION:
                if user.activated:
                    raise ValidationError("User already activated.")

                elapsed = (event_date - user.signup_date).days

                if elapsed < 0 or elapsed > self.activation_window_days:
                    raise ValidationError(
                        "Activation occurred outside the allowed window."
                    )

                user.activated = True
                user.activation_date = event_date

            elif event.event_type == EventType.LOGIN:
                user.active_dates.add(event_date)
                self.daily_active[event_date].add(user.user_id)

            elif event.event_type in (
                EventType.PURCHASE,
                EventType.SUBSCRIPTION
            ):
                amount = self._money(properties.get("amount"))

                user.revenue = round(user.revenue + amount, 2)
                user.purchases += 1

            elif event.event_type == EventType.REFERRAL_SENT:
                if not user.activated:
                    raise ValidationError(
                        "Only activated users can send referrals."
                    )

            elif event.event_type == EventType.REFERRAL_CONVERTED:
                if not user.activated:
                    raise ValidationError(
                        "Referrer must be activated."
                    )

                if not properties.get("referred_user_id"):
                    raise ValidationError("Missing referred user.")

            elif event.event_type == EventType.CANCELLATION:
                user.cancelled = True

        self.events.append(event)
        self.event_ids.add(event.event_id)

    def record(self, user_id: str, event_type: EventType,
               timestamp: datetime, properties: Optional[dict] = None):
        event = GrowthEvent(
            event_id=str(uuid4()),
            user_id=user_id,
            event_type=event_type,
            timestamp=timestamp,
            properties=properties or {}
        )
        self.process(event)
        return event

    def acquisition_report(self) -> dict[str, Any]:
        result = {}

        for source, visitors in self.visitors.items():
            signups = sum(
                1 for user in self.users.values()
                if user.acquisition_source == source
            )

            result[source] = {
                "visitors": len(visitors),
                "signups": signups,
                "conversion_pct": FunnelMetrics.percentage(
                    signups, len(visitors)
                )
            }

        return result

    def activation_report(self) -> dict[str, Any]:
        total = len(self.users)
        activated = sum(user.activated for user in self.users.values())

        return {
            "registered_users": total,
            "activated_users": activated,
            "activation_rate_pct": FunnelMetrics.percentage(
                activated, total
            )
        }

    def retention_report(self, period_days: int = 7) -> dict[str, Any]:
        """
        Measures cohort retention:
        users who logged in during the selected period after signup.
        """

        if period_days <= 0:
            raise ValueError("Period must be positive.")

        cohorts = defaultdict(list)

        for user in self.users.values():
            cohorts[user.signup_date].append(user)

        report = {}

        for cohort_date, members in sorted(cohorts.items()):
            retained = sum(
                any(
                    0 <= (active_date - user.signup_date).days <= period_days
                    for active_date in user.active_dates
                )
                for user in members
            )

            report[cohort_date.isoformat()] = {
                "cohort_size": len(members),
                "retained": retained,
                "retention_pct": FunnelMetrics.percentage(
                    retained, len(members)
                )
            }

        return report

    def revenue_report(self) -> dict[str, Any]:
        paying = [u for u in self.users.values() if u.revenue > 0]
        revenue = sum(u.revenue for u in self.users.values())

        return {
            "total_revenue": round(revenue, 2),
            "paying_customers": len(paying),
            "average_revenue_per_user": round(
                revenue / len(self.users), 2
            ) if self.users else 0,
            "average_revenue_per_paying_user": round(
                revenue / len(paying), 2
            ) if paying else 0,
            "transactions": sum(u.purchases for u in self.users.values())
        }

    def referral_report(self) -> dict[str, Any]:
        referred_users = [
            u for u in self.users.values() if u.referred_by
        ]

        referrers = defaultdict(int)

        for user in referred_users:
            referrers[user.referred_by] += 1

        return {
            "referred_signups": len(referred_users),
            "unique_referrers": len(referrers),
            "referrals_per_referrer": dict(referrers),
            "viral_coefficient": round(
                len(referred_users) / len(self.users), 3
            ) if self.users else 0
        }

    def funnel_report(self) -> FunnelMetrics:
        return FunnelMetrics(
            visitors=len(set().union(*self.visitors.values()))
            if self.visitors else 0,
            signups=len(self.users),
            activated=sum(u.activated for u in self.users.values()),
            retained=sum(bool(u.active_dates) for u in self.users.values()),
            paying=sum(u.revenue > 0 for u in self.users.values()),
            referred=sum(bool(u.referred_by) for u in self.users.values())
        )

    def experiment(self, control: list[bool],
                   treatment: list[bool]) -> dict[str, Any]:
        """Compare binary conversion outcomes."""

        if not control or not treatment:
            raise ValidationError("Both experiment groups need observations.")

        control_rate = sum(control) / len(control)
        treatment_rate = sum(treatment) / len(treatment)

        return {
            "control_conversion": round(control_rate * 100, 2),
            "treatment_conversion": round(treatment_rate * 100, 2),
            "absolute_lift_percentage_points": round(
                (treatment_rate - control_rate) * 100, 2
            ),
            "relative_lift_pct": round(
                (treatment_rate / control_rate - 1) * 100, 2
            ) if control_rate else None,
            "statistical_significance_tested": False
        }

    def export_csv(self, filepath: Path) -> None:
        """Export customer-level data without sensitive attributes."""

        fields = [
            "user_id", "acquisition_source", "signup_date",
            "activated", "activation_date", "revenue",
            "purchases", "cancelled"
        ]

        with filepath.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            for user in self.users.values():
                row = asdict(user)
                row["active_dates"] = None
                writer.writerow({
                    key: row[key] for key in fields
                })

    def report(self) -> dict[str, Any]:
        return {
            "acquisition": self.acquisition_report(),
            "activation": self.activation_report(),
            "retention": self.retention_report(),
            "revenue": self.revenue_report(),
            "referral": self.referral_report(),
            "funnel": self.funnel_report().report()
        }


def build_demo() -> GrowthEngine:
    engine = GrowthEngine(activation_window_days=7)

    base = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)

    events = [
        ("u001", EventType.VISIT, 0, {"source": "organic"}),
        ("u001", EventType.SIGNUP, 0, {"source": "organic"}),
        ("u001", EventType.ACTIVATION, 1, {}),
        ("u001", EventType.LOGIN, 3, {}),
        ("u001", EventType.PURCHASE, 4, {"amount": 49.99}),
        ("u002", EventType.VISIT, 0, {"source": "paid"}),
        ("u002", EventType.SIGNUP, 0, {"source": "paid"}),
        ("u002", EventType.ACTIVATION, 2, {}),
        ("u002", EventType.LOGIN, 5, {}),
        ("u002", EventType.SUBSCRIPTION, 6, {"amount": 99.00}),
        ("u003", EventType.VISIT, 1, {"source": "organic"}),
        ("u003", EventType.SIGNUP, 1, {
            "source": "organic", "referred_by": "u001"
        }),
        ("u003", EventType.ACTIVATION, 2, {}),
        ("u003", EventType.LOGIN, 4, {}),
        ("u004", EventType.VISIT, 2, {"source": "social"}),
        ("u004", EventType.SIGNUP, 2, {"source": "social"}),
        ("u004", EventType.ACTIVATION, 3, {}),
        ("u004", EventType.PURCHASE, 5, {"amount": 29.00}),
        ("u005", EventType.VISIT, 3, {"source": "paid"}),
        ("u005", EventType.SIGNUP, 3, {"source": "paid"}),
    ]

    for user_id, event_type, offset, properties in events:
        engine.record(
            user_id,
            event_type,
            base + timedelta(days=offset),
            properties
        )

    return engine


def run_tests(engine: GrowthEngine) -> None:
    assert len(engine.users) == 5
    assert engine.activation_report()["activated_users"] == 4
    assert engine.revenue_report()["total_revenue"] == 177.99
    assert engine.referral_report()["referred_signups"] == 1

    try:
        engine.record(
            "u001", EventType.SIGNUP,
            datetime.now(timezone.utc)
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Duplicate registration was accepted.")

    try:
        engine.record(
            "unknown", EventType.PURCHASE,
            datetime.now(timezone.utc),
            {"amount": 10}
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Unregistered purchase was accepted.")

    logger.info("All integrity tests passed.")


def main() -> None:
    engine = build_demo()
    run_tests(engine)

    print("\nAARRR PRODUCT GROWTH REPORT")
    print("=" * 55)

    print(json.dumps(engine.report(), indent=2, default=str))

    print("\nACQUISITION CHANNEL PERFORMANCE")
    print(json.dumps(engine.acquisition_report(), indent=2))

    print("\nEXPERIMENT COMPARISON")
    print(json.dumps(
        engine.experiment(
            [False, True, False, False, True, False, True, False],
            [True, True, False, True, True, False, True, True]
        ),
        indent=2
    ))

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "growth_users.csv"
        engine.export_csv(output)
        assert output.exists()
        print("\nCustomer report exported successfully.")


if __name__ == "__main__":
    main()
