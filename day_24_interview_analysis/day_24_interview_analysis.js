/*
 * Interview Analysis: Notes, Coding, Patterns, Themes, Insights,
 * Evidence vs Assumptions
 *
 * This self-contained JavaScript file complements the Python implementation.
 * It emphasizes application-level data structures, functional transformations,
 * validation, indexing, asynchronous analysis, event-driven progress reporting,
 * search, scoring, and report generation.
 *
 * Runtime:
 *   Node.js 18+ recommended.
 *
 * No external npm packages are required.
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. Core data structures
// -----------------------------------------------------------------------------

const EvidenceLevel = Object.freeze({
    DIRECT: "direct",
    OBSERVED: "observed",
    INTERPRETED: "interpreted",
    ASSUMPTION: "assumption",
});

const NoteType = Object.freeze({
    QUOTE: "quote",
    PARAPHRASE: "paraphrase",
    OBSERVATION: "observation",
    CONTEXT: "context",
});

class InterviewNote {
    constructor({
        noteId,
        participantId,
        questionId,
        text,
        noteType = NoteType.QUOTE,
        evidenceLevel = EvidenceLevel.DIRECT,
        metadata = {},
    }) {
        this.noteId = noteId;
        this.participantId = participantId;
        this.questionId = questionId;
        this.text = normalizeText(text);
        this.noteType = noteType;
        this.evidenceLevel = evidenceLevel;
        this.metadata = metadata;
    }
}

class CodeDefinition {
    constructor({
        codeId,
        name,
        definition,
        inclusionRule,
        exclusionRule,
        aliases = [],
        parentCode = null,
    }) {
        this.codeId = codeId;
        this.name = name;
        this.definition = definition;
        this.inclusionRule = inclusionRule;
        this.exclusionRule = exclusionRule;
        this.aliases = new Set(aliases);
        this.parentCode = parentCode;
    }
}

class CodingAssignment {
    constructor({
        noteId,
        codeId,
        confidence,
        rationale,
        analyst = "primary",
    }) {
        if (confidence < 0 || confidence > 1) {
            throw new RangeError("Coding confidence must be between 0 and 1.");
        }

        this.noteId = noteId;
        this.codeId = codeId;
        this.confidence = confidence;
        this.rationale = rationale;
        this.analyst = analyst;
    }
}

class Pattern {
    constructor({
        patternId,
        name,
        description,
        supportingCodes,
        supportingNotes,
    }) {
        this.patternId = patternId;
        this.name = name;
        this.description = description;
        this.supportingCodes = supportingCodes;
        this.supportingNotes = supportingNotes;
    }
}

class Theme {
    constructor({
        themeId,
        name,
        researchQuestion,
        description,
        supportingPatterns,
        supportingNotes,
        contradictoryNotes = [],
        confidence = 0,
    }) {
        this.themeId = themeId;
        this.name = name;
        this.researchQuestion = researchQuestion;
        this.description = description;
        this.supportingPatterns = supportingPatterns;
        this.supportingNotes = supportingNotes;
        this.contradictoryNotes = contradictoryNotes;
        this.confidence = confidence;
    }
}

// -----------------------------------------------------------------------------
// 2. Sample data
// -----------------------------------------------------------------------------

function buildSampleInterview() {
    const rows = [
        ["N01", "P01", "Q01",
            "I usually start with the dashboard because it gives me the numbers I need without opening several spreadsheets."],
        ["N02", "P01", "Q02",
            "The dashboard saves time when I am preparing the weekly review."],
        ["N03", "P01", "Q03",
            "I still export the data to Excel when I need to combine it with information from another team."],
        ["N04", "P01", "Q04",
            "I trust the dashboard for totals, but I check unusual numbers against the source system."],

        ["N05", "P02", "Q01",
            "The dashboard is useful, but I often cannot find the metric I want."],
        ["N06", "P02", "Q02",
            "I spend time looking through filters before I can answer a question."],
        ["N07", "P02", "Q03",
            "When the dashboard is slow, I download the data and work locally."],
        ["N08", "P02", "Q04",
            "I am not sure whether the definitions of some metrics have changed."],

        ["N09", "P03", "Q01",
            "I mainly use the dashboard before meetings to check whether anything looks unusual."],
        ["N10", "P03", "Q02",
            "For normal questions it is fast enough, but detailed analysis takes me to spreadsheets."],
        ["N11", "P03", "Q03",
            "I prefer exporting because I can calculate things the dashboard does not provide."],
        ["N12", "P03", "Q04",
            "I ask colleagues when I do not understand where a number came from."],

        ["N13", "P04", "Q01",
            "I use the dashboard every day and rarely need another tool."],
        ["N14", "P04", "Q02",
            "The filters are easy for me because I only use a few standard views."],
        ["N15", "P04", "Q03",
            "I do not export data unless someone specifically asks for a file."],
        ["N16", "P04", "Q04",
            "The metric definitions are clear enough for my daily work."],

        ["N17", "P05", "Q01",
            "I like having everything in one place, but the interface feels crowded."],
        ["N18", "P05", "Q02",
            "I usually use saved views because changing filters takes too long."],
        ["N19", "P05", "Q03",
            "I export when I need to prepare a custom report."],
        ["N20", "P05", "Q04",
            "I would like clearer explanations of how metrics are calculated."],
    ];

    return rows.map(
        ([noteId, participantId, questionId, text]) =>
            new InterviewNote({
                noteId,
                participantId,
                questionId,
                text,
            })
    );
}

// -----------------------------------------------------------------------------
// 3. Text processing
// -----------------------------------------------------------------------------

const STOP_WORDS = new Set([
    "a", "an", "and", "are", "as", "at", "be", "because", "but", "by",
    "can", "do", "for", "from", "have", "i", "if", "in", "is", "it",
    "me", "my", "of", "on", "or", "so", "that", "the", "their", "this",
    "to", "use", "when", "with", "you", "your", "we", "our", "was",
    "were", "often", "usually", "still", "only", "more", "some",
]);

function normalizeText(text) {
    return String(text).trim().replace(/\s+/g, " ");
}

function tokenize(text, removeStopWords = true) {
    const tokens = normalizeText(text)
        .toLowerCase()
        .match(/[a-z0-9']+/g) || [];

    if (!removeStopWords) {
        return tokens;
    }

    return tokens.filter((token) => !STOP_WORDS.has(token));
}

function containsAny(text, phrases) {
    const normalized = normalizeText(text).toLowerCase();
    return phrases.some((phrase) =>
        normalized.includes(String(phrase).toLowerCase())
    );
}

function wordFrequency(notes) {
    const frequency = new Map();

    for (const note of notes) {
        for (const token of tokenize(note.text)) {
            frequency.set(token, (frequency.get(token) || 0) + 1);
        }
    }

    return new Map(
        [...frequency.entries()].sort((a, b) => b[1] - a[1])
    );
}

// -----------------------------------------------------------------------------
// 4. Codebook
// -----------------------------------------------------------------------------

function buildCodebook() {
    const definitions = [
        {
            codeId: "C01",
            name: "time saving",
            definition: "The system reduces time or effort required to obtain information.",
            inclusionRule: "Explicit time or effort reduction.",
            exclusionRule: "Positive comments without a time component.",
            aliases: ["saves time", "save time", "faster"],
        },
        {
            codeId: "C02",
            name: "dashboard usefulness",
            definition: "The dashboard directly supports a task.",
            inclusionRule: "Explicit usefulness or direct dashboard use.",
            exclusionRule: "Pure frustration without utility.",
            aliases: ["useful", "everything in one place"],
        },
        {
            codeId: "C03",
            name: "export dependency",
            definition: "Data is moved to another tool for analysis or reporting.",
            inclusionRule: "Export, Excel, spreadsheet, or local analysis.",
            exclusionRule: "External tools unrelated to the task.",
            aliases: ["export", "excel", "spreadsheet", "work locally"],
        },
        {
            codeId: "C04",
            name: "findability problem",
            definition: "The participant has difficulty locating information.",
            inclusionRule: "Explicit difficulty finding a metric or function.",
            exclusionRule: "General navigation without difficulty.",
            aliases: ["cannot find", "can't find", "find the metric"],
        },
        {
            codeId: "C05",
            name: "filter friction",
            definition: "Filtering or changing views creates effort or delay.",
            inclusionRule: "Difficulty or delay involving filters.",
            exclusionRule: "Filters explicitly described as easy.",
            aliases: ["filters", "changing filters", "takes too long"],
        },
        {
            codeId: "C06",
            name: "performance friction",
            definition: "System speed disrupts the workflow.",
            inclusionRule: "Explicit system slowness.",
            exclusionRule: "Unspecified dissatisfaction.",
            aliases: ["slow", "slower"],
        },
        {
            codeId: "C07",
            name: "trust verification",
            definition: "The participant checks information against another source.",
            inclusionRule: "Verification or source checking.",
            exclusionRule: "Metric definition discussion without verification.",
            aliases: ["trust", "check", "source system"],
        },
        {
            codeId: "C08",
            name: "metric ambiguity",
            definition: "Metric definitions or calculations are unclear.",
            inclusionRule: "Explicit uncertainty about meaning or calculation.",
            exclusionRule: "Clear understanding.",
            aliases: ["definitions", "calculated", "understand where"],
        },
        {
            codeId: "C10",
            name: "meeting preparation",
            definition: "Dashboard use supports meeting or review preparation.",
            inclusionRule: "Explicit meeting or review use.",
            exclusionRule: "General dashboard use.",
            aliases: ["meeting", "meetings", "weekly review"],
        },
    ];

    return new Map(
        definitions.map(
            (definition) => [
                definition.codeId,
                new CodeDefinition(definition),
            ]
        )
    );
}

// -----------------------------------------------------------------------------
// 5. Candidate coding
// -----------------------------------------------------------------------------

function candidateCodeRules() {
    return new Map([
        ["C01", ["saves time", "save time", "faster", "without opening several"]],
        ["C02", ["dashboard is useful", "dashboard", "everything in one place", "useful"]],
        ["C03", ["export", "excel", "spreadsheet", "work locally"]],
        ["C04", ["cannot find", "can't find", "find the metric"]],
        ["C05", ["filters", "filter", "changing filters", "takes too long"]],
        ["C06", ["slow", "slower", "speed"]],
        ["C07", ["trust", "check", "source system", "where a number came from"]],
        ["C08", ["definitions", "metric definitions", "how metrics are calculated"]],
        ["C10", ["meeting", "meetings", "weekly review"]],
    ]);
}

function candidateRationale(codeId) {
    const rationales = {
        C01: "The text contains an explicit time or effort reduction.",
        C02: "The text explicitly refers to dashboard utility or use.",
        C03: "The text describes moving data to another analytical environment.",
        C04: "The text explicitly describes difficulty locating information.",
        C05: "The text references filtering or changing views.",
        C06: "The text explicitly describes slowness.",
        C07: "The text describes verification or source checking.",
        C08: "The text describes uncertainty about metric meaning or calculation.",
        C10: "The text connects dashboard use with a meeting or review.",
    };

    return rationales[codeId];
}

function autoCodeNote(note) {
    const assignments = [];
    const rules = candidateCodeRules();

    for (const [codeId, phrases] of rules.entries()) {
        if (containsAny(note.text, phrases)) {
            let confidence = 0.88;

            if (
                codeId === "C02" &&
                normalizeText(note.text).toLowerCase() === "dashboard"
            ) {
                confidence = 0.55;
            }

            assignments.push(
                new CodingAssignment({
                    noteId: note.noteId,
                    codeId,
                    confidence,
                    rationale: candidateRationale(codeId),
                })
            );
        }
    }

    return assignments;
}

function refineAssignments(notes, candidates) {
    const noteMap = new Map(
        notes.map((note) => [note.noteId, note])
    );

    return candidates.filter((assignment) => {
        const note = noteMap.get(assignment.noteId);

        if (!note) {
            return false;
        }

        if (
            assignment.codeId === "C02" &&
            !containsAny(note.text, [
                "useful",
                "saves time",
                "everything in one place",
                "use the dashboard",
                "dashboard is useful",
            ])
        ) {
            return false;
        }

        if (
            assignment.codeId === "C05" &&
            containsAny(note.text, ["filters are easy"])
        ) {
            return false;
        }

        if (
            assignment.codeId === "C08" &&
            containsAny(note.text, ["clear enough"])
        ) {
            return false;
        }

        return true;
    });
}

// -----------------------------------------------------------------------------
// 6. Indexing
// -----------------------------------------------------------------------------

function buildNoteIndex(notes) {
    const index = new Map();

    for (const note of notes) {
        index.set(note.noteId, note);
    }

    return index;
}

function buildParticipantIndex(notes) {
    const index = new Map();

    for (const note of notes) {
        if (!index.has(note.participantId)) {
            index.set(note.participantId, []);
        }

        index.get(note.participantId).push(note);
    }

    return index;
}

function buildCodeIndex(assignments) {
    const index = new Map();

    for (const assignment of assignments) {
        if (!index.has(assignment.codeId)) {
            index.set(assignment.codeId, []);
        }

        index.get(assignment.codeId).push(assignment);
    }

    return index;
}

// -----------------------------------------------------------------------------
// 7. Code statistics
// -----------------------------------------------------------------------------

function countBy(items, selector) {
    const counts = new Map();

    for (const item of items) {
        const key = selector(item);
        counts.set(key, (counts.get(key) || 0) + 1);
    }

    return counts;
}

function participantCountByCode(assignments, notes) {
    const noteMap = buildNoteIndex(notes);
    const participants = new Map();

    for (const assignment of assignments) {
        const note = noteMap.get(assignment.noteId);

        if (!note) {
            continue;
        }

        if (!participants.has(assignment.codeId)) {
            participants.set(assignment.codeId, new Set());
        }

        participants.get(assignment.codeId).add(note.participantId);
    }

    return new Map(
        [...participants.entries()].map(
            ([codeId, ids]) => [codeId, ids.size]
        )
    );
}

// -----------------------------------------------------------------------------
// 8. Co-occurrence
// -----------------------------------------------------------------------------

function groupAssignmentsByNote(assignments) {
    const groups = new Map();

    for (const assignment of assignments) {
        if (!groups.has(assignment.noteId)) {
            groups.set(assignment.noteId, []);
        }

        groups.get(assignment.noteId).push(assignment);
    }

    return groups;
}

function codeCooccurrence(assignments) {
    const groups = groupAssignmentsByNote(assignments);
    const pairs = new Map();

    for (const noteAssignments of groups.values()) {
        const codes = [...new Set(
            noteAssignments.map((assignment) => assignment.codeId)
        )].sort();

        for (let i = 0; i < codes.length; i += 1) {
            for (let j = i + 1; j < codes.length; j += 1) {
                const key = `${codes[i]}|${codes[j]}`;
                pairs.set(key, (pairs.get(key) || 0) + 1);
            }
        }
    }

    return new Map(
        [...pairs.entries()].sort((a, b) => b[1] - a[1])
    );
}

// -----------------------------------------------------------------------------
// 9. Pattern and theme analysis
// -----------------------------------------------------------------------------

function detectPatterns(notes, assignments) {
    const grouped = groupAssignmentsByNote(assignments);

    const rules = [
        {
            patternId: "P01",
            name: "dashboard-to-spreadsheet workflow",
            description:
                "The dashboard supports initial retrieval while customized work continues elsewhere.",
            requiredCodes: new Set(["C02", "C03"]),
        },
        {
            patternId: "P02",
            name: "verification behavior",
            description:
                "Participants validate or question dashboard information.",
            requiredCodes: new Set(["C07"]),
        },
        {
            patternId: "P03",
            name: "navigation and filtering friction",
            description:
                "Participants encounter difficulty locating or configuring information.",
            requiredCodes: new Set(["C04", "C05"]),
        },
        {
            patternId: "P04",
            name: "metric understanding gap",
            description:
                "Participants experience uncertainty about definitions or calculations.",
            requiredCodes: new Set(["C08"]),
        },
        {
            patternId: "P05",
            name: "meeting-oriented use",
            description:
                "Dashboard use supports meetings or reviews.",
            requiredCodes: new Set(["C10"]),
        },
        {
            patternId: "P06",
            name: "performance-driven workaround",
            description:
                "Slow response encourages external analysis.",
            requiredCodes: new Set(["C03", "C06"]),
        },
    ];

    return rules
        .map((rule) => {
            const supportingNotes = [];

            for (const [noteId, noteAssignments] of grouped.entries()) {
                const codes = new Set(
                    noteAssignments.map((assignment) => assignment.codeId)
                );

                const supported = [...rule.requiredCodes]
                    .every((codeId) => codes.has(codeId));

                if (supported) {
                    supportingNotes.push(noteId);
                }
            }

            if (supportingNotes.length === 0) {
                return null;
            }

            return new Pattern({
                patternId: rule.patternId,
                name: rule.name,
                description: rule.description,
                supportingCodes: [...rule.requiredCodes],
                supportingNotes,
            });
        })
        .filter(Boolean);
}

function participantIdsForNotes(noteIds, noteMap) {
    return new Set(
        noteIds
            .map((noteId) => noteMap.get(noteId))
            .filter(Boolean)
            .map((note) => note.participantId)
    );
}

function buildThemes(notes, patterns) {
    const noteMap = buildNoteIndex(notes);
    const patternMap = new Map(
        patterns.map((pattern) => [pattern.patternId, pattern])
    );

    const specifications = [
        {
            themeId: "T01",
            name: "efficiency with boundary conditions",
            researchQuestion: "How does the system affect work efficiency?",
            description:
                "The dashboard can reduce initial information-gathering effort, " +
                "but efficiency depends on task complexity, navigation, and system performance.",
            patterns: ["P01", "P03", "P06"],
        },
        {
            themeId: "T02",
            name: "dashboard as an entry point rather than a complete workflow",
            researchQuestion:
                "How does the system fit into broader analytical workflows?",
            description:
                "The dashboard often serves as a starting point, while customized analysis continues elsewhere.",
            patterns: ["P01", "P06"],
        },
        {
            themeId: "T03",
            name: "trust depends on interpretability and verification",
            researchQuestion:
                "What affects confidence in dashboard information?",
            description:
                "Participants describe verification behavior and uncertainty when metric definitions are unclear.",
            patterns: ["P02", "P04"],
        },
        {
            themeId: "T04",
            name: "usage varies by task and user",
            researchQuestion:
                "How consistently is the system used?",
            description:
                "Interviewees use materially different workflows, from dashboard-only use to frequent exports.",
            patterns: ["P01", "P03"],
        },
    ];

    return specifications.map((specification) => {
        const supportingPatterns = specification.patterns
            .filter((patternId) => patternMap.has(patternId));

        const supportingNotes = [
            ...new Set(
                supportingPatterns.flatMap(
                    (patternId) => patternMap.get(patternId).supportingNotes
                )
            ),
        ];

        const contradictoryNotes = [];

        if (specification.themeId === "T01") {
            for (const note of notes) {
                if (containsAny(note.text, [
                    "filters are easy",
                    "rarely need another tool",
                    "clear enough",
                ])) {
                    contradictoryNotes.push(note.noteId);
                }
            }
        }

        if (specification.themeId === "T02") {
            for (const note of notes) {
                if (containsAny(note.text, [
                    "rarely need another tool",
                    "do not export data",
                ])) {
                    contradictoryNotes.push(note.noteId);
                }
            }
        }

        if (specification.themeId === "T03") {
            for (const note of notes) {
                if (containsAny(note.text, ["clear enough"])) {
                    contradictoryNotes.push(note.noteId);
                }
            }
        }

        const participantCount = participantIdsForNotes(
            supportingNotes,
            noteMap
        ).size;

        const contradictionCount = new Set(
            contradictoryNotes
        ).size;

        const confidence =
            participantCount + contradictionCount === 0
                ? 0
                : participantCount /
                  (participantCount + contradictionCount);

        return new Theme({
            themeId: specification.themeId,
            name: specification.name,
            researchQuestion: specification.researchQuestion,
            description: specification.description,
            supportingPatterns,
            supportingNotes,
            contradictoryNotes,
            confidence: Number(confidence.toFixed(3)),
        });
    });
}

// -----------------------------------------------------------------------------
// 10. Evidence and assumptions
// -----------------------------------------------------------------------------

function buildClaims() {
    return [
        {
            claimId: "CL01",
            text:
                "P01 reports that the dashboard reduces the need to open several spreadsheets.",
            level: EvidenceLevel.DIRECT,
            supportingNoteIds: ["N01"],
            contradictingNoteIds: [],
            rationale: "The participant explicitly described the workflow.",
        },
        {
            claimId: "CL02",
            text: "The dashboard saves time for every user.",
            level: EvidenceLevel.ASSUMPTION,
            supportingNoteIds: ["N02"],
            contradictingNoteIds: [],
            rationale:
                "One participant cannot establish a universal claim.",
        },
        {
            claimId: "CL03",
            text:
                "Some participants use the dashboard as an initial step and then export data.",
            level: EvidenceLevel.INTERPRETED,
            supportingNoteIds: ["N01", "N03", "N10", "N11", "N19"],
            contradictingNoteIds: [],
            rationale:
                "Multiple direct observations support a broader workflow interpretation.",
        },
        {
            claimId: "CL04",
            text:
                "Metric ambiguity may reduce confidence in dashboard information.",
            level: EvidenceLevel.INTERPRETED,
            supportingNoteIds: ["N04", "N08", "N12", "N20"],
            contradictingNoteIds: [],
            rationale:
                "Verification behavior and uncertainty about definitions occur together.",
        },
        {
            claimId: "CL05",
            text: "Every participant dislikes the dashboard interface.",
            level: EvidenceLevel.ASSUMPTION,
            supportingNoteIds: ["N17"],
            contradictingNoteIds: ["N13", "N14", "N16"],
            rationale:
                "The dataset contains participants reporting positive experiences.",
        },
    ];
}

function evidenceStrength(claim, notes) {
    const noteMap = buildNoteIndex(notes);

    const supportingNotes = claim.supportingNoteIds
        .map((noteId) => noteMap.get(noteId))
        .filter(Boolean);

    if (supportingNotes.length === 0) {
        return 0;
    }

    const participantCount = new Set(
        supportingNotes.map((note) => note.participantId)
    ).size;

    const directCount = supportingNotes.filter(
        (note) => note.evidenceLevel === EvidenceLevel.DIRECT
    ).length;

    const supportComponent = Math.min(
        supportingNotes.length / 5,
        1
    );

    const participantComponent = Math.min(
        participantCount / 5,
        1
    );

    const directComponent = directCount / supportingNotes.length;

    const contradictionComponent =
        1 / (1 + claim.contradictingNoteIds.length);

    const levelMultiplier = {
        [EvidenceLevel.DIRECT]: 1,
        [EvidenceLevel.OBSERVED]: 0.95,
        [EvidenceLevel.INTERPRETED]: 0.75,
        [EvidenceLevel.ASSUMPTION]: 0.15,
    };

    const score = (
        0.30 * supportComponent +
        0.30 * participantComponent +
        0.20 * directComponent +
        0.20 * contradictionComponent
    ) * levelMultiplier[claim.level];

    return Number(score.toFixed(3));
}

// -----------------------------------------------------------------------------
// 11. Search and retrieval
// -----------------------------------------------------------------------------

function searchNotes(notes, query) {
    const normalizedQuery = normalizeText(query).toLowerCase();

    return notes.filter((note) =>
        note.text.toLowerCase().includes(normalizedQuery)
    );
}

function notesForCode(codeId, assignments, notes) {
    const noteMap = buildNoteIndex(notes);

    const ids = new Set(
        assignments
            .filter((assignment) => assignment.codeId === codeId)
            .map((assignment) => assignment.noteId)
    );

    return [...ids]
        .map((noteId) => noteMap.get(noteId))
        .filter(Boolean);
}

// -----------------------------------------------------------------------------
// 12. Similarity
// -----------------------------------------------------------------------------

function jaccardSimilarity(left, right) {
    const union = new Set([...left, ...right]);

    if (union.size === 0) {
        return 0;
    }

    let intersection = 0;

    for (const value of left) {
        if (right.has(value)) {
            intersection += 1;
        }
    }

    return intersection / union.size;
}

function mostSimilarPairs(notes, minimumSimilarity = 0.2) {
    const results = [];

    for (let i = 0; i < notes.length; i += 1) {
        const leftTerms = new Set(tokenize(notes[i].text));

        for (let j = i + 1; j < notes.length; j += 1) {
            const rightTerms = new Set(tokenize(notes[j].text));
            const similarity = jaccardSimilarity(
                leftTerms,
                rightTerms
            );

            if (similarity >= minimumSimilarity) {
                results.push({
                    left: notes[i].noteId,
                    right: notes[j].noteId,
                    similarity: Number(similarity.toFixed(3)),
                });
            }
        }
    }

    return results.sort(
        (a, b) => b.similarity - a.similarity
    );
}

// -----------------------------------------------------------------------------
// 13. Participant profiles
// -----------------------------------------------------------------------------

function buildParticipantProfiles(notes, assignments, codebook) {
    const noteMap = buildNoteIndex(notes);
    const participantMap = new Map();

    for (const assignment of assignments) {
        const note = noteMap.get(assignment.noteId);

        if (!note) {
            continue;
        }

        if (!participantMap.has(note.participantId)) {
            participantMap.set(note.participantId, []);
        }

        participantMap.get(note.participantId).push(assignment);
    }

    const profiles = new Map();

    for (const [participantId, participantAssignments] of participantMap) {
        const counts = countBy(
            participantAssignments,
            (assignment) => assignment.codeId
        );

        const topCodes = [...counts.entries()]
            .sort((a, b) => b[1] - a[1])
            .map(([codeId]) => codebook.get(codeId)?.name || codeId)
            .slice(0, 5);

        profiles.set(participantId, {
            codeCount: participantAssignments.length,
            uniqueCodes: counts.size,
            topCodes,
        });
    }

    return profiles;
}

// -----------------------------------------------------------------------------
// 14. Validation and audit
// -----------------------------------------------------------------------------

function auditAssignments(notes, assignments, codebook) {
    const noteIds = new Set(
        notes.map((note) => note.noteId)
    );

    const errors = [];

    for (const assignment of assignments) {
        if (!noteIds.has(assignment.noteId)) {
            errors.push(
                `Unknown note ID: ${assignment.noteId}`
            );
        }

        if (!codebook.has(assignment.codeId)) {
            errors.push(
                `Unknown code ID: ${assignment.codeId}`
            );
        }

        if (!assignment.rationale.trim()) {
            errors.push(
                `Missing rationale: ${assignment.noteId}/${assignment.codeId}`
            );
        }
    }

    return errors;
}

// -----------------------------------------------------------------------------
// 15. Event-driven progress reporting
// -----------------------------------------------------------------------------

class AnalysisEventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) || [];

        for (const listener of listeners) {
            listener(payload);
        }
    }
}

// -----------------------------------------------------------------------------
// 16. Asynchronous analysis
// -----------------------------------------------------------------------------

function asynchronousStep(name, operation, eventBus) {
    return new Promise((resolve) => {
        setImmediate(() => {
            eventBus.emit("stepStarted", { name });

            try {
                const result = operation();
                eventBus.emit("stepCompleted", { name });
                resolve(result);
            } catch (error) {
                eventBus.emit("stepFailed", {
                    name,
                    error: error.message,
                });
                throw error;
            }
        });
    });
}

async function runAsynchronousPipeline(notes, codebook, eventBus) {
    const candidates = await asynchronousStep(
        "candidate coding",
        () => notes.flatMap(autoCodeNote),
        eventBus
    );

    const assignments = await asynchronousStep(
        "coding refinement",
        () => refineAssignments(notes, candidates),
        eventBus
    );

    const patterns = await asynchronousStep(
        "pattern detection",
        () => detectPatterns(notes, assignments),
        eventBus
    );

    const themes = await asynchronousStep(
        "theme construction",
        () => buildThemes(notes, patterns),
        eventBus
    );

    return {
        candidates,
        assignments,
        patterns,
        themes,
    };
}

// -----------------------------------------------------------------------------
// 17. Report generation
// -----------------------------------------------------------------------------

function generateReport({
    notes,
    codebook,
    assignments,
    patterns,
    themes,
    claims,
}) {
    const noteMap = buildNoteIndex(notes);
    const frequencies = countBy(
        assignments,
        (assignment) => assignment.codeId
    );

    const participantCounts = participantCountByCode(
        assignments,
        notes
    );

    const lines = [];

    lines.push("INTERVIEW ANALYSIS REPORT");
    lines.push("=========================");
    lines.push("");
    lines.push(`Participants: ${new Set(notes.map((n) => n.participantId)).size}`);
    lines.push(`Notes: ${notes.length}`);
    lines.push(`Codes used: ${frequencies.size}`);
    lines.push("");

    lines.push("CODE DISTRIBUTION");
    lines.push("-----------------");

    for (const [codeId, count] of [...frequencies.entries()]
        .sort((a, b) => b[1] - a[1])) {
        const definition = codebook.get(codeId);

        lines.push(
            `${codeId} | ${definition.name} | ` +
            `occurrences=${count} | ` +
            `participants=${participantCounts.get(codeId) || 0}`
        );
    }

    lines.push("");
    lines.push("PATTERNS");
    lines.push("--------");

    for (const pattern of patterns) {
        lines.push(
            `${pattern.patternId} | ${pattern.name} | ` +
            `notes=${pattern.supportingNotes.length}`
        );
    }

    lines.push("");
    lines.push("THEMES");
    lines.push("------");

    for (const theme of themes) {
        lines.push(
            `${theme.themeId} | ${theme.name} | ` +
            `confidence-indicator=${theme.confidence}`
        );

        lines.push(`  ${theme.description}`);
        lines.push(
            `  Supporting notes: ${theme.supportingNotes.join(", ")}`
        );

        lines.push(
            `  Contradictory notes: ${
                theme.contradictoryNotes.join(", ") || "None identified"
            }`
        );
    }

    lines.push("");
    lines.push("CLAIM AUDIT");
    lines.push("-----------");

    for (const claim of claims) {
        lines.push(
            `${claim.claimId} | ${claim.level} | ` +
            `support=${evidenceStrength(claim, notes)}`
        );

        lines.push(`  ${claim.text}`);
        lines.push(
            `  Evidence: ${claim.supportingNoteIds.join(", ")}`
        );
    }

    return lines.join("\n");
}

// -----------------------------------------------------------------------------
// 18. Main
// -----------------------------------------------------------------------------

async function main() {
    const notes = buildSampleInterview();
    const codebook = buildCodebook();

    const eventBus = new AnalysisEventBus();

    eventBus.on("stepStarted", ({ name }) => {
        console.log(`\n[START] ${name}`);
    });

    eventBus.on("stepCompleted", ({ name }) => {
        console.log(`[DONE] ${name}`);
    });

    eventBus.on("stepFailed", ({ name, error }) => {
        console.error(`[FAIL] ${name}: ${error}`);
    });

    console.log("INTERVIEW ANALYSIS");
    console.log("==================");
    console.log(`Notes loaded: ${notes.length}`);

    const frequencies = wordFrequency(notes);

    console.log("\nTop exploratory terms:");
    console.log(
        [...frequencies.entries()]
            .slice(0, 15)
            .map(([word, count]) => `${word}=${count}`)
            .join(", ")
    );

    const result = await runAsynchronousPipeline(
        notes,
        codebook,
        eventBus
    );

    const {
        candidates,
        assignments,
        patterns,
        themes,
    } = result;

    console.log("\nCandidate assignments:", candidates.length);
    console.log("Reviewed assignments:", assignments.length);

    const auditErrors = auditAssignments(
        notes,
        assignments,
        codebook
    );

    if (auditErrors.length > 0) {
        console.error("\nCoding audit errors:");
        auditErrors.forEach((error) => console.error(error));
    } else {
        console.log("\nCoding audit: no structural errors.");
    }

    const participantCounts = participantCountByCode(
        assignments,
        notes
    );

    console.log("\nCode statistics:");

    for (const [codeId, count] of [...countBy(
        assignments,
        (assignment) => assignment.codeId
    ).entries()].sort((a, b) => b[1] - a[1])) {
        console.log(
            `${codeId} ${codebook.get(codeId).name}: ` +
            `${count} occurrences, ` +
            `${participantCounts.get(codeId) || 0} participants`
        );
    }

    console.log("\nCode co-occurrence:");

    const cooccurrence = codeCooccurrence(assignments);

    for (const [pair, count] of [...cooccurrence.entries()].slice(0, 10)) {
        console.log(`${pair}: ${count}`);
    }

    console.log("\nPatterns:");

    for (const pattern of patterns) {
        console.log(
            `${pattern.patternId}: ${pattern.name} ` +
            `(${pattern.supportingNotes.length} notes)`
        );
    }

    console.log("\nThemes:");

    for (const theme of themes) {
        console.log(
            `${theme.themeId}: ${theme.name} ` +
            `support=${theme.supportingNotes.length}, ` +
            `contradiction=${theme.contradictoryNotes.length}, ` +
            `indicator=${theme.confidence}`
        );
    }

    console.log("\nEvidence versus assumptions:");

    const claims = buildClaims();

    for (const claim of claims) {
        console.log(
            `${claim.claimId}: ${claim.level} | ` +
            `support=${evidenceStrength(claim, notes)}`
        );
    }

    console.log("\nSearch example:");

    const searchResults = searchNotes(notes, "export");

    for (const note of searchResults) {
        console.log(`${note.noteId}: ${note.text}`);
    }

    console.log("\nCode retrieval example:");

    for (const note of notesForCode(
        "C03",
        assignments,
        notes
    )) {
        console.log(`${note.noteId}: ${note.text}`);
    }

    console.log("\nParticipant profiles:");

    const profiles = buildParticipantProfiles(
        notes,
        assignments,
        codebook
    );

    for (const [participantId, profile] of profiles.entries()) {
        console.log(
            participantId,
            JSON.stringify(profile)
        );
    }

    console.log("\nSimilar note pairs:");

    const similarPairs = mostSimilarPairs(notes);

    for (const pair of similarPairs.slice(0, 10)) {
        console.log(
            `${pair.left} <-> ${pair.right}: ${pair.similarity}`
        );
    }

    console.log("\nGenerated report:\n");

    console.log(
        generateReport({
            notes,
            codebook,
            assignments,
            patterns,
            themes,
            claims,
        })
    );

    console.log("\nMethodological controls:");
    console.log(
        "1. Frequency is descriptive, not proof of importance."
    );
    console.log(
        "2. Co-occurrence does not establish causality."
    );
    console.log(
        "3. Automated coding produces candidates requiring review."
    );
    console.log(
        "4. Contradictory evidence should remain visible."
    );
    console.log(
        "5. Claims should remain traceable to note IDs."
    );
}

main().catch((error) => {
    console.error("Analysis failed:", error);
    process.exitCode = 1;
});
