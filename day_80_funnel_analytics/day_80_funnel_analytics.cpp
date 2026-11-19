#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

using Timestamp = long long;

enum class EventType {
    Visit,
    ProductView,
    AddToCart,
    Checkout,
    Purchase
};

enum class Device {
    Mobile,
    Desktop,
    Tablet
};

string toString(EventType type) {
    switch (type) {
        case EventType::Visit: return "visit";
        case EventType::ProductView: return "product_view";
        case EventType::AddToCart: return "add_to_cart";
        case EventType::Checkout: return "checkout";
        case EventType::Purchase: return "purchase";
    }

    throw invalid_argument("Unknown event type.");
}

string toString(Device device) {
    switch (device) {
        case Device::Mobile: return "mobile";
        case Device::Desktop: return "desktop";
        case Device::Tablet: return "tablet";
    }

    throw invalid_argument("Unknown device.");
}

struct Event {
    string eventId;
    string userId;
    EventType type;
    Timestamp timestamp;
    string channel;
    Device device;
    string country;
};

struct FunnelDefinition {
    string name;
    vector<EventType> steps;
    Timestamp conversionWindow;

    void validate() const {
        if (name.empty()) {
            throw invalid_argument("Funnel name cannot be empty.");
        }

        if (steps.size() < 2) {
            throw invalid_argument("Funnel requires at least two steps.");
        }

        if (conversionWindow <= 0) {
            throw invalid_argument("Invalid conversion window.");
        }

        set<EventType> uniqueSteps(steps.begin(), steps.end());

        if (uniqueSteps.size() != steps.size()) {
            throw invalid_argument("Duplicate funnel steps.");
        }
    }
};

struct StepMetric {
    string name;
    size_t users = 0;
    size_t previousUsers = 0;
    size_t droppedUsers = 0;
    double conversionRate = 0;
    double dropOffRate = 0;
};

struct FunnelReport {
    string funnelName;
    size_t totalUsers = 0;
    size_t convertedUsers = 0;
    double overallConversionRate = 0;
    vector<StepMetric> steps;
};

class EventStore {
private:
    unordered_map<string, Event> events;
    unordered_map<string, vector<Event>> userEvents;

public:
    void add(const Event& event) {
        if (event.eventId.empty() || event.userId.empty()) {
            throw invalid_argument("Event and user IDs are required.");
        }

        if (events.find(event.eventId) != events.end()) {
            throw invalid_argument("Duplicate event ID.");
        }

        events.emplace(event.eventId, event);
        userEvents[event.userId].push_back(event);
    }

    void addBatch(const vector<Event>& batch) {
        unordered_set<string> incoming;

        for (const auto& event : batch) {
            if (event.eventId.empty() || event.userId.empty()) {
                throw invalid_argument("Invalid event in batch.");
            }

            if (
                events.count(event.eventId) ||
                !incoming.insert(event.eventId).second
            ) {
                throw invalid_argument("Duplicate batch event.");
            }
        }

        for (const auto& event : batch) {
            add(event);
        }
    }

    vector<Event> getUserEvents(const string& userId) const {
        auto it = userEvents.find(userId);

        if (it == userEvents.end()) {
            return {};
        }

        vector<Event> result = it->second;

        sort(
            result.begin(),
            result.end(),
            [](const Event& a, const Event& b) {
                return a.timestamp < b.timestamp;
            }
        );

        return result;
    }

    vector<string> getUserIds() const {
        vector<string> result;

        for (const auto& item : userEvents) {
            result.push_back(item.first);
        }

        return result;
    }

    size_t size() const {
        return events.size();
    }
};

class FunnelGovernanceEngine {
private:
    const EventStore& store;
    FunnelDefinition definition;

    vector<bool> evaluateProgression(
        const vector<Event>& events,
        Timestamp cohortStart
    ) const {
        vector<bool> completed(
            definition.steps.size(),
            false
        );

        size_t currentStep = 0;

        for (const auto& event : events) {
            if (event.timestamp < cohortStart) {
                continue;
            }

            if (
                event.timestamp - cohortStart >
                definition.conversionWindow
            ) {
                break;
            }

            if (event.type != definition.steps[currentStep]) {
                continue;
            }

            completed[currentStep] = true;
            currentStep++;

            if (currentStep == definition.steps.size()) {
                break;
            }
        }

        return completed;
    }

public:
    FunnelGovernanceEngine(
        const EventStore& eventStore,
        FunnelDefinition funnel
    ) : store(eventStore), definition(std::move(funnel)) {
        definition.validate();
    }

    FunnelReport analyze(
        const string& channelFilter = "",
        const string& deviceFilter = ""
    ) const {
        vector<size_t> counts(definition.steps.size(), 0);

        for (const string& userId : store.getUserIds()) {
            vector<Event> events = store.getUserEvents(userId);

            auto entry = find_if(
                events.begin(),
                events.end(),
                [&](const Event& event) {
                    return event.type == definition.steps[0];
                }
            );

            if (entry == events.end()) {
                continue;
            }

            if (
                !channelFilter.empty() &&
                entry->channel != channelFilter
            ) {
                continue;
            }

            if (
                !deviceFilter.empty() &&
                toString(entry->device) != deviceFilter
            ) {
                continue;
            }

            vector<bool> progression = evaluateProgression(
                events,
                entry->timestamp
            );

            for (size_t i = 0; i < progression.size(); ++i) {
                if (!progression[i]) {
                    break;
                }

                counts[i]++;
            }
        }

        FunnelReport report;
        report.funnelName = definition.name;
        report.totalUsers = counts.front();
        report.convertedUsers = counts.back();

        report.overallConversionRate =
            report.totalUsers == 0
                ? 0
                : 100.0 * report.convertedUsers / report.totalUsers;

        for (size_t i = 0; i < definition.steps.size(); ++i) {
            StepMetric metric;

            metric.name = toString(definition.steps[i]);
            metric.users = counts[i];

            metric.previousUsers =
                i == 0 ? counts[i] : counts[i - 1];

            metric.droppedUsers =
                metric.previousUsers - metric.users;

            if (metric.previousUsers > 0) {
                metric.conversionRate =
                    100.0 * metric.users / metric.previousUsers;

                metric.dropOffRate =
                    100.0 * metric.droppedUsers / metric.previousUsers;
            }

            report.steps.push_back(metric);
        }

        validateReport(report);

        return report;
    }

    static void validateReport(const FunnelReport& report) {
        for (size_t i = 1; i < report.steps.size(); ++i) {
            if (report.steps[i].users > report.steps[i - 1].users) {
                throw logic_error("Funnel progression invariant violated.");
            }
        }

        if (
            report.overallConversionRate < 0 ||
            report.overallConversionRate > 100
        ) {
            throw logic_error("Invalid overall conversion rate.");
        }
    }
};

void printReport(const FunnelReport& report) {
    cout << "\nFUNNEL ANALYTICS REPORT\n";
    cout << string(75, '=') << '\n';

    cout << "Funnel: " << report.funnelName << '\n';
    cout << "Initial users: " << report.totalUsers << '\n';
    cout << "Converted users: " << report.convertedUsers << '\n';

    cout << fixed << setprecision(2);
    cout << "Overall conversion: "
         << report.overallConversionRate << "%\n\n";

    cout << left << setw(20) << "Step"
         << right << setw(10) << "Users"
         << setw(15) << "Conversion"
         << setw(15) << "Drop-off"
         << setw(12) << "Dropped" << '\n';

    for (const auto& step : report.steps) {
        cout << left << setw(20) << step.name
             << right << setw(10) << step.users
             << setw(14) << step.conversionRate << "%"
             << setw(14) << step.dropOffRate << "%"
             << setw(12) << step.droppedUsers
             << '\n';
    }
}

vector<Event> generateSampleEvents() {
    const vector<vector<EventType>> journeys = {
        {EventType::Visit, EventType::ProductView,
         EventType::AddToCart, EventType::Checkout, EventType::Purchase},

        {EventType::Visit, EventType::ProductView,
         EventType::AddToCart, EventType::Checkout},

        {EventType::Visit, EventType::ProductView},

        {EventType::Visit, EventType::ProductView,
         EventType::AddToCart, EventType::Checkout, EventType::Purchase},

        {EventType::Visit, EventType::ProductView,
         EventType::AddToCart},

        {EventType::Visit},

        {EventType::Visit, EventType::ProductView,
         EventType::AddToCart, EventType::Checkout, EventType::Purchase},

        {EventType::Visit, EventType::ProductView,
         EventType::Checkout}
    };

    const vector<string> channels = {
        "organic", "paid", "organic", "paid",
        "referral", "organic", "paid", "referral"
    };

    vector<Event> result;

    Timestamp base = 1000000;
    int counter = 1;

    for (size_t i = 0; i < journeys.size(); ++i) {
        for (size_t j = 0; j < journeys[i].size(); ++j) {
            result.push_back({
                "E" + to_string(counter++),
                "U" + to_string(i + 1),
                journeys[i][j],
                base + static_cast<Timestamp>(i * 15 + j * 3) * 60,
                channels[i],
                i % 2 == 0 ? Device::Mobile : Device::Desktop,
                i % 2 == 0 ? "IN" : "US"
            });
        }
    }

    return result;
}

void runTests(
    const FunnelGovernanceEngine& engine
) {
    FunnelReport report = engine.analyze();

    if (report.totalUsers != 8) {
        throw runtime_error("Initial cohort test failed.");
    }

    if (report.convertedUsers != 3) {
        throw runtime_error("Conversion test failed.");
    }

    if (
        report.steps[1].users != 7 ||
        report.steps[2].users != 5 ||
        report.steps[3].users != 4
    ) {
        throw runtime_error("Intermediate funnel test failed.");
    }

    FunnelReport organic = engine.analyze("organic");

    if (organic.totalUsers != 3) {
        throw runtime_error("Channel segmentation test failed.");
    }

    FunnelReport nonexistent = engine.analyze("unknown");

    if (nonexistent.totalUsers != 0) {
        throw runtime_error("Empty segment test failed.");
    }

    cout << "\nAll C++17 funnel tests passed.\n";
}

int main() {
    try {
        EventStore store;

        store.addBatch(generateSampleEvents());

        FunnelDefinition funnel{
            "E-commerce Purchase Funnel",
            {
                EventType::Visit,
                EventType::ProductView,
                EventType::AddToCart,
                EventType::Checkout,
                EventType::Purchase
            },
            24 * 60 * 60
        };

        FunnelGovernanceEngine engine(store, funnel);

        printReport(engine.analyze());

        cout << "\nCHANNEL SEGMENTATION\n";

        for (const string& channel : {
            "organic", "paid", "referral"
        }) {
            FunnelReport report = engine.analyze(channel);

            cout << channel << ": "
                 << report.convertedUsers << "/"
                 << report.totalUsers << ", "
                 << fixed << setprecision(2)
                 << report.overallConversionRate << "%\n";
        }

        cout << "\nDEVICE SEGMENTATION\n";

        for (const string& device : {
            "mobile", "desktop"
        }) {
            FunnelReport report = engine.analyze("", device);

            cout << device << ": "
                 << report.convertedUsers << "/"
                 << report.totalUsers << ", "
                 << report.overallConversionRate << "%\n";
        }

        runTests(engine);

        cout << "\nStored events: " << store.size() << '\n';

    } catch (const exception& error) {
        cerr << "Funnel analytics error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
