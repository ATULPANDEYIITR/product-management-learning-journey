import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.OptionalDouble;
import java.util.stream.Collectors;

public class DesignThinkingEnterpriseModel {

    enum Stage {
        EMPATHIZE,
        DEFINE,
        IDEATE,
        PROTOTYPE,
        TEST
    }

    enum TestOutcome {
        SUCCESS,
        FAILURE
    }

    record User(
        String id,
        String role,
        String context
    ) {
        User {
            requireText(id, "User id");
            requireText(role, "User role");
            requireText(context, "User context");
        }
    }

    record Observation(
        String userId,
        String behavior,
        String painPoint,
        double evidenceStrength
    ) {
        Observation {
            requireText(userId, "Observation user");
            requireText(behavior, "Observation behavior");
            requireText(painPoint, "Observation pain point");

            if (evidenceStrength < 0 || evidenceStrength > 1) {
                throw new IllegalArgumentException(
                    "Evidence strength must be between 0 and 1"
                );
            }
        }
    }

    record Insight(
        String statement,
        double confidence,
        List<Observation> evidence
    ) {
        Insight {
            requireText(statement, "Insight statement");

            if (confidence < 0 || confidence > 1) {
                throw new IllegalArgumentException(
                    "Insight confidence must be between 0 and 1"
                );
            }

            evidence = List.copyOf(evidence);
        }
    }

    record ProblemStatement(
        String user,
        String need,
        String insight,
        String successMeasure
    ) {
        ProblemStatement {
            requireText(user, "Problem user");
            requireText(need, "Problem need");
            requireText(insight, "Problem insight");
            requireText(successMeasure, "Problem success measure");
        }
    }

    record Idea(
        String name,
        String description,
        double userValue,
        double feasibility,
        double desirability,
        double risk
    ) {
        Idea {
            requireText(name, "Idea name");
            requireText(description, "Idea description");

            validateScore(userValue, "User value");
            validateScore(feasibility, "Feasibility");
            validateScore(desirability, "Desirability");
            validateScore(risk, "Risk");
        }

        double score() {
            return userValue * 0.40
                + feasibility * 0.25
                + desirability * 0.25
                - risk * 0.10;
        }
    }

    record Prototype(
        String ideaName,
        String fidelity,
        List<String> interactions,
        List<String> assumptions
    ) {
        Prototype {
            requireText(ideaName, "Prototype idea");
            requireText(fidelity, "Prototype fidelity");
            interactions = List.copyOf(interactions);
            assumptions = List.copyOf(assumptions);
        }
    }

    record TestResult(
        String participantId,
        String task,
        TestOutcome outcome,
        double timeSeconds,
        int errors,
        int satisfaction,
        String observation
    ) {
        TestResult {
            requireText(participantId, "Participant");
            requireText(task, "Task");
            requireText(observation, "Observation");

            if (timeSeconds <= 0) {
                throw new IllegalArgumentException("Task time must be positive");
            }

            if (errors < 0) {
                throw new IllegalArgumentException("Errors cannot be negative");
            }

            if (satisfaction < 1 || satisfaction > 5) {
                throw new IllegalArgumentException(
                    "Satisfaction must be between 1 and 5"
                );
            }
        }
    }

    static final class DesignRepository {
        private final List<User> users = new ArrayList<>();
        private final List<Observation> observations = new ArrayList<>();
        private final List<Insight> insights = new ArrayList<>();
        private final List<Idea> ideas = new ArrayList<>();
        private final List<TestResult> tests = new ArrayList<>();

        private ProblemStatement problem;
        private Prototype prototype;

        void addUser(User user) {
            users.add(Objects.requireNonNull(user));
        }

        void addObservation(Observation observation) {
            observations.add(Objects.requireNonNull(observation));
        }

        void addInsight(Insight insight) {
            insights.add(Objects.requireNonNull(insight));
        }

        void addIdea(Idea idea) {
            ideas.add(Objects.requireNonNull(idea));
        }

        void addTest(TestResult result) {
            tests.add(Objects.requireNonNull(result));
        }

        void setProblem(ProblemStatement problem) {
            this.problem = Objects.requireNonNull(problem);
        }

        void setPrototype(Prototype prototype) {
            this.prototype = Objects.requireNonNull(prototype);
        }

        List<Observation> observations() {
            return List.copyOf(observations);
        }

        List<Insight> insights() {
            return List.copyOf(insights);
        }

        List<Idea> ideas() {
            return List.copyOf(ideas);
        }

        List<TestResult> tests() {
            return List.copyOf(tests);
        }

        OptionalDouble completionRate() {
            if (tests.isEmpty()) {
                return OptionalDouble.empty();
            }

            return OptionalDouble.of(
                tests.stream()
                    .mapToInt(test ->
                        test.outcome() == TestOutcome.SUCCESS ? 1 : 0
                    )
                    .average()
                    .orElse(0)
            );
        }

        OptionalDouble averageErrors() {
            return tests.stream()
                .mapToInt(TestResult::errors)
                .average();
        }

        OptionalDouble averageSatisfaction() {
            return tests.stream()
                .mapToInt(TestResult::satisfaction)
                .average();
        }

        void printState() {
            System.out.println("Users: " + users.size());
            System.out.println("Observations: " + observations.size());
            System.out.println("Insights: " + insights.size());
            System.out.println("Ideas: " + ideas.size());
            System.out.println(
                "Problem defined: " + (problem != null)
            );
            System.out.println(
                "Prototype created: " + (prototype != null)
            );
            System.out.println("Tests: " + tests.size());
        }
    }

    static final class DesignService {
        private final DesignRepository repository;
        private Stage stage = Stage.EMPATHIZE;

        DesignService(DesignRepository repository) {
            this.repository = repository;
        }

        void transitionTo(Stage next) {
            Objects.requireNonNull(next);

            int current = stage.ordinal();
            int target = next.ordinal();

            if (target > current + 1) {
                throw new IllegalStateException(
                    "The workflow cannot skip a design stage"
                );
            }

            stage = next;
        }

        void synthesizeInsights() {
            if (repository.observations().isEmpty()) {
                throw new IllegalStateException(
                    "Empathy evidence is required"
                );
            }

            Map<String, List<Observation>> grouped =
                repository.observations()
                    .stream()
                    .collect(Collectors.groupingBy(
                        Observation::painPoint,
                        () -> new java.util.LinkedHashMap<>(),
                        Collectors.toList()
                    ));

            grouped.forEach((painPoint, evidence) -> {
                double confidence = evidence.stream()
                    .mapToDouble(Observation::evidenceStrength)
                    .average()
                    .orElseThrow();

                repository.addInsight(
                    new Insight(
                        "Repeated evidence indicates that users experience: "
                            + painPoint,
                        confidence,
                        evidence
                    )
                );
            });
        }

        void defineProblem() {
            Insight strongest = repository.insights()
                .stream()
                .max(Comparator.comparingDouble(Insight::confidence))
                .orElseThrow(() ->
                    new IllegalStateException(
                        "Insights are required before problem definition"
                    )
                );

            repository.setProblem(
                new ProblemStatement(
                    "Employees processing internal requests",
                    "A contextual workflow that exposes state, evidence, and next action",
                    strongest.statement(),
                    "Reduce processing time while maintaining decision accuracy"
                )
            );
        }

        void createPrototype() {
            Idea selected = repository.ideas()
                .stream()
                .max(Comparator.comparingDouble(Idea::score))
                .orElseThrow(() ->
                    new IllegalStateException(
                        "At least one idea is required"
                    )
                );

            repository.setPrototype(
                new Prototype(
                    selected.name(),
                    "Medium fidelity",
                    List.of(
                        "Filter request queue",
                        "Open request context",
                        "Inspect evidence",
                        "Identify blockers",
                        "Perform the next action"
                    ),
                    List.of(
                        "The next action is visible without leaving the request",
                        "Decision evidence is available at the decision point",
                        "A blocked request exposes the missing information"
                    )
                )
            );
        }

        void evaluateTests() {
            List<TestResult> tests = repository.tests();

            if (tests.isEmpty()) {
                throw new IllegalStateException("No test results exist");
            }

            double completion = repository.completionRate().orElseThrow();
            double errors = repository.averageErrors().orElseThrow();
            double satisfaction =
                repository.averageSatisfaction().orElseThrow();

            System.out.printf(
                "Completion rate: %.1f%%%n",
                completion * 100
            );
            System.out.printf("Average errors: %.2f%n", errors);
            System.out.printf(
                "Average satisfaction: %.2f/5%n",
                satisfaction
            );

            tests.stream()
                .filter(test -> test.outcome() == TestOutcome.FAILURE)
                .findFirst()
                .ifPresent(test ->
                    System.out.println(
                        "Iteration trigger: " + test.observation()
                    )
                );
        }

        Stage currentStage() {
            return stage;
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " cannot be empty");
        }
    }

    private static void validateScore(double value, String field) {
        if (value < 0 || value > 10) {
            throw new IllegalArgumentException(
                field + " must be between 0 and 10"
            );
        }
    }

    public static void main(String[] args) {
        try {
            DesignRepository repository = new DesignRepository();
            DesignService service = new DesignService(repository);

            repository.addUser(new User(
                "U01",
                "Operations Analyst",
                "Handles a high volume of internal requests"
            ));

            repository.addUser(new User(
                "U02",
                "Finance Analyst",
                "Reviews requests requiring financial approval"
            ));

            repository.addUser(new User(
                "U03",
                "Team Manager",
                "Monitors blocked work and queue health"
            ));

            repository.addObservation(new Observation(
                "U01",
                "Copies queue information into a spreadsheet",
                "Request state is difficult to see",
                0.95
            ));

            repository.addObservation(new Observation(
                "U01",
                "Switches applications to locate request context",
                "Information is fragmented",
                0.90
            ));

            repository.addObservation(new Observation(
                "U02",
                "Delays approval when supporting evidence is incomplete",
                "Decision context is incomplete",
                0.92
            ));

            repository.addObservation(new Observation(
                "U03",
                "Contacts analysts to discover why work is blocked",
                "Metrics do not explain blockers",
                0.88
            ));

            service.synthesizeInsights();
            service.transitionTo(Stage.DEFINE);
            service.defineProblem();

            service.transitionTo(Stage.IDEATE);

            repository.addIdea(new Idea(
                "Contextual Request Workspace",
                "A unified request view with state, evidence, history, and next action",
                9,
                8,
                9,
                3
            ));

            repository.addIdea(new Idea(
                "Decision Summary Panel",
                "A focused decision surface with purpose, evidence, and exceptions",
                8,
                9,
                8,
                2
            ));

            repository.addIdea(new Idea(
                "Blocker Explanation Engine",
                "A component that explains the exact reason work cannot proceed",
                8,
                7,
                7,
                5
            ));

            System.out.println("\nIdeas ranked by design score:");

            repository.ideas()
                .stream()
                .sorted(Comparator.comparingDouble(Idea::score).reversed())
                .forEach(idea ->
                    System.out.printf(
                        "%s -> %.2f%n",
                        idea.name(),
                        idea.score()
                    )
                );

            service.transitionTo(Stage.PROTOTYPE);
            service.createPrototype();

            service.transitionTo(Stage.TEST);

            repository.addTest(new TestResult(
                "U01",
                "Find the next processable request",
                TestOutcome.SUCCESS,
                38,
                1,
                4,
                "The state filter was easy to find."
            ));

            repository.addTest(new TestResult(
                "U02",
                "Approve a request using available evidence",
                TestOutcome.SUCCESS,
                46,
                0,
                5,
                "The decision context was sufficient."
            ));

            repository.addTest(new TestResult(
                "U03",
                "Identify why a request is blocked",
                TestOutcome.FAILURE,
                71,
                3,
                2,
                "The blocked state was visible, but the missing field was unclear."
            ));

            System.out.println("\nTest analysis:");
            service.evaluateTests();

            repository.printState();

            if (repository.completionRate().orElse(0) < 1.0) {
                System.out.println(
                    "\nDesign iteration required: expose the missing field "
                    + "and recovery action directly in the blocked state."
                );
            }

        } catch (IllegalArgumentException | IllegalStateException error) {
            System.err.println(
                "Design workflow error: " + error.getMessage()
            );
            System.exit(1);
        }
    }
}
