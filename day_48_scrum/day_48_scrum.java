import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise Scrum model for an online banking delivery team.
 * Requires Java 17 or later.
 *
 * Domain types make role accountabilities, backlog state, Sprint Goal,
 * Increment acceptance, and event sequencing explicit.
 */

public class ScrumEnterpriseDemo {

    enum Accountability {
        PRODUCT_OWNER,
        SCRUM_MASTER,
        DEVELOPER
    }

    enum WorkStatus {
        TO_DO,
        IN_PROGRESS,
        DONE
    }

    enum SprintEvent {
        SPRINT_PLANNING,
        DAILY_SCRUM,
        SPRINT_REVIEW,
        SPRINT_RETROSPECTIVE
    }

    record TeamMember(String name, Accountability accountability) {
        TeamMember {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Member name is required.");
            }
            Objects.requireNonNull(accountability, "Accountability is required.");
        }
    }

    static final class ProductBacklogItem {
        private final String id;
        private final String title;
        private final int priority;
        private final int estimate;
        private final List<String> acceptanceCriteria;
        private WorkStatus status = WorkStatus.TO_DO;
        private boolean accepted;

        ProductBacklogItem(
                String id,
                String title,
                int priority,
                int estimate,
                List<String> acceptanceCriteria) {
            if (id == null || id.isBlank() || title == null || title.isBlank()) {
                throw new IllegalArgumentException("Item ID and title are required.");
            }
            if (priority < 1 || estimate < 0) {
                throw new IllegalArgumentException("Invalid priority or estimate.");
            }
            if (acceptanceCriteria == null || acceptanceCriteria.isEmpty()) {
                throw new IllegalArgumentException("Acceptance criteria are required.");
            }

            this.id = id;
            this.title = title;
            this.priority = priority;
            this.estimate = estimate;
            this.acceptanceCriteria = List.copyOf(acceptanceCriteria);
        }

        String id() {
            return id;
        }

        String title() {
            return title;
        }

        int priority() {
            return priority;
        }

        int estimate() {
            return estimate;
        }

        WorkStatus status() {
            return status;
        }

        boolean accepted() {
            return accepted;
        }

        void transitionTo(WorkStatus next) {
            Objects.requireNonNull(next, "Next status is required.");

            boolean allowed =
                    (status == WorkStatus.TO_DO && next == WorkStatus.IN_PROGRESS)
                    || (status == WorkStatus.IN_PROGRESS
                        && (next == WorkStatus.DONE || next == WorkStatus.TO_DO));

            if (!allowed) {
                throw new IllegalStateException(
                        "Invalid transition for " + id + ": " + status + " -> " + next);
            }
            status = next;
        }

        void markAccepted() {
            if (status != WorkStatus.DONE) {
                throw new IllegalStateException(
                        "Only completed work can enter the Increment.");
            }
            accepted = true;
        }

        void returnToProductBacklog() {
            status = WorkStatus.TO_DO;
            accepted = false;
        }

        List<String> acceptanceCriteria() {
            return acceptanceCriteria;
        }
    }

    record SprintGoal(String statement) {
        SprintGoal {
            if (statement == null || statement.isBlank()) {
                throw new IllegalArgumentException("Sprint Goal cannot be empty.");
            }
        }
    }

    record ScrumEvent(
            SprintEvent type,
            LocalDate date,
            String description) {
        ScrumEvent {
            Objects.requireNonNull(type);
            Objects.requireNonNull(date);
            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException("Event description is required.");
            }
        }
    }

    static final class Sprint {
        private final int number;
        private final LocalDate startDate;
        private final int durationDays;
        private final SprintGoal goal;
        private final List<ProductBacklogItem> selected;
        private final List<String> impediments = new ArrayList<>();
        private boolean reviewCompleted;
        private boolean retrospectiveCompleted;
        private boolean closed;

        Sprint(
                int number,
                LocalDate startDate,
                int durationDays,
                SprintGoal goal,
                List<ProductBacklogItem> selected) {
            if (number < 1 || durationDays < 1 || durationDays > 30) {
                throw new IllegalArgumentException("Invalid sprint number or duration.");
            }
            this.number = number;
            this.startDate = Objects.requireNonNull(startDate);
            this.durationDays = durationDays;
            this.goal = Objects.requireNonNull(goal);
            this.selected = new ArrayList<>(selected);
        }

        LocalDate endDate() {
            return startDate.plusDays(durationDays - 1L);
        }

        int plannedPoints() {
            return selected.stream().mapToInt(ProductBacklogItem::estimate).sum();
        }

        int acceptedPoints() {
            return selected.stream()
                    .filter(ProductBacklogItem::accepted)
                    .mapToInt(ProductBacklogItem::estimate)
                    .sum();
        }
    }

    static final class ScrumService {
        private final String product;
        private final TeamMember productOwner;
        private final TeamMember scrumMaster;
        private final List<TeamMember> developers;
        private final List<ProductBacklogItem> productBacklog;
        private final List<ProductBacklogItem> increment = new ArrayList<>();
        private final List<ScrumEvent> eventHistory = new ArrayList<>();
        private final List<String> improvementActions = new ArrayList<>();
        private Sprint currentSprint;

        ScrumService(
                String product,
                TeamMember productOwner,
                TeamMember scrumMaster,
                List<TeamMember> developers,
                List<ProductBacklogItem> backlog) {
            if (product == null || product.isBlank()) {
                throw new IllegalArgumentException("Product name is required.");
            }
            this.product = product;
            this.productOwner = requireRole(
                    productOwner, Accountability.PRODUCT_OWNER);
            this.scrumMaster = requireRole(
                    scrumMaster, Accountability.SCRUM_MASTER);

            if (developers == null || developers.isEmpty()) {
                throw new IllegalArgumentException("At least one Developer is required.");
            }
            this.developers = List.copyOf(developers);
            for (TeamMember developer : this.developers) {
                requireRole(developer, Accountability.DEVELOPER);
            }

            Set<String> names = new HashSet<>();
            names.add(productOwner.name());
            names.add(scrumMaster.name());
            for (TeamMember developer : developers) {
                if (!names.add(developer.name())) {
                    throw new IllegalArgumentException("Team member names must be unique.");
                }
            }

            this.productBacklog = new ArrayList<>(backlog);
            Set<String> ids = new HashSet<>();
            for (ProductBacklogItem item : productBacklog) {
                if (!ids.add(item.id())) {
                    throw new IllegalArgumentException("Duplicate backlog item: " + item.id());
                }
            }
        }

        private static TeamMember requireRole(
                TeamMember member, Accountability expected) {
            Objects.requireNonNull(member, "Team member is required.");
            if (member.accountability() != expected) {
                throw new IllegalArgumentException(
                        "Expected accountability: " + expected);
            }
            return member;
        }

        private void requireActiveSprint() {
            if (currentSprint == null || currentSprint.closed) {
                throw new IllegalStateException("No active sprint.");
            }
        }

        void refineProductBacklog() {
            productBacklog.sort(
                    Comparator.comparingInt(ProductBacklogItem::priority)
                            .thenComparing(ProductBacklogItem::id));

            System.out.println("\nProduct Backlog");
            productBacklog.forEach(item ->
                    System.out.printf(
                            "%s | %s | priority=%d | estimate=%d%n",
                            item.id(), item.title(), item.priority(), item.estimate()));
        }

        Sprint planSprint(
                int number,
                LocalDate startDate,
                int durationDays,
                int capacity,
                String goalText) {
            if (currentSprint != null && !currentSprint.closed) {
                throw new IllegalStateException("Close the current sprint first.");
            }
            if (capacity < 0) {
                throw new IllegalArgumentException("Capacity cannot be negative.");
            }

            SprintGoal goal = new SprintGoal(goalText);
            List<ProductBacklogItem> selected = new ArrayList<>();
            int remaining = capacity;

            // Priority determines selection order; estimates constrain the
            // feasible plan. Actual delivery remains uncertain.
            for (ProductBacklogItem item : productBacklog) {
                if (item.status() == WorkStatus.TO_DO && item.estimate() <= remaining) {
                    selected.add(item);
                    remaining -= item.estimate();
                }
            }

            currentSprint = new Sprint(number, startDate, durationDays, goal, selected);
            record(
                    SprintEvent.SPRINT_PLANNING,
                    startDate,
                    "Goal: " + goal.statement() + "; selected " + selected.size() + " items.");

            System.out.printf(
                    "Sprint %d: %s%nPlanned points: %d, remaining capacity: %d%n",
                    number, goal.statement(), currentSprint.plannedPoints(), remaining);

            return currentSprint;
        }

        private ProductBacklogItem findSprintItem(String id) {
            requireActiveSprint();
            return currentSprint.selected.stream()
                    .filter(item -> item.id().equals(id))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException(
                            id + " is not in the Sprint Backlog."));
        }

        void updateWork(String id, WorkStatus status) {
            ProductBacklogItem item = findSprintItem(id);
            item.transitionTo(status);
            record(
                    SprintEvent.DAILY_SCRUM,
                    LocalDate.now(),
                    id + " changed to " + status);
        }

        void dailyScrum(LocalDate eventDate, List<String> impediments) {
            requireActiveSprint();
            if (eventDate.isBefore(currentSprint.startDate)
                    || eventDate.isAfter(currentSprint.endDate())) {
                throw new IllegalArgumentException(
                        "Daily Scrum date must fall within the sprint.");
            }

            for (String impediment : impediments) {
                if (impediment != null && !impediment.isBlank()
                        && !currentSprint.impediments.contains(impediment)) {
                    currentSprint.impediments.add(impediment);
                }
            }

            long done = currentSprint.selected.stream()
                    .filter(item -> item.status() == WorkStatus.DONE)
                    .count();

            record(
                    SprintEvent.DAILY_SCRUM,
                    eventDate,
                    "Progress toward goal: " + done + "/"
                            + currentSprint.selected.size() + " items implemented.");

            currentSprint.impediments.forEach(
                    item -> System.out.println("Impediment: " + item));
        }

        void sprintReview(List<String> feedback) {
            requireActiveSprint();
            if (currentSprint.reviewCompleted) {
                throw new IllegalStateException("Sprint Review already completed.");
            }

            for (ProductBacklogItem item : currentSprint.selected) {
                if (item.status() == WorkStatus.DONE) {
                    item.markAccepted();
                    increment.add(item);
                } else {
                    item.returnToProductBacklog();
                }
            }

            currentSprint.reviewCompleted = true;
            record(
                    SprintEvent.SPRINT_REVIEW,
                    LocalDate.now(),
                    "Stakeholders inspected the Increment. Feedback: " + feedback);

            System.out.printf(
                    "Accepted Increment: %d points%n",
                    currentSprint.acceptedPoints());
        }

        void retrospective(List<String> actions) {
            requireActiveSprint();
            if (!currentSprint.reviewCompleted) {
                throw new IllegalStateException(
                        "Sprint Review must be completed first.");
            }
            if (currentSprint.retrospectiveCompleted) {
                throw new IllegalStateException("Retrospective already completed.");
            }

            actions.stream()
                    .filter(Objects::nonNull)
                    .map(String::trim)
                    .filter(action -> !action.isEmpty())
                    .forEach(improvementActions::add);

            currentSprint.retrospectiveCompleted = true;
            record(
                    SprintEvent.SPRINT_RETROSPECTIVE,
                    LocalDate.now(),
                    "Improvement actions recorded: " + improvementActions);
        }

        void closeSprint() {
            requireActiveSprint();
            if (!currentSprint.reviewCompleted
                    || !currentSprint.retrospectiveCompleted) {
                throw new IllegalStateException(
                        "Review and retrospective are required before closure.");
            }
            currentSprint.closed = true;
            System.out.println("Sprint " + currentSprint.number + " closed.");
        }

        private void record(SprintEvent type, LocalDate date, String description) {
            ScrumEvent event = new ScrumEvent(type, date, description);
            eventHistory.add(event);
            System.out.println("[" + type + "] " + description);
        }

        void report() {
            System.out.println("\nEnterprise Delivery Report");
            System.out.println("Product: " + product);
            System.out.println("Product Owner: " + productOwner.name());
            System.out.println("Scrum Master: " + scrumMaster.name());
            System.out.println("Developers: " + developers.size());
            System.out.println("Product Backlog items: " + productBacklog.size());
            System.out.println("Increment items: " + increment.size());
            System.out.println("Recorded Scrum events: " + eventHistory.size());
            System.out.println("Improvement actions: " + improvementActions.size());
        }
    }

    public static void main(String[] args) {
        TeamMember owner = new TeamMember("Maya", Accountability.PRODUCT_OWNER);
        TeamMember master = new TeamMember("Arjun", Accountability.SCRUM_MASTER);

        List<TeamMember> developers = List.of(
                new TeamMember("Neha", Accountability.DEVELOPER),
                new TeamMember("Kabir", Accountability.DEVELOPER),
                new TeamMember("Sara", Accountability.DEVELOPER));

        List<ProductBacklogItem> backlog = List.of(
                new ProductBacklogItem(
                        "BANK-401", "Validate transfer payload", 1, 5,
                        List.of("Reject malformed payload", "Validate beneficiary")),
                new ProductBacklogItem(
                        "BANK-402", "Persist audit events", 2, 8,
                        List.of("Record transfer outcome", "Store correlation ID")),
                new ProductBacklogItem(
                        "BANK-403", "Expose transfer status", 3, 3,
                        List.of("Authorized customer can query status")));

        ScrumService service = new ScrumService(
                "Digital Banking Reliability", owner, master, developers, backlog);

        service.refineProductBacklog();

        Sprint sprint = service.planSprint(
                1,
                LocalDate.of(2026, 10, 19),
                10,
                16,
                "Make bank transfers safer through validation and traceability.");

        if (!sprint.selected.isEmpty()) {
            String firstItem = sprint.selected.get(0).id();
            service.updateWork(firstItem, WorkStatus.IN_PROGRESS);
            service.updateWork(firstItem, WorkStatus.DONE);
        }

        service.dailyScrum(
                LocalDate.of(2026, 10, 19),
                List.of("Representative failure fixtures are not ready."));

        service.sprintReview(List.of(
                "Confirm validation behavior for malformed transfer requests."));

        service.retrospective(List.of(
                "Prepare failure fixtures before development.",
                "Clarify audit-event acceptance criteria during refinement."));

        service.closeSprint();
        service.report();

        try {
            service.updateWork("UNKNOWN", WorkStatus.IN_PROGRESS);
        } catch (IllegalArgumentException exception) {
            System.out.println("Expected validation failure: " + exception.getMessage());
        }
    }
}
