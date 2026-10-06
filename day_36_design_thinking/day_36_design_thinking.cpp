#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

enum class Stage {
    Empathize,
    Define,
    Ideate,
    Prototype,
    Test
};

std::string stageName(Stage stage) {
    switch (stage) {
        case Stage::Empathize: return "Empathize";
        case Stage::Define: return "Define";
        case Stage::Ideate: return "Ideate";
        case Stage::Prototype: return "Prototype";
        case Stage::Test: return "Test";
    }
    throw std::logic_error("Unknown design stage");
}

struct User {
    std::string id;
    std::string role;
    std::string context;
};

struct Observation {
    std::string userId;
    std::string behavior;
    std::string painPoint;
    double evidenceStrength;
};

struct Insight {
    std::string statement;
    double confidence;
    std::vector<std::string> observationIds;
};

struct ProblemStatement {
    std::string user;
    std::string need;
    std::string insight;
    std::string successMeasure;
};

struct Idea {
    std::string name;
    std::string description;
    double userValue;
    double feasibility;
    double desirability;
    double risk;

    double score() const {
        return userValue * 0.40
             + feasibility * 0.25
             + desirability * 0.25
             - risk * 0.10;
    }
};

struct Prototype {
    std::string ideaName;
    std::string fidelity;
    std::vector<std::string> interactions;
    std::vector<std::string> assumptions;
};

struct TestResult {
    std::string participantId;
    std::string task;
    bool completed;
    double timeSeconds;
    int errors;
    int satisfaction;
    std::string observation;
};

class GovernanceExperienceEngine {
private:
    Stage currentStage = Stage::Empathize;
    std::vector<User> users;
    std::vector<Observation> observations;
    std::vector<Insight> insights;
    std::optional<ProblemStatement> problem;
    std::vector<Idea> ideas;
    std::optional<Prototype> prototype;
    std::vector<TestResult> tests;

    static double average(const std::vector<double>& values) {
        if (values.empty()) {
            throw std::invalid_argument("Cannot average an empty collection");
        }

        return std::accumulate(values.begin(), values.end(), 0.0)
             / static_cast<double>(values.size());
    }

public:
    void addUser(User user) {
        if (user.id.empty() || user.role.empty()) {
            throw std::invalid_argument("User requires an id and role");
        }
        users.push_back(std::move(user));
    }

    void addObservation(Observation observation) {
        if (observation.userId.empty() || observation.behavior.empty()) {
            throw std::invalid_argument("Observation requires a user and behavior");
        }

        if (observation.evidenceStrength < 0.0 ||
            observation.evidenceStrength > 1.0) {
            throw std::invalid_argument("Evidence strength must be between 0 and 1");
        }

        observations.push_back(std::move(observation));
    }

    void transition(Stage next) {
        const int current = static_cast<int>(currentStage);
        const int target = static_cast<int>(next);

        // The case study permits sequential progress but also permits
        // returning to an earlier stage after test evidence exposes a problem.
        if (target > current + 1) {
            throw std::logic_error(
                "A design stage cannot be skipped without completing the intervening stage"
            );
        }

        currentStage = next;
    }

    void synthesizeInsights() {
        if (observations.empty()) {
            throw std::logic_error("Empathy data is required before synthesis");
        }

        std::map<std::string, std::vector<const Observation*>> groups;

        for (const auto& observation : observations) {
            groups[observation.painPoint].push_back(&observation);
        }

        for (const auto& [painPoint, evidence] : groups) {
            std::vector<double> strengths;
            std::vector<std::string> ids;

            for (const auto* observation : evidence) {
                strengths.push_back(observation->evidenceStrength);
                ids.push_back(observation->userId);
            }

            insights.push_back({
                "Repeated evidence indicates that users experience: " + painPoint,
                average(strengths),
                ids
            });
        }
    }

    void defineProblem() {
        if (insights.empty()) {
            throw std::logic_error("Insights must exist before defining the problem");
        }

        const auto strongest = std::max_element(
            insights.begin(),
            insights.end(),
            [](const Insight& a, const Insight& b) {
                return a.confidence < b.confidence;
            }
        );

        problem = ProblemStatement{
            "Employees processing internal requests",
            "A contextual workflow that exposes state, evidence, and next action",
            strongest->statement,
            "Reduce processing time while maintaining decision accuracy"
        };
    }

    void addIdea(Idea idea) {
        if (idea.name.empty()) {
            throw std::invalid_argument("Idea requires a name");
        }

        for (double value : {
            idea.userValue,
            idea.feasibility,
            idea.desirability,
            idea.risk
        }) {
            if (value < 0.0 || value > 10.0) {
                throw std::invalid_argument("Idea scores must be between 0 and 10");
            }
        }

        ideas.push_back(std::move(idea));
    }

    void createPrototype() {
        if (ideas.empty()) {
            throw std::logic_error("Ideation must produce at least one idea");
        }

        const auto best = std::max_element(
            ideas.begin(),
            ideas.end(),
            [](const Idea& a, const Idea& b) {
                return a.score() < b.score();
            }
        );

        prototype = Prototype{
            best->name,
            "Medium fidelity",
            {
                "Filter the request queue",
                "Open request context",
                "Inspect decision evidence",
                "See blocking condition",
                "Perform the next workflow action"
            },
            {
                "Users can identify the next action without changing screens",
                "Approvers can access decision context at the point of decision",
                "Blocked requests reveal the information required for recovery"
            }
        };
    }

    void addTest(TestResult result) {
        if (result.participantId.empty() || result.task.empty()) {
            throw std::invalid_argument("Test requires a participant and task");
        }

        if (result.timeSeconds <= 0.0 ||
            result.errors < 0 ||
            result.satisfaction < 1 ||
            result.satisfaction > 5) {
            throw std::invalid_argument("Invalid usability test measurements");
        }

        tests.push_back(std::move(result));
    }

    void printInsights() const {
        std::cout << "\nEvidence synthesis\n";

        for (const auto& insight : insights) {
            std::cout << "- " << insight.statement
                      << " | confidence="
                      << std::fixed << std::setprecision(2)
                      << insight.confidence << '\n';
        }
    }

    void printIdeas() const {
        std::vector<const Idea*> ranked;

        for (const auto& idea : ideas) {
            ranked.push_back(&idea);
        }

        std::sort(
            ranked.begin(),
            ranked.end(),
            [](const Idea* a, const Idea* b) {
                return a->score() > b->score();
            }
        );

        std::cout << "\nIdeation ranking\n";

        for (const auto* idea : ranked) {
            std::cout << idea->name
                      << " | score="
                      << std::fixed << std::setprecision(2)
                      << idea->score()
                      << '\n';
        }
    }

    void evaluateTests() const {
        if (tests.empty()) {
            throw std::logic_error("No usability tests have been recorded");
        }

        double completion = 0.0;
        double errors = 0.0;
        double satisfaction = 0.0;

        std::vector<double> times;

        for (const auto& result : tests) {
            completion += result.completed ? 1.0 : 0.0;
            errors += result.errors;
            satisfaction += result.satisfaction;
            times.push_back(result.timeSeconds);
        }

        std::sort(times.begin(), times.end());

        const double medianTime = times[times.size() / 2];

        std::cout << "\nUsability test analysis\n";
        std::cout << "Completion rate: "
                  << std::fixed << std::setprecision(1)
                  << (completion / tests.size()) * 100.0
                  << "%\n";
        std::cout << "Median task time: "
                  << medianTime << " seconds\n";
        std::cout << "Average errors: "
                  << errors / tests.size() << '\n';
        std::cout << "Average satisfaction: "
                  << satisfaction / tests.size() << "/5\n";

        const auto failed = std::find_if(
            tests.begin(),
            tests.end(),
            [](const TestResult& result) {
                return !result.completed;
            }
        );

        if (failed != tests.end()) {
            std::cout << "Iteration trigger: "
                      << failed->observation << '\n';
        }
    }

    void printArchitecture() const {
        std::cout << "\nCase-study architecture\n";
        std::cout << "Observation evidence -> insight synthesis -> "
                     "problem framing -> alternative concepts -> "
                     "prototype -> behavioral testing -> iteration\n";

        if (problem) {
            std::cout << "Defined need: " << problem->need << '\n';
            std::cout << "Success measure: " << problem->successMeasure << '\n';
        }

        if (prototype) {
            std::cout << "Prototype: " << prototype->ideaName << '\n';
            std::cout << "Prototype fidelity: " << prototype->fidelity << '\n';
        }
    }
};

int main() {
    try {
        GovernanceExperienceEngine engine;

        engine.addUser({
            "U01",
            "Operations Analyst",
            "Processes a high volume of internal requests"
        });

        engine.addUser({
            "U02",
            "Finance Analyst",
            "Reviews requests requiring financial approval"
        });

        engine.addUser({
            "U03",
            "Team Manager",
            "Monitors blocked work and operational queues"
        });

        engine.addObservation({
            "U01",
            "Copies queue information into a personal spreadsheet",
            "Request state is difficult to see",
            0.95
        });

        engine.addObservation({
            "U01",
            "Switches between applications to find request context",
            "Information is fragmented",
            0.90
        });

        engine.addObservation({
            "U02",
            "Delays an approval when evidence is incomplete",
            "Decision context is incomplete",
            0.92
        });

        engine.addObservation({
            "U03",
            "Contacts analysts to discover why work is blocked",
            "Metrics do not explain blockers",
            0.88
        });

        std::cout << "Current stage: "
                  << stageName(Stage::Empathize) << '\n';

        engine.synthesizeInsights();
        engine.printInsights();

        engine.transition(Stage::Define);
        engine.defineProblem();

        engine.transition(Stage::Ideate);

        engine.addIdea({
            "Contextual Request Workspace",
            "A unified view of request state, evidence, history, and next action",
            9.0,
            8.0,
            9.0,
            3.0
        });

        engine.addIdea({
            "Decision Summary Panel",
            "A focused approval surface containing purpose, evidence, and exceptions",
            8.0,
            9.0,
            8.0,
            2.0
        });

        engine.addIdea({
            "Blocker Explanation Engine",
            "A workflow component that explains exactly why a request cannot proceed",
            8.0,
            7.0,
            7.0,
            5.0
        });

        engine.printIdeas();

        engine.transition(Stage::Prototype);
        engine.createPrototype();

        engine.transition(Stage::Test);

        engine.addTest({
            "U01",
            "Find the next processable request",
            true,
            38.0,
            1,
            4,
            "The state filter was easy to find, but one label caused hesitation"
        });

        engine.addTest({
            "U02",
            "Approve a request using the available evidence",
            true,
            46.0,
            0,
            5,
            "The decision context was available without leaving the request"
        });

        engine.addTest({
            "U03",
            "Identify why a request is blocked",
            false,
            71.0,
            3,
            2,
            "The blocked state was visible, but the missing information was unclear"
        });

        engine.evaluateTests();
        engine.printArchitecture();

        std::cout << "\nDesign decision\n";
        std::cout << "The prototype should be revised so that a blocked request "
                     "exposes both the missing information and the recovery action.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Design workflow error: "
                  << error.what() << '\n';
        return 1;
    }
}
