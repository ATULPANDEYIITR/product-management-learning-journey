/*
 * Customer Understanding: Industry-Style Customer Intelligence Case Study
 *
 * Scenario:
 * ---------
 * A B2B software company wants to understand its customers across the full
 * buying and usage system. The company must distinguish users, buyers,
 * decision-makers, and influencers; segment accounts; calculate transparent
 * health indicators; analyze customer needs and journey friction; prioritize
 * evidence-backed opportunities; and produce a structured customer insight
 * report.
 *
 * Language:
 * C++17 or later
 *
 * Build:
 * g++ -std=c++17 -O2 customer_understanding.cpp -o customer_understanding
 *
 * The program uses only the C++ standard library.
 */

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


// ============================================================================
// 1. ENUMERATIONS AND BASIC TYPES
// ============================================================================

enum class Role {
    Customer,
    User,
    Buyer,
    DecisionMaker,
    Influencer
};

string roleToString(Role role) {
    switch (role) {
        case Role::Customer:
            return "customer";
        case Role::User:
            return "user";
        case Role::Buyer:
            return "buyer";
        case Role::DecisionMaker:
            return "decision-maker";
        case Role::Influencer:
            return "influencer";
    }

    return "unknown";
}


enum class JourneyStage {
    Awareness,
    Consideration,
    Evaluation,
    Purchase,
    Onboarding,
    Adoption,
    Retention,
    Expansion,
    Advocacy
};

string stageToString(JourneyStage stage) {
    switch (stage) {
        case JourneyStage::Awareness:
            return "awareness";
        case JourneyStage::Consideration:
            return "consideration";
        case JourneyStage::Evaluation:
            return "evaluation";
        case JourneyStage::Purchase:
            return "purchase";
        case JourneyStage::Onboarding:
            return "onboarding";
        case JourneyStage::Adoption:
            return "adoption";
        case JourneyStage::Retention:
            return "retention";
        case JourneyStage::Expansion:
            return "expansion";
        case JourneyStage::Advocacy:
            return "advocacy";
    }

    return "unknown";
}


// ============================================================================
// 2. DOMAIN CLASSES
// ============================================================================

struct Participant {
    string name;
    Role role;
    string department;
    vector<string> goals;
    vector<string> concerns;
    double influence;
};


struct CustomerAccount {
    string id;
    string industry;
    int companySize;
    double annualValue;
    int sessionsPerMonth;
    int supportTickets;
    double satisfaction;
    double adoptionRate;
    int decisionCycleDays;
    string primaryGoal;
};


struct JourneyTouchpoint {
    JourneyStage stage;
    string channel;
    string customerAction;
    string emotion;
    double friction;
};


struct Need {
    string name;
    double importance;
    double satisfaction;
    int affectedCustomers;
    double strategicRelevance;

    double opportunityScore() const {
        if (importance < 0.0 ||
            satisfaction < 0.0 ||
            satisfaction > 10.0 ||
            affectedCustomers < 0 ||
            strategicRelevance < 0.0) {
            throw invalid_argument("Invalid need values.");
        }

        /*
         * This is an explicit heuristic rather than a universal product
         * management formula. The square-root term prevents very large
         * populations from overwhelming the other dimensions completely.
         */
        return importance
             * (10.0 - satisfaction)
             * sqrt(max(1, affectedCustomers))
             * strategicRelevance;
    }
};


struct Evidence {
    string source;
    string statement;
    double strength;
    int sampleSize;

    double weightedStrength() const {
        if (strength < 0.0 || strength > 1.0 || sampleSize < 0) {
            throw invalid_argument("Invalid evidence.");
        }

        return strength * min(1.0, sampleSize / 50.0);
    }
};


struct Persona {
    string name;
    string segment;
    vector<string> goals;
    vector<string> painPoints;
    vector<string> behaviors;
    vector<string> channels;
    vector<string> objections;
    vector<string> buyingTriggers;
    int evidenceCount;

    bool isEvidenceBacked() const {
        return evidenceCount > 0;
    }
};


struct CustomerInsight {
    string customerId;
    string segment;
    double healthScore;
    string primaryNeed;
    double journeyFriction;
    int evidenceCount;

    string riskLevel() const {
        if (healthScore < 40.0 || journeyFriction >= 8.0) {
            return "high";
        }

        if (healthScore < 70.0 || journeyFriction >= 5.0) {
            return "medium";
        }

        return "low";
    }
};


// ============================================================================
// 3. VALIDATION
// ============================================================================

vector<string> validateCustomer(const CustomerAccount& customer) {
    vector<string> errors;

    if (customer.id.empty()) {
        errors.push_back("missing customer ID");
    }

    if (customer.companySize < 0) {
        errors.push_back("company size cannot be negative");
    }

    if (customer.annualValue < 0.0) {
        errors.push_back("annual value cannot be negative");
    }

    if (customer.sessionsPerMonth < 0) {
        errors.push_back("session count cannot be negative");
    }

    if (customer.supportTickets < 0) {
        errors.push_back("support ticket count cannot be negative");
    }

    if (customer.satisfaction < 0.0 ||
        customer.satisfaction > 10.0) {
        errors.push_back("satisfaction must be between 0 and 10");
    }

    if (customer.adoptionRate < 0.0 ||
        customer.adoptionRate > 1.0) {
        errors.push_back("adoption rate must be between 0 and 1");
    }

    if (customer.decisionCycleDays < 0) {
        errors.push_back("decision cycle cannot be negative");
    }

    return errors;
}


// ============================================================================
// 4. CUSTOMER SEGMENTATION
// ============================================================================

string sizeSegment(const CustomerAccount& customer) {
    if (customer.companySize < 100) {
        return "small";
    }

    if (customer.companySize < 1000) {
        return "mid-market";
    }

    return "enterprise";
}


string adoptionSegment(const CustomerAccount& customer) {
    if (customer.adoptionRate < 0.50) {
        return "low adoption";
    }

    if (customer.adoptionRate < 0.80) {
        return "moderate adoption";
    }

    return "high adoption";
}


// ============================================================================
// 5. CUSTOMER HEALTH MODEL
// ============================================================================

double customerHealthScore(const CustomerAccount& customer) {
    if (customer.satisfaction < 0.0 ||
        customer.satisfaction > 10.0 ||
        customer.adoptionRate < 0.0 ||
        customer.adoptionRate > 1.0) {
        throw invalid_argument("Invalid customer health inputs.");
    }

    /*
     * The model is intentionally transparent:
     *
     * Satisfaction -> stated experience
     * Adoption     -> depth of product use
     * Engagement   -> activity
     * Support      -> friction proxy
     *
     * These weights are illustrative and must be validated against actual
     * retention or expansion outcomes before being used operationally.
     */
    const double satisfaction = customer.satisfaction / 10.0;
    const double adoption = customer.adoptionRate;
    const double engagement =
        min(customer.sessionsPerMonth / 60.0, 1.0);
    const double supportQuality =
        1.0 - min(customer.supportTickets / 20.0, 1.0);

    return 100.0 * (
        0.30 * satisfaction +
        0.35 * adoption +
        0.20 * engagement +
        0.15 * supportQuality
    );
}


// ============================================================================
// 6. BUYING-UNIT ANALYSIS
// ============================================================================

class BuyingUnit {
private:
    string organization;
    vector<Participant> participants;

public:
    BuyingUnit(
        string organizationName,
        vector<Participant> members
    )
        : organization(std::move(organizationName)),
          participants(std::move(members)) {}

    const string& getOrganization() const {
        return organization;
    }

    const vector<Participant>& getParticipants() const {
        return participants;
    }

    map<string, int> roleCounts() const {
        map<string, int> counts;

        for (const auto& participant : participants) {
            counts[roleToString(participant.role)]++;
        }

        return counts;
    }

    optional<Participant> mostInfluential() const {
        if (participants.empty()) {
            return nullopt;
        }

        return *max_element(
            participants.begin(),
            participants.end(),
            [](const Participant& a, const Participant& b) {
                return a.influence < b.influence;
            }
        );
    }
};


// ============================================================================
// 7. CUSTOMER JOURNEY ANALYSIS
// ============================================================================

class JourneyAnalyzer {
private:
    vector<JourneyTouchpoint> touchpoints;

public:
    explicit JourneyAnalyzer(vector<JourneyTouchpoint> points)
        : touchpoints(std::move(points)) {}

    map<string, double> averageFrictionByStage() const {
        map<string, vector<double>> grouped;

        for (const auto& point : touchpoints) {
            if (point.friction < 0.0 || point.friction > 10.0) {
                throw invalid_argument("Journey friction must be 0-10.");
            }

            grouped[stageToString(point.stage)].push_back(point.friction);
        }

        map<string, double> result;

        for (const auto& [stage, values] : grouped) {
            const double total =
                accumulate(values.begin(), values.end(), 0.0);

            result[stage] = total / values.size();
        }

        return result;
    }

    optional<JourneyTouchpoint> highestFrictionPoint() const {
        if (touchpoints.empty()) {
            return nullopt;
        }

        return *max_element(
            touchpoints.begin(),
            touchpoints.end(),
            [](const JourneyTouchpoint& a,
               const JourneyTouchpoint& b) {
                return a.friction < b.friction;
            }
        );
    }
};


// ============================================================================
// 8. RFM MODEL
// ============================================================================

struct RFMRecord {
    string customerId;
    int recencyDays;
    int frequency;
    double monetaryValue;
};


int percentileScore(
    const vector<double>& values,
    double value
) {
    if (values.empty()) {
        throw invalid_argument("Cannot score an empty population.");
    }

    const int count = static_cast<int>(
        count_if(
            values.begin(),
            values.end(),
            [value](double candidate) {
                return candidate <= value;
            }
        )
    );

    return max(
        1,
        min(
            5,
            static_cast<int>(
                floor(
                    static_cast<double>(count) /
                    values.size() *
                    5.0
                )
            )
        )
    );
}


struct RFMScore {
    int recency;
    int frequency;
    int monetary;
};


RFMScore calculateRFM(
    const RFMRecord& record,
    const vector<RFMRecord>& population
) {
    vector<double> recencyValues;
    vector<double> frequencyValues;
    vector<double> monetaryValues;

    for (const auto& item : population) {
        recencyValues.push_back(
            -static_cast<double>(item.recencyDays)
        );
        frequencyValues.push_back(
            static_cast<double>(item.frequency)
        );
        monetaryValues.push_back(item.monetaryValue);
    }

    return {
        percentileScore(
            recencyValues,
            -static_cast<double>(record.recencyDays)
        ),
        percentileScore(
            frequencyValues,
            static_cast<double>(record.frequency)
        ),
        percentileScore(
            monetaryValues,
            record.monetaryValue
        )
    };
}


// ============================================================================
// 9. SEGMENT AGGREGATION
// ============================================================================

struct SegmentStatistics {
    int count = 0;
    double averageValue = 0.0;
    double averageSatisfaction = 0.0;
    double averageAdoption = 0.0;
};


map<string, SegmentStatistics> aggregateSegments(
    const vector<CustomerAccount>& customers
) {
    struct Accumulator {
        int count = 0;
        double valueTotal = 0.0;
        double satisfactionTotal = 0.0;
        double adoptionTotal = 0.0;
    };

    map<string, Accumulator> accumulators;

    for (const auto& customer : customers) {
        const string segment = sizeSegment(customer);
        auto& accumulator = accumulators[segment];

        accumulator.count++;
        accumulator.valueTotal += customer.annualValue;
        accumulator.satisfactionTotal += customer.satisfaction;
        accumulator.adoptionTotal += customer.adoptionRate;
    }

    map<string, SegmentStatistics> result;

    for (const auto& [segment, accumulator] : accumulators) {
        SegmentStatistics statistics;

        statistics.count = accumulator.count;
        statistics.averageValue =
            accumulator.valueTotal / accumulator.count;
        statistics.averageSatisfaction =
            accumulator.satisfactionTotal / accumulator.count;
        statistics.averageAdoption =
            accumulator.adoptionTotal / accumulator.count;

        result[segment] = statistics;
    }

    return result;
}


// ============================================================================
// 10. NEED PRIORITIZATION
// ============================================================================

vector<Need> rankNeeds(vector<Need> needs) {
    sort(
        needs.begin(),
        needs.end(),
        [](const Need& a, const Need& b) {
            return a.opportunityScore() >
                   b.opportunityScore();
        }
    );

    return needs;
}


// ============================================================================
// 11. EVIDENCE QUALITY
// ============================================================================

double evidenceConfidence(
    const vector<Evidence>& evidenceItems
) {
    if (evidenceItems.empty()) {
        return 0.0;
    }

    double total = 0.0;

    for (const auto& evidence : evidenceItems) {
        total += evidence.weightedStrength();
    }

    return min(
        1.0,
        total / static_cast<double>(evidenceItems.size())
    );
}


// ============================================================================
// 12. CUSTOMER INSIGHT PIPELINE
// ============================================================================

class CustomerIntelligenceSystem {
private:
    vector<CustomerAccount> customers;
    vector<Need> needs;
    vector<Evidence> evidence;
    JourneyAnalyzer journeyAnalyzer;

public:
    CustomerIntelligenceSystem(
        vector<CustomerAccount> accounts,
        vector<Need> customerNeeds,
        vector<Evidence> researchEvidence,
        JourneyAnalyzer analyzer
    )
        : customers(std::move(accounts)),
          needs(std::move(customerNeeds)),
          evidence(std::move(researchEvidence)),
          journeyAnalyzer(std::move(analyzer)) {}

    vector<CustomerInsight> generateInsights() const {
        vector<CustomerInsight> insights;

        const auto frictionData =
            journeyAnalyzer.averageFrictionByStage();

        double averageFriction = 0.0;

        if (!frictionData.empty()) {
            double total = 0.0;

            for (const auto& [stage, friction] : frictionData) {
                total += friction;
            }

            averageFriction =
                total / static_cast<double>(frictionData.size());
        }

        const string primaryNeed =
            needs.empty() ? "unknown" : rankNeeds(needs).front().name;

        for (const auto& customer : customers) {
            CustomerInsight insight;

            insight.customerId = customer.id;
            insight.segment =
                sizeSegment(customer) + " / " +
                adoptionSegment(customer);
            insight.healthScore =
                customerHealthScore(customer);
            insight.primaryNeed = primaryNeed;
            insight.journeyFriction = averageFriction;
            insight.evidenceCount =
                static_cast<int>(evidence.size());

            insights.push_back(insight);
        }

        return insights;
    }

    double researchConfidence() const {
        return evidenceConfidence(evidence);
    }
};


// ============================================================================
// 13. CONSOLE REPORTING
// ============================================================================

void printCustomerReport(
    const vector<CustomerInsight>& insights
) {
    cout << "\n"
         << string(78, '=')
         << "\nCustomer insight report\n"
         << string(78, '=')
         << "\n";

    cout << left
         << setw(10) << "ID"
         << setw(28) << "Segment"
         << setw(12) << "Health"
         << setw(10) << "Risk"
         << "Primary need\n";

    cout << string(78, '-')
         << "\n";

    for (const auto& insight : insights) {
        cout << left
             << setw(10) << insight.customerId
             << setw(28) << insight.segment
             << setw(12) << fixed
             << setprecision(1)
             << insight.healthScore
             << setw(10) << insight.riskLevel()
             << insight.primaryNeed
             << "\n";
    }
}


// ============================================================================
// 14. UNIT TEST HELPERS
// ============================================================================

void require(
    bool condition,
    const string& message
) {
    if (!condition) {
        throw runtime_error("Test failed: " + message);
    }
}


void runTests() {
    CustomerAccount validCustomer{
        "C001",
        "manufacturing",
        450,
        120000.0,
        38,
        2,
        8.4,
        0.87,
        45,
        "efficiency"
    };

    require(
        validateCustomer(validCustomer).empty(),
        "valid customer should pass validation"
    );

    require(
        sizeSegment(validCustomer) == "mid-market",
        "company size segmentation"
    );

    require(
        adoptionSegment(validCustomer) == "high adoption",
        "adoption segmentation"
    );

    const double health =
        customerHealthScore(validCustomer);

    require(
        health > 0.0 && health <= 100.0,
        "health must be within 0-100"
    );

    Need need{
        "Simplify onboarding",
        9.0,
        4.0,
        820,
        1.0
    };

    require(
        need.opportunityScore() > 0.0,
        "opportunity score should be positive"
    );

    vector<double> vectorA{1.0, 0.0};
    vector<double> vectorB{0.0, 1.0};

    const double distance =
        sqrt(
            pow(vectorA[0] - vectorB[0], 2) +
            pow(vectorA[1] - vectorB[1], 2)
        );

    require(
        abs(distance - sqrt(2.0)) < 1e-9,
        "Euclidean distance calculation"
    );

    bool invalidRejected = false;

    try {
        CustomerAccount invalidCustomer{
            "BAD",
            "retail",
            50,
            -100.0,
            10,
            1,
            6.0,
            0.5,
            20,
            "cost"
        };

        invalidRejected =
            !validateCustomer(invalidCustomer).empty();
    } catch (...) {
        invalidRejected = true;
    }

    require(
        invalidRejected,
        "invalid customer should be rejected"
    );
}


// ============================================================================
// 15. MAIN INDUSTRY CASE STUDY
// ============================================================================

int main() {
    try {
        cout << string(78, '=')
             << "\nCustomer Understanding Industry Case Study\n"
             << string(78, '=')
             << "\n";

        // --------------------------------------------------------------------
        // Step 1: Create a realistic B2B buying unit.
        // --------------------------------------------------------------------

        BuyingUnit buyingUnit(
            "Northstar Manufacturing",
            {
                {
                    "Asha",
                    Role::User,
                    "Operations",
                    {"fast reporting", "simple workflows"},
                    {"training time"},
                    0.55
                },
                {
                    "Rahul",
                    Role::Buyer,
                    "Procurement",
                    {"commercial clarity"},
                    {"contract complexity"},
                    0.65
                },
                {
                    "Meera",
                    Role::DecisionMaker,
                    "Finance",
                    {"ROI", "cost control"},
                    {"uncertain payback"},
                    0.95
                },
                {
                    "Vikram",
                    Role::Influencer,
                    "IT",
                    {"security", "integration"},
                    {"data exposure"},
                    0.80
                }
            }
        );

        cout << "\nBuying organization: "
             << buyingUnit.getOrganization()
             << "\n";

        for (const auto& participant :
             buyingUnit.getParticipants()) {
            cout << "  "
                 << participant.name
                 << " | "
                 << roleToString(participant.role)
                 << " | "
                 << participant.department
                 << " | influence="
                 << participant.influence
                 << "\n";
        }

        const auto influential =
            buyingUnit.mostInfluential();

        if (influential.has_value()) {
            cout << "Most influential participant by "
                    "explicit model score: "
                 << influential->name
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Step 2: Create customer accounts.
        // --------------------------------------------------------------------

        vector<CustomerAccount> customers{
            {
                "C001",
                "manufacturing",
                450,
                120000.0,
                38,
                2,
                8.4,
                0.87,
                45,
                "efficiency"
            },
            {
                "C002",
                "retail",
                70,
                18000.0,
                14,
                8,
                6.1,
                0.48,
                18,
                "cost"
            },
            {
                "C003",
                "finance",
                1200,
                310000.0,
                61,
                1,
                9.0,
                0.92,
                90,
                "risk"
            },
            {
                "C004",
                "education",
                250,
                42000.0,
                27,
                5,
                7.2,
                0.69,
                30,
                "access"
            },
            {
                "C005",
                "manufacturing",
                900,
                220000.0,
                51,
                3,
                8.7,
                0.89,
                70,
                "efficiency"
            }
        };

        cout << "\nValidation results:\n";

        for (const auto& customer : customers) {
            const auto errors =
                validateCustomer(customer);

            cout << "  "
                 << customer.id
                 << ": "
                 << (errors.empty() ? "valid" : "invalid")
                 << "\n";

            for (const auto& error : errors) {
                cout << "    - "
                     << error
                     << "\n";
            }
        }

        // --------------------------------------------------------------------
        // Step 3: Build customer journey evidence.
        // --------------------------------------------------------------------

        vector<JourneyTouchpoint> touchpoints{
            {
                JourneyStage::Awareness,
                "search",
                "reads comparison article",
                "curious",
                2.0
            },
            {
                JourneyStage::Consideration,
                "website",
                "reviews documentation",
                "interested",
                4.0
            },
            {
                JourneyStage::Evaluation,
                "demo",
                "tests workflow",
                "uncertain",
                7.0
            },
            {
                JourneyStage::Purchase,
                "sales",
                "reviews contract",
                "cautious",
                8.0
            },
            {
                JourneyStage::Onboarding,
                "application",
                "imports data",
                "frustrated",
                9.0
            }
        };

        JourneyAnalyzer journeyAnalyzer(
            touchpoints
        );

        cout << "\nJourney friction by stage:\n";

        for (const auto& [stage, friction] :
             journeyAnalyzer.averageFrictionByStage()) {
            cout << "  "
                 << setw(15)
                 << left
                 << stage
                 << " "
                 << fixed
                 << setprecision(2)
                 << friction
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Step 4: Identify customer needs.
        // --------------------------------------------------------------------

        vector<Need> needs{
            {
                "Simplify onboarding",
                9.0,
                4.0,
                820,
                1.0
            },
            {
                "Improve exports",
                7.0,
                6.0,
                540,
                0.8
            },
            {
                "Improve advanced reporting",
                8.0,
                5.0,
                210,
                0.9
            }
        };

        cout << "\nPrioritized needs:\n";

        for (const auto& need : rankNeeds(needs)) {
            cout << "  "
                 << setw(32)
                 << left
                 << need.name
                 << " score="
                 << fixed
                 << setprecision(2)
                 << need.opportunityScore()
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Step 5: Add research evidence.
        // --------------------------------------------------------------------

        vector<Evidence> evidence{
            {
                "interview",
                "Users struggle with initial configuration.",
                0.90,
                18
            },
            {
                "analytics",
                "Many accounts abandon setup before completion.",
                0.95,
                1200
            },
            {
                "support",
                "Configuration generates repeated questions.",
                0.80,
                74
            }
        };

        // --------------------------------------------------------------------
        // Step 6: Build a persona.
        // --------------------------------------------------------------------

        Persona operationsPersona{
            "Operations Analyst",
            "mid-market operations",
            {"reduce manual work", "produce reliable reports"},
            {"spreadsheet duplication", "slow reporting"},
            {"checks reports daily", "exports data weekly"},
            {"email", "web application"},
            {"migration effort", "training"},
            {"reporting errors", "compliance changes"},
            27
        };

        cout << "\nPersona:\n";
        cout << "  Name: "
             << operationsPersona.name
             << "\n";
        cout << "  Segment: "
             << operationsPersona.segment
             << "\n";
        cout << "  Evidence-backed: "
             << boolalpha
             << operationsPersona.isEvidenceBacked()
             << "\n";

        // --------------------------------------------------------------------
        // Step 7: Create the intelligence system.
        // --------------------------------------------------------------------

        CustomerIntelligenceSystem intelligenceSystem(
            customers,
            needs,
            evidence,
            journeyAnalyzer
        );

        const auto insights =
            intelligenceSystem.generateInsights();

        printCustomerReport(insights);

        cout << "\nResearch confidence indicator: "
             << fixed
             << setprecision(3)
             << intelligenceSystem.researchConfidence()
             << "\n";

        // --------------------------------------------------------------------
        // Step 8: Aggregate segments.
        // --------------------------------------------------------------------

        cout << "\nSegment statistics:\n";

        const auto statistics =
            aggregateSegments(customers);

        for (const auto& [segment, stats] :
             statistics) {
            cout << "  "
                 << segment
                 << " | customers="
                 << stats.count
                 << " | avg value="
                 << fixed
                 << setprecision(2)
                 << stats.averageValue
                 << " | avg satisfaction="
                 << stats.averageSatisfaction
                 << " | avg adoption="
                 << stats.averageAdoption
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Step 9: RFM analysis.
        // --------------------------------------------------------------------

        vector<RFMRecord> rfmRecords{
            {"C001", 7, 24, 120000.0},
            {"C002", 64, 5, 18000.0},
            {"C003", 3, 38, 310000.0},
            {"C004", 21, 13, 42000.0},
            {"C005", 10, 29, 220000.0}
        };

        cout << "\nRFM scores:\n";

        for (const auto& record : rfmRecords) {
            const auto score =
                calculateRFM(
                    record,
                    rfmRecords
                );

            cout << "  "
                 << record.customerId
                 << " | R="
                 << score.recency
                 << " F="
                 << score.frequency
                 << " M="
                 << score.monetary
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Step 10: Demonstrate a critical edge case.
        // --------------------------------------------------------------------

        cout << "\nEdge-case handling:\n";

        try {
            Need invalidNeed{
                "Invalid example",
                9.0,
                12.0,
                10,
                1.0
            };

            cout << invalidNeed.opportunityScore()
                 << "\n";
        } catch (const exception& error) {
            cout << "  Rejected invalid need: "
                 << error.what()
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Step 11: Run internal tests.
        // --------------------------------------------------------------------

        runTests();

        cout << "\n"
             << string(78, '=')
             << "\nAll C++ validation tests passed.\n"
             << string(78, '=')
             << "\n";

        return 0;
    }
    catch (const exception& error) {
        /*
         * The top-level handler prevents an unhandled exception from
         * terminating the process without context. Production systems should
         * use structured logging and should avoid exposing sensitive internal
         * information to external users.
         */
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }
}
