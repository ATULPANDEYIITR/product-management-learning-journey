from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from statistics import mean
from typing import Callable, Iterable
import json
import tempfile


class DesignStage(str, Enum):
    EMPATHIZE = "Empathize"
    DEFINE = "Define"
    IDEATE = "Ideate"
    PROTOTYPE = "Prototype"
    TEST = "Test"


@dataclass(frozen=True)
class User:
    user_id: str
    name: str
    role: str
    context: str


@dataclass
class Observation:
    user_id: str
    behavior: str
    quote: str
    pain_point: str
    evidence_strength: float


@dataclass
class Insight:
    statement: str
    supporting_observations: list[Observation]
    confidence: float


@dataclass
class ProblemStatement:
    user: str
    need: str
    insight: str
    measurable_outcome: str


@dataclass
class Idea:
    name: str
    description: str
    user_value: float
    feasibility: float
    desirability: float
    risk: float

    @property
    def score(self) -> float:
        return (
            self.user_value * 0.40
            + self.feasibility * 0.25
            + self.desirability * 0.25
            - self.risk * 0.10
        )


@dataclass
class Prototype:
    idea_name: str
    fidelity: str
    interactions: list[str]
    assumptions: list[str]


@dataclass
class TestResult:
    participant_id: str
    task: str
    completed: bool
    time_seconds: float
    errors: int
    satisfaction: int
    observation: str


@dataclass
class DesignThinkingProject:
    name: str
    users: list[User] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    problem_statements: list[ProblemStatement] = field(default_factory=list)
    ideas: list[Idea] = field(default_factory=list)
    prototypes: list[Prototype] = field(default_factory=list)
    tests: list[TestResult] = field(default_factory=list)


def section(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def collect_empathy(project: DesignThinkingProject) -> None:
    """Empathy starts with observed behavior instead of assumed requirements."""
    section("EMPATHIZE: OBSERVE PEOPLE IN CONTEXT")

    project.users.extend(
        [
            User(
                "U01",
                "Anika",
                "Operations Analyst",
                "Processes many internal service requests during working hours.",
            ),
            User(
                "U02",
                "Ravi",
                "Finance Analyst",
                "Needs to approve requests while switching between applications.",
            ),
            User(
                "U03",
                "Meera",
                "Team Manager",
                "Monitors request queues and intervenes when work becomes blocked.",
            ),
        ]
    )

    project.observations.extend(
        [
            Observation(
                "U01",
                "Copies request details into a spreadsheet before processing them.",
                "I keep a separate sheet because I cannot easily see what is waiting.",
                "Poor visibility of request state.",
                0.95,
            ),
            Observation(
                "U01",
                "Opens several screens to determine whether required information exists.",
                "I check three places before I know whether I can start.",
                "Information is fragmented.",
                0.90,
            ),
            Observation(
                "U02",
                "Delays approvals when the request lacks context.",
                "I do not want to approve something when I cannot see why it matters.",
                "Approval decisions lack contextual information.",
                0.92,
            ),
            Observation(
                "U03",
                "Contacts analysts directly to discover blocked work.",
                "The dashboard tells me the count, but not why something is stuck.",
                "Status metrics do not explain causes.",
                0.88,
            ),
        ]
    )

    for observation in project.observations:
        print(
            f"{observation.user_id}: {observation.behavior} "
            f"| evidence={observation.evidence_strength:.2f}"
        )


def synthesize_insights(project: DesignThinkingProject) -> None:
    """Affinity-style synthesis converts observations into evidence-backed insights."""
    section("EMPATHIZE -> DEFINE: SYNTHESIZE EVIDENCE")

    grouped: dict[str, list[Observation]] = {}
    for observation in project.observations:
        grouped.setdefault(observation.pain_point, []).append(observation)

    for pain_point, observations in grouped.items():
        confidence = mean(o.evidence_strength for o in observations)
        statement = {
            "Poor visibility of request state.": (
                "Users need a continuously visible representation of request state "
                "because manual tracking creates uncertainty."
            ),
            "Information is fragmented.": (
                "Users need request context in one working view because switching "
                "between systems interrupts processing."
            ),
            "Approval decisions lack contextual information.": (
                "Approvers need decision-relevant context at the point of approval "
                "because missing context creates deliberate delays."
            ),
            "Status metrics do not explain causes.": (
                "Managers need actionable explanations of blocked work rather than "
                "aggregate counts alone."
            ),
        }[pain_point]

        project.insights.append(
            Insight(statement, observations, confidence)
        )
        print(f"\nInsight: {statement}")
        print(f"Confidence: {confidence:.2f}")


def define_problem(project: DesignThinkingProject) -> None:
    """A useful problem statement describes a user, need, insight, and outcome."""
    section("DEFINE: FRAME THE RIGHT PROBLEM")

    project.problem_statements.append(
        ProblemStatement(
            user="Operations and finance staff handling internal requests",
            need="A single contextual workspace for understanding, processing, and approving requests",
            insight=(
                "Observed work is slowed by fragmented information, unclear state, "
                "and insufficient decision context."
            ),
            measurable_outcome=(
                "Reduce median request-processing time while maintaining decision accuracy."
            ),
        )
    )

    for problem in project.problem_statements:
        print(f"User: {problem.user}")
        print(f"Need: {problem.need}")
        print(f"Insight: {problem.insight}")
        print(f"Outcome: {problem.measurable_outcome}")


def ideate(project: DesignThinkingProject) -> None:
    """Ideation deliberately creates alternatives before selecting a solution."""
    section("IDEATE: GENERATE AND EVALUATE OPTIONS")

    project.ideas.extend(
        [
            Idea(
                "Contextual Request Workspace",
                "A unified queue showing state, required information, history, and next action.",
                9,
                8,
                9,
                3,
            ),
            Idea(
                "Decision Summary Panel",
                "A compact approval view that surfaces purpose, amount, evidence, and exceptions.",
                8,
                9,
                8,
                2,
            ),
            Idea(
                "Blocker Explanation Engine",
                "Detects incomplete or blocked requests and explains the blocking condition.",
                8,
                7,
                7,
                5,
            ),
            Idea(
                "Automated Spreadsheet Export",
                "Exports queue data to a standardized spreadsheet for manual tracking.",
                5,
                10,
                5,
                1,
            ),
        ]
    )

    for idea in sorted(project.ideas, key=lambda item: item.score, reverse=True):
        print(f"{idea.name}: score={idea.score:.2f}")


def build_prototype(project: DesignThinkingProject) -> Prototype:
    """A prototype makes assumptions observable without building the full product."""
    section("PROTOTYPE: MAKE ASSUMPTIONS TANGIBLE")

    selected = max(project.ideas, key=lambda idea: idea.score)

    prototype = Prototype(
        idea_name=selected.name,
        fidelity="medium",
        interactions=[
            "Filter requests by state",
            "Open a request and inspect context",
            "See missing information",
            "Approve or return a request",
            "View the reason a request is blocked",
        ],
        assumptions=[
            "Users understand a consolidated request timeline.",
            "A visible next action reduces navigation effort.",
            "Approvers trust concise evidence when source details remain accessible.",
        ],
    )

    project.prototypes.append(prototype)

    print(f"Selected concept: {prototype.idea_name}")
    print(f"Fidelity: {prototype.fidelity}")
    print("Interactions:")
    for interaction in prototype.interactions:
        print(f"  - {interaction}")

    return prototype


def run_usability_test(project: DesignThinkingProject) -> None:
    """Testing measures behavior and records qualitative evidence separately."""
    section("TEST: OBSERVE BEHAVIOR, NOT JUST OPINIONS")

    project.tests.extend(
        [
            TestResult(
                "U01",
                "Find the next request that can be processed",
                True,
                38,
                1,
                4,
                "User immediately used the state filter but hesitated over one status label.",
            ),
            TestResult(
                "U02",
                "Decide whether a request should be approved",
                True,
                46,
                0,
                5,
                "User found amount, purpose, and supporting evidence without leaving the page.",
            ),
            TestResult(
                "U03",
                "Identify why a request is blocked",
                False,
                71,
                3,
                2,
                "User understood that the request was blocked but could not find the missing field.",
            ),
        ]
    )

    for result in project.tests:
        print(
            f"{result.participant_id} | {result.task} | "
            f"completed={result.completed} | time={result.time_seconds:.0f}s | "
            f"errors={result.errors} | satisfaction={result.satisfaction}/5"
        )


def analyze_test_results(project: DesignThinkingProject) -> dict[str, float]:
    section("TEST ANALYSIS: TURN RESULTS INTO DESIGN DECISIONS")

    if not project.tests:
        raise ValueError("No test results are available.")

    completion_rate = mean(result.completed for result in project.tests)
    median_time = sorted(r.time_seconds for r in project.tests)[len(project.tests) // 2]
    average_errors = mean(r.errors for r in project.tests)
    average_satisfaction = mean(r.satisfaction for r in project.tests)

    metrics = {
        "completion_rate": completion_rate,
        "median_time_seconds": median_time,
        "average_errors": average_errors,
        "average_satisfaction": average_satisfaction,
    }

    for name, value in metrics.items():
        print(f"{name}: {value:.2f}")

    return metrics


def validate_test_quality(project: DesignThinkingProject) -> None:
    """Testing quality depends on representative tasks and observable behavior."""
    section("TEST QUALITY VALIDATION")

    if len(project.tests) < 3:
        raise ValueError("At least three participants are required for this demonstration.")

    if any(not 1 <= result.satisfaction <= 5 for result in project.tests):
        raise ValueError("Satisfaction scores must be between 1 and 5.")

    if any(result.time_seconds <= 0 for result in project.tests):
        raise ValueError("Task duration must be positive.")

    print("Test dataset passed structural validation.")


def persist_project(project: DesignThinkingProject, path: Path) -> None:
    """Persisting the design evidence makes decisions traceable across iterations."""
    payload = {
        "name": project.name,
        "users": [user.__dict__ for user in project.users],
        "observations": [observation.__dict__ for observation in project.observations],
        "insights": [
            {
                "statement": insight.statement,
                "confidence": insight.confidence,
                "supporting_observations": [
                    observation.__dict__
                    for observation in insight.supporting_observations
                ],
            }
            for insight in project.insights
        ],
        "problem_statements": [problem.__dict__ for problem in project.problem_statements],
        "ideas": [
            {
                **idea.__dict__,
                "score": idea.score,
            }
            for idea in project.ideas
        ],
        "prototypes": [prototype.__dict__ for prototype in project.prototypes],
        "tests": [result.__dict__ for result in project.tests],
    }

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def demonstrate_iteration(project: DesignThinkingProject) -> None:
    """The cycle is iterative: test evidence changes the next prototype."""
    section("ITERATION: RETURN TO THE APPROPRIATE STAGE")

    blocked_task = next(
        result
        for result in project.tests
        if not result.completed
    )

    print(f"Observed failure: {blocked_task.observation}")
    print(
        "Design response: expose the exact missing field directly inside the "
        "blocked-request state instead of requiring another navigation step."
    )

    updated_assumption = (
        "When a request is blocked, the interface must expose the blocking field "
        "and the action required to resolve it."
    )

    project.prototypes[-1].assumptions.append(updated_assumption)
    print(f"New prototype assumption: {updated_assumption}")


def run_regression_checks(project: DesignThinkingProject) -> None:
    """Small executable checks protect the integrity of the design dataset."""
    section("REGRESSION CHECKS")

    assert project.observations, "Empathy evidence must exist."
    assert project.insights, "Insights must be grounded in observations."
    assert project.problem_statements, "A defined problem must exist."
    assert project.ideas, "Ideation must produce alternatives."
    assert project.prototypes, "A prototype must exist."
    assert project.tests, "The prototype must be tested."

    for insight in project.insights:
        assert insight.supporting_observations
        assert 0 <= insight.confidence <= 1

    for idea in project.ideas:
        assert 0 <= idea.score <= 10

    print("All design-thinking integrity checks passed.")


def main() -> None:
    project = DesignThinkingProject(
        name="Internal Request Processing Experience"
    )

    collect_empathy(project)
    synthesize_insights(project)
    define_problem(project)
    ideate(project)
    build_prototype(project)
    run_usability_test(project)
    validate_test_quality(project)
    metrics = analyze_test_results(project)
    demonstrate_iteration(project)
    run_regression_checks(project)

    with tempfile.TemporaryDirectory() as temporary_directory:
        output_path = Path(temporary_directory) / "design_thinking_evidence.json"
        persist_project(project, output_path)

        loaded = json.loads(output_path.read_text(encoding="utf-8"))
        print(f"\nEvidence persisted successfully: {output_path.name}")
        print(f"Stored observations: {len(loaded['observations'])}")
        print(f"Stored ideas: {len(loaded['ideas'])}")
        print(f"Stored test results: {len(loaded['tests'])}")

    section("DESIGN DECISION")
    if metrics["completion_rate"] < 1.0:
        print(
            "The prototype should be revised before treating the workflow as "
            "production-ready because at least one task was not completed."
        )
    else:
        print("All observed tasks completed successfully.")


if __name__ == "__main__":
    main()
