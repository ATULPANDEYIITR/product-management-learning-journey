"""
Product Thinking: Problems vs Solutions, Outcomes vs Outputs, Customer Value,
Business Value, and Systems Thinking

This standalone study script teaches product thinking from absolute beginner
level through advanced practice. It uses executable Python examples to model
product decisions, customer and business value, outcome measurement,
prioritization, assumptions, experiments, feedback loops, and systems.

The examples are intentionally small enough to inspect and modify while still
representing realistic product-management reasoning.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
import math
import statistics


# =============================================================================
# 1. PRODUCT THINKING FUNDAMENTALS
# =============================================================================

print("=" * 80)
print("1. PRODUCT THINKING FUNDAMENTALS")
print("=" * 80)

"""
Product thinking is a way of reasoning about products as systems that create
value for customers while producing sustainable value for the organization.

A product decision should not begin with:
    "What feature should we build?"

A stronger starting point is:
    "What problem exists?"
    "Who experiences it?"
    "How important is it?"
    "What outcome should improve?"
    "Why would solving it create customer value?"
    "Why would solving it create business value?"
    "What is the smallest useful intervention we can test?"

Important distinctions:

Problem:
    An unmet need, difficulty, pain, limitation, risk, or desired progress.

Solution:
    A proposed intervention intended to address a problem.

Output:
    Something the team produces, such as a feature, screen, API, campaign,
    workflow, or release.

Outcome:
    A measurable change in customer behavior, customer condition, or business
    performance caused partly by the product.

Customer value:
    The benefit perceived or experienced by the customer.

Business value:
    The economic, strategic, operational, risk-related, or competitive benefit
    received by the organization.

Systems thinking:
    Understanding how multiple components interact, including feedback loops,
    incentives, dependencies, delays, constraints, and unintended consequences.
"""


@dataclass
class ProductIdea:
    name: str
    problem: str
    target_customer: str
    proposed_solution: str
    expected_customer_value: str
    expected_business_value: str


calculator_feature = ProductIdea(
    name="Automatic expense categorization",
    problem="Users spend significant time manually categorizing transactions.",
    target_customer="People who track personal finances regularly",
    proposed_solution="Automatically categorize transactions using transaction data.",
    expected_customer_value="Less manual effort and faster expense tracking.",
    expected_business_value="Higher retention because tracking becomes easier.",
)

print("\nExample product idea:")
print(calculator_feature)


# =============================================================================
# 2. PROBLEMS VS SOLUTIONS
# =============================================================================

print("\n" + "=" * 80)
print("2. PROBLEMS VS SOLUTIONS")
print("=" * 80)

"""
A problem describes the undesirable condition or unmet need.

A solution describes one possible response.

Confusing the two creates solution bias.

Example:

Solution-first:
    "We need a mobile app."

Problem-first:
    "Customers cannot easily check order status while away from a computer."

The second formulation leaves room for several solutions:
    - responsive web page
    - SMS updates
    - mobile application
    - email notifications
    - messaging integration
    - improved customer-service workflow

A good product thinker keeps the problem stable while allowing solutions
to change as evidence improves.
"""


@dataclass
class ProblemStatement:
    user: str
    situation: str
    difficulty: str
    consequence: str

    def describe(self) -> str:
        return (
            f"{self.user} experiences difficulty when {self.situation}. "
            f"The difficulty is {self.difficulty}, which results in "
            f"{self.consequence}."
        )


problem = ProblemStatement(
    user="frequent online shoppers",
    situation="they need to track several deliveries",
    difficulty="they must manually check multiple order pages",
    consequence="uncertainty and repeated effort",
)

print(problem.describe())


@dataclass
class SolutionHypothesis:
    solution: str
    mechanism: str
    assumption: str

    def describe(self) -> str:
        return (
            f"Solution: {self.solution}\n"
            f"Mechanism: {self.mechanism}\n"
            f"Key assumption: {self.assumption}"
        )


hypothesis = SolutionHypothesis(
    solution="Unified delivery tracking",
    mechanism="Collect shipment events into one timeline",
    assumption="Users value having multiple deliveries visible in one place",
)

print("\nSolution hypothesis:")
print(hypothesis.describe())


# =============================================================================
# 3. FIVE WHYS AND ROOT-CAUSE THINKING
# =============================================================================

print("\n" + "=" * 80)
print("3. ROOT-CAUSE THINKING")
print("=" * 80)

"""
A visible symptom is not necessarily the root problem.

The Five Whys technique repeatedly asks why an observed condition occurs.

It should not be treated as a mechanical formula. Real systems often have
multiple causes, but the technique helps prevent premature solution selection.
"""


def five_whys(initial_problem: str, why_chain: Sequence[str]) -> List[str]:
    chain = [initial_problem]
    chain.extend(why_chain)
    return chain


why_chain = five_whys(
    "Users abandon checkout.",
    [
        "Checkout requires too many steps.",
        "The process asks for information before payment.",
        "The organization historically optimized for data collection.",
        "Several internal workflows depend on those fields.",
        "The product architecture reflects internal processes rather than the
         customer's primary goal.",
    ],
)

print("\nFive Whys chain:")
for index, item in enumerate(why_chain, start=1):
    print(f"{index}. {item}")


# =============================================================================
# 4. JOBS, NEEDS, PAINS, AND DESIRED PROGRESS
# =============================================================================

print("\n" + "=" * 80)
print("4. CUSTOMER NEEDS, PAINS, AND DESIRED PROGRESS")
print("=" * 80)

"""
Customers usually do not want a feature for its own sake.

They want progress.

For example:
    Feature: one-click reorder
    Desired progress: obtain a familiar product quickly without repeating work

A useful product analysis separates:

Functional need:
    What the customer needs to accomplish.

Emotional need:
    How the customer wants to feel.

Social need:
    How the customer wants to be perceived or interact with others.

Pain:
    Something that creates effort, cost, uncertainty, risk, delay, or
    frustration.

Desired gain:
    An improvement the customer hopes to obtain.
"""


@dataclass
class CustomerNeed:
    functional: str
    emotional: str
    social: str
    pains: List[str]
    desired_gains: List[str]


need = CustomerNeed(
    functional="Complete an expense report accurately",
    emotional="Feel confident that no important item was missed",
    social="Appear reliable to the finance team",
    pains=["Manual entry", "Missing receipts", "Uncertainty about categories"],
    desired_gains=["Accuracy", "Speed", "Confidence"],
)

print("\nCustomer need model:")
print("Functional:", need.functional)
print("Emotional:", need.emotional)
print("Social:", need.social)
print("Pains:", ", ".join(need.pains))
print("Desired gains:", ", ".join(need.desired_gains))


# =============================================================================
# 5. CUSTOMER VALUE
# =============================================================================

print("\n" + "=" * 80)
print("5. CUSTOMER VALUE")
print("=" * 80)

"""
Customer value can be understood as the relationship between benefits and
sacrifices.

A simplified conceptual model is:

    Customer Value = Perceived Benefits - Perceived Sacrifices

Benefits can include:
    - saved time
    - reduced effort
    - increased income
    - improved accuracy
    - reduced risk
    - convenience
    - confidence
    - enjoyment

Sacrifices can include:
    - price
    - time
    - learning effort
    - switching cost
    - privacy cost
    - attention
    - complexity
    - operational effort

The equation below is a teaching model, not a universal measurement formula.
"""


def customer_value(
    functional_benefit: float,
    emotional_benefit: float,
    convenience_benefit: float,
    monetary_cost: float,
    effort_cost: float,
    switching_cost: float,
) -> float:
    benefits = functional_benefit + emotional_benefit + convenience_benefit
    sacrifices = monetary_cost + effort_cost + switching_cost
    return benefits - sacrifices


value = customer_value(
    functional_benefit=40,
    emotional_benefit=20,
    convenience_benefit=30,
    monetary_cost=15,
    effort_cost=10,
    switching_cost=5,
)

print(f"\nIllustrative customer-value score: {value}")


# =============================================================================
# 6. BUSINESS VALUE
# =============================================================================

print("\n" + "=" * 80)
print("6. BUSINESS VALUE")
print("=" * 80)

"""
Business value is broader than revenue.

Possible sources include:

Revenue:
    - subscriptions
    - transactions
    - advertising
    - licensing
    - expansion

Cost reduction:
    - lower support volume
    - lower infrastructure cost
    - lower manual operations

Risk reduction:
    - fraud prevention
    - regulatory compliance
    - security improvements

Strategic value:
    - stronger distribution
    - market entry
    - differentiation
    - ecosystem effects
    - data or capability development

A feature can create customer value without creating enough business value.
A feature can also create business value while harming customers, which is
usually a sign that the product strategy or incentive structure is unhealthy.
"""


@dataclass
class BusinessValue:
    incremental_revenue: float = 0.0
    cost_savings: float = 0.0
    risk_reduction: float = 0.0
    strategic_value: float = 0.0

    def total(self) -> float:
        return (
            self.incremental_revenue
            + self.cost_savings
            + self.risk_reduction
            + self.strategic_value
        )


business_value = BusinessValue(
    incremental_revenue=50000,
    cost_savings=15000,
    risk_reduction=10000,
    strategic_value=25000,
)

print(f"Illustrative business-value score: {business_value.total():,.0f}")


# =============================================================================
# 7. CUSTOMER VALUE AND BUSINESS VALUE MUST CONNECT
# =============================================================================

print("\n" + "=" * 80)
print("7. CONNECTING CUSTOMER VALUE TO BUSINESS VALUE")
print("=" * 80)

"""
A strong product hypothesis describes a causal chain.

Example:

Faster checkout
    -> less customer effort
    -> fewer checkout abandonments
    -> more completed purchases
    -> higher revenue

The intermediate customer outcome matters because simply launching a faster
checkout is an output. The actual product value appears when customer behavior
and business performance improve.
"""


@dataclass
class ValueChain:
    output: str
    customer_change: str
    customer_metric: str
    business_change: str
    business_metric: str


checkout_chain = ValueChain(
    output="Reduced checkout steps",
    customer_change="Checkout becomes faster and easier",
    customer_metric="Checkout completion rate",
    business_change="More purchases are completed",
    business_metric="Completed orders per active customer",
)

print("\nValue chain:")
for field_name in checkout_chain.__dataclass_fields__:
    print(f"{field_name}: {getattr(checkout_chain, field_name)}")


# =============================================================================
# 8. OUTPUTS VS OUTCOMES
# =============================================================================

print("\n" + "=" * 80)
print("8. OUTPUTS VS OUTCOMES")
print("=" * 80)

"""
Outputs are things a team controls directly.

Examples:
    - feature released
    - number of experiments launched
    - number of support articles written
    - number of API endpoints implemented

Outcomes describe meaningful change.

Examples:
    - activation improves
    - task completion becomes faster
    - error rate declines
    - customer retention improves
    - support contacts decrease

Output:
    "We released a recommendation engine."

Outcome:
    "More customers discover relevant products and purchase them."

Outputs are not useless. They are necessary. The mistake is treating them as
evidence that the underlying problem has been solved.
"""


@dataclass
class ProductResult:
    output: str
    output_metric: float
    outcome: str
    outcome_metric_before: float
    outcome_metric_after: float

    def outcome_change(self) -> float:
        return self.outcome_metric_after - self.outcome_metric_before


result = ProductResult(
    output="Redesigned onboarding flow",
    output_metric=1,
    outcome="Activation rate",
    outcome_metric_before=0.42,
    outcome_metric_after=0.51,
)

print(f"Output delivered: {result.output}")
print(f"Outcome change: {result.outcome_change():.0%}")


# =============================================================================
# 9. NORTH-STAR AND SUPPORTING METRICS
# =============================================================================

print("\n" + "=" * 80)
print("9. PRODUCT METRICS")
print("=" * 80)

"""
A useful metric hierarchy can contain:

Business goal
    -> product outcome
        -> user behavior
            -> leading indicators

Example:

Business goal:
    Sustainable revenue

Product outcome:
    Customers repeatedly obtain useful value

Behavior:
    Customers complete meaningful tasks

Leading indicators:
    activation, feature adoption, successful task completion

Guardrail metrics are important because optimizing one metric can damage
another.

Example:
    A recommendation system increases clicks but also increases returns.

Click-through rate alone would look positive.
Return rate is a guardrail showing possible customer-value deterioration.
"""


@dataclass
class Metric:
    name: str
    value: float
    direction: str
    role: str


metrics = [
    Metric("Activation rate", 0.51, "higher", "outcome"),
    Metric("Task completion rate", 0.83, "higher", "leading indicator"),
    Metric("Average support contacts", 1.7, "lower", "guardrail"),
    Metric("Return rate", 0.09, "lower", "guardrail"),
]

for metric in metrics:
    print(
        f"{metric.name}: {metric.value} | "
        f"preferred direction={metric.direction} | role={metric.role}"
    )


# =============================================================================
# 10. METRIC CALCULATIONS
# =============================================================================

print("\n" + "=" * 80)
print("10. PRACTICAL PRODUCT METRIC CALCULATIONS")
print("=" * 80)


def conversion_rate(conversions: int, opportunities: int) -> float:
    if opportunities < 0 or conversions < 0:
        raise ValueError("Counts cannot be negative.")
    if conversions > opportunities:
        raise ValueError("Conversions cannot exceed opportunities.")
    if opportunities == 0:
        return 0.0
    return conversions / opportunities


def retention_rate(retained_users: int, starting_users: int) -> float:
    if retained_users < 0 or starting_users < 0:
        raise ValueError("User counts cannot be negative.")
    if retained_users > starting_users:
        raise ValueError("Retained users cannot exceed starting users.")
    if starting_users == 0:
        return 0.0
    return retained_users / starting_users


def churn_rate(churned_users: int, starting_users: int) -> float:
    return 1 - retention_rate(starting_users - churned_users, starting_users)


print("Conversion rate:", f"{conversion_rate(250, 1000):.1%}")
print("Retention rate:", f"{retention_rate(700, 1000):.1%}")
print("Churn rate:", f"{churn_rate(300, 1000):.1%}")


# =============================================================================
# 11. PROBLEM SELECTION
# =============================================================================

print("\n" + "=" * 80)
print("11. PROBLEM SELECTION")
print("=" * 80)

"""
Product teams rarely have unlimited capacity.

A problem can be evaluated using dimensions such as:

    - customer frequency
    - customer severity
    - strategic importance
    - business impact
    - evidence strength
    - urgency
    - feasibility
    - risk

A scoring model is a decision aid, not a substitute for judgment.
"""


@dataclass
class ProblemCandidate:
    name: str
    reach: float
    severity: float
    strategic_fit: float
    evidence: float
    urgency: float

    def score(self) -> float:
        return (
            self.reach * 0.20
            + self.severity * 0.25
            + self.strategic_fit * 0.20
            + self.evidence * 0.20
            + self.urgency * 0.15
        )


problems = [
    ProblemCandidate("Checkout confusion", 9, 9, 8, 9, 8),
    ProblemCandidate("Profile customization", 5, 4, 6, 7, 3),
    ProblemCandidate("Advanced theme options", 3, 3, 4, 6, 2),
]

for candidate in sorted(problems, key=lambda item: item.score(), reverse=True):
    print(f"{candidate.name}: {candidate.score():.2f}")


# =============================================================================
# 12. RICE PRIORITIZATION
# =============================================================================

print("\n" + "=" * 80)
print("12. RICE PRIORITIZATION")
print("=" * 80)

"""
RICE is commonly expressed as:

    RICE = Reach * Impact * Confidence / Effort

Reach:
    Number of affected customers or events in a period.

Impact:
    Estimated magnitude of effect.

Confidence:
    Confidence in the estimates.

Effort:
    Relative amount of work.

The exact scale can be adapted. The important idea is to make assumptions
visible instead of hiding them behind intuition.
"""


@dataclass
class RiceItem:
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float

    def score(self) -> float:
        if self.effort <= 0:
            raise ValueError("Effort must be positive.")
        return self.reach * self.impact * self.confidence / self.effort


rice_items = [
    RiceItem("Simplify checkout", 8000, 2.5, 0.85, 8),
    RiceItem("Improve search filters", 5000, 1.5, 0.75, 5),
    RiceItem("Add profile themes", 2500, 0.5, 0.70, 3),
]

for item in sorted(rice_items, key=lambda x: x.score(), reverse=True):
    print(f"{item.name}: RICE={item.score():.2f}")


# =============================================================================
# 13. VALUE VS EFFORT
# =============================================================================

print("\n" + "=" * 80)
print("13. VALUE VS EFFORT")
print("=" * 80)

"""
A simple value-effort matrix helps separate:

High value / low effort:
    Often attractive opportunities.

High value / high effort:
    Strategic initiatives that may require deeper planning.

Low value / low effort:
    Possible quick wins, but they should not crowd out important work.

Low value / high effort:
    Usually poor candidates unless there is a hidden constraint or obligation.
"""


def value_effort_category(value: float, effort: float) -> str:
    if value >= 7 and effort <= 4:
        return "high value / low effort"
    if value >= 7 and effort > 4:
        return "high value / high effort"
    if value < 7 and effort <= 4:
        return "low value / low effort"
    return "low value / high effort"


examples = [
    ("Checkout copy improvement", 8, 2),
    ("Payment architecture migration", 9, 9),
    ("Minor icon adjustment", 3, 1),
    ("Complex personalization engine", 5, 9),
]

for name, value, effort in examples:
    print(name, "->", value_effort_category(value, effort))


# =============================================================================
# 14. ASSUMPTIONS AND RISKS
# =============================================================================

print("\n" + "=" * 80)
print("14. ASSUMPTIONS AND RISKS")
print("=" * 80)

"""
Every product proposal contains assumptions.

Typical assumptions:

Desirability:
    Customers actually want the proposed value.

Usability:
    Customers can understand and use the solution.

Feasibility:
    The organization can technically and operationally deliver it.

Viability:
    The economics and business model can support it.

Strategic alignment:
    It supports an important organizational direction.

A high-risk assumption should often be tested before substantial investment.
"""


@dataclass
class Assumption:
    statement: str
    importance: float
    uncertainty: float

    def risk_score(self) -> float:
        return self.importance * self.uncertainty


assumptions = [
    Assumption(
        "Customers will use automatic categorization.",
        importance=9,
        uncertainty=8,
    ),
    Assumption(
        "Transaction data can be categorized reliably.",
        importance=9,
        uncertainty=6,
    ),
    Assumption(
        "Implementation can fit existing architecture.",
        importance=7,
        uncertainty=5,
    ),
]

for assumption in sorted(assumptions, key=lambda x: x.risk_score(), reverse=True):
    print(f"{assumption.risk_score():.0f}: {assumption.statement}")


# =============================================================================
# 15. EXPERIMENT DESIGN
# =============================================================================

print("\n" + "=" * 80)
print("15. PRODUCT EXPERIMENTS")
print("=" * 80)

"""
A good experiment connects:

Hypothesis
    -> intervention
    -> expected behavior
    -> metric
    -> threshold
    -> decision

Example:

Hypothesis:
    If checkout is shortened, completion rate will increase.

Experiment:
    Show a simplified checkout to a controlled group.

Primary metric:
    Purchase completion rate.

Guardrails:
    Payment failure rate, refund rate, customer complaints.

Decision rule:
    Ship, iterate, or stop based on predefined evidence.
"""


@dataclass
class Experiment:
    hypothesis: str
    primary_metric: str
    baseline: float
    target: float
    observed: float
    guardrail_name: str
    guardrail_limit: float
    observed_guardrail: float

    def passes_primary_metric(self) -> bool:
        return self.observed >= self.target

    def passes_guardrail(self) -> bool:
        return self.observed_guardrail <= self.guardrail_limit

    def decision(self) -> str:
        if self.passes_primary_metric() and self.passes_guardrail():
            return "Evidence supports continuation."
        if not self.passes_guardrail():
            return "Stop or redesign because the guardrail deteriorated."
        return "Primary metric did not reach the target."


experiment = Experiment(
    hypothesis="Reducing checkout steps will increase completed purchases.",
    primary_metric="Checkout completion rate",
    baseline=0.62,
    target=0.68,
    observed=0.71,
    guardrail_name="Payment failure rate",
    guardrail_limit=0.04,
    observed_guardrail=0.025,
)

print(experiment.hypothesis)
print("Decision:", experiment.decision())


# =============================================================================
# 16. CAUSAL THINKING
# =============================================================================

print("\n" + "=" * 80)
print("16. CAUSAL THINKING")
print("=" * 80)

"""
Correlation does not automatically establish causation.

Suppose conversion increased after a new feature launched.

Possible explanations include:
    - the feature caused the increase
    - seasonality
    - marketing activity
    - pricing changes
    - a competitor outage
    - changes in traffic composition
    - random variation

Controlled experiments can help isolate causal effects.

A simplified treatment-control comparison is shown below.
"""


def relative_lift(control_rate: float, treatment_rate: float) -> float:
    if control_rate <= 0:
        raise ValueError("Control rate must be positive.")
    return (treatment_rate - control_rate) / control_rate


control = 0.20
treatment = 0.24

print(f"Relative lift: {relative_lift(control, treatment):.1%}")


def absolute_lift(control_rate: float, treatment_rate: float) -> float:
    return treatment_rate - control_rate


print(f"Absolute lift: {absolute_lift(control, treatment):.1%}")


# =============================================================================
# 17. STATISTICAL THINKING FOR PRODUCT DECISIONS
# =============================================================================

print("\n" + "=" * 80)
print("17. BASIC STATISTICAL THINKING")
print("=" * 80)

"""
Product experiments contain noise.

Important concepts include:

Mean:
    Average value.

Median:
    Middle value after sorting.

Variance:
    How dispersed observations are.

Sample size:
    Number of observations.

Confidence interval:
    A range expressing uncertainty around an estimate.

Statistical significance:
    A property of a statistical test under specified assumptions. It does not
    automatically mean that a change is useful to customers or valuable to the
    business.

Practical significance:
    Whether the magnitude of the effect is meaningful in the real product.
"""


def mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate the mean of an empty sequence.")
    return statistics.mean(values)


def median(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate the median of an empty sequence.")
    return statistics.median(values)


sample = [0.21, 0.19, 0.24, 0.23, 0.20, 0.26, 0.22]

print("Mean:", f"{mean(sample):.3f}")
print("Median:", f"{median(sample):.3f}")
print("Sample standard deviation:", f"{statistics.stdev(sample):.3f}")


# =============================================================================
# 18. FUNNEL THINKING
# =============================================================================

print("\n" + "=" * 80)
print("18. FUNNEL THINKING")
print("=" * 80)

"""
A funnel represents sequential customer steps.

Example:
    visit
    -> signup
    -> activation
    -> first successful task
    -> repeat use
    -> purchase

Funnel analysis identifies where users are lost.

It is important to avoid assuming that the largest percentage drop is always
the most important problem. A small percentage drop can represent a huge
absolute customer loss, and a large drop may be expected behavior.
"""


def funnel_rates(counts: Sequence[int]) -> List[float]:
    if not counts:
        return []
    if any(count < 0 for count in counts):
        raise ValueError("Funnel counts cannot be negative.")

    rates = [1.0]
    for previous, current in zip(counts, counts[1:]):
        if current > previous:
            raise ValueError("Funnel counts must not increase.")
        rates.append(current / previous if previous else 0.0)
    return rates


funnel = [10000, 7200, 4500, 3100, 2100]
rates = funnel_rates(funnel)

print("Funnel counts:", funnel)
print("Step-to-step rates:", [f"{rate:.1%}" for rate in rates])


# =============================================================================
# 19. COHORT THINKING
# =============================================================================

print("\n" + "=" * 80)
print("19. COHORT ANALYSIS")
print("=" * 80)

"""
A cohort is a group of users sharing a defined starting condition, often a
signup or activation period.

Cohorts help answer questions such as:

    Did users acquired in June retain better than users acquired in May?
    Did a product change improve retention for new users?
    Are improvements caused by acquisition mix rather than product quality?

Cohort comparisons are often more informative than a single aggregate metric.
"""


cohorts = {
    "January": [0.42, 0.31, 0.25, 0.21],
    "February": [0.44, 0.35, 0.28, 0.24],
    "March": [0.47, 0.39, 0.32, 0.27],
}

for cohort_name, retention_values in cohorts.items():
    print(
        cohort_name,
        "retention:",
        " -> ".join(f"{value:.0%}" for value in retention_values),
    )


# =============================================================================
# 20. CUSTOMER SEGMENTATION
# =============================================================================

print("\n" + "=" * 80)
print("20. CUSTOMER SEGMENTATION")
print("=" * 80)

"""
Different customers can have different problems and different definitions of
value.

Segmentation can be based on:

    - behavior
    - use case
    - frequency
    - willingness to pay
    - organization size
    - lifecycle stage
    - context

Avoid segmentation that is merely descriptive but does not change a decision.
"""


@dataclass
class Customer:
    customer_id: int
    monthly_usage: int
    monthly_spend: float
    support_contacts: int

    def segment(self) -> str:
        if self.monthly_usage >= 30 and self.monthly_spend >= 100:
            return "power customer"
        if self.monthly_usage >= 10:
            return "regular customer"
        return "light customer"


customers = [
    Customer(1, 45, 180, 2),
    Customer(2, 15, 60, 1),
    Customer(3, 4, 10, 0),
]

for customer in customers:
    print(customer.customer_id, "->", customer.segment())


# =============================================================================
# 21. PERSONAS VS BEHAVIORAL SEGMENTS
# =============================================================================

print("\n" + "=" * 80)
print("21. PERSONAS VS BEHAVIORAL SEGMENTS")
print("=" * 80)

"""
A persona is a representation of a meaningful customer pattern.

A persona becomes useful when it changes product decisions.

Behavioral segmentation is often stronger for quantitative decisions because it
uses observable behavior.

Example:

Persona:
    "Time-constrained professional"

Behavioral segment:
    "Users who perform fewer than five sessions per month but complete high-value
     transactions."

The second definition can be measured directly.
"""


def behavioral_segment(
    sessions_per_month: int,
    transaction_value: float,
) -> str:
    if sessions_per_month < 5 and transaction_value >= 500:
        return "low-frequency / high-value"
    if sessions_per_month >= 20:
        return "high-frequency"
    return "standard"


print(behavioral_segment(3, 900))
print(behavioral_segment(25, 100))
print(behavioral_segment(10, 200))


# =============================================================================
# 22. CUSTOMER JOURNEY THINKING
# =============================================================================

print("\n" + "=" * 80)
print("22. CUSTOMER JOURNEY")
print("=" * 80)

"""
A customer journey examines the sequence of experiences surrounding a goal.

Typical stages:
    awareness
    consideration
    acquisition
    onboarding
    first value
    repeated use
    support
    renewal
    advocacy

The product itself may only control part of the journey.

Systems-oriented product thinking considers handoffs among:
    product
    marketing
    sales
    support
    operations
    payment systems
    external partners
"""


@dataclass
class JourneyStage:
    name: str
    customer_goal: str
    friction: int
    importance: int

    def opportunity_score(self) -> int:
        return self.friction * self.importance


journey = [
    JourneyStage("Onboarding", "Understand how to get started", 8, 9),
    JourneyStage("First value", "Complete the first meaningful task", 9, 10),
    JourneyStage("Repeat use", "Obtain value consistently", 6, 10),
    JourneyStage("Support", "Resolve problems quickly", 5, 6),
]

for stage in sorted(journey, key=lambda x: x.opportunity_score(), reverse=True):
    print(stage.name, stage.opportunity_score())


# =============================================================================
# 23. DESIGNING A PRODUCT OUTCOME
# =============================================================================

print("\n" + "=" * 80)
print("23. OUTCOME DESIGN")
print("=" * 80)

"""
A useful outcome should describe a change rather than an artifact.

Weak:
    "Launch personalized recommendations."

Stronger:
    "Increase the proportion of sessions in which users discover a relevant
     item without increasing returns or complaints."

The stronger outcome:
    - describes customer behavior
    - contains a measurable dimension
    - includes a guardrail
    - avoids prescribing one implementation
"""


@dataclass
class Outcome:
    desired_change: str
    metric: str
    baseline: float
    target: float
    guardrails: Dict[str, float]

    def target_gap(self) -> float:
        return self.target - self.baseline


outcome = Outcome(
    desired_change="More users successfully complete their first meaningful task.",
    metric="First-task completion rate",
    baseline=0.45,
    target=0.60,
    guardrails={
        "support_contact_rate": 0.10,
        "error_rate": 0.03,
    },
)

print("Outcome:", outcome.desired_change)
print("Gap:", f"{outcome.target_gap():.0%}")


# =============================================================================
# 24. PRODUCT STRATEGY
# =============================================================================

print("\n" + "=" * 80)
print("24. PRODUCT STRATEGY")
print("=" * 80)

"""
Strategy connects:

Current situation
    -> target customer
    -> important problem
    -> desired future state
    -> choices
    -> capabilities
    -> measures

Strategy is partly about choosing what NOT to pursue.

A roadmap is not the strategy itself.

A roadmap describes planned work.
A strategy explains why those choices matter.
"""


@dataclass
class ProductStrategy:
    target_customer: str
    important_problem: str
    desired_outcome: str
    strategic_choice: str
    explicit_non_goal: str

    def describe(self) -> str:
        return (
            f"Target customer: {self.target_customer}\n"
            f"Problem: {self.important_problem}\n"
            f"Outcome: {self.desired_outcome}\n"
            f"Choice: {self.strategic_choice}\n"
            f"Non-goal: {self.explicit_non_goal}"
        )


strategy = ProductStrategy(
    target_customer="Small businesses managing recurring invoices",
    important_problem="Invoice follow-up consumes significant administrative time.",
    desired_outcome="Increase on-time payment rate while reducing manual follow-up.",
    strategic_choice="Automate high-confidence reminders before expanding into
                       complex collections workflows.",
    explicit_non_goal="Become a full enterprise accounts-receivable platform.",
)

print(strategy.describe())


# =============================================================================
# 25. ROADMAP THINKING
# =============================================================================

print("\n" + "=" * 80)
print("25. ROADMAP THINKING")
print("=" * 80)

"""
A feature roadmap lists outputs.

An outcome-oriented roadmap groups work around customer or business problems.

Feature roadmap:
    Q1: reminders
    Q2: dashboard
    Q3: reporting

Outcome roadmap:
    Q1: reduce missed payments
    Q2: improve cash-flow visibility
    Q3: reduce reconciliation effort

The second framing keeps the desired result visible even if the implementation
changes.
"""


@dataclass
class RoadmapTheme:
    period: str
    problem_or_outcome: str
    candidate_solutions: List[str]


roadmap = [
    RoadmapTheme(
        "Q1",
        "Reduce missed payments",
        ["Automated reminders", "Payment links", "Reminder scheduling"],
    ),
    RoadmapTheme(
        "Q2",
        "Improve cash-flow visibility",
        ["Forecasting", "Receivables dashboard", "Risk indicators"],
    ),
]

for item in roadmap:
    print(f"{item.period}: {item.problem_or_outcome}")
    print("  Candidate solutions:", ", ".join(item.candidate_solutions))


# =============================================================================
# 26. MVP THINKING
# =============================================================================

print("\n" + "=" * 80)
print("26. MVP AND MINIMUM VIABLE LEARNING")
print("=" * 80)

"""
An MVP should not be interpreted as "the worst possible version of a product."

The useful question is:

    What is the smallest credible intervention that allows us to learn whether
    the important assumption is true?

Possible MVP forms:
    - manual service
    - prototype
    - landing page
    - concierge workflow
    - limited beta
    - rule-based implementation
    - single-segment release

The correct MVP depends on the uncertainty being tested.
"""


@dataclass
class MVP:
    assumption: str
    smallest_test: str
    evidence_needed: str

    def describe(self) -> str:
        return (
            f"Assumption: {self.assumption}\n"
            f"Smallest test: {self.smallest_test}\n"
            f"Evidence: {self.evidence_needed}"
        )


mvp = MVP(
    assumption="Customers want proactive payment reminders.",
    smallest_test="Manually send reminders to a small group of consenting customers.",
    evidence_needed="Reminder engagement and improvement in payment timing.",
)

print(mvp.describe())


# =============================================================================
# 27. DISCOVERY VS DELIVERY
# =============================================================================

print("\n" + "=" * 80)
print("27. DISCOVERY AND DELIVERY")
print("=" * 80)

"""
Discovery reduces uncertainty about:
    - customer problem
    - desirability
    - solution usefulness
    - business viability
    - technical feasibility

Delivery converts a validated direction into a reliable product capability.

The two activities interact continuously.

A team that only delivers can efficiently build the wrong thing.
A team that only discovers can learn indefinitely without creating value.
"""


@dataclass
class DiscoveryEvidence:
    source: str
    evidence_strength: float
    limitation: str


evidence = [
    DiscoveryEvidence(
        "Customer interview",
        0.45,
        "Self-reported behavior may differ from actual behavior.",
    ),
    DiscoveryEvidence(
        "Observed product behavior",
        0.70,
        "Observed behavior may lack causal explanation.",
    ),
    DiscoveryEvidence(
        "Controlled experiment",
        0.90,
        "Requires sufficient traffic and valid experimental design.",
    ),
]

for item in evidence:
    print(f"{item.source}: strength={item.evidence_strength:.0%}")
    print(f"  Limitation: {item.limitation}")


# =============================================================================
# 28. QUALITATIVE VS QUANTITATIVE EVIDENCE
# =============================================================================

print("\n" + "=" * 80)
print("28. QUALITATIVE VS QUANTITATIVE EVIDENCE")
print("=" * 80)

"""
Qualitative evidence helps explain:
    - why something happens
    - what customers mean
    - hidden needs
    - workflow context
    - emotional and organizational factors

Quantitative evidence helps estimate:
    - frequency
    - magnitude
    - distribution
    - trends
    - correlations
    - behavioral changes

Neither automatically replaces the other.
"""


@dataclass
class Evidence:
    method: str
    answers: str
    weakness: str


evidence_types = [
    Evidence(
        "Interview",
        "Why might customers experience this problem?",
        "Small samples and self-report bias.",
    ),
    Evidence(
        "Analytics",
        "How frequently does this behavior occur?",
        "Often cannot explain why.",
    ),
    Evidence(
        "Experiment",
        "Did the intervention cause a measurable change?",
        "Can be expensive or difficult to run correctly.",
    ),
]

for item in evidence_types:
    print(f"{item.method}: {item.answers}")
    print(f"  Limitation: {item.weakness}")


# =============================================================================
# 29. PRIORITIZING EVIDENCE, NOT JUST FEATURES
# =============================================================================

print("\n" + "=" * 80)
print("29. PRIORITIZING LEARNING")
print("=" * 80)

"""
Sometimes the best next action is not building a feature.

A useful learning-priority score can consider:

    impact of being wrong
    uncertainty
    cost of testing

High-impact + high-uncertainty assumptions are strong candidates for early
testing.
"""


def learning_priority(
    impact_if_wrong: float,
    uncertainty: float,
    test_cost: float,
) -> float:
    if test_cost <= 0:
        raise ValueError("Test cost must be positive.")
    return impact_if_wrong * uncertainty / test_cost


learning_tasks = [
    ("Test willingness to use reminders", 9, 8, 2),
    ("Validate dashboard color preference", 2, 5, 1),
    ("Check API scalability assumption", 8, 7, 5),
]

for name, impact, uncertainty, cost in learning_tasks:
    print(name, "->", f"{learning_priority(impact, uncertainty, cost):.2f}")


# =============================================================================
# 30. TRADE-OFFS
# =============================================================================

print("\n" + "=" * 80)
print("30. PRODUCT TRADE-OFFS")
print("=" * 80)

"""
Product decisions frequently involve trade-offs.

Examples:
    simplicity vs flexibility
    speed vs completeness
    personalization vs privacy
    short-term revenue vs long-term trust
    customization vs maintainability
    growth vs operational stability
    automation vs human control

There is rarely a universally correct answer. The decision depends on the
target customer, context, strategy, constraints, and risk tolerance.
"""


@dataclass
class Tradeoff:
    option_a: str
    option_b: str
    primary_value: str
    sacrificed_value: str

    def explain(self) -> str:
        return (
            f"{self.option_a} prioritizes {self.primary_value} at the expense of "
            f"some {self.sacrificed_value}; {self.option_b} reverses that emphasis."
        )


tradeoff = Tradeoff(
    option_a="Simple default workflow",
    option_b="Highly configurable workflow",
    primary_value="low cognitive effort",
    sacrificed_value="customization",
)

print(tradeoff.explain())


# =============================================================================
# 31. CONSTRAINT THINKING
# =============================================================================

print("\n" + "=" * 80)
print("31. CONSTRAINTS")
print("=" * 80)

"""
Constraints can include:

    - engineering capacity
    - legal requirements
    - data availability
    - latency
    - budget
    - organizational dependencies
    - legacy architecture
    - supply limitations
    - trust and safety requirements

A product decision should distinguish:
    "We cannot do this now"
from:
    "This is not strategically valuable."

Constraints affect timing and implementation, but should not automatically
determine the underlying customer problem.
"""


@dataclass
class Constraint:
    name: str
    severity: int
    controllability: int

    def priority(self) -> float:
        return self.severity / max(self.controllability, 1)


constraints = [
    Constraint("Limited engineering capacity", 8, 5),
    Constraint("Missing customer data", 9, 3),
    Constraint("Regulatory approval", 10, 1),
]

for item in sorted(constraints, key=lambda x: x.priority(), reverse=True):
    print(item.name, f"priority={item.priority():.2f}")


# =============================================================================
# 32. SYSTEMS THINKING
# =============================================================================

print("\n" + "=" * 80)
print("32. SYSTEMS THINKING")
print("=" * 80)

"""
Systems thinking asks:

    What components interact?
    What causes what?
    Where are the feedback loops?
    Where are the delays?
    What incentives exist?
    What happens when one variable changes?
    What unintended consequences might appear?

A product is rarely isolated.

Example:
    More promotions
        -> more orders
        -> more warehouse load
        -> slower fulfillment
        -> more customer complaints
        -> lower retention

Optimizing only order volume can therefore damage the larger system.
"""


@dataclass
class SystemNode:
    name: str
    value: float


system_nodes = {
    "orders": SystemNode("orders", 1000),
    "warehouse_load": SystemNode("warehouse_load", 700),
    "fulfillment_delay": SystemNode("fulfillment_delay", 2),
    "complaints": SystemNode("complaints", 50),
    "retention": SystemNode("retention", 0.70),
}

print("\nInitial system state:")
for node in system_nodes.values():
    print(node.name, "=", node.value)


# =============================================================================
# 33. CAUSAL CHAINS
# =============================================================================

print("\n" + "=" * 80)
print("33. CAUSAL CHAINS")
print("=" * 80)


@dataclass
class CausalLink:
    cause: str
    effect: str
    relationship_strength: float


causal_links = [
    CausalLink("Promotions", "Orders", 0.80),
    CausalLink("Orders", "Warehouse load", 0.75),
    CausalLink("Warehouse load", "Fulfillment delay", 0.65),
    CausalLink("Fulfillment delay", "Complaints", 0.70),
    CausalLink("Complaints", "Retention", -0.60),
]

for link in causal_links:
    print(
        f"{link.cause} -> {link.effect} "
        f"(illustrative strength={link.relationship_strength:+.2f})"
    )


# =============================================================================
# 34. FEEDBACK LOOPS
# =============================================================================

print("\n" + "=" * 80)
print("34. FEEDBACK LOOPS")
print("=" * 80)

"""
Reinforcing loop:
    A increases B, and B increases A.

Balancing loop:
    A increases B, while B eventually reduces A.

Example reinforcing loop:
    Better product quality
        -> customer satisfaction
        -> word of mouth
        -> more users
        -> more revenue
        -> more resources for quality

Example balancing loop:
    More demand
        -> longer processing time
        -> lower service capacity
        -> lower completed demand
"""


@dataclass
class FeedbackLoop:
    name: str
    loop_type: str
    variables: List[str]

    def describe(self) -> str:
        return f"{self.name} ({self.loop_type}): " + " -> ".join(self.variables)


loops = [
    FeedbackLoop(
        "Growth loop",
        "reinforcing",
        ["quality", "satisfaction", "referrals", "users", "resources"],
    ),
    FeedbackLoop(
        "Capacity loop",
        "balancing",
        ["demand", "load", "delay", "satisfaction", "completed demand"],
    ),
]

for loop in loops:
    print(loop.describe())


# =============================================================================
# 35. STOCKS AND FLOWS
# =============================================================================

print("\n" + "=" * 80)
print("35. STOCKS AND FLOWS")
print("=" * 80)

"""
In systems thinking:

Stock:
    An accumulated quantity.

Flow:
    A rate that changes a stock.

Example:
    Active customers = stock
    New customers = inflow
    Churned customers = outflow

Basic relationship:

    ending_stock = starting_stock + inflow - outflow
"""


def ending_stock(starting: int, inflow: int, outflow: int) -> int:
    if min(starting, inflow, outflow) < 0:
        raise ValueError("Stock and flow values cannot be negative.")
    if outflow > starting + inflow:
        raise ValueError("Outflow cannot exceed available stock.")
    return starting + inflow - outflow


print("Ending active customers:", ending_stock(10000, 1800, 1200))


# =============================================================================
# 36. DELAYS
# =============================================================================

print("\n" + "=" * 80)
print("36. SYSTEM DELAYS")
print("=" * 80)

"""
A decision can have delayed effects.

Example:

Marketing spend
    -> acquisition
    -> onboarding
    -> first value
    -> retention
    -> revenue

If revenue is measured immediately after spending, the decision-maker may
misinterpret the system.

Delayed feedback can create overreaction:
    increase investment
    -> wait
    -> see no immediate effect
    -> increase investment again
    -> delayed effects arrive together
    -> excessive capacity or spending
"""


def delayed_effect(
    current_input: float,
    historical_inputs: Sequence[float],
    weights: Sequence[float],
) -> float:
    if len(historical_inputs) != len(weights):
        raise ValueError("Inputs and weights must have the same length.")
    if not weights:
        return current_input
    weighted_history = sum(value * weight for value, weight in zip(historical_inputs, weights))
    return weighted_history / sum(weights)


print(
    "Illustrative delayed demand estimate:",
    f"{delayed_effect(100, [90, 80, 70], [0.5, 0.3, 0.2]):.1f}",
)


# =============================================================================
# 37. UNINTENDED CONSEQUENCES
# =============================================================================

print("\n" + "=" * 80)
print("37. UNINTENDED CONSEQUENCES")
print("=" * 80)

"""
A metric becomes dangerous when teams optimize it without considering the
system around it.

Example:

Goal:
    Reduce average support handling time.

Possible unintended result:
    Agents close tickets quickly without solving the underlying issue.

The metric improves while customer satisfaction deteriorates.

A better design uses:
    primary metric
    + quality metric
    + customer guardrail
"""


@dataclass
class MetricBundle:
    primary: float
    quality: float
    customer_guardrail: float

    def acceptable(self) -> bool:
        return (
            self.primary >= 0.80
            and self.quality >= 0.75
            and self.customer_guardrail >= 0.80
        )


bundle = MetricBundle(
    primary=0.90,
    quality=0.78,
    customer_guardrail=0.84,
)

print("Metric bundle acceptable:", bundle.acceptable())


# =============================================================================
# 38. GOODHART'S LAW
# =============================================================================

print("\n" + "=" * 80)
print("38. METRIC GAMING AND GOODHART'S LAW")
print("=" * 80)

"""
A common product-management warning is:

    When a measure becomes a target, it can cease to be a good measure.

If a support team is rewarded only for reducing average handling time, it may
optimize the number rather than customer resolution.

This does not mean metrics are bad. It means metric design must consider:
    - incentives
    - gaming behavior
    - quality
    - unintended effects
"""


@dataclass
class SupportMetrics:
    handling_time: float
    first_contact_resolution: float
    customer_satisfaction: float

    def healthy(self) -> bool:
        return (
            self.first_contact_resolution >= 0.75
            and self.customer_satisfaction >= 0.80
        )


support = SupportMetrics(
    handling_time=4.5,
    first_contact_resolution=0.81,
    customer_satisfaction=0.86,
)

print("Healthy support outcome:", support.healthy())


# =============================================================================
# 39. INCENTIVES
# =============================================================================

print("\n" + "=" * 80)
print("39. INCENTIVES AND PRODUCT BEHAVIOR")
print("=" * 80)

"""
People respond to incentives.

If the product rewards:
    - clicks, users may click more
    - purchases, users may buy unsuitable items
    - referrals, users may send low-quality referrals
    - time spent, users may spend unnecessary time

The product manager should ask:

    What behavior does this metric encourage?
    What behavior does it accidentally encourage?
    Who bears the cost?
    What guardrail detects the damage?
"""


@dataclass
class IncentiveModel:
    target_metric: str
    desired_behavior: str
    possible_gaming: str
    guardrail: str


incentive = IncentiveModel(
    target_metric="Number of completed orders",
    desired_behavior="Customers successfully purchase useful products",
    possible_gaming="Aggressive discounts create low-quality purchases and returns",
    guardrail="Return rate and contribution margin",
)

print("Target:", incentive.target_metric)
print("Desired behavior:", incentive.desired_behavior)
print("Gaming risk:", incentive.possible_gaming)
print("Guardrail:", incentive.guardrail)


# =============================================================================
# 40. SECOND-ORDER EFFECTS
# =============================================================================

print("\n" + "=" * 80)
print("40. SECOND-ORDER EFFECTS")
print("=" * 80)

"""
First-order effect:
    Immediate direct result.

Second-order effect:
    Consequence caused by the first-order change.

Example:

Lower delivery price
    -> more orders
    -> higher courier demand
    -> higher delivery costs
    -> lower margin

Another example:

Aggressive notification frequency
    -> more app opens
    -> more short-term engagement
    -> notification fatigue
    -> users disable notifications
    -> lower long-term engagement
"""


@dataclass
class Effect:
    order: int
    event: str


effects = [
    Effect(1, "More notifications are sent."),
    Effect(2, "Short-term opens increase."),
    Effect(3, "Notification fatigue increases."),
    Effect(4, "More users mute notifications."),
    Effect(5, "Reach of future important notifications decreases."),
]

for effect in effects:
    print(f"{effect.order}. {effect.event}")


# =============================================================================
# 41. PLATFORM AND NETWORK EFFECTS
# =============================================================================

print("\n" + "=" * 80)
print("41. NETWORK EFFECTS")
print("=" * 80)

"""
A network effect occurs when the value experienced by one participant changes
as the number or quality of participants changes.

Direct network effect:
    More users can make the product more useful to users.

Indirect network effect:
    More users attract complementary participants, which improves value.

Network effects differ from simple growth.

A product becoming larger does not automatically mean each user receives more
value.
"""


def direct_network_value(users: int, base_value: float, coefficient: float) -> float:
    if users < 0:
        raise ValueError("Users cannot be negative.")
    return base_value + coefficient * math.log1p(users)


for users in [10, 100, 1000, 10000]:
    print(users, "users -> value index", f"{direct_network_value(users, 10, 2):.2f}")


# =============================================================================
# 42. PLATFORM THINKING
# =============================================================================

print("\n" + "=" * 80)
print("42. PLATFORM THINKING")
print("=" * 80)

"""
Platforms coordinate multiple participant groups.

Examples:
    buyers and sellers
    riders and drivers
    developers and users
    advertisers and audiences

Platform product thinking considers:
    - participant incentives
    - liquidity
    - matching
    - trust
    - safety
    - quality
    - governance
    - supply-demand balance

Improving one side can damage another side.
"""


@dataclass
class PlatformState:
    buyers: int
    sellers: int
    successful_matches: int

    def buyer_match_rate(self) -> float:
        return self.successful_matches / self.buyers if self.buyers else 0.0

    def seller_match_rate(self) -> float:
        return self.successful_matches / self.sellers if self.sellers else 0.0


platform = PlatformState(1000, 600, 450)

print("Buyer match rate:", f"{platform.buyer_match_rate():.1%}")
print("Seller match rate:", f"{platform.seller_match_rate():.1%}")


# =============================================================================
# 43. TRUST AS A PRODUCT VARIABLE
# =============================================================================

print("\n" + "=" * 80)
print("43. TRUST")
print("=" * 80)

"""
Trust can be a core product outcome.

Trust can depend on:
    - reliability
    - transparency
    - predictable behavior
    - security
    - privacy
    - accuracy
    - dispute handling

Trust is often slower to build than to destroy, so short-term optimization can
have long-term consequences.
"""


@dataclass
class TrustModel:
    reliability: float
    transparency: float
    security: float
    recovery_quality: float

    def trust_index(self) -> float:
        return (
            self.reliability * 0.35
            + self.transparency * 0.20
            + self.security * 0.30
            + self.recovery_quality * 0.15
        )


trust = TrustModel(0.92, 0.80, 0.95, 0.85)
print("Illustrative trust index:", f"{trust.trust_index():.2%}")


# =============================================================================
# 44. PRODUCT QUALITY
# =============================================================================

print("\n" + "=" * 80)
print("44. PRODUCT QUALITY")
print("=" * 80)

"""
Product quality includes more than visual design.

Dimensions can include:
    - correctness
    - reliability
    - usability
    - accessibility
    - performance
    - security
    - recoverability
    - consistency

A product can be feature-rich but low quality if users cannot reliably obtain
the intended value.
"""


@dataclass
class QualityDimensions:
    correctness: float
    reliability: float
    usability: float
    performance: float
    accessibility: float
    security: float

    def weighted_score(self) -> float:
        weights = {
            "correctness": 0.25,
            "reliability": 0.20,
            "usability": 0.20,
            "performance": 0.10,
            "accessibility": 0.10,
            "security": 0.15,
        }
        return (
            self.correctness * weights["correctness"]
            + self.reliability * weights["reliability"]
            + self.usability * weights["usability"]
            + self.performance * weights["performance"]
            + self.accessibility * weights["accessibility"]
            + self.security * weights["security"]
        )


quality = QualityDimensions(0.95, 0.90, 0.82, 0.88, 0.75, 0.97)
print("Illustrative quality score:", f"{quality.weighted_score():.2%}")


# =============================================================================
# 45. PRODUCT ANALYTICS AND EVENT DESIGN
# =============================================================================

print("\n" + "=" * 80)
print("45. PRODUCT ANALYTICS")
print("=" * 80)

"""
Product analytics requires clear event definitions.

Bad event:
    "button_clicked"

Better event:
    "checkout_payment_submitted"

An event should capture meaningful product behavior.

A useful event model includes:
    event name
    timestamp
    user or anonymous identifier
    relevant properties
    context

Analytics systems also require attention to privacy, data minimization, access
control, retention policies, and legal obligations.
"""


@dataclass
class ProductEvent:
    event_name: str
    user_id: str
    properties: Dict[str, object]

    def validate(self) -> None:
        if not self.event_name:
            raise ValueError("Event name is required.")
        if not self.user_id:
            raise ValueError("User identifier is required.")


event = ProductEvent(
    event_name="checkout_payment_submitted",
    user_id="user-123",
    properties={
        "payment_method": "card",
        "cart_value": 125.50,
        "currency": "INR",
    },
)

event.validate()
print("Valid event:", event)


# =============================================================================
# 46. DATA QUALITY
# =============================================================================

print("\n" + "=" * 80)
print("46. DATA QUALITY")
print("=" * 80)

"""
Product decisions depend on data quality.

Common problems:
    - missing events
    - duplicate events
    - inconsistent definitions
    - changing instrumentation
    - bots
    - identity fragmentation
    - delayed data
    - survivorship bias
    - selection bias

A metric definition should specify:
    numerator
    denominator
    population
    time window
    exclusions
    data source
"""


@dataclass
class MetricDefinition:
    name: str
    numerator: str
    denominator: str
    population: str
    time_window: str

    def definition(self) -> str:
        return (
            f"{self.name} = {self.numerator} / {self.denominator}; "
            f"population={self.population}; window={self.time_window}"
        )


activation_metric = MetricDefinition(
    name="Activation rate",
    numerator="users completing the first meaningful task",
    denominator="new eligible users",
    population="users who completed signup",
    time_window="within 7 days of signup",
)

print(activation_metric.definition())


# =============================================================================
# 47. PRODUCT DECISION RECORD
# =============================================================================

print("\n" + "=" * 80)
print("47. PRODUCT DECISION RECORD")
print("=" * 80)

"""
A decision record makes reasoning inspectable.

Useful fields:
    problem
    evidence
    assumptions
    options
    trade-offs
    decision
    expected outcome
    metrics
    risks
    review date

This reduces decision-making based only on memory or authority.
"""


@dataclass
class ProductDecision:
    problem: str
    evidence: List[str]
    assumptions: List[str]
    options: List[str]
    decision: str
    expected_outcome: str
    risks: List[str]

    def print_record(self) -> None:
        print("Problem:", self.problem)
        print("Evidence:")
        for item in self.evidence:
            print("  -", item)
        print("Assumptions:")
        for item in self.assumptions:
            print("  -", item)
        print("Options:", ", ".join(self.options))
        print("Decision:", self.decision)
        print("Expected outcome:", self.expected_outcome)
        print("Risks:")
        for item in self.risks:
            print("  -", item)


decision = ProductDecision(
    problem="Users abandon the onboarding flow before reaching first value.",
    evidence=[
        "Analytics show the largest drop occurs before the first task.",
        "Interviews indicate uncertainty about the next action.",
    ],
    assumptions=[
        "Reducing initial choices will make the next action clearer.",
        "The reduced flow will preserve required account information.",
    ],
    options=[
        "Redesign onboarding",
        "Add instructional content",
        "Add live assistance",
    ],
    decision="Test a simplified onboarding flow first.",
    expected_outcome="Increase first-task completion without increasing support contacts.",
    risks=["Important information may become harder to collect."],
)

decision.print_record()


# =============================================================================
# 48. PRODUCT CASE STUDY: FOOD DELIVERY
# =============================================================================

print("\n" + "=" * 80)
print("48. CASE STUDY: FOOD DELIVERY")
print("=" * 80)

"""
Scenario:

A food-delivery company observes that order volume is increasing, but customer
retention is declining.

A solution-first response might be:
    "Build a loyalty program."

Product-thinking analysis asks:
    - Which customers are leaving?
    - When did their experience deteriorate?
    - What changed?
    - Is the problem price, quality, reliability, selection, or trust?
    - Which outcome predicts retention?
"""

food_data = {
    "orders_per_week": 2.8,
    "average_delivery_delay_minutes": 18,
    "late_order_rate": 0.14,
    "customer_retention": 0.61,
}

print("Observed metrics:")
for key, value in food_data.items():
    print(f"{key}: {value}")

"""
A hypothesis could be:

    Reducing severe delivery delays will improve customer retention.

Possible output:
    Improve courier allocation.

Desired customer outcome:
    Fewer severely delayed deliveries.

Business outcome:
    Higher repeat ordering and retention.

Guardrails:
    courier utilization
    cancellation rate
    delivery cost
"""


# =============================================================================
# 49. CASE STUDY: FINTECH
# =============================================================================

print("\n" + "=" * 80)
print("49. CASE STUDY: FINTECH")
print("=" * 80)

"""
Scenario:

A financial application wants more users to invest.

A weak product objective:
    "Add ten investment features."

A stronger problem framing:
    "New users struggle to understand which investment action is appropriate
     for their stated goal and risk tolerance."

Potential customer value:
    better confidence and lower cognitive effort.

Potential business value:
    increased successful activation and long-term account value.

Important guardrails:
    suitability
    transparency
    error rate
    complaint rate
    regulatory compliance
    privacy
"""


@dataclass
class FintechMetrics:
    onboarding_completion: float
    first_investment_rate: float
    complaint_rate: float
    error_rate: float

    def healthy(self) -> bool:
        return (
            self.onboarding_completion >= 0.70
            and self.first_investment_rate >= 0.35
            and self.complaint_rate <= 0.03
            and self.error_rate <= 0.02
        )


fintech = FintechMetrics(0.76, 0.42, 0.018, 0.011)
print("Fintech outcome state is healthy:", fintech.healthy())


# =============================================================================
# 50. CASE STUDY: B2B SOFTWARE
# =============================================================================

print("\n" + "=" * 80)
print("50. CASE STUDY: B2B SOFTWARE")
print("=" * 80)

"""
B2B product decisions contain multiple stakeholders.

Possible stakeholders:
    end user
    manager
    administrator
    procurement
    security team
    finance team
    executive sponsor

Customer value can differ by stakeholder.

Example:
    End user -> faster work
    Manager -> visibility
    Administrator -> easier configuration
    Security -> controlled access
    Finance -> predictable cost
"""


@dataclass
class StakeholderValue:
    stakeholder: str
    desired_value: str
    metric: str


stakeholders = [
    StakeholderValue("End user", "Complete work faster", "task completion time"),
    StakeholderValue("Manager", "See operational performance", "report usage"),
    StakeholderValue("Administrator", "Reduce configuration effort", "setup time"),
    StakeholderValue("Security", "Control access", "policy violations"),
    StakeholderValue("Finance", "Control spend", "cost per active account"),
]

for stakeholder in stakeholders:
    print(
        f"{stakeholder.stakeholder}: {stakeholder.desired_value} "
        f"-> {stakeholder.metric}"
    )


# =============================================================================
# 51. BUSINESS MODEL THINKING
# =============================================================================

print("\n" + "=" * 80)
print("51. BUSINESS MODEL")
print("=" * 80)

"""
Product thinking must consider how value becomes sustainable.

A simplified business model can include:

Revenue per customer
    - variable cost
    = contribution per customer

Lifetime value depends on retention, frequency, margin, and other assumptions.

The exact calculation varies by business model.
"""


def contribution_margin(
    revenue: float,
    variable_cost: float,
) -> float:
    if revenue < 0 or variable_cost < 0:
        raise ValueError("Revenue and cost cannot be negative.")
    if revenue == 0:
        return 0.0
    return (revenue - variable_cost) / revenue


print(
    "Contribution margin:",
    f"{contribution_margin(1000, 350):.1%}",
)


def simple_ltv(
    average_revenue_per_period: float,
    gross_margin: float,
    churn_rate_per_period: float,
) -> float:
    if average_revenue_per_period < 0:
        raise ValueError("Revenue cannot be negative.")
    if not 0 < gross_margin <= 1:
        raise ValueError("Gross margin must be between 0 and 1.")
    if not 0 < churn_rate_per_period <= 1:
        raise ValueError("Churn must be between 0 and 1.")
    return average_revenue_per_period * gross_margin / churn_rate_per_period


print(
    "Illustrative LTV:",
    f"{simple_ltv(500, 0.70, 0.05):,.2f}",
)


# =============================================================================
# 52. UNIT ECONOMICS
# =============================================================================

print("\n" + "=" * 80)
print("52. UNIT ECONOMICS")
print("=" * 80)

"""
Unit economics asks whether the economics of an individual customer,
transaction, order, or other unit make sense.

Common measures:
    CAC: customer acquisition cost
    LTV: lifetime value
    contribution margin
    payback period

A healthy aggregate business can still contain unhealthy customer segments.
"""


def ltv_to_cac_ratio(ltv: float, cac: float) -> float:
    if cac <= 0:
        raise ValueError("CAC must be positive.")
    return ltv / cac


ltv = simple_ltv(500, 0.70, 0.05)
cac = 150

print("LTV:CAC ratio:", f"{ltv_to_cac_ratio(ltv, cac):.2f}:1")


# =============================================================================
# 53. PRICING AND CUSTOMER VALUE
# =============================================================================

print("\n" + "=" * 80)
print("53. PRICING")
print("=" * 80)

"""
Price is part of the customer value equation.

A higher price can still create high value if the benefit is substantially
greater.

Pricing analysis can consider:
    willingness to pay
    alternatives
    switching cost
    customer segment
    marginal cost
    strategic positioning
    perceived differentiation
"""


def value_surplus(perceived_value: float, price: float) -> float:
    return perceived_value - price


print("Illustrative customer surplus:", value_surplus(200, 80))


# =============================================================================
# 54. PLATFORM FLYWHEELS AND DYNAMICS
# =============================================================================

print("\n" + "=" * 80)
print("54. PRODUCT FLYWHEEL")
print("=" * 80)

"""
A flywheel describes a reinforcing mechanism.

Example:

More useful content
    -> more users
    -> more contributions
    -> better content
    -> more useful content

The critical product-thinking question is:

    What mechanism causes the loop to reinforce itself?

A decorative diagram without a causal mechanism is not a useful flywheel.
"""


@dataclass
class Flywheel:
    stages: List[str]

    def check(self) -> bool:
        return len(self.stages) >= 3 and self.stages[0] == self.stages[-1]


flywheel = Flywheel(
    [
        "More useful content",
        "More users",
        "More contributions",
        "Better content",
        "More useful content",
    ]
)

print("Valid reinforcing cycle:", flywheel.check())


# =============================================================================
# 55. PRODUCT OPERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("55. PRODUCT OPERATIONS")
print("=" * 80)

"""
A product is not finished when code is deployed.

Production considerations include:
    - monitoring
    - incident response
    - customer support
    - rollback
    - experimentation
    - data integrity
    - access control
    - capacity
    - documentation
    - change management

Product thinking therefore includes the operational environment in which
customer value is actually delivered.
"""


@dataclass
class ProductionReadiness:
    monitoring: bool
    rollback: bool
    support_process: bool
    data_quality: bool
    security_review: bool

    def ready(self) -> bool:
        return all(
            [
                self.monitoring,
                self.rollback,
                self.support_process,
                self.data_quality,
                self.security_review,
            ]
        )


readiness = ProductionReadiness(True, True, True, True, True)
print("Production ready:", readiness.ready())


# =============================================================================
# 56. SECURITY AS PRODUCT VALUE
# =============================================================================

print("\n" + "=" * 80)
print("56. SECURITY AND PRIVACY")
print("=" * 80)

"""
Security is not merely an engineering concern.

A security failure can destroy:
    - customer trust
    - business value
    - regulatory standing
    - product adoption
    - operational continuity

Product decisions should consider:
    least privilege
    data minimization
    secure defaults
    authentication
    authorization
    auditability
    retention
    incident response

Privacy should be considered in the problem and solution definition, not only
after implementation.
"""


@dataclass
class SecurityAssessment:
    data_sensitivity: int
    exposure: int
    impact: int
    control_strength: int

    def residual_risk(self) -> int:
        inherent_risk = self.data_sensitivity * self.exposure * self.impact
        mitigation = max(self.control_strength, 1)
        return math.ceil(inherent_risk / mitigation)


security = SecurityAssessment(
    data_sensitivity=8,
    exposure=6,
    impact=9,
    control_strength=12,
)

print("Illustrative residual-risk score:", security.residual_risk())


# =============================================================================
# 57. ACCESSIBILITY
# =============================================================================

print("\n" + "=" * 80)
print("57. ACCESSIBILITY AS PRODUCT THINKING")
print("=" * 80)

"""
Accessibility concerns whether people with different abilities can perceive,
understand, navigate, and operate the product.

Accessibility is both:
    - a customer-value consideration
    - a quality consideration
    - often a legal or organizational requirement

Examples:
    keyboard navigation
    readable contrast
    captions
    alternative text
    clear error messages
    semantic structure
    screen-reader compatibility

A product that works for the average user but excludes important users can be
poorly designed from a systems perspective.
"""


@dataclass
class AccessibilityChecks:
    keyboard_access: bool
    readable_text: bool
    captions: bool
    clear_errors: bool

    def passes_basic_checks(self) -> bool:
        return all(
            [
                self.keyboard_access,
                self.readable_text,
                self.captions,
                self.clear_errors,
            ]
        )


accessibility = AccessibilityChecks(True, True, True, True)
print("Basic accessibility checks pass:", accessibility.passes_basic_checks())


# =============================================================================
# 58. FAILURE MODES
# =============================================================================

print("\n" + "=" * 80)
print("58. FAILURE MODES IN PRODUCT THINKING")
print("=" * 80)

"""
Common failure modes include:

1. Solution-first thinking
   Starting with a predetermined feature.

2. Feature output obsession
   Measuring delivery volume instead of customer outcomes.

3. HiPPO decision-making
   Giving disproportionate weight to the highest-paid person's opinion.

4. Vanity metrics
   Tracking impressive-looking numbers that do not represent value.

5. Local optimization
   Improving one component while damaging the wider system.

6. Metric gaming
   Optimizing a target while violating its intended purpose.

7. Confirmation bias
   Seeking evidence that supports an existing belief.

8. Survivorship bias
   Studying successful customers while ignoring those who left.

9. Selection bias
   Drawing conclusions from a non-representative sample.

10. Premature scaling
    Investing heavily before important assumptions are validated.

11. Ignoring operational reality
    Treating launch as the end rather than the beginning of measurement.

12. Ignoring edge cases
    Designing only for the normal path.

The following helper class makes a checklist executable.
"""


@dataclass
class ProductRiskChecklist:
    solution_first: bool = False
    output_only: bool = False
    vanity_metric: bool = False
    local_optimization: bool = False
    confirmation_bias: bool = False
    selection_bias: bool = False
    premature_scaling: bool = False
    operational_gap: bool = False

    def risks(self) -> List[str]:
        checks = {
            "solution-first thinking": self.solution_first,
            "output-only measurement": self.output_only,
            "vanity metric": self.vanity_metric,
            "local optimization": self.local_optimization,
            "confirmation bias": self.confirmation_bias,
            "selection bias": self.selection_bias,
            "premature scaling": self.premature_scaling,
            "operational gap": self.operational_gap,
        }
        return [name for name, present in checks.items() if present]


risk_check = ProductRiskChecklist(
    solution_first=True,
    output_only=True,
    vanity_metric=True,
    local_optimization=True,
)

print("Detected risks:", ", ".join(risk_check.risks()))


# =============================================================================
# 59. EDGE CASES IN PRODUCT METRICS
# =============================================================================

print("\n" + "=" * 80)
print("59. EDGE CASES")
print("=" * 80)

"""
Metrics can behave unexpectedly in edge cases.

Examples:
    - zero denominators
    - tiny sample sizes
    - new users without enough observation time
    - duplicate users
    - bots
    - data outages
    - changing definitions
    - seasonality
    - extreme outliers

Production metric code should fail safely or explicitly define behavior.
"""


edge_cases = [
    ("zero opportunities", lambda: conversion_rate(0, 0)),
    ("zero starting users", lambda: retention_rate(0, 0)),
]

for name, operation in edge_cases:
    try:
        print(name, "->", operation())
    except Exception as exc:
        print(name, "-> error:", exc)


# =============================================================================
# 60. PRODUCT DECISION WITH MULTIPLE OPTIONS
# =============================================================================

print("\n" + "=" * 80)
print("60. MULTI-OPTION DECISION MODEL")
print("=" * 80)

"""
Good product thinking compares multiple plausible approaches.

Example problem:
    Customers struggle to understand account fees.

Options:
    A. Redesign pricing page
    B. Add contextual explanations
    C. Add calculator
    D. Simplify pricing structure

The correct choice depends on the actual source of confusion.
"""


@dataclass
class Option:
    name: str
    customer_value: float
    business_value: float
    confidence: float
    effort: float
    risk: float

    def decision_score(self) -> float:
        numerator = (
            self.customer_value
            + self.business_value
        ) * self.confidence
        return numerator / (self.effort + self.risk)


options = [
    Option("Redesign pricing page", 8, 7, 0.85, 4, 2),
    Option("Contextual explanations", 7, 6, 0.80, 3, 1),
    Option("Fee calculator", 8, 8, 0.65, 6, 2),
    Option("Simplify pricing structure", 10, 9, 0.45, 10, 5),
]

for option in sorted(options, key=lambda x: x.decision_score(), reverse=True):
    print(f"{option.name}: {option.decision_score():.2f}")


# =============================================================================
# 61. EXPECTED VALUE UNDER UNCERTAINTY
# =============================================================================

print("\n" + "=" * 80)
print("61. EXPECTED VALUE")
print("=" * 80)

"""
When outcomes are uncertain, expected value can organize thinking.

    Expected Value = probability * payoff

This does not predict the future precisely. It makes assumptions explicit.

It is particularly useful when comparing:
    - uncertain opportunities
    - experiments
    - risk-reduction investments
    - strategic bets
"""


def expected_value(probability: float, payoff: float) -> float:
    if not 0 <= probability <= 1:
        raise ValueError("Probability must be between 0 and 1.")
    return probability * payoff


bets = [
    ("Experiment A", 0.70, 100),
    ("Experiment B", 0.40, 220),
    ("Experiment C", 0.90, 55),
]

for name, probability, payoff in bets:
    print(name, "->", expected_value(probability, payoff))


# =============================================================================
# 62. REGRET MINIMIZATION
# =============================================================================

print("\n" + "=" * 80)
print("62. REGRET AND REVERSIBILITY")
print("=" * 80)

"""
A useful advanced decision question is:

    "How costly is it if we are wrong?"

Another is:

    "How reversible is this decision?"

Reversible decisions can often be made quickly with limited analysis.
Irreversible or expensive decisions deserve stronger evidence.

Examples:

Reversible:
    copy change
    small UI experiment
    limited beta

Less reversible:
    major architecture migration
    acquisition
    long-term contractual commitment
    fundamental business-model change
"""


@dataclass
class DecisionReversibility:
    name: str
    impact_if_wrong: float
    reversibility: float
    evidence_strength: float

    def decision_risk(self) -> float:
        return (
            self.impact_if_wrong
            * (1 - self.reversibility)
            * (1 - self.evidence_strength)
        )


decisions = [
    DecisionReversibility("Copy experiment", 3, 0.95, 0.50),
    DecisionReversibility("Architecture migration", 10, 0.20, 0.60),
    DecisionReversibility("Pricing model change", 9, 0.30, 0.40),
]

for item in sorted(decisions, key=lambda x: x.decision_risk(), reverse=True):
    print(item.name, "risk:", f"{item.decision_risk():.2f}")


# =============================================================================
# 63. COUNTERFACTUAL THINKING
# =============================================================================

print("\n" + "=" * 80)
print("63. COUNTERFACTUAL THINKING")
print("=" * 80)

"""
A counterfactual asks:

    "What would have happened if we had not made the change?"

This matters because simple before-and-after comparisons can be misleading.

Example:

Before launch:
    conversion = 20%

After launch:
    conversion = 24%

The counterfactual might have been 23% because of seasonality.

The causal effect would then be closer to:
    24% - 23% = 1 percentage point

Controlled experiments, matched comparisons, and other causal methods can help
estimate the counterfactual.
"""


def estimated_incremental_effect(
    observed_after: float,
    estimated_counterfactual: float,
) -> float:
    return observed_after - estimated_counterfactual


print(
    "Illustrative incremental effect:",
    f"{estimated_incremental_effect(0.24, 0.23):.1%}",
)


# =============================================================================
# 64. SYSTEM BOUNDARIES
# =============================================================================

print("\n" + "=" * 80)
print("64. SYSTEM BOUNDARIES")
print("=" * 80)

"""
A system boundary defines what is included in analysis.

For an e-commerce checkout, the boundary might include:
    browser
    payment service
    inventory
    fraud system
    order service
    customer notifications

If the boundary is too narrow, important causes may be missed.
If it is too broad, analysis can become impractical.

The right boundary depends on the decision being made.
"""


@dataclass
class SystemBoundary:
    included_components: List[str]
    excluded_components: List[str]

    def describe(self) -> None:
        print("Included:")
        for component in self.included_components:
            print("  -", component)
        print("Excluded:")
        for component in self.excluded_components:
            print("  -", component)


checkout_boundary = SystemBoundary(
    included_components=[
        "checkout UI",
        "payment service",
        "inventory service",
        "fraud checks",
        "order creation",
    ],
    excluded_components=[
        "long-term delivery optimization",
        "warehouse staffing",
    ],
)

checkout_boundary.describe()


# =============================================================================
# 65. LEVERAGE POINTS
# =============================================================================

print("\n" + "=" * 80)
print("65. LEVERAGE POINTS")
print("=" * 80)

"""
A leverage point is a place where a relatively small intervention can produce
a significant system-level effect.

Possible leverage points include:
    - information flow
    - incentives
    - rules
    - constraints
    - feedback loops
    - goals
    - system structure

Example:

Instead of manually fixing thousands of customer mistakes, change the interface
so the mistake becomes difficult to make.

That changes the system rather than repeatedly treating the symptom.
"""


@dataclass
class LeveragePoint:
    intervention: str
    expected_system_effect: str
    effort: float
    potential_impact: float

    def leverage_score(self) -> float:
        if self.effort <= 0:
            raise ValueError("Effort must be positive.")
        return self.potential_impact / self.effort


leverage_points = [
    LeveragePoint(
        "Prevent invalid input at entry",
        "Fewer downstream corrections",
        3,
        9,
    ),
    LeveragePoint(
        "Hire more support agents",
        "More capacity for existing errors",
        7,
        6,
    ),
    LeveragePoint(
        "Rewrite every support response",
        "Improved handling consistency",
        6,
        5,
    ),
]

for point in sorted(
    leverage_points,
    key=lambda x: x.leverage_score(),
    reverse=True,
):
    print(point.intervention, "->", f"{point.leverage_score():.2f}")


# =============================================================================
# 66. PRODUCT SYSTEM MODEL
# =============================================================================

print("\n" + "=" * 80)
print("66. INTEGRATED PRODUCT SYSTEM")
print("=" * 80)

"""
The following model combines:

Customer problem
    -> solution hypothesis
    -> output
    -> customer outcome
    -> business outcome
    -> feedback
    -> learning
    -> next decision
"""


@dataclass
class ProductSystem:
    problem: str
    solution_hypothesis: str
    output: str
    customer_outcome: str
    business_outcome: str
    primary_metric: str
    guardrails: List[str]
    learning_question: str

    def inspect(self) -> None:
        fields = [
            ("Problem", self.problem),
            ("Solution hypothesis", self.solution_hypothesis),
            ("Output", self.output),
            ("Customer outcome", self.customer_outcome),
            ("Business outcome", self.business_outcome),
            ("Primary metric", self.primary_metric),
            ("Guardrails", ", ".join(self.guardrails)),
            ("Learning question", self.learning_question),
        ]
        for label, value in fields:
            print(f"{label}: {value}")


product_system = ProductSystem(
    problem="Users abandon complex onboarding.",
    solution_hypothesis="Reducing initial decisions will help users reach value faster.",
    output="Simplified onboarding flow.",
    customer_outcome="More new users complete their first meaningful task.",
    business_outcome="More activated users become retained customers.",
    primary_metric="First-task completion rate",
    guardrails=["support contacts", "error rate", "account completion"],
    learning_question="Does simplification increase first-task completion without
                         reducing required information quality?",
)

product_system.inspect()


# =============================================================================
# 67. COMPLETE PRODUCT THINKING WORKFLOW
# =============================================================================

print("\n" + "=" * 80)
print("67. COMPLETE PRODUCT THINKING WORKFLOW")
print("=" * 80)

"""
A practical end-to-end workflow:

1. Observe
   Collect customer, business, market, operational, and behavioral evidence.

2. Frame
   Define the problem without prematurely selecting a solution.

3. Segment
   Identify which customers and contexts matter.

4. Diagnose
   Explore causes, constraints, and system relationships.

5. Define outcomes
   Specify the meaningful customer and business changes desired.

6. Identify assumptions
   Make uncertainty visible.

7. Prioritize learning
   Test high-impact, uncertain assumptions.

8. Generate alternatives
   Produce multiple possible interventions.

9. Compare trade-offs
   Consider value, effort, risk, reversibility, and strategic fit.

10. Experiment
    Test the smallest credible intervention.

11. Measure
    Track outcomes and guardrails.

12. Learn
    Update beliefs based on evidence.

13. Deliver
    Build the appropriate production solution.

14. Monitor
    Observe real-world performance.

15. Reassess
    Continue, iterate, stop, or redirect.

This process is iterative rather than strictly linear.
"""


@dataclass
class ProductThinkingWorkflow:
    steps: List[str]

    def validate(self) -> List[str]:
        required_keywords = [
            "Observe",
            "Frame",
            "Diagnose",
            "Define outcomes",
            "Identify assumptions",
            "Experiment",
            "Measure",
            "Learn",
            "Deliver",
            "Monitor",
        ]
        missing = []
        for keyword in required_keywords:
            if not any(keyword.lower() in step.lower() for step in self.steps):
                missing.append(keyword)
        return missing


workflow = ProductThinkingWorkflow(
    steps=[
        "Observe customer and business evidence",
        "Frame the problem",
        "Segment relevant customers",
        "Diagnose root causes and system relationships",
        "Define outcomes",
        "Identify assumptions",
        "Prioritize learning",
        "Generate alternatives",
        "Compare trade-offs",
        "Experiment",
        "Measure outcomes",
        "Learn from evidence",
        "Deliver the appropriate solution",
        "Monitor production behavior",
        "Reassess the problem",
    ]
)

print("Missing workflow concepts:", workflow.validate())


# =============================================================================
# 68. PRACTICE EXERCISE ENGINE
# =============================================================================

print("\n" + "=" * 80)
print("68. PRODUCT THINKING PRACTICE")
print("=" * 80)

"""
The following exercises are represented as structured data so the script can
also function as a study worksheet.
"""


@dataclass
class PracticeCase:
    scenario: str
    weak_solution_first_statement: str
    problem_question: str
    outcome_question: str
    system_question: str


practice_cases = [
    PracticeCase(
        scenario="A banking app has a low percentage of users completing
                   identity verification.",
        weak_solution_first_statement="Add more verification screens.",
        problem_question="What prevents eligible customers from completing verification?",
        outcome_question="What customer behavior should improve?",
        system_question="Which fraud, compliance, support, or operational effects could change?",
    ),
    PracticeCase(
        scenario="A learning platform has high course enrollment but low completion.",
        weak_solution_first_statement="Add gamification badges.",
        problem_question="Why do learners stop progressing?",
        outcome_question="What meaningful learning behavior should improve?",
        system_question="How do content difficulty, reminders, schedules, and incentives interact?",
    ),
    PracticeCase(
        scenario="A marketplace has many sellers but low buyer conversion.",
        weak_solution_first_statement="Build a new recommendation page.",
        problem_question="What prevents buyers from finding trustworthy offers?",
        outcome_question="What should improve for buyers and sellers?",
        system_question="How do ranking, supply quality, trust, pricing, and liquidity interact?",
    ),
]

for index, case in enumerate(practice_cases, start=1):
    print(f"\nCase {index}: {case.scenario}")
    print("Weak solution-first statement:", case.weak_solution_first_statement)
    print("Problem question:", case.problem_question)
    print("Outcome question:", case.outcome_question)
    print("Systems question:", case.system_question)


# =============================================================================
# 69. COMMON PRODUCT THINKING QUESTIONS
# =============================================================================

print("\n" + "=" * 80)
print("69. PRODUCT THINKING QUESTION BANK")
print("=" * 80)

"""
These questions can be used during product reviews.

Problem:
    - What exactly is the customer struggling with?
    - Who experiences it?
    - How frequently?
    - How severe is it?
    - What evidence supports this?

Customer value:
    - What progress does the customer want?
    - What effort does the product remove?
    - What benefit does the customer actually perceive?
    - What alternatives already exist?

Business value:
    - How does customer value translate into business value?
    - What business metric should change?
    - What costs or risks are affected?
    - Is the value sustainable?

Outcome:
    - What should change after the intervention?
    - How will we measure it?
    - What is the baseline?
    - What guardrails are necessary?

Solution:
    - Why this solution?
    - What alternatives exist?
    - Which assumption does it test?
    - How reversible is the decision?

Systems:
    - What other components are affected?
    - Are there feedback loops?
    - Are there delays?
    - What incentives change?
    - What second-order effects are possible?

Execution:
    - What is the smallest credible experiment?
    - What must be true for this to work?
    - What happens if the result is negative?
"""


question_bank = {
    "problem": 5,
    "customer_value": 4,
    "business_value": 4,
    "outcome": 4,
    "solution": 4,
    "systems": 5,
    "execution": 3,
}

print("Question categories:")
for category, count in question_bank.items():
    print(f"{category}: {count} key questions")


# =============================================================================
# 70. FINAL INTEGRATED EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("70. FINAL INTEGRATED EXAMPLE")
print("=" * 80)

"""
Scenario:

An online education platform observes:

    - many learners register
    - relatively few complete the first lesson
    - support contacts mention uncertainty about where to begin
    - course content itself receives positive ratings

A solution-first approach might immediately propose:
    "Build an AI tutor."
    "Add gamification."
    "Redesign the dashboard."

A product-thinking approach starts with the problem.

Problem:
    New learners have difficulty identifying and completing the first meaningful
    action after registration.

Customer value:
    Clearer path to first learning progress.

Business value:
    Higher activation and potentially stronger retention.

Outcome:
    Increase first-lesson completion from 45% to 60%.

Potential guardrails:
    support contacts
    lesson quality ratings
    time-to-first-lesson

Assumption:
    The primary barrier is navigation and decision uncertainty rather than lack
    of interest.

Experiment:
    Simplify the initial path and test it with a controlled cohort.

Systems considerations:
    - course sequencing
    - notifications
    - instructor expectations
    - analytics instrumentation
    - support workload
    - learner motivation

Only after evidence supports the diagnosis should the team commit to a larger
solution.
"""


integrated = {
    "problem": "New learners struggle to identify the first meaningful action.",
    "target_customer": "New learners",
    "customer_value": "Faster and clearer progress toward first learning value.",
    "business_value": "Higher activation and potentially improved retention.",
    "output": "Simplified initial learning path.",
    "customer_outcome": "First-lesson completion increases.",
    "business_outcome": "Activated learners increase.",
    "primary_metric": "First-lesson completion rate",
    "baseline": 0.45,
    "target": 0.60,
    "guardrails": [
        "support contact rate",
        "lesson quality rating",
        "time to first lesson",
    ],
    "key_assumption": "Navigation uncertainty is a major cause of early abandonment.",
    "experiment": "Compare the simplified path against the existing onboarding experience.",
}

for key, value in integrated.items():
    print(f"{key}: {value}")


# =============================================================================
# 71. SELF-CHECK QUIZ
# =============================================================================

print("\n" + "=" * 80)
print("71. SELF-CHECK QUIZ")
print("=" * 80)

"""
Questions:

1. Is a feature a problem or a solution?
2. Is a released feature an output or an outcome?
3. Why can customer value and business value diverge?
4. Why should guardrail metrics accompany primary metrics?
5. What does systems thinking add to local product optimization?
6. Why are assumptions important?
7. Why can a before-and-after metric comparison fail to establish causation?
8. What is the difference between a stock and a flow?
9. Why does reversibility affect decision speed?
10. What is an unintended second-order effect?

Expected conceptual answers:

1. A feature is a solution.
2. A released feature is an output.
3. Customer benefit does not automatically translate into sustainable economics,
   strategic value, or operational feasibility.
4. Guardrails detect harmful side effects.
5. It reveals dependencies, feedback loops, delays, incentives, and
   second-order effects.
6. They expose uncertainty and identify what should be validated.
7. External changes and natural variation can explain the difference.
8. A stock accumulates; a flow changes the stock.
9. Reversible decisions have lower downside if wrong.
10. A consequence produced indirectly by the initial intervention.
"""


quiz_answers = {
    1: "Feature = solution",
    2: "Released feature = output",
    3: "Customer and business value require a causal and sustainable connection.",
    4: "Guardrails detect unwanted side effects.",
    5: "Systems thinking exposes relationships and unintended consequences.",
    6: "Assumptions make uncertainty explicit.",
    7: "The observed change may have causes other than the intervention.",
    8: "Stock accumulates; flow changes stock.",
    9: "Reversible decisions have lower downside when incorrect.",
    10: "A second-order effect is an indirect consequence of an intervention.",
}

for number, answer in quiz_answers.items():
    print(f"{number}. {answer}")


# =============================================================================
# 72. PRODUCTION-ORIENTED PRODUCT THINKING CHECKLIST
# =============================================================================

print("\n" + "=" * 80)
print("72. PRODUCTION-ORIENTED CHECKLIST")
print("=" * 80)

"""
Before approving a significant product initiative, verify:

Problem:
    [x] Specific customer problem identified
    [x] Target customer identified
    [x] Evidence collected
    [x] Root causes considered

Value:
    [x] Customer value described
    [x] Business value described
    [x] Causal connection considered

Outcome:
    [x] Outcome defined
    [x] Baseline defined
    [x] Target defined
    [x] Guardrails defined

Decision:
    [x] Alternatives considered
    [x] Assumptions documented
    [x] Trade-offs documented
    [x] Reversibility considered

Systems:
    [x] Dependencies considered
    [x] Feedback loops considered
    [x] Incentives considered
    [x] Second-order effects considered
    [x] Operational consequences considered

Delivery:
    [x] Experiment or validation path defined
    [x] Instrumentation defined
    [x] Monitoring considered
    [x] Security and privacy considered
    [x] Accessibility considered

The checklist is intentionally simple. Real product decisions require judgment
about which dimensions matter most for the specific context.
"""


checklist = [
    "Customer problem",
    "Evidence",
    "Customer value",
    "Business value",
    "Outcome",
    "Assumptions",
    "Alternatives",
    "Trade-offs",
    "System effects",
    "Experiment",
    "Measurement",
    "Guardrails",
    "Operations",
    "Security and privacy",
    "Accessibility",
]

for index, item in enumerate(checklist, start=1):
    print(f"[x] {index}. {item}")


# =============================================================================
# 73. END-TO-END DECISION FUNCTION
# =============================================================================

print("\n" + "=" * 80)
print("73. END-TO-END PRODUCT DECISION FUNCTION")
print("=" * 80)

"""
The function below demonstrates how several product-thinking concepts can be
combined into a structured decision.

It intentionally does not claim that a mathematical score can replace product
judgment. The score is a transparent decision aid.
"""


@dataclass
class ProductOpportunity:
    problem_severity: float
    customer_reach: float
    customer_value: float
    business_value: float
    evidence_strength: float
    uncertainty: float
    effort: float
    system_risk: float
    reversibility: float

    def score(self) -> float:
        if self.effort <= 0:
            raise ValueError("Effort must be positive.")

        benefit = (
            self.problem_severity
            * self.customer_reach
            * self.customer_value
            * self.business_value
            * self.evidence_strength
        )

        uncertainty_penalty = 1 + self.uncertainty
        system_penalty = 1 + self.system_risk
        reversibility_factor = 0.5 + self.reversibility

        return (
            benefit
            * reversibility_factor
            / (self.effort * uncertainty_penalty * system_penalty)
        )


opportunity = ProductOpportunity(
    problem_severity=9,
    customer_reach=8,
    customer_value=8,
    business_value=8,
    evidence_strength=0.80,
    uncertainty=0.30,
    effort=5,
    system_risk=0.20,
    reversibility=0.80,
)

print("Illustrative integrated opportunity score:", f"{opportunity.score():.2f}")


# =============================================================================
# 74. FINAL PRINCIPLES AS MACHINE-READABLE RULES
# =============================================================================

print("\n" + "=" * 80)
print("74. CORE PRODUCT THINKING RULES")
print("=" * 80)

"""
Core principles:

1. Start with problems, not predetermined solutions.
2. Distinguish outputs from outcomes.
3. Define value from the customer's perspective.
4. Connect customer value to business value.
5. Make assumptions explicit.
6. Use evidence to reduce uncertainty.
7. Measure outcomes rather than delivery volume alone.
8. Use guardrails to detect harmful side effects.
9. Consider multiple alternatives.
10. Make trade-offs explicit.
11. Treat metrics as imperfect representations of reality.
12. Be careful with incentives and metric gaming.
13. Think in systems rather than isolated features.
14. Look for feedback loops and delays.
15. Consider second-order effects.
16. Prefer reversible decisions when uncertainty is high.
17. Validate important assumptions before large investments.
18. Treat quality, accessibility, security, privacy, and operations as part of
    product value.
19. Reassess decisions as evidence changes.
20. Optimize for meaningful customer and business outcomes rather than feature
    count.
"""


principles = [
    "Start with problems, not predetermined solutions.",
    "Distinguish outputs from outcomes.",
    "Define value from the customer's perspective.",
    "Connect customer value to business value.",
    "Make assumptions explicit.",
    "Use evidence to reduce uncertainty.",
    "Measure outcomes rather than delivery volume alone.",
    "Use guardrails to detect harmful side effects.",
    "Consider multiple alternatives.",
    "Make trade-offs explicit.",
    "Treat metrics as imperfect representations of reality.",
    "Be careful with incentives and metric gaming.",
    "Think in systems rather than isolated features.",
    "Look for feedback loops and delays.",
    "Consider second-order effects.",
    "Prefer reversible decisions when uncertainty is high.",
    "Validate important assumptions before large investments.",
    "Treat quality, accessibility, security, privacy, and operations as product concerns.",
    "Reassess decisions as evidence changes.",
    "Optimize for meaningful customer and business outcomes rather than feature count.",
]

for index, principle in enumerate(principles, start=1):
    print(f"{index}. {principle}")


# =============================================================================
# 75. SCRIPT COMPLETION
# =============================================================================

print("\n" + "=" * 80)
print("PRODUCT THINKING STUDY SCRIPT COMPLETE")
print("=" * 80)
print(
    "This script demonstrated product thinking through problems, solutions, "
    "outcomes, customer value, business value, evidence, prioritization, "
    "experimentation, metrics, trade-offs, and systems thinking."
)
