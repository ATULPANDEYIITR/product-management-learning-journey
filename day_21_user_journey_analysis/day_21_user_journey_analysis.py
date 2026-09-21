"""
USER JOURNEY ANALYSIS
=====================

Topic:
Touchpoints, pain points, moments of truth, friction, emotions, opportunities

This standalone study script teaches User Journey Analysis from beginner
through advanced level. It combines conceptual explanations with executable
Python examples.

The examples model a digital banking journey, but the analytical techniques
can be reused for e-commerce, healthcare, education, SaaS, government
services, financial services, mobile applications, and other customer-facing
systems.

The script intentionally uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from statistics import mean, median
from typing import Iterable, Optional
import math
import json
import csv
import io


# ============================================================================
# 1. FUNDAMENTAL TERMINOLOGY
# ============================================================================

def explain_fundamentals() -> None:
    print("\n" + "=" * 78)
    print("1. FUNDAMENTAL CONCEPTS")
    print("=" * 78)

    concepts = {
        "User journey": (
            "The sequence of experiences a person has while trying to achieve "
            "a goal with an organization, product, service, or process."
        ),
        "Journey stage": (
            "A meaningful phase of the journey, such as awareness, research, "
            "signup, onboarding, usage, support, or renewal."
        ),
        "Touchpoint": (
            "A specific interaction between the user and the organization, "
            "such as an advertisement, website page, app screen, email, "
            "support call, branch visit, or transaction."
        ),
        "Pain point": (
            "A problem experienced by the user that makes the journey harder, "
            "slower, more expensive, confusing, risky, or unpleasant."
        ),
        "Friction": (
            "Anything that introduces unnecessary effort, delay, uncertainty, "
            "or cognitive load."
        ),
        "Moment of truth": (
            "An interaction where the user's perception, trust, confidence, "
            "or decision can change substantially."
        ),
        "Emotion": (
            "The user's emotional state during a journey interaction, such as "
            "confidence, anxiety, frustration, relief, or satisfaction."
        ),
        "Opportunity": (
            "A plausible improvement area discovered from evidence about "
            "user needs, behavior, pain, friction, or unmet expectations."
        ),
        "Journey map": (
            "A structured representation of stages, actions, touchpoints, "
            "thoughts, emotions, pain points, and opportunities."
        ),
        "Service blueprint": (
            "A deeper operational view connecting the user's journey to "
            "frontstage and backstage organizational processes."
        ),
    }

    for term, definition in concepts.items():
        print(f"\n{term}")
        print(f"  {definition}")


# ============================================================================
# 2. JOURNEY STRUCTURE
# ============================================================================

class JourneyStage(Enum):
    AWARENESS = "Awareness"
    CONSIDERATION = "Consideration"
    SIGNUP = "Signup"
    ONBOARDING = "Onboarding"
    FIRST_USE = "First Use"
    REPEAT_USE = "Repeat Use"
    SUPPORT = "Support"
    RETENTION = "Retention"


class Emotion(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class Touchpoint:
    name: str
    channel: str
    action: str
    effort_minutes: float
    emotion: Emotion
    pain_score: float
    friction_score: float
    importance: float
    moment_of_truth: bool = False
    evidence: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Keep analytical scores within defined boundaries."""
        if self.effort_minutes < 0:
            raise ValueError("Effort cannot be negative.")

        for field_name, value in (
            ("pain_score", self.pain_score),
            ("friction_score", self.friction_score),
            ("importance", self.importance),
        ):
            if not 0 <= value <= 10:
                raise ValueError(f"{field_name} must be between 0 and 10.")


@dataclass
class JourneyStageData:
    stage: JourneyStage
    user_goal: str
    user_actions: list[str]
    touchpoints: list[Touchpoint]
    expectations: list[str]
    opportunities: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.user_goal.strip():
            raise ValueError("A journey stage must have a user goal.")
        for touchpoint in self.touchpoints:
            touchpoint.validate()


@dataclass
class Journey:
    persona: str
    goal: str
    stages: list[JourneyStageData]

    def validate(self) -> None:
        if not self.persona.strip():
            raise ValueError("Persona cannot be empty.")
        if not self.stages:
            raise ValueError("Journey must contain at least one stage.")

        for stage in self.stages:
            stage.validate()


# ============================================================================
# 3. A BASIC USER JOURNEY
# ============================================================================

def build_banking_journey() -> Journey:
    """Create a realistic journey for opening a digital bank account."""

    return Journey(
        persona="First-time digital banking customer",
        goal="Open an account and successfully make the first transaction",
        stages=[
            JourneyStageData(
                stage=JourneyStage.AWARENESS,
                user_goal="Find a trustworthy account with useful features.",
                user_actions=[
                    "Searches for account options",
                    "Reads product information",
                    "Checks fees and eligibility",
                ],
                expectations=[
                    "Clear pricing",
                    "Simple eligibility rules",
                    "Trustworthy organization",
                ],
                touchpoints=[
                    Touchpoint(
                        name="Search result",
                        channel="Search",
                        action="Clicks a product page",
                        effort_minutes=2,
                        emotion=Emotion.POSITIVE,
                        pain_score=2,
                        friction_score=1,
                        importance=5,
                        evidence=["Search click-through data"],
                    ),
                    Touchpoint(
                        name="Pricing page",
                        channel="Website",
                        action="Reviews fees",
                        effort_minutes=5,
                        emotion=Emotion.NEUTRAL,
                        pain_score=5,
                        friction_score=5,
                        importance=7,
                        moment_of_truth=True,
                        evidence=["Users report difficulty finding fee details"],
                    ),
                ],
            ),
            JourneyStageData(
                stage=JourneyStage.CONSIDERATION,
                user_goal="Decide whether the account is suitable.",
                user_actions=[
                    "Compares benefits",
                    "Reads FAQs",
                    "Checks requirements",
                ],
                expectations=[
                    "Accurate information",
                    "Simple comparison",
                    "No hidden conditions",
                ],
                touchpoints=[
                    Touchpoint(
                        name="FAQ",
                        channel="Website",
                        action="Checks eligibility",
                        effort_minutes=7,
                        emotion=Emotion.NEUTRAL,
                        pain_score=4,
                        friction_score=4,
                        importance=6,
                        evidence=["FAQ search logs"],
                    )
                ],
            ),
            JourneyStageData(
                stage=JourneyStage.SIGNUP,
                user_goal="Start an application quickly.",
                user_actions=[
                    "Enters personal information",
                    "Provides contact details",
                    "Accepts terms",
                ],
                expectations=[
                    "Few unnecessary fields",
                    "Progress visibility",
                    "Data privacy",
                ],
                touchpoints=[
                    Touchpoint(
                        name="Signup form",
                        channel="Web application",
                        action="Completes registration",
                        effort_minutes=8,
                        emotion=Emotion.POSITIVE,
                        pain_score=3,
                        friction_score=3,
                        importance=8,
                        evidence=["Form analytics"],
                    )
                ],
            ),
            JourneyStageData(
                stage=JourneyStage.ONBOARDING,
                user_goal="Complete identity verification.",
                user_actions=[
                    "Uploads identity document",
                    "Completes verification",
                    "Waits for confirmation",
                ],
                expectations=[
                    "Fast verification",
                    "Clear instructions",
                    "Confidence that documents are secure",
                ],
                touchpoints=[
                    Touchpoint(
                        name="Identity verification",
                        channel="Mobile app",
                        action="Uploads identity document",
                        effort_minutes=15,
                        emotion=Emotion.NEGATIVE,
                        pain_score=8,
                        friction_score=8,
                        importance=10,
                        moment_of_truth=True,
                        evidence=[
                            "High verification abandonment",
                            "Repeated document-upload attempts",
                        ],
                    )
                ],
            ),
            JourneyStageData(
                stage=JourneyStage.FIRST_USE,
                user_goal="Make the first successful transaction.",
                user_actions=[
                    "Adds money",
                    "Selects recipient",
                    "Confirms transaction",
                ],
                expectations=[
                    "Clear confirmation",
                    "Immediate status",
                    "No unexpected fees",
                ],
                touchpoints=[
                    Touchpoint(
                        name="First transaction",
                        channel="Mobile app",
                        action="Completes transfer",
                        effort_minutes=4,
                        emotion=Emotion.VERY_POSITIVE,
                        pain_score=1,
                        friction_score=1,
                        importance=10,
                        moment_of_truth=True,
                        evidence=["Successful transaction rate"],
                    )
                ],
            ),
            JourneyStageData(
                stage=JourneyStage.SUPPORT,
                user_goal="Resolve problems if something goes wrong.",
                user_actions=[
                    "Opens help",
                    "Searches support articles",
                    "Contacts support if necessary",
                ],
                expectations=[
                    "Fast response",
                    "Accurate information",
                    "Human escalation when needed",
                ],
                touchpoints=[
                    Touchpoint(
                        name="Support chatbot",
                        channel="In-app support",
                        action="Searches for transaction help",
                        effort_minutes=10,
                        emotion=Emotion.NEGATIVE,
                        pain_score=7,
                        friction_score=7,
                        importance=8,
                        moment_of_truth=True,
                        evidence=["Support transcripts"],
                    )
                ],
            ),
        ],
    )


# ============================================================================
# 4. BASIC JOURNEY REPORTING
# ============================================================================

def print_journey_map(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("4. JOURNEY MAP")
    print("=" * 78)

    for number, stage in enumerate(journey.stages, start=1):
        print(f"\n{number}. {stage.stage.value}")
        print(f"   Goal: {stage.user_goal}")
        print("   Actions:")
        for action in stage.user_actions:
            print(f"     - {action}")

        print("   Touchpoints:")
        for touchpoint in stage.touchpoints:
            print(
                f"     - {touchpoint.name} | "
                f"channel={touchpoint.channel} | "
                f"emotion={touchpoint.emotion.name} | "
                f"pain={touchpoint.pain_score}/10 | "
                f"friction={touchpoint.friction_score}/10"
            )


# ============================================================================
# 5. PAIN POINT ANALYSIS
# ============================================================================

def calculate_pain_priority(touchpoint: Touchpoint) -> float:
    """
    A simple prioritization score.

    Pain alone is not enough. A severe problem affecting an insignificant
    interaction may be less urgent than a moderate problem at a critical
    interaction.

    Formula:
        pain × friction × importance / 100
    """
    return (
        touchpoint.pain_score
        * touchpoint.friction_score
        * touchpoint.importance
        / 100
    )


def identify_pain_points(journey: Journey) -> list[tuple[float, str, Touchpoint]]:
    results = []

    for stage in journey.stages:
        for touchpoint in stage.touchpoints:
            score = calculate_pain_priority(touchpoint)
            if touchpoint.pain_score >= 5 or touchpoint.friction_score >= 5:
                results.append((score, stage.stage.value, touchpoint))

    return sorted(results, key=lambda item: item[0], reverse=True)


def print_pain_analysis(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("5. PAIN POINT ANALYSIS")
    print("=" * 78)

    for score, stage_name, touchpoint in identify_pain_points(journey):
        print(
            f"{stage_name:15} | "
            f"{touchpoint.name:25} | "
            f"priority={score:5.2f} | "
            f"pain={touchpoint.pain_score:.1f} | "
            f"friction={touchpoint.friction_score:.1f}"
        )


# ============================================================================
# 6. MOMENTS OF TRUTH
# ============================================================================

def find_moments_of_truth(journey: Journey) -> list[tuple[str, Touchpoint]]:
    moments = []

    for stage in journey.stages:
        for touchpoint in stage.touchpoints:
            if touchpoint.moment_of_truth:
                moments.append((stage.stage.value, touchpoint))

    return moments


def print_moments_of_truth(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("6. MOMENTS OF TRUTH")
    print("=" * 78)

    for stage_name, touchpoint in find_moments_of_truth(journey):
        print(
            f"{stage_name:15} | {touchpoint.name:25} | "
            f"emotion={touchpoint.emotion.name} | "
            f"importance={touchpoint.importance}/10"
        )


# ============================================================================
# 7. EMOTION ANALYSIS
# ============================================================================

def emotion_score(emotion: Emotion) -> int:
    return emotion.value


def calculate_stage_emotion(stage: JourneyStageData) -> float:
    if not stage.touchpoints:
        return 0.0

    return mean(
        emotion_score(touchpoint.emotion)
        for touchpoint in stage.touchpoints
    )


def print_emotional_curve(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("7. EMOTIONAL CURVE")
    print("=" * 78)

    for stage in journey.stages:
        score = calculate_stage_emotion(stage)
        visual = "█" * int((score + 2) * 5)
        print(f"{stage.stage.value:15} | {score:+.2f} | {visual}")


# ============================================================================
# 8. FRICTION ANALYSIS
# ============================================================================

@dataclass
class FrictionAnalysis:
    touchpoint_name: str
    effort_minutes: float
    friction_score: float
    likely_source: str
    recommendation: str


def classify_friction(touchpoint: Touchpoint) -> FrictionAnalysis:
    """
    Friction can arise from several sources. A score does not explain the
    cause by itself, so the analyst must interpret behavioral evidence.
    """
    if touchpoint.effort_minutes >= 12 and touchpoint.friction_score >= 7:
        source = "High effort"
        recommendation = "Reduce steps, repeated input, or waiting."
    elif touchpoint.friction_score >= 7:
        source = "High cognitive or procedural friction"
        recommendation = "Improve instructions, defaults, feedback, and flow."
    elif touchpoint.effort_minutes >= 8:
        source = "Moderate effort"
        recommendation = "Measure whether every required step is necessary."
    else:
        source = "Low observable friction"
        recommendation = "Monitor rather than redesign without evidence."

    return FrictionAnalysis(
        touchpoint_name=touchpoint.name,
        effort_minutes=touchpoint.effort_minutes,
        friction_score=touchpoint.friction_score,
        likely_source=source,
        recommendation=recommendation,
    )


def print_friction_analysis(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("8. FRICTION ANALYSIS")
    print("=" * 78)

    for stage in journey.stages:
        for touchpoint in stage.touchpoints:
            analysis = classify_friction(touchpoint)
            print(
                f"\n{stage.stage.value} / {analysis.touchpoint_name}"
                f"\n  Effort: {analysis.effort_minutes:.1f} minutes"
                f"\n  Friction: {analysis.friction_score:.1f}/10"
                f"\n  Possible source: {analysis.likely_source}"
                f"\n  Action: {analysis.recommendation}"
            )


# ============================================================================
# 9. EXPECTATION GAP
# ============================================================================

def expectation_gap(
    perceived_experience: float,
    expected_experience: float,
) -> float:
    """
    Positive values mean the experience exceeded the expectation.
    Negative values mean it fell below expectation.
    """
    return perceived_experience - expected_experience


def demonstrate_expectation_gaps() -> None:
    print("\n" + "=" * 78)
    print("9. EXPECTATION GAPS")
    print("=" * 78)

    scenarios = [
        ("Fast verification", 9, 8),
        ("Document upload", 4, 8),
        ("First transaction", 9, 8),
        ("Support", 3, 7),
    ]

    for name, perceived, expected in scenarios:
        gap = expectation_gap(perceived, expected)
        print(
            f"{name:22} | expected={expected} | "
            f"perceived={perceived} | gap={gap:+.1f}"
        )


# ============================================================================
# 10. CUSTOMER EFFORT
# ============================================================================

def customer_effort_score(touchpoints: Iterable[Touchpoint]) -> float:
    """
    This simplified metric combines normalized time and friction.

    In production research, effort should usually be measured using validated
    survey instruments or observed behavioral measures rather than assuming
    that minutes alone represent perceived effort.
    """
    points = list(touchpoints)
    if not points:
        return 0.0

    effort_components = []

    for point in points:
        time_component = min(point.effort_minutes / 20, 1.0) * 5
        friction_component = point.friction_score / 10 * 5
        effort_components.append(time_component + friction_component)

    return mean(effort_components)


# ============================================================================
# 11. OPPORTUNITY IDENTIFICATION
# ============================================================================

@dataclass
class Opportunity:
    stage: str
    problem: str
    evidence: list[str]
    user_need: str
    proposed_direction: str
    impact: float
    confidence: float
    effort: float

    @property
    def opportunity_score(self) -> float:
        """
        A simple prioritization model.

        High impact and confidence increase priority.
        High implementation effort decreases priority.

        This is a decision aid, not a substitute for research.
        """
        return self.impact * self.confidence / max(self.effort, 1)


def derive_opportunities(journey: Journey) -> list[Opportunity]:
    opportunities = []

    for stage in journey.stages:
        for touchpoint in stage.touchpoints:
            if touchpoint.pain_score < 5 and touchpoint.friction_score < 5:
                continue

            if touchpoint.name == "Identity verification":
                direction = (
                    "Provide clearer upload guidance, progress feedback, "
                    "validation before submission, and recovery for failed attempts."
                )
                need = "Complete verification with confidence and minimal repetition."
            elif touchpoint.name == "Support chatbot":
                direction = (
                    "Improve intent recognition, show relevant account context, "
                    "and provide a clear human escalation route."
                )
                need = "Resolve problems without repeating the same information."
            elif touchpoint.name == "Pricing page":
                direction = (
                    "Expose important fees and eligibility conditions in a "
                    "plain-language comparison view."
                )
                need = "Understand the real cost before committing."
            else:
                direction = "Investigate the root cause using behavioral evidence."
                need = "Complete the task with less uncertainty and effort."

            opportunities.append(
                Opportunity(
                    stage=stage.stage.value,
                    problem=touchpoint.name,
                    evidence=touchpoint.evidence,
                    user_need=need,
                    proposed_direction=direction,
                    impact=touchpoint.importance,
                    confidence=7.0 if touchpoint.evidence else 4.0,
                    effort=5.0,
                )
            )

    return sorted(
        opportunities,
        key=lambda opportunity: opportunity.opportunity_score,
        reverse=True,
    )


def print_opportunities(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("11. OPPORTUNITY ANALYSIS")
    print("=" * 78)

    for opportunity in derive_opportunities(journey):
        print(f"\n{opportunity.stage} / {opportunity.problem}")
        print(f"  User need: {opportunity.user_need}")
        print(f"  Evidence: {'; '.join(opportunity.evidence)}")
        print(f"  Direction: {opportunity.proposed_direction}")
        print(f"  Priority aid: {opportunity.opportunity_score:.2f}")


# ============================================================================
# 12. ROOT-CAUSE ANALYSIS
# ============================================================================

def five_whys(problem: str, causes: list[str]) -> list[str]:
    """
    The Five Whys technique is a questioning structure for moving from an
    observed problem toward possible underlying causes.

    It should not be treated as proof of causality. The resulting hypotheses
    should be tested against research or operational evidence.
    """
    print("\n" + "=" * 78)
    print("12. FIVE WHYS")
    print("=" * 78)
    print(f"Observed problem: {problem}")

    chain = []
    for index, cause in enumerate(causes[:5], start=1):
        chain.append(cause)
        print(f"Why {index}: {cause}")

    return chain


# ============================================================================
# 13. JOURNEY FUNNEL ANALYSIS
# ============================================================================

@dataclass
class FunnelStage:
    name: str
    users_entering: int
    users_completing: int

    @property
    def completion_rate(self) -> float:
        if self.users_entering <= 0:
            return 0.0
        return self.users_completing / self.users_entering

    @property
    def abandonment_rate(self) -> float:
        return 1.0 - self.completion_rate


def analyze_funnel(stages: list[FunnelStage]) -> None:
    print("\n" + "=" * 78)
    print("13. FUNNEL ANALYSIS")
    print("=" * 78)

    for stage in stages:
        print(
            f"{stage.name:22} | "
            f"entered={stage.users_entering:6} | "
            f"completed={stage.users_completing:6} | "
            f"completion={stage.completion_rate:6.1%} | "
            f"abandonment={stage.abandonment_rate:6.1%}"
        )


# ============================================================================
# 14. COHORT COMPARISON
# ============================================================================

def compare_cohorts() -> None:
    print("\n" + "=" * 78)
    print("14. COHORT COMPARISON")
    print("=" * 78)

    cohorts = {
        "Mobile users": [8, 7, 6, 5, 7],
        "Desktop users": [7, 6, 5, 4, 6],
        "Returning users": [9, 8, 8, 7, 8],
        "First-time users": [5, 4, 3, 6, 4],
    }

    for cohort, scores in cohorts.items():
        print(
            f"{cohort:20} | "
            f"mean={mean(scores):.2f} | "
            f"median={median(scores):.2f} | "
            f"range={min(scores)}-{max(scores)}"
        )


# ============================================================================
# 15. TOUCHPOINT CHANNEL ANALYSIS
# ============================================================================

def analyze_channels(journey: Journey) -> None:
    grouped: dict[str, list[Touchpoint]] = defaultdict(list)

    for stage in journey.stages:
        for touchpoint in stage.touchpoints:
            grouped[touchpoint.channel].append(touchpoint)

    print("\n" + "=" * 78)
    print("15. CHANNEL ANALYSIS")
    print("=" * 78)

    for channel, points in sorted(grouped.items()):
        print(
            f"{channel:20} | "
            f"touchpoints={len(points)} | "
            f"avg friction={mean(p.friction_score for p in points):.2f} | "
            f"avg pain={mean(p.pain_score for p in points):.2f} | "
            f"avg effort={mean(p.effort_minutes for p in points):.2f} min"
        )


# ============================================================================
# 16. SERVICE BLUEPRINT VIEW
# ============================================================================

@dataclass
class BlueprintStep:
    stage: str
    customer_action: str
    frontstage: str
    backstage: str
    support_system: str
    failure_risk: float


def build_blueprint() -> list[BlueprintStep]:
    return [
        BlueprintStep(
            stage="Signup",
            customer_action="Submits registration",
            frontstage="Signup form validates fields",
            backstage="Identity service receives data",
            support_system="Database and validation service",
            failure_risk=3,
        ),
        BlueprintStep(
            stage="Verification",
            customer_action="Uploads identity document",
            frontstage="App displays verification progress",
            backstage="Document processing and verification",
            support_system="Storage, OCR, verification provider",
            failure_risk=8,
        ),
        BlueprintStep(
            stage="Transaction",
            customer_action="Confirms transfer",
            frontstage="App displays transaction status",
            backstage="Payment processing and ledger update",
            support_system="Fraud detection and transaction database",
            failure_risk=6,
        ),
    ]


def print_blueprint(blueprint: list[BlueprintStep]) -> None:
    print("\n" + "=" * 78)
    print("16. SERVICE BLUEPRINT")
    print("=" * 78)

    for step in blueprint:
        print(f"\nStage: {step.stage}")
        print(f"  Customer: {step.customer_action}")
        print(f"  Frontstage: {step.frontstage}")
        print(f"  Backstage: {step.backstage}")
        print(f"  Support: {step.support_system}")
        print(f"  Failure risk: {step.failure_risk}/10")


# ============================================================================
# 17. DATA QUALITY AND EVIDENCE
# ============================================================================

@dataclass
class Evidence:
    source: str
    observation: str
    confidence: float
    sample_size: Optional[int] = None

    def validate(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1.")
        if self.sample_size is not None and self.sample_size < 0:
            raise ValueError("Sample size cannot be negative.")


def demonstrate_evidence_hierarchy() -> None:
    print("\n" + "=" * 78)
    print("17. EVIDENCE QUALITY")
    print("=" * 78)

    evidence = [
        Evidence(
            source="Analytics",
            observation="42% of users abandon verification",
            confidence=0.90,
            sample_size=12000,
        ),
        Evidence(
            source="Interview",
            observation="Users describe document upload as confusing",
            confidence=0.70,
            sample_size=12,
        ),
        Evidence(
            source="Team assumption",
            observation="Users probably dislike the screen",
            confidence=0.20,
        ),
    ]

    for item in evidence:
        item.validate()
        print(
            f"{item.source:18} | confidence={item.confidence:.0%} | "
            f"sample={item.sample_size} | {item.observation}"
        )

    print(
        "\nImportant principle: a journey map should distinguish observed "
        "evidence from assumptions and interpretations."
    )


# ============================================================================
# 18. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("18. EDGE CASES")
    print("=" * 78)

    empty_touchpoints: list[Touchpoint] = []
    print(
        "Empty touchpoint effort:",
        customer_effort_score(empty_touchpoints),
    )

    try:
        invalid_touchpoint = Touchpoint(
            name="Invalid",
            channel="Test",
            action="Test",
            effort_minutes=-1,
            emotion=Emotion.NEUTRAL,
            pain_score=5,
            friction_score=5,
            importance=5,
        )
        invalid_touchpoint.validate()
    except ValueError as error:
        print("Negative effort correctly rejected:", error)

    try:
        invalid_touchpoint = Touchpoint(
            name="Invalid score",
            channel="Test",
            action="Test",
            effort_minutes=1,
            emotion=Emotion.NEUTRAL,
            pain_score=11,
            friction_score=5,
            importance=5,
        )
        invalid_touchpoint.validate()
    except ValueError as error:
        print("Out-of-range score correctly rejected:", error)

    print(
        "\nEdge-case lesson: analytical systems need explicit handling for "
        "missing data, invalid scores, empty journeys, and unusual behavior."
    )


# ============================================================================
# 19. EXPORTING A JOURNEY MAP
# ============================================================================

def journey_to_dict(journey: Journey) -> dict:
    return {
        "persona": journey.persona,
        "goal": journey.goal,
        "stages": [
            {
                "stage": stage.stage.value,
                "user_goal": stage.user_goal,
                "actions": stage.user_actions,
                "expectations": stage.expectations,
                "touchpoints": [
                    {
                        "name": point.name,
                        "channel": point.channel,
                        "action": point.action,
                        "effort_minutes": point.effort_minutes,
                        "emotion": point.emotion.name,
                        "pain_score": point.pain_score,
                        "friction_score": point.friction_score,
                        "importance": point.importance,
                        "moment_of_truth": point.moment_of_truth,
                        "evidence": point.evidence,
                    }
                    for point in stage.touchpoints
                ],
            }
            for stage in journey.stages
        ],
    }


def demonstrate_json_export(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("19. STRUCTURED DATA EXPORT")
    print("=" * 78)

    document = journey_to_dict(journey)
    serialized = json.dumps(document, indent=2)

    print(serialized[:2500])
    if len(serialized) > 2500:
        print("... output shortened for terminal readability ...")


# ============================================================================
# 20. CSV ANALYSIS
# ============================================================================

def demonstrate_csv_processing(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("20. CSV-STYLE JOURNEY DATA PROCESSING")
    print("=" * 78)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "stage",
            "touchpoint",
            "channel",
            "pain",
            "friction",
            "importance",
            "effort_minutes",
        ]
    )

    for stage in journey.stages:
        for point in stage.touchpoints:
            writer.writerow(
                [
                    stage.stage.value,
                    point.name,
                    point.channel,
                    point.pain_score,
                    point.friction_score,
                    point.importance,
                    point.effort_minutes,
                ]
            )

    csv_text = output.getvalue()
    print(csv_text)


# ============================================================================
# 21. QUANTITATIVE PRIORITIZATION
# ============================================================================

def impact_effort_matrix(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("21. IMPACT-EFFORT ANALYSIS")
    print("=" * 78)

    for opportunity in derive_opportunities(journey):
        impact = opportunity.impact
        effort = opportunity.effort

        if impact >= 7 and effort <= 5:
            category = "High impact / lower effort"
        elif impact >= 7:
            category = "High impact / higher effort"
        elif effort <= 5:
            category = "Lower impact / lower effort"
        else:
            category = "Lower impact / higher effort"

        print(
            f"{opportunity.problem:25} | "
            f"impact={impact:.1f} | effort={effort:.1f} | {category}"
        )


# ============================================================================
# 22. EXPERIENCE CONSISTENCY
# ============================================================================

def calculate_experience_variability(journey: Journey) -> float:
    scores = [
        point.friction_score
        for stage in journey.stages
        for point in stage.touchpoints
    ]

    if len(scores) < 2:
        return 0.0

    average = mean(scores)
    variance = mean((score - average) ** 2 for score in scores)
    return math.sqrt(variance)


def demonstrate_variability(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("22. EXPERIENCE VARIABILITY")
    print("=" * 78)

    variability = calculate_experience_variability(journey)
    print(f"Friction standard deviation: {variability:.2f}")

    print(
        "High variability can indicate that some journey stages work well "
        "while others create substantially different experiences."
    )


# ============================================================================
# 23. RESEARCH QUESTIONS
# ============================================================================

def generate_research_questions(journey: Journey) -> list[str]:
    questions = []

    for stage in journey.stages:
        for point in stage.touchpoints:
            if point.pain_score >= 6 or point.friction_score >= 6:
                questions.extend(
                    [
                        f"What causes users to struggle at {point.name}?",
                        f"What information is missing at {point.name}?",
                        f"Which users experience the greatest friction at {point.name}?",
                        f"Where do users abandon the task around {point.name}?",
                        f"Which operational constraints contribute to {point.name}?",
                    ]
                )

    return questions


def print_research_questions(journey: Journey) -> None:
    print("\n" + "=" * 78)
    print("23. RESEARCH QUESTIONS")
    print("=" * 78)

    for question in generate_research_questions(journey):
        print(f"- {question}")


# ============================================================================
# 24. EXPERIMENT DESIGN
# ============================================================================

@dataclass
class Experiment:
    hypothesis: str
    change: str
    primary_metric: str
    guardrail_metric: str
    success_condition: str


def demonstrate_experiment_design() -> None:
    print("\n" + "=" * 78)
    print("24. JOURNEY IMPROVEMENT EXPERIMENT")
    print("=" * 78)

    experiment = Experiment(
        hypothesis=(
            "Clearer document-upload instructions will reduce verification "
            "abandonment."
        ),
        change=(
            "Show accepted formats, examples, immediate validation, and "
            "progress feedback before submission."
        ),
        primary_metric="Verification completion rate",
        guardrail_metric="Verification error rate",
        success_condition=(
            "Completion increases without materially increasing verification errors."
        ),
    )

    print(f"Hypothesis: {experiment.hypothesis}")
    print(f"Change: {experiment.change}")
    print(f"Primary metric: {experiment.primary_metric}")
    print(f"Guardrail: {experiment.guardrail_metric}")
    print(f"Success condition: {experiment.success_condition}")


# ============================================================================
# 25. ADVANCED ANALYTICAL PRINCIPLES
# ============================================================================

def print_advanced_principles() -> None:
    print("\n" + "=" * 78)
    print("25. ADVANCED PRINCIPLES")
    print("=" * 78)

    principles = [
        (
            "Journey maps are models",
            "They simplify reality. A map is not the journey itself."
        ),
        (
            "Evidence before interpretation",
            "Separate what users did from what analysts believe it means."
        ),
        (
            "Segment before averaging",
            "Different personas, channels, geographies, and experience levels "
            "can behave differently."
        ),
        (
            "Analyze transitions",
            "Problems often occur between stages rather than inside a single "
            "touchpoint."
        ),
        (
            "Study backstage causes",
            "A front-end problem can originate in policies, systems, data, "
            "staffing, or operational processes."
        ),
        (
            "Do not equate emotion with usability",
            "A strong emotion may be caused by context, risk, importance, or "
            "expectation rather than interface quality alone."
        ),
        (
            "Measure outcomes",
            "A redesigned touchpoint should be evaluated using behavior, "
            "business outcomes, and user experience measures."
        ),
        (
            "Watch for unintended consequences",
            "Reducing one form of friction can create security, compliance, "
            "fraud, operational, or accessibility problems elsewhere."
        ),
    ]

    for principle, explanation in principles:
        print(f"\n{principle}:")
        print(f"  {explanation}")


# ============================================================================
# 26. COMMON MISTAKES
# ============================================================================

def print_common_mistakes() -> None:
    print("\n" + "=" * 78)
    print("26. COMMON MISTAKES")
    print("=" * 78)

    mistakes = [
        "Mapping the company's internal process instead of the user's experience.",
        "Treating every contact as equally important.",
        "Recording emotions without evidence.",
        "Confusing a symptom with a root cause.",
        "Using averages that hide important user segments.",
        "Assuming the loudest complaint represents every user.",
        "Creating opportunities before identifying the actual problem.",
        "Ignoring offline, human, operational, or policy touchpoints.",
        "Optimizing a single screen while damaging the complete journey.",
        "Measuring satisfaction without measuring task completion.",
        "Treating a journey map as a static document.",
        "Ignoring accessibility and users with different capabilities.",
        "Removing security controls merely to reduce friction.",
        "Using invented precision in scores that are actually subjective.",
    ]

    for mistake in mistakes:
        print(f"- {mistake}")


# ============================================================================
# 27. PRODUCTION-ORIENTED CHECKLIST
# ============================================================================

def print_production_checklist() -> None:
    print("\n" + "=" * 78)
    print("27. PRODUCTION ANALYSIS CHECKLIST")
    print("=" * 78)

    checklist = [
        "Define the user segment.",
        "Define the user's goal.",
        "Define the journey start and end.",
        "Collect behavioral and qualitative evidence.",
        "List stages in the user's language.",
        "Document actions rather than organizational departments.",
        "Identify every meaningful touchpoint.",
        "Record expectations before evaluating the experience.",
        "Record pain points and friction separately.",
        "Identify moments of truth.",
        "Capture emotions with evidence.",
        "Look for stage-to-stage breakdowns.",
        "Investigate operational root causes.",
        "Segment the data.",
        "Prioritize opportunities using explicit criteria.",
        "Define measurable outcome metrics.",
        "Test proposed improvements.",
        "Monitor guardrail metrics.",
        "Update the journey map when evidence changes.",
    ]

    for index, item in enumerate(checklist, start=1):
        print(f"{index:02}. {item}")


# ============================================================================
# 28. MAIN EXECUTION
# ============================================================================

def main() -> None:
    journey = build_banking_journey()
    journey.validate()

    explain_fundamentals()
    print_journey_map(journey)
    print_pain_analysis(journey)
    print_moments_of_truth(journey)
    print_emotional_curve(journey)
    print_friction_analysis(journey)
    demonstrate_expectation_gaps()

    all_touchpoints = [
        point
        for stage in journey.stages
        for point in stage.touchpoints
    ]

    print("\n" + "=" * 78)
    print("10. CUSTOMER EFFORT")
    print("=" * 78)
    print(f"Estimated journey effort index: {customer_effort_score(all_touchpoints):.2f}/10")

    print_opportunities(journey)

    five_whys(
        "Users abandon identity verification.",
        [
            "Some users cannot successfully upload their document.",
            "The interface does not clearly communicate accepted formats.",
            "Validation occurs after the user submits the document.",
            "The system was designed around successful submissions rather than recovery.",
            "Failure-recovery requirements were not sufficiently represented in the original journey.",
        ],
    )

    analyze_funnel(
        [
            FunnelStage("Product page", 10000, 7200),
            FunnelStage("Application start", 7200, 5900),
            FunnelStage("Verification start", 5900, 3400),
            FunnelStage("Verification complete", 3400, 2950),
            FunnelStage("First transaction", 2950, 2400),
        ]
    )

    compare_cohorts()
    analyze_channels(journey)
    print_blueprint(build_blueprint())
    demonstrate_evidence_hierarchy()
    demonstrate_edge_cases()
    demonstrate_json_export(journey)
    demonstrate_csv_processing(journey)
    impact_effort_matrix(journey)
    demonstrate_variability(journey)
    print_research_questions(journey)
    demonstrate_experiment_design()
    print_advanced_principles()
    print_common_mistakes()
    print_production_checklist()

    print("\n" + "=" * 78)
    print("END OF USER JOURNEY ANALYSIS STUDY SCRIPT")
    print("=" * 78)


if __name__ == "__main__":
    main()
