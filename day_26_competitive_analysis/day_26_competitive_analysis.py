"""
Competitive Analysis
====================

A comprehensive, executable study file covering:
- Competitors and competitive landscapes
- Direct vs. indirect competition
- Market segmentation
- Competitor identification
- Feature comparison
- Weighted competitive analysis
- Positioning
- Differentiation
- Competitive matrices
- Feature parity and gaps
- Strengths and weaknesses
- Pricing and value analysis
- Strategic interpretation
- Scenario analysis
- Data validation
- Sensitivity analysis
- Performance considerations
- Practical limitations and common analytical mistakes

The examples use a fictional project-management software market so that the
analysis remains concrete without depending on external data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# ============================================================================
# 1. FOUNDATIONAL TERMINOLOGY
# ============================================================================

class CompetitionType(Enum):
    """Classification of how a competitor satisfies the same customer need."""

    DIRECT = "Direct"
    INDIRECT = "Indirect"
    POTENTIAL = "Potential"


class FeatureStatus(Enum):
    """Useful classification for comparing a feature across products."""

    ABSENT = "Absent"
    BASIC = "Basic"
    STRONG = "Strong"
    DIFFERENTIATED = "Differentiated"


@dataclass(frozen=True)
class Feature:
    """A customer-visible capability used in a competitive comparison."""

    name: str
    category: str
    description: str


@dataclass
class Competitor:
    """
    Represents a product or alternative competing for the same customer need.

    Scores use a 1-5 scale:
        1 = very weak
        2 = weak
        3 = adequate
        4 = strong
        5 = excellent
    """

    name: str
    competition_type: CompetitionType
    target_segment: str
    price_per_user: float
    scores: Dict[str, float]
    feature_status: Dict[str, FeatureStatus]
    positioning_statement: str = ""
    notes: List[str] = field(default_factory=list)

    def validate(self, criteria: Iterable[str]) -> None:
        """Validate that a competitor has usable scores for every criterion."""
        criteria = list(criteria)

        if not self.name.strip():
            raise ValueError("Competitor name cannot be empty.")

        if self.price_per_user < 0:
            raise ValueError("Price cannot be negative.")

        missing = [criterion for criterion in criteria if criterion not in self.scores]
        if missing:
            raise ValueError(
                f"{self.name} is missing scores for: {', '.join(missing)}"
            )

        for criterion, score in self.scores.items():
            if score < 1 or score > 5:
                raise ValueError(
                    f"{self.name}: score for '{criterion}' must be between 1 and 5."
                )


@dataclass(frozen=True)
class Criterion:
    """A decision criterion and its importance weight."""

    name: str
    weight: float
    description: str

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError("Criterion weight cannot be negative.")


@dataclass
class PositioningProfile:
    """Describes how a product is intended to occupy a market position."""

    product_name: str
    target_customer: str
    primary_need: str
    key_difference: str
    value_proposition: str
    proof_points: List[str]


# ============================================================================
# 2. BASIC DATA
# ============================================================================

FEATURES = [
    Feature(
        "Task Management",
        "Core",
        "Create, assign, prioritize, and track work."
    ),
    Feature(
        "Workflow Automation",
        "Automation",
        "Automate repetitive work and business processes."
    ),
    Feature(
        "Analytics",
        "Insights",
        "Measure team performance and operational outcomes."
    ),
    Feature(
        "AI Assistance",
        "Intelligence",
        "Use AI-supported functions for planning and work execution."
    ),
    Feature(
        "Integrations",
        "Platform",
        "Connect the product with external business systems."
    ),
    Feature(
        "Enterprise Security",
        "Security",
        "Support access control, governance, auditing, and security requirements."
    ),
]


# ============================================================================
# 3. COMPETITOR DATASET
# ============================================================================

COMPETITORS = [
    Competitor(
        name="TaskFlow",
        competition_type=CompetitionType.DIRECT,
        target_segment="SMB project teams",
        price_per_user=12,
        scores={
            "Ease of Use": 4.7,
            "Task Management": 4.6,
            "Workflow Automation": 4.1,
            "Analytics": 3.7,
            "AI Assistance": 3.6,
            "Integrations": 4.2,
            "Enterprise Security": 3.5,
            "Price Value": 4.5,
        },
        feature_status={
            "Task Management": FeatureStatus.STRONG,
            "Workflow Automation": FeatureStatus.STRONG,
            "Analytics": FeatureStatus.STRONG,
            "AI Assistance": FeatureStatus.BASIC,
            "Integrations": FeatureStatus.STRONG,
            "Enterprise Security": FeatureStatus.BASIC,
        },
        positioning_statement="Simple project management for growing teams.",
        notes=["Strong usability", "Competitive price", "Less enterprise depth"],
    ),
    Competitor(
        name="EnterpriseSuite",
        competition_type=CompetitionType.DIRECT,
        target_segment="Large enterprises",
        price_per_user=30,
        scores={
            "Ease of Use": 3.0,
            "Task Management": 4.5,
            "Workflow Automation": 4.7,
            "Analytics": 4.8,
            "AI Assistance": 4.2,
            "Integrations": 4.8,
            "Enterprise Security": 5.0,
            "Price Value": 3.0,
        },
        feature_status={
            "Task Management": FeatureStatus.STRONG,
            "Workflow Automation": FeatureStatus.DIFFERENTIATED,
            "Analytics": FeatureStatus.DIFFERENTIATED,
            "AI Assistance": FeatureStatus.STRONG,
            "Integrations": FeatureStatus.DIFFERENTIATED,
            "Enterprise Security": FeatureStatus.DIFFERENTIATED,
        },
        positioning_statement="Enterprise-grade work management at scale.",
        notes=["Strong governance", "High capability", "Higher cost and complexity"],
    ),
    Competitor(
        name="SpreadsheetPro",
        competition_type=CompetitionType.INDIRECT,
        target_segment="Small teams and individuals",
        price_per_user=8,
        scores={
            "Ease of Use": 4.2,
            "Task Management": 3.0,
            "Workflow Automation": 2.5,
            "Analytics": 3.6,
            "AI Assistance": 3.0,
            "Integrations": 3.9,
            "Enterprise Security": 3.0,
            "Price Value": 4.8,
        },
        feature_status={
            "Task Management": FeatureStatus.BASIC,
            "Workflow Automation": FeatureStatus.BASIC,
            "Analytics": FeatureStatus.STRONG,
            "AI Assistance": FeatureStatus.BASIC,
            "Integrations": FeatureStatus.STRONG,
            "Enterprise Security": FeatureStatus.BASIC,
        },
        positioning_statement="Flexible spreadsheet-based business analysis.",
        notes=["Very flexible", "Familiar workflow", "Requires manual configuration"],
    ),
    Competitor(
        name="EmailWorkflow",
        competition_type=CompetitionType.INDIRECT,
        target_segment="Small service businesses",
        price_per_user=5,
        scores={
            "Ease of Use": 4.8,
            "Task Management": 2.4,
            "Workflow Automation": 2.0,
            "Analytics": 1.8,
            "AI Assistance": 2.2,
            "Integrations": 3.5,
            "Enterprise Security": 3.2,
            "Price Value": 4.9,
        },
        feature_status={
            "Task Management": FeatureStatus.ABSENT,
            "Workflow Automation": FeatureStatus.BASIC,
            "Analytics": FeatureStatus.ABSENT,
            "AI Assistance": FeatureStatus.BASIC,
            "Integrations": FeatureStatus.BASIC,
            "Enterprise Security": FeatureStatus.BASIC,
        },
        positioning_statement="Use familiar communication tools to coordinate work.",
        notes=["Low switching cost", "Extremely familiar", "Poor visibility at scale"],
    ),
]


# ============================================================================
# 4. CRITERIA AND WEIGHTS
# ============================================================================

CRITERIA = [
    Criterion("Ease of Use", 0.15, "How quickly customers can understand and use the product."),
    Criterion("Task Management", 0.15, "Quality of core project and work management."),
    Criterion("Workflow Automation", 0.15, "Ability to automate recurring processes."),
    Criterion("Analytics", 0.10, "Quality of reporting and operational insight."),
    Criterion("AI Assistance", 0.10, "Quality and usefulness of intelligent assistance."),
    Criterion("Integrations", 0.10, "Breadth and usefulness of integrations."),
    Criterion("Enterprise Security", 0.10, "Security and governance capability."),
    Criterion("Price Value", 0.15, "Customer value relative to price."),
]


# ============================================================================
# 5. UTILITY FUNCTIONS
# ============================================================================

def weighted_score(
    competitor: Competitor,
    criteria: Sequence[Criterion],
) -> float:
    """
    Calculate a weighted competitive score.

    Formula:
        weighted score = Σ(score × criterion weight)
    """
    return sum(
        competitor.scores[criterion.name] * criterion.weight
        for criterion in criteria
    )


def total_weight(criteria: Sequence[Criterion]) -> float:
    """Return the sum of all criterion weights."""
    return sum(criterion.weight for criterion in criteria)


def normalize_weights(criteria: Sequence[Criterion]) -> List[Criterion]:
    """
    Normalize arbitrary weights to a total of 1.

    This is useful when analysts initially assign weights that do not sum to 1.
    """
    total = total_weight(criteria)

    if total <= 0:
        raise ValueError("At least one positive criterion weight is required.")

    return [
        Criterion(
            criterion.name,
            criterion.weight / total,
            criterion.description,
        )
        for criterion in criteria
    ]


def validate_competitor_dataset(
    competitors: Sequence[Competitor],
    criteria: Sequence[Criterion],
) -> None:
    """Validate the entire competitive dataset."""
    if not competitors:
        raise ValueError("At least one competitor is required.")

    for competitor in competitors:
        competitor.validate(criterion.name for criterion in criteria)


def classify_competitor(
    competitor: Competitor,
    target_customer: str,
    primary_need: str,
) -> str:
    """
    Explain competitor classification.

    Classification should be based on customer and need overlap, not simply
    whether two products appear in the same broad industry.
    """
    if competitor.competition_type == CompetitionType.DIRECT:
        return (
            f"{competitor.name} is direct because it targets "
            f"{target_customer} with a substantially similar solution to "
            f"{primary_need}."
        )

    if competitor.competition_type == CompetitionType.INDIRECT:
        return (
            f"{competitor.name} is indirect because customers can use it "
            f"to address part of the same underlying need through a different "
            f"solution."
        )

    return (
        f"{competitor.name} is considered potential competition because "
        f"its capabilities could be redirected toward the target need."
    )


def print_header(title: str) -> None:
    """Print a readable terminal section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_score_table(
    competitors: Sequence[Competitor],
    criteria: Sequence[Criterion],
) -> None:
    """Print weighted scores without requiring external libraries."""
    print(f"{'Competitor':<20} {'Type':<12} {'Weighted Score':>15}")
    print("-" * 52)

    for competitor in competitors:
        score = weighted_score(competitor, criteria)
        print(
            f"{competitor.name:<20} "
            f"{competitor.competition_type.value:<12} "
            f"{score:>15.2f}"
        )


def feature_gap_analysis(
    focal_product: Mapping[str, FeatureStatus],
    competitor: Competitor,
) -> List[str]:
    """
    Identify features where the competitor has a stronger status than the
    focal product.

    This is an analytical gap list, not automatically a product roadmap.
    """
    gaps = []

    strength_order = {
        FeatureStatus.ABSENT: 0,
        FeatureStatus.BASIC: 1,
        FeatureStatus.STRONG: 2,
        FeatureStatus.DIFFERENTIATED: 3,
    }

    for feature_name, competitor_status in competitor.feature_status.items():
        focal_status = focal_product.get(feature_name, FeatureStatus.ABSENT)

        if strength_order[competitor_status] > strength_order[focal_status]:
            gaps.append(
                f"{feature_name}: competitor={competitor_status.value}, "
                f"focal_product={focal_status.value}"
            )

    return gaps


def compare_feature(
    feature_name: str,
    competitors: Sequence[Competitor],
) -> Dict[str, FeatureStatus]:
    """Return one feature's status across competitors."""
    return {
        competitor.name: competitor.feature_status.get(
            feature_name,
            FeatureStatus.ABSENT,
        )
        for competitor in competitors
    }


def price_per_value_point(
    competitor: Competitor,
    criteria: Sequence[Criterion],
) -> float:
    """
    Calculate price divided by weighted capability score.

    Lower is not automatically 'better'. Price-value metrics require context
    such as willingness to pay, customer segment, switching cost, and margins.
    """
    score = weighted_score(competitor, criteria)

    if score == 0:
        return float("inf")

    return competitor.price_per_user / score


def euclidean_distance(
    point_a: Sequence[float],
    point_b: Sequence[float],
) -> float:
    """Calculate Euclidean distance between two equal-length points."""
    if len(point_a) != len(point_b):
        raise ValueError("Points must have equal dimensions.")

    return sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


def competitive_position_vector(
    competitor: Competitor,
    dimensions: Sequence[str],
) -> List[float]:
    """Build a vector suitable for a simple positioning-map analysis."""
    return [competitor.scores[dimension] for dimension in dimensions]


def sensitivity_analysis(
    competitors: Sequence[Competitor],
    base_criteria: Sequence[Criterion],
    changed_weight: str,
    new_weight: float,
) -> List[Tuple[str, float]]:
    """
    Recalculate competitors after changing one criterion weight.

    This demonstrates why conclusions can change when assumptions change.
    """
    if not 0 <= new_weight <= 1:
        raise ValueError("New weight must be between 0 and 1.")

    modified = []

    for criterion in base_criteria:
        if criterion.name == changed_weight:
            modified.append(
                Criterion(
                    criterion.name,
                    new_weight,
                    criterion.description,
                )
            )
        else:
            modified.append(criterion)

    modified = normalize_weights(modified)

    return sorted(
        [
            (competitor.name, weighted_score(competitor, modified))
            for competitor in competitors
        ],
        key=lambda item: item[1],
        reverse=True,
    )


def print_feature_matrix(
    features: Sequence[Feature],
    competitors: Sequence[Competitor],
) -> None:
    """Print a feature comparison matrix."""
    print(f"{'Feature':<25}", end="")
    for competitor in competitors:
        print(f"{competitor.name:<20}", end="")
    print()

    print("-" * (25 + 20 * len(competitors)))

    for feature in features:
        print(f"{feature.name:<25}", end="")

        for competitor in competitors:
            status = competitor.feature_status.get(
                feature.name,
                FeatureStatus.ABSENT,
            )
            print(f"{status.value:<20}", end="")

        print()


# ============================================================================
# 6. POSITIONING ANALYSIS
# ============================================================================

def build_positioning_profile() -> PositioningProfile:
    """
    Define a fictional focal product.

    Good positioning describes a target customer and a meaningful customer
    problem. It is not simply a list of features.
    """
    return PositioningProfile(
        product_name="FocusFlow",
        target_customer="Growing operations teams with 20-200 employees",
        primary_need="Coordinating repeatable operational work without enterprise-level complexity",
        key_difference="Combines simple workflow automation with actionable operational analytics",
        value_proposition=(
            "FocusFlow helps growing teams standardize recurring work, "
            "automate routine steps, and understand operational performance "
            "without requiring a large enterprise implementation."
        ),
        proof_points=[
            "Fast workflow configuration",
            "Operational analytics built around workflows",
            "Automation designed for non-technical users",
            "Lower complexity than enterprise work-management platforms",
        ],
    )


def positioning_map(
    competitors: Sequence[Competitor],
    x_dimension: str,
    y_dimension: str,
) -> List[Tuple[str, float, float]]:
    """
    Produce two-dimensional positioning coordinates.

    A positioning map is a simplification. Real customer perception is
    multidimensional and should be validated with customer research.
    """
    return [
        (
            competitor.name,
            competitor.scores[x_dimension],
            competitor.scores[y_dimension],
        )
        for competitor in competitors
    ]


# ============================================================================
# 7. ANALYTICAL REPORTING
# ============================================================================

def print_competitor_profiles(
    competitors: Sequence[Competitor],
    profile: PositioningProfile,
) -> None:
    """Explain why each competitor belongs in the competitive set."""
    print_header("COMPETITOR CLASSIFICATION")

    for competitor in competitors:
        print(f"\n{competitor.name}")
        print(f"  Type: {competitor.competition_type.value}")
        print(f"  Segment: {competitor.target_segment}")
        print(
            "  Classification:",
            classify_competitor(
                competitor,
                profile.target_customer,
                profile.primary_need,
            ),
        )
        print(f"  Positioning: {competitor.positioning_statement}")


def print_positioning_profile(profile: PositioningProfile) -> None:
    """Display the focal product's positioning."""
    print_header("FOCAL PRODUCT POSITIONING")

    print(f"Product: {profile.product_name}")
    print(f"Target customer: {profile.target_customer}")
    print(f"Primary need: {profile.primary_need}")
    print(f"Key difference: {profile.key_difference}")
    print(f"Value proposition: {profile.value_proposition}")

    print("Proof points:")
    for proof_point in profile.proof_points:
        print(f"  - {proof_point}")


def print_price_analysis(
    competitors: Sequence[Competitor],
    criteria: Sequence[Criterion],
) -> None:
    """Show price and capability metrics."""
    print_header("PRICE-VALUE ANALYSIS")

    print(
        f"{'Competitor':<20}"
        f"{'Price/User':>12}"
        f"{'Score':>12}"
        f"{'Price/Point':>15}"
    )
    print("-" * 59)

    for competitor in competitors:
        score = weighted_score(competitor, criteria)
        ratio = price_per_value_point(competitor, criteria)

        print(
            f"{competitor.name:<20}"
            f"${competitor.price_per_user:>10.2f}"
            f"{score:>12.2f}"
            f"${ratio:>13.2f}"
        )


def print_positioning_map(
    competitors: Sequence[Competitor],
    x_dimension: str,
    y_dimension: str,
) -> None:
    """Print coordinates for a conceptual two-axis positioning map."""
    print_header(
        f"POSITIONING MAP: {x_dimension} vs. {y_dimension}"
    )

    print(f"{'Competitor':<20}{x_dimension:>15}{y_dimension:>18}")
    print("-" * 53)

    for name, x, y in positioning_map(
        competitors,
        x_dimension,
        y_dimension,
    ):
        print(f"{name:<20}{x:>15.2f}{y:>18.2f}")


def print_sensitivity_analysis(
    competitors: Sequence[Competitor],
    criteria: Sequence[Criterion],
) -> None:
    """Demonstrate how changing analytical assumptions changes scores."""
    print_header("SENSITIVITY ANALYSIS")

    scenarios = [
        ("Ease of Use", 0.30),
        ("Enterprise Security", 0.30),
        ("Price Value", 0.30),
    ]

    for criterion_name, new_weight in scenarios:
        print(
            f"\nScenario: increase '{criterion_name}' weight "
            f"to {new_weight:.0%}"
        )

        results = sensitivity_analysis(
            competitors,
            criteria,
            criterion_name,
            new_weight,
        )

        for name, score in results:
            print(f"  {name:<20} {score:.2f}")


def print_feature_gaps(
    focal_product_features: Mapping[str, FeatureStatus],
    competitors: Sequence[Competitor],
) -> None:
    """Show where each competitor has stronger feature coverage."""
    print_header("FOCAL PRODUCT FEATURE-GAP ANALYSIS")

    for competitor in competitors:
        print(f"\nAgainst {competitor.name}:")

        gaps = feature_gap_analysis(
            focal_product_features,
            competitor,
        )

        if not gaps:
            print("  No stronger competitor feature status detected.")
        else:
            for gap in gaps:
                print(f"  - {gap}")


# ============================================================================
# 8. ADVANCED CONCEPTS
# ============================================================================

def explain_analytical_principles() -> None:
    """
    Print concise conceptual notes alongside executable analysis.

    These comments and outputs intentionally connect the calculations to
    actual competitive-analysis practice.
    """
    print_header("KEY ANALYTICAL PRINCIPLES")

    principles = [
        (
            "Competitive set",
            "Include alternatives customers can realistically choose, "
            "not merely products with similar feature lists."
        ),
        (
            "Direct competition",
            "The competitor addresses a substantially similar customer need "
            "with a similar category of solution."
        ),
        (
            "Indirect competition",
            "The alternative solves the underlying need through a different "
            "product category, workflow, or resource."
        ),
        (
            "Feature comparison",
            "A feature matrix describes capability differences but does not "
            "by itself prove customer value."
        ),
        (
            "Positioning",
            "Positioning defines how a product should be understood relative "
            "to alternatives for a particular target customer."
        ),
        (
            "Differentiation",
            "A meaningful differentiator should matter to customers and be "
            "credible, defensible, and observable."
        ),
        (
            "Weighted scoring",
            "Weighted scoring makes assumptions explicit but does not convert "
            "subjective judgments into objective truth."
        ),
        (
            "Sensitivity analysis",
            "If small weight changes produce large changes in the result, "
            "the analysis is assumption-sensitive."
        ),
        (
            "Strategic interpretation",
            "A competitive gap is not automatically a product requirement. "
            "Customer importance, cost, feasibility, and strategic fit matter."
        ),
    ]

    for title, explanation in principles:
        print(f"\n{title}:")
        print(f"  {explanation}")


# ============================================================================
# 9. EDGE CASES AND VALIDATION DEMONSTRATIONS
# ============================================================================

def demonstrate_edge_cases() -> None:
    """Demonstrate important failure conditions."""
    print_header("EDGE CASES AND VALIDATION")

    invalid_competitor = Competitor(
        name="InvalidExample",
        competition_type=CompetitionType.DIRECT,
        target_segment="Example",
        price_per_user=-10,
        scores={"Ease of Use": 7},
        feature_status={},
    )

    try:
        invalid_competitor.validate(["Ease of Use", "Task Management"])
    except ValueError as error:
        print(f"Validation caught an invalid dataset: {error}")

    try:
        euclidean_distance([1, 2], [1])
    except ValueError as error:
        print(f"Vector validation caught an invalid input: {error}")

    try:
        normalize_weights([])
    except ValueError as error:
        print(f"Weight validation caught an invalid input: {error}")


# ============================================================================
# 10. UNIT-STYLE TESTS
# ============================================================================

def run_tests() -> None:
    """Small built-in tests that verify important analytical functions."""
    print_header("BUILT-IN TESTS")

    criteria = normalize_weights(CRITERIA)
    validate_competitor_dataset(COMPETITORS, criteria)

    assert abs(total_weight(criteria) - 1.0) < 1e-9

    score = weighted_score(COMPETITORS[0], criteria)
    assert 1 <= score <= 5

    point_a = [1, 2, 3]
    point_b = [4, 6, 3]
    assert abs(euclidean_distance(point_a, point_b) - 5.0) < 1e-9

    profile = build_positioning_profile()
    assert profile.product_name == "FocusFlow"
    assert profile.target_customer

    print("All built-in tests passed.")


# ============================================================================
# 11. COMPLETE DEMONSTRATION
# ============================================================================

def main() -> None:
    """Run the complete competitive-analysis study."""
    criteria = normalize_weights(CRITERIA)
    validate_competitor_dataset(COMPETITORS, criteria)

    profile = build_positioning_profile()

    print_header("COMPETITIVE ANALYSIS STUDY")
    print(
        "This executable study models a competitive-analysis process for "
        "a fictional project-management market."
    )

    print_positioning_profile(profile)
    print_competitor_profiles(COMPETITORS, profile)

    print_header("WEIGHTED COMPETITIVE COMPARISON")
    print_score_table(COMPETITORS, criteria)

    print_header("FEATURE COMPARISON MATRIX")
    print_feature_matrix(FEATURES, COMPETITORS)

    print_price_analysis(COMPETITORS, criteria)

    focal_product_features = {
        "Task Management": FeatureStatus.STRONG,
        "Workflow Automation": FeatureStatus.DIFFERENTIATED,
        "Analytics": FeatureStatus.DIFFERENTIATED,
        "AI Assistance": FeatureStatus.STRONG,
        "Integrations": FeatureStatus.STRONG,
        "Enterprise Security": FeatureStatus.BASIC,
    }

    print_feature_gaps(
        focal_product_features,
        COMPETITORS,
    )

    print_positioning_map(
        COMPETITORS,
        "Ease of Use",
        "Workflow Automation",
    )

    print_header("FEATURE-SPECIFIC COMPARISON")
    for feature_name in ["Task Management", "AI Assistance", "Enterprise Security"]:
        print(f"\n{feature_name}:")
        comparison = compare_feature(feature_name, COMPETITORS)

        for competitor_name, status in comparison.items():
            print(f"  {competitor_name:<20} {status.value}")

    explain_analytical_principles()
    print_sensitivity_analysis(COMPETITORS, criteria)
    demonstrate_edge_cases()
    run_tests()

    print_header("IMPLEMENTATION AND PRODUCTION CONSIDERATIONS")
    print(
        "For production analysis, replace illustrative scores with traceable "
        "evidence such as customer interviews, product testing, pricing pages, "
        "sales win/loss data, usage data, and structured market research."
    )
    print(
        "Keep raw observations separate from analyst judgments so that the "
        "reasoning behind each score remains auditable."
    )
    print(
        "Avoid treating one composite score as the answer to a strategic "
        "question. Examine customer segment, use case, price, capabilities, "
        "switching costs, distribution, and defensibility separately."
    )


if __name__ == "__main__":
    main()
