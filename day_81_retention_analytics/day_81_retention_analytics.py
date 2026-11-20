from __future__ import annotations

import argparse
import csv
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable
from statistics import mean
from enum import Enum


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("retention_analytics")


class EventType(str, Enum):
    SIGNUP = "signup"
    ACTIVE = "active"
    PURCHASE = "purchase"
    LOGIN = "login"


@dataclass(frozen=True)
class UserEvent:
    user_id: str
    event_date: date
    event_type: EventType


@dataclass
class UserMetrics:
    user_id: str
    signup_date: date
    last_active: date
    churned: bool = False
    resurrected: bool = False


class RetentionError(Exception):
    pass


class RetentionAnalytics:
    """
    Calculates cohort retention, retention curves, churn,
    and resurrection using distinct user activity dates.

    Retention is measured using exact elapsed-day intervals.
    Churn is determined using an inactivity threshold.
    """

    def __init__(self, churn_days: int = 30):
        if churn_days < 1:
            raise ValueError("churn_days must be positive")

        self.churn_days = churn_days
        self.events: list[UserEvent] = []
        self.users: dict[str, UserMetrics] = {}
        self.activities: dict[str, set[date]] = defaultdict(set)

    def add_event(self, event: UserEvent) -> None:
        if not event.user_id or not event.user_id.strip():
            raise ValueError("User ID cannot be empty")

        self.events.append(event)

    def load_events(self, events: Iterable[UserEvent]) -> None:
        for event in events:
            self.add_event(event)

    def load_csv(self, filename: str) -> None:
        required = {"user_id", "event_date", "event_type"}

        with open(filename, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise RetentionError(
                    f"CSV must contain columns: {sorted(required)}"
                )

            for row in reader:
                try:
                    self.add_event(
                        UserEvent(
                            user_id=row["user_id"].strip(),
                            event_date=date.fromisoformat(row["event_date"]),
                            event_type=EventType(row["event_type"].lower())
                        )
                    )
                except (ValueError, KeyError) as exc:
                    raise RetentionError(
                        f"Invalid event row: {row}"
                    ) from exc

    def process(self) -> None:
        self.users.clear()
        self.activities.clear()

        # Deduplicate events by user and activity date.
        unique_events = {
            (event.user_id, event.event_date, event.event_type)
            for event in self.events
        }

        grouped = defaultdict(list)

        for user_id, event_date, event_type in unique_events:
            grouped[user_id].append((event_date, event_type))

        for user_id, user_events in grouped.items():
            user_events.sort(key=lambda item: item[0])

            signup_dates = [
                event_date
                for event_date, event_type in user_events
                if event_type == EventType.SIGNUP
            ]

            if not signup_dates:
                raise RetentionError(
                    f"User {user_id} has no signup event"
                )

            signup = min(signup_dates)

            active_dates = {
                event_date
                for event_date, event_type in user_events
                if event_type in {
                    EventType.ACTIVE,
                    EventType.LOGIN,
                    EventType.PURCHASE
                }
                and event_date >= signup
            }

            # Signup establishes the cohort but does not automatically
            # count as product activity.
            self.activities[user_id] = active_dates

            if active_dates:
                last_active = max(active_dates)
            else:
                last_active = signup

            self.users[user_id] = UserMetrics(
                user_id=user_id,
                signup_date=signup,
                last_active=last_active
            )

        logger.info(
            "Processed %d users and %d unique events",
            len(self.users),
            len(unique_events)
        )

    def _validate_processed(self) -> None:
        if not self.users:
            raise RetentionError(
                "No processed users. Call process() first."
            )

    def retention_curve(
        self,
        observation_date: date,
        intervals: tuple[int, ...] = (0, 1, 7, 14, 30)
    ) -> dict[int, dict[str, float | int]]:
        self._validate_processed()

        if not intervals or any(day < 0 for day in intervals):
            raise ValueError("Intervals must be nonnegative")

        if observation_date < min(
            user.signup_date for user in self.users.values()
        ):
            raise ValueError("Observation date precedes signup data")

        results = {}

        for interval in sorted(set(intervals)):
            eligible = [
                user for user in self.users.values()
                if user.signup_date + timedelta(days=interval)
                <= observation_date
            ]

            retained = sum(
                user.user_id in self.activities
                and user.signup_date + timedelta(days=interval)
                in self.activities[user.user_id]
                for user in eligible
            )

            denominator = len(eligible)

            results[interval] = {
                "eligible_users": denominator,
                "retained_users": retained,
                "retention_rate": (
                    round(retained / denominator * 100, 2)
                    if denominator else 0.0
                )
            }

        return results

    def cohort_retention(
        self,
        observation_date: date,
        max_age_days: int = 30
    ) -> dict[str, dict[int, float]]:
        self._validate_processed()

        if max_age_days < 0:
            raise ValueError("max_age_days cannot be negative")

        cohorts = defaultdict(list)

        for user in self.users.values():
            cohort = user.signup_date.strftime("%Y-%m")
            cohorts[cohort].append(user)

        report = {}

        for cohort, members in sorted(cohorts.items()):
            cohort_start = min(user.signup_date for user in members)

            daily_retention = {}

            for day in range(max_age_days + 1):
                eligible = [
                    user for user in members
                    if user.signup_date + timedelta(days=day)
                    <= observation_date
                ]

                if not eligible:
                    continue

                retained = sum(
                    user.signup_date + timedelta(days=day)
                    in self.activities[user.user_id]
                    for user in eligible
                )

                daily_retention[day] = round(
                    retained / len(eligible) * 100, 2
                )

            report[cohort] = daily_retention

        return report

    def churn_analysis(
        self,
        observation_date: date
    ) -> dict[str, object]:
        self._validate_processed()

        if any(
            observation_date < user.signup_date
            for user in self.users.values()
        ):
            raise ValueError("Observation date precedes a signup")

        churned = []
        active = []
        not_yet_eligible = []

        for user in self.users.values():
            if user.signup_date + timedelta(days=self.churn_days) > observation_date:
                not_yet_eligible.append(user.user_id)
                continue

            inactive_days = (
                observation_date - user.last_active
            ).days

            if inactive_days >= self.churn_days:
                churned.append(user.user_id)
                user.churned = True
            else:
                active.append(user.user_id)
                user.churned = False

        eligible_count = len(churned) + len(active)

        return {
            "observation_date": observation_date.isoformat(),
            "churn_threshold_days": self.churn_days,
            "eligible_users": eligible_count,
            "churned_users": len(churned),
            "active_users": len(active),
            "not_yet_eligible": len(not_yet_eligible),
            "churn_rate": round(
                len(churned) / eligible_count * 100, 2
            ) if eligible_count else 0.0,
            "churned_user_ids": sorted(churned),
            "active_user_ids": sorted(active)
        }

    def resurrection_analysis(
        self,
        observation_date: date
    ) -> dict[str, object]:
        self._validate_processed()

        resurrected_users = []
        resurrection_events = []

        for user_id, activity_dates in self.activities.items():
            ordered = sorted(activity_dates)

            if len(ordered) < 2:
                continue

            for previous, current in zip(ordered, ordered[1:]):
                inactive_days = (current - previous).days

                if inactive_days >= self.churn_days:
                    if current <= observation_date:
                        resurrected_users.append(user_id)
                        resurrection_events.append({
                            "user_id": user_id,
                            "last_activity_before_gap": previous.isoformat(),
                            "resurrection_date": current.isoformat(),
                            "inactive_days": inactive_days
                        })

            if any(
                event["user_id"] == user_id
                for event in resurrection_events
            ):
                self.users[user_id].resurrected = True

        return {
            "resurrected_users": len(set(resurrected_users)),
            "resurrection_events": len(resurrection_events),
            "resurrection_user_ids": sorted(set(resurrected_users)),
            "events": resurrection_events
        }

    def retention_summary(self, observation_date: date) -> dict:
        curve = self.retention_curve(observation_date)
        churn = self.churn_analysis(observation_date)
        resurrection = self.resurrection_analysis(observation_date)

        return {
            "total_users": len(self.users),
            "observation_date": observation_date.isoformat(),
            "retention_curve": curve,
            "churn": churn,
            "resurrection": resurrection
        }

    def export_json(self, filename: str, observation_date: date) -> None:
        report = self.retention_summary(observation_date)
        target = Path(filename)

        target.parent.mkdir(parents=True, exist_ok=True)

        # Write to a temporary file before replacing the destination.
        temporary = target.with_suffix(target.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(report, indent=2),
                encoding="utf-8"
            )
            temporary.replace(target)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise


def build_sample_data() -> list[UserEvent]:
    raw = [
        ("U001", "2026-01-01", "signup"),
        ("U001", "2026-01-01", "active"),
        ("U001", "2026-01-02", "active"),
        ("U001", "2026-01-08", "active"),
        ("U001", "2026-03-05", "active"),

        ("U002", "2026-01-03", "signup"),
        ("U002", "2026-01-03", "active"),
        ("U002", "2026-01-04", "active"),

        ("U003", "2026-01-10", "signup"),
        ("U003", "2026-01-10", "active"),
        ("U003", "2026-02-15", "active"),

        ("U004", "2026-02-01", "signup"),
        ("U004", "2026-02-01", "active"),
        ("U004", "2026-02-02", "active"),
        ("U004", "2026-02-08", "active"),

        ("U005", "2026-02-05", "signup"),
        ("U005", "2026-02-05", "active"),

        ("U006", "2026-02-15", "signup"),
        ("U006", "2026-02-15", "active"),
        ("U006", "2026-03-20", "active"),

        ("U007", "2026-03-01", "signup"),
        ("U007", "2026-03-01", "active"),
        ("U007", "2026-03-02", "active"),

        ("U008", "2026-03-10", "signup"),
        ("U008", "2026-03-10", "active"),
        ("U008", "2026-04-15", "active"),

        ("U009", "2026-03-15", "signup"),
        ("U009", "2026-03-15", "active"),
    ]

    return [
        UserEvent(
            user_id=user_id,
            event_date=date.fromisoformat(event_date),
            event_type=EventType(event_type)
        )
        for user_id, event_date, event_type in raw
    ]


def run_tests() -> None:
    analytics = RetentionAnalytics(churn_days=30)
    analytics.load_events(build_sample_data())
    analytics.process()

    observation = date(2026, 5, 1)

    curve = analytics.retention_curve(observation)

    assert curve[0]["retention_rate"] == 100.0
    assert curve[0]["eligible_users"] == 9

    churn = analytics.churn_analysis(observation)
    assert churn["eligible_users"] == 9

    resurrection = analytics.resurrection_analysis(observation)
    assert resurrection["resurrected_users"] >= 1

    # Duplicate activity must not increase the retained-user count.
    analytics.add_event(
        UserEvent("U001", date(2026, 1, 2), EventType.ACTIVE)
    )
    analytics.process()

    assert len(analytics.activities["U001"]) == 4

    logger.info("All retention analytics assertions passed")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cohort retention, churn and resurrection analytics"
    )

    parser.add_argument("--csv", help="Input CSV event file")
    parser.add_argument("--date", default="2026-05-01")
    parser.add_argument("--churn-days", type=int, default=30)
    parser.add_argument("--output", default="retention_report.json")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    analytics = RetentionAnalytics(args.churn_days)

    if args.csv:
        analytics.load_csv(args.csv)
    else:
        analytics.load_events(build_sample_data())

    analytics.process()

    observation_date = date.fromisoformat(args.date)

    report = analytics.retention_summary(observation_date)

    print(json.dumps(report, indent=2))

    analytics.export_json(args.output, observation_date)

    logger.info("Report saved to %s", args.output)


if __name__ == "__main__":
    main()
