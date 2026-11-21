import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.stream.Collectors;

public class EngagementMetricsEnterprise {

    enum EventType {
        LOGIN(true),
        PAGE_VIEW(true),
        ACTION(true),
        PURCHASE(true),
        LOGOUT(false);

        private final boolean qualifying;

        EventType(boolean qualifying) {
            this.qualifying = qualifying;
        }

        boolean qualifies() {
            return qualifying;
        }
    }

    enum SessionStatus {
        ACTIVE,
        COMPLETED
    }

    record User(String id, String organization) {
        User {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("User ID is required.");
            }
            if (organization == null || organization.isBlank()) {
                throw new IllegalArgumentException(
                    "Organization is required."
                );
            }
        }
    }

    record EngagementEvent(
        String eventId,
        User user,
        EventType type,
        Instant timestamp
    ) {
        EngagementEvent {
            Objects.requireNonNull(eventId, "Event ID is required.");
            Objects.requireNonNull(user, "User is required.");
            Objects.requireNonNull(type, "Event type is required.");
            Objects.requireNonNull(timestamp, "Timestamp is required.");

            if (eventId.isBlank()) {
                throw new IllegalArgumentException("Empty event ID.");
            }

            if (timestamp.isAfter(Instant.now().plusSeconds(300))) {
                throw new IllegalArgumentException(
                    "Future event timestamp rejected."
                );
            }
        }
    }

    record Session(
        String userId,
        Instant startedAt,
        Instant lastEventAt,
        int eventCount,
        SessionStatus status
    ) {
        long durationSeconds() {
            return Duration.between(
                startedAt,
                lastEventAt
            ).toSeconds();
        }
    }

    record EngagementPolicy(
        Duration sessionTimeout,
        int weeklyWindowDays,
        int monthlyWindowDays,
        ZoneOffset reportingZone
    ) {
        EngagementPolicy {
            Objects.requireNonNull(sessionTimeout);
            Objects.requireNonNull(reportingZone);

            if (
                sessionTimeout.isZero() ||
                sessionTimeout.isNegative() ||
                sessionTimeout.compareTo(Duration.ofDays(1)) > 0
            ) {
                throw new IllegalArgumentException(
                    "Session timeout must be positive and at most one day."
                );
            }

            if (weeklyWindowDays != 7 || monthlyWindowDays != 30) {
                throw new IllegalArgumentException(
                    "This implementation requires 7-day and 30-day windows."
                );
            }
        }

        static EngagementPolicy standard() {
            return new EngagementPolicy(
                Duration.ofMinutes(30),
                7,
                30,
                ZoneOffset.UTC
            );
        }
    }

    record EngagementReport(
        LocalDate date,
        int dau,
        int wau,
        int mau,
        double stickiness,
        int qualifyingEvents,
        int sessions,
        double averageSessionDuration,
        double averageSessionsPerUser,
        double averageEventsPerSession
    ) {}

    static class DuplicateEventException extends RuntimeException {
        DuplicateEventException(String message) {
            super(message);
        }
    }

    static class EventRepository {
        private final Map<String, EngagementEvent> eventsById =
            new HashMap<>();

        private final Map<String, List<EngagementEvent>> eventsByUser =
            new HashMap<>();

        public synchronized void save(EngagementEvent event) {
            if (eventsById.containsKey(event.eventId())) {
                throw new DuplicateEventException(
                    "Duplicate event ID: " + event.eventId()
                );
            }

            eventsById.put(event.eventId(), event);

            eventsByUser
                .computeIfAbsent(
                    event.user().id(),
                    key -> new ArrayList<>()
                )
                .add(event);
        }

        public synchronized List<EngagementEvent> allEvents() {
            return List.copyOf(eventsById.values());
        }

        public synchronized List<EngagementEvent> eventsForUser(
            String userId
        ) {
            return List.copyOf(
                eventsByUser.getOrDefault(userId, List.of())
            );
        }

        public synchronized int size() {
            return eventsById.size();
        }
    }

    static class SessionService {
        private final EngagementPolicy policy;

        SessionService(EngagementPolicy policy) {
            this.policy = policy;
        }

        List<Session> generate(List<EngagementEvent> events) {
            Map<String, List<EngagementEvent>> grouped =
                events.stream()
                    .filter(event -> event.type().qualifies())
                    .collect(Collectors.groupingBy(
                        event -> event.user().id()
                    ));

            List<Session> sessions = new ArrayList<>();

            Comparator<EngagementEvent> ordering =
                Comparator.comparing(EngagementEvent::timestamp)
                    .thenComparing(EngagementEvent::eventId);

            for (var entry : grouped.entrySet()) {
                List<EngagementEvent> userEvents = entry.getValue();

                userEvents.sort(ordering);

                Instant start = null;
                Instant last = null;
                int count = 0;

                for (EngagementEvent event : userEvents) {
                    Instant current = event.timestamp();

                    if (
                        start == null ||
                        Duration.between(last, current)
                            .compareTo(policy.sessionTimeout()) > 0
                    ) {
                        if (start != null) {
                            sessions.add(new Session(
                                entry.getKey(),
                                start,
                                last,
                                count,
                                SessionStatus.COMPLETED
                            ));
                        }

                        start = current;
                        last = current;
                        count = 1;
                    } else {
                        last = current;
                        count++;
                    }
                }

                if (start != null) {
                    sessions.add(new Session(
                        entry.getKey(),
                        start,
                        last,
                        count,
                        SessionStatus.COMPLETED
                    ));
                }
            }

            sessions.sort(
                Comparator.comparing(Session::startedAt)
                    .thenComparing(Session::userId)
            );

            return List.copyOf(sessions);
        }
    }

    static class EngagementService {
        private final EventRepository repository;
        private final EngagementPolicy policy;
        private final SessionService sessionService;

        EngagementService(
            EventRepository repository,
            EngagementPolicy policy
        ) {
            this.repository = repository;
            this.policy = policy;
            this.sessionService = new SessionService(policy);
        }

        private Set<String> activeUsers(
            Instant start,
            Instant end
        ) {
            return repository.allEvents()
                .stream()
                .filter(event -> event.type().qualifies())
                .filter(event ->
                    !event.timestamp().isBefore(start) &&
                    event.timestamp().isBefore(end)
                )
                .map(event -> event.user().id())
                .collect(Collectors.toSet());
        }

        public EngagementReport calculate(LocalDate date) {
            Objects.requireNonNull(date);

            Instant dayStart = date.atStartOfDay(
                policy.reportingZone()
            ).toInstant();

            Instant dayEnd = date.plusDays(1)
                .atStartOfDay(policy.reportingZone())
                .toInstant();

            Instant weekStart = date.minusDays(
                policy.weeklyWindowDays() - 1
            ).atStartOfDay(policy.reportingZone()).toInstant();

            Instant monthStart = date.minusDays(
                policy.monthlyWindowDays() - 1
            ).atStartOfDay(policy.reportingZone()).toInstant();

            Set<String> dauUsers = activeUsers(dayStart, dayEnd);
            Set<String> wauUsers = activeUsers(weekStart, dayEnd);
            Set<String> mauUsers = activeUsers(monthStart, dayEnd);

            List<EngagementEvent> dailyEvents =
                repository.allEvents()
                    .stream()
                    .filter(event -> event.type().qualifies())
                    .filter(event ->
                        !event.timestamp().isBefore(dayStart) &&
                        event.timestamp().isBefore(dayEnd)
                    )
                    .toList();

            List<Session> sessions =
                sessionService.generate(dailyEvents);

            double duration = sessions.stream()
                .mapToLong(Session::durationSeconds)
                .average()
                .orElse(0.0);

            double averageEvents = sessions.stream()
                .mapToInt(Session::eventCount)
                .average()
                .orElse(0.0);

            long sessionUsers = sessions.stream()
                .map(Session::userId)
                .distinct()
                .count();

            double averageSessions = sessionUsers == 0
                ? 0.0
                : (double) sessions.size() / sessionUsers;

            double stickiness = mauUsers.isEmpty()
                ? 0.0
                : 100.0 * dauUsers.size() / mauUsers.size();

            return new EngagementReport(
                date,
                dauUsers.size(),
                wauUsers.size(),
                mauUsers.size(),
                stickiness,
                dailyEvents.size(),
                sessions.size(),
                duration,
                averageSessions,
                averageEvents
            );
        }

        public Map<Integer, Long> frequencyDistribution(
            LocalDate date
        ) {
            Instant start = date.atStartOfDay(
                policy.reportingZone()
            ).toInstant();

            Instant end = date.plusDays(1)
                .atStartOfDay(policy.reportingZone())
                .toInstant();

            List<EngagementEvent> dailyEvents =
                repository.allEvents()
                    .stream()
                    .filter(event -> event.type().qualifies())
                    .filter(event ->
                        !event.timestamp().isBefore(start) &&
                        event.timestamp().isBefore(end)
                    )
                    .toList();

            Map<String, Long> userSessions =
                sessionService.generate(dailyEvents)
                    .stream()
                    .collect(Collectors.groupingBy(
                        Session::userId,
                        Collectors.counting()
                    ));

            return userSessions.values()
                .stream()
                .collect(Collectors.groupingBy(
                    count -> count.intValue(),
                    TreeMap::new,
                    Collectors.counting()
                ));
        }
    }

    private static EngagementEvent event(
        String eventId,
        String userId,
        EventType type,
        String timestamp
    ) {
        return new EngagementEvent(
            eventId,
            new User(userId, "enterprise_001"),
            type,
            Instant.parse(timestamp)
        );
    }

    private static void printReport(EngagementReport report) {
        System.out.println("\nENTERPRISE ENGAGEMENT REPORT");
        System.out.println("Date: " + report.date());
        System.out.println("DAU: " + report.dau());
        System.out.println("WAU: " + report.wau());
        System.out.println("MAU: " + report.mau());
        System.out.printf(
            "Stickiness: %.2f%%%n",
            report.stickiness()
        );
        System.out.println(
            "Qualifying events: " + report.qualifyingEvents()
        );
        System.out.println("Sessions: " + report.sessions());
        System.out.printf(
            "Average session duration: %.2f seconds%n",
            report.averageSessionDuration()
        );
        System.out.printf(
            "Average sessions per user: %.2f%n",
            report.averageSessionsPerUser()
        );
        System.out.printf(
            "Average events per session: %.2f%n",
            report.averageEventsPerSession()
        );
    }

    public static void main(String[] args) {
        try {
            EngagementPolicy policy = EngagementPolicy.standard();
            EventRepository repository = new EventRepository();

            List<EngagementEvent> sample = List.of(
                event(
                    "e1", "user_001", EventType.LOGIN,
                    "2026-11-19T09:00:00Z"
                ),
                event(
                    "e2", "user_001", EventType.PAGE_VIEW,
                    "2026-11-19T09:05:00Z"
                ),
                event(
                    "e3", "user_001", EventType.ACTION,
                    "2026-11-19T09:15:00Z"
                ),
                event(
                    "e4", "user_001", EventType.LOGIN,
                    "2026-11-19T11:00:00Z"
                ),
                event(
                    "e5", "user_002", EventType.LOGIN,
                    "2026-11-19T10:00:00Z"
                ),
                event(
                    "e6", "user_002", EventType.PURCHASE,
                    "2026-11-19T10:10:00Z"
                ),
                event(
                    "e7", "user_003", EventType.PAGE_VIEW,
                    "2026-11-18T12:00:00Z"
                ),
                event(
                    "e8", "user_003", EventType.ACTION,
                    "2026-11-17T12:00:00Z"
                ),
                event(
                    "e9", "user_004", EventType.LOGIN,
                    "2026-11-01T08:00:00Z"
                ),
                event(
                    "e10", "user_005", EventType.LOGOUT,
                    "2026-11-19T12:00:00Z"
                )
            );

            for (EngagementEvent event : sample) {
                repository.save(event);
            }

            System.out.println(
                "Stored events: " + repository.size()
            );

            try {
                repository.save(sample.get(0));
            } catch (DuplicateEventException exception) {
                System.out.println(
                    "Duplicate protection: " + exception.getMessage()
                );
            }

            EngagementService service =
                new EngagementService(repository, policy);

            EngagementReport report = service.calculate(
                LocalDate.of(2026, 11, 19)
            );

            printReport(report);

            System.out.println("\nSESSION FREQUENCY DISTRIBUTION");

            service.frequencyDistribution(
                LocalDate.of(2026, 11, 19)
            ).forEach((sessions, users) ->
                System.out.println(
                    sessions + " sessions: " + users + " users"
                )
            );

            if (
                report.dau() != 2 ||
                report.wau() != 3 ||
                report.mau() != 4 ||
                Math.abs(report.stickiness() - 50.0) > 0.001
            ) {
                throw new IllegalStateException(
                    "Engagement validation failed."
                );
            }

            System.out.println("\nAll enterprise checks passed.");

        } catch (RuntimeException exception) {
            System.err.println(
                "Enterprise analytics error: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
