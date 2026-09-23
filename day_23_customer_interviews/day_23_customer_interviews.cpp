#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

/*
    Customer Interview Research System

    This C++17 case study models an industry-style customer research workflow.

    Scenario:
        A software company wants to understand how small businesses manage
        overdue invoices. The research team needs to conduct interviews,
        capture evidence, classify statements, identify themes, preserve
        contradictions, and produce an evidence-based research report.

    The program demonstrates:
        - Domain modeling with classes and structs
        - Validation
        - Question design
        - Bias detection
        - Interview records
        - Evidence classification
        - Probing
        - Thematic analysis
        - Contradiction handling
        - Frequency analysis
        - Complexity considerations
        - Defensive programming
        - Modular design
        - Report generation
*/


// -----------------------------------------------------------------------------
// 1. UTILITY FUNCTIONS
// -----------------------------------------------------------------------------

string toLower(string value) {
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

bool containsIgnoreCase(const string& text, const string& phrase) {
    return toLower(text).find(toLower(phrase)) != string::npos;
}

vector<string> tokenize(const string& text) {
    vector<string> words;
    string current;

    for (char character : text) {
        if (isalpha(static_cast<unsigned char>(character))) {
            current += static_cast<char>(
                tolower(static_cast<unsigned char>(character))
            );
        } else if (!current.empty()) {
            words.push_back(current);
            current.clear();
        }
    }

    if (!current.empty()) {
        words.push_back(current);
    }

    return words;
}

bool isStopWord(const string& word) {
    static const set<string> stopWords = {
        "the", "a", "an", "and", "or", "to", "of", "in", "on",
        "for", "is", "it", "i", "we", "this", "that", "with",
        "my", "our", "was", "are", "be", "have", "has"
    };

    return stopWords.count(word) > 0;
}


// -----------------------------------------------------------------------------
// 2. RESEARCH OBJECTIVE
// -----------------------------------------------------------------------------

struct ResearchObjective {
    string primaryQuestion;
    vector<string> evidenceNeeded;
    vector<string> outOfScope;

    void print() const {
        cout << "\nResearch question:\n"
             << primaryQuestion << "\n";

        cout << "\nEvidence needed:\n";
        for (const auto& item : evidenceNeeded) {
            cout << "  - " << item << "\n";
        }

        cout << "\nOut of scope:\n";
        for (const auto& item : outOfScope) {
            cout << "  - " << item << "\n";
        }
    }
};


// -----------------------------------------------------------------------------
// 3. PARTICIPANT
// -----------------------------------------------------------------------------

class Participant {
private:
    string id;
    string name;
    string role;
    string companySize;
    string experience;

public:
    Participant(
        string id,
        string name,
        string role,
        string companySize,
        string experience
    )
        : id(move(id)),
          name(move(name)),
          role(move(role)),
          companySize(move(companySize)),
          experience(move(experience)) {}

    const string& getId() const {
        return id;
    }

    const string& getRole() const {
        return role;
    }

    const string& getCompanySize() const {
        return companySize;
    }

    bool isEligible(const string& requiredRole) const {
        return toLower(role) == toLower(requiredRole);
    }

    void print() const {
        cout << id << " | "
             << name << " | "
             << role << " | "
             << companySize << " | "
             << experience << "\n";
    }
};


// -----------------------------------------------------------------------------
// 4. QUESTION MODEL AND BIAS DETECTION
// -----------------------------------------------------------------------------

enum class QuestionType {
    Behavioral,
    Open,
    Probing,
    Leading,
    Hypothetical,
    DoubleBarreled,
    Unknown
};

string questionTypeToString(QuestionType type) {
    switch (type) {
        case QuestionType::Behavioral:
            return "Behavioral";
        case QuestionType::Open:
            return "Open";
        case QuestionType::Probing:
            return "Probing";
        case QuestionType::Leading:
            return "Leading";
        case QuestionType::Hypothetical:
            return "Hypothetical";
        case QuestionType::DoubleBarreled:
            return "Double-barreled";
        default:
            return "Unknown";
    }
}

struct InterviewQuestion {
    string text;
    QuestionType type;
    string purpose;

    vector<string> detectRisks() const {
        vector<string> risks;
        const string lower = toLower(text);

        if (
            lower.find("don't you think") != string::npos ||
            lower.find("wouldn't you") != string::npos ||
            lower.find("would you agree") != string::npos ||
            lower.find("isn't it") != string::npos
        ) {
            risks.push_back("Leading wording");
        }

        if (
            lower.find("would you use") != string::npos ||
            lower.find("would you buy") != string::npos ||
            lower.find("would you pay") != string::npos
        ) {
            risks.push_back("Hypothetical behavior");
        }

        if (
            lower.find(" and ") != string::npos ||
            lower.find(" or ") != string::npos
        ) {
            risks.push_back("Possibly double-barreled");
        }

        if (tokenize(text).size() > 30) {
            risks.push_back("Question may be too complex");
        }

        return risks;
    }
};


// -----------------------------------------------------------------------------
// 5. EVIDENCE MODEL
// -----------------------------------------------------------------------------

enum class EvidenceType {
    ConcreteBehavior,
    StatedOpinion,
    HypotheticalIntention,
    GeneralStatement
};

string evidenceTypeToString(EvidenceType type) {
    switch (type) {
        case EvidenceType::ConcreteBehavior:
            return "Concrete behavior";
        case EvidenceType::StatedOpinion:
            return "Stated opinion";
        case EvidenceType::HypotheticalIntention:
            return "Hypothetical intention";
        default:
            return "General statement";
    }
}

struct Evidence {
    string participantId;
    string text;
    EvidenceType type;
    int strength;
    string rationale;
};

Evidence classifyEvidence(
    const string& participantId,
    const string& statement
) {
    const string lower = toLower(statement);

    if (
        lower.find("last week") != string::npos ||
        lower.find("last month") != string::npos ||
        lower.find("yesterday") != string::npos ||
        lower.find("this morning") != string::npos
    ) {
        return {
            participantId,
            statement,
            EvidenceType::ConcreteBehavior,
            5,
            "The statement describes a concrete past event."
        };
    }

    if (
        lower.rfind("i think", 0) == 0 ||
        lower.rfind("i believe", 0) == 0 ||
        lower.rfind("i feel", 0) == 0
    ) {
        return {
            participantId,
            statement,
            EvidenceType::StatedOpinion,
            3,
            "The statement explicitly describes a belief or opinion."
        };
    }

    if (
        lower.find("would") != string::npos ||
        lower.find("might") != string::npos ||
        lower.find("probably") != string::npos
    ) {
        return {
            participantId,
            statement,
            EvidenceType::HypotheticalIntention,
            2,
            "The statement concerns possible rather than observed behavior."
        };
    }

    return {
        participantId,
        statement,
        EvidenceType::GeneralStatement,
        3,
        "The statement lacks sufficient context for stronger classification."
    };
}


// -----------------------------------------------------------------------------
// 6. INTERVIEW RECORD
// -----------------------------------------------------------------------------

struct InterviewNote {
    string observation;
    optional<string> quote;
    optional<string> interpretation;
};

class InterviewRecord {
private:
    Participant participant;
    vector<InterviewQuestion> questions;
    vector<string> answers;
    vector<InterviewNote> notes;

public:
    explicit InterviewRecord(const Participant& participant)
        : participant(participant) {}

    void addQuestion(const InterviewQuestion& question) {
        if (question.text.empty()) {
            throw invalid_argument("Interview question cannot be empty.");
        }

        questions.push_back(question);
    }

    void addAnswer(const string& answer) {
        if (answer.empty()) {
            throw invalid_argument("Interview answer cannot be empty.");
        }

        answers.push_back(answer);
    }

    void addNote(
        const string& observation,
        optional<string> quote = nullopt,
        optional<string> interpretation = nullopt
    ) {
        if (observation.empty()) {
            throw invalid_argument("Observation cannot be empty.");
        }

        notes.push_back({
            observation,
            move(quote),
            move(interpretation)
        });
    }

    const Participant& getParticipant() const {
        return participant;
    }

    const vector<InterviewQuestion>& getQuestions() const {
        return questions;
    }

    const vector<string>& getAnswers() const {
        return answers;
    }

    const vector<InterviewNote>& getNotes() const {
        return notes;
    }

    bool isConsistent() const {
        return questions.size() == answers.size();
    }
};


// -----------------------------------------------------------------------------
// 7. PROBING ENGINE
// -----------------------------------------------------------------------------

class ProbeEngine {
public:
    static string chooseProbe(const string& answer) {
        const string lower = toLower(answer);

        if (
            lower.find("usually") != string::npos ||
            lower.find("often") != string::npos
        ) {
            return "When did this last happen?";
        }

        if (
            lower.find("problem") != string::npos ||
            lower.find("difficult") != string::npos
        ) {
            return "Can you give me a recent example?";
        }

        if (
            lower.find("then") != string::npos ||
            lower.find("after") != string::npos
        ) {
            return "What happened next?";
        }

        return "What do you mean by that?";
    }
};


// -----------------------------------------------------------------------------
// 8. THEMATIC ANALYSIS
// -----------------------------------------------------------------------------

class ThemeAnalyzer {
public:
    static map<string, int> wordFrequency(
        const vector<Evidence>& evidence
    ) {
        map<string, int> frequencies;

        for (const auto& item : evidence) {
            for (const auto& word : tokenize(item.text)) {
                if (!isStopWord(word) && word.size() > 2) {
                    ++frequencies[word];
                }
            }
        }

        return frequencies;
    }

    static map<string, vector<Evidence>> groupByTheme(
        const vector<Evidence>& evidence
    ) {
        map<string, vector<Evidence>> grouped;

        for (const auto& item : evidence) {
            const string lower = toLower(item.text);

            if (
                lower.find("spreadsheet") != string::npos ||
                lower.find("copy") != string::npos ||
                lower.find("manual") != string::npos
            ) {
                grouped["Manual work"].push_back(item);
            } else if (
                lower.find("reminder") != string::npos ||
                lower.find("calendar") != string::npos
            ) {
                grouped["Reminders"].push_back(item);
            } else if (
                lower.find("difficult") != string::npos ||
                lower.find("problem") != string::npos ||
                lower.find("slow") != string::npos
            ) {
                grouped["Pain points"].push_back(item);
            } else {
                grouped["Other"].push_back(item);
            }
        }

        return grouped;
    }
};


// -----------------------------------------------------------------------------
// 9. CONTRADICTION ANALYSIS
// -----------------------------------------------------------------------------

struct ContradictionGroup {
    vector<Evidence> supporting;
    vector<Evidence> contradicting;
};

ContradictionGroup identifyContradictions(
    const vector<Evidence>& evidence
) {
    ContradictionGroup result;

    for (const auto& item : evidence) {
        const string lower = toLower(item.text);

        if (
            lower.find("works well") != string::npos ||
            lower.find("sufficient") != string::npos ||
            lower.find("easy") != string::npos
        ) {
            result.supporting.push_back(item);
        }

        if (
            lower.find("difficult") != string::npos ||
            lower.find("slow") != string::npos ||
            lower.find("problem") != string::npos
        ) {
            result.contradicting.push_back(item);
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// 10. RESEARCH REPORT
// -----------------------------------------------------------------------------

class ResearchReport {
private:
    ResearchObjective objective;
    vector<Evidence> evidence;

public:
    ResearchReport(
        ResearchObjective objective,
        vector<Evidence> evidence
    )
        : objective(move(objective)),
          evidence(move(evidence)) {}

    void print() const {
        cout << "\n"
             << "============================================================\n"
             << "CUSTOMER RESEARCH REPORT\n"
             << "============================================================\n";

        cout << "\nResearch objective:\n"
             << objective.primaryQuestion << "\n";

        cout << "\nEvidence records: "
             << evidence.size() << "\n";

        map<EvidenceType, int> counts;

        for (const auto& item : evidence) {
            ++counts[item.type];
        }

        cout << "\nEvidence classification:\n";

        for (const auto& [type, count] : counts) {
            cout << "  "
                 << evidenceTypeToString(type)
                 << ": "
                 << count
                 << "\n";
        }

        cout << "\nEvidence detail:\n";

        for (const auto& item : evidence) {
            cout << "  ["
                 << item.participantId
                 << "] "
                 << evidenceTypeToString(item.type)
                 << " | strength="
                 << item.strength
                 << "\n    "
                 << item.text
                 << "\n";
        }

        auto themes = ThemeAnalyzer::groupByTheme(evidence);

        cout << "\nThemes:\n";

        for (const auto& [theme, items] : themes) {
            cout << "  "
                 << theme
                 << " ("
                 << items.size()
                 << " evidence records)\n";
        }

        auto contradictions = identifyContradictions(evidence);

        cout << "\nContradiction check:\n";
        cout << "  Statements indicating adequacy: "
             << contradictions.supporting.size()
             << "\n";
        cout << "  Statements indicating difficulty: "
             << contradictions.contradicting.size()
             << "\n";

        cout << "\nThe report preserves both supporting and contradictory evidence.\n";
    }
};


// -----------------------------------------------------------------------------
// 11. PERFORMANCE ANALYSIS
// -----------------------------------------------------------------------------

void demonstrateComplexity() {
    cout << "\n"
         << "============================================================\n"
         << "COMPLEXITY CONSIDERATIONS\n"
         << "============================================================\n";

    cout << R"(
Question validation:
    For a question containing n characters, simple substring checks are
    approximately O(n) for each pattern in ordinary usage.

Evidence classification:
    Approximately O(n) for a statement of length n when using linear scans.

Token frequency:
    If there are N total tokens, the counting process is approximately O(N)
    expected time using a hash table or O(N log K) using an ordered map,
    where K is the number of distinct terms.

Theme grouping:
    Approximately O(N) for N evidence records when each record is classified
    with a fixed number of keyword checks.

Memory:
    Interview records require storage proportional to the number of questions,
    answers, notes, and evidence records.

Important engineering trade-off:
    A more sophisticated natural-language analysis system could produce richer
    classifications but would introduce additional dependencies, complexity,
    and opportunities for incorrect interpretation. Simple deterministic
    rules are easier to inspect and audit, but they are less capable of
    understanding context.
)";
}


// -----------------------------------------------------------------------------
// 12. VALIDATION AND FAILURE CONDITIONS
// -----------------------------------------------------------------------------

void validateInterview(const InterviewRecord& interview) {
    if (!interview.isConsistent()) {
        throw runtime_error(
            "Interview validation failed: question and answer counts differ."
        );
    }

    if (interview.getQuestions().empty()) {
        throw runtime_error(
            "Interview validation failed: no questions were recorded."
        );
    }

    if (interview.getAnswers().empty()) {
        throw runtime_error(
            "Interview validation failed: no answers were recorded."
        );
    }
}


// -----------------------------------------------------------------------------
// 13. MAIN CASE STUDY
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << fixed << setprecision(2);

        cout << "CUSTOMER INTERVIEWS: C++ INDUSTRY CASE STUDY\n";

        // ---------------------------------------------------------------------
        // Define the research objective.
        // ---------------------------------------------------------------------

        ResearchObjective objective{
            "How do small businesses currently manage overdue invoices?",
            {
                "Current workflow",
                "Recent real-world behavior",
                "Frequency of follow-up",
                "Pain points",
                "Workarounds",
                "Consequences of missed follow-up"
            },
            {
                "Whether participants like our proposed product",
                "Unprompted feature wish lists",
                "Unverified assumptions about the market"
            }
        };

        objective.print();

        // ---------------------------------------------------------------------
        // Recruit and validate participants.
        // ---------------------------------------------------------------------

        cout << "\nParticipants:\n";

        vector<Participant> participants{
            Participant(
                "P01",
                "Asha",
                "Owner",
                "1-10",
                "Personally manages customer payments"
            ),
            Participant(
                "P02",
                "Ravi",
                "Accountant",
                "11-50",
                "Manages reconciliation"
            ),
            Participant(
                "P03",
                "Neha",
                "Designer",
                "1-10",
                "Does not manage billing"
            )
        };

        for (const auto& participant : participants) {
            participant.print();
        }

        // ---------------------------------------------------------------------
        // Design an interview guide.
        // ---------------------------------------------------------------------

        vector<InterviewQuestion> questions{
            {
                "Tell me about the last time you followed up on an overdue invoice.",
                QuestionType::Behavioral,
                "Capture a recent concrete event."
            },
            {
                "What happened after you contacted the customer?",
                QuestionType::Probing,
                "Understand the sequence."
            },
            {
                "What was difficult about the process?",
                QuestionType::Open,
                "Identify friction."
            },
            {
                "Would you use automatic invoice reminders?",
                QuestionType::Hypothetical,
                "Concept reaction; lower evidentiary value."
            }
        };

        cout << "\nQuestion quality review:\n";

        for (const auto& question : questions) {
            cout << "\n"
                 << questionTypeToString(question.type)
                 << ": "
                 << question.text
                 << "\n";

            cout << "Purpose: "
                 << question.purpose
                 << "\n";

            const auto risks = question.detectRisks();

            if (risks.empty()) {
                cout << "Risks: none detected by deterministic checks\n";
            } else {
                cout << "Risks:\n";

                for (const auto& risk : risks) {
                    cout << "  - " << risk << "\n";
                }
            }
        }

        // ---------------------------------------------------------------------
        // Create interview records.
        // ---------------------------------------------------------------------

        InterviewRecord interviewOne(participants[0]);

        interviewOne.addQuestion(questions[0]);
        interviewOne.addAnswer(
            "Last week I checked overdue invoices in my spreadsheet."
        );

        interviewOne.addQuestion(questions[1]);
        interviewOne.addAnswer(
            "Then I copied the customer information into an email."
        );

        interviewOne.addQuestion(questions[2]);
        interviewOne.addAnswer(
            "The difficult part is remembering which customers already received reminders."
        );

        interviewOne.addNote(
            "Participant opened a spreadsheet while explaining the workflow.",
            "I keep everything in this spreadsheet.",
            "The spreadsheet appears central to the current process."
        );

        InterviewRecord interviewTwo(participants[1]);

        interviewTwo.addQuestion(questions[0]);
        interviewTwo.addAnswer(
            "Last month I reconciled payment data manually."
        );

        interviewTwo.addQuestion(questions[1]);
        interviewTwo.addAnswer(
            "After reconciliation, I contacted customers with outstanding balances."
        );

        interviewTwo.addQuestion(questions[2]);
        interviewTwo.addAnswer(
            "Manual reconciliation is slow when there are many transactions."
        );

        interviewTwo.addNote(
            "Participant described exporting transaction information.",
            "I export the data and reconcile it manually.",
            "The existing workflow contains manual processing."
        );

        InterviewRecord interviewThree(participants[2]);

        interviewThree.addQuestion(questions[0]);
        interviewThree.addAnswer(
            "I do not handle invoices in my role."
        );

        interviewThree.addQuestion(questions[1]);
        interviewThree.addAnswer(
            "The accounting team handles those questions."
        );

        interviewThree.addQuestion(questions[2]);
        interviewThree.addAnswer(
            "I cannot provide a detailed example."
        );

        // ---------------------------------------------------------------------
        // Validate interviews.
        // ---------------------------------------------------------------------

        validateInterview(interviewOne);
        validateInterview(interviewTwo);
        validateInterview(interviewThree);

        cout << "\nAll interview records passed structural validation.\n";

        // ---------------------------------------------------------------------
        // Convert interview answers into evidence records.
        // ---------------------------------------------------------------------

        vector<Evidence> evidence;

        auto collectEvidence = [&evidence](const InterviewRecord& interview) {
            const auto& answers = interview.getAnswers();
            const string& participantId = interview.getParticipant().getId();

            for (const auto& answer : answers) {
                evidence.push_back(
                    classifyEvidence(participantId, answer)
                );
            }
        };

        collectEvidence(interviewOne);
        collectEvidence(interviewTwo);
        collectEvidence(interviewThree);

        // ---------------------------------------------------------------------
        // Demonstrate probing.
        // ---------------------------------------------------------------------

        cout << "\nProbe examples:\n";

        for (const auto& item : evidence) {
            cout << "Answer: "
                 << item.text
                 << "\n";

            cout << "Probe: "
                 << ProbeEngine::chooseProbe(item.text)
                 << "\n\n";
        }

        // ---------------------------------------------------------------------
        // Analyze themes.
        // ---------------------------------------------------------------------

        cout << "\nTheme analysis:\n";

        const auto themes = ThemeAnalyzer::groupByTheme(evidence);

        for (const auto& [theme, items] : themes) {
            cout << "\n"
                 << theme
                 << ":\n";

            for (const auto& item : items) {
                cout << "  ["
                     << item.participantId
                     << "] "
                     << item.text
                     << "\n";
            }
        }

        // ---------------------------------------------------------------------
        // Detect contradictory evidence.
        // ---------------------------------------------------------------------

        cout << "\nContradiction analysis:\n";

        const auto contradictions = identifyContradictions(evidence);

        cout << "Adequacy-related evidence: "
             << contradictions.supporting.size()
             << "\n";

        cout << "Difficulty-related evidence: "
             << contradictions.contradicting.size()
             << "\n";

        // ---------------------------------------------------------------------
        // Word-frequency analysis.
        // ---------------------------------------------------------------------

        cout << "\nKeyword frequency analysis:\n";

        const auto frequencies = ThemeAnalyzer::wordFrequency(evidence);

        vector<pair<string, int>> sortedFrequencies(
            frequencies.begin(),
            frequencies.end()
        );

        sort(
            sortedFrequencies.begin(),
            sortedFrequencies.end(),
            [](const auto& left, const auto& right) {
                if (left.second != right.second) {
                    return left.second > right.second;
                }

                return left.first < right.first;
            }
        );

        const size_t limit = min<size_t>(10, sortedFrequencies.size());

        for (size_t index = 0; index < limit; ++index) {
            cout << "  "
                 << sortedFrequencies[index].first
                 << ": "
                 << sortedFrequencies[index].second
                 << "\n";
        }

        // ---------------------------------------------------------------------
        // Generate the final research report.
        // ---------------------------------------------------------------------

        ResearchReport report(objective, evidence);
        report.print();

        // ---------------------------------------------------------------------
        // Complexity and implementation considerations.
        // ---------------------------------------------------------------------

        demonstrateComplexity();

        cout << "\n"
             << "============================================================\n"
             << "IMPLEMENTATION CONSIDERATIONS\n"
             << "============================================================\n";

        cout << R"(
For production research software, additional controls would be appropriate:

1. Access control
   Only authorized researchers should access participant information.

2. Data minimization
   Store only information required for the research purpose.

3. Separation of identifiers
   Participant identity data should be separated from analytical content
   when practical.

4. Auditability
   Changes to interview notes and research classifications should be
   traceable.

5. Data validation
   Missing, duplicated, or inconsistent interview records should be detected.

6. Privacy
   Recordings, transcripts, and quotes may contain confidential information.

7. Human review
   Automated classification should support researchers rather than silently
   replace contextual judgment.

8. Sampling discipline
   Interview results should not automatically be treated as population-level
   measurements.

9. Contradiction preservation
   A reporting system should store evidence that challenges the working
   hypothesis instead of filtering it out.

10. Reproducibility
    Researchers should preserve the question guide, participant criteria,
    coding rules, and analysis process.
)";

        cout << "\nCase study completed successfully.\n";

    } catch (const exception& error) {
        cerr << "\nProgram error: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
