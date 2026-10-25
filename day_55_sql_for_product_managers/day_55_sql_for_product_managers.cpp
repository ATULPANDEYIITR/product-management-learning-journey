#include <algorithm>
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
    Activation,
    Purchase,
    Churn
};

string eventName(EventType type) {
    switch (type) {
        case EventType::View: return "view";
        case EventType::Activation: return "activation";
        case EventType::Purchase: return "purchase";
        case EventType::Churn: return "churn";
    }
    throw logic_error("Unknown event type");
}

struct Product {
    int id;
    string name;
    string category;
};

struct User {
    int id;
    string country;
    string channel;
};

struct Event {
    int id;
    int userId;
    int productId;
    EventType type;
    string date;
    long long revenueCents;
};

struct ProductReport {
    string name;
    string category;
    size_t purchases = 0;
    long long revenueCents = 0;
};

class ProductAnalytics {
private:
    vector<Product> products;
    vector<User> users;
    vector<Event> events;

    unordered_map<int, size_t> productIndex;
    unordered_map<int, size_t> userIndex;

    static bool inRange(const string& date,
                        const string& start,
                        const string& end) {
        // ISO YYYY-MM-DD dates sort lexicographically in chronological order.
        return date >= start && date <= end;
    }

    static void validateRange(const string& start, const string& end) {
        auto validDate = [](const string& value) {
            if (value.size() != 10 || value[4] != '-' || value[7] != '-') {
                return false;
            }
            for (size_t i = 0; i < value.size(); ++i) {
                if (i == 4 || i == 7) continue;
                if (value[i] < '0' || value[i] > '9') return false;
            }
            const int month = stoi(value.substr(5, 2));
            const int day = stoi(value.substr(8, 2));
            return month >= 1 && month <= 12 && day >= 1 && day <= 31;
        };

        if (!validDate(start) || !validDate(end)) {
            throw invalid_argument("Dates must use YYYY-MM-DD format.");
        }
        if (start > end) {
            throw invalid_argument("Start date must not follow end date.");
        }
    }

    void validateData() {
        productIndex.clear();
        userIndex.clear();

        for (size_t i = 0; i < products.size(); ++i) {
            if (products[i].id <= 0 ||
                !productIndex.emplace(products[i].id, i).second) {
                throw invalid_argument("Product IDs must be unique and positive.");
            }
        }

        for (size_t i = 0; i < users.size(); ++i) {
            if (users[i].id <= 0 ||
                !userIndex.emplace(users[i].id, i).second) {
                throw invalid_argument("User IDs must be unique and positive.");
            }
        }

        unordered_set<int> eventIds;
        for (const auto& event : events) {
            if (event.id <= 0 || !eventIds.insert(event.id).second) {
                throw invalid_argument("Event IDs must be unique and positive.");
            }
            if (!userIndex.count(event.userId) ||
                !productIndex.count(event.productId)) {
                throw invalid_argument("Event references an unknown user or product.");
            }
            if (event.revenueCents < 0) {
                throw invalid_argument("Revenue cannot be negative.");
            }
            if (event.type != EventType::Purchase && event.revenueCents != 0) {
                throw invalid_argument("Only purchase events may record revenue.");
            }
        }
    }

public:
    ProductAnalytics(vector<Product> productData,
                     vector<User> userData,
                     vector<Event> eventData)
        : products(move(productData)),
          users(move(userData)),
          events(move(eventData)) {
        validateData();
    }

    vector<ProductReport> revenueByProduct(
        const string& start, const string& end) const {
        validateRange(start, end);

        vector<ProductReport> reports;
        unordered_map<int, size_t> reportIndex;

        // Initialize every product to model LEFT JOIN behavior.
        for (const auto& product : products) {
            reportIndex[product.id] = reports.size();
            reports.push_back({product.name, product.category, 0, 0});
        }

        for (const auto& event : events) {
            if (event.type != EventType::Purchase ||
                !inRange(event.date, start, end)) {
                continue;
            }

            auto found = reportIndex.find(event.productId);
            if (found == reportIndex.end()) {
                throw logic_error("Validated product index is inconsistent.");
            }
            auto& report = reports[found->second];
            ++report.purchases;
            report.revenueCents += event.revenueCents;
        }

        sort(reports.begin(), reports.end(),
             [](const ProductReport& a, const ProductReport& b) {
                 if (a.revenueCents != b.revenueCents) {
                     return a.revenueCents > b.revenueCents;
                 }
                 return a.name < b.name;
             });
        return reports;
    }

    void printRevenueReport(const string& start, const string& end) const {
        const auto reports = revenueByProduct(start, end);
        cout << "\nRevenue by product: " << start << " to " << end << "\n";
        cout << left << setw(22) << "Product"
             << setw(18) << "Category"
             << right << setw(10) << "Purchases"
             << setw(14) << "Revenue\n";
        cout << string(64, '-') << '\n';

        for (const auto& report : reports) {
            cout << left << setw(22) << report.name
                 << setw(18) << report.category
                 << right << setw(10) << report.purchases
                 << setw(10) << fixed << setprecision(2)
                 << (report.revenueCents / 100.0) << '\n';
        }
    }

    void printChannelReport() const {
        struct Metrics {
            set<int> users;
            set<int> payers;
            long long revenueCents = 0;
        };

        map<string, Metrics> metrics;
        for (const auto& user : users) {
            metrics[user.channel].users.insert(user.id);
        }

        for (const auto& event : events) {
            if (event.type != EventType::Purchase) continue;
            const auto userIt = userIndex.find(event.userId);
            if (userIt == userIndex.end()) {
                throw logic_error("Validated user index is inconsistent.");
            }
            auto& metric = metrics[users[userIt->second].channel];
            metric.payers.insert(event.userId);
            metric.revenueCents += event.revenueCents;
        }

        cout << "\nAcquisition performance\n";
        cout << left << setw(16) << "Channel"
             << right << setw(12) << "Users"
             << setw(12) << "Payers"
             << setw(14) << "Revenue"
             << setw(14) << "Conversion\n";

        for (const auto& [channel, metric] : metrics) {
            const double conversion = metric.users.empty()
                ? 0.0
                : 100.0 * metric.payers.size() / metric.users.size();

            cout << left << setw(16) << channel
                 << right << setw(12) << metric.users.size()
                 << setw(12) << metric.payers.size()
                 << setw(10) << fixed << setprecision(2)
                 << metric.revenueCents / 100.0
                 << setw(12) << conversion << "%\n";
        }
    }

    long long totalRevenue(const string& start, const string& end) const {
        validateRange(start, end);
        long long total = 0;
        for (const auto& event : events) {
            if (event.type == EventType::Purchase &&
                inRange(event.date, start, end)) {
                total += event.revenueCents;
            }
        }
        return total;
    }
};

int main() {
    try {
        vector<Product> products = {
            {1, "Analytics Pro", "Analytics"},
            {2, "Team Workspace", "Collaboration"},
            {3, "Mobile Insights", "Analytics"}
        };

        vector<User> users = {
            {101, "India", "Organic"},
            {102, "USA", "Paid Search"},
            {103, "India", "Referral"},
            {104, "UK", "Organic"},
            {105, "USA", "Paid Search"},
            {106, "India", "Referral"}
        };

        vector<Event> events = {
            {1, 101, 1, EventType::View, "2026-03-01", 0},
            {2, 101, 1, EventType::Activation, "2026-03-02", 0},
            {3, 101, 1, EventType::Purchase, "2026-03-05", 9900},
            {4, 102, 1, EventType::View, "2026-03-02", 0},
            {5, 102, 1, EventType::Purchase, "2026-03-07", 14900},
            {6, 103, 2, EventType::View, "2026-03-03", 0},
            {7, 103, 2, EventType::Activation, "2026-03-04", 0},
            {8, 104, 2, EventType::View, "2026-03-05", 0},
            {9, 105, 3, EventType::View, "2026-03-06", 0},
            {10, 105, 3, EventType::Activation, "2026-03-07", 0},
            {11, 105, 3, EventType::Purchase, "2026-03-08", 4900},
            {12, 106, 1, EventType::View, "2026-03-09", 0},
            {13, 106, 1, EventType::Churn, "2026-03-20", 0},
            {14, 101, 1, EventType::Purchase, "2026-04-02", 9900}
        };

        ProductAnalytics analytics(products, users, events);
        analytics.printRevenueReport("2026-03-01", "2026-03-31");
        analytics.printChannelReport();

        const long long marchRevenue =
            analytics.totalRevenue("2026-03-01", "2026-03-31");
        if (marchRevenue != 29700) {
            throw runtime_error("March revenue assertion failed.");
        }

        cout << "\nValidated March revenue: $"
             << fixed << setprecision(2) << marchRevenue / 100.0 << '\n';

        try {
            analytics.totalRevenue("2026-04-01", "2026-03-01");
            throw runtime_error("Invalid date range was accepted.");
        } catch (const invalid_argument&) {
            cout << "Invalid date range correctly rejected.\n";
        }
    } catch (const exception& error) {
        cerr << "Analytics error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
