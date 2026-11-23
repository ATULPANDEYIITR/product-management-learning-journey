#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * SaaS Revenue Governance and Metrics Engine
 *
 * C++17
 *
 * Models:
 * - Subscription revenue movements
 * - New, expansion, contraction and churned MRR
 * - NRR and GRR
 * - Logo churn and revenue churn
 * - CAC and CAC payback
 * - Branch-independent metric evaluation
 * - Revenue reconciliation
 * - Merge-independent policy validation
 */

enum class MovementType {
    NewBusiness,
    Expansion,
    Contraction,
    Churn,
    Unchanged
};

enum class SubscriptionStatus {
    Active,
    Churned
};

struct CustomerMovement {
    string customerId;
    double startingMRR;
    double endingMRR;
    MovementType type;
};

struct RevenueMetrics {
    string period;

    double startingMRR = 0;
    double endingMRR = 0;
    double newMRR = 0;
    double expansionMRR = 0;
    double contractionMRR = 0;
    double churnedMRR = 0;

    int startingCustomers = 0;
    int endingCustomers = 0;
    int newCustomers = 0;
    int churnedCustomers = 0;
};

struct AcquisitionData {
    double salesMarketingCost;
    int newCustomers;
    double grossMargin;
};

class ValidationException : public runtime_error {
public:
    explicit ValidationException(const string& message)
        : runtime_error(message) {}
};

class MetricCalculator {
private:
    static constexpr double EPSILON = 1e-8;

    static void validateMoney(double value, const string& field) {
        if (!isfinite(value) || value < 0) {
            throw ValidationException(
                field + " must be finite and non-negative"
            );
        }
    }

public:
    static MovementType classify(double start, double end) {
        validateMoney(start, "Starting MRR");
        validateMoney(end, "Ending MRR");

        if (start == 0 && end > 0)
            return MovementType::NewBusiness;

        if (start > 0 && end == 0)
            return MovementType::Churn;

        if (end > start)
            return MovementType::Expansion;

        if (end < start)
            return MovementType::Contraction;

        return MovementType::Unchanged;
    }

    static RevenueMetrics calculate(
        const string& period,
        const vector<CustomerMovement>& movements
    ) {
        if (movements.empty()) {
            throw ValidationException(
                "At least one movement is required"
            );
        }

        RevenueMetrics metrics;
        metrics.period = period;

        unordered_set<string> processed;

        for (const auto& movement : movements) {
            if (movement.customerId.empty()) {
                throw ValidationException(
                    "Customer ID cannot be empty"
                );
            }

            if (!processed.insert(movement.customerId).second) {
                throw ValidationException(
                    "Duplicate customer movement: " +
                    movement.customerId
                );
            }

            validateMoney(movement.startingMRR, "Starting MRR");
            validateMoney(movement.endingMRR, "Ending MRR");

            const auto actualType = classify(
                movement.startingMRR,
                movement.endingMRR
            );

            if (actualType != movement.type) {
                throw ValidationException(
                    "Movement classification mismatch"
                );
            }

            const double start = movement.startingMRR;
            const double end = movement.endingMRR;

            metrics.startingMRR += start;
            metrics.endingMRR += end;

            if (start > 0) {
                metrics.startingCustomers++;

                if (end == 0) {
                    metrics.churnedMRR += start;
                    metrics.churnedCustomers++;
                }
                else if (end > start) {
                    metrics.expansionMRR += end - start;
                }
                else if (end < start) {
                    metrics.contractionMRR += start - end;
                }
            }
            else if (end > 0) {
                metrics.newMRR += end;
                metrics.newCustomers++;
            }

            if (end > 0) {
                metrics.endingCustomers++;
            }
        }

        const double expected =
            metrics.startingMRR +
            metrics.newMRR +
            metrics.expansionMRR -
            metrics.contractionMRR -
            metrics.churnedMRR;

        if (abs(expected - metrics.endingMRR) > EPSILON) {
            throw ValidationException(
                "MRR reconciliation failed"
            );
        }

        return metrics;
    }

    static optional<double> nrr(const RevenueMetrics& m) {
        if (m.startingMRR == 0) {
            return nullopt;
        }

        return (
            m.startingMRR
            - m.churnedMRR
            - m.contractionMRR
            + m.expansionMRR
        ) / m.startingMRR * 100.0;
    }

    static optional<double> grr(const RevenueMetrics& m) {
        if (m.startingMRR == 0) {
            return nullopt;
        }

        return (
            m.startingMRR
            - m.churnedMRR
            - m.contractionMRR
        ) / m.startingMRR * 100.0;
    }

    static optional<double> logoChurn(const RevenueMetrics& m) {
        if (m.startingCustomers == 0) {
            return nullopt;
        }

        return static_cast<double>(m.churnedCustomers)
            / m.startingCustomers * 100.0;
    }

    static optional<double> revenueChurn(const RevenueMetrics& m) {
        if (m.startingMRR == 0) {
            return nullopt;
        }

        return (
            m.churnedMRR + m.contractionMRR
        ) / m.startingMRR * 100.0;
    }

    static optional<double> expansionRate(const RevenueMetrics& m) {
        if (m.startingMRR == 0) {
            return nullopt;
        }

        return m.expansionMRR / m.startingMRR * 100.0;
    }

    static optional<double> mrrGrowth(const RevenueMetrics& m) {
        if (m.startingMRR == 0) {
            return nullopt;
        }

        return (
            m.endingMRR - m.startingMRR
        ) / m.startingMRR * 100.0;
    }

    static double cac(const AcquisitionData& data) {
        validateMoney(data.salesMarketingCost, "Acquisition cost");

        if (data.newCustomers <= 0) {
            throw ValidationException(
                "New customer count must be positive"
            );
        }

        return data.salesMarketingCost / data.newCustomers;
    }

    static double paybackMonths(
        const AcquisitionData& data,
        double averageMRR
    ) {
        validateMoney(averageMRR, "Average MRR");

        if (data.grossMargin <= 0 || data.grossMargin > 100) {
            throw ValidationException(
                "Gross margin must be between 0 and 100"
            );
        }

        if (averageMRR == 0) {
            throw ValidationException(
                "Average MRR must be positive"
            );
        }

        const double monthlyGrossProfit =
            averageMRR * data.grossMargin / 100.0;

        return cac(data) / monthlyGrossProfit;
    }
};

class RepositoryReport {
public:
    static void display(
        const RevenueMetrics& metrics
    ) {
        auto printOptional = [](const string& name,
                                const optional<double>& value) {
            cout << left << setw(28) << name;

            if (value) {
                cout << fixed << setprecision(2)
                     << *value << "%\n";
            }
            else {
                cout << "N/A\n";
            }
        };

        cout << "\nSAAS METRICS: " << metrics.period << "\n";
        cout << string(48, '=') << "\n";

        cout << left << setw(28) << "Starting MRR"
             << metrics.startingMRR << "\n";

        cout << left << setw(28) << "Ending MRR"
             << metrics.endingMRR << "\n";

        cout << left << setw(28) << "New MRR"
             << metrics.newMRR << "\n";

        cout << left << setw(28) << "Expansion MRR"
             << metrics.expansionMRR << "\n";

        cout << left << setw(28) << "Contraction MRR"
             << metrics.contractionMRR << "\n";

        cout << left << setw(28) << "Churned MRR"
             << metrics.churnedMRR << "\n";

        printOptional(
            "Net Revenue Retention",
            MetricCalculator::nrr(metrics)
        );

        printOptional(
            "Gross Revenue Retention",
            MetricCalculator::grr(metrics)
        );

        printOptional(
            "Logo Churn",
            MetricCalculator::logoChurn(metrics)
        );

        printOptional(
            "Revenue Churn",
            MetricCalculator::revenueChurn(metrics)
        );

        printOptional(
            "Expansion Rate",
            MetricCalculator::expansionRate(metrics)
        );

        printOptional(
            "MRR Growth",
            MetricCalculator::mrrGrowth(metrics)
        );
    }
};

class CohortAnalysis {
public:
    static map<string, map<string, double>> calculate(
        const map<string, map<string, double>>& cohorts
    ) {
        map<string, map<string, double>> result;

        for (const auto& [cohort, periods] : cohorts) {
            auto baselineIterator = periods.find("M0");

            if (baselineIterator == periods.end() ||
                baselineIterator->second <= 0) {
                throw ValidationException(
                    "Cohort requires a positive M0 baseline"
                );
            }

            const double baseline = baselineIterator->second;

            for (const auto& [period, revenue] : periods) {
                if (!isfinite(revenue) || revenue < 0) {
                    throw ValidationException(
                        "Invalid cohort revenue"
                    );
                }

                result[cohort][period] =
                    revenue / baseline * 100.0;
            }
        }

        return result;
    }
};

int main() {
    try {
        vector<CustomerMovement> movements;

        auto add = [&](const string& id, double start, double end) {
            movements.push_back({
                id,
                start,
                end,
                MetricCalculator::classify(start, end)
            });
        };

        add("C001", 1000, 1200);
        add("C002", 2000, 1500);
        add("C003", 1500, 0);
        add("C004", 500, 500);
        add("C005", 0, 1000);
        add("C006", 0, 800);

        const RevenueMetrics metrics =
            MetricCalculator::calculate(
                "2026-10",
                movements
            );

        RepositoryReport::display(metrics);

        AcquisitionData acquisition{
            12000,
            2,
            80
        };

        cout << "\nACQUISITION ECONOMICS\n";
        cout << string(48, '=') << "\n";

        cout << "CAC: "
             << MetricCalculator::cac(acquisition)
             << "\n";

        cout << "CAC Payback Months: "
             << MetricCalculator::paybackMonths(
                    acquisition,
                    900
                )
             << "\n";

        map<string, map<string, double>> cohorts = {
            {
                "2026-Q3",
                {
                    {"M0", 10000},
                    {"M1", 9800},
                    {"M2", 10500},
                    {"M3", 11000}
                }
            },
            {
                "2026-Q4",
                {
                    {"M0", 15000},
                    {"M1", 14200}
                }
            }
        };

        cout << "\nCOHORT RETENTION\n";
        cout << string(48, '=') << "\n";

        const auto cohortResults =
            CohortAnalysis::calculate(cohorts);

        for (const auto& [cohort, periods] : cohortResults) {
            cout << cohort << "\n";

            for (const auto& [period, percentage] : periods) {
                cout << "  " << period << ": "
                     << fixed << setprecision(2)
                     << percentage << "%\n";
            }
        }

        // Validate edge cases.
        try {
            AcquisitionData invalid{1000, 0, 80};
            MetricCalculator::cac(invalid);
        }
        catch (const ValidationException& error) {
            cout << "\nExpected validation error: "
                 << error.what() << "\n";
        }

        cout << "\nAll calculations completed successfully.\n";
    }
    catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
