#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

enum class BillingCycle {
    Monthly = 1,
    Quarterly = 3,
    SemiAnnual = 6,
    Annual = 12
};

enum class SubscriptionState {
    Active,
    Cancelled,
    Suspended
};

struct Customer {
    string id;
    bool active = true;
};

struct Subscription {
    string id;
    string customerId;
    double price;
    BillingCycle cycle;
    SubscriptionState state;
};

struct Acquisition {
    double marketingSpend;
    double salesSpend;
    int newCustomers;
};

struct OperatingCosts {
    double variableCost;
    double fixedCost;
};

struct Metrics {
    int totalUsers = 0;
    int payingUsers = 0;

    double mrr = 0;
    double arr = 0;
    double grossProfit = 0;

    optional<double> arpu;
    optional<double> arppu;
    optional<double> ltv;
    optional<double> cac;
    optional<double> grossMargin;
    optional<double> ltvCacRatio;
    optional<double> paybackMonths;
};

class MonetizationException : public runtime_error {
public:
    explicit MonetizationException(const string& message)
        : runtime_error(message) {}
};

class MonetizationEngine {
private:
    unordered_map<string, Customer> customers;
    unordered_map<string, Subscription> subscriptions;

    Acquisition acquisition;
    OperatingCosts costs;
    optional<double> monthlyChurn;

    static bool validMoney(double amount) {
        return isfinite(amount) && amount >= 0;
    }

    static optional<double> divide(double a, double b) {
        if (b <= 0 || !isfinite(b)) {
            return nullopt;
        }
        return a / b;
    }

    static double monthlyPrice(const Subscription& s) {
        return s.price / static_cast<int>(s.cycle);
    }

public:
    MonetizationEngine(
        Acquisition acquisitionData,
        OperatingCosts costData,
        optional<double> churn
    ) : acquisition(acquisitionData),
        costs(costData),
        monthlyChurn(churn) {

        if (!validMoney(acquisition.marketingSpend) ||
            !validMoney(acquisition.salesSpend) ||
            !validMoney(costs.variableCost) ||
            !validMoney(costs.fixedCost)) {
            throw MonetizationException("Invalid financial input.");
        }

        if (acquisition.newCustomers < 0) {
            throw MonetizationException("Invalid acquisition count.");
        }

        if (monthlyChurn &&
            (!isfinite(*monthlyChurn) ||
             *monthlyChurn < 0 ||
             *monthlyChurn > 1)) {
            throw MonetizationException("Invalid churn rate.");
        }
    }

    void addCustomer(const Customer& customer) {
        if (customer.id.empty()) {
            throw MonetizationException("Customer ID is required.");
        }

        if (customers.count(customer.id)) {
            throw MonetizationException("Duplicate customer.");
        }

        customers.emplace(customer.id, customer);
    }

    void addSubscription(const Subscription& subscription) {
        if (subscription.id.empty() ||
            subscription.customerId.empty()) {
            throw MonetizationException("Subscription IDs are required.");
        }

        if (!customers.count(subscription.customerId)) {
            throw MonetizationException("Unknown customer.");
        }

        if (subscriptions.count(subscription.id)) {
            throw MonetizationException("Duplicate subscription.");
        }

        if (!validMoney(subscription.price)) {
            throw MonetizationException("Invalid subscription price.");
        }

        subscriptions.emplace(subscription.id, subscription);
    }

    void updateState(
        const string& subscriptionId,
        SubscriptionState newState
    ) {
        auto it = subscriptions.find(subscriptionId);

        if (it == subscriptions.end()) {
            throw MonetizationException("Subscription not found.");
        }

        it->second.state = newState;
    }

    Metrics calculate() const {
        Metrics result;

        unordered_set<string> payingCustomerIds;

        for (const auto& [id, customer] : customers) {
            if (customer.active) {
                result.totalUsers++;
            }
        }

        // Aggregate subscriptions once instead of repeatedly scanning them.
        for (const auto& [id, subscription] : subscriptions) {
            auto customerIt = customers.find(subscription.customerId);

            if (customerIt == customers.end() ||
                !customerIt->second.active ||
                subscription.state != SubscriptionState::Active) {
                continue;
            }

            result.mrr += monthlyPrice(subscription);
            payingCustomerIds.insert(subscription.customerId);
        }

        result.payingUsers = static_cast<int>(
            payingCustomerIds.size()
        );

        result.arr = result.mrr * 12;

        result.arpu = divide(
            result.mrr,
            result.totalUsers
        );

        result.arppu = divide(
            result.mrr,
            result.payingUsers
        );

        result.grossProfit =
            result.mrr - costs.variableCost;

        result.grossMargin = divide(
            result.grossProfit,
            result.mrr
        );

        const double acquisitionCost =
            acquisition.marketingSpend +
            acquisition.salesSpend;

        result.cac = divide(
            acquisitionCost,
            acquisition.newCustomers
        );

        if (result.arppu &&
            result.grossMargin &&
            monthlyChurn &&
            *monthlyChurn > 0) {

            result.ltv =
                (*result.arppu * *result.grossMargin) /
                *monthlyChurn;
        }

        if (result.ltv && result.cac) {
            result.ltvCacRatio = divide(
                *result.ltv,
                *result.cac
            );
        }

        if (result.cac &&
            result.arppu &&
            result.grossMargin) {

            double contribution =
                *result.arppu * *result.grossMargin;

            result.paybackMonths = divide(
                *result.cac,
                contribution
            );
        }

        return result;
    }

    static void printMetric(
        const string& label,
        const optional<double>& value
    ) {
        cout << left << setw(28) << label;

        if (value) {
            cout << fixed << setprecision(2) << *value;
        } else {
            cout << "N/A";
        }

        cout << '\n';
    }

    static void printReport(const Metrics& m) {
        cout << "\nMONETIZATION GOVERNANCE REPORT\n";
        cout << string(48, '=') << '\n';

        cout << "Total users                 " << m.totalUsers << '\n';
        cout << "Paying users                " << m.payingUsers << '\n';

        printMetric("ARPU", m.arpu);
        printMetric("ARPPU", m.arppu);
        printMetric("MRR", m.mrr);
        printMetric("ARR", m.arr);
        printMetric("LTV", m.ltv);
        printMetric("CAC", m.cac);
        printMetric("Gross profit", m.grossProfit);
        printMetric("Gross margin", m.grossMargin);
        printMetric("LTV/CAC", m.ltvCacRatio);
        printMetric("CAC payback (months)", m.paybackMonths);

        cout << "\nACQUISITION ASSESSMENT\n";

        if (!m.ltvCacRatio) {
            cout << "Insufficient data.\n";
        } else if (*m.ltvCacRatio < 1) {
            cout << "Acquisition economics are negative.\n";
        } else if (*m.ltvCacRatio < 3) {
            cout << "Below conventional 3:1 reference.\n";
        } else {
            cout << "Meets conventional 3:1 reference.\n";
        }
    }
};

int main() {
    try {
        Acquisition acquisition{
            3000.00,
            2000.00,
            5
        };

        OperatingCosts costs{
            180.00,
            1200.00
        };

        MonetizationEngine engine(
            acquisition,
            costs,
            0.05
        );

        engine.addCustomer({"C001", true});
        engine.addCustomer({"C002", true});
        engine.addCustomer({"C003", true});
        engine.addCustomer({"C004", true});
        engine.addCustomer({"C005", true});
        engine.addCustomer({"C006", false});

        engine.addSubscription({
            "S001", "C001", 100.00,
            BillingCycle::Monthly,
            SubscriptionState::Active
        });

        engine.addSubscription({
            "S002", "C002", 150.00,
            BillingCycle::Monthly,
            SubscriptionState::Active
        });

        engine.addSubscription({
            "S003", "C003", 600.00,
            BillingCycle::Quarterly,
            SubscriptionState::Active
        });

        engine.addSubscription({
            "S004", "C004", 1200.00,
            BillingCycle::Annual,
            SubscriptionState::Active
        });

        engine.addSubscription({
            "S005", "C005", 250.00,
            BillingCycle::Monthly,
            SubscriptionState::Cancelled
        });

        // Cancelled subscriptions contribute zero MRR.
        Metrics metrics = engine.calculate();

        MonetizationEngine::printReport(metrics);

        // Boundary validation.
        if (metrics.totalUsers != 5 ||
            metrics.payingUsers != 4) {
            throw MonetizationException(
                "Unexpected user aggregation."
            );
        }

        // An empty user population produces unavailable ARPU.
        MonetizationEngine emptyEngine(
            acquisition,
            costs,
            0.05
        );

        Metrics emptyMetrics = emptyEngine.calculate();

        if (emptyMetrics.arpu.has_value()) {
            throw MonetizationException(
                "Zero-user ARPU validation failed."
            );
        }

        cout << "\nAll validation checks passed.\n";
    }
    catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
