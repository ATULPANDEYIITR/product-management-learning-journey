import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class RepositoryGovernanceApp {

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
        public Commit {
            if (sha == null || !sha.matches("[0-9a-f]{7,40}")) {
                throw new IllegalArgumentException("Invalid commit SHA.");
            }
            if (message == null || message.isBlank()) {
                throw new IllegalArgumentException("Commit message is required.");
            }
        }
    }

    record ReviewComment(
        String reviewer,
        String path,
        int line,
        String body,
        boolean resolved
    ) {
        public ReviewComment {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(path);
            Objects.requireNonNull(body);

            if (line < 1) {
                throw new IllegalArgumentException("Line number must be positive.");
            }
            if (body.isBlank()) {
                throw new IllegalArgumentException("Comment body is required.");
            }
        }
    }

    static final class Reviewer {
        private final String username;
        private final Set<String> teams;
        private boolean active;

        Reviewer(String username, Set<String> teams) {
            if (username == null || username.isBlank()) {
                throw new IllegalArgumentException("Reviewer username is required.");
            }

            this.username = username;
            this.teams = new HashSet<>(teams);
            this.active = true;
        }

        String username() {
            return username;
        }

        boolean active() {
            return active;
        }

        void deactivate() {
            active = false;
        }
    }

    static final class Review {
        private final String reviewer;
        private ReviewState state;
        private final String commitSha;
        private boolean dismissed;

        Review(String reviewer, ReviewState state, String commitSha) {
            this.reviewer = Objects.requireNonNull(reviewer);
            this.state = Objects.requireNonNull(state);
            this.commitSha = Objects.requireNonNull(commitSha);
        }

        String reviewer() {
            return reviewer;
        }

        ReviewState state() {
            return state;
        }

        String commitSha() {
            return commitSha;
        }

        boolean dismissed() {
            return dismissed;
        }

        void dismiss() {
            dismissed = true;
            state = ReviewState.DISMISSED;
        }
    }

    static final class Branch {
        private final String name;
        private final List<String> commits = new ArrayList<>();
        private boolean protectedBranch;

        Branch(String name, boolean protectedBranch) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Branch name is required.");
            }

            this.name = name;
            this.protectedBranch = protectedBranch;
        }

        String name() {
            return name;
        }

        List<String> commits() {
            return commits;
        }

        boolean protectedBranch() {
            return protectedBranch;
        }

        void protect() {
            protectedBranch = true;
        }
    }

    static final class PullRequest {
        private final int number;
        private final String sourceBranch;
        private final String targetBranch;
        private final String title;
        private final String author;
        private PullRequestState state;
        private final List<String> commits;
        private final List<Review> reviews = new ArrayList<>();
        private final List<ReviewComment> comments = new ArrayList<>();
        private final Map<String, Boolean> statusChecks = new HashMap<>();
        private MergeStrategy mergeStrategy = MergeStrategy.SQUASH;

        PullRequest(
            int number,
            String sourceBranch,
            String targetBranch,
            String title,
            String author,
            PullRequestState state,
            List<String> commits
        ) {
            this.number = number;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.title = title;
            this.author = author;
            this.state = state;
            this.commits = new ArrayList<>(commits);
        }

        int number() {
            return number;
        }

        String sourceBranch() {
            return sourceBranch;
        }

        String targetBranch() {
            return targetBranch;
        }

        PullRequestState state() {
            return state;
        }

        void addReview(Review review) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Review requires an open pull request.");
            }
            reviews.add(review);
        }

        void addComment(ReviewComment comment) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Comment requires an open pull request.");
            }
            comments.add(comment);
        }

        void setStatusCheck(String name, boolean passed) {
            statusChecks.put(name, passed);
        }

        void setMergeStrategy(MergeStrategy strategy) {
            mergeStrategy = Objects.requireNonNull(strategy);
        }

        MergeStrategy mergeStrategy() {
            return mergeStrategy;
        }

        List<String> commits() {
            return Collections.unmodifiableList(commits);
        }

        List<Review> reviews() {
            return Collections.unmodifiableList(reviews);
        }

        List<ReviewComment> comments() {
            return Collections.unmodifiableList(comments);
        }

        Map<String, Boolean> statusChecks() {
            return Collections.unmodifiableMap(statusChecks);
        }

        void markMerged() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException("Only open pull requests can be merged.");
            }
            state = PullRequestState.MERGED;
        }
    }

    record BranchProtectionPolicy(
        int requiredReviews,
        Set<String> requiredStatusChecks,
        boolean requireConversationResolution,
        boolean allowDirectPush,
        boolean allowForcePush,
        boolean allowBranchDeletion,
        boolean requireLinearHistory,
        Set<MergeStrategy> allowedMergeStrategies,
        Set<String> bypassUsers
    ) {
        BranchProtectionPolicy {
            if (requiredReviews < 0) {
                throw new IllegalArgumentException("Required reviews cannot be negative.");
            }

            requiredStatusChecks = Set.copyOf(requiredStatusChecks);
            allowedMergeStrategies = Set.copyOf(allowedMergeStrategies);
            bypassUsers = Set.copyOf(bypassUsers);
        }
    }

    record MergeDecision(boolean eligible, List<String> reasons) {
        MergeDecision {
            reasons = List.copyOf(reasons);
        }
    }

    static final class Repository {
        private final String name;
        private final Map<String, Branch> branches = new HashMap<>();
        private final Map<String, Commit> commits = new HashMap<>();
        private final Map<String, Reviewer> reviewers = new HashMap<>();
        private final Map<Integer, PullRequest> pullRequests = new HashMap<>();
        private final Map<String, BranchProtectionPolicy> policies = new HashMap<>();

        Repository(String name) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Repository name is required.");
            }
            this.name = name;
        }

        void addBranch(String name, boolean protectedBranch) {
            if (branches.containsKey(name)) {
                throw new IllegalArgumentException("Branch already exists.");
            }
            branches.put(name, new Branch(name, protectedBranch));
        }

        void addCommit(String sha, String message, String branchName) {
            Branch branch = requireBranch(branchName);

            if (commits.containsKey(sha)) {
                throw new IllegalArgumentException("Commit already exists.");
            }

            Commit commit = new Commit(sha, message);
            commits.put(sha, commit);
            branch.commits().add(sha);
        }

        void registerReviewer(Reviewer reviewer) {
            if (reviewers.containsKey(reviewer.username())) {
                throw new IllegalArgumentException("Reviewer already exists.");
            }
            reviewers.put(reviewer.username(), reviewer);
        }

        void setProtection(
            String branchName,
            BranchProtectionPolicy policy
        ) {
            Branch branch = requireBranch(branchName);
            branch.protect();
            policies.put(branchName, policy);
        }

        PullRequest createPullRequest(
            int number,
            String source,
            String target,
            String title,
            String author
        ) {
            if (pullRequests.containsKey(number)) {
                throw new IllegalArgumentException("Pull request already exists.");
            }

            Branch sourceBranch = requireBranch(source);
            requireBranch(target);

            if (source.equals(target)) {
                throw new IllegalArgumentException(
                    "Source and target branches must differ."
                );
            }

            if (title == null || title.isBlank()) {
                throw new IllegalArgumentException("Pull request title is required.");
            }

            PullRequest pr = new PullRequest(
                number,
                source,
                target,
                title,
                author,
                PullRequestState.OPEN,
                sourceBranch.commits()
            );

            pullRequests.put(number, pr);
            return pr;
        }

        MergeDecision evaluateMerge(int number) {
            PullRequest pr = requirePullRequest(number);
            Branch target = requireBranch(pr.targetBranch());

            List<String> reasons = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                reasons.add("Pull request is not open.");
            }

            if (pr.commits().isEmpty()) {
                reasons.add("Pull request has no commits.");
            }

            BranchProtectionPolicy policy = policies.get(target.name());

            if (policy == null) {
                return new MergeDecision(reasons.isEmpty(), reasons);
            }

            if (!policy.allowedMergeStrategies().contains(pr.mergeStrategy())) {
                reasons.add("Selected merge strategy is not allowed.");
            }

            if (policy.requireConversationResolution()) {
                boolean unresolved = pr.comments()
                    .stream()
                    .anyMatch(comment -> !comment.resolved());

                if (unresolved) {
                    reasons.add("Unresolved review conversations remain.");
                }
            }

            Set<String> approvals = new HashSet<>();
            Set<String> requestedChanges = new HashSet<>();

            for (Review review : pr.reviews()) {
                if (review.dismissed()) {
                    continue;
                }

                Reviewer reviewer = reviewers.get(review.reviewer());

                if (reviewer == null || !reviewer.active()) {
                    continue;
                }

                /*
                 * The review references a commit. A later commit changes the
                 * effective review state because the old review is stale.
                 */
                if (!pr.commits().contains(review.commitSha())) {
                    continue;
                }

                if (review.state() == ReviewState.APPROVED) {
                    approvals.add(review.reviewer());
                }

                if (review.state() == ReviewState.CHANGES_REQUESTED) {
                    requestedChanges.add(review.reviewer());
                }
            }

            if (!requestedChanges.isEmpty()) {
                reasons.add("A reviewer has requested changes.");
            }

            if (approvals.size() < policy.requiredReviews()) {
                reasons.add(
                    "Eligible approvals: " +
                    approvals.size() +
                    "/" +
                    policy.requiredReviews()
                );
            }

            for (String requiredCheck : policy.requiredStatusChecks()) {
                if (!Boolean.TRUE.equals(
                    pr.statusChecks().get(requiredCheck)
                )) {
                    reasons.add(
                        "Required status check failed or is missing: " +
                        requiredCheck
                    );
                }
            }

            return new MergeDecision(reasons.isEmpty(), reasons);
        }

        void merge(int number, String actor) {
            PullRequest pr = requirePullRequest(number);
            BranchProtectionPolicy policy = policies.get(pr.targetBranch());

            boolean bypass =
                policy != null &&
                policy.bypassUsers().contains(actor);

            MergeDecision decision =
                bypass
                    ? new MergeDecision(true, List.of())
                    : evaluateMerge(number);

            if (!decision.eligible()) {
                throw new IllegalStateException(
                    "Merge blocked: " +
                    String.join("; ", decision.reasons())
                );
            }

            Branch target = requireBranch(pr.targetBranch());

            if (pr.mergeStrategy() == MergeStrategy.SQUASH) {
                target.commits().add("squash-" + pr.number());
            } else {
                target.commits().addAll(pr.commits());
            }

            pr.markMerged();

            System.out.println(
                "PR #" + number +
                " merged into " + target.name() +
                " using " + pr.mergeStrategy()
            );
        }

        private Branch requireBranch(String name) {
            Branch branch = branches.get(name);

            if (branch == null) {
                throw new IllegalArgumentException(
                    "Unknown branch: " + name
                );
            }

            return branch;
        }

        private PullRequest requirePullRequest(int number) {
            PullRequest pr = pullRequests.get(number);

            if (pr == null) {
                throw new IllegalArgumentException(
                    "Unknown pull request: " + number
                );
            }

            return pr;
        }
    }

    public static void main(String[] args) {
        Repository repository = new Repository("inventory-platform");

        repository.addBranch("main", true);
        repository.addBranch("feature/relational-schema", false);

        repository.addCommit(
            "a1b2c3d",
            "Create warehouse table",
            "main"
        );

        repository.addCommit(
            "b2c3d4e",
            "Create inventory foreign key",
            "feature/relational-schema"
        );

        repository.registerReviewer(
            new Reviewer(
                "maya",
                Set.of("database-reviewers")
            )
        );

        repository.registerReviewer(
            new Reviewer(
                "rahul",
                Set.of("application-reviewers")
            )
        );

        BranchProtectionPolicy policy =
            new BranchProtectionPolicy(
                1,
                Set.of("sql-tests", "integration-tests"),
                true,
                false,
                false,
                false,
                true,
                EnumSet.of(MergeStrategy.SQUASH),
                Set.of()
            );

        repository.setProtection("main", policy);

        PullRequest pr = repository.createPullRequest(
            42,
            "feature/relational-schema",
            "main",
            "Add relational inventory schema",
            "atul"
        );

        pr.addComment(
            new ReviewComment(
                "maya",
                "schema.sql",
                32,
                "Foreign key relationship is correctly modeled.",
                true
            )
        );

        pr.addReview(
            new Review(
                "maya",
                ReviewState.APPROVED,
                "b2c3d4e"
            )
        );

        pr.setStatusCheck("sql-tests", true);
        pr.setStatusCheck("integration-tests", true);

        MergeDecision decision =
            repository.evaluateMerge(42);

        System.out.println(
            "Merge eligible: " + decision.eligible()
        );

        for (String reason : decision.reasons()) {
            System.out.println("Blocking reason: " + reason);
        }

        if (decision.eligible()) {
            repository.merge(42, "atul");
        }
    }
}
