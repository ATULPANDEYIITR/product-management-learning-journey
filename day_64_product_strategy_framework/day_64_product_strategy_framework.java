import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class RepositoryGovernance {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, APPROVED, CHANGES_REQUESTED, DISMISSED
    }

    enum CheckState {
        PENDING, PASSED, FAILED
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class Commit {
        final String sha;
        final String message;
        final String author;

        Commit(String sha, String message, String author) {
            if (sha == null || sha.isBlank()
                    || message == null || message.isBlank()
                    || author == null || author.isBlank()) {
                throw new ValidationException("Invalid commit.");
            }

            this.sha = sha;
            this.message = message;
            this.author = author;
        }
    }

    static class Branch {
        final String name;
        final List<Commit> commits = new ArrayList<>();
        boolean protectedBranch;

        Branch(String name, List<Commit> initialCommits) {
            if (name == null || name.isBlank()) {
                throw new ValidationException("Branch name is required.");
            }

            this.name = name;
            this.commits.addAll(initialCommits);
        }

        String head() {
            return commits.isEmpty()
                    ? null
                    : commits.get(commits.size() - 1).sha;
        }
    }

    record ReviewComment(
            String reviewer,
            String filePath,
            int line,
            String body,
            boolean resolved) {

        ReviewComment {
            if (reviewer == null || reviewer.isBlank()
                    || filePath == null || filePath.isBlank()
                    || line < 1
                    || body == null || body.isBlank()) {
                throw new ValidationException("Invalid review comment.");
            }
        }
    }

    static class Review {
        final String reviewer;
        ReviewState state;
        final List<ReviewComment> comments;
        boolean stale;
        boolean dismissed;

        Review(
                String reviewer,
                ReviewState state,
                List<ReviewComment> comments) {

            if (reviewer == null || reviewer.isBlank()) {
                throw new ValidationException("Reviewer is required.");
            }

            this.reviewer = reviewer;
            this.state = state;
            this.comments = new ArrayList<>(comments);
            this.dismissed = state == ReviewState.DISMISSED;
        }
    }

    record StatusCheck(String name, CheckState state) {
        StatusCheck {
            if (name == null || name.isBlank() || state == null) {
                throw new ValidationException("Invalid status check.");
            }
        }
    }

    record BranchProtectionPolicy(
            int requiredApprovals,
            Set<String> requiredChecks,
            boolean requireConversationsResolved,
            boolean requireLinearHistory,
            boolean allowDirectPush,
            boolean allowForcePush,
            boolean allowBranchDeletion,
            boolean allowAdminBypass,
            Set<MergeStrategy> allowedMergeStrategies) {

        BranchProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new ValidationException(
                        "Approval count cannot be negative.");
            }

            requiredChecks = Set.copyOf(requiredChecks);
            allowedMergeStrategies =
                    EnumSet.copyOf(allowedMergeStrategies);
        }
    }

    static class PullRequest {
        final int number;
        final String title;
        final String sourceBranch;
        final String targetBranch;
        final String author;
        PullRequestState state;
        final List<Commit> commits;
        final List<Review> reviews = new ArrayList<>();
        final Map<String, StatusCheck> checks = new HashMap<>();
        final Set<String> requestedReviewers = new HashSet<>();
        String baseHeadAtCreation;

        PullRequest(
                int number,
                String title,
                String sourceBranch,
                String targetBranch,
                String author,
                PullRequestState state,
                List<Commit> commits,
                String baseHeadAtCreation) {

            this.number = number;
            this.title = title;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.author = author;
            this.state = state;
            this.commits = new ArrayList<>(commits);
            this.baseHeadAtCreation = baseHeadAtCreation;
        }

        void requestReview(String reviewer) {
            if (reviewer.equals(author)) {
                throw new ValidationException(
                        "Authors cannot review their own Pull Request.");
            }
            requestedReviewers.add(reviewer);
        }

        void addReview(Review review) {
            if (review.reviewer.equals(author)) {
                throw new ValidationException("Self-review is prohibited.");
            }
            reviews.add(review);
        }

        void addCommit(Commit commit) {
            if (state != PullRequestState.OPEN
                    && state != PullRequestState.DRAFT) {
                throw new ValidationException(
                        "Cannot modify closed or merged Pull Request.");
            }

            commits.add(commit);

            for (Review review : reviews) {
                if (review.state == ReviewState.APPROVED) {
                    review.stale = true;
                }
            }
        }

        void setStatusCheck(StatusCheck check) {
            checks.put(check.name(), check);
        }
    }

    record MergeDecision(
            boolean eligible,
            List<String> reasons) {
    }

    static class MergeEligibilityService {

        MergeDecision evaluate(
                PullRequest pr,
                Branch target,
                BranchProtectionPolicy policy,
                MergeStrategy strategy,
                boolean administrator) {

            List<String> reasons = new ArrayList<>();

            if (pr.state != PullRequestState.OPEN) {
                reasons.add("Pull Request is not open.");
            }

            if (pr.commits.isEmpty()) {
                reasons.add("Pull Request contains no changes.");
            }

            if (!policy.allowedMergeStrategies().contains(strategy)) {
                reasons.add("Selected merge strategy is not permitted.");
            }

            Set<String> validApprovers = new HashSet<>();

            for (Review review : pr.reviews) {
                if (review.state == ReviewState.APPROVED
                        && !review.stale
                        && !review.dismissed
                        && pr.requestedReviewers.contains(review.reviewer)) {
                    validApprovers.add(review.reviewer);
                }
            }

            if (validApprovers.size() < policy.requiredApprovals()) {
                reasons.add(
                        "Required approvals not satisfied: "
                                + validApprovers.size()
                                + "/"
                                + policy.requiredApprovals()
                );
            }

            for (String required : policy.requiredChecks()) {
                StatusCheck check = pr.checks.get(required);

                if (check == null || check.state() != CheckState.PASSED) {
                    reasons.add(
                            "Required status check is missing or failed: "
                                    + required
                    );
                }
            }

            if (policy.requireConversationsResolved()) {
                boolean unresolved = pr.reviews.stream()
                        .flatMap(review -> review.comments.stream())
                        .anyMatch(comment -> !comment.resolved());

                if (unresolved) {
                    reasons.add("Unresolved review conversations remain.");
                }
            }

            if (policy.requireLinearHistory()
                    && strategy == MergeStrategy.MERGE_COMMIT) {
                reasons.add(
                        "Merge commits violate the linear-history policy.");
            }

            boolean changesRequested = pr.reviews.stream()
                    .anyMatch(review ->
                            review.state == ReviewState.CHANGES_REQUESTED
                                    && !review.dismissed);

            if (changesRequested) {
                reasons.add("A reviewer has requested changes.");
            }

            if (administrator && policy.allowAdminBypass()) {
                return new MergeDecision(
                        pr.state == PullRequestState.OPEN
                                && !pr.commits.isEmpty(),
                        List.of()
                );
            }

            return new MergeDecision(
                    reasons.isEmpty(),
                    List.copyOf(reasons)
            );
        }
    }

    static class RepositoryService {
        private final Map<String, Branch> branches = new HashMap<>();
        private final Map<Integer, PullRequest> pullRequests =
                new HashMap<>();
        private final Map<String, BranchProtectionPolicy> policies =
                new HashMap<>();
        private final MergeEligibilityService eligibilityService =
                new MergeEligibilityService();

        private int nextPR = 1;

        void addBranch(Branch branch) {
            if (branches.containsKey(branch.name)) {
                throw new ValidationException("Duplicate branch.");
            }
            branches.put(branch.name, branch);
        }

        void protectBranch(
                String branchName,
                BranchProtectionPolicy policy) {

            Branch branch = branches.get(branchName);

            if (branch == null) {
                throw new ValidationException("Unknown branch.");
            }

            branch.protectedBranch = true;
            policies.put(branchName, policy);
        }

        PullRequest createPullRequest(
                String title,
                String source,
                String target,
                String author,
                boolean draft) {

            Branch sourceBranch = branches.get(source);
            Branch targetBranch = branches.get(target);

            if (sourceBranch == null || targetBranch == null) {
                throw new ValidationException(
                        "Source and target branches must exist.");
            }

            if (source.equals(target)) {
                throw new ValidationException(
                        "Source and target must differ.");
            }

            PullRequest pr = new PullRequest(
                    nextPR++,
                    title,
                    source,
                    target,
                    author,
                    draft
                            ? PullRequestState.DRAFT
                            : PullRequestState.OPEN,
                    sourceBranch.commits,
                    targetBranch.head()
            );

            pullRequests.put(pr.number, pr);
            return pr;
        }

        MergeDecision evaluate(
                int prNumber,
                MergeStrategy strategy,
                boolean administrator) {

            PullRequest pr = pullRequests.get(prNumber);

            if (pr == null) {
                throw new ValidationException("Unknown Pull Request.");
            }

            Branch target = branches.get(pr.targetBranch);
            BranchProtectionPolicy policy =
                    policies.get(pr.targetBranch);

            if (policy == null) {
                throw new ValidationException(
                        "Target branch has no protection policy.");
            }

            return eligibilityService.evaluate(
                    pr,
                    target,
                    policy,
                    strategy,
                    administrator
            );
        }

        void merge(
                int prNumber,
                String actor,
                MergeStrategy strategy) {

            PullRequest pr = pullRequests.get(prNumber);

            if (pr == null) {
                throw new ValidationException("Unknown Pull Request.");
            }

            MergeDecision decision =
                    evaluate(prNumber, strategy, false);

            if (!decision.eligible()) {
                throw new IllegalStateException(
                        "Merge blocked: "
                                + String.join(
                                " | ",
                                decision.reasons())
                );
            }

            Branch target = branches.get(pr.targetBranch);

            switch (strategy) {
                case SQUASH -> target.commits.add(
                        new Commit(
                                "squash-" + pr.number,
                                pr.title,
                                actor
                        )
                );

                case MERGE_COMMIT -> target.commits.add(
                        new Commit(
                                "merge-" + pr.number,
                                "Merge PR #" + pr.number,
                                actor
                        )
                );

                case REBASE -> target.commits.addAll(pr.commits);
            }

            pr.state = PullRequestState.MERGED;
        }
    }

    public static void main(String[] args) {
        RepositoryService repository = new RepositoryService();

        List<Commit> baseCommits = List.of(
                new Commit("c001", "Initial release", "alice"),
                new Commit("c002", "Add payment service", "alice")
        );

        repository.addBranch(
                new Branch("main", baseCommits)
        );

        repository.addBranch(
                new Branch(
                        "feature/refunds",
                        List.of(
                                baseCommits.get(0),
                                baseCommits.get(1),
                                new Commit(
                                        "c003",
                                        "Implement refund API",
                                        "bob"
                                )
                        )
                )
        );

        BranchProtectionPolicy policy =
                new BranchProtectionPolicy(
                        2,
                        Set.of("unit-tests", "security-scan"),
                        true,
                        true,
                        false,
                        false,
                        false,
                        false,
                        EnumSet.of(
                                MergeStrategy.SQUASH,
                                MergeStrategy.REBASE
                        )
                );

        repository.protectBranch("main", policy);

        PullRequest pr = repository.createPullRequest(
                "Implement refund API",
                "feature/refunds",
                "main",
                "bob",
                false
        );

        pr.requestReview("alice");
        pr.requestReview("carol");

        pr.addReview(
                new Review(
                        "alice",
                        ReviewState.APPROVED,
                        List.of(
                                new ReviewComment(
                                        "alice",
                                        "RefundService.java",
                                        48,
                                        "Validate the refund amount.",
                                        true
                                )
                        )
                )
        );

        pr.addReview(
                new Review(
                        "carol",
                        ReviewState.APPROVED,
                        List.of()
                )
        );

        pr.setStatusCheck(
                new StatusCheck(
                        "unit-tests",
                        CheckState.PASSED
                )
        );

        pr.setStatusCheck(
                new StatusCheck(
                        "security-scan",
                        CheckState.PASSED
                )
        );

        MergeDecision decision =
                repository.evaluate(
                        pr.number,
                        MergeStrategy.SQUASH,
                        false
                );

        System.out.println(
                "PR #" + pr.number
                        + " eligible: "
                        + decision.eligible()
        );

        decision.reasons().forEach(
                reason -> System.out.println("BLOCKED: " + reason)
        );

        repository.merge(
                pr.number,
                "release-manager",
                MergeStrategy.SQUASH
        );

        System.out.println("PR state: " + pr.state);
        System.out.println(
                "main HEAD: "
                        + repository.branches.get("main").head()
        );

        // New commits make previous approvals stale.
        PullRequest second = repository.createPullRequest(
                "Improve refund validation",
                "feature/refunds",
                "main",
                "david",
                false
        );

        second.requestReview("alice");

        second.addReview(
                new Review(
                        "alice",
                        ReviewState.APPROVED,
                        List.of()
                )
        );

        second.setStatusCheck(
                new StatusCheck(
                        "unit-tests",
                        CheckState.PASSED
                )
        );

        second.setStatusCheck(
                new StatusCheck(
                        "security-scan",
                        CheckState.PASSED
                )
        );

        second.addCommit(
                new Commit(
                        "c004",
                        "Handle invalid refund amount",
                        "david"
                )
        );

        MergeDecision staleDecision =
                repository.evaluate(
                        second.number,
                        MergeStrategy.SQUASH,
                        false
                );

        System.out.println(
                "PR #" + second.number
                        + " eligible after new commit: "
                        + staleDecision.eligible()
        );

        staleDecision.reasons().forEach(
                reason -> System.out.println("BLOCKED: " + reason)
        );
    }
}
