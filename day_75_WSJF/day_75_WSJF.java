import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Enterprise WSJF prioritization and governance application.
 *
 * Cost of Delay = Business Value + Time Criticality + Risk Reduction
 * WSJF = Cost of Delay / Job Size
 *
 * Features:
 * - Immutable domain records
 * - Explicit business scoring
 * - Dependency management
 * - Enterprise prioritization policies
 * - State transition validation
 * - Capacity-aware scheduling
 * - Scenario evaluation
 * - Audit events
 * - Custom domain exceptions
 */

public class WSJFEnterprise {

    enum WorkStatus {
        BACKLOG,
        READY,
        IN_PROGRESS,
        BLOCKED,
        COMPLETED
    }

    enum AuditType {
        ITEM_CREATED,
        STATUS_CHANGED,
        POLICY_EVALUATED,
        ITEM_SCHEDULED
    }

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    static class ValidationException extends DomainException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class DependencyException extends DomainException {
        DependencyException(String message) {
            super(message);
        }
    }

    record Score(
        BigDecimal businessValue,
        BigDecimal timeCriticality,
        BigDecimal riskReduction,
        BigDecimal jobSize
    ) {
        Score {
            requireNonNegative(businessValue, "Business value");
            requireNonNegative(timeCriticality, "Time criticality");
            requireNonNegative(riskReduction, "Risk reduction");
            requirePositive(jobSize, "Job size");
        }

        private static void requireNonNegative(
            BigDecimal value,
            String name
        ) {
            if (value == null || value.signum() < 0) {
                throw new ValidationException(
                    name + " must be non-negative"
                );
            }
        }

        private static void requirePositive(
            BigDecimal value,
            String name
        ) {
            if (value == null || value.signum() <= 0) {
                throw new ValidationException(
                    name + " must be positive"
                );
            }
        }

        BigDecimal costOfDelay() {
            return businessValue
                .add(timeCriticality)
                .add(riskReduction);
        }

        BigDecimal wsjf() {
            return costOfDelay().divide(
                jobSize,
                6,
                RoundingMode.HALF_UP
            );
        }
    }

    record WorkItem(
        String id,
        String title,
        String owner,
        Score score,
        WorkStatus status,
        Set<String> dependencies,
        long version
    ) {
        WorkItem {
            if (id == null || id.isBlank()) {
                throw new ValidationException("ID is required");
            }

            if (title == null || title.isBlank()) {
                throw new ValidationException("Title is required");
            }

            if (owner == null || owner.isBlank()) {
                throw new ValidationException("Owner is required");
            }

            Objects.requireNonNull(score, "Score is required");
            Objects.requireNonNull(status, "Status is required");

            dependencies = Set.copyOf(dependencies);

            if (dependencies.contains(id)) {
                throw new DependencyException(
                    "Self-dependency is prohibited"
                );
            }

            if (version < 1) {
                throw new ValidationException("Invalid version");
            }
        }

        WorkItem withStatus(WorkStatus nextStatus) {
            return new WorkItem(
                id,
                title,
                owner,
                score,
                nextStatus,
                dependencies,
                version + 1
            );
        }
    }

    record RankedItem(
        WorkItem item,
        BigDecimal costOfDelay,
        BigDecimal wsjf
    ) {}

    record AuditEvent(
        String eventId,
        AuditType type,
        String itemId,
        String description,
        Instant timestamp
    ) {}

    record ScheduleResult(
        List<WorkItem> selected,
        BigDecimal usedCapacity,
        BigDecimal remainingCapacity
    ) {
        ScheduleResult {
            selected = List.copyOf(selected);
        }
    }

    record ScenarioResult(
        String itemId,
        BigDecimal originalWSJF,
        BigDecimal hypotheticalWSJF,
        BigDecimal difference
    ) {}

    interface EligibilityPolicy {
        List<String> evaluate(WorkItem item);
    }

    static final class EnterprisePolicy
        implements EligibilityPolicy {

        private final BigDecimal minimumBusinessValue;
        private final BigDecimal minimumRiskReduction;
        private final BigDecimal maximumJobSize;

        EnterprisePolicy(
            BigDecimal minimumBusinessValue,
            BigDecimal minimumRiskReduction,
            BigDecimal maximumJobSize
        ) {
            this.minimumBusinessValue = minimumBusinessValue;
            this.minimumRiskReduction = minimumRiskReduction;
            this.maximumJobSize = maximumJobSize;
        }

        @Override
        public List<String> evaluate(WorkItem item) {
            List<String> reasons = new ArrayList<>();

            if (item.status() != WorkStatus.READY) {
                reasons.add("Item is not READY");
            }

            if (item.score().businessValue()
                .compareTo(minimumBusinessValue) < 0) {
                reasons.add("Business value below policy threshold");
            }

            if (item.score().riskReduction()
                .compareTo(minimumRiskReduction) < 0) {
                reasons.add("Risk reduction below policy threshold");
            }

            if (item.score().jobSize()
                .compareTo(maximumJobSize) > 0) {
                reasons.add("Job size exceeds policy limit");
            }

            return List.copyOf(reasons);
        }
    }

    static final class AuditService {
        private final List<AuditEvent> events = new ArrayList<>();

        void record(
            AuditType type,
            String itemId,
            String description
        ) {
            events.add(new AuditEvent(
                UUID.randomUUID().toString(),
                type,
                itemId,
                description,
                Instant.now()
            ));
        }

        List<AuditEvent> events() {
            return List.copyOf(events);
        }
    }

    static final class WorkItemRepository {
        private final Map<String, WorkItem> items =
            new HashMap<>();

        WorkItem save(WorkItem item) {
            items.put(item.id(), item);
            return item;
        }

        WorkItem find(String id) {
            WorkItem item = items.get(id);

            if (item == null) {
                throw new ValidationException(
                    "Unknown work item: " + id
                );
            }

            return item;
        }

        List<WorkItem> findAll() {
            return List.copyOf(items.values());
        }

        boolean contains(String id) {
            return items.containsKey(id);
        }
    }

    static final class WSJFService {
        private final WorkItemRepository repository;
        private final EligibilityPolicy policy;
        private final AuditService audit;

        private static final Comparator<RankedItem> RANKING =
            Comparator
                .comparing(RankedItem::wsjf)
                .reversed()
                .thenComparing(
                    RankedItem::costOfDelay,
                    Comparator.reverseOrder()
                )
                .thenComparing(
                    ranked -> ranked.item().score().jobSize()
                )
                .thenComparing(ranked -> ranked.item().id());

        WSJFService(
            WorkItemRepository repository,
            EligibilityPolicy policy,
            AuditService audit
        ) {
            this.repository = repository;
            this.policy = policy;
            this.audit = audit;
        }

        void register(WorkItem item) {
            if (repository.contains(item.id())) {
                throw new ValidationException(
                    "Duplicate work-item ID: " + item.id()
                );
            }

            // Validate dependencies before committing the new item.
            for (String dependency : item.dependencies()) {
                if (!repository.contains(dependency)) {
                    throw new DependencyException(
                        "Missing dependency: " + dependency
                    );
                }
            }

            repository.save(item);

            try {
                validateGraph();
            } catch (RuntimeException error) {
                // Roll back the registration if graph validation fails.
                // Repository is intentionally private to this service.
                repository.items.remove(item.id());
                throw error;
            }

            audit.record(
                AuditType.ITEM_CREATED,
                item.id(),
                "Work item registered"
            );
        }

        private void validateGraph() {
            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();

            for (WorkItem item : repository.findAll()) {
                visit(item.id(), visiting, visited);
            }
        }

        private void visit(
            String id,
            Set<String> visiting,
            Set<String> visited
        ) {
            if (visiting.contains(id)) {
                throw new DependencyException(
                    "Dependency cycle detected at " + id
                );
            }

            if (visited.contains(id)) {
                return;
            }

            visiting.add(id);

            for (String dependency :
                repository.find(id).dependencies()) {
                visit(dependency, visiting, visited);
            }

            visiting.remove(id);
            visited.add(id);
        }

        List<RankedItem> ranking() {
            return repository.findAll().stream()
                .filter(item -> {
                    List<String> reasons = policy.evaluate(item);

                    audit.record(
                        AuditType.POLICY_EVALUATED,
                        item.id(),
                        reasons.isEmpty()
                            ? "Eligible"
                            : String.join("; ", reasons)
                    );

                    return reasons.isEmpty();
                })
                .map(item -> new RankedItem(
                    item,
                    item.score().costOfDelay(),
                    item.score().wsjf()
                ))
                .sorted(RANKING)
                .toList();
        }

        void transition(
            String itemId,
            WorkStatus nextStatus
        ) {
            WorkItem item = repository.find(itemId);

            Map<WorkStatus, Set<WorkStatus>> transitions =
                Map.of(
                    WorkStatus.BACKLOG,
                    Set.of(WorkStatus.READY, WorkStatus.BLOCKED),

                    WorkStatus.READY,
                    Set.of(
                        WorkStatus.BACKLOG,
                        WorkStatus.IN_PROGRESS,
                        WorkStatus.BLOCKED
                    ),

                    WorkStatus.IN_PROGRESS,
                    Set.of(
                        WorkStatus.READY,
                        WorkStatus.BLOCKED,
                        WorkStatus.COMPLETED
                    ),

                    WorkStatus.BLOCKED,
                    Set.of(WorkStatus.READY, WorkStatus.BACKLOG),

                    WorkStatus.COMPLETED,
                    Set.of()
                );

            if (!transitions.get(item.status()).contains(nextStatus)) {
                throw new DomainException(
                    "Invalid state transition"
                );
            }

            if (nextStatus == WorkStatus.READY) {
                for (String dependency : item.dependencies()) {
                    if (repository.find(dependency).status()
                        != WorkStatus.COMPLETED) {
                        throw new DependencyException(
                            "Incomplete dependency: " + dependency
                        );
                    }
                }
            }

            repository.save(item.withStatus(nextStatus));

            audit.record(
                AuditType.STATUS_CHANGED,
                itemId,
                item.status() + " -> " + nextStatus
            );
        }

        ScheduleResult schedule(BigDecimal capacity) {
            if (capacity == null || capacity.signum() < 0) {
                throw new ValidationException(
                    "Capacity must be non-negative"
                );
            }

            BigDecimal remaining = capacity;

            Set<String> completed = repository.findAll().stream()
                .filter(item -> item.status() == WorkStatus.COMPLETED)
                .map(WorkItem::id)
                .collect(Collectors.toSet());

            List<WorkItem> selected = new ArrayList<>();
            Set<String> selectedIds = new HashSet<>();

            List<RankedItem> candidates = ranking();

            boolean progress = true;

            while (progress) {
                progress = false;

                for (RankedItem ranked : candidates) {
                    WorkItem item = ranked.item();

                    if (selectedIds.contains(item.id())) {
                        continue;
                    }

                    if (item.score().jobSize().compareTo(remaining) > 0) {
                        continue;
                    }

                    boolean dependenciesReady =
                        completed.containsAll(item.dependencies());

                    if (!dependenciesReady) {
                        continue;
                    }

                    selected.add(item);
                    selectedIds.add(item.id());
                    completed.add(item.id());

                    remaining = remaining.subtract(
                        item.score().jobSize()
                    );

                    audit.record(
                        AuditType.ITEM_SCHEDULED,
                        item.id(),
                        "Selected for capacity plan"
                    );

                    progress = true;
                    break;
                }
            }

            return new ScheduleResult(
                selected,
                capacity.subtract(remaining),
                remaining
            );
        }

        ScenarioResult analyzeScenario(
            String id,
            BigDecimal businessChange,
            BigDecimal timeChange,
            BigDecimal riskChange,
            BigDecimal sizeChange
        ) {
            WorkItem item = repository.find(id);
            Score current = item.score();

            Score hypothetical = new Score(
                current.businessValue().add(businessChange),
                current.timeCriticality().add(timeChange),
                current.riskReduction().add(riskChange),
                current.jobSize().add(sizeChange)
            );

            BigDecimal original = current.wsjf();
            BigDecimal projected = hypothetical.wsjf();

            return new ScenarioResult(
                id,
                original,
                projected,
                projected.subtract(original)
            );
        }
    }

    private static BigDecimal decimal(String value) {
        return new BigDecimal(value);
    }

    private static WorkItem createItem(
        String id,
        String title,
        String owner,
        String businessValue,
        String timeCriticality,
        String riskReduction,
        String jobSize,
        Set<String> dependencies
    ) {
        return new WorkItem(
            id,
            title,
            owner,
            new Score(
                decimal(businessValue),
                decimal(timeCriticality),
                decimal(riskReduction),
                decimal(jobSize)
            ),
            WorkStatus.READY,
            dependencies,
            1
        );
    }

    public static void main(String[] args) {
        try {
            WorkItemRepository repository =
                new WorkItemRepository();

            AuditService audit = new AuditService();

            EligibilityPolicy policy = new EnterprisePolicy(
                decimal("3"),
                decimal("0"),
                decimal("20")
            );

            WSJFService service = new WSJFService(
                repository,
                policy,
                audit
            );

            service.register(createItem(
                "ENT-301",
                "Security vulnerability remediation",
                "Security Team",
                "9", "10", "10", "3",
                Set.of()
            ));

            service.register(createItem(
                "ENT-302",
                "Payment platform modernization",
                "Payments Team",
                "9", "10", "8", "5",
                Set.of()
            ));

            service.register(createItem(
                "ENT-303",
                "Database migration foundation",
                "Platform Team",
                "7", "6", "9", "5",
                Set.of()
            ));

            service.register(createItem(
                "ENT-304",
                "Automated regression testing",
                "Quality Team",
                "6", "7", "8", "3",
                Set.of("ENT-303")
            ));

            service.register(createItem(
                "ENT-305",
                "Customer analytics dashboard",
                "Data Team",
                "8", "5", "3", "8",
                Set.of()
            ));

            System.out.println("\nENTERPRISE WSJF RANKING");
            System.out.println(
                "ID\t\tCOST OF DELAY\tSIZE\tWSJF"
            );

            for (RankedItem ranked : service.ranking()) {
                System.out.println(
                    ranked.item().id() + "\t\t" +
                    ranked.costOfDelay() + "\t\t" +
                    ranked.item().score().jobSize() + "\t" +
                    ranked.wsjf()
                );
            }

            System.out.println("\nCAPACITY PLAN");

            ScheduleResult schedule =
                service.schedule(decimal("12"));

            for (int i = 0; i < schedule.selected().size(); i++) {
                WorkItem item = schedule.selected().get(i);

                System.out.println(
                    (i + 1) + ". " + item.id() +
                    " - " + item.title()
                );
            }

            System.out.println(
                "Used: " + schedule.usedCapacity()
            );

            System.out.println(
                "Remaining: " + schedule.remainingCapacity()
            );

            System.out.println("\nSCENARIO ANALYSIS");

            System.out.println(
                service.analyzeScenario(
                    "ENT-305",
                    decimal("3"),
                    decimal("2"),
                    decimal("0"),
                    decimal("0")
                )
            );

            System.out.println("\nDEPENDENCY STATE TRANSITION");

            service.transition(
                "ENT-303",
                WorkStatus.IN_PROGRESS
            );

            service.transition(
                "ENT-303",
                WorkStatus.COMPLETED
            );

            System.out.println(
                "Database migration completed."
            );

            System.out.println("\nAUDIT EVENTS");

            audit.events().forEach(event ->
                System.out.println(
                    event.timestamp() + " | " +
                    event.type() + " | " +
                    event.itemId() + " | " +
                    event.description()
                )
            );

            System.out.println("\nAUDIT EVENT COUNT: " +
                audit.events().size());

        } catch (DomainException error) {
            System.err.println(
                "Enterprise prioritization failure: " +
                error.getMessage()
            );

            System.exit(1);
        }
    }
}
