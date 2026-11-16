import java.time.Duration;
import java.time.YearMonth;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
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
import java.util.stream.Collectors;

/*
 * Enterprise Product Analytics Platform
 *
 * Java 17
 *
 * Features:
 * - Typed analytics events
 * - Immutable user and event records
 * - Event ingestion and idempotency
 * - Identity resolution
 * - Session lifecycle
 * - Product metrics
 * - Ordered conversion funnels
 * - Cohort retention
 * - Analytics policy evaluation
 *
 * Compile:
 * javac ProductAnalytics.java
 *
 * Run:
 * java ProductAnalytics
 */

public class ProductAnalytics {

    // ========================================================
    // 1. Domain types
    // ========================================================

    enum EventType {
        SIGNUP,
        LOGIN,
        PAGE_VIEW,
        PRODUCT_VIEW,
        ADD_TO_CART,
        CHECKOUT_STARTED,
        PURCHASE
    }

    enum Plan {
        FREE,
        PREMIUM,
        ENTERPRISE
    }

    enum EventStatus {
        ACCEPTED,
        REJECTED,
        DUPLICATE
    }

    enum MetricPeriod {
        DAILY,
        WEEKLY,
        MONTHLY
    }

    // ========================================================
    // 2. Exceptions
    // ========================================================

    static class AnalyticsException extends RuntimeException {
        AnalyticsException(String message) {
            super(message);
        }
    }

    static class ValidationException extends AnalyticsException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class DuplicateEventException extends AnalyticsException {
        DuplicateEventException(String message) {
            super(message);
        }
    }

    // ========================================================
    // 3. Immutable domain records
    // ========================================================

    record User(
        String userId,
        String anonymousId,
        String country,
        Plan plan,
        Instant createdAt
    ) {
        User {
            requireText(userId, "User ID");
            requireText(country, "Country");

            Objects.requireNonNull(plan);
            Objects.requireNonNull(createdAt);
        }
    }

    record AnalyticsEvent(
        String eventId,
        String userId,
        EventType eventType,
        Instant timestamp,
        String sessionId,
        Map<String, Object> properties
    ) {
        AnalyticsEvent {
            requireText(eventId, "Event ID");
            requireText(userId, "User ID");

            Objects.requireNonNull(eventType);
            Objects.requireNonNull(timestamp);

            properties = validateProperties(properties);
        }
    }

    record Session(
        String sessionId,
        String userId,
        Instant startedAt,
        Instant lastEventAt,
        int eventCount,
        Set<EventType> eventTypes
    ) {
        Session {
            eventTypes = Set.copyOf(eventTypes);
        }

        long durationSeconds() {
            return Math.max(
                0,
                Duration.between(
                    startedAt,
                    lastEventAt
                ).getSeconds()
            );
        }
    }

    record FunnelResult(
        List<EventType> steps,
        List<Long> counts,
        List<Double> conversionRates,
        double overallConversion
    ) {
        FunnelResult {
            steps = List.copyOf(steps);
            counts = List.copyOf(counts);
            conversionRates = List.copyOf(conversionRates);
        }
    }

    record CohortResult(
        YearMonth cohortMonth,
        int cohortSize,
        Map<Integer, Integer> retained
    ) {
        CohortResult {
            retained = Collections.unmodifiableMap(
                new TreeMap<>(retained)
            );
        }

        double retentionRate(int monthOffset) {
            if (cohortSize == 0) return 0;

            return 100.0 * retained.getOrDefault(
                monthOffset,
                0
            ) / cohortSize;
        }
    }

    record AnalyticsSummary(
        long totalEvents,
        long activeUsers,
        double revenue,
        double averageOrderValue,
        Map<EventType, Long> eventCounts
    ) {
        AnalyticsSummary {
            eventCounts = Map.copyOf(eventCounts);
        }
    }

    // ========================================================
    // 4. Validation utilities
    // ========================================================

    static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new ValidationException(
                field + " cannot be empty."
            );
        }

        if (value.length() > 150) {
            throw new ValidationException(
                field + " exceeds maximum length."
            );
        }
    }

    static Map<String, Object> validateProperties(
        Map<String, Object> input
    ) {
        Objects.requireNonNull(input, "Properties cannot be null.");

        if (input.size() > 50) {
            throw new ValidationException(
                "Property limit exceeded."
            );
        }

        Map<String, Object> copy = new LinkedHashMap<>();

        for (var entry : input.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();

            requireText(key, "Property key");

            if (
                value != null &&
                !(value instanceof String) &&
                !(value instanceof Number) &&
                !(value instanceof Boolean)
            ) {
                throw new ValidationException(
                    "Unsupported property type: " + key
                );
            }

            if (value instanceof Double number &&
                !Double.isFinite(number)) {
                throw new ValidationException(
                    "Non-finite property: " + key
                );
            }

            if (value instanceof String text &&
                text.length() > 2000) {
                throw new ValidationException(
                    "Property value too large: " + key
                );
            }

            copy.put(key, value);
        }

        return Collections.unmodifiableMap(copy);
    }

    // ========================================================
    // 5. Identity service
    // ========================================================

    static class IdentityService {

        private final Map<String, User> users =
            new ConcurrentHashMap<>();

        private final Map<String, String> anonymousMappings =
            new ConcurrentHashMap<>();

        void register(User user) {
            Objects.requireNonNull(user);

            if (users.putIfAbsent(
                user.userId(),
                user
            ) != null) {
                throw new ValidationException(
                    "User already exists."
                );
            }

            if (user.anonymousId() != null) {
                String existing = anonymousMappings.putIfAbsent(
                    user.anonymousId(),
                    user.userId()
                );

                if (existing != null) {
                    users.remove(user.userId(), user);

                    throw new ValidationException(
                        "Anonymous identity already linked."
                    );
                }
            }
        }

        String resolve(String identifier) {
            if (users.containsKey(identifier)) {
                return identifier;
            }

            return anonymousMappings.get(identifier);
        }

        void link(String anonymousId, String userId) {
            requireText(anonymousId, "Anonymous ID");

            if (!users.containsKey(userId)) {
                throw new ValidationException(
                    "Unknown user."
                );
            }

            String existing = anonymousMappings.putIfAbsent(
                anonymousId,
                userId
            );

            if (existing != null && !existing.equals(userId)) {
                throw new ValidationException(
                    "Identity conflict."
                );
            }
        }

        Map<String, User> getUsers() {
            return Map.copyOf(users);
        }
    }

    // ========================================================
    // 6. Event ingestion service
    // ========================================================

    static class EventIngestionService {

        private final IdentityService identityService;

        private final Map<String, AnalyticsEvent> events =
            new ConcurrentHashMap<>();

        EventIngestionService(IdentityService identityService) {
            this.identityService = identityService;
        }

        EventStatus ingest(AnalyticsEvent input) {
            Objects.requireNonNull(input);

            String resolvedUser = identityService.resolve(
                input.userId()
            );

            if (resolvedUser == null) {
                throw new ValidationException(
                    "Unknown user identity."
                );
            }

            AnalyticsEvent normalized = new AnalyticsEvent(
                input.eventId(),
                resolvedUser,
                input.eventType(),
                input.timestamp(),
                input.sessionId(),
                input.properties()
            );

            AnalyticsEvent existing = events.putIfAbsent(
                normalized.eventId(),
                normalized
            );

            if (existing != null) {
                if (existing.equals(normalized)) {
                    return EventStatus.DUPLICATE;
                }

                throw new DuplicateEventException(
                    "Event ID reused with different content."
                );
            }

            return EventStatus.ACCEPTED;
        }

        List<AnalyticsEvent> getEvents() {
            return events.values()
                .stream()
                .sorted(
                    Comparator.comparing(
                        AnalyticsEvent::timestamp
                    ).thenComparing(
                        AnalyticsEvent::eventId
                    )
                )
                .toList();
        }

        List<AnalyticsEvent> getByUser(String userId) {
            return getEvents().stream()
                .filter(event -> event.userId().equals(userId))
                .toList();
        }
    }

    // ========================================================
    // 7. Session management service
    // ========================================================

    static class SessionService {

        private final Duration inactivityTimeout;

        SessionService(Duration inactivityTimeout) {
            if (
                inactivityTimeout == null ||
                inactivityTimeout.isZero() ||
                inactivityTimeout.isNegative()
            ) {
                throw new ValidationException(
                    "Invalid inactivity timeout."
                );
            }

            this.inactivityTimeout = inactivityTimeout;
        }

        List<Session> buildSessions(
            List<AnalyticsEvent> events
        ) {
            Map<String, List<AnalyticsEvent>> byUser =
                events.stream().collect(
                    Collectors.groupingBy(
                        AnalyticsEvent::userId
                    )
                );

            List<Session> sessions = new ArrayList<>();

            for (var entry : byUser.entrySet()) {
                List<AnalyticsEvent> userEvents = entry.getValue();

                userEvents.sort(
                    Comparator.comparing(
                        AnalyticsEvent::timestamp
                    ).thenComparing(
                        AnalyticsEvent::eventId
                    )
                );

                Instant startedAt = null;
                Instant lastEventAt = null;

                String sessionId = null;
                int eventCount = 0;

                Set<EventType> types = new HashSet<>();

                for (AnalyticsEvent event : userEvents) {
                    boolean expired = (
                        lastEventAt == null ||
                        Duration.between(
                            lastEventAt,
                            event.timestamp()
                        ).compareTo(inactivityTimeout) > 0
                    );

                    boolean changed = (
                        sessionId != null &&
                        event.sessionId() != null &&
                        !sessionId.equals(event.sessionId())
                    );

                    if (expired || changed) {
                        if (startedAt != null) {
                            sessions.add(
                                new Session(
                                    sessionId,
                                    entry.getKey(),
                                    startedAt,
                                    lastEventAt,
                                    eventCount,
                                    types
                                )
                            );
                        }

                        startedAt = event.timestamp();
                        sessionId = event.sessionId() != null
                            ? event.sessionId()
                            : UUID.randomUUID().toString();

                        eventCount = 0;
                        types = new HashSet<>();
                    }

                    lastEventAt = event.timestamp();
                    eventCount++;
                    types.add(event.eventType());
                }

                if (startedAt != null) {
                    sessions.add(
                        new Session(
                            sessionId,
                            entry.getKey(),
                            startedAt,
                            lastEventAt,
                            eventCount,
                            types
                        )
                    );
                }
            }

            return List.copyOf(sessions);
        }
    }

    // ========================================================
    // 8. Metrics service
    // ========================================================

    static class MetricsService {

        AnalyticsSummary calculate(
            List<AnalyticsEvent> events
        ) {
            Set<String> activeUsers = new HashSet<>();

            Map<EventType, Long> eventCounts =
                new EnumMap<>(EventType.class);

            double revenue = 0;
            long purchases = 0;

            for (AnalyticsEvent event : events) {
                activeUsers.add(event.userId());

                eventCounts.merge(
                    event.eventType(),
                    1L,
                    Long::sum
                );

                if (event.eventType() == EventType.PURCHASE) {
                    Object amount = event.properties().get("amount");

                    if (!(amount instanceof Number number)) {
                        throw new ValidationException(
                            "Purchase requires a numeric amount."
                        );
                    }

                    double value = number.doubleValue();

                    if (!Double.isFinite(value) || value < 0) {
                        throw new ValidationException(
                            "Invalid purchase amount."
                        );
                    }

                    revenue += value;
                    purchases++;
                }
            }

            return new AnalyticsSummary(
                events.size(),
                activeUsers.size(),
                revenue,
                purchases == 0 ? 0 : revenue / purchases,
                eventCounts
            );
        }
    }

    // ========================================================
    // 9. Funnel service
    // ========================================================

    static class FunnelService {

        FunnelResult evaluate(
            List<AnalyticsEvent> events,
            List<EventType> steps,
            Duration conversionWindow
        ) {
            if (steps == null || steps.size() < 2) {
                throw new ValidationException(
                    "At least two funnel steps required."
                );
            }

            if (new HashSet<>(steps).size() != steps.size()) {
                throw new ValidationException(
                    "Funnel steps must be unique."
                );
            }

            if (
                conversionWindow == null ||
                conversionWindow.isZero() ||
                conversionWindow.isNegative()
            ) {
                throw new ValidationException(
                    "Invalid conversion window."
                );
            }

            Map<String, List<AnalyticsEvent>> grouped =
                events.stream().collect(
                    Collectors.groupingBy(
                        AnalyticsEvent::userId
                    )
                );

            long[] counts = new long[steps.size()];

            for (List<AnalyticsEvent> userEvents : grouped.values()) {
                userEvents.sort(
                    Comparator.comparing(
                        AnalyticsEvent::timestamp
                    )
                );

                int cursor = 0;
                Instant firstStep = null;

                for (AnalyticsEvent event : userEvents) {
                    if (
                        event.eventType() != steps.get(cursor)
                    ) {
                        continue;
                    }

                    if (firstStep == null) {
                        firstStep = event.timestamp();
                    } else if (
                        Duration.between(
                            firstStep,
                            event.timestamp()
                        ).compareTo(conversionWindow) > 0
                    ) {
                        break;
                    }

                    counts[cursor]++;

                    cursor++;

                    if (cursor == steps.size()) {
                        break;
                    }
                }
            }

            List<Long> countList = new ArrayList<>();
            List<Double> rates = new ArrayList<>();

            for (int i = 0; i < steps.size(); i++) {
                countList.add(counts[i]);

                double rate;

                if (i == 0) {
                    rate = counts[0] > 0 ? 100.0 : 0.0;
                } else {
                    rate = counts[i - 1] == 0
                        ? 0.0
                        : 100.0 * counts[i] / counts[i - 1];
                }

                rates.add(rate);
            }

            double overall = counts[0] == 0
                ? 0.0
                : 100.0 * counts[counts.length - 1] / counts[0];

            return new FunnelResult(
                steps,
                countList,
                rates,
                overall
            );
        }
    }

    // ========================================================
    // 10. Cohort service
    // ========================================================

    static class CohortService {

        List<CohortResult> analyze(
            Map<String, User> users,
            List<AnalyticsEvent> events
        ) {
            Map<String, Set<YearMonth>> activity = new HashMap<>();

            for (AnalyticsEvent event : events) {
                YearMonth month = YearMonth.from(
                    event.timestamp().atZone(ZoneOffset.UTC)
                );

                activity.computeIfAbsent(
                    event.userId(),
                    key -> new HashSet<>()
                ).add(month);
            }

            Map<YearMonth, List<String>> cohorts = new TreeMap<>();

            for (User user : users.values()) {
                YearMonth month = YearMonth.from(
                    user.createdAt().atZone(ZoneOffset.UTC)
                );

                cohorts.computeIfAbsent(
                    month,
                    key -> new ArrayList<>()
                ).add(user.userId());
            }

            List<CohortResult> results = new ArrayList<>();

            for (var cohort : cohorts.entrySet()) {
                YearMonth cohortMonth = cohort.getKey();

                Map<Integer, Integer> retained = new TreeMap<>();

                for (String userId : cohort.getValue()) {
                    for (YearMonth activeMonth :
                        activity.getOrDefault(
                            userId,
                            Collections.emptySet()
                        )) {

                        long offset = java.time.temporal.ChronoUnit
                            .MONTHS.between(
                                cohortMonth,
                                activeMonth
                            );

                        if (offset >= 0) {
                            retained.merge(
                                Math.toIntExact(offset),
                                1,
                                Integer::sum
                            );
                        }
                    }
                }

                retained.put(0, cohort.getValue().size());

                results.add(
                    new CohortResult(
                        cohortMonth,
                        cohort.getValue().size(),
                        retained
                    )
                );
            }

            return List.copyOf(results);
        }
    }

    // ========================================================
    // 11. Analytics policy
    // ========================================================

    interface AnalyticsPolicy {
        boolean accepts(AnalyticsEvent event);
        String description();
    }

    static class PurchasePolicy implements AnalyticsPolicy {

        @Override
        public boolean accepts(AnalyticsEvent event) {
            if (event.eventType() != EventType.PURCHASE) {
                return true;
            }

            Object amount = event.properties().get("amount");

            return amount instanceof Number number &&
                Double.isFinite(number.doubleValue()) &&
                number.doubleValue() >= 0;
        }

        @Override
        public String description() {
            return "Purchases must contain a nonnegative numeric amount.";
        }
    }

    // ========================================================
    // 12. Test data builder
    // ========================================================

    static AnalyticsEvent event(
        String id,
        String userId,
        EventType type,
        Instant timestamp,
        Map<String, Object> properties
    ) {
        return new AnalyticsEvent(
            id,
            userId,
            type,
            timestamp,
            userId + "-SESSION-1",
            properties
        );
    }

    static void addJourney(
        EventIngestionService ingestion,
        String userId,
        Instant base,
        boolean purchase,
        double amount,
        String productId
    ) {
        EventType[] journey = purchase
            ? new EventType[] {
                EventType.SIGNUP,
                EventType.LOGIN,
                EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART,
                EventType.CHECKOUT_STARTED,
                EventType.PURCHASE
            }
            : new EventType[] {
                EventType.SIGNUP,
                EventType.LOGIN,
                EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART
            };

        for (int i = 0; i < journey.length; i++) {
            Map<String, Object> properties = new HashMap<>();

            if (
                journey[i] == EventType.PRODUCT_VIEW ||
                journey[i] == EventType.ADD_TO_CART
            ) {
                properties.put("productId", productId);
            }

            if (journey[i] == EventType.PURCHASE) {
                properties.put("amount", amount);
                properties.put("currency", "INR");
            }

            ingestion.ingest(
                event(
                    userId + "-EVENT-" + (i + 1),
                    userId,
                    journey[i],
                    base.plusSeconds(i * 60L),
                    properties
                )
            );
        }
    }

    // ========================================================
    // 13. Reporting
    // ========================================================

    static void report(
        AnalyticsSummary metrics,
        List<Session> sessions,
        FunnelResult funnel,
        List<CohortResult> cohorts
    ) {
        System.out.println("\nENTERPRISE PRODUCT ANALYTICS");
        System.out.println("============================");

        System.out.println("Events: " + metrics.totalEvents());
        System.out.println("Active users: " + metrics.activeUsers());
        System.out.printf(
            "Revenue: %.2f%n",
            metrics.revenue()
        );

        System.out.printf(
            "Average order value: %.2f%n",
            metrics.averageOrderValue()
        );

        System.out.println("\nEVENT COUNTS");

        metrics.eventCounts().forEach(
            (type, count) ->
                System.out.println(type + ": " + count)
        );

        System.out.println("\nSESSIONS");

        System.out.println("Total sessions: " + sessions.size());

        double averageDuration = sessions.stream()
            .mapToLong(Session::durationSeconds)
            .average()
            .orElse(0);

        System.out.printf(
            "Average duration: %.2f seconds%n",
            averageDuration
        );

        System.out.println("\nFUNNEL");

        for (int i = 0; i < funnel.steps().size(); i++) {
            System.out.printf(
                "%-20s users=%d conversion=%.2f%%%n",
                funnel.steps().get(i),
                funnel.counts().get(i),
                funnel.conversionRates().get(i)
            );
        }

        System.out.printf(
            "Overall conversion: %.2f%%%n",
            funnel.overallConversion()
        );

        System.out.println("\nCOHORTS");

        for (CohortResult cohort : cohorts) {
            System.out.println(
                cohort.cohortMonth() +
                " users=" + cohort.cohortSize()
            );

            cohort.retained().forEach(
                (offset, count) ->
                    System.out.printf(
                        "  M%d: %d users, %.2f%%%n",
                        offset,
                        count,
                        cohort.retentionRate(offset)
                    )
            );
        }
    }

    // ========================================================
    // 14. Application entry point
    // ========================================================

    public static void main(String[] args) {

        try {
            IdentityService identity = new IdentityService();

            Instant base = Instant.parse(
                "2026-09-01T09:00:00Z"
            );

            List<User> users = List.of(
                new User(
                    "U001", "A001", "IN",
                    Plan.FREE, base
                ),
                new User(
                    "U002", "A002", "IN",
                    Plan.PREMIUM, base.plusSeconds(7200)
                ),
                new User(
                    "U003", "A003", "US",
                    Plan.FREE, base.plusSeconds(86400)
                ),
                new User(
                    "U004", "A004", "IN",
                    Plan.PREMIUM, base.plusSeconds(2592000)
                ),
                new User(
                    "U005", "A005", "GB",
                    Plan.FREE, base.plusSeconds(2678400)
                )
            );

            users.forEach(identity::register);

            EventIngestionService ingestion =
                new EventIngestionService(identity);

            addJourney(
                ingestion,
                "U001",
                base,
                true,
                1499,
                "P100"
            );

            addJourney(
                ingestion,
                "U002",
                base.plusSeconds(7200),
                true,
                2499,
                "P200"
            );

            addJourney(
                ingestion,
                "U003",
                base.plusSeconds(86400),
                false,
                0,
                "P100"
            );

            addJourney(
                ingestion,
                "U004",
                base.plusSeconds(2592000),
                false,
                0,
                "P300"
            );

            addJourney(
                ingestion,
                "U005",
                base.plusSeconds(2678400),
                true,
                799,
                "P100"
            );

            List<AnalyticsEvent> events = ingestion.getEvents();

            if (events.size() != 26) {
                throw new AnalyticsException(
                    "Unexpected event count."
                );
            }

            // Verify idempotent event ingestion.
            EventStatus duplicateStatus = ingestion.ingest(
                events.get(0)
            );

            if (duplicateStatus != EventStatus.DUPLICATE) {
                throw new AnalyticsException(
                    "Duplicate event handling failed."
                );
            }

            MetricsService metricsService = new MetricsService();

            AnalyticsSummary metrics =
                metricsService.calculate(events);

            if (metrics.activeUsers() != 5) {
                throw new AnalyticsException(
                    "Incorrect active user count."
                );
            }

            if (Math.abs(metrics.revenue() - 4797.0) > 0.001) {
                throw new AnalyticsException(
                    "Incorrect revenue."
                );
            }

            SessionService sessionService =
                new SessionService(Duration.ofMinutes(30));

            List<Session> sessions =
                sessionService.buildSessions(events);

            FunnelService funnelService = new FunnelService();

            FunnelResult funnel = funnelService.evaluate(
                events,
                List.of(
                    EventType.SIGNUP,
                    EventType.PRODUCT_VIEW,
                    EventType.ADD_TO_CART,
                    EventType.CHECKOUT_STARTED,
                    EventType.PURCHASE
                ),
                Duration.ofDays(7)
            );

            if (funnel.counts().get(4) != 3) {
                throw new AnalyticsException(
                    "Unexpected funnel conversions."
                );
            }

            CohortService cohortService = new CohortService();

            List<CohortResult> cohorts =
                cohortService.analyze(
                    identity.getUsers(),
                    events
                );

            AnalyticsPolicy policy = new PurchasePolicy();

            for (AnalyticsEvent event : events) {
                if (!policy.accepts(event)) {
                    throw new AnalyticsException(
                        "Event violates policy: " +
                        policy.description()
                    );
                }
            }

            // Identity resolution test.
            if (!"U001".equals(identity.resolve("A001"))) {
                throw new AnalyticsException(
                    "Identity resolution failed."
                );
            }

            // Unknown identity test.
            try {
                ingestion.ingest(
                    new AnalyticsEvent(
                        "INVALID",
                        "UNKNOWN",
                        EventType.PAGE_VIEW,
                        base,
                        null,
                        Map.of()
                    )
                );

                throw new AnalyticsException(
                    "Unknown user was accepted."
                );

            } catch (ValidationException expected) {
                System.out.println(
                    "Unknown identity correctly rejected."
                );
            }

            report(
                metrics,
                sessions,
                funnel,
                cohorts
            );

            System.out.println(
                "\nAll enterprise analytics validations passed."
            );

        } catch (AnalyticsException error) {
            System.err.println(
                "Analytics error: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
