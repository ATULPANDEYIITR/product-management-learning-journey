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
 * RICE Framework: Enterprise Product Governance System
 *
 * Java 17 implementation.
 *
 * Domain separation:
 * 1. Opportunity data
 * 2. Evidence verification
 * 3. RICE scoring
 * 4. Approval policy
 * 5. Portfolio optimization
 * 6. Scenario analysis
 * 7. Audit reporting
 */

public class RiceGovernance {

    enum Decision {
        ACCEPT,
        REVIEW,
        DEFER
    }

    enum Priority {
        HIGH,
        MEDIUM,
        LOW
    }

    enum EvidenceStatus {
        VERIFIED,
        UNVERIFIED,
        MISSING
    }

    enum Lifecycle {
        DRAFT,
        SUBMITTED,
        EVALUATED,
        APPROVED,
        DEFERRED
    }

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    record RICEItem(
        String id,
        String name,
        double reach,
        double impact,
        double confidence,
        double effort,
        double strategicValue,
        String category,
        EvidenceStatus evidenceStatus,
        List<String> dependencies
    ) {
        RICEItem {
            Objects.requireNonNull(id);
            Objects.requireNonNull(name);
            Objects.requireNonNull(category);
            Objects.requireNonNull(evidenceStatus);
            Objects.requireNonNull(dependencies);

            if (id.isBlank() || name.isBlank()) {
                throw new DomainException("ID and name are required.");
            }

            if (
                !Double.isFinite(reach) ||
                !Double.isFinite(impact) ||
                !Double.isFinite(confidence) ||
                !Double.isFinite(effort) ||
                !Double.isFinite(strategicValue)
            ) {
                throw new DomainException("Numeric values must be finite.");
            }

            if (
                reach < 0 ||
                impact <= 0 ||
                effort <= 0 ||
                strategicValue < 0
            ) {
                throw new DomainException("Invalid RICE values.");
            }

            if (confidence < 0 || confidence > 100) {
                throw new DomainException(
                    "Confidence must be between 0 and 100."
                );
            }

            if (dependencies.contains(id)) {
                throw new DomainException("Self-dependency is invalid.");
            }

            if (new HashSet<>(dependencies).size() != dependencies.size()) {
                throw new DomainException("Duplicate dependencies.");
            }

            dependencies = List.copyOf(dependencies);
        }
    }

    record RICEPolicy(
        double highThreshold,
        double mediumThreshold,
        double minimumConfidence,
        boolean requireVerifiedEvidence
    ) {
        RICEPolicy {
            if (
                !Double.isFinite(highThreshold) ||
                !Double.isFinite(mediumThreshold) ||
                highThreshold <= mediumThreshold ||
                mediumThreshold < 0
            ) {
                throw new DomainException("Invalid score thresholds.");
            }

            if (
                minimumConfidence < 0 ||
                minimumConfidence > 100
            ) {
                throw new DomainException("Invalid confidence policy.");
            }
        }

        static RICEPolicy standard() {
            return new RICEPolicy(100, 30, 40, true);
        }
    }

    record Evaluation(
        String itemId,
        double score,
        double efficiency,
        Priority priority,
        Decision decision,
        List<String> limitations,
        EvidenceStatus evidenceStatus,
        int rank
    ) {
        Evaluation {
            limitations = List.copyOf(limitations);
        }
    }

    record Scenario(
        double optimistic,
        double baseline,
        double pessimistic
    ) {}

    record AuditEvent(
        String eventId,
        String itemId,
        String event,
        String details
    ) {}

    interface EvidenceVerifier {
        EvidenceStatus verify(RICEItem item);
    }

    static class StaticEvidenceVerifier implements EvidenceVerifier {

        @Override
        public EvidenceStatus verify(RICEItem item) {
            if (item.evidenceStatus() == EvidenceStatus.MISSING) {
                return EvidenceStatus.MISSING;
            }

            return item.evidenceStatus();
        }
    }

    static class RICEScoringService {

        private final RICEPolicy policy;

        RICEScoringService(RICEPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        double score(RICEItem item) {
            return (
                item.reach() *
                item.impact() *
                item.confidence() / 100.0 /
                item.effort()
            );
        }

        Evaluation evaluate(
            RICEItem item,
            EvidenceStatus evidenceStatus
        ) {

            double score = score(item);

            List<String> limitations = new ArrayList<>();

            if (item.confidence() < policy.minimumConfidence()) {
                limitations.add("Confidence below required threshold.");
            }

            if (item.reach() == 0) {
                limitations.add("Zero measurable reach.");
            }

            if (evidenceStatus == EvidenceStatus.MISSING) {
                limitations.add("Evidence is missing.");
            }

            if (evidenceStatus == EvidenceStatus.UNVERIFIED) {
                limitations.add("Evidence requires verification.");
            }

            Decision decision;

            if (
                item.confidence() < policy.minimumConfidence() ||
                evidenceStatus == EvidenceStatus.MISSING ||
                (
                    policy.requireVerifiedEvidence() &&
                    evidenceStatus != EvidenceStatus.VERIFIED
                )
            ) {
                decision = Decision.REVIEW;
            } else if (score >= policy.highThreshold()) {
                decision = Decision.ACCEPT;
            } else if (score >= policy.mediumThreshold()) {
                decision = Decision.REVIEW;
            } else {
                decision = Decision.DEFER;
            }

            Priority priority =
                score >= policy.highThreshold() ? Priority.HIGH :
                score >= policy.mediumThreshold() ? Priority.MEDIUM :
                Priority.LOW;

            return new Evaluation(
                item.id(),
                score,
                score / item.effort(),
                priority,
                decision,
                limitations,
                evidenceStatus,
                0
            );
        }
    }

    static class DependencyService {

        void validate(List<RICEItem> items) {
            Map<String, RICEItem> index = new HashMap<>();

            for (RICEItem item : items) {
                if (index.putIfAbsent(item.id(), item) != null) {
                    throw new DomainException(
                        "Duplicate item ID: " + item.id()
                    );
                }
            }

            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();

            for (RICEItem item : items) {
                visit(item.id(), index, visiting, visited);
            }
        }

        private void visit(
            String id,
            Map<String, RICEItem> index,
            Set<String> visiting,
            Set<String> visited
        ) {

            if (visiting.contains(id)) {
                throw new DomainException("Dependency cycle detected.");
            }

            if (visited.contains(id)) {
                return;
            }

            RICEItem item = index.get(id);

            if (item == null) {
                throw new DomainException("Unknown dependency: " + id);
            }

            visiting.add(id);

            for (String dependency : item.dependencies()) {
                if (!index.containsKey(dependency)) {
                    throw new DomainException(
                        "Missing dependency: " + dependency
                    );
                }

                visit(dependency, index, visiting, visited);
            }

            visiting.remove(id);
            visited.add(id);
        }
    }

    static class PortfolioService {

        private final RICEScoringService scoringService;
        private final EvidenceVerifier evidenceVerifier;
        private final DependencyService dependencyService;

        private final List<AuditEvent> auditEvents = new ArrayList<>();

        PortfolioService(
            RICEScoringService scoringService,
            EvidenceVerifier evidenceVerifier,
            DependencyService dependencyService
        ) {
            this.scoringService = scoringService;
            this.evidenceVerifier = evidenceVerifier;
            this.dependencyService = dependencyService;
        }

        List<Evaluation> evaluate(List<RICEItem> items) {
            dependencyService.validate(items);

            List<Evaluation> evaluations = items.stream()
                .map(item -> {
                    EvidenceStatus status = evidenceVerifier.verify(item);

                    Evaluation result = scoringService.evaluate(
                        item,
                        status
                    );

                    auditEvents.add(new AuditEvent(
                        UUID.randomUUID().toString(),
                        item.id(),
                        "EVALUATED",
                        "Score=" + result.score()
                    ));

                    return result;
                })
                .sorted(
                    Comparator.comparingDouble(Evaluation::score)
                        .reversed()
                        .thenComparing(Evaluation::itemId)
                )
                .toList();

            List<Evaluation> ranked = new ArrayList<>();

            for (int i = 0; i < evaluations.size(); i++) {
                Evaluation old = evaluations.get(i);

                ranked.add(new Evaluation(
                    old.itemId(),
                    old.score(),
                    old.efficiency(),
                    old.priority(),
                    old.decision(),
                    old.limitations(),
                    old.evidenceStatus(),
                    i + 1
                ));
            }

            return List.copyOf(ranked);
        }

        List<AuditEvent> auditTrail() {
            return List.copyOf(auditEvents);
        }
    }

    static class PortfolioOptimizer {

        private static final int SCALE = 10;

        record SelectedItem(
            RICEItem item,
            Evaluation evaluation
        ) {}

        List<SelectedItem> optimize(
            List<RICEItem> items,
            List<Evaluation> evaluations,
            double effortBudget
        ) {

            if (!Double.isFinite(effortBudget) || effortBudget < 0) {
                throw new DomainException("Invalid effort budget.");
            }

            if (effortBudget > 10000) {
                throw new DomainException("Budget exceeds optimizer limit.");
            }

            Map<String, RICEItem> itemIndex = items.stream()
                .collect(Collectors.toMap(
                    RICEItem::id,
                    item -> item
                ));

            List<Evaluation> eligible = evaluations.stream()
                .filter(e -> e.decision() == Decision.ACCEPT)
                .toList();

            int capacity = (int) Math.floor(
                effortBudget * SCALE + 1e-9
            );

            double[] dp = new double[capacity + 1];

            @SuppressWarnings("unchecked")
            List<Integer>[] selections = new List[capacity + 1];

            for (int i = 0; i <= capacity; i++) {
                selections[i] = new ArrayList<>();
            }

            for (int i = 0; i < eligible.size(); i++) {
                Evaluation evaluation = eligible.get(i);
                RICEItem item = itemIndex.get(evaluation.itemId());

                int weight = (int) Math.ceil(
                    item.effort() * SCALE - 1e-12
                );

                if (weight > capacity) {
                    continue;
                }

                for (int c = capacity; c >= weight; c--) {
                    double candidate =
                        dp[c - weight] + evaluation.score();

                    if (candidate > dp[c]) {
                        dp[c] = candidate;

                        List<Integer> next = new ArrayList<>(
                            selections[c - weight]
                        );

                        next.add(i);
                        selections[c] = next;
                    }
                }
            }

            List<SelectedItem> selected = new ArrayList<>();

            for (int index : selections[capacity]) {
                Evaluation evaluation = eligible.get(index);

                selected.add(new SelectedItem(
                    itemIndex.get(evaluation.itemId()),
                    evaluation
                ));
            }

            return List.copyOf(selected);
        }
    }

    static class ScenarioAnalyzer {

        static double calculate(
            RICEItem item,
            double reachFactor,
            double impactFactor,
            double confidenceFactor,
            double effortFactor
        ) {

            double[] factors = {
                reachFactor,
                impactFactor,
                confidenceFactor,
                effortFactor
            };

            for (double factor : factors) {
                if (!Double.isFinite(factor) || factor <= 0) {
                    throw new DomainException("Invalid scenario factor.");
                }
            }

            double confidence = Math.min(
                100,
                item.confidence() * confidenceFactor
            );

            return (
                item.reach() * reachFactor *
                item.impact() * impactFactor *
                confidence / 100.0 /
                (item.effort() * effortFactor)
            );
        }

        static Scenario analyze(RICEItem item) {
            return new Scenario(
                calculate(item, 1.2, 1.2, 1.1, 0.9),
                calculate(item, 1, 1, 1, 1),
                calculate(item, 0.8, 0.8, 0.8, 1.2)
            );
        }
    }

    private static List<RICEItem> samplePortfolio() {
        return List.of(
            new RICEItem(
                "P001", "Account recovery",
                12000, 2, 90, 3, 8,
                "Security", EvidenceStatus.VERIFIED, List.of()
            ),
            new RICEItem(
                "P002", "Dashboard redesign",
                8500, 1, 85, 4, 2,
                "Product", EvidenceStatus.VERIFIED, List.of()
            ),
            new RICEItem(
                "P003", "Incident notifications",
                15000, 1.5, 95, 2, 9,
                "Reliability", EvidenceStatus.VERIFIED, List.of()
            ),
            new RICEItem(
                "P004", "Recommendation engine",
                5000, 3, 35, 8, 5,
                "Experiment", EvidenceStatus.UNVERIFIED, List.of()
            ),
            new RICEItem(
                "P005", "Accessibility improvements",
                6000, 1.5, 95, 2.5, 7,
                "Accessibility", EvidenceStatus.VERIFIED, List.of()
            ),
            new RICEItem(
                "P006", "Legacy reporting",
                0, 1, 80, 3, 1,
                "Operations", EvidenceStatus.MISSING, List.of()
            )
        );
    }

    private static void runTests(RICEScoringService service) {
        RICEItem test = new RICEItem(
            "TEST", "Formula test",
            1000, 2, 80, 4, 0,
            "Test", EvidenceStatus.VERIFIED, List.of()
        );

        double score = service.score(test);

        if (Math.abs(score - 400) > 1e-9) {
            throw new DomainException("Formula test failed.");
        }

        try {
            new RICEItem(
                "BAD", "Invalid",
                -1, 2, 80, 4, 0,
                "Test", EvidenceStatus.VERIFIED, List.of()
            );

            throw new DomainException("Negative reach test failed.");
        } catch (DomainException expected) {
            if (expected.getMessage().equals("Negative reach test failed.")) {
                throw expected;
            }
        }

        System.out.println("Validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            RICEPolicy policy = RICEPolicy.standard();

            RICEScoringService scoring = new RICEScoringService(policy);

            runTests(scoring);

            PortfolioService portfolio = new PortfolioService(
                scoring,
                new StaticEvidenceVerifier(),
                new DependencyService()
            );

            List<RICEItem> items = samplePortfolio();

            List<Evaluation> results = portfolio.evaluate(items);

            System.out.println("\nENTERPRISE RICE EVALUATION");
            System.out.println(
                "--------------------------------------------------------------"
            );

            for (Evaluation result : results) {
                System.out.printf(
                    "%d | %s | %.2f | %s | %s%n",
                    result.rank(),
                    result.itemId(),
                    result.score(),
                    result.priority(),
                    result.decision()
                );

                for (String limitation : result.limitations()) {
                    System.out.println("    " + limitation);
                }
            }

            PortfolioOptimizer optimizer = new PortfolioOptimizer();

            List<PortfolioOptimizer.SelectedItem> selected =
                optimizer.optimize(items, results, 12);

            System.out.println("\nOPTIMIZED PORTFOLIO");

            double totalEffort = 0;

            for (var entry : selected) {
                System.out.printf(
                    "%s | %.1f months | %.2f%n",
                    entry.item().name(),
                    entry.item().effort(),
                    entry.evaluation().score()
                );

                totalEffort += entry.item().effort();
            }

            System.out.printf(
                "Total effort: %.1f / 12.0 months%n",
                totalEffort
            );

            System.out.println("\nSCENARIO ANALYSIS");

            for (RICEItem item : items) {
                Scenario scenario = ScenarioAnalyzer.analyze(item);

                System.out.printf(
                    "%s | Optimistic %.2f | Baseline %.2f | Pessimistic %.2f%n",
                    item.name(),
                    scenario.optimistic(),
                    scenario.baseline(),
                    scenario.pessimistic()
                );
            }

            System.out.println(
                "\nAudit events recorded: " + portfolio.auditTrail().size()
            );

        } catch (DomainException error) {
            System.err.println("Governance failure: " + error.getMessage());
            System.exit(1);
        }
    }
}
