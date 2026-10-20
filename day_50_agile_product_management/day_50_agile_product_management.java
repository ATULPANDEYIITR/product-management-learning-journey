import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class AgileProductManagement {

    enum BacklogState {
        DISCOVERY,
        READY,
        IN_PROGRESS,
        DONE
    }

    enum Priority {
        CRITICAL(4),
        HIGH(3),
        MEDIUM(2),
        LOW(1);

        private final int weight;

        Priority(int weight) {
            this.weight = weight;
        }

        public int weight() {
            return weight;
        }
    }

    record ProductGoal(
            String id,
            String statement,
            String metric,
            double target,
            LocalDate deadline) {

        ProductGoal {
            requireText(id, "Product goal id");
            requireText(statement, "Product goal statement");
            requireText(metric, "Product goal metric");

            if (target < 0 || target > 1) {
                throw new ValidationException(
                        "Product goal target must be between 0 and 1");
            }

            Objects.requireNonNull(deadline, "Product goal deadline");
        }
    }

    record RoadmapOutcome(
            String id,
            String statement,
            LocalDate targetDate,
            String productGoalId) {

        RoadmapOutcome {
            requireText(id, "Roadmap outcome id");
            requireText(statement, "Roadmap outcome statement");
            requireText(productGoalId, "Product goal reference");
            Objects.requireNonNull(targetDate, "Roadmap target date");
        }
    }

    record BacklogItem(
            String id,
            String title,
            String customerProblem,
            int value,
            int effort,
            Priority priority,
            BacklogState state,
            Set<String> evidence) {

        BacklogItem {
            requireText(id, "Backlog item id");
            requireText(title, "Backlog title");
            requireText(customerProblem, "Customer problem");

            if (value < 1 || value > 100) {
                throw new ValidationException("Value must be between 1 and 100");
            }

            if (effort < 1 || effort > 100) {
                throw new ValidationException("Effort must be between 1 and 100");
            }

            Objects.requireNonNull(priority, "Priority");
            Objects.requireNonNull(state, "Backlog state");

            if (evidence == null || evidence.isEmpty()) {
                throw new ValidationException(
                        "Backlog item requires discovery evidence");
            }

            evidence = Set.copyOf(evidence);
        }

        double score() {
            return (double) value * priority.weight() / effort;
        }

        BacklogItem withState(BacklogState nextState) {
            return new BacklogItem(
                    id,
                    title,
                    customerProblem,
                    value,
                    effort,
                    priority,
                    nextState,
                    evidence);
        }
    }

    record SprintGoal(
            String sprintId,
            String statement,
            String productGoalId) {

        SprintGoal {
            requireText(sprintId, "Sprint id");
            requireText(statement, "Sprint goal");
            requireText(productGoalId, "Product goal id");
        }
    }

    static final class Sprint {
        private final SprintGoal goal;
        private final LocalDate start;
        private final LocalDate end;
        private final List<String> selectedItemIds = new ArrayList<>();

        Sprint(SprintGoal goal, LocalDate start, LocalDate end) {
            this.goal = Objects.requireNonNull(goal);
            this.start = Objects.requireNonNull(start);
            this.end = Objects.requireNonNull(end);

            if (start.isAfter(end)) {
                throw new ValidationException("Sprint start cannot exceed end");
            }
        }

        void select(String itemId) {
            if (selectedItemIds.contains(itemId)) {
                throw new ValidationException("Duplicate sprint item: " + itemId);
            }
            selectedItemIds.add(itemId);
        }

        List<String> selectedItems() {
            return List.copyOf(selectedItemIds);
        }

        SprintGoal goal() {
            return goal;
        }
    }

    record DiscoveryExperiment(
            String id,
            String hypothesis,
            String method,
            double threshold,
            List<Double> observations) {

        DiscoveryExperiment {
            requireText(id, "Experiment id");
            requireText(hypothesis, "Hypothesis");
            requireText(method, "Method");

            if (threshold < 0 || threshold > 1) {
                throw new ValidationException("Threshold must be between 0 and 1");
            }

            observations = observations == null
                    ? List.of()
                    : List.copyOf(observations);

            for (double observation : observations) {
                if (observation < 0 || observation > 1) {
                    throw new ValidationException(
                            "Observation must be between 0 and 1");
                }
            }
        }

        double result() {
            if (observations.isEmpty()) {
                return Double.NaN;
            }

            return observations.stream()
                    .mapToDouble(Double::doubleValue)
                    .average()
                    .orElse(Double.NaN);
        }

        boolean supportsHypothesis() {
            double result = result();
            return !Double.isNaN(result) && result >= threshold;
        }
    }

    static final class ProductGovernanceService {
        private final Map<String, ProductGoal> goals = new HashMap<>();
        private final Map<String, RoadmapOutcome> roadmap = new HashMap<>();
        private final Map<String, BacklogItem> backlog = new HashMap<>();
        private final Map<String, Sprint> sprints = new HashMap<>();
        private final Map<String, DiscoveryExperiment> experiments = new HashMap<>();
        private final EnumMap<BacklogState, Integer> stateCounts =
                new EnumMap<>(BacklogState.class);

        void addGoal(ProductGoal goal) {
            rejectDuplicate(goals, goal.id(), "product goal");
            goals.put(goal.id(), goal);
        }

        void addRoadmapOutcome(RoadmapOutcome outcome) {
            if (!goals.containsKey(outcome.productGoalId())) {
                throw new ValidationException(
                        "Roadmap outcome references unknown product goal");
            }

            rejectDuplicate(roadmap, outcome.id(), "roadmap outcome");
            roadmap.put(outcome.id(), outcome);
        }

        void addBacklogItem(BacklogItem item) {
            rejectDuplicate(backlog, item.id(), "backlog item");
            backlog.put(item.id(), item);
            incrementState(item.state());
        }

        void addExperiment(DiscoveryExperiment experiment) {
            rejectDuplicate(experiments, experiment.id(), "experiment");
            experiments.put(experiment.id(), experiment);
        }

        List<BacklogItem> prioritizedItems() {
            return backlog.values().stream()
                    .filter(item ->
                            item.state() == BacklogState.READY ||
                            item.state() == BacklogState.DISCOVERY)
                    .sorted(
                            Comparator.comparingDouble(BacklogItem::score)
                                    .reversed()
                                    .thenComparing(
                                            item -> item.priority().weight(),
                                            Comparator.reverseOrder()))
                    .toList();
        }

        void createSprint(
                SprintGoal goal,
                LocalDate start,
                LocalDate end,
                int capacity) {

            if (!goals.containsKey(goal.productGoalId())) {
                throw new ValidationException(
                        "Sprint must support an existing product goal");
            }

            if (capacity <= 0) {
                throw new ValidationException("Sprint capacity must be positive");
            }

            if (sprints.containsKey(goal.sprintId())) {
                throw new ValidationException("Duplicate sprint");
            }

            Sprint sprint = new Sprint(goal, start, end);
            int remaining = capacity;

            for (BacklogItem item : prioritizedItems()) {
                if (item.effort() <= remaining) {
                    transition(
                            item.id(),
                            BacklogState.IN_PROGRESS);
                    sprint.select(item.id());
                    remaining -= item.effort();
                }
            }

            if (sprint.selectedItems().isEmpty()) {
                throw new ValidationException(
                        "No backlog item fits sprint capacity");
            }

            sprints.put(goal.sprintId(), sprint);
        }

        void completeItem(String itemId, String sprintId) {
            Sprint sprint = sprints.get(sprintId);

            if (sprint == null) {
                throw new ValidationException("Unknown sprint");
            }

            if (!sprint.selectedItems().contains(itemId)) {
                throw new ValidationException(
                        "Item is not selected for this sprint");
            }

            transition(itemId, BacklogState.DONE);
        }

        boolean sprintIsOutcomeAligned(String sprintId) {
            Sprint sprint = sprints.get(sprintId);

            if (sprint == null) {
                return false;
            }

            ProductGoal productGoal =
                    goals.get(sprint.goal().productGoalId());

            if (productGoal == null) {
                return false;
            }

            return sprint.selectedItems().stream()
                    .map(backlog::get)
                    .filter(Objects::nonNull)
                    .allMatch(item ->
                            item.state() == BacklogState.DONE);
        }

        void printReport() {
            System.out.println("PRODUCT GOVERNANCE REPORT");
            System.out.println();

            System.out.println("Product goals: " + goals.size());
            System.out.println("Roadmap outcomes: " + roadmap.size());
            System.out.println("Backlog items: " + backlog.size());
            System.out.println("Sprints: " + sprints.size());
            System.out.println("Experiments: " + experiments.size());

            System.out.println("\nPrioritized backlog:");

            for (BacklogItem item : prioritizedItems()) {
                System.out.printf(
                        "%s | score=%.2f | priority=%s | state=%s%n",
                        item.id(),
                        item.score(),
                        item.priority(),
                        item.state());
            }

            System.out.println("\nDiscovery evidence:");

            for (DiscoveryExperiment experiment : experiments.values()) {
                String result = Double.isNaN(experiment.result())
                        ? "no observations"
                        : String.format("%.2f", experiment.result());

                System.out.printf(
                        "%s | result=%s | hypothesis=%s%n",
                        experiment.id(),
                        result,
                        experiment.supportsHypothesis()
                                ? "supported"
                                : "not supported");
            }
        }

        private void transition(String itemId, BacklogState nextState) {
            BacklogItem current = backlog.get(itemId);

            if (current == null) {
                throw new ValidationException("Unknown backlog item");
            }

            boolean valid = switch (current.state()) {
                case DISCOVERY ->
                        nextState == BacklogState.READY ||
                        nextState == BacklogState.IN_PROGRESS;
                case READY ->
                        nextState == BacklogState.IN_PROGRESS;
                case IN_PROGRESS ->
                        nextState == BacklogState.DONE;
                case DONE -> false;
            };

            if (!valid) {
                throw new ValidationException(
                        "Invalid transition: " +
                        current.state() + " -> " + nextState);
            }

            decrementState(current.state());
            BacklogItem updated = current.withState(nextState);
            backlog.put(itemId, updated);
            incrementState(nextState);
        }

        private void incrementState(BacklogState state) {
            stateCounts.merge(state, 1, Integer::sum);
        }

        private void decrementState(BacklogState state) {
            stateCounts.compute(
                    state,
                    (key, value) -> value == null || value <= 1 ? 0 : value - 1);
        }

        private static <K, V> void rejectDuplicate(
                Map<K, V> map,
                K key,
                String entity) {

            if (map.containsKey(key)) {
                throw new ValidationException("Duplicate " + entity + ": " + key);
            }
        }
    }

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new ValidationException(field + " cannot be blank");
        }
    }

    public static void main(String[] args) {
        ProductGovernanceService service =
                new ProductGovernanceService();

        ProductGoal goal = new ProductGoal(
                "PG-01",
                "Increase successful first-week activation.",
                "activation_rate",
                0.65,
                LocalDate.of(2027, 1, 18));

        service.addGoal(goal);

        service.addRoadmapOutcome(
                new RoadmapOutcome(
                        "RO-01",
                        "Reduce onboarding friction before first value.",
                        LocalDate.of(2026, 12, 4),
                        "PG-01"));

        service.addBacklogItem(
                new BacklogItem(
                        "PB-101",
                        "Simplify first-run setup",
                        "Users abandon setup before reaching first value.",
                        90,
                        8,
                        Priority.CRITICAL,
                        BacklogState.READY,
                        Set.of("funnel analysis", "interviews")));

        service.addBacklogItem(
                new BacklogItem(
                        "PB-102",
                        "Add contextual onboarding checklist",
                        "Users cannot identify their next useful action.",
                        82,
                        5,
                        Priority.HIGH,
                        BacklogState.READY,
                        Set.of("support tickets", "customer interviews")));

        service.addBacklogItem(
                new BacklogItem(
                        "PB-103",
                        "Improve recurring report navigation",
                        "Users spend too long finding recurring reports.",
                        65,
                        13,
                        Priority.MEDIUM,
                        BacklogState.READY,
                        Set.of("navigation analytics")));

        service.addExperiment(
                new DiscoveryExperiment(
                        "EXP-01",
                        "Guided setup improves first-value completion.",
                        "Prototype usability test",
                        0.70,
                        List.of(0.72, 0.76, 0.68, 0.74)));

        service.createSprint(
                new SprintGoal(
                        "SPR-01",
                        "Improve the path from account creation to first value.",
                        "PG-01"),
                LocalDate.of(2026, 10, 20),
                LocalDate.of(2026, 11, 2),
                13);

        service.printReport();

        service.completeItem("PB-101", "SPR-01");
        service.completeItem("PB-102", "SPR-01");

        System.out.println(
                "\nSprint outcome alignment: " +
                service.sprintIsOutcomeAligned("SPR-01"));
    }
}
