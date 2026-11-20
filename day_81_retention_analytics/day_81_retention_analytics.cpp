#include <algorithm>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

using Day = long long;

constexpr Day SECONDS_PER_DAY = 86400;

enum class EventType {
    SIGNUP,
    ACTIVE,
    LOGIN,
    PURCHASE
};

enum class UserStatus {
    ACTIVE,
    CHURNED,
    NOT_ELIGIBLE
};

struct Event {
    string userId;
    Day day;
    EventType type;
};

struct User {
    string id;
    Day signup;
    Day lastActive;
    set<Day> activities;
};

struct RetentionResult {
    int interval;
    int eligible;
    int retained;
    double percentage;
};

struct ChurnResult {
    int active = 0;
    int churned = 0;
    int notEligible = 0;
};

struct Resurrection {
    string userId;
    Day previousActivity;
    Day resurrectionDate;
    Day inactiveDays;
};

class DateUtil {
public:
    static Day parse(const string& input) {
        tm value = {};

        istringstream stream(input);
        stream >> get_time(&value, "%Y-%m-%d");

        if (stream.fail()) {
            throw invalid_argument("Invalid date: " + input);
        }

        char extra;
        if (stream >> extra) {
            throw invalid_argument("Unexpected date characters");
        }

        value.tm_hour = 0;
        value.tm_min = 0;
        value.tm_sec = 0;
        value.tm_isdst = 0;

        const time_t timestamp = timegm(&value);

        tm normalized = {};
        gmtime_r(&timestamp, &normalized);

        if (normalized.tm_year != value.tm_year ||
            normalized.tm_mon != value.tm_mon ||
            normalized.tm_mday != value.tm_mday) {
            throw invalid_argument("Invalid calendar date");
        }

        return static_cast<Day>(timestamp / SECONDS_PER_DAY);
    }

    static string format(Day day) {
        time_t timestamp = static_cast<time_t>(
            day * SECONDS_PER_DAY
        );

        tm value = {};
        gmtime_r(&timestamp, &value);

        ostringstream stream;
        stream << put_time(&value, "%Y-%m-%d");
        return stream.str();
    }

    static string month(Day day) {
        return format(day).substr(0, 7);
    }
};

class RetentionEngine {
private:
    int churnDays;

    // Ordered sets prevent duplicate activity from inflating retention.
    unordered_map<string, vector<Event>> rawEvents;
    unordered_map<string, User> users;

    bool processed = false;

    static bool isActivity(EventType type) {
        return type == EventType::ACTIVE ||
               type == EventType::LOGIN ||
               type == EventType::PURCHASE;
    }

public:
    explicit RetentionEngine(int threshold = 30)
        : churnDays(threshold) {
        if (threshold < 1) {
            throw invalid_argument(
                "Churn threshold must be positive"
            );
        }
    }

    void addEvent(const Event& event) {
        if (event.userId.empty() || event.userId.size() > 128) {
            throw invalid_argument("Invalid user ID");
        }

        rawEvents[event.userId].push_back(event);
        processed = false;
    }

    void process() {
        unordered_map<string, User> nextUsers;

        for (const auto& entry : rawEvents) {
            const string& userId = entry.first;
            const auto& events = entry.second;

            Day signup = -1;
            set<Day> activities;

            // Events are sorted to determine the earliest signup.
            vector<Event> ordered = events;

            sort(
                ordered.begin(),
                ordered.end(),
                [](const Event& a, const Event& b) {
                    if (a.day != b.day) return a.day < b.day;
                    return static_cast<int>(a.type) <
                           static_cast<int>(b.type);
                }
            );

            for (const Event& event : ordered) {
                if (event.type == EventType::SIGNUP) {
                    if (signup == -1 || event.day < signup) {
                        signup = event.day;
                    }
                }
            }

            if (signup == -1) {
                throw runtime_error(
                    "User has no signup event: " + userId
                );
            }

            for (const Event& event : ordered) {
                if (isActivity(event.type) &&
                    event.day >= signup) {
                    activities.insert(event.day);
                }
            }

            Day lastActive = signup;

            if (!activities.empty()) {
                lastActive = *activities.rbegin();
            }

            nextUsers.emplace(
                userId,
                User{
                    userId,
                    signup,
                    lastActive,
                    move(activities)
                }
            );
        }

        users.swap(nextUsers);
        processed = true;

        cout << "Processed " << users.size() << " users.\n";
    }

    void requireProcessed() const {
        if (!processed || users.empty()) {
            throw runtime_error(
                "Process events before running analytics"
            );
        }
    }

    vector<RetentionResult> retentionCurve(
        Day observation,
        const vector<int>& intervals
    ) const {
        requireProcessed();

        vector<RetentionResult> results;

        set<int> uniqueIntervals(
            intervals.begin(),
            intervals.end()
        );

        for (int interval : uniqueIntervals) {
            if (interval < 0) {
                throw invalid_argument(
                    "Negative retention interval"
                );
            }

            int eligible = 0;
            int retained = 0;

            for (const auto& entry : users) {
                const User& user = entry.second;

                const Day target = user.signup + interval;

                if (target > observation) {
                    continue;
                }

                eligible++;

                if (user.activities.count(target)) {
                    retained++;
                }
            }

            const double percentage = eligible
                ? 100.0 * retained / eligible
                : 0.0;

            results.push_back({
                interval,
                eligible,
                retained,
                percentage
            });
        }

        return results;
    }

    map<string, map<int, double>> cohortRetention(
        Day observation,
        int maxAge
    ) const {
        requireProcessed();

        if (maxAge < 0) {
            throw invalid_argument("Invalid maximum cohort age");
        }

        map<string, vector<const User*>> cohorts;

        for (const auto& entry : users) {
            const User& user = entry.second;
            cohorts[DateUtil::month(user.signup)].push_back(&user);
        }

        map<string, map<int, double>> report;

        for (const auto& cohort : cohorts) {
            const auto& members = cohort.second;

            for (int age = 0; age <= maxAge; ++age) {
                int eligible = 0;
                int retained = 0;

                for (const User* user : members) {
                    const Day target = user->signup + age;

                    if (target > observation) {
                        continue;
                    }

                    eligible++;

                    if (user->activities.count(target)) {
                        retained++;
                    }
                }

                if (eligible > 0) {
                    report[cohort.first][age] =
                        100.0 * retained / eligible;
                }
            }
        }

        return report;
    }

    ChurnResult churnAnalysis(Day observation) const {
        requireProcessed();

        ChurnResult result;

        for (const auto& entry : users) {
            const User& user = entry.second;

            if (observation < user.signup) {
                throw invalid_argument(
                    "Observation precedes signup"
                );
            }

            const Day tenure = observation - user.signup;

            if (tenure < churnDays) {
                result.notEligible++;
                continue;
            }

            const Day inactive = observation - user.lastActive;

            if (inactive >= churnDays) {
                result.churned++;
            } else {
                result.active++;
            }
        }

        return result;
    }

    vector<Resurrection> resurrectionAnalysis(
        Day observation
    ) const {
        requireProcessed();

        vector<Resurrection> results;

        for (const auto& entry : users) {
            const User& user = entry.second;

            if (user.activities.size() < 2) {
                continue;
            }

            auto previous = user.activities.begin();
            auto current = next(previous);

            while (current != user.activities.end()) {
                const Day gap = *current - *previous;

                if (gap >= churnDays && *current <= observation) {
                    results.push_back({
                        user.id,
                        *previous,
                        *current,
                        gap
                    });
                }

                previous = current;
                ++current;
            }
        }

        return results;
    }

    void printReport(Day observation) const {
        cout << "\n====================================\n";
        cout << "       RETENTION ANALYTICS\n";
        cout << "====================================\n";

        cout << "Observation: "
             << DateUtil::format(observation) << "\n";

        cout << "Total users: " << users.size() << "\n";

        cout << "\nRETENTION CURVE\n";

        const auto curve = retentionCurve(
            observation,
            {0, 1, 7, 14, 30}
        );

        for (const auto& result : curve) {
            cout << "D" << result.interval
                 << " | Eligible: " << result.eligible
                 << " | Retained: " << result.retained
                 << " | Rate: " << fixed << setprecision(2)
                 << result.percentage << "%\n";
        }

        cout << "\nCOHORT RETENTION\n";

        const auto cohorts = cohortRetention(observation, 30);

        for (const auto& cohort : cohorts) {
            cout << cohort.first << "\n";

            for (const auto& period : cohort.second) {
                cout << "  D" << period.first
                     << ": " << fixed << setprecision(2)
                     << period.second << "%\n";
            }
        }

        cout << "\nCHURN ANALYSIS\n";

        const ChurnResult churn = churnAnalysis(observation);

        const int eligible = churn.active + churn.churned;

        cout << "Active: " << churn.active << "\n";
        cout << "Churned: " << churn.churned << "\n";
        cout << "Not eligible: " << churn.notEligible << "\n";

        cout << "Churn rate: "
             << fixed << setprecision(2)
             << (eligible
                 ? 100.0 * churn.churned / eligible
                 : 0.0)
             << "%\n";

        cout << "\nRESURRECTION ANALYSIS\n";

        const auto resurrections =
            resurrectionAnalysis(observation);

        set<string> resurrectedUsers;

        for (const auto& event : resurrections) {
            resurrectedUsers.insert(event.userId);

            cout << event.userId
                 << " | Previous: "
                 << DateUtil::format(event.previousActivity)
                 << " | Returned: "
                 << DateUtil::format(event.resurrectionDate)
                 << " | Inactive days: "
                 << event.inactiveDays << "\n";
        }

        cout << "Resurrected users: "
             << resurrectedUsers.size() << "\n";

        cout << "Resurrection events: "
             << resurrections.size() << "\n";
    }
};

vector<Event> sampleEvents() {
    vector<Event> events;

    auto add = [&](string user, string date, EventType type) {
        events.push_back({
            move(user),
            DateUtil::parse(date),
            type
        });
    };

    add("U001", "2026-01-01", EventType::SIGNUP);
    add("U001", "2026-01-01", EventType::ACTIVE);
    add("U001", "2026-01-02", EventType::ACTIVE);
    add("U001", "2026-01-08", EventType::ACTIVE);
    add("U001", "2026-03-05", EventType::ACTIVE);

    add("U002", "2026-01-03", EventType::SIGNUP);
    add("U002", "2026-01-03", EventType::ACTIVE);

    add("U003", "2026-01-10", EventType::SIGNUP);
    add("U003", "2026-01-10", EventType::ACTIVE);
    add("U003", "2026-02-15", EventType::ACTIVE);

    add("U004", "2026-02-01", EventType::SIGNUP);
    add("U004", "2026-02-01", EventType::ACTIVE);
    add("U004", "2026-02-02", EventType::ACTIVE);

    add("U005", "2026-02-05", EventType::SIGNUP);
    add("U005", "2026-02-05", EventType::ACTIVE);

    add("U006", "2026-02-15", EventType::SIGNUP);
    add("U006", "2026-02-15", EventType::ACTIVE);
    add("U006", "2026-03-20", EventType::ACTIVE);

    add("U007", "2026-03-01", EventType::SIGNUP);
    add("U007", "2026-03-01", EventType::ACTIVE);

    add("U008", "2026-03-10", EventType::SIGNUP);
    add("U008", "2026-03-10", EventType::ACTIVE);

    add("U009", "2026-03-15", EventType::SIGNUP);
    add("U009", "2026-03-15", EventType::ACTIVE);

    return events;
}

void runTests() {
    RetentionEngine engine(30);

    for (const auto& event : sampleEvents()) {
        engine.addEvent(event);
    }

    engine.process();

    const Day observation = DateUtil::parse("2026-05-01");

    const auto curve = engine.retentionCurve(
        observation,
        {0, 1, 7}
    );

    if (curve.empty() ||
        curve.front().retained != 9 ||
        curve.front().percentage != 100.0) {
        throw runtime_error("Retention test failed");
    }

    const auto churn = engine.churnAnalysis(observation);

    if (churn.active + churn.churned != 9) {
        throw runtime_error("Churn eligibility test failed");
    }

    const auto resurrection =
        engine.resurrectionAnalysis(observation);

    if (resurrection.empty()) {
        throw runtime_error("Resurrection test failed");
    }

    bool rejected = false;

    try {
        RetentionEngine invalidEngine(0);
    } catch (const invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Threshold validation failed");
    }

    cout << "All C++17 tests passed.\n";
}

int main(int argc, char* argv[]) {
    try {
        if (argc > 1 && string(argv[1]) == "--test") {
            runTests();
            return 0;
        }

        RetentionEngine engine(30);

        for (const auto& event : sampleEvents()) {
            engine.addEvent(event);
        }

        engine.process();

        engine.printReport(
            DateUtil::parse("2026-05-01")
        );

        return 0;

    } catch (const exception& error) {
        cerr << "Analytics failure: "
             << error.what() << "\n";

        return 1;
    }
}
