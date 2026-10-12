#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Repository-independent product requirements governance engine.
 *
 * Case study: a regulated procurement platform requires requirements to be
 * traceable, measurable, dependency-safe, reviewed, and verified before release.
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic prd_governance.cpp -o prd_governance
 *
 * The engine deliberately distinguishes document completeness, requirement
 * approval, acceptance verification, and release readiness.
 */

enum class Priority { Must, Should, Could, Wont };
enum class State { Draft, InReview, Approved, Implemented, Verified, Rejected };
enum class RiskLevel { Low, Medium, High, Critical };

std::string toString(Priority priority) {
    switch (priority) {
        case Priority::Must: return "Must";
        case Priority::Should: return "Should";
        case Priority::Could: return "Could";
        case Priority::Wont: return "Won't";
    }
    throw std::logic_error("Unknown priority");
}

std::string toString(State state) {
    switch (state) {
        case State::Draft: return "Draft";
        case State::InReview: return "In Review";
        case State::Approved: return "Approved";
        case State::Implemented: return "Implemented";
        case State::Verified: return "Verified";
        case State::Rejected: return "Rejected";
    }
    throw std::logic_error("Unknown requirement state");
}

std::string toString(RiskLevel level) {
    switch (level) {
        case RiskLevel::Low: return "Low";
        case RiskLevel::Medium: return "Medium";
        case RiskLevel::High: return "High";
        case RiskLevel::Critical: return "Critical";
    }
    throw std::logic_error("Unknown risk level");
}

struct AcceptanceCriterion {
    std::string id;
    std::string given;
    std::string when;
    std::string then;

    std::vector<std::string> validate() const {
        std::vector<std::string> errors;
        if (id.empty()) errors.push_back("Acceptance criterion ID is required.");
        if (given.empty()) errors.push_back(id + ": Given condition is required.");
        if (when.empty()) errors.push_back(id + ": When action is required.");
        if (then.empty()) errors.push_back(id + ": Then outcome is required.");
        return errors;
    }
};

struct Requirement {
    std::string id;
    std::string title;
    std::string description;
    std::string rationale;
    std::string owner;
    Priority priority;
    State state = State::Draft;
    std::vector<std::string> dependencies;
    std::vector<AcceptanceCriterion> criteria;
};

struct Risk {
    std::string id;
    std::string description;
    int probability;
    int impact;
    std::string mitigation;
    std::string contingency;

    int score() const {
        return probability * impact;
    }

    RiskLevel level() const {
        const int value = score();
        if (value >= 20) return RiskLevel::Critical;
        if (value >= 12) return RiskLevel::High;
        if (value >= 6) return RiskLevel::Medium;
        return RiskLevel::Low;
    }

    void validate() const {
        if (probability < 1 || probability > 5 ||
            impact < 1 || impact > 5) {
            throw std::invalid_argument(
                id + ": probability and impact must be between 1 and 5"
            );
        }
        if (description.empty() || mitigation.empty() || contingency.empty()) {
            throw std::invalid_argument(
                id + ": risk description, mitigation, and contingency are required"
            );
        }
    }
};

class RequirementsEngine {
private:
    std::unordered_map<std::string, Requirement> requirements_;
    std::vector<Risk> risks_;
    std::vector<std::string> auditLog_;

    static bool isAllowedTransition(State from, State to) {
        switch (from) {
            case State::Draft:
                return to == State::InReview;
            case State::InReview:
                return to == State::Draft ||
                       to == State::Approved ||
                       to == State::Rejected;
            case State::Approved:
                return to == State::InReview || to == State::Implemented;
            case State::Implemented:
                return to == State::InReview || to == State::Verified;
            case State::Verified:
                return to == State::InReview;
            case State::Rejected:
                return to == State::Draft;
        }
        return false;
    }

    void log(const std::string& message) {
        auditLog_.push_back(message);
    }

    void transition(const std::string& id, State next, const std::string& actor) {
        auto it = requirements_.find(id);
        if (it == requirements_.end()) {
            throw std::invalid_argument("Unknown requirement: " + id);
        }
        if (actor.empty()) {
            throw std::invalid_argument("Workflow actor cannot be empty.");
        }
        if (!isAllowedTransition(it->second.state, next)) {
            throw std::logic_error(
                "Invalid transition for " + id + ": " +
                toString(it->second.state) + " -> " + toString(next)
            );
        }

        const State previous = it->second.state;
        it->second.state = next;
        log(actor + " changed " + id + " from " +
            toString(previous) + " to " + toString(next));
    }

    void ensureDependenciesReady(const Requirement& requirement) const {
        for (const auto& dependencyId : requirement.dependencies) {
            auto dependency = requirements_.find(dependencyId);
            if (dependency == requirements_.end()) {
                throw std::invalid_argument(
                    requirement.id + " references unknown dependency " + dependencyId
                );
            }
            const State state = dependency->second.state;
            if (state != State::Approved &&
                state != State::Implemented &&
                state != State::Verified) {
                throw std::logic_error(
                    "Dependency " + dependencyId + " is not approved."
                );
            }
        }
    }

    bool hasDependencyCycle() const {
        enum class Mark { Visiting, Visited };
        std::unordered_map<std::string, Mark> marks;

        // Depth-first search detects back edges without enumerating every
        // possible dependency path. Complexity is O(V + E).
        auto visit = [&](auto&& self, const std::string& id) -> bool {
            auto mark = marks.find(id);
            if (mark != marks.end()) {
                return mark->second == Mark::Visiting;
            }

            marks[id] = Mark::Visiting;
            const auto& requirement = requirements_.at(id);
            for (const auto& dependency : requirement.dependencies) {
                if (requirements_.find(dependency) != requirements_.end() &&
                    self(self, dependency)) {
                    return true;
                }
            }
            marks[id] = Mark::Visited;
            return false;
        };

        for (const auto& entry : requirements_) {
            if (marks.find(entry.first) == marks.end() &&
                visit(visit, entry.first)) {
                return true;
            }
        }
        return false;
    }

public:
    void addRequirement(Requirement requirement) {
        if (requirement.id.empty() || requirement.title.empty() ||
            requirement.description.empty() || requirement.rationale.empty() ||
            requirement.owner.empty()) {
            throw std::invalid_argument(
                "Requirement ID, title, description, rationale, and owner are required."
            );
        }
        if (requirement.criteria.empty()) {
            throw std::invalid_argument(
                requirement.id + " needs at least one acceptance criterion."
            );
        }
        for (const auto& criterion : requirement.criteria) {
            const auto errors = criterion.validate();
            if (!errors.empty()) {
                throw std::invalid_argument(errors.front());
            }
        }

        const std::string id = requirement.id;
        if (!requirements_.emplace(id, std::move(requirement)).second) {
            throw std::invalid_argument("Duplicate requirement ID: " + id);
        }
        log("Created requirement " + id);
    }

    void addRisk(Risk risk) {
        risk.validate();
        const auto duplicate = std::find_if(
            risks_.begin(), risks_.end(),
            [&](const Risk& existing) { return existing.id == risk.id; }
        );
        if (duplicate != risks_.end()) {
            throw std::invalid_argument("Duplicate risk ID: " + risk.id);
        }
        risks_.push_back(std::move(risk));
    }

    void requestReview(const std::string& id, const std::string& actor) {
        const auto it = requirements_.find(id);
        if (it == requirements_.end()) {
            throw std::invalid_argument("Unknown requirement: " + id);
        }
        ensureDependenciesReady(it->second);
        transition(id, State::InReview, actor);
    }

    void approve(const std::string& id, const std::string& reviewer) {
        const auto it = requirements_.find(id);
        if (it == requirements_.end()) {
            throw std::invalid_argument("Unknown requirement: " + id);
        }
        if (reviewer == it->second.owner) {
            throw std::logic_error("Requirement owners cannot approve their own requirements.");
        }
        transition(id, State::Approved, reviewer);
    }

    void reject(const std::string& id, const std::string& reviewer,
                const std::string& reason) {
        if (reason.empty()) {
            throw std::invalid_argument("A rejection requires a reason.");
        }
        log("Rejection rationale for " + id + ": " + reason);
        transition(id, State::Rejected, reviewer);
    }

    void markImplemented(const std::string& id, const std::string& actor) {
        transition(id, State::Implemented, actor);
    }

    void verify(const std::string& id,
                const std::map<std::string, bool>& results,
                const std::string& tester) {
        const auto it = requirements_.find(id);
        if (it == requirements_.end()) {
            throw std::invalid_argument("Unknown requirement: " + id);
        }
        if (it->second.state != State::Implemented) {
            throw std::logic_error(
                "Acceptance testing requires an implemented requirement."
            );
        }

        std::set<std::string> expected;
        for (const auto& criterion : it->second.criteria) {
            expected.insert(criterion.id);
        }

        for (const auto& result : results) {
            if (expected.find(result.first) == expected.end()) {
                throw std::invalid_argument(
                    "Test result references unknown criterion " + result.first
                );
            }
        }

        std::vector<std::string> failed;
        for (const auto& criterionId : expected) {
            const auto result = results.find(criterionId);
            if (result == results.end() || !result->second) {
                failed.push_back(criterionId);
            }
        }

        if (!failed.empty()) {
            std::string message = "Acceptance verification failed:";
            for (const auto& id : failed) message += " " + id;
            log(tester + " failed acceptance tests for " + id);
            throw std::logic_error(message);
        }

        transition(id, State::Verified, tester);
    }

    bool documentValid(std::vector<std::string>& errors) const {
        for (const auto& entry : requirements_) {
            const auto& requirement = entry.second;
            for (const auto& dependency : requirement.dependencies) {
                if (requirements_.find(dependency) == requirements_.end()) {
                    errors.push_back(
                        requirement.id + " has unknown dependency " + dependency
                    );
                }
            }
        }
        if (hasDependencyCycle()) {
            errors.push_back("Requirement dependency graph contains a cycle.");
        }
        return errors.empty();
    }

    bool releaseReady() const {
        std::vector<std::string> errors;
        if (!documentValid(errors)) return false;

        // Only Must requirements block release. Lower priorities remain visible
        // but do not silently become mandatory release gates.
        for (const auto& entry : requirements_) {
            const auto& requirement = entry.second;
            if (requirement.priority == Priority::Must &&
                requirement.state != State::Verified) {
                return false;
            }
        }
        return true;
    }

    void printReport() const {
        std::vector<const Requirement*> ordered;
        for (const auto& entry : requirements_) {
            ordered.push_back(&entry.second);
        }
        std::sort(
            ordered.begin(), ordered.end(),
            [](const Requirement* left, const Requirement* right) {
                if (left->priority != right->priority) {
                    return static_cast<int>(left->priority) <
                           static_cast<int>(right->priority);
                }
                return left->id < right->id;
            }
        );

        std::cout << "\nRequirement register\n";
        for (const auto* requirement : ordered) {
            std::cout << requirement->id << " | "
                      << toString(requirement->priority) << " | "
                      << toString(requirement->state) << " | "
                      << requirement->title << '\n';
        }

        std::vector<Risk> sortedRisks = risks_;
        std::sort(
            sortedRisks.begin(), sortedRisks.end(),
            [](const Risk& left, const Risk& right) {
                return left.score() > right.score();
            }
        );

        std::cout << "\nRisk register\n";
        for (const auto& risk : sortedRisks) {
            std::cout << risk.id << " | score=" << risk.score()
                      << " | " << toString(risk.level())
                      << " | " << risk.description << '\n';
        }

        std::cout << "\nRelease ready: "
                  << (releaseReady() ? "yes" : "no") << '\n';
        std::cout << "\nAudit log\n";
        for (const auto& event : auditLog_) {
            std::cout << "- " << event << '\n';
        }
    }
};

int main() {
    try {
        RequirementsEngine engine;

        engine.addRequirement({
            "REQ-201",
            "Validate purchase requests",
            "Reject requests that omit required procurement fields.",
            "Complete requests reduce avoidable processing delays.",
            "Product Manager",
            Priority::Must,
            State::Draft,
            {},
            {
                {"AC-201-A",
                 "All mandatory fields are supplied",
                 "The requester submits the form",
                 "The service creates a uniquely identified request"},
                {"AC-201-B",
                 "The cost center is missing",
                 "The requester submits the form",
                 "The service rejects submission with a field-specific error"}
            }
        });

        engine.addRequirement({
            "REQ-202",
            "Route requests through approval policy",
            "Select an approver group using amount and cost-center rules.",
            "Purchases must follow delegated financial authority.",
            "Procurement Lead",
            Priority::Must,
            State::Draft,
            {"REQ-201"},
            {
                {"AC-202-A",
                 "A request matches an active policy",
                 "The routing service evaluates the request",
                 "The request receives the configured approval assignment"}
            }
        });

        engine.addRisk({
            "RISK-201",
            "Approval thresholds are outdated",
            4,
            5,
            "Require policy ownership and effective-date validation",
            "Hold unmatched requests for authorized manual resolution"
        });

        engine.addRisk({
            "RISK-202",
            "Supporting documents expose confidential information",
            3,
            5,
            "Enforce authorization, encryption, and retention controls",
            "Restrict access and initiate the security incident process"
        });

        engine.requestReview("REQ-201", "Product Manager");
        engine.approve("REQ-201", "Procurement Lead");
        engine.markImplemented("REQ-201", "Engineering Lead");
        engine.verify(
            "REQ-201",
            {{"AC-201-A", true}, {"AC-201-B", true}},
            "QA Lead"
        );

        engine.requestReview("REQ-202", "Procurement Lead");
        engine.approve("REQ-202", "Finance Lead");
        engine.markImplemented("REQ-202", "Engineering Lead");

        // A failed criterion must prevent verification and release readiness.
        try {
            engine.verify(
                "REQ-202",
                {{"AC-202-A", false}},
                "QA Lead"
            );
        } catch (const std::logic_error& error) {
            std::cout << "Expected acceptance-test failure: "
                      << error.what() << '\n';
        }

        engine.printReport();
    } catch (const std::exception& error) {
        std::cerr << "Governance error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
