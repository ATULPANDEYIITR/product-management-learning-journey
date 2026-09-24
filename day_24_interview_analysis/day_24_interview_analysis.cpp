/*
 * Interview Analysis Case Study
 *
 * Scenario:
 * An organization has conducted interviews with users of an internal
 * analytics dashboard. The research team wants to understand how people use
 * the dashboard, where friction occurs, why users export data, how trust is
 * formed, and which interpretations are directly supported by evidence.
 *
 * The program demonstrates:
 * - structured interview notes
 * - codebooks
 * - rule-assisted coding
 * - analyst validation
 * - coding matrices
 * - code frequencies
 * - participant coverage
 * - code co-occurrence
 * - pattern construction
 * - theme construction
 * - evidence versus assumption
 * - negative-case analysis
 * - participant profiles
 * - validation
 * - complexity analysis
 *
 * Build:
 *   g++ -std=c++17 -O2 interview_analysis.cpp -o interview_analysis
 *
 * Run:
 *   ./interview_analysis
 */

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// 1. Domain model
// -----------------------------------------------------------------------------

enum class EvidenceLevel {
    Direct,
    Observed,
    Interpreted,
    Assumption
};

string evidenceLevelToString(EvidenceLevel level) {
    switch (level) {
        case EvidenceLevel::Direct:
            return "direct";
        case EvidenceLevel::Observed:
            return "observed";
        case EvidenceLevel::Interpreted:
            return "interpreted";
        case EvidenceLevel::Assumption:
            return "assumption";
    }

    return "unknown";
}

enum class NoteType {
    Quote,
    Paraphrase,
    Observation,
    Context
};

struct InterviewNote {
    string noteId;
    string participantId;
    string questionId;
    string text;
    NoteType noteType;
    EvidenceLevel evidenceLevel;
};

struct Code {
    string codeId;
    string name;
    string definition;
    string inclusionRule;
    string exclusionRule;
};

struct CodingAssignment {
    string noteId;
    string codeId;
    double confidence;
    string rationale;
    string analyst;
};

struct Pattern {
    string patternId;
    string name;
    string description;
    vector<string> supportingCodes;
    vector<string> supportingNotes;
};

struct Theme {
    string themeId;
    string name;
    string researchQuestion;
    string description;
    vector<string> supportingPatterns;
    vector<string> supportingNotes;
    vector<string> contradictoryNotes;
    double confidence;
};

struct Claim {
    string claimId;
    string text;
    EvidenceLevel level;
    vector<string> supportingNoteIds;
    vector<string> contradictingNoteIds;
    string rationale;
};

// -----------------------------------------------------------------------------
// 2. Utility functions
// -----------------------------------------------------------------------------

string lowerCopy(string value) {
    transform(
        value.begin(),
        value.end(),
        value.begin(),
        [](unsigned char character) {
            return static_cast<char>(tolower(character));
        }
    );

    return value;
}

bool containsIgnoreCase(
    const string& text,
    const vector<string>& phrases
) {
    const string normalized = lowerCopy(text);

    for (const string& phrase : phrases) {
        if (normalized.find(lowerCopy(phrase)) != string::npos) {
            return true;
        }
    }

    return false;
}

string shorten(const string& text, size_t maximumLength = 68) {
    if (text.size() <= maximumLength) {
        return text;
    }

    return text.substr(0, maximumLength - 3) + "...";
}

void printSection(const string& title) {
    cout << "\n";
    cout << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

// -----------------------------------------------------------------------------
// 3. Dataset
// -----------------------------------------------------------------------------

vector<InterviewNote> buildInterviewDataset() {
    return {
        {
            "N01", "P01", "Q01",
            "I usually start with the dashboard because it gives me the numbers I need without opening several spreadsheets.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N02", "P01", "Q02",
            "The dashboard saves time when I am preparing the weekly review.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N03", "P01", "Q03",
            "I still export the data to Excel when I need to combine it with information from another team.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N04", "P01", "Q04",
            "I trust the dashboard for totals, but I check unusual numbers against the source system.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N05", "P02", "Q01",
            "The dashboard is useful, but I often cannot find the metric I want.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N06", "P02", "Q02",
            "I spend time looking through filters before I can answer a question.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N07", "P02", "Q03",
            "When the dashboard is slow, I download the data and work locally.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N08", "P02", "Q04",
            "I am not sure whether the definitions of some metrics have changed.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N09", "P03", "Q01",
            "I mainly use the dashboard before meetings to check whether anything looks unusual.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N10", "P03", "Q02",
            "For normal questions it is fast enough, but detailed analysis takes me to spreadsheets.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N11", "P03", "Q03",
            "I prefer exporting because I can calculate things the dashboard does not provide.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N12", "P03", "Q04",
            "I ask colleagues when I do not understand where a number came from.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N13", "P04", "Q01",
            "I use the dashboard every day and rarely need another tool.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N14", "P04", "Q02",
            "The filters are easy for me because I only use a few standard views.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N15", "P04", "Q03",
            "I do not export data unless someone specifically asks for a file.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N16", "P04", "Q04",
            "The metric definitions are clear enough for my daily work.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N17", "P05", "Q01",
            "I like having everything in one place, but the interface feels crowded.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N18", "P05", "Q02",
            "I usually use saved views because changing filters takes too long.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N19", "P05", "Q03",
            "I export when I need to prepare a custom report.",
            NoteType::Quote,
            EvidenceLevel::Direct
        },
        {
            "N20", "P05", "Q04",
            "I would like clearer explanations of how metrics are calculated.",
            NoteType::Quote,
            EvidenceLevel::Direct
        }
    };
}

// -----------------------------------------------------------------------------
// 4. Codebook
// -----------------------------------------------------------------------------

map<string, Code> buildCodebook() {
    vector<Code> definitions = {
        {
            "C01",
            "time saving",
            "The system reduces time or effort required to obtain information.",
            "Explicit time or effort reduction.",
            "Generic positive comments without time or effort."
        },
        {
            "C02",
            "dashboard usefulness",
            "The dashboard directly supports a task or decision.",
            "Explicit utility or direct dashboard use.",
            "Pure frustration without utility."
        },
        {
            "C03",
            "export dependency",
            "Data is moved to another environment for analysis.",
            "Export, spreadsheet, Excel, or local analysis.",
            "External tools unrelated to completing the task."
        },
        {
            "C04",
            "findability problem",
            "The participant has difficulty locating information.",
            "Explicit difficulty finding a metric or function.",
            "General navigation without difficulty."
        },
        {
            "C05",
            "filter friction",
            "Filtering or changing views creates effort or delay.",
            "Difficulty or delay involving filters.",
            "Filters explicitly described as easy."
        },
        {
            "C06",
            "performance friction",
            "System responsiveness disrupts the workflow.",
            "Explicit slowness.",
            "General dissatisfaction without performance evidence."
        },
        {
            "C07",
            "trust verification",
            "The participant checks information against another source.",
            "Verification or source checking.",
            "Metric-definition discussion without verification."
        },
        {
            "C08",
            "metric ambiguity",
            "Metric definitions or calculations are unclear.",
            "Explicit uncertainty about meaning or calculation.",
            "Clear understanding."
        },
        {
            "C10",
            "meeting preparation",
            "Dashboard use supports meeting or review preparation.",
            "Explicit meeting or review connection.",
            "General dashboard use."
        }
    };

    map<string, Code> codebook;

    for (const Code& code : definitions) {
        codebook.emplace(code.codeId, code);
    }

    return codebook;
}

// -----------------------------------------------------------------------------
// 5. Rule-assisted coding
// -----------------------------------------------------------------------------

struct CodeRule {
    string codeId;
    vector<string> phrases;
};

vector<CodeRule> buildRules() {
    return {
        {"C01", {"saves time", "save time", "faster", "without opening several"}},
        {"C02", {"dashboard is useful", "dashboard", "everything in one place", "useful"}},
        {"C03", {"export", "excel", "spreadsheet", "work locally"}},
        {"C04", {"cannot find", "can't find", "find the metric"}},
        {"C05", {"filters", "filter", "changing filters", "takes too long"}},
        {"C06", {"slow", "slower", "speed"}},
        {"C07", {"trust", "check", "source system", "where a number came from"}},
        {"C08", {"definitions", "metric definitions", "how metrics are calculated"}},
        {"C10", {"meeting", "meetings", "weekly review"}}
    };
}

string rationaleForCode(const string& codeId) {
    static const map<string, string> rationales = {
        {"C01", "Explicit time or effort reduction."},
        {"C02", "Explicit dashboard utility or use."},
        {"C03", "Movement of data into another analytical environment."},
        {"C04", "Explicit difficulty locating information."},
        {"C05", "Reference to filtering or changing views."},
        {"C06", "Explicit system slowness."},
        {"C07", "Verification or source checking."},
        {"C08", "Uncertainty about metric meaning or calculation."},
        {"C10", "Connection between dashboard use and a meeting or review."}
    };

    auto iterator = rationales.find(codeId);

    if (iterator == rationales.end()) {
        return "No rationale defined.";
    }

    return iterator->second;
}

vector<CodingAssignment> candidateCoding(
    const vector<InterviewNote>& notes
) {
    vector<CodingAssignment> assignments;

    for (const InterviewNote& note : notes) {
        for (const CodeRule& rule : buildRules()) {
            if (containsIgnoreCase(note.text, rule.phrases)) {
                double confidence = 0.88;

                // "dashboard" alone is too broad to prove usefulness.
                if (
                    rule.codeId == "C02" &&
                    lowerCopy(note.text) == "dashboard"
                ) {
                    confidence = 0.55;
                }

                assignments.push_back({
                    note.noteId,
                    rule.codeId,
                    confidence,
                    rationaleForCode(rule.codeId),
                    "primary"
                });
            }
        }
    }

    return assignments;
}

vector<CodingAssignment> reviewCoding(
    const vector<InterviewNote>& notes,
    const vector<CodingAssignment>& candidates
) {
    unordered_map<string, InterviewNote> noteMap;

    for (const InterviewNote& note : notes) {
        noteMap[note.noteId] = note;
    }

    vector<CodingAssignment> reviewed;

    for (const CodingAssignment& assignment : candidates) {
        const InterviewNote& note = noteMap.at(assignment.noteId);

        if (assignment.codeId == "C02") {
            if (!containsIgnoreCase(
                    note.text,
                    {
                        "useful",
                        "saves time",
                        "everything in one place",
                        "use the dashboard",
                        "dashboard is useful"
                    }
                )) {
                continue;
            }
        }

        if (
            assignment.codeId == "C05" &&
            containsIgnoreCase(note.text, {"filters are easy"})
        ) {
            continue;
        }

        if (
            assignment.codeId == "C08" &&
            containsIgnoreCase(note.text, {"clear enough"})
        ) {
            continue;
        }

        reviewed.push_back(assignment);
    }

    return reviewed;
}

// -----------------------------------------------------------------------------
// 6. Indexes
// -----------------------------------------------------------------------------

unordered_map<string, InterviewNote> buildNoteIndex(
    const vector<InterviewNote>& notes
) {
    unordered_map<string, InterviewNote> index;

    for (const InterviewNote& note : notes) {
        index[note.noteId] = note;
    }

    return index;
}

unordered_map<string, vector<string>> buildParticipantNoteIndex(
    const vector<InterviewNote>& notes
) {
    unordered_map<string, vector<string>> index;

    for (const InterviewNote& note : notes) {
        index[note.participantId].push_back(note.noteId);
    }

    return index;
}

// -----------------------------------------------------------------------------
// 7. Code statistics
// -----------------------------------------------------------------------------

map<string, int> codeFrequency(
    const vector<CodingAssignment>& assignments
) {
    map<string, int> counts;

    for (const CodingAssignment& assignment : assignments) {
        ++counts[assignment.codeId];
    }

    return counts;
}

map<string, set<string>> participantsByCode(
    const vector<InterviewNote>& notes,
    const vector<CodingAssignment>& assignments
) {
    const auto noteMap = buildNoteIndex(notes);
    map<string, set<string>> participants;

    for (const CodingAssignment& assignment : assignments) {
        auto iterator = noteMap.find(assignment.noteId);

        if (iterator != noteMap.end()) {
            participants[assignment.codeId].insert(
                iterator->second.participantId
            );
        }
    }

    return participants;
}

// -----------------------------------------------------------------------------
// 8. Co-occurrence
// -----------------------------------------------------------------------------

map<pair<string, string>, int> codeCooccurrence(
    const vector<CodingAssignment>& assignments
) {
    map<string, set<string>> codesByNote;

    for (const CodingAssignment& assignment : assignments) {
        codesByNote[assignment.noteId].insert(
            assignment.codeId
        );
    }

    map<pair<string, string>, int> pairs;

    for (const auto& entry : codesByNote) {
        const vector<string> codes(
            entry.second.begin(),
            entry.second.end()
        );

        for (size_t i = 0; i < codes.size(); ++i) {
            for (size_t j = i + 1; j < codes.size(); ++j) {
                ++pairs[{codes[i], codes[j]}];
            }
        }
    }

    return pairs;
}

// -----------------------------------------------------------------------------
// 9. Pattern detection
// -----------------------------------------------------------------------------

struct PatternRule {
    string patternId;
    string name;
    string description;
    set<string> requiredCodes;
};

vector<PatternRule> buildPatternRules() {
    return {
        {
            "P01",
            "dashboard-to-spreadsheet workflow",
            "The dashboard supports initial retrieval while customized work continues elsewhere.",
            {"C02", "C03"}
        },
        {
            "P02",
            "verification behavior",
            "Participants validate or question dashboard information.",
            {"C07"}
        },
        {
            "P03",
            "navigation and filtering friction",
            "Participants encounter difficulty locating or configuring information.",
            {"C04", "C05"}
        },
        {
            "P04",
            "metric understanding gap",
            "Participants experience uncertainty about definitions or calculations.",
            {"C08"}
        },
        {
            "P05",
            "meeting-oriented use",
            "Dashboard use supports meetings or reviews.",
            {"C10"}
        },
        {
            "P06",
            "performance-driven workaround",
            "Slow response encourages external analysis.",
            {"C03", "C06"}
        }
    };
}

vector<Pattern> detectPatterns(
    const vector<InterviewNote>& notes,
    const vector<CodingAssignment>& assignments
) {
    map<string, set<string>> codesByNote;

    for (const CodingAssignment& assignment : assignments) {
        codesByNote[assignment.noteId].insert(
            assignment.codeId
        );
    }

    vector<Pattern> patterns;

    for (const PatternRule& rule : buildPatternRules()) {
        vector<string> supportingNotes;

        for (const auto& entry : codesByNote) {
            bool supported = true;

            for (const string& requiredCode : rule.requiredCodes) {
                if (!entry.second.count(requiredCode)) {
                    supported = false;
                    break;
                }
            }

            if (supported) {
                supportingNotes.push_back(entry.first);
            }
        }

        if (!supportingNotes.empty()) {
            patterns.push_back({
                rule.patternId,
                rule.name,
                rule.description,
                vector<string>(
                    rule.requiredCodes.begin(),
                    rule.requiredCodes.end()
                ),
                supportingNotes
            });
        }
    }

    return patterns;
}

// -----------------------------------------------------------------------------
// 10. Theme construction
// -----------------------------------------------------------------------------

struct ThemeRule {
    string themeId;
    string name;
    string researchQuestion;
    string description;
    vector<string> patterns;
};

vector<ThemeRule> buildThemeRules() {
    return {
        {
            "T01",
            "efficiency with boundary conditions",
            "How does the system affect work efficiency?",
            "The dashboard can reduce initial information-gathering effort, but efficiency depends on task complexity, navigation, and system performance.",
            {"P01", "P03", "P06"}
        },
        {
            "T02",
            "dashboard as an entry point rather than a complete workflow",
            "How does the system fit into broader analytical workflows?",
            "The dashboard often serves as a starting point, while customized analysis continues elsewhere.",
            {"P01", "P06"}
        },
        {
            "T03",
            "trust depends on interpretability and verification",
            "What affects confidence in dashboard information?",
            "Participants describe verification behavior and uncertainty when metric definitions are unclear.",
            {"P02", "P04"}
        },
        {
            "T04",
            "usage varies by task and user",
            "How consistently is the system used?",
            "Interviewees use materially different workflows, from dashboard-only use to frequent exports.",
            {"P01", "P03"}
        }
    };
}

vector<string> uniqueStrings(const vector<string>& values) {
    set<string> unique(
        values.begin(),
        values.end()
    );

    return {
        unique.begin(),
        unique.end()
    };
}

vector<Theme> buildThemes(
    const vector<InterviewNote>& notes,
    const vector<Pattern>& patterns
) {
    unordered_map<string, Pattern> patternMap;

    for (const Pattern& pattern : patterns) {
        patternMap[pattern.patternId] = pattern;
    }

    const auto noteMap = buildNoteIndex(notes);

    vector<Theme> themes;

    for (const ThemeRule& rule : buildThemeRules()) {
        vector<string> supportingNotes;

        for (const string& patternId : rule.patterns) {
            auto iterator = patternMap.find(patternId);

            if (iterator == patternMap.end()) {
                continue;
            }

            supportingNotes.insert(
                supportingNotes.end(),
                iterator->second.supportingNotes.begin(),
                iterator->second.supportingNotes.end()
            );
        }

        supportingNotes = uniqueStrings(supportingNotes);

        vector<string> contradictoryNotes;

        if (rule.themeId == "T01") {
            for (const InterviewNote& note : notes) {
                if (containsIgnoreCase(
                        note.text,
                        {
                            "filters are easy",
                            "rarely need another tool",
                            "clear enough"
                        }
                    )) {
                    contradictoryNotes.push_back(note.noteId);
                }
            }
        }

        if (rule.themeId == "T02") {
            for (const InterviewNote& note : notes) {
                if (containsIgnoreCase(
                        note.text,
                        {
                            "rarely need another tool",
                            "do not export data"
                        }
                    )) {
                    contradictoryNotes.push_back(note.noteId);
                }
            }
        }

        if (rule.themeId == "T03") {
            for (const InterviewNote& note : notes) {
                if (containsIgnoreCase(
                        note.text,
                        {"clear enough"}
                    )) {
                    contradictoryNotes.push_back(note.noteId);
                }
            }
        }

        set<string> supportingParticipants;
        set<string> contradictoryParticipants;

        for (const string& noteId : supportingNotes) {
            auto iterator = noteMap.find(noteId);

            if (iterator != noteMap.end()) {
                supportingParticipants.insert(
                    iterator->second.participantId
                );
            }
        }

        for (const string& noteId : contradictoryNotes) {
            auto iterator = noteMap.find(noteId);

            if (iterator != noteMap.end()) {
                contradictoryParticipants.insert(
                    iterator->second.participantId
                );
            }
        }

        const double denominator =
            static_cast<double>(
                supportingParticipants.size() +
                contradictoryParticipants.size()
            );

        const double confidence =
            denominator == 0.0
                ? 0.0
                : supportingParticipants.size() / denominator;

        themes.push_back({
            rule.themeId,
            rule.name,
            rule.researchQuestion,
            rule.description,
            rule.patterns,
            supportingNotes,
            contradictoryNotes,
            confidence
        });
    }

    return themes;
}

// -----------------------------------------------------------------------------
// 11. Claims and evidence analysis
// -----------------------------------------------------------------------------

vector<Claim> buildClaims() {
    return {
        {
            "CL01",
            "P01 reports that the dashboard reduces the need to open several spreadsheets.",
            EvidenceLevel::Direct,
            {"N01"},
            {},
            "The participant explicitly described the workflow."
        },
        {
            "CL02",
            "The dashboard saves time for every user.",
            EvidenceLevel::Assumption,
            {"N02"},
            {},
            "One participant cannot establish a universal claim."
        },
        {
            "CL03",
            "Some participants use the dashboard as an initial step and then export data.",
            EvidenceLevel::Interpreted,
            {"N01", "N03", "N10", "N11", "N19"},
            {},
            "Multiple direct observations support a broader workflow interpretation."
        },
        {
            "CL04",
            "Metric ambiguity may reduce confidence in dashboard information.",
            EvidenceLevel::Interpreted,
            {"N04", "N08", "N12", "N20"},
            {},
            "Verification behavior and uncertainty about definitions occur together."
        },
        {
            "CL05",
            "Every participant dislikes the dashboard interface.",
            EvidenceLevel::Assumption,
            {"N17"},
            {"N13", "N14", "N16"},
            "The dataset contains participants reporting positive experiences."
        }
    };
}

double evidenceStrength(
    const Claim& claim,
    const vector<InterviewNote>& notes
) {
    const auto noteMap = buildNoteIndex(notes);

    vector<InterviewNote> supportingNotes;

    for (const string& noteId : claim.supportingNoteIds) {
        auto iterator = noteMap.find(noteId);

        if (iterator != noteMap.end()) {
            supportingNotes.push_back(iterator->second);
        }
    }

    if (supportingNotes.empty()) {
        return 0.0;
    }

    set<string> participants;

    size_t directCount = 0;

    for (const InterviewNote& note : supportingNotes) {
        participants.insert(note.participantId);

        if (note.evidenceLevel == EvidenceLevel::Direct) {
            ++directCount;
        }
    }

    const double supportComponent = min(
        supportingNotes.size() / 5.0,
        1.0
    );

    const double participantComponent = min(
        participants.size() / 5.0,
        1.0
    );

    const double directComponent =
        static_cast<double>(directCount) /
        supportingNotes.size();

    const double contradictionComponent =
        1.0 /
        (1.0 + claim.contradictingNoteIds.size());

    double multiplier = 1.0;

    switch (claim.level) {
        case EvidenceLevel::Direct:
            multiplier = 1.0;
            break;
        case EvidenceLevel::Observed:
            multiplier = 0.95;
            break;
        case EvidenceLevel::Interpreted:
            multiplier = 0.75;
            break;
        case EvidenceLevel::Assumption:
            multiplier = 0.15;
            break;
    }

    const double score =
        (
            0.30 * supportComponent +
            0.30 * participantComponent +
            0.20 * directComponent +
            0.20 * contradictionComponent
        ) * multiplier;

    return score;
}

// -----------------------------------------------------------------------------
// 12. Participant profiles
// -----------------------------------------------------------------------------

struct ParticipantProfile {
    string participantId;
    size_t noteCount = 0;
    size_t assignmentCount = 0;
    set<string> uniqueCodes;
    vector<string> topCodes;
};

vector<ParticipantProfile> buildParticipantProfiles(
    const vector<InterviewNote>& notes,
    const vector<CodingAssignment>& assignments
) {
    const auto noteMap = buildNoteIndex(notes);

    map<string, vector<string>> codesByParticipant;
    map<string, size_t> noteCounts;

    for (const InterviewNote& note : notes) {
        ++noteCounts[note.participantId];
    }

    for (const CodingAssignment& assignment : assignments) {
        auto iterator = noteMap.find(assignment.noteId);

        if (iterator != noteMap.end()) {
            codesByParticipant[iterator->second.participantId]
                .push_back(assignment.codeId);
        }
    }

    vector<ParticipantProfile> profiles;

    for (const auto& entry : noteCounts) {
        ParticipantProfile profile;

        profile.participantId = entry.first;
        profile.noteCount = entry.second;

        map<string, int> counts;

        for (const string& codeId : codesByParticipant[entry.first]) {
            ++counts[codeId];
            profile.uniqueCodes.insert(codeId);
        }

        profile.assignmentCount =
            codesByParticipant[entry.first].size();

        vector<pair<string, int>> ranked(
            counts.begin(),
            counts.end()
        );

        sort(
            ranked.begin(),
            ranked.end(),
            [](const auto& left, const auto& right) {
                if (left.second != right.second) {
                    return left.second > right.second;
                }

                return left.first < right.first;
            }
        );

        for (
            size_t i = 0;
            i < ranked.size() && i < 5;
            ++i
        ) {
            profile.topCodes.push_back(ranked[i].first);
        }

        profiles.push_back(profile);
    }

    return profiles;
}

// -----------------------------------------------------------------------------
// 13. Coding matrix
// -----------------------------------------------------------------------------

map<string, map<string, int>> buildCodingMatrix(
    const vector<InterviewNote>& notes,
    const map<string, Code>& codebook,
    const vector<CodingAssignment>& assignments
) {
    const auto noteMap = buildNoteIndex(notes);

    map<string, map<string, int>> matrix;

    for (const InterviewNote& note : notes) {
        for (const auto& codeEntry : codebook) {
            matrix[note.participantId][codeEntry.first] = 0;
        }
    }

    for (const CodingAssignment& assignment : assignments) {
        auto noteIterator = noteMap.find(assignment.noteId);

        if (noteIterator != noteMap.end()) {
            matrix[noteIterator->second.participantId]
                 [assignment.codeId] = 1;
        }
    }

    return matrix;
}

// -----------------------------------------------------------------------------
// 14. Validation
// -----------------------------------------------------------------------------

vector<string> validateCoding(
    const vector<InterviewNote>& notes,
    const map<string, Code>& codebook,
    const vector<CodingAssignment>& assignments
) {
    set<string> noteIds;

    for (const InterviewNote& note : notes) {
        noteIds.insert(note.noteId);
    }

    vector<string> errors;

    for (const CodingAssignment& assignment : assignments) {
        if (!noteIds.count(assignment.noteId)) {
            errors.push_back(
                "Unknown note: " + assignment.noteId
            );
        }

        if (!codebook.count(assignment.codeId)) {
            errors.push_back(
                "Unknown code: " + assignment.codeId
            );
        }

        if (
            assignment.confidence < 0.0 ||
            assignment.confidence > 1.0
        ) {
            errors.push_back(
                "Invalid confidence: " +
                assignment.noteId +
                "/" +
                assignment.codeId
            );
        }

        if (assignment.rationale.empty()) {
            errors.push_back(
                "Missing rationale: " +
                assignment.noteId +
                "/" +
                assignment.codeId
            );
        }
    }

    return errors;
}

// -----------------------------------------------------------------------------
// 15. Report
// -----------------------------------------------------------------------------

void printDataset(
    const vector<InterviewNote>& notes
) {
    cout << left
         << setw(6) << "ID"
         << setw(14) << "Participant"
         << setw(10) << "Question"
         << setw(14) << "Evidence"
         << "Text\n";

    cout << string(78, '-') << "\n";

    for (const InterviewNote& note : notes) {
        cout << left
             << setw(6) << note.noteId
             << setw(14) << note.participantId
             << setw(10) << note.questionId
             << setw(14) << evidenceLevelToString(note.evidenceLevel)
             << shorten(note.text)
             << "\n";
    }
}

void printCodeStatistics(
    const map<string, Code>& codebook,
    const vector<InterviewNote>& notes,
    const vector<CodingAssignment>& assignments
) {
    const auto frequencies = codeFrequency(assignments);
    const auto participants = participantsByCode(
        notes,
        assignments
    );

    cout << left
         << setw(7) << "Code"
         << setw(34) << "Name"
         << setw(14) << "Occurrences"
         << "Participants\n";

    cout << string(78, '-') << "\n";

    for (const auto& entry : frequencies) {
        const string& codeId = entry.first;

        cout << left
             << setw(7) << codeId
             << setw(34) << codebook.at(codeId).name
             << setw(14) << entry.second
             << participants.at(codeId).size()
             << "\n";
    }
}

void printPatterns(
    const vector<Pattern>& patterns
) {
    for (const Pattern& pattern : patterns) {
        cout << "\n"
             << pattern.patternId
             << ": "
             << pattern.name
             << "\n";

        cout << "  " << pattern.description << "\n";
        cout << "  Codes: ";

        for (const string& code : pattern.supportingCodes) {
            cout << code << " ";
        }

        cout << "\n  Notes: ";

        for (const string& note : pattern.supportingNotes) {
            cout << note << " ";
        }

        cout << "\n";
    }
}

void printThemes(
    const vector<Theme>& themes
) {
    for (const Theme& theme : themes) {
        cout << "\n"
             << theme.themeId
             << ": "
             << theme.name
             << "\n";

        cout << "  Research question: "
             << theme.researchQuestion
             << "\n";

        cout << "  Description: "
             << theme.description
             << "\n";

        cout << "  Supporting patterns: ";

        for (const string& pattern : theme.supportingPatterns) {
            cout << pattern << " ";
        }

        cout << "\n  Supporting notes: ";

        for (const string& note : theme.supportingNotes) {
            cout << note << " ";
        }

        cout << "\n  Contradictory notes: ";

        if (theme.contradictoryNotes.empty()) {
            cout << "None";
        } else {
            for (const string& note : theme.contradictoryNotes) {
                cout << note << " ";
            }
        }

        cout << "\n  Support indicator: "
             << fixed
             << setprecision(3)
             << theme.confidence
             << "\n";
    }
}

void printClaims(
    const vector<Claim>& claims,
    const vector<InterviewNote>& notes
) {
    for (const Claim& claim : claims) {
        cout << "\n"
             << claim.claimId
             << ": "
             << claim.text
             << "\n";

        cout << "  Level: "
             << evidenceLevelToString(claim.level)
             << "\n";

        cout << "  Supporting notes: ";

        for (const string& note : claim.supportingNoteIds) {
            cout << note << " ";
        }

        cout << "\n  Contradicting notes: ";

        if (claim.contradictingNoteIds.empty()) {
            cout << "None";
        } else {
            for (const string& note : claim.contradictingNoteIds) {
                cout << note << " ";
            }
        }

        cout << "\n  Rationale: "
             << claim.rationale
             << "\n";

        cout << "  Evidence-support indicator: "
             << fixed
             << setprecision(3)
             << evidenceStrength(claim, notes)
             << "\n";
    }
}

// -----------------------------------------------------------------------------
// 16. Case-study application
// -----------------------------------------------------------------------------

class InterviewAnalysisSystem {
private:
    vector<InterviewNote> notes;
    map<string, Code> codebook;
    vector<CodingAssignment> assignments;
    vector<Pattern> patterns;
    vector<Theme> themes;
    vector<Claim> claims;

public:
    InterviewAnalysisSystem()
        : notes(buildInterviewDataset()),
          codebook(buildCodebook()),
          claims(buildClaims()) {}

    void ingest() {
        if (notes.empty()) {
            throw runtime_error(
                "Interview dataset cannot be empty."
            );
        }

        cout << "Loaded "
             << notes.size()
             << " interview notes.\n";
    }

    void code() {
        const vector<CodingAssignment> candidates =
            candidateCoding(notes);

        assignments = reviewCoding(
            notes,
            candidates
        );

        cout << "Candidate assignments: "
             << candidates.size()
             << "\n";

        cout << "Reviewed assignments: "
             << assignments.size()
             << "\n";
    }

    void constructPatterns() {
        patterns = detectPatterns(
            notes,
            assignments
        );
    }

    void constructThemes() {
        themes = buildThemes(
            notes,
            patterns
        );
    }

    void validate() const {
        const vector<string> errors =
            validateCoding(
                notes,
                codebook,
                assignments
            );

        if (errors.empty()) {
            cout << "Coding validation passed.\n";
            return;
        }

        for (const string& error : errors) {
            cerr << "VALIDATION ERROR: "
                 << error
                 << "\n";
        }

        throw runtime_error(
            "Coding validation failed."
        );
    }

    void report() const {
        printSection("Interview dataset");
        printDataset(notes);

        printSection("Code statistics");
        printCodeStatistics(
            codebook,
            notes,
            assignments
        );

        printSection("Code co-occurrence");

        const auto pairs =
            codeCooccurrence(assignments);

        for (const auto& entry : pairs) {
            cout << entry.first.first
                 << " + "
                 << entry.first.second
                 << ": "
                 << entry.second
                 << "\n";
        }

        printSection("Patterns");
        printPatterns(patterns);

        printSection("Themes");
        printThemes(themes);

        printSection("Evidence versus assumptions");
        printClaims(claims, notes);

        printSection("Participant profiles");

        const auto profiles =
            buildParticipantProfiles(
                notes,
                assignments
            );

        for (const ParticipantProfile& profile : profiles) {
            cout << profile.participantId
                 << ": notes="
                 << profile.noteCount
                 << ", assignments="
                 << profile.assignmentCount
                 << ", unique codes="
                 << profile.uniqueCodes.size()
                 << "\n";

            cout << "  Top codes: ";

            for (const string& code : profile.topCodes) {
                cout << code << " ";
            }

            cout << "\n";
        }

        printSection("Coding matrix");

        const auto matrix =
            buildCodingMatrix(
                notes,
                codebook,
                assignments
            );

        cout << setw(14) << "Participant";

        for (const auto& code : codebook) {
            cout << setw(5) << code.first;
        }

        cout << "\n";

        for (const auto& participant : matrix) {
            cout << setw(14)
                 << participant.first;

            for (const auto& code : codebook) {
                cout << setw(5)
                     << participant.second.at(code.first);
            }

            cout << "\n";
        }
    }

    void search(const string& query) const {
        printSection(
            "Keyword search: " + query
        );

        const string normalizedQuery =
            lowerCopy(query);

        for (const InterviewNote& note : notes) {
            if (
                lowerCopy(note.text)
                    .find(normalizedQuery)
                != string::npos
            ) {
                cout << note.noteId
                     << ": "
                     << note.text
                     << "\n";
            }
        }
    }

    void demonstrateConstraints() const {
        printSection("Design and performance considerations");

        const size_t n = notes.size();
        const size_t m = codebook.size();

        cout << "Number of notes: "
             << n
             << "\n";

        cout << "Number of codes: "
             << m
             << "\n";

        cout << "Rule-assisted coding: approximately O(N*M*K), "
             << "where K is average phrase matching work.\n";

        cout << "Code co-occurrence: approximately O(N*C^2), "
             << "where C is the number of distinct codes attached to a note.\n";

        cout << "A pairwise note similarity implementation would require "
             << "O(N^2) note comparisons.\n";

        cout << "For large datasets, indexed storage and sparse representations "
             << "can reduce repeated scanning.\n";

        cout << "\nTrade-offs:\n";
        cout << "- unordered_map gives fast average lookup but does not preserve order.\n";
        cout << "- map preserves sorted keys but typically has logarithmic lookup.\n";
        cout << "- transparent rules are easy to audit but have limited semantic coverage.\n";
        cout << "- automated coding scales better but can miss context and negation.\n";
        cout << "- manual coding captures nuance but requires time and analyst discipline.\n";
    }
};

// -----------------------------------------------------------------------------
// 17. Main
// -----------------------------------------------------------------------------

int main() {
    try {
        InterviewAnalysisSystem system;

        system.ingest();
        system.code();
        system.validate();
        system.constructPatterns();
        system.constructThemes();

        system.report();

        system.search("export");
        system.demonstrateConstraints();

        printSection("Industry-style analytical statements");

        cout << "1. Several participants use the dashboard for rapid "
             << "information retrieval, while customized analysis frequently "
             << "continues in spreadsheets.\n";

        cout << "2. Exporting appears associated with analytical tasks that "
             << "exceed the dashboard's available calculations or views.\n";

        cout << "3. Trust varies with the clarity of metric definitions and "
             << "the need to verify unusual values.\n";

        cout << "4. The interviews show meaningful variation in workflow, "
             << "including participants who rarely leave the dashboard.\n";

        printSection("Methodological controls");

        cout << "- Frequency is descriptive and does not automatically establish importance.\n";
        cout << "- Co-occurrence does not establish causality.\n";
        cout << "- Automated coding is candidate generation, not final judgment.\n";
        cout << "- Contradictory cases must remain visible.\n";
        cout << "- Participant statements should not be rewritten as independently verified facts.\n";
        cout << "- Small interview samples should not be treated as population statistics.\n";

        return 0;
    }
    catch (const exception& error) {
        cerr << "Analysis failed: "
             << error.what()
             << "\n";

        return 1;
    }
}
