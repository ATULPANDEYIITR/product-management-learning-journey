// File: cpp/src/journey_analyzer.cpp
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

struct Touchpoint {
    std::string channel;
    int sentiment;
    int effort;
};

struct Stage {
    std::string name;
    std::vector<Touchpoint> touchpoints;
};

class JourneyAnalyzer {
public:
    explicit JourneyAnalyzer(std::vector<Stage> stages)
        : stages_(std::move(stages)) {
        validate();
    }

    double averageSentiment() const {
        const auto points = allTouchpoints();

        if (points.empty()) {
            return 0.0;
        }

        const int total = std::accumulate(
            points.begin(),
            points.end(),
            0,
            [](int sum, const Touchpoint& point) {
                return sum + point.sentiment;
            }
        );

        return static_cast<double>(total) / points.size();
    }

    double averageEffort() const {
        const auto points = allTouchpoints();

        if (points.empty()) {
            return 0.0;
        }

        const int total = std::accumulate(
            points.begin(),
            points.end(),
            0,
            [](int sum, const Touchpoint& point) {
                return sum + point.effort;
            }
        );

        return static_cast<double>(total) / points.size();
    }

    std::map<std::string, int> channelFrequency() const {
        std::map<std::string, int> frequency;

        for (const auto& stage : stages_) {
            for (const auto& point : stage.touchpoints) {
                ++frequency[point.channel];
            }
        }

        return frequency;
    }

    void printReport() const {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Customer Journey Analysis\n";
        std::cout << "-------------------------\n";
        std::cout << "Average sentiment: " << averageSentiment() << "\n";
        std::cout << "Average effort: " << averageEffort() << "\n";
        std::cout << "Touchpoints: " << allTouchpoints().size() << "\n";

        std::cout << "\nChannel frequency:\n";

        for (const auto& [channel, count] : channelFrequency()) {
            std::cout << "  " << channel << ": " << count << "\n";
        }
    }

private:
    std::vector<Stage> stages_;

    std::vector<Touchpoint> allTouchpoints() const {
        std::vector<Touchpoint> points;

        for (const auto& stage : stages_) {
            points.insert(
                points.end(),
                stage.touchpoints.begin(),
                stage.touchpoints.end()
            );
        }

        return points;
    }

    void validate() const {
        if (stages_.empty()) {
            throw std::invalid_argument("A journey must contain at least one stage.");
        }

        for (const auto& stage : stages_) {
            if (stage.name.empty()) {
                throw std::invalid_argument("Stage names cannot be empty.");
            }

            for (const auto& point : stage.touchpoints) {
                if (point.channel.empty()) {
                    throw std::invalid_argument("Touchpoint channels cannot be empty.");
                }

                if (point.sentiment < -5 || point.sentiment > 5) {
                    throw std::invalid_argument(
                        "Sentiment must be between -5 and 5."
                    );
                }

                if (point.effort < 1 || point.effort > 5) {
                    throw std::invalid_argument(
                        "Effort must be between 1 and 5."
                    );
                }
            }
        }
    }
};

int main() {
    const std::vector<Stage> journey = {
        {
            "awareness",
            {
                {"Search", 3, 2},
                {"Social", 2, 2}
            }
        },
        {
            "consideration",
            {
                {"Website", 1, 3},
                {"Review site", 2, 4}
            }
        },
        {
            "purchase",
            {
                {"Checkout", -1, 4}
            }
        },
        {
            "onboarding",
            {
                {"Email", 2, 2}
            }
        },
        {
            "usage",
            {
                {"Application", 4, 2}
            }
        },
        {
            "retention",
            {
                {"Support", 3, 2}
            }
        },
        {
            "advocacy",
            {
                {"Referral", 5, 1}
            }
        }
    };

    try {
        JourneyAnalyzer analyzer(journey);
        analyzer.printReport();
    } catch (const std::exception& error) {
        std::cerr << "Analysis error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
