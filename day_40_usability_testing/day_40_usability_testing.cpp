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
#include <vector>

/*
 * Repository-style usability case study: an enterprise procurement portal.
 *
 * The research team must decide whether a redesigned supplier discovery,
 * quotation comparison, and request submission workflow is usable enough
 * for release. This program models task evidence, participant outcomes,
 * severity-based findings, and release-oriented iteration decisions.
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic usability_testing.cpp -o usability_testing
 */

enum class Outcome {
    Success,
    Partial,
    Failure,
    Abandoned
};

enum class Severity {
    Cosmetic = 1,
    Minor = 2,
    Major = 3,
    Critical = 4
};

enum class EvidenceKind {
    Observed,
    ParticipantReported,
    Inferred
};

std::string toString(Outcome outcome) {
    switch (outcome) {
        case Outcome::Success: return "success";
        case Outcome::Partial: return "partial";
        case Outcome::Failure: return "failure";
        case Outcome::Abandoned: return "abandoned";
    }
    throw std::logic_error("Unknown outcome.");
}

std::string toString(Severity severity) {
    switch (severity) {
        case Severity::Cosmetic: return "cosmetic";
        case Severity::Minor: return "minor";
        case Severity::Major: return "major";
        case Severity::Critical: return "critical";
    }
    throw std::logic_error("Unknown severity.");
}

struct TaskDefinition {
    std::string id;
    std::string scenario;
    std::vector<std::string> successCriteria;
    double timeLimitSeconds;

    void validate() const {
        if (id.empty() || scenario.empty() || successCriteria.empty()) {
            throw std::invalid_argument(
                "Tasks need an ID, scenario, and observable success criteria."
            );
        }
        if (!std::isfinite(timeLimitSeconds) || timeLimitSeconds <= 0.0) {
            throw std::invalid_argument("Task time limit must be positive.");
        }
    }
};

struct Participant {
    std::string id;
    std::string role;
    std::string experience;
    bool consented;

    void validate() const {
        if (id.empty() || role.empty() || experience.empty()) {
            throw std::invalid_argument("Participant fields cannot be empty.");
        }
        if (!consented) {
            throw std::invalid_argument(
                "A participant cannot be enrolled without consent."
            );
        }
    }
};

struct Observation {
    double elapsedSeconds;
    std::string event;
    std::string target;
    std::string description;
    EvidenceKind evidenceKind;

    void validate() const {
        if (!std::isfinite(elapsedSeconds) || elapsedSeconds < 0.0) {
            throw std::invalid_argument("Observation time must be non-negative.");
        }
        if (event.empty() || target.empty() || description.empty()) {
            throw std::invalid_argument("Observation fields cannot be empty.");
        }
    }
};

struct TaskResult {
    std::string participantId;
    std::string taskId;
    Outcome outcome;
    double durationSeconds;
    int errors;
    int assistanceRequests;
    std::optional<int> confidence;
    std::vector<Observation> observations;

    void validate() const {
        if (participantId.empty() || taskId.empty()) {
            throw std::invalid_argument("Task result identifiers are required.");
        }
        if (!std::isfinite(durationSeconds) || durationSeconds < 0.0) {
            throw std::invalid_argument("Duration must be non-negative.");
        }
        if (errors < 0 || assistanceRequests < 0) {
            throw std::invalid_argument("Counts cannot be negative.");
        }
        if (confidence && (*confidence < 1 || *confidence > 5)) {
            throw std::invalid_argument("Confidence must be between one and five.");
        }
        for (const auto& observation : observations) {
            observation.validate();
        }
    }
};

struct UsabilityProblem {
    std::string id;
    std::string title;
    std::string description;
    Severity severity;
    std::set<std::string> affectedTasks;
    int participantFrequency;
    double impact;
    std::vector<std::string> evidence;
    std::string proposedChange;

    void validate(const std::set<std::string>& knownTasks) const {
        if (id.empty() || title.empty() || description.empty() ||
            proposedChange.empty()) {
            throw std::invalid_argument("Problem fields cannot be empty.");
        }
        if (affectedTasks.empty()) {
            throw std::invalid_argument("A problem must affect a task.");
        }
        for (const auto& taskId : affectedTasks) {
            if (!knownTasks.count(taskId)) {
                throw std::invalid_argument("Problem references an unknown task.");
            }
        }
        if (participantFrequency < 0) {
            throw std::invalid_argument("Frequency cannot be negative.");
        }
        if (!std::isfinite(impact) || impact < 0.0 || impact > 1.0) {
            throw std::invalid_argument("Impact must be between zero and one.");
        }
        if (evidence.empty()) {
            throw std::invalid_argument("A finding requires supporting evidence.");
        }
    }

    double priorityScore() const {
        return static_cast<int>(severity) *
               std::log1p(participantFrequency) * impact;
    }
};

struct TaskMetrics {
    std::string taskId;
    std::size_t participantCount = 0;
    double successRate = 0.0;
    double partialOrSuccessRate = 0.0;
    std::optional<double> medianDuration;
    double meanErrors = 0.0;
    double assistanceRate = 0.0;
};

class GovernanceWorkbench {
private:
    std::map<std::string, TaskDefinition> tasks_;
    std::map<std::string, Participant> participants_;
    std::vector<TaskResult> results_;
    std::map<std::string, UsabilityProblem> problems_;

public:
    void addTask(const TaskDefinition& task) {
        task.validate();
        if (!tasks_.emplace(task.id, task).second) {
            throw std::invalid_argument("Duplicate task ID: " + task.id);
        }
    }

    void addParticipant(const Participant& participant) {
        participant.validate();
        if (!participants_.emplace(participant.id, participant).second) {
            throw std::invalid_argument(
                "Duplicate participant ID: " + participant.id
            );
        }
    }

    void recordResult(const TaskResult& result) {
        result.validate();

        if (!participants_.count(result.participantId)) {
            throw std::invalid_argument("Unknown participant.");
        }
        if (!tasks_.count(result.taskId)) {
            throw std::invalid_argument("Unknown task.");
        }

        const auto duplicate = std::find_if(
            results_.begin(), results_.end(),
            [&](const TaskResult& existing) {
                return existing.participantId == result.participantId &&
                       existing.taskId == result.taskId;
            }
        );
        if (duplicate != results_.end()) {
            throw std::invalid_argument(
                "A participant cannot have duplicate final task results."
            );
        }

        results_.push_back(result);
    }

    void addProblem(const UsabilityProblem& problem) {
        std::set<std::string> taskIds;
        for (const auto& item : tasks_) taskIds.insert(item.first);

        problem.validate(taskIds);
        if (!problems_.emplace(problem.id, problem).second) {
            throw std::invalid_argument("Duplicate problem ID: " + problem.id);
        }
    }

    TaskMetrics metricsFor(const std::string& taskId) const {
        if (!tasks_.count(taskId)) {
            throw std::invalid_argument("Unknown task: " + taskId);
        }

        std::vector<double> durations;
        TaskMetrics metrics;
        metrics.taskId = taskId;
        int successes = 0;
        int partialOrSuccess = 0;
        int totalErrors = 0;
        int assisted = 0;

        for (const auto& result : results_) {
            if (result.taskId != taskId) continue;

            ++metrics.participantCount;
            totalErrors += result.errors;
            if (result.assistanceRequests > 0) ++assisted;

            if (result.outcome == Outcome::Success) {
                ++successes;
                durations.push_back(result.durationSeconds);
            }
            if (result.outcome == Outcome::Success ||
                result.outcome == Outcome::Partial) {
                ++partialOrSuccess;
            }
        }

        if (metrics.participantCount == 0) return metrics;

        metrics.successRate =
            static_cast<double>(successes) / metrics.participantCount;
        metrics.partialOrSuccessRate =
            static_cast<double>(partialOrSuccess) / metrics.participantCount;
        metrics.meanErrors =
            static_cast<double>(totalErrors) / metrics.participantCount;
        metrics.assistanceRate =
            static_cast<double>(assisted) / metrics.participantCount;

        if (!durations.empty()) {
            std::sort(durations.begin(), durations.end());
            const std::size_t middle = durations.size() / 2;
            if (durations.size() % 2 == 0) {
                metrics.medianDuration =
                    (durations[middle - 1] + durations[middle]) / 2.0;
            } else {
                metrics.medianDuration = durations[middle];
            }
        }
        return metrics;
    }

    std::vector<UsabilityProblem> prioritizedProblems() const {
        std::vector<UsabilityProblem> ordered;
        for (const auto& item : problems_) ordered.push_back(item.second);

        std::sort(
            ordered.begin(), ordered.end(),
            [](const UsabilityProblem& left, const UsabilityProblem& right) {
                if (left.priorityScore() != right.priorityScore()) {
                    return left.priorityScore() > right.priorityScore();
                }
                return left.id < right.id;
            }
        );
        return ordered;
    }

    const std::map<std::string, TaskDefinition>& tasks() const {
        return tasks_;
    }
};

void printMetrics(const TaskMetrics& metrics) {
    std::cout << std::left << std::setw(25) << metrics.taskId
              << std::right << std::setw(5) << metrics.participantCount
              << std::setw(12) << std::fixed << std::setprecision(1)
              << metrics.successRate * 100.0 << "%"
              << std::setw(12) << metrics.partialOrSuccessRate * 100.0 << "%"
              << std::setw(12);

    if (metrics.medianDuration) {
        std::cout << *metrics.medianDuration;
    } else {
        std::cout << "N/A";
    }

    std::cout << std::setw(12) << metrics.meanErrors
              << std::setw(12) << metrics.assistanceRate * 100.0 << "%\n";
}

GovernanceWorkbench buildCaseStudy() {
    GovernanceWorkbench workbench;

    workbench.addTask({
        "supplier-search",
        "Find an electrical supplier with active approval.",
        {
            "Supplier selected",
            "Active approval verified",
            "Electrical category verified"
        },
        240.0
    });

    workbench.addTask({
        "quotation-review",
        "Choose the lowest-priced quotation that satisfies the specification.",
        {
            "Quotations compared",
            "Compliance verified",
            "Correct offer selected"
        },
        300.0
    });

    workbench.addTask({
        "request-submit",
        "Submit a request and verify its reference number.",
        {
            "Quantity validated",
            "Request submitted",
            "Confirmation verified"
        },
        360.0
    });

    const std::vector<Participant> participants = {
        {"P201", "Procurement officer", "frequent", true},
        {"P202", "Purchase analyst", "occasional", true},
        {"P203", "Vendor manager", "frequent", true},
        {"P204", "Department coordinator", "occasional", true}
    };
    for (const auto& participant : participants) {
        workbench.addParticipant(participant);
    }

    // Separate observations from interpretations so analysts can revisit
    // the evidence when a proposed fix does not improve the next iteration.
    workbench.recordResult({
        "P201", "supplier-search", Outcome::Success, 72.0, 0, 0, 5,
        {
            {10.0, "filter_opened", "approval-filter",
             "Opened the supplier approval filter.", EvidenceKind::Observed},
            {35.0, "supplier_selected", "supplier-row",
             "Selected a supplier with active approval.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P202", "supplier-search", Outcome::Failure, 240.0, 3, 1, 2,
        {
            {25.0, "wrong_selection", "supplier-row",
             "Selected a supplier with pending approval.", EvidenceKind::Observed},
            {110.0, "assistance", "moderator",
             "Asked how to distinguish approval states.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P203", "supplier-search", Outcome::Success, 88.0, 1, 0, 4,
        {
            {22.0, "search", "supplier-search",
             "Used a category term in the search field.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P204", "supplier-search", Outcome::Partial, 180.0, 2, 1, 3,
        {
            {40.0, "filter_confusion", "approval-filter",
             "Changed the filter repeatedly before choosing a supplier.",
             EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P201", "quotation-review", Outcome::Partial, 160.0, 2, 0, 3,
        {
            {25.0, "sort", "unit-price",
             "Sorted by price before checking compliance.", EvidenceKind::Observed},
            {85.0, "wrong_selection", "quotation-row",
             "Selected a low-priced non-compliant offer.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P202", "quotation-review", Outcome::Failure, 300.0, 4, 2, 2,
        {
            {75.0, "comparison_confusion", "compliance-column",
             "Could not determine which offers met the specification.",
             EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P203", "quotation-review", Outcome::Success, 130.0, 1, 0, 5,
        {
            {90.0, "compliance_check", "specification-details",
             "Opened the specification before selecting an offer.",
             EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P204", "quotation-review", Outcome::Success, 145.0, 1, 0, 4,
        {
            {65.0, "comparison", "quotation-table",
             "Compared compliance and total cost.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P201", "request-submit", Outcome::Success, 165.0, 1, 0, 5,
        {
            {100.0, "confirmation", "submission-banner",
             "Read the submitted confirmation.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P202", "request-submit", Outcome::Failure, 360.0, 4, 2, 2,
        {
            {180.0, "repeated_submission", "submit-button",
             "Repeated submission after ambiguous feedback.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P203", "request-submit", Outcome::Success, 190.0, 1, 0, 4,
        {
            {150.0, "history_check", "request-history",
             "Used request history to verify submission.", EvidenceKind::Observed}
        }
    });

    workbench.recordResult({
        "P204", "request-submit", Outcome::Success, 175.0, 1, 0, 4,
        {
            {120.0, "validation", "quantity-field",
             "Corrected quantity after inline validation.", EvidenceKind::Observed}
        }
    });

    workbench.addProblem({
        "UX-301",
        "Supplier approval status is ambiguous",
        "A pending supplier can be mistaken for an approved supplier.",
        Severity::Critical,
        {"supplier-search"},
        2,
        0.95,
        {
            "Observed selection of a supplier with pending approval.",
            "Observed repeated confusion with the approval filter."
        },
        "Use explicit Active, Pending, and Expired labels with an approved-only filter."
    });

    workbench.addProblem({
        "UX-302",
        "Quotation price is visually separated from compliance",
        "A low raw price can be selected before specification compliance is checked.",
        Severity::Critical,
        {"quotation-review"},
        2,
        0.90,
        {
            "Observed selection of a non-compliant low-priced quotation.",
            "Observed difficulty identifying compliant offers."
        },
        "Show compliance status and total cost together; identify the lowest compliant offer."
    });

    workbench.addProblem({
        "UX-303",
        "Request submission state is unclear",
        "Users may repeat a submission when the resulting state is ambiguous.",
        Severity::Major,
        {"request-submit"},
        1,
        0.80,
        {
            "Observed repeated submission after unclear feedback."
        },
        "Display a durable confirmation with a unique request reference."
    });

    return workbench;
}

void runValidationChecks() {
    std::cout << "\nVALIDATION CHECKS\n";

    bool rejected = false;
    try {
        TaskDefinition invalid{"", "", {}, -1.0};
        invalid.validate();
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    if (!rejected) throw std::runtime_error("Invalid task was accepted.");

    rejected = false;
    try {
        Participant unconsented{"P-X", "Analyst", "new", false};
        unconsented.validate();
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    if (!rejected) throw std::runtime_error("Unconsented participant was accepted.");

    std::cout << "Invalid tasks and unconsented enrollment were rejected.\n";
}

int main() {
    try {
        GovernanceWorkbench workbench = buildCaseStudy();

        std::cout << "PROCUREMENT PORTAL USABILITY STUDY\n";
        std::cout << "TASK METRICS\n";
        std::cout << std::left << std::setw(25) << "Task"
                  << std::right << std::setw(5) << "N"
                  << std::setw(12) << "Success"
                  << std::setw(12) << "Partial+"
                  << std::setw(12) << "Median sec"
                  << std::setw(12) << "Mean errors"
                  << std::setw(12) << "Assisted" << '\n';

        for (const auto& task : workbench.tasks()) {
            printMetrics(workbench.metricsFor(task.first));
        }

        std::cout << "\nPRIORITIZED DESIGN FINDINGS\n";
        for (const auto& problem : workbench.prioritizedProblems()) {
            std::cout << problem.id << " | " << problem.title
                      << " | " << toString(problem.severity)
                      << " | score=" << std::fixed << std::setprecision(3)
                      << problem.priorityScore() << '\n';
            std::cout << "  Change: " << problem.proposedChange << '\n';
        }

        std::cout << "\nITERATION DECISION\n";
        const auto supplierMetrics = workbench.metricsFor("supplier-search");
        if (supplierMetrics.successRate < 0.80 ||
            supplierMetrics.assistanceRate > 0.20) {
            std::cout
                << "Supplier discovery requires redesign and a new moderated test.\n";
        } else {
            std::cout
                << "Supplier discovery meets the illustrative release threshold.\n";
        }

        std::cout
            << "A release decision must also consider task risk, qualitative evidence, "
            << "and organizational acceptance criteria.\n";

        runValidationChecks();
    } catch (const std::exception& error) {
        std::cerr << "Study execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
