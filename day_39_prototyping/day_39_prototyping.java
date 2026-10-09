import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/**
 * Enterprise prototype governance and usability evaluation.
 *
 * Compile: javac PrototypeGovernance.java
 * Run:     java PrototypeGovernance
 *
 * Requires Java 17 or later. The example uses only the standard library.
 */
public class PrototypeGovernance {

    enum Fidelity {
        LOW,
        MEDIUM,
        HIGH
    }

    enum Lifecycle {
        DRAFT,
        TESTABLE,
        RETIRED
    }

    enum Screen {
        DASHBOARD,
        EXPENSE_FORM,
        SUBMITTING,
        CONFIRMATION,
        HISTORY
    }

    enum Outcome {
        COMPLETED,
        FAILED,
        ABANDONED
    }

    record DesignElement(
            String id,
            String label,
            boolean interactive,
            Map<String, String> attributes) {

        DesignElement {
            requireText(id, "Element ID");
            requireText(label, "Element label");
            attributes = Map.copyOf(Objects.requireNonNull(attributes));
        }
    }

    record ScreenDefinition(String id, List<DesignElement> elements) {
        ScreenDefinition {
            requireText(id, "Screen ID");
            elements = List.copyOf(Objects.requireNonNull(elements));

            Set<String> identifiers = new HashSet<>();
            for (DesignElement element : elements) {
                if (!identifiers.add(element.id())) {
                    throw new IllegalArgumentException(
                            "Duplicate element ID on screen " + id);
                }
            }
        }
    }

    static final class PrototypeArtifact {
        private final String id;
        private final Fidelity fidelity;
        private final String researchQuestion;
        private final Map<String, ScreenDefinition> screens;
        private final List<String> assumptions = new ArrayList<>();
        private Lifecycle lifecycle = Lifecycle.DRAFT;
        private int revision = 1;

        PrototypeArtifact(
                String id,
                Fidelity fidelity,
                String researchQuestion,
                List<ScreenDefinition> definitions) {
            this.id = requireText(id, "Prototype ID");
            this.fidelity = Objects.requireNonNull(fidelity);
            this.researchQuestion = requireText(
                    researchQuestion, "Research question");

            if (definitions == null || definitions.isEmpty()) {
                throw new IllegalArgumentException(
                        "A prototype needs at least one screen.");
            }

            Map<String, ScreenDefinition> indexed = new java.util.LinkedHashMap<>();
            for (ScreenDefinition definition : definitions) {
                if (indexed.putIfAbsent(definition.id(), definition) != null) {
                    throw new IllegalArgumentException(
                            "Duplicate screen ID: " + definition.id());
                }
            }
            this.screens = Collections.unmodifiableMap(indexed);
        }

        void publish() {
            if (lifecycle != Lifecycle.DRAFT) {
                throw new IllegalStateException(
                        "Only draft prototypes can be published.");
            }
            lifecycle = Lifecycle.TESTABLE;
        }

        void revise(String evidence) {
            if (lifecycle == Lifecycle.RETIRED) {
                throw new IllegalStateException(
                        "Retired prototypes cannot be revised.");
            }
            assumptions.add(requireText(evidence, "Revision evidence"));
            revision++;
        }

        void retire() {
            if (lifecycle == Lifecycle.RETIRED) {
                throw new IllegalStateException("Prototype already retired.");
            }
            lifecycle = Lifecycle.RETIRED;
        }

        long interactiveElementCount() {
            return screens.values().stream()
                    .flatMap(screen -> screen.elements().stream())
                    .filter(DesignElement::interactive)
                    .count();
        }

        void print() {
            System.out.printf(
                    "%s | %s | lifecycle=%s | screens=%d | interactive=%d%n",
                    id, fidelity, lifecycle, screens.size(),
                    interactiveElementCount());
            System.out.println("  Research question: " + researchQuestion);
        }
    }

    record Expense(
            long id,
            String description,
            BigDecimal amount,
            String category,
            Instant submittedAt) {

        Expense {
            if (id <= 0) {
                throw new IllegalArgumentException("Expense ID must be positive.");
            }
            description = requireText(description, "Description");
            category = requireText(category, "Category");
            amount = Objects.requireNonNull(amount)
                    .setScale(2, RoundingMode.HALF_UP);

            if (amount.signum() <= 0 ||
                    amount.compareTo(new BigDecimal("1000000.00")) > 0) {
                throw new IllegalArgumentException(
                        "Amount must be between 0.01 and 1,000,000.00.");
            }
            submittedAt = Objects.requireNonNull(submittedAt);
        }
    }

    static final class ExpenseService {
        private final List<Expense> expenses = new ArrayList<>();
        private long nextId = 1;

        Expense submit(String description, BigDecimal amount, String category) {
            // The service creates immutable records only after validating every
            // required field, avoiding partially constructed expense objects.
            Expense expense = new Expense(
                    nextId, description, amount, category, Instant.now());
            expenses.add(expense);
            nextId++;
            return expense;
        }

        List<Expense> findAll() {
            return List.copyOf(expenses);
        }

        BigDecimal total() {
            return expenses.stream()
                    .map(Expense::amount)
                    .reduce(BigDecimal.ZERO, BigDecimal::add)
                    .setScale(2, RoundingMode.HALF_UP);
        }
    }

    static final class PrototypeSession {
        private final ExpenseService service;
        private final Fidelity fidelity;
        private final Map<Screen, Set<Screen>> transitions =
                new EnumMap<>(Screen.class);
        private Screen current = Screen.DASHBOARD;
        private boolean pending;
        private String lastMessage = "";

        PrototypeSession(ExpenseService service, Fidelity fidelity) {
            this.service = Objects.requireNonNull(service);
            if (fidelity == Fidelity.LOW) {
                throw new IllegalArgumentException(
                        "Low-fidelity artifacts do not execute form submissions.");
            }
            this.fidelity = fidelity;

            transitions.put(Screen.DASHBOARD,
                    Set.of(Screen.EXPENSE_FORM, Screen.HISTORY));
            transitions.put(Screen.EXPENSE_FORM,
                    Set.of(Screen.DASHBOARD));
            transitions.put(Screen.CONFIRMATION,
                    Set.of(Screen.DASHBOARD, Screen.HISTORY));
            transitions.put(Screen.HISTORY,
                    Set.of(Screen.DASHBOARD));
            transitions.put(Screen.SUBMITTING, Set.of());
        }

        boolean navigate(Screen destination) {
            Objects.requireNonNull(destination);
            if (!transitions.getOrDefault(current, Set.of())
                    .contains(destination)) {
                lastMessage = "Invalid navigation: " + current + " -> " +
                        destination;
                return false;
            }
            current = destination;
            lastMessage = "";
            return true;
        }

        Optional<Expense> submit(
                String description, BigDecimal amount, String category) {
            if (current != Screen.EXPENSE_FORM) {
                lastMessage = "Open the expense form before submitting.";
                return Optional.empty();
            }
            if (pending) {
                lastMessage = "A submission is already in progress.";
                return Optional.empty();
            }

            pending = true;
            current = Screen.SUBMITTING;

            try {
                Expense expense = service.submit(description, amount, category);
                current = Screen.CONFIRMATION;
                lastMessage = "Submission completed.";
                return Optional.of(expense);
            } catch (IllegalArgumentException exception) {
                // Validation failure returns to the form so users can correct
                // input instead of losing the task or seeing a false success.
                current = Screen.EXPENSE_FORM;
                lastMessage = exception.getMessage();
                return Optional.empty();
            } finally {
                pending = false;
            }
        }

        Screen currentScreen() {
            return current;
        }

        String lastMessage() {
            return lastMessage;
        }

        Fidelity fidelity() {
            return fidelity;
        }
    }

    record UsabilityObservation(
            String participant,
            String task,
            Outcome outcome,
            double durationSeconds,
            int errors,
            int confidence) {

        UsabilityObservation {
            requireText(participant, "Participant");
            requireText(task, "Task");
            Objects.requireNonNull(outcome);

            if (!Double.isFinite(durationSeconds) || durationSeconds < 0) {
                throw new IllegalArgumentException(
                        "Duration must be finite and non-negative.");
            }
            if (errors < 0) {
                throw new IllegalArgumentException(
                        "Error count cannot be negative.");
            }
            if (confidence < 1 || confidence > 5) {
                throw new IllegalArgumentException(
                        "Confidence must be between 1 and 5.");
            }
        }
    }

    static final class UsabilityReport {
        private final List<UsabilityObservation> observations;

        UsabilityReport(List<UsabilityObservation> observations) {
            if (observations == null || observations.isEmpty()) {
                throw new IllegalArgumentException(
                        "Usability evidence cannot be empty.");
            }
            this.observations = List.copyOf(observations);
        }

        void print() {
            long completed = observations.stream()
                    .filter(item -> item.outcome() == Outcome.COMPLETED)
                    .count();
            long errors = observations.stream()
                    .mapToLong(UsabilityObservation::errors)
                    .sum();
            double averageDuration = observations.stream()
                    .mapToDouble(UsabilityObservation::durationSeconds)
                    .average().orElseThrow();
            double averageConfidence = observations.stream()
                    .mapToInt(UsabilityObservation::confidence)
                    .average().orElseThrow();
            double completionRate =
                    (double) completed / observations.size();

            System.out.printf("Completion rate: %.1f%%%n",
                    completionRate * 100);
            System.out.printf("Mean duration: %.1f seconds%n", averageDuration);
            System.out.println("Observed errors: " + errors);
            System.out.printf("Mean confidence: %.2f / 5%n",
                    averageConfidence);

            if (completionRate < 0.90) {
                System.out.println(
                        "Research action: investigate navigation and task wording.");
            }
            if (errors > observations.size()) {
                System.out.println(
                        "Research action: investigate field validation and recovery.");
            }
        }
    }

    private static String requireText(String value, String label) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(label + " is required.");
        }
        return value.trim();
    }

    private static List<PrototypeArtifact> createArtifacts() {
        DesignElement paperSubmit =
                new DesignElement("submit", "Submit expense", false, Map.of());
        DesignElement clickableSubmit =
                new DesignElement("submit", "Submit expense", true,
                        Map.of("role", "primary-action"));
        DesignElement validatedAmount =
                new DesignElement("amount", "Expense amount", true,
                        Map.of("minimum", "0.01", "maximum", "1000000.00"));
        DesignElement loadingButton =
                new DesignElement("submit", "Submit expense", true,
                        Map.of("loading-state", "visible"));

        return List.of(
                new PrototypeArtifact(
                        "paper-flow", Fidelity.LOW,
                        "Can employees locate the expense submission path?",
                        List.of(
                                new ScreenDefinition("dashboard",
                                        List.of(paperSubmit)),
                                new ScreenDefinition("form",
                                        List.of(new DesignElement(
                                                "amount", "Amount", false,
                                                Map.of())))
                        )),
                new PrototypeArtifact(
                        "clickable-flow", Fidelity.MEDIUM,
                        "Can employees complete the expense form?",
                        List.of(
                                new ScreenDefinition("dashboard",
                                        List.of(clickableSubmit)),
                                new ScreenDefinition("form",
                                        List.of(validatedAmount))
                        )),
                new PrototypeArtifact(
                        "realistic-flow", Fidelity.HIGH,
                        "Does visible loading feedback prevent repeat actions?",
                        List.of(
                                new ScreenDefinition("form",
                                        List.of(validatedAmount, loadingButton)),
                                new ScreenDefinition("confirmation",
                                        List.of(new DesignElement(
                                                "receipt", "Receipt reference",
                                                false, Map.of())))
                        ))
        );
    }

    public static void main(String[] args) {
        List<PrototypeArtifact> artifacts = createArtifacts();
        System.out.println("Enterprise prototype artifacts");
        for (PrototypeArtifact artifact : artifacts) {
            artifact.print();
        }

        PrototypeArtifact medium = artifacts.get(1);
        medium.publish();
        medium.revise(
                "Testing exposed ambiguity in the amount field's currency.");
        medium.print();

        ExpenseService service = new ExpenseService();
        PrototypeSession session =
                new PrototypeSession(service, Fidelity.HIGH);

        System.out.println("\nWorkflow experiment");
        System.out.println("Open form: " +
                session.navigate(Screen.EXPENSE_FORM));

        Optional<Expense> valid = session.submit(
                "Regional travel",
                new BigDecimal("1250.50"),
                "Travel");
        valid.ifPresent(expense ->
                System.out.println("Created expense: " + expense));

        session.navigate(Screen.DASHBOARD);
        session.navigate(Screen.EXPENSE_FORM);

        Optional<Expense> invalid = session.submit(
                "Office supplies", new BigDecimal("-25.00"), "Operations");
        System.out.println("Invalid submission accepted: " + invalid.isPresent());
        System.out.println("Recovery screen: " + session.currentScreen());
        System.out.println("Feedback: " + session.lastMessage());
        System.out.println("Ledger total: " + service.total());

        UsabilityReport report = new UsabilityReport(List.of(
                new UsabilityObservation(
                        "employee-A", "submit-expense", Outcome.COMPLETED,
                        24.0, 0, 5),
                new UsabilityObservation(
                        "employee-B", "submit-expense", Outcome.COMPLETED,
                        39.0, 1, 4),
                new UsabilityObservation(
                        "employee-C", "submit-expense", Outcome.ABANDONED,
                        60.0, 3, 2)
        ));

        System.out.println("\nUsability evidence");
        report.print();

        if (service.findAll().size() != 1 ||
                service.total().compareTo(new BigDecimal("1250.50")) != 0 ||
                session.currentScreen() != Screen.EXPENSE_FORM) {
            throw new IllegalStateException(
                    "An enterprise prototype invariant failed.");
        }

        System.out.println("Prototype governance checks passed.");
    }
}
