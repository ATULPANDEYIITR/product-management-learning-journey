from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, date
from enum import Enum
from statistics import mean
from typing import Iterable
import json


class EventType(str, Enum):
    LOGIN = "login"
    PAGE_VIEW = "page_view"
    ACTION = "action"
    PURCHASE = "purchase"
    LOGOUT = "logout"


class MetricError(Exception):
    pass


@dataclass(frozen=True)
class EngagementEvent:
    event_id: str
    user_id: str
    event_type: EventType
    timestamp: datetime
    properties: dict | None = None

    def __post_init__(self):
        if not self.event_id or not self.user_id:
            raise ValueError("Event ID and user ID are required.")
        if self.timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")
        if self.timestamp > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("Future event timestamp is invalid.")


@dataclass
class Session:
    user_id: str
    started_at: datetime
    last_event_at: datetime
    event_count: int = 1

    @property
    def duration_seconds(self) -> float:
        return max(0.0, (self.last_event_at - self.started_at).total_seconds())


@dataclass
class EngagementReport:
    report_date: date
    dau: int
    wau: int
    mau: int
    stickiness: float
    events: int
    total_sessions: int
    average_sessions_per_user: float
    average_session_duration: float
    average_events_per_session: float
    sessions_per_user: dict[str, int]


class EngagementAnalytics:
    """
    Engagement measurement engine.

    Active user definition:
    A user is active when at least one qualifying event occurs.

    DAU: distinct active users in one calendar day.
    WAU: distinct active users in seven calendar days.
    MAU: distinct active users in thirty calendar days.
    Stickiness: DAU / MAU * 100.

    Sessions are separated by an inactivity timeout.
    """

    QUALIFYING_EVENTS = {
        EventType.LOGIN,
        EventType.PAGE_VIEW,
        EventType.ACTION,
        EventType.PURCHASE,
    }

    def __init__(self, session_timeout_minutes: int = 30):
        if not 1 <= session_timeout_minutes <= 1440:
            raise ValueError("Session timeout must be between 1 and 1440 minutes.")

        self.timeout = timedelta(minutes=session_timeout_minutes)
        self.events: list[EngagementEvent] = []
        self.event_ids: set[str] = set()

    def ingest(self, event: EngagementEvent) -> bool:
        """Accept an event once. Duplicate event IDs are ignored."""
        if event.event_id in self.event_ids:
            return False

        self.event_ids.add(event.event_id)
        self.events.append(event)
        return True

    def ingest_many(self, events: Iterable[EngagementEvent]) -> int:
        accepted = 0

        for event in events:
            if self.ingest(event):
                accepted += 1

        return accepted

    def _events_until(self, end: datetime) -> list[EngagementEvent]:
        return sorted(
            (
                event for event in self.events
                if event.timestamp <= end
            ),
            key=lambda event: (event.timestamp, event.event_id)
        )

    def active_users(self, start: datetime, end: datetime) -> set[str]:
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("Date boundaries must be timezone-aware.")

        if start > end:
            raise ValueError("Start must not exceed end.")

        return {
            event.user_id
            for event in self.events
            if start <= event.timestamp <= end
            and event.event_type in self.QUALIFYING_EVENTS
        }

    def sessionize(self, events: Iterable[EngagementEvent]) -> list[Session]:
        """
        Build sessions independently for each user.

        An event starts a new session if its gap from the preceding
        qualifying event exceeds the configured inactivity timeout.
        """
        grouped = defaultdict(list)

        for event in events:
            if event.event_type in self.QUALIFYING_EVENTS:
                grouped[event.user_id].append(event)

        sessions = []

        for user_id, user_events in grouped.items():
            user_events.sort(key=lambda e: (e.timestamp, e.event_id))
            current = None

            for event in user_events:
                if (
                    current is None
                    or event.timestamp - current.last_event_at > self.timeout
                ):
                    if current is not None:
                        sessions.append(current)

                    current = Session(
                        user_id=user_id,
                        started_at=event.timestamp,
                        last_event_at=event.timestamp,
                    )
                else:
                    current.last_event_at = event.timestamp
                    current.event_count += 1

            if current is not None:
                sessions.append(current)

        return sorted(
            sessions,
            key=lambda session: (session.started_at, session.user_id)
        )

    def calculate(self, report_date: date) -> EngagementReport:
        """
        Calculate metrics using UTC calendar boundaries.

        The seven-day and thirty-day windows include the report date.
        """
        end = datetime.combine(
            report_date,
            datetime.max.time(),
            tzinfo=timezone.utc
        )

        start_day = datetime.combine(
            report_date,
            datetime.min.time(),
            tzinfo=timezone.utc
        )

        dau_users = self.active_users(start_day, end)

        wau_users = self.active_users(
            start_day - timedelta(days=6),
            end
        )

        mau_users = self.active_users(
            start_day - timedelta(days=29),
            end
        )

        dau = len(dau_users)
        wau = len(wau_users)
        mau = len(mau_users)

        stickiness = round(dau / mau * 100, 2) if mau else 0.0

        qualifying_events = [
            event for event in self._events_until(end)
            if event.event_type in self.QUALIFYING_EVENTS
        ]

        sessions = self.sessionize(qualifying_events)

        sessions_by_user = defaultdict(int)

        for session in sessions:
            sessions_by_user[session.user_id] += 1

        durations = [session.duration_seconds for session in sessions]

        return EngagementReport(
            report_date=report_date,
            dau=dau,
            wau=wau,
            mau=mau,
            stickiness=stickiness,
            events=len(qualifying_events),
            total_sessions=len(sessions),
            average_sessions_per_user=(
                len(sessions) / len(sessions_by_user)
                if sessions_by_user else 0.0
            ),
            average_session_duration=(
                mean(durations) if durations else 0.0
            ),
            average_events_per_session=(
                sum(s.event_count for s in sessions) / len(sessions)
                if sessions else 0.0
            ),
            sessions_per_user=dict(sessions_by_user),
        )

    def daily_trend(self, start: date, end: date) -> list[dict]:
        if start > end:
            raise ValueError("Invalid reporting range.")

        results = []
        current = start

        while current <= end:
            report = self.calculate(current)

            results.append({
                "date": current.isoformat(),
                "dau": report.dau,
                "wau": report.wau,
                "mau": report.mau,
                "stickiness": report.stickiness,
                "sessions": report.total_sessions,
            })

            current += timedelta(days=1)

        return results

    def frequency_distribution(self, report_date: date) -> dict:
        """Count sessions per user for the selected calendar day."""
        start = datetime.combine(
            report_date, datetime.min.time(), tzinfo=timezone.utc
        )
        end = datetime.combine(
            report_date, datetime.max.time(), tzinfo=timezone.utc
        )

        daily_events = [
            event for event in self.events
            if start <= event.timestamp <= end
        ]

        sessions = self.sessionize(daily_events)
        distribution = defaultdict(int)

        user_counts = defaultdict(int)

        for session in sessions:
            user_counts[session.user_id] += 1

        for count in user_counts.values():
            distribution[count] += 1

        return dict(sorted(distribution.items()))


def make_event(event_id, user_id, event_type, timestamp):
    return EngagementEvent(
        event_id=event_id,
        user_id=user_id,
        event_type=EventType(event_type),
        timestamp=datetime.fromisoformat(timestamp).replace(
            tzinfo=timezone.utc
        ),
    )


def demonstrate():
    analytics = EngagementAnalytics(session_timeout_minutes=30)

    sample_events = [
        make_event("e1", "user_001", "login", "2026-11-19T09:00:00"),
        make_event("e2", "user_001", "page_view", "2026-11-19T09:05:00"),
        make_event("e3", "user_001", "action", "2026-11-19T09:15:00"),
        make_event("e4", "user_001", "login", "2026-11-19T11:00:00"),
        make_event("e5", "user_002", "login", "2026-11-19T10:00:00"),
        make_event("e6", "user_002", "purchase", "2026-11-19T10:10:00"),
        make_event("e7", "user_003", "page_view", "2026-11-18T12:00:00"),
        make_event("e8", "user_003", "action", "2026-11-17T12:00:00"),
        make_event("e9", "user_004", "login", "2026-11-01T08:00:00"),
        make_event("e10", "user_005", "logout", "2026-11-19T12:00:00"),
    ]

    accepted = analytics.ingest_many(sample_events)

    # Duplicate delivery does not increase engagement counts.
    duplicate_accepted = analytics.ingest(sample_events[0])

    report = analytics.calculate(date(2026, 11, 19))

    print("ACCEPTED EVENTS:", accepted)
    print("DUPLICATE ACCEPTED:", duplicate_accepted)
    print("\nENGAGEMENT REPORT")
    print(json.dumps({
        "date": report.report_date.isoformat(),
        "DAU": report.dau,
        "WAU": report.wau,
        "MAU": report.mau,
        "stickiness_percent": report.stickiness,
        "events": report.events,
        "sessions": report.total_sessions,
        "average_sessions_per_user": round(
            report.average_sessions_per_user, 2
        ),
        "average_session_duration_seconds": round(
            report.average_session_duration, 2
        ),
        "average_events_per_session": round(
            report.average_events_per_session, 2
        ),
    }, indent=4))

    print("\nDAILY TREND")
    print(json.dumps(
        analytics.daily_trend(
            date(2026, 11, 17),
            date(2026, 11, 19)
        ),
        indent=4
    ))

    print("\nSESSION FREQUENCY DISTRIBUTION")
    print(analytics.frequency_distribution(date(2026, 11, 19)))

    # Verify important metric properties.
    assert report.dau == 2
    assert report.wau == 3
    assert report.mau == 4
    assert report.stickiness == 50.0
    assert accepted == 10
    assert duplicate_accepted is False

    # Empty-data edge case.
    empty = EngagementAnalytics()
    empty_report = empty.calculate(date(2026, 11, 19))

    assert empty_report.dau == 0
    assert empty_report.mau == 0
    assert empty_report.stickiness == 0.0

    print("\nAll validation assertions passed.")


if __name__ == "__main__":
    try:
        demonstrate()
    except (ValueError, MetricError) as error:
        print(f"Analytics error: {error}")
        raise
