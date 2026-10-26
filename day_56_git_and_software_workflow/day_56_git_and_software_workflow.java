import java.time.Instant;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
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
        MERGE, SQUASH, REBASE
    }

    record Commit(
        String sha,
        String author,
        String message,
        Instant createdAt
    ) {}

    record Review(
        String reviewer,
        ReviewState state,
        String commitSha,
        List<String> comments
    ) {
        Review {
            comments = List.copyOf(comments);
        }
    }

    record StatusCheck(
        String name,
        CheckState state,
        String commitSha
    ) {}

    record ProtectionPolicy(
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean allowDirectPush,
        boolean allowForcePush,
        boolean allowDeletion,
        boolean requireLinearHistory,
        Set<MergeStrategy> allowedStrategies
    ) {
        ProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Approval requirement cannot be negative"
                );
            }
            requiredChecks = Set.copyOf(requiredChecks);
            allowedStrategies = Set.copyOf(allowedStrategies);
        }
    }

    static final class Branch {
        private final String name;
        private final List<Commit> commits = new ArrayList<>();

        Branch(String name) {
            this.name = Objects.requireNonNull(name);
        }

        String name() {
            return name;
        }

        List<Commit> commits() {
            return commits;
        }

        String headSha() {
            if (commits.isEmpty()) {
                return null;
            }
            return commits.getLast().sha();
        }
    }

    static final class PullRequest {
        private final int number;
        private final String source;
        private final String target;
        private final String author;

        private PullRequestState state;
        private final List<Commit> commits;
        private final List<Review> reviews = new ArrayList<>();
        private final List<StatusCheck> checks = new ArrayList<>();
        private int unresolvedConversations;
        private boolean synchronizedWithSource = true;
        private MergeStrategy mergeStrategy;

        PullRequest(
            int number,
            String source,
            String target,
            String author,
            PullRequestState state,
            List<Commit> commits
        ) {
            this.number = number;
            this.source = source;
            this.target = target;
            this.author = author;
            this.state = state;
            this.commits = new ArrayList<>(commits);
        }

        int number() {
            return number;
        }

        String source() {
            return source;
        }

        String target() {
            return target;
        }

        String author() {
            return author;
        }

        PullRequestState state() {
            return state;
        }

        String headSha() {
            return commits.isEmpty()
                ? null
                : commits.getLast().sha();
        }
    }

    static final class GovernanceException extends RuntimeException {
        GovernanceException(String message) {
            super(message);
        }
    }

    static final class MergeEligibility {
        private final List<String> reasons;

        MergeEligibility(List<String> reasons) {
            this.reasons = List.copyOf(reasons);
        }

        boolean eligible() {
            return reasons.isEmpty();
        }

        List<String> reasons() {
            return reasons;
        }
    }

    interface ReviewPolicy {
        boolean eligibleReviewer(
            PullRequest pullRequest,
            String reviewer
        );

        boolean blocksMerge(Review review, String headSha);
    }

    static final class StandardReviewPolicy implements ReviewPolicy {

        @Override
        public boolean eligibleReviewer(
            PullRequest pullRequest,
            String reviewer
        ) {
            return !pullRequest.author().equals(reviewer);
        }

        @Override
        public boolean blocksMerge(
            Review review,
            String headSha
        ) {
            return review.state() == ReviewState.CHANGES_REQUESTED
                && review.commitSha().equals(headSha);
        }
    }

    static final class RepositoryService {
        private final Map<String, Branch> branches = new HashMap<>();
        private final Map<Integer, PullRequest> pullRequests = new HashMap<>();
        private final Map<String, ProtectionPolicy> policies = new HashMap<>();
        private final Set<String> users = new HashSet<>();
        private final ReviewPolicy reviewPolicy = new StandardReviewPolicy();

        private int nextPr = 1;

        void addUser(String user) {
            requireText(user, "User");
            users.add(user);
        }

        void createBranch(String name) {
            requireText(name, "Branch");
            if (branches.containsKey(name)) {
                throw new GovernanceException("Branch already exists");
            }
            branches.put(name, new Branch(name));
        }

        void protectBranch(
            String branch,
            ProtectionPolicy policy
        ) {
            requireBranch(branch);
            policies.put(branch, policy);
        }

        Commit commit(
            String branch,
            String author,
            String message
        ) {
            requireBranch(branch);
            if (!users.contains(author)) {
                throw new GovernanceException("Unknown author");
            }
            requireText(message, "Commit message");

            Branch target = branches.get(branch);
            String previous = target.headSha() == null
                ? "root"
                : target.headSha();

            String sha = Integer.toHexString(
                Objects.hash(
                    previous,
                    author,
                    message,
                    System.nanoTime()
                )
            );

            Commit commit = new Commit(
                sha,
                author,
                message.trim(),
                Instant.now()
            );

            target.commits().add(commit);
            return commit;
        }

        PullRequest createPullRequest(
            String source,
            String target,
            String author,
            boolean draft
        ) {
            requireBranch(source);
            requireBranch(target);

            if (source.equals(target)) {
                throw new GovernanceException(
                    "Source and target branches must differ"
                );
            }

            if (!users.contains(author)) {
                throw new GovernanceException("Unknown PR author");
            }

            PullRequest request = new PullRequest(
                nextPr++,
                source,
                target,
                author,
                draft
                    ? PullRequestState.DRAFT
                    : PullRequestState.OPEN,
                branches.get(source).commits()
            );

            pullRequests.put(request.number(), request);
            return request;
        }

        void markReady(int number) {
            PullRequest pr = requirePr(number);
            if (pr.state() != PullRequestState.DRAFT) {
                throw new GovernanceException(
                    "Only draft PRs can become ready"
                );
            }
            setState(pr, PullRequestState.OPEN);
        }

        void synchronize(int number) {
            PullRequest pr = requirePr(number);
            pr.commits.clear();
            pr.commits.addAll(
                branches.get(pr.source()).commits()
            );
            pr.synchronizedWithSource = true;
        }

        void requestChanges(
            int number,
            String reviewer,
            String comment
        ) {
            submitReview(
                number,
                reviewer,
                ReviewState.CHANGES_REQUESTED,
                List.of(comment)
            );
        }

        void approve(int number, String reviewer) {
            submitReview(
                number,
                reviewer,
                ReviewState.APPROVED,
                List.of()
            );
        }

        private void submitReview(
            int number,
            String reviewer,
            ReviewState state,
            List<String> comments
        ) {
            PullRequest pr = requirePr(number);

            if (!users.contains(reviewer)) {
                throw new GovernanceException("Unknown reviewer");
            }
            if (!reviewPolicy.eligibleReviewer(pr, reviewer)) {
                throw new GovernanceException(
                    "Reviewer is not eligible"
                );
            }
            if (pr.state() != PullRequestState.OPEN) {
                throw new GovernanceException(
                    "Review requires an open PR"
                );
            }
            if (
                state == ReviewState.CHANGES_REQUESTED &&
                comments.isEmpty()
            ) {
                throw new GovernanceException(
                    "Requested changes require a comment"
                );
            }

            pr.reviews.add(
                new Review(
                    reviewer,
                    state,
                    pr.headSha(),
                    comments
                )
            );
        }

        void addCheck(
            int number,
            String name,
            CheckState state
        ) {
            PullRequest pr = requirePr(number);
            requireText(name, "Check name");

            pr.checks.add(
                new StatusCheck(
                    name,
                    state,
                    pr.headSha()
                )
            );
        }

        void addConversation(int number) {
            requirePr(number).unresolvedConversations++;
        }

        void resolveConversation(int number) {
            PullRequest pr = requirePr(number);
            if (pr.unresolvedConversations == 0) {
                throw new GovernanceException(
                    "No unresolved conversation"
                );
            }
            pr.unresolvedConversations--;
        }

        MergeEligibility evaluate(
            int number,
            MergeStrategy strategy
        ) {
            PullRequest pr = requirePr(number);
            List<String> reasons = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                reasons.add("PR is not open");
            }

            if (pr.headSha() == null) {
                reasons.add("PR has no commits");
            }

            if (!pr.synchronizedWithSource) {
                reasons.add("Source branch is stale");
            }

            ProtectionPolicy policy = policies.get(pr.target());

            if (policy == null) {
                return new MergeEligibility(reasons);
            }

            Map<String, Review> latestReviews = new HashMap<>();

            for (Review review : pr.reviews) {
                latestReviews.put(review.reviewer(), review);
            }

            long approvals = latestReviews.values()
                .stream()
                .filter(
                    review ->
                        review.state() == ReviewState.APPROVED &&
                        review.commitSha().equals(pr.headSha())
                )
                .count();

            boolean requestedChanges = latestReviews.values()
                .stream()
                .anyMatch(
                    review ->
                        reviewPolicy.blocksMerge(
                            review,
                            pr.headSha()
                        )
                );

            if (requestedChanges) {
                reasons.add("Current requested changes remain");
            }

            if (approvals < policy.requiredApprovals()) {
                reasons.add(
                    "Approvals " +
                    approvals +
                    "/" +
                    policy.requiredApprovals()
                );
            }

            for (String required : policy.requiredChecks()) {
                boolean passed = pr.checks
                    .stream()
                    .anyMatch(
                        check ->
                            check.name().equals(required) &&
                            check.state() == CheckState.PASSED &&
                            check.commitSha().equals(pr.headSha())
                    );

                if (!passed) {
                    reasons.add(
                        "Required check not passed: " + required
                    );
                }
            }

            if (
                policy.requireResolvedConversations() &&
                pr.unresolvedConversations > 0
            ) {
                reasons.add("Unresolved conversations remain");
            }

            if (!policy.allowedStrategies().contains(strategy)) {
                reasons.add(
                    "Merge strategy is not allowed: " + strategy
                );
            }

            return new MergeEligibility(reasons);
        }

        void merge(
            int number,
            MergeStrategy strategy
        ) {
            PullRequest pr = requirePr(number);
            MergeEligibility result = evaluate(number, strategy);

            if (!result.eligible()) {
                throw new GovernanceException(
                    String.join("; ", result.reasons())
                );
            }

            Branch target = branches.get(pr.target());
            Branch source = branches.get(pr.source());

            if (strategy == MergeStrategy.SQUASH) {
                target.commits().add(
                    new Commit(
                        "squash-" + pr.number(),
                        pr.author(),
                        "Squash PR #" + pr.number(),
                        Instant.now()
                    )
                );
            } else {
                target.commits().addAll(source.commits());
            }

            pr.mergeStrategy = strategy;
            setState(pr, PullRequestState.MERGED);
        }

        private void setState(
            PullRequest pr,
            PullRequestState state
        ) {
            pr.state = state;
        }

        private PullRequest requirePr(int number) {
            PullRequest pr = pullRequests.get(number);
            if (pr == null) {
                throw new GovernanceException(
                    "Unknown Pull Request #" + number
                );
            }
            return pr;
        }

        private void requireBranch(String name) {
            if (!branches.containsKey(name)) {
                throw new GovernanceException(
                    "Unknown branch: " + name
                );
            }
        }

        private static void requireText(
            String value,
            String field
        ) {
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException(
                    field + " cannot be empty"
                );
            }
        }
    }

    public static void main(String[] args) {
        RepositoryService repository = new RepositoryService();

        repository.addUser("alice");
        repository.addUser("bob");
        repository.addUser("carol");

        repository.createBranch("main");
        repository.createBranch("feature/release-validation");

        repository.protectBranch(
            "main",
            new ProtectionPolicy(
                2,
                Set.of("tests", "security"),
                true,
                false,
                false,
                false,
                true,
                EnumSet.of(
                    MergeStrategy.SQUASH,
                    MergeStrategy.REBASE
                )
            )
        );

        repository.commit(
            "main",
            "alice",
            "Initialize release service"
        );

        repository.commit(
            "feature/release-validation",
            "alice",
            "Validate release metadata"
        );

        PullRequest pr = repository.createPullRequest(
            "feature/release-validation",
            "main",
            "alice",
            true
        );

        repository.markReady(pr.number());
        repository.synchronize(pr.number());
        repository.addConversation(pr.number());

        repository.requestChanges(
            pr.number(),
            "carol",
            "Require validation of release version."
        );

        repository.addCheck(
            pr.number(),
            "tests",
            CheckState.PASSED
        );

        repository.addCheck(
            pr.number(),
            "security",
            CheckState.PASSED
        );

        MergeEligibility first =
            repository.evaluate(
                pr.number(),
                MergeStrategy.SQUASH
            );

        System.out.println("Initial eligibility: " + first.eligible());
        first.reasons().forEach(reason ->
            System.out.println(" - " + reason)
        );

        repository.resolveConversation(pr.number());
        repository.approve(pr.number(), "bob");
        repository.approve(pr.number(), "carol");

        MergeEligibility second =
            repository.evaluate(
                pr.number(),
                MergeStrategy.SQUASH
            );

        System.out.println(
            "\nFinal eligibility: " + second.eligible()
        );

        repository.merge(
            pr.number(),
            MergeStrategy.SQUASH
        );

        System.out.println(
            "Final state: " + pr.state()
        );

        /*
         * Enterprise design decisions:
         * 1. Domain records are immutable where historical data should not
         *    change after creation.
         * 2. Pull Request state transitions are controlled by a service.
         * 3. Review approvals are tied to a specific commit SHA.
         * 4. Branch protection is separate from review policy.
         * 5. Merge eligibility is evaluated before target-branch mutation.
         * 6. HashMap lookups provide near-constant average branch/PR access.
         */
    }
}
