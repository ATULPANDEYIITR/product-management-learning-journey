/*
 * USER RESEARCH CASE STUDY
 * ========================
 *
 * Modern C++17 implementation of a realistic user-research analytics system.
 *
 * Scenario:
 * A digital public-service portal has received reports that users struggle
 * to complete an online application. The research team combines:
 *
 *   1. Participant screening
 *   2. Interview evidence
 *   3. Usability-test observations
 *   4. Survey responses
 *   5. Qualitative coding
 *   6. Quantitative analysis
 *   7. Cross-tabulation
 *   8. Evidence triangulation
 *   9. Issue prioritization
 *  10. Research reporting
 *
 * The program uses only the C++17 standard library.
 */

#include <algorithm>
#include <cmath>
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
#include <utility>
#include <vector>

using namespace std;


// -----------------------------------------------------------------------------
// 1. OUTPUT HELPERS
// -----------------------------------------------------------------------------

void printSection(const string& title) {
    cout << "\n" << string(80, '=') << "\n";
    cout << title << "\n";
    cout << string(80, '=') << "\n";
}

void printSubsection(const string& title) {
    cout << "\n--- " << title << " ---\n";
}


// -----------------------------------------------------------------------------
// 2. PARTICIPANT MODEL
// -----------------------------------------------------------------------------

enum class ExperienceLevel {
    Beginner,
    Intermediate,
    Advanced
};

string toString(ExperienceLevel level) {
    switch (level) {
        case ExperienceLevel::Beginner:
            return "beginner";
        case ExperienceLevel::Intermediate:
            return "intermediate";
        case ExperienceLevel::Advanced:
            return "advanced";
    }

    return "unknown";
}

struct Participant {
    string id;
    int age;
    ExperienceLevel experience;
    int recentUsageCount;
    string primaryGoal;
    bool consented;
};

bool isEligible(const Participant& participant) {
    return participant.consented
        && participant.age >= 18
        && participant.age <= 70
        && participant.recentUsageCount >= 1;
}


// -----------------------------------------------------------------------------
// 3. INTERVIEW EVIDENCE
// -----------------------------------------------------------------------------

struct InterviewExcerpt {
    string participantId;
    string context;
    string text;
};

enum class ResearchCode {
    UnclearCallToAction,
    UnclearStatusLanguage,
    MissingSystemFeedback,
    UnclearNextStep,
    UnnecessaryDataRequest,
    NavigationAnxiety
};

string toString(ResearchCode code) {
    switch (code) {
        case ResearchCode::UnclearCallToAction:
            return "unclear_call_to_action";
        case ResearchCode::UnclearStatusLanguage:
            return "unclear_status_language";
        case ResearchCode::MissingSystemFeedback:
            return "missing_system_feedback";
        case ResearchCode::UnclearNextStep:
            return "unclear_next_step";
        case ResearchCode::UnnecessaryDataRequest:
            return "unnecessary_data_request";
        case ResearchCode::NavigationAnxiety:
            return "navigation_anxiety";
    }

    return "unknown";
}

vector<ResearchCode> codeInterview(const InterviewExcerpt& excerpt) {
    vector<ResearchCode> codes;
    const string& text = excerpt.text;

    if (text.find("which button") != string::npos) {
        codes.push_back(ResearchCode::UnclearCallToAction);
    }

    if (text.find("status page") != string::npos) {
        codes.push_back(ResearchCode::UnclearStatusLanguage);
    }

    if (text.find("really been uploaded") != string::npos) {
        codes.push_back(ResearchCode::MissingSystemFeedback);
    }

    if (text.find("next step") != string::npos) {
        codes.push_back(ResearchCode::UnclearNextStep);
    }

    if (text.find("information I thought") != string::npos) {
        codes.push_back(ResearchCode::UnnecessaryDataRequest);
    }

    if (text.find("going back") != string::npos) {
        codes.push_back(ResearchCode::NavigationAnxiety);
    }

    return codes;
}


// -----------------------------------------------------------------------------
// 4. USABILITY TEST MODEL
// -----------------------------------------------------------------------------

struct UsabilityResult {
    string participantId;
    bool completed;
    double timeSeconds;
    int errors;
    int satisfaction;
};

double calculateMean(const vector<double>& values) {
    if (values.empty()) {
        return 0.0;
    }

    const double sum = accumulate(values.begin(), values.end(), 0.0);
    return sum / static_cast<double>(values.size());
}

double calculateSuccessRate(const vector<UsabilityResult>& results) {
    if (results.empty()) {
        return 0.0;
    }

    const int successful = count_if(
        results.begin(),
        results.end(),
        [](const UsabilityResult& result) {
            return result.completed;
        }
    );

    return static_cast<double>(successful) / results.size();
}

double calculateAverageErrors(const vector<UsabilityResult>& results) {
    if (results.empty()) {
        return 0.0;
    }

    double total = 0.0;

    for (const auto& result : results) {
        total += result.errors;
    }

    return total / results.size();
}


// -----------------------------------------------------------------------------
// 5. SURVEY MODEL
// -----------------------------------------------------------------------------

struct SurveyResponse {
    string id;
    string ageGroup;
    int satisfaction;
    int easeOfUse;
    int recommendation;
    bool uploadProblem;
    bool statusProblem;
};

bool validateSurveyResponse(const SurveyResponse& response, string& error) {
    if (response.satisfaction < 1 || response.satisfaction > 5) {
        error = "Satisfaction must be between 1 and 5.";
        return false;
    }

    if (response.easeOfUse < 1 || response.easeOfUse > 5) {
        error = "Ease of use must be between 1 and 5.";
        return false;
    }

    if (response.recommendation < 0 || response.recommendation > 10) {
        error = "Recommendation must be between 0 and 10.";
        return false;
    }

    return true;
}

double calculateNPS(const vector<SurveyResponse>& responses) {
    if (responses.empty()) {
        return 0.0;
    }

    int promoters = 0;
    int detractors = 0;

    for (const auto& response : responses) {
        if (response.recommendation >= 9) {
            ++promoters;
        }

        if (response.recommendation <= 6) {
            ++detractors;
        }
    }

    const double promoterRate =
        100.0 * promoters / responses.size();

    const double detractorRate =
        100.0 * detractors / responses.size();

    return promoterRate - detractorRate;
}


// -----------------------------------------------------------------------------
// 6. RESEARCH REPOSITORY
// -----------------------------------------------------------------------------

struct ResearchArtifact {
    string id;
    string type;
    string content;
    optional<string> participantId;
    set<string> tags;
};

class ResearchRepository {
private:
    unordered_map<string, ResearchArtifact> artifacts;

public:
    void add(const ResearchArtifact& artifact) {
        if (artifact.id.empty()) {
            throw invalid_argument("Artifact ID cannot be empty.");
        }

        if (artifact.type.empty()) {
            throw invalid_argument("Artifact type cannot be empty.");
        }

        if (artifact.content.empty()) {
            throw invalid_argument("Artifact content cannot be empty.");
        }

        if (artifacts.find(artifact.id) != artifacts.end()) {
            throw runtime_error("Artifact ID already exists.");
        }

        artifacts.emplace(artifact.id, artifact);
    }

    vector<ResearchArtifact> findByTag(const string& tag) const {
        vector<ResearchArtifact> result;

        for (const auto& [id, artifact] : artifacts) {
            if (artifact.tags.find(tag) != artifact.tags.end()) {
                result.push_back(artifact);
            }
        }

        return result;
    }

    map<string, int> countByType() const {
        map<string, int> counts;

        for (const auto& [id, artifact] : artifacts) {
            ++counts[artifact.type];
        }

        return counts;
    }

    size_t size() const {
        return artifacts.size();
    }
};


// -----------------------------------------------------------------------------
// 7. ISSUE PRIORITIZATION
// -----------------------------------------------------------------------------

struct ResearchIssue {
    string name;
    double frequency;
    double severity;
    double confidence;

    double evidencePriority() const {
        /*
         * This is an explicit heuristic for the case study.
         * It is not a universal research formula.
         *
         * A real organization should define prioritization according to
         * its research goals, decision context, and governance requirements.
         */
        return frequency * severity * confidence;
    }
};


// -----------------------------------------------------------------------------
// 8. RESEARCH STUDY ENGINE
// -----------------------------------------------------------------------------

class UserResearchStudy {
private:
    vector<Participant> participants;
    vector<InterviewExcerpt> interviews;
    vector<UsabilityResult> usabilityResults;
    vector<SurveyResponse> surveyResponses;

public:
    UserResearchStudy(
        vector<Participant> participants_,
        vector<InterviewExcerpt> interviews_,
        vector<UsabilityResult> usabilityResults_,
        vector<SurveyResponse> surveyResponses_
    )
        : participants(move(participants_)),
          interviews(move(interviews_)),
          usabilityResults(move(usabilityResults_)),
          surveyResponses(move(surveyResponses_)) {}

    void validateData() const {
        printSubsection("Data Validation");

        int validParticipants = 0;

        for (const auto& participant : participants) {
            if (!participant.id.empty()) {
                ++validParticipants;
            }
        }

        cout << "Participants with valid IDs: "
             << validParticipants << "/" << participants.size() << "\n";

        int validSurveys = 0;

        for (const auto& response : surveyResponses) {
            string error;

            if (validateSurveyResponse(response, error)) {
                ++validSurveys;
            } else {
                cout << "Invalid survey " << response.id
                     << ": " << error << "\n";
            }
        }

        cout << "Valid survey responses: "
             << validSurveys << "/" << surveyResponses.size() << "\n";
    }

    void analyzeParticipants() const {
        printSubsection("Participant Screening");

        int eligible = 0;

        for (const auto& participant : participants) {
            if (isEligible(participant)) {
                ++eligible;

                cout << participant.id
                     << " | age=" << participant.age
                     << " | experience=" << toString(participant.experience)
                     << " | goal=" << participant.primaryGoal
                     << "\n";
            }
        }

        cout << "Eligible participants: "
             << eligible << "/" << participants.size() << "\n";
    }

    map<ResearchCode, int> codeFrequency() const {
        map<ResearchCode, int> frequency;

        for (const auto& interview : interviews) {
            const auto codes = codeInterview(interview);

            for (ResearchCode code : codes) {
                ++frequency[code];
            }
        }

        return frequency;
    }

    void analyzeQualitativeEvidence() const {
        printSubsection("Qualitative Coding");

        const auto frequency = codeFrequency();

        for (const auto& [code, count] : frequency) {
            cout << toString(code)
                 << ": " << count << " evidence item(s)\n";
        }
    }

    void analyzeUsability() const {
        printSubsection("Usability Metrics");

        vector<double> times;

        for (const auto& result : usabilityResults) {
            times.push_back(result.timeSeconds);
        }

        cout << fixed << setprecision(2);

        cout << "Task success rate: "
             << calculateSuccessRate(usabilityResults) * 100.0
             << "%\n";

        cout << "Mean task time: "
             << calculateMean(times)
             << " seconds\n";

        cout << "Mean errors: "
             << calculateAverageErrors(usabilityResults)
             << "\n";
    }

    void analyzeSurvey() const {
        printSubsection("Survey Metrics");

        vector<double> satisfaction;
        vector<double> ease;

        int uploadProblems = 0;
        int statusProblems = 0;

        for (const auto& response : surveyResponses) {
            satisfaction.push_back(response.satisfaction);
            ease.push_back(response.easeOfUse);

            if (response.uploadProblem) {
                ++uploadProblems;
            }

            if (response.statusProblem) {
                ++statusProblems;
            }
        }

        cout << fixed << setprecision(2);

        cout << "Mean satisfaction: "
             << calculateMean(satisfaction)
             << "/5\n";

        cout << "Mean ease of use: "
             << calculateMean(ease)
             << "/5\n";

        cout << "Upload problem rate: "
             << 100.0 * uploadProblems / surveyResponses.size()
             << "%\n";

        cout << "Status problem rate: "
             << 100.0 * statusProblems / surveyResponses.size()
             << "%\n";

        cout << "NPS: "
             << calculateNPS(surveyResponses)
             << "\n";
    }

    map<string, pair<int, int>> uploadProblemsByAgeGroup() const {
        map<string, pair<int, int>> table;

        for (const auto& response : surveyResponses) {
            auto& record = table[response.ageGroup];

            ++record.first;

            if (response.uploadProblem) {
                ++record.second;
            }
        }

        return table;
    }

    void analyzeCrossTabulation() const {
        printSubsection("Cross-Tabulation: Upload Problems by Age Group");

        const auto table = uploadProblemsByAgeGroup();

        for (const auto& [ageGroup, counts] : table) {
            const int total = counts.first;
            const int affected = counts.second;

            const double rate =
                total == 0
                    ? 0.0
                    : 100.0 * affected / total;

            cout << ageGroup
                 << " | n=" << total
                 << " | affected=" << affected
                 << " | rate=" << fixed << setprecision(1)
                 << rate << "%\n";
        }
    }

    void generateFindings() const {
        printSubsection("Evidence-Based Findings");

        const auto codes = codeFrequency();

        const auto missingFeedback =
            codes.find(ResearchCode::MissingSystemFeedback);

        const auto unclearStatus =
            codes.find(ResearchCode::UnclearStatusLanguage);

        cout << "Finding 1:\n";
        cout << "Multiple evidence sources indicate uncertainty around "
             << "the completion of file upload.\n";

        cout << "Finding 2:\n";

        if (unclearStatus != codes.end()) {
            cout << "Interview evidence indicates that status terminology "
                 << "may not match participant vocabulary.\n";
        } else {
            cout << "The current interview sample contains limited direct "
                 << "evidence about status terminology.\n";
        }

        cout << "Finding 3:\n";
        cout << "Usability observations should be interpreted alongside "
             << "survey frequency and qualitative explanations rather than "
             << "in isolation.\n";
    }

    void prioritizeIssues() const {
        printSubsection("Research Issue Prioritization");

        vector<ResearchIssue> issues = {
            {
                "Upload uncertainty",
                0.50,
                5.0,
                0.85
            },
            {
                "Status terminology",
                0.40,
                3.0,
                0.70
            },
            {
                "Navigation anxiety",
                0.20,
                4.0,
                0.55
            },
            {
                "Extra information request",
                0.30,
                2.0,
                0.60
            }
        };

        sort(
            issues.begin(),
            issues.end(),
            [](const ResearchIssue& a, const ResearchIssue& b) {
                return a.evidencePriority() > b.evidencePriority();
            }
        );

        for (const auto& issue : issues) {
            cout << issue.name
                 << " | frequency=" << issue.frequency
                 << " | severity=" << issue.severity
                 << " | confidence=" << issue.confidence
                 << " | heuristic="
                 << issue.evidencePriority()
                 << "\n";
        }

        cout << "\nThe ordering above is an analytical heuristic for this "
             << "case study, not a universal research standard.\n";
    }

    void discussLimitations() const {
        printSubsection("Study Limitations");

        const vector<string> limitations = {
            "The sample is small.",
            "The simulated sample may not represent the target population.",
            "Self-reported survey responses may contain recall or response bias.",
            "Observed usability behavior may differ from natural production behavior.",
            "The research environment may influence participant behavior.",
            "Cross-sectional evidence does not automatically establish causation.",
            "Qualitative themes depend on coding decisions and contextual interpretation."
        };

        for (const auto& limitation : limitations) {
            cout << "- " << limitation << "\n";
        }
    }

    void run() const {
        printSection("User Research Case Study");

        cout << "Scenario: An online public-service application "
             << "has reported workflow friction.\n";

        validateData();
        analyzeParticipants();
        analyzeQualitativeEvidence();
        analyzeUsability();
        analyzeSurvey();
        analyzeCrossTabulation();
        generateFindings();
        prioritizeIssues();
        discussLimitations();
    }
};


// -----------------------------------------------------------------------------
// 9. MAIN DATASET
// -----------------------------------------------------------------------------

vector<Participant> createParticipants() {
    return {
        {
            "P01",
            24,
            ExperienceLevel::Beginner,
            2,
            "submit application",
            true
        },
        {
            "P02",
            31,
            ExperienceLevel::Intermediate,
            8,
            "track request",
            true
        },
        {
            "P03",
            45,
            ExperienceLevel::Advanced,
            12,
            "submit application",
            true
        },
        {
            "P04",
            17,
            ExperienceLevel::Beginner,
            5,
            "submit application",
            false
        },
        {
            "P05",
            38,
            ExperienceLevel::Intermediate,
            4,
            "find information",
            true
        }
    };
}

vector<InterviewExcerpt> createInterviews() {
    return {
        {
            "P01",
            "submission",
            "I did not know which button would actually submit the request."
        },
        {
            "P02",
            "status",
            "The status page uses words that I do not normally use."
        },
        {
            "P03",
            "upload",
            "I expected the next step to be visible after I uploaded the document."
        },
        {
            "P05",
            "upload",
            "I kept checking whether the file had really been uploaded."
        },
        {
            "P01",
            "form",
            "The form asks for information I thought the organization already had."
        },
        {
            "P02",
            "navigation",
            "I was worried that going back would erase what I entered."
        }
    };
}

vector<UsabilityResult> createUsabilityResults() {
    return {
        {"P01", true, 145.0, 2, 4},
        {"P02", true, 102.0, 1, 4},
        {"P03", true, 88.0, 0, 5},
        {"P05", false, 240.0, 4, 2}
    };
}

vector<SurveyResponse> createSurveyResponses() {
    return {
        {"S01", "18-29", 3, 3, 6, true, true},
        {"S02", "30-44", 4, 4, 8, false, true},
        {"S03", "45-59", 2, 2, 4, true, true},
        {"S04", "30-44", 5, 5, 9, false, false},
        {"S05", "18-29", 3, 3, 7, true, false},
        {"S06", "45-59", 2, 2, 5, true, true},
        {"S07", "30-44", 4, 4, 8, false, true},
        {"S08", "60+", 3, 3, 6, true, true}
    };
}


// -----------------------------------------------------------------------------
// 10. RESEARCH REPOSITORY DEMONSTRATION
// -----------------------------------------------------------------------------

void demonstrateRepository() {
    printSection("Research Evidence Repository");

    ResearchRepository repository;

    repository.add({
        "INT-001",
        "interview",
        "Participant described uncertainty after upload.",
        "P01",
        {"upload", "feedback"}
    });

    repository.add({
        "UT-001",
        "usability",
        "Participant checked upload status twice.",
        "P01",
        {"upload", "behavior"}
    });

    repository.add({
        "SUR-001",
        "survey",
        "Participant reported an upload problem.",
        "S01",
        {"upload", "quantitative"}
    });

    cout << "Repository artifacts: "
         << repository.size()
         << "\n";

    cout << "Counts by type:\n";

    for (const auto& [type, count] : repository.countByType()) {
        cout << "  " << type << ": " << count << "\n";
    }

    cout << "Artifacts tagged 'upload':\n";

    for (const auto& artifact : repository.findByTag("upload")) {
        cout << "  " << artifact.id
             << ": " << artifact.content
             << "\n";
    }

    try {
        repository.add({
            "INT-001",
            "interview",
            "Duplicate artifact",
            nullopt,
            {"duplicate"}
        });
    } catch (const exception& error) {
        cout << "Handled expected repository error: "
             << error.what()
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// 11. SECURITY AND GOVERNANCE
// -----------------------------------------------------------------------------

void discussSecurityAndGovernance() {
    printSection("Security and Research Governance");

    const vector<pair<string, string>> controls = {
        {
            "Access control",
            "Restrict research data to authorized people."
        },
        {
            "Encryption",
            "Protect sensitive research data during storage and transmission."
        },
        {
            "Data minimization",
            "Collect only information necessary for the research purpose."
        },
        {
            "Pseudonymization",
            "Separate participant identity from analytical records where practical."
        },
        {
            "Retention",
            "Define how long research records should be retained."
        },
        {
            "Auditability",
            "Record important data-access and governance events."
        },
        {
            "Secure deletion",
            "Dispose of data according to applicable policy and obligations."
        }
    };

    for (const auto& [name, description] : controls) {
        cout << name << ": "
             << description
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// 12. MAIN
// -----------------------------------------------------------------------------

int main() {
    try {
        UserResearchStudy study(
            createParticipants(),
            createInterviews(),
            createUsabilityResults(),
            createSurveyResponses()
        );

        study.run();
        demonstrateRepository();
        discussSecurityAndGovernance();

        printSection("Case Study Complete");

        cout << "The program modeled an end-to-end research workflow from "
             << "participant screening and evidence collection through "
             << "qualitative coding, quantitative analysis, triangulation, "
             << "prioritization, governance, and reporting.\n";

        return 0;
    }
    catch (const exception& error) {
        cerr << "Fatal research-system error: "
             << error.what()
             << "\n";

        return 1;
    }
}
