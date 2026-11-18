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
#include <vector>

using namespace std;

/*
 * AARRR Framework: Repository-independent Growth Governance Engine
 *
 * Implements an event-sourced product growth model:
 * Acquisition -> Activation -> Retention -> Revenue -> Referral
 *
 * C++17, standard library only.
 *
 * The implementation emphasizes:
 * - Strong domain types
 * - Deterministic metric calculation
 * - Data validation
 * - Customer lifecycle state
 * - Funnel conversion
 * - Cohort retention
 * - Revenue accounting
 * - Referral attribution
 * - Growth experiment analysis
 */

enum class Stage {
    Acquisition,
    Activation,
    Retention,
    Revenue,
    Referral
};

enum class EventType {
    Visit,
    Signup,
    Activation,
    Login,
    Purchase,
    ReferralSent,
    Cancellation
};

string toString(Stage stage) {
    switch (stage) {
        case Stage::Acquisition: return "Acquisition";
        case Stage::Activation: return "Activation";
        case Stage::Retention: return "Retention";
        case Stage::Revenue: return "Revenue";
        case Stage::Referral: return "Referral";
    }

    throw logic_error("Unknown growth stage.");
}

struct Event {
    string id;
    string userId;
    EventType type;
    int day;
    string source;
    string referrer;
    long long amountCents = 0;
};

struct Customer {
    string id;
    string source;
    int signupDay;
    int activationDay = -1;
    string referredBy;
    long long revenueCents = 0;
    int transactions = 0;
    int referralsSent = 0;
    bool cancelled = false;
    set<int> activeDays;

    bool activated() const {
        return activationDay >= 0;
    }

    bool paying() const {
        return revenueCents > 0;
    }
};

struct FunnelMetrics {
    size_t visitors = 0;
    size_t signups = 0;
    size_t activated = 0;
    size_t retained = 0;
    size_t paying = 0;
    size_t referred = 0;

    static double rate(size_t numerator, size_t denominator) {
        if (denominator == 0) return 0.0;

        return 100.0 * static_cast<double>(numerator) /
               static_cast<double>(denominator);
    }
};

struct ChannelMetrics {
    size_t visitors = 0;
    size_t signups = 0;

    double conversion() const {
        return visitors
            ? 100.0 * signups / visitors
            : 0.0;
    }
};

struct ExperimentResult {
    double controlRate;
    double treatmentRate;
    double absoluteLift;
    double relativeLift;
};

class GrowthException : public runtime_error {
public:
    using runtime_error::runtime_error;
};

class GrowthEngine {
private:
    unordered_map<string, Customer> customers;
    unordered_map<string, unordered_set<string>> channelVisitors;
    unordered_set<string> processedEvents;
    vector<Event> eventHistory;
    int activationWindowDays;

    void validateEvent(const Event& event) const {
        if (event.id.empty() || event.id.size() > 100) {
            throw GrowthException("Invalid event identifier.");
        }

        if (event.userId.empty() || event.userId.size() > 100) {
            throw GrowthException("Invalid customer identifier.");
        }

        if (event.day < 0) {
            throw GrowthException("Negative event day.");
        }

        if (event.amountCents < 0 ||
            event.amountCents > 10000000000LL) {
            throw GrowthException("Invalid monetary amount.");
        }
    }

public:
    explicit GrowthEngine(int activationWindow = 7)
        : activationWindowDays(activationWindow) {

        if (activationWindow < 0) {
            throw GrowthException("Invalid activation window.");
        }
    }

    void process(const Event& event) {
        validateEvent(event);

        if (processedEvents.count(event.id)) {
            throw GrowthException("Duplicate event.");
        }

        auto it = customers.find(event.userId);

        if (event.type == EventType::Visit) {
            if (event.source.empty()) {
                throw GrowthException("Missing acquisition channel.");
            }

            channelVisitors[event.source].insert(event.userId);
        }
        else if (event.type == EventType::Signup) {
            if (it != customers.end()) {
                throw GrowthException("Duplicate signup.");
            }

            if (event.source.empty()) {
                throw GrowthException("Missing acquisition channel.");
            }

            if (!event.referrer.empty()) {
                if (event.referrer == event.userId ||
                    customers.find(event.referrer) == customers.end()) {
                    throw GrowthException("Invalid referral attribution.");
                }
            }

            Customer customer;
            customer.id = event.userId;
            customer.source = event.source;
            customer.signupDay = event.day;
            customer.referredBy = event.referrer;

            customers.emplace(event.userId, move(customer));
        }
        else {
            if (it == customers.end()) {
                throw GrowthException("Customer does not exist.");
            }

            Customer& customer = it->second;

            switch (event.type) {
                case EventType::Activation:
                    if (customer.activated()) {
                        throw GrowthException("Already activated.");
                    }

                    if (event.day < customer.signupDay ||
                        event.day - customer.signupDay >
                            activationWindowDays) {
                        throw GrowthException(
                            "Activation outside permitted window."
                        );
                    }

                    customer.activationDay = event.day;
                    break;

                case EventType::Login:
                    if (event.day < customer.signupDay) {
                        throw GrowthException(
                            "Activity predates registration."
                        );
                    }

                    customer.activeDays.insert(event.day);
                    break;

                case EventType::Purchase:
                    if (!customer.activated()) {
                        throw GrowthException(
                            "Purchase requires activation."
                        );
                    }

                    if (event.amountCents <= 0) {
                        throw GrowthException(
                            "Purchase amount must be positive."
                        );
                    }

                    if (customer.revenueCents >
                        10000000000LL - event.amountCents) {
                        throw GrowthException("Revenue overflow.");
                    }

                    customer.revenueCents += event.amountCents;
                    ++customer.transactions;
                    break;

                case EventType::ReferralSent:
                    if (!customer.activated()) {
                        throw GrowthException(
                            "Referral requires activation."
                        );
                    }

                    ++customer.referralsSent;
                    break;

                case EventType::Cancellation:
                    customer.cancelled = true;
                    break;

                default:
                    throw GrowthException("Invalid event transition.");
            }
        }

        // Commit the event identifier only after validation and mutation.
        processedEvents.insert(event.id);
        eventHistory.push_back(event);
    }

    map<string, ChannelMetrics> acquisition() const {
        map<string, ChannelMetrics> result;

        for (const auto& [source, visitors] : channelVisitors) {
            result[source].visitors = visitors.size();
        }

        for (const auto& [id, customer] : customers) {
            ++result[customer.source].signups;
        }

        return result;
    }

    FunnelMetrics funnel() const {
        FunnelMetrics result;

        set<string> uniqueVisitors;

        for (const auto& [source, visitors] : channelVisitors) {
            uniqueVisitors.insert(visitors.begin(), visitors.end());
        }

        result.visitors = uniqueVisitors.size();
        result.signups = customers.size();

        for (const auto& [id, customer] : customers) {
            if (customer.activated()) ++result.activated;
            if (!customer.activeDays.empty()) ++result.retained;
            if (customer.paying()) ++result.paying;
            if (!customer.referredBy.empty()) ++result.referred;
        }

        return result;
    }

    map<int, pair<size_t, size_t>> retention(
        int periodDays = 7
    ) const {
        if (periodDays < 1) {
            throw GrowthException("Invalid retention period.");
        }

        map<int, pair<size_t, size_t>> cohorts;

        for (const auto& [id, customer] : customers) {
            auto& metrics = cohorts[customer.signupDay];

            ++metrics.first;

            bool retained = any_of(
                customer.activeDays.begin(),
                customer.activeDays.end(),
                [&](int day) {
                    return day >= customer.signupDay &&
                           day <= customer.signupDay + periodDays;
                }
            );

            if (retained) ++metrics.second;
        }

        return cohorts;
    }

    map<string, long long> revenueByChannel() const {
        map<string, long long> result;

        for (const auto& [id, customer] : customers) {
            result[customer.source] += customer.revenueCents;
        }

        return result;
    }

    map<string, size_t> referralCounts() const {
        map<string, size_t> result;

        for (const auto& [id, customer] : customers) {
            if (!customer.referredBy.empty()) {
                ++result[customer.referredBy];
            }
        }

        return result;
    }

    static ExperimentResult compareExperiment(
        const vector<bool>& control,
        const vector<bool>& treatment
    ) {
        if (control.empty() || treatment.empty()) {
            throw GrowthException("Experiment groups cannot be empty.");
        }

        double c = static_cast<double>(
            count(control.begin(), control.end(), true)
        ) / control.size();

        double t = static_cast<double>(
            count(treatment.begin(), treatment.end(), true)
        ) / treatment.size();

        return {
            c * 100.0,
            t * 100.0,
            (t - c) * 100.0,
            c > 0 ? (t / c - 1.0) * 100.0 : 0.0
        };
    }

    const unordered_map<string, Customer>& getCustomers() const {
        return customers;
    }

    size_t eventCount() const {
        return eventHistory.size();
    }
};

void printReport(const GrowthEngine& engine) {
    const FunnelMetrics f = engine.funnel();

    cout << fixed << setprecision(2);

    cout << "\n========== AARRR GROWTH REPORT ==========\n";

    cout << "\nACQUISITION\n";

    for (const auto& [source, metrics] : engine.acquisition()) {
        cout << source
             << " | Visitors: " << metrics.visitors
             << " | Signups: " << metrics.signups
             << " | Conversion: " << metrics.conversion()
             << "%\n";
    }

    cout << "\nACTIVATION\n";
    cout << "Registered: " << f.signups << '\n';
    cout << "Activated: " << f.activated << '\n';
    cout << "Activation rate: "
         << FunnelMetrics::rate(f.activated, f.signups) << "%\n";

    cout << "\nRETENTION\n";

    for (const auto& [day, metrics] : engine.retention()) {
        cout << "Signup day " << day
             << " | Cohort size: " << metrics.first
             << " | Retained: " << metrics.second
             << " | Rate: "
             << FunnelMetrics::rate(
                 metrics.second, metrics.first
             ) << "%\n";
    }

    cout << "\nREVENUE\n";

    for (const auto& [source, cents] : engine.revenueByChannel()) {
        cout << source << " | Revenue: $"
             << cents / 100.0 << '\n';
    }

    cout << "\nREFERRAL\n";

    for (const auto& [referrer, count] : engine.referralCounts()) {
        cout << referrer << " | Referred customers: "
             << count << '\n';
    }

    cout << "\nFUNNEL\n";
    cout << "Visitors: " << f.visitors << '\n';
    cout << "Signups: " << f.signups << '\n';
    cout << "Activated: " << f.activated << '\n';
    cout << "Retained: " << f.retained << '\n';
    cout << "Paying: " << f.paying << '\n';
    cout << "Referred: " << f.referred << '\n';

    cout << "\n=========================================\n";
}

int main() {
    try {
        GrowthEngine engine(7);
        int sequence = 1;

        auto add = [&](string user,
                       EventType type,
                       int day,
                       string source = "",
                       string referrer = "",
                       long long amount = 0) {

            engine.process({
                "EVT-" + to_string(sequence++),
                move(user),
                type,
                day,
                move(source),
                move(referrer),
                amount
            });
        };

        // Organic acquisition and monetization.
        add("U001", EventType::Visit, 0, "organic");
        add("U001", EventType::Signup, 0, "organic");
        add("U001", EventType::Activation, 1);
        add("U001", EventType::Login, 3);
        add("U001", EventType::Purchase, 4, "", "", 4999);
        add("U001", EventType::ReferralSent, 5);

        // Paid acquisition.
        add("U002", EventType::Visit, 0, "paid");
        add("U002", EventType::Signup, 0, "paid");
        add("U002", EventType::Activation, 2);
        add("U002", EventType::Login, 5);
        add("U002", EventType::Purchase, 6, "", "", 9900);

        // Referred customer.
        add("U003", EventType::Visit, 1, "referral");
        add("U003", EventType::Signup, 1, "referral", "U001");
        add("U003", EventType::Activation, 2);
        add("U003", EventType::Login, 4);

        // Social acquisition.
        add("U004", EventType::Visit, 2, "social");
        add("U004", EventType::Signup, 2, "social");
        add("U004", EventType::Activation, 3);
        add("U004", EventType::Purchase, 5, "", "", 2900);

        // Acquired but not activated.
        add("U005", EventType::Visit, 3, "paid");
        add("U005", EventType::Signup, 3, "paid");

        printReport(engine);

        cout << "\nEXPERIMENT ANALYSIS\n";

        const auto experiment = GrowthEngine::compareExperiment(
            {false, true, false, false, true, false},
            {true, true, false, true, true, false}
        );

        cout << "Control: " << experiment.controlRate << "%\n";
        cout << "Treatment: " << experiment.treatmentRate << "%\n";
        cout << "Absolute lift: " << experiment.absoluteLift << " pp\n";
        cout << "Relative lift: " << experiment.relativeLift << "%\n";

        // Negative test: purchases before activation are rejected.
        bool rejected = false;

        try {
            engine.process({
                "INVALID-001",
                "U005",
                EventType::Purchase,
                5,
                "",
                "",
                1000
            });
        }
        catch (const GrowthException& error) {
            rejected = true;
            cerr << "\nExpected validation failure: "
                 << error.what() << '\n';
        }

        if (!rejected) {
            throw GrowthException(
                "Invalid purchase was unexpectedly accepted."
            );
        }

        cout << "\nProcessed events: " << engine.eventCount() << '\n';
        cout << "Growth analysis completed.\n";

    }
    catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
