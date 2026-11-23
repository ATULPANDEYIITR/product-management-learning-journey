#!/usr/bin/env python3
"""
SaaS Metrics Analytics Engine
=============================

Implements:
- Customer churn and revenue churn
- Expansion and contraction MRR
- Net Revenue Retention (NRR)
- Gross Revenue Retention (GRR)
- Customer Acquisition Cost (CAC)
- CAC payback period
- Cohort-based revenue analysis
- Monthly recurring revenue reconciliation
- Validation, reporting, and scenario analysis

Python 3.10+
Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from collections import defaultdict
from typing import Optional
import json
import logging
import unittest


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("saas_metrics")

ZERO = Decimal("0")
HUNDRED = Decimal("100")


class MetricError(Exception):
    """Base exception for metric calculation errors."""


class ValidationError(MetricError):
    """Raised when business input violates validation rules."""


class InsufficientDataError(MetricError):
    """Raised when a metric cannot be calculated reliably."""


class CustomerStatus(str, Enum):
    ACTIVE = "active"
    CHURNED = "churned"


@dataclass(frozen=True)
class Customer:
    customer_id: str
    name: str
    acquisition_date: date
    monthly_recurring_revenue: Decimal
    status: CustomerStatus = CustomerStatus.ACTIVE
    segment: str = "SMB"

    def __post_init__(self):
        if not self.customer_id.strip():
            raise ValidationError("Customer ID cannot be empty.")

        if self.monthly_recurring_revenue < ZERO:
            raise ValidationError("MRR cannot be negative.")


@dataclass(frozen=True)
class RevenueMovement:
    customer_id: str
    period: str
    starting_mrr: Decimal
    ending_mrr: Decimal

    def __post_init__(self):
        if self.starting_mrr < ZERO or self.ending_mrr < ZERO:
            raise ValidationError("MRR values cannot be negative.")

        try:
            year, month = map(int, self.period.split("-"))
            date(year, month, 1)
        except (ValueError, TypeError):
            raise ValidationError(
                "Period must use YYYY-MM format."
            )


@dataclass(frozen=True)
class AcquisitionCosts:
    period: str
    sales_marketing_cost: Decimal
    new_customers: int
    gross_margin: Decimal

    def __post_init__(self):
        if self.sales_marketing_cost < ZERO:
            raise ValidationError("Acquisition cost cannot be negative.")

        if self.new_customers < 0:
            raise ValidationError("Customer count cannot be negative.")

        if not ZERO <= self.gross_margin <= HUNDRED:
            raise ValidationError(
                "Gross margin must be between 0 and 100."
            )


@dataclass
class SaaSMetrics:
    period: str
    starting_mrr: Decimal
    ending_mrr: Decimal
    new_mrr: Decimal
    expansion_mrr: Decimal
    contraction_mrr: Decimal
    churned_mrr: Decimal
    starting_customers: int
    ending_customers: int
    churned_customers: int
    new_customers: int

    @property
    def gross_revenue_retention(self) -> Optional[Decimal]:
        if self.starting_mrr == ZERO:
            return None

        retained = (
            self.starting_mrr
            - self.churned_mrr
            - self.contraction_mrr
        )

        return retained / self.starting_mrr * HUNDRED

    @property
    def net_revenue_retention(self) -> Optional[Decimal]:
        if self.starting_mrr == ZERO:
            return None

        retained = (
            self.starting_mrr
            - self.churned_mrr
            - self.contraction_mrr
            + self.expansion_mrr
        )

        return retained / self.starting_mrr * HUNDRED

    @property
    def revenue_churn_rate(self) -> Optional[Decimal]:
        if self.starting_mrr == ZERO:
            return None

        return (
            (self.churned_mrr + self.contraction_mrr)
            / self.starting_mrr
            * HUNDRED
        )

    @property
    def logo_churn_rate(self) -> Optional[Decimal]:
        if self.starting_customers == 0:
            return None

        return (
            Decimal(self.churned_customers)
            / Decimal(self.starting_customers)
            * HUNDRED
        )

    @property
    def expansion_rate(self) -> Optional[Decimal]:
        if self.starting_mrr == ZERO:
            return None

        return self.expansion_mrr / self.starting_mrr * HUNDRED

    @property
    def mrr_growth_rate(self) -> Optional[Decimal]:
        if self.starting_mrr == ZERO:
            return None

        return (
            (self.ending_mrr - self.starting_mrr)
            / self.starting_mrr
            * HUNDRED
        )

    def validate_reconciliation(self):
        expected = (
            self.starting_mrr
            + self.new_mrr
            + self.expansion_mrr
            - self.contraction_mrr
            - self.churned_mrr
        )

        if expected != self.ending_mrr:
            raise ValidationError(
                f"MRR reconciliation failed: expected {expected}, "
                f"received {self.ending_mrr}."
            )

        if self.churned_customers > self.starting_customers:
            raise ValidationError(
                "Churned customers exceed starting customers."
            )

        if self.ending_customers < 0 or self.new_customers < 0:
            raise ValidationError("Invalid customer count.")

        return True


class SaaSAnalytics:

    def __init__(self):
        self.movements: dict[str, list[RevenueMovement]] = defaultdict(list)
        self.acquisition_records: dict[str, AcquisitionCosts] = {}

    def add_movement(self, movement: RevenueMovement):
        if any(
            existing.customer_id == movement.customer_id
            and existing.period == movement.period
            for existing in self.movements[movement.period]
        ):
            raise ValidationError(
                "Duplicate customer movement for the period."
            )

        self.movements[movement.period].append(movement)

    def add_acquisition_cost(self, record: AcquisitionCosts):
        if record.period in self.acquisition_records:
            raise ValidationError(
                "Acquisition record already exists for this period."
            )

        self.acquisition_records[record.period] = record

    def calculate_period(self, period: str) -> SaaSMetrics:
        records = self.movements.get(period, [])

        if not records:
            raise InsufficientDataError(
                f"No revenue movements found for {period}."
            )

        starting_mrr = sum(
            (r.starting_mrr for r in records), ZERO
        )

        ending_mrr = sum(
            (r.ending_mrr for r in records), ZERO
        )

        new_mrr = ZERO
        expansion_mrr = ZERO
        contraction_mrr = ZERO
        churned_mrr = ZERO

        starting_customers = 0
        ending_customers = 0
        churned_customers = 0
        new_customers = 0

        for record in records:
            start = record.starting_mrr
            end = record.ending_mrr

            if start > ZERO:
                starting_customers += 1

                if end == ZERO:
                    churned_mrr += start
                    churned_customers += 1
                elif end > start:
                    expansion_mrr += end - start
                elif end < start:
                    contraction_mrr += start - end

            elif end > ZERO:
                new_mrr += end
                new_customers += 1

            if end > ZERO:
                ending_customers += 1

        metrics = SaaSMetrics(
            period=period,
            starting_mrr=starting_mrr,
            ending_mrr=ending_mrr,
            new_mrr=new_mrr,
            expansion_mrr=expansion_mrr,
            contraction_mrr=contraction_mrr,
            churned_mrr=churned_mrr,
            starting_customers=starting_customers,
            ending_customers=ending_customers,
            churned_customers=churned_customers,
            new_customers=new_customers
        )

        metrics.validate_reconciliation()
        return metrics

    def cac(self, period: str) -> Decimal:
        record = self.acquisition_records.get(period)

        if record is None:
            raise InsufficientDataError(
                f"Missing acquisition data for {period}."
            )

        if record.new_customers == 0:
            raise InsufficientDataError(
                "CAC cannot be calculated with zero new customers."
            )

        return (
            record.sales_marketing_cost
            / Decimal(record.new_customers)
        )

    def cac_payback_months(
        self,
        period: str,
        average_new_customer_mrr: Decimal
    ) -> Decimal:

        record = self.acquisition_records.get(period)

        if record is None:
            raise InsufficientDataError(
                "Acquisition data unavailable."
            )

        if record.new_customers == 0:
            raise InsufficientDataError(
                "No acquired customers."
            )

        if average_new_customer_mrr <= ZERO:
            raise ValidationError(
                "Average new customer MRR must be positive."
            )

        if record.gross_margin == ZERO:
            raise InsufficientDataError(
                "Zero gross margin produces no payback."
            )

        acquisition_cost = self.cac(period)

        monthly_gross_profit = (
            average_new_customer_mrr
            * record.gross_margin
            / HUNDRED
        )

        return acquisition_cost / monthly_gross_profit

    def customer_lifetime_revenue(
        self,
        average_monthly_revenue: Decimal,
        monthly_logo_churn_rate: Decimal
    ) -> Decimal:

        if average_monthly_revenue < ZERO:
            raise ValidationError("Revenue cannot be negative.")

        if not ZERO < monthly_logo_churn_rate <= HUNDRED:
            raise ValidationError(
                "Monthly churn must be greater than zero "
                "and no greater than 100%."
            )

        return (
            average_monthly_revenue
            / (monthly_logo_churn_rate / HUNDRED)
        )

    def cohort_analysis(
        self,
        cohorts: dict[str, dict[str, Decimal]]
    ) -> dict[str, dict[str, Optional[Decimal]]]:

        result = {}

        for cohort_name, revenue_periods in cohorts.items():
            if not revenue_periods:
                continue

            baseline = revenue_periods.get("M0", ZERO)

            if baseline <= ZERO:
                raise ValidationError(
                    f"Invalid baseline for cohort {cohort_name}."
                )

            result[cohort_name] = {}

            for period, revenue in revenue_periods.items():
                if revenue < ZERO:
                    raise ValidationError(
                        "Cohort revenue cannot be negative."
                    )

                result[cohort_name][period] = (
                    revenue / baseline * HUNDRED
                )

        return result

    @staticmethod
    def percentage(value: Optional[Decimal]) -> str:
        if value is None:
            return "N/A"

        return f"{value.quantize(Decimal('0.01'))}%"

    def report(self, metrics: SaaSMetrics) -> dict:
        return {
            "period": metrics.period,
            "starting_mrr": str(metrics.starting_mrr),
            "ending_mrr": str(metrics.ending_mrr),
            "new_mrr": str(metrics.new_mrr),
            "expansion_mrr": str(metrics.expansion_mrr),
            "contraction_mrr": str(metrics.contraction_mrr),
            "churned_mrr": str(metrics.churned_mrr),
            "nrr": self.percentage(
                metrics.net_revenue_retention
            ),
            "grr": self.percentage(
                metrics.gross_revenue_retention
            ),
            "revenue_churn": self.percentage(
                metrics.revenue_churn_rate
            ),
            "logo_churn": self.percentage(
                metrics.logo_churn_rate
            ),
            "mrr_growth": self.percentage(
                metrics.mrr_growth_rate
            )
        }


def decimal(value: str | int | float) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValidationError(
            f"Invalid decimal value: {value}"
        ) from exc


def build_demo() -> SaaSAnalytics:
    analytics = SaaSAnalytics()

    # Existing customers may expand, contract, or churn.
    movements = [
        RevenueMovement("C001", "2026-10", decimal(1000), decimal(1200)),
        RevenueMovement("C002", "2026-10", decimal(2000), decimal(1500)),
        RevenueMovement("C003", "2026-10", decimal(1500), ZERO),
        RevenueMovement("C004", "2026-10", decimal(500), decimal(500)),
        RevenueMovement("C005", "2026-10", ZERO, decimal(1000)),
        RevenueMovement("C006", "2026-10", ZERO, decimal(800)),
    ]

    for movement in movements:
        analytics.add_movement(movement)

    analytics.add_acquisition_cost(
        AcquisitionCosts(
            period="2026-10",
            sales_marketing_cost=decimal(12000),
            new_customers=2,
            gross_margin=decimal(80)
        )
    )

    return analytics


class MetricsTests(unittest.TestCase):

    def test_retention(self):
        metrics = SaaSMetrics(
            "2026-10",
            decimal(5000),
            decimal(5000),
            decimal(1800),
            decimal(200),
            decimal(500),
            decimal(1500),
            4, 5, 1, 2
        )

        self.assertEqual(
            metrics.net_revenue_retention,
            decimal(64)
        )

        self.assertEqual(
            metrics.gross_revenue_retention,
            decimal(60)
        )

    def test_reconciliation(self):
        metrics = SaaSMetrics(
            "2026-10",
            decimal(5000),
            decimal(5000),
            decimal(1800),
            decimal(200),
            decimal(500),
            decimal(1000),
            4, 5, 1, 2
        )

        with self.assertRaises(ValidationError):
            metrics.validate_reconciliation()

    def test_zero_baseline(self):
        metrics = SaaSMetrics(
            "2026-10",
            ZERO, ZERO, ZERO, ZERO, ZERO, ZERO,
            0, 0, 0, 0
        )

        self.assertIsNone(metrics.net_revenue_retention)
        self.assertIsNone(metrics.gross_revenue_retention)

    def test_invalid_margin(self):
        with self.assertRaises(ValidationError):
            AcquisitionCosts(
                "2026-10", decimal(1000), 2, decimal(120)
            )


def main():
    analytics = build_demo()
    metrics = analytics.calculate_period("2026-10")

    print("\nSAAS REVENUE PERFORMANCE")
    print("=" * 55)

    print(json.dumps(
        analytics.report(metrics),
        indent=4
    ))

    cac = analytics.cac("2026-10")

    average_mrr = decimal(900)

    payback = analytics.cac_payback_months(
        "2026-10",
        average_mrr
    )

    print("\nCUSTOMER ACQUISITION ECONOMICS")
    print("=" * 55)
    print(f"CAC: {cac:.2f}")
    print(f"Average new customer MRR: {average_mrr:.2f}")
    print(f"CAC payback period: {payback:.2f} months")

    ltv = analytics.customer_lifetime_revenue(
        decimal(900),
        decimal(3)
    )

    print(f"Simple revenue-based lifetime value: {ltv:.2f}")

    cohorts = {
        "2026-Q3": {
            "M0": decimal(10000),
            "M1": decimal(9800),
            "M2": decimal(10500),
            "M3": decimal(11000)
        },
        "2026-Q4": {
            "M0": decimal(15000),
            "M1": decimal(14200)
        }
    }

    print("\nCOHORT REVENUE RETENTION")
    print("=" * 55)
    print(json.dumps(
        {
            cohort: {
                period: f"{value:.2f}%"
                for period, value in periods.items()
            }
            for cohort, periods
            in analytics.cohort_analysis(cohorts).items()
        },
        indent=4
    ))

    print("\nVALIDATION TESTS")
    unittest.main(argv=["saas_metrics.py"], exit=False)


if __name__ == "__main__":
    main()
