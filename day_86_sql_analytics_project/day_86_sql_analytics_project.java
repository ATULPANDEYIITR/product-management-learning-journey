import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Enterprise Product Analytics Platform.
 *
 * Java 17.
 *
 * Domain areas:
 * - Product performance
 * - Customer event processing
 * - Conversion funnel
 * - Cohort retention
 * - RFM segmentation
 * - Acquisition channel analysis
 * - Data quality
 */
public class ProductAnalytics {

    enum EventType {
        VIEW,
        ADD_TO_CART,
        CHECKOUT,
        PURCHASE,
        REFUND
    }

    enum Segment {
        NO_PURCHASE,
        CHAMPIONS,
        LOYAL_CUSTOMERS,
        RECENT_CUSTOMERS,
        AT_RISK,
        DORMANT,
        REGULAR_CUSTOMERS
    }

    enum FunnelStage {
        VIEW,
        ADD_TO_CART,
        CHECKOUT,
        PURCHASE
    }

    static class AnalyticsException extends RuntimeException {
        AnalyticsException(String message) {
            super(message);
        }
    }

    record Product(
        int id,
        String name,
        String category,
        double price,
        double cost
    ) {
        Product {
            if (id <= 0 || name == null || name.isBlank()
                || category == null || category.isBlank()
                || !Double.isFinite(price)
                || !Double.isFinite(cost)
                || price < 0 || cost < 0) {
                throw new AnalyticsException("Invalid product");
            }
        }
    }

    record Customer(
        int id,
        LocalDate registeredAt,
        String acquisitionChannel,
        String region
    ) {
        Customer {
            if (id <= 0 || registeredAt == null
                || acquisitionChannel == null
                || acquisitionChannel.isBlank()
                || region == null || region.isBlank()) {
                throw new AnalyticsException("Invalid customer");
            }
        }
    }

    record Event(
        long id,
        int customerId,
        int productId,
        EventType type,
        LocalDate eventDate,
        int quantity,
        double amount,
        String sessionId
    ) {
        Event {
            if (id <= 0 || customerId <= 0 || productId <= 0
                || type == null || eventDate == null
                || quantity <= 0
                || !Double.isFinite(amount)
                || amount < 0) {
                throw new AnalyticsException("Invalid event");
            }

            if (type != EventType.PURCHASE && amount != 0) {
                throw new AnalyticsException(
                    "Only purchase events may contain transaction amounts"
                );
            }

            sessionId = sessionId == null ? "" : sessionId;
        }
    }

    record DateRange(LocalDate start, LocalDate end) {
        DateRange {
            Objects.requireNonNull(start);
            Objects.requireNonNull(end);

            if (start.isAfter(end)) {
                throw new AnalyticsException("Invalid date range");
            }
        }

        boolean contains(LocalDate date) {
            return !date.isBefore(start) && !date.isAfter(end);
        }
    }

    record ProductReport(
        String productName,
        String category,
        long views,
        long cartEvents,
        long purchases,
        long units,
        long uniqueBuyers,
        double revenue,
        double estimatedCost,
        double margin,
        double conversionRate
    ) {}

    record FunnelReport(
        FunnelStage stage,
        long users,
        Double conversionFromPrevious,
        Double conversionFromFirst
    ) {}

    record RetentionReport(
        String cohort,
        int monthNumber,
        long cohortSize,
        long activeCustomers,
        double retentionRate
    ) {}

    record CustomerReport(
        int customerId,
        Segment segment,
        Integer recency,
        long frequency,
        double monetary,
        String acquisitionChannel
    ) {}

    record ChannelReport(
        String channel,
        long visitors,
        long buyers,
        double revenue,
        double conversionRate
    ) {}

    record QualityReport(
        long eventCount,
        long uniqueEventIds,
        long customers,
        long products,
        long eventsWithoutSession,
        long purchaseEvents,
        long refundEvents
    ) {}

    static class ProductAccumulator {
        long views;
        long cartEvents;
        long purchases;
        long units;
        double revenue;
        Set<Integer> buyers = new HashSet<>();
    }

    static class CustomerPurchaseAccumulator {
        LocalDate latestPurchase;
        long frequency;
        double purchaseValue;
        double refunds;
    }

    static class EventRepository {
        private final Map<Integer, Product> products;
        private final Map<Integer, Customer> customers;

        private final Map<Long, Event> events =
            new ConcurrentHashMap<>();

        private final Map<Integer, List<Event>> customerIndex =
            new ConcurrentHashMap<>();

        private final LongAdder eventCount = new LongAdder();

        EventRepository(
            List<Product> products,
            List<Customer> customers
        ) {
            this.products = products.stream().collect(
                Collectors.toUnmodifiableMap(
                    Product::id,
                    product -> product
                )
            );

            this.customers = customers.stream().collect(
                Collectors.toUnmodifiableMap(
                    Customer::id,
                    customer -> customer
                )
            );
        }

        synchronized void insert(Event event) {
            validate(event);

            if (events.containsKey(event.id())) {
                throw new AnalyticsException("Duplicate event ID");
            }

            events.put(event.id(), event);

            customerIndex.computeIfAbsent(
                event.customerId(),
                ignored -> Collections.synchronizedList(
                    new ArrayList<>()
                )
            ).add(event);

            eventCount.increment();
        }

        private void validate(Event event) {
            Objects.requireNonNull(event);

            Customer customer = customers.get(event.customerId());

            if (customer == null) {
                throw new AnalyticsException("Unknown customer");
            }

            if (!products.containsKey(event.productId())) {
                throw new AnalyticsException("Unknown product");
            }

            if (event.eventDate().isBefore(customer.registeredAt())) {
                throw new AnalyticsException(
                    "Event predates registration"
                );
            }
        }

        List<Event> eventsIn(DateRange range) {
            return events.values().stream()
                .filter(e -> range.contains(e.eventDate()))
                .sorted(Comparator.comparing(Event::eventDate)
                    .thenComparingLong(Event::id))
                .toList();
        }

        List<Event> eventsForCustomer(int customerId) {
            return List.copyOf(
                customerIndex.getOrDefault(customerId, List.of())
            );
        }

        Product product(int id) {
            return products.get(id);
        }

        Customer customer(int id) {
            return customers.get(id);
        }

        Map<Integer, Customer> customers() {
            return customers;
        }

        Map<Integer, Product> products() {
            return products;
        }

        long count() {
            return eventCount.sum();
        }
    }

    static class ProductAnalyticsService {
        private final EventRepository repository;

        ProductAnalyticsService(EventRepository repository) {
            this.repository = repository;
        }

        List<ProductReport> productPerformance(DateRange range) {
            Map<Integer, ProductAccumulator> metrics = new HashMap<>();

            for (Event event : repository.eventsIn(range)) {
                ProductAccumulator row = metrics.computeIfAbsent(
                    event.productId(),
                    ignored -> new ProductAccumulator()
                );

                switch (event.type()) {
                    case VIEW -> row.views++;
                    case ADD_TO_CART -> row.cartEvents++;
                    case PURCHASE -> {
                        row.purchases++;
                        row.units += event.quantity();
                        row.revenue += event.amount();
                        row.buyers.add(event.customerId());
                    }
                    case REFUND -> row.revenue -= event.amount();
                    case CHECKOUT -> {
                        // Checkout events are not purchase transactions.
                    }
                }
            }

            List<ProductReport> output = new ArrayList<>();

            metrics.forEach((productId, row) -> {
                Product product = repository.product(productId);
                double estimatedCost = row.units * product.cost();

                output.add(new ProductReport(
                    product.name(),
                    product.category(),
                    row.views,
                    row.cartEvents,
                    row.purchases,
                    row.units,
                    row.buyers.size(),
                    round(row.revenue),
                    round(estimatedCost),
                    round(row.revenue - estimatedCost),
                    row.views == 0 ? 0 :
                        round(100.0 * row.purchases / row.views)
                ));
            });

            output.sort(
                Comparator.comparingDouble(ProductReport::revenue)
                    .reversed()
            );

            return List.copyOf(output);
        }

        List<FunnelReport> conversionFunnel(DateRange range) {
            Map<FunnelStage, Set<Integer>> stageUsers =
                new EnumMap<>(FunnelStage.class);

            for (FunnelStage stage : FunnelStage.values()) {
                stageUsers.put(stage, new HashSet<>());
            }

            for (Event event : repository.eventsIn(range)) {
                try {
                    stageUsers.get(
                        FunnelStage.valueOf(event.type().name())
                    ).add(event.customerId());
                } catch (IllegalArgumentException ignored) {
                    // Refund events do not belong to the conversion funnel.
                }
            }

            long firstCount = stageUsers.get(FunnelStage.VIEW).size();
            Long previous = null;

            List<FunnelReport> result = new ArrayList<>();

            for (FunnelStage stage : FunnelStage.values()) {
                long current = stageUsers.get(stage).size();

                Double previousRate = previous == null || previous == 0
                    ? null
                    : round(100.0 * current / previous);

                Double firstRate = firstCount == 0
                    ? null
                    : round(100.0 * current / firstCount);

                result.add(new FunnelReport(
                    stage,
                    current,
                    previousRate,
                    firstRate
                ));

                previous = current;
            }

            return List.copyOf(result);
        }

        Map<String, Long> orderedSessionFunnel(DateRange range) {
            Map<String, List<Event>> sessions = repository.eventsIn(range)
                .stream()
                .filter(event -> !event.sessionId().isBlank())
                .collect(Collectors.groupingBy(Event::sessionId));

            Map<String, Long> result = new TreeMap<>();

            for (FunnelStage stage : FunnelStage.values()) {
                result.put(stage.name(), 0L);
            }

            for (List<Event> session : sessions.values()) {
                session.sort(
                    Comparator.comparing(Event::eventDate)
                        .thenComparingLong(Event::id)
                );

                int expected = 0;

                for (Event event : session) {
                    if (expected < FunnelStage.values().length
                        && event.type().name().equals(
                            FunnelStage.values()[expected].name()
                        )) {
                        expected++;
                    }
                }

                for (int i = 0; i < expected; i++) {
                    String key = FunnelStage.values()[i].name();
                    result.merge(key, 1L, Long::sum);
                }
            }

            return Map.copyOf(result);
        }

        List<RetentionReport> retention(
            LocalDate cohortStart,
            LocalDate cohortEnd,
            LocalDate analysisEnd
        ) {
            if (cohortStart.isAfter(cohortEnd)
                || cohortEnd.isAfter(analysisEnd)) {
                throw new AnalyticsException("Invalid cohort range");
            }

            Map<LocalDate, Set<Integer>> cohorts = new TreeMap<>();
            Map<LocalDate, Set<Integer>> monthlyActivity = new HashMap<>();

            for (Customer customer : repository.customers().values()) {
                if (!customer.registeredAt().isBefore(cohortStart)
                    && !customer.registeredAt().isAfter(cohortEnd)) {

                    LocalDate key = customer.registeredAt()
                        .withDayOfMonth(1);

                    cohorts.computeIfAbsent(
                        key, ignored -> new HashSet<>()
                    ).add(customer.id());
                }
            }

            for (Event event : repository.eventsIn(
                new DateRange(cohortStart, analysisEnd)
            )) {
                LocalDate key = event.eventDate().withDayOfMonth(1);

                monthlyActivity.computeIfAbsent(
                    key, ignored -> new HashSet<>()
                ).add(event.customerId());
            }

            List<RetentionReport> result = new ArrayList<>();

            for (var cohort : cohorts.entrySet()) {
                LocalDate cohortMonth = cohort.getKey();
                Set<Integer> members = cohort.getValue();

                int months = (int) ChronoUnit.MONTHS.between(
                    cohortMonth,
                    analysisEnd.withDayOfMonth(1)
                );

                for (int month = 0; month <= months; month++) {
                    LocalDate current = cohortMonth.plusMonths(month);

                    Set<Integer> activeUsers = monthlyActivity.getOrDefault(
                        current,
                        Set.of()
                    );

                    long active = members.stream()
                        .filter(activeUsers::contains)
                        .count();

                    result.add(new RetentionReport(
                        cohortMonth.toString(),
                        month,
                        members.size(),
                        active,
                        round(100.0 * active / members.size())
                    ));
                }
            }

            return List.copyOf(result);
        }

        List<CustomerReport> segmentation(LocalDate referenceDate) {
            List<CustomerReport> reports = new ArrayList<>();

            for (Customer customer : repository.customers().values()) {
                CustomerPurchaseAccumulator data =
                    new CustomerPurchaseAccumulator();

                for (Event event :
                    repository.eventsForCustomer(customer.id())) {

                    if (event.eventDate().isAfter(referenceDate)) {
                        continue;
                    }

                    if (event.type() == EventType.PURCHASE) {
                        data.frequency++;
                        data.purchaseValue += event.amount();

                        if (data.latestPurchase == null ||
                            event.eventDate().isAfter(data.latestPurchase)) {
                            data.latestPurchase = event.eventDate();
                        }
                    } else if (event.type() == EventType.REFUND) {
                        data.refunds += event.amount();
                    }
                }

                if (data.frequency == 0) {
                    reports.add(new CustomerReport(
                        customer.id(),
                        Segment.NO_PURCHASE,
                        null,
                        0,
                        0,
                        customer.acquisitionChannel()
                    ));
                    continue;
                }

                int recency = (int) ChronoUnit.DAYS.between(
                    data.latestPurchase,
                    referenceDate
                );

                double monetary = data.purchaseValue - data.refunds;

                if (monetary < 0) {
                    throw new AnalyticsException(
                        "Refunds exceed purchase value"
                    );
                }

                Segment segment;

                if (recency <= 30 && data.frequency >= 3
                    && monetary >= 5000) {
                    segment = Segment.CHAMPIONS;
                } else if (recency <= 60 && data.frequency >= 2) {
                    segment = Segment.LOYAL_CUSTOMERS;
                } else if (recency <= 30 && data.frequency == 1) {
                    segment = Segment.RECENT_CUSTOMERS;
                } else if (recency > 90 && data.frequency >= 2) {
                    segment = Segment.AT_RISK;
                } else if (recency > 180) {
                    segment = Segment.DORMANT;
                } else {
                    segment = Segment.REGULAR_CUSTOMERS;
                }

                reports.add(new CustomerReport(
                    customer.id(),
                    segment,
                    recency,
                    data.frequency,
                    round(monetary),
                    customer.acquisitionChannel()
                ));
            }

            reports.sort(
                Comparator.comparing(CustomerReport::segment)
                    .thenComparingInt(CustomerReport::customerId)
            );

            return List.copyOf(reports);
        }

        List<ChannelReport> channelPerformance(DateRange range) {
            class ChannelData {
                Set<Integer> visitors = new HashSet<>();
                Set<Integer> buyers = new HashSet<>();
                double revenue;
            }

            Map<String, ChannelData> metrics = new HashMap<>();

            for (Event event : repository.eventsIn(range)) {
                Customer customer = repository.customer(
                    event.customerId()
                );

                ChannelData row = metrics.computeIfAbsent(
                    customer.acquisitionChannel(),
                    ignored -> new ChannelData()
                );

                switch (event.type()) {
                    case VIEW -> row.visitors.add(customer.id());
                    case PURCHASE -> {
                        row.buyers.add(customer.id());
                        row.revenue += event.amount();
                    }
                    case REFUND -> row.revenue -= event.amount();
                    default -> {
                    }
                }
            }

            return metrics.entrySet().stream()
                .map(entry -> {
                    ChannelData row = entry.getValue();

                    return new ChannelReport(
                        entry.getKey(),
                        row.visitors.size(),
                        row.buyers.size(),
                        round(row.revenue),
                        row.visitors.isEmpty()
                            ? 0
                            : round(
                                100.0 * row.buyers.size()
                                / row.visitors.size()
                            )
                    );
                })
                .sorted(
                    Comparator.comparingDouble(ChannelReport::revenue)
                        .reversed()
                )
                .toList();
        }

        QualityReport qualityReport() {
            List<Event> all = repository.eventsIn(
                new DateRange(
                    LocalDate.of(2000, 1, 1),
                    LocalDate.of(2100, 1, 1)
                )
            );

            return new QualityReport(
                all.size(),
                all.stream().map(Event::id).distinct().count(),
                repository.customers().size(),
                repository.products().size(),
                all.stream().filter(
                    e -> e.sessionId().isBlank()
                ).count(),
                all.stream().filter(
                    e -> e.type() == EventType.PURCHASE
                ).count(),
                all.stream().filter(
                    e -> e.type() == EventType.REFUND
                ).count()
            );
        }

        private static double round(double value) {
            return Math.round(value * 100.0) / 100.0;
        }
    }

    static List<Product> sampleProducts() {
        return List.of(
            new Product(101, "Laptop Pro", "Electronics", 1200, 850),
            new Product(102, "Wireless Mouse", "Accessories", 35, 12),
            new Product(103, "Mechanical Keyboard", "Accessories", 95, 48),
            new Product(104, "Smart Watch", "Wearables", 250, 140),
            new Product(105, "USB-C Hub", "Accessories", 55, 22)
        );
    }

    static List<Customer> sampleCustomers() {
        return List.of(
            new Customer(1, LocalDate.of(2026, 1, 5), "Organic", "North"),
            new Customer(2, LocalDate.of(2026, 1, 12), "Paid Search", "South"),
            new Customer(3, LocalDate.of(2026, 2, 3), "Social", "East"),
            new Customer(4, LocalDate.of(2026, 2, 15), "Organic", "West"),
            new Customer(5, LocalDate.of(2026, 3, 1), "Referral", "North"),
            new Customer(6, LocalDate.of(2026, 3, 10), "Paid Search", "South"),
            new Customer(7, LocalDate.of(2026, 4, 2), "Social", "East"),
            new Customer(8, LocalDate.of(2026, 4, 15), "Referral", "West")
        );
    }

    static List<Event> sampleEvents() {
        LocalDate base = LocalDate.of(2026, 4, 1);

        Object[][] raw = {
            {1,1,101,EventType.VIEW,0,0},
            {2,1,101,EventType.ADD_TO_CART,1,0},
            {3,1,101,EventType.CHECKOUT,2,0},
            {4,1,101,EventType.PURCHASE,3,1200},
            {5,1,102,EventType.PURCHASE,40,35},
            {6,1,103,EventType.PURCHASE,60,95},
            {7,2,102,EventType.VIEW,1,0},
            {8,2,102,EventType.ADD_TO_CART,2,0},
            {9,2,102,EventType.PURCHASE,4,35},
            {10,2,102,EventType.REFUND,10,0},
            {11,3,104,EventType.VIEW,5,0},
            {12,3,104,EventType.PURCHASE,7,250},
            {13,4,103,EventType.VIEW,12,0},
            {14,4,103,EventType.ADD_TO_CART,13,0},
            {15,4,103,EventType.CHECKOUT,14,0},
            {16,4,103,EventType.PURCHASE,15,95},
            {17,5,105,EventType.VIEW,20,0},
            {18,5,105,EventType.PURCHASE,22,55},
            {19,6,101,EventType.VIEW,25,0},
            {20,6,101,EventType.ADD_TO_CART,26,0},
            {21,7,104,EventType.VIEW,28,0},
            {22,8,102,EventType.VIEW,29,0},
            {23,8,102,EventType.PURCHASE,30,35}
        };

        List<Event> result = new ArrayList<>();

        for (Object[] row : raw) {
            long id = (int) row[0];
            int customer = (int) row[1];
            int product = (int) row[2];
            EventType type = (EventType) row[3];
            int day = (int) row[4];
            double amount = (double) row[5];

            result.add(new Event(
                id,
                customer,
                product,
                type,
                base.plusDays(day),
                1,
                amount,
                "S-" + customer + "-" + day / 7
            ));
        }

        return List.copyOf(result);
    }

    public static void main(String[] args) {
        try {
            EventRepository repository = new EventRepository(
                sampleProducts(),
                sampleCustomers()
            );

            for (Event event : sampleEvents()) {
                repository.insert(event);
            }

            ProductAnalyticsService service =
                new ProductAnalyticsService(repository);

            DateRange reportingPeriod = new DateRange(
                LocalDate.of(2026, 4, 1),
                LocalDate.of(2026, 6, 30)
            );

            System.out.println("PRODUCT PERFORMANCE");

            service.productPerformance(reportingPeriod)
                .forEach(System.out::println);

            System.out.println("\nCONVERSION FUNNEL");

            service.conversionFunnel(reportingPeriod)
                .forEach(System.out::println);

            System.out.println("\nORDERED SESSION FUNNEL");

            System.out.println(
                service.orderedSessionFunnel(reportingPeriod)
            );

            System.out.println("\nRETENTION");

            service.retention(
                LocalDate.of(2026, 1, 1),
                LocalDate.of(2026, 4, 30),
                LocalDate.of(2026, 6, 30)
            ).forEach(System.out::println);

            System.out.println("\nCUSTOMER SEGMENTATION");

            service.segmentation(
                LocalDate.of(2026, 6, 30)
            ).forEach(System.out::println);

            System.out.println("\nCHANNEL PERFORMANCE");

            service.channelPerformance(reportingPeriod)
                .forEach(System.out::println);

            System.out.println("\nDATA QUALITY");

            System.out.println(service.qualityReport());

            try {
                repository.insert(sampleEvents().get(0));
                throw new AnalyticsException(
                    "Duplicate validation failed"
                );
            } catch (AnalyticsException expected) {
                if (!expected.getMessage().equals("Duplicate event ID")) {
                    throw expected;
                }

                System.out.println("Duplicate event validation: PASS");
            }

            System.out.println(
                "Accepted events: " + repository.count()
            );

        } catch (AnalyticsException exception) {
            System.err.println(
                "Analytics failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
