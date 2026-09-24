"""
Interview Analysis: Notes, Coding, Patterns, Themes, Insights, Evidence vs Assumptions

A self-contained study and implementation file for analyzing interview data.

The script progresses from:
1. Raw interview notes
2. Data cleaning and segmentation
3. Descriptive coding
4. Codebook construction
5. Pattern detection
6. Theme development
7. Evidence extraction
8. Evidence-versus-assumption separation
9. Frequency and co-occurrence analysis
10. Participant-level analysis
11. Negative-case analysis
12. Confidence and triangulation
13. Lightweight qualitative scoring
14. Search and retrieval
15. Export-ready reporting
16. An end-to-end interview-analysis pipeline

Important methodological distinction:
- A note is an observation or transcription fragment.
- A code is a short analytic label attached to meaningful data.
- A pattern is a recurring or related observation across coded data.
- A theme is a broader interpretive concept supported by multiple pieces of evidence.
- An insight is an analytically useful interpretation derived from evidence.
- An assumption is an unsupported or insufficiently supported interpretation.
- Frequency is useful for orientation, but frequency alone does not establish importance.
- A single unusual observation can be analytically important even when it is rare.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum
import math
import re
import statistics
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


# ---------------------------------------------------------------------------
# 1. Core concepts represented as data structures
# ---------------------------------------------------------------------------

class EvidenceLevel(Enum):
    """
    A simple evidence classification.

    DIRECT:
        The participant explicitly said or demonstrated something.

    OBSERVED:
        The researcher directly observed behavior or an interaction.

    INTERPRETED:
        The analyst has inferred a meaning from direct evidence.

    ASSUMPTION:
        A claim is plausible but currently lacks sufficient supporting evidence.
    """

    DIRECT = "direct"
    OBSERVED = "observed"
    INTERPRETED = "interpreted"
    ASSUMPTION = "assumption"


class NoteType(Enum):
    QUOTE = "quote"
    PARAPHRASE = "paraphrase"
    OBSERVATION = "observation"
    CONTEXT = "context"


@dataclass
class InterviewNote:
    """
    One atomic unit of interview material.

    Keeping notes atomic makes coding, retrieval, comparison, and auditing easier.
    """

    note_id: str
    participant_id: str
    question_id: str
    text: str
    note_type: NoteType
    evidence_level: EvidenceLevel = EvidenceLevel.DIRECT
    timestamp_seconds: Optional[int] = None
    source_location: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class Code:
    """
    A code is a concise label representing a meaningful idea in the data.
    """

    code_id: str
    name: str
    definition: str
    inclusion_rule: str
    exclusion_rule: str
    parent_code: Optional[str] = None
    aliases: Set[str] = field(default_factory=set)


@dataclass
class CodingAssignment:
    """
    Connects one note to one code.

    Confidence refers to coding confidence, not truth of the underlying claim.
    """

    note_id: str
    code_id: str
    confidence: float
    rationale: str
    analyst: str = "primary"


@dataclass
class Pattern:
    pattern_id: str
    name: str
    description: str
    supporting_codes: List[str]
    supporting_notes: List[str]
    participant_count: int
    occurrence_count: int


@dataclass
class Theme:
    theme_id: str
    name: str
    research_question: str
    description: str
    supporting_patterns: List[str]
    supporting_notes: List[str]
    contradictory_notes: List[str]
    confidence: float


@dataclass
class Claim:
    """
    An explicit analytic statement.

    Claims are separated from raw evidence so that interpretation can be audited.
    """

    claim_id: str
    text: str
    level: EvidenceLevel
    supporting_note_ids: List[str]
    contradicting_note_ids: List[str] = field(default_factory=list)
    rationale: str = ""


# ---------------------------------------------------------------------------
# 2. Sample interview dataset
# ---------------------------------------------------------------------------

def build_sample_interview() -> List[InterviewNote]:
    """
    Creates a small but non-trivial dataset.

    The content models interviews with users of an internal analytics system.
    The same topic can appear positively and negatively, allowing contradiction
    and negative-case analysis.
    """

    raw = [
        (
            "N01", "P01", "Q01",
            "I usually start with the dashboard because it gives me the numbers "
            "I need without opening several spreadsheets.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N02", "P01", "Q02",
            "The dashboard saves time when I am preparing the weekly review.",
            NoteType.PARAPHRASE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N03", "P01", "Q03",
            "I still export the data to Excel when I need to combine it with "
            "information from another team.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N04", "P01", "Q04",
            "I trust the dashboard for totals, but I check unusual numbers "
            "against the source system.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N05", "P02", "Q01",
            "The dashboard is useful, but I often cannot find the metric I want.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N06", "P02", "Q02",
            "I spend time looking through filters before I can answer a question.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N07", "P02", "Q03",
            "When the dashboard is slow, I download the data and work locally.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N08", "P02", "Q04",
            "I am not sure whether the definitions of some metrics have changed.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N09", "P03", "Q01",
            "I mainly use the dashboard before meetings to check whether anything "
            "looks unusual.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N10", "P03", "Q02",
            "For normal questions it is fast enough, but detailed analysis takes "
            "me to spreadsheets.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N11", "P03", "Q03",
            "I prefer exporting because I can calculate things the dashboard does "
            "not provide.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N12", "P03", "Q04",
            "I ask colleagues when I do not understand where a number came from.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N13", "P04", "Q01",
            "I use the dashboard every day and rarely need another tool.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N14", "P04", "Q02",
            "The filters are easy for me because I only use a few standard views.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N15", "P04", "Q03",
            "I do not export data unless someone specifically asks for a file.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N16", "P04", "Q04",
            "The metric definitions are clear enough for my daily work.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N17", "P05", "Q01",
            "I like having everything in one place, but the interface feels crowded.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N18", "P05", "Q02",
            "I usually use saved views because changing filters takes too long.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N19", "P05", "Q03",
            "I export when I need to prepare a custom report.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
        (
            "N20", "P05", "Q04",
            "I would like clearer explanations of how metrics are calculated.",
            NoteType.QUOTE,
            EvidenceLevel.DIRECT,
        ),
    ]

    return [
        InterviewNote(
            note_id=item[0],
            participant_id=item[1],
            question_id=item[2],
            text=item[3],
            note_type=item[4],
            evidence_level=item[5],
        )
        for item in raw
    ]


# ---------------------------------------------------------------------------
# 3. Basic text processing
# ---------------------------------------------------------------------------

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "but", "by",
    "can", "do", "for", "from", "have", "i", "if", "in", "is", "it",
    "me", "my", "of", "on", "or", "so", "that", "the", "their", "this",
    "to", "use", "when", "with", "you", "your", "we", "our", "was",
    "were", "often", "usually", "still", "only", "more", "some",
}


def normalize_text(text: str) -> str:
    """Normalize whitespace and case without destroying the original note."""
    return re.sub(r"\s+", " ", text.strip())


def tokenize(text: str, remove_stop_words: bool = True) -> List[str]:
    """
    Tokenize text into simple word tokens.

    This is intentionally lightweight. Qualitative coding should not depend
    exclusively on automated NLP tokenization.
    """
    tokens = re.findall(r"[A-Za-z0-9']+", text.lower())
    if remove_stop_words:
        tokens = [token for token in tokens if token not in STOP_WORDS]
    return tokens


def word_frequencies(notes: Sequence[InterviewNote]) -> Counter:
    """Calculate exploratory word frequencies."""
    counts = Counter()
    for note in notes:
        counts.update(tokenize(note.text))
    return counts


def keyword_search(
    notes: Sequence[InterviewNote],
    query: str,
) -> List[InterviewNote]:
    """
    Case-insensitive keyword or phrase search.

    Search is a retrieval aid, not evidence of a theme by itself.
    """
    query_normalized = normalize_text(query).lower()
    return [
        note for note in notes
        if query_normalized in normalize_text(note.text).lower()
    ]


# ---------------------------------------------------------------------------
# 4. Codebook
# ---------------------------------------------------------------------------

def build_codebook() -> Dict[str, Code]:
    """
    Creates a transparent codebook.

    A good codebook specifies what belongs and what does not belong in a code.
    This reduces arbitrary coding decisions.
    """

    codes = [
        Code(
            "C01",
            "time saving",
            "The system reduces time or effort required to obtain information.",
            "Statements explicitly describing faster work, saved time, or reduced effort.",
            "Generic positive comments without a time or effort component.",
            aliases={"faster", "saves time", "efficient"},
        ),
        Code(
            "C02",
            "dashboard usefulness",
            "The dashboard directly supports a task or decision.",
            "Statements describing useful dashboard functionality or direct use.",
            "Statements describing only frustration or a missing capability.",
            aliases={"useful", "dashboard", "one place"},
        ),
        Code(
            "C03",
            "export dependency",
            "The participant moves data to another tool to complete work.",
            "Statements describing exports, spreadsheets, or local analysis.",
            "Mention of external tools unrelated to completing the analytical task.",
            aliases={"export", "excel", "spreadsheet", "local analysis"},
        ),
        Code(
            "C04",
            "findability problem",
            "The participant has difficulty locating a metric, view, or function.",
            "Statements describing search, navigation, or discovery difficulty.",
            "A statement merely saying that filters exist.",
            aliases={"cannot find", "find", "discover"},
        ),
        Code(
            "C05",
            "filter friction",
            "Filtering or changing views creates effort or delay.",
            "Statements describing difficulty, delay, or excessive work with filters.",
            "Statements saying filters are easy or routine.",
            aliases={"filters", "filter", "takes too long"},
        ),
        Code(
            "C06",
            "performance friction",
            "System speed or responsiveness disrupts work.",
            "Statements explicitly describing slowness or performance problems.",
            "General dissatisfaction without a performance reference.",
            aliases={"slow", "latency", "performance"},
        ),
        Code(
            "C07",
            "trust verification",
            "The participant verifies dashboard information against another source.",
            "Statements describing checking, validating, or questioning data.",
            "Statements that merely discuss metric definitions.",
            aliases={"trust", "check", "verify", "source"},
        ),
        Code(
            "C08",
            "metric ambiguity",
            "The participant lacks clarity about metric definitions or calculations.",
            "Statements describing uncertainty about definitions or calculations.",
            "A clear statement that definitions are understood.",
            aliases={"definitions", "calculation", "unclear metric"},
        ),
        Code(
            "C09",
            "workflow variation",
            "Different participants use materially different workflows.",
            "Evidence of distinct usage strategies for comparable tasks.",
            "Minor wording differences without workflow implications.",
            aliases={"different workflow", "usage variation"},
        ),
        Code(
            "C10",
            "meeting preparation",
            "The dashboard is used specifically to prepare for meetings or reviews.",
            "Statements explicitly linking dashboard use to meetings or reviews.",
            "General daily use without meeting preparation.",
            aliases={"meeting", "review", "before meetings"},
        ),
    ]

    return {code.code_id: code for code in codes}


# ---------------------------------------------------------------------------
# 5. Rule-assisted coding
# ---------------------------------------------------------------------------

def phrase_present(text: str, phrases: Iterable[str]) -> bool:
    normalized = normalize_text(text).lower()
    return any(phrase.lower() in normalized for phrase in phrases)


def auto_code_note(note: InterviewNote) -> List[CodingAssignment]:
    """
    Demonstrates transparent rule-assisted coding.

    The rules are intentionally visible. Automated coding should be treated as
    candidate coding that requires review, not as unquestionable truth.
    """

    text = note.text.lower()
    assignments: List[CodingAssignment] = []

    rules = {
        "C01": [
            "saves time", "save time", "faster", "quick", "quickly",
            "without opening several",
        ],
        "C02": [
            "dashboard is useful", "dashboard", "everything in one place",
            "useful",
        ],
        "C03": [
            "export", "excel", "spreadsheet", "work locally",
        ],
        "C04": [
            "cannot find", "can't find", "find the metric",
        ],
        "C05": [
            "filters", "filter", "changing filters", "takes too long",
        ],
        "C06": [
            "slow", "slower", "speed",
        ],
        "C07": [
            "trust", "check", "source system", "where a number came from",
        ],
        "C08": [
            "definitions", "metric definitions", "how metrics are calculated",
            "understand where",
        ],
        "C10": [
            "meeting", "meetings", "weekly review",
        ],
    }

    rationales = {
        "C01": "The note contains an explicit time or effort reduction.",
        "C02": "The note explicitly refers to dashboard utility or use.",
        "C03": "The note describes moving data to another analytical environment.",
        "C04": "The note explicitly describes difficulty locating information.",
        "C05": "The note references filtering or changing views.",
        "C06": "The note explicitly describes system slowness.",
        "C07": "The note describes verification or source checking.",
        "C08": "The note describes uncertainty about metric meaning or calculation.",
        "C10": "The note explicitly connects use with a meeting or review.",
    }

    for code_id, keywords in rules.items():
        if phrase_present(text, keywords):
            confidence = 0.88

            # Reduce confidence when the match is broad and potentially ambiguous.
            if code_id == "C02" and text.strip() == "dashboard":
                confidence = 0.55

            assignments.append(
                CodingAssignment(
                    note_id=note.note_id,
                    code_id=code_id,
                    confidence=confidence,
                    rationale=rationales[code_id],
                )
            )

    return assignments


def manual_refinement(
    notes: Sequence[InterviewNote],
    candidate_assignments: Sequence[CodingAssignment],
) -> List[CodingAssignment]:
    """
    Demonstrates analyst refinement.

    Some automated matches need contextual correction. For this dataset,
    "dashboard" by itself is not sufficient to prove usefulness.
    """
    note_map = {note.note_id: note for note in notes}
    refined = []

    for assignment in candidate_assignments:
        note = note_map[assignment.note_id]

        if assignment.code_id == "C02":
            if not phrase_present(note.text, [
                "useful",
                "saves time",
                "everything in one place",
                "use the dashboard",
                "dashboard is useful",
            ]):
                continue

        if assignment.code_id == "C05":
            if phrase_present(note.text, ["filters are easy"]):
                continue

        if assignment.code_id == "C08":
            if phrase_present(note.text, ["clear enough"]):
                continue

        refined.append(assignment)

    return refined


# ---------------------------------------------------------------------------
# 6. Coding matrix and code statistics
# ---------------------------------------------------------------------------

def assignments_by_code(
    assignments: Sequence[CodingAssignment],
) -> Dict[str, List[CodingAssignment]]:
    result: Dict[str, List[CodingAssignment]] = defaultdict(list)
    for assignment in assignments:
        result[assignment.code_id].append(assignment)
    return result


def assignments_by_note(
    assignments: Sequence[CodingAssignment],
) -> Dict[str, List[CodingAssignment]]:
    result: Dict[str, List[CodingAssignment]] = defaultdict(list)
    for assignment in assignments:
        result[assignment.note_id].append(assignment)
    return result


def code_frequency(
    assignments: Sequence[CodingAssignment],
) -> Counter:
    return Counter(assignment.code_id for assignment in assignments)


def participant_count_by_code(
    assignments: Sequence[CodingAssignment],
    notes: Sequence[InterviewNote],
) -> Dict[str, int]:
    note_map = {note.note_id: note for note in notes}
    participants: Dict[str, Set[str]] = defaultdict(set)

    for assignment in assignments:
        participant = note_map[assignment.note_id].participant_id
        participants[assignment.code_id].add(participant)

    return {code_id: len(ids) for code_id, ids in participants.items()}


def build_coding_matrix(
    notes: Sequence[InterviewNote],
    codes: Sequence[Code],
    assignments: Sequence[CodingAssignment],
) -> Dict[str, Dict[str, int]]:
    """
    Returns a participant/code matrix.

    A value of 1 means at least one note from the participant received that code.
    """
    matrix: Dict[str, Dict[str, int]] = {}

    for note in notes:
        matrix.setdefault(note.participant_id, {})
        for code in codes:
            matrix[note.participant_id].setdefault(code.code_id, 0)

    for assignment in assignments:
        participant = next(
            note.participant_id for note in notes
            if note.note_id == assignment.note_id
        )
        matrix[participant][assignment.code_id] = 1

    return matrix


# ---------------------------------------------------------------------------
# 7. Co-occurrence analysis
# ---------------------------------------------------------------------------

def code_cooccurrence(
    assignments: Sequence[CodingAssignment],
) -> Counter:
    """
    Counts pairs of codes appearing on the same note.

    Co-occurrence can suggest relationships but does not prove causality.
    """
    grouped = assignments_by_note(assignments)
    pairs = Counter()

    for note_assignments in grouped.values():
        code_ids = sorted({
            assignment.code_id for assignment in note_assignments
        })

        for index, left in enumerate(code_ids):
            for right in code_ids[index + 1:]:
                pairs[(left, right)] += 1

    return pairs


def jaccard_similarity(
    left: Set[str],
    right: Set[str],
) -> float:
    """Similarity based on intersection over union."""
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def code_participant_sets(
    assignments: Sequence[CodingAssignment],
    notes: Sequence[InterviewNote],
) -> Dict[str, Set[str]]:
    note_map = {note.note_id: note for note in notes}
    result: Dict[str, Set[str]] = defaultdict(set)

    for assignment in assignments:
        result[assignment.code_id].add(
            note_map[assignment.note_id].participant_id
        )

    return result


# ---------------------------------------------------------------------------
# 8. Pattern detection
# ---------------------------------------------------------------------------

def detect_patterns(
    notes: Sequence[InterviewNote],
    assignments: Sequence[CodingAssignment],
) -> List[Pattern]:
    """
    Converts repeated code combinations into higher-level patterns.

    The rules are explicit and therefore auditable.
    """
    grouped = assignments_by_note(assignments)
    note_map = {note.note_id: note for note in notes}

    pattern_rules = [
        (
            "P01",
            "dashboard-to-spreadsheet workflow",
            "Participants use the dashboard for initial information retrieval "
            "and move to spreadsheets or local analysis for more customized work.",
            {"C02", "C03"},
        ),
        (
            "P02",
            "verification behavior",
            "Participants validate or question dashboard information using another source.",
            {"C07"},
        ),
        (
            "P03",
            "navigation and filtering friction",
            "Participants experience difficulty locating information or configuring views.",
            {"C04", "C05"},
        ),
        (
            "P04",
            "metric understanding gap",
            "Participants experience uncertainty about metric definitions or calculations.",
            {"C08"},
        ),
        (
            "P05",
            "meeting-oriented use",
            "Dashboard use is connected with meeting or review preparation.",
            {"C10"},
        ),
        (
            "P06",
            "performance-driven workaround",
            "Slow system response leads users to move analysis outside the system.",
            {"C03", "C06"},
        ),
    ]

    patterns = []

    for pattern_id, name, description, required_codes in pattern_rules:
        supporting_notes = []

        for note_id, note_assignments in grouped.items():
            codes_on_note = {
                assignment.code_id for assignment in note_assignments
            }

            if required_codes <= codes_on_note:
                supporting_notes.append(note_id)

        if not supporting_notes:
            # A single-code pattern can still be meaningful.
            for note_id, note_assignments in grouped.items():
                codes_on_note = {
                    assignment.code_id for assignment in note_assignments
                }
                if len(required_codes) == 1 and required_codes <= codes_on_note:
                    supporting_notes.append(note_id)

        if supporting_notes:
            participants = {
                note_map[note_id].participant_id
                for note_id in supporting_notes
            }

            patterns.append(
                Pattern(
                    pattern_id=pattern_id,
                    name=name,
                    description=description,
                    supporting_codes=sorted(required_codes),
                    supporting_notes=supporting_notes,
                    participant_count=len(participants),
                    occurrence_count=len(supporting_notes),
                )
            )

    return patterns


# ---------------------------------------------------------------------------
# 9. Theme construction
# ---------------------------------------------------------------------------

def build_themes(
    notes: Sequence[InterviewNote],
    assignments: Sequence[CodingAssignment],
    patterns: Sequence[Pattern],
) -> List[Theme]:
    """
    Constructs themes from patterns.

    Theme construction remains interpretive. The function makes the reasoning
    visible rather than pretending that a mathematical formula discovers themes.
    """
    note_map = {note.note_id: note for note in notes}
    pattern_map = {pattern.pattern_id: pattern for pattern in patterns}

    theme_specs = [
        (
            "T01",
            "efficiency with boundary conditions",
            "How does the system affect work efficiency?",
            "The dashboard can reduce initial information-gathering effort, "
            "but efficiency depends on task complexity, navigation, and "
            "whether the required analysis fits the dashboard.",
            ["P01", "P03", "P06"],
        ),
        (
            "T02",
            "dashboard as an entry point rather than a complete workflow",
            "How does the system fit into users' broader analytical workflows?",
            "The dashboard frequently serves as a starting point, while "
            "custom analysis continues in spreadsheets or local tools.",
            ["P01", "P06"],
        ),
        (
            "T03",
            "trust depends on interpretability and verification",
            "What affects confidence in dashboard information?",
            "Participants describe verification behavior and uncertainty "
            "when metric definitions or calculations are unclear.",
            ["P02", "P04"],
        ),
        (
            "T04",
            "usage varies by task and user",
            "How consistently is the system used?",
            "The interviews show materially different workflows, ranging from "
            "daily dashboard-only use to frequent exports and local analysis.",
            ["P01", "P03"],
        ),
    ]

    themes = []

    for theme_id, name, question, description, pattern_ids in theme_specs:
        valid_pattern_ids = [
            pattern_id for pattern_id in pattern_ids
            if pattern_id in pattern_map
        ]

        supporting_notes = []
        for pattern_id in valid_pattern_ids:
            supporting_notes.extend(pattern_map[pattern_id].supporting_notes)

        supporting_notes = sorted(set(supporting_notes))

        # Search for contradictory evidence.
        contradictory_notes = []

        if theme_id == "T01":
            for note in notes:
                if phrase_present(note.text, [
                    "filters are easy",
                    "rarely need another tool",
                    "clear enough",
                ]):
                    contradictory_notes.append(note.note_id)

        if theme_id == "T02":
            for note in notes:
                if phrase_present(note.text, [
                    "rarely need another tool",
                    "do not export data",
                ]):
                    contradictory_notes.append(note.note_id)

        if theme_id == "T03":
            for note in notes:
                if phrase_present(note.text, ["clear enough"]):
                    contradictory_notes.append(note.note_id)

        if theme_id == "T04":
            contradictory_notes = []

        support = len(supporting_notes)
        contradiction = len(contradictory_notes)

        # This is not a truth probability. It is an explicit support indicator.
        confidence = support / (support + contradiction) if support + contradiction else 0

        themes.append(
            Theme(
                theme_id=theme_id,
                name=name,
                research_question=question,
                description=description,
                supporting_patterns=valid_pattern_ids,
                supporting_notes=supporting_notes,
                contradictory_notes=contradictory_notes,
                confidence=round(confidence, 3),
            )
        )

    return themes


# ---------------------------------------------------------------------------
# 10. Evidence versus assumptions
# ---------------------------------------------------------------------------

def classify_claims(notes: Sequence[InterviewNote]) -> List[Claim]:
    """
    Demonstrates the separation between evidence and interpretation.

    The examples deliberately include an unsupported assumption so the analyst
    can see how the distinction works.
    """

    note_map = {note.note_id: note for note in notes}

    claims = [
        Claim(
            "CL01",
            "P01 reports that the dashboard reduces the need to open several spreadsheets.",
            EvidenceLevel.DIRECT,
            ["N01"],
            rationale="The participant explicitly described the workflow.",
        ),
        Claim(
            "CL02",
            "The dashboard saves time for every user.",
            EvidenceLevel.ASSUMPTION,
            ["N02"],
            rationale="One participant's statement cannot establish a universal claim.",
        ),
        Claim(
            "CL03",
            "Some participants use the dashboard as an initial step and then export data.",
            EvidenceLevel.INTERPRETED,
            ["N01", "N03", "N10", "N11", "N19"],
            rationale="Multiple direct observations support a broader workflow interpretation.",
        ),
        Claim(
            "CL04",
            "Metric ambiguity may reduce confidence in dashboard information.",
            EvidenceLevel.INTERPRETED,
            ["N04", "N08", "N12", "N20"],
            rationale="Verification behavior and uncertainty about definitions appear together.",
        ),
        Claim(
            "CL05",
            "Every participant dislikes the dashboard interface.",
            EvidenceLevel.ASSUMPTION,
            ["N17"],
            rationale="The dataset contains participants who report positive experiences.",
        ),
    ]

    # Validate referenced IDs so claims remain auditable.
    valid_ids = set(note_map)
    for claim in claims:
        missing = set(claim.supporting_note_ids) - valid_ids
        if missing:
            raise ValueError(
                f"Claim {claim.claim_id} references missing notes: {missing}"
            )

    return claims


def evidence_strength(
    claim: Claim,
    notes: Sequence[InterviewNote],
) -> float:
    """
    Provides a heuristic evidence-support indicator.

    This is not statistical significance and should not be interpreted as one.
    It considers:
    - number of supporting notes
    - number of participants
    - contradiction
    - direct versus interpreted status
    """
    note_map = {note.note_id: note for note in notes}
    support_notes = [
        note_map[note_id]
        for note_id in claim.supporting_note_ids
        if note_id in note_map
    ]

    if not support_notes:
        return 0.0

    participant_count = len({
        note.participant_id for note in support_notes
    })

    direct_count = sum(
        note.evidence_level == EvidenceLevel.DIRECT
        for note in support_notes
    )

    support_component = min(len(support_notes) / 5, 1.0)
    participant_component = min(participant_count / 5, 1.0)
    direct_component = direct_count / len(support_notes)

    contradiction_component = (
        1 / (1 + len(claim.contradicting_note_ids))
    )

    level_multiplier = {
        EvidenceLevel.DIRECT: 1.00,
        EvidenceLevel.OBSERVED: 0.95,
        EvidenceLevel.INTERPRETED: 0.75,
        EvidenceLevel.ASSUMPTION: 0.15,
    }[claim.level]

    score = (
        0.30 * support_component
        + 0.30 * participant_component
        + 0.20 * direct_component
        + 0.20 * contradiction_component
    ) * level_multiplier

    return round(score, 3)


# ---------------------------------------------------------------------------
# 11. Negative-case analysis
# ---------------------------------------------------------------------------

def find_negative_cases(
    notes: Sequence[InterviewNote],
    themes: Sequence[Theme],
) -> Dict[str, List[str]]:
    """
    Finds notes that challenge themes.

    Negative cases are important because they prevent analysts from treating
    repeated evidence as universal evidence.
    """
    result = {}

    for theme in themes:
        result[theme.theme_id] = theme.contradictory_notes

    return result


# ---------------------------------------------------------------------------
# 12. Participant profiles
# ---------------------------------------------------------------------------

def participant_profiles(
    notes: Sequence[InterviewNote],
    assignments: Sequence[CodingAssignment],
    codebook: Dict[str, Code],
) -> Dict[str, Dict[str, object]]:
    """
    Builds concise participant-level profiles.

    Participant profiles help preserve within-case analysis before cross-case
    aggregation.
    """
    note_map = {note.note_id: note for note in notes}
    result: Dict[str, Dict[str, object]] = {}

    grouped = defaultdict(list)
    for assignment in assignments:
        grouped[note_map[assignment.note_id].participant_id].append(assignment)

    for participant in sorted({note.participant_id for note in notes}):
        participant_assignments = grouped.get(participant, [])

        counts = Counter(
            assignment.code_id
            for assignment in participant_assignments
        )

        code_names = [
            codebook[code_id].name
            for code_id, _ in counts.most_common()
        ]

        result[participant] = {
            "note_count": sum(
                note.participant_id == participant for note in notes
            ),
            "code_count": len(participant_assignments),
            "top_codes": code_names[:5],
        }

    return result


# ---------------------------------------------------------------------------
# 13. Diversity and saturation-oriented indicators
# ---------------------------------------------------------------------------

def unique_codes_per_interview(
    notes: Sequence[InterviewNote],
    assignments: Sequence[CodingAssignment],
) -> Dict[str, int]:
    note_map = {note.note_id: note for note in notes}
    grouped = defaultdict(set)

    for assignment in assignments:
        grouped[note_map[assignment.note_id].participant_id].add(
            assignment.code_id
        )

    return {
        participant: len(codes)
        for participant, codes in sorted(grouped.items())
    }


def incremental_code_coverage(
    notes: Sequence[InterviewNote],
    assignments: Sequence[CodingAssignment],
) -> List[Tuple[int, str, int]]:
    """
    Calculates cumulative unique codes as interviews are added.

    This can help inspect whether later interviews are still introducing
    substantially new concepts. It is not, by itself, proof of saturation.
    """
    note_map = {note.note_id: note for note in notes}
    participant_order = sorted({
        note.participant_id for note in notes
    })

    codes_seen: Set[str] = set()
    output = []

    for index, participant in enumerate(participant_order, start=1):
        participant_codes = {
            assignment.code_id
            for assignment in assignments
            if note_map[assignment.note_id].participant_id == participant
        }

        new_codes = participant_codes - codes_seen
        codes_seen.update(participant_codes)

        output.append((index, participant, len(new_codes)))

    return output


# ---------------------------------------------------------------------------
# 14. Simple similarity analysis
# ---------------------------------------------------------------------------

def note_term_set(note: InterviewNote) -> Set[str]:
    return set(tokenize(note.text))


def most_similar_note_pairs(
    notes: Sequence[InterviewNote],
    minimum_similarity: float = 0.20,
) -> List[Tuple[str, str, float]]:
    """
    Uses Jaccard similarity on content words.

    This is a lightweight exploratory technique. Semantic similarity would
    require a more sophisticated representation, but lexical similarity is
    transparent and dependency-free.
    """
    results = []

    for index, left in enumerate(notes):
        left_terms = note_term_set(left)

        for right in notes[index + 1:]:
            right_terms = note_term_set(right)
            similarity = jaccard_similarity(left_terms, right_terms)

            if similarity >= minimum_similarity:
                results.append((
                    left.note_id,
                    right.note_id,
                    round(similarity, 3),
                ))

    return sorted(results, key=lambda item: item[2], reverse=True)


# ---------------------------------------------------------------------------
# 15. Qualitative scoring without pretending it is statistical proof
# ---------------------------------------------------------------------------

def thematic_support_score(
    theme: Theme,
    notes: Sequence[InterviewNote],
) -> Dict[str, float]:
    """
    Produces descriptive support indicators.

    The score should not be reported as a probability or significance test.
    """
    note_map = {note.note_id: note for note in notes}

    participants = {
        note_map[note_id].participant_id
        for note_id in theme.supporting_notes
    }

    contradiction_participants = {
        note_map[note_id].participant_id
        for note_id in theme.contradictory_notes
    }

    participant_coverage = (
        len(participants) / len({
            note.participant_id for note in notes
        })
        if notes else 0
    )

    contradiction_rate = (
        len(contradiction_participants) /
        max(len(participants | contradiction_participants), 1)
    )

    return {
        "supporting_notes": float(len(theme.supporting_notes)),
        "supporting_participants": float(len(participants)),
        "participant_coverage": round(participant_coverage, 3),
        "contradicting_notes": float(len(theme.contradictory_notes)),
        "contradiction_rate": round(contradiction_rate, 3),
        "analyst_confidence_indicator": theme.confidence,
    }


# ---------------------------------------------------------------------------
# 16. Querying coded data
# ---------------------------------------------------------------------------

def notes_for_code(
    code_id: str,
    assignments: Sequence[CodingAssignment],
    notes: Sequence[InterviewNote],
) -> List[InterviewNote]:
    note_map = {note.note_id: note for note in notes}

    note_ids = {
        assignment.note_id
        for assignment in assignments
        if assignment.code_id == code_id
    }

    return [
        note
        for note in notes
        if note.note_id in note_ids
    ]


def participants_for_code(
    code_id: str,
    assignments: Sequence[CodingAssignment],
    notes: Sequence[InterviewNote],
) -> Set[str]:
    return {
        note.participant_id
        for note in notes_for_code(code_id, assignments, notes)
    }


# ---------------------------------------------------------------------------
# 17. Auditability
# ---------------------------------------------------------------------------

def audit_coding(
    notes: Sequence[InterviewNote],
    assignments: Sequence[CodingAssignment],
    codebook: Dict[str, Code],
) -> List[str]:
    """
    Checks structural quality of the coding dataset.
    """
    errors = []
    note_ids = {note.note_id for note in notes}

    for assignment in assignments:
        if assignment.note_id not in note_ids:
            errors.append(
                f"Assignment references unknown note: {assignment.note_id}"
            )

        if assignment.code_id not in codebook:
            errors.append(
                f"Assignment references unknown code: {assignment.code_id}"
            )

        if not 0 <= assignment.confidence <= 1:
            errors.append(
                f"Invalid confidence for {assignment.note_id}/{assignment.code_id}"
            )

        if not assignment.rationale.strip():
            errors.append(
                f"Missing rationale for {assignment.note_id}/{assignment.code_id}"
            )

    return errors


# ---------------------------------------------------------------------------
# 18. Reporting helpers
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_note_table(notes: Sequence[InterviewNote]) -> None:
    print(f"{'ID':<5} {'Participant':<12} {'Question':<8} {'Evidence':<12} Text")
    print("-" * 78)

    for note in notes:
        text = note.text
        if len(text) > 62:
            text = text[:59] + "..."
        print(
            f"{note.note_id:<5} "
            f"{note.participant_id:<12} "
            f"{note.question_id:<8} "
            f"{note.evidence_level.value:<12} "
            f"{text}"
        )


def print_code_statistics(
    assignments: Sequence[CodingAssignment],
    notes: Sequence[InterviewNote],
    codebook: Dict[str, Code],
) -> None:
    frequencies = code_frequency(assignments)
    participant_counts = participant_count_by_code(assignments, notes)

    print(f"{'Code':<6} {'Name':<32} {'Occurrences':<12} Participants")
    print("-" * 78)

    for code_id, count in frequencies.most_common():
        print(
            f"{code_id:<6} "
            f"{codebook[code_id].name:<32} "
            f"{count:<12} "
            f"{participant_counts.get(code_id, 0)}"
        )


def print_patterns(
    patterns: Sequence[Pattern],
) -> None:
    for pattern in patterns:
        print(f"\n{pattern.pattern_id}: {pattern.name}")
        print(f"  Description: {pattern.description}")
        print(f"  Supporting codes: {', '.join(pattern.supporting_codes)}")
        print(f"  Occurrences: {pattern.occurrence_count}")
        print(f"  Participants: {pattern.participant_count}")
        print(f"  Notes: {', '.join(pattern.supporting_notes)}")


def print_themes(
    themes: Sequence[Theme],
    notes: Sequence[InterviewNote],
) -> None:
    for theme in themes:
        metrics = thematic_support_score(theme, notes)

        print(f"\n{theme.theme_id}: {theme.name}")
        print(f"  Research question: {theme.research_question}")
        print(f"  Description: {theme.description}")
        print(f"  Patterns: {', '.join(theme.supporting_patterns)}")
        print(f"  Supporting notes: {', '.join(theme.supporting_notes)}")
        print(
            f"  Contradictory notes: "
            f"{', '.join(theme.contradictory_notes) or 'None identified'}"
        )
        print(f"  Support metrics: {metrics}")


def print_claim_audit(
    claims: Sequence[Claim],
    notes: Sequence[InterviewNote],
) -> None:
    for claim in claims:
        score = evidence_strength(claim, notes)
        print(f"\n{claim.claim_id}: {claim.text}")
        print(f"  Classification: {claim.level.value}")
        print(f"  Supporting notes: {', '.join(claim.supporting_note_ids)}")
        print(
            "  Contradicting notes: "
            + (", ".join(claim.contradicting_note_ids) or "None")
        )
        print(f"  Rationale: {claim.rationale}")
        print(f"  Evidence-support indicator: {score}")


# ---------------------------------------------------------------------------
# 19. End-to-end pipeline
# ---------------------------------------------------------------------------

def run_analysis() -> None:
    notes = build_sample_interview()
    codebook = build_codebook()

    # Preserve raw text but normalize whitespace for downstream processing.
    for note in notes:
        note.text = normalize_text(note.text)

    print_section("Interview dataset")
    print_note_table(notes)

    print_section("Exploratory vocabulary")
    frequencies = word_frequencies(notes)

    for word, count in frequencies.most_common(20):
        print(f"{word:<20} {count}")

    print_section("Rule-assisted candidate coding")

    candidate_assignments = []
    for note in notes:
        candidate_assignments.extend(auto_code_note(note))

    print(f"Candidate assignments: {len(candidate_assignments)}")

    assignments = manual_refinement(
        notes,
        candidate_assignments,
    )

    print(f"Reviewed assignments: {len(assignments)}")

    print_section("Coding audit")
    errors = audit_coding(notes, assignments, codebook)

    if errors:
        for error in errors:
            print("ERROR:", error)
    else:
        print("No structural coding errors detected.")

    print_section("Code statistics")
    print_code_statistics(assignments, notes, codebook)

    print_section("Code co-occurrence")
    cooccurrence = code_cooccurrence(assignments)

    for (left, right), count in cooccurrence.most_common():
        print(
            f"{left} ({codebook[left].name}) + "
            f"{right} ({codebook[right].name}): {count}"
        )

    print_section("Participant-level coding matrix")
    matrix = build_coding_matrix(
        notes,
        list(codebook.values()),
        assignments,
    )

    code_ids = list(codebook)
    header = "Participant".ljust(14) + " ".join(
        code_id.rjust(4) for code_id in code_ids
    )
    print(header)
    print("-" * len(header))

    for participant, values in matrix.items():
        row = participant.ljust(14)
        row += " ".join(
            str(values[code_id]).rjust(4)
            for code_id in code_ids
        )
        print(row)

    print_section("Patterns")
    patterns = detect_patterns(notes, assignments)
    print_patterns(patterns)

    print_section("Themes")
    themes = build_themes(
        notes,
        assignments,
        patterns,
    )
    print_themes(themes, notes)

    print_section("Evidence versus assumptions")
    claims = classify_claims(notes)
    print_claim_audit(claims, notes)

    print_section("Negative-case analysis")
    negative_cases = find_negative_cases(notes, themes)

    for theme_id, note_ids in negative_cases.items():
        print(
            f"{theme_id}: "
            f"{', '.join(note_ids) if note_ids else 'No contradictory notes identified'}"
        )

    print_section("Participant profiles")
    profiles = participant_profiles(
        notes,
        assignments,
        codebook,
    )

    for participant, profile in profiles.items():
        print(participant, profile)

    print_section("Code diversity by participant")
    diversity = unique_codes_per_interview(notes, assignments)

    for participant, count in diversity.items():
        print(f"{participant}: {count} unique codes")

    print_section("Incremental code coverage")
    for interview_number, participant, new_code_count in incremental_code_coverage(
        notes,
        assignments,
    ):
        print(
            f"Interview {interview_number} ({participant}): "
            f"{new_code_count} newly observed codes"
        )

    print_section("Lexical similarity")
    pairs = most_similar_note_pairs(notes)

    for left, right, similarity in pairs[:10]:
        print(f"{left} <-> {right}: {similarity}")

    print_section("Keyword retrieval")
    query = "export"
    matches = keyword_search(notes, query)

    print(f"Query: {query}")
    for note in matches:
        print(f"{note.note_id}: {note.text}")

    print_section("Code-specific retrieval")
    export_notes = notes_for_code(
        "C03",
        assignments,
        notes,
    )

    print("Notes coded as export dependency:")
    for note in export_notes:
        print(f"{note.note_id}: {note.text}")

    print_section("Evidence concepts demonstrated")
    concepts = [
        "Raw notes must remain traceable.",
        "Coding is different from summarizing.",
        "A code should have a definition and boundary.",
        "Patterns connect recurring observations.",
        "Themes integrate related patterns into an analytic explanation.",
        "Insights should be traceable to evidence.",
        "Assumptions must be labeled rather than presented as findings.",
        "Contradictory evidence should be actively searched for.",
        "Participant counts describe distribution, not statistical significance.",
        "Frequency does not automatically equal importance.",
        "Automated coding is a candidate-generation mechanism, not a replacement for judgment.",
        "A reproducible analysis should preserve an audit trail.",
    ]

    for number, concept in enumerate(concepts, start=1):
        print(f"{number:02d}. {concept}")

    print_section("Example final analytical statements")

    final_statements = [
        "Several participants use the dashboard for rapid information retrieval, "
        "while more customized analysis frequently continues in spreadsheets.",
        "The need to export data appears to be associated with analytical tasks "
        "that exceed the dashboard's available calculations or views.",
        "Trust is not uniformly absent or present; participants describe "
        "verification behavior and different levels of confidence depending on "
        "metric clarity and the situation.",
        "The interviews contain meaningful variation: one participant reports "
        "rarely needing another tool, while others rely on exports or local analysis.",
    ]

    for statement in final_statements:
        print(f"- {statement}")

    print_section("Methodological cautions")
    cautions = [
        "Do not convert a small interview sample into population-level statistics.",
        "Do not treat the most frequent code as automatically the most important theme.",
        "Do not remove contradictory evidence simply because it weakens a preferred interpretation.",
        "Do not confuse participant opinion with independently verified fact.",
        "Do not rewrite interpretations as if participants explicitly stated them.",
        "Do not use coding confidence as a measure of participant truthfulness.",
        "Do not infer causality merely because two codes co-occur.",
        "Do not claim saturation solely because no new code appeared in one interview.",
    ]

    for caution in cautions:
        print(f"- {caution}")


# ---------------------------------------------------------------------------
# 20. Additional advanced demonstrations
# ---------------------------------------------------------------------------

def demonstrate_advanced_concepts() -> None:
    """
    Compact demonstrations of concepts useful in more advanced interview analysis.
    """

    print_section("Advanced concept: code hierarchy")

    parent = Code(
        code_id="PARENT01",
        name="workflow friction",
        definition="Difficulty that interferes with completing an analytical task.",
        inclusion_rule="A task is made harder, slower, or less direct.",
        exclusion_rule="General dislike without a workflow consequence.",
    )

    children = [
        Code(
            code_id="CHILD01",
            name="filter friction",
            definition="Difficulty configuring filters.",
            inclusion_rule="Filtering causes effort or delay.",
            exclusion_rule="Filtering is described as easy.",
            parent_code=parent.code_id,
        ),
        Code(
            code_id="CHILD02",
            name="performance friction",
            definition="Slow system response.",
            inclusion_rule="The system is explicitly slow.",
            exclusion_rule="Unspecified dissatisfaction.",
            parent_code=parent.code_id,
        ),
    ]

    print(f"Parent: {parent.name}")
    for child in children:
        print(f"  Child: {child.name} -> parent={child.parent_code}")

    print_section("Advanced concept: simple information retrieval")

    notes = build_sample_interview()

    document_term_sets = {
        note.note_id: note_term_set(note)
        for note in notes
    }

    query_terms = {"dashboard", "export"}

    ranked = []

    for note_id, terms in document_term_sets.items():
        overlap = len(terms & query_terms)
        if overlap:
            ranked.append((note_id, overlap))

    for note_id, score in sorted(
        ranked,
        key=lambda item: item[1],
        reverse=True,
    )[:10]:
        print(f"{note_id}: retrieval score={score}")

    print_section("Advanced concept: disagreement between analysts")

    analyst_a = {
        "N01": {"C01", "C02"},
        "N02": {"C01"},
        "N03": {"C03"},
    }

    analyst_b = {
        "N01": {"C02"},
        "N02": {"C01"},
        "N03": {"C03", "C02"},
    }

    all_pairs = []

    for note_id in sorted(set(analyst_a) | set(analyst_b)):
        set_a = analyst_a.get(note_id, set())
        set_b = analyst_b.get(note_id, set())
        similarity = jaccard_similarity(set_a, set_b)
        all_pairs.append(similarity)
        print(
            f"{note_id}: analyst agreement indicator="
            f"{similarity:.3f}"
        )

    if all_pairs:
        print(
            "Mean coding agreement indicator:",
            round(statistics.mean(all_pairs), 3),
        )

    print_section("Advanced concept: complexity")

    n = len(notes)
    m = len(list(build_codebook()))

    print(f"Notes: {n}")
    print(f"Codes: {m}")
    print(
        "Naive note-code rule evaluation is approximately O(N*M*K), "
        "where K is the average number of matching phrases."
    )
    print(
        "Pairwise note similarity is O(N^2) comparisons before token-set "
        "operations are considered."
    )
    print(
        "For large datasets, indexed retrieval, sparse matrices, database "
        "storage, or specialized text-processing pipelines can reduce cost."
    )


# ---------------------------------------------------------------------------
# 21. Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_analysis()
    demonstrate_advanced_concepts()
