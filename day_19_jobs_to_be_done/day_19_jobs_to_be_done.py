"""
Jobs To Be Done (JTBD)
======================

A standalone study and executable demonstration of the Jobs To Be Done framework.

The program progresses from:
1. Basic JTBD terminology
2. Functional, emotional, and social jobs
3. Job stories
4. Job statements and desired outcomes
5. Job decomposition
6. Interview-style evidence
7. Opportunity scoring
8. Persona versus job-oriented thinking
9. Switching and competing solutions
10. Job clustering
11. A small product-discovery case study
12. Edge cases and validation
13. A reusable JTBD analysis engine
14. A simple prioritization simulation

JTBD is a product-discovery framework. It focuses on the progress a person
is trying to make in a particular circumstance rather than treating a
demographic persona as the primary unit of analysis.

The examples use fictional research data so the program can run without
external files or services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import math
import re


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL TERMINOLOGY
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_subsection(title: str) -> None:
    print(f"\n--- {title} ---")


print_section("1. JTBD FUNDAMENTALS")

print(
    """
Jobs To Be Done (JTBD) studies the progress people are trying to make
in a particular circumstance.

A job is not simply a product feature and it is not necessarily a task.

Examples:
    Weak feature statement:
        "The application needs a calendar."

    Functional job:
        "Organize upcoming commitments so I know what requires attention."

    Emotional job:
        "Feel confident that I have not forgotten something important."

    Social job:
        "Appear reliable when coordinating commitments with other people."

The framework is useful because several different products can compete
for the same job. A person may use software, a spreadsheet, a notebook,
a colleague, memory, or no solution at all to accomplish the same job.
"""
)


# ---------------------------------------------------------------------------
# 2. CORE JOB TYPES
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Job:
    title: str
    functional: str
    emotional: str
    social: str
    circumstance: str
    desired_outcome: str

    def describe(self) -> None:
        print(f"Job: {self.title}")
        print(f"  Circumstance: {self.circumstance}")
        print(f"  Functional:   {self.functional}")
        print(f"  Emotional:     {self.emotional}")
        print(f"  Social:        {self.social}")
        print(f"  Outcome:       {self.desired_outcome}")


study_job = Job(
    title="Prepare for an important examination",
    circumstance="The examination is approaching and study time is limited.",
    functional="Identify what matters most and organize study work.",
    emotional="Feel prepared rather than uncertain or overwhelmed.",
    social="Be able to demonstrate preparation to teachers, peers, or family.",
    desired_outcome="Increase readiness while reducing wasted study effort.",
)

study_job.describe()


# ---------------------------------------------------------------------------
# 3. JOB STORIES
# ---------------------------------------------------------------------------

print_section("2. JOB STORIES")

print(
    """
A common JTBD job-story structure is:

    When <circumstance>,
    I want to <motivation>,
    so I can <expected outcome>.

The structure intentionally emphasizes the situation and desired progress.

A job story is different from a feature request.

Feature request:
    "I want a dashboard."

Job story:
    "When I have several study subjects and limited time, I want to
     quickly identify the topics requiring attention, so I can allocate
     my study time effectively."
"""
)


@dataclass(frozen=True)
class JobStory:
    circumstance: str
    motivation: str
    outcome: str

    def render(self) -> str:
        return (
            f"When {self.circumstance}, "
            f"I want to {self.motivation}, "
            f"so I can {self.outcome}."
        )


job_story = JobStory(
    circumstance="I have several subjects to revise before an examination",
    motivation="identify which topics need the most attention",
    outcome="allocate my limited study time effectively",
)

print(job_story.render())


# ---------------------------------------------------------------------------
# 4. JOB VERSUS FEATURE VERSUS PERSONA
# ---------------------------------------------------------------------------

print_section("3. JOB VERSUS FEATURE VERSUS PERSONA")

comparison = {
    "Persona": "A representation of a user group or archetype.",
    "Feature": "A capability supplied by a product.",
    "Task": "An activity performed by a person.",
    "Job": "The progress a person is trying to make in a circumstance.",
    "Job story": "A structured expression of circumstance, motivation, and outcome.",
    "Desired outcome": "A measurable improvement the person wants while doing the job.",
}

for concept, definition in comparison.items():
    print(f"{concept:15}: {definition}")

print(
    """
Example:

Persona:
    "University student."

Task:
    "Read lecture notes."

Feature:
    "Searchable notes."

Job:
    "Prepare for an assessment efficiently when the amount of material
     exceeds the available study time."

The same persona can have many unrelated jobs, and the same job can be
performed by people belonging to very different demographic groups.
"""
)


# ---------------------------------------------------------------------------
# 5. JOB DECOMPOSITION
# ---------------------------------------------------------------------------

print_section("4. JOB DECOMPOSITION")

print(
    """
A complex job can be decomposed into stages.

Example:
    "Prepare for an examination"

    1. Define the target
    2. Gather relevant material
    3. Determine knowledge gaps
    4. Prioritize topics
    5. Practice
    6. Review mistakes
    7. Assess readiness
    8. Adjust the study plan

Decomposition helps distinguish the primary job from supporting jobs.
"""

study_stages = [
    "Define the target",
    "Gather relevant material",
    "Determine knowledge gaps",
    "Prioritize topics",
    "Practice",
    "Review mistakes",
    "Assess readiness",
    "Adjust the study plan",
]

for index, stage in enumerate(study_stages, start=1):
    print(f"{index}. {stage}")


# ---------------------------------------------------------------------------
# 6. DESIRED OUTCOMES
# ---------------------------------------------------------------------------

print_section("5. DESIRED OUTCOMES")

print(
    """
Desired outcomes should describe what the customer wants to improve,
reduce, increase, or control.

Weak:
    "Make studying better."

Stronger:
    "Minimize the time required to identify high-priority topics."

Useful outcome patterns include:
    minimize the time...
    minimize the likelihood...
    minimize the effort...
    increase the likelihood...
    increase the predictability...
    increase the control...
"""
)


@dataclass(frozen=True)
class DesiredOutcome:
    statement: str
    importance: float
    satisfaction: float

    def validate(self) -> None:
        if not 0 <= self.importance <= 10:
            raise ValueError("Importance must be between 0 and 10.")
        if not 0 <= self.satisfaction <= 10:
            raise ValueError("Satisfaction must be between 0 and 10.")

    def opportunity_score(self) -> float:
        """
        A commonly used opportunity formulation is:

            Opportunity = Importance + max(Importance - Satisfaction, 0)

        This implementation is deliberately explicit so that the
        calculation can be inspected and tested.
        """
        self.validate()
        return self.importance + max(self.importance - self.satisfaction, 0)


outcomes = [
    DesiredOutcome(
        "Minimize the time required to identify weak topics.", 9, 4
    ),
    DesiredOutcome(
        "Increase confidence that the study plan covers important material.", 8, 5
    ),
    DesiredOutcome(
        "Minimize the effort required to track revision progress.", 6, 7
    ),
    DesiredOutcome(
        "Increase the likelihood of remembering difficult concepts.", 9, 3
    ),
]

for outcome in outcomes:
    print(f"{outcome.statement}")
    print(
        f"  Importance={outcome.importance:.1f}, "
        f"Satisfaction={outcome.satisfaction:.1f}, "
        f"Opportunity={outcome.opportunity_score():.1f}"
    )


# ---------------------------------------------------------------------------
# 7. OPPORTUNITY SCORING
# ---------------------------------------------------------------------------

print_section("6. OPPORTUNITY SCORING")

print(
    """
Opportunity scoring is a prioritization technique used in some JTBD
research practices.

It is not a universal law of JTBD and should not replace qualitative
research.

A high score can indicate:
    - high importance
    - relatively low satisfaction

A low score can indicate:
    - low importance
    - high satisfaction
    - or both

The numerical score should be treated as evidence for discussion,
not as proof that a product decision is correct.
"""
)

for outcome in sorted(outcomes, key=lambda item: item.opportunity_score(), reverse=True):
    print(f"{outcome.opportunity_score():5.1f}  {outcome.statement}")


# ---------------------------------------------------------------------------
# 8. CIRCUMSTANCE MATTERS
# ---------------------------------------------------------------------------

print_section("7. CIRCUMSTANCE")

circumstances = [
    "I have thirty minutes before leaving for work.",
    "I have an examination in two weeks.",
    "I need to explain the same result to a non-technical stakeholder.",
    "I am comparing several financial products.",
    "I have received an unexpected error in production.",
]

print(
    """
The same person can have different jobs because circumstances change.

For example:
    At home:
        "Understand a technical concept deeply."

    During a meeting:
        "Explain the concept clearly within two minutes."

The underlying domain may be identical, but the circumstance changes
constraints, desired outcomes, and solution requirements.
"""
)

for circumstance in circumstances:
    print(f"- {circumstance}")


# ---------------------------------------------------------------------------
# 9. FUNCTIONAL, EMOTIONAL, AND SOCIAL DIMENSIONS
# ---------------------------------------------------------------------------

print_section("8. FUNCTIONAL, EMOTIONAL, AND SOCIAL JOBS")

job_dimensions = {
    "Functional": [
        "complete a practical task",
        "solve a problem",
        "make a decision",
        "organize information",
        "reduce time or effort",
    ],
    "Emotional": [
        "feel confident",
        "reduce anxiety or uncertainty",
        "feel in control",
        "avoid frustration",
        "feel accomplished",
    ],
    "Social": [
        "appear competent",
        "be perceived as reliable",
        "fit an expected social role",
        "signal expertise or taste",
        "maintain a relationship",
    ],
}

for dimension, examples in job_dimensions.items():
    print(f"\n{dimension} jobs:")
    for example in examples:
        print(f"  - {example}")


# ---------------------------------------------------------------------------
# 10. SWITCHING AND COMPETING SOLUTIONS
# ---------------------------------------------------------------------------

print_section("9. SWITCHING AND COMPETING SOLUTIONS")

print(
    """
JTBD analysis often examines what people were using before a new solution
and why they changed.

The competition is therefore broader than direct product competitors.

Example job:
    "Track personal expenses accurately."

Possible solutions:
    - spreadsheet
    - banking application
    - notebook
    - budgeting application
    - memory
    - exported transaction file
    - asking another person for help

A product can lose a customer to a non-product solution if that solution
performs the job adequately under the customer's circumstances.
"""
)


@dataclass
class SwitchingEvent:
    previous_solution: str
    new_solution: str
    trigger: str
    push: str
    pull: str
    anxiety: str
    habit: str

    def forces_of_progress(self) -> Dict[str, str]:
        return {
            "push": self.push,
            "pull": self.pull,
            "anxiety": self.anxiety,
            "habit": self.habit,
        }


switch = SwitchingEvent(
    previous_solution="Spreadsheet",
    new_solution="Expense application",
    trigger="Transaction volume became difficult to maintain manually.",
    push="Manual categorization consumed too much time.",
    pull="Automatic transaction categorization was attractive.",
    anxiety="Concern about privacy and incorrect categorization.",
    habit="Existing spreadsheet workflow was familiar.",
)

print(f"Previous solution: {switch.previous_solution}")
print(f"New solution:      {switch.new_solution}")
print(f"Trigger:           {switch.trigger}")

for force, description in switch.forces_of_progress().items():
    print(f"{force.title():18}: {description}")


# ---------------------------------------------------------------------------
# 11. INTERVIEW EVIDENCE
# ---------------------------------------------------------------------------

print_section("10. INTERVIEW EVIDENCE")

print(
    """
Strong JTBD research distinguishes observed or reported evidence from
interpretation.

A useful interview question often asks about a real event:

    "Tell me about the last time you had this problem."

This is generally more informative than:

    "Would you use a product that solved this?"

The first question asks about behavior and circumstances.
The second asks for a prediction or opinion.
"""
)


@dataclass(frozen=True)
class InterviewQuote:
    participant_id: str
    circumstance: str
    behavior: str
    previous_solution: str
    pain: str
    desired_result: str


interviews = [
    InterviewQuote(
        "P01",
        "An exam was two weeks away.",
        "Created a spreadsheet of topics and marked weak areas.",
        "Spreadsheet",
        "Maintaining the list became tedious.",
        "Know which topics deserve attention first.",
    ),
    InterviewQuote(
        "P02",
        "Several assignments were due in one week.",
        "Used calendar reminders and handwritten notes.",
        "Calendar + notebook",
        "Information was scattered.",
        "See priorities in one place.",
    ),
    InterviewQuote(
        "P03",
        "A difficult subject had many formulas.",
        "Solved practice problems repeatedly.",
        "Textbook + notebook",
        "Did not know which concepts were still weak.",
        "Receive evidence of readiness.",
    ),
]

for interview in interviews:
    print(f"\n{interview.participant_id}")
    print(f"  Circumstance:       {interview.circumstance}")
    print(f"  Behavior:           {interview.behavior}")
    print(f"  Previous solution:  {interview.previous_solution}")
    print(f"  Pain:               {interview.pain}")
    print(f"  Desired result:     {interview.desired_result}")


# ---------------------------------------------------------------------------
# 12. CODING QUALITATIVE RESEARCH
# ---------------------------------------------------------------------------

print_section("11. QUALITATIVE CODING")

print(
    """
Qualitative interview data can be coded into recurring themes.

Coding does not mean mechanically converting human behavior into numbers.
It is a way of organizing evidence so that recurring patterns can be
examined systematically.
"""
)

theme_keywords = {
    "time pressure": {"deadline", "limited", "week", "tomorrow"},
    "scattered information": {"scattered", "different", "multiple", "place"},
    "uncertainty": {"know", "weak", "uncertain", "confidence"},
    "manual effort": {"tedious", "manual", "repeatedly", "maintaining"},
}

sample_text = "Information was scattered and maintaining the list became tedious."

lower_text = sample_text.lower()

for theme, keywords in theme_keywords.items():
    matches = [keyword for keyword in keywords if keyword in lower_text]
    if matches:
        print(f"{theme:22}: {matches}")


# ---------------------------------------------------------------------------
# 13. JOB CLUSTERING
# ---------------------------------------------------------------------------

print_section("12. JOB CLUSTERING")

print(
    """
Individual statements may express the same underlying job.

For example:
    "I want to see my weak chapters."
    "I need to know what to revise first."
    "I do not want to spend time guessing what matters."

These can be clustered around:
    "Identify and prioritize knowledge gaps."
"""
)


@dataclass(frozen=True)
class JobEvidence:
    participant_id: str
    job_statement: str
    cluster: str


evidence = [
    JobEvidence("P01", "Identify weak chapters.", "Prioritize knowledge gaps"),
    JobEvidence("P02", "Know what to revise first.", "Prioritize knowledge gaps"),
    JobEvidence("P03", "Avoid guessing what matters.", "Prioritize knowledge gaps"),
    JobEvidence("P04", "Track deadlines.", "Manage commitments"),
    JobEvidence("P05", "Know which assignment comes first.", "Manage commitments"),
]

clusters: Dict[str, List[JobEvidence]] = defaultdict(list)

for item in evidence:
    clusters[item.cluster].append(item)

for cluster, items in clusters.items():
    print(f"\n{cluster}")
    for item in items:
        print(f"  {item.participant_id}: {item.job_statement}")


# ---------------------------------------------------------------------------
# 14. JOB ANALYSIS ENGINE
# ---------------------------------------------------------------------------

print_section("13. REUSABLE JTBD ANALYSIS ENGINE")


@dataclass
class JTBDAnalysis:
    name: str
    circumstance: str
    functional_job: str
    emotional_job: str
    social_job: str
    desired_outcomes: List[DesiredOutcome] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    barriers: List[str] = field(default_factory=list)

    def validate(self) -> None:
        fields_to_validate = {
            "name": self.name,
            "circumstance": self.circumstance,
            "functional_job": self.functional_job,
            "emotional_job": self.emotional_job,
            "social_job": self.social_job,
        }

        for field_name, value in fields_to_validate.items():
            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty.")

        for outcome in self.desired_outcomes:
            outcome.validate()

    def average_opportunity(self) -> float:
        self.validate()
        if not self.desired_outcomes:
            return 0.0
        return mean(
            outcome.opportunity_score()
            for outcome in self.desired_outcomes
        )

    def highest_opportunity(self) -> Optional[DesiredOutcome]:
        self.validate()
        if not self.desired_outcomes:
            return None
        return max(
            self.desired_outcomes,
            key=lambda outcome: outcome.opportunity_score(),
        )

    def report(self) -> None:
        self.validate()
        print(f"JTBD analysis: {self.name}")
        print(f"  Circumstance: {self.circumstance}")
        print(f"  Functional job: {self.functional_job}")
        print(f"  Emotional job: {self.emotional_job}")
        print(f"  Social job: {self.social_job}")
        print(f"  Alternatives: {', '.join(self.alternatives)}")
        print(f"  Barriers: {', '.join(self.barriers)}")

        print("  Desired outcomes:")
        for outcome in self.desired_outcomes:
            print(
                f"    - {outcome.statement} "
                f"(opportunity={outcome.opportunity_score():.1f})"
            )


analysis = JTBDAnalysis(
    name="Examination preparation",
    circumstance="A student has several topics to revise before an important exam.",
    functional_job="Identify, prioritize, practice, and review knowledge gaps.",
    emotional_job="Feel prepared and reduce uncertainty about readiness.",
    social_job="Demonstrate reliable preparation to relevant stakeholders.",
    desired_outcomes=[
        DesiredOutcome(
            "Minimize the time required to identify weak topics.", 9, 4
        ),
        DesiredOutcome(
            "Increase confidence in examination readiness.", 9, 5
        ),
        DesiredOutcome(
            "Minimize effort required to monitor revision progress.", 7, 6
        ),
    ],
    alternatives=[
        "Notebook",
        "Spreadsheet",
        "Calendar",
        "Textbook",
        "Memory",
    ],
    barriers=[
        "Limited time",
        "Scattered information",
        "Uncertainty about importance",
    ],
)

analysis.report()


# ---------------------------------------------------------------------------
# 15. JOB STORY GENERATION
# ---------------------------------------------------------------------------

print_section("14. JOB STORY GENERATION")

def build_job_story(
    circumstance: str,
    motivation: str,
    outcome: str,
) -> JobStory:
    """
    A small reusable constructor separates the three core components.
    Validation prevents empty job-story components.
    """
    values = {
        "circumstance": circumstance,
        "motivation": motivation,
        "outcome": outcome,
    }

    for name, value in values.items():
        if not value.strip():
            raise ValueError(f"{name} cannot be empty.")

    return JobStory(circumstance, motivation, outcome)


generated_story = build_job_story(
    "I have limited time before an examination",
    "identify the most important knowledge gaps",
    "spend my study time where it can produce the greatest improvement",
)

print(generated_story.render())


# ---------------------------------------------------------------------------
# 16. VALIDATION AND EDGE CASES
# ---------------------------------------------------------------------------

print_section("15. EDGE CASES AND VALIDATION")

print(
    """
Important edge cases include:

    - empty job statements
    - missing circumstances
    - invalid numerical ratings
    - no desired outcomes
    - duplicate evidence
    - overly broad jobs
    - jobs that are actually features
    - jobs that contain a proposed solution
    - hypothetical rather than observed behavior
"""
)

try:
    invalid_outcome = DesiredOutcome(
        "Invalid example",
        importance=12,
        satisfaction=4,
    )
    invalid_outcome.opportunity_score()
except ValueError as error:
    print(f"Validation caught invalid score: {error}")


try:
    empty_story = build_job_story("", "identify a problem", "make progress")
except ValueError as error:
    print(f"Validation caught empty circumstance: {error}")


empty_analysis = JTBDAnalysis(
    name="No outcomes",
    circumstance="A valid circumstance exists.",
    functional_job="Perform a valid job.",
    emotional_job="Feel confident.",
    social_job="Appear reliable.",
)

print(
    f"Analysis with no outcomes has average opportunity: "
    f"{empty_analysis.average_opportunity():.1f}"
)


# ---------------------------------------------------------------------------
# 17. IDENTIFYING FEATURE-ORIENTED LANGUAGE
# ---------------------------------------------------------------------------

print_section("16. FEATURE LANGUAGE VERSUS JOB LANGUAGE")

feature_terms = {
    "dashboard": "feature-oriented",
    "notification": "feature-oriented",
    "mobile app": "solution-oriented",
    "identify important topics": "job-oriented",
    "reduce uncertainty": "outcome-oriented",
    "prioritize work under time pressure": "job-oriented",
}

for phrase, classification in feature_terms.items():
    print(f"{phrase:40} -> {classification}")


def is_solution_or_feature_oriented(statement: str) -> bool:
    """
    This is only a heuristic. Human interpretation remains necessary.
    """
    solution_words = {
        "app",
        "dashboard",
        "button",
        "notification",
        "feature",
        "platform",
        "AI",
        "software",
        "screen",
    }

    words = set(re.findall(r"[A-Za-z]+", statement.lower()))
    return bool(words.intersection({word.lower() for word in solution_words}))


candidate_statements = [
    "I need a dashboard.",
    "I need to prioritize work before the deadline.",
    "I want notifications.",
    "I want to reduce uncertainty before making a decision.",
]

for statement in candidate_statements:
    print(
        f"{statement:65} -> "
        f"{'likely solution language' if is_solution_or_feature_oriented(statement) else 'not obviously solution language'}"
    )


# ---------------------------------------------------------------------------
# 18. COMPETING SOLUTION MATRIX
# ---------------------------------------------------------------------------

print_section("17. COMPETING SOLUTIONS")

@dataclass(frozen=True)
class SolutionEvaluation:
    solution: str
    speed: int
    effort: int
    confidence: int
    flexibility: int

    def score(self) -> float:
        """
        Higher speed, confidence, and flexibility are beneficial.
        Lower effort is beneficial, so effort is converted to
        an inverse score.
        """
        return mean([
            self.speed,
            11 - self.effort,
            self.confidence,
            self.flexibility,
        ])


solutions = [
    SolutionEvaluation("Notebook", 5, 4, 6, 9),
    SolutionEvaluation("Spreadsheet", 7, 6, 8, 8),
    SolutionEvaluation("Specialized application", 9, 3, 8, 7),
    SolutionEvaluation("Memory", 10, 1, 3, 4),
]

for solution in sorted(solutions, key=lambda item: item.score(), reverse=True):
    print(
        f"{solution.solution:25} "
        f"composite-analysis-score={solution.score():.2f}"
    )

print(
    """
This composite score is a demonstration of structured comparison, not a
universal JTBD metric. The dimensions and weights should be derived from
the actual job and research context.
"""
)


# ---------------------------------------------------------------------------
# 19. JOB MAP
# ---------------------------------------------------------------------------

print_section("18. JOB MAP")

job_map = {
    "Define": "Clarify what must be achieved.",
    "Locate": "Find relevant information or resources.",
    "Prepare": "Arrange inputs and conditions.",
    "Confirm": "Check whether the selected approach is appropriate.",
    "Execute": "Perform the core activity.",
    "Monitor": "Observe progress and emerging problems.",
    "Modify": "Adjust the approach when conditions change.",
    "Conclude": "Determine whether the desired result was achieved.",
}

for stage, description in job_map.items():
    print(f"{stage:10}: {description}")


# ---------------------------------------------------------------------------
# 20. PRODUCT DISCOVERY CASE STUDY
# ---------------------------------------------------------------------------

print_section("19. PRODUCT DISCOVERY CASE STUDY")

print(
    """
Scenario:
    A team is considering a study-planning application.

A feature-first approach might immediately request:
    - calendar
    - dashboard
    - reminders
    - charts

A JTBD approach begins with:
    - What was the person trying to accomplish?
    - In what circumstance?
    - What did they use before?
    - What made the existing approach insufficient?
    - What outcome were they trying to improve?
"""
)

case_study = JTBDAnalysis(
    name="Study planning under time pressure",
    circumstance=(
        "A learner has several subjects, limited time, and an upcoming assessment."
    ),
    functional_job=(
        "Determine what to study, in what order, and whether preparation is sufficient."
    ),
    emotional_job=(
        "Reduce uncertainty and feel in control of preparation."
    ),
    social_job=(
        "Appear prepared and dependable when discussing academic progress."
    ),
    desired_outcomes=[
        DesiredOutcome(
            "Minimize the time needed to identify high-priority topics.",
            10,
            3,
        ),
        DesiredOutcome(
            "Minimize the likelihood of overlooking an important topic.",
            10,
            4,
        ),
        DesiredOutcome(
            "Increase confidence that preparation is sufficient.",
            9,
            5,
        ),
        DesiredOutcome(
            "Minimize effort required to update the study plan.",
            7,
            6,
        ),
    ],
    alternatives=[
        "Notebook",
        "Spreadsheet",
        "Calendar",
        "Textbook",
        "Peer advice",
    ],
    barriers=[
        "Poor information organization",
        "Changing deadlines",
        "Limited time",
        "Unclear priorities",
    ],
)

case_study.report()

highest = case_study.highest_opportunity()
if highest:
    print(
        "\nHighest opportunity outcome in this illustrative dataset:"
        f"\n  {highest.statement}"
        f"\n  Score: {highest.opportunity_score():.1f}"
    )


# ---------------------------------------------------------------------------
# 21. ANTI-PATTERNS
# ---------------------------------------------------------------------------

print_section("20. COMMON JTBD MISTAKES")

mistakes = [
    (
        "Treating a feature as the job",
        "Example: 'The job is to use a dashboard.'",
        "A dashboard is a solution; investigate what progress it supports.",
    ),
    (
        "Defining a job by demographic identity",
        "Example: 'The job of students is to use this application.'",
        "Start with circumstances and desired progress.",
    ),
    (
        "Writing an excessively broad job",
        "Example: 'Be successful in life.'",
        "Use a bounded circumstance and observable progress.",
    ),
    (
        "Using only hypothetical preference questions",
        "Example: 'Would you buy this?'",
        "Investigate real past behavior and switching events.",
    ),
    (
        "Ignoring existing alternatives",
        "Example: treating the new application as the only solution.",
        "Study workarounds, habits, manual processes, and competing products.",
    ),
    (
        "Assuming emotional and social dimensions are optional",
        "Example: studying only time savings.",
        "Examine confidence, identity, trust, reputation, and social context.",
    ),
]

for title, example, correction in mistakes:
    print(f"\n{title}")
    print(f"  Problem: {example}")
    print(f"  Better approach: {correction}")


# ---------------------------------------------------------------------------
# 22. ADVANCED CONSIDERATIONS
# ---------------------------------------------------------------------------

print_section("21. ADVANCED JTBD CONSIDERATIONS")

advanced_points = [
    "Jobs exist in circumstances, so the same customer can have different jobs.",
    "A single job can contain functional, emotional, and social dimensions.",
    "A job can be decomposed into stages without confusing stages with the overall job.",
    "Solutions compete according to how well they help the customer make progress.",
    "Switching decisions can involve both attraction to a new solution and resistance to change.",
    "A job statement should avoid embedding a specific implementation unnecessarily.",
    "Research should distinguish observed behavior from interpretation.",
    "Quantitative prioritization is useful only when the underlying measurements are meaningful.",
    "The same job may be performed differently across contexts because constraints change.",
    "A product opportunity can exist where an important desired outcome is poorly satisfied.",
]

for point in advanced_points:
    print(f"- {point}")


# ---------------------------------------------------------------------------
# 23. PERFORMANCE AND DATA DESIGN
# ---------------------------------------------------------------------------

print_section("22. IMPLEMENTATION AND PERFORMANCE")

print(
    """
The educational engine uses simple in-memory structures.

Typical operations:
    - validating a job: O(k), where k is the number of outcomes
    - finding the highest opportunity: O(k)
    - calculating an average opportunity: O(k)
    - clustering evidence by an existing cluster: O(n)

Sorting outcomes requires O(k log k).

For large research datasets, practical systems may need:
    - persistent storage
    - structured identifiers
    - duplicate detection
    - qualitative coding workflows
    - access control
    - audit trails
    - versioned research decisions
    - statistical analysis
    - privacy controls
"""
)


# ---------------------------------------------------------------------------
# 24. SECURITY AND PRIVACY
# ---------------------------------------------------------------------------

print_section("23. SECURITY AND PRIVACY")

print(
    """
JTBD research can contain sensitive behavioral information.

A production research system should consider:
    - informed consent
    - data minimization
    - removal of unnecessary personally identifying information
    - access controls
    - encryption at rest and in transit
    - retention policies
    - audit logging
    - careful handling of interview recordings and transcripts

A job analysis should not require collecting personal information that is
irrelevant to the research question.
"""
)


# ---------------------------------------------------------------------------
# 25. TESTS
# ---------------------------------------------------------------------------

print_section("24. SELF-TESTS")

def run_tests() -> None:
    outcome = DesiredOutcome("Test outcome", 8, 3)
    assert math.isclose(outcome.opportunity_score(), 13.0)

    story = build_job_story(
        "a deadline is approaching",
        "prioritize the most important work",
        "use limited time effectively",
    )
    assert story.circumstance == "a deadline is approaching"
    assert "so I can" in story.render()

    valid_analysis = JTBDAnalysis(
        name="Test",
        circumstance="A circumstance",
        functional_job="A functional job",
        emotional_job="An emotional job",
        social_job="A social job",
        desired_outcomes=[outcome],
    )
    assert valid_analysis.highest_opportunity() == outcome
    assert math.isclose(valid_analysis.average_opportunity(), 13.0)

    try:
        DesiredOutcome("Bad", -1, 5).opportunity_score()
    except ValueError:
        pass
    else:
        raise AssertionError("Negative importance should fail validation.")

    print("All self-tests passed.")


run_tests()


# ---------------------------------------------------------------------------
# 26. FINAL EXECUTABLE JTBD WORKFLOW
# ---------------------------------------------------------------------------

print_section("25. COMPLETE JTBD WORKFLOW")

workflow = [
    "1. Identify a meaningful circumstance.",
    "2. Investigate a real event rather than relying only on hypothetical preference.",
    "3. Describe what the person was trying to accomplish.",
    "4. Separate the job from the current solution.",
    "5. Identify functional, emotional, and social dimensions.",
    "6. Examine previous solutions and workarounds.",
    "7. Identify switching triggers and barriers.",
    "8. Extract desired outcomes.",
    "9. Cluster similar evidence.",
    "10. Validate the job statement against actual research evidence.",
    "11. Prioritize important outcomes with appropriate evidence.",
    "12. Design solutions against the job rather than assuming the feature is the job.",
]

for item in workflow:
    print(item)

print(
    """
The central analytical question is:

    What progress is the person trying to make, under what circumstances,
    and what evidence shows that the current ways of making that progress
    are insufficient?

That question keeps the analysis focused on customer progress rather than
prematurely selecting a product feature.
"""
)
