import java.util.ArrayList;
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

public class ProductBacklogGovernance {

    enum WorkType {
        FEATURE, DEFECT, SECURITY, TECHNICAL_DEBT, SPIKE
    }

    enum Status {
        PROPOSED, REFINING, READY, IN_PROGRESS, BLOCKED, DONE, REJECTED
    }

    enum PriorityBand {
        CRITICAL, HIGH, MEDIUM, LOW
    }

    static final class BacklogException extends RuntimeException {
        BacklogException(String message) {
            super(message);
        }
    }

    static final class WorkItem {
        private final String id;
        private final WorkType type;
        private String title;
        private String description;
        private int businessValue;
        private int urgency;
        private int riskReduction;
        private int effort;
        private Status status = Status.PROPOSED;
        private final Set<String> dependencies = new HashSet<>();
        private final List<String> acceptanceCriteria = new ArrayList<>();
        private double debtPrincipal;
        private double debtInterestPerSprint;
        private long version = 1;

        WorkItem(
                String id,
                String title,
                WorkType type,
                String description,
                int businessValue,
                int urgency,
                int riskReduction,
                int effort
        ) {
            this.id = Objects.requireNonNull(id).trim().toUpperCase();
            this.title = Objects.requireNonNull(title).trim();
            this.type = Objects.requireNonNull(type);
            this.description = Objects.requireNonNull(description).trim();
            this.businessValue = businessValue;
            this.urgency = urgency;
            this.riskReduction = riskReduction;
            this.effort = effort;
            validate();
        }

        private void validate() {
            if (id.isBlank() || title.isBlank() || description.isBlank()) {
                throw new BacklogException("ID, title, and description are required.");
            }
            if (businessValue < 1 || businessValue > 10 ||
                    urgency < 1 || urgency > 10 ||
                    riskReduction < 1 || riskReduction > 10) {
                throw new BacklogException("Business scores must be between 1 and 10.");
            }
            if (effort < 1 || effort > 100) {
                throw new BacklogException("Effort must be between 1 and 100.");
            }
            if (debtPrincipal < 0 || debtInterestPerSprint < 0) {
                throw new BacklogException("Debt estimates cannot be negative.");
            }
        }

        WorkItem dependsOn(String dependencyId) {
            dependencies.add(dependencyId.toUpperCase());
            version++;
            return this;
        }

        WorkItem accepts(String criterion) {
            String normalized = Objects.requireNonNull(criterion).trim();
            if (normalized.isBlank()) {
                throw new BacklogException("Acceptance criteria cannot be blank.");
            }
            acceptanceCriteria.add(normalized);
            version++;
            return this;
        }

        WorkItem estimatesDebt(double principal, double interestPerSprint) {
            if (principal < 0 || interestPerSprint < 0) {
                throw new BacklogException("Debt estimates cannot be negative.");
            }
            debtPrincipal = principal;
            debtInterestPerSprint = interestPerSprint;
            version++;
            return this;
        }
    }

    record PriorityAssessment(
            String itemId,
            PriorityBand band,
            double score,
            int effort
    ) {}

    record DebtForecast(
            String itemId,
            double principal,
            double projectedInterest,
            double projectedCost
    ) {}

    record SprintPlan(
            List<String> itemIds,
            int effortUsed,
            int capacity
    ) {
        SprintPlan {
            itemIds = List.copyOf(itemIds);
        }
    }

    static final class BacklogRepository {
        private final Map<String, WorkItem> items = new LinkedHashMap<>();

        void add(WorkItem item) {
            if (items.containsKey(item.id)) {
                throw new BacklogException("Duplicate work item: " + item.id);
            }
            for (String dependency : item.dependencies) {
                if (!items.containsKey(dependency)) {
                    throw new BacklogException(
                            "Prerequisite must exist before dependent item: " + dependency
                    );
                }
            }
            items.put(item.id, item);
            try {
                validateAcyclic();
            } catch (RuntimeException error) {
                items.remove(item.id);
                throw error;
            }
        }

        WorkItem get(String id) {
            WorkItem item = items.get(id.toUpperCase());
            if (item == null) {
                throw new BacklogException("Unknown item: " + id);
            }
            return item;
        }

        List<WorkItem> all() {
            return List.copyOf(items.values());
        }

        private void validateAcyclic() {
            Set<String> visited = new HashSet<>();
            Set<String> active = new HashSet<>();
            for (String id : items.keySet()) {
                visit(id, visited, active);
            }
        }

        private void visit(
                String id,
                Set<String> visited,
                Set<String> active
        ) {
            if (active.contains(id)) {
                throw new BacklogException("Dependency cycle detected at " + id);
            }
            if (!visited.add(id)) return;

            active.add(id);
            for (String dependency : get(id).dependencies) {
                if (!items.containsKey(dependency)) {
                    throw new BacklogException("Unknown dependency: " + dependency);
                }
                visit(dependency, visited, active);
            }
            active.remove(id);
        }
    }

    static final class WorkflowService {
        private final BacklogRepository repository;

        private static final Map<Status, Set<Status>> TRANSITIONS =
                new EnumMap<>(Status.class);

        static {
            TRANSITIONS.put(Status.PROPOSED,
                    Set.of(Status.REFINING, Status.REJECTED));
            TRANSITIONS.put(Status.REFINING,
                    Set.of(Status.PROPOSED, Status.READY, Status.REJECTED));
            TRANSITIONS.put(Status.READY,
                    Set.of(Status.REFINING, Status.IN_PROGRESS, Status.REJECTED));
            TRANSITIONS.put(Status.IN_PROGRESS,
                    Set.of(Status.BLOCKED, Status.DONE, Status.READY));
            TRANSITIONS.put(Status.BLOCKED,
                    Set.of(Status.IN_PROGRESS, Status.READY));
            TRANSITIONS.put(Status.DONE, Set.of());
            TRANSITIONS.put(Status.REJECTED, Set.of(Status.REFINING));
        }

        WorkflowService(BacklogRepository repository) {
            this.repository = repository;
        }

        List<String> blockers(String id) {
            return repository.get(id).dependencies.stream()
                    .filter(dependency ->
                            repository.get(dependency).status != Status.DONE)
                    .sorted()
                    .toList();
        }

        void transition(String id, Status next) {
            WorkItem item = repository.get(id);
            if (!TRANSITIONS.get(item.status).contains(next)) {
                throw new BacklogException(
                        "Invalid transition " + item.status + " -> " + next
                );
            }
            if (next == Status.READY && item.acceptanceCriteria.isEmpty()) {
                throw new BacklogException("Ready work requires acceptance criteria.");
            }
            if ((next == Status.READY || next == Status.IN_PROGRESS) &&
                    !blockers(id).isEmpty()) {
                throw new BacklogException("Unfinished prerequisites prevent this transition.");
            }
            item.status = next;
            item.version++;
        }

        void refineDescription(String id, String description, long expectedVersion) {
            WorkItem item = repository.get(id);
            if (item.version != expectedVersion) {
                throw new BacklogException("Stale refinement version.");
            }
            if (item.status != Status.PROPOSED &&
                    item.status != Status.REFINING &&
                    item.status != Status.READY) {
                throw new BacklogException("Started work cannot be silently redefined.");
            }
            if (description == null || description.isBlank()) {
                throw new BacklogException("Refined description cannot be empty.");
            }
            item.description = description.trim();
            item.version++;
        }
    }

    static final class PrioritizationService {
        private final BacklogRepository repository;

        PrioritizationService(BacklogRepository repository) {
            this.repository = repository;
        }

        double score(WorkItem item) {
            double costOfDelay =
                    item.businessValue * 0.5 +
                    item.urgency * 0.3 +
                    item.riskReduction * 0.2;
            return costOfDelay / item.effort;
        }

        PriorityBand band(WorkItem item) {
            if ((item.type == WorkType.SECURITY || item.type == WorkType.DEFECT) &&
                    (item.urgency >= 9 || item.riskReduction >= 9)) {
                return PriorityBand.CRITICAL;
            }
            double score = score(item);
            if (score >= 3.5) return PriorityBand.HIGH;
            if (score >= 1.8) return PriorityBand.MEDIUM;
            return PriorityBand.LOW;
        }

        List<PriorityAssessment> assess() {
            return repository.all().stream()
                    .filter(item -> item.status != Status.DONE &&
                            item.status != Status.REJECTED)
                    .map(item -> new PriorityAssessment(
                            item.id, band(item), score(item), item.effort))
                    .sorted(Comparator
                            .comparing(PriorityAssessment::band)
                            .thenComparing(
                                    PriorityAssessment::score,
                                    Comparator.reverseOrder())
                            .thenComparing(PriorityAssessment::itemId))
                    .toList();
        }

        List<DebtForecast> forecastDebt(int sprints) {
            if (sprints < 0) {
                throw new BacklogException("Sprint horizon cannot be negative.");
            }
            return repository.all().stream()
                    .filter(item -> item.type == WorkType.TECHNICAL_DEBT)
                    .map(item -> {
                        double interest = item.debtInterestPerSprint * sprints;
                        return new DebtForecast(
                                item.id, item.debtPrincipal, interest,
                                item.debtPrincipal + interest);
                    })
                    .sorted(Comparator.comparingDouble(
                            DebtForecast::projectedCost).reversed())
                    .toList();
        }
    }

    static final class SprintPlanner {
        private final BacklogRepository repository;
        private final WorkflowService workflow;
        private final PrioritizationService prioritization;
        private final int capacity;

        SprintPlanner(
                BacklogRepository repository,
                WorkflowService workflow,
                PrioritizationService prioritization,
                int capacity
        ) {
            if (capacity < 1) throw new BacklogException("Capacity must be positive.");
            this.repository = repository;
            this.workflow = workflow;
            this.prioritization = prioritization;
            this.capacity = capacity;
        }

        SprintPlan plan() {
            Set<String> satisfied = repository.all().stream()
                    .filter(item -> item.status == Status.DONE)
                    .map(item -> item.id)
                    .collect(Collectors.toCollection(HashSet::new));

            List<String> selected = new ArrayList<>();
            int effortUsed = 0;
            boolean progress;

            do {
                progress = false;
                for (PriorityAssessment assessment : prioritization.assess()) {
                    WorkItem item = repository.get(assessment.itemId());
                    if (item.status != Status.READY || satisfied.contains(item.id)) continue;
                    if (effortUsed + item.effort > capacity) continue;
                    if (!item.dependencies.stream().allMatch(satisfied::contains)) continue;

                    selected.add(item.id);
                    satisfied.add(item.id);
                    effortUsed += item.effort;
                    progress = true;
                    break;
                }
            } while (progress);

            return new SprintPlan(selected, effortUsed, capacity);
        }
    }

    public static void main(String[] args) {
        BacklogRepository repository = new BacklogRepository();

        WorkItem foundation = new WorkItem(
                "CORE-401", "Establish tenant identity propagation",
                WorkType.FEATURE,
                "Propagate authenticated tenant identity across service boundaries.",
                9, 8, 9, 3
        ).accepts("Each request carries a verified tenant identity.")
         .accepts("Missing identity is rejected before business processing.");

        WorkItem audit = new WorkItem(
                "CORE-402", "Record security-sensitive changes",
                WorkType.FEATURE,
                "Create auditable events for privileged changes.",
                8, 7, 9, 4
        ).dependsOn("CORE-401")
         .accepts("Events identify the actor, action, and timestamp.")
         .accepts("Secrets and raw credentials are excluded.");

        WorkItem debt = new WorkItem(
                "CORE-403", "Remove repeated policy evaluation",
                WorkType.TECHNICAL_DEBT,
                "Cache safe policy inputs and eliminate repeated database reads.",
                7, 6, 8, 3
        ).estimatesDebt(15000, 1700)
         .accepts("Authorization outcomes remain identical.")
         .accepts("Repeated policy reads are measured in tests.");

        WorkItem security = new WorkItem(
                "CORE-404", "Fix cross-tenant data exposure",
                WorkType.SECURITY,
                "Apply tenant ownership predicates to every data retrieval path.",
                10, 10, 10, 2
        ).accepts("Cross-tenant retrieval is denied.")
         .accepts("Regression tests cover valid and invalid ownership.");

        repository.add(foundation);
        repository.add(audit);
        repository.add(debt);
        repository.add(security);

        WorkflowService workflow = new WorkflowService(repository);
        PrioritizationService prioritization = new PrioritizationService(repository);

        for (String id : List.of("CORE-401", "CORE-402", "CORE-403", "CORE-404")) {
            workflow.transition(id, Status.REFINING);
            if (id.equals("CORE-402")) continue;
            workflow.transition(id, Status.READY);
        }

        System.out.println("Enterprise product backlog");
        System.out.printf("%-12s %-10s %8s %8s%n",
                "Item", "Priority", "Score", "Effort");
        for (PriorityAssessment assessment : prioritization.assess()) {
            System.out.printf("%-12s %-10s %8.2f %8d%n",
                    assessment.itemId(),
                    assessment.band(),
                    assessment.score(),
                    assessment.effort());
        }

        System.out.println("\nPrerequisite validation");
        System.out.println("CORE-402 blockers: " + workflow.blockers("CORE-402"));
        try {
            workflow.transition("CORE-402", Status.READY);
        } catch (BacklogException error) {
            System.out.println("Rejected as expected: " + error.getMessage());
        }

        System.out.println("\nProjected technical debt");
        for (DebtForecast forecast : prioritization.forecastDebt(6)) {
            System.out.printf(
                    "%s: principal=%.2f, interest=%.2f, forecast=%.2f%n",
                    forecast.itemId(), forecast.principal(),
                    forecast.projectedInterest(), forecast.projectedCost());
        }

        System.out.println("\nSprint plan");
        SprintPlanner planner = new SprintPlanner(
                repository, workflow, prioritization, 10);
        SprintPlan plan = planner.plan();
        System.out.println("Selected items: " + plan.itemIds());
        System.out.println("Effort: " + plan.effortUsed() + "/" + plan.capacity());

        System.out.println("\nConcurrent refinement protection");
        WorkItem target = repository.get("CORE-402");
        long staleVersion = target.version;
        workflow.refineDescription(
                "CORE-402",
                "Record privileged configuration changes with a tamper-evident audit trail.",
                staleVersion);
        try {
            workflow.refineDescription(
                    "CORE-402", "Overwrite based on stale data.", staleVersion);
        } catch (BacklogException error) {
            System.out.println("Rejected as expected: " + error.getMessage());
        }

        System.out.println("\nAudit and backlog governance");
        System.out.println("Backlog items: " + repository.all().size());
        System.out.println("Stable item IDs support traceability across refinement.");
        System.out.println("Priority scores inform decisions but do not override security obligations.");
        System.out.println("Plan selection is capacity-aware and dependency-aware, not globally optimal.");
    }
}
