import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class UXFundamentals {

    enum Severity {
        INFO,
        MINOR,
        MAJOR,
        CRITICAL
    }

    enum IssueType {
        UI,
        USABILITY,
        ACCESSIBILITY,
        INTERACTION,
        INFORMATION_ARCHITECTURE
    }

    enum ControlType {
        BUTTON,
        LINK,
        INPUT,
        CHECKBOX,
        SELECT
    }

    record Control(
        String id,
        String accessibleName,
        ControlType type,
        boolean keyboardReachable
    ) {
        Control {
            Objects.requireNonNull(id);
            Objects.requireNonNull(type);

            if (id.isBlank()) {
                throw new DomainException("Control id cannot be blank.");
            }
        }
    }

    record UXIssue(
        IssueType type,
        Severity severity,
        String screenId,
        String description,
        String recommendation
    ) {}

    record TaskResult(
        String name,
        boolean completed,
        double durationSeconds,
        int steps,
        int errors
    ) {
        TaskResult {
            if (name == null || name.isBlank()) {
                throw new DomainException("Task name is required.");
            }

            if (durationSeconds < 0 || steps <= 0 || errors < 0 || errors > steps) {
                throw new DomainException("Invalid task measurements.");
            }
        }
    }

    record UXScreen(
        String id,
        String title,
        List<String> navigation,
        String primaryAction,
        List<Control> controls,
        Map<String, Double> contrastRatios,
        List<String> contentSections
    ) {
        UXScreen {
            Objects.requireNonNull(id);
            Objects.requireNonNull(title);
            Objects.requireNonNull(navigation);
            Objects.requireNonNull(primaryAction);
            Objects.requireNonNull(controls);
            Objects.requireNonNull(contrastRatios);
            Objects.requireNonNull(contentSections);

            if (id.isBlank() || title.isBlank()) {
                throw new DomainException("Screen id and title are required.");
            }

            if (controls.isEmpty()) {
                throw new DomainException("A screen must contain controls.");
            }

            navigation = List.copyOf(navigation);
            controls = List.copyOf(controls);
            contrastRatios = Map.copyOf(contrastRatios);
            contentSections = List.copyOf(contentSections);
        }
    }

    record UsabilityMetrics(
        double completionRate,
        double averageDurationSeconds,
        double errorRate
    ) {}

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    interface UXRule {
        List<UXIssue> evaluate(UXScreen screen);
    }

    static class AccessibilityRule implements UXRule {
        @Override
        public List<UXIssue> evaluate(UXScreen screen) {
            List<UXIssue> issues = new ArrayList<>();

            for (Control control : screen.controls()) {
                if (control.accessibleName() == null ||
                    control.accessibleName().isBlank()) {
                    issues.add(new UXIssue(
                        IssueType.ACCESSIBILITY,
                        Severity.MAJOR,
                        screen.id(),
                        "Control '" + control.id() + "' has no accessible name.",
                        "Provide a meaningful visible or programmatic accessible name."
                    ));
                }

                if (!control.keyboardReachable()) {
                    issues.add(new UXIssue(
                        IssueType.ACCESSIBILITY,
                        Severity.CRITICAL,
                        screen.id(),
                        "Control '" + control.id() + "' is not keyboard reachable.",
                        "Make the control available through keyboard interaction."
                    ));
                }
            }

            for (Map.Entry<String, Double> entry :
                    screen.contrastRatios().entrySet()) {
                if (entry.getValue() < 4.5) {
                    issues.add(new UXIssue(
                        IssueType.ACCESSIBILITY,
                        Severity.MAJOR,
                        screen.id(),
                        "Contrast ratio for '" + entry.getKey()
                            + "' is below 4.5:1.",
                        "Increase contrast to meet the applicable accessibility threshold."
                    ));
                }
            }

            return issues;
        }
    }

    static class InformationArchitectureRule implements UXRule {
        @Override
        public List<UXIssue> evaluate(UXScreen screen) {
            List<UXIssue> issues = new ArrayList<>();

            if (screen.navigation().size() > 7) {
                issues.add(new UXIssue(
                    IssueType.INFORMATION_ARCHITECTURE,
                    Severity.MINOR,
                    screen.id(),
                    "Primary navigation has more than seven top-level destinations.",
                    "Group related destinations and reduce navigation breadth."
                ));
            }

            Set<String> sections = new HashSet<>(screen.contentSections());

            if (sections.size() != screen.contentSections().size()) {
                issues.add(new UXIssue(
                    IssueType.INFORMATION_ARCHITECTURE,
                    Severity.MINOR,
                    screen.id(),
                    "Content section labels are duplicated.",
                    "Use distinct labels that communicate information structure."
                ));
            }

            return issues;
        }
    }

    static class InteractionRule implements UXRule {
        @Override
        public List<UXIssue> evaluate(UXScreen screen) {
            boolean primaryActionExists = screen.controls()
                .stream()
                .anyMatch(control -> control.id().equals(screen.primaryAction()));

            if (!primaryActionExists) {
                return List.of(new UXIssue(
                    IssueType.INTERACTION,
                    Severity.MAJOR,
                    screen.id(),
                    "Primary action is not represented by a control.",
                    "Expose the primary task as an actionable control."
                ));
            }

            return List.of();
        }
    }

    static class UsabilityRule implements UXRule {
        @Override
        public List<UXIssue> evaluate(UXScreen screen) {
            if (screen.contentSections().isEmpty()) {
                return List.of(new UXIssue(
                    IssueType.USABILITY,
                    Severity.MAJOR,
                    screen.id(),
                    "No content grouping is defined.",
                    "Establish a clear hierarchy for the information on the screen."
                ));
            }

            return List.of();
        }
    }

    static class UXPolicy {
        private final List<UXRule> rules = List.of(
            new AccessibilityRule(),
            new InformationArchitectureRule(),
            new InteractionRule(),
            new UsabilityRule()
        );

        List<UXIssue> evaluate(UXScreen screen) {
            return rules.stream()
                .flatMap(rule -> rule.evaluate(screen).stream())
                .toList();
        }
    }

    static class UXService {
        private final Map<String, UXScreen> screens = new HashMap<>();
        private final UXPolicy policy = new UXPolicy();

        void registerScreen(UXScreen screen) {
            if (screens.containsKey(screen.id())) {
                throw new DomainException(
                    "Screen already registered: " + screen.id()
                );
            }

            screens.put(screen.id(), screen);
        }

        List<UXIssue> audit() {
            return screens.values()
                .stream()
                .flatMap(screen -> policy.evaluate(screen).stream())
                .toList();
        }

        static UsabilityMetrics measure(List<TaskResult> tasks) {
            if (tasks.isEmpty()) {
                return new UsabilityMetrics(0, 0, 0);
            }

            long completed = tasks.stream()
                .filter(TaskResult::completed)
                .count();

            double duration = tasks.stream()
                .mapToDouble(TaskResult::durationSeconds)
                .sum();

            int steps = tasks.stream()
                .mapToInt(TaskResult::steps)
                .sum();

            int errors = tasks.stream()
                .mapToInt(TaskResult::errors)
                .sum();

            return new UsabilityMetrics(
                (double) completed / tasks.size(),
                duration / tasks.size(),
                (double) errors / Math.max(steps, 1)
            );
        }
    }

    static UXScreen dashboard() {
        return new UXScreen(
            "dashboard",
            "Project Dashboard",
            List.of(
                "Projects",
                "Reports",
                "Teams",
                "Activity",
                "Integrations",
                "Billing",
                "Settings",
                "Help"
            ),
            "Create project",
            List.of(
                new Control(
                    "Search",
                    "Search projects",
                    ControlType.INPUT,
                    true
                ),
                new Control(
                    "Create project",
                    "Create project",
                    ControlType.BUTTON,
                    true
                ),
                new Control(
                    "Open project",
                    "Open project",
                    ControlType.LINK,
                    true
                ),
                new Control(
                    "Account menu",
                    "Account menu",
                    ControlType.BUTTON,
                    true
                )
            ),
            Map.of(
                "body-text", 7.2,
                "muted-text", 3.3,
                "primary-button", 4.9
            ),
            List.of("Projects", "Recent activity")
        );
    }

    static UXScreen accountSettings() {
        return new UXScreen(
            "settings",
            "Account Settings",
            List.of("Projects", "Settings"),
            "Save",
            List.of(
                new Control(
                    "Account name",
                    "Account name",
                    ControlType.INPUT,
                    true
                ),
                new Control(
                    "Save",
                    "Save settings",
                    ControlType.BUTTON,
                    true
                ),
                new Control(
                    "Delete account",
                    "",
                    ControlType.BUTTON,
                    false
                )
            ),
            Map.of(
                "body-text", 8.1,
                "primary-button", 5.2
            ),
            List.of("Profile", "Security", "Account")
        );
    }

    static void printIssues(List<UXIssue> issues) {
        EnumMap<Severity, Integer> counts =
            new EnumMap<>(Severity.class);

        for (Severity severity : Severity.values()) {
            counts.put(severity, 0);
        }

        System.out.println("\n=== UX POLICY AUDIT ===");

        for (UXIssue issue : issues) {
            counts.merge(issue.severity(), 1, Integer::sum);

            System.out.printf(
                "[%s] %s [%s] %s%n",
                issue.severity(),
                issue.type(),
                issue.screenId(),
                issue.description()
            );

            System.out.println(
                "  Recommendation: " + issue.recommendation()
            );
        }

        System.out.println("\nIssue counts:");
        counts.forEach((severity, count) ->
            System.out.println(severity + ": " + count)
        );
    }

    public static void main(String[] args) {
        try {
            UXService service = new UXService();

            service.registerScreen(dashboard());
            service.registerScreen(accountSettings());

            List<UXIssue> issues = service.audit();
            printIssues(issues);

            List<TaskResult> tasks = List.of(
                new TaskResult(
                    "Find project",
                    true,
                    18.4,
                    5,
                    0
                ),
                new TaskResult(
                    "Create project",
                    true,
                    31.7,
                    7,
                    1
                ),
                new TaskResult(
                    "Change account settings",
                    false,
                    44.2,
                    8,
                    3
                )
            );

            UsabilityMetrics metrics =
                UXService.measure(tasks);

            System.out.println("\n=== USABILITY METRICS ===");
            System.out.printf(
                "Completion rate: %.2f%%%n",
                metrics.completionRate() * 100
            );
            System.out.printf(
                "Average task time: %.2f seconds%n",
                metrics.averageDurationSeconds()
            );
            System.out.printf(
                "Error rate: %.2f%%%n",
                metrics.errorRate() * 100
            );

            long criticalIssues = issues.stream()
                .filter(issue -> issue.severity() == Severity.CRITICAL)
                .count();

            System.out.println("\n=== RELEASE GATE ===");

            if (criticalIssues > 0) {
                System.out.println(
                    "BLOCKED: critical accessibility issues remain."
                );
            } else {
                System.out.println(
                    "PASS: no critical accessibility issues detected."
                );
            }
        } catch (DomainException exception) {
            System.err.println(
                "UX workflow failed: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
