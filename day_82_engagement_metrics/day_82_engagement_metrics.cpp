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
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

enum class EventType {
    Login,
    PageView,
    Action,
    Purchase,
    Logout
};

string eventName(EventType type) {
    switch (type) {
        case EventType::Login: return "LOGIN";
        case EventType::PageView: return "PAGE_VIEW";
        case EventType::Action: return "ACTION";
        case EventType::Purchase: return "PURCHASE";
        case EventType::Logout: return "LOGOUT";
    }
    return "UNKNOWN";
}

bool qualifies(EventType type) {
    return type != EventType::Logout;
}

struct Event {
    string eventId;
    string userId;
    EventType type;
    long long timestamp;

    void validate() const {
        if (eventId.empty() || userId.empty()) {
            throw invalid_argument("Event ID and user ID are required.");
        }

        if (timestamp < 0) {
            throw invalid_argument("Negative timestamps are invalid.");
        }
    }
};

struct Session {
    string userId;
    long long start;
    long long lastEvent;
    size_t eventCount = 1;

    double durationSeconds() const {
        return static_cast<double>(lastEvent - start);
    }
};

struct Metrics {
    int dau = 0;
    int wau = 0;
    int mau = 0;
    double stickiness = 0.0;
    int eventCount = 0;
    int sessionCount = 0;
    double averageSessionDuration = 0.0;
    double averageSessionsPerUser = 0.0;
    double averageEventsPerSession = 0.0;
};

class EngagementEngine {
private:
    vector<Event> events;
    unordered_set<string> eventIds;
    long long sessionTimeout;

    static constexpr long long DAY = 86400;

    vector<Event> eventsInRange(
        long long start,
        long long end
    ) const {
        vector<Event> result;

        for (const auto& event : events) {
            if (
                qualifies(event.type) &&
                event.timestamp >= start &&
                event.timestamp < end
            ) {
                result.push_back(event);
            }
        }

        return result;
    }

    set<string> activeUsers(
        long long start,
        long long end
    ) const {
        set<string> users;

        for (const auto& event : events) {
            if (
                qualifies(event.type) &&
                event.timestamp >= start &&
                event.timestamp < end
            ) {
                users.insert(event.userId);
            }
        }

        return users;
    }

public:
    explicit EngagementEngine(long long timeoutSeconds = 1800)
        : sessionTimeout(timeoutSeconds) {
        if (timeoutSeconds <= 0 || timeoutSeconds > 86400) {
            throw invalid_argument("Invalid session timeout.");
        }
    }

    bool ingest(const Event& event) {
        event.validate();

        if (eventIds.count(event.eventId)) {
            return false;
        }

        eventIds.insert(event.eventId);
        events.push_back(event);

        return true;
    }

    size_t ingestBatch(const vector<Event>& batch) {
        size_t accepted = 0;

        for (const auto& event : batch) {
            if (ingest(event)) {
                ++accepted;
            }
        }

        return accepted;
    }

    vector<Session> createSessions(
        const vector<Event>& input
    ) const {
        unordered_map<string, vector<Event>> byUser;

        for (const auto& event : input) {
            if (qualifies(event.type)) {
                byUser[event.userId].push_back(event);
            }
        }

        vector<Session> result;

        for (auto& entry : byUser) {
            auto& userEvents = entry.second;

            sort(
                userEvents.begin(),
                userEvents.end(),
                [](const Event& a, const Event& b) {
                    if (a.timestamp != b.timestamp) {
                        return a.timestamp < b.timestamp;
                    }
                    return a.eventId < b.eventId;
                }
            );

            bool initialized = false;
            Session current{};

            for (const auto& event : userEvents) {
                if (
                    !initialized ||
                    event.timestamp - current.lastEvent > sessionTimeout
                ) {
                    if (initialized) {
                        result.push_back(current);
                    }

                    current = Session{
                        event.userId,
                        event.timestamp,
                        event.timestamp,
                        1
                    };

                    initialized = true;
                } else {
                    current.lastEvent = event.timestamp;
                    ++current.eventCount;
                }
            }

            if (initialized) {
                result.push_back(current);
            }
        }

        sort(
            result.begin(),
            result.end(),
            [](const Session& a, const Session& b) {
                if (a.start != b.start) {
                    return a.start < b.start;
                }
                return a.userId < b.userId;
            }
        );

        return result;
    }

    Metrics calculate(long long reportDayStart) const {
        if (reportDayStart < 0) {
            throw invalid_argument("Invalid reporting boundary.");
        }

        const long long dayEnd = reportDayStart + DAY;

        const auto dauUsers = activeUsers(
            reportDayStart,
            dayEnd
        );

        const auto wauUsers = activeUsers(
            reportDayStart - 6 * DAY,
            dayEnd
        );

        const auto mauUsers = activeUsers(
            reportDayStart - 29 * DAY,
            dayEnd
        );

        const auto dailyEvents = eventsInRange(
            reportDayStart,
            dayEnd
        );

        const auto sessions = createSessions(dailyEvents);

        Metrics metrics;

        metrics.dau = static_cast<int>(dauUsers.size());
        metrics.wau = static_cast<int>(wauUsers.size());
        metrics.mau = static_cast<int>(mauUsers.size());

        metrics.stickiness = metrics.mau
            ? 100.0 * metrics.dau / metrics.mau
            : 0.0;

        metrics.eventCount = static_cast<int>(dailyEvents.size());
        metrics.sessionCount = static_cast<int>(sessions.size());

        double totalDuration = 0.0;
        size_t totalSessionEvents = 0;

        set<string> sessionUsers;

        for (const auto& session : sessions) {
            totalDuration += session.durationSeconds();
            totalSessionEvents += session.eventCount;
            sessionUsers.insert(session.userId);
        }

        if (!sessions.empty()) {
            metrics.averageSessionDuration =
                totalDuration / sessions.size();

            metrics.averageEventsPerSession =
                static_cast<double>(totalSessionEvents) / sessions.size();
        }

        if (!sessionUsers.empty()) {
            metrics.averageSessionsPerUser =
                static_cast<double>(sessions.size()) / sessionUsers.size();
        }

        return metrics;
    }

    map<int, int> frequencyDistribution(
        long long reportDayStart
    ) const {
        const auto dailyEvents = eventsInRange(
            reportDayStart,
            reportDayStart + DAY
        );

        const auto sessions = createSessions(dailyEvents);

        unordered_map<string, int> userCounts;

        for (const auto& session : sessions) {
            ++userCounts[session.userId];
        }

        map<int, int> distribution;

        for (const auto& entry : userCounts) {
            ++distribution[entry.second];
        }

        return distribution;
    }

    size_t eventCount() const {
        return events.size();
    }
};

void printMetrics(const Metrics& m) {
    cout << fixed << setprecision(2);

    cout << "\nENGAGEMENT METRICS\n";
    cout << "DAU: " << m.dau << '\n';
    cout << "WAU: " << m.wau << '\n';
    cout << "MAU: " << m.mau << '\n';
    cout << "Stickiness: " << m.stickiness << "%\n";
    cout << "Qualifying events: " << m.eventCount << '\n';
    cout << "Sessions: " << m.sessionCount << '\n';
    cout << "Average session duration: "
         << m.averageSessionDuration << " seconds\n";
    cout << "Average sessions per user: "
         << m.averageSessionsPerUser << '\n';
    cout << "Average events per session: "
         << m.averageEventsPerSession << '\n';
}

int main() {
    try {
        EngagementEngine engine(1800);

        const long long day17 = 1794873600LL;
        const long long day18 = 1794960000LL;
        const long long day19 = 1795046400LL;

        vector<Event> sample = {
            {"e1", "user_001", EventType::Login, day19 + 32400},
            {"e2", "user_001", EventType::PageView, day19 + 32700},
            {"e3", "user_001", EventType::Action, day19 + 33300},
            {"e4", "user_001", EventType::Login, day19 + 39600},
            {"e5", "user_002", EventType::Login, day19 + 36000},
            {"e6", "user_002", EventType::Purchase, day19 + 36600},
            {"e7", "user_003", EventType::PageView, day18 + 43200},
            {"e8", "user_003", EventType::Action, day17 + 43200},
            {"e9", "user_004", EventType::Login, day19 - 18 * DAY},
            {"e10", "user_005", EventType::Logout, day19 + 43200}
        };

        const size_t accepted = engine.ingestBatch(sample);

        cout << "Accepted events: " << accepted << '\n';

        // Repeated event IDs are rejected without changing state.
        bool duplicateAccepted = engine.ingest(sample.front());

        cout << "Duplicate accepted: "
             << boolalpha << duplicateAccepted << '\n';

        Metrics report = engine.calculate(day19);
        printMetrics(report);

        cout << "\nSESSION FREQUENCY DISTRIBUTION\n";

        for (const auto& entry :
             engine.frequencyDistribution(day19)) {
            cout << entry.first << " sessions: "
                 << entry.second << " users\n";
        }

        // Invariants for the sample reporting date.
        if (
            report.dau != 2 ||
            report.wau != 3 ||
            report.mau != 4 ||
            fabs(report.stickiness - 50.0) > 0.001 ||
            accepted != 10 ||
            duplicateAccepted
        ) {
            throw runtime_error("Metric validation failed.");
        }

        EngagementEngine emptyEngine;
        Metrics emptyReport = emptyEngine.calculate(day19);

        if (
            emptyReport.dau != 0 ||
            emptyReport.mau != 0 ||
            emptyReport.stickiness != 0.0
        ) {
            throw runtime_error("Empty dataset validation failed.");
        }

        cout << "\nAll validation checks passed.\n";

    } catch (const exception& error) {
        cerr << "Analytics failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
