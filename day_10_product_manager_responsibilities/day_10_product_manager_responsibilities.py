"""
PRODUCT MANAGER RESPONSIBILITIES
================================

A comprehensive, executable study file covering Product Management
responsibilities from beginner to advanced level.

Main areas covered:
1. Product management fundamentals
2. Product strategy
3. Customer and problem discovery
4. Market and competitor analysis
5. Personas and jobs-to-be-done
6. Product vision and goals
7. Product metrics and OKRs
8. Prioritization frameworks
9. Requirements and PRDs
10. User stories and acceptance criteria
11. Roadmaps and release planning
12. Agile execution
13. Stakeholder communication
14. Product analytics
15. Experimentation and A/B testing
16. Launch management
17. Post-launch analysis
18. Risk management
19. Product quality and incident management
20. Product lifecycle management
21. Unit economics and business considerations
22. Technical collaboration
23. Product operations
24. Advanced product management concepts
25. Practical end-to-end product case study
26. Validation and testing of product-management artifacts

The examples use Python data structures, functions, classes, calculations,
simulations, validation, scoring models, and small analytical utilities.
No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from math import sqrt
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# =============================================================================
# 1. PRODUCT MANAGEMENT FUNDAMENTALS
# =============================================================================

print("=" * 80)
print("PRODUCT MANAGER RESPONSIBILITIES")
print("=" * 80)


class ProductStage(Enum):
    """Typical stages in a product lifecycle."""

    DISCOVERY = "Discovery"
    VALIDATION = "Validation"
    DEVELOPMENT = "Development"
    LAUNCH = "Launch"
    GROWTH = "Growth"
    MATURITY = "Maturity"
    DECLINE = "Decline"


class Priority(Enum):
    """Simple priority classification."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Product:
    """
    Represents a product at a high level.

    A product manager usually works across customer, business, technology,
    design, operations, marketing, sales, finance, and leadership concerns.
    """

    name: str
    target_customer: str
    problem: str
    value_proposition: str
    stage: ProductStage


product = Product(
    name="MarketX",
    target_customer="Beginner and intermediate retail investors",
    problem="Users need a safe environment to practice investment decisions.",
    value_proposition="Paper trading with portfolio analytics and risk insights.",
    stage=ProductStage.VALIDATION,
)

print("\nProduct definition:")
print(product)


# Product management is different from project management.
# Product management asks primarily:
# - What problem should be solved?
# - For whom?
# - Why should it be solved?
# - What outcome should the product create?
#
# Project management focuses more heavily on:
# - When will the work be completed?
# - Who is responsible for each activity?
# - What resources and dependencies affect delivery?
# - How should scope, schedule, and execution be controlled?
#
# Product and project management can overlap, but they are not interchangeable.


@dataclass
class ProductManagerResponsibility:
    """A responsibility map used throughout this study file."""

    area: str
    objective: str
    typical_outputs: List[str]


responsibilities = [
    ProductManagerResponsibility(
        "Strategy",
        "Determine where the product should compete and what outcomes matter.",
        ["Product strategy", "Vision", "Goals", "Strategic bets"],
    ),
    ProductManagerResponsibility(
        "Discovery",
        "Understand customers, problems, behaviors, and opportunities.",
        ["Interviews", "Personas", "JTBD", "Problem statements"],
    ),
    ProductManagerResponsibility(
        "Prioritization",
        "Choose which opportunities and product changes deserve investment.",
        ["Priority scores", "Roadmaps", "Trade-off decisions"],
    ),
    ProductManagerResponsibility(
        "Requirements",
        "Translate validated customer and business needs into buildable definitions.",
        ["PRDs", "User stories", "Acceptance criteria"],
    ),
    ProductManagerResponsibility(
        "Execution",
        "Coordinate product delivery across design, engineering, QA, and stakeholders.",
        ["Backlog", "Release plans", "Decision logs"],
    ),
    ProductManagerResponsibility(
        "Launch",
        "Prepare the product, organization, customers, and market for release.",
        ["Launch plan", "Go-to-market checklist", "Training"],
    ),
    ProductManagerResponsibility(
        "Analytics",
        "Measure whether product behavior and business outcomes are improving.",
        ["Metrics", "Funnels", "Experiments", "Dashboards"],
    ),
    ProductManagerResponsibility(
        "Communication",
        "Create alignment among stakeholders with different goals and perspectives.",
        ["Updates", "Presentations", "Decision records"],
    ),
]

print("\nCore responsibility areas:")
for responsibility in responsibilities:
    print(f"- {responsibility.area}: {responsibility.objective}")


# =============================================================================
# 2. PRODUCT STRATEGY
# =============================================================================

print("\n" + "=" * 80)
print("2. PRODUCT STRATEGY")
print("=" * 80)


@dataclass
class ProductVision:
    """
    A product vision describes the desired future state.

    A vision is intentionally broader than a feature list.
    """

    customer: str
    desired_change: str
    long_term_value: str

    def statement(self) -> str:
        return (
            f"For {self.customer}, we aim to create {self.desired_change}, "
            f"creating {self.long_term_value}."
        )


vision = ProductVision(
    customer="people learning investing",
    desired_change="a realistic and safe environment for investment practice",
    long_term_value="better decision-making without requiring real capital",
)

print("Vision:")
print(vision.statement())


@dataclass
class StrategicObjective:
    name: str
    metric: str
    baseline: float
    target: float
    deadline: str

    @property
    def required_improvement(self) -> float:
        if self.baseline == 0:
            return float("inf")
        return ((self.target - self.baseline) / self.baseline) * 100


objective = StrategicObjective(
    name="Improve activation",
    metric="Users completing first paper trade",
    baseline=35,
    target=55,
    deadline="Q4",
)

print(
    f"\nStrategic objective: {objective.name}\n"
    f"Metric: {objective.metric}\n"
    f"Required improvement: {objective.required_improvement:.1f}%"
)


# A useful strategy hierarchy:
#
# Vision
#   -> Product strategy
#       -> Strategic objectives
#           -> Product bets
#               -> Initiatives
#                   -> Features
#                       -> User stories
#                           -> Implementation tasks
#
# A common product-management mistake is starting at the bottom:
# "We need feature X."
#
# A stronger approach starts with:
# "What customer or business outcome requires us to consider feature X?"


@dataclass
class ProductBet:
    name: str
    customer_problem: str
    expected_outcome: str
    evidence_strength: int  # 1 to 5
    business_alignment: int  # 1 to 5
    feasibility: int  # 1 to 5


strategic_bet = ProductBet(
    name="Simplified onboarding",
    customer_problem="New users struggle to understand the first action.",
    expected_outcome="Increase first-session activation.",
    evidence_strength=4,
    business_alignment=5,
    feasibility=4,
)

print("\nStrategic product bet:")
print(strategic_bet)


# =============================================================================
# 3. PRODUCT DISCOVERY
# =============================================================================

print("\n" + "=" * 80)
print("3. PRODUCT DISCOVERY")
print("=" * 80)


# Discovery attempts to reduce uncertainty before significant investment.
#
# Important discovery questions:
# - Who has the problem?
# - How frequently does it occur?
# - How severe is it?
# - What does the customer do today?
# - What alternatives exist?
# - What triggers the problem?
# - What prevents the customer from solving it?
# - Would the customer change behavior?
# - Would the customer pay?
#
# Discovery should not be treated as simply "asking users what features they want."


@dataclass
class InterviewInsight:
    interviewee: str
    problem: str
    current_behavior: str
    pain_level: int  # 1 to 5
    frequency: int  # 1 to 5
    evidence_quote: str


interview_insights = [
    InterviewInsight(
        "User A",
        "Does not understand portfolio risk.",
        "Uses a spreadsheet after watching online tutorials.",
        5,
        4,
        "I can see profit, but I don't know how risky the portfolio is.",
    ),
    InterviewInsight(
        "User B",
        "Finds paper-trading interfaces complicated.",
        "Avoids advanced features.",
        4,
        5,
        "There are too many numbers before I can place a trade.",
    ),
    InterviewInsight(
        "User C",
        "Cannot understand whether practice improved decisions.",
        "Reviews trades manually.",
        3,
        3,
        "I want to know whether I am actually getting better.",
    ),
]


def average_pain(insights: Sequence[InterviewInsight]) -> float:
    """Calculate average reported pain across interviews."""
    return mean(item.pain_level for item in insights)


print(f"Average reported pain: {average_pain(interview_insights):.2f}/5")


# Customer discovery is stronger when qualitative evidence is combined
# with behavioral evidence. A customer saying "I like this" is weaker evidence
# than repeated behavior demonstrating that the feature solves a real problem.


# =============================================================================
# 4. PERSONAS
# =============================================================================

print("\n" + "=" * 80)
print("4. PERSONAS")
print("=" * 80)


@dataclass
class Persona:
    name: str
    role: str
    goals: List[str]
    frustrations: List[str]
    behaviors: List[str]
    context: str


persona = Persona(
    name="Practical Learner",
    role="New retail investor",
    goals=[
        "Understand basic investing",
        "Practice without financial loss",
        "Measure improvement",
    ],
    frustrations=[
        "Complex terminology",
        "Too many screens",
        "Unclear feedback",
    ],
    behaviors=[
        "Researches before trading",
        "Uses mobile frequently",
        "Reviews mistakes after trades",
    ],
    context="Learning investment concepts while working full-time.",
)

print(persona)


# Personas should represent meaningful behavioral differences.
# They should not become fictional biographies containing irrelevant details.


# =============================================================================
# 5. JOBS TO BE DONE
# =============================================================================

print("\n" + "=" * 80)
print("5. JOBS TO BE DONE")
print("=" * 80)


@dataclass
class JobToBeDone:
    situation: str
    motivation: str
    desired_outcome: str

    def statement(self) -> str:
        return (
            f"When {self.situation}, I want to {self.motivation}, "
            f"so that {self.desired_outcome}."
        )


job = JobToBeDone(
    situation="I am learning investing but do not want to risk real money",
    motivation="practice realistic portfolio decisions",
    desired_outcome="I can evaluate my decision-making safely",
)

print(job.statement())


# JTBD focuses on the progress a customer is trying to make.
# This helps prevent the team from defining the problem too narrowly
# around an existing product or feature.


# =============================================================================
# 6. PROBLEM STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("6. PROBLEM STATEMENTS")
print("=" * 80)


@dataclass
class ProblemStatement:
    user: str
    situation: str
    problem: str
    impact: str
    evidence: str

    def formatted(self) -> str:
        return (
            f"User: {self.user}\n"
            f"Situation: {self.situation}\n"
            f"Problem: {self.problem}\n"
            f"Impact: {self.impact}\n"
            f"Evidence: {self.evidence}"
        )


problem = ProblemStatement(
    user="beginner investors",
    situation="when reviewing their simulated trades",
    problem="they cannot easily understand the relationship between risk and return",
    impact="they have difficulty learning from their decisions",
    evidence="multiple interviews and repeated portfolio-review behavior",
)

print(problem.formatted())


# A strong problem statement describes the user's difficulty and its consequence.
# It should not prematurely prescribe a solution.


# =============================================================================
# 7. MARKET AND COMPETITOR ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("7. MARKET AND COMPETITOR ANALYSIS")
print("=" * 80)


@dataclass
class Competitor:
    name: str
    target_segment: str
    strengths: List[str]
    weaknesses: List[str]
    pricing_position: str


competitors = [
    Competitor(
        "Broker A",
        "Active retail investors",
        ["Large market coverage", "Fast execution"],
        ["Complex for beginners"],
        "Freemium",
    ),
    Competitor(
        "Broker B",
        "Long-term investors",
        ["Simple interface", "Educational content"],
        ["Limited simulation"],
        "Low cost",
    ),
]


def compare_competitors(items: Sequence[Competitor]) -> None:
    for item in items:
        print(f"\n{item.name}")
        print(f"Target: {item.target_segment}")
        print(f"Strengths: {', '.join(item.strengths)}")
        print(f"Weaknesses: {', '.join(item.weaknesses)}")
        print(f"Pricing: {item.pricing_position}")


compare_competitors(competitors)


# Competitive analysis should examine:
# - Customer segment
# - Core job
# - Product experience
# - Distribution
# - Pricing
# - Brand
# - Technology
# - Switching costs
# - Network effects
# - Regulatory constraints
# - Differentiation
#
# Competitors are not limited to companies selling the same software.
# A spreadsheet, manual process, internal workflow, or doing nothing
# can also be an alternative.


# =============================================================================
# 8. PRODUCT OPPORTUNITY ASSESSMENT
# =============================================================================

print("\n" + "=" * 80)
print("8. OPPORTUNITY ASSESSMENT")
print("=" * 80)


@dataclass
class Opportunity:
    name: str
    customer_reach: int
    problem_frequency: int
    problem_severity: int
    strategic_alignment: int
    confidence: int
    effort: int

    def opportunity_score(self) -> float:
        """
        A simple opportunity score.

        This is not a universal industry formula. Product teams should
        adapt scoring to their context and validate assumptions.
        """
        numerator = (
            self.customer_reach
            * self.problem_frequency
            * self.problem_severity
            * self.strategic_alignment
            * self.confidence
        )
        return numerator / max(self.effort, 1)


opportunities = [
    Opportunity("Risk explanation", 5, 4, 5, 5, 4, 4),
    Opportunity("Theme customization", 3, 3, 2, 2, 4, 3),
    Opportunity("Trade history export", 3, 4, 2, 3, 5, 2),
]

for opportunity in sorted(
    opportunities, key=lambda item: item.opportunity_score(), reverse=True
):
    print(
        f"{opportunity.name}: "
        f"{opportunity.opportunity_score():.2f}"
    )


# =============================================================================
# 9. PRIORITIZATION
# =============================================================================

print("\n" + "=" * 80)
print("9. PRIORITIZATION")
print("=" * 80)


# Prioritization is a decision-making activity under constraints.
#
# Constraints can include:
# - Engineering capacity
# - Design capacity
# - Budget
# - Time
# - Legal requirements
# - Security requirements
# - Dependencies
# - Strategic commitments
# - Operational capacity
#
# Prioritization is not simply "do the feature with the loudest stakeholder."


@dataclass
class Feature:
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float
    urgency: float = 1.0


def rice_score(feature: Feature) -> float:
    """
    RICE-style score:
        Reach * Impact * Confidence / Effort

    Reach can represent users affected during a defined period.
    Impact and confidence should use an explicitly documented scale.
    """
    return (
        feature.reach
        * feature.impact
        * feature.confidence
        * feature.urgency
        / max(feature.effort, 0.01)
    )


features = [
    Feature("Portfolio risk dashboard", 8000, 3, 0.85, 8, 1.0),
    Feature("Custom color themes", 4000, 0.5, 0.90, 3, 0.8),
    Feature("Trade journal", 6000, 2, 0.75, 5, 1.0),
    Feature("Keyboard shortcuts", 2000, 0.5, 0.95, 2, 0.7),
]

print("\nRICE-style prioritization:")
for feature in sorted(features, key=rice_score, reverse=True):
    print(f"{feature.name}: {rice_score(feature):.2f}")


def impact_effort_score(impact: int, effort: int) -> str:
    """
    Simple impact-versus-effort categorization.

    This resembles a 2x2 matrix:
    - High impact, low effort -> quick win
    - High impact, high effort -> strategic project
    - Low impact, low effort -> fill-in
    - Low impact, high effort -> deprioritize
    """
    if impact >= 4 and effort <= 2:
        return "Quick win"
    if impact >= 4 and effort > 2:
        return "Strategic project"
    if impact < 4 and effort <= 2:
        return "Fill-in"
    return "Deprioritize"


print("\nImpact versus effort:")
examples = [(5, 1), (5, 5), (2, 1), (2, 5)]
for impact, effort in examples:
    print(
        f"Impact={impact}, Effort={effort}: "
        f"{impact_effort_score(impact, effort)}"
    )


# Other prioritization frameworks include:
# - MoSCoW
# - Kano
# - Value versus effort
# - Opportunity scoring
# - WSJF
# - Cost of delay
# - Strategic alignment
# - Risk reduction
# - Regulatory necessity
#
# No framework removes judgment.
# A prioritization model makes assumptions visible and comparable.


# =============================================================================
# 10. WSJF
# =============================================================================

print("\n" + "=" * 80)
print("10. WSJF")
print("=" * 80)


@dataclass
class WSJFItem:
    name: str
    user_business_value: float
    time_criticality: float
    risk_reduction: float
    job_size: float

    def wsjf(self) -> float:
        cost_of_delay = (
            self.user_business_value
            + self.time_criticality
            + self.risk_reduction
        )
        return cost_of_delay / max(self.job_size, 0.01)


wsjf_items = [
    WSJFItem("Compliance reporting", 8, 10, 10, 5),
    WSJFItem("Dashboard redesign", 7, 5, 3, 8),
    WSJFItem("New visual theme", 3, 2, 1, 3),
]

for item in sorted(wsjf_items, key=lambda item: item.wsjf(), reverse=True):
    print(f"{item.name}: WSJF={item.wsjf():.2f}")


# =============================================================================
# 11. MOSCOW PRIORITIZATION
# =============================================================================

print("\n" + "=" * 80)
print("11. MOSCOW PRIORITIZATION")
print("=" * 80)


moscow = {
    "Must have": [
        "User authentication",
        "Order validation",
        "Portfolio calculation",
    ],
    "Should have": [
        "Trade history filters",
        "Performance charts",
    ],
    "Could have": [
        "Theme customization",
        "Additional visualizations",
    ],
    "Won't have now": [
        "Social trading",
        "Gamification",
    ],
}

for category, items in moscow.items():
    print(f"\n{category}:")
    for item in items:
        print(f"  - {item}")


# =============================================================================
# 12. PRODUCT REQUIREMENTS
# =============================================================================

print("\n" + "=" * 80)
print("12. PRODUCT REQUIREMENTS")
print("=" * 80)


@dataclass
class Requirement:
    id: str
    title: str
    description: str
    rationale: str
    priority: Priority
    dependencies: List[str] = field(default_factory=list)
    non_functional: bool = False


requirements = [
    Requirement(
        "REQ-001",
        "Display portfolio value",
        "The system shall display current portfolio value.",
        "Users need to understand current portfolio status.",
        Priority.CRITICAL,
    ),
    Requirement(
        "REQ-002",
        "Validate order quantity",
        "The system shall reject invalid quantities.",
        "Invalid orders could create incorrect portfolio states.",
        Priority.CRITICAL,
        non_functional=False,
    ),
    Requirement(
        "REQ-003",
        "Response time",
        "The portfolio screen should load within the defined performance target.",
        "Slow experiences reduce usability.",
        Priority.HIGH,
        non_functional=True,
    ),
]

for requirement in requirements:
    print(
        f"{requirement.id}: {requirement.title} "
        f"({requirement.priority.value})"
    )


# Functional requirements describe behavior.
# Non-functional requirements describe qualities or constraints such as:
# - Performance
# - Reliability
# - Security
# - Accessibility
# - Scalability
# - Observability
# - Availability
#
# A good product manager makes important requirements measurable where possible.


# =============================================================================
# 13. PRODUCT REQUIREMENTS DOCUMENT
# =============================================================================

print("\n" + "=" * 80)
print("13. PRODUCT REQUIREMENTS DOCUMENT")
print("=" * 80)


@dataclass
class PRD:
    title: str
    problem: str
    objective: str
    target_users: List[str]
    scope_in: List[str]
    scope_out: List[str]
    requirements: List[Requirement]
    success_metrics: Dict[str, str]
    assumptions: List[str]
    risks: List[str]

    def validate(self) -> List[str]:
        """Identify common PRD quality problems."""
        issues = []

        if not self.problem.strip():
            issues.append("Problem statement is missing.")

        if not self.objective.strip():
            issues.append("Objective is missing.")

        if not self.target_users:
            issues.append("Target users are missing.")

        if not self.success_metrics:
            issues.append("Success metrics are missing.")

        if not self.scope_in:
            issues.append("In-scope definition is missing.")

        for requirement in self.requirements:
            if not requirement.description.strip():
                issues.append(
                    f"{requirement.id} has no requirement description."
                )

        return issues


prd = PRD(
    title="Portfolio Risk Dashboard",
    problem=(
        "Users can see profit and loss but cannot easily understand "
        "portfolio risk."
    ),
    objective="Help users interpret risk while reviewing their portfolio.",
    target_users=["Beginner investors", "Intermediate investors"],
    scope_in=[
        "Risk score",
        "Portfolio volatility",
        "Diversification view",
        "Plain-language explanations",
    ],
    scope_out=[
        "Personalized financial advice",
        "Automated real-money trading",
    ],
    requirements=[
        Requirement(
            "REQ-RISK-001",
            "Risk score",
            "Display a portfolio risk score using documented methodology.",
            "Users need a concise risk indicator.",
            Priority.HIGH,
        )
    ],
    success_metrics={
        "Risk dashboard adoption": "At least 30% of active users view it monthly.",
        "Interpretation rate": "At least 60% answer an interpretation task correctly.",
    },
    assumptions=[
        "Users understand basic portfolio concepts.",
        "Required market data is available.",
    ],
    risks=[
        "Users may interpret the score as financial advice.",
        "Risk methodology may be misunderstood.",
    ],
)

print(f"PRD validation issues: {prd.validate()}")


# =============================================================================
# 14. USER STORIES
# =============================================================================

print("\n" + "=" * 80)
print("14. USER STORIES")
print("=" * 80)


@dataclass
class UserStory:
    id: str
    role: str
    action: str
    benefit: str

    def format(self) -> str:
        return (
            f"As a {self.role}, I want to {self.action}, "
            f"so that {self.benefit}."
        )


story = UserStory(
    "US-001",
    "portfolio learner",
    "see a simple risk indicator",
    "I can quickly understand whether my portfolio is concentrated",
)

print(story.format())


# User stories are intentionally focused on user value.
# They should not become implementation instructions such as:
# "Create a SQL table with three columns."
#
# Implementation details can be defined collaboratively with engineering
# after the user and product requirements are clear.


# =============================================================================
# 15. ACCEPTANCE CRITERIA
# =============================================================================

print("\n" + "=" * 80)
print("15. ACCEPTANCE CRITERIA")
print("=" * 80)


@dataclass
class AcceptanceCriterion:
    given: str
    when: str
    then: str

    def format(self) -> str:
        return f"Given {self.given}, when {self.when}, then {self.then}."


acceptance_criteria = [
    AcceptanceCriterion(
        "the user has a portfolio",
        "the risk dashboard opens",
        "a risk score is displayed",
    ),
    AcceptanceCriterion(
        "the portfolio contains only one asset",
        "diversification is calculated",
        "the concentration is identified correctly",
    ),
    AcceptanceCriterion(
        "required market data is unavailable",
        "the user opens the dashboard",
        "the interface communicates that the calculation cannot be completed",
    ),
]

for criterion in acceptance_criteria:
    print("-", criterion.format())


# Acceptance criteria define observable behavior.
# Strong criteria are:
# - Specific
# - Testable
# - Unambiguous
# - Relevant to the requirement
#
# They are not the same as a complete QA test plan.


# =============================================================================
# 16. EDGE CASES AND EXCEPTIONS IN REQUIREMENTS
# =============================================================================

print("\n" + "=" * 80)
print("16. EDGE CASES")
print("=" * 80)


def calculate_concentration(weights: Sequence[float]) -> float:
    """
    Calculate the largest portfolio weight.

    Edge cases:
    - Empty portfolio -> 0
    - Negative weights -> invalid
    - Weights greater than 1 -> invalid for this simplified model
    """
    if not weights:
        return 0.0

    if any(weight < 0 for weight in weights):
        raise ValueError("Portfolio weights cannot be negative.")

    if any(weight > 1 for weight in weights):
        raise ValueError("Each portfolio weight must be <= 1.")

    return max(weights)


test_weights = [
    [0.50, 0.30, 0.20],
    [1.00],
    [],
]

for weights in test_weights:
    print(f"Weights={weights}, concentration={calculate_concentration(weights)}")

try:
    calculate_concentration([0.50, -0.20, 0.70])
except ValueError as error:
    print(f"Handled invalid input: {error}")


# Product managers should actively ask:
# "What happens if this is empty?"
# "What happens if the user enters zero?"
# "What happens if data is missing?"
# "What happens if the user repeats the action?"
# "What happens if two users change the same thing?"
# "What happens if the network fails?"
# "What happens if permissions are insufficient?"
# "What happens if the underlying assumption changes?"


# =============================================================================
# 17. ROADMAPS
# =============================================================================

print("\n" + "=" * 80)
print("17. ROADMAPS")
print("=" * 80)


@dataclass
class RoadmapItem:
    name: str
    outcome: str
    quarter: str
    confidence: str


roadmap = [
    RoadmapItem(
        "Onboarding redesign",
        "Increase activation",
        "Q1",
        "High",
    ),
    RoadmapItem(
        "Risk dashboard",
        "Improve portfolio understanding",
        "Q2",
        "Medium",
    ),
    RoadmapItem(
        "Advanced analytics",
        "Increase retention among experienced users",
        "Q3",
        "Medium",
    ),
]

for item in roadmap:
    print(
        f"{item.quarter}: {item.name} -> "
        f"{item.outcome} [{item.confidence} confidence]"
    )


# A roadmap should communicate direction and intended outcomes.
# It should not become a promise that every date and feature is fixed forever.
#
# Roadmap formats may include:
# - Theme-based roadmaps
# - Outcome-based roadmaps
# - Now / Next / Later
# - Quarterly roadmaps
# - Capability roadmaps
#
# The right format depends on the audience and organizational context.


# =============================================================================
# 18. OKRs
# =============================================================================

print("\n" + "=" * 80)
print("18. OKRs")
print("=" * 80)


@dataclass
class KeyResult:
    description: str
    baseline: float
    target: float
    current: float

    def completion_percentage(self) -> float:
        denominator = self.target - self.baseline
        if denominator == 0:
            return 100.0 if self.current == self.target else 0.0

        raw = ((self.current - self.baseline) / denominator) * 100
        return max(0.0, min(100.0, raw))


@dataclass
class Objective:
    title: str
    key_results: List[KeyResult]

    def completion(self) -> float:
        if not self.key_results:
            return 0.0
        return mean(
            result.completion_percentage()
            for result in self.key_results
        )


okr = Objective(
    title="Make first-time product activation easier",
    key_results=[
        KeyResult(
            "First-trade completion rate",
            baseline=35,
            target=60,
            current=52,
        ),
        KeyResult(
            "Onboarding completion rate",
            baseline=45,
            target=75,
            current=68,
        ),
    ],
)

print(f"Objective: {okr.title}")
for key_result in okr.key_results:
    print(
        f"- {key_result.description}: "
        f"{key_result.completion_percentage():.1f}% complete"
    )
print(f"Objective completion: {okr.completion():.1f}%")


# OKRs distinguish an objective from measurable results.
# A feature list such as "launch dashboard" is not itself a strong outcome.
# A stronger key result might be a change in customer behavior or business performance.


# =============================================================================
# 19. AGILE EXECUTION
# =============================================================================

print("\n" + "=" * 80)
print("19. AGILE EXECUTION")
print("=" * 80)


@dataclass
class BacklogItem:
    id: str
    title: str
    status: str
    priority: Priority
    estimate_points: int
    owner: str


backlog = [
    BacklogItem(
        "B-001",
        "Create portfolio API",
        "Ready",
        Priority.CRITICAL,
        8,
        "Engineering",
    ),
    BacklogItem(
        "B-002",
        "Design risk card",
        "In progress",
        Priority.HIGH,
        3,
        "Design",
    ),
    BacklogItem(
        "B-003",
        "Write analytics events",
        "Ready",
        Priority.HIGH,
        5,
        "Engineering",
    ),
]

for item in backlog:
    print(
        f"{item.id} | {item.title} | {item.status} | "
        f"{item.priority.value} | {item.estimate_points} points"
    )


# Product managers often work with agile teams, but terminology and role
# boundaries vary by organization.
#
# Typical concepts:
# - Product backlog
# - Sprint
# - Sprint planning
# - Daily coordination
# - Review/demo
# - Retrospective
# - Refinement
# - Definition of Done
# - Release
#
# The product manager's exact role can differ from a Product Owner role.
# Some organizations combine them, while others separate responsibilities.


# =============================================================================
# 20. EXECUTION MANAGEMENT
# =============================================================================

print("\n" + "=" * 80)
print("20. EXECUTION MANAGEMENT")
print("=" * 80)


@dataclass
class Dependency:
    item: str
    depends_on: str
    reason: str
    risk_level: str


dependencies = [
    Dependency(
        "Risk dashboard",
        "Portfolio API",
        "Dashboard requires portfolio calculations.",
        "High",
    ),
    Dependency(
        "Analytics dashboard",
        "Event tracking",
        "Analytics requires event instrumentation.",
        "Medium",
    ),
]

for dependency in dependencies:
    print(
        f"{dependency.item} depends on {dependency.depends_on}: "
        f"{dependency.reason} Risk={dependency.risk_level}"
    )


@dataclass
class Decision:
    question: str
    decision: str
    rationale: str
    owner: str
    date_recorded: str


decision = Decision(
    question="Should risk score be shown before or after portfolio return?",
    decision="Show risk beside return.",
    rationale="Users need both dimensions to interpret performance.",
    owner="Product Manager",
    date_recorded="2026-09-10",
)

print("\nDecision record:")
print(decision)


# Decision logs reduce repeated debates.
# A useful decision record captures:
# - Decision
# - Context
# - Alternatives
# - Rationale
# - Owner
# - Date
# - Reversal conditions, when relevant


# =============================================================================
# 21. STAKEHOLDER MANAGEMENT
# =============================================================================

print("\n" + "=" * 80)
print("21. STAKEHOLDER MANAGEMENT")
print("=" * 80)


@dataclass
class Stakeholder:
    name: str
    function: str
    influence: int
    interest: int
    concern: str


stakeholders = [
    Stakeholder(
        "Engineering Lead",
        "Engineering",
        5,
        5,
        "Technical feasibility and capacity",
    ),
    Stakeholder(
        "Marketing Lead",
        "Marketing",
        4,
        4,
        "Positioning and launch readiness",
    ),
    Stakeholder(
        "Finance Lead",
        "Finance",
        4,
        3,
        "Revenue and cost impact",
    ),
    Stakeholder(
        "Customer Support Lead",
        "Operations",
        3,
        5,
        "Support volume and customer confusion",
    ),
]


def stakeholder_priority(stakeholder: Stakeholder) -> int:
    return stakeholder.influence * stakeholder.interest


for stakeholder in sorted(
    stakeholders,
    key=stakeholder_priority,
    reverse=True,
):
    print(
        f"{stakeholder.name} ({stakeholder.function}) -> "
        f"engagement score {stakeholder_priority(stakeholder)}"
    )


# Stakeholder management is not about satisfying everyone.
# It is about understanding:
# - Who decides?
# - Who is affected?
# - Who provides expertise?
# - Who can block progress?
# - Who needs information?
#
# Product managers often have influence without direct authority.
# Evidence, clarity, trust, and consistent decision-making therefore matter.


# =============================================================================
# 22. COMMUNICATION
# =============================================================================

print("\n" + "=" * 80)
print("22. PRODUCT COMMUNICATION")
print("=" * 80)


@dataclass
class ProductUpdate:
    period: str
    progress: List[str]
    metrics: Dict[str, str]
    risks: List[str]
    decisions_needed: List[str]

    def formatted(self) -> str:
        lines = [f"Product update: {self.period}", "", "Progress:"]
        lines.extend(f"- {item}" for item in self.progress)

        lines.append("\nMetrics:")
        lines.extend(f"- {key}: {value}" for key, value in self.metrics.items())

        lines.append("\nRisks:")
        lines.extend(f"- {risk}" for risk in self.risks)

        lines.append("\nDecisions needed:")
        lines.extend(f"- {decision}" for decision in self.decisions_needed)

        return "\n".join(lines)


update = ProductUpdate(
    period="Week 4",
    progress=[
        "Risk calculation completed",
        "Design prototype tested with five users",
    ],
    metrics={
        "Prototype comprehension": "4/5 users understood the indicator",
        "Engineering completion": "70%",
    },
    risks=[
        "Market data dependency remains unresolved",
    ],
    decisions_needed=[
        "Approve risk-score methodology",
    ],
)

print(update.formatted())


# Effective product communication should answer:
# - What happened?
# - Why does it matter?
# - What evidence exists?
# - What changed?
# - What is at risk?
# - What decision is required?
#
# Different audiences require different levels of detail.


# =============================================================================
# 23. PRODUCT METRICS
# =============================================================================

print("\n" + "=" * 80)
print("23. PRODUCT METRICS")
print("=" * 80)


# Metrics should be tied to a product question.
#
# Common categories:
# - Acquisition
# - Activation
# - Engagement
# - Retention
# - Revenue
# - Referral
# - Quality
# - Reliability
# - Customer satisfaction
#
# A metric without context can be misleading.


@dataclass
class ProductMetrics:
    visitors: int
    signups: int
    activated_users: int
    retained_users: int
    paying_users: int
    revenue: float

    def signup_conversion(self) -> float:
        return safe_rate(self.signups, self.visitors)

    def activation_rate(self) -> float:
        return safe_rate(self.activated_users, self.signups)

    def retention_rate(self) -> float:
        return safe_rate(self.retained_users, self.activated_users)

    def payer_conversion(self) -> float:
        return safe_rate(self.paying_users, self.activated_users)


def safe_rate(numerator: float, denominator: float) -> float:
    """Return a percentage while safely handling zero denominators."""
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100


metrics = ProductMetrics(
    visitors=10000,
    signups=1200,
    activated_users=720,
    retained_users=360,
    paying_users=180,
    revenue=450000,
)

print(f"Signup conversion: {metrics.signup_conversion():.1f}%")
print(f"Activation rate: {metrics.activation_rate():.1f}%")
print(f"Retention rate: {metrics.retention_rate():.1f}%")
print(f"Payer conversion: {metrics.payer_conversion():.1f}%")


# =============================================================================
# 24. FUNNEL ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("24. FUNNEL ANALYSIS")
print("=" * 80)


@dataclass
class FunnelStep:
    name: str
    users: int


funnel = [
    FunnelStep("Visited landing page", 10000),
    FunnelStep("Created account", 4000),
    FunnelStep("Completed onboarding", 2500),
    FunnelStep("First trade", 1500),
    FunnelStep("Second trade", 900),
]


def analyze_funnel(steps: Sequence[FunnelStep]) -> None:
    if not steps:
        return

    initial = steps[0].users

    for index, step in enumerate(steps):
        total_conversion = safe_rate(step.users, initial)

        if index == 0:
            step_conversion = 100.0
        else:
            previous = steps[index - 1].users
            step_conversion = safe_rate(step.users, previous)

        print(
            f"{step.name}: users={step.users}, "
            f"step conversion={step_conversion:.1f}%, "
            f"overall conversion={total_conversion:.1f}%"
        )


analyze_funnel(funnel)


# Funnel analysis helps identify where user progression weakens.
# It does not automatically explain why the drop happens.
# Quantitative analysis should often be followed by qualitative discovery.


# =============================================================================
# 25. RETENTION
# =============================================================================

print("\n" + "=" * 80)
print("25. RETENTION")
print("=" * 80)


def cohort_retention(
    starting_users: int,
    active_users_by_period: Sequence[int],
) -> List[float]:
    """
    Calculate retention percentages for a cohort.

    Example:
    starting_users=1000
    active_users_by_period=[1000, 600, 450]
    returns [100%, 60%, 45%]
    """
    if starting_users <= 0:
        return [0.0 for _ in active_users_by_period]

    return [
        safe_rate(active_users, starting_users)
        for active_users in active_users_by_period
    ]


retention = cohort_retention(1000, [1000, 650, 500, 420, 380])
print("Cohort retention:", [f"{value:.1f}%" for value in retention])


# Retention can be analyzed by:
# - Signup cohort
# - Geography
# - Acquisition source
# - Product version
# - User segment
# - Feature adoption
#
# Cohort analysis is generally more informative than looking only at a
# single aggregate retention number.


# =============================================================================
# 26. NORTH STAR METRIC
# =============================================================================

print("\n" + "=" * 80)
print("26. NORTH STAR METRIC")
print("=" * 80)


@dataclass
class NorthStarMetric:
    name: str
    definition: str
    customer_value_relationship: str
    guardrails: List[str]


north_star = NorthStarMetric(
    name="Meaningful learning sessions",
    definition="Sessions where a user completes a practice decision and reviews the outcome.",
    customer_value_relationship="Measures repeated product behavior associated with learning.",
    guardrails=[
        "Support ticket rate",
        "Data quality",
        "User satisfaction",
    ],
)

print(north_star)


# A North Star Metric should connect product activity to customer value.
# It should not be selected merely because it is easy to increase.
#
# Guardrail metrics protect against optimization that improves one metric
# while damaging another important outcome.


# =============================================================================
# 27. PRODUCT ANALYTICS EVENTS
# =============================================================================

print("\n" + "=" * 80)
print("27. EVENT INSTRUMENTATION")
print("=" * 80)


@dataclass
class AnalyticsEvent:
    event_name: str
    user_id: str
    timestamp: str
    properties: Dict[str, str]


events = [
    AnalyticsEvent(
        "onboarding_completed",
        "U001",
        "2026-09-10T09:00:00",
        {"source": "organic"},
    ),
    AnalyticsEvent(
        "trade_placed",
        "U001",
        "2026-09-10T09:05:00",
        {"asset": "NIFTY", "side": "BUY"},
    ),
]


def count_events(
    event_list: Sequence[AnalyticsEvent],
    event_name: str,
) -> int:
    return sum(event.event_name == event_name for event in event_list)


print("Trade events:", count_events(events, "trade_placed"))


# Event names should be:
# - Consistent
# - Clearly defined
# - Stable enough for analysis
# - Accompanied by documented properties
#
# Poor instrumentation creates poor analytics regardless of how advanced
# the dashboard is.


# =============================================================================
# 28. EXPERIMENTATION AND A/B TESTING
# =============================================================================

print("\n" + "=" * 80)
print("28. EXPERIMENTATION")
print("=" * 80)


@dataclass
class ExperimentGroup:
    name: str
    users: int
    conversions: int

    @property
    def conversion_rate(self) -> float:
        return safe_rate(self.conversions, self.users)


control = ExperimentGroup("Control", 1000, 120)
variant = ExperimentGroup("Variant", 1000, 150)

print(
    f"Control conversion: {control.conversion_rate:.2f}%\n"
    f"Variant conversion: {variant.conversion_rate:.2f}%"
)


def relative_lift(
    control_rate: float,
    variant_rate: float,
) -> float:
    if control_rate == 0:
        return float("inf") if variant_rate > 0 else 0.0
    return ((variant_rate - control_rate) / control_rate) * 100


print(
    f"Observed relative lift: "
    f"{relative_lift(control.conversion_rate, variant.conversion_rate):.2f}%"
)


def pooled_standard_error(
    control_users: int,
    control_rate: float,
    variant_users: int,
    variant_rate: float,
) -> float:
    """
    Approximate standard error for difference in two proportions.

    Rates are expected as decimals, not percentages.
    """
    if control_users <= 0 or variant_users <= 0:
        raise ValueError("Group sizes must be positive.")

    return sqrt(
        (
            control_rate * (1 - control_rate) / control_users
        )
        + (
            variant_rate * (1 - variant_rate) / variant_users
        )
    )


control_rate_decimal = control.conversion_rate / 100
variant_rate_decimal = variant.conversion_rate / 100

standard_error = pooled_standard_error(
    control.users,
    control_rate_decimal,
    variant.users,
    variant_rate_decimal,
)

z_score = (
    variant_rate_decimal - control_rate_decimal
) / standard_error

print(f"Approximate z-score: {z_score:.3f}")


# Product experimentation requires more than observing which percentage is larger.
#
# Important considerations:
# - Randomization
# - Sample size
# - Primary metric
# - Guardrail metrics
# - Experiment duration
# - Statistical uncertainty
# - Multiple comparisons
# - Seasonality
# - Novelty effects
# - Sample-ratio mismatch
# - Segmentation
#
# A statistically significant result can still be strategically unimportant.
# A strategically important effect can be difficult to detect with insufficient data.


# =============================================================================
# 29. BASIC SAMPLE SIZE INTUITION
# =============================================================================

print("\n" + "=" * 80)
print("29. EXPERIMENT SAMPLE SIZE INTUITION")
print("=" * 80)


def approximate_proportion_sample_size(
    baseline_rate: float,
    minimum_detectable_effect: float,
    z_alpha: float = 1.96,
    z_power: float = 0.84,
) -> int:
    """
    Rough per-group sample-size approximation.

    This is intentionally educational, not a replacement for a full
    experimental design calculation.

    baseline_rate:
        Expected baseline conversion as a decimal.

    minimum_detectable_effect:
        Absolute change as a decimal.
    """
    if not 0 < baseline_rate < 1:
        raise ValueError("Baseline rate must be between 0 and 1.")

    if minimum_detectable_effect <= 0:
        raise ValueError("Minimum detectable effect must be positive.")

    variance = baseline_rate * (1 - baseline_rate)
    numerator = (
        (z_alpha * sqrt(2 * variance))
        + (z_power * sqrt(variance))
    ) ** 2

    sample_size = numerator / (minimum_detectable_effect ** 2)
    return int(sample_size) + 1


sample_size = approximate_proportion_sample_size(
    baseline_rate=0.12,
    minimum_detectable_effect=0.02,
)

print(f"Approximate sample size per group: {sample_size}")


# =============================================================================
# 30. PRODUCT LAUNCH
# =============================================================================

print("\n" + "=" * 80)
print("30. PRODUCT LAUNCH")
print("=" * 80)


@dataclass
class LaunchChecklist:
    product_ready: bool
    qa_complete: bool
    analytics_ready: bool
    support_ready: bool
    documentation_ready: bool
    marketing_ready: bool
    legal_ready: bool
    rollback_ready: bool

    def is_launch_ready(self) -> bool:
        return all(
            [
                self.product_ready,
                self.qa_complete,
                self.analytics_ready,
                self.support_ready,
                self.documentation_ready,
                self.marketing_ready,
                self.legal_ready,
                self.rollback_ready,
            ]
        )


launch = LaunchChecklist(
    product_ready=True,
    qa_complete=True,
    analytics_ready=True,
    support_ready=True,
    documentation_ready=True,
    marketing_ready=False,
    legal_ready=True,
    rollback_ready=True,
)

print("Launch ready:", launch.is_launch_ready())


# Launch readiness commonly spans:
# Product
# Engineering
# QA
# Analytics
# Security
# Legal/compliance
# Customer support
# Sales
# Marketing
# Documentation
# Operations
#
# A launch is not complete merely because engineering says the code is done.


# =============================================================================
# 31. GO-TO-MARKET
# =============================================================================

print("\n" + "=" * 80)
print("31. GO-TO-MARKET")
print("=" * 80)


@dataclass
class GTMPlan:
    target_segment: str
    positioning: str
    core_message: str
    channels: List[str]
    pricing: str
    sales_enablement: List[str]
    support_enablement: List[str]


gtm = GTMPlan(
    target_segment="Learners seeking safe investment practice",
    positioning="A realistic practice environment rather than a real-money broker.",
    core_message="Practice decisions, review outcomes, improve your process.",
    channels=["Organic search", "Educational communities", "Partnerships"],
    pricing="Freemium",
    sales_enablement=["Product demo", "FAQ", "Feature comparison"],
    support_enablement=["Knowledge base", "Troubleshooting guide"],
)

print(gtm)


# Product managers may own GTM directly or coordinate with marketing,
# sales, growth, and operations depending on the organization.


# =============================================================================
# 32. LAUNCH PHASING
# =============================================================================

print("\n" + "=" * 80)
print("32. PHASED RELEASE")
print("=" * 80)


class ReleaseType(Enum):
    INTERNAL = "Internal"
    ALPHA = "Alpha"
    BETA = "Beta"
    PILOT = "Pilot"
    GENERAL_AVAILABILITY = "General Availability"


@dataclass
class Release:
    version: str
    release_type: ReleaseType
    percentage_users: float
    rollback_plan: str


releases = [
    Release("1.0", ReleaseType.INTERNAL, 0, "Disable feature flag."),
    Release("1.1", ReleaseType.BETA, 10, "Rollback to previous version."),
    Release("1.2", ReleaseType.GENERAL_AVAILABILITY, 100, "Standard rollback."),
]

for release in releases:
    print(
        f"{release.version}: {release.release_type.value}, "
        f"{release.percentage_users}% users"
    )


# Feature flags and phased releases can reduce launch risk.
# They can also create operational complexity and technical debt if flags
# are never removed or their states are poorly documented.


# =============================================================================
# 33. POST-LAUNCH ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("33. POST-LAUNCH ANALYSIS")
print("=" * 80)


@dataclass
class LaunchResult:
    metric: str
    target: float
    actual: float
    unit: str

    @property
    def achievement(self) -> float:
        if self.target == 0:
            return 0.0
        return (self.actual / self.target) * 100


launch_results = [
    LaunchResult("Activation", 50, 57, "%"),
    LaunchResult("Feature adoption", 30, 24, "%"),
    LaunchResult("Crash rate", 1.0, 0.4, "%"),
]

for result in launch_results:
    print(
        f"{result.metric}: target={result.target}{result.unit}, "
        f"actual={result.actual}{result.unit}, "
        f"achievement={result.achievement:.1f}%"
    )


# Post-launch questions:
# - Did customers use it?
# - Did behavior change?
# - Did the target outcome improve?
# - Did guardrail metrics worsen?
# - Which customer segments benefited?
# - Which did not?
# - What unexpected behavior appeared?
# - Was the original problem actually solved?
# - What should be improved, expanded, or removed?


# =============================================================================
# 34. PRODUCT QUALITY
# =============================================================================

print("\n" + "=" * 80)
print("34. PRODUCT QUALITY")
print("=" * 80)


@dataclass
class QualityIncident:
    severity: str
    description: str
    affected_users: int
    detected_at: str
    status: str


incident = QualityIncident(
    severity="High",
    description="Portfolio values were stale for some users.",
    affected_users=125,
    detected_at="2026-09-10 08:30",
    status="Investigating",
)

print(incident)


# Product managers may participate in incident management by:
# - Understanding customer impact
# - Establishing severity
# - Coordinating communication
# - Aligning on mitigation
# - Tracking recovery
# - Ensuring follow-up actions
#
# Engineering owns technical diagnosis and remediation details,
# while the exact responsibility split depends on the organization.


# =============================================================================
# 35. RISK MANAGEMENT
# =============================================================================

print("\n" + "=" * 80)
print("35. RISK MANAGEMENT")
print("=" * 80)


@dataclass
class ProductRisk:
    name: str
    probability: int  # 1-5
    impact: int  # 1-5
    mitigation: str

    @property
    def risk_score(self) -> int:
        return self.probability * self.impact


risks = [
    ProductRisk(
        "Incorrect portfolio calculation",
        2,
        5,
        "Automated tests and reconciliation.",
    ),
    ProductRisk(
        "User misunderstanding",
        4,
        4,
        "Plain-language explanations and usability testing.",
    ),
    ProductRisk(
        "Data provider outage",
        3,
        4,
        "Fallback handling and stale-data messaging.",
    ),
]

for risk in sorted(risks, key=lambda item: item.risk_score, reverse=True):
    print(
        f"{risk.name}: score={risk.risk_score}, "
        f"mitigation={risk.mitigation}"
    )


# Common product risk categories:
# - Desirability risk
# - Viability risk
# - Feasibility risk
# - Usability risk
# - Operational risk
# - Security risk
# - Privacy risk
# - Compliance risk
# - Data risk
# - Delivery risk
# - Reputation risk


# =============================================================================
# 36. BUSINESS MODEL AND UNIT ECONOMICS
# =============================================================================

print("\n" + "=" * 80)
print("36. BUSINESS MODEL AND UNIT ECONOMICS")
print("=" * 80)


@dataclass
class UnitEconomics:
    average_revenue_per_customer: float
    variable_cost_per_customer: float
    acquisition_cost: float
    average_lifetime_months: float

    @property
    def contribution_margin(self) -> float:
        return (
            self.average_revenue_per_customer
            - self.variable_cost_per_customer
        )

    @property
    def lifetime_value(self) -> float:
        return (
            self.contribution_margin
            * self.average_lifetime_months
        )

    @property
    def ltv_to_cac(self) -> float:
        if self.acquisition_cost == 0:
            return float("inf")
        return self.lifetime_value / self.acquisition_cost


economics = UnitEconomics(
    average_revenue_per_customer=500,
    variable_cost_per_customer=120,
    acquisition_cost=1500,
    average_lifetime_months=24,
)

print(f"Contribution margin: ₹{economics.contribution_margin:.2f}")
print(f"Estimated LTV: ₹{economics.lifetime_value:.2f}")
print(f"LTV:CAC: {economics.ltv_to_cac:.2f}")


# Product managers do not always own financial modeling, but product decisions
# should understand economic consequences.
#
# Useful concepts:
# - Revenue
# - Gross margin
# - Contribution margin
# - CAC
# - LTV
# - ARPU
# - Conversion
# - Churn
# - Payback period
# - Fixed cost
# - Variable cost


# =============================================================================
# 37. PRICING
# =============================================================================

print("\n" + "=" * 80)
print("37. PRICING")
print("=" * 80)


@dataclass
class PricingScenario:
    customers: int
    price: float
    conversion_rate: float

    @property
    def expected_customers(self) -> float:
        return self.customers * self.conversion_rate

    @property
    def expected_revenue(self) -> float:
        return self.expected_customers * self.price


pricing_scenarios = [
    PricingScenario(10000, 199, 0.05),
    PricingScenario(10000, 299, 0.04),
    PricingScenario(10000, 499, 0.025),
]

for scenario in pricing_scenarios:
    print(
        f"Price ₹{scenario.price:.0f}: "
        f"expected revenue ₹{scenario.expected_revenue:,.2f}"
    )


# Pricing is not merely a mathematical optimization problem.
# Product managers should consider:
# - Customer willingness to pay
# - Perceived value
# - Competitive alternatives
# - Segmentation
# - Price sensitivity
# - Packaging
# - Costs
# - Strategic positioning
# - Cannibalization
# - Taxes and regional differences


# =============================================================================
# 38. CUSTOMER SATISFACTION
# =============================================================================

print("\n" + "=" * 80)
print("38. CUSTOMER SATISFACTION")
print("=" * 80)


def calculate_nps(scores: Sequence[int]) -> float:
    """
    Net Promoter Score:
        % promoters - % detractors

    Promoters: 9-10
    Passives: 7-8
    Detractors: 0-6
    """
    if not scores:
        return 0.0

    invalid = [score for score in scores if score < 0 or score > 10]
    if invalid:
        raise ValueError("NPS scores must be between 0 and 10.")

    promoters = sum(score >= 9 for score in scores)
    detractors = sum(score <= 6 for score in scores)

    promoter_percentage = promoters / len(scores) * 100
    detractor_percentage = detractors / len(scores) * 100

    return promoter_percentage - detractor_percentage


nps_scores = [10, 9, 8, 7, 6, 9, 10, 5, 8, 9]
print(f"NPS: {calculate_nps(nps_scores):.1f}")


# Satisfaction metrics should be interpreted with context.
# NPS, CSAT, CES, app ratings, support contacts, and qualitative feedback
# measure different aspects of the customer experience.


# =============================================================================
# 39. TECHNICAL COLLABORATION
# =============================================================================

print("\n" + "=" * 80)
print("39. TECHNICAL COLLABORATION")
print("=" * 80)


@dataclass
class TechnicalConstraint:
    constraint: str
    product_implication: str
    mitigation: str


technical_constraints = [
    TechnicalConstraint(
        "API rate limit",
        "Real-time data refresh cannot be unlimited.",
        "Cache data and define refresh expectations.",
    ),
    TechnicalConstraint(
        "Database scalability",
        "High-volume analytics queries may become expensive.",
        "Use appropriate indexing, aggregation, and architecture.",
    ),
    TechnicalConstraint(
        "Third-party dependency",
        "A provider outage can affect core functionality.",
        "Design fallback behavior and monitor dependency health.",
    ),
]

for constraint in technical_constraints:
    print(
        f"{constraint.constraint}: "
        f"{constraint.product_implication} "
        f"Mitigation: {constraint.mitigation}"
    )


# A product manager does not need to implement every technical component,
# but technical literacy improves product decisions.
#
# Important technical concepts for product managers include:
# - APIs
# - Databases
# - Authentication and authorization
# - Frontend and backend
# - Cloud infrastructure
# - Caching
# - Queues
# - Logging
# - Monitoring
# - Feature flags
# - Data pipelines
# - Integrations
# - System reliability


# =============================================================================
# 40. SECURITY AND PRIVACY
# =============================================================================

print("\n" + "=" * 80)
print("40. SECURITY AND PRIVACY")
print("=" * 80)


@dataclass
class SecurityRequirement:
    area: str
    requirement: str
    rationale: str


security_requirements = [
    SecurityRequirement(
        "Authentication",
        "Users must prove their identity before accessing protected data.",
        "Prevent unauthorized access.",
    ),
    SecurityRequirement(
        "Authorization",
        "Users must only access permitted resources.",
        "Prevent privilege violations.",
    ),
    SecurityRequirement(
        "Data protection",
        "Sensitive information must be appropriately protected.",
        "Reduce confidentiality risk.",
    ),
    SecurityRequirement(
        "Auditability",
        "Important actions should be traceable where appropriate.",
        "Support investigation and accountability.",
    ),
]

for requirement in security_requirements:
    print(
        f"{requirement.area}: {requirement.requirement} "
        f"Reason: {requirement.rationale}"
    )


# Security is a product concern as well as an engineering concern.
# Product managers should ask:
# - What data is collected?
# - Why is it collected?
# - Who can access it?
# - How long is it retained?
# - What happens if an account is compromised?
# - What happens if a third-party service fails?
# - Are there regulatory obligations?
#
# Privacy requirements vary by jurisdiction and product context.


# =============================================================================
# 41. ACCESSIBILITY
# =============================================================================

print("\n" + "=" * 80)
print("41. ACCESSIBILITY")
print("=" * 80)


@dataclass
class AccessibilityCheck:
    criterion: str
    status: bool
    rationale: str


accessibility_checks = [
    AccessibilityCheck(
        "Keyboard access",
        True,
        "Important actions should not require a mouse.",
    ),
    AccessibilityCheck(
        "Readable contrast",
        True,
        "Text and controls need sufficient visual distinction.",
    ),
    AccessibilityCheck(
        "Clear labels",
        True,
        "Controls should communicate their purpose.",
    ),
    AccessibilityCheck(
        "Error communication",
        True,
        "Errors should be understandable and actionable.",
    ),
]

for check in accessibility_checks:
    print(
        f"{check.criterion}: {'PASS' if check.status else 'FAIL'} "
        f"- {check.rationale}"
    )


# Accessibility should be considered during discovery, design,
# requirements, development, testing, and launch rather than added at the end.


# =============================================================================
# 42. PRODUCT OPERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("42. PRODUCT OPERATIONS")
print("=" * 80)


@dataclass
class ProductOperation:
    activity: str
    frequency: str
    owner: str
    purpose: str


operations = [
    ProductOperation(
        "Metric review",
        "Weekly",
        "Product",
        "Identify important product changes.",
    ),
    ProductOperation(
        "Backlog refinement",
        "Weekly",
        "Product + Engineering",
        "Prepare work for execution.",
    ),
    ProductOperation(
        "Customer feedback review",
        "Weekly",
        "Product + Support",
        "Identify recurring customer problems.",
    ),
    ProductOperation(
        "Roadmap review",
        "Monthly",
        "Product + Leadership",
        "Reassess priorities against evidence.",
    ),
]

for operation in operations:
    print(
        f"{operation.activity} | {operation.frequency} | "
        f"{operation.owner} | {operation.purpose}"
    )


# Product operations creates repeatable systems for:
# - Feedback management
# - Analytics
# - Documentation
# - Planning
# - Product launches
# - Stakeholder updates
# - Research repositories
# - Decision records


# =============================================================================
# 43. PRODUCT FEEDBACK SYSTEM
# =============================================================================

print("\n" + "=" * 80)
print("43. FEEDBACK SYSTEM")
print("=" * 80)


@dataclass
class Feedback:
    source: str
    segment: str
    topic: str
    sentiment: str
    frequency: int
    severity: int


feedback = [
    Feedback("Support", "Beginner", "Onboarding", "negative", 20, 4),
    Feedback("Interview", "Beginner", "Risk", "negative", 15, 5),
    Feedback("Survey", "Intermediate", "Analytics", "positive", 10, 3),
    Feedback("Sales", "Professional", "Reporting", "negative", 6, 4),
]


def feedback_priority(item: Feedback) -> int:
    return item.frequency * item.severity


for item in sorted(feedback, key=feedback_priority, reverse=True):
    print(
        f"{item.topic}: priority={feedback_priority(item)}, "
        f"source={item.source}, segment={item.segment}"
    )


# Feedback volume alone should not determine roadmap priority.
# A single high-severity issue may deserve more attention than dozens
# of low-impact requests.


# =============================================================================
# 44. EXPERIMENT HYPOTHESES
# =============================================================================

print("\n" + "=" * 80)
print("44. HYPOTHESIS-DRIVEN PRODUCT DEVELOPMENT")
print("=" * 80)


@dataclass
class Hypothesis:
    assumption: str
    change: str
    expected_behavior: str
    metric: str
    threshold: float

    def statement(self) -> str:
        return (
            f"We believe that {self.change} will cause "
            f"{self.expected_behavior}, measured by {self.metric}, "
            f"reaching at least {self.threshold}."
        )


hypothesis = Hypothesis(
    assumption="Users abandon onboarding because the first action is unclear.",
    change="showing one recommended first action",
    expected_behavior="more users complete their first trade",
    metric="first-trade completion rate",
    threshold=0.55,
)

print(hypothesis.statement())


# Hypothesis-driven development makes assumptions explicit.
# It encourages teams to test uncertain beliefs rather than treating
# assumptions as established facts.


# =============================================================================
# 45. PRODUCT DISCOVERY EXPERIMENTS
# =============================================================================

print("\n" + "=" * 80)
print("45. DISCOVERY EXPERIMENTS")
print("=" * 80)


@dataclass
class DiscoveryExperiment:
    method: str
    question: str
    cost: str
    evidence_type: str
    decision_rule: str


discovery_experiments = [
    DiscoveryExperiment(
        "Customer interviews",
        "Do users understand the problem?",
        "Low",
        "Qualitative",
        "Proceed if recurring pain appears across target users.",
    ),
    DiscoveryExperiment(
        "Prototype usability test",
        "Can users complete the proposed workflow?",
        "Low",
        "Behavioral",
        "Proceed if most target users complete the core task.",
    ),
    DiscoveryExperiment(
        "Fake-door test",
        "Will users express interest in a proposed capability?",
        "Low",
        "Behavioral",
        "Investigate if meaningful target users click.",
    ),
    DiscoveryExperiment(
        "Pricing test",
        "Does willingness to pay support the proposed model?",
        "Medium",
        "Behavioral",
        "Proceed if economics and demand meet defined thresholds.",
    ),
]

for experiment in discovery_experiments:
    print(
        f"{experiment.method}: {experiment.question} "
        f"Evidence={experiment.evidence_type}"
    )


# Different experiments answer different questions.
# A survey may measure stated preference.
# A prototype can test usability.
# A behavioral experiment can test actual action.
# No single research method answers every product question.


# =============================================================================
# 46. MVP
# =============================================================================

print("\n" + "=" * 80)
print("46. MVP")
print("=" * 80)


@dataclass
class MVP:
    customer_problem: str
    minimum_capability: List[str]
    learning_goal: str
    excluded_capabilities: List[str]


mvp = MVP(
    customer_problem="Users need to practice investment decisions safely.",
    minimum_capability=[
        "Create practice portfolio",
        "Place simulated trade",
        "View resulting position",
    ],
    learning_goal="Determine whether users repeatedly practice decisions.",
    excluded_capabilities=[
        "Social features",
        "Advanced automation",
        "Complex customization",
    ],
)

print(mvp)


# MVP means the smallest product capable of generating meaningful learning
# or delivering a minimum viable value proposition.
#
# It does not mean:
# - lowest possible quality
# - broken software
# - no security
# - no accessibility
# - arbitrary removal of essential functionality


# =============================================================================
# 47. PRODUCT-MARKET FIT
# =============================================================================

print("\n" + "=" * 80)
print("47. PRODUCT-MARKET FIT")
print("=" * 80)


@dataclass
class PMFSignal:
    signal: str
    evidence: str
    strength: int


pmf_signals = [
    PMFSignal(
        "Retention",
        "Users return repeatedly without repeated prompting.",
        4,
    ),
    PMFSignal(
        "Organic demand",
        "Users refer other users.",
        3,
    ),
    PMFSignal(
        "Customer pull",
        "Customers actively request continued access.",
        5,
    ),
    PMFSignal(
        "Economic viability",
        "Revenue or other value supports sustainable operation.",
        3,
    ),
]

pmf_score = mean(signal.strength for signal in pmf_signals)
print(f"Illustrative PMF signal score: {pmf_score:.2f}/5")


# Product-market fit is not a single universally accepted metric.
# It is better understood through converging evidence involving:
# - Retention
# - Customer value
# - Demand
# - Growth
# - Monetization or strategic value
# - Competitive strength


# =============================================================================
# 48. PRODUCT LIFECYCLE
# =============================================================================

print("\n" + "=" * 80)
print("48. PRODUCT LIFECYCLE")
print("=" * 80)


lifecycle_actions = {
    ProductStage.DISCOVERY: "Understand problems and validate assumptions.",
    ProductStage.VALIDATION: "Test desirability, feasibility, and viability.",
    ProductStage.DEVELOPMENT: "Build and validate the product.",
    ProductStage.LAUNCH: "Release and monitor the product.",
    ProductStage.GROWTH: "Improve acquisition, activation, retention, and economics.",
    ProductStage.MATURITY: "Optimize efficiency and defend differentiation.",
    ProductStage.DECLINE: "Decide whether to reposition, maintain, migrate, or retire.",
}

for stage, action in lifecycle_actions.items():
    print(f"{stage.value}: {action}")


# Product management responsibilities change by lifecycle stage.
# Discovery emphasizes uncertainty reduction.
# Growth emphasizes scalable value creation.
# Maturity emphasizes optimization and defensibility.
# Decline may require migration or sunset decisions.


# =============================================================================
# 49. SUNSETTING A FEATURE
# =============================================================================

print("\n" + "=" * 80)
print("49. FEATURE SUNSETTING")
print("=" * 80)


@dataclass
class SunsetAssessment:
    feature: str
    active_users: int
    strategic_value: int
    maintenance_cost: int
    alternatives_available: bool
    migration_effort: int

    def score_for_sunset(self) -> float:
        """
        Higher score suggests stronger reasons to consider retirement.

        This is an illustrative decision aid, not an automatic decision.
        """
        value_penalty = max(1, self.strategic_value)
        alternative_factor = 1.5 if self.alternatives_available else 0.5

        return (
            self.maintenance_cost
            * alternative_factor
            * (1 + self.migration_effort / 10)
            / value_penalty
        )


sunset = SunsetAssessment(
    feature="Legacy export format",
    active_users=150,
    strategic_value=1,
    maintenance_cost=5,
    alternatives_available=True,
    migration_effort=2,
)

print(f"Sunset assessment score: {sunset.score_for_sunset():.2f}")


# Removing a feature can be difficult because:
# - Existing users may depend on it.
# - Contracts may exist.
# - Documentation may reference it.
# - Support teams may need preparation.
# - Data migration may be required.
# - Trust can be damaged by abrupt changes.


# =============================================================================
# 50. PRODUCT DECISION TRADE-OFFS
# =============================================================================

print("\n" + "=" * 80)
print("50. TRADE-OFFS")
print("=" * 80)


@dataclass
class TradeOff:
    option_a: str
    option_b: str
    advantage_a: str
    advantage_b: str
    decision_factor: str


trade_offs = [
    TradeOff(
        "Build now",
        "Research first",
        "Faster delivery",
        "Lower uncertainty",
        "How uncertain and expensive is the decision?",
    ),
    TradeOff(
        "Custom build",
        "Third-party integration",
        "Greater control",
        "Faster implementation",
        "Strategic importance versus time and cost",
    ),
    TradeOff(
        "Broad launch",
        "Phased launch",
        "Faster exposure",
        "Lower operational risk",
        "Risk tolerance and reversibility",
    ),
]

for trade_off in trade_offs:
    print(
        f"{trade_off.option_a} vs {trade_off.option_b}: "
        f"{trade_off.decision_factor}"
    )


# Product management frequently involves choosing between imperfect options.
# The objective is not to eliminate trade-offs.
# It is to make them explicit and select the option with the best expected outcome.


# =============================================================================
# 51. REVERSIBILITY
# =============================================================================

print("\n" + "=" * 80)
print("51. REVERSIBILITY")
print("=" * 80)


@dataclass
class DecisionRisk:
    decision: str
    reversibility: str
    potential_impact: str
    recommended_behavior: str


decision_risks = [
    DecisionRisk(
        "Change button copy",
        "High",
        "Low",
        "Decide quickly and test.",
    ),
    DecisionRisk(
        "Change pricing model",
        "Medium",
        "High",
        "Research carefully and monitor closely.",
    ),
    DecisionRisk(
        "Migrate customer data",
        "Low",
        "Very high",
        "Use extensive validation, backups, and staged rollout.",
    ),
]

for item in decision_risks:
    print(
        f"{item.decision}: reversibility={item.reversibility}; "
        f"impact={item.potential_impact}; "
        f"behavior={item.recommended_behavior}"
    )


# Reversible decisions can often be made faster.
# Hard-to-reverse decisions deserve stronger evidence and safeguards.


# =============================================================================
# 52. COST OF DELAY
# =============================================================================

print("\n" + "=" * 80)
print("52. COST OF DELAY")
print("=" * 80)


def cost_of_delay(
    weekly_value_loss: float,
    delay_weeks: int,
) -> float:
    return weekly_value_loss * delay_weeks


print(
    "Estimated cost of an 8-week delay:",
    f"₹{cost_of_delay(75000, 8):,.2f}",
)


# Cost of delay can include:
# - Lost revenue
# - Lost customers
# - Competitive disadvantage
# - Increased operational cost
# - Regulatory exposure
# - Delayed learning
#
# It should be estimated transparently rather than presented as false precision.


# =============================================================================
# 53. PRODUCT ANALYTICS QUALITY
# =============================================================================

print("\n" + "=" * 80)
print("53. ANALYTICS QUALITY")
print("=" * 80)


@dataclass
class MetricDefinition:
    name: str
    numerator: str
    denominator: str
    population: str
    time_window: str
    exclusions: List[str]

    def validate(self) -> List[str]:
        errors = []

        if not self.numerator:
            errors.append("Numerator is missing.")
        if not self.denominator:
            errors.append("Denominator is missing.")
        if not self.population:
            errors.append("Population is missing.")
        if not self.time_window:
            errors.append("Time window is missing.")

        return errors


metric_definition = MetricDefinition(
    name="Activation rate",
    numerator="Users who complete first trade",
    denominator="Users who create an account",
    population="New registered users",
    time_window="Within 7 days of registration",
    exclusions=["Internal test accounts"],
)

print("Metric definition errors:", metric_definition.validate())


# A metric should have a stable definition.
# Otherwise two teams may use the same metric name for different calculations.


# =============================================================================
# 54. DATA SEGMENTATION
# =============================================================================

print("\n" + "=" * 80)
print("54. SEGMENTATION")
print("=" * 80)


@dataclass
class UserRecord:
    segment: str
    activated: bool
    retained: bool


users = [
    UserRecord("Beginner", True, True),
    UserRecord("Beginner", True, False),
    UserRecord("Beginner", False, False),
    UserRecord("Intermediate", True, True),
    UserRecord("Intermediate", True, True),
]


def retention_by_segment(
    records: Sequence[UserRecord],
) -> Dict[str, float]:
    grouped: Dict[str, List[UserRecord]] = {}

    for record in records:
        grouped.setdefault(record.segment, []).append(record)

    result: Dict[str, float] = {}

    for segment, segment_users in grouped.items():
        retained = sum(user.retained for user in segment_users)
        result[segment] = safe_rate(retained, len(segment_users))

    return result


print("Retention by segment:", retention_by_segment(users))


# Segmentation helps reveal differences hidden by averages.
# Useful dimensions depend on the product and may include:
# - User maturity
# - Geography
# - Device
# - Acquisition source
# - Customer size
# - Plan
# - Use case
# - Behavior


# =============================================================================
# 55. PRODUCT DECISION MATRIX
# =============================================================================

print("\n" + "=" * 80)
print("55. DECISION MATRIX")
print("=" * 80)


@dataclass
class DecisionOption:
    name: str
    customer_value: float
    business_value: float
    feasibility: float
    risk: float

    def weighted_score(self) -> float:
        return (
            self.customer_value * 0.35
            + self.business_value * 0.30
            + self.feasibility * 0.20
            + (10 - self.risk) * 0.15
        )


options = [
    DecisionOption("Build internally", 8, 7, 5, 4),
    DecisionOption("Buy solution", 6, 8, 9, 3),
    DecisionOption("Partner", 7, 7, 7, 5),
]

for option in sorted(
    options,
    key=lambda item: item.weighted_score(),
    reverse=True,
):
    print(f"{option.name}: {option.weighted_score():.2f}")


# Weighted decision matrices are useful when several criteria matter.
# The weights should be discussed explicitly because they encode strategy.


# =============================================================================
# 56. PRODUCT TEAM COLLABORATION
# =============================================================================

print("\n" + "=" * 80)
print("56. PRODUCT TEAM")
print("=" * 80)


@dataclass
class ProductTeamMember:
    role: str
    primary_focus: str
    typical_contribution: str


team = [
    ProductTeamMember(
        "Product Manager",
        "Customer and business outcomes",
        "Problem definition, prioritization, alignment",
    ),
    ProductTeamMember(
        "Product Designer",
        "User experience",
        "Research, interaction design, usability",
    ),
    ProductTeamMember(
        "Engineering Lead",
        "Technical delivery",
        "Architecture, feasibility, implementation",
    ),
    ProductTeamMember(
        "Data Analyst",
        "Evidence and measurement",
        "Metrics, analysis, experimentation",
    ),
    ProductTeamMember(
        "QA",
        "Product quality",
        "Validation and defect detection",
    ),
]

for member in team:
    print(
        f"{member.role}: {member.primary_focus} -> "
        f"{member.typical_contribution}"
    )


# High-performing product teams collaborate continuously rather than
# passing requirements from one function to another like a linear chain.


# =============================================================================
# 57. PRODUCT MANAGER AS CONNECTOR
# =============================================================================

print("\n" + "=" * 80)
print("57. PRODUCT MANAGER AS CONNECTOR")
print("=" * 80)


@dataclass
class ProductQuestion:
    question: str
    primary_partner: str
    evidence_needed: str


product_questions = [
    ProductQuestion(
        "Is the problem important enough to solve?",
        "Customer research",
        "Behavioral and qualitative evidence",
    ),
    ProductQuestion(
        "Can we build it?",
        "Engineering",
        "Technical feasibility",
    ),
    ProductQuestion(
        "Will users understand it?",
        "Design",
        "Usability evidence",
    ),
    ProductQuestion(
        "Will it improve the target outcome?",
        "Analytics",
        "Metric or experiment evidence",
    ),
    ProductQuestion(
        "Can we launch it safely?",
        "Operations",
        "Readiness and risk evidence",
    ),
]

for question in product_questions:
    print(
        f"{question.question} -> {question.primary_partner} "
        f"({question.evidence_needed})"
    )


# The PM role often exists at the intersection of:
#
# Customer value
# Business value
# Technical feasibility
# User experience
# Operational reality
#
# The PM helps the organization make coherent decisions across these dimensions.


# =============================================================================
# 58. PRODUCT DISCOVERY TO DELIVERY PIPELINE
# =============================================================================

print("\n" + "=" * 80)
print("58. DISCOVERY TO DELIVERY PIPELINE")
print("=" * 80)


@dataclass
class ProductWorkItem:
    stage: str
    output: str
    decision: str


pipeline = [
    ProductWorkItem(
        "Problem discovery",
        "Validated problem",
        "Should we investigate further?",
    ),
    ProductWorkItem(
        "Opportunity assessment",
        "Prioritized opportunity",
        "Is this worth investment?",
    ),
    ProductWorkItem(
        "Solution discovery",
        "Tested solution concept",
        "Does the solution appear useful?",
    ),
    ProductWorkItem(
        "Requirements",
        "PRD and acceptance criteria",
        "Is the work sufficiently defined?",
    ),
    ProductWorkItem(
        "Execution",
        "Working product",
        "Is it ready to release?",
    ),
    ProductWorkItem(
        "Launch",
        "Released product",
        "Is it safe and valuable at scale?",
    ),
    ProductWorkItem(
        "Measurement",
        "Evidence",
        "What should happen next?",
    ),
]

for item in pipeline:
    print(
        f"{item.stage}: {item.output} -> {item.decision}"
    )


# Product management is an iterative loop, not a one-way pipeline.
#
# Evidence after launch can invalidate assumptions made during discovery.
# Good product teams revise plans when evidence changes.


# =============================================================================
# 59. ADVANCED: OPPORTUNITY COST
# =============================================================================

print("\n" + "=" * 80)
print("59. OPPORTUNITY COST")
print("=" * 80)


@dataclass
class Investment:
    name: str
    capacity_units: int
    expected_value: float


investments = [
    Investment("Risk dashboard", 8, 95),
    Investment("Theme customization", 3, 20),
    Investment("Trade journal", 5, 55),
    Investment("Advanced reporting", 10, 80),
]


def value_per_capacity(investment: Investment) -> float:
    return investment.expected_value / max(investment.capacity_units, 1)


for investment in sorted(
    investments,
    key=value_per_capacity,
    reverse=True,
):
    print(
        f"{investment.name}: "
        f"value/capacity={value_per_capacity(investment):.2f}"
    )


# Choosing one initiative consumes capacity that could have been used elsewhere.
# Opportunity cost is therefore central to prioritization.


# =============================================================================
# 60. ADVANCED: SCENARIO ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("60. SCENARIO ANALYSIS")
print("=" * 80)


@dataclass
class Scenario:
    name: str
    probability: float
    outcome: float


scenarios = [
    Scenario("High adoption", 0.25, 1000000),
    Scenario("Expected adoption", 0.55, 600000),
    Scenario("Low adoption", 0.20, 100000),
]


def expected_value(scenario_list: Sequence[Scenario]) -> float:
    total_probability = sum(item.probability for item in scenario_list)

    if abs(total_probability - 1.0) > 0.001:
        raise ValueError("Scenario probabilities should sum to approximately 1.")

    return sum(item.probability * item.outcome for item in scenario_list)


print(f"Expected value: ₹{expected_value(scenarios):,.2f}")


# Expected-value analysis is useful for uncertain decisions.
# It should not hide uncertainty behind a single number.
# Scenario ranges, confidence levels, and assumptions should remain visible.


# =============================================================================
# 61. ADVANCED: AARRR / PIRATE FUNNEL
# =============================================================================

print("\n" + "=" * 80)
print("61. AARRR FUNNEL")
print("=" * 80)


aarrr = {
    "Acquisition": 10000,
    "Activation": 2500,
    "Retention": 1000,
    "Revenue": 250,
    "Referral": 100,
}

for stage, users in aarrr.items():
    print(f"{stage}: {users}")


# AARRR is a mnemonic for:
# Acquisition
# Activation
# Retention
# Revenue
# Referral
#
# It is a useful analytical structure, not a universal product strategy.


# =============================================================================
# 62. ADVANCED: CHURN
# =============================================================================

print("\n" + "=" * 80)
print("62. CHURN")
print("=" * 80)


def churn_rate(
    customers_start: int,
    customers_lost: int,
) -> float:
    if customers_start <= 0:
        return 0.0
    return customers_lost / customers_start * 100


print(f"Monthly churn: {churn_rate(5000, 250):.2f}%")


# Churn can refer to:
# - Customer churn
# - User churn
# - Revenue churn
# - Logo churn
#
# Definitions must be explicit because the same word can describe different populations.


# =============================================================================
# 63. ADVANCED: GROWTH ACCOUNTING
# =============================================================================

print("\n" + "=" * 80)
print("63. GROWTH ACCOUNTING")
print("=" * 80)


@dataclass
class GrowthAccounting:
    starting_active: int
    new_users: int
    resurrected_users: int
    churned_users: int

    @property
    def ending_active(self) -> int:
        return (
            self.starting_active
            + self.new_users
            + self.resurrected_users
            - self.churned_users
        )


growth = GrowthAccounting(
    starting_active=10000,
    new_users=2000,
    resurrected_users=500,
    churned_users=1200,
)

print(f"Ending active users: {growth.ending_active}")


# Growth accounting separates:
# - New users
# - Retained users
# - Resurrected users
# - Churned users
#
# This can reveal whether growth is coming from acquisition or improved retention.


# =============================================================================
# 64. ADVANCED: DAU / MAU
# =============================================================================

print("\n" + "=" * 80)
print("64. DAU / MAU")
print("=" * 80)


def dau_mau_ratio(daily_active_users: int, monthly_active_users: int) -> float:
    if monthly_active_users <= 0:
        return 0.0
    return daily_active_users / monthly_active_users * 100


print(
    f"DAU/MAU: "
    f"{dau_mau_ratio(2500, 10000):.1f}%"
)


# DAU/MAU is sometimes used as a rough engagement indicator.
# It should not be interpreted without understanding:
# - Product frequency
# - User expectations
# - Measurement windows
# - User segment
# - Seasonality


# =============================================================================
# 65. ADVANCED: BUSINESS METRICS
# =============================================================================

print("\n" + "=" * 80)
print("65. BUSINESS METRICS")
print("=" * 80)


def gross_margin(revenue: float, cost_of_goods_sold: float) -> float:
    if revenue == 0:
        return 0.0
    return (revenue - cost_of_goods_sold) / revenue * 100


def arpu(revenue: float, active_users: int) -> float:
    if active_users == 0:
        return 0.0
    return revenue / active_users


def payback_months(cac: float, monthly_contribution: float) -> float:
    if monthly_contribution <= 0:
        return float("inf")
    return cac / monthly_contribution


print(f"Gross margin: {gross_margin(1000000, 400000):.1f}%")
print(f"ARPU: ₹{arpu(1000000, 20000):.2f}")
print(f"CAC payback: {payback_months(1500, 300):.2f} months")


# Product managers should know enough finance to understand the consequences
# of acquisition, retention, pricing, product costs, and monetization decisions.


# =============================================================================
# 66. ADVANCED: DCF-STYLE PRODUCT THINKING
# =============================================================================

print("\n" + "=" * 80)
print("66. DISCOUNTED CASH FLOW INTUITION")
print("=" * 80)


def present_value(
    cash_flow: float,
    discount_rate: float,
    period: int,
) -> float:
    if discount_rate <= -1:
        raise ValueError("Discount rate must be greater than -100%.")

    return cash_flow / ((1 + discount_rate) ** period)


cash_flows = [200000, 250000, 300000]
discount_rate = 0.10

pv_values = [
    present_value(cash_flow, discount_rate, period)
    for period, cash_flow in enumerate(cash_flows, start=1)
]

print("Present values:", [f"₹{value:,.2f}" for value in pv_values])
print(f"Total present value: ₹{sum(pv_values):,.2f}")


# Product investments can be evaluated economically when appropriate.
# A simplified DCF demonstrates that future value is discounted because
# future cash flows have different economic value from immediate cash flows.


# =============================================================================
# 67. ADVANCED: PRODUCT ANALYTICS PIPELINE
# =============================================================================

print("\n" + "=" * 80)
print("67. ANALYTICS PIPELINE")
print("=" * 80)


@dataclass
class AnalyticsPipeline:
    collection: str
    validation: str
    storage: str
    transformation: str
    analysis: str
    decision: str


analytics_pipeline = AnalyticsPipeline(
    collection="Product events",
    validation="Schema and quality checks",
    storage="Analytics data store",
    transformation="Metric calculations",
    analysis="Dashboard and investigation",
    decision="Prioritization or product action",
)

print(analytics_pipeline)


# Product analytics quality depends on the full pipeline.
# A dashboard cannot compensate for missing or incorrectly defined events.


# =============================================================================
# 68. ADVANCED: PRODUCT EXPERIMENT DECISION
# =============================================================================

print("\n" + "=" * 80)
print("68. EXPERIMENT DECISION")
print("=" * 80)


@dataclass
class ExperimentDecision:
    primary_metric_improved: bool
    statistical_evidence: bool
    guardrails_healthy: bool
    customer_value_consistent: bool

    def recommendation(self) -> str:
        if (
            self.primary_metric_improved
            and self.statistical_evidence
            and self.guardrails_healthy
            and self.customer_value_consistent
        ):
            return "Strong case to scale, subject to operational review."

        if self.primary_metric_improved and self.guardrails_healthy:
            return "Promising result; investigate uncertainty before scaling."

        return "Do not scale based on current evidence."


experiment_decision = ExperimentDecision(
    primary_metric_improved=True,
    statistical_evidence=True,
    guardrails_healthy=True,
    customer_value_consistent=True,
)

print(experiment_decision.recommendation())


# An experiment result should be evaluated against the original hypothesis,
# not only against the question "Did the number go up?"


# =============================================================================
# 69. ADVANCED: PRODUCT QUALITY SCORE
# =============================================================================

print("\n" + "=" * 80)
print("69. PRODUCT QUALITY SCORE")
print("=" * 80)


@dataclass
class QualityDimensions:
    reliability: float
    usability: float
    performance: float
    accessibility: float
    supportability: float

    def score(self) -> float:
        values = [
            self.reliability,
            self.usability,
            self.performance,
            self.accessibility,
            self.supportability,
        ]
        return mean(values)


quality = QualityDimensions(
    reliability=9,
    usability=8,
    performance=8,
    accessibility=7,
    supportability=8,
)

print(f"Illustrative quality score: {quality.score():.2f}/10")


# Composite scores are convenient but can hide critical failures.
# A product with excellent average quality can still have a severe security
# or reliability problem. Critical guardrails should therefore be evaluated separately.


# =============================================================================
# 70. ADVANCED: PRODUCT GOVERNANCE
# =============================================================================

print("\n" + "=" * 80)
print("70. PRODUCT GOVERNANCE")
print("=" * 80)


@dataclass
class GovernanceCheck:
    area: str
    owner: str
    evidence: str
    review_frequency: str


governance = [
    GovernanceCheck(
        "Product metrics",
        "Product Analytics",
        "Metric definitions and dashboard",
        "Monthly",
    ),
    GovernanceCheck(
        "Security",
        "Security",
        "Risk assessment and controls",
        "Quarterly",
    ),
    GovernanceCheck(
        "Compliance",
        "Legal/Compliance",
        "Applicable requirements",
        "As required",
    ),
    GovernanceCheck(
        "Data quality",
        "Data/Engineering",
        "Quality monitoring",
        "Weekly",
    ),
]

for check in governance:
    print(
        f"{check.area}: owner={check.owner}, "
        f"review={check.review_frequency}"
    )


# Governance becomes especially important when products operate at scale,
# handle sensitive information, or have regulatory obligations.


# =============================================================================
# 71. END-TO-END CASE STUDY
# =============================================================================

print("\n" + "=" * 80)
print("71. END-TO-END PRODUCT CASE STUDY")
print("=" * 80)


@dataclass
class ProductCase:
    name: str
    customer_problem: ProblemStatement
    opportunity: Opportunity
    vision: ProductVision
    mvp: MVP
    primary_metric: str


case = ProductCase(
    name="Practice Investing",
    customer_problem=problem,
    opportunity=opportunities[0],
    vision=vision,
    mvp=mvp,
    primary_metric="Weekly meaningful learning sessions",
)

print(f"Case: {case.name}")
print(f"Problem: {case.customer_problem.problem}")
print(f"Opportunity score: {case.opportunity.opportunity_score():.2f}")
print(f"Vision: {case.vision.statement()}")
print(f"Primary metric: {case.primary_metric}")


# A simplified end-to-end product process:
#
# 1. Identify a problem.
# 2. Collect evidence.
# 3. Define the target user.
# 4. Assess opportunity size and strategic fit.
# 5. Generate and test possible solutions.
# 6. Select an MVP.
# 7. Define measurable requirements.
# 8. Align design and engineering.
# 9. Prioritize execution.
# 10. Instrument analytics.
# 11. Test quality.
# 12. Prepare launch.
# 13. Release in an appropriate manner.
# 14. Measure outcomes.
# 15. Learn and adjust.


# =============================================================================
# 72. PRODUCT MANAGER DAILY WORK SIMULATION
# =============================================================================

print("\n" + "=" * 80)
print("72. PRODUCT MANAGER DAILY WORK SIMULATION")
print("=" * 80)


@dataclass
class PMTask:
    time: str
    task: str
    purpose: str


daily_schedule = [
    PMTask(
        "09:00",
        "Review product metrics",
        "Detect important behavioral changes.",
    ),
    PMTask(
        "10:00",
        "Engineering sync",
        "Resolve execution risks and dependencies.",
    ),
    PMTask(
        "11:00",
        "Customer interview",
        "Investigate a recurring problem.",
    ),
    PMTask(
        "13:00",
        "Requirements refinement",
        "Clarify scope and acceptance criteria.",
    ),
    PMTask(
        "15:00",
        "Stakeholder meeting",
        "Make or communicate a product decision.",
    ),
    PMTask(
        "16:00",
        "Prioritization analysis",
        "Reassess work against evidence and constraints.",
    ),
    PMTask(
        "17:00",
        "Decision documentation",
        "Maintain alignment and traceability.",
    ),
]

for task in daily_schedule:
    print(f"{task.time} - {task.task}: {task.purpose}")


# There is no universal PM daily schedule.
# Work varies substantially by company, product stage, team structure,
# business model, and current product problems.


# =============================================================================
# 73. PRODUCT MANAGER WEEKLY OPERATING SYSTEM
# =============================================================================

print("\n" + "=" * 80)
print("73. WEEKLY OPERATING SYSTEM")
print("=" * 80)


weekly_rhythm = {
    "Monday": [
        "Review metrics",
        "Review priorities",
        "Identify execution risks",
    ],
    "Tuesday": [
        "Customer discovery",
        "Requirements work",
    ],
    "Wednesday": [
        "Design and engineering collaboration",
        "Backlog refinement",
    ],
    "Thursday": [
        "Experiment review",
        "Stakeholder communication",
    ],
    "Friday": [
        "Product review",
        "Decision documentation",
        "Roadmap reassessment",
    ],
}

for day, activities in weekly_rhythm.items():
    print(f"\n{day}:")
    for activity in activities:
        print(f"  - {activity}")


# This is an example operating rhythm, not a mandatory schedule.


# =============================================================================
# 74. COMMON PRODUCT MANAGEMENT MISTAKES
# =============================================================================

print("\n" + "=" * 80)
print("74. COMMON MISTAKES")
print("=" * 80)


mistakes_and_corrections = {
    "Feature-first thinking":
        "Start with the customer problem and desired outcome.",
    "Roadmap as a fixed promise":
        "Communicate assumptions, confidence, and intended outcomes.",
    "Vanity metrics":
        "Prefer metrics connected to customer or business value.",
    "Stakeholder-driven prioritization":
        "Use evidence and explicit decision criteria.",
    "Ignoring technical constraints":
        "Collaborate with engineering early.",
    "Ignoring edge cases":
        "Define failure and boundary behavior before release.",
    "Overbuilding":
        "Test assumptions before making large commitments.",
    "Under-measuring":
        "Instrument important product behaviors before launch.",
    "Confusing activity with outcome":
        "Measure whether customer behavior or business results changed.",
    "Treating research as proof":
        "Use research to reduce uncertainty, not to manufacture certainty.",
    "Ignoring operational readiness":
        "Include support, analytics, security, legal, and rollback planning.",
    "Avoiding difficult decisions":
        "Document trade-offs and make the best decision with available evidence.",
}

for mistake, correction in mistakes_and_corrections.items():
    print(f"{mistake} -> {correction}")


# =============================================================================
# 75. PRODUCT MANAGEMENT BEST PRACTICES
# =============================================================================

print("\n" + "=" * 80)
print("75. BEST PRACTICES")
print("=" * 80)


best_practices = [
    "Define the customer and problem clearly.",
    "Separate facts, assumptions, and opinions.",
    "Use evidence proportional to decision risk.",
    "Keep strategy connected to measurable outcomes.",
    "Make prioritization criteria explicit.",
    "Write requirements that are understandable and testable.",
    "Collaborate with design and engineering early.",
    "Instrument important product behavior.",
    "Treat launches as controlled operational events.",
    "Use phased release strategies when risk is meaningful.",
    "Review both primary and guardrail metrics.",
    "Document important decisions.",
    "Communicate changes in priorities clearly.",
    "Revisit assumptions when evidence changes.",
    "Remove low-value complexity.",
    "Consider accessibility, security, privacy, and reliability.",
    "Measure outcomes rather than simply counting shipped features.",
]

for number, practice in enumerate(best_practices, start=1):
    print(f"{number}. {practice}")


# =============================================================================
# 76. PRODUCT MANAGEMENT CHECKLIST
# =============================================================================

print("\n" + "=" * 80)
print("76. PRODUCT CHECKLIST")
print("=" * 80)


product_checklist = {
    "Strategy": [
        "Vision defined",
        "Target customer defined",
        "Strategic outcome defined",
    ],
    "Discovery": [
        "Problem evidence collected",
        "Current behavior understood",
        "Alternatives identified",
    ],
    "Prioritization": [
        "Options compared",
        "Effort considered",
        "Strategic alignment considered",
    ],
    "Requirements": [
        "Scope defined",
        "User stories written",
        "Acceptance criteria defined",
        "Edge cases considered",
    ],
    "Execution": [
        "Dependencies identified",
        "Risks tracked",
        "Decisions documented",
    ],
    "Analytics": [
        "Events defined",
        "Metrics defined",
        "Baseline established",
        "Success threshold established",
    ],
    "Launch": [
        "QA complete",
        "Support prepared",
        "Documentation ready",
        "Rollback plan ready",
    ],
    "Post-launch": [
        "Outcome measured",
        "Guardrails reviewed",
        "Customer feedback reviewed",
    ],
}

for category, checks in product_checklist.items():
    print(f"\n{category}:")
    for check in checks:
        print(f"[ ] {check}")


# =============================================================================
# 77. VALIDATION TESTS
# =============================================================================

print("\n" + "=" * 80)
print("77. SELF-TESTS")
print("=" * 80)


def assert_equal(actual, expected, description: str) -> None:
    """Simple test helper for this standalone educational script."""
    if actual != expected:
        raise AssertionError(
            f"{description}: expected {expected!r}, got {actual!r}"
        )


def assert_almost_equal(
    actual: float,
    expected: float,
    tolerance: float,
    description: str,
) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"{description}: expected approximately {expected}, got {actual}"
        )


assert_equal(
    calculate_concentration([0.5, 0.3, 0.2]),
    0.5,
    "Portfolio concentration",
)

assert_equal(
    safe_rate(50, 100),
    50.0,
    "Percentage calculation",
)

assert_equal(
    safe_rate(50, 0),
    0.0,
    "Zero denominator handling",
)

assert_almost_equal(
    relative_lift(10.0, 12.0),
    20.0,
    0.0001,
    "Relative lift",
)

assert_equal(
    calculate_nps([10, 9, 8, 7, 6, 5]),
    0.0,
    "NPS calculation",
)

assert_equal(
    launch.is_launch_ready(),
    False,
    "Launch readiness",
)

assert_equal(
    len(prd.validate()),
    0,
    "PRD validation",
)

print("All self-tests passed.")


# =============================================================================
# 78. ADVANCED PRODUCT THINKING PRINCIPLES
# =============================================================================

print("\n" + "=" * 80)
print("78. ADVANCED PRODUCT THINKING PRINCIPLES")
print("=" * 80)


advanced_principles = [
    (
        "Outcome over output",
        "Shipping more features does not automatically create more value.",
    ),
    (
        "Evidence over hierarchy",
        "A decision should be informed by evidence rather than stakeholder seniority alone.",
    ),
    (
        "Learning over certainty",
        "Discovery reduces uncertainty but rarely eliminates it completely.",
    ),
    (
        "Trade-offs over wish lists",
        "Every investment has an opportunity cost.",
    ),
    (
        "Systems over isolated features",
        "Customer behavior is shaped by the complete product experience.",
    ),
    (
        "Measurement before interpretation",
        "A metric must be correctly defined before conclusions are drawn from it.",
    ),
    (
        "Reversibility matters",
        "High-impact irreversible decisions deserve stronger evidence and controls.",
    ),
    (
        "Guardrails matter",
        "Optimizing one metric can damage another important outcome.",
    ),
]

for principle, explanation in advanced_principles:
    print(f"{principle}: {explanation}")


# =============================================================================
# 79. COMPLETE PRODUCT MANAGER RESPONSIBILITY MAP
# =============================================================================

print("\n" + "=" * 80)
print("79. COMPLETE RESPONSIBILITY MAP")
print("=" * 80)


responsibility_map = {
    "Strategy": [
        "Vision",
        "Product strategy",
        "Strategic objectives",
        "Product bets",
        "Business alignment",
    ],
    "Discovery": [
        "Customer research",
        "Problem discovery",
        "Personas",
        "Jobs-to-be-done",
        "Competitive research",
        "Opportunity assessment",
    ],
    "Prioritization": [
        "RICE",
        "WSJF",
        "MoSCoW",
        "Value versus effort",
        "Cost of delay",
        "Opportunity cost",
    ],
    "Requirements": [
        "Problem statements",
        "PRDs",
        "User stories",
        "Acceptance criteria",
        "Functional requirements",
        "Non-functional requirements",
        "Edge cases",
    ],
    "Execution": [
        "Backlog",
        "Dependencies",
        "Risk management",
        "Decision records",
        "Cross-functional coordination",
    ],
    "Launch": [
        "Readiness",
        "Go-to-market",
        "Phased release",
        "Feature flags",
        "Support preparation",
        "Rollback planning",
    ],
    "Analytics": [
        "Event instrumentation",
        "Funnels",
        "Retention",
        "Cohorts",
        "Experiments",
        "North Star metrics",
        "Business metrics",
    ],
    "Communication": [
        "Stakeholder management",
        "Executive updates",
        "Decision communication",
        "Documentation",
        "Cross-functional alignment",
    ],
    "Lifecycle": [
        "Growth",
        "Optimization",
        "Feature retirement",
        "Sunsetting",
        "Migration",
    ],
    "Governance": [
        "Security",
        "Privacy",
        "Accessibility",
        "Compliance",
        "Data quality",
        "Reliability",
    ],
}

for area, items in responsibility_map.items():
    print(f"\n{area}")
    for item in items:
        print(f"  - {item}")


# =============================================================================
# 80. FINAL EXECUTABLE PRODUCT MANAGEMENT MODEL
# =============================================================================

print("\n" + "=" * 80)
print("80. PRODUCT MANAGEMENT DECISION MODEL")
print("=" * 80)


@dataclass
class ProductDecisionModel:
    """
    A compact model connecting the major responsibilities.

    This represents a practical reasoning sequence:

        Problem
          -> Evidence
          -> Opportunity
          -> Strategy
          -> Prioritization
          -> Requirements
          -> Execution
          -> Launch
          -> Measurement
          -> Learning
          -> New decision
    """

    problem: str
    evidence_strength: int
    strategic_alignment: int
    customer_value: int
    business_value: int
    feasibility: int
    risk: int
    measurable_outcome: str

    def decision_score(self) -> float:
        positive = (
            self.evidence_strength
            + self.strategic_alignment
            + self.customer_value
            + self.business_value
            + self.feasibility
        )
        risk_adjusted = positive - self.risk
        return risk_adjusted

    def decision_quality(self) -> str:
        score = self.decision_score()

        if score >= 20:
            return "Strong candidate for investment."
        if score >= 14:
            return "Promising candidate requiring normal validation."
        if score >= 8:
            return "Requires stronger evidence or clearer strategic fit."
        return "Weak candidate under the current assumptions."


decision_model = ProductDecisionModel(
    problem="Users struggle to understand portfolio risk.",
    evidence_strength=4,
    strategic_alignment=5,
    customer_value=5,
    business_value=4,
    feasibility=4,
    risk=2,
    measurable_outcome="Increase correct interpretation of portfolio risk.",
)

print("Problem:", decision_model.problem)
print("Decision score:", decision_model.decision_score())
print("Assessment:", decision_model.decision_quality())
print("Outcome:", decision_model.measurable_outcome)


# =============================================================================
# SCRIPT EXECUTION NOTES
# =============================================================================
#
# This file is intentionally executable from beginning to end.
#
# It uses only Python's standard library.
#
# The calculations and frameworks are educational implementations.
# Real product decisions require context-specific definitions, data,
# organizational constraints, customer evidence, technical assessment,
# and appropriate legal, security, privacy, and financial review.
#
# The central product-management operating loop demonstrated throughout
# this file is:
#
#   Understand the customer
#       ↓
#   Define the problem
#       ↓
#   Gather evidence
#       ↓
#   Assess opportunities
#       ↓
#   Establish strategy and outcomes
#       ↓
#   Prioritize investments
#       ↓
#   Define requirements
#       ↓
#   Collaborate on design and engineering
#       ↓
#   Execute and manage risks
#       ↓
#   Prepare the launch
#       ↓
#   Release safely
#       ↓
#   Measure behavior and outcomes
#       ↓
#   Learn
#       ↓
#   Reprioritize
#
# Product management is therefore not limited to writing requirements
# or managing a backlog. It is a continuous decision-making discipline
# focused on creating customer and business value under constraints.
#
# =============================================================================
# END OF SCRIPT
# =============================================================================
