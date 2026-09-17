"""
Customer Understanding: Customers, Users, Buyers, Decision-Makers, Influencers, Personas

A standalone study and implementation file covering customer understanding from
beginner concepts through advanced segmentation, persona modeling, buying-unit
analysis, journey analysis, scoring, validation, experimentation, and a
privacy-conscious customer intelligence pipeline.

The examples use only Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from collections import Counter, defaultdict
import re
import unittest


# ============================================================================
# 1. FOUNDATIONS
# ============================================================================

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain(text: str) -> None:
    print(text)


section("1. Customer understanding fundamentals")

explain(
    """
Customer understanding is the systematic study of people and organizations
connected to a product or service.

Several roles that are often incorrectly treated as one person can be
different:

Customer:
    The person or organization that has a relationship with the provider.

User:
    The person who actually uses the product or service.

Buyer:
    The person who purchases or initiates the transaction.

Decision-maker:
    The person with authority to approve or reject a purchase.

Influencer:
    A person whose knowledge, opinion, requirements, reputation, or behavior
    affects the decision without necessarily owning the final decision.

These roles may overlap. A consumer buying a notebook for personal use may be
the customer, user, buyer, and decision-maker. In an enterprise software
purchase, they can be different people.
"""
)


# ============================================================================
# 2. CUSTOMER-ROLE MODEL
# ============================================================================

class CustomerRole(Enum):
    CUSTOMER = "customer"
    USER = "user"
    BUYER = "buyer"
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"


@dataclass
class Person:
    name: str
    role: CustomerRole
    department: str = ""
    needs: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    influence_level: float = 0.0

    def describe(self) -> str:
        return (
            f"{self.name}: {self.role.value}; "
            f"department={self.department or 'N/A'}; "
            f"influence={self.influence_level:.1f}"
        )


@dataclass
class BuyingUnit:
    organization: str
    participants: List[Person]

    def roles_present(self) -> Counter:
        return Counter(person.role.value for person in self.participants)

    def missing_roles(self) -> List[str]:
        expected = {
            CustomerRole.USER.value,
            CustomerRole.BUYER.value,
            CustomerRole.DECISION_MAKER.value,
            CustomerRole.INFLUENCER.value,
        }
        return sorted(expected - set(self.roles_present()))

    def most_influential(self) -> Optional[Person]:
        if not self.participants:
            return None
        return max(self.participants, key=lambda person: person.influence_level)


buying_unit = BuyingUnit(
    organization="Northstar Manufacturing",
    participants=[
        Person(
            "Asha",
            CustomerRole.USER,
            "Operations",
            ["simple workflow", "fast reporting"],
            ["training time"],
            0.55,
        ),
        Person(
            "Rahul",
            CustomerRole.BUYER,
            "Procurement",
            ["commercial clarity"],
            ["contract complexity"],
            0.65,
        ),
        Person(
            "Meera",
            CustomerRole.DECISION_MAKER,
            "Finance",
            ["ROI", "cost control"],
            ["uncertain payback"],
            0.95,
        ),
        Person(
            "Vikram",
            CustomerRole.INFLUENCER,
            "IT",
            ["security", "integration"],
            ["data exposure"],
            0.80,
        ),
    ],
)

for participant in buying_unit.participants:
    print(participant.describe())

print("Roles present:", dict(buying_unit.roles_present()))
print("Missing roles:", buying_unit.missing_roles())
print(
    "Most influential:",
    buying_unit.most_influential().name
    if buying_unit.most_influential()
    else "None",
)


# ============================================================================
# 3. NEEDS, PAINS, JOBS, OUTCOMES
# ============================================================================

@dataclass
class CustomerNeed:
    statement: str
    importance: float
    current_satisfaction: float

    def opportunity_score(self) -> float:
        """
        A simple opportunity heuristic.

        It is not a universal industry formula. It combines importance and
        dissatisfaction to identify areas deserving investigation.
        """
        return self.importance * (10.0 - self.current_satisfaction)


needs = [
    CustomerNeed("Reduce manual reporting", 9.0, 3.0),
    CustomerNeed("Improve data visibility", 8.0, 5.0),
    CustomerNeed("Reduce onboarding time", 7.0, 4.0),
]

for need in needs:
    print(
        f"{need.statement}: opportunity={need.opportunity_score():.2f}"
    )

explain(
    """
A need describes something valuable to the customer. A pain point describes
friction or an undesirable current condition. A desired outcome describes the
result the customer wants.

A useful distinction is between a feature request and an underlying need.

Feature request:
    "Add a dashboard."

Underlying need:
    "I need to identify abnormal performance without manually combining
    multiple reports."

The second formulation is more useful for customer research because multiple
solutions can satisfy the same need.
"""
)


# ============================================================================
# 4. PERSONAS
# ============================================================================

@dataclass
class Persona:
    name: str
    segment: str
    goals: List[str]
    pain_points: List[str]
    behaviors: List[str]
    preferred_channels: List[str]
    objections: List[str]
    buying_triggers: List[str]
    evidence_count: int = 0

    def quality_check(self) -> Dict[str, bool]:
        return {
            "has_goals": bool(self.goals),
            "has_pain_points": bool(self.pain_points),
            "has_behaviors": bool(self.behaviors),
            "has_channels": bool(self.preferred_channels),
            "has_objections": bool(self.objections),
            "has_triggers": bool(self.buying_triggers),
            "has_evidence": self.evidence_count > 0,
        }


operations_persona = Persona(
    name="Operations Analyst",
    segment="mid-market operations",
    goals=["reduce manual work", "produce reliable reports"],
    pain_points=["spreadsheet duplication", "slow reporting"],
    behaviors=["checks reports daily", "exports data weekly"],
    preferred_channels=["email", "web application"],
    objections=["migration effort", "training"],
    buying_triggers=["reporting errors", "new compliance requirement"],
    evidence_count=27,
)

print("Persona:", operations_persona.name)
print("Persona quality:", operations_persona.quality_check())


# ============================================================================
# 5. DEMOGRAPHICS VS BEHAVIOR VS PSYCHOGRAPHICS
# ============================================================================

customer_profile = {
    "demographics": {
        "age_band": "30-39",
        "location": "urban",
        "occupation": "operations professional",
    },
    "firmographics": {
        "company_size": "mid-market",
        "industry": "manufacturing",
    },
    "behavioral": {
        "weekly_sessions": 5,
        "feature_usage": ["reports", "exports", "alerts"],
        "purchase_frequency": 2,
    },
    "psychographic": {
        "priorities": ["control", "reliability"],
        "risk_tolerance": "moderate",
    },
}

for category, attributes in customer_profile.items():
    print(f"{category}: {attributes}")

explain(
    """
Demographics describe population characteristics such as age bands or
occupation. Firmographics are organizational characteristics such as
industry, company size, and revenue band. Behavioral data describes what
people do. Psychographic information concerns attitudes, motivations,
priorities, and preferences.

Behavioral and contextual evidence should not automatically be inferred from
demographic categories. A persona should represent observed or researched
patterns rather than stereotypes.
"""
)


# ============================================================================
# 6. CUSTOMER JOURNEY
# ============================================================================

class JourneyStage(Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"
    ONBOARDING = "onboarding"
    ADOPTION = "adoption"
    RETENTION = "retention"
    EXPANSION = "expansion"
    ADVOCACY = "advocacy"


@dataclass
class JourneyTouchpoint:
    stage: JourneyStage
    channel: str
    customer_action: str
    emotion: str
    friction: float
    evidence: str = ""

    def friction_level(self) -> str:
        if self.friction < 3:
            return "low"
        if self.friction < 7:
            return "medium"
        return "high"


journey = [
    JourneyTouchpoint(
        JourneyStage.AWARENESS,
        "search",
        "reads comparison article",
        "curious",
        2.0,
        "interview evidence",
    ),
    JourneyTouchpoint(
        JourneyStage.CONSIDERATION,
        "website",
        "reviews feature documentation",
        "interested",
        4.0,
        "analytics",
    ),
    JourneyTouchpoint(
        JourneyStage.EVALUATION,
        "demo",
        "tests workflow",
        "uncertain",
        7.0,
        "interview",
    ),
    JourneyTouchpoint(
        JourneyStage.PURCHASE,
        "sales",
        "requests contract",
        "cautious",
        8.0,
        "CRM data",
    ),
    JourneyTouchpoint(
        JourneyStage.ONBOARDING,
        "application",
        "imports data",
        "frustrated",
        9.0,
        "support tickets",
    ),
]

for touchpoint in journey:
    print(
        touchpoint.stage.value,
        "->",
        touchpoint.channel,
        "| friction:",
        touchpoint.friction_level(),
    )


# ============================================================================
# 7. CUSTOMER RESEARCH EVIDENCE
# ============================================================================

class EvidenceType(Enum):
    INTERVIEW = "interview"
    SURVEY = "survey"
    OBSERVATION = "observation"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    SALES = "sales"
    EXPERIMENT = "experiment"


@dataclass
class Evidence:
    source: EvidenceType
    statement: str
    strength: float
    sample_size: int

    def weighted_strength(self) -> float:
        return self.strength * min(1.0, self.sample_size / 50.0)


evidence = [
    Evidence(
        EvidenceType.INTERVIEW,
        "Users struggle with initial configuration.",
        0.90,
        18,
    ),
    Evidence(
        EvidenceType.ANALYTICS,
        "Many accounts abandon setup before completion.",
        0.95,
        1200,
    ),
    Evidence(
        EvidenceType.SUPPORT,
        "Configuration generates repeated questions.",
        0.80,
        74,
    ),
]

for item in evidence:
    print(
        item.source.value,
        "| weighted strength:",
        round(item.weighted_strength(), 3),
    )

explain(
    """
No single research method captures the entire customer picture.

Interviews provide depth but normally use smaller samples.
Surveys can quantify stated attitudes but depend on question quality.
Observation captures behavior in context.
Product analytics captures actual digital behavior but often lacks the reason
behind that behavior.
Support records reveal recurring problems.
Sales conversations reveal buying concerns but can be biased toward active
prospects.
Experiments can test causal effects under controlled conditions.

Triangulation means comparing evidence from multiple sources rather than
treating one source as unquestionable truth.
"""
)


# ============================================================================
# 8. CUSTOMER SEGMENTATION
# ============================================================================

@dataclass
class Customer:
    customer_id: str
    industry: str
    company_size: int
    annual_value: float
    sessions_per_month: int
    support_tickets: int
    satisfaction: float
    adoption_rate: float
    decision_cycle_days: int
    primary_goal: str


customers = [
    Customer("C001", "manufacturing", 450, 120000, 38, 2, 8.4, 0.87, 45, "efficiency"),
    Customer("C002", "retail", 70, 18000, 14, 8, 6.1, 0.48, 18, "cost"),
    Customer("C003", "finance", 1200, 310000, 61, 1, 9.0, 0.92, 90, "risk"),
    Customer("C004", "education", 250, 42000, 27, 5, 7.2, 0.69, 30, "access"),
    Customer("C005", "manufacturing", 900, 220000, 51, 3, 8.7, 0.89, 70, "efficiency"),
]


def segment_by_company_size(customer: Customer) -> str:
    if customer.company_size < 100:
        return "small"
    if customer.company_size < 1000:
        return "mid-market"
    return "enterprise"


def segment_by_adoption(customer: Customer) -> str:
    if customer.adoption_rate < 0.50:
        return "low adoption"
    if customer.adoption_rate < 0.80:
        return "moderate adoption"
    return "high adoption"


for customer in customers:
    print(
        customer.customer_id,
        segment_by_company_size(customer),
        segment_by_adoption(customer),
    )


# ============================================================================
# 9. RFM ANALYSIS
# ============================================================================

@dataclass
class RFMRecord:
    customer_id: str
    recency_days: int
    frequency: int
    monetary_value: float


rfm_records = [
    RFMRecord("C001", 7, 24, 120000),
    RFMRecord("C002", 64, 5, 18000),
    RFMRecord("C003", 3, 38, 310000),
    RFMRecord("C004", 21, 13, 42000),
    RFMRecord("C005", 10, 29, 220000),
]


def percentile_rank(values: Sequence[float], value: float) -> float:
    """
    Returns a simple empirical percentile.

    Duplicate values receive the same lower-bound style rank. This is useful
    for demonstration and is not intended to replace a statistical library
    for specialized production requirements.
    """
    if not values:
        raise ValueError("values cannot be empty")
    sorted_values = sorted(values)
    rank = sum(v <= value for v in sorted_values)
    return rank / len(sorted_values)


def rfm_score(record: RFMRecord, all_records: Sequence[RFMRecord]) -> Tuple[int, int, int]:
    recency_values = [-r.recency_days for r in all_records]
    frequency_values = [r.frequency for r in all_records]
    monetary_values = [r.monetary_value for r in all_records]

    r = min(5, max(1, int(percentile_rank(recency_values, -record.recency_days) * 5)))
    f = min(5, max(1, int(percentile_rank(frequency_values, record.frequency) * 5)))
    m = min(5, max(1, int(percentile_rank(monetary_values, record.monetary_value) * 5)))

    return r, f, m


for record in rfm_records:
    print(record.customer_id, "RFM:", rfm_score(record, rfm_records))


# ============================================================================
# 10. CUSTOMER VALUE AND SIMPLE SCORING
# ============================================================================

def estimated_lifetime_value(
    average_order_value: float,
    purchases_per_year: float,
    expected_years: float,
    gross_margin: float,
) -> float:
    """
    Simplified LTV model.

    Real businesses may incorporate retention curves, discount rates,
    contribution margins, expansion, acquisition costs, and cohort behavior.
    """
    if min(
        average_order_value,
        purchases_per_year,
        expected_years,
        gross_margin,
    ) < 0:
        raise ValueError("LTV inputs cannot be negative")

    return (
        average_order_value
        * purchases_per_year
        * expected_years
        * gross_margin
    )


def customer_health_score(customer: Customer) -> float:
    """
    Transparent weighted score.

    The weights are illustrative. They should be validated against actual
    retention, expansion, or other outcomes before production use.
    """
    satisfaction_component = customer.satisfaction / 10.0
    adoption_component = customer.adoption_rate
    engagement_component = min(customer.sessions_per_month / 60.0, 1.0)
    support_component = 1.0 - min(customer.support_tickets / 20.0, 1.0)

    return 100 * (
        0.30 * satisfaction_component
        + 0.35 * adoption_component
        + 0.20 * engagement_component
        + 0.15 * support_component
    )


for customer in customers:
    print(
        customer.customer_id,
        "health:",
        round(customer_health_score(customer), 1),
    )

print(
    "Example LTV:",
    estimated_lifetime_value(1000, 6, 4, 0.70),
)


# ============================================================================
# 11. CUSTOMER NEED PRIORITIZATION
# ============================================================================

@dataclass
class Opportunity:
    name: str
    importance: float
    satisfaction: float
    affected_customers: int
    strategic_relevance: float

    def score(self) -> float:
        return (
            self.importance
            * (10 - self.satisfaction)
            * sqrt(max(1, self.affected_customers))
            * self.strategic_relevance
        )


opportunities = [
    Opportunity("Simplify onboarding", 9, 4, 820, 1.0),
    Opportunity("Improve exports", 7, 6, 540, 0.8),
    Opportunity("Add advanced reporting", 8, 5, 210, 0.9),
]

for opportunity in opportunities:
    print(opportunity.name, round(opportunity.score(), 2))


# ============================================================================
# 12. BUYING PROCESS AND OBJECTIONS
# ============================================================================

@dataclass
class BuyingCriterion:
    criterion: str
    importance: float
    perceived_performance: float
    evidence: str = ""

    def weighted_value(self) -> float:
        return self.importance * self.perceived_performance


criteria = [
    BuyingCriterion("security", 10, 8.5, "security review"),
    BuyingCriterion("integration", 8, 7.5, "technical evaluation"),
    BuyingCriterion("price", 7, 6.0, "procurement"),
    BuyingCriterion("ease of use", 9, 7.0, "user testing"),
]

total_weight = sum(item.importance for item in criteria)
weighted_average = sum(
    item.weighted_value() for item in criteria
) / total_weight

print("Weighted buying evaluation:", round(weighted_average, 2))


# ============================================================================
# 13. QUALITATIVE DATA CODING
# ============================================================================

STOP_WORDS = {
    "the", "a", "an", "and", "is", "to", "of", "for", "with",
    "we", "our", "it", "this", "that", "in", "on", "be",
}


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def keyword_frequency(texts: Iterable[str]) -> Counter:
    counter = Counter()
    for text in texts:
        counter.update(tokenize(text))
    return counter


interview_quotes = [
    "The setup takes too long and our team needs simpler onboarding.",
    "We need reliable reports because manual reporting takes too long.",
    "Security approval is important before we can purchase the system.",
    "The reporting workflow is useful but configuration is difficult.",
]

frequencies = keyword_frequency(interview_quotes)
print("Frequent research terms:", frequencies.most_common(10))


# ============================================================================
# 14. THEMATIC ANALYSIS
# ============================================================================

THEMES = {
    "onboarding": {"setup", "onboarding", "configuration"},
    "reporting": {"reports", "reporting", "workflow"},
    "security": {"security", "approval"},
    "efficiency": {"long", "manual", "simpler"},
}


def detect_themes(text: str) -> Dict[str, int]:
    words = set(tokenize(text))
    return {
        theme: len(words & keywords)
        for theme, keywords in THEMES.items()
        if words & keywords
    }


for quote in interview_quotes:
    print(quote)
    print("Themes:", detect_themes(quote))


# ============================================================================
# 15. SIMILARITY FOR PERSONA / SEGMENT EXPLORATION
# ============================================================================

def cosine_similarity(
    vector_a: Dict[str, float],
    vector_b: Dict[str, float],
) -> float:
    """
    Computes cosine similarity between sparse vectors.

    A value near 1 means similar direction; near 0 means little overlap.
    Negative values can occur with signed numeric vectors.
    """
    keys = set(vector_a) | set(vector_b)
    dot = sum(vector_a.get(k, 0.0) * vector_b.get(k, 0.0) for k in keys)
    norm_a = sqrt(sum(value * value for value in vector_a.values()))
    norm_b = sqrt(sum(value * value for value in vector_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


persona_a = {
    "efficiency": 1.0,
    "reporting": 0.9,
    "security": 0.2,
    "cost": 0.4,
}

persona_b = {
    "efficiency": 0.8,
    "reporting": 0.7,
    "security": 0.3,
    "cost": 0.5,
}

print("Persona similarity:", round(cosine_similarity(persona_a, persona_b), 3))


# ============================================================================
# 16. SIMPLE CLUSTERING WITHOUT EXTERNAL PACKAGES
# ============================================================================

def euclidean_distance(point_a: Sequence[float], point_b: Sequence[float]) -> float:
    if len(point_a) != len(point_b):
        raise ValueError("points must have equal dimensions")
    return sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


def nearest_centroid(
    point: Sequence[float],
    centroids: Sequence[Sequence[float]],
) -> int:
    if not centroids:
        raise ValueError("at least one centroid is required")
    distances = [
        euclidean_distance(point, centroid)
        for centroid in centroids
    ]
    return min(range(len(distances)), key=distances.__getitem__)


points = [
    (0.9, 0.8),
    (0.8, 0.7),
    (0.2, 0.3),
    (0.1, 0.2),
    (0.6, 0.7),
]

centroids = [
    (0.8, 0.8),
    (0.2, 0.2),
]

for point in points:
    print(point, "cluster:", nearest_centroid(point, centroids))


# ============================================================================
# 17. CUSTOMER FEEDBACK SENTIMENT HEURISTIC
# ============================================================================

POSITIVE_WORDS = {
    "easy", "useful", "fast", "reliable", "excellent", "helpful",
    "clear", "good", "valuable",
}

NEGATIVE_WORDS = {
    "slow", "difficult", "bad", "confusing", "frustrating", "expensive",
    "broken", "hard", "problem",
}


def sentiment_score(text: str) -> float:
    words = tokenize(text)
    positive = sum(word in POSITIVE_WORDS for word in words)
    negative = sum(word in NEGATIVE_WORDS for word in words)

    if positive + negative == 0:
        return 0.0

    return (positive - negative) / (positive + negative)


feedback = [
    "The product is easy and useful but setup is difficult.",
    "Reports are reliable and fast.",
    "The workflow is confusing and slow.",
]

for item in feedback:
    print(round(sentiment_score(item), 2), item)

explain(
    """
This sentiment example is intentionally simple. Keyword sentiment can miss
negation, context, sarcasm, domain terminology, mixed sentiment, and language
variation. A production system should validate its method against labeled
data instead of treating a heuristic score as objective truth.
"""
)


# ============================================================================
# 18. CUSTOMER JOURNEY FRICTION ANALYSIS
# ============================================================================

def journey_friction_by_stage(
    touchpoints: Sequence[JourneyTouchpoint],
) -> Dict[str, float]:
    grouped: Dict[str, List[float]] = defaultdict(list)

    for touchpoint in touchpoints:
        grouped[touchpoint.stage.value].append(touchpoint.friction)

    return {
        stage: mean(scores)
        for stage, scores in grouped.items()
    }


print("Journey friction:", journey_friction_by_stage(journey))


# ============================================================================
# 19. RETENTION / CHURN CONCEPTS
# ============================================================================

def monthly_retention(starting_customers: int, retained_customers: int) -> float:
    if starting_customers <= 0:
        raise ValueError("starting_customers must be positive")
    if retained_customers < 0 or retained_customers > starting_customers:
        raise ValueError("retained_customers must be within valid range")
    return retained_customers / starting_customers


def monthly_churn(starting_customers: int, lost_customers: int) -> float:
    return 1.0 - monthly_retention(
        starting_customers,
        starting_customers - lost_customers,
    )


print("Retention:", monthly_retention(1000, 950))
print("Churn:", monthly_churn(1000, 50))


# ============================================================================
# 20. COHORT ANALYSIS
# ============================================================================

cohorts = {
    "2026-01": [1.00, 0.72, 0.61, 0.56],
    "2026-02": [1.00, 0.76, 0.66, 0.60],
    "2026-03": [1.00, 0.80, 0.69],
}


def cohort_summary(cohort_data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    summary = {}

    for cohort, retention_values in cohort_data.items():
        if not retention_values:
            continue

        summary[cohort] = {
            "initial": retention_values[0],
            "latest_observed": retention_values[-1],
            "months_observed": len(retention_values),
        }

    return summary


print("Cohort analysis:", cohort_summary(cohorts))


# ============================================================================
# 21. CUSTOMER FEEDBACK PRIORITIZATION
# ============================================================================

@dataclass
class FeedbackItem:
    text: str
    frequency: int
    severity: float
    strategic_fit: float
    evidence_quality: float

    def priority_score(self) -> float:
        return (
            self.frequency
            * self.severity
            * self.strategic_fit
            * self.evidence_quality
        )


feedback_items = [
    FeedbackItem(
        "setup is confusing",
        180,
        0.8,
        0.95,
        0.9,
    ),
    FeedbackItem(
        "more export formats",
        75,
        0.4,
        0.7,
        0.8,
    ),
    FeedbackItem(
        "advanced dashboard",
        110,
        0.5,
        0.85,
        0.7,
    ),
]

for item in sorted(
    feedback_items,
    key=lambda value: value.priority_score(),
    reverse=True,
):
    print(item.text, round(item.priority_score(), 2))


# ============================================================================
# 22. CUSTOMER DATA QUALITY
# ============================================================================

def validate_customer(customer: Customer) -> List[str]:
    errors = []

    if not customer.customer_id.strip():
        errors.append("missing customer ID")

    if customer.company_size < 0:
        errors.append("negative company size")

    if customer.annual_value < 0:
        errors.append("negative annual value")

    if customer.sessions_per_month < 0:
        errors.append("negative session count")

    if customer.support_tickets < 0:
        errors.append("negative support ticket count")

    if not 0 <= customer.satisfaction <= 10:
        errors.append("satisfaction must be between 0 and 10")

    if not 0 <= customer.adoption_rate <= 1:
        errors.append("adoption rate must be between 0 and 1")

    if customer.decision_cycle_days < 0:
        errors.append("negative decision cycle")

    return errors


for customer in customers:
    print(customer.customer_id, "valid:", validate_customer(customer) == [])


# ============================================================================
# 23. PRIVACY AND RESPONSIBLE CUSTOMER UNDERSTANDING
# ============================================================================

@dataclass
class DataField:
    name: str
    purpose: str
    sensitivity: str
    retention_days: Optional[int] = None


data_catalog = [
    DataField("customer_id", "account identification", "low", 3650),
    DataField("usage_events", "product improvement", "medium", 730),
    DataField("support_topic", "service improvement", "medium", 730),
    DataField("email", "account communication", "personal", 3650),
]

for field_definition in data_catalog:
    print(
        field_definition.name,
        "| purpose:",
        field_definition.purpose,
        "| sensitivity:",
        field_definition.sensitivity,
    )

explain(
    """
Responsible customer understanding requires purpose limitation, appropriate
access controls, data minimization, retention rules, transparency, security,
and compliance with applicable privacy requirements.

Do not collect sensitive personal information merely because it might be
interesting. Do not infer protected characteristics from weak proxies.
Separate research evidence from assumptions. Restrict access to customer data
according to legitimate business need.

Customer understanding should improve the product and customer experience,
not become an excuse for unnecessary surveillance.
"""
)


# ============================================================================
# 24. EXPERIMENTATION
# ============================================================================

@dataclass
class ExperimentResult:
    variant: str
    visitors: int
    conversions: int

    @property
    def conversion_rate(self) -> float:
        if self.visitors <= 0:
            raise ValueError("visitors must be positive")
        return self.conversions / self.visitors


control = ExperimentResult("control", 5000, 450)
variant = ExperimentResult("simplified onboarding", 5000, 525)

print(
    "Control conversion:",
    round(control.conversion_rate * 100, 2),
    "%",
)
print(
    "Variant conversion:",
    round(variant.conversion_rate * 100, 2),
    "%",
)


def absolute_lift(
    control_rate: float,
    variant_rate: float,
) -> float:
    return variant_rate - control_rate


def relative_lift(
    control_rate: float,
    variant_rate: float,
) -> float:
    if control_rate == 0:
        raise ValueError("control rate cannot be zero")
    return (variant_rate - control_rate) / control_rate


print(
    "Absolute lift:",
    round(
        absolute_lift(
            control.conversion_rate,
            variant.conversion_rate,
        ) * 100,
        2,
    ),
    "percentage points",
)

print(
    "Relative lift:",
    round(
        relative_lift(
            control.conversion_rate,
            variant.conversion_rate,
        ) * 100,
        2,
    ),
    "%",
)

explain(
    """
A difference in observed conversion rates does not automatically establish
causality. Experimental design must consider randomization, sample size,
measurement integrity, exposure, contamination, novelty effects, statistical
uncertainty, and the business metric being optimized.
"""
)


# ============================================================================
# 25. CUSTOMER DECISION MAP
# ============================================================================

@dataclass
class DecisionFactor:
    name: str
    user_weight: float
    buyer_weight: float
    decision_maker_weight: float
    influencer_weight: float

    def weighted_importance(self) -> float:
        return mean([
            self.user_weight,
            self.buyer_weight,
            self.decision_maker_weight,
            self.influencer_weight,
        ])


decision_factors = [
    DecisionFactor("ease of use", 10, 5, 6, 7),
    DecisionFactor("price", 6, 10, 8, 4),
    DecisionFactor("security", 5, 6, 10, 9),
    DecisionFactor("integration", 8, 7, 9, 10),
]

for factor in decision_factors:
    print(
        factor.name,
        "average role importance:",
        round(factor.weighted_importance(), 2),
    )


# ============================================================================
# 26. CUSTOMER INTELLIGENCE PIPELINE
# ============================================================================

@dataclass
class CustomerInsight:
    customer_id: str
    segment: str
    health_score: float
    primary_need: str
    journey_friction: float
    evidence_count: int

    def risk_level(self) -> str:
        if self.health_score < 40 or self.journey_friction >= 8:
            return "high"
        if self.health_score < 70 or self.journey_friction >= 5:
            return "medium"
        return "low"


def build_customer_insight(
    customer: Customer,
    primary_need: str,
    friction: float,
    evidence_count: int,
) -> CustomerInsight:
    return CustomerInsight(
        customer_id=customer.customer_id,
        segment=f"{segment_by_company_size(customer)} / "
        f"{segment_by_adoption(customer)}",
        health_score=customer_health_score(customer),
        primary_need=primary_need,
        journey_friction=friction,
        evidence_count=evidence_count,
    )


insights = [
    build_customer_insight(customers[0], "simpler reporting", 4.0, 8),
    build_customer_insight(customers[1], "easier onboarding", 8.5, 12),
    build_customer_insight(customers[2], "security controls", 3.0, 15),
]

for insight in insights:
    print(
        insight.customer_id,
        "|",
        insight.segment,
        "| health:",
        round(insight.health_score, 1),
        "| risk:",
        insight.risk_level(),
    )


# ============================================================================
# 27. ADVANCED: EVIDENCE-CONFIDENT PERSONA
# ============================================================================

@dataclass
class PersonaClaim:
    claim: str
    source_count: int
    sample_size: int
    confidence: float

    def adjusted_confidence(self) -> float:
        source_factor = min(1.0, self.source_count / 3.0)
        sample_factor = min(1.0, self.sample_size / 100.0)
        return self.confidence * (0.6 * source_factor + 0.4 * sample_factor)


claims = [
    PersonaClaim(
        "Configuration complexity is a major onboarding problem.",
        3,
        1500,
        0.90,
    ),
    PersonaClaim(
        "Senior buyers prioritize security documentation.",
        2,
        28,
        0.80,
    ),
]

for claim in claims:
    print(
        claim.claim,
        "| adjusted confidence:",
        round(claim.adjusted_confidence(), 3),
    )


# ============================================================================
# 28. ADVANCED: SEGMENT PROFILE
# ============================================================================

@dataclass
class SegmentProfile:
    name: str
    members: List[Customer]

    def average_value(self) -> float:
        if not self.members:
            return 0.0
        return mean(customer.annual_value for customer in self.members)

    def average_satisfaction(self) -> float:
        if not self.members:
            return 0.0
        return mean(customer.satisfaction for customer in self.members)

    def average_adoption(self) -> float:
        if not self.members:
            return 0.0
        return mean(customer.adoption_rate for customer in self.members)


segments: Dict[str, List[Customer]] = defaultdict(list)

for customer in customers:
    segments[segment_by_company_size(customer)].append(customer)

for name, members in segments.items():
    profile = SegmentProfile(name, members)
    print(
        name,
        "| members:", len(members),
        "| average value:", round(profile.average_value(), 2),
        "| satisfaction:", round(profile.average_satisfaction(), 2),
        "| adoption:", round(profile.average_adoption(), 3),
    )


# ============================================================================
# 29. COMMON MISTAKES
# ============================================================================

common_mistakes = [
    "Treating the buyer and user as automatically identical.",
    "Creating personas from imagination rather than evidence.",
    "Confusing demographics with motivations.",
    "Relying only on surveys or only on analytics.",
    "Using averages that hide important segments.",
    "Treating correlation as causation.",
    "Ignoring non-buyers and churned customers.",
    "Optimizing for clicks instead of meaningful outcomes.",
    "Collecting unnecessary personal data.",
    "Assuming one persona explains every customer.",
]

for number, mistake in enumerate(common_mistakes, start=1):
    print(f"{number}. {mistake}")


# ============================================================================
# 30. EDGE CASES
# ============================================================================

edge_cases = [
    ("Same person has every role", "Common in individual consumer purchases."),
    ("One buyer represents many users", "Common in enterprise procurement."),
    ("Many influencers", "Possible when technical, financial, and legal reviews coexist."),
    ("User rejects the product but buyer renews", "Role-specific incentives can differ."),
    ("Customer never uses the purchased feature", "Purchase does not prove adoption."),
    ("High satisfaction but low usage", "Satisfaction alone does not prove product value."),
    ("High usage but low satisfaction", "Usage may be necessary rather than voluntary."),
]

for case, implication in edge_cases:
    print(case, "->", implication)


# ============================================================================
# 31. TESTS
# ============================================================================

class CustomerUnderstandingTests(unittest.TestCase):
    def test_ltv(self) -> None:
        self.assertEqual(
            estimated_lifetime_value(100, 2, 3, 0.5),
            300.0,
        )

    def test_zero_vector_similarity(self) -> None:
        self.assertEqual(
            cosine_similarity({"a": 0}, {"a": 1}),
            0.0,
        )

    def test_retention(self) -> None:
        self.assertAlmostEqual(
            monthly_retention(100, 90),
            0.9,
        )

    def test_customer_validation(self) -> None:
        valid_customer = customers[0]
        self.assertEqual(validate_customer(valid_customer), [])

    def test_negative_ltv_rejected(self) -> None:
        with self.assertRaises(ValueError):
            estimated_lifetime_value(-1, 2, 3, 0.5)


def run_tests() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        CustomerUnderstandingTests
    )
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


# ============================================================================
# 32. STUDY CHECKLIST
# ============================================================================

section("Customer understanding study checklist")

checklist = [
    "Identify the customer relationship.",
    "Separate customer, user, buyer, decision-maker, and influencer roles.",
    "Identify functional and emotional needs.",
    "Document pains, desired outcomes, and buying triggers.",
    "Collect evidence from multiple research methods.",
    "Separate observed behavior from stated preference.",
    "Create evidence-based personas.",
    "Segment customers using relevant variables.",
    "Map the customer journey and friction points.",
    "Understand decision criteria and objections.",
    "Measure adoption, retention, satisfaction, and value.",
    "Validate assumptions with experiments where appropriate.",
    "Audit data quality and research bias.",
    "Apply privacy, security, and data-minimization principles.",
    "Continuously update customer understanding as evidence changes.",
]

for item in checklist:
    print("[ ]", item)


# ============================================================================
# 33. EXECUTABLE TEST ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\nRunning validation tests...")
    run_tests()
    print("\nCustomer understanding examples completed successfully.")
