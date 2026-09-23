"""
Customer Interviews: From Beginner Foundations to Advanced Practice

This standalone study script teaches customer interviewing as a product-research
discipline. It covers interview preparation, research objectives, participant
selection, question design, neutrality, bias, probing, active listening,
note-taking, evidence classification, synthesis, prioritization, and practical
analysis.

The examples use fictional data and do not require external packages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter, defaultdict
from typing import Iterable, Optional
import re
import statistics


# ---------------------------------------------------------------------------
# 1. FOUNDATIONS
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain_customer_interview() -> None:
    section("1. What is a customer interview?")

    print(
        """
A customer interview is a structured conversation used to understand a
person's experiences, behaviors, problems, goals, constraints, and decision
processes.

The objective is usually not to convince the participant, validate a product
idea, or collect compliments. The objective is to learn how the participant
currently behaves and why.

A useful distinction is:

    Opinion:
        "I think an automatic reminder would be useful."

    Behavior:
        "I currently put a reminder in my calendar after every appointment."

    Experience:
        "Last month I forgot an appointment because the reminder was buried
        among other notifications."

    Motivation:
        "I want to avoid missing appointments because rescheduling costs me
        time."

Behavior and concrete past experiences are often more informative than
hypothetical opinions because they describe what actually happened.
"""
    )


# ---------------------------------------------------------------------------
# 2. RESEARCH OBJECTIVES
# ---------------------------------------------------------------------------

@dataclass
class ResearchObjective:
    question: str
    evidence_needed: list[str]
    out_of_scope: list[str] = field(default_factory=list)

    def describe(self) -> None:
        print(f"\nResearch question: {self.question}")
        print("Evidence needed:")
        for item in self.evidence_needed:
            print(f"  - {item}")

        if self.out_of_scope:
            print("Out of scope:")
            for item in self.out_of_scope:
                print(f"  - {item}")


def create_research_objective() -> ResearchObjective:
    return ResearchObjective(
        question="How do small businesses currently track unpaid invoices?",
        evidence_needed=[
            "Current tools and workflow",
            "Frequency of invoice follow-up",
            "Recent examples of missed or delayed payments",
            "Time and effort involved",
            "Workarounds and alternatives",
            "Consequences of delayed payment",
        ],
        out_of_scope=[
            "Whether the participant likes our proposed product",
            "Whether the participant would download an app",
            "Hypothetical feature wish lists without behavioral context",
        ],
    )


# ---------------------------------------------------------------------------
# 3. INTERVIEW PREPARATION
# ---------------------------------------------------------------------------

@dataclass
class ParticipantProfile:
    participant_id: str
    role: str
    company_size: str
    relevant_experience: str

    def matches_criteria(self, required_role: str) -> bool:
        return self.role.lower() == required_role.lower()


def prepare_interview() -> None:
    section("2. Interview preparation")

    objective = create_research_objective()
    objective.describe()

    participants = [
        ParticipantProfile(
            "P01", "Owner", "1-10", "Personally follows up on customer invoices"
        ),
        ParticipantProfile(
            "P02", "Accountant", "11-50", "Manages invoice reconciliation"
        ),
        ParticipantProfile(
            "P03", "Designer", "1-10", "Does not handle billing"
        ),
    ]

    print("\nParticipant screening:")
    for participant in participants:
        suitable = participant.matches_criteria("Owner") or (
            participant.role.lower() == "accountant"
        )
        print(
            f"{participant.participant_id}: {participant.role} -> "
            f"{'eligible' if suitable else 'not eligible'}"
        )

    print(
        """
Preparation should define:

1. The research objective.
2. The target participant.
3. The recruiting criteria.
4. The interview format and duration.
5. The opening explanation.
6. The question guide.
7. The note-taking method.
8. The consent and privacy approach.
9. The evidence that will count as useful.
10. The analysis method.

A discussion guide should be a navigation aid rather than a rigid script.
The interviewer should follow relevant information when a participant
introduces something important.
"""
    )


# ---------------------------------------------------------------------------
# 4. QUESTION DESIGN
# ---------------------------------------------------------------------------

@dataclass
class InterviewQuestion:
    text: str
    purpose: str
    risk_flags: list[str] = field(default_factory=list)

    @property
    def is_high_risk(self) -> bool:
        return bool(self.risk_flags)


def evaluate_question(question: str) -> InterviewQuestion:
    lowered = question.lower()
    risk_flags: list[str] = []

    leading_patterns = [
        r"\bdon't you think\b",
        r"\bwouldn't you\b",
        r"\bwould you agree\b",
        r"\bisn't it\b",
        r"\bdo you like\b",
    ]

    hypothetical_patterns = [
        r"\bwould you use\b",
        r"\bwould you buy\b",
        r"\bwould you pay\b",
        r"\bwould you consider\b",
    ]

    double_barrel_markers = [" and ", " or "]

    if any(re.search(pattern, lowered) for pattern in leading_patterns):
        risk_flags.append("leading wording")

    if any(re.search(pattern, lowered) for pattern in hypothetical_patterns):
        risk_flags.append("hypothetical behavior")

    if any(marker in lowered for marker in double_barrel_markers):
        risk_flags.append("possibly double-barreled")

    if len(question.split()) > 30:
        risk_flags.append("too long or complex")

    return InterviewQuestion(
        text=question,
        purpose="Identify information about customer experience",
        risk_flags=risk_flags,
    )


def demonstrate_question_design() -> None:
    section("3. Question design")

    questions = [
        "What happened the last time you had to follow up on an unpaid invoice?",
        "How do you currently track unpaid invoices?",
        "What do you like about your current process?",
        "Don't you think automated reminders would save time?",
        "Would you use an application that automatically sends reminders?",
        "How do you track invoices and how do you decide when to contact customers?",
    ]

    for text in questions:
        result = evaluate_question(text)
        print(f"\nQuestion: {result.text}")
        if result.risk_flags:
            print("Potential issues:", ", ".join(result.risk_flags))
        else:
            print("Potential issues: none detected by this simple heuristic")

    print(
        """
Useful question forms include:

Open:
    "Tell me about the last time..."

Behavioral:
    "What did you do next?"

Contextual:
    "What was happening at the time?"

Frequency:
    "How often does that happen?"

Sequence:
    "What happens before that? What happens after that?"

Contrast:
    "How is this different from the way you handled it previously?"

Reflection:
    "What makes that difficult?"

Avoid turning the interview into a questionnaire. A participant's answer
should create opportunities for targeted follow-up questions.
"""
    )


# ---------------------------------------------------------------------------
# 5. BIAS DETECTION
# ---------------------------------------------------------------------------

@dataclass
class BiasCheck:
    question: str
    bias_type: str
    explanation: str
    revision: str


def bias_checks() -> list[BiasCheck]:
    return [
        BiasCheck(
            question="How much do you love our new dashboard?",
            bias_type="Leading question",
            explanation="The wording assumes the participant likes the dashboard.",
            revision="What was your experience using the dashboard?",
        ),
        BiasCheck(
            question="Would you use our product every day?",
            bias_type="Hypothetical bias",
            explanation="The participant predicts future behavior rather than "
                        "describing observed behavior.",
            revision="How do you currently perform this task?",
        ),
        BiasCheck(
            question="How easy and fast was the process?",
            bias_type="Double-barreled question",
            explanation="Ease and speed are separate dimensions.",
            revision="How easy was the process? How long did it take?",
        ),
        BiasCheck(
            question="Why did you fail to complete the process?",
            bias_type="Loaded wording",
            explanation="The word 'fail' assigns a negative interpretation.",
            revision="What happened when you tried to complete the process?",
        ),
    ]


def demonstrate_bias_detection() -> None:
    section("4. Avoiding interview bias")

    for check in bias_checks():
        print(f"\nOriginal: {check.question}")
        print(f"Bias: {check.bias_type}")
        print(f"Reason: {check.explanation}")
        print(f"Neutral revision: {check.revision}")

    print(
        """
Common sources of bias include:

- Leading wording
- Confirmation bias
- Selection bias
- Recall bias
- Social desirability bias
- Acquiescence bias
- Interviewer effects
- Order effects
- Sampling bias
- Survivorship bias
- Framing effects
- Hypothetical bias

Bias cannot usually be eliminated completely. The practical goal is to
identify important sources of distortion and reduce them systematically.
"""
    )


# ---------------------------------------------------------------------------
# 6. PROBING
# ---------------------------------------------------------------------------

PROBE_LIBRARY = {
    "clarification": [
        "What do you mean by that?",
        "Could you give me an example?",
    ],
    "sequence": [
        "What happened next?",
        "What happened immediately before that?",
    ],
    "frequency": [
        "How often does that happen?",
        "When did this last happen?",
    ],
    "impact": [
        "What effect did that have?",
        "What did you do because of that?",
    ],
    "root_cause": [
        "What makes that difficult?",
        "Why is that important to you?",
    ],
}


def choose_probe(answer: str) -> str:
    lowered = answer.lower()

    if "usually" in lowered or "often" in lowered:
        return PROBE_LIBRARY["frequency"][1]

    if "problem" in lowered or "difficult" in lowered:
        return PROBE_LIBRARY["impact"][0]

    if "then" in lowered or "after" in lowered:
        return PROBE_LIBRARY["sequence"][0]

    return PROBE_LIBRARY["clarification"][0]


def demonstrate_probing() -> None:
    section("5. Probing")

    answers = [
        "Usually I check it once a week.",
        "The biggest problem is that customers forget.",
        "Then I send an email and wait.",
        "It is complicated.",
    ]

    for answer in answers:
        print(f"Participant: {answer}")
        print(f"Possible probe: {choose_probe(answer)}\n")

    print(
        """
A good probe follows evidence already provided by the participant.

Weak probing:
    "What other features would you want?"

Evidence-oriented probing:
    "You mentioned that you started using a spreadsheet. When did you start
     doing that, and what problem were you trying to solve?"

The second approach moves from abstract preferences toward observable
experience.
"""
    )


# ---------------------------------------------------------------------------
# 7. ACTIVE LISTENING
# ---------------------------------------------------------------------------

@dataclass
class ListeningRecord:
    participant_statement: str
    interviewer_response: str
    listening_behavior: str


def demonstrate_active_listening() -> None:
    section("6. Active listening")

    records = [
        ListeningRecord(
            participant_statement="I stopped using the old system because it "
                                  "kept timing out.",
            interviewer_response="What happened the last time it timed out?",
            listening_behavior="Follow the concrete incident",
        ),
        ListeningRecord(
            participant_statement="I have a workaround now.",
            interviewer_response="Can you walk me through the workaround?",
            listening_behavior="Explore the current behavior",
        ),
        ListeningRecord(
            participant_statement="It is annoying, but I just deal with it.",
            interviewer_response="What do you normally do when that happens?",
            listening_behavior="Explore behavior instead of assuming severity",
        ),
    ]

    for record in records:
        print(f"\nParticipant: {record.participant_statement}")
        print(f"Response: {record.interviewer_response}")
        print(f"Listening principle: {record.listening_behavior}")

    print(
        """
Active listening involves more than staying silent. It includes:

- Paying attention to exact language.
- Detecting uncertainty.
- Reflecting important statements.
- Asking relevant follow-ups.
- Avoiding premature interpretation.
- Allowing pauses.
- Distinguishing what was said from what the interviewer assumes.

An interviewer should resist the urge to repair, defend, justify, or sell.
"""
    )


# ---------------------------------------------------------------------------
# 8. EVIDENCE CLASSIFICATION
# ---------------------------------------------------------------------------

@dataclass
class Evidence:
    text: str
    evidence_type: str
    confidence: str
    rationale: str


def classify_statement(statement: str) -> Evidence:
    lowered = statement.lower()

    if "last week" in lowered or "yesterday" in lowered or "last month" in lowered:
        return Evidence(
            statement,
            "recent behavioral evidence",
            "high",
            "The statement refers to a concrete past event.",
        )

    if lowered.startswith(("i think", "i believe", "i feel")):
        return Evidence(
            statement,
            "stated opinion",
            "medium",
            "The statement explicitly expresses a belief or opinion.",
        )

    if "would" in lowered or "might" in lowered:
        return Evidence(
            statement,
            "hypothetical intention",
            "low",
            "The statement describes possible future behavior.",
        )

    return Evidence(
        statement,
        "general statement",
        "medium",
        "The statement lacks enough context for stronger classification.",
    )


def demonstrate_evidence_classification() -> None:
    section("7. Evidence classification")

    statements = [
        "Last week I spent forty minutes reconciling three invoices.",
        "I think automation would be useful.",
        "I would probably use a mobile application.",
        "I usually check invoices on Fridays.",
    ]

    for statement in statements:
        evidence = classify_statement(statement)
        print(f"\nStatement: {evidence.text}")
        print(f"Type: {evidence.evidence_type}")
        print(f"Confidence: {evidence.confidence}")
        print(f"Reason: {evidence.rationale}")


# ---------------------------------------------------------------------------
# 9. NOTE-TAKING
# ---------------------------------------------------------------------------

@dataclass
class InterviewNote:
    participant_id: str
    observation: str
    direct_quote: Optional[str] = None
    interpretation: Optional[str] = None
    evidence_strength: str = "medium"


def separate_observation_from_interpretation() -> None:
    section("8. Note-taking")

    notes = [
        InterviewNote(
            participant_id="P01",
            observation="Participant opened a spreadsheet before answering.",
            direct_quote="I keep everything in this spreadsheet.",
            interpretation="The spreadsheet is probably central to the workflow.",
            evidence_strength="high",
        ),
        InterviewNote(
            participant_id="P02",
            observation="Participant paused before describing the current process.",
            direct_quote=None,
            interpretation="The process may be difficult.",
            evidence_strength="low",
        ),
    ]

    for note in notes:
        print(f"\nParticipant: {note.participant_id}")
        print(f"Observation: {note.observation}")
        print(f"Quote: {note.direct_quote or '[none]'}")
        print(f"Interpretation: {note.interpretation}")
        print(f"Evidence strength: {note.evidence_strength}")

    print(
        """
Keep three layers separate:

Observation:
    What happened or what the participant explicitly said.

Interpretation:
    What the researcher thinks the evidence may mean.

Hypothesis:
    A testable explanation that requires additional evidence.

This separation reduces accidental conversion of assumptions into facts.
"""
    )


# ---------------------------------------------------------------------------
# 10. SYNTHESIS
# ---------------------------------------------------------------------------

@dataclass
class InterviewFinding:
    participant_id: str
    theme: str
    statement: str
    frequency: Optional[int] = None


def group_findings_by_theme(
    findings: Iterable[InterviewFinding],
) -> dict[str, list[InterviewFinding]]:
    grouped: dict[str, list[InterviewFinding]] = defaultdict(list)

    for finding in findings:
        grouped[finding.theme].append(finding)

    return dict(grouped)


def synthesize_findings() -> None:
    section("9. Synthesizing interviews")

    findings = [
        InterviewFinding(
            "P01",
            "manual_work",
            "Uses a spreadsheet to track invoice status.",
        ),
        InterviewFinding(
            "P02",
            "manual_work",
            "Copies payment information into a spreadsheet.",
        ),
        InterviewFinding(
            "P03",
            "reminders",
            "Uses calendar reminders to remember follow-ups.",
        ),
        InterviewFinding(
            "P04",
            "manual_work",
            "Exports payment data and reconciles it manually.",
        ),
        InterviewFinding(
            "P05",
            "reminders",
            "Sets reminders after checking overdue invoices.",
        ),
    ]

    grouped = group_findings_by_theme(findings)

    for theme, theme_findings in grouped.items():
        print(f"\nTheme: {theme}")
        print(f"Participants represented: {len(theme_findings)}")

        for finding in theme_findings:
            print(f"  {finding.participant_id}: {finding.statement}")

    print(
        """
Do not treat frequency as the only measure of importance.

A theme can be:
    frequent + severe
    frequent + minor
    rare + severe
    rare + minor

A rare event may matter greatly in a safety-critical workflow, while a
frequent inconvenience may have relatively low consequences.
"""
    )


# ---------------------------------------------------------------------------
# 11. THEMATIC ANALYSIS
# ---------------------------------------------------------------------------

STOP_WORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is",
    "it", "i", "we", "this", "that", "with", "my", "our", "was", "are",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


def keyword_frequency(texts: Iterable[str]) -> Counter:
    counter = Counter()

    for text in texts:
        counter.update(tokenize(text))

    return counter


def demonstrate_thematic_analysis() -> None:
    section("10. Basic thematic analysis")

    transcripts = [
        "I use a spreadsheet because the accounting system is difficult to search.",
        "I check the spreadsheet every Friday before sending reminders.",
        "The accounting system contains the payment information but reconciliation "
        "still takes time.",
        "I use calendar reminders when an invoice becomes overdue.",
    ]

    frequency = keyword_frequency(transcripts)

    print("Frequent non-trivial terms:")
    for word, count in frequency.most_common(12):
        print(f"  {word}: {count}")

    print(
        """
Automated word counts can support analysis, but frequency alone does not
identify a meaningful theme. Context, participant meaning, severity,
sequence, and contradictory evidence remain important.
"""
    )


# ---------------------------------------------------------------------------
# 12. CONTRADICTIONS AND NEGATIVE CASES
# ---------------------------------------------------------------------------

def inspect_contradictions() -> None:
    section("11. Contradictions and negative cases")

    evidence = {
        "P01": "Manual spreadsheets are slow.",
        "P02": "Manual spreadsheets work well for our small team.",
        "P03": "Spreadsheets become difficult when invoice volume increases.",
    }

    for participant, statement in evidence.items():
        print(f"{participant}: {statement}")

    print(
        """
A strong synthesis should preserve disagreement.

Instead of:
    "Customers hate spreadsheets."

Prefer:
    "Participants differed. Some described spreadsheets as sufficient at
     current volume, while others reported increasing difficulty as volume
     increased."

Contradictory evidence often identifies segmentation variables such as:
    - company size
    - workflow complexity
    - frequency
    - expertise
    - regulatory requirements
    - transaction volume
"""
    )


# ---------------------------------------------------------------------------
# 13. INTERVIEW FLOW
# ---------------------------------------------------------------------------

@dataclass
class InterviewStage:
    name: str
    objective: str
    example_action: str


def show_interview_flow() -> None:
    section("12. A practical interview structure")

    stages = [
        InterviewStage(
            "Opening",
            "Create context and explain purpose.",
            "Explain that the discussion concerns the participant's experience.",
        ),
        InterviewStage(
            "Context",
            "Understand role and environment.",
            "Ask what responsibilities are connected to the workflow.",
        ),
        InterviewStage(
            "Recent experience",
            "Capture concrete behavior.",
            "Ask about the last time the participant performed the task.",
        ),
        InterviewStage(
            "Deep dive",
            "Understand difficulties, workarounds, and decisions.",
            "Probe important statements.",
        ),
        InterviewStage(
            "Contrast",
            "Understand alternatives and changes.",
            "Ask what they used before and why it changed.",
        ),
        InterviewStage(
            "Closing",
            "Capture omitted information.",
            "Ask what important issue was not discussed.",
        ),
    ]

    for stage in stages:
        print(f"\n{stage.name}")
        print(f"Objective: {stage.objective}")
        print(f"Action: {stage.example_action}")


# ---------------------------------------------------------------------------
# 14. INTERVIEW GUIDE GENERATOR
# ---------------------------------------------------------------------------

def generate_question_guide(
    research_topic: str,
    target_behavior: str,
) -> list[str]:
    return [
        f"Can you tell me about your role in {research_topic}?",
        f"When was the last time you {target_behavior}?",
        f"Can you walk me through what happened from beginning to end?",
        "What was difficult about that process?",
        "What did you do when that problem occurred?",
        "What alternatives have you tried?",
        "What made you change or keep your current approach?",
        "What happens when the process goes wrong?",
        "How frequently does this occur?",
        "What have I not asked about that is important to this workflow?",
    ]


def demonstrate_guide_generation() -> None:
    section("13. Generating a behavior-focused question guide")

    guide = generate_question_guide(
        research_topic="invoice management",
        target_behavior="follow up on an overdue invoice",
    )

    for number, question in enumerate(guide, start=1):
        print(f"{number}. {question}")


# ---------------------------------------------------------------------------
# 15. SAMPLE INTERVIEW SIMULATION
# ---------------------------------------------------------------------------

@dataclass
class SimulatedParticipant:
    name: str
    role: str
    responses: dict[str, str]

    def answer(self, topic: str) -> str:
        return self.responses.get(
            topic,
            "I do not have a specific example for that.",
        )


def run_interview_simulation() -> None:
    section("14. Simulated customer interview")

    participant = SimulatedParticipant(
        name="Participant 01",
        role="Small-business owner",
        responses={
            "recent_event": (
                "Last Tuesday I checked which invoices were overdue, copied "
                "the customer details into an email, and sent three reminders."
            ),
            "difficulty": (
                "The difficult part is remembering which customers have already "
                "received a reminder."
            ),
            "workaround": (
                "I add a note in the spreadsheet after sending an email."
            ),
            "impact": (
                "If I forget, payment can be delayed by another week."
            ),
        },
    )

    print(f"Participant role: {participant.role}")

    questions = [
        ("recent_event", "Tell me about the last time you followed up on an overdue invoice."),
        ("difficulty", "What was difficult about that process?"),
        ("workaround", "What do you do to manage that difficulty?"),
        ("impact", "What happens when the process does not go as planned?"),
    ]

    for topic, question in questions:
        answer = participant.answer(topic)
        print(f"\nInterviewer: {question}")
        print(f"Participant: {answer}")

        if topic == "difficulty":
            print(
                "Possible probe:",
                "Can you give me a recent example?",
            )


# ---------------------------------------------------------------------------
# 16. ADVANCED: EVIDENCE MATRIX
# ---------------------------------------------------------------------------

@dataclass
class EvidenceMatrixRow:
    participant: str
    behavior: str
    frequency: str
    consequence: str
    workaround: str
    confidence: str


def build_evidence_matrix() -> list[EvidenceMatrixRow]:
    return [
        EvidenceMatrixRow(
            "P01",
            "Checks overdue invoices manually",
            "Weekly",
            "Follow-up can be delayed",
            "Spreadsheet note",
            "High",
        ),
        EvidenceMatrixRow(
            "P02",
            "Exports reconciliation data",
            "Daily",
            "Consumes staff time",
            "Manual copy/paste",
            "High",
        ),
        EvidenceMatrixRow(
            "P03",
            "Uses calendar reminders",
            "Per invoice",
            "Occasional missed follow-up",
            "Calendar event",
            "Medium",
        ),
    ]


def demonstrate_evidence_matrix() -> None:
    section("15. Evidence matrix")

    rows = build_evidence_matrix()

    headers = [
        "Participant",
        "Behavior",
        "Frequency",
        "Consequence",
        "Workaround",
        "Confidence",
    ]

    print(" | ".join(headers))
    print("-" * 110)

    for row in rows:
        print(
            " | ".join(
                [
                    row.participant,
                    row.behavior,
                    row.frequency,
                    row.consequence,
                    row.workaround,
                    row.confidence,
                ]
            )
        )


# ---------------------------------------------------------------------------
# 17. ADVANCED: HYPOTHESIS TESTING
# ---------------------------------------------------------------------------

@dataclass
class ResearchHypothesis:
    statement: str
    supporting_evidence: list[str]
    contradicting_evidence: list[str]

    def evidence_balance(self) -> str:
        support = len(self.supporting_evidence)
        contradiction = len(self.contradicting_evidence)

        if support == 0 and contradiction == 0:
            return "No evidence"
        if contradiction > support:
            return "Contradictory evidence is substantial"
        if contradiction:
            return "Mixed evidence"
        return "Supporting evidence recorded"


def demonstrate_hypothesis_testing() -> None:
    section("16. Hypothesis testing")

    hypothesis = ResearchHypothesis(
        statement="Small businesses struggle with invoice follow-up.",
        supporting_evidence=[
            "P01 described manual tracking.",
            "P03 reported missed reminders.",
            "P04 described manual reconciliation.",
        ],
        contradicting_evidence=[
            "P02 reported that the existing process works at current volume.",
        ],
    )

    print("Hypothesis:", hypothesis.statement)
    print("Status:", hypothesis.evidence_balance())

    print("\nSupporting evidence:")
    for item in hypothesis.supporting_evidence:
        print(f"  + {item}")

    print("\nContradicting evidence:")
    for item in hypothesis.contradicting_evidence:
        print(f"  - {item}")

    print(
        """
The purpose of an interview study is not to force evidence toward an
existing hypothesis. Contradictory evidence should remain visible and may
lead to a narrower research statement.
"""
    )


# ---------------------------------------------------------------------------
# 18. SAMPLE-SIZE AND SATURATION CONCEPTS
# ---------------------------------------------------------------------------

def demonstrate_saturation() -> None:
    section("17. Saturation and sample size")

    interview_themes = [
        {"manual tracking", "reminders", "spreadsheet"},
        {"manual tracking", "reminders", "spreadsheet", "reconciliation"},
        {"manual tracking", "reminders", "spreadsheet"},
        {"manual tracking", "reminders", "calendar"},
        {"manual tracking", "spreadsheet"},
    ]

    cumulative: set[str] = set()

    for index, themes in enumerate(interview_themes, start=1):
        new_themes = themes - cumulative
        cumulative.update(themes)

        print(
            f"Interview {index}: new themes = "
            f"{sorted(new_themes) if new_themes else 'none'}"
        )

    print(
        """
There is no universal interview count that guarantees saturation.

Sample size depends on:
    - research objective
    - population heterogeneity
    - study design
    - risk of missing important cases
    - depth of interviews
    - number of relevant segments
    - available evidence

"Saturation" should be treated as an analytical judgment, not as a magic
number.
"""
    )


# ---------------------------------------------------------------------------
# 19. PRIVACY AND ETHICS
# ---------------------------------------------------------------------------

def demonstrate_ethics() -> None:
    section("18. Privacy and research ethics")

    sensitive_fields = {
        "name": "Direct identifier",
        "email": "Contact information",
        "salary": "Potentially sensitive personal information",
        "customer_data": "Potentially confidential business information",
    }

    print("Example fields requiring careful handling:")
    for field_name, reason in sensitive_fields.items():
        print(f"  {field_name}: {reason}")

    print(
        """
Good practices include:

- Collect only information needed for the research objective.
- Explain how the conversation will be used.
- Obtain appropriate consent when recording.
- Avoid collecting unnecessary personal information.
- Store research data securely.
- Separate identifiers from analytical notes where appropriate.
- Respect participant confidentiality.
- Avoid presenting a participant's statement as representative of an entire
  population without sufficient evidence.

A research participant is a source of evidence, not merely a source of
quotes.
"""
    )


# ---------------------------------------------------------------------------
# 20. INTERVIEW QUALITY CHECK
# ---------------------------------------------------------------------------

@dataclass
class InterviewQualityReview:
    question_neutrality: int
    behavioral_evidence: int
    probing_quality: int
    listening_quality: int
    documentation_quality: int

    def total(self) -> int:
        values = [
            self.question_neutrality,
            self.behavioral_evidence,
            self.probing_quality,
            self.listening_quality,
            self.documentation_quality,
        ]
        return sum(values)

    def average(self) -> float:
        values = [
            self.question_neutrality,
            self.behavioral_evidence,
            self.probing_quality,
            self.listening_quality,
            self.documentation_quality,
        ]
        return statistics.mean(values)


def review_interview_quality() -> None:
    section("19. Interview quality review")

    review = InterviewQualityReview(
        question_neutrality=4,
        behavioral_evidence=5,
        probing_quality=4,
        listening_quality=5,
        documentation_quality=4,
    )

    print(f"Recorded dimensions total: {review.total()}")
    print(f"Recorded dimensions average: {review.average():.2f}")

    print(
        """
This numerical example is a self-review aid rather than a universal quality
score. Interview quality cannot be reduced reliably to one number. The
dimensions should trigger reflection on specific research behaviors.
"""
    )


# ---------------------------------------------------------------------------
# 21. COMMON MISTAKES
# ---------------------------------------------------------------------------

def demonstrate_common_mistakes() -> None:
    section("20. Common mistakes")

    mistakes = {
        "Selling during the interview":
            "The interviewer changes from researcher to salesperson.",
        "Asking for opinions only":
            "Opinions without behavior or context can be weak evidence.",
        "Asking too many questions":
            "The conversation becomes a survey and leaves little room for probing.",
        "Filling every silence":
            "Important details may be lost before the participant finishes thinking.",
        "Ignoring contradictions":
            "The analysis becomes confirmation rather than research.",
        "Leading the participant":
            "The participant may agree with the interviewer's framing.",
        "Treating one participant as the market":
            "A single experience cannot automatically represent a population.",
        "Confusing severity with frequency":
            "A rare problem may still have major consequences.",
    }

    for mistake, consequence in mistakes.items():
        print(f"\n{mistake}:")
        print(f"  {consequence}")


# ---------------------------------------------------------------------------
# 22. END-TO-END RESEARCH WORKFLOW
# ---------------------------------------------------------------------------

def end_to_end_workflow() -> None:
    section("21. End-to-end customer interview workflow")

    workflow = [
        "Define the decision the research should inform.",
        "Convert the decision into research questions.",
        "Identify the relevant participant population.",
        "Define recruiting criteria.",
        "Create a flexible interview guide.",
        "Review questions for leading, hypothetical, double-barreled, and loaded wording.",
        "Conduct interviews using concrete past behavior as the primary evidence source.",
        "Probe important statements.",
        "Record observations separately from interpretations.",
        "Transcribe or organize evidence consistently.",
        "Code findings by theme.",
        "Preserve contradictory and negative cases.",
        "Compare themes across participant segments.",
        "Assess evidence strength and uncertainty.",
        "Identify research gaps.",
        "Use findings to inform product, service, or process decisions.",
    ]

    for index, step in enumerate(workflow, start=1):
        print(f"{index:02d}. {step}")


# ---------------------------------------------------------------------------
# 23. MINI CAPSTONE
# ---------------------------------------------------------------------------

def mini_capstone() -> None:
    section("22. Mini capstone: evaluating a proposed feature")

    print(
        """
Suppose a product team wants to build automatic invoice reminders.

A weak interview question:
    "Would you like automatic reminders?"

A stronger research sequence:

    1. "Tell me about the last overdue invoice you handled."
    2. "What did you do?"
    3. "How did you know it was overdue?"
    4. "What happened after you contacted the customer?"
    5. "How often does this occur?"
    6. "What tools are involved?"
    7. "What happens when a follow-up is missed?"
    8. "Have you tried changing this process?"
    9. "Why did you keep or abandon that approach?"
   10. "Is there anything difficult about this process that we have not discussed?"

Only after understanding the current workflow should a proposed solution be
introduced, and even then the interviewer should distinguish reactions to
the concept from evidence about the underlying problem.
"""
    )


# ---------------------------------------------------------------------------
# 24. RUN ALL LESSONS
# ---------------------------------------------------------------------------

def main() -> None:
    section("CUSTOMER INTERVIEWS: COMPLETE PRACTICAL STUDY")

    explain_customer_interview()
    prepare_interview()
    demonstrate_question_design()
    demonstrate_bias_detection()
    demonstrate_probing()
    demonstrate_active_listening()
    demonstrate_evidence_classification()
    separate_observation_from_interpretation()
    synthesize_findings()
    demonstrate_thematic_analysis()
    inspect_contradictions()
    show_interview_flow()
    demonstrate_guide_generation()
    run_interview_simulation()
    demonstrate_evidence_matrix()
    demonstrate_hypothesis_testing()
    demonstrate_saturation()
    demonstrate_ethics()
    review_interview_quality()
    demonstrate_common_mistakes()
    end_to_end_workflow()
    mini_capstone()

    section("Study complete")
    print(
        """
Core principle:
Study what people actually do, understand why they do it, probe concrete
experiences, separate evidence from interpretation, and preserve uncertainty
and contradictory evidence.
"""
    )


if __name__ == "__main__":
    main()
