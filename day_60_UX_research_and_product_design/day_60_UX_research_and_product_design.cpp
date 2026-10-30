#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class CritiqueSeverity {
    Low,
    Medium,
    High,
    Critical
};

struct Evidence {
    string id;
    string participantReference;
    string observation;
    int severity;
    double confidence;
};

struct Theme {
    string id;
    string name;
    vector<string> evidenceIds;
    double estimatedEffortHours;
};

struct Component {
    string name;
    bool interactive;
    bool keyboardAccessible;
    string accessibleDescription;
};

struct Screen {
    string id;
    string accessibleName;
    vector<string> componentOrder;
    vector<string> keyboardOrder;
    vector<string> requiredTokens;
};

struct UsabilityAttempt {
    string participantReference;
    string taskName;
    string screenId;
    bool succeeded;
    double durationSeconds;
    int criticalErrors;
};

struct Critique {
    string id;
    string screenId;
    string heuristic;
    CritiqueSeverity severity;
    string description;
    string recommendation;
    bool resolved;
};

struct ThemeScore {
    string themeName;
    size_t evidenceCount;
    double averageSeverity;
    double averageConfidence;
    double effortHours;
    double priorityScore;
};

struct QualityReport {
    bool eligible = false;
    vector<string> blockers;
    size_t evidenceCount = 0;
    size_t themeCount = 0;
    size_t screenCount = 0;
    size_t usabilityAttempts = 0;
    double taskSuccessRate = 0.0;
    double averageDurationSeconds = 0.0;
    int criticalErrors = 0;
};

class ValidationError : public runtime_error {
public:
    explicit ValidationError(const string& message)
        : runtime_error(message) {}
};

double channelToLinear(int channel) {
    const double value = static_cast<double>(channel) / 255.0;
    return value <= 0.04045
        ? value / 12.92
        : pow((value + 0.055) / 1.055, 2.4);
}

double luminance(const string& color) {
    if (color.size() != 7 || color[0] != '#') {
        throw ValidationError("Color must use the #RRGGBB format.");
    }

    auto parseChannel = [&color](size_t offset) {
        try {
            const int value = stoi(color.substr(offset, 2), nullptr, 16);
            return value;
        } catch (const exception&) {
            throw ValidationError("Invalid hexadecimal color: " + color);
        }
    };

    const double red = channelToLinear(parseChannel(1));
    const double green = channelToLinear(parseChannel(3));
    const double blue = channelToLinear(parseChannel(5));

    return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
}

double contrastRatio(const string& foreground, const string& background) {
    const double first = luminance(foreground);
    const double second = luminance(background);
    return (max(first, second) + 0.05) / (min(first, second) + 0.05);
}

class DesignSystem {
private:
    map<string, string> tokens;
    map<string, Component> components;
    vector<pair<string, string>> contrastPairs;

public:
    DesignSystem(
        map<string, string> tokenValues,
        map<string, Component> componentDefinitions,
        vector<pair<string, string>> pairs
    )
        : tokens(move(tokenValues)),
          components(move(componentDefinitions)),
          contrastPairs(move(pairs)) {}

    vector<string> validate() const {
        vector<string> errors;

        for (const auto& pair : contrastPairs) {
            const auto foreground = tokens.find(pair.first);
            const auto background = tokens.find(pair.second);

            if (foreground == tokens.end() || background == tokens.end()) {
                errors.push_back(
                    "Missing contrast pair: " + pair.first + "/" + pair.second
                );
                continue;
            }

            try {
                const double ratio = contrastRatio(
                    foreground->second,
                    background->second
                );
                if (ratio < 4.5) {
                    ostringstream message;
                    message << "Contrast below 4.5:1 for "
                            << pair.first << "/" << pair.second
                            << " (" << fixed << setprecision(2)
                            << ratio << ":1).";
                    errors.push_back(message.str());
                }
            } catch (const ValidationError& error) {
                errors.push_back(error.what());
            }
        }

        return errors;
    }

    vector<string> validateScreen(const Screen& screen) const {
        vector<string> errors;
        vector<string> expectedKeyboardOrder;

        if (screen.accessibleName.empty()) {
            errors.push_back(screen.id + ": accessible name is required.");
        }

        set<string> uniqueComponents;
        for (const string& name : screen.componentOrder) {
            if (!uniqueComponents.insert(name).second) {
                errors.push_back(screen.id + ": duplicate component " + name + ".");
                continue;
            }

            const auto component = components.find(name);
            if (component == components.end()) {
                errors.push_back(screen.id + ": unknown component " + name + ".");
                continue;
            }

            const Component& specification = component->second;

            if (!specification.keyboardAccessible) {
                errors.push_back(
                    screen.id + ": " + name + " is not keyboard accessible."
                );
            }
            if (specification.accessibleDescription.empty()) {
                errors.push_back(
                    screen.id + ": " + name + " lacks an accessible description."
                );
            }
            if (specification.interactive) {
                expectedKeyboardOrder.push_back(name);
            }
        }

        if (expectedKeyboardOrder != screen.keyboardOrder) {
            errors.push_back(
                screen.id + ": keyboard order differs from interactive layout order."
            );
        }

        for (const string& token : screen.requiredTokens) {
            if (tokens.find(token) == tokens.end()) {
                errors.push_back(screen.id + ": missing token " + token + ".");
            }
        }

        return errors;
    }
};

class UXQualityEngine {
private:
    map<string, Evidence> evidence;
    map<string, Theme> themes;
    map<string, Screen> screens;
    vector<UsabilityAttempt> usabilityAttempts;
    vector<Critique> critiques;
    DesignSystem designSystem;

    void requireText(const string& value, const string& field) const {
        if (value.empty()) {
            throw ValidationError(field + " cannot be empty.");
        }
    }

public:
    explicit UXQualityEngine(DesignSystem system)
        : designSystem(move(system)) {}

    void addEvidence(const Evidence& item) {
        requireText(item.id, "Evidence ID");
        requireText(item.participantReference, "Participant reference");
        requireText(item.observation, "Observation");

        if (item.severity < 1 || item.severity > 5) {
            throw ValidationError("Evidence severity must be between 1 and 5.");
        }
        if (!isfinite(item.confidence) || item.confidence < 0.0 ||
            item.confidence > 1.0) {
            throw ValidationError("Evidence confidence must be between 0 and 1.");
        }
        if (evidence.count(item.id)) {
            throw ValidationError("Duplicate evidence ID: " + item.id);
        }

        evidence.emplace(item.id, item);
    }

    void addTheme(const Theme& theme) {
        requireText(theme.id, "Theme ID");
        requireText(theme.name, "Theme name");

        if (themes.count(theme.id)) {
            throw ValidationError("Duplicate theme ID: " + theme.id);
        }
        if (theme.evidenceIds.empty() || theme.estimatedEffortHours <= 0.0) {
            throw ValidationError("Theme requires evidence and positive effort.");
        }

        set<string> uniqueIds;
        for (const string& id : theme.evidenceIds) {
            if (!evidence.count(id)) {
                throw ValidationError("Unknown evidence reference: " + id);
            }
            if (!uniqueIds.insert(id).second) {
                throw ValidationError("Duplicate evidence reference: " + id);
            }
        }

        themes.emplace(theme.id, theme);
    }

    vector<ThemeScore> synthesize() const {
        if (evidence.size() < 3 || themes.size() < 2) {
            throw ValidationError(
                "Synthesis requires at least three evidence records and two themes."
            );
        }

        vector<ThemeScore> scores;
        for (const auto& entry : themes) {
            const Theme& theme = entry.second;
            double severityTotal = 0.0;
            double confidenceTotal = 0.0;

            for (const string& id : theme.evidenceIds) {
                const Evidence& item = evidence.at(id);
                severityTotal += item.severity;
                confidenceTotal += item.confidence;
            }

            const double count = static_cast<double>(theme.evidenceIds.size());
            const double averageSeverity = severityTotal / count;
            const double averageConfidence = confidenceTotal / count;

            scores.push_back({
                theme.name,
                theme.evidenceIds.size(),
                averageSeverity,
                averageConfidence,
                theme.estimatedEffortHours,
                count * averageSeverity * averageConfidence /
                    theme.estimatedEffortHours
            });
        }

        sort(scores.begin(), scores.end(),
            [](const ThemeScore& first, const ThemeScore& second) {
                return first.priorityScore > second.priorityScore;
            });

        return scores;
    }

    void addScreen(const Screen& screen) {
        requireText(screen.id, "Screen ID");

        if (screens.count(screen.id)) {
            throw ValidationError("Duplicate screen ID: " + screen.id);
        }

        const vector<string> errors = designSystem.validateScreen(screen);
        if (!errors.empty()) {
            throw ValidationError(errors.front());
        }

        screens.emplace(screen.id, screen);
    }

    void addUsabilityAttempt(const UsabilityAttempt& attempt) {
        if (!screens.count(attempt.screenId)) {
            throw ValidationError("Attempt references an unknown screen.");
        }
        requireText(attempt.participantReference, "Participant reference");
        requireText(attempt.taskName, "Task name");

        if (attempt.durationSeconds <= 0.0 || attempt.criticalErrors < 0) {
            throw ValidationError("Invalid usability timing or error count.");
        }

        usabilityAttempts.push_back(attempt);
    }

    void addCritique(const Critique& critique) {
        if (!screens.count(critique.screenId)) {
            throw ValidationError("Critique references an unknown screen.");
        }
        requireText(critique.id, "Critique ID");
        requireText(critique.heuristic, "Heuristic");
        requireText(critique.description, "Description");
        requireText(critique.recommendation, "Recommendation");

        const auto duplicate = find_if(
            critiques.begin(), critiques.end(),
            [&critique](const Critique& current) {
                return current.id == critique.id;
            }
        );

        if (duplicate != critiques.end()) {
            throw ValidationError("Duplicate critique ID: " + critique.id);
        }

        critiques.push_back(critique);
    }

    QualityReport evaluate() const {
        QualityReport report;
        report.evidenceCount = evidence.size();
        report.themeCount = themes.size();
        report.screenCount = screens.size();
        report.usabilityAttempts = usabilityAttempts.size();

        if (evidence.size() < 5) {
            report.blockers.push_back("At least five research evidence records are required.");
        }
        if (themes.size() < 2) {
            report.blockers.push_back("At least two synthesized themes are required.");
        }
        if (screens.size() < 2) {
            report.blockers.push_back("At least two validated wireframe screens are required.");
        }
        if (usabilityAttempts.size() < 5) {
            report.blockers.push_back("At least five usability task attempts are required.");
        }

        int successful = 0;
        double totalDuration = 0.0;

        for (const UsabilityAttempt& attempt : usabilityAttempts) {
            successful += attempt.succeeded ? 1 : 0;
            totalDuration += attempt.durationSeconds;
            report.criticalErrors += attempt.criticalErrors;
        }

        if (!usabilityAttempts.empty()) {
            report.taskSuccessRate =
                static_cast<double>(successful) / usabilityAttempts.size();
            report.averageDurationSeconds =
                totalDuration / usabilityAttempts.size();
        }

        if (report.taskSuccessRate < 0.80) {
            report.blockers.push_back("Task success rate is below 80%.");
        }
        if (report.criticalErrors > 0) {
            report.blockers.push_back("Prototype testing contains critical errors.");
        }

        for (const auto& entry : screens) {
            const vector<string> errors =
                designSystem.validateScreen(entry.second);
            report.blockers.insert(
                report.blockers.end(), errors.begin(), errors.end()
            );
        }

        const vector<string> systemErrors = designSystem.validate();
        report.blockers.insert(
            report.blockers.end(), systemErrors.begin(), systemErrors.end()
        );

        for (const Critique& critique : critiques) {
            if (critique.severity == CritiqueSeverity::Critical &&
                !critique.resolved) {
                report.blockers.push_back(
                    "Unresolved critical critique: " + critique.id
                );
            }
        }

        report.eligible = report.blockers.empty();
        return report;
    }
};

string severityLabel(CritiqueSeverity severity) {
    switch (severity) {
        case CritiqueSeverity::Low: return "low";
        case CritiqueSeverity::Medium: return "medium";
        case CritiqueSeverity::High: return "high";
        case CritiqueSeverity::Critical: return "critical";
    }
    return "unknown";
}

int main() {
    try {
        map<string, string> tokens = {
            {"color.text", "#17212B"},
            {"color.surface", "#FFFFFF"},
            {"color.action", "#1247A8"},
            {"space.medium", "16px"}
        };

        map<string, Component> components = {
            {"SearchField", {"SearchField", true, true, "Origin and destination input"}},
            {"PrimaryButton", {"PrimaryButton", true, true, "Submit route search"}},
            {"RouteCard", {"RouteCard", true, true, "Selectable journey option"}}
        };

        DesignSystem designSystem(
            tokens,
            components,
            {
                {"color.text", "color.surface"},
                {"color.action", "color.surface"}
            }
        );

        UXQualityEngine engine(move(designSystem));

        const vector<Evidence> evidenceItems = {
            {"E01", "P-001", "Transfer requirements are unclear.", 5, 0.95},
            {"E02", "P-002", "Transfer points are difficult to identify.", 4, 0.90},
            {"E03", "P-003", "Users compare journeys by total time.", 3, 0.85},
            {"E04", "P-004", "The complete fare is difficult to locate.", 5, 0.95},
            {"E05", "P-005", "Fare presentation is inconsistent.", 4, 0.90},
            {"E06", "P-006", "Users need to compare fare categories.", 3, 0.85}
        };

        for (const Evidence& item : evidenceItems) {
            engine.addEvidence(item);
        }

        engine.addTheme({
            "T01", "Transfer uncertainty", {"E01", "E02", "E03"}, 8.0
        });
        engine.addTheme({
            "T02", "Fare transparency", {"E04", "E05", "E06"}, 5.0
        });

        cout << "RESEARCH SYNTHESIS\n";
        for (const ThemeScore& score : engine.synthesize()) {
            cout << fixed << setprecision(3)
                 << score.themeName
                 << " | evidence=" << score.evidenceCount
                 << " | severity=" << score.averageSeverity
                 << " | confidence=" << score.averageConfidence
                 << " | priority=" << score.priorityScore << '\n';
        }

        engine.addScreen({
            "S01",
            "Search for a public transport journey",
            {"SearchField", "PrimaryButton"},
            {"SearchField", "PrimaryButton"},
            {"color.text", "color.surface", "color.action"}
        });

        engine.addScreen({
            "S02",
            "Available journey options",
            {"RouteCard", "PrimaryButton"},
            {"RouteCard", "PrimaryButton"},
            {"color.text", "color.surface", "color.action"}
        });

        engine.addCritique({
            "C01",
            "S02",
            "Visibility of system status",
            CritiqueSeverity::Medium,
            "The selected route is not visually persistent.",
            "Provide a selected state and accessible announcement.",
            false
        });

        engine.addCritique({
            "C02",
            "S01",
            "Error prevention",
            CritiqueSeverity::Critical,
            "The early prototype accepted an empty origin.",
            "Validate the origin before route calculation.",
            true
        });

        const vector<UsabilityAttempt> attempts = {
            {"P-007", "Find fastest route", "S01", true, 62, 0},
            {"P-008", "Compare journey options", "S02", true, 75, 0},
            {"P-009", "Identify transfers", "S02", true, 81, 0},
            {"P-010", "Find complete fare", "S02", false, 110, 0},
            {"P-011", "Search return journey", "S01", true, 69, 0}
        };

        for (const UsabilityAttempt& attempt : attempts) {
            engine.addUsabilityAttempt(attempt);
        }

        const QualityReport report = engine.evaluate();

        cout << "\nDESIGN QUALITY REPORT\n";
        cout << "Eligible: " << (report.eligible ? "yes" : "no") << '\n';
        cout << "Evidence: " << report.evidenceCount << '\n';
        cout << "Themes: " << report.themeCount << '\n';
        cout << "Screens: " << report.screenCount << '\n';
        cout << "Usability attempts: " << report.usabilityAttempts << '\n';
        cout << fixed << setprecision(1)
             << "Task success rate: " << report.taskSuccessRate * 100.0 << "%\n"
             << "Average task duration: " << report.averageDurationSeconds << " seconds\n"
             << "Critical errors: " << report.criticalErrors << '\n';

        for (const string& blocker : report.blockers) {
            cout << "BLOCKER: " << blocker << '\n';
        }

        if (!report.eligible) {
            return 2;
        }

        // Invalid evidence is rejected instead of silently changing research metrics.
        bool invalidInputRejected = false;
        try {
            engine.addEvidence({"E99", "P-099", "Invalid severity.", 9, 0.9});
        } catch (const ValidationError&) {
            invalidInputRejected = true;
        }

        if (!invalidInputRejected) {
            throw runtime_error("Evidence validation test unexpectedly passed.");
        }

        return 0;
    } catch (const exception& error) {
        cerr << "UX quality workflow failed: " << error.what() << '\n';
        return 1;
    }
}
