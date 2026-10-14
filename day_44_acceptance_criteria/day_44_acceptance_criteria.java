import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;

public class AcceptanceCriteriaGovernance {

    enum Priority {
        MUST, SHOULD, COULD
    }

    enum CriterionStatus {
        DRAFT, READY, VERIFIED, FAILED
    }

    enum ReviewState {
        PENDING, APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED
    }

    enum CheckState {
        PENDING, PASSED, FAILED
    }

    enum MergeMethod {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record Scenario(
        String given,
        String when,
        String then,
        String expected,
        Set<String> tags
    ) {
        Scenario {
            Objects.requireNonNull(given);
            Objects.requireNonNull(when);
            Objects.requireNonNull(then);
            Objects.requireNonNull(expected);
            tags = Set.copyOf(tags);
        }

        List<String> validate() {
            List<String> errors = new ArrayList<>();
            if (given.isBlank() || when.isBlank() ||
                then.isBlank() || expected.isBlank()) {
                errors.add("Given, When, Then, and expected behavior are required.");
            }
            if (tags.isEmpty()) {
                errors.add("At least one scenario tag is required.");
            }
            return errors;
        }
    }

    record Review(
        String reviewer,
        boolean eligible,
        String commitSha,
        ReviewState state
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            Objects.requireNonNull(state);
        }
    }

    record StatusCheck(
        String name,
        String commitSha,
        CheckState state
    ) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Check name is required.");
            }
            Objects.requireNonNull(state);
        }
    }

    static final class AcceptanceCriterion {
        private static final Pattern ID_PATTERN =
            Pattern.compile("AC-[A-Z]{2,8}-\\d{3}");

        private final String id;
        private final String title;
        private final String description;
        private final Priority priority;
        private final String owner;
        private final List<Scenario> scenarios;
        private final List<String> evidence = new ArrayList<>();
        private CriterionStatus status = CriterionStatus.DRAFT;

        AcceptanceCriterion(
            String id,
            String title,
            String description,
            Priority priority,
            String owner,
            List<Scenario> scenarios
        ) {
            this.id = Objects.requireNonNull(id);
            this.title = Objects.requireNonNull(title);
            this.description = Objects.requireNonNull(description);
            this.priority = Objects.requireNonNull(priority);
            this.owner = Objects.requireNonNull(owner);
            this.scenarios = List.copyOf(scenarios);
        }

        List<String> validate() {
            List<String> errors = new ArrayList<>();

            if (!ID_PATTERN.matcher(id).matches()) {
                errors.add("Criterion ID must match AC-AREA-001.");
            }
            if (title.isBlank() || title.length() > 120) {
                errors.add("Title must be non-empty and no longer than 120 characters.");
            }
            if (description.strip().length() < 15) {
                errors.add("Description must specify the required behavior.");
            }
            if (owner.isBlank()) {
                errors.add("An accountable owner is required.");
            }
            if (scenarios.isEmpty()) {
                errors.add("At least one scenario is required.");
            }

            for (int i = 0; i < scenarios.size(); i++) {
                for (String error : scenarios.get(i).validate()) {
                    errors.add("Scenario " + (i + 1) + ": " + error);
                }
            }
            return errors;
        }

        void markReady() {
            List<String> errors = validate();
            if (!errors.isEmpty()) {
                throw new IllegalStateException(String.join("; ", errors));
            }
            if (status != CriterionStatus.DRAFT &&
                status != CriterionStatus.FAILED &&
                status != CriterionStatus.VERIFIED) {
                throw new IllegalStateException("Invalid readiness transition.");
            }
            status = CriterionStatus.READY;
        }

        void recordExecution(boolean passed, String evidenceText) {
            if (status != CriterionStatus.READY) {
                throw new IllegalStateException(
                    "Only a ready criterion can be executed."
                );
            }
            if (evidenceText == null || evidenceText.isBlank()) {
                throw new IllegalArgumentException("Execution evidence is required.");
            }
            evidence.add(evidenceText.strip());
            status = passed ? CriterionStatus.VERIFIED : CriterionStatus.FAILED;
        }

        CriterionStatus status() {
            return status;
        }

        List<String> evidence() {
            return List.copyOf(evidence);
        }
    }

    record BranchProtection(
        String branch,
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean requireLinearHistory,
        boolean allowForcePush,
        boolean allowDeletion,
        boolean dismissStaleApprovals
    ) {
        BranchProtection {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException("Approval count cannot be negative.");
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    record PullRequest(
        int number,
        String sourceBranch,
        String targetBranch,
        String headSha,
        boolean draft,
        boolean open,
        boolean mergeConflict,
        boolean conversationsResolved,
        List<String> commits,
        List<Review> reviews,
        List<StatusCheck> checks
    ) {
        PullRequest {
            if (number <= 0) {
                throw new IllegalArgumentException("Pull request number must be positive.");
            }
            Objects.requireNonNull(sourceBranch);
            Objects.requireNonNull(targetBranch);
            Objects.requireNonNull(headSha);
            commits = List.copyOf(commits);
            reviews = List.copyOf(reviews);
            checks = List.copyOf(checks);
        }
    }

    record Eligibility(boolean eligible, List<String> blockers) {
        Eligibility {
            blockers = List.copyOf(blockers);
        }
    }

    static final class MergeEligibilityService {

        Eligibility evaluate(PullRequest pr, BranchProtection policy) {
            List<String> blockers = new ArrayList<>();

            if (!pr.open()) blockers.add("Pull request is closed.");
            if (pr.draft()) blockers.add("Draft request cannot be merged.");
            if (pr.sourceBranch().isBlank() || pr.targetBranch().isBlank()) {
                blockers.add("Source and target branches are required.");
            }
            if (pr.sourceBranch().equals(pr.targetBranch())) {
                blockers.add("Source and target branches must differ.");
            }
            if (!pr.targetBranch().equals(policy.branch())) {
                blockers.add("Policy does not match the target branch.");
            }
            if (pr.headSha().length() < 7) {
                blockers.add("Current head SHA is invalid.");
            }
            if (pr.mergeConflict()) blockers.add("Merge conflicts remain.");
            if (policy.requireResolvedConversations() &&
                !pr.conversationsResolved()) {
                blockers.add("Review conversations remain unresolved.");
            }
            if (policy.requireLinearHistory() && pr.commits().size() > 1) {
                blockers.add("Submitted history violates the configured linear-history rule.");
            }

            Set<String> approvedReviewers = new HashSet<>();
            for (Review review : pr.reviews()) {
                boolean current = pr.headSha().equals(review.commitSha());
                if (review.eligible() &&
                    review.state() == ReviewState.APPROVED &&
                    (!policy.dismissStaleApprovals() || current)) {
                    approvedReviewers.add(review.reviewer());
                }
            }

            if (approvedReviewers.size() < policy.requiredApprovals()) {
                blockers.add("Insufficient eligible approvals.");
            }

            for (String required : policy.requiredChecks()) {
                boolean passed = pr.checks().stream().anyMatch(check ->
                    check.name().equals(required) &&
                    check.state() == CheckState.PASSED &&
                    pr.headSha().equals(check.commitSha())
                );
                if (!passed) {
                    blockers.add("Required check is missing, stale, pending, or failed: "
                        + required);
                }
            }

            return new Eligibility(blockers.isEmpty(), blockers);
        }
    }

    private static Scenario protectedBranchScenario() {
        return new Scenario(
            "A production branch requires an independent approval",
            "A pull request is submitted without an eligible approval",
            "The merge is blocked",
            "Passing checks do not replace the required review decision.",
            Set.of("approval", "negative")
        );
    }

    public static void main(String[] args) {
        AcceptanceCriterion criterion = new AcceptanceCriterion(
            "AC-GOV-001",
            "Enforce protected branch merge criteria",
            "Changes targeting production must satisfy review and CI policies.",
            Priority.MUST,
            "Repository Maintainer",
            List.of(
                protectedBranchScenario(),
                new Scenario(
                    "The latest revision has approval and passing required checks",
                    "The merge service evaluates the request",
                    "The request is eligible if all configured policies pass",
                    "Only current review and check evidence satisfies policy.",
                    Set.of("branch-protection", "positive")
                )
            )
        );

        List<String> definitionErrors = criterion.validate();
        if (!definitionErrors.isEmpty()) {
            throw new IllegalStateException(String.join("; ", definitionErrors));
        }

        criterion.markReady();
        criterion.recordExecution(
            true,
            "Automated acceptance test confirmed missing approval blocks merging."
        );

        BranchProtection policy = new BranchProtection(
            "main",
            2,
            Set.of("unit-tests", "security-scan"),
            true,
            false,
            false,
            false,
            true
        );

        PullRequest pr = new PullRequest(
            184,
            "feature/session-timeout",
            "main",
            "f19a82c",
            false,
            true,
            false,
            true,
            List.of("aa12bc3", "f19a82c"),
            List.of(
                new Review("alex", true, "f19a82c", ReviewState.APPROVED),
                new Review("sam", true, "aa12bc3", ReviewState.APPROVED)
            ),
            List.of(
                new StatusCheck("unit-tests", "f19a82c", CheckState.PASSED),
                new StatusCheck("security-scan", "f19a82c", CheckState.PENDING),
                new StatusCheck("security-scan", "aa12bc3", CheckState.PASSED)
            )
        );

        MergeEligibilityService service = new MergeEligibilityService();
        Eligibility first = service.evaluate(pr, policy);

        System.out.println("Criterion status: " + criterion.status());
        System.out.println("Initial merge eligibility: " + first.eligible());
        first.blockers().forEach(blocker -> System.out.println("Blocked: " + blocker));

        PullRequest updated = new PullRequest(
            pr.number(),
            pr.sourceBranch(),
            pr.targetBranch(),
            pr.headSha(),
            pr.draft(),
            pr.open(),
            pr.mergeConflict(),
            pr.conversationsResolved(),
            pr.commits(),
            List.of(
                new Review("alex", true, "f19a82c", ReviewState.APPROVED),
                new Review("sam", true, "f19a82c", ReviewState.APPROVED)
            ),
            List.of(
                new StatusCheck("unit-tests", "f19a82c", CheckState.PASSED),
                new StatusCheck("security-scan", "f19a82c", CheckState.PASSED)
            )
        );

        Eligibility second = service.evaluate(updated, policy);
        System.out.println("\nAfter required checks and reviews are current:");
        System.out.println("Merge eligibility: " + second.eligible());
        second.blockers().forEach(blocker -> System.out.println("Blocked: " + blocker));

        PullRequest draft = new PullRequest(
            updated.number(),
            updated.sourceBranch(),
            updated.targetBranch(),
            updated.headSha(),
            true,
            true,
            false,
            true,
            updated.commits(),
            updated.reviews(),
            updated.checks()
        );

        System.out.println(
            "\nDraft eligibility: " + service.evaluate(draft, policy).eligible()
        );
    }
}
