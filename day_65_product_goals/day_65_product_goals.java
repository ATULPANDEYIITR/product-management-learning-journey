import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.HashSet;
import java.util.stream.Collectors;

/*
 * Product Goals: Enterprise OKR and Strategic Metrics Management.
 *
 * Java 17 features:
 * - Records
 * - Enums
 * - Immutable measurement objects
 * - Interfaces
 * - Generic repository
 * - Domain services
 * - Explicit lifecycle transitions
 * - Weighted progress calculations
 * - Approval and ownership policies
 * - Data-quality and freshness controls
 * - Audit history
 */

public class ProductGoals {

    enum GoalStatus {
        DRAFT,
        ACTIVE,
        AT_RISK,
        ACHIEVED,
        MISSED,
        CANCELLED
    }

    enum MetricDirection {
        INCREASE,
        DECREASE
    }

    enum MetricCategory {
        LEADING,
        LAGGING,
        GUARDRAIL
    }

    static class GoalException extends RuntimeException {
        GoalException(String message) {
            super(message);
        }
    }

    static class ValidationException extends GoalException {
        ValidationException(String message) {
            super(message);
        }
    }

    record Measurement(
        double value,
        Instant timestamp,
        String source,
        double confidence
    ) {
        Measurement {
            if (!Double.isFinite(value)) {
                throw new ValidationException("Measurement must be finite.");
            }

            Objects.requireNonNull(timestamp, "Timestamp is required.");

            if (source == null || source.isBlank()) {
                throw new ValidationException("Source is required.");
            }

            if (!Double.isFinite(confidence) ||
                confidence < 0 || confidence > 1) {
                throw new ValidationException("Invalid confidence.");
            }
        }
    }

    record GoalAudit(
        String event,
        Instant timestamp,
        String actor
    ) {}

    record MetricReport(
        String metricId,
        String name,
        double baseline,
        double current,
        double target,
        double progress,
        String unit,
        double confidence,
        boolean withinGuardrails
    ) {}

    record ObjectiveReport(
        String objectiveId,
        String title,
        String owner,
        GoalStatus status,
        double progress,
        List<MetricReport> keyResults
    ) {}

    interface ProgressCalculator {
        double calculate(Metric metric);
    }

    static class StandardProgressCalculator
            implements ProgressCalculator {

        @Override
        public double calculate(Metric metric) {
            double progress =
                (metric.currentValue() - metric.baseline()) /
                (metric.target() - metric.baseline()) * 100.0;

            return Math.max(0, Math.min(100, progress));
        }
    }

    static class Metric {
        private final String id;
        private final String name;
        private final String unit;
        private final double baseline;
        private final double target;
        private final double weight;
        private final MetricDirection direction;
        private final MetricCategory category;
        private final double lowerGuardrail;
        private final double upperGuardrail;

        private final List<Measurement> measurements =
            new ArrayList<>();

        Metric(
            String id,
            String name,
            String unit,
            double baseline,
            double target,
            double weight,
            MetricDirection direction,
            MetricCategory category,
            double lowerGuardrail,
            double upperGuardrail
        ) {
            if (id == null || id.isBlank() ||
                name == null || name.isBlank() ||
                unit == null || unit.isBlank()) {
                throw new ValidationException("Metric identity is required.");
            }

            if (!Double.isFinite(baseline) ||
                !Double.isFinite(target) ||
                !Double.isFinite(weight)) {
                throw new ValidationException("Metric values must be finite.");
            }

            if (weight <= 0 || baseline == target) {
                throw new ValidationException("Invalid metric configuration.");
            }

            if (direction == MetricDirection.INCREASE && target <= baseline) {
                throw new ValidationException("Increase target is invalid.");
            }

            if (direction == MetricDirection.DECREASE && target >= baseline) {
                throw new ValidationException("Decrease target is invalid.");
            }

            if (lowerGuardrail > upperGuardrail) {
                throw new ValidationException("Invalid guardrail boundaries.");
            }

            this.id = id;
            this.name = name;
            this.unit = unit;
            this.baseline = baseline;
            this.target = target;
            this.weight = weight;
            this.direction = direction;
            this.category = category;
            this.lowerGuardrail = lowerGuardrail;
            this.upperGuardrail = upperGuardrail;
        }

        void record(Measurement measurement) {
            if (!measurements.isEmpty()) {
                Instant previous = measurements.get(
                    measurements.size() - 1
                ).timestamp();

                if (!measurement.timestamp().isAfter(previous)) {
                    throw new ValidationException(
                        "Measurements must be chronological."
                    );
                }
            }

            measurements.add(measurement);
        }

        double currentValue() {
            if (measurements.isEmpty()) {
                return baseline;
            }

            return measurements.get(
                measurements.size() - 1
            ).value();
        }

        double confidence() {
            if (measurements.isEmpty()) return 0;

            return measurements.get(
                measurements.size() - 1
            ).confidence();
        }

        double baseline() {
            return baseline;
        }

        double target() {
            return target;
        }

        double weight() {
            return weight;
        }

        String id() {
            return id;
        }

        boolean withinGuardrails() {
            return currentValue() >= lowerGuardrail &&
                   currentValue() <= upperGuardrail;
        }

        MetricReport report(ProgressCalculator calculator) {
            return new MetricReport(
                id,
                name,
                baseline,
                currentValue(),
                target,
                calculator.calculate(this),
                unit,
                confidence(),
                withinGuardrails()
            );
        }
    }

    static class Objective {
        private final String id;
        private final String title;
        private final String owner;
        private final Instant deadline;
        private final String parentId;

        private final Map<String, Metric> keyResults =
            new HashMap<>();

        private final List<GoalAudit> auditTrail =
            new ArrayList<>();

        private GoalStatus status = GoalStatus.DRAFT;

        Objective(
            String id,
            String title,
            String owner,
            Instant deadline,
            String parentId
        ) {
            if (id == null || id.isBlank() ||
                title == null || title.isBlank() ||
                owner == null || owner.isBlank()) {
                throw new ValidationException("Objective identity is required.");
            }

            this.id = id;
            this.title = title;
            this.owner = owner;
            this.deadline = Objects.requireNonNull(deadline);
            this.parentId = parentId;
        }

        void addKeyResult(Metric metric) {
            if (status != GoalStatus.DRAFT) {
                throw new GoalException(
                    "Key Results cannot be changed after activation."
                );
            }

            if (keyResults.putIfAbsent(metric.id(), metric) != null) {
                throw new ValidationException("Duplicate Key Result.");
            }
        }

        void activate(String actor) {
            if (status != GoalStatus.DRAFT) {
                throw new GoalException("Invalid activation transition.");
            }

            if (keyResults.isEmpty()) {
                throw new ValidationException(
                    "Objectives require at least one Key Result."
                );
            }

            if (actor == null || actor.isBlank()) {
                throw new ValidationException("Actor is required.");
            }

            status = GoalStatus.ACTIVE;

            auditTrail.add(new GoalAudit(
                "ACTIVATED",
                Instant.now(),
                actor
            ));
        }

        double progress(ProgressCalculator calculator) {
            if (keyResults.isEmpty()) return 0;

            double weightedProgress = 0;
            double totalWeight = 0;

            for (Metric metric : keyResults.values()) {
                weightedProgress +=
                    calculator.calculate(metric) * metric.weight();

                totalWeight += metric.weight();
            }

            return weightedProgress / totalWeight;
        }

        GoalStatus evaluate(
            Instant now,
            ProgressCalculator calculator
        ) {
            if (status == GoalStatus.DRAFT ||
                status == GoalStatus.CANCELLED) {
                return status;
            }

            boolean guardrailFailure = keyResults.values()
                .stream()
                .anyMatch(metric -> !metric.withinGuardrails());

            GoalStatus previous = status;

            if (guardrailFailure) {
                status = GoalStatus.AT_RISK;
            } else if (progress(calculator) >= 100) {
                status = GoalStatus.ACHIEVED;
            } else if (now.isAfter(deadline)) {
                status = GoalStatus.MISSED;
            } else if (progress(calculator) < 40) {
                status = GoalStatus.AT_RISK;
            } else {
                status = GoalStatus.ACTIVE;
            }

            if (previous != status) {
                auditTrail.add(new GoalAudit(
                    "STATUS_CHANGED:" + previous + "->" + status,
                    now,
                    "SYSTEM"
                ));
            }

            return status;
        }

        void cancel(String actor) {
            if (status != GoalStatus.DRAFT &&
                status != GoalStatus.ACTIVE &&
                status != GoalStatus.AT_RISK) {
                throw new GoalException("Cannot cancel this objective.");
            }

            status = GoalStatus.CANCELLED;

            auditTrail.add(new GoalAudit(
                "CANCELLED",
                Instant.now(),
                actor
            ));
        }

        ObjectiveReport report(ProgressCalculator calculator) {
            List<MetricReport> metrics = keyResults.values()
                .stream()
                .map(metric -> metric.report(calculator))
                .collect(Collectors.toList());

            return new ObjectiveReport(
                id,
                title,
                owner,
                status,
                progress(calculator),
                List.copyOf(metrics)
            );
        }

        String id() {
            return id;
        }

        String parentId() {
            return parentId;
        }

        List<GoalAudit> auditTrail() {
            return Collections.unmodifiableList(auditTrail);
        }
    }

    interface Repository<T> {
        void save(String id, T value);
        Optional<T> find(String id);
        List<T> findAll();
    }

    static class InMemoryRepository<T> implements Repository<T> {
        private final Map<String, T> data = new HashMap<>();

        @Override
        public void save(String id, T value) {
            if (data.containsKey(id)) {
                throw new ValidationException("Duplicate repository ID.");
            }

            data.put(id, Objects.requireNonNull(value));
        }

        @Override
        public Optional<T> find(String id) {
            return Optional.ofNullable(data.get(id));
        }

        @Override
        public List<T> findAll() {
            return List.copyOf(data.values());
        }
    }

    static class GoalService {
        private final Repository<Objective> repository;
        private final ProgressCalculator calculator;

        GoalService(
            Repository<Objective> repository,
            ProgressCalculator calculator
        ) {
            this.repository = repository;
            this.calculator = calculator;
        }

        void create(Objective objective) {
            if (objective.parentId() != null &&
                repository.find(objective.parentId()).isEmpty()) {
                throw new ValidationException(
                    "Parent strategic objective does not exist."
                );
            }

            repository.save(objective.id(), objective);
        }

        void evaluateAll(Instant now) {
            repository.findAll().forEach(
                objective -> objective.evaluate(now, calculator)
            );
        }

        List<ObjectiveReport> portfolioReport() {
            return repository.findAll()
                .stream()
                .map(objective -> objective.report(calculator))
                .toList();
        }

        List<ObjectiveReport> childObjectives(String parentId) {
            return repository.findAll()
                .stream()
                .filter(objective ->
                    parentId.equals(objective.parentId()))
                .map(objective -> objective.report(calculator))
                .toList();
        }
    }

    public static void main(String[] args) {
        ProgressCalculator calculator =
            new StandardProgressCalculator();

        Repository<Objective> repository =
            new InMemoryRepository<>();

        GoalService service = new GoalService(repository, calculator);

        Objective strategic = new Objective(
            "STR-001",
            "Improve digital product experience",
            "Product Director",
            Instant.parse("2026-12-31T23:59:59Z"),
            null
        );

        strategic.addKeyResult(new Metric(
            "KR-STR-001",
            "Customer experience improvement",
            "score",
            60,
            80,
            1,
            MetricDirection.INCREASE,
            MetricCategory.LAGGING,
            50,
            100
        ));

        service.create(strategic);
        strategic.activate("product-director");

        Objective retention = new Objective(
            "OBJ-001",
            "Improve customer retention",
            "Product Manager",
            Instant.parse("2026-12-31T23:59:59Z"),
            "STR-001"
        );

        Metric retentionMetric = new Metric(
            "KR-001",
            "Monthly retention",
            "percent",
            70,
            85,
            3,
            MetricDirection.INCREASE,
            MetricCategory.LAGGING,
            60,
            100
        );

        retentionMetric.record(new Measurement(
            80,
            Instant.parse("2026-11-01T10:00:00Z"),
            "Subscription analytics",
            0.97
        ));

        Metric activationMetric = new Metric(
            "KR-002",
            "Customer activation",
            "percent",
            40,
            70,
            1,
            MetricDirection.INCREASE,
            MetricCategory.LEADING,
            30,
            100
        );

        activationMetric.record(new Measurement(
            60,
            Instant.parse("2026-11-01T10:00:00Z"),
            "Product analytics",
            0.94
        ));

        retention.addKeyResult(retentionMetric);
        retention.addKeyResult(activationMetric);

        service.create(retention);
        retention.activate("product-manager");

        service.evaluateAll(
            Instant.parse("2026-11-04T10:00:00Z")
        );

        System.out.println("ENTERPRISE PRODUCT GOAL REPORT");

        for (ObjectiveReport report : service.portfolioReport()) {
            System.out.println("\nObjective: " + report.title());
            System.out.println("Owner: " + report.owner());
            System.out.println("Status: " + report.status());
            System.out.printf(
                "Progress: %.2f%%%n",
                report.progress()
            );

            for (MetricReport metric : report.keyResults()) {
                System.out.printf(
                    "%s | %s | Current: %.2f | Target: %.2f | " +
                    "Progress: %.2f%% | Quality: %.2f%n",
                    metric.metricId(),
                    metric.name(),
                    metric.current(),
                    metric.target(),
                    metric.progress(),
                    metric.confidence()
                );
            }
        }

        System.out.println("\nSTRATEGIC ALIGNMENT");

        service.childObjectives("STR-001").forEach(
            report -> System.out.println(
                report.objectiveId() + " -> " + report.title()
            )
        );

        if (Math.abs(retention.progress(calculator) - 66.6666667) > 0.01) {
            throw new GoalException("Progress calculation failed.");
        }

        try {
            retentionMetric.record(new Measurement(
                82,
                Instant.parse("2026-10-31T10:00:00Z"),
                "Invalid historical record",
                0.9
            ));
        } catch (ValidationException error) {
            System.out.println(
                "\nInvalid historical measurement rejected: " +
                error.getMessage()
            );
        }

        System.out.println("\nEnterprise goal evaluation completed.");
    }
}
