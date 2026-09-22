"""
USER RESEARCH: A COMPLETE PRACTICAL STUDY
=========================================

This standalone program teaches user research from beginner to advanced level
through executable examples.

Topics demonstrated:
- What user research is
- Qualitative and quantitative research
- Research questions and objectives
- Research hypotheses
- Research plans
- Participant screening
- Sampling
- Interviews
- Surveys
- Observation
- Usability testing
- Research notes
- Coding qualitative data
- Affinity analysis
- Thematic analysis
- Quantitative survey analysis
- Cross-tabulation
- Satisfaction metrics
- Task success rate
- Time-on-task
- Error rate
- Net Promoter Score
- Confidence intervals
- Bias and confounding factors
- Triangulation
- Research validity and reliability
- Ethical considerations
- Research repositories
- Evidence strength
- Advanced mixed-method research
- Practical product recommendations
- A complete simulated research study

The program intentionally uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter, defaultdict
from statistics import mean, median, stdev
from math import sqrt
from typing import Dict, List, Tuple, Iterable, Optional
import random
import re
import textwrap


# ---------------------------------------------------------------------------
# 1. FOUNDATIONS
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title.upper())
    print("=" * 80)


def print_subsection(title: str) -> None:
    print(f"\n--- {title} ---")


def explain_foundations() -> None:
    print_section("1. What Is User Research?")

    print(
        "User research is the systematic study of people, their behaviors, "
        "needs, goals, expectations, problems, environments, and experiences "
        "with a product, service, process, or system."
    )

    print(
        "\nResearch can generate different kinds of evidence. Qualitative "
        "research helps explain why people behave or think in particular ways. "
        "Quantitative research measures patterns, frequencies, proportions, "
        "relationships, and outcomes."
    )

    concepts = {
        "Research objective": "What the study needs to understand or measure.",
        "Research question": "A specific question the study attempts to answer.",
        "Hypothesis": "A testable expectation about a relationship or outcome.",
        "Participant": "A person who contributes research data.",
        "Sample": "The subset of the target population included in a study.",
        "Method": "The procedure used to collect evidence.",
        "Finding": "An evidence-supported observation from collected data.",
        "Insight": "A meaningful interpretation that explains an important pattern.",
        "Recommendation": "An action proposed because of research evidence.",
    }

    for term, definition in concepts.items():
        print(f"{term}: {definition}")


# ---------------------------------------------------------------------------
# 2. RESEARCH PLAN
# ---------------------------------------------------------------------------

@dataclass
class ResearchQuestion:
    question: str
    method: str
    evidence_needed: str


@dataclass
class ResearchPlan:
    problem_statement: str
    objective: str
    target_population: str
    research_questions: List[ResearchQuestion]
    methods: List[str]
    risks: List[str]

    def display(self) -> None:
        print_section("2. Research Plan")
        print(f"Problem: {self.problem_statement}")
        print(f"Objective: {self.objective}")
        print(f"Target population: {self.target_population}")

        print_subsection("Research Questions")
        for index, item in enumerate(self.research_questions, 1):
            print(f"{index}. {item.question}")
            print(f"   Method: {item.method}")
            print(f"   Evidence: {item.evidence_needed}")

        print_subsection("Methods")
        for method in self.methods:
            print(f"- {method}")

        print_subsection("Potential Risks")
        for risk in self.risks:
            print(f"- {risk}")


def build_research_plan() -> ResearchPlan:
    return ResearchPlan(
        problem_statement=(
            "Users report difficulty completing an online service request "
            "without assistance."
        ),
        objective=(
            "Understand where users struggle, why they struggle, and which "
            "changes could reduce completion difficulty."
        ),
        target_population=(
            "Adults who have used similar online service portals within the "
            "last six months."
        ),
        research_questions=[
            ResearchQuestion(
                "Where do users experience the greatest friction?",
                "Moderated usability testing",
                "Task observations, errors, hesitation, and completion outcomes",
            ),
            ResearchQuestion(
                "Why do users experience this friction?",
                "Semi-structured interviews",
                "Participant explanations, expectations, motivations, and mental models",
            ),
            ResearchQuestion(
                "How common are the observed problems?",
                "Survey",
                "Frequency and distribution of reported problems",
            ),
            ResearchQuestion(
                "Which issues appear most important to users?",
                "Survey plus interviews",
                "Severity, frequency, and qualitative evidence",
            ),
        ],
        methods=[
            "Participant screening",
            "Semi-structured interviews",
            "Moderated usability testing",
            "Online survey",
            "Qualitative thematic analysis",
            "Descriptive quantitative analysis",
            "Triangulation",
        ],
        risks=[
            "Small or unrepresentative sample",
            "Leading interview questions",
            "Researcher interpretation bias",
            "Participant recall errors",
            "Survey response bias",
            "Artificial usability-test environment",
        ],
    )


# ---------------------------------------------------------------------------
# 3. SAMPLING AND SCREENING
# ---------------------------------------------------------------------------

@dataclass
class Participant:
    participant_id: str
    age: int
    experience_level: str
    frequency: int
    primary_goal: str
    consented: bool = True


def is_eligible(participant: Participant) -> bool:
    """
    A screening rule should be defined before recruiting participants.
    This prevents changing eligibility criteria after seeing participants.
    """
    return (
        participant.consented
        and 18 <= participant.age <= 70
        and participant.frequency >= 1
        and participant.experience_level in {"beginner", "intermediate", "advanced"}
    )


def demonstrate_sampling() -> List[Participant]:
    print_section("3. Sampling and Participant Screening")

    participants = [
        Participant("P01", 24, "beginner", 2, "submit application"),
        Participant("P02", 31, "intermediate", 8, "track request"),
        Participant("P03", 45, "advanced", 12, "submit application"),
        Participant("P04", 17, "beginner", 5, "submit application", False),
        Participant("P05", 38, "intermediate", 4, "find information"),
        Participant("P06", 67, "beginner", 1, "submit application"),
    ]

    eligible = [p for p in participants if is_eligible(p)]

    print(f"Total candidates: {len(participants)}")
    print(f"Eligible participants: {len(eligible)}")

    for participant in eligible:
        print(
            f"{participant.participant_id}: "
            f"age={participant.age}, "
            f"experience={participant.experience_level}, "
            f"frequency={participant.frequency}"
        )

    print(
        "\nSampling does not automatically make a study representative. "
        "Researchers must consider recruitment method, inclusion criteria, "
        "population coverage, sample size, and selection bias."
    )

    return eligible


# ---------------------------------------------------------------------------
# 4. QUALITATIVE INTERVIEW DATA
# ---------------------------------------------------------------------------

@dataclass
class InterviewExcerpt:
    participant_id: str
    text: str
    context: str


INTERVIEW_EXCERPTS = [
    InterviewExcerpt(
        "P01",
        "I did not know which button would actually submit the request.",
        "submission",
    ),
    InterviewExcerpt(
        "P02",
        "The status page uses words that I do not normally use.",
        "status",
    ),
    InterviewExcerpt(
        "P03",
        "I expected the next step to be visible after I uploaded the document.",
        "upload",
    ),
    InterviewExcerpt(
        "P05",
        "I kept checking whether the file had really been uploaded.",
        "upload",
    ),
    InterviewExcerpt(
        "P06",
        "I wanted someone to tell me what would happen after submission.",
        "submission",
    ),
    InterviewExcerpt(
        "P01",
        "The form asks for information I thought the organization already had.",
        "form",
    ),
    InterviewExcerpt(
        "P02",
        "I was worried that going back would erase what I entered.",
        "navigation",
    ),
]


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def keyword_frequency(excerpts: Iterable[InterviewExcerpt]) -> Counter:
    stop_words = {
        "the", "a", "an", "i", "to", "and", "of", "that", "was",
        "is", "it", "for", "after", "my", "had", "would", "be",
        "what", "did", "not", "which", "have", "really", "me",
    }

    words = []
    for excerpt in excerpts:
        words.extend(
            word for word in tokenize(excerpt.text)
            if word not in stop_words
        )

    return Counter(words)


def demonstrate_qualitative_coding(excerpts: List[InterviewExcerpt]) -> None:
    print_section("4. Qualitative Research and Coding")

    print_subsection("Raw Interview Evidence")
    for excerpt in excerpts:
        print(f"{excerpt.participant_id} [{excerpt.context}]: {excerpt.text}")

    print_subsection("Simple Keyword Analysis")
    frequencies = keyword_frequency(excerpts)

    for word, count in frequencies.most_common(10):
        print(f"{word}: {count}")

    print(
        "\nKeyword frequency is not thematic analysis. A frequent word may "
        "be unimportant, while a less frequent idea may represent a serious "
        "problem. Human interpretation and contextual coding remain essential."
    )


# ---------------------------------------------------------------------------
# 5. THEMATIC ANALYSIS
# ---------------------------------------------------------------------------

@dataclass
class CodedExcerpt:
    participant_id: str
    text: str
    codes: List[str]


CODE_RULES = {
    "unclear_call_to_action": [
        "which button",
        "submit the request",
    ],
    "unclear_status_language": [
        "status page",
        "words that i do not",
    ],
    "missing_system_feedback": [
        "whether the file",
        "really been uploaded",
    ],
    "unclear_next_step": [
        "next step",
        "after i uploaded",
    ],
    "unclear_post_submission_process": [
        "what would happen after submission",
    ],
    "unnecessary_data_request": [
        "information i thought",
        "already had",
    ],
    "navigation_anxiety": [
        "going back",
        "erase what i entered",
    ],
}


def code_excerpt(excerpt: InterviewExcerpt) -> CodedExcerpt:
    text = excerpt.text.lower()
    codes = []

    for code, patterns in CODE_RULES.items():
        if any(pattern in text for pattern in patterns):
            codes.append(code)

    return CodedExcerpt(
        participant_id=excerpt.participant_id,
        text=excerpt.text,
        codes=codes,
    )


def thematic_analysis(excerpts: List[InterviewExcerpt]) -> Dict[str, List[str]]:
    coded = [code_excerpt(excerpt) for excerpt in excerpts]

    themes = defaultdict(list)

    for item in coded:
        for code in item.codes:
            themes[code].append(item.participant_id)

    return dict(themes)


def demonstrate_thematic_analysis(excerpts: List[InterviewExcerpt]) -> None:
    print_section("5. Thematic Analysis")

    themes = thematic_analysis(excerpts)

    for theme, participants in themes.items():
        print(
            f"{theme}: "
            f"{len(participants)} evidence item(s), "
            f"participants={sorted(set(participants))}"
        )

    print(
        "\nA typical thematic-analysis workflow is: familiarize with data, "
        "generate codes, group related codes, develop themes, review themes, "
        "define themes, and connect conclusions to evidence."
    )


# ---------------------------------------------------------------------------
# 6. AFFINITY ANALYSIS
# ---------------------------------------------------------------------------

AFFINITY_GROUPS = {
    "Feedback and visibility": {
        "missing_system_feedback",
        "unclear_status_language",
    },
    "Workflow clarity": {
        "unclear_call_to_action",
        "unclear_next_step",
        "unclear_post_submission_process",
    },
    "Data-entry concerns": {
        "unnecessary_data_request",
        "navigation_anxiety",
    },
}


def map_codes_to_themes() -> Dict[str, List[str]]:
    result = defaultdict(list)

    for theme, codes in AFFINITY_GROUPS.items():
        for code in codes:
            result[theme].append(code)

    return dict(result)


def demonstrate_affinity_analysis() -> None:
    print_section("6. Affinity Analysis")

    for theme, codes in map_codes_to_themes().items():
        print(f"\n{theme}")
        for code in codes:
            print(f"  - {code}")

    print(
        "\nAffinity analysis groups related observations into larger concepts. "
        "The grouping should remain traceable to the underlying evidence."
    )


# ---------------------------------------------------------------------------
# 7. USABILITY TESTING METRICS
# ---------------------------------------------------------------------------

@dataclass
class UsabilityTaskResult:
    participant_id: str
    task_name: str
    completed: bool
    time_seconds: float
    errors: int
    satisfaction: int


USABILITY_RESULTS = [
    UsabilityTaskResult("P01", "Submit Request", True, 145, 2, 4),
    UsabilityTaskResult("P02", "Submit Request", True, 102, 1, 4),
    UsabilityTaskResult("P03", "Submit Request", True, 88, 0, 5),
    UsabilityTaskResult("P05", "Submit Request", False, 240, 4, 2),
    UsabilityTaskResult("P06", "Submit Request", True, 180, 3, 3),
]


def task_success_rate(results: List[UsabilityTaskResult]) -> float:
    if not results:
        return 0.0
    return sum(result.completed for result in results) / len(results)


def average_time(results: List[UsabilityTaskResult]) -> float:
    return mean(result.time_seconds for result in results) if results else 0.0


def average_errors(results: List[UsabilityTaskResult]) -> float:
    return mean(result.errors for result in results) if results else 0.0


def demonstrate_usability_metrics() -> None:
    print_section("7. Usability Testing Metrics")

    success = task_success_rate(USABILITY_RESULTS)
    time_average = average_time(USABILITY_RESULTS)
    errors = average_errors(USABILITY_RESULTS)

    print(f"Task success rate: {success:.1%}")
    print(f"Average task time: {time_average:.1f} seconds")
    print(f"Average errors per participant: {errors:.2f}")

    print_subsection("Participant-Level Results")
    for result in USABILITY_RESULTS:
        print(
            f"{result.participant_id}: "
            f"completed={result.completed}, "
            f"time={result.time_seconds}s, "
            f"errors={result.errors}, "
            f"satisfaction={result.satisfaction}/5"
        )

    print(
        "\nA usability metric becomes meaningful when its definition is "
        "consistent across participants and tasks."
    )


# ---------------------------------------------------------------------------
# 8. SURVEY DATA
# ---------------------------------------------------------------------------

@dataclass
class SurveyResponse:
    participant_id: str
    age_group: str
    satisfaction: int
    ease_of_use: int
    recommendation: int
    encountered_upload_problem: bool
    encountered_status_problem: bool


SURVEY_RESPONSES = [
    SurveyResponse("S01", "18-29", 3, 3, 6, True, True),
    SurveyResponse("S02", "30-44", 4, 4, 8, False, True),
    SurveyResponse("S03", "45-59", 2, 2, 4, True, True),
    SurveyResponse("S04", "30-44", 5, 5, 9, False, False),
    SurveyResponse("S05", "18-29", 3, 3, 7, True, False),
    SurveyResponse("S06", "45-59", 2, 2, 5, True, True),
    SurveyResponse("S07", "30-44", 4, 4, 8, False, True),
    SurveyResponse("S08", "60+", 3, 3, 6, True, True),
    SurveyResponse("S09", "18-29", 4, 4, 8, False, False),
    SurveyResponse("S10", "30-44", 5, 5, 9, False, False),
]


def calculate_nps(responses: List[SurveyResponse]) -> float:
    """
    NPS = percentage of promoters - percentage of detractors.

    9-10 = promoters
    7-8  = passives
    0-6  = detractors

    NPS is a particular standardized metric. It should not be confused
    with general satisfaction.
    """
    if not responses:
        return 0.0

    promoters = sum(r.recommendation >= 9 for r in responses)
    detractors = sum(r.recommendation <= 6 for r in responses)

    return ((promoters / len(responses)) - (detractors / len(responses))) * 100


def demonstrate_survey_analysis() -> None:
    print_section("8. Quantitative Survey Analysis")

    satisfaction_scores = [r.satisfaction for r in SURVEY_RESPONSES]
    ease_scores = [r.ease_of_use for r in SURVEY_RESPONSES]

    print(f"Responses: {len(SURVEY_RESPONSES)}")
    print(f"Mean satisfaction: {mean(satisfaction_scores):.2f}/5")
    print(f"Median satisfaction: {median(satisfaction_scores):.2f}/5")
    print(f"Mean ease of use: {mean(ease_scores):.2f}/5")
    print(f"NPS: {calculate_nps(SURVEY_RESPONSES):.1f}")

    upload_problem_rate = mean(
        response.encountered_upload_problem
        for response in SURVEY_RESPONSES
    )

    status_problem_rate = mean(
        response.encountered_status_problem
        for response in SURVEY_RESPONSES
    )

    print(f"Upload-problem rate: {upload_problem_rate:.1%}")
    print(f"Status-problem rate: {status_problem_rate:.1%}")


# ---------------------------------------------------------------------------
# 9. CROSS-TABULATION
# ---------------------------------------------------------------------------

def cross_tabulate(
    responses: List[SurveyResponse],
    category_attribute: str,
    boolean_attribute: str,
) -> Dict[str, Tuple[int, int, float]]:
    table = {}

    categories = sorted(
        {getattr(response, category_attribute) for response in responses}
    )

    for category in categories:
        group = [
            response
            for response in responses
            if getattr(response, category_attribute) == category
        ]

        affected = sum(
            getattr(response, boolean_attribute)
            for response in group
        )

        table[category] = (
            len(group),
            affected,
            affected / len(group) if group else 0.0,
        )

    return table


def demonstrate_cross_tabulation() -> None:
    print_section("9. Cross-Tabulation")

    table = cross_tabulate(
        SURVEY_RESPONSES,
        "age_group",
        "encountered_upload_problem",
    )

    print("Age group | Participants | Upload problem | Rate")
    print("-" * 55)

    for category, (count, affected, rate) in table.items():
        print(f"{category:9} | {count:12} | {affected:14} | {rate:.1%}")


# ---------------------------------------------------------------------------
# 10. BASIC STATISTICS AND UNCERTAINTY
# ---------------------------------------------------------------------------

def mean_confidence_interval(
    values: List[float],
    z_value: float = 1.96,
) -> Tuple[float, float]:
    """
    Approximate 95% confidence interval for a sample mean.

    This approximation assumes independent observations and uses a normal
    critical value. Small samples may require a t-distribution instead.
    """
    if len(values) < 2:
        raise ValueError("At least two observations are required.")

    sample_mean = mean(values)
    sample_std = stdev(values)
    standard_error = sample_std / sqrt(len(values))
    margin = z_value * standard_error

    return sample_mean - margin, sample_mean + margin


def demonstrate_uncertainty() -> None:
    print_section("10. Uncertainty and Confidence Intervals")

    values = [result.time_seconds for result in USABILITY_RESULTS]

    lower, upper = mean_confidence_interval(values)

    print(f"Mean task time: {mean(values):.2f} seconds")
    print(f"Approximate 95% CI: [{lower:.2f}, {upper:.2f}]")

    print(
        "\nA confidence interval expresses sampling uncertainty under the "
        "assumptions of the statistical procedure. It does not mean that "
        "95% of individual users fall inside the interval."
    )


# ---------------------------------------------------------------------------
# 11. BIAS DETECTION
# ---------------------------------------------------------------------------

@dataclass
class BiasRisk:
    name: str
    mechanism: str
    mitigation: str


BIAS_RISKS = [
    BiasRisk(
        "Selection bias",
        "Recruitment disproportionately includes certain types of users.",
        "Define the target population and recruitment criteria before recruitment.",
    ),
    BiasRisk(
        "Leading-question bias",
        "Question wording encourages a particular response.",
        "Use neutral and open-ended wording.",
    ),
    BiasRisk(
        "Confirmation bias",
        "Researchers notice evidence supporting existing assumptions.",
        "Record contradictory evidence and use independent review where possible.",
    ),
    BiasRisk(
        "Recall bias",
        "Participants do not accurately remember past events.",
        "Ask about recent concrete experiences and use behavioral evidence.",
    ),
    BiasRisk(
        "Social desirability bias",
        "Participants give answers they believe are socially acceptable.",
        "Create a non-judgmental environment and emphasize honest feedback.",
    ),
    BiasRisk(
        "Observer effect",
        "People change behavior because they know they are being observed.",
        "Use unobtrusive observation where ethically and practically appropriate.",
    ),
]


def demonstrate_biases() -> None:
    print_section("11. Research Bias")

    for bias in BIAS_RISKS:
        print(f"\n{bias.name}")
        print(f"Mechanism: {bias.mechanism}")
        print(f"Mitigation: {bias.mitigation}")


# ---------------------------------------------------------------------------
# 12. TRIANGULATION
# ---------------------------------------------------------------------------

@dataclass
class Evidence:
    source: str
    finding: str
    strength: str


EVIDENCE = [
    Evidence(
        "Interview",
        "Participants describe uncertainty about whether uploads succeeded.",
        "qualitative",
    ),
    Evidence(
        "Usability test",
        "Participants repeatedly check the upload area before continuing.",
        "behavioral",
    ),
    Evidence(
        "Survey",
        "50% of respondents report encountering upload problems.",
        "quantitative",
    ),
]


def demonstrate_triangulation() -> None:
    print_section("12. Triangulation")

    for evidence in EVIDENCE:
        print(
            f"{evidence.source}: {evidence.finding} "
            f"[{evidence.strength}]"
        )

    print(
        "\nTriangulation compares evidence from different methods or sources. "
        "Agreement across independent evidence types can strengthen confidence "
        "in a finding, while disagreement identifies areas requiring further study."
    )


# ---------------------------------------------------------------------------
# 13. EVIDENCE-BASED INSIGHTS
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    observation: str
    evidence: List[str]
    interpretation: str
    confidence: str


FINDINGS = [
    Finding(
        observation="Users experience uncertainty around file submission.",
        evidence=[
            "Interview excerpts mention uncertainty.",
            "Usability observations show repeated checking.",
            "Survey responses report upload problems.",
        ],
        interpretation=(
            "The workflow may provide insufficient feedback after file upload."
        ),
        confidence="moderate-to-high",
    ),
    Finding(
        observation="Status terminology can be difficult to understand.",
        evidence=[
            "Interview participants explicitly describe unfamiliar wording."
        ],
        interpretation=(
            "Status labels may not match users' existing vocabulary or expectations."
        ),
        confidence="moderate",
    ),
]


def demonstrate_findings() -> None:
    print_section("13. From Evidence to Insight")

    for index, finding in enumerate(FINDINGS, 1):
        print(f"\nFinding {index}: {finding.observation}")
        print("Evidence:")
        for evidence in finding.evidence:
            print(f"  - {evidence}")
        print(f"Interpretation: {finding.interpretation}")
        print(f"Confidence: {finding.confidence}")


# ---------------------------------------------------------------------------
# 14. RESEARCH QUALITY
# ---------------------------------------------------------------------------

def discuss_research_quality() -> None:
    print_section("14. Validity, Reliability, and Research Quality")

    concepts = {
        "Construct validity": (
            "Whether the study actually measures the concept it claims to measure."
        ),
        "Internal validity": (
            "Whether observed relationships can reasonably be attributed to the "
            "factors being studied rather than uncontrolled alternatives."
        ),
        "External validity": (
            "Whether findings can reasonably transfer to other populations or contexts."
        ),
        "Reliability": (
            "Whether a measurement or procedure produces reasonably consistent results."
        ),
        "Ecological validity": (
            "How closely the research context represents real-world conditions."
        ),
        "Researcher reflexivity": (
            "Awareness of how the researcher's assumptions, position, and decisions "
            "may influence the study."
        ),
    }

    for term, definition in concepts.items():
        print(f"{term}: {definition}")


# ---------------------------------------------------------------------------
# 15. ETHICS AND PRIVACY
# ---------------------------------------------------------------------------

def demonstrate_ethics() -> None:
    print_section("15. Research Ethics and Privacy")

    principles = [
        "Obtain informed consent before participation.",
        "Explain what data will be collected and why.",
        "Collect only data necessary for the research purpose.",
        "Protect personally identifiable information.",
        "Allow participants to withdraw when applicable.",
        "Avoid unnecessary deception.",
        "Store research data securely.",
        "Restrict access to authorized researchers.",
        "Separate participant identity from analysis data when possible.",
        "Report findings honestly, including contradictory evidence.",
        "Avoid fabricating, altering, or selectively hiding research results.",
    ]

    for principle in principles:
        print(f"- {principle}")


# ---------------------------------------------------------------------------
# 16. RESEARCH REPOSITORY MODEL
# ---------------------------------------------------------------------------

@dataclass
class ResearchArtifact:
    artifact_id: str
    artifact_type: str
    source: str
    content: str
    participant_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class ResearchRepository:
    """
    A small in-memory model of a research repository.

    A production repository would normally require authentication,
    authorization, encryption, retention policies, audit logging, and
    stronger privacy controls.
    """

    def __init__(self) -> None:
        self.artifacts: Dict[str, ResearchArtifact] = {}

    def add(self, artifact: ResearchArtifact) -> None:
        if artifact.artifact_id in self.artifacts:
            raise ValueError("Artifact ID already exists.")
        self.artifacts[artifact.artifact_id] = artifact

    def find_by_tag(self, tag: str) -> List[ResearchArtifact]:
        return [
            artifact
            for artifact in self.artifacts.values()
            if tag in artifact.tags
        ]

    def count_by_type(self) -> Counter:
        return Counter(
            artifact.artifact_type
            for artifact in self.artifacts.values()
        )


def demonstrate_repository() -> None:
    print_section("16. Research Repository")

    repository = ResearchRepository()

    repository.add(
        ResearchArtifact(
            "INT-001",
            "interview",
            "moderated interview",
            "Participant described uncertainty after upload.",
            "P01",
            ["upload", "feedback"],
        )
    )

    repository.add(
        ResearchArtifact(
            "UT-001",
            "usability_observation",
            "usability test",
            "Participant checked upload status twice.",
            "P01",
            ["upload", "feedback", "behavior"],
        )
    )

    repository.add(
        ResearchArtifact(
            "SUR-001",
            "survey",
            "online survey",
            "Participant reported upload difficulty.",
            "S01",
            ["upload", "quantitative"],
        )
    )

    print("Artifacts by type:", dict(repository.count_by_type()))

    print("\nArtifacts tagged 'upload':")
    for artifact in repository.find_by_tag("upload"):
        print(f"- {artifact.artifact_id}: {artifact.content}")


# ---------------------------------------------------------------------------
# 17. RESEARCH PRIORITIZATION
# ---------------------------------------------------------------------------

@dataclass
class ResearchIssue:
    name: str
    frequency: float
    severity: float
    confidence: float

    @property
    def evidence_priority(self) -> float:
        """
        This is a research-analysis heuristic, not a universal formula.

        Higher frequency, severity, and confidence increase the value of
        investigating an issue. Different organizations may use different
        prioritization models.
        """
        return self.frequency * self.severity * self.confidence


def demonstrate_prioritization() -> None:
    print_section("17. Evidence-Based Issue Prioritization")

    issues = [
        ResearchIssue("Upload uncertainty", 0.50, 5.0, 0.85),
        ResearchIssue("Status terminology", 0.40, 3.0, 0.70),
        ResearchIssue("Navigation anxiety", 0.20, 4.0, 0.55),
        ResearchIssue("Extra information request", 0.30, 2.0, 0.60),
    ]

    for issue in sorted(
        issues,
        key=lambda item: item.evidence_priority,
        reverse=True,
    ):
        print(
            f"{issue.name}: "
            f"frequency={issue.frequency:.0%}, "
            f"severity={issue.severity:.1f}, "
            f"confidence={issue.confidence:.0%}, "
            f"heuristic={issue.evidence_priority:.2f}"
        )

    print(
        "\nA prioritization score should be treated as a decision aid, not "
        "as a replacement for evidence or stakeholder judgment."
    )


# ---------------------------------------------------------------------------
# 18. ADVANCED RESEARCH DESIGN
# ---------------------------------------------------------------------------

@dataclass
class MixedMethodPhase:
    name: str
    purpose: str
    method: str
    output: str


def demonstrate_mixed_methods() -> None:
    print_section("18. Advanced Mixed-Method Research")

    phases = [
        MixedMethodPhase(
            "Exploration",
            "Discover unknown problems and user language.",
            "Interviews",
            "Themes and hypotheses",
        ),
        MixedMethodPhase(
            "Measurement",
            "Estimate prevalence and distribution.",
            "Survey",
            "Frequencies and relationships",
        ),
        MixedMethodPhase(
            "Behavioral validation",
            "Observe actual task behavior.",
            "Usability testing",
            "Success, errors, time, behavior",
        ),
        MixedMethodPhase(
            "Integration",
            "Compare and reconcile evidence.",
            "Triangulation",
            "Evidence-backed findings",
        ),
    ]

    for phase in phases:
        print(f"\n{phase.name}")
        print(f"Purpose: {phase.purpose}")
        print(f"Method: {phase.method}")
        print(f"Output: {phase.output}")


# ---------------------------------------------------------------------------
# 19. ADVANCED CONCEPTS
# ---------------------------------------------------------------------------

def discuss_advanced_concepts() -> None:
    print_section("19. Advanced Concepts")

    concepts = [
        (
            "Longitudinal research",
            "Studies the same phenomenon across time to identify change, adaptation, "
            "retention, or evolving behavior."
        ),
        (
            "Diary studies",
            "Participants record experiences close to when they occur, reducing some "
            "recall limitations."
        ),
        (
            "Contextual inquiry",
            "Researcher observes and questions participants in the environment where "
            "the relevant work naturally occurs."
        ),
        (
            "Card sorting",
            "Participants organize information items to reveal how they group concepts."
        ),
        (
            "Tree testing",
            "Evaluates whether users can locate information within an information architecture."
        ),
        (
            "Concept testing",
            "Examines participant reactions to a proposed concept before full implementation."
        ),
        (
            "A/B testing",
            "Randomized comparison of variants to estimate differences in a defined outcome."
        ),
        (
            "Causal inference",
            "Attempts to distinguish causal effects from associations using appropriate "
            "study designs and assumptions."
        ),
        (
            "Mixed-method research",
            "Combines qualitative and quantitative evidence in a deliberately integrated design."
        ),
        (
            "Triangulation",
            "Compares evidence across methods, researchers, sources, or theoretical perspectives."
        ),
        (
            "Saturation",
            "A qualitative concept describing diminishing emergence of substantively new themes "
            "under a defined research design."
        ),
        (
            "Research ops",
            "The systems, processes, repositories, recruitment, governance, and operational "
            "practices supporting research at scale."
        ),
    ]

    for name, definition in concepts:
        print(f"{name}: {definition}")


# ---------------------------------------------------------------------------
# 20. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print_section("20. Edge Cases and Exceptions")

    print_subsection("Empty dataset")
    empty_results: List[UsabilityTaskResult] = []
    print(f"Success rate: {task_success_rate(empty_results):.1%}")
    print(f"Average time: {average_time(empty_results):.1f}")

    print_subsection("Missing statistical observations")
    try:
        mean_confidence_interval([42])
    except ValueError as error:
        print(f"Handled expected error: {error}")

    print_subsection("Duplicate repository identifier")
    repository = ResearchRepository()
    artifact = ResearchArtifact(
        "A01",
        "note",
        "researcher",
        "Example",
    )

    repository.add(artifact)

    try:
        repository.add(artifact)
    except ValueError as error:
        print(f"Handled expected error: {error}")

    print(
        "\nReal studies also face missing responses, participant dropouts, "
        "contradictory accounts, ambiguous observations, invalid survey responses, "
        "small samples, measurement error, and operational constraints."
    )


# ---------------------------------------------------------------------------
# 21. COMMON RESEARCH MISTAKES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    print_section("21. Common Research Mistakes")

    mistakes = [
        (
            "Starting with a solution",
            "Researchers may unconsciously seek evidence supporting a predetermined feature."
        ),
        (
            "Asking leading questions",
            "Participants can be pushed toward the researcher's preferred answer."
        ),
        (
            "Confusing opinions with behavior",
            "What users say they will do is not always identical to what they do."
        ),
        (
            "Treating a small sample as universal",
            "Qualitative evidence can be deep without being statistically representative."
        ),
        (
            "Reporting percentages without denominators",
            "A percentage without sample size can be misleading."
        ),
        (
            "Ignoring contradictory evidence",
            "Disconfirming observations can expose weak assumptions."
        ),
        (
            "Overinterpreting correlation",
            "Association does not by itself establish causation."
        ),
        (
            "Using jargon with participants",
            "Technical terminology can alter participant interpretation."
        ),
        (
            "Collecting unnecessary personal data",
            "More data increases privacy and governance responsibilities."
        ),
        (
            "Skipping traceability",
            "A finding should be traceable to observations, responses, or other evidence."
        ),
    ]

    for mistake, consequence in mistakes:
        print(f"\n{mistake}")
        print(f"Why it matters: {consequence}")


# ---------------------------------------------------------------------------
# 22. PRODUCTION-ORIENTED RESEARCH PIPELINE
# ---------------------------------------------------------------------------

class ResearchPipeline:
    """
    A compact representation of an end-to-end research workflow.

    In production, each stage would have governance, access controls,
    documentation, quality checks, and versioning.
    """

    def __init__(self) -> None:
        self.stages = [
            "Define problem",
            "Define objectives",
            "Create research questions",
            "Select method",
            "Define population",
            "Recruit participants",
            "Collect evidence",
            "Clean and organize data",
            "Code and analyze",
            "Triangulate",
            "Develop findings",
            "Communicate evidence",
            "Translate findings into decisions",
            "Archive research artifacts",
        ]

    def execute_simulation(self) -> None:
        print_section("22. End-to-End Research Pipeline")

        for number, stage in enumerate(self.stages, 1):
            print(f"{number:02d}. {stage}")


# ---------------------------------------------------------------------------
# 23. RESEARCH QUESTION QUALITY CHECK
# ---------------------------------------------------------------------------

def evaluate_research_question(question: str) -> Dict[str, bool]:
    """
    A lightweight heuristic for teaching question quality.

    This does not determine whether a question is scientifically valid.
    Human methodological review is still required.
    """
    normalized = question.strip().lower()

    return {
        "not_empty": bool(normalized),
        "reasonable_length": 8 <= len(normalized.split()) <= 30,
        "contains_question_form": normalized.endswith("?"),
        "avoids_obvious_leading_phrase": not normalized.startswith(
            ("don't you think", "wouldn't you agree")
        ),
    }


def demonstrate_question_quality() -> None:
    print_section("23. Research Question Quality")

    questions = [
        "Where do users experience difficulty when submitting a request?",
        "Don't you think the new upload design is easier to use?",
        "How do users decide what to do after receiving a status update?",
    ]

    for question in questions:
        evaluation = evaluate_research_question(question)
        print(f"\nQuestion: {question}")
        for criterion, passed in evaluation.items():
            print(f"  {criterion}: {'PASS' if passed else 'REVIEW'}")


# ---------------------------------------------------------------------------
# 24. SIMULATED RESEARCH REPORT
# ---------------------------------------------------------------------------

def generate_research_report() -> str:
    """
    Produces a compact report from the simulated evidence.
    The report separates observed evidence from interpretation.
    """

    success = task_success_rate(USABILITY_RESULTS)
    mean_task_time = average_time(USABILITY_RESULTS)
    upload_rate = mean(
        response.encountered_upload_problem
        for response in SURVEY_RESPONSES
    )

    return textwrap.dedent(
        f"""
        RESEARCH STUDY REPORT
        ---------------------

        Research objective:
        Understand friction in an online service-request workflow.

        Behavioral evidence:
        The observed task success rate was {success:.1%}.
        Mean observed task time was {mean_task_time:.1f} seconds.

        Survey evidence:
        {upload_rate:.1%} of surveyed respondents reported an upload problem.

        Qualitative evidence:
        Interviews included repeated concerns about upload feedback, status
        terminology, next-step visibility, and navigation.

        Interpretation:
        The evidence suggests that workflow visibility and system feedback
        deserve focused investigation.

        Important limitation:
        These simulated observations are illustrative and should not be
        treated as representative evidence about a real user population.

        Recommended research decision:
        Validate the proposed interpretation with additional participants,
        especially users who differ from the current sample.
        """
    ).strip()


# ---------------------------------------------------------------------------
# 25. PERFORMANCE CONSIDERATIONS
# ---------------------------------------------------------------------------

def demonstrate_performance() -> None:
    print_section("25. Performance Considerations")

    random.seed(7)
    synthetic_codes = [
        random.choice(
            [
                "navigation",
                "feedback",
                "upload",
                "status",
                "form",
                "search",
            ]
        )
        for _ in range(10_000)
    ]

    frequencies = Counter(synthetic_codes)

    print(f"Synthetic observations analyzed: {len(synthetic_codes)}")
    print(f"Unique codes: {len(frequencies)}")
    print(f"Most common code: {frequencies.most_common(1)[0]}")

    print(
        "\nFor large research datasets, indexed databases, columnar processing, "
        "streaming, vectorized operations, and specialized qualitative-analysis "
        "systems may become appropriate. The correct architecture depends on "
        "data size, privacy requirements, query patterns, and governance."
    )


# ---------------------------------------------------------------------------
# 26. SECURITY AND DATA GOVERNANCE
# ---------------------------------------------------------------------------

def demonstrate_security() -> None:
    print_section("26. Security and Data Governance")

    controls = {
        "Access control": "Only authorized people should access research data.",
        "Encryption": "Protect sensitive data at rest and during transmission.",
        "Data minimization": "Collect only information required for the stated purpose.",
        "Pseudonymization": "Separate participant identity from analytical records when possible.",
        "Retention": "Define how long research data should be retained.",
        "Auditability": "Maintain appropriate records of access and important changes.",
        "Secure deletion": "Dispose of data according to applicable policy and obligations.",
        "Consent management": "Record the basis and scope of participant consent where required.",
    }

    for control, description in controls.items():
        print(f"{control}: {description}")


# ---------------------------------------------------------------------------
# 27. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    explain_foundations()

    plan = build_research_plan()
    plan.display()

    participants = demonstrate_sampling()

    demonstrate_qualitative_coding(INTERVIEW_EXCERPTS)
    demonstrate_thematic_analysis(INTERVIEW_EXCERPTS)
    demonstrate_affinity_analysis()

    demonstrate_usability_metrics()
    demonstrate_survey_analysis()
    demonstrate_cross_tabulation()
    demonstrate_uncertainty()

    demonstrate_biases()
    demonstrate_triangulation()
    demonstrate_findings()

    discuss_research_quality()
    demonstrate_ethics()
    demonstrate_repository()
    demonstrate_prioritization()

    demonstrate_mixed_methods()
    discuss_advanced_concepts()
    demonstrate_edge_cases()
    demonstrate_common_mistakes()

    pipeline = ResearchPipeline()
    pipeline.execute_simulation()

    demonstrate_question_quality()

    print_section("24. Simulated Research Report")
    print(generate_research_report())

    demonstrate_performance()
    demonstrate_security()

    print_section("Research Study Complete")
    print(
        f"Participants passing the screening example: {len(participants)}"
    )
    print(
        "The examples above model a complete research workflow from "
        "question formulation through evidence collection, analysis, "
        "triangulation, quality assessment, and reporting."
    )


if __name__ == "__main__":
    main()
