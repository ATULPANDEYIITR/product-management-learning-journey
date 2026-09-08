"""
Product Organizations: A Comprehensive Python Study Script

This script explains how major functions inside a product organization work
together to discover, build, launch, sell, support, operate, and improve products.

Functions covered:
- Product teams
- Engineering
- Design
- Marketing
- Sales
- Customer Success
- Operations
- Executive Leadership

The examples use a fictional SaaS product organization called "NexaCloud".
The script is self-contained and uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
from collections import defaultdict
from statistics import mean


# =============================================================================
# 1. FUNDAMENTAL CONCEPT: WHAT IS A PRODUCT ORGANIZATION?
# =============================================================================

# A product organization is not simply a group called "Product".
#
# It is a coordinated system of functions responsible for creating and
# delivering value through products. Different organizations may have different
# reporting structures, but most product businesses involve the following
# responsibilities:
#
# Product:
#   Determines what problems should be solved and why.
#
# Engineering:
#   Determines how the solution can be built reliably and technically.
#
# Design:
#   Determines how the solution should work and feel for users.
#
# Marketing:
#   Determines how the market understands the product and why customers should
#   care about it.
#
# Sales:
#   Helps potential customers evaluate and purchase the product.
#
# Customer Success:
#   Helps customers adopt the product and achieve desired outcomes.
#
# Operations:
#   Creates scalable processes, systems, coordination mechanisms, and controls.
#
# Executive Leadership:
#   Sets strategic direction, allocates resources, and resolves organizational
#   trade-offs.


class ProductLifecycleStage(Enum):
    """Major stages through which a product initiative may move."""

    DISCOVERY = "Discovery"
    VALIDATION = "Validation"
    DEVELOPMENT = "Development"
    LAUNCH = "Launch"
    GROWTH = "Growth"
    MATURITY = "Maturity"
    RETIREMENT = "Retirement"


class Priority(Enum):
    """A simple prioritization classification."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class WorkStatus(Enum):
    """Basic workflow states."""

    IDEA = "Idea"
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETE = "Complete"


# =============================================================================
# 2. CORE BUSINESS ENTITIES
# =============================================================================


@dataclass
class Customer:
    """
    Represents a customer.

    Product organizations must distinguish between:
    - Users: people who directly use a product.
    - Buyers: people or organizations that pay.
    - Decision makers: people who approve purchases.
    - Administrators: people responsible for implementation.
    - Influencers: people who influence purchasing decisions.

    A single person may occupy more than one role.
    """

    name: str
    segment: str
    annual_revenue: float
    active_users: int
    satisfaction_score: float
    churn_risk: float


@dataclass
class UserProblem:
    """
    Represents a problem discovered through research or customer interaction.

    A feature request is not automatically equivalent to a user problem.

    Example:
        Feature request:
            "Add a dark mode."

        Possible underlying problem:
            "Users experience visual discomfort during long working sessions."

    Product teams should attempt to understand the underlying problem before
    committing to a particular solution.
    """

    description: str
    affected_users: int
    severity: int  # 1 to 10
    evidence_strength: float  # 0.0 to 1.0
    strategic_alignment: float  # 0.0 to 1.0


@dataclass
class Feature:
    """
    Represents a product capability.

    Features are outputs. Business outcomes are different.

    Output:
        "We launched automated reporting."

    Outcome:
        "Customer reporting time decreased by 40%."

    Product organizations should avoid measuring success only through outputs.
    """

    name: str
    description: str
    estimated_effort: int
    expected_impact: float
    confidence: float
    priority: Priority = Priority.MEDIUM
    status: WorkStatus = WorkStatus.IDEA
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProductMetric:
    """
    Represents a measurable product or business indicator.

    Common metric categories:
    - Acquisition
    - Activation
    - Engagement
    - Retention
    - Revenue
    - Referral
    - Reliability
    - Customer satisfaction
    """

    name: str
    value: float
    target: float
    unit: str

    def achievement_ratio(self) -> float:
        """Returns performance relative to target."""

        if self.target == 0:
            return 0.0

        return self.value / self.target


# =============================================================================
# 3. PRODUCT MANAGEMENT
# =============================================================================


class ProductManager:
    """
    Product Management coordinates product decisions.

    Important distinction:
    Product Management does not "own every decision".

    Effective product management works through collaboration with engineering,
    design, commercial teams, customers, and leadership.

    Typical responsibilities include:
    - Understanding customers and markets
    - Defining product strategy
    - Prioritizing opportunities
    - Defining desired outcomes
    - Communicating direction
    - Managing trade-offs
    - Coordinating stakeholders
    - Measuring results
    """

    def __init__(self, name: str):
        self.name = name
        self.product_problems: List[UserProblem] = []
        self.roadmap: List[Feature] = []

    def add_problem(self, problem: UserProblem) -> None:
        self.product_problems.append(problem)

    def opportunity_score(self, problem: UserProblem) -> float:
        """
        Calculate a simplified opportunity score.

        This combines:
        - Number of affected users
        - Severity
        - Evidence
        - Strategic alignment

        Real organizations may use RICE, ICE, WSJF, Kano, Opportunity Scoring,
        Cost of Delay, or custom prioritization systems.

        No prioritization formula is objectively perfect.
        Formulas structure discussion but do not replace judgment.
        """

        return (
            problem.affected_users
            * problem.severity
            * problem.evidence_strength
            * problem.strategic_alignment
        )

    def rank_problems(self) -> List[UserProblem]:
        """Rank discovered problems from highest to lowest opportunity."""

        return sorted(
            self.product_problems,
            key=self.opportunity_score,
            reverse=True,
        )

    def rice_score(
        self,
        reach: float,
        impact: float,
        confidence: float,
        effort: float,
    ) -> float:
        """
        Calculate a simplified RICE score.

        RICE:
            Reach × Impact × Confidence
            ---------------------------
                    Effort

        Edge case:
            Effort must not be zero because division by zero is invalid.

        A very low estimated effort can artificially inflate the score, so
        estimates should be reviewed critically.
        """

        if effort <= 0:
            raise ValueError("Effort must be greater than zero.")

        if confidence < 0 or confidence > 1:
            raise ValueError("Confidence must be between 0 and 1.")

        return (reach * impact * confidence) / effort

    def add_to_roadmap(self, feature: Feature) -> None:
        self.roadmap.append(feature)

    def prioritize_roadmap(self) -> List[Feature]:
        """
        Rank features using expected impact, confidence, and effort.

        Simplified formula:
            impact × confidence / effort

        This resembles an expected value approach.

        Important limitation:
        Quantitative formulas can create false precision. An estimate of 8.2
        does not necessarily mean a feature is objectively better than one
        scoring 8.0.
        """

        def score(feature: Feature) -> float:
            if feature.estimated_effort <= 0:
                return 0.0

            return (
                feature.expected_impact
                * feature.confidence
                / feature.estimated_effort
            )

        return sorted(self.roadmap, key=score, reverse=True)


# =============================================================================
# 4. PRODUCT STRATEGY
# =============================================================================


@dataclass
class ProductStrategy:
    """
    A product strategy provides a coherent direction for product decisions.

    A useful strategy commonly addresses:
    - Target customers
    - Problems to solve
    - Desired position
    - Strategic advantages
    - Major bets
    - Success measures
    """

    vision: str
    target_segment: str
    strategic_problem: str
    differentiation: str
    success_metrics: List[str]


def evaluate_strategy_alignment(
    feature: Feature,
    strategy_keywords: Set[str],
) -> float:
    """
    Performs a simple keyword-based alignment demonstration.

    Real strategy evaluation requires human judgment and context.

    This function demonstrates that implementation systems can encode basic
    decision criteria, but automated scoring cannot fully determine strategic
    quality.
    """

    text = f"{feature.name} {feature.description}".lower()

    if not strategy_keywords:
        return 0.0

    matches = sum(
        1 for keyword in strategy_keywords
        if keyword.lower() in text
    )

    return matches / len(strategy_keywords)


# =============================================================================
# 5. PRODUCT ROADMAPS
# =============================================================================


class Roadmap:
    """
    A roadmap communicates direction and planned sequencing.

    A roadmap is not necessarily a commitment to deliver every listed feature.

    Common roadmap styles:
    - Feature-based roadmap
    - Outcome-based roadmap
    - Theme-based roadmap
    - Time-based roadmap
    - Now / Next / Later roadmap

    A strong roadmap communicates:
    - Why work matters
    - Expected outcomes
    - Major themes
    - Dependencies
    - Uncertainty
    """

    def __init__(self):
        self.items: List[Feature] = []

    def add_item(self, feature: Feature) -> None:
        self.items.append(feature)

    def validate_dependencies(self) -> Dict[str, List[str]]:
        """
        Detect dependencies that refer to unknown features.

        Missing dependencies are common causes of planning failures.
        """

        known_features = {feature.name for feature in self.items}

        missing = {}

        for feature in self.items:
            unknown_dependencies = [
                dependency
                for dependency in feature.dependencies
                if dependency not in known_features
            ]

            if unknown_dependencies:
                missing[feature.name] = unknown_dependencies

        return missing


# =============================================================================
# 6. PRODUCT TEAM STRUCTURES
# =============================================================================


class ProductTeamModel(Enum):
    """
    Common organizational structures.

    Functional:
        Teams grouped by discipline.

    Feature Team:
        Cross-functional team organized around product delivery.

    Platform Team:
        Provides reusable capabilities to other teams.

    Matrix:
        People may belong simultaneously to functional and product structures.

    Product Line:
        Teams organized around distinct product areas.
    """

    FUNCTIONAL = "Functional"
    FEATURE_TEAM = "Feature Team"
    PLATFORM_TEAM = "Platform Team"
    MATRIX = "Matrix"
    PRODUCT_LINE = "Product Line"


@dataclass
class TeamMember:
    name: str
    function: str
    skills: List[str]


@dataclass
class CrossFunctionalTeam:
    """
    Represents a product delivery team.

    Cross-functional teams reduce handoffs by placing complementary expertise
    closer to the work.
    """

    name: str
    mission: str
    members: List[TeamMember] = field(default_factory=list)

    def functions_present(self) -> Set[str]:
        return {member.function for member in self.members}

    def missing_core_functions(self) -> Set[str]:
        """
        Checks whether key capabilities are represented.

        Not every team requires dedicated members for every discipline.
        The appropriate structure depends on organizational size and context.
        """

        required = {"Product", "Engineering", "Design"}
        return required - self.functions_present()


# =============================================================================
# 7. ENGINEERING ORGANIZATION
# =============================================================================


@dataclass
class TechnicalRisk:
    description: str
    probability: float
    impact: float

    def exposure(self) -> float:
        """
        Simplified risk exposure.

        Exposure = Probability × Impact
        """

        return self.probability * self.impact


class EngineeringTeam:
    """
    Engineering converts product requirements into working systems.

    Major responsibilities can include:
    - Architecture
    - Software development
    - Testing
    - Reliability
    - Security
    - Performance
    - Infrastructure
    - Technical debt management
    """

    def __init__(self, name: str):
        self.name = name
        self.technical_debt_items: List[str] = []
        self.risks: List[TechnicalRisk] = []

    def estimate_delivery_time(
        self,
        feature: Feature,
        team_capacity_points: float,
    ) -> float:
        """
        Estimate delivery cycles.

        Important:
        Estimation is probabilistic.

        It should not be treated as a guaranteed completion date.
        """

        if team_capacity_points <= 0:
            raise ValueError("Team capacity must be greater than zero.")

        return feature.estimated_effort / team_capacity_points

    def add_technical_debt(self, description: str) -> None:
        self.technical_debt_items.append(description)

    def add_risk(self, risk: TechnicalRisk) -> None:
        self.risks.append(risk)

    def highest_risk(self) -> Optional[TechnicalRisk]:
        if not self.risks:
            return None

        return max(self.risks, key=lambda risk: risk.exposure())


# =============================================================================
# 8. SOFTWARE DELIVERY QUALITY
# =============================================================================


class DeploymentError(Exception):
    """Custom exception representing a deployment failure."""


@dataclass
class Deployment:
    version: str
    passed_tests: bool
    security_review_passed: bool
    rollback_available: bool
    status: str = "Pending"


class ReleaseManager:
    """
    Demonstrates basic production release checks.

    Production systems require stronger controls depending on risk,
    regulation, system criticality, and organizational context.
    """

    def deploy(self, deployment: Deployment) -> str:
        """
        Prevent deployment if critical quality gates fail.
        """

        if not deployment.passed_tests:
            deployment.status = "Rejected"
            raise DeploymentError(
                "Deployment rejected because automated tests failed."
            )

        if not deployment.security_review_passed:
            deployment.status = "Rejected"
            raise DeploymentError(
                "Deployment rejected because security review failed."
            )

        if not deployment.rollback_available:
            deployment.status = "Rejected"
            raise DeploymentError(
                "Deployment rejected because no rollback mechanism exists."
            )

        deployment.status = "Deployed"
        return f"Version {deployment.version} deployed successfully."


# =============================================================================
# 9. DESIGN ORGANIZATION
# =============================================================================


@dataclass
class UserJourneyStep:
    action: str
    friction_score: float
    description: str


class DesignTeam:
    """
    Design focuses on the interaction between people and products.

    Design disciplines may include:
    - User experience design
    - User interface design
    - User research
    - Content design
    - Interaction design
    - Service design
    - Design systems

    Design is not limited to visual appearance.
    """

    def __init__(self, name: str):
        self.name = name

    def journey_friction_score(
        self,
        journey: List[UserJourneyStep],
    ) -> float:
        """
        Calculates average friction across a journey.

        Edge case:
        An empty journey has no measurable friction.
        """

        if not journey:
            return 0.0

        return mean(step.friction_score for step in journey)

    def identify_high_friction_steps(
        self,
        journey: List[UserJourneyStep],
        threshold: float,
    ) -> List[UserJourneyStep]:
        return [
            step
            for step in journey
            if step.friction_score >= threshold
        ]


# =============================================================================
# 10. PRODUCT DESIGN AND USER RESEARCH
# =============================================================================


@dataclass
class ResearchFinding:
    participant_group: str
    observation: str
    frequency: int
    confidence: float


class UserResearchRepository:
    """
    Stores research findings.

    Common research methods:
    - Interviews
    - Surveys
    - Usability tests
    - Diary studies
    - Contextual inquiry
    - Analytics analysis

    Important limitation:
    Research samples may not represent the entire market.
    """

    def __init__(self):
        self.findings: List[ResearchFinding] = []

    def add_finding(self, finding: ResearchFinding) -> None:
        self.findings.append(finding)

    def strongest_findings(
        self,
        minimum_confidence: float,
    ) -> List[ResearchFinding]:
        return sorted(
            [
                finding
                for finding in self.findings
                if finding.confidence >= minimum_confidence
            ],
            key=lambda finding: finding.frequency,
            reverse=True,
        )


# =============================================================================
# 11. MARKETING ORGANIZATION
# =============================================================================


@dataclass
class MarketSegment:
    name: str
    market_size: int
    willingness_to_pay: float
    acquisition_cost: float


@dataclass
class Positioning:
    target_customer: str
    category: str
    key_benefit: str
    differentiation: str


class MarketingTeam:
    """
    Marketing connects product value with market understanding.

    Responsibilities may include:
    - Positioning
    - Messaging
    - Segmentation
    - Product marketing
    - Demand generation
    - Brand
    - Campaigns
    - Competitive intelligence
    """

    def __init__(self, name: str):
        self.name = name

    def customer_acquisition_cost(
        self,
        marketing_spend: float,
        customers_acquired: int,
    ) -> float:
        """
        CAC = Marketing spend / New customers acquired
        """

        if customers_acquired <= 0:
            raise ValueError(
                "Customers acquired must be greater than zero."
            )

        return marketing_spend / customers_acquired

    def conversion_rate(
        self,
        conversions: int,
        visitors: int,
    ) -> float:
        """
        Conversion rate expressed as a decimal.
        """

        if visitors <= 0:
            return 0.0

        if conversions < 0:
            raise ValueError("Conversions cannot be negative.")

        return conversions / visitors

    def evaluate_segment(
        self,
        segment: MarketSegment,
    ) -> float:
        """
        Simplified segment attractiveness score.

        Larger market size and willingness to pay increase attractiveness.
        Higher acquisition cost reduces attractiveness.
        """

        if segment.acquisition_cost <= 0:
            raise ValueError(
                "Acquisition cost must be greater than zero."
            )

        return (
            segment.market_size
            * segment.willingness_to_pay
            / segment.acquisition_cost
        )


# =============================================================================
# 12. SALES ORGANIZATION
# =============================================================================


class DealStage(Enum):
    PROSPECTING = "Prospecting"
    QUALIFICATION = "Qualification"
    DISCOVERY = "Discovery"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"


@dataclass
class SalesDeal:
    customer_name: str
    deal_value: float
    stage: DealStage
    probability: float


class SalesTeam:
    """
    Sales helps customers evaluate and purchase products.

    Sales complexity varies significantly.

    Common sales models:
    - Self-service
    - Inside sales
    - Field sales
    - Enterprise sales
    - Partner sales
    """

    def __init__(self, name: str):
        self.name = name
        self.pipeline: List[SalesDeal] = []

    def add_deal(self, deal: SalesDeal) -> None:
        if deal.deal_value < 0:
            raise ValueError("Deal value cannot be negative.")

        if not 0 <= deal.probability <= 1:
            raise ValueError(
                "Deal probability must be between 0 and 1."
            )

        self.pipeline.append(deal)

    def total_pipeline_value(self) -> float:
        return sum(
            deal.deal_value
            for deal in self.pipeline
            if deal.stage not in {
                DealStage.CLOSED_WON,
                DealStage.CLOSED_LOST,
            }
        )

    def weighted_pipeline_value(self) -> float:
        """
        Expected pipeline value.

        Expected value does not guarantee future revenue.
        """

        return sum(
            deal.deal_value * deal.probability
            for deal in self.pipeline
            if deal.stage not in {
                DealStage.CLOSED_WON,
                DealStage.CLOSED_LOST,
            }
        )

    def win_rate(self) -> float:
        closed_deals = [
            deal
            for deal in self.pipeline
            if deal.stage in {
                DealStage.CLOSED_WON,
                DealStage.CLOSED_LOST,
            }
        ]

        if not closed_deals:
            return 0.0

        won_deals = sum(
            1
            for deal in closed_deals
            if deal.stage == DealStage.CLOSED_WON
        )

        return won_deals / len(closed_deals)


# =============================================================================
# 13. CUSTOMER SUCCESS
# =============================================================================


class CustomerSuccessTeam:
    """
    Customer Success focuses on customers obtaining value from the product.

    Customer support and customer success are related but distinct.

    Customer Support:
        Primarily resolves questions and problems.

    Customer Success:
        Focuses more broadly on adoption, value realization, retention,
        expansion, and long-term customer outcomes.

    In smaller companies, one team may perform both functions.
    """

    def __init__(self, name: str):
        self.name = name
        self.customers: List[Customer] = []

    def add_customer(self, customer: Customer) -> None:
        self.customers.append(customer)

    def average_satisfaction(self) -> float:
        if not self.customers:
            return 0.0

        return mean(
            customer.satisfaction_score
            for customer in self.customers
        )

    def identify_at_risk_customers(
        self,
        risk_threshold: float,
    ) -> List[Customer]:
        return [
            customer
            for customer in self.customers
            if customer.churn_risk >= risk_threshold
        ]

    def net_revenue_retention(
        self,
        starting_revenue: float,
        expansion_revenue: float,
        contraction_revenue: float,
        churned_revenue: float,
    ) -> float:
        """
        NRR =
            (Starting Revenue
             + Expansion
             - Contraction
             - Churn)
            / Starting Revenue

        NRR can exceed 100% when expansion is greater than revenue lost.
        """

        if starting_revenue <= 0:
            raise ValueError(
                "Starting revenue must be greater than zero."
            )

        ending_revenue = (
            starting_revenue
            + expansion_revenue
            - contraction_revenue
            - churned_revenue
        )

        return ending_revenue / starting_revenue


# =============================================================================
# 14. OPERATIONS
# =============================================================================


@dataclass
class OperationalProcess:
    name: str
    steps: List[str]
    owner: str
    documented: bool


class OperationsTeam:
    """
    Operations enables repeatable and scalable organizational execution.

    Examples:
    - Product Operations
    - Revenue Operations
    - Business Operations
    - Sales Operations
    - Customer Operations
    - Engineering Operations

    Operations becomes increasingly important as organizational complexity grows.
    """

    def __init__(self, name: str):
        self.name = name
        self.processes: List[OperationalProcess] = []

    def add_process(self, process: OperationalProcess) -> None:
        self.processes.append(process)

    def undocumented_processes(self) -> List[OperationalProcess]:
        return [
            process
            for process in self.processes
            if not process.documented
        ]

    def validate_process_ownership(self) -> List[str]:
        """
        Processes without ownership often fail because no one is accountable for
        maintaining or improving them.
        """

        issues = []

        for process in self.processes:
            if not process.owner.strip():
                issues.append(
                    f"Process '{process.name}' has no owner."
                )

        return issues


# =============================================================================
# 15. EXECUTIVE LEADERSHIP
# =============================================================================


@dataclass
class StrategicInvestment:
    name: str
    expected_return: float
    risk: float
    resource_cost: float
    strategic_alignment: float


class ExecutiveLeadership:
    """
    Executive leadership typically operates at a portfolio and organizational
    level.

    Key responsibilities:
    - Vision and strategy
    - Capital allocation
    - Organizational design
    - Executive decision-making
    - Risk management
    - Long-term trade-offs
    """

    def __init__(self, leadership_group: str):
        self.leadership_group = leadership_group

    def investment_score(
        self,
        investment: StrategicInvestment,
    ) -> float:
        """
        Simplified strategic investment scoring model.

        Higher expected return and alignment are positive.
        Higher risk and cost reduce the score.

        Real investment decisions involve uncertainty, timing, optionality,
        competitive dynamics, cash constraints, and organizational capability.
        """

        denominator = (
            investment.risk
            + investment.resource_cost
        )

        if denominator <= 0:
            raise ValueError(
                "Combined risk and resource cost must be greater than zero."
            )

        return (
            investment.expected_return
            * investment.strategic_alignment
            / denominator
        )


# =============================================================================
# 16. CROSS-FUNCTIONAL COLLABORATION
# =============================================================================


@dataclass
class Decision:
    """
    Represents an organizational decision.

    Decision quality depends on:
    - Clear decision ownership
    - Relevant expertise
    - Timely information
    - Appropriate authority
    - Explicit trade-offs
    """

    description: str
    accountable: str
    consulted: List[str]
    informed: List[str]


class DecisionFramework:
    """
    Demonstrates a simplified RACI-like decision structure.

    RACI:
    - Responsible: Performs the work
    - Accountable: Ultimately answerable
    - Consulted: Provides input
    - Informed: Kept aware

    Important warning:
    Excessively complex responsibility matrices can slow organizations down.
    """

    def __init__(self):
        self.decisions: List[Decision] = []

    def add_decision(self, decision: Decision) -> None:
        if not decision.accountable.strip():
            raise ValueError(
                "Every important decision should have an accountable owner."
            )

        self.decisions.append(decision)

    def find_decisions_by_owner(
        self,
        owner: str,
    ) -> List[Decision]:
        return [
            decision
            for decision in self.decisions
            if decision.accountable == owner
        ]


# =============================================================================
# 17. PRODUCT DEVELOPMENT LIFECYCLE
# =============================================================================


class ProductInitiative:
    """
    Represents an initiative moving through the product lifecycle.

    Product development is rarely perfectly linear.

    Discovery may continue during development.
    Customer feedback may require changes after launch.
    Engineering constraints may change the product design.

    This class models stages for teaching purposes.
    """

    VALID_TRANSITIONS = {
        ProductLifecycleStage.DISCOVERY: {
            ProductLifecycleStage.VALIDATION,
        },
        ProductLifecycleStage.VALIDATION: {
            ProductLifecycleStage.DEVELOPMENT,
            ProductLifecycleStage.DISCOVERY,
        },
        ProductLifecycleStage.DEVELOPMENT: {
            ProductLifecycleStage.LAUNCH,
            ProductLifecycleStage.VALIDATION,
        },
        ProductLifecycleStage.LAUNCH: {
            ProductLifecycleStage.GROWTH,
        },
        ProductLifecycleStage.GROWTH: {
            ProductLifecycleStage.MATURITY,
        },
        ProductLifecycleStage.MATURITY: {
            ProductLifecycleStage.RETIREMENT,
            ProductLifecycleStage.GROWTH,
        },
        ProductLifecycleStage.RETIREMENT: set(),
    }

    def __init__(
        self,
        name: str,
        stage: ProductLifecycleStage = ProductLifecycleStage.DISCOVERY,
    ):
        self.name = name
        self.stage = stage
        self.history = [stage]

    def transition_to(
        self,
        new_stage: ProductLifecycleStage,
    ) -> None:
        """
        Prevent invalid lifecycle transitions.
        """

        allowed = self.VALID_TRANSITIONS[self.stage]

        if new_stage not in allowed:
            raise ValueError(
                f"Invalid transition from {self.stage.value} "
                f"to {new_stage.value}."
            )

        self.stage = new_stage
        self.history.append(new_stage)


# =============================================================================
# 18. PRODUCT METRICS AND THE PRODUCT FUNNEL
# =============================================================================


class ProductAnalytics:
    """
    Demonstrates a simplified product funnel.

    A common funnel might be:

        Acquisition
            ↓
        Activation
            ↓
        Engagement
            ↓
        Retention
            ↓
        Revenue

    Metric definitions must be consistent.
    A metric becomes misleading when different teams calculate it differently.
    """

    @staticmethod
    def retention_rate(
        retained_users: int,
        starting_users: int,
    ) -> float:
        if starting_users <= 0:
            return 0.0

        if retained_users < 0:
            raise ValueError(
                "Retained users cannot be negative."
            )

        return retained_users / starting_users

    @staticmethod
    def activation_rate(
        activated_users: int,
        new_users: int,
    ) -> float:
        if new_users <= 0:
            return 0.0

        return activated_users / new_users

    @staticmethod
    def churn_rate(
        churned_customers: int,
        starting_customers: int,
    ) -> float:
        if starting_customers <= 0:
            return 0.0

        return churned_customers / starting_customers


# =============================================================================
# 19. EXPERIMENTATION
# =============================================================================


@dataclass
class ExperimentResult:
    name: str
    control_conversions: int
    control_visitors: int
    treatment_conversions: int
    treatment_visitors: int


class ExperimentAnalyzer:
    """
    Provides a simple experiment comparison.

    This does not replace formal statistical analysis.

    A production experimentation system may require:
    - Randomization
    - Sample size planning
    - Statistical significance testing
    - Confidence intervals
    - Guardrail metrics
    - Multiple-testing controls
    """

    @staticmethod
    def conversion_rate(
        conversions: int,
        visitors: int,
    ) -> float:
        if visitors <= 0:
            return 0.0

        return conversions / visitors

    def analyze(
        self,
        result: ExperimentResult,
    ) -> Dict[str, float]:
        control_rate = self.conversion_rate(
            result.control_conversions,
            result.control_visitors,
        )

        treatment_rate = self.conversion_rate(
            result.treatment_conversions,
            result.treatment_visitors,
        )

        absolute_difference = treatment_rate - control_rate

        relative_lift = 0.0

        if control_rate > 0:
            relative_lift = (
                treatment_rate - control_rate
            ) / control_rate

        return {
            "control_rate": control_rate,
            "treatment_rate": treatment_rate,
            "absolute_difference": absolute_difference,
            "relative_lift": relative_lift,
        }


# =============================================================================
# 20. TECHNICAL DEBT AND PRODUCT TRADE-OFFS
# =============================================================================


@dataclass
class ProductTradeOff:
    option_a: str
    option_b: str
    speed_score_a: float
    quality_score_a: float
    cost_score_a: float
    speed_score_b: float
    quality_score_b: float
    cost_score_b: float


def compare_trade_off(
    trade_off: ProductTradeOff,
) -> Dict[str, float]:
    """
    Demonstrates weighted trade-off analysis.

    Assumption:
    Higher scores are better.

    Weights:
    - Speed: 30%
    - Quality: 40%
    - Cost efficiency: 30%

    Organizations should change weights according to strategic context.
    """

    score_a = (
        trade_off.speed_score_a * 0.30
        + trade_off.quality_score_a * 0.40
        + trade_off.cost_score_a * 0.30
    )

    score_b = (
        trade_off.speed_score_b * 0.30
        + trade_off.quality_score_b * 0.40
        + trade_off.cost_score_b * 0.30
    )

    return {
        trade_off.option_a: score_a,
        trade_off.option_b: score_b,
    }


# =============================================================================
# 21. ORGANIZATIONAL DEPENDENCIES
# =============================================================================


class DependencyGraph:
    """
    Represents dependencies between teams or work items.

    Dependencies are important because organizational delays often occur at
    interfaces between teams rather than within individual teams.
    """

    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)

    def add_dependency(
        self,
        work_item: str,
        dependency: str,
    ) -> None:
        """
        work_item depends on dependency.
        """

        self.graph[work_item].add(dependency)

        # Ensure dependency exists as a graph node.
        self.graph.setdefault(dependency, set())

    def dependencies_of(
        self,
        work_item: str,
    ) -> Set[str]:
        return self.graph.get(work_item, set())

    def has_cycle(self) -> bool:
        """
        Detect circular dependencies using depth-first search.

        A cycle occurs when:
            A depends on B
            B depends on C
            C depends on A

        Circular dependencies can create planning deadlocks.
        """

        visited = set()
        active_path = set()

        def visit(node: str) -> bool:
            if node in active_path:
                return True

            if node in visited:
                return False

            visited.add(node)
            active_path.add(node)

            for dependency in self.graph[node]:
                if visit(dependency):
                    return True

            active_path.remove(node)

            return False

        return any(
            visit(node)
            for node in self.graph
        )


# =============================================================================
# 22. PRODUCT ORGANIZATION OPERATING MODEL
# =============================================================================


@dataclass
class OperatingCadence:
    """
    Cadences provide predictable coordination.

    Examples:
    - Daily engineering synchronization
    - Weekly product review
    - Monthly business review
    - Quarterly planning
    - Annual strategy review

    Excessive meetings can reduce execution time.
    The objective is coordination, not meeting volume.
    """

    name: str
    frequency: str
    participants: List[str]
    purpose: str


class ProductOrganization:
    """
    Integrates the major functions into one organizational model.
    """

    def __init__(self, company_name: str):
        self.company_name = company_name
        self.teams: Dict[str, object] = {}
        self.metrics: List[ProductMetric] = []
        self.cadences: List[OperatingCadence] = []

    def register_team(
        self,
        team_name: str,
        team: object,
    ) -> None:
        if team_name in self.teams:
            raise ValueError(
                f"Team '{team_name}' is already registered."
            )

        self.teams[team_name] = team

    def add_metric(
        self,
        metric: ProductMetric,
    ) -> None:
        self.metrics.append(metric)

    def add_cadence(
        self,
        cadence: OperatingCadence,
    ) -> None:
        self.cadences.append(cadence)

    def performance_dashboard(
        self,
    ) -> Dict[str, float]:
        """
        Returns metric achievement ratios.
        """

        return {
            metric.name: metric.achievement_ratio()
            for metric in self.metrics
        }


# =============================================================================
# 23. PRODUCT, ENGINEERING, DESIGN TRIAD
# =============================================================================


class ProductEngineeringDesignTriad:
    """
    A common cross-functional collaboration model.

    Product:
        Focuses on customer, business, problem, and outcome.

    Engineering:
        Focuses on technical feasibility, architecture, quality, and risk.

    Design:
        Focuses on user behavior, usability, accessibility, and experience.

    Effective collaboration requires disagreement when evidence differs.
    The objective is not automatic consensus. The objective is better decisions.
    """

    def evaluate_solution(
        self,
        customer_value: float,
        technical_feasibility: float,
        usability: float,
    ) -> float:
        """
        Simplified balanced solution score.

        Each dimension is weighted equally.

        A solution with excellent customer value but extremely poor technical
        feasibility may fail.

        A technically excellent solution with poor usability may also fail.
        """

        values = [
            customer_value,
            technical_feasibility,
            usability,
        ]

        if any(value < 0 or value > 10 for value in values):
            raise ValueError(
                "All evaluation scores must be between 0 and 10."
            )

        return mean(values)


# =============================================================================
# 24. GO-TO-MARKET COLLABORATION
# =============================================================================


class GoToMarketReadiness:
    """
    Product launches require coordination beyond software development.

    Product readiness may include:
    - Functional completeness
    - Documentation
    - Pricing
    - Positioning
    - Sales enablement
    - Customer support readiness
    - Analytics
    - Operational readiness
    """

    REQUIRED_AREAS = {
        "product",
        "engineering",
        "design",
        "marketing",
        "sales",
        "customer_success",
        "operations",
    }

    def __init__(self):
        self.readiness: Dict[str, bool] = {}

    def mark_ready(
        self,
        area: str,
        ready: bool,
    ) -> None:
        if area not in self.REQUIRED_AREAS:
            raise ValueError(
                f"Unknown readiness area: {area}"
            )

        self.readiness[area] = ready

    def launch_ready(self) -> bool:
        return all(
            self.readiness.get(area, False)
            for area in self.REQUIRED_AREAS
        )

    def blockers(self) -> List[str]:
        return [
            area
            for area in self.REQUIRED_AREAS
            if not self.readiness.get(area, False)
        ]


# =============================================================================
# 25. COMMON ORGANIZATIONAL FAILURE MODES
# =============================================================================


class OrganizationalHealthCheck:
    """
    Detects simplified organizational warning signs.

    Common failure modes include:
    - Product building without validated customer problems
    - Engineering being involved too late
    - Design being treated only as visual styling
    - Marketing learning about launches at the last moment
    - Sales making promises unsupported by the product
    - Customer feedback not reaching product teams
    - Operations becoming bureaucracy instead of enablement
    - Leadership changing priorities too frequently
    """

    def __init__(self):
        self.warnings: List[str] = []

    def check_feature(
        self,
        feature: Feature,
    ) -> None:
        if feature.confidence < 0.3:
            self.warnings.append(
                f"{feature.name}: low confidence in expected impact."
            )

        if feature.estimated_effort > 50:
            self.warnings.append(
                f"{feature.name}: unusually high implementation effort."
            )

        if not feature.description.strip():
            self.warnings.append(
                f"{feature.name}: missing feature description."
            )

    def check_metric(
        self,
        metric: ProductMetric,
    ) -> None:
        if metric.target <= 0:
            self.warnings.append(
                f"{metric.name}: metric target must be greater than zero."
            )


# =============================================================================
# 26. PRODUCTION CONSIDERATIONS
# =============================================================================


class ProductionChecklist:
    """
    Production systems require more than feature functionality.

    Common concerns:
    - Reliability
    - Scalability
    - Security
    - Observability
    - Data protection
    - Incident response
    - Backup and recovery
    - Performance
    """

    def __init__(
        self,
        monitoring: bool,
        logging: bool,
        backups: bool,
        access_controls: bool,
        incident_response_plan: bool,
    ):
        self.monitoring = monitoring
        self.logging = logging
        self.backups = backups
        self.access_controls = access_controls
        self.incident_response_plan = incident_response_plan

    def missing_controls(self) -> List[str]:
        controls = {
            "Monitoring": self.monitoring,
            "Logging": self.logging,
            "Backups": self.backups,
            "Access Controls": self.access_controls,
            "Incident Response Plan": self.incident_response_plan,
        }

        return [
            control
            for control, implemented in controls.items()
            if not implemented
        ]

    def production_ready(self) -> bool:
        return not self.missing_controls()


# =============================================================================
# 27. END-TO-END SIMULATION
# =============================================================================


def run_product_organization_simulation() -> None:
    """
    Demonstrates how the major organizational functions interact.
    """

    print("=" * 78)
    print("PRODUCT ORGANIZATION END-TO-END SIMULATION")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # PRODUCT DISCOVERY
    # -------------------------------------------------------------------------

    product_manager = ProductManager("Asha")

    problems = [
        UserProblem(
            description=(
                "Customers spend excessive time manually creating reports."
            ),
            affected_users=5000,
            severity=9,
            evidence_strength=0.9,
            strategic_alignment=0.95,
        ),
        UserProblem(
            description=(
                "Users cannot easily customize dashboard layouts."
            ),
            affected_users=2000,
            severity=6,
            evidence_strength=0.8,
            strategic_alignment=0.7,
        ),
        UserProblem(
            description=(
                "Users want additional interface color themes."
            ),
            affected_users=1000,
            severity=3,
            evidence_strength=0.6,
            strategic_alignment=0.3,
        ),
    ]

    for problem in problems:
        product_manager.add_problem(problem)

    print("\nTOP PRODUCT PROBLEMS")

    for problem in product_manager.rank_problems():
        print(
            f"- {problem.description} "
            f"| Opportunity Score: "
            f"{product_manager.opportunity_score(problem):,.2f}"
        )

    # -------------------------------------------------------------------------
    # PRODUCT STRATEGY
    # -------------------------------------------------------------------------

    strategy = ProductStrategy(
        vision=(
            "Make business analytics faster and easier for operations teams."
        ),
        target_segment="Mid-market operations teams",
        strategic_problem=(
            "Manual reporting consumes excessive operational time."
        ),
        differentiation=(
            "Automated, customizable reporting with rapid setup."
        ),
        success_metrics=[
            "Report creation time",
            "Weekly active users",
            "Customer retention",
        ],
    )

    print("\nPRODUCT STRATEGY")
    print(f"Vision: {strategy.vision}")
    print(f"Target Segment: {strategy.target_segment}")
    print(f"Strategic Problem: {strategy.strategic_problem}")

    # -------------------------------------------------------------------------
    # PRODUCT ROADMAP
    # -------------------------------------------------------------------------

    automated_reporting = Feature(
        name="Automated Reporting",
        description=(
            "Generate scheduled business reports automatically."
        ),
        estimated_effort=30,
        expected_impact=9,
        confidence=0.85,
        priority=Priority.CRITICAL,
        dependencies=["Reporting API"],
    )

    reporting_api = Feature(
        name="Reporting API",
        description=(
            "Provide a reliable backend API for reporting workflows."
        ),
        estimated_effort=20,
        expected_impact=7,
        confidence=0.9,
        priority=Priority.HIGH,
    )

    dashboard_customization = Feature(
        name="Dashboard Customization",
        description=(
            "Allow users to customize analytics dashboards."
        ),
        estimated_effort=18,
        expected_impact=6,
        confidence=0.75,
    )

    for feature in [
        automated_reporting,
        reporting_api,
        dashboard_customization,
    ]:
        product_manager.add_to_roadmap(feature)

    print("\nPRIORITIZED ROADMAP")

    for feature in product_manager.prioritize_roadmap():
        print(
            f"- {feature.name} "
            f"| Effort: {feature.estimated_effort} "
            f"| Impact: {feature.expected_impact} "
            f"| Confidence: {feature.confidence}"
        )

    roadmap = Roadmap()

    for feature in product_manager.roadmap:
        roadmap.add_item(feature)

    missing_dependencies = roadmap.validate_dependencies()

    print("\nDEPENDENCY VALIDATION")

    if missing_dependencies:
        print("Missing dependencies:", missing_dependencies)
    else:
        print("All roadmap dependencies are represented.")

    # -------------------------------------------------------------------------
    # PRODUCT TEAM
    # -------------------------------------------------------------------------

    product_team = CrossFunctionalTeam(
        name="Reporting Experience Team",
        mission=(
            "Reduce customer reporting effort through automation."
        ),
        members=[
            TeamMember(
                name="Asha",
                function="Product",
                skills=[
                    "Strategy",
                    "Research",
                    "Prioritization",
                ],
            ),
            TeamMember(
                name="Rahul",
                function="Engineering",
                skills=[
                    "Backend",
                    "APIs",
                    "Architecture",
                ],
            ),
            TeamMember(
                name="Meera",
                function="Design",
                skills=[
                    "UX Research",
                    "Interaction Design",
                ],
            ),
        ],
    )

    print("\nCROSS-FUNCTIONAL TEAM")
    print("Functions:", product_team.functions_present())
    print(
        "Missing Core Functions:",
        product_team.missing_core_functions(),
    )

    # -------------------------------------------------------------------------
    # ENGINEERING
    # -------------------------------------------------------------------------

    engineering = EngineeringTeam("Platform Engineering")

    engineering.add_risk(
        TechnicalRisk(
            description=(
                "Reporting queries may create high database load."
            ),
            probability=0.7,
            impact=9,
        )
    )

    engineering.add_risk(
        TechnicalRisk(
            description=(
                "Third-party data integration may be unreliable."
            ),
            probability=0.4,
            impact=6,
        )
    )

    highest_risk = engineering.highest_risk()

    print("\nENGINEERING RISK")

    if highest_risk:
        print(
            f"Highest Risk: {highest_risk.description} "
            f"| Exposure: {highest_risk.exposure():.2f}"
        )

    estimated_cycles = engineering.estimate_delivery_time(
        automated_reporting,
        team_capacity_points=15,
    )

    print(
        "Estimated Delivery Cycles:",
        f"{estimated_cycles:.2f}",
    )

    # -------------------------------------------------------------------------
    # DESIGN
    # -------------------------------------------------------------------------

    design = DesignTeam("Product Design")

    journey = [
        UserJourneyStep(
            action="Select data",
            friction_score=3,
            description="User selects report data.",
        ),
        UserJourneyStep(
            action="Configure report",
            friction_score=8,
            description="User manually configures report parameters.",
        ),
        UserJourneyStep(
            action="Generate report",
            friction_score=4,
            description="User generates report.",
        ),
        UserJourneyStep(
            action="Share report",
            friction_score=7,
            description="User manually exports and sends report.",
        ),
    ]

    print("\nUSER EXPERIENCE ANALYSIS")
    print(
        "Average Friction:",
        f"{design.journey_friction_score(journey):.2f}",
    )

    high_friction_steps = design.identify_high_friction_steps(
        journey,
        threshold=7,
    )

    for step in high_friction_steps:
        print(
            f"High Friction Step: {step.action} "
            f"| Score: {step.friction_score}"
        )

    # -------------------------------------------------------------------------
    # MARKETING
    # -------------------------------------------------------------------------

    marketing = MarketingTeam("Product Marketing")

    enterprise_segment = MarketSegment(
        name="Mid-Market Operations",
        market_size=100000,
        willingness_to_pay=8,
        acquisition_cost=500,
    )

    attractiveness = marketing.evaluate_segment(
        enterprise_segment
    )

    print("\nMARKET ANALYSIS")
    print(
        f"Segment: {enterprise_segment.name} "
        f"| Attractiveness Score: {attractiveness:.2f}"
    )

    cac = marketing.customer_acquisition_cost(
        marketing_spend=50000,
        customers_acquired=100,
    )

    print(f"Customer Acquisition Cost: {cac:.2f}")

    # -------------------------------------------------------------------------
    # SALES
    # -------------------------------------------------------------------------

    sales = SalesTeam("Enterprise Sales")

    sales.add_deal(
        SalesDeal(
            customer_name="Alpha Industries",
            deal_value=120000,
            stage=DealStage.PROPOSAL,
            probability=0.6,
        )
    )

    sales.add_deal(
        SalesDeal(
            customer_name="Beta Logistics",
            deal_value=80000,
            stage=DealStage.NEGOTIATION,
            probability=0.75,
        )
    )

    sales.add_deal(
        SalesDeal(
            customer_name="Gamma Retail",
            deal_value=50000,
            stage=DealStage.CLOSED_WON,
            probability=1.0,
        )
    )

    print("\nSALES PIPELINE")
    print(
        f"Open Pipeline Value: "
        f"{sales.total_pipeline_value():,.2f}"
    )

    print(
        f"Weighted Pipeline Value: "
        f"{sales.weighted_pipeline_value():,.2f}"
    )

    print(
        f"Win Rate: {sales.win_rate():.2%}"
    )

    # -------------------------------------------------------------------------
    # CUSTOMER SUCCESS
    # -------------------------------------------------------------------------

    customer_success = CustomerSuccessTeam(
        "Customer Success"
    )

    customer_success.add_customer(
        Customer(
            name="Alpha Industries",
            segment="Mid-Market",
            annual_revenue=120000,
            active_users=500,
            satisfaction_score=8.5,
            churn_risk=0.15,
        )
    )

    customer_success.add_customer(
        Customer(
            name="Delta Manufacturing",
            segment="Mid-Market",
            annual_revenue=70000,
            active_users=120,
            satisfaction_score=5.5,
            churn_risk=0.75,
        )
    )

    customer_success.add_customer(
        Customer(
            name="Omega Services",
            segment="SMB",
            annual_revenue=25000,
            active_users=50,
            satisfaction_score=7.8,
            churn_risk=0.3,
        )
    )

    print("\nCUSTOMER SUCCESS")
    print(
        "Average Satisfaction:",
        f"{customer_success.average_satisfaction():.2f}",
    )

    at_risk = customer_success.identify_at_risk_customers(
        risk_threshold=0.6
    )

    for customer in at_risk:
        print(
            f"At Risk Customer: {customer.name} "
            f"| Churn Risk: {customer.churn_risk:.2f}"
        )

    nrr = customer_success.net_revenue_retention(
        starting_revenue=1000000,
        expansion_revenue=180000,
        contraction_revenue=50000,
        churned_revenue=70000,
    )

    print(f"Net Revenue Retention: {nrr:.2%}")

    # -------------------------------------------------------------------------
    # OPERATIONS
    # -------------------------------------------------------------------------

    operations = OperationsTeam("Product Operations")

    operations.add_process(
        OperationalProcess(
            name="Product Feedback Intake",
            steps=[
                "Collect feedback",
                "Classify feedback",
                "Review trends",
                "Share insights",
            ],
            owner="Product Operations Lead",
            documented=True,
        )
    )

    operations.add_process(
        OperationalProcess(
            name="Launch Readiness Review",
            steps=[
                "Review product readiness",
                "Review GTM readiness",
                "Confirm support readiness",
            ],
            owner="",
            documented=False,
        )
    )

    print("\nOPERATIONS")

    for process in operations.undocumented_processes():
        print(
            f"Undocumented Process: {process.name}"
        )

    for issue in operations.validate_process_ownership():
        print(issue)

    # -------------------------------------------------------------------------
    # EXECUTIVE LEADERSHIP
    # -------------------------------------------------------------------------

    leadership = ExecutiveLeadership(
        "Executive Leadership Team"
    )

    investments = [
        StrategicInvestment(
            name="Automated Reporting",
            expected_return=9,
            risk=4,
            resource_cost=5,
            strategic_alignment=0.95,
        ),
        StrategicInvestment(
            name="International Expansion",
            expected_return=10,
            risk=8,
            resource_cost=9,
            strategic_alignment=0.7,
        ),
        StrategicInvestment(
            name="New Collaboration Module",
            expected_return=7,
            risk=5,
            resource_cost=6,
            strategic_alignment=0.6,
        ),
    ]

    print("\nSTRATEGIC INVESTMENT PRIORITIES")

    ranked_investments = sorted(
        investments,
        key=leadership.investment_score,
        reverse=True,
    )

    for investment in ranked_investments:
        score = leadership.investment_score(
            investment
        )

        print(
            f"- {investment.name}: "
            f"{score:.2f}"
        )

    # -------------------------------------------------------------------------
    # PRODUCT-ENGINEERING-DESIGN TRIAD
    # -------------------------------------------------------------------------

    triad = ProductEngineeringDesignTriad()

    solution_score = triad.evaluate_solution(
        customer_value=9,
        technical_feasibility=8,
        usability=9,
    )

    print("\nPRODUCT-ENGINEERING-DESIGN TRIAD")
    print(
        f"Balanced Solution Score: "
        f"{solution_score:.2f}/10"
    )

    # -------------------------------------------------------------------------
    # GO-TO-MARKET READINESS
    # -------------------------------------------------------------------------

    launch = GoToMarketReadiness()

    readiness_status = {
        "product": True,
        "engineering": True,
        "design": True,
        "marketing": True,
        "sales": True,
        "customer_success": False,
        "operations": True,
    }

    for area, ready in readiness_status.items():
        launch.mark_ready(area, ready)

    print("\nGO-TO-MARKET READINESS")
    print("Launch Ready:", launch.launch_ready())
    print("Launch Blockers:", launch.blockers())

    # -------------------------------------------------------------------------
    # ANALYTICS
    # -------------------------------------------------------------------------

    print("\nPRODUCT ANALYTICS")

    activation = ProductAnalytics.activation_rate(
        activated_users=800,
        new_users=1000,
    )

    retention = ProductAnalytics.retention_rate(
        retained_users=720,
        starting_users=900,
    )

    churn = ProductAnalytics.churn_rate(
        churned_customers=15,
        starting_customers=300,
    )

    print(f"Activation Rate: {activation:.2%}")
    print(f"Retention Rate: {retention:.2%}")
    print(f"Churn Rate: {churn:.2%}")

    # -------------------------------------------------------------------------
    # EXPERIMENTATION
    # -------------------------------------------------------------------------

    experiment = ExperimentAnalyzer()

    result = experiment.analyze(
        ExperimentResult(
            name="Simplified Report Creation",
            control_conversions=120,
            control_visitors=1000,
            treatment_conversions=160,
            treatment_visitors=1000,
        )
    )

    print("\nEXPERIMENT ANALYSIS")

    for metric_name, value in result.items():
        print(
            f"{metric_name}: {value:.4f}"
        )

    # -------------------------------------------------------------------------
    # DEPENDENCY MANAGEMENT
    # -------------------------------------------------------------------------

    dependencies = DependencyGraph()

    dependencies.add_dependency(
        "Marketing Launch",
        "Product Release",
    )

    dependencies.add_dependency(
        "Sales Enablement",
        "Marketing Launch",
    )

    dependencies.add_dependency(
        "Product Release",
        "Engineering Deployment",
    )

    print("\nDEPENDENCY ANALYSIS")
    print(
        "Circular Dependency Detected:",
        dependencies.has_cycle(),
    )

    # -------------------------------------------------------------------------
    # ORGANIZATIONAL HEALTH
    # -------------------------------------------------------------------------

    health_check = OrganizationalHealthCheck()

    for feature in product_manager.roadmap:
        health_check.check_feature(feature)

    metrics = [
        ProductMetric(
            name="Weekly Active Users",
            value=12000,
            target=15000,
            unit="users",
        ),
        ProductMetric(
            name="Retention Rate",
            value=0.82,
            target=0.85,
            unit="ratio",
        ),
    ]

    for metric in metrics:
        health_check.check_metric(metric)

    print("\nORGANIZATIONAL HEALTH WARNINGS")

    if health_check.warnings:
        for warning in health_check.warnings:
            print("-", warning)
    else:
        print("No simplified warning conditions detected.")

    # -------------------------------------------------------------------------
    # ORGANIZATIONAL DASHBOARD
    # -------------------------------------------------------------------------

    organization = ProductOrganization("NexaCloud")

    organization.register_team(
        "Product",
        product_manager,
    )

    organization.register_team(
        "Engineering",
        engineering,
    )

    organization.register_team(
        "Design",
        design,
    )

    organization.register_team(
        "Marketing",
        marketing,
    )

    organization.register_team(
        "Sales",
        sales,
    )

    organization.register_team(
        "Customer Success",
        customer_success,
    )

    organization.register_team(
        "Operations",
        operations,
    )

    organization.register_team(
        "Leadership",
        leadership,
    )

    for metric in metrics:
        organization.add_metric(metric)

    organization.add_cadence(
        OperatingCadence(
            name="Weekly Product Review",
            frequency="Weekly",
            participants=[
                "Product",
                "Engineering",
                "Design",
            ],
            purpose=(
                "Review progress, risks, evidence, and decisions."
            ),
        )
    )

    organization.add_cadence(
        OperatingCadence(
            name="Monthly Business Review",
            frequency="Monthly",
            participants=[
                "Product",
                "Marketing",
                "Sales",
                "Customer Success",
                "Leadership",
            ],
            purpose=(
                "Review product and business performance."
            ),
        )
    )

    print("\nORGANIZATIONAL DASHBOARD")

    for metric_name, achievement in (
        organization.performance_dashboard().items()
    ):
        print(
            f"{metric_name}: "
            f"{achievement:.2%} of target"
        )

    # -------------------------------------------------------------------------
    # PRODUCTION READINESS
    # -------------------------------------------------------------------------

    production = ProductionChecklist(
        monitoring=True,
        logging=True,
        backups=True,
        access_controls=True,
        incident_response_plan=False,
    )

    print("\nPRODUCTION READINESS")
    print(
        "Production Ready:",
        production.production_ready(),
    )

    print(
        "Missing Controls:",
        production.missing_controls(),
    )

    # -------------------------------------------------------------------------
    # DEPLOYMENT EXAMPLE
    # -------------------------------------------------------------------------

    release_manager = ReleaseManager()

    deployment = Deployment(
        version="2.0.0",
        passed_tests=True,
        security_review_passed=True,
        rollback_available=True,
    )

    print("\nDEPLOYMENT")

    try:
        message = release_manager.deploy(deployment)
        print(message)
    except DeploymentError as error:
        print(
            "Deployment Failed:",
            error,
        )

    # -------------------------------------------------------------------------
    # PRODUCT LIFECYCLE
    # -------------------------------------------------------------------------

    initiative = ProductInitiative(
        "Automated Reporting"
    )

    initiative.transition_to(
        ProductLifecycleStage.VALIDATION
    )

    initiative.transition_to(
        ProductLifecycleStage.DEVELOPMENT
    )

    initiative.transition_to(
        ProductLifecycleStage.LAUNCH
    )

    print("\nPRODUCT LIFECYCLE")
    print(
        " → ".join(
            stage.value
            for stage in initiative.history
        )
    )

    # -------------------------------------------------------------------------
    # TRADE-OFF ANALYSIS
    # -------------------------------------------------------------------------

    trade_off = ProductTradeOff(
        option_a="Build Custom Reporting Engine",
        option_b="Integrate Existing Reporting Service",
        speed_score_a=4,
        quality_score_a=9,
        cost_score_a=5,
        speed_score_b=9,
        quality_score_b=6,
        cost_score_b=8,
    )

    comparison = compare_trade_off(trade_off)

    print("\nTRADE-OFF ANALYSIS")

    for option, score in comparison.items():
        print(
            f"{option}: {score:.2f}"
        )

    print("\nSIMULATION COMPLETE")


# =============================================================================
# 28. MAIN PROGRAM
# =============================================================================


def main() -> None:
    """
    Program entry point.
    """

    run_product_organization_simulation()


if __name__ == "__main__":
    main()
