import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ProductEngineeringCollaboration {

    enum Priority {
        LOW, MEDIUM, HIGH, CRITICAL
    }

    enum WorkState {
        PROPOSED, DISCOVERY, ESTIMATED, READY, BLOCKED, IN_PROGRESS, DONE
    }

    enum DecisionStatus {
        PROPOSED, ACCEPTED, REJECTED
    }

    enum TradeOff {
        SPEED, COST, QUALITY, SECURITY, SCALABILITY, MAINTAINABILITY
    }

    static class CollaborationException extends RuntimeException {
        CollaborationException(String message) {
            super(message);
        }
    }

    static class ValidationException extends CollaborationException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class StateTransitionException extends CollaborationException {
        StateTransitionException(String message) {
            super(message);
        }
    }

    record Estimate(int storyPoints, double engineeringDays, double confidence) {
        Estimate {
            if (storyPoints <= 0) {
                throw new ValidationException("Story points must be positive.");
            }
            if (engineeringDays <= 0) {
                throw new ValidationException("Engineering days must be positive.");
            }
            if (confidence <= 0 || confidence > 1) {
                throw new ValidationException(
                    "Confidence must be between 0 and 1."
                );
            }
        }
    }

    record ArchitectureOption(
        String name,
        String description,
        double deliveryDays,
        double monthlyCost,
        int scalability,
        int maintainability,
        int security,
        int complexity
    ) {
        ArchitectureOption {
            if (name == null || name.isBlank()) {
                throw new ValidationException("Architecture name is required.");
            }
            if (deliveryDays <= 0 || monthlyCost < 0) {
                throw new ValidationException("Architecture cost is invalid.");
            }

            List<Integer> scores = List.of(
                scalability,
                maintainability,
                security,
                complexity
            );

            if (scores.stream().anyMatch(score -> score < 1 || score > 5)) {
                throw new ValidationException(
                    "Architecture scores must be between 1 and 5."
                );
            }
        }
    }

    record Decision(
        String id,
        String title,
        String chosenOption,
        String rationale,
        List<String> tradeOffs,
        DecisionStatus status
    ) {
        Decision {
            if (id == null || id.isBlank() ||
                title == null || title.isBlank() ||
                chosenOption == null || chosenOption.isBlank() ||
                rationale == null || rationale.isBlank()) {
                throw new ValidationException("Decision fields are incomplete.");
            }

            tradeOffs = List.copyOf(tradeOffs);
        }
    }

    static final class Requirement {
        private final String key;
        private final String title;
        private final String description;
        private final List<String> acceptanceCriteria;
        private final Priority priority;
        private final Set<String> dependencies;
        private final List<String> risks;

        private Estimate estimate;
        private WorkState state = WorkState.PROPOSED;

        Requirement(
            String key,
            String title,
            String description,
            List<String> acceptanceCriteria,
            Priority priority,
            Set<String> dependencies,
            List<String> risks
        ) {
            this.key = key;
            this.title = title;
            this.description = description;
            this.acceptanceCriteria = List.copyOf(acceptanceCriteria);
            this.priority = priority;
            this.dependencies = Set.copyOf(dependencies);
            this.risks = List.copyOf(risks);
            validate();
        }

        private void validate() {
            if (key == null || !key.matches("[A-Z]{2,8}-\\d{1,6}")) {
                throw new ValidationException("Invalid requirement key.");
            }
            if (title == null || title.isBlank()) {
                throw new ValidationException("Requirement title is required.");
            }
            if (description == null || description.isBlank()) {
                throw new ValidationException("Requirement description is required.");
            }
            if (acceptanceCriteria.isEmpty() ||
                acceptanceCriteria.stream().anyMatch(String::isBlank)) {
                throw new ValidationException(
                    "Valid acceptance criteria are required."
                );
            }
        }

        void setEstimate(Estimate estimate) {
            this.estimate = estimate;
            if (state == WorkState.PROPOSED ||
                state == WorkState.DISCOVERY) {
                state = WorkState.ESTIMATED;
            }
        }

        String key() {
            return key;
        }

        String title() {
            return title;
        }

        Priority priority() {
            return priority;
        }

        Set<String> dependencies() {
            return dependencies;
        }

        Estimate estimate() {
            return estimate;
        }

        WorkState state() {
            return state;
        }

        void state(WorkState state) {
            this.state = state;
        }
    }

    interface Policy {
        boolean accepts(Requirement requirement, List<ArchitectureOption> options,
                        List<Decision> decisions);

        String reason();
    }

    static final class EstimateConfidencePolicy implements Policy {
        @Override
        public boolean accepts(
            Requirement requirement,
            List<ArchitectureOption> options,
            List<Decision> decisions
        ) {
            return requirement.estimate() != null &&
                   requirement.estimate().confidence() >= 0.60;
        }

        @Override
        public String reason() {
            return "Estimate confidence must be at least 60%.";
        }
    }

    static final class ArchitectureDecisionPolicy implements Policy {
        @Override
        public boolean accepts(
            Requirement requirement,
            List<ArchitectureOption> options,
            List<Decision> decisions
        ) {
            return decisions.stream()
                .anyMatch(decision -> decision.status() == DecisionStatus.ACCEPTED);
        }

        @Override
        public String reason() {
            return "At least one architecture decision must be accepted.";
        }
    }

    static final class DependencyPolicy implements Policy {
        @Override
        public boolean accepts(
            Requirement requirement,
            List<ArchitectureOption> options,
            List<Decision> decisions
        ) {
            return requirement.dependencies().stream()
                .noneMatch(dependency -> dependency.startsWith("BLOCKED:"));
        }

        @Override
        public String reason() {
            return "Blocked dependencies prevent readiness.";
        }
    }

    static final class ArchitectureScoringService {
        private final EnumMap<TradeOff, Double> weights;

        ArchitectureScoringService(Map<TradeOff, Double> weights) {
            this.weights = new EnumMap<>(TradeOff.class);
            this.weights.putAll(weights);

            if (weights.isEmpty()) {
                throw new ValidationException("Weights cannot be empty.");
            }

            if (weights.values().stream().anyMatch(value -> value < 0)) {
                throw new ValidationException("Weights cannot be negative.");
            }
        }

        double score(ArchitectureOption option) {
            return weight(TradeOff.SPEED) * (1.0 / option.deliveryDays())
                + weight(TradeOff.COST)
                    * (1.0 / Math.max(option.monthlyCost(), 1.0))
                + weight(TradeOff.SCALABILITY) * option.scalability()
                + weight(TradeOff.MAINTAINABILITY) * option.maintainability()
                + weight(TradeOff.SECURITY) * option.security()
                + weight(TradeOff.QUALITY) * (6 - option.complexity());
        }

        List<ArchitectureOption> rank(List<ArchitectureOption> options) {
            return options.stream()
                .sorted(Comparator.comparingDouble(this::score).reversed())
                .toList();
        }

        private double weight(TradeOff tradeOff) {
            return weights.getOrDefault(tradeOff, 0.0);
        }
    }

    static final class CollaborationService {
        private final Requirement requirement;
        private final List<ArchitectureOption> architectureOptions =
            new ArrayList<>();
        private final List<Decision> decisions = new ArrayList<>();
        private final List<Policy> policies = List.of(
            new EstimateConfidencePolicy(),
            new ArchitectureDecisionPolicy(),
            new DependencyPolicy()
        );

        CollaborationService(Requirement requirement) {
            this.requirement = requirement;
        }

        void transition(WorkState next) {
            if (!allowed(requirement.state(), next)) {
                throw new StateTransitionException(
                    "Illegal transition from "
                    + requirement.state()
                    + " to "
                    + next
                );
            }

            if (next == WorkState.READY) {
                validateReadiness();
            }

            requirement.state(next);
        }

        void setEstimate(Estimate estimate) {
            requirement.setEstimate(estimate);
        }

        void addArchitectureOption(ArchitectureOption option) {
            boolean duplicate = architectureOptions.stream()
                .anyMatch(existing -> existing.name().equals(option.name()));

            if (duplicate) {
                throw new ValidationException(
                    "Duplicate architecture option: " + option.name()
                );
            }

            architectureOptions.add(option);
        }

        void addDecision(Decision decision) {
            boolean knownOption = architectureOptions.stream()
                .anyMatch(option ->
                    option.name().equals(decision.chosenOption()));

            if (!knownOption) {
                throw new ValidationException(
                    "Decision references an unknown architecture option."
                );
            }

            decisions.add(decision);
        }

        private void validateReadiness() {
            if (architectureOptions.isEmpty()) {
                throw new ValidationException(
                    "At least one architecture option is required."
                );
            }

            for (Policy policy : policies) {
                if (!policy.accepts(requirement, architectureOptions, decisions)) {
                    throw new ValidationException(policy.reason());
                }
            }
        }

        private boolean allowed(WorkState from, WorkState to) {
            return switch (from) {
                case PROPOSED -> to == WorkState.DISCOVERY;
                case DISCOVERY ->
                    to == WorkState.ESTIMATED || to == WorkState.BLOCKED;
                case ESTIMATED ->
                    to == WorkState.READY || to == WorkState.BLOCKED;
                case READY ->
                    to == WorkState.IN_PROGRESS || to == WorkState.BLOCKED;
                case BLOCKED ->
                    to == WorkState.DISCOVERY || to == WorkState.READY;
                case IN_PROGRESS ->
                    to == WorkState.DONE || to == WorkState.BLOCKED;
                case DONE -> false;
            };
        }

        Requirement requirement() {
            return requirement;
        }

        List<ArchitectureOption> architectureOptions() {
            return Collections.unmodifiableList(architectureOptions);
        }

        List<Decision> decisions() {
            return Collections.unmodifiableList(decisions);
        }
    }

    static CollaborationService buildScenario() {
        Requirement requirement = new Requirement(
            "SHIP-415",
            "Introduce controlled feature rollout",
            "Allow product teams to release a new search ranking policy "
                + "through a measurable and reversible rollout.",
            List.of(
                "The rollout can target a defined percentage of traffic.",
                "The previous policy can be restored without redeployment.",
                "Operational metrics identify degraded ranking behavior.",
                "Access to rollout controls is restricted."
            ),
            Priority.HIGH,
            Set.of("SEARCH-390"),
            List.of(
                "Incorrect rollout configuration can affect search quality.",
                "Metrics may lag during rapid traffic changes."
            )
        );

        CollaborationService service = new CollaborationService(requirement);
        service.transition(WorkState.DISCOVERY);

        service.addArchitectureOption(new ArchitectureOption(
            "Server-side feature flag",
            "Evaluate rollout policy centrally at request time.",
            5,
            240,
            5,
            5,
            5,
            2
        ));

        service.addArchitectureOption(new ArchitectureOption(
            "Client-side configuration",
            "Distribute rollout state to clients.",
            3,
            120,
            3,
            3,
            2,
            4
        ));

        service.addArchitectureOption(new ArchitectureOption(
            "Database configuration only",
            "Read a simple rollout percentage directly from storage.",
            2,
            80,
            2,
            2,
            3,
            2
        ));

        ArchitectureScoringService scorer =
            new ArchitectureScoringService(Map.of(
                TradeOff.SPEED, 0.10,
                TradeOff.COST, 0.05,
                TradeOff.SCALABILITY, 0.20,
                TradeOff.MAINTAINABILITY, 0.20,
                TradeOff.SECURITY, 0.35,
                TradeOff.QUALITY, 0.10
            ));

        ArchitectureOption chosen =
            scorer.rank(service.architectureOptions()).get(0);

        service.addDecision(new Decision(
            "ADR-042",
            "Feature rollout control plane",
            chosen.name(),
            "A server-side flag provides centralized authorization, "
                + "consistent evaluation, and immediate rollback.",
            List.of(
                "Adds a small request-time evaluation cost.",
                "Requires reliable configuration storage."
            ),
            DecisionStatus.ACCEPTED
        ));

        service.setEstimate(new Estimate(5, 5.0, 0.86));
        service.transition(WorkState.READY);

        return service;
    }

    static void runValidationTests() {
        try {
            new Estimate(0, 1, 0.8);
            throw new IllegalStateException("Invalid estimate was accepted.");
        } catch (ValidationException expected) {
            // Expected domain failure.
        }

        Requirement requirement = new Requirement(
            "TEST-1",
            "State test",
            "Test requirement.",
            List.of("Criterion"),
            Priority.LOW,
            Set.of(),
            List.of()
        );

        CollaborationService service = new CollaborationService(requirement);

        try {
            service.transition(WorkState.READY);
            throw new IllegalStateException("Invalid transition was accepted.");
        } catch (StateTransitionException expected) {
            // Expected domain failure.
        }
    }

    public static void main(String[] args) {
        runValidationTests();

        try {
            CollaborationService service = buildScenario();

            ArchitectureScoringService scorer =
                new ArchitectureScoringService(Map.of(
                    TradeOff.SPEED, 0.10,
                    TradeOff.SCALABILITY, 0.20,
                    TradeOff.MAINTAINABILITY, 0.20,
                    TradeOff.SECURITY, 0.40,
                    TradeOff.QUALITY, 0.10
                ));

            List<ArchitectureOption> ranking =
                scorer.rank(service.architectureOptions());

            System.out.println("ENTERPRISE PRODUCT-ENGINEERING COLLABORATION");
            System.out.println("=============================================");
            System.out.println("Requirement: " + service.requirement().key());
            System.out.println("Title: " + service.requirement().title());
            System.out.println("Priority: " + service.requirement().priority());
            System.out.println("State: " + service.requirement().state());

            Estimate estimate = service.requirement().estimate();
            System.out.printf(
                "Estimate: %d points, %.1f days, %.0f%% confidence%n",
                estimate.storyPoints(),
                estimate.engineeringDays(),
                estimate.confidence() * 100
            );

            System.out.println("\nArchitecture ranking:");
            for (int i = 0; i < ranking.size(); i++) {
                ArchitectureOption option = ranking.get(i);
                System.out.printf(
                    "%d. %s | score=%.4f | delivery=%.1f days%n",
                    i + 1,
                    option.name(),
                    scorer.score(option),
                    option.deliveryDays()
                );
            }

            System.out.println("\nAccepted decisions:");
            service.decisions().stream()
                .filter(decision -> decision.status() == DecisionStatus.ACCEPTED)
                .forEach(decision -> {
                    System.out.println(
                        decision.id() + ": " + decision.chosenOption()
                    );
                    System.out.println(
                        "Rationale: " + decision.rationale()
                    );
                });

            System.out.println("\nImplementation readiness: READY");
        } catch (CollaborationException exception) {
            System.err.println(
                "Domain failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
