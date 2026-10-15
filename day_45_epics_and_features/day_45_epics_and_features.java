#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Repository-sized product delivery case study:
 * a platform team decomposes an enterprise audit product into epics,
 * features, stories, and engineering tasks.
 *
 * C++17 implementation emphasizes typed hierarchy rules, indexed lookup,
 * dependency graphs, aggregate progress, and release-gate evaluation.
 */

enum class WorkType {
    Epic,
    Feature,
    Story,
    Task
};

enum class Status {
    Backlog,
    Ready,
    InProgress,
    Blocked,
    Done,
    Cancelled
};

enum class Priority {
    Low,
    Medium,
    High,
    Critical
};

std::string toString(WorkType type) {
    switch (type) {
        case WorkType::Epic: return "Epic";
        case WorkType::Feature: return "Feature";
        case WorkType::Story: return "Story";
        case WorkType::Task: return "Task";
    }
    throw std::logic_error("Unknown work type");
}

std::string toString(Status status) {
    switch (status) {
        case Status::Backlog: return "Backlog";
        case Status::Ready: return "Ready";
        case Status::InProgress: return "In Progress";
        case Status::Blocked: return "Blocked";
        case Status::Done: return "Done";
        case Status::Cancelled: return "Cancelled";
    }
    throw std::logic_error("Unknown status");
}

std::string toString(Priority priority) {
    switch (priority) {
        case Priority::Low: return "Low";
        case Priority::Medium: return "Medium";
        case Priority::High: return "High";
        case Priority::Critical: return "Critical";
    }
    throw std::logic_error("Unknown priority");
}

struct WorkItem {
    std::string id;
    std::string title;
    WorkType type;
    std::optional<std::string> parentId;
    Status status = Status::Backlog;
    Priority priority = Priority::Medium;
    std::string owner;
    std::optional<double> storyPoints;
    std::optional<double> estimateHours;
    std::vector<std::string> acceptanceCriteria;
    std::set<std::string> dependencies;
};

struct Progress {
    double total = 0.0;
    double completed = 0.0;
    double remaining = 0.0;
    double percent = 0.0;
    std::size_t unestimatedStories = 0;
    std::string unit = "story points";
};

class GovernanceError : public std::runtime_error {
public:
    explicit GovernanceError(const std::string& message)
        : std::runtime_error(message) {}
};

class DeliveryPortfolio {
private:
    std::unordered_map<std::string, WorkItem> items;
    std::unordered_map<std::string, std::vector<std::string>> childIndex;

    static std::optional<WorkType> expectedParent(WorkType type) {
        switch (type) {
            case WorkType::Epic: return std::nullopt;
            case WorkType::Feature: return WorkType::Epic;
            case WorkType::Story: return WorkType::Feature;
            case WorkType::Task: return WorkType::Story;
        }
        throw std::logic_error("Unknown work type");
    }

    static bool isTerminal(Status status) {
        return status == Status::Done || status == Status::Cancelled;
    }

    void validateDependencies(
        const std::unordered_map<std::string, WorkItem>& candidateItems
    ) const {
        std::set<std::string> visiting;
        std::set<std::string> visited;

        // Three-color depth-first search detects cycles in O(V + E).
        std::function<void(const std::string&)> visit =
            [&](const std::string& id) {
                if (visiting.count(id)) {
                    throw GovernanceError(
                        "Dependency cycle detected at " + id
                    );
                }

                if (visited.count(id)) {
                    return;
                }

                visiting.insert(id);
                const auto& item = candidateItems.at(id);

                for (const auto& dependency : item.dependencies) {
                    if (!candidateItems.count(dependency)) {
                        throw GovernanceError(
                            "Unknown dependency " + dependency
                        );
                    }
                    visit(dependency);
                }

                visiting.erase(id);
                visited.insert(id);
            };

        for (const auto& pair : candidateItems) {
            visit(pair.first);
        }
    }

public:
    void add(WorkItem item) {
        if (item.id.empty() || item.title.empty()) {
            throw GovernanceError("ID and title are required");
        }

        if (items.count(item.id)) {
            throw GovernanceError("Duplicate ID: " + item.id);
        }

        const auto requiredParent = expectedParent(item.type);

        if (!requiredParent.has_value()) {
            if (item.parentId.has_value()) {
                throw GovernanceError("An epic cannot have a parent");
            }
        } else {
            if (!item.parentId.has_value()) {
                throw GovernanceError(
                    toString(item.type) + " requires a parent"
                );
            }

            const auto parent = items.find(*item.parentId);
            if (parent == items.end()) {
                throw GovernanceError(
                    "Parent does not exist: " + *item.parentId
                );
            }

            if (parent->second.type != *requiredParent) {
                throw GovernanceError(
                    toString(item.type) + " must be beneath " +
                    toString(*requiredParent)
                );
            }
        }

        if (item.storyPoints.has_value()) {
            if (item.type != WorkType::Story || *item.storyPoints < 0.0) {
                throw GovernanceError("Invalid story-point estimate");
            }
        }

        if (item.estimateHours.has_value()) {
            if (item.type != WorkType::Task || *item.estimateHours < 0.0) {
                throw GovernanceError("Invalid task-hour estimate");
            }
        }

        if (item.type == WorkType::Story &&
            item.acceptanceCriteria.empty()) {
            throw GovernanceError(
                "Stories require explicit acceptance criteria"
            );
        }

        if (item.dependencies.count(item.id)) {
            throw GovernanceError("An item cannot depend on itself");
        }

        for (const auto& dependency : item.dependencies) {
            if (!items.count(dependency)) {
                throw GovernanceError(
                    "Dependency must exist before item creation: " +
                    dependency
                );
            }
        }

        const std::string id = item.id;
        const auto parentId = item.parentId;

        items.emplace(id, std::move(item));

        try {
            validateDependencies(items);
        } catch (...) {
            items.erase(id);
            throw;
        }

        if (parentId.has_value()) {
            childIndex[*parentId].push_back(id);
        }
    }

    const WorkItem& get(const std::string& id) const {
        const auto iterator = items.find(id);
        if (iterator == items.end()) {
            throw GovernanceError("Unknown work item: " + id);
        }
        return iterator->second;
    }

    std::vector<std::string> children(const std::string& id) const {
        const auto iterator = childIndex.find(id);
        if (iterator == childIndex.end()) {
            return {};
        }

        auto result = iterator->second;
        std::sort(result.begin(), result.end());
        return result;
    }

    std::vector<std::string> descendants(const std::string& root) const {
        std::vector<std::string> result;
        std::vector<std::string> stack = children(root);

        while (!stack.empty()) {
            const auto id = stack.back();
            stack.pop_back();
            result.push_back(id);

            const auto nested = children(id);
            stack.insert(stack.end(), nested.begin(), nested.end());
        }

        return result;
    }

    std::vector<std::string> unmetDependencies(
        const std::string& id
    ) const {
        std::vector<std::string> unmet;

        for (const auto& dependency : get(id).dependencies) {
            if (get(dependency).status != Status::Done) {
                unmet.push_back(dependency);
            }
        }

        return unmet;
    }

    void transition(const std::string& id, Status next) {
        auto iterator = items.find(id);
        if (iterator == items.end()) {
            throw GovernanceError("Unknown work item: " + id);
        }

        auto& item = iterator->second;
        if (item.status == next) {
            return;
        }

        const std::map<Status, std::set<Status>> allowed = {
            {Status::Backlog, {Status::Ready, Status::Cancelled}},
            {Status::Ready, {
                Status::InProgress, Status::Blocked, Status::Cancelled
            }},
            {Status::InProgress, {
                Status::Ready, Status::Blocked, Status::Done, Status::Cancelled
            }},
            {Status::Blocked, {
                Status::Ready, Status::InProgress, Status::Cancelled
            }},
            {Status::Done, {Status::Ready}},
            {Status::Cancelled, {Status::Backlog}}
        };

        if (!allowed.at(item.status).count(next)) {
            throw GovernanceError(
                "Invalid transition for " + id + ": " +
                toString(item.status) + " -> " + toString(next)
            );
        }

        if (next == Status::InProgress) {
            const auto unmet = unmetDependencies(id);
            if (!unmet.empty()) {
                throw GovernanceError(
                    id + " cannot start because dependencies are incomplete"
                );
            }
        }

        if (next == Status::Done) {
            const auto nested = descendants(id);

            if (item.type == WorkType::Story) {
                for (const auto& child : children(id)) {
                    if (!isTerminal(get(child).status)) {
                        throw GovernanceError(
                            "Story has unfinished task: " + child
                        );
                    }
                }
            }

            if (item.type == WorkType::Feature || item.type == WorkType::Epic) {
                for (const auto& descendant : nested) {
                    const auto& child = get(descendant);

                    if ((child.type == WorkType::Story ||
                         child.type == WorkType::Task) &&
                        !isTerminal(child.status)) {
                        throw GovernanceError(
                            id + " has unfinished descendant: " + descendant
                        );
                    }
                }
            }
        }

        item.status = next;
    }

    Progress calculateProgress(const std::string& root) const {
        Progress progress;
        const auto nested = descendants(root);

        std::vector<const WorkItem*> stories;
        for (const auto& id : nested) {
            const auto& item = get(id);
            if (item.type == WorkType::Story &&
                item.status != Status::Cancelled) {
                stories.push_back(&item);
            }
        }

        const bool hasStoryPoints = std::any_of(
            stories.begin(), stories.end(),
            [](const WorkItem* story) {
                return story->storyPoints.has_value();
            }
        );

        if (hasStoryPoints) {
            progress.unit = "story points";

            for (const auto* story : stories) {
                if (!story->storyPoints.has_value()) {
                    ++progress.unestimatedStories;
                    continue;
                }

                progress.total += *story->storyPoints;
                if (story->status == Status::Done) {
                    progress.completed += *story->storyPoints;
                }
            }
        } else {
            progress.unit = "task hours";

            for (const auto& id : nested) {
                const auto& item = get(id);
                if (item.type != WorkType::Task ||
                    item.status == Status::Cancelled ||
                    !item.estimateHours.has_value()) {
                    continue;
                }

                progress.total += *item.estimateHours;
                if (item.status == Status::Done) {
                    progress.completed += *item.estimateHours;
                }
            }
            progress.unestimatedStories = stories.size();
        }

        progress.remaining = progress.total - progress.completed;
        progress.percent = progress.total > 0.0
            ? 100.0 * progress.completed / progress.total
            : 0.0;

        return progress;
    }

    bool releaseReady(const std::string& epicId) const {
        if (get(epicId).type != WorkType::Epic) {
            throw GovernanceError("Release readiness requires an epic");
        }

        for (const auto& id : descendants(epicId)) {
            const auto& item = get(id);

            if (item.type == WorkType::Story &&
                item.status != Status::Done &&
                item.status != Status::Cancelled) {
                return false;
            }

            if (item.status == Status::Blocked) {
                return false;
            }
        }

        return true;
    }

    void printTree(const std::string& root, int depth = 0) const {
        const auto& item = get(root);

        std::cout << std::string(static_cast<std::size_t>(depth * 2), ' ')
                  << item.id << " [" << toString(item.type) << "] "
                  << item.title << " (" << toString(item.status) << ")\n";

        for (const auto& child : children(root)) {
            printTree(child, depth + 1);
        }
    }
};

int main() {
    try {
        DeliveryPortfolio portfolio;

        portfolio.add({
            "EP-300",
            "Public Sector Audit Platform",
            WorkType::Epic,
            std::nullopt,
            Status::Backlog,
            Priority::Critical,
            "Product Office"
        });

        portfolio.add({
            "FE-310",
            "Evidence Collection",
            WorkType::Feature,
            "EP-300",
            Status::Backlog,
            Priority::High,
            "Audit Engineering"
        });

        portfolio.add({
            "ST-311",
            "As an auditor, I can upload inspection evidence",
            WorkType::Story,
            "FE-310",
            Status::Backlog,
            Priority::High,
            "Audit Engineering",
            5.0,
            std::nullopt,
            {
                "Only authorized auditors can upload evidence",
                "Each upload records its checksum and submission time"
            }
        });

        portfolio.add({
            "TS-311A",
            "Implement evidence metadata persistence",
            WorkType::Task,
            "ST-311",
            Status::Backlog,
            Priority::High,
            "Backend Team",
            std::nullopt,
            8.0
        });

        portfolio.add({
            "TS-311B",
            "Verify uploaded-file integrity",
            WorkType::Task,
            "ST-311",
            Status::Backlog,
            Priority::High,
            "Security Engineering",
            std::nullopt,
            5.0,
            {},
            {"TS-311A"}
        });

        portfolio.add({
            "ST-312",
            "As an auditor, I can search submitted evidence",
            WorkType::Story,
            "FE-310",
            Status::Backlog,
            Priority::Medium,
            "Audit Engineering",
            8.0,
            std::nullopt,
            {
                "Search results respect departmental access",
                "Results can be filtered by submission date"
            }
        });

        portfolio.add({
            "FE-320",
            "Audit Trail Reporting",
            WorkType::Feature,
            "EP-300",
            Status::Backlog,
            Priority::High,
            "Reporting Team"
        });

        std::cout << "Delivery hierarchy\n";
        portfolio.printTree("EP-300");

        const auto initial = portfolio.calculateProgress("EP-300");
        std::cout << std::fixed << std::setprecision(2)
                  << "\nInitial progress: " << initial.completed
                  << "/" << initial.total << " " << initial.unit
                  << " (" << initial.percent << "%)\n";

        try {
            portfolio.transition("TS-311B", Status::InProgress);
        } catch (const GovernanceError& error) {
            std::cout << "Expected dependency rejection: "
                      << error.what() << "\n";
        }

        portfolio.transition("TS-311A", Status::Ready);
        portfolio.transition("TS-311A", Status::InProgress);
        portfolio.transition("TS-311A", Status::Done);

        portfolio.transition("TS-311B", Status::Ready);
        portfolio.transition("TS-311B", Status::InProgress);
        portfolio.transition("TS-311B", Status::Done);

        portfolio.transition("ST-311", Status::Ready);
        portfolio.transition("ST-311", Status::InProgress);
        portfolio.transition("ST-311", Status::Done);

        const auto updated = portfolio.calculateProgress("EP-300");
        std::cout << "\nUpdated progress: " << updated.completed
                  << "/" << updated.total << " " << updated.unit
                  << " (" << updated.percent << "%)\n";

        std::cout << "Release ready: "
                  << (portfolio.releaseReady("EP-300") ? "yes" : "no")
                  << "\n";

        try {
            portfolio.add({
                "FE-BAD",
                "Incorrectly nested feature",
                WorkType::Feature,
                "ST-311"
            });
        } catch (const GovernanceError& error) {
            std::cout << "Expected hierarchy rejection: "
                      << error.what() << "\n";
        }

        std::cout << "\nUpdated hierarchy\n";
        portfolio.printTree("EP-300");

    } catch (const std::exception& error) {
        std::cerr << "Fatal portfolio error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
