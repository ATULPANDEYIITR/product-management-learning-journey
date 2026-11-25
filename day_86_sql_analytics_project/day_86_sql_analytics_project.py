#!/usr/bin/env python3
"""
Product SQL Analytics Project
Product dataset analysis, conversion funnel, retention, and customer segmentation.

Python 3.10+
Standard-library implementation.
"""

from __future__ import annotations

import csv
import json
import logging
import statistics
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)
logger = logging.getLogger("product_analytics")

OUTPUT_DIR = Path("analytics_output")


class EventType(str, Enum):
    VIEW = "view"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT = "checkout"
    PURCHASE = "purchase"
    REFUND = "refund"


@dataclass(frozen=True)
class Product:
    product_id: int
    name: str
    category: str
    price: float
    cost: float
    active: bool = True

    def __post_init__(self):
        if self.product_id <= 0:
            raise ValueError("Product ID must be positive")
        if not self.name.strip() or not self.category.strip():
            raise ValueError("Product name and category are required")
        if self.price < 0 or self.cost < 0:
            raise ValueError("Price and cost cannot be negative")
        if self.cost > self.price and self.price > 0:
            logger.warning("Product %s has negative unit margin", self.name)


@dataclass(frozen=True)
class Customer:
    customer_id: int
    registration_date: date
    acquisition_channel: str
    region: str

    def __post_init__(self):
        if self.customer_id <= 0:
            raise ValueError("Customer ID must be positive")


@dataclass(frozen=True)
class Event:
    event_id: int
    customer_id: int
    product_id: int
    event_type: EventType
    timestamp: datetime
    quantity: int = 1
    amount: float = 0.0
    session_id: str = ""

    def __post_init__(self):
        if self.event_id <= 0:
            raise ValueError("Event ID must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.timestamp.tzinfo is None:
            raise ValueError("Event timestamp must include timezone")


@dataclass
class FunnelResult:
    stage: str
    users: int
    conversion_from_previous: Optional[float]
    conversion_from_first: Optional[float]


class AnalyticsEngine:
    """
    Analytics engine using indexed dictionaries and sets.

    Time complexity:
    - Event ingestion: O(1) average per event.
    - Product aggregation: O(E).
    - Funnel aggregation: O(E).
    - Retention: O(E).
    - Segmentation: O(C log C) for sorted output.
    """

    FUNNEL_STAGES = (
        EventType.VIEW,
        EventType.ADD_TO_CART,
        EventType.CHECKOUT,
        EventType.PURCHASE,
    )

    def __init__(
        self,
        products: Iterable[Product],
        customers: Iterable[Customer],
        events: Iterable[Event],
    ):
        self.products = {p.product_id: p for p in products}
        self.customers = {c.customer_id: c for c in customers}
        self.events: list[Event] = []
        self.event_ids: set[int] = set()
        self.events_by_customer = defaultdict(list)
        self.events_by_product = defaultdict(list)

        for event in events:
            self.add_event(event)

    def add_event(self, event: Event) -> None:
        if event.event_id in self.event_ids:
            raise ValueError(f"Duplicate event ID: {event.event_id}")

        if event.customer_id not in self.customers:
            raise ValueError("Unknown customer")

        if event.product_id not in self.products:
            raise ValueError("Unknown product")

        if event.timestamp.date() < self.customers[
            event.customer_id
        ].registration_date:
            raise ValueError("Event predates customer registration")

        if event.event_type != EventType.PURCHASE and event.amount != 0:
            raise ValueError("Only purchase events may contain transaction amounts")

        self.event_ids.add(event.event_id)
        self.events.append(event)
        self.events_by_customer[event.customer_id].append(event)
        self.events_by_product[event.product_id].append(event)

    def events_in_period(
        self,
        start: date,
        end: date,
    ) -> list[Event]:
        if start > end:
            raise ValueError("Start date cannot exceed end date")

        return [
            e for e in self.events
            if start <= e.timestamp.date() <= end
        ]

    def product_performance(
        self,
        start: date,
        end: date,
    ) -> list[dict]:
        """Calculate product engagement, revenue, and margins."""

        selected = self.events_in_period(start, end)
        metrics = defaultdict(
            lambda: {
                "views": 0,
                "cart_events": 0,
                "purchases": 0,
                "units_sold": 0,
                "revenue": 0.0,
                "buyers": set(),
            }
        )

        for event in selected:
            row = metrics[event.product_id]

            if event.event_type == EventType.VIEW:
                row["views"] += 1
            elif event.event_type == EventType.ADD_TO_CART:
                row["cart_events"] += 1
            elif event.event_type == EventType.PURCHASE:
                row["purchases"] += 1
                row["units_sold"] += event.quantity
                row["revenue"] += event.amount
                row["buyers"].add(event.customer_id)
            elif event.event_type == EventType.REFUND:
                row["revenue"] -= event.amount

        results = []

        for product_id, row in metrics.items():
            product = self.products[product_id]
            revenue = row["revenue"]
            cost = row["units_sold"] * product.cost

            results.append({
                "product": product.name,
                "category": product.category,
                "views": row["views"],
                "cart_events": row["cart_events"],
                "purchases": row["purchases"],
                "units_sold": row["units_sold"],
                "unique_buyers": len(row["buyers"]),
                "revenue": round(revenue, 2),
                "estimated_cost": round(cost, 2),
                "estimated_margin": round(revenue - cost, 2),
                "view_to_purchase_rate": round(
                    row["purchases"] / row["views"] * 100, 2
                ) if row["views"] else 0.0,
            })

        return sorted(
            results,
            key=lambda x: x["revenue"],
            reverse=True
        )

    def conversion_funnel(
        self,
        start: date,
        end: date,
    ) -> list[FunnelResult]:
        """
        Calculate a user-level funnel.

        Each customer is counted once per stage.
        This is a stage-presence funnel, not a session-sequenced funnel.
        """

        selected = self.events_in_period(start, end)
        stage_users = defaultdict(set)

        for event in selected:
            if event.event_type in self.FUNNEL_STAGES:
                stage_users[event.event_type].add(event.customer_id)

        results = []
        previous_users = None
        first_users = len(stage_users[EventType.VIEW])

        for stage in self.FUNNEL_STAGES:
            current = len(stage_users[stage])

            previous_rate = (
                round(current / previous_users * 100, 2)
                if previous_users else None
            )

            first_rate = (
                round(current / first_users * 100, 2)
                if first_users else None
            )

            results.append(FunnelResult(
                stage=stage.value,
                users=current,
                conversion_from_previous=previous_rate,
                conversion_from_first=first_rate,
            ))

            previous_users = current

        return results

    def session_funnel(
        self,
        start: date,
        end: date,
    ) -> dict:
        """
        Calculate ordered conversion by session.

        A session qualifies for a stage only when it contains all
        preceding stages in chronological order.
        """

        selected = self.events_in_period(start, end)
        sessions = defaultdict(list)

        for event in selected:
            if event.session_id:
                sessions[event.session_id].append(event)

        stage_counts = Counter()
        valid_sessions = 0

        for session_events in sessions.values():
            ordered = sorted(session_events, key=lambda e: e.timestamp)
            expected = list(self.FUNNEL_STAGES)
            current_index = 0

            for event in ordered:
                if current_index < len(expected):
                    if event.event_type == expected[current_index]:
                        current_index += 1

            if any(e.event_type == EventType.VIEW for e in ordered):
                valid_sessions += 1

            for index, stage in enumerate(expected):
                if current_index > index:
                    stage_counts[stage.value] += 1

        return {
            "sessions_with_views": valid_sessions,
            "stage_counts": dict(stage_counts),
            "sessions_without_session_id": sum(
                1 for e in selected if not e.session_id
            ),
        }

    def retention_analysis(
        self,
        start: date,
        end: date,
    ) -> list[dict]:
        """
        Cohort retention by customer registration month.

        Activity is defined as any recorded event.
        Refunds and passive events also count as activity in this model.
        """

        if start > end:
            raise ValueError("Invalid analysis period")

        cohorts = defaultdict(set)
        activity = defaultdict(set)

        for customer in self.customers.values():
            if start <= customer.registration_date <= end:
                cohort_month = customer.registration_date.strftime("%Y-%m")
                cohorts[cohort_month].add(customer.customer_id)

        for event in self.events:
            if start <= event.timestamp.date() <= end:
                activity[event.timestamp.date().replace(day=1)].add(
                    event.customer_id
                )

        results = []

        for cohort_month, members in sorted(cohorts.items()):
            cohort_start = date.fromisoformat(cohort_month + "-01")

            max_month = (
                end.year - cohort_start.year
            ) * 12 + end.month - cohort_start.month

            for month_number in range(max_month + 1):
                month_start = (
                    cohort_start.replace(day=1)
                    + timedelta(days=month_number * 31)
                ).replace(day=1)

                active = len(members & activity.get(month_start, set()))

                results.append({
                    "cohort": cohort_month,
                    "month_number": month_number,
                    "cohort_size": len(members),
                    "active_customers": active,
                    "retention_rate": round(
                        active / len(members) * 100, 2
                    ) if members else 0.0,
                })

        return results

    def customer_segmentation(
        self,
        reference_date: date,
    ) -> list[dict]:
        """
        RFM segmentation.

        Recency: days since last purchase.
        Frequency: number of purchase transactions.
        Monetary: total purchase value minus recorded refunds.
        """

        purchase_data = defaultdict(list)

        for event in self.events:
            if event.event_type in (
                EventType.PURCHASE,
                EventType.REFUND
            ):
                purchase_data[event.customer_id].append(event)

        results = []

        for customer_id, customer in self.customers.items():
            customer_events = purchase_data[customer_id]

            purchases = [
                e for e in customer_events
                if e.event_type == EventType.PURCHASE
                and e.timestamp.date() <= reference_date
            ]

            refunds = [
                e for e in customer_events
                if e.event_type == EventType.REFUND
                and e.timestamp.date() <= reference_date
            ]

            if not purchases:
                results.append({
                    "customer_id": customer_id,
                    "segment": "No Purchase",
                    "recency_days": None,
                    "frequency": 0,
                    "monetary": 0.0,
                    "channel": customer.acquisition_channel,
                })
                continue

            last_purchase = max(e.timestamp.date() for e in purchases)
            recency = (reference_date - last_purchase).days
            frequency = len(purchases)
            monetary = (
                sum(e.amount for e in purchases)
                - sum(e.amount for e in refunds)
            )

            if recency < 0:
                raise ValueError("Reference date precedes purchase date")

            if monetary < 0:
                raise ValueError("Refunds exceed purchase value")

            if recency <= 30 and frequency >= 3 and monetary >= 5000:
                segment = "Champions"
            elif recency <= 60 and frequency >= 2:
                segment = "Loyal Customers"
            elif recency <= 30 and frequency == 1:
                segment = "Recent Customers"
            elif recency > 90 and frequency >= 2:
                segment = "At Risk"
            elif recency > 180:
                segment = "Dormant"
            else:
                segment = "Regular Customers"

            results.append({
                "customer_id": customer_id,
                "segment": segment,
                "recency_days": recency,
                "frequency": frequency,
                "monetary": round(monetary, 2),
                "channel": customer.acquisition_channel,
            })

        return results

    def channel_performance(
        self,
        start: date,
        end: date,
    ) -> list[dict]:
        selected = self.events_in_period(start, end)
        channel_metrics = defaultdict(
            lambda: {
                "visitors": set(),
                "buyers": set(),
                "revenue": 0.0,
            }
        )

        for event in selected:
            customer = self.customers[event.customer_id]
            channel = channel_metrics[customer.acquisition_channel]

            if event.event_type == EventType.VIEW:
                channel["visitors"].add(event.customer_id)

            if event.event_type == EventType.PURCHASE:
                channel["buyers"].add(event.customer_id)
                channel["revenue"] += event.amount

            if event.event_type == EventType.REFUND:
                channel["revenue"] -= event.amount

        output = []

        for name, row in channel_metrics.items():
            visitors = len(row["visitors"])
            buyers = len(row["buyers"])

            output.append({
                "channel": name,
                "visitors": visitors,
                "buyers": buyers,
                "revenue": round(row["revenue"], 2),
                "conversion_rate": round(
                    buyers / visitors * 100, 2
                ) if visitors else 0.0,
            })

        return sorted(output, key=lambda x: x["revenue"], reverse=True)

    def data_quality_report(self) -> dict:
        duplicate_sessions = Counter(
            e.session_id for e in self.events if e.session_id
        )

        return {
            "total_customers": len(self.customers),
            "total_products": len(self.products),
            "total_events": len(self.events),
            "unique_event_ids": len(self.event_ids),
            "events_without_session": sum(
                not e.session_id for e in self.events
            ),
            "purchase_events": sum(
                e.event_type == EventType.PURCHASE for e in self.events
            ),
            "refund_events": sum(
                e.event_type == EventType.REFUND for e in self.events
            ),
            "sessions_with_multiple_events": sum(
                count > 1 for count in duplicate_sessions.values()
            ),
        }

    @staticmethod
    def save_json(data, filename: str) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / filename

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, default=str)

        logger.info("Saved %s", path)

    @staticmethod
    def save_csv(data: list[dict], filename: str) -> None:
        if not data:
            logger.warning("No records available for %s", filename)
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / filename

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(data[0].keys())
            )
            writer.writeheader()
            writer.writerows(data)

        logger.info("Saved %s", path)


def build_sample_data():
    products = [
        Product(101, "Laptop Pro", "Electronics", 1200, 850),
        Product(102, "Wireless Mouse", "Accessories", 35, 12),
        Product(103, "Mechanical Keyboard", "Accessories", 95, 48),
        Product(104, "Smart Watch", "Wearables", 250, 140),
        Product(105, "USB-C Hub", "Accessories", 55, 22),
    ]

    customers = [
        Customer(1, date(2026, 1, 5), "Organic", "North"),
        Customer(2, date(2026, 1, 12), "Paid Search", "South"),
        Customer(3, date(2026, 2, 3), "Social", "East"),
        Customer(4, date(2026, 2, 15), "Organic", "West"),
        Customer(5, date(2026, 3, 1), "Referral", "North"),
        Customer(6, date(2026, 3, 10), "Paid Search", "South"),
        Customer(7, date(2026, 4, 2), "Social", "East"),
        Customer(8, date(2026, 4, 15), "Referral", "West"),
    ]

    base = datetime(2026, 4, 1, 10, tzinfo=timezone.utc)

    raw_events = [
        (1, 1, 101, EventType.VIEW, 0, 0),
        (2, 1, 101, EventType.ADD_TO_CART, 1, 0),
        (3, 1, 101, EventType.CHECKOUT, 2, 0),
        (4, 1, 101, EventType.PURCHASE, 3, 1200),
        (5, 1, 102, EventType.PURCHASE, 40, 35),
        (6, 1, 103, EventType.PURCHASE, 60, 95),
        (7, 2, 102, EventType.VIEW, 1, 0),
        (8, 2, 102, EventType.ADD_TO_CART, 2, 0),
        (9, 2, 102, EventType.PURCHASE, 4, 35),
        (10, 2, 102, EventType.REFUND, 10, 35),
        (11, 3, 104, EventType.VIEW, 5, 0),
        (12, 3, 104, EventType.PURCHASE, 7, 250),
        (13, 4, 103, EventType.VIEW, 12, 0),
        (14, 4, 103, EventType.ADD_TO_CART, 13, 0),
        (15, 4, 103, EventType.CHECKOUT, 14, 0),
        (16, 4, 103, EventType.PURCHASE, 15, 95),
        (17, 5, 105, EventType.VIEW, 20, 0),
        (18, 5, 105, EventType.PURCHASE, 22, 55),
        (19, 6, 101, EventType.VIEW, 25, 0),
        (20, 6, 101, EventType.ADD_TO_CART, 26, 0),
        (21, 7, 104, EventType.VIEW, 28, 0),
        (22, 8, 102, EventType.VIEW, 29, 0),
        (23, 8, 102, EventType.PURCHASE, 30, 35),
    ]

    events = []

    for event_id, customer_id, product_id, event_type, day, amount in raw_events:
        events.append(Event(
            event_id=event_id,
            customer_id=customer_id,
            product_id=product_id,
            event_type=event_type,
            timestamp=base + timedelta(days=day),
            amount=amount,
            session_id=f"S-{customer_id}-{day // 7}",
        ))

    return products, customers, events


def run_tests(engine: AnalyticsEngine):
    assert len(engine.events) == 23

    funnel = engine.conversion_funnel(
        date(2026, 4, 1), date(2026, 6, 30)
    )

    assert funnel[0].users >= funnel[-1].users
    assert engine.data_quality_report()["unique_event_ids"] == 23

    try:
        engine.add_event(engine.events[0])
        raise AssertionError("Duplicate event should fail")
    except ValueError:
        pass

    try:
        Event(
            999, 1, 101, EventType.VIEW,
            datetime(2026, 4, 1), 1, 0, "INVALID"
        )
        raise AssertionError("Naive timestamp should fail")
    except ValueError:
        pass

    logger.info("All validation tests passed")


def main():
    products, customers, events = build_sample_data()

    engine = AnalyticsEngine(products, customers, events)

    run_tests(engine)

    start = date(2026, 4, 1)
    end = date(2026, 6, 30)

    product_report = engine.product_performance(start, end)
    funnel_report = [
        asdict(row)
        for row in engine.conversion_funnel(start, end)
    ]
    session_report = engine.session_funnel(start, end)
    retention_report = engine.retention_analysis(
        date(2026, 1, 1), end
    )
    segmentation_report = engine.customer_segmentation(end)
    channel_report = engine.channel_performance(start, end)
    quality_report = engine.data_quality_report()

    print("\nPRODUCT PERFORMANCE")
    for row in product_report:
        print(row)

    print("\nCONVERSION FUNNEL")
    for row in funnel_report:
        print(row)

    print("\nSESSION FUNNEL")
    print(session_report)

    print("\nRETENTION")
    for row in retention_report:
        print(row)

    print("\nCUSTOMER SEGMENTS")
    for row in segmentation_report:
        print(row)

    print("\nCHANNEL PERFORMANCE")
    for row in channel_report:
        print(row)

    print("\nDATA QUALITY")
    print(quality_report)

    engine.save_json(product_report, "product_performance.json")
    engine.save_json(funnel_report, "conversion_funnel.json")
    engine.save_json(session_report, "session_funnel.json")
    engine.save_json(retention_report, "retention.json")
    engine.save_json(segmentation_report, "segmentation.json")
    engine.save_json(channel_report, "channel_performance.json")
    engine.save_json(quality_report, "data_quality.json")

    engine.save_csv(product_report, "product_performance.csv")
    engine.save_csv(segmentation_report, "segmentation.csv")


if __name__ == "__main__":
    main()
