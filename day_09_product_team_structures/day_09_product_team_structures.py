"""
Product Team Structures: Functional, Cross-Functional, Squad, Tribe,
Platform Teams, Feature Teams, and Product Teams

This standalone study script teaches organizational structures used to build,
operate, and manage digital products. It progresses from basic organizational
concepts to advanced team-topology analysis.

The examples use only Python's standard library.

Run:
    python product_team_structures.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ============================================================================
# 1. FOUNDATIONAL TERMINOLOGY
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


section("1. PRODUCT TEAM STRUCTURES: FOUNDATIONAL CONCEPTS")

print(
    """
A product team is a group of people organized to discover, build, deliver,
operate, and improve a product or part of a product.

A team structure answers questions such as:

1. Who reports to whom?
2. Which skills belong to the same team?
3. Who owns product outcomes?
4. Who makes technical decisions?
5. How does work move between teams?
6. Who owns a customer journey or business capability?
7. How are dependencies handled?
8. How does the organization scale?

Important distinctions:

- Organizational structure describes reporting relationships and authority.
- Team topology describes how teams are shaped around work and interaction.
- Product operating model describes how product strategy, discovery,
  delivery, measurement, and decision-making work together.
- Team design describes the composition and responsibilities of an individual
  team.

A structure is not automatically good because it has a fashionable name.
Its effectiveness depends on product complexity, organizational maturity,
team autonomy, architecture, regulatory constraints, dependencies, and the
type of work being performed.
"""
)


# ============================================================================
# 2. CORE TEAM BUILDING BLOCKS
# ============================================================================

class StructureType(Enum):
    FUNCTIONAL = "Functional"
    CROSS_FUNCTIONAL = "Cross-functional"
    SQUAD = "Squad"
    TRIBE = "Tribe"
    PLATFORM = "Platform team"
    FEATURE = "Feature team"
    PRODUCT = "Product team"


class TeamInteractionMode(Enum):
    COLLABORATION = "Collaboration"
    X_AS_A_SERVICE = "X-as-a-service"
    FACILITATION = "Facilitation"


@dataclass
class Role:
    """A role represents a capability commonly found in product organizations."""

    name: str
    primary_responsibility: str
    typical_decisions: List[str] = field(default_factory=list)


@dataclass
class Team:
    """A simplified representation of a product team."""

    name: str
    structure: StructureType
    purpose: str
    roles: List[str]
    owns_outcome: bool
    customer_facing: bool
    autonomy: int
    dependency_level: int
    typical_size: Tuple[int, int]
    interaction_modes: List[TeamInteractionMode] = field(default_factory=list)

    def average_size(self) -> float:
        return mean(self.typical_size)

    def autonomy_ratio(self) -> float:
        """Return autonomy as a 0.0 to 1.0 ratio."""
        return self.autonomy / 10

    def dependency_ratio(self) -> float:
        """Return dependency intensity as a 0.0 to 1.0 ratio."""
        return self.dependency_level / 10


ROLES = [
    Role(
        "Product Manager",
        "Product strategy, prioritization, outcomes, and product decisions",
        ["Problem selection", "Prioritization", "Outcome definition"],
    ),
    Role(
        "Product Designer",
        "User research, interaction design, experience design, and validation",
        ["Experience decisions", "Design validation", "User research"],
    ),
    Role(
        "Software Engineer",
        "Software implementation, technical design, quality, and maintainability",
        ["Implementation", "Technical design", "Engineering trade-offs"],
    ),
    Role(
        "Data Analyst",
        "Measurement, experimentation, analysis, and decision support",
        ["Metric definition", "Experiment analysis", "Product insights"],
    ),
    Role(
        "QA Engineer",
        "Quality assurance, test strategy, and defect prevention",
        ["Test strategy", "Quality gates", "Risk-based testing"],
    ),
    Role(
        "DevOps/SRE",
        "Reliability, deployment, infrastructure, observability, and operations",
        ["Reliability controls", "Deployment design", "Operational readiness"],
    ),
]


def print_roles() -> None:
    subsection("Common Product Roles")
    for role in ROLES:
        print(f"\n{role.name}")
        print(f"  Responsibility: {role.primary_responsibility}")
        print(f"  Decisions: {', '.join(role.typical_decisions)}")


print_roles()


# ============================================================================
# 3. FUNCTIONAL TEAM STRUCTURE
# ============================================================================

section("2. FUNCTIONAL TEAM STRUCTURE")

functional_team = Team(
    name="Engineering Department",
    structure=StructureType.FUNCTIONAL,
    purpose="Group people according to professional specialization.",
    roles=["Software Engineer", "QA Engineer", "DevOps/SRE"],
    owns_outcome=False,
    customer_facing=False,
    autonomy=4,
    dependency_level=8,
    typical_size=(10, 100),
    interaction_modes=[TeamInteractionMode.COLLABORATION],
)

print(
    f"""
Definition:
A functional structure groups specialists by discipline. Engineering,
design, data, marketing, sales, and other disciplines are often separate
organizational units.

Example:
    Product
      |
      +-- Engineering
      +-- Design
      +-- Data
      +-- Marketing

Advantages:
- Strong professional communities.
- Easier mentoring within a discipline.
- Consistent standards and technical practices.
- Efficient allocation of scarce specialists.
- Clear functional leadership.

Risks:
- Handoffs between departments.
- Local optimization.
- Long queues for specialist work.
- Product decisions can become fragmented.
- Accountability for customer outcomes may be unclear.

Team: {functional_team.name}
Autonomy: {functional_team.autonomy}/10
Dependency level: {functional_team.dependency_level}/10
"""
)


# ============================================================================
# 4. CROSS-FUNCTIONAL TEAM STRUCTURE
# ============================================================================

section("3. CROSS-FUNCTIONAL TEAM STRUCTURE")

cross_functional_team = Team(
    name="Checkout Product Team",
    structure=StructureType.CROSS_FUNCTIONAL,
    purpose="Own a customer problem using multiple disciplines in one team.",
    roles=[
        "Product Manager",
        "Product Designer",
        "Software Engineer",
        "QA Engineer",
        "Data Analyst",
    ],
    owns_outcome=True,
    customer_facing=True,
    autonomy=8,
    dependency_level=3,
    typical_size=(5, 10),
    interaction_modes=[TeamInteractionMode.COLLABORATION],
)

print(
    f"""
Definition:
A cross-functional team contains the capabilities required to solve a
product problem without requiring every major decision to pass through
separate functional departments.

Typical composition:
    Product Manager
    Product Designer
    Engineers
    QA
    Data/Analytics

The important property is not the exact job titles. The important property is
that the team has sufficient skills to move from problem discovery toward
delivery and measurement.

Team: {cross_functional_team.name}
Roles: {", ".join(cross_functional_team.roles)}
Owns outcome: {cross_functional_team.owns_outcome}
Autonomy: {cross_functional_team.autonomy}/10
Dependencies: {cross_functional_team.dependency_level}/10
"""
)


# ============================================================================
# 5. SQUAD MODEL
# ============================================================================

section("4. SQUAD STRUCTURE")

squad = Team(
    name="Payments Squad",
    structure=StructureType.SQUAD,
    purpose="A small, autonomous team aligned to a product mission or area.",
    roles=[
        "Product Manager",
        "Product Designer",
        "Software Engineer",
        "QA Engineer",
        "Data Analyst",
    ],
    owns_outcome=True,
    customer_facing=True,
    autonomy=9,
    dependency_level=3,
    typical_size=(5, 9),
    interaction_modes=[TeamInteractionMode.COLLABORATION],
)

print(
    f"""
A squad is commonly used to describe a small, relatively autonomous,
cross-functional product team.

The term became strongly associated with the model described publicly by
Spotify, but the term should not be treated as a universal organizational
standard.

Typical characteristics:
- Small team.
- Cross-functional capabilities.
- Clear mission or product area.
- High autonomy.
- Direct responsibility for product outcomes.

Important distinction:
"Squad" describes a team pattern. It does not inherently define reporting
lines, governance, strategy, architecture, or company-wide organization.

Team: {squad.name}
Typical size: {squad.typical_size[0]}-{squad.typical_size[1]}
Autonomy: {squad.autonomy}/10
"""
)


# ============================================================================
# 6. TRIBE MODEL
# ============================================================================

section("5. TRIBE STRUCTURE")

tribe = Team(
    name="Commerce Tribe",
    structure=StructureType.TRIBE,
    purpose="Coordinate multiple squads working in a related product domain.",
    roles=["Product Managers", "Designers", "Engineers", "Analysts"],
    owns_outcome=True,
    customer_facing=True,
    autonomy=8,
    dependency_level=5,
    typical_size=(20, 150),
    interaction_modes=[TeamInteractionMode.COLLABORATION],
)

print(
    f"""
A tribe is a grouping of multiple squads around a broader product domain.

Conceptually:

    Tribe: Commerce
        |
        +-- Squad: Checkout
        +-- Squad: Cart
        +-- Squad: Pricing
        +-- Squad: Promotions

The tribe can provide coordination without requiring every decision to be
centralized.

Potential benefits:
- Shared product context.
- Better coordination among related teams.
- Communities of practice.
- Reduced duplication.

Potential risks:
- Coordination overhead.
- Ambiguous authority.
- Too many ceremonies.
- Tribes can become departments under a different name.
- Cross-tribe dependencies may remain unresolved.

A tribe is therefore a scaling pattern, not a guarantee of autonomy.
"""
)


# ============================================================================
# 7. PLATFORM TEAMS
# ============================================================================

section("6. PLATFORM TEAM STRUCTURE")

platform_team = Team(
    name="Developer Platform Team",
    structure=StructureType.PLATFORM,
    purpose="Provide reusable internal capabilities that accelerate product teams.",
    roles=["Software Engineer", "DevOps/SRE", "Security Engineer"],
    owns_outcome=False,
    customer_facing=False,
    autonomy=8,
    dependency_level=4,
    typical_size=(5, 12),
    interaction_modes=[
        TeamInteractionMode.X_AS_A_SERVICE,
        TeamInteractionMode.FACILITATION,
    ],
)

print(
    f"""
A platform team builds and operates capabilities consumed by other teams.

Examples:
- CI/CD infrastructure.
- Internal developer portals.
- Authentication infrastructure.
- Cloud infrastructure abstractions.
- Observability platforms.
- Shared data platforms.
- Internal APIs.
- Identity and access services.

The platform's customers are usually internal teams.

A mature platform team treats internal developers as customers and optimizes
for usability, reliability, adoption, and reduced cognitive load.

Team: {platform_team.name}
Purpose: {platform_team.purpose}
"""
)


# ============================================================================
# 8. FEATURE TEAM
# ============================================================================

section("7. FEATURE TEAM STRUCTURE")

feature_team = Team(
    name="Checkout Feature Team",
    structure=StructureType.FEATURE,
    purpose="Deliver a feature or feature slice across the required technical layers.",
    roles=["Product Manager", "Designer", "Frontend Engineer", "Backend Engineer"],
    owns_outcome=False,
    customer_facing=True,
    autonomy=6,
    dependency_level=7,
    typical_size=(4, 10),
    interaction_modes=[TeamInteractionMode.COLLABORATION],
)

print(
    f"""
A feature team is organized around delivering features rather than owning a
stable product or business outcome.

For example:

    Feature request
        |
        +-- Design
        +-- Frontend
        +-- Backend
        +-- QA
        +-- Release

Feature teams can be useful when:
- A temporary initiative requires concentrated capacity.
- The organization is transitioning between structures.
- A feature spans multiple components.
- A fixed-scope delivery effort is required.

Risks:
- Feature completion can become the success metric.
- Teams may lack long-term ownership.
- Technical dependencies can remain high.
- Product learning may stop when the feature ships.
"""
)


# ============================================================================
# 9. PRODUCT TEAM
# ============================================================================

section("8. PRODUCT TEAM STRUCTURE")

product_team = Team(
    name="Customer Growth Product Team",
    structure=StructureType.PRODUCT,
    purpose="Continuously own a product problem, customer outcome, and measurable result.",
    roles=[
        "Product Manager",
        "Product Designer",
        "Software Engineer",
        "Data Analyst",
    ],
    owns_outcome=True,
    customer_facing=True,
    autonomy=9,
    dependency_level=3,
    typical_size=(5, 10),
    interaction_modes=[TeamInteractionMode.COLLABORATION],
)

print(
    f"""
A product team is generally organized around a persistent product problem,
customer segment, business capability, or measurable outcome.

This differs from a feature team because ownership continues after a feature
is released.

A product team may ask:
- Which customer problem matters?
- What evidence supports the problem?
- What outcome are we trying to change?
- What should we build?
- What should we not build?
- Did the solution work?
- What should we change next?

This supports continuous discovery and delivery rather than feature
completion as the primary endpoint.

Team: {product_team.name}
Owns outcome: {product_team.owns_outcome}
Autonomy: {product_team.autonomy}/10
"""
)


# ============================================================================
# 10. COMPARISON MODEL
# ============================================================================

section("9. STRUCTURE COMPARISON")

teams = [
    functional_team,
    cross_functional_team,
    squad,
    tribe,
    platform_team,
    feature_team,
    product_team,
]

print(
    f"{'Structure':<20}"
    f"{'Outcome':<12}"
    f"{'Customer':<12}"
    f"{'Autonomy':<10}"
    f"{'Dependency':<12}"
    f"{'Size':<12}"
)
print("-" * 78)

for team in teams:
    print(
        f"{team.structure.value:<20}"
        f"{str(team.owns_outcome):<12}"
        f"{str(team.customer_facing):<12}"
        f"{team.autonomy:<10}"
        f"{team.dependency_level:<12}"
        f"{team.typical_size[0]}-{team.typical_size[1]:<10}"
    )


# ============================================================================
# 11. REPORTING STRUCTURE VS DELIVERY STRUCTURE
# ============================================================================

section("10. REPORTING LINES AND PRODUCT DELIVERY ARE DIFFERENT")

print(
    """
One of the most important organizational design principles is that a team can
have one reporting structure and a different delivery structure.

For example:

    Functional reporting:
        Engineer -> Engineering Manager

    Product delivery:
        Engineer -> Product Team -> Customer Outcome

This means the engineering manager may be responsible for:
- Career development.
- Hiring.
- Engineering standards.
- Compensation.
- Coaching.

The product team may be responsible for:
- Product decisions.
- Problem discovery.
- Prioritization.
- Delivery.
- Outcome measurement.

Separating these concepts prevents the mistaken assumption that every product
team must be a standalone department.
"""
)


# ============================================================================
# 12. TEAM TOPOLOGIES
# ============================================================================

section("11. TEAM TOPOLOGIES")

print(
    """
A useful advanced distinction is between a team's purpose and its interaction
with other teams.

Three important interaction modes are:

1. Collaboration
   Two teams actively work together for a period of time.

2. X-as-a-service
   One team provides a capability that another team consumes through a
   defined interface.

3. Facilitation
   One team helps another team acquire a capability or improve its ability
   to work independently.

The same organization can contain different interaction modes at once.

Example:

    Product Team
         |
         +---- collaboration ----> Data Team
         |
         +---- consumes ----------> Platform Team
         |
         +---- facilitation ------> Security Team
"""
)


# ============================================================================
# 13. TEAM API CONCEPT
# ============================================================================

@dataclass
class TeamAPI:
    """
    A conceptual team API.

    It defines what another team can reasonably expect from a team, reducing
    ambiguity around ownership and interaction.
    """

    team_name: str
    purpose: str
    provides: List[str]
    consumes: List[str]
    decision_authority: List[str]
    escalation_path: str

    def validate(self) -> List[str]:
        errors = []

        if not self.team_name.strip():
            errors.append("Team name cannot be empty.")

        if not self.purpose.strip():
            errors.append("Team purpose cannot be empty.")

        if not self.provides and not self.consumes:
            errors.append("Team API should document at least one interaction.")

        if not self.decision_authority:
            errors.append("Decision authority should be explicit.")

        return errors


product_api = TeamAPI(
    team_name="Checkout Product Team",
    purpose="Improve successful checkout completion.",
    provides=["Customer checkout experience", "Checkout metrics"],
    consumes=["Payment platform", "Identity service", "Analytics platform"],
    decision_authority=[
        "Product prioritization within mission",
        "UX decisions",
        "Experiment selection",
    ],
    escalation_path="Product leadership for strategic conflicts",
)

print("\nTeam API validation:")
print(product_api.validate() or "Valid")


# ============================================================================
# 14. TEAM BOUNDARIES
# ============================================================================

section("12. TEAM BOUNDARIES AND OWNERSHIP")

@dataclass
class Capability:
    name: str
    owner: Optional[str] = None
    criticality: int = 5

    def is_unowned(self) -> bool:
        return self.owner is None


capabilities = [
    Capability("Checkout UI", "Checkout Product Team", 8),
    Capability("Payment Authorization", "Payments Platform Team", 10),
    Capability("Customer Analytics", "Data Platform Team", 8),
    Capability("Promotion Rules", "Growth Product Team", 7),
    Capability("Deployment Pipeline", "Developer Platform Team", 9),
    Capability("Fraud Detection", None, 10),
]

print("Capability ownership audit:")
for capability in capabilities:
    status = "UNOWNED" if capability.is_unowned() else capability.owner
    print(f"  {capability.name:<25} -> {status}")

unowned_critical_capabilities = [
    capability
    for capability in capabilities
    if capability.is_unowned() and capability.criticality >= 8
]

print("\nCritical capabilities without ownership:")
for capability in unowned_critical_capabilities:
    print(f"  {capability.name}")


# ============================================================================
# 15. DEPENDENCY GRAPH
# ============================================================================

section("13. DEPENDENCY ANALYSIS")

@dataclass(frozen=True)
class Dependency:
    source: str
    target: str
    reason: str
    criticality: int


dependencies = [
    Dependency("Checkout Product Team", "Payments Platform Team",
                "Payment authorization", 9),
    Dependency("Checkout Product Team", "Identity Team",
                "Customer authentication", 8),
    Dependency("Checkout Product Team", "Analytics Platform Team",
                "Experiment data", 6),
    Dependency("Growth Product Team", "Checkout Product Team",
                "Checkout conversion signal", 5),
    Dependency("Payments Platform Team", "Security Team",
                "Security controls", 9),
]

print("Dependency graph:")
for dependency in dependencies:
    print(
        f"  {dependency.source} -> {dependency.target} "
        f"[criticality={dependency.criticality}] "
        f"({dependency.reason})"
    )


def calculate_dependency_pressure(
    dependencies: Iterable[Dependency],
    team_name: str,
) -> float:
    """Calculate average dependency criticality involving a given team."""
    relevant = [
        dependency.criticality
        for dependency in dependencies
        if dependency.source == team_name or dependency.target == team_name
    ]
    return mean(relevant) if relevant else 0.0


for name in [
    "Checkout Product Team",
    "Payments Platform Team",
    "Growth Product Team",
]:
    print(
        f"{name}: dependency pressure "
        f"{calculate_dependency_pressure(dependencies, name):.2f}/10"
    )


# ============================================================================
# 16. FEATURE TEAM VS PRODUCT TEAM
# ============================================================================

section("14. FEATURE TEAM VS PRODUCT TEAM")

print(
    """
Feature-oriented ownership:

    Objective -> Feature -> Release -> Done

Product-oriented ownership:

    Problem -> Hypothesis -> Solution -> Release -> Measure -> Learn -> Repeat

The second model changes the definition of completion.

A feature team may be optimized for:
- Scope.
- Schedule.
- Feature throughput.
- Release completion.

A product team should generally be optimized for:
- Customer outcomes.
- Business outcomes.
- Learning velocity.
- Sustainable product improvement.

A feature team is not inherently bad. The issue arises when a temporary
delivery mechanism becomes a permanent substitute for product ownership.
"""
)


# ============================================================================
# 17. PLATFORM TEAM VS SHARED SERVICES
# ============================================================================

section("15. PLATFORM TEAM VS SHARED SERVICES")

print(
    """
A traditional shared-services team often behaves like a centralized queue:

    Product Team -> Request -> Central Team -> Wait -> Delivery

A product-oriented platform team aims for:

    Product Team -> Self-service Platform -> Immediate Capability

The distinction is primarily about the developer experience and operating
model, not the label.

Platform teams should minimize:
- Manual ticket queues.
- Hidden operational complexity.
- Excessive coupling.
- Unclear service levels.
- Mandatory platform usage without sufficient value.

A platform team should maximize:
- Self-service.
- Documentation.
- Reliability.
- Discoverability.
- Automation.
- Clear interfaces.
- Measurable adoption.
"""
)


# ============================================================================
# 18. SCALING ORGANIZATIONS
# ============================================================================

section("16. SCALING FROM ONE TEAM TO MANY")

print(
    """
Small organization:

    One cross-functional product team
        |
        +-- Product
        +-- Design
        +-- Engineering
        +-- Data

Growing organization:

    Product Group
        |
        +-- Product Team A
        +-- Product Team B
        +-- Product Team C
        +-- Platform Team

Larger organization:

    Tribe / Product Area
        |
        +-- Product Team A
        +-- Product Team B
        +-- Product Team C
        +-- Platform Team

The scaling principle is not simply "create more teams."

The organization must also decide:
- What each team owns.
- How teams interact.
- Which decisions are local.
- Which decisions require coordination.
- How architecture supports team boundaries.
- How strategy is communicated.
- How dependencies are reduced.
"""
)


# ============================================================================
# 19. TEAM COGNITIVE LOAD
# ============================================================================

section("17. COGNITIVE LOAD")

@dataclass
class CognitiveLoadModel:
    domain_complexity: float
    system_complexity: float
    operational_complexity: float
    coordination_complexity: float

    def total(self) -> float:
        return (
            self.domain_complexity
            + self.system_complexity
            + self.operational_complexity
            + self.coordination_complexity
        )

    def normalized(self) -> float:
        return min(self.total() / 40, 1.0)


low_load = CognitiveLoadModel(4, 3, 2, 2)
high_load = CognitiveLoadModel(9, 9, 8, 9)

print(f"Low-load team: {low_load.total():.1f}/40")
print(f"High-load team: {high_load.total():.1f}/40")

print(
    """
Team size should not be optimized independently of cognitive load.

A team responsible for:
- a complex domain,
- a large technical system,
- production operations,
- compliance,
- and many external dependencies

may be overloaded even if it has a reasonable headcount.

Reducing cognitive load can involve:
- Better APIs.
- Platform capabilities.
- Clear ownership.
- Smaller bounded contexts.
- Automation.
- Documentation.
- Removing unnecessary responsibilities.
"""
)


# ============================================================================
# 20. AUTONOMY AND ALIGNMENT
# ============================================================================

section("18. AUTONOMY AND ALIGNMENT")

@dataclass
class TeamHealth:
    autonomy: float
    alignment: float
    clarity: float
    dependency: float

    def autonomy_alignment_index(self) -> float:
        """
        A simple educational index.

        This is not an industry-standard metric. It demonstrates how multiple
        organizational factors can be modeled rather than treated as isolated
        concepts.
        """
        return (
            self.autonomy * 0.30
            + self.alignment * 0.30
            + self.clarity * 0.25
            + (10 - self.dependency) * 0.15
        )


healthy_team = TeamHealth(
    autonomy=9,
    alignment=9,
    clarity=9,
    dependency=2,
)

constrained_team = TeamHealth(
    autonomy=3,
    alignment=8,
    clarity=5,
    dependency=9,
)

print(
    f"Healthy autonomous team index: "
    f"{healthy_team.autonomy_alignment_index():.2f}/10"
)
print(
    f"Constrained team index: "
    f"{constrained_team.autonomy_alignment_index():.2f}/10"
)

print(
    """
Autonomy without alignment can create duplicated or conflicting work.

Alignment without autonomy can create slow decision-making.

Effective product organizations attempt to establish:
- Clear strategic direction.
- Explicit product outcomes.
- Local decision authority.
- Transparent constraints.
- Strong feedback loops.
"""
)


# ============================================================================
# 21. TEAM DESIGN SCORECARD
# ============================================================================

section("19. TEAM DESIGN SCORECARD")

@dataclass
class TeamScorecard:
    mission_clarity: int
    ownership_clarity: int
    skill_completeness: int
    autonomy: int
    dependency_control: int
    customer_access: int
    technical_health: int

    def validate_scores(self) -> None:
        values = [
            self.mission_clarity,
            self.ownership_clarity,
            self.skill_completeness,
            self.autonomy,
            self.dependency_control,
            self.customer_access,
            self.technical_health,
        ]

        if any(value < 0 or value > 10 for value in values):
            raise ValueError("Every score must be between 0 and 10.")

    def score(self) -> float:
        self.validate_scores()
        return mean(
            [
                self.mission_clarity,
                self.ownership_clarity,
                self.skill_completeness,
                self.autonomy,
                self.dependency_control,
                self.customer_access,
                self.technical_health,
            ]
        )


scorecard = TeamScorecard(
    mission_clarity=9,
    ownership_clarity=9,
    skill_completeness=8,
    autonomy=8,
    dependency_control=7,
    customer_access=8,
    technical_health=8,
)

print(f"Team design score: {scorecard.score():.2f}/10")


# ============================================================================
# 22. DECISION RIGHTS
# ============================================================================

section("20. DECISION RIGHTS")

@dataclass
class Decision:
    name: str
    owner: str
    consultation_required: bool
    escalation_required: bool = False


decisions = [
    Decision("Product backlog ordering", "Product Team", True),
    Decision("Interaction design", "Product Team", True),
    Decision("Implementation approach", "Engineering Team", True),
    Decision("Enterprise security policy", "Security Team", True),
    Decision("Company strategy", "Executive Leadership", True),
    Decision("Platform API design", "Platform Team", True),
]

for decision in decisions:
    print(
        f"{decision.name:<30} "
        f"owner={decision.owner:<25} "
        f"consult={decision.consultation_required}"
    )

print(
    """
A common organizational failure is confusing consultation with approval.

A team can consult:
- Security.
- Legal.
- Architecture.
- Finance.
- Operations.

without requiring every decision to be approved centrally.

Decision rights should be explicit for important recurring decisions.
"""


# ============================================================================
# 23. PRODUCT MANAGER RESPONSIBILITY IN DIFFERENT STRUCTURES
# ============================================================================

section("21. PRODUCT MANAGER RESPONSIBILITIES ACROSS STRUCTURES")

pm_responsibilities: Dict[StructureType, List[str]] = {
    StructureType.FUNCTIONAL: [
        "Coordinate priorities across functions",
        "Manage handoffs",
        "Build shared product context",
    ],
    StructureType.CROSS_FUNCTIONAL: [
        "Own product outcomes",
        "Prioritize work",
        "Lead discovery and validation",
    ],
    StructureType.SQUAD: [
        "Maintain squad mission",
        "Prioritize customer problems",
        "Align squad with product strategy",
    ],
    StructureType.TRIBE: [
        "Coordinate product direction",
        "Manage cross-squad outcomes",
        "Resolve strategic conflicts",
    ],
    StructureType.PLATFORM: [
        "Define internal customer outcomes",
        "Prioritize platform capabilities",
        "Measure adoption and reliability",
    ],
    StructureType.FEATURE: [
        "Define feature value",
        "Coordinate delivery",
        "Validate feature requirements",
    ],
    StructureType.PRODUCT: [
        "Own measurable product outcomes",
        "Manage product strategy",
        "Lead continuous discovery and delivery",
    ],
}

for structure, responsibilities in pm_responsibilities.items():
    print(f"\n{structure.value}:")
    for responsibility in responsibilities:
        print(f"  - {responsibility}")


# ============================================================================
# 24. PRODUCT OPERATING MODEL
# ============================================================================

section("22. PRODUCT OPERATING MODEL")

print(
    """
A team structure works inside a larger product operating model.

A mature product operating model connects:

    Strategy
       |
       v
    Outcomes
       |
       v
    Product discovery
       |
       v
    Prioritization
       |
       v
    Delivery
       |
       v
    Measurement
       |
       +------> Learning
                    |
                    +----> Strategy adjustment

Changing team names without changing the operating model usually produces
limited improvement.

A product organization needs consistency between:
- Strategy.
- Funding.
- Team missions.
- Decision rights.
- Architecture.
- Metrics.
- Talent management.
- Planning.
"""
)


# ============================================================================
# 25. ORGANIZATIONAL DESIGN SIMULATION
# ============================================================================

section("23. STRUCTURE SELECTION SIMULATION")

@dataclass
class OrganizationContext:
    product_complexity: int
    organization_size: int
    regulatory_intensity: int
    platform_need: int
    need_for_speed: int
    customer_proximity: int
    architecture_modularity: int

    def validate(self) -> None:
        values = [
            self.product_complexity,
            self.organization_size,
            self.regulatory_intensity,
            self.platform_need,
            self.need_for_speed,
            self.customer_proximity,
            self.architecture_modularity,
        ]

        if any(value < 1 or value > 10 for value in values):
            raise ValueError("Context values must be from 1 to 10.")


def recommend_structure(context: OrganizationContext) -> List[Tuple[str, float]]:
    """
    Educational scoring model.

    This function demonstrates structured decision-making. It does not claim
    that organizational design can be reduced to a universal formula.
    """
    context.validate()

    scores: Dict[StructureType, float] = {
        StructureType.FUNCTIONAL: 0,
        StructureType.CROSS_FUNCTIONAL: 0,
        StructureType.SQUAD: 0,
        StructureType.TRIBE: 0,
        StructureType.PLATFORM: 0,
        StructureType.FEATURE: 0,
        StructureType.PRODUCT: 0,
    }

    scores[StructureType.FUNCTIONAL] += (
        context.organization_size * 0.4
        + context.regulatory_intensity * 0.5
    )

    scores[StructureType.CROSS_FUNCTIONAL] += (
        context.need_for_speed * 0.8
        + context.customer_proximity * 0.8
        + context.architecture_modularity * 0.3
    )

    scores[StructureType.SQUAD] += (
        context.need_for_speed * 0.9
        + context.customer_proximity * 0.9
        + context.architecture_modularity * 0.6
    )

    scores[StructureType.TRIBE] += (
        context.product_complexity * 0.9
        + context.organization_size * 0.7
        + context.architecture_modularity * 0.4
    )

    scores[StructureType.PLATFORM] += (
        context.platform_need * 1.2
        + context.organization_size * 0.4
        + context.architecture_modularity * 0.7
    )

    scores[StructureType.FEATURE] += (
        context.need_for_speed * 0.5
        + context.product_complexity * 0.4
        + context.regulatory_intensity * 0.3
    )

    scores[StructureType.PRODUCT] += (
        context.need_for_speed * 1.0
        + context.customer_proximity * 1.0
        + context.architecture_modularity * 0.7
        + context.product_complexity * 0.4
    )

    ranked = sorted(
        ((structure.value, score) for structure, score in scores.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    return ranked


startup_context = OrganizationContext(
    product_complexity=5,
    organization_size=3,
    regulatory_intensity=2,
    platform_need=3,
    need_for_speed=10,
    customer_proximity=10,
    architecture_modularity=6,
)

enterprise_context = OrganizationContext(
    product_complexity=10,
    organization_size=10,
    regulatory_intensity=9,
    platform_need=10,
    need_for_speed=6,
    customer_proximity=6,
    architecture_modularity=8,
)

for label, context in [
    ("Startup", startup_context),
    ("Large enterprise", enterprise_context),
]:
    print(f"\n{label} structure ranking:")
    for structure, score in recommend_structure(context):
        print(f"  {structure:<20} {score:.2f}")


# ============================================================================
# 26. HYBRID STRUCTURES
# ============================================================================

section("24. HYBRID STRUCTURES")

print(
    """
Real organizations frequently combine structures.

Example:

    Functional reporting
        |
        +-- Engineering
        +-- Design
        +-- Data

    Product delivery
        |
        +-- Squad A
        +-- Squad B
        +-- Squad C

    Platform capability
        |
        +-- Developer Platform
        +-- Data Platform
        +-- Security Platform

This hybrid model can combine:
- Functional career development.
- Cross-functional product ownership.
- Platform specialization.
- Product-area coordination.

The key risk is matrix complexity.

If a person has:
    1. functional manager,
    2. product manager,
    3. project manager,
    4. architecture authority,
    5. platform owner,

without clear decision rights, accountability becomes ambiguous.
"""


# ============================================================================
# 27. MATRIX ORGANIZATIONS
# ============================================================================

section("25. MATRIX STRUCTURES")

@dataclass
class Person:
    name: str
    functional_manager: str
    product_team: str
    project_assignment: Optional[str] = None

    def management_channels(self) -> int:
        channels = 2 if self.functional_manager and self.product_team else 1
        if self.project_assignment:
            channels += 1
        return channels


person = Person(
    name="Engineer A",
    functional_manager="Engineering Manager",
    product_team="Checkout Product Team",
    project_assignment=None,
)

print(
    f"{person.name} has {person.management_channels()} primary "
    f"organizational channels."
)

print(
    """
Matrix structures can provide flexibility, but they require explicit rules
for:
- Priority conflicts.
- Performance evaluation.
- Resource allocation.
- Technical authority.
- Product authority.
- Escalation.

A matrix is not automatically more collaborative. It can simply distribute
ambiguity across more dimensions.
"""
)


# ============================================================================
# 28. TEAM TOPOLOGY ANTI-PATTERNS
# ============================================================================

section("26. COMMON ANTI-PATTERNS")

anti_patterns = {
    "Feature factory": (
        "Teams continuously ship features without measuring whether outcomes "
        "improve."
    ),
    "Dependency maze": (
        "A simple customer change requires coordination across many teams."
    ),
    "Platform ticket queue": (
        "A platform team becomes a centralized manual service desk."
    ),
    "Team without ownership": (
        "A team receives work but has no authority over the relevant outcome."
    ),
    "Fake autonomy": (
        "A team is called autonomous but must obtain approval for routine decisions."
    ),
    "Overloaded product team": (
        "One team owns too many domains and cannot maintain sufficient context."
    ),
    "Duplicate platforms": (
        "Multiple teams independently build similar internal capabilities."
    ),
}

for name, description in anti_patterns.items():
    print(f"\n{name}")
    print(f"  {description}")


# ============================================================================
# 29. EDGE CASES
# ============================================================================

section("27. EDGE CASES AND EXCEPTIONS")

print(
    """
1. Highly regulated products
   Full autonomy may be constrained by legal, security, safety, or compliance
   requirements. The goal is clear decision boundaries rather than unlimited
   independence.

2. Very small startups
   One person may temporarily perform product management, design, engineering,
   analytics, and operations. Formal team topology may not be necessary.

3. Hardware/software products
   Hardware, firmware, manufacturing, software, and supply-chain dependencies
   may require structures beyond conventional digital product teams.

4. Safety-critical systems
   Independent verification and strict governance may be mandatory.

5. Temporary transformation programs
   Feature teams can be useful when a specific migration or transformation
   requires concentrated expertise.

6. Shared regulatory capabilities
   Central security, legal, compliance, or risk teams may be appropriate when
   independence and consistency are more important than local autonomy.

7. Platform teams with external customers
   A platform can evolve into a product in its own right when external
   customers directly consume it.

8. Multiple products sharing one capability
   A platform or enabling team can prevent repeated implementation, provided
   the platform does not become an organizational bottleneck.
"""
)


# ============================================================================
# 30. PERFORMANCE AND FLOW
# ============================================================================

section("28. PERFORMANCE, FLOW, AND DELIVERY")

@dataclass
class FlowMetrics:
    lead_time_days: float
    work_in_progress: int
    throughput_per_week: float
    failure_rate: float

    def approximate_flow_efficiency(self, active_days: float) -> float:
        if self.lead_time_days <= 0:
            raise ValueError("Lead time must be positive.")
        if active_days < 0:
            raise ValueError("Active time cannot be negative.")
        return min(active_days / self.lead_time_days, 1.0)

    def quality_adjusted_throughput(self) -> float:
        return self.throughput_per_week * (1 - self.failure_rate)


team_a_flow = FlowMetrics(
    lead_time_days=10,
    work_in_progress=8,
    throughput_per_week=5,
    failure_rate=0.10,
)

team_b_flow = FlowMetrics(
    lead_time_days=4,
    work_in_progress=4,
    throughput_per_week=6,
    failure_rate=0.05,
)

for name, metrics in [("Team A", team_a_flow), ("Team B", team_b_flow)]:
    print(f"\n{name}")
    print(f"  Quality-adjusted throughput: {metrics.quality_adjusted_throughput():.2f}")
    print(
        f"  Flow efficiency estimate: "
        f"{metrics.approximate_flow_efficiency(2):.2%}"
    )

print(
    """
Team structure affects flow through:
- Number of handoffs.
- Queue lengths.
- Dependency count.
- Decision latency.
- Cognitive load.
- Batch size.
- Ownership clarity.

High output does not necessarily mean high product performance. A team can
release many features while producing little customer value.

Useful measures should connect delivery activity with customer and business
outcomes.
"""
)


# ============================================================================
# 31. LITTLE'S LAW
# ============================================================================

section("29. LITTLE'S LAW AND TEAM FLOW")

print(
    """
Little's Law:

    WIP = Throughput × Lead Time

Therefore:

    Lead Time = WIP / Throughput

Example:
    WIP = 20 work items
    Throughput = 5 items/week

    Lead Time ≈ 20 / 5 = 4 weeks

This relationship is useful for understanding why increasing work in progress
can increase waiting time.

Team structure influences WIP indirectly through:
- Handoffs.
- Dependencies.
- Approval queues.
- Batch size.
- Team specialization.

The formula assumes a sufficiently stable system and should not be applied
blindly to transient or highly unstable processes.
"""
)

wip = 20
throughput = 5
lead_time = wip / throughput
print(f"Example lead time: {lead_time:.1f} weeks")


# ============================================================================
# 32. SECURITY AND GOVERNANCE
# ============================================================================

section("30. SECURITY AND GOVERNANCE")

print(
    """
Product team autonomy must coexist with organizational controls.

Security-sensitive boundaries may require:
- Identity and access management.
- Least privilege.
- Audit logging.
- Secure development practices.
- Vulnerability management.
- Data classification.
- Regulatory controls.
- Incident response.
- Separation of duties.

A useful model is:

    Central governance
           |
           v
    Guardrails and standards
           |
           v
    Autonomous execution

The objective is not to remove all central control. It is to centralize
controls that benefit from consistency while decentralizing decisions that
benefit from product context.

Security ownership must be explicit. A platform team should not become the
unintended owner of every application's security responsibility.
"""


# ============================================================================
# 33. ARCHITECTURE AND TEAM TOPOLOGY
# ============================================================================

section("31. ARCHITECTURE AND TEAM STRUCTURE")

print(
    """
Architecture and organizational structure influence each other.

If every product team must modify the same tightly coupled codebase, nominal
team autonomy may be misleading.

A team boundary works better when:
- Ownership boundaries are clear.
- Interfaces are stable.
- APIs are well-defined.
- Deployment can be performed safely.
- Data ownership is explicit.
- Operational responsibility is clear.

Conway's Law describes the observation that organizations tend to produce
systems reflecting their communication structures.

The practical implication is important:
Changing team topology without considering architecture can create either
stronger boundaries or new coordination problems.

Architecture should therefore be considered during organizational design.
"""


# ============================================================================
# 34. DATA OWNERSHIP
# ============================================================================

section("32. DATA OWNERSHIP ACROSS PRODUCT TEAMS")

@dataclass
class DataDomain:
    name: str
    owner_team: str
    source_of_truth: bool
    consumers: List[str]


data_domains = [
    DataDomain(
        "Customer Profile",
        "Identity Product Team",
        True,
        ["Checkout Product Team", "Marketing Product Team"],
    ),
    DataDomain(
        "Order",
        "Order Product Team",
        True,
        ["Analytics Platform Team", "Support Team"],
    ),
    DataDomain(
        "Payment Transaction",
        "Payments Platform Team",
        True,
        ["Finance Team", "Risk Team"],
    ),
]

for domain in data_domains:
    print(f"\n{domain.name}")
    print(f"  Owner: {domain.owner_team}")
    print(f"  Source of truth: {domain.source_of_truth}")
    print(f"  Consumers: {', '.join(domain.consumers)}")


# ============================================================================
# 35. PRODUCT TEAM MISSION DESIGN
# ============================================================================

section("33. TEAM MISSION DESIGN")

@dataclass
class ProductMission:
    team_name: str
    customer: str
    problem: str
    outcome: str
    boundaries: List[str]

    def is_well_formed(self) -> bool:
        return all(
            value.strip()
            for value in [self.team_name, self.customer, self.problem, self.outcome]
        ) and bool(self.boundaries)


mission = ProductMission(
    team_name="Checkout Product Team",
    customer="Customers purchasing online",
    problem="Customers abandon checkout because the process is difficult or unreliable.",
    outcome="Increase successful checkout completion while maintaining trust and payment security.",
    boundaries=[
        "Checkout experience",
        "Checkout orchestration",
        "Checkout experimentation",
    ],
)

print(f"Mission well formed: {mission.is_well_formed()}")
print(f"Outcome: {mission.outcome}")


# ============================================================================
# 36. STRUCTURE DECISION TREE
# ============================================================================

section("34. PRACTICAL STRUCTURE DECISION TREE")

def structure_decision_tree(
    needs_specialization: bool,
    needs_end_to_end_ownership: bool,
    needs_platform_capability: bool,
    needs_temporary_delivery_focus: bool,
    many_related_teams: bool,
) -> str:
    """
    Simple educational decision tree.

    Real organizational design requires qualitative analysis beyond this
    function.
    """
    if needs_platform_capability:
        return "Consider a platform team."

    if needs_temporary_delivery_focus:
        return "Consider a feature-oriented team."

    if needs_end_to_end_ownership and many_related_teams:
        return "Consider multiple product teams coordinated within a product area or tribe."

    if needs_end_to_end_ownership:
        return "Consider a cross-functional product team or squad."

    if needs_specialization:
        return "A functional structure may be appropriate, possibly combined with product teams."

    return "Use the smallest structure that provides clear ownership and sufficient capability."


cases = [
    (
        "Specialized legal/security work",
        True, False, False, False, False
    ),
    (
        "End-to-end customer problem",
        False, True, False, False, False
    ),
    (
        "Shared developer infrastructure",
        False, False, True, False, True
    ),
    (
        "Temporary migration project",
        False, False, False, True, False
    ),
    (
        "Large product with multiple related teams",
        False, True, False, False, True
    ),
]

for description, *arguments in cases:
    print(f"\n{description}:")
    print(f"  {structure_decision_tree(*arguments)}")


# ============================================================================
# 37. UNIT TESTS
# ============================================================================

section("35. VALIDATION AND TESTING")

def test_cognitive_load() -> None:
    model = CognitiveLoadModel(5, 5, 5, 5)
    assert model.total() == 20
    assert model.normalized() == 0.5


def test_dependency_pressure() -> None:
    dependencies = [
        Dependency("A", "B", "API", 8),
        Dependency("C", "A", "Data", 6),
    ]
    assert calculate_dependency_pressure(dependencies, "A") == 7


def test_team_api_validation() -> None:
    invalid_api = TeamAPI(
        team_name="",
        purpose="",
        provides=[],
        consumes=[],
        decision_authority=[],
        escalation_path="",
    )
    errors = invalid_api.validate()
    assert len(errors) == 4


def test_flow_metrics() -> None:
    metrics = FlowMetrics(10, 10, 5, 0.2)
    assert metrics.quality_adjusted_throughput() == 4
    assert metrics.approximate_flow_efficiency(5) == 0.5


def test_score_validation() -> None:
    valid = TeamScorecard(10, 9, 8, 7, 6, 5, 4)
    assert valid.score() == mean([10, 9, 8, 7, 6, 5, 4])

    try:
        TeamScorecard(11, 9, 8, 7, 6, 5, 4).score()
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid score to raise ValueError.")


def run_tests() -> None:
    tests = [
        test_cognitive_load,
        test_dependency_pressure,
        test_team_api_validation,
        test_flow_metrics,
        test_score_validation,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(f"Passed {passed}/{len(tests)} tests.")


run_tests()


# ============================================================================
# 38. PRODUCTION DESIGN PRINCIPLES
# ============================================================================

section("36. PRODUCTION-READY TEAM DESIGN PRINCIPLES")

print(
    """
1. Define ownership explicitly.
   Every important product, capability, service, and data domain should have
   an accountable owner.

2. Optimize for outcomes.
   A team should know what customer or business result it is responsible for.

3. Minimize unnecessary dependencies.
   Dependencies create coordination cost and waiting time.

4. Keep teams cognitively manageable.
   Team boundaries should reflect the amount of knowledge a team can
   realistically maintain.

5. Treat platform teams as products.
   Internal users need usable interfaces, documentation, reliability, and
   measurable value.

6. Separate career management from product prioritization when appropriate.
   Functional leadership and product leadership can have different purposes.

7. Make decision rights explicit.
   Consultation should not automatically mean approval.

8. Align architecture and organization.
   Team boundaries should be supported by technical boundaries where feasible.

9. Preserve appropriate governance.
   Security, legal, compliance, and safety constraints may require centralized
   controls.

10. Measure flow and outcomes.
    Track delivery performance, quality, customer outcomes, and business
    results rather than feature volume alone.

11. Revisit structure when the environment changes.
    A structure that worked at 20 people may be inappropriate at 500 people.

12. Avoid organizational theater.
    Renaming departments as squads, tribes, or product teams does not create
    autonomy or product ownership by itself.
"""
)


# ============================================================================
# 39. INTEGRATED EXAMPLE
# ============================================================================

section("37. INTEGRATED PRODUCT ORGANIZATION EXAMPLE")

integrated_teams = [
    Team(
        "Checkout Product Team",
        StructureType.PRODUCT,
        "Increase successful checkout completion.",
        ["Product Manager", "Designer", "Engineers", "Data Analyst"],
        True,
        True,
        9,
        3,
        (6, 9),
        [TeamInteractionMode.COLLABORATION, TeamInteractionMode.X_AS_A_SERVICE],
    ),
    Team(
        "Payments Platform",
        StructureType.PLATFORM,
        "Provide secure payment processing capabilities.",
        ["Engineers", "SRE", "Security Engineer"],
        False,
        False,
        8,
        4,
        (7, 12),
        [TeamInteractionMode.X_AS_A_SERVICE],
    ),
    Team(
        "Growth Product Team",
        StructureType.PRODUCT,
        "Improve customer acquisition and activation.",
        ["Product Manager", "Designer", "Engineers", "Data Analyst"],
        True,
        True,
        9,
        4,
        (6, 10),
        [TeamInteractionMode.COLLABORATION],
    ),
    Team(
        "Developer Platform",
        StructureType.PLATFORM,
        "Reduce engineering cognitive load through self-service tooling.",
        ["Engineers", "SRE"],
        False,
        False,
        9,
        2,
        (5, 10),
        [TeamInteractionMode.X_AS_A_SERVICE, TeamInteractionMode.FACILITATION],
    ),
]

print("Integrated team portfolio:")
for team in integrated_teams:
    print(
        f"\n{team.name}"
        f"\n  Type: {team.structure.value}"
        f"\n  Purpose: {team.purpose}"
        f"\n  Roles: {', '.join(team.roles)}"
        f"\n  Outcome ownership: {team.owns_outcome}"
        f"\n  Autonomy: {team.autonomy}/10"
        f"\n  Dependencies: {team.dependency_level}/10"
        f"\n  Interaction: {', '.join(mode.value for mode in team.interaction_modes)}"
    )


# ============================================================================
# 40. FINAL STUDY CHECK
# ============================================================================

section("38. CONCEPT CHECK")

questions = {
    "Functional teams primarily optimize around what?":
        "Professional specialization and functional capability.",
    "What distinguishes a cross-functional product team?":
        "It contains multiple capabilities needed to solve a product problem.",
    "What is a squad?":
        "A small, relatively autonomous team organized around a mission or area.",
    "What is a tribe?":
        "A grouping of related squads or teams around a broader product domain.",
    "What does a platform team provide?":
        "Reusable capabilities consumed by other teams, often through self-service.",
    "What is a feature team?":
        "A team organized primarily around delivering features or feature slices.",
    "What distinguishes a product team?":
        "Persistent ownership of a customer problem, product area, and measurable outcomes.",
    "Why do dependencies matter?":
        "They introduce coordination, queues, waiting, and decision latency.",
    "Why is cognitive load important?":
        "A team cannot maintain unlimited domain, technical, operational, and coordination knowledge.",
    "Does a team name create autonomy?":
        "No. Autonomy depends on decision rights, ownership, capabilities, architecture, and governance.",
}

for question, answer in questions.items():
    print(f"\nQ: {question}")
    print(f"A: {answer}")


# ============================================================================
# 41. EXECUTABLE REFERENCE TABLE
# ============================================================================

section("39. QUICK REFERENCE")

reference = [
    (
        "Functional",
        "Discipline",
        "Specialization",
        "Handoffs",
        "Best when strong functional capability is essential",
    ),
    (
        "Cross-functional",
        "Customer problem",
        "End-to-end capability",
        "Moderate/low",
        "Strong default for product discovery and delivery",
    ),
    (
        "Squad",
        "Mission/product area",
        "Small autonomous team",
        "Low within mission",
        "Useful as a compact team topology",
    ),
    (
        "Tribe",
        "Product domain",
        "Coordination at scale",
        "Cross-team",
        "Useful for many related teams",
    ),
    (
        "Platform",
        "Internal capability",
        "Reusable services",
        "Service dependency",
        "Useful for shared technical capabilities",
    ),
    (
        "Feature",
        "Feature",
        "Delivery focus",
        "Can be high",
        "Useful for temporary or feature-oriented work",
    ),
    (
        "Product",
        "Outcome/problem",
        "Persistent ownership",
        "Designed to be low",
        "Strong fit for continuous product management",
    ),
]

print(
    f"{'Structure':<18}"
    f"{'Organized Around':<22}"
    f"{'Primary Strength':<25}"
    f"{'Typical Risk':<20}"
)
print("-" * 90)

for row in reference:
    print(
        f"{row[0]:<18}"
        f"{row[1]:<22}"
        f"{row[2]:<25}"
        f"{row[3]:<20}"
    )

print(
    """
Key design principle:

    Structure should follow the work, ownership, required capabilities,
    decision boundaries, and organizational context.

The objective is not to maximize the number of teams, minimize hierarchy,
or adopt a particular named framework. The objective is to create a system
in which capable teams can make appropriate decisions, coordinate efficiently,
learn from customers, deliver reliably, and remain accountable for meaningful
outcomes.
"""
)

print("\nStudy script execution completed successfully.")
