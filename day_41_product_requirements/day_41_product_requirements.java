import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Enterprise product requirements management and approval workflow.
 * Requires Java 17 or later. Run with: java ProductRequirementsApp.java
 */
public class ProductRequirementsApp {

    enum RequirementType {
        FUNCTIONAL, NON_FUNCTIONAL, BUSINESS, CONSTRAINT
    }

    enum Priority {
        MUST, SHOULD, COULD, WONT
    }

    enum RequirementState {
        DRAFT, IN_REVIEW, APPROVED, IMPLEMENTED, VERIFIED, REJECTED
    }

    enum ReviewOutcome {
        COMMENT, REQUEST_CHANGES, APPROVE
    }

    enum ChangeState {
        PENDING, APPROVED, DEFERRED
    }

    record AcceptanceCriterion(String given, String when, String then) {
        AcceptanceCriterion {
            requireText(given, "criterion given");
            requireText(when, "criterion when");
            requireText(then, "criterion then");
        }
    }

    record Stakeholder(
        String id,
        String name,
        String role,
        int influence,
        int interest,
        Set<String> goals
    ) {
        Stakeholder {
            requireText(id, "stakeholder ID");
            requireText(name, "stakeholder name");
            requireText(role, "stakeholder role");
            if (influence < 1 || influence > 5 || interest < 1 || interest > 5) {
                throw new IllegalArgumentException(
                    "Influence and interest must be between 1 and 5"
                );
            }
            goals = Set.copyOf(goals);
        }
    }

    record ReviewRecord(
        String reviewerId,
        ReviewOutcome outcome,
        String rationale,
        Instant createdAt,
        int requirementVersion
    ) {
        ReviewRecord {
            requireText(reviewerId, "reviewer ID");
            Objects.requireNonNull(outcome, "review outcome");
            requireText(rationale, "review rationale");
            Objects.requireNonNull(createdAt, "review timestamp");
        }
    }

    static final class Requirement {
        private static final Pattern ID_PATTERN =
            Pattern.compile("REQ-(FR|NFR|BR|CON)-\\d{3}");

        private final String id;
        private String title;
        private String description;
        private final RequirementType type;
        private final Priority priority;
        private final String owner;
        private final String source;
        private String targetMetric;
        private final Set<String> dependencies = new HashSet<>();
        private final Set<String> deliveryTickets = new HashSet<>();
        private final List<AcceptanceCriterion> criteria = new ArrayList<>();
        private final List<ReviewRecord> reviewHistory = new ArrayList<>();
        private RequirementState state = RequirementState.DRAFT;
        private int version = 1;

        Requirement(
            String id,
            String title,
            String description,
            RequirementType type,
            Priority priority,
            String owner,
            String source
        ) {
            if (!ID_PATTERN.matcher(Objects.requireNonNull(id)).matches()) {
                throw new IllegalArgumentException("Invalid requirement ID: " + id);
            }
            this.id = id;
            this.title = requireText(title, "requirement title");
            this.description = requireText(description, "requirement description");
            this.type = Objects.requireNonNull(type);
            this.priority = Objects.requireNonNull(priority);
            this.owner = requireText(owner, "requirement owner");
            this.source = requireText(source, "requirement source");
        }

        String id() { return id; }
        String title() { return title; }
        String description() { return description; }
        RequirementType type() { return type; }
        Priority priority() { return priority; }
        RequirementState state() { return state; }
        int version() { return version; }
        String targetMetric() { return targetMetric; }

        void addCriterion(AcceptanceCriterion criterion) {
            requireMutable();
            criteria.add(Objects.requireNonNull(criterion));
        }

        void setTargetMetric(String metric) {
            requireMutable();
            targetMetric = requireText(metric, "target metric");
        }

        void addDependency(String dependencyId) {
            requireMutable();
            if (id.equals(dependencyId)) {
                throw new IllegalArgumentException("A requirement cannot depend on itself");
            }
            dependencies.add(requireText(dependencyId, "dependency ID"));
        }

        void linkDeliveryTicket(String ticketId) {
            deliveryTickets.add(requireText(ticketId, "delivery ticket"));
        }

        Set<String> dependencies() {
            return Set.copyOf(dependencies);
        }

        Set<String> deliveryTickets() {
            return Set.copyOf(deliveryTickets);
        }

        List<ReviewRecord> reviewHistory() {
            return List.copyOf(reviewHistory);
        }

        void revise(String actor, String newTitle, String newDescription) {
            requireText(actor, "revision actor");
            if (state != RequirementState.DRAFT && state != RequirementState.IN_REVIEW) {
                throw new IllegalStateException(
                    "Approved baseline changes require a controlled change request"
                );
            }
            String validatedTitle = requireText(newTitle, "new title");
            String validatedDescription = requireText(newDescription, "new description");
            title = validatedTitle;
            description = validatedDescription;
            version++;
        }

        void transition(RequirementState next) {
            Objects.requireNonNull(next, "next state");
            boolean allowed = switch (state) {
                case DRAFT -> EnumSet.of(
                    RequirementState.IN_REVIEW, RequirementState.REJECTED
                ).contains(next);
                case IN_REVIEW -> EnumSet.of(
                    RequirementState.DRAFT,
                    RequirementState.APPROVED,
                    RequirementState.REJECTED
                ).contains(next);
                case APPROVED -> EnumSet.of(
                    RequirementState.IN_REVIEW,
                    RequirementState.IMPLEMENTED
                ).contains(next);
                case IMPLEMENTED -> next == RequirementState.VERIFIED;
                case VERIFIED -> next == RequirementState.IN_REVIEW;
                case REJECTED -> next == RequirementState.DRAFT;
            };

            if (!allowed) {
                throw new IllegalStateException(
                    "Invalid requirement transition: " + state + " -> " + next
                );
            }
            state = next;
        }

        void validate() {
            if (description.length() < 15) {
                throw new IllegalStateException(id + ": description is not specific enough");
            }
            if (type == RequirementType.FUNCTIONAL && criteria.isEmpty()) {
                throw new IllegalStateException(id + ": acceptance criteria are required");
            }
            if (type == RequirementType.NON_FUNCTIONAL &&
                (targetMetric == null || targetMetric.isBlank())) {
                throw new IllegalStateException(id + ": measurable target is required");
            }
            if (deliveryTickets.isEmpty()) {
                throw new IllegalStateException(id + ": implementation trace is missing");
            }
        }

        private void requireMutable() {
            if (state != RequirementState.DRAFT && state != RequirementState.IN_REVIEW) {
                throw new IllegalStateException(
                    "Only draft or in-review requirements can be edited directly"
                );
            }
        }
    }

    record ChangeRequest(
        String id,
        String requirementId,
        String requester,
        String description,
        double effortDays,
        String impact,
        ChangeState state,
        String decisionReason
    ) {
        ChangeRequest {
            requireText(id, "change ID");
            requireText(requirementId, "requirement ID");
            requireText(requester, "requester");
            requireText(description, "change description");
            requireText(impact, "change impact");
            if (!Double.isFinite(effortDays) || effortDays <= 0) {
                throw new IllegalArgumentException("Effort must be positive and finite");
            }
            Objects.requireNonNull(state);
            requireText(decisionReason, "decision reason");
        }
    }

    record ReleaseAssessment(
        boolean ready,
        List<String> unverifiedMandatoryRequirements,
        List<String> traceabilityGaps,
        List<String> dependencyErrors
    ) {
        ReleaseAssessment {
            unverifiedMandatoryRequirements = List.copyOf(unverifiedMandatoryRequirements);
            traceabilityGaps = List.copyOf(traceabilityGaps);
            dependencyErrors = List.copyOf(dependencyErrors);
        }
    }

    static final class RequirementsService {
        private final Map<String, Requirement> requirements = new LinkedHashMap<>();
        private final Map<String, Stakeholder> stakeholders = new LinkedHashMap<>();
        private final Map<String, ChangeRequest> changes = new LinkedHashMap<>();

        void addStakeholder(Stakeholder stakeholder) {
            if (stakeholders.putIfAbsent(stakeholder.id(), stakeholder) != null) {
                throw new IllegalArgumentException(
                    "Duplicate stakeholder: " + stakeholder.id()
                );
            }
        }

        void addRequirement(Requirement requirement) {
            requirement.validate();
            if (requirements.putIfAbsent(requirement.id(), requirement) != null) {
                throw new IllegalArgumentException(
                    "Duplicate requirement: " + requirement.id()
                );
            }
        }

        Requirement getRequirement(String id) {
            Requirement requirement = requirements.get(id);
            if (requirement == null) {
                throw new IllegalArgumentException("Unknown requirement: " + id);
            }
            return requirement;
        }

        void submitReview(
            String requirementId,
            String reviewerId,
            ReviewOutcome outcome,
            String rationale
        ) {
            Requirement requirement = getRequirement(requirementId);
            if (!stakeholders.containsKey(reviewerId)) {
                throw new IllegalArgumentException("Reviewer is not a registered stakeholder");
            }
            if (requirement.state() != RequirementState.IN_REVIEW) {
                throw new IllegalStateException(
                    "Review decisions require an in-review requirement"
                );
            }
            requirement.reviewHistory.add(new ReviewRecord(
                reviewerId,
                outcome,
                requireText(rationale, "review rationale"),
                Instant.now(),
                requirement.version()
            ));

            if (outcome == ReviewOutcome.REQUEST_CHANGES) {
                requirement.transition(RequirementState.DRAFT);
            } else if (outcome == ReviewOutcome.APPROVE) {
                requirement.transition(RequirementState.APPROVED);
            }
        }

        void recordChange(ChangeRequest request) {
            getRequirement(request.requirementId());
            if (changes.putIfAbsent(request.id(), request) != null) {
                throw new IllegalArgumentException("Duplicate change request");
            }
        }

        List<String> dependencyErrors() {
            List<String> errors = new ArrayList<>();
            for (Requirement requirement : requirements.values()) {
                for (String dependency : requirement.dependencies()) {
                    if (!requirements.containsKey(dependency)) {
                        errors.add(
                            requirement.id() + " depends on missing " + dependency
                        );
                    }
                }
            }
            errors.addAll(findDependencyCycles());
            return errors;
        }

        private List<String> findDependencyCycles() {
            Set<String> visited = new HashSet<>();
            Set<String> active = new HashSet<>();
            List<String> errors = new ArrayList<>();
            for (String id : requirements.keySet()) {
                visitDependency(id, visited, active, new ArrayList<>(), errors);
            }
            return errors.stream().distinct().toList();
        }

        private void visitDependency(
            String id,
            Set<String> visited,
            Set<String> active,
            List<String> path,
            List<String> errors
        ) {
            if (active.contains(id)) {
                errors.add("Circular dependency detected: " + path + " -> " + id);
                return;
            }
            if (!visited.add(id)) return;

            active.add(id);
            path.add(id);
            Requirement requirement = requirements.get(id);
            if (requirement != null) {
                for (String dependency : requirement.dependencies()) {
                    if (requirements.containsKey(dependency)) {
                        visitDependency(dependency, visited, active, path, errors);
                    }
                }
            }
            path.remove(path.size() - 1);
            active.remove(id);
        }

        ReleaseAssessment assessRelease() {
            List<String> unverified = requirements.values().stream()
                .filter(r -> r.priority() == Priority.MUST)
                .filter(r -> r.state() != RequirementState.VERIFIED)
                .map(Requirement::id)
                .toList();

            List<String> gaps = new ArrayList<>();
            for (Requirement requirement : requirements.values()) {
                try {
                    requirement.validate();
                } catch (IllegalStateException exception) {
                    gaps.add(exception.getMessage());
                }
            }

            List<String> dependencyProblems = dependencyErrors();
            return new ReleaseAssessment(
                unverified.isEmpty() && gaps.isEmpty() && dependencyProblems.isEmpty(),
                unverified,
                gaps,
                dependencyProblems
            );
        }

        Collection<Requirement> requirements() {
            return List.copyOf(requirements.values());
        }

        List<Requirement> prioritizedOptionalRequirements() {
            // Mandatory requirements are policy obligations, not candidates for RICE ranking.
            return requirements.values().stream()
                .filter(r -> r.priority() == Priority.COULD ||
                             r.priority() == Priority.SHOULD)
                .sorted(Comparator.comparing(Requirement::id))
                .toList();
        }
    }

    static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " cannot be empty");
        }
        return value.trim();
    }

    static double riceScore(double reach, double impact, double confidence, double effort) {
        if (!Double.isFinite(reach) || !Double.isFinite(impact) ||
            !Double.isFinite(confidence) || !Double.isFinite(effort) ||
            reach < 0 || impact < 0 || confidence < 0 || confidence > 1 || effort <= 0) {
            throw new IllegalArgumentException("Invalid RICE input");
        }
        return reach * impact * confidence / effort;
    }

    public static void main(String[] args) {
        RequirementsService service = new RequirementsService();

        service.addStakeholder(new Stakeholder(
            "ST-001",
            "Maya Rao",
            "Procurement analyst",
            4,
            5,
            Set.of("track supplier applications", "reduce rework")
        ));
        service.addStakeholder(new Stakeholder(
            "ST-002",
            "Arjun Sen",
            "Compliance officer",
            5,
            4,
            Set.of("retain audit evidence", "enforce document policies")
        ));

        Requirement intake = new Requirement(
            "REQ-FR-001",
            "Create supplier application",
            "Authenticated suppliers can create a draft with legal identity and contact details.",
            RequirementType.FUNCTIONAL,
            Priority.MUST,
            "Product manager",
            "Supplier interviews"
        );
        intake.addCriterion(new AcceptanceCriterion(
            "Supplier is authenticated",
            "Valid required fields are submitted",
            "A draft is created and a reference is returned"
        ));
        intake.linkDeliveryTicket("SUP-101");
        service.addRequirement(intake);

        Requirement documents = new Requirement(
            "REQ-FR-002",
            "Check mandatory documents",
            "The portal validates documents against the published supplier-category checklist.",
            RequirementType.FUNCTIONAL,
            Priority.MUST,
            "Product manager",
            "Compliance workshop"
        );
        documents.addCriterion(new AcceptanceCriterion(
            "A checklist has been published",
            "The supplier submits the application",
            "Missing mandatory documents are reported and final submission is blocked"
        ));
        documents.addDependency("REQ-FR-001");
        documents.linkDeliveryTicket("SUP-110");
        service.addRequirement(documents);

        Requirement latency = new Requirement(
            "REQ-NFR-001",
            "Meet read-latency target",
            "The portal serves application reads within the agreed latency under concurrent load.",
            RequirementType.NON_FUNCTIONAL,
            Priority.MUST,
            "Engineering lead",
            "Performance review"
        );
        latency.setTargetMetric("p95 < 300 ms at 500 concurrent users");
        latency.linkDeliveryTicket("OPS-40");
        service.addRequirement(latency);

        intake.transition(RequirementState.IN_REVIEW);
        service.submitReview(
            "REQ-FR-001",
            "ST-001",
            ReviewOutcome.APPROVE,
            "Required identity fields and duplicate handling are testable."
        );

        documents.transition(RequirementState.IN_REVIEW);
        service.submitReview(
            "REQ-FR-002",
            "ST-002",
            ReviewOutcome.REQUEST_CHANGES,
            "Specify how category changes affect the required document checklist."
        );

        ChangeRequest change = new ChangeRequest(
            "CR-014",
            "REQ-FR-002",
            "ST-002",
            "Add reminders before supplier documents expire",
            4.0,
            "Requires notification preferences and scheduling",
            ChangeState.DEFERRED,
            "Deferred pending capacity and notification-policy review"
        );
        service.recordChange(change);

        System.out.println("Requirement states");
        for (Requirement requirement : service.requirements()) {
            System.out.printf(
                "%s | %s | %s | version %d%n",
                requirement.id(),
                requirement.priority(),
                requirement.state(),
                requirement.version()
            );
        }

        System.out.println("\nDependency validation");
        service.dependencyErrors().forEach(System.out::println);

        System.out.println("\nOptional requirement prioritization");
        service.prioritizedOptionalRequirements().forEach(
            requirement -> System.out.println(requirement.id() + ": " + requirement.title())
        );
        System.out.printf(
            "Expiry reminder RICE score: %.2f%n",
            riceScore(500, 1.5, 0.8, 4)
        );

        System.out.println("\nRelease assessment");
        ReleaseAssessment assessment = service.assessRelease();
        System.out.println("Ready: " + assessment.ready());
        System.out.println("Unverified mandatory requirements: " +
            assessment.unverifiedMandatoryRequirements());
        System.out.println("Traceability gaps: " + assessment.traceabilityGaps());
        System.out.println("Dependency errors: " + assessment.dependencyErrors());

        try {
            riceScore(100, 2, 0.8, 0);
        } catch (IllegalArgumentException exception) {
            System.out.println("Rejected invalid RICE calculation: " + exception.getMessage());
        }

        try {
            documents.transition(RequirementState.VERIFIED);
        } catch (IllegalStateException exception) {
            System.out.println("Rejected invalid state transition: " + exception.getMessage());
        }
    }
}
