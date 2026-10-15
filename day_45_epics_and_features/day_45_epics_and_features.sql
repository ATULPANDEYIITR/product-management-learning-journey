import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/*
 * Enterprise product planning domain model.
 *
 * Java 17 implementation using records for immutable commands and events,
 * enums for constrained state values, domain objects for mutable lifecycle
 * state, and services for hierarchy, estimation, and release validation.
 */

public class EpicFeatureManagement {

    enum WorkType {
        EPIC, FEATURE, STORY, TASK
    }

    enum Status {
        BACKLOG, READY, IN_PROGRESS, BLOCKED, DONE, CANCELLED
    }

    enum Priority {
        LOW, MEDIUM, HIGH, CRITICAL
    }

    static final class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    record AcceptanceCriterion(String description) {
        AcceptanceCriterion {
            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Acceptance criterion cannot be blank."
                );
            }
            description = description.strip();
        }
    }

    record WorkCommand(
        String id,
        String title,
        WorkType type,
        String parentId,
        Priority priority,
        String owner,
        Double storyPoints,
        Double estimateHours,
        List<AcceptanceCriterion> criteria,
        Set<String> dependencyIds,
        LocalDate dueDate
    ) {
        WorkCommand {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("ID is required.");
            }
            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException("Title is required.");
            }

            Objects.requireNonNull(type, "Work type is required.");
            Objects.requireNonNull(priority, "Priority is required.");

            id = id.strip();
            title = title.strip();
            criteria = List.copyOf(criteria == null ? List.of() : criteria);
            dependencyIds = Set.copyOf(
                dependencyIds == null ? Set.of() : dependencyIds
            );

            if (storyPoints != null &&
                (!Double.isFinite(storyPoints) || storyPoints < 0)) {
                throw new IllegalArgumentException(
                    "Story points must be finite and non-negative."
                );
            }

            if (estimateHours != null &&
                (!Double.isFinite(estimateHours) || estimateHours < 0)) {
                throw new IllegalArgumentException(
                    "Task hours must be finite and non-negative."
                );
            }

            if (type != WorkType.STORY && storyPoints != null) {
                throw new IllegalArgumentException(
                    "Only stories may carry story points."
                );
            }

            if (type != WorkType.TASK && estimateHours != null) {
                throw new IllegalArgumentException(
                    "Only tasks may carry hour estimates."
                );
            }

            if (type == WorkType.STORY && criteria.isEmpty()) {
                throw new IllegalArgumentException(
                    "A story requires acceptance criteria."
                );
            }

            if (dependencyIds.contains(id)) {
                throw new IllegalArgumentException(
                    "A work item cannot depend on itself."
                );
            }
        }
    }

    record DomainEvent(
        long sequence,
        String itemId,
        String eventType,
        String detail
    ) {}

    record Progress(
        String unit,
        double total,
        double completed,
        double remaining,
        double percentComplete,
        int unestimatedStories
    ) {}

    record ReadinessReport(
        String epicId,
        boolean ready,
        List<String> unfinishedStories,
        List<String> blockedItems,
        List<String> missingOwners
    ) {
        ReadinessReport {
            unfinishedStories = List.copyOf(unfinishedStories);
            blockedItems = List.copyOf(blockedItems);
            missingOwners = List.copyOf(missingOwners);
        }
    }

    static final class WorkItem {
        private final String id;
        private final String title;
        private final WorkType type;
        private final String parentId;
        private final Priority priority;
        private final String owner;
        private final Double storyPoints;
        private final Double estimateHours;
        private final List<AcceptanceCriterion> criteria;
        private final Set<String> dependencyIds;
        private final LocalDate dueDate;

        private Status status = Status.BACKLOG;
        private long version = 1;

        WorkItem(WorkCommand command) {
            id = command.id();
            title = command.title();
            type = command.type();
            parentId = command.parentId();
            priority = command.priority();
            owner = command.owner();
            storyPoints = command.storyPoints();
            estimateHours = command.estimateHours();
            criteria = command.criteria();
            dependencyIds = command.dependencyIds();
            dueDate = command.dueDate();
        }

        String id() { return id; }
        String title() { return title; }
        WorkType type() { return type; }
        String parentId() { return parentId; }
        Priority priority() { return priority; }
        String owner() { return owner; }
        Double storyPoints() { return storyPoints; }
        Double estimateHours() { return estimateHours; }
        List<AcceptanceCriterion> criteria() { return criteria; }
        Set<String> dependencyIds() { return dependencyIds; }
        LocalDate dueDate() { return dueDate; }
        Status status() { return status; }
        long version() { return version; }

        void changeStatus(Status next) {
            status = next;
            version++;
        }
    }

    static final class ProductPortfolio {
        private final Map<String, WorkItem> items = new HashMap<>();
        private final Map<String, List<String>> children = new HashMap<>();
        private final List<DomainEvent> events = new ArrayList<>();
        private final AtomicLong eventSequence = new AtomicLong();

        private static final Map<WorkType, WorkType> REQUIRED_PARENT =
            Map.of(
                WorkType.FEATURE, WorkType.EPIC,
                WorkType.STORY, WorkType.FEATURE,
                WorkType.TASK, WorkType.STORY
            );

        private static final Map<Status, Set<Status>> TRANSITIONS =
            buildTransitions();

        private static Map<Status, Set<Status>> buildTransitions() {
            Map<Status, Set<Status>> transitions =
                new EnumMap<>(Status.class);

            transitions.put(
                Status.BACKLOG,
                Set.of(Status.READY, Status.CANCELLED)
            );
            transitions.put(
                Status.READY,
                Set.of(Status.IN_PROGRESS, Status.BLOCKED, Status.CANCELLED)
            );
            transitions.put(
                Status.IN_PROGRESS,
                Set.of(
                    Status.READY, Status.BLOCKED,
                    Status.DONE, Status.CANCELLED
                )
            );
            transitions.put(
                Status.BLOCKED,
                Set.of(Status.READY, Status.IN_PROGRESS, Status.CANCELLED)
            );
            transitions.put(Status.DONE, Set.of(Status.READY));
            transitions.put(Status.CANCELLED, Set.of(Status.BACKLOG));

            return Collections.unmodifiableMap(transitions);
        }

        void add(WorkCommand command) {
            if (items.containsKey(command.id())) {
                throw new DomainException(
                    "Duplicate work item: " + command.id()
                );
            }

            WorkType expectedParent = REQUIRED_PARENT.get(command.type());

            if (command.type() == WorkType.EPIC) {
                if (command.parentId() != null) {
                    throw new DomainException("An epic cannot have a parent.");
                }
            } else {
                if (command.parentId() == null) {
                    throw new DomainException(
                        command.type() + " requires a parent."
                    );
                }

                WorkItem parent = requireItem(command.parentId());
                if (parent.type() != expectedParent) {
                    throw new DomainException(
                        command.type() + " must be beneath " + expectedParent
                    );
                }
            }

            for (String dependencyId : command.dependencyIds()) {
                if (!items.containsKey(dependencyId)) {
                    throw new DomainException(
                        "Unknown dependency: " + dependencyId
                    );
                }
            }

            WorkItem item = new WorkItem(command);
            items.put(item.id(), item);

            try {
                validateDependencyGraph();
            } catch (RuntimeException exception) {
                items.remove(item.id());
                throw exception;
            }

            if (item.parentId() != null) {
                children.computeIfAbsent(
                    item.parentId(), ignored -> new ArrayList<>()
                ).add(item.id());
            }

            publish(item.id(), "CREATED", item.type().name());
        }

        private WorkItem requireItem(String id) {
            WorkItem item = items.get(id);
            if (item == null) {
                throw new DomainException("Unknown work item: " + id);
            }
            return item;
        }

        List<WorkItem> childrenOf(String parentId) {
            return children.getOrDefault(parentId, List.of())
                .stream()
                .map(this::requireItem)
                .sorted(Comparator.comparing(WorkItem::id))
                .toList();
        }

        List<WorkItem> descendantsOf(String rootId) {
            List<WorkItem> result = new ArrayList<>();
            List<String> stack = new ArrayList<>();

            childrenOf(rootId).stream()
                .map(WorkItem::id)
                .forEach(stack::add);

            while (!stack.isEmpty()) {
                String id = stack.remove(stack.size() - 1);
                WorkItem item = requireItem(id);
                result.add(item);

                childrenOf(id).stream()
                    .map(WorkItem::id)
                    .forEach(stack::add);
            }

            return result;
        }

        private void validateDependencyGraph() {
            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();

            for (String id : items.keySet()) {
                visit(id, visiting, visited);
            }
        }

        private void visit(
            String id,
            Set<String> visiting,
            Set<String> visited
        ) {
            if (visiting.contains(id)) {
                throw new DomainException(
                    "Dependency cycle detected at " + id
                );
            }

            if (!visited.add(id)) {
                return;
            }

            visiting.add(id);
            for (String dependencyId : requireItem(id).dependencyIds()) {
                visit(dependencyId, visiting, visited);
            }
            visiting.remove(id);
        }

        void transition(
            String id,
            Status next,
            long expectedVersion
        ) {
            WorkItem item = requireItem(id);

            // Version checks reject stale client commands before mutation.
            if (item.version() != expectedVersion) {
                throw new DomainException(
                    "Stale update for " + id +
                    ": expected version " + expectedVersion +
                    ", actual version " + item.version()
                );
            }

            if (item.status() == next) {
                return;
            }

            if (!TRANSITIONS.get(item.status()).contains(next)) {
                throw new DomainException(
                    "Invalid transition: " + item.status() + " -> " + next
                );
            }

            if (next == Status.IN_PROGRESS) {
                List<String> unmet = item.dependencyIds().stream()
                    .filter(dependencyId ->
                        requireItem(dependencyId).status() != Status.DONE
                    )
                    .toList();

                if (!unmet.isEmpty()) {
                    throw new DomainException(
                        "Incomplete dependencies: " + String.join(", ", unmet)
                    );
                }
            }

            if (next == Status.DONE) {
                List<WorkItem> nested = descendantsOf(id);

                if (item.type() == WorkType.STORY &&
                    childrenOf(id).stream().anyMatch(child ->
                        child.status() != Status.DONE &&
                        child.status() != Status.CANCELLED)) {
                    throw new DomainException(
                        "Story cannot complete with unfinished tasks."
                    );
                }

                if (item.type() == WorkType.EPIC ||
                    item.type() == WorkType.FEATURE) {
                    boolean unfinished = nested.stream().anyMatch(child ->
                        (child.type() == WorkType.STORY ||
                         child.type() == WorkType.TASK) &&
                        child.status() != Status.DONE &&
                        child.status() != Status.CANCELLED
                    );

                    if (unfinished) {
                        throw new DomainException(
                            "Aggregate work cannot complete before descendants."
                        );
                    }
                }
            }

            Status previous = item.status();
            item.changeStatus(next);
            publish(id, "STATUS_CHANGED", previous + " -> " + next);
        }

        private void publish(String itemId, String eventType, String detail) {
            events.add(new DomainEvent(
                eventSequence.incrementAndGet(),
                itemId,
                eventType,
                detail
            ));
        }

        Progress progress(String rootId) {
            List<WorkItem> stories = descendantsOf(rootId).stream()
                .filter(item -> item.type() == WorkType.STORY)
                .filter(item -> item.status() != Status.CANCELLED)
                .toList();

            List<WorkItem> estimated = stories.stream()
                .filter(item -> item.storyPoints() != null)
                .toList();

            int unestimated = stories.size() - estimated.size();

            if (!estimated.isEmpty()) {
                double total = estimated.stream()
                    .mapToDouble(item -> item.storyPoints())
                    .sum();

                double completed = estimated.stream()
                    .filter(item -> item.status() == Status.DONE)
                    .mapToDouble(item -> item.storyPoints())
                    .sum();

                return new Progress(
                    "story points",
                    total,
                    completed,
                    total - completed,
                    total == 0 ? 0 : completed / total * 100,
                    unestimated
                );
            }

            double totalHours = descendantsOf(rootId).stream()
                .filter(item -> item.type() == WorkType.TASK)
                .filter(item -> item.status() != Status.CANCELLED)
                .filter(item -> item.estimateHours() != null)
                .mapToDouble(item -> item.estimateHours())
                .sum();

            double completedHours = descendantsOf(rootId).stream()
                .filter(item -> item.type() == WorkType.TASK)
                .filter(item -> item.status() == Status.DONE)
                .filter(item -> item.estimateHours() != null)
                .mapToDouble(item -> item.estimateHours())
                .sum();

            return new Progress(
                "task hours",
                totalHours,
                completedHours,
                totalHours - completedHours,
                totalHours == 0 ? 0 : completedHours / totalHours * 100,
                stories.size()
            );
        }

        ReadinessReport readiness(String epicId) {
            WorkItem epic = requireItem(epicId);
            if (epic.type() != WorkType.EPIC) {
                throw new DomainException("Readiness requires an epic.");
            }

            List<WorkItem> descendants = descendantsOf(epicId);

            List<String> unfinishedStories = descendants.stream()
                .filter(item -> item.type() == WorkType.STORY)
                .filter(item -> item.status() != Status.DONE &&
                                item.status() != Status.CANCELLED)
                .map(WorkItem::id)
                .toList();

            List<String> blockedItems = descendants.stream()
                .filter(item -> item.status() == Status.BLOCKED)
                .map(WorkItem::id)
                .toList();

            List<String> missingOwners = descendants.stream()
                .filter(item -> item.type() == WorkType.STORY ||
                                item.type() == WorkType.TASK)
                .filter(item -> item.status() != Status.CANCELLED)
                .filter(item -> item.owner() == null ||
                                item.owner().isBlank())
                .map(WorkItem::id)
                .toList();

            boolean ready = unfinishedStories.isEmpty()
                && blockedItems.isEmpty()
                && missingOwners.isEmpty();

            return new ReadinessReport(
                epicId,
                ready,
                unfinishedStories,
                blockedItems,
                missingOwners
            );
        }

        List<DomainEvent> events() {
            return List.copyOf(events);
        }

        void printTree(String rootId, int depth) {
            WorkItem item = requireItem(rootId);

            System.out.printf(
                "%s%s [%s] %s (%s)%n",
                "  ".repeat(depth),
                item.id(),
                item.type(),
                item.title(),
                item.status()
            );

            for (WorkItem child : childrenOf(rootId)) {
                printTree(child.id(), depth + 1);
            }
        }
    }

    private static WorkCommand command(
        String id,
        String title,
        WorkType type,
        String parent,
        Priority priority,
        String owner,
        Double points,
        Double hours,
        List<String> criteria,
        Set<String> dependencies
    ) {
        return new WorkCommand(
            id,
            title,
            type,
            parent,
            priority,
            owner,
            points,
            hours,
            criteria.stream().map(AcceptanceCriterion::new).toList(),
            dependencies,
            LocalDate.of(2026, 12, 15)
        );
    }

    public static void main(String[] args) {
        ProductPortfolio portfolio = new ProductPortfolio();

        portfolio.add(command(
            "EP-400", "Enterprise Data Governance",
            WorkType.EPIC, null, Priority.CRITICAL, "Product Office",
            null, null, List.of(), Set.of()
        ));

        portfolio.add(command(
            "FE-410", "Data Quality Controls",
            WorkType.FEATURE, "EP-400", Priority.HIGH, "Data Platform",
            null, null, List.of(), Set.of()
        ));

        portfolio.add(command(
            "ST-411", "As a steward, I can define a validation rule",
            WorkType.STORY, "FE-410", Priority.HIGH, "Data Platform",
            5.0, null,
            List.of(
                "Rules identify null values in required fields",
                "Rule execution records failed-row counts"
            ),
            Set.of()
        ));

        portfolio.add(command(
            "TS-411A", "Implement rule configuration persistence",
            WorkType.TASK, "ST-411", Priority.HIGH, "Backend Team",
            null, 8.0, List.of(), Set.of()
        ));

        portfolio.add(command(
            "TS-411B", "Test rule evaluation against sample datasets",
            WorkType.TASK, "ST-411", Priority.MEDIUM, "Quality Engineering",
            null, 5.0, List.of(), Set.of("TS-411A")
        ));

        portfolio.add(command(
            "ST-412", "As a steward, I can inspect failed records",
            WorkType.STORY, "FE-410", Priority.MEDIUM, "Data Platform",
            8.0, null,
            List.of(
                "Failed records identify the violated rule",
                "Sensitive field values are masked in standard reports"
            ),
            Set.of()
        ));

        System.out.println("Enterprise delivery hierarchy");
        portfolio.printTree("EP-400", 0);

        System.out.println("\nInitial progress");
        System.out.println(portfolio.progress("EP-400"));

        try {
            portfolio.transition("TS-411B", Status.IN_PROGRESS, 1);
        } catch (DomainException exception) {
            System.out.println(
                "Expected dependency failure: " + exception.getMessage()
            );
        }

        portfolio.transition("TS-411A", Status.READY, 1);
        portfolio.transition("TS-411A", Status.IN_PROGRESS, 2);
        portfolio.transition("TS-411A", Status.DONE, 3);

        portfolio.transition("TS-411B", Status.READY, 1);
        portfolio.transition("TS-411B", Status.IN_PROGRESS, 2);
        portfolio.transition("TS-411B", Status.DONE, 3);

        portfolio.transition("ST-411", Status.READY, 1);
        portfolio.transition("ST-411", Status.IN_PROGRESS, 2);
        portfolio.transition("ST-411", Status.DONE, 3);

        try {
            portfolio.transition("ST-411", Status.READY, 1);
        } catch (DomainException exception) {
            System.out.println(
                "Expected stale-command failure: " + exception.getMessage()
            );
        }

        System.out.println("\nUpdated progress");
        System.out.println(portfolio.progress("EP-400"));

        System.out.println("\nRelease readiness");
        System.out.println(portfolio.readiness("EP-400"));

        System.out.println("\nRecorded domain events");
        portfolio.events().forEach(System.out::println);
    }
}
