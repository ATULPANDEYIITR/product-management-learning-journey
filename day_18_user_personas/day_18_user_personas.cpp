/*
 * USER PERSONAS
 *
 * C++17 industry-style case study:
 *
 * Scenario:
 * A digital learning platform wants to understand recurring user segments
 * before designing new product workflows.
 *
 * The program models:
 * - Demographics
 * - Behaviors
 * - Goals
 * - Frustrations
 * - Jobs-to-be-Done
 * - Motivations
 * - Research evidence
 * - Segmentation
 * - Persona synthesis
 * - Feature relevance
 * - Validation
 * - Scenario analysis
 * - Complexity considerations
 *
 * Compile:
 *   g++ -std=c++17 -O2 user_personas.cpp -o user_personas
 */

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <vector>

using namespace std;


// ---------------------------------------------------------------------------
// 1. ENUMERATIONS
// ---------------------------------------------------------------------------

enum class JobType {
    Functional,
    Emotional,
    Social
};

enum class MotivationCategory {
    Autonomy,
    Mastery,
    Belonging,
    Security,
    Status,
    Convenience,
    Achievement,
    Curiosity,
    Savings
};

enum class EvidenceLevel {
    Observed,
    Reported,
    Inferred,
    Assumed
};


// ---------------------------------------------------------------------------
// 2. ENUMERATION HELPERS
// ---------------------------------------------------------------------------

string toString(JobType type) {
    switch (type) {
        case JobType::Functional:
            return "functional";
        case JobType::Emotional:
            return "emotional";
        case JobType::Social:
            return "social";
    }

    return "unknown";
}

string toString(MotivationCategory category) {
    switch (category) {
        case MotivationCategory::Autonomy:
            return "autonomy";
        case MotivationCategory::Mastery:
            return "mastery";
        case MotivationCategory::Belonging:
            return "belonging";
        case MotivationCategory::Security:
            return "security";
        case MotivationCategory::Status:
            return "status";
        case MotivationCategory::Convenience:
            return "convenience";
        case MotivationCategory::Achievement:
            return "achievement";
        case MotivationCategory::Curiosity:
            return "curiosity";
        case MotivationCategory::Savings:
            return "savings";
    }

    return "unknown";
}

string toString(EvidenceLevel level) {
    switch (level) {
        case EvidenceLevel::Observed:
            return "observed";
        case EvidenceLevel::Reported:
            return "reported";
        case EvidenceLevel::Inferred:
            return "inferred";
        case EvidenceLevel::Assumed:
            return "assumed";
    }

    return "unknown";
}


// ---------------------------------------------------------------------------
// 3. EVIDENCE
// ---------------------------------------------------------------------------

struct Evidence {
    string source;
    string statement;
    EvidenceLevel level;
    int sampleSize = 0;

    double qualityScore() const {
        switch (level) {
            case EvidenceLevel::Observed:
                return 1.00;
            case EvidenceLevel::Reported:
                return 0.85;
            case EvidenceLevel::Inferred:
                return 0.55;
            case EvidenceLevel::Assumed:
                return 0.20;
        }

        return 0.0;
    }
};


// ---------------------------------------------------------------------------
// 4. JOB-TO-BE-DONE
// ---------------------------------------------------------------------------

struct Job {
    string description;
    JobType type;
    int importance;
    int frequency;

    bool valid() const {
        return !description.empty()
            && importance >= 1
            && importance <= 10
            && frequency >= 1
            && frequency <= 10;
    }

    double priority() const {
        return static_cast<double>(importance) * frequency;
    }
};


// ---------------------------------------------------------------------------
// 5. FRUSTRATION
// ---------------------------------------------------------------------------

struct Frustration {
    string description;
    int severity;
    int frequency;
    string workaround;

    double impact() const {
        return static_cast<double>(severity) * frequency;
    }
};


// ---------------------------------------------------------------------------
// 6. MOTIVATION
// ---------------------------------------------------------------------------

struct Motivation {
    MotivationCategory category;
    string description;
    int strength;

    double normalizedStrength() const {
        const int bounded = max(0, min(10, strength));
        return bounded / 10.0;
    }
};


// ---------------------------------------------------------------------------
// 7. RAW RESEARCH OBSERVATION
// ---------------------------------------------------------------------------

struct UserObservation {
    string userId;
    set<string> behaviors;
    set<string> goals;
    set<string> frustrations;
    int technologyComfort;
    int priceSensitivity;
};


// ---------------------------------------------------------------------------
// 8. PERSONA
// ---------------------------------------------------------------------------

struct Persona {
    string name;
    string archetype;
    string description;

    string ageRange;
    string location;
    string occupation;
    string education;

    vector<string> behaviors;
    vector<string> goals;
    vector<Frustration> frustrations;
    vector<Job> jobs;
    vector<Motivation> motivations;
    vector<Evidence> evidence;

    int technologyComfort = 5;
    int priceSensitivity = 5;

    vector<string> validate() const {
        vector<string> errors;

        if (name.empty()) {
            errors.push_back("Persona name is required.");
        }

        if (archetype.empty()) {
            errors.push_back("Persona archetype is required.");
        }

        if (behaviors.empty()) {
            errors.push_back("At least one behavior is required.");
        }

        if (goals.empty()) {
            errors.push_back("At least one goal is required.");
        }

        if (jobs.empty()) {
            errors.push_back("At least one job is required.");
        }

        if (technologyComfort < 1 || technologyComfort > 10) {
            errors.push_back(
                "Technology comfort must be between 1 and 10."
            );
        }

        if (priceSensitivity < 1 || priceSensitivity > 10) {
            errors.push_back(
                "Price sensitivity must be between 1 and 10."
            );
        }

        for (const Job& job : jobs) {
            if (!job.valid()) {
                errors.push_back("Invalid job detected.");
            }
        }

        return errors;
    }

    double frustrationImpact() const {
        double total = 0;

        for (const Frustration& frustration : frustrations) {
            total += frustration.impact();
        }

        return total;
    }

    double jobPriority() const {
        double total = 0;

        for (const Job& job : jobs) {
            total += job.priority();
        }

        return total;
    }

    double motivationStrength() const {
        if (motivations.empty()) {
            return 0;
        }

        double total = 0;

        for (const Motivation& motivation : motivations) {
            total += motivation.normalizedStrength();
        }

        return total / motivations.size();
    }

    double evidenceStrength() const {
        if (evidence.empty()) {
            return 0;
        }

        double total = 0;

        for (const Evidence& item : evidence) {
            total += item.qualityScore();
        }

        return total / evidence.size();
    }
};


// ---------------------------------------------------------------------------
// 9. FEATURE MODEL
// ---------------------------------------------------------------------------

struct ProductFeature {
    string name;
    vector<string> solves;
};


// ---------------------------------------------------------------------------
// 10. FREQUENCY TABLE
// ---------------------------------------------------------------------------

map<string, int> frequencyTable(
    const vector<UserObservation>& records,
    char dimension
) {
    map<string, int> frequency;

    for (const auto& record : records) {
        const set<string>* values = nullptr;

        if (dimension == 'b') {
            values = &record.behaviors;
        } else if (dimension == 'g') {
            values = &record.goals;
        } else if (dimension == 'f') {
            values = &record.frustrations;
        }

        if (values == nullptr) {
            continue;
        }

        for (const string& value : *values) {
            ++frequency[value];
        }
    }

    return frequency;
}


// ---------------------------------------------------------------------------
// 11. RESEARCH SUMMARY
// ---------------------------------------------------------------------------

struct ResearchSummary {
    int userCount = 0;
    map<string, int> behaviors;
    map<string, int> goals;
    map<string, int> frustrations;
    double averageTechnologyComfort = 0;
    double averagePriceSensitivity = 0;
};

ResearchSummary aggregateResearch(
    const vector<UserObservation>& records
) {
    ResearchSummary summary;

    summary.userCount = static_cast<int>(records.size());

    if (records.empty()) {
        return summary;
    }

    summary.behaviors = frequencyTable(records, 'b');
    summary.goals = frequencyTable(records, 'g');
    summary.frustrations = frequencyTable(records, 'f');

    int technologyTotal = 0;
    int priceTotal = 0;

    for (const auto& record : records) {
        technologyTotal += record.technologyComfort;
        priceTotal += record.priceSensitivity;
    }

    summary.averageTechnologyComfort =
        static_cast<double>(technologyTotal) / records.size();

    summary.averagePriceSensitivity =
        static_cast<double>(priceTotal) / records.size();

    return summary;
}


// ---------------------------------------------------------------------------
// 12. MAP PRINTING
// ---------------------------------------------------------------------------

void printFrequencyTable(
    const string& title,
    const map<string, int>& frequency
) {
    cout << "\n" << title << "\n";

    vector<pair<string, int>> values(
        frequency.begin(),
        frequency.end()
    );

    sort(
        values.begin(),
        values.end(),
        [](const auto& first, const auto& second) {
            if (first.second != second.second) {
                return first.second > second.second;
            }

            return first.first < second.first;
        }
    );

    for (const auto& [key, value] : values) {
        cout << "  " << key << ": " << value << "\n";
    }
}


// ---------------------------------------------------------------------------
// 13. BEHAVIORAL SEGMENTATION
// ---------------------------------------------------------------------------

string assignSegment(const UserObservation& observation) {
    /*
     * This transparent rule is deliberately simple.
     *
     * A production organization may use clustering or other statistical
     * techniques, but mathematical clustering does not automatically create
     * a meaningful persona. Human interpretation and validation remain
     * important.
     */

    if (
        observation.goals.count("decision") > 0 ||
        observation.behaviors.count("dashboard") > 0
    ) {
        return "decision_oriented";
    }

    if (observation.goals.count("learn") > 0) {
        return "learning_oriented";
    }

    return "other";
}


// ---------------------------------------------------------------------------
// 14. PERSONA SYNTHESIS
// ---------------------------------------------------------------------------

Persona synthesizePersona(
    const string& name,
    const string& archetype,
    const vector<UserObservation>& records
) {
    if (records.empty()) {
        throw invalid_argument(
            "At least one research observation is required."
        );
    }

    const ResearchSummary summary =
        aggregateResearch(records);

    Persona persona;

    persona.name = name;
    persona.archetype = archetype;
    persona.description =
        "Research-derived behavioral segment.";

    /*
     * Demographics are intentionally not invented here.
     * The synthesis algorithm uses only behavioral evidence.
     */

    for (const auto& [behavior, count] : summary.behaviors) {
        if (count >= static_cast<int>(records.size() / 2)) {
            persona.behaviors.push_back(behavior);
        }
    }

    for (const auto& [goal, count] : summary.goals) {
        if (count >= static_cast<int>(records.size() / 2)) {
            persona.goals.push_back(goal);
        }
    }

    for (const auto& [frustration, count] : summary.frustrations) {
        Frustration item;

        item.description = frustration;
        item.severity = min(10, count * 3);
        item.frequency = min(10, count * 3);

        persona.frustrations.push_back(item);
    }

    persona.jobs.push_back({
        "Complete recurring tasks represented in research.",
        JobType::Functional,
        8,
        7
    });

    persona.motivations.push_back({
        MotivationCategory::Convenience,
        "Reduce friction in recurring work.",
        7
    });

    persona.evidence.push_back({
        "Aggregated research observations",
        "This persona was synthesized from recorded user observations.",
        EvidenceLevel::Observed,
        static_cast<int>(records.size())
    });

    persona.technologyComfort =
        static_cast<int>(
            round(summary.averageTechnologyComfort)
        );

    persona.priceSensitivity =
        static_cast<int>(
            round(summary.averagePriceSensitivity)
        );

    return persona;
}


// ---------------------------------------------------------------------------
// 15. PERSONA REPORT
// ---------------------------------------------------------------------------

void printPersona(const Persona& persona) {
    cout << "\n========================================\n";
    cout << "PERSONA: " << persona.name << "\n";
    cout << "Archetype: " << persona.archetype << "\n";
    cout << "Description: " << persona.description << "\n";

    cout << "\nDemographics\n";
    cout << "  Age: "
         << (persona.ageRange.empty()
             ? "Not specified"
             : persona.ageRange)
         << "\n";

    cout << "  Location: "
         << (persona.location.empty()
             ? "Not specified"
             : persona.location)
         << "\n";

    cout << "  Occupation: "
         << (persona.occupation.empty()
             ? "Not specified"
             : persona.occupation)
         << "\n";

    cout << "\nBehaviors\n";

    for (const string& behavior : persona.behaviors) {
        cout << "  - " << behavior << "\n";
    }

    cout << "\nGoals\n";

    for (const string& goal : persona.goals) {
        cout << "  - " << goal << "\n";
    }

    cout << "\nFrustrations\n";

    for (const Frustration& frustration : persona.frustrations) {
        cout << "  - " << frustration.description
             << " | severity=" << frustration.severity
             << " | frequency=" << frustration.frequency
             << " | impact=" << frustration.impact()
             << "\n";
    }

    cout << "\nJobs\n";

    for (const Job& job : persona.jobs) {
        cout << "  - [" << toString(job.type) << "] "
             << job.description
             << " | priority=" << job.priority()
             << "\n";
    }

    cout << "\nMotivations\n";

    for (const Motivation& motivation : persona.motivations) {
        cout << "  - [" << toString(motivation.category) << "] "
             << motivation.description
             << " | strength=" << motivation.strength
             << "/10\n";
    }

    cout << "\nEvidence strength: "
         << fixed << setprecision(3)
         << persona.evidenceStrength()
         << "\n";
}


// ---------------------------------------------------------------------------
// 16. FEATURE RELEVANCE
// ---------------------------------------------------------------------------

string lowerCopy(string text) {
    transform(
        text.begin(),
        text.end(),
        text.begin(),
        [](unsigned char character) {
            return static_cast<char>(
                tolower(character)
            );
        }
    );

    return text;
}

bool containsIgnoreCase(
    const string& text,
    const string& pattern
) {
    return lowerCopy(text).find(lowerCopy(pattern))
        != string::npos;
}

string personaSearchText(const Persona& persona) {
    ostringstream output;

    for (const string& behavior : persona.behaviors) {
        output << behavior << " ";
    }

    for (const string& goal : persona.goals) {
        output << goal << " ";
    }

    for (const Frustration& frustration : persona.frustrations) {
        output << frustration.description << " ";
    }

    for (const Job& job : persona.jobs) {
        output << job.description << " ";
    }

    return output.str();
}

double featureRelevance(
    const Persona& persona,
    const ProductFeature& feature
) {
    if (feature.solves.empty()) {
        return 0;
    }

    const string text = personaSearchText(persona);

    int matches = 0;

    for (const string& solution : feature.solves) {
        if (containsIgnoreCase(text, solution)) {
            ++matches;
        }
    }

    return static_cast<double>(matches)
        / feature.solves.size();
}


// ---------------------------------------------------------------------------
// 17. PERSONA QUALITY REPORT
// ---------------------------------------------------------------------------

struct QualityReport {
    bool validStructure;
    vector<string> errors;
    double evidenceStrength;
    size_t behaviorCount;
    size_t goalCount;
    size_t frustrationCount;
    size_t jobCount;
    size_t motivationCount;
};

QualityReport analyzeQuality(const Persona& persona) {
    const vector<string> errors = persona.validate();

    return {
        errors.empty(),
        errors,
        persona.evidenceStrength(),
        persona.behaviors.size(),
        persona.goals.size(),
        persona.frustrations.size(),
        persona.jobs.size(),
        persona.motivations.size()
    };
}

void printQualityReport(const QualityReport& report) {
    cout << "\nQUALITY REPORT\n";

    cout << "  Valid structure: "
         << (report.validStructure ? "yes" : "no")
         << "\n";

    cout << "  Evidence strength: "
         << fixed << setprecision(3)
         << report.evidenceStrength
         << "\n";

    cout << "  Behaviors: "
         << report.behaviorCount
         << "\n";

    cout << "  Goals: "
         << report.goalCount
         << "\n";

    cout << "  Frustrations: "
         << report.frustrationCount
         << "\n";

    cout << "  Jobs: "
         << report.jobCount
         << "\n";

    cout << "  Motivations: "
         << report.motivationCount
         << "\n";

    if (!report.errors.empty()) {
        cout << "  Errors:\n";

        for (const string& error : report.errors) {
            cout << "    - " << error << "\n";
        }
    }
}


// ---------------------------------------------------------------------------
// 18. CASE STUDY DATA
// ---------------------------------------------------------------------------

vector<UserObservation> learningResearch = {
    {
        "L001",
        {"search", "compare", "practice"},
        {"learn", "career"},
        {"time", "unclear_instructions"},
        9,
        8
    },
    {
        "L002",
        {"search", "practice", "documentation"},
        {"learn", "complete_task"},
        {"complexity"},
        8,
        9
    },
    {
        "L003",
        {"search", "compare", "practice"},
        {"learn", "career"},
        {"complexity"},
        9,
        7
    },
    {
        "L004",
        {"search", "documentation", "practice"},
        {"learn", "complete_task"},
        {"unclear_instructions"},
        8,
        8
    },
    {
        "L005",
        {"compare", "practice", "community"},
        {"career", "learn"},
        {"price", "time"},
        7,
        9
    }
};


// ---------------------------------------------------------------------------
// 19. CASE STUDY FEATURE SET
// ---------------------------------------------------------------------------

vector<ProductFeature> learningFeatures = {
    {
        "Guided workflow",
        {
            "unclear instructions",
            "complexity",
            "learn"
        }
    },
    {
        "Practice workspace",
        {
            "practice",
            "complete_task",
            "learn"
        }
    },
    {
        "Progress evidence",
        {
            "career",
            "confidence",
            "achievement"
        }
    },
    {
        "Saved workspace",
        {
            "time",
            "repetitive work",
            "save_time"
        }
    }
};


// ---------------------------------------------------------------------------
// 20. SCENARIO ANALYSIS
// ---------------------------------------------------------------------------

struct FeatureHypothesis {
    string feature;
    double relevance;
};

vector<FeatureHypothesis> evaluateFeatures(
    const Persona& persona,
    const vector<ProductFeature>& features
) {
    vector<FeatureHypothesis> results;

    for (const ProductFeature& feature : features) {
        results.push_back({
            feature.name,
            featureRelevance(persona, feature)
        });
    }

    sort(
        results.begin(),
        results.end(),
        [](const FeatureHypothesis& first,
           const FeatureHypothesis& second) {
            if (first.relevance != second.relevance) {
                return first.relevance > second.relevance;
            }

            return first.feature < second.feature;
        }
    );

    return results;
}


// ---------------------------------------------------------------------------
// 21. PERSONA COMPARISON
// ---------------------------------------------------------------------------

void comparePersonas(
    const Persona& first,
    const Persona& second
) {
    cout << "\nPERSONA COMPARISON\n";

    cout << "  " << first.name
         << " goals: "
         << first.goals.size()
         << "\n";

    cout << "  " << second.name
         << " goals: "
         << second.goals.size()
         << "\n";

    cout << "  " << first.name
         << " job priority: "
         << first.jobPriority()
         << "\n";

    cout << "  " << second.name
         << " job priority: "
         << second.jobPriority()
         << "\n";

    cout << "  " << first.name
         << " frustration impact: "
         << first.frustrationImpact()
         << "\n";

    cout << "  " << second.name
         << " frustration impact: "
         << second.frustrationImpact()
         << "\n";

    cout << "  " << first.name
         << " technology comfort: "
         << first.technologyComfort
         << "/10\n";

    cout << "  " << second.name
         << " technology comfort: "
         << second.technologyComfort
         << "/10\n";

    /*
     * The program reports dimensions separately rather than producing an
     * overall persona score. Different personas can represent different
     * meaningful user segments without one being universally "better."
     */
}


// ---------------------------------------------------------------------------
// 22. MAIN CASE STUDY
// ---------------------------------------------------------------------------

int main() {
    cout << string(78, '=') << "\n";
    cout << "USER PERSONAS: INDUSTRY-STYLE C++ CASE STUDY\n";
    cout << string(78, '=') << "\n";

    cout << "\nScenario:\n";
    cout << "A digital learning platform wants to understand its users "
            "before redesigning recurring learning workflows.\n";

    // ---------------------------------------------------------------
    // Step A: Aggregate raw research.
    // ---------------------------------------------------------------

    const ResearchSummary research =
        aggregateResearch(learningResearch);

    cout << "\nResearch participants: "
         << research.userCount
         << "\n";

    printFrequencyTable(
        "Common behaviors",
        research.behaviors
    );

    printFrequencyTable(
        "Common goals",
        research.goals
    );

    printFrequencyTable(
        "Common frustrations",
        research.frustrations
    );

    cout << "\nAverage technology comfort: "
         << fixed << setprecision(2)
         << research.averageTechnologyComfort
         << "/10\n";

    cout << "Average price sensitivity: "
         << research.averagePriceSensitivity
         << "/10\n";

    // ---------------------------------------------------------------
    // Step B: Segment observations.
    // ---------------------------------------------------------------

    map<string, int> segmentCounts;

    for (const UserObservation& observation : learningResearch) {
        ++segmentCounts[assignSegment(observation)];
    }

    cout << "\nSegments\n";

    for (const auto& [segment, count] : segmentCounts) {
        cout << "  " << segment
             << ": " << count
             << " users\n";
    }

    // ---------------------------------------------------------------
    // Step C: Synthesize a persona.
    // ---------------------------------------------------------------

    Persona learner = synthesizePersona(
        "Practical Career Learner",
        "Evidence-Based Skill Builder",
        learningResearch
    );

    learner.ageRange = "20-35";
    learner.location = "Not used for segmentation";
    learner.occupation = "Student / early-career professional";
    learner.education = "Undergraduate or postgraduate";

    /*
     * Demographic fields are explicitly separated from behavioral fields.
     * The occupation is descriptive context, not a deterministic rule.
     */

    learner.jobs.push_back({
        "Build practical evidence that a learned skill can be applied.",
        JobType::Functional,
        9,
        8
    });

    learner.jobs.push_back({
        "Feel prepared when facing a real technical task.",
        JobType::Emotional,
        8,
        7
    });

    learner.motivations.push_back({
        MotivationCategory::Mastery,
        "Convert theoretical knowledge into usable competence.",
        10
    });

    learner.motivations.push_back({
        MotivationCategory::Achievement,
        "Make visible progress toward career objectives.",
        9
    });

    learner.motivations.push_back({
        MotivationCategory::Convenience,
        "Reduce inefficient learning workflows.",
        8
    });

    printPersona(learner);

    // ---------------------------------------------------------------
    // Step D: Validate the persona.
    // ---------------------------------------------------------------

    const QualityReport quality =
        analyzeQuality(learner);

    printQualityReport(quality);

    // ---------------------------------------------------------------
    // Step E: Evaluate feature hypotheses.
    // ---------------------------------------------------------------

    cout << "\nFeature relevance hypotheses\n";

    const vector<FeatureHypothesis> hypotheses =
        evaluateFeatures(
            learner,
            learningFeatures
        );

    for (const FeatureHypothesis& hypothesis : hypotheses) {
        cout << "  " << hypothesis.feature
             << " -> "
             << fixed << setprecision(3)
             << hypothesis.relevance
             << "\n";
    }

    // ---------------------------------------------------------------
    // Step F: Scenario analysis.
    // ---------------------------------------------------------------

    cout << "\nScenario\n";
    cout << "The user needs to complete a technical task under "
            "time pressure.\n";

    cout << "\nLikely goals:\n";

    for (const string& goal : learner.goals) {
        cout << "  - " << goal << "\n";
    }

    vector<Frustration> rankedFrustrations =
        learner.frustrations;

    sort(
        rankedFrustrations.begin(),
        rankedFrustrations.end(),
        [](const Frustration& first,
           const Frustration& second) {
            if (first.impact() != second.impact()) {
                return first.impact() > second.impact();
            }

            return first.description < second.description;
        }
    );

    cout << "\nHigh-impact frustrations:\n";

    for (const Frustration& frustration : rankedFrustrations) {
        cout << "  - " << frustration.description
             << " | impact="
             << frustration.impact()
             << "\n";
    }

    // ---------------------------------------------------------------
    // Step G: Construct a second persona for comparison.
    // ---------------------------------------------------------------

    Persona manager = {
        "Meera",
        "Decision-Focused Manager",
        "A manager who needs reliable evidence for operational decisions.",
        "30-45",
        "Large metropolitan area",
        "Product manager",
        "Graduate education",
        {
            "Reviews dashboards before meetings.",
            "Requests evidence when metrics conflict.",
            "Validates important numbers."
        },
        {
            "Make decisions using reliable information.",
            "Reduce time spent preparing recurring reports."
        },
        {
            {
                "Fragmented information",
                9,
                7,
                "Combines information manually."
            },
            {
                "Manual reporting",
                8,
                8,
                "Uses spreadsheets and saved templates."
            }
        },
        {
            {
                "Turn fragmented information into a decision-ready view.",
                JobType::Functional,
                10,
                8
            },
            {
                "Feel confident when explaining decisions.",
                JobType::Emotional,
                9,
                7
            },
            {
                "Demonstrate disciplined decision-making.",
                JobType::Social,
                7,
                6
            }
        },
        {
            {
                MotivationCategory::Achievement,
                "Wants measurable outcomes.",
                9
            },
            {
                MotivationCategory::Security,
                "Wants defensible decisions.",
                8
            }
        },
        {
            {
                "Interview research",
                "Managers described evidence verification as important.",
                EvidenceLevel::Reported,
                22
            }
        },
        7,
        5
    };

    printPersona(manager);

    comparePersonas(learner, manager);

    // ---------------------------------------------------------------
    // Step H: Edge cases.
    // ---------------------------------------------------------------

    cout << "\nEdge-case validation\n";

    Persona emptyPersona;

    const QualityReport emptyQuality =
        analyzeQuality(emptyPersona);

    printQualityReport(emptyQuality);

    // ---------------------------------------------------------------
    // Step I: Responsible persona design.
    // ---------------------------------------------------------------

    cout << "\nResponsible persona design\n";
    cout << "  - Collect only product-relevant personal information.\n";
    cout << "  - Prefer ranges when exact values are unnecessary.\n";
    cout << "  - Separate evidence from assumptions.\n";
    cout << "  - Do not treat demographics as deterministic predictors.\n";
    cout << "  - Protect raw research information.\n";
    cout << "  - Avoid fabricated quotations.\n";
    cout << "  - Validate persona assumptions with actual research.\n";

    // ---------------------------------------------------------------
    // Complexity notes.
    // ---------------------------------------------------------------

    cout << "\nComplexity notes\n";
    cout << "  Frequency aggregation: O(N * A)\n";
    cout << "  Persona validation: O(J + E)\n";
    cout << "  Feature evaluation: O(F * S * T)\n";
    cout << "  Sorting frustrations: O(P log P)\n";
    cout << "  N = observations, A = attributes, J = jobs, E = evidence,\n";
    cout << "  F = features, S = feature solution terms, T = persona text size,\n";
    cout << "  P = frustration count.\n";

    cout << "\n"
         << string(78, '=')
         << "\n";
    cout << "CASE STUDY COMPLETE\n";
    cout << string(78, '=')
         << "\n";

    return 0;
}
