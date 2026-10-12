import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

/*
 * Enterprise PRD governance model.
 *
 * Compile and run:
 *   javac PrdGovernance.java
 *   java PrdGovernance
 *
 * The model separates product-document quality, requirement review, approval
 * authority, acceptance verification, and release policy.
 */
public class PrdGovernance {

    enum Priority {
        MUST, SHOULD, COULD, WONT
    }

    enum RequirementType {
        FUNCTIONAL, NON_FUNCTIONAL, BUSINESS, TECHNICAL, COMPLIANCE
    }

    enum State {
        DRAFT, IN_REVIEW, APPROVED, IMPLEMENTED, VERIFIED, REJECTED
    }

    enum Decision {
        APPROVE, REQUEST_CHANGES, REJECT
    }

    static final class AcceptanceCriterion {
        private final String id;
        private final String given;
        private final String when;
        private final String then;

        AcceptanceCriterion(String id, String given, String when, String then) {
            this.id = requireText(id, "criterion ID");
            this.given = requireText(given, "Given");
            this.when = requireText(when, "When");
            this.then = requireText(then, "Then");
        }

        String id() {
            return id;
        }

        @Override
        public String toString() {
            return id + ": Given " + given + "; when " + when + "; then " + then;
        }
    }

    static final class Requirement {
        private final String id;
        private final String title;
        private final String description;
        private final String rationale;
        private final String owner;
        private final RequirementType type;
        private final Priority priority;
        private final List<String> dependencies;
        private final List<AcceptanceCriterion> criteria;
        private State state = State.DRAFT;

        Requirement(
                String id,
                String title,
                String description,
                String rationale,
                String owner,
                RequirementType type,
                Priority priority,
                List<String> dependencies,
                List<AcceptanceCriterion> criteria) {
            this.id = requireText(id, "requirement ID");
            this.title = requireText(title, "requirement title");
            this.description = requireText(description, "requirement description");
            this.rationale = requireText(rationale, "requirement rationale");
            this.owner = requireText(owner, "requirement owner");
            this.type = Objects.requireNonNull(type);
            this.priority = Objects.requireNonNull(priority);
            this.dependencies = List.copyOf(dependencies);
            this.criteria = List.copyOf(criteria);

            if (this.criteria.isEmpty()) {
                throw new IllegalArgumentException(
                        id + " must have at least one acceptance criterion.");
            }
        }

        String id() {
            return id;
        }

        String owner() {
            return owner;
        }

        Priority priority() {
            return priority;
        }

        State state() {
            return state;
        }

        List<String> dependencies() {
            return dependencies;
        }

        List<AcceptanceCriterion> criteria() {
            return criteria;
        }

        void setState(State state) {
            this.state = state;
        }

        @Override
        public String toString() {
            return id + " | " + priority + " | " + state + " | " + title;
        }
    }

    static final class ReviewRecord {
        private final String reviewer;
        private final Decision decision;
        private final String rationale;
        private final LocalDate recordedOn;

        ReviewRecord(String reviewer, Decision decision, String rationale) {
            this.reviewer = requireText(reviewer, "reviewer");
            this.decision = Objects.requireNonNull(decision);
            this.rationale = requireText(rationale, "review rationale");
            this.recordedOn = LocalDate.now();
        }
    }

    static final class ApprovalPolicy {
        private final int requiredApprovals;
        private final Set<String> eligibleReviewers;

        ApprovalPolicy(int requiredApprovals, Set<String> eligibleReviewers) {
            if (requiredApprovals < 1) {
                throw new IllegalArgumentException(
                        "At least one approval is required.");
            }
            if (eligibleReviewers.size() < requiredApprovals) {
                throw new IllegalArgumentException(
                        "Eligible reviewer pool is smaller than approval quorum.");
            }
            this.requiredApprovals = requiredApprovals;
            this.eligibleReviewers = Set.copyOf(eligibleReviewers);
        }

        boolean eligible(String reviewer) {
            return eligibleReviewers.contains(reviewer);
        }

        int requiredApprovals() {
            return requiredApprovals;
        }
    }

    static final class Risk {
        private final String id;
        private final String description;
        private final int probability;
        private final int impact;
        private final String mitigation;
        private final String owner;

        Risk(
                String id,
                String description,
                int probability,
                int impact,
                String mitigation,
                String owner) {
            this.id = requireText(id, "risk ID");
            this.description = requireText(description, "risk description");
            this.mitigation = requireText(mitigation, "risk mitigation");
            this.owner = requireText(owner, "risk owner");

            if (probability < 1 || probability > 5 ||
                    impact < 1 || impact > 5) {
                throw new IllegalArgumentException(
                        "Risk probability and impact must be between 1 and 5.");
            }
            this.probability = probability;
            this.impact = impact;
        }

        int score() {
            return probability * impact;
        }

        String severity() {
            if (score() >= 20) return "Critical";
            if (score() >= 12) return "High";
            if (score() >= 6) return "Medium";
            return "Low";
        }

        @Override
        public String toString() {
            return id + " | score=" + score() + " | " + severity()
                    + " | owner=" + owner + " | " + description;
        }
    }

    static final class ProductDocument {
        private final String productName;
        private final String problemStatement;
        private final List<String> evidence;
        private final Map<String, String> measurableGoals;
        private final List<String> inScope;
        private final List<String> outOfScope;
        private final List<Requirement> requirements;
        private final List<Risk> risks;
        private final List<String> releaseCriteria;

        ProductDocument(
                String productName,
                String problemStatement,
                List<String> evidence,
                Map<String, String> measurableGoals,
                List<String> inScope,
                List<String> outOfScope,
                List<Requirement> requirements,
                List<Risk> risks,
                List<String> releaseCriteria) {
            this.productName = requireText(productName, "product name");
            this.problemStatement = requireText(problemStatement, "problem statement");
            this.evidence = List.copyOf(evidence);
            this.measurableGoals = Map.copyOf(measurableGoals);
            this.inScope = List.copyOf(inScope);
            this.outOfScope = List.copyOf(outOfScope);
            this.requirements = List.copyOf(requirements);
            this.risks = List.copyOf(risks);
            this.releaseCriteria = List.copyOf(releaseCriteria);
        }

        List<String> validate() {
            List<String> errors = new ArrayList<>();

            if (evidence.isEmpty()) errors.add("Problem evidence is required.");
            if (measurableGoals.isEmpty()) errors.add("Measurable goals are required.");
            if (inScope.isEmpty()) errors.add("In-scope items are required.");
            if (requirements.isEmpty()) errors.add("Requirements are required.");
            if (releaseCriteria.isEmpty()) errors.add("Release criteria are required.");

            Set<String> ids = new HashSet<>();
            for (Requirement requirement : requirements) {
                if (!ids.add(requirement.id())) {
                    errors.add("Duplicate requirement ID: " + requirement.id());
                }
            }

            for (Requirement requirement : requirements) {
                for (String dependency : requirement.dependencies()) {
                    if (!ids.contains(dependency)) {
                        errors.add(requirement.id() +
                                " references unknown dependency " + dependency);
                    }
                    if (requirement.id().equals(dependency)) {
                        errors.add(requirement.id() +
                                " cannot depend on itself.");
                    }
                }
            }

            if (containsDependencyCycle()) {
                errors.add("Requirement dependencies contain a cycle.");
            }
            return errors;
        }

        private boolean containsDependencyCycle() {
            Map<String, Requirement> byId = new HashMap<>();
            for (Requirement requirement : requirements) {
                byId.put(requirement.id(), requirement);
            }

            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();

            for (Requirement requirement : requirements) {
                if (cycleFrom(requirement.id(), byId, visiting, visited)) {
                    return true;
                }
            }
            return false;
        }

        private boolean cycleFrom(
                String id,
                Map<String, Requirement> byId,
                Set<String> visiting,
                Set<String> visited) {
            if (visiting.contains(id)) return true;
            if (visited.contains(id)) return false;

            visiting.add(id);
            Requirement requirement = byId.get(id);
            if (requirement != null) {
                for (String dependency : requirement.dependencies()) {
                    if (byId.containsKey(dependency) &&
                            cycleFrom(dependency, byId, visiting, visited)) {
                        return true;
                    }
                }
            }
            visiting.remove(id);
            visited.add(id);
            return false;
        }

        String productName() {
            return productName;
        }

        String problemStatement() {
            return problemStatement;
        }

        List<Requirement> requirements() {
            return requirements;
        }

        List<Risk> risks() {
            return risks;
        }
    }

    static final class ReviewService {
        private final ProductDocument document;
        private final ApprovalPolicy policy;
        private final Map<String, Map<String, ReviewRecord>> reviews =
                new LinkedHashMap<>();
        private final List<String> audit = new ArrayList<>();

        ReviewService(ProductDocument document, ApprovalPolicy policy) {
            this.document = Objects.requireNonNull(document);
            this.policy = Objects.requireNonNull(policy);
        }

        void requestReview(String requirementId, String actor) {
            Requirement requirement = getRequirement(requirementId);
            requireText(actor, "actor");
            requireDependenciesApproved(requirement);
            transition(requirement, State.IN_REVIEW, actor);
        }

        void recordReview(
                String requirementId,
                String reviewer,
                Decision decision,
                String rationale) {
            Requirement requirement = getRequirement(requirementId);
            requireText(reviewer, "reviewer");

            if (!policy.eligible(reviewer)) {
                throw new SecurityException(
                        reviewer + " is not eligible to review requirements.");
            }
            if (reviewer.equals(requirement.owner())) {
                throw new SecurityException(
                        "Requirement owners cannot approve their own requirements.");
            }
            if (requirement.state() != State.IN_REVIEW) {
                throw new IllegalStateException(
                        "Requirement must be in review before a decision is recorded.");
            }

            ReviewRecord record = new ReviewRecord(reviewer, decision, rationale);
            reviews.computeIfAbsent(requirementId, ignored -> new LinkedHashMap<>())
                    .put(reviewer, record);

            audit.add("Review " + decision + " recorded for " + requirementId
                    + " by " + reviewer);

            if (decision == Decision.REJECT) {
                transition(requirement, State.REJECTED, reviewer);
                return;
            }
            if (decision == Decision.REQUEST_CHANGES) {
                transition(requirement, State.DRAFT, reviewer);
                return;
            }

            long approvals = reviews.get(requirementId).values().stream()
                    .filter(review -> review.decision == Decision.APPROVE)
                    .map(review -> review.reviewer)
                    .distinct()
                    .count();

            if (approvals >= policy.requiredApprovals()) {
                transition(requirement, State.APPROVED, reviewer);
            }
        }

        void markImplemented(String requirementId, String actor) {
            transition(getRequirement(requirementId), State.IMPLEMENTED, actor);
        }

        void verifyAcceptance(
                String requirementId,
                Map<String, Boolean> results,
                String tester) {
            Requirement requirement = getRequirement(requirementId);
            if (requirement.state() != State.IMPLEMENTED) {
                throw new IllegalStateException(
                        "Acceptance testing requires an implemented requirement.");
            }

            Set<String> expected = new HashSet<>();
            for (AcceptanceCriterion criterion : requirement.criteria()) {
                expected.add(criterion.id());
            }
            if (!results.keySet().equals(expected)) {
                throw new IllegalArgumentException(
                        "Test result IDs must exactly match acceptance criterion IDs.");
            }

            List<String> failed = results.entrySet().stream()
                    .filter(entry -> !Boolean.TRUE.equals(entry.getValue()))
                    .map(Map.Entry::getKey)
                    .toList();

            audit.add("Acceptance tests executed for " + requirementId
                    + " by " + tester + "; failures=" + failed.size());

            if (!failed.isEmpty()) {
                throw new IllegalStateException(
                        "Acceptance tests failed: " + String.join(", ", failed));
            }
            transition(requirement, State.VERIFIED, tester);
        }

        private Requirement getRequirement(String id) {
            return document.requirements().stream()
                    .filter(requirement -> requirement.id().equals(id))
                    .findFirst()
                    .orElseThrow(() ->
                            new IllegalArgumentException("Unknown requirement: " + id));
        }

        private void requireDependenciesApproved(Requirement requirement) {
            for (String dependencyId : requirement.dependencies()) {
                Requirement dependency = getRequirement(dependencyId);
                State state = dependency.state();
                if (state != State.APPROVED &&
                        state != State.IMPLEMENTED &&
                        state != State.VERIFIED) {
                    throw new IllegalStateException(
                            "Dependency " + dependencyId + " is not approved.");
                }
            }
        }

        private void transition(Requirement requirement, State next, String actor) {
            requireText(actor, "actor");
            State current = requirement.state();

            Map<State, Set<State>> transitions = new EnumMap<>(State.class);
            transitions.put(State.DRAFT, Set.of(State.IN_REVIEW));
            transitions.put(State.IN_REVIEW,
                    Set.of(State.DRAFT, State.APPROVED, State.REJECTED));
            transitions.put(State.APPROVED,
                    Set.of(State.IN_REVIEW, State.IMPLEMENTED));
            transitions.put(State.IMPLEMENTED,
                    Set.of(State.IN_REVIEW, State.VERIFIED));
            transitions.put(State.VERIFIED, Set.of(State.IN_REVIEW));
            transitions.put(State.REJECTED, Set.of(State.DRAFT));

            if (!transitions.get(current).contains(next)) {
                throw new IllegalStateException(
                        "Invalid transition: " + current + " -> " + next);
            }

            requirement.setState(next);
            audit.add(UUID.randomUUID() + " | " + actor + " | "
                    + requirement.id() + " | " + current + " -> " + next);
        }

        boolean releaseReady() {
            if (!document.validate().isEmpty()) return false;
            return document.requirements().stream()
                    .filter(requirement -> requirement.priority() == Priority.MUST)
                    .allMatch(requirement -> requirement.state() == State.VERIFIED);
        }

        void printReport() {
            System.out.println("\nRequirement state");
            document.requirements().forEach(System.out::println);

            System.out.println("\nRisk register");
            document.risks().stream()
                    .sorted((left, right) ->
                            Integer.compare(right.score(), left.score()))
                    .forEach(System.out::println);

            System.out.println("\nAudit events");
            audit.forEach(System.out::println);

            System.out.println("\nRelease ready: " + releaseReady());
        }
    }

    private static String requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " cannot be blank.");
        }
        return value;
    }

    public static void main(String[] args) {
        try {
            Requirement requestValidation = new Requirement(
                    "REQ-301",
                    "Validate procurement requests",
                    "Reject submissions with missing mandatory fields.",
                    "Incomplete requests cause manual rework.",
                    "Product Manager",
                    RequirementType.FUNCTIONAL,
                    Priority.MUST,
                    List.of(),
                    List.of(
                            new AcceptanceCriterion(
                                    "AC-301-A",
                                    "Mandatory fields are present",
                                    "The requester submits the request",
                                    "The service assigns a unique request ID"),
                            new AcceptanceCriterion(
                                    "AC-301-B",
                                    "The cost center is absent",
                                    "The requester submits the request",
                                    "The service rejects the request with a field-specific error")
                    )
            );

            Requirement approvalRouting = new Requirement(
                    "REQ-302",
                    "Route requests using approval policy",
                    "Select an authorized approver group by amount and cost center.",
                    "Financial authority must be enforced consistently.",
                    "Procurement Lead",
                    RequirementType.FUNCTIONAL,
                    Priority.MUST,
                    List.of("REQ-301"),
                    List.of(
                            new AcceptanceCriterion(
                                    "AC-302-A",
                                    "An active policy matches the request",
                                    "The routing service evaluates the request",
                                    "The request is assigned to the required approver group")
                    )
            );

            ProductDocument document = new ProductDocument(
                    "Procurement Request Portal",
                    "Email-based procurement requests are incomplete, difficult to track, and hard to audit.",
                    List.of(
                            "Discovery interviews report repeated missing-field requests.",
                            "Approval routing depends on manually maintained spreadsheets."
                    ),
                    Map.of(
                            "Completeness", "At least 95% of submissions pass initial validation.",
                            "Routing accuracy", "At least 99% of requests follow the correct approval path."
                    ),
                    List.of("Request submission", "Policy-based approval routing", "Status visibility"),
                    List.of("Supplier payments", "Contract negotiation"),
                    List.of(requestValidation, approvalRouting),
                    List.of(
                            new Risk(
                                    "RISK-301",
                                    "Approval policy may be outdated",
                                    4,
                                    5,
                                    "Validate policy ownership and effective dates",
                                    "Procurement Operations"),
                            new Risk(
                                    "RISK-302",
                                    "Confidential documents may be exposed",
                                    3,
                                    5,
                                    "Enforce access control and encryption",
                                    "Security Lead")
                    ),
                    List.of(
                            "All Must requirements pass acceptance tests.",
                            "No unresolved critical security defect remains."
                    )
            );

            List<String> errors = document.validate();
            if (!errors.isEmpty()) {
                throw new IllegalStateException(String.join("; ", errors));
            }

            ApprovalPolicy policy = new ApprovalPolicy(
                    2,
                    Set.of("Procurement Lead", "Finance Lead", "Security Lead", "QA Lead")
            );
            ReviewService service = new ReviewService(document, policy);

            service.requestReview("REQ-301", "Product Manager");
            service.recordReview(
                    "REQ-301",
                    "Procurement Lead",
                    Decision.APPROVE,
                    "Validation behavior is measurable.");
            service.recordReview(
                    "REQ-301",
                    "Security Lead",
                    Decision.APPROVE,
                    "Server-side validation is required.");
            service.markImplemented("REQ-301", "Engineering Lead");
            service.verifyAcceptance(
                    "REQ-301",
                    Map.of("AC-301-A", true, "AC-301-B", true),
                    "QA Lead");

            service.requestReview("REQ-302", "Procurement Lead");
            service.recordReview(
                    "REQ-302",
                    "Finance Lead",
                    Decision.APPROVE,
                    "Approval routing reflects delegated authority.");
            service.recordReview(
                    "REQ-302",
                    "Security Lead",
                    Decision.APPROVE,
                    "Unmatched policies must not auto-approve requests.");
            service.markImplemented("REQ-302", "Engineering Lead");

            // An incomplete or failing test suite cannot produce Verified state.
            try {
                service.verifyAcceptance(
                        "REQ-302",
                        Map.of("AC-302-A", false),
                        "QA Lead");
            } catch (IllegalStateException exception) {
                System.out.println("Expected verification failure: "
                        + exception.getMessage());
            }

            System.out.println("PRD: " + document.productName());
            System.out.println("Problem: " + document.problemStatement());
            service.printReport();
        } catch (RuntimeException exception) {
            System.err.println("PRD governance error: " + exception.getMessage());
            System.exitCode = 1;
        }
    }
}
