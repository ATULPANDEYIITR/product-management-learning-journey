import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class SolutionDesign {

    enum HypothesisStatus {
        PROPOSED, VALIDATED, REJECTED
    }

    enum ConstraintType {
        FUNCTIONAL, NON_FUNCTIONAL, TECHNICAL, BUSINESS, REGULATORY
    }

    enum DecisionStatus {
        PROPOSED, SELECTED, REJECTED
    }

    record Hypothesis(
        String id,
        String statement,
        String evidenceRequired,
        HypothesisStatus status,
        double confidence
    ) {
        Hypothesis {
            Objects.requireNonNull(id);
            Objects.requireNonNull(statement);
            Objects.requireNonNull(evidenceRequired);

            if (confidence < 0 || confidence > 1) {
                throw new IllegalArgumentException(
                    "Confidence must be between 0 and 1."
                );
            }
        }

        Hypothesis evaluate(
            double evidenceQuality,
            double observedValue,
            double requiredValue
        ) {
            if (evidenceQuality < 0 || evidenceQuality > 1) {
                throw new IllegalArgumentException(
                    "Evidence quality must be between 0 and 1."
                );
            }

            if (observedValue >= requiredValue) {
                return new Hypothesis(
                    id,
                    statement,
                    evidenceRequired,
                    HypothesisStatus.VALIDATED,
                    Math.min(1.0, 0.5 + 0.5 * evidenceQuality)
                );
            }

            return new Hypothesis(
                id,
                statement,
                evidenceRequired,
                HypothesisStatus.REJECTED,
                Math.max(0.0, 0.5 * (1.0 - evidenceQuality))
            );
        }
    }

    record Constraint(
        String id,
        ConstraintType type,
        String description,
        boolean hard
    ) {
        Constraint {
            Objects.requireNonNull(id);
            Objects.requireNonNull(type);
            Objects.requireNonNull(description);
        }
    }

    record Alternative(
        String name,
        String description,
        double expectedValue,
        double deliveryCost,
        double operatingCost,
        double implementationRisk,
        double scalability,
        double maintainability,
        double reversibility,
        double constraintPenalty
    ) {
        double score() {
            return expectedValue
                + 0.20 * scalability
                + 0.15 * maintainability
                + 0.10 * reversibility
                - 0.35 * implementationRisk
                - 0.15 * deliveryCost
                - 0.10 * operatingCost
                - constraintPenalty;
        }
    }

    record TradeOff(
        String criterion,
        String preferredAlternative,
        String rationale
    ) {}

    record Decision(
        Alternative selected,
        List<Alternative> rejected,
        List<TradeOff> tradeOffs
    ) {}

    static final class DesignRepository {
        private final Map<String, Hypothesis> hypotheses =
            new LinkedHashMap<>();

        private final Map<String, Constraint> constraints =
            new LinkedHashMap<>();

        private final List<Alternative> alternatives =
            new ArrayList<>();

        void addHypothesis(Hypothesis hypothesis) {
            if (hypotheses.putIfAbsent(hypothesis.id(), hypothesis) != null) {
                throw new IllegalArgumentException(
                    "Duplicate hypothesis: " + hypothesis.id()
                );
            }
        }

        void addConstraint(Constraint constraint) {
            if (constraints.putIfAbsent(
                constraint.id(), constraint
            ) != null) {
                throw new IllegalArgumentException(
                    "Duplicate constraint: " + constraint.id()
                );
            }
        }

        void addAlternative(Alternative alternative) {
            if (alternatives.stream()
                    .anyMatch(a -> a.name().equals(alternative.name()))) {
                throw new IllegalArgumentException(
                    "Duplicate alternative: " + alternative.name()
                );
            }
            alternatives.add(alternative);
        }

        private void requireResolvedHypotheses() {
            List<String> unresolved = hypotheses.values()
                .stream()
                .filter(h -> h.status() == HypothesisStatus.PROPOSED)
                .map(Hypothesis::id)
                .toList();

            if (!unresolved.isEmpty()) {
                throw new IllegalStateException(
                    "Unresolved hypotheses: " + String.join(", ", unresolved)
                );
            }
        }

        List<Alternative> rankedAlternatives() {
            requireResolvedHypotheses();

            return alternatives.stream()
                .sorted(
                    Comparator.comparingDouble(Alternative::score)
                        .reversed()
                )
                .toList();
        }

        Decision decide() {
            List<Alternative> ranked = rankedAlternatives();

            if (ranked.isEmpty()) {
                throw new IllegalStateException(
                    "At least one alternative is required."
                );
            }

            Alternative selected = ranked.getFirst();

            List<TradeOff> tradeOffs = List.of(
                new TradeOff(
                    "Latency",
                    "Queue-backed asynchronous architecture",
                    "Acknowledgement is decoupled from downstream processing."
                ),
                new TradeOff(
                    "Operational simplicity",
                    "Direct synchronous API",
                    "It has fewer infrastructure components and failure states."
                ),
                new TradeOff(
                    "Replay capability",
                    "Managed event-streaming architecture",
                    "Durable streams are designed for high-throughput replay."
                )
            );

            return new Decision(
                selected,
                ranked.subList(1, ranked.size()),
                tradeOffs
            );
        }

        void printDomainModel() {
            System.out.println("\n=== Enterprise design model ===");

            for (Constraint constraint : constraints.values()) {
                System.out.printf(
                    "%s [%s] %s%n",
                    constraint.id(),
                    constraint.type(),
                    constraint.description()
                );
            }
        }

        void printHypotheses() {
            System.out.println("\n=== Hypothesis states ===");

            hypotheses.values().forEach(h ->
                System.out.printf(
                    "%s: %s, confidence=%.2f%n",
                    h.id(),
                    h.status(),
                    h.confidence()
                )
            );
        }
    }

    static DesignRepository buildRepository() {
        DesignRepository repository = new DesignRepository();

        Hypothesis async = new Hypothesis(
            "H-ASYNC",
            "Asynchronous processing absorbs bursts without blocking clients.",
            "Load-test p95 latency and queue-depth measurements.",
            HypothesisStatus.PROPOSED,
            0.5
        ).evaluate(0.90, 0.91, 0.80);

        Hypothesis durable = new Hypothesis(
            "H-DURABLE",
            "Durable buffering preserves accepted events through failures.",
            "Failure-injection and restart tests.",
            HypothesisStatus.PROPOSED,
            0.5
        ).evaluate(0.95, 0.98, 0.90);

        Hypothesis replay = new Hypothesis(
            "H-REPLAY",
            "Replay is valuable when downstream transformations change.",
            "Production reprocessing evidence.",
            HypothesisStatus.PROPOSED,
            0.5
        ).evaluate(0.75, 0.86, 0.70);

        repository.addHypothesis(async);
        repository.addHypothesis(durable);
        repository.addHypothesis(replay);

        repository.addConstraint(new Constraint(
            "C-LATENCY",
            ConstraintType.NON_FUNCTIONAL,
            "Client acknowledgement should normally remain below 300 ms.",
            true
        ));

        repository.addConstraint(new Constraint(
            "C-DURABILITY",
            ConstraintType.TECHNICAL,
            "Accepted events must survive consumer restart.",
            true
        ));

        repository.addConstraint(new Constraint(
            "C-BUDGET",
            ConstraintType.BUSINESS,
            "Infrastructure and operating costs must remain moderate.",
            true
        ));

        repository.addConstraint(new Constraint(
            "C-AUDIT",
            ConstraintType.REGULATORY,
            "Processing outcomes must remain traceable.",
            true
        ));

        repository.addAlternative(new Alternative(
            "Direct synchronous API",
            "Request waits for processing.",
            6.0, 2.0, 2.0, 2.0, 4.0, 7.0, 8.0, 3.0
        ));

        repository.addAlternative(new Alternative(
            "Queue-backed asynchronous architecture",
            "API acknowledges accepted work while workers process durable messages.",
            9.0, 4.0, 4.0, 3.0, 8.0, 8.0, 8.0, 0.0
        ));

        repository.addAlternative(new Alternative(
            "Managed event-streaming architecture",
            "Partitioned streams support throughput and historical replay.",
            9.5, 7.0, 6.0, 5.0, 10.0, 6.0, 5.0, 1.5
        ));

        return repository;
    }

    static void printDecision(Decision decision) {
        System.out.println("\n=== Decision ===");
        System.out.printf(
            "Selected: %s%nScore: %.3f%n",
            decision.selected().name(),
            decision.selected().score()
        );

        System.out.println("\nRejected alternatives:");
        decision.rejected().forEach(a ->
            System.out.printf(
                "%s: %.3f%n",
                a.name(),
                a.score()
            )
        );

        System.out.println("\nTrade-offs:");
        decision.tradeOffs().forEach(t ->
            System.out.printf(
                "%s -> %s%n  %s%n",
                t.criterion(),
                t.preferredAlternative(),
                t.rationale()
            )
        );
    }

    public static void main(String[] args) {
        try {
            DesignRepository repository = buildRepository();

            repository.printHypotheses();
            repository.printDomainModel();

            System.out.println("\n=== Ranked alternatives ===");
            repository.rankedAlternatives().forEach(a ->
                System.out.printf(
                    "%s: %.3f%n",
                    a.name(),
                    a.score()
                )
            );

            Decision decision = repository.decide();
            printDecision(decision);

            // A tighter budget changes the decision inputs without changing
            // the domain rules. This makes the trade-off measurable.
            Alternative selected = decision.selected();

            Alternative budgetVariant = new Alternative(
                selected.name(),
                selected.description(),
                selected.expectedValue(),
                selected.deliveryCost() + 2,
                selected.operatingCost() + 1,
                selected.implementationRisk(),
                selected.scalability(),
                selected.maintainability(),
                selected.reversibility(),
                selected.constraintPenalty()
            );

            System.out.println("\n=== Budget sensitivity ===");
            System.out.printf(
                "Baseline: %.3f%nScenario: %.3f%n",
                selected.score(),
                budgetVariant.score()
            );

        } catch (RuntimeException error) {
            System.err.println(
                "Solution design evaluation failed: "
                + error.getMessage()
            );
            System.exit(1);
        }
    }
}
