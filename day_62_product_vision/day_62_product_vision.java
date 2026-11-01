import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ProductVisionGovernance {

    enum VisionStatus {
        DRAFT,
        VALIDATED,
        APPROVED,
        ACTIVE,
        RETIRED
    }

    enum Horizon {
        NOW("0-12 months"),
        NEXT("1-3 years"),
        FUTURE("3-5 years");

        private final String label;

        Horizon(String label) {
            this.label = label;
        }

        public String label() {
            return label;
        }
    }

    record CustomerSegment(
        String name,
        Set<String> needs,
        Set<String> painPoints
    ) {
        CustomerSegment {
            needs = Set.copyOf(needs);
            painPoints = Set.copyOf(painPoints);
        }
    }

    static final class Vision {
        private final String product;
        private final String statement;
        private final String customerValue;
        private final String futureState;
        private final List<String> strategicDirections;
        private final List<String> evidence;
        private final Horizon horizon;
        private VisionStatus status;

        Vision(
            String product,
            String statement,
            String customerValue,
            String futureState,
            List<String> strategicDirections,
            List<String> evidence,
            Horizon horizon
        ) {
            this.product = product;
            this.statement = statement;
            this.customerValue = customerValue;
            this.futureState = futureState;
            this.strategicDirections =
                List.copyOf(strategicDirections);
            this.evidence = List.copyOf(evidence);
            this.horizon = horizon;
            this.status = VisionStatus.DRAFT;
        }

        String product() {
            return product;
        }

        String statement() {
            return statement;
        }

        String customerValue() {
            return customerValue;
        }

        String futureState() {
            return futureState;
        }

        List<String> strategicDirections() {
            return strategicDirections;
        }

        List<String> evidence() {
            return evidence;
        }

        Horizon horizon() {
            return horizon;
        }

        VisionStatus status() {
            return status;
        }

        void setStatus(VisionStatus status) {
            this.status = status;
        }
    }

    static final class VisionException extends RuntimeException {
        VisionException(String message) {
            super(message);
        }
    }

    interface VisionPolicy {
        List<String> validate(Vision vision);
    }

    static final class OutcomeBasedVisionPolicy
        implements VisionPolicy {

        private static final Set<String> IMPLEMENTATION_TERMS =
            Set.of(
                "button",
                "database table",
                "screen",
                "api endpoint"
            );

        @Override
        public List<String> validate(Vision vision) {
            List<String> errors = new ArrayList<>();

            if (vision.product() == null ||
                vision.product().isBlank()) {
                errors.add("Product name is required.");
            }

            if (vision.statement() == null ||
                vision.statement().length() < 30) {
                errors.add("Vision statement is too short.");
            }

            if (vision.customerValue() == null ||
                vision.customerValue().isBlank()) {
                errors.add("Customer value is required.");
            }

            if (vision.futureState() == null ||
                vision.futureState().isBlank()) {
                errors.add("Future state is required.");
            }

            if (vision.strategicDirections().isEmpty()) {
                errors.add("Strategic direction is required.");
            }

            if (vision.evidence().isEmpty()) {
                errors.add("Evidence is required.");
            }

            String statement =
                vision.statement() == null
                    ? ""
                    : vision.statement().toLowerCase();

            if (IMPLEMENTATION_TERMS.stream()
                .anyMatch(statement::contains)) {
                errors.add(
                    "Vision must describe outcomes rather than implementation."
                );
            }

            return Collections.unmodifiableList(errors);
        }
    }

    static final class VisionRepository {
        private final Map<String, Vision> visions = new HashMap<>();

        void save(Vision vision) {
            if (visions.containsKey(vision.product())) {
                throw new VisionException(
                    "A vision already exists for this product."
                );
            }

            visions.put(vision.product(), vision);
        }

        Vision find(String product) {
            Vision vision = visions.get(product);

            if (vision == null) {
                throw new VisionException(
                    "Vision not found: " + product
                );
            }

            return vision;
        }
    }

    static final class VisionService {
        private final VisionRepository repository;
        private final VisionPolicy policy;

        VisionService(
            VisionRepository repository,
            VisionPolicy policy
        ) {
            this.repository = repository;
            this.policy = policy;
        }

        void create(Vision vision) {
            List<String> errors = policy.validate(vision);

            if (!errors.isEmpty()) {
                throw new VisionException(String.join(" ", errors));
            }

            repository.save(vision);
        }

        void validate(String product) {
            Vision vision = repository.find(product);

            requireStatus(vision, VisionStatus.DRAFT);

            List<String> errors = policy.validate(vision);

            if (!errors.isEmpty()) {
                throw new VisionException(String.join(" ", errors));
            }

            vision.setStatus(VisionStatus.VALIDATED);
        }

        void approve(String product) {
            Vision vision = repository.find(product);
            requireStatus(vision, VisionStatus.VALIDATED);
            vision.setStatus(VisionStatus.APPROVED);
        }

        void activate(String product) {
            Vision vision = repository.find(product);
            requireStatus(vision, VisionStatus.APPROVED);
            vision.setStatus(VisionStatus.ACTIVE);
        }

        void retire(String product) {
            Vision vision = repository.find(product);
            requireStatus(vision, VisionStatus.ACTIVE);
            vision.setStatus(VisionStatus.RETIRED);
        }

        private void requireStatus(
            Vision vision,
            VisionStatus expected
        ) {
            if (vision.status() != expected) {
                throw new VisionException(
                    "Expected status " + expected +
                    " but found " + vision.status()
                );
            }
        }
    }

    static final class AlignmentService {
        double calculate(
            Vision vision,
            Set<String> priorities,
            List<CustomerSegment> customers
        ) {
            if (priorities.isEmpty()) {
                return 0.0;
            }

            long strategicMatches =
                vision.strategicDirections()
                    .stream()
                    .filter(priorities::contains)
                    .count();

            double strategicScore =
                (double) strategicMatches / priorities.size();

            Set<String> customerTerms = new HashSet<>();

            customers.forEach(customer -> {
                customerTerms.addAll(customer.needs());
                customerTerms.addAll(customer.painPoints());
            });

            long customerMatches =
                vision.strategicDirections()
                    .stream()
                    .filter(customerTerms::contains)
                    .count();

            double customerScore =
                (double) customerMatches /
                Math.max(vision.strategicDirections().size(), 1);

            return (strategicScore * 0.7 +
                    customerScore * 0.3) * 100.0;
        }
    }

    static final class ReportingService {
        void print(Vision vision, double alignment) {
            System.out.println("\nPRODUCT VISION GOVERNANCE REPORT");
            System.out.println("=".repeat(70));
            System.out.println("Product: " + vision.product());
            System.out.println("Status: " + vision.status());
            System.out.println("Horizon: " + vision.horizon().label());
            System.out.println("Vision: " + vision.statement());
            System.out.println(
                "Customer value: " + vision.customerValue()
            );
            System.out.println(
                "Future state: " + vision.futureState()
            );
            System.out.printf(
                "Strategic alignment: %.2f%%%n",
                alignment
            );
        }
    }

    public static void main(String[] args) {
        VisionRepository repository = new VisionRepository();
        VisionPolicy policy = new OutcomeBasedVisionPolicy();
        VisionService service =
            new VisionService(repository, policy);
        AlignmentService alignmentService =
            new AlignmentService();

        Vision vision = new Vision(
            "Operations Intelligence Platform",
            "Enable operations teams to make faster, more reliable decisions from a unified understanding of operational conditions.",
            "Customers gain visibility, reduce decision delays, and improve operational reliability.",
            "Operations become measurable and predictable, allowing teams to identify problems early and coordinate action.",
            List.of(
                "customer trust",
                "operational efficiency",
                "data-driven decisions",
                "scalable growth"
            ),
            List.of(
                "Customer interviews identify fragmented operational information.",
                "Pilot users report delays caused by manual consolidation.",
                "Managers require consistent operational indicators."
            ),
            Horizon.NEXT
        );

        try {
            service.create(vision);
            service.validate(vision.product());
            service.approve(vision.product());
            service.activate(vision.product());

            List<CustomerSegment> customers = List.of(
                new CustomerSegment(
                    "Operations teams",
                    Set.of("visibility", "speed", "reliability"),
                    Set.of("manual work", "decision delays")
                ),
                new CustomerSegment(
                    "Managers",
                    Set.of("control", "insight", "predictability"),
                    Set.of("unclear priorities", "slow reporting")
                )
            );

            Set<String> priorities = Set.of(
                "customer trust",
                "operational efficiency",
                "data-driven decisions",
                "scalable growth"
            );

            double alignment =
                alignmentService.calculate(
                    vision,
                    priorities,
                    customers
                );

            new ReportingService().print(
                vision,
                alignment
            );

            try {
                service.activate(vision.product());
            } catch (VisionException expected) {
                System.out.println(
                    "\nExpected transition failure: " +
                    expected.getMessage()
                );
            }

            Vision invalid = new Vision(
                "Invalid Product",
                "Add a button and database table.",
                "",
                "",
                List.of(),
                List.of(),
                Horizon.NOW
            );

            List<String> errors = policy.validate(invalid);

            System.out.println(
                "Invalid vision errors: " + errors.size()
            );

            if (errors.isEmpty()) {
                throw new VisionException(
                    "Invalid vision unexpectedly passed validation."
                );
            }

        } catch (VisionException error) {
            System.err.println(
                "Governance failure: " + error.getMessage()
            );
            System.exit(1);
        }
    }
}
