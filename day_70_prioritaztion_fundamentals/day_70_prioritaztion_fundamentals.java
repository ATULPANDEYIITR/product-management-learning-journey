import java.time.Instant;
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
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Prioritization Fundamentals
 *
 * Enterprise portfolio prioritization model.
 *
 * Features:
 * - Explicit domain types
 * - Pluggable scoring frameworks
 * - RICE, WSJF and weighted scoring
 * - MoSCoW classification
 * - Portfolio capacity policies
 * - Dependency validation
 * - Mandatory initiative enforcement
 * - Opportunity-cost analysis
 * - Immutable allocation records
 * - Decision audit history
 *
 * Java 17, standard library only.
 */

public class PrioritizationFundamentals {

    enum Priority {
        CRITICAL, HIGH, MEDIUM, LOW
    }

    enum MoSCoW {
        MUST, SHOULD, COULD, WONT
    }

    enum Status {
        PROPOSED, EVALUATED, SELECTED, DEFERRED
    }

    enum Framework {
        RICE, WSJF, WEIGHTED
    }

    static class PrioritizationException extends RuntimeException {
        PrioritizationException(String message) {
            super(message);
        }
    }

    static class ValidationException extends PrioritizationException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class CapacityException extends PrioritizationException {
        CapacityException(String message) {
            super(message);
        }
    }

    record Initiative(
        String id,
        String name,
        String description,
        double reach,
        double impact,
        double confidence,
        double effort,
        double businessValue,
        double urgency,
        double riskReduction,
        double strategicAlignment,
        double cost,
        boolean mandatory,
        Priority priority,
        MoSCoW classification,
        Set<String> dependencies
    ) {
        Initiative {
            if (id == null || id.isBlank()) {
                throw new ValidationException(
                    "Initiative ID is required."
                );
            }

            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Initiative name is required."
                );
            }

            Objects.requireNonNull(priority);
            Objects.requireNonNull(classification);

            dependencies = Set.copyOf(
                Objects.requireNonNull(dependencies)
            );

            if (dependencies.contains(id)) {
                throw new ValidationException(
                    "Self-dependency is prohibited."
                );
            }

            validateNonNegative("reach", reach);
            validateRange("impact", impact, 0, 10);
            validateRange("confidence", confidence, 0, 1);
            validateRange("effort", effort, Double.MIN_VALUE, Double.MAX_VALUE);
            validateRange("businessValue", businessValue, 0, 10);
            validateRange("urgency", urgency, 0, 10);
            validateRange("riskReduction", riskReduction, 0, 10);
            validateRange("strategicAlignment", strategicAlignment, 0, 10);
            validateNonNegative("cost", cost);
        }

        private static void validateNonNegative(
            String name,
            double value
        ) {
            if (!Double.isFinite(value) || value < 0) {
                throw new ValidationException(
                    name + " must be finite and non-negative."
                );
            }
        }

        private static void validateRange(
            String name,
            double value,
            double minimum,
            double maximum
        ) {
            if (
                !Double.isFinite(value) ||
                value < minimum ||
                value > maximum
            ) {
                throw new ValidationException(
                    name + " must be between " +
                    minimum + " and " + maximum + "."
                );
            }
        }
    }

    record Capacity(double effort, double budget) {
        Capacity {
            if (
                !Double.isFinite(effort) ||
                !Double.isFinite(budget) ||
                effort < 0 ||
                budget < 0
            ) {
                throw new ValidationException(
                    "Invalid portfolio capacity."
                );
            }
        }
    }

    record Score(
        String initiativeId,
        Framework framework,
        double value
    ) {}

    record Decision(
        String initiativeId,
        Status status,
        double score,
        String explanation
    ) {}

    record Allocation(
        UUID allocationId,
        Instant createdAt,
        Framework framework,
        List<String> selected,
        List<String> deferred,
        double effortUsed,
        double budgetUsed,
        double remainingEffort,
        double remainingBudget,
        double businessValue,
        double opportunityCost,
        List<Decision> decisions
    ) {
        Allocation {
            selected = List.copyOf(selected);
            deferred = List.copyOf(deferred);
            decisions = List.copyOf(decisions);
        }
    }

    interface ScoringStrategy {
        Framework framework();

        double calculate(Initiative initiative);
    }

    static final class RiceStrategy implements ScoringStrategy {

        @Override
        public Framework framework() {
            return Framework.RICE;
        }

        @Override
        public double calculate(Initiative item) {
            return (
                item.reach() *
                item.impact() *
                item.confidence()
            ) / item.effort();
        }
    }

    static final class WsjfStrategy implements ScoringStrategy {

        @Override
        public Framework framework() {
            return Framework.WSJF;
        }

        @Override
        public double calculate(Initiative item) {
            return (
                item.businessValue() +
                item.urgency() +
                item.riskReduction()
            ) / item.effort();
        }
    }

    static final class WeightedStrategy implements ScoringStrategy {

        private final Map<String, Double> weights;

        WeightedStrategy() {
            Map<String, Double> configured = new LinkedHashMap<>();

            configured.put("businessValue", 0.30);
            configured.put("strategicAlignment", 0.30);
            configured.put("urgency", 0.15);
            configured.put("riskReduction", 0.15);
            configured.put("confidence", 0.10);

            double sum = configured.values()
                .stream()
                .mapToDouble(Double::doubleValue)
                .sum();

            if (Math.abs(sum - 1.0) > 1e-9) {
                throw new ValidationException(
                    "Weighted criteria must sum to 1."
                );
            }

            this.weights = Map.copyOf(configured);
        }

        @Override
        public Framework framework() {
            return Framework.WEIGHTED;
        }

        @Override
        public double calculate(Initiative item) {
            return (
                item.businessValue() * weights.get("businessValue") +
                item.strategicAlignment() *
                    weights.get("strategicAlignment") +
                item.urgency() * weights.get("urgency") +
                item.riskReduction() * weights.get("riskReduction") +
                item.confidence() * 10 *
                    weights.get("confidence")
            );
        }
    }

    static final class PrioritizationPolicy {

        private final double minimumConfidence;
        private final boolean requireStrategicAlignment;

        PrioritizationPolicy(
            double minimumConfidence,
            boolean requireStrategicAlignment
        ) {
            if (
                !Double.isFinite(minimumConfidence) ||
                minimumConfidence < 0 ||
                minimumConfidence > 1
            ) {
                throw new ValidationException(
                    "Invalid minimum confidence."
                );
            }

            this.minimumConfidence = minimumConfidence;
            this.requireStrategicAlignment =
                requireStrategicAlignment;
        }

        String evaluate(Initiative item) {
            if (item.confidence() < minimumConfidence) {
                return "Confidence threshold not satisfied.";
            }

            if (
                requireStrategicAlignment &&
                item.strategicAlignment() == 0
            ) {
                return "Strategic alignment is required.";
            }

            if (item.classification() == MoSCoW.WONT &&
                item.mandatory()) {
                return "A mandatory initiative cannot be classified WONT.";
            }

            return null;
        }
    }

    static final class PrioritizationService {

        private final Map<String, Initiative> initiatives;
        private final Map<Framework, ScoringStrategy> strategies;
        private final PrioritizationPolicy policy;

        private final List<Allocation> auditHistory =
            new ArrayList<>();

        PrioritizationService(
            List<Initiative> input,
            PrioritizationPolicy policy
        ) {
            if (input == null || input.isEmpty()) {
                throw new ValidationException(
                    "Portfolio cannot be empty."
                );
            }

            this.policy = Objects.requireNonNull(policy);

            Map<String, Initiative> indexed = new LinkedHashMap<>();

            for (Initiative item : input) {
                if (indexed.putIfAbsent(item.id(), item) != null) {
                    throw new ValidationException(
                        "Duplicate initiative: " + item.id()
                    );
                }
            }

            this.initiatives = Collections.unmodifiableMap(indexed);

            Map<Framework, ScoringStrategy> registered =
                new EnumMap<>(Framework.class);

            register(registered, new RiceStrategy());
            register(registered, new WsjfStrategy());
            register(registered, new WeightedStrategy());

            this.strategies = Collections.unmodifiableMap(registered);

            validateDependencies();
        }

        private static void register(
            Map<Framework, ScoringStrategy> registry,
            ScoringStrategy strategy
        ) {
            if (registry.putIfAbsent(
                strategy.framework(),
                strategy
            ) != null) {
                throw new ValidationException(
                    "Duplicate scoring strategy."
                );
            }
        }

        private void validateDependencies() {
            for (Initiative item : initiatives.values()) {
                for (String dependency : item.dependencies()) {
                    if (!initiatives.containsKey(dependency)) {
                        throw new ValidationException(
                            item.id() +
                            " references missing dependency " +
                            dependency
                        );
                    }
                }
            }

            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();

            for (String id : initiatives.keySet()) {
                visit(id, visiting, visited);
            }
        }

        private void visit(
            String id,
            Set<String> visiting,
            Set<String> visited
        ) {
            if (visiting.contains(id)) {
                throw new ValidationException(
                    "Circular dependency detected."
                );
            }

            if (visited.contains(id)) {
                return;
            }

            visiting.add(id);

            for (String dependency :
                initiatives.get(id).dependencies()) {
                visit(dependency, visiting, visited);
            }

            visiting.remove(id);
            visited.add(id);
        }

        private double score(
            Initiative item,
            Framework framework
        ) {
            ScoringStrategy strategy = strategies.get(framework);

            if (strategy == null) {
                throw new ValidationException(
                    "Unsupported scoring framework."
                );
            }

            return strategy.calculate(item);
        }

        List<Score> rank(Framework framework) {
            return initiatives.values()
                .stream()
                .map(item -> new Score(
                    item.id(),
                    framework,
                    score(item, framework)
                ))
                .sorted(
                    Comparator
                        .comparing(
                            (Score score) ->
                                !initiatives.get(
                                    score.initiativeId()
                                ).mandatory()
                        )
                        .thenComparing(
                            Comparator.comparingDouble(
                                Score::value
                            ).reversed()
                        )
                        .thenComparing(Score::initiativeId)
                )
                .toList();
        }

        private Set<String> dependencyClosure(String root) {
            Set<String> result = new HashSet<>();
            List<String> stack = new ArrayList<>();

            stack.add(root);

            while (!stack.isEmpty()) {
                String current = stack.remove(stack.size() - 1);

                if (!result.add(current)) {
                    continue;
                }

                stack.addAll(
                    initiatives.get(current).dependencies()
                );
            }

            return result;
        }

        Allocation allocate(
            Capacity capacity,
            Framework framework
        ) {
            Objects.requireNonNull(capacity);

            List<Score> ranking = rank(framework);

            Set<String> selected = new HashSet<>();
            Set<String> deferred = new HashSet<>();

            Map<String, Double> scores = new HashMap<>();

            ranking.forEach(
                item -> scores.put(
                    item.initiativeId(),
                    item.value()
                )
            );

            double[] consumption = {0.0, 0.0};

            // Dependency closure is accounted for incrementally.
            java.util.function.Function<String, Boolean> include =
                id -> {
                    Set<String> closure = dependencyClosure(id);

                    Set<String> additions = new HashSet<>(closure);
                    additions.removeAll(selected);

                    double effort = additions.stream()
                        .map(initiatives::get)
                        .mapToDouble(Initiative::effort)
                        .sum();

                    double budget = additions.stream()
                        .map(initiatives::get)
                        .mapToDouble(Initiative::cost)
                        .sum();

                    if (
                        consumption[0] + effort > capacity.effort() + 1e-9 ||
                        consumption[1] + budget > capacity.budget() + 1e-9
                    ) {
                        return false;
                    }

                    selected.addAll(additions);

                    consumption[0] += effort;
                    consumption[1] += budget;

                    return true;
                };

            // Mandatory work must fit. The service does not silently
            // override financial or resource governance.
            for (Score entry : ranking) {
                Initiative item = initiatives.get(
                    entry.initiativeId()
                );

                if (!item.mandatory()) {
                    continue;
                }

                if (!include.apply(item.id())) {
                    throw new CapacityException(
                        "Mandatory initiative " + item.id() +
                        " exceeds available capacity."
                    );
                }
            }

            for (Score entry : ranking) {
                String id = entry.initiativeId();

                if (selected.contains(id)) {
                    continue;
                }

                Initiative item = initiatives.get(id);

                if (policy.evaluate(item) != null) {
                    deferred.add(id);
                    continue;
                }

                // Every dependency must also satisfy the policy.
                boolean dependencyEligible =
                    dependencyClosure(id)
                        .stream()
                        .allMatch(dependency ->
                            policy.evaluate(
                                initiatives.get(dependency)
                            ) == null ||
                            selected.contains(dependency)
                        );

                if (
                    !dependencyEligible ||
                    !include.apply(id)
                ) {
                    deferred.add(id);
                }
            }

            deferred.addAll(
                initiatives.keySet()
                    .stream()
                    .filter(id -> !selected.contains(id))
                    .toList()
            );

            double businessValue = selected.stream()
                .map(initiatives::get)
                .mapToDouble(Initiative::businessValue)
                .sum();

            double opportunityCost = deferred.stream()
                .mapToDouble(scores::get)
                .sum();

            List<Decision> decisions = new ArrayList<>();

            for (String id : initiatives.keySet()) {
                Initiative item = initiatives.get(id);

                Status status = selected.contains(id)
                    ? Status.SELECTED
                    : Status.DEFERRED;

                String explanation = selected.contains(id)
                    ? "Selected within portfolio constraints."
                    : "Deferred because of capacity, policy or ranking.";

                decisions.add(new Decision(
                    id,
                    status,
                    scores.get(id),
                    explanation
                ));
            }

            Allocation allocation = new Allocation(
                UUID.randomUUID(),
                Instant.now(),
                framework,
                selected.stream().sorted().toList(),
                deferred.stream().sorted().toList(),
                consumption[0],
                consumption[1],
                capacity.effort() - consumption[0],
                capacity.budget() - consumption[1],
                businessValue,
                opportunityCost,
                decisions
            );

            auditHistory.add(allocation);

            return allocation;
        }

        List<Allocation> history() {
            return List.copyOf(auditHistory);
        }

        Map<Framework, Allocation> sensitivityAnalysis(
            Capacity capacity
        ) {
            Map<Framework, Allocation> report =
                new EnumMap<>(Framework.class);

            for (Framework framework : Framework.values()) {
                report.put(
                    framework,
                    allocate(capacity, framework)
                );
            }

            return Collections.unmodifiableMap(report);
        }
    }

    static List<Initiative> samplePortfolio() {
        return List.of(
            new Initiative(
                "I001", "Security compliance",
                "Mandatory security remediation.",
                100, 10, 0.99, 8,
                10, 10, 10, 10,
                12000, true,
                Priority.CRITICAL, MoSCoW.MUST,
                Set.of()
            ),
            new Initiative(
                "I002", "Customer analytics",
                "Customer usage intelligence.",
                8000, 8, 0.85, 13,
                9, 7, 4, 9,
                18000, false,
                Priority.HIGH, MoSCoW.SHOULD,
                Set.of("I001")
            ),
            new Initiative(
                "I003", "Infrastructure optimization",
                "Reduce recurring cloud costs.",
                5000, 7, 0.95, 5,
                8, 8, 6, 8,
                7000, false,
                Priority.HIGH, MoSCoW.MUST,
                Set.of()
            ),
            new Initiative(
                "I004", "Internal dashboard",
                "Operational reporting.",
                2000, 5, 0.90, 4,
                5, 3, 2, 6,
                4000, false,
                Priority.MEDIUM, MoSCoW.COULD,
                Set.of()
            ),
            new Initiative(
                "I005", "Disaster recovery",
                "Improve recovery capabilities.",
                1000, 9, 0.90, 7,
                9, 9, 10, 9,
                10000, false,
                Priority.HIGH, MoSCoW.SHOULD,
                Set.of()
            ),
            new Initiative(
                "I006", "Mobile redesign",
                "Improve mobile user experience.",
                6000, 6, 0.75, 10,
                7, 5, 3, 8,
                14000, false,
                Priority.LOW, MoSCoW.COULD,
                Set.of()
            )
        );
    }

    static void runValidationTests() {
        boolean rejected = false;

        try {
            new Initiative(
                "BAD", "Invalid", "",
                1, 1, 1, 0,
                1, 1, 1, 1,
                1, false,
                Priority.LOW, MoSCoW.COULD,
                Set.of()
            );
        } catch (ValidationException exception) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError(
                "Invalid effort validation failed."
            );
        }

        rejected = false;

        try {
            Initiative a = new Initiative(
                "A", "A", "",
                1, 1, 1, 1,
                1, 1, 1, 1,
                1, false,
                Priority.LOW, MoSCoW.COULD,
                Set.of("B")
            );

            Initiative b = new Initiative(
                "B", "B", "",
                1, 1, 1, 1,
                1, 1, 1, 1,
                1, false,
                Priority.LOW, MoSCoW.COULD,
                Set.of("A")
            );

            new PrioritizationService(
                List.of(a, b),
                new PrioritizationPolicy(0, false)
            );

        } catch (ValidationException exception) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError(
                "Circular dependency validation failed."
            );
        }

        System.out.println("Validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            PrioritizationPolicy policy =
                new PrioritizationPolicy(0.60, true);

            PrioritizationService service =
                new PrioritizationService(
                    samplePortfolio(),
                    policy
                );

            Capacity capacity = new Capacity(
                35,
                45000
            );

            System.out.println(
                "PRIORITIZATION FUNDAMENTALS"
            );

            for (Framework framework : Framework.values()) {
                System.out.println(
                    "\nFramework: " + framework
                );

                for (Score score : service.rank(framework)) {
                    System.out.printf(
                        "%-8s %-32s %.2f%n",
                        score.initiativeId(),
                        samplePortfolio().stream()
                            .filter(item ->
                                item.id().equals(score.initiativeId())
                            )
                            .findFirst()
                            .orElseThrow()
                            .name(),
                        score.value()
                    );
                }
            }

            Allocation result = service.allocate(
                capacity,
                Framework.WEIGHTED
            );

            System.out.println("\nPORTFOLIO ALLOCATION");
            System.out.println("Selected: " + result.selected());
            System.out.println("Deferred: " + result.deferred());

            System.out.printf(
                "Effort used: %.2f%n",
                result.effortUsed()
            );

            System.out.printf(
                "Budget used: %.2f%n",
                result.budgetUsed()
            );

            System.out.printf(
                "Remaining effort: %.2f%n",
                result.remainingEffort()
            );

            System.out.printf(
                "Remaining budget: %.2f%n",
                result.remainingBudget()
            );

            System.out.printf(
                "Business value: %.2f%n",
                result.businessValue()
            );

            System.out.printf(
                "Opportunity cost: %.2f%n",
                result.opportunityCost()
            );

            System.out.println("\nSENSITIVITY ANALYSIS");

            Map<Framework, Allocation> report =
                service.sensitivityAnalysis(capacity);

            report.forEach((framework, allocation) ->
                System.out.println(
                    framework + " -> " + allocation.selected()
                )
            );

            System.out.println(
                "\nAudit records: " + service.history().size()
            );

            runValidationTests();

        } catch (PrioritizationException exception) {
            System.err.println(
                "PRIORITIZATION ERROR: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
