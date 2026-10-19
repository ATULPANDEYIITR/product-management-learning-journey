import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

public class KanbanEnterpriseModel {

    enum Stage {
        BACKLOG,
        READY,
        DEVELOPMENT,
        REVIEW,
        TESTING,
        DONE
    }

    enum Priority {
        EXPEDITED(0),
        HIGH(1),
        NORMAL(2),
        LOW(3);

        private final int rank;

        Priority(int rank) {
            this.rank = rank;
        }

        int rank() {
            return rank;
        }
    }

    record Transition(Stage from, Stage to, Instant at) {}

    static final class WorkItem {
        private final String key;
        private final String service;
        private final Priority priority;
        private final Instant createdAt;
        private Instant startedAt;
        private Instant completedAt;
        private Stage stage;
        private final List<Transition> history = new ArrayList<>();

        WorkItem(
                String key,
                String service,
                Priority priority,
                Instant createdAt,
                Stage initialStage
        ) {
            this.key = Objects.requireNonNull(key);
            this.service = Objects.requireNonNull(service);
            this.priority = Objects.requireNonNull(priority);
            this.createdAt = Objects.requireNonNull(createdAt);
            this.stage = Objects.requireNonNull(initialStage);
            history.add(new Transition(initialStage, initialStage, createdAt));
        }

        String key() {
            return key;
        }

        String service() {
            return service;
        }

        Priority priority() {
            return priority;
        }

        Instant createdAt() {
            return createdAt;
        }

        Instant startedAt() {
            return startedAt;
        }

        Instant completedAt() {
            return completedAt;
        }

        Stage stage() {
            return stage;
        }

        List<Transition> history() {
            return List.copyOf(history);
        }

        void transition(Stage destination, Instant at) {
            if (stage == destination) {
                return;
            }

            Stage previous = stage;
            stage = destination;
            history.add(new Transition(previous, destination, at));

            if (startedAt == null &&
                    destination == Stage.DEVELOPMENT) {
                startedAt = at;
            }

            if (destination == Stage.DONE) {
                completedAt = at;
            }
        }
    }

    static final class WipPolicy {
        private final Map<Stage, Integer> limits =
                new EnumMap<>(Stage.class);

        void setLimit(Stage stage, int limit) {
            if (limit < 1) {
                throw new IllegalArgumentException(
                        "WIP limit must be positive"
                );
            }
            limits.put(stage, limit);
        }

        boolean permits(Stage stage, long currentCount) {
            Integer limit = limits.get(stage);
            return limit == null || currentCount < limit;
        }

        Optional<Integer> limit(Stage stage) {
            return Optional.ofNullable(limits.get(stage));
        }
    }

    static final class KanbanBoard {
        private final Map<String, WorkItem> items = new HashMap<>();
        private final WipPolicy policy;

        KanbanBoard(WipPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        void add(WorkItem item) {
            if (items.putIfAbsent(item.key(), item) != null) {
                throw new IllegalArgumentException(
                        "Duplicate work item: " + item.key()
                );
            }
        }

        long count(Stage stage) {
            return items.values()
                    .stream()
                    .filter(item -> item.stage() == stage)
                    .count();
        }

        boolean move(String key, Stage destination, Instant at) {
            WorkItem item = items.get(key);

            if (item == null) {
                throw new IllegalArgumentException(
                        "Unknown work item: " + key
                );
            }

            if (!policy.permits(destination, count(destination))) {
                System.out.println(
                        "BLOCKED " + key + ": " +
                        destination + " reached its WIP limit"
                );
                return false;
            }

            item.transition(destination, at);

            System.out.println(
                    "FLOW " + key + " -> " + destination
            );

            return true;
        }

        Optional<WorkItem> pull(
                Stage source,
                Stage destination,
                Instant at
        ) {
            if (!policy.permits(destination, count(destination))) {
                return Optional.empty();
            }

            return items.values()
                    .stream()
                    .filter(item -> item.stage() == source)
                    .sorted(
                            Comparator
                                    .comparingInt(
                                            (WorkItem item) ->
                                                    item.priority().rank()
                                    )
                                    .thenComparing(
                                            WorkItem::createdAt
                                    )
                    )
                    .findFirst()
                    .filter(item -> move(
                            item.key(),
                            destination,
                            at
                    ))
                    .map(item -> item);
        }

        Map<Stage, Long> snapshot() {
            Map<Stage, Long> result =
                    new EnumMap<>(Stage.class);

            for (Stage stage : Stage.values()) {
                result.put(stage, count(stage));
            }

            return result;
        }

        List<WorkItem> completed() {
            return items.values()
                    .stream()
                    .filter(item -> item.stage() == Stage.DONE)
                    .toList();
        }
    }

    interface FlowMetric {
        double calculate(List<WorkItem> items);
    }

    static final class AverageCycleTime
            implements FlowMetric {

        @Override
        public double calculate(List<WorkItem> items) {
            List<Long> seconds = items.stream()
                    .filter(item ->
                            item.startedAt() != null &&
                            item.completedAt() != null)
                    .map(item ->
                            Duration.between(
                                    item.startedAt(),
                                    item.completedAt()
                            ).toSeconds())
                    .toList();

            if (seconds.isEmpty()) {
                return 0.0;
            }

            return seconds.stream()
                    .mapToLong(Long::longValue)
                    .average()
                    .orElse(0.0) / 3600.0;
        }
    }

    static double littleLaw(
            double averageWip,
            double throughputPerDay
    ) {
        if (averageWip < 0 || throughputPerDay <= 0) {
            throw new IllegalArgumentException(
                    "Invalid Little's Law inputs"
            );
        }

        return averageWip / throughputPerDay;
    }

    private static WorkItem item(
            String key,
            String service,
            Priority priority,
            Instant created
    ) {
        return new WorkItem(
                key,
                service,
                priority,
                created,
                Stage.READY
        );
    }

    public static void main(String[] args) {
        WipPolicy policy = new WipPolicy();
        policy.setLimit(Stage.DEVELOPMENT, 3);
        policy.setLimit(Stage.REVIEW, 1);
        policy.setLimit(Stage.TESTING, 2);

        KanbanBoard board = new KanbanBoard(policy);
        Instant base = Instant.parse(
                "2026-10-19T04:00:00Z"
        );

        board.add(item(
                "ORD-1001",
                "Order Processing",
                Priority.HIGH,
                base.minusSeconds(86_400 * 4)
        ));

        board.add(item(
                "ORD-1002",
                "Order Processing",
                Priority.NORMAL,
                base.minusSeconds(86_400 * 3)
        ));

        board.add(item(
                "PAY-2001",
                "Payments",
                Priority.EXPEDITED,
                base.minusSeconds(86_400 * 2)
        ));

        board.add(item(
                "OBS-3001",
                "Observability",
                Priority.NORMAL,
                base.minusSeconds(86_400)
        ));

        board.add(item(
                "SEC-4001",
                "Security",
                Priority.HIGH,
                base.minusSeconds(43_200)
        ));

        System.out.println("Initial board");
        System.out.println(board.snapshot());

        Instant developmentTime = base;

        board.pull(
                Stage.READY,
                Stage.DEVELOPMENT,
                developmentTime
        );

        board.pull(
                Stage.READY,
                Stage.DEVELOPMENT,
                developmentTime.plusSeconds(1800)
        );

        board.pull(
                Stage.READY,
                Stage.DEVELOPMENT,
                developmentTime.plusSeconds(3600)
        );

        // Development is intentionally full. Starting another item would
        // increase local activity without increasing delivery capacity.
        board.pull(
                Stage.READY,
                Stage.DEVELOPMENT,
                developmentTime.plusSeconds(5400)
        );

        // Review has a tighter limit than Development, deliberately creating
        // a bottleneck that can propagate backward into the pull system.
        Optional<WorkItem> reviewItem = board.pull(
                Stage.DEVELOPMENT,
                Stage.REVIEW,
                developmentTime.plusSeconds(7200)
        );

        if (reviewItem.isPresent()) {
            WorkItem item = reviewItem.get();

            board.move(
                    item.key(),
                    Stage.TESTING,
                    developmentTime.plusSeconds(10_800)
            );

            board.move(
                    item.key(),
                    Stage.DONE,
                    developmentTime.plusSeconds(14_400)
            );
        }

        // Once downstream capacity exists, another development item can be
        // pulled rather than being started before capacity becomes available.
        board.pull(
                Stage.READY,
                Stage.DEVELOPMENT,
                developmentTime.plusSeconds(15_000)
        );

        System.out.println("\nCurrent board");
        System.out.println(board.snapshot());

        FlowMetric cycleMetric = new AverageCycleTime();
        System.out.printf(
                "Average completed cycle time: %.2f hours%n",
                cycleMetric.calculate(board.completed())
        );

        System.out.printf(
                "Little's Law estimate: %.2f days%n",
                littleLaw(5.0, 2.0)
        );

        System.out.println("\nCompleted work");
        for (WorkItem completed : board.completed()) {
            System.out.printf(
                    "%s | %s | %s%n",
                    completed.key(),
                    completed.service(),
                    completed.stage()
            );
        }

        System.out.println("\nPolicy distinctions");
        System.out.println(
                "The board models WIP limits as capacity constraints."
        );
        System.out.println(
                "Pull selection chooses eligible work only when "
                        + "the destination has capacity."
        );
        System.out.println(
                "Cycle time begins when work enters Development and "
                        + "ends when it reaches Done."
        );
        System.out.println(
                "Throughput concerns completed items rather than "
                        + "items merely started."
        );
    }
}
