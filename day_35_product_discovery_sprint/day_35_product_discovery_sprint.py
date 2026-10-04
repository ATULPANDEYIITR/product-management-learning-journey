"""
Product Discovery Sprint
------------------------
A self-contained product discovery sprint simulator.

The implementation models a realistic product team investigating a problem,
turning research evidence into opportunity themes, generating hypotheses and
solutions, and validating the strongest concepts before committing engineering
capacity.

The script deliberately separates:
- Discovery planning: scope, questions, participants, evidence plan, timeboxes.
- Research: interviews, observation, survey evidence, behavioral signals.
- Synthesis: coding observations, clustering evidence, identifying patterns.
- Ideation: opportunity statements, concepts, prioritization.
- Validation: experiments, evidence thresholds, decisions, and learning.

Run:
    python product_discovery_sprint.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from statistics import mean
from typing import Dict, Iterable, List, Sequence, Tuple
import math
import random
import re


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

class EvidenceType(Enum):
    INTERVIEW = "interview"
    OBSERVATION = "observation"
    SURVEY = "survey"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    EXPERIMENT = "experiment"


class ResearchConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExperimentType(Enum):
    PROTOTYPE = "prototype"
    CONCEPT_TEST = "concept_test"
    USABILITY = "usability"
    FAKE_DOOR = "fake_door"


class Decision(Enum):
    CONTINUE = "continue"
    ITERATE = "iterate"
    STOP = "stop"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class SprintPlan:
    product_area: str
    target_segment: str
    business_outcome: str
    sprint_days: int
    research_questions: Tuple[str, ...]
    constraints: Tuple[str, ...]
    success_criteria: Tuple[str, ...]


@dataclass
class Participant:
    participant_id: str
    segment: str
    role: str
    frequency: str
    context: str


@dataclass
class ResearchObservation:
    observation_id: str
    source_id: str
    evidence_type: EvidenceType
    participant_id: str | None
    text: str
    severity: float
    frequency: int
    confidence: ResearchConfidence = ResearchConfidence.MEDIUM
    tags: set[str] = field(default_factory=set)

    @property
    def weighted_signal(self) -> float:
        confidence_weight = {
            ResearchConfidence.LOW: 0.7,
            ResearchConfidence.MEDIUM: 1.0,
            ResearchConfidence.HIGH: 1.3,
        }[self.confidence]
        return self.severity * math.log1p(self.frequency) * confidence_weight


@dataclass
class Theme:
    theme_id: str
    name: str
    description: str
    evidence_ids: List[str]
    user_impact: float
    frequency: float
    strategic_fit: float

    @property
    def opportunity_score(self) -> float:
        return round(
            (self.user_impact * 0.40)
            + (self.frequency * 0.30)
            + (self.strategic_fit * 0.30),
            2,
        )


@dataclass
class Opportunity:
    opportunity_id: str
    theme_id: str
    statement: str
    target_behavior: str
    evidence_strength: float
    business_value: float
    feasibility: float

    @property
    def opportunity_score(self) -> float:
        return round(
            (self.evidence_strength * 0.40)
            + (self.business_value * 0.35)
            + (self.feasibility * 0.25),
            2,
        )


@dataclass
class Concept:
    concept_id: str
    opportunity_id: str
    name: str
    mechanism: str
    expected_behavior_change: str
    confidence: float
    effort: float
    reach: float

    @property
    def desirability_score(self) -> float:
        return round(
            self.confidence * self.reach * (1.0 / max(self.effort, 1.0)),
            2,
        )


@dataclass
class Experiment:
    experiment_id: str
    concept_id: str
    experiment_type: ExperimentType
    participants: int
    success_metric: str
    baseline: float
    observed: float
    threshold: float
    qualitative_signal: float
    decision: Decision | None = None
    notes: str = ""

    @property
    def quantitative_lift(self) -> float:
        if self.baseline == 0:
            return 0.0
        return (self.observed - self.baseline) / self.baseline

    def evaluate(self) -> Decision:
        quantitative_pass = self.observed >= self.threshold
        qualitative_pass = self.qualitative_signal >= 0.65

        if quantitative_pass and qualitative_pass:
            self.decision = Decision.CONTINUE
        elif quantitative_pass or qualitative_pass:
            self.decision = Decision.ITERATE
        else:
            self.decision = Decision.STOP

        return self.decision


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------

def build_sprint_plan() -> SprintPlan:
    """Create a discovery plan with questions that can actually be researched."""
    return SprintPlan(
        product_area="B2B procurement workflow",
        target_segment="Procurement managers at mid-sized manufacturers",
        business_outcome="Reduce time spent identifying and comparing qualified suppliers",
        sprint_days=10,
        research_questions=(
            "Where does supplier discovery break down during an active procurement request?",
            "Which information is missing when procurement teams compare suppliers?",
            "Which workarounds do procurement managers use to compensate for missing information?",
            "What evidence would make a procurement manager trust a supplier recommendation?",
            "Which part of the workflow is sufficiently painful to justify product intervention?",
        ),
        constraints=(
            "No production system changes during discovery",
            "Use anonymized research data",
            "Validate the problem before validating a solution",
            "Do not treat participant preference as proof of future behavior",
        ),
        success_criteria=(
            "At least three independent evidence sources support the highest-priority problem",
            "The team can describe the target behavior without prescribing a solution",
            "At least two concepts can be tested with low-fidelity prototypes",
            "Validation produces a measurable decision rather than a preference vote",
        ),
    )


def create_research_calendar(plan: SprintPlan) -> Dict[int, List[str]]:
    """Represent a practical sprint cadence rather than a generic task list."""
    if plan.sprint_days < 5:
        raise ValueError("A discovery sprint needs enough time for research and synthesis.")

    calendar = {
        1: ["Align outcome", "Map assumptions", "Finalize research questions"],
        2: ["Recruit participants", "Prepare interview guide", "Audit existing evidence"],
        3: ["Interview procurement managers", "Observe supplier-search workflow"],
        4: ["Continue interviews", "Review behavioral and support evidence"],
        5: ["Code evidence", "Cluster observations", "Identify tensions"],
        6: ["Form opportunity statements", "Prioritize opportunities"],
        7: ["Generate solution concepts", "Select validation candidates"],
        8: ["Run concept and usability tests"],
        9: ["Analyze experiment evidence", "Update assumptions"],
        10: ["Make validation decisions", "Document evidence and unresolved risks"],
    }

    return {day: activities for day, activities in calendar.items() if day <= plan.sprint_days}


# ---------------------------------------------------------------------------
# Research collection
# ---------------------------------------------------------------------------

def create_participants() -> List[Participant]:
    """Create varied research participants so evidence is not sourced from one persona."""
    return [
        Participant(
            "P-001",
            "strategic procurement",
            "procurement manager",
            "weekly",
            "compares multiple suppliers for high-value purchases",
        ),
        Participant(
            "P-002",
            "operational procurement",
            "buyer",
            "daily",
            "handles recurring purchases under time pressure",
        ),
        Participant(
            "P-003",
            "strategic procurement",
            "category manager",
            "monthly",
            "evaluates suppliers against compliance requirements",
        ),
        Participant(
            "P-004",
            "operational procurement",
            "senior buyer",
            "daily",
            "switches between spreadsheets, email, supplier portals, and ERP",
        ),
        Participant(
            "P-005",
            "strategic procurement",
            "procurement lead",
            "weekly",
            "reviews supplier shortlists produced by team members",
        ),
    ]


def collect_research_observations() -> List[ResearchObservation]:
    """
    Produce realistic mixed-method evidence.

    The observations are intentionally not all positive or negative. Discovery
    requires contradictory evidence to expose assumptions and segment differences.
    """
    return [
        ResearchObservation(
            "OBS-001", "INT-001", EvidenceType.INTERVIEW, "P-001",
            "I search three supplier portals before I trust that I have seen the market.",
            0.82, 4, ResearchConfidence.HIGH,
            {"search", "coverage", "trust"},
        ),
        ResearchObservation(
            "OBS-002", "INT-001", EvidenceType.INTERVIEW, "P-001",
            "The supplier page often tells me what the supplier wants me to know, not what I need to compare.",
            0.88, 3, ResearchConfidence.HIGH,
            {"comparison", "information", "trust"},
        ),
        ResearchObservation(
            "OBS-003", "OBS-001", EvidenceType.OBSERVATION, "P-001",
            "Buyer copies lead time, minimum order quantity, certification, and price into a spreadsheet.",
            0.91, 5, ResearchConfidence.HIGH,
            {"spreadsheet", "comparison", "manual_work"},
        ),
        ResearchObservation(
            "OBS-004", "INT-002", EvidenceType.INTERVIEW, "P-002",
            "For recurring purchases I usually call suppliers I already know because researching new ones takes too long.",
            0.79, 4, ResearchConfidence.HIGH,
            {"existing_supplier", "time", "discovery"},
        ),
        ResearchObservation(
            "OBS-005", "INT-003", EvidenceType.INTERVIEW, "P-003",
            "A cheaper supplier is useless if I cannot verify the required certification.",
            0.94, 4, ResearchConfidence.HIGH,
            {"compliance", "risk", "trust"},
        ),
        ResearchObservation(
            "OBS-006", "OBS-002", EvidenceType.OBSERVATION, "P-003",
            "Buyer opens separate certification documents before adding a supplier to the shortlist.",
            0.87, 3, ResearchConfidence.HIGH,
            {"compliance", "manual_work", "shortlist"},
        ),
        ResearchObservation(
            "OBS-007", "INT-004", EvidenceType.INTERVIEW, "P-004",
            "I maintain a personal spreadsheet because supplier portals do not preserve my comparison context.",
            0.83, 5, ResearchConfidence.HIGH,
            {"spreadsheet", "context", "comparison"},
        ),
        ResearchObservation(
            "OBS-008", "SUP-2026-09", EvidenceType.SUPPORT, None,
            "Support tickets frequently ask where supplier qualification evidence can be found.",
            0.71, 18, ResearchConfidence.MEDIUM,
            {"support", "qualification", "trust"},
        ),
        ResearchObservation(
            "OBS-009", "AN-2026-Q3", EvidenceType.ANALYTICS, None,
            "Supplier detail pages have high repeat visits but low shortlist conversion.",
            0.74, 1, ResearchConfidence.MEDIUM,
            {"analytics", "shortlist", "discovery"},
        ),
        ResearchObservation(
            "OBS-010", "SUR-2026-09", EvidenceType.SURVEY, None,
            "64% of respondents report spending at least 30 minutes manually comparing supplier attributes.",
            0.76, 64, ResearchConfidence.MEDIUM,
            {"survey", "comparison", "manual_work"},
        ),
        ResearchObservation(
            "OBS-011", "INT-005", EvidenceType.INTERVIEW, "P-005",
            "My team sends me a shortlist, but I often send it back because the evidence behind each supplier is unclear.",
            0.86, 3, ResearchConfidence.HIGH,
            {"shortlist", "evidence", "review"},
        ),
        ResearchObservation(
            "OBS-012", "INT-002", EvidenceType.INTERVIEW, "P-002",
            "When the requirement is urgent, I accept less market coverage in exchange for speed.",
            0.72, 3, ResearchConfidence.MEDIUM,
            {"time", "coverage", "tradeoff"},
        ),
    ]


# ---------------------------------------------------------------------------
# Research analysis and synthesis
# ---------------------------------------------------------------------------

def evidence_by_tag(
    observations: Iterable[ResearchObservation],
    tag: str,
) -> List[ResearchObservation]:
    return [item for item in observations if tag in item.tags]


def calculate_theme_metrics(
    evidence: Sequence[ResearchObservation],
    impact_multiplier: float,
    strategic_fit: float,
) -> Tuple[float, float]:
    if not evidence:
        return 0.0, 0.0

    weighted = sum(item.weighted_signal for item in evidence)
    frequency = min(10.0, math.log1p(sum(item.frequency for item in evidence)) * 2.0)
    impact = min(10.0, mean(item.severity for item in evidence) * 10.0 * impact_multiplier)
    fit = max(0.0, min(10.0, strategic_fit))
    return impact, frequency + fit * 0.0


def synthesize_themes(
    observations: Sequence[ResearchObservation],
) -> List[Theme]:
    """
    Cluster observations by product-discovery meaning.

    This is deliberately a transparent coding model. In a real research team,
    qualitative coding can be more nuanced, but explicit mappings make the
    reasoning auditable.
    """
    definitions = {
        "THEME-001": (
            "Manual comparison burden",
            "Buyers reconstruct comparable supplier information in spreadsheets and other personal artifacts.",
            {"comparison", "spreadsheet", "manual_work"},
            1.00,
            8.8,
        ),
        "THEME-002": (
            "Qualification evidence gap",
            "Supplier discovery becomes difficult when compliance and qualification evidence is fragmented or unclear.",
            {"compliance", "qualification", "trust", "evidence"},
            1.10,
            9.5,
        ),
        "THEME-003": (
            "Coverage versus speed trade-off",
            "Urgent procurement requests cause buyers to sacrifice market coverage to avoid lengthy supplier research.",
            {"coverage", "time", "discovery", "existing_supplier"},
            0.95,
            8.2,
        ),
        "THEME-004": (
            "Shortlist verification friction",
            "Decision makers cannot efficiently verify why a supplier belongs on a shortlist.",
            {"shortlist", "review", "evidence", "trust"},
            1.05,
            9.0,
        ),
    }

    themes: List[Theme] = []

    for theme_id, (name, description, tags, impact_multiplier, strategic_fit) in definitions.items():
        matched = [
            observation
            for observation in observations
            if observation.tags.intersection(tags)
        ]

        if not matched:
            continue

        weighted_signal = sum(item.weighted_signal for item in matched)
        frequency = min(10.0, math.log1p(weighted_signal) * 2.2)
        user_impact = min(
            10.0,
            mean(item.severity for item in matched) * 10.0 * impact_multiplier,
        )

        themes.append(
            Theme(
                theme_id,
                name,
                description,
                [item.observation_id for item in matched],
                round(user_impact, 2),
                round(frequency, 2),
                strategic_fit,
            )
        )

    return sorted(themes, key=lambda theme: theme.opportunity_score, reverse=True)


def build_opportunities(
    themes: Sequence[Theme],
) -> List[Opportunity]:
    statements = {
        "THEME-001": (
            "Procurement managers need a faster way to compare supplier attributes "
            "without manually reconstructing equivalent fields.",
            "compare suppliers using consistent evidence fields",
            8.4,
            8.8,
            7.8,
        ),
        "THEME-002": (
            "Procurement managers need qualification evidence attached to supplier "
            "decisions so that lower-cost alternatives do not create verification risk.",
            "verify qualification evidence before shortlisting",
            9.2,
            9.1,
            7.1,
        ),
        "THEME-003": (
            "Buyers need a way to discover credible alternatives without paying the "
            "full time cost of broad market research.",
            "expand supplier coverage while preserving decision speed",
            8.0,
            8.3,
            6.9,
        ),
        "THEME-004": (
            "Procurement leads need shortlist decisions to expose their supporting "
            "evidence so that review does not restart the research process.",
            "review a supplier shortlist through traceable evidence",
            8.7,
            8.9,
            7.4,
        ),
    }

    opportunities = []
    for theme in themes:
        statement = statements.get(theme.theme_id)
        if statement is None:
            continue

        text, behavior, evidence, business, feasibility = statement
        opportunities.append(
            Opportunity(
                f"OPP-{len(opportunities) + 1:03d}",
                theme.theme_id,
                text,
                behavior,
                evidence,
                business,
                feasibility,
            )
        )

    return sorted(
        opportunities,
        key=lambda opportunity: opportunity.opportunity_score,
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Ideation
# ---------------------------------------------------------------------------

def generate_concepts(opportunities: Sequence[Opportunity]) -> List[Concept]:
    """Generate distinct solution mechanisms rather than feature-name variations."""
    concepts: List[Concept] = []

    concept_catalog = {
        "THEME-001": [
            (
                "CON-001",
                "Evidence comparison workspace",
                "Normalize supplier attributes into a comparison matrix with source evidence beside each field.",
                "Buyer completes a supplier comparison with fewer manual copy/paste steps.",
                0.79,
                5.0,
                8.5,
            ),
            (
                "CON-002",
                "Requirement-aware shortlist",
                "Convert procurement requirements into comparison columns and flag missing supplier data.",
                "Buyer focuses research on missing decision-critical attributes.",
                0.71,
                4.0,
                7.8,
            ),
        ],
        "THEME-002": [
            (
                "CON-003",
                "Qualification evidence ledger",
                "Present certifications and qualification documents as traceable evidence linked to supplier claims.",
                "Buyer verifies eligibility without searching across separate document sources.",
                0.84,
                6.0,
                8.1,
            ),
            (
                "CON-004",
                "Evidence freshness monitor",
                "Show evidence age, source, verification status, and expiry risk next to supplier qualification data.",
                "Buyer distinguishes current evidence from potentially stale qualification claims.",
                0.76,
                5.0,
                7.2,
            ),
        ],
        "THEME-003": [
            (
                "CON-005",
                "Coverage gap detector",
                "Compare the current supplier shortlist against requirement dimensions and identify under-covered areas.",
                "Buyer sees whether the shortlist is narrow because of time rather than evidence.",
                0.69,
                4.0,
                7.5,
            ),
        ],
        "THEME-004": [
            (
                "CON-006",
                "Decision evidence packet",
                "Generate a traceable evidence view showing why each supplier entered the shortlist.",
                "Procurement lead can review decisions without repeating the research.",
                0.81,
                4.0,
                8.0,
            ),
        ],
    }

    for opportunity in opportunities:
        for record in concept_catalog.get(opportunity.theme_id, []):
            concept_id, name, mechanism, behavior, confidence, effort, reach = record
            concepts.append(
                Concept(
                    concept_id,
                    opportunity.opportunity_id,
                    name,
                    mechanism,
                    behavior,
                    confidence,
                    effort,
                    reach,
                )
            )

    return sorted(concepts, key=lambda concept: concept.desirability_score, reverse=True)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def create_experiments(concepts: Sequence[Concept]) -> List[Experiment]:
    """
    Construct small validation experiments.

    The metrics are intentionally behavior-oriented. A participant saying that
    a concept is useful is weaker evidence than successfully completing a
    realistic task with it.
    """
    experiment_specs = {
        "CON-001": (
            ExperimentType.USABILITY,
            8,
            "Successful supplier comparison completion rate",
            0.45,
            0.875,
            0.75,
            "Participants consistently used evidence columns instead of returning to supplier portals.",
        ),
        "CON-002": (
            ExperimentType.CONCEPT_TEST,
            10,
            "Participants selecting the requirement-driven workflow",
            0.40,
            0.60,
            0.72,
            "Participants understood the concept, but several wanted broader control over generated fields.",
        ),
        "CON-003": (
            ExperimentType.USABILITY,
            7,
            "Successful qualification verification rate",
            0.50,
            0.714,
            0.75,
            "Users understood the evidence relationship but needed clearer source provenance.",
        ),
        "CON-004": (
            ExperimentType.CONCEPT_TEST,
            9,
            "Participants identifying stale evidence",
            0.30,
            0.556,
            0.60,
            "The freshness signal was understood but was not consistently acted upon.",
        ),
        "CON-005": (
            ExperimentType.PROTOTYPE,
            8,
            "Participants detecting a coverage gap",
            0.35,
            0.875,
            0.70,
            "The gap visualization changed which suppliers participants investigated next.",
        ),
        "CON-006": (
            ExperimentType.USABILITY,
            8,
            "Reviewers verifying shortlist rationale without restarting research",
            0.35,
            0.75,
            0.70,
            "Reviewers could trace most decisions, but two evidence paths were ambiguous.",
        ),
    }

    experiments = []
    for concept in concepts:
        spec = experiment_specs.get(concept.concept_id)
        if spec is None:
            continue

        experiment_type, participants, metric, baseline, observed, threshold, notes = spec

        experiments.append(
            Experiment(
                f"EXP-{len(experiments) + 1:03d}",
                concept.concept_id,
                experiment_type,
                participants,
                metric,
                baseline,
                observed,
                threshold,
                0.70 if observed >= threshold else 0.55,
                notes=notes,
            )
        )

    return experiments


def run_validation(experiments: Sequence[Experiment]) -> None:
    for experiment in experiments:
        experiment.evaluate()


def identify_learning(experiment: Experiment) -> str:
    """Translate experiment outcome into a concrete product-discovery learning."""
    if experiment.decision == Decision.CONTINUE:
        return "Evidence supports the behavior change strongly enough to justify the next validation stage."
    if experiment.decision == Decision.ITERATE:
        return "The mechanism has evidence but exposes a usability or trust gap that must be tested again."
    return "The observed behavior did not justify further investment in the tested mechanism."
    

# ---------------------------------------------------------------------------
# Assumption management
# ---------------------------------------------------------------------------

@dataclass
class Assumption:
    assumption_id: str
    statement: str
    type: str
    importance: float
    uncertainty: float
    evidence: float = 0.0

    @property
    def risk_score(self) -> float:
        return round(self.importance * self.uncertainty * (1.0 - self.evidence), 2)


def prioritize_assumptions(assumptions: Sequence[Assumption]) -> List[Assumption]:
    return sorted(assumptions, key=lambda item: item.risk_score, reverse=True)


def build_assumptions() -> List[Assumption]:
    return [
        Assumption(
            "ASM-001",
            "Procurement managers will trust normalized supplier attributes only when each important field has visible evidence provenance.",
            "desirability/trust",
            0.95,
            0.75,
            0.65,
        ),
        Assumption(
            "ASM-002",
            "Reducing comparison effort will cause buyers to evaluate more qualified alternatives rather than simply completing the same process faster.",
            "behavior",
            0.88,
            0.80,
            0.35,
        ),
        Assumption(
            "ASM-003",
            "Supplier qualification data can be kept sufficiently current to support decision-making.",
            "feasibility/data",
            0.92,
            0.85,
            0.30,
        ),
        Assumption(
            "ASM-004",
            "Procurement leads value traceable evidence enough to change their shortlist review behavior.",
            "business/desirability",
            0.80,
            0.60,
            0.50,
        ),
    ]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_plan(plan: SprintPlan, calendar: Dict[int, List[str]]) -> None:
    print("\n=== PRODUCT DISCOVERY SPRINT PLAN ===")
    print(f"Product area: {plan.product_area}")
    print(f"Target segment: {plan.target_segment}")
    print(f"Business outcome: {plan.business_outcome}")
    print(f"Sprint duration: {plan.sprint_days} days")

    print("\nResearch questions:")
    for question in plan.research_questions:
        print(f"  - {question}")

    print("\nSprint cadence:")
    for day, activities in calendar.items():
        print(f"  Day {day}: {'; '.join(activities)}")


def print_research_summary(observations: Sequence[ResearchObservation]) -> None:
    print("\n=== RESEARCH EVIDENCE ===")

    source_counts: Dict[EvidenceType, int] = {}
    for observation in observations:
        source_counts[observation.evidence_type] = (
            source_counts.get(observation.evidence_type, 0) + 1
        )

    for evidence_type, count in source_counts.items():
        print(f"{evidence_type.value:12} {count} observations")

    print("\nHigh-signal observations:")
    for observation in sorted(
        observations,
        key=lambda item: item.weighted_signal,
        reverse=True,
    )[:6]:
        print(
            f"  {observation.observation_id} | "
            f"{observation.evidence_type.value:11} | "
            f"signal={observation.weighted_signal:.2f} | "
            f"{observation.text}"
        )


def print_themes(themes: Sequence[Theme]) -> None:
    print("\n=== SYNTHESIZED THEMES ===")
    for theme in themes:
        print(
            f"{theme.theme_id} | {theme.name} | "
            f"opportunity score={theme.opportunity_score:.2f}"
        )
        print(f"  {theme.description}")
        print(f"  Evidence: {', '.join(theme.evidence_ids)}")


def print_opportunities(opportunities: Sequence[Opportunity]) -> None:
    print("\n=== OPPORTUNITY SPACE ===")
    for opportunity in opportunities:
        print(
            f"{opportunity.opportunity_id} | "
            f"score={opportunity.opportunity_score:.2f}"
        )
        print(f"  {opportunity.statement}")
        print(f"  Target behavior: {opportunity.target_behavior}")


def print_concepts(concepts: Sequence[Concept]) -> None:
    print("\n=== IDEATED CONCEPTS ===")
    for concept in concepts:
        print(
            f"{concept.concept_id} | {concept.name} | "
            f"desirability score={concept.desirability_score:.2f}"
        )
        print(f"  Mechanism: {concept.mechanism}")
        print(f"  Expected behavior: {concept.expected_behavior_change}")


def print_validation(experiments: Sequence[Experiment]) -> None:
    print("\n=== VALIDATION RESULTS ===")
    for experiment in experiments:
        print(
            f"{experiment.experiment_id} | {experiment.concept_id} | "
            f"{experiment.experiment_type.value} | "
            f"decision={experiment.decision.value}"
        )
        print(
            f"  Metric: {experiment.success_metric}; "
            f"baseline={experiment.baseline:.1%}; "
            f"observed={experiment.observed:.1%}; "
            f"threshold={experiment.threshold:.1%}; "
            f"lift={experiment.quantitative_lift:.1%}"
        )
        print(f"  Learning: {identify_learning(experiment)}")
        print(f"  Notes: {experiment.notes}")


def print_assumptions(assumptions: Sequence[Assumption]) -> None:
    print("\n=== ASSUMPTION RISK ===")
    for assumption in assumptions:
        print(
            f"{assumption.assumption_id} | risk={assumption.risk_score:.2f} | "
            f"{assumption.type}"
        )
        print(f"  {assumption.statement}")


# ---------------------------------------------------------------------------
# Quality checks
# ---------------------------------------------------------------------------

def validate_discovery_integrity(
    plan: SprintPlan,
    observations: Sequence[ResearchObservation],
    themes: Sequence[Theme],
    opportunities: Sequence[Opportunity],
    concepts: Sequence[Concept],
    experiments: Sequence[Experiment],
) -> None:
    """
    Enforce useful discovery-quality invariants.

    These checks prevent a polished-looking sprint report from hiding broken
    traceability, missing evidence, or unmeasurable validation.
    """
    if not plan.research_questions:
        raise AssertionError("Discovery cannot begin without research questions.")

    if len(observations) < 3:
        raise AssertionError("Evidence base is too small for synthesis.")

    observation_ids = {item.observation_id for item in observations}

    for theme in themes:
        if not set(theme.evidence_ids).issubset(observation_ids):
            raise AssertionError(f"{theme.theme_id} contains unknown evidence.")

    theme_ids = {theme.theme_id for theme in themes}

    for opportunity in opportunities:
        if opportunity.theme_id not in theme_ids:
            raise AssertionError("Opportunity is not traceable to a synthesized theme.")

        if not 0 <= opportunity.evidence_strength <= 10:
            raise AssertionError("Evidence strength must remain on the 0-10 scale.")

    opportunity_ids = {item.opportunity_id for item in opportunities}

    for concept in concepts:
        if concept.opportunity_id not in opportunity_ids:
            raise AssertionError("Concept is not traceable to an opportunity.")

    concept_ids = {item.concept_id for item in concepts}

    for experiment in experiments:
        if experiment.concept_id not in concept_ids:
            raise AssertionError("Experiment references an unknown concept.")
        if experiment.participants <= 0:
            raise AssertionError("Experiments require actual participants.")
        if not 0 <= experiment.baseline <= 1:
            raise AssertionError("Baseline must be a proportion.")
        if not 0 <= experiment.observed <= 1:
            raise AssertionError("Observed result must be a proportion.")
        if not 0 <= experiment.threshold <= 1:
            raise AssertionError("Validation threshold must be a proportion.")


def demonstrate_edge_cases() -> None:
    print("\n=== DISCOVERY EDGE CASES ===")

    zero_baseline = Experiment(
        "EXP-EDGE-001",
        "CON-001",
        ExperimentType.FAKE_DOOR,
        12,
        "Activation rate",
        0.0,
        0.18,
        0.15,
        0.70,
    )
    print(
        "Zero-baseline lift:",
        zero_baseline.quantitative_lift,
        "(undefined ratios are represented safely as 0 rather than raising ZeroDivisionError)"
    )

    empty_theme = synthesize_themes([])
    print(f"Empty evidence synthesis produces {len(empty_theme)} themes.")

    try:
        invalid_plan = SprintPlan(
            "x",
            "y",
            "z",
            2,
            (),
            (),
            (),
        )
        create_research_calendar(invalid_plan)
    except ValueError as exc:
        print(f"Invalid sprint plan rejected: {exc}")


# ---------------------------------------------------------------------------
# A lightweight experiment simulation
# ---------------------------------------------------------------------------

def simulate_task_outcomes(
    participants: int,
    success_probability: float,
    seed: int = 42,
) -> Tuple[int, float]:
    """
    Simulate task completion to show why raw counts and rates should both be retained.

    A fixed seed makes the educational run reproducible. Production experiments
    should preserve the actual assignment mechanism and raw event data instead.
    """
    if participants <= 0:
        raise ValueError("Participant count must be positive.")
    if not 0 <= success_probability <= 1:
        raise ValueError("Success probability must be between 0 and 1.")

    rng = random.Random(seed)
    successes = sum(
        1
        for _ in range(participants)
        if rng.random() < success_probability
    )
    return successes, successes / participants


def demonstrate_validation_statistics() -> None:
    print("\n=== VALIDATION MEASUREMENT ===")
    successes, rate = simulate_task_outcomes(20, 0.78)
    print(f"Successful tasks: {successes}/20")
    print(f"Observed completion rate: {rate:.1%}")

    # A small sample can be noisy. A confidence interval prevents the team
    # from treating one observed proportion as exact product truth.
    standard_error = math.sqrt(rate * (1 - rate) / 20)
    margin = 1.96 * standard_error
    print(
        f"Approximate 95% interval: "
        f"{max(0, rate - margin):.1%} to {min(1, rate + margin):.1%}"
    )


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main() -> None:
    plan = build_sprint_plan()
    calendar = create_research_calendar(plan)
    participants = create_participants()
    observations = collect_research_observations()

    themes = synthesize_themes(observations)
    opportunities = build_opportunities(themes)
    concepts = generate_concepts(opportunities)

    experiments = create_experiments(concepts)
    run_validation(experiments)

    assumptions = prioritize_assumptions(build_assumptions())

    validate_discovery_integrity(
        plan,
        observations,
        themes,
        opportunities,
        concepts,
        experiments,
    )

    print_plan(plan, calendar)

    print("\nResearch participants:")
    for participant in participants:
        print(
            f"  {participant.participant_id}: "
            f"{participant.role} / {participant.segment} / {participant.context}"
        )

    print_research_summary(observations)
    print_themes(themes)
    print_opportunities(opportunities)
    print_concepts(concepts)
    print_validation(experiments)
    print_assumptions(assumptions)
    demonstrate_validation_statistics()
    demonstrate_edge_cases()

    print("\n=== SPRINT DECISION FRAME ===")
    continue_items = [
        experiment
        for experiment in experiments
        if experiment.decision == Decision.CONTINUE
    ]
    iterate_items = [
        experiment
        for experiment in experiments
        if experiment.decision == Decision.ITERATE
    ]
    stop_items = [
        experiment
        for experiment in experiments
        if experiment.decision == Decision.STOP
    ]

    print(f"Continue: {', '.join(item.concept_id for item in continue_items) or 'none'}")
    print(f"Iterate: {', '.join(item.concept_id for item in iterate_items) or 'none'}")
    print(f"Stop: {', '.join(item.concept_id for item in stop_items) or 'none'}")

    print(
        "\nDiscovery principle demonstrated: evidence moves through "
        "question -> observation -> theme -> opportunity -> concept -> "
        "experiment -> decision. Each transition preserves traceability."
    )


if __name__ == "__main__":
    main()
