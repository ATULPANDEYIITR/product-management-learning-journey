/*
 * Product Discovery Sprint
 * ------------------------
 * Enterprise-oriented Java 17 domain model for product discovery.
 *
 * The program models discovery as an explicit domain workflow:
 * research -> synthesis -> opportunities -> ideation -> validation -> decision.
 *
 * Java-specific design choices:
 * - records for immutable evidence and experiment specifications
 * - enums for controlled domain states
 * - interfaces for validation policies
 * - sealed validation results for explicit outcomes
 * - collections for traceability between evidence and opportunities
 * - service classes for separation of domain policy from orchestration
 *
 * Compile:
 *   javac ProductDiscoverySprint.java
 *
 * Run:
 *   java ProductDiscoverySprint
 */

import java.time.Instant;
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

public class ProductDiscoverySprint {

    enum EvidenceType {
        INTERVIEW,
        OBSERVATION,
        SURVEY,
        ANALYTICS,
        SUPPORT
    }

    enum SprintPhase {
        PLANNED,
        RESEARCH,
        SYNTHESIS,
        IDEATION,
        VALIDATION,
        DECISION
    }

    enum Decision {
        CONTINUE,
        ITERATE,
        STOP
    }

    enum AssumptionType {
        DESIRABILITY,
        BEHAVIOR,
        FEASIBILITY,
        BUSINESS
    }

    record ResearchQuestion(String text) {
        ResearchQuestion {
            requireText(text, "Research question");
        }
    }

    record Participant(
        String id,
        String segment,
        String role,
        String context
    ) {
        Participant {
            requireText(id, "Participant id");
            requireText(segment, "Segment");
            requireText(role, "Role");
            requireText(context, "Context");
        }
    }

    record Evidence(
        String id,
        String source,
        EvidenceType type,
        String participantId,
        String statement,
        double severity,
        int frequency,
        Set<String> tags
    ) {
        Evidence {
            requireText(id, "Evidence id");
            requireText(source, "Evidence source");
            requireText(statement, "Evidence statement");

            if (severity < 0 || severity > 1) {
                throw new IllegalArgumentException("Evidence severity must be 0-1");
            }

            if (frequency <= 0) {
                throw new IllegalArgumentException("Evidence frequency must be positive");
            }

            tags = Set.copyOf(tags == null ? Set.of() : tags);
        }

        double signal() {
            return severity * Math.log1p(frequency);
        }
    }

    record Theme(
        String id,
        String name,
        String description,
        Set<String> tags,
        List<String> evidenceIds,
        double userImpact,
        double strategicFit
    ) {
        Theme {
            requireText(id, "Theme id");
            requireText(name, "Theme name");
            requireText(description, "Theme description");

            if (userImpact < 0 || userImpact > 10 ||
                strategicFit < 0 || strategicFit > 10) {
                throw new IllegalArgumentException("Theme scores must be 0-10");
            }

            tags = Set.copyOf(tags);
            evidenceIds = List.copyOf(evidenceIds);
        }

        double score() {
            return userImpact * 0.55 + strategicFit * 0.45;
        }
    }

    record Opportunity(
        String id,
        String themeId,
        String statement,
        String targetBehavior,
        double evidenceStrength,
        double businessValue,
        double feasibility
    ) {
        Opportunity {
            requireText(id, "Opportunity id");
            requireText(statement, "Opportunity statement");
            requireText(targetBehavior, "Target behavior");

            validateTenPointScore(evidenceStrength, "Evidence strength");
            validateTenPointScore(businessValue, "Business value");
            validateTenPointScore(feasibility, "Feasibility");
        }

        double score() {
            return evidenceStrength * 0.40
                    + businessValue * 0.35
                    + feasibility * 0.25;
        }
    }

    record Concept(
        String id,
        String opportunityId,
        String name,
        String mechanism,
        double confidence,
        double effort,
        double reach
    ) {
        Concept {
            requireText(id, "Concept id");
            requireText(name, "Concept name");
            requireText(mechanism, "Concept mechanism");

            if (confidence < 0 || confidence > 1) {
                throw new IllegalArgumentException("Concept confidence must be 0-1");
            }

            if (effort <= 0) {
                throw new IllegalArgumentException("Concept effort must be positive");
            }

            validateTenPointScore(reach, "Concept reach");
        }

        double score() {
            return confidence * reach / effort;
        }
    }

    record ExperimentResult(
        String id,
        String conceptId,
        String metric,
        int participants,
        double baseline,
        double observed,
        double threshold,
        double qualitativeSignal,
        Decision decision,
        Instant completedAt
    ) {
        ExperimentResult {
            if (participants < 5) {
                throw new IllegalArgumentException(
                    "Validation experiment requires at least five participants"
                );
            }

            validateProbability(baseline, "Baseline");
            validateProbability(observed, "Observed");
            validateProbability(threshold, "Threshold");
            validateProbability(qualitativeSignal, "Qualitative signal");
        }

        Double lift() {
            return baseline == 0
                    ? null
                    : (observed - baseline) / baseline;
        }
    }

    record Assumption(
        String id,
        String statement,
        AssumptionType type,
        double importance,
        double uncertainty,
        double evidence
    ) {
        Assumption {
            requireText(id, "Assumption id");
            requireText(statement, "Assumption statement");

            validateProbability(importance, "Importance");
            validateProbability(uncertainty, "Uncertainty");
            validateProbability(evidence, "Evidence");
        }

        double risk() {
            return importance * uncertainty * (1 - evidence);
        }
    }

    sealed interface ValidationPolicy
        permits ThresholdValidationPolicy {
        Decision evaluate(
            double baseline,
            double observed,
            double threshold,
            double qualitativeSignal
        );
    }

    static final class ThresholdValidationPolicy implements ValidationPolicy {
        private final double qualitativeThreshold;

        ThresholdValidationPolicy(double qualitativeThreshold) {
            validateProbability(qualitativeThreshold, "Qualitative threshold");
            this.qualitativeThreshold = qualitativeThreshold;
        }

        @Override
        public Decision evaluate(
            double baseline,
            double observed,
            double threshold,
            double qualitativeSignal
        ) {
            boolean quantitativePass = observed >= threshold;
            boolean qualitativePass = qualitativeSignal >= qualitativeThreshold;

            if (quantitativePass && qualitativePass) {
                return Decision.CONTINUE;
            }

            if (quantitativePass || qualitativePass) {
                return Decision.ITERATE;
            }

            return Decision.STOP;
        }
    }

    static final class DiscoveryRepository {
        private final Map<String, Evidence> evidence = new HashMap<>();
        private final Map<String, Theme> themes = new HashMap<>();
        private final Map<String, Opportunity> opportunities = new HashMap<>();
        private final Map<String, Concept> concepts = new HashMap<>();
        private final List<ExperimentResult> experiments = new ArrayList<>();

        void saveEvidence(Evidence item) {
            requireUnique(evidence, item.id(), "Evidence");
            evidence.put(item.id(), item);
        }

        void saveTheme(Theme item) {
            requireUnique(themes, item.id(), "Theme");

            for (String evidenceId : item.evidenceIds()) {
                if (!evidence.containsKey(evidenceId)) {
                    throw new IllegalStateException(
                        "Theme references missing evidence: " + evidenceId
                    );
                }
            }

            themes.put(item.id(), item);
        }

        void saveOpportunity(Opportunity item) {
            requireUnique(opportunities, item.id(), "Opportunity");

            if (!themes.containsKey(item.themeId())) {
                throw new IllegalStateException(
                    "Opportunity references missing theme: " + item.themeId()
                );
            }

            opportunities.put(item.id(), item);
        }

        void saveConcept(Concept item) {
            requireUnique(concepts, item.id(), "Concept");

            if (!opportunities.containsKey(item.opportunityId())) {
                throw new IllegalStateException(
                    "Concept references missing opportunity: " + item.opportunityId()
                );
            }

            concepts.put(item.id(), item);
        }

        void saveExperiment(ExperimentResult result) {
            if (!concepts.containsKey(result.conceptId())) {
                throw new IllegalStateException(
                    "Experiment references missing concept: " + result.conceptId()
                );
            }

            experiments.add(result);
        }

        List<Evidence> evidence() {
            return List.copyOf(evidence.values());
        }

        List<Theme> rankedThemes() {
            return themes.values()
                .stream()
                .sorted(Comparator.comparingDouble(Theme::score).reversed())
                .toList();
        }

        List<Opportunity> rankedOpportunities() {
            return opportunities.values()
                .stream()
                .sorted(Comparator.comparingDouble(Opportunity::score).reversed())
                .toList();
        }

        List<Concept> rankedConcepts() {
            return concepts.values()
                .stream()
                .sorted(Comparator.comparingDouble(Concept::score).reversed())
                .toList();
        }

        List<ExperimentResult> experiments() {
            return List.copyOf(experiments);
        }

        private static <T> void requireUnique(
            Map<String, T> map,
            String id,
            String type
        ) {
            if (map.containsKey(id)) {
                throw new IllegalStateException(
                    type + " id already exists: " + id
                );
            }
        }
    }

    static final class ResearchService {
        private final DiscoveryRepository repository;

        ResearchService(DiscoveryRepository repository) {
            this.repository = repository;
        }

        Theme synthesizeTheme(
            String id,
            String name,
            String description,
            Set<String> tags,
            double strategicFit
        ) {
            List<Evidence> supportingEvidence = repository.evidence()
                .stream()
                .filter(item -> tags.stream().anyMatch(item.tags()::contains))
                .toList();

            if (supportingEvidence.isEmpty()) {
                throw new IllegalStateException(
                    "Cannot synthesize a theme without supporting evidence"
                );
            }

            double averageSeverity = supportingEvidence
                .stream()
                .mapToDouble(Evidence::severity)
                .average()
                .orElse(0);

            double userImpact = Math.min(10, averageSeverity * 10);

            Theme theme = new Theme(
                id,
                name,
                description,
                tags,
                supportingEvidence.stream()
                    .map(Evidence::id)
                    .toList(),
                userImpact,
                strategicFit
            );

            repository.saveTheme(theme);
            return theme;
        }
    }

    static final class ValidationService {
        private final DiscoveryRepository repository;
        private final ValidationPolicy policy;

        ValidationService(
            DiscoveryRepository repository,
            ValidationPolicy policy
        ) {
            this.repository = repository;
            this.policy = policy;
        }

        ExperimentResult validate(
            String conceptId,
            String metric,
            int participants,
            double baseline,
            double observed,
            double threshold,
            double qualitativeSignal
        ) {
            if (repository.rankedConcepts()
                .stream()
                .noneMatch(concept -> concept.id().equals(conceptId))) {
                throw new IllegalStateException(
                    "Cannot validate unknown concept: " + conceptId
                );
            }

            Decision decision = policy.evaluate(
                baseline,
                observed,
                threshold,
                qualitativeSignal
            );

            ExperimentResult result = new ExperimentResult(
                UUID.randomUUID().toString(),
                conceptId,
                metric,
                participants,
                baseline,
                observed,
                threshold,
                qualitativeSignal,
                decision,
                Instant.now()
            );

            repository.saveExperiment(result);
            return result;
        }
    }

    static final class SprintController {
        private SprintPhase phase = SprintPhase.PLANNED;

        void transitionTo(SprintPhase next) {
            Set<SprintPhase> allowed = switch (phase) {
                case PLANNED -> EnumSet.of(SprintPhase.RESEARCH);
                case RESEARCH -> EnumSet.of(SprintPhase.SYNTHESIS);
                case SYNTHESIS -> EnumSet.of(SprintPhase.IDEATION);
                case IDEATION -> EnumSet.of(SprintPhase.VALIDATION);
                case VALIDATION -> EnumSet.of(SprintPhase.DECISION);
                case DECISION -> EnumSet.noneOf(SprintPhase.class);
            };

            if (!allowed.contains(next)) {
                throw new IllegalStateException(
                    "Invalid sprint transition: " + phase + " -> " + next
                );
            }

            phase = next;
            System.out.printf(
                "[SPRINT] phase changed to %s%n",
                phase
            );
        }

        SprintPhase phase() {
            return phase;
        }
    }

    private static void addEvidence(
        DiscoveryRepository repository
    ) {
        repository.saveEvidence(new Evidence(
            "OBS-001",
            "INT-001",
            EvidenceType.INTERVIEW,
            "P-001",
            "I copy supplier lead time, MOQ, certification, and price into my spreadsheet.",
            0.90,
            5,
            Set.of("comparison", "manual", "spreadsheet")
        ));

        repository.saveEvidence(new Evidence(
            "OBS-002",
            "OBS-001",
            EvidenceType.OBSERVATION,
            "P-001",
            "Buyer opens multiple supplier pages and manually transfers attributes.",
            0.93,
            4,
            Set.of("comparison", "manual")
        ));

        repository.saveEvidence(new Evidence(
            "OBS-003",
            "INT-002",
            EvidenceType.INTERVIEW,
            "P-002",
            "Urgent requests cause buyers to reuse known suppliers because qualification takes too long.",
            0.84,
            4,
            Set.of("qualification", "time", "trust")
        ));

        repository.saveEvidence(new Evidence(
            "OBS-004",
            "INT-003",
            EvidenceType.INTERVIEW,
            "P-003",
            "A lower price does not matter if the supplier certification cannot be verified.",
            0.95,
            3,
            Set.of("qualification", "trust", "evidence")
        ));

        repository.saveEvidence(new Evidence(
            "OBS-005",
            "SUP-2026-09",
            EvidenceType.SUPPORT,
            null,
            "Support requests frequently ask where supplier qualification evidence is stored.",
            0.72,
            18,
            Set.of("qualification", "trust", "evidence")
        ));

        repository.saveEvidence(new Evidence(
            "OBS-006",
            "AN-2026-Q3",
            EvidenceType.ANALYTICS,
            null,
            "Supplier detail pages receive repeat visits but have low shortlist conversion.",
            0.70,
            1,
            Set.of("discovery", "shortlist")
        ));
    }

    private static void printResearch(
        DiscoveryRepository repository
    ) {
        System.out.println("\n=== RESEARCH ===");

        repository.evidence()
            .stream()
            .sorted(Comparator.comparingDouble(Evidence::signal).reversed())
            .forEach(item ->
                System.out.printf(
                    "%s | %s | signal=%.2f | %s%n",
                    item.id(),
                    item.type(),
                    item.signal(),
                    item.statement()
                )
            );
    }

    private static void printSynthesis(
        DiscoveryRepository repository
    ) {
        System.out.println("\n=== SYNTHESIS ===");

        repository.rankedThemes().forEach(theme ->
            System.out.printf(
                "%s | %s | score=%.2f | evidence=%d%n%s%n",
                theme.id(),
                theme.name(),
                theme.score(),
                theme.evidenceIds().size(),
                theme.description()
            )
        );
    }

    private static void printOpportunities(
        DiscoveryRepository repository
    ) {
        System.out.println("\n=== OPPORTUNITIES ===");

        repository.rankedOpportunities().forEach(opportunity ->
            System.out.printf(
                "%s | score=%.2f%n  %s%n  Behavior: %s%n",
                opportunity.id(),
                opportunity.score(),
                opportunity.statement(),
                opportunity.targetBehavior()
            )
        );
    }

    private static void printConcepts(
        DiscoveryRepository repository
    ) {
        System.out.println("\n=== CONCEPTS ===");

        repository.rankedConcepts().forEach(concept ->
            System.out.printf(
                "%s | %s | score=%.2f%n  %s%n",
                concept.id(),
                concept.name(),
                concept.score(),
                concept.mechanism()
            )
        );
    }

    private static void printValidation(
        DiscoveryRepository repository
    ) {
        System.out.println("\n=== VALIDATION ===");

        repository.experiments().forEach(result -> {
            String lift = result.lift() == null
                ? "undefined"
                : String.format("%.1f%%", result.lift() * 100);

            System.out.printf(
                "%s | concept=%s | decision=%s | observed=%.1f%% | threshold=%.1f%% | lift=%s%n",
                result.id(),
                result.conceptId(),
                result.decision(),
                result.observed() * 100,
                result.threshold() * 100,
                lift
            );
        });
    }

    private static void demonstrateFailureState() {
        System.out.println("\n=== FAILURE STATE ===");

        DiscoveryRepository repository = new DiscoveryRepository();

        try {
            repository.saveOpportunity(new Opportunity(
                "OPP-BAD",
                "THEME-UNKNOWN",
                "This opportunity has no traceable theme.",
                "invalid",
                8,
                8,
                8
            ));
        } catch (IllegalStateException exception) {
            System.out.println(
                "Rejected invalid opportunity: " + exception.getMessage()
            );
        }
    }

    private static void validateTenPointScore(
        double value,
        String name
    ) {
        if (!Double.isFinite(value) || value < 0 || value > 10) {
            throw new IllegalArgumentException(
                name + " must be between 0 and 10"
            );
        }
    }

    private static void validateProbability(
        double value,
        String name
    ) {
        if (!Double.isFinite(value) || value < 0 || value > 1) {
            throw new IllegalArgumentException(
                name + " must be between 0 and 1"
            );
        }
    }

    private static void requireText(
        String value,
        String name
    ) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                name + " cannot be blank"
            );
        }
    }

    public static void main(String[] args) {
        DiscoveryRepository repository = new DiscoveryRepository();
        ResearchService researchService = new ResearchService(repository);
        ValidationService validationService =
            new ValidationService(
                repository,
                new ThresholdValidationPolicy(0.65)
            );
        SprintController sprint = new SprintController();

        System.out.println("=== PRODUCT DISCOVERY SPRINT ===");
        System.out.println(
            "Enterprise case: supplier discovery and qualification"
        );

        List<Participant> participants = List.of(
            new Participant(
                "P-001",
                "strategic procurement",
                "procurement manager",
                "high-value supplier comparison"
            ),
            new Participant(
                "P-002",
                "operational procurement",
                "buyer",
                "urgent recurring purchases"
            ),
            new Participant(
                "P-003",
                "strategic procurement",
                "category manager",
                "supplier qualification"
            )
        );

        List<ResearchQuestion> questions = List.of(
            new ResearchQuestion(
                "Where does supplier comparison create unnecessary work?"
            ),
            new ResearchQuestion(
                "What evidence is required before supplier qualification can be trusted?"
            ),
            new ResearchQuestion(
                "Which workaround reveals a meaningful unmet need?"
            )
        );

        System.out.printf(
            "Participants: %d | Research questions: %d%n",
            participants.size(),
            questions.size()
        );

        sprint.transitionTo(SprintPhase.RESEARCH);
        addEvidence(repository);

        sprint.transitionTo(SprintPhase.SYNTHESIS);

        Theme comparisonTheme = researchService.synthesizeTheme(
            "THEME-001",
            "Manual comparison burden",
            "Supplier information is reconstructed manually before buyers can compare alternatives.",
            Set.of("comparison", "manual", "spreadsheet"),
            8.7
        );

        Theme qualificationTheme = researchService.synthesizeTheme(
            "THEME-002",
            "Qualification evidence gap",
            "Qualification evidence is fragmented enough to slow trust decisions.",
            Set.of("qualification", "trust", "evidence"),
            9.3
        );

        sprint.transitionTo(SprintPhase.IDEATION);

        Opportunity comparisonOpportunity = new Opportunity(
            "OPP-001",
            comparisonTheme.id(),
            "Procurement managers need comparable supplier evidence without reconstructing it manually.",
            "complete supplier comparisons using normalized evidence",
            8.8,
            8.9,
            7.8
        );

        Opportunity qualificationOpportunity = new Opportunity(
            "OPP-002",
            qualificationTheme.id(),
            "Procurement managers need qualification evidence attached to supplier decisions.",
            "verify supplier qualification before committing research time",
            9.2,
            9.1,
            7.0
        );

        repository.saveOpportunity(comparisonOpportunity);
        repository.saveOpportunity(qualificationOpportunity);

        Concept comparisonConcept = new Concept(
            "CON-001",
            comparisonOpportunity.id(),
            "Evidence comparison workspace",
            "Normalize supplier attributes and keep source evidence beside each attribute.",
            0.82,
            5,
            8.5
        );

        Concept qualificationConcept = new Concept(
            "CON-002",
            qualificationOpportunity.id(),
            "Qualification evidence ledger",
            "Expose qualification claims with verification state and evidence provenance.",
            0.76,
            6,
            8.0
        );

        repository.saveConcept(comparisonConcept);
        repository.saveConcept(qualificationConcept);

        sprint.transitionTo(SprintPhase.VALIDATION);

        validationService.validate(
            comparisonConcept.id(),
            "supplier comparison task completion",
            8,
            0.45,
            0.875,
            0.75,
            0.84
        );

        validationService.validate(
            qualificationConcept.id(),
            "qualification verification task completion",
            8,
            0.50,
            0.625,
            0.75,
            0.71
        );

        sprint.transitionTo(SprintPhase.DECISION);

        printResearch(repository);
        printSynthesis(repository);
        printOpportunities(repository);
        printConcepts(repository);
        printValidation(repository);
        demonstrateFailureState();

        System.out.println("\n=== ENTERPRISE DISCOVERY DECISIONS ===");

        repository.experiments().forEach(result -> {
            switch (result.decision()) {
                case CONTINUE ->
                    System.out.println(
                        result.conceptId()
                        + ": continue to another validation stage."
                    );
                case ITERATE ->
                    System.out.println(
                        result.conceptId()
                        + ": iterate because evidence is incomplete."
                    );
                case STOP ->
                    System.out.println(
                        result.conceptId()
                        + ": stop because validation failed."
                    );
            }
        });

        System.out.println("\n=== SPRINT PHASE ===");
        System.out.println(sprint.phase());
    }
}
