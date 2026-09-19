/*
 * Jobs To Be Done (JTBD)
 * ======================
 *
 * C++17 case study:
 * "Study Progress Management Under Examination Time Pressure"
 *
 * The program models a realistic product-discovery scenario in which
 * researchers analyze how learners prepare for examinations.
 *
 * It demonstrates:
 *   - job definitions
 *   - functional, emotional, and social jobs
 *   - job stories
 *   - desired outcomes
 *   - opportunity scoring
 *   - interview evidence
 *   - evidence clustering
 *   - competing solutions
 *   - switching forces
 *   - job-map stages
 *   - validation
 *   - complexity considerations
 *   - modular C++ design
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic jtbd_case_study.cpp -o jtbd
 *
 * Run:
 *   ./jtbd
 */

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

void section(const string& title) {
    cout << "\n" << string(80, '=') << "\n";
    cout << title << "\n";
    cout << string(80, '=') << "\n";
}

void subsection(const string& title) {
    cout << "\n--- " << title << " ---\n";
}

string trim(const string& input) {
    const size_t first = input.find_first_not_of(" \t\n\r");
    if (first == string::npos) {
        return "";
    }

    const size_t last = input.find_last_not_of(" \t\n\r");
    return input.substr(first, last - first + 1);
}

void requireNonEmpty(const string& value, const string& fieldName) {
    if (trim(value).empty()) {
        throw invalid_argument(fieldName + " cannot be empty.");
    }
}

void requireRating(double value, const string& fieldName) {
    if (!isfinite(value) || value < 0.0 || value > 10.0) {
        throw invalid_argument(
            fieldName + " must be between 0 and 10."
        );
    }
}

// ---------------------------------------------------------------------------
// Job story
// ---------------------------------------------------------------------------

struct JobStory {
    string circumstance;
    string motivation;
    string outcome;

    void validate() const {
        requireNonEmpty(circumstance, "Circumstance");
        requireNonEmpty(motivation, "Motivation");
        requireNonEmpty(outcome, "Outcome");
    }

    string render() const {
        validate();

        return "When " + circumstance +
               ", I want to " + motivation +
               ", so I can " + outcome + ".";
    }
};

// ---------------------------------------------------------------------------
// Desired outcome
// ---------------------------------------------------------------------------

struct DesiredOutcome {
    string statement;
    double importance;
    double satisfaction;

    void validate() const {
        requireNonEmpty(statement, "Outcome statement");
        requireRating(importance, "Importance");
        requireRating(satisfaction, "Satisfaction");
    }

    double opportunityScore() const {
        validate();

        /*
         * Illustrative opportunity formula:
         *
         *   Importance + max(Importance - Satisfaction, 0)
         *
         * The formula is useful for demonstrating prioritization but is
         * not a substitute for the underlying research evidence.
         */
        return importance + max(importance - satisfaction, 0.0);
    }
};

// ---------------------------------------------------------------------------
// Primary JTBD model
// ---------------------------------------------------------------------------

class JobAnalysis {
private:
    string name_;
    string circumstance_;
    string functionalJob_;
    string emotionalJob_;
    string socialJob_;

    vector<DesiredOutcome> outcomes_;
    vector<string> alternatives_;
    vector<string> barriers_;

public:
    JobAnalysis(
        string name,
        string circumstance,
        string functionalJob,
        string emotionalJob,
        string socialJob,
        vector<DesiredOutcome> outcomes,
        vector<string> alternatives,
        vector<string> barriers
    )
        : name_(move(name)),
          circumstance_(move(circumstance)),
          functionalJob_(move(functionalJob)),
          emotionalJob_(move(emotionalJob)),
          socialJob_(move(socialJob)),
          outcomes_(move(outcomes)),
          alternatives_(move(alternatives)),
          barriers_(move(barriers)) {
        validate();
    }

    void validate() const {
        requireNonEmpty(name_, "Job name");
        requireNonEmpty(circumstance_, "Circumstance");
        requireNonEmpty(functionalJob_, "Functional job");
        requireNonEmpty(emotionalJob_, "Emotional job");
        requireNonEmpty(socialJob_, "Social job");

        for (const auto& outcome : outcomes_) {
            outcome.validate();
        }
    }

    double averageOpportunity() const {
        if (outcomes_.empty()) {
            return 0.0;
        }

        double total = 0.0;

        for (const auto& outcome : outcomes_) {
            total += outcome.opportunityScore();
        }

        return total / static_cast<double>(outcomes_.size());
    }

    optional<DesiredOutcome> highestOpportunity() const {
        if (outcomes_.empty()) {
            return nullopt;
        }

        auto iterator = max_element(
            outcomes_.begin(),
            outcomes_.end(),
            [](const DesiredOutcome& left, const DesiredOutcome& right) {
                return left.opportunityScore() <
                       right.opportunityScore();
            }
        );

        return *iterator;
    }

    void printReport() const {
        cout << "Job: " << name_ << "\n";
        cout << "Circumstance: " << circumstance_ << "\n";
        cout << "Functional job: " << functionalJob_ << "\n";
        cout << "Emotional job: " << emotionalJob_ << "\n";
        cout << "Social job: " << socialJob_ << "\n";

        cout << "Alternatives:\n";
        for (const auto& alternative : alternatives_) {
            cout << "  - " << alternative << "\n";
        }

        cout << "Barriers:\n";
        for (const auto& barrier : barriers_) {
            cout << "  - " << barrier << "\n";
        }

        cout << "Desired outcomes:\n";

        for (const auto& outcome : outcomes_) {
            cout << "  - " << outcome.statement
                 << " | importance=" << outcome.importance
                 << " | satisfaction=" << outcome.satisfaction
                 << " | opportunity=" << fixed << setprecision(1)
                 << outcome.opportunityScore()
                 << "\n";
        }

        cout << "Average opportunity: "
             << fixed << setprecision(2)
             << averageOpportunity()
             << "\n";
    }
};

// ---------------------------------------------------------------------------
// Interview evidence
// ---------------------------------------------------------------------------

struct InterviewEvidence {
    string participantId;
    string circumstance;
    string behavior;
    string previousSolution;
    string pain;
    string desiredResult;
};

void printInterview(const InterviewEvidence& interview) {
    cout << "\nParticipant: " << interview.participantId << "\n";
    cout << "  Circumstance: " << interview.circumstance << "\n";
    cout << "  Behavior: " << interview.behavior << "\n";
    cout << "  Previous solution: " << interview.previousSolution << "\n";
    cout << "  Pain: " << interview.pain << "\n";
    cout << "  Desired result: " << interview.desiredResult << "\n";
}

// ---------------------------------------------------------------------------
// Coded evidence
// ---------------------------------------------------------------------------

struct CodedEvidence {
    string participantId;
    string statement;
    string cluster;
};

map<string, vector<CodedEvidence>>
clusterEvidence(const vector<CodedEvidence>& evidence) {
    map<string, vector<CodedEvidence>> clusters;

    for (const auto& item : evidence) {
        clusters[item.cluster].push_back(item);
    }

    return clusters;
}

// ---------------------------------------------------------------------------
// Switching forces
// ---------------------------------------------------------------------------

struct SwitchingForces {
    string previousSolution;
    string newSolution;
    string trigger;
    string push;
    string pull;
    string anxiety;
    string habit;

    void print() const {
        cout << "Previous solution: " << previousSolution << "\n";
        cout << "New solution: " << newSolution << "\n";
        cout << "Trigger: " << trigger << "\n";
        cout << "Push: " << push << "\n";
        cout << "Pull: " << pull << "\n";
        cout << "Anxiety: " << anxiety << "\n";
        cout << "Habit: " << habit << "\n";
    }
};

// ---------------------------------------------------------------------------
// Competing solution
// ---------------------------------------------------------------------------

struct SolutionEvaluation {
    string name;

    /*
     * All values are rated from 1 to 10.
     * Higher effort is undesirable, so score() inverts it.
     */
    int speed;
    int effort;
    int confidence;
    int flexibility;

    void validate() const {
        const vector<pair<string, int>> values = {
            {"speed", speed},
            {"effort", effort},
            {"confidence", confidence},
            {"flexibility", flexibility}
        };

        for (const auto& [field, value] : values) {
            if (value < 1 || value > 10) {
                throw invalid_argument(
                    field + " must be between 1 and 10."
                );
            }
        }
    }

    double score() const {
        validate();

        return (
            static_cast<double>(speed) +
            static_cast<double>(11 - effort) +
            static_cast<double>(confidence) +
            static_cast<double>(flexibility)
        ) / 4.0;
    }
};

// ---------------------------------------------------------------------------
// Job map
// ---------------------------------------------------------------------------

struct JobMapStage {
    string name;
    string description;
};

// ---------------------------------------------------------------------------
// Research repository
// ---------------------------------------------------------------------------

class ResearchRepository {
private:
    vector<InterviewEvidence> interviews_;
    vector<CodedEvidence> codedEvidence_;

public:
    void addInterview(InterviewEvidence interview) {
        requireNonEmpty(interview.participantId, "Participant ID");
        requireNonEmpty(interview.circumstance, "Interview circumstance");
        requireNonEmpty(interview.behavior, "Interview behavior");
        interviews_.push_back(move(interview));
    }

    void addCodedEvidence(CodedEvidence evidence) {
        requireNonEmpty(evidence.participantId, "Participant ID");
        requireNonEmpty(evidence.statement, "Evidence statement");
        requireNonEmpty(evidence.cluster, "Evidence cluster");
        codedEvidence_.push_back(move(evidence));
    }

    const vector<InterviewEvidence>& interviews() const {
        return interviews_;
    }

    const vector<CodedEvidence>& codedEvidence() const {
        return codedEvidence_;
    }

    size_t interviewCount() const {
        return interviews_.size();
    }
};

// ---------------------------------------------------------------------------
// Product-discovery analysis service
// ---------------------------------------------------------------------------

class JTBDAnalysisService {
public:
    static vector<DesiredOutcome>
    sortByOpportunity(vector<DesiredOutcome> outcomes) {
        sort(
            outcomes.begin(),
            outcomes.end(),
            [](const DesiredOutcome& left, const DesiredOutcome& right) {
                return left.opportunityScore() >
                       right.opportunityScore();
            }
        );

        return outcomes;
    }

    static set<string>
    identifyPreviousSolutions(
        const vector<InterviewEvidence>& interviews
    ) {
        set<string> solutions;

        for (const auto& interview : interviews) {
            if (!trim(interview.previousSolution).empty()) {
                solutions.insert(interview.previousSolution);
            }
        }

        return solutions;
    }
};

// ---------------------------------------------------------------------------
// Interactive input helper
// ---------------------------------------------------------------------------

int readBoundedInteger(
    const string& prompt,
    int minimum,
    int maximum
) {
    while (true) {
        cout << prompt;

        int value;

        if (cin >> value && value >= minimum && value <= maximum) {
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return value;
        }

        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        cout << "Enter a number from "
             << minimum << " to "
             << maximum << ".\n";
    }
}

// ---------------------------------------------------------------------------
// Main case study
// ---------------------------------------------------------------------------

int main() {
    try {
        section("JOBS TO BE DONE CASE STUDY");

        cout << R"(
Scenario
--------
A product team is investigating how learners prepare for important
examinations.

The team is considering a study-planning system. Instead of starting
with a list of desired features, the analysis begins with the job the
learner is trying to accomplish.

Primary job:
    Prepare effectively for an important examination when time is limited.

This scenario is intentionally broader than a specific product feature.
A notebook, spreadsheet, textbook, calendar, peer, or software application
may all participate in accomplishing the same job.
)";

        // ------------------------------------------------------------------
        // Basic job story
        // ------------------------------------------------------------------

        section("1. JOB STORY");

        JobStory studyStory{
            "I have several subjects to revise before an examination",
            "identify the topics that require the most attention",
            "allocate my limited study time effectively"
        };

        cout << studyStory.render() << "\n";

        // ------------------------------------------------------------------
        // Functional, emotional, and social jobs
        // ------------------------------------------------------------------

        section("2. JOB DIMENSIONS");

        cout << "Functional job:\n"
             << "  Determine what to study, in what order, and whether\n"
             << "  preparation is sufficient.\n\n";

        cout << "Emotional job:\n"
             << "  Reduce uncertainty and feel in control of preparation.\n\n";

        cout << "Social job:\n"
             << "  Demonstrate reliable preparation when discussing progress.\n";

        // ------------------------------------------------------------------
        // Desired outcomes
        // ------------------------------------------------------------------

        section("3. DESIRED OUTCOMES");

        vector<DesiredOutcome> outcomes{
            {
                "Minimize the time needed to identify high-priority topics.",
                10.0,
                3.0
            },
            {
                "Minimize the likelihood of overlooking an important topic.",
                10.0,
                4.0
            },
            {
                "Increase confidence that preparation is sufficient.",
                9.0,
                5.0
            },
            {
                "Minimize effort required to update the study plan.",
                7.0,
                6.0
            },
            {
                "Increase the likelihood of remembering difficult concepts.",
                9.0,
                3.0
            }
        };

        for (const auto& outcome : outcomes) {
            cout << outcome.statement
                 << "\n  Importance: " << outcome.importance
                 << "\n  Satisfaction: " << outcome.satisfaction
                 << "\n  Opportunity: " << outcome.opportunityScore()
                 << "\n\n";
        }

        // ------------------------------------------------------------------
        // Job analysis
        // ------------------------------------------------------------------

        section("4. COMPLETE JTBD ANALYSIS");

        JobAnalysis analysis(
            "Study planning under examination time pressure",
            "A learner has several subjects, limited time, and an upcoming assessment.",
            "Determine what to study, in what order, and whether preparation is sufficient.",
            "Reduce uncertainty and feel in control of preparation.",
            "Appear prepared and dependable when discussing academic progress.",
            outcomes,
            {
                "Notebook",
                "Spreadsheet",
                "Calendar",
                "Textbook",
                "Peer advice"
            },
            {
                "Poor information organization",
                "Changing deadlines",
                "Limited time",
                "Unclear priorities"
            }
        );

        analysis.printReport();

        // ------------------------------------------------------------------
        // Interview evidence
        // ------------------------------------------------------------------

        section("5. INTERVIEW EVIDENCE");

        ResearchRepository repository;

        repository.addInterview({
            "P01",
            "An examination was two weeks away.",
            "Created a spreadsheet of topics and marked weak areas.",
            "Spreadsheet",
            "Maintaining the list became tedious.",
            "Know which topics deserve attention first."
        });

        repository.addInterview({
            "P02",
            "Several assignments were due in one week.",
            "Used calendar reminders and handwritten notes.",
            "Calendar and notebook",
            "Information was scattered.",
            "See priorities in one place."
        });

        repository.addInterview({
            "P03",
            "A difficult subject contained many formulas.",
            "Solved practice problems repeatedly.",
            "Textbook and notebook",
            "It was difficult to determine which concepts remained weak.",
            "Obtain evidence of readiness."
        });

        for (const auto& interview : repository.interviews()) {
            printInterview(interview);
        }

        // ------------------------------------------------------------------
        // Previous solutions
        // ------------------------------------------------------------------

        section("6. PREVIOUS AND COMPETING SOLUTIONS");

        const auto solutions =
            JTBDAnalysisService::identifyPreviousSolutions(
                repository.interviews()
            );

        for (const auto& solution : solutions) {
            cout << "- " << solution << "\n";
        }

        cout << R"(
JTBD competition is not restricted to direct commercial competitors.

A manual process can compete with software.
A spreadsheet can compete with a specialized application.
Memory can compete with a reminder system.
A person can compete with an automated workflow.

The relevant comparison is how effectively each approach helps the person
make progress under the specific circumstance.
)";

        // ------------------------------------------------------------------
        // Switching forces
        // ------------------------------------------------------------------

        section("7. SWITCHING FORCES");

        SwitchingForces switching{
            "Spreadsheet",
            "Specialized study-planning system",
            "Manual planning became difficult as the number of subjects increased.",
            "Maintaining and updating the spreadsheet consumed too much time.",
            "Automatic prioritization could reduce manual work.",
            "The learner was concerned that an automated priority system might be wrong.",
            "The spreadsheet was familiar and already contained historical information."
        };

        switching.print();

        // ------------------------------------------------------------------
        // Coded evidence
        // ------------------------------------------------------------------

        section("8. QUALITATIVE EVIDENCE CLUSTERING");

        repository.addCodedEvidence({
            "P01",
            "Identify weak chapters.",
            "Prioritize knowledge gaps"
        });

        repository.addCodedEvidence({
            "P02",
            "Know what to revise first.",
            "Prioritize knowledge gaps"
        });

        repository.addCodedEvidence({
            "P03",
            "Avoid guessing what matters.",
            "Prioritize knowledge gaps"
        });

        repository.addCodedEvidence({
            "P04",
            "Track assignment deadlines.",
            "Manage commitments"
        });

        repository.addCodedEvidence({
            "P05",
            "Know which assignment comes first.",
            "Manage commitments"
        });

        const clusters =
            clusterEvidence(repository.codedEvidence());

        for (const auto& [clusterName, items] : clusters) {
            cout << "\nCluster: " << clusterName << "\n";

            for (const auto& item : items) {
                cout << "  " << item.participantId
                     << ": " << item.statement << "\n";
            }
        }

        // ------------------------------------------------------------------
        // Job map
        // ------------------------------------------------------------------

        section("9. JOB MAP");

        vector<JobMapStage> jobMap{
            {"Define", "Clarify what must be achieved."},
            {"Locate", "Find relevant study material."},
            {"Prepare", "Arrange material, schedule, and conditions."},
            {"Confirm", "Check whether the selected study approach is appropriate."},
            {"Execute", "Perform study and practice activities."},
            {"Monitor", "Observe progress and remaining knowledge gaps."},
            {"Modify", "Change the plan when new information appears."},
            {"Conclude", "Determine whether readiness is sufficient."}
        };

        for (const auto& stage : jobMap) {
            cout << left << setw(12)
                 << stage.name
                 << ": "
                 << stage.description
                 << "\n";
        }

        // ------------------------------------------------------------------
        // Solution comparison
        // ------------------------------------------------------------------

        section("10. COMPETING SOLUTION ANALYSIS");

        vector<SolutionEvaluation> solutionEvaluations{
            {"Notebook", 5, 4, 6, 9},
            {"Spreadsheet", 7, 6, 8, 8},
            {"Specialized application", 9, 3, 8, 7},
            {"Memory", 10, 1, 3, 4}
        };

        sort(
            solutionEvaluations.begin(),
            solutionEvaluations.end(),
            [](const SolutionEvaluation& left,
               const SolutionEvaluation& right) {
                return left.score() > right.score();
            }
        );

        cout << fixed << setprecision(2);

        for (const auto& solution : solutionEvaluations) {
            cout << setw(28)
                 << left
                 << solution.name
                 << "illustrative score="
                 << solution.score()
                 << "\n";
        }

        cout << R"(
The score above is deliberately illustrative. A real research program
should define dimensions and weights from the actual job and evidence.
A numerical comparison should not be treated as an objective universal
ranking of solutions.
)";

        // ------------------------------------------------------------------
        // Prioritized outcomes
        // ------------------------------------------------------------------

        section("11. PRIORITIZED OUTCOMES");

        const auto prioritized =
            JTBDAnalysisService::sortByOpportunity(outcomes);

        for (size_t index = 0; index < prioritized.size(); ++index) {
            cout << index + 1
                 << ". "
                 << prioritized[index].statement
                 << " | opportunity="
                 << prioritized[index].opportunityScore()
                 << "\n";
        }

        // ------------------------------------------------------------------
        // Highest opportunity
        // ------------------------------------------------------------------

        section("12. HIGHEST OPPORTUNITY");

        const auto highest = analysis.highestOpportunity();

        if (highest.has_value()) {
            cout << "Outcome:\n"
                 << "  " << highest->statement << "\n"
                 << "Opportunity score: "
                 << highest->opportunityScore()
                 << "\n";
        } else {
            cout << "No desired outcomes were supplied.\n";
        }

        // ------------------------------------------------------------------
        // Edge-case validation
        // ------------------------------------------------------------------

        section("13. EDGE CASES");

        try {
            DesiredOutcome invalid{
                "Invalid importance",
                12.0,
                5.0
            };

            cout << invalid.opportunityScore() << "\n";
        } catch (const exception& error) {
            cout << "Caught invalid rating: "
                 << error.what()
                 << "\n";
        }

        try {
            JobStory invalidStory{
                "",
                "prioritize work",
                "use time effectively"
            };

            cout << invalidStory.render() << "\n";
        } catch (const exception& error) {
            cout << "Caught invalid job story: "
                 << error.what()
                 << "\n";
        }

        // ------------------------------------------------------------------
        // Complexity analysis
        // ------------------------------------------------------------------

        section("14. ALGORITHMIC COMPLEXITY");

        cout << R"(
For k desired outcomes:

    opportunityScore() for one outcome: O(1)
    averageOpportunity():               O(k)
    highestOpportunity():               O(k)
    sorting outcomes:                   O(k log k)

For n evidence records:

    grouping by an ordered std::map:    O(n log g)
    where g is the number of clusters

For this educational case study, the data sizes are small. In a production
research system, the more important engineering issues would often be
data quality, persistence, access control, auditability, and research
governance rather than raw CPU performance.
)";

        // ------------------------------------------------------------------
        // Architecture discussion
        // ------------------------------------------------------------------

        section("15. ARCHITECTURE");

        cout << R"(
The case study separates responsibilities into several components:

    JobStory
        Represents circumstance, motivation, and desired outcome.

    DesiredOutcome
        Validates importance and satisfaction and calculates opportunity.

    JobAnalysis
        Represents a complete JTBD analysis.

    InterviewEvidence
        Stores structured evidence from a research event.

    ResearchRepository
        Stores interview and coded evidence.

    JTBDAnalysisService
        Performs reusable analytical operations.

    SolutionEvaluation
        Models alternative approaches to the same job.

This separation reduces coupling and makes the analysis easier to test,
extend, and integrate into a larger application.
)";

        // ------------------------------------------------------------------
        // Security and privacy
        // ------------------------------------------------------------------

        section("16. SECURITY AND PRIVACY");

        cout << R"(
JTBD research can contain sensitive personal and behavioral information.

A production system should consider:

    - informed consent
    - data minimization
    - access control
    - encryption
    - secure storage
    - retention policies
    - removal of unnecessary identifiers
    - audit logs
    - controlled transcript access
    - separation of research identifiers from personal identity

The data model should collect only information required to answer the
research question.
)";

        // ------------------------------------------------------------------
        // Self-tests
        // ------------------------------------------------------------------

        section("17. SELF-TESTS");

        {
            DesiredOutcome testOutcome{
                "Test outcome",
                8.0,
                3.0
            };

            const double expected = 13.0;
            const double actual = testOutcome.opportunityScore();

            if (fabs(actual - expected) > 1e-9) {
                throw runtime_error(
                    "Opportunity calculation test failed."
                );
            }
        }

        {
            JobStory testStory{
                "a deadline is approaching",
                "prioritize important work",
                "use limited time effectively"
            };

            const string rendered = testStory.render();

            if (rendered.find("When") == string::npos ||
                rendered.find("so I can") == string::npos) {
                throw runtime_error(
                    "Job story rendering test failed."
                );
            }
        }

        {
            try {
                DesiredOutcome invalid{
                    "Invalid",
                    -1.0,
                    4.0
                };

                invalid.opportunityScore();

                throw runtime_error(
                    "Invalid rating should have caused an exception."
                );
            } catch (const invalid_argument&) {
                // Expected failure.
            }
        }

        cout << "All C++ self-tests passed.\n";

        // ------------------------------------------------------------------
        // Optional interactive component
        // ------------------------------------------------------------------

        section("18. INTERACTIVE OUTCOME EXAMPLE");

        cout << R"(
Enter an importance and satisfaction rating to calculate an illustrative
opportunity score. The values use a 1-10 scale.

This small interaction demonstrates validation and input handling without
requiring external libraries.
)";

        const int importance = readBoundedInteger(
            "Importance (1-10): ",
            1,
            10
        );

        const int satisfaction = readBoundedInteger(
            "Satisfaction (1-10): ",
            1,
            10
        );

        DesiredOutcome interactiveOutcome{
            "User-supplied illustrative outcome",
            static_cast<double>(importance),
            static_cast<double>(satisfaction)
        };

        cout << "Opportunity score: "
             << interactiveOutcome.opportunityScore()
             << "\n";

        // ------------------------------------------------------------------
        // Complete workflow
        // ------------------------------------------------------------------

        section("19. COMPLETE JTBD WORKFLOW");

        const vector<string> workflow{
            "Identify a meaningful circumstance.",
            "Investigate a real event and actual behavior.",
            "Describe the progress the person was trying to make.",
            "Separate the job from the current solution.",
            "Identify functional, emotional, and social dimensions.",
            "Examine previous solutions and workarounds.",
            "Identify switching triggers and barriers.",
            "Extract desired outcomes.",
            "Cluster recurring evidence.",
            "Validate the job against research evidence.",
            "Prioritize important outcomes using appropriate evidence.",
            "Design solutions against the job rather than assuming a feature is the job."
        };

        for (size_t index = 0; index < workflow.size(); ++index) {
            cout << index + 1
                 << ". "
                 << workflow[index]
                 << "\n";
        }

        section("20. KEY ANALYTICAL QUESTION");

        cout << R"(
What progress is the person trying to make, under what circumstances,
and what evidence shows that current ways of making that progress are
insufficient?

The answer should come from research evidence rather than from a
premature feature list.
)";

        return 0;
    }
    catch (const exception& error) {
        cerr << "\nFatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
