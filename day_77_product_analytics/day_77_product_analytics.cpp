#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * Product Analytics and Governance Engine
 *
 * C++17 implementation of:
 * - User and event domain modeling
 * - Event property validation
 * - Duplicate detection
 * - Sessionization
 * - Ordered conversion funnels
 * - Cohort retention
 * - Revenue aggregation
 * - Analytics reporting
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic product_analytics.cpp -o analytics
 *
 * Run:
 * ./analytics
 */

// ============================================================
// 1. Domain types
// ============================================================

enum class EventType {
    Signup,
    Login,
    PageView,
    ProductView,
    AddToCart,
    CheckoutStarted,
    Purchase
};

string eventName(EventType type) {
    switch (type) {
        case EventType::Signup: return "signup";
        case EventType::Login: return "login";
        case EventType::PageView: return "page_view";
        case EventType::ProductView: return "product_view";
        case EventType::AddToCart: return "add_to_cart";
        case EventType::CheckoutStarted: return "checkout_started";
        case EventType::Purchase: return "purchase";
    }

    throw runtime_error("Unknown event type.");
}

struct User {
    string id;
    string country;
    string plan;
    int creationMinute;
};

struct Event {
    string id;
    string userId;
    EventType type;
    int timestampMinute;
    string sessionId;
    map<string, string> properties;
};

struct Session {
    string id;
    string userId;
    int startedAt;
    int lastEventAt;
    int eventCount = 0;
    set<string> eventNames;

    int duration() const {
        return max(0, lastEventAt - startedAt);
    }
};

struct FunnelResult {
    vector<string> steps;
    vector<int> counts;
    vector<double> rates;
    double overallConversion = 0.0;
};

struct CohortResult {
    string month;
    int users = 0;
    map<int, int> retained;
};


// ============================================================
// 2. Utility functions
// ============================================================

void require(bool condition, const string& message) {
    if (!condition) {
        throw invalid_argument(message);
    }
}

string monthKey(int absoluteMinute) {
    // The simulation uses a 30-day month for compact test data.
    int absoluteDay = absoluteMinute / 1440;
    int month = absoluteDay / 30 + 1;

    return "2026-" + (month < 10 ? "0" : "") +
           to_string(month);
}

int monthIndex(const string& month) {
    size_t separator = month.find('-');

    if (separator == string::npos) {
        throw invalid_argument("Invalid cohort month.");
    }

    return stoi(month.substr(separator + 1));
}

int monthOffset(const string& first, const string& second) {
    int firstYear = stoi(first.substr(0, 4));
    int secondYear = stoi(second.substr(0, 4));

    return (secondYear - firstYear) * 12 +
           monthIndex(second) - monthIndex(first);
}


// ============================================================
// 3. Event repository
// ============================================================

class EventRepository {
private:
    unordered_map<string, User> users;
    unordered_set<string> eventIds;
    vector<Event> events;

    static void validateEvent(const Event& event) {
        require(!event.id.empty(), "Empty event ID.");
        require(!event.userId.empty(), "Empty user ID.");
        require(event.timestampMinute >= 0, "Negative timestamp.");
        require(event.properties.size() <= 50, "Property limit exceeded.");

        for (const auto& property : event.properties) {
            require(!property.first.empty(), "Empty property key.");
            require(property.second.size() <= 2000,
                    "Property value too large.");
        }
    }

public:
    void registerUser(const User& user) {
        require(!user.id.empty(), "Empty user ID.");

        auto result = users.emplace(user.id, user);

        if (!result.second) {
            throw runtime_error("Duplicate user registration.");
        }
    }

    void addEvent(const Event& event) {
        validateEvent(event);

        require(users.count(event.userId) > 0,
                "Event references unknown user.");

        if (!eventIds.insert(event.id).second) {
            throw runtime_error("Duplicate event ID.");
        }

        events.push_back(event);
    }

    void addBatch(const vector<Event>& batch) {
        unordered_set<string> batchIds;

        for (const auto& event : batch) {
            validateEvent(event);

            require(users.count(event.userId) > 0,
                    "Unknown user in batch.");

            require(eventIds.count(event.id) == 0,
                    "Existing event ID in batch.");

            require(batchIds.insert(event.id).second,
                    "Duplicate ID within batch.");
        }

        // Validate the entire batch before modifying repository state.
        for (const auto& event : batch) {
            eventIds.insert(event.id);
            events.push_back(event);
        }
    }

    const vector<Event>& getEvents() const {
        return events;
    }

    const unordered_map<string, User>& getUsers() const {
        return users;
    }

    vector<Event> findByUser(const string& userId) const {
        vector<Event> result;

        for (const auto& event : events) {
            if (event.userId == userId) {
                result.push_back(event);
            }
        }

        return result;
    }
};


// ============================================================
// 4. Sessionization engine
// ============================================================

class SessionEngine {
private:
    int timeoutMinutes;

public:
    explicit SessionEngine(int timeout = 30)
        : timeoutMinutes(timeout) {
        require(timeout > 0, "Invalid session timeout.");
    }

    vector<Session> build(
        const vector<Event>& events
    ) const {
        unordered_map<string, vector<Event>> grouped;

        for (const auto& event : events) {
            grouped[event.userId].push_back(event);
        }

        vector<Session> sessions;

        for (auto& entry : grouped) {
            auto& userEvents = entry.second;

            sort(
                userEvents.begin(),
                userEvents.end(),
                [](const Event& a, const Event& b) {
                    if (a.timestampMinute != b.timestampMinute) {
                        return a.timestampMinute < b.timestampMinute;
                    }
                    return a.id < b.id;
                }
            );

            Session* current = nullptr;

            for (const auto& event : userEvents) {
                bool expired =
                    current == nullptr ||
                    event.timestampMinute - current->lastEventAt >
                        timeoutMinutes;

                bool explicitChange =
                    current != nullptr &&
                    !event.sessionId.empty() &&
                    current->id != event.sessionId;

                if (expired || explicitChange) {
                    sessions.push_back({
                        event.sessionId.empty()
                            ? event.id + "-SESSION"
                            : event.sessionId,
                        event.userId,
                        event.timestampMinute,
                        event.timestampMinute,
                        0,
                        {}
                    });

                    current = &sessions.back();
                }

                current->lastEventAt = max(
                    current->lastEventAt,
                    event.timestampMinute
                );

                current->eventCount++;
                current->eventNames.insert(
                    eventName(event.type)
                );
            }
        }

        return sessions;
    }
};


// ============================================================
// 5. Product metrics
// ============================================================

class MetricsEngine {
public:
    struct Result {
        int totalEvents = 0;
        int activeUsers = 0;
        double revenue = 0.0;
        double averageOrderValue = 0.0;

        map<string, int> eventCounts;
        map<string, int> uniqueUsers;
    };

    Result calculate(const vector<Event>& events) const {
        Result result;

        unordered_set<string> activeUsers;
        map<string, unordered_set<string>> eventUsers;

        int purchases = 0;

        for (const auto& event : events) {
            string name = eventName(event.type);

            result.totalEvents++;
            result.eventCounts[name]++;
            activeUsers.insert(event.userId);
            eventUsers[name].insert(event.userId);

            if (event.type == EventType::Purchase) {
                auto amount = event.properties.find("amount");

                require(
                    amount != event.properties.end(),
                    "Purchase requires amount."
                );

                double value = stod(amount->second);

                require(
                    isfinite(value) && value >= 0,
                    "Invalid purchase amount."
                );

                result.revenue += value;
                purchases++;
            }
        }

        result.activeUsers = static_cast<int>(activeUsers.size());

        for (const auto& entry : eventUsers) {
            result.uniqueUsers[entry.first] =
                static_cast<int>(entry.second.size());
        }

        if (purchases > 0) {
            result.averageOrderValue =
                result.revenue / purchases;
        }

        return result;
    }
};


// ============================================================
// 6. Funnel engine
// ============================================================

class FunnelEngine {
public:
    FunnelResult evaluate(
        const vector<Event>& events,
        const vector<EventType>& steps,
        int conversionWindowMinutes = 10080
    ) const {
        require(steps.size() >= 2,
                "A funnel requires at least two steps.");

        require(conversionWindowMinutes > 0,
                "Invalid funnel window.");

        set<EventType> uniqueSteps(
            steps.begin(),
            steps.end()
        );

        require(uniqueSteps.size() == steps.size(),
                "Duplicate funnel step.");

        unordered_map<string, vector<Event>> grouped;

        for (const auto& event : events) {
            grouped[event.userId].push_back(event);
        }

        FunnelResult result;

        result.counts.assign(steps.size(), 0);

        for (EventType type : steps) {
            result.steps.push_back(eventName(type));
        }

        for (auto& entry : grouped) {
            auto& userEvents = entry.second;

            sort(
                userEvents.begin(),
                userEvents.end(),
                [](const Event& a, const Event& b) {
                    return a.timestampMinute < b.timestampMinute;
                }
            );

            size_t cursor = 0;
            int firstTimestamp = -1;

            for (const auto& event : userEvents) {
                if (event.type != steps[cursor]) {
                    continue;
                }

                if (firstTimestamp < 0) {
                    firstTimestamp = event.timestampMinute;
                } else if (
                    event.timestampMinute - firstTimestamp >
                    conversionWindowMinutes
                ) {
                    break;
                }

                result.counts[cursor]++;

                cursor++;

                if (cursor == steps.size()) {
                    break;
                }
            }
        }

        result.rates.resize(steps.size(), 0.0);

        for (size_t i = 0; i < steps.size(); i++) {
            if (i == 0) {
                result.rates[i] =
                    result.counts[i] > 0 ? 100.0 : 0.0;
            } else if (result.counts[i - 1] > 0) {
                result.rates[i] =
                    100.0 * result.counts[i] /
                    result.counts[i - 1];
            }
        }

        if (result.counts.front() > 0) {
            result.overallConversion =
                100.0 * result.counts.back() /
                result.counts.front();
        }

        return result;
    }
};


// ============================================================
// 7. Cohort analysis
// ============================================================

class CohortEngine {
public:
    vector<CohortResult> analyze(
        const unordered_map<string, User>& users,
        const vector<Event>& events
    ) const {
        unordered_map<string, unordered_set<string>> activity;

        for (const auto& event : events) {
            activity[event.userId].insert(
                monthKey(event.timestampMinute)
            );
        }

        map<string, vector<string>> cohorts;

        for (const auto& entry : users) {
            cohorts[monthKey(entry.second.creationMinute)]
                .push_back(entry.first);
        }

        vector<CohortResult> results;

        for (const auto& cohort : cohorts) {
            CohortResult result;

            result.month = cohort.first;
            result.users = static_cast<int>(
                cohort.second.size()
            );

            for (const auto& userId : cohort.second) {
                auto found = activity.find(userId);

                if (found == activity.end()) {
                    continue;
                }

                for (const auto& activeMonth : found->second) {
                    int offset = monthOffset(
                        cohort.first,
                        activeMonth
                    );

                    if (offset >= 0) {
                        result.retained[offset]++;
                    }
                }
            }

            result.retained[0] = result.users;
            results.push_back(result);
        }

        return results;
    }
};


// ============================================================
// 8. Test data
// ============================================================

vector<Event> makeJourney(
    const string& userId,
    int base,
    const vector<pair<EventType, int>>& journey,
    const vector<double>& purchaseAmounts = {}
) {
    vector<Event> result;

    int purchaseIndex = 0;

    for (size_t i = 0; i < journey.size(); i++) {
        Event event;

        event.id = userId + "-EVENT-" + to_string(i + 1);
        event.userId = userId;
        event.type = journey[i].first;
        event.timestampMinute = base + journey[i].second;
        event.sessionId = userId + "-SESSION-1";

        if (event.type == EventType::Purchase) {
            require(
                purchaseIndex < static_cast<int>(
                    purchaseAmounts.size()
                ),
                "Missing purchase amount."
            );

            ostringstream amount;

            amount << fixed << setprecision(2)
                   << purchaseAmounts[purchaseIndex++];

            event.properties["amount"] = amount.str();
        }

        result.push_back(event);
    }

    return result;
}


// ============================================================
// 9. Reporting
// ============================================================

void printReport(
    const MetricsEngine::Result& metrics,
    const vector<Session>& sessions,
    const FunnelResult& funnel,
    const vector<CohortResult>& cohorts
) {
    cout << "\nPRODUCT ANALYTICS REPORT\n";
    cout << "========================\n";

    cout << "Total events: " << metrics.totalEvents << '\n';
    cout << "Active users: " << metrics.activeUsers << '\n';

    cout << fixed << setprecision(2);

    cout << "Revenue: " << metrics.revenue << '\n';
    cout << "Average order value: "
         << metrics.averageOrderValue << '\n';

    cout << "\nEVENT COUNTS\n";

    for (const auto& entry : metrics.eventCounts) {
        cout << left << setw(25)
             << entry.first << entry.second << '\n';
    }

    cout << "\nSESSION ANALYSIS\n";

    int totalDuration = 0;

    for (const auto& session : sessions) {
        totalDuration += session.duration();
    }

    cout << "Sessions: " << sessions.size() << '\n';

    cout << "Average duration (minutes): "
         << (
             sessions.empty()
                 ? 0.0
                 : static_cast<double>(totalDuration) /
                   sessions.size()
         ) << '\n';

    cout << "\nCONVERSION FUNNEL\n";

    for (size_t i = 0; i < funnel.steps.size(); i++) {
        cout << setw(25) << left << funnel.steps[i]
             << " users=" << funnel.counts[i]
             << " conversion=" << funnel.rates[i]
             << "%\n";
    }

    cout << "Overall conversion: "
         << funnel.overallConversion << "%\n";

    cout << "\nCOHORT RETENTION\n";

    for (const auto& cohort : cohorts) {
        cout << cohort.month
             << " users=" << cohort.users << " retention=";

        for (const auto& entry : cohort.retained) {
            double rate = cohort.users > 0
                ? 100.0 * entry.second / cohort.users
                : 0.0;

            cout << " M" << entry.first
                 << "=" << rate << "%";
        }

        cout << '\n';
    }
}


// ============================================================
// 10. Main
// ============================================================

int main() {
    try {
        EventRepository repository;

        vector<User> users = {
            {"U001", "IN", "free", 0},
            {"U002", "IN", "premium", 120},
            {"U003", "US", "free", 1440},
            {"U004", "IN", "premium", 43200},
            {"U005", "GB", "free", 44640}
        };

        for (const auto& user : users) {
            repository.registerUser(user);
        }

        vector<Event> events;

        const vector<pair<EventType, int>> standardJourney = {
            {EventType::Signup, 0},
            {EventType::Login, 1},
            {EventType::ProductView, 3},
            {EventType::AddToCart, 5},
            {EventType::CheckoutStarted, 8},
            {EventType::Purchase, 12}
        };

        const vector<pair<EventType, int>> incompleteJourney = {
            {EventType::Signup, 0},
            {EventType::Login, 2},
            {EventType::ProductView, 4},
            {EventType::AddToCart, 6}
        };

        const vector<pair<EventType, int>> partialJourney = {
            {EventType::Signup, 0},
            {EventType::Login, 1},
            {EventType::ProductView, 3}
        };

        auto u1 = makeJourney(
            "U001", 0, standardJourney, {1499.0}
        );

        auto u2 = makeJourney(
            "U002", 120, standardJourney, {2499.0}
        );

        auto u3 = makeJourney(
            "U003", 1440, incompleteJourney
        );

        auto u4 = makeJourney(
            "U004", 43200, partialJourney
        );

        auto u5 = makeJourney(
            "U005", 44640, standardJourney, {799.0}
        );

        // Simulate later-month product activity.
        auto addActivity = [](
            const string& userId,
            int minute,
            const string& id
        ) {
            return Event{
                id,
                userId,
                EventType::PageView,
                minute,
                userId + "-SESSION-2",
                {{"page", "/dashboard"}}
            };
        };

        events.insert(events.end(), u1.begin(), u1.end());
        events.insert(events.end(), u2.begin(), u2.end());
        events.insert(events.end(), u3.begin(), u3.end());
        events.insert(events.end(), u4.begin(), u4.end());
        events.insert(events.end(), u5.begin(), u5.end());

        events.push_back(
            addActivity("U001", 31 * 1440, "U001-RETURN")
        );

        events.push_back(
            addActivity("U002", 32 * 1440, "U002-RETURN")
        );

        repository.addBatch(events);

        require(
            repository.getEvents().size() == 32,
            "Unexpected event count."
        );

        MetricsEngine metricsEngine;

        auto metrics = metricsEngine.calculate(
            repository.getEvents()
        );

        require(metrics.activeUsers == 5,
                "Incorrect active user count.");

        require(abs(metrics.revenue - 4797.0) < 0.001,
                "Incorrect revenue.");

        SessionEngine sessionEngine(30);

        auto sessions = sessionEngine.build(
            repository.getEvents()
        );

        FunnelEngine funnelEngine;

        auto funnel = funnelEngine.evaluate(
            repository.getEvents(),
            {
                EventType::Signup,
                EventType::ProductView,
                EventType::AddToCart,
                EventType::CheckoutStarted,
                EventType::Purchase
            }
        );

        require(funnel.counts[0] == 5,
                "Incorrect funnel entry count.");

        require(funnel.counts[4] == 3,
                "Incorrect funnel conversion count.");

        CohortEngine cohortEngine;

        auto cohorts = cohortEngine.analyze(
            repository.getUsers(),
            repository.getEvents()
        );

        require(!cohorts.empty(), "Missing cohorts.");

        // Duplicate event test.
        bool duplicateRejected = false;

        try {
            repository.addEvent(events.front());
        } catch (const exception&) {
            duplicateRejected = true;
        }

        require(duplicateRejected,
                "Duplicate event was not rejected.");

        // Unknown user test.
        bool unknownUserRejected = false;

        try {
            Event invalid{
                "INVALID-1",
                "UNKNOWN",
                EventType::PageView,
                100,
                "",
                {}
            };

            repository.addEvent(invalid);
        } catch (const exception&) {
            unknownUserRejected = true;
        }

        require(unknownUserRejected,
                "Unknown user was not rejected.");

        printReport(
            metrics,
            sessions,
            funnel,
            cohorts
        );

        cout << "\nVALIDATION\n";
        cout << "All repository and analytics tests passed.\n";

        return 0;

    } catch (const exception& error) {
        cerr << "Analytics failure: "
             << error.what() << '\n';

        return 1;
    }
}
