import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.UUID;

/**
 * Enterprise user-story governance for a digital banking product.
 *
 * Compile:
 *   javac UserStories.java
 *
 * Run:
 *   java UserStories
 *
 * The model separates user outcomes, acceptance conditions, INVEST quality,
 * refinement decisions, and implementation state.
 */
public class UserStories {

    enum State {
        DRAFT,
        REFINEMENT,
        READY,
        IN_PROGRESS,
        DONE,
        BLOCKED
    }

    enum InvestDimension {
        INDEPENDENT,
        NEGOTIABLE,
        VALUABLE,
        ESTIMABLE,
        SMALL,
        TESTABLE
    }

    enum CriterionType {
        FUNCTIONAL,
        VALIDATION,
        SECURITY,
        PERFORMANCE,
        ACCESSIBILITY
    }

    enum ReviewDecision {
        ACCEPT,
        REQUEST_CHANGES,
        REJECT
    }

    record Persona(
        String name,
        String role,
        String context,
        String goal
    ) {
        Persona {
            name = requireText(name, "Persona name");
            role = requireText(role, "Persona role");
            context = requireText(context, "Persona context");
            goal = requireText(goal, "Persona goal");
        }
    }

    record AcceptanceCriterion(
        String given,
        String when,
        String then,
        CriterionType type
    ) {
        AcceptanceCriterion {
            given = requireText(given, "Given");
            when = requireText(when, "When");
            then = requireText(then, "Then");
            Objects.requireNonNull(type, "Criterion type is required.");
        }

        boolean isObservable() {
            return given.length() >= 8 &&
                   when.length() >= 8 &&
                   then.length() >= 8;
        }

        @Override
        public String toString() {
            return "[" + type + "] Given " + given +
                   ", when " + when +
                   ", then " + then + ".";
        }
    }

    record RefinementResult(
        ReviewDecision decision,
        String reviewer,
        List<String> findings
    ) {
        RefinementResult {
            Objects.requireNonNull(decision);
            reviewer = requireText(reviewer, "Reviewer");
            findings = List.copyOf(findings);
        }
    }

    static final class StoryException extends RuntimeException {
        StoryException(String message) {
            super(message);
        }
    }

    static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new StoryException(field + " cannot be empty.");
        }
        return value.trim();
    }

    static final class UserStory {
        private final String id;
        private final String title;
        private final Persona persona;
        private final String need;
        private final String value;
        private final List<AcceptanceCriterion> criteria;
        private final EnumMap<InvestDimension, Boolean> invest;
        private final Set<String> dependencies;
        private final List<String> auditLog = new ArrayList<>();

        private int points;
        private int priority;
        private State state = State.DRAFT;
        private long revision = 1;

        UserStory(
            String id,
            String title,
            Persona persona,
            String need,
            String value,
            List<AcceptanceCriterion> criteria,
            int points,
            int priority,
            Set<String> dependencies,
            Map<InvestDimension, Boolean> investValues
        ) {
            this.id = requireText(id, "Story ID");
            if (!id.matches("[A-Z]+-\\d+")) {
                throw new StoryException("Story ID must resemble BANK-201.");
            }

            this.title = requireText(title, "Story title");
            this.persona = Objects.requireNonNull(persona);
            this.need = requireText(need, "User need");
            this.value = requireText(value, "User value");

            if (criteria == null || criteria.isEmpty()) {
                throw new StoryException(
                    "A user story requires acceptance criteria."
                );
            }

            this.criteria = List.copyOf(criteria);
            if (points < 0) {
                throw new StoryException("Points cannot be negative.");
            }
            if (priority < 1 || priority > 5) {
                throw new StoryException("Priority must be between 1 and 5.");
            }

            this.points = points;
            this.priority = priority;
            this.dependencies = new TreeSet<>(dependencies);

            if (this.dependencies.contains(id)) {
                throw new StoryException("A story cannot depend on itself.");
            }

            this.invest = new EnumMap<>(InvestDimension.class);
            for (InvestDimension dimension : InvestDimension.values()) {
                this.invest.put(
                    dimension,
                    investValues.getOrDefault(dimension, Boolean.TRUE)
                );
            }

            audit("Story created");
        }

        String getId() {
            return id;
        }

        String getTitle() {
            return title;
        }

        State getState() {
            return state;
        }

        int getPriority() {
            return priority;
        }

        int getPoints() {
            return points;
        }

        Set<String> getDependencies() {
            return Collections.unmodifiableSet(dependencies);
        }

        String statement() {
            return "As a " + persona.role() +
                   ", I want " + need +
                   ", so that " + value + ".";
        }

        List<String> validationErrors() {
            List<String> errors = new ArrayList<>();

            if (criteria.stream().anyMatch(c -> !c.isObservable())) {
                errors.add("One or more criteria are not sufficiently specific.");
            }

            for (InvestDimension dimension : InvestDimension.values()) {
                if (!invest.get(dimension)) {
                    errors.add("INVEST criterion fails: " + dimension);
                }
            }

            if (state == State.READY && !errors.isEmpty()) {
                errors.add("Ready state conflicts with story quality.");
            }

            return errors;
        }

        List<InvestDimension> investFailures() {
            List<InvestDimension> failures = new ArrayList<>();
            invest.forEach((dimension, passed) -> {
                if (!passed) failures.add(dimension);
            });
            return List.copyOf(failures);
        }

        void setInvestResult(InvestDimension dimension, boolean passed) {
            if (state == State.DONE || state == State.IN_PROGRESS) {
                throw new StoryException(
                    "INVEST attributes cannot be changed after work starts."
                );
            }
            invest.put(Objects.requireNonNull(dimension), passed);
            revision++;
            audit("INVEST updated: " + dimension + "=" + passed);
        }

        void transition(State next, Map<String, UserStory> backlog) {
            Objects.requireNonNull(next);

            EnumMap<State, Set<State>> allowed = new EnumMap<>(State.class);
            allowed.put(State.DRAFT,
                EnumSet.of(State.REFINEMENT, State.BLOCKED));
            allowed.put(State.REFINEMENT,
                EnumSet.of(State.DRAFT, State.READY, State.BLOCKED));
            allowed.put(State.READY,
                EnumSet.of(State.IN_PROGRESS, State.REFINEMENT, State.BLOCKED));
            allowed.put(State.IN_PROGRESS,
                EnumSet.of(State.DONE, State.BLOCKED, State.REFINEMENT));
            allowed.put(State.BLOCKED,
                EnumSet.of(State.REFINEMENT, State.READY));
            allowed.put(State.DONE, EnumSet.noneOf(State.class));

            if (!allowed.get(state).contains(next)) {
                throw new StoryException(
                    "Invalid transition for " + id + ": " + state + " -> " + next
                );
            }

            if (next == State.READY) {
                List<InvestDimension> failures = investFailures();
                if (!failures.isEmpty()) {
                    throw new StoryException(
                        "INVEST failures prevent readiness: " + failures
                    );
                }

                for (String dependency : dependencies) {
                    UserStory required = backlog.get(dependency);
                    if (required == null || required.state != State.DONE) {
                        throw new StoryException(
                            "Dependency is not complete: " + dependency
                        );
                    }
                }
            }

            State previous = state;
            state = next;
            revision++;
            audit("State changed from " + previous + " to " + next);
        }

        void recordRefinement(RefinementResult result) {
            Objects.requireNonNull(result);

            if (state != State.REFINEMENT) {
                throw new StoryException(
                    "Refinement decisions require the refinement state."
                );
            }

            audit(
                "Refinement by " + result.reviewer() +
                ": " + result.decision() +
                ", findings=" + result.findings()
            );

            if (result.decision() == ReviewDecision.REQUEST_CHANGES) {
                transition(State.DRAFT, Map.of());
            } else if (result.decision() == ReviewDecision.REJECT) {
                transition(State.BLOCKED, Map.of());
            }
        }

        private void audit(String message) {
            auditLog.add(
                "revision=" + revision + " | " + message
            );
        }

        void printDetails() {
            System.out.println("\n" + id + " - " + title);
            System.out.println(statement());
            System.out.println("State: " + state);
            System.out.println("Points: " + points);
            System.out.println("Priority: " + priority);
            System.out.println("Dependencies: " + dependencies);

            for (AcceptanceCriterion criterion : criteria) {
                System.out.println("  " + criterion);
            }

            System.out.println("INVEST failures: " + investFailures());
            System.out.println("Audit:");
            auditLog.forEach(line -> System.out.println("  " + line));
        }
    }

    static final class Backlog {
        private final Map<String, UserStory> stories = new HashMap<>();

        void add(UserStory story) {
            Objects.requireNonNull(story);
            if (stories.putIfAbsent(story.getId(), story) != null) {
                throw new StoryException(
                    "Duplicate story ID: " + story.getId()
                );
            }
        }

        Map<String, UserStory> view() {
            return Collections.unmodifiableMap(stories);
        }

        List<String> dependencyOrder() {
            List<String> result = new ArrayList<>();
            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();

            for (String id : new TreeSet<>(stories.keySet())) {
                visit(id, visiting, visited, result);
            }

            return result;
        }

        private void visit(
            String id,
            Set<String> visiting,
            Set<String> visited,
            List<String> result
        ) {
            if (visiting.contains(id)) {
                throw new StoryException("Dependency cycle at " + id);
            }
            if (visited.contains(id)) return;

            UserStory story = stories.get(id);
            if (story == null) {
                throw new StoryException("Unknown story: " + id);
            }

            visiting.add(id);
            for (String dependency : story.getDependencies()) {
                if (!stories.containsKey(dependency)) {
                    throw new StoryException(
                        id + " references missing dependency " + dependency
                    );
                }
                visit(dependency, visiting, visited, result);
            }

            visiting.remove(id);
            visited.add(id);
            result.add(id);
        }

        List<UserStory> prioritized() {
            return stories.values().stream()
                .sorted((a, b) -> {
                    int priorityOrder =
                        Integer.compare(a.getPriority(), b.getPriority());
                    if (priorityOrder != 0) return priorityOrder;

                    int sizeOrder =
                        Integer.compare(a.getPoints(), b.getPoints());
                    if (sizeOrder != 0) return sizeOrder;

                    return a.getId().compareTo(b.getId());
                })
                .toList();
        }
    }

    public static void main(String[] args) {
        Persona customer = new Persona(
            "Nisha",
            "bank customer",
            "using mobile banking",
            "transfer money with a clear confirmation"
        );

        Persona auditor = new Persona(
            "Dev",
            "compliance analyst",
            "reviewing customer transfer records",
            "verify that transfer evidence is retained"
        );

        List<AcceptanceCriterion> accountCriteria = List.of(
            new AcceptanceCriterion(
                "the customer has authenticated",
                "the customer selects an eligible account",
                "the account balance and currency are displayed",
                CriterionType.FUNCTIONAL
            )
        );

        List<AcceptanceCriterion> transferCriteria = List.of(
            new AcceptanceCriterion(
                "the customer has selected an eligible account",
                "the customer submits a valid transfer",
                "the system records one transfer and displays a reference",
                CriterionType.FUNCTIONAL
            ),
            new AcceptanceCriterion(
                "a previous transfer request succeeded without a response",
                "the customer retries with the same idempotency key",
                "the original transfer is returned without a second debit",
                CriterionType.SECURITY
            )
        );

        List<AcceptanceCriterion> auditCriteria = List.of(
            new AcceptanceCriterion(
                "a transfer has completed",
                "an authorized analyst requests its audit record",
                "the record shows a reference, timestamp, and outcome",
                CriterionType.SECURITY
            )
        );

        Backlog backlog = new Backlog();

        UserStory account = new UserStory(
            "BANK-201",
            "Display an eligible funding account",
            customer,
            "view an eligible funding account",
            "I can select the correct source of funds",
            accountCriteria,
            3,
            1,
            Set.of(),
            Map.of()
        );

        UserStory transfer = new UserStory(
            "BANK-202",
            "Submit a money transfer",
            customer,
            "transfer money after reviewing recipient and amount",
            "I can send money with a traceable confirmation",
            transferCriteria,
            5,
            1,
            Set.of("BANK-201"),
            Map.of()
        );

        UserStory audit = new UserStory(
            "BANK-203",
            "Inspect transfer evidence",
            auditor,
            "retrieve an authorized transfer audit record",
            "I can verify the recorded transaction outcome",
            auditCriteria,
            3,
            2,
            Set.of("BANK-202"),
            Map.of(InvestDimension.SMALL, false)
        );

        backlog.add(account);
        backlog.add(transfer);
        backlog.add(audit);

        System.out.println("Dependency order: " + backlog.dependencyOrder());

        account.transition(State.REFINEMENT, backlog.view());
        account.transition(State.READY, backlog.view());
        account.transition(State.IN_PROGRESS, backlog.view());
        account.transition(State.DONE, backlog.view());

        transfer.transition(State.REFINEMENT, backlog.view());
        transfer.transition(State.READY, backlog.view());

        transfer.transition(State.IN_PROGRESS, backlog.view());
        transfer.transition(State.DONE, backlog.view());

        audit.transition(State.REFINEMENT, backlog.view());

        try {
            audit.transition(State.READY, backlog.view());
        } catch (StoryException error) {
            System.out.println(
                "Expected readiness rejection: " + error.getMessage()
            );
        }

        audit.setInvestResult(InvestDimension.SMALL, true);
        audit.transition(State.READY, backlog.view());

        System.out.println("\nPrioritized enterprise backlog:");
        backlog.prioritized().forEach(UserStory::printDetails);

        // Immutable records, explicit transitions, and controlled access to
        // collections reduce accidental mutation of domain state.
    }
}
