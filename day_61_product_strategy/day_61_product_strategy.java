import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ProductStrategyGovernance {

    enum ProductStage {
        DISCOVERY, VALIDATION, DELIVERY, SCALE
    }

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record ProductGoal(
            String name,
            String metric,
            double target,
            double current) {

        ProductGoal {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Goal name is required.");
            }
            if (metric == null || metric.isBlank()) {
                throw new IllegalArgumentException("Goal metric is required.");
            }
            if (target <= 0 || Double.isNaN(target)) {
                throw new IllegalArgumentException("Goal target must be positive.");
            }
            if (current < 0 || Double.isNaN(current)) {
                throw new IllegalArgumentException(
                        "Goal current value must be non-negative.");
            }
        }

        boolean achieved() {
            return current >= target;
        }
    }

    record Commit(
            String sha,
            String message,
            String author,
            Instant createdAt) {

        Commit {
            if (sha == null || !sha.matches("[A-Fa-f0-9]{8,64}")) {
                throw new IllegalArgumentException("Invalid commit SHA.");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required.");
            }
        }
    }

    record Review(
            String reviewer,
            ReviewState state,
            String reviewedCommit,
            Instant createdAt) {

        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            if (reviewedCommit == null || reviewedCommit.isBlank()) {
                throw new IllegalArgumentException(
                        "Reviewed commit is required.");
            }
        }
    }

    record ProductStrategy(
            String vision,
            String mission,
            List<String> strategicChoices,
            List<ProductGoal> goals) {

        ProductStrategy {
            if (vision == null || vision.isBlank()) {
                throw new IllegalArgumentException("Vision is required.");
            }
            if (mission == null || mission.isBlank()) {
                throw new IllegalArgumentException("Mission is required.");
            }

            strategicChoices = List.copyOf(strategicChoices);
            goals = List.copyOf(goals);
        }

        double score() {
            if (goals.isEmpty()) {
                return 0.0;
            }

            return goals.stream()
                    .mapToDouble(goal ->
                            Math.min(goal.current() / goal.target(), 1.0))
                    .average()
                    .orElse(0.0);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String title;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<Commit> commits = new ArrayList<>();
        private final List<Review> reviews = new ArrayList<>();
        private final Map<String, Boolean> statusChecks = new HashMap<>();
        private final Set<String> openConversations = new HashSet<>();

        private PullRequestState state;
        private MergeStrategy mergeStrategy = MergeStrategy.SQUASH;
        private boolean draft;

        PullRequest(
                int number,
                String title,
                String author,
                String sourceBranch,
                String targetBranch,
                boolean draft) {

            if (number <= 0) {
                throw new IllegalArgumentException(
                        "Pull Request number must be positive.");
            }

            this.number = number;
            this.title = requireText(title, "Title");
            this.author = requireText(author, "Author");
            this.sourceBranch = requireText(sourceBranch, "Source branch");
            this.targetBranch = requireText(targetBranch, "Target branch");
            this.draft = draft;
            this.state = draft
                    ? PullRequestState.DRAFT
                    : PullRequestState.OPEN;
        }

        private static String requireText(String value, String field) {
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException(field + " is required.");
            }
            return value;
        }

        void addCommit(Commit commit) {
            if (state == PullRequestState.MERGED) {
                throw new IllegalStateException(
                        "Cannot modify a merged Pull Request.");
            }
            commits.add(commit);
        }

        void addReview(Review review) {
            if (state == PullRequestState.MERGED ||
                    state == PullRequestState.CLOSED) {
                throw new IllegalStateException(
                        "Closed or merged PR cannot receive reviews.");
            }
            reviews.add(review);
        }

        void setStatus(String name, boolean passed) {
            statusChecks.put(requireText(name, "Status check"), passed);
        }

        void openConversation(String id) {
            openConversations.add(requireText(id, "Conversation ID"));
        }

        void resolveConversation(String id) {
            openConversations.remove(id);
        }

        String headCommit() {
            if (commits.isEmpty()) {
                throw new IllegalStateException(
                        "Pull Request contains no commits.");
            }
            return commits.get(commits.size() - 1).sha();
        }

        int number() {
            return number;
        }

        String targetBranch() {
            return targetBranch;
        }

        PullRequestState state() {
            return state;
        }

        boolean draft() {
            return draft;
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        Map<String, Boolean> statusChecks() {
            return Map.copyOf(statusChecks);
        }

        Set<String> openConversations() {
            return Set.copyOf(openConversations);
        }

        void markMerged() {
            state = PullRequestState.MERGED;
        }

        void setMergeStrategy(MergeStrategy strategy) {
            this.mergeStrategy = strategy;
        }

        MergeStrategy mergeStrategy() {
            return mergeStrategy;
        }
    }

    record BranchProtection(
            String branch,
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireResolvedConversations,
            boolean allowDirectPush,
            boolean allowForcePush,
            boolean allowDeletion,
            boolean requireLinearHistory,
            boolean allowAdministratorBypass) {

        BranchProtection {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                        "Required approvals cannot be negative.");
            }

            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    static final class Repository {
        private final String name;
        private final Set<String> branches = new HashSet<>();
        private final Map<Integer, PullRequest> pullRequests = new HashMap<>();
        private final Map<String, BranchProtection> protections = new HashMap<>();

        Repository(String name) {
            this.name = requireText(name, "Repository name");
        }

        private static String requireText(String value, String field) {
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException(field + " is required.");
            }
            return value;
        }

        void addBranch(String branch) {
            branches.add(requireText(branch, "Branch name"));
        }

        void protectBranch(BranchProtection policy) {
            if (!branches.contains(policy.branch())) {
                throw new IllegalArgumentException(
                        "Protected branch does not exist.");
            }
            protections.put(policy.branch(), policy);
        }

        void addPullRequest(PullRequest pr) {
            if (!branches.contains(pr.targetBranch())) {
                throw new IllegalArgumentException(
                        "Pull Request target branch does not exist.");
            }

            if (pullRequests.containsKey(pr.number())) {
                throw new IllegalArgumentException(
                        "Pull Request number already exists.");
            }

            pullRequests.put(pr.number(), pr);
        }

        PullRequest pullRequest(int number) {
            PullRequest pr = pullRequests.get(number);
            if (pr == null) {
                throw new IllegalArgumentException(
                        "Pull Request does not exist.");
            }
            return pr;
        }

        BranchProtection protection(String branch) {
            BranchProtection policy = protections.get(branch);
            if (policy == null) {
                throw new IllegalStateException(
                        "Branch has no protection policy.");
            }
            return policy;
        }
    }

    record Eligibility(boolean eligible, List<String> reasons) {
    }

    static final class MergeEligibilityService {

        Eligibility evaluate(
                PullRequest pr,
                BranchProtection policy) {

            List<String> reasons = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                reasons.add("Pull Request is not open.");
            }

            if (pr.draft()) {
                reasons.add("Draft Pull Requests cannot be merged.");
            }

            String head;
            try {
                head = pr.headCommit();
            } catch (IllegalStateException exception) {
                reasons.add(exception.getMessage());
                return new Eligibility(false, List.copyOf(reasons));
            }

            Set<String> approvals = new HashSet<>();
            Set<String> requestedChanges = new HashSet<>();

            for (Review review : pr.reviews()) {
                if (review.state() == ReviewState.APPROVED &&
                        review.reviewedCommit().equals(head)) {
                    approvals.add(review.reviewer());
                }

                if (review.state() == ReviewState.CHANGES_REQUESTED) {
                    requestedChanges.add(review.reviewer());
                }
            }

            if (!requestedChanges.isEmpty()) {
                reasons.add("Requested changes remain from: " +
                        String.join(", ", requestedChanges));
            }

            if (approvals.size() < policy.requiredApprovals()) {
                reasons.add(
                        "Current approvals: " + approvals.size() +
                        "; required: " + policy.requiredApprovals());
            }

            for (String requiredCheck : policy.requiredChecks()) {
                if (!Boolean.TRUE.equals(
                        pr.statusChecks().get(requiredCheck))) {
                    reasons.add(
                            "Required check failed or is missing: " +
                            requiredCheck);
                }
            }

            if (policy.requireResolvedConversations() &&
                    !pr.openConversations().isEmpty()) {
                reasons.add(
                        "Unresolved conversations: " +
                        pr.openConversations().size());
            }

            return new Eligibility(
                    reasons.isEmpty(),
                    List.copyOf(reasons));
        }

        String merge(
                Repository repository,
                int number) {

            PullRequest pr = repository.pullRequest(number);
            BranchProtection policy = repository.protection(
                    pr.targetBranch());

            Eligibility result = evaluate(pr, policy);

            if (!result.eligible()) {
                return "MERGE BLOCKED\n- " +
                        String.join("\n- ", result.reasons());
            }

            pr.markMerged();

            return "MERGED PR #" + pr.number() +
                    " using " +
                    pr.mergeStrategy().name().toLowerCase();
        }
    }

    private static ProductStrategy createStrategy() {
        return new ProductStrategy(
                "Make repository change management predictable, reviewable, and safe.",
                "Connect product intent with controlled engineering delivery.",
                List.of(
                        "Use Pull Requests as the controlled change-entry workflow.",
                        "Separate review decisions from repository enforcement.",
                        "Tie approvals to the exact commit under evaluation.",
                        "Use automated checks as objective merge evidence.",
                        "Protect critical branches from uncontrolled writes."
                ),
                List.of(
                        new ProductGoal(
                                "review_coverage",
                                "production PRs reviewed",
                                95,
                                92),
                        new ProductGoal(
                                "compliant_merges",
                                "policy-compliant merges",
                                90,
                                94)
                )
        );
    }

    private static PullRequest createHealthyPullRequest() {
        PullRequest pr = new PullRequest(
                142,
                "Introduce product strategy governance metrics",
                "atul",
                "feature/product-strategy",
                "main",
                false);

        pr.addCommit(new Commit(
                "a1b2c3d4",
                "Implement product strategy model",
                "atul",
                Instant.now()));

        pr.addCommit(new Commit(
                "e5f6a7b8",
                "Address review findings",
                "atul",
                Instant.now()));

        pr.addReview(new Review(
                "maya",
                ReviewState.APPROVED,
                "e5f6a7b8",
                Instant.now()));

        pr.addReview(new Review(
                "rohan",
                ReviewState.APPROVED,
                "e5f6a7b8",
                Instant.now()));

        pr.setStatus("unit-tests", true);
        pr.setStatus("security-scan", true);
        pr.setStatus("product-policy", true);

        return pr;
    }

    private static PullRequest createStaleApprovalPullRequest() {
        PullRequest pr = new PullRequest(
                143,
                "Change product governance policy",
                "atul",
                "feature/product-strategy",
                "main",
                false);

        pr.addCommit(new Commit(
                "11111111",
                "Initial governance policy",
                "atul",
                Instant.now()));

        pr.addCommit(new Commit(
                "22222222",
                "Modify governance policy after review",
                "atul",
                Instant.now()));

        pr.addReview(new Review(
                "maya",
                ReviewState.APPROVED,
                "11111111",
                Instant.now()));

        pr.addReview(new Review(
                "rohan",
                ReviewState.APPROVED,
                "11111111",
                Instant.now()));

        pr.setStatus("unit-tests", true);
        pr.setStatus("security-scan", true);
        pr.setStatus("product-policy", true);

        return pr;
    }

    public static void main(String[] args) {
        ProductStrategy strategy = createStrategy();

        System.out.println("PRODUCT STRATEGY");
        System.out.println("===============================");
        System.out.println("Vision: " + strategy.vision());
        System.out.println("Mission: " + strategy.mission());
        System.out.printf(
                "Strategy score: %.1f%%%n%n",
                strategy.score() * 100.0);

        Repository repository = new Repository("payment-platform");

        repository.addBranch("main");
        repository.addBranch("feature/product-strategy");

        repository.protectBranch(
                new BranchProtection(
                        "main",
                        2,
                        Set.of(
                                "unit-tests",
                                "security-scan",
                                "product-policy"),
                        true,
                        false,
                        false,
                        false,
                        true,
                        false));

        repository.addPullRequest(createHealthyPullRequest());
        repository.addPullRequest(createStaleApprovalPullRequest());

        MergeEligibilityService service =
                new MergeEligibilityService();

        System.out.println("HEALTHY PULL REQUEST");
        System.out.println("===============================");

        Eligibility healthy = service.evaluate(
                repository.pullRequest(142),
                repository.protection("main"));

        System.out.println("Eligible: " + healthy.eligible());
        healthy.reasons().forEach(reason ->
                System.out.println("- " + reason));

        System.out.println(service.merge(repository, 142));
        System.out.println();

        System.out.println("STALE APPROVAL CASE");
        System.out.println("===============================");

        Eligibility stale = service.evaluate(
                repository.pullRequest(143),
                repository.protection("main"));

        System.out.println("Eligible: " + stale.eligible());
        stale.reasons().forEach(reason ->
                System.out.println("- " + reason));
    }
}
