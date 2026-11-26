import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/*
 * EXPERIMENTATION: ENTERPRISE EXPERIMENT GOVERNANCE
 *
 * Java 17 implementation of a controlled experimentation platform.
 *
 * Features:
 * - Immutable domain records
 * - Hypothesis management
 * - Experiment lifecycle
 * - Randomized allocation
 * - Control and treatment variants
 * - Metric aggregation
 * - Statistical evaluation
 * - Approval-independent experiment governance
 * - Guardrail enforcement
 * - Audit events
 * - Validation and exception handling
 */

public class ExperimentationEnterprise {

    // -----------------------------------------------------
    // 1. ENUMERATIONS
    // -----------------------------------------------------

    enum ExperimentStatus {
        DRAFT,
        RUNNING,
        COMPLETED,
        CANCELLED
    }

    enum Group {
        CONTROL,
        TREATMENT
    }

    enum Direction {
        INCREASE,
        DECREASE,
        DIFFERENT
    }

    enum Decision {
        REJECT_NULL,
        FAIL_TO_REJECT_NULL,
        INVALID
    }


    // -----------------------------------------------------
    // 2. CUSTOM EXCEPTIONS
    // -----------------------------------------------------

    static class ExperimentException extends RuntimeException {
        ExperimentException(String message) {
            super(message);
        }
    }

    static class ValidationException extends ExperimentException {
        ValidationException(String message) {
            super(message);
        }
    }


    // -----------------------------------------------------
    // 3. DOMAIN RECORDS
    // -----------------------------------------------------

    record Hypothesis(
        String researchQuestion,
        String nullHypothesis,
        String alternativeHypothesis,
        String metric,
        Direction direction
    ) {
        Hypothesis {
            requireText(researchQuestion, "Research question");
            requireText(nullHypothesis, "Null hypothesis");
            requireText(alternativeHypothesis, "Alternative hypothesis");
            requireText(metric, "Metric");

            Objects.requireNonNull(direction);
        }
    }

    record ExperimentPolicy(
        double significanceLevel,
        double statisticalPower,
        int minimumGroupSize,
        double maximumGuardrailIncrease
    ) {
        ExperimentPolicy {
            if (
                significanceLevel <= 0 ||
                significanceLevel >= 1
            ) {
                throw new ValidationException("Invalid significance level.");
            }

            if (
                statisticalPower <= 0 ||
                statisticalPower >= 1
            ) {
                throw new ValidationException("Invalid statistical power.");
            }

            if (minimumGroupSize < 2) {
                throw new ValidationException("Invalid minimum group size.");
            }

            if (maximumGuardrailIncrease < 0) {
                throw new ValidationException("Invalid guardrail threshold.");
            }
        }
    }

    record ExperimentDefinition(
        UUID id,
        String name,
        Hypothesis hypothesis,
        double baselineRate,
        double treatmentRate,
        long randomSeed,
        ExperimentPolicy policy
    ) {
        ExperimentDefinition {
            Objects.requireNonNull(id);
            Objects.requireNonNull(hypothesis);
            Objects.requireNonNull(policy);

            requireText(name, "Experiment name");

            validateProbability(baselineRate, "Baseline rate");
            validateProbability(treatmentRate, "Treatment rate");

            if (baselineRate == 0 || baselineRate == 1) {
                throw new ValidationException(
                    "Baseline rate must be between 0 and 1."
                );
            }
        }
    }

    record Participant(
        String participantId,
        Group group
    ) {}

    record Observation(
        String participantId,
        Group group,
        boolean converted,
        long timestamp
    ) {}

    record GroupMetrics(
        int participants,
        int conversions,
        double conversionRate
    ) {}

    record ConfidenceInterval(
        double lower,
        double upper
    ) {}

    record AnalysisResult(
        UUID experimentId,
        GroupMetrics control,
        GroupMetrics treatment,
        double absoluteEffect,
        double relativeEffect,
        double zScore,
        double pValue,
        ConfidenceInterval confidenceInterval,
        boolean guardrailPassed,
        Decision decision
    ) {}

    record AuditEvent(
        long timestamp,
        String event,
        String description
    ) {}


    // -----------------------------------------------------
    // 4. COMMON VALIDATION
    // -----------------------------------------------------

    static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new ValidationException(field + " is required.");
        }
    }

    static void validateProbability(double value, String field) {
        if (
            !Double.isFinite(value) ||
            value < 0 ||
            value > 1
        ) {
            throw new ValidationException(
                field + " must be between 0 and 1."
            );
        }
    }


    // -----------------------------------------------------
    // 5. EXPERIMENT ALLOCATION SERVICE
    // -----------------------------------------------------

    interface AllocationStrategy {
        List<Participant> allocate(
            int count,
            long seed
        );
    }

    static class RandomizedAllocation implements AllocationStrategy {

        @Override
        public List<Participant> allocate(int count, long seed) {
            if (count < 2) {
                throw new ValidationException(
                    "At least two participants are required."
                );
            }

            List<Group> groups = new ArrayList<>();

            for (int i = 0; i < count / 2; i++) {
                groups.add(Group.CONTROL);
                groups.add(Group.TREATMENT);
            }

            if (count % 2 != 0) {
                groups.add(
                    new Random(seed).nextBoolean()
                        ? Group.CONTROL
                        : Group.TREATMENT
                );
            }

            Collections.shuffle(groups, new Random(seed));

            List<Participant> participants = new ArrayList<>();

            for (int i = 0; i < groups.size(); i++) {
                participants.add(
                    new Participant(
                        "PARTICIPANT-" + (i + 1),
                        groups.get(i)
                    )
                );
            }

            return List.copyOf(participants);
        }
    }


    // -----------------------------------------------------
    // 6. EXPERIMENT LIFECYCLE SERVICE
    // -----------------------------------------------------

    static class ExperimentService {

        private final ExperimentDefinition definition;
        private final AllocationStrategy allocationStrategy;

        private ExperimentStatus status = ExperimentStatus.DRAFT;

        private List<Participant> participants = List.of();
        private List<Observation> observations = List.of();

        private final List<AuditEvent> auditEvents =
            new ArrayList<>();

        ExperimentService(
            ExperimentDefinition definition,
            AllocationStrategy allocationStrategy
        ) {
            this.definition = Objects.requireNonNull(definition);
            this.allocationStrategy =
                Objects.requireNonNull(allocationStrategy);
        }

        private void audit(String event, String description) {
            auditEvents.add(
                new AuditEvent(
                    System.currentTimeMillis(),
                    event,
                    description
                )
            );
        }

        private void requireStatus(ExperimentStatus expected) {
            if (status != expected) {
                throw new ExperimentException(
                    "Expected " + expected + " but found " + status
                );
            }
        }

        public synchronized void start() {
            requireStatus(ExperimentStatus.DRAFT);

            status = ExperimentStatus.RUNNING;

            audit("STARTED", "Experiment execution initiated.");
        }

        public synchronized void cancel(String reason) {
            if (
                status != ExperimentStatus.DRAFT &&
                status != ExperimentStatus.RUNNING
            ) {
                throw new ExperimentException(
                    "Experiment cannot be cancelled."
                );
            }

            status = ExperimentStatus.CANCELLED;

            audit("CANCELLED", reason);
        }

        public synchronized List<Participant> assign(int count) {
            requireStatus(ExperimentStatus.RUNNING);

            if (!participants.isEmpty()) {
                throw new ExperimentException(
                    "Participants have already been assigned."
                );
            }

            participants = allocationStrategy.allocate(
                count,
                definition.randomSeed()
            );

            audit(
                "ASSIGNMENT",
                "Assigned " + participants.size() + " participants."
            );

            return participants;
        }

        // -------------------------------------------------
        // 7. EXPERIMENT EXECUTION
        // -------------------------------------------------

        public synchronized List<Observation> execute() {
            requireStatus(ExperimentStatus.RUNNING);

            if (participants.isEmpty()) {
                throw new ExperimentException(
                    "Participant assignment is missing."
                );
            }

            if (!observations.isEmpty()) {
                throw new ExperimentException(
                    "Experiment has already been executed."
                );
            }

            Random random = new Random(
                definition.randomSeed() + 100
            );

            List<Observation> results = new ArrayList<>();

            for (Participant participant : participants) {
                double probability =
                    participant.group() == Group.CONTROL
                        ? definition.baselineRate()
                        : definition.treatmentRate();

                boolean converted =
                    random.nextDouble() < probability;

                results.add(
                    new Observation(
                        participant.participantId(),
                        participant.group(),
                        converted,
                        System.currentTimeMillis()
                    )
                );
            }

            observations = List.copyOf(results);

            audit(
                "EXECUTION",
                "Recorded " + observations.size() + " observations."
            );

            return observations;
        }

        // -------------------------------------------------
        // 8. DATA INTEGRITY
        // -------------------------------------------------

        private void validateObservations() {
            if (observations.size() != participants.size()) {
                throw new ExperimentException(
                    "Observation count does not match assignment count."
                );
            }

            Map<String, Group> assignmentMap = new HashMap<>();

            for (Participant participant : participants) {
                assignmentMap.put(
                    participant.participantId(),
                    participant.group()
                );
            }

            Set<String> seen = new HashSet<>();

            for (Observation observation : observations) {
                Group assigned = assignmentMap.get(
                    observation.participantId()
                );

                if (
                    assigned == null ||
                    assigned != observation.group() ||
                    !seen.add(observation.participantId())
                ) {
                    throw new ExperimentException(
                        "Observation integrity violation."
                    );
                }
            }
        }

        // -------------------------------------------------
        // 9. METRIC AGGREGATION
        // -------------------------------------------------

        private GroupMetrics aggregate(Group group) {
            int total = 0;
            int conversions = 0;

            for (Observation observation : observations) {
                if (observation.group() != group) {
                    continue;
                }

                total++;

                if (observation.converted()) {
                    conversions++;
                }
            }

            return new GroupMetrics(
                total,
                conversions,
                total == 0 ? 0 : (double) conversions / total
            );
        }

        // -------------------------------------------------
        // 10. STATISTICAL SERVICE
        // -------------------------------------------------

        public synchronized AnalysisResult analyze(
            double controlErrorRate,
            double treatmentErrorRate
        ) {
            requireStatus(ExperimentStatus.RUNNING);

            validateProbability(controlErrorRate, "Control error rate");
            validateProbability(treatmentErrorRate, "Treatment error rate");

            validateObservations();

            GroupMetrics control = aggregate(Group.CONTROL);
            GroupMetrics treatment = aggregate(Group.TREATMENT);

            int minimum = definition.policy().minimumGroupSize();

            if (
                control.participants() < minimum ||
                treatment.participants() < minimum
            ) {
                throw new ExperimentException(
                    "Insufficient sample size."
                );
            }

            double pooled =
                (double) (
                    control.conversions() +
                    treatment.conversions()
                ) /
                (
                    control.participants() +
                    treatment.participants()
                );

            double standardError = Math.sqrt(
                pooled * (1 - pooled) *
                (
                    1.0 / control.participants() +
                    1.0 / treatment.participants()
                )
            );

            if (standardError == 0) {
                throw new ExperimentException(
                    "Statistical variance is zero."
                );
            }

            double effect =
                treatment.conversionRate() -
                control.conversionRate();

            double z = effect / standardError;

            double pValue = erfc(
                Math.abs(z) / Math.sqrt(2)
            );

            double confidenceError = 1.95996398454 *
                Math.sqrt(
                    control.conversionRate() *
                    (1 - control.conversionRate()) /
                    control.participants()
                    +
                    treatment.conversionRate() *
                    (1 - treatment.conversionRate()) /
                    treatment.participants()
                );

            ConfidenceInterval interval = new ConfidenceInterval(
                effect - confidenceError,
                effect + confidenceError
            );

            boolean guardrailPassed =
                treatmentErrorRate - controlErrorRate
                <= definition.policy().maximumGuardrailIncrease();

            boolean favorable = switch (
                definition.hypothesis().direction()
            ) {
                case INCREASE -> effect > 0;
                case DECREASE -> effect < 0;
                case DIFFERENT -> true;
            };

            Decision decision;

            if (!guardrailPassed) {
                decision = Decision.INVALID;
            } else if (
                pValue < definition.policy().significanceLevel()
                && favorable
            ) {
                decision = Decision.REJECT_NULL;
            } else {
                decision = Decision.FAIL_TO_REJECT_NULL;
            }

            AnalysisResult result = new AnalysisResult(
                definition.id(),
                control,
                treatment,
                effect,
                control.conversionRate() > 0
                    ? effect / control.conversionRate()
                    : 0,
                z,
                pValue,
                interval,
                guardrailPassed,
                decision
            );

            status = ExperimentStatus.COMPLETED;

            audit(
                "ANALYSIS",
                "Statistical analysis completed: " + decision
            );

            return result;
        }

        // -------------------------------------------------
        // 11. AUDIT AND ACCESSORS
        // -------------------------------------------------

        public List<AuditEvent> getAuditEvents() {
            return List.copyOf(auditEvents);
        }

        public ExperimentStatus getStatus() {
            return status;
        }

        public ExperimentDefinition getDefinition() {
            return definition;
        }
    }


    // -----------------------------------------------------
    // 12. SAMPLE SIZE ESTIMATION
    // -----------------------------------------------------

    static class SampleSizeCalculator {

        static int calculate(
            double p1,
            double p2,
            double alpha,
            double power
        ) {
            validateProbability(p1, "Baseline");
            validateProbability(p2, "Treatment");

            if (
                p1 == 0 || p1 == 1 ||
                p2 == 0 || p2 == 1 ||
                p1 == p2
            ) {
                throw new ValidationException(
                    "Invalid effect size."
                );
            }

            if (!(alpha > 0 && alpha < 1)) {
                throw new ValidationException("Invalid alpha.");
            }

            if (!(power > 0 && power < 1)) {
                throw new ValidationException("Invalid power.");
            }

            double zAlpha = alpha == 0.05
                ? 1.959964
                : 2.575829;

            double zBeta = power >= 0.90
                ? 1.281552
                : 0.841621;

            double pooled = (p1 + p2) / 2;

            double numerator = Math.pow(
                zAlpha * Math.sqrt(2 * pooled * (1 - pooled))
                +
                zBeta * Math.sqrt(
                    p1 * (1 - p1) + p2 * (1 - p2)
                ),
                2
            );

            return (int) Math.ceil(
                numerator / Math.pow(p2 - p1, 2)
            );
        }
    }


    // -----------------------------------------------------
    // 13. STATISTICAL HELPER
    // -----------------------------------------------------

    static double erfc(double x) {
        double z = Math.abs(x);

        double t = 1.0 / (1.0 + 0.5 * z);

        double answer = t * Math.exp(
            -z * z
            - 1.26551223
            + t * (
                1.00002368
                + t * (
                    0.37409196
                    + t * (
                        0.09678418
                        + t * (
                            -0.18628806
                            + t * (
                                0.27886807
                                + t * (
                                    -1.13520398
                                    + t * (
                                        1.48851587
                                        + t * (
                                            -0.82215223
                                            + t * 0.17087277
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        );

        return x >= 0 ? answer : 2 - answer;
    }


    // -----------------------------------------------------
    // 14. MAIN EXECUTION
    // -----------------------------------------------------

    public static void main(String[] args) {

        Hypothesis hypothesis = new Hypothesis(
            "Does a redesigned checkout increase purchases?",
            "The redesigned checkout does not change conversion.",
            "The redesigned checkout increases conversion.",
            "purchase_conversion",
            Direction.INCREASE
        );

        ExperimentPolicy policy = new ExperimentPolicy(
            0.05,
            0.80,
            30,
            0.01
        );

        ExperimentDefinition definition =
            new ExperimentDefinition(
                UUID.randomUUID(),
                "Enterprise Checkout Experiment",
                hypothesis,
                0.10,
                0.125,
                42,
                policy
            );

        AllocationStrategy allocation =
            new RandomizedAllocation();

        ExperimentService service = new ExperimentService(
            definition,
            allocation
        );

        System.out.println("EXPERIMENT");
        System.out.println("----------");

        System.out.println(definition.name());

        System.out.println(
            "Estimated sample size per group: " +
            SampleSizeCalculator.calculate(
                definition.baselineRate(),
                definition.treatmentRate(),
                policy.significanceLevel(),
                policy.statisticalPower()
            )
        );

        service.start();

        service.assign(2000);

        service.execute();

        AnalysisResult result = service.analyze(
            0.02,
            0.021
        );

        System.out.println("\nANALYSIS REPORT");
        System.out.println("----------------");

        System.out.println("Control rate: " +
            result.control().conversionRate());

        System.out.println("Treatment rate: " +
            result.treatment().conversionRate());

        System.out.println("Absolute effect: " +
            result.absoluteEffect());

        System.out.println("P-value: " +
            result.pValue());

        System.out.println("Confidence interval: " +
            result.confidenceInterval());

        System.out.println("Guardrail passed: " +
            result.guardrailPassed());

        System.out.println("Decision: " +
            result.decision());

        System.out.println("\nAUDIT EVENTS");

        service.getAuditEvents().forEach(event ->
            System.out.println(
                event.event() + ": " + event.description()
            )
        );

        System.out.println("\nFinal state: " + service.getStatus());
    }
}
