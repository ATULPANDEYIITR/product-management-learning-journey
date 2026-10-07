/*
 * Ideation Techniques: Enterprise Repository-Free Case Study
 *
 * Java 17 implementation demonstrating:
 *
 *   Brainstorming
 *       Participant-based divergent generation with delayed evaluation.
 *
 *   Crazy 8s
 *       Eight rapid, deliberately different directions.
 *
 *   SCAMPER
 *       Explicit transformation operators applied to an existing concept.
 *
 *   Mind Mapping
 *       A hierarchical domain model of a central problem.
 *
 *   Reverse Brainstorming
 *       Failure-first analysis converted into countermeasures.
 *
 * The example domain is customer support operations, where the objective is
 * to reduce response time without reducing resolution quality.
 */

import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

public class IdeationTechniquesDemo {

    // -----------------------------------------------------------------------
    // Domain enums
    // -----------------------------------------------------------------------

    enum Technique {
        BRAINSTORMING,
        CRAZY_8S,
        SCAMPER,
        MIND_MAPPING,
        REVERSE_BRAINSTORMING
    }

    enum Perspective {
        CUSTOMER,
        SUPPORT_AGENT,
        OPERATIONS,
        TECHNOLOGY,
        QUALITY
    }

    enum ScamperOperator {
        SUBSTITUTE,
        COMBINE,
        ADAPT,
        MODIFY,
        PUT_TO_ANOTHER_USE,
        ELIMINATE,
        REVERSE
    }

    // -----------------------------------------------------------------------
    // Immutable idea model
    // -----------------------------------------------------------------------

    record Idea(
        String title,
        String description,
        Technique technique,
        int novelty,
        int feasibility,
        int impact,
        int confidence,
        Set<String> tags
    ) {
        Idea {
            Objects.requireNonNull(title, "title");
            Objects.requireNonNull(description, "description");
            Objects.requireNonNull(technique, "technique");

            if (title.isBlank()) {
                throw new IllegalArgumentException(
                    "Idea title cannot be blank."
                );
            }

            if (description.isBlank()) {
                throw new IllegalArgumentException(
                    "Idea description cannot be blank."
                );
            }

            validateScore("novelty", novelty);
            validateScore("feasibility", feasibility);
            validateScore("impact", impact);
            validateScore("confidence", confidence);

            tags = Set.copyOf(tags);
        }

        private static void validateScore(String name, int value) {
            if (value < 1 || value > 5) {
                throw new IllegalArgumentException(
                    name + " must be between 1 and 5."
                );
            }
        }

        double score() {
            return novelty * 0.25
                 + feasibility * 0.25
                 + impact * 0.35
                 + confidence * 0.15;
        }
    }

    // -----------------------------------------------------------------------
    // Enterprise participants
    // -----------------------------------------------------------------------

    record Participant(
        String name,
        Perspective perspective,
        Set<String> expertise
    ) {
        Participant {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Participant name is required."
                );
            }

            Objects.requireNonNull(perspective);
            expertise = Set.copyOf(expertise);
        }
    }

    // -----------------------------------------------------------------------
    // Brainstorming service
    // -----------------------------------------------------------------------

    static final class BrainstormingService {

        private final String problem;
        private final List<Participant> participants;

        BrainstormingService(
            String problem,
            List<Participant> participants
        ) {
            if (problem == null || problem.isBlank()) {
                throw new IllegalArgumentException(
                    "Brainstorming problem is required."
                );
            }

            if (participants == null || participants.isEmpty()) {
                throw new IllegalArgumentException(
                    "At least one participant is required."
                );
            }

            this.problem = problem;
            this.participants = List.copyOf(participants);
        }

        List<Idea> generate() {
            return participants.stream()
                .map(this::generateForParticipant)
                .toList();
        }

        private Idea generateForParticipant(
            Participant participant
        ) {
            String description = switch (participant.perspective()) {
                case CUSTOMER ->
                    "Show response expectations and proactive progress updates.";
                case SUPPORT_AGENT ->
                    "Surface similar resolved cases while an agent works.";
                case OPERATIONS ->
                    "Escalate cases according to queue age and workload.";
                case TECHNOLOGY ->
                    "Classify incoming requests automatically before routing.";
                case QUALITY ->
                    "Measure response speed with reopening and resolution quality.";
            };

            return new Idea(
                participant.name() + " perspective",
                description,
                Technique.BRAINSTORMING,
                4,
                4,
                4,
                4,
                Set.of(
                    "divergent",
                    participant.perspective().name().toLowerCase()
                )
            );
        }

        Idea buildOn(Idea base) {
            Objects.requireNonNull(base);

            return new Idea(
                "Unified intelligent intake",
                "Combine the strongest contribution with automatic "
                    + "classification and duplicate detection.",
                Technique.BRAINSTORMING,
                5,
                4,
                5,
                4,
                Set.of("synthesis", "divergent", "automation")
            );
        }
    }

    // -----------------------------------------------------------------------
    // Crazy 8s service
    // -----------------------------------------------------------------------

    static final class Crazy8sService {

        private final String challenge;

        Crazy8sService(String challenge) {
            if (challenge == null || challenge.isBlank()) {
                throw new IllegalArgumentException(
                    "Crazy 8s challenge is required."
                );
            }

            this.challenge = challenge;
        }

        List<Idea> generate() {
            List<String> prompts = List.of(
                "Remove a manual step.",
                "Automate request classification.",
                "Create guided self-service.",
                "Reverse the normal assignment flow.",
                "Personalize the resolution path.",
                "Make queue state visible.",
                "Combine intake and knowledge retrieval.",
                "Design an intentionally extreme low-touch path."
            );

            return prompts.stream()
                .map(this::createIdea)
                .toList();
        }

        private Idea createIdea(String prompt) {
            return new Idea(
                "Crazy 8 direction",
                prompt,
                Technique.CRAZY_8S,
                4,
                4,
                4,
                3,
                Set.of("rapid", "time-boxed")
            );
        }
    }

    // -----------------------------------------------------------------------
    // SCAMPER service
    // -----------------------------------------------------------------------

    static final class ScamperService {

        private final String existingConcept;

        ScamperService(String existingConcept) {
            if (existingConcept == null || existingConcept.isBlank()) {
                throw new IllegalArgumentException(
                    "An existing concept is required for SCAMPER."
                );
            }

            this.existingConcept = existingConcept;
        }

        List<Idea> generate() {
            return EnumSet.allOf(ScamperOperator.class)
                .stream()
                .map(this::apply)
                .toList();
        }

        private Idea apply(ScamperOperator operator) {
            String description = switch (operator) {
                case SUBSTITUTE ->
                    "Replace first-come-first-served routing with "
                        + "skill and urgency routing.";
                case COMBINE ->
                    "Combine intake, classification, and knowledge retrieval.";
                case ADAPT ->
                    "Adapt emergency-dispatch queueing principles for severe cases.";
                case MODIFY ->
                    "Make intake questions adaptive to previous answers.";
                case PUT_TO_ANOTHER_USE ->
                    "Use support history to identify recurring product defects.";
                case ELIMINATE ->
                    "Remove supervisor handoffs for low-risk known resolutions.";
                case REVERSE ->
                    "Push status updates before customers need to request them.";
            };

            return new Idea(
                operator + ": " + existingConcept,
                description,
                Technique.SCAMPER,
                5,
                operator == ScamperOperator.SUBSTITUTE
                    || operator == ScamperOperator.MODIFY
                    || operator == ScamperOperator.ELIMINATE
                    ? 4 : 3,
                operator == ScamperOperator.COMBINE
                    || operator == ScamperOperator.PUT_TO_ANOTHER_USE
                    || operator == ScamperOperator.REVERSE
                    ? 5 : 4,
                4,
                Set.of("transformation", operator.name().toLowerCase())
            );
        }
    }

    // -----------------------------------------------------------------------
    // Mind map domain
    // -----------------------------------------------------------------------

    static final class MindMapNode {

        private final String label;
        private final String relationship;
        private final List<MindMapNode> children = new ArrayList<>();

        MindMapNode(String label, String relationship) {
            this.label = label;
            this.relationship = relationship;
        }

        MindMapNode addChild(
            String childLabel,
            String childRelationship
        ) {
            MindMapNode child =
                new MindMapNode(childLabel, childRelationship);

            children.add(child);
            return child;
        }

        int depth() {
            if (children.isEmpty()) {
                return 1;
            }

            return 1 + children.stream()
                .mapToInt(MindMapNode::depth)
                .max()
                .orElse(0);
        }

        void print(int depth) {
            System.out.println(
                "  ".repeat(depth)
                    + "- " + label
                    + " [" + relationship + "]"
            );

            for (MindMapNode child : children) {
                child.print(depth + 1);
            }
        }

        void collectIdeas(List<Idea> destination, int depth) {
            if (depth > 0) {
                destination.add(
                    new Idea(
                        label,
                        relationship,
                        Technique.MIND_MAPPING,
                        4,
                        4,
                        4,
                        3,
                        Set.of("association", relationship)
                    )
                );
            }

            for (MindMapNode child : children) {
                child.collectIdeas(destination, depth + 1);
            }
        }
    }

    static final class MindMapService {

        private final MindMapNode root;

        MindMapService(String problem) {
            if (problem == null || problem.isBlank()) {
                throw new IllegalArgumentException(
                    "Mind map problem is required."
                );
            }

            root = new MindMapNode(problem, "central problem");
        }

        void build() {
            MindMapNode customer =
                root.addChild("Customer experience", "dimension");

            customer.addChild(
                "Response expectations",
                "concern"
            );

            customer.addChild(
                "Self-service",
                "opportunity"
            );

            customer.addChild(
                "Progress visibility",
                "opportunity"
            );

            MindMapNode workflow =
                root.addChild("Workflow", "dimension");

            MindMapNode routing =
                workflow.addChild("Routing", "process");

            routing.addChild(
                "Skill matching",
                "mechanism"
            );

            routing.addChild(
                "Urgency classification",
                "mechanism"
            );

            workflow.addChild(
                "Handoffs",
                "bottleneck"
            );

            workflow.addChild(
                "Queue aging",
                "metric"
            );

            MindMapNode knowledge =
                root.addChild("Knowledge", "dimension");

            knowledge.addChild(
                "Search quality",
                "capability"
            );

            knowledge.addChild(
                "Reusable resolutions",
                "capability"
            );

            knowledge.addChild(
                "Missing documentation",
                "root cause"
            );
        }

        void print() {
            root.print(0);
        }

        int depth() {
            return root.depth();
        }

        List<Idea> toIdeas() {
            List<Idea> ideas = new ArrayList<>();
            root.collectIdeas(ideas, 0);
            return List.copyOf(ideas);
        }
    }

    // -----------------------------------------------------------------------
    // Reverse brainstorming
    // -----------------------------------------------------------------------

    static final class ReverseBrainstormingService {

        private final String desiredOutcome;

        ReverseBrainstormingService(String desiredOutcome) {
            if (desiredOutcome == null || desiredOutcome.isBlank()) {
                throw new IllegalArgumentException(
                    "Desired outcome is required."
                );
            }

            this.desiredOutcome = desiredOutcome;
        }

        List<String> failureMechanisms() {
            return List.of(
                "Route every request to one queue regardless of skill.",
                "Hide response expectations from customers.",
                "Require approval for every support decision.",
                "Copy customer information manually at every handoff.",
                "Measure closure count while ignoring reopened cases.",
                "Allow aging cases to remain mixed with new cases."
            );
        }

        List<Idea> createCountermeasures() {
            Map<String, String> inversions = Map.of(
                "Route every request to one queue regardless of skill.",
                "Route according to skill, urgency, and workload.",
                "Hide response expectations from customers.",
                "Expose realistic response windows and progress updates.",
                "Require approval for every support decision.",
                "Reserve approval for exceptions and high-risk cases.",
                "Copy customer information manually at every handoff.",
                "Maintain one shared case record through the workflow.",
                "Measure closure count while ignoring reopened cases.",
                "Track speed together with resolution quality and reopening.",
                "Allow aging cases to remain mixed with new cases.",
                "Use aging thresholds and explicit escalation paths."
            );

            return failureMechanisms().stream()
                .map(failure -> new Idea(
                    "Countermeasure",
                    inversions.get(failure),
                    Technique.REVERSE_BRAINSTORMING,
                    4,
                    4,
                    5,
                    4,
                    Set.of("failure-analysis", "countermeasure")
                ))
                .toList();
        }
    }

    // -----------------------------------------------------------------------
    // Evaluation service
    // -----------------------------------------------------------------------

    static final class EvaluationService {

        List<Idea> deduplicate(List<Idea> ideas) {
            Set<String> seen = new LinkedHashSet<>();
            List<Idea> result = new ArrayList<>();

            for (Idea idea : ideas) {
                String normalized =
                    idea.description().trim().toLowerCase();

                if (seen.add(normalized)) {
                    result.add(idea);
                }
            }

            return List.copyOf(result);
        }

        List<Idea> rank(List<Idea> ideas) {
            return ideas.stream()
                .sorted(
                    Comparator.comparingDouble(Idea::score)
                        .reversed()
                )
                .toList();
        }

        Map<Technique, Double> averageScoreByTechnique(
            List<Idea> ideas
        ) {
            Map<Technique, List<Idea>> groups =
                ideas.stream()
                    .collect(
                        Collectors.groupingBy(
                            Idea::technique,
                            () -> new EnumMap<>(Technique.class),
                            Collectors.toList()
                        )
                    );

            Map<Technique, Double> result =
                new EnumMap<>(Technique.class);

            groups.forEach(
                (technique, techniqueIdeas) ->
                    result.put(
                        technique,
                        techniqueIdeas.stream()
                            .mapToDouble(Idea::score)
                            .average()
                            .orElse(0)
                    )
            );

            return result;
        }

        List<Idea> balancedPortfolio(
            List<Idea> ideas,
            int limit
        ) {
            if (limit <= 0) {
                throw new IllegalArgumentException(
                    "Portfolio limit must be positive."
                );
            }

            List<Idea> ranked = rank(
                deduplicate(ideas)
            );

            List<Idea> selected = new ArrayList<>();
            Set<Technique> represented =
                EnumSet.noneOf(Technique.class);

            for (Idea idea : ranked) {
                if (selected.size() >= limit) {
                    break;
                }

                if (!represented.contains(idea.technique())) {
                    selected.add(idea);
                    represented.add(idea.technique());
                }
            }

            for (Idea idea : ranked) {
                if (selected.size() >= limit) {
                    break;
                }

                if (!selected.contains(idea)) {
                    selected.add(idea);
                }
            }

            return List.copyOf(selected);
        }
    }

    // -----------------------------------------------------------------------
    // Output
    // -----------------------------------------------------------------------

    static void printIdeas(
        String title,
        List<Idea> ideas,
        int limit
    ) {
        System.out.println("\n" + title);
        System.out.println("-".repeat(title.length()));

        for (int i = 0; i < Math.min(limit, ideas.size()); i++) {
            Idea idea = ideas.get(i);

            System.out.printf(
                "%d. %s%n   %s%n   score=%.2f | novelty=%d | "
                    + "feasibility=%d | impact=%d%n",
                i + 1,
                idea.title(),
                idea.description(),
                idea.score(),
                idea.novelty(),
                idea.feasibility(),
                idea.impact()
            );
        }
    }

    // -----------------------------------------------------------------------
    // Main enterprise workflow
    // -----------------------------------------------------------------------

    public static void main(String[] args) {

        String problem =
            "Reduce customer support response time without reducing "
                + "resolution quality.";

        System.out.println("IDEATION TECHNIQUES");
        System.out.println("===================");
        System.out.println("Challenge: " + problem);

        List<Participant> participants = List.of(
            new Participant(
                "Asha",
                Perspective.CUSTOMER,
                Set.of("service-design")
            ),
            new Participant(
                "Ravi",
                Perspective.SUPPORT_AGENT,
                Set.of("support")
            ),
            new Participant(
                "Meera",
                Perspective.OPERATIONS,
                Set.of("operations")
            ),
            new Participant(
                "Kabir",
                Perspective.TECHNOLOGY,
                Set.of("automation")
            ),
            new Participant(
                "Nisha",
                Perspective.QUALITY,
                Set.of("quality")
            )
        );

        List<Idea> allIdeas = new ArrayList<>();

        // Brainstorming produces contributions independently and postpones
        // selection so that early evaluation does not narrow the search.
        BrainstormingService brainstorming =
            new BrainstormingService(problem, participants);

        List<Idea> brainstormingIdeas =
            brainstorming.generate();

        allIdeas.addAll(brainstormingIdeas);
        allIdeas.add(
            brainstorming.buildOn(
                brainstormingIdeas.get(0)
            )
        );

        printIdeas(
            "Brainstorming",
            brainstormingIdeas,
            5
        );

        // Crazy 8s creates exactly eight directions because the constraint
        // itself is part of the technique.
        Crazy8sService crazy8s =
            new Crazy8sService(
                "Reduce response time without adding permanent headcount."
            );

        List<Idea> crazyIdeas = crazy8s.generate();
        allIdeas.addAll(crazyIdeas);

        printIdeas(
            "Crazy 8s",
            crazyIdeas,
            8
        );

        // SCAMPER is transformation-oriented and therefore starts from an
        // existing concept rather than from a blank problem statement.
        ScamperService scamper =
            new ScamperService(
                "A conventional manually triaged support queue"
            );

        List<Idea> scamperIdeas = scamper.generate();
        allIdeas.addAll(scamperIdeas);

        printIdeas(
            "SCAMPER",
            scamperIdeas,
            7
        );

        // The mind map models associations and hierarchy explicitly.
        MindMapService mindMap =
            new MindMapService("Slow customer support response");

        mindMap.build();

        System.out.println("\nMind Map");
        System.out.println("--------");
        mindMap.print();
        System.out.println("Map depth: " + mindMap.depth());

        List<Idea> mappedIdeas = mindMap.toIdeas();
        allIdeas.addAll(mappedIdeas);

        // Reverse brainstorming first models undesirable behavior and then
        // turns each mechanism into a prevention or improvement action.
        ReverseBrainstormingService reverse =
            new ReverseBrainstormingService(
                "Fast and reliable support response"
            );

        System.out.println(
            "\nReverse Brainstorming Failure Mechanisms"
        );
        System.out.println(
            "----------------------------------------"
        );

        reverse.failureMechanisms()
            .forEach(failure -> System.out.println("- " + failure));

        List<Idea> reverseIdeas =
            reverse.createCountermeasures();

        allIdeas.addAll(reverseIdeas);

        printIdeas(
            "Reverse Brainstorming Countermeasures",
            reverseIdeas,
            6
        );

        EvaluationService evaluator =
            new EvaluationService();

        List<Idea> uniqueIdeas =
            evaluator.deduplicate(allIdeas);

        List<Idea> ranked =
            evaluator.rank(uniqueIdeas);

        printIdeas(
            "Highest-ranked concepts",
            ranked,
            10
        );

        System.out.println("\nAverage score by technique");
        System.out.println("--------------------------");

        evaluator.averageScoreByTechnique(uniqueIdeas)
            .forEach(
                (technique, average) ->
                    System.out.printf(
                        "%-28s %.2f%n",
                        technique,
                        average
                    )
            );

        List<Idea> portfolio =
            evaluator.balancedPortfolio(uniqueIdeas, 6);

        printIdeas(
            "Balanced concept portfolio",
            portfolio,
            portfolio.size()
        );

        System.out.println("\nImplementation distinctions");
        System.out.println("---------------------------");
        System.out.println(
            "Brainstorming: participant-driven divergence with delayed evaluation."
        );
        System.out.println(
            "Crazy 8s: rapid generation constrained to eight directions."
        );
        System.out.println(
            "SCAMPER: structured transformation of an existing concept."
        );
        System.out.println(
            "Mind Mapping: hierarchical association around a central problem."
        );
        System.out.println(
            "Reverse Brainstorming: failure-first analysis followed by inversion."
        );

        // Enterprise validation example: malformed domain objects are
        // rejected at construction time rather than entering the workflow.
        System.out.println("\nValidation");
        System.out.println("----------");

        try {
            new Idea(
                "",
                "Invalid idea",
                Technique.BRAINSTORMING,
                3,
                3,
                3,
                3,
                Set.of()
            );
        } catch (IllegalArgumentException exception) {
            System.out.println(
                "Invalid idea rejected: "
                    + exception.getMessage()
            );
        }
    }
}
