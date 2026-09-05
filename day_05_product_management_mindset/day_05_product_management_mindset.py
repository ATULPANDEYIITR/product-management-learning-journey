"""
Product Management Mindset
==========================

A comprehensive, executable study file covering the Product Management Mindset
from absolute beginner concepts through advanced product decision-making.

The examples are intentionally self-contained and use only the Python standard
library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean, median
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
import random
import statistics


# ============================================================================
# 1. PRODUCT MANAGEMENT MINDSET: FOUNDATIONS
# ============================================================================

"""
Product management is not simply the activity of writing requirements,
managing a backlog, or coordinating engineering.

A product manager is responsible for helping a team solve valuable customer
problems in a way that is feasible for the organization and sustainable as a
business.

The product management mindset is a collection of habits:

1. Customer obsession
   Understand the customer's problem before prescribing a solution.

2. Ownership
   Take responsibility for outcomes rather than merely completing assigned
   tasks.

3. Curiosity
   Continuously ask why, what evidence exists, and what remains unknown.

4. Experimentation
   Test important assumptions before investing heavily in a solution.

5. Analytical thinking
   Convert observations into structured evidence and decisions.

6. Business thinking
   Understand revenue, cost, risk, incentives, strategy, and economics.

7. Technical awareness
   Understand enough technology to reason about feasibility, architecture,
   dependencies, constraints, reliability, and trade-offs.

8. Prioritization
   Accept that not everything can be done and make explicit trade-offs.

9. Communication
   Create shared understanding among customers, design, engineering,
   leadership, sales, operations, finance, legal, and other stakeholders.

10. Outcome orientation
    Measure whether the product created a meaningful result rather than
    simply measuring whether a feature was shipped.
"""


# ============================================================================
# 2. A SIMPLE PRODUCT MINDSET MODEL
# ============================================================================

@dataclass
class ProductIdea:
    """Represents an initial product idea before rigorous validation."""

    name: str
    target_customer: str
    problem: str
    proposed_solution: str


def evaluate_idea_quality(idea: ProductIdea) -> Dict[str, bool]:
    """
    Check whether an idea contains the basic elements needed for product
    reasoning.

    This is not a formal scoring system. It is a thinking aid.
    """
    return {
        "named_customer": bool(idea.target_customer.strip()),
        "clear_problem": bool(idea.problem.strip()),
        "explicit_solution": bool(idea.proposed_solution.strip()),
        "problem_before_solution": bool(idea.problem.strip()),
    }


idea = ProductIdea(
    name="Expense Manager",
    target_customer="Young professionals",
    problem="People struggle to understand where their monthly money goes.",
    proposed_solution="A mobile application that automatically categorizes expenses.",
)

print("PRODUCT IDEA EVALUATION")
for criterion, passed in evaluate_idea_quality(idea).items():
    print(f"{criterion}: {'PASS' if passed else 'FAIL'}")


# ============================================================================
# 3. PROBLEM-FIRST THINKING
# ============================================================================

"""
A common product mistake is solution-first thinking:

    "We should build feature X."

A product mindset asks:

    "Who has a problem?"
    "What exactly is the problem?"
    "How frequently does it occur?"
    "How severe is it?"
    "What evidence supports it?"
    "What alternatives does the customer use?"
    "Why is solving it valuable?"

Problem statements should avoid embedding the solution.

Weak:
    "Users need a dashboard."

Better:
    "Users cannot quickly understand which expenses are consuming their
     monthly budget."

A useful problem statement identifies:
    - user
    - context
    - difficulty
    - consequence
"""


@dataclass
class ProblemStatement:
    customer: str
    context: str
    difficulty: str
    consequence: str

    def as_text(self) -> str:
        return (
            f"{self.customer} experiences difficulty {self.difficulty} "
            f"when {self.context}, which causes {self.consequence}."
        )


problem = ProblemStatement(
    customer="Young professionals",
    context="reviewing their monthly spending",
    difficulty="understanding where money is being spent",
    consequence="late discovery of unnecessary expenditure",
)

print("\nPROBLEM STATEMENT")
print(problem.as_text())


# ============================================================================
# 4. CUSTOMER OBSESSION
# ============================================================================

"""
Customer obsession means optimizing for genuine customer value rather than
internal assumptions.

It does NOT mean:
    - accepting every customer request
    - building whatever the loudest customer asks for
    - ignoring business constraints
    - treating customer satisfaction as the only metric

A customer request is evidence of a need, but the requested solution may not
be the best solution.

Example:

Customer says:
    "Add an export-to-Excel button."

Possible underlying needs:
    - share data with a manager
    - perform calculations
    - archive records
    - integrate with another workflow

The PM should investigate the underlying job.
"""


@dataclass
class CustomerInterview:
    customer: str
    quote: str
    observed_behavior: str
    frequency: int
    severity: int

    def problem_signal(self) -> float:
        """Simple prioritization signal based on frequency and severity."""
        return self.frequency * self.severity


interviews = [
    CustomerInterview(
        "Customer A",
        "I always forget where my money went.",
        "Reviews transactions once per month.",
        5,
        4,
    ),
    CustomerInterview(
        "Customer B",
        "I want a beautiful dark theme.",
        "Changes application theme occasionally.",
        2,
        1,
    ),
    CustomerInterview(
        "Customer C",
        "I cannot tell if I am overspending.",
        "Checks bank transactions manually.",
        5,
        5,
    ),
]

print("\nCUSTOMER PROBLEM SIGNALS")
for interview in interviews:
    print(
        interview.customer,
        "signal=",
        interview.problem_signal(),
        "quote=",
        interview.quote,
    )


# ============================================================================
# 5. CUSTOMER REQUEST VS CUSTOMER NEED
# ============================================================================

def separate_request_from_need(request: str) -> Dict[str, str]:
    """
    Demonstrates a useful PM habit: distinguish what the customer asks for
    from the outcome they may actually want.
    """
    request_lower = request.lower()

    if "export" in request_lower:
        return {
            "request": request,
            "possible_need": "Move or share information efficiently.",
            "investigation_question": "What does the customer do with the exported data?",
        }

    if "notification" in request_lower:
        return {
            "request": request,
            "possible_need": "Avoid missing an important event.",
            "investigation_question": "Which event matters and what happens if it is missed?",
        }

    return {
        "request": request,
        "possible_need": "Unknown until investigated.",
        "investigation_question": "What outcome would this request improve?",
    }


print("\nREQUEST VS NEED")
print(separate_request_from_need("Please add an Excel export button."))


# ============================================================================
# 6. OWNERSHIP
# ============================================================================

"""
Ownership is outcome responsibility.

A task-oriented mindset says:
    "The ticket is complete."

An ownership mindset asks:
    "Did completing the ticket actually solve the problem?"

Ownership includes:
    - identifying risks early
    - communicating uncertainty
    - coordinating dependencies
    - validating results
    - learning from failures
    - escalating when necessary
    - avoiding blame-oriented behavior
"""


@dataclass
class ProductOutcome:
    objective: str
    baseline: float
    target: float
    actual: float

    @property
    def achieved(self) -> bool:
        return self.actual >= self.target

    @property
    def improvement(self) -> float:
        if self.baseline == 0:
            return float("inf") if self.actual > 0 else 0.0
        return (self.actual - self.baseline) / self.baseline


outcome = ProductOutcome(
    objective="Increase successful onboarding completion",
    baseline=40,
    target=60,
    actual=55,
)

print("\nOUTCOME OWNERSHIP")
print("Objective:", outcome.objective)
print("Target achieved:", outcome.achieved)
print("Relative improvement:", round(outcome.improvement * 100, 2), "%")


# ============================================================================
# 7. CURIOSITY AND THE FIVE WHYS
# ============================================================================

def five_whys(initial_problem: str, causes: Sequence[str]) -> List[str]:
    """
    Store a five-whys investigation.

    The causes must be evidence-based in real product work. The function
    itself does not pretend that a cause is true merely because it was written.
    """
    result = [initial_problem]
    result.extend(causes[:5])
    return result


why_chain = five_whys(
    "Users abandon onboarding.",
    [
        "The setup process feels difficult.",
        "Users are asked for information they do not understand.",
        "The value of providing the information is unclear.",
        "The product communicates value too late.",
        "The onboarding flow was designed around internal data requirements.",
    ],
)

print("\nFIVE WHYS")
for index, statement in enumerate(why_chain):
    print(f"{index}: {statement}")


# ============================================================================
# 8. HYPOTHESES
# ============================================================================

"""
A hypothesis is a testable belief.

Weak:
    "Users will like the new dashboard."

Stronger:
    "If we show users a weekly spending summary immediately after login,
     then the percentage of users who review their spending will increase."

A useful hypothesis contains:
    - intervention
    - target behavior
    - expected effect
    - measurable metric
    - timeframe when appropriate
"""


@dataclass
class Hypothesis:
    assumption: str
    intervention: str
    expected_behavior: str
    metric: str
    threshold: float

    def statement(self) -> str:
        return (
            f"If {self.intervention}, then {self.expected_behavior}, "
            f"measured using {self.metric}, with a target of {self.threshold}."
        )


hypothesis = Hypothesis(
    assumption="Users need faster spending feedback.",
    intervention="we show a weekly spending summary",
    expected_behavior="more users will review their spending",
    metric="weekly review rate",
    threshold=0.20,
)

print("\nHYPOTHESIS")
print(hypothesis.statement())


# ============================================================================
# 9. ASSUMPTIONS AND RISK
# ============================================================================

class AssumptionType(Enum):
    DESIRABILITY = "customer wants it"
    FEASIBILITY = "we can build it"
    VIABILITY = "business can sustain it"
    USABILITY = "customers can use it"
    COMPLIANCE = "it satisfies applicable rules"


@dataclass
class Assumption:
    statement: str
    assumption_type: AssumptionType
    impact: int
    uncertainty: int

    @property
    def risk_score(self) -> int:
        return self.impact * self.uncertainty


assumptions = [
    Assumption(
        "Customers want automatic spending categorization.",
        AssumptionType.DESIRABILITY,
        5,
        4,
    ),
    Assumption(
        "Transaction data can be categorized with acceptable accuracy.",
        AssumptionType.FEASIBILITY,
        5,
        3,
    ),
    Assumption(
        "Customers will pay for advanced financial insights.",
        AssumptionType.VIABILITY,
        5,
        5,
    ),
]

print("\nASSUMPTION RISK")
for assumption in sorted(assumptions, key=lambda x: x.risk_score, reverse=True):
    print(
        assumption.assumption_type.value,
        "| risk=",
        assumption.risk_score,
        "|",
        assumption.statement,
    )


# ============================================================================
# 10. EXPERIMENTATION
# ============================================================================

"""
Experimentation is useful when uncertainty is high.

A product experiment should have:
    - explicit hypothesis
    - target population
    - intervention
    - success metric
    - decision threshold
    - duration
    - guardrail metrics
    - interpretation rules

An experiment is not merely "release something and look at analytics."
"""


@dataclass
class Experiment:
    name: str
    hypothesis: str
    primary_metric: str
    baseline: float
    treatment: float
    minimum_success: float

    @property
    def relative_change(self) -> float:
        if self.baseline == 0:
            return float("inf") if self.treatment > 0 else 0
        return (self.treatment - self.baseline) / self.baseline

    @property
    def passed(self) -> bool:
        return self.relative_change >= self.minimum_success


experiment = Experiment(
    name="Weekly spending summary",
    hypothesis="A summary increases weekly review behavior.",
    primary_metric="weekly review rate",
    baseline=0.30,
    treatment=0.36,
    minimum_success=0.15,
)

print("\nEXPERIMENT")
print("Relative change:", round(experiment.relative_change * 100, 2), "%")
print("Passed:", experiment.passed)


# ============================================================================
# 11. EXPERIMENT DESIGN: SAMPLE SIZE INTUITION
# ============================================================================

def proportion_difference(control: int, control_successes: int,
                          treatment: int, treatment_successes: int) -> float:
    """Calculate absolute difference between two observed proportions."""
    if control <= 0 or treatment <= 0:
        raise ValueError("Group sizes must be positive.")

    control_rate = control_successes / control
    treatment_rate = treatment_successes / treatment
    return treatment_rate - control_rate


difference = proportion_difference(
    control=1000,
    control_successes=300,
    treatment=1000,
    treatment_successes=360,
)

print("\nOBSERVED EXPERIMENT DIFFERENCE")
print(round(difference * 100, 2), "percentage points")


# ============================================================================
# 12. METRICS: INPUT, OUTPUT, OUTCOME, GUARDRAIL
# ============================================================================

"""
Metric categories:

Input metrics:
    Resources consumed.
    Example: engineering hours.

Output metrics:
    What was produced.
    Example: number of features shipped.

Behavior metrics:
    What customers do.
    Example: percentage completing onboarding.

Outcome metrics:
    What changes for customers or the business.
    Example: successful activation rate.

Guardrail metrics:
    Metrics that must not deteriorate while optimizing the primary metric.
    Example: support contacts or fraud rate.
"""


@dataclass
class Metric:
    name: str
    category: str
    value: float
    unit: str

    def display(self) -> str:
        return f"{self.name}: {self.value} {self.unit} [{self.category}]"


metrics = [
    Metric("Engineering hours", "input", 800, "hours"),
    Metric("Features shipped", "output", 12, "features"),
    Metric("Activation rate", "behavior", 0.62, "rate"),
    Metric("Customer retention", "outcome", 0.74, "rate"),
    Metric("Support tickets", "guardrail", 145, "tickets"),
]

print("\nMETRIC TYPES")
for metric in metrics:
    print(metric.display())


# ============================================================================
# 13. NORTH STAR METRIC
# ============================================================================

"""
A North Star Metric attempts to represent sustained customer value delivered
by the product.

It should not be a vanity metric.

Examples depend on the product:
    - completed learning sessions
    - successful transactions
    - meaningful weekly collaboration
    - completed deliveries

The metric should be connected to customer value and long-term business
health. It should not be selected merely because it is easy to increase.
"""


@dataclass
class MetricTree:
    north_star: str
    drivers: Dict[str, List[str]]

    def show(self) -> None:
        print(self.north_star)
        for driver, metrics_for_driver in self.drivers.items():
            print(f"  {driver}")
            for metric_name in metrics_for_driver:
                print(f"    - {metric_name}")


metric_tree = MetricTree(
    north_star="Successful weekly financial decisions",
    drivers={
        "Data quality": ["categorization accuracy", "transaction coverage"],
        "Engagement": ["weekly review rate", "insight open rate"],
        "Trust": ["error reports", "support complaints"],
    },
)

print("\nMETRIC TREE")
metric_tree.show()


# ============================================================================
# 14. FUNNEL THINKING
# ============================================================================

def funnel_rates(stages: Sequence[Tuple[str, int]]) -> List[Tuple[str, float]]:
    """
    Convert funnel counts into conversion rates relative to the first stage.
    """
    if not stages:
        return []

    initial = stages[0][1]
    if initial <= 0:
        raise ValueError("Initial funnel count must be positive.")

    return [(name, count / initial) for name, count in stages]


funnel = [
    ("Visitors", 10000),
    ("Signups", 3000),
    ("Activated", 1800),
    ("Paid", 450),
]

print("\nFUNNEL")
for stage, rate in funnel_rates(funnel):
    print(stage, round(rate * 100, 2), "% of initial users")


# ============================================================================
# 15. RETENTION AND COHORT THINKING
# ============================================================================

def retention_rate(starting_users: int, retained_users: int) -> float:
    if starting_users <= 0:
        raise ValueError("Starting users must be positive.")
    if retained_users < 0 or retained_users > starting_users:
        raise ValueError("Retained users must be between zero and starting users.")
    return retained_users / starting_users


print("\nRETENTION")
print("Week 4 retention:", retention_rate(1000, 420))


# ============================================================================
# 16. AARRR / PIRATE FUNNEL
# ============================================================================

"""
AARRR commonly refers to:
    Acquisition
    Activation
    Retention
    Revenue
    Referral

It is a useful behavioral framework, not a universal product-management law.

A product manager should adapt the model to the actual product.
"""


@dataclass
class AARRRMetrics:
    acquisition: int
    activation: int
    retention: int
    revenue_customers: int
    referrals: int

    def conversion_rates(self) -> Dict[str, float]:
        if self.acquisition <= 0:
            raise ValueError("Acquisition must be positive.")

        return {
            "activation": self.activation / self.acquisition,
            "retention": self.retention / self.activation
            if self.activation
            else 0,
            "revenue": self.revenue_customers / self.retention
            if self.retention
            else 0,
            "referral": self.referrals / self.revenue_customers
            if self.revenue_customers
            else 0,
        }


aarrr = AARRRMetrics(10000, 4000, 1800, 600, 150)
print("\nAARRR")
print(aarrr.conversion_rates())


# ============================================================================
# 17. PRIORITIZATION: RICE
# ============================================================================

"""
RICE is one prioritization framework:

RICE = Reach * Impact * Confidence / Effort

Reach:
    Number of customers affected in the chosen period.

Impact:
    Estimated effect per affected customer.

Confidence:
    Confidence in the estimates.

Effort:
    Relative amount of work.

The formula does not produce objective truth. It makes assumptions visible.
"""


@dataclass
class RICEItem:
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
    RICEItem("Automatic categorization", 5000, 3, 0.8, 10),
    RICEItem("Dark mode", 7000, 0.5, 0.9, 4),
    RICEItem("Advanced reports", 2000, 2, 0.7, 8),
]

print("\nRICE PRIORITIZATION")
for item in sorted(rice_items, key=lambda x: x.score(), reverse=True):
    print(item.name, "=", round(item.score(), 2))


# ============================================================================
# 18. VALUE VS EFFORT
# ============================================================================

@dataclass
class ValueEffortItem:
    name: str
    value: float
    effort: float

    @property
    def value_density(self) -> float:
        if self.effort <= 0:
            raise ValueError("Effort must be positive.")
        return self.value / self.effort


value_effort_items = [
    ValueEffortItem("Improve onboarding copy", 7, 2),
    ValueEffortItem("Build analytics platform", 10, 10),
    ValueEffortItem("Add profile customization", 4, 3),
]

print("\nVALUE / EFFORT")
for item in sorted(
    value_effort_items,
    key=lambda x: x.value_density,
    reverse=True,
):
    print(item.name, round(item.value_density, 2))


# ============================================================================
# 19. KANO MODEL
# ============================================================================

"""
Kano categorizes product attributes by their relationship with satisfaction.

Common categories:
    Must-be:
        Expected. Absence creates dissatisfaction.

    Performance:
        Better performance generally produces more satisfaction.

    Delighters:
        Unexpected benefits that can increase satisfaction.

    Indifferent:
        Little meaningful effect on satisfaction.

    Reverse:
        Some customers may dislike the feature.

Classification is customer- and context-dependent.
"""


class KanoCategory(Enum):
    MUST_BE = "Must-be"
    PERFORMANCE = "Performance"
    DELIGHTER = "Delighter"
    INDIFFERENT = "Indifferent"
    REVERSE = "Reverse"


@dataclass
class KanoFeature:
    name: str
    category: KanoCategory
    rationale: str


kano_features = [
    KanoFeature(
        "Secure login",
        KanoCategory.MUST_BE,
        "Customers expect basic account security.",
    ),
    KanoFeature(
        "Faster reports",
        KanoCategory.PERFORMANCE,
        "Improved speed directly affects perceived utility.",
    ),
    KanoFeature(
        "Personalized spending insight",
        KanoCategory.DELIGHTER,
        "Unexpected useful insight may increase satisfaction.",
    ),
]


print("\nKANO CLASSIFICATION")
for feature in kano_features:
    print(feature.name, "->", feature.category.value)


# ============================================================================
# 20. CUSTOMER JOURNEY THINKING
# ============================================================================

@dataclass
class JourneyStage:
    name: str
    customer_goal: str
    pain_point: str
    opportunity: str


journey = [
    JourneyStage(
        "Discover",
        "Understand whether the product is relevant.",
        "Value proposition is unclear.",
        "Communicate a concrete customer outcome.",
    ),
    JourneyStage(
        "Onboard",
        "Reach first useful outcome.",
        "Too much setup before value.",
        "Shorten time-to-value.",
    ),
    JourneyStage(
        "Use",
        "Complete the primary job.",
        "Important information is difficult to find.",
        "Improve information architecture.",
    ),
    JourneyStage(
        "Retain",
        "Continue receiving value.",
        "Value is not consistently visible.",
        "Improve recurring value loops.",
    ),
]

print("\nCUSTOMER JOURNEY")
for stage in journey:
    print(stage.name, "| goal:", stage.customer_goal)
    print("  pain:", stage.pain_point)
    print("  opportunity:", stage.opportunity)


# ============================================================================
# 21. JOBS TO BE DONE
# ============================================================================

"""
Jobs-to-be-Done focuses on the progress customers are trying to make.

A job can be:
    - functional
    - emotional
    - social

Example:
    "Help me understand my spending before payday so I can avoid unpleasant
     financial surprises."

The product is a means of accomplishing progress, not necessarily the job
itself.
"""


@dataclass
class CustomerJob:
    situation: str
    motivation: str
    desired_outcome: str

    def formulate(self) -> str:
        return (
            f"When {self.situation}, I want to {self.motivation}, "
            f"so I can {self.desired_outcome}."
        )


job = CustomerJob(
    situation="I am approaching the end of the month",
    motivation="understand my remaining discretionary budget",
    desired_outcome="avoid unexpected overspending",
)

print("\nJOB TO BE DONE")
print(job.formulate())


# ============================================================================
# 22. PERSONAS AND SEGMENTATION
# ============================================================================

@dataclass
class Segment:
    name: str
    population: int
    problem_frequency: float
    willingness_to_pay: float
    strategic_fit: float

    def attractiveness(self) -> float:
        return (
            self.population
            * self.problem_frequency
            * self.willingness_to_pay
            * self.strategic_fit
        )


segments = [
    Segment("Young professionals", 100000, 0.8, 0.6, 0.9),
    Segment("Students", 200000, 0.5, 0.2, 0.7),
    Segment("Small business owners", 50000, 0.9, 0.9, 0.8),
]

print("\nSEGMENT ATTRACTIVENESS")
for segment in sorted(
    segments,
    key=lambda item: item.attractiveness(),
    reverse=True,
):
    print(segment.name, round(segment.attractiveness(), 2))


# ============================================================================
# 23. MARKET AND COMPETITIVE THINKING
# ============================================================================

"""
A PM should distinguish:

Competitor:
    A product directly or indirectly competing for the same customer need.

Alternative:
    Any method the customer can use to accomplish the job.

Substitute:
    A different category of solution satisfying a similar need.

Competition therefore includes:
    - direct products
    - adjacent products
    - manual processes
    - spreadsheets
    - internal workflows
    - doing nothing
"""


@dataclass
class Alternative:
    name: str
    customer_value: float
    switching_cost: float
    weakness: float

    def opportunity_score(self) -> float:
        return self.customer_value + self.weakness - self.switching_cost


alternatives = [
    Alternative("Spreadsheet", 7, 2, 5),
    Alternative("Manual bank review", 5, 1, 6),
    Alternative("Existing finance app", 8, 4, 3),
    Alternative("Do nothing", 3, 0, 8),
]

print("\nALTERNATIVE ANALYSIS")
for alternative in alternatives:
    print(alternative.name, alternative.opportunity_score())


# ============================================================================
# 24. BUSINESS MODEL THINKING
# ============================================================================

"""
A product manager should understand how product value becomes business value.

Common business model components include:
    - customer segments
    - value proposition
    - channels
    - revenue streams
    - cost structure
    - key activities
    - partnerships
    - retention economics

A useful distinction:

Customer value:
    What the customer gains.

Business value:
    What the organization gains.

A product must be able to reconcile both.
"""


@dataclass
class UnitEconomics:
    average_revenue_per_customer: float
    variable_cost_per_customer: float
    acquisition_cost: float

    @property
    def contribution_margin(self) -> float:
        return (
            self.average_revenue_per_customer
            - self.variable_cost_per_customer
        )

    @property
    def ltv_to_cac(self) -> float:
        if self.acquisition_cost <= 0:
            raise ValueError("Acquisition cost must be positive.")
        return self.contribution_margin / self.acquisition_cost


economics = UnitEconomics(
    average_revenue_per_customer=1200,
    variable_cost_per_customer=300,
    acquisition_cost=450,
)

print("\nUNIT ECONOMICS")
print("Contribution margin:", economics.contribution_margin)
print("LTV/CAC proxy:", round(economics.ltv_to_cac, 2))


# ============================================================================
# 25. PRICING THINKING
# ============================================================================

@dataclass
class PricingScenario:
    price: float
    customers: int
    variable_cost_per_customer: float

    @property
    def revenue(self) -> float:
        return self.price * self.customers

    @property
    def contribution(self) -> float:
        return (
            self.price - self.variable_cost_per_customer
        ) * self.customers


pricing_scenarios = [
    PricingScenario(499, 10000, 150),
    PricingScenario(799, 7000, 150),
    PricingScenario(999, 5000, 150),
]

print("\nPRICING SCENARIOS")
for scenario in pricing_scenarios:
    print(
        "price=", scenario.price,
        "revenue=", scenario.revenue,
        "contribution=", scenario.contribution,
    )


# ============================================================================
# 26. PRODUCT STRATEGY
# ============================================================================

"""
Strategy connects:

    Mission
       ↓
    Target customer
       ↓
    Customer problem
       ↓
    Product value proposition
       ↓
    Strategic choices
       ↓
    Capabilities
       ↓
    Metrics
       ↓
    Execution

Strategy requires choices.

A strategy that says "serve everyone and build everything" does not provide
useful direction.
"""


@dataclass
class ProductStrategy:
    target_customer: str
    problem: str
    differentiation: str
    strategic_metric: str
    non_goals: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        issues = []

        if not self.target_customer:
            issues.append("Target customer is undefined.")
        if not self.problem:
            issues.append("Problem is undefined.")
        if not self.differentiation:
            issues.append("Differentiation is undefined.")
        if not self.strategic_metric:
            issues.append("Strategic metric is undefined.")
        if not self.non_goals:
            issues.append("No explicit non-goals have been defined.")

        return issues


strategy = ProductStrategy(
    target_customer="Professionals with irregular monthly spending",
    problem="They cannot quickly understand whether spending is on track.",
    differentiation="Fast, trustworthy, actionable financial explanations.",
    strategic_metric="weekly successful financial reviews",
    non_goals=["full-service banking", "investment brokerage"],
)

print("\nSTRATEGY VALIDATION")
for issue in strategy.validate():
    print("Issue:", issue)


# ============================================================================
# 27. PRODUCT VISION VS STRATEGY VS ROADMAP
# ============================================================================

"""
Vision:
    Desired future state.

Strategy:
    Choices about how to move toward that future state.

Roadmap:
    A communication and planning representation of intended product work.

Backlog:
    A more detailed collection of work items.

These are not interchangeable.
"""


@dataclass
class ProductPlanningLayers:
    vision: str
    strategy: str
    roadmap_themes: List[str]
    backlog_items: List[str]


planning_layers = ProductPlanningLayers(
    vision="Help people make confident everyday financial decisions.",
    strategy="Win through trustworthy, fast, personalized spending insights.",
    roadmap_themes=[
        "Reduce time-to-insight",
        "Improve data trust",
        "Increase recurring value",
    ],
    backlog_items=[
        "Improve categorization feedback",
        "Add weekly insight card",
        "Reduce onboarding fields",
    ],
)

print("\nPLANNING LAYERS")
print("Vision:", planning_layers.vision)
print("Strategy:", planning_layers.strategy)
print("Roadmap:", planning_layers.roadmap_themes)
print("Backlog:", planning_layers.backlog_items)


# ============================================================================
# 28. OUTCOME-BASED ROADMAP
# ============================================================================

@dataclass
class Outcome:
    name: str
    baseline: float
    target: float

    def gap(self) -> float:
        return self.target - self.baseline


outcomes = [
    Outcome("Activation", 0.40, 0.60),
    Outcome("Weekly engagement", 0.25, 0.40),
    Outcome("Retention", 0.50, 0.65),
]

print("\nOUTCOME-BASED ROADMAP")
for item in outcomes:
    print(item.name, "gap=", round(item.gap(), 2))


# ============================================================================
# 29. DISCOVERY VS DELIVERY
# ============================================================================

"""
Product discovery:
    Determine whether the team should solve a problem and what solution is
    likely to work.

Product delivery:
    Build, test, release, operate, and improve the chosen solution.

They overlap continuously.

A strong team does not perform discovery once and then blindly execute a
fixed plan.
"""


@dataclass
class DiscoveryQuestion:
    question: str
    evidence_needed: str


discovery_questions = [
    DiscoveryQuestion(
        "Is this a meaningful customer problem?",
        "Interview evidence, behavioral data, support patterns.",
    ),
    DiscoveryQuestion(
        "Will customers use the proposed behavior?",
        "Prototype tests or controlled experiments.",
    ),
    DiscoveryQuestion(
        "Can the system support the experience?",
        "Technical feasibility investigation.",
    ),
    DiscoveryQuestion(
        "Can the business sustain the model?",
        "Economic analysis and pricing evidence.",
    ),
]

print("\nDISCOVERY QUESTIONS")
for question in discovery_questions:
    print(question.question)
    print("  Evidence:", question.evidence_needed)


# ============================================================================
# 30. MVP THINKING
# ============================================================================

"""
MVP means Minimum Viable Product.

The purpose is not:
    "Build the smallest possible software."

The purpose is:
    "Create the smallest credible product or experiment capable of testing
     an important assumption and delivering real value."

An MVP may be:
    - manual service
    - prototype
    - concierge workflow
    - limited feature
    - landing page experiment
    - operational pilot

The appropriate MVP depends on the uncertainty being tested.
"""


@dataclass
class MVP:
    assumption: str
    minimum_capability: str
    learning_metric: str

    def describe(self) -> str:
        return (
            f"Assumption: {self.assumption}\n"
            f"Minimum capability: {self.minimum_capability}\n"
            f"Learning metric: {self.learning_metric}"
        )


mvp = MVP(
    assumption="Users value personalized weekly spending advice.",
    minimum_capability="Manually prepare weekly spending insights for a pilot group.",
    learning_metric="percentage of pilot users who act on the advice",
)

print("\nMVP")
print(mvp.describe())


# ============================================================================
# 31. USER STORIES
# ============================================================================

@dataclass
class UserStory:
    role: str
    action: str
    benefit: str

    def format(self) -> str:
        return f"As a {self.role}, I want to {self.action}, so that {self.benefit}."


story = UserStory(
    role="customer",
    action="see my weekly spending trend",
    benefit="I can identify whether my spending is increasing",
)

print("\nUSER STORY")
print(story.format())


# ============================================================================
# 32. ACCEPTANCE CRITERIA
# ============================================================================

@dataclass
class AcceptanceCriterion:
    condition: str
    expected_result: str

    def format(self) -> str:
        return f"Given {self.condition}, the system should {self.expected_result}."


criteria = [
    AcceptanceCriterion(
        "the customer has at least seven days of categorized transactions",
        "display the weekly spending trend",
    ),
    AcceptanceCriterion(
        "there is insufficient transaction data",
        "explain why the trend cannot yet be calculated",
    ),
]

print("\nACCEPTANCE CRITERIA")
for criterion in criteria:
    print(criterion.format())


# ============================================================================
# 33. PRODUCT REQUIREMENTS AND QUALITY
# ============================================================================

"""
A useful product requirement distinguishes:

Functional requirement:
    What the system should do.

Non-functional requirement:
    How well it should behave.

Examples of non-functional requirements:
    - latency
    - reliability
    - availability
    - accessibility
    - privacy
    - security
    - scalability
    - observability
"""


@dataclass
class Requirement:
    identifier: str
    requirement_type: str
    statement: str
    priority: str


requirements = [
    Requirement(
        "FR-001",
        "Functional",
        "The system shall display categorized weekly spending.",
        "Must",
    ),
    Requirement(
        "NFR-001",
        "Performance",
        "The weekly summary should load within the defined latency objective.",
        "Must",
    ),
    Requirement(
        "NFR-002",
        "Security",
        "Sensitive financial information shall be protected according to applicable controls.",
        "Must",
    ),
]

print("\nREQUIREMENTS")
for requirement in requirements:
    print(
        requirement.identifier,
        "|",
        requirement.requirement_type,
        "|",
        requirement.priority,
        "|",
        requirement.statement,
    )


# ============================================================================
# 34. TRADE-OFF THINKING
# ============================================================================

"""
Product decisions frequently involve competing objectives.

Examples:
    speed vs quality
    scope vs schedule
    personalization vs privacy
    convenience vs security
    flexibility vs simplicity
    growth vs monetization
    short-term revenue vs long-term retention

A mature PM makes the trade-off explicit.
"""


@dataclass
class TradeOff:
    decision: str
    benefit: str
    cost: str
    risk: str

    def communicate(self) -> str:
        return (
            f"Decision: {self.decision}\n"
            f"Benefit: {self.benefit}\n"
            f"Cost: {self.cost}\n"
            f"Risk: {self.risk}"
        )


tradeoff = TradeOff(
    decision="Launch with manual categorization correction before automation.",
    benefit="Faster learning about category errors.",
    cost="Higher operational workload.",
    risk="Pilot scale may be limited.",
)

print("\nTRADE-OFF")
print(tradeoff.communicate())


# ============================================================================
# 35. DECISION MATRICES
# ============================================================================

@dataclass
class DecisionOption:
    name: str
    customer_value: float
    business_value: float
    feasibility: float
    risk_penalty: float

    def weighted_score(
        self,
        customer_weight: float = 0.35,
        business_weight: float = 0.30,
        feasibility_weight: float = 0.25,
        risk_weight: float = 0.10,
    ) -> float:
        return (
            self.customer_value * customer_weight
            + self.business_value * business_weight
            + self.feasibility * feasibility_weight
            - self.risk_penalty * risk_weight
        )


options = [
    DecisionOption("Manual pilot", 9, 6, 9, 2),
    DecisionOption("Full automation", 10, 9, 4, 7),
    DecisionOption("Dashboard only", 6, 5, 9, 1),
]

print("\nDECISION MATRIX")
for option in sorted(
    options,
    key=lambda x: x.weighted_score(),
    reverse=True,
):
    print(option.name, round(option.weighted_score(), 2))


# ============================================================================
# 36. STAKEHOLDER MANAGEMENT
# ============================================================================

"""
Stakeholder management is not about pleasing everyone.

It involves understanding:
    - interests
    - influence
    - information needs
    - incentives
    - concerns
    - decision rights

A useful distinction is:
    Who decides?
    Who contributes?
    Who executes?
    Who is affected?
"""


@dataclass
class Stakeholder:
    name: str
    influence: int
    interest: int
    concern: str

    def engagement_level(self) -> str:
        score = self.influence * self.interest

        if score >= 16:
            return "Manage closely"
        if score >= 8:
            return "Keep engaged"
        return "Monitor"


stakeholders = [
    Stakeholder("Engineering Lead", 5, 5, "Architecture and delivery risk"),
    Stakeholder("Finance", 4, 3, "Unit economics"),
    Stakeholder("Customer Support", 3, 5, "Support workload"),
    Stakeholder("Executive Sponsor", 5, 4, "Strategic impact"),
]

print("\nSTAKEHOLDER ANALYSIS")
for stakeholder in stakeholders:
    print(
        stakeholder.name,
        "->",
        stakeholder.engagement_level(),
        "| concern:",
        stakeholder.concern,
    )


# ============================================================================
# 37. COMMUNICATION AS A PRODUCT MANAGEMENT SKILL
# ============================================================================

@dataclass
class DecisionRecord:
    decision: str
    context: str
    evidence: List[str]
    alternatives_rejected: List[str]
    risks: List[str]

    def format(self) -> str:
        return (
            f"Decision: {self.decision}\n"
            f"Context: {self.context}\n"
            f"Evidence: {', '.join(self.evidence)}\n"
            f"Rejected alternatives: {', '.join(self.alternatives_rejected)}\n"
            f"Risks: {', '.join(self.risks)}"
        )


decision = DecisionRecord(
    decision="Run a manual pilot before building automation.",
    context="Automation demand is plausible but willingness to act on insights is uncertain.",
    evidence=[
        "Customer interviews show recurring spending confusion.",
        "Prototype users opened weekly insights.",
    ],
    alternatives_rejected=[
        "Build the full automation system immediately",
        "Ship a generic dashboard",
    ],
    risks=[
        "Manual process may not scale",
        "Pilot results may not generalize",
    ],
)

print("\nDECISION RECORD")
print(decision.format())


# ============================================================================
# 38. ANALYTICAL THINKING: MEAN, MEDIAN, DISTRIBUTION
# ============================================================================

response_times = [2, 3, 3, 4, 5, 5, 6, 7, 40]

print("\nDATA ANALYSIS")
print("Mean:", round(mean(response_times), 2))
print("Median:", median(response_times))

"""
The large value of 40 demonstrates why averages can hide distribution shape.

A PM should inspect:
    - median
    - percentiles
    - distribution
    - outliers
    - segmentation
    - time trends

A single average rarely explains user behavior.
"""


# ============================================================================
# 39. PERCENTILES
# ============================================================================

def percentile_nearest_rank(values: Sequence[float], percentile: float) -> float:
    """
    Simple nearest-rank percentile implementation.

    This intentionally uses a transparent definition for educational purposes.
    Production analytics systems may use different percentile interpolation
    methods.
    """
    if not values:
        raise ValueError("Values cannot be empty.")
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100.")

    sorted_values = sorted(values)
    rank = max(1, int((percentile / 100) * len(sorted_values) + 0.999999))
    return sorted_values[rank - 1]


print("\nPERCENTILES")
for p in [50, 90, 95, 99]:
    print(f"P{p}:", percentile_nearest_rank(response_times, p))


# ============================================================================
# 40. CORRELATION IS NOT CAUSATION
# ============================================================================

"""
If users who receive notifications retain better, several explanations are
possible:

    - notifications cause better retention
    - highly engaged users are more likely to enable notifications
    - a third factor causes both

Therefore observational correlation does not automatically establish causal
impact.

Controlled experimentation can strengthen causal inference, although
experiments themselves require careful design.
"""


def correlation(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Sequences must have equal length and at least two values.")

    x_mean = mean(x)
    y_mean = mean(y)

    numerator = sum(
        (a - x_mean) * (b - y_mean)
        for a, b in zip(x, y)
    )

    x_variance = sum((a - x_mean) ** 2 for a in x)
    y_variance = sum((b - y_mean) ** 2 for b in y)

    denominator = sqrt(x_variance * y_variance)

    if denominator == 0:
        return 0.0

    return numerator / denominator


notifications = [0, 0, 1, 1, 1, 0, 1, 0]
retention = [0, 0, 1, 1, 1, 0, 1, 0]

print("\nCORRELATION EXAMPLE")
print("Correlation:", correlation(notifications, retention))


# ============================================================================
# 41. SEGMENTATION
# ============================================================================

@dataclass
class User:
    user_id: int
    segment: str
    activated: bool
    retained: bool
    revenue: float


users = [
    User(1, "professional", True, True, 100),
    User(2, "professional", True, True, 100),
    User(3, "professional", True, False, 0),
    User(4, "student", True, False, 0),
    User(5, "student", False, False, 0),
    User(6, "professional", True, True, 100),
]


def segment_retention(users: Iterable[User]) -> Dict[str, float]:
    grouped: Dict[str, List[User]] = {}

    for user in users:
        grouped.setdefault(user.segment, []).append(user)

    result = {}

    for segment, segment_users in grouped.items():
        result[segment] = (
            sum(user.retained for user in segment_users)
            / len(segment_users)
        )

    return result


print("\nSEGMENT RETENTION")
print(segment_retention(users))


# ============================================================================
# 42. EXPERIMENT GUARDRAILS
# ============================================================================

@dataclass
class ExperimentResult:
    primary_metric_change: float
    conversion_change: float
    complaint_change: float
    error_change: float

    def decision(self) -> str:
        """
        A deliberately simple rule illustrating guardrails.

        Primary metric must improve while serious guardrails remain within
        acceptable deterioration.
        """
        if self.primary_metric_change < 0.10:
            return "Do not scale: primary metric improvement is insufficient."

        if self.complaint_change > 0.05:
            return "Do not scale: complaints increased too much."

        if self.error_change > 0.02:
            return "Do not scale: error rate increased too much."

        return "Eligible for controlled expansion."


experiment_result = ExperimentResult(
    primary_metric_change=0.14,
    conversion_change=0.08,
    complaint_change=0.01,
    error_change=0.005,
)

print("\nEXPERIMENT GUARDRAILS")
print(experiment_result.decision())


# ============================================================================
# 43. PRODUCT ANALYTICS EVENT DESIGN
# ============================================================================

@dataclass
class AnalyticsEvent:
    event_name: str
    user_id: int
    properties: Dict[str, object]

    def validate(self) -> List[str]:
        errors = []

        if not self.event_name:
            errors.append("Event name is required.")

        if self.user_id <= 0:
            errors.append("User ID must be positive.")

        if not isinstance(self.properties, dict):
            errors.append("Properties must be a dictionary.")

        return errors


event = AnalyticsEvent(
    "weekly_insight_opened",
    101,
    {"insight_type": "spending_trend", "source": "home"},
)

print("\nANALYTICS EVENT")
print("Validation errors:", event.validate())


# ============================================================================
# 44. DATA QUALITY
# ============================================================================

def validate_metric_series(values: Sequence[float]) -> Dict[str, object]:
    errors = []

    if not values:
        errors.append("Series is empty.")

    if any(value < 0 for value in values):
        errors.append("Negative values detected.")

    if any(value != value for value in values):
        errors.append("NaN-like value detected.")

    return {
        "valid": not errors,
        "errors": errors,
        "count": len(values),
    }


print("\nDATA QUALITY")
print(validate_metric_series([10, 20, 30, 40]))


# ============================================================================
# 45. TECHNICAL AWARENESS
# ============================================================================

"""
A product manager does not need to implement every technical component.

Technical awareness means understanding enough to ask good questions:

Architecture:
    What systems are involved?

APIs:
    How do systems communicate?

Databases:
    Where is the data stored?

Latency:
    How quickly must a response arrive?

Scalability:
    What happens as traffic increases?

Reliability:
    What happens when dependencies fail?

Security:
    Who can access the data?

Privacy:
    What data is collected and why?

Observability:
    How will failures be detected?

Technical debt:
    What future cost is created by a shortcut?
"""


@dataclass
class TechnicalConstraint:
    category: str
    constraint: str
    product_impact: str


technical_constraints = [
    TechnicalConstraint(
        "Latency",
        "Insight generation depends on an external data service.",
        "User experience may degrade if the dependency is slow.",
    ),
    TechnicalConstraint(
        "Reliability",
        "Categorization service may temporarily fail.",
        "The product needs graceful fallback behavior.",
    ),
    TechnicalConstraint(
        "Privacy",
        "Financial transactions are sensitive information.",
        "Access controls, retention, and data handling require careful design.",
    ),
]

print("\nTECHNICAL CONSTRAINTS")
for constraint in technical_constraints:
    print(
        constraint.category,
        "|",
        constraint.constraint,
        "| impact:",
        constraint.product_impact,
    )


# ============================================================================
# 46. FAILURE MODES
# ============================================================================

@dataclass
class FailureMode:
    failure: str
    likelihood: int
    impact: int
    mitigation: str

    @property
    def risk_priority(self) -> int:
        return self.likelihood * self.impact


failure_modes = [
    FailureMode(
        "Incorrect transaction categorization",
        4,
        5,
        "Provide correction mechanisms and monitor accuracy.",
    ),
    FailureMode(
        "Insight generation unavailable",
        2,
        4,
        "Provide cached or graceful fallback information.",
    ),
    FailureMode(
        "Excessive notifications",
        3,
        3,
        "Use frequency controls and customer preferences.",
    ),
]

print("\nFAILURE MODE PRIORITIZATION")
for failure in sorted(
    failure_modes,
    key=lambda item: item.risk_priority,
    reverse=True,
):
    print(
        failure.failure,
        "| risk=",
        failure.risk_priority,
        "| mitigation=",
        failure.mitigation,
    )


# ============================================================================
# 47. SECURITY MINDSET
# ============================================================================

"""
Security is a product concern whenever product decisions affect:

    - authentication
    - authorization
    - sensitive data
    - payment information
    - identity
    - account recovery
    - integrations
    - logging
    - third-party services

Product questions include:
    Who should access this?
    What is the minimum data required?
    What happens if an account is compromised?
    What should be logged?
    What information must not be exposed?
    What are the abuse cases?

Security should be considered during discovery and design rather than only
after implementation.
"""


@dataclass
class SecurityQuestion:
    question: str
    reason: str


security_questions = [
    SecurityQuestion(
        "Who is authorized to view the data?",
        "Prevents inappropriate access.",
    ),
    SecurityQuestion(
        "What is the minimum data required?",
        "Reduces unnecessary data exposure.",
    ),
    SecurityQuestion(
        "What happens after repeated failed authentication?",
        "Helps reason about abuse and account protection.",
    ),
    SecurityQuestion(
        "Can sensitive information appear in logs?",
        "Logs may have broad access and long retention.",
    ),
]

print("\nSECURITY QUESTIONS")
for item in security_questions:
    print(item.question)
    print("  Reason:", item.reason)


# ============================================================================
# 48. PRIVACY BY DESIGN
# ============================================================================

@dataclass
class DataDecision:
    data_element: str
    purpose: str
    necessary: bool
    sensitivity: str

    def decision(self) -> str:
        if not self.necessary:
            return "Reconsider collection."
        if self.sensitivity.lower() == "high":
            return "Collect only with strong justification and appropriate controls."
        return "Collection may be justified if properly controlled."


data_decisions = [
    DataDecision(
        "Transaction amount",
        "Calculate spending trends",
        True,
        "high",
    ),
    DataDecision(
        "Favorite color",
        "Personalize interface",
        False,
        "low",
    ),
]

print("\nPRIVACY BY DESIGN")
for item in data_decisions:
    print(item.data_element, "->", item.decision())


# ============================================================================
# 49. ACCESSIBILITY
# ============================================================================

"""
Accessibility is part of product quality.

A PM should consider:
    - keyboard access
    - screen readers
    - color contrast
    - readable text
    - touch target size
    - captions where relevant
    - understandable error messages
    - cognitive load

Accessibility should not be treated as an optional cosmetic enhancement.
"""


@dataclass
class AccessibilityCheck:
    criterion: str
    passed: bool
    rationale: str


accessibility_checks = [
    AccessibilityCheck(
        "Important information does not rely solely on color.",
        True,
        "Users should have another signal.",
    ),
    AccessibilityCheck(
        "Interactive elements have meaningful labels.",
        True,
        "Labels support assistive technologies.",
    ),
    AccessibilityCheck(
        "Errors explain how to recover.",
        True,
        "Users need actionable feedback.",
    ),
]

print("\nACCESSIBILITY CHECKS")
for check in accessibility_checks:
    print(check.criterion, "->", "PASS" if check.passed else "FAIL")


# ============================================================================
# 50. ETHICAL PRODUCT THINKING
# ============================================================================

"""
A feature can be technically feasible, commercially attractive, and still
create unacceptable harm.

Ethical product questions include:
    - Who benefits?
    - Who might be harmed?
    - Is consent meaningful?
    - Is the experience manipulative?
    - Are vulnerable users disproportionately affected?
    - Are incentives aligned with customer interests?
    - Are important limitations disclosed?

Dark patterns can produce short-term conversion while damaging trust.
"""


@dataclass
class EthicalReview:
    mechanism: str
    customer_benefit: str
    potential_harm: str
    mitigation: str


ethical_review = EthicalReview(
    mechanism="Defaulting customers into frequent notifications",
    customer_benefit="Important insights may be noticed sooner.",
    potential_harm="Customers may feel manipulated or overwhelmed.",
    mitigation="Use clear opt-in controls and reasonable defaults.",
)

print("\nETHICAL REVIEW")
print("Mechanism:", ethical_review.mechanism)
print("Benefit:", ethical_review.customer_benefit)
print("Potential harm:", ethical_review.potential_harm)
print("Mitigation:", ethical_review.mitigation)


# ============================================================================
# 51. EXPERIMENTATION ETHICS
# ============================================================================

"""
Not every experiment is acceptable merely because it is statistically useful.

Experiments should consider:
    - informed consent where required
    - privacy
    - potential harm
    - fairness
    - vulnerable populations
    - reversibility
    - appropriate review

The ability to measure an outcome does not automatically justify manipulating
that outcome.
"""


@dataclass
class ExperimentEthics:
    intervention: str
    potential_harm: str
    reversible: bool
    approval_required: bool

    def risk_statement(self) -> str:
        if self.potential_harm and not self.reversible:
            return "High caution required: intervention may create difficult-to-reverse harm."
        if self.approval_required:
            return "Appropriate review should occur before launch."
        return "Continue with standard ethical review."


ethics = ExperimentEthics(
    intervention="Change financial notifications",
    potential_harm="Customers may make decisions based on misleading information.",
    reversible=True,
    approval_required=True,
)

print("\nEXPERIMENT ETHICS")
print(ethics.risk_statement())


# ============================================================================
# 52. ROADMAP PRIORITIZATION UNDER CONSTRAINTS
# ============================================================================

def greedy_prioritize(
    items: Sequence[Tuple[str, float, float]],
    capacity: float,
) -> List[str]:
    """
    Select items using value density.

    This is an intentionally simple heuristic. Real prioritization can require
    dependencies, strategic constraints, regulatory work, sequencing, and
    uncertainty that a greedy algorithm cannot capture.
    """
    if capacity < 0:
        raise ValueError("Capacity cannot be negative.")

    ranked = sorted(
        items,
        key=lambda item: item[1] / item[2] if item[2] > 0 else float("inf"),
        reverse=True,
    )

    selected = []
    used = 0.0

    for name, value, effort in ranked:
        if effort <= 0:
            raise ValueError(f"Effort for {name} must be positive.")

        if used + effort <= capacity:
            selected.append(name)
            used += effort

    return selected


roadmap_candidates = [
    ("Onboarding simplification", 9, 3),
    ("Advanced reporting", 10, 7),
    ("Notification redesign", 6, 2),
    ("Theme customization", 3, 2),
]

print("\nCONSTRAINED PRIORITIZATION")
print(greedy_prioritize(roadmap_candidates, capacity=7))


# ============================================================================
# 53. DEPENDENCIES
# ============================================================================

@dataclass
class Dependency:
    item: str
    depends_on: str
    consequence: str


dependencies = [
    Dependency(
        "Personalized insight",
        "Reliable transaction categorization",
        "Insight quality suffers if categorization is inaccurate.",
    ),
    Dependency(
        "Automated categorization",
        "Transaction data integration",
        "Automation cannot operate without sufficient data.",
    ),
]

print("\nDEPENDENCIES")
for dependency in dependencies:
    print(
        dependency.item,
        "depends on",
        dependency.depends_on,
        "->",
        dependency.consequence,
    )


# ============================================================================
# 54. OPPORTUNITY COST
# ============================================================================

"""
Every product decision has opportunity cost.

Choosing:
    Feature A

means the team may not be able to:
    - improve onboarding
    - fix reliability
    - validate another market
    - address technical debt
    - improve retention

The relevant question is not only:
    "Is Feature A valuable?"

It is:
    "Is Feature A more valuable than the best realistic alternative use of
     the same resources?"
"""


@dataclass
class OpportunityCostDecision:
    selected: str
    rejected_alternative: str
    reason: str


opportunity_cost = OpportunityCostDecision(
    selected="Improve onboarding",
    rejected_alternative="Build a new dashboard",
    reason="Activation is currently a larger strategic constraint.",
)

print("\nOPPORTUNITY COST")
print(opportunity_cost)


# ============================================================================
# 55. PRODUCT-MARKET FIT THINKING
# ============================================================================

"""
Product-market fit is not a single universal number.

Useful evidence can include:
    - retention
    - repeated usage
    - organic demand
    - referrals
    - willingness to pay
    - customer pull
    - low dependence on incentives

A product can have strong acquisition but weak retention and therefore still
have a serious value problem.
"""


@dataclass
class PMFEvidence:
    retention: float
    referral_rate: float
    willingness_to_pay: float
    organic_acquisition: float

    def score(self) -> float:
        return mean(
            [
                self.retention,
                self.referral_rate,
                self.willingness_to_pay,
                self.organic_acquisition,
            ]
        )


pmf_evidence = PMFEvidence(0.65, 0.18, 0.55, 0.40)

print("\nPMF EVIDENCE")
print("Illustrative composite:", round(pmf_evidence.score(), 3))


# ============================================================================
# 56. GROWTH MINDSET IN PRODUCT MANAGEMENT
# ============================================================================

"""
Growth is not simply acquiring more users.

Growth can involve:
    - acquisition
    - activation
    - retention
    - monetization
    - referral
    - expansion

A product mindset asks which constraint currently limits sustainable growth.
"""


@dataclass
class GrowthConstraint:
    stage: str
    conversion: float

    @property
    def opportunity(self) -> float:
        return 1 - self.conversion


growth_constraints = [
    GrowthConstraint("Acquisition", 0.20),
    GrowthConstraint("Activation", 0.35),
    GrowthConstraint("Retention", 0.55),
    GrowthConstraint("Paid conversion", 0.12),
]

print("\nGROWTH CONSTRAINTS")
for constraint in sorted(
    growth_constraints,
    key=lambda item: item.opportunity,
    reverse=True,
):
    print(constraint.stage, "opportunity=", round(constraint.opportunity, 2))


# ============================================================================
# 57. FLYWHEELS
# ============================================================================

"""
A flywheel describes reinforcing product or business loops.

Example:

More useful insights
        ↓
More customer engagement
        ↓
More behavioral data
        ↓
Better personalization
        ↓
More useful insights

The loop only works if each connection is causally meaningful and does not
create unacceptable privacy, quality, or incentive problems.
"""


@dataclass
class Flywheel:
    stages: List[str]

    def show(self) -> None:
        for index, stage in enumerate(self.stages, start=1):
            next_stage = self.stages[index % len(self.stages)]
            print(f"{stage} -> {next_stage}")


flywheel = Flywheel(
    [
        "Useful insights",
        "Customer engagement",
        "Behavioral learning",
        "Better personalization",
    ]
)

print("\nFLYWHEEL")
flywheel.show()


# ============================================================================
# 58. PLATFORM THINKING
# ============================================================================

"""
A platform product serves multiple participant groups or enables other
products and services.

Platform questions include:
    - Who are the sides?
    - What value does each side receive?
    - What creates network effects?
    - What prevents low-quality supply?
    - How are trust and safety handled?
    - What happens when one side becomes too powerful?

Network effects can be:
    Direct:
        Value increases as more users of the same type join.

    Indirect:
        Value increases because another participant group grows.
"""


@dataclass
class PlatformSide:
    name: str
    value_from_platform: str
    critical_risk: str


platform_sides = [
    PlatformSide(
        "Customers",
        "Access to useful financial insights.",
        "Loss of trust due to inaccurate information.",
    ),
    PlatformSide(
        "Data providers",
        "A channel for delivering authorized data.",
        "Privacy and authorization failures.",
    ),
]

print("\nPLATFORM THINKING")
for side in platform_sides:
    print(side.name, "| value:", side.value_from_platform)
    print("  risk:", side.critical_risk)


# ============================================================================
# 59. TECHNICAL DEBT
# ============================================================================

@dataclass
class TechnicalDebt:
    shortcut: str
    immediate_benefit: str
    future_cost: str
    interest_rate: int

    def priority(self) -> int:
        return self.interest_rate


technical_debt = [
    TechnicalDebt(
        "Hard-coded category rules",
        "Faster pilot launch",
        "More expensive maintenance as categories grow.",
        4,
    ),
    TechnicalDebt(
        "Limited automated tests",
        "Shorter initial development time",
        "Higher regression risk.",
        5,
    ),
]

print("\nTECHNICAL DEBT")
for debt in sorted(technical_debt, key=lambda x: x.priority(), reverse=True):
    print(
        debt.shortcut,
        "| immediate:",
        debt.immediate_benefit,
        "| future:",
        debt.future_cost,
    )


# ============================================================================
# 60. PRODUCT OPERATIONS
# ============================================================================

"""
A product does not end at launch.

Product operations can involve:
    - monitoring
    - incident response
    - support workflows
    - release management
    - customer feedback
    - analytics quality
    - experimentation
    - documentation
    - governance

A PM should understand operational consequences of product decisions.
"""


@dataclass
class OperationalMetric:
    name: str
    current: float
    threshold: float

    def status(self) -> str:
        return "OK" if self.current <= self.threshold else "ALERT"


operational_metrics = [
    OperationalMetric("Error rate", 0.012, 0.020),
    OperationalMetric("Support escalation rate", 0.031, 0.050),
    OperationalMetric("Insight generation latency", 1.8, 2.5),
]

print("\nOPERATIONAL METRICS")
for metric in operational_metrics:
    print(metric.name, metric.current, "->", metric.status())


# ============================================================================
# 61. INCIDENT PRODUCT THINKING
# ============================================================================

@dataclass
class ProductIncident:
    impact: str
    customer_effect: str
    immediate_action: str
    follow_up: str


incident = ProductIncident(
    impact="Weekly insights unavailable",
    customer_effect="Customers cannot access expected spending guidance.",
    immediate_action="Restore service and communicate clearly.",
    follow_up="Identify root cause and prevent recurrence.",
)

print("\nPRODUCT INCIDENT")
print("Impact:", incident.impact)
print("Customer effect:", incident.customer_effect)
print("Immediate action:", incident.immediate_action)
print("Follow-up:", incident.follow_up)


# ============================================================================
# 62. ROOT CAUSE VS SYMPTOM
# ============================================================================

@dataclass
class RootCauseAnalysis:
    symptom: str
    evidence: List[str]
    suspected_root_cause: str
    validation_test: str


rca = RootCauseAnalysis(
    symptom="Onboarding completion decreased.",
    evidence=[
        "Drop began after a form change.",
        "Largest drop occurs on the new identity step.",
    ],
    suspected_root_cause="Additional identity questions create friction.",
    validation_test="Test a reduced form with the same audience.",
)

print("\nROOT CAUSE ANALYSIS")
print("Symptom:", rca.symptom)
print("Evidence:", rca.evidence)
print("Suspected cause:", rca.suspected_root_cause)
print("Validation:", rca.validation_test)


# ============================================================================
# 63. PRE-MORTEM
# ============================================================================

"""
A pre-mortem asks:

    "Imagine the product initiative failed. What probably caused the failure?"

It can expose risks before execution.
"""


@dataclass
class PreMortem:
    failure_reason: str
    probability: float
    impact: float
    mitigation: str

    def risk(self) -> float:
        return self.probability * self.impact


premortems = [
    PreMortem(
        "Customers do not trust the insights.",
        0.30,
        5,
        "Make data provenance and correction behavior visible.",
    ),
    PreMortem(
        "Engineering complexity delays launch.",
        0.40,
        4,
        "Prototype technical architecture early.",
    ),
    PreMortem(
        "The feature improves engagement but not retention.",
        0.35,
        4,
        "Define retention guardrails and outcome metrics.",
    ),
]

print("\nPRE-MORTEM")
for risk in sorted(premortems, key=lambda x: x.risk(), reverse=True):
    print(risk.failure_reason, "risk=", round(risk.risk(), 2))


# ============================================================================
# 64. POST-MORTEM / LEARNING REVIEW
# ============================================================================

@dataclass
class LearningReview:
    expected: str
    observed: str
    learning: str
    action: str


learning_review = LearningReview(
    expected="Weekly insights would significantly improve retention.",
    observed="Engagement increased but retention barely changed.",
    learning="Engagement with the insight did not address the primary retention constraint.",
    action="Investigate recurring value and retention barriers.",
)

print("\nLEARNING REVIEW")
print("Expected:", learning_review.expected)
print("Observed:", learning_review.observed)
print("Learning:", learning_review.learning)
print("Action:", learning_review.action)


# ============================================================================
# 65. DECISION-MAKING UNDER UNCERTAINTY
# ============================================================================

@dataclass
class UncertainOutcome:
    outcome: str
    probability: float
    value: float

    def expected_value(self) -> float:
        return self.probability * self.value


uncertain_outcomes = [
    UncertainOutcome("High customer adoption", 0.40, 100),
    UncertainOutcome("Moderate adoption", 0.40, 50),
    UncertainOutcome("Low adoption", 0.20, -20),
]

expected_value = sum(
    outcome.expected_value()
    for outcome in uncertain_outcomes
)

print("\nEXPECTED VALUE")
print("Illustrative expected value:", round(expected_value, 2))


# ============================================================================
# 66. REVERSIBLE VS IRREVERSIBLE DECISIONS
# ============================================================================

@dataclass
class DecisionType:
    decision: str
    reversibility: str
    recommended_speed: str


decision_types = [
    DecisionType(
        "Change copy in a small experiment",
        "Highly reversible",
        "Decide quickly with lightweight analysis.",
    ),
    DecisionType(
        "Commit to a multi-year architecture",
        "Hard to reverse",
        "Use deeper analysis and cross-functional review.",
    ),
]

print("\nDECISION REVERSIBILITY")
for item in decision_types:
    print(
        item.decision,
        "|",
        item.reversibility,
        "|",
        item.recommended_speed,
    )


# ============================================================================
# 67. PRECISE PRODUCT QUESTIONS
# ============================================================================

"""
Weak question:
    "Why are users not using the feature?"

Better questions:
    "Which cohort has the largest activation drop?"
    "At which funnel step does abandonment increase?"
    "Did the change begin after a particular release?"
    "Is the problem acquisition-specific?"
    "What behavior predicts successful retention?"
"""


@dataclass
class ProductQuestion:
    weak_question: str
    improved_question: str


questions = [
    ProductQuestion(
        "Why don't users like onboarding?",
        "Which onboarding step has the largest cohort-adjusted abandonment increase?",
    ),
    ProductQuestion(
        "Is the feature successful?",
        "Did the feature improve the predefined primary outcome without violating guardrails?",
    ),
]

print("\nQUESTION QUALITY")
for question in questions:
    print("Weak:", question.weak_question)
    print("Improved:", question.improved_question)


# ============================================================================
# 68. COMMON PRODUCT MANAGEMENT COGNITIVE BIASES
# ============================================================================

"""
Important biases include:

Confirmation bias:
    Searching for evidence that supports an existing belief.

Availability bias:
    Overweighting memorable examples.

Recency bias:
    Giving excessive weight to recent events.

Anchoring:
    Relying too heavily on an initial number or opinion.

Sunk-cost fallacy:
    Continuing because resources have already been spent.

HiPPO effect:
    Overweighting the highest-paid person's opinion.

Survivorship bias:
    Learning only from visible successes.

Good product practice uses evidence, dissent, experimentation, and explicit
decision criteria to reduce these risks.
"""


@dataclass
class BiasCheck:
    bias: str
    warning_question: str


bias_checks = [
    BiasCheck(
        "Confirmation bias",
        "What evidence would prove our current belief wrong?",
    ),
    BiasCheck(
        "Sunk-cost fallacy",
        "If we had not invested already, would we choose this today?",
    ),
    BiasCheck(
        "HiPPO effect",
        "Would we make the same decision if the senior opinion were removed?",
    ),
]

print("\nBIAS CHECKS")
for check in bias_checks:
    print(check.bias, "->", check.warning_question)


# ============================================================================
# 69. PRE-MORTEM WITH ASSUMPTION MAPPING
# ============================================================================

@dataclass
class AssumptionMap:
    assumption: str
    evidence_strength: int
    impact: int

    def priority(self) -> int:
        uncertainty = 6 - self.evidence_strength
        return uncertainty * self.impact


assumption_map = [
    AssumptionMap("Customers have this problem", 3, 5),
    AssumptionMap("Customers will change behavior", 2, 5),
    AssumptionMap("Engineering can build the solution", 4, 4),
    AssumptionMap("Customers will pay", 1, 5),
]

print("\nASSUMPTION MAP")
for item in sorted(
    assumption_map,
    key=lambda x: x.priority(),
    reverse=True,
):
    print(item.assumption, "priority=", item.priority())


# ============================================================================
# 70. CUSTOMER FEEDBACK CLASSIFICATION
# ============================================================================

class FeedbackType(Enum):
    BUG = "Bug"
    FEATURE_REQUEST = "Feature request"
    USABILITY = "Usability issue"
    VALUE_PROBLEM = "Value problem"
    PRAISE = "Praise"
    UNKNOWN = "Unknown"


def classify_feedback(text: str) -> FeedbackType:
    lower = text.lower()

    if "crash" in lower or "error" in lower:
        return FeedbackType.BUG
    if "add" in lower or "please build" in lower:
        return FeedbackType.FEATURE_REQUEST
    if "confusing" in lower or "hard to use" in lower:
        return FeedbackType.USABILITY
    if "not useful" in lower or "doesn't help" in lower:
        return FeedbackType.VALUE_PROBLEM
    if "love" in lower or "great" in lower:
        return FeedbackType.PRAISE

    return FeedbackType.UNKNOWN


feedback = [
    "The application crashes after I open the report.",
    "Please add a weekly spending email.",
    "The category editor is confusing.",
    "The dashboard is not useful for my workflow.",
    "I love the weekly insights.",
]

print("\nFEEDBACK CLASSIFICATION")
for item in feedback:
    print(item, "->", classify_feedback(item).value)


# ============================================================================
# 71. FEEDBACK PRIORITIZATION
# ============================================================================

@dataclass
class FeedbackItem:
    text: str
    affected_users: int
    frequency: int
    severity: int
    strategic_relevance: int

    def score(self) -> float:
        return (
            self.affected_users
            * self.frequency
            * self.severity
            * self.strategic_relevance
        )


feedback_items = [
    FeedbackItem("Categorization is wrong", 4000, 5, 4, 5),
    FeedbackItem("Need more themes", 7000, 2, 1, 1),
    FeedbackItem("Onboarding is confusing", 2500, 4, 4, 5),
]

print("\nFEEDBACK PRIORITIZATION")
for item in sorted(
    feedback_items,
    key=lambda x: x.score(),
    reverse=True,
):
    print(item.text, "score=", item.score())


# ============================================================================
# 72. RELEASE READINESS
# ============================================================================

@dataclass
class ReleaseReadiness:
    product_validated: bool
    critical_bugs_resolved: bool
    analytics_ready: bool
    support_ready: bool
    rollback_ready: bool
    security_reviewed: bool

    def ready(self) -> bool:
        return all(
            [
                self.product_validated,
                self.critical_bugs_resolved,
                self.analytics_ready,
                self.support_ready,
                self.rollback_ready,
                self.security_reviewed,
            ]
        )


release = ReleaseReadiness(
    product_validated=True,
    critical_bugs_resolved=True,
    analytics_ready=True,
    support_ready=True,
    rollback_ready=True,
    security_reviewed=True,
)

print("\nRELEASE READINESS")
print("Ready:", release.ready())


# ============================================================================
# 73. POST-LAUNCH REVIEW
# ============================================================================

@dataclass
class LaunchReview:
    primary_metric_before: float
    primary_metric_after: float
    guardrail_before: float
    guardrail_after: float

    def primary_change(self) -> float:
        return self.primary_metric_after - self.primary_metric_before

    def guardrail_change(self) -> float:
        return self.guardrail_after - self.guardrail_before


launch_review = LaunchReview(0.40, 0.48, 0.02, 0.021)

print("\nPOST-LAUNCH REVIEW")
print("Primary metric change:", launch_review.primary_change())
print("Guardrail change:", launch_review.guardrail_change())


# ============================================================================
# 74. PRODUCT-MANAGEMENT OPERATING LOOP
# ============================================================================

"""
A practical operating loop:

    Observe
       ↓
    Identify problem
       ↓
    Form hypothesis
       ↓
    Assess assumptions
       ↓
    Generate options
       ↓
    Prioritize
       ↓
    Prototype / experiment
       ↓
    Build
       ↓
    Measure
       ↓
    Learn
       ↓
    Adjust

The loop is iterative rather than strictly linear.
"""


@dataclass
class ProductLoop:
    stages: List[str]

    def run_once(self) -> None:
        for number, stage in enumerate(self.stages, start=1):
            print(f"{number}. {stage}")


product_loop = ProductLoop(
    [
        "Observe customer behavior",
        "Define the problem",
        "Form a hypothesis",
        "Identify assumptions",
        "Evaluate options",
        "Prioritize",
        "Experiment",
        "Deliver",
        "Measure outcomes",
        "Learn and adjust",
    ]
)

print("\nPRODUCT MANAGEMENT LOOP")
product_loop.run_once()


# ============================================================================
# 75. INTEGRATED CASE STUDY
# ============================================================================

"""
The following case combines the major concepts.

Scenario:
    A financial product has strong acquisition but weak activation and
    retention.

Observed evidence:
    - many users sign up
    - fewer users complete setup
    - users who reach the first insight are more likely to return
    - customers complain that setup asks too many questions

Mindset:
    Do not immediately build another feature.
    Investigate the activation constraint.
"""


@dataclass
class CaseStudy:
    visitors: int
    signups: int
    activated: int
    retained: int
    primary_complaint: str

    def activation_rate(self) -> float:
        return self.activated / self.signups

    def retention_from_activation(self) -> float:
        return self.retained / self.activated


case = CaseStudy(
    visitors=100000,
    signups=30000,
    activated=12000,
    retained=7200,
    primary_complaint="Setup asks for too much information.",
)

print("\nINTEGRATED CASE STUDY")
print("Activation:", round(case.activation_rate() * 100, 2), "%")
print(
    "Retention from activated users:",
    round(case.retention_from_activation() * 100, 2),
    "%",
)
print("Primary complaint:", case.primary_complaint)


# ============================================================================
# 76. CASE STUDY HYPOTHESIS
# ============================================================================

case_hypothesis = Hypothesis(
    assumption="Long setup reduces activation.",
    intervention="we reduce non-essential onboarding questions",
    expected_behavior="a greater proportion of signups will reach first value",
    metric="activation rate",
    threshold=0.15,
)

print("\nCASE STUDY HYPOTHESIS")
print(case_hypothesis.statement())


# ============================================================================
# 77. CASE STUDY EXPERIMENT
# ============================================================================

case_experiment = Experiment(
    name="Reduced onboarding",
    hypothesis="Reducing non-essential questions increases activation.",
    primary_metric="activation rate",
    baseline=0.40,
    treatment=0.47,
    minimum_success=0.10,
)

print("\nCASE STUDY EXPERIMENT")
print("Change:", round(case_experiment.relative_change * 100, 2), "%")
print("Decision threshold passed:", case_experiment.passed)


# ============================================================================
# 78. CASE STUDY GUARDRAILS
# ============================================================================

case_guardrails = ExperimentResult(
    primary_metric_change=case_experiment.relative_change,
    conversion_change=0.06,
    complaint_change=-0.02,
    error_change=0.001,
)

print("\nCASE STUDY GUARDRAILS")
print(case_guardrails.decision())


# ============================================================================
# 79. PRODUCT THINKING INTERVIEW QUESTIONS
# ============================================================================

"""
Typical product-thinking questions require structured reasoning rather than
memorized definitions.

Useful structure:

1. Clarify the objective.
2. Identify target customer.
3. Define the problem.
4. Segment the users.
5. Identify pain points.
6. Generate alternatives.
7. Prioritize.
8. Define success metrics.
9. Discuss trade-offs and risks.
10. Explain how you would validate the decision.
"""


def product_interview_framework(problem: str) -> List[str]:
    return [
        f"Clarify the objective for: {problem}",
        "Identify the target customer.",
        "Define the customer problem without prematurely choosing a solution.",
        "Segment users by meaningful differences.",
        "Identify the most important pain point.",
        "Generate multiple solution approaches.",
        "Prioritize using explicit criteria.",
        "Define primary and guardrail metrics.",
        "Identify technical, business, ethical, and operational risks.",
        "Design the smallest credible validation experiment.",
    ]


print("\nPRODUCT INTERVIEW FRAMEWORK")
for step in product_interview_framework("Improve product activation"):
    print("-", step)


# ============================================================================
# 80. PRODUCT MINDSET SELF-ASSESSMENT
# ============================================================================

@dataclass
class MindsetDimension:
    name: str
    score: int
    evidence: str


mindset_assessment = [
    MindsetDimension(
        "Customer obsession",
        4,
        "Uses customer problems and behavior as primary evidence.",
    ),
    MindsetDimension(
        "Ownership",
        4,
        "Focuses on outcomes and follows issues through launch.",
    ),
    MindsetDimension(
        "Curiosity",
        5,
        "Tests assumptions instead of accepting explanations immediately.",
    ),
    MindsetDimension(
        "Experimentation",
        4,
        "Uses hypotheses and measurable validation.",
    ),
    MindsetDimension(
        "Analytical thinking",
        4,
        "Uses segmentation, funnels, metrics, and causal reasoning.",
    ),
    MindsetDimension(
        "Business thinking",
        3,
        "Considers pricing, costs, revenue, and strategic value.",
    ),
    MindsetDimension(
        "Technical awareness",
        3,
        "Considers architecture, reliability, privacy, security, and constraints.",
    ),
]

print("\nMINDSET SELF-ASSESSMENT")
for dimension in mindset_assessment:
    print(
        dimension.name,
        "| score=",
        dimension.score,
        "|",
        dimension.evidence,
    )


# ============================================================================
# 81. FINAL INTEGRATED DECISION ENGINE
# ============================================================================

@dataclass
class ProductDecision:
    customer_value: float
    business_value: float
    evidence: float
    feasibility: float
    strategic_fit: float
    risk: float

    def score(self) -> float:
        """
        A deliberately transparent illustrative decision model.

        It should never be treated as a universal product-management formula.
        Product decisions often require qualitative judgment and constraints
        that cannot be represented by a single score.
        """
        return (
            self.customer_value * 0.25
            + self.business_value * 0.20
            + self.evidence * 0.20
            + self.feasibility * 0.15
            + self.strategic_fit * 0.20
            - self.risk * 0.15
        )


final_decision = ProductDecision(
    customer_value=9,
    business_value=8,
    evidence=7,
    feasibility=7,
    strategic_fit=9,
    risk=3,
)

print("\nINTEGRATED PRODUCT DECISION")
print("Illustrative score:", round(final_decision.score(), 2))


# ============================================================================
# 82. KEY MINDSET RULES AS EXECUTABLE CHECKS
# ============================================================================

@dataclass
class MindsetChecklist:
    customer_problem_defined: bool
    evidence_collected: bool
    assumptions_identified: bool
    success_metric_defined: bool
    tradeoffs_explicit: bool
    technical_risks_considered: bool
    business_impact_considered: bool
    ethical_risks_considered: bool
    post_launch_measurement_planned: bool

    def missing_items(self) -> List[str]:
        checks = {
            "customer_problem_defined": self.customer_problem_defined,
            "evidence_collected": self.evidence_collected,
            "assumptions_identified": self.assumptions_identified,
            "success_metric_defined": self.success_metric_defined,
            "tradeoffs_explicit": self.tradeoffs_explicit,
            "technical_risks_considered": self.technical_risks_considered,
            "business_impact_considered": self.business_impact_considered,
            "ethical_risks_considered": self.ethical_risks_considered,
            "post_launch_measurement_planned": self.post_launch_measurement_planned,
        }

        return [name for name, passed in checks.items() if not passed]


checklist = MindsetChecklist(
    customer_problem_defined=True,
    evidence_collected=True,
    assumptions_identified=True,
    success_metric_defined=True,
    tradeoffs_explicit=True,
    technical_risks_considered=True,
    business_impact_considered=True,
    ethical_risks_considered=True,
    post_launch_measurement_planned=True,
)

print("\nPRODUCT MINDSET CHECKLIST")
missing = checklist.missing_items()
print("Ready:", not missing)
print("Missing:", missing)


# ============================================================================
# 83. COMMON MISTAKES
# ============================================================================

"""
Common mistakes demonstrated conceptually by the models above:

1. Starting with a solution instead of a problem.
2. Treating every customer request as a requirement.
3. Confusing feature delivery with customer outcomes.
4. Using vanity metrics.
5. Ignoring retention while optimizing acquisition.
6. Treating correlation as causation.
7. Prioritizing based only on seniority.
8. Ignoring opportunity cost.
9. Building before validating important assumptions.
10. Treating MVP as "the smallest feature set" rather than a learning vehicle.
11. Ignoring technical constraints.
12. Treating security and privacy as post-launch concerns.
13. Ignoring accessibility.
14. Ignoring ethical consequences.
15. Using prioritization formulas as if they were objective truth.
16. Failing to define guardrail metrics.
17. Measuring averages without examining distributions and segments.
18. Continuing an initiative because of sunk costs.
19. Confusing strategy with a list of features.
20. Treating a roadmap as an unchangeable contract.
"""


# ============================================================================
# 84. EDGE CASES IN PRODUCT DECISION-MAKING
# ============================================================================

"""
Important edge cases:

- A feature may have low direct customer value but be required for regulation.
- A technically expensive initiative may be strategically essential.
- A low-revenue customer segment may unlock a valuable network effect.
- A metric may improve while actual customer welfare decreases.
- A statistically significant experiment may have a trivial practical effect.
- A successful experiment may not scale because operating costs increase.
- A customer request may reveal a serious underlying problem even when the
  requested solution is wrong.
- A high-confidence estimate can still be based on biased evidence.
- A roadmap item may be urgent because of an external deadline rather than
  because it has the highest RICE score.
- A product may need to do less rather than add more features.
"""


# ============================================================================
# 85. TESTING THE EDUCATIONAL IMPLEMENTATIONS
# ============================================================================

def run_basic_tests() -> None:
    """Small assertions demonstrate expected behavior and edge handling."""

    assert retention_rate(100, 50) == 0.5
    assert evaluate_idea_quality(idea)["clear_problem"] is True

    assert RICEItem(
        "Test", reach=100, impact=2, confidence=0.5, effort=5
    ).score() == 20

    assert classify_feedback("The app crashes") == FeedbackType.BUG

    try:
        retention_rate(0, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for zero starting users.")

    try:
        RICEItem(
            "Invalid",
            reach=100,
            impact=1,
            confidence=1,
            effort=0,
        ).score()
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for zero effort.")


print("\nRUNNING BASIC TESTS")
run_basic_tests()
print("All basic tests passed.")


# ============================================================================
# 86. PERFORMANCE CONSIDERATIONS
# ============================================================================

"""
Most examples in this file operate on small educational datasets.

For larger product analytics systems:

    - avoid repeatedly scanning the same large dataset
    - use database aggregation where appropriate
    - index frequently queried fields
    - precompute expensive metrics when latency matters
    - distinguish batch analytics from real-time analytics
    - use sampling when exact computation is unnecessary
    - monitor query cost
    - validate metric definitions centrally
    - avoid duplicate event processing

The Python examples are intentionally simple so that the product reasoning
remains visible.
"""


# ============================================================================
# 87. PRODUCTION PRODUCT-MANAGEMENT CONSIDERATIONS
# ============================================================================

"""
Production product management requires a stronger operating discipline:

Customer:
    - continuous feedback
    - behavioral evidence
    - segmentation
    - customer support signals

Product:
    - clear outcomes
    - coherent strategy
    - roadmap communication
    - discovery and delivery

Technology:
    - reliability
    - scalability
    - security
    - privacy
    - observability
    - technical debt

Business:
    - revenue
    - costs
    - pricing
    - unit economics
    - strategic positioning

Operations:
    - release readiness
    - incident management
    - support
    - governance

Decision quality:
    - explicit assumptions
    - evidence
    - uncertainty
    - trade-offs
    - reversible decisions
    - learning loops
"""


# ============================================================================
# 88. COMPREHENSIVE PRODUCT REVIEW
# ============================================================================

@dataclass
class ProductReview:
    problem_clarity: int
    customer_evidence: int
    solution_quality: int
    business_viability: int
    technical_feasibility: int
    usability: int
    strategic_fit: int
    risk_management: int
    measurement: int

    def average_score(self) -> float:
        values = [
            self.problem_clarity,
            self.customer_evidence,
            self.solution_quality,
            self.business_viability,
            self.technical_feasibility,
            self.usability,
            self.strategic_fit,
            self.risk_management,
            self.measurement,
        ]

        return statistics.mean(values)


review = ProductReview(
    problem_clarity=9,
    customer_evidence=8,
    solution_quality=7,
    business_viability=8,
    technical_feasibility=7,
    usability=8,
    strategic_fit=9,
    risk_management=7,
    measurement=9,
)

print("\nCOMPREHENSIVE PRODUCT REVIEW")
print("Average:", round(review.average_score(), 2))


# ============================================================================
# 89. PRODUCT MANAGER MINDSET PRINCIPLES
# ============================================================================

principles = [
    "Start with customer problems rather than preferred solutions.",
    "Seek evidence before increasing confidence.",
    "Treat assumptions as things to test.",
    "Own outcomes rather than only activities.",
    "Use metrics to improve decisions, not to replace judgment.",
    "Prioritize explicitly because resources are limited.",
    "Understand business economics.",
    "Understand technical constraints without pretending to be the engineer.",
    "Design for security, privacy, accessibility, and reliability.",
    "Make trade-offs visible.",
    "Prefer learning before large irreversible commitments.",
    "Use experiments carefully and ethically.",
    "Distinguish correlation from causation.",
    "Inspect segments and distributions rather than relying on averages.",
    "Treat roadmaps as directional tools rather than promises of certainty.",
    "Learn after launch and change course when evidence requires it.",
]

print("\nPRODUCT MANAGEMENT MINDSET PRINCIPLES")
for number, principle in enumerate(principles, start=1):
    print(f"{number}. {principle}")


# ============================================================================
# 90. EXECUTABLE STUDY EXERCISE
# ============================================================================

"""
The following exercise provides a reusable structure for practicing product
thinking with a new problem.
"""


def analyze_product_problem(
    customer: str,
    problem: str,
    baseline_metric: float,
    target_metric: float,
    effort: float,
) -> Dict[str, object]:
    if not customer.strip():
        raise ValueError("Customer cannot be empty.")
    if not problem.strip():
        raise ValueError("Problem cannot be empty.")
    if effort <= 0:
        raise ValueError("Effort must be positive.")

    gap = target_metric - baseline_metric

    return {
        "customer": customer,
        "problem": problem,
        "baseline": baseline_metric,
        "target": target_metric,
        "gap": gap,
        "effort": effort,
        "requires_validation": True,
        "mindset": [
            "Understand customer context.",
            "Collect evidence.",
            "Identify assumptions.",
            "Define measurable outcome.",
            "Compare alternatives.",
            "Assess technical and business constraints.",
            "Experiment before large commitment when uncertainty is material.",
        ],
    }


exercise = analyze_product_problem(
    customer="Employees using an internal knowledge platform",
    problem="They cannot quickly find reliable answers.",
    baseline_metric=0.45,
    target_metric=0.65,
    effort=8,
)

print("\nEXECUTABLE STUDY EXERCISE")
for key, value in exercise.items():
    print(f"{key}: {value}")


# ============================================================================
# END OF STUDY FILE
# ============================================================================

"""
The central operating principle represented throughout this file is:

    Customer problem
        +
    Evidence
        +
    Product judgment
        +
    Business understanding
        +
    Technical awareness
        +
    Experimentation
        +
    Outcome measurement
        =
    Better product decisions

A product management mindset is therefore not a single framework or formula.
It is a disciplined way of thinking about customers, problems, evidence,
trade-offs, execution, technology, business value, risk, and outcomes.
"""
