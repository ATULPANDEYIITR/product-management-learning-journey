#include <algorithm>
#include <cmath>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Roadmap Communication and Governance Engine.
 *
 * Evaluates roadmap consistency and produces four distinct
 * communication views:
 * 1. Executive
 * 2. Engineering
 * 3. Sales
 * 4. Customer
 *
 * C++17, standard library only.
 */

enum class Audience {
    Executive,
    Engineering,
    Sales,
    Customer
};

enum class Status {
    Planned,
    InProgress,
    Blocked,
    AtRisk,
    Completed,
    Cancelled
};

enum class Priority {
    Critical,
    High,
    Medium,
    Low
};

enum class Confidence {
    High,
    Medium,
    Low
};

string toString(Status status) {
    switch (status) {
        case Status::Planned: return "Planned";
        case Status::InProgress: return "In Progress";
        case Status::Blocked: return "Blocked";
        case Status::AtRisk: return "At Risk";
        case Status::Completed: return "Completed";
        case Status::Cancelled: return "Cancelled";
    }

    throw invalid_argument("Unknown status.");
}

string toString(Priority priority) {
    switch (priority) {
        case Priority::Critical: return "Critical";
        case Priority::High: return "High";
        case Priority::Medium: return "Medium";
        case Priority::Low: return "Low";
    }

    throw invalid_argument("Unknown priority.");
}

string toString(Confidence confidence) {
    switch (confidence) {
        case Confidence::High: return "High";
        case Confidence::Medium: return "Medium";
        case Confidence::Low: return "Low";
    }

    throw invalid_argument("Unknown confidence.");
}

struct Milestone {
    string id;
    string name;
    string targetDate;
    Status status;
    double progress;

    void validate() const {
        if (id.empty() || name.empty()) {
            throw invalid_argument("Milestone ID and name are required.");
        }

        if (progress < 0 || progress > 100) {
            throw invalid_argument("Invalid milestone progress.");
        }
    }
};

struct RoadmapItem {
    string id;
    string title;
    string description;
    string owner;
    string objective;
    string businessValue;
    string engineeringDetails;
    string salesMessage;
    string customerImpact;
    string startDate;
    string targetDate;

    Priority priority;
    Status status;
    Confidence confidence;

    double progress = 0.0;
    string risk;

    set<string> dependencies;
    vector<Milestone> milestones;

    void validate() const {
        if (id.empty() || title.empty() ||
            owner.empty() || objective.empty()) {
            throw invalid_argument("Required roadmap fields are missing.");
        }

        if (startDate.empty() || targetDate.empty() ||
            targetDate < startDate) {
            throw invalid_argument("Invalid roadmap date range.");
        }

        if (!isfinite(progress) || progress < 0 || progress > 100) {
            throw invalid_argument("Progress must be between 0 and 100.");
        }

        if (status == Status::Planned && progress > 0) {
            throw invalid_argument(
                "Planned items cannot have implementation progress."
            );
        }

        if (status == Status::Completed && progress != 100) {
            throw invalid_argument(
                "Completed items must have 100% progress."
            );
        }

        for (const auto& milestone : milestones) {
            milestone.validate();
        }
    }
};

class RoadmapEngine {
private:
    string name;
    string owner;

    map<string, RoadmapItem> items;
    unsigned long long version = 1;

    void validateDependencies() const {
        set<string> visited;
        set<string> active;

        function<void(const string&)> visit =
            [&](const string& id) {
                if (active.count(id)) {
                    throw invalid_argument("Circular dependency detected.");
                }

                if (visited.count(id)) return;

                auto it = items.find(id);

                if (it == items.end()) {
                    throw invalid_argument("Unknown roadmap item.");
                }

                active.insert(id);

                for (const auto& dependency : it->second.dependencies) {
                    if (!items.count(dependency)) {
                        throw invalid_argument(
                            "Dependency does not exist: " + dependency
                        );
                    }

                    visit(dependency);
                }

                active.erase(id);
                visited.insert(id);
            };

        for (const auto& entry : items) {
            visit(entry.first);
        }
    }

public:
    RoadmapEngine(string roadmapName, string roadmapOwner)
        : name(move(roadmapName)), owner(move(roadmapOwner)) {
        if (name.empty() || owner.empty()) {
            throw invalid_argument("Roadmap name and owner are required.");
        }
    }

    void addItem(const RoadmapItem& item) {
        item.validate();

        if (items.count(item.id)) {
            throw invalid_argument("Duplicate roadmap item.");
        }

        items.emplace(item.id, item);

        try {
            validateDependencies();
        } catch (...) {
            items.erase(item.id);
            throw;
        }

        ++version;
    }

    const RoadmapItem& getItem(const string& id) const {
        auto it = items.find(id);

        if (it == items.end()) {
            throw out_of_range("Roadmap item not found: " + id);
        }

        return it->second;
    }

    void updateStatus(
        const string& id,
        Status newStatus,
        double newProgress
    ) {
        auto it = items.find(id);

        if (it == items.end()) {
            throw out_of_range("Unknown roadmap item.");
        }

        RoadmapItem& item = it->second;

        if (item.status == Status::Cancelled) {
            throw logic_error("Cancelled items cannot be updated.");
        }

        if (item.status == Status::Completed &&
            newStatus != Status::Completed) {
            throw logic_error("Completed item correction is required.");
        }

        if (!isfinite(newProgress) ||
            newProgress < 0 || newProgress > 100) {
            throw invalid_argument("Invalid progress.");
        }

        if (newStatus == Status::Planned && newProgress > 0) {
            throw invalid_argument("Planned item cannot show progress.");
        }

        if (newStatus == Status::Completed) {
            newProgress = 100;
        }

        item.status = newStatus;
        item.progress = newProgress;

        ++version;
    }

    bool dependenciesReady(const string& id) const {
        const auto& item = getItem(id);

        for (const auto& dependency : item.dependencies) {
            if (getItem(dependency).status != Status::Completed) {
                return false;
            }
        }

        return true;
    }

    double portfolioProgress() const {
        double total = 0;
        size_t count = 0;

        for (const auto& entry : items) {
            if (entry.second.status == Status::Cancelled) {
                continue;
            }

            total += entry.second.progress;
            ++count;
        }

        return count == 0 ? 0 : total / count;
    }

    vector<const RoadmapItem*> getRisks() const {
        vector<const RoadmapItem*> result;

        for (const auto& entry : items) {
            const auto& item = entry.second;

            if (item.status == Status::Blocked ||
                item.status == Status::AtRisk ||
                !item.risk.empty()) {
                result.push_back(&item);
            }
        }

        return result;
    }

    string generate(Audience audience) const {
        ostringstream out;

        switch (audience) {
            case Audience::Executive:
                out << "EXECUTIVE ROADMAP: " << name << '\n';
                out << "Owner: " << owner << '\n';
                out << "Portfolio progress: "
                    << fixed << setprecision(1)
                    << portfolioProgress() << "%\n\n";

                for (const auto& entry : items) {
                    const auto& item = entry.second;

                    out << item.title << '\n';
                    out << "Objective: " << item.objective << '\n';
                    out << "Business value: " << item.businessValue << '\n';
                    out << "Status: " << toString(item.status) << '\n';
                    out << "Target: " << item.targetDate << '\n';
                    out << "Confidence: "
                        << toString(item.confidence) << '\n';
                    out << "Risk: "
                        << (item.risk.empty() ? "None" : item.risk)
                        << "\n\n";
                }

                out << "DECISION ATTENTION\n";

                for (const auto* item : getRisks()) {
                    out << "- " << item->title << ": "
                        << (item->risk.empty()
                            ? toString(item->status)
                            : item->risk)
                        << '\n';
                }
                break;

            case Audience::Engineering:
                out << "ENGINEERING DELIVERY ROADMAP: " << name << '\n';

                for (const auto& entry : items) {
                    const auto& item = entry.second;

                    out << "\nFEATURE: " << item.title << '\n';
                    out << "Owner: " << item.owner << '\n';
                    out << "Priority: " << toString(item.priority) << '\n';
                    out << "Status: " << toString(item.status) << '\n';
                    out << "Technical scope: "
                        << item.engineeringDetails << '\n';
                    out << "Progress: " << item.progress << "%\n";
                    out << "Dependencies: ";

                    if (item.dependencies.empty()) {
                        out << "None";
                    } else {
                        for (const auto& dependency : item.dependencies) {
                            out << dependency << ' ';
                        }
                    }

                    out << "\nDependencies ready: "
                        << boolalpha << dependenciesReady(item.id);
                    out << "\nTarget: " << item.targetDate << '\n';
                    out << "Risk: "
                        << (item.risk.empty() ? "None" : item.risk)
                        << '\n';

                    for (const auto& milestone : item.milestones) {
                        out << "  Milestone: " << milestone.name
                            << " | " << milestone.targetDate
                            << " | " << toString(milestone.status)
                            << '\n';
                    }
                }
                break;

            case Audience::Sales:
                out << "SALES ENABLEMENT ROADMAP: " << name << '\n';

                for (const auto& entry : items) {
                    const auto& item = entry.second;

                    if (item.status == Status::Cancelled) continue;

                    out << "\nFEATURE: " << item.title << '\n';
                    out << "Customer value: "
                        << item.businessValue << '\n';
                    out << "Sales positioning: "
                        << item.salesMessage << '\n';
                    out << "Availability: "
                        << toString(item.status) << '\n';
                    out << "Target: " << item.targetDate << '\n';
                    out << "Confidence: "
                        << toString(item.confidence) << '\n';
                }

                out << "\nOnly released capabilities should be "
                    << "represented as currently available.\n";
                break;

            case Audience::Customer:
                out << "CUSTOMER ROADMAP: " << name << '\n';

                for (const auto& entry : items) {
                    const auto& item = entry.second;

                    if (item.status == Status::Cancelled ||
                        item.status == Status::Blocked) {
                        continue;
                    }

                    out << "\nFEATURE: " << item.title << '\n';

                    out << "Status: ";

                    switch (item.status) {
                        case Status::Planned: out << "Planned"; break;
                        case Status::InProgress:
                            out << "In development";
                            break;
                        case Status::AtRisk:
                            out << "Under review";
                            break;
                        case Status::Completed:
                            out << "Completed";
                            break;
                        default: break;
                    }

                    out << "\nCustomer impact: "
                        << (item.customerImpact.empty()
                            ? item.businessValue
                            : item.customerImpact);
                    out << "\nTarget: " << item.targetDate << '\n';
                }

                out << "\nTarget dates are estimates, not guaranteed "
                    << "delivery commitments.\n";
                break;
        }

        return out.str();
    }

    unsigned long long getVersion() const {
        return version;
    }

    size_t size() const {
        return items.size();
    }
};

RoadmapItem makeItem(
    string id,
    string title,
    string startDate,
    string targetDate,
    Status status,
    double progress,
    set<string> dependencies = {}
) {
    RoadmapItem item{};

    item.id = move(id);
    item.title = move(title);
    item.description = "Enterprise platform capability.";
    item.owner = "Platform Engineering";
    item.objective = "Improve enterprise operations.";
    item.businessValue = "Increase business efficiency.";
    item.engineeringDetails = "API integration and service implementation.";
    item.salesMessage = "Enterprise platform capability.";
    item.customerImpact = "Improved customer experience.";
    item.startDate = move(startDate);
    item.targetDate = move(targetDate);
    item.priority = Priority::High;
    item.status = status;
    item.confidence = Confidence::Medium;
    item.progress = progress;
    item.dependencies = move(dependencies);

    return item;
}

void runTests(RoadmapEngine& roadmap) {
    if (roadmap.size() != 4) {
        throw runtime_error("Unexpected roadmap size.");
    }

    if (!roadmap.dependenciesReady("RM-002")) {
        throw runtime_error("Completed dependency should be ready.");
    }

    if (roadmap.dependenciesReady("RM-003")) {
        throw runtime_error("Incomplete dependency should not be ready.");
    }

    if (abs(roadmap.portfolioProgress() - 43.75) > 0.001) {
        throw runtime_error("Incorrect portfolio progress.");
    }

    try {
        auto invalid = makeItem(
            "RM-005",
            "Invalid dependency",
            "2027-01-01",
            "2027-02-01",
            Status::Planned,
            0,
            {"UNKNOWN"}
        );

        roadmap.addItem(invalid);
        throw runtime_error("Unknown dependency was accepted.");
    } catch (const invalid_argument&) {
        // Expected validation failure.
    }

    cout << "All C++ validation tests passed.\n";
}

int main() {
    try {
        RoadmapEngine roadmap(
            "Enterprise Product Platform 2027",
            "Product Management Office"
        );

        auto identity = makeItem(
            "RM-001",
            "Identity Management",
            "2026-10-01",
            "2026-12-15",
            Status::Completed,
            100
        );

        identity.priority = Priority::Critical;
        identity.confidence = Confidence::High;
        identity.engineeringDetails =
            "OIDC, OAuth 2.0 and role-based access control.";

        roadmap.addItem(identity);

        auto analytics = makeItem(
            "RM-002",
            "Analytics Dashboard",
            "2026-11-01",
            "2027-02-15",
            Status::InProgress,
            55,
            {"RM-001"}
        );

        analytics.engineeringDetails =
            "Event ingestion, aggregation APIs and dashboard UI.";

        roadmap.addItem(analytics);

        auto reporting = makeItem(
            "RM-003",
            "Automated Reporting",
            "2026-11-15",
            "2027-03-15",
            Status::AtRisk,
            20,
            {"RM-002"}
        );

        reporting.risk = "Data integration capacity constraints.";
        reporting.confidence = Confidence::Low;

        roadmap.addItem(reporting);

        auto portal = makeItem(
            "RM-004",
            "Customer Self-Service Portal",
            "2027-01-01",
            "2027-04-30",
            Status::Planned,
            0,
            {"RM-001"}
        );

        portal.customerImpact =
            "Simplified customer account management.";

        roadmap.addItem(portal);

        runTests(roadmap);

        cout << "\nPORTFOLIO METRICS\n";
        cout << "Items: " << roadmap.size() << '\n';
        cout << "Progress: " << fixed << setprecision(2)
             << roadmap.portfolioProgress() << "%\n";
        cout << "Version: " << roadmap.getVersion() << '\n';

        const vector<pair<Audience, string>> audiences = {
            {Audience::Executive, "EXECUTIVE"},
            {Audience::Engineering, "ENGINEERING"},
            {Audience::Sales, "SALES"},
            {Audience::Customer, "CUSTOMER"}
        };

        for (const auto& entry : audiences) {
            cout << "\n" << string(70, '=') << '\n';
            cout << entry.second << " COMMUNICATION\n\n";
            cout << roadmap.generate(entry.first);
        }

        cout << "\nPROGRAM COMPLETED SUCCESSFULLY.\n";

    } catch (const exception& error) {
        cerr << "Roadmap processing error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
