"""
Competitive Intelligence: A Complete Practical Study

This standalone program teaches competitive intelligence (CI) from beginner
through advanced level and demonstrates a complete competitor-research
workflow using simulated, structured data.

The program covers:
- Competitor identification and classification
- Market segmentation
- Competitor profiles
- Product and feature comparison
- Pricing analysis
- Positioning analysis
- Customer-review analysis
- Strengths and weaknesses
- Website and traffic indicators
- Company and funding indicators
- Competitive scoring
- Opportunity-gap analysis
- Strategic implications
- Evidence quality
- Confidence levels
- Data normalization
- Trend analysis
- Scenario analysis
- Ethical and legal boundaries
- Basic statistical analysis
- A reusable CI pipeline

No external packages are required.
The data is intentionally simulated. Tools such as Similarweb and Crunchbase
can provide real-world inputs, but this script does not call their APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import re


# ============================================================================
# 1. FUNDAMENTAL TERMINOLOGY
# ============================================================================

class CompetitorType(Enum):
    DIRECT = "Direct"
    INDIRECT = "Indirect"
    POTENTIAL = "Potential"


class EvidenceQuality(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Evidence:
    """
    Evidence is separated from interpretation.

    A CI system should preserve where a claim came from and how reliable
    that source is rather than treating every observation as equally certain.
    """
    source: str
    observation: str
    quality: EvidenceQuality
    collected_date: str = "2026-09-27"

    def reliability_weight(self) -> float:
        return {
            EvidenceQuality.HIGH: 1.0,
            EvidenceQuality.MEDIUM: 0.7,
            EvidenceQuality.LOW: 0.4,
        }[self.quality]


@dataclass
class Review:
    rating: float
    text: str
    source: str

    def sentiment(self) -> str:
        """
        A deliberately small rule-based classifier.

        Real production systems can use a trained NLP model, but simple
        transparent rules are useful for demonstrating the mechanics.
        """
        positive_words = {
            "easy", "fast", "excellent", "helpful", "simple", "great",
            "reliable", "useful", "intuitive", "good", "powerful"
        }
        negative_words = {
            "slow", "expensive", "confusing", "difficult", "poor",
            "limited", "buggy", "complex", "missing", "bad"
        }

        words = set(re.findall(r"[a-z]+", self.text.lower()))
        positive = len(words & positive_words)
        negative = len(words & negative_words)

        if positive > negative:
            return "positive"
        if negative > positive:
            return "negative"
        return "neutral"


@dataclass
class PricingPlan:
    name: str
    monthly_price: float
    annual_discount: float
    included_units: int

    def effective_monthly_annual_price(self) -> float:
        return self.monthly_price * (1 - self.annual_discount)


@dataclass
class Competitor:
    name: str
    competitor_type: CompetitorType
    segment: str
    target_customer: str
    primary_positioning: str
    website_visits_millions: float
    visit_growth_percent: float
    estimated_funding_millions: float
    employee_count: int
    plans: List[PricingPlan]
    features: Dict[str, float]
    reviews: List[Review]
    evidence: List[Evidence] = field(default_factory=list)

    def average_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return mean(review.rating for review in self.reviews)

    def review_sentiment_ratio(self) -> float:
        """
        Returns positive reviews / all reviews.

        This is a descriptive metric, not a statement about true customer
        satisfaction because review samples can be biased.
        """
        if not self.reviews:
            return 0.0
        positive = sum(r.sentiment() == "positive" for r in self.reviews)
        return positive / len(self.reviews)

    def entry_price(self) -> float:
        if not self.plans:
            return 0.0
        return min(plan.monthly_price for plan in self.plans)


# ============================================================================
# 2. SAMPLE MARKET DATA
# ============================================================================

def create_sample_competitors() -> List[Competitor]:
    """
    Creates fictional companies.

    Names and figures are synthetic and are not claims about real companies.
    The workflow can be fed with real research data obtained from appropriate
    public sources and authorized commercial datasets.
    """
    return [
        Competitor(
            name="MarketPilot",
            competitor_type=CompetitorType.DIRECT,
            segment="SMB intelligence",
            target_customer="Small and medium businesses",
            primary_positioning="Affordable competitive monitoring",
            website_visits_millions=4.8,
            visit_growth_percent=12.0,
            estimated_funding_millions=18,
            employee_count=95,
            plans=[
                PricingPlan("Starter", 49, 0.15, 5),
                PricingPlan("Growth", 129, 0.20, 20),
                PricingPlan("Enterprise", 399, 0.25, 100),
            ],
            features={
                "competitor_tracking": 9,
                "pricing_monitoring": 8,
                "review_analysis": 6,
                "market_reports": 7,
                "alerts": 9,
                "api": 5,
            },
            reviews=[
                Review(4.5, "Easy monitoring and helpful alerts", "ReviewSite"),
                Review(4.0, "Good pricing but reporting is limited", "ReviewSite"),
                Review(3.5, "Simple interface but API is confusing", "ReviewSite"),
            ],
            evidence=[
                Evidence("Company website", "Three commercial tiers", EvidenceQuality.HIGH),
                Evidence("Traffic intelligence", "Growing website traffic", EvidenceQuality.MEDIUM),
                Evidence("Customer reviews", "Users value monitoring", EvidenceQuality.MEDIUM),
            ],
        ),
        Competitor(
            name="InsightForge",
            competitor_type=CompetitorType.DIRECT,
            segment="Enterprise intelligence",
            target_customer="Large organizations",
            primary_positioning="Deep enterprise competitive intelligence",
            website_visits_millions=7.2,
            visit_growth_percent=6.0,
            estimated_funding_millions=65,
            employee_count=310,
            plans=[
                PricingPlan("Professional", 299, 0.10, 25),
                PricingPlan("Enterprise", 899, 0.15, 150),
            ],
            features={
                "competitor_tracking": 10,
                "pricing_monitoring": 9,
                "review_analysis": 8,
                "market_reports": 10,
                "alerts": 8,
                "api": 9,
            },
            reviews=[
                Review(4.3, "Powerful reports but expensive", "ReviewSite"),
                Review(4.1, "Excellent data but complex setup", "ReviewSite"),
                Review(3.8, "Useful enterprise features but difficult", "ReviewSite"),
            ],
            evidence=[
                Evidence("Company website", "Enterprise-oriented plans", EvidenceQuality.HIGH),
                Evidence("Company database", "Substantial funding reported", EvidenceQuality.MEDIUM),
                Evidence("Customer reviews", "Strong reporting with complexity", EvidenceQuality.MEDIUM),
            ],
        ),
        Competitor(
            name="ReviewLens",
            competitor_type=CompetitorType.INDIRECT,
            segment="Customer intelligence",
            target_customer="Consumer brands",
            primary_positioning="Customer-review analytics",
            website_visits_millions=3.1,
            visit_growth_percent=19.0,
            estimated_funding_millions=11,
            employee_count=72,
            plans=[
                PricingPlan("Basic", 39, 0.10, 10),
                PricingPlan("Pro", 99, 0.15, 40),
            ],
            features={
                "competitor_tracking": 5,
                "pricing_monitoring": 4,
                "review_analysis": 10,
                "market_reports": 6,
                "alerts": 7,
                "api": 6,
            },
            reviews=[
                Review(4.6, "Excellent review analysis and easy interface", "ReviewSite"),
                Review(4.4, "Fast and useful customer insights", "ReviewSite"),
                Review(4.2, "Great product but missing market reports", "ReviewSite"),
            ],
            evidence=[
                Evidence("Company website", "Review-centric product", EvidenceQuality.HIGH),
                Evidence("Traffic intelligence", "High traffic growth", EvidenceQuality.MEDIUM),
            ],
        ),
        Competitor(
            name="DataAtlas",
            competitor_type=CompetitorType.POTENTIAL,
            segment="Business data",
            target_customer="Technology companies",
            primary_positioning="Large-scale company and market data",
            website_visits_millions=9.4,
            visit_growth_percent=3.0,
            estimated_funding_millions=120,
            employee_count=620,
            plans=[
                PricingPlan("Data", 499, 0.10, 50),
                PricingPlan("Enterprise", 1499, 0.20, 300),
            ],
            features={
                "competitor_tracking": 8,
                "pricing_monitoring": 5,
                "review_analysis": 3,
                "market_reports": 9,
                "alerts": 6,
                "api": 10,
            },
            reviews=[
                Review(4.0, "Powerful data but expensive", "ReviewSite"),
                Review(3.9, "Excellent API but complex", "ReviewSite"),
                Review(4.1, "Reliable datasets", "ReviewSite"),
            ],
            evidence=[
                Evidence("Company database", "Large business-data provider", EvidenceQuality.MEDIUM),
                Evidence("Traffic intelligence", "Large website audience", EvidenceQuality.MEDIUM),
            ],
        ),
    ]


# ============================================================================
# 3. MARKET DISCOVERY
# ============================================================================

def classify_competitors(
    competitors: Sequence[Competitor],
) -> Dict[CompetitorType, List[Competitor]]:
    result = {category: [] for category in CompetitorType}
    for competitor in competitors:
        result[competitor.competitor_type].append(competitor)
    return result


def display_market_map(competitors: Sequence[Competitor]) -> None:
    print("\nMARKET MAP")
    print("-" * 90)
    print(
        f"{'Company':<18}"
        f"{'Type':<12}"
        f"{'Segment':<25}"
        f"{'Positioning'}"
    )
    print("-" * 90)

    for company in competitors:
        print(
            f"{company.name:<18}"
            f"{company.competitor_type.value:<12}"
            f"{company.segment:<25}"
            f"{company.primary_positioning}"
        )


# ============================================================================
# 4. NORMALIZATION
# ============================================================================

def min_max_normalize(values: Sequence[float]) -> List[float]:
    """
    Converts values into a 0-100 range.

    If every value is identical, each receives 50 to avoid division by zero.
    """
    if not values:
        return []

    minimum = min(values)
    maximum = max(values)

    if minimum == maximum:
        return [50.0 for _ in values]

    return [
        100 * (value - minimum) / (maximum - minimum)
        for value in values
    ]


def feature_average(competitor: Competitor) -> float:
    if not competitor.features:
        return 0.0
    return mean(competitor.features.values())


# ============================================================================
# 5. PRICING INTELLIGENCE
# ============================================================================

def pricing_table(competitors: Sequence[Competitor]) -> None:
    print("\nPRICING INTELLIGENCE")
    print("-" * 90)

    for competitor in competitors:
        print(f"\n{competitor.name}")
        for plan in competitor.plans:
            annual_price = plan.effective_monthly_annual_price()
            print(
                f"  {plan.name:<12}"
                f" Monthly: ${plan.monthly_price:>7.2f}"
                f"  Effective annual monthly: ${annual_price:>7.2f}"
                f"  Units: {plan.included_units}"
            )


def price_positioning(competitors: Sequence[Competitor]) -> Dict[str, str]:
    prices = {c.name: c.entry_price() for c in competitors}
    ordered = sorted(prices.items(), key=lambda item: item[1])

    if not ordered:
        return {}

    result = {}
    for index, (name, price) in enumerate(ordered):
        if index == 0:
            result[name] = "Lowest entry price"
        elif index == len(ordered) - 1:
            result[name] = "Highest entry price"
        else:
            result[name] = "Mid-market entry price"
    return result


# ============================================================================
# 6. POSITIONING ANALYSIS
# ============================================================================

def positioning_matrix(
    competitors: Sequence[Competitor],
) -> List[Tuple[str, float, float]]:
    """
    Produces a conceptual two-dimensional positioning map:

    X = feature breadth
    Y = normalized entry-price level

    The result describes observable dimensions. It does not declare a
    universally superior competitor.
    """
    feature_values = [feature_average(c) for c in competitors]
    price_values = [c.entry_price() for c in competitors]

    normalized_features = min_max_normalize(feature_values)
    normalized_prices = min_max_normalize(price_values)

    return [
        (c.name, feature_score, price_score)
        for c, feature_score, price_score
        in zip(competitors, normalized_features, normalized_prices)
    ]


# ============================================================================
# 7. REVIEW INTELLIGENCE
# ============================================================================

def review_analysis(competitors: Sequence[Competitor]) -> None:
    print("\nCUSTOMER-REVIEW ANALYSIS")
    print("-" * 90)

    for competitor in competitors:
        print(
            f"{competitor.name:<18}"
            f" Average rating: {competitor.average_rating():.2f}"
            f"  Positive ratio: {competitor.review_sentiment_ratio():.1%}"
        )

        for review in competitor.reviews:
            print(
                f"    {review.rating:.1f}/5 "
                f"{review.sentiment():<8} "
                f"{review.text}"
            )


def extract_review_themes(reviews: Iterable[Review]) -> Dict[str, int]:
    """
    Counts simple recurring themes.

    Production review mining normally needs robust NLP, language detection,
    spam filtering, duplicate detection, aspect extraction, and sampling
    controls.
    """
    themes = {
        "price": {"expensive", "pricing"},
        "usability": {"easy", "simple", "confusing", "difficult"},
        "performance": {"fast", "slow"},
        "quality": {"excellent", "good", "great", "poor"},
        "capability": {"powerful", "limited", "missing"},
        "reliability": {"reliable", "buggy"},
    }

    counts = {theme: 0 for theme in themes}

    for review in reviews:
        words = set(re.findall(r"[a-z]+", review.text.lower()))
        for theme, keywords in themes.items():
            if words & keywords:
                counts[theme] += 1

    return counts


# ============================================================================
# 8. SWOT-STYLE EVIDENCE MAPPING
# ============================================================================

def identify_weakness_signals(competitor: Competitor) -> List[str]:
    signals = []

    if competitor.average_rating() < 4.0:
        signals.append("Review rating is below 4.0 in the supplied sample.")

    if competitor.entry_price() > 250:
        signals.append("High entry price may constrain price-sensitive buyers.")

    if competitor.features.get("api", 0) < 7:
        signals.append("API capability scores relatively low in the supplied model.")

    if competitor.features.get("review_analysis", 0) < 6:
        signals.append("Review-analysis capability is limited in the supplied model.")

    return signals


def identify_strength_signals(competitor: Competitor) -> List[str]:
    signals = []

    if competitor.features.get("competitor_tracking", 0) >= 9:
        signals.append("Strong competitor-tracking capability.")

    if competitor.features.get("api", 0) >= 9:
        signals.append("Strong API capability.")

    if competitor.website_visits_millions >= 7:
        signals.append("Large website audience in the supplied traffic dataset.")

    if competitor.visit_growth_percent >= 15:
        signals.append("High website-traffic growth in the supplied dataset.")

    return signals


# ============================================================================
# 9. OPPORTUNITY-GAP ANALYSIS
# ============================================================================

@dataclass
class Opportunity:
    capability: str
    market_gap: float
    strategic_importance: float
    evidence_strength: float
    opportunity_score: float


def opportunity_analysis(
    competitors: Sequence[Competitor],
    target_capabilities: Sequence[str],
) -> List[Opportunity]:
    """
    A gap is defined here as 10 minus the average competitor capability score.

    This is a modeling assumption, not an objective measurement of market
    opportunity. The final score combines:
      - capability gap
      - strategic importance
      - evidence strength
    """
    opportunities = []

    for capability in target_capabilities:
        scores = [
            competitor.features.get(capability, 0)
            for competitor in competitors
        ]

        if not scores:
            continue

        average_score = mean(scores)
        gap = max(0.0, 10.0 - average_score)

        importance = {
            "competitor_tracking": 0.9,
            "pricing_monitoring": 1.0,
            "review_analysis": 0.9,
            "market_reports": 0.8,
            "alerts": 0.7,
            "api": 0.85,
        }.get(capability, 0.5)

        evidence_strength = mean(
            evidence.reliability_weight()
            for competitor in competitors
            for evidence in competitor.evidence
        )

        score = gap * importance * evidence_strength

        opportunities.append(
            Opportunity(
                capability=capability,
                market_gap=gap,
                strategic_importance=importance,
                evidence_strength=evidence_strength,
                opportunity_score=score,
            )
        )

    return sorted(
        opportunities,
        key=lambda opportunity: opportunity.opportunity_score,
        reverse=True,
    )


# ============================================================================
# 10. COMPETITIVE INTELLIGENCE SCORECARD
# ============================================================================

@dataclass
class ScoreWeights:
    traffic: float = 0.15
    traffic_growth: float = 0.10
    product: float = 0.25
    reviews: float = 0.15
    affordability: float = 0.15
    evidence: float = 0.20


def calculate_scorecard(
    competitors: Sequence[Competitor],
    weights: ScoreWeights,
) -> Dict[str, Dict[str, float]]:
    """
    Produces a multidimensional descriptive scorecard.

    The dimensions should be interpreted independently. The scorecard is
    useful for structured analysis, but it is sensitive to assumptions,
    weights, data quality, sampling bias, and missing data.
    """
    traffic = min_max_normalize(
        [c.website_visits_millions for c in competitors]
    )
    growth = min_max_normalize(
        [c.visit_growth_percent for c in competitors]
    )
    product = min_max_normalize(
        [feature_average(c) for c in competitors]
    )
    reviews = min_max_normalize(
        [c.average_rating() for c in competitors]
    )

    prices = [c.entry_price() for c in competitors]
    affordability = [
        100 - value for value in min_max_normalize(prices)
    ]

    evidence = [
        100 * mean(e.reliability_weight() for e in c.evidence)
        if c.evidence else 0
        for c in competitors
    ]

    result = {}

    for index, competitor in enumerate(competitors):
        result[competitor.name] = {
            "traffic": traffic[index],
            "traffic_growth": growth[index],
            "product": product[index],
            "reviews": reviews[index],
            "affordability": affordability[index],
            "evidence": evidence[index],
        }

    return result


# ============================================================================
# 11. STATISTICS
# ============================================================================

def correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    """
    Pearson correlation coefficient.

    Returns 0 for degenerate input where variance is zero.
    """
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0

    x_mean = mean(xs)
    y_mean = mean(ys)

    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in zip(xs, ys)
    )

    denominator_x = sqrt(
        sum((x - x_mean) ** 2 for x in xs)
    )
    denominator_y = sqrt(
        sum((y - y_mean) ** 2 for y in ys)
    )

    denominator = denominator_x * denominator_y

    if denominator == 0:
        return 0.0

    return numerator / denominator


def traffic_growth_correlation(competitors: Sequence[Competitor]) -> float:
    traffic = [c.website_visits_millions for c in competitors]
    growth = [c.visit_growth_percent for c in competitors]
    return correlation(traffic, growth)


# ============================================================================
# 12. TREND AND SCENARIO ANALYSIS
# ============================================================================

@dataclass
class MonthlyMetric:
    month: str
    value: float


def compound_growth(value: float, annual_rate: float, years: float) -> float:
    """
    Applies compound growth.

    This is a mathematical scenario model, not a forecast of actual business
    performance.
    """
    return value * ((1 + annual_rate) ** years)


def project_traffic(
    competitor: Competitor,
    years: int = 3,
) -> float:
    annual_rate = competitor.visit_growth_percent / 100
    return compound_growth(
        competitor.website_visits_millions,
        annual_rate,
        years,
    )


def scenario_table(competitors: Sequence[Competitor]) -> None:
    print("\nTHREE-YEAR TRAFFIC SCENARIO")
    print("-" * 90)

    for competitor in competitors:
        projected = project_traffic(competitor)
        print(
            f"{competitor.name:<18}"
            f" Current: {competitor.website_visits_millions:>6.2f}M"
            f"  Growth assumption: {competitor.visit_growth_percent:>5.1f}%"
            f"  Scenario: {projected:>9.2f}M"
        )


# ============================================================================
# 13. DATA-QUALITY CHECKS
# ============================================================================

def validate_competitor(competitor: Competitor) -> List[str]:
    problems = []

    if competitor.website_visits_millions < 0:
        problems.append("Website visits cannot be negative.")

    if competitor.visit_growth_percent < -100:
        problems.append("Traffic decline cannot exceed -100%.")

    if competitor.estimated_funding_millions < 0:
        problems.append("Funding cannot be negative.")

    for plan in competitor.plans:
        if plan.monthly_price < 0:
            problems.append(f"Negative price in plan {plan.name}.")
        if not 0 <= plan.annual_discount <= 1:
            problems.append(
                f"Annual discount for {plan.name} must be between 0 and 1."
            )
        if plan.included_units < 0:
            problems.append(
                f"Included units for {plan.name} cannot be negative."
            )

    for review in competitor.reviews:
        if not 0 <= review.rating <= 5:
            problems.append(
                f"Review rating {review.rating} is outside 0-5."
            )

    return problems


def run_data_quality_checks(competitors: Sequence[Competitor]) -> None:
    print("\nDATA-QUALITY CHECK")
    print("-" * 90)

    any_problem = False

    for competitor in competitors:
        problems = validate_competitor(competitor)

        if problems:
            any_problem = True
            print(f"{competitor.name}:")
            for problem in problems:
                print(f"  ERROR: {problem}")
        else:
            print(f"{competitor.name}: OK")

    if not any_problem:
        print("All supplied records passed the validation rules.")


# ============================================================================
# 14. ETHICAL AND LEGAL CI RULES
# ============================================================================

def ethical_ci_check() -> List[str]:
    """
    A practical boundary checklist.

    Competitive intelligence should use lawful, authorized, appropriately
    sourced information. This example explicitly excludes credential theft,
    bypassing access controls, deception, unauthorized scraping, malware,
    confidential information theft, and other prohibited acquisition methods.
    """
    return [
        "Use public, licensed, or explicitly authorized information.",
        "Respect terms of service, access controls, robots policies, and laws.",
        "Do not obtain passwords, private records, confidential documents, or trade secrets.",
        "Do not impersonate customers or employees to obtain restricted information.",
        "Separate verified observations from assumptions and interpretation.",
        "Record source, collection date, methodology, and evidence quality.",
        "Avoid presenting estimates as confirmed facts.",
        "Protect sensitive internal research and credentials.",
    ]


# ============================================================================
# 15. CI REPORT GENERATION
# ============================================================================

def generate_report(competitors: Sequence[Competitor]) -> str:
    """
    Generates a compact text report from the structured data.
    """
    lines = [
        "=" * 90,
        "COMPETITIVE INTELLIGENCE REPORT",
        "=" * 90,
        "",
        "Market participants:",
    ]

    for competitor in competitors:
        lines.append(
            f"- {competitor.name}: "
            f"{competitor.competitor_type.value}, "
            f"{competitor.segment}"
        )

    lines.extend(
        [
            "",
            "Pricing:",
        ]
    )

    for competitor in competitors:
        lines.append(
            f"- {competitor.name}: entry price ${competitor.entry_price():.2f}/month"
        )

    lines.extend(
        [
            "",
            "Review observations:",
        ]
    )

    for competitor in competitors:
        lines.append(
            f"- {competitor.name}: "
            f"{competitor.average_rating():.2f}/5 average in supplied sample"
        )

    lines.extend(
        [
            "",
            "Evidence caveat:",
            "This report uses synthetic demonstration data. "
            "It is a model of a CI workflow rather than a factual report "
            "about real companies.",
        ]
    )

    return "\n".join(lines)


# ============================================================================
# 16. END-TO-END WORKFLOW
# ============================================================================

def run_competitive_intelligence_workflow() -> None:
    competitors = create_sample_competitors()

    print("=" * 90)
    print("COMPETITIVE INTELLIGENCE LEARNING LAB")
    print("=" * 90)

    # Step 1: Discover and classify competitors.
    display_market_map(competitors)

    classified = classify_competitors(competitors)

    print("\nCOMPETITOR CLASSIFICATION")
    print("-" * 90)

    for category, companies in classified.items():
        names = ", ".join(company.name for company in companies)
        print(f"{category.value}: {names or 'None'}")

    # Step 2: Validate raw research data.
    run_data_quality_checks(competitors)

    # Step 3: Analyze pricing.
    pricing_table(competitors)

    print("\nPRICE POSITIONING")
    print("-" * 90)

    for name, position in price_positioning(competitors).items():
        print(f"{name:<18} {position}")

    # Step 4: Analyze product positioning.
    print("\nPOSITIONING MATRIX")
    print("-" * 90)
    print(f"{'Company':<18}{'Feature index':>18}{'Price index':>18}")

    for name, feature_score, price_score in positioning_matrix(competitors):
        print(
            f"{name:<18}"
            f"{feature_score:>18.2f}"
            f"{price_score:>18.2f}"
        )

    # Step 5: Analyze customer reviews.
    review_analysis(competitors)

    print("\nREVIEW THEMES")
    print("-" * 90)

    for competitor in competitors:
        themes = extract_review_themes(competitor.reviews)
        print(f"{competitor.name}: {themes}")

    # Step 6: Identify documented signals.
    print("\nSTRENGTH SIGNALS AND WEAKNESS SIGNALS")
    print("-" * 90)

    for competitor in competitors:
        print(f"\n{competitor.name}")

        strengths = identify_strength_signals(competitor)
        weaknesses = identify_weakness_signals(competitor)

        print("  Strength signals:")
        for signal in strengths or ["None identified by the supplied rules."]:
            print(f"    - {signal}")

        print("  Weakness signals:")
        for signal in weaknesses or ["None identified by the supplied rules."]:
            print(f"    - {signal}")

    # Step 7: Identify capability gaps.
    target_capabilities = [
        "competitor_tracking",
        "pricing_monitoring",
        "review_analysis",
        "market_reports",
        "alerts",
        "api",
    ]

    opportunities = opportunity_analysis(
        competitors,
        target_capabilities,
    )

    print("\nCAPABILITY GAP ANALYSIS")
    print("-" * 90)

    for opportunity in opportunities:
        print(
            f"{opportunity.capability:<24}"
            f" Gap: {opportunity.market_gap:>5.2f}"
            f" Importance: {opportunity.strategic_importance:>5.2f}"
            f" Evidence: {opportunity.evidence_strength:>5.2f}"
            f" Score: {opportunity.opportunity_score:>6.2f}"
        )

    # Step 8: Build multidimensional scorecard.
    scorecard = calculate_scorecard(
        competitors,
        ScoreWeights(),
    )

    print("\nMULTIDIMENSIONAL SCORECARD")
    print("-" * 90)

    for company, dimensions in scorecard.items():
        print(f"\n{company}")
        for dimension, value in dimensions.items():
            print(f"  {dimension:<20} {value:>6.2f}")

    # Step 9: Statistical relationship.
    correlation_value = traffic_growth_correlation(competitors)

    print("\nTRAFFIC / TRAFFIC-GROWTH CORRELATION")
    print("-" * 90)
    print(
        f"Pearson correlation: {correlation_value:.3f}"
    )
    print(
        "Correlation describes association in the supplied sample; "
        "it does not establish causation."
    )

    # Step 10: Scenario analysis.
    scenario_table(competitors)

    # Step 11: Ethical boundary checklist.
    print("\nETHICAL AND LEGAL CI CHECKLIST")
    print("-" * 90)

    for rule in ethical_ci_check():
        print(f"- {rule}")

    # Step 12: Produce a final text artifact.
    print("\nGENERATED REPORT")
    print(generate_report(competitors))

    print("\nEND OF COMPETITIVE INTELLIGENCE STUDY")


# ============================================================================
# 17. UNIT-STYLE SELF TESTS
# ============================================================================

def run_self_tests() -> None:
    """
    Small internal tests make the learning file executable as a study artifact
    while also demonstrating validation and regression testing.
    """
    assert min_max_normalize([10, 20, 30]) == [0.0, 50.0, 100.0]
    assert min_max_normalize([5, 5, 5]) == [50.0, 50.0, 50.0]

    plan = PricingPlan(
        name="Test",
        monthly_price=100,
        annual_discount=0.20,
        included_units=10,
    )
    assert plan.effective_monthly_annual_price() == 80

    review = Review(
        rating=4.5,
        text="Excellent and easy product",
        source="test",
    )
    assert review.sentiment() == "positive"

    competitor = Competitor(
        name="TestCo",
        competitor_type=CompetitorType.DIRECT,
        segment="Test",
        target_customer="Test customers",
        primary_positioning="Test positioning",
        website_visits_millions=1,
        visit_growth_percent=5,
        estimated_funding_millions=1,
        employee_count=10,
        plans=[plan],
        features={"api": 8},
        reviews=[review],
    )

    assert competitor.entry_price() == 100
    assert competitor.average_rating() == 4.5
    assert validate_competitor(competitor) == []

    print("Self-tests passed.")


# ============================================================================
# 18. PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run_self_tests()
    run_competitive_intelligence_workflow()
