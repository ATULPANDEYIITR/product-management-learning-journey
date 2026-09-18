"""
USER PERSONAS
A comprehensive study and implementation of persona creation, demographics,
behaviors, goals, frustrations, jobs, and motivations.

This script progresses from basic persona concepts to:
- Persona structure and terminology
- Demographic and behavioral attributes
- Goals, frustrations, jobs, motivations
- Evidence quality and assumptions
- Persona creation and validation
- Persona segmentation
- Behavioral scoring
- Jobs-to-be-Done modeling
- Motivation modeling
- Persona comparison
- Scenario simulation
- Data aggregation
- Bias and privacy considerations
- Serialization and reporting
- A realistic product-management case study
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import Counter, defaultdict
from statistics import mean
from typing import Any, Iterable, Optional
import json
import math
import re


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL CONCEPTS
# ---------------------------------------------------------------------------

print("=" * 78)
print("USER PERSONAS: FROM FUNDAMENTALS TO ADVANCED IMPLEMENTATION")
print("=" * 78)

print(
    """
A user persona is a research-informed representation of a meaningful user
segment. A persona describes patterns in users' characteristics, behaviors,
needs, goals, frustrations, jobs, and motivations.

A persona is not simply a fictional biography. Its value comes from the
evidence and behavioral patterns behind it.

Important dimensions include:

1. Demographics
   Age range, location, occupation, education, household context, and other
   attributes when they are relevant to the product.

2. Behaviors
   How users discover, evaluate, use, abandon, return to, and recommend a
   product or service.

3. Goals
   Outcomes users are trying to achieve.

4. Frustrations
   Obstacles, pain points, risks, delays, confusing interactions, and unmet
   needs.

5. Jobs
   The functional, emotional, and social progress a user is trying to make.

6. Motivations
   Forces that explain why a user chooses an action.

A useful persona separates observed evidence from assumptions.
"""
)


# ---------------------------------------------------------------------------
# 2. ENUMERATIONS AND CORE DATA STRUCTURES
# ---------------------------------------------------------------------------

class EvidenceLevel(Enum):
    """Indicates how strongly an attribute is supported by research."""

    OBSERVED = "observed"
    REPORTED = "reported"
    INFERRED = "inferred"
    ASSUMED = "assumed"


class JobType(Enum):
    """Common Jobs-to-be-Done categories."""

    FUNCTIONAL = "functional"
    EMOTIONAL = "emotional"
    SOCIAL = "social"


class MotivationCategory(Enum):
    """Broad motivation categories useful for product research."""

    AUTONOMY = "autonomy"
    MASTERY = "mastery"
    BELONGING = "belonging"
    SECURITY = "security"
    STATUS = "status"
    CONVENIENCE = "convenience"
    ACHIEVEMENT = "achievement"
    CURIOSITY = "curiosity"
    SAVINGS = "savings"


@dataclass
class Evidence:
    """Research evidence attached to an observation or attribute."""

    source: str
    statement: str
    level: EvidenceLevel
    sample_size: Optional[int] = None

    def quality_score(self) -> float:
        """Convert evidence level to a simple strength score."""
        scores = {
            EvidenceLevel.OBSERVED: 1.00,
            EvidenceLevel.REPORTED: 0.85,
            EvidenceLevel.INFERRED: 0.55,
            EvidenceLevel.ASSUMED: 0.20,
        }
        return scores[self.level]


@dataclass
class Job:
    """Represents a job a user is trying to accomplish."""

    description: str
    job_type: JobType
    importance: int
    frequency: int
    current_solution: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.description.strip():
            errors.append("Job description cannot be empty.")
        if not 1 <= self.importance <= 10:
            errors.append("Importance must be between 1 and 10.")
        if not 1 <= self.frequency <= 10:
            errors.append("Frequency must be between 1 and 10.")
        return errors

    def priority_score(self) -> float:
        return self.importance * self.frequency


@dataclass
class Motivation:
    """Represents a force that influences user behavior."""

    category: MotivationCategory
    description: str
    strength: int
    evidence: Optional[Evidence] = None

    def normalized_strength(self) -> float:
        return max(0, min(10, self.strength)) / 10


@dataclass
class Frustration:
    """Represents a pain point or obstacle."""

    description: str
    severity: int
    frequency: int
    current_workaround: str = ""

    def impact_score(self) -> float:
        return self.severity * self.frequency


@dataclass
class Persona:
    """A structured user persona."""

    name: str
    archetype: str
    description: str

    # Demographics should only be included when they help explain behavior.
    age_range: str = ""
    location: str = ""
    occupation: str = ""
    education: str = ""

    behaviors: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    frustrations: list[Frustration] = field(default_factory=list)
    jobs: list[Job] = field(default_factory=list)
    motivations: list[Motivation] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    preferred_channels: list[str] = field(default_factory=list)
    technology_comfort: int = 5
    price_sensitivity: int = 5

    def validate(self) -> list[str]:
        """Check structural and semantic quality of the persona."""
        errors = []

        if not self.name.strip():
            errors.append("Persona name is required.")

        if not self.archetype.strip():
            errors.append("Persona archetype is required.")

        if not self.goals:
            errors.append("A persona should have at least one goal.")

        if not self.jobs:
            errors.append("A persona should have at least one job.")

        if not self.behaviors:
            errors.append("A persona should contain behavioral observations.")

        if not 1 <= self.technology_comfort <= 10:
            errors.append("Technology comfort must be between 1 and 10.")

        if not 1 <= self.price_sensitivity <= 10:
            errors.append("Price sensitivity must be between 1 and 10.")

        for job in self.jobs:
            errors.extend(job.validate())

        return errors

    def goal_count(self) -> int:
        return len(self.goals)

    def frustration_impact(self) -> float:
        return sum(item.impact_score() for item in self.frustrations)

    def job_priority(self) -> float:
        return sum(job.priority_score() for job in self.jobs)

    def motivation_strength(self) -> float:
        if not self.motivations:
            return 0.0
        return mean(m.normalized_strength() for m in self.motivations)

    def evidence_strength(self) -> float:
        if not self.evidence:
            return 0.0
        return mean(e.quality_score() for e in self.evidence)

    def behavior_keywords(self) -> set[str]:
        """Extract simple normalized keywords from behavioral statements."""
        text = " ".join(self.behaviors).lower()
        words = re.findall(r"[a-z]{4,}", text)
        stop_words = {
            "with", "that", "this", "from", "they", "their", "often",
            "when", "into", "uses", "user", "users", "before", "after",
        }
        return {word for word in words if word not in stop_words}

    def summary(self) -> str:
        return (
            f"{self.name} ({self.archetype}): "
            f"{self.occupation or 'occupation not specified'}; "
            f"{len(self.goals)} goals; "
            f"{len(self.jobs)} jobs; "
            f"{len(self.frustrations)} frustrations; "
            f"{len(self.motivations)} motivations."
        )


# ---------------------------------------------------------------------------
# 3. BASIC PERSONA CREATION
# ---------------------------------------------------------------------------

student_persona = Persona(
    name="Aarav",
    archetype="Time-Constrained Learner",
    description=(
        "A learner who needs practical technical knowledge while balancing "
        "academic and professional responsibilities."
    ),
    age_range="20-28",
    location="Urban India",
    occupation="Graduate student / early-career professional",
    education="Undergraduate or postgraduate education",
    behaviors=[
        "Searches for practical explanations before attempting a task.",
        "Compares multiple options before committing to a tool.",
        "Uses a laptop for structured work and a phone for quick research.",
        "Returns to products that reduce repetitive work.",
        "Abandons workflows when instructions are unclear.",
    ],
    goals=[
        "Complete technical tasks accurately.",
        "Learn concepts without wasting time.",
        "Build evidence of practical competence.",
    ],
    frustrations=[
        Frustration(
            "Unclear instructions force repeated searching.",
            severity=8,
            frequency=8,
            current_workaround="Searches several tutorials and forums.",
        ),
        Frustration(
            "Tools with unnecessary complexity slow down simple tasks.",
            severity=7,
            frequency=6,
            current_workaround="Uses simpler alternative tools.",
        ),
    ],
    jobs=[
        Job(
            "Understand a technical concept well enough to apply it.",
            JobType.FUNCTIONAL,
            importance=9,
            frequency=8,
            current_solution="Tutorials, documentation, experimentation.",
        ),
        Job(
            "Feel confident that the result is correct.",
            JobType.EMOTIONAL,
            importance=8,
            frequency=7,
            current_solution="Cross-checks results.",
        ),
    ],
    motivations=[
        Motivation(
            MotivationCategory.MASTERY,
            "Wants demonstrable technical competence.",
            strength=9,
        ),
        Motivation(
            MotivationCategory.CONVENIENCE,
            "Values efficient workflows.",
            strength=8,
        ),
        Motivation(
            MotivationCategory.ACHIEVEMENT,
            "Wants measurable progress toward career goals.",
            strength=8,
        ),
    ],
    evidence=[
        Evidence(
            source="Interview study",
            statement="Participants repeatedly asked for practical examples.",
            level=EvidenceLevel.REPORTED,
            sample_size=18,
        ),
        Evidence(
            source="Usage analytics",
            statement="Long instructions correlate with early abandonment.",
            level=EvidenceLevel.OBSERVED,
            sample_size=1200,
        ),
    ],
    preferred_channels=["Search", "Documentation", "Video", "Community"],
    technology_comfort=8,
    price_sensitivity=7,
)

print("\n--- Basic persona ---")
print(student_persona.summary())
print("Validation:", student_persona.validate())


# ---------------------------------------------------------------------------
# 4. DEMOGRAPHICS: USEFUL BUT NOT SUFFICIENT
# ---------------------------------------------------------------------------

print(
    """
Demographic data describes who a user is in broad measurable terms.
Examples include age range, location, occupation, and education.

Demographics become useful when they help explain a product-relevant
behavior. A demographic attribute should not automatically be treated as a
behavioral prediction.

For example:
    "Age 25-34" is descriptive.
    "Needs mobile-first interaction" is behavioral.
    "Prefers mobile because work happens away from a desk" connects context
    to behavior.

Avoid treating demographic categories as deterministic.
"""
)

demographic_example = {
    "age_range": "25-34",
    "occupation": "Operations analyst",
    "location": "Large metropolitan area",
    "education": "Postgraduate",
}

print("Demographic example:", demographic_example)


# ---------------------------------------------------------------------------
# 5. BEHAVIORAL ATTRIBUTES
# ---------------------------------------------------------------------------

behavior_categories = {
    "discovery": [
        "Search engines",
        "Recommendations",
        "Professional communities",
    ],
    "evaluation": [
        "Compares features",
        "Reads reviews",
        "Tests free version",
    ],
    "usage": [
        "Frequent short sessions",
        "Occasional deep sessions",
        "Keyboard-heavy workflow",
    ],
    "retention": [
        "Returns when the product saves time",
        "Exports data",
        "Builds habitual workflows",
    ],
}

print("\n--- Behavioral dimensions ---")
for category, examples in behavior_categories.items():
    print(f"{category.title()}: {', '.join(examples)}")


# ---------------------------------------------------------------------------
# 6. GOALS
# ---------------------------------------------------------------------------

def classify_goal(goal: str) -> str:
    """Simple rule-based goal classification."""
    text = goal.lower()

    if any(word in text for word in ["learn", "understand", "master"]):
        return "learning"
    if any(word in text for word in ["save", "reduce", "faster", "time"]):
        return "efficiency"
    if any(word in text for word in ["earn", "career", "job", "income"]):
        return "career"
    if any(word in text for word in ["safe", "secure", "risk"]):
        return "security"
    return "general"


print("\n--- Goal classification ---")
for goal in student_persona.goals:
    print(f"{goal} -> {classify_goal(goal)}")


# ---------------------------------------------------------------------------
# 7. FRUSTRATIONS AND PAIN-POINT PRIORITIZATION
# ---------------------------------------------------------------------------

def rank_frustrations(persona: Persona) -> list[Frustration]:
    """Rank pain points by severity multiplied by frequency."""
    return sorted(
        persona.frustrations,
        key=lambda frustration: frustration.impact_score(),
        reverse=True,
    )


print("\n--- Frustration prioritization ---")
for frustration in rank_frustrations(student_persona):
    print(
        f"{frustration.description} | "
        f"impact={frustration.impact_score():.0f}"
    )


# ---------------------------------------------------------------------------
# 8. JOBS-TO-BE-DONE
# ---------------------------------------------------------------------------

print(
    """
Jobs-to-be-Done focuses on the progress a person is trying to make.

Functional job:
    Complete an objective.

Emotional job:
    Achieve a desired internal feeling.

Social job:
    Achieve or maintain a desired social perception.

A job is different from a feature. "Export to PDF" is a feature.
"Produce a shareable report" is a job.
"""
)

jtbd_persona = Persona(
    name="Meera",
    archetype="Decision-Focused Manager",
    description="A manager who needs concise evidence to make operational decisions.",
    occupation="Product manager",
    behaviors=[
        "Reviews dashboards before weekly meetings.",
        "Requests evidence when metrics conflict.",
        "Delegates data preparation but validates key numbers.",
    ],
    goals=[
        "Make decisions using reliable information.",
        "Reduce time spent preparing recurring reports.",
    ],
    jobs=[
        Job(
            "Turn fragmented information into a decision-ready view.",
            JobType.FUNCTIONAL,
            importance=10,
            frequency=8,
        ),
        Job(
            "Feel confident when explaining a decision to stakeholders.",
            JobType.EMOTIONAL,
            importance=9,
            frequency=7,
        ),
        Job(
            "Demonstrate disciplined decision-making to stakeholders.",
            JobType.SOCIAL,
            importance=7,
            frequency=6,
        ),
    ],
    motivations=[
        Motivation(
            MotivationCategory.ACHIEVEMENT,
            "Wants decisions to produce measurable outcomes.",
            9,
        ),
        Motivation(
            MotivationCategory.SECURITY,
            "Wants defensible decisions.",
            8,
        ),
    ],
)

print("\n--- JTBD example ---")
for job in jtbd_persona.jobs:
    print(
        f"[{job.job_type.value}] {job.description} "
        f"| priority={job.priority_score():.0f}"
    )


# ---------------------------------------------------------------------------
# 9. MOTIVATION MODEL
# ---------------------------------------------------------------------------

def rank_motivations(persona: Persona) -> list[Motivation]:
    return sorted(
        persona.motivations,
        key=lambda motivation: motivation.strength,
        reverse=True,
    )


print("\n--- Motivation ranking for analysis ---")
for motivation in rank_motivations(student_persona):
    print(
        f"{motivation.category.value}: "
        f"{motivation.strength}/10 - {motivation.description}"
    )


# ---------------------------------------------------------------------------
# 10. PERSONA QUALITY CHECKS
# ---------------------------------------------------------------------------

def detect_persona_risks(persona: Persona) -> list[str]:
    """
    Detect common persona-quality problems.

    This is intentionally a heuristic tool. It does not determine whether a
    persona is valid; it identifies areas requiring human review.
    """
    risks = []

    if persona.evidence_strength() < 0.5:
        risks.append("Persona has weak or insufficiently documented evidence.")

    if len(persona.evidence) < 2:
        risks.append("Few evidence records are attached.")

    if not persona.frustrations:
        risks.append("No frustrations are documented.")

    if not persona.motivations:
        risks.append("No motivations are documented.")

    if len(persona.demographic_fields()) if False else False:
        pass

    return risks


# ---------------------------------------------------------------------------
# 11. PERSONA COMPARISON
# ---------------------------------------------------------------------------

def compare_personas(
    first: Persona,
    second: Persona,
) -> dict[str, Any]:
    """Return descriptive differences without declaring a universal winner."""
    return {
        "first_name": first.name,
        "second_name": second.name,
        "goal_count": (first.goal_count(), second.goal_count()),
        "job_priority": (first.job_priority(), second.job_priority()),
        "frustration_impact": (
            first.frustration_impact(),
            second.frustration_impact(),
        ),
        "motivation_strength": (
            round(first.motivation_strength(), 3),
            round(second.motivation_strength(), 3),
        ),
        "technology_comfort": (
            first.technology_comfort,
            second.technology_comfort,
        ),
        "price_sensitivity": (
            first.price_sensitivity,
            second.price_sensitivity,
        ),
    }


print("\n--- Persona comparison ---")
print(json.dumps(compare_personas(student_persona, jtbd_persona), indent=2))


# ---------------------------------------------------------------------------
# 12. BEHAVIORAL SIMILARITY
# ---------------------------------------------------------------------------

def jaccard_similarity(first: set[str], second: set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    union = first | second
    if not union:
        return 1.0
    return len(first & second) / len(union)


def persona_behavior_similarity(first: Persona, second: Persona) -> float:
    return jaccard_similarity(
        first.behavior_keywords(),
        second.behavior_keywords(),
    )


print("\nBehavioral keyword similarity:")
print(
    f"{student_persona.name} vs {jtbd_persona.name}: "
    f"{persona_behavior_similarity(student_persona, jtbd_persona):.3f}"
)


# ---------------------------------------------------------------------------
# 13. SEGMENTATION
# ---------------------------------------------------------------------------

@dataclass
class UserObservation:
    """Raw research observation used before persona synthesis."""

    user_id: str
    behaviors: set[str]
    goals: set[str]
    frustration_tags: set[str]
    technology_comfort: int
    price_sensitivity: int


observations = [
    UserObservation(
        "U001",
        {"search", "compare", "documentation"},
        {"learn", "complete_task"},
        {"complexity"},
        9,
        7,
    ),
    UserObservation(
        "U002",
        {"search", "documentation"},
        {"learn"},
        {"unclear_instructions"},
        8,
        8,
    ),
    UserObservation(
        "U003",
        {"dashboard", "reporting", "compare"},
        {"decision", "save_time"},
        {"fragmented_data"},
        7,
        5,
    ),
    UserObservation(
        "U004",
        {"search", "compare", "documentation"},
        {"learn", "complete_task"},
        {"complexity"},
        9,
        6,
    ),
]


def simple_behavior_segment(observation: UserObservation) -> str:
    """
    Demonstrates transparent rule-based segmentation.

    Production segmentation can use statistical clustering, but the result
    should still be interpreted in product and research context.
    """
    if "dashboard" in observation.behaviors or "decision" in observation.goals:
        return "decision_oriented"
    if "learn" in observation.goals:
        return "learning_oriented"
    return "other"


segment_counts = Counter(
    simple_behavior_segment(observation)
    for observation in observations
)

print("\n--- Segment distribution ---")
for segment, count in segment_counts.items():
    print(segment, count)


# ---------------------------------------------------------------------------
# 14. AGGREGATING RESEARCH OBSERVATIONS
# ---------------------------------------------------------------------------

def aggregate_observations(
    records: Iterable[UserObservation],
) -> dict[str, Any]:
    records = list(records)

    behavior_frequency = Counter(
        behavior
        for record in records
        for behavior in record.behaviors
    )

    goal_frequency = Counter(
        goal
        for record in records
        for goal in record.goals
    )

    frustration_frequency = Counter(
        frustration
        for record in records
        for frustration in record.frustration_tags
    )

    return {
        "user_count": len(records),
        "common_behaviors": behavior_frequency.most_common(),
        "common_goals": goal_frequency.most_common(),
        "common_frustrations": frustration_frequency.most_common(),
        "average_technology_comfort": (
            mean(record.technology_comfort for record in records)
            if records else 0
        ),
        "average_price_sensitivity": (
            mean(record.price_sensitivity for record in records)
            if records else 0
        ),
    }


print("\n--- Research aggregation ---")
print(json.dumps(aggregate_observations(observations), indent=2))


# ---------------------------------------------------------------------------
# 15. FROM RAW RESEARCH TO PERSONA
# ---------------------------------------------------------------------------

def synthesize_persona(
    name: str,
    archetype: str,
    records: list[UserObservation],
) -> Persona:
    """
    Build a transparent persona from observations.

    This implementation deliberately does not invent demographics. It uses
    only behavioral evidence supplied in the observations.
    """
    if not records:
        raise ValueError("At least one research observation is required.")

    aggregate = aggregate_observations(records)

    behaviors = [
        behavior
        for behavior, count in aggregate["common_behaviors"]
        if count >= max(1, len(records) // 2)
    ]

    goals = [
        goal
        for goal, count in aggregate["common_goals"]
        if count >= max(1, len(records) // 2)
    ]

    frustrations = [
        Frustration(
            description=tag.replace("_", " ").capitalize(),
            severity=min(10, count * 3),
            frequency=min(10, count * 3),
        )
        for tag, count in aggregate["common_frustrations"]
    ]

    evidence = [
        Evidence(
            source="Aggregated research observations",
            statement=f"{len(records)} observations contributed to this persona.",
            level=EvidenceLevel.OBSERVED,
            sample_size=len(records),
        )
    ]

    return Persona(
        name=name,
        archetype=archetype,
        description="Research-derived behavioral segment.",
        behaviors=behaviors,
        goals=goals,
        frustrations=frustrations,
        jobs=[
            Job(
                description="Complete the recurring tasks represented in research.",
                job_type=JobType.FUNCTIONAL,
                importance=8,
                frequency=7,
            )
        ],
        motivations=[
            Motivation(
                category=MotivationCategory.CONVENIENCE,
                description="Reduce friction in recurring work.",
                strength=7,
                evidence=evidence[0],
            )
        ],
        evidence=evidence,
        technology_comfort=round(
            mean(record.technology_comfort for record in records)
        ),
        price_sensitivity=round(
            mean(record.price_sensitivity for record in records)
        ),
    )


research_persona = synthesize_persona(
    "Research-Derived Learner",
    "Evidence-Based Learning Segment",
    [observations[0], observations[1], observations[3]],
)

print("\n--- Synthesized persona ---")
print(research_persona.summary())


# ---------------------------------------------------------------------------
# 16. PERSONA SCENARIO SIMULATION
# ---------------------------------------------------------------------------

@dataclass
class ProductFeature:
    name: str
    solves_jobs: list[str]
    reduces_frustrations: list[str]
    supports_goals: list[str]


features = [
    ProductFeature(
        name="Guided workflow",
        solves_jobs=["understand", "complete"],
        reduces_frustrations=["unclear instructions"],
        supports_goals=["learn"],
    ),
    ProductFeature(
        name="Saved workspace",
        solves_jobs=["repeat", "organize"],
        reduces_frustrations=["repetitive work"],
        supports_goals=["save time"],
    ),
    ProductFeature(
        name="Evidence panel",
        solves_jobs=["verify"],
        reduces_frustrations=["uncertainty"],
        supports_goals=["confidence"],
    ),
]


def feature_relevance(persona: Persona, feature: ProductFeature) -> float:
    """
    Heuristic relevance model.

    It is not a substitute for user research. It simply demonstrates how
    persona attributes can be translated into explicit product hypotheses.
    """
    persona_text = " ".join(
        persona.goals
        + persona.behaviors
        + [f.description for f in persona.frustrations]
        + [j.description for j in persona.jobs]
    ).lower()

    matched_terms = 0

    for phrase in (
        feature.solves_jobs
        + feature.reduces_frustrations
        + feature.supports_goals
    ):
        if phrase.lower() in persona_text:
            matched_terms += 1

    return matched_terms / max(
        1,
        len(
            feature.solves_jobs
            + feature.reduces_frustrations
            + feature.supports_goals
        ),
    )


print("\n--- Feature/persona relevance hypotheses ---")
for feature in features:
    print(
        f"{feature.name}: "
        f"{feature_relevance(student_persona, feature):.2f}"
    )


# ---------------------------------------------------------------------------
# 17. PERSONA-BASED SCENARIO
# ---------------------------------------------------------------------------

def simulate_scenario(
    persona: Persona,
    scenario: str,
    available_features: list[ProductFeature],
) -> dict[str, Any]:
    relevant = [
        {
            "feature": feature.name,
            "relevance": round(feature_relevance(persona, feature), 3),
        }
        for feature in available_features
    ]

    relevant.sort(key=lambda item: item["relevance"], reverse=True)

    return {
        "persona": persona.name,
        "scenario": scenario,
        "likely_goals": persona.goals,
        "major_frustrations": [
            item.description for item in rank_frustrations(persona)
        ],
        "feature_hypotheses": relevant,
    }


scenario = simulate_scenario(
    student_persona,
    "The user needs to complete a technical task under time pressure.",
    features,
)

print("\n--- Scenario simulation ---")
print(json.dumps(scenario, indent=2))


# ---------------------------------------------------------------------------
# 18. PERSONA CANVAS GENERATION
# ---------------------------------------------------------------------------

def render_persona_canvas(persona: Persona) -> str:
    """Create a compact text report suitable for documentation."""
    lines = [
        f"PERSONA: {persona.name}",
        f"Archetype: {persona.archetype}",
        f"Description: {persona.description}",
        "",
        "DEMOGRAPHICS",
        f"- Age: {persona.age_range or 'Not specified'}",
        f"- Location: {persona.location or 'Not specified'}",
        f"- Occupation: {persona.occupation or 'Not specified'}",
        f"- Education: {persona.education or 'Not specified'}",
        "",
        "BEHAVIORS",
    ]

    lines.extend(f"- {item}" for item in persona.behaviors)

    lines.append("")
    lines.append("GOALS")
    lines.extend(f"- {item}" for item in persona.goals)

    lines.append("")
    lines.append("FRUSTRATIONS")
    lines.extend(
        f"- {item.description} "
        f"(severity={item.severity}, frequency={item.frequency})"
        for item in persona.frustrations
    )

    lines.append("")
    lines.append("JOBS")
    lines.extend(
        f"- [{item.job_type.value}] {item.description}"
        for item in persona.jobs
    )

    lines.append("")
    lines.append("MOTIVATIONS")
    lines.extend(
        f"- [{item.category.value}] {item.description} "
        f"(strength={item.strength}/10)"
        for item in persona.motivations
    )

    return "\n".join(lines)


print("\n--- Persona canvas ---")
print(render_persona_canvas(student_persona))


# ---------------------------------------------------------------------------
# 19. JSON SERIALIZATION
# ---------------------------------------------------------------------------

def enum_to_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [enum_to_value(item) for item in value]
    if isinstance(value, dict):
        return {key: enum_to_value(item) for key, item in value.items()}
    return value


def persona_to_json(persona: Persona) -> str:
    """Serialize a persona without requiring external packages."""
    raw = asdict(persona)
    return json.dumps(enum_to_value(raw), indent=2)


serialized = persona_to_json(student_persona)

print("\n--- JSON serialization preview ---")
print(serialized[:1200] + "\n...")


# ---------------------------------------------------------------------------
# 20. DESERIALIZATION
# ---------------------------------------------------------------------------

def persona_from_dict(data: dict[str, Any]) -> Persona:
    """Reconstruct a Persona from a compatible dictionary."""
    frustrations = [
        Frustration(**item)
        for item in data.get("frustrations", [])
    ]

    jobs = [
        Job(
            description=item["description"],
            job_type=JobType(item["job_type"]),
            importance=item["importance"],
            frequency=item["frequency"],
            current_solution=item.get("current_solution", ""),
        )
        for item in data.get("jobs", [])
    ]

    motivations = [
        Motivation(
            category=MotivationCategory(item["category"]),
            description=item["description"],
            strength=item["strength"],
        )
        for item in data.get("motivations", [])
    ]

    evidence = [
        Evidence(
            source=item["source"],
            statement=item["statement"],
            level=EvidenceLevel(item["level"]),
            sample_size=item.get("sample_size"),
        )
        for item in data.get("evidence", [])
    ]

    allowed = {
        "name",
        "archetype",
        "description",
        "age_range",
        "location",
        "occupation",
        "education",
        "behaviors",
        "goals",
        "preferred_channels",
        "technology_comfort",
        "price_sensitivity",
    }

    fields = {key: data[key] for key in allowed if key in data}

    return Persona(
        **fields,
        frustrations=frustrations,
        jobs=jobs,
        motivations=motivations,
        evidence=evidence,
    )


restored_persona = persona_from_dict(json.loads(serialized))

print("\nRestored persona:")
print(restored_persona.summary())


# ---------------------------------------------------------------------------
# 21. DATA QUALITY AND ASSUMPTION DETECTION
# ---------------------------------------------------------------------------

def identify_assumptions(persona: Persona) -> list[str]:
    """
    Identify attributes that should be reviewed before research use.

    The function cannot determine truth. It highlights statements whose
    evidence level indicates uncertainty.
    """
    assumptions = []

    for evidence in persona.evidence:
        if evidence.level in {EvidenceLevel.INFERRED, EvidenceLevel.ASSUMED}:
            assumptions.append(evidence.statement)

    for motivation in persona.motivations:
        if motivation.evidence and motivation.evidence.level in {
            EvidenceLevel.INFERRED,
            EvidenceLevel.ASSUMED,
        }:
            assumptions.append(motivation.description)

    return assumptions


print("\n--- Assumption review ---")
print(identify_assumptions(student_persona))


# ---------------------------------------------------------------------------
# 22. EDGE CASES
# ---------------------------------------------------------------------------

print("\n--- Edge cases ---")

empty_persona = Persona(
    name="",
    archetype="",
    description="",
)

print("Empty persona validation:")
for error in empty_persona.validate():
    print("  -", error)

empty_jobs: list[Job] = []
print("Empty job priority:", sum(job.priority_score() for job in empty_jobs))

print(
    "Jaccard similarity of two empty sets:",
    jaccard_similarity(set(), set()),
)


# ---------------------------------------------------------------------------
# 23. PRIVACY AND ETHICAL DESIGN
# ---------------------------------------------------------------------------

print(
    """
Persona research should minimize unnecessary personal data.

Important practices:
- Collect only attributes relevant to the research question.
- Prefer ranges over exact values when exact values are unnecessary.
- Avoid storing sensitive personal information merely to make personas vivid.
- Separate research evidence from fictional narrative details.
- Do not treat demographic categories as deterministic predictors.
- Document uncertainty.
- Protect raw research data.
- Use aggregated patterns where individual identification is unnecessary.
- Review whether an attribute could create unfair treatment or exclusion.
- Do not fabricate quotations or research findings.
"""
)


# ---------------------------------------------------------------------------
# 24. ADVANCED PERSONA GOVERNANCE
# ---------------------------------------------------------------------------

@dataclass
class PersonaVersion:
    """Tracks persona evolution over time."""

    version: str
    created_at: str
    evidence_count: int
    change_reason: str


persona_history = [
    PersonaVersion(
        version="1.0",
        created_at="2026-01-10",
        evidence_count=12,
        change_reason="Initial behavioral synthesis",
    ),
    PersonaVersion(
        version="1.1",
        created_at="2026-04-22",
        evidence_count=27,
        change_reason="Updated recurring workflow observations",
    ),
    PersonaVersion(
        version="2.0",
        created_at="2026-08-30",
        evidence_count=51,
        change_reason="Segment definition revised after additional research",
    ),
]

print("\n--- Persona governance history ---")
for version in persona_history:
    print(
        version.version,
        version.created_at,
        version.evidence_count,
        version.change_reason,
    )


# ---------------------------------------------------------------------------
# 25. INDUSTRY-STYLE PRODUCT CASE STUDY
# ---------------------------------------------------------------------------

print("\n" + "=" * 78)
print("CASE STUDY: RESEARCHING A DIGITAL LEARNING PLATFORM")
print("=" * 78)

case_records = [
    UserObservation(
        "L001",
        {"search", "compare", "practice"},
        {"learn", "complete_task"},
        {"unclear_instructions", "time"},
        9,
        8,
    ),
    UserObservation(
        "L002",
        {"search", "practice", "documentation"},
        {"learn", "career"},
        {"time", "complexity"},
        8,
        9,
    ),
    UserObservation(
        "L003",
        {"search", "compare", "practice"},
        {"learn", "career"},
        {"complexity"},
        9,
        7,
    ),
    UserObservation(
        "L004",
        {"search", "documentation", "practice"},
        {"learn", "complete_task"},
        {"unclear_instructions"},
        8,
        8,
    ),
    UserObservation(
        "L005",
        {"compare", "practice", "community"},
        {"career", "learn"},
        {"price", "time"},
        7,
        9,
    ),
]

learning_persona = synthesize_persona(
    "Practical Career Learner",
    "Evidence-Based Skill Builder",
    case_records,
)

learning_persona.jobs.extend(
    [
        Job(
            "Build practical evidence that a learned skill can be applied.",
            JobType.FUNCTIONAL,
            importance=9,
            frequency=8,
        ),
        Job(
            "Feel prepared when facing a real technical task.",
            JobType.EMOTIONAL,
            importance=8,
            frequency=7,
        ),
    ]
)

learning_persona.motivations.extend(
    [
        Motivation(
            MotivationCategory.MASTERY,
            "Wants to convert theory into usable competence.",
            10,
        ),
        Motivation(
            MotivationCategory.ACHIEVEMENT,
            "Wants visible progress toward career objectives.",
            9,
        ),
        Motivation(
            MotivationCategory.CONVENIENCE,
            "Values efficient learning workflows.",
            8,
        ),
    ]
)

print(render_persona_canvas(learning_persona))


# ---------------------------------------------------------------------------
# 26. REQUIREMENT TRANSLATION
# ---------------------------------------------------------------------------

def persona_to_product_hypotheses(persona: Persona) -> list[str]:
    """
    Convert persona evidence into testable product hypotheses.

    These are hypotheses, not proven requirements.
    """
    hypotheses = []

    for frustration in persona.frustrations:
        hypotheses.append(
            f"If the product reduces '{frustration.description.lower()}', "
            f"task completion should improve for this segment."
        )

    for goal in persona.goals:
        hypotheses.append(
            f"A workflow supporting '{goal.lower()}' should be evaluated "
            f"with this segment."
        )

    return hypotheses


print("\n--- Product hypotheses ---")
for hypothesis in persona_to_product_hypotheses(learning_persona):
    print("-", hypothesis)


# ---------------------------------------------------------------------------
# 27. PERSONA SUCCESS METRICS
# ---------------------------------------------------------------------------

@dataclass
class PersonaMetric:
    """Metric used to test whether a persona-based product hypothesis holds."""

    name: str
    definition: str
    desired_direction: str


metrics = [
    PersonaMetric(
        "Task completion rate",
        "Percentage of users completing the target workflow.",
        "increase",
    ),
    PersonaMetric(
        "Time to completion",
        "Elapsed time from workflow start to successful completion.",
        "decrease",
    ),
    PersonaMetric(
        "Repeat usage",
        "Percentage returning for the same relevant workflow.",
        "increase",
    ),
    PersonaMetric(
        "Error rate",
        "Percentage of workflows containing a meaningful user error.",
        "decrease",
    ),
]

print("\n--- Metrics for persona hypotheses ---")
for metric in metrics:
    print(
        f"{metric.name}: {metric.definition} "
        f"({metric.desired_direction})"
    )


# ---------------------------------------------------------------------------
# 28. ADVANCED TRADE-OFF: PERSONA DETAIL VS USABILITY
# ---------------------------------------------------------------------------

def persona_detail_score(persona: Persona) -> dict[str, float]:
    """
    Illustrate a documentation trade-off.

    More fields do not automatically mean better personas. Excessive detail
    can distract teams from behaviorally important information.
    """
    field_count = len(
        [
            value
            for value in [
                persona.age_range,
                persona.location,
                persona.occupation,
                persona.education,
            ]
            if value
        ]
    )

    behavioral_count = (
        len(persona.behaviors)
        + len(persona.goals)
        + len(persona.frustrations)
        + len(persona.jobs)
        + len(persona.motivations)
    )

    return {
        "demographic_detail": float(field_count),
        "behavioral_detail": float(behavioral_count),
        "evidence_strength": persona.evidence_strength(),
    }


print("\n--- Persona detail analysis ---")
print(persona_detail_score(learning_persona))


# ---------------------------------------------------------------------------
# 29. FINAL VALIDATION
# ---------------------------------------------------------------------------

def validate_research_persona(persona: Persona) -> dict[str, Any]:
    """Produce a structured quality report."""
    validation_errors = persona.validate()
    assumptions = identify_assumptions(persona)

    return {
        "valid_structure": not validation_errors,
        "errors": validation_errors,
        "evidence_strength": round(persona.evidence_strength(), 3),
        "assumption_count": len(assumptions),
        "goal_count": len(persona.goals),
        "job_count": len(persona.jobs),
        "frustration_count": len(persona.frustrations),
        "motivation_count": len(persona.motivations),
        "behavior_count": len(persona.behaviors),
    }


print("\n--- Final validation ---")
print(json.dumps(validate_research_persona(learning_persona), indent=2))

print("\n" + "=" * 78)
print("END OF USER PERSONA STUDY")
print("=" * 78)
