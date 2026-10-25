import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class ProductAnalyticsApp {

    enum EventType {
        VIEW, SIGNUP, ACTIVATION, PURCHASE, CHURN
    }

    record Product(int id, String name, String category) {
        Product {
            if (id <= 0) throw new IllegalArgumentException("Product ID must be positive.");
            requireText(name, "Product name");
            requireText(category, "Product category");
        }
    }

    record User(int id, String country, String acquisitionChannel) {
        User {
            if (id <= 0) throw new IllegalArgumentException("User ID must be positive.");
            requireText(country, "Country");
            requireText(acquisitionChannel, "Acquisition channel");
        }
    }

    record ProductEvent(
            int id,
            int userId,
            int productId,
            EventType type,
            LocalDate date,
            BigDecimal revenue) {
        ProductEvent {
            if (id <= 0) throw new IllegalArgumentException("Event ID must be positive.");
            Objects.requireNonNull(type, "Event type is required.");
            Objects.requireNonNull(date, "Event date is required.");
            Objects.requireNonNull(revenue, "Revenue is required.");

            if (revenue.signum() < 0) {
                throw new IllegalArgumentException("Revenue cannot be negative.");
            }
            if (type != EventType.PURCHASE && revenue.signum() != 0) {
                throw new IllegalArgumentException("Only purchases may record revenue.");
            }
            revenue = revenue.setScale(2, RoundingMode.HALF_UP);
        }
    }

    record RevenueReport(
            String product,
            String category,
            long purchaseEvents,
            BigDecimal revenue,
            BigDecimal averagePurchase) {}

    record ChannelReport(
            String channel,
            int registeredUsers,
            int payingUsers,
            BigDecimal revenue,
            BigDecimal conversionPercent) {}

    static final class AnalyticsException extends RuntimeException {
        AnalyticsException(String message) {
            super(message);
        }
    }

    static final class ProductAnalyticsService {
        private final List<Product> products;
        private final List<User> users;
        private final List<ProductEvent> events;
        private final Map<Integer, Product> productsById;
        private final Map<Integer, User> usersById;

        ProductAnalyticsService(
                List<Product> products,
                List<User> users,
                List<ProductEvent> events) {
            this.products = List.copyOf(products);
            this.users = List.copyOf(users);
            this.events = List.copyOf(events);
            this.productsById = uniqueIndex(this.products, Product::id, "product");
            this.usersById = uniqueIndex(this.users, User::id, "user");
            validateEvents();
        }

        private static <T> Map<Integer, T> uniqueIndex(
                List<T> items,
                java.util.function.ToIntFunction<T> idExtractor,
                String entityName) {
            Map<Integer, T> index = new HashMap<>();
            for (T item : items) {
                int id = idExtractor.applyAsInt(item);
                if (index.putIfAbsent(id, item) != null) {
                    throw new AnalyticsException("Duplicate " + entityName + " ID: " + id);
                }
            }
            return Map.copyOf(index);
        }

        private void validateEvents() {
            Set<Integer> eventIds = new HashSet<>();
            for (ProductEvent event : events) {
                if (!eventIds.add(event.id())) {
                    throw new AnalyticsException("Duplicate event ID: " + event.id());
                }
                if (!usersById.containsKey(event.userId())) {
                    throw new AnalyticsException("Unknown user in event " + event.id());
                }
                if (!productsById.containsKey(event.productId())) {
                    throw new AnalyticsException("Unknown product in event " + event.id());
                }
            }
        }

        private static void validateRange(LocalDate start, LocalDate end) {
            Objects.requireNonNull(start, "Start date is required.");
            Objects.requireNonNull(end, "End date is required.");
            if (start.isAfter(end)) {
                throw new IllegalArgumentException("Start date must not follow end date.");
            }
        }

        List<RevenueReport> revenueByProduct(LocalDate start, LocalDate end) {
            validateRange(start, end);

            Map<Integer, List<ProductEvent>> purchases = events.stream()
                    .filter(event -> event.type() == EventType.PURCHASE)
                    .filter(event -> !event.date().isBefore(start) && !event.date().isAfter(end))
                    .collect(Collectors.groupingBy(ProductEvent::productId));

            // Start from products, not purchases, to preserve products with zero revenue.
            return products.stream()
                    .map(product -> {
                        List<ProductEvent> matching =
                                purchases.getOrDefault(product.id(), List.of());

                        BigDecimal revenue = matching.stream()
                                .map(ProductEvent::revenue)
                                .reduce(BigDecimal.ZERO, BigDecimal::add);

                        BigDecimal average = matching.isEmpty()
                                ? BigDecimal.ZERO
                                : revenue.divide(
                                        BigDecimal.valueOf(matching.size()),
                                        2,
                                        RoundingMode.HALF_UP);

                        return new RevenueReport(
                                product.name(),
                                product.category(),
                                matching.size(),
                                revenue,
                                average);
                    })
                    .sorted(Comparator.comparing(RevenueReport::revenue)
                            .reversed()
                            .thenComparing(RevenueReport::product))
                    .toList();
        }

        List<ChannelReport> acquisitionPerformance() {
            Map<String, List<User>> usersByChannel = users.stream()
                    .collect(Collectors.groupingBy(
                            User::acquisitionChannel, TreeMap::new, Collectors.toList()));

            Map<String, Set<Integer>> payersByChannel = new HashMap<>();
            Map<String, BigDecimal> revenueByChannel = new HashMap<>();

            for (ProductEvent event : events) {
                if (event.type() != EventType.PURCHASE) continue;

                User user = usersById.get(event.userId());
                String channel = user.acquisitionChannel();

                payersByChannel.computeIfAbsent(channel, ignored -> new HashSet<>())
                        .add(user.id());
                revenueByChannel.merge(channel, event.revenue(), BigDecimal::add);
            }

            List<ChannelReport> reports = new ArrayList<>();
            for (Map.Entry<String, List<User>> entry : usersByChannel.entrySet()) {
                String channel = entry.getKey();
                int registered = entry.getValue().size();
                int payers = payersByChannel.getOrDefault(channel, Set.of()).size();

                BigDecimal revenue = revenueByChannel.getOrDefault(
                        channel, BigDecimal.ZERO);

                BigDecimal conversion = registered == 0
                        ? BigDecimal.ZERO
                        : BigDecimal.valueOf(payers)
                                .multiply(BigDecimal.valueOf(100))
                                .divide(BigDecimal.valueOf(registered), 2, RoundingMode.HALF_UP);

                reports.add(new ChannelReport(
                        channel, registered, payers, revenue, conversion));
            }

            return reports.stream()
                    .sorted(Comparator.comparing(ChannelReport::revenue).reversed()
                            .thenComparing(ChannelReport::channel))
                    .toList();
        }

        BigDecimal totalRevenue(LocalDate start, LocalDate end) {
            validateRange(start, end);
            return events.stream()
                    .filter(event -> event.type() == EventType.PURCHASE)
                    .filter(event -> !event.date().isBefore(start) && !event.date().isAfter(end))
                    .map(ProductEvent::revenue)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " cannot be blank.");
        }
    }

    private static ProductEvent event(
            int id, int userId, int productId, EventType type, String date, String revenue) {
        try {
            return new ProductEvent(
                    id, userId, productId, type, LocalDate.parse(date), new BigDecimal(revenue));
        } catch (DateTimeParseException exception) {
            throw new IllegalArgumentException("Invalid date for event " + id, exception);
        }
    }

    public static void main(String[] args) {
        List<Product> products = List.of(
                new Product(1, "Analytics Pro", "Analytics"),
                new Product(2, "Team Workspace", "Collaboration"),
                new Product(3, "Mobile Insights", "Analytics"));

        List<User> users = List.of(
                new User(101, "India", "Organic"),
                new User(102, "USA", "Paid Search"),
                new User(103, "India", "Referral"),
                new User(104, "UK", "Organic"),
                new User(105, "USA", "Paid Search"),
                new User(106, "India", "Referral"));

        List<ProductEvent> events = List.of(
                event(1, 101, 1, EventType.VIEW, "2026-03-01", "0"),
                event(2, 101, 1, EventType.ACTIVATION, "2026-03-02", "0"),
                event(3, 101, 1, EventType.PURCHASE, "2026-03-05", "99"),
                event(4, 102, 1, EventType.VIEW, "2026-03-02", "0"),
                event(5, 102, 1, EventType.PURCHASE, "2026-03-07", "149"),
                event(6, 103, 2, EventType.VIEW, "2026-03-03", "0"),
                event(7, 103, 2, EventType.ACTIVATION, "2026-03-04", "0"),
                event(8, 104, 2, EventType.VIEW, "2026-03-05", "0"),
                event(9, 105, 3, EventType.VIEW, "2026-03-06", "0"),
                event(10, 105, 3, EventType.ACTIVATION, "2026-03-07", "0"),
                event(11, 105, 3, EventType.PURCHASE, "2026-03-08", "49"),
                event(12, 106, 1, EventType.VIEW, "2026-03-09", "0"),
                event(13, 106, 1, EventType.CHURN, "2026-03-20", "0"),
                event(14, 101, 1, EventType.PURCHASE, "2026-04-02", "99"));

        try {
            ProductAnalyticsService service =
                    new ProductAnalyticsService(products, users, events);

            LocalDate start = LocalDate.parse("2026-03-01");
            LocalDate end = LocalDate.parse("2026-03-31");

            System.out.println("Revenue by product");
            service.revenueByProduct(start, end).forEach(System.out::println);

            System.out.println("\nAcquisition performance");
            service.acquisitionPerformance().forEach(System.out::println);

            BigDecimal revenue = service.totalRevenue(start, end);
            if (revenue.compareTo(new BigDecimal("297.00")) != 0) {
                throw new AnalyticsException("March revenue validation failed.");
            }
            System.out.println("\nValidated March revenue: " + revenue);

            try {
                service.totalRevenue(
                        LocalDate.parse("2026-04-01"),
                        LocalDate.parse("2026-03-01"));
                throw new AnalyticsException("Invalid date range was accepted.");
            } catch (IllegalArgumentException expected) {
                System.out.println("Invalid date range correctly rejected.");
            }
        } catch (RuntimeException exception) {
            System.err.println("Analytics failed: " + exception.getMessage());
            System.exit(1);
        }
    }
}
