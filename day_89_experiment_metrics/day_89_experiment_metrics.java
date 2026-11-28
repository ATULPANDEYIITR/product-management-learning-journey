import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;

/**
 * Experiment Metrics Enterprise Governance System
 *
 * Java 17
 *
 * Models:
 * - Experiment lifecycle
 * - Primary metric ownership
 * - Secondary performance metrics
 * - Guardrail policies
 * - Statistical sample-size planning
 * - Stable traffic allocation
 * - Statistical evaluation
 * - Experiment approval decisions
 */

public class ExperimentMetrics {

    enum MetricType {
        PRIMARY,
        SECONDARY,
        GUARDRAIL
    }

    enum ExperimentStatus {
        DRAFT,
        RUNNING,
        COMPLETED,
        INVALID
    }

    enum Decision {
        SHIP,
        DO_NOT_SHIP,
        INCONCLUSIVE
    }

    static class ExperimentException extends RuntimeException {
        ExperimentException(String message) {
            super(message);
        }
    }

    record MetricDefinition(
        String name,
        MetricType type,
        String unit,
        boolean higherIsBetter
    ) {
        MetricDefinition {
            Objects.requireNonNull(name);
            Objects.requireNonNull(type);
            Objects.requireNonNull(unit);

            if (name.isBlank()) {
                throw new ExperimentException(
                    "Metric name cannot be empty"
                );
            }
        }
    }

    record ExperimentConfig(
        String id,
        String name,
        double baselineConversion,
        double relativeMDE,
        double alpha,
        double power
    ) {
        ExperimentConfig {
            if (id == null || id.isBlank() ||
                name == null || name.isBlank()) {
                throw new ExperimentException(
                    "Experiment identity is required"
                );
            }

            if (!(baselineConversion > 0 &&
                  baselineConversion < 1)) {
                throw new ExperimentException(
                    "Invalid baseline conversion"
                );
            }

            if (!(relativeMDE > 0 && relativeMDE < 1)) {
                throw new ExperimentException("Invalid MDE");
            }

            if (!(alpha > 0 && alpha < 1)) {
                throw new ExperimentException("Invalid alpha");
            }

            if (!(power > 0 && power < 1)) {
                throw new ExperimentException("Invalid power");
            }

            if (baselineConversion *
                (1 + relativeMDE) >= 1) {
                throw new ExperimentException(
                    "Treatment conversion exceeds 1"
                );
            }
        }
    }

    record EvaluationPolicy(
        double minimumConversionImprovement,
        double maximumRefundIncrease,
        double maximumP95LatencyIncrease,
        int minimumReviewsEquivalent
    ) {
        EvaluationPolicy {
            if (maximumRefundIncrease < 0 ||
                maximumP95LatencyIncrease < 0 ||
                minimumReviewsEquivalent < 0) {
                throw new ExperimentException(
                    "Invalid evaluation thresholds"
                );
            }
        }
    }

    record Observation(
        String userId,
        boolean converted,
        double revenue,
        boolean refunded,
        double latency
    ) {
        Observation {
            if (userId == null || userId.isBlank()) {
                throw new ExperimentException("Invalid user ID");
            }

            if (!Double.isFinite(revenue) ||
                !Double.isFinite(latency) ||
                revenue < 0 || latency <= 0) {
                throw new ExperimentException(
                    "Invalid observation values"
                );
            }

            if (!converted && (revenue > 0 || refunded)) {
                throw new ExperimentException(
                    "Conversion-dependent metrics require conversion"
                );
            }
        }
    }

    static final class ExperimentLifecycle {

        private ExperimentStatus status = ExperimentStatus.DRAFT;

        private static final Map<ExperimentStatus,
            List<ExperimentStatus>> TRANSITIONS = Map.of(
                ExperimentStatus.DRAFT,
                List.of(
                    ExperimentStatus.RUNNING,
                    ExperimentStatus.INVALID
                ),

                ExperimentStatus.RUNNING,
                List.of(
                    ExperimentStatus.COMPLETED,
                    ExperimentStatus.INVALID
                ),

                ExperimentStatus.COMPLETED,
                List.of(),

                ExperimentStatus.INVALID,
                List.of()
            );

        public void transition(ExperimentStatus next) {
            if (!TRANSITIONS.get(status).contains(next)) {
                throw new ExperimentException(
                    "Invalid lifecycle transition: " +
                    status + " -> " + next
                );
            }

            status = next;
        }

        public ExperimentStatus status() {
            return status;
        }
    }

    static final class MetricRegistry {

        private final Map<String, MetricDefinition> metrics =
            new HashMap<>();

        public void register(MetricDefinition metric) {
            if (metrics.putIfAbsent(metric.name(), metric) != null) {
                throw new ExperimentException(
                    "Duplicate metric: " + metric.name()
                );
            }
        }

        public List<MetricDefinition> getByType(MetricType type) {
            return metrics.values()
                .stream()
                .filter(metric -> metric.type() == type)
                .sorted((a, b) -> a.name().compareTo(b.name()))
                .toList();
        }

        public MetricDefinition get(String name) {
            MetricDefinition metric = metrics.get(name);

            if (metric == null) {
                throw new ExperimentException(
                    "Metric not registered: " + name
                );
            }

            return metric;
        }
    }

    static final class TrafficAllocator {

        private final String experimentId;

        TrafficAllocator(String experimentId) {
            this.experimentId = experimentId;
        }

        public String assign(String userId) {
            if (userId == null || userId.isBlank()) {
                throw new ExperimentException("Invalid user ID");
            }

            try {
                MessageDigest digest =
                    MessageDigest.getInstance("SHA-256");

                byte[] result = digest.digest(
                    (experimentId + ":" + userId)
                        .getBytes(java.nio.charset.StandardCharsets.UTF_8)
                );

                return (result[0] & 1) == 0
                    ? "control"
                    : "treatment";

            } catch (NoSuchAlgorithmException exception) {
                throw new ExperimentException(
                    "SHA-256 unavailable"
                );
            }
        }
    }

    static final class SampleSizeCalculator {

        private static double inverseNormal(double p) {
            if (!(p > 0 && p < 1)) {
                throw new ExperimentException(
                    "Invalid probability"
                );
            }

            double[] a = {
                -39.6968302866538, 220.946098424521,
                -275.928510446969, 138.357751867269,
                -30.6647980661472, 2.50662827745924
            };

            double[] b = {
                -54.4760987982241, 161.585836858041,
                -155.698979859887, 66.8013118877197,
                -13.2806815528857
            };

            double[] c = {
                -0.00778489400243029, -0.322396458041136,
                -2.40075827716184, -2.54973253934373,
                4.37466414146497, 2.93816398269878
            };

            double[] d = {
                0.00778469570904146, 0.32246712907004,
                2.445134137143, 3.75440866190742
            };

            if (p < 0.02425) {
                double q = Math.sqrt(-2 * Math.log(p));

                return (((((c[0] * q + c[1]) * q + c[2]) * q +
                    c[3]) * q + c[4]) * q + c[5]) /
                    ((((d[0] * q + d[1]) * q + d[2]) * q +
                        d[3]) * q + 1);
            }

            if (p > 0.97575) {
                return -inverseNormal(1 - p);
            }

            double q = p - 0.5;
            double r = q * q;

            return (((((a[0] * r + a[1]) * r + a[2]) * r +
                a[3]) * r + a[4]) * r + a[5]) * q /
                (((((b[0] * r + b[1]) * r + b[2]) * r +
                    b[3]) * r + b[4]) * r) + 1);
        }

        public static int calculate(ExperimentConfig config) {
            double p1 = config.baselineConversion();
            double p2 = p1 * (1 + config.relativeMDE());

            double pooled = (p1 + p2) / 2;
            double difference = p2 - p1;

            double zAlpha = inverseNormal(
                1 - config.alpha() / 2
            );

            double zPower = inverseNormal(config.power());

            double numerator = Math.pow(
                zAlpha * Math.sqrt(
                    2 * pooled * (1 - pooled)
                ) +
                zPower * Math.sqrt(
                    p1 * (1 - p1) + p2 * (1 - p2)
                ),
                2
            );

            return (int) Math.ceil(
                numerator / (difference * difference)
            );
        }
    }

    static final class ExperimentGroup {

        private final String name;
        private final List<Observation> observations =
            new ArrayList<>();

        ExperimentGroup(String name) {
            this.name = name;
        }

        public void add(Observation observation) {
            observations.add(observation);
        }

        public int users() {
            return observations.size();
        }

        public int conversions() {
            return (int) observations.stream()
                .filter(Observation::converted)
                .count();
        }

        public int refunds() {
            return (int) observations.stream()
                .filter(Observation::refunded)
                .count();
        }

        public double conversionRate() {
            if (users() == 0) {
                throw new ExperimentException("Empty group");
            }

            return (double) conversions() / users();
        }

        public double refundRate() {
            return conversions() == 0
                ? 0
                : (double) refunds() / conversions();
        }

        public List<Double> revenue() {
            return observations.stream()
                .filter(Observation::converted)
                .map(Observation::revenue)
                .toList();
        }

        public List<Double> latency() {
            return observations.stream()
                .map(Observation::latency)
                .toList();
        }

        public String name() {
            return name;
        }
    }

    static final class Simulator {

        private final ExperimentConfig config;
        private final TrafficAllocator allocator;
        private final Random random;

        Simulator(ExperimentConfig config, long seed) {
            this.config = config;
            this.allocator = new TrafficAllocator(config.id());
            this.random = new Random(seed);
        }

        private double gaussian() {
            return random.nextGaussian();
        }

        public Map<String, ExperimentGroup> generate(int totalUsers) {
            if (totalUsers < 2) {
                throw new ExperimentException(
                    "At least two users are required"
                );
            }

            Map<String, ExperimentGroup> groups =
                new HashMap<>();

            groups.put("control", new ExperimentGroup("control"));
            groups.put("treatment", new ExperimentGroup("treatment"));

            for (int i = 0; i < totalUsers; i++) {
                String userId = "user-" + i;
                String variant = allocator.assign(userId);

                ExperimentGroup group = groups.get(variant);

                double probability = variant.equals("control")
                    ? config.baselineConversion()
                    : config.baselineConversion() *
                        (1 + config.relativeMDE());

                boolean converted = random.nextDouble() < probability;

                double revenue = converted
                    ? Math.exp(3.5 + gaussian() * 0.6)
                    : 0;

                boolean refunded = converted &&
                    random.nextDouble() < 0.035;

                double baseLatency = variant.equals("control")
                    ? 180
                    : 190;

                double latency = Math.max(
                    1,
                    baseLatency + gaussian() * 25
                );

                group.add(new Observation(
                    userId,
                    converted,
                    revenue,
                    refunded,
                    latency
                ));
            }

            return Collections.unmodifiableMap(groups);
        }
    }

    static final class StatisticalAnalyzer {

        static double normalCDF(double z) {
            return 0.5 * erfc(-z / Math.sqrt(2));
        }

        private static double erfc(double x) {
            double z = Math.abs(x);
            double t = 1.0 / (1.0 + 0.5 * z);

            double answer = t * Math.exp(
                -z * z - 1.26551223 +
                t * (1.00002368 +
                t * (0.37409196 +
                t * (0.09678418 +
                t * (-0.18628806 +
                t * (0.27886807 +
                t * (-1.13520398 +
                t * (1.48851587 +
                t * (-0.82215223 +
                t * 0.17087277))))))))
            );

            return x >= 0 ? answer : 2 - answer;
        }

        static double proportionPValue(
            ExperimentGroup control,
            ExperimentGroup treatment
        ) {
            double p1 = control.conversionRate();
            double p2 = treatment.conversionRate();

            double pooled = (double) (
                control.conversions() + treatment.conversions()
            ) / (control.users() + treatment.users());

            double se = Math.sqrt(
                pooled * (1 - pooled) *
                (1.0 / control.users() +
                 1.0 / treatment.users())
            );

            if (se == 0) {
                return p1 == p2 ? 1 : 0;
            }

            double z = (p2 - p1) / se;

            return 2 * (1 - normalCDF(Math.abs(z)));
        }

        static double mean(List<Double> values) {
            if (values.isEmpty()) {
                return 0;
            }

            return values.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElse(0);
        }

        static double percentile(
            List<Double> values,
            double fraction
        ) {
            if (values.isEmpty()) {
                throw new ExperimentException(
                    "Cannot calculate percentile of empty data"
                );
            }

            List<Double> sorted = values.stream()
                .sorted()
                .toList();

            double position = fraction * (sorted.size() - 1);

            int lower = (int) Math.floor(position);
            int upper = (int) Math.ceil(position);

            return sorted.get(lower) +
                (sorted.get(upper) - sorted.get(lower)) *
                (position - lower);
        }

        static double welchNormalPValue(
            List<Double> a,
            List<Double> b
        ) {
            if (a.size() < 2 || b.size() < 2) {
                return Double.NaN;
            }

            double meanA = mean(a);
            double meanB = mean(b);

            double varA = variance(a);
            double varB = variance(b);

            double se = Math.sqrt(
                varA / a.size() + varB / b.size()
            );

            if (se == 0) {
                return meanA == meanB ? 1 : 0;
            }

            double z = (meanB - meanA) / se;

            return 2 * (1 - normalCDF(Math.abs(z)));
        }

        private static double variance(List<Double> values) {
            double mean = mean(values);

            return values.stream()
                .mapToDouble(value -> Math.pow(value - mean, 2))
                .sum() / (values.size() - 1);
        }
    }

    record EvaluationReport(
        Decision decision,
        double controlConversion,
        double treatmentConversion,
        double pValue,
        double controlRevenue,
        double treatmentRevenue,
        double controlRefundRate,
        double treatmentRefundRate,
        double controlP95,
        double treatmentP95,
        boolean sampleSufficient,
        Map<String, Boolean> guardrails
    ) {}

    static final class EvaluationService {

        private final EvaluationPolicy policy;

        EvaluationService(EvaluationPolicy policy) {
            this.policy = policy;
        }

        public EvaluationReport evaluate(
            ExperimentGroup control,
            ExperimentGroup treatment,
            int requiredPerGroup,
            double alpha
        ) {
            double controlRate = control.conversionRate();
            double treatmentRate = treatment.conversionRate();

            double pValue =
                StatisticalAnalyzer.proportionPValue(
                    control, treatment
                );

            double controlRevenue =
                StatisticalAnalyzer.mean(control.revenue());

            double treatmentRevenue =
                StatisticalAnalyzer.mean(treatment.revenue());

            double controlRefund = control.refundRate();
            double treatmentRefund = treatment.refundRate();

            double controlP95 =
                StatisticalAnalyzer.percentile(
                    control.latency(), 0.95
                );

            double treatmentP95 =
                StatisticalAnalyzer.percentile(
                    treatment.latency(), 0.95
                );

            boolean sufficient =
                control.users() >= requiredPerGroup &&
                treatment.users() >= requiredPerGroup;

            Map<String, Boolean> guardrails = new HashMap<>();

            guardrails.put(
                "refund_rate",
                treatmentRefund - controlRefund <=
                    policy.maximumRefundIncrease()
            );

            guardrails.put(
                "p95_latency",
                treatmentP95 - controlP95 <=
                    policy.maximumP95LatencyIncrease()
            );

            boolean guardrailsPass =
                guardrails.values().stream().allMatch(Boolean::booleanValue);

            Decision decision;

            if (!sufficient) {
                decision = Decision.INCONCLUSIVE;
            } else if (!guardrailsPass) {
                decision = Decision.DO_NOT_SHIP;
            } else if (
                pValue < alpha &&
                treatmentRate - controlRate >
                    policy.minimumConversionImprovement()
            ) {
                decision = Decision.SHIP;
            } else {
                decision = Decision.INCONCLUSIVE;
            }

            return new EvaluationReport(
                decision,
                controlRate,
                treatmentRate,
                pValue,
                controlRevenue,
                treatmentRevenue,
                controlRefund,
                treatmentRefund,
                controlP95,
                treatmentP95,
                sufficient,
                Map.copyOf(guardrails)
            );
        }
    }

    public static void main(String[] args) {

        try {
            ExperimentConfig config = new ExperimentConfig(
                "EXP-001",
                "Checkout Redesign",
                0.10,
                0.10,
                0.05,
                0.80
            );

            MetricRegistry registry = new MetricRegistry();

            registry.register(new MetricDefinition(
                "conversion_rate",
                MetricType.PRIMARY,
                "percentage",
                true
            ));

            registry.register(new MetricDefinition(
                "revenue_per_conversion",
                MetricType.SECONDARY,
                "currency",
                true
            ));

            registry.register(new MetricDefinition(
                "refund_rate",
                MetricType.GUARDRAIL,
                "percentage",
                false
            ));

            registry.register(new MetricDefinition(
                "p95_latency",
                MetricType.GUARDRAIL,
                "milliseconds",
                false
            ));

            int required =
                SampleSizeCalculator.calculate(config);

            System.out.println("EXPERIMENT CONFIGURATION");
            System.out.println("-----------------------");
            System.out.println("Name: " + config.name());
            System.out.println("Required sample per group: " + required);

            System.out.println(
                "Primary metrics: " +
                registry.getByType(MetricType.PRIMARY).size()
            );

            System.out.println(
                "Secondary metrics: " +
                registry.getByType(MetricType.SECONDARY).size()
            );

            System.out.println(
                "Guardrails: " +
                registry.getByType(MetricType.GUARDRAIL).size()
            );

            ExperimentLifecycle lifecycle =
                new ExperimentLifecycle();

            lifecycle.transition(ExperimentStatus.RUNNING);

            Simulator simulator = new Simulator(config, 42);

            Map<String, ExperimentGroup> groups =
                simulator.generate(required * 2);

            EvaluationPolicy policy = new EvaluationPolicy(
                0,
                0.02,
                40,
                0
            );

            EvaluationService evaluator =
                new EvaluationService(policy);

            EvaluationReport report = evaluator.evaluate(
                groups.get("control"),
                groups.get("treatment"),
                required,
                config.alpha()
            );

            System.out.println("\nEVALUATION RESULTS");
            System.out.println("------------------");

            System.out.printf(
                "Control conversion: %.4f%%%n",
                report.controlConversion() * 100
            );

            System.out.printf(
                "Treatment conversion: %.4f%%%n",
                report.treatmentConversion() * 100
            );

            System.out.printf(
                "Absolute change: %.4f percentage points%n",
                (report.treatmentConversion() -
                    report.controlConversion()) * 100
            );

            System.out.printf(
                "P-value: %.6f%n",
                report.pValue()
            );

            System.out.println("\nSECONDARY METRIC");

            System.out.printf(
                "Control revenue per conversion: %.2f%n",
                report.controlRevenue()
            );

            System.out.printf(
                "Treatment revenue per conversion: %.2f%n",
                report.treatmentRevenue()
            );

            System.out.println("\nGUARDRAILS");

            report.guardrails().forEach(
                (name, passed) ->
                    System.out.println(
                        name + ": " + (passed ? "PASS" : "FAIL")
                    )
            );

            System.out.println("\nFINAL DECISION");
            System.out.println(report.decision());

            lifecycle.transition(ExperimentStatus.COMPLETED);

            System.out.println(
                "Lifecycle: " + lifecycle.status()
            );

        } catch (ExperimentException exception) {
            System.err.println(
                "Experiment validation error: " +
                exception.getMessage()
            );

            System.exit(1);
        }
    }
}
