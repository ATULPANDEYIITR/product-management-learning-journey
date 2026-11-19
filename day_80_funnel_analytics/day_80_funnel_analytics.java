import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Enterprise Funnel Analytics
 *
 * Java 17
 * No third-party dependencies.
 *
 * Models event ingestion, cohort construction, sequential funnel
 * progression, segmentation, conversion analysis, and reporting.
 */

public class FunnelAnalytics {

    enum EventType {
        VISIT("visit"),
        PRODUCT_VIEW("product_view"),
        ADD_TO_CART("add_to_cart"),
        CHECKOUT("checkout"),
        PURCHASE("purchase");

        private final String value;

        EventType(String value) {
            this.value = value;
        }

        public String value() {
            return value;
        }
    }

    enum Device {
        MOBILE,
        DESKTOP,
        TABLET
    }

    enum Channel {
        ORGANIC,
        PAID,
        REFERRAL
    }

    record AnalyticsEvent(
        String eventId,
        String userId,
        EventType type,
        Instant timestamp,
        Channel channel,
        Device device,
        String country,
        Map<String, String> attributes
    ) {
        AnalyticsEvent {
            Objects.requireNonNull(eventId);
            Objects.requireNonNull(userId);
            Objects.requireNonNull(type);
            Objects.requireNonNull(timestamp);
            Objects.requireNonNull(channel);
            Objects.requireNonNull(device);
            Objects.requireNonNull(country);

            if (eventId.isBlank() || userId.isBlank()) {
                throw new IllegalArgumentException(
                    "Event ID and user ID are required."
                );
            }

            attributes = Map.copyOf(attributes);
        }
    }

    record FunnelDefinition(
        String name,
        List<EventType> steps,
        Duration conversionWindow
    ) {
        FunnelDefinition {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Funnel name is required."
                );
            }

            steps = List.copyOf(steps);

            if (steps.size() < 2) {
                throw new IllegalArgumentException(
                    "A funnel requires at least two steps."
                );
            }

            if (new HashSet<>(steps).size() != steps.size()) {
                throw new IllegalArgumentException(
                    "Funnel steps must be unique."
                );
            }

            Objects.requireNonNull(conversionWindow);

            if (
                conversionWindow.isZero() ||
                conversionWindow.isNegative()
            ) {
                throw new IllegalArgumentException(
                    "Invalid conversion window."
                );
            }
        }
    }

    record StepMetric(
        EventType step,
        long users,
        long previousUsers,
        long droppedUsers,
        double conversionRate,
        double dropOffRate
    ) {}

    record FunnelReport(
        String funnelName,
        long totalUsers,
        long convertedUsers,
        double overallConversionRate,
        List<StepMetric> steps
    ) {
        FunnelReport {
            steps = List.copyOf(steps);
        }
    }

    static class EventRepository {
        private final Map<String, AnalyticsEvent> events =
            new HashMap<>();

        private final Map<String, List<AnalyticsEvent>> users =
            new HashMap<>();

        public synchronized void add(AnalyticsEvent event) {
            Objects.requireNonNull(event);

            if (events.containsKey(event.eventId())) {
                throw new IllegalArgumentException(
                    "Duplicate event ID: " + event.eventId()
                );
            }

            events.put(event.eventId(), event);

            users.computeIfAbsent(
                event.userId(),
                ignored -> new ArrayList<>()
            ).add(event);
        }

        public synchronized void addBatch(
            List<AnalyticsEvent> batch
        ) {
            Set<String> incoming = new HashSet<>();

            for (AnalyticsEvent event : batch) {
                if (
                    event == null ||
                    events.containsKey(event.eventId()) ||
                    !incoming.add(event.eventId())
                ) {
                    throw new IllegalArgumentException(
                        "Invalid or duplicate batch event."
                    );
                }
            }

            // Commit only after complete batch validation.
            for (AnalyticsEvent event : batch) {
                add(event);
            }
        }

        public synchronized List<AnalyticsEvent> getUserEvents(
            String userId
        ) {
            return users.getOrDefault(
                userId,
                Collections.emptyList()
            ).stream()
                .sorted(Comparator.comparing(
                    AnalyticsEvent::timestamp
                ))
                .toList();
        }

        public synchronized List<String> userIds() {
            return List.copyOf(users.keySet());
        }

        public synchronized long size() {
            return events.size();
        }
    }

    interface CohortPolicy {
        boolean include(AnalyticsEvent entryEvent);
    }

    static class ChannelPolicy implements CohortPolicy {
        private final Channel requiredChannel;

        ChannelPolicy(Channel requiredChannel) {
            this.requiredChannel = requiredChannel;
        }

        @Override
        public boolean include(AnalyticsEvent event) {
            return event.channel() == requiredChannel;
        }
    }

    static class DevicePolicy implements CohortPolicy {
        private final Device requiredDevice;

        DevicePolicy(Device requiredDevice) {
            this.requiredDevice = requiredDevice;
        }

        @Override
        public boolean include(AnalyticsEvent event) {
            return event.device() == requiredDevice;
        }
    }

    static class FunnelAnalysisService {
        private final EventRepository repository;

        FunnelAnalysisService(EventRepository repository) {
            this.repository = Objects.requireNonNull(repository);
        }

        private boolean[] evaluateProgression(
            List<AnalyticsEvent> events,
            FunnelDefinition funnel,
            Instant entryTime
        ) {
            boolean[] completed = new boolean[
                funnel.steps().size()
            ];

            int nextStep = 0;

            for (AnalyticsEvent event : events) {
                if (event.timestamp().isBefore(entryTime)) {
                    continue;
                }

                if (
                    Duration.between(
                        entryTime,
                        event.timestamp()
                    ).compareTo(funnel.conversionWindow()) > 0
                ) {
                    break;
                }

                if (event.type() != funnel.steps().get(nextStep)) {
                    continue;
                }

                completed[nextStep] = true;
                nextStep++;

                if (nextStep == funnel.steps().size()) {
                    break;
                }
            }

            return completed;
        }

        public FunnelReport analyze(
            FunnelDefinition funnel,
            CohortPolicy policy
        ) {
            Objects.requireNonNull(funnel);

            long[] counts = new long[funnel.steps().size()];

            for (String userId : repository.userIds()) {
                List<AnalyticsEvent> events =
                    repository.getUserEvents(userId);

                AnalyticsEvent entry = events.stream()
                    .filter(event ->
                        event.type() == funnel.steps().get(0)
                    )
                    .findFirst()
                    .orElse(null);

                if (entry == null) {
                    continue;
                }

                if (
                    policy != null &&
                    !policy.include(entry)
                ) {
                    continue;
                }

                boolean[] progression = evaluateProgression(
                    events,
                    funnel,
                    entry.timestamp()
                );

                for (int i = 0; i < progression.length; i++) {
                    if (!progression[i]) {
                        break;
                    }

                    counts[i]++;
                }
            }

            return buildReport(funnel, counts);
        }

        private FunnelReport buildReport(
            FunnelDefinition funnel,
            long[] counts
        ) {
            List<StepMetric> metrics = new ArrayList<>();

            for (int i = 0; i < counts.length; i++) {
                long previous = i == 0
                    ? counts[i]
                    : counts[i - 1];

                long dropped = previous - counts[i];

                double conversion = previous == 0
                    ? 0
                    : 100.0 * counts[i] / previous;

                double dropOff = previous == 0
                    ? 0
                    : 100.0 * dropped / previous;

                metrics.add(new StepMetric(
                    funnel.steps().get(i),
                    counts[i],
                    previous,
                    dropped,
                    conversion,
                    dropOff
                ));
            }

            long total = counts[0];
            long converted = counts[counts.length - 1];

            double overall = total == 0
                ? 0
                : 100.0 * converted / total;

            FunnelReport report = new FunnelReport(
                funnel.name(),
                total,
                converted,
                overall,
                metrics
            );

            validate(report);

            return report;
        }

        private void validate(FunnelReport report) {
            for (int i = 1; i < report.steps().size(); i++) {
                if (
                    report.steps().get(i).users() >
                    report.steps().get(i - 1).users()
                ) {
                    throw new IllegalStateException(
                        "Funnel count invariant violated."
                    );
                }
            }
        }

        public Map<Channel, FunnelReport> byChannel(
            FunnelDefinition funnel
        ) {
            Map<Channel, FunnelReport> result =
                new LinkedHashMap<>();

            for (Channel channel : Channel.values()) {
                result.put(
                    channel,
                    analyze(funnel, new ChannelPolicy(channel))
                );
            }

            return result;
        }

        public Map<Device, FunnelReport> byDevice(
            FunnelDefinition funnel
        ) {
            Map<Device, FunnelReport> result =
                new LinkedHashMap<>();

            for (Device device : Device.values()) {
                result.put(
                    device,
                    analyze(funnel, new DevicePolicy(device))
                );
            }

            return result;
        }
    }

    static class FunnelReportingService {
        public void print(FunnelReport report) {
            System.out.println(
                "\nFUNNEL: " + report.funnelName()
            );

            System.out.println(
                "Initial users: " + report.totalUsers()
            );

            System.out.println(
                "Converted users: " + report.convertedUsers()
            );

            System.out.printf(
                "Overall conversion: %.2f%%%n",
                report.overallConversionRate()
            );

            System.out.printf(
                "%-20s %10s %15s %15s %10s%n",
                "Step",
                "Users",
                "Conversion",
                "Drop-off",
                "Dropped"
            );

            for (StepMetric metric : report.steps()) {
                System.out.printf(
                    "%-20s %10d %14.2f%% %14.2f%% %10d%n",
                    metric.step().value(),
                    metric.users(),
                    metric.conversionRate(),
                    metric.dropOffRate(),
                    metric.droppedUsers()
                );
            }
        }

        public List<Map<String, Object>> toRows(
            FunnelReport report
        ) {
            return report.steps().stream().map(metric -> {
                Map<String, Object> row = new LinkedHashMap<>();

                row.put("step", metric.step().value());
                row.put("users", metric.users());
                row.put("conversion_rate", metric.conversionRate());
                row.put("drop_off_rate", metric.dropOffRate());

                return row;
            }).toList();
        }
    }

    private static EventRepository sampleData() {
        EventRepository repository = new EventRepository();

        EventType[][] journeys = {
            {
                EventType.VISIT, EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART, EventType.CHECKOUT,
                EventType.PURCHASE
            },
            {
                EventType.VISIT, EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART, EventType.CHECKOUT
            },
            {
                EventType.VISIT, EventType.PRODUCT_VIEW
            },
            {
                EventType.VISIT, EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART, EventType.CHECKOUT,
                EventType.PURCHASE
            },
            {
                EventType.VISIT, EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART
            },
            {
                EventType.VISIT
            },
            {
                EventType.VISIT, EventType.PRODUCT_VIEW,
                EventType.ADD_TO_CART, EventType.CHECKOUT,
                EventType.PURCHASE
            },
            {
                EventType.VISIT, EventType.PRODUCT_VIEW,
                EventType.CHECKOUT
            }
        };

        Channel[] channels = {
            Channel.ORGANIC,
            Channel.PAID,
            Channel.ORGANIC,
            Channel.PAID,
            Channel.REFERRAL,
            Channel.ORGANIC,
            Channel.PAID,
            Channel.REFERRAL
        };

        Device[] devices = {
            Device.MOBILE,
            Device.DESKTOP,
            Device.MOBILE,
            Device.DESKTOP,
            Device.MOBILE,
            Device.DESKTOP,
            Device.MOBILE,
            Device.DESKTOP
        };

        Instant base = Instant.parse(
            "2026-11-01T09:00:00Z"
        );

        List<AnalyticsEvent> batch = new ArrayList<>();

        int counter = 1;

        for (int i = 0; i < journeys.length; i++) {
            for (int j = 0; j < journeys[i].length; j++) {
                Instant timestamp = base.plus(
                    Duration.ofMinutes(i * 15L + j * 3L)
                );

                batch.add(new AnalyticsEvent(
                    String.format("E%04d", counter++),
                    String.format("U%03d", i + 1),
                    journeys[i][j],
                    timestamp,
                    channels[i],
                    devices[i],
                    i % 2 == 0 ? "IN" : "US",
                    Map.of("campaign", "winter_2026")
                ));
            }
        }

        repository.addBatch(batch);

        return repository;
    }

    private static void runTests(
        FunnelAnalysisService service,
        FunnelDefinition funnel
    ) {
        FunnelReport report = service.analyze(funnel, null);

        if (
            report.totalUsers() != 8 ||
            report.convertedUsers() != 3 ||
            report.steps().get(1).users() != 7 ||
            report.steps().get(2).users() != 5 ||
            report.steps().get(3).users() != 4
        ) {
            throw new AssertionError("Funnel test failed.");
        }

        FunnelReport organic = service.analyze(
            funnel,
            new ChannelPolicy(Channel.ORGANIC)
        );

        if (organic.totalUsers() != 3) {
            throw new AssertionError("Channel test failed.");
        }

        FunnelReport mobile = service.analyze(
            funnel,
            new DevicePolicy(Device.MOBILE)
        );

        if (mobile.totalUsers() != 4) {
            throw new AssertionError("Device test failed.");
        }

        System.out.println("\nAll Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            EventRepository repository = sampleData();

            FunnelDefinition funnel = new FunnelDefinition(
                "E-commerce Purchase Funnel",
                List.of(
                    EventType.VISIT,
                    EventType.PRODUCT_VIEW,
                    EventType.ADD_TO_CART,
                    EventType.CHECKOUT,
                    EventType.PURCHASE
                ),
                Duration.ofHours(24)
            );

            FunnelAnalysisService service =
                new FunnelAnalysisService(repository);

            FunnelReportingService reporting =
                new FunnelReportingService();

            FunnelReport report = service.analyze(funnel, null);

            reporting.print(report);

            System.out.println("\nCHANNEL SEGMENTATION");

            service.byChannel(funnel).forEach((channel, result) -> {
                System.out.printf(
                    "%s: %d/%d, %.2f%%%n",
                    channel,
                    result.convertedUsers(),
                    result.totalUsers(),
                    result.overallConversionRate()
                );
            });

            System.out.println("\nDEVICE SEGMENTATION");

            service.byDevice(funnel).forEach((device, result) -> {
                System.out.printf(
                    "%s: %d/%d, %.2f%%%n",
                    device,
                    result.convertedUsers(),
                    result.totalUsers(),
                    result.overallConversionRate()
                );
            });

            runTests(service, funnel);

            System.out.println(
                "\nTotal stored events: " + repository.size()
            );

        } catch (Exception exception) {
            System.err.println(
                "Analytics failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
