import java.util.*;
import java.util.stream.Collectors;

/*
 * ENTERPRISE PRODUCT ROADMAP GOVERNANCE
 *
 * Java 17 implementation featuring:
 * - Explicit roadmap domain types.
 * - Feature delivery planning.
 * - Outcome and KPI management.
 * - Strategic theme alignment.
 * - Now-Next-Later planning.
 * - Dependency graph validation.
 * - Policy-driven prioritization.
 * - Controlled lifecycle transitions.
 * - Immutable reporting records.
 * - Enterprise validation and exception handling.
 */

public class RoadmapManagement {

    enum RoadmapType {
        FEATURE,
        OUTCOME,
        THEME,
        NOW_NEXT_LATER
    }

    enum Status {
        PROPOSED,
        PLANNED,
        IN_PROGRESS,
        BLOCKED,
        COMPLETED,
        CANCELLED
    }

    enum Priority {
        CRITICAL(1),
        HIGH(2),
        MEDIUM(3),
        LOW(4);

        private final int rank;

        Priority(int rank) {
            this.rank = rank;
        }

        int rank() {
            return rank;
        }
    }

    enum Horizon {
        NOW,
        NEXT,
        LATER
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

    static class DependencyException extends RoadmapException {
        DependencyException(String message) {
            super(message);
        }
    }

    record Metric(
        String name,
        double baseline,
        double target,
        double current,
        String unit
    ) {
        Metric {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Metric name is required."
                );
            }

            if (
                baseline < 0 ||
                target < 0 ||
                current < 0
            ) {
                throw new ValidationException(
                    "Metric values cannot be negative."
                );
            }

            Objects.requireNonNull(unit);
        }

        double progress() {
            double difference = target - baseline;

            if (difference == 0) {
                return current == target ? 100 : 0;
            }

            return Math.max(
                0,
                Math.min(
                    100,
                    ((current - baseline) / difference) * 100
                )
            );
        }

        Metric withCurrent(double value) {
            return new Metric(
                name,
                baseline,
                target,
                value,
                unit
            );
        }
    }

    record Theme(
        String id,
        String name,
        String objective,
        String owner
    ) {
        Theme {
            Objects.requireNonNull(id);
            Objects.requireNonNull(name);
            Objects.requireNonNull(objective);

            if (
                id.isBlank() ||
                name.isBlank() ||
                objective.isBlank()
            ) {
                throw new ValidationException(
                    "Theme fields cannot be empty."
                );
            }
        }
    }

    record RoadmapItem(
        String id,
        String title,
        String description,
        String owner,
        RoadmapType type,
        Priority priority,
        Status status,
        Optional<Horizon> horizon,
        Optional<String> themeId,
        Optional<Metric> metric,
        Set<String> dependencies,
        Set<String> tags,
        double progress,
        double confidence,
        long version
    ) {
        RoadmapItem {
            Objects.requireNonNull(id);
            Objects.requireNonNull(title);
            Objects.requireNonNull(owner);
            Objects.requireNonNull(type);
            Objects.requireNonNull(priority);
            Objects.requireNonNull(status);

            horizon = Objects.requireNonNull(horizon);
            themeId = Objects.requireNonNull(themeId);
            metric = Objects.requireNonNull(metric);

            dependencies = Set.copyOf(dependencies);
            tags = Set.copyOf(tags);

            if (
                id.isBlank() ||
                title.isBlank() ||
                owner.isBlank()
            ) {
                throw new ValidationException(
                    "Item identity, title, and owner are required."
                );
            }

            if (progress < 0 || progress > 100) {
                throw new ValidationException(
                    "Progress must be between 0 and 100."
                );
            }

            if (confidence < 0 || confidence > 1) {
                throw new ValidationException(
                    "Confidence must be between 0 and 1."
                );
            }

            if (
                type == RoadmapType.OUTCOME &&
                metric.isEmpty()
            ) {
                throw new ValidationException(
                    "Outcome items require a metric."
                );
            }

            if (
                type == RoadmapType.NOW_NEXT_LATER &&
                horizon.isEmpty()
            ) {
                throw new ValidationException(
                    "Horizon items require a planning horizon."
                );
            }

            if (dependencies.contains(id)) {
                throw new DependencyException(
                    "Self-dependency is prohibited."
                );
            }
        }

        RoadmapItem withStatus(Status next) {
            return new RoadmapItem(
                id,
                title,
                description,
                owner,
                type,
                priority,
                next,
                horizon,
                themeId,
                metric,
                dependencies,
                tags,
                next == Status.COMPLETED ? 100 : progress,
                confidence,
                version + 1
            );
        }

        RoadmapItem withMetric(Metric nextMetric) {
            return new RoadmapItem(
                id,
                title,
                description,
                owner,
                type,
                priority,
                status,
                horizon,
                themeId,
                Optional.of(nextMetric),
                dependencies,
                tags,
                progress,
                confidence,
                version + 1
            );
        }

        RoadmapItem withHorizon(Horizon next) {
            return new RoadmapItem(
                id,
                title,
                description,
                owner,
                type,
                priority,
                status,
                Optional.of(next),
                themeId,
                metric,
                dependencies,
                tags,
                progress,
                confidence,
                version + 1
            );
        }
    }

    record RoadmapReport(
        String name,
        RoadmapType type,
        int total,
        int completed,
        double completionPercentage,
        Map<Status, Long> statusCounts
    ) {}

    interface PrioritizationPolicy {
        double score(RoadmapItem item);
    }

    static class WeightedPrioritizationPolicy
        implements PrioritizationPolicy {

        @Override
        public double score(RoadmapItem item) {
            double priorityWeight =
                5.0 - item.priority().rank();

            return priorityWeight *
                item.confidence();
        }
    }

    static class RoadmapService {

        private final String name;
        private final RoadmapType type;

        private final Map<String, RoadmapItem> items =
            new LinkedHashMap<>();

        private final Map<String, Theme> themes =
            new LinkedHashMap<>();

        private final PrioritizationPolicy policy;

        RoadmapService(
            String name,
            RoadmapType type,
            PrioritizationPolicy policy
        ) {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Roadmap name is required."
                );
            }

            this.name = name;
            this.type = Objects.requireNonNull(type);
            this.policy = Objects.requireNonNull(policy);
        }

        public void addTheme(Theme theme) {
            if (themes.containsKey(theme.id())) {
                throw new ValidationException(
                    "Duplicate theme identifier."
                );
            }

            themes.put(theme.id(), theme);
        }

        public void addItem(RoadmapItem item) {
            if (item.type() != type) {
                throw new ValidationException(
                    "Roadmap type mismatch."
                );
            }

            if (items.containsKey(item.id())) {
                throw new ValidationException(
                    "Duplicate roadmap item."
                );
            }

            if (
                item.themeId().isPresent() &&
                !themes.containsKey(item.themeId().get())
            ) {
                throw new ValidationException(
                    "Referenced theme does not exist."
                );
            }

            for (String dependency : item.dependencies()) {
                if (!items.containsKey(dependency)) {
                    throw new DependencyException(
                        "Unknown dependency: " + dependency
                    );
                }
            }

            items.put(item.id(), item);

            try {
                validateDependencyGraph();
            } catch (RuntimeException error) {
                items.remove(item.id());
                throw error;
            }
        }

        private void validateDependencyGraph() {
            Map<String, Integer> states = new HashMap<>();

            for (String id : items.keySet()) {
                visit(id, states);
            }
        }

        private void visit(
            String id,
            Map<String, Integer> states
        ) {
            int state = states.getOrDefault(id, 0);

            if (state == 1) {
                throw new DependencyException(
                    "Circular dependency detected."
                );
            }

            if (state == 2) {
                return;
            }

            states.put(id, 1);

            RoadmapItem item = items.get(id);

            for (String dependency : item.dependencies()) {
                if (!items.containsKey(dependency)) {
                    throw new DependencyException(
                        "Missing dependency."
                    );
                }

                visit(dependency, states);
            }

            states.put(id, 2);
        }

        private RoadmapItem requireItem(String id) {
            RoadmapItem item = items.get(id);

            if (item == null) {
                throw new ValidationException(
                    "Roadmap item does not exist: " + id
                );
            }

            return item;
        }

        public void updateStatus(
            String id,
            Status nextStatus,
            long expectedVersion
        ) {
            RoadmapItem item = requireItem(id);

            if (item.version() != expectedVersion) {
                throw new RoadmapException(
                    "Concurrent modification detected."
                );
            }

            if (
                item.status() == Status.COMPLETED ||
                item.status() == Status.CANCELLED
            ) {
                throw new RoadmapException(
                    "Terminal items cannot be modified."
                );
            }

            if (nextStatus == Status.IN_PROGRESS) {
                for (String dependency : item.dependencies()) {
                    if (
                        requireItem(dependency).status() !=
                        Status.COMPLETED
                    ) {
                        throw new DependencyException(
                            "Dependencies must be completed."
                        );
                    }
                }
            }

            items.put(id, item.withStatus(nextStatus));
        }

        public void updateMetric(
            String id,
            double current
        ) {
            RoadmapItem item = requireItem(id);

            Metric metric = item.metric().orElseThrow(
                () -> new ValidationException(
                    "Outcome metric is missing."
                )
            );

            items.put(
                id,
                item.withMetric(metric.withCurrent(current))
            );
        }

        public void moveHorizon(
            String id,
            Horizon nextHorizon
        ) {
            RoadmapItem item = requireItem(id);

            if (type != RoadmapType.NOW_NEXT_LATER) {
                throw new ValidationException(
                    "This is not a horizon roadmap."
                );
            }

            items.put(
                id,
                item.withHorizon(nextHorizon)
            );
        }

        public List<RoadmapItem> prioritizedItems() {
            return items.values()
                .stream()
                .sorted(
                    Comparator.comparingDouble(
                        policy::score
                    ).reversed()
                )
                .toList();
        }

        public RoadmapReport report() {
            Map<Status, Long> counts =
                Arrays.stream(Status.values())
                    .collect(
                        Collectors.toMap(
                            status -> status,
                            status -> items.values()
                                .stream()
                                .filter(
                                    item -> item.status() == status
                                )
                                .count()
                        )
                    );

            int completed = counts.get(Status.COMPLETED);
            int total = items.size();

            double percentage = total == 0
                ? 0
                : completed * 100.0 / total;

            return new RoadmapReport(
                name,
                type,
                total,
                completed,
                percentage,
                Map.copyOf(counts)
            );
        }

        public Map<Horizon, List<String>> horizonReport() {
            Map<Horizon, List<String>> report =
                new EnumMap<>(Horizon.class);

            for (Horizon horizon : Horizon.values()) {
                report.put(horizon, new ArrayList<>());
            }

            for (RoadmapItem item : items.values()) {
                item.horizon().ifPresent(
                    horizon -> report.get(horizon).add(
                        item.title()
                    )
                );
            }

            return report.entrySet()
                .stream()
                .collect(
                    Collectors.toUnmodifiableMap(
                        Map.Entry::getKey,
                        entry -> List.copyOf(entry.getValue())
                    )
                );
        }

        public List<Metric> outcomeMetrics() {
            return items.values()
                .stream()
                .flatMap(item -> item.metric().stream())
                .toList();
        }

        public int size() {
            return items.size();
        }
    }

    static RoadmapItem createItem(
        String id,
        String title,
        String owner,
        RoadmapType type,
        Priority priority,
        Set<String> dependencies,
        Optional<Horizon> horizon,
        Optional<String> themeId,
        Optional<Metric> metric
    ) {
        return new RoadmapItem(
            id,
            title,
            "Enterprise roadmap delivery item",
            owner,
            type,
            priority,
            Status.PROPOSED,
            horizon,
            themeId,
            metric,
            dependencies,
            Set.of(),
            0,
            0.85,
            1
        );
    }

    static void runTests() {
        PrioritizationPolicy policy =
            new WeightedPrioritizationPolicy();

        RoadmapService service = new RoadmapService(
            "Test Roadmap",
            RoadmapType.FEATURE,
            policy
        );

        RoadmapItem first = createItem(
            "F1",
            "Authentication",
            "Security",
            RoadmapType.FEATURE,
            Priority.CRITICAL,
            Set.of(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty()
        );

        RoadmapItem second = createItem(
            "F2",
            "Analytics",
            "Product",
            RoadmapType.FEATURE,
            Priority.HIGH,
            Set.of("F1"),
            Optional.empty(),
            Optional.empty(),
            Optional.empty()
        );

        service.addItem(first);
        service.addItem(second);

        service.updateStatus("F1", Status.COMPLETED, 1);
        service.updateStatus("F2", Status.IN_PROGRESS, 1);

        if (service.size() != 2) {
            throw new AssertionError("Item count failed.");
        }

        if (service.report().completed() != 1) {
            throw new AssertionError("Completion failed.");
        }

        RoadmapService invalid = new RoadmapService(
            "Invalid",
            RoadmapType.FEATURE,
            policy
        );

        try {
            invalid.addItem(createItem(
                "X1",
                "Invalid dependency",
                "Engineering",
                RoadmapType.FEATURE,
                Priority.HIGH,
                Set.of("UNKNOWN"),
                Optional.empty(),
                Optional.empty(),
                Optional.empty()
            ));

            throw new AssertionError(
                "Missing dependency accepted."
            );
        } catch (DependencyException expected) {
            // Expected failure.
        }

        System.out.println("Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            PrioritizationPolicy policy =
                new WeightedPrioritizationPolicy();

            RoadmapService features = new RoadmapService(
                "Customer Platform",
                RoadmapType.FEATURE,
                policy
            );

            features.addItem(createItem(
                "F001",
                "Multi-factor authentication",
                "Security",
                RoadmapType.FEATURE,
                Priority.CRITICAL,
                Set.of(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty()
            ));

            features.addItem(createItem(
                "F002",
                "Customer analytics",
                "Product",
                RoadmapType.FEATURE,
                Priority.HIGH,
                Set.of("F001"),
                Optional.empty(),
                Optional.empty(),
                Optional.empty()
            ));

            features.updateStatus(
                "F001",
                Status.COMPLETED,
                1
            );

            features.updateStatus(
                "F002",
                Status.IN_PROGRESS,
                1
            );

            System.out.println("FEATURE ROADMAP");
            System.out.println(features.report());

            RoadmapService outcomes = new RoadmapService(
                "Customer Experience",
                RoadmapType.OUTCOME,
                policy
            );

            outcomes.addItem(createItem(
                "O001",
                "Reduce onboarding time",
                "Operations",
                RoadmapType.OUTCOME,
                Priority.HIGH,
                Set.of(),
                Optional.empty(),
                Optional.empty(),
                Optional.of(new Metric(
                    "Onboarding duration",
                    10,
                    4,
                    7,
                    "days"
                ))
            ));

            outcomes.updateMetric("O001", 5);

            System.out.println("\nOUTCOME ROADMAP");

            for (Metric metric : outcomes.outcomeMetrics()) {
                System.out.println(
                    metric.name() +
                    ": " +
                    metric.progress() +
                    "% progress"
                );
            }

            RoadmapService themes = new RoadmapService(
                "Strategic Investment",
                RoadmapType.THEME,
                policy
            );

            themes.addTheme(new Theme(
                "T001",
                "Trust and Security",
                "Improve platform security",
                "Technology Office"
            ));

            themes.addItem(createItem(
                "TITEM001",
                "Centralized audit logging",
                "Platform Engineering",
                RoadmapType.THEME,
                Priority.HIGH,
                Set.of(),
                Optional.empty(),
                Optional.of("T001"),
                Optional.empty()
            ));

            System.out.println("\nTHEME ROADMAP");
            System.out.println(themes.report());

            RoadmapService horizons = new RoadmapService(
                "Product Investment Horizons",
                RoadmapType.NOW_NEXT_LATER,
                policy
            );

            horizons.addItem(createItem(
                "H001",
                "Resolve payment errors",
                "Payments",
                RoadmapType.NOW_NEXT_LATER,
                Priority.CRITICAL,
                Set.of(),
                Optional.of(Horizon.NOW),
                Optional.empty(),
                Optional.empty()
            ));

            horizons.addItem(createItem(
                "H002",
                "Improve reporting",
                "Analytics",
                RoadmapType.NOW_NEXT_LATER,
                Priority.HIGH,
                Set.of(),
                Optional.of(Horizon.NEXT),
                Optional.empty(),
                Optional.empty()
            ));

            horizons.addItem(createItem(
                "H003",
                "Predictive planning",
                "Strategy",
                RoadmapType.NOW_NEXT_LATER,
                Priority.MEDIUM,
                Set.of(),
                Optional.of(Horizon.LATER),
                Optional.empty(),
                Optional.empty()
            ));

            System.out.println("\nNOW-NEXT-LATER ROADMAP");
            System.out.println(horizons.horizonReport());

            runTests();

        } catch (RoadmapException error) {
            System.err.println(
                "Roadmap governance error: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
