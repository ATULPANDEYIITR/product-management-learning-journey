"""
PRODUCT LIFECYCLE
=================

A comprehensive, executable study guide covering the Product Lifecycle from
discovery through retirement.

Lifecycle covered:
    1. Discovery
    2. Validation
    3. Development
    4. Launch
    5. Growth
    6. Maturity
    7. Decline
    8. Retirement

This file is intentionally self-contained and uses only the Python standard
library.

The examples use a fictional product named "FlowBoard", a collaborative
workflow-management product. The examples are generic enough to demonstrate
product-management principles without depending on external services.

Run:
    python product_lifecycle.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Callable, Iterable, Optional
import math
import random
import statistics
import unittest


# ============================================================================
# 1. PRODUCT LIFECYCLE FUNDAMENTALS
# ============================================================================

class LifecycleStage(Enum):
    """Canonical product lifecycle stages used in this study guide."""

    DISCOVERY = "Discovery"
    VALIDATION = "Validation"
    DEVELOPMENT = "Development"
    LAUNCH = "Launch"
    GROWTH = "Growth"
    MATURITY = "Maturity"
    DECLINE = "Decline"
    RETIREMENT = "Retirement"


@dataclass
class Product:
    """Basic representation of a product moving through its lifecycle."""

    name: str
    category: str
    stage: LifecycleStage = LifecycleStage.DISCOVERY
    version: str = "0.1.0"
    customers: int = 0
    monthly_revenue: float = 0.0
    monthly_active_users: int = 0
    monthly_churn_rate: float = 0.0
    gross_margin: float = 0.0
    market_share: float = 0.0
    notes: list[str] = field(default_factory=list)

    def move_to(self, stage: LifecycleStage) -> None:
        """Move the product to another lifecycle stage."""

        self.stage = stage

    def add_note(self, note: str) -> None:
        self.notes.append(note)


def explain_lifecycle() -> None:
    """Print the lifecycle at a high level."""

    print("\nPRODUCT LIFECYCLE")
    print("-" * 80)

    stages = [
        (
            LifecycleStage.DISCOVERY,
            "Identify a meaningful customer problem and potential opportunity.",
        ),
        (
            LifecycleStage.VALIDATION,
            "Test whether the problem, solution, demand, and business model are credible.",
        ),
        (
            LifecycleStage.DEVELOPMENT,
            "Build, test, instrument, and prepare the product for real users.",
        ),
        (
            LifecycleStage.LAUNCH,
            "Introduce the product to its target market and establish initial adoption.",
        ),
        (
            LifecycleStage.GROWTH,
            "Increase adoption, retention, revenue, distribution, and operational capacity.",
        ),
        (
            LifecycleStage.MATURITY,
            "Optimize a stable product while defending market position and economics.",
        ),
        (
            LifecycleStage.DECLINE,
            "Manage weakening demand, economics, relevance, or strategic importance.",
        ),
        (
            LifecycleStage.RETIREMENT,
            "Safely discontinue the product and migrate or support remaining users.",
        ),
    ]

    for stage, definition in stages:
        print(f"{stage.value:12} | {definition}")


# ============================================================================
# 2. PRODUCT DISCOVERY
# ============================================================================

@dataclass
class CustomerProblem:
    """A structured representation of a discovered customer problem."""

    customer_segment: str
    problem: str
    frequency: float
    severity: float
    current_alternative: str
    willingness_to_pay: float
    evidence_count: int = 0

    @property
    def problem_score(self) -> float:
        """
        Estimate problem attractiveness.

        The score is not a universal industry formula. It is a teaching
        heuristic showing how multiple signals can be combined.
        """

        return (
            self.frequency
            * self.severity
            * max(self.willingness_to_pay, 0)
            * math.log1p(self.evidence_count)
        )


def conduct_customer_interview(
    customer_name: str,
    role: str,
    current_process: str,
    pain_point: str,
    frequency: int,
    impact: int,
) -> dict:
    """
    Represent an interview record.

    Good discovery focuses on behavior and evidence rather than asking only
    whether a customer likes an idea.
    """

    return {
        "customer": customer_name,
        "role": role,
        "current_process": current_process,
        "pain_point": pain_point,
        "frequency": frequency,
        "impact": impact,
    }


def calculate_problem_priority(
    frequency: float,
    severity: float,
    reach: float,
    strategic_fit: float,
) -> float:
    """
    Calculate a simple opportunity-priority score.

    All input dimensions are expected on a 1-10 scale.
    """

    values = [frequency, severity, reach, strategic_fit]

    if any(value < 1 or value > 10 for value in values):
        raise ValueError("All priority inputs must be between 1 and 10.")

    return frequency * severity * reach * strategic_fit


def create_persona(
    name: str,
    role: str,
    goals: list[str],
    frustrations: list[str],
    behaviors: list[str],
) -> dict:
    """Create a lightweight persona representation."""

    if not name.strip():
        raise ValueError("Persona name cannot be empty.")

    return {
        "name": name,
        "role": role,
        "goals": goals,
        "frustrations": frustrations,
        "behaviors": behaviors,
    }


def build_value_proposition(
    customer: str,
    problem: str,
    solution: str,
    outcome: str,
) -> str:
    """Create a concise value proposition."""

    return (
        f"For {customer} who struggle with {problem}, "
        f"{solution} helps them achieve {outcome}."
    )


# ============================================================================
# 3. MARKET AND COMPETITIVE DISCOVERY
# ============================================================================

@dataclass
class Competitor:
    name: str
    price: float
    market_share: float
    strengths: list[str]
    weaknesses: list[str]


def compare_competitors(competitors: Iterable[Competitor]) -> list[dict]:
    """Create normalized competitor observations."""

    competitors = list(competitors)

    if not competitors:
        return []

    maximum_share = max(c.market_share for c in competitors)

    return [
        {
            "name": competitor.name,
            "price": competitor.price,
            "relative_market_share": (
                competitor.market_share / maximum_share
                if maximum_share > 0
                else 0
            ),
            "strength_count": len(competitor.strengths),
            "weakness_count": len(competitor.weaknesses),
        }
        for competitor in competitors
    ]


def estimate_tam(
    number_of_potential_customers: int,
    annual_revenue_per_customer: float,
) -> float:
    """Estimate Total Addressable Market."""

    if number_of_potential_customers < 0:
        raise ValueError("Customer count cannot be negative.")

    if annual_revenue_per_customer < 0:
        raise ValueError("Revenue per customer cannot be negative.")

    return number_of_potential_customers * annual_revenue_per_customer


def estimate_sam(
    tam: float,
    addressable_percentage: float,
) -> float:
    """Estimate Serviceable Available Market."""

    if not 0 <= addressable_percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    return tam * addressable_percentage / 100


def estimate_som(
    sam: float,
    realistic_market_capture_percentage: float,
) -> float:
    """Estimate Serviceable Obtainable Market."""

    if not 0 <= realistic_market_capture_percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    return sam * realistic_market_capture_percentage / 100


# ============================================================================
# 4. OPPORTUNITY ASSESSMENT
# ============================================================================

@dataclass
class Opportunity:
    """Opportunity record used for discovery prioritization."""

    name: str
    customer_value: float
    business_value: float
    strategic_alignment: float
    confidence: float
    effort: float

    def score(self) -> float:
        """Weighted opportunity score divided by estimated effort."""

        numerator = (
            self.customer_value * 0.35
            + self.business_value * 0.25
            + self.strategic_alignment * 0.20
            + self.confidence * 0.20
        )

        return numerator / max(self.effort, 0.1)


def prioritize_opportunities(
    opportunities: list[Opportunity],
) -> list[tuple[str, float]]:
    """Return opportunities ordered from highest to lowest score."""

    ranked = [(item.name, round(item.score(), 2)) for item in opportunities]
    return sorted(ranked, key=lambda item: item[1], reverse=True)


# ============================================================================
# 5. VALIDATION
# ============================================================================

@dataclass
class Hypothesis:
    """A falsifiable product hypothesis."""

    statement: str
    metric: str
    threshold: float
    observed_value: Optional[float] = None

    def is_supported(self) -> bool:
        """
        Determine whether observed evidence supports the hypothesis.

        This example assumes higher values are better. Real hypotheses may
        require lower-is-better, directional, or statistical tests.
        """

        if self.observed_value is None:
            raise ValueError("Observed value has not been recorded.")

        return self.observed_value >= self.threshold


def design_experiment(
    hypothesis: str,
    target_metric: str,
    success_threshold: float,
    duration_days: int,
) -> dict:
    """Create an experiment specification."""

    if duration_days <= 0:
        raise ValueError("Experiment duration must be positive.")

    return {
        "hypothesis": hypothesis,
        "metric": target_metric,
        "success_threshold": success_threshold,
        "duration_days": duration_days,
    }


def calculate_conversion_rate(
    conversions: int,
    opportunities: int,
) -> float:
    """Calculate conversion rate safely."""

    if opportunities < 0 or conversions < 0:
        raise ValueError("Counts cannot be negative.")

    if conversions > opportunities:
        raise ValueError("Conversions cannot exceed opportunities.")

    if opportunities == 0:
        return 0.0

    return conversions / opportunities


def calculate_retention_rate(
    retained_users: int,
    starting_users: int,
) -> float:
    """Calculate cohort retention."""

    if retained_users < 0 or starting_users < 0:
        raise ValueError("User counts cannot be negative.")

    if retained_users > starting_users:
        raise ValueError("Retained users cannot exceed starting users.")

    if starting_users == 0:
        return 0.0

    return retained_users / starting_users


def calculate_churn_rate(
    lost_customers: int,
    starting_customers: int,
) -> float:
    """Calculate customer churn."""

    if lost_customers < 0 or starting_customers < 0:
        raise ValueError("Counts cannot be negative.")

    if lost_customers > starting_customers:
        raise ValueError("Lost customers cannot exceed starting customers.")

    if starting_customers == 0:
        return 0.0

    return lost_customers / starting_customers


@dataclass
class ValidationExperiment:
    """Experiment result with decision rules."""

    name: str
    sample_size: int
    success_rate: float
    threshold: float

    def decision(self) -> str:
        if self.sample_size <= 0:
            return "INCONCLUSIVE: insufficient sample size."

        if self.success_rate >= self.threshold:
            return "SUPPORTED: evidence meets the predefined threshold."

        return "NOT SUPPORTED: evidence is below the predefined threshold."


def run_fake_validation_experiment(
    sample_size: int,
    expected_conversion: float,
    random_seed: int = 42,
) -> ValidationExperiment:
    """
    Generate deterministic synthetic validation data.

    Synthetic data is useful for learning the mechanics, but should not be
    confused with evidence from real customers.
    """

    if sample_size <= 0:
        raise ValueError("Sample size must be positive.")

    if not 0 <= expected_conversion <= 1:
        raise ValueError("Conversion probability must be between 0 and 1.")

    rng = random.Random(random_seed)
    conversions = sum(
        1 for _ in range(sample_size)
        if rng.random() < expected_conversion
    )

    observed_rate = conversions / sample_size

    return ValidationExperiment(
        name="Synthetic Landing Page Test",
        sample_size=sample_size,
        success_rate=observed_rate,
        threshold=0.10,
    )


# ============================================================================
# 6. MVP AND PRODUCT SCOPE
# ============================================================================

@dataclass
class Feature:
    """Feature with prioritization attributes."""

    name: str
    customer_value: float
    business_value: float
    confidence: float
    effort: float
    risk: float = 0.0

    def rice_score(self, reach: float) -> float:
        """
        RICE-style score:

            Reach × Impact × Confidence / Effort

        Impact is represented here by a weighted customer/business value.
        """

        if reach < 0:
            raise ValueError("Reach cannot be negative.")

        impact = (
            self.customer_value * 0.6
            + self.business_value * 0.4
        )

        return reach * impact * self.confidence / max(self.effort, 0.1)

    def value_effort_score(self) -> float:
        """Simple value divided by effort heuristic."""

        value = self.customer_value + self.business_value
        return value / max(self.effort, 0.1)


def prioritize_features(features: list[Feature], reach: float) -> list[dict]:
    """Rank features using a RICE-style score."""

    ranked = []

    for feature in features:
        ranked.append(
            {
                "feature": feature.name,
                "rice": round(feature.rice_score(reach), 2),
                "value_effort": round(feature.value_effort_score(), 2),
            }
        )

    return sorted(ranked, key=lambda item: item["rice"], reverse=True)


def define_mvp(features: list[Feature], maximum_effort: float) -> list[Feature]:
    """
    Create a simple MVP selection.

    Features are considered in value-to-effort order. This is a teaching
    heuristic rather than a replacement for strategic product judgment.
    """

    if maximum_effort <= 0:
        raise ValueError("Maximum effort must be positive.")

    selected: list[Feature] = []
    consumed_effort = 0.0

    for feature in sorted(
        features,
        key=lambda item: item.value_effort_score(),
        reverse=True,
    ):
        if consumed_effort + feature.effort <= maximum_effort:
            selected.append(feature)
            consumed_effort += feature.effort

    return selected


# ============================================================================
# 7. PRODUCT REQUIREMENTS
# ============================================================================

@dataclass
class Requirement:
    """Functional or non-functional product requirement."""

    identifier: str
    description: str
    requirement_type: str
    priority: str
    acceptance_criteria: list[str]

    def is_complete(self) -> bool:
        """Basic quality check for a requirement."""

        valid_types = {"functional", "non-functional"}
        valid_priorities = {"must", "should", "could", "wont"}

        return (
            bool(self.identifier.strip())
            and bool(self.description.strip())
            and self.requirement_type in valid_types
            and self.priority in valid_priorities
            and bool(self.acceptance_criteria)
        )


def create_user_story(
    role: str,
    action: str,
    benefit: str,
) -> str:
    """Create a standard user story."""

    return f"As a {role}, I want to {action}, so that {benefit}."


# ============================================================================
# 8. DEVELOPMENT
# ============================================================================

@dataclass
class Sprint:
    """Simple sprint representation."""

    number: int
    goal: str
    planned_points: int
    completed_points: int = 0

    @property
    def velocity(self) -> int:
        return self.completed_points


def calculate_average_velocity(sprints: list[Sprint]) -> float:
    """Calculate average completed story points."""

    if not sprints:
        return 0.0

    return mean(sprint.completed_points for sprint in sprints)


def estimate_sprints(
    remaining_story_points: int,
    average_velocity: float,
) -> int:
    """Estimate the number of sprints required."""

    if remaining_story_points < 0:
        raise ValueError("Remaining points cannot be negative.")

    if average_velocity <= 0:
        raise ValueError("Average velocity must be positive.")

    return math.ceil(remaining_story_points / average_velocity)


def calculate_burndown(
    total_work: int,
    completed_by_period: list[int],
) -> list[int]:
    """
    Return remaining work after each period.

    Values are clamped at zero because work cannot become negative.
    """

    if total_work < 0:
        raise ValueError("Total work cannot be negative.")

    remaining = total_work
    result = []

    for completed in completed_by_period:
        if completed < 0:
            raise ValueError("Completed work cannot be negative.")

        remaining = max(0, remaining - completed)
        result.append(remaining)

    return result


# ============================================================================
# 9. QUALITY ASSURANCE
# ============================================================================

@dataclass
class Defect:
    """Software/product defect record."""

    identifier: str
    severity: str
    discovered_stage: LifecycleStage
    resolved: bool = False


def defect_escape_rate(
    defects_found_after_launch: int,
    total_defects: int,
) -> float:
    """Calculate the percentage of defects escaping into production."""

    if total_defects < 0 or defects_found_after_launch < 0:
        raise ValueError("Defect counts cannot be negative.")

    if defects_found_after_launch > total_defects:
        raise ValueError("Escaped defects cannot exceed total defects.")

    if total_defects == 0:
        return 0.0

    return defects_found_after_launch / total_defects


def test_acceptance_criteria(
    criteria: list[tuple[str, bool]],
) -> dict:
    """Evaluate whether all acceptance criteria pass."""

    results = {description: passed for description, passed in criteria}

    return {
        "criteria": results,
        "all_passed": all(results.values()) if results else False,
    }


# ============================================================================
# 10. RELEASE MANAGEMENT
# ============================================================================

@dataclass
class Release:
    """Product release record."""

    version: str
    release_date: str
    features: list[str]
    known_issues: list[str]
    rollback_plan: str

    def is_production_ready(self) -> bool:
        """Basic release-readiness gate."""

        return bool(
            self.version
            and self.release_date
            and self.features
            and self.rollback_plan
            and not self.critical_known_issue
        )

    @property
    def critical_known_issue(self) -> bool:
        """Treat a specifically labeled issue as a release blocker."""

        return any(
            issue.strip().lower().startswith("critical:")
            for issue in self.known_issues
        )


# ============================================================================
# 11. LAUNCH
# ============================================================================

@dataclass
class LaunchPlan:
    """Go-to-market launch plan."""

    product_name: str
    target_segment: str
    positioning: str
    channels: list[str]
    pricing: float
    launch_goal: int
    support_capacity: int


def launch_readiness_score(
    product_ready: bool,
    support_ready: bool,
    analytics_ready: bool,
    marketing_ready: bool,
    rollback_ready: bool,
) -> float:
    """Calculate a simple five-dimension readiness score."""

    checks = [
        product_ready,
        support_ready,
        analytics_ready,
        marketing_ready,
        rollback_ready,
    ]

    return sum(checks) / len(checks)


def calculate_trial_to_paid(
    trials: int,
    paid_customers: int,
) -> float:
    """Calculate trial-to-paid conversion."""

    return calculate_conversion_rate(paid_customers, trials)


# ============================================================================
# 12. LAUNCH METRICS
# ============================================================================

@dataclass
class FunnelMetrics:
    """Basic acquisition funnel metrics."""

    visitors: int
    signups: int
    activated: int
    paying: int

    def rates(self) -> dict[str, float]:
        return {
            "visitor_to_signup": calculate_conversion_rate(
                self.signups,
                self.visitors,
            ),
            "signup_to_activation": calculate_conversion_rate(
                self.activated,
                self.signups,
            ),
            "activation_to_paid": calculate_conversion_rate(
                self.paying,
                self.activated,
            ),
            "visitor_to_paid": calculate_conversion_rate(
                self.paying,
                self.visitors,
            ),
        }


# ============================================================================
# 13. ACTIVATION
# ============================================================================

def calculate_activation_rate(
    activated_users: int,
    new_users: int,
) -> float:
    """Calculate activation rate."""

    return calculate_conversion_rate(activated_users, new_users)


def calculate_dau_mau_ratio(
    daily_active_users: int,
    monthly_active_users: int,
) -> float:
    """
    Calculate DAU/MAU, commonly used as an engagement indicator.

    It should not be interpreted as a universal quality score because usage
    patterns differ substantially by product category.
    """

    if daily_active_users < 0 or monthly_active_users < 0:
        raise ValueError("User counts cannot be negative.")

    if daily_active_users > monthly_active_users:
        raise ValueError("DAU cannot exceed MAU under this simplified model.")

    if monthly_active_users == 0:
        return 0.0

    return daily_active_users / monthly_active_users


# ============================================================================
# 14. GROWTH
# ============================================================================

def compound_growth(
    initial_value: float,
    growth_rate: float,
    periods: int,
) -> float:
    """Calculate compounded growth."""

    if initial_value < 0:
        raise ValueError("Initial value cannot be negative.")

    if periods < 0:
        raise ValueError("Periods cannot be negative.")

    return initial_value * ((1 + growth_rate) ** periods)


def growth_rate(
    old_value: float,
    new_value: float,
) -> float:
    """Calculate percentage growth."""

    if old_value < 0 or new_value < 0:
        raise ValueError("Values cannot be negative.")

    if old_value == 0:
        return math.inf if new_value > 0 else 0.0

    return (new_value - old_value) / old_value


def calculate_monthly_recurring_revenue(
    customers: int,
    average_revenue_per_customer: float,
) -> float:
    """Calculate MRR."""

    if customers < 0 or average_revenue_per_customer < 0:
        raise ValueError("Inputs cannot be negative.")

    return customers * average_revenue_per_customer


def calculate_annual_recurring_revenue(mrr: float) -> float:
    """Convert monthly recurring revenue to annual recurring revenue."""

    if mrr < 0:
        raise ValueError("MRR cannot be negative.")

    return mrr * 12


# ============================================================================
# 15. UNIT ECONOMICS
# ============================================================================

def calculate_cac(
    sales_and_marketing_cost: float,
    new_customers: int,
) -> float:
    """Calculate Customer Acquisition Cost."""

    if sales_and_marketing_cost < 0:
        raise ValueError("Cost cannot be negative.")

    if new_customers < 0:
        raise ValueError("Customer count cannot be negative.")

    if new_customers == 0:
        return math.inf

    return sales_and_marketing_cost / new_customers


def calculate_arpu(
    revenue: float,
    active_customers: int,
) -> float:
    """Calculate Average Revenue Per User/Customer."""

    if revenue < 0 or active_customers < 0:
        raise ValueError("Inputs cannot be negative.")

    if active_customers == 0:
        return 0.0

    return revenue / active_customers


def calculate_ltv(
    average_revenue_per_customer: float,
    gross_margin: float,
    monthly_churn: float,
) -> float:
    """
    Simplified subscription LTV model.

    LTV ≈ ARPU × gross margin / monthly churn

    This is a useful heuristic, not a universal financial valuation model.
    """

    if average_revenue_per_customer < 0:
        raise ValueError("ARPU cannot be negative.")

    if not 0 <= gross_margin <= 1:
        raise ValueError("Gross margin must be between 0 and 1.")

    if not 0 <= monthly_churn <= 1:
        raise ValueError("Churn must be between 0 and 1.")

    if monthly_churn == 0:
        return math.inf

    return average_revenue_per_customer * gross_margin / monthly_churn


def ltv_to_cac_ratio(ltv: float, cac: float) -> float:
    """Calculate LTV/CAC."""

    if ltv < 0 or cac < 0:
        raise ValueError("LTV and CAC cannot be negative.")

    if cac == 0:
        return math.inf

    return ltv / cac


def cac_payback_months(
    cac: float,
    monthly_revenue_per_customer: float,
    gross_margin: float,
) -> float:
    """Estimate CAC payback period."""

    if cac < 0 or monthly_revenue_per_customer < 0:
        raise ValueError("Inputs cannot be negative.")

    if not 0 <= gross_margin <= 1:
        raise ValueError("Gross margin must be between 0 and 1.")

    monthly_gross_profit = monthly_revenue_per_customer * gross_margin

    if monthly_gross_profit == 0:
        return math.inf

    return cac / monthly_gross_profit


# ============================================================================
# 16. RETENTION AND COHORT ANALYSIS
# ============================================================================

@dataclass
class Cohort:
    """Simple user cohort."""

    name: str
    starting_users: int
    retained_by_month: list[int]

    def retention_curve(self) -> list[float]:
        return [
            calculate_retention_rate(
                retained,
                self.starting_users,
            )
            for retained in self.retained_by_month
        ]


def average_cohort_retention(cohorts: list[Cohort]) -> list[float]:
    """Average retention by cohort month."""

    if not cohorts:
        return []

    maximum_months = max(len(cohort.retained_by_month) for cohort in cohorts)
    result = []

    for month in range(maximum_months):
        observations = [
            cohort.retention_curve()[month]
            for cohort in cohorts
            if month < len(cohort.retained_by_month)
        ]

        result.append(mean(observations) if observations else 0.0)

    return result


# ============================================================================
# 17. CHURN ANALYSIS
# ============================================================================

@dataclass
class ChurnReason:
    reason: str
    customers: int


def churn_distribution(
    reasons: list[ChurnReason],
) -> dict[str, float]:
    """Calculate each churn reason's share of churn."""

    total = sum(reason.customers for reason in reasons)

    if total == 0:
        return {reason.reason: 0.0 for reason in reasons}

    return {
        reason.reason: reason.customers / total
        for reason in reasons
    }


def net_revenue_retention(
    starting_revenue: float,
    expansion: float,
    contraction: float,
    churn: float,
) -> float:
    """
    Calculate Net Revenue Retention.

    NRR = (starting revenue + expansion - contraction - churn)
          / starting revenue
    """

    values = [
        starting_revenue,
        expansion,
        contraction,
        churn,
    ]

    if any(value < 0 for value in values):
        raise ValueError("Revenue values cannot be negative.")

    if starting_revenue == 0:
        return 0.0

    ending_revenue = (
        starting_revenue
        + expansion
        - contraction
        - churn
    )

    return ending_revenue / starting_revenue


# ============================================================================
# 18. GROWTH LOOPS
# ============================================================================

@dataclass
class GrowthLoop:
    """
    Generic growth-loop model.

    Example:
        User creates content
            -> content is shared
            -> new users see content
            -> new users sign up
            -> new users create content
    """

    name: str
    input_users: int
    actions_per_user: float
    invite_rate: float
    conversion_rate: float

    def generated_users(self) -> float:
        return (
            self.input_users
            * self.actions_per_user
            * self.invite_rate
            * self.conversion_rate
        )


def simulate_growth_loop(
    initial_users: int,
    loop: GrowthLoop,
    generations: int,
) -> list[float]:
    """Simulate users generated by repeated growth-loop generations."""

    if initial_users < 0:
        raise ValueError("Initial users cannot be negative.")

    if generations < 0:
        raise ValueError("Generations cannot be negative.")

    population = float(initial_users)
    result = [population]

    for _ in range(generations):
        current_loop = GrowthLoop(
            name=loop.name,
            input_users=int(population),
            actions_per_user=loop.actions_per_user,
            invite_rate=loop.invite_rate,
            conversion_rate=loop.conversion_rate,
        )

        population = current_loop.generated_users()
        result.append(population)

    return result


# ============================================================================
# 19. PRICING
# ============================================================================

@dataclass
class PricingPlan:
    """Pricing tier."""

    name: str
    monthly_price: float
    included_users: int
    target_segment: str


def calculate_revenue_mix(
    plans: list[PricingPlan],
    customer_distribution: dict[str, int],
) -> dict[str, float]:
    """Calculate revenue by pricing plan."""

    revenue = {}

    for plan in plans:
        customers = customer_distribution.get(plan.name, 0)

        if customers < 0:
            raise ValueError("Customer counts cannot be negative.")

        revenue[plan.name] = customers * plan.monthly_price

    return revenue


def price_sensitivity(
    base_demand: float,
    price_change_percentage: float,
    elasticity: float,
) -> float:
    """
    Simple demand elasticity model.

    Demand change = elasticity × price change.

    Elasticity is typically negative for conventional demand curves.
    """

    if base_demand < 0:
        raise ValueError("Demand cannot be negative.")

    demand_change = elasticity * price_change_percentage
    return max(0.0, base_demand * (1 + demand_change / 100))


# ============================================================================
# 20. MATURITY
# ============================================================================

def calculate_market_share(
    product_sales: float,
    total_market_sales: float,
) -> float:
    """Calculate market share."""

    if product_sales < 0 or total_market_sales < 0:
        raise ValueError("Sales cannot be negative.")

    if product_sales > total_market_sales:
        raise ValueError("Product sales cannot exceed total market sales.")

    if total_market_sales == 0:
        return 0.0

    return product_sales / total_market_sales


def calculate_gross_margin(
    revenue: float,
    cost_of_goods_sold: float,
) -> float:
    """Calculate gross margin."""

    if revenue < 0 or cost_of_goods_sold < 0:
        raise ValueError("Values cannot be negative.")

    if cost_of_goods_sold > revenue:
        raise ValueError("COGS cannot exceed revenue in this simplified model.")

    if revenue == 0:
        return 0.0

    return (revenue - cost_of_goods_sold) / revenue


def calculate_operating_margin(
    revenue: float,
    cogs: float,
    operating_expenses: float,
) -> float:
    """Calculate operating margin."""

    if min(revenue, cogs, operating_expenses) < 0:
        raise ValueError("Values cannot be negative.")

    if revenue == 0:
        return 0.0

    operating_profit = revenue - cogs - operating_expenses
    return operating_profit / revenue


# ============================================================================
# 21. MATURITY STRATEGIES
# ============================================================================

def classify_maturity_strategy(
    growth_rate_value: float,
    market_share: float,
    profitability: float,
) -> str:
    """
    Recommend a broad strategic posture.

    This is intentionally simplified. Actual strategic decisions require
    competitive, customer, financial, technological, and organizational data.
    """

    if growth_rate_value > 0.15 and market_share < 0.20:
        return "INVEST FOR GROWTH"

    if growth_rate_value > 0.05 and profitability > 0:
        return "OPTIMIZE AND EXPAND"

    if growth_rate_value <= 0.05 and profitability > 0:
        return "DEFEND AND HARVEST"

    return "REASSESS STRATEGIC ROLE"


# ============================================================================
# 22. DECLINE
# ============================================================================

@dataclass
class DeclineSignal:
    """Signal that may indicate product decline."""

    metric: str
    current: float
    previous: float
    direction: str

    def deterioration(self) -> float:
        """Return the magnitude of deterioration as a positive fraction."""

        if self.previous == 0:
            return 0.0

        raw_change = (self.current - self.previous) / abs(self.previous)

        if self.direction == "higher_is_better":
            return max(0.0, -raw_change)

        if self.direction == "lower_is_better":
            return max(0.0, raw_change)

        raise ValueError("Direction must identify which direction is better.")


def decline_risk_score(signals: list[DeclineSignal]) -> float:
    """Average normalized deterioration across signals."""

    if not signals:
        return 0.0

    values = [signal.deterioration() for signal in signals]
    return min(1.0, mean(values))


def determine_decline_response(
    demand_change: float,
    profitability: float,
    strategic_fit: float,
    customer_dependency: float,
) -> str:
    """
    Select a broad response to decline.

    Possible responses:
        Revitalize
        Harvest
        Divest
        Retire

    The model is illustrative, not a substitute for business analysis.
    """

    if demand_change > 0:
        return "Revitalize"

    if profitability > 0 and strategic_fit > 0.5:
        return "Harvest"

    if profitability < 0 and strategic_fit > 0.5:
        return "Divest or reposition"

    if customer_dependency > 0.7:
        return "Plan controlled retirement with migration"

    return "Retire"


# ============================================================================
# 23. RETIREMENT
# ============================================================================

@dataclass
class RetirementPlan:
    """Controlled product-retirement plan."""

    product_name: str
    announcement_date: str
    end_of_sale_date: str
    end_of_support_date: str
    migration_plan: str
    data_export_available: bool
    communication_channels: list[str]
    owner: str

    def readiness_checks(self) -> dict[str, bool]:
        """Check important retirement responsibilities."""

        return {
            "timeline_defined": bool(
                self.announcement_date
                and self.end_of_sale_date
                and self.end_of_support_date
            ),
            "migration_plan_defined": bool(self.migration_plan.strip()),
            "data_export": self.data_export_available,
            "communications_defined": bool(self.communication_channels),
            "owner_defined": bool(self.owner.strip()),
        }

    def ready(self) -> bool:
        return all(self.readiness_checks().values())


def calculate_migration_completion(
    migrated_customers: int,
    eligible_customers: int,
) -> float:
    """Calculate migration completion rate."""

    return calculate_conversion_rate(
        migrated_customers,
        eligible_customers,
    )


def retirement_risk_score(
    remaining_customers: int,
    critical_customers: int,
    unresolved_dependencies: int,
    data_export_ready: bool,
) -> float:
    """
    Estimate retirement risk.

    This combines operational indicators into a bounded score.
    """

    if min(
        remaining_customers,
        critical_customers,
        unresolved_dependencies,
    ) < 0:
        raise ValueError("Counts cannot be negative.")

    if remaining_customers == 0:
        customer_risk = 0.0
    else:
        customer_risk = critical_customers / remaining_customers

    dependency_risk = min(1.0, unresolved_dependencies / 10)
    export_risk = 0.0 if data_export_ready else 0.3

    return min(
        1.0,
        customer_risk * 0.5
        + dependency_risk * 0.3
        + export_risk * 0.2,
    )


# ============================================================================
# 24. PRODUCT PORTFOLIO MANAGEMENT
# ============================================================================

@dataclass
class PortfolioProduct:
    """Product-level portfolio record."""

    name: str
    stage: LifecycleStage
    growth_rate: float
    market_share: float
    profitability: float


def portfolio_posture(product: PortfolioProduct) -> str:
    """
    Determine a broad investment posture.

    The lifecycle stage matters because identical metrics can imply different
    actions at different points in the lifecycle.
    """

    if product.stage in {
        LifecycleStage.DISCOVERY,
        LifecycleStage.VALIDATION,
    }:
        return "LEARN AND VALIDATE"

    if product.stage == LifecycleStage.DEVELOPMENT:
        return "BUILD SELECTIVELY"

    if product.stage == LifecycleStage.LAUNCH:
        return "ESTABLISH PRODUCT-MARKET FIT"

    if product.stage == LifecycleStage.GROWTH:
        return "INVEST FOR SCALE"

    if product.stage == LifecycleStage.MATURITY:
        if product.profitability > 0:
            return "OPTIMIZE AND DEFEND"
        return "RESTRUCTURE OR REPOSITION"

    if product.stage == LifecycleStage.DECLINE:
        return "HARVEST, REPOSITION, DIVEST, OR RETIRE"

    return "CONTROLLED RETIREMENT"


# ============================================================================
# 25. PRODUCT-MARKET FIT
# ============================================================================

@dataclass
class PMFSignals:
    """Collection of product-market-fit signals."""

    retention: float
    organic_growth: float
    customer_satisfaction: float
    repeat_usage: float
    willingness_to_pay: float


def pmf_signal_score(signals: PMFSignals) -> float:
    """Calculate a weighted PMF signal score."""

    values = [
        signals.retention,
        signals.organic_growth,
        signals.customer_satisfaction,
        signals.repeat_usage,
        signals.willingness_to_pay,
    ]

    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("PMF signals must be between 0 and 1.")

    weights = [0.30, 0.20, 0.15, 0.20, 0.15]

    return sum(value * weight for value, weight in zip(values, weights))


# ============================================================================
# 26. EXPERIMENTATION AND A/B TESTING
# ============================================================================

@dataclass
class ExperimentVariant:
    name: str
    visitors: int
    conversions: int

    @property
    def conversion_rate(self) -> float:
        return calculate_conversion_rate(
            self.conversions,
            self.visitors,
        )


def absolute_conversion_lift(
    control: ExperimentVariant,
    treatment: ExperimentVariant,
) -> float:
    """Calculate absolute conversion-rate lift."""

    return treatment.conversion_rate - control.conversion_rate


def relative_conversion_lift(
    control: ExperimentVariant,
    treatment: ExperimentVariant,
) -> float:
    """Calculate relative conversion lift."""

    if control.conversion_rate == 0:
        return math.inf if treatment.conversion_rate > 0 else 0.0

    return (
        treatment.conversion_rate - control.conversion_rate
    ) / control.conversion_rate


# ============================================================================
# 27. STATISTICAL APPROXIMATION FOR TWO PROPORTIONS
# ============================================================================

def two_proportion_z_test(
    control: ExperimentVariant,
    treatment: ExperimentVariant,
) -> tuple[float, float]:
    """
    Approximate two-proportion z-test.

    Returns:
        z_score, approximate two-sided p-value

    This implementation uses the normal approximation and is appropriate only
    when sample sizes and expected counts are sufficiently large.

    It is included to demonstrate the statistical reasoning behind product
    experimentation. Production experimentation should account for experiment
    design, randomization, power, sequential testing, segmentation, and
    multiple-comparison issues.
    """

    if control.visitors <= 0 or treatment.visitors <= 0:
        raise ValueError("Both variants require positive visitor counts.")

    p1 = control.conversion_rate
    p2 = treatment.conversion_rate

    pooled = (
        control.conversions + treatment.conversions
    ) / (
        control.visitors + treatment.visitors
    )

    standard_error = math.sqrt(
        pooled
        * (1 - pooled)
        * (
            1 / control.visitors
            + 1 / treatment.visitors
        )
    )

    if standard_error == 0:
        return 0.0, 1.0

    z = (p2 - p1) / standard_error

    # Normal-distribution CDF using erf from the standard library.
    cdf = 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))
    p_value = 2 * (1 - cdf)

    return z, p_value


# ============================================================================
# 28. PRODUCT ANALYTICS
# ============================================================================

@dataclass
class ProductMetrics:
    """Monthly product metrics."""

    month: str
    customers: int
    mau: int
    revenue: float
    churn_rate: float
    cac: float
    gross_margin: float


def metric_change(
    previous: float,
    current: float,
) -> float:
    """Generic percentage-change function."""

    return growth_rate(previous, current)


def analyze_metric_trend(
    values: list[float],
) -> dict[str, float]:
    """Return basic descriptive statistics for a metric series."""

    if not values:
        return {
            "minimum": 0.0,
            "maximum": 0.0,
            "mean": 0.0,
            "median": 0.0,
        }

    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
    }


# ============================================================================
# 29. PRODUCT HEALTH SCORE
# ============================================================================

@dataclass
class ProductHealth:
    """Weighted product health score."""

    activation: float
    retention: float
    revenue_growth: float
    gross_margin: float
    satisfaction: float

    def score(self) -> float:
        """
        Calculate a weighted score.

        Inputs are expected as normalized values between 0 and 1.
        """

        metrics = [
            self.activation,
            self.retention,
            self.revenue_growth,
            self.gross_margin,
            self.satisfaction,
        ]

        if any(not 0 <= metric <= 1 for metric in metrics):
            raise ValueError("Health metrics must be between 0 and 1.")

        weights = {
            "activation": 0.20,
            "retention": 0.30,
            "revenue_growth": 0.20,
            "gross_margin": 0.15,
            "satisfaction": 0.15,
        }

        return (
            self.activation * weights["activation"]
            + self.retention * weights["retention"]
            + self.revenue_growth * weights["revenue_growth"]
            + self.gross_margin * weights["gross_margin"]
            + self.satisfaction * weights["satisfaction"]
        )


# ============================================================================
# 30. PRODUCT DECISION FRAMEWORK
# ============================================================================

def product_decision(
    stage: LifecycleStage,
    evidence_strength: float,
    customer_value: float,
    business_value: float,
    operational_risk: float,
) -> str:
    """
    Produce a broad product decision.

    This function demonstrates a decision framework rather than an automatic
    substitute for product-management judgment.
    """

    for value in (
        evidence_strength,
        customer_value,
        business_value,
        operational_risk,
    ):
        if not 0 <= value <= 1:
            raise ValueError("Decision inputs must be between 0 and 1.")

    if stage == LifecycleStage.DISCOVERY:
        if evidence_strength < 0.4:
            return "Continue problem discovery."
        return "Advance the strongest opportunity to validation."

    if stage == LifecycleStage.VALIDATION:
        if evidence_strength < 0.5:
            return "Revise hypothesis or stop the concept."
        return "Proceed toward MVP development."

    if stage == LifecycleStage.DEVELOPMENT:
        if operational_risk > 0.7:
            return "Resolve critical technical or operational risks."
        return "Continue toward launch readiness."

    if stage == LifecycleStage.LAUNCH:
        if customer_value < 0.5:
            return "Improve product experience before scaling acquisition."
        return "Optimize activation and early retention."

    if stage == LifecycleStage.GROWTH:
        if business_value > 0.6 and customer_value > 0.6:
            return "Invest in scalable growth."
        return "Improve product-market fit before aggressive scaling."

    if stage == LifecycleStage.MATURITY:
        if business_value > 0.6:
            return "Optimize profitability and defend the position."
        return "Reposition, differentiate, or reduce investment."

    if stage == LifecycleStage.DECLINE:
        if customer_value > 0.7:
            return "Investigate revitalization or migration to a successor."
        return "Evaluate harvest, divestment, or retirement."

    return "Execute controlled retirement."


# ============================================================================
# 31. EDGE CASES AND SPECIAL CONDITIONS
# ============================================================================

def classify_lifecycle_ambiguity(
    growth_rate_value: float,
    revenue_growth: float,
    user_growth: float,
    profitability: float,
) -> list[str]:
    """
    Identify situations where a product may not fit a simple lifecycle label.

    Products can grow in one dimension while declining in another.
    """

    signals = []

    if growth_rate_value > 0 and profitability < 0:
        signals.append("Growth without profitability")

    if user_growth > 0 and revenue_growth < 0:
        signals.append("User growth without revenue growth")

    if user_growth < 0 and revenue_growth > 0:
        signals.append("Revenue growth despite user decline")

    if growth_rate_value == 0 and profitability > 0:
        signals.append("Stable economics")

    if not signals:
        signals.append("No major lifecycle ambiguity detected")

    return signals


def compare_lifecycle_stages(
    first: LifecycleStage,
    second: LifecycleStage,
) -> str:
    """Explain the primary distinction between two lifecycle stages."""

    distinctions = {
        frozenset(
            {LifecycleStage.DISCOVERY, LifecycleStage.VALIDATION}
        ): "Discovery searches for problems and opportunities; validation tests specific hypotheses.",
        frozenset(
            {LifecycleStage.VALIDATION, LifecycleStage.DEVELOPMENT}
        ): "Validation tests whether to build; development determines how to build reliably.",
        frozenset(
            {LifecycleStage.DEVELOPMENT, LifecycleStage.LAUNCH}
        ): "Development prepares the product; launch introduces it to the market.",
        frozenset(
            {LifecycleStage.LAUNCH, LifecycleStage.GROWTH}
        ): "Launch establishes initial adoption; growth seeks repeatable scalable expansion.",
        frozenset(
            {LifecycleStage.GROWTH, LifecycleStage.MATURITY}
        ): "Growth prioritizes expansion; maturity prioritizes optimization and defense.",
        frozenset(
            {LifecycleStage.MATURITY, LifecycleStage.DECLINE}
        ): "Maturity is stable optimization; decline requires strategic response to weakening conditions.",
        frozenset(
            {LifecycleStage.DECLINE, LifecycleStage.RETIREMENT}
        ): "Decline is a condition; retirement is an intentional business decision.",
    }

    key = frozenset({first, second})

    if key in distinctions:
        return distinctions[key]

    if first == second:
        return "The two inputs represent the same lifecycle stage."

    return "These stages differ in their dominant product-management objectives."


# ============================================================================
# 32. SECURITY AND PRIVACY IN THE PRODUCT LIFECYCLE
# ============================================================================

@dataclass
class SecurityControl:
    """Security control mapped to a lifecycle phase."""

    stage: LifecycleStage
    control: str
    risk_reduced: str


def security_by_lifecycle_stage() -> list[SecurityControl]:
    """Return representative security practices across the lifecycle."""

    return [
        SecurityControl(
            LifecycleStage.DISCOVERY,
            "Identify security and privacy requirements early.",
            "Building a product that cannot satisfy required trust constraints.",
        ),
        SecurityControl(
            LifecycleStage.VALIDATION,
            "Validate data-handling assumptions and threat scenarios.",
            "Invalid assumptions about sensitive data or attack surfaces.",
        ),
        SecurityControl(
            LifecycleStage.DEVELOPMENT,
            "Use secure coding, dependency management, access control, and testing.",
            "Implementation vulnerabilities.",
        ),
        SecurityControl(
            LifecycleStage.LAUNCH,
            "Verify logging, monitoring, incident response, and configuration.",
            "Operational security failures.",
        ),
        SecurityControl(
            LifecycleStage.GROWTH,
            "Scale identity, authorization, abuse prevention, and observability.",
            "Security weaknesses caused by scale.",
        ),
        SecurityControl(
            LifecycleStage.MATURITY,
            "Patch, rotate secrets, review permissions, and reassess threats.",
            "Security debt and accumulated exposure.",
        ),
        SecurityControl(
            LifecycleStage.DECLINE,
            "Maintain security despite reduced investment.",
            "Neglect of legacy security risks.",
        ),
        SecurityControl(
            LifecycleStage.RETIREMENT,
            "Delete, export, archive, or migrate data according to obligations.",
            "Data exposure after product shutdown.",
        ),
    ]


# ============================================================================
# 33. TECHNICAL DEBT AND PRODUCT DEBT
# ============================================================================

@dataclass
class DebtItem:
    """Product or technical debt item."""

    description: str
    impact: float
    urgency: float
    effort_to_fix: float

    def priority(self) -> float:
        return self.impact * self.urgency / max(self.effort_to_fix, 0.1)


def prioritize_debt(items: list[DebtItem]) -> list[DebtItem]:
    """Prioritize debt using impact, urgency, and effort."""

    return sorted(items, key=lambda item: item.priority(), reverse=True)


# ============================================================================
# 34. ROADMAP MANAGEMENT
# ============================================================================

@dataclass
class RoadmapItem:
    """Outcome-oriented roadmap item."""

    quarter: str
    objective: str
    success_metric: str
    target: float


def roadmap_quality_score(
    items: list[RoadmapItem],
) -> float:
    """
    Score whether roadmap items include useful outcome information.

    A high score means the roadmap contains objectives, metrics, and targets.
    """

    if not items:
        return 0.0

    complete = sum(
        bool(
            item.quarter.strip()
            and item.objective.strip()
            and item.success_metric.strip()
            and item.target >= 0
        )
        for item in items
    )

    return complete / len(items)


# ============================================================================
# 35. PRODUCT OPERATIONS
# ============================================================================

@dataclass
class Incident:
    """Production incident."""

    identifier: str
    severity: str
    affected_customers: int
    minutes_unavailable: int
    resolved: bool = False


def calculate_availability(
    total_minutes: int,
    unavailable_minutes: int,
) -> float:
    """Calculate service availability."""

    if total_minutes <= 0:
        raise ValueError("Total minutes must be positive.")

    if unavailable_minutes < 0:
        raise ValueError("Unavailable minutes cannot be negative.")

    if unavailable_minutes > total_minutes:
        raise ValueError("Unavailable time cannot exceed total time.")

    return 1 - unavailable_minutes / total_minutes


def incident_rate(
    incidents: list[Incident],
    customer_count: int,
) -> float:
    """Calculate incidents per customer."""

    if customer_count < 0:
        raise ValueError("Customer count cannot be negative.")

    if customer_count == 0:
        return 0.0

    return len(incidents) / customer_count


# ============================================================================
# 36. CHANGE MANAGEMENT
# ============================================================================

@dataclass
class ChangeRequest:
    """Change request for a product."""

    description: str
    customer_impact: float
    business_impact: float
    technical_risk: float
    urgency: float

    def score(self) -> float:
        """Prioritize change requests."""

        for value in (
            self.customer_impact,
            self.business_impact,
            self.technical_risk,
            self.urgency,
        ):
            if not 0 <= value <= 1:
                raise ValueError("Change metrics must be between 0 and 1.")

        return (
            self.customer_impact * 0.30
            + self.business_impact * 0.25
            + self.urgency * 0.25
            + (1 - self.technical_risk) * 0.20
        )


# ============================================================================
# 37. PRODUCT GOVERNANCE
# ============================================================================

@dataclass
class ProductDecisionRecord:
    """Decision record for important product choices."""

    decision: str
    context: str
    alternatives: list[str]
    rationale: str
    owner: str
    date: str

    def complete(self) -> bool:
        return all(
            [
                self.decision.strip(),
                self.context.strip(),
                self.alternatives,
                self.rationale.strip(),
                self.owner.strip(),
                self.date.strip(),
            ]
        )


# ============================================================================
# 38. END-TO-END PRODUCT LIFECYCLE SIMULATION
# ============================================================================

def simulate_flowboard_lifecycle() -> list[dict]:
    """
    Simulate the lifecycle of FlowBoard.

    The numerical values are intentionally illustrative. They demonstrate
    how priorities and metrics can change as a product moves through stages.
    """

    timeline = [
        {
            "stage": LifecycleStage.DISCOVERY.value,
            "customers": 0,
            "mau": 0,
            "revenue": 0,
            "churn": None,
            "primary_objective": "Find a high-value problem.",
        },
        {
            "stage": LifecycleStage.VALIDATION.value,
            "customers": 20,
            "mau": 15,
            "revenue": 0,
            "churn": 0.10,
            "primary_objective": "Test demand and willingness to pay.",
        },
        {
            "stage": LifecycleStage.DEVELOPMENT.value,
            "customers": 50,
            "mau": 35,
            "revenue": 500,
            "churn": 0.08,
            "primary_objective": "Build a reliable minimum viable product.",
        },
        {
            "stage": LifecycleStage.LAUNCH.value,
            "customers": 200,
            "mau": 160,
            "revenue": 3000,
            "churn": 0.07,
            "primary_objective": "Establish adoption and activation.",
        },
        {
            "stage": LifecycleStage.GROWTH.value,
            "customers": 2000,
            "mau": 1600,
            "revenue": 35000,
            "churn": 0.04,
            "primary_objective": "Scale acquisition and retention.",
        },
        {
            "stage": LifecycleStage.MATURITY.value,
            "customers": 8000,
            "mau": 6200,
            "revenue": 150000,
            "churn": 0.025,
            "primary_objective": "Optimize economics and defend market position.",
        },
        {
            "stage": LifecycleStage.DECLINE.value,
            "customers": 6200,
            "mau": 4200,
            "revenue": 112000,
            "churn": 0.055,
            "primary_objective": "Determine whether to revitalize or retire.",
        },
        {
            "stage": LifecycleStage.RETIREMENT.value,
            "customers": 500,
            "mau": 100,
            "revenue": 10000,
            "churn": 0.12,
            "primary_objective": "Migrate remaining customers safely.",
        },
    ]

    return timeline


def print_lifecycle_simulation(timeline: list[dict]) -> None:
    """Print the end-to-end lifecycle simulation."""

    print("\nEND-TO-END PRODUCT LIFECYCLE SIMULATION")
    print("-" * 100)

    for period in timeline:
        churn = (
            "N/A"
            if period["churn"] is None
            else f"{period['churn']:.1%}"
        )

        print(
            f"{period['stage']:12} | "
            f"Customers: {period['customers']:>5} | "
            f"MAU: {period['mau']:>5} | "
            f"Revenue: ${period['revenue']:>9,.0f} | "
            f"Churn: {churn:>6}"
        )
        print(f"    Objective: {period['primary_objective']}")


# ============================================================================
# 39. COMPLETE PRODUCT LIFECYCLE CHECKLIST
# ============================================================================

def lifecycle_checklist() -> dict[str, list[str]]:
    """Return stage-specific product-management checklists."""

    return {
        "Discovery": [
            "Define target customer",
            "Understand customer jobs and pain points",
            "Observe current behavior",
            "Identify alternatives and competitors",
            "Estimate market opportunity",
            "Document assumptions",
            "Identify major risks",
        ],
        "Validation": [
            "Write falsifiable hypotheses",
            "Define success metrics before testing",
            "Run customer experiments",
            "Validate willingness to pay",
            "Test solution desirability",
            "Assess feasibility",
            "Assess business viability",
            "Decide whether to proceed, pivot, or stop",
        ],
        "Development": [
            "Define product requirements",
            "Prioritize MVP scope",
            "Design user experience",
            "Implement product capabilities",
            "Test functionality",
            "Address security and privacy",
            "Instrument analytics",
            "Prepare support and operations",
        ],
        "Launch": [
            "Confirm product readiness",
            "Confirm operational readiness",
            "Prepare positioning",
            "Prepare pricing",
            "Prepare distribution channels",
            "Prepare support",
            "Monitor activation",
            "Monitor reliability and customer feedback",
        ],
        "Growth": [
            "Improve acquisition",
            "Improve activation",
            "Improve retention",
            "Develop scalable distribution",
            "Optimize pricing",
            "Monitor unit economics",
            "Expand customer segments carefully",
            "Scale infrastructure and support",
        ],
        "Maturity": [
            "Protect retention",
            "Improve efficiency",
            "Defend differentiation",
            "Manage technical debt",
            "Optimize pricing and packaging",
            "Expand strategically",
            "Maintain quality",
            "Assess future strategic options",
        ],
        "Decline": [
            "Identify causes of decline",
            "Separate temporary weakness from structural decline",
            "Assess revitalization opportunities",
            "Assess profitability",
            "Assess customer dependency",
            "Evaluate successor products",
            "Plan communication",
            "Choose harvest, reposition, divest, or retire",
        ],
        "Retirement": [
            "Define retirement timeline",
            "Communicate early",
            "Offer migration paths",
            "Provide data export where appropriate",
            "Resolve contractual obligations",
            "Securely handle remaining data",
            "Maintain necessary support",
            "Shut down systems safely",
            "Document lessons learned",
        ],
    }


# ============================================================================
# 40. COMMON PRODUCT-MANAGEMENT MISTAKES
# ============================================================================

def common_mistakes() -> list[dict[str, str]]:
    """Return common mistakes and better approaches."""

    return [
        {
            "mistake": "Starting with a solution instead of a problem.",
            "better": "Investigate customer problems and existing alternatives first.",
        },
        {
            "mistake": "Treating customer enthusiasm as proof of demand.",
            "better": "Measure behavior, commitment, usage, and willingness to pay.",
        },
        {
            "mistake": "Building too much before validation.",
            "better": "Test the riskiest assumptions with the smallest useful experiment.",
        },
        {
            "mistake": "Measuring vanity metrics.",
            "better": "Connect metrics to customer outcomes and business outcomes.",
        },
        {
            "mistake": "Confusing launch with product-market fit.",
            "better": "Treat launch as the beginning of market learning.",
        },
        {
            "mistake": "Scaling acquisition before fixing retention.",
            "better": "Investigate activation and retention before aggressive growth spending.",
        },
        {
            "mistake": "Ignoring unit economics during growth.",
            "better": "Track CAC, LTV, margins, payback, and retention.",
        },
        {
            "mistake": "Assuming mature products require no innovation.",
            "better": "Continuously improve differentiation, efficiency, and customer value.",
        },
        {
            "mistake": "Waiting too long to address decline.",
            "better": "Monitor leading indicators and evaluate strategic options early.",
        },
        {
            "mistake": "Treating retirement as merely switching off servers.",
            "better": "Plan migration, communication, contracts, data, support, and security.",
        },
    ]


# ============================================================================
# 41. CONCEPTUAL COMPARISONS
# ============================================================================

def lifecycle_comparison_table() -> list[dict[str, str]]:
    """Return important conceptual distinctions."""

    return [
        {
            "concept": "Discovery vs Validation",
            "distinction": (
                "Discovery explores problems and opportunities; validation "
                "tests explicit assumptions."
            ),
        },
        {
            "concept": "MVP vs Prototype",
            "distinction": (
                "A prototype is primarily a learning artifact; an MVP is a "
                "minimal real product intended to create measurable customer value."
            ),
        },
        {
            "concept": "Launch vs Growth",
            "distinction": (
                "Launch introduces the product; growth establishes repeatable "
                "and scalable acquisition and retention."
            ),
        },
        {
            "concept": "Growth vs Maturity",
            "distinction": (
                "Growth emphasizes expansion; maturity emphasizes optimization, "
                "defense, efficiency, and sustained value."
            ),
        },
        {
            "concept": "Decline vs Retirement",
            "distinction": (
                "Decline describes weakening product conditions; retirement is "
                "the deliberate decision to discontinue the product."
            ),
        },
        {
            "concept": "Feature Delivery vs Product Outcome",
            "distinction": (
                "Delivery measures what was built; outcome measures whether the "
                "customer or business problem improved."
            ),
        },
    ]


# ============================================================================
# 42. REAL-WORLD PRODUCT DECISION EXAMPLE
# ============================================================================

def analyze_flowboard_business_case() -> dict:
    """Analyze a fictional business case using lifecycle metrics."""

    revenue = 150_000
    cogs = 45_000
    operating_expenses = 70_000
    sales_marketing = 30_000
    new_customers = 600
    active_customers = 8_000
    arpu = calculate_arpu(revenue, active_customers)
    cac = calculate_cac(sales_marketing, new_customers)
    gross_margin = calculate_gross_margin(revenue, cogs)
    ltv = calculate_ltv(arpu, gross_margin, 0.025)
    ratio = ltv_to_cac_ratio(ltv, cac)
    payback = cac_payback_months(cac, arpu, gross_margin)

    return {
        "revenue": revenue,
        "gross_margin": gross_margin,
        "operating_margin": calculate_operating_margin(
            revenue,
            cogs,
            operating_expenses,
        ),
        "arpu": arpu,
        "cac": cac,
        "ltv": ltv,
        "ltv_cac": ratio,
        "cac_payback_months": payback,
    }


# ============================================================================
# 43. UNIT TESTS
# ============================================================================

class TestProductLifecycle(unittest.TestCase):
    """Basic automated tests for the educational implementations."""

    def test_conversion_rate(self) -> None:
        self.assertAlmostEqual(
            calculate_conversion_rate(20, 100),
            0.20,
        )

    def test_retention_rate(self) -> None:
        self.assertAlmostEqual(
            calculate_retention_rate(80, 100),
            0.80,
        )

    def test_churn_rate(self) -> None:
        self.assertAlmostEqual(
            calculate_churn_rate(10, 100),
            0.10,
        )

    def test_mrr(self) -> None:
        self.assertEqual(
            calculate_monthly_recurring_revenue(100, 20),
            2000,
        )

    def test_arr(self) -> None:
        self.assertEqual(
            calculate_annual_recurring_revenue(2000),
            24000,
        )

    def test_gross_margin(self) -> None:
        self.assertAlmostEqual(
            calculate_gross_margin(100, 40),
            0.60,
        )

    def test_market_share(self) -> None:
        self.assertAlmostEqual(
            calculate_market_share(25, 100),
            0.25,
        )

    def test_mvp_selection(self) -> None:
        features = [
            Feature("A", 9, 8, 0.9, 3),
            Feature("B", 5, 5, 0.8, 10),
        ]

        selected = define_mvp(features, maximum_effort=5)

        self.assertEqual([feature.name for feature in selected], ["A"])

    def test_release_blocked_by_critical_issue(self) -> None:
        release = Release(
            version="1.0.0",
            release_date="2026-09-01",
            features=["Feature A"],
            known_issues=["Critical: data corruption"],
            rollback_plan="Rollback to previous version",
        )

        self.assertFalse(release.is_production_ready())

    def test_release_can_be_ready(self) -> None:
        release = Release(
            version="1.0.0",
            release_date="2026-09-01",
            features=["Feature A"],
            known_issues=["Minor: cosmetic issue"],
            rollback_plan="Rollback to previous version",
        )

        self.assertTrue(release.is_production_ready())

    def test_lifecycle_stage_comparison(self) -> None:
        explanation = compare_lifecycle_stages(
            LifecycleStage.GROWTH,
            LifecycleStage.MATURITY,
        )

        self.assertIn("Growth", explanation)
        self.assertIn("maturity", explanation.lower())

    def test_retirement_readiness(self) -> None:
        plan = RetirementPlan(
            product_name="FlowBoard Legacy",
            announcement_date="2026-01-01",
            end_of_sale_date="2026-06-01",
            end_of_support_date="2027-01-01",
            migration_plan="Move users to FlowBoard Next",
            data_export_available=True,
            communication_channels=["email", "dashboard"],
            owner="Product Operations",
        )

        self.assertTrue(plan.ready())

    def test_health_score(self) -> None:
        health = ProductHealth(
            activation=0.8,
            retention=0.7,
            revenue_growth=0.6,
            gross_margin=0.75,
            satisfaction=0.8,
        )

        self.assertGreater(health.score(), 0.0)

    def test_invalid_conversion(self) -> None:
        with self.assertRaises(ValueError):
            calculate_conversion_rate(101, 100)


def run_tests() -> None:
    """Run the educational unit tests."""

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestProductLifecycle
    )
    result = unittest.TextTestRunner(verbosity=1).run(suite)

    print(
        f"\nTests run: {result.testsRun}, "
        f"failures: {len(result.failures)}, "
        f"errors: {len(result.errors)}"
    )


# ============================================================================
# 44. COMPREHENSIVE DEMONSTRATION
# ============================================================================

def run_demonstrations() -> None:
    """Run representative examples from the entire lifecycle."""

    explain_lifecycle()

    # ------------------------------------------------------------------------
    # Discovery example
    # ------------------------------------------------------------------------

    print("\nDISCOVERY EXAMPLE")
    print("-" * 80)

    interview = conduct_customer_interview(
        customer_name="Asha",
        role="Operations Manager",
        current_process="Spreadsheet-based task tracking",
        pain_point="Work is duplicated across teams and deadlines are missed.",
        frequency=9,
        impact=8,
    )

    print("Interview evidence:")
    for key, value in interview.items():
        print(f"  {key}: {value}")

    problem = CustomerProblem(
        customer_segment="Mid-sized operations teams",
        problem="Cross-team work is difficult to coordinate.",
        frequency=8,
        severity=8,
        current_alternative="Spreadsheets and chat messages",
        willingness_to_pay=7,
        evidence_count=18,
    )

    print(f"Problem score: {problem.problem_score:.2f}")

    persona = create_persona(
        name="Operations Manager",
        role="Manages cross-functional workflows",
        goals=[
            "Reduce missed deadlines",
            "Improve visibility",
            "Reduce manual coordination",
        ],
        frustrations=[
            "Scattered information",
            "Manual status updates",
            "Unclear ownership",
        ],
        behaviors=[
            "Uses spreadsheets",
            "Uses messaging platforms",
            "Creates recurring status reports",
        ],
    )

    print(f"Persona: {persona['name']}")
    print(
        "Value proposition:",
        build_value_proposition(
            "operations managers",
            "cross-team coordination problems",
            "FlowBoard",
            "clear ownership and workflow visibility",
        ),
    )

    # ------------------------------------------------------------------------
    # Market sizing
    # ------------------------------------------------------------------------

    print("\nMARKET SIZING")
    print("-" * 80)

    tam = estimate_tam(500_000, 600)
    sam = estimate_sam(tam, 20)
    som = estimate_som(sam, 5)

    print(f"TAM: ${tam:,.0f}")
    print(f"SAM: ${sam:,.0f}")
    print(f"SOM: ${som:,.0f}")

    competitors = [
        Competitor(
            "Competitor A",
            25,
            0.30,
            ["Brand", "Distribution"],
            ["Complex setup"],
        ),
        Competitor(
            "Competitor B",
            15,
            0.20,
            ["Low price"],
            ["Limited integrations"],
        ),
        Competitor(
            "Competitor C",
            40,
            0.10,
            ["Enterprise controls"],
            ["Expensive"],
        ),
    ]

    print("\nCompetitor analysis:")
    for row in compare_competitors(competitors):
        print(row)

    # ------------------------------------------------------------------------
    # Opportunity prioritization
    # ------------------------------------------------------------------------

    print("\nOPPORTUNITY PRIORITIZATION")
    print("-" * 80)

    opportunities = [
        Opportunity("Automated task assignment", 9, 8, 9, 8, 5),
        Opportunity("Custom themes", 4, 3, 3, 9, 2),
        Opportunity("Executive dashboard", 7, 8, 7, 7, 6),
        Opportunity("Calendar integration", 8, 7, 8, 8, 4),
    ]

    for name, score in prioritize_opportunities(opportunities):
        print(f"{name:30} score={score}")

    # ------------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------------

    print("\nVALIDATION")
    print("-" * 80)

    hypothesis = Hypothesis(
        statement="Teams that see a workflow demonstration will request a trial.",
        metric="trial_request_rate",
        threshold=0.10,
        observed_value=0.14,
    )

    print(f"Hypothesis supported: {hypothesis.is_supported()}")

    experiment = design_experiment(
        hypothesis=hypothesis.statement,
        target_metric=hypothesis.metric,
        success_threshold=hypothesis.threshold,
        duration_days=14,
    )

    print("Experiment design:")
    for key, value in experiment.items():
        print(f"  {key}: {value}")

    validation = run_fake_validation_experiment(
        sample_size=1000,
        expected_conversion=0.14,
    )

    print(
        f"Synthetic validation rate: "
        f"{validation.success_rate:.2%}"
    )
    print(validation.decision())

    # ------------------------------------------------------------------------
    # MVP
    # ------------------------------------------------------------------------

    print("\nMVP PRIORITIZATION")
    print("-" * 80)

    features = [
        Feature("Task management", 10, 9, 0.95, 8),
        Feature("Team dashboard", 8, 8, 0.90, 5),
        Feature("Calendar integration", 7, 7, 0.80, 6),
        Feature("Advanced reporting", 6, 6, 0.70, 8),
        Feature("Custom themes", 2, 2, 0.90, 2),
    ]

    ranked_features = prioritize_features(features, reach=1000)

    for item in ranked_features:
        print(
            f"{item['feature']:25} "
            f"RICE={item['rice']:>8} "
            f"Value/Effort={item['value_effort']:>6}"
        )

    mvp = define_mvp(features, maximum_effort=20)

    print("\nSelected MVP features:")
    for feature in mvp:
        print(f"  - {feature.name}")

    # ------------------------------------------------------------------------
    # Requirements
    # ------------------------------------------------------------------------

    print("\nREQUIREMENTS")
    print("-" * 80)

    story = create_user_story(
        "Operations Manager",
        "assign a task to a team member",
        "everyone knows who owns the work",
    )

    requirement = Requirement(
        identifier="REQ-001",
        description="Users must be able to assign tasks.",
        requirement_type="functional",
        priority="must",
        acceptance_criteria=[
            "A task can have one owner.",
            "The owner receives an in-app notification.",
            "The task displays the current owner.",
        ],
    )

    print(story)
    print(f"Requirement complete: {requirement.is_complete()}")

    # ------------------------------------------------------------------------
    # Development
    # ------------------------------------------------------------------------

    print("\nDEVELOPMENT PLANNING")
    print("-" * 80)

    sprints = [
        Sprint(1, "Core task model", 25, 22),
        Sprint(2, "Assignment workflow", 25, 24),
        Sprint(3, "Notifications", 30, 27),
        Sprint(4, "Dashboard", 30, 28),
    ]

    velocity = calculate_average_velocity(sprints)
    remaining = 110

    print(f"Average velocity: {velocity:.2f} points/sprint")
    print(
        f"Estimated sprints for {remaining} points: "
        f"{estimate_sprints(remaining, velocity)}"
    )

    burndown = calculate_burndown(
        110,
        [22, 24, 27, 28, 20],
    )

    print(f"Remaining work after periods: {burndown}")

    # ------------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------------

    print("\nQUALITY")
    print("-" * 80)

    criteria = [
        ("User can assign a task", True),
        ("Owner receives notification", True),
        ("Assignment appears in dashboard", True),
    ]

    acceptance = test_acceptance_criteria(criteria)
    print(f"Acceptance criteria passed: {acceptance['all_passed']}")

    escaped = defect_escape_rate(
        defects_found_after_launch=3,
        total_defects=40,
    )

    print(f"Defect escape rate: {escaped:.2%}")

    # ------------------------------------------------------------------------
    # Launch
    # ------------------------------------------------------------------------

    print("\nLAUNCH READINESS")
    print("-" * 80)

    launch = LaunchPlan(
        product_name="FlowBoard",
        target_segment="Mid-sized operations teams",
        positioning="A simple workflow system for cross-team execution.",
        channels=["Direct sales", "Content", "Partnerships"],
        pricing=20,
        launch_goal=500,
        support_capacity=1000,
    )

    readiness = launch_readiness_score(
        product_ready=True,
        support_ready=True,
        analytics_ready=True,
        marketing_ready=True,
        rollback_ready=True,
    )

    print(f"Launch readiness: {readiness:.0%}")
    print(f"Target segment: {launch.target_segment}")
    print(f"Launch price: ${launch.pricing}/month")

    funnel = FunnelMetrics(
        visitors=10_000,
        signups=1_500,
        activated=900,
        paying=180,
    )

    print("Launch funnel:")
    for name, rate in funnel.rates().items():
        print(f"  {name}: {rate:.2%}")

    # ------------------------------------------------------------------------
    # Growth
    # ------------------------------------------------------------------------

    print("\nGROWTH")
    print("-" * 80)

    customers = 2000
    arpu = 25

    mrr = calculate_monthly_recurring_revenue(customers, arpu)
    arr = calculate_annual_recurring_revenue(mrr)

    print(f"MRR: ${mrr:,.0f}")
    print(f"ARR: ${arr:,.0f}")

    print(
        "Monthly customer growth from 2,000 to 2,500:",
        f"{growth_rate(2000, 2500):.2%}",
    )

    loop = GrowthLoop(
        name="Collaborative invitation loop",
        input_users=1000,
        actions_per_user=3,
        invite_rate=0.15,
        conversion_rate=0.25,
    )

    print(
        f"Users generated by loop: "
        f"{loop.generated_users():.0f}"
    )

    print(
        "Loop simulation:",
        [
            round(value)
            for value in simulate_growth_loop(1000, loop, 4)
        ],
    )

    # ------------------------------------------------------------------------
    # Unit economics
    # ------------------------------------------------------------------------

    print("\nUNIT ECONOMICS")
    print("-" * 80)

    cac = calculate_cac(30_000, 600)
    arpu = calculate_arpu(150_000, 8000)
    margin = 0.70
    churn = 0.025
    ltv = calculate_ltv(arpu, margin, churn)

    print(f"CAC: ${cac:,.2f}")
    print(f"ARPU: ${arpu:,.2f}")
    print(f"LTV: ${ltv:,.2f}")
    print(f"LTV/CAC: {ltv_to_cac_ratio(ltv, cac):.2f}")
    print(
        f"CAC payback: "
        f"{cac_payback_months(cac, arpu, margin):.2f} months"
    )

    # ------------------------------------------------------------------------
    # Cohorts
    # ------------------------------------------------------------------------

    print("\nCOHORT RETENTION")
    print("-" * 80)

    cohorts = [
        Cohort("January", 1000, [900, 800, 750, 700]),
        Cohort("February", 1200, [1050, 920, 850, 780]),
        Cohort("March", 1100, [980, 860, 790, 720]),
    ]

    for cohort in cohorts:
        print(
            f"{cohort.name}: "
            + ", ".join(
                f"{value:.1%}"
                for value in cohort.retention_curve()
            )
        )

    average_retention = average_cohort_retention(cohorts)

    print(
        "Average retention: "
        + ", ".join(
            f"{value:.1%}"
            for value in average_retention
        )
    )

    # ------------------------------------------------------------------------
    # Churn
    # ------------------------------------------------------------------------

    print("\nCHURN ANALYSIS")
    print("-" * 80)

    churn_reasons = [
        ChurnReason("Missing integration", 40),
        ChurnReason("Price", 25),
        ChurnReason("Low usage", 20),
        ChurnReason("Switched competitor", 15),
    ]

    for reason, share in churn_distribution(churn_reasons).items():
        print(f"{reason:25} {share:.1%}")

    nrr = net_revenue_retention(
        starting_revenue=100_000,
        expansion=12_000,
        contraction=5_000,
        churn=8_000,
    )

    print(f"NRR: {nrr:.2%}")

    # ------------------------------------------------------------------------
    # Maturity
    # ------------------------------------------------------------------------

    print("\nMATURITY")
    print("-" * 80)

    market_share = calculate_market_share(
        product_sales=150,
        total_market_sales=1000,
    )

    gross_margin = calculate_gross_margin(
        revenue=150_000,
        cost_of_goods_sold=45_000,
    )

    operating_margin = calculate_operating_margin(
        revenue=150_000,
        cogs=45_000,
        operating_expenses=70_000,
    )

    print(f"Market share: {market_share:.1%}")
    print(f"Gross margin: {gross_margin:.1%}")
    print(f"Operating margin: {operating_margin:.1%}")

    strategy = classify_maturity_strategy(
        growth_rate_value=0.04,
        market_share=market_share,
        profitability=operating_margin,
    )

    print(f"Maturity strategy: {strategy}")

    # ------------------------------------------------------------------------
    # Experimentation
    # ------------------------------------------------------------------------

    print("\nA/B EXPERIMENT")
    print("-" * 80)

    control = ExperimentVariant(
        name="Control",
        visitors=10_000,
        conversions=1000,
    )

    treatment = ExperimentVariant(
        name="Treatment",
        visitors=10_000,
        conversions=1100,
    )

    print(f"Control conversion: {control.conversion_rate:.2%}")
    print(f"Treatment conversion: {treatment.conversion_rate:.2%}")
    print(
        f"Absolute lift: "
        f"{absolute_conversion_lift(control, treatment):.2%}"
    )
    print(
        f"Relative lift: "
        f"{relative_conversion_lift(control, treatment):.2%}"
    )

    z, p_value = two_proportion_z_test(control, treatment)

    print(f"Z-score: {z:.3f}")
    print(f"Approximate p-value: {p_value:.4f}")

    # ------------------------------------------------------------------------
    # Decline
    # ------------------------------------------------------------------------

    print("\nDECLINE")
    print("-" * 80)

    signals = [
        DeclineSignal(
            "Monthly active users",
            current=4200,
            previous=6200,
            direction="higher_is_better",
        ),
        DeclineSignal(
            "Revenue",
            current=112000,
            previous=150000,
            direction="higher_is_better",
        ),
        DeclineSignal(
            "Churn",
            current=0.055,
            previous=0.025,
            direction="lower_is_better",
        ),
    ]

    for signal in signals:
        print(
            f"{signal.metric:25} "
            f"deterioration={signal.deterioration():.1%}"
        )

    risk = decline_risk_score(signals)

    print(f"Decline risk score: {risk:.1%}")

    response = determine_decline_response(
        demand_change=-0.20,
        profitability=-0.05,
        strategic_fit=0.80,
        customer_dependency=0.75,
    )

    print(f"Decline response: {response}")

    ambiguity = classify_lifecycle_ambiguity(
        growth_rate_value=-0.20,
        revenue_growth=-0.25,
        user_growth=-0.30,
        profitability=-0.05,
    )

    print("Lifecycle signals:")
    for signal in ambiguity:
        print(f"  - {signal}")

    # ------------------------------------------------------------------------
    # Retirement
    # ------------------------------------------------------------------------

    print("\nRETIREMENT")
    print("-" * 80)

    retirement = RetirementPlan(
        product_name="FlowBoard Legacy",
        announcement_date="2026-10-01",
        end_of_sale_date="2027-01-01",
        end_of_support_date="2027-07-01",
        migration_plan="Move remaining customers to FlowBoard Next.",
        data_export_available=True,
        communication_channels=[
            "Email",
            "Product dashboard",
            "Customer success",
        ],
        owner="Product Operations",
    )

    print("Retirement readiness:")
    for check, passed in retirement.readiness_checks().items():
        print(f"  {check}: {'PASS' if passed else 'FAIL'}")

    print(
        f"Migration completion: "
        f"{calculate_migration_completion(450, 500):.1%}"
    )

    retirement_risk = retirement_risk_score(
        remaining_customers=500,
        critical_customers=50,
        unresolved_dependencies=2,
        data_export_ready=True,
    )

    print(f"Retirement risk: {retirement_risk:.1%}")

    # ------------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------------

    print("\nSECURITY THROUGH THE LIFECYCLE")
    print("-" * 80)

    for control in security_by_lifecycle_stage():
        print(
            f"{control.stage.value:12} | "
            f"{control.control}"
        )

    # ------------------------------------------------------------------------
    # Portfolio
    # ------------------------------------------------------------------------

    print("\nPORTFOLIO MANAGEMENT")
    print("-" * 80)

    portfolio = [
        PortfolioProduct(
            "FlowBoard Core",
            LifecycleStage.MATURITY,
            0.04,
            0.15,
            0.20,
        ),
        PortfolioProduct(
            "FlowBoard Next",
            LifecycleStage.GROWTH,
            0.30,
            0.05,
            0.10,
        ),
        PortfolioProduct(
            "FlowBoard Legacy",
            LifecycleStage.DECLINE,
            -0.20,
            0.02,
            -0.05,
        ),
    ]

    for item in portfolio:
        print(
            f"{item.name:20} "
            f"{item.stage.value:12} "
            f"-> {portfolio_posture(item)}"
        )

    # ------------------------------------------------------------------------
    # Product health
    # ------------------------------------------------------------------------

    print("\nPRODUCT HEALTH")
    print("-" * 80)

    health = ProductHealth(
        activation=0.75,
        retention=0.72,
        revenue_growth=0.65,
        gross_margin=0.70,
        satisfaction=0.82,
    )

    print(f"Product health score: {health.score():.2%}")

    # ------------------------------------------------------------------------
    # Product decision
    # ------------------------------------------------------------------------

    print("\nSTAGE-BASED PRODUCT DECISION")
    print("-" * 80)

    decision = product_decision(
        stage=LifecycleStage.GROWTH,
        evidence_strength=0.85,
        customer_value=0.90,
        business_value=0.80,
        operational_risk=0.20,
    )

    print(decision)

    # ------------------------------------------------------------------------
    # Roadmap quality
    # ------------------------------------------------------------------------

    roadmap = [
        RoadmapItem(
            "Q1",
            "Improve activation",
            "Activated users",
            0.60,
        ),
        RoadmapItem(
            "Q2",
            "Improve retention",
            "Month-3 retention",
            0.70,
        ),
        RoadmapItem(
            "Q3",
            "Improve enterprise adoption",
            "Enterprise ARR",
            1_000_000,
        ),
    ]

    print(
        f"\nRoadmap quality score: "
        f"{roadmap_quality_score(roadmap):.1%}"
    )

    # ------------------------------------------------------------------------
    # Lifecycle simulation
    # ------------------------------------------------------------------------

    timeline = simulate_flowboard_lifecycle()
    print_lifecycle_simulation(timeline)

    # ------------------------------------------------------------------------
    # Checklist
    # ------------------------------------------------------------------------

    print("\nLIFECYCLE CHECKLIST")
    print("-" * 80)

    for stage, checks in lifecycle_checklist().items():
        print(f"\n{stage}")
        for check in checks:
            print(f"  [ ] {check}")

    # ------------------------------------------------------------------------
    # Common mistakes
    # ------------------------------------------------------------------------

    print("\nCOMMON MISTAKES")
    print("-" * 80)

    for item in common_mistakes():
        print(f"\nMistake: {item['mistake']}")
        print(f"Better:  {item['better']}")

    # ------------------------------------------------------------------------
    # Comparisons
    # ------------------------------------------------------------------------

    print("\nIMPORTANT DISTINCTIONS")
    print("-" * 80)

    for item in lifecycle_comparison_table():
        print(f"\n{item['concept']}")
        print(f"  {item['distinction']}")

    # ------------------------------------------------------------------------
    # Business case
    # ------------------------------------------------------------------------

    print("\nFLOWBOARD BUSINESS CASE")
    print("-" * 80)

    business_case = analyze_flowboard_business_case()

    for key, value in business_case.items():
        if isinstance(value, float):
            print(f"{key:25}: {value:.4f}")
        else:
            print(f"{key:25}: {value}")


# ============================================================================
# 45. COMMAND-LINE ENTRY POINT
# ============================================================================

def main() -> None:
    """Main program entry point."""

    print("=" * 80)
    print("PRODUCT LIFECYCLE: DISCOVERY TO RETIREMENT")
    print("=" * 80)

    run_demonstrations()

    print("\n")
    print("=" * 80)
    print("RUNNING AUTOMATED TESTS")
    print("=" * 80)

    run_tests()

    print("\nStudy guide execution completed.")


if __name__ == "__main__":
    main()
