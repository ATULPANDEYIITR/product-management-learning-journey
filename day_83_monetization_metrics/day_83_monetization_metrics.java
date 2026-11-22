import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

/**
 * Enterprise Monetization Analytics System
 *
 * Java 17
 *
 * Models subscription billing, financial metrics, acquisition economics,
 * reporting periods, and monetization policy evaluation.
 */
public class MonetizationEnterprise {

    enum BillingInterval {
        MONTHLY(1),
        QUARTERLY(3),
        SEMIANNUAL(6),
        ANNUAL(12);

        private final int months;

        BillingInterval(int months) {
            this.months = months;
        }

        public int months() {
            return months;
        }
    }

    enum SubscriptionStatus {
        ACTIVE,
        CANCELLED,
        PAST_DUE,
        SUSPENDED
    }

    enum FindingSeverity {
        INFO,
        WARNING,
        CRITICAL
    }

    static class BusinessException extends RuntimeException {
        BusinessException(String message) {
            super(message);
        }
    }

    record Customer(
        String id,
        boolean active,
        YearMonth acquiredMonth
    ) {
        Customer {
            if (id == null || id.isBlank()) {
                throw new BusinessException("Customer ID is required.");
            }
            if (acquiredMonth == null) {
                throw new BusinessException("Acquisition month is required.");
            }
        }
    }

    record Subscription(
        String id,
        String customerId,
        BigDecimal price,
        BillingInterval interval,
        SubscriptionStatus status
    ) {
        Subscription {
            if (id == null || id.isBlank() ||
                customerId == null || customerId.isBlank()) {
                throw new BusinessException("Subscription identifiers required.");
            }

            requireNonNegative(price, "Subscription price");

            if (interval == null || status == null) {
                throw new BusinessException("Billing configuration is required.");
            }
        }

        BigDecimal monthlyRevenue() {
            if (status != SubscriptionStatus.ACTIVE) {
                return BigDecimal.ZERO;
            }

            return price.divide(
                BigDecimal.valueOf(interval.months()),
                8,
                RoundingMode.HALF_UP
            );
        }
    }

    record AcquisitionBudget(
        BigDecimal marketingSpend,
        BigDecimal salesSpend,
        int newCustomers
    ) {
        AcquisitionBudget {
            requireNonNegative(marketingSpend, "Marketing spend");
            requireNonNegative(salesSpend, "Sales spend");

            if (newCustomers < 0) {
                throw new BusinessException("Invalid customer count.");
            }
        }

        BigDecimal totalSpend() {
            return marketingSpend.add(salesSpend);
        }
    }

    record CostStructure(
        BigDecimal variableCost,
        BigDecimal fixedCost
    ) {
        CostStructure {
            requireNonNegative(variableCost, "Variable cost");
            requireNonNegative(fixedCost, "Fixed cost");
        }
    }

    record MonetizationPolicy(
        BigDecimal minimumGrossMargin,
        BigDecimal minimumLtvCacRatio,
        BigDecimal maximumPaybackMonths
    ) {
        MonetizationPolicy {
            requireNonNegative(minimumGrossMargin, "Minimum gross margin");
            requireNonNegative(minimumLtvCacRatio, "Minimum LTV/CAC");
            requireNonNegative(maximumPaybackMonths, "Maximum payback");
        }
    }

    record FinancialMetrics(
        YearMonth reportingMonth,
        int totalUsers,
        int payingUsers,
        BigDecimal arpu,
        BigDecimal arppu,
        BigDecimal mrr,
        BigDecimal arr,
        BigDecimal ltv,
        BigDecimal cac,
        BigDecimal grossProfit,
        BigDecimal grossMargin,
        BigDecimal ltvCacRatio,
        BigDecimal paybackMonths
    ) {}

    record PolicyFinding(
        FindingSeverity severity,
        String code,
        String message
    ) {}

    static void requireNonNegative(
        BigDecimal value,
        String field
    ) {
        if (value == null || value.signum() < 0) {
            throw new BusinessException(
                field + " must be non-negative."
            );
        }
    }

    static BigDecimal money(BigDecimal value) {
        return value.setScale(2, RoundingMode.HALF_UP);
    }

    static Optional<BigDecimal> safeDivide(
        BigDecimal numerator,
        BigDecimal denominator
    ) {
        if (denominator == null || denominator.signum() == 0) {
            return Optional.empty();
        }

        return Optional.of(
            numerator.divide(
                denominator,
                8,
                RoundingMode.HALF_UP
            )
        );
    }

    static class SubscriptionRepository {

        private final Map<String, Customer> customers = new HashMap<>();
        private final Map<String, Subscription> subscriptions = new HashMap<>();

        public void registerCustomer(Customer customer) {
            if (customers.putIfAbsent(customer.id(), customer) != null) {
                throw new BusinessException("Duplicate customer.");
            }
        }

        public void registerSubscription(Subscription subscription) {
            if (!customers.containsKey(subscription.customerId())) {
                throw new BusinessException("Unknown subscription customer.");
            }

            if (subscriptions.putIfAbsent(
                subscription.id(),
                subscription
            ) != null) {
                throw new BusinessException("Duplicate subscription.");
            }
        }

        public void changeStatus(
            String subscriptionId,
            SubscriptionStatus newStatus
        ) {
            Subscription existing = subscriptions.get(subscriptionId);

            if (existing == null) {
                throw new BusinessException("Subscription not found.");
            }

            subscriptions.put(
                subscriptionId,
                new Subscription(
                    existing.id(),
                    existing.customerId(),
                    existing.price(),
                    existing.interval(),
                    newStatus
                )
            );
        }

        public List<Customer> customers() {
            return List.copyOf(customers.values());
        }

        public List<Subscription> subscriptions() {
            return List.copyOf(subscriptions.values());
        }
    }

    static class MonetizationService {

        private final SubscriptionRepository repository;

        MonetizationService(SubscriptionRepository repository) {
            this.repository = repository;
        }

        public FinancialMetrics calculate(
            YearMonth reportingMonth,
            AcquisitionBudget acquisition,
            CostStructure costs,
            BigDecimal monthlyChurn
        ) {
            if (reportingMonth == null) {
                throw new BusinessException("Reporting month is required.");
            }

            if (monthlyChurn == null ||
                monthlyChurn.signum() < 0 ||
                monthlyChurn.compareTo(BigDecimal.ONE) > 0) {
                throw new BusinessException("Invalid monthly churn.");
            }

            List<Customer> activeCustomers =
                repository.customers().stream()
                    .filter(Customer::active)
                    .toList();

            Set<String> payingCustomerIds = new HashSet<>();

            BigDecimal mrr = repository.subscriptions().stream()
                .filter(s -> s.status() == SubscriptionStatus.ACTIVE)
                .filter(s -> activeCustomers.stream().anyMatch(
                    c -> c.id().equals(s.customerId())
                ))
                .peek(s -> payingCustomerIds.add(s.customerId()))
                .map(Subscription::monthlyRevenue)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

            int totalUsers = activeCustomers.size();
            int payingUsers = payingCustomerIds.size();

            Optional<BigDecimal> arpu = safeDivide(
                mrr,
                BigDecimal.valueOf(totalUsers)
            );

            Optional<BigDecimal> arppu = safeDivide(
                mrr,
                BigDecimal.valueOf(payingUsers)
            );

            BigDecimal arr = mrr.multiply(BigDecimal.valueOf(12));

            BigDecimal grossProfit = mrr.subtract(costs.variableCost());

            Optional<BigDecimal> margin = safeDivide(
                grossProfit,
                mrr
            );

            Optional<BigDecimal> cac = safeDivide(
                acquisition.totalSpend(),
                BigDecimal.valueOf(acquisition.newCustomers())
            );

            Optional<BigDecimal> ltv = Optional.empty();

            if (arppu.isPresent() &&
                margin.isPresent() &&
                monthlyChurn.signum() > 0) {

                ltv = Optional.of(
                    arppu.get()
                        .multiply(margin.get())
                        .divide(
                            monthlyChurn,
                            8,
                            RoundingMode.HALF_UP
                        )
                );
            }

            Optional<BigDecimal> ratio = Optional.empty();

            if (ltv.isPresent() && cac.isPresent()) {
                ratio = safeDivide(ltv.get(), cac.get());
            }

            Optional<BigDecimal> payback = Optional.empty();

            if (cac.isPresent() &&
                arppu.isPresent() &&
                margin.isPresent()) {

                BigDecimal contribution =
                    arppu.get().multiply(margin.get());

                payback = safeDivide(
                    cac.get(),
                    contribution
                );
            }

            return new FinancialMetrics(
                reportingMonth,
                totalUsers,
                payingUsers,
                arpu.map(MonetizationEnterprise::money).orElse(null),
                arppu.map(MonetizationEnterprise::money).orElse(null),
                money(mrr),
                money(arr),
                ltv.map(MonetizationEnterprise::money).orElse(null),
                cac.map(MonetizationEnterprise::money).orElse(null),
                money(grossProfit),
                margin.map(MonetizationEnterprise::money).orElse(null),
                ratio.map(MonetizationEnterprise::money).orElse(null),
                payback.map(MonetizationEnterprise::money).orElse(null)
            );
        }
    }

    static class GovernanceService {

        private final MonetizationPolicy policy;

        GovernanceService(MonetizationPolicy policy) {
            this.policy = policy;
        }

        public List<PolicyFinding> evaluate(FinancialMetrics metrics) {
            List<PolicyFinding> findings = new ArrayList<>();

            if (metrics.grossMargin() == null) {
                findings.add(new PolicyFinding(
                    FindingSeverity.WARNING,
                    "MARGIN_UNAVAILABLE",
                    "Gross margin cannot be evaluated."
                ));
            } else if (
                metrics.grossMargin().compareTo(
                    policy.minimumGrossMargin()
                ) < 0
            ) {
                findings.add(new PolicyFinding(
                    FindingSeverity.CRITICAL,
                    "MARGIN_BELOW_POLICY",
                    "Gross margin is below the permitted threshold."
                ));
            }

            if (metrics.ltvCacRatio() == null) {
                findings.add(new PolicyFinding(
                    FindingSeverity.WARNING,
                    "LTV_CAC_UNAVAILABLE",
                    "Acquisition economics cannot be evaluated."
                ));
            } else if (
                metrics.ltvCacRatio().compareTo(
                    policy.minimumLtvCacRatio()
                ) < 0
            ) {
                findings.add(new PolicyFinding(
                    FindingSeverity.CRITICAL,
                    "LTV_CAC_BELOW_POLICY",
                    "Customer lifetime value is insufficient relative to CAC."
                ));
            }

            if (metrics.paybackMonths() != null &&
                metrics.paybackMonths().compareTo(
                    policy.maximumPaybackMonths()
                ) > 0) {
                findings.add(new PolicyFinding(
                    FindingSeverity.WARNING,
                    "PAYBACK_TOO_LONG",
                    "Customer acquisition payback exceeds policy."
                ));
            }

            if (findings.isEmpty()) {
                findings.add(new PolicyFinding(
                    FindingSeverity.INFO,
                    "POLICY_COMPLIANT",
                    "All available monetization policy checks passed."
                ));
            }

            return List.copyOf(findings);
        }
    }

    static void printReport(FinancialMetrics m) {
        System.out.println("\nENTERPRISE MONETIZATION REPORT");
        System.out.println("Reporting month: " + m.reportingMonth());
        System.out.println("----------------------------------------");

        System.out.println("Total users: " + m.totalUsers());
        System.out.println("Paying users: " + m.payingUsers());

        System.out.println("ARPU: " + m.arpu());
        System.out.println("ARPPU: " + m.arppu());
        System.out.println("MRR: " + m.mrr());
        System.out.println("ARR: " + m.arr());
        System.out.println("LTV: " + m.ltv());
        System.out.println("CAC: " + m.cac());
        System.out.println("Gross profit: " + m.grossProfit());
        System.out.println("Gross margin: " + m.grossMargin());
        System.out.println("LTV/CAC: " + m.ltvCacRatio());
        System.out.println("Payback months: " + m.paybackMonths());
    }

    public static void main(String[] args) {

        try {
            SubscriptionRepository repository =
                new SubscriptionRepository();

            YearMonth reportingMonth = YearMonth.of(2026, 11);

            repository.registerCustomer(
                new Customer("C001", true, reportingMonth.minusMonths(8))
            );

            repository.registerCustomer(
                new Customer("C002", true, reportingMonth.minusMonths(6))
            );

            repository.registerCustomer(
                new Customer("C003", true, reportingMonth.minusMonths(4))
            );

            repository.registerCustomer(
                new Customer("C004", true, reportingMonth.minusMonths(2))
            );

            repository.registerCustomer(
                new Customer("C005", false, reportingMonth.minusMonths(1))
            );

            repository.registerSubscription(new Subscription(
                "S001", "C001", new BigDecimal("100"),
                BillingInterval.MONTHLY, SubscriptionStatus.ACTIVE
            ));

            repository.registerSubscription(new Subscription(
                "S002", "C002", new BigDecimal("450"),
                BillingInterval.QUARTERLY, SubscriptionStatus.ACTIVE
            ));

            repository.registerSubscription(new Subscription(
                "S003", "C003", new BigDecimal("1200"),
                BillingInterval.ANNUAL, SubscriptionStatus.ACTIVE
            ));

            repository.registerSubscription(new Subscription(
                "S004", "C004", new BigDecimal("200"),
                BillingInterval.MONTHLY, SubscriptionStatus.CANCELLED
            ));

            repository.registerSubscription(new Subscription(
                "S005", "C005", new BigDecimal("300"),
                BillingInterval.MONTHLY, SubscriptionStatus.ACTIVE
            ));

            AcquisitionBudget acquisition = new AcquisitionBudget(
                new BigDecimal("3000"),
                new BigDecimal("2000"),
                5
            );

            CostStructure costs = new CostStructure(
                new BigDecimal("180"),
                new BigDecimal("1200")
            );

            MonetizationService service =
                new MonetizationService(repository);

            FinancialMetrics metrics = service.calculate(
                reportingMonth,
                acquisition,
                costs,
                new BigDecimal("0.05")
            );

            printReport(metrics);

            MonetizationPolicy policy = new MonetizationPolicy(
                new BigDecimal("0.50"),
                new BigDecimal("3.00"),
                new BigDecimal("12.00")
            );

            GovernanceService governance =
                new GovernanceService(policy);

            System.out.println("\nPOLICY EVALUATION");

            governance.evaluate(metrics).forEach(finding ->
                System.out.println(
                    finding.severity() + " | " +
                    finding.code() + " | " +
                    finding.message()
                )
            );

            // Zero-revenue and zero-user cases remain explicitly unavailable.
            FinancialMetrics zeroCase = new MonetizationService(
                new SubscriptionRepository()
            ).calculate(
                reportingMonth,
                acquisition,
                costs,
                new BigDecimal("0.05")
            );

            if (zeroCase.arpu() != null ||
                zeroCase.arppu() != null) {
                throw new BusinessException(
                    "Zero-population validation failed."
                );
            }

            System.out.println("\nAll enterprise validation checks passed.");

        } catch (BusinessException exception) {
            System.err.println(
                "Business validation failed: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
