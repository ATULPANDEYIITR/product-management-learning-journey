#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

/*
 * SURVEY DESIGN: C++17 INDUSTRY-STYLE CASE STUDY
 *
 * Scenario
 * --------
 * A software company wants to measure the experience of customers who used
 * its service during the previous 30 days.
 *
 * The system models:
 *   1. Survey objectives and traceability
 *   2. A target population and sampling frame
 *   3. Stratified probability sampling
 *   4. Survey questions and validation
 *   5. Conditional branching
 *   6. Response-quality checks
 *   7. Data cleaning
 *   8. Likert-scale analysis
 *   9. Net Promoter Score
 *  10. Cross-tabulation
 *  11. Missing-data analysis
 *  12. Basic confidence-interval estimation
 *  13. Design-effect reasoning
 *  14. Security and privacy considerations
 *
 * Compile:
 *   g++ -std=c++17 -O2 survey_design.cpp -o survey_design
 *
 * The program uses only the C++ standard library.
 */

using namespace std;

// =============================================================================
// 1. BASIC DATA MODELS
// =============================================================================

enum class QuestionType {
    SingleChoice,
    MultipleChoice,
    Scale,
    Text
};

string questionTypeName(QuestionType type) {
    switch (type) {
        case QuestionType::SingleChoice:
            return "Single Choice";
        case QuestionType::MultipleChoice:
            return "Multiple Choice";
        case QuestionType::Scale:
            return "Scale";
        case QuestionType::Text:
            return "Text";
    }

    return "Unknown";
}

struct SurveyObjective {
    string id;
    string description;
    string metric;
    string population;
};

struct SurveyQuestion {
    string id;
    string text;
    QuestionType type;
    bool required = false;
    vector<string> options;
    optional<int> minimum;
    optional<int> maximum;
};

struct Response {
    string respondentId;
    unordered_map<string, string> scalarAnswers;
    unordered_map<string, vector<string>> multipleAnswers;

    double completionSeconds = 0.0;
    bool attentionCheckPassed = true;
    bool duplicate = false;
};


// =============================================================================
// 2. SURVEY VALIDATION
// =============================================================================

class Survey {
private:
    string title;
    string purpose;
    string population;
    vector<SurveyQuestion> questions;

public:
    Survey(
        string titleValue,
        string purposeValue,
        string populationValue,
        vector<SurveyQuestion> questionList
    )
        : title(move(titleValue)),
          purpose(move(purposeValue)),
          population(move(populationValue)),
          questions(move(questionList)) {}

    const string& getTitle() const {
        return title;
    }

    const vector<SurveyQuestion>& getQuestions() const {
        return questions;
    }

    vector<string> validateResponse(const Response& response) const {
        vector<string> errors;

        for (const auto& question : questions) {
            if (question.type == QuestionType::MultipleChoice) {
                auto it = response.multipleAnswers.find(question.id);

                if (question.required &&
                    (it == response.multipleAnswers.end() ||
                     it->second.empty())) {
                    errors.push_back(
                        question.id + ": required multiple-choice question."
                    );
                    continue;
                }

                if (it == response.multipleAnswers.end()) {
                    continue;
                }

                for (const auto& answer : it->second) {
                    if (find(
                            question.options.begin(),
                            question.options.end(),
                            answer
                        ) == question.options.end()) {
                        errors.push_back(
                            question.id + ": invalid option '" +
                            answer + "'."
                        );
                    }
                }

                continue;
            }

            auto it = response.scalarAnswers.find(question.id);

            if (it == response.scalarAnswers.end()) {
                if (question.required) {
                    errors.push_back(
                        question.id + ": required answer missing."
                    );
                }
                continue;
            }

            const string& answer = it->second;

            if (question.required && answer.empty()) {
                errors.push_back(
                    question.id + ": required answer is empty."
                );
                continue;
            }

            if (question.type == QuestionType::SingleChoice) {
                if (find(
                        question.options.begin(),
                        question.options.end(),
                        answer
                    ) == question.options.end()) {
                    errors.push_back(
                        question.id + ": invalid single-choice option."
                    );
                }
            }

            if (question.type == QuestionType::Scale) {
                try {
                    size_t processed = 0;
                    int numericValue = stoi(answer, &processed);

                    if (processed != answer.size()) {
                        throw invalid_argument("extra characters");
                    }

                    if (question.minimum.has_value() &&
                        numericValue < question.minimum.value()) {
                        errors.push_back(
                            question.id + ": value is below minimum."
                        );
                    }

                    if (question.maximum.has_value() &&
                        numericValue > question.maximum.value()) {
                        errors.push_back(
                            question.id + ": value exceeds maximum."
                        );
                    }
                } catch (const exception&) {
                    errors.push_back(
                        question.id + ": scale answer is not an integer."
                    );
                }
            }
        }

        return errors;
    }
};


// =============================================================================
// 3. STRATIFIED SAMPLING
// =============================================================================

struct Customer {
    int id;
    string region;
    string plan;
    bool eligible;
};

vector<Customer> stratifiedSample(
    const vector<Customer>& population,
    size_t requestedSampleSize,
    unsigned seed
) {
    if (requestedSampleSize == 0) {
        return {};
    }

    vector<Customer> eligibleCustomers;

    for (const auto& customer : population) {
        if (customer.eligible) {
            eligibleCustomers.push_back(customer);
        }
    }

    if (requestedSampleSize > eligibleCustomers.size()) {
        throw invalid_argument(
            "Requested sample is larger than the eligible population."
        );
    }

    map<string, vector<Customer>> strata;

    for (const auto& customer : eligibleCustomers) {
        strata[customer.region].push_back(customer);
    }

    const size_t totalEligible = eligibleCustomers.size();

    map<string, size_t> allocations;
    map<string, double> remainders;

    size_t allocated = 0;

    for (const auto& [region, customers] : strata) {
        double exact =
            static_cast<double>(customers.size()) *
            static_cast<double>(requestedSampleSize) /
            static_cast<double>(totalEligible);

        size_t base = static_cast<size_t>(floor(exact));

        allocations[region] = base;
        remainders[region] = exact - static_cast<double>(base);
        allocated += base;
    }

    /*
     * Largest-remainder allocation avoids losing the requested sample size
     * through integer rounding.
     */
    vector<string> regions;

    for (const auto& [region, _] : strata) {
        regions.push_back(region);
    }

    sort(
        regions.begin(),
        regions.end(),
        [&](const string& a, const string& b) {
            return remainders[a] > remainders[b];
        }
    );

    size_t remaining = requestedSampleSize - allocated;

    for (size_t i = 0; i < remaining; ++i) {
        ++allocations[regions[i % regions.size()]];
    }

    mt19937 generator(seed);

    vector<Customer> result;

    for (const auto& [region, customers] : strata) {
        vector<Customer> shuffled = customers;

        shuffle(
            shuffled.begin(),
            shuffled.end(),
            generator
        );

        size_t count = allocations[region];

        result.insert(
            result.end(),
            shuffled.begin(),
            shuffled.begin() + static_cast<long>(count)
        );
    }

    return result;
}


// =============================================================================
// 4. BRANCHING LOGIC
// =============================================================================

struct BranchRule {
    string sourceQuestionId;
    string expectedAnswer;
    string destinationQuestionId;

    bool matches(
        const unordered_map<string, string>& answers
    ) const {
        auto it = answers.find(sourceQuestionId);

        return it != answers.end() &&
               it->second == expectedAnswer;
    }
};

optional<string> determineNextQuestion(
    const vector<BranchRule>& rules,
    const unordered_map<string, string>& answers
) {
    for (const auto& rule : rules) {
        if (rule.matches(answers)) {
            return rule.destinationQuestionId;
        }
    }

    return nullopt;
}


// =============================================================================
// 5. NUMERICAL UTILITIES
// =============================================================================

double mean(const vector<int>& values) {
    if (values.empty()) {
        throw invalid_argument("Cannot calculate mean of empty vector.");
    }

    double total = accumulate(
        values.begin(),
        values.end(),
        0.0
    );

    return total / static_cast<double>(values.size());
}

double median(vector<int> values) {
    if (values.empty()) {
        throw invalid_argument("Cannot calculate median of empty vector.");
    }

    sort(values.begin(), values.end());

    size_t middle = values.size() / 2;

    if (values.size() % 2 == 0) {
        return (
            static_cast<double>(values[middle - 1]) +
            static_cast<double>(values[middle])
        ) / 2.0;
    }

    return static_cast<double>(values[middle]);
}

double nps(const vector<int>& scores) {
    if (scores.empty()) {
        throw invalid_argument("NPS requires at least one response.");
    }

    int promoters = 0;
    int detractors = 0;

    for (int score : scores) {
        if (score < 0 || score > 10) {
            throw invalid_argument(
                "NPS score must be between 0 and 10."
            );
        }

        if (score >= 9) {
            ++promoters;
        }

        if (score <= 6) {
            ++detractors;
        }
    }

    double denominator = static_cast<double>(scores.size());

    return (
        static_cast<double>(promoters) / denominator * 100.0
    ) - (
        static_cast<double>(detractors) / denominator * 100.0
    );
}


// =============================================================================
// 6. RESPONSE-QUALITY DETECTION
// =============================================================================

vector<string> qualityFlags(
    const Response& response,
    double minimumCompletionSeconds
) {
    vector<string> flags;

    if (response.completionSeconds < minimumCompletionSeconds) {
        flags.push_back("Unusually fast completion.");
    }

    if (!response.attentionCheckPassed) {
        flags.push_back("Attention check failed.");
    }

    if (response.duplicate) {
        flags.push_back("Potential duplicate response.");
    }

    return flags;
}


// =============================================================================
// 7. MISSING DATA
// =============================================================================

double missingRate(
    const vector<optional<int>>& values
) {
    if (values.empty()) {
        return 0.0;
    }

    size_t missing = 0;

    for (const auto& value : values) {
        if (!value.has_value()) {
            ++missing;
        }
    }

    return (
        static_cast<double>(missing) /
        static_cast<double>(values.size())
    ) * 100.0;
}


// =============================================================================
// 8. CROSS-TABULATION
// =============================================================================

map<string, map<string, int>> crossTabulate(
    const vector<string>& rows,
    const vector<string>& columns
) {
    if (rows.size() != columns.size()) {
        throw invalid_argument(
            "Cross-tabulation vectors must have equal length."
        );
    }

    map<string, map<string, int>> table;

    for (size_t i = 0; i < rows.size(); ++i) {
        ++table[rows[i]][columns[i]];
    }

    return table;
}


// =============================================================================
// 9. CONFIDENCE INTERVAL
// =============================================================================

pair<double, double> proportionConfidenceInterval(
    double proportion,
    size_t sampleSize,
    double z = 1.96
) {
    if (
        proportion < 0.0 ||
        proportion > 1.0 ||
        sampleSize == 0
    ) {
        throw invalid_argument(
            "Invalid proportion or sample size."
        );
    }

    double standardError = sqrt(
        proportion * (1.0 - proportion) /
        static_cast<double>(sampleSize)
    );

    double margin = z * standardError;

    double lower = max(
        0.0,
        proportion - margin
    );

    double upper = min(
        1.0,
        proportion + margin
    );

    return {lower, upper};
}


// =============================================================================
// 10. DESIGN EFFECT
// =============================================================================

double designEffect(
    double averageClusterSize,
    double intraclassCorrelation
) {
    if (averageClusterSize < 1.0) {
        throw invalid_argument(
            "Average cluster size must be at least 1."
        );
    }

    if (
        intraclassCorrelation < 0.0 ||
        intraclassCorrelation > 1.0
    ) {
        throw invalid_argument(
            "ICC must be between 0 and 1."
        );
    }

    return 1.0 +
           (averageClusterSize - 1.0) *
           intraclassCorrelation;
}


// =============================================================================
// 11. DATA CLEANING
// =============================================================================

vector<Response> removeDuplicates(
    const vector<Response>& responses
) {
    set<string> seen;
    vector<Response> cleaned;

    for (const auto& response : responses) {
        if (seen.insert(response.respondentId).second) {
            cleaned.push_back(response);
        }
    }

    return cleaned;
}


// =============================================================================
// 12. MAIN CASE STUDY
// =============================================================================

int main() {
    cout << string(78, '=') << '\n';
    cout << "SURVEY DESIGN: CUSTOMER EXPERIENCE CASE STUDY\n";
    cout << string(78, '=') << "\n\n";

    // -------------------------------------------------------------------------
    // A. Define research objectives.
    // -------------------------------------------------------------------------

    vector<SurveyObjective> objectives = {
        {
            "OBJ-01",
            "Measure recent customer satisfaction.",
            "Mean satisfaction score",
            "Eligible customers who used the service within 30 days"
        },
        {
            "OBJ-02",
            "Identify service areas needing improvement.",
            "Frequency of selected improvement areas",
            "Eligible recent users"
        },
        {
            "OBJ-03",
            "Measure willingness to recommend.",
            "Net Promoter Score",
            "Eligible recent users"
        }
    };

    cout << "RESEARCH OBJECTIVES\n";
    for (const auto& objective : objectives) {
        cout << objective.id << ": "
             << objective.description << '\n';
        cout << "  Metric: " << objective.metric << '\n';
        cout << "  Population: " << objective.population << "\n\n";
    }

    // -------------------------------------------------------------------------
    // B. Build a simulated population.
    // -------------------------------------------------------------------------

    cout << string(78, '-') << '\n';
    cout << "TARGET POPULATION AND SAMPLING FRAME\n";
    cout << string(78, '-') << '\n';

    vector<string> regions = {
        "North",
        "South",
        "West",
        "East"
    };

    vector<string> plans = {
        "Free",
        "Basic",
        "Professional",
        "Enterprise"
    };

    vector<Customer> population;

    for (int id = 1; id <= 400; ++id) {
        const string& region =
            regions[static_cast<size_t>((id - 1) % regions.size())];

        const string& plan =
            plans[static_cast<size_t>((id - 1) % plans.size())];

        /*
         * Every tenth record is treated as outside the eligibility condition.
         * This demonstrates that the sampling frame can contain people who
         * are not part of the target population.
         */
        bool eligible = (id % 10 != 0);

        population.push_back({
            id,
            region,
            plan,
            eligible
        });
    }

    size_t eligibleCount = count_if(
        population.begin(),
        population.end(),
        [](const Customer& customer) {
            return customer.eligible;
        }
    );

    cout << "Frame records: " << population.size() << '\n';
    cout << "Eligible records: " << eligibleCount << "\n\n";

    // -------------------------------------------------------------------------
    // C. Stratified probability sampling.
    // -------------------------------------------------------------------------

    cout << "STRATIFIED SAMPLE\n";

    vector<Customer> sample =
        stratifiedSample(population, 40, 42);

    map<string, int> sampleByRegion;

    for (const auto& customer : sample) {
        ++sampleByRegion[customer.region];
    }

    cout << "Requested sample: 40\n";
    cout << "Actual sample: " << sample.size() << '\n';

    for (const auto& [region, count] : sampleByRegion) {
        cout << "  " << region << ": " << count << '\n';
    }

    // -------------------------------------------------------------------------
    // D. Define the survey instrument.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "SURVEY INSTRUMENT\n";
    cout << string(78, '-') << '\n';

    vector<SurveyQuestion> questions = {
        {
            "S1",
            "Have you used the service during the last 30 days?",
            QuestionType::SingleChoice,
            true,
            {"Yes", "No"},
            nullopt,
            nullopt
        },
        {
            "S2",
            "How satisfied are you with the service?",
            QuestionType::Scale,
            true,
            {},
            1,
            5
        },
        {
            "S3",
            "Which areas need improvement?",
            QuestionType::MultipleChoice,
            false,
            {
                "Speed",
                "Reliability",
                "Support",
                "Pricing",
                "Features"
            },
            nullopt,
            nullopt
        },
        {
            "S4",
            "How likely are you to recommend the service?",
            QuestionType::Scale,
            true,
            {},
            0,
            10
        },
        {
            "S5",
            "What is the most important improvement?",
            QuestionType::Text,
            false,
            {},
            nullopt,
            nullopt
        }
    };

    Survey survey(
        "Service Experience Study",
        "Measure recent customer experience and improvement priorities.",
        "Customers who used the service during the last 30 days.",
        questions
    );

    for (const auto& question : survey.getQuestions()) {
        cout << question.id << " | "
             << questionTypeName(question.type)
             << " | required=" << boolalpha
             << question.required << '\n';
        cout << "  " << question.text << '\n';
    }

    // -------------------------------------------------------------------------
    // E. Conditional branching.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "CONDITIONAL LOGIC\n";
    cout << string(78, '-') << '\n';

    vector<BranchRule> rules = {
        {
            "S1",
            "Yes",
            "S2"
        },
        {
            "S1",
            "No",
            "S5"
        }
    };

    unordered_map<string, string> routingAnswers = {
        {"S1", "Yes"}
    };

    auto nextQuestion =
        determineNextQuestion(
            rules,
            routingAnswers
        );

    if (nextQuestion.has_value()) {
        cout << "Next question: "
             << nextQuestion.value() << '\n';
    } else {
        cout << "No branch rule matched.\n";
    }

    // -------------------------------------------------------------------------
    // F. Create completed responses.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "RESPONSE COLLECTION\n";
    cout << string(78, '-') << '\n';

    vector<Response> responses;

    responses.push_back({
        "R1",
        {
            {"S1", "Yes"},
            {"S2", "5"},
            {"S4", "10"},
            {"S5", "Keep the service fast."}
        },
        {
            {"S3", {"Speed"}}
        },
        124.0,
        true,
        false
    });

    responses.push_back({
        "R2",
        {
            {"S1", "Yes"},
            {"S2", "4"},
            {"S4", "8"},
            {"S5", "Improve support response time."}
        },
        {
            {"S3", {"Support", "Reliability"}}
        },
        186.0,
        true,
        false
    });

    responses.push_back({
        "R3",
        {
            {"S1", "No"},
            {"S4", "4"},
            {"S5", "Improve onboarding."}
        },
        {
            {"S3", {}}
        },
        21.0,
        false,
        false
    });

    responses.push_back({
        "R4",
        {
            {"S1", "Yes"},
            {"S2", "3"},
            {"S4", "6"},
            {"S5", "Make pricing clearer."}
        },
        {
            {"S3", {"Pricing"}}
        },
        170.0,
        true,
        false
    });

    /*
     * Deliberately duplicated response to demonstrate duplicate detection.
     */
    responses.push_back({
        "R1",
        {
            {"S1", "Yes"},
            {"S2", "5"},
            {"S4", "10"}
        },
        {
            {"S3", {"Speed"}}
        },
        110.0,
        true,
        true
    });

    // -------------------------------------------------------------------------
    // G. Validate every response.
    // -------------------------------------------------------------------------

    cout << "\nVALIDATION RESULTS\n";

    for (const auto& response : responses) {
        vector<string> errors =
            survey.validateResponse(response);

        cout << response.respondentId << ": ";

        if (errors.empty()) {
            cout << "valid";
        } else {
            cout << "invalid\n";

            for (const auto& error : errors) {
                cout << "  - " << error << '\n';
            }
        }

        cout << '\n';
    }

    // -------------------------------------------------------------------------
    // H. Response-quality checks.
    // -------------------------------------------------------------------------

    cout << "RESPONSE QUALITY FLAGS\n";

    for (const auto& response : responses) {
        vector<string> flags =
            qualityFlags(response, 30.0);

        cout << response.respondentId << ":\n";

        if (flags.empty()) {
            cout << "  No automated quality flags.\n";
        } else {
            for (const auto& flag : flags) {
                cout << "  - " << flag << '\n';
            }
        }
    }

    // -------------------------------------------------------------------------
    // I. Remove duplicates.
    // -------------------------------------------------------------------------

    cout << "\nDATA CLEANING\n";

    vector<Response> cleanedResponses =
        removeDuplicates(responses);

    cout << "Before deduplication: "
         << responses.size() << '\n';

    cout << "After deduplication: "
         << cleanedResponses.size() << '\n';

    // -------------------------------------------------------------------------
    // J. Analyze valid recent users.
    // -------------------------------------------------------------------------

    vector<int> satisfactionScores;
    vector<int> recommendationScores;

    vector<string> planGroups;
    vector<string> satisfactionGroups;

    map<string, int> improvementCounts;

    for (const auto& response : cleanedResponses) {
        auto usageIt =
            response.scalarAnswers.find("S1");

        if (
            usageIt == response.scalarAnswers.end() ||
            usageIt->second != "Yes"
        ) {
            continue;
        }

        auto satisfactionIt =
            response.scalarAnswers.find("S2");

        if (satisfactionIt != response.scalarAnswers.end()) {
            satisfactionScores.push_back(
                stoi(satisfactionIt->second)
            );

            if (satisfactionIt->second == "4" ||
                satisfactionIt->second == "5") {
                satisfactionGroups.push_back("Satisfied");
            } else if (satisfactionIt->second == "3") {
                satisfactionGroups.push_back("Neutral");
            } else {
                satisfactionGroups.push_back("Dissatisfied");
            }
        }

        auto recommendationIt =
            response.scalarAnswers.find("S4");

        if (recommendationIt != response.scalarAnswers.end()) {
            recommendationScores.push_back(
                stoi(recommendationIt->second)
            );
        }

        auto improvementIt =
            response.multipleAnswers.find("S3");

        if (improvementIt != response.multipleAnswers.end()) {
            for (const auto& area : improvementIt->second) {
                ++improvementCounts[area];
            }
        }
    }

    // -------------------------------------------------------------------------
    // K. Descriptive analysis.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "DESCRIPTIVE ANALYSIS\n";
    cout << string(78, '-') << '\n';

    if (!satisfactionScores.empty()) {
        cout << fixed << setprecision(2);

        cout << "Mean satisfaction: "
             << mean(satisfactionScores) << '\n';

        cout << "Median satisfaction: "
             << median(satisfactionScores) << '\n';
    }

    if (!recommendationScores.empty()) {
        cout << "NPS: "
             << nps(recommendationScores)
             << '\n';
    }

    cout << "Improvement areas:\n";

    for (const auto& [area, count] : improvementCounts) {
        cout << "  " << area << ": "
             << count << '\n';
    }

    // -------------------------------------------------------------------------
    // L. Cross-tabulation example.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "CROSS-TABULATION\n";
    cout << string(78, '-') << '\n';

    vector<string> planValues = {
        "Free",
        "Free",
        "Basic",
        "Basic",
        "Professional",
        "Professional"
    };

    vector<string> satisfactionValues = {
        "Satisfied",
        "Neutral",
        "Satisfied",
        "Dissatisfied",
        "Satisfied",
        "Neutral"
    };

    auto table =
        crossTabulate(
            planValues,
            satisfactionValues
        );

    for (const auto& [plan, columns] : table) {
        cout << plan << ":\n";

        for (const auto& [category, count] : columns) {
            cout << "  " << category
                 << ": " << count << '\n';
        }
    }

    // -------------------------------------------------------------------------
    // M. Missing-data analysis.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "MISSING DATA\n";
    cout << string(78, '-') << '\n';

    vector<optional<int>> missingExample = {
        5,
        4,
        nullopt,
        3,
        nullopt,
        5,
        4
    };

    cout << "Missing rate: "
         << missingRate(missingExample)
         << "%\n";

    // -------------------------------------------------------------------------
    // N. Confidence interval.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "APPROXIMATE CONFIDENCE INTERVAL\n";
    cout << string(78, '-') << '\n';

    /*
     * This example uses a simple proportion interval. It illustrates sampling
     * uncertainty but does not correct for nonresponse, coverage error,
     * clustering, stratification weights, or measurement error.
     */
    auto interval =
        proportionConfidenceInterval(
            0.60,
            400
        );

    cout << "Estimated proportion: 60%\n";
    cout << "Approximate 95% interval: "
         << interval.first * 100.0
         << "% to "
         << interval.second * 100.0
         << "%\n";

    // -------------------------------------------------------------------------
    // O. Cluster sampling design effect.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "CLUSTER DESIGN EFFECT\n";
    cout << string(78, '-') << '\n';

    double deff =
        designEffect(
            10.0,
            0.10
        );

    cout << "Average cluster size: 10\n";
    cout << "Intraclass correlation: 0.10\n";
    cout << "Approximate design effect: "
         << deff << '\n';

    // -------------------------------------------------------------------------
    // P. Platform mapping.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "FORM-BUILDER DESIGN MAPPING\n";
    cout << string(78, '-') << '\n';

    cout << "Google Forms commonly supports:\n";
    cout << "  - Required questions\n";
    cout << "  - Sections\n";
    cout << "  - Choice questions\n";
    cout << "  - Linear scales\n";
    cout << "  - Grid questions\n";
    cout << "  - Response collection and spreadsheet workflows\n";

    cout << "\nTypeform commonly emphasizes:\n";
    cout << "  - One-question-at-a-time interaction\n";
    cout << "  - Conditional logic\n";
    cout << "  - Branching\n";
    cout << "  - Question piping\n";
    cout << "  - Interactive respondent flows\n";

    // -------------------------------------------------------------------------
    // Q. Security and privacy.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "SECURITY AND PRIVACY CONTROLS\n";
    cout << string(78, '-') << '\n';

    vector<string> securityControls = {
        "Collect only information required for the research objective.",
        "Protect raw respondent data with access controls.",
        "Use encrypted transport for online submissions.",
        "Separate direct identifiers from analytical datasets where practical.",
        "Do not expose respondent-level data through public dashboards.",
        "Validate responses on the server as well as in the browser.",
        "Treat free-text responses as potentially sensitive.",
        "Define retention and deletion rules.",
        "Review third-party form platform privacy and data-processing settings."
    };

    for (const auto& control : securityControls) {
        cout << "- " << control << '\n';
    }

    // -------------------------------------------------------------------------
    // R. Architectural interpretation.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "ARCHITECTURAL INTERPRETATION\n";
    cout << string(78, '-') << '\n';

    cout
        << "1. Objective layer: defines what decision or research question is measured.\n"
        << "2. Population layer: defines who the conclusions concern.\n"
        << "3. Sampling layer: defines how observations are selected.\n"
        << "4. Instrument layer: defines questions and measurement scales.\n"
        << "5. Logic layer: determines which questions respondents see.\n"
        << "6. Validation layer: checks structural correctness of responses.\n"
        << "7. Quality layer: identifies potential low-quality observations.\n"
        << "8. Cleaning layer: prepares data for analysis.\n"
        << "9. Analysis layer: calculates descriptive statistics and indicators.\n"
        << "10. Governance layer: protects respondent data and documents limitations.\n";

    // -------------------------------------------------------------------------
    // S. Important limitations.
    // -------------------------------------------------------------------------

    cout << '\n' << string(78, '-') << '\n';
    cout << "CASE-STUDY LIMITATIONS\n";
    cout << string(78, '-') << '\n';

    vector<string> limitations = {
        "The population is simulated rather than a real customer database.",
        "The response set is intentionally small for demonstration.",
        "No nonresponse adjustment is implemented.",
        "The confidence interval is an educational approximation.",
        "No weighting estimator is implemented.",
        "No causal inference is justified by these survey responses.",
        "Automated quality flags are not proof that a respondent acted improperly.",
        "A form builder does not eliminate sampling or measurement bias."
    };

    for (const auto& limitation : limitations) {
        cout << "- " << limitation << '\n';
    }

    cout << '\n' << string(78, '=') << '\n';
    cout << "CASE STUDY EXECUTION COMPLETE\n";
    cout << string(78, '=') << '\n';

    return 0;
}
