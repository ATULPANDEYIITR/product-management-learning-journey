import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class Main {

    enum DebtCategory {
        CODE, TEST, ARCHITECTURE, SECURITY, INFRASTRUCTURE, DOCUMENTATION
    }

    enum DebtStatus {
        OPEN, PLANNED, IN_PROGRESS, RESOLVED, ACCEPTED
    }

    enum ReviewState {
        PENDING, APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED
    }

    enum Priority {
        LOW, MEDIUM, HIGH, CRITICAL
    }

    static final class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    record Commit(
        String sha,
        String message,
        String author,
        int changedFiles,
        int additions,
        int deletions
    ) {
        Commit {
            if (sha == null || sha.length() < 7) {
                throw new ValidationException("Commit SHA is invalid.");
            }
            if (message == null || message.isBlank()) {
                throw new ValidationException("Commit message is required.");
            }
        }
    }

    static final class TechnicalDebtItem {
        private final int id;
        private final String title;
        private final DebtCategory category;
        private final String owner;
        private final double principalHours;
        private final double remediationHours;
        private final double monthlyInterestHours;
        private final int impact;
        private final double probability;
        private final int urgency;
        private final int securityExposure;
        private final Set<String> affectedComponents;
        private DebtStatus status;

        TechnicalDebtItem(
            int id,
            String title,
            DebtCategory category,
            String owner,
            double principalHours,
            double remediationHours,
            double monthlyInterestHours,
            int impact,
            double probability,
            int urgency,
            int securityExposure,
            Set<String> affectedComponents
        ) {
            this.id = id;
            this.title = Objects.requireNonNull(title);
            this.category = Objects.requireNonNull(category);
            this.owner = Objects.requireNonNull(owner);
            this.principalHours = principalHours;
            this.remediationHours = remediationHours;
            this.monthlyInterestHours = monthlyInterestHours;
            this.impact = impact;
            this.probability = probability;
            this.urgency = urgency;
            this.securityExposure = securityExposure;
            this.affectedComponents =
                Set.copyOf(affectedComponents == null
                    ? Set.of()
                    : affectedComponents);
            this.status = DebtStatus.OPEN;
            validate();
        }

        private void validate() {
            if (id <= 0) throw new ValidationException("Invalid debt ID.");
            if (title.isBlank() || owner.isBlank()) {
                throw new ValidationException("Title and owner are required.");
            }
            if (principalHours <= 0 || remediationHours <= 0) {
                throw new ValidationException("Effort estimates must be positive.");
            }
            if (monthlyInterestHours < 0) {
                throw new ValidationException("Interest cannot be negative.");
            }
            if (impact < 1 || impact > 10) {
                throw new ValidationException("Impact must be 1..10.");
            }
            if (probability < 0 || probability > 1) {
                throw new ValidationException("Probability must be 0..1.");
            }
            if (urgency < 1 || urgency > 10) {
                throw new ValidationException("Urgency must be 1..10.");
            }
            if (securityExposure < 0 || securityExposure > 10) {
                throw new ValidationException(
                    "Security exposure must be 0..10.");
            }
        }

        double riskScore() {
            return impact * probability * 10
                + urgency * 2
                + securityExposure * 3;
        }

        double priorityScore() {
            return (
                monthlyInterestHours * 4
                + riskScore() * 2
                + securityExposure * 5
            ) / Math.max(remediationHours, 1.0);
        }

        Priority priority() {
            double score = priorityScore();
            if (score >= 70) return Priority.CRITICAL;
            if (score >= 40) return Priority.HIGH;
            if (score >= 20) return Priority.MEDIUM;
            return Priority.LOW;
        }

        double remediationHours() {
            return remediationHours;
        }

        int id() {
            return id;
        }

        String title() {
            return title;
        }

        DebtStatus status() {
            return status;
        }
    }

    record Review(
        String reviewer,
        ReviewState state,
        List<String> comments,
        Instant submittedAt
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new ValidationException("Reviewer is required.");
            }
            Objects.requireNonNull(state);
            comments = List.copyOf(comments == null ? List.of() : comments);
            submittedAt = submittedAt == null ? Instant.now() : submittedAt;
        }
    }

    record StatusCheck(String name, boolean passed, boolean required) {}

    record BranchProtectionPolicy(
        String branch,
        int requiredReviews,
        Set<String> requiredStatusChecks,
        boolean requireConversationResolution,
        boolean restrictDirectPush,
        boolean restrictForcePush,
        boolean restrictDeletion,
        boolean requireLinearHistory,
        boolean allowAdminBypass,
        double maximumDebtScore
    ) {
        BranchProtectionPolicy {
            if (branch == null || branch.isBlank()) {
                throw new ValidationException("Protected branch is required.");
            }
            if (requiredReviews < 0) {
                throw new ValidationException("Review requirement cannot be negative.");
            }
            requiredStatusChecks =
                Set.copyOf(requiredStatusChecks == null
                    ? Set.of()
                    : requiredStatusChecks);
            if (maximumDebtScore < 0) {
                throw new ValidationException("Debt threshold cannot be negative.");
            }
        }
    }

    static final class PullRequest {
        private final int number;
        private final String title;
        private final String author;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<Commit> commits;
        private final List<Review> reviews = new ArrayList<>();
        private final List<StatusCheck> statusChecks = new ArrayList<>();
        private final Set<Integer> technicalDebtIds;
        private boolean draft;
        private boolean open = true;
        private boolean synchronizedWithBase = true;
        private boolean conflicts;
        private int unresolvedConversations;

        PullRequest(
            int number,
            String title,
            String author,
            String sourceBranch,
            String targetBranch,
            List<Commit> commits,
            Set<Integer> technicalDebtIds,
            boolean draft
        ) {
            this.number = number;
            this.title = title;
            this.author = author;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.commits = List.copyOf(commits);
            this.technicalDebtIds = Set.copyOf(technicalDebtIds);
            this.draft = draft;
        }

        void addReview(Review review) {
            if (!open) {
                throw new ValidationException(
                    "Closed Pull Requests cannot receive reviews.");
            }
            reviews.add(review);
        }

        void addStatusCheck(StatusCheck check) {
            statusChecks.add(check);
        }

        int approvalCount() {
            return (int) reviews.stream()
                .filter(review -> review.state() == ReviewState.APPROVED)
                .count();
        }

        boolean hasChangeRequest() {
            return reviews.stream()
                .anyMatch(review ->
                    review.state() == ReviewState.CHANGES_REQUESTED);
        }

        boolean requiredChecksPass() {
            return statusChecks.stream()
                .filter(StatusCheck::required)
                .allMatch(StatusCheck::passed);
        }

        Set<Integer> technicalDebtIds() {
            return technicalDebtIds;
        }

        String targetBranch() {
            return targetBranch;
        }

        boolean isDraft() {
            return draft;
        }

        boolean isOpen() {
            return open;
        }

        boolean isSynchronizedWithBase() {
            return synchronizedWithBase;
        }

        boolean hasConflicts() {
            return conflicts;
        }

        int unresolvedConversations() {
            return unresolvedConversations;
        }

        void setUnresolvedConversations(int value) {
            if (value < 0) {
                throw new ValidationException(
                    "Conversation count cannot be negative.");
            }
            unresolvedConversations = value;
        }
    }

    record MergeDecision(boolean eligible, List<String> reasons) {}

    static final class MergeEligibilityService {
        private final Map<Integer, TechnicalDebtItem> debt;
        private final Map<String, BranchProtectionPolicy> policies;

        MergeEligibilityService(
            Map<Integer, TechnicalDebtItem> debt,
            Map<String, BranchProtectionPolicy> policies
        ) {
            this.debt = debt;
            this.policies = policies;
        }

        MergeDecision evaluate(
            PullRequest pr,
            String actor,
            boolean administrator
        ) {
            List<String> reasons = new ArrayList<>();

            if (!pr.isOpen()) reasons.add("Pull Request is closed.");
            if (pr.isDraft()) reasons.add("Draft Pull Request cannot be merged.");
            if (pr.hasConflicts()) reasons.add("Merge conflicts are unresolved.");
            if (!pr.isSynchronizedWithBase()) {
                reasons.add("Pull Request is stale relative to its base branch.");
            }

            BranchProtectionPolicy policy =
                policies.get(pr.targetBranch());

            if (policy == null) {
                return new MergeDecision(reasons.isEmpty(), List.copyOf(reasons));
            }

            if (pr.approvalCount() < policy.requiredReviews()) {
                reasons.add(
                    "Required approvals: "
                    + pr.approvalCount()
                    + "/"
                    + policy.requiredReviews()
                    + "."
                );
            }

            if (pr.hasChangeRequest()) {
                reasons.add("A reviewer has requested changes.");
            }

            if (!pr.requiredChecksPass()) {
                reasons.add("At least one required status check failed.");
            }

            if (policy.requireConversationResolution()
                && pr.unresolvedConversations() > 0) {
                reasons.add("Review conversations remain unresolved.");
            }

            Set<String> presentChecks = new HashSet<>();
            // A failed check remains present but is not treated as satisfying
            // the policy.
            for (StatusCheck check : getChecks(pr)) {
                if (check.passed()) {
                    presentChecks.add(check.name());
                }
            }

            for (String required : policy.requiredStatusChecks()) {
                if (!presentChecks.contains(required)) {
                    reasons.add("Required check missing or failed: " + required);
                }
            }

            double debtScore = pr.technicalDebtIds().stream()
                .map(debt::get)
                .filter(Objects::nonNull)
                .mapToDouble(TechnicalDebtItem::priorityScore)
                .sum();

            if (debtScore > policy.maximumDebtScore()) {
                reasons.add(
                    String.format(
                        "Technical debt score %.2f exceeds %.2f.",
                        debtScore,
                        policy.maximumDebtScore()
                    )
                );
            }

            if (actor.equalsIgnoreCase(getAuthor(pr))
                && policy.requiredReviews() > 0) {
                reasons.add("Author cannot provide all required independent approvals.");
            }

            // Administrator bypass is deliberately not applied automatically.
            // Governance policy must explicitly permit it, and security/status
            // controls remain independently evaluated.
            if (administrator && policy.allowAdminBypass()) {
                reasons.removeIf(reason ->
                    reason.startsWith("Required approvals:"));
            }

            return new MergeDecision(reasons.isEmpty(), List.copyOf(reasons));
        }

        private static List<StatusCheck> getChecks(PullRequest pr) {
            try {
                var field = PullRequest.class.getDeclaredField("statusChecks");
                field.setAccessible(true);
                @SuppressWarnings("unchecked")
                List<StatusCheck> checks =
                    (List<StatusCheck>) field.get(pr);
                return List.copyOf(checks);
            } catch (ReflectiveOperationException ex) {
                throw new IllegalStateException("Cannot inspect status checks.", ex);
            }
        }

        private static String getAuthor(PullRequest pr) {
            try {
                var field = PullRequest.class.getDeclaredField("author");
                field.setAccessible(true);
                return (String) field.get(pr);
            } catch (ReflectiveOperationException ex) {
                throw new IllegalStateException("Cannot inspect author.", ex);
            }
        }
    }

    static final class RepositoryService {
        private final String repositoryName;
        private final Set<String> branches = new HashSet<>();
        private final Map<Integer, TechnicalDebtItem> debt = new LinkedHashMap<>();
        private final Map<Integer, PullRequest> pullRequests = new HashMap<>();
        private final Map<String, BranchProtectionPolicy> policies =
            new HashMap<>();
        private int nextDebtId = 1;
        private int nextPrNumber = 1;

        RepositoryService(String repositoryName) {
            this.repositoryName = Objects.requireNonNull(repositoryName);
        }

        void addBranch(String branch) {
            if (branch == null || branch.isBlank() || !branches.add(branch)) {
                throw new ValidationException("Invalid or duplicate branch.");
            }
        }

        void addDebt(TechnicalDebtItem item) {
            if (item.id() != nextDebtId) {
                throw new ValidationException("Debt IDs must be sequential.");
            }
            debt.put(item.id(), item);
            nextDebtId++;
        }

        void protect(BranchProtectionPolicy policy) {
            if (!branches.contains(policy.branch())) {
                throw new ValidationException(
                    "Cannot protect an unknown branch.");
            }
            policies.put(policy.branch(), policy);
        }

        PullRequest createPullRequest(
            String title,
            String author,
            String source,
            String target,
            List<Commit> commits,
            Set<Integer> debtIds
        ) {
            if (!branches.contains(source) || !branches.contains(target)) {
                throw new ValidationException(
                    "Pull Request references an unknown branch.");
            }
            if (source.equals(target)) {
                throw new ValidationException(
                    "Source and target branches must differ.");
            }
            if (!debt.keySet().containsAll(debtIds)) {
                throw new ValidationException(
                    "Pull Request references unknown technical debt.");
            }

            PullRequest pr = new PullRequest(
                nextPrNumber++,
                title,
                author,
                source,
                target,
                commits,
                debtIds,
                false
            );
            pullRequests.put(pr.number, pr);
            return pr;
        }

        List<TechnicalDebtItem> prioritizedDebt() {
            return debt.values().stream()
                .filter(item ->
                    item.status() != DebtStatus.RESOLVED
                    && item.status() != DebtStatus.ACCEPTED)
                .sorted(
                    Comparator.comparingDouble(
                        TechnicalDebtItem::priorityScore).reversed())
                .toList();
        }

        List<Integer> allocateDebt(double capacity, double debtRatio) {
            if (capacity <= 0) {
                throw new ValidationException("Capacity must be positive.");
            }
            if (debtRatio < 0 || debtRatio > 1) {
                throw new ValidationException("Debt ratio must be 0..1.");
            }

            double remaining = capacity * debtRatio;
            List<Integer> selected = new ArrayList<>();

            for (TechnicalDebtItem item : prioritizedDebt()) {
                if (item.remediationHours() <= remaining) {
                    selected.add(item.id());
                    remaining -= item.remediationHours();
                }
            }
            return selected;
        }

        MergeEligibilityService mergeEligibilityService() {
            return new MergeEligibilityService(debt, policies);
        }
    }

    public static void main(String[] args) {
        try {
            RepositoryService repository =
                new RepositoryService("billing-platform");

            repository.addBranch("main");
            repository.addBranch("develop");
            repository.addBranch("feature/billing-refactor");

            repository.addDebt(new TechnicalDebtItem(
                1,
                "Duplicated billing validation",
                DebtCategory.CODE,
                "billing-team",
                12,
                20,
                8,
                8,
                0.8,
                8,
                4,
                Set.of("billing", "checkout")
            ));

            repository.addDebt(new TechnicalDebtItem(
                2,
                "Incomplete payment failure tests",
                DebtCategory.TEST,
                "quality-team",
                8,
                16,
                6,
                7,
                0.7,
                7,
                3,
                Set.of("payments")
            ));

            repository.addDebt(new TechnicalDebtItem(
                3,
                "Static test credential",
                DebtCategory.SECURITY,
                "security-team",
                3,
                6,
                2,
                10,
                0.5,
                10,
                10,
                Set.of("integration-tests")
            ));

            repository.protect(new BranchProtectionPolicy(
                "main",
                2,
                Set.of("unit-tests", "security-scan", "integration-tests"),
                true,
                true,
                true,
                true,
                true,
                false,
                85
            ));

            PullRequest pr = repository.createPullRequest(
                "Refactor billing validation",
                "nina",
                "feature/billing-refactor",
                "main",
                List.of(
                    new Commit(
                        "abc12345",
                        "refactor billing validation",
                        "nina",
                        8,
                        180,
                        120
                    ),
                    new Commit(
                        "def67890",
                        "add billing failure tests",
                        "nina",
                        5,
                        140,
                        15
                    )
                ),
                Set.of(1, 2)
            );

            pr.addStatusCheck(new StatusCheck("unit-tests", true, true));
            pr.addStatusCheck(new StatusCheck("security-scan", true, true));
            pr.addStatusCheck(
                new StatusCheck("integration-tests", false, true));

            pr.addReview(new Review(
                "omar",
                ReviewState.APPROVED,
                List.of("Validation boundaries are clearer."),
                Instant.now()
            ));

            pr.addReview(new Review(
                "priya",
                ReviewState.CHANGES_REQUESTED,
                List.of("Cover duplicate billing requests."),
                Instant.now()
            ));

            pr.setUnresolvedConversations(1);

            System.out.println("Technical debt ranking");
            for (TechnicalDebtItem item : repository.prioritizedDebt()) {
                System.out.printf(
                    "#%d %-8s score=%6.2f risk=%6.2f %s%n",
                    item.id(),
                    item.priority(),
                    item.priorityScore(),
                    item.riskScore(),
                    item.title()
                );
            }

            MergeDecision decision =
                repository.mergeEligibilityService()
                    .evaluate(pr, "nina", false);

            System.out.println(
                "\nMerge eligibility: "
                + (decision.eligible() ? "ELIGIBLE" : "BLOCKED")
            );

            decision.reasons().forEach(reason -> System.out.println("- " + reason));

            List<Integer> selected =
                repository.allocateDebt(80, 0.30);

            System.out.println("\nDebt items selected within capacity:");
            selected.forEach(id -> System.out.println("- #" + id));

            if (decision.eligible()) {
                throw new IllegalStateException(
                    "Sample Pull Request should be blocked.");
            }

            if (selected.isEmpty()) {
                throw new IllegalStateException(
                    "Capacity allocation selected no debt item.");
            }

            System.out.println("\nValidation checks passed.");
        } catch (ValidationException | IllegalStateException ex) {
            System.err.println("Execution failed: " + ex.getMessage());
            System.exit(1);
        }
    }
}
