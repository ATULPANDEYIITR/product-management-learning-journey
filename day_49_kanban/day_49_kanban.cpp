#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using Clock = std::chrono::system_clock;
using TimePoint = Clock::time_point;

enum class Column {
    Backlog,
    Ready,
    Development,
    Review,
    Testing,
    Done
};

std::string toString(Column column) {
    switch (column) {
        case Column::Backlog: return "Backlog";
        case Column::Ready: return "Ready";
        case Column::Development: return "Development";
        case Column::Review: return "Review";
        case Column::Testing: return "Testing";
        case Column::Done: return "Done";
    }
    return "Unknown";
}

struct WorkItem {
    std::string id;
    std::string service;
    int priority;
    Column column;
    TimePoint created;
    std::optional<TimePoint> started;
    std::optional<TimePoint> completed;
    std::vector<Column> history;
};

struct FlowReport {
    double averageCycleHours{};
    double throughputPerDay{};
    double averageWip{};
};

class GovernanceBoard {
private:
    std::unordered_map<std::string, WorkItem> items_;
    std::map<Column, std::size_t> limits_;

    std::size_t count(Column column) const {
        std::size_t result = 0;
        for (const auto& [id, item] : items_) {
            if (item.column == column) {
                ++result;
            }
        }
        return result;
    }

    bool canEnter(Column column) const {
        auto it = limits_.find(column);
        return it == limits_.end() || count(column) < it->second;
    }

public:
    explicit GovernanceBoard(std::map<Column, std::size_t> limits)
        : limits_(std::move(limits)) {}

    void add(WorkItem item) {
        if (items_.contains(item.id)) {
            throw std::invalid_argument("Duplicate work item: " + item.id);
        }

        if (item.priority < 1) {
            throw std::invalid_argument("Priority must be positive");
        }

        item.history.push_back(item.column);
        items_.emplace(item.id, std::move(item));
    }

    bool move(const std::string& id, Column destination) {
        auto it = items_.find(id);
        if (it == items_.end()) {
            throw std::out_of_range("Unknown item: " + id);
        }

        WorkItem& item = it->second;

        if (item.column == destination) {
            return true;
        }

        if (!canEnter(destination)) {
            std::cout
                << "BLOCKED " << item.id
                << ": " << toString(destination)
                << " has reached its WIP limit\n";
            return false;
        }

        const auto now = Clock::now();
        const Column previous = item.column;

        item.column = destination;
        item.history.push_back(destination);

        if (destination == Column::Development && !item.started) {
            item.started = now;
        }

        if (destination == Column::Done) {
            item.completed = now;
        }

        std::cout
            << "FLOW " << item.id << ": "
            << toString(previous) << " -> "
            << toString(destination) << '\n';

        return true;
    }

    std::optional<std::string> pull(Column source, Column destination) {
        if (!canEnter(destination)) {
            return std::nullopt;
        }

        std::vector<WorkItem*> candidates;

        for (auto& [id, item] : items_) {
            if (item.column == source) {
                candidates.push_back(&item);
            }
        }

        if (candidates.empty()) {
            return std::nullopt;
        }

        std::sort(
            candidates.begin(),
            candidates.end(),
            [](const WorkItem* a, const WorkItem* b) {
                if (a->priority != b->priority) {
                    return a->priority < b->priority;
                }
                return a->created < b->created;
            }
        );

        const std::string selected = candidates.front()->id;
        if (move(selected, destination)) {
            return selected;
        }

        return std::nullopt;
    }

    void printBoard() const {
        std::map<Column, std::size_t> counts;

        for (const auto& [id, item] : items_) {
            ++counts[item.column];
        }

        std::cout << "\nBoard state\n";
        for (const auto& [column, countValue] : counts) {
            std::cout
                << std::left << std::setw(15)
                << toString(column)
                << countValue << '\n';
        }
    }

    std::vector<const WorkItem*> completedItems() const {
        std::vector<const WorkItem*> result;

        for (const auto& [id, item] : items_) {
            if (item.column == Column::Done && item.completed) {
                result.push_back(&item);
            }
        }

        return result;
    }
};

double hoursBetween(TimePoint start, TimePoint end) {
    using Hours = std::chrono::duration<double, std::ratio<3600>>;
    return Hours(end - start).count();
}

FlowReport calculateFlow(const GovernanceBoard& board) {
    const auto completed = board.completedItems();

    double totalCycleHours = 0.0;

    for (const auto* item : completed) {
        if (item->started && item->completed) {
            totalCycleHours += hoursBetween(
                *item->started,
                *item->completed
            );
        }
    }

    const double averageCycle =
        completed.empty()
            ? 0.0
            : totalCycleHours / completed.size();

    // The case study uses a seven-day observation window for throughput.
    const double throughput =
        static_cast<double>(completed.size()) / 7.0;

    return {
        averageCycle,
        throughput,
        4.0
    };
}

double littleLawCycleTime(
    double averageWip,
    double throughputPerDay
) {
    if (averageWip < 0.0 || throughputPerDay <= 0.0) {
        throw std::invalid_argument(
            "Little's Law requires non-negative WIP and positive throughput"
        );
    }

    return averageWip / throughputPerDay;
}

int main() {
    GovernanceBoard board({
        {Column::Development, 3},
        {Column::Review, 2},
        {Column::Testing, 2}
    });

    const auto now = Clock::now();

    board.add({
        "PAY-201",
        "Payment service",
        1,
        Column::Ready,
        now - std::chrono::hours(30),
        std::nullopt,
        std::nullopt,
        {}
    });

    board.add({
        "PAY-202",
        "Payment service",
        2,
        Column::Ready,
        now - std::chrono::hours(20),
        std::nullopt,
        std::nullopt,
        {}
    });

    board.add({
        "OBS-301",
        "Observability",
        3,
        Column::Ready,
        now - std::chrono::hours(12),
        std::nullopt,
        std::nullopt,
        {}
    });

    board.add({
        "DB-401",
        "Database",
        2,
        Column::Ready,
        now - std::chrono::hours(10),
        std::nullopt,
        std::nullopt,
        {}
    });

    board.add({
        "SEC-501",
        "Security",
        1,
        Column::Ready,
        now - std::chrono::hours(8),
        std::nullopt,
        std::nullopt,
        {}
    });

    board.printBoard();

    // Pull-based movement fills Development only to its explicit WIP limit.
    board.pull(Column::Ready, Column::Development);
    board.pull(Column::Ready, Column::Development);
    board.pull(Column::Ready, Column::Development);

    // The next pull is refused because no downstream capacity is required
    // to justify starting additional development work.
    board.pull(Column::Ready, Column::Development);

    board.printBoard();

    // Moving one item into Review frees Development capacity.
    auto developmentItem =
        board.pull(Column::Development, Column::Review);

    if (developmentItem) {
        // Testing is another constrained stage. Once testing completes,
        // Done has no WIP restriction and represents completed flow.
        board.move(*developmentItem, Column::Testing);
        board.move(*developmentItem, Column::Done);
    }

    board.pull(Column::Ready, Column::Development);

    board.printBoard();

    const FlowReport report = calculateFlow(board);

    std::cout << "\nFlow report\n";
    std::cout
        << "Average cycle hours: "
        << std::fixed << std::setprecision(2)
        << report.averageCycleHours << '\n';

    std::cout
        << "Observed throughput per day: "
        << report.throughputPerDay << '\n';

    const double estimatedCycle =
        littleLawCycleTime(4.0, 2.0);

    std::cout
        << "Little's Law cycle-time estimate: "
        << estimatedCycle << " days\n";

    std::cout << "\nCase-study observations\n";
    std::cout
        << "A full Review column can become a bottleneck even when "
           "Development has available capacity.\n";

    std::cout
        << "WIP limits expose blocked flow instead of hiding it by "
           "starting more work upstream.\n";

    std::cout
        << "Throughput measures completed work; WIP alone does not "
           "represent delivery performance.\n";

    return 0;
}
