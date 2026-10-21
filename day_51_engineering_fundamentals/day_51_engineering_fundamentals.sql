import java.time.Instant;
import java.util.*;

public class RepositoryGovernance {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record Commit(String sha, String message) {
        Commit {
            if (sha == null || sha.isBlank() || message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit SHA and message are required.");
            }
        }
    }

    record Review(
        String reviewer,
        ReviewState state,
        String comment,
        Instant submittedAt
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            if (state == null) {
                throw new IllegalArgumentException("Review state is required.");
            }
        }
    }

    record StatusCheck(String name, boolean passed) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Status check name is required.");
            }
        }
    }

    record BranchProtectionPolicy(
        String branch,
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean requireLinearHistory,
        boolean allowDirectPush,
        boolean allowForcePush,
        boolean allowDeletion
    ) {
        BranchProtectionPolicy {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException("Approval count cannot be negative.");
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    static final class PullRequest {
        private final int number;
        private final String title;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;

        private PullRequestState state = PullRequestState.DRAFT;

        private final List<Commit> commits = new ArrayList<>();
        private final Set<String> requestedReviewers = new HashSet<>();
        private final Map<String, Review> reviews = new HashMap<>();
        private final Map<String, StatusCheck> checks = new HashMap<>();

        private int unresolvedConversations;
        private boolean mergeConflict;
        private boolean synchronizedWithBase = true;

        PullRequest(
            int number,
            String title,
            String author,
            String sourceBranch,
            String targetBranch
        ) {
            if (number <= 0) {
                throw new IllegalArgumentException("Pull Request number must be positive.");
            }

            if (sourceBranch == null || targetBranch == null ||
                sourceBranch.isBlank() || targetBranch.isBlank()) {
                throw new IllegalArgumentException("Both branches are required.");
            }

            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Source and target branches must differ.");
            }

            this.number = number;
            this.title = Objects.requireNonNull(title);
            this.author = Objects.requireNonNull(author);
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
        }

        void addCommit(Commit commit) {
            ensureMutable();
            commits.add(Objects.requireNonNull(commit));

            // New commits may require the Pull Request to be synchronized again.
            synchronizedWithBase = false;
        }

        void open() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException("Only draft Pull Requests can be opened.");
            }

            if (commits.isEmpty()) {
                throw new IllegalStateException("At least one commit is required.");
            }

            state = PullRequestState.OPEN;
        }

        void requestReview(String reviewer) {
            ensureOpen();

            if (reviewer == null || reviewer.isBlank() || reviewer.equals(author)) {
                throw new IllegalArgumentException("Invalid reviewer.");
            }

            requestedReviewers.add(reviewer);
        }

        void submitReview(
            String reviewer,
            ReviewState reviewState,
            String comment
        ) {
            ensureOpen();

            if (!requestedReviewers.contains(reviewer)) {
                throw new IllegalStateException("Reviewer was not requested.");
            }

            if (reviewer.equals(author)) {
                throw new SecurityException("Self-review is prohibited.");
            }

            reviews.put(
                reviewer,
                new Review(
                    reviewer,
                    reviewState,
                    comment == null ? "" : comment,
                    Instant.now()
                )
            );
        }

        void updateStatusCheck(String name, boolean passed) {
            checks.put(name, new StatusCheck(name, passed));
        }

        void addConversation() {
            ensureOpen();
            unresolvedConversations++;
        }

        void resolveConversation() {
            if (unresolvedConversations == 0) {
                throw new IllegalStateException("No unresolved conversations exist.");
            }
            unresolvedConversations--;
        }

        void resolveConflict() {
            mergeConflict = false;
            synchronizedWithBase = false;
        }

        void synchronizeWithBase() {
            if (mergeConflict) {
                throw new IllegalStateException("Cannot synchronize while conflicts exist.");
            }
            synchronizedWithBase = true;
        }

        void introduceConflict() {
            mergeConflict = true;
            synchronizedWithBase = false;
        }

        long approvalCount() {
            return reviews.values().stream()
                .filter(review -> review.state() == ReviewState.APPROVED)
                .count();
        }

        Collection<Review> reviews() {
            return Collections.unmodifiableCollection(reviews.values());
        }

        Map<String, StatusCheck> checks() {
            return Collections.unmodifiableMap(checks);
        }

        int unresolvedConversations() {
            return unresolvedConversations;
        }

        boolean hasConflict() {
            return mergeConflict;
        }

        boolean synchronizedWithBase() {
            return synchronizedWithBase;
        }

        PullRequestState state() {
            return state;
        }

        String targetBranch() {
            return targetBranch;
        }

        void merge(MergeStrategy strategy) {
            ensureOpen();

            if (strategy == null) {
                throw new IllegalArgumentException("Merge strategy is required.");
            }

            state = PullRequestState.MERGED;
        }

        private void ensureOpen() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Pull Request must be open.");
            }
        }

        private void ensureMutable() {
            if (state == PullRequestState.CLOSED ||
                state == PullRequestState.MERGED) {
                throw new IllegalStateException(
                    "Closed and merged Pull Requests are immutable."
                );
            }
        }
    }

    record MergeDecision(boolean eligible, List<String> blockers) {
        MergeDecision {
            blockers = List.copyOf(blockers);
        }
    }

    static final class MergeEligibilityService {

        MergeDecision evaluate(
            PullRequest pullRequest,
            BranchProtectionPolicy policy
        ) {
            List<String> blockers = new ArrayList<>();

            if (pullRequest.state() != PullRequestState.OPEN) {
                blockers.add("Pull Request is not open.");
            }

            if (pullRequest.hasConflict()) {
                blockers.add("Merge conflicts exist.");
            }

            if (!pullRequest.synchronizedWithBase()) {
                blockers.add("Pull Request is not synchronized with the base branch.");
            }

            if (
                policy.requireResolvedConversations() &&
                pullRequest.unresolvedConversations() > 0
            ) {
                blockers.add("Unresolved review conversations remain.");
            }

            if (pullRequest.approvalCount() < policy.requiredApprovals()) {
                blockers.add(
                    "Required approvals: " + policy.requiredApprovals()
                        + ", received: " + pullRequest.approvalCount() + "."
                );
            }

            for (String requiredCheck : policy.requiredChecks()) {
                StatusCheck check = pullRequest.checks().get(requiredCheck);

                if (check == null || !check.passed()) {
                    blockers.add(
                        "Required status check failed or is missing: "
                            + requiredCheck
                    );
                }
            }

            return new MergeDecision(blockers.isEmpty(), blockers);
        }

        void merge(
            PullRequest pullRequest,
            BranchProtectionPolicy policy,
            MergeStrategy strategy
        ) {
            MergeDecision decision = evaluate(pullRequest, policy);

            if (!decision.eligible()) {
                throw new IllegalStateException(
                    "Merge blocked: " + String.join(" ", decision.blockers())
                );
            }

            pullRequest.merge(strategy);
        }
    }

    public static void main(String[] args) {
        BranchProtectionPolicy policy = new BranchProtectionPolicy(
            "main",
            2,
            Set.of("build", "tests", "security"),
            true,
            true,
            false,
            false,
            false
        );

        PullRequest pullRequest = new PullRequest(
            500,
            "Harden customer authorization",
            "alice",
            "feature/customer-auth",
            "main"
        );

        pullRequest.addCommit(
            new Commit("c001", "Validate authorization token")
        );
        pullRequest.addCommit(
            new Commit("c002", "Reject unauthorized customer access")
        );

        pullRequest.open();

        pullRequest.requestReview("bob");
        pullRequest.requestReview("carol");

        pullRequest.submitReview(
            "bob",
            ReviewState.APPROVED,
            "Authorization boundary is correct."
        );

        pullRequest.submitReview(
            "carol",
            ReviewState.APPROVED,
            "Failure behavior is explicit."
        );

        pullRequest.updateStatusCheck("build", true);
        pullRequest.updateStatusCheck("tests", true);
        pullRequest.updateStatusCheck("security", true);

        pullRequest.addConversation();

        MergeEligibilityService service = new MergeEligibilityService();

        MergeDecision blocked = service.evaluate(pullRequest, policy);
        System.out.println("Eligible before discussion resolution: "
            + blocked.eligible());
        blocked.blockers().forEach(blocker ->
            System.out.println("Blocker: " + blocker)
        );

        pullRequest.resolveConversation();
        pullRequest.synchronizeWithBase();

        MergeDecision eligible = service.evaluate(pullRequest, policy);
        System.out.println("Eligible after resolution: "
            + eligible.eligible());

        service.merge(
            pullRequest,
            policy,
            MergeStrategy.SQUASH
        );

        System.out.println("Pull Request state: " + pullRequest.state());

        try {
            pullRequest.addCommit(
                new Commit("c003", "Attempt modification after merge")
            );
        } catch (IllegalStateException exception) {
            System.out.println("Expected failure: " + exception.getMessage());
        }
    }
}
