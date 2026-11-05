import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.OptionalDouble;
import java.util.UUID;
import java.util.stream.Collectors;

public class OKRManagementSystem {

    enum IndicatorType {
        LEADING,
        LAGGING
    }

    enum ObjectiveStatus {
        DRAFT,
        ACTIVE,
        AT_RISK,
        COMPLETED,
        CANCELLED
    }

    enum EventType {
        CREATED,
        ACTIVATED,
        RESULT_UPDATED,
        STATUS_CHANGED
    }

    static class OKRException extends RuntimeException {
        OKRException(String message) {
            super(message);
        }
    }

    static class AuthorizationException extends OKRException {
        AuthorizationException(String message) {
            super(message);
        }
    }

    record AuditEvent(
        Instant timestamp,
        EventType type,
        String objectiveId,
        String description
    ) {}

    record KeyResultSnapshot(
        String id,
        String title,
        double baseline,
        double current,
        double target,
        String unit,
        IndicatorType indicatorType,
        double progress
    ) {}

    record ObjectiveReport(
        String objective,
        String owner,
        String department,
        ObjectiveStatus status,
        double weightedProgress,
        Double leadingProgress,
        Double laggingProgress
    ) {}

    static void validateText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new OKRException(field + " cannot be empty.");
        }
    }

    static void validateNumber(double value, String field) {
        if (!Double.isFinite(value) || Math.abs(value) > 1e12) {
            throw new OKRException(field + " is invalid.");
        }
    }

    static final class KeyResult {
        private final String id;
        private final String title;
        private final double baseline;
        private final double target;
        private final String unit;
        private final IndicatorType indicatorType;
        private final double weight;
        private final boolean higherIsBetter;

        private double current;
        private final List<KeyResultSnapshot> history =
            new ArrayList<>();

        KeyResult(
            String title,
            double baseline,
            double current,
            double target,
            String unit,
            IndicatorType indicatorType,
            double weight,
            boolean higherIsBetter
        ) {
            validateText(title, "Key result title");
            validateText(unit, "Unit");

            validateNumber(baseline, "Baseline");
            validateNumber(current, "Current");
            validateNumber(target, "Target");
            validateNumber(weight, "Weight");

            if (baseline == target) {
                throw new OKRException(
                    "Baseline and target cannot match."
                );
            }

            if (weight <= 0) {
                throw new OKRException("Weight must be positive.");
            }

            if (higherIsBetter
                ? target <= baseline
                : target >= baseline) {
                throw new OKRException("Invalid target direction.");
            }

            this.id = UUID.randomUUID().toString();
            this.title = title;
            this.baseline = baseline;
            this.current = current;
            this.target = target;
            this.unit = unit;
            this.indicatorType =
                Objects.requireNonNull(indicatorType);
            this.weight = weight;
            this.higherIsBetter = higherIsBetter;
        }

        String id() {
            return id;
        }

        String title() {
            return title;
        }

        double weight() {
            return weight;
        }

        IndicatorType indicatorType() {
            return indicatorType;
        }

        double current() {
            return current;
        }

        double progress() {
            return Math.max(
                0,
                Math.min(
                    1,
                    (current - baseline) / (target - baseline)
                )
            );
        }

        void update(double value) {
            validateNumber(value, "Updated value");

            current = value;

            history.add(new KeyResultSnapshot(
                id,
                title,
                baseline,
                current,
                target,
                unit,
                indicatorType,
                progress()
            ));
        }

        List<KeyResultSnapshot> history() {
            return Collections.unmodifiableList(history);
        }
    }

    static final class Objective {
        private final String id;
        private final String title;
        private final String owner;
        private final String department;
        private final String period;
        private final String parentId;
        private final String description;

        private ObjectiveStatus status = ObjectiveStatus.DRAFT;

        private final Map<String, KeyResult> keyResults =
            new LinkedHashMap<>();

        Objective(
            String title,
            String owner,
            String department,
            String period,
            String parentId,
            String description
        ) {
            validateText(title, "Objective title");
            validateText(owner, "Owner");
            validateText(department, "Department");
            validateText(period, "Period");

            this.id = UUID.randomUUID().toString();
            this.title = title;
            this.owner = owner;
            this.department = department;
            this.period = period;
            this.parentId = parentId;
            this.description = description == null ? "" : description;
        }

        String id() {
            return id;
        }

        String title() {
            return title;
        }

        String owner() {
            return owner;
        }

        String department() {
            return department;
        }

        String period() {
            return period;
        }

        String parentId() {
            return parentId;
        }

        ObjectiveStatus status() {
            return status;
        }

        Map<String, KeyResult> keyResults() {
            return Collections.unmodifiableMap(keyResults);
        }

        void addKeyResult(KeyResult result) {
            if (status != ObjectiveStatus.DRAFT) {
                throw new OKRException(
                    "Key results cannot be added after activation."
                );
            }

            boolean duplicate = keyResults.values().stream()
                .anyMatch(existing ->
                    existing.title().equalsIgnoreCase(result.title())
                );

            if (duplicate || keyResults.containsKey(result.id())) {
                throw new OKRException("Duplicate key result.");
            }

            keyResults.put(result.id(), result);
        }

        void activate() {
            if (status != ObjectiveStatus.DRAFT &&
                status != ObjectiveStatus.ACTIVE) {
                throw new OKRException(
                    "Invalid objective state transition."
                );
            }

            if (keyResults.isEmpty()) {
                throw new OKRException(
                    "At least one key result is required."
                );
            }

            status = ObjectiveStatus.ACTIVE;
        }

        double progress() {
            double totalWeight = keyResults.values().stream()
                .mapToDouble(KeyResult::weight)
                .sum();

            if (totalWeight == 0) return 0;

            return keyResults.values().stream()
                .mapToDouble(kr -> kr.progress() * kr.weight())
                .sum() / totalWeight;
        }

        OptionalDouble indicatorProgress(IndicatorType type) {
            List<KeyResult> selected = keyResults.values().stream()
                .filter(kr -> kr.indicatorType() == type)
                .toList();

            if (selected.isEmpty()) {
                return OptionalDouble.empty();
            }

            return OptionalDouble.of(
                selected.stream()
                    .mapToDouble(KeyResult::progress)
                    .average()
                    .orElse(0)
            );
        }

        void evaluate() {
            if (status == ObjectiveStatus.CANCELLED ||
                status == ObjectiveStatus.COMPLETED) {
                return;
            }

            if (progress() >= 1.0) {
                status = ObjectiveStatus.COMPLETED;
            } else if (progress() < 0.4) {
                status = ObjectiveStatus.AT_RISK;
            } else {
                status = ObjectiveStatus.ACTIVE;
            }
        }
    }

    interface AuthorizationPolicy {
        boolean mayUpdate(String actor, Objective objective);
    }

    static final class OwnerAuthorizationPolicy
        implements AuthorizationPolicy {

        @Override
        public boolean mayUpdate(String actor, Objective objective) {
            return actor.equals(objective.owner());
        }
    }

    static final class OKRService {
        private final Map<String, Objective> objectives =
            new LinkedHashMap<>();

        private final List<AuditEvent> auditLog =
            new ArrayList<>();

        private final AuthorizationPolicy authorizationPolicy;

        OKRService(AuthorizationPolicy authorizationPolicy) {
            this.authorizationPolicy =
                Objects.requireNonNull(authorizationPolicy);
        }

        void addObjective(Objective objective) {
            if (objectives.containsKey(objective.id())) {
                throw new OKRException("Duplicate objective.");
            }

            if (objective.parentId() != null) {
                Objective parent = getObjective(objective.parentId());

                if (!parent.period().equals(objective.period())) {
                    throw new OKRException(
                        "Aligned objectives must share a period."
                    );
                }
            }

            objectives.put(objective.id(), objective);

            log(
                EventType.CREATED,
                objective.id(),
                "Objective registered."
            );
        }

        Objective getObjective(String id) {
            Objective objective = objectives.get(id);

            if (objective == null) {
                throw new OKRException("Objective not found.");
            }

            return objective;
        }

        void activate(String objectiveId) {
            Objective objective = getObjective(objectiveId);
            objective.activate();

            log(
                EventType.ACTIVATED,
                objectiveId,
                "Objective activated."
            );
        }

        void updateKeyResult(
            String objectiveId,
            String keyResultId,
            String actor,
            double value
        ) {
            Objective objective = getObjective(objectiveId);

            if (!authorizationPolicy.mayUpdate(actor, objective)) {
                throw new AuthorizationException(
                    "Actor cannot update this objective."
                );
            }

            if (objective.status() != ObjectiveStatus.ACTIVE &&
                objective.status() != ObjectiveStatus.AT_RISK) {
                throw new OKRException(
                    "Objective is not accepting updates."
                );
            }

            KeyResult result = objective.keyResults().get(keyResultId);

            if (result == null) {
                throw new OKRException("Key result not found.");
            }

            double previous = result.current();
            result.update(value);

            ObjectiveStatus oldStatus = objective.status();
            objective.evaluate();

            log(
                EventType.RESULT_UPDATED,
                objectiveId,
                result.title() + ": " + previous + " -> " + value
            );

            if (oldStatus != objective.status()) {
                log(
                    EventType.STATUS_CHANGED,
                    objectiveId,
                    oldStatus + " -> " + objective.status()
                );
            }
        }

        List<ObjectiveReport> report() {
            return objectives.values().stream()
                .map(objective -> {
                    objective.evaluate();

                    Double leading = objective.indicatorProgress(
                        IndicatorType.LEADING
                    ).isPresent()
                        ? objective.indicatorProgress(
                            IndicatorType.LEADING
                        ).getAsDouble()
                        : null;

                    Double lagging = objective.indicatorProgress(
                        IndicatorType.LAGGING
                    ).isPresent()
                        ? objective.indicatorProgress(
                            IndicatorType.LAGGING
                        ).getAsDouble()
                        : null;

                    return new ObjectiveReport(
                        objective.title(),
                        objective.owner(),
                        objective.department(),
                        objective.status(),
                        objective.progress(),
                        leading,
                        lagging
                    );
                })
                .toList();
        }

        List<AuditEvent> auditLog() {
            return Collections.unmodifiableList(auditLog);
        }

        List<String> alignmentTree(String parentId) {
            Objective parent = getObjective(parentId);

            List<String> output = new ArrayList<>();
            appendAlignment(parent, 0, output);
            return output;
        }

        private void appendAlignment(
            Objective objective,
            int depth,
            List<String> output
        ) {
            output.add(
                " ".repeat(depth * 2) +
                objective.title() +
                " (" +
                String.format("%.1f", objective.progress() * 100) +
                "%)"
            );

            objectives.values().stream()
                .filter(child ->
                    objective.id().equals(child.parentId())
                )
                .forEach(child ->
                    appendAlignment(child, depth + 1, output)
                );
        }

        private void log(
            EventType type,
            String objectiveId,
            String description
        ) {
            auditLog.add(new AuditEvent(
                Instant.now(),
                type,
                objectiveId,
                description
            ));
        }
    }

    public static void main(String[] args) {
        try {
            OKRService service = new OKRService(
                new OwnerAuthorizationPolicy()
            );

            Objective company = new Objective(
                "Improve digital banking competitiveness",
                "CEO",
                "Executive",
                "2026-Q4",
                null,
                "Improve customer outcomes and platform adoption."
            );

            KeyResult retention = new KeyResult(
                "Customer retention rate",
                70, 76, 90,
                "%",
                IndicatorType.LAGGING,
                2.0,
                true
            );

            company.addKeyResult(retention);

            company.addKeyResult(new KeyResult(
                "Monthly active customers",
                100000, 125000, 200000,
                "customers",
                IndicatorType.LAGGING,
                1.0,
                true
            ));

            service.addObjective(company);

            Objective product = new Objective(
                "Improve mobile onboarding",
                "Product Director",
                "Product",
                "2026-Q4",
                company.id(),
                "Reduce friction in customer registration."
            );

            KeyResult usability = new KeyResult(
                "Usability tests completed",
                0, 10, 20,
                "tests",
                IndicatorType.LEADING,
                1.0,
                true
            );

            product.addKeyResult(usability);

            product.addKeyResult(new KeyResult(
                "Onboarding completion rate",
                40, 55, 80,
                "%",
                IndicatorType.LAGGING,
                1.0,
                true
            ));

            service.addObjective(product);

            service.activate(company.id());
            service.activate(product.id());

            service.updateKeyResult(
                product.id(),
                usability.id(),
                "Product Director",
                16
            );

            System.out.println("ORGANIZATION OKR REPORT");

            service.report().forEach(report ->
                System.out.println(report)
            );

            System.out.println("\nOBJECTIVE ALIGNMENT");

            service.alignmentTree(company.id()).forEach(
                System.out::println
            );

            System.out.println("\nAUDIT EVENTS");

            service.auditLog().forEach(System.out::println);

            try {
                service.updateKeyResult(
                    product.id(),
                    usability.id(),
                    "Unauthorized User",
                    18
                );
            } catch (AuthorizationException exception) {
                System.out.println(
                    "Expected authorization failure: " +
                    exception.getMessage()
                );
            }

        } catch (OKRException exception) {
            System.err.println("OKR failure: " + exception.getMessage());
            System.exit(1);
        }
    }
}
