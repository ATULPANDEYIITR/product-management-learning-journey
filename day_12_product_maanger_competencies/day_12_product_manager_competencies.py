"""
Product Manager Competencies: Business, Technology, UX, Analytics,
Leadership, Communication, and Strategy

A self-contained study and practice program that teaches Product Management
competencies from beginner to advanced level through executable Python
examples.

The program intentionally uses the Python standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean, median
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


# =============================================================================
# 1. FOUNDATIONS: WHAT A PRODUCT MANAGER DOES
# =============================================================================

def section(title: str) -> None:
    """Print a consistent educational section heading."""
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


def subsection(title: str) -> None:
    """Print a subsection heading."""
    print("\n" + "-" * 72)
    print(title)
    print("-" * 72)


def explain(term: str, definition: str) -> None:
    """Print a concise definition used throughout the study program."""
    print(f"{term}: {definition}")


def competency_overview() -> None:
    section("FOUNDATIONS: PRODUCT MANAGEMENT COMPETENCY MODEL")

    explain(
        "Product Management",
        "The discipline of identifying valuable customer problems, deciding what "
        "to build, aligning teams around outcomes, and learning whether the "
        "product creates sustainable customer and business value.",
    )

    explain(
        "Product Manager",
        "A cross-functional product leader who connects customer needs, business "
        "objectives, technology constraints, user experience, evidence, and "
        "execution decisions.",
    )

    explain(
        "Product Strategy",
        "A coherent set of choices about customers, problems, positioning, "
        "outcomes, capabilities, and priorities.",
    )

    explain(
        "Product Outcome",
        "A measurable change in customer behavior, customer value, or business "
        "performance caused by product decisions.",
    )

    competencies = {
        "Business": "Markets, customers, business models, economics, competition, and financial reasoning.",
        "Technology": "Software concepts, architecture, APIs, data, security, reliability, and technical trade-offs.",
        "UX": "User research, journeys, interaction design, usability, accessibility, and customer experience.",
        "Analytics": "Metrics, funnels, cohorts, experimentation, statistics, and evidence-based decisions.",
        "Leadership": "Alignment, decision-making, influence, conflict management, ownership, and team effectiveness.",
        "Communication": "Writing, presentations, requirements, storytelling, stakeholder communication, and negotiation.",
        "Strategy": "Vision, positioning, segmentation, competitive advantage, prioritization, roadmaps, and portfolio choices.",
    }

    for name, description in competencies.items():
        print(f"\n{name}:")
        print(f"  {description}")

    print(
        "\nA strong Product Manager does not treat these competencies as isolated "
        "subjects. Business determines why value matters, UX clarifies the human "
        "problem, technology determines feasible solution space, analytics provides "
        "evidence, communication creates shared understanding, leadership coordinates "
        "people, and strategy determines which opportunities deserve attention."
    )


# =============================================================================
# 2. BUSINESS COMPETENCY
# =============================================================================

class BusinessModel(Enum):
    SUBSCRIPTION = "Subscription"
    TRANSACTION = "Transaction"
    ADVERTISING = "Advertising"
    MARKETPLACE = "Marketplace"
    FREEMIUM = "Freemium"
    LICENSING = "Licensing"


@dataclass
class UnitEconomics:
    """Basic unit-economic model for evaluating product sustainability."""

    price: float
    variable_cost: float
    acquisition_cost: float
    retention_months: float

    @property
    def contribution_margin(self) -> float:
        return self.price - self.variable_cost

    @property
    def contribution_margin_rate(self) -> float:
        if self.price == 0:
            return 0.0
        return self.contribution_margin / self.price

    @property
    def ltv(self) -> float:
        return self.contribution_margin * self.retention_months

    @property
    def ltv_cac_ratio(self) -> float:
        if self.acquisition_cost == 0:
            return float("inf")
        return self.ltv / self.acquisition_cost

    def report(self) -> None:
        print(f"Price: ${self.price:.2f}")
        print(f"Variable cost: ${self.variable_cost:.2f}")
        print(f"Contribution margin: ${self.contribution_margin:.2f}")
        print(f"Contribution margin rate: {self.contribution_margin_rate:.1%}")
        print(f"Estimated LTV: ${self.ltv:.2f}")
        print(f"CAC: ${self.acquisition_cost:.2f}")
        print(f"LTV/CAC: {self.ltv_cac_ratio:.2f}x")


def business_analysis_example() -> None:
    section("BUSINESS COMPETENCY")

    explain(
        "Market",
        "The group of customers and organizations that could potentially buy or use a product.",
    )
    explain(
        "Value Proposition",
        "The specific customer value a product promises to create.",
    )
    explain(
        "Revenue",
        "Money generated by selling products, services, subscriptions, transactions, or other monetized value.",
    )
    explain(
        "Gross Margin",
        "Revenue remaining after direct costs associated with delivering the product or service.",
    )
    explain(
        "CAC",
        "Customer Acquisition Cost: the average cost required to acquire a customer.",
    )
    explain(
        "LTV",
        "Lifetime Value: the expected economic contribution generated by a customer during the relationship.",
    )
    explain(
        "Churn",
        "The rate at which customers or users stop using or paying for a product.",
    )

    subsection("Business model classification")
    for model in BusinessModel:
        print(f"{model.name}: {model.value}")

    subsection("Unit economics example")
    economics = UnitEconomics(
        price=30.0,
        variable_cost=8.0,
        acquisition_cost=55.0,
        retention_months=8.0,
    )
    economics.report()

    subsection("Break-even reasoning")
    monthly_fixed_cost = 100_000
    contribution_per_customer = economics.contribution_margin

    if contribution_per_customer > 0:
        break_even_customers = monthly_fixed_cost / contribution_per_customer
        print(
            f"Monthly fixed cost: ${monthly_fixed_cost:,.0f}\n"
            f"Customers required to cover fixed cost: "
            f"{break_even_customers:,.0f}"
        )

    print(
        "\nProduct Managers should not optimize revenue blindly. A product can "
        "increase revenue while damaging retention, support costs, trust, or "
        "long-term customer value. Business competency therefore requires "
        "understanding the economic system around the product."
    )


# =============================================================================
# 3. MARKET AND COMPETITIVE ANALYSIS
# =============================================================================

@dataclass
class Competitor:
    name: str
    market_share: float
    price_index: float
    feature_score: float
    distribution_score: float


def competitive_position(competitors: Sequence[Competitor]) -> None:
    section("MARKET AND COMPETITIVE THINKING")

    if not competitors:
        print("No competitor data supplied.")
        return

    total_share = sum(c.market_share for c in competitors)

    print("Competitive landscape:")
    for competitor in competitors:
        share = (
            competitor.market_share / total_share
            if total_share
            else 0
        )
        print(
            f"{competitor.name}: "
            f"share={share:.1%}, "
            f"price_index={competitor.price_index:.2f}, "
            f"feature_score={competitor.feature_score:.1f}, "
            f"distribution={competitor.distribution_score:.1f}"
        )

    strongest = max(
        competitors,
        key=lambda c: c.feature_score + c.distribution_score,
    )

    print(
        f"\nStrongest combined feature/distribution position in this sample: "
        f"{strongest.name}"
    )

    print(
        "\nA Product Manager should distinguish between direct competitors, "
        "substitutes, internal alternatives, and the customer's choice to do nothing."
    )


# =============================================================================
# 4. TECHNOLOGY COMPETENCY
# =============================================================================

@dataclass
class TechnicalOption:
    name: str
    engineering_effort: float
    scalability: float
    reliability: float
    flexibility: float
    security_risk: float

    def weighted_score(self) -> float:
        return (
            self.scalability * 0.25
            + self.reliability * 0.25
            + self.flexibility * 0.15
            + (10 - self.security_risk) * 0.20
            + (10 - self.engineering_effort) * 0.15
        )


def technology_competency() -> None:
    section("TECHNOLOGY COMPETENCY")

    explain(
        "Frontend",
        "The part of a product users directly interact with, such as a web or mobile interface.",
    )
    explain(
        "Backend",
        "Server-side software responsible for business logic, data processing, integrations, and APIs.",
    )
    explain(
        "API",
        "A defined interface through which software components communicate.",
    )
    explain(
        "Database",
        "A system used to persist, retrieve, update, and organize structured or unstructured data.",
    )
    explain(
        "Latency",
        "The time between a request and the corresponding response.",
    )
    explain(
        "Availability",
        "The proportion of time a system is operational and accessible.",
    )
    explain(
        "Scalability",
        "The ability of a system to handle increasing workload without unacceptable degradation.",
    )
    explain(
        "Technical Debt",
        "The future cost created when expedient technical choices increase maintenance or change costs.",
    )

    subsection("Architecture reasoning")
    print(
        "A Product Manager does not need to implement every technical component, "
        "but should understand enough technology to ask useful questions."
    )

    questions = [
        "What system component owns this responsibility?",
        "What data is created, stored, and transmitted?",
        "Which APIs or external systems are involved?",
        "What happens when the dependency is unavailable?",
        "What are the latency and availability expectations?",
        "What security or privacy risks exist?",
        "What technical debt could this decision create?",
        "What is the simplest architecture that satisfies the actual requirement?",
    ]

    for question in questions:
        print(f"- {question}")

    subsection("Technology trade-off example")

    options = [
        TechnicalOption("Simple synchronous service", 3, 5, 7, 5, 3),
        TechnicalOption("Cached service", 5, 8, 8, 6, 4),
        TechnicalOption("Distributed event architecture", 8, 10, 8, 9, 6),
    ]

    for option in options:
        print(
            f"{option.name}: effort={option.engineering_effort}, "
            f"scalability={option.scalability}, reliability={option.reliability}, "
            f"flexibility={option.flexibility}, security_risk={option.security_risk}, "
            f"weighted_score={option.weighted_score():.2f}"
        )

    print(
        "\nThe highest technical score is not automatically the correct product "
        "decision. Complexity should be justified by actual scale, reliability, "
        "organizational capability, risk, and expected value."
    )


# =============================================================================
# 5. UX COMPETENCY
# =============================================================================

@dataclass
class UserJourneyStep:
    step: str
    effort: int
    satisfaction: int
    failure_rate: float


def ux_analysis(journey: Sequence[UserJourneyStep]) -> None:
    section("UX COMPETENCY")

    explain(
        "User Experience",
        "The complete quality of interaction a person has with a product before, during, and after use.",
    )
    explain(
        "Usability",
        "How effectively, efficiently, and satisfactorily users can accomplish intended tasks.",
    )
    explain(
        "Accessibility",
        "Designing products so people with different abilities can use them effectively.",
    )
    explain(
        "User Journey",
        "The sequence of actions, expectations, decisions, and experiences through a product experience.",
    )
    explain(
        "User Research",
        "Systematic investigation of user needs, behaviors, motivations, constraints, and problems.",
    )

    subsection("Journey analysis")

    total_effort = sum(step.effort for step in journey)
    average_satisfaction = mean(step.satisfaction for step in journey)
    highest_failure = max(journey, key=lambda step: step.failure_rate)

    for step in journey:
        print(
            f"{step.step}: "
            f"effort={step.effort}/10, "
            f"satisfaction={step.satisfaction}/10, "
            f"failure_rate={step.failure_rate:.1%}"
        )

    print(f"\nTotal journey effort: {total_effort}")
    print(f"Average satisfaction: {average_satisfaction:.2f}/10")
    print(
        f"Highest observed failure point: {highest_failure.step} "
        f"({highest_failure.failure_rate:.1%})"
    )

    print(
        "\nUX decisions should begin with user problems rather than visual features. "
        "A Product Manager should understand the distinction between what users "
        "request, what they actually need, and what evidence shows causes the problem."
    )


# =============================================================================
# 6. USER RESEARCH AND PROBLEM DEFINITION
# =============================================================================

@dataclass
class ResearchObservation:
    source: str
    problem: str
    frequency: int
    severity: int
    confidence: float

    def evidence_score(self) -> float:
        return self.frequency * self.severity * self.confidence


def prioritize_research_observations(
    observations: Sequence[ResearchObservation],
) -> List[ResearchObservation]:
    return sorted(
        observations,
        key=lambda item: item.evidence_score(),
        reverse=True,
    )


def research_example() -> None:
    section("USER RESEARCH AND PROBLEM DEFINITION")

    observations = [
        ResearchObservation("Interview", "Users cannot understand pricing", 14, 7, 0.80),
        ResearchObservation("Support tickets", "Checkout errors occur", 8, 10, 0.95),
        ResearchObservation("Survey", "Users request more themes", 31, 2, 0.65),
        ResearchObservation("Session recording", "Users miss the primary action", 19, 8, 0.85),
    ]

    ranked = prioritize_research_observations(observations)

    print("Evidence-ranked problems:")
    for rank, observation in enumerate(ranked, start=1):
        print(
            f"{rank}. {observation.problem} | "
            f"source={observation.source} | "
            f"frequency={observation.frequency} | "
            f"severity={observation.severity} | "
            f"confidence={observation.confidence:.0%} | "
            f"score={observation.evidence_score():.2f}"
        )

    print(
        "\nThe score is an educational heuristic, not a universal research formula. "
        "Qualitative evidence should not be reduced to a number without understanding "
        "context, sampling limitations, and contradictory evidence."
    )


# =============================================================================
# 7. ANALYTICS COMPETENCY
# =============================================================================

@dataclass
class Funnel:
    visitors: int
    signups: int
    activated: int
    paying: int

    def signup_rate(self) -> float:
        return safe_rate(self.signups, self.visitors)

    def activation_rate_from_signups(self) -> float:
        return safe_rate(self.activated, self.signups)

    def paid_conversion_from_activation(self) -> float:
        return safe_rate(self.paying, self.activated)

    def visitor_to_paid_rate(self) -> float:
        return safe_rate(self.paying, self.visitors)

    def report(self) -> None:
        print(f"Visitors: {self.visitors:,}")
        print(f"Signups: {self.signups:,}")
        print(f"Activated: {self.activated:,}")
        print(f"Paying: {self.paying:,}")
        print(f"Visitor -> signup: {self.signup_rate():.2%}")
        print(f"Signup -> activation: {self.activation_rate_from_signups():.2%}")
        print(f"Activation -> paid: {self.paid_conversion_from_activation():.2%}")
        print(f"Visitor -> paid: {self.visitor_to_paid_rate():.2%}")


def safe_rate(numerator: float, denominator: float) -> float:
    """Calculate a rate without allowing division by zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def analytics_competency() -> None:
    section("ANALYTICS COMPETENCY")

    explain(
        "North Star Metric",
        "A metric intended to represent sustained customer value while connecting product activity to business outcomes.",
    )
    explain(
        "Leading Indicator",
        "A measure that can change before a desired outcome and may help predict it.",
    )
    explain(
        "Lagging Indicator",
        "A measure of an outcome that becomes visible after relevant behavior has occurred.",
    )
    explain(
        "Funnel",
        "A sequence of stages used to understand progression and drop-off.",
    )
    explain(
        "Cohort",
        "A group of users sharing a defined characteristic or starting event, analyzed over time.",
    )
    explain(
        "Retention",
        "The proportion of users who continue to use a product after a defined period.",
    )

    subsection("Funnel example")
    funnel = Funnel(
        visitors=100_000,
        signups=20_000,
        activated=12_000,
        paying=2_400,
    )
    funnel.report()

    print(
        "\nAnalytics competency is not simply dashboard reading. It requires "
        "asking whether a metric is correctly defined, whether the data is reliable, "
        "whether the denominator is appropriate, and whether the metric represents "
        "the underlying product outcome."
    )


# =============================================================================
# 8. RETENTION AND COHORT ANALYSIS
# =============================================================================

def retention_rate(starting_users: int, returning_users: int) -> float:
    return safe_rate(returning_users, starting_users)


def cohort_analysis() -> None:
    section("COHORT AND RETENTION ANALYSIS")

    cohorts = {
        "January": [1000, 650, 510, 430],
        "February": [1200, 780, 590, 470],
        "March": [900, 630, 500, 420],
    }

    for cohort, counts in cohorts.items():
        initial = counts[0]
        rates = [retention_rate(initial, count) for count in counts]
        formatted = ", ".join(f"{rate:.1%}" for rate in rates)
        print(f"{cohort}: users={counts} | retention={formatted}")

    print(
        "\nCohort analysis helps distinguish product changes from changes in the "
        "composition of incoming users. Aggregate retention can improve even when "
        "individual cohorts are deteriorating, so both views matter."
    )


# =============================================================================
# 9. EXPERIMENTATION AND STATISTICAL REASONING
# =============================================================================

@dataclass
class ExperimentGroup:
    name: str
    users: int
    conversions: int

    @property
    def conversion_rate(self) -> float:
        return safe_rate(self.conversions, self.users)


def absolute_lift(control: ExperimentGroup, treatment: ExperimentGroup) -> float:
    return treatment.conversion_rate - control.conversion_rate


def relative_lift(control: ExperimentGroup, treatment: ExperimentGroup) -> float:
    if control.conversion_rate == 0:
        return 0.0
    return absolute_lift(control, treatment) / control.conversion_rate


def pooled_standard_error(
    control: ExperimentGroup,
    treatment: ExperimentGroup,
) -> float:
    p1 = control.conversion_rate
    p2 = treatment.conversion_rate

    variance = (
        p1 * (1 - p1) / control.users
        + p2 * (1 - p2) / treatment.users
    )
    return sqrt(variance)


def experiment_analysis() -> None:
    section("EXPERIMENTATION")

    explain(
        "A/B Test",
        "A controlled comparison in which different user groups receive different product variants.",
    )
    explain(
        "Control",
        "The baseline experience against which the treatment is evaluated.",
    )
    explain(
        "Treatment",
        "The changed experience being evaluated.",
    )
    explain(
        "Absolute Lift",
        "The difference between treatment and control conversion rates.",
    )
    explain(
        "Relative Lift",
        "Absolute lift divided by the control rate.",
    )
    explain(
        "Statistical Significance",
        "Evidence that an observed difference is unlikely under a specified null hypothesis, subject to assumptions and test design.",
    )

    control = ExperimentGroup("Control", 20_000, 2_000)
    treatment = ExperimentGroup("Treatment", 20_500, 2_255)

    abs_lift = absolute_lift(control, treatment)
    rel_lift = relative_lift(control, treatment)
    standard_error = pooled_standard_error(control, treatment)
    z_score = abs_lift / standard_error if standard_error else 0.0

    print(f"Control conversion: {control.conversion_rate:.2%}")
    print(f"Treatment conversion: {treatment.conversion_rate:.2%}")
    print(f"Absolute lift: {abs_lift:.2%}")
    print(f"Relative lift: {rel_lift:.2%}")
    print(f"Approximate z-score: {z_score:.2f}")

    print(
        "\nA Product Manager should not interpret statistical significance as "
        "business significance. A tiny statistically reliable improvement can "
        "have little economic value, while a large observed improvement can be "
        "uncertain because the sample is small."
    )


# =============================================================================
# 10. PRIORITIZATION
# =============================================================================

@dataclass
class ProductOpportunity:
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float

    def rice_score(self) -> float:
        if self.effort <= 0:
            return 0.0
        return self.reach * self.impact * self.confidence / self.effort


def rice_prioritization(opportunities: Sequence[ProductOpportunity]) -> None:
    section("STRATEGY AND PRIORITIZATION")

    explain(
        "RICE",
        "A prioritization heuristic using Reach, Impact, Confidence, and Effort.",
    )

    ranked = sorted(
        opportunities,
        key=lambda opportunity: opportunity.rice_score(),
        reverse=True,
    )

    for rank, opportunity in enumerate(ranked, start=1):
        print(
            f"{rank}. {opportunity.name}: "
            f"reach={opportunity.reach:.1f}, "
            f"impact={opportunity.impact:.1f}, "
            f"confidence={opportunity.confidence:.1%}, "
            f"effort={opportunity.effort:.1f}, "
            f"RICE={opportunity.rice_score():.2f}"
        )

    print(
        "\nRICE is not a mathematical truth. Its value is in making assumptions "
        "explicit and comparable. High-impact strategic work can deserve attention "
        "even when a mechanical score ranks it lower."
    )


# =============================================================================
# 11. OTHER PRIORITIZATION FRAMEWORKS
# =============================================================================

def prioritization_frameworks() -> None:
    section("PRIORITIZATION FRAMEWORK COMPARISON")

    frameworks = {
        "RICE": "Reach × Impact × Confidence ÷ Effort",
        "ICE": "Impact × Confidence ÷ Effort",
        "Value vs Effort": "Compare expected value with implementation cost.",
        "MoSCoW": "Must, Should, Could, Won't for a defined scope.",
        "Kano": "Classifies features by how they affect satisfaction.",
        "Opportunity Scoring": "Prioritizes opportunities based on importance and satisfaction.",
        "Cost of Delay": "Considers economic impact of postponing an opportunity.",
    }

    for name, description in frameworks.items():
        print(f"{name}: {description}")

    print(
        "\nThe framework should follow the decision. Use simple methods when "
        "uncertainty is high and detailed scoring would create false precision. "
        "Use more structured economic analysis when sequencing has material financial consequences."
    )


# =============================================================================
# 12. PRODUCT STRATEGY
# =============================================================================

@dataclass
class Strategy:
    vision: str
    target_customer: str
    customer_problem: str
    desired_outcome: str
    strategic_constraint: str

    def test_quality(self) -> List[str]:
        weaknesses = []

        if not self.vision.strip():
            weaknesses.append("Vision is undefined.")
        if not self.target_customer.strip():
            weaknesses.append("Target customer is undefined.")
        if not self.customer_problem.strip():
            weaknesses.append("Customer problem is undefined.")
        if not self.desired_outcome.strip():
            weaknesses.append("Desired outcome is undefined.")
        if not self.strategic_constraint.strip():
            weaknesses.append("Strategic constraint is undefined.")

        return weaknesses


def strategy_example() -> None:
    section("PRODUCT STRATEGY")

    strategy = Strategy(
        vision="Make small-business cash-flow decisions easier.",
        target_customer="Owners of small businesses with limited finance staff.",
        customer_problem="Financial information is fragmented and difficult to interpret.",
        desired_outcome="Increase weekly active financial planning behavior and retention.",
        strategic_constraint="The first release must use existing transaction integrations.",
    )

    print(f"Vision: {strategy.vision}")
    print(f"Target customer: {strategy.target_customer}")
    print(f"Problem: {strategy.customer_problem}")
    print(f"Outcome: {strategy.desired_outcome}")
    print(f"Constraint: {strategy.strategic_constraint}")

    weaknesses = strategy.test_quality()
    if weaknesses:
        print("\nStrategy quality issues:")
        for weakness in weaknesses:
            print(f"- {weakness}")
    else:
        print("\nThe strategy contains the core elements required for a testable product direction.")

    print(
        "\nStrategy is fundamentally about choices. A strategy that attempts to "
        "serve every customer, solve every problem, and prioritize every opportunity "
        "does not provide useful guidance."
    )


# =============================================================================
# 13. PRODUCT-MARKET FIT AND OUTCOMES
# =============================================================================

def product_outcome_tree() -> None:
    section("OUTCOME-BASED PRODUCT THINKING")

    tree = {
        "Business outcome": [
            "Increase recurring revenue",
            "Reduce avoidable support cost",
            "Improve customer retention",
        ],
        "Product outcomes": [
            "Increase successful task completion",
            "Increase meaningful feature adoption",
            "Reduce time to first value",
        ],
        "Behavioral indicators": [
            "More users complete the target workflow",
            "Users return to repeat the valuable behavior",
            "Users reach activation faster",
        ],
    }

    for level, outcomes in tree.items():
        print(f"\n{level}:")
        for outcome in outcomes:
            print(f"  - {outcome}")

    print(
        "\nA feature is an output. Adoption is a behavior. Customer value is an "
        "outcome. Business performance is a broader outcome. Product management "
        "becomes stronger when teams explicitly connect these layers."
    )


# =============================================================================
# 14. COMMUNICATION COMPETENCY
# =============================================================================

@dataclass
class ProductDecision:
    decision: str
    problem: str
    evidence: List[str]
    alternatives_rejected: List[str]
    risks: List[str]
    success_metric: str


def write_decision_brief(decision: ProductDecision) -> str:
    """Generate a concise decision document suitable for stakeholder alignment."""
    evidence_text = "\n".join(f"- {item}" for item in decision.evidence)
    rejected_text = "\n".join(f"- {item}" for item in decision.alternatives_rejected)
    risks_text = "\n".join(f"- {item}" for item in decision.risks)

    return (
        f"Decision: {decision.decision}\n\n"
        f"Problem:\n{decision.problem}\n\n"
        f"Evidence:\n{evidence_text}\n\n"
        f"Alternatives not selected:\n{rejected_text}\n\n"
        f"Risks:\n{risks_text}\n\n"
        f"Success metric:\n{decision.success_metric}\n"
    )


def communication_competency() -> None:
    section("COMMUNICATION COMPETENCY")

    explain(
        "Product Requirement",
        "A statement describing a product behavior, constraint, or outcome that the team must satisfy.",
    )
    explain(
        "User Story",
        "A lightweight representation of a user need, commonly expressed through user, need, and value.",
    )
    explain(
        "Acceptance Criteria",
        "Specific conditions that determine whether a requirement has been satisfied.",
    )
    explain(
        "Decision Record",
        "A written record explaining a significant decision, its reasoning, alternatives, and consequences.",
    )

    decision = ProductDecision(
        decision="Simplify the checkout flow before adding new payment methods.",
        problem="Checkout abandonment is materially higher than expected.",
        evidence=[
            "The highest funnel drop occurs between address entry and payment confirmation.",
            "Support tickets show repeated confusion around the confirmation step.",
            "The existing payment method supports the majority of customers.",
        ],
        alternatives_rejected=[
            "Add more payment methods immediately because the evidence does not establish that payment-method coverage is the primary constraint.",
            "Increase marketing traffic because increasing traffic does not directly solve checkout friction.",
        ],
        risks=[
            "Removing optional information may reduce data available to downstream teams.",
            "A simplified flow could expose hidden edge cases.",
        ],
        success_metric="Reduce checkout abandonment without reducing successful payment completion.",
    )

    print(write_decision_brief(decision))

    print(
        "Good Product Management communication separates facts, assumptions, "
        "decisions, risks, and unresolved questions. It avoids hiding uncertainty "
        "behind confident language."
    )


# =============================================================================
# 15. LEADERSHIP AND INFLUENCE
# =============================================================================

@dataclass
class Stakeholder:
    name: str
    influence: int
    interest: int
    primary_concern: str

    @property
    def priority(self) -> int:
        return self.influence * self.interest


def stakeholder_mapping(stakeholders: Sequence[Stakeholder]) -> None:
    section("LEADERSHIP AND STAKEHOLDER MANAGEMENT")

    explain(
        "Influence",
        "The degree to which a stakeholder can affect product decisions, resources, execution, or outcomes.",
    )
    explain(
        "Interest",
        "The degree to which a stakeholder is affected by or concerned with the product decision.",
    )
    explain(
        "Alignment",
        "A shared understanding of goals, constraints, decisions, and responsibilities.",
    )
    explain(
        "Influence Without Authority",
        "The ability to move decisions through evidence, relationships, clarity, and credibility rather than formal reporting power.",
    )

    ranked = sorted(stakeholders, key=lambda s: s.priority, reverse=True)

    for stakeholder in ranked:
        print(
            f"{stakeholder.name}: influence={stakeholder.influence}/5, "
            f"interest={stakeholder.interest}/5, "
            f"priority={stakeholder.priority}, "
            f"concern={stakeholder.primary_concern}"
        )

    print(
        "\nStakeholder management is not about making everyone agree with every "
        "decision. It is about ensuring that the right people understand the "
        "decision, its evidence, trade-offs, ownership, and consequences."
    )


# =============================================================================
# 16. CONFLICT MANAGEMENT
# =============================================================================

def conflict_analysis(
    product_goal: str,
    stakeholder_positions: Dict[str, str],
) -> None:
    section("CONFLICT MANAGEMENT")

    print(f"Shared product goal: {product_goal}")

    for stakeholder, position in stakeholder_positions.items():
        print(f"{stakeholder}: {position}")

    print(
        "\nA useful conflict sequence is:\n"
        "1. Establish the shared outcome.\n"
        "2. Separate interests from stated positions.\n"
        "3. Identify evidence and assumptions.\n"
        "4. Make constraints explicit.\n"
        "5. Generate alternatives.\n"
        "6. Decide who owns the decision.\n"
        "7. Record the decision and revisit conditions."
    )


# =============================================================================
# 17. PRODUCT DISCOVERY AND DELIVERY
# =============================================================================

class ProductStage(Enum):
    DISCOVER = "Discover"
    DEFINE = "Define"
    DESIGN = "Design"
    BUILD = "Build"
    LAUNCH = "Launch"
    LEARN = "Learn"


def product_lifecycle() -> None:
    section("PRODUCT DISCOVERY AND DELIVERY")

    for stage in ProductStage:
        print(f"{stage.name}: {stage.value}")

    print(
        "\nDiscovery reduces uncertainty about the problem and potential solution. "
        "Delivery converts validated decisions into reliable product increments. "
        "The stages are not necessarily strictly sequential because learning can "
        "change assumptions at any point."
    )


# =============================================================================
# 18. PRODUCT REQUIREMENTS AND ACCEPTANCE CRITERIA
# =============================================================================

@dataclass
class Requirement:
    title: str
    user: str
    need: str
    value: str
    acceptance_criteria: List[str]

    def validate(self) -> List[str]:
        issues = []

        if not self.title.strip():
            issues.append("Missing requirement title.")
        if not self.user.strip():
            issues.append("Missing user.")
        if not self.need.strip():
            issues.append("Missing user need.")
        if not self.value.strip():
            issues.append("Missing expected value.")
        if not self.acceptance_criteria:
            issues.append("Missing acceptance criteria.")

        return issues


def requirements_example() -> None:
    section("REQUIREMENTS AND PRODUCT SPECIFICATION")

    requirement = Requirement(
        title="Save a preferred payment method",
        user="Returning customer",
        need="Reuse a previously authorized payment method",
        value="Complete checkout with less repeated effort",
        acceptance_criteria=[
            "A customer can explicitly choose to save the payment method.",
            "The saved method is displayed on subsequent eligible checkouts.",
            "The customer can remove the saved method.",
            "Sensitive payment credentials are not stored directly by the product.",
        ],
    )

    print(f"As a {requirement.user}, I want to {requirement.need}, so that {requirement.value}.")
    print("\nAcceptance criteria:")
    for criterion in requirement.acceptance_criteria:
        print(f"- {criterion}")

    issues = requirement.validate()
    print("\nValidation:")
    print("Valid requirement." if not issues else "\n".join(issues))


# =============================================================================
# 19. ROADMAP DESIGN
# =============================================================================

@dataclass
class RoadmapItem:
    name: str
    strategic_alignment: int
    customer_value: int
    confidence: int
    effort: int
    dependency_count: int

    def priority_score(self) -> float:
        denominator = max(1, self.effort + self.dependency_count)
        return (
            self.strategic_alignment
            * self.customer_value
            * self.confidence
            / denominator
        )


def roadmap_example() -> None:
    section("ROADMAP AND PORTFOLIO THINKING")

    items = [
        RoadmapItem("Improve activation", 10, 9, 8, 5, 1),
        RoadmapItem("New dashboard theme", 4, 3, 7, 2, 0),
        RoadmapItem("Reduce checkout failures", 10, 10, 9, 6, 2),
        RoadmapItem("Advanced export format", 6, 5, 6, 4, 1),
    ]

    ranked = sorted(items, key=lambda item: item.priority_score(), reverse=True)

    for item in ranked:
        print(
            f"{item.name}: score={item.priority_score():.2f}, "
            f"alignment={item.strategic_alignment}, "
            f"value={item.customer_value}, "
            f"confidence={item.confidence}, "
            f"effort={item.effort}, "
            f"dependencies={item.dependency_count}"
        )

    print(
        "\nA roadmap should communicate direction, outcomes, sequencing, and "
        "important commitments. Treating a roadmap as a permanent list of "
        "features can create false certainty when discovery and dependencies remain uncertain."
    )


# =============================================================================
# 20. PRODUCT METRICS TREE
# =============================================================================

@dataclass
class MetricNode:
    name: str
    value: float
    children: List["MetricNode"] = field(default_factory=list)

    def print_tree(self, indent: int = 0) -> None:
        print(" " * indent + f"{self.name}: {self.value:.2f}")
        for child in self.children:
            child.print_tree(indent + 4)


def metrics_tree_example() -> None:
    section("METRIC TREES")

    root = MetricNode(
        "Monthly recurring revenue",
        500_000,
        children=[
            MetricNode(
                "Paying customers",
                10_000,
                children=[
                    MetricNode("New customers", 1_500),
                    MetricNode("Retained customers", 8_500),
                ],
            ),
            MetricNode(
                "Average revenue per customer",
                50,
                children=[
                    MetricNode("Plan mix", 0.60),
                    MetricNode("Expansion revenue", 0.20),
                ],
            ),
        ],
    )

    root.print_tree()

    print(
        "\nMetric trees help connect high-level business outcomes to measurable "
        "drivers. They are useful for deciding where product work can influence "
        "business performance."
    )


# =============================================================================
# 21. DATA QUALITY AND ANALYTICS PITFALLS
# =============================================================================

def analytics_pitfalls() -> None:
    section("ANALYTICS PITFALLS")

    pitfalls = {
        "Vanity metrics": "Numbers that look impressive but have weak connection to customer or business outcomes.",
        "Survivorship bias": "Analyzing only users who remain and ignoring users who left.",
        "Selection bias": "The analyzed sample differs systematically from the intended population.",
        "Simpson's paradox": "An aggregate relationship can reverse when data is separated into meaningful groups.",
        "Denominator error": "A rate is calculated against an inappropriate population.",
        "Instrumentation gaps": "Events are missing, duplicated, delayed, or incorrectly defined.",
        "Correlation vs causation": "Two variables moving together does not prove one caused the other.",
        "Metric gaming": "Teams change behavior to improve a measured number without improving the underlying outcome.",
    }

    for name, description in pitfalls.items():
        print(f"{name}: {description}")

    print(
        "\nThe Product Manager should ask: What exactly is being measured? Who is "
        "included? Who is excluded? When is the event recorded? What alternative "
        "explanations exist? What decision would change if the result were different?"
    )


# =============================================================================
# 22. SECURITY AND PRIVACY COMPETENCY
# =============================================================================

def security_competency() -> None:
    section("SECURITY, PRIVACY, AND TRUST")

    explain(
        "Authentication",
        "Verifying who a user or system is.",
    )
    explain(
        "Authorization",
        "Determining what an authenticated user or system is allowed to do.",
    )
    explain(
        "Encryption",
        "Transforming information so unauthorized parties cannot meaningfully read it without the required key.",
    )
    explain(
        "Least Privilege",
        "Granting only the permissions necessary to perform an intended task.",
    )
    explain(
        "Data Minimization",
        "Collecting and retaining only data that has a justified product or operational purpose.",
    )
    explain(
        "Threat Modeling",
        "Systematically identifying assets, threats, attack paths, and mitigations.",
    )

    security_questions = [
        "What sensitive information does the feature process?",
        "Who can access the information?",
        "Why is each piece of data collected?",
        "How long should it be retained?",
        "What happens if an account is compromised?",
        "What external services receive the data?",
        "What auditability is required?",
        "What abuse cases should be tested before launch?",
    ]

    print("\nProduct security review questions:")
    for question in security_questions:
        print(f"- {question}")

    print(
        "\nSecurity is a product responsibility as well as an engineering responsibility. "
        "Product decisions define data flows, permissions, user-facing controls, and "
        "business processes that determine the practical risk surface."
    )


# =============================================================================
# 23. RELIABILITY AND PRODUCTION READINESS
# =============================================================================

@dataclass
class ProductionReadiness:
    functionality: bool
    monitoring: bool
    rollback: bool
    support: bool
    documentation: bool
    security_review: bool
    data_quality: bool

    def readiness_score(self) -> float:
        checks = [
            self.functionality,
            self.monitoring,
            self.rollback,
            self.support,
            self.documentation,
            self.security_review,
            self.data_quality,
        ]
        return sum(checks) / len(checks)

    def report(self) -> None:
        checks = {
            "Functionality": self.functionality,
            "Monitoring": self.monitoring,
            "Rollback": self.rollback,
            "Support": self.support,
            "Documentation": self.documentation,
            "Security review": self.security_review,
            "Data quality": self.data_quality,
        }

        for name, complete in checks.items():
            print(f"{name}: {'READY' if complete else 'MISSING'}")

        print(f"Readiness score: {self.readiness_score():.1%}")


def production_example() -> None:
    section("PRODUCTION AND LAUNCH COMPETENCY")

    readiness = ProductionReadiness(
        functionality=True,
        monitoring=True,
        rollback=True,
        support=False,
        documentation=True,
        security_review=True,
        data_quality=False,
    )

    readiness.report()

    print(
        "\nProduction readiness extends beyond whether code works. Product teams "
        "should consider observability, operational ownership, customer support, "
        "rollback procedures, security, data integrity, communication, and failure handling."
    )


# =============================================================================
# 24. EXPERIMENT DESIGN AND GUARDRAIL METRICS
# =============================================================================

@dataclass
class ExperimentDesign:
    hypothesis: str
    primary_metric: str
    guardrail_metrics: List[str]
    target_population: str
    duration_days: int

    def validate(self) -> List[str]:
        problems = []

        if not self.hypothesis.strip():
            problems.append("Hypothesis is missing.")
        if not self.primary_metric.strip():
            problems.append("Primary metric is missing.")
        if not self.guardrail_metrics:
            problems.append("At least one guardrail metric should be considered.")
        if not self.target_population.strip():
            problems.append("Target population is missing.")
        if self.duration_days <= 0:
            problems.append("Duration must be positive.")

        return problems


def experiment_design_example() -> None:
    section("EXPERIMENT DESIGN")

    experiment = ExperimentDesign(
        hypothesis="Reducing checkout form complexity will increase completed purchases.",
        primary_metric="Completed purchase rate",
        guardrail_metrics=[
            "Payment failure rate",
            "Refund rate",
            "Customer support contact rate",
        ],
        target_population="Eligible customers beginning checkout",
        duration_days=21,
    )

    print(f"Hypothesis: {experiment.hypothesis}")
    print(f"Primary metric: {experiment.primary_metric}")
    print(f"Population: {experiment.target_population}")
    print(f"Duration: {experiment.duration_days} days")
    print("Guardrails:")
    for metric in experiment.guardrail_metrics:
        print(f"- {metric}")

    problems = experiment.validate()
    print("\nDesign validation:")
    print("Valid design." if not problems else "\n".join(problems))

    print(
        "\nGuardrail metrics prevent local optimization. A change that increases "
        "conversion but also increases fraud, refunds, latency, or support burden "
        "may be harmful despite improving the primary metric."
    )


# =============================================================================
# 25. CUSTOMER SEGMENTATION
# =============================================================================

@dataclass
class CustomerSegment:
    name: str
    population: int
    revenue: float
    retention: float
    strategic_fit: float

    def revenue_per_customer(self) -> float:
        return safe_rate(self.revenue, self.population)

    def segment_value_score(self) -> float:
        return (
            self.revenue_per_customer()
            * self.retention
            * self.strategic_fit
        )


def segmentation_example() -> None:
    section("CUSTOMER SEGMENTATION")

    segments = [
        CustomerSegment("Small business", 8_000, 2_400_000, 0.72, 0.90),
        CustomerSegment("Mid-market", 2_000, 1_800_000, 0.84, 1.00),
        CustomerSegment("Enterprise", 300, 1_500_000, 0.91, 0.70),
    ]

    for segment in segments:
        print(
            f"{segment.name}: population={segment.population:,}, "
            f"revenue=${segment.revenue:,.0f}, "
            f"revenue/customer=${segment.revenue_per_customer():,.2f}, "
            f"retention={segment.retention:.1%}, "
            f"strategic_fit={segment.strategic_fit:.1%}, "
            f"illustrative_value={segment.segment_value_score():,.2f}"
        )

    print(
        "\nSegmentation is useful when different customer groups have materially "
        "different needs, economics, behavior, or strategic importance. Averages "
        "can hide these differences."
    )


# =============================================================================
# 26. PRODUCT DECISION MATRIX
# =============================================================================

def decision_matrix(
    options: Sequence[str],
    criteria: Sequence[str],
    scores: Dict[str, Dict[str, float]],
    weights: Dict[str, float],
) -> List[Tuple[str, float]]:
    """Calculate weighted decision scores."""
    results = []

    for option in options:
        score = 0.0
        for criterion in criteria:
            score += scores[option][criterion] * weights[criterion]
        results.append((option, score))

    return sorted(results, key=lambda pair: pair[1], reverse=True)


def decision_matrix_example() -> None:
    section("MULTI-CRITERIA DECISION MAKING")

    options = ["Build", "Buy", "Partner"]
    criteria = ["customer_value", "speed", "control", "risk"]

    weights = {
        "customer_value": 0.40,
        "speed": 0.20,
        "control": 0.20,
        "risk": 0.20,
    }

    scores = {
        "Build": {"customer_value": 9, "speed": 4, "control": 10, "risk": 5},
        "Buy": {"customer_value": 7, "speed": 9, "control": 5, "risk": 7},
        "Partner": {"customer_value": 8, "speed": 7, "control": 7, "risk": 8},
    }

    results = decision_matrix(options, criteria, scores, weights)

    for option, score in results:
        print(f"{option}: weighted score={score:.2f}")

    print(
        "\nWeighted matrices expose assumptions. They should support discussion, "
        "not replace judgment. Changing the weights can change the decision, "
        "which is useful because it reveals which assumptions matter most."
    )


# =============================================================================
# 27. PERFORMANCE CONSIDERATIONS FOR PRODUCT MANAGERS
# =============================================================================

def performance_considerations() -> None:
    section("PERFORMANCE AND SCALE")

    considerations = [
        ("Latency", "How quickly customers receive a useful response."),
        ("Throughput", "How much work the system can process over a period."),
        ("Capacity", "How much workload infrastructure can support."),
        ("Caching", "Reducing repeated expensive work by reusing appropriate results."),
        ("Database indexing", "Improving lookup performance at the cost of storage and write overhead."),
        ("Pagination", "Returning large datasets in manageable portions."),
        ("Asynchronous processing", "Moving non-immediate work outside the critical user request."),
        ("Rate limiting", "Controlling request volume to protect systems and dependencies."),
    ]

    for concept, explanation in considerations:
        print(f"{concept}: {explanation}")

    print(
        "\nProduct decisions should specify meaningful performance requirements "
        "rather than vague statements such as 'the product must be fast.' "
        "A useful requirement might define an acceptable response-time percentile "
        "for a specific workflow and traffic condition."
    )


# =============================================================================
# 28. PRODUCT OPERATING MODEL
# =============================================================================

@dataclass
class ProductTeamRole:
    role: str
    primary_responsibility: str


def product_team_model() -> None:
    section("CROSS-FUNCTIONAL PRODUCT TEAM")

    roles = [
        ProductTeamRole("Product Manager", "Customer problems, product direction, priorities, outcomes, and alignment."),
        ProductTeamRole("Engineering", "Technical implementation, architecture, reliability, security, and maintainability."),
        ProductTeamRole("Design / UX", "Research, interaction design, information architecture, usability, and experience quality."),
        ProductTeamRole("Data / Analytics", "Measurement, analysis, experimentation, instrumentation, and evidence."),
        ProductTeamRole("Marketing", "Positioning, acquisition, messaging, launches, and market feedback."),
        ProductTeamRole("Sales", "Customer relationships, commercial feedback, objections, and deal requirements."),
        ProductTeamRole("Customer Success / Support", "Adoption, customer health, recurring issues, and qualitative feedback."),
    ]

    for role in roles:
        print(f"{role.role}: {role.primary_responsibility}")

    print(
        "\nThe Product Manager coordinates these perspectives rather than replacing "
        "their expertise. Strong product leadership makes specialist knowledge "
        "usable in a shared decision process."
    )


# =============================================================================
# 29. PRODUCT DISCOVERY SCORECARD
# =============================================================================

@dataclass
class DiscoveryScore:
    desirability: float
    feasibility: float
    viability: float
    usability: float
    strategic_fit: float

    def average(self) -> float:
        values = [
            self.desirability,
            self.feasibility,
            self.viability,
            self.usability,
            self.strategic_fit,
        ]
        return mean(values)


def discovery_scorecard() -> None:
    section("DISCOVERY SCORECARD")

    score = DiscoveryScore(
        desirability=8.5,
        feasibility=7.0,
        viability=8.0,
        usability=7.5,
        strategic_fit=9.0,
    )

    print(f"Desirability: {score.desirability}/10")
    print(f"Feasibility: {score.feasibility}/10")
    print(f"Viability: {score.viability}/10")
    print(f"Usability: {score.usability}/10")
    print(f"Strategic fit: {score.strategic_fit}/10")
    print(f"Average assessment: {score.average():.2f}/10")

    print(
        "\nA strong opportunity must survive several perspectives. Customers "
        "may want something that is economically unattractive. A profitable idea "
        "may be technically impractical. A technically feasible product may have "
        "poor usability or weak strategic fit."
    )


# =============================================================================
# 30. EDGE CASES AND COMMON PRODUCT MANAGEMENT ERRORS
# =============================================================================

def common_mistakes() -> None:
    section("COMMON MISTAKES AND EDGE CASES")

    mistakes = [
        (
            "Feature-first thinking",
            "Starting with a feature instead of identifying the underlying customer problem."
        ),
        (
            "Stakeholder-driven roadmap",
            "Treating the loudest stakeholder request as automatically more important."
        ),
        (
            "Metric obsession",
            "Optimizing a number without checking whether the number represents meaningful value."
        ),
        (
            "False precision",
            "Assigning highly precise scores to uncertain assumptions and treating them as facts."
        ),
        (
            "Ignoring technical debt",
            "Assuming engineering complexity disappears because it is not visible to customers."
        ),
        (
            "Ignoring operational cost",
            "Launching functionality without considering support, infrastructure, compliance, or maintenance."
        ),
        (
            "Research confirmation",
            "Looking only for evidence that supports an existing idea."
        ),
        (
            "Premature scaling",
            "Adding architectural complexity before actual scale or reliability requirements justify it."
        ),
        (
            "No rollback plan",
            "Launching changes without a safe mechanism for responding to unexpected harm."
        ),
        (
            "Confusing activity with progress",
            "Measuring tickets completed or features shipped rather than meaningful outcomes."
        ),
    ]

    for mistake, explanation in mistakes:
        print(f"{mistake}: {explanation}")


# =============================================================================
# 31. INTEGRATED CASE STUDY
# =============================================================================

@dataclass
class ProductCase:
    product: str
    target_customer: str
    problem: str
    current_conversion: float
    target_conversion: float
    monthly_users: int
    monthly_revenue: float


def integrated_case_study() -> None:
    section("INTEGRATED PRODUCT MANAGEMENT CASE STUDY")

    case = ProductCase(
        product="Small-business financial planning platform",
        target_customer="Small-business owners",
        problem="Users struggle to convert transaction data into actionable weekly decisions.",
        current_conversion=0.18,
        target_conversion=0.24,
        monthly_users=50_000,
        monthly_revenue=750_000,
    )

    print(f"Product: {case.product}")
    print(f"Target customer: {case.target_customer}")
    print(f"Problem: {case.problem}")
    print(f"Current activation: {case.current_conversion:.1%}")
    print(f"Target activation: {case.target_conversion:.1%}")
    print(f"Monthly users: {case.monthly_users:,}")
    print(f"Monthly revenue: ${case.monthly_revenue:,.0f}")

    subsection("Business lens")
    incremental_users = case.monthly_users * (
        case.target_conversion - case.current_conversion
    )
    print(f"Potential additional activated users/month: {incremental_users:,.0f}")

    subsection("Analytics lens")
    funnel = Funnel(
        visitors=case.monthly_users,
        signups=15_000,
        activated=int(case.monthly_users * case.current_conversion),
        paying=4_000,
    )
    funnel.report()

    subsection("UX lens")
    journey = [
        UserJourneyStep("Connect account", 4, 7, 0.06),
        UserJourneyStep("Understand financial position", 8, 5, 0.22),
        UserJourneyStep("Create plan", 9, 4, 0.28),
        UserJourneyStep("Review recommendation", 5, 8, 0.08),
    ]
    ux_analysis(journey)

    subsection("Strategy lens")
    strategy = Strategy(
        vision="Help small-business owners make confident financial decisions.",
        target_customer=case.target_customer,
        customer_problem=case.problem,
        desired_outcome="Increase successful weekly financial planning behavior.",
        strategic_constraint="Use existing transaction data before adding new integrations.",
    )
    print(f"Strategic outcome: {strategy.desired_outcome}")
    print(f"Constraint: {strategy.strategic_constraint}")

    subsection("Prioritization lens")
    opportunities = [
        ProductOpportunity("Simplify plan creation", 80, 9, 0.85, 5),
        ProductOpportunity("Add more bank integrations", 35, 6, 0.70, 8),
        ProductOpportunity("Improve recommendation explanation", 60, 8, 0.80, 4),
        ProductOpportunity("Add visual themes", 20, 2, 0.90, 2),
    ]
    rice_prioritization(opportunities)

    subsection("Experiment lens")
    experiment = ExperimentDesign(
        hypothesis="A guided planning workflow will increase successful plan creation.",
        primary_metric="Completed plan creation rate",
        guardrail_metrics=[
            "Time to completion",
            "Support contact rate",
            "Weekly retention",
        ],
        target_population="New users with connected transaction accounts",
        duration_days=28,
    )
    print(f"Hypothesis: {experiment.hypothesis}")
    print(f"Primary metric: {experiment.primary_metric}")
    print(f"Duration: {experiment.duration_days} days")
    print("Guardrails:", ", ".join(experiment.guardrail_metrics))

    print(
        "\nThe integrated case demonstrates the central Product Management "
        "competency: connecting multiple disciplines to one coherent decision. "
        "The best product decision is rarely visible from a single functional lens."
    )


# =============================================================================
# 32. PRODUCT MANAGER COMPETENCY SELF-ASSESSMENT
# =============================================================================

@dataclass
class CompetencyRating:
    competency: str
    rating: float
    evidence: str

    def level(self) -> str:
        if self.rating < 3:
            return "Foundational"
        if self.rating < 5:
            return "Developing"
        if self.rating < 7:
            return "Working"
        if self.rating < 9:
            return "Advanced"
        return "Expert-level practice"


def competency_self_assessment() -> None:
    section("COMPETENCY SELF-ASSESSMENT")

    ratings = [
        CompetencyRating("Business", 7.0, "Can interpret basic economics and market trade-offs."),
        CompetencyRating("Technology", 6.0, "Understands APIs, architecture concepts, and technical trade-offs."),
        CompetencyRating("UX", 7.0, "Can reason about journeys, usability, and user problems."),
        CompetencyRating("Analytics", 7.5, "Can interpret funnels, cohorts, and experiments."),
        CompetencyRating("Leadership", 6.5, "Can align stakeholders around decisions and outcomes."),
        CompetencyRating("Communication", 8.0, "Can create structured decision documents and requirements."),
        CompetencyRating("Strategy", 6.5, "Can connect customer problems with outcomes and priorities."),
    ]

    for rating in ratings:
        print(
            f"{rating.competency}: {rating.rating:.1f}/10 | "
            f"{rating.level()} | {rating.evidence}"
        )

    print(
        "\nA competency rating should be supported by observable evidence such as "
        "decisions made, analyses performed, customer research conducted, products "
        "shipped, experiments interpreted, conflicts resolved, or business outcomes influenced."
    )


# =============================================================================
# 33. ADVANCED PRODUCT THINKING
# =============================================================================

def advanced_product_principles() -> None:
    section("ADVANCED PRODUCT MANAGEMENT PRINCIPLES")

    principles = [
        "Optimize for customer and business outcomes rather than feature volume.",
        "Treat assumptions as hypotheses that can be tested.",
        "Make opportunity cost explicit when prioritizing.",
        "Separate reversible decisions from difficult-to-reverse decisions.",
        "Prefer evidence proportional to the cost and risk of the decision.",
        "Use qualitative evidence to understand why and quantitative evidence to understand what and how much.",
        "Account for second-order effects such as support burden, trust, cannibalization, and operational complexity.",
        "Design metrics so local optimization does not damage the broader product system.",
        "Use strategy to constrain choices rather than to describe every possible activity.",
        "Build alignment before execution requires it.",
        "Preserve decision context so future teams understand why choices were made.",
        "Treat reliability, security, privacy, accessibility, and operational readiness as product qualities.",
        "Manage uncertainty explicitly instead of hiding it behind precise estimates.",
        "Use customer segmentation when averages conceal materially different behaviors.",
        "Continuously compare expected value with realized outcomes.",
    ]

    for number, principle in enumerate(principles, start=1):
        print(f"{number}. {principle}")


# =============================================================================
# 34. FINAL EXECUTION
# =============================================================================

def run_all_lessons() -> None:
    """Run every educational demonstration in a logical learning sequence."""

    competency_overview()
    business_analysis_example()

    competitive_position(
        [
            Competitor("Competitor A", 42, 1.00, 8.5, 9.0),
            Competitor("Competitor B", 31, 0.80, 7.5, 7.5),
            Competitor("Competitor C", 17, 1.20, 8.0, 6.0),
            Competitor("Our product", 10, 0.90, 7.0, 7.0),
        ]
    )

    technology_competency()

    ux_analysis(
        [
            UserJourneyStep("Discovery", 3, 8, 0.04),
            UserJourneyStep("Registration", 5, 7, 0.09),
            UserJourneyStep("Activation", 8, 5, 0.21),
            UserJourneyStep("Core task", 7, 6, 0.15),
            UserJourneyStep("Repeat use", 4, 8, 0.07),
        ]
    )

    research_example()
    analytics_competency()
    cohort_analysis()
    experiment_analysis()

    rice_prioritization(
        [
            ProductOpportunity("Improve activation", 80, 9, 0.90, 6),
            ProductOpportunity("Reduce support contacts", 50, 7, 0.80, 4),
            ProductOpportunity("New reporting feature", 30, 6, 0.70, 7),
            ProductOpportunity("Visual customization", 20, 3, 0.90, 2),
        ]
    )

    prioritization_frameworks()
    strategy_example()
    product_outcome_tree()
    communication_competency()

    stakeholder_mapping(
        [
            Stakeholder("Engineering Lead", 5, 5, "Technical feasibility and maintainability"),
            Stakeholder("Design Lead", 4, 5, "Experience quality and research evidence"),
            Stakeholder("Finance", 5, 3, "Economic impact"),
            Stakeholder("Sales", 4, 4, "Customer and market requirements"),
            Stakeholder("Support", 3, 5, "Operational and customer pain"),
        ]
    )

    conflict_analysis(
        "Increase successful customer outcomes without creating unacceptable operational risk.",
        {
            "Engineering": "Reduce complexity before expanding scope.",
            "Sales": "Add customer-requested capabilities quickly.",
            "Finance": "Protect economic efficiency.",
            "Support": "Reduce recurring customer problems.",
        },
    )

    product_lifecycle()
    requirements_example()
    roadmap_example()
    metrics_tree_example()
    analytics_pitfalls()
    security_competency()
    production_example()
    experiment_design_example()
    segmentation_example()
    decision_matrix_example()
    performance_considerations()
    product_team_model()
    discovery_scorecard()
    common_mistakes()
    integrated_case_study()
    competency_self_assessment()
    advanced_product_principles()

    section("END OF PRODUCT MANAGEMENT COMPETENCY PROGRAM")
    print(
        "The demonstrations above connect business, technology, UX, analytics, "
        "leadership, communication, and strategy into a unified Product Management "
        "decision-making model."
    )


if __name__ == "__main__":
    run_all_lessons()
