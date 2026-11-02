import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.EnumSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

public class ProductMissionGovernance {

    enum MissionType {
        ORGANIZATIONAL,
        PRODUCT
    }

    enum MissionStatus {
        DRAFT,
        ACTIVE,
        RETIRED
    }

    enum MissionDecision {
        ALIGNED,
        MISALIGNED,
        INVALID
    }

    static final class MissionValidationException extends Exception {
        MissionValidationException(String message) {
            super(message);
        }
    }

    record Mission(
        String name,
        String statement,
        String purpose,
        MissionType type,
        MissionStatus status,
        Set<String> strategicThemes
    ) {
        Mission {
            Objects.requireNonNull(name, "name");
            Objects.requireNonNull(statement, "statement");
            Objects.requireNonNull(purpose, "purpose");
            Objects.requireNonNull(type, "type");
            Objects.requireNonNull(status, "status");
            Objects.requireNonNull(strategicThemes, "strategicThemes");

            strategicThemes = Collections.unmodifiableSet(
                new LinkedHashSet<>(strategicThemes)
            );
        }

        void validate() throws MissionValidationException {
            if (name.isBlank()) {
                throw new MissionValidationException(
                    "Mission name cannot be empty."
                );
            }

            if (statement.isBlank()) {
                throw new MissionValidationException(
                    "Mission statement cannot be empty."
                );
            }

            if (purpose.isBlank()) {
                throw new MissionValidationException(
                    "Mission purpose cannot be empty."
                );
            }

            if (statement.length() > 300) {
                throw new MissionValidationException(
                    "Mission statement exceeds 300 characters."
                );
            }

            if (strategicThemes.isEmpty()) {
                throw new MissionValidationException(
                    "Mission requires at least one strategic theme."
                );
            }
        }
    }

    interface MissionPolicy {
        MissionDecision evaluate(
            Mission organizationalMission,
            Mission productMission
        ) throws MissionValidationException;
    }

    static final class StrategicAlignmentPolicy
        implements MissionPolicy {

        @Override
        public MissionDecision evaluate(
            Mission organizationalMission,
            Mission productMission
        ) throws MissionValidationException {

            organizationalMission.validate();
            productMission.validate();

            if (organizationalMission.type()
                != MissionType.ORGANIZATIONAL) {

                throw new MissionValidationException(
                    "Parent mission must be organizational."
                );
            }

            if (productMission.type() != MissionType.PRODUCT) {
                throw new MissionValidationException(
                    "Product mission must be product-specific."
                );
            }

            Set<String> sharedThemes =
                new LinkedHashSet<>(organizationalMission.strategicThemes());

            sharedThemes.retainAll(productMission.strategicThemes());

            return sharedThemes.isEmpty()
                ? MissionDecision.MISALIGNED
                : MissionDecision.ALIGNED;
        }
    }

    static final class ProductMissionService {
        private final MissionPolicy policy;

        ProductMissionService(MissionPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        MissionDecision assess(
            Mission organization,
            Mission product
        ) throws MissionValidationException {
            return policy.evaluate(organization, product);
        }

        Set<String> sharedThemes(
            Mission organization,
            Mission product
        ) {
            Set<String> shared =
                new LinkedHashSet<>(organization.strategicThemes());

            shared.retainAll(product.strategicThemes());

            return shared;
        }

        double purposeClarity(Mission mission) {
            Set<String> statementWords =
                tokenize(mission.statement());

            Set<String> purposeWords =
                tokenize(mission.purpose());

            if (statementWords.isEmpty() || purposeWords.isEmpty()) {
                return 0.0;
            }

            Set<String> intersection =
                new LinkedHashSet<>(statementWords);

            intersection.retainAll(purposeWords);

            int denominator = Math.max(
                statementWords.size(),
                purposeWords.size()
            );

            return intersection.size() * 100.0 / denominator;
        }

        private Set<String> tokenize(String text) {
            return java.util.Arrays.stream(
                    text.toLowerCase()
                        .replaceAll("[^a-z0-9 ]", " ")
                        .split("\\s+")
                )
                .filter(word -> word.length() > 3)
                .collect(Collectors.toCollection(LinkedHashSet::new));
        }
    }

    static final class MetricRegistry<T extends Number> {
        private final Map<String, T> metrics = new LinkedHashMap<>();

        void put(String name, T value) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Metric name cannot be empty."
                );
            }

            metrics.put(name, Objects.requireNonNull(value));
        }

        Map<String, T> values() {
            return Collections.unmodifiableMap(metrics);
        }
    }

    record Product(
        String name,
        Mission organizationalMission,
        Mission productMission,
        MetricRegistry<Double> metrics
    ) {}

    static void writeAudit(
        Path path,
        Product product,
        ProductMissionService service,
        MissionDecision decision
    ) throws IOException {

        Set<String> themes = service.sharedThemes(
            product.organizationalMission(),
            product.productMission()
        );

        double clarity =
            service.purposeClarity(product.productMission());

        String content = """
            Product Mission Audit
            =====================
            Product: %s
            Decision: %s
            Organizational Mission: %s
            Product Mission: %s
            Shared Strategic Themes: %s
            Purpose Clarity: %.2f%%
            Metrics: %d
            """.formatted(
                product.name(),
                decision,
                product.organizationalMission().statement(),
                product.productMission().statement(),
                String.join(", ", themes),
                clarity,
                product.metrics().values().size()
            );

        Files.writeString(path, content);
    }

    public static void main(String[] args) {
        try {
            Mission organization = new Mission(
                "Acme Organizational Mission",
                "Improve access to trustworthy digital services by making "
                    + "essential customer interactions simpler and more "
                    + "reliable.",
                "Deliver dependable services that solve important customer "
                    + "problems.",
                MissionType.ORGANIZATIONAL,
                MissionStatus.ACTIVE,
                Set.of(
                    "customer trust",
                    "simplicity",
                    "reliability"
                )
            );

            Mission productMission = new Mission(
                "Payments Product Mission",
                "Enable customers to complete everyday payments quickly, "
                    + "clearly, and reliably.",
                "Reduce friction in everyday transactions while preserving "
                    + "customer trust and reliability.",
                MissionType.PRODUCT,
                MissionStatus.ACTIVE,
                Set.of(
                    "customer trust",
                    "simplicity",
                    "reliability"
                )
            );

            MetricRegistry<Double> metrics = new MetricRegistry<>();
            metrics.put("successful_transaction_rate", 99.2);
            metrics.put("payment_completion_time_seconds", 18.5);
            metrics.put("customer_satisfaction", 91.4);

            Product product = new Product(
                "Acme Pay",
                organization,
                productMission,
                metrics
            );

            MissionPolicy policy =
                new StrategicAlignmentPolicy();

            ProductMissionService service =
                new ProductMissionService(policy);

            MissionDecision decision = service.assess(
                organization,
                productMission
            );

            System.out.println(
                "PRODUCT MISSION GOVERNANCE"
            );
            System.out.println(
                "=========================="
            );
            System.out.println(
                "Product: " + product.name()
            );
            System.out.println(
                "Decision: " + decision
            );
            System.out.println(
                "Shared themes: "
                    + String.join(
                        ", ",
                        service.sharedThemes(
                            organization,
                            productMission
                        )
                    )
            );
            System.out.printf(
                "Purpose clarity: %.2f%%%n",
                service.purposeClarity(productMission)
            );

            Path auditPath =
                Path.of("product-mission-audit.txt");

            writeAudit(
                auditPath,
                product,
                service,
                decision
            );

            System.out.println(
                "Audit written to " + auditPath.toAbsolutePath()
            );

            try {
                Mission invalid = new Mission(
                    "Invalid Mission",
                    "",
                    "",
                    MissionType.PRODUCT,
                    MissionStatus.DRAFT,
                    Set.of("reliability")
                );

                invalid.validate();
            } catch (MissionValidationException error) {
                System.out.println(
                    "Validation failure handled: "
                        + error.getMessage()
                );
            }

        } catch (MissionValidationException | IOException error) {
            System.err.println(
                "Execution failed: " + error.getMessage()
            );
            System.exit(1);
        }
    }
}
