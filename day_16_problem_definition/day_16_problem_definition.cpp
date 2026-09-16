#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

/*
 * Problem Definition
 *
 * Technical case study:
 * Reliable online examination submission system
 *
 * The program demonstrates:
 * - problem statements
 * - symptoms versus root causes
 * - causal hypotheses
 * - problem framing
 * - problem boundaries
 * - evidence classification
 * - constraints
 * - measurable gaps
 * - stakeholder perspectives
 * - causal investigation
 * - data analysis
 * - validation
 * - complexity
 * - defensive design
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic problem_definition.cpp -o problem_definition
 */

// -----------------------------------------------------------------------------
// 1. GENERAL UTILITIES
// -----------------------------------------------------------------------------

void printSection(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

void printSubsection(const string& title) {
    cout << "\n" << string(78, '-') << "\n";
    cout << title << "\n";
    cout << string(78, '-') << "\n";
}

string percent(double value) {
    ostringstream output;
    output << fixed << setprecision(2) << value * 100.0 << "%";
    return output.str();
}

string number(double value) {
    ostringstream output;
    output << fixed << setprecision(2) << value;
    return output.str();
}


// -----------------------------------------------------------------------------
// 2. PROBLEM STATEMENT
// -----------------------------------------------------------------------------

struct ProblemStatement {
    string affectedActor;
    string currentCondition;
    string measurableGap;
    string consequence;
    vector<string> evidence;
    optional<string> timeframe;
    optional<string> scope;

    vector<string> validate() const {
        vector<string> errors;

        if (affectedActor.empty()) {
            errors.push_back("Affected actor is missing.");
        }

        if (currentCondition.empty()) {
            errors.push_back("Current condition is missing.");
        }

        if (measurableGap.empty()) {
            errors.push_back("Measurable gap is missing.");
        }

        if (consequence.empty()) {
            errors.push_back("Consequence is missing.");
        }

        if (evidence.empty()) {
            errors.push_back("Evidence is missing.");
        }

        return errors;
    }

    string render() const {
        ostringstream output;

        output << affectedActor << " is experiencing "
               << currentCondition << ". "
               << "The measurable gap is " << measurableGap << ". "
               << "This matters because " << consequence << ".";

        if (scope.has_value()) {
            output << " Scope: " << scope.value() << ".";
        }

        if (timeframe.has_value()) {
            output << " Timeframe: " << timeframe.value() << ".";
        }

        return output.str();
    }
};

void demonstrateProblemStatement() {
    printSection("1. Problem statement fundamentals");

    cout << "Weak statement:\n";
    cout << "The website needs a better checkout system.\n";

    ProblemStatement strong{
        "Online customers",
        "abandon purchases during checkout",
        "checkout completion is 61% compared with a target of 75%",
        "completed orders are lost and support demand increases",
        {
            "Analytics show a 39% abandonment rate.",
            "Session analysis shows repeated validation failures.",
            "Interviews indicate uncertainty about delivery charges."
        },
        "the last three months",
        "the web checkout flow"
    };

    cout << "\nStructured statement:\n";
    cout << strong.render() << "\n";

    cout << "\nValidation:\n";

    const auto errors = strong.validate();

    if (errors.empty()) {
        cout << "PASS\n";
    } else {
        for (const auto& error : errors) {
            cout << "FAIL: " << error << "\n";
        }
    }
}


// -----------------------------------------------------------------------------
// 3. SYMPTOMS AND ROOT CAUSES
// -----------------------------------------------------------------------------

enum class CausalType {
    ObservableProblem,
    Symptom,
    ContributingCause,
    RootCauseCandidate,
    SystemicCause
};

string causalTypeName(CausalType type) {
    switch (type) {
        case CausalType::ObservableProblem:
            return "observable problem";
        case CausalType::Symptom:
            return "symptom";
        case CausalType::ContributingCause:
            return "contributing cause";
        case CausalType::RootCauseCandidate:
            return "root cause candidate";
        case CausalType::SystemicCause:
            return "systemic cause";
    }

    return "unknown";
}

struct CausalNode {
    string name;
    CausalType type;
    vector<CausalNode> children;

    CausalNode(string nodeName, CausalType nodeType)
        : name(std::move(nodeName)), type(nodeType) {}

    CausalNode& addChild(CausalNode child) {
        children.push_back(std::move(child));
        return children.back();
    }
};

void printCausalTree(const CausalNode& node, int depth = 0) {
    cout << string(depth * 2, ' ')
         << "- [" << causalTypeName(node.type) << "] "
         << node.name << "\n";

    for (const auto& child : node.children) {
        printCausalTree(child, depth + 1);
    }
}

void demonstrateSymptomsAndCauses() {
    printSection("2. Symptoms versus root causes");

    CausalNode root(
        "Customer support backlog increased",
        CausalType::ObservableProblem
    );

    auto& symptom = root.addChild(
        CausalNode(
            "Average response time increased from 6 to 21 hours",
            CausalType::Symptom
        )
    );

    auto& routingCause = symptom.addChild(
        CausalNode(
            "Tickets are routed to incorrect queues",
            CausalType::ContributingCause
        )
    );

    auto& taxonomyCause = routingCause.addChild(
        CausalNode(
            "Routing rules use an obsolete service taxonomy",
            CausalType::RootCauseCandidate
        )
    );

    taxonomyCause.addChild(
        CausalNode(
            "No recurring process reviews routing accuracy",
            CausalType::SystemicCause
        )
    );

    printCausalTree(root);

    cout << "\nA symptom is observable evidence. A root cause is a causal "
         << "explanation that must be supported by evidence. Multiple causes "
         << "may interact.\n";
}


// -----------------------------------------------------------------------------
// 4. FIVE WHYS
// -----------------------------------------------------------------------------

struct WhyStep {
    int number;
    string condition;
    string answer;
};

vector<WhyStep> fiveWhys(
    const string& initialProblem,
    const vector<string>& answers
) {
    vector<WhyStep> steps;
    string current = initialProblem;

    for (size_t i = 0; i < answers.size(); ++i) {
        steps.push_back({
            static_cast<int>(i + 1),
            current,
            answers[i]
        });

        current = answers[i];
    }

    return steps;
}

void demonstrateFiveWhys() {
    printSection("3. Five Whys");

    const vector<string> answers{
        "Warehouse picking begins later than planned.",
        "Picking waits for manual payment-status confirmation.",
        "Payment exceptions are checked in another system.",
        "The systems do not exchange exception status automatically.",
        "The integration was never designed for exception-state synchronization."
    };

    const auto steps = fiveWhys(
        "Orders are shipped late.",
        answers
    );

    for (const auto& step : steps) {
        cout << "Why " << step.number << ": Why does '"
             << step.condition << "' occur?\n";
        cout << "Answer: " << step.answer << "\n";
    }

    cout << "\nFive Whys generates a causal hypothesis. The final answer "
         << "requires validation before being called the root cause.\n";
}


// -----------------------------------------------------------------------------
// 5. PROBLEM FRAME
// -----------------------------------------------------------------------------

struct ProblemFrame {
    string actor;
    string desiredOutcome;
    string currentState;
    string gap;
    string context;
    vector<string> constraints;
    vector<string> assumptions;
    vector<string> exclusions;
    map<string, string> successMetrics;

    string render() const {
        ostringstream output;

        output << "Actor: " << actor << "\n";
        output << "Desired outcome: " << desiredOutcome << "\n";
        output << "Current state: " << currentState << "\n";
        output << "Gap: " << gap << "\n";
        output << "Context: " << context << "\n";

        output << "Constraints:\n";
        for (const auto& item : constraints) {
            output << "  - " << item << "\n";
        }

        output << "Assumptions:\n";
        for (const auto& item : assumptions) {
            output << "  - " << item << "\n";
        }

        output << "Exclusions:\n";
        for (const auto& item : exclusions) {
            output << "  - " << item << "\n";
        }

        output << "Success metrics:\n";
        for (const auto& [name, definition] : successMetrics) {
            output << "  - " << name << ": " << definition << "\n";
        }

        return output.str();
    }
};

ProblemFrame createExaminationFrame() {
    return {
        "Students using an examination portal",
        "complete legitimate submissions before the deadline",
        "submissions sometimes fail or remain pending during peak traffic",
        "successful submission rate falls below the operational target during peak periods",
        "online examinations with concentrated submission activity",
        {
            "Existing authentication must remain unchanged.",
            "Exam deadlines cannot be extended automatically.",
            "Student records must remain protected.",
            "Infrastructure spending is constrained."
        },
        {
            "Examination rules are correct.",
            "Student home internet is outside institutional control.",
            "Submission events are timestamped accurately."
        },
        {
            "Changing examination policy.",
            "Replacing the identity provider.",
            "Diagnosing individual home networks."
        },
        {
            {
                "submission success rate",
                "successful final submissions divided by final attempts"
            },
            {
                "p95 submission latency",
                "95th percentile time to acknowledge a submission"
            },
            {
                "duplicate submission rate",
                "duplicate final submissions per 1,000 attempts"
            }
        }
    };
}

void demonstrateProblemFrame() {
    printSection("4. Problem framing");

    const auto frame = createExaminationFrame();
    cout << frame.render();
}


// -----------------------------------------------------------------------------
// 6. PROBLEM BOUNDARY
// -----------------------------------------------------------------------------

class ProblemBoundary {
private:
    set<string> inside_;
    set<string> outside_;

public:
    ProblemBoundary(
        initializer_list<string> inside,
        initializer_list<string> outside
    )
        : inside_(inside), outside_(outside) {}

    string classify(const string& item) const {
        const bool inside = inside_.find(item) != inside_.end();
        const bool outside = outside_.find(item) != outside_.end();

        if (inside && outside) {
            return "CONFLICT";
        }

        if (inside) {
            return "INSIDE";
        }

        if (outside) {
            return "OUTSIDE";
        }

        return "UNDEFINED";
    }

    void print() const {
        cout << "Inside:\n";
        for (const auto& item : inside_) {
            cout << "  [IN]  " << item << "\n";
        }

        cout << "\nOutside:\n";
        for (const auto& item : outside_) {
            cout << "  [OUT] " << item << "\n";
        }
    }
};

void demonstrateBoundary() {
    printSection("5. Problem boundaries");

    ProblemBoundary boundary{
        {
            "submission API",
            "submission database",
            "queueing mechanism",
            "retry logic",
            "portal validation"
        },
        {
            "student home Wi-Fi",
            "examination policy",
            "internet service providers",
            "student device hardware"
        }
    };

    boundary.print();

    cout << "\nClassification examples:\n";

    for (const string& item : {
        "submission API",
        "student home Wi-Fi",
        "examination policy",
        "unknown payment provider"
    }) {
        cout << item << ": " << boundary.classify(item) << "\n";
    }

    cout << "\nUndefined does not mean irrelevant. It means the boundary "
         << "decision has not yet been documented.\n";
}


// -----------------------------------------------------------------------------
// 7. EVIDENCE
// -----------------------------------------------------------------------------

enum class EvidenceType {
    MeasuredFact,
    Observation,
    Hypothesis,
    Opinion
};

string evidenceTypeName(EvidenceType type) {
    switch (type) {
        case EvidenceType::MeasuredFact:
            return "measured fact";
        case EvidenceType::Observation:
            return "observation";
        case EvidenceType::Hypothesis:
            return "hypothesis";
        case EvidenceType::Opinion:
            return "opinion";
    }

    return "unknown";
}

struct EvidenceItem {
    string statement;
    EvidenceType type;
    double confidence;
    string source;

    bool valid() const {
        return !statement.empty() &&
               confidence >= 0.0 &&
               confidence <= 1.0;
    }
};

void demonstrateEvidence() {
    printSection("6. Evidence quality");

    const vector<EvidenceItem> evidence{
        {
            "Checkout abandonment was 39% in August.",
            EvidenceType::MeasuredFact,
            0.98,
            "analytics database"
        },
        {
            "Customers are confused by delivery charges.",
            EvidenceType::Observation,
            0.78,
            "20 customer interviews"
        },
        {
            "A new checkout page will solve abandonment.",
            EvidenceType::Hypothesis,
            0.35,
            "untested proposal"
        },
        {
            "The checkout should look simpler.",
            EvidenceType::Opinion,
            0.20,
            "stakeholder preference"
        }
    };

    for (const auto& item : evidence) {
        cout << "[" << evidenceTypeName(item.type) << "] "
             << item.statement << "\n";
        cout << "  confidence=" << percent(item.confidence)
             << ", source=" << item.source
             << ", valid=" << boolalpha << item.valid()
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// 8. METRICS
// -----------------------------------------------------------------------------

struct Metric {
    string name;
    double baseline;
    double target;
    string unit;
    bool higherIsBetter;

    double gap() const {
        return target - baseline;
    }

    bool reached(double actual) const {
        return higherIsBetter
            ? actual >= target
            : actual <= target;
    }
};

void demonstrateMetrics() {
    printSection("7. Measurable gaps");

    const vector<Metric> metrics{
        {"checkout completion rate", 0.61, 0.75, "%", true},
        {"p95 checkout latency", 8.4, 3.0, "seconds", false},
        {"support contacts per 1,000 orders", 92.0, 55.0, "contacts", false}
    };

    const map<string, double> actualValues{
        {"checkout completion rate", 0.77},
        {"p95 checkout latency", 3.4},
        {"support contacts per 1,000 orders", 51.0}
    };

    for (const auto& metric : metrics) {
        const double actual = actualValues.at(metric.name);

        cout << metric.name
             << ": baseline=" << metric.baseline
             << ", target=" << metric.target
             << ", gap=" << metric.gap()
             << ", actual=" << actual
             << ", status="
             << (metric.reached(actual) ? "TARGET MET" : "TARGET NOT MET")
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// 9. EXAMINATION SYSTEM DATA MODEL
// -----------------------------------------------------------------------------

struct ExaminationRecord {
    string date;
    long long attempts;
    long long successful;
    long long paymentErrors;
    long long validationErrors;
    long long timeouts;
    long long duplicates;

    double successRate() const {
        if (attempts == 0) {
            return 0.0;
        }

        return static_cast<double>(successful) /
               static_cast<double>(attempts);
    }

    long long failures() const {
        return attempts - successful;
    }
};

vector<ExaminationRecord> buildRecords() {
    return {
        {"2026-08-01", 12000, 11160, 330, 210, 240, 18},
        {"2026-08-02", 12100, 11253, 340, 195, 312, 20},
        {"2026-08-03", 11900, 11007, 420, 180, 293, 19},
        {"2026-08-04", 12500, 11375, 510, 205, 410, 24},
        {"2026-08-05", 12800, 11456, 570, 220, 554, 28},
        {"2026-08-06", 13000, 11570, 610, 230, 590, 31},
        {"2026-08-07", 13200, 11616, 640, 245, 699, 35}
    };
};

struct AggregateAnalysis {
    long long attempts = 0;
    long long successful = 0;
    long long paymentErrors = 0;
    long long validationErrors = 0;
    long long timeouts = 0;
    long long duplicates = 0;

    double successRate() const {
        return attempts == 0
            ? 0.0
            : static_cast<double>(successful) /
              static_cast<double>(attempts);
    }

    double failureRate() const {
        return 1.0 - successRate();
    }

    double rate(long long count) const {
        return attempts == 0
            ? 0.0
            : static_cast<double>(count) /
              static_cast<double>(attempts);
    }
};

AggregateAnalysis analyzeRecords(
    const vector<ExaminationRecord>& records
) {
    AggregateAnalysis result;

    // One linear pass gives O(n) time and O(1) additional aggregation state.
    for (const auto& record : records) {
        result.attempts += record.attempts;
        result.successful += record.successful;
        result.paymentErrors += record.paymentErrors;
        result.validationErrors += record.validationErrors;
        result.timeouts += record.timeouts;
        result.duplicates += record.duplicates;
    }

    return result;
}

void demonstrateCaseStudyData() {
    printSection("8. Industry-style case study");

    const auto records = buildRecords();
    const auto analysis = analyzeRecords(records);

    cout << "Total attempts: " << analysis.attempts << "\n";
    cout << "Successful: " << analysis.successful << "\n";
    cout << "Success rate: " << percent(analysis.successRate()) << "\n";
    cout << "Failure rate: " << percent(analysis.failureRate()) << "\n";
    cout << "Payment error rate: "
         << percent(analysis.rate(analysis.paymentErrors)) << "\n";
    cout << "Validation error rate: "
         << percent(analysis.rate(analysis.validationErrors)) << "\n";
    cout << "Timeout rate: "
         << percent(analysis.rate(analysis.timeouts)) << "\n";
    cout << "Duplicate rate: "
         << percent(analysis.rate(analysis.duplicates)) << "\n";

    cout << "\nDaily observations:\n";

    for (const auto& record : records) {
        cout << record.date
             << ": success=" << percent(record.successRate())
             << ", failures=" << record.failures()
             << ", payments=" << record.paymentErrors
             << ", validation=" << record.validationErrors
             << ", timeouts=" << record.timeouts
             << ", duplicates=" << record.duplicates
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// 10. INVESTIGATION HYPOTHESES
// -----------------------------------------------------------------------------

struct Hypothesis {
    string statement;
    string test;
    vector<string> supportingEvidence;
    vector<string> contradictingEvidence;

    string status() const {
        if (!contradictingEvidence.empty()) {
            return "requires revision";
        }

        if (!supportingEvidence.empty()) {
            return "supported but not proven";
        }

        return "untested";
    }
};

void demonstrateHypotheses() {
    printSection("9. Causal hypotheses");

    Hypothesis hypothesis{
        "Submission timeouts materially contribute to duplicate submissions.",
        "Compare duplicate frequency in timeout and non-timeout submission paths.",
        {
            "Duplicate events frequently follow timeout events."
        },
        {}
    };

    cout << "Statement: " << hypothesis.statement << "\n";
    cout << "Test: " << hypothesis.test << "\n";
    cout << "Status: " << hypothesis.status() << "\n";

    for (const auto& item : hypothesis.supportingEvidence) {
        cout << "  + " << item << "\n";
    }
}


// -----------------------------------------------------------------------------
// 11. PARETO ANALYSIS
// -----------------------------------------------------------------------------

struct ParetoEntry {
    string cause;
    long long count;
    double cumulativeShare;
};

vector<ParetoEntry> paretoAnalysis(
    const map<string, long long>& causes
) {
    vector<pair<string, long long>> sortedCauses(
        causes.begin(),
        causes.end()
    );

    sort(
        sortedCauses.begin(),
        sortedCauses.end(),
        [](const auto& left, const auto& right) {
            return left.second > right.second;
        }
    );

    const long long total = accumulate(
        sortedCauses.begin(),
        sortedCauses.end(),
        0LL,
        [](long long sum, const auto& item) {
            return sum + item.second;
        }
    );

    vector<ParetoEntry> result;

    if (total <= 0) {
        return result;
    }

    long long cumulative = 0;

    for (const auto& [cause, count] : sortedCauses) {
        cumulative += count;

        result.push_back({
            cause,
            count,
            static_cast<double>(cumulative) /
                static_cast<double>(total)
        });
    }

    return result;
}

void demonstratePareto() {
    printSection("10. Pareto-style cause analysis");

    const map<string, long long> causes{
        {"payment failures", 410},
        {"delivery-price confusion", 230},
        {"slow response", 170},
        {"validation errors", 110},
        {"miscellaneous", 80}
    };

    for (const auto& item : paretoAnalysis(causes)) {
        cout << left << setw(30)
             << item.cause
             << right << setw(5)
             << item.count
             << " incidents | cumulative="
             << percent(item.cumulativeShare)
             << "\n";
    }

    cout << "\nPareto analysis identifies concentration. It does not "
         << "establish causality by itself.\n";
}


// -----------------------------------------------------------------------------
// 12. STAKEHOLDERS
// -----------------------------------------------------------------------------

struct Stakeholder {
    string name;
    string role;
    string concern;
    string influence;
};

void demonstrateStakeholders() {
    printSection("11. Stakeholder perspectives");

    const vector<Stakeholder> stakeholders{
        {
            "Student",
            "primary user",
            "successful submission before deadline",
            "high"
        },
        {
            "Faculty",
            "assessment owner",
            "valid and traceable submissions",
            "high"
        },
        {
            "IT operations",
            "system operator",
            "availability and maintainability",
            "high"
        },
        {
            "Security",
            "risk owner",
            "confidentiality and integrity",
            "high"
        },
        {
            "Finance",
            "budget owner",
            "controlled infrastructure cost",
            "medium"
        }
    };

    for (const auto& stakeholder : stakeholders) {
        cout << setw(18) << left << stakeholder.name
             << " | " << setw(20) << stakeholder.role
             << " | " << setw(45) << stakeholder.concern
             << " | influence=" << stakeholder.influence
             << "\n";
    }
}


// -----------------------------------------------------------------------------
// 13. INVESTIGATION PRIORITIZATION
// -----------------------------------------------------------------------------

struct InvestigationCandidate {
    string name;
    double impact;
    double uncertainty;
    double controllability;

    double investigationValue() const {
        return impact * uncertainty * controllability;
    }
};

void demonstrateInvestigationPrioritization() {
    printSection("12. Investigation prioritization");

    vector<InvestigationCandidate> candidates{
        {
            "payment authorization failures",
            0.90,
            0.40,
            0.80
        },
        {
            "submission timeouts",
            0.85,
            0.75,
            0.90
        },
        {
            "validation errors",
            0.45,
            0.50,
            0.90
        },
        {
            "student home Wi-Fi",
            0.70,
            0.80,
            0.10
        }
    };

    for (const auto& candidate : candidates) {
        cout << setw(35) << left << candidate.name
             << " impact=" << candidate.impact
             << " uncertainty=" << candidate.uncertainty
             << " controllability=" << candidate.controllability
             << " investigation_value="
             << candidate.investigationValue()
             << "\n";
    }

    cout << "\nThis is an investigation heuristic, not a causal ranking "
         << "or universal decision rule.\n";
}


// -----------------------------------------------------------------------------
// 14. BEFORE/AFTER VALIDATION
// -----------------------------------------------------------------------------

struct ComparisonResult {
    double beforeMean;
    double afterMean;
    double absoluteChange;
    double relativeChange;
};

ComparisonResult compareBeforeAfter(
    const vector<double>& before,
    const vector<double>& after
) {
    if (before.empty() || after.empty()) {
        throw invalid_argument(
            "Before and after samples cannot be empty."
        );
    }

    const double beforeMean =
        accumulate(before.begin(), before.end(), 0.0) /
        static_cast<double>(before.size());

    const double afterMean =
        accumulate(after.begin(), after.end(), 0.0) /
        static_cast<double>(after.size());

    const double absoluteChange = afterMean - beforeMean;

    const double relativeChange =
        beforeMean == 0.0
            ? numeric_limits<double>::quiet_NaN()
            : absoluteChange / beforeMean;

    return {
        beforeMean,
        afterMean,
        absoluteChange,
        relativeChange
    };
}

void demonstrateValidation() {
    printSection("13. Validating an intervention");

    const vector<double> before{
        39, 41, 38, 42, 40, 39, 43
    };

    const vector<double> after{
        31, 29, 30, 32, 28, 31, 30
    };

    const auto result = compareBeforeAfter(before, after);

    cout << "Before mean: " << result.beforeMean << "\n";
    cout << "After mean: " << result.afterMean << "\n";
    cout << "Absolute change: " << result.absoluteChange << "\n";
    cout << "Relative change: " << percent(result.relativeChange) << "\n";

    cout << "\nA before/after change can be confounded by seasonality, "
         << "traffic mix, concurrent changes, measurement changes, "
         << "and regression to the mean.\n";
}


// -----------------------------------------------------------------------------
// 15. SYSTEM COMPONENT BOUNDARY
// -----------------------------------------------------------------------------

class SubmissionSystem {
private:
    set<string> components_;

public:
    SubmissionSystem()
        : components_{
            "portal",
            "validation",
            "submission API",
            "queue",
            "database",
            "retry manager",
            "monitoring"
        } {}

    bool contains(const string& component) const {
        return components_.find(component) != components_.end();
    }

    void describe() const {
        cout << "System components:\n";

        for (const auto& component : components_) {
            cout << "  - " << component << "\n";
        }
    }
};

void demonstrateSystemBoundary() {
    printSection("14. Technical system boundary");

    SubmissionSystem system;
    system.describe();

    cout << "\nExamples:\n";
    cout << "submission API -> "
         << boolalpha << system.contains("submission API") << "\n";
    cout << "student home router -> "
         << boolalpha << system.contains("student home router") << "\n";

    cout << "\nA system boundary should identify what the investigation "
         << "can observe, change, or control. External dependencies can "
         << "still matter without becoming internal components.\n";
}


// -----------------------------------------------------------------------------
// 16. EDGE CASES
// -----------------------------------------------------------------------------

void demonstrateEdgeCases() {
    printSection("15. Edge cases and failure modes");

    const vector<pair<string, string>> cases{
        {
            "Multiple root causes",
            "Capacity, deployment, dependency, and monitoring problems can interact."
        },
        {
            "One cause, multiple symptoms",
            "A failed identity service can produce several visible failures."
        },
        {
            "Changing baseline",
            "Traffic or population changes can alter metrics without a process change."
        },
        {
            "Rare severe event",
            "Mean performance may conceal a low-frequency safety or security failure."
        },
        {
            "External cause",
            "The root cause may be outside the project boundary."
        },
        {
            "Unknown cause",
            "A valid problem can be defined before its cause is known."
        },
        {
            "Metric conflict",
            "Improving one metric may damage another."
        }
    };

    for (const auto& [name, description] : cases) {
        cout << name << ": " << description << "\n";
    }
}


// -----------------------------------------------------------------------------
// 17. SECURITY
// -----------------------------------------------------------------------------

void demonstrateSecurity() {
    printSection("16. Security and privacy considerations");

    const vector<string> rules{
        "Collect only evidence necessary for the investigation.",
        "Do not expose student identifiers in diagnostic output.",
        "Use least privilege for sensitive evidence.",
        "Record access to protected diagnostic datasets.",
        "Redact identifiers when aggregate evidence is sufficient.",
        "Treat manipulated metrics as a possible governance or security problem.",
        "Do not define a security problem only as a technical symptom."
    };

    for (const auto& rule : rules) {
        cout << "- " << rule << "\n";
    }
}


// -----------------------------------------------------------------------------
// 18. COMMON PROBLEM-DEFINITION FAILURES
// -----------------------------------------------------------------------------

void demonstrateCommonMistakes() {
    printSection("17. Common mistakes");

    const vector<pair<string, string>> mistakes{
        {
            "Solution disguised as problem",
            "Build a new submission service."
        },
        {
            "Cause disguised as problem",
            "The database is too slow."
        },
        {
            "Vague condition",
            "The application is bad."
        },
        {
            "Unbounded responsibility",
            "Ensure no student ever has an internet problem."
        },
        {
            "Metric without user impact",
            "Increase throughput without defining why throughput matters."
        },
        {
            "Opinion presented as fact",
            "Users hate the new interface."
        }
    };

    for (const auto& [category, example] : mistakes) {
        cout << category << ": " << example << "\n";
    }
}


// -----------------------------------------------------------------------------
// 19. COMPLETE WORKFLOW
// -----------------------------------------------------------------------------

vector<string> workflow() {
    return {
        "Observe the undesirable condition",
        "Identify affected actors",
        "Establish evidence and baseline",
        "Define the desired condition",
        "State the measurable gap",
        "Document context",
        "Separate symptoms from causal hypotheses",
        "Investigate causes",
        "Define boundaries and exclusions",
        "Document constraints and assumptions",
        "Define success metrics",
        "Validate the framing"
    };
}

void demonstrateWorkflow() {
    printSection("18. End-to-end workflow");

    const auto stages = workflow();

    for (size_t i = 0; i < stages.size(); ++i) {
        cout << setw(2) << right << i + 1
             << ". " << stages[i] << "\n";
    }
}


// -----------------------------------------------------------------------------
// 20. MAIN CASE STUDY REASONING
// -----------------------------------------------------------------------------

void runCaseStudy() {
    printSection("19. Complete case-study reasoning");

    const auto frame = createExaminationFrame();

    cout << "Problem frame:\n";
    cout << frame.render();

    cout << "\n\nObserved data:\n";

    const auto records = buildRecords();
    const auto analysis = analyzeRecords(records);

    cout << "Success rate: " << percent(analysis.successRate()) << "\n";
    cout << "Failure rate: " << percent(analysis.failureRate()) << "\n";

    const map<string, long long> failureCategories{
        {"payment errors", analysis.paymentErrors},
        {"validation errors", analysis.validationErrors},
        {"timeouts", analysis.timeouts},
        {"duplicates", analysis.duplicates}
    };

    cout << "\nFailure-related event concentration:\n";

    for (const auto& item : paretoAnalysis(failureCategories)) {
        cout << "  " << item.cause
             << ": " << item.count
             << " | cumulative=" << percent(item.cumulativeShare)
             << "\n";
    }

    cout << "\nProblem-definition conclusion for the case:\n";
    cout << "The system has a measurable submission-reliability problem "
         << "during concentrated traffic. The evidence identifies several "
         << "candidate causal mechanisms, but selecting one as the root "
         << "cause requires further causal testing.\n";

    cout << "\nBoundary decision:\n";
    cout << "The project includes the portal, submission path, persistence, "
         << "retry behavior, and monitoring. Student home networks and "
         << "examination policy remain external conditions.\n";

    cout << "\nSuccess criteria:\n";
    for (const auto& [name, definition] : frame.successMetrics) {
        cout << "  - " << name << ": " << definition << "\n";
    }
}


// -----------------------------------------------------------------------------
// 21. MAIN
// -----------------------------------------------------------------------------

int main() {
    try {
        printSection("PROBLEM DEFINITION TECHNICAL CASE STUDY");

        cout << "Topic: problem statements, symptoms versus root causes, "
             << "problem framing, and problem boundaries\n";

        demonstrateProblemStatement();
        demonstrateSymptomsAndCauses();
        demonstrateFiveWhys();
        demonstrateProblemFrame();
        demonstrateBoundary();
        demonstrateEvidence();
        demonstrateMetrics();
        demonstrateCaseStudyData();
        demonstrateHypotheses();
        demonstratePareto();
        demonstrateStakeholders();
        demonstrateInvestigationPrioritization();
        demonstrateValidation();
        demonstrateSystemBoundary();
        demonstrateEdgeCases();
        demonstrateSecurity();
        demonstrateCommonMistakes();
        demonstrateWorkflow();
        runCaseStudy();

        printSection("FINAL PRACTICE PROBLEM");

        ProblemStatement practice{
            "Retail customers",
            "abandon carts before payment completion",
            "conversion is 58% while the agreed target is 70%",
            "orders and expected revenue are lost",
            {
                "Analytics show high exits on the payment step.",
                "Payment-error sessions show higher abandonment.",
                "The effect is concentrated during evening traffic peaks."
            },
            "the previous six weeks",
            "the web purchase flow"
        };

        cout << practice.render() << "\n";

        const auto errors = practice.validate();

        if (errors.empty()) {
            cout << "Validation: PASS\n";
        } else {
            cout << "Validation: FAIL\n";
            for (const auto& error : errors) {
                cout << "  - " << error << "\n";
            }
        }

        cout << "\nCore discipline: define what is happening before deciding "
             << "why it is happening, and investigate causes before selecting "
             << "a solution.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Program failed: " << error.what() << "\n";
        return 1;
    }
}
