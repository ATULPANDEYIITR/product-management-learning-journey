"""
Product Thinking Exercises
===========================

A comprehensive, self-contained study script for practicing product thinking
through product teardowns, product critique, product problem identification,
and opportunity identification.

The script progresses from beginner concepts to structured product analysis,
including:

1. Product thinking fundamentals
2. Product teardown
3. Product critique
4. User problem identification
5. Jobs-to-be-done
6. User segmentation
7. Problem framing
8. Opportunity identification
9. Opportunity trees
10. Hypothesis formation
11. Product metrics
12. Prioritization
13. Root-cause analysis
14. Customer journey analysis
15. Competitive comparison
16. Product diagnosis
17. Experiment design
18. Edge cases and failure modes
19. Advanced teardown exercises
20. A complete end-to-end product case study

The examples use familiar product categories but do not depend on external
packages or external data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# =============================================================================
# SECTION 1: BASIC PRODUCT THINKING CONCEPTS
# =============================================================================

print("=" * 80)
print("PRODUCT THINKING EXERCISES")
print("=" * 80)


def explain_product_thinking() -> None:
    """
    Demonstrates the basic distinction between a product feature and a
    customer problem.

    Product thinking starts with the user's desired outcome rather than
    starting with a feature that someone wants to build.
    """

    print("\n--- Product thinking fundamentals ---")

    feature = "Add one-click reorder"
    underlying_problem = "Customers repeatedly purchase the same items."
    desired_outcome = "Customers should be able to reorder familiar items quickly."

    print("Feature:", feature)
    print("Underlying problem:", underlying_problem)
    print("Desired outcome:", desired_outcome)

    print(
        "\nProduct thinking asks whether the proposed feature is the best "
        "way to achieve the desired customer outcome."
    )


explain_product_thinking()


# =============================================================================
# SECTION 2: PRODUCT THINKING VOCABULARY
# =============================================================================

class ProductTerm(Enum):
    USER = "Person who interacts with or receives value from the product"
    CUSTOMER = "Person or organization that pays for the product"
    NEED = "A condition or requirement the user is trying to satisfy"
    PROBLEM = "An obstacle preventing the desired outcome"
    JOB = "The progress the user is trying to make"
    OPPORTUNITY = "A meaningful area where a product can improve an outcome"
    SOLUTION = "A proposed way of addressing a problem or opportunity"
    FEATURE = "A product capability exposed to users"
    OUTCOME = "The measurable result created by a product"
    METRIC = "A quantitative measure used to understand product behavior"
    HYPOTHESIS = "A testable belief about users, problems, or solutions"


print("\n--- Product terminology ---")
for term in ProductTerm:
    print(f"{term.name}: {term.value}")


# =============================================================================
# SECTION 3: PRODUCT TEARDOWN
# =============================================================================

@dataclass
class Product:
    """
    Represents a product being analyzed.

    A teardown should not be limited to listing features. It should examine
    users, problems, value proposition, journey, business model, metrics,
    trade-offs, and failure points.
    """

    name: str
    category: str
    target_users: List[str]
    primary_problem: str
    value_proposition: str
    core_features: List[str]
    monetization: str
    primary_metric: str


@dataclass
class TeardownResult:
    product_name: str
    target_user_analysis: str
    problem_analysis: str
    value_analysis: str
    feature_analysis: str
    monetization_analysis: str
    metric_analysis: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    risks: List[str]


def perform_teardown(product: Product) -> TeardownResult:
    """
    Performs a structured product teardown.

    A teardown asks:
    - Who is the product for?
    - What problem does it solve?
    - Why does the solution create value?
    - Which features support the value proposition?
    - How does the product make money?
    - Which metric represents successful product behavior?
    - What appears strong or weak?
    - Where might meaningful opportunities exist?
    """

    feature_count = len(product.core_features)

    feature_analysis = (
        f"The product has {feature_count} core features. "
        "Features should be evaluated by the user problem they address, "
        "not merely by their quantity."
    )

    strengths = [
        "Clear target-user definition",
        "Explicit customer problem",
        "Value proposition connected to a user outcome",
    ]

    weaknesses = [
        "The stated problem may contain multiple sub-problems",
        "The primary metric may not capture long-term customer value",
        "Feature usefulness must be validated through user behavior",
    ]

    opportunities = [
        "Reduce friction in the highest-value customer journey",
        "Improve the weakest stage of the user funnel",
        "Test whether underserved segments have different needs",
    ]

    risks = [
        "Optimizing a local metric while damaging overall customer value",
        "Building features before validating the underlying problem",
        "Confusing user requests with root problems",
    ]

    return TeardownResult(
        product_name=product.name,
        target_user_analysis=f"Primary users: {', '.join(product.target_users)}",
        problem_analysis=product.primary_problem,
        value_analysis=product.value_proposition,
        feature_analysis=feature_analysis,
        monetization_analysis=product.monetization,
        metric_analysis=product.primary_metric,
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        risks=risks,
    )


sample_product = Product(
    name="QuickCart",
    category="Online grocery delivery",
    target_users=[
        "Busy professionals",
        "Parents managing household shopping",
        "Customers who frequently reorder essentials",
    ],
    primary_problem="Customers need groceries without spending significant time shopping.",
    value_proposition="Order household essentials quickly and receive them at a convenient time.",
    core_features=[
        "Search",
        "Category browsing",
        "Shopping cart",
        "Saved addresses",
        "Scheduled delivery",
        "Order history",
        "Reorder",
        "Digital payment",
    ],
    monetization="Product margin, delivery fees, subscriptions, and promotions",
    primary_metric="Successful repeat orders",
)

teardown = perform_teardown(sample_product)

print("\n--- Product teardown example ---")
print("Product:", teardown.product_name)
print("Users:", teardown.target_user_analysis)
print("Problem:", teardown.problem_analysis)
print("Value proposition:", teardown.value_analysis)
print("Feature analysis:", teardown.feature_analysis)
print("Monetization:", teardown.monetization_analysis)
print("Primary metric:", teardown.metric_analysis)

print("\nStrengths:")
for item in teardown.strengths:
    print(" -", item)

print("\nWeaknesses:")
for item in teardown.weaknesses:
    print(" -", item)

print("\nPotential opportunities:")
for item in teardown.opportunities:
    print(" -", item)

print("\nRisks:")
for item in teardown.risks:
    print(" -", item)


# =============================================================================
# SECTION 4: PRODUCT CRITIQUE
# =============================================================================

@dataclass
class ProductCritique:
    """
    A structured critique separates observation from interpretation.

    Good critique is specific enough to explain:
    1. What happens?
    2. Why might it be a problem?
    3. Who experiences it?
    4. What evidence would confirm it?
    5. What outcome could improve?
    """

    observation: str
    affected_user: str
    suspected_problem: str
    severity: int
    frequency: int
    confidence: int
    evidence_needed: str

    def priority_score(self) -> float:
        """
        Calculates a simple critique priority score.

        Severity, frequency, and confidence are scored from 1 to 5.
        """
        return self.severity * self.frequency * self.confidence


critique = ProductCritique(
    observation="The checkout requires several screens before payment.",
    affected_user="Customers making routine purchases",
    suspected_problem="Checkout friction may increase abandonment.",
    severity=4,
    frequency=5,
    confidence=3,
    evidence_needed="Checkout funnel data, session recordings, and user interviews.",
)

print("\n--- Product critique ---")
print("Observation:", critique.observation)
print("Affected user:", critique.affected_user)
print("Suspected problem:", critique.suspected_problem)
print("Priority score:", critique.priority_score())
print("Evidence needed:", critique.evidence_needed)


# =============================================================================
# SECTION 5: OBSERVATION VS PROBLEM VS SOLUTION
# =============================================================================

@dataclass
class ProductStatement:
    observation: str
    problem: str
    solution: str


def classify_product_statement(statement: ProductStatement) -> None:
    """
    Demonstrates three different levels of product reasoning.

    Observation:
        What is happening?

    Problem:
        Why might the observed behavior matter?

    Solution:
        What could be built or changed?

    Strong product analysis keeps these levels separate.
    """

    print("\n--- Observation, problem, and solution ---")
    print("Observation:", statement.observation)
    print("Problem:", statement.problem)
    print("Solution:", statement.solution)


classification_example = ProductStatement(
    observation="Many users abandon the onboarding process.",
    problem="Users may not understand the product's value early enough.",
    solution="Test a shorter onboarding flow with earlier value demonstration.",
)

classify_product_statement(classification_example)


# =============================================================================
# SECTION 6: USER SEGMENTATION
# =============================================================================

@dataclass
class UserSegment:
    name: str
    context: str
    goal: str
    pain_points: List[str]
    frequency: str
    willingness_to_pay: int


segments = [
    UserSegment(
        name="Occasional buyer",
        context="Orders groceries once or twice per month",
        goal="Complete a purchase conveniently",
        pain_points=["Forgets products", "Does not know delivery options"],
        frequency="Low",
        willingness_to_pay=2,
    ),
    UserSegment(
        name="Frequent household shopper",
        context="Orders several times per month",
        goal="Restock recurring household items quickly",
        pain_points=["Repeating the same search", "Time-consuming checkout"],
        frequency="High",
        willingness_to_pay=4,
    ),
    UserSegment(
        name="Time-sensitive professional",
        context="Needs groceries around a demanding work schedule",
        goal="Receive essential products within a predictable time window",
        pain_points=["Uncertain delivery times", "Limited planning time"],
        frequency="Medium",
        willingness_to_pay=5,
    ),
]


def analyze_segments(user_segments: Sequence[UserSegment]) -> None:
    print("\n--- User segmentation ---")

    for segment in user_segments:
        print(f"\nSegment: {segment.name}")
        print("Context:", segment.context)
        print("Goal:", segment.goal)
        print("Pain points:", ", ".join(segment.pain_points))
        print("Frequency:", segment.frequency)
        print("Willingness to pay:", segment.willingness_to_pay, "/ 5")


analyze_segments(segments)


# =============================================================================
# SECTION 7: JOBS-TO-BE-DONE
# =============================================================================

@dataclass
class JobStatement:
    situation: str
    motivation: str
    desired_outcome: str

    def sentence(self) -> str:
        return (
            f"When {self.situation}, I want to {self.motivation}, "
            f"so that {self.desired_outcome}."
        )


job = JobStatement(
    situation="I realize that common household items are running low",
    motivation="reorder them with minimal effort",
    desired_outcome="I can restore my household supplies without rebuilding my shopping list",
)

print("\n--- Jobs-to-be-done ---")
print(job.sentence())


# =============================================================================
# SECTION 8: PROBLEM FRAMING
# =============================================================================

@dataclass
class ProblemStatement:
    user: str
    context: str
    obstacle: str
    impact: str

    def formulate(self) -> str:
        return (
            f"{self.user} needs to achieve a goal in {self.context}, "
            f"but {self.obstacle}, which causes {self.impact}."
        )


problem_statement = ProblemStatement(
    user="Frequent grocery shoppers",
    context="during recurring household restocking",
    obstacle="must repeatedly search for the same products",
    impact="unnecessary effort and longer shopping sessions",
)

print("\n--- Problem statement ---")
print(problem_statement.formulate())


# =============================================================================
# SECTION 9: ROOT-CAUSE ANALYSIS
# =============================================================================

@dataclass
class WhyNode:
    question: str
    answer: str


def five_whys(initial_problem: str, why_chain: Sequence[str]) -> List[WhyNode]:
    """
    Creates a Five Whys analysis.

    Five Whys is not a mathematical rule requiring exactly five questions.
    The important principle is repeatedly testing whether an explanation
    represents a deeper cause.
    """

    nodes = []
    current_question = initial_problem

    for answer in why_chain:
        nodes.append(WhyNode(current_question, answer))
        current_question = f"Why is this happening? Because {answer}"

    return nodes


why_analysis = five_whys(
    "Customers abandon checkout.",
    [
        "Checkout requires several actions.",
        "The customer must repeatedly confirm information.",
        "The system does not reliably retain customer preferences.",
        "Different checkout requirements are handled independently.",
        "The checkout architecture evolved around individual features rather than one coherent purchase flow.",
    ],
)

print("\n--- Five Whys ---")
for index, node in enumerate(why_analysis, start=1):
    print(f"Why {index}:")
    print(" Question:", node.question)
    print(" Answer:", node.answer)


# =============================================================================
# SECTION 10: CUSTOMER JOURNEY
# =============================================================================

@dataclass
class JourneyStage:
    name: str
    user_goal: str
    friction: int
    satisfaction: int
    business_risk: int

    def opportunity_score(self) -> int:
        """
        High friction and business risk combined with low satisfaction
        produce a larger opportunity score.
        """
        return self.friction * self.business_risk * (6 - self.satisfaction)


customer_journey = [
    JourneyStage(
        "Awareness",
        "Understand whether the service is useful",
        friction=2,
        satisfaction=4,
        business_risk=2,
    ),
    JourneyStage(
        "Discovery",
        "Find relevant products",
        friction=3,
        satisfaction=3,
        business_risk=3,
    ),
    JourneyStage(
        "Cart",
        "Confirm the desired items",
        friction=2,
        satisfaction=4,
        business_risk=2,
    ),
    JourneyStage(
        "Checkout",
        "Pay and select delivery",
        friction=5,
        satisfaction=2,
        business_risk=5,
    ),
    JourneyStage(
        "Delivery",
        "Receive the order as expected",
        friction=3,
        satisfaction=3,
        business_risk=5,
    ),
    JourneyStage(
        "Repeat purchase",
        "Quickly reorder recurring products",
        friction=4,
        satisfaction=2,
        business_risk=4,
    ),
]

print("\n--- Customer journey analysis ---")
for stage in customer_journey:
    print(
        f"{stage.name}: "
        f"friction={stage.friction}, "
        f"satisfaction={stage.satisfaction}, "
        f"business_risk={stage.business_risk}, "
        f"opportunity_score={stage.opportunity_score()}"
    )


# =============================================================================
# SECTION 11: OPPORTUNITY IDENTIFICATION
# =============================================================================

@dataclass
class Opportunity:
    name: str
    customer_problem: str
    affected_users: int
    frequency: float
    importance: float
    strategic_fit: float
    evidence_strength: float

    def score(self) -> float:
        """
        Weighted opportunity score.

        This is intentionally a heuristic rather than an objective truth.
        Product prioritization should not be reduced to a single number.
        """
        return (
            self.affected_users
            * self.frequency
            * self.importance
            * self.strategic_fit
            * self.evidence_strength
        )


opportunities = [
    Opportunity(
        name="Faster repeat ordering",
        customer_problem="Frequent shoppers repeatedly rebuild common baskets",
        affected_users=8,
        frequency=5,
        importance=4,
        strategic_fit=5,
        evidence_strength=3,
    ),
    Opportunity(
        name="Simpler checkout",
        customer_problem="Customers encounter unnecessary checkout steps",
        affected_users=9,
        frequency=5,
        importance=5,
        strategic_fit=5,
        evidence_strength=4,
    ),
    Opportunity(
        name="Improved product discovery",
        customer_problem="Customers struggle to find relevant products",
        affected_users=7,
        frequency=4,
        importance=4,
        strategic_fit=4,
        evidence_strength=3,
    ),
]

print("\n--- Opportunity identification ---")
for opportunity in sorted(opportunities, key=lambda item: item.score(), reverse=True):
    print(f"{opportunity.name}: {opportunity.score():,.0f}")


# =============================================================================
# SECTION 12: OPPORTUNITY TREE
# =============================================================================

@dataclass
class OpportunityNode:
    name: str
    children: List["OpportunityNode"] = field(default_factory=list)

    def display(self, level: int = 0) -> None:
        print("  " * level + "- " + self.name)
        for child in self.children:
            child.display(level + 1)


opportunity_tree = OpportunityNode(
    "Increase successful repeat purchases",
    children=[
        OpportunityNode(
            "Increase purchase frequency",
            children=[
                OpportunityNode("Make recurring purchases easier"),
                OpportunityNode("Improve product discovery"),
                OpportunityNode("Increase confidence in availability"),
            ],
        ),
        OpportunityNode(
            "Reduce checkout abandonment",
            children=[
                OpportunityNode("Reduce unnecessary steps"),
                OpportunityNode("Improve payment reliability"),
                OpportunityNode("Increase delivery-time clarity"),
            ],
        ),
        OpportunityNode(
            "Improve post-purchase experience",
            children=[
                OpportunityNode("Improve order tracking"),
                OpportunityNode("Resolve failed deliveries"),
                OpportunityNode("Simplify repeat ordering"),
            ],
        ),
    ],
)

print("\n--- Opportunity tree ---")
opportunity_tree.display()


# =============================================================================
# SECTION 13: PRODUCT HYPOTHESES
# =============================================================================

@dataclass
class Hypothesis:
    user: str
    problem: str
    intervention: str
    expected_behavior: str
    metric: str
    success_threshold: float

    def statement(self) -> str:
        return (
            f"We believe {self.user} experiences {self.problem}. "
            f"If we {self.intervention}, we expect {self.expected_behavior}. "
            f"We will measure {self.metric} and consider the test successful "
            f"if it reaches {self.success_threshold}."
        )


hypothesis = Hypothesis(
    user="frequent shoppers",
    problem="repeatedly searching for familiar products",
    intervention="provide a personalized reorder basket",
    expected_behavior="complete recurring purchases with fewer interactions",
    metric="repeat-order completion rate",
    success_threshold=0.70,
)

print("\n--- Product hypothesis ---")
print(hypothesis.statement())


# =============================================================================
# SECTION 14: PRODUCT METRICS
# =============================================================================

@dataclass
class Funnel:
    visitors: int
    product_views: int
    cart_additions: int
    checkouts: int
    purchases: int

    def conversion_rates(self) -> Dict[str, float]:
        def safe_rate(numerator: int, denominator: int) -> float:
            return numerator / denominator if denominator else 0.0

        return {
            "visitor_to_product_view": safe_rate(
                self.product_views, self.visitors
            ),
            "product_view_to_cart": safe_rate(
                self.cart_additions, self.product_views
            ),
            "cart_to_checkout": safe_rate(
                self.checkouts, self.cart_additions
            ),
            "checkout_to_purchase": safe_rate(
                self.purchases, self.checkouts
            ),
            "visitor_to_purchase": safe_rate(
                self.purchases, self.visitors
            ),
        }


funnel = Funnel(
    visitors=10000,
    product_views=7600,
    cart_additions=2800,
    checkouts=1900,
    purchases=1425,
)

print("\n--- Funnel metrics ---")
for stage, rate in funnel.conversion_rates().items():
    print(f"{stage}: {rate:.1%}")


# =============================================================================
# SECTION 15: NORTH-STAR METRIC AND GUARDRAIL METRICS
# =============================================================================

@dataclass
class MetricDefinition:
    name: str
    type: str
    definition: str
    potential_risk: str


metrics = [
    MetricDefinition(
        name="Successful repeat orders",
        type="Outcome metric",
        definition="Completed repeat purchases by customers who previously purchased",
        potential_risk="May hide customer dissatisfaction if orders are driven by discounts.",
    ),
    MetricDefinition(
        name="Checkout completion rate",
        type="Funnel metric",
        definition="Completed purchases divided by initiated checkout sessions",
        potential_risk="Optimization could increase completion while reducing basket quality.",
    ),
    MetricDefinition(
        name="Customer retention",
        type="Guardrail/business metric",
        definition="Share of customers returning during a defined period",
        potential_risk="Requires a carefully chosen retention window.",
    ),
    MetricDefinition(
        name="Refund rate",
        type="Guardrail metric",
        definition="Orders requiring refunds divided by total orders",
        potential_risk="A low refund rate does not prove customer satisfaction.",
    ),
]

print("\n--- Product metrics ---")
for metric in metrics:
    print(f"\n{metric.name}")
    print("Type:", metric.type)
    print("Definition:", metric.definition)
    print("Risk:", metric.potential_risk)


# =============================================================================
# SECTION 16: PRIORITIZATION
# =============================================================================

@dataclass
class PrioritizationItem:
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float

    def rice_score(self) -> float:
        """
        Simplified RICE score.

        RICE is commonly expressed as:
            Reach × Impact × Confidence / Effort

        Reach and effort should be measured consistently within a portfolio.
        """

        if self.effort <= 0:
            raise ValueError("Effort must be greater than zero.")

        return (
            self.reach
            * self.impact
            * self.confidence
            / self.effort
        )


prioritization_items = [
    PrioritizationItem(
        name="One-tap reorder",
        reach=7000,
        impact=3.0,
        confidence=0.75,
        effort=4.0,
    ),
    PrioritizationItem(
        name="Checkout simplification",
        reach=8500,
        impact=4.0,
        confidence=0.85,
        effort=6.0,
    ),
    PrioritizationItem(
        name="New recommendation engine",
        reach=6000,
        impact=3.5,
        confidence=0.45,
        effort=10.0,
    ),
]

print("\n--- RICE prioritization ---")
for item in sorted(
    prioritization_items,
    key=lambda value: value.rice_score(),
    reverse=True,
):
    print(f"{item.name}: {item.rice_score():,.2f}")


# =============================================================================
# SECTION 17: VALUE VS EFFORT
# =============================================================================

@dataclass
class ValueEffortItem:
    name: str
    value: int
    effort: int

    def quadrant(self) -> str:
        """
        Classifies ideas using simple 1-5 thresholds.

        This is a directional tool. A real product decision should also
        consider strategic fit, evidence, dependencies, risk, and timing.
        """
        if self.value >= 4 and self.effort <= 2:
            return "Quick win"
        if self.value >= 4 and self.effort >= 4:
            return "Strategic investment"
        if self.value <= 2 and self.effort <= 2:
            return "Low priority"
        return "Questionable or needs more evidence"


value_effort_items = [
    ValueEffortItem("Saved shopping lists", 5, 2),
    ValueEffortItem("Checkout redesign", 5, 4),
    ValueEffortItem("Cosmetic icon refresh", 2, 1),
    ValueEffortItem("Complex loyalty marketplace", 3, 5),
]

print("\n--- Value vs effort ---")
for item in value_effort_items:
    print(
        f"{item.name}: value={item.value}, effort={item.effort}, "
        f"classification={item.quadrant()}"
    )


# =============================================================================
# SECTION 18: KANO-STYLE FEATURE CLASSIFICATION
# =============================================================================

class FeatureCategory(Enum):
    BASIC = "Expected feature; absence causes dissatisfaction"
    PERFORMANCE = "More improvement generally produces more satisfaction"
    DELIGHT = "Unexpected feature that can create disproportionate satisfaction"
    INDIFFERENT = "Little meaningful effect on customer satisfaction"
    REVERSE = "Some customers prefer not to have the feature"


feature_classifications = {
    "Reliable payment": FeatureCategory.BASIC,
    "Faster delivery": FeatureCategory.PERFORMANCE,
    "Unexpected personalized recommendation": FeatureCategory.DELIGHT,
    "Decorative animation": FeatureCategory.INDIFFERENT,
}


print("\n--- Feature classification ---")
for feature, category in feature_classifications.items():
    print(f"{feature}: {category.value}")


# =============================================================================
# SECTION 19: COMPETITIVE PRODUCT COMPARISON
# =============================================================================

@dataclass
class Competitor:
    name: str
    acquisition: int
    discovery: int
    checkout: int
    delivery: int
    retention: int

    def total_score(self) -> int:
        return (
            self.acquisition
            + self.discovery
            + self.checkout
            + self.delivery
            + self.retention
        )


competitors = [
    Competitor("Product A", 4, 4, 3, 5, 4),
    Competitor("Product B", 5, 3, 5, 3, 4),
    Competitor("Product C", 3, 5, 4, 4, 3),
]

print("\n--- Competitive comparison ---")
for competitor in sorted(
    competitors,
    key=lambda item: item.total_score(),
    reverse=True,
):
    print(
        f"{competitor.name}: total={competitor.total_score()}, "
        f"acquisition={competitor.acquisition}, "
        f"discovery={competitor.discovery}, "
        f"checkout={competitor.checkout}, "
        f"delivery={competitor.delivery}, "
        f"retention={competitor.retention}"
    )


# =============================================================================
# SECTION 20: PRODUCT CRITIQUE SCORECARD
# =============================================================================

@dataclass
class CritiqueDimension:
    name: str
    score: int
    reasoning: str


def calculate_critique_score(
    dimensions: Sequence[CritiqueDimension],
) -> float:
    """
    Calculates the average score across critique dimensions.

    Scores are expected to be from 1 to 5.
    """
    if not dimensions:
        raise ValueError("At least one critique dimension is required.")

    for dimension in dimensions:
        if not 1 <= dimension.score <= 5:
            raise ValueError(
                f"Score for {dimension.name!r} must be between 1 and 5."
            )

    return mean(dimension.score for dimension in dimensions)


critique_dimensions = [
    CritiqueDimension(
        "Problem clarity",
        4,
        "The product addresses a recognizable customer problem.",
    ),
    CritiqueDimension(
        "Usability",
        3,
        "The primary flow works but contains avoidable friction.",
    ),
    CritiqueDimension(
        "Value",
        4,
        "The product creates clear convenience for frequent users.",
    ),
    CritiqueDimension(
        "Differentiation",
        3,
        "Several competitors offer comparable functionality.",
    ),
    CritiqueDimension(
        "Retention potential",
        4,
        "Recurring household needs create opportunities for repeat use.",
    ),
]

print("\n--- Product critique scorecard ---")
for dimension in critique_dimensions:
    print(f"{dimension.name}: {dimension.score}/5")
    print("Reasoning:", dimension.reasoning)

print(
    "Average critique score:",
    f"{calculate_critique_score(critique_dimensions):.2f}/5",
)


# =============================================================================
# SECTION 21: CUSTOMER PAIN PRIORITIZATION
# =============================================================================

@dataclass
class CustomerPain:
    name: str
    severity: int
    frequency: int
    affected_population: int
    strategic_relevance: int

    def score(self) -> int:
        return (
            self.severity
            * self.frequency
            * self.affected_population
            * self.strategic_relevance
        )


customer_pains = [
    CustomerPain("Slow checkout", 5, 5, 5, 5),
    CustomerPain("Unclear delivery window", 4, 4, 4, 5),
    CustomerPain("Poor visual polish", 2, 3, 5, 2),
    CustomerPain("Limited reorder support", 4, 5, 4, 5),
]

print("\n--- Customer pain prioritization ---")
for pain in sorted(customer_pains, key=lambda item: item.score(), reverse=True):
    print(f"{pain.name}: {pain.score():,}")


# =============================================================================
# SECTION 22: EDGE CASES IN PRODUCT THINKING
# =============================================================================

def demonstrate_product_edge_cases() -> None:
    """
    Product decisions become difficult when normal assumptions break.

    Important edge cases include:
    - A problem is severe but rare.
    - A problem is common but minor.
    - A feature is popular but strategically harmful.
    - Users request a solution instead of describing the problem.
    - A metric improves while customer value decreases.
    - A solution helps one segment but harms another.
    """

    print("\n--- Product thinking edge cases ---")

    cases = [
        (
            "Severe but rare problem",
            "May require specialized handling rather than broad prioritization.",
        ),
        (
            "Common but minor problem",
            "Can become important at scale, especially when cumulative friction is high.",
        ),
        (
            "Popular feature request",
            "Popularity does not prove that the feature addresses the root problem.",
        ),
        (
            "Metric improves but satisfaction falls",
            "The metric may be incomplete or vulnerable to local optimization.",
        ),
        (
            "Segment conflict",
            "A product decision may benefit one segment while creating friction for another.",
        ),
        (
            "No evidence",
            "The appropriate action may be discovery rather than implementation.",
        ),
    ]

    for case, interpretation in cases:
        print(f"{case}: {interpretation}")


demonstrate_product_edge_cases()


# =============================================================================
# SECTION 23: FEATURE REQUEST ANALYSIS
# =============================================================================

@dataclass
class FeatureRequest:
    requested_by: str
    request: str
    underlying_goal: str
    evidence: List[str]

    def quality_of_request(self) -> str:
        """
        A feature request becomes stronger when it contains evidence about
        a repeated user problem rather than only a preferred implementation.
        """
        if len(self.evidence) >= 3:
            return "Strong evidence base"
        if len(self.evidence) == 2:
            return "Moderate evidence base"
        return "Weak evidence base"


feature_request = FeatureRequest(
    requested_by="Frequent customers",
    request="Add a reorder button",
    underlying_goal="Reduce the effort required to repeat common purchases",
    evidence=[
        "Users repeatedly search for the same products",
        "Order history is frequently visited",
        "Repeat customers have longer shopping sessions than expected",
    ],
)

print("\n--- Feature request analysis ---")
print("Request:", feature_request.request)
print("Underlying goal:", feature_request.underlying_goal)
print("Evidence quality:", feature_request.quality_of_request())


# =============================================================================
# SECTION 24: EXPERIMENT DESIGN
# =============================================================================

@dataclass
class Experiment:
    name: str
    hypothesis: str
    control: str
    treatment: str
    primary_metric: str
    guardrail_metrics: List[str]
    duration_days: int

    def validate(self) -> List[str]:
        problems = []

        if not self.hypothesis.strip():
            problems.append("Hypothesis is missing.")

        if not self.control.strip():
            problems.append("Control condition is missing.")

        if not self.treatment.strip():
            problems.append("Treatment condition is missing.")

        if not self.primary_metric.strip():
            problems.append("Primary metric is missing.")

        if self.duration_days <= 0:
            problems.append("Duration must be greater than zero.")

        if not self.guardrail_metrics:
            problems.append("At least one guardrail metric is recommended.")

        return problems


experiment = Experiment(
    name="One-tap reorder experiment",
    hypothesis=(
        "A personalized reorder entry point will reduce effort for "
        "frequent shoppers and increase successful repeat orders."
    ),
    control="Existing shopping experience",
    treatment="Personalized reorder entry point",
    primary_metric="Repeat-order completion rate",
    guardrail_metrics=[
        "Average order value",
        "Refund rate",
        "Customer support contacts",
    ],
    duration_days=21,
)

print("\n--- Experiment design ---")
print("Experiment:", experiment.name)
print("Hypothesis:", experiment.hypothesis)
print("Control:", experiment.control)
print("Treatment:", experiment.treatment)
print("Primary metric:", experiment.primary_metric)
print("Guardrails:", ", ".join(experiment.guardrail_metrics))
print("Validation errors:", experiment.validate())


# =============================================================================
# SECTION 25: EXPERIMENT RESULT INTERPRETATION
# =============================================================================

@dataclass
class ExperimentResult:
    control_metric: float
    treatment_metric: float
    control_guardrail: float
    treatment_guardrail: float

    def relative_lift(self) -> float:
        if self.control_metric == 0:
            raise ZeroDivisionError("Control metric cannot be zero.")
        return (
            self.treatment_metric - self.control_metric
        ) / self.control_metric

    def guardrail_change(self) -> float:
        if self.control_guardrail == 0:
            raise ZeroDivisionError("Control guardrail cannot be zero.")
        return (
            self.treatment_guardrail - self.control_guardrail
        ) / self.control_guardrail


experiment_result = ExperimentResult(
    control_metric=0.42,
    treatment_metric=0.49,
    control_guardrail=0.025,
    treatment_guardrail=0.026,
)

print("\n--- Experiment result ---")
print("Primary metric relative lift:", f"{experiment_result.relative_lift():.1%}")
print(
    "Guardrail relative change:",
    f"{experiment_result.guardrail_change():.1%}",
)
print(
    "Interpretation: The primary metric improved, but the guardrail should "
    "be examined before declaring the experiment successful."
)


# =============================================================================
# SECTION 26: PRODUCT DIAGNOSIS
# =============================================================================

@dataclass
class ProductDiagnosis:
    symptom: str
    possible_causes: List[str]
    evidence_to_collect: List[str]
    possible_interventions: List[str]


diagnosis = ProductDiagnosis(
    symptom="Checkout conversion decreased.",
    possible_causes=[
        "New checkout friction",
        "Payment failures",
        "Unexpected fees",
        "Delivery availability changes",
        "Lower-intent traffic mix",
    ],
    evidence_to_collect=[
        "Conversion funnel by checkout step",
        "Payment failure rates",
        "Traffic source conversion",
        "Customer support complaints",
        "Device and platform breakdown",
    ],
    possible_interventions=[
        "Fix the highest-volume technical failure",
        "Reduce unnecessary checkout steps",
        "Clarify fees earlier",
        "Improve payment recovery",
    ],
)

print("\n--- Product diagnosis ---")
print("Symptom:", diagnosis.symptom)

print("Possible causes:")
for cause in diagnosis.possible_causes:
    print(" -", cause)

print("Evidence to collect:")
for evidence in diagnosis.evidence_to_collect:
    print(" -", evidence)

print("Possible interventions:")
for intervention in diagnosis.possible_interventions:
    print(" -", intervention)


# =============================================================================
# SECTION 27: FUNNEL DIAGNOSTIC ANALYSIS
# =============================================================================

def identify_largest_funnel_drop(
    funnel_rates: Dict[str, float],
) -> Tuple[str, float]:
    """
    Identifies the lowest conversion stage.

    A low conversion stage is a signal for investigation, not automatic proof
    that the stage is the root cause.
    """
    if not funnel_rates:
        raise ValueError("Funnel rates cannot be empty.")

    stage, rate = min(funnel_rates.items(), key=lambda item: item[1])
    return stage, rate


largest_drop_stage, largest_drop_rate = identify_largest_funnel_drop(
    funnel.conversion_rates()
)

print("\n--- Funnel diagnosis ---")
print(
    "Lowest conversion stage:",
    largest_drop_stage,
    f"({largest_drop_rate:.1%})",
)
print(
    "Important distinction: the lowest conversion rate does not automatically "
    "identify the root cause. The stage may naturally have lower conversion."
)


# =============================================================================
# SECTION 28: AARRR-STYLE PRODUCT ANALYSIS
# =============================================================================

@dataclass
class PirateFunnel:
    acquisition: int
    activation: int
    retention: int
    revenue: int
    referral: int

    def rates(self) -> Dict[str, float]:
        """
        Returns stage counts as percentages of the original acquisition base.

        Real analytics often require cohort-specific denominators. This simple
        example is designed to demonstrate the concept.
        """
        if self.acquisition <= 0:
            raise ValueError("Acquisition must be greater than zero.")

        return {
            "acquisition": self.acquisition / self.acquisition,
            "activation": self.activation / self.acquisition,
            "retention": self.retention / self.acquisition,
            "revenue": self.revenue / self.acquisition,
            "referral": self.referral / self.acquisition,
        }


aarrr = PirateFunnel(
    acquisition=10000,
    activation=6200,
    retention=3100,
    revenue=1800,
    referral=900,
)

print("\n--- AARRR-style analysis ---")
for stage, rate in aarr.rates().items():
    print(f"{stage}: {rate:.1%}")


# =============================================================================
# SECTION 29: NORTH-STAR METRIC DESIGN EXERCISE
# =============================================================================

@dataclass
class NorthStarCandidate:
    name: str
    customer_value: int
    frequency: int
    measurability: int
    strategic_alignment: int

    def score(self) -> int:
        return (
            self.customer_value
            * self.frequency
            * self.measurability
            * self.strategic_alignment
        )


north_star_candidates = [
    NorthStarCandidate(
        "App sessions",
        customer_value=2,
        frequency=5,
        measurability=5,
        strategic_alignment=2,
    ),
    NorthStarCandidate(
        "Successful orders",
        customer_value=5,
        frequency=4,
        measurability=5,
        strategic_alignment=5,
    ),
    NorthStarCandidate(
        "Push notification opens",
        customer_value=1,
        frequency=3,
        measurability=5,
        strategic_alignment=1,
    ),
]

print("\n--- North-star metric exercise ---")
for candidate in sorted(
    north_star_candidates,
    key=lambda item: item.score(),
    reverse=True,
):
    print(f"{candidate.name}: {candidate.score():,}")


# =============================================================================
# SECTION 30: PRODUCT TRADE-OFFS
# =============================================================================

@dataclass
class TradeOff:
    decision: str
    benefit: str
    cost: str
    affected_party: str
    reversibility: str


tradeoffs = [
    TradeOff(
        decision="Add aggressive promotional discounts",
        benefit="Potentially increases short-term orders",
        cost="Can reduce margin and train customers to wait for discounts",
        affected_party="Business and price-sensitive customers",
        reversibility="Medium",
    ),
    TradeOff(
        decision="Require more verification during checkout",
        benefit="May reduce fraud",
        cost="Creates additional customer friction",
        affected_party="Customers and risk operations",
        reversibility="High",
    ),
    TradeOff(
        decision="Prioritize delivery speed",
        benefit="Improves convenience",
        cost="May increase operational cost",
        affected_party="Customers and operations",
        reversibility="Medium",
    ),
]

print("\n--- Product trade-offs ---")
for tradeoff in tradeoffs:
    print(f"\nDecision: {tradeoff.decision}")
    print("Benefit:", tradeoff.benefit)
    print("Cost:", tradeoff.cost)
    print("Affected party:", tradeoff.affected_party)
    print("Reversibility:", tradeoff.reversibility)


# =============================================================================
# SECTION 31: SEGMENT-SPECIFIC PRODUCT DECISIONS
# =============================================================================

def compare_segment_needs(
    user_segments: Sequence[UserSegment],
) -> Dict[str, List[str]]:
    """
    Creates a simplified segment-to-need map.

    This demonstrates why a product should not assume that every user has
    identical motivations.
    """

    mapping: Dict[str, List[str]] = {}

    for segment in user_segments:
        mapping[segment.name] = segment.pain_points

    return mapping


print("\n--- Segment-specific needs ---")
for segment_name, pains in compare_segment_needs(segments).items():
    print(segment_name, "->", ", ".join(pains))


# =============================================================================
# SECTION 32: PRODUCT DESIGN CONSTRAINTS
# =============================================================================

@dataclass
class Constraint:
    name: str
    type: str
    description: str
    consequence: str


constraints = [
    Constraint(
        "Regulatory",
        "External",
        "Certain financial, healthcare, or identity flows may have legal requirements.",
        "The ideal user flow may need additional verification or disclosures.",
    ),
    Constraint(
        "Technical",
        "Internal",
        "Legacy systems may limit available capabilities.",
        "A theoretically simple feature may require substantial engineering work.",
    ),
    Constraint(
        "Operational",
        "Internal",
        "Delivery capacity may vary by geography and time.",
        "Product promises must align with real operational capacity.",
    ),
    Constraint(
        "Economic",
        "Business",
        "Every feature consumes resources and affects unit economics.",
        "Customer value must be evaluated alongside cost.",
    ),
]

print("\n--- Product constraints ---")
for constraint in constraints:
    print(f"\n{constraint.name} ({constraint.type})")
    print("Description:", constraint.description)
    print("Consequence:", constraint.consequence)


# =============================================================================
# SECTION 33: SECURITY AND TRUST IN PRODUCT THINKING
# =============================================================================

@dataclass
class TrustRisk:
    risk: str
    product_effect: str
    mitigation: str


trust_risks = [
    TrustRisk(
        "Payment data exposure",
        "Customers may lose confidence in the service.",
        "Minimize sensitive-data exposure and use secure payment infrastructure.",
    ),
    TrustRisk(
        "Incorrect personalization",
        "Recommendations can feel intrusive or misleading.",
        "Use transparent controls and appropriate data boundaries.",
    ),
    TrustRisk(
        "Dark patterns",
        "Short-term conversion may increase while trust declines.",
        "Make fees, subscriptions, cancellations, and choices explicit.",
    ),
    TrustRisk(
        "Unclear consent",
        "Users may not understand how their information is used.",
        "Provide understandable consent and privacy controls.",
    ),
]

print("\n--- Security and trust considerations ---")
for risk in trust_risks:
    print(f"\nRisk: {risk.risk}")
    print("Product effect:", risk.product_effect)
    print("Mitigation:", risk.mitigation)


# =============================================================================
# SECTION 34: COMMON PRODUCT THINKING MISTAKES
# =============================================================================

common_mistakes = {
    "Starting with a solution": (
        "A proposed feature is treated as the problem before the problem "
        "has been validated."
    ),
    "Confusing requests with needs": (
        "Customers may request a specific implementation when their real "
        "need is broader."
    ),
    "Feature counting": (
        "More functionality is incorrectly treated as proof of better product quality."
    ),
    "Metric tunnel vision": (
        "A single metric is optimized without checking customer or business guardrails."
    ),
    "Ignoring segmentation": (
        "A product decision is evaluated against an average user who may not exist."
    ),
    "Assuming correlation is causation": (
        "A relationship between two measurements is interpreted as causal without evidence."
    ),
    "Copying competitors": (
        "A competitor feature is copied without understanding the underlying strategy."
    ),
    "Skipping trade-offs": (
        "Benefits are documented while costs, risks, and affected parties are ignored."
    ),
}

print("\n--- Common product thinking mistakes ---")
for mistake, explanation in common_mistakes.items():
    print(f"\n{mistake}:")
    print(explanation)


# =============================================================================
# SECTION 35: PRODUCT TEARDOWN CHECKLIST
# =============================================================================

TEARDOWN_CHECKLIST = [
    "Identify the target customer and user.",
    "Describe the customer's context.",
    "Identify the core job to be done.",
    "State the primary problem.",
    "Identify the desired customer outcome.",
    "Describe the value proposition.",
    "Map the main user journey.",
    "Identify friction points.",
    "Map important features to user problems.",
    "Identify the monetization model.",
    "Identify important product metrics.",
    "Analyze retention mechanisms.",
    "Analyze differentiation.",
    "Identify trust and security concerns.",
    "Identify operational and technical constraints.",
    "Identify product strengths.",
    "Identify weaknesses.",
    "Separate symptoms from root causes.",
    "Generate opportunities.",
    "Prioritize opportunities using evidence and trade-offs.",
]

print("\n--- Product teardown checklist ---")
for number, item in enumerate(TEARDOWN_CHECKLIST, start=1):
    print(f"{number:02d}. {item}")


# =============================================================================
# SECTION 36: PRODUCT CRITIQUE TEMPLATE
# =============================================================================

def build_product_critique(
    product_name: str,
    user: str,
    observation: str,
    problem: str,
    evidence: Sequence[str],
    opportunity: str,
) -> Dict[str, object]:
    """
    Produces a structured critique record.

    The function deliberately separates:
    - what was observed,
    - what is believed to be happening,
    - what evidence exists,
    - and what opportunity may follow.
    """

    return {
        "product": product_name,
        "user": user,
        "observation": observation,
        "suspected_problem": problem,
        "evidence": list(evidence),
        "opportunity": opportunity,
    }


critique_record = build_product_critique(
    product_name="QuickCart",
    user="Frequent household shoppers",
    observation="Repeat customers frequently revisit order history.",
    problem="Customers may not have a sufficiently direct repeat-purchase path.",
    evidence=[
        "High order-history visits",
        "Frequent recurring purchases",
        "Long sessions during repeat shopping",
    ],
    opportunity="Create a faster repeat-order workflow.",
)

print("\n--- Structured critique record ---")
for key, value in critique_record.items():
    print(f"{key}: {value}")


# =============================================================================
# SECTION 37: ADVANCED OPPORTUNITY SCORING
# =============================================================================

@dataclass
class AdvancedOpportunity:
    name: str
    reach: float
    pain_severity: float
    frequency: float
    strategic_fit: float
    evidence: float
    implementation_risk: float
    operational_complexity: float

    def score(self) -> float:
        """
        A custom opportunity score.

        Higher implementation risk and operational complexity reduce the score.
        This is useful for teaching structured reasoning, but it should not be
        treated as a universal prioritization formula.
        """

        denominator = (
            self.implementation_risk
            + self.operational_complexity
        )

        if denominator <= 0:
            raise ValueError("Risk and complexity must produce a positive denominator.")

        return (
            self.reach
            * self.pain_severity
            * self.frequency
            * self.strategic_fit
            * self.evidence
            / denominator
        )


advanced_opportunities = [
    AdvancedOpportunity(
        "One-tap recurring basket",
        reach=8,
        pain_severity=5,
        frequency=5,
        strategic_fit=5,
        evidence=4,
        implementation_risk=2,
        operational_complexity=2,
    ),
    AdvancedOpportunity(
        "Predictive shopping assistant",
        reach=7,
        pain_severity=3,
        frequency=4,
        strategic_fit=4,
        evidence=2,
        implementation_risk=5,
        operational_complexity=4,
    ),
    AdvancedOpportunity(
        "Delivery-slot redesign",
        reach=8,
        pain_severity=4,
        frequency=4,
        strategic_fit=5,
        evidence=4,
        implementation_risk=3,
        operational_complexity=4,
    ),
]

print("\n--- Advanced opportunity scoring ---")
for opportunity in sorted(
    advanced_opportunities,
    key=lambda item: item.score(),
    reverse=True,
):
    print(f"{opportunity.name}: {opportunity.score():.2f}")


# =============================================================================
# SECTION 38: PRODUCT COUNTERFACTUAL EXERCISES
# =============================================================================

counterfactual_questions = [
    "What would happen if this feature disappeared tomorrow?",
    "Which users would notice first?",
    "Which user problem would return?",
    "Could another workflow solve the same problem more simply?",
    "What happens if usage grows by 10x?",
    "What happens if the product enters a new geographic market?",
    "What happens if the product serves a less technical user segment?",
    "Which assumptions would become invalid under those conditions?",
]

print("\n--- Counterfactual product exercises ---")
for question in counterfactual_questions:
    print("-", question)


# =============================================================================
# SECTION 39: PRODUCT METRIC FAILURE MODES
# =============================================================================

@dataclass
class MetricFailureMode:
    name: str
    example: str
    defense: str


metric_failure_modes = [
    MetricFailureMode(
        "Goodhart's Law",
        "Optimizing clicks can increase meaningless clicks.",
        "Define metrics around meaningful customer outcomes.",
    ),
    MetricFailureMode(
        "Survivorship bias",
        "Studying only retained users can hide why others left.",
        "Analyze both retained and churned cohorts.",
    ),
    MetricFailureMode(
        "Selection bias",
        "Surveying only highly engaged users may produce overly positive feedback.",
        "Include representative user groups.",
    ),
    MetricFailureMode(
        "Vanity metrics",
        "Total registrations can rise without active product usage.",
        "Track activation, retention, and value creation.",
    ),
    MetricFailureMode(
        "Local optimization",
        "Checkout conversion improves while refunds increase.",
        "Use guardrail metrics.",
    ),
]

print("\n--- Metric failure modes ---")
for mode in metric_failure_modes:
    print(f"\n{mode.name}")
    print("Example:", mode.example)
    print("Defense:", mode.defense)


# =============================================================================
# SECTION 40: PRODUCT EXPERIMENT DECISION LOGIC
# =============================================================================

def interpret_experiment(
    control: float,
    treatment: float,
    guardrail_control: float,
    guardrail_treatment: float,
    minimum_lift: float = 0.05,
    maximum_guardrail_degradation: float = 0.10,
) -> str:
    """
    Provides a simple decision rule for educational purposes.

    Real experimentation requires statistical inference, experiment design,
    sample-size planning, randomization checks, and appropriate confidence
    intervals or Bayesian analysis.
    """

    if control <= 0:
        raise ValueError("Control value must be positive.")

    lift = (treatment - control) / control

    if guardrail_control == 0:
        guardrail_change = 0.0
    else:
        guardrail_change = (
            guardrail_treatment - guardrail_control
        ) / guardrail_control

    if lift >= minimum_lift and guardrail_change <= maximum_guardrail_degradation:
        return "Promising result; investigate statistical and practical significance."

    if lift < minimum_lift:
        return "Primary metric improvement is below the desired threshold."

    return "Guardrail degradation requires investigation."


print("\n--- Experiment interpretation ---")
print(
    interpret_experiment(
        control=0.40,
        treatment=0.47,
        guardrail_control=0.020,
        guardrail_treatment=0.021,
    )
)


# =============================================================================
# SECTION 41: PRODUCT DESIGN EXERCISE GENERATOR
# =============================================================================

@dataclass
class ProductExercise:
    title: str
    prompt: str
    expected_analysis: List[str]


exercises = [
    ProductExercise(
        title="Checkout teardown",
        prompt="Analyze an online shopping checkout and identify three sources of friction.",
        expected_analysis=[
            "User goal",
            "Friction point",
            "Potential root cause",
            "Evidence needed",
            "Opportunity",
        ],
    ),
    ProductExercise(
        title="Streaming product critique",
        prompt="Critique a streaming service whose users struggle to choose what to watch.",
        expected_analysis=[
            "Decision problem",
            "User segments",
            "Discovery journey",
            "Recommendation trade-offs",
            "Success metrics",
        ],
    ),
    ProductExercise(
        title="Banking opportunity identification",
        prompt="Identify opportunities for a digital banking product serving first-time investors.",
        expected_analysis=[
            "User context",
            "Jobs to be done",
            "Trust barriers",
            "Financial-product constraints",
            "Opportunity areas",
        ],
    ),
    ProductExercise(
        title="Learning product teardown",
        prompt="Analyze a learning application with high acquisition but weak retention.",
        expected_analysis=[
            "Activation definition",
            "Learning journey",
            "Retention drivers",
            "Root-cause hypotheses",
            "Experiments",
        ],
    ),
]

print("\n--- Product thinking exercises ---")
for exercise in exercises:
    print(f"\n{exercise.title}")
    print("Prompt:", exercise.prompt)
    print("Analyze:")
    for item in exercise.expected_analysis:
        print(" -", item)


# =============================================================================
# SECTION 42: COMPLETE END-TO-END CASE STUDY
# =============================================================================

@dataclass
class CaseStudy:
    product: Product
    segment: UserSegment
    job: JobStatement
    problem: ProblemStatement
    opportunity: Opportunity
    hypothesis: Hypothesis
    experiment: Experiment


case_study = CaseStudy(
    product=sample_product,
    segment=segments[1],
    job=job,
    problem=problem_statement,
    opportunity=opportunities[0],
    hypothesis=hypothesis,
    experiment=experiment,
)


def run_case_study(case: CaseStudy) -> None:
    """
    Runs a complete product-thinking workflow.

    The sequence is intentionally:

        Product
          ↓
        User
          ↓
        Job
          ↓
        Problem
          ↓
        Opportunity
          ↓
        Hypothesis
          ↓
        Experiment

    This prevents jumping directly from a vague complaint to a feature.
    """

    print("\n--- Complete end-to-end case study ---")

    print("\n1. Product")
    print(case.product.name)

    print("\n2. User segment")
    print(case.segment.name)
    print("Context:", case.segment.context)
    print("Goal:", case.segment.goal)

    print("\n3. Job")
    print(case.job.sentence())

    print("\n4. Problem")
    print(case.problem.formulate())

    print("\n5. Opportunity")
    print(case.opportunity.name)
    print("Customer problem:", case.opportunity.customer_problem)
    print("Opportunity score:", case.opportunity.score())

    print("\n6. Hypothesis")
    print(case.hypothesis.statement())

    print("\n7. Experiment")
    print(case.experiment.name)
    print("Control:", case.experiment.control)
    print("Treatment:", case.experiment.treatment)
    print("Primary metric:", case.experiment.primary_metric)
    print("Guardrails:", ", ".join(case.experiment.guardrail_metrics))


run_case_study(case_study)


# =============================================================================
# SECTION 43: PRODUCT TEARDOWN QUESTIONS
# =============================================================================

teardown_questions = [
    "Who is the primary user?",
    "Who is the customer or economic buyer?",
    "What situation causes the user to seek the product?",
    "What job is the user trying to accomplish?",
    "What is the most important problem?",
    "What alternatives existed before the product?",
    "What is the product's core value proposition?",
    "Which feature creates the most customer value?",
    "Which feature may be unnecessary?",
    "Where does the main journey begin?",
    "Where does it end?",
    "Where does the user experience friction?",
    "What causes users to abandon the journey?",
    "What encourages users to return?",
    "How does the company monetize the product?",
    "What are the key product metrics?",
    "Which metric could be misleading?",
    "What are the main operational constraints?",
    "What are the major security and trust risks?",
    "What differentiates the product?",
    "Which competitors solve the same problem differently?",
    "Which customer segments are underserved?",
    "What opportunity has the strongest evidence?",
    "What should be tested before being built?",
]

print("\n--- Product teardown questions ---")
for question in teardown_questions:
    print("-", question)


# =============================================================================
# SECTION 44: PRODUCT CRITIQUE QUESTIONS
# =============================================================================

critique_questions = [
    "What specifically is confusing?",
    "Which user encounters the problem?",
    "How frequently does it occur?",
    "How severe is the consequence?",
    "Is the problem functional, emotional, economic, or operational?",
    "Is the problem caused by product design or an external constraint?",
    "What evidence supports the critique?",
    "What evidence could disprove it?",
    "Could the observed behavior be intentional?",
    "Does the issue affect all segments equally?",
    "What metric should move if the problem is real?",
    "What guardrail could prevent unintended consequences?",
]

print("\n--- Product critique questions ---")
for question in critique_questions:
    print("-", question)


# =============================================================================
# SECTION 45: OPPORTUNITY IDENTIFICATION QUESTIONS
# =============================================================================

opportunity_questions = [
    "Which user problem is both meaningful and recurring?",
    "How many users experience it?",
    "How often do they experience it?",
    "How painful is it?",
    "What is the current workaround?",
    "How costly is the workaround?",
    "How well do existing alternatives solve it?",
    "Does solving it support product strategy?",
    "Can the organization realistically solve it?",
    "What evidence currently exists?",
    "What evidence is missing?",
    "What experiment could reduce uncertainty?",
]

print("\n--- Opportunity identification questions ---")
for question in opportunity_questions:
    print("-", question)


# =============================================================================
# SECTION 46: PRODUCT THINKING DECISION FRAMEWORK
# =============================================================================

def product_decision_framework(
    user_problem: str,
    evidence_strength: int,
    user_impact: int,
    frequency: int,
    strategic_fit: int,
    implementation_effort: int,
    risk: int,
) -> Dict[str, object]:
    """
    Produces a structured product decision assessment.

    All dimensions are 1-5.

    The output intentionally contains both an opportunity score and the
    underlying dimensions so that the score does not become a black box.
    """

    dimensions = {
        "evidence_strength": evidence_strength,
        "user_impact": user_impact,
        "frequency": frequency,
        "strategic_fit": strategic_fit,
        "implementation_effort": implementation_effort,
        "risk": risk,
    }

    for name, value in dimensions.items():
        if not 1 <= value <= 5:
            raise ValueError(f"{name} must be between 1 and 5.")

    opportunity_score = (
        evidence_strength
        * user_impact
        * frequency
        * strategic_fit
    )

    complexity_score = implementation_effort * risk

    if opportunity_score >= 300 and complexity_score <= 8:
        recommendation = "Strong candidate for validation and potential prioritization."
    elif opportunity_score >= 200:
        recommendation = "Promising opportunity; gather more evidence."
    else:
        recommendation = "Do not prioritize yet; investigate the problem further."

    return {
        "user_problem": user_problem,
        "dimensions": dimensions,
        "opportunity_score": opportunity_score,
        "complexity_score": complexity_score,
        "recommendation": recommendation,
    }


decision = product_decision_framework(
    user_problem="Frequent customers spend too much time rebuilding recurring baskets.",
    evidence_strength=4,
    user_impact=5,
    frequency=5,
    strategic_fit=5,
    implementation_effort=2,
    risk=2,
)

print("\n--- Product decision framework ---")
for key, value in decision.items():
    print(f"{key}: {value}")


# =============================================================================
# SECTION 47: ADVANCED PRODUCT THINKING PRINCIPLES
# =============================================================================

advanced_principles = [
    (
        "Problem space before solution space",
        "Understand the customer problem and its context before choosing an implementation."
    ),
    (
        "Outcome over output",
        "A shipped feature is an output; improved customer behavior or business value is an outcome."
    ),
    (
        "Evidence over intuition",
        "Intuition can generate hypotheses, but evidence should influence confidence."
    ),
    (
        "Segment before generalizing",
        "Different users can have different jobs, constraints, and definitions of value."
    ),
    (
        "Systems thinking",
        "A local improvement can create downstream effects in operations, economics, trust, or retention."
    ),
    (
        "Trade-offs are part of product quality",
        "A product decision is incomplete without considering what it makes worse."
    ),
    (
        "Reversibility matters",
        "Low-cost reversible experiments can be preferable to irreversible large investments."
    ),
    (
        "Metrics require context",
        "A metric becomes meaningful only when its denominator, time window, cohort, and business context are understood."
    ),
]

print("\n--- Advanced product thinking principles ---")
for principle, explanation in advanced_principles:
    print(f"\n{principle}")
    print(explanation)


# =============================================================================
# SECTION 48: PERFORMANCE AND ANALYTICAL EFFICIENCY
# =============================================================================

def rank_items(
    items: Iterable[Tuple[str, float]],
    descending: bool = True,
) -> List[Tuple[str, float]]:
    """
    Efficiently ranks a collection of scored product opportunities.

    Python's built-in sorting is O(n log n), which is normally appropriate for
    product prioritization datasets of practical size.

    For extremely large datasets or streaming analytics, specialized data
    structures or database-side ranking may be more appropriate.
    """

    return sorted(items, key=lambda item: item[1], reverse=descending)


ranked = rank_items(
    [
        ("Opportunity A", 92.0),
        ("Opportunity B", 75.0),
        ("Opportunity C", 88.0),
        ("Opportunity D", 63.0),
    ]
)

print("\n--- Opportunity ranking ---")
for item, score in ranked:
    print(item, score)


# =============================================================================
# SECTION 49: STATISTICAL REASONING BASICS FOR PRODUCT EXPERIMENTS
# =============================================================================

def proportion_difference(
    control_successes: int,
    control_trials: int,
    treatment_successes: int,
    treatment_trials: int,
) -> Dict[str, float]:
    """
    Calculates basic conversion rates and absolute/relative differences.

    This does not establish statistical significance.
    """

    if control_trials <= 0 or treatment_trials <= 0:
        raise ValueError("Trial counts must be positive.")

    control_rate = control_successes / control_trials
    treatment_rate = treatment_successes / treatment_trials

    absolute_difference = treatment_rate - control_rate

    if control_rate == 0:
        relative_difference = 0.0
    else:
        relative_difference = absolute_difference / control_rate

    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "absolute_difference": absolute_difference,
        "relative_difference": relative_difference,
    }


statistical_example = proportion_difference(
    control_successes=420,
    control_trials=1000,
    treatment_successes=490,
    treatment_trials=1000,
)

print("\n--- Experiment measurement ---")
for key, value in statistical_example.items():
    print(f"{key}: {value:.3f}")


# =============================================================================
# SECTION 50: SIMPLE CONFIDENCE-INTERVAL BUILDING BLOCK
# =============================================================================

def approximate_proportion_standard_error(
    proportion: float,
    sample_size: int,
) -> float:
    """
    Calculates the standard error for a binomial proportion.

    This is an educational building block rather than a complete experiment
    analysis methodology.
    """

    if sample_size <= 0:
        raise ValueError("Sample size must be positive.")

    if not 0 <= proportion <= 1:
        raise ValueError("Proportion must be between 0 and 1.")

    return sqrt(
        proportion * (1 - proportion) / sample_size
    )


def approximate_95_percent_interval(
    proportion: float,
    sample_size: int,
) -> Tuple[float, float]:
    """
    Calculates a simple normal approximation to a 95% confidence interval.

    The normal approximation can perform poorly for small samples or extreme
    proportions. Production analysis should use an appropriate statistical
    method for the experiment design.
    """

    standard_error = approximate_proportion_standard_error(
        proportion,
        sample_size,
    )

    margin = 1.96 * standard_error

    return (
        max(0.0, proportion - margin),
        min(1.0, proportion + margin),
    )


interval = approximate_95_percent_interval(
    proportion=0.49,
    sample_size=1000,
)

print("\n--- Approximate confidence interval ---")
print(
    f"Conversion rate: 49.0%, "
    f"approximate 95% interval: {interval[0]:.1%} to {interval[1]:.1%}"
)


# =============================================================================
# SECTION 51: PRODUCT DISCOVERY VS DELIVERY
# =============================================================================

@dataclass
class WorkType:
    name: str
    central_question: str
    typical_activity: str
    output: str


work_types = [
    WorkType(
        "Product discovery",
        "Are we solving the right problem?",
        "Research, analysis, interviews, experimentation",
        "Validated problem, opportunity, or hypothesis",
    ),
    WorkType(
        "Product delivery",
        "Can we build and operate the chosen solution effectively?",
        "Design, engineering, testing, release",
        "Working product capability",
    ),
    WorkType(
        "Product measurement",
        "Did the product create the intended outcome?",
        "Analytics, experiments, cohort analysis",
        "Evidence about outcomes",
    ),
]

print("\n--- Discovery, delivery, and measurement ---")
for work_type in work_types:
    print(f"\n{work_type.name}")
    print("Central question:", work_type.central_question)
    print("Typical activity:", work_type.typical_activity)
    print("Output:", work_type.output)


# =============================================================================
# SECTION 52: PRODUCT THINKING INTERVIEW EXERCISES
# =============================================================================

interview_cases = [
    {
        "question": "How would you improve a food delivery application?",
        "first_step": "Define the target user and identify the specific problem before proposing features.",
    },
    {
        "question": "A ride-sharing app has declining rides. What would you investigate?",
        "first_step": "Decompose the problem by acquisition, activation, supply, demand, geography, time, and user segment.",
    },
    {
        "question": "Users complain that a banking app is difficult to use.",
        "first_step": "Identify the exact journey and task where users experience difficulty.",
    },
    {
        "question": "A learning application has many registrations but low retention.",
        "first_step": "Define activation and examine where users fail to experience meaningful learning value.",
    },
]

print("\n--- Product interview exercises ---")
for case in interview_cases:
    print("\nQuestion:", case["question"])
    print("Recommended first analytical move:", case["first_step"])


# =============================================================================
# SECTION 53: PRODUCT TEARDOWN MINI EXERCISES
# =============================================================================

mini_products = [
    {
        "name": "Digital wallet",
        "question": "Why would a user choose this wallet instead of cash, cards, or another wallet?",
    },
    {
        "name": "Professional networking platform",
        "question": "What recurring user job causes professionals to return?",
    },
    {
        "name": "Video streaming platform",
        "question": "Where does the product create friction between wanting entertainment and starting content?",
    },
    {
        "name": "Food delivery application",
        "question": "Which part of the journey most directly determines successful order completion?",
    },
    {
        "name": "Online education platform",
        "question": "What must happen after signup for the user to perceive meaningful value?",
    },
]

print("\n--- Mini teardown exercises ---")
for product_case in mini_products:
    print(f"\n{product_case['name']}")
    print(product_case["question"])


# =============================================================================
# SECTION 54: ADVANCED CASE: DECLINING RETENTION
# =============================================================================

@dataclass
class RetentionCohort:
    cohort: str
    users: int
    day_7_retained: int
    day_30_retained: int

    def retention_rates(self) -> Dict[str, float]:
        if self.users <= 0:
            raise ValueError("Users must be positive.")

        return {
            "day_7": self.day_7_retained / self.users,
            "day_30": self.day_30_retained / self.users,
        }


retention_cohorts = [
    RetentionCohort("January", 10000, 4300, 2200),
    RetentionCohort("February", 9800, 4100, 2050),
    RetentionCohort("March", 10200, 3500, 1600),
]

print("\n--- Retention cohort analysis ---")
for cohort in retention_cohorts:
    rates = cohort.retention_rates()
    print(
        f"{cohort.cohort}: "
        f"day_7={rates['day_7']:.1%}, "
        f"day_30={rates['day_30']:.1%}"
    )

print(
    "\nAnalytical exercise: determine whether the retention decline is "
    "associated with acquisition source, product changes, user mix, "
    "operational performance, or changes in customer expectations."
)


# =============================================================================
# SECTION 55: ROOT-CAUSE HYPOTHESIS MATRIX
# =============================================================================

@dataclass
class RootCauseHypothesis:
    cause: str
    predicted_signal: str
    evidence_source: str
    confidence: int

    def priority(self) -> int:
        return self.confidence


root_cause_hypotheses = [
    RootCauseHypothesis(
        "Onboarding became longer",
        "Activation rate decreases immediately after onboarding change",
        "Funnel analytics and release timeline",
        5,
    ),
    RootCauseHypothesis(
        "Traffic quality changed",
        "Retention decreases primarily for new acquisition channels",
        "Cohort and acquisition-source analysis",
        4,
    ),
    RootCauseHypothesis(
        "Core value became less reliable",
        "Retention decreases across existing and new users",
        "Product reliability and customer support data",
        4,
    ),
    RootCauseHypothesis(
        "Competition changed",
        "Churn increases among segments exposed to alternatives",
        "Competitive research and churn interviews",
        2,
    ),
]

print("\n--- Root-cause hypothesis matrix ---")
for hypothesis_item in sorted(
    root_cause_hypotheses,
    key=lambda item: item.priority(),
    reverse=True,
):
    print(f"\nCause: {hypothesis_item.cause}")
    print("Predicted signal:", hypothesis_item.predicted_signal)
    print("Evidence source:", hypothesis_item.evidence_source)
    print("Confidence:", hypothesis_item.confidence, "/ 5")


# =============================================================================
# SECTION 56: PRODUCT OPPORTUNITY VS FEATURE
# =============================================================================

@dataclass
class OpportunityVsFeature:
    opportunity: str
    possible_solutions: List[str]


opportunity_example = OpportunityVsFeature(
    opportunity="Reduce effort for customers making recurring purchases",
    possible_solutions=[
        "One-tap reorder",
        "Saved baskets",
        "Smart reorder reminders",
        "Order-history shortcuts",
        "Subscription for recurring products",
    ],
)

print("\n--- Opportunity versus feature ---")
print("Opportunity:", opportunity_example.opportunity)
print("Possible solutions:")
for solution in opportunity_example.possible_solutions:
    print(" -", solution)

print(
    "\nThe opportunity is broader than any single feature. "
    "This keeps the product team from prematurely committing to one implementation."
)


# =============================================================================
# SECTION 57: PRODUCT STRATEGY CONNECTION
# =============================================================================

@dataclass
class StrategicLink:
    product_goal: str
    customer_outcome: str
    business_outcome: str
    metric: str


strategic_link = StrategicLink(
    product_goal="Increase repeat purchasing",
    customer_outcome="Reduce effort for recurring shopping",
    business_outcome="Increase retention and customer lifetime value",
    metric="Successful repeat-order rate",
)

print("\n--- Product strategy connection ---")
print("Product goal:", strategic_link.product_goal)
print("Customer outcome:", strategic_link.customer_outcome)
print("Business outcome:", strategic_link.business_outcome)
print("Metric:", strategic_link.metric)


# =============================================================================
# SECTION 58: PRODUCT REVIEW WITH RED FLAGS
# =============================================================================

@dataclass
class ProductReview:
    positive_observations: List[str]
    concerns: List[str]
    unanswered_questions: List[str]
    evidence_required: List[str]

    def red_flag_count(self) -> int:
        return len(self.concerns)


product_review = ProductReview(
    positive_observations=[
        "Clear recurring customer use case",
        "Convenient digital purchase flow",
        "Potential for repeat behavior",
    ],
    concerns=[
        "Checkout friction",
        "Unclear differentiation",
        "Potential dependence on discounts",
    ],
    unanswered_questions=[
        "Why do users abandon checkout?",
        "Which segment has the highest lifetime value?",
        "What causes repeat customers to return?",
    ],
    evidence_required=[
        "Funnel data",
        "Cohort retention data",
        "Customer interviews",
        "Operational performance data",
    ],
)

print("\n--- Product review ---")
print("Positive observations:")
for item in product_review.positive_observations:
    print(" -", item)

print("Concerns:")
for item in product_review.concerns:
    print(" -", item)

print("Unanswered questions:")
for item in product_review.unanswered_questions:
    print(" -", item)

print("Evidence required:")
for item in product_review.evidence_required:
    print(" -", item)

print("Red flag count:", product_review.red_flag_count())


# =============================================================================
# SECTION 59: FINAL PRACTICE FRAMEWORK
# =============================================================================

def product_thinking_workflow(product_name: str) -> List[str]:
    """
    Returns a reusable workflow for performing a product-thinking exercise.
    """

    if not product_name.strip():
        raise ValueError("Product name cannot be empty.")

    return [
        f"1. Define the product: {product_name}",
        "2. Identify the primary user and customer.",
        "3. Identify the user's context and job.",
        "4. State the most important problem.",
        "5. Describe the desired customer outcome.",
        "6. Map the current journey.",
        "7. Identify friction and failure points.",
        "8. Separate observations from hypotheses.",
        "9. Identify root causes.",
        "10. Generate opportunity areas.",
        "11. Separate opportunities from specific features.",
        "12. Evaluate evidence.",
        "13. Estimate user and business impact.",
        "14. Identify constraints and trade-offs.",
        "15. Select measurable hypotheses.",
        "16. Design experiments before committing to large solutions.",
        "17. Define primary and guardrail metrics.",
        "18. Analyze results without confusing correlation and causation.",
        "19. Reassess the product decision using new evidence.",
    ]


print("\n--- Reusable product-thinking workflow ---")
for step in product_thinking_workflow("QuickCart"):
    print(step)


# =============================================================================
# SECTION 60: PRACTICE ASSIGNMENT
# =============================================================================

practice_assignment = {
    "task": "Perform a complete product teardown.",
    "select_one": [
        "Digital banking application",
        "Food delivery application",
        "Online learning platform",
        "Professional networking platform",
        "Online marketplace",
    ],
    "required_analysis": [
        "Target user",
        "Customer",
        "User context",
        "Job to be done",
        "Primary problem",
        "Value proposition",
        "Main journey",
        "Three friction points",
        "Two root-cause hypotheses",
        "Three opportunity areas",
        "Three possible solutions for one opportunity",
        "Primary success metric",
        "Two guardrail metrics",
        "One experiment",
        "One major trade-off",
        "One security or trust consideration",
        "One important limitation of the analysis",
    ],
}

print("\n--- Practice assignment ---")
print("Task:", practice_assignment["task"])
print("Choose one:")
for product_option in practice_assignment["select_one"]:
    print(" -", product_option)

print("Required analysis:")
for requirement in practice_assignment["required_analysis"]:
    print(" -", requirement)


# =============================================================================
# SECTION 61: SELF-ASSESSMENT RUBRIC
# =============================================================================

@dataclass
class RubricDimension:
    name: str
    description: str
    score: int


rubric = [
    RubricDimension(
        "Problem clarity",
        "Clearly identifies a meaningful user problem rather than a feature request.",
        4,
    ),
    RubricDimension(
        "User understanding",
        "Shows awareness of context, segmentation, motivation, and behavior.",
        4,
    ),
    RubricDimension(
        "Evidence",
        "Distinguishes facts from assumptions and identifies missing evidence.",
        3,
    ),
    RubricDimension(
        "Opportunity quality",
        "Connects product opportunities to meaningful customer outcomes.",
        4,
    ),
    RubricDimension(
        "Prioritization",
        "Considers impact, reach, confidence, effort, risk, and strategy.",
        4,
    ),
    RubricDimension(
        "Metrics",
        "Defines outcome metrics and guardrails rather than relying only on activity metrics.",
        4,
    ),
    RubricDimension(
        "Trade-offs",
        "Recognizes who benefits, who may be harmed, and what the business gives up.",
        3,
    ),
    RubricDimension(
        "Experimentation",
        "Converts uncertain assumptions into measurable tests.",
        4,
    ),
]

print("\n--- Self-assessment rubric ---")
rubric_average = mean(item.score for item in rubric)

for item in rubric:
    print(f"{item.name}: {item.score}/5")
    print("  ", item.description)

print(f"Average self-assessment score: {rubric_average:.2f}/5")


# =============================================================================
# SECTION 62: IMPORTANT DISTINCTIONS
# =============================================================================

distinctions = [
    (
        "User vs customer",
        "The user interacts with the product; the customer may be the person or organization paying for it."
    ),
    (
        "Problem vs solution",
        "A problem describes an unmet need or obstacle; a solution describes a possible intervention."
    ),
    (
        "Feature vs opportunity",
        "A feature is one implementation; an opportunity describes a broader area for improvement."
    ),
    (
        "Observation vs hypothesis",
        "An observation describes evidence; a hypothesis explains what may be causing it."
    ),
    (
        "Output vs outcome",
        "An output is something the team ships; an outcome is the change produced for users or the business."
    ),
    (
        "Correlation vs causation",
        "Two variables moving together does not establish that one caused the other."
    ),
    (
        "Activation vs acquisition",
        "Acquisition brings users into the product; activation indicates that users experience meaningful initial value."
    ),
    (
        "Retention vs frequency",
        "Frequency measures how often users act; retention measures whether users return over a defined period."
    ),
]

print("\n--- Important distinctions ---")
for distinction, explanation in distinctions:
    print(f"\n{distinction}")
    print(explanation)


# =============================================================================
# SECTION 63: SCRIPT COMPLETION
# =============================================================================

print("\n" + "=" * 80)
print("PRODUCT THINKING EXERCISES COMPLETE")
print("=" * 80)
print(
    "\nThe script demonstrated a complete product-thinking chain:"
    "\nProduct → User → Job → Problem → Evidence → Opportunity →"
    "\nHypothesis → Experiment → Metric → Learning → Decision"
)
