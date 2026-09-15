"""
Product Discovery: Fundamentals, Problem Discovery, Customer Discovery,
Market Discovery, and Opportunity Discovery

This standalone study file teaches product discovery from beginner to advanced
level through executable Python examples.

The examples model a hypothetical product called "StudyFlow", a learning
platform for working professionals. The same discovery methods can be adapted
to consumer, B2B, fintech, SaaS, education, healthcare, and marketplace
products.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum
from math import log, sqrt
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import random
import re


# ============================================================================
# 1. PRODUCT DISCOVERY FUNDAMENTALS
# ============================================================================

print("=" * 80)
print("PRODUCT DISCOVERY")
print("=" * 80)


def explain_discovery() -> None:
    """
    Product discovery is the systematic process of reducing uncertainty about
    what should be built, for whom, why it matters, and whether a viable
    opportunity exists.

    Discovery differs from delivery:
        Discovery asks: "Are we solving the right problem?"
        Delivery asks: "Can we build the chosen solution correctly?"

    The major uncertainty areas modeled in this file are:
        - Problem: Is there a meaningful problem?
        - Customer: Who experiences it and who cares enough to act?
        - Market: How large and attractive is the surrounding market?
        - Opportunity: Is there a strategically attractive space to pursue?
        - Solution: Does a proposed intervention actually improve outcomes?
        - Business: Can value be captured sustainably?
    """
    print("\nDiscovery reduces uncertainty before substantial delivery investment.")
    print("Core questions:")
    print("  1. What problem exists?")
    print("  2. Who experiences it?")
    print("  3. How frequently and severely does it occur?")
    print("  4. What alternatives exist today?")
    print("  5. How large and attractive is the market?")
    print("  6. Which opportunity deserves investment?")
    print("  7. What evidence would justify proceeding?")


explain_discovery()


# ============================================================================
# 2. IMPORTANT TERMINOLOGY
# ============================================================================

TERMS = {
    "problem": "An undesirable condition or unmet need experienced by a person or organization.",
    "customer": "A person or organization that receives value from a product and may pay for it.",
    "user": "A person who directly interacts with or uses a product.",
    "buyer": "The person or organization responsible for purchasing.",
    "market": "A population of potential customers sharing a relevant need or category.",
    "segment": "A subgroup of customers with meaningful shared characteristics or needs.",
    "need": "An outcome or condition the customer considers important.",
    "pain": "A costly, frustrating, risky, or otherwise undesirable consequence.",
    "job_to_be_done": "The progress a customer is trying to make in a particular situation.",
    "alternative": "Any existing behavior, product, service, workaround, or inaction competing for the customer's attention.",
    "opportunity": "A validated or promising problem space where customer value and strategic or economic potential may exist.",
    "hypothesis": "A testable belief about customers, problems, markets, behavior, or outcomes.",
    "assumption": "An unverified belief required for a product decision to be valid.",
    "evidence": "Observed information that increases or decreases confidence in a hypothesis.",
    "insight": "A meaningful interpretation of evidence that changes understanding or decision-making.",
    "experiment": "A controlled or structured test designed to learn about an important uncertainty.",
    "desirability": "Whether customers want or value the proposed outcome.",
    "viability": "Whether the product can support a sustainable business or organizational outcome.",
    "feasibility": "Whether the organization can realistically build and operate the solution.",
    "usability": "How effectively users can understand and use the product.",
}

print("\nKey terminology:")
for term, definition in TERMS.items():
    print(f"- {term}: {definition}")


# ============================================================================
# 3. DISCOVERY AS AN UNCERTAINTY-REDUCTION PROCESS
# ============================================================================

@dataclass
class Hypothesis:
    statement: str
    importance: float
    confidence: float
    evidence_strength: float = 0.0

    @property
    def uncertainty(self) -> float:
        """Higher uncertainty means more discovery is required."""
        return max(0.0, 1.0 - self.confidence)

    @property
    def risk_score(self) -> float:
        """
        A simple prioritization model.

        Important assumptions with low confidence receive high scores.
        """
        return self.importance * self.uncertainty


hypotheses = [
    Hypothesis(
        "Working professionals frequently abandon courses because they cannot maintain a consistent study schedule.",
        importance=0.95,
        confidence=0.35,
    ),
    Hypothesis(
        "Customers will pay for a system that converts large courses into manageable daily plans.",
        importance=0.90,
        confidence=0.20,
    ),
    Hypothesis(
        "Existing calendar and note-taking tools are insufficient alternatives.",
        importance=0.60,
        confidence=0.50,
    ),
]

print("\nHypothesis risk:")
for hypothesis in sorted(hypotheses, key=lambda item: item.risk_score, reverse=True):
    print(
        f"{hypothesis.risk_score:.2f} | "
        f"importance={hypothesis.importance:.2f} | "
        f"confidence={hypothesis.confidence:.2f} | "
        f"{hypothesis.statement}"
    )


# ============================================================================
# 4. DISCOVERY FUNNEL
# ============================================================================

def discovery_funnel(
    observations: int,
    problems: int,
    validated_problems: int,
    opportunities: int,
    experiments: int,
) -> None:
    """
    Discovery normally narrows a broad information space.

    Example:
        many observations
            -> recurring problems
            -> validated problems
            -> attractive opportunities
            -> experiments
    """
    print("\nDiscovery funnel:")
    print(f"Observations:        {observations}")
    print(f"Potential problems:  {problems}")
    print(f"Validated problems:  {validated_problems}")
    print(f"Opportunities:       {opportunities}")
    print(f"Experiments:         {experiments}")


discovery_funnel(120, 25, 8, 3, 2)


# ============================================================================
# 5. PROBLEM DISCOVERY
# ============================================================================

@dataclass
class ProblemObservation:
    customer_id: str
    situation: str
    behavior: str
    consequence: str
    frequency_per_month: float
    severity: float
    current_solution: str
    willingness_to_change: float


observations = [
    ProblemObservation(
        "C01",
        "After work",
        "Studies inconsistently",
        "Course completion is delayed",
        18,
        7,
        "Calendar reminders",
        8,
    ),
    ProblemObservation(
        "C02",
        "After work",
        "Saves videos but rarely schedules study",
        "Knowledge remains incomplete",
        12,
        8,
        "Notes app",
        7,
    ),
    ProblemObservation(
        "C03",
        "Weekend",
        "Attempts large study sessions",
        "Feels overwhelmed and stops",
        8,
        9,
        "Spreadsheet",
        9,
    ),
    ProblemObservation(
        "C04",
        "Commute",
        "Watches short lessons",
        "Cannot maintain course sequence",
        20,
        6,
        "Video app",
        6,
    ),
]


def problem_frequency_score(items: Sequence[ProblemObservation]) -> float:
    return mean(item.frequency_per_month for item in items)


def problem_severity_score(items: Sequence[ProblemObservation]) -> float:
    return mean(item.severity for item in items)


print("\nProblem evidence:")
print(
    f"Average monthly frequency: {problem_frequency_score(observations):.1f}"
)
print(
    f"Average severity: {problem_severity_score(observations):.1f}/10"
)


# ============================================================================
# 6. PROBLEM STATEMENT
# ============================================================================

def create_problem_statement(
    customer_segment: str,
    situation: str,
    problem: str,
    impact: str,
) -> str:
    """
    A strong problem statement describes a customer, context, problem, and
    consequence without prematurely prescribing a solution.
    """
    return (
        f"{customer_segment} who are {situation} struggle with {problem}, "
        f"which results in {impact}."
    )


problem_statement = create_problem_statement(
    "Working professionals taking online courses",
    "trying to study after work",
    "turning large amounts of course content into a sustainable study routine",
    "incomplete courses, wasted subscriptions, and reduced confidence",
)

print("\nProblem statement:")
print(problem_statement)


# ============================================================================
# 7. PROBLEM VS SOLUTION FRAMING
# ============================================================================

def demonstrate_problem_vs_solution() -> None:
    """
    Bad discovery often starts with a solution and searches for evidence that
    justifies it.

    Better discovery starts with the customer situation and desired outcome.
    """
    solution_first = "Customers need an AI-powered study planner."
    problem_first = (
        "Working professionals struggle to maintain a realistic study routine "
        "when course content is large and their available time changes."
    )

    print("\nSolution-first framing:")
    print(solution_first)
    print("\nProblem-first framing:")
    print(problem_first)


demonstrate_problem_vs_solution()


# ============================================================================
# 8. CUSTOMER DISCOVERY
# ============================================================================

@dataclass
class CustomerProfile:
    customer_id: str
    role: str
    age_group: str
    goal: str
    context: str
    current_alternatives: List[str]
    pain_points: List[str]
    buying_authority: bool
    willingness_to_pay: float


customers = [
    CustomerProfile(
        "C01",
        "Data analyst",
        "25-34",
        "Learn cloud computing",
        "Full-time job",
        ["Calendar", "YouTube", "Spreadsheet"],
        ["No consistent schedule", "Forgets where to resume"],
        True,
        8,
    ),
    CustomerProfile(
        "C02",
        "Product manager",
        "25-34",
        "Improve SQL",
        "Full-time job",
        ["Notes", "Calendar"],
        ["Course feels too long", "Difficulty measuring progress"],
        True,
        7,
    ),
    CustomerProfile(
        "C03",
        "Engineer",
        "25-34",
        "Learn machine learning",
        "Full-time job",
        ["Notion", "Calendar", "Course platform"],
        ["Too much content", "Loses momentum"],
        True,
        9,
    ),
]


def customer_segmentation(
    profiles: Sequence[CustomerProfile],
) -> Dict[str, List[str]]:
    """
    Simple behavioral segmentation.

    Real segmentation should use variables that predict meaningful differences
    in needs, behavior, willingness to pay, or product usage.
    """
    segments: Dict[str, List[str]] = defaultdict(list)

    for profile in profiles:
        if profile.buying_authority and profile.willingness_to_pay >= 8:
            segment = "high-intent professionals"
        elif profile.buying_authority:
            segment = "moderate-intent professionals"
        else:
            segment = "non-buying users"

        segments[segment].append(profile.customer_id)

    return dict(segments)


print("\nCustomer segments:")
for segment, customer_ids in customer_segmentation(customers).items():
    print(f"- {segment}: {customer_ids}")


# ============================================================================
# 9. USER, CUSTOMER, BUYER, AND STAKEHOLDER
# ============================================================================

def role_distinction_example() -> Dict[str, str]:
    return {
        "user": "Employee using the learning platform",
        "customer": "Organization purchasing learning access",
        "buyer": "HR or procurement representative",
        "economic_buyer": "Person accountable for budget and financial outcome",
        "decision_maker": "Person who approves the purchase",
        "influencer": "Person who affects the purchase decision",
        "administrator": "Person who manages accounts and configuration",
    }


print("\nCustomer-role distinction:")
for role, description in role_distinction_example().items():
    print(f"- {role}: {description}")


# ============================================================================
# 10. CUSTOMER INTERVIEWING
# ============================================================================

def interview_questions() -> List[str]:
    """
    Discovery interviews should focus on real behavior and recent experiences.

    Weak question:
        "Would you use our study planner?"

    Better questions:
        Ask about what happened, what they did, what it cost, and what they
        tried before.
    """
    return [
        "Tell me about the last time you tried to complete an online course.",
        "What were you trying to accomplish?",
        "What happened when your schedule changed?",
        "What did you do next?",
        "What tools or workarounds did you use?",
        "How often does this happen?",
        "What is the consequence when it happens?",
        "What have you already tried?",
        "What did you like or dislike about those alternatives?",
        "Have you ever paid to solve this problem?",
    ]


print("\nBehavior-focused interview questions:")
for question in interview_questions():
    print(f"- {question}")


# ============================================================================
# 11. INTERVIEW BIAS
# ============================================================================

BIAS_PATTERNS = {
    "leading_question": "Wouldn't an automated planner make studying easier?",
    "hypothetical_question": "Would you pay $10 per month for this?",
    "double_barreled": "Do you find studying difficult and expensive?",
    "solution_pitch": "We have built a smart planner. What do you think?",
    "social_desirability": "You value professional development, right?",
    "recency_bias": "What was your most recent learning experience?",
}

print("\nCommon interview bias patterns:")
for bias, example in BIAS_PATTERNS.items():
    print(f"- {bias}: {example}")


# ============================================================================
# 12. CODING QUALITATIVE INTERVIEW DATA
# ============================================================================

INTERVIEW_NOTES = [
    "I have three courses open but I usually forget which lesson comes next.",
    "My meetings move around, so fixed daily reminders become annoying.",
    "I already use a calendar, but it does not understand course progress.",
    "I often save courses during sales and never finish them.",
    "When I miss two days, restarting feels difficult.",
    "I use spreadsheets to divide large courses into weekly targets.",
]


def extract_simple_themes(notes: Iterable[str]) -> Counter:
    """
    A lightweight keyword-based coding demonstration.

    Professional research uses richer qualitative coding, but the example
    illustrates the underlying process: raw observations -> codes -> themes.
    """
    themes = Counter()

    keywords = {
        "planning": ["schedule", "calendar", "divide", "targets"],
        "continuity": ["next", "restart", "miss", "progress"],
        "abandonment": ["forget", "never finish", "open"],
        "overload": ["large", "three courses"],
    }

    for note in notes:
        normalized = note.lower()
        for theme, words in keywords.items():
            if any(word in normalized for word in words):
                themes[theme] += 1

    return themes


print("\nInterview themes:")
for theme, count in extract_simple_themes(INTERVIEW_NOTES).most_common():
    print(f"- {theme}: {count}")


# ============================================================================
# 13. JOBS TO BE DONE
# ============================================================================

@dataclass
class Job:
    situation: str
    motivation: str
    desired_outcome: str


job = Job(
    situation="When my work schedule becomes unpredictable",
    motivation="I still want to make progress on a course",
    desired_outcome="I want a realistic study plan that adapts to my available time",
)

print("\nJob-to-be-done formulation:")
print(
    f"When {job.situation.lower()}, "
    f"I want to {job.motivation.lower()}, "
    f"so that {job.desired_outcome.lower()}."
)


# ============================================================================
# 14. CUSTOMER JOURNEY
# ============================================================================

@dataclass
class JourneyStage:
    stage: str
    customer_action: str
    pain: str
    evidence: str


journey = [
    JourneyStage("Discover", "Finds a course", "Too many choices", "Search behavior"),
    JourneyStage("Purchase", "Buys a course", "Uncertain value", "Purchase rate"),
    JourneyStage("Start", "Begins lessons", "Large content volume", "Activation"),
    JourneyStage("Continue", "Returns to study", "Schedule conflicts", "Weekly retention"),
    JourneyStage("Complete", "Finishes course", "Loss of momentum", "Completion rate"),
]


print("\nCustomer journey:")
for stage in journey:
    print(
        f"{stage.stage:10} | action={stage.customer_action} | "
        f"pain={stage.pain} | evidence={stage.evidence}"
    )


# ============================================================================
# 15. MARKET DISCOVERY
# ============================================================================

@dataclass
class MarketEstimate:
    total_customers: int
    annual_price: float
    addressable_percentage: float
    reachable_percentage: float

    @property
    def tam(self) -> float:
        """Theoretical total annual revenue if all relevant customers bought."""
        return self.total_customers * self.annual_price

    @property
    def sam(self) -> float:
        """Serviceable addressable market under chosen constraints."""
        return self.tam * self.addressable_percentage

    @property
    def som(self) -> float:
        """Illustrative realistically reachable share."""
        return self.sam * self.reachable_percentage


market = MarketEstimate(
    total_customers=5_000_000,
    annual_price=120.0,
    addressable_percentage=0.25,
    reachable_percentage=0.02,
)

print("\nIllustrative market sizing:")
print(f"TAM: ${market.tam:,.0f}")
print(f"SAM: ${market.sam:,.0f}")
print(f"SOM: ${market.som:,.0f}")


# ============================================================================
# 16. TOP-DOWN VS BOTTOM-UP MARKET SIZING
# ============================================================================

def top_down_market_size(
    total_population: int,
    relevant_percentage: float,
    annual_spend: float,
) -> float:
    return total_population * relevant_percentage * annual_spend


def bottom_up_market_size(
    potential_accounts: int,
    expected_customers_per_account: float,
    annual_revenue_per_customer: float,
) -> float:
    return (
        potential_accounts
        * expected_customers_per_account
        * annual_revenue_per_customer
    )


top_down = top_down_market_size(100_000_000, 0.05, 120)
bottom_up = bottom_up_market_size(20_000, 100, 120)

print("\nMarket-sizing comparison:")
print(f"Top-down estimate:   ${top_down:,.0f}")
print(f"Bottom-up estimate:  ${bottom_up:,.0f}")
print("Bottom-up estimates are often more useful for operational planning.")


# ============================================================================
# 17. MARKET SEGMENTATION
# ============================================================================

@dataclass
class Segment:
    name: str
    population: int
    pain: float
    willingness_to_pay: float
    accessibility: float
    strategic_fit: float

    def attractiveness(self) -> float:
        return (
            self.pain
            * self.willingness_to_pay
            * self.accessibility
            * self.strategic_fit
        )


segments = [
    Segment("Working professionals", 5_000_000, 9, 8, 8, 9),
    Segment("University students", 10_000_000, 6, 4, 9, 7),
    Segment("Corporate L&D teams", 50_000, 8, 9, 6, 10),
    Segment("Retired learners", 3_000_000, 4, 3, 5, 4),
]

print("\nSegment attractiveness:")
for segment in sorted(segments, key=Segment.attractiveness, reverse=True):
    print(
        f"{segment.name:25} | population={segment.population:,} | "
        f"score={segment.attractiveness():.0f}"
    )


# ============================================================================
# 18. COMPETITIVE AND ALTERNATIVE DISCOVERY
# ============================================================================

@dataclass
class Alternative:
    name: str
    price: float
    convenience: float
    effectiveness: float
    flexibility: float


alternatives = [
    Alternative("Calendar", 0, 8, 4, 6),
    Alternative("Spreadsheet", 0, 5, 6, 8),
    Alternative("Course platform", 100, 7, 7, 5),
    Alternative("Personal coach", 600, 7, 9, 8),
    Alternative("Do nothing", 0, 10, 1, 10),
]

print("\nAlternative landscape:")
for alternative in alternatives:
    print(
        f"{alternative.name:20} | price={alternative.price:4.0f} | "
        f"convenience={alternative.convenience}/10 | "
        f"effectiveness={alternative.effectiveness}/10"
    )


# ============================================================================
# 19. DIRECT AND INDIRECT COMPETITION
# ============================================================================

competition = {
    "direct": ["Adaptive study planners", "Learning productivity platforms"],
    "indirect": ["Calendars", "Spreadsheets", "Notes applications"],
    "behavioral": ["Doing nothing", "Abandoning the course", "Studying manually"],
    "internal": ["Building an internal process", "Hiring a coach"],
}

print("\nCompetitive categories:")
for category, examples in competition.items():
    print(f"- {category}: {', '.join(examples)}")


# ============================================================================
# 20. OPPORTUNITY DISCOVERY
# ============================================================================

@dataclass
class Opportunity:
    name: str
    customer_value: float
    market_potential: float
    strategic_fit: float
    feasibility: float
    confidence: float

    def score(self) -> float:
        """
        Multiplicative scoring makes a severe weakness visible.

        This is a prioritization aid, not a universal mathematical truth.
        """
        return (
            self.customer_value
            * self.market_potential
            * self.strategic_fit
            * self.feasibility
            * self.confidence
        )


opportunities = [
    Opportunity("Adaptive daily study planning", 9, 8, 9, 8, 0.75),
    Opportunity("Course marketplace", 6, 10, 5, 5, 0.40),
    Opportunity("Human tutoring marketplace", 8, 9, 6, 4, 0.55),
    Opportunity("Corporate learning analytics", 7, 7, 8, 7, 0.65),
]

print("\nOpportunity scoring:")
for opportunity in sorted(opportunities, key=Opportunity.score, reverse=True):
    print(f"{opportunity.name:35} | score={opportunity.score():.2f}")


# ============================================================================
# 21. OPPORTUNITY SOLUTION TREE
# ============================================================================

opportunity_tree = {
    "Desired outcome": {
        "Complete more courses": {
            "Better planning": [
                "Adaptive schedule",
                "Time-aware task generation",
            ],
            "Better continuity": [
                "Resume guidance",
                "Progress reminders",
            ],
            "Better motivation": [
                "Progress visualization",
                "Milestone feedback",
            ],
        }
    }
}

def print_tree(tree: Dict, level: int = 0) -> None:
    for key, value in tree.items():
        print("  " * level + f"- {key}")
        if isinstance(value, dict):
            print_tree(value, level + 1)
        elif isinstance(value, list):
            for item in value:
                print("  " * (level + 1) + f"- {item}")


print("\nOpportunity solution tree:")
print_tree(opportunity_tree)


# ============================================================================
# 22. DESIRABILITY, VIABILITY, FEASIBILITY
# ============================================================================

@dataclass
class DVF:
    desirability: float
    viability: float
    feasibility: float

    def balanced_score(self) -> float:
        return min(self.desirability, self.viability, self.feasibility)


dvf = DVF(8.5, 6.5, 8.0)

print("\nDesirability / viability / feasibility:")
print(f"Desirability: {dvf.desirability}/10")
print(f"Viability:    {dvf.viability}/10")
print(f"Feasibility:  {dvf.feasibility}/10")
print(f"Constraint score: {dvf.balanced_score():.1f}/10")


# ============================================================================
# 23. EVIDENCE QUALITY
# ============================================================================

class EvidenceType(Enum):
    OPINION = "opinion"
    INTENT = "intent"
    BEHAVIOR = "behavior"
    COMMITMENT = "commitment"
    OUTCOME = "outcome"


EVIDENCE_STRENGTH = {
    EvidenceType.OPINION: 1,
    EvidenceType.INTENT: 2,
    EvidenceType.BEHAVIOR: 4,
    EvidenceType.COMMITMENT: 5,
    EvidenceType.OUTCOME: 6,
}

print("\nEvidence hierarchy:")
for evidence_type, strength in EVIDENCE_STRENGTH.items():
    print(f"- {evidence_type.value:12}: {strength}/6")


# ============================================================================
# 24. HYPOTHESIS TESTING
# ============================================================================

@dataclass
class ExperimentResult:
    participants: int
    successes: int

    @property
    def conversion_rate(self) -> float:
        if self.participants == 0:
            return 0.0
        return self.successes / self.participants


def evaluate_hypothesis(
    result: ExperimentResult,
    threshold: float,
) -> str:
    if result.participants <= 0:
        return "invalid experiment: no participants"

    rate = result.conversion_rate

    if rate >= threshold:
        return "evidence supports the hypothesis"
    return "evidence does not meet the predefined threshold"


experiment = ExperimentResult(100, 31)
print("\nExperiment:")
print(f"Conversion: {experiment.conversion_rate:.1%}")
print(evaluate_hypothesis(experiment, 0.25))


# ============================================================================
# 25. SURVEY ANALYSIS
# ============================================================================

survey_scores = [8, 7, 9, 6, 9, 8, 7, 9, 5, 8]

print("\nSurvey analysis:")
print(f"Mean:   {mean(survey_scores):.2f}")
print(f"Median: {median(survey_scores):.2f}")
print(f"Min:    {min(survey_scores)}")
print(f"Max:    {max(survey_scores)}")


def net_promoter_score(responses: Sequence[int]) -> float:
    """
    NPS:
        promoters = 9-10
        passives  = 7-8
        detractors = 0-6

    Score = % promoters - % detractors.
    """
    if not responses:
        return 0.0

    promoters = sum(score >= 9 for score in responses)
    detractors = sum(score <= 6 for score in responses)

    return (promoters / len(responses) - detractors / len(responses)) * 100


nps_responses = [9, 10, 8, 7, 6, 9, 10, 5, 8, 9]
print(f"NPS: {net_promoter_score(nps_responses):.1f}")


# ============================================================================
# 26. COHORT THINKING
# ============================================================================

@dataclass
class Cohort:
    name: str
    users: int
    retained_users: List[int]

    def retention_rates(self) -> List[float]:
        if self.users == 0:
            return []
        return [count / self.users for count in self.retained_users]


cohort = Cohort(
    "September",
    1000,
    [1000, 720, 560, 480, 430],
)

print("\nCohort retention:")
for month, retention in enumerate(cohort.retention_rates(), start=0):
    print(f"Month {month}: {retention:.1%}")


# ============================================================================
# 27. ACTIVATION AND BEHAVIORAL METRICS
# ============================================================================

@dataclass
class Funnel:
    visitors: int
    signups: int
    activated: int
    retained: int
    paid: int

    def rates(self) -> Dict[str, float]:
        def ratio(numerator: int, denominator: int) -> float:
            return numerator / denominator if denominator else 0.0

        return {
            "visitor_to_signup": ratio(self.signups, self.visitors),
            "signup_to_activation": ratio(self.activated, self.signups),
            "activation_to_retention": ratio(self.retained, self.activated),
            "retention_to_paid": ratio(self.paid, self.retained),
        }


funnel = Funnel(10_000, 1_000, 650, 400, 80)

print("\nProduct funnel:")
for name, rate in funnel.rates().items():
    print(f"- {name}: {rate:.1%}")


# ============================================================================
# 28. VANITY METRICS VS ACTIONABLE METRICS
# ============================================================================

metrics = {
    "vanity": [
        "Total registered users",
        "Total downloads",
        "Total page views",
    ],
    "actionable": [
        "Weekly active users",
        "Activation rate",
        "Course completion rate",
        "Time to first successful study session",
        "Retention by cohort",
        "Paid conversion by segment",
    ],
}

print("\nMetric classification:")
for category, values in metrics.items():
    print(f"{category.title()}:")
    for value in values:
        print(f"  - {value}")


# ============================================================================
# 29. RICE PRIORITIZATION
# ============================================================================

@dataclass
class RiceOpportunity:
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float

    def score(self) -> float:
        if self.effort <= 0:
            return 0.0
        return self.reach * self.impact * self.confidence / self.effort


rice_items = [
    RiceOpportunity("Adaptive scheduling", 5000, 3, 0.8, 4),
    RiceOpportunity("Progress resume", 4000, 2, 0.9, 2),
    RiceOpportunity("Gamification", 3000, 1, 0.5, 5),
    RiceOpportunity("Corporate analytics", 500, 3, 0.7, 6),
]

print("\nRICE prioritization:")
for item in sorted(rice_items, key=RiceOpportunity.score, reverse=True):
    print(f"{item.name:25} | RICE={item.score():.1f}")


# ============================================================================
# 30. VALUE VS EFFORT
# ============================================================================

def value_effort_classification(value: float, effort: float) -> str:
    if value >= 7 and effort <= 4:
        return "high-value / low-effort"
    if value >= 7 and effort > 4:
        return "high-value / high-effort"
    if value < 7 and effort <= 4:
        return "low-value / low-effort"
    return "low-value / high-effort"


print("\nValue-effort matrix:")
examples = [
    ("Adaptive schedule", 9, 4),
    ("Social feed", 4, 8),
    ("Resume button", 8, 2),
    ("Custom video editor", 5, 9),
]
for name, value, effort in examples:
    print(f"{name:25} -> {value_effort_classification(value, effort)}")


# ============================================================================
# 31. ASSUMPTION MAPPING
# ============================================================================

@dataclass
class Assumption:
    description: str
    importance: int
    uncertainty: int

    @property
    def risk(self) -> int:
        return self.importance * self.uncertainty


assumptions = [
    Assumption("Customers have recurring scheduling problems", 5, 4),
    Assumption("Customers can describe the problem reliably", 3, 2),
    Assumption("The product can integrate with calendars", 4, 3),
    Assumption("Customers will pay", 5, 5),
    Assumption("A small team can build the MVP", 4, 2),
]

print("\nAssumption risk map:")
for assumption in sorted(assumptions, key=lambda item: item.risk, reverse=True):
    print(f"{assumption.risk:2} | {assumption.description}")


# ============================================================================
# 32. LEAST-RISKY TEST
# ============================================================================

@dataclass
class Experiment:
    hypothesis: str
    method: str
    cost: float
    duration_days: int
    evidence_type: EvidenceType
    success_metric: str


experiments = [
    Experiment(
        "Customers want adaptive schedules",
        "Concierge prototype with 20 customers",
        50,
        7,
        EvidenceType.BEHAVIOR,
        "60% use the generated plan twice per week",
    ),
    Experiment(
        "Customers will pay",
        "Pre-order offer to qualified customers",
        20,
        5,
        EvidenceType.COMMITMENT,
        "10% place a paid deposit",
    ),
    Experiment(
        "Calendar integration improves retention",
        "A/B test integration vs manual planning",
        100,
        21,
        EvidenceType.OUTCOME,
        "Retention improves by at least 10%",
    ),
]

print("\nExperiment portfolio:")
for experiment in experiments:
    print(
        f"- {experiment.method}: cost=${experiment.cost:.0f}, "
        f"{experiment.duration_days} days, success={experiment.success_metric}"
    )


# ============================================================================
# 33. MVP AND CONCIERGE TESTING
# ============================================================================

def concierge_plan(
    course_hours: float,
    available_hours_per_week: float,
    weeks: int,
) -> List[float]:
    """
    Concierge testing can manually deliver the intended outcome before
    automating the complete workflow.
    """
    if course_hours < 0 or available_hours_per_week <= 0 or weeks <= 0:
        raise ValueError("Course hours must be non-negative and capacity positive.")

    capacity = available_hours_per_week * weeks
    remaining = course_hours
    plan = []

    for _ in range(weeks):
        allocation = min(available_hours_per_week, remaining)
        plan.append(allocation)
        remaining -= allocation

    return plan


print("\nConcierge planning example:")
print(concierge_plan(12, 3, 6))


# ============================================================================
# 34. EXPERIMENT DESIGN
# ============================================================================

@dataclass
class ExperimentDesign:
    hypothesis: str
    target_population: str
    intervention: str
    baseline: float
    target: float
    duration_days: int

    def is_success(self, measured: float) -> bool:
        return measured >= self.target


experiment_design = ExperimentDesign(
    hypothesis="Adaptive planning improves weekly study consistency.",
    target_population="Professionals with unfinished online courses",
    intervention="Personalized weekly study plan",
    baseline=0.35,
    target=0.50,
    duration_days=28,
)

print("\nExperiment design:")
print(experiment_design)
print(
    "Measured result 0.53:",
    "success" if experiment_design.is_success(0.53) else "failure",
)


# ============================================================================
# 35. STATISTICAL REASONING
# ============================================================================

def proportion_standard_error(
    successes: int,
    observations: int,
) -> float:
    """
    Approximate standard error for a binomial proportion.

    This is useful for understanding why small experiments can produce noisy
    conversion rates.
    """
    if observations <= 0:
        raise ValueError("Observations must be positive.")

    p = successes / observations
    return sqrt(p * (1 - p) / observations)


successes = 31
observations_count = 100

print("\nApproximate experiment uncertainty:")
print(
    f"Observed proportion: {successes / observations_count:.1%}"
)
print(
    f"Standard error: {proportion_standard_error(successes, observations_count):.3f}"
)


# ============================================================================
# 36. SAMPLE SIZE INTUITION
# ============================================================================

def approximate_sample_size_for_proportion(
    p: float,
    margin_of_error: float,
    z: float = 1.96,
) -> int:
    """
    Approximate sample size for a population proportion.

    It assumes a simple random sample and is intended for conceptual learning.
    """
    if not 0 < p < 1:
        raise ValueError("p must be between 0 and 1.")
    if margin_of_error <= 0:
        raise ValueError("Margin of error must be positive.")

    n = z**2 * p * (1 - p) / margin_of_error**2
    return round(n)


print("\nApproximate sample size:")
print(
    approximate_sample_size_for_proportion(
        p=0.5,
        margin_of_error=0.05,
    )
)


# ============================================================================
# 37. DISCOVERY RESEARCH QUALITY
# ============================================================================

def evidence_quality_score(
    recency: float,
    behavioral_directness: float,
    sample_diversity: float,
    reproducibility: float,
) -> float:
    """
    Simple weighted framework for comparing evidence sources.

    Scores are normalized from 0 to 1.
    """
    return (
        0.20 * recency
        + 0.35 * behavioral_directness
        + 0.20 * sample_diversity
        + 0.25 * reproducibility
    )


print("\nEvidence quality examples:")
print(
    "Customer interview:",
    round(evidence_quality_score(0.9, 0.8, 0.6, 0.6), 2),
)
print(
    "Anonymous survey:",
    round(evidence_quality_score(0.8, 0.5, 0.8, 0.7), 2),
)
print(
    "Actual product behavior:",
    round(evidence_quality_score(1.0, 1.0, 0.8, 0.9), 2),
)


# ============================================================================
# 38. DISCOVERY ANTI-PATTERNS
# ============================================================================

ANTI_PATTERNS = {
    "confirmation_bias": "Searching only for evidence supporting an existing belief.",
    "solution_bias": "Treating a preferred solution as the problem.",
    "small_sample_overconfidence": "Making strong conclusions from very few observations.",
    "selection_bias": "Learning only from unusually interested or available customers.",
    "survivorship_bias": "Studying successful users while ignoring abandoned users.",
    "leading_interviews": "Steering customers toward desired answers.",
    "feature_requests_as_requirements": "Treating every requested feature as the underlying need.",
    "vanity_metrics": "Using numbers that look impressive but do not guide decisions.",
    "premature_scaling": "Building a large system before fundamental assumptions are validated.",
    "false_precision": "Presenting uncertain market estimates as exact facts.",
}

print("\nDiscovery anti-patterns:")
for name, description in ANTI_PATTERNS.items():
    print(f"- {name}: {description}")


# ============================================================================
# 39. EDGE CASES
# ============================================================================

def validate_discovery_observation(observation: ProblemObservation) -> List[str]:
    errors = []

    if not observation.customer_id:
        errors.append("customer ID is missing")

    if observation.frequency_per_month < 0:
        errors.append("frequency cannot be negative")

    if not 0 <= observation.severity <= 10:
        errors.append("severity must be between 0 and 10")

    if not 0 <= observation.willingness_to_change <= 10:
        errors.append("willingness to change must be between 0 and 10")

    if not observation.situation.strip():
        errors.append("situation is missing")

    return errors


print("\nValidation edge cases:")
invalid_observation = ProblemObservation(
    "",
    "",
    "behavior",
    "impact",
    -2,
    12,
    "none",
    -1,
)
print(validate_discovery_observation(invalid_observation))


# ============================================================================
# 40. CUSTOMER VALUE MODEL
# ============================================================================

def customer_value(
    benefit: float,
    pain_reduction: float,
    time_saved: float,
    switching_cost: float,
) -> float:
    """
    A conceptual value model.

    The units are intentionally normalized rather than pretending customer
    value can be reduced to one universally correct equation.
    """
    return (
        0.40 * benefit
        + 0.30 * pain_reduction
        + 0.20 * time_saved
        - 0.10 * switching_cost
    )


print("\nConceptual customer value:")
print(
    customer_value(
        benefit=9,
        pain_reduction=8,
        time_saved=7,
        switching_cost=4,
    )
)


# ============================================================================
# 41. OPPORTUNITY COST
# ============================================================================

@dataclass
class Initiative:
    name: str
    expected_value: float
    cost: float
    strategic_fit: float

    def net_value(self) -> float:
        return self.expected_value * self.strategic_fit - self.cost


initiatives = [
    Initiative("Adaptive planner", 90, 35, 0.95),
    Initiative("Social community", 55, 30, 0.60),
    Initiative("Video editor", 70, 60, 0.45),
]

print("\nOpportunity cost comparison:")
for initiative in sorted(initiatives, key=Initiative.net_value, reverse=True):
    print(f"{initiative.name:20} | net value={initiative.net_value():.1f}")


# ============================================================================
# 42. DISCOVERY DECISION GATE
# ============================================================================

@dataclass
class DecisionGate:
    problem_evidence: float
    customer_evidence: float
    market_evidence: float
    solution_evidence: float
    business_evidence: float

    def readiness(self) -> float:
        return mean(
            [
                self.problem_evidence,
                self.customer_evidence,
                self.market_evidence,
                self.solution_evidence,
                self.business_evidence,
            ]
        )

    def decision(self) -> str:
        score = self.readiness()

        if score >= 8:
            return "proceed with strong evidence"
        if score >= 6:
            return "proceed with targeted validation"
        if score >= 4:
            return "continue discovery"
        return "reconsider the opportunity"


gate = DecisionGate(8, 8, 7, 5, 6)

print("\nDecision gate:")
print(f"Readiness: {gate.readiness():.1f}/10")
print(f"Decision: {gate.decision()}")


# ============================================================================
# 43. ADVANCED: INFORMATION GAIN
# ============================================================================

def binary_entropy(probability: float) -> float:
    """
    Shannon entropy for a binary hypothesis.

    Entropy measures uncertainty. Maximum uncertainty occurs near 0.5.
    """
    if probability <= 0 or probability >= 1:
        return 0.0
    return -(
        probability * log(probability, 2)
        + (1 - probability) * log(1 - probability, 2)
    )


def expected_information_gain(
    prior_probability: float,
    outcomes: Sequence[Tuple[float, float]],
) -> float:
    """
    Conceptual information-gain calculation.

    Each tuple is:
        (posterior probability of hypothesis, probability of that outcome)

    The function compares prior entropy with expected posterior entropy.
    """
    prior_entropy = binary_entropy(prior_probability)
    expected_posterior_entropy = sum(
        outcome_probability * binary_entropy(posterior)
        for posterior, outcome_probability in outcomes
    )
    return prior_entropy - expected_posterior_entropy


gain = expected_information_gain(
    0.5,
    [
        (0.8, 0.5),
        (0.2, 0.5),
    ],
)

print("\nInformation gain:")
print(f"Expected information gain: {gain:.3f} bits")


# ============================================================================
# 44. EXPERIMENT SELECTION BY INFORMATION VALUE
# ============================================================================

@dataclass
class DiscoveryExperiment:
    name: str
    cost: float
    expected_information_gain: float
    decision_impact: float

    def information_value_per_cost(self) -> float:
        if self.cost <= 0:
            return 0.0
        return self.expected_information_gain * self.decision_impact / self.cost


discovery_experiments = [
    DiscoveryExperiment("Interview", 10, 0.30, 0.7),
    DiscoveryExperiment("Prototype test", 100, 0.60, 0.9),
    DiscoveryExperiment("Paid pre-order", 30, 0.80, 1.0),
    DiscoveryExperiment("Large survey", 200, 0.35, 0.5),
]

print("\nExperiment information value:")
for item in sorted(
    discovery_experiments,
    key=DiscoveryExperiment.information_value_per_cost,
    reverse=True,
):
    print(
        f"{item.name:20} | "
        f"value/cost={item.information_value_per_cost():.4f}"
    )


# ============================================================================
# 45. BAYESIAN UPDATING
# ============================================================================

def bayesian_update(
    prior: float,
    likelihood_if_true: float,
    likelihood_if_false: float,
) -> float:
    """
    Bayes' theorem:
        P(H|E) = P(E|H)P(H) / P(E)

    This demonstrates how evidence can update confidence in a discovery
    hypothesis.
    """
    numerator = likelihood_if_true * prior
    evidence_probability = (
        likelihood_if_true * prior
        + likelihood_if_false * (1 - prior)
    )

    if evidence_probability == 0:
        return 0.0

    return numerator / evidence_probability


posterior = bayesian_update(
    prior=0.30,
    likelihood_if_true=0.80,
    likelihood_if_false=0.20,
)

print("\nBayesian hypothesis update:")
print(f"Prior probability:     30.0%")
print(f"Posterior probability: {posterior:.1%}")


# ============================================================================
# 46. MARKET ATTRACTIVENESS MODEL
# ============================================================================

@dataclass
class MarketAttractiveness:
    growth: float
    margin: float
    competition: float
    accessibility: float
    regulatory_risk: float
    strategic_fit: float

    def score(self) -> float:
        """
        Higher competition and regulatory risk reduce attractiveness.
        """
        return (
            0.20 * self.growth
            + 0.20 * self.margin
            + 0.20 * (10 - self.competition)
            + 0.15 * self.accessibility
            + 0.10 * (10 - self.regulatory_risk)
            + 0.15 * self.strategic_fit
        )


market_attractiveness = MarketAttractiveness(
    growth=8,
    margin=7,
    competition=6,
    accessibility=8,
    regulatory_risk=3,
    strategic_fit=9,
)

print("\nMarket attractiveness:")
print(f"{market_attractiveness.score():.2f}/10")


# ============================================================================
# 47. DISCOVERY SCORECARD
# ============================================================================

def scorecard(
    problem: float,
    customer: float,
    market: float,
    opportunity: float,
    evidence: float,
) -> Dict[str, float]:
    return {
        "problem": problem,
        "customer": customer,
        "market": market,
        "opportunity": opportunity,
        "evidence": evidence,
        "overall": mean([problem, customer, market, opportunity, evidence]),
    }


final_scorecard = scorecard(8.5, 8.0, 7.5, 8.2, 6.8)

print("\nDiscovery scorecard:")
for key, value in final_scorecard.items():
    print(f"{key.title():12}: {value:.2f}")


# ============================================================================
# 48. PRODUCTION-ORIENTED DISCOVERY CHECKLIST
# ============================================================================

CHECKLIST = [
    "Define the decision that discovery must support.",
    "Separate facts, observations, interpretations, and assumptions.",
    "Identify the highest-risk assumptions.",
    "Interview customers about recent real behavior.",
    "Study non-consumption and abandoned behavior.",
    "Map alternatives, including manual workarounds and inaction.",
    "Segment customers by meaningful behavioral differences.",
    "Estimate market size using explicit assumptions.",
    "Evaluate desirability, viability, and feasibility.",
    "Design the smallest experiment capable of changing the decision.",
    "Define success and failure criteria before running the test.",
    "Track evidence quality rather than evidence quantity.",
    "Look for contradictory evidence.",
    "Avoid treating customer requests as complete problem definitions.",
    "Record decisions and the evidence behind them.",
]

print("\nProduction discovery checklist:")
for item in CHECKLIST:
    print(f"[ ] {item}")


# ============================================================================
# 49. COMPLETE MINI DISCOVERY WORKFLOW
# ============================================================================

def run_mini_discovery() -> Dict[str, object]:
    """
    A compact end-to-end discovery workflow.

    The workflow is intentionally simple enough for beginners while exposing
    the structure used in more sophisticated discovery programs.
    """
    raw_observations = observations

    valid_observations = [
        item for item in raw_observations
        if not validate_discovery_observation(item)
    ]

    recurring_problem = (
        problem_frequency_score(valid_observations) >= 10
        and problem_severity_score(valid_observations) >= 7
    )

    qualified_customers = [
        customer for customer in customers
        if customer.buying_authority and customer.willingness_to_pay >= 7
    ]

    best_opportunity = max(opportunities, key=Opportunity.score)

    return {
        "valid_observations": len(valid_observations),
        "recurring_problem_detected": recurring_problem,
        "qualified_customers": len(qualified_customers),
        "best_opportunity": best_opportunity.name,
        "best_opportunity_score": best_opportunity.score(),
    }


print("\nMini discovery workflow:")
for key, value in run_mini_discovery().items():
    print(f"- {key}: {value}")


# ============================================================================
# 50. PRACTICAL RULES
# ============================================================================

RULES = [
    "Start with uncertainty, not features.",
    "A problem is not validated merely because a customer says it sounds useful.",
    "Recent behavior is generally stronger evidence than hypothetical intent.",
    "A workaround is evidence that customers are already investing effort.",
    "Frequency alone does not prove importance; consequences matter.",
    "Large markets are not automatically attractive markets.",
    "A small high-value segment can be more attractive than a huge weakly served segment.",
    "Competition can validate demand while also increasing execution difficulty.",
    "Do not confuse willingness to pay with actual payment.",
    "Define experiment thresholds before seeing results.",
    "Negative evidence is valuable because it prevents wasted delivery effort.",
    "Discovery is continuous; markets, customers, alternatives, and assumptions change.",
]

print("\nCore rules:")
for rule in RULES:
    print(f"- {rule}")


# ============================================================================
# 51. RUNNING THE STUDY FILE
# ============================================================================

def main() -> None:
    """
    The demonstrations above execute when the file is imported or run.

    This function exists as a clear executable entry point for future extension
    without introducing external dependencies.
    """
    print("\n" + "=" * 80)
    print("PRODUCT DISCOVERY STUDY FILE EXECUTED SUCCESSFULLY")
    print("=" * 80)
    print(
        "The examples covered problem discovery, customer discovery, "
        "market discovery, opportunity discovery, experimentation, "
        "evidence evaluation, prioritization, and advanced uncertainty analysis."
    )


if __name__ == "__main__":
    main()
