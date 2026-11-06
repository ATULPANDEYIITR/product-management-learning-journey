import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Enterprise Product Roadmapping
 *
 * Domain-driven implementation covering:
 * strategic themes, outcomes, initiatives, prioritization,
 * dependency validation, governance, capacity and reporting.
 */
public class ProductRoadmap {

    enum Status {
        PROPOSED,
        APPROVED,
        PLANNED,
        IN_PROGRESS,
        BLOCKED,
        COMPLETED,
        CANCELLED
    }

    enum Decision {
        APPROVE,
        REJECT
    }

    static class RoadmapException extends RuntimeException {
        public RoadmapException(String message) {
            super(message);
        }
    }

    record Theme(
        String id,
        String name,
        String objective,
        String executiveSponsor
    ) {
        Theme {
            requireText(id, "Theme ID");
            requireText(name, "Theme name");
            requireText(objective, "Theme objective");
            requireText(executiveSponsor, "Executive sponsor");
        }
    }

    record Outcome(
        String id,
        String description,
        double baseline,
        double target,
        double current,
        String unit
    ) {
        Outcome {
            requireText(id, "Outcome ID");
            requireText(description, "Outcome description");
            requireText(unit, "Outcome unit");

            if (
                !Double.isFinite(baseline) ||
                !Double.isFinite(target) ||
                !Double.isFinite(current) ||
                baseline == target
            ) {
                throw new RoadmapException(
                    "Invalid outcome measurements."
                );
            }
        }

        double progress() {
            double value =
                (current - baseline) /
                (target - baseline) * 100.0;

            return Math.max(0, Math.min(100, value));
        }

        boolean achieved() {
            return target > baseline
                ? current >= target
                : current <= target;
        }
    }

    record InitiativeProposal(
        String id,
        String name,
        String themeId,
        String outcomeId,
        LocalDate start,
        LocalDate end,
        int effort,
        double impact,
        double confidence,
        double alignment,
        List<String> dependencies,
        String owner
    ) {
        InitiativeProposal {
            requireText(id, "Initiative ID");
            requireText(name, "Initiative name");
            requireText(themeId, "Theme ID");
            requireText(outcomeId, "Outcome ID");
            requireText(owner, "Owner");

            Objects.requireNonNull(start);
            Objects.requireNonNull(end);

            dependencies = List.copyOf(dependencies);

            if (start.isAfter(end) || effort <= 0) {
                throw new RoadmapException(
                    "Invalid initiative timeline or effort."
                );
            }

            validateScore(impact, "Impact");
            validateScore(confidence, "Confidence");
            validateScore(alignment, "Alignment");

            if (confidence > 1 || alignment > 1) {
                throw new RoadmapException(
                    "Confidence and alignment must be in [0,1]."
                );
            }

            if (new HashSet<>(dependencies).size()
                != dependencies.size()) {
                throw new RoadmapException(
                    "Duplicate dependencies."
                );
            }

            if (dependencies.contains(id)) {
                throw new RoadmapException(
                    "Self-dependency is prohibited."
                );
            }
        }
    }

    record ReviewDecision(
        String reviewer,
        String role,
        Decision decision,
        String justification
    ) {
        ReviewDecision {
            requireText(reviewer, "Reviewer");
            requireText(role, "Reviewer role");
            requireText(justification, "Justification");

            Objects.requireNonNull(decision);
        }
    }

    record InitiativeView(
        InitiativeProposal proposal,
        Status status,
        double priorityScore
    ) {}

    record CapacityResult(
        int sprintNumber,
        int allocatedEffort,
        int availableCapacity,
        boolean overloaded
    ) {}

    interface RoadmapPolicy {
        void validate(InitiativeProposal proposal);
    }

    static class EnterprisePolicy implements RoadmapPolicy {
        private final int maximumEffort;
        private final Set<String> permittedOwners;

        EnterprisePolicy(
            int maximumEffort,
            Set<String> permittedOwners
        ) {
            if (maximumEffort <= 0) {
                throw new RoadmapException(
                    "Maximum effort must be positive."
                );
            }

            this.maximumEffort = maximumEffort;
            this.permittedOwners = Set.copyOf(permittedOwners);
        }

        @Override
        public void validate(InitiativeProposal proposal) {
            if (proposal.effort() > maximumEffort) {
                throw new RoadmapException(
                    "Initiative exceeds enterprise effort limit."
                );
            }

            if (!permittedOwners.contains(proposal.owner())) {
                throw new RoadmapException(
                    "Initiative owner is not authorized."
                );
            }
        }
    }

    static class ManagedInitiative {
        private final InitiativeProposal proposal;
        private Status status;
        private final List<ReviewDecision> decisions =
            new ArrayList<>();

        ManagedInitiative(InitiativeProposal proposal) {
            this.proposal = proposal;
            this.status = Status.PROPOSED;
        }

        InitiativeProposal proposal() {
            return proposal;
        }

        Status status() {
            return status;
        }

        List<ReviewDecision> decisions() {
            return List.copyOf(decisions);
        }

        void addDecision(ReviewDecision decision) {
            if (status != Status.PROPOSED) {
                throw new RoadmapException(
                    "Decisions are accepted only for proposed initiatives."
                );
            }

            if (
                decisions.stream().anyMatch(
                    existing ->
                        existing.reviewer().equals(decision.reviewer())
                )
            ) {
                throw new RoadmapException(
                    "A reviewer may submit only one decision."
                );
            }

            decisions.add(decision);
        }

        void transition(Status next) {
            Map<Status, Set<Status>> allowed = Map.of(
                Status.PROPOSED, Set.of(
                    Status.APPROVED,
                    Status.CANCELLED
                ),
                Status.APPROVED, Set.of(
                    Status.PLANNED,
                    Status.CANCELLED
                ),
                Status.PLANNED, Set.of(
                    Status.IN_PROGRESS,
                    Status.BLOCKED,
                    Status.CANCELLED
                ),
                Status.IN_PROGRESS, Set.of(
                    Status.BLOCKED,
                    Status.COMPLETED,
                    Status.CANCELLED
                ),
                Status.BLOCKED, Set.of(
                    Status.PLANNED,
                    Status.IN_PROGRESS,
                    Status.CANCELLED
                ),
                Status.COMPLETED, Set.of(),
                Status.CANCELLED, Set.of()
            );

            if (!allowed.get(status).contains(next)) {
                throw new RoadmapException(
                    "Invalid transition: " + status + " -> " + next
                );
            }

            status = next;
        }
    }

    static class RoadmapService {
        private final String productName;
        private final LocalDate start;
        private final LocalDate end;
        private final int sprintCapacity;
        private final int requiredApprovals;

        private final RoadmapPolicy policy;

        private final Map<String, Theme> themes =
            new LinkedHashMap<>();

        private final Map<String, Outcome> outcomes =
            new LinkedHashMap<>();

        private final Map<String, ManagedInitiative> initiatives =
            new LinkedHashMap<>();

        RoadmapService(
            String productName,
            LocalDate start,
            LocalDate end,
            int sprintCapacity,
            int requiredApprovals,
            RoadmapPolicy policy
        ) {
            requireText(productName, "Product name");

            if (
                start.isAfter(end) ||
                sprintCapacity <= 0 ||
                requiredApprovals <= 0
            ) {
                throw new RoadmapException(
                    "Invalid roadmap configuration."
                );
            }

            this.productName = productName;
            this.start = start;
            this.end = end;
            this.sprintCapacity = sprintCapacity;
            this.requiredApprovals = requiredApprovals;
            this.policy = Objects.requireNonNull(policy);
        }

        void addTheme(Theme theme) {
            if (themes.putIfAbsent(theme.id(), theme) != null) {
                throw new RoadmapException("Duplicate theme.");
            }
        }

        void addOutcome(Outcome outcome) {
            if (outcomes.putIfAbsent(outcome.id(), outcome) != null) {
                throw new RoadmapException("Duplicate outcome.");
            }
        }

        void propose(InitiativeProposal proposal) {
            if (initiatives.containsKey(proposal.id())) {
                throw new RoadmapException(
                    "Duplicate initiative ID."
                );
            }

            if (!themes.containsKey(proposal.themeId())) {
                throw new RoadmapException(
                    "Unknown strategic theme."
                );
            }

            if (!outcomes.containsKey(proposal.outcomeId())) {
                throw new RoadmapException(
                    "Unknown outcome."
                );
            }

            if (
                proposal.start().isBefore(start) ||
                proposal.end().isAfter(end)
            ) {
                throw new RoadmapException(
                    "Initiative exceeds roadmap period."
                );
            }

            policy.validate(proposal);

            initiatives.put(
                proposal.id(),
                new ManagedInitiative(proposal)
            );
        }

        void submitDecision(
            String initiativeId,
            ReviewDecision decision
        ) {
            ManagedInitiative item = get(initiativeId);
            item.addDecision(decision);
        }

        void approve(String initiativeId) {
            ManagedInitiative item = get(initiativeId);

            long approvals = item.decisions().stream()
                .filter(d -> d.decision() == Decision.APPROVE)
                .count();

            long rejections = item.decisions().stream()
                .filter(d -> d.decision() == Decision.REJECT)
                .count();

            if (rejections > 0 || approvals < requiredApprovals) {
                throw new RoadmapException(
                    "Approval requirements are not satisfied."
                );
            }

            item.transition(Status.APPROVED);
        }

        void plan(String initiativeId) {
            get(initiativeId).transition(Status.PLANNED);
        }

        void startInitiative(String initiativeId) {
            ManagedInitiative item = get(initiativeId);

            validateDependencies();

            for (String dependency :
                item.proposal().dependencies()) {

                if (get(dependency).status() != Status.COMPLETED) {
                    throw new RoadmapException(
                        "Dependency not completed: " + dependency
                    );
                }
            }

            item.transition(Status.IN_PROGRESS);
        }

        void block(String initiativeId) {
            get(initiativeId).transition(Status.BLOCKED);
        }

        void complete(String initiativeId) {
            get(initiativeId).transition(Status.COMPLETED);
        }

        private ManagedInitiative get(String id) {
            ManagedInitiative item = initiatives.get(id);

            if (item == null) {
                throw new RoadmapException(
                    "Unknown initiative: " + id
                );
            }

            return item;
        }

        void validateDependencies() {
            Set<String> visited = new HashSet<>();
            Set<String> visiting = new HashSet<>();

            for (String id : initiatives.keySet()) {
                visit(id, visited, visiting);
            }

            for (ManagedInitiative item : initiatives.values()) {
                for (String dependency :
                    item.proposal().dependencies()) {

                    ManagedInitiative prerequisite = get(dependency);

                    if (
                        !prerequisite.proposal().end()
                            .isBefore(item.proposal().start())
                    ) {
                        throw new RoadmapException(
                            "Dependency timeline conflict: "
                            + item.proposal().id()
                        );
                    }
                }
            }
        }

        private void visit(
            String id,
            Set<String> visited,
            Set<String> visiting
        ) {
            if (visiting.contains(id)) {
                throw new RoadmapException(
                    "Dependency cycle detected."
                );
            }

            if (visited.contains(id)) return;

            ManagedInitiative item = get(id);
            visiting.add(id);

            for (String dependency :
                item.proposal().dependencies()) {
                visit(dependency, visited, visiting);
            }

            visiting.remove(id);
            visited.add(id);
        }

        double score(InitiativeProposal proposal) {
            return proposal.impact()
                * proposal.confidence()
                * proposal.alignment()
                / proposal.effort();
        }

        List<InitiativeView> prioritized() {
            return initiatives.values().stream()
                .map(item -> new InitiativeView(
                    item.proposal(),
                    item.status(),
                    score(item.proposal())
                ))
                .sorted(
                    Comparator.comparingDouble(
                        InitiativeView::priorityScore
                    ).reversed().thenComparing(
                        view -> view.proposal().id()
                    )
                )
                .toList();
        }

        List<InitiativeView> ready() {
            return initiatives.values().stream()
                .filter(item -> item.status() == Status.PLANNED)
                .filter(item ->
                    item.proposal().dependencies().stream()
                        .allMatch(id ->
                            get(id).status() == Status.COMPLETED
                        )
                )
                .map(item -> new InitiativeView(
                    item.proposal(),
                    item.status(),
                    score(item.proposal())
                ))
                .toList();
        }

        Map<Integer, CapacityResult> capacityReport() {
            Map<Integer, Integer> allocations = new HashMap<>();

            for (ManagedInitiative item : initiatives.values()) {
                if (
                    item.status() == Status.PROPOSED ||
                    item.status() == Status.CANCELLED
                ) {
                    continue;
                }

                InitiativeProposal p = item.proposal();

                int first = (int) ChronoUnit.DAYS.between(
                    start,
                    p.start()
                ) / 14;

                int last = (int) ChronoUnit.DAYS.between(
                    start,
                    p.end()
                ) / 14;

                for (int sprint = first; sprint <= last; sprint++) {
                    allocations.merge(
                        sprint,
                        p.effort(),
                        Integer::sum
                    );
                }
            }

            Map<Integer, CapacityResult> result =
                new java.util.TreeMap<>();

            allocations.forEach((sprint, effort) ->
                result.put(
                    sprint,
                    new CapacityResult(
                        sprint + 1,
                        effort,
                        Math.max(0, sprintCapacity - effort),
                        effort > sprintCapacity
                    )
                )
            );

            return result;
        }

        void printReport() {
            System.out.println("\nPRODUCT: " + productName);

            System.out.println("\nSTRATEGIC THEMES");

            themes.values().forEach(theme ->
                System.out.println(
                    theme.id() + " | " +
                    theme.name() + " | " +
                    theme.objective()
                )
            );

            System.out.println("\nPRIORITIZED INITIATIVES");

            prioritized().forEach(view ->
                System.out.printf(
                    "%s | %s | Score: %.3f | Status: %s%n",
                    view.proposal().id(),
                    view.proposal().name(),
                    view.priorityScore(),
                    view.status()
                )
            );

            System.out.println("\nOUTCOME MEASUREMENTS");

            outcomes.values().forEach(outcome ->
                System.out.printf(
                    "%s | Current: %.2f | Target: %.2f | "
                    + "Progress: %.2f%% | Achieved: %s%n",
                    outcome.id(),
                    outcome.current(),
                    outcome.target(),
                    outcome.progress(),
                    outcome.achieved()
                )
            );

            System.out.println("\nCAPACITY REPORT");

            capacityReport().values().forEach(capacity ->
                System.out.println(capacity)
            );
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new RoadmapException(field + " is required.");
        }
    }

    private static void validateScore(
        double value,
        String field
    ) {
        if (
            !Double.isFinite(value) ||
            value < 0 ||
            value > 10
        ) {
            throw new RoadmapException(
                field + " must be between 0 and 10."
            );
        }
    }

    public static void main(String[] args) {
        try {
            EnterprisePolicy policy = new EnterprisePolicy(
                50,
                Set.of("Platform Team", "Product Team")
            );

            RoadmapService roadmap = new RoadmapService(
                "Enterprise Commerce Platform",
                LocalDate.of(2027, 1, 1),
                LocalDate.of(2027, 3, 31),
                40,
                2,
                policy
            );

            roadmap.addTheme(new Theme(
                "T1",
                "Customer Experience",
                "Increase checkout conversion.",
                "Chief Product Officer"
            ));

            roadmap.addTheme(new Theme(
                "T2",
                "Platform Reliability",
                "Improve platform availability.",
                "Chief Technology Officer"
            ));

            roadmap.addOutcome(new Outcome(
                "O1",
                "Checkout completion rate",
                65,
                85,
                72,
                "%"
            ));

            roadmap.addOutcome(new Outcome(
                "O2",
                "Platform availability",
                99,
                99.9,
                99.5,
                "%"
            ));

            roadmap.propose(new InitiativeProposal(
                "I1",
                "Payment Infrastructure Upgrade",
                "T2",
                "O2",
                LocalDate.of(2027, 1, 1),
                LocalDate.of(2027, 1, 20),
                30,
                9,
                0.9,
                1.0,
                List.of(),
                "Platform Team"
            ));

            roadmap.propose(new InitiativeProposal(
                "I2",
                "Checkout Optimization",
                "T1",
                "O1",
                LocalDate.of(2027, 1, 21),
                LocalDate.of(2027, 2, 10),
                25,
                8,
                0.85,
                0.9,
                List.of("I1"),
                "Product Team"
            ));

            roadmap.propose(new InitiativeProposal(
                "I3",
                "One-Click Checkout",
                "T1",
                "O1",
                LocalDate.of(2027, 2, 11),
                LocalDate.of(2027, 3, 10),
                40,
                10,
                0.8,
                1.0,
                List.of("I2"),
                "Product Team"
            ));

            roadmap.validateDependencies();

            // Two independent enterprise decisions are required.
            for (String reviewer : List.of("Director Product", "Director Technology")) {
                roadmap.submitDecision(
                    "I1",
                    new ReviewDecision(
                        reviewer,
                        "Executive",
                        Decision.APPROVE,
                        "Strategic and technical assessment passed."
                    )
                );
            }

            roadmap.approve("I1");
            roadmap.plan("I1");
            roadmap.startInitiative("I1");
            roadmap.complete("I1");

            for (String reviewer : List.of("Product Manager", "Engineering Lead")) {
                roadmap.submitDecision(
                    "I2",
                    new ReviewDecision(
                        reviewer,
                        "Delivery Governance",
                        Decision.APPROVE,
                        "Business value and feasibility verified."
                    )
                );
            }

            roadmap.approve("I2");
            roadmap.plan("I2");
            roadmap.startInitiative("I2");

            roadmap.printReport();

            System.out.println("\nREADY INITIATIVES");

            roadmap.ready().forEach(item ->
                System.out.println(item.proposal().name())
            );

            // Invalid owner is rejected by enterprise policy.
            try {
                roadmap.propose(new InitiativeProposal(
                    "I4",
                    "Unauthorized Initiative",
                    "T1",
                    "O1",
                    LocalDate.of(2027, 3, 1),
                    LocalDate.of(2027, 3, 15),
                    10,
                    5,
                    0.8,
                    0.8,
                    List.of(),
                    "External Contractor"
                ));
            } catch (RoadmapException error) {
                System.out.println(
                    "\nEXPECTED GOVERNANCE ERROR: "
                    + error.getMessage()
                );
            }

        } catch (RoadmapException error) {
            System.err.println(
                "Roadmap execution failed: " + error.getMessage()
            );
            System.exit(1);
        }
    }
}
