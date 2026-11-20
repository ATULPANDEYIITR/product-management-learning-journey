import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.stream.Collectors;

/*
 * Enterprise Retention Analytics
 *
 * Domain:
 *   Customer -> Events -> Acquisition Cohort
 *   -> Retention -> Churn -> Resurrection
 *
 * Retention uses exact elapsed-day activity.
 * Churn uses an inactivity threshold.
 * Resurrection records activity after a qualifying inactivity gap.
 */
public class RetentionAnalytics {

    enum EventType {
        SIGNUP,
        ACTIVE,
        LOGIN,
        PURCHASE
    }

    enum CustomerStatus {
        ACTIVE,
        CHURNED,
        NOT_ELIGIBLE
    }

    record CustomerEvent(
        String customerId,
        LocalDate eventDate,
        EventType eventType
    ) {
        CustomerEvent {
            if (customerId == null ||
                customerId.isBlank() ||
                customerId.length() > 128) {
                throw new IllegalArgumentException(
                    "Invalid customer ID"
                );
            }

            Objects.requireNonNull(eventDate);
            Objects.requireNonNull(eventType);
        }
    }

    record RetentionMetric(
        int day,
        int eligibleCustomers,
        int retainedCustomers,
        double retentionRate
    ) {}

    record ResurrectionEvent(
        String customerId,
        LocalDate previousActivity,
        LocalDate resurrectionDate,
        long inactiveDays
    ) {}

    record ChurnReport(
        int active,
        int churned,
        int notEligible,
        double churnRate
    ) {}

    record Customer(
        String customerId,
        LocalDate signupDate,
        LocalDate lastActivity,
        Set<LocalDate> activityDates
    ) {
        Customer {
            activityDates = Collections.unmodifiableSet(
                new TreeSet<>(activityDates)
            );
        }
    }

    static class AnalyticsException extends RuntimeException {
        AnalyticsException(String message) {
            super(message);
        }
    }

    static class RetentionPolicy {
        private final int churnDays;
        private final List<Integer> intervals;

        RetentionPolicy(int churnDays, Collection<Integer> intervals) {
            if (churnDays < 1) {
                throw new IllegalArgumentException(
                    "Churn threshold must be positive"
                );
            }

            if (intervals == null || intervals.isEmpty() ||
                intervals.stream().anyMatch(
                    day -> day == null || day < 0
                )) {
                throw new IllegalArgumentException(
                    "Invalid retention intervals"
                );
            }

            this.churnDays = churnDays;

            this.intervals = intervals.stream()
                .distinct()
                .sorted()
                .toList();
        }

        int churnDays() {
            return churnDays;
        }

        List<Integer> intervals() {
            return intervals;
        }

        CustomerStatus evaluate(
            long tenureDays,
            long inactiveDays
        ) {
            if (tenureDays < churnDays) {
                return CustomerStatus.NOT_ELIGIBLE;
            }

            return inactiveDays >= churnDays
                ? CustomerStatus.CHURNED
                : CustomerStatus.ACTIVE;
        }
    }

    static class EventRepository {
        private final Map<String, Set<CustomerEvent>> events =
            new HashMap<>();

        public synchronized void add(CustomerEvent event) {
            Objects.requireNonNull(event);

            events.computeIfAbsent(
                event.customerId(),
                ignored -> new HashSet<>()
            ).add(event);
        }

        public synchronized void addBatch(
            Collection<CustomerEvent> batch
        ) {
            if (batch == null) {
                throw new IllegalArgumentException(
                    "Batch cannot be null"
                );
            }

            // Validate before inserting to avoid partial ingestion.
            List<CustomerEvent> validated = new ArrayList<>();

            for (CustomerEvent event : batch) {
                validated.add(Objects.requireNonNull(event));
            }

            for (CustomerEvent event : validated) {
                add(event);
            }
        }

        public synchronized Map<String, List<CustomerEvent>> snapshot() {
            Map<String, List<CustomerEvent>> copy = new TreeMap<>();

            for (var entry : events.entrySet()) {
                List<CustomerEvent> sorted = entry.getValue()
                    .stream()
                    .sorted(
                        Comparator.comparing(
                            CustomerEvent::eventDate
                        ).thenComparing(
                            CustomerEvent::eventType
                        )
                    )
                    .toList();

                copy.put(entry.getKey(), sorted);
            }

            return Collections.unmodifiableMap(copy);
        }

        public synchronized int size() {
            return events.values()
                .stream()
                .mapToInt(Set::size)
                .sum();
        }
    }

    static class CustomerProjection {
        private final EventRepository repository;

        CustomerProjection(EventRepository repository) {
            this.repository = repository;
        }

        Map<String, Customer> build() {
            Map<String, Customer> customers = new TreeMap<>();

            for (var entry : repository.snapshot().entrySet()) {
                String customerId = entry.getKey();
                List<CustomerEvent> events = entry.getValue();

                LocalDate signup = events.stream()
                    .filter(event ->
                        event.eventType() == EventType.SIGNUP
                    )
                    .map(CustomerEvent::eventDate)
                    .min(LocalDate::compareTo)
                    .orElseThrow(() -> new AnalyticsException(
                        "Missing signup event: " + customerId
                    ));

                Set<LocalDate> activities = events.stream()
                    .filter(event ->
                        EnumSet.of(
                            EventType.ACTIVE,
                            EventType.LOGIN,
                            EventType.PURCHASE
                        ).contains(event.eventType())
                    )
                    .map(CustomerEvent::eventDate)
                    .filter(date -> !date.isBefore(signup))
                    .collect(Collectors.toCollection(TreeSet::new));

                LocalDate lastActivity = activities.stream()
                    .max(LocalDate::compareTo)
                    .orElse(signup);

                customers.put(
                    customerId,
                    new Customer(
                        customerId,
                        signup,
                        lastActivity,
                        activities
                    )
                );
            }

            return Collections.unmodifiableMap(customers);
        }
    }

    static class RetentionService {
        private final RetentionPolicy policy;
        private final Map<String, Customer> customers;

        RetentionService(
            RetentionPolicy policy,
            Map<String, Customer> customers
        ) {
            this.policy = policy;
            this.customers = Map.copyOf(customers);

            if (this.customers.isEmpty()) {
                throw new AnalyticsException(
                    "No customers available"
                );
            }
        }

        private void validateObservation(LocalDate observation) {
            Objects.requireNonNull(observation);

            boolean invalid = customers.values()
                .stream()
                .anyMatch(customer ->
                    observation.isBefore(customer.signupDate())
                );

            if (invalid) {
                throw new AnalyticsException(
                    "Observation date precedes a signup"
                );
            }
        }

        List<RetentionMetric> retentionCurve(
            LocalDate observation
        ) {
            validateObservation(observation);

            List<RetentionMetric> report = new ArrayList<>();

            for (int interval : policy.intervals()) {
                List<Customer> eligible = customers.values()
                    .stream()
                    .filter(customer ->
                        !customer.signupDate()
                            .plusDays(interval)
                            .isAfter(observation)
                    )
                    .toList();

                int retained = (int) eligible.stream()
                    .filter(customer ->
                        customer.activityDates().contains(
                            customer.signupDate().plusDays(interval)
                        )
                    )
                    .count();

                double percentage = eligible.isEmpty()
                    ? 0.0
                    : 100.0 * retained / eligible.size();

                report.add(new RetentionMetric(
                    interval,
                    eligible.size(),
                    retained,
                    percentage
                ));
            }

            return List.copyOf(report);
        }

        Map<String, Map<Integer, Double>> cohortRetention(
            LocalDate observation,
            int maxAge
        ) {
            validateObservation(observation);

            if (maxAge < 0) {
                throw new IllegalArgumentException(
                    "Maximum cohort age cannot be negative"
                );
            }

            Map<String, List<Customer>> cohorts =
                customers.values()
                    .stream()
                    .collect(Collectors.groupingBy(
                        customer -> customer.signupDate()
                            .withDayOfMonth(1).toString(),
                        TreeMap::new,
                        Collectors.toList()
                    ));

            Map<String, Map<Integer, Double>> report =
                new LinkedHashMap<>();

            for (var cohort : cohorts.entrySet()) {
                Map<Integer, Double> periods = new TreeMap<>();

                for (int age = 0; age <= maxAge; age++) {
                    final int interval = age;

                    List<Customer> eligible = cohort.getValue()
                        .stream()
                        .filter(customer ->
                            !customer.signupDate()
                                .plusDays(interval)
                                .isAfter(observation)
                        )
                        .toList();

                    if (eligible.isEmpty()) {
                        continue;
                    }

                    long retained = eligible.stream()
                        .filter(customer ->
                            customer.activityDates().contains(
                                customer.signupDate()
                                    .plusDays(interval)
                            )
                        )
                        .count();

                    periods.put(
                        age,
                        100.0 * retained / eligible.size()
                    );
                }

                report.put(
                    cohort.getKey(),
                    Collections.unmodifiableMap(periods)
                );
            }

            return Collections.unmodifiableMap(report);
        }

        ChurnReport churnAnalysis(LocalDate observation) {
            validateObservation(observation);

            int active = 0;
            int churned = 0;
            int notEligible = 0;

            for (Customer customer : customers.values()) {
                long tenure = ChronoUnit.DAYS.between(
                    customer.signupDate(),
                    observation
                );

                long inactive = ChronoUnit.DAYS.between(
                    customer.lastActivity(),
                    observation
                );

                CustomerStatus status = policy.evaluate(
                    tenure,
                    inactive
                );

                switch (status) {
                    case ACTIVE -> active++;
                    case CHURNED -> churned++;
                    case NOT_ELIGIBLE -> notEligible++;
                }
            }

            int eligible = active + churned;

            return new ChurnReport(
                active,
                churned,
                notEligible,
                eligible == 0
                    ? 0.0
                    : 100.0 * churned / eligible
            );
        }

        List<ResurrectionEvent> resurrectionAnalysis(
            LocalDate observation
        ) {
            validateObservation(observation);

            List<ResurrectionEvent> report = new ArrayList<>();

            for (Customer customer : customers.values()) {
                List<LocalDate> dates = customer.activityDates()
                    .stream()
                    .filter(date -> !date.isAfter(observation))
                    .sorted()
                    .toList();

                for (int index = 1; index < dates.size(); index++) {
                    LocalDate previous = dates.get(index - 1);
                    LocalDate current = dates.get(index);

                    long gap = ChronoUnit.DAYS.between(
                        previous,
                        current
                    );

                    if (gap >= policy.churnDays()) {
                        report.add(new ResurrectionEvent(
                            customer.customerId(),
                            previous,
                            current,
                            gap
                        ));
                    }
                }
            }

            return List.copyOf(report);
        }

        Map<String, Object> generateReport(
            LocalDate observation
        ) {
            validateObservation(observation);

            Map<String, Object> report = new LinkedHashMap<>();

            report.put("observationDate", observation);
            report.put("totalCustomers", customers.size());
            report.put("retentionCurve", retentionCurve(observation));
            report.put(
                "cohortRetention",
                cohortRetention(observation, 30)
            );
            report.put("churn", churnAnalysis(observation));
            report.put(
                "resurrection",
                resurrectionAnalysis(observation)
            );

            return Collections.unmodifiableMap(report);
        }
    }

    private static List<CustomerEvent> sampleEvents() {
        List<CustomerEvent> events = new ArrayList<>();

        add(events, "U001", "2026-01-01", EventType.SIGNUP);
        add(events, "U001", "2026-01-01", EventType.ACTIVE);
        add(events, "U001", "2026-01-02", EventType.ACTIVE);
        add(events, "U001", "2026-01-08", EventType.ACTIVE);
        add(events, "U001", "2026-03-05", EventType.ACTIVE);

        add(events, "U002", "2026-01-03", EventType.SIGNUP);
        add(events, "U002", "2026-01-03", EventType.ACTIVE);

        add(events, "U003", "2026-01-10", EventType.SIGNUP);
        add(events, "U003", "2026-01-10", EventType.ACTIVE);
        add(events, "U003", "2026-02-15", EventType.ACTIVE);

        add(events, "U004", "2026-02-01", EventType.SIGNUP);
        add(events, "U004", "2026-02-01", EventType.ACTIVE);
        add(events, "U004", "2026-02-02", EventType.ACTIVE);

        add(events, "U005", "2026-02-05", EventType.SIGNUP);
        add(events, "U005", "2026-02-05", EventType.ACTIVE);

        add(events, "U006", "2026-02-15", EventType.SIGNUP);
        add(events, "U006", "2026-02-15", EventType.ACTIVE);
        add(events, "U006", "2026-03-20", EventType.ACTIVE);

        add(events, "U007", "2026-03-01", EventType.SIGNUP);
        add(events, "U007", "2026-03-01", EventType.ACTIVE);

        add(events, "U008", "2026-03-10", EventType.SIGNUP);
        add(events, "U008", "2026-03-10", EventType.ACTIVE);

        add(events, "U009", "2026-03-15", EventType.SIGNUP);
        add(events, "2026-03-15", "2026-03-15", EventType.ACTIVE);

        return events;
    }

    private static void add(
        List<CustomerEvent> events,
        String userId,
        String date,
        EventType type
    ) {
        events.add(new CustomerEvent(
            userId,
            LocalDate.parse(date),
            type
        ));
    }

    private static void runTests() {
        EventRepository repository = new EventRepository();

        List<CustomerEvent> events = sampleEvents();

        repository.addBatch(events);
        repository.add(events.get(0));

        CustomerProjection projection =
            new CustomerProjection(repository);

        Map<String, Customer> customers = projection.build();

        if (customers.size() != 9) {
            throw new AssertionError("Customer count test failed");
        }

        RetentionPolicy policy = new RetentionPolicy(
            30,
            List.of(0, 1, 7, 14, 30)
        );

        RetentionService service = new RetentionService(
            policy,
            customers
        );

        LocalDate observation = LocalDate.parse("2026-05-01");

        List<RetentionMetric> curve =
            service.retentionCurve(observation);

        if (curve.get(0).retainedCustomers() != 9) {
            throw new AssertionError("Day-zero retention failed");
        }

        ChurnReport churn = service.churnAnalysis(observation);

        if (churn.active() + churn.churned() != 9) {
            throw new AssertionError("Churn eligibility failed");
        }

        if (service.resurrectionAnalysis(observation).isEmpty()) {
            throw new AssertionError("Resurrection test failed");
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            if (args.length > 0 && args[0].equals("--test")) {
                runTests();
                return;
            }

            EventRepository repository = new EventRepository();

            repository.addBatch(sampleEvents());

            CustomerProjection projection =
                new CustomerProjection(repository);

            Map<String, Customer> customers = projection.build();

            RetentionPolicy policy = new RetentionPolicy(
                30,
                List.of(0, 1, 7, 14, 30)
            );

            RetentionService service = new RetentionService(
                policy,
                customers
            );

            Map<String, Object> report = service.generateReport(
                LocalDate.parse("2026-05-01")
            );

            report.forEach((key, value) -> {
                System.out.println("\n" + key);
                System.out.println(value);
            });

        } catch (Exception exception) {
            System.err.println(
                "Retention analytics failure: " +
                exception.getMessage()
            );

            System.exit(1);
        }
    }
}
