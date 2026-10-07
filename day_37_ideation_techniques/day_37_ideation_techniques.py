"""
Ideation Techniques: Brainstorming, Crazy 8s, SCAMPER, Mind Mapping,
and Reverse Brainstorming

A self-contained technical learning and simulation program.

The program models five distinct ideation techniques:

- Brainstorming: divergent group idea generation under explicit rules.
- Crazy 8s: rapid visual ideation using eight short time-boxed prompts.
- SCAMPER: structured transformation of an existing concept through
  Substitute, Combine, Adapt, Modify, Put to another use, Eliminate,
  and Reverse/Rearrange.
- Mind Mapping: hierarchical association of a central problem with
  branches, sub-branches, and relationships.
- Reverse Brainstorming: deliberately identifying ways to worsen a
  problem, then converting those failure ideas into improvement actions.

The examples use a realistic operations problem: reducing customer
support response time without simply adding more staff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections import Counter, defaultdict
from itertools import combinations
import math
import random
import statistics
from typing import Iterable


# ---------------------------------------------------------------------------
# Shared domain model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Idea:
    """An idea with enough metadata to support comparison and evaluation."""

    title: str
    description: str
    source: str
    novelty: int = 3
    feasibility: int = 3
    impact: int = 3
    confidence: int = 3
    tags: tuple[str, ...] = ()

    def score(self) -> float:
        """Weighted score favoring impact while retaining feasibility."""
        return (
            self.novelty * 0.25
            + self.feasibility * 0.25
            + self.impact * 0.35
            + self.confidence * 0.15
        )

    def validate(self) -> None:
        for field_name, value in (
            ("novelty", self.novelty),
            ("feasibility", self.feasibility),
            ("impact", self.impact),
            ("confidence", self.confidence),
        ):
            if not 1 <= value <= 5:
                raise ValueError(
                    f"{field_name} must be between 1 and 5, got {value}"
                )

        if not self.title.strip():
            raise ValueError("Idea title cannot be empty.")
        if not self.description.strip():
            raise ValueError("Idea description cannot be empty.")


@dataclass
class Participant:
    name: str
    perspective: str
    expertise: set[str] = field(default_factory=set)

    def contribute(self, prompt: str, seed: int) -> str:
        """Create a deterministic contribution from a participant profile."""
        rng = random.Random(seed)

        perspective_ideas = {
            "customer": [
                "show an estimated response time before submission",
                "let customers choose urgency with evidence",
                "provide proactive progress notifications",
            ],
            "support_agent": [
                "route requests by skill rather than queue order",
                "surface similar resolved cases while typing",
                "create reusable response fragments for recurring issues",
            ],
            "operations": [
                "rebalance workload automatically across teams",
                "measure queue age instead of only ticket count",
                "introduce an exception queue for aging requests",
            ],
            "technology": [
                "classify requests automatically at intake",
                "detect duplicate cases before assignment",
                "use event-driven alerts for abnormal queue growth",
            ],
            "quality": [
                "sample automated resolutions for quality review",
                "define escalation thresholds from historical defects",
                "track first-contact resolution alongside speed",
            ],
        }

        candidates = perspective_ideas.get(
            self.perspective,
            [
                "remove an unnecessary handoff",
                "make the decision rule explicit",
                "measure the bottleneck directly",
            ],
        )

        idea = rng.choice(candidates)
        return f"{self.name} ({self.perspective}): {idea}"


class DivergenceMode(Enum):
    FREE = "free"
    STRUCTURED = "structured"


@dataclass
class EvaluationResult:
    idea: Idea
    rank: int
    score: float


# ---------------------------------------------------------------------------
# Brainstorming
# ---------------------------------------------------------------------------

class BrainstormingSession:
    """
    Models conventional brainstorming as a divergent activity.

    The important mechanism is separation of generation from evaluation.
    Ideas are collected without scoring first, then evaluated afterward.
    This prevents early criticism from narrowing the search space.
    """

    RULES = (
        "Defer judgment during generation.",
        "Seek quantity before selection.",
        "Build on other participants' ideas.",
        "Permit unusual ideas.",
    )

    def __init__(
        self,
        problem: str,
        participants: list[Participant],
        mode: DivergenceMode = DivergenceMode.STRUCTURED,
    ) -> None:
        if not problem.strip():
            raise ValueError("Problem statement cannot be empty.")
        if not participants:
            raise ValueError("At least one participant is required.")

        self.problem = problem
        self.participants = participants
        self.mode = mode
        self.ideas: list[Idea] = []

    def generate(self, rounds: int = 3) -> list[Idea]:
        if rounds <= 0:
            raise ValueError("rounds must be positive.")

        self.ideas.clear()

        for round_number in range(1, rounds + 1):
            for index, participant in enumerate(self.participants):
                contribution = participant.contribute(
                    self.problem,
                    seed=round_number * 100 + index,
                )

                self.ideas.append(
                    Idea(
                        title=f"{participant.name}'s round {round_number} idea",
                        description=contribution.split(": ", 1)[-1],
                        source="Brainstorming",
                        novelty=2 + ((round_number + index) % 4),
                        feasibility=2 + (index % 4),
                        impact=3 + ((round_number + index) % 3),
                        confidence=3,
                        tags=(participant.perspective, "divergent"),
                    )
                )

        return self.ideas

    def build_on_existing(self) -> Idea:
        """
        Demonstrate 'build on another idea' rather than independent ideation.
        """
        if not self.ideas:
            raise RuntimeError("Generate brainstorming ideas first.")

        base = max(self.ideas, key=lambda item: item.impact)
        derived = Idea(
            title="Unified intelligent intake",
            description=(
                f"Combine '{base.description}' with automatic classification "
                "and duplicate detection before assignment."
            ),
            source="Brainstorming",
            novelty=5,
            feasibility=4,
            impact=5,
            confidence=4,
            tags=("synthesis", "intake", "automation"),
        )
        self.ideas.append(derived)
        return derived

    def evaluate_after_divergence(self) -> list[EvaluationResult]:
        for idea in self.ideas:
            idea.validate()

        ranked = sorted(
            self.ideas,
            key=lambda item: item.score(),
            reverse=True,
        )

        return [
            EvaluationResult(idea=idea, rank=index, score=idea.score())
            for index, idea in enumerate(ranked, start=1)
        ]


# ---------------------------------------------------------------------------
# Crazy 8s
# ---------------------------------------------------------------------------

class Crazy8sSession:
    """
    Models Crazy 8s as eight rapid concepts generated under time pressure.

    The technique intentionally changes the constraint from 'find one good
    idea' to 'generate eight distinct directions quickly'. This reduces
    attachment to the first acceptable concept.
    """

    PROMPTS = (
        "remove a step",
        "automate the repetitive part",
        "make the customer self-serve",
        "reverse the normal workflow",
        "personalize the experience",
        "make the process visible",
        "combine two stages",
        "design an intentionally extreme version",
    )

    def __init__(self, challenge: str) -> None:
        if not challenge.strip():
            raise ValueError("Challenge cannot be empty.")
        self.challenge = challenge

    def generate(self) -> list[Idea]:
        ideas = []

        for number, prompt in enumerate(self.PROMPTS, start=1):
            descriptions = {
                1: "Remove manual triage by asking only the minimum diagnostic questions.",
                2: "Automatically classify incoming requests and suggest the correct queue.",
                3: "Expose guided troubleshooting so customers can resolve routine issues.",
                4: "Let the system assign work dynamically instead of waiting for supervisors.",
                5: "Adapt response paths to customer type, issue severity, and history.",
                6: "Show queue position, expected response window, and escalation state.",
                7: "Combine intake and knowledge retrieval into one interaction.",
                8: "Create a near-zero-touch support path for predictable requests.",
            }

            ideas.append(
                Idea(
                    title=f"Crazy 8 concept {number}",
                    description=f"Prompt '{prompt}': {descriptions[number]}",
                    source="Crazy 8s",
                    novelty=min(5, 2 + number // 2),
                    feasibility=4 if number in {1, 2, 6, 7} else 3,
                    impact=4 if number in {2, 3, 4, 7, 8} else 3,
                    confidence=3,
                    tags=("rapid", f"prompt-{number}"),
                )
            )

        return ideas


# ---------------------------------------------------------------------------
# SCAMPER
# ---------------------------------------------------------------------------

class ScamperOperator(Enum):
    SUBSTITUTE = "Substitute"
    COMBINE = "Combine"
    ADAPT = "Adapt"
    MODIFY = "Modify"
    PUT_TO_ANOTHER_USE = "Put to another use"
    ELIMINATE = "Eliminate"
    REVERSE = "Reverse/Rearrange"


class ScamperWorkshop:
    """
    Applies seven transformation lenses to an existing service concept.

    SCAMPER is not a free-form idea list. Its distinctive mechanism is
    transformation of something that already exists.
    """

    def __init__(self, existing_concept: str) -> None:
        if not existing_concept.strip():
            raise ValueError("Existing concept cannot be empty.")
        self.existing_concept = existing_concept

    def apply(self, operator: ScamperOperator) -> Idea:
        transformations = {
            ScamperOperator.SUBSTITUTE: (
                "Replace first-come-first-served assignment with "
                "skill-and-urgency-based routing."
            ),
            ScamperOperator.COMBINE: (
                "Combine intake, classification, and knowledge retrieval "
                "into a single guided workflow."
            ),
            ScamperOperator.ADAPT: (
                "Adapt the queue model from emergency dispatch so severe "
                "cases receive immediate routing."
            ),
            ScamperOperator.MODIFY: (
                "Modify the customer portal to ask adaptive questions "
                "based on earlier answers."
            ),
            ScamperOperator.PUT_TO_ANOTHER_USE: (
                "Use historical support patterns to identify recurring "
                "product defects before customers report them."
            ),
            ScamperOperator.ELIMINATE: (
                "Eliminate unnecessary supervisor handoffs for low-risk "
                "requests with known resolution paths."
            ),
            ScamperOperator.REVERSE: (
                "Instead of waiting for customers to request updates, "
                "push status information before customers ask."
            ),
        }

        description = transformations[operator]

        return Idea(
            title=f"{operator.value}: {self.existing_concept}",
            description=description,
            source="SCAMPER",
            novelty=5 if operator in {
                ScamperOperator.PUT_TO_ANOTHER_USE,
                ScamperOperator.REVERSE,
            } else 4,
            feasibility=4 if operator in {
                ScamperOperator.SUBSTITUTE,
                ScamperOperator.MODIFY,
                ScamperOperator.ELIMINATE,
            } else 3,
            impact=5 if operator in {
                ScamperOperator.COMBINE,
                ScamperOperator.PUT_TO_ANOTHER_USE,
                ScamperOperator.REVERSE,
            } else 4,
            confidence=4,
            tags=(operator.value.lower(), "transformation"),
        )


# ---------------------------------------------------------------------------
# Mind mapping
# ---------------------------------------------------------------------------

@dataclass
class MindMapNode:
    label: str
    relationship: str
    children: list["MindMapNode"] = field(default_factory=list)

    def add_child(self, label: str, relationship: str) -> "MindMapNode":
        child = MindMapNode(label=label, relationship=relationship)
        self.children.append(child)
        return child

    def depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children)

    def flatten(self) -> list[tuple[str, str, int]]:
        result: list[tuple[str, str, int]] = []

        def visit(node: MindMapNode, level: int) -> None:
            result.append((node.label, node.relationship, level))
            for child in node.children:
                visit(child, level + 1)

        visit(self, 0)
        return result


class MindMap:
    """
    Represents associative thinking as a tree rather than a flat list.

    The structure allows a central challenge to branch into dimensions,
    causes, opportunities, interventions, and measures.
    """

    def __init__(self, central_problem: str) -> None:
        if not central_problem.strip():
            raise ValueError("Central problem cannot be empty.")
        self.root = MindMapNode(central_problem, "central challenge")

    def build_support_response_map(self) -> None:
        customer = self.root.add_child("Customer experience", "dimension")
        customer.add_child("Expected response time", "concern")
        customer.add_child("Self-service", "opportunity")
        customer.add_child("Progress visibility", "opportunity")

        workflow = self.root.add_child("Workflow", "dimension")
        routing = workflow.add_child("Routing", "process")
        routing.add_child("Skill matching", "mechanism")
        routing.add_child("Urgency classification", "mechanism")
        workflow.add_child("Handoffs", "bottleneck")
        workflow.add_child("Queue aging", "metric")

        knowledge = self.root.add_child("Knowledge", "dimension")
        knowledge.add_child("Search quality", "capability")
        knowledge.add_child("Reusable resolutions", "capability")
        knowledge.add_child("Missing documentation", "root cause")

        measurement = self.root.add_child("Measurement", "dimension")
        measurement.add_child("First response time", "metric")
        measurement.add_child("First-contact resolution", "quality metric")
        measurement.add_child("Reopened cases", "quality signal")

    def print_tree(self) -> None:
        for label, relationship, level in self.root.flatten():
            indent = "  " * level
            print(f"{indent}- {label} [{relationship}]")


# ---------------------------------------------------------------------------
# Reverse brainstorming
# ---------------------------------------------------------------------------

class ReverseBrainstorming:
    """
    Starts with a deliberate deterioration question.

    The important distinction is that the group does not immediately propose
    improvements. It first exposes failure mechanisms by asking how to make
    the target outcome worse. Those mechanisms are then inverted into
    countermeasures.
    """

    def __init__(self, desired_outcome: str) -> None:
        if not desired_outcome.strip():
            raise ValueError("Desired outcome cannot be empty.")
        self.desired_outcome = desired_outcome

    def generate_failure_ideas(self) -> list[str]:
        return [
            "route every request to the same queue regardless of skill",
            "hide queue status so customers cannot predict response time",
            "require a supervisor approval for every request",
            "duplicate customer information across every handoff",
            "measure only ticket closure count and ignore reopening",
            "allow unresolved aging cases to remain mixed with new cases",
        ]

    @staticmethod
    def invert(failure_idea: str) -> str:
        inversion_rules = {
            "route every request to the same queue regardless of skill":
                "Route requests using skill, urgency, and workload.",
            "hide queue status so customers cannot predict response time":
                "Expose realistic response windows and status updates.",
            "require a supervisor approval for every request":
                "Reserve supervisor approval for exceptions and high-risk cases.",
            "duplicate customer information across every handoff":
                "Maintain one shared case record across the workflow.",
            "measure only ticket closure count and ignore reopening":
                "Track resolution quality, reopening, and customer outcome.",
            "allow unresolved aging cases to remain mixed with new cases":
                "Create explicit aging thresholds and an escalation path.",
        }

        return inversion_rules.get(
            failure_idea,
            f"Prevent the failure mechanism: {failure_idea}",
        )

    def produce_countermeasures(self) -> list[Idea]:
        failures = self.generate_failure_ideas()

        return [
            Idea(
                title=f"Countermeasure: {failure}",
                description=self.invert(failure),
                source="Reverse Brainstorming",
                novelty=4,
                feasibility=4,
                impact=5,
                confidence=4,
                tags=("failure-analysis", "countermeasure"),
            )
            for failure in failures
        ]


# ---------------------------------------------------------------------------
# Cross-technique synthesis
# ---------------------------------------------------------------------------

def deduplicate_by_description(ideas: Iterable[Idea]) -> list[Idea]:
    """Remove exact duplicates while preserving first occurrence."""
    seen: set[str] = set()
    unique: list[Idea] = []

    for idea in ideas:
        normalized = " ".join(idea.description.lower().split())
        if normalized not in seen:
            seen.add(normalized)
            unique.append(idea)

    return unique


def tag_distribution(ideas: Iterable[Idea]) -> Counter[str]:
    counts: Counter[str] = Counter()

    for idea in ideas:
        counts.update(idea.tags)

    return counts


def diversity_score(ideas: list[Idea]) -> float:
    """
    Estimate diversity from unique technique-tag combinations.

    This is not a scientific creativity metric. It is a simple diagnostic
    for demonstrating how a system can detect overly homogeneous output.
    """
    if not ideas:
        return 0.0

    signatures = {
        tuple(sorted(idea.tags))
        for idea in ideas
    }

    return min(100.0, len(signatures) / len(ideas) * 100)


def select_portfolio(ideas: list[Idea], limit: int = 5) -> list[Idea]:
    """
    Select a balanced portfolio rather than simply taking the highest scores.

    A portfolio gets one high-impact idea, one highly feasible idea, one
    structurally different idea, and then fills remaining positions by score.
    """
    if limit <= 0:
        raise ValueError("limit must be positive.")

    unique = deduplicate_by_description(ideas)

    if not unique:
        return []

    selected: list[Idea] = []

    candidates = [
        max(unique, key=lambda item: item.impact),
        max(unique, key=lambda item: item.feasibility),
        max(unique, key=lambda item: item.novelty),
    ]

    for candidate in candidates:
        if candidate not in selected:
            selected.append(candidate)

    for candidate in sorted(unique, key=lambda item: item.score(), reverse=True):
        if len(selected) >= limit:
            break
        if candidate not in selected:
            selected.append(candidate)

    return selected[:limit]


def print_idea_table(title: str, ideas: list[Idea], limit: int | None = None) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    display = ideas if limit is None else ideas[:limit]

    for index, idea in enumerate(display, start=1):
        print(
            f"{index:>2}. {idea.title}\n"
            f"    {idea.description}\n"
            f"    score={idea.score():.2f} | "
            f"novelty={idea.novelty} | feasibility={idea.feasibility} | "
            f"impact={idea.impact}"
        )


# ---------------------------------------------------------------------------
# Evaluation diagnostics
# ---------------------------------------------------------------------------

def compare_techniques(
    technique_results: dict[str, list[Idea]],
) -> None:
    print("\nTechnique comparison")
    print("--------------------")

    for technique, ideas in technique_results.items():
        if not ideas:
            continue

        average_score = statistics.mean(idea.score() for idea in ideas)
        average_novelty = statistics.mean(idea.novelty for idea in ideas)
        average_feasibility = statistics.mean(idea.feasibility for idea in ideas)

        print(
            f"{technique:24} "
            f"ideas={len(ideas):2} "
            f"avg_score={average_score:.2f} "
            f"avg_novelty={average_novelty:.2f} "
            f"avg_feasibility={average_feasibility:.2f}"
        )


def analyze_combinations(ideas: list[Idea]) -> list[tuple[str, str, float]]:
    """
    Find pairs of ideas whose combined descriptions suggest complementary
    directions. This models synthesis after divergent exploration.
    """
    results = []

    for left, right in combinations(ideas, 2):
        if left.source == right.source:
            continue

        shared_tags = set(left.tags) & set(right.tags)

        synergy = (
            left.impact
            + right.impact
            + len(shared_tags)
            + (1 if left.source != right.source else 0)
        )

        results.append((left.title, right.title, float(synergy)))

    return sorted(results, key=lambda item: item[2], reverse=True)


# ---------------------------------------------------------------------------
# Validation and edge-case demonstrations
# ---------------------------------------------------------------------------

def demonstrate_validation() -> None:
    print("\nValidation and failure conditions")
    print("---------------------------------")

    try:
        Idea(
            title="",
            description="Invalid idea",
            source="Test",
        ).validate()
    except ValueError as error:
        print(f"Empty title rejected: {error}")

    try:
        Idea(
            title="Bad score",
            description="Invalid score",
            source="Test",
            impact=7,
        ).validate()
    except ValueError as error:
        print(f"Out-of-range score rejected: {error}")

    try:
        BrainstormingSession("", [])
    except ValueError as error:
        print(f"Invalid brainstorming session rejected: {error}")

    try:
        Crazy8sSession(" ").generate()
    except ValueError as error:
        print(f"Invalid Crazy 8s challenge rejected: {error}")


# ---------------------------------------------------------------------------
# Main educational workflow
# ---------------------------------------------------------------------------

def main() -> None:
    problem = (
        "How might a customer support organization reduce response time "
        "without reducing resolution quality?"
    )

    participants = [
        Participant(
            name="Asha",
            perspective="customer",
            expertise={"customer-experience", "service-design"},
        ),
        Participant(
            name="Ravi",
            perspective="support_agent",
            expertise={"support", "knowledge-management"},
        ),
        Participant(
            name="Meera",
            perspective="operations",
            expertise={"operations", "capacity-planning"},
        ),
        Participant(
            name="Kabir",
            perspective="technology",
            expertise={"automation", "data"},
        ),
        Participant(
            name="Nisha",
            perspective="quality",
            expertise={"quality", "risk"},
        ),
    ]

    print("IDEATION TECHNIQUES WORKSHOP")
    print("============================")
    print(f"Challenge: {problem}")

    # Brainstorming explores the problem from multiple participant
    # perspectives before evaluation begins.
    brainstorming = BrainstormingSession(problem, participants)
    brainstorming_ideas = brainstorming.generate(rounds=2)
    brainstorming.build_on_existing()

    print_idea_table(
        "Brainstorming: divergent generation",
        brainstorming_ideas,
        limit=6,
    )

    ranked_brainstorming = brainstorming.evaluate_after_divergence()

    print("\nPost-generation evaluation")
    print("--------------------------")
    for result in ranked_brainstorming[:5]:
        print(f"{result.rank}. {result.idea.title}: {result.score:.2f}")

    # Crazy 8s changes the generation constraint. Each prompt forces a
    # different direction rather than repeatedly refining one idea.
    crazy8s = Crazy8sSession(
        "Reduce support response time without adding permanent headcount."
    )
    crazy_ideas = crazy8s.generate()

    print_idea_table("Crazy 8s: rapid directional exploration", crazy_ideas)

    # SCAMPER starts with an existing concept and transforms it through
    # distinct operators rather than generating unrelated ideas.
    scamper = ScamperWorkshop(
        "A conventional ticket queue with manual triage"
    )
    scamper_ideas = [
        scamper.apply(operator)
        for operator in ScamperOperator
    ]

    print_idea_table(
        "SCAMPER: transformation of an existing concept",
        scamper_ideas,
    )

    # Mind mapping represents relationships and dimensions rather than
    # treating ideas as independent records.
    mind_map = MindMap("Slow customer support response")
    mind_map.build_support_response_map()

    print("\nMind map")
    print("--------")
    mind_map.print_tree()
    print(f"Tree depth: {mind_map.root.depth()}")

    # Reverse brainstorming intentionally constructs undesirable conditions,
    # making hidden failure mechanisms easier to identify.
    reverse = ReverseBrainstorming(
        "Fast, reliable customer support response"
    )
    failures = reverse.generate_failure_ideas()

    print("\nReverse brainstorming: failure mechanisms")
    print("------------------------------------------")
    for failure in failures:
        print(f"- {failure}")

    reverse_ideas = reverse.produce_countermeasures()

    print_idea_table(
        "Reverse brainstorming: converted countermeasures",
        reverse_ideas,
    )

    all_results = {
        "Brainstorming": brainstorming_ideas,
        "Crazy 8s": crazy_ideas,
        "SCAMPER": scamper_ideas,
        "Mind Mapping": [
            Idea(
                title=label,
                description=relationship,
                source="Mind Mapping",
                novelty=4,
                feasibility=4,
                impact=4,
                confidence=3,
                tags=("map", relationship),
            )
            for label, relationship, _ in mind_map.root.flatten()
            if label != mind_map.root.label
        ],
        "Reverse Brainstorming": reverse_ideas,
    }

    compare_techniques(all_results)

    combined = deduplicate_by_description(
        idea
        for ideas in all_results.values()
        for idea in ideas
    )

    print(f"\nUnique generated concepts: {len(combined)}")
    print(f"Tag diversity diagnostic: {diversity_score(combined):.1f}%")

    distribution = tag_distribution(combined)
    print("\nMost common idea characteristics")
    print("--------------------------------")
    for tag, count in distribution.most_common(10):
        print(f"{tag:24} {count}")

    portfolio = select_portfolio(combined, limit=6)
    print_idea_table(
        "Cross-technique concept portfolio",
        portfolio,
    )

    synergies = analyze_combinations(combined)

    print("\nCross-technique synthesis opportunities")
    print("---------------------------------------")
    for left, right, score in synergies[:5]:
        print(f"{left} + {right} -> synergy={score:.1f}")

    demonstrate_validation()

    print("\nPractical distinction")
    print("---------------------")
    print(
        "Brainstorming expands the search space through participant ideas. "
        "Crazy 8s deliberately increases speed and variety through rapid "
        "time-boxed prompts. SCAMPER transforms an existing concept using "
        "specific modification lenses. Mind mapping exposes relationships "
        "between dimensions and subproblems. Reverse brainstorming uncovers "
        "failure mechanisms by intentionally worsening the target outcome."
    )


if __name__ == "__main__":
    main()
