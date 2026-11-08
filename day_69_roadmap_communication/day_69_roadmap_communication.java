import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Roadmap Communication Enterprise Management System.
 *
 * Java 17.
 *
 * Models:
 * - Executive roadmaps
 * - Engineering roadmaps
 * - Sales roadmaps
 * - Customer roadmaps
 * - Dependencies and milestones
 * - Communication policies
 * - Validation and state transitions
 * - Risk and progress evaluation
 * - Immutable reporting snapshots
 */

public class RoadmapCommunication {

    enum Audience {
        EXECUTIVE,
        ENGINEERING,
        SALES,
        CUSTOMER
    }

    enum Status {
        PLANNED,
        IN_PROGRESS,
        BLOCKED,
        AT_RISK,
        COMPLETED,
        CANCELLED
    }

    enum Priority {
        CRITICAL,
        HIGH,
        MEDIUM,
        LOW
    }

    enum Confidence {
        HIGH,
        MEDIUM,
        LOW
    }

    static class RoadmapException extends RuntimeException {
        RoadmapException(String message) {
            super(message);
        }
    }

    static class ValidationException extends RoadmapException {
        ValidationException(String message) {
            super(message);
        }
    }

    record Milestone(
        String id,
        String name,
        LocalDate targetDate,
        Status status,
        double progress
    ) {
        Milestone {
            requireText(id, "Milestone ID");
            requireText(name, "Milestone name");
            Objects.requireNonNull(targetDate);
            Objects.requireNonNull(status);

            validateProgress(progress);

            if (status == Status.COMPLETED && progress != 100) {
                throw new ValidationException(
                    "Completed milestones must have 100% progress."
                );
            }
        }
    }

    record RoadmapItem(
        String id,
        String title,
        String description,
        String owner,
        String objective,
        String businessValue,
        String engineeringDetails,
        String salesMessage,
        String customerImpact,
        LocalDate startDate,
        LocalDate targetDate,
        Priority priority,
        Status status,
        Confidence confidence,
        double progress,
        String risk,
        Set<String> dependencies,
        List<Milestone> milestones
    ) {
        RoadmapItem {
            requireText(id, "ID");
            requireText(title, "Title");
            requireText(owner, "Owner");
            requireText(objective, "Objective");

            Objects.requireNonNull(startDate);
            Objects.requireNonNull(targetDate);
            Objects.requireNonNull(priority);
            Objects.requireNonNull(status);
            Objects.requireNonNull(confidence);

            if (targetDate.isBefore(startDate)) {
                throw new ValidationException(
                    "Target date cannot precede start date."
                );
            }

            validateProgress(progress);

            if (status == Status.PLANNED && progress > 0) {
                throw new ValidationException(
                    "Planned items cannot have implementation progress."
                );
            }

            if (status == Status.COMPLETED && progress != 100) {
                throw new ValidationException(
                    "Completed items must have 100% progress."
                );
            }

            dependencies = Set.copyOf(
                dependencies == null ? Set.of() : dependencies
            );

            milestones = List.copyOf(
                milestones == null ? List.of() : milestones
            );

            description = description == null ? "" : description;
            businessValue = businessValue == null ? "" : businessValue;
            engineeringDetails = engineeringDetails == null
                ? "" : engineeringDetails;
            salesMessage = salesMessage == null ? "" : salesMessage;
            customerImpact = customerImpact == null
                ? "" : customerImpact;
            risk = risk == null ? "" : risk;
        }

        RoadmapItem withStatus(Status newStatus, double newProgress) {
            return new RoadmapItem(
                id,
                title,
                description,
                owner,
                objective,
                businessValue,
                engineeringDetails,
                salesMessage,
                customerImpact,
                startDate,
                targetDate,
                priority,
                newStatus,
                confidence,
                newStatus == Status.COMPLETED ? 100 : newProgress,
                risk,
                dependencies,
                milestones
            );
        }
    }

    record RoadmapEvent(
        UUID eventId,
        String itemId,
        String eventType,
        long version,
        LocalDate eventDate
    ) {}

    record RoadmapSnapshot(
        String name,
        String owner,
        long version,
        LocalDate generatedDate,
        Map<String, RoadmapItem> items
    ) {
        RoadmapSnapshot {
            items = Collections.unmodifiableMap(
                new HashMap<>(items)
            );
        }
    }

    interface CommunicationPolicy {
        String generate(RoadmapSnapshot snapshot);
    }

    static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new ValidationException(field + " is required.");
        }
    }

    static void validateProgress(double progress) {
        if (!Double.isFinite(progress) ||
            progress < 0 || progress > 100) {
            throw new ValidationException(
                "Progress must be between 0 and 100."
            );
        }
    }

    static class RoadmapRepository {
        private final Map<String, RoadmapItem> items =
            new HashMap<>();

        private final List<RoadmapEvent> events =
            new ArrayList<>();

        private long version = 1;

        public synchronized void add(RoadmapItem item) {
            Objects.requireNonNull(item);

            if (items.containsKey(item.id())) {
                throw new ValidationException(
                    "Duplicate roadmap item: " + item.id()
                );
            }

            items.put(item.id(), item);

            try {
                validateDependencies();
            } catch (RuntimeException exception) {
                items.remove(item.id());
                throw exception;
            }

            record(item.id(), "ITEM_ADDED");
        }

        public synchronized RoadmapItem get(String id) {
            RoadmapItem item = items.get(id);

            if (item == null) {
                throw new RoadmapException(
                    "Roadmap item not found: " + id
                );
            }

            return item;
        }

        public synchronized void updateStatus(
            String id,
            Status newStatus,
            double newProgress
        ) {
            RoadmapItem existing = get(id);

            if (existing.status() == Status.CANCELLED) {
                throw new RoadmapException(
                    "Cancelled items cannot be updated."
                );
            }

            if (existing.status() == Status.COMPLETED &&
                newStatus != Status.COMPLETED) {
                throw new RoadmapException(
                    "Completed items require correction approval."
                );
            }

            validateProgress(newProgress);

            if (newStatus == Status.PLANNED && newProgress > 0) {
                throw new ValidationException(
                    "Planned items cannot have implementation progress."
                );
            }

            RoadmapItem updated = existing.withStatus(
                newStatus,
                newProgress
            );

            items.put(id, updated);
            record(id, "STATUS_UPDATED");
        }

        private void record(String id, String eventType) {
            version++;

            events.add(new RoadmapEvent(
                UUID.randomUUID(),
                id,
                eventType,
                version,
                LocalDate.now()
            ));
        }

        private void validateDependencies() {
            Set<String> visited = new HashSet<>();
            Set<String> active = new HashSet<>();

            for (String id : items.keySet()) {
                visit(id, visited, active);
            }
        }

        private void visit(
            String id,
            Set<String> visited,
            Set<String> active
        ) {
            if (active.contains(id)) {
                throw new ValidationException(
                    "Circular dependency detected."
                );
            }

            if (visited.contains(id)) return;

            RoadmapItem item = get(id);
            active.add(id);

            for (String dependency : item.dependencies()) {
                if (!items.containsKey(dependency)) {
                    throw new ValidationException(
                        "Unknown dependency: " + dependency
                    );
                }

                visit(dependency, visited, active);
            }

            active.remove(id);
            visited.add(id);
        }

        public synchronized boolean dependenciesReady(String id) {
            RoadmapItem item = get(id);

            return item.dependencies().stream()
                .allMatch(dependency ->
                    get(dependency).status() == Status.COMPLETED
                );
        }

        public synchronized double calculateProgress() {
            List<RoadmapItem> activeItems = items.values()
                .stream()
                .filter(item ->
                    item.status() != Status.CANCELLED
                )
                .toList();

            if (activeItems.isEmpty()) return 0;

            return activeItems.stream()
                .mapToDouble(RoadmapItem::progress)
                .average()
                .orElse(0);
        }

        public synchronized List<RoadmapItem> risks() {
            return items.values()
                .stream()
                .filter(item ->
                    item.status() == Status.BLOCKED ||
                    item.status() == Status.AT_RISK ||
                    !item.risk().isBlank()
                )
                .toList();
        }

        public synchronized RoadmapSnapshot snapshot(
            String name,
            String owner
        ) {
            return new RoadmapSnapshot(
                name,
                owner,
                version,
                LocalDate.now(),
                items
            );
        }

        public synchronized List<RoadmapEvent> getEvents() {
            return List.copyOf(events);
        }

        public synchronized int size() {
            return items.size();
        }
    }

    static class ExecutivePolicy implements CommunicationPolicy {

        @Override
        public String generate(RoadmapSnapshot snapshot) {
            StringBuilder report = new StringBuilder();

            report.append("EXECUTIVE ROADMAP: ")
                .append(snapshot.name())
                .append("\n");

            report.append("Owner: ")
                .append(snapshot.owner())
                .append("\n\n");

            double progress = snapshot.items().values()
                .stream()
                .filter(item ->
                    item.status() != Status.CANCELLED
                )
                .mapToDouble(RoadmapItem::progress)
                .average()
                .orElse(0);

            report.append(
                String.format("Portfolio progress: %.1f%%\n\n", progress)
            );

            snapshot.items().values().stream()
                .sorted((a, b) ->
                    a.targetDate().compareTo(b.targetDate())
                )
                .forEach(item -> report
                    .append(item.title()).append('\n')
                    .append("Objective: ")
                    .append(item.objective()).append('\n')
                    .append("Business value: ")
                    .append(item.businessValue()).append('\n')
                    .append("Status: ")
                    .append(item.status()).append('\n')
                    .append("Target: ")
                    .append(item.targetDate()).append('\n')
                    .append("Confidence: ")
                    .append(item.confidence()).append('\n')
                    .append("Risk: ")
                    .append(item.risk().isBlank()
                        ? "None" : item.risk())
                    .append("\n\n")
                );

            return report.toString();
        }
    }

    static class EngineeringPolicy implements CommunicationPolicy {

        @Override
        public String generate(RoadmapSnapshot snapshot) {
            StringBuilder report = new StringBuilder();

            report.append("ENGINEERING DELIVERY ROADMAP\n\n");

            for (RoadmapItem item : snapshot.items().values()) {
                report.append("FEATURE: ")
                    .append(item.title()).append('\n');

                report.append("Owner: ")
                    .append(item.owner()).append('\n');

                report.append("Priority: ")
                    .append(item.priority()).append('\n');

                report.append("Status: ")
                    .append(item.status()).append('\n');

                report.append("Technical scope: ")
                    .append(item.engineeringDetails()).append('\n');

                report.append("Progress: ")
                    .append(item.progress()).append("%\n");

                report.append("Dependencies: ")
                    .append(item.dependencies()).append('\n');

                report.append("Target: ")
                    .append(item.targetDate()).append('\n');

                report.append("Risk: ")
                    .append(item.risk().isBlank()
                        ? "None" : item.risk())
                    .append("\n\n");

                for (Milestone milestone : item.milestones()) {
                    report.append("  Milestone: ")
                        .append(milestone.name())
                        .append(" | ")
                        .append(milestone.status())
                        .append(" | ")
                        .append(milestone.targetDate())
                        .append('\n');
                }
            }

            return report.toString();
        }
    }

    static class SalesPolicy implements CommunicationPolicy {

        @Override
        public String generate(RoadmapSnapshot snapshot) {
            StringBuilder report = new StringBuilder();

            report.append("SALES ENABLEMENT ROADMAP\n\n");

            snapshot.items().values().stream()
                .filter(item ->
                    item.status() != Status.CANCELLED
                )
                .sorted((a, b) ->
                    a.targetDate().compareTo(b.targetDate())
                )
                .forEach(item -> report
                    .append("FEATURE: ")
                    .append(item.title()).append('\n')
                    .append("Customer value: ")
                    .append(item.businessValue()).append('\n')
                    .append("Sales positioning: ")
                    .append(item.salesMessage()).append('\n')
                    .append("Availability: ")
                    .append(item.status()).append('\n')
                    .append("Target: ")
                    .append(item.targetDate()).append('\n')
                    .append("Confidence: ")
                    .append(item.confidence()).append("\n\n")
                );

            report.append(
                "Sales teams must not represent planned features "
                + "as currently available."
            );

            return report.toString();
        }
    }

    static class CustomerPolicy implements CommunicationPolicy {

        @Override
        public String generate(RoadmapSnapshot snapshot) {
            StringBuilder report = new StringBuilder();

            report.append("CUSTOMER PRODUCT ROADMAP\n\n");

            snapshot.items().values().stream()
                .filter(item ->
                    item.status() != Status.CANCELLED &&
                    item.status() != Status.BLOCKED
                )
                .sorted((a, b) ->
                    a.targetDate().compareTo(b.targetDate())
                )
                .forEach(item -> {
                    String publicStatus = switch (item.status()) {
                        case PLANNED -> "Planned";
                        case IN_PROGRESS -> "In development";
                        case AT_RISK -> "Under review";
                        case COMPLETED -> "Completed";
                        default -> "Not currently available";
                    };

                    report.append("FEATURE: ")
                        .append(item.title()).append('\n');

                    report.append("Status: ")
                        .append(publicStatus).append('\n');

                    report.append("Customer impact: ")
                        .append(item.customerImpact().isBlank()
                            ? item.businessValue()
                            : item.customerImpact())
                        .append('\n');

                    report.append("Target: ")
                        .append(item.targetDate())
                        .append("\n\n");
                });

            report.append(
                "Target dates are estimates and are subject to "
                + "product and delivery conditions."
            );

            return report.toString();
        }
    }

    static class CommunicationService {
        private final Map<Audience, CommunicationPolicy> policies =
            new EnumMap<>(Audience.class);

        CommunicationService() {
            policies.put(Audience.EXECUTIVE, new ExecutivePolicy());
            policies.put(Audience.ENGINEERING, new EngineeringPolicy());
            policies.put(Audience.SALES, new SalesPolicy());
            policies.put(Audience.CUSTOMER, new CustomerPolicy());
        }

        public String generate(
            Audience audience,
            RoadmapSnapshot snapshot
        ) {
            CommunicationPolicy policy = policies.get(audience);

            if (policy == null) {
                throw new RoadmapException(
                    "No communication policy configured."
                );
            }

            return policy.generate(snapshot);
        }

        public Map<Audience, String> generateAll(
            RoadmapSnapshot snapshot
        ) {
            Map<Audience, String> reports =
                new EnumMap<>(Audience.class);

            for (Audience audience : Audience.values()) {
                reports.put(
                    audience,
                    generate(audience, snapshot)
                );
            }

            return Collections.unmodifiableMap(reports);
        }
    }

    static RoadmapItem createItem(
        String id,
        String title,
        LocalDate start,
        LocalDate target,
        Status status,
        double progress,
        Set<String> dependencies
    ) {
        return new RoadmapItem(
            id,
            title,
            "Enterprise platform capability.",
            "Platform Engineering",
            "Improve enterprise operations.",
            "Increase business efficiency.",
            "API integration and service development.",
            "Enterprise product capability.",
            "Improved customer experience.",
            start,
            target,
            Priority.HIGH,
            status,
            Confidence.MEDIUM,
            progress,
            "",
            dependencies,
            List.of()
        );
    }

    static void runTests(RoadmapRepository repository) {
        if (repository.size() != 4) {
            throw new RoadmapException("Incorrect item count.");
        }

        if (!repository.dependenciesReady("RM-002")) {
            throw new RoadmapException(
                "Completed dependency should be ready."
            );
        }

        if (repository.dependenciesReady("RM-003")) {
            throw new RoadmapException(
                "Incomplete dependency should not be ready."
            );
        }

        if (Math.abs(repository.calculateProgress() - 43.75) > 0.001) {
            throw new RoadmapException("Incorrect progress.");
        }

        System.out.println("All Java validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            RoadmapRepository repository = new RoadmapRepository();

            RoadmapItem identity = createItem(
                "RM-001",
                "Identity Management",
                LocalDate.of(2026, 10, 1),
                LocalDate.of(2026, 12, 15),
                Status.COMPLETED,
                100,
                Set.of()
            );

            identity = new RoadmapItem(
                identity.id(),
                identity.title(),
                identity.description(),
                identity.owner(),
                identity.objective(),
                identity.businessValue(),
                "OIDC, OAuth 2.0 and role-based access control.",
                "Enterprise identity controls.",
                "Improved account protection.",
                identity.startDate(),
                identity.targetDate(),
                Priority.CRITICAL,
                Status.COMPLETED,
                Confidence.HIGH,
                100,
                "",
                Set.of(),
                List.of(new Milestone(
                    "MS-001",
                    "Authentication service",
                    LocalDate.of(2026, 11, 15),
                    Status.COMPLETED,
                    100
                ))
            );

            repository.add(identity);

            repository.add(createItem(
                "RM-002",
                "Analytics Dashboard",
                LocalDate.of(2026, 11, 1),
                LocalDate.of(2027, 2, 15),
                Status.IN_PROGRESS,
                55,
                Set.of("RM-001")
            ));

            RoadmapItem reporting = createItem(
                "RM-003",
                "Automated Reporting",
                LocalDate.of(2026, 11, 15),
                LocalDate.of(2027, 3, 15),
                Status.AT_RISK,
                20,
                Set.of("RM-002")
            );

            reporting = new RoadmapItem(
                reporting.id(),
                reporting.title(),
                reporting.description(),
                reporting.owner(),
                reporting.objective(),
                reporting.businessValue(),
                reporting.engineeringDetails(),
                "Scheduled business reports.",
                "Consistent reporting.",
                reporting.startDate(),
                reporting.targetDate(),
                Priority.HIGH,
                Status.AT_RISK,
                Confidence.LOW,
                20,
                "Data integration capacity constraints.",
                reporting.dependencies(),
                List.of()
            );

            repository.add(reporting);

            repository.add(createItem(
                "RM-004",
                "Customer Self-Service Portal",
                LocalDate.of(2027, 1, 1),
                LocalDate.of(2027, 4, 30),
                Status.PLANNED,
                0,
                Set.of("RM-001")
            ));

            runTests(repository);

            RoadmapSnapshot snapshot = repository.snapshot(
                "Enterprise Product Platform 2027",
                "Product Management Office"
            );

            CommunicationService communication =
                new CommunicationService();

            System.out.printf(
                "Portfolio progress: %.2f%%%n",
                repository.calculateProgress()
            );

            System.out.println(
                "Roadmap version: " + snapshot.version()
            );

            for (Map.Entry<Audience, String> entry :
                communication.generateAll(snapshot).entrySet()) {

                System.out.println("\n" + "=".repeat(70));
                System.out.println(entry.getKey());
                System.out.println(entry.getValue());
            }

            System.out.println("\nROADMAP EVENT HISTORY");

            repository.getEvents().forEach(System.out::println);

        } catch (RoadmapException exception) {
            System.err.println(
                "Roadmap error: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
