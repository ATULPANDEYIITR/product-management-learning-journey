import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * Enterprise SaaS Revenue Management System.
 *
 * Java 17
 *
 * Includes:
 * - Subscription revenue movements
 * - Revenue retention policies
 * - Churn and expansion calculations
 * - Customer acquisition economics
 * - CAC payback
 * - Cohort retention
 * - Immutable domain records
 * - Enterprise metric validation
 * - Revenue reconciliation
 */

public class SaaSMetricsEnterprise {

    private static final BigDecimal ZERO = BigDecimal.ZERO;
    private static final BigDecimal HUNDRED =
            new BigDecimal("100");

    enum SubscriptionStatus {
        ACTIVE,
        CHURNED
    }

    enum MovementType {
        NEW_BUSINESS,
        EXPANSION,
        CONTRACTION,
        CHURN,
        UNCHANGED
    }

    enum MetricStatus {
        CALCULATED,
        INSUFFICIENT_DATA
    }

    static class DomainException extends RuntimeException {
        public DomainException(String message) {
            super(message);
        }
    }

    static class InsufficientDataException
            extends DomainException {
        public InsufficientDataException(String message) {
            super(message);
        }
    }

    record Customer(
            String customerId,
            String customerName,
            String segment,
            YearMonth acquisitionMonth
    ) {
        Customer {
            if (customerId == null || customerId.isBlank()) {
                throw new DomainException(
                        "Customer ID is required"
                );
            }

            Objects.requireNonNull(customerName);
            Objects.requireNonNull(segment);
            Objects.requireNonNull(acquisitionMonth);
        }
    }

    record RevenueMovement(
            String customerId,
            YearMonth period,
            BigDecimal startingMRR,
            BigDecimal endingMRR
    ) {
        RevenueMovement {
            Objects.requireNonNull(customerId);
            Objects.requireNonNull(period);

            validateMoney(startingMRR, "Starting MRR");
            validateMoney(endingMRR, "Ending MRR");
        }

        MovementType classify() {
            int comparison =
                    endingMRR.compareTo(startingMRR);

            if (startingMRR.compareTo(ZERO) == 0 &&
                    endingMRR.compareTo(ZERO) > 0) {
                return MovementType.NEW_BUSINESS;
            }

            if (startingMRR.compareTo(ZERO) > 0 &&
                    endingMRR.compareTo(ZERO) == 0) {
                return MovementType.CHURN;
            }

            if (comparison > 0) {
                return MovementType.EXPANSION;
            }

            if (comparison < 0) {
                return MovementType.CONTRACTION;
            }

            return MovementType.UNCHANGED;
        }
    }

    record AcquisitionRecord(
            YearMonth period,
            BigDecimal salesMarketingCost,
            int newCustomers,
            BigDecimal grossMargin
    ) {
        AcquisitionRecord {
            Objects.requireNonNull(period);
            validateMoney(
                    salesMarketingCost,
                    "Acquisition cost"
            );

            if (newCustomers < 0) {
                throw new DomainException(
                        "New customer count cannot be negative"
                );
            }

            if (grossMargin.compareTo(ZERO) < 0 ||
                    grossMargin.compareTo(HUNDRED) > 0) {
                throw new DomainException(
                        "Gross margin must be between 0 and 100"
                );
            }
        }
    }

    record RevenueSnapshot(
            YearMonth period,
            BigDecimal startingMRR,
            BigDecimal endingMRR,
            BigDecimal newMRR,
            BigDecimal expansionMRR,
            BigDecimal contractionMRR,
            BigDecimal churnedMRR,
            int startingCustomers,
            int endingCustomers,
            int newCustomers,
            int churnedCustomers
    ) {}

    record MetricResult(
            MetricStatus status,
            BigDecimal value,
            String explanation
    ) {
        static MetricResult calculated(BigDecimal value) {
            return new MetricResult(
                    MetricStatus.CALCULATED,
                    value,
                    "Metric successfully calculated"
            );
        }

        static MetricResult unavailable(String reason) {
            return new MetricResult(
                    MetricStatus.INSUFFICIENT_DATA,
                    null,
                    reason
            );
        }
    }

    static void validateMoney(
            BigDecimal value,
            String field
    ) {
        if (value == null || value.compareTo(ZERO) < 0) {
            throw new DomainException(
                    field + " must be non-negative"
            );
        }
    }

    static BigDecimal divide(
            BigDecimal numerator,
            BigDecimal denominator
    ) {
        return numerator.divide(
                denominator,
                8,
                RoundingMode.HALF_UP
        );
    }

    static BigDecimal percentage(
            BigDecimal numerator,
            BigDecimal denominator
    ) {
        return divide(numerator, denominator)
                .multiply(HUNDRED)
                .setScale(2, RoundingMode.HALF_UP);
    }

    interface RetentionPolicy {
        MetricResult calculate(RevenueSnapshot snapshot);
    }

    static class NetRetentionPolicy
            implements RetentionPolicy {

        @Override
        public MetricResult calculate(
                RevenueSnapshot snapshot
        ) {
            if (snapshot.startingMRR().compareTo(ZERO) == 0) {
                return MetricResult.unavailable(
                        "No opening MRR baseline"
                );
            }

            BigDecimal retained =
                    snapshot.startingMRR()
                            .subtract(snapshot.churnedMRR())
                            .subtract(snapshot.contractionMRR())
                            .add(snapshot.expansionMRR());

            return MetricResult.calculated(
                    percentage(
                            retained,
                            snapshot.startingMRR()
                    )
            );
        }
    }

    static class GrossRetentionPolicy
            implements RetentionPolicy {

        @Override
        public MetricResult calculate(
                RevenueSnapshot snapshot
        ) {
            if (snapshot.startingMRR().compareTo(ZERO) == 0) {
                return MetricResult.unavailable(
                        "No opening MRR baseline"
                );
            }

            BigDecimal retained =
                    snapshot.startingMRR()
                            .subtract(snapshot.churnedMRR())
                            .subtract(snapshot.contractionMRR());

            return MetricResult.calculated(
                    percentage(
                            retained,
                            snapshot.startingMRR()
                    )
            );
        }
    }

    static class RevenueLedger {

        private final Map<YearMonth,
                List<RevenueMovement>> movements =
                new HashMap<>();

        public void record(RevenueMovement movement) {
            List<RevenueMovement> periodMovements =
                    movements.computeIfAbsent(
                            movement.period(),
                            key -> new ArrayList<>()
                    );

            boolean duplicate = periodMovements.stream()
                    .anyMatch(existing ->
                            existing.customerId().equals(
                                    movement.customerId()
                            )
                    );

            if (duplicate) {
                throw new DomainException(
                        "Duplicate customer movement"
                );
            }

            periodMovements.add(movement);
        }

        public RevenueSnapshot snapshot(YearMonth period) {
            List<RevenueMovement> records =
                    movements.get(period);

            if (records == null || records.isEmpty()) {
                throw new InsufficientDataException(
                        "No movements for " + period
                );
            }

            BigDecimal opening = ZERO;
            BigDecimal closing = ZERO;
            BigDecimal newMRR = ZERO;
            BigDecimal expansion = ZERO;
            BigDecimal contraction = ZERO;
            BigDecimal churn = ZERO;

            int startingCustomers = 0;
            int endingCustomers = 0;
            int newCustomers = 0;
            int churnedCustomers = 0;

            Set<String> processed = new HashSet<>();

            for (RevenueMovement movement : records) {
                if (!processed.add(movement.customerId())) {
                    throw new DomainException(
                            "Duplicate customer in snapshot"
                    );
                }

                BigDecimal start = movement.startingMRR();
                BigDecimal end = movement.endingMRR();

                opening = opening.add(start);
                closing = closing.add(end);

                if (start.compareTo(ZERO) > 0) {
                    startingCustomers++;

                    if (end.compareTo(ZERO) == 0) {
                        churn = churn.add(start);
                        churnedCustomers++;
                    } else if (end.compareTo(start) > 0) {
                        expansion = expansion.add(
                                end.subtract(start)
                        );
                    } else if (end.compareTo(start) < 0) {
                        contraction = contraction.add(
                                start.subtract(end)
                        );
                    }
                } else if (end.compareTo(ZERO) > 0) {
                    newMRR = newMRR.add(end);
                    newCustomers++;
                }

                if (end.compareTo(ZERO) > 0) {
                    endingCustomers++;
                }
            }

            BigDecimal expected = opening
                    .add(newMRR)
                    .add(expansion)
                    .subtract(contraction)
                    .subtract(churn);

            if (expected.compareTo(closing) != 0) {
                throw new DomainException(
                        "Revenue reconciliation failed"
                );
            }

            return new RevenueSnapshot(
                    period,
                    opening,
                    closing,
                    newMRR,
                    expansion,
                    contraction,
                    churn,
                    startingCustomers,
                    endingCustomers,
                    newCustomers,
                    churnedCustomers
            );
        }
    }

    static class AcquisitionService {

        public BigDecimal calculateCAC(
                AcquisitionRecord record
        ) {
            if (record.newCustomers() == 0) {
                throw new InsufficientDataException(
                        "No new customers available for CAC"
                );
            }

            return divide(
                    record.salesMarketingCost(),
                    BigDecimal.valueOf(record.newCustomers())
            ).setScale(2, RoundingMode.HALF_UP);
        }

        public BigDecimal calculatePaybackMonths(
                AcquisitionRecord record,
                BigDecimal averageMonthlyRevenue
        ) {
            validateMoney(
                    averageMonthlyRevenue,
                    "Average MRR"
            );

            if (averageMonthlyRevenue.compareTo(ZERO) == 0) {
                throw new DomainException(
                        "Average MRR must be positive"
                );
            }

            if (record.grossMargin().compareTo(ZERO) == 0) {
                throw new InsufficientDataException(
                        "Zero gross margin prevents payback"
                );
            }

            BigDecimal cac = calculateCAC(record);

            BigDecimal monthlyGrossProfit =
                    averageMonthlyRevenue
                            .multiply(record.grossMargin())
                            .divide(
                                    HUNDRED,
                                    8,
                                    RoundingMode.HALF_UP
                            );

            return divide(
                    cac,
                    monthlyGrossProfit
            ).setScale(2, RoundingMode.HALF_UP);
        }
    }

    static class RevenueAnalyticsService {

        private final RevenueLedger ledger;
        private final RetentionPolicy netPolicy =
                new NetRetentionPolicy();
        private final RetentionPolicy grossPolicy =
                new GrossRetentionPolicy();

        RevenueAnalyticsService(RevenueLedger ledger) {
            this.ledger = ledger;
        }

        Map<String, Object> evaluate(YearMonth period) {
            RevenueSnapshot snapshot =
                    ledger.snapshot(period);

            Map<String, Object> report = new HashMap<>();

            report.put("period", period.toString());
            report.put("startingMRR", snapshot.startingMRR());
            report.put("endingMRR", snapshot.endingMRR());
            report.put("newMRR", snapshot.newMRR());
            report.put("expansionMRR", snapshot.expansionMRR());
            report.put("contractionMRR", snapshot.contractionMRR());
            report.put("churnedMRR", snapshot.churnedMRR());

            report.put(
                    "NRR",
                    netPolicy.calculate(snapshot)
            );

            report.put(
                    "GRR",
                    grossPolicy.calculate(snapshot)
            );

            report.put(
                    "logoChurn",
                    snapshot.startingCustomers() == 0
                            ? MetricResult.unavailable(
                                    "No opening customer baseline"
                            )
                            : MetricResult.calculated(
                                    percentage(
                                            BigDecimal.valueOf(
                                                    snapshot.churnedCustomers()
                                            ),
                                            BigDecimal.valueOf(
                                                    snapshot.startingCustomers()
                                            )
                                    )
                            )
            );

            report.put(
                    "revenueChurn",
                    snapshot.startingMRR().compareTo(ZERO) == 0
                            ? MetricResult.unavailable(
                                    "No opening MRR baseline"
                            )
                            : MetricResult.calculated(
                                    percentage(
                                            snapshot.churnedMRR()
                                                    .add(snapshot.contractionMRR()),
                                            snapshot.startingMRR()
                                    )
                            )
            );

            return Collections.unmodifiableMap(report);
        }
    }

    static class CohortService {

        public Map<String, Map<String, BigDecimal>> analyze(
                Map<String, Map<String, BigDecimal>> cohorts
        ) {
            Map<String, Map<String, BigDecimal>> result =
                    new HashMap<>();

            cohorts.forEach((cohort, periods) -> {
                BigDecimal baseline = periods.get("M0");

                if (baseline == null ||
                        baseline.compareTo(ZERO) <= 0) {
                    throw new DomainException(
                            "Invalid cohort baseline: " + cohort
                    );
                }

                Map<String, BigDecimal> retention =
                        new HashMap<>();

                periods.forEach((period, revenue) -> {
                    validateMoney(revenue, "Cohort revenue");

                    retention.put(
                            period,
                            percentage(revenue, baseline)
                    );
                });

                result.put(
                        cohort,
                        Collections.unmodifiableMap(retention)
                );
            });

            return Collections.unmodifiableMap(result);
        }
    }

    private static void printReport(
            Map<String, Object> report
    ) {
        System.out.println("\nENTERPRISE SAAS METRICS");
        System.out.println("========================================");

        report.forEach((key, value) ->
                System.out.printf("%-22s %s%n", key, value)
        );
    }

    public static void main(String[] args) {
        try {
            RevenueLedger ledger = new RevenueLedger();

            YearMonth period = YearMonth.of(2026, 10);

            ledger.record(new RevenueMovement(
                    "C001", period,
                    new BigDecimal("1000"),
                    new BigDecimal("1200")
            ));

            ledger.record(new RevenueMovement(
                    "C002", period,
                    new BigDecimal("2000"),
                    new BigDecimal("1500")
            ));

            ledger.record(new RevenueMovement(
                    "C003", period,
                    new BigDecimal("1500"),
                    ZERO
            ));

            ledger.record(new RevenueMovement(
                    "C004", period,
                    new BigDecimal("500"),
                    new BigDecimal("500")
            ));

            ledger.record(new RevenueMovement(
                    "C005", period,
                    ZERO,
                    new BigDecimal("1000")
            ));

            ledger.record(new RevenueMovement(
                    "C006", period,
                    ZERO,
                    new BigDecimal("800")
            ));

            RevenueAnalyticsService analytics =
                    new RevenueAnalyticsService(ledger);

            printReport(analytics.evaluate(period));

            AcquisitionRecord acquisition =
                    new AcquisitionRecord(
                            period,
                            new BigDecimal("12000"),
                            2,
                            new BigDecimal("80")
                    );

            AcquisitionService acquisitionService =
                    new AcquisitionService();

            System.out.println("\nACQUISITION ECONOMICS");
            System.out.println("========================================");

            System.out.println(
                    "CAC: " +
                    acquisitionService.calculateCAC(acquisition)
            );

            System.out.println(
                    "Payback Months: " +
                    acquisitionService.calculatePaybackMonths(
                            acquisition,
                            new BigDecimal("900")
                    )
            );

            Map<String, Map<String, BigDecimal>> cohorts =
                    Map.of(
                            "2026-Q3",
                            Map.of(
                                    "M0", new BigDecimal("10000"),
                                    "M1", new BigDecimal("9800"),
                                    "M2", new BigDecimal("10500"),
                                    "M3", new BigDecimal("11000")
                            ),
                            "2026-Q4",
                            Map.of(
                                    "M0", new BigDecimal("15000"),
                                    "M1", new BigDecimal("14200")
                            )
                    );

            System.out.println("\nCOHORT RETENTION");
            new CohortService().analyze(cohorts)
                    .forEach((name, values) ->
                            System.out.println(name + ": " + values)
                    );

            // Explicit failure test.
            try {
                new AcquisitionService().calculateCAC(
                        new AcquisitionRecord(
                                period,
                                new BigDecimal("1000"),
                                0,
                                new BigDecimal("80")
                        )
                );
            } catch (InsufficientDataException expected) {
                System.out.println(
                        "\nExpected validation: " +
                        expected.getMessage()
                );
            }

            System.out.println("\nProcessing completed.");

        } catch (DomainException exception) {
            System.err.println(
                    "Business validation failed: " +
                    exception.getMessage()
            );
            System.exitCode = 1;
        }
    }
}
