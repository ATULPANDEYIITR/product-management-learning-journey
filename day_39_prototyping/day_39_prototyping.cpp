#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Repository-independent prototype case study:
 * an enterprise expense-management team evaluates three prototype fidelity
 * levels using a task-flow model and measured usability evidence.
 *
 * Compile: g++ -std=c++17 -Wall -Wextra -pedantic prototype_case.cpp -o prototype_case
 */

enum class Fidelity { Low, Medium, High };
enum class ScreenState { Dashboard, Form, Loading, Confirmation, History };
enum class TaskOutcome { Completed, Failed, Abandoned };

std::string to_string(Fidelity fidelity) {
    switch (fidelity) {
        case Fidelity::Low: return "Low fidelity";
        case Fidelity::Medium: return "Medium fidelity";
        case Fidelity::High: return "High fidelity";
    }
    throw std::logic_error("Unknown fidelity.");
}

std::string to_string(ScreenState state) {
    switch (state) {
        case ScreenState::Dashboard: return "Dashboard";
        case ScreenState::Form: return "Expense form";
        case ScreenState::Loading: return "Submitting";
        case ScreenState::Confirmation: return "Confirmation";
        case ScreenState::History: return "Expense history";
    }
    throw std::logic_error("Unknown screen state.");
}

struct Element {
    std::string id;
    std::string label;
    bool interactive;
};

struct Screen {
    std::string id;
    std::vector<Element> elements;
};

class PrototypeArtifact {
public:
    PrototypeArtifact(
        std::string id,
        Fidelity fidelity,
        std::string research_question,
        std::vector<Screen> screens
    )
        : id_(std::move(id)),
          fidelity_(fidelity),
          research_question_(std::move(research_question)),
          screens_(std::move(screens)) {
        if (id_.empty() || research_question_.empty() || screens_.empty()) {
            throw std::invalid_argument(
                "A prototype requires an ID, research question, and screens."
            );
        }

        std::set<std::string> screen_ids;
        for (const auto& screen : screens_) {
            if (screen.id.empty() || !screen_ids.insert(screen.id).second) {
                throw std::invalid_argument("Screen IDs must be unique.");
            }
            std::set<std::string> element_ids;
            for (const auto& element : screen.elements) {
                if (element.id.empty() ||
                    !element_ids.insert(element.id).second) {
                    throw std::invalid_argument(
                        "Element IDs must be unique within each screen."
                    );
                }
            }
        }
    }

    std::size_t screen_count() const {
        return screens_.size();
    }

    std::size_t interactive_element_count() const {
        std::size_t count = 0;
        for (const auto& screen : screens_) {
            count += static_cast<std::size_t>(
                std::count_if(
                    screen.elements.begin(),
                    screen.elements.end(),
                    [](const Element& element) {
                        return element.interactive;
                    }
                )
            );
        }
        return count;
    }

    void print() const {
        std::cout << id_ << " | " << to_string(fidelity_)
                  << " | screens=" << screen_count()
                  << " | interactive elements="
                  << interactive_element_count() << '\n'
                  << "  Research question: " << research_question_ << '\n';
    }

private:
    std::string id_;
    Fidelity fidelity_;
    std::string research_question_;
    std::vector<Screen> screens_;
};

struct Expense {
    unsigned long id;
    std::string description;
    double amount;
    std::string category;
};

class ExpenseLedger {
public:
    Expense submit(
        const std::string& description,
        double amount,
        const std::string& category
    ) {
        if (description.find_first_not_of(" \t\n") == std::string::npos) {
            throw std::invalid_argument("Description is required.");
        }
        if (category.find_first_not_of(" \t\n") == std::string::npos) {
            throw std::invalid_argument("Category is required.");
        }
        if (!std::isfinite(amount) || amount <= 0.0 || amount > 1'000'000.0) {
            throw std::invalid_argument(
                "Amount must be finite and between 0 and 1,000,000."
            );
        }

        // Store integer cents to avoid accumulating binary floating-point
        // rounding errors in the ledger total.
        const auto cents = static_cast<long long>(std::llround(amount * 100.0));
        const Expense expense{
            next_id_++,
            description,
            static_cast<double>(cents) / 100.0,
            category
        };
        expenses_.push_back(expense);
        total_cents_ += cents;
        return expense;
    }

    double total() const {
        return static_cast<double>(total_cents_) / 100.0;
    }

    const std::vector<Expense>& expenses() const {
        return expenses_;
    }

private:
    unsigned long next_id_ = 1;
    long long total_cents_ = 0;
    std::vector<Expense> expenses_;
};

class PrototypeSession {
public:
    explicit PrototypeSession(ExpenseLedger& ledger) : ledger_(ledger) {}

    bool navigate(ScreenState destination) {
        const std::map<ScreenState, std::set<ScreenState>> routes{
            {ScreenState::Dashboard,
             {ScreenState::Form, ScreenState::History}},
            {ScreenState::Form, {ScreenState::Dashboard}},
            {ScreenState::Confirmation,
             {ScreenState::Dashboard, ScreenState::History}},
            {ScreenState::History, {ScreenState::Dashboard}},
            {ScreenState::Loading, {}}
        };

        if (routes.at(state_).count(destination) == 0) {
            last_error_ = "Unsupported navigation from " + to_string(state_) +
                          " to " + to_string(destination);
            return false;
        }

        state_ = destination;
        last_error_.clear();
        return true;
    }

    bool submit(
        const std::string& description,
        double amount,
        const std::string& category
    ) {
        if (state_ != ScreenState::Form) {
            last_error_ = "Open the expense form before submitting.";
            return false;
        }
        if (pending_) {
            last_error_ = "A submission is already in progress.";
            return false;
        }

        pending_ = true;
        state_ = ScreenState::Loading;

        try {
            const Expense result = ledger_.submit(description, amount, category);
            last_receipt_ = result.id;
            state_ = ScreenState::Confirmation;
            last_error_.clear();
            pending_ = false;
            return true;
        } catch (const std::invalid_argument& error) {
            // A validation failure must not strand the interface in a loading
            // state; the user needs a path back to the editable form.
            last_error_ = error.what();
            state_ = ScreenState::Form;
            pending_ = false;
            return false;
        }
    }

    ScreenState state() const { return state_; }
    const std::string& last_error() const { return last_error_; }
    std::optional<unsigned long> receipt() const { return last_receipt_; }

private:
    ExpenseLedger& ledger_;
    ScreenState state_ = ScreenState::Dashboard;
    bool pending_ = false;
    std::optional<unsigned long> last_receipt_;
    std::string last_error_;
};

struct UsabilityObservation {
    std::string participant;
    std::string task;
    TaskOutcome outcome;
    double duration_seconds;
    unsigned errors;
    unsigned confidence; // Five-point self-reported confidence scale.
};

class UsabilityStudy {
public:
    void add(UsabilityObservation observation) {
        if (observation.participant.empty() || observation.task.empty()) {
            throw std::invalid_argument("Participant and task are required.");
        }
        if (!std::isfinite(observation.duration_seconds) ||
            observation.duration_seconds < 0.0) {
            throw std::invalid_argument("Duration must be finite and non-negative.");
        }
        if (observation.confidence < 1 || observation.confidence > 5) {
            throw std::invalid_argument("Confidence must be between one and five.");
        }
        observations_.push_back(std::move(observation));
    }

    void report() const {
        if (observations_.empty()) {
            throw std::logic_error("Cannot report an empty usability study.");
        }

        const auto completed = std::count_if(
            observations_.begin(),
            observations_.end(),
            [](const UsabilityObservation& item) {
                return item.outcome == TaskOutcome::Completed;
            }
        );

        double duration_sum = 0.0;
        unsigned error_sum = 0;
        unsigned confidence_sum = 0;
        for (const auto& item : observations_) {
            duration_sum += item.duration_seconds;
            error_sum += item.errors;
            confidence_sum += item.confidence;
        }

        const double completion_rate =
            static_cast<double>(completed) / observations_.size();

        std::cout << std::fixed << std::setprecision(2)
                  << "Participants/tasks: " << observations_.size() << '\n'
                  << "Task completion rate: " << completion_rate * 100.0 << "%\n"
                  << "Mean duration: "
                  << duration_sum / observations_.size() << " seconds\n"
                  << "Total observed errors: " << error_sum << '\n'
                  << "Mean confidence: "
                  << static_cast<double>(confidence_sum) /
                         observations_.size()
                  << " / 5\n";

        if (completion_rate < 0.90) {
            std::cout << "Research decision: investigate task comprehension.\n";
        }
        if (error_sum > observations_.size()) {
            std::cout << "Research decision: inspect validation and recovery.\n";
        }
    }

private:
    std::vector<UsabilityObservation> observations_;
};

int main() {
    try {
        std::vector<PrototypeArtifact> prototypes;

        prototypes.emplace_back(
            "paper-expense",
            Fidelity::Low,
            "Can employees find the primary expense action?",
            std::vector<Screen>{
                {"dashboard", {{"summary", "Expense summary", false},
                               {"submit", "Submit expense", false}}},
                {"form", {{"amount", "Amount", false},
                          {"description", "Description", false}}}
            }
        );

        prototypes.emplace_back(
            "clickable-expense",
            Fidelity::Medium,
            "Can employees complete the form without guidance?",
            std::vector<Screen>{
                {"dashboard", {{"submit", "Submit expense", true}}},
                {"form", {{"amount", "Amount input", true},
                          {"description", "Description input", true},
                          {"category", "Category selector", true}}}
            }
        );

        prototypes.emplace_back(
            "realistic-expense",
            Fidelity::High,
            "Does realistic submission feedback prevent duplicate actions?",
            std::vector<Screen>{
                {"dashboard", {{"summary", "Expense summary", true}}},
                {"form", {{"amount", "Validated amount", true},
                          {"submit", "Loading-aware submit button", true}}},
                {"confirmation", {{"receipt", "Submission receipt", false}}}
            }
        );

        std::cout << "Prototype fidelity artifacts\n";
        for (const auto& prototype : prototypes) {
            prototype.print();
        }

        ExpenseLedger ledger;
        PrototypeSession session(ledger);

        std::cout << "\nInteraction experiment\n";
        std::cout << "Navigate to form: "
                  << std::boolalpha << session.navigate(ScreenState::Form) << '\n';

        const bool first = session.submit("Regional travel", 1250.50, "Travel");
        std::cout << "Valid submission: " << first
                  << ", screen=" << to_string(session.state()) << '\n';

        if (session.receipt()) {
            std::cout << "Receipt ID: " << *session.receipt() << '\n';
        }

        session.navigate(ScreenState::Dashboard);
        session.navigate(ScreenState::Form);
        const bool second = session.submit("Office supplies", -25.0, "Operations");
        std::cout << "Invalid submission: " << second
                  << ", screen=" << to_string(session.state())
                  << ", reason=" << session.last_error() << '\n';

        std::cout << "Ledger entries: " << ledger.expenses().size()
                  << ", total: " << ledger.total() << '\n';

        UsabilityStudy study;
        study.add({"employee-A", "submit-expense", TaskOutcome::Completed,
                   24.0, 0, 5});
        study.add({"employee-B", "submit-expense", TaskOutcome::Completed,
                   39.0, 1, 4});
        study.add({"employee-C", "submit-expense", TaskOutcome::Abandoned,
                   60.0, 3, 2});

        std::cout << "\nUsability evidence\n";
        study.report();

        // Verify invariants so the demonstration detects silent regressions.
        if (ledger.expenses().size() != 1 ||
            std::abs(ledger.total() - 1250.50) > 0.001 ||
            session.state() != ScreenState::Form) {
            throw std::runtime_error("Prototype experiment invariant failed.");
        }

        std::cout << "\nAll case-study invariants passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Case study failed: " << error.what() << '\n';
        return 1;
    }
}
