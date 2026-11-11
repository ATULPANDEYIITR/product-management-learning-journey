import java.util.*;
import java.util.stream.Collectors;

/**
 * MoSCoW Enterprise Requirements Prioritization.
 *
 * Java version: 17
 *
 * Features:
 * - Immutable requirement identity.
 * - Explicit priority and status domain types.
 * - Dependency graph validation.
 * - Priority decision history.
 * - Release capacity evaluation.
 * - Policy-based validation.
 * - Enterprise reporting.
 * - Automated tests.
 */
public class MoSCoWPrioritization {

    enum Priority {
        MUST_HAVE("Must-have"),
        SHOULD_HAVE("Should-have"),
        COULD_HAVE("Could-have"),
        WONT_HAVE("Won't-have");

        private final String label;

        Priority(String label) {
            this.label = label;
        }

        public String label() {
            return label;
        }
    }

    enum Status {
        PROPOSED,
        APPROVED,
        IN_PROGRESS,
        COMPLETED,
        DEFERRED
    }

    record Requirement(
        String id,
        String title,
        String description,
        Priority priority,
        int businessValue,
        int effort,
        String owner,
        List<String> dependencies,
        Status status
    ) {
        Requirement {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Requirement ID is mandatory."
                );
            }

            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException(
                    "Requirement title is mandatory."
                );
            }

            Objects.requireNonNull(priority);
            Objects.requireNonNull(status);

            if (businessValue < 1 || businessValue > 10) {
                throw new IllegalArgumentException(
                    "Business value must be between 1 and 10."
                );
            }

            if (effort < 1 || effort > 100) {
                throw new IllegalArgumentException(
                    "Effort must be between 1 and 100."
                );
            }

            if (owner == null || owner.isBlank()) {
                throw new IllegalArgumentException(
                    "Requirement owner is mandatory."
                );
            }

            dependencies = List.copyOf(dependencies);

            if (new HashSet<>(dependencies).size()
                != dependencies.size()) {
                throw new IllegalArgumentException(
                    "Duplicate dependencies are prohibited."
                );
            }

            if (dependencies.contains(id)) {
                throw new IllegalArgumentException(
                    "Self-dependency is prohibited."
                );
            }
        }

        double valueEffortRatio() {
            return (double) businessValue / effort;
        }

        Requirement withPriority(Priority newPriority) {
            return new Requirement(
                id, title, description, newPriority,
                businessValue, effort, owner,
                dependencies, status
            );
        }

        Requirement withStatus(Status newStatus) {
            return new Requirement(
                id, title, description, priority,
                businessValue, effort, owner,
                dependencies, newStatus
            );
        }
    }

    record PriorityDecision(
        String requirementId,
        Priority oldPriority,
        Priority newPriority,
        String actor,
        String reason,
        Date timestamp
    ) {}

    record ReleasePlan(
        List<Requirement> selected,
        int remainingCapacity,
        boolean mandatoryShortfall
    ) {
        ReleasePlan {
            selected = List.copyOf(selected);
        }
    }

    interface RequirementPolicy {
        void validate(Requirement requirement);
    }

    static class StandardRequirementPolicy
        implements RequirementPolicy {

        @Override
        public void validate(Requirement requirement) {
            if (requirement.priority() == Priority.WONT_HAVE &&
                requirement.status() == Status.IN_PROGRESS) {
                throw new IllegalArgumentException(
                    "Won't-have requirements cannot be in progress."
                );
            }
        }
    }

    static class PrioritizationService {

        private final Map<String, Requirement> requirements =
            new LinkedHashMap<>();

        private final List<PriorityDecision> history =
            new ArrayList<>();

        private final RequirementPolicy policy;

        PrioritizationService(RequirementPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public void add(Requirement requirement) {
            policy.validate(requirement);

            if (requirements.containsKey(requirement.id())) {
                throw new IllegalArgumentException(
                    "Duplicate requirement ID."
                );
            }

            requirements.put(requirement.id(), requirement);

            try {
                validateDependencyGraph();
            } catch (RuntimeException exception) {
                requirements.remove(requirement.id());
                throw exception;
            }
        }

        public Requirement get(String id) {
            Requirement requirement = requirements.get(id);

            if (requirement == null) {
                throw new NoSuchElementException(
                    "Requirement not found: " + id
                );
            }

            return requirement;
        }

        public void changePriority(
            String id,
            Priority newPriority,
            String actor,
            String reason
        ) {
            Requirement current = get(id);

            Objects.requireNonNull(newPriority);

            if (actor == null || actor.isBlank() ||
                reason == null || reason.isBlank()) {
                throw new IllegalArgumentException(
                    "Actor and reason are required."
                );
            }

            if (current.priority() == newPriority) return;

            Requirement updated =
                current.withPriority(newPriority);

            policy.validate(updated);

            requirements.put(id, updated);

            history.add(new PriorityDecision(
                id,
                current.priority(),
                newPriority,
                actor,
                reason,
                new Date()
            ));
        }

        public void changeStatus(String id, Status newStatus) {
            Requirement current = get(id);

            Requirement updated = current.withStatus(
                Objects.requireNonNull(newStatus)
            );

            policy.validate(updated);

            requirements.put(id, updated);
        }

        private void validateDependencyGraph() {
            for (Requirement requirement : requirements.values()) {
                for (String dependency :
                    requirement.dependencies()) {
                    if (!requirements.containsKey(dependency)) {
                        throw new IllegalArgumentException(
                            "Unknown dependency: " + dependency
                        );
                    }
                }
            }

            Set<String> visited = new HashSet<>();
            Set<String> active = new HashSet<>();

            for (String id : requirements.keySet()) {
                visit(id, visited, active);
            }
        }

        private void visit(
            String id,
            Set<String> visited,
            Set<String> active
        ) {
            if (active.contains(id)) {
                throw new IllegalArgumentException(
                    "Circular dependency detected."
                );
            }

            if (visited.contains(id)) return;

            active.add(id);

            for (String dependency :
                get(id).dependencies()) {
                visit(dependency, visited, active);
            }

            active.remove(id);
            visited.add(id);
        }

        public boolean dependenciesReady(String id) {
            return get(id).dependencies().stream()
                .allMatch(dependency ->
                    get(dependency).status() == Status.COMPLETED
                );
        }

        public ReleasePlan evaluateRelease(int capacity) {
            if (capacity < 0) {
                throw new IllegalArgumentException(
                    "Capacity cannot be negative."
                );
            }

            List<Requirement> mandatory =
                requirements.values().stream()
                    .filter(r -> r.priority() == Priority.MUST_HAVE)
                    .filter(r -> r.status() != Status.COMPLETED)
                    .sorted(Comparator.comparing(Requirement::id))
                    .toList();

            List<Requirement> optional =
                requirements.values().stream()
                    .filter(r -> r.priority() != Priority.MUST_HAVE)
                    .filter(r -> r.priority() != Priority.WONT_HAVE)
                    .filter(r -> r.status() != Status.COMPLETED)
                    .sorted(
                        Comparator.comparingDouble(
                            Requirement::valueEffortRatio
                        ).reversed()
                        .thenComparing(Requirement::id)
                    )
                    .toList();

            int mandatoryEffort = mandatory.stream()
                .mapToInt(Requirement::effort)
                .sum();

            int remaining = capacity;

            List<Requirement> selected = new ArrayList<>();
            Set<String> selectedIds = new HashSet<>();

            List<Requirement> candidates = new ArrayList<>();
            candidates.addAll(mandatory);
            candidates.addAll(optional);

            for (Requirement requirement : candidates) {

                boolean dependenciesReady =
                    requirement.dependencies().stream().allMatch(
                        dependency ->
                            selectedIds.contains(dependency) ||
                            get(dependency).status() == Status.COMPLETED
                    );

                if (dependenciesReady &&
                    requirement.effort() <= remaining) {
                    selected.add(requirement);
                    selectedIds.add(requirement.id());
                    remaining -= requirement.effort();
                }
            }

            return new ReleasePlan(
                selected,
                remaining,
                mandatoryEffort > capacity
            );
        }

        public Map<Priority, Long> categoryCounts() {
            return Arrays.stream(Priority.values())
                .collect(Collectors.toMap(
                    priority -> priority,
                    priority -> requirements.values().stream()
                        .filter(r -> r.priority() == priority)
                        .count(),
                    (a, b) -> a,
                    () -> new EnumMap<>(Priority.class)
                ));
        }

        public List<PriorityDecision> history() {
            return List.copyOf(history);
        }

        public Collection<Requirement> all() {
            return List.copyOf(requirements.values());
        }
    }

    private static Requirement create(
        String id,
        String title,
        Priority priority,
        int value,
        int effort,
        String owner,
        String... dependencies
    ) {
        return new Requirement(
            id,
            title,
            "Requirement for the current product release.",
            priority,
            value,
            effort,
            owner,
            List.of(dependencies),
            Status.PROPOSED
        );
    }

    private static void runTests() {
        PrioritizationService service =
            new PrioritizationService(
                new StandardRequirementPolicy()
            );

        service.add(create(
            "T001", "Authentication",
            Priority.MUST_HAVE, 10, 8, "Security"
        ));

        service.add(create(
            "T002", "Payment Processing",
            Priority.MUST_HAVE, 10, 13, "Payments",
            "T001"
        ));

        if (service.all().size() != 2) {
            throw new AssertionError("Registration failed.");
        }

        if (service.dependenciesReady("T002")) {
            throw new AssertionError("Dependency test failed.");
        }

        service.changeStatus("T001", Status.COMPLETED);

        if (!service.dependenciesReady("T002")) {
            throw new AssertionError("Completion test failed.");
        }

        service.changePriority(
            "T002",
            Priority.SHOULD_HAVE,
            "Product Owner",
            "Scope reassessment."
        );

        if (service.history().size() != 1) {
            throw new AssertionError("History test failed.");
        }

        try {
            service.add(create(
                "T003", "Invalid cycle",
                Priority.COULD_HAVE, 5, 3, "Engineering",
                "T003"
            ));
            throw new AssertionError("Cycle was accepted.");
        } catch (IllegalArgumentException expected) {
            // Expected validation result.
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {

        PrioritizationService service =
            new PrioritizationService(
                new StandardRequirementPolicy()
            );

        service.add(create(
            "R001", "User Authentication",
            Priority.MUST_HAVE, 10, 8, "Security Team"
        ));

        service.add(create(
            "R002", "Payment Processing",
            Priority.MUST_HAVE, 10, 13, "Payments Team",
            "R001"
        ));

        service.add(create(
            "R003", "Audit Logging",
            Priority.MUST_HAVE, 9, 5, "Platform Team"
        ));

        service.add(create(
            "R004", "Business Analytics",
            Priority.SHOULD_HAVE, 8, 8, "Analytics Team"
        ));

        service.add(create(
            "R005", "Email Notifications",
            Priority.SHOULD_HAVE, 7, 5, "Communications Team"
        ));

        service.add(create(
            "R006", "Custom Themes",
            Priority.COULD_HAVE, 4, 3, "Frontend Team"
        ));

        service.add(create(
            "R007", "Animated Backgrounds",
            Priority.WONT_HAVE, 2, 5, "Frontend Team"
        ));

        System.out.println("\nMOSCOW REQUIREMENTS REPORT");

        service.categoryCounts().forEach(
            (priority, count) ->
                System.out.println(
                    priority.label() + ": " + count
                )
        );

        ReleasePlan plan = service.evaluateRelease(30);

        System.out.println("\nRELEASE PLAN");

        plan.selected().forEach(requirement ->
            System.out.printf(
                "%s | %s | %s | Effort: %d%n",
                requirement.id(),
                requirement.title(),
                requirement.priority().label(),
                requirement.effort()
            )
        );

        System.out.println(
            "Remaining capacity: " + plan.remainingCapacity()
        );

        System.out.println(
            "Mandatory shortfall: " + plan.mandatoryShortfall()
        );

        runTests();
    }
}
