import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Enterprise Kano Model implementation.
 *
 * Models customer requirements, questionnaire responses,
 * feature classification, satisfaction coefficients,
 * and product prioritization.
 */
public class KanoEnterprise {

    enum Response {
        LIKE,
        EXPECT,
        NEUTRAL,
        TOLERATE,
        DISLIKE
    }

    enum Category {
        MUST_BE,
        PERFORMANCE,
        ATTRACTIVE,
        INDIFFERENT,
        REVERSE,
        QUESTIONABLE
    }

    enum FeatureStatus {
        PROPOSED,
        UNDER_RESEARCH,
        APPROVED,
        IN_DEVELOPMENT,
        RELEASED,
        REJECTED
    }

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    record CustomerResponse(
        String customerId,
        Response functional,
        Response dysfunctional
    ) {
        CustomerResponse {
            if (customerId == null || customerId.isBlank()) {
                throw new ValidationException("Invalid customer ID.");
            }

            if (functional == null || dysfunctional == null) {
                throw new ValidationException(
                    "Both questionnaire responses are required."
                );
            }
        }

        Category classify() {
            return evaluate(functional, dysfunctional);
        }
    }

    record Coefficients(
        double satisfaction,
        double dissatisfaction
    ) {}

    record Analysis(
        String featureId,
        String featureName,
        Category classification,
        int responseCount,
        Coefficients coefficients,
        double questionableRate
    ) {}

    /*
     * The matrix is indexed by enum ordinal:
     * functional response first, dysfunctional response second.
     */
    private static final Category[][] MATRIX = {
        {
            Category.QUESTIONABLE,
            Category.REVERSE,
            Category.REVERSE,
            Category.REVERSE,
            Category.MUST_BE
        },
        {
            Category.ATTRACTIVE,
            Category.INDIFFERENT,
            Category.INDIFFERENT,
            Category.INDIFFERENT,
            Category.MUST_BE
        },
        {
            Category.PERFORMANCE,
            Category.INDIFFERENT,
            Category.INDIFFERENT,
            Category.INDIFFERENT,
            Category.MUST_BE
        },
        {
            Category.PERFORMANCE,
            Category.INDIFFERENT,
            Category.INDIFFERENT,
            Category.INDIFFERENT,
            Category.MUST_BE
        },
        {
            Category.PERFORMANCE,
            Category.PERFORMANCE,
            Category.PERFORMANCE,
            Category.PERFORMANCE,
            Category.QUESTIONABLE
        }
    };

    static Category evaluate(
        Response functional,
        Response dysfunctional
    ) {
        return MATRIX[functional.ordinal()][dysfunctional.ordinal()];
    }

    static class KanoFeature {
        private final String id;
        private final String name;
        private final String description;

        private FeatureStatus status = FeatureStatus.PROPOSED;

        private final Map<String, CustomerResponse> responses =
            new HashMap<>();

        KanoFeature(String id, String name, String description) {
            if (id == null || id.isBlank() ||
                name == null || name.isBlank()) {
                throw new ValidationException(
                    "Feature ID and name are mandatory."
                );
            }

            this.id = id;
            this.name = name;
            this.description = description;
        }

        void addResponse(CustomerResponse response) {
            if (responses.putIfAbsent(
                response.customerId(),
                response
            ) != null) {
                throw new ValidationException(
                    "Duplicate customer response: " +
                    response.customerId()
                );
            }
        }

        EnumMap<Category, Integer> counts() {
            EnumMap<Category, Integer> result =
                new EnumMap<>(Category.class);

            for (Category category : Category.values()) {
                result.put(category, 0);
            }

            for (CustomerResponse response : responses.values()) {
                result.merge(response.classify(), 1, Integer::sum);
            }

            return result;
        }

        Category dominantCategory() {
            if (responses.isEmpty()) {
                throw new ValidationException(
                    "Feature has no customer responses."
                );
            }

            EnumMap<Category, Integer> counts = counts();

            List<Category> validCategories = List.of(
                Category.MUST_BE,
                Category.PERFORMANCE,
                Category.ATTRACTIVE,
                Category.INDIFFERENT,
                Category.REVERSE
            );

            Category best = Category.QUESTIONABLE;
            int maximum = 0;

            for (Category category : validCategories) {
                int count = counts.get(category);

                if (count > maximum) {
                    maximum = count;
                    best = category;
                }
            }

            return best;
        }

        Coefficients calculateCoefficients() {
            EnumMap<Category, Integer> counts = counts();

            int attractive = counts.get(Category.ATTRACTIVE);
            int performance = counts.get(Category.PERFORMANCE);
            int mustBe = counts.get(Category.MUST_BE);
            int indifferent = counts.get(Category.INDIFFERENT);

            int denominator =
                attractive + performance + mustBe + indifferent;

            if (denominator == 0) {
                return new Coefficients(0.0, 0.0);
            }

            double satisfaction =
                (double) (attractive + performance) / denominator;

            double dissatisfaction =
                -(double) (performance + mustBe) / denominator;

            return new Coefficients(
                satisfaction,
                dissatisfaction
            );
        }

        double questionableRate() {
            if (responses.isEmpty()) {
                return 0.0;
            }

            return (double) counts().get(Category.QUESTIONABLE)
                / responses.size();
        }

        void transitionTo(FeatureStatus newStatus) {
            Map<FeatureStatus, Set<FeatureStatus>> allowed =
                Map.of(
                    FeatureStatus.PROPOSED,
                    Set.of(
                        FeatureStatus.UNDER_RESEARCH,
                        FeatureStatus.REJECTED
                    ),
                    FeatureStatus.UNDER_RESEARCH,
                    Set.of(
                        FeatureStatus.APPROVED,
                        FeatureStatus.REJECTED
                    ),
                    FeatureStatus.APPROVED,
                    Set.of(
                        FeatureStatus.IN_DEVELOPMENT,
                        FeatureStatus.REJECTED
                    ),
                    FeatureStatus.IN_DEVELOPMENT,
                    Set.of(FeatureStatus.RELEASED),
                    FeatureStatus.RELEASED,
                    Set.of(),
                    FeatureStatus.REJECTED,
                    Set.of()
                );

            if (!allowed.get(status).contains(newStatus)) {
                throw new ValidationException(
                    "Invalid feature status transition: " +
                    status + " -> " + newStatus
                );
            }

            status = newStatus;
        }

        String id() {
            return id;
        }

        String name() {
            return name;
        }

        FeatureStatus status() {
            return status;
        }

        int responseCount() {
            return responses.size();
        }
    }

    static class KanoService {
        private final Map<String, KanoFeature> features =
            new HashMap<>();

        void register(KanoFeature feature) {
            if (features.putIfAbsent(
                feature.id(),
                feature
            ) != null) {
                throw new ValidationException(
                    "Feature already exists."
                );
            }
        }

        void recordResponse(
            String featureId,
            CustomerResponse response
        ) {
            KanoFeature feature = features.get(featureId);

            if (feature == null) {
                throw new ValidationException(
                    "Unknown feature ID: " + featureId
                );
            }

            feature.addResponse(response);
        }

        List<Analysis> analyze() {
            return features.values()
                .stream()
                .filter(feature -> feature.responseCount() > 0)
                .map(feature -> new Analysis(
                    feature.id(),
                    feature.name(),
                    feature.dominantCategory(),
                    feature.responseCount(),
                    feature.calculateCoefficients(),
                    feature.questionableRate()
                ))
                .sorted(
                    Comparator.comparingDouble(
                        analysis ->
                            analysis.coefficients().dissatisfaction()
                    )
                )
                .toList();
        }

        void printReport() {
            System.out.println(
                "\nENTERPRISE KANO CUSTOMER ANALYSIS"
            );

            System.out.printf(
                "%-23s %-17s %-13s %-16s %-12s%n",
                "Feature",
                "Classification",
                "Satisfaction",
                "Dissatisfaction",
                "Questionable"
            );

            for (Analysis analysis : analyze()) {
                System.out.printf(
                    "%-23s %-17s %-13.3f %-16.3f %-12.3f%n",
                    analysis.featureName(),
                    analysis.classification(),
                    analysis.coefficients().satisfaction(),
                    analysis.coefficients().dissatisfaction(),
                    analysis.questionableRate()
                );
            }
        }
    }

    public static void main(String[] args) {
        try {
            KanoService service = new KanoService();

            service.register(new KanoFeature(
                "F001", "Account Security",
                "Secure authentication and protection."
            ));

            service.register(new KanoFeature(
                "F002", "Application Speed",
                "Fast processing and response."
            ));

            service.register(new KanoFeature(
                "F003", "AI Recommendations",
                "Personalized suggestions."
            ));

            service.register(new KanoFeature(
                "F004", "Custom Dashboard",
                "User-configurable dashboard."
            ));

            Map<String, List<CustomerResponse>> dataset =
                new HashMap<>();

            dataset.put("F001", List.of(
                new CustomerResponse("C001", Response.LIKE, Response.DISLIKE),
                new CustomerResponse("C002", Response.EXPECT, Response.DISLIKE),
                new CustomerResponse("C003", Response.LIKE, Response.DISLIKE)
            ));

            dataset.put("F002", List.of(
                new CustomerResponse("C001", Response.LIKE, Response.DISLIKE),
                new CustomerResponse("C002", Response.LIKE, Response.NEUTRAL),
                new CustomerResponse("C003", Response.LIKE, Response.DISLIKE)
            ));

            dataset.put("F003", List.of(
                new CustomerResponse("C001", Response.EXPECT, Response.DISLIKE),
                new CustomerResponse("C002", Response.EXPECT, Response.DISLIKE),
                new CustomerResponse("C003", Response.LIKE, Response.DISLIKE)
            ));

            dataset.put("F004", List.of(
                new CustomerResponse("C001", Response.NEUTRAL, Response.NEUTRAL),
                new CustomerResponse("C002", Response.EXPECT, Response.NEUTRAL),
                new CustomerResponse("C003", Response.NEUTRAL, Response.TOLERATE)
            ));

            dataset.forEach((featureId, responses) ->
                responses.forEach(response ->
                    service.recordResponse(featureId, response)
                )
            );

            service.printReport();

            // Demonstrate enterprise feature lifecycle.
            KanoFeature lifecycleFeature =
                new KanoFeature("F005", "Mobile Access", "Mobile access.");

            lifecycleFeature.transitionTo(
                FeatureStatus.UNDER_RESEARCH
            );

            lifecycleFeature.transitionTo(
                FeatureStatus.APPROVED
            );

            lifecycleFeature.transitionTo(
                FeatureStatus.IN_DEVELOPMENT
            );

            System.out.println(
                "\nFeature lifecycle: " + lifecycleFeature.status()
            );

            // Verify classification.
            if (evaluate(Response.LIKE, Response.DISLIKE)
                != Category.MUST_BE) {
                throw new IllegalStateException(
                    "Kano classification test failed."
                );
            }

            // Verify duplicate response rejection.
            try {
                service.recordResponse(
                    "F001",
                    new CustomerResponse(
                        "C001",
                        Response.LIKE,
                        Response.DISLIKE
                    )
                );

                throw new IllegalStateException(
                    "Duplicate validation failed."
                );
            } catch (ValidationException expected) {
                System.out.println(
                    "Duplicate response correctly rejected."
                );
            }

            System.out.println("All validation tests passed.");

        } catch (RuntimeException exception) {
            System.err.println(
                "Application error: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
