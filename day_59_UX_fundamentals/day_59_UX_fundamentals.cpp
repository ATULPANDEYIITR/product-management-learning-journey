#include <algorithm>
#include <cmath>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

enum class Severity {
    Info,
    Minor,
    Major,
    Critical
};

enum class IssueType {
    UI,
    Usability,
    Accessibility,
    Interaction,
    InformationArchitecture
};

enum class ControlType {
    Button,
    Link,
    Input,
    Checkbox,
    Select
};

struct Control {
    std::string id;
    std::string accessibleName;
    ControlType type;
    bool keyboardReachable;
    bool visible;
};

struct Screen {
    std::string id;
    std::string title;
    std::vector<std::string> navigation;
    std::vector<Control> controls;
    std::string primaryAction;
    std::map<std::string, double> contrastRatios;
    std::vector<std::string> contentSections;
};

struct StatusCheck {
    std::string name;
    bool passed;
    bool required;
};

struct UXIssue {
    IssueType type;
    Severity severity;
    std::string screenId;
    std::string description;
    std::string recommendation;
};

struct TaskMeasurement {
    std::string name;
    bool completed;
    double durationSeconds;
    int steps;
    int errors;
};

struct UsabilityMetrics {
    double completionRate;
    double averageDuration;
    double errorRate;
};

class UXValidationException : public std::runtime_error {
public:
    explicit UXValidationException(const std::string& message)
        : std::runtime_error(message) {}
};

class UXGovernanceEngine {
private:
    static constexpr double NORMAL_TEXT_CONTRAST = 4.5;

    std::unordered_map<std::string, Screen> screens;
    std::vector<UXIssue> issues;

    static UXIssue makeIssue(
        IssueType type,
        Severity severity,
        const std::string& screen,
        const std::string& description,
        const std::string& recommendation
    ) {
        return {type, severity, screen, description, recommendation};
    }

public:
    void addScreen(Screen screen) {
        if (screen.id.empty() || screen.title.empty()) {
            throw UXValidationException("Screen requires an id and title.");
        }

        if (screens.contains(screen.id)) {
            throw UXValidationException("Duplicate screen: " + screen.id);
        }

        if (screen.controls.empty()) {
            throw UXValidationException("Screen requires at least one control.");
        }

        screens.emplace(screen.id, std::move(screen));
    }

    void evaluateInformationArchitecture() {
        for (const auto& [id, screen] : screens) {
            if (screen.navigation.size() > 7) {
                issues.push_back(makeIssue(
                    IssueType::InformationArchitecture,
                    Severity::Minor,
                    id,
                    "Primary navigation contains more than seven top-level destinations.",
                    "Group related destinations and reduce navigation breadth."
                ));
            }

            std::set<std::string> sectionNames(
                screen.contentSections.begin(),
                screen.contentSections.end()
            );

            if (sectionNames.size() != screen.contentSections.size()) {
                issues.push_back(makeIssue(
                    IssueType::InformationArchitecture,
                    Severity::Minor,
                    id,
                    "Content sections contain duplicate labels.",
                    "Use unique, meaningful labels for information groups."
                ));
            }
        }
    }

    void evaluateAccessibility() {
        for (const auto& [id, screen] : screens) {
            for (const auto& control : screen.controls) {
                if (control.accessibleName.empty()) {
                    issues.push_back(makeIssue(
                        IssueType::Accessibility,
                        Severity::Major,
                        id,
                        "Control '" + control.id + "' has no accessible name.",
                        "Provide a meaningful accessible name."
                    ));
                }

                if (!control.keyboardReachable) {
                    issues.push_back(makeIssue(
                        IssueType::Accessibility,
                        Severity::Critical,
                        id,
                        "Control '" + control.id + "' cannot be reached by keyboard.",
                        "Expose the control through the keyboard interaction model."
                    ));
                }
            }

            for (const auto& [token, ratio] : screen.contrastRatios) {
                if (ratio < NORMAL_TEXT_CONTRAST) {
                    issues.push_back(makeIssue(
                        IssueType::Accessibility,
                        Severity::Major,
                        id,
                        "Contrast token '" + token + "' has insufficient contrast.",
                        "Use a color combination with adequate contrast."
                    ));
                }
            }
        }
    }

    void evaluateInteraction() {
        for (const auto& [id, screen] : screens) {
            const auto action = std::find_if(
                screen.controls.begin(),
                screen.controls.end(),
                [&](const Control& control) {
                    return control.id == screen.primaryAction;
                }
            );

            if (action == screen.controls.end()) {
                issues.push_back(makeIssue(
                    IssueType::Interaction,
                    Severity::Major,
                    id,
                    "The declared primary action is not a real control.",
                    "Represent the primary task with an actionable control."
                ));
            }

            if (screen.contentSections.empty()) {
                issues.push_back(makeIssue(
                    IssueType::Usability,
                    Severity::Major,
                    id,
                    "No content grouping has been defined.",
                    "Establish a clear visual and semantic information hierarchy."
                ));
            }
        }
    }

    void evaluateUI() {
        std::set<std::string> primaryActions;

        for (const auto& [id, screen] : screens) {
            primaryActions.insert(screen.primaryAction);
        }

        if (primaryActions.size() > 1) {
            issues.push_back(makeIssue(
                IssueType::UI,
                Severity::Minor,
                "*",
                "Primary-action labels vary between screens.",
                "Standardize action terminology according to user intent."
            ));
        }
    }

    std::vector<UXIssue> runAudit() {
        issues.clear();

        evaluateInformationArchitecture();
        evaluateAccessibility();
        evaluateInteraction();
        evaluateUI();

        return issues;
    }

    static UsabilityMetrics calculateMetrics(
        const std::vector<TaskMeasurement>& tasks
    ) {
        if (tasks.empty()) {
            return {0.0, 0.0, 0.0};
        }

        double duration = 0.0;
        int completed = 0;
        int totalSteps = 0;
        int totalErrors = 0;

        for (const auto& task : tasks) {
            if (task.durationSeconds < 0.0) {
                throw UXValidationException("Negative task duration.");
            }

            if (task.steps <= 0 || task.errors < 0 || task.errors > task.steps) {
                throw UXValidationException("Invalid task measurement.");
            }

            duration += task.durationSeconds;
            completed += task.completed ? 1 : 0;
            totalSteps += task.steps;
            totalErrors += task.errors;
        }

        return {
            static_cast<double>(completed) / tasks.size(),
            duration / tasks.size(),
            static_cast<double>(totalErrors) / std::max(totalSteps, 1)
        };
    }

    const std::unordered_map<std::string, Screen>& getScreens() const {
        return screens;
    }
};

std::string severityToString(Severity severity) {
    switch (severity) {
        case Severity::Info: return "INFO";
        case Severity::Minor: return "MINOR";
        case Severity::Major: return "MAJOR";
        case Severity::Critical: return "CRITICAL";
    }

    return "UNKNOWN";
}

std::string issueTypeToString(IssueType type) {
    switch (type) {
        case IssueType::UI: return "UI";
        case IssueType::Usability: return "USABILITY";
        case IssueType::Accessibility: return "ACCESSIBILITY";
        case IssueType::Interaction: return "INTERACTION";
        case IssueType::InformationArchitecture: return "INFORMATION_ARCHITECTURE";
    }

    return "UNKNOWN";
}

void printAudit(const std::vector<UXIssue>& issues) {
    std::cout << "\n=== UX AUDIT ===\n";

    std::map<Severity, int> counts;

    for (const auto& issue : issues) {
        ++counts[issue.severity];

        std::cout
            << '[' << severityToString(issue.severity) << "] "
            << issueTypeToString(issue.type)
            << " [" << issue.screenId << "] "
            << issue.description << '\n'
            << "  Recommendation: "
            << issue.recommendation << '\n';
    }

    std::cout << "\nIssue counts:\n";
    std::cout << "Critical: " << counts[Severity::Critical] << '\n';
    std::cout << "Major:    " << counts[Severity::Major] << '\n';
    std::cout << "Minor:    " << counts[Severity::Minor] << '\n';
    std::cout << "Info:     " << counts[Severity::Info] << '\n';
}

int main() {
    try {
        UXGovernanceEngine engine;

        engine.addScreen({
            "dashboard",
            "Project Dashboard",
            {
                "Projects",
                "Reports",
                "Teams",
                "Activity",
                "Integrations",
                "Billing",
                "Settings",
                "Help"
            },
            {
                {"Search", "Search projects", ControlType::Input, true, true},
                {"Create project", "Create project", ControlType::Button, true, true},
                {"Open project", "Open project", ControlType::Link, true, true},
                {"Account menu", "Account menu", ControlType::Button, true, true}
            },
            "Create project",
            {
                {"body-text", 7.1},
                {"muted-text", 3.2},
                {"primary-button", 4.9}
            },
            {"Projects", "Recent activity"}
        });

        engine.addScreen({
            "settings",
            "Account Settings",
            {"Projects", "Settings"},
            {
                {"Account name", "Account name", ControlType::Input, true, true},
                {"Save", "Save settings", ControlType::Button, true, true},
                {"Delete account", "", ControlType::Button, false, true}
            },
            "Save",
            {
                {"body-text", 8.0},
                {"primary-button", 5.2}
            },
            {"Profile", "Security", "Account"}
        });

        const auto issues = engine.runAudit();
        printAudit(issues);

        const std::vector<TaskMeasurement> tasks = {
            {"Find project", true, 18.4, 5, 0},
            {"Create project", true, 31.7, 7, 1},
            {"Change account settings", false, 44.2, 8, 3}
        };

        const auto metrics = UXGovernanceEngine::calculateMetrics(tasks);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "\n=== USABILITY METRICS ===\n";
        std::cout
            << "Completion rate: "
            << metrics.completionRate * 100.0 << "%\n";
        std::cout
            << "Average task time: "
            << metrics.averageDuration << " seconds\n";
        std::cout
            << "Error rate: "
            << metrics.errorRate * 100.0 << "%\n";

        const auto criticalCount = std::count_if(
            issues.begin(),
            issues.end(),
            [](const UXIssue& issue) {
                return issue.severity == Severity::Critical;
            }
        );

        std::cout << "\nRelease gate:\n";

        if (criticalCount > 0) {
            std::cout
                << "BLOCKED: "
                << criticalCount
                << " critical accessibility issue(s) remain.\n";
        } else {
            std::cout
                << "PASS: no critical accessibility issues detected.\n";
        }

        std::cout
            << "\nDesign rule: proposed UI changes are evaluated separately "
            << "from interaction behavior, accessibility, information structure, "
            << "and usability evidence.\n";

        return criticalCount > 0 ? 2 : 0;
    }
    catch (const std::exception& exception) {
        std::cerr
            << "UX evaluation failed: "
            << exception.what()
            << '\n';
        return 1;
    }
}
