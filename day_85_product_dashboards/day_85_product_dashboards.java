import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Enterprise Product Dashboard Governance System
 *
 * Java 17
 *
 * Domain-oriented implementation:
 * - Immutable metric definitions
 * - KPI ownership and hierarchy
 * - Observation validation
 * - Aggregation services
 * - Dashboard configuration
 * - Access-control policies
 * - Alert lifecycle
 * - Reporting snapshots
 * - Service-level failure handling
 */

public class ProductDashboard {

    enum MetricCategory {
        NORTH_STAR,
        BUSINESS,
        PRODUCT,
        ENGAGEMENT,
        RELIABILITY
    }

    enum MetricType {
        COUNT,
        PERCENTAGE,
        CURRENCY,
        DURATION,
        RATIO
    }

    enum Aggregation {
        SUM,
        AVERAGE,
        MINIMUM,
        MAXIMUM,
        LAST
    }

    enum Severity {
        WARNING,
        CRITICAL
    }

    enum Role {
        VIEWER(1),
        ANALYST(2),
        ADMIN(3);

        private final int level;

        Role(int level) {
            this.level = level;
        }

        public int level() {
            return level;
        }
    }

    enum AlertState {
        ACTIVE,
        ACKNOWLEDGED,
        RESOLVED
    }

    static class DashboardException extends RuntimeException {
        DashboardException(String message) {
            super(message);
        }
    }

    static class ValidationException extends DashboardException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class AuthorizationException extends DashboardException {
        AuthorizationException(String message) {
            super(message);
        }
    }

    record MetricDefinition(
        String name,
        String description,
        MetricCategory category,
        MetricType type,
        String unit,
        Aggregation aggregation,
        boolean higherIsBetter,
        Double target,
        Double warningThreshold,
        Double criticalThreshold
    ) {
        MetricDefinition {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Metric name is required."
                );
            }

            if (description == null || description.isBlank()) {
                throw new ValidationException(
                    "Metric description is required."
                );
            }

            Objects.requireNonNull(category);
            Objects.requireNonNull(type);
            Objects.requireNonNull(aggregation);

            if (unit == null || unit.isBlank()) {
                throw new ValidationException(
                    "Metric unit is required."
                );
            }

            validateOptional(target, "target");
            validateOptional(warningThreshold, "warning threshold");
            validateOptional(criticalThreshold, "critical threshold");

            if (type == MetricType.PERCENTAGE && !unit.equals("%")) {
                throw new ValidationException(
                    "Percentage metrics must use %."
                );
            }
        }

        private static void validateOptional(
            Double value,
            String name
        ) {
            if (value != null && !Double.isFinite(value)) {
                throw new ValidationException(
                    name + " must be finite."
                );
            }
        }

        void validateValue(double value) {
            if (!Double.isFinite(value)) {
                throw new ValidationException(
                    "Metric value must be finite."
                );
            }

            if (type == MetricType.PERCENTAGE &&
                (value < 0 || value > 100)) {
                throw new ValidationException(
                    name + " must be between 0 and 100."
                );
            }

            if ((type == MetricType.COUNT ||
                 type == MetricType.DURATION) && value < 0) {
                throw new ValidationException(
                    name + " cannot be negative."
                );
            }
        }
    }

    record Observation(
        String metricName,
        double value,
        Instant timestamp,
        Map<String, String> dimensions,
        String entityId
    ) {
        Observation {
            if (metricName == null || metricName.isBlank()) {
                throw new ValidationException(
                    "Metric name is required."
                );
            }

            Objects.requireNonNull(timestamp);

            if (!Double.isFinite(value)) {
                throw new ValidationException(
                    "Observation value must be finite."
                );
            }

            dimensions = Map.copyOf(dimensions);

            if (dimensions.entrySet().stream().anyMatch(
                entry -> entry.getKey().isBlank() ||
                         entry.getValue().isBlank()
            )) {
                throw new ValidationException(
                    "Dimension keys and values cannot be empty."
                );
            }
        }
    }

    record DashboardConfig(
        String id,
        String title,
        List<String> metricNames,
        Duration refreshInterval,
        Map<String, Role> permissions
    ) {
        DashboardConfig {
            if (id == null || id.isBlank() ||
                title == null || title.isBlank()) {
                throw new ValidationException(
                    "Dashboard ID and title are required."
                );
            }

            if (metricNames == null || metricNames.isEmpty()) {
                throw new ValidationException(
                    "Dashboard must contain metrics."
                );
            }

            metricNames = List.copyOf(metricNames);
            refreshInterval = Objects.requireNonNull(
                refreshInterval
            );

            if (refreshInterval.compareTo(
                Duration.ofSeconds(5)
            ) < 0) {
                throw new ValidationException(
                    "Refresh interval must be at least five seconds."
                );
            }

            permissions = Map.copyOf(permissions);
        }
    }

    record Alert(
        UUID id,
        String metricName,
        Severity severity,
        double observedValue,
        Instant timestamp,
        AlertState state
    ) {
        Alert withState(AlertState newState) {
            return new Alert(
                id,
                metricName,
                severity,
                observedValue,
                timestamp,
                newState
            );
        }
    }

    record MetricResult(
        Double currentValue,
        Double previousValue,
        Double changePercentage,
        String unit,
        String category,
        int sampleCount,
        Double target,
        Alert alert
    ) {}

    record DashboardSnapshot(
        String dashboardId,
        String title,
        Instant generatedAt,
        Instant periodStart,
        Instant periodEnd,
        Map<String, MetricResult> metrics,
        List<Alert> alerts
    ) {
        DashboardSnapshot {
            metrics = Map.copyOf(metrics);
            alerts = List.copyOf(alerts);
        }
    }

    static class MetricRegistry {
        private final Map<String, MetricDefinition> definitions =
            new HashMap<>();

        void register(MetricDefinition definition) {
            Objects.requireNonNull(definition);

            if (definitions.putIfAbsent(
                definition.name(),
                definition
            ) != null) {
                throw new ValidationException(
                    "Duplicate metric: " + definition.name()
                );
            }
        }

        MetricDefinition get(String name) {
            MetricDefinition definition = definitions.get(name);

            if (definition == null) {
                throw new ValidationException(
                    "Unknown metric: " + name
                );
            }

            return definition;
        }

        List<MetricDefinition> all() {
            return List.copyOf(definitions.values());
        }
    }

    static class ObservationRepository {
        private final MetricRegistry registry;
        private final List<Observation> observations =
            new ArrayList<>();

        ObservationRepository(MetricRegistry registry) {
            this.registry = registry;
        }

        void insert(Observation observation) {
            MetricDefinition definition =
                registry.get(observation.metricName());

            definition.validateValue(observation.value());

            observations.add(observation);
        }

        List<Observation> query(
            String metricName,
            Instant start,
            Instant end,
            Map<String, String> dimensions
        ) {
            registry.get(metricName);

            if (!start.isBefore(end)) {
                throw new ValidationException(
                    "Invalid observation time window."
                );
            }

            return observations.stream()
                .filter(item ->
                    item.metricName().equals(metricName)
                )
                .filter(item ->
                    !item.timestamp().isBefore(start) &&
                    item.timestamp().isBefore(end)
                )
                .filter(item ->
                    dimensions.entrySet().stream().allMatch(
                        required ->
                            Objects.equals(
                                item.dimensions().get(required.getKey()),
                                required.getValue()
                            )
                    )
                )
                .sorted(Comparator.comparing(
                    Observation::timestamp
                ))
                .toList();
        }
    }

    static class AggregationService {

        Optional<Double> aggregate(
            List<Observation> observations,
            Aggregation method
        ) {
            if (observations.isEmpty()) {
                return Optional.empty();
            }

            List<Double> values = observations.stream()
                .map(Observation::value)
                .toList();

            return switch (method) {
                case SUM -> Optional.of(
                    values.stream().mapToDouble(
                        Double::doubleValue
                    ).sum()
                );

                case AVERAGE -> Optional.of(
                    values.stream().mapToDouble(
                        Double::doubleValue
                    ).average().orElseThrow()
                );

                case MINIMUM -> Optional.of(
                    values.stream().mapToDouble(
                        Double::doubleValue
                    ).min().orElseThrow()
                );

                case MAXIMUM -> Optional.of(
                    values.stream().mapToDouble(
                        Double::doubleValue
                    ).max().orElseThrow()
                );

                case LAST -> observations.stream()
                    .max(Comparator.comparing(
                        Observation::timestamp
                    ))
                    .map(Observation::value);
            };
        }
    }

    static class AccessPolicy {

        void authorize(
            DashboardConfig config,
            String username,
            Role requiredRole
        ) {
            Role actualRole = config.permissions().get(username);

            if (actualRole == null ||
                actualRole.level() < requiredRole.level()) {
                throw new AuthorizationException(
                    "Insufficient access for " + username
                );
            }
        }
    }

    static class AlertService {
        private final Map<String, Alert> activeAlerts =
            new HashMap<>();

        Optional<Alert> evaluate(
            MetricDefinition definition,
            double value,
            Instant timestamp
        ) {
            definition.validateValue(value);

            Severity severity = null;

            if (definition.higherIsBetter()) {
                if (definition.criticalThreshold() != null &&
                    value < definition.criticalThreshold()) {
                    severity = Severity.CRITICAL;
                } else if (
                    definition.warningThreshold() != null &&
                    value < definition.warningThreshold()
                ) {
                    severity = Severity.WARNING;
                }
            } else {
                if (definition.criticalThreshold() != null &&
                    value > definition.criticalThreshold()) {
                    severity = Severity.CRITICAL;
                } else if (
                    definition.warningThreshold() != null &&
                    value > definition.warningThreshold()
                ) {
                    severity = Severity.WARNING;
                }
            }

            if (severity == null) {
                resolveMetric(definition.name());
                return Optional.empty();
            }

            String key = definition.name() + ":" + severity;

            if (activeAlerts.containsKey(key)) {
                return Optional.empty();
            }

            Alert alert = new Alert(
                UUID.randomUUID(),
                definition.name(),
                severity,
                value,
                timestamp,
                AlertState.ACTIVE
            );

            activeAlerts.put(key, alert);

            return Optional.of(alert);
        }

        void acknowledge(String metricName) {
            activeAlerts.replaceAll((key, alert) ->
                alert.metricName().equals(metricName)
                    ? alert.withState(AlertState.ACKNOWLEDGED)
                    : alert
            );

            activeAlerts.entrySet().removeIf(
                entry -> entry.getValue().state()
                    == AlertState.ACKNOWLEDGED
            );
        }

        void resolveMetric(String metricName) {
            activeAlerts.entrySet().removeIf(
                entry -> entry.getValue().metricName()
                    .equals(metricName)
            );
        }

        List<Alert> activeAlerts() {
            return List.copyOf(activeAlerts.values());
        }
    }

    static class DashboardService {
        private final MetricRegistry registry;
        private final ObservationRepository repository;
        private final AggregationService aggregator;
        private final AlertService alertService;
        private final AccessPolicy accessPolicy;

        DashboardService(
            MetricRegistry registry,
            ObservationRepository repository,
            AggregationService aggregator,
            AlertService alertService,
            AccessPolicy accessPolicy
        ) {
            this.registry = registry;
            this.repository = repository;
            this.aggregator = aggregator;
            this.alertService = alertService;
            this.accessPolicy = accessPolicy;
        }

        DashboardSnapshot build(
            DashboardConfig config,
            String username,
            Instant start,
            Instant end
        ) {
            accessPolicy.authorize(
                config,
                username,
                Role.VIEWER
            );

            if (!start.isBefore(end)) {
                throw new ValidationException(
                    "Dashboard start must precede end."
                );
            }

            Duration duration = Duration.between(start, end);
            Instant previousStart = start.minus(duration);

            Map<String, MetricResult> results =
                new HashMap<>();

            for (String metricName : config.metricNames()) {
                MetricDefinition definition =
                    registry.get(metricName);

                List<Observation> currentObservations =
                    repository.query(
                        metricName,
                        start,
                        end,
                        Map.of()
                    );

                List<Observation> previousObservations =
                    repository.query(
                        metricName,
                        previousStart,
                        start,
                        Map.of()
                    );

                Double current = aggregator.aggregate(
                    currentObservations,
                    definition.aggregation()
                ).orElse(null);

                Double previous = aggregator.aggregate(
                    previousObservations,
                    definition.aggregation()
                ).orElse(null);

                Double change = null;

                if (current != null &&
                    previous != null &&
                    previous != 0) {

                    change = (
                        (current - previous) /
                        Math.abs(previous)
                    ) * 100.0;
                }

                Alert alert = current == null
                    ? null
                    : alertService.evaluate(
                        definition,
                        current,
                        end
                    ).orElse(null);

                results.put(
                    metricName,
                    new MetricResult(
                        current,
                        previous,
                        change,
                        definition.unit(),
                        definition.category().name(),
                        currentObservations.size(),
                        definition.target(),
                        alert
                    )
                );
            }

            return new DashboardSnapshot(
                config.id(),
                config.title(),
                Instant.now(),
                start,
                end,
                results,
                alertService.activeAlerts()
            );
        }
    }

    private static MetricDefinition metric(
        String name,
        String description,
        MetricCategory category,
        MetricType type,
        String unit,
        Aggregation aggregation,
        boolean higherIsBetter,
        Double target,
        Double warning,
        Double critical
    ) {
        return new MetricDefinition(
            name,
            description,
            category,
            type,
            unit,
            aggregation,
            higherIsBetter,
            target,
            warning,
            critical
        );
    }

    private static void printSnapshot(
        DashboardSnapshot snapshot
    ) {
        System.out.println("\n" + snapshot.title());
        System.out.println("=".repeat(85));

        System.out.printf(
            "%-30s %-12s %-10s %-12s %-12s%n",
            "METRIC",
            "CURRENT",
            "UNIT",
            "CHANGE %",
            "STATUS"
        );

        snapshot.metrics().forEach((name, result) -> {
            String current = result.currentValue() == null
                ? "NO DATA"
                : String.format("%.2f", result.currentValue());

            String change = result.changePercentage() == null
                ? "N/A"
                : String.format(
                    "%.2f",
                    result.changePercentage()
                );

            String status = result.alert() == null
                ? "NORMAL"
                : result.alert().severity().name();

            System.out.printf(
                "%-30s %-12s %-10s %-12s %-12s%n",
                name,
                current,
                result.unit(),
                change,
                status
            );
        });
    }

    public static void main(String[] args) {
        try {
            MetricRegistry registry = new MetricRegistry();

            registry.register(metric(
                "monthly_active_users",
                "Monthly active users",
                MetricCategory.NORTH_STAR,
                MetricType.COUNT,
                "users",
                Aggregation.LAST,
                true,
                50000.0,
                40000.0,
                30000.0
            ));

            registry.register(metric(
                "conversion_rate",
                "Visitor-to-customer conversion rate",
                MetricCategory.BUSINESS,
                MetricType.PERCENTAGE,
                "%",
                Aggregation.AVERAGE,
                true,
                5.0,
                3.5,
                2.0
            ));

            registry.register(metric(
                "daily_revenue",
                "Recognized daily revenue",
                MetricCategory.BUSINESS,
                MetricType.CURRENCY,
                "INR",
                Aggregation.SUM,
                true,
                500000.0,
                null,
                null
            ));

            registry.register(metric(
                "crash_rate",
                "Application crash rate",
                MetricCategory.RELIABILITY,
                MetricType.PERCENTAGE,
                "%",
                Aggregation.AVERAGE,
                false,
                0.5,
                1.0,
                2.0
            ));

            ObservationRepository repository =
                new ObservationRepository(registry);

            Instant now = Instant.now();

            List<Observation> sample = List.of(
                new Observation(
                    "monthly_active_users",
                    35000,
                    now.minusSeconds(86400),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "monthly_active_users",
                    38000,
                    now.minusSeconds(100),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "conversion_rate",
                    4.1,
                    now.minusSeconds(86400),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "conversion_rate",
                    3.2,
                    now.minusSeconds(100),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "daily_revenue",
                    420000,
                    now.minusSeconds(86400),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "daily_revenue",
                    390000,
                    now.minusSeconds(100),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "crash_rate",
                    0.7,
                    now.minusSeconds(86400),
                    Map.of("platform", "all"),
                    null
                ),
                new Observation(
                    "crash_rate",
                    2.4,
                    now.minusSeconds(100),
                    Map.of("platform", "all"),
                    null
                )
            );

            sample.forEach(repository::insert);

            DashboardConfig config = new DashboardConfig(
                "executive-product-dashboard",
                "Product Performance Dashboard",
                registry.all().stream()
                    .map(MetricDefinition::name)
                    .toList(),
                Duration.ofSeconds(60),
                Map.of(
                    "administrator", Role.ADMIN,
                    "analyst", Role.ANALYST,
                    "executive", Role.VIEWER
                )
            );

            DashboardService service = new DashboardService(
                registry,
                repository,
                new AggregationService(),
                new AlertService(),
                new AccessPolicy()
            );

            DashboardSnapshot snapshot = service.build(
                config,
                "administrator",
                now.minusSeconds(86400),
                now.plusSeconds(1)
            );

            printSnapshot(snapshot);

            System.out.println("\nACTIVE ALERTS");

            snapshot.alerts().forEach(alert ->
                System.out.println(
                    alert.metricName() + " | " +
                    alert.severity() + " | " +
                    alert.observedValue()
                )
            );

            System.out.println("\nVALIDATION TEST");

            try {
                registry.get("unknown_metric");
            } catch (DashboardException exception) {
                System.out.println(exception.getMessage());
            }

            System.out.println("\nAUTHORIZATION TEST");

            try {
                service.build(
                    config,
                    "unauthorized_user",
                    now.minusSeconds(86400),
                    now.plusSeconds(1)
                );
            } catch (AuthorizationException exception) {
                System.out.println(exception.getMessage());
            }

        } catch (DashboardException exception) {
            System.err.println(
                "Dashboard execution failed: " +
                exception.getMessage()
            );

            System.exit(1);
        }
    }
}
