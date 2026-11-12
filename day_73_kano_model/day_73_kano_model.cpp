#include <algorithm>
#include <array>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class Response {
    Like,
    Expect,
    Neutral,
    Tolerate,
    Dislike
};

enum class Category {
    MustBe,
    Performance,
    Attractive,
    Indifferent,
    Reverse,
    Questionable
};

string toString(Category category) {
    switch (category) {
        case Category::MustBe: return "Must-be";
        case Category::Performance: return "Performance";
        case Category::Attractive: return "Attractive";
        case Category::Indifferent: return "Indifferent";
        case Category::Reverse: return "Reverse";
        case Category::Questionable: return "Questionable";
    }

    throw logic_error("Unknown category.");
}

string toString(Response response) {
    switch (response) {
        case Response::Like: return "Like";
        case Response::Expect: return "Expect";
        case Response::Neutral: return "Neutral";
        case Response::Tolerate: return "Tolerate";
        case Response::Dislike: return "Dislike";
    }

    throw logic_error("Unknown response.");
}

Category evaluate(Response functional, Response dysfunctional) {
    /*
     * Kano evaluation matrix.
     * Rows: functional responses.
     * Columns: dysfunctional responses.
     */
    static const array<array<Category, 5>, 5> matrix = {{
        {{
            Category::Questionable,
            Category::Reverse,
            Category::Reverse,
            Category::Reverse,
            Category::MustBe
        }},
        {{
            Category::Attractive,
            Category::Indifferent,
            Category::Indifferent,
            Category::Indifferent,
            Category::MustBe
        }},
        {{
            Category::Performance,
            Category::Indifferent,
            Category::Indifferent,
            Category::Indifferent,
            Category::MustBe
        }},
        {{
            Category::Performance,
            Category::Indifferent,
            Category::Indifferent,
            Category::Indifferent,
            Category::MustBe
        }},
        {{
            Category::Performance,
            Category::Performance,
            Category::Performance,
            Category::Performance,
            Category::Questionable
        }}
    }};

    return matrix.at(static_cast<size_t>(functional))
                 .at(static_cast<size_t>(dysfunctional));
}

struct CustomerResponse {
    string customerId;
    Response functional;
    Response dysfunctional;

    Category classification() const {
        return evaluate(functional, dysfunctional);
    }
};

struct Coefficients {
    double satisfaction = 0.0;
    double dissatisfaction = 0.0;
};

class Feature {
private:
    string id;
    string name;
    string description;
    vector<CustomerResponse> responses;

public:
    Feature(string featureId, string featureName, string featureDescription)
        : id(move(featureId)),
          name(move(featureName)),
          description(move(featureDescription)) {

        if (id.empty() || name.empty()) {
            throw invalid_argument("Feature ID and name are required.");
        }
    }

    void addResponse(const CustomerResponse& response) {
        if (response.customerId.empty()) {
            throw invalid_argument("Customer ID cannot be empty.");
        }

        auto duplicate = find_if(
            responses.begin(),
            responses.end(),
            [&](const CustomerResponse& existing) {
                return existing.customerId == response.customerId;
            }
        );

        if (duplicate != responses.end()) {
            throw invalid_argument("Duplicate customer response.");
        }

        responses.push_back(response);
    }

    map<Category, int> getCounts() const {
        map<Category, int> counts = {
            {Category::MustBe, 0},
            {Category::Performance, 0},
            {Category::Attractive, 0},
            {Category::Indifferent, 0},
            {Category::Reverse, 0},
            {Category::Questionable, 0}
        };

        for (const auto& response : responses) {
            ++counts[response.classification()];
        }

        return counts;
    }

    Category dominantCategory() const {
        if (responses.empty()) {
            throw logic_error("No responses available.");
        }

        auto counts = getCounts();

        const array<Category, 5> categories = {
            Category::MustBe,
            Category::Performance,
            Category::Attractive,
            Category::Indifferent,
            Category::Reverse
        };

        Category best = categories.front();
        int maximum = 0;

        for (Category category : categories) {
            if (counts[category] > maximum) {
                maximum = counts[category];
                best = category;
            }
        }

        return maximum == 0 ? Category::Questionable : best;
    }

    Coefficients calculateCoefficients() const {
        auto counts = getCounts();

        int attractive = counts[Category::Attractive];
        int performance = counts[Category::Performance];
        int mustBe = counts[Category::MustBe];
        int indifferent = counts[Category::Indifferent];

        int denominator =
            attractive + performance + mustBe + indifferent;

        if (denominator == 0) {
            return {};
        }

        return {
            static_cast<double>(attractive + performance) / denominator,
            -static_cast<double>(performance + mustBe) / denominator
        };
    }

    double questionableRate() const {
        if (responses.empty()) {
            return 0.0;
        }

        auto counts = getCounts();

        return static_cast<double>(
            counts[Category::Questionable]
        ) / responses.size();
    }

    string getId() const { return id; }
    string getName() const { return name; }
    size_t responseCount() const { return responses.size(); }
};

class GovernanceEngine {
private:
    map<string, Feature> features;

public:
    void registerFeature(Feature feature) {
        auto [iterator, inserted] = features.emplace(
            feature.getId(),
            move(feature)
        );

        if (!inserted) {
            throw invalid_argument("Feature already registered.");
        }
    }

    void submitResponse(
        const string& featureId,
        const CustomerResponse& response
    ) {
        auto iterator = features.find(featureId);

        if (iterator == features.end()) {
            throw out_of_range("Unknown feature ID.");
        }

        iterator->second.addResponse(response);
    }

    void generateReport() const {
        cout << "\nKANO CUSTOMER SATISFACTION REPORT\n";
        cout << string(90, '=') << '\n';

        struct Result {
            string name;
            Category category;
            Coefficients coefficients;
            double questionableRate;
        };

        vector<Result> results;

        for (const auto& [id, feature] : features) {
            if (feature.responseCount() == 0) {
                continue;
            }

            results.push_back({
                feature.getName(),
                feature.dominantCategory(),
                feature.calculateCoefficients(),
                feature.questionableRate()
            });
        }

        sort(
            results.begin(),
            results.end(),
            [](const Result& a, const Result& b) {
                return a.coefficients.dissatisfaction <
                       b.coefficients.dissatisfaction;
            }
        );

        cout << left
             << setw(24) << "Feature"
             << setw(17) << "Classification"
             << setw(15) << "Satisfaction"
             << setw(17) << "Dissatisfaction"
             << "Questionable\n";

        for (const auto& result : results) {
            cout << left
                 << setw(24) << result.name
                 << setw(17) << toString(result.category)
                 << setw(15) << fixed << setprecision(3)
                 << result.coefficients.satisfaction
                 << setw(17) << result.coefficients.dissatisfaction
                 << result.questionableRate << '\n';
        }
    }
};

int main() {
    try {
        GovernanceEngine engine;

        engine.registerFeature(
            Feature("F001", "Account Security", "Secure authentication")
        );

        engine.registerFeature(
            Feature("F002", "Application Speed", "Fast processing")
        );

        engine.registerFeature(
            Feature("F003", "AI Recommendations", "Personalized suggestions")
        );

        engine.registerFeature(
            Feature("F004", "Custom Dashboard", "User configuration")
        );

        const map<string, vector<CustomerResponse>> dataset = {
            {"F001", {
                {"C001", Response::Like, Response::Dislike},
                {"C002", Response::Expect, Response::Dislike},
                {"C003", Response::Like, Response::Dislike},
                {"C004", Response::Neutral, Response::Dislike}
            }},
            {"F002", {
                {"C001", Response::Like, Response::Dislike},
                {"C002", Response::Like, Response::Neutral},
                {"C003", Response::Like, Response::Dislike},
                {"C004", Response::Expect, Response::Dislike}
            }},
            {"F003", {
                {"C001", Response::Expect, Response::Dislike},
                {"C002", Response::Expect, Response::Dislike},
                {"C003", Response::Like, Response::Dislike},
                {"C004", Response::Neutral, Response::Neutral}
            }},
            {"F004", {
                {"C001", Response::Neutral, Response::Neutral},
                {"C002", Response::Expect, Response::Neutral},
                {"C003", Response::Neutral, Response::Tolerate}
            }}
        };

        for (const auto& [featureId, responses] : dataset) {
            for (const auto& response : responses) {
                engine.submitResponse(featureId, response);
            }
        }

        engine.generateReport();

        // Verify matrix behavior.
        if (evaluate(Response::Like, Response::Dislike)
            != Category::MustBe) {
            throw logic_error("Kano matrix validation failed.");
        }

        // Verify duplicate protection.
        try {
            engine.submitResponse(
                "F001",
                {"C001", Response::Like, Response::Dislike}
            );

            throw logic_error("Duplicate validation failed.");
        } catch (const invalid_argument&) {
            cout << "\nDuplicate response correctly rejected.\n";
        }

        cout << "All validation checks passed.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
