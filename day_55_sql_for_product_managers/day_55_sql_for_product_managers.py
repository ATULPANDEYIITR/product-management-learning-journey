#!/usr/bin/env python3
"""Practical SQL analytics for product managers using only the Python standard library."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Any


SCHEMA = """
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    launch_date TEXT NOT NULL
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    signup_date TEXT NOT NULL,
    country TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL
);

CREATE TABLE events (
    event_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    event_type TEXT NOT NULL CHECK (
        event_type IN ('view', 'signup', 'activation', 'purchase', 'churn')
    ),
    event_date TEXT NOT NULL,
    revenue NUMERIC NOT NULL DEFAULT 0 CHECK (revenue >= 0)
);

CREATE INDEX idx_events_date_type ON events(event_date, event_type);
CREATE INDEX idx_events_user ON events(user_id);
CREATE INDEX idx_events_product ON events(product_id);
CREATE INDEX idx_users_signup ON users(signup_date);
"""


SAMPLE_DATA = {
    "products": [
        (1, "Analytics Pro", "Analytics", "2026-01-01"),
        (2, "Team Workspace", "Collaboration", "2026-02-01"),
        (3, "Mobile Insights", "Analytics", "2026-03-01"),
    ],
    "users": [
        (101, "2026-01-05", "India", "Organic"),
        (102, "2026-01-10", "USA", "Paid Search"),
        (103, "2026-02-12", "India", "Referral"),
        (104, "2026-02-20", "UK", "Organic"),
        (105, "2026-03-03", "USA", "Paid Search"),
        (106, "2026-03-10", "India", "Referral"),
    ],
    "events": [
        (1, 101, 1, "view", "2026-03-01", 0),
        (2, 101, 1, "activation", "2026-03-02", 0),
        (3, 101, 1, "purchase", "2026-03-05", 99),
        (4, 102, 1, "view", "2026-03-02", 0),
        (5, 102, 1, "purchase", "2026-03-07", 149),
        (6, 103, 2, "view", "2026-03-03", 0),
        (7, 103, 2, "activation", "2026-03-04", 0),
        (8, 104, 2, "view", "2026-03-05", 0),
        (9, 105, 3, "view", "2026-03-06", 0),
        (10, 105, 3, "activation", "2026-03-07", 0),
        (11, 105, 3, "purchase", "2026-03-08", 49),
        (12, 106, 1, "view", "2026-03-09", 0),
        (13, 106, 1, "churn", "2026-03-20", 0),
        (14, 101, 1, "purchase", "2026-04-02", 99),
    ],
}


@dataclass(frozen=True)
class QueryResult:
    title: str
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]

    def display(self) -> None:
        print(f"\n{self.title}")
        if not self.rows:
            print("(no rows)")
            return
        widths = [
            max(len(str(self.columns[i])), *(len(str(row[i])) for row in self.rows))
            for i in range(len(self.columns))
        ]
        print(" | ".join(self.columns[i].ljust(widths[i]) for i in range(len(widths))))
        print("-+-".join("-" * width for width in widths))
        for row in self.rows:
            print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(widths))))


class ProductAnalytics:
    """Runs parameterized SQL queries and validates analytical inputs."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def query(
        self,
        title: str,
        sql: str,
        parameters: tuple[Any, ...] = (),
    ) -> QueryResult:
        cursor = self.connection.execute(sql, parameters)
        rows = cursor.fetchall()
        return QueryResult(
            title=title,
            columns=tuple(column[0] for column in cursor.description or ()),
            rows=tuple(tuple(row) for row in rows),
        )

    @staticmethod
    def validate_date_range(start: str, end: str) -> None:
        try:
            parsed_start = date.fromisoformat(start)
            parsed_end = date.fromisoformat(end)
        except ValueError as exc:
            raise ValueError("Dates must use valid YYYY-MM-DD values.") from exc
        if parsed_start > parsed_end:
            raise ValueError("Start date must not be after end date.")

    def revenue_by_product(self, start: str, end: str) -> QueryResult:
        self.validate_date_range(start, end)
        return self.query(
            "Revenue by product (LEFT JOIN retains products with no purchases)",
            """
            SELECT
                p.product_name,
                p.category,
                COUNT(e.event_id) AS purchase_events,
                COALESCE(SUM(e.revenue), 0) AS total_revenue,
                ROUND(AVG(e.revenue), 2) AS average_event_revenue
            FROM products AS p
            LEFT JOIN events AS e
                ON e.product_id = p.product_id
               AND e.event_type = 'purchase'
               AND e.event_date BETWEEN ? AND ?
            GROUP BY p.product_id, p.product_name, p.category
            ORDER BY total_revenue DESC, p.product_name
            """,
            (start, end),
        )

    def acquisition_performance(self) -> QueryResult:
        return self.query(
            "Users and purchases by acquisition channel",
            """
            SELECT
                u.acquisition_channel,
                COUNT(DISTINCT u.user_id) AS registered_users,
                COUNT(DISTINCT CASE
                    WHEN e.event_type = 'purchase' THEN u.user_id
                END) AS paying_users,
                COALESCE(SUM(CASE
                    WHEN e.event_type = 'purchase' THEN e.revenue
                    ELSE 0
                END), 0) AS revenue,
                ROUND(
                    100.0 * COUNT(DISTINCT CASE
                        WHEN e.event_type = 'purchase' THEN u.user_id
                    END) / NULLIF(COUNT(DISTINCT u.user_id), 0),
                    2
                ) AS payer_conversion_percent
            FROM users AS u
            LEFT JOIN events AS e ON e.user_id = u.user_id
            GROUP BY u.acquisition_channel
            ORDER BY revenue DESC
            """,
        )

    def activation_funnel(self) -> QueryResult:
        return self.query(
            "Distinct-user funnel (not a sequential event funnel)",
            """
            SELECT
                COUNT(DISTINCT CASE WHEN event_type = 'view'
                    THEN user_id END) AS viewers,
                COUNT(DISTINCT CASE WHEN event_type = 'activation'
                    THEN user_id END) AS activated_users,
                COUNT(DISTINCT CASE WHEN event_type = 'purchase'
                    THEN user_id END) AS paying_users,
                ROUND(
                    100.0 * COUNT(DISTINCT CASE WHEN event_type = 'activation'
                        THEN user_id END)
                    / NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'view'
                        THEN user_id END), 0),
                    2
                ) AS activation_to_view_percent
            FROM events
            WHERE event_date BETWEEN ? AND ?
            """,
            ("2026-03-01", "2026-03-31"),
        )

    def daily_revenue(self, start: str, end: str) -> QueryResult:
        self.validate_date_range(start, end)
        return self.query(
            "Daily revenue",
            """
            SELECT event_date, SUM(revenue) AS daily_revenue
            FROM events
            WHERE event_type = 'purchase'
              AND event_date BETWEEN ? AND ?
            GROUP BY event_date
            HAVING SUM(revenue) > 0
            ORDER BY event_date
            """,
            (start, end),
        )

    def products_without_activity(self) -> QueryResult:
        return self.query(
            "Products without recorded events",
            """
            SELECT p.product_name
            FROM products AS p
            LEFT JOIN events AS e ON e.product_id = p.product_id
            WHERE e.event_id IS NULL
            ORDER BY p.product_name
            """,
        )


def create_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(SCHEMA)
        with connection:
            connection.executemany(
                "INSERT INTO products VALUES (?, ?, ?, ?)",
                SAMPLE_DATA["products"],
            )
            connection.executemany(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                SAMPLE_DATA["users"],
            )
            connection.executemany(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
                SAMPLE_DATA["events"],
            )
    except sqlite3.Error:
        connection.close()
        raise
    return connection


def run_assertions(analytics: ProductAnalytics) -> None:
    revenue = analytics.query(
        "Revenue validation",
        """
        SELECT SUM(revenue) AS total
        FROM events
        WHERE event_type = 'purchase'
          AND event_date BETWEEN ? AND ?
        """,
        ("2026-03-01", "2026-03-31"),
    )
    assert revenue.rows[0][0] == 297

    channels = analytics.query(
        "Distinct channel count",
        "SELECT COUNT(DISTINCT acquisition_channel) FROM users",
    )
    assert channels.rows[0][0] == 3

    try:
        analytics.validate_date_range("2026-04-01", "2026-03-01")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid date range was accepted.")


def main() -> None:
    connection = create_database()
    try:
        analytics = ProductAnalytics(connection)
        run_assertions(analytics)

        analytics.revenue_by_product("2026-03-01", "2026-03-31").display()
        analytics.acquisition_performance().display()
        analytics.activation_funnel().display()
        analytics.daily_revenue("2026-03-01", "2026-03-31").display()
        analytics.products_without_activity().display()

        print("\nValidation passed.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
