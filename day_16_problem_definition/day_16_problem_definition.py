"""
Problem Definition: problem statements, symptoms vs root causes, problem framing,
and problem boundaries.

This standalone study file progresses from basic problem-definition concepts to
structured diagnosis, causal analysis, boundary definition, assumptions,
constraints, stakeholder analysis, measurable objectives, prioritization,
validation, and an industry-style case study.

Run:
    python problem_definition.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Optional
import math
import statistics
import textwrap


# ---------------------------------------------------------------------------
# 1. FOUNDATIONS
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


class ProblemType(Enum):
    """Useful classifications for deciding how a problem should be framed."""

    PERFORMANCE = "performance"
    QUALITY = "quality"
    RELIABILITY = "reliability"
    COST = "cost"
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    CUSTOMER_EXPERIENCE = "customer experience"
    GROWTH = "growth"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    TECHNICAL = "technical"


@dataclass
class ProblemStatement:
    """
    A structured representation of a problem.

    A strong problem statement describes an undesirable current condition,
    affected users or systems, measurable evidence, and consequences without
    prematurely prescribing a solution.
    """

    affected_actor: str
    current_condition: str
    measurable_gap: str
    consequence: str
    evidence: list[str] = field(default_factory=list)
    timeframe: Optional[str] = None
    location_or_scope: Optional[str] = None

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.affected_actor.strip():
            errors.append("Affected actor is missing.")
        if not self.current_condition.strip():
            errors.append("Current condition is missing.")
        if not self.measurable_gap.strip():
            errors.append("Measurable gap is missing.")
        if not self.consequence.strip():
            errors.append("Consequence is missing.")
        if not self.evidence:
            errors.append("At least one evidence item is required.")

        return errors

    def render(self) -> str:
        scope = f" Scope: {self.location_or_scope}." if self.location_or_scope else ""
        time = f" Timeframe: {self.timeframe}." if self.timeframe else ""

        return (
            f"{self.affected_actor} is experiencing {self.current_condition}. "
            f"The measurable gap is {self.measurable_gap}. "
            f"This matters because {self.consequence}.{scope}{time}"
        )


def demonstrate_basic_problem_statement() -> None:
    print_section("1. Problem statement fundamentals")

    weak = "The website needs a better checkout system."

    strong = ProblemStatement(
        affected_actor="Online customers",
        current_condition="abandon purchases during checkout",
        measurable_gap="checkout completion is 61% compared with a target of 75%",
        consequence="lost completed orders and avoidable support contacts",
        evidence=[
            "Checkout analytics show a 39% abandonment rate.",
            "Session analysis shows repeated validation failures.",
            "Customer interviews mention uncertainty about delivery charges.",
        ],
        timeframe="the last three months",
        location_or_scope="the web checkout flow",
    )

    print("Weak statement:")
    print(weak)

    print("\nStructured statement:")
    print(strong.render())

    print("\nValidation:")
    errors = strong.validate()
    print("Valid" if not errors else errors)


# ---------------------------------------------------------------------------
# 2. SYMPTOMS, PROBLEMS, ROOT CAUSES, AND CONSEQUENCES
# ---------------------------------------------------------------------------

@dataclass
class CausalNode:
    name: str
    kind: str
    parent: Optional["CausalNode"] = None
    children: list["CausalNode"] = field(default_factory=list)

    def add_child(self, child: "CausalNode") -> None:
        child.parent = self
        self.children.append(child)


def print_causal_tree(node: CausalNode, level: int = 0) -> None:
    print("  " * level + f"- [{node.kind}] {node.name}")
    for child in node.children:
        print_causal_tree(child, level + 1)


def demonstrate_symptom_root_cause() -> None:
    print_section("2. Symptoms versus root causes")

    root = CausalNode(
        "Customer support backlog increased",
        "observable problem",
    )

    symptom = CausalNode(
        "Average response time increased from 6 hours to 21 hours",
        "symptom",
    )

    operational_cause = CausalNode(
        "Tickets are being routed to the wrong queue",
        "contributing cause",
    )

    process_cause = CausalNode(
        "Routing rules were copied from an obsolete service taxonomy",
        "root cause candidate",
    )

    measurement_cause = CausalNode(
        "No weekly review exists for routing accuracy",
        "systemic cause",
    )

    root.add_child(symptom)
    symptom.add_child(operational_cause)
    operational_cause.add_child(process_cause)
    process_cause.add_child(measurement_cause)

    print_causal_tree(root)

    print(
        "\nImportant distinction:\n"
        "A symptom is evidence of an undesirable condition. A root cause is a "
        "factor whose removal or correction would materially reduce the condition. "
        "A single problem can have multiple interacting causes."
    )


# ---------------------------------------------------------------------------
# 3. FIVE WHYS
# ---------------------------------------------------------------------------

@dataclass
class WhyStep:
    question: str
    answer: str


def five_whys(
    initial_problem: str,
    answers: Iterable[str],
) -> list[WhyStep]:
    """
    Apply a simple Five Whys chain.

    Five Whys is not proof of causality. It is a disciplined questioning method
    that helps move from an observed condition toward potentially actionable causes.
    """
    steps: list[WhyStep] = []
    current = initial_problem

    for answer in answers:
        question = f"Why does this occur? Because {current}."
        steps.append(WhyStep(question=question, answer=answer))
        current = answer

    return steps


def demonstrate_five_whys() -> None:
    print_section("3. Five Whys")

    initial = "Orders are frequently shipped late."

    answers = [
        "Warehouse picking starts later than the planned release time.",
        "Picking work waits for manual payment-status confirmation.",
        "Payment exceptions are checked in a separate system.",
        "The two systems do not exchange exception status automatically.",
        "The integration was never designed for exception-state synchronization.",
    ]

    steps = five_whys(initial, answers)

    current = initial
    for index, step in enumerate(steps, start=1):
        print(f"Why {index}: {step.question}")
        print(f"Answer: {step.answer}")
        current = step.answer

    print(
        "\nThe fifth answer is a root-cause candidate, not automatically a proven "
        "root cause. Evidence and controlled investigation are still required."
    )


# ---------------------------------------------------------------------------
# 4. PROBLEM FRAMING
# ---------------------------------------------------------------------------

@dataclass
class ProblemFrame:
    actor: str
    desired_outcome: str
    current_state: str
    gap: str
    context: str
    constraints: list[str]
    assumptions: list[str]
    exclusions: list[str]
    success_metrics: dict[str, str]

    def render(self) -> str:
        lines = [
            f"Actor: {self.actor}",
            f"Desired outcome: {self.desired_outcome}",
            f"Current state: {self.current_state}",
            f"Gap: {self.gap}",
            f"Context: {self.context}",
            "Constraints:",
        ]

        lines.extend(f"  - {item}" for item in self.constraints)

        lines.append("Assumptions:")
        lines.extend(f"  - {item}" for item in self.assumptions)

        lines.append("Exclusions:")
        lines.extend(f"  - {item}" for item in self.exclusions)

        lines.append("Success metrics:")
        lines.extend(f"  - {name}: {definition}" for name, definition in self.success_metrics.items())

        return "\n".join(lines)


def demonstrate_problem_framing() -> ProblemFrame:
    print_section("4. Problem framing")

    frame = ProblemFrame(
        actor="Students using a university examination portal",
        desired_outcome="complete legitimate submissions before the deadline",
        current_state="submissions sometimes fail or remain pending near peak traffic",
        gap="successful submission rate falls below the operational target during peak periods",
        context="online examinations with concentrated submission activity",
        constraints=[
            "Existing authentication must remain unchanged.",
            "Exam deadlines cannot be extended automatically.",
            "Student records must remain protected.",
            "The university has a fixed infrastructure budget.",
        ],
        assumptions=[
            "The examination rules are correct.",
            "Student internet access is outside institutional control.",
            "Submission events are timestamped accurately.",
        ],
        exclusions=[
            "Changing examination policy.",
            "Replacing the student identity system.",
            "Diagnosing individual students' home networks.",
        ],
        success_metrics={
            "submission success rate": "successful final submissions divided by attempted final submissions",
            "p95 submission latency": "95th percentile time required to acknowledge a submission",
            "duplicate submission rate": "duplicate final submissions per 1,000 attempts",
        },
    )

    print(frame.render())
    return frame


# ---------------------------------------------------------------------------
# 5. PROBLEM BOUNDARIES
# ---------------------------------------------------------------------------

@dataclass
class Boundary:
    inside: list[str]
    outside: list[str]

    def classify(self, item: str) -> str:
        if item in self.inside:
            return "INSIDE"
        if item in self.outside:
            return "OUTSIDE"
        return "UNDEFINED"

    def report(self) -> None:
        print("Inside the problem boundary:")
        for item in self.inside:
            print(f"  [IN]  {item}")

        print("\nOutside the problem boundary:")
        for item in self.outside:
            print(f"  [OUT] {item}")

        print("\nUnclassified items should not silently be treated as either inside or outside.")


def demonstrate_boundaries() -> Boundary:
    print_section("5. Problem boundaries")

    boundary = Boundary(
        inside=[
            "submission API",
            "submission database",
            "queueing mechanism",
            "retry logic",
            "portal validation",
        ],
        outside=[
            "student home Wi-Fi",
            "university examination policy",
            "internet service providers",
            "student device hardware",
        ],
    )

    boundary.report()

    print("\nClassification examples:")
    for item in [
        "submission API",
        "student home Wi-Fi",
        "examination policy",
        "unclassified third-party payment service",
    ]:
        print(f"{item}: {boundary.classify(item)}")

    return boundary


# ---------------------------------------------------------------------------
# 6. FACTS, ASSUMPTIONS, HYPOTHESES, AND OPINIONS
# ---------------------------------------------------------------------------

@dataclass
class EvidenceItem:
    statement: str
    evidence_type: str
    confidence: float
    source: str

    def validate(self) -> bool:
        return 0.0 <= self.confidence <= 1.0


def demonstrate_evidence_quality() -> None:
    print_section("6. Facts, assumptions, hypotheses, and opinions")

    evidence = [
        EvidenceItem(
            "Checkout abandonment was 39% in August.",
            "measured fact",
            0.98,
            "analytics database",
        ),
        EvidenceItem(
            "Customers are confused by delivery charges.",
            "interview observation",
            0.78,
            "20 customer interviews",
        ),
        EvidenceItem(
            "A new checkout page will solve abandonment.",
            "hypothesis",
            0.35,
            "untested product proposal",
        ),
        EvidenceItem(
            "The checkout should look simpler.",
            "opinion",
            0.20,
            "stakeholder preference",
        ),
    ]

    for item in evidence:
        print(
            f"[{item.evidence_type.upper()}] {item.statement}\n"
            f"  confidence={item.confidence:.0%}, source={item.source}"
        )

    print(
        "\nA disciplined problem definition keeps measured observations separate "
        "from assumptions and proposed solutions."
    )


# ---------------------------------------------------------------------------
# 7. CONSTRAINTS AND ASSUMPTIONS
# ---------------------------------------------------------------------------

@dataclass
class Constraint:
    name: str
    category: str
    description: str
    hard: bool = True


def demonstrate_constraints() -> None:
    print_section("7. Constraints")

    constraints = [
        Constraint("Deadline", "time", "The service must be stabilized before the next exam cycle."),
        Constraint("Budget", "financial", "Infrastructure spending cannot exceed the approved allocation."),
        Constraint("Privacy", "legal/security", "Student data cannot be exposed to unauthorized parties."),
        Constraint("Compatibility", "technical", "The existing identity provider must continue to work."),
        Constraint("Capacity", "operational", "The system must support peak submission bursts."),
        Constraint("Scope", "organizational", "The project does not redesign university examination policy."),
    ]

    for constraint in constraints:
        level = "HARD" if constraint.hard else "SOFT"
        print(f"[{level}] {constraint.category}: {constraint.name}")
        print(f"       {constraint.description}")

    print(
        "\nA constraint is not automatically a root cause. It describes a condition "
        "that limits the feasible solution space."
    )


# ---------------------------------------------------------------------------
# 8. MEASURABLE PROBLEM DEFINITION
# ---------------------------------------------------------------------------

@dataclass
class Metric:
    name: str
    baseline: float
    target: float
    unit: str
    higher_is_better: bool

    def gap(self) -> float:
        return self.target - self.baseline

    def target_reached(self, actual: float) -> bool:
        if self.higher_is_better:
            return actual >= self.target
        return actual <= self.target


def demonstrate_metrics() -> None:
    print_section("8. Turning vague problems into measurable gaps")

    metrics = [
        Metric("checkout completion rate", 0.61, 0.75, "%", True),
        Metric("p95 checkout latency", 8.4, 3.0, "seconds", False),
        Metric("support contacts per 1,000 orders", 92, 55, "contacts", False),
    ]

    for metric in metrics:
        print(
            f"{metric.name}: baseline={metric.baseline}, "
            f"target={metric.target}, unit={metric.unit}, gap={metric.gap():.2f}"
        )

    print("\nExample target checks:")
    actual_values = {
        "checkout completion rate": 0.77,
        "p95 checkout latency": 3.4,
        "support contacts per 1,000 orders": 51,
    }

    for metric in metrics:
        actual = actual_values[metric.name]
        status = "TARGET MET" if metric.target_reached(actual) else "TARGET NOT MET"
        print(f"{metric.name}: actual={actual} -> {status}")


# ---------------------------------------------------------------------------
# 9. PROBLEM DECOMPOSITION
# ---------------------------------------------------------------------------

@dataclass
class Subproblem:
    name: str
    parent: Optional[str]
    measurable: bool
    independent_enough: bool


def demonstrate_decomposition() -> None:
    print_section("9. Problem decomposition")

    root = "Low checkout completion rate"

    subproblems = [
        Subproblem("Payment authorization failures", root, True, True),
        Subproblem("Unexpected delivery cost", root, True, True),
        Subproblem("Slow page response", root, True, True),
        Subproblem("Confusing error messages", root, True, True),
        Subproblem("Inventory changed during checkout", root, True, False),
    ]

    print(f"Root problem: {root}")

    for subproblem in subproblems:
        independence = "mostly independent" if subproblem.independent_enough else "interacting with other causes"
        measurement = "measurable" if subproblem.measurable else "needs operational definition"
        print(f"  - {subproblem.name}: {measurement}, {independence}")

    print(
        "\nGood decomposition reduces complexity without pretending that interacting "
        "subproblems are completely independent."
    )


# ---------------------------------------------------------------------------
# 10. PARETO ANALYSIS
# ---------------------------------------------------------------------------

def pareto_analysis(causes: dict[str, int]) -> list[tuple[str, int, float]]:
    total = sum(causes.values())
    if total <= 0:
        return []

    ordered = sorted(causes.items(), key=lambda pair: pair[1], reverse=True)

    result = []
    cumulative = 0

    for name, count in ordered:
        cumulative += count
        result.append((name, count, cumulative / total))

    return result


def demonstrate_pareto() -> None:
    print_section("10. Pareto-style cause analysis")

    causes = {
        "payment failures": 410,
        "delivery-price confusion": 230,
        "slow response": 170,
        "validation errors": 110,
        "miscellaneous": 80,
    }

    result = pareto_analysis(causes)

    for name, count, cumulative in result:
        print(f"{name:30} {count:4} incidents | cumulative={cumulative:6.2%}")

    print(
        "\nPareto analysis helps identify concentration. It does not prove that the "
        "largest category is the deepest causal mechanism."
    )


# ---------------------------------------------------------------------------
# 11. CAUSAL HYPOTHESES
# ---------------------------------------------------------------------------

@dataclass
class Hypothesis:
    statement: str
    test: str
    supporting_evidence: list[str]
    disconfirming_evidence: list[str]

    def status(self) -> str:
        if self.supporting_evidence and not self.disconfirming_evidence:
            return "supported but not proven"
        if self.disconfirming_evidence:
            return "requires revision"
        return "untested"


def demonstrate_hypotheses() -> None:
    print_section("11. Causal hypotheses")

    hypothesis = Hypothesis(
        statement="Payment failures materially contribute to checkout abandonment.",
        test="Compare abandonment after payment errors with abandonment after successful authorization.",
        supporting_evidence=[
            "Payment-error sessions have much higher abandonment.",
            "The effect appears across multiple weeks.",
        ],
        disconfirming_evidence=[],
    )

    print(f"Hypothesis: {hypothesis.statement}")
    print(f"Test: {hypothesis.test}")
    print(f"Status: {hypothesis.status()}")

    print("\nSupporting evidence:")
    for item in hypothesis.supporting_evidence:
        print(f"  + {item}")

    print(
        "\nCorrelation can support a hypothesis but does not automatically establish "
        "causation. Experiments, natural experiments, process tracing, or controlled "
        "comparisons may be necessary."
    )


# ---------------------------------------------------------------------------
# 12. ROOT-CAUSE VALIDATION
# ---------------------------------------------------------------------------

def compare_before_after(
    before: list[float],
    after: list[float],
) -> dict[str, float]:
    if not before or not after:
        raise ValueError("Both samples must contain at least one observation.")

    before_mean = statistics.mean(before)
    after_mean = statistics.mean(after)

    return {
        "before_mean": before_mean,
        "after_mean": after_mean,
        "absolute_change": after_mean - before_mean,
        "relative_change": (
            (after_mean - before_mean) / before_mean
            if before_mean != 0
            else math.nan
        ),
    }


def demonstrate_validation() -> None:
    print_section("12. Testing a root-cause intervention")

    before = [39, 41, 38, 42, 40, 39, 43]
    after = [31, 29, 30, 32, 28, 31, 30]

    comparison = compare_before_after(before, after)

    for key, value in comparison.items():
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")

    print(
        "\nA before/after change is informative but can be confounded by seasonality, "
        "traffic mix, concurrent changes, measurement changes, and regression to the mean."
    )


# ---------------------------------------------------------------------------
# 13. BOUNDARY FAILURE MODES
# ---------------------------------------------------------------------------

def boundary_failure_examples() -> None:
    print_section("13. Common boundary failures")

    failures = {
        "too broad": "Improve the entire university digital experience.",
        "too narrow": "Fix the color of the submit button.",
        "solution disguised as problem": "Build a new submission service.",
        "cause disguised as problem": "The database is too slow.",
        "metric without user impact": "Increase API throughput.",
        "unbounded responsibility": "Make sure no student ever has an internet problem.",
    }

    for category, example in failures.items():
        print(f"{category}: {example}")


# ---------------------------------------------------------------------------
# 14. STAKEHOLDER PERSPECTIVES
# ---------------------------------------------------------------------------

@dataclass
class Stakeholder:
    name: str
    role: str
    concern: str
    influence: str


def demonstrate_stakeholders() -> None:
    print_section("14. Stakeholder perspectives")

    stakeholders = [
        Stakeholder("Student", "primary user", "successful submission before deadline", "high"),
        Stakeholder("Faculty", "assessment owner", "valid and traceable submissions", "high"),
        Stakeholder("IT operations", "system operator", "availability and maintainability", "high"),
        Stakeholder("Security team", "risk owner", "confidentiality and integrity", "high"),
        Stakeholder("Finance", "budget owner", "controlled infrastructure cost", "medium"),
    ]

    for stakeholder in stakeholders:
        print(
            f"{stakeholder.name:18} | {stakeholder.role:20} | "
            f"{stakeholder.concern:45} | influence={stakeholder.influence}"
        )

    print(
        "\nDifferent stakeholders may describe the same underlying problem differently. "
        "Problem definition should preserve the underlying condition while recording "
        "these different perspectives."
    )


# ---------------------------------------------------------------------------
# 15. SOLUTION BIAS
# ---------------------------------------------------------------------------

def detect_solution_bias(statement: str) -> list[str]:
    solution_verbs = [
        "build",
        "develop",
        "implement",
        "deploy",
        "automate",
        "replace",
        "migrate",
        "buy",
    ]

    lowered = statement.lower()

    return [
        verb
        for verb in solution_verbs
        if verb in lowered
    ]


def demonstrate_solution_bias() -> None:
    print_section("15. Detecting solution bias")

    statements = [
        "Build a faster API.",
        "Students cannot reliably complete final submission during peak traffic.",
        "Implement a new database.",
        "Payment confirmation is delayed and causes users to retry.",
    ]

    for statement in statements:
        detected = detect_solution_bias(statement)
        print(f"{statement}")
        print(f"  possible solution-language terms: {detected or 'none'}")

    print(
        "\nA solution can be appropriate, but it should normally be selected after "
        "the problem, causes, constraints, and success criteria have been understood."
    )


# ---------------------------------------------------------------------------
# 16. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print_section("16. Edge cases and subtle situations")

    cases = [
        (
            "Multiple root causes",
            "A service outage may result from capacity limits, faulty deployment, "
            "dependency failure, and weak monitoring simultaneously.",
        ),
        (
            "One cause, multiple symptoms",
            "A broken identity dependency can produce login failures, API failures, "
            "support tickets, and lost transactions.",
        ),
        (
            "Changing baseline",
            "A problem can appear smaller or larger because traffic, users, or "
            "measurement definitions changed.",
        ),
        (
            "Local optimum",
            "Improving one metric can damage another, such as reducing latency by "
            "reducing validation that protects data quality.",
        ),
        (
            "Rare severe event",
            "Average performance can look healthy while a low-frequency safety "
            "failure remains unacceptable.",
        ),
        (
            "External cause",
            "The root cause may sit outside the project boundary even though the "
            "project must mitigate its effects.",
        ),
        (
            "Unknown cause",
            "A valid problem definition can exist before the root cause is known.",
        ),
    ]

    for name, description in cases:
        print(f"{name}: {description}")


# ---------------------------------------------------------------------------
# 17. QUALITY CHECKLIST
# ---------------------------------------------------------------------------

def problem_definition_checklist(frame: ProblemFrame) -> dict[str, bool]:
    return {
        "affected actor identified": bool(frame.actor.strip()),
        "current state described": bool(frame.current_state.strip()),
        "desired state described": bool(frame.desired_outcome.strip()),
        "gap defined": bool(frame.gap.strip()),
        "context documented": bool(frame.context.strip()),
        "constraints documented": bool(frame.constraints),
        "assumptions documented": bool(frame.assumptions),
        "exclusions documented": bool(frame.exclusions),
        "success metrics defined": bool(frame.success_metrics),
    }


def demonstrate_checklist(frame: ProblemFrame) -> None:
    print_section("17. Problem-definition quality checklist")

    checklist = problem_definition_checklist(frame)

    for criterion, passed in checklist.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {criterion}")


# ---------------------------------------------------------------------------
# 18. ADVANCED CASE STUDY
# ---------------------------------------------------------------------------

@dataclass
class IncidentRecord:
    date: str
    attempts: int
    successful: int
    payment_errors: int
    validation_errors: int
    timeout_errors: int
    duplicate_submissions: int

    def success_rate(self) -> float:
        return self.successful / self.attempts if self.attempts else 0.0

    def failure_count(self) -> int:
        return self.attempts - self.successful


def build_case_study_data() -> list[IncidentRecord]:
    return [
        IncidentRecord("2026-08-01", 12000, 11160, 330, 210, 240, 18),
        IncidentRecord("2026-08-02", 12100, 11253, 340, 195, 312, 20),
        IncidentRecord("2026-08-03", 11900, 11007, 420, 180, 293, 19),
        IncidentRecord("2026-08-04", 12500, 11375, 510, 205, 410, 24),
        IncidentRecord("2026-08-05", 12800, 11456, 570, 220, 554, 28),
        IncidentRecord("2026-08-06", 13000, 11570, 610, 230, 590, 31),
        IncidentRecord("2026-08-07", 13200, 11616, 640, 245, 699, 35),
    ]


def analyze_case_study(data: list[IncidentRecord]) -> dict[str, float]:
    total_attempts = sum(item.attempts for item in data)
    total_successes = sum(item.successful for item in data)
    total_payment_errors = sum(item.payment_errors for item in data)
    total_validation_errors = sum(item.validation_errors for item in data)
    total_timeouts = sum(item.timeout_errors for item in data)
    total_duplicates = sum(item.duplicate_submissions for item in data)

    return {
        "attempts": total_attempts,
        "successes": total_successes,
        "success_rate": total_successes / total_attempts,
        "failure_rate": 1 - total_successes / total_attempts,
        "payment_error_rate": total_payment_errors / total_attempts,
        "validation_error_rate": total_validation_errors / total_attempts,
        "timeout_rate": total_timeouts / total_attempts,
        "duplicate_rate": total_duplicates / total_attempts,
    }


def demonstrate_case_study() -> None:
    print_section("18. Industry-style case study: examination submission reliability")

    data = build_case_study_data()
    analysis = analyze_case_study(data)

    for key, value in analysis.items():
        if key in {"attempts", "successes"}:
            print(f"{key}: {value:,.0f}")
        else:
            print(f"{key}: {value:.2%}")

    print("\nDaily observations:")
    for record in data:
        print(
            f"{record.date}: success={record.success_rate():.2%}, "
            f"payments={record.payment_errors}, "
            f"validation={record.validation_errors}, "
            f"timeouts={record.timeout_errors}, "
            f"duplicates={record.duplicate_submissions}"
        )

    print(
        "\nProblem framing decision:\n"
        "The observed problem is submission reliability during concentrated "
        "traffic. The data alone does not justify immediately declaring a specific "
        "component the root cause. Payment errors, timeouts, validation behavior, "
        "and their interactions should be investigated."
    )


# ---------------------------------------------------------------------------
# 19. PRIORITIZATION WITHOUT CONFUSING PRIORITY WITH CAUSALITY
# ---------------------------------------------------------------------------

@dataclass
class InvestigationCandidate:
    name: str
    impact: float
    uncertainty: float
    controllability: float

    def investigation_priority(self) -> float:
        return self.impact * self.uncertainty * self.controllability


def demonstrate_investigation_prioritization() -> None:
    print_section("19. Prioritizing investigation work")

    candidates = [
        InvestigationCandidate("payment authorization failures", 0.90, 0.40, 0.80),
        InvestigationCandidate("submission timeouts", 0.85, 0.75, 0.90),
        InvestigationCandidate("validation errors", 0.45, 0.50, 0.90),
        InvestigationCandidate("student home Wi-Fi", 0.70, 0.80, 0.10),
    ]

    for candidate in candidates:
        print(
            f"{candidate.name:35} "
            f"impact={candidate.impact:.2f} "
            f"uncertainty={candidate.uncertainty:.2f} "
            f"controllability={candidate.controllability:.2f} "
            f"investigation_value={candidate.investigation_priority():.3f}"
        )

    print(
        "\nThis calculation is an investigation heuristic, not a claim about "
        "causality or a universal prioritization formula."
    )


# ---------------------------------------------------------------------------
# 20. PERFORMANCE AND IMPLEMENTATION CONSIDERATIONS
# ---------------------------------------------------------------------------

def demonstrate_complexity() -> None:
    print_section("20. Computational perspective")

    records = build_case_study_data()

    # A single pass computes totals in O(n) time and O(1) additional space
    # apart from the input collection.
    analysis = analyze_case_study(records)

    print(f"Analyzed {len(records)} records in one linear pass.")
    print(f"Failure rate: {analysis['failure_rate']:.2%}")

    # Sorting causes by frequency costs O(k log k), where k is the number of causes.
    causes = {
        "payment": 3080,
        "validation": 1485,
        "timeouts": 3098,
        "duplicates": 175,
    }

    ordered = sorted(causes.items(), key=lambda item: item[1], reverse=True)

    print("Sorted causes:")
    for name, count in ordered:
        print(f"  {name}: {count}")


# ---------------------------------------------------------------------------
# 21. SECURITY CONSIDERATIONS
# ---------------------------------------------------------------------------

def demonstrate_security_considerations() -> None:
    print_section("21. Security and privacy considerations")

    security_rules = [
        "Do not expose personal data merely to obtain diagnostic evidence.",
        "Separate operational logs from sensitive student records.",
        "Apply least privilege to diagnostic datasets.",
        "Record who accessed sensitive evidence.",
        "Redact identifiers when aggregate evidence is sufficient.",
        "Treat manipulated metrics as a possible attack or governance problem.",
        "Do not define a security problem only as a technical symptom.",
    ]

    for rule in security_rules:
        print(f"- {rule}")


# ---------------------------------------------------------------------------
# 22. DEBUGGING A BAD PROBLEM DEFINITION
# ---------------------------------------------------------------------------

def diagnose_problem_statement(statement: ProblemStatement) -> list[str]:
    issues: list[str] = []

    text = statement.render().lower()

    if any(
        word in text
        for word in ["build ", "implement ", "deploy ", "replace ", "automate "]
    ):
        issues.append("Possible solution bias detected.")

    if not statement.evidence:
        issues.append("No evidence supplied.")

    if "%" not in statement.measurable_gap and not any(
        character.isdigit() for character in statement.measurable_gap
    ):
        issues.append("The measurable gap may not contain a quantifiable baseline or target.")

    return issues


def demonstrate_debugging() -> None:
    print_section("22. Debugging a weak problem definition")

    weak = ProblemStatement(
        affected_actor="the company",
        current_condition="has a bad application",
        measurable_gap="bad performance",
        consequence="users are unhappy",
        evidence=[],
    )

    print("Statement:")
    print(weak.render())

    print("\nDetected issues:")
    for issue in diagnose_problem_statement(weak):
        print(f"- {issue}")

    print(
        "\nThe purpose of diagnosis is not to make wording complicated. It is to "
        "make the problem observable, bounded, testable, and decision-useful."
    )


# ---------------------------------------------------------------------------
# 23. COMPLETE WORKFLOW
# ---------------------------------------------------------------------------

def problem_definition_workflow() -> list[str]:
    """
    A reusable high-level workflow.

    1. Observe the undesirable condition.
    2. Identify affected actors.
    3. Establish evidence and baseline.
    4. Define the desired condition.
    5. State the measurable gap.
    6. Identify context.
    7. Separate symptoms from causal hypotheses.
    8. Investigate causes.
    9. Define boundaries and exclusions.
    10. Document constraints and assumptions.
    11. Define success metrics.
    12. Validate the framing with stakeholders and evidence.
    """
    return [
        "Observe",
        "Identify",
        "Measure",
        "Define desired state",
        "Frame the gap",
        "Separate symptoms from causes",
        "Investigate",
        "Set boundaries",
        "Document assumptions and constraints",
        "Define success metrics",
        "Validate",
    ]


def demonstrate_workflow() -> None:
    print_section("23. End-to-end workflow")

    for number, stage in enumerate(problem_definition_workflow(), start=1):
        print(f"{number:2}. {stage}")


# ---------------------------------------------------------------------------
# 24. PRACTICAL EXAMPLES
# ---------------------------------------------------------------------------

def practical_examples() -> None:
    print_section("24. Practical transformations")

    examples = [
        (
            "Weak: The app is slow.",
            "Better: Mobile users experience a p95 response time of 6.8 seconds "
            "on the order-history endpoint, above the 2.5-second operational target.",
        ),
        (
            "Weak: Customers hate support.",
            "Better: First-contact resolution is 54%, causing 46% of support cases "
            "to require at least one additional interaction.",
        ),
        (
            "Weak: The database needs replacement.",
            "Better: Order queries exceed the latency target during peak load, "
            "and the evidence must determine whether indexing, query design, "
            "capacity, locking, or architecture is responsible.",
        ),
        (
            "Weak: Build an AI fraud detector.",
            "Better: Fraud losses have increased while manual review capacity remains "
            "fixed; the investigation must determine which transaction patterns "
            "are associated with preventable losses.",
        ),
    ]

    for weak, better in examples:
        print(weak)
        print(better)
        print()


# ---------------------------------------------------------------------------
# 25. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("PROBLEM DEFINITION STUDY PROGRAM")
    print(
        "Topic: problem statements, symptoms versus root causes, "
        "problem framing, and problem boundaries"
    )

    demonstrate_basic_problem_statement()
    demonstrate_symptom_root_cause()
    demonstrate_five_whys()
    frame = demonstrate_problem_framing()
    demonstrate_boundaries()
    demonstrate_evidence_quality()
    demonstrate_constraints()
    demonstrate_metrics()
    demonstrate_decomposition()
    demonstrate_pareto()
    demonstrate_hypotheses()
    demonstrate_validation()
    boundary_failure_examples()
    demonstrate_stakeholders()
    demonstrate_solution_bias()
    demonstrate_edge_cases()
    demonstrate_checklist(frame)
    demonstrate_case_study()
    demonstrate_investigation_prioritization()
    demonstrate_complexity()
    demonstrate_security_considerations()
    demonstrate_debugging()
    demonstrate_workflow()
    practical_examples()

    print_section("FINAL PRACTICE EXERCISE")

    exercise = ProblemStatement(
        affected_actor="Retail customers",
        current_condition="abandon carts before completing payment",
        measurable_gap="conversion is 58% while the agreed baseline target is 70%",
        consequence="orders and expected revenue are lost",
        evidence=[
            "Analytics show a high exit rate on the payment step.",
            "Payment-error sessions have higher abandonment.",
            "The effect is concentrated during evening traffic peaks.",
        ],
        timeframe="the previous six weeks",
        location_or_scope="the web purchase flow",
    )

    print("Practice problem statement:")
    print(exercise.render())

    print("\nValidation:")
    print("PASS" if not exercise.validate() else exercise.validate())

    print(
        "\nKey discipline demonstrated by this program: define what is happening "
        "before deciding why it is happening, and define why it is happening "
        "before selecting what should be built or changed."
    )


if __name__ == "__main__":
    main()
