import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * AARRR Framework: Enterprise Product Growth Management System
 *
 * Java 17
 * No third-party dependencies.
 *
 * Domain architecture:
 * Event -> Customer Lifecycle -> Growth Metrics -> Policy Evaluation
 *
 * Includes:
 * - Acquisition attribution
 * - Activation qualification
 * - Retention cohorts
 * - Revenue accounting
 * - Referral attribution
 * - Growth policies
 * - Event validation
 * - Idempotent event processing
 * - Experiment comparison
 * - Enterprise reporting
 */

public class AarrrEnterprise {

    enum GrowthStage {
        ACQUISITION,
        ACTIVATION,
        RETENTION,
        REVENUE,
        REFERRAL
    }

    enum EventType {
        VISIT,
        SIGNUP,
        ACTIVATION,
        LOGIN,
        PURCHASE,
        SUBSCRIPTION,
        REFERRAL_SENT,
        CANCELLATION
    }

    enum CustomerStatus {
        REGISTERED,
        ACTIVATED,
        PAYING,
        CANCELLED
    }

    enum PolicyDecision {
        ALLOW,
        DENY
    }

    record GrowthEvent(
        String eventId,
        String userId,
        EventType type,
        LocalDate eventDate,
        String source,
        String referrer,
        long amountCents
    ) {
        GrowthEvent {
            Objects.requireNonNull(eventId);
            Objects.requireNonNull(userId);
            Objects.requireNonNull(type);
            Objects.requireNonNull(eventDate);

            if (eventId.isBlank() || eventId.length() > 100) {
                throw new DomainException("Invalid event ID.");
            }

            if (userId.isBlank() || userId.length() > 100) {
                throw new DomainException("Invalid user ID.");
            }

            if (amountCents < 0 || amountCents > 10_000_000_000L) {
                throw new DomainException("Invalid monetary amount.");
            }
        }
    }

    record GrowthPolicy(
        int activationWindowDays,
        boolean activationRequiredForPurchase,
        boolean referralRequiresActivation,
        long maximumTransactionCents
    ) {
        GrowthPolicy {
            if (activationWindowDays < 0 ||
                maximumTransactionCents <= 0) {
                throw new DomainException("Invalid growth policy.");
            }
        }

        PolicyDecision evaluatePurchase(Customer customer,
                                        GrowthEvent event) {
            if (activationRequiredForPurchase &&
                !customer.isActivated()) {
                return PolicyDecision.DENY;
            }

            if (event.amountCents() <= 0 ||
                event.amountCents() > maximumTransactionCents) {
                return PolicyDecision.DENY;
            }

            return PolicyDecision.ALLOW;
        }

        PolicyDecision evaluateReferral(Customer customer) {
            if (referralRequiresActivation &&
                !customer.isActivated()) {
                return PolicyDecision.DENY;
            }

            return PolicyDecision.ALLOW;
        }
    }

    record StageMetrics(
        long visitors,
        long signups,
        long activated,
        long retained,
        long paying,
        long referred
    ) {
        static double rate(long numerator, long denominator) {
            return denominator == 0
                ? 0.0
                : 100.0 * numerator / denominator;
        }

        Map<String, Double> conversionRates() {
            Map<String, Double> result = new LinkedHashMap<>();

            result.put(
                "visitor_to_signup",
                rate(signups, visitors)
            );

            result.put(
                "signup_to_activation",
                rate(activated, signups)
            );

            result.put(
                "activation_to_retention",
                rate(retained, activated)
            );

            result.put(
                "activation_to_revenue",
                rate(paying, activated)
            );

            result.put(
                "activation_to_referral",
                rate(referred, activated)
            );

            return Collections.unmodifiableMap(result);
        }
    }

    record CohortMetric(
        LocalDate cohortDate,
        int cohortSize,
        int retainedUsers,
        double retentionRate
    ) {}

    record ExperimentResult(
        double controlRate,
        double treatmentRate,
        double absoluteLift,
        Double relativeLift
    ) {}

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    static class Customer {
        private final String userId;
        private final String acquisitionSource;
        private final LocalDate signupDate;
        private final String referredBy;

        private LocalDate activationDate;
        private LocalDate lastActivity;
        private long revenueCents;
        private int transactions;
        private int referralsSent;
        private boolean cancelled;

        private final Set<LocalDate> activeDates = new HashSet<>();

        Customer(String userId, String source,
                 LocalDate signupDate, String referredBy) {
            this.userId = userId;
            this.acquisitionSource = source;
            this.signupDate = signupDate;
            this.referredBy = referredBy;
        }

        String getUserId() {
            return userId;
        }

        String getAcquisitionSource() {
            return acquisitionSource;
        }

        LocalDate getSignupDate() {
            return signupDate;
        }

        String getReferredBy() {
            return referredBy;
        }

        Set<LocalDate> getActiveDates() {
            return Collections.unmodifiableSet(activeDates);
        }

        boolean isActivated() {
            return activationDate != null;
        }

        boolean isPaying() {
            return revenueCents > 0;
        }

        CustomerStatus status() {
            if (cancelled) return CustomerStatus.CANCELLED;
            if (isPaying()) return CustomerStatus.PAYING;
            if (isActivated()) return CustomerStatus.ACTIVATED;
            return CustomerStatus.REGISTERED;
        }

        void activate(LocalDate date) {
            activationDate = date;
        }

        void recordActivity(LocalDate date) {
            activeDates.add(date);
            lastActivity = date;
        }

        void recordPurchase(long amountCents) {
            revenueCents = Math.addExact(revenueCents, amountCents);
            transactions++;
        }

        void recordReferral() {
            referralsSent++;
        }

        void cancel() {
            cancelled = true;
        }
    }

    interface GrowthMetric {
        String name();
        double calculate(List<Customer> customers);
    }

    static class ActivationMetric implements GrowthMetric {
        @Override
        public String name() {
            return "Activation Rate";
        }

        @Override
        public double calculate(List<Customer> customers) {
            if (customers.isEmpty()) return 0;

            long activated = customers.stream()
                .filter(Customer::isActivated)
                .count();

            return 100.0 * activated / customers.size();
        }
    }

    static class RevenueMetric implements GrowthMetric {
        @Override
        public String name() {
            return "Average Revenue Per User";
        }

        @Override
        public double calculate(List<Customer> customers) {
            if (customers.isEmpty()) return 0;

            long revenue = customers.stream()
                .mapToLong(customer -> customer.revenueCents)
                .sum();

            return revenue / 100.0 / customers.size();
        }
    }

    static class GrowthService {
        private final GrowthPolicy policy;

        private final Map<String, Customer> customers =
            new ConcurrentHashMap<>();

        private final Map<String, GrowthEvent> processedEvents =
            new ConcurrentHashMap<>();

        private final Map<String, Set<String>> acquisitionVisitors =
            new HashMap<>();

        private final List<GrowthEvent> eventHistory =
            new ArrayList<>();

        private final AtomicInteger sequence = new AtomicInteger();

        GrowthService(GrowthPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        /**
         * Synchronized state transition prevents concurrent requests
         * from registering or processing the same event twice.
         */
        public synchronized void process(GrowthEvent event) {
            Objects.requireNonNull(event);

            if (processedEvents.containsKey(event.eventId())) {
                throw new DomainException("Duplicate event.");
            }

            Customer customer = customers.get(event.userId());

            switch (event.type()) {
                case VISIT -> {
                    if (event.source() == null ||
                        event.source().isBlank()) {
                        throw new DomainException(
                            "Acquisition source required."
                        );
                    }

                    acquisitionVisitors
                        .computeIfAbsent(
                            event.source(),
                            ignored -> new HashSet<>()
                        )
                        .add(event.userId());
                }

                case SIGNUP -> {
                    if (customer != null) {
                        throw new DomainException("Duplicate signup.");
                    }

                    if (event.source() == null ||
                        event.source().isBlank()) {
                        throw new DomainException(
                            "Acquisition source required."
                        );
                    }

                    if (event.referrer() != null &&
                        (!customers.containsKey(event.referrer()) ||
                         event.referrer().equals(event.userId()))) {
                        throw new DomainException(
                            "Invalid referral attribution."
                        );
                    }

                    customers.put(
                        event.userId(),
                        new Customer(
                            event.userId(),
                            event.source(),
                            event.eventDate(),
                            event.referrer()
                        )
                    );
                }

                default -> {
                    if (customer == null) {
                        throw new DomainException(
                            "Customer must register first."
                        );
                    }

                    switch (event.type()) {
                        case ACTIVATION -> {
                            if (customer.isActivated()) {
                                throw new DomainException(
                                    "Already activated."
                                );
                            }

                            long elapsed = java.time.temporal.ChronoUnit
                                .DAYS.between(
                                    customer.getSignupDate(),
                                    event.eventDate()
                                );

                            if (elapsed < 0 ||
                                elapsed > policy.activationWindowDays()) {
                                throw new DomainException(
                                    "Activation outside allowed window."
                                );
                            }

                            customer.activate(event.eventDate());
                        }

                        case LOGIN -> {
                            if (event.eventDate().isBefore(
                                    customer.getSignupDate())) {
                                throw new DomainException(
                                    "Activity predates signup."
                                );
                            }

                            customer.recordActivity(event.eventDate());
                        }

                        case PURCHASE, SUBSCRIPTION -> {
                            if (policy.evaluatePurchase(
                                    customer, event) != PolicyDecision.ALLOW) {
                                throw new DomainException(
                                    "Purchase violates growth policy."
                                );
                            }

                            customer.recordPurchase(event.amountCents());
                        }

                        case REFERRAL_SENT -> {
                            if (policy.evaluateReferral(customer) !=
                                PolicyDecision.ALLOW) {
                                throw new DomainException(
                                    "Referral violates growth policy."
                                );
                            }

                            customer.recordReferral();
                        }

                        case CANCELLATION -> customer.cancel();

                        default -> throw new DomainException(
                            "Unsupported customer transition."
                        );
                    }
                }
            }

            processedEvents.put(event.eventId(), event);
            eventHistory.add(event);
        }

        public synchronized GrowthEvent createAndProcess(
            String userId,
            EventType type,
            LocalDate date,
            String source,
            String referrer,
            long amountCents
        ) {
            GrowthEvent event = new GrowthEvent(
                "EVT-" + sequence.incrementAndGet(),
                userId,
                type,
                date,
                source,
                referrer,
                amountCents
            );

            process(event);
            return event;
        }

        public List<Customer> customers() {
            return List.copyOf(customers.values());
        }

        public StageMetrics metrics() {
            List<Customer> all = customers();

            long activated = all.stream()
                .filter(Customer::isActivated)
                .count();

            long retained = all.stream()
                .filter(customer -> !customer.activeDates.isEmpty())
                .count();

            long paying = all.stream()
                .filter(Customer::isPaying)
                .count();

            long referred = all.stream()
                .filter(customer -> customer.getReferredBy() != null)
                .count();

            long visitors = acquisitionVisitors.values().stream()
                .flatMap(Set::stream)
                .distinct()
                .count();

            return new StageMetrics(
                visitors,
                all.size(),
                activated,
                retained,
                paying,
                referred
            );
        }

        public Map<String, Map<String, Double>> acquisitionReport() {
            Map<String, Map<String, Double>> report =
                new TreeMap<>();

            acquisitionVisitors.forEach((source, visitors) -> {
                long signups = customers.values().stream()
                    .filter(customer ->
                        customer.getAcquisitionSource().equals(source))
                    .count();

                Map<String, Double> metrics = new LinkedHashMap<>();

                metrics.put("visitors", (double) visitors.size());
                metrics.put("signups", (double) signups);
                metrics.put(
                    "conversionRate",
                    StageMetrics.rate(signups, visitors.size())
                );

                report.put(source, Collections.unmodifiableMap(metrics));
            });

            return Collections.unmodifiableMap(report);
        }

        public Map<LocalDate, CohortMetric> retentionReport(
            int periodDays
        ) {
            if (periodDays < 1) {
                throw new DomainException("Invalid retention period.");
            }

            Map<LocalDate, List<Customer>> cohorts =
                customers.values().stream().collect(
                    Collectors.groupingBy(
                        Customer::getSignupDate,
                        TreeMap::new,
                        Collectors.toList()
                    )
                );

            Map<LocalDate, CohortMetric> result = new TreeMap<>();

            cohorts.forEach((date, members) -> {
                long retained = members.stream()
                    .filter(customer ->
                        customer.getActiveDates().stream().anyMatch(day -> {
                            long elapsed =
                                java.time.temporal.ChronoUnit.DAYS.between(
                                    date, day
                                );

                            return elapsed >= 0 && elapsed <= periodDays;
                        })
                    )
                    .count();

                result.put(
                    date,
                    new CohortMetric(
                        date,
                        members.size(),
                        (int) retained,
                        StageMetrics.rate(retained, members.size())
                    )
                );
            });

            return Collections.unmodifiableMap(result);
        }

        public Map<String, Double> revenueReport() {
            long totalCents = customers.values().stream()
                .mapToLong(customer -> customer.revenueCents)
                .sum();

            long paying = customers.values().stream()
                .filter(Customer::isPaying)
                .count();

            double total = totalCents / 100.0;

            Map<String, Double> result = new LinkedHashMap<>();

            result.put("totalRevenue", total);
            result.put("payingCustomers", (double) paying);
            result.put("transactions", customers.values().stream()
                .mapToInt(customer -> customer.transactions)
                .sum());

            result.put(
                "ARPU",
                customers.isEmpty() ? 0.0 : total / customers.size()
            );

            result.put(
                "ARPPU",
                paying == 0 ? 0.0 : total / paying
            );

            return Collections.unmodifiableMap(result);
        }

        public Map<String, Long> referralReport() {
            return customers.values().stream()
                .filter(customer -> customer.getReferredBy() != null)
                .collect(Collectors.groupingBy(
                    Customer::getReferredBy,
                    TreeMap::new,
                    Collectors.counting()
                ));
        }

        public Map<CustomerStatus, Long> customerStatusReport() {
            Map<CustomerStatus, Long> result =
                new EnumMap<>(CustomerStatus.class);

            for (CustomerStatus status : CustomerStatus.values()) {
                result.put(status, customers.values().stream()
                    .filter(customer -> customer.status() == status)
                    .count());
            }

            return Collections.unmodifiableMap(result);
        }

        public int eventCount() {
            return eventHistory.size();
        }
    }

    static class ExperimentService {
        static ExperimentResult compare(
            List<Boolean> control,
            List<Boolean> treatment
        ) {
            if (control.isEmpty() || treatment.isEmpty()) {
                throw new DomainException(
                    "Experiment groups cannot be empty."
                );
            }

            Predicate<Boolean> converted = Boolean.TRUE::equals;

            double controlRate = control.stream()
                .filter(converted)
                .count() / (double) control.size();

            double treatmentRate = treatment.stream()
                .filter(converted)
                .count() / (double) treatment.size();

            return new ExperimentResult(
                controlRate * 100,
                treatmentRate * 100,
                (treatmentRate - controlRate) * 100,
                controlRate == 0
                    ? null
                    : (treatmentRate / controlRate - 1) * 100
            );
        }
    }

    static void printReport(GrowthService service) {
        StageMetrics metrics = service.metrics();

        System.out.println("\n========== AARRR ENTERPRISE REPORT ==========");

        System.out.println("\nACQUISITION");
        service.acquisitionReport().forEach((source, values) ->
            System.out.printf(
                "%s | Visitors %.0f | Signups %.0f | Conversion %.2f%%%n",
                source,
                values.get("visitors"),
                values.get("signups"),
                values.get("conversionRate")
            )
        );

        System.out.println("\nACTIVATION");
        System.out.printf(
            "Activation: %d / %d = %.2f%%%n",
            metrics.activated(),
            metrics.signups(),
            StageMetrics.rate(metrics.activated(), metrics.signups())
        );

        System.out.println("\nRETENTION");
        service.retentionReport(7).forEach((date, cohort) ->
            System.out.printf(
                "%s | Size %d | Retained %d | %.2f%%%n",
                date,
                cohort.cohortSize(),
                cohort.retainedUsers(),
                cohort.retentionRate()
            )
        );

        System.out.println("\nREVENUE");
        service.revenueReport().forEach((name, value) ->
            System.out.printf("%s: %.2f%n", name, value)
        );

        System.out.println("\nREFERRALS");
        service.referralReport().forEach((referrer, count) ->
            System.out.printf("%s: %d%n", referrer, count)
        );

        System.out.println("\nCUSTOMER STATES");
        service.customerStatusReport().forEach((status, count) ->
            System.out.println(status + ": " + count)
        );

        System.out.println("\nFUNNEL");
        metrics.conversionRates().forEach((stage, rate) ->
            System.out.printf("%s: %.2f%%%n", stage, rate)
        );
    }

    public static void main(String[] args) {
        try {
            GrowthPolicy policy = new GrowthPolicy(
                7,
                true,
                true,
                100_000_000
            );

            GrowthService service = new GrowthService(policy);

            LocalDate start = LocalDate.of(2026, 10, 1);

            service.createAndProcess(
                "U001", EventType.VISIT, start,
                "organic", null, 0
            );

            service.createAndProcess(
                "U001", EventType.SIGNUP, start,
                "organic", null, 0
            );

            service.createAndProcess(
                "U001", EventType.ACTIVATION, start.plusDays(1),
                null, null, 0
            );

            service.createAndProcess(
                "U001", EventType.LOGIN, start.plusDays(3),
                null, null, 0
            );

            service.createAndProcess(
                "U001", EventType.PURCHASE, start.plusDays(4),
                null, null, 4999
            );

            service.createAndProcess(
                "U001", EventType.REFERRAL_SENT, start.plusDays(5),
                null, null, 0
            );

            service.createAndProcess(
                "U002", EventType.VISIT, start,
                "paid", null, 0
            );

            service.createAndProcess(
                "U002", EventType.SIGNUP, start,
                "paid", null, 0
            );

            service.createAndProcess(
                "U002", EventType.ACTIVATION, start.plusDays(2),
                null, null, 0
            );

            service.createAndProcess(
                "U002", EventType.LOGIN, start.plusDays(5),
                null, null, 0
            );

            service.createAndProcess(
                "U002", EventType.SUBSCRIPTION, start.plusDays(6),
                null, null, 9900
            );

            service.createAndProcess(
                "U003", EventType.VISIT, start.plusDays(1),
                "referral", null, 0
            );

            service.createAndProcess(
                "U003", EventType.SIGNUP, start.plusDays(1),
                "referral", "U001", 0
            );

            service.createAndProcess(
                "U003", EventType.ACTIVATION, start.plusDays(2),
                null, null, 0
            );

            service.createAndProcess(
                "U003", EventType.LOGIN, start.plusDays(4),
                null, null, 0
            );

            service.createAndProcess(
                "U004", EventType.SIGNUP, start.plusDays(2),
                "social", null, 0
            );

            service.createAndProcess(
                "U004", EventType.ACTIVATION, start.plusDays(3),
                null, null, 0
            );

            service.createAndProcess(
                "U004", EventType.PURCHASE, start.plusDays(5),
                null, null, 2900
            );

            service.createAndProcess(
                "U005", EventType.SIGNUP, start.plusDays(3),
                "paid", null, 0
            );

            printReport(service);

            System.out.println("\nEXPERIMENT");
            ExperimentResult experiment = ExperimentService.compare(
                List.of(false, true, false, false, true, false),
                List.of(true, true, false, true, true, false)
            );

            System.out.println(experiment);

            System.out.println("\nMETRIC EXTENSION");

            List<GrowthMetric> metrics = List.of(
                new ActivationMetric(),
                new RevenueMetric()
            );

            for (GrowthMetric metric : metrics) {
                System.out.printf(
                    "%s: %.2f%n",
                    metric.name(),
                    metric.calculate(service.customers())
                );
            }

            // Failure-state test: a registered but inactive customer
            // must not be able to purchase.
            try {
                service.createAndProcess(
                    "U005", EventType.PURCHASE, start.plusDays(5),
                    null, null, 1000
                );

                throw new DomainException(
                    "Invalid purchase was unexpectedly accepted."
                );
            } catch (DomainException expected) {
                System.out.println(
                    "\nExpected policy rejection: " + expected.getMessage()
                );
            }

            System.out.println(
                "\nProcessed events: " + service.eventCount()
            );

        } catch (Exception error) {
            System.err.println("Enterprise growth failure: " +
                error.getMessage());
            System.exitCode = 1;
        }
    }
}
