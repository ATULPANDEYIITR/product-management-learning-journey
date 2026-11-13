import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/*
 * VALUE VS EFFORT
 *
 * Enterprise portfolio prioritization and governance.
 *
 * Java 17
 * No third-party dependencies.
 */

public class ValueEffortEnterprise {

    enum Risk {
        LOW(1.00),
        MEDIUM(0.85),
        HIGH(0.65);

        final double factor;

        Risk(double factor) {
            this.factor = factor;
        }
    }

    enum Priority {
        QUICK_WIN,
        STRATEGIC,
        FILL_IN,
        LOW_PRIORITY
    }

    enum ReviewState {
        APPROVED,
        CHANGES_REQUESTED,
        COMMENTED,
        DISMISSED
    }

    enum CheckState {
        PASSED,
        FAILED,
        PENDING
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        MERGED,
        CLOSED
    }

    record EffortEstimate(
        double low,
        double expected,
        double high
    ) {
        EffortEstimate {
            if (!Double.isFinite(low) ||
                !Double.isFinite(expected) ||
                !Double.isFinite(high) ||
                low < 0 ||
                expected <= 0 ||
                low > expected ||
                expected > high) {
                throw new IllegalArgumentException(
                    "Invalid effort estimate."
                );
            }
        }

        double mean() {
            return (low + expected + high) / 3.0;
        }
    }

    record Opportunity(
        String id,
        String name,
        double customerImpact,
        double strategicAlignment,
        double revenueImpact,
        double urgency,
        double valueConfidence,
        double effortConfidence,
        EffortEstimate effort,
        Risk risk,
        Set<String> dependencies
    ) {
        Opportunity {
            Objects.requireNonNull(id);
            Objects.requireNonNull(name);
            Objects.requireNonNull(effort);
            Objects.requireNonNull(risk);

            dependencies = Set.copyOf(dependencies);

            if (id.isBlank() || name.isBlank()) {
                throw new IllegalArgumentException(
                    "ID and name are required."
                );
            }

            List<Double> ratings = List.of(
                customerImpact,
                strategicAlignment,
                revenueImpact,
                urgency,
                valueConfidence,
                effortConfidence
            );

            if (ratings.stream().anyMatch(
                score -> !Double.isFinite(score) ||
                    score < 1 || score > 5
            )) {
                throw new IllegalArgumentException(
                    "Ratings must be between 1 and 5."
                );
            }

            if (dependencies.contains(id)) {
                throw new IllegalArgumentException(
                    "Self-dependency is prohibited."
                );
            }
        }
    }

    record Evaluation(
        String opportunityId,
        String name,
        double value,
        double adjustedValue,
        double effort,
        double ratio,
        double confidence,
        Priority priority,
        Risk risk
    ) {}

    record Review(
        String reviewerId,
        boolean eligible,
        boolean stale,
        ReviewState state
    ) {
        Review {
            Objects.requireNonNull(reviewerId);
            Objects.requireNonNull(state);
        }
    }

    record ProtectionPolicy(
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean requireUpdatedSource,
        boolean prohibitDraftMerge
    ) {
        ProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Approval count cannot be negative."
                );
            }

            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    static class PullRequest {
        private final String id;
        private final String sourceBranch;
        private final String targetBranch;

        private PullRequestState state;

        private boolean sourceUpdated;
        private boolean conflicts;
        private boolean conversationsResolved;
        private final boolean linearHistory;

        private final Map<String, CheckState> checks =
            new HashMap<>();

        private final List<Review> reviews =
            new ArrayList<>();

        PullRequest(
            String id,
            String sourceBranch,
            String targetBranch,
            PullRequestState state,
            boolean sourceUpdated,
            boolean conflicts,
            boolean conversationsResolved,
            boolean linearHistory
        ) {
            this.id = Objects.requireNonNull(id);
            this.sourceBranch = Objects.requireNonNull(sourceBranch);
            this.targetBranch = Objects.requireNonNull(targetBranch);
            this.state = Objects.requireNonNull(state);
            this.sourceUpdated = sourceUpdated;
            this.conflicts = conflicts;
            this.conversationsResolved = conversationsResolved;
            this.linearHistory = linearHistory;

            if (id.isBlank() ||
                sourceBranch.isBlank() ||
                targetBranch.isBlank() ||
                sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException(
                    "Invalid Pull Request identity or branches."
                );
            }
        }

        void addReview(Review review) {
            reviews.add(Objects.requireNonNull(review));
        }

        void setCheck(String name, CheckState state) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Check name is required."
                );
            }

            checks.put(name, Objects.requireNonNull(state));
        }

        void updateSource(boolean updated) {
            sourceUpdated = updated;
        }

        void updateConversations(boolean resolved) {
            conversationsResolved = resolved;
        }

        void setConflicts(boolean conflicts) {
            this.conflicts = conflicts;
        }

        void close() {
            if (state == PullRequestState.MERGED) {
                throw new IllegalStateException(
                    "Merged Pull Requests cannot be closed as unmerged."
                );
            }

            state = PullRequestState.CLOSED;
        }

        void reopen() {
            if (state != PullRequestState.CLOSED) {
                throw new IllegalStateException(
                    "Only closed Pull Requests can be reopened."
                );
            }

            state = PullRequestState.OPEN;
        }
    }

    static class EstimationService {

        private static final Map<String, Double> WEIGHTS = Map.of(
            "customer", 0.35,
            "strategy", 0.30,
            "revenue", 0.20,
            "urgency", 0.15
        );

        Evaluation evaluate(Opportunity opportunity) {
            double value = (
                opportunity.customerImpact() * WEIGHTS.get("customer") +
                opportunity.strategicAlignment() * WEIGHTS.get("strategy") +
                opportunity.revenueImpact() * WEIGHTS.get("revenue") +
                opportunity.urgency() * WEIGHTS.get("urgency")
            ) / 5.0 * 100;

            double confidence = Math.min(
                opportunity.valueConfidence(),
                opportunity.effortConfidence()
            ) / 5.0;

            double adjusted =
                value * confidence * opportunity.risk().factor;

            double effort = opportunity.effort().mean();
            double ratio = adjusted / effort;

            Priority priority;

            if (ratio >= 20) {
                priority = Priority.QUICK_WIN;
            } else if (ratio >= 8) {
                priority = Priority.STRATEGIC;
            } else if (adjusted >= 25) {
                priority = Priority.FILL_IN;
            } else {
                priority = Priority.LOW_PRIORITY;
            }

            return new Evaluation(
                opportunity.id(),
                opportunity.name(),
                value,
                adjusted,
                effort,
                ratio,
                confidence,
                priority,
                opportunity.risk()
            );
        }
    }

    static class PortfolioService {

        private final Map<String, Opportunity> opportunities =
            new LinkedHashMap<>();

        private final EstimationService estimationService =
            new EstimationService();

        void register(Opportunity opportunity) {
            Objects.requireNonNull(opportunity);

            if (opportunities.putIfAbsent(
                opportunity.id(), opportunity
            ) != null) {
                throw new IllegalArgumentException(
                    "Duplicate opportunity ID."
                );
            }
        }

        void validateDependencies() {
            Set<String> visited = new HashSet<>();
            Set<String> active = new HashSet<>();

            for (String id : opportunities.keySet()) {
                visit(id, visited, active);
            }
        }

        private void visit(
            String id,
            Set<String> visited,
            Set<String> active
        ) {
            if (active.contains(id)) {
                throw new IllegalStateException(
                    "Dependency cycle detected."
                );
            }

            if (visited.contains(id)) return;

            Opportunity item = opportunities.get(id);

            if (item == null) {
                throw new IllegalStateException(
                    "Unknown dependency: " + id
                );
            }

            active.add(id);

            for (String dependency : item.dependencies()) {
                visit(dependency, visited, active);
            }

            active.remove(id);
            visited.add(id);
        }

        List<Evaluation> evaluateAll() {
            validateDependencies();

            return opportunities.values()
                .stream()
                .map(estimationService::evaluate)
                .sorted(
                    Comparator.comparingDouble(
                        Evaluation::ratio
                    ).reversed()
                )
                .toList();
        }

        List<Evaluation> allocate(
            List<Evaluation> evaluations,
            double capacity
        ) {
            if (!Double.isFinite(capacity) || capacity < 0) {
                throw new IllegalArgumentException(
                    "Invalid capacity."
                );
            }

            Map<String, Evaluation> evaluationMap =
                evaluations.stream().collect(
                    Collectors.toMap(
                        Evaluation::opportunityId,
                        Function.identity()
                    )
                );

            Set<String> selected = new LinkedHashSet<>();
            double remaining = capacity;

            for (Evaluation evaluation : evaluations) {
                Set<String> bundle = new LinkedHashSet<>();

                collectDependencies(
                    evaluation.opportunityId(),
                    bundle
                );

                double required = bundle.stream()
                    .filter(id -> !selected.contains(id))
                    .mapToDouble(
                        id -> evaluationMap.get(id).effort()
                    )
                    .sum();

                if (required <= remaining) {
                    selected.addAll(bundle);
                    remaining -= required;
                }
            }

            return selected.stream()
                .map(evaluationMap::get)
                .sorted(
                    Comparator.comparingDouble(
                        Evaluation::ratio
                    ).reversed()
                )
                .toList();
        }

        private void collectDependencies(
            String id,
            Set<String> bundle
        ) {
            if (!bundle.add(id)) return;

            Opportunity opportunity = opportunities.get(id);

            for (String dependency : opportunity.dependencies()) {
                collectDependencies(dependency, bundle);
            }
        }
    }

    static class GovernanceService {

        List<String> evaluateMergeEligibility(
            PullRequest pr,
            ProtectionPolicy policy
        ) {
            List<String> blockers = new ArrayList<>();

            if (pr.state != PullRequestState.OPEN) {
                blockers.add("Pull Request is not open.");
            }

            if (policy.prohibitDraftMerge &&
                pr.state == PullRequestState.DRAFT) {
                blockers.add("Draft Pull Request cannot merge.");
            }

            if (!pr.sourceUpdated &&
                policy.requireUpdatedSource) {
                blockers.add("Source branch requires synchronization.");
            }

            if (pr.conflicts) {
                blockers.add("Merge conflicts detected.");
            }

            if (policy.requireResolvedConversations &&
                !pr.conversationsResolved) {
                blockers.add("Unresolved review conversations.");
            }

            if (!pr.linearHistory) {
                blockers.add("Linear history requirement not satisfied.");
            }

            int approvals = 0;
            boolean requestedChanges = false;

            // Only the latest eligible review from each reviewer counts.
            Map<String, Review> latestReviews = new HashMap<>();

            for (Review review : pr.reviews) {
                Review previous = latestReviews.get(review.reviewerId());

                if (previous == null) {
                    latestReviews.put(review.reviewerId(), review);
                } else {
                    latestReviews.put(review.reviewerId(), review);
                }
            }

            for (Review review : latestReviews.values()) {
                if (!review.eligible() ||
                    review.stale() ||
                    review.state() == ReviewState.DISMISSED) {
                    continue;
                }

                if (review.state() == ReviewState.CHANGES_REQUESTED) {
                    requestedChanges = true;
                }

                if (review.state() == ReviewState.APPROVED) {
                    approvals++;
                }
            }

            if (approvals < policy.requiredApprovals()) {
                blockers.add("Required approvals not satisfied.");
            }

            if (requestedChanges) {
                blockers.add("Active changes-requested review exists.");
            }

            for (String required : policy.requiredChecks()) {
                if (pr.checks.get(required) != CheckState.PASSED) {
                    blockers.add(
                        "Required check missing or unsuccessful: " +
                        required
                    );
                }
            }

            return List.copyOf(blockers);
        }
    }

    static Opportunity sample(
        String id,
        String name,
        double customer,
        double strategy,
        double revenue,
        double urgency,
        double valueConfidence,
        double effortConfidence,
        EffortEstimate effort,
        Risk risk,
        Set<String> dependencies
    ) {
        return new Opportunity(
            id,
            name,
            customer,
            strategy,
            revenue,
            urgency,
            valueConfidence,
            effortConfidence,
            effort,
            risk,
            dependencies
        );
    }

    public static void main(String[] args) {

        PortfolioService portfolio = new PortfolioService();

        portfolio.register(sample(
            "OP-401", "Deployment Automation",
            5, 5, 4, 5, 5, 5,
            new EffortEstimate(2, 3, 5),
            Risk.LOW, Set.of()
        ));

        portfolio.register(sample(
            "OP-402", "Analytics Dashboard",
            4, 3, 3, 3, 4, 4,
            new EffortEstimate(5, 8, 12),
            Risk.MEDIUM, Set.of()
        ));

        portfolio.register(sample(
            "OP-403", "Security Automation",
            5, 5, 4, 5, 4, 4,
            new EffortEstimate(4, 6, 10),
            Risk.LOW, Set.of()
        ));

        portfolio.register(sample(
            "OP-404", "Documentation Upgrade",
            2, 3, 1, 2, 5, 5,
            new EffortEstimate(2, 3, 4),
            Risk.LOW, Set.of()
        ));

        portfolio.register(sample(
            "OP-405", "Data Integration",
            5, 5, 5, 4, 3, 3,
            new EffortEstimate(12, 18, 25),
            Risk.HIGH, Set.of("OP-404")
        ));

        List<Evaluation> results = portfolio.evaluateAll();

        System.out.println("\nENTERPRISE OPPORTUNITY RANKING");

        System.out.printf(
            "%-25s %10s %10s %10s %10s %20s%n",
            "Opportunity",
            "Value",
            "Adjusted",
            "Effort",
            "Ratio",
            "Priority"
        );

        for (Evaluation result : results) {
            System.out.printf(
                "%-25s %10.2f %10.2f %10.2f %10.2f %20s%n",
                result.name(),
                result.value(),
                result.adjustedValue(),
                result.effort(),
                result.ratio(),
                result.priority()
            );
        }

        System.out.println("\nCAPACITY ALLOCATION");

        List<Evaluation> selected =
            portfolio.allocate(results, 15);

        selected.forEach(item ->
            System.out.printf(
                "%s | %.2f effort units%n",
                item.name(),
                item.effort()
            )
        );

        PullRequest pr = new PullRequest(
            "PR-601",
            "feature/security-automation",
            "main",
            PullRequestState.OPEN,
            true,
            false,
            true,
            true
        );

        pr.addReview(new Review(
            "reviewer-1", true, false, ReviewState.APPROVED
        ));

        pr.addReview(new Review(
            "reviewer-2", true, false, ReviewState.APPROVED
        ));

        pr.setCheck("build", CheckState.PASSED);
        pr.setCheck("tests", CheckState.PASSED);
        pr.setCheck("security", CheckState.PASSED);

        ProtectionPolicy policy = new ProtectionPolicy(
            2,
            Set.of("build", "tests", "security"),
            true,
            true,
            true
        );

        GovernanceService governance = new GovernanceService();

        List<String> blockers =
            governance.evaluateMergeEligibility(pr, policy);

        System.out.println("\nMERGE ELIGIBILITY");

        if (blockers.isEmpty()) {
            System.out.println("All governance conditions satisfied.");
        } else {
            blockers.forEach(System.out::println);
        }

        // Test a failure state.
        pr.updateConversations(false);

        blockers = governance.evaluateMergeEligibility(pr, policy);

        System.out.println("\nFAILURE SCENARIO");

        blockers.forEach(System.out::println);
    }
}
