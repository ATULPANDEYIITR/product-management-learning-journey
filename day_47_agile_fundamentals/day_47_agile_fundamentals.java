import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/*
 * Agile Fundamentals: enterprise delivery governance model.
 *
 * Compile and run:
 *   javac AgileFundamentals.java
 *   java AgileFundamentals
 *
 * Java 17 or later; standard library only.
 *
 * The domain model separates product ownership, delivery work, acceptance,
 * iteration governance, and retrospective improvement.
 */

public class AgileFundamentals {

    enum WorkStatus {
        BACKLOG,
        READY,
        IN_PROGRESS,
        IN_REVIEW,
        TESTING,
        ACCEPTED,
        RELEASED,
        BLOCKED
    }

    enum WorkCategory {
        CUSTOMER_FEATURE,
        DEFECT,
        TECHNICAL_ENABLER,
        RESEARCH
    }

    enum IterationStatus {
        PLANNING,
        ACTIVE,
        COMPLETED
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
                    "Acceptance criterion cannot be empty."
                );
            }
        }
    }

    static final class WorkItem {
        private final String id;
        private final String title;
        private final String outcome;
        private final WorkCategory category;
        private final int points;
        private final int businessValue;
        private final List<AcceptanceCriterion> criteria;
        private final Set<String> dependencies;
        private final Map<String, Boolean> verification = new LinkedHashMap<>();
        private final List<String> audit = new ArrayList<>();

        private WorkStatus status = WorkStatus.BACKLOG;
        private String blocker;
        private String acceptedBy;
        private String releaseName;

        WorkItem(
            String id,
            String title,
            String outcome,
            WorkCategory category,
            int points,
            int businessValue,
            List<AcceptanceCriterion> criteria,
            Set<String> dependencies
        ) {
            if (id == null || id.isBlank() ||
                title == null || title.isBlank() ||
                outcome == null || outcome.isBlank()) {
                throw new IllegalArgumentException(
                    "Work item identity and outcome are required."
                );
            }
            if (points <= 0 || businessValue < 0) {
                throw new IllegalArgumentException(
                    "Points must be positive and business value non-negative."
                );
            }
            if (criteria == null || criteria.isEmpty()) {
                throw new IllegalArgumentException(
                    "A work item requires acceptance criteria."
                );
            }

            this.id = id;
            this.title = title;
            this.outcome = outcome;
            this.category = Objects.requireNonNull(category);
            this.points = points;
            this.businessValue = businessValue;
            this.criteria = List.copyOf(criteria);
            this.dependencies = Set.copyOf(dependencies);

            for (AcceptanceCriterion criterion : this.criteria) {
                verification.put(criterion.description(), false);
            }
            audit("created");
        }

        private void audit(String event) {
            audit.add(Instant.now() + " | " + event);
        }

        public String id() {
            return id;
        }

        public String title() {
            return title;
        }

        public int points() {
            return points;
        }

        public int businessValue() {
            return businessValue;
        }

        public WorkStatus status() {
            return status;
        }

        public String outcome() {
            return outcome;
        }

        public WorkCategory category() {
            return category;
        }

        public List<AcceptanceCriterion> criteria() {
            return criteria;
        }

        public Set<String> dependencies() {
            return dependencies;
        }

        public List<String> auditTrail() {
            return Collections.unmodifiableList(audit);
        }

        public double valuePerPoint() {
            return (double) businessValue / points;
        }

        void transition(WorkStatus target, boolean dependenciesReleased) {
            Set<WorkStatus> allowed = switch (status) {
                case BACKLOG -> EnumSet.of(WorkStatus.READY);
                case READY -> EnumSet.of(WorkStatus.IN_PROGRESS);
                case IN_PROGRESS -> EnumSet.of(
                    WorkStatus.IN_REVIEW, WorkStatus.BLOCKED
                );
                case IN_REVIEW -> EnumSet.of(
                    WorkStatus.TESTING, WorkStatus.IN_PROGRESS,
                    WorkStatus.BLOCKED
                );
                case TESTING -> EnumSet.of(
                    WorkStatus.ACCEPTED, WorkStatus.IN_PROGRESS,
                    WorkStatus.BLOCKED
                );
                case ACCEPTED -> EnumSet.of(WorkStatus.RELEASED);
                case BLOCKED -> EnumSet.of(WorkStatus.IN_PROGRESS);
                case RELEASED -> EnumSet.noneOf(WorkStatus.class);
            };

            if (!allowed.contains(target)) {
                throw new DomainException(
                    "Invalid transition for " + id + ": " +
                    status + " -> " + target
                );
            }

            if (target == WorkStatus.ACCEPTED) {
                if (verification.values().stream().anyMatch(value -> !value)) {
                    throw new DomainException(
                        "All acceptance criteria must be verified."
                    );
                }
                if (!dependenciesReleased) {
                    throw new DomainException(
                        "Dependencies must be released before acceptance."
                    );
                }
                if (acceptedBy == null) {
                    throw new DomainException(
                        "A named acceptance authority is required."
                    );
                }
            }

            if (target == WorkStatus.BLOCKED &&
                (blocker == null || blocker.isBlank())) {
                throw new DomainException(
                    "Blocked work requires a recorded reason."
                );
            }

            WorkStatus previous = status;
            status = target;
            audit(previous + " -> " + target);
        }

        void verifyCriterion(String description) {
            if (!verification.containsKey(description)) {
                throw new DomainException(
                    "Unknown acceptance criterion: " + description
                );
            }
            verification.put(description, true);
            audit("criterion verified: " + description);
        }

        void setBlocker(String reason) {
            if (reason == null || reason.isBlank()) {
                throw new IllegalArgumentException(
                    "Blocker reason cannot be empty."
                );
            }
            blocker = reason;
            audit("blocked: " + reason);
        }

        void clearBlocker() {
            blocker = null;
            audit("blocker cleared");
        }

        void designateAcceptanceAuthority(String stakeholder) {
            if (stakeholder == null || stakeholder.isBlank()) {
                throw new IllegalArgumentException(
                    "Acceptance authority must be named."
                );
            }
            acceptedBy = stakeholder;
        }

        void release(String name) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Release name cannot be empty."
                );
            }
            releaseName = name;
            audit("release: " + name);
        }

        String releaseName() {
            return releaseName;
        }
    }

    record TeamMember(String name, double availableDays, double focusFactor) {
        TeamMember {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Team member name is required."
                );
            }
            if (availableDays < 0 || focusFactor <= 0 || focusFactor > 1) {
                throw new IllegalArgumentException(
                    "Invalid availability or focus factor."
                );
            }
        }

        double effectiveDays() {
            return availableDays * focusFactor;
        }
    }

    static final class ProductBacklog {
        private final Map<String, WorkItem> items = new LinkedHashMap<>();

        void add(WorkItem item) {
            Objects.requireNonNull(item);
            if (items.putIfAbsent(item.id(), item) != null) {
                throw new DomainException(
                    "Duplicate work item: " + item.id()
                );
            }
        }

        WorkItem get(String id) {
            WorkItem item = items.get(id);
            if (item == null) {
                throw new DomainException("Unknown work item: " + id);
            }
            return item;
        }

        List<WorkItem> prioritized() {
            return items.values().stream()
                .filter(item ->
                    item.status() == WorkStatus.BACKLOG ||
                    item.status() == WorkStatus.READY
                )
                .sorted((left, right) ->
                    Double.compare(
                        right.valuePerPoint(),
                        left.valuePerPoint()
                    )
                )
                .toList();
        }

        boolean dependenciesReleased(WorkItem item) {
            return item.dependencies().stream()
                .allMatch(dependency -> get(dependency).status() ==
                    WorkStatus.RELEASED);
        }

        List<WorkItem> allItems() {
            return List.copyOf(items.values());
        }
    }

    static final class Iteration {
        private final String name;
        private final String goal;
        private final int durationDays;
        private final ProductBacklog backlog;
        private final List<WorkItem> committed = new ArrayList<>();
        private IterationStatus status = IterationStatus.PLANNING;

        Iteration(
            String name,
            String goal,
            int durationDays,
            ProductBacklog backlog
        ) {
            if (name == null || name.isBlank() ||
                goal == null || goal.isBlank() || durationDays <= 0) {
                throw new IllegalArgumentException(
                    "Iteration requires a name, goal, and duration."
                );
            }
            this.name = name;
            this.goal = goal;
            this.durationDays = durationDays;
            this.backlog = Objects.requireNonNull(backlog);
        }

        void plan(List<String> itemIds, int pointBudget) {
            if (status != IterationStatus.PLANNING) {
                throw new DomainException(
                    "Iteration is no longer open for planning."
                );
            }
            if (itemIds.isEmpty() ||
                itemIds.size() != itemIds.stream().distinct().count()) {
                throw new DomainException(
                    "Select unique work items for the iteration."
                );
            }

            List<WorkItem> selected = itemIds.stream()
                .map(backlog::get)
                .toList();

            int total = selected.stream().mapToInt(WorkItem::points).sum();
            if (total > pointBudget) {
                throw new DomainException(
                    "Planned points exceed the point budget."
                );
            }

            for (WorkItem item : selected) {
                if (item.status() != WorkStatus.READY) {
                    throw new DomainException(
                        item.id() + " is not ready for planning."
                    );
                }
                if (!backlog.dependenciesReleased(item)) {
                    throw new DomainException(
                        item.id() + " has incomplete dependencies."
                    );
                }
            }

            committed.addAll(selected);
        }

        void start() {
            if (status != IterationStatus.PLANNING || committed.isEmpty()) {
                throw new DomainException(
                    "Only a populated planned iteration can start."
                );
            }
            status = IterationStatus.ACTIVE;
        }

        void begin(String id) {
            requireActive();
            WorkItem item = committedItem(id);
            item.transition(WorkStatus.IN_PROGRESS, true);
        }

        void submitForReview(String id) {
            requireActive();
            committedItem(id).transition(WorkStatus.IN_REVIEW, true);
        }

        void startTesting(String id) {
            requireActive();
            committedItem(id).transition(WorkStatus.TESTING, true);
        }

        void accept(String id, String stakeholder) {
            requireActive();
            WorkItem item = committedItem(id);
            item.designateAcceptanceAuthority(stakeholder);
            item.transition(
                WorkStatus.ACCEPTED,
                backlog.dependenciesReleased(item)
            );
        }

        void release(String id, String releaseName) {
            requireActive();
            WorkItem item = committedItem(id);
            item.transition(WorkStatus.RELEASED, true);
            item.release(releaseName);
        }

        void block(String id, String reason) {
            requireActive();
            WorkItem item = committedItem(id);
            item.setBlocker(reason);
            item.transition(WorkStatus.BLOCKED, true);
        }

        void unblock(String id) {
            requireActive();
            WorkItem item = committedItem(id);
            item.clearBlocker();
            item.transition(WorkStatus.IN_PROGRESS, true);
        }

        int finish() {
            requireActive();
            status = IterationStatus.COMPLETED;
            return committed.stream()
                .filter(item -> item.status() == WorkStatus.RELEASED)
                .mapToInt(WorkItem::points)
                .sum();
        }

        private void requireActive() {
            if (status != IterationStatus.ACTIVE) {
                throw new DomainException("Iteration is not active.");
            }
        }

        private WorkItem committedItem(String id) {
            return committed.stream()
                .filter(item -> item.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new DomainException(
                    id + " is not committed to " + name
                ));
        }

        String report() {
            int plannedPoints = committed.stream()
                .mapToInt(WorkItem::points)
                .sum();
            int releasedPoints = committed.stream()
                .filter(item -> item.status() == WorkStatus.RELEASED)
                .mapToInt(WorkItem::points)
                .sum();
            String unfinished = committed.stream()
                .filter(item -> item.status() != WorkStatus.RELEASED)
                .map(WorkItem::id)
                .collect(Collectors.joining(", "));

            return "Iteration: " + name +
                "\nGoal: " + goal +
                "\nDuration: " + durationDays + " days" +
                "\nStatus: " + status +
                "\nPlanned points: " + plannedPoints +
                "\nReleased points: " + releasedPoints +
                "\nUnfinished work: " +
                (unfinished.isEmpty() ? "none" : unfinished);
        }
    }

    record ImprovementAction(
        String description,
        String owner,
        String successMeasure
    ) {
        ImprovementAction {
            if (description == null || description.isBlank() ||
                owner == null || owner.isBlank() ||
                successMeasure == null || successMeasure.isBlank()) {
                throw new IllegalArgumentException(
                    "Improvement action needs a description, owner, and measure."
                );
            }
        }
    }

    static final class Retrospective {
        private final List<String> evidence = new ArrayList<>();
        private final List<ImprovementAction> actions = new ArrayList<>();

        void recordObservation(String observation) {
            if (observation == null || observation.isBlank()) {
                throw new IllegalArgumentException(
                    "Retrospective observations require evidence."
                );
            }
            evidence.add(observation);
        }

        void addAction(ImprovementAction action) {
            actions.add(Objects.requireNonNull(action));
        }

        void print() {
            System.out.println("Evidence:");
            evidence.forEach(value -> System.out.println("- " + value));
            System.out.println("Improvement actions:");
            actions.forEach(action ->
                System.out.println(
                    "- " + action.description() +
                    " | owner: " + action.owner() +
                    " | measure: " + action.successMeasure()
                )
            );
        }
    }

    private static WorkItem item(
        String id,
        String title,
        int points,
        int value,
        List<String> criteria,
        Set<String> dependencies
    ) {
        return new WorkItem(
            id,
            title,
            "Improve the citizen service portal.",
            WorkCategory.CUSTOMER_FEATURE,
            points,
            value,
            criteria.stream().map(AcceptanceCriterion::new).toList(),
            dependencies
        );
    }

    public static void main(String[] args) {
        ProductBacklog backlog = new ProductBacklog();

        WorkItem signIn = item(
            "PORTAL-301",
            "Secure citizen sign-in",
            5,
            90,
            List.of(
                "Valid credentials establish a session",
                "Invalid credentials are rejected"
            ),
            Set.of()
        );

        WorkItem statusView = item(
            "PORTAL-302",
            "Request status display",
            3,
            75,
            List.of(
                "Current request status is visible",
                "Keyboard users can navigate the page"
            ),
            Set.of("PORTAL-301")
        );

        WorkItem retryProtection = item(
            "PORTAL-303",
            "Duplicate submission protection",
            3,
            95,
            List.of(
                "Repeated request identifiers do not duplicate records",
                "Distinct request identifiers remain independent"
            ),
            Set.of()
        );

        backlog.add(signIn);
        backlog.add(statusView);
        backlog.add(retryProtection);

        signIn.transition(WorkStatus.READY, true);
        statusView.transition(WorkStatus.READY, false);
        retryProtection.transition(WorkStatus.READY, true);

        List<TeamMember> members = List.of(
            new TeamMember("Maya", 8, 0.80),
            new TeamMember("Arjun", 8, 0.75),
            new TeamMember("Nisha", 6, 0.80)
        );

        double effectiveCapacity = members.stream()
            .mapToDouble(TeamMember::effectiveDays)
            .sum();

        System.out.println("AGILE ENTERPRISE DELIVERY MODEL");
        System.out.printf(
            "Effective working-day capacity: %.1f%n",
            effectiveCapacity
        );

        System.out.println("\nPrioritized backlog:");
        backlog.prioritized().forEach(work ->
            System.out.printf(
                "%s | %s | %d points | value/point %.2f%n",
                work.id(),
                work.title(),
                work.points(),
                work.valuePerPoint()
            )
        );

        Iteration iteration = new Iteration(
            "Iteration A",
            "Ship secure sign-in and reliable submission.",
            10,
            backlog
        );

        iteration.plan(List.of("PORTAL-301", "PORTAL-303"), 8);
        iteration.start();

        iteration.begin("PORTAL-301");
        iteration.submitForReview("PORTAL-301");
        iteration.startTesting("PORTAL-301");

        try {
            iteration.accept("PORTAL-301", "Product Owner");
        } catch (DomainException error) {
            System.out.println(
                "\nAcceptance guard correctly rejected incomplete evidence: " +
                error.getMessage()
            );
        }

        signIn.verifyCriterion("Valid credentials establish a session");
        signIn.verifyCriterion("Invalid credentials are rejected");
        iteration.accept("PORTAL-301", "Product Owner");
        iteration.release("PORTAL-301", "portal-2026.10-a");

        iteration.begin("PORTAL-303");
        iteration.block(
            "PORTAL-303",
            "Integration environment drops repeated request identifiers."
        );
        System.out.println(
            "Operational blocker recorded in the work item audit trail."
        );
        iteration.unblock("PORTAL-303");
        iteration.submitForReview("PORTAL-303");
        iteration.startTesting("PORTAL-303");
        retryProtection.verifyCriterion(
            "Repeated request identifiers do not duplicate records"
        );
        retryProtection.verifyCriterion(
            "Distinct request identifiers remain independent"
        );
        iteration.accept("PORTAL-303", "Service Operations");
        iteration.release("PORTAL-303", "portal-2026.10-a");

        System.out.println("\nIteration report:");
        System.out.println(iteration.report());

        Iteration nextIteration = new Iteration(
            "Iteration B",
            "Expose request progress to citizens.",
            10,
            backlog
        );
        nextIteration.plan(List.of("PORTAL-302"), 3);

        Retrospective retrospective = new Retrospective();
        retrospective.recordObservation(
            "The invalid-credential acceptance check exposed a security gap."
        );
        retrospective.addAction(new ImprovementAction(
            "Run both authentication criteria in continuous integration.",
            "Maya",
            "Every proposed increment passes both authentication checks."
        ));

        System.out.println("\nRetrospective:");
        retrospective.print();

        System.out.println("\nNext iteration is planned after dependency release.");
        System.out.println(
            "Audit entries for authentication: " + signIn.auditTrail().size()
        );
    }
}
