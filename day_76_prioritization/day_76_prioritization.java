import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Advanced Enterprise Opportunity Prioritization System
 *
 * Java 17 engineering perspective:
 * - Immutable domain records
 * - Enterprise scoring policies
 * - Strategic and economic evaluation
 * - Explicit lifecycle transitions
 * - Dependency validation
 * - Approval and portfolio allocation
 * - Decision audit history
 * - Sensitivity analysis
 * - Deterministic reporting
 *
 * Run:
 * javac AdvancedPrioritization.java
 * java AdvancedPrioritization
 */

public class AdvancedPrioritization {

    enum Status {
        PROPOSED,
        EVALUATED,
        APPROVED,
        DEFERRED,
        REJECTED
    }

    enum Tier {
        CRITICAL,
        HIGH,
        MEDIUM,
        LOW
    }

    enum DecisionType {
        CREATED,
        EVALUATED,
        APPROVED,
        DEFERRED,
        REJECTED
    }

    static class PrioritizationException
            extends RuntimeException {

        PrioritizationException(String message) {
            super(message);
        }
    }

    static class ValidationException
            extends PrioritizationException {

        ValidationException(String message) {
            super(message);
        }
    }

    static class DependencyException
            extends PrioritizationException {

        DependencyException(String message) {
            super(message);
        }
    }

    record Weights(
        double strategicFit,
        double economicValue,
        double customerValue,
        double urgency,
        double feasibility,
        double riskAdjustment
    ) {
        Weights {
            double[] values = {
                strategicFit,
                economicValue,
                customerValue,
                urgency,
                feasibility,
                riskAdjustment
            };

            double sum = 0;

            for (double value : values) {
                if (!Double.isFinite(value) || value < 0) {
                    throw new ValidationException(
                        "Weights must be finite and non-negative."
                    );
                }

                sum += value;
            }

            if (Math.abs(sum - 1.0) > 1e-9) {
                throw new ValidationException(
                    "Weights must sum to 1."
                );
            }
        }

        static Weights defaults() {
            return new Weights(
                0.25, 0.25, 0.15,
                0.15, 0.10, 0.10
            );
        }
    }

    record Opportunity(
        String id,
        String name,
        String description,
        double strategicFit,
        double expectedBenefit,
        double implementationCost,
        double customerValue,
        double urgency,
        double feasibility,
        double risk,
        double confidence,
        double costOfDelay,
        double effort,
        Set<String> dependencies,
        boolean mandatory
    ) {
        Opportunity {
            Objects.requireNonNull(id);
            Objects.requireNonNull(name);
            Objects.requireNonNull(description);
            Objects.requireNonNull(dependencies);

            if (id.isBlank() || name.isBlank()) {
                throw new ValidationException(
                    "Opportunity ID and name are required."
                );
            }

            checkRange("strategicFit", strategicFit);
            checkRange("customerValue", customerValue);
            checkRange("urgency", urgency);
            checkRange("feasibility", feasibility);
            checkRange("risk", risk);
            checkRange("confidence", confidence);

            checkNonNegative("expectedBenefit", expectedBenefit);
            checkNonNegative(
                "implementationCost",
                implementationCost
            );
            checkNonNegative("costOfDelay", costOfDelay);
            checkNonNegative("effort", effort);

            if (implementationCost <= 0 || effort <= 0) {
                throw new ValidationException(
                    "Implementation cost and effort must be positive."
                );
            }

            if (dependencies.contains(id)) {
                throw new DependencyException(
                    "Self-dependency is prohibited."
                );
            }

            dependencies = Collections.unmodifiableSet(
                new TreeSet<>(dependencies)
            );
        }

        private static void checkRange(
            String name,
            double value
        ) {
            if (
                !Double.isFinite(value) ||
                value < 0 ||
                value > 100
            ) {
                throw new ValidationException(
                    name + " must be between 0 and 100."
                );
            }
        }

        private static void checkNonNegative(
            String name,
            double value
        ) {
            if (!Double.isFinite(value) || value < 0) {
                throw new ValidationException(
                    name + " must be non-negative."
                );
            }
        }
    }

    record EconomicResult(
        double expectedBenefit,
        double netValue,
        double roi,
        double economicScore,
        double wsjf
    ) {}

    record Score(
        String opportunityId,
        String name,
        double weightedScore,
        double adjustedScore,
        double netValue,
        double roi,
        double wsjf,
        Tier tier,
        int rank
    ) {}

    record DecisionEvent(
        UUID eventId,
        String opportunityId,
        DecisionType type,
        String actor,
        String reason,
        Instant timestamp
    ) {}

    record PortfolioResult(
        double budget,
        double allocated,
        double expectedBenefit,
        double netValue,
        List<String> selected,
        List<String> deferred
    ) {
        PortfolioResult {
            selected = List.copyOf(selected);
            deferred = List.copyOf(deferred);
        }
    }

    interface ScoringPolicy {
        Score evaluate(
            Opportunity opportunity,
            Weights weights
        );
    }

    static final class EconomicPolicy {

        EconomicResult evaluate(Opportunity opportunity) {
            double expected =
                opportunity.expectedBenefit()
                * opportunity.confidence() / 100.0;

            double net =
                expected - opportunity.implementationCost();

            double roi =
                net / opportunity.implementationCost() * 100.0;

            double economicScore = Math.max(
                0,
                Math.min(
                    100,
                    50 + 50 * (
                        net / opportunity.implementationCost()
                    )
                )
            );

            double wsjf =
                opportunity.costOfDelay() /
                opportunity.effort();

            return new EconomicResult(
                expected,
                net,
                roi,
                economicScore,
                wsjf
            );
        }
    }

    static final class DefaultScoringPolicy
            implements ScoringPolicy {

        private final EconomicPolicy economicPolicy =
            new EconomicPolicy();

        @Override
        public Score evaluate(
            Opportunity opportunity,
            Weights weights
        ) {
            EconomicResult economic =
                economicPolicy.evaluate(opportunity);

            double weighted =
                opportunity.strategicFit()
                    * weights.strategicFit()
                + economic.economicScore()
                    * weights.economicValue()
                + opportunity.customerValue()
                    * weights.customerValue()
                + opportunity.urgency()
                    * weights.urgency()
                + opportunity.feasibility()
                    * weights.feasibility()
                + (100 - opportunity.risk())
                    * weights.riskAdjustment();

            double adjusted =
                weighted * opportunity.confidence() / 100.0;

            Tier tier;

            if (adjusted >= 85) {
                tier = Tier.CRITICAL;
            } else if (adjusted >= 70) {
                tier = Tier.HIGH;
            } else if (adjusted >= 50) {
                tier = Tier.MEDIUM;
            } else {
                tier = Tier.LOW;
            }

            return new Score(
                opportunity.id(),
                opportunity.name(),
                weighted,
                adjusted,
                economic.netValue(),
                economic.roi(),
                economic.wsjf(),
                tier,
                0
            );
        }
    }

    static final class ApprovalPolicy {

        private final int requiredApprovals;
        private final double minimumStrategicFit;

        ApprovalPolicy(
            int requiredApprovals,
            double minimumStrategicFit
        ) {
            if (
                requiredApprovals < 1 ||
                minimumStrategicFit < 0 ||
                minimumStrategicFit > 100
            ) {
                throw new ValidationException(
                    "Invalid approval policy."
                );
            }

            this.requiredApprovals = requiredApprovals;
            this.minimumStrategicFit = minimumStrategicFit;
        }

        boolean canApprove(
            Opportunity opportunity,
            Set<String> eligibleApprovers,
            Set<String> submittedApprovals
        ) {
            long validApprovals = submittedApprovals.stream()
                .filter(eligibleApprovers::contains)
                .distinct()
                .count();

            return validApprovals >= requiredApprovals
                && opportunity.strategicFit()
                    >= minimumStrategicFit;
        }
    }

    static final class PortfolioService {

        PortfolioResult allocate(
            List<Opportunity> opportunities,
            List<Score> scores,
            double budget
        ) {
            if (!Double.isFinite(budget) || budget < 0) {
                throw new ValidationException(
                    "Invalid portfolio budget."
                );
            }

            Map<String, Opportunity> registry =
                opportunities.stream().collect(
                    Collectors.toMap(
                        Opportunity::id,
                        item -> item
                    )
                );

            Map<String, Score> scoreMap =
                scores.stream().collect(
                    Collectors.toMap(
                        Score::opportunityId,
                        item -> item
                    )
                );

            Set<String> selected = new TreeSet<>();
            Set<String> deferred = new TreeSet<>();

            double remaining = budget;

            List<Opportunity> ordered =
                opportunities.stream()
                    .sorted(
                        Comparator
                            .comparing(
                                Opportunity::mandatory
                            ).reversed()
                            .thenComparing(
                                Comparator.comparingDouble(
                                    item -> scoreMap.get(
                                        item.id()
                                    ).adjustedScore()
                                ).reversed()
                            )
                            .thenComparing(Opportunity::id)
                    )
                    .toList();

            for (Opportunity item : ordered) {
                Set<String> closure =
                    dependencyClosure(item.id(), registry);

                Set<String> missing =
                    new TreeSet<>(closure);

                missing.removeAll(selected);

                double cost = missing.stream()
                    .map(registry::get)
                    .mapToDouble(
                        Opportunity::implementationCost
                    )
                    .sum();

                if (cost <= remaining) {
                    selected.addAll(missing);
                    remaining -= cost;
                } else if (item.mandatory()) {
                    throw new PrioritizationException(
                        "Mandatory opportunity exceeds budget: "
                            + item.id()
                    );
                } else {
                    deferred.add(item.id());
                }
            }

            List<Opportunity> selectedItems =
                selected.stream()
                    .map(registry::get)
                    .toList();

            double expectedBenefit = selectedItems.stream()
                .mapToDouble(
                    item -> item.expectedBenefit()
                        * item.confidence() / 100.0
                )
                .sum();

            double allocated = budget - remaining;

            return new PortfolioResult(
                budget,
                allocated,
                expectedBenefit,
                expectedBenefit - allocated,
                new ArrayList<>(selected),
                new ArrayList<>(deferred)
            );
        }

        private Set<String> dependencyClosure(
            String id,
            Map<String, Opportunity> registry
        ) {
            Set<String> result = new HashSet<>();
            Set<String> visiting = new HashSet<>();

            collect(
                id,
                registry,
                result,
                visiting
            );

            return result;
        }

        private void collect(
            String id,
            Map<String, Opportunity> registry,
            Set<String> result,
            Set<String> visiting
        ) {
            if (result.contains(id)) return;

            if (!visiting.add(id)) {
                throw new DependencyException(
                    "Circular dependency detected."
                );
            }

            Opportunity item = registry.get(id);

            if (item == null) {
                throw new DependencyException(
                    "Missing dependency: " + id
                );
            }

            for (String dependency : item.dependencies()) {
                collect(
                    dependency,
                    registry,
                    result,
                    visiting
                );
            }

            visiting.remove(id);
            result.add(id);
        }
    }

    static final class OpportunityService {

        private final Map<String, Opportunity> registry =
            new LinkedHashMap<>();

        private final Map<String, Status> states =
            new HashMap<>();

        private final List<DecisionEvent> auditLog =
            new ArrayList<>();

        private final Weights weights;
        private final ScoringPolicy scoringPolicy;
        private final ApprovalPolicy approvalPolicy;

        OpportunityService(
            Weights weights,
            ScoringPolicy scoringPolicy,
            ApprovalPolicy approvalPolicy
        ) {
            this.weights = weights;
            this.scoringPolicy = scoringPolicy;
            this.approvalPolicy = approvalPolicy;
        }

        void register(Opportunity opportunity) {
            if (registry.containsKey(opportunity.id())) {
                throw new ValidationException(
                    "Duplicate opportunity ID."
                );
            }

            registry.put(opportunity.id(), opportunity);
            states.put(opportunity.id(), Status.PROPOSED);

            record(
                opportunity.id(),
                DecisionType.CREATED,
                "SYSTEM",
                "Opportunity registered."
            );
        }

        private void validateDependencies() {
            for (Opportunity opportunity : registry.values()) {
                for (String dependency :
                     opportunity.dependencies()) {
                    if (!registry.containsKey(dependency)) {
                        throw new DependencyException(
                            opportunity.id()
                                + " depends on missing "
                                + dependency
                        );
                    }
                }
            }

            Set<String> visited = new HashSet<>();
            Set<String> visiting = new HashSet<>();

            for (String id : registry.keySet()) {
                visit(id, visited, visiting);
            }
        }

        private void visit(
            String id,
            Set<String> visited,
            Set<String> visiting
        ) {
            if (visiting.contains(id)) {
                throw new DependencyException(
                    "Circular dependency detected."
                );
            }

            if (visited.contains(id)) return;

            visiting.add(id);

            for (String dependency :
                 registry.get(id).dependencies()) {
                visit(dependency, visited, visiting);
            }

            visiting.remove(id);
            visited.add(id);
        }

        List<Score> evaluateAll() {
            validateDependencies();

            List<Score> results =
                registry.values().stream()
                    .map(item -> scoringPolicy.evaluate(
                        item,
                        weights
                    ))
                    .sorted(
                        Comparator
                            .comparingDouble(
                                Score::adjustedScore
                            ).reversed()
                            .thenComparing(
                                Comparator.comparingDouble(
                                    Score::wsjf
                                ).reversed()
                            )
                            .thenComparing(
                                Score::opportunityId
                            )
                    )
                    .toList();

            List<Score> ranked = new ArrayList<>();

            for (int i = 0; i < results.size(); i++) {
                Score original = results.get(i);

                Score item = new Score(
                    original.opportunityId(),
                    original.name(),
                    original.weightedScore(),
                    original.adjustedScore(),
                    original.netValue(),
                    original.roi(),
                    original.wsjf(),
                    original.tier(),
                    i + 1
                );

                ranked.add(item);

                if (states.get(item.opportunityId())
                        == Status.PROPOSED) {
                    states.put(
                        item.opportunityId(),
                        Status.EVALUATED
                    );
                }

                record(
                    item.opportunityId(),
                    DecisionType.EVALUATED,
                    "SCORING_SERVICE",
                    "Score: " + item.adjustedScore()
                );
            }

            return List.copyOf(ranked);
        }

        void approve(
            String id,
            String actor,
            Set<String> eligibleApprovers,
            Set<String> submittedApprovals
        ) {
            Opportunity opportunity = require(id);

            if (states.get(id) != Status.EVALUATED) {
                throw new PrioritizationException(
                    "Only evaluated opportunities can be approved."
                );
            }

            if (!approvalPolicy.canApprove(
                opportunity,
                eligibleApprovers,
                submittedApprovals
            )) {
                throw new PrioritizationException(
                    "Approval requirements not satisfied."
                );
            }

            states.put(id, Status.APPROVED);

            record(
                id,
                DecisionType.APPROVED,
                actor,
                "Approval policy satisfied."
            );
        }

        void defer(String id, String actor, String reason) {
            require(id);

            if (reason == null || reason.isBlank()) {
                throw new ValidationException(
                    "A deferral reason is required."
                );
            }

            Status current = states.get(id);

            if (
                current == Status.APPROVED ||
                current == Status.REJECTED
            ) {
                throw new PrioritizationException(
                    "Finalized decisions cannot be deferred."
                );
            }

            states.put(id, Status.DEFERRED);

            record(
                id,
                DecisionType.DEFERRED,
                actor,
                reason
            );
        }

        void reject(String id, String actor, String reason) {
            require(id);

            if (reason == null || reason.isBlank()) {
                throw new ValidationException(
                    "A rejection reason is required."
                );
            }

            if (states.get(id) == Status.APPROVED) {
                throw new PrioritizationException(
                    "Approved opportunity cannot be rejected "
                        + "without an explicit reversal workflow."
                );
            }

            states.put(id, Status.REJECTED);

            record(
                id,
                DecisionType.REJECTED,
                actor,
                reason
            );
        }

        private Opportunity require(String id) {
            Opportunity item = registry.get(id);

            if (item == null) {
                throw new ValidationException(
                    "Unknown opportunity: " + id
                );
            }

            return item;
        }

        private void record(
            String id,
            DecisionType type,
            String actor,
            String reason
        ) {
            auditLog.add(new DecisionEvent(
                UUID.randomUUID(),
                id,
                type,
                actor,
                reason,
                Instant.now()
            ));
        }

        Map<String, Status> getStates() {
            return Collections.unmodifiableMap(
                new HashMap<>(states)
            );
        }

        List<DecisionEvent> getAuditLog() {
            return List.copyOf(auditLog);
        }

        List<Opportunity> getOpportunities() {
            return List.copyOf(registry.values());
        }
    }

    private static Opportunity create(
        String id,
        String name,
        double strategic,
        double benefit,
        double cost,
        double customer,
        double urgency,
        double feasibility,
        double risk,
        double confidence,
        double delay,
        double effort,
        Set<String> dependencies,
        boolean mandatory
    ) {
        return new Opportunity(
            id,
            name,
            "Enterprise investment opportunity.",
            strategic,
            benefit,
            cost,
            customer,
            urgency,
            feasibility,
            risk,
            confidence,
            delay,
            effort,
            dependencies,
            mandatory
        );
    }

    public static void main(String[] args) {

        try {
            Weights weights = Weights.defaults();

            OpportunityService service =
                new OpportunityService(
                    weights,
                    new DefaultScoringPolicy(),
                    new ApprovalPolicy(2, 70)
                );

            service.register(create(
                "OP-001",
                "Customer Analytics Platform",
                95, 900000, 250000,
                90, 85, 80, 25, 85,
                120000, 12,
                Set.of(),
                false
            ));

            service.register(create(
                "OP-002",
                "Cloud Cost Optimization",
                85, 600000, 150000,
                65, 75, 90, 15, 90,
                85000, 8,
                Set.of(),
                false
            ));

            service.register(create(
                "OP-003",
                "Security Monitoring Modernization",
                100, 750000, 300000,
                80, 95, 75, 20, 90,
                180000, 15,
                Set.of(),
                true
            ));

            service.register(create(
                "OP-004",
                "Mobile Experience Improvement",
                75, 450000, 120000,
                95, 70, 85, 15, 80,
                70000, 7,
                Set.of("OP-001"),
                false
            ));

            service.register(create(
                "OP-005",
                "Reporting Automation",
                60, 180000, 80000,
                50, 45, 95, 10, 95,
                20000, 5,
                Set.of(),
                false
            ));

            List<Score> ranking = service.evaluateAll();

            System.out.println("\nENTERPRISE OPPORTUNITY RANKING");

            System.out.printf(
                "%-6s %-12s %-35s %10s %10s %10s %10s%n",
                "Rank",
                "ID",
                "Opportunity",
                "Weighted",
                "Adjusted",
                "ROI",
                "WSJF"
            );

            for (Score item : ranking) {
                System.out.printf(
                    "%-6d %-12s %-35s %10.2f %10.2f %10.2f %10.2f%n",
                    item.rank(),
                    item.opportunityId(),
                    item.name(),
                    item.weightedScore(),
                    item.adjustedScore(),
                    item.roi(),
                    item.wsjf()
                );
            }

            Set<String> eligibleApprovers = Set.of(
                "PRODUCT_DIRECTOR",
                "FINANCE_DIRECTOR",
                "SECURITY_DIRECTOR"
            );

            Set<String> approvals = Set.of(
                "PRODUCT_DIRECTOR",
                "FINANCE_DIRECTOR"
            );

            service.approve(
                "OP-001",
                "INVESTMENT_COMMITTEE",
                eligibleApprovers,
                approvals
            );

            PortfolioService portfolioService =
                new PortfolioService();

            PortfolioResult portfolio =
                portfolioService.allocate(
                    service.getOpportunities(),
                    ranking,
                    700000
                );

            System.out.println("\nPORTFOLIO ALLOCATION");

            System.out.println(
                "Budget: " + portfolio.budget()
            );

            System.out.println(
                "Allocated: " + portfolio.allocated()
            );

            System.out.println(
                "Expected benefit: "
                    + portfolio.expectedBenefit()
            );

            System.out.println(
                "Net value: " + portfolio.netValue()
            );

            System.out.println(
                "Selected: " + portfolio.selected()
            );

            System.out.println(
                "Deferred: " + portfolio.deferred()
            );

            System.out.println("\nLIFECYCLE STATES");
            service.getStates().forEach(
                (id, status) ->
                    System.out.println(id + " -> " + status)
            );

            System.out.println("\nAUDIT EVENTS");

            service.getAuditLog().forEach(event ->
                System.out.println(
                    event.timestamp()
                        + " | "
                        + event.opportunityId()
                        + " | "
                        + event.type()
                        + " | "
                        + event.actor()
                )
            );

        } catch (PrioritizationException error) {
            System.err.println(
                "Prioritization failure: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
