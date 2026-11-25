#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
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

enum class EventType {
    View,
    AddToCart,
    Checkout,
    Purchase,
    Refund
};

enum class CustomerSegment {
    NoPurchase,
    Champions,
    Loyal,
    Recent,
    AtRisk,
    Dormant,
    Regular
};

string toString(EventType type) {
    switch (type) {
        case EventType::View: return "View";
        case EventType::AddToCart: return "Add To Cart";
        case EventType::Checkout: return "Checkout";
        case EventType::Purchase: return "Purchase";
        case EventType::Refund: return "Refund";
    }

    throw logic_error("Unknown event type");
}

string toString(CustomerSegment segment) {
    switch (segment) {
        case CustomerSegment::NoPurchase: return "No Purchase";
        case CustomerSegment::Champions: return "Champions";
        case CustomerSegment::Loyal: return "Loyal Customers";
        case CustomerSegment::Recent: return "Recent Customers";
        case CustomerSegment::AtRisk: return "At Risk";
        case CustomerSegment::Dormant: return "Dormant";
        case CustomerSegment::Regular: return "Regular Customers";
    }

    throw logic_error("Unknown segment");
}

struct Product {
    int id;
    string name;
    string category;
    double price;
    double cost;
};

struct Customer {
    int id;
    int registrationDay;
    string channel;
    string region;
};

struct Event {
    int id;
    int customerId;
    int productId;
    EventType type;
    int day;
    int quantity;
    double amount;
    string sessionId;
};

struct ProductMetrics {
    int views = 0;
    int cartEvents = 0;
    int purchases = 0;
    int units = 0;
    double revenue = 0;
    unordered_set<int> buyers;
};

struct CustomerMetrics {
    int recency = 0;
    int frequency = 0;
    double monetary = 0;
    CustomerSegment segment = CustomerSegment::NoPurchase;
};

class AnalyticsEngine {
private:
    unordered_map<int, Product> products;
    unordered_map<int, Customer> customers;
    unordered_map<int, vector<Event>> customerEvents;
    vector<Event> events;
    unordered_set<int> eventIds;

    static constexpr int FUNNEL_SIZE = 4;

    static int stageIndex(EventType type) {
        switch (type) {
            case EventType::View: return 0;
            case EventType::AddToCart: return 1;
            case EventType::Checkout: return 2;
            case EventType::Purchase: return 3;
            default: return -1;
        }
    }

    void validateEvent(const Event& event) const {
        if (event.id <= 0 || event.customerId <= 0 ||
            event.productId <= 0) {
            throw invalid_argument("Identifiers must be positive");
        }

        if (!customers.count(event.customerId)) {
            throw invalid_argument("Unknown customer");
        }

        if (!products.count(event.productId)) {
            throw invalid_argument("Unknown product");
        }

        if (event.quantity <= 0 || event.amount < 0 ||
            !isfinite(event.amount)) {
            throw invalid_argument("Invalid quantity or amount");
        }

        if (event.day < customers.at(event.customerId).registrationDay) {
            throw invalid_argument("Event predates customer registration");
        }

        if (event.type != EventType::Purchase && event.amount != 0) {
            throw invalid_argument(
                "Only purchase events may have transaction amounts"
            );
        }
    }

public:
    AnalyticsEngine(
        const vector<Product>& productList,
        const vector<Customer>& customerList
    ) {
        for (const auto& product : productList) {
            if (product.id <= 0 || product.name.empty() ||
                product.price < 0 || product.cost < 0) {
                throw invalid_argument("Invalid product");
            }

            if (!products.emplace(product.id, product).second) {
                throw invalid_argument("Duplicate product ID");
            }
        }

        for (const auto& customer : customerList) {
            if (customer.id <= 0 || customer.channel.empty()) {
                throw invalid_argument("Invalid customer");
            }

            if (!customers.emplace(customer.id, customer).second) {
                throw invalid_argument("Duplicate customer ID");
            }
        }
    }

    void ingest(const Event& event) {
        validateEvent(event);

        if (eventIds.count(event.id)) {
            throw invalid_argument("Duplicate event ID");
        }

        // Indexes provide average O(1) customer lookup.
        eventIds.insert(event.id);
        events.push_back(event);
        customerEvents[event.customerId].push_back(event);
    }

    size_t eventCount() const {
        return events.size();
    }

    vector<pair<string, ProductMetrics>> productAnalysis(
        int startDay,
        int endDay
    ) const {
        if (startDay > endDay) {
            throw invalid_argument("Invalid reporting period");
        }

        unordered_map<int, ProductMetrics> metrics;

        for (const auto& event : events) {
            if (event.day < startDay || event.day > endDay) {
                continue;
            }

            auto& row = metrics[event.productId];

            switch (event.type) {
                case EventType::View:
                    row.views++;
                    break;

                case EventType::AddToCart:
                    row.cartEvents++;
                    break;

                case EventType::Purchase:
                    row.purchases++;
                    row.units += event.quantity;
                    row.revenue += event.amount;
                    row.buyers.insert(event.customerId);
                    break;

                case EventType::Refund:
                    row.revenue -= event.amount;
                    break;

                default:
                    break;
            }
        }

        vector<pair<string, ProductMetrics>> output;

        for (const auto& [id, row] : metrics) {
            output.push_back({products.at(id).name, row});
        }

        sort(output.begin(), output.end(),
            [](const auto& a, const auto& b) {
                return a.second.revenue > b.second.revenue;
            }
        );

        return output;
    }

    array<int, FUNNEL_SIZE> conversionFunnel(
        int startDay,
        int endDay
    ) const {
        if (startDay > endDay) {
            throw invalid_argument("Invalid reporting period");
        }

        array<unordered_set<int>, FUNNEL_SIZE> stageUsers;

        for (const auto& event : events) {
            if (event.day < startDay || event.day > endDay) {
                continue;
            }

            int index = stageIndex(event.type);

            if (index >= 0) {
                stageUsers[index].insert(event.customerId);
            }
        }

        array<int, FUNNEL_SIZE> counts{};

        for (int i = 0; i < FUNNEL_SIZE; i++) {
            counts[i] = static_cast<int>(stageUsers[i].size());
        }

        return counts;
    }

    map<string, int> orderedSessionFunnel(
        int startDay,
        int endDay
    ) const {
        map<string, vector<Event>> sessions;

        for (const auto& event : events) {
            if (event.day >= startDay && event.day <= endDay &&
                !event.sessionId.empty()) {
                sessions[event.sessionId].push_back(event);
            }
        }

        map<string, int> counts;

        for (const auto& session : sessions) {
            auto sessionEvents = session.second;

            sort(
                sessionEvents.begin(),
                sessionEvents.end(),
                [](const Event& a, const Event& b) {
                    return a.day < b.day ||
                        (a.day == b.day && a.id < b.id);
                }
            );

            int nextStage = 0;

            for (const auto& event : sessionEvents) {
                if (stageIndex(event.type) == nextStage) {
                    nextStage++;
                }
            }

            for (int i = 0; i < nextStage; i++) {
                counts[toString(static_cast<EventType>(i))]++;
            }
        }

        return counts;
    }

    vector<map<string, double>> retention(
        int cohortStart,
        int cohortEnd,
        int analysisEnd
    ) const {
        if (cohortStart > cohortEnd || cohortEnd > analysisEnd) {
            throw invalid_argument("Invalid cohort period");
        }

        map<int, set<int>> cohorts;
        map<int, set<int>> activity;

        for (const auto& [id, customer] : customers) {
            if (customer.registrationDay >= cohortStart &&
                customer.registrationDay <= cohortEnd) {
                int month = customer.registrationDay / 30;
                cohorts[month].insert(id);
            }
        }

        for (const auto& event : events) {
            if (event.day >= cohortStart && event.day <= analysisEnd) {
                activity[event.day / 30].insert(event.customerId);
            }
        }

        vector<map<string, double>> result;

        for (const auto& [cohortMonth, members] : cohorts) {
            for (int month = cohortMonth;
                 month <= analysisEnd / 30;
                 month++) {

                int active = 0;

                for (int customerId : members) {
                    if (activity[month].count(customerId)) {
                        active++;
                    }
                }

                double rate = members.empty() ? 0 :
                    100.0 * active / members.size();

                result.push_back({
                    {"cohort_month", static_cast<double>(cohortMonth)},
                    {"month_number", static_cast<double>(
                        month - cohortMonth
                    )},
                    {"cohort_size", static_cast<double>(members.size())},
                    {"active_customers", static_cast<double>(active)},
                    {"retention_rate", rate}
                });
            }
        }

        return result;
    }

    vector<pair<int, CustomerMetrics>> segmentCustomers(
        int referenceDay
    ) const {
        vector<pair<int, CustomerMetrics>> result;

        for (const auto& [id, customer] : customers) {
            vector<Event> purchases;
            double refunds = 0;

            for (const auto& event : customerEvents.at(id)) {
                if (event.day > referenceDay) {
                    continue;
                }

                if (event.type == EventType::Purchase) {
                    purchases.push_back(event);
                }

                if (event.type == EventType::Refund) {
                    refunds += event.amount;
                }
            }

            CustomerMetrics metrics;

            if (purchases.empty()) {
                result.push_back({id, metrics});
                continue;
            }

            int latest = 0;

            for (const auto& purchase : purchases) {
                latest = max(latest, purchase.day);
                metrics.monetary += purchase.amount;
            }

            metrics.recency = referenceDay - latest;
            metrics.frequency = static_cast<int>(purchases.size());
            metrics.monetary -= refunds;

            if (metrics.monetary < 0) {
                throw logic_error("Negative customer monetary value");
            }

            if (metrics.recency <= 30 &&
                metrics.frequency >= 3 &&
                metrics.monetary >= 5000) {
                metrics.segment = CustomerSegment::Champions;
            } else if (metrics.recency <= 60 &&
                       metrics.frequency >= 2) {
                metrics.segment = CustomerSegment::Loyal;
            } else if (metrics.recency <= 30 &&
                       metrics.frequency == 1) {
                metrics.segment = CustomerSegment::Recent;
            } else if (metrics.recency > 90 &&
                       metrics.frequency >= 2) {
                metrics.segment = CustomerSegment::AtRisk;
            } else if (metrics.recency > 180) {
                metrics.segment = CustomerSegment::Dormant;
            } else {
                metrics.segment = CustomerSegment::Regular;
            }

            result.push_back({id, metrics});
        }

        return result;
    }

    map<string, pair<int, double>> channelAnalysis(
        int startDay,
        int endDay
    ) const {
        struct ChannelData {
            set<int> visitors;
            set<int> buyers;
            double revenue = 0;
        };

        map<string, ChannelData> channels;

        for (const auto& event : events) {
            if (event.day < startDay || event.day > endDay) {
                continue;
            }

            const auto& customer = customers.at(event.customerId);
            auto& row = channels[customer.channel];

            if (event.type == EventType::View) {
                row.visitors.insert(customer.id);
            } else if (event.type == EventType::Purchase) {
                row.buyers.insert(customer.id);
                row.revenue += event.amount;
            } else if (event.type == EventType::Refund) {
                row.revenue -= event.amount;
            }
        }

        map<string, pair<int, double>> result;

        for (const auto& [channel, row] : channels) {
            result[channel] = {
                static_cast<int>(row.visitors.size()),
                row.revenue
            };
        }

        return result;
    }
};

vector<Product> sampleProducts() {
    return {
        {101, "Laptop Pro", "Electronics", 1200, 850},
        {102, "Wireless Mouse", "Accessories", 35, 12},
        {103, "Mechanical Keyboard", "Accessories", 95, 48},
        {104, "Smart Watch", "Wearables", 250, 140},
        {105, "USB-C Hub", "Accessories", 55, 22}
    };
}

vector<Customer> sampleCustomers() {
    return {
        {1, 5, "Organic", "North"},
        {2, 12, "Paid Search", "South"},
        {3, 33, "Social", "East"},
        {4, 45, "Organic", "West"},
        {5, 60, "Referral", "North"},
        {6, 70, "Paid Search", "South"},
        {7, 92, "Social", "East"},
        {8, 105, "Referral", "West"}
    };
}

vector<Event> sampleEvents() {
    using T = EventType;

    return {
        {1,1,101,T::View,90,1,0,"S1"},
        {2,1,101,T::AddToCart,91,1,0,"S1"},
        {3,1,101,T::Checkout,92,1,0,"S1"},
        {4,1,101,T::Purchase,93,1,1200,"S1"},
        {5,1,102,T::Purchase,130,1,35,"S2"},
        {6,1,103,T::Purchase,150,1,95,"S3"},
        {7,2,102,T::View,91,1,0,"S4"},
        {8,2,102,T::AddToCart,92,1,0,"S4"},
        {9,2,102,T::Purchase,94,1,35,"S4"},
        {10,2,102,T::Refund,100,1,0,"S5"},
        {11,3,104,T::View,95,1,0,"S6"},
        {12,3,104,T::Purchase,97,1,250,"S6"},
        {13,4,103,T::View,102,1,0,"S7"},
        {14,4,103,T::AddToCart,103,1,0,"S7"},
        {15,4,103,T::Checkout,104,1,0,"S7"},
        {16,4,103,T::Purchase,105,1,95,"S7"},
        {17,5,105,T::View,110,1,0,"S8"},
        {18,5,105,T::Purchase,112,1,55,"S8"},
        {19,6,101,T::View,115,1,0,"S9"},
        {20,6,101,T::AddToCart,116,1,0,"S9"},
        {21,7,104,T::View,118,1,0,"S10"},
        {22,8,102,T::View,119,1,0,"S11"},
        {23,8,102,T::Purchase,120,1,35,"S11"}
    };
}

int main() {
    try {
        AnalyticsEngine engine(sampleProducts(), sampleCustomers());

        for (const auto& event : sampleEvents()) {
            engine.ingest(event);
        }

        cout << fixed << setprecision(2);

        cout << "PRODUCT ANALYTICS\n";

        for (const auto& [name, metrics] :
             engine.productAnalysis(90, 180)) {

            cout << name
                 << " | Views: " << metrics.views
                 << " | Cart: " << metrics.cartEvents
                 << " | Purchases: " << metrics.purchases
                 << " | Buyers: " << metrics.buyers.size()
                 << " | Revenue: " << metrics.revenue
                 << '\n';
        }

        cout << "\nCONVERSION FUNNEL\n";

        const auto funnel = engine.conversionFunnel(90, 180);

        for (int i = 0; i < FUNNEL_SIZE; i++) {
            cout << i << " | Users: " << funnel[i] << '\n';
        }

        cout << "\nSESSION FUNNEL\n";

        for (const auto& [stage, count] :
             engine.orderedSessionFunnel(90, 180)) {
            cout << stage << ": " << count << '\n';
        }

        cout << "\nCUSTOMER SEGMENTATION\n";

        for (const auto& [id, metrics] :
             engine.segmentCustomers(180)) {
            cout << "Customer " << id
                 << " | Segment: " << toString(metrics.segment)
                 << " | Frequency: " << metrics.frequency
                 << " | Monetary: " << metrics.monetary
                 << '\n';
        }

        cout << "\nRETENTION ANALYSIS\n";

        for (const auto& row : engine.retention(0, 119, 180)) {
            cout << "Cohort: " << row.at("cohort_month")
                 << " | Month: " << row.at("month_number")
                 << " | Retention: " << row.at("retention_rate")
                 << "%\n";
        }

        cout << "\nCHANNEL ANALYSIS\n";

        for (const auto& [channel, metrics] :
             engine.channelAnalysis(90, 180)) {
            cout << channel
                 << " | Visitors: " << metrics.first
                 << " | Revenue: " << metrics.second
                 << '\n';
        }

        cout << "\nVALIDATION TESTS\n";

        bool duplicateRejected = false;

        try {
            engine.ingest(sampleEvents().front());
        } catch (const invalid_argument&) {
            duplicateRejected = true;
        }

        if (!duplicateRejected) {
            throw logic_error("Duplicate event validation failed");
        }

        cout << "Duplicate event rejection: PASS\n";
        cout << "Total accepted events: " << engine.eventCount() << '\n';

    } catch (const exception& error) {
        cerr << "Analytics failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
