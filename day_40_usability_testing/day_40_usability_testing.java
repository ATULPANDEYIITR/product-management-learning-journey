import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/*
 * Enterprise usability research and design-iteration governance.
 *
 * Compile and run:
 *   javac UsabilityTesting.java
 *   java UsabilityTesting
 *
 * Java 17+, standard library only.
 *
 * The domain model distinguishes a planned task, an observed session,
 * a measured outcome, an evidence-backed usability finding, and a release
 * decision. These objects have different validation and lifecycle rules.
 */

public class UsabilityTesting {

    enum Outcome {
        SUCCESS,
        PARTIAL,
        FAILURE,
        ABANDONED
    }

    enum Severity {
        COSMETIC(1),
        MINOR(2),
        MAJOR(3),
        CRITICAL(4);

        private final int weight;

        Severity(int weight) {
            this.weight = weight;
        }

        int weight() {
            return weight;
        }
    }

    enum EvidenceKind {
        OBSERVED,
        PARTICIPANT_REPORTED,
        INFERRED
    }

    enum FindingStatus {
        OPEN,
        IN_PROGRESS,
        FIXED,
        VERIFIED,
        ACCEPTED_RISK
    }

    enum ReleaseDecision {
        READY_FOR_NEXT_VALIDATION,
        REDESIGN_REQUIRED,
        INSUFFICIENT_EVIDENCE
    }

    record ResearchQuestion(
            String id,
            String question,
            String designDecision
    ) {
        ResearchQuestion {
            requireText(id, "Question ID");
            requireText(question, "Question");
            requireText(designDecision, "Design decision");
        }
    }

    record TaskDefinition(
            String id,
            String scenario,
            List<String> successCriteria,
            int timeLimitSeconds
    ) {
        TaskDefinition {
            requireText(id, "Task ID");
            requireText(scenario, "Task scenario");
            successCriteria = List.copyOf(successCriteria);
            if (successCriteria.isEmpty()) {
                throw new IllegalArgumentException(
                        "Tasks require observable success criteria."
                );
            }
            if (timeLimitSeconds <= 0) {
                throw new IllegalArgumentException(
                        "Time limit must be positive."
                );
            }
        }
    }

    record Participant(
            String id,
            String role,
            String experience,
            boolean consented
    ) {
        Participant {
            requireText(id, "Participant ID");
            requireText(role, "Participant role");
            requireText(experience, "Experience level");
            if (!consented) {
                throw new SecurityException(
                        "Enrollment requires recorded participant consent."
                );
            }
        }
    }

    record Observation(
            String id,
            String taskId,
            long elapsedMilliseconds,
            String event,
            String target,
            String description,
            EvidenceKind evidenceKind
    ) {
        Observation {
            requireText(id, "Observation ID");
            requireText(taskId, "Task ID");
            requireText(event, "Event");
            requireText(target, "Target");
            requireText(description, "Description");
            Objects.requireNonNull(evidenceKind, "Evidence kind");
            if (elapsedMilliseconds < 0) {
                throw new IllegalArgumentException(
                        "Observation time cannot be negative."
                );
            }
        }
    }

    record TaskResult(
            String participantId,
            String taskId,
            Outcome outcome,
            double durationSeconds,
            int errors,
            int assistanceRequests,
            Integer confidence,
            List<Observation> observations
    ) {
        TaskResult {
            requireText(participantId, "Participant ID");
            requireText(taskId, "Task ID");
            Objects.requireNonNull(outcome, "Outcome");
            observations = List.copyOf(observations);

            if (!Double.isFinite(durationSeconds) || durationSeconds < 0) {
                throw new IllegalArgumentException(
                        "Duration must be finite and non-negative."
                );
            }
            if (errors < 0 || assistanceRequests < 0) {
                throw new IllegalArgumentException(
                        "Counts cannot be negative."
                );
            }
            if (confidence != null && (confidence < 1 || confidence > 5)) {
                throw new IllegalArgumentException(
                        "Confidence must be between one and five."
                );
            }
            if (outcome == Outcome.SUCCESS || outcome == Outcome.PARTIAL) {
                if (durationSeconds == 0) {
                    throw new IllegalArgumentException(
                            "Completed task duration must be positive."
                    );
                }
            }
            for (Observation observation : observations) {
                if (!observation.taskId().equals(taskId)) {
                    throw new IllegalArgumentException(
                            "Observation belongs to another task."
                    );
                }
            }
        }
    }

    record ProblemEvidence(
            String reference,
            EvidenceKind kind,
            String statement
    ) {
        ProblemEvidence {
            requireText(reference, "Evidence reference");
            Objects.requireNonNull(kind, "Evidence kind");
            requireText(statement, "Evidence statement");
        }
    }

    static final class UsabilityFinding {
        private final String id;
        private final String title;
        private final String description;
        private final Severity severity;
        private final Set<String> affectedTaskIds;
        private final int participantFrequency;
        private final double impact;
        private final List<ProblemEvidence> evidence;
        private final String proposedChange;
        private FindingStatus status;

        UsabilityFinding(
                String id,
                String title,
                String description,
                Severity severity,
                Set<String> affectedTaskIds,
                int participantFrequency,
                double impact,
                List<ProblemEvidence> evidence,
                String proposedChange
        ) {
            requireText(id, "Finding ID");
            requireText(title, "Finding title");
            requireText(description, "Finding description");
            requireText(proposedChange, "Proposed change");
            this.severity = Objects.requireNonNull(severity, "Severity");
            this.affectedTaskIds = Set.copyOf(affectedTaskIds);
            this.evidence = List.copyOf(evidence);

            if (this.affectedTaskIds.isEmpty()) {
                throw new IllegalArgumentException(
                        "Findings must reference affected tasks."
                );
            }
            if (participantFrequency < 0) {
                throw new IllegalArgumentException(
                        "Frequency cannot be negative."
                );
            }
            if (!Double.isFinite(impact) || impact < 0 || impact > 1) {
                throw new IllegalArgumentException(
                        "Impact must be between zero and one."
                );
            }
            if (this.evidence.isEmpty()) {
                throw new IllegalArgumentException(
                        "Findings require supporting evidence."
                );
            }

            this.id = id;
            this.title = title;
            this.description = description;
            this.participantFrequency = participantFrequency;
            this.impact = impact;
            this.proposedChange = proposedChange;
            this.status = FindingStatus.OPEN;
        }

        double priorityScore() {
            return severity.weight()
                    * Math.log1p(participantFrequency)
                    * impact;
        }

        void transitionTo(FindingStatus next) {
            Objects.requireNonNull(next, "Next finding status");

            // Fixing an issue and verifying a fix are distinct research states.
            boolean allowed = switch (status) {
                case OPEN -> next == FindingStatus.IN_PROGRESS
                        || next == FindingStatus.ACCEPTED_RISK;
                case IN_PROGRESS -> next == FindingStatus.FIXED
                        || next == FindingStatus.OPEN;
                case FIXED -> next == FindingStatus.VERIFIED
                        || next == FindingStatus.IN_PROGRESS;
                case VERIFIED -> next == FindingStatus.IN_PROGRESS;
                case ACCEPTED_RISK -> next == FindingStatus.OPEN;
            };

            if (!allowed) {
                throw new IllegalStateException(
                        "Invalid finding transition: " + status + " -> " + next
                );
            }
            status = next;
        }

        String id() {
            return id;
        }

        String title() {
            return title;
        }

        String description() {
            return description;
        }

        Severity severity() {
            return severity;
        }

        Set<String> affectedTaskIds() {
            return affectedTaskIds;
        }

        List<ProblemEvidence> evidence() {
            return evidence;
        }

        String proposedChange() {
            return proposedChange;
        }

        FindingStatus status() {
            return status;
        }
    }

    record TaskMetrics(
            String taskId,
            int participantCount,
            double successRate,
            double partialOrSuccessRate,
            Double medianSuccessfulDuration,
            double meanErrors,
            double assistanceRate
    ) {}

    record ReleasePolicy(
            double minimumSuccessRate,
            double maximumAssistanceRate,
            Set<Severity> blockingSeverities,
            boolean requireAllCriticalFindingsVerified
    ) {
        ReleasePolicy {
            if (!Double.isFinite(minimumSuccessRate)
                    || minimumSuccessRate < 0
                    || minimumSuccessRate > 1) {
                throw new IllegalArgumentException(
                        "Success threshold must be between zero and one."
                );
            }
            if (!Double.isFinite(maximumAssistanceRate)
                    || maximumAssistanceRate < 0
                    || maximumAssistanceRate > 1) {
                throw new IllegalArgumentException(
                        "Assistance threshold must be between zero and one."
                );
            }
            blockingSeverities = Set.copyOf(blockingSeverities);
        }
    }

    static final class StudyPlan {
        private final String studyId;
        private final String objective;
        private final List<ResearchQuestion> questions;
        private final Map<String, TaskDefinition> tasks;
        private final int targetParticipants;

        StudyPlan(
                String studyId,
                String objective,
                List<ResearchQuestion> questions,
                List<TaskDefinition> tasks,
                int targetParticipants
        ) {
            requireText(studyId, "Study ID");
            requireText(objective, "Study objective");
            if (targetParticipants <= 0) {
                throw new IllegalArgumentException(
                        "Target participant count must be positive."
                );
            }
            if (questions.isEmpty() || tasks.isEmpty()) {
                throw new IllegalArgumentException(
                        "A study requires research questions and tasks."
                );
            }

            Map<String, TaskDefinition> taskMap = new HashMap<>();
            for (TaskDefinition task : tasks) {
                if (taskMap.putIfAbsent(task.id(), task) != null) {
                    throw new IllegalArgumentException(
                            "Duplicate task ID: " + task.id()
                    );
                }
            }

            this.studyId = studyId;
            this.objective = objective;
            this.questions = List.copyOf(questions);
            this.tasks = Map.copyOf(taskMap);
            this.targetParticipants = targetParticipants;
        }

        TaskDefinition task(String taskId) {
            TaskDefinition task = tasks.get(taskId);
            if (task == null) {
                throw new IllegalArgumentException("Unknown task: " + taskId);
            }
            return task;
        }

        String studyId() {
            return studyId;
        }

        String objective() {
            return objective;
        }

        List<ResearchQuestion> questions() {
            return questions;
        }

        Map<String, TaskDefinition> tasks() {
            return tasks;
        }

        int targetParticipants() {
            return targetParticipants;
        }
    }

    static final class StudyService {
        private final StudyPlan plan;
        private final Map<String, Participant> participants = new HashMap<>();
        private final Map<String, TaskResult> results = new HashMap<>();
        private final Map<String, UsabilityFinding> findings = new HashMap<>();

        StudyService(StudyPlan plan) {
            this.plan = Objects.requireNonNull(plan, "Study plan");
        }

        void enroll(Participant participant) {
            if (participants.putIfAbsent(participant.id(), participant) != null) {
                throw new IllegalArgumentException(
                        "Participant already enrolled: " + participant.id()
                );
            }
        }

        void record(TaskResult result) {
            if (!participants.containsKey(result.participantId())) {
                throw new IllegalArgumentException("Participant is not enrolled.");
            }

            TaskDefinition task = plan.task(result.taskId());
            if (result.durationSeconds() > task.timeLimitSeconds()
                    && result.outcome() == Outcome.SUCCESS) {
                // Preserve success but keep the time-limit breach visible in
                // metrics and review. Timing policy should not rewrite evidence.
                System.out.println(
                        "Time-limit breach recorded for " + task.id()
                );
            }

            String key = result.participantId() + "::" + result.taskId();
            if (results.putIfAbsent(key, result) != null) {
                throw new IllegalArgumentException(
                        "Duplicate final result for " + key
                );
            }
        }

        void registerFinding(UsabilityFinding finding) {
            for (String taskId : finding.affectedTaskIds()) {
                plan.task(taskId);
            }
            if (findings.putIfAbsent(finding.id(), finding) != null) {
                throw new IllegalArgumentException(
                        "Duplicate finding ID: " + finding.id()
                );
            }
        }

        List<TaskResult> resultsFor(String taskId) {
            plan.task(taskId);
            return results.values().stream()
                    .filter(result -> result.taskId().equals(taskId))
                    .toList();
        }

        TaskMetrics metricsFor(String taskId) {
            List<TaskResult> taskResults = resultsFor(taskId);
            int count = taskResults.size();

            if (count == 0) {
                return new TaskMetrics(taskId, 0, 0, 0, null, 0, 0);
            }

            long successes = taskResults.stream()
                    .filter(result -> result.outcome() == Outcome.SUCCESS)
                    .count();

            long partialOrSuccess = taskResults.stream()
                    .filter(result -> result.outcome() == Outcome.SUCCESS
                            || result.outcome() == Outcome.PARTIAL)
                    .count();

            List<Double> successfulDurations = taskResults.stream()
                    .filter(result -> result.outcome() == Outcome.SUCCESS)
                    .map(TaskResult::durationSeconds)
                    .sorted()
                    .toList();

            Double median = null;
            if (!successfulDurations.isEmpty()) {
                int middle = successfulDurations.size() / 2;
                median = successfulDurations.size() % 2 == 1
                        ? successfulDurations.get(middle)
                        : (successfulDurations.get(middle - 1)
                            + successfulDurations.get(middle)) / 2.0;
            }

            double meanErrors = taskResults.stream()
                    .mapToInt(TaskResult::errors)
                    .average()
                    .orElse(0);

            double assistanceRate = taskResults.stream()
                    .filter(result -> result.assistanceRequests() > 0)
                    .count() / (double) count;

            return new TaskMetrics(
                    taskId,
                    count,
                    successes / (double) count,
                    partialOrSuccess / (double) count,
                    median,
                    meanErrors,
                    assistanceRate
            );
        }

        List<UsabilityFinding> prioritizedFindings() {
            return findings.values().stream()
                    .sorted(Comparator
                            .comparingDouble(UsabilityFinding::priorityScore)
                            .reversed()
                            .thenComparing(UsabilityFinding::id))
                    .toList();
        }

        ReleaseDecision evaluateRelease(ReleasePolicy policy) {
            if (results.isEmpty()) {
                return ReleaseDecision.INSUFFICIENT_EVIDENCE;
            }

            boolean criticalUnverified = findings.values().stream().anyMatch(
                    finding -> finding.severity() == Severity.CRITICAL
                            && finding.status() != FindingStatus.VERIFIED
                            && policy.requireAllCriticalFindingsVerified()
            );

            boolean blockingFinding = findings.values().stream().anyMatch(
                    finding -> policy.blockingSeverities().contains(finding.severity())
                            && finding.status() != FindingStatus.VERIFIED
                            && finding.status() != FindingStatus.ACCEPTED_RISK
            );

            boolean metricFailure = plan.tasks().keySet().stream().anyMatch(
                    taskId -> {
                        TaskMetrics metrics = metricsFor(taskId);
                        return metrics.participantCount() > 0
                                && (metrics.successRate() < policy.minimumSuccessRate()
                                || metrics.assistanceRate() > policy.maximumAssistanceRate());
                    }
            );

            if (criticalUnverified || blockingFinding || metricFailure) {
                return ReleaseDecision.REDESIGN_REQUIRED;
            }
            return ReleaseDecision.READY_FOR_NEXT_VALIDATION;
        }

        StudyPlan plan() {
            return plan;
        }
    }

    private static void requireText(String value, String label) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(label + " cannot be blank.");
        }
    }

    private static StudyService createStudy() {
        List<ResearchQuestion> questions = List.of(
                new ResearchQuestion(
                        "RQ-1",
                        "Can officers distinguish active and pending suppliers?",
                        "Clarify approval labels and filtering."
                ),
                new ResearchQuestion(
                        "RQ-2",
                        "Can officers choose the lowest compliant quotation?",
                        "Expose compliance alongside total cost."
                ),
                new ResearchQuestion(
                        "RQ-3",
                        "Can officers confirm a request was submitted?",
                        "Improve durable submission feedback."
                )
        );

        List<TaskDefinition> tasks = List.of(
                new TaskDefinition(
                        "supplier-search",
                        "Find a supplier with active approval.",
                        List.of("Supplier found", "Approval verified"),
                        240
                ),
                new TaskDefinition(
                        "quotation-review",
                        "Choose the lowest-priced compliant offer.",
                        List.of("Offers compared", "Compliance verified"),
                        300
                ),
                new TaskDefinition(
                        "request-submit",
                        "Submit a purchase request and verify confirmation.",
                        List.of("Request submitted", "Reference verified"),
                        360
                )
        );

        StudyPlan plan = new StudyPlan(
                "ENTERPRISE-UX-17",
                "Evaluate critical procurement workflows before release.",
                questions,
                tasks,
                6
        );

        StudyService service = new StudyService(plan);
        service.enroll(new Participant("P301", "Procurement officer", "frequent", true));
        service.enroll(new Participant("P302", "Purchase analyst", "occasional", true));
        service.enroll(new Participant("P303", "Vendor manager", "frequent", true));
        service.enroll(new Participant("P304", "Department coordinator", "occasional", true));

        service.record(new TaskResult(
                "P301", "supplier-search", Outcome.SUCCESS, 70, 0, 0, 5,
                List.of(
                        new Observation(
                                UUID.randomUUID().toString(),
                                "supplier-search",
                                12000,
                                "filter_applied",
                                "approval-status",
                                "Selected active approval.",
                                EvidenceKind.OBSERVED
                        )
                )
        ));

        service.record(new TaskResult(
                "P302", "supplier-search", Outcome.FAILURE, 240, 3, 1, 2,
                List.of(
                        new Observation(
                                UUID.randomUUID().toString(),
                                "supplier-search",
                                30000,
                                "wrong_selection",
                                "supplier-row",
                                "Selected a supplier with pending approval.",
                                EvidenceKind.OBSERVED
                        )
                )
        ));

        service.record(new TaskResult(
                "P303", "supplier-search", Outcome.SUCCESS, 82, 1, 0, 4,
                List.of()
        ));

        service.record(new TaskResult(
                "P304", "supplier-search", Outcome.PARTIAL, 180, 2, 1, 3,
                List.of()
        ));

        service.record(new TaskResult(
                "P301", "quotation-review", Outcome.PARTIAL, 160, 2, 0, 3,
                List.of(
                        new Observation(
                                UUID.randomUUID().toString(),
                                "quotation-review",
                                25000,
                                "wrong_selection",
                                "quotation-row",
                                "Selected a low-priced offer before verifying compliance.",
                                EvidenceKind.OBSERVED
                        )
                )
        ));

        service.record(new TaskResult(
                "P302", "quotation-review", Outcome.FAILURE, 300, 4, 2, 2,
                List.of()
        ));

        service.record(new TaskResult(
                "P303", "quotation-review", Outcome.SUCCESS, 125, 1, 0, 5,
                List.of()
        ));

        service.record(new TaskResult(
                "P304", "quotation-review", Outcome.SUCCESS, 142, 1, 0, 4,
                List.of()
        ));

        service.record(new TaskResult(
                "P301", "request-submit", Outcome.SUCCESS, 165, 1, 0, 5,
                List.of()
        ));

        service.record(new TaskResult(
                "P302", "request-submit", Outcome.FAILURE, 360, 4, 2, 2,
                List.of(
                        new Observation(
                                UUID.randomUUID().toString(),
                                "request-submit",
                                180000,
                                "repeated_submission",
                                "submit-button",
                                "Repeated submission after unclear confirmation.",
                                EvidenceKind.OBSERVED
                        )
                )
        ));

        service.record(new TaskResult(
                "P303", "request-submit", Outcome.SUCCESS, 190, 1, 0, 4,
                List.of()
        ));

        service.record(new TaskResult(
                "P304", "request-submit", Outcome.SUCCESS, 175, 1, 0, 4,
                List.of()
        ));

        service.registerFinding(new UsabilityFinding(
                "UX-401",
                "Ambiguous supplier approval labels",
                "Pending suppliers are mistaken for active suppliers.",
                Severity.CRITICAL,
                Set.of("supplier-search"),
                2,
                0.95,
                List.of(
                        new ProblemEvidence(
                                "OBS-401",
                                EvidenceKind.OBSERVED,
                                "A participant selected a supplier with pending approval."
                        ),
                        new ProblemEvidence(
                                "OBS-402",
                                EvidenceKind.OBSERVED,
                                "A participant requested help distinguishing states."
                        )
                ),
                "Use explicit status text and an approved-only filter."
        ));

        service.registerFinding(new UsabilityFinding(
                "UX-402",
                "Quotation compliance is not visible during comparison",
                "The lowest raw price can be selected before checking compliance.",
                Severity.CRITICAL,
                Set.of("quotation-review"),
                2,
                0.9,
                List.of(
                        new ProblemEvidence(
                                "OBS-403",
                                EvidenceKind.OBSERVED,
                                "A non-compliant quotation was selected."
                        )
                ),
                "Display specification compliance beside total price."
        ));

        service.registerFinding(new UsabilityFinding(
                "UX-403",
                "Submission confirmation is not sufficiently clear",
                "Users cannot confidently distinguish a submitted request from a pending action.",
                Severity.MAJOR,
                Set.of("request-submit"),
                1,
                0.8,
                List.of(
                        new ProblemEvidence(
                                "OBS-404",
                                EvidenceKind.OBSERVED,
                                "A participant repeated the submission."
                        )
                ),
                "Show a persistent confirmation and request reference."
        ));

        return service;
    }

    private static void demonstrateStateTransitions() {
        UsabilityFinding example = new UsabilityFinding(
                "UX-EXAMPLE",
                "Example finding",
                "Demonstrates the finding lifecycle.",
                Severity.MINOR,
                Set.of("supplier-search"),
                1,
                0.4,
                List.of(
                        new ProblemEvidence(
                                "OBS-EXAMPLE",
                                EvidenceKind.OBSERVED,
                                "A participant hesitated at the filter."
                        )
                ),
                "Clarify the filter label."
        );

        example.transitionTo(FindingStatus.IN_PROGRESS);
        example.transitionTo(FindingStatus.FIXED);
        example.transitionTo(FindingStatus.VERIFIED);

        if (example.status() != FindingStatus.VERIFIED) {
            throw new IllegalStateException("Finding verification failed.");
        }

        try {
            example.transitionTo(FindingStatus.FIXED);
            throw new IllegalStateException("Invalid transition was accepted.");
        } catch (IllegalStateException expected) {
            if (!expected.getMessage().startsWith("Invalid finding transition")) {
                throw expected;
            }
        }
    }

    public static void main(String[] args) {
        StudyService service = createStudy();

        System.out.println("STUDY: " + service.plan().studyId());
        System.out.println(service.plan().objective());
        System.out.println("Planned participants: "
                + service.plan().targetParticipants());

        System.out.println("\nTASK METRICS");
        for (String taskId : service.plan().tasks().keySet()) {
            TaskMetrics metrics = service.metricsFor(taskId);
            System.out.printf(
                    "%-22s n=%d success=%.1f%% partial-or-success=%.1f%% "
                            + "median-success-seconds=%s mean-errors=%.2f "
                            + "assistance=%.1f%%%n",
                    metrics.taskId(),
                    metrics.participantCount(),
                    metrics.successRate() * 100,
                    metrics.partialOrSuccessRate() * 100,
                    metrics.medianSuccessfulDuration() == null
                            ? "N/A"
                            : String.format("%.1f", metrics.medianSuccessfulDuration()),
                    metrics.meanErrors(),
                    metrics.assistanceRate() * 100
            );
        }

        System.out.println("\nPRIORITIZED FINDINGS");
        for (UsabilityFinding finding : service.prioritizedFindings()) {
            System.out.printf(
                    "%s | %s | severity=%s | priority=%.3f | status=%s%n",
                    finding.id(),
                    finding.title(),
                    finding.severity(),
                    finding.priorityScore(),
                    finding.status()
            );
            System.out.println("  Change: " + finding.proposedChange());
        }

        ReleasePolicy policy = new ReleasePolicy(
                0.80,
                0.20,
                EnumSet.of(Severity.CRITICAL),
                true
        );

        System.out.println("\nRELEASE ASSESSMENT");
        System.out.println(service.evaluateRelease(policy));

        demonstrateStateTransitions();
        System.out.println("\nState-transition validation passed.");
    }
}
