"""
Stakeholder Management
======================

A self-contained study and practice script covering stakeholder management
from beginner to advanced level.

The script demonstrates:
- Internal and external stakeholders
- Stakeholder identification and classification
- Power, interest, influence, impact, urgency, legitimacy and proximity
- Stakeholder mapping
- Power-interest, influence-impact and salience models
- Stakeholder expectations and needs
- Stakeholder analysis
- Communication planning
- Communication methods and cadence
- RACI responsibilities
- Engagement strategies
- Conflict management
- Expectation management
- Stakeholder prioritisation
- Risk-based stakeholder analysis
- Change management
- Negotiation concepts
- Escalation
- Feedback loops
- Stakeholder sentiment
- Communication effectiveness
- Quantitative stakeholder scoring
- Network relationships
- Scenario simulation
- Edge cases
- Validation and error handling
- Testing
- Performance considerations
- Governance and security considerations
- A practical end-to-end stakeholder management workflow

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from statistics import mean
from typing import Dict, List, Optional, Tuple, Set
import math
import random
import re


# =============================================================================
# 1. FUNDAMENTAL TERMINOLOGY
# =============================================================================

print("=" * 80)
print("STAKEHOLDER MANAGEMENT: BEGINNER TO ADVANCED")
print("=" * 80)


def explain_basic_terms() -> None:
    """
    Demonstrates the most important beginner-level terminology.
    """

    terms = {
        "Stakeholder": (
            "A person, group, or organization that can affect a project, "
            "be affected by it, or perceive itself as affected by it."
        ),
        "Internal stakeholder": (
            "A stakeholder within the organization, such as an employee, "
            "manager, executive, project team, or internal department."
        ),
        "External stakeholder": (
            "A stakeholder outside the organization, such as a customer, "
            "supplier, regulator, partner, investor, or community."
        ),
        "Influence": (
            "The ability of a stakeholder to affect decisions, resources, "
            "people, outcomes, or project direction."
        ),
        "Interest": (
            "The degree to which a stakeholder cares about or is affected "
            "by the project or its outcome."
        ),
        "Expectation": (
            "What a stakeholder believes should happen, including expected "
            "quality, timing, communication, benefits, or behavior."
        ),
        "Engagement": (
            "The process of building and maintaining an appropriate working "
            "relationship with stakeholders."
        ),
        "Communication": (
            "The deliberate exchange of information, decisions, status, "
            "requirements, concerns, feedback, and expectations."
        ),
    }

    for term, definition in terms.items():
        print(f"\n{term}")
        print(f"  {definition}")


explain_basic_terms()


# =============================================================================
# 2. INTERNAL VS EXTERNAL STAKEHOLDERS
# =============================================================================

class StakeholderType(Enum):
    INTERNAL = "Internal"
    EXTERNAL = "External"


@dataclass
class Stakeholder:
    """
    Represents a stakeholder and the attributes used during analysis.

    Scores normally use a 1-5 scale:
    1 = very low
    5 = very high
    """

    name: str
    stakeholder_type: StakeholderType
    role: str
    influence: int
    interest: int
    impact: int
    urgency: int = 3
    legitimacy: int = 3
    proximity: int = 3
    expectations: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    preferred_channels: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate stakeholder data before analysis."""

        if not self.name.strip():
            raise ValueError("Stakeholder name cannot be empty.")

        if not self.role.strip():
            raise ValueError("Stakeholder role cannot be empty.")

        for field_name in (
            "influence",
            "interest",
            "impact",
            "urgency",
            "legitimacy",
            "proximity",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer.")

            if not 1 <= value <= 5:
                raise ValueError(
                    f"{field_name} must be between 1 and 5."
                )

    def is_internal(self) -> bool:
        return self.stakeholder_type == StakeholderType.INTERNAL

    def is_external(self) -> bool:
        return self.stakeholder_type == StakeholderType.EXTERNAL


internal_example = Stakeholder(
    name="Project Manager",
    stakeholder_type=StakeholderType.INTERNAL,
    role="Project leadership",
    influence=5,
    interest=5,
    impact=5,
    expectations=["Clear authority", "Timely decisions", "Accurate reporting"],
    concerns=["Schedule delays"],
    preferred_channels=["Meeting", "Email"],
)

external_example = Stakeholder(
    name="Customer",
    stakeholder_type=StakeholderType.EXTERNAL,
    role="Product customer",
    influence=4,
    interest=5,
    impact=5,
    expectations=["Quality product", "Reliable delivery"],
    concerns=["Cost overruns"],
    preferred_channels=["Email", "Review meeting"],
)

internal_example.validate()
external_example.validate()

print("\nInternal stakeholder example:")
print(internal_example)

print("\nExternal stakeholder example:")
print(external_example)


# =============================================================================
# 3. IDENTIFICATION
# =============================================================================

def identify_stakeholders() -> List[Stakeholder]:
    """
    Creates a realistic stakeholder register.

    Identification should happen early and should be revisited because
    stakeholder relevance can change during the project lifecycle.
    """

    stakeholders = [
        Stakeholder(
            "Project Sponsor",
            StakeholderType.INTERNAL,
            "Executive sponsor",
            5, 4, 5,
            4, 5, 4,
            ["Business value", "Executive visibility"],
            ["Poor ROI", "Major delays"],
            ["Executive meeting", "Dashboard"],
        ),
        Stakeholder(
            "Project Team",
            StakeholderType.INTERNAL,
            "Delivery team",
            4, 5, 5,
            4, 5, 5,
            ["Clear requirements", "Reasonable workload"],
            ["Scope creep", "Unclear priorities"],
            ["Team meeting", "Chat", "Task tracker"],
        ),
        Stakeholder(
            "Finance Department",
            StakeholderType.INTERNAL,
            "Financial control",
            4, 3, 4,
            3, 5, 3,
            ["Budget discipline", "Forecast accuracy"],
            ["Overspending"],
            ["Email", "Review meeting"],
        ),
        Stakeholder(
            "Customer",
            StakeholderType.EXTERNAL,
            "Product customer",
            5, 5, 5,
            5, 5, 5,
            ["Quality", "Timely delivery"],
            ["Defects", "Missed commitments"],
            ["Email", "Review meeting"],
        ),
        Stakeholder(
            "Supplier",
            StakeholderType.EXTERNAL,
            "Technology supplier",
            3, 4, 4,
            4, 4, 4,
            ["Clear purchase orders", "Predictable demand"],
            ["Late payments", "Changing requirements"],
            ["Email", "Vendor meeting"],
        ),
        Stakeholder(
            "Regulator",
            StakeholderType.EXTERNAL,
            "Compliance authority",
            5, 3, 5,
            5, 5, 3,
            ["Compliance", "Evidence"],
            ["Non-compliance"],
            ["Formal report", "Official correspondence"],
        ),
        Stakeholder(
            "Community",
            StakeholderType.EXTERNAL,
            "Affected local community",
            2, 3, 3,
            4, 4, 4,
            ["Minimal disruption"],
            ["Noise", "Environmental impact"],
            ["Public meeting", "Notice"],
        ),
    ]

    for stakeholder in stakeholders:
        stakeholder.validate()

    return stakeholders


stakeholders = identify_stakeholders()

print("\nStakeholder register:")
for stakeholder in stakeholders:
    print(
        f"- {stakeholder.name}: "
        f"{stakeholder.stakeholder_type.value}, "
        f"influence={stakeholder.influence}, "
        f"interest={stakeholder.interest}"
    )


# =============================================================================
# 4. STAKEHOLDER REGISTER
# =============================================================================

@dataclass
class StakeholderRegister:
    stakeholders: List[Stakeholder] = field(default_factory=list)

    def add(self, stakeholder: Stakeholder) -> None:
        stakeholder.validate()

        if self.get(stakeholder.name) is not None:
            raise ValueError(
                f"Stakeholder '{stakeholder.name}' already exists."
            )

        self.stakeholders.append(stakeholder)

    def get(self, name: str) -> Optional[Stakeholder]:
        normalized = name.strip().lower()

        for stakeholder in self.stakeholders:
            if stakeholder.name.lower() == normalized:
                return stakeholder

        return None

    def remove(self, name: str) -> bool:
        stakeholder = self.get(name)

        if stakeholder is None:
            return False

        self.stakeholders.remove(stakeholder)
        return True

    def internal(self) -> List[Stakeholder]:
        return [
            stakeholder
            for stakeholder in self.stakeholders
            if stakeholder.is_internal()
        ]

    def external(self) -> List[Stakeholder]:
        return [
            stakeholder
            for stakeholder in self.stakeholders
            if stakeholder.is_external()
        ]

    def sort_by_influence(self) -> List[Stakeholder]:
        return sorted(
            self.stakeholders,
            key=lambda stakeholder: stakeholder.influence,
            reverse=True,
        )


register = StakeholderRegister(stakeholders.copy())

print("\nInternal stakeholders:")
for stakeholder in register.internal():
    print(f"- {stakeholder.name}")

print("\nExternal stakeholders:")
for stakeholder in register.external():
    print(f"- {stakeholder.name}")


# =============================================================================
# 5. POWER-INTEREST GRID
# =============================================================================

class EngagementLevel(Enum):
    MONITOR = "Monitor"
    KEEP_INFORMED = "Keep Informed"
    KEEP_SATISFIED = "Keep Satisfied"
    MANAGE_CLOSELY = "Manage Closely"


def classify_power_interest(
    influence: int,
    interest: int,
) -> EngagementLevel:
    """
    Power-interest interpretation:

        High influence + high interest -> Manage closely
        High influence + low interest  -> Keep satisfied
        Low influence + high interest  -> Keep informed
        Low influence + low interest   -> Monitor
    """

    if influence >= 4 and interest >= 4:
        return EngagementLevel.MANAGE_CLOSELY

    if influence >= 4 and interest < 4:
        return EngagementLevel.KEEP_SATISFIED

    if influence < 4 and interest >= 4:
        return EngagementLevel.KEEP_INFORMED

    return EngagementLevel.MONITOR


print("\nPower-interest classification:")
for stakeholder in stakeholders:
    level = classify_power_interest(
        stakeholder.influence,
        stakeholder.interest,
    )
    print(f"- {stakeholder.name}: {level.value}")


# =============================================================================
# 6. INFLUENCE-IMPACT ANALYSIS
# =============================================================================

def influence_impact_score(stakeholder: Stakeholder) -> int:
    """
    Multiplication emphasizes cases where both influence and impact
    are significant.
    """

    return stakeholder.influence * stakeholder.impact


print("\nInfluence-impact scores:")
for stakeholder in sorted(
    stakeholders,
    key=influence_impact_score,
    reverse=True,
):
    print(
        f"- {stakeholder.name}: "
        f"{influence_impact_score(stakeholder)}"
    )


# =============================================================================
# 7. STAKEHOLDER SALIENCE
# =============================================================================

def salience_score(stakeholder: Stakeholder) -> float:
    """
    Stakeholder salience commonly considers:

    - Power
    - Legitimacy
    - Urgency

    A simple educational model multiplies normalized dimensions.
    """

    return (
        stakeholder.influence
        * stakeholder.legitimacy
        * stakeholder.urgency
    )


def salience_category(stakeholder: Stakeholder) -> str:
    score = salience_score(stakeholder)

    if score >= 80:
        return "Very high salience"

    if score >= 45:
        return "High salience"

    if score >= 20:
        return "Moderate salience"

    return "Low salience"


print("\nStakeholder salience:")
for stakeholder in sorted(
    stakeholders,
    key=salience_score,
    reverse=True,
):
    print(
        f"- {stakeholder.name}: "
        f"score={salience_score(stakeholder):.0f}, "
        f"{salience_category(stakeholder)}"
    )


# =============================================================================
# 8. STAKEHOLDER PRIORITISATION
# =============================================================================

def priority_score(stakeholder: Stakeholder) -> float:
    """
    A practical prioritisation score.

    This is not a universal industry formula. It is a transparent
    decision-support model. Real organizations should define weights
    according to context.
    """

    weights = {
        "influence": 0.25,
        "interest": 0.15,
        "impact": 0.25,
        "urgency": 0.15,
        "legitimacy": 0.10,
        "proximity": 0.10,
    }

    return (
        stakeholder.influence * weights["influence"]
        + stakeholder.interest * weights["interest"]
        + stakeholder.impact * weights["impact"]
        + stakeholder.urgency * weights["urgency"]
        + stakeholder.legitimacy * weights["legitimacy"]
        + stakeholder.proximity * weights["proximity"]
    )


def priority_category(score: float) -> str:
    if score >= 4.0:
        return "Critical"

    if score >= 3.25:
        return "High"

    if score >= 2.5:
        return "Medium"

    return "Low"


print("\nPrioritised stakeholder list:")
for stakeholder in sorted(
    stakeholders,
    key=priority_score,
    reverse=True,
):
    score = priority_score(stakeholder)
    print(
        f"- {stakeholder.name}: "
        f"{score:.2f} ({priority_category(score)})"
    )


# =============================================================================
# 9. EXPECTATION MANAGEMENT
# =============================================================================

@dataclass
class Expectation:
    stakeholder: str
    expectation: str
    importance: int
    feasibility: int
    status: str = "Unassessed"

    def validate(self) -> None:
        if not self.stakeholder.strip():
            raise ValueError("Expectation stakeholder cannot be empty.")

        if not self.expectation.strip():
            raise ValueError("Expectation cannot be empty.")

        if not 1 <= self.importance <= 5:
            raise ValueError("Importance must be between 1 and 5.")

        if not 1 <= self.feasibility <= 5:
            raise ValueError("Feasibility must be between 1 and 5.")


def classify_expectation(expectation: Expectation) -> str:
    """
    High importance and high feasibility:
        Priority commitment

    High importance and low feasibility:
        Negotiate or reset expectations

    Low importance and high feasibility:
        Consider opportunistically

    Low importance and low feasibility:
        Deprioritise
    """

    if expectation.importance >= 4 and expectation.feasibility >= 4:
        return "Priority commitment"

    if expectation.importance >= 4 and expectation.feasibility < 4:
        return "Negotiate or reset expectations"

    if expectation.importance < 4 and expectation.feasibility >= 4:
        return "Optional improvement"

    return "Deprioritise"


expectations = [
    Expectation(
        "Customer",
        "Release the product by the agreed date",
        importance=5,
        feasibility=4,
    ),
    Expectation(
        "Customer",
        "Provide every requested feature immediately",
        importance=4,
        feasibility=2,
    ),
    Expectation(
        "Finance Department",
        "Maintain approved budget",
        importance=5,
        feasibility=5,
    ),
]

print("\nExpectation analysis:")
for expectation in expectations:
    expectation.validate()
    expectation.status = classify_expectation(expectation)

    print(
        f"- {expectation.stakeholder}: "
        f"{expectation.expectation} -> {expectation.status}"
    )


# =============================================================================
# 10. EXPECTATION VS REQUIREMENT
# =============================================================================

def compare_requirement_and_expectation() -> None:
    """
    A requirement is a defined need or condition that forms part of
    an agreed scope.

    An expectation may be assumed by a stakeholder without being
    formally agreed.

    Effective management makes implicit expectations visible.
    """

    requirement = {
        "description": "System must support 1,000 concurrent users.",
        "source": "Approved specification",
        "status": "Committed",
    }

    expectation = {
        "description": "The system should always feel instant.",
        "source": "Stakeholder assumption",
        "status": "Needs clarification",
    }

    print("\nRequirement:")
    print(requirement)

    print("\nExpectation:")
    print(expectation)


compare_requirement_and_expectation()


# =============================================================================
# 11. COMMUNICATION PLANNING
# =============================================================================

@dataclass
class CommunicationPlanItem:
    stakeholder: str
    purpose: str
    information: str
    channel: str
    frequency: str
    owner: str
    escalation_trigger: str

    def validate(self) -> None:
        fields = {
            "stakeholder": self.stakeholder,
            "purpose": self.purpose,
            "information": self.information,
            "channel": self.channel,
            "frequency": self.frequency,
            "owner": self.owner,
            "escalation_trigger": self.escalation_trigger,
        }

        for field_name, value in fields.items():
            if not value.strip():
                raise ValueError(
                    f"Communication field '{field_name}' cannot be empty."
                )


communication_plan = [
    CommunicationPlanItem(
        stakeholder="Project Sponsor",
        purpose="Decision making and executive visibility",
        information="Progress, risks, budget and major decisions",
        channel="Executive review",
        frequency="Biweekly",
        owner="Project Manager",
        escalation_trigger="Critical risk or material schedule variance",
    ),
    CommunicationPlanItem(
        stakeholder="Project Team",
        purpose="Coordination",
        information="Tasks, blockers, decisions and priorities",
        channel="Team meeting and task tracker",
        frequency="Weekly",
        owner="Project Manager",
        escalation_trigger="Blocker threatens milestone",
    ),
    CommunicationPlanItem(
        stakeholder="Customer",
        purpose="Expectation alignment",
        information="Progress, scope, risks and decisions",
        channel="Review meeting",
        frequency="Weekly",
        owner="Product Manager",
        escalation_trigger="Requirement or delivery commitment changes",
    ),
    CommunicationPlanItem(
        stakeholder="Regulator",
        purpose="Compliance",
        information="Required evidence and compliance status",
        channel="Formal report",
        frequency="Milestone-based",
        owner="Compliance Lead",
        escalation_trigger="Potential regulatory breach",
    ),
]

print("\nCommunication plan:")
for item in communication_plan:
    item.validate()
    print(
        f"- {item.stakeholder}: "
        f"{item.channel}, {item.frequency}, owner={item.owner}"
    )


# =============================================================================
# 12. COMMUNICATION CHANNEL SELECTION
# =============================================================================

def choose_communication_channel(
    sensitivity: str,
    complexity: str,
    urgency: str,
    stakeholder_preference: Optional[str] = None,
) -> str:
    """
    Communication channel selection should consider:

    - Sensitivity
    - Complexity
    - Urgency
    - Need for documentation
    - Stakeholder preference

    High sensitivity should generally favor controlled channels.
    Complex issues often benefit from synchronous discussion.
    """

    sensitivity = sensitivity.lower()
    complexity = complexity.lower()
    urgency = urgency.lower()

    if sensitivity == "high":
        return "Formal controlled meeting with documented decision record"

    if urgency == "high" and complexity == "low":
        return "Direct message or phone call followed by written confirmation"

    if complexity == "high":
        return "Structured meeting followed by written action log"

    if stakeholder_preference:
        return stakeholder_preference

    return "Email or project collaboration platform"


channel_examples = [
    ("low", "low", "low"),
    ("high", "high", "medium"),
    ("medium", "high", "high"),
]

print("\nCommunication channel examples:")
for sensitivity, complexity, urgency in channel_examples:
    channel = choose_communication_channel(
        sensitivity,
        complexity,
        urgency,
    )
    print(
        f"- sensitivity={sensitivity}, "
        f"complexity={complexity}, "
        f"urgency={urgency} -> {channel}"
    )


# =============================================================================
# 13. COMMUNICATION QUALITY
# =============================================================================

@dataclass
class CommunicationMessage:
    stakeholder: str
    objective: str
    key_message: str
    evidence: str
    decision_required: Optional[str] = None
    action_owner: Optional[str] = None
    deadline: Optional[str] = None

    def validate(self) -> None:
        required_fields = {
            "stakeholder": self.stakeholder,
            "objective": self.objective,
            "key_message": self.key_message,
            "evidence": self.evidence,
        }

        for field_name, value in required_fields.items():
            if not value.strip():
                raise ValueError(
                    f"Communication field '{field_name}' is required."
                )

        if self.decision_required and not self.action_owner:
            raise ValueError(
                "A decision request should identify an action owner."
            )


message = CommunicationMessage(
    stakeholder="Project Sponsor",
    objective="Obtain approval for schedule adjustment",
    key_message="The integration milestone requires a two-week adjustment.",
    evidence="Vendor dependency has slipped by ten working days.",
    decision_required="Approve revised milestone",
    action_owner="Project Sponsor",
    deadline="Friday",
)

message.validate()

print("\nStructured communication message:")
print(message)


# =============================================================================
# 14. RACI
# =============================================================================

@dataclass
class RACIEntry:
    task: str
    responsible: Set[str]
    accountable: Set[str]
    consulted: Set[str]
    informed: Set[str]

    def validate(self) -> None:
        if not self.task.strip():
            raise ValueError("Task cannot be empty.")

        if len(self.accountable) != 1:
            raise ValueError(
                "A practical RACI assignment should normally have exactly "
                "one accountable party."
            )

        overlap = self.responsible & self.informed

        if overlap:
            raise ValueError(
                "A stakeholder should not normally be both Responsible "
                "and Informed for the same task."
            )


raci_entries = [
    RACIEntry(
        task="Approve project scope",
        responsible={"Project Manager"},
        accountable={"Project Sponsor"},
        consulted={"Customer"},
        informed={"Finance Department", "Project Team"},
    ),
    RACIEntry(
        task="Develop product",
        responsible={"Project Team"},
        accountable={"Project Manager"},
        consulted={"Customer"},
        informed={"Project Sponsor"},
    ),
]

print("\nRACI analysis:")
for entry in raci_entries:
    entry.validate()
    print(
        f"- {entry.task}: "
        f"R={', '.join(entry.responsible)}, "
        f"A={', '.join(entry.accountable)}, "
        f"C={', '.join(entry.consulted)}, "
        f"I={', '.join(entry.informed)}"
    )


# =============================================================================
# 15. CURRENT VS DESIRED ENGAGEMENT
# =============================================================================

class EngagementState(Enum):
    UNAWARE = "Unaware"
    RESISTANT = "Resistant"
    NEUTRAL = "Neutral"
    SUPPORTIVE = "Supportive"
    LEADING = "Leading"


@dataclass
class EngagementAssessment:
    stakeholder: str
    current: EngagementState
    desired: EngagementState

    def gap(self) -> int:
        order = {
            EngagementState.UNAWARE: 0,
            EngagementState.RESISTANT: 1,
            EngagementState.NEUTRAL: 2,
            EngagementState.SUPPORTIVE: 3,
            EngagementState.LEADING: 4,
        }

        return order[self.desired] - order[self.current]


engagements = [
    EngagementAssessment(
        "Project Sponsor",
        EngagementState.SUPPORTIVE,
        EngagementState.LEADING,
    ),
    EngagementAssessment(
        "Customer",
        EngagementState.NEUTRAL,
        EngagementState.SUPPORTIVE,
    ),
    EngagementAssessment(
        "Project Team",
        EngagementState.SUPPORTIVE,
        EngagementState.SUPPORTIVE,
    ),
]

print("\nEngagement gap analysis:")
for assessment in engagements:
    print(
        f"- {assessment.stakeholder}: "
        f"{assessment.current.value} -> "
        f"{assessment.desired.value}; "
        f"gap={assessment.gap()}"
    )


# =============================================================================
# 16. ENGAGEMENT STRATEGIES
# =============================================================================

def engagement_strategy(
    influence: int,
    interest: int,
    engagement_gap: int = 0,
) -> str:
    """
    Selects a strategy using power-interest logic and engagement gap.

    The numerical gap is an aid to planning, not a substitute for
    stakeholder judgment.
    """

    base_strategy = classify_power_interest(influence, interest)

    if engagement_gap >= 2:
        return (
            f"{base_strategy.value}: intensive engagement, "
            "clarification and relationship building"
        )

    if engagement_gap == 1:
        return (
            f"{base_strategy.value}: targeted engagement and "
            "frequent expectation alignment"
        )

    if engagement_gap == 0:
        return f"{base_strategy.value}: maintain current engagement"

    return (
        f"{base_strategy.value}: monitor for disengagement "
        "or changing expectations"
    )


print("\nEngagement strategies:")
for stakeholder in stakeholders:
    print(
        f"- {stakeholder.name}: "
        f"{engagement_strategy(stakeholder.influence, stakeholder.interest)}"
    )


# =============================================================================
# 17. CONFLICT MANAGEMENT
# =============================================================================

class ConflictStyle(Enum):
    AVOID = "Avoid"
    ACCOMMODATE = "Accommodate"
    COMPROMISE = "Compromise"
    COMPETE = "Compete"
    COLLABORATE = "Collaborate"


def recommend_conflict_style(
    issue_importance: int,
    relationship_importance: int,
    urgency: int,
) -> ConflictStyle:
    """
    Simplified conflict-style selection.

    High issue importance + high relationship importance:
        Collaborate

    Low issue importance + high relationship importance:
        Accommodate

    High issue importance + low relationship importance:
        Compete may be appropriate for time-critical decisions

    Medium values:
        Compromise

    Very low urgency and low importance:
        Avoid may be acceptable
    """

    if issue_importance >= 4 and relationship_importance >= 4:
        return ConflictStyle.COLLABORATE

    if issue_importance <= 2 and relationship_importance >= 4:
        return ConflictStyle.ACCOMMODATE

    if issue_importance >= 4 and relationship_importance <= 2:
        if urgency >= 4:
            return ConflictStyle.COMPETE
        return ConflictStyle.COMPROMISE

    if issue_importance <= 2 and relationship_importance <= 2:
        return ConflictStyle.AVOID

    return ConflictStyle.COMPROMISE


conflict_cases = [
    ("Strategic requirement", 5, 5, 3),
    ("Minor preference", 2, 5, 2),
    ("Critical emergency", 5, 2, 5),
    ("Scheduling disagreement", 3, 4, 3),
]

print("\nConflict management examples:")
for name, issue, relationship, urgency in conflict_cases:
    style = recommend_conflict_style(
        issue,
        relationship,
        urgency,
    )
    print(f"- {name}: {style.value}")


# =============================================================================
# 18. CONFLICT RESOLUTION PROCESS
# =============================================================================

@dataclass
class Conflict:
    issue: str
    stakeholder_a: str
    stakeholder_b: str
    facts: List[str]
    interests_a: List[str]
    interests_b: List[str]
    constraints: List[str]

    def identify_shared_interests(self) -> List[str]:
        normalized_a = {item.lower() for item in self.interests_a}
        normalized_b = {item.lower() for item in self.interests_b}

        return sorted(normalized_a & normalized_b)

    def resolution_factors(self) -> Dict[str, int]:
        return {
            "facts": len(self.facts),
            "shared_interests": len(self.identify_shared_interests()),
            "constraints": len(self.constraints),
        }


conflict = Conflict(
    issue="Delivery date disagreement",
    stakeholder_a="Customer",
    stakeholder_b="Project Team",
    facts=[
        "Original delivery date was agreed in the contract.",
        "A third-party dependency has slipped.",
    ],
    interests_a=["predictable delivery", "quality"],
    interests_b=["quality", "predictable delivery"],
    constraints=["vendor delay", "fixed release window"],
)

print("\nConflict analysis:")
print(f"Issue: {conflict.issue}")
print(f"Shared interests: {conflict.identify_shared_interests()}")
print(f"Resolution factors: {conflict.resolution_factors()}")


# =============================================================================
# 19. NEGOTIATION
# =============================================================================

@dataclass
class NegotiationPosition:
    stakeholder: str
    stated_position: str
    underlying_interests: List[str]
    minimum_acceptable_outcome: str
    preferred_outcome: str


def compare_positions(
    first: NegotiationPosition,
    second: NegotiationPosition,
) -> Dict[str, Set[str]]:
    first_interests = {
        item.lower() for item in first.underlying_interests
    }

    second_interests = {
        item.lower() for item in second.underlying_interests
    }

    return {
        "shared": first_interests & second_interests,
        "first_only": first_interests - second_interests,
        "second_only": second_interests - first_interests,
    }


negotiation_a = NegotiationPosition(
    stakeholder="Customer",
    stated_position="Deliver by 30 June",
    underlying_interests=["market timing", "quality", "predictability"],
    minimum_acceptable_outcome="Deliver by 15 July",
    preferred_outcome="Deliver by 30 June",
)

negotiation_b = NegotiationPosition(
    stakeholder="Project Team",
    stated_position="Deliver by 15 July",
    underlying_interests=["quality", "predictability", "manageable workload"],
    minimum_acceptable_outcome="Deliver by 15 July",
    preferred_outcome="Deliver by 15 July",
)

print("\nNegotiation analysis:")
print(compare_positions(negotiation_a, negotiation_b))


# =============================================================================
# 20. STAKEHOLDER RISKS
# =============================================================================

@dataclass
class StakeholderRisk:
    stakeholder: str
    description: str
    probability: int
    impact: int
    response: str

    def score(self) -> int:
        return self.probability * self.impact

    def validate(self) -> None:
        if not 1 <= self.probability <= 5:
            raise ValueError("Probability must be 1-5.")

        if not 1 <= self.impact <= 5:
            raise ValueError("Impact must be 1-5.")

        if not self.description.strip():
            raise ValueError("Risk description cannot be empty.")

        if not self.response.strip():
            raise ValueError("Risk response cannot be empty.")


stakeholder_risks = [
    StakeholderRisk(
        "Customer",
        "Loss of confidence due to repeated missed milestones",
        4,
        5,
        "Increase transparency and agree recovery plan",
    ),
    StakeholderRisk(
        "Regulator",
        "Delayed submission of compliance evidence",
        2,
        5,
        "Establish compliance milestone tracking",
    ),
    StakeholderRisk(
        "Project Team",
        "Resistance caused by uncontrolled scope changes",
        4,
        4,
        "Strengthen change-control process",
    ),
]

print("\nStakeholder risk register:")
for risk in stakeholder_risks:
    risk.validate()
    print(
        f"- {risk.stakeholder}: "
        f"risk score={risk.score()}, "
        f"response={risk.response}"
    )


# =============================================================================
# 21. CHANGE MANAGEMENT AND STAKEHOLDERS
# =============================================================================

@dataclass
class ChangeRequest:
    description: str
    affected_stakeholders: List[str]
    expected_benefit: int
    disruption: int
    urgency: int

    def score(self) -> float:
        """
        Educational prioritisation model.

        Benefit increases the score.
        Disruption reduces the score.
        Urgency increases the score.
        """

        return (
            self.expected_benefit * 0.45
            + self.urgency * 0.30
            - self.disruption * 0.25
        )


change_requests = [
    ChangeRequest(
        "Add customer reporting dashboard",
        ["Customer", "Project Team", "Project Sponsor"],
        expected_benefit=5,
        disruption=3,
        urgency=4,
    ),
    ChangeRequest(
        "Change internal color scheme",
        ["Project Team"],
        expected_benefit=2,
        disruption=2,
        urgency=1,
    ),
]

print("\nChange request prioritisation:")
for change in sorted(
    change_requests,
    key=lambda item: item.score(),
    reverse=True,
):
    print(
        f"- {change.description}: "
        f"score={change.score():.2f}"
    )


# =============================================================================
# 22. STAKEHOLDER SENTIMENT
# =============================================================================

class Sentiment(Enum):
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"
    POSITIVE = "Positive"


@dataclass
class SentimentObservation:
    stakeholder: str
    sentiment: Sentiment
    confidence: float
    evidence: str

    def validate(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1.")

        if not self.evidence.strip():
            raise ValueError("Evidence cannot be empty.")


sentiment_observations = [
    SentimentObservation(
        "Customer",
        Sentiment.NEGATIVE,
        0.90,
        "Two consecutive milestone complaints",
    ),
    SentimentObservation(
        "Project Sponsor",
        Sentiment.POSITIVE,
        0.80,
        "Explicit support for recovery plan",
    ),
    SentimentObservation(
        "Project Team",
        Sentiment.NEUTRAL,
        0.70,
        "Mixed feedback about workload",
    ),
]

print("\nStakeholder sentiment:")
for observation in sentiment_observations:
    observation.validate()
    print(
        f"- {observation.stakeholder}: "
        f"{observation.sentiment.value}, "
        f"confidence={observation.confidence:.0%}"
    )


# =============================================================================
# 23. COMMUNICATION EFFECTIVENESS
# =============================================================================

@dataclass
class CommunicationMetric:
    stakeholder: str
    message_delivered: bool
    understood: bool
    action_completed: bool
    response_time_hours: float

    def effectiveness_score(self) -> float:
        """
        Measures communication outcome rather than message volume.

        A message is not automatically effective because it was sent.
        Understanding and action completion matter.
        """

        score = 0.0

        if self.message_delivered:
            score += 0.30

        if self.understood:
            score += 0.35

        if self.action_completed:
            score += 0.35

        return score


communication_metrics = [
    CommunicationMetric("Customer", True, True, True, 12),
    CommunicationMetric("Project Sponsor", True, True, False, 30),
    CommunicationMetric("Project Team", True, False, False, 8),
]

print("\nCommunication effectiveness:")
for metric in communication_metrics:
    print(
        f"- {metric.stakeholder}: "
        f"{metric.effectiveness_score():.0%}"
    )


# =============================================================================
# 24. STAKEHOLDER FEEDBACK LOOP
# =============================================================================

@dataclass
class Feedback:
    stakeholder: str
    topic: str
    rating: int
    comment: str

    def validate(self) -> None:
        if not 1 <= self.rating <= 5:
            raise ValueError("Feedback rating must be 1-5.")

        if not self.comment.strip():
            raise ValueError("Feedback comment cannot be empty.")


class FeedbackLoop:
    def __init__(self) -> None:
        self.feedback: List[Feedback] = []

    def add(self, feedback: Feedback) -> None:
        feedback.validate()
        self.feedback.append(feedback)

    def average_rating(self) -> float:
        if not self.feedback:
            return 0.0

        return mean(item.rating for item in self.feedback)

    def by_stakeholder(self, stakeholder: str) -> List[Feedback]:
        return [
            item
            for item in self.feedback
            if item.stakeholder.lower() == stakeholder.lower()
        ]

    def improvement_areas(self) -> List[str]:
        return [
            item.topic
            for item in self.feedback
            if item.rating <= 2
        ]


feedback_loop = FeedbackLoop()

feedback_loop.add(
    Feedback(
        "Customer",
        "Communication frequency",
        2,
        "Updates are too infrequent.",
    )
)

feedback_loop.add(
    Feedback(
        "Customer",
        "Transparency",
        3,
        "Risk reporting is improving.",
    )
)

feedback_loop.add(
    Feedback(
        "Project Team",
        "Requirement clarity",
        2,
        "Several requirements remain ambiguous.",
    )
)

print("\nFeedback loop:")
print(f"Average rating: {feedback_loop.average_rating():.2f}")
print(f"Improvement areas: {feedback_loop.improvement_areas()}")


# =============================================================================
# 25. STAKEHOLDER RELATIONSHIP NETWORK
# =============================================================================

class StakeholderNetwork:
    """
    A simple directed graph representing stakeholder relationships.

    Example:
        Sponsor -> Project Manager
        Customer -> Product Manager
        Regulator -> Compliance Lead

    Relationships can represent communication paths, dependencies,
    influence or escalation channels.
    """

    def __init__(self) -> None:
        self.graph: Dict[str, Set[str]] = defaultdict(set)

    def add_relationship(self, source: str, target: str) -> None:
        if not source.strip() or not target.strip():
            raise ValueError("Source and target cannot be empty.")

        self.graph[source].add(target)

    def neighbors(self, stakeholder: str) -> Set[str]:
        return set(self.graph.get(stakeholder, set()))

    def all_nodes(self) -> Set[str]:
        nodes = set(self.graph.keys())

        for targets in self.graph.values():
            nodes.update(targets)

        return nodes

    def influence_count(self) -> Dict[str, int]:
        return {
            node: sum(
                1
                for targets in self.graph.values()
                if node in targets
            )
            for node in self.all_nodes()
        }

    def shortest_path(
        self,
        start: str,
        target: str,
    ) -> Optional[List[str]]:
        if start == target:
            return [start]

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            for neighbor in self.neighbors(current):
                if neighbor in visited:
                    continue

                new_path = path + [neighbor]

                if neighbor == target:
                    return new_path

                visited.add(neighbor)
                queue.append((neighbor, new_path))

        return None


network = StakeholderNetwork()

network.add_relationship("Project Sponsor", "Project Manager")
network.add_relationship("Customer", "Product Manager")
network.add_relationship("Project Manager", "Project Team")
network.add_relationship("Product Manager", "Project Team")
network.add_relationship("Regulator", "Compliance Lead")
network.add_relationship("Compliance Lead", "Project Manager")

print("\nStakeholder network:")
print(f"Nodes: {sorted(network.all_nodes())}")
print(f"Inbound influence count: {network.influence_count()}")

print(
    "Path from Regulator to Project Team:",
    network.shortest_path(
        "Regulator",
        "Project Team",
    ),
)


# =============================================================================
# 26. IDENTIFYING CENTRAL STAKEHOLDERS
# =============================================================================

def central_stakeholders(
    network: StakeholderNetwork,
) -> List[Tuple[str, int]]:
    """
    Uses inbound relationship count as a simple centrality measure.

    This is intentionally simple. Large organizational networks can use
    more advanced graph metrics such as degree, betweenness or eigenvector
    centrality.
    """

    counts = network.influence_count()

    return sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )


print("\nCentral stakeholder approximation:")
for name, count in central_stakeholders(network):
    print(f"- {name}: {count}")


# =============================================================================
# 27. STAKEHOLDER MAPPING
# =============================================================================

def power_interest_matrix(
    stakeholders: List[Stakeholder],
) -> Dict[str, List[str]]:
    matrix = {
        EngagementLevel.MANAGE_CLOSELY.value: [],
        EngagementLevel.KEEP_SATISFIED.value: [],
        EngagementLevel.KEEP_INFORMED.value: [],
        EngagementLevel.MONITOR.value: [],
    }

    for stakeholder in stakeholders:
        category = classify_power_interest(
            stakeholder.influence,
            stakeholder.interest,
        )
        matrix[category.value].append(stakeholder.name)

    return matrix


matrix = power_interest_matrix(stakeholders)

print("\nPower-interest matrix:")
for category, names in matrix.items():
    print(f"{category}:")
    for name in names:
        print(f"  - {name}")


# =============================================================================
# 28. STAKEHOLDER HEAT SCORE
# =============================================================================

def stakeholder_heat_score(stakeholder: Stakeholder) -> float:
    """
    Combines several dimensions into an attention indicator.

    The score is not a universal standard. It is useful for prioritising
    attention when many stakeholders exist.
    """

    return (
        0.25 * stakeholder.influence
        + 0.20 * stakeholder.interest
        + 0.20 * stakeholder.impact
        + 0.15 * stakeholder.urgency
        + 0.10 * stakeholder.legitimacy
        + 0.10 * stakeholder.proximity
    )


print("\nStakeholder heat scores:")
for stakeholder in sorted(
    stakeholders,
    key=stakeholder_heat_score,
    reverse=True,
):
    print(
        f"- {stakeholder.name}: "
        f"{stakeholder_heat_score(stakeholder):.2f}"
    )


# =============================================================================
# 29. NORMALISATION
# =============================================================================

def normalize_score(value: float, minimum: float = 1, maximum: float = 5) -> float:
    """
    Converts a score from a 1-5 scale to a 0-1 scale.

    Normalisation allows different metrics to be combined more safely.
    """

    if maximum <= minimum:
        raise ValueError("Maximum must be greater than minimum.")

    if value < minimum or value > maximum:
        raise ValueError("Value must fall within the supplied range.")

    return (value - minimum) / (maximum - minimum)


print("\nNormalised examples:")
for value in [1, 2, 3, 4, 5]:
    print(f"{value} -> {normalize_score(value):.2f}")


# =============================================================================
# 30. WEIGHTED STAKEHOLDER MODEL
# =============================================================================

@dataclass
class StakeholderWeights:
    influence: float
    interest: float
    impact: float
    urgency: float
    legitimacy: float
    proximity: float

    def validate(self) -> None:
        values = [
            self.influence,
            self.interest,
            self.impact,
            self.urgency,
            self.legitimacy,
            self.proximity,
        ]

        if any(value < 0 for value in values):
            raise ValueError("Weights cannot be negative.")

        if not math.isclose(sum(values), 1.0, rel_tol=1e-9):
            raise ValueError("Weights must sum to 1.")


def weighted_stakeholder_score(
    stakeholder: Stakeholder,
    weights: StakeholderWeights,
) -> float:
    weights.validate()

    scores = {
        "influence": normalize_score(stakeholder.influence),
        "interest": normalize_score(stakeholder.interest),
        "impact": normalize_score(stakeholder.impact),
        "urgency": normalize_score(stakeholder.urgency),
        "legitimacy": normalize_score(stakeholder.legitimacy),
        "proximity": normalize_score(stakeholder.proximity),
    }

    return (
        scores["influence"] * weights.influence
        + scores["interest"] * weights.interest
        + scores["impact"] * weights.impact
        + scores["urgency"] * weights.urgency
        + scores["legitimacy"] * weights.legitimacy
        + scores["proximity"] * weights.proximity
    )


weights = StakeholderWeights(
    influence=0.25,
    interest=0.15,
    impact=0.25,
    urgency=0.15,
    legitimacy=0.10,
    proximity=0.10,
)

print("\nWeighted stakeholder scores:")
for stakeholder in stakeholders:
    print(
        f"- {stakeholder.name}: "
        f"{weighted_stakeholder_score(stakeholder, weights):.3f}"
    )


# =============================================================================
# 31. STAKEHOLDER DYNAMICS
# =============================================================================

@dataclass
class StakeholderSnapshot:
    period: str
    influence: int
    interest: int
    sentiment: Sentiment


class StakeholderTrend:
    def __init__(self, stakeholder: str) -> None:
        self.stakeholder = stakeholder
        self.snapshots: List[StakeholderSnapshot] = []

    def add_snapshot(self, snapshot: StakeholderSnapshot) -> None:
        if not 1 <= snapshot.influence <= 5:
            raise ValueError("Influence must be 1-5.")

        if not 1 <= snapshot.interest <= 5:
            raise ValueError("Interest must be 1-5.")

        self.snapshots.append(snapshot)

    def influence_change(self) -> int:
        if len(self.snapshots) < 2:
            return 0

        return (
            self.snapshots[-1].influence
            - self.snapshots[0].influence
        )

    def interest_change(self) -> int:
        if len(self.snapshots) < 2:
            return 0

        return (
            self.snapshots[-1].interest
            - self.snapshots[0].interest
        )


customer_trend = StakeholderTrend("Customer")

customer_trend.add_snapshot(
    StakeholderSnapshot(
        "Month 1",
        influence=4,
        interest=4,
        sentiment=Sentiment.POSITIVE,
    )
)

customer_trend.add_snapshot(
    StakeholderSnapshot(
        "Month 2",
        influence=5,
        interest=5,
        sentiment=Sentiment.NEUTRAL,
    )
)

customer_trend.add_snapshot(
    StakeholderSnapshot(
        "Month 3",
        influence=5,
        interest=5,
        sentiment=Sentiment.NEGATIVE,
    )
)

print("\nStakeholder trend:")
print(f"Influence change: {customer_trend.influence_change()}")
print(f"Interest change: {customer_trend.interest_change()}")


# =============================================================================
# 32. ESCALATION MANAGEMENT
# =============================================================================

@dataclass
class EscalationRule:
    name: str
    condition: str
    severity_threshold: int
    owner: str


@dataclass
class Issue:
    title: str
    severity: int
    stakeholder: str
    unresolved_hours: float

    def validate(self) -> None:
        if not 1 <= self.severity <= 5:
            raise ValueError("Severity must be 1-5.")

        if self.unresolved_hours < 0:
            raise ValueError("Unresolved hours cannot be negative.")


escalation_rules = [
    EscalationRule(
        "Critical stakeholder issue",
        "Severity >= 4",
        4,
        "Project Manager",
    ),
    EscalationRule(
        "Executive escalation",
        "Severity >= 5 and unresolved > 24 hours",
        5,
        "Project Sponsor",
    ),
]


def escalation_required(issue: Issue) -> Optional[str]:
    issue.validate()

    if issue.severity >= 5 and issue.unresolved_hours > 24:
        return "Executive escalation"

    if issue.severity >= 4:
        return "Critical stakeholder issue"

    return None


issues = [
    Issue(
        "Customer acceptance concern",
        severity=4,
        stakeholder="Customer",
        unresolved_hours=10,
    ),
    Issue(
        "Regulatory compliance concern",
        severity=5,
        stakeholder="Regulator",
        unresolved_hours=30,
    ),
    Issue(
        "Minor reporting preference",
        severity=2,
        stakeholder="Finance Department",
        unresolved_hours=5,
    ),
]

print("\nEscalation analysis:")
for issue in issues:
    print(
        f"- {issue.title}: "
        f"{escalation_required(issue) or 'No escalation'}"
    )


# =============================================================================
# 33. STAKEHOLDER DECISION RIGHTS
# =============================================================================

@dataclass
class Decision:
    title: str
    decision_owner: str
    consulted_stakeholders: Set[str]
    informed_stakeholders: Set[str]
    deadline: str

    def validate(self) -> None:
        if not self.decision_owner.strip():
            raise ValueError("Decision owner is required.")

        if not self.title.strip():
            raise ValueError("Decision title is required.")

        if self.decision_owner in self.informed_stakeholders:
            raise ValueError(
                "Decision owner should not be classified only as informed."
            )


decisions = [
    Decision(
        "Approve revised delivery date",
        "Project Sponsor",
        {"Customer", "Project Manager"},
        {"Project Team", "Finance Department"},
        "Friday",
    ),
    Decision(
        "Approve technical architecture",
        "Project Manager",
        {"Project Team", "Customer"},
        {"Project Sponsor"},
        "Wednesday",
    ),
]

print("\nDecision ownership:")
for decision in decisions:
    decision.validate()
    print(
        f"- {decision.title}: "
        f"owner={decision.decision_owner}"
    )


# =============================================================================
# 34. MEETING DESIGN
# =============================================================================

@dataclass
class StakeholderMeeting:
    title: str
    objective: str
    participants: List[str]
    decisions_needed: List[str]
    pre_read: List[str]
    outputs: List[str]

    def is_well_defined(self) -> bool:
        return bool(
            self.title.strip()
            and self.objective.strip()
            and self.participants
            and self.outputs
        )


meeting = StakeholderMeeting(
    title="Customer steering review",
    objective="Review progress, risks and required decisions",
    participants=["Customer", "Project Manager", "Project Sponsor"],
    decisions_needed=["Approve revised milestone"],
    pre_read=["Status report", "Risk register"],
    outputs=["Decision record", "Updated action list"],
)

print("\nMeeting quality check:")
print(f"Well defined: {meeting.is_well_defined()}")


# =============================================================================
# 35. STAKEHOLDER COMMUNICATION CADENCE
# =============================================================================

@dataclass
class CommunicationCadence:
    stakeholder: str
    minimum_frequency_days: int
    maximum_frequency_days: int

    def validate(self) -> None:
        if self.minimum_frequency_days < 0:
            raise ValueError("Minimum frequency cannot be negative.")

        if (
            self.maximum_frequency_days
            < self.minimum_frequency_days
        ):
            raise ValueError(
                "Maximum frequency cannot be below minimum frequency."
            )


cadences = [
    CommunicationCadence("Customer", 7, 14),
    CommunicationCadence("Project Sponsor", 14, 30),
    CommunicationCadence("Project Team", 1, 7),
    CommunicationCadence("Regulator", 30, 90),
]

print("\nCommunication cadence:")
for cadence in cadences:
    cadence.validate()
    print(
        f"- {cadence.stakeholder}: "
        f"{cadence.minimum_frequency_days}-"
        f"{cadence.maximum_frequency_days} days"
    )


# =============================================================================
# 36. COMMON STAKEHOLDER MANAGEMENT MISTAKES
# =============================================================================

common_mistakes = {
    "Identifying stakeholders only once": (
        "Stakeholders and their influence can change over time."
    ),
    "Treating every stakeholder identically": (
        "Different stakeholders require different levels and forms of engagement."
    ),
    "Confusing communication volume with communication quality": (
        "Frequent communication is ineffective if the message is unclear or "
        "the stakeholder does not understand the required action."
    ),
    "Ignoring low-power stakeholders": (
        "Low-power stakeholders may still have high interest, local knowledge, "
        "legitimacy or the ability to create reputational consequences."
    ),
    "Overpromising": (
        "Unrealistic commitments create trust problems and future conflict."
    ),
    "Failing to document decisions": (
        "Undocumented decisions can produce conflicting interpretations."
    ),
    "Using technical language with non-technical stakeholders": (
        "Communication should match stakeholder knowledge and decision needs."
    ),
    "Escalating too late": (
        "Delayed escalation can reduce the available options for recovery."
    ),
}

print("\nCommon mistakes:")
for mistake, consequence in common_mistakes.items():
    print(f"- {mistake}: {consequence}")


# =============================================================================
# 37. EDGE CASES
# =============================================================================

def demonstrate_edge_cases() -> None:
    """
    Stakeholder analysis has several situations where simplistic
    classifications can fail.
    """

    cases = [
        {
            "name": "High interest, low formal power",
            "influence": 2,
            "interest": 5,
            "interpretation": (
                "Keep informed, but do not assume the stakeholder is unimportant."
            ),
        },
        {
            "name": "High formal power, low interest",
            "influence": 5,
            "interest": 2,
            "interpretation": (
                "Keep satisfied and monitor for changes in interest."
            ),
        },
        {
            "name": "Stakeholder changes category",
            "influence": 3,
            "interest": 3,
            "interpretation": (
                "A stakeholder's position may change after an organizational "
                "restructure or project milestone."
            ),
        },
        {
            "name": "Conflicting stakeholder expectations",
            "influence": 5,
            "interest": 5,
            "interpretation": (
                "Prioritise transparent negotiation rather than satisfying "
                "all expectations simultaneously."
            ),
        },
        {
            "name": "Stakeholder anonymity",
            "influence": 1,
            "interest": 5,
            "interpretation": (
                "Where legitimate concerns can be raised anonymously, "
                "the absence of identity should not automatically invalidate "
                "the underlying issue."
            ),
        },
    ]

    print("\nEdge cases:")

    for case in cases:
        classification = classify_power_interest(
            case["influence"],
            case["interest"],
        )

        print(
            f"- {case['name']}: "
            f"{classification.value}. "
            f"{case['interpretation']}"
        )


demonstrate_edge_cases()


# =============================================================================
# 38. INTERNAL VS EXTERNAL COMMUNICATION COMPARISON
# =============================================================================

def compare_internal_external_communication() -> Dict[str, Dict[str, str]]:
    return {
        "Internal": {
            "primary_focus": "Coordination and organizational execution",
            "typical_language": "Operational and organizational terminology",
            "examples": "Team meetings, internal dashboards, management reviews",
            "major_risk": "Misalignment or internal resistance",
        },
        "External": {
            "primary_focus": "Relationship, commitments, trust and external impact",
            "typical_language": "Audience-specific and commercially appropriate",
            "examples": "Customer reviews, vendor meetings, regulatory reports",
            "major_risk": "Reputational, contractual or regulatory consequences",
        },
    }


print("\nInternal vs external communication:")
comparison = compare_internal_external_communication()

for stakeholder_type, details in comparison.items():
    print(f"\n{stakeholder_type}:")
    for key, value in details.items():
        print(f"  {key}: {value}")


# =============================================================================
# 39. COMMUNICATION PLAN VALIDATION
# =============================================================================

def validate_communication_plan(
    plan: List[CommunicationPlanItem],
) -> List[str]:
    errors: List[str] = []

    seen = set()

    for item in plan:
        try:
            item.validate()
        except (ValueError, TypeError) as error:
            errors.append(str(error))

        key = (
            item.stakeholder.lower(),
            item.purpose.lower(),
        )

        if key in seen:
            errors.append(
                f"Duplicate communication purpose for {item.stakeholder}."
            )

        seen.add(key)

    return errors


print("\nCommunication plan validation:")
plan_errors = validate_communication_plan(communication_plan)

if plan_errors:
    for error in plan_errors:
        print(f"- ERROR: {error}")
else:
    print("No validation errors found.")


# =============================================================================
# 40. STAKEHOLDER REGISTER VALIDATION
# =============================================================================

def validate_register(
    register: StakeholderRegister,
) -> List[str]:
    errors: List[str] = []

    names = set()

    for stakeholder in register.stakeholders:
        try:
            stakeholder.validate()
        except (ValueError, TypeError) as error:
            errors.append(
                f"{stakeholder.name}: {error}"
            )

        normalized_name = stakeholder.name.strip().lower()

        if normalized_name in names:
            errors.append(
                f"Duplicate stakeholder: {stakeholder.name}"
            )

        names.add(normalized_name)

    return errors


print("\nStakeholder register validation:")
register_errors = validate_register(register)

if register_errors:
    for error in register_errors:
        print(f"- ERROR: {error}")
else:
    print("No validation errors found.")


# =============================================================================
# 41. PERFORMANCE CONSIDERATIONS
# =============================================================================

def performance_demo(number_of_stakeholders: int = 1000) -> Dict[str, float]:
    """
    Generates a larger stakeholder collection to illustrate algorithmic
    considerations.

    Most basic stakeholder classifications are O(n).
    Sorting stakeholders is O(n log n).
    A naive all-pairs comparison is O(n²).
    """

    if number_of_stakeholders < 1:
        raise ValueError("Number of stakeholders must be positive.")

    generated = [
        Stakeholder(
            name=f"Stakeholder {index}",
            stakeholder_type=(
                StakeholderType.INTERNAL
                if index % 2 == 0
                else StakeholderType.EXTERNAL
            ),
            role="Generated role",
            influence=(index % 5) + 1,
            interest=((index + 1) % 5) + 1,
            impact=((index + 2) % 5) + 1,
        )
        for index in range(number_of_stakeholders)
    ]

    start_size = len(generated)

    linear_result = [
        stakeholder
        for stakeholder in generated
        if stakeholder.influence >= 4
    ]

    sorted_result = sorted(
        generated,
        key=priority_score,
        reverse=True,
    )

    pair_count = number_of_stakeholders * (
        number_of_stakeholders - 1
    ) // 2

    return {
        "stakeholders": start_size,
        "linear_filter_result": len(linear_result),
        "sorted_result": len(sorted_result),
        "potential_pairs": pair_count,
    }


print("\nPerformance model:")
print(performance_demo(1000))


# =============================================================================
# 42. SECURITY AND CONFIDENTIALITY CONSIDERATIONS
# =============================================================================

security_principles = [
    (
        "Need-to-know access",
        "Sensitive stakeholder information should only be available to people "
        "who require it for legitimate work."
    ),
    (
        "Data minimisation",
        "Record only stakeholder information that is relevant to the purpose."
    ),
    (
        "Confidential concerns",
        "Sensitive complaints or whistleblowing information should not be "
        "distributed broadly."
    ),
    (
        "Access control",
        "Stakeholder registers containing sensitive information should be "
        "protected through appropriate permissions."
    ),
    (
        "Auditability",
        "Important decisions and approvals should have traceable records."
    ),
    (
        "Privacy",
        "Personal information should be handled according to applicable "
        "privacy requirements and organizational policy."
    ),
]

print("\nSecurity and confidentiality principles:")
for principle, explanation in security_principles:
    print(f"- {principle}: {explanation}")


# =============================================================================
# 43. GOVERNANCE CONSIDERATIONS
# =============================================================================

governance_checks = {
    "Decision rights": "Are decision makers explicitly identified?",
    "Escalation": "Are escalation thresholds defined?",
    "Accountability": "Is each important action assigned to an owner?",
    "Documentation": "Are important commitments and decisions recorded?",
    "Review frequency": "Is stakeholder analysis periodically reviewed?",
    "Conflicts": "Are conflicts of interest identified and handled?",
    "Compliance": "Are regulatory stakeholders and obligations tracked?",
}

print("\nGovernance checks:")
for check, question in governance_checks.items():
    print(f"- {check}: {question}")


# =============================================================================
# 44. PRODUCTION-ORIENTED STAKEHOLDER MANAGEMENT SYSTEM
# =============================================================================

@dataclass
class StakeholderManagementSystem:
    """
    Integrates stakeholder identification, analysis, communication,
    risk and engagement information into one structure.

    A production system would typically persist this information in
    a database and enforce role-based access controls.
    """

    register: StakeholderRegister
    risks: List[StakeholderRisk] = field(default_factory=list)
    communications: List[CommunicationPlanItem] = field(
        default_factory=list
    )
    feedback: FeedbackLoop = field(default_factory=FeedbackLoop)

    def critical_stakeholders(self) -> List[Stakeholder]:
        return [
            stakeholder
            for stakeholder in self.register.stakeholders
            if priority_category(priority_score(stakeholder))
            == "Critical"
        ]

    def high_risk_stakeholders(self) -> List[str]:
        return [
            risk.stakeholder
            for risk in self.risks
            if risk.score() >= 15
        ]

    def stakeholders_needing_attention(self) -> List[str]:
        """
        Combines several indicators rather than relying on a single
        stakeholder dimension.
        """

        attention = set()

        for stakeholder in self.register.stakeholders:
            if stakeholder_heat_score(stakeholder) >= 4.0:
                attention.add(stakeholder.name)

        for risk in self.risks:
            if risk.score() >= 15:
                attention.add(risk.stakeholder)

        return sorted(attention)


system = StakeholderManagementSystem(
    register=register,
    risks=stakeholder_risks,
    communications=communication_plan,
)

system.feedback.add(
    Feedback(
        "Customer",
        "Project transparency",
        2,
        "Stakeholder requested more frequent risk updates.",
    )
)

print("\nIntegrated stakeholder management system:")
print(
    "Critical stakeholders:",
    [item.name for item in system.critical_stakeholders()],
)
print(
    "High-risk stakeholders:",
    system.high_risk_stakeholders(),
)
print(
    "Stakeholders needing attention:",
    system.stakeholders_needing_attention(),
)


# =============================================================================
# 45. END-TO-END PROJECT SCENARIO
# =============================================================================

def run_end_to_end_scenario() -> None:
    """
    Simulates a stakeholder management workflow for a software
    implementation project.
    """

    print("\n" + "=" * 80)
    print("END-TO-END STAKEHOLDER MANAGEMENT SCENARIO")
    print("=" * 80)

    scenario_stakeholders = [
        Stakeholder(
            "Executive Sponsor",
            StakeholderType.INTERNAL,
            "Funding and strategic oversight",
            5, 4, 5,
            expectations=[
                "Business value",
                "Controlled budget",
                "Predictable delivery",
            ],
            concerns=[
                "Budget overrun",
                "Strategic failure",
            ],
        ),
        Stakeholder(
            "Implementation Team",
            StakeholderType.INTERNAL,
            "Technical delivery",
            4, 5, 5,
            expectations=[
                "Clear requirements",
                "Stable priorities",
                "Adequate resources",
            ],
            concerns=[
                "Scope creep",
                "Resource constraints",
            ],
        ),
        Stakeholder(
            "Customer",
            StakeholderType.EXTERNAL,
            "Business user",
            5, 5, 5,
            expectations=[
                "Usable solution",
                "On-time delivery",
                "Training",
            ],
            concerns=[
                "Operational disruption",
                "Poor usability",
            ],
        ),
        Stakeholder(
            "Vendor",
            StakeholderType.EXTERNAL,
            "Third-party technology provider",
            3, 4, 4,
            expectations=[
                "Stable specifications",
                "Timely approvals",
            ],
            concerns=[
                "Requirement changes",
                "Payment delays",
            ],
        ),
    ]

    scenario_register = StakeholderRegister(
        scenario_stakeholders
    )

    print("\nStep 1: Identify stakeholders")

    for stakeholder in scenario_register.stakeholders:
        print(
            f"- {stakeholder.name} "
            f"({stakeholder.stakeholder_type.value})"
        )

    print("\nStep 2: Analyse influence and interest")

    for stakeholder in scenario_register.stakeholders:
        category = classify_power_interest(
            stakeholder.influence,
            stakeholder.interest,
        )

        print(
            f"- {stakeholder.name}: "
            f"{category.value}"
        )

    print("\nStep 3: Assess expectations")

    for stakeholder in scenario_register.stakeholders:
        print(f"- {stakeholder.name}")

        for expectation in stakeholder.expectations:
            print(f"  Expectation: {expectation}")

        for concern in stakeholder.concerns:
            print(f"  Concern: {concern}")

    print("\nStep 4: Design communication")

    for stakeholder in scenario_register.stakeholders:
        category = classify_power_interest(
            stakeholder.influence,
            stakeholder.interest,
        )

        if category == EngagementLevel.MANAGE_CLOSELY:
            frequency = "Weekly"
        elif category == EngagementLevel.KEEP_SATISFIED:
            frequency = "Biweekly"
        elif category == EngagementLevel.KEEP_INFORMED:
            frequency = "Biweekly"
        else:
            frequency = "Monthly"

        print(
            f"- {stakeholder.name}: "
            f"{frequency}, "
            f"channels={stakeholder.preferred_channels}"
        )

    print("\nStep 5: Detect high-priority stakeholders")

    ranked = sorted(
        scenario_register.stakeholders,
        key=priority_score,
        reverse=True,
    )

    for stakeholder in ranked:
        print(
            f"- {stakeholder.name}: "
            f"{priority_score(stakeholder):.2f}"
        )

    print("\nStep 6: Monitor changes")

    customer = scenario_register.get("Customer")

    if customer:
        original_interest = customer.interest

        customer.interest = 5
        customer.influence = 5

        print(
            f"Customer influence changed from "
            f"{original_interest} interest baseline to "
            f"influence={customer.influence}, "
            f"interest={customer.interest}."
        )

    print("\nStep 7: Escalate material issues")

    scenario_issue = Issue(
        title="Customer acceptance issue",
        severity=5,
        stakeholder="Customer",
        unresolved_hours=30,
    )

    print(
        f"Issue: {scenario_issue.title}; "
        f"escalation={escalation_required(scenario_issue)}"
    )

    print("\nStep 8: Close the feedback loop")

    scenario_feedback = Feedback(
        stakeholder="Customer",
        topic="Communication transparency",
        rating=2,
        comment="Risk updates need to be more frequent.",
    )

    scenario_feedback.validate()

    print(
        f"Feedback received: "
        f"{scenario_feedback.topic}, "
        f"rating={scenario_feedback.rating}"
    )

    print(
        "\nThe stakeholder management cycle should then be repeated "
        "because stakeholder conditions are dynamic."
    )


run_end_to_end_scenario()


# =============================================================================
# 46. AUTOMATED TESTS
# =============================================================================

def run_tests() -> None:
    """Basic unit-style tests for important stakeholder logic."""

    # Power-interest classification
    assert (
        classify_power_interest(5, 5)
        == EngagementLevel.MANAGE_CLOSELY
    )

    assert (
        classify_power_interest(5, 2)
        == EngagementLevel.KEEP_SATISFIED
    )

    assert (
        classify_power_interest(2, 5)
        == EngagementLevel.KEEP_INFORMED
    )

    assert (
        classify_power_interest(2, 2)
        == EngagementLevel.MONITOR
    )

    # Normalisation
    assert math.isclose(normalize_score(1), 0.0)
    assert math.isclose(normalize_score(3), 0.5)
    assert math.isclose(normalize_score(5), 1.0)

    # Risk
    test_risk = StakeholderRisk(
        "Test",
        "Test risk",
        4,
        5,
        "Mitigate",
    )

    assert test_risk.score() == 20

    # Feedback
    test_feedback = FeedbackLoop()

    test_feedback.add(
        Feedback(
            "Test",
            "Communication",
            4,
            "Good",
        )
    )

    test_feedback.add(
        Feedback(
            "Test",
            "Transparency",
            2,
            "Needs improvement",
        )
    )

    assert math.isclose(
        test_feedback.average_rating(),
        3.0,
    )

    assert "Transparency" in test_feedback.improvement_areas()

    # Network
    test_network = StakeholderNetwork()
    test_network.add_relationship("A", "B")
    test_network.add_relationship("B", "C")

    assert test_network.shortest_path("A", "C") == ["A", "B", "C"]

    # RACI
    valid_raci = RACIEntry(
        task="Test task",
        responsible={"A"},
        accountable={"B"},
        consulted={"C"},
        informed={"D"},
    )

    valid_raci.validate()

    # Stakeholder validation
    valid_stakeholder = Stakeholder(
        "Valid",
        StakeholderType.INTERNAL,
        "Role",
        3,
        3,
        3,
    )

    valid_stakeholder.validate()

    print("\nAll automated tests passed.")


print("\n" + "=" * 80)
print("RUNNING TESTS")
print("=" * 80)

run_tests()


# =============================================================================
# 47. PRACTICAL DECISION FRAMEWORK
# =============================================================================

def stakeholder_decision_framework(
    stakeholder: Stakeholder,
) -> Dict[str, str]:
    """
    Produces a compact operational recommendation.

    This framework combines:
    1. Power-interest position
    2. Priority score
    3. Expectations
    4. Communication preference
    5. Main concerns
    """

    engagement = classify_power_interest(
        stakeholder.influence,
        stakeholder.interest,
    )

    score = priority_score(stakeholder)

    if score >= 4.0:
        attention = "Critical attention"
    elif score >= 3.25:
        attention = "High attention"
    elif score >= 2.5:
        attention = "Moderate attention"
    else:
        attention = "Low attention"

    return {
        "stakeholder": stakeholder.name,
        "type": stakeholder.stakeholder_type.value,
        "engagement": engagement.value,
        "attention": attention,
        "priority_score": f"{score:.2f}",
        "preferred_channels": (
            ", ".join(stakeholder.preferred_channels)
            if stakeholder.preferred_channels
            else "Not specified"
        ),
        "main_expectations": (
            "; ".join(stakeholder.expectations)
            if stakeholder.expectations
            else "Not specified"
        ),
        "main_concerns": (
            "; ".join(stakeholder.concerns)
            if stakeholder.concerns
            else "Not specified"
        ),
    }


print("\nPractical stakeholder decision framework:")

for stakeholder in stakeholders:
    result = stakeholder_decision_framework(stakeholder)

    print(f"\n{result['stakeholder']}")
    for key, value in result.items():
        if key != "stakeholder":
            print(f"  {key}: {value}")


# =============================================================================
# 48. FINAL OPERATIONAL CHECKLIST
# =============================================================================

stakeholder_management_checklist = [
    "Identify all relevant internal stakeholders.",
    "Identify all relevant external stakeholders.",
    "Record stakeholder roles and relationships.",
    "Assess influence and interest.",
    "Assess impact, urgency, legitimacy and proximity where relevant.",
    "Map stakeholders into appropriate categories.",
    "Document expectations and concerns.",
    "Distinguish requirements from assumptions.",
    "Identify conflicts between stakeholder expectations.",
    "Define desired engagement levels.",
    "Create a communication plan.",
    "Match communication channels to stakeholder needs.",
    "Assign communication ownership.",
    "Define decision rights.",
    "Use RACI where responsibility clarity is required.",
    "Track stakeholder-related risks.",
    "Define escalation thresholds.",
    "Collect stakeholder feedback.",
    "Measure communication effectiveness.",
    "Monitor stakeholder sentiment and changes.",
    "Review stakeholder analysis periodically.",
    "Protect sensitive stakeholder information.",
    "Document important decisions and commitments.",
    "Close feedback loops.",
]

print("\n" + "=" * 80)
print("STAKEHOLDER MANAGEMENT CHECKLIST")
print("=" * 80)

for index, item in enumerate(stakeholder_management_checklist, start=1):
    print(f"{index:02d}. {item}")


# =============================================================================
# 49. KEY PRINCIPLES ENCODED AS ASSERTIONS
# =============================================================================

def demonstrate_core_principles() -> None:
    """
    Core principles represented as executable assertions.

    These assertions are educational rules of thumb, not absolute laws.
    """

    # Stakeholder type must be explicit.
    assert StakeholderType.INTERNAL.value == "Internal"
    assert StakeholderType.EXTERNAL.value == "External"

    # High power + high interest deserves close engagement.
    assert (
        classify_power_interest(5, 5)
        == EngagementLevel.MANAGE_CLOSELY
    )

    # High power + low interest requires satisfaction rather than
    # unnecessarily intensive operational communication.
    assert (
        classify_power_interest(5, 2)
        == EngagementLevel.KEEP_SATISFIED
    )

    # Low power + high interest should not be ignored.
    assert (
        classify_power_interest(2, 5)
        == EngagementLevel.KEEP_INFORMED
    )

    # Low power + low interest generally requires monitoring.
    assert (
        classify_power_interest(2, 2)
        == EngagementLevel.MONITOR
    )

    # Risk rises when probability and impact rise.
    low_risk = 1 * 1
    high_risk = 5 * 5

    assert high_risk > low_risk

    print("\nCore principle assertions passed.")


demonstrate_core_principles()


# =============================================================================
# 50. SCRIPT COMPLETION
# =============================================================================

print("\n" + "=" * 80)
print("STAKEHOLDER MANAGEMENT STUDY SCRIPT COMPLETED")
print("=" * 80)
print(
    "The examples above form a complete executable study reference "
    "covering stakeholder identification, analysis, mapping, expectations, "
    "communication, engagement, conflict, risk, governance and monitoring."
)
