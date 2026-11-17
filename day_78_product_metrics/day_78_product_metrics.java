import java.time.Instant;
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
import java.util.stream.Collectors;

/**
 * PRODUCT METRICS ENTERPRISE MANAGEMENT SYSTEM
 *
 * Java 17 implementation of:
 * - North Star Metric governance
 * - Input and output metric management
 * - Guardrail policies
 * - Immutable domain records
 * - Metric observation processing
 * - Metric dependency validation
 * - Product performance reporting
 * - Experiment analysis
 * - Business rule enforcement
 *
 * Compile:
 * javac ProductMetrics.java
 *
 * Run:
 * java ProductMetrics
 */

public class ProductMetrics {

    enum Category {
        NORTH_STAR,
        INPUT,
        OUTPUT,
        GUARDRAIL
    }

    enum Direction {
        HIGHER,
        LOWER,
        RANGE
    }

    enum Status {
        ON_TRACK,
        BELOW_TARGET,
        ABOVE_LIMIT,
        BELOW_RANGE,
        ABOVE_RANGE,
        MISSING
    }

    enum AlertSeverity {
        WARNING,
        CRITICAL
    }

    static class ProductException extends RuntimeException {
        ProductException(String message) {
            super(message);
        }
    }

    static class ValidationException extends ProductException {
        ValidationException(String message) {
            super(message);
        }
    }

    record MetricDefinition(
        String name,
        Category category,
        String unit,
        Direction direction,
        Double target,
        Double minimum,
        Double maximum,
        String description
    ) {
        MetricDefinition {
            Objects.requireNonNull(name);
            Objects.requireNonNull(category);
            Objects.requireNonNull(unit);
            Objects.requireNonNull(direction);

            if (name.isBlank()) {
                throw new ValidationException(
                    "Metric name cannot be blank."
                );
            }

            if (
                target != null &&
                (!Double.isFinite(target) || target < 0)
            ) {
                throw new ValidationException("Invalid target.");
            }

            if (
                minimum != null &&
                (!Double.isFinite(minimum) || minimum < 0)
            ) {
                throw new ValidationException("Invalid minimum.");
            }

            if (
                maximum != null &&
                (!Double.isFinite(maximum) || maximum < 0)
            ) {
                throw new ValidationException("Invalid maximum.");
            }

            if (
                minimum != null &&
                maximum != null &&
                minimum > maximum
            ) {
                throw new ValidationException(
                    "Minimum cannot exceed maximum."
                );
            }
        }
    }

    record Observation(
        UUID eventId,
        String metricName,
        String period,
        double value,
        long sampleSize,
        Instant recordedAt
    ) {
        Observation {
            Objects.requireNonNull(eventId);
            Objects.requireNonNull(metricName);
            Objects.requireNonNull(period);
            Objects.requireNonNull(recordedAt);

            if (metricName.isBlank() || period.isBlank()) {
                throw new ValidationException(
                    "Metric name and period are required."
                );
            }

            if (!Double.isFinite(value) || value < 0) {
                throw new ValidationException(
                    "Observation must be finite and non-negative."
                );
            }

            if (sampleSize <= 0) {
                throw new ValidationException(
                    "Sample size must be positive."
                );
            }
        }
    }

    record Evaluation(
        String metricName,
        Category category,
        double current,
        Double previous,
        Double changePercent,
        Double target,
        Status status
    ) {}

    record Alert(
        String metricName,
        AlertSeverity severity,
        String message,
        double observedValue
    ) {}

    record ExperimentGroup(
        String name,
        double value,
        long sampleSize
    ) {}

    record ExperimentResult(
        double absoluteLift,
        Double relativeLift,
        String interpretation
    ) {}

    record ProductReport(
        String productName,
        String period,
        Evaluation northStar,
        List<Evaluation> metrics,
        List<Alert> alerts,
        Map<Category, Long> categoryCounts
    ) {
        ProductReport {
            metrics = List.copyOf(metrics);
            alerts = List.copyOf(alerts);
            categoryCounts = Map.copyOf(categoryCounts);
        }
    }

    static class MetricRepository {

        private final Map<String, MetricDefinition> definitions =
            new HashMap<>();

        private final Map<String, Map<String, Observation>> observations =
            new HashMap<>();

        private final Set<UUID> processedEvents = new HashSet<>();

        public synchronized void register(
            MetricDefinition definition
        ) {
            String key = normalize(definition.name());

            if (definitions.containsKey(key)) {
                throw new ValidationException(
                    "Duplicate metric: " + definition.name()
                );
            }

            definitions.put(key, definition);
            observations.put(key, new HashMap<>());
        }

        public synchronized void record(Observation observation) {
            String key = normalize(observation.metricName());

            MetricDefinition definition = definitions.get(key);

            if (definition == null) {
                throw new ValidationException(
                    "Unknown metric: " + observation.metricName()
                );
            }

            if (processedEvents.contains(observation.eventId())) {
                throw new ValidationException(
                    "Duplicate event ID."
                );
            }

            if (
                definition.minimum() != null &&
                observation.value() < definition.minimum()
            ) {
                throw new ValidationException(
                    "Value below valid metric range."
                );
            }

            if (
                definition.maximum() != null &&
                observation.value() > definition.maximum()
            ) {
                throw new ValidationException(
                    "Value above valid metric range."
                );
            }

            Map<String, Observation> periods =
                observations.get(key);

            if (periods.containsKey(observation.period())) {
                throw new ValidationException(
                    "Duplicate metric observation for period."
                );
            }

            periods.put(observation.period(), observation);
            processedEvents.add(observation.eventId());
        }

        public MetricDefinition getDefinition(String name) {
            MetricDefinition definition =
                definitions.get(normalize(name));

            if (definition == null) {
                throw new ValidationException(
                    "Unknown metric: " + name
                );
            }

            return definition;
        }

        public Observation getObservation(
            String metricName,
            String period
        ) {
            return observations
                .getOrDefault(normalize(metricName), Map.of())
                .get(period);
        }

        public List<MetricDefinition> getAllDefinitions() {
            return List.copyOf(definitions.values());
        }

        public List<MetricDefinition> getByCategory(
            Category category
        ) {
            return definitions.values()
                .stream()
                .filter(item -> item.category() == category)
                .toList();
        }

        public long countEvents() {
            return processedEvents.size();
        }

        private static String normalize(String name) {
            return name.trim().toLowerCase();
        }
    }

    interface EvaluationPolicy {
        Evaluation evaluate(
            MetricDefinition definition,
            Observation current,
            Observation previous
        );
    }

    static class DefaultEvaluationPolicy
        implements EvaluationPolicy {

        @Override
        public Evaluation evaluate(
            MetricDefinition definition,
            Observation current,
            Observation previous
        ) {
            if (current == null) {
                return new Evaluation(
                    definition.name(),
                    definition.category(),
                    0,
                    null,
                    null,
                    definition.target(),
                    Status.MISSING
                );
            }

            double value = current.value();
            Double previousValue =
                previous == null ? null : previous.value();

            Double change = null;

            if (previousValue != null && previousValue != 0) {
                change = (
                    (value - previousValue) /
                    Math.abs(previousValue)
                ) * 100.0;
            }

            Status status = Status.ON_TRACK;

            if (
                definition.direction() == Direction.HIGHER &&
                definition.target() != null &&
                value < definition.target()
            ) {
                status = Status.BELOW_TARGET;
            }

            if (
                definition.direction() == Direction.LOWER &&
                definition.target() != null &&
                value > definition.target()
            ) {
                status = Status.ABOVE_LIMIT;
            }

            if (definition.direction() == Direction.RANGE) {
                if (
                    definition.minimum() != null &&
                    value < definition.minimum()
                ) {
                    status = Status.BELOW_RANGE;
                } else if (
                    definition.maximum() != null &&
                    value > definition.maximum()
                ) {
                    status = Status.ABOVE_RANGE;
                }
            }

            return new Evaluation(
                definition.name(),
                definition.category(),
                value,
                previousValue,
                change,
                definition.target(),
                status
            );
        }
    }

    static class GuardrailPolicy {

        public List<Alert> evaluate(
            MetricRepository repository,
            String period
        ) {
            List<Alert> alerts = new ArrayList<>();

            for (
                MetricDefinition definition :
                repository.getByCategory(Category.GUARDRAIL)
            ) {
                Observation observation =
                    repository.getObservation(
                        definition.name(),
                        period
                    );

                if (observation == null) {
                    alerts.add(new Alert(
                        definition.name(),
                        AlertSeverity.WARNING,
                        "Missing guardrail observation.",
                        0
                    ));
                    continue;
                }

                boolean breach = false;
                String reason = "";

                if (
                    definition.direction() == Direction.LOWER &&
                    definition.target() != null &&
                    observation.value() > definition.target()
                ) {
                    breach = true;
                    reason = "Lower-is-better target exceeded.";
                }

                if (
                    definition.maximum() != null &&
                    observation.value() > definition.maximum()
                ) {
                    breach = true;
                    reason = "Maximum permitted value exceeded.";
                }

                if (
                    definition.minimum() != null &&
                    observation.value() < definition.minimum()
                ) {
                    breach = true;
                    reason = "Minimum permitted value breached.";
                }

                if (breach) {
                    alerts.add(new Alert(
                        definition.name(),
                        AlertSeverity.CRITICAL,
                        reason,
                        observation.value()
                    ));
                }
            }

            return List.copyOf(alerts);
        }
    }

    static class ExperimentService {

        public ExperimentResult compare(
            ExperimentGroup control,
            ExperimentGroup treatment,
            long minimumSampleSize
        ) {
            for (
                ExperimentGroup group :
                List.of(control, treatment)
            ) {
                if (
                    group.sampleSize() < minimumSampleSize ||
                    !Double.isFinite(group.value()) ||
                    group.value() < 0
                ) {
                    throw new ValidationException(
                        "Invalid or insufficient experiment data."
                    );
                }
            }

            double lift =
                treatment.value() - control.value();

            Double relativeLift = null;

            if (control.value() != 0) {
                relativeLift =
                    lift / Math.abs(control.value()) * 100.0;
            }

            String interpretation =
                lift > 0
                    ? "Positive observed treatment lift."
                    : lift < 0
                        ? "Negative observed treatment lift."
                        : "No observed treatment lift.";

            return new ExperimentResult(
                lift,
                relativeLift,
                interpretation
            );
        }
    }

    static class ProductMetricsService {

        private final String productName;
        private final MetricRepository repository;
        private final EvaluationPolicy evaluationPolicy;
        private final GuardrailPolicy guardrailPolicy;

        ProductMetricsService(String productName) {
            this.productName = productName;
            this.repository = new MetricRepository();
            this.evaluationPolicy = new DefaultEvaluationPolicy();
            this.guardrailPolicy = new GuardrailPolicy();
        }

        public void registerMetric(MetricDefinition definition) {
            repository.register(definition);
        }

        public void recordObservation(Observation observation) {
            repository.record(observation);
        }

        public Evaluation evaluate(
            String metricName,
            String period,
            String previousPeriod
        ) {
            MetricDefinition definition =
                repository.getDefinition(metricName);

            Observation current = repository.getObservation(
                metricName,
                period
            );

            Observation previous = repository.getObservation(
                metricName,
                previousPeriod
            );

            return evaluationPolicy.evaluate(
                definition,
                current,
                previous
            );
        }

        public ProductReport generateReport(
            String period,
            String previousPeriod
        ) {
            List<MetricDefinition> northStarMetrics =
                repository.getByCategory(Category.NORTH_STAR);

            if (northStarMetrics.size() != 1) {
                throw new ProductException(
                    "Exactly one North Star Metric is required."
                );
            }

            Evaluation northStar = evaluate(
                northStarMetrics.get(0).name(),
                period,
                previousPeriod
            );

            List<Evaluation> evaluations =
                repository.getAllDefinitions()
                    .stream()
                    .map(definition -> evaluate(
                        definition.name(),
                        period,
                        previousPeriod
                    ))
                    .toList();

            List<Alert> alerts =
                guardrailPolicy.evaluate(repository, period);

            Map<Category, Long> counts =
                evaluations.stream()
                    .collect(Collectors.groupingBy(
                        Evaluation::category,
                        () -> new EnumMap<>(Category.class),
                        Collectors.counting()
                    ));

            return new ProductReport(
                productName,
                period,
                northStar,
                evaluations,
                alerts,
                counts
            );
        }

        public MetricRepository repository() {
            return repository;
        }
    }

    private static Observation observation(
        String metric,
        String period,
        double value
    ) {
        return new Observation(
            UUID.randomUUID(),
            metric,
            period,
            value,
            10000,
            Instant.now()
        );
    }

    private static ProductMetricsService createDemo() {
        ProductMetricsService service =
            new ProductMetricsService(
                "Enterprise Learning Platform"
            );

        service.registerMetric(new MetricDefinition(
            "Weekly Active Learners",
            Category.NORTH_STAR,
            "users",
            Direction.HIGHER,
            12000.0,
            null,
            null,
            "Users completing meaningful learning activities."
        ));

        service.registerMetric(new MetricDefinition(
            "Activation Rate",
            Category.INPUT,
            "%",
            Direction.HIGHER,
            65.0,
            0.0,
            100.0,
            "Percentage of new users reaching activation."
        ));

        service.registerMetric(new MetricDefinition(
            "Lesson Completion Rate",
            Category.INPUT,
            "%",
            Direction.HIGHER,
            75.0,
            0.0,
            100.0,
            "Percentage of started lessons completed."
        ));

        service.registerMetric(new MetricDefinition(
            "Weekly Learning Sessions",
            Category.INPUT,
            "sessions",
            Direction.HIGHER,
            45000.0,
            null,
            null,
            "Meaningful learning sessions."
        ));

        service.registerMetric(new MetricDefinition(
            "Subscription Revenue",
            Category.OUTPUT,
            "INR",
            Direction.HIGHER,
            1500000.0,
            null,
            null,
            "Recognized subscription revenue."
        ));

        service.registerMetric(new MetricDefinition(
            "Retention Rate",
            Category.OUTPUT,
            "%",
            Direction.HIGHER,
            85.0,
            0.0,
            100.0,
            "Percentage of retained users."
        ));

        service.registerMetric(new MetricDefinition(
            "Application Error Rate",
            Category.GUARDRAIL,
            "%",
            Direction.LOWER,
            1.0,
            0.0,
            2.0,
            "Percentage of requests producing errors."
        ));

        service.registerMetric(new MetricDefinition(
            "Page Load Time",
            Category.GUARDRAIL,
            "seconds",
            Direction.LOWER,
            2.0,
            0.0,
            3.0,
            "Average application page load time."
        ));

        Map<String, double[]> dataset = new HashMap<>();

        dataset.put("Weekly Active Learners", new double[]{10800, 12400});
        dataset.put("Activation Rate", new double[]{62, 68});
        dataset.put("Lesson Completion Rate", new double[]{72, 78});
        dataset.put("Weekly Learning Sessions", new double[]{41000, 47000});
        dataset.put("Subscription Revenue", new double[]{1380000, 1570000});
        dataset.put("Retention Rate", new double[]{84, 86});
        dataset.put("Application Error Rate", new double[]{0.8, 2.4});
        dataset.put("Page Load Time", new double[]{1.8, 2.2});

        dataset.forEach((metric, values) -> {
            service.recordObservation(
                observation(metric, "previous", values[0])
            );

            service.recordObservation(
                observation(metric, "current", values[1])
            );
        });

        return service;
    }

    private static void runAssertions(
        ProductMetricsService service
    ) {
        Evaluation northStar = service.evaluate(
            "Weekly Active Learners",
            "current",
            "previous"
        );

        if (northStar.current() != 12400) {
            throw new AssertionError("North Star value mismatch.");
        }

        if (
            northStar.changePercent() == null ||
            Math.abs(northStar.changePercent() - 14.8148) > 0.01
        ) {
            throw new AssertionError("Growth calculation failed.");
        }

        ExperimentService experimentService =
            new ExperimentService();

        ExperimentResult result = experimentService.compare(
            new ExperimentGroup("Control", 65, 500),
            new ExperimentGroup("Treatment", 70, 520),
            30
        );

        if (Math.abs(result.absoluteLift() - 5) > 0.0001) {
            throw new AssertionError("Experiment lift failed.");
        }

        System.out.println("All enterprise validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            ProductMetricsService service = createDemo();

            runAssertions(service);

            ProductReport report = service.generateReport(
                "current",
                "previous"
            );

            System.out.println("\nPRODUCT METRICS REPORT");
            System.out.println("Product: " + report.productName());
            System.out.println("Period: " + report.period());

            System.out.println("\nNORTH STAR METRIC");
            System.out.println(report.northStar());

            System.out.println("\nMETRIC PERFORMANCE");

            for (Evaluation evaluation : report.metrics()) {
                System.out.println(
                    evaluation.metricName()
                    + " | "
                    + evaluation.category()
                    + " | "
                    + evaluation.current()
                    + " | "
                    + evaluation.status()
                );
            }

            System.out.println("\nGUARDRAIL ALERTS");

            if (report.alerts().isEmpty()) {
                System.out.println("No breaches detected.");
            }

            for (Alert alert : report.alerts()) {
                System.out.println(
                    alert.severity()
                    + " | "
                    + alert.metricName()
                    + " | "
                    + alert.message()
                );
            }

            System.out.println("\nMETRIC CATEGORY COUNTS");
            report.categoryCounts().forEach(
                (category, count) ->
                    System.out.println(category + ": " + count)
            );

        } catch (ProductException exception) {
            System.err.println(
                "PRODUCT METRICS ERROR: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
