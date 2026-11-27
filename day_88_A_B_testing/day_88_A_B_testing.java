import java.util.*;
import java.time.Instant;

/*
 * Enterprise A/B Testing and Experiment Governance.
 *
 * Java 17
 * No third-party dependencies.
 *
 * Domain components:
 * - Experiment configuration
 * - Randomization service
 * - Control and treatment groups
 * - Participant exposure records
 * - Conversion measurements
 * - Statistical evaluation
 * - Sample-size planning
 * - Guardrail policies
 * - Experiment lifecycle
 * - Immutable reporting
 */

public class ABTestingEnterprise {

    enum ExperimentState {
        DRAFT,
        RUNNING,
        COMPLETED,
        STOPPED
    }

    enum Group {
        CONTROL,
        TREATMENT
    }

    enum Decision {
        INCONCLUSIVE,
        TREATMENT_WINS,
        CONTROL_WINS,
        SIGNIFICANT_WITHOUT_PRACTICAL_WIN,
        INSUFFICIENT_SAMPLE
    }

    static class ExperimentException extends RuntimeException {
        ExperimentException(String message) {
            super(message);
        }
    }

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    record ExperimentConfig(
        String name,
        double controlRate,
        double treatmentRate,
        double allocationRatio,
        double alpha,
        double minimumEffect,
        int minimumGroupSize,
        long randomSeed
    ) {
        ExperimentConfig {
            if (name == null || name.isBlank()) {
                throw new ValidationException("Experiment name required.");
            }

            validateProbability(controlRate, "Control rate");
            validateProbability(treatmentRate, "Treatment rate");
            validateProbability(allocationRatio, "Allocation ratio");
            validateProbability(alpha, "Significance level");

            if (minimumEffect < 0 || minimumGroupSize < 1) {
                throw new ValidationException("Invalid experiment policy.");
            }
        }
    }

    record Participant(
        String participantId,
        Group group,
        Instant assignedAt
    ) {}

    record Outcome(
        String participantId,
        boolean converted,
        double revenue,
        Instant recordedAt
    ) {}

    record GroupMetrics(
        Group group,
        long participants,
        long conversions,
        double conversionRate,
        double averageRevenue
    ) {}

    record StatisticalResult(
        double absoluteLift,
        Double relativeLift,
        double zScore,
        double pValue,
        double confidenceLow,
        double confidenceHigh,
        boolean significant
    ) {}

    record ExperimentReport(
        String experimentName,
        ExperimentState state,
        GroupMetrics control,
        GroupMetrics treatment,
        StatisticalResult statistics,
        Decision decision,
        Instant generatedAt
    ) {}

    interface AssignmentPolicy {
        Group assign(String participantId);
    }

    static void validateProbability(double value, String name) {
        if (!Double.isFinite(value) || value <= 0 || value >= 1) {
            throw new ValidationException(
                name + " must be between zero and one."
            );
        }
    }

    static double normalCDF(double x) {
        return 0.5 * (1.0 + erf(x / Math.sqrt(2.0)));
    }

    // Numerical approximation to the error function.
    static double erf(double x) {
        double sign = x < 0 ? -1 : 1;
        x = Math.abs(x);

        double t = 1.0 / (1.0 + 0.3275911 * x);

        double polynomial =
            (((((1.061405429 * t - 1.453152027) * t)
            + 1.421413741) * t - 0.284496736) * t
            + 0.254829592) * t;

        return sign * (
            1.0 - polynomial * Math.exp(-x * x)
        );
    }

    static double inverseNormal(double p) {
        if (!(p > 0 && p < 1)) {
            throw new ValidationException("Invalid normal probability.");
        }

        double low = -8;
        double high = 8;

        for (int i = 0; i < 120; i++) {
            double mid = (low + high) / 2;

            if (normalCDF(mid) < p) {
                low = mid;
            } else {
                high = mid;
            }
        }

        return (low + high) / 2;
    }

    static int calculateRequiredSampleSize(
        double baseline,
        double effect,
        double alpha,
        double power
    ) {
        validateProbability(baseline, "Baseline rate");
        validateProbability(alpha, "Significance level");
        validateProbability(power, "Power");

        if (effect <= 0 || baseline + effect >= 1) {
            throw new ValidationException("Invalid detectable effect.");
        }

        double treatment = baseline + effect;
        double average = (baseline + treatment) / 2;

        double za = inverseNormal(1 - alpha / 2);
        double zb = inverseNormal(power);

        double numerator = Math.pow(
            za * Math.sqrt(2 * average * (1 - average))
            + zb * Math.sqrt(
                baseline * (1 - baseline)
                + treatment * (1 - treatment)
            ),
            2
        );

        return (int) Math.ceil(
            numerator / (effect * effect)
        );
    }

    static class RandomAssignmentPolicy implements AssignmentPolicy {

        private final double controlRatio;
        private final Random random;

        RandomAssignmentPolicy(double controlRatio, long seed) {
            validateProbability(controlRatio, "Control ratio");
            this.controlRatio = controlRatio;
            this.random = new Random(seed);
        }

        @Override
        public Group assign(String participantId) {
            Objects.requireNonNull(participantId);

            return random.nextDouble() < controlRatio
                ? Group.CONTROL
                : Group.TREATMENT;
        }
    }

    static class ExperimentService {

        private final ExperimentConfig config;
        private final AssignmentPolicy assignmentPolicy;

        private final Map<String, Participant> participants =
            new LinkedHashMap<>();

        private final Map<String, Outcome> outcomes =
            new HashMap<>();

        private ExperimentState state = ExperimentState.DRAFT;

        ExperimentService(
            ExperimentConfig config,
            AssignmentPolicy assignmentPolicy
        ) {
            this.config = Objects.requireNonNull(config);
            this.assignmentPolicy =
                Objects.requireNonNull(assignmentPolicy);
        }

        public synchronized void start() {
            if (state != ExperimentState.DRAFT) {
                throw new ExperimentException(
                    "Invalid experiment start transition."
                );
            }

            state = ExperimentState.RUNNING;
        }

        public synchronized Participant assign(String participantId) {
            requireRunning();

            if (participantId == null || participantId.isBlank()) {
                throw new ValidationException(
                    "Participant ID is required."
                );
            }

            if (participants.containsKey(participantId)) {
                throw new ExperimentException(
                    "Participant already assigned."
                );
            }

            Group group = assignmentPolicy.assign(participantId);

            Participant participant = new Participant(
                participantId,
                group,
                Instant.now()
            );

            participants.put(participantId, participant);

            return participant;
        }

        public synchronized void recordOutcome(
            String participantId,
            boolean converted,
            double revenue
        ) {
            requireRunning();

            if (!participants.containsKey(participantId)) {
                throw new ExperimentException(
                    "Participant has no experiment assignment."
                );
            }

            if (outcomes.containsKey(participantId)) {
                throw new ExperimentException(
                    "Duplicate outcome measurement."
                );
            }

            if (!Double.isFinite(revenue) || revenue < 0) {
                throw new ValidationException(
                    "Revenue must be finite and non-negative."
                );
            }

            if (converted && revenue == 0) {
                throw new ValidationException(
                    "Converted participants require positive revenue."
                );
            }

            outcomes.put(
                participantId,
                new Outcome(
                    participantId,
                    converted,
                    revenue,
                    Instant.now()
                )
            );
        }

        private void requireRunning() {
            if (state != ExperimentState.RUNNING) {
                throw new ExperimentException(
                    "Experiment is not running."
                );
            }
        }

        private GroupMetrics calculateGroup(Group group) {
            long total = 0;
            long conversions = 0;
            double revenue = 0;

            for (Outcome outcome : outcomes.values()) {
                Participant participant =
                    participants.get(outcome.participantId());

                if (participant.group() != group) {
                    continue;
                }

                total++;

                if (outcome.converted()) {
                    conversions++;
                }

                revenue += outcome.revenue();
            }

            if (total == 0) {
                throw new ExperimentException(
                    "Group has no recorded observations: " + group
                );
            }

            return new GroupMetrics(
                group,
                total,
                conversions,
                (double) conversions / total,
                revenue / total
            );
        }

        private StatisticalResult calculateStatistics(
            GroupMetrics control,
            GroupMetrics treatment
        ) {
            double p1 = control.conversionRate();
            double p2 = treatment.conversionRate();

            double pooled =
                (control.conversions() + treatment.conversions())
                / (double) (
                    control.participants() +
                    treatment.participants()
                );

            double standardError = Math.sqrt(
                pooled * (1 - pooled) *
                (
                    1.0 / control.participants()
                    + 1.0 / treatment.participants()
                )
            );

            double z = standardError == 0
                ? 0
                : (p2 - p1) / standardError;

            double pValue = standardError == 0
                ? 1
                : 2 * (1 - normalCDF(Math.abs(z)));

            double difference = p2 - p1;

            double unpooledSE = Math.sqrt(
                p1 * (1 - p1) / control.participants()
                + p2 * (1 - p2) / treatment.participants()
            );

            double critical = inverseNormal(
                1 - config.alpha() / 2
            );

            return new StatisticalResult(
                difference,
                p1 == 0 ? null : difference / p1,
                z,
                pValue,
                difference - critical * unpooledSE,
                difference + critical * unpooledSE,
                pValue < config.alpha()
            );
        }

        public synchronized ExperimentReport evaluate() {
            if (state == ExperimentState.DRAFT) {
                throw new ExperimentException(
                    "Experiment has not started."
                );
            }

            GroupMetrics control = calculateGroup(Group.CONTROL);
            GroupMetrics treatment = calculateGroup(Group.TREATMENT);

            StatisticalResult statistics =
                calculateStatistics(control, treatment);

            Decision decision;

            if (
                control.participants() < config.minimumGroupSize()
                || treatment.participants() < config.minimumGroupSize()
            ) {
                decision = Decision.INSUFFICIENT_SAMPLE;
            } else if (!statistics.significant()) {
                decision = Decision.INCONCLUSIVE;
            } else if (
                statistics.absoluteLift() > 0
                && statistics.absoluteLift() >= config.minimumEffect()
            ) {
                decision = Decision.TREATMENT_WINS;
            } else if (statistics.absoluteLift() < 0) {
                decision = Decision.CONTROL_WINS;
            } else {
                decision = Decision.SIGNIFICANT_WITHOUT_PRACTICAL_WIN;
            }

            return new ExperimentReport(
                config.name(),
                state,
                control,
                treatment,
                statistics,
                decision,
                Instant.now()
            );
        }

        public synchronized void complete() {
            requireRunning();
            state = ExperimentState.COMPLETED;
        }

        public synchronized void stop() {
            requireRunning();
            state = ExperimentState.STOPPED;
        }

        public synchronized ExperimentState getState() {
            return state;
        }

        public synchronized int participantCount() {
            return participants.size();
        }
    }

    static void runTests() {
        double cdf = normalCDF(0);

        if (Math.abs(cdf - 0.5) > 0.0001) {
            throw new AssertionError("Normal CDF validation failed.");
        }

        int sample = calculateRequiredSampleSize(
            0.10, 0.02, 0.05, 0.80
        );

        if (sample <= 0) {
            throw new AssertionError("Sample size must be positive.");
        }

        ExperimentConfig config = new ExperimentConfig(
            "Validation Experiment",
            0.10,
            0.12,
            0.50,
            0.05,
            0.01,
            1,
            42
        );

        ExperimentService service = new ExperimentService(
            config,
            new RandomAssignmentPolicy(0.50, 42)
        );

        service.start();
        service.assign("participant-1");

        try {
            service.assign("participant-1");
            throw new AssertionError("Duplicate assignment accepted.");
        } catch (ExperimentException expected) {
            // Expected.
        }

        System.out.println("All Java 17 tests passed.");
    }

    static void runDemo() {
        ExperimentConfig config = new ExperimentConfig(
            "Enterprise Checkout Conversion Experiment",
            0.10,
            0.12,
            0.50,
            0.05,
            0.01,
            100,
            2026
        );

        ExperimentService service = new ExperimentService(
            config,
            new RandomAssignmentPolicy(0.50, 2026)
        );

        service.start();

        Random outcomes = new Random(42);

        for (int i = 1; i <= 20000; i++) {
            String id = "customer-" + i;

            Participant participant = service.assign(id);

            double probability =
                participant.group() == Group.CONTROL
                ? 0.10
                : 0.12;

            boolean converted =
                outcomes.nextDouble() < probability;

            double revenue = converted
                ? 100 + outcomes.nextDouble() * 400
                : 0;

            service.recordOutcome(id, converted, revenue);
        }

        service.complete();

        ExperimentReport report = service.evaluate();

        System.out.println("\nENTERPRISE A/B TEST REPORT");
        System.out.println("Experiment: " + report.experimentName());
        System.out.println("State: " + report.state());

        System.out.println("\nCONTROL");
        System.out.println(report.control());

        System.out.println("\nTREATMENT");
        System.out.println(report.treatment());

        System.out.println("\nSTATISTICAL RESULTS");
        System.out.println(report.statistics());

        System.out.println("\nDECISION");
        System.out.println(report.decision());

        System.out.println("\nSAMPLE SIZE PLANNING");
        System.out.println(
            "Required participants per group: "
            + calculateRequiredSampleSize(
                0.10, 0.02, 0.05, 0.80
            )
        );
    }

    public static void main(String[] args) {
        try {
            runTests();
            runDemo();
        } catch (RuntimeException exception) {
            System.err.println(
                "Experiment execution failed: " +
                exception.getMessage()
            );

            System.exit(1);
        }
    }
}
