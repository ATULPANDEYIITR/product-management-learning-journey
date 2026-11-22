#!/usr/bin/env python3
"""
Monetization Metrics Analytics Engine

Implements:
- ARPU: Average Revenue Per User
- ARPPU: Average Revenue Per Paying User
- MRR: Monthly Recurring Revenue
- ARR: Annual Recurring Revenue
- LTV: Customer Lifetime Value
- CAC: Customer Acquisition Cost
- Gross Margin

Uses Decimal arithmetic for financial calculations.
Python 3.10+
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from enum import Enum
from typing import Optional
import json
import logging
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

D = Decimal
ZERO = D("0")
CENT = D("0.01")


class MonetizationError(Exception):
    """Base exception for monetization calculations."""


class ValidationError(MonetizationError):
    """Raised when financial or customer data is invalid."""


class MetricUnavailableError(MonetizationError):
    """Raised when a metric cannot be calculated reliably."""


class RevenueType(Enum):
    RECURRING = "recurring"
    ONE_TIME = "one_time"


@dataclass(frozen=True)
class Customer:
    customer_id: str
    is_paying: bool
    acquisition_date: date
    active: bool = True

    def __post_init__(self):
        if not self.customer_id.strip():
            raise ValidationError("Customer ID cannot be empty.")


@dataclass(frozen=True)
class RevenueRecord:
    customer_id: str
    amount: Decimal
    revenue_type: RevenueType
    billing_interval_months: int = 1

    def __post_init__(self):
        if self.amount < ZERO:
            raise ValidationError("Revenue cannot be negative.")

        if self.billing_interval_months < 1:
            raise ValidationError("Billing interval must be positive.")


@dataclass(frozen=True)
class AcquisitionData:
    marketing_spend: Decimal
    sales_spend: Decimal
    new_customers: int

    def __post_init__(self):
        if self.marketing_spend < ZERO or self.sales_spend < ZERO:
            raise ValidationError("Acquisition costs cannot be negative.")

        if self.new_customers < 0:
            raise ValidationError("New customer count cannot be negative.")


@dataclass(frozen=True)
class CostData:
    variable_cost: Decimal
    fixed_cost: Decimal = ZERO

    def __post_init__(self):
        if self.variable_cost < ZERO or self.fixed_cost < ZERO:
            raise ValidationError("Operating costs cannot be negative.")


@dataclass(frozen=True)
class MonetizationMetrics:
    reporting_date: date
    total_users: int
    paying_users: int
    arpu: Optional[Decimal]
    arppu: Optional[Decimal]
    mrr: Decimal
    arr: Decimal
    ltv: Optional[Decimal]
    cac: Optional[Decimal]
    gross_margin: Optional[Decimal]
    gross_profit: Decimal
    monthly_churn_rate: Optional[Decimal]

    def to_dict(self):
        return {
            "reporting_date": self.reporting_date.isoformat(),
            "total_users": self.total_users,
            "paying_users": self.paying_users,
            "ARPU": str(self.arpu) if self.arpu is not None else None,
            "ARPPU": str(self.arppu) if self.arppu is not None else None,
            "MRR": str(self.mrr),
            "ARR": str(self.arr),
            "LTV": str(self.ltv) if self.ltv is not None else None,
            "CAC": str(self.cac) if self.cac is not None else None,
            "gross_margin": (
                str(self.gross_margin)
                if self.gross_margin is not None else None
            ),
            "gross_profit": str(self.gross_profit),
            "monthly_churn_rate": (
                str(self.monthly_churn_rate)
                if self.monthly_churn_rate is not None else None
            )
        }


class MonetizationEngine:
    """
    Calculates subscription monetization metrics.

    MRR includes normalized recurring revenue only.
    ARR is an annualized run-rate, not recognized annual revenue.
    LTV uses a simplified steady-state model.
    """

    def __init__(
        self,
        customers: list[Customer],
        revenue_records: list[RevenueRecord],
        acquisition: AcquisitionData,
        costs: CostData,
        monthly_churn_rate: Optional[Decimal]
    ):
        self.customers = customers
        self.revenue_records = revenue_records
        self.acquisition = acquisition
        self.costs = costs
        self.monthly_churn_rate = monthly_churn_rate

        self._validate()

    def _validate(self):
        ids = [customer.customer_id for customer in self.customers]

        if len(ids) != len(set(ids)):
            raise ValidationError("Duplicate customer IDs detected.")

        known_ids = set(ids)

        for record in self.revenue_records:
            if record.customer_id not in known_ids:
                raise ValidationError(
                    f"Unknown customer: {record.customer_id}"
                )

        if self.monthly_churn_rate is not None:
            if not ZERO <= self.monthly_churn_rate <= D("1"):
                raise ValidationError(
                    "Monthly churn must be between 0 and 1."
                )

        if self.acquisition.new_customers > len(self.customers):
            raise ValidationError(
                "Acquired customers exceed the supplied customer population."
            )

    @staticmethod
    def money(value: Decimal) -> Decimal:
        return value.quantize(CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def safe_divide(
        numerator: Decimal,
        denominator: Decimal
    ) -> Optional[Decimal]:
        if denominator == ZERO:
            return None
        return numerator / denominator

    def calculate_mrr(self) -> Decimal:
        active_ids = {
            customer.customer_id
            for customer in self.customers
            if customer.active and customer.is_paying
        }

        mrr = ZERO

        for record in self.revenue_records:
            if (
                record.customer_id in active_ids
                and record.revenue_type == RevenueType.RECURRING
            ):
                mrr += (
                    record.amount /
                    D(record.billing_interval_months)
                )

        return self.money(mrr)

    def calculate(self, reporting_date: date) -> MonetizationMetrics:
        active_customers = [
            customer for customer in self.customers
            if customer.active
        ]

        paying_customers = [
            customer for customer in active_customers
            if customer.is_paying
        ]

        total_users = len(active_customers)
        paying_users = len(paying_customers)

        mrr = self.calculate_mrr()
        arr = self.money(mrr * D("12"))

        arpu = self.safe_divide(mrr, D(total_users))
        arppu = self.safe_divide(mrr, D(paying_users))

        total_revenue = (
            mrr + sum(
                (
                    record.amount
                    for record in self.revenue_records
                    if record.revenue_type == RevenueType.ONE_TIME
                ),
                ZERO
            )
        )

        gross_profit = (
            total_revenue - self.costs.variable_cost
        )

        gross_margin = self.safe_divide(
            gross_profit,
            total_revenue
        )

        total_acquisition_cost = (
            self.acquisition.marketing_spend
            + self.acquisition.sales_spend
        )

        cac = self.safe_divide(
            total_acquisition_cost,
            D(self.acquisition.new_customers)
        )

        ltv = None

        if (
            arppu is not None
            and gross_margin is not None
            and self.monthly_churn_rate is not None
            and self.monthly_churn_rate > ZERO
        ):
            ltv = (
                arppu
                * gross_margin
                / self.monthly_churn_rate
            )

        return MonetizationMetrics(
            reporting_date=reporting_date,
            total_users=total_users,
            paying_users=paying_users,
            arpu=self.money(arpu) if arpu is not None else None,
            arppu=self.money(arppu) if arppu is not None else None,
            mrr=mrr,
            arr=arr,
            ltv=self.money(ltv) if ltv is not None else None,
            cac=self.money(cac) if cac is not None else None,
            gross_margin=(
                gross_margin.quantize(
                    D("0.0001"),
                    rounding=ROUND_HALF_UP
                )
                if gross_margin is not None else None
            ),
            gross_profit=self.money(gross_profit),
            monthly_churn_rate=self.monthly_churn_rate
        )


class MonetizationAnalyzer:
    """Evaluates business economics and operational health."""

    @staticmethod
    def ltv_cac_ratio(
        ltv: Optional[Decimal],
        cac: Optional[Decimal]
    ) -> Optional[Decimal]:
        if ltv is None or cac is None or cac <= ZERO:
            return None
        return (ltv / cac).quantize(D("0.01"))

    @staticmethod
    def payback_period(
        cac: Optional[Decimal],
        arppu: Optional[Decimal],
        gross_margin: Optional[Decimal]
    ) -> Optional[Decimal]:
        if cac is None or arppu is None or gross_margin is None:
            return None

        monthly_contribution = arppu * gross_margin

        if monthly_contribution <= ZERO:
            return None

        return (
            cac / monthly_contribution
        ).quantize(D("0.01"))

    @staticmethod
    def classify_ratio(ratio: Optional[Decimal]) -> str:
        if ratio is None:
            return "Unavailable"
        if ratio < D("1"):
            return "Acquisition economics are negative"
        if ratio < D("3"):
            return "Below conventional 3:1 benchmark"
        return "Meets or exceeds conventional 3:1 benchmark"


def save_report(metrics: MonetizationMetrics, output_path: str):
    """Write a JSON report without using floating-point money values."""
    path = Path(output_path)

    if path.suffix.lower() != ".json":
        raise ValidationError("Report path must use .json extension.")

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(".tmp")

    try:
        temporary_path.write_text(
            json.dumps(metrics.to_dict(), indent=4),
            encoding="utf-8"
        )
        temporary_path.replace(path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def main():
    customers = [
        Customer("C001", True, date(2026, 1, 10)),
        Customer("C002", True, date(2026, 2, 12)),
        Customer("C003", True, date(2026, 3, 15)),
        Customer("C004", False, date(2026, 4, 20)),
        Customer("C005", True, date(2026, 5, 25)),
        Customer("C006", False, date(2026, 6, 5)),
    ]

    revenue_records = [
        RevenueRecord("C001", D("100"), RevenueType.RECURRING),
        RevenueRecord("C002", D("150"), RevenueType.RECURRING),
        RevenueRecord("C003", D("200"), RevenueType.RECURRING),
        RevenueRecord("C005", D("250"), RevenueType.RECURRING),
        RevenueRecord("C001", D("50"), RevenueType.ONE_TIME),
    ]

    acquisition = AcquisitionData(
        marketing_spend=D("3000"),
        sales_spend=D("2000"),
        new_customers=5
    )

    costs = CostData(
        variable_cost=D("180"),
        fixed_cost=D("1200")
    )

    engine = MonetizationEngine(
        customers=customers,
        revenue_records=revenue_records,
        acquisition=acquisition,
        costs=costs,
        monthly_churn_rate=D("0.05")
    )

    metrics = engine.calculate(date(2026, 11, 30))

    ratio = MonetizationAnalyzer.ltv_cac_ratio(
        metrics.ltv,
        metrics.cac
    )

    payback = MonetizationAnalyzer.payback_period(
        metrics.cac,
        metrics.arppu,
        metrics.gross_margin
    )

    print("\nMONETIZATION PERFORMANCE REPORT")
    print("=" * 45)

    for name, value in metrics.to_dict().items():
        print(f"{name:25}: {value}")

    print(f"{'LTV/CAC Ratio':25}: {ratio}")
    print(f"{'CAC Payback (months)':25}: {payback}")
    print(
        f"{'Acquisition Assessment':25}: "
        f"{MonetizationAnalyzer.classify_ratio(ratio)}"
    )

    save_report(metrics, "monetization_report.json")
    logging.info("Report saved successfully.")

    # Boundary tests.
    assert MonetizationAnalyzer.ltv_cac_ratio(
        D("300"), D("100")
    ) == D("3.00")

    assert MonetizationAnalyzer.ltv_cac_ratio(
        D("300"), ZERO
    ) is None

    assert engine.calculate_mrr() == D("700.00")

    logging.info("Validation tests passed.")


if __name__ == "__main__":
    try:
        main()
    except (MonetizationError, OSError, ArithmeticError) as exc:
        logging.error("Execution failed: %s", exc)
        raise SystemExit(1)
