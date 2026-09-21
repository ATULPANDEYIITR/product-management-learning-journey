/*
USER JOURNEY ANALYSIS
=====================

Technical case study:
Digital banking account-opening journey

The program models a user journey from product discovery through account
verification and first transaction. It demonstrates:

- Journey stages
- Touchpoints
- Pain points
- Friction
- Emotions
- Moments of truth
- Evidence
- Opportunity identification
- Impact/effort prioritization
- Funnel analysis
- Segmentation
- Service blueprinting
- Root-cause analysis
- Validation
- Complexity considerations
- Production-oriented design decisions

C++17 or later.
*/

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;


// ============================================================================
// 1. DOMAIN TYPES
// ============================================================================

enum class Emotion {
    VeryNegative = -2,
    Negative = -1,
    Neutral = 0,
    Positive = 1,
    VeryPositive = 2
};


string emotionToString(Emotion emotion) {
    switch (emotion) {
        case Emotion::VeryNegative: return "Very Negative";
        case Emotion::Negative: return "Negative";
        case Emotion::Neutral: return "Neutral";
        case Emotion::Positive: return "Positive";
        case Emotion::VeryPositive: return "Very Positive";
    }

    return "Unknown";
}


struct Touchpoint {
    string name;
    string channel;
    string action;

    double effortMinutes{};
    Emotion emotion{Emotion::Neutral};

    double painScore{};
    double frictionScore{};
    double importance{};

    bool momentOfTruth{false};

    vector<string> evidence;

    void validate() const {
        if (name.empty()) {
            throw invalid_argument("Touchpoint name cannot be empty.");
        }

        if (effortMinutes < 0) {
            throw invalid_argument("Effort cannot be negative.");
        }

        for (const auto& [label, value] : vector<pair<string, double>>{
                 {"pain", painScore},
                 {"friction", frictionScore},
                 {"importance", importance}}) {

            if (value < 0 || value > 10) {
                throw invalid_argument(
                    label + " must be between 0 and 10."
                );
            }
        }
    }
};


struct JourneyStage {
    string name;
    string userGoal;

    vector<string> userActions;
    vector<string> expectations;
    vector<Touchpoint> touchpoints;
};


struct Journey {
    string persona;
    string goal;
    vector<JourneyStage> stages;

    void validate() const {
        if (persona.empty()) {
            throw invalid_argument("Persona cannot be empty.");
        }

        if (stages.empty()) {
            throw invalid_argument(
                "A journey must contain at least one stage."
            );
        }

        for (const auto& stage : stages) {
            if (stage.userGoal.empty()) {
                throw invalid_argument(
                    "Every stage must have a user goal."
                );
            }

            for (const auto& point : stage.touchpoints) {
                point.validate();
            }
        }
    }
};


// ============================================================================
// 2. ANALYTICAL TYPES
// ============================================================================

struct Opportunity {
    string stage;
    string problem;
    string userNeed;
    string direction;

    double impact{};
    double confidence{};
    double effort{};

    double priorityScore() const {
        return impact * confidence / max(effort, 1.0);
    }
};


struct FunnelStage {
    string name;
    int entered{};
    int completed{};

    double completionRate() const {
        if (entered <= 0) {
            return 0.0;
        }

        return static_cast<double>(completed) / entered;
    }

    double abandonmentRate() const {
        return 1.0 - completionRate();
    }
};


struct BlueprintStep {
    string stage;
    string customerAction;
    string frontstage;
    string backstage;
    string supportSystem;
    double failureRisk{};
};


// ============================================================================
// 3. UTILITY FUNCTIONS
// ============================================================================

double average(const vector<double>& values) {
    if (values.empty()) {
        return 0.0;
    }

    const double total =
        accumulate(values.begin(), values.end(), 0.0);

    return total / values.size();
}


double painPriority(const Touchpoint& point) {
    /*
    The formula combines severity and strategic importance.

    It is intentionally simple. Production prioritization should also consider
    affected population, frequency, revenue impact, regulatory risk,
    accessibility, technical constraints, and evidence quality.
    */
    return (
        point.painScore *
        point.frictionScore *
        point.importance
    ) / 100.0;
}


vector<const Touchpoint*> allTouchpoints(const Journey& journey) {
    vector<const Touchpoint*> result;

    for (const auto& stage : journey.stages) {
        for (const auto& point : stage.touchpoints) {
            result.push_back(&point);
        }
    }

    return result;
}


// ============================================================================
// 4. JOURNEY CONSTRUCTION
// ============================================================================

Journey buildJourney() {
    Journey journey;

    journey.persona = "First-time digital banking customer";
    journey.goal =
        "Open an account and complete the first transaction";

    journey.stages = {
        {
            "Awareness",
            "Find a trustworthy account",
            {
                "Searches online",
                "Reviews product information",
                "Checks fees"
            },
            {
                "Clear pricing",
                "Simple eligibility",
                "Trustworthy information"
            },
            {
                {
                    "Search result",
                    "Search",
                    "Opens product page",
                    2,
                    Emotion::Positive,
                    2,
                    1,
                    5,
                    false,
                    {"Search analytics"}
                },
                {
                    "Pricing page",
                    "Website",
                    "Reviews fees",
                    5,
                    Emotion::Neutral,
                    5,
                    5,
                    7,
                    true,
                    {"Users struggle to locate fee information"}
                }
            }
        },

        {
            "Consideration",
            "Decide whether the account is suitable",
            {
                "Reads FAQs",
                "Checks eligibility",
                "Compares benefits"
            },
            {
                "Accurate information",
                "Easy comparison"
            },
            {
                {
                    "Eligibility FAQ",
                    "Website",
                    "Checks requirements",
                    7,
                    Emotion::Neutral,
                    4,
                    4,
                    6,
                    false,
                    {"FAQ search behavior"}
                }
            }
        },

        {
            "Signup",
            "Start the application",
            {
                "Enters information",
                "Accepts terms",
                "Submits form"
            },
            {
                "Few unnecessary fields",
                "Visible progress"
            },
            {
                {
                    "Signup form",
                    "Web application",
                    "Completes registration",
                    8,
                    Emotion::Positive,
                    3,
                    3,
                    8,
                    false,
                    {"Form analytics"}
                }
            }
        },

        {
            "Onboarding",
            "Complete identity verification",
            {
                "Uploads document",
                "Corrects errors",
                "Waits for confirmation"
            },
            {
                "Clear instructions",
                "Fast verification",
                "Secure document handling"
            },
            {
                {
                    "Identity verification",
                    "Mobile app",
                    "Uploads identity document",
                    15,
                    Emotion::Negative,
                    8,
                    8,
                    10,
                    true,
                    {
                        "High verification abandonment",
                        "Repeated upload attempts"
                    }
                }
            }
        },

        {
            "First Use",
            "Make the first successful transaction",
            {
                "Adds funds",
                "Selects recipient",
                "Confirms transfer"
            },
            {
                "Clear confirmation",
                "Immediate status"
            },
            {
                {
                    "First transaction",
                    "Mobile app",
                    "Completes transfer",
                    4,
                    Emotion::VeryPositive,
                    1,
                    1,
                    10,
                    true,
                    {"Transaction success rate"}
                }
            }
        },

        {
            "Support",
            "Resolve a problem",
            {
                "Opens help",
                "Searches articles",
                "Contacts support"
            },
            {
                "Fast answer",
                "No repeated information"
            },
            {
                {
                    "Support chatbot",
                    "In-app support",
                    "Searches for transaction help",
                    10,
                    Emotion::Negative,
                    7,
                    7,
                    8,
                    true,
                    {"Support transcripts"}
                }
            }
        }
    };

    journey.validate();
    return journey;
}


// ============================================================================
// 5. JOURNEY MAP
// ============================================================================

void printJourneyMap(const Journey& journey) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "JOURNEY MAP\n";
    cout << string(78, '=') << '\n';

    for (size_t index = 0; index < journey.stages.size(); ++index) {
        const auto& stage = journey.stages[index];

        cout << "\n" << index + 1 << ". " << stage.name << '\n';
        cout << "Goal: " << stage.userGoal << '\n';

        cout << "Actions:\n";
        for (const auto& action : stage.userActions) {
            cout << "  - " << action << '\n';
        }

        cout << "Touchpoints:\n";
        for (const auto& point : stage.touchpoints) {
            cout << "  - " << point.name
                 << " | channel=" << point.channel
                 << " | pain=" << point.painScore
                 << "/10 | friction=" << point.frictionScore
                 << "/10 | emotion=" << emotionToString(point.emotion)
                 << '\n';
        }
    }
}


// ============================================================================
// 6. PAIN POINT ANALYSIS
// ============================================================================

void analyzePainPoints(const Journey& journey) {
    struct RankedPoint {
        const Touchpoint* point;
        double priority;
    };

    vector<RankedPoint> ranked;

    for (const auto& point : allTouchpoints(journey)) {
        if (point->painScore >= 5 || point->frictionScore >= 5) {
            ranked.push_back({
                point,
                painPriority(*point)
            });
        }
    }

    sort(
        ranked.begin(),
        ranked.end(),
        [](const RankedPoint& a, const RankedPoint& b) {
            return a.priority > b.priority;
        }
    );

    cout << "\n" << string(78, '=') << '\n';
    cout << "PAIN POINT PRIORITIZATION\n";
    cout << string(78, '=') << '\n';

    for (const auto& item : ranked) {
        cout << left << setw(27)
             << item.point->name
             << " pain=" << item.point->painScore
             << " friction=" << item.point->frictionScore
             << " importance=" << item.point->importance
             << " priority=" << fixed << setprecision(2)
             << item.priority
             << '\n';
    }
}


// ============================================================================
// 7. MOMENTS OF TRUTH
// ============================================================================

void printMomentsOfTruth(const Journey& journey) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "MOMENTS OF TRUTH\n";
    cout << string(78, '=') << '\n';

    for (const auto& point : allTouchpoints(journey)) {
        if (point->momentOfTruth) {
            cout << point->name
                 << " | emotion=" << emotionToString(point->emotion)
                 << " | importance=" << point->importance
                 << "/10\n";
        }
    }
}


// ============================================================================
// 8. EMOTIONAL CURVE
// ============================================================================

void printEmotionalCurve(const Journey& journey) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "EMOTIONAL CURVE\n";
    cout << string(78, '=') << '\n';

    for (const auto& stage : journey.stages) {
        vector<double> scores;

        for (const auto& point : stage.touchpoints) {
            scores.push_back(
                static_cast<int>(point.emotion)
            );
        }

        const double score = average(scores);

        const int barLength =
            max(0, static_cast<int>(round((score + 2) * 5)));

        cout << left << setw(20)
             << stage.name
             << " | " << fixed << setprecision(2)
             << score << " | "
             << string(barLength, '#')
             << '\n';
    }
}


// ============================================================================
// 9. CHANNEL ANALYSIS
// ============================================================================

void analyzeChannels(const Journey& journey) {
    struct ChannelStats {
        vector<double> pain;
        vector<double> friction;
        vector<double> effort;
    };

    unordered_map<string, ChannelStats> channels;

    for (const auto& point : allTouchpoints(journey)) {
        auto& stats = channels[point->channel];

        stats.pain.push_back(point->painScore);
        stats.friction.push_back(point->frictionScore);
        stats.effort.push_back(point->effortMinutes);
    }

    cout << "\n" << string(78, '=') << '\n';
    cout << "CHANNEL ANALYSIS\n";
    cout << string(78, '=') << '\n';

    for (const auto& [channel, stats] : channels) {
        cout << left << setw(22)
             << channel
             << " count=" << stats.pain.size()
             << " avg pain=" << fixed << setprecision(2)
             << average(stats.pain)
             << " avg friction=" << average(stats.friction)
             << " avg effort=" << average(stats.effort)
             << " min\n";
    }
}


// ============================================================================
// 10. FUNNEL ANALYSIS
// ============================================================================

void analyzeFunnel(const vector<FunnelStage>& stages) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "FUNNEL ANALYSIS\n";
    cout << string(78, '=') << '\n';

    for (const auto& stage : stages) {
        cout << left << setw(26)
             << stage.name
             << " entered=" << setw(6)
             << stage.entered
             << " completed=" << setw(6)
             << stage.completed
             << " completion=" << fixed << setprecision(1)
             << stage.completionRate() * 100
             << "% abandonment="
             << stage.abandonmentRate() * 100
             << "%\n";
    }
}


// ============================================================================
// 11. OPPORTUNITY GENERATION
// ============================================================================

vector<Opportunity> generateOpportunities(const Journey& journey) {
    vector<Opportunity> opportunities;

    for (const auto& stage : journey.stages) {
        for (const auto& point : stage.touchpoints) {
            if (
                point.painScore < 5 &&
                point.frictionScore < 5
            ) {
                continue;
            }

            string direction;

            if (point.name == "Identity verification") {
                direction =
                    "Add format guidance, examples, immediate validation, "
                    "progress feedback, and recovery paths.";
            } else if (point.name == "Support chatbot") {
                direction =
                    "Improve intent recognition, contextual responses, "
                    "and human escalation.";
            } else if (point.name == "Pricing page") {
                direction =
                    "Make important fees and conditions visible in plain language.";
            } else {
                direction =
                    "Investigate the root cause before selecting a solution.";
            }

            opportunities.push_back({
                stage.name,
                point.name,
                "Complete the task with less uncertainty and effort.",
                direction,
                point.importance,
                point.evidence.empty() ? 0.4 : 0.8,
                5.0
            });
        }
    }

    sort(
        opportunities.begin(),
        opportunities.end(),
        [](const Opportunity& a, const Opportunity& b) {
            return a.priorityScore() > b.priorityScore();
        }
    );

    return opportunities;
}


void printOpportunities(const Journey& journey) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "OPPORTUNITY ANALYSIS\n";
    cout << string(78, '=') << '\n';

    for (const auto& opportunity : generateOpportunities(journey)) {
        cout << "\nStage: " << opportunity.stage
             << "\nProblem: " << opportunity.problem
             << "\nNeed: " << opportunity.userNeed
             << "\nDirection: " << opportunity.direction
             << "\nPriority aid: " << fixed << setprecision(3)
             << opportunity.priorityScore()
             << '\n';
    }
}


// ============================================================================
// 12. SERVICE BLUEPRINT
// ============================================================================

vector<BlueprintStep> buildBlueprint() {
    return {
        {
            "Signup",
            "Submits registration",
            "Form validates data",
            "Identity service processes data",
            "Database and validation service",
            3
        },
        {
            "Verification",
            "Uploads document",
            "App displays status",
            "Verification service processes document",
            "Storage, OCR, verification provider",
            8
        },
        {
            "Transaction",
            "Confirms transfer",
            "App shows transaction status",
            "Payment service updates ledger",
            "Fraud and transaction systems",
            6
        }
    };
}


void printBlueprint(const vector<BlueprintStep>& blueprint) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "SERVICE BLUEPRINT\n";
    cout << string(78, '=') << '\n';

    for (const auto& step : blueprint) {
        cout << "\n" << step.stage
             << "\n  Customer: " << step.customerAction
             << "\n  Frontstage: " << step.frontstage
             << "\n  Backstage: " << step.backstage
             << "\n  Support: " << step.supportSystem
             << "\n  Failure risk: " << step.failureRisk
             << "/10\n";
    }
}


// ============================================================================
// 13. FIVE WHYS
// ============================================================================

void printFiveWhys(
    const string& problem,
    const vector<string>& causes
) {
    cout << "\n" << string(78, '=') << '\n';
    cout << "FIVE WHYS\n";
    cout << string(78, '=') << '\n';

    cout << "Observed problem: " << problem << '\n';

    for (size_t i = 0; i < min<size_t>(5, causes.size()); ++i) {
        cout << "Why " << i + 1 << ": "
             << causes[i] << '\n';
    }

    cout <<
        "The causal chain is a hypothesis and should be checked against "
        "research and operational evidence.\n";
}


// ============================================================================
// 14. CUSTOMER EFFORT
// ============================================================================

double customerEffort(const Journey& journey) {
    const auto points = allTouchpoints(journey);

    if (points.empty()) {
        return 0.0;
    }

    vector<double> effortScores;

    for (const auto* point : points) {
        const double timeComponent =
            min(point->effortMinutes / 20.0, 1.0) * 5.0;

        const double frictionComponent =
            point->frictionScore / 10.0 * 5.0;

        effortScores.push_back(
            timeComponent + frictionComponent
        );
    }

    return average(effortScores);
}


// ============================================================================
// 15. SEGMENT COMPARISON
// ============================================================================

void analyzeSegments() {
    map<string, vector<double>> segments = {
        {"First-time users", {4, 5, 3, 4, 5}},
        {"Returning users", {8, 9, 7, 8, 9}},
        {"Mobile users", {6, 5, 7, 6, 5}},
        {"Desktop users", {7, 6, 5, 7, 6}}
    };

    cout << "\n" << string(78, '=') << '\n';
    cout << "SEGMENT ANALYSIS\n";
    cout << string(78, '=') << '\n';

    for (const auto& [segment, scores] : segments) {
        cout << left << setw(22)
             << segment
             << " mean=" << fixed << setprecision(2)
             << average(scores)
             << " min=" << *min_element(scores.begin(), scores.end())
             << " max=" << *max_element(scores.begin(), scores.end())
             << '\n';
    }
}


// ============================================================================
// 16. FRICTION VARIABILITY
// ============================================================================

double standardDeviation(const vector<double>& values) {
    if (values.empty()) {
        return 0.0;
    }

    const double averageValue = average(values);

    double squaredDifference = 0.0;

    for (double value : values) {
        squaredDifference +=
            pow(value - averageValue, 2);
    }

    return sqrt(
        squaredDifference / values.size()
    );
}


void analyzeFrictionVariability(const Journey& journey) {
    vector<double> friction;

    for (const auto* point : allTouchpoints(journey)) {
        friction.push_back(point->frictionScore);
    }

    cout << "\n" << string(78, '=') << '\n';
    cout << "FRICTION VARIABILITY\n";
    cout << string(78, '=') << '\n';

    cout << "Standard deviation: "
         << fixed << setprecision(2)
         << standardDeviation(friction)
         << '\n';

    cout <<
        "Variation can indicate that some journey interactions perform "
        "very differently from others.\n";
}


// ============================================================================
// 17. EDGE-CASE VALIDATION
// ============================================================================

void demonstrateValidation() {
    cout << "\n" << string(78, '=') << '\n';
    cout << "VALIDATION AND EDGE CASES\n";
    cout << string(78, '=') << '\n';

    try {
        Touchpoint invalid{
            "Invalid",
            "Test",
            "Test",
            -1,
            Emotion::Neutral,
            5,
            5,
            5,
            false,
            {}
        };

        invalid.validate();
    } catch (const exception& error) {
        cout << "Rejected invalid effort: "
             << error.what() << '\n';
    }

    try {
        Touchpoint invalid{
            "Invalid score",
            "Test",
            "Test",
            1,
            Emotion::Neutral,
            11,
            5,
            5,
            false,
            {}
        };

        invalid.validate();
    } catch (const exception& error) {
        cout << "Rejected invalid score: "
             << error.what() << '\n';
    }
}


// ============================================================================
// 18. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        Journey journey = buildJourney();

        printJourneyMap(journey);
        analyzePainPoints(journey);
        printMomentsOfTruth(journey);
        printEmotionalCurve(journey);
        analyzeChannels(journey);

        cout << "\n" << string(78, '=') << '\n';
        cout << "CUSTOMER EFFORT\n";
        cout << string(78, '=') << '\n';

        cout << "Effort index: "
             << fixed << setprecision(2)
             << customerEffort(journey)
             << "/10\n";

        analyzeFunnel({
            {"Product page", 10000, 7200},
            {"Application start", 7200, 5900},
            {"Verification start", 5900, 3400},
            {"Verification complete", 3400, 2950},
            {"First transaction", 2950, 2400}
        });

        analyzeSegments();

        printOpportunities(journey);

        printBlueprint(buildBlueprint());

        printFiveWhys(
            "Users abandon identity verification",
            {
                "Some document uploads fail.",
                "Accepted formats are unclear.",
                "Validation occurs too late.",
                "Recovery paths are weak.",
                "Failure scenarios were not sufficiently represented in design."
            }
        );

        analyzeFrictionVariability(journey);
        demonstrateValidation();

        cout << "\n" << string(78, '=') << '\n';
        cout << "IMPLEMENTATION NOTES\n";
        cout << string(78, '=') << '\n';

        cout <<
            "The primary journey traversal is O(T), where T is the number "
            "of touchpoints.\n";

        cout <<
            "Pain-point ranking is O(T log T) because qualifying touchpoints "
            "are sorted by priority.\n";

        cout <<
            "The model stores journey information in vectors because ordered "
            "journey stages and touchpoints are central to the problem.\n";

        cout <<
            "unordered_map is used for channel aggregation because average "
            "lookup and insertion are approximately constant time.\n";

        cout <<
            "Production systems should separate domain models, persistence, "
            "analytics, API layers, authentication, authorization, logging, "
            "and observability rather than placing everything in main().\n";

        cout << "\n" << string(78, '=') << '\n';
        cout << "END OF USER JOURNEY ANALYSIS CASE STUDY\n";
        cout << string(78, '=') << '\n';

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
