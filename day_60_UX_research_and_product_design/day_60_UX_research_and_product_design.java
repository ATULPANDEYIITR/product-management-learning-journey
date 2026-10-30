import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/*
 * Enterprise-oriented UX research and product-design workflow.
 *
 * Java 17 features used:
 * records, immutable collection snapshots, domain-specific exceptions,
 * interfaces, streams, explicit lifecycle transitions, and policy evaluation.
 */

public class UxResearchProductDesign {

    enum ProjectPhase {
        DISCOVERY,
        SYNTHESIZED,
        DESIGN,
        VALIDATED
    }

    enum Severity {
        LOW,
        MEDIUM,
        HIGH,
        CRITICAL
    }

    static final class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    record Evidence(
        String id,
        String participantReference,
        String observation,
        int severity,
        double confidence,
        String method
    ) {
        Evidence {
            requireText(id, "Evidence ID");
            requireText(participantReference, "Participant reference");
            requireText(observation, "Observation");
            requireText(method, "Research method");

            if (observation.length() > 600) {
                throw new DomainException("Observation exceeds 600 characters.");
            }
            if (severity < 1 || severity > 5) {
                throw new DomainException("Severity must be between 1 and 5.");
            }
            if (!Double.isFinite(confidence) || confidence < 0 || confidence > 1) {
                throw new DomainException("Confidence must be between 0 and 1.");
            }
            if (!Set.of("interview", "survey", "observation", "usability_test")
                    .contains(method)) {
                throw new DomainException("Unsupported research method.");
            }
        }
    }

    record Theme(
        String id,
        String name,
        Set<String> evidenceIds,
        double effortHours
    ) {
        Theme {
            requireText(id, "Theme ID");
            requireText(name, "Theme name");
            evidenceIds = Set.copyOf(evidenceIds);

            if (evidenceIds.isEmpty()) {
                throw new DomainException("A theme requires evidence references.");
            }
            if (!Double.isFinite(effortHours) || effortHours <= 0) {
                throw new DomainException("Theme effort must be positive.");
            }
        }
    }

    record ThemeScore(
        String themeName,
        int evidenceCount,
        double averageSeverity,
        double averageConfidence,
        double effortHours,
        double priorityScore
    ) {}

    record ComponentSpec(
        String name,
        boolean interactive,
        boolean keyboardAccessible,
        String accessibleDescription
    ) {
        ComponentSpec {
            requireText(name, "Component name");
            requireText(accessibleDescription, "Accessible description");
        }
    }

    record Screen(
        String id,
        String title,
        String accessibleName,
        List<String> components,
        List<String> keyboardOrder,
        Set<String> requiredTokens
    ) {
        Screen {
            requireText(id, "Screen ID");
            requireText(title, "Screen title");
            requireText(accessibleName, "Accessible screen name");
            components = List.copyOf(components);
            keyboardOrder = List.copyOf(keyboardOrder);
            requiredTokens = Set.copyOf(requiredTokens);

            if (components.isEmpty()) {
                throw new DomainException("A screen must contain components.");
            }
        }
    }

    record UsabilityResult(
        String participantReference,
        String taskName,
        String screenId,
        boolean succeeded,
        double durationSeconds,
        int criticalErrors
    ) {
        UsabilityResult {
            requireText(participantReference, "Participant reference");
            requireText(taskName, "Task name");
            requireText(screenId, "Screen ID");

            if (!Double.isFinite(durationSeconds) || durationSeconds <= 0) {
                throw new DomainException("Task duration must be positive.");
            }
            if (criticalErrors < 0) {
                throw new DomainException("Critical errors cannot be negative.");
            }
        }
    }

    record CritiqueIssue(
        String id,
        String screenId,
        String heuristic,
        Severity severity,
        String description,
        String recommendation,
        boolean resolved
    ) {
        CritiqueIssue {
            requireText(id, "Critique ID");
            requireText(screenId, "Screen ID");
            requireText(heuristic, "Heuristic");
            requireText(description, "Description");
            requireText(recommendation, "Recommendation");
            Objects.requireNonNull(severity, "Severity is required.");
        }
    }

    static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new DomainException(field + " must not be empty.");
        }
    }

    static double relativeLuminance(String color) {
        if (color == null || !color.matches("#[0-9a-fA-F]{6}")) {
            throw new DomainException("Invalid hexadecimal color: " + color);
        }

        int red = Integer.parseInt(color.substring(1, 3), 16);
        int green = Integer.parseInt(color.substring(3, 5), 16);
        int blue = Integer.parseInt(color.substring(5, 7), 16);

        double[] channels = {red / 255.0, green / 255.0, blue / 255.0};
        double[] linear = new double[3];

        for (int index = 0; index < channels.length; index++) {
            double value = channels[index];
            linear[index] = value <= 0.04045
                ? value / 12.92
                : Math.pow((value + 0.055) / 1.055, 2.4);
        }

        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
    }

    static double contrastRatio(String foreground, String background) {
        double first = relativeLuminance(foreground);
        double second = relativeLuminance(background);
        return (Math.max(first, second) + 0.05)
            / (Math.min(first, second) + 0.05);
    }

    static final class DesignSystem {
        private final Map<String, String> tokens;
        private final Map<String, ComponentSpec> components;
        private final List<List<String>> contrastPairs;

        DesignSystem(
            Map<String, String> tokens,
            Map<String, ComponentSpec> components,
            List<List<String>> contrastPairs
        ) {
            this.tokens = Map.copyOf(tokens);
            this.components = Map.copyOf(components);
            this.contrastPairs = contrastPairs.stream()
                .map(List::copyOf)
                .toList();
        }

        List<String> validate() {
            List<String> errors = new ArrayList<>();

            for (List<String> pair : contrastPairs) {
                String foreground = tokens.get(pair.get(0));
                String background = tokens.get(pair.get(1));

                if (foreground == null || background == null) {
                    errors.add("Missing contrast token pair: " + pair);
                    continue;
                }

                try {
                    double ratio = contrastRatio(foreground, background);
                    if (ratio < 4.5) {
                        errors.add(
                            "Contrast below 4.5:1 for " + pair
                                + " (" + String.format("%.2f", ratio) + ":1)."
                        );
                    }
                } catch (DomainException exception) {
                    errors.add(exception.getMessage());
                }
            }

            return errors;
        }

        List<String> validateScreen(Screen screen) {
            List<String> errors = new ArrayList<>();
            List<String> expectedKeyboardOrder = new ArrayList<>();

            if (new HashSet<>(screen.components()).size() != screen.components().size()) {
                errors.add(screen.id() + ": duplicate component in layout.");
            }

            for (String componentName : screen.components()) {
                ComponentSpec component = components.get(componentName);

                if (component == null) {
                    errors.add(screen.id() + ": unknown component " + componentName);
                    continue;
                }

                if (!component.keyboardAccessible()) {
                    errors.add(screen.id() + ": " + componentName + " is not keyboard accessible.");
                }
                if (component.accessibleDescription().isBlank()) {
                    errors.add(screen.id() + ": " + componentName + " lacks accessible description.");
                }
                if (component.interactive()) {
                    expectedKeyboardOrder.add(componentName);
                }
            }

            if (!expectedKeyboardOrder.equals(screen.keyboardOrder())) {
                errors.add(screen.id() + ": keyboard order differs from interactive layout order.");
            }

            for (String token : screen.requiredTokens()) {
                if (!tokens.containsKey(token)) {
                    errors.add(screen.id() + ": missing design token " + token);
                }
            }

            return errors;
        }
    }

    static final class UXProject {
        private final String name;
        private final DesignSystem designSystem;

        private ProjectPhase phase = ProjectPhase.DISCOVERY;
        private final Map<String, Evidence> evidence = new LinkedHashMap<>();
        private final Map<String, Theme> themes = new LinkedHashMap<>();
        private final Map<String, Screen> screens = new LinkedHashMap<>();
        private final List<UsabilityResult> usabilityResults = new ArrayList<>();
        private final Map<String, CritiqueIssue> critiques = new LinkedHashMap<>();

        UXProject(String name, DesignSystem designSystem) {
            requireText(name, "Project name");
            this.name = name;
            this.designSystem = Objects.requireNonNull(designSystem);
        }

        ProjectPhase phase() {
            return phase;
        }

        String name() {
            return name;
        }

        void addEvidence(Evidence item) {
            requirePhase(ProjectPhase.DISCOVERY, "Evidence intake");
            if (evidence.putIfAbsent(item.id(), item) != null) {
                throw new DomainException("Duplicate evidence ID: " + item.id());
            }
        }

        void addTheme(Theme theme) {
            requirePhase(ProjectPhase.DISCOVERY, "Theme definition");

            if (themes.containsKey(theme.id())) {
                throw new DomainException("Duplicate theme ID: " + theme.id());
            }

            Set<String> missing = theme.evidenceIds().stream()
                .filter(id -> !evidence.containsKey(id))
                .collect(Collectors.toSet());

            if (!missing.isEmpty()) {
                throw new DomainException("Theme references unknown evidence: " + missing);
            }

            themes.put(theme.id(), theme);
        }

        private void requirePhase(ProjectPhase expected, String operation) {
            if (phase != expected) {
                throw new DomainException(
                    operation + " is not permitted during phase " + phase
                );
            }
        }

        List<ThemeScore> synthesize() {
            requirePhase(ProjectPhase.DISCOVERY, "Synthesis");

            if (evidence.size() < 3 || themes.size() < 2) {
                throw new DomainException(
                    "Synthesis requires three evidence records and two themes."
                );
            }

            List<ThemeScore> scores = themes.values().stream()
                .map(theme -> {
                    List<Evidence> linked = theme.evidenceIds().stream()
                        .map(evidence::get)
                        .toList();

                    double averageSeverity = linked.stream()
                        .mapToInt(Evidence::severity)
                        .average()
                        .orElse(0.0);

                    double averageConfidence = linked.stream()
                        .mapToDouble(Evidence::confidence)
                        .average()
                        .orElse(0.0);

                    double priority = linked.size()
                        * averageSeverity
                        * averageConfidence
                        / theme.effortHours();

                    return new ThemeScore(
                        theme.name(),
                        linked.size(),
                        averageSeverity,
                        averageConfidence,
                        theme.effortHours(),
                        priority
                    );
                })
                .sorted(Comparator.comparingDouble(ThemeScore::priorityScore).reversed())
                .toList();

            phase = ProjectPhase.SYNTHESIZED;
            return scores;
        }

        void startDesign() {
            requirePhase(ProjectPhase.SYNTHESIZED, "Design transition");
            phase = ProjectPhase.DESIGN;
        }

        void addScreen(Screen screen) {
            requirePhase(ProjectPhase.DESIGN, "Screen registration");

            if (screens.containsKey(screen.id())) {
                throw new DomainException("Duplicate screen ID: " + screen.id());
            }

            List<String> errors = designSystem.validateScreen(screen);
            if (!errors.isEmpty()) {
                throw new DomainException(String.join("; ", errors));
            }

            screens.put(screen.id(), screen);
        }

        void recordUsabilityResult(UsabilityResult result) {
            requirePhase(ProjectPhase.DESIGN, "Usability result registration");

            if (!screens.containsKey(result.screenId())) {
                throw new DomainException("Usability result references an unknown screen.");
            }
            usabilityResults.add(result);
        }

        void addCritique(CritiqueIssue issue) {
            if (!screens.containsKey(issue.screenId())) {
                throw new DomainException("Critique references an unknown screen.");
            }
            if (critiques.putIfAbsent(issue.id(), issue) != null) {
                throw new DomainException("Duplicate critique ID: " + issue.id());
            }
        }

        void resolveCritique(String issueId) {
            CritiqueIssue issue = critiques.get(issueId);
            if (issue == null) {
                throw new DomainException("Unknown critique: " + issueId);
            }

            critiques.put(
                issueId,
                new CritiqueIssue(
                    issue.id(),
                    issue.screenId(),
                    issue.heuristic(),
                    issue.severity(),
                    issue.description(),
                    issue.recommendation(),
                    true
                )
            );
        }

        List<String> structuralBlockers() {
            List<String> blockers = new ArrayList<>(designSystem.validate());

            for (Screen screen : screens.values()) {
                blockers.addAll(designSystem.validateScreen(screen));
            }
            return blockers;
        }

        List<String> usabilityBlockers() {
            List<String> blockers = new ArrayList<>();

            if (usabilityResults.size() < 5) {
                blockers.add("At least five usability task results are required.");
            }

            long successful = usabilityResults.stream()
                .filter(UsabilityResult::succeeded)
                .count();

            double successRate = usabilityResults.isEmpty()
                ? 0.0
                : (double) successful / usabilityResults.size();

            if (successRate < 0.80) {
                blockers.add("Task success rate is below 80%.");
            }

            int criticalErrors = usabilityResults.stream()
                .mapToInt(UsabilityResult::criticalErrors)
                .sum();

            if (criticalErrors > 0) {
                blockers.add("Prototype testing recorded critical errors.");
            }

            return blockers;
        }

        List<String> critiqueBlockers() {
            return critiques.values().stream()
                .filter(issue -> issue.severity() == Severity.CRITICAL && !issue.resolved())
                .map(issue -> "Unresolved critical critique: " + issue.id())
                .toList();
        }

        double taskSuccessRate() {
            if (usabilityResults.isEmpty()) {
                return 0.0;
            }

            return (double) usabilityResults.stream()
                .filter(UsabilityResult::succeeded)
                .count() / usabilityResults.size();
        }

        double averageTaskDuration() {
            return usabilityResults.stream()
                .mapToDouble(UsabilityResult::durationSeconds)
                .average()
                .orElse(0.0);
        }

        int criticalErrorCount() {
            return usabilityResults.stream()
                .mapToInt(UsabilityResult::criticalErrors)
                .sum();
        }

        int screenCount() {
            return screens.size();
        }

        int taskCount() {
            return usabilityResults.size();
        }
    }

    interface ReadinessPolicy {
        List<String> evaluate(UXProject project);
    }

    static final class DefaultReadinessPolicy implements ReadinessPolicy {
        @Override
        public List<String> evaluate(UXProject project) {
            List<String> blockers = new ArrayList<>();

            if (project.screenCount() < 2) {
                blockers.add("At least two screens are required.");
            }

            blockers.addAll(project.structuralBlockers());
            blockers.addAll(project.usabilityBlockers());
            blockers.addAll(project.critiqueBlockers());

            return List.copyOf(blockers);
        }
    }

    record ReadinessReport(
        String project,
        ProjectPhase phase,
        boolean eligible,
        List<String> blockers,
        int screens,
        int usabilityTasks,
        double successRate,
        double averageDurationSeconds,
        int criticalErrors
    ) {
        ReadinessReport {
            blockers = List.copyOf(blockers);
        }
    }

    static final class GovernanceService {
        private final ReadinessPolicy policy;

        GovernanceService(ReadinessPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        ReadinessReport evaluate(UXProject project) {
            if (project.phase() != ProjectPhase.DESIGN) {
                throw new DomainException("Readiness evaluation requires the design phase.");
            }

            List<String> blockers = policy.evaluate(project);
            boolean eligible = blockers.isEmpty();

            if (eligible) {
                project.phase = ProjectPhase.VALIDATED;
            }

            return new ReadinessReport(
                project.name(),
                project.phase(),
                eligible,
                blockers,
                project.screenCount(),
                project.taskCount(),
                project.taskSuccessRate(),
                project.averageTaskDuration(),
                project.criticalErrorCount()
            );
        }
    }

    static DesignSystem createDesignSystem() {
        Map<String, String> tokens = Map.of(
            "color.text", "#17212B",
            "color.surface", "#FFFFFF",
            "color.action", "#1247A8",
            "space.medium", "16px"
        );

        Map<String, ComponentSpec> components = Map.of(
            "SearchField",
            new ComponentSpec(
                "SearchField", true, true, "Origin and destination input"
            ),
            "PrimaryButton",
            new ComponentSpec(
                "PrimaryButton", true, true, "Submit route search"
            ),
            "RouteCard",
            new ComponentSpec(
                "RouteCard", true, true, "Selectable journey option"
            )
        );

        return new DesignSystem(
            tokens,
            components,
            List.of(
                List.of("color.text", "color.surface"),
                List.of("color.action", "color.surface")
            )
        );
    }

    static UXProject createExampleProject() {
        UXProject project = new UXProject(
            "City Transit Companion",
            createDesignSystem()
        );

        List<Evidence> evidence = List.of(
            new Evidence("E01", "P-001", "Transfer requirements are unclear.", 5, 0.95, "interview"),
            new Evidence("E02", "P-002", "Transfer points are difficult to identify.", 4, 0.90, "observation"),
            new Evidence("E03", "P-003", "Users compare journeys by total time.", 3, 0.85, "interview"),
            new Evidence("E04", "P-004", "The complete fare is difficult to locate.", 5, 0.95, "interview"),
            new Evidence("E05", "P-005", "Fare presentation is inconsistent.", 4, 0.90, "survey"),
            new Evidence("E06", "P-006", "Users need to compare fare categories.", 3, 0.85, "observation")
        );

        evidence.forEach(project::addEvidence);

        project.addTheme(
            new Theme("T01", "Transfer uncertainty", Set.of("E01", "E02", "E03"), 8.0)
        );
        project.addTheme(
            new Theme("T02", "Fare transparency", Set.of("E04", "E05", "E06"), 5.0)
        );

        return project;
    }

    public static void main(String[] args) {
        try {
            UXProject project = createExampleProject();

            System.out.println("RESEARCH SYNTHESIS");
            project.synthesize().forEach(score ->
                System.out.printf(
                    "%s | evidence=%d | confidence=%.2f | priority=%.3f%n",
                    score.themeName(),
                    score.evidenceCount(),
                    score.averageConfidence(),
                    score.priorityScore()
                )
            );

            project.startDesign();

            project.addScreen(new Screen(
                "S01",
                "Route search",
                "Search for a public transport journey",
                List.of("SearchField", "PrimaryButton"),
                List.of("SearchField", "PrimaryButton"),
                Set.of("color.text", "color.surface", "color.action")
            ));

            project.addScreen(new Screen(
                "S02",
                "Route results",
                "Available journey options",
                List.of("RouteCard", "PrimaryButton"),
                List.of("RouteCard", "PrimaryButton"),
                Set.of("color.text", "color.surface", "color.action")
            ));

            project.addCritique(new CritiqueIssue(
                "C01",
                "S02",
                "Visibility of system status",
                Severity.MEDIUM,
                "The selected route is not visually persistent.",
                "Provide a selected state and accessible announcement.",
                false
            ));

            project.addCritique(new CritiqueIssue(
                "C02",
                "S01",
                "Error prevention",
                Severity.CRITICAL,
                "The prototype initially accepted an empty origin.",
                "Validate the origin before route calculation.",
                false
            ));
            project.resolveCritique("C02");

            List<UsabilityResult> testResults = List.of(
                new UsabilityResult("P-007", "Find fastest route", "S01", true, 62, 0),
                new UsabilityResult("P-008", "Compare journey options", "S02", true, 75, 0),
                new UsabilityResult("P-009", "Identify transfers", "S02", true, 81, 0),
                new UsabilityResult("P-010", "Find complete fare", "S02", false, 110, 0),
                new UsabilityResult("P-011", "Search return journey", "S01", true, 69, 0)
            );

            testResults.forEach(project::recordUsabilityResult);

            GovernanceService governance = new GovernanceService(
                new DefaultReadinessPolicy()
            );

            ReadinessReport report = governance.evaluate(project);

            System.out.println("\nDESIGN GOVERNANCE REPORT");
            System.out.println("Project: " + report.project());
            System.out.println("Phase: " + report.phase());
            System.out.println("Eligible: " + report.eligible());
            System.out.printf("Task success: %.1f%%%n", report.successRate() * 100);
            System.out.printf("Average duration: %.1f seconds%n", report.averageDurationSeconds());
            System.out.println("Critical errors: " + report.criticalErrors());

            report.blockers().forEach(blocker ->
                System.out.println("BLOCKER: " + blocker)
            );

            if (!report.eligible()) {
                System.exit(2);
            }

            // Verify that the domain rejects lifecycle violations.
            boolean transitionRejected = false;
            try {
                project.startDesign();
            } catch (DomainException expected) {
                transitionRejected = true;
            }

            if (!transitionRejected) {
                throw new DomainException("Invalid lifecycle transition was not rejected.");
            }

        } catch (DomainException exception) {
            System.err.println("UX workflow failed: " + exception.getMessage());
            System.exit(1);
        }
    }
}
