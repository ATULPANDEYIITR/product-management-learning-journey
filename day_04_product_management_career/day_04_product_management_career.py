"""
PRODUCT MANAGEMENT CAREER
A detailed learning script covering Product Management as a career,
from foundational concepts to advanced product strategy, execution,
analytics, leadership, and career development.

This script is designed as an educational program. Run it in a terminal
or Python environment and read through each section carefully.

The objective is not to simulate a Product Manager's job through code,
but to use Python as a structured medium for understanding how product
management concepts, decisions, frameworks, metrics, and career
progression connect with one another.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ============================================================================
# SECTION 1: UNDERSTANDING PRODUCT MANAGEMENT
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT CAREER")
print("=" * 80)

print("""
Product Management is a professional discipline focused on identifying
valuable problems, understanding users, defining solutions, aligning
stakeholders, guiding product development, measuring outcomes, and
continuously improving a product.

A Product Manager is not simply a person who tells engineers what to build.

The role sits at the intersection of several areas:

1. CUSTOMER
   Understanding user needs, frustrations, motivations, and behaviour.

2. BUSINESS
   Understanding revenue, costs, competition, market opportunities,
   organisational objectives, and long-term strategy.

3. TECHNOLOGY
   Understanding what is technically possible, what constraints exist,
   how systems work at a practical level, and how development decisions
   affect the product.

4. DESIGN
   Understanding usability, accessibility, interaction patterns, and the
   experience users have while interacting with a product.

A Product Manager continuously attempts to answer four fundamental questions:

    What problem should we solve?
    Who are we solving it for?
    Why is solving this problem valuable?
    How will we know whether the solution worked?
""")


# ============================================================================
# SECTION 2: PRODUCT, PROJECT, AND PROGRAM MANAGEMENT
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT VS PROJECT MANAGEMENT VS PROGRAM MANAGEMENT")
print("=" * 80)

comparison = {
    "Product Management": {
        "primary_focus": "Value creation and product outcomes",
        "main_question": "What should we build and why?",
        "success_measure": "Customer and business outcomes",
        "time_horizon": "Continuous and long-term",
        "ownership": "Product direction and prioritisation"
    },
    "Project Management": {
        "primary_focus": "Execution of a defined initiative",
        "main_question": "How will we deliver this work?",
        "success_measure": "Scope, time, budget, and delivery",
        "time_horizon": "Defined beginning and end",
        "ownership": "Planning, coordination, and execution"
    },
    "Program Management": {
        "primary_focus": "Coordination across multiple related initiatives",
        "main_question": "How do multiple initiatives achieve a larger goal?",
        "success_measure": "Strategic alignment and combined outcomes",
        "time_horizon": "Medium to long-term",
        "ownership": "Cross-project coordination"
    }
}

for discipline, details in comparison.items():
    print(f"\n{discipline}")
    for key, value in details.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


# ============================================================================
# SECTION 3: WHAT A PRODUCT MANAGER ACTUALLY DOES
# ============================================================================

print("\n" + "=" * 80)
print("CORE RESPONSIBILITIES OF A PRODUCT MANAGER")
print("=" * 80)

responsibilities = [
    "Understand customers and users",
    "Identify meaningful problems",
    "Conduct market and competitive research",
    "Define product strategy",
    "Set product goals",
    "Write product requirements",
    "Create and maintain a product roadmap",
    "Prioritise product opportunities",
    "Work with engineering teams",
    "Work with designers",
    "Coordinate with business stakeholders",
    "Support product launches",
    "Analyse product data",
    "Measure product outcomes",
    "Identify product improvements",
    "Manage trade-offs and constraints"
]

for number, responsibility in enumerate(responsibilities, start=1):
    print(f"{number}. {responsibility}")


# ============================================================================
# SECTION 4: PRODUCT THINKING
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT THINKING")
print("=" * 80)

print("""
Product thinking is the ability to approach a situation through the lens
of users, problems, value, constraints, and measurable outcomes.

A weak approach often begins with a solution:

    "We should build a mobile application."

A stronger product approach begins with a problem:

    "Users are abandoning the process because completing it on a desktop
     device takes too long."

The difference is important.

Solutions can change.
The underlying problem may remain.

A Product Manager should avoid becoming emotionally attached to the first
solution that appears reasonable.

A useful structure is:

    USER -> PROBLEM -> CAUSE -> OPPORTUNITY -> SOLUTION -> OUTCOME

For example:

    USER:
        Small business owners.

    PROBLEM:
        They spend too much time manually tracking inventory.

    CAUSE:
        Inventory information is stored in spreadsheets and updated
        inconsistently.

    OPPORTUNITY:
        A simple inventory tracking system could reduce manual effort.

    SOLUTION:
        Inventory dashboard with automatic stock updates.

    OUTCOME:
        Reduction in time spent managing inventory and fewer stock errors.
""")


# ============================================================================
# SECTION 5: USER PROBLEMS AND CUSTOMER DISCOVERY
# ============================================================================

print("\n" + "=" * 80)
print("CUSTOMER DISCOVERY")
print("=" * 80)

print("""
Customer discovery is the process of learning about users before assuming
that a proposed solution is valuable.

A common mistake is asking users:

    "Would you use this feature?"

Users often say yes to hypothetical questions.

More useful questions focus on actual behaviour:

    "Tell me about the last time you faced this problem."

    "How do you currently solve it?"

    "How often does this happen?"

    "What is frustrating about the current process?"

    "What happens if you do nothing?"

    "Have you spent money trying to solve this problem?"

Past behaviour is generally more useful than hypothetical enthusiasm.
""")

interview_framework = {
    "Context": "Understand the user's environment and situation.",
    "Behaviour": "Understand what the user currently does.",
    "Pain": "Identify frustration, inefficiency, risk, or unmet needs.",
    "Impact": "Understand the consequences of the problem.",
    "Current Solution": "Understand alternatives and workarounds.",
    "Motivation": "Understand why solving the problem matters."
}

for stage, purpose in interview_framework.items():
    print(f"\n{stage}: {purpose}")


# ============================================================================
# SECTION 6: USER PERSONAS AND SEGMENTATION
# ============================================================================

print("\n" + "=" * 80)
print("USER SEGMENTATION")
print("=" * 80)

@dataclass
class UserSegment:
    name: str
    characteristics: List[str]
    needs: List[str]
    problems: List[str]
    behaviour: List[str]


example_segment = UserSegment(
    name="Early Career Professional",
    characteristics=[
        "Limited professional experience",
        "Actively seeking career growth",
        "Uses digital learning platforms"
    ],
    needs=[
        "Practical skills",
        "Clear career guidance",
        "Evidence of professional capability"
    ],
    problems=[
        "Difficulty identifying relevant skills",
        "Information overload",
        "Limited practical experience"
    ],
    behaviour=[
        "Consumes online educational content",
        "Searches for job opportunities",
        "Uses professional networking platforms"
    ]
)

print(f"\nUser Segment: {example_segment.name}")

for attribute, values in {
    "Characteristics": example_segment.characteristics,
    "Needs": example_segment.needs,
    "Problems": example_segment.problems,
    "Behaviour": example_segment.behaviour
}.items():
    print(f"\n{attribute}:")
    for value in values:
        print(f"  - {value}")


# ============================================================================
# SECTION 7: JOBS TO BE DONE
# ============================================================================

print("\n" + "=" * 80)
print("JOBS TO BE DONE")
print("=" * 80)

print("""
Jobs To Be Done is a framework used to understand what users are trying
to accomplish.

Users do not necessarily want a product feature.

They want progress.

For example, a person may not want:

    "An online course recommendation system."

The underlying job may be:

    "Help me identify what I should learn to become qualified for a
     particular professional role."

A common Jobs To Be Done structure is:

    When [situation],
    I want to [motivation or action],
    so I can [desired outcome].

Example:

    When I am preparing for a Product Manager interview,
    I want to identify the most important skills to practice,
    so I can use my preparation time efficiently.

This framework helps Product Managers focus on outcomes rather than
features.
""")


# ============================================================================
# SECTION 8: MARKET RESEARCH
# ============================================================================

print("\n" + "=" * 80)
print("MARKET RESEARCH")
print("=" * 80)

market_research_areas = {
    "Market Size": "How large is the potential opportunity?",
    "Market Growth": "Is demand increasing, stable, or declining?",
    "Customer Segments": "Which groups have different needs?",
    "Competitors": "Who currently serves the market?",
    "Alternatives": "What do users do without the product?",
    "Trends": "What technological, social, or economic changes matter?",
    "Pricing": "What are users willing to pay?",
    "Barriers": "What prevents adoption?"
}

for area, question in market_research_areas.items():
    print(f"{area}: {question}")


# ============================================================================
# SECTION 9: COMPETITOR ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("COMPETITOR ANALYSIS")
print("=" * 80)

@dataclass
class Competitor:
    name: str
    strengths: List[str]
    weaknesses: List[str]
    target_users: str
    differentiation: str


competitors = [
    Competitor(
        name="Competitor A",
        strengths=["Strong brand recognition", "Large customer base"],
        weaknesses=["Complex user experience", "High pricing"],
        target_users="Large organisations",
        differentiation="Comprehensive enterprise platform"
    ),
    Competitor(
        name="Competitor B",
        strengths=["Simple interface", "Affordable pricing"],
        weaknesses=["Limited advanced functionality"],
        target_users="Small businesses",
        differentiation="Ease of use"
    )
]

for competitor in competitors:
    print(f"\nCompetitor: {competitor.name}")
    print(f"Target Users: {competitor.target_users}")
    print(f"Differentiation: {competitor.differentiation}")
    print(f"Strengths: {', '.join(competitor.strengths)}")
    print(f"Weaknesses: {', '.join(competitor.weaknesses)}")

print("""
Competitor analysis should not become feature copying.

A competitor having a feature does not automatically mean your product
needs the same feature.

The important question is:

    Does this feature solve a meaningful problem for our target users
    and support our product strategy?
""")


# ============================================================================
# SECTION 10: PRODUCT STRATEGY
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT STRATEGY")
print("=" * 80)

print("""
Product strategy defines how a product intends to create value and achieve
its objectives.

A product strategy normally addresses:

    1. Where will we compete?
    2. Which users will we serve?
    3. Which problems will we prioritise?
    4. How will we differentiate?
    5. What outcomes are we trying to achieve?
    6. What capabilities must we develop?

Strategy is different from a feature list.

A feature list might say:

    - Build notifications
    - Build search
    - Build analytics

A strategy explains why particular investments are important and how they
contribute to a larger objective.
""")


# ============================================================================
# SECTION 11: PRODUCT VISION
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT VISION")
print("=" * 80)

print("""
A product vision describes the long-term change a product intends to create.

A useful product vision should be:

    Clear
    Ambitious
    User-centred
    Directional
    Long-term

A vision is not a detailed development plan.

For example:

    "Make professional financial management accessible to small businesses."

This provides direction without dictating every feature.

The roadmap and product decisions should move the product toward the
broader vision.
""")


# ============================================================================
# SECTION 12: PRODUCT ROADMAP
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT ROADMAP")
print("=" * 80)

@dataclass
class RoadmapItem:
    theme: str
    objective: str
    initiatives: List[str]
    success_metric: str


roadmap = [
    RoadmapItem(
        theme="User Activation",
        objective="Increase the percentage of new users reaching initial value",
        initiatives=[
            "Simplify onboarding",
            "Improve account setup",
            "Reduce unnecessary steps"
        ],
        success_metric="Activation rate"
    ),
    RoadmapItem(
        theme="Retention",
        objective="Increase continued product usage",
        initiatives=[
            "Improve recurring value",
            "Address major usability problems",
            "Improve relevant notifications"
        ],
        success_metric="Monthly retention rate"
    )
]

for item in roadmap:
    print(f"\nTheme: {item.theme}")
    print(f"Objective: {item.objective}")
    print("Initiatives:")
    for initiative in item.initiatives:
        print(f"  - {initiative}")
    print(f"Success Metric: {item.success_metric}")


# ============================================================================
# SECTION 13: PRODUCT REQUIREMENTS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT REQUIREMENTS DOCUMENT")
print("=" * 80)

print("""
A Product Requirements Document, often called a PRD, communicates what a
product initiative intends to accomplish and provides sufficient clarity
for stakeholders and development teams.

A strong PRD usually contains:

    1. Background
    2. Problem statement
    3. Product objective
    4. Target users
    5. User scenarios
    6. Requirements
    7. Constraints
    8. Success metrics
    9. Assumptions
    10. Risks
    11. Open questions

Requirements should explain the expected outcome and behaviour.

Poor requirement:

    "Build a better dashboard."

Improved requirement:

    "Users should be able to view their current account performance,
     historical performance, and recent activity from a single dashboard."

The Product Manager does not need to prescribe unnecessary technical
implementation details unless those details are essential to the product
requirement.
""")


# ============================================================================
# SECTION 14: USER STORIES
# ============================================================================

print("\n" + "=" * 80)
print("USER STORIES")
print("=" * 80)

print("""
A common user story structure is:

    As a [type of user],
    I want [action or capability],
    so that [benefit or outcome].

Example:

    As a registered customer,
    I want to view my previous orders,
    so that I can quickly track my purchase history.

A user story is often accompanied by acceptance criteria.

Acceptance criteria define conditions that must be satisfied for the
requirement to be considered complete.

Example:

    Given that the user is logged in,
    when the user opens the order history,
    then the system should display previous completed orders.
""")


# ============================================================================
# SECTION 15: PRODUCT BACKLOG
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT BACKLOG")
print("=" * 80)

@dataclass
class BacklogItem:
    title: str
    user_value: int
    business_value: int
    effort: int
    risk: int
    priority_score: float = field(init=False)

    def __post_init__(self):
        self.priority_score = (
            self.user_value +
            self.business_value +
            self.risk
        ) / max(self.effort, 1)


backlog = [
    BacklogItem("Improve onboarding", 9, 8, 5, 6),
    BacklogItem("Add profile customisation", 5, 4, 8, 2),
    BacklogItem("Fix payment failure issue", 10, 9, 3, 9),
    BacklogItem("Add advanced reporting", 7, 8, 9, 5)
]

sorted_backlog = sorted(
    backlog,
    key=lambda item: item.priority_score,
    reverse=True
)

print("\nPRIORITISED BACKLOG")

for item in sorted_backlog:
    print(
        f"{item.title} | "
        f"Priority Score: {item.priority_score:.2f}"
    )

print("""
This is only one illustrative prioritisation method.

Real prioritisation requires judgement.

Numerical frameworks can improve consistency, but they cannot replace
understanding of strategy, customer needs, technical constraints, timing,
risk, and organisational context.
""")


# ============================================================================
# SECTION 16: PRIORITISATION FRAMEWORKS
# ============================================================================

print("\n" + "=" * 80)
print("PRIORITISATION FRAMEWORKS")
print("=" * 80)

print("""
COMMON FRAMEWORKS

1. RICE

R = Reach
I = Impact
C = Confidence
E = Effort

Formula:

    RICE Score = (Reach × Impact × Confidence) / Effort

2. ICE

Impact
Confidence
Ease

Formula:

    ICE Score = Impact × Confidence × Ease

3. VALUE VS EFFORT

High Value + Low Effort:
    Usually attractive.

High Value + High Effort:
    Requires strategic consideration.

Low Value + Low Effort:
    May be useful if resources are available.

Low Value + High Effort:
    Usually lower priority.

4. COST OF DELAY

Measures the cost of postponing an initiative.

5. MOScOW

Must Have
Should Have
Could Have
Won't Have for now

The main peculiarity of prioritisation is that priority is not permanent.

A feature can be high priority today and low priority next month because:

    - Customer behaviour changed.
    - A competitor changed the market.
    - A technical dependency appeared.
    - Business objectives changed.
    - New information was discovered.
""")


# ============================================================================
# SECTION 17: WORKING WITH ENGINEERING
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT AND ENGINEERING")
print("=" * 80)

print("""
A Product Manager and an Engineering team have different but complementary
responsibilities.

The Product Manager should generally provide clarity about:

    - The problem
    - The user
    - The desired outcome
    - Business importance
    - Requirements
    - Constraints
    - Priority

Engineers provide expertise regarding:

    - Technical feasibility
    - Architecture
    - System limitations
    - Development complexity
    - Technical risk
    - Performance
    - Security
    - Scalability

A weak relationship treats engineering as a feature factory.

A stronger relationship involves engineers early because technical
knowledge can influence product decisions.

The best solution may not be the first product idea.

Technical constraints sometimes lead to better and simpler product
solutions.
""")


# ============================================================================
# SECTION 18: WORKING WITH DESIGN
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT AND DESIGN")
print("=" * 80)

print("""
Product design is not decoration.

Design addresses how users interact with a product and whether the product
can be understood and used effectively.

Product Managers should work with designers to understand:

    User goals
    User flows
    Information hierarchy
    Interaction patterns
    Accessibility
    Error states
    Edge cases
    User feedback

A Product Manager should avoid prescribing every visual detail.

The PM should communicate:

    What problem needs to be solved?
    Who experiences the problem?
    What outcome matters?
    What constraints exist?

The design team should contribute expertise about how the experience can
best achieve those objectives.
""")


# ============================================================================
# SECTION 19: AGILE AND PRODUCT MANAGEMENT
# ============================================================================

print("\n" + "=" * 80)
print("AGILE ENVIRONMENTS")
print("=" * 80)

print("""
Agile is frequently misunderstood as simply working in short development
cycles.

The deeper purpose is to reduce uncertainty by learning and adapting.

Common concepts include:

    Product Backlog
    Sprint
    Sprint Planning
    Daily Stand-up
    Sprint Review
    Retrospective

A Product Manager may work closely with these processes, although the
exact responsibilities vary by organisation.

Agile does not eliminate the need for strategy.

A team can efficiently deliver the wrong product.

The Product Manager must therefore connect:

    Long-term strategy
            ↓
    Product objectives
            ↓
    Roadmap initiatives
            ↓
    Prioritised work
            ↓
    Development
            ↓
    Customer outcomes
""")


# ============================================================================
# SECTION 20: PRODUCT METRICS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT METRICS")
print("=" * 80)

print("""
Product decisions should be connected to measurable outcomes where
possible.

Important categories include:

    Acquisition
    Activation
    Engagement
    Retention
    Revenue
    Referral

This structure is sometimes represented as AARRR:

    Acquisition
    Activation
    Retention
    Revenue
    Referral
""")

metrics = {
    "Acquisition": [
        "New users",
        "Traffic",
        "Cost per acquisition"
    ],
    "Activation": [
        "Onboarding completion",
        "First successful action",
        "Time to first value"
    ],
    "Engagement": [
        "Daily active users",
        "Monthly active users",
        "Feature usage"
    ],
    "Retention": [
        "Weekly retention",
        "Monthly retention",
        "Churn rate"
    ],
    "Revenue": [
        "Revenue",
        "Average revenue per user",
        "Conversion rate"
    ]
}

for category, examples in metrics.items():
    print(f"\n{category}")
    for metric in examples:
        print(f"  - {metric}")


# ============================================================================
# SECTION 21: NORTH STAR METRIC
# ============================================================================

print("\n" + "=" * 80)
print("NORTH STAR METRIC")
print("=" * 80)

print("""
A North Star Metric represents a meaningful measure of value delivered by
the product.

It should ideally connect user value and sustainable business success.

Examples differ by product.

For a marketplace:

    Successful transactions

For a communication product:

    Meaningful interactions

For an educational platform:

    Successful learning outcomes

The important point is that the North Star Metric should not merely be a
vanity metric.

A vanity metric can look impressive without demonstrating meaningful value.

For example:

    Total registered users

may increase even if most users never use the product.
""")


# ============================================================================
# SECTION 22: PRODUCT ANALYTICS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT ANALYTICS")
print("=" * 80)

print("""
Product analytics helps answer questions such as:

    Where are users leaving the product?

    Which features are being used?

    Which user groups are retaining?

    What behaviour is associated with successful users?

    Did a product change improve outcomes?

A Product Manager should develop analytical thinking.

This does not necessarily mean becoming a data scientist.

It means being able to:

    Frame a question
    Identify relevant data
    Understand patterns
    Recognise limitations
    Avoid confusing correlation with causation
    Make decisions using evidence
""")


# ============================================================================
# SECTION 23: FUNNEL ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("FUNNEL ANALYSIS")
print("=" * 80)

funnel = {
    "Visited Website": 10000,
    "Created Account": 4000,
    "Completed Onboarding": 2800,
    "Used Core Feature": 1800,
    "Purchased Product": 600
}

previous_stage = None

for stage, users in funnel.items():
    print(f"\n{stage}: {users} users")

    if previous_stage is not None:
        conversion = users / previous_stage * 100
        print(f"Conversion from previous stage: {conversion:.2f}%")

    previous_stage = users

print("""
A funnel identifies where users move through a process and where they
drop out.

The existence of a drop-off does not automatically explain why it occurs.

Quantitative data identifies patterns.

Qualitative research helps explain those patterns.

For example:

    Data:
        Many users abandon onboarding.

    Research:
        Users report confusion about a required form field.

The combination produces a stronger product decision.
""")


# ============================================================================
# SECTION 24: RETENTION
# ============================================================================

print("\n" + "=" * 80)
print("RETENTION")
print("=" * 80)

print("""
Acquiring users is not sufficient.

A product must usually provide recurring value if it depends on continued
usage.

Retention asks:

    Do users return?

    Do they continue receiving value?

    At what point do they stop?

Retention analysis often examines cohorts.

A cohort is a group of users sharing a common characteristic, such as:

    Users who joined during the same month.

Example:

    January cohort:
        1,000 users joined.

    After one month:
        600 remained active.

    One-month retention:
        60%.

Cohort analysis can reveal whether changes in the product improve or
reduce long-term behaviour.
""")


# ============================================================================
# SECTION 25: EXPERIMENTATION AND A/B TESTING
# ============================================================================

print("\n" + "=" * 80)
print("EXPERIMENTATION")
print("=" * 80)

print("""
Experimentation allows Product Managers to test assumptions.

Example assumption:

    "Reducing onboarding steps will increase activation."

An experiment may compare:

    Version A:
        Existing onboarding.

    Version B:
        Simplified onboarding.

The relevant outcome could be:

    Activation rate.

A/B testing requires careful thinking.

Potential problems include:

    Small sample sizes
    Incorrect metrics
    Seasonal behaviour
    Selection bias
    Statistical noise
    Multiple simultaneous changes

A Product Manager should not interpret every numerical difference as a
meaningful result.
""")


# ============================================================================
# SECTION 26: BUSINESS MODELS
# ============================================================================

print("\n" + "=" * 80)
print("BUSINESS MODELS")
print("=" * 80)

business_models = {
    "Subscription": "Customers pay recurring fees.",
    "Marketplace": "The platform earns from transactions.",
    "Advertising": "Revenue comes from advertisers.",
    "Freemium": "Basic functionality is free and advanced features are paid.",
    "Transaction Fee": "Revenue is earned for each transaction.",
    "Licensing": "Customers pay for the right to use technology or content.",
    "Enterprise Sales": "Products are sold directly to organisations."
}

for model, description in business_models.items():
    print(f"\n{model}: {description}")


# ============================================================================
# SECTION 27: PRODUCT ECONOMICS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT ECONOMICS")
print("=" * 80)

print("""
Product Managers should understand the economics of the products they
manage.

Important concepts include:

    Customer Acquisition Cost (CAC)

    Lifetime Value (LTV)

    Gross Margin

    Conversion Rate

    Churn

    Average Revenue Per User (ARPU)

A simplified relationship is:

    Sustainable business
        =
    Valuable customers
        +
    Efficient acquisition
        +
    Sufficient retention
        +
    Viable economics

Growth without sustainable economics can create long-term problems.
""")


# ============================================================================
# SECTION 28: PRODUCT LAUNCH
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT LAUNCH")
print("=" * 80)

print("""
A product launch is more than deploying software.

A launch may require coordination across:

    Engineering
    Design
    Marketing
    Sales
    Customer Support
    Legal
    Operations
    Leadership

Important launch considerations include:

    Who is the target audience?

    How will users discover the feature?

    What information do users need?

    Is customer support prepared?

    Are analytics implemented?

    What happens if the product fails?

    How will success be measured?

A technically successful deployment can still be a commercially unsuccessful
launch if customers do not understand, discover, trust, or adopt the
product.
""")


# ============================================================================
# SECTION 29: STAKEHOLDER MANAGEMENT
# ============================================================================

print("\n" + "=" * 80)
print("STAKEHOLDER MANAGEMENT")
print("=" * 80)

print("""
Product Managers frequently work without direct authority over everyone
involved in product development.

This makes stakeholder management essential.

Stakeholders may include:

    Executives
    Engineers
    Designers
    Sales teams
    Marketing teams
    Customers
    Operations teams
    Legal teams
    Finance teams

Effective stakeholder management requires:

    Clear communication
    Shared understanding
    Early alignment
    Transparent trade-offs
    Evidence-based reasoning
    Appropriate expectation management

Stakeholder management is not simply agreeing with everyone.

Conflicting priorities are normal.

The Product Manager must make the reasoning behind decisions visible.
""")


# ============================================================================
# SECTION 30: COMMUNICATION
# ============================================================================

print("\n" + "=" * 80)
print("COMMUNICATION AS A PRODUCT MANAGEMENT SKILL")
print("=" * 80)

print("""
Product Management requires different communication styles for different
audiences.

Executive communication usually needs:

    Context
    Decision
    Business impact
    Risk
    Required action

Engineering communication often needs:

    Problem
    User context
    Requirements
    Priority
    Constraints

Customer communication often needs:

    Clear language
    Relevant value
    Minimal jargon

One of the most important skills is the ability to reduce unnecessary
complexity without losing important information.
""")


# ============================================================================
# SECTION 31: DECISION MAKING
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT DECISION MAKING")
print("=" * 80)

print("""
Product Managers rarely have perfect information.

Decisions are often made under uncertainty.

A useful decision process is:

    1. Define the decision.
    2. Identify the available options.
    3. Gather relevant evidence.
    4. Identify assumptions.
    5. Evaluate risks.
    6. Understand trade-offs.
    7. Make the decision.
    8. Measure the result.
    9. Update understanding.

The ability to reverse a decision is also important.

Some decisions are difficult to reverse.

Others are relatively inexpensive experiments.

High-risk and irreversible decisions usually require greater analysis.
Reversible decisions can often be tested more quickly.
""")


# ============================================================================
# SECTION 32: TRADE-OFFS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT TRADE-OFFS")
print("=" * 80)

print("""
Product decisions frequently involve trade-offs.

Examples:

    Speed vs quality

    Feature breadth vs simplicity

    Short-term revenue vs long-term trust

    Customisation vs maintainability

    Innovation vs reliability

    User demand vs strategic direction

There is rarely a universally correct answer.

The Product Manager must understand what is being sacrificed when a
particular decision is made.

A decision is stronger when its trade-off is explicit.
""")


# ============================================================================
# SECTION 33: TECHNICAL PRODUCT MANAGEMENT
# ============================================================================

print("\n" + "=" * 80)
print("TECHNICAL PRODUCT MANAGEMENT")
print("=" * 80)

print("""
Technical Product Managers work on products or domains where technical
understanding is particularly important.

Examples include:

    Developer platforms
    APIs
    Cloud systems
    Cybersecurity products
    Data platforms
    Machine learning products
    Infrastructure products

A Technical Product Manager does not necessarily need to write production
software every day.

Technical competence can include understanding:

    APIs
    Databases
    System architecture
    Authentication
    Data flows
    Cloud infrastructure
    Performance
    Scalability
    Security constraints

The required technical depth depends heavily on the product.
""")


# ============================================================================
# SECTION 34: AI PRODUCT MANAGEMENT
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT FOR AI-BASED PRODUCTS")
print("=" * 80)

print("""
AI-based products introduce additional uncertainties.

Traditional software often follows deterministic logic.

AI systems may produce probabilistic outputs.

This creates additional product concerns:

    Model accuracy
    Failure behaviour
    Data quality
    Bias
    Explainability
    Evaluation
    Latency
    Cost
    User trust
    Human oversight

A product feature based on a machine learning model must be evaluated as
both:

    A technical system

and

    A user experience.

A model can perform well on a technical benchmark but still create a poor
user experience.
""")


# ============================================================================
# SECTION 35: PRODUCT MANAGER CAREER LEVELS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT CAREER PROGRESSION")
print("=" * 80)

career_levels = {
    "Associate Product Manager": [
        "Learns product development processes",
        "Owns smaller features",
        "Conducts research",
        "Supports experienced PMs"
    ],
    "Product Manager": [
        "Owns product areas",
        "Defines requirements",
        "Prioritises work",
        "Measures outcomes"
    ],
    "Senior Product Manager": [
        "Owns complex product areas",
        "Influences strategy",
        "Handles greater ambiguity",
        "Mentors other PMs"
    ],
    "Lead or Principal Product Manager": [
        "Solves highly complex strategic problems",
        "Influences multiple teams",
        "Provides product leadership"
    ],
    "Group Product Manager": [
        "Manages multiple product areas",
        "May manage Product Managers",
        "Coordinates product strategy"
    ],
    "Director of Product": [
        "Leads significant product organisations",
        "Defines broader product strategy"
    ],
    "Vice President of Product": [
        "Owns major product strategy and organisation"
    ],
    "Chief Product Officer": [
        "Provides executive product leadership"
    ]
}

for level, responsibilities_at_level in career_levels.items():
    print(f"\n{level}")
    for responsibility in responsibilities_at_level:
        print(f"  - {responsibility}")


# ============================================================================
# SECTION 36: CORE PRODUCT MANAGEMENT SKILLS
# ============================================================================

print("\n" + "=" * 80)
print("CORE SKILLS")
print("=" * 80)

core_skills = {
    "Product Thinking": "Understanding problems before solutions.",
    "User Research": "Understanding user behaviour and needs.",
    "Communication": "Creating clarity across different audiences.",
    "Prioritisation": "Choosing what deserves resources.",
    "Analytics": "Using data to understand behaviour and outcomes.",
    "Strategy": "Connecting decisions to long-term objectives.",
    "Business Understanding": "Understanding markets and economics.",
    "Technical Understanding": "Understanding product constraints and systems.",
    "Leadership": "Influencing without relying solely on authority.",
    "Decision Making": "Making sound choices under uncertainty."
}

for skill, explanation in core_skills.items():
    print(f"\n{skill}: {explanation}")


# ============================================================================
# SECTION 37: PRODUCT PORTFOLIO
# ============================================================================

print("\n" + "=" * 80)
print("BUILDING A PRODUCT MANAGEMENT PORTFOLIO")
print("=" * 80)

print("""
A Product Management portfolio demonstrates thinking rather than simply
listing certificates.

Useful portfolio material can include:

    Product case studies
    Product improvement analyses
    Market research
    User research exercises
    PRDs
    Product strategy documents
    Roadmaps
    Prioritisation analyses
    Product metric analysis
    Product experiments

A strong case study generally demonstrates:

    Context
        ↓
    Problem
        ↓
    Research
        ↓
    Insights
        ↓
    Options
        ↓
    Decision
        ↓
    Proposed solution
        ↓
    Measurement approach

The quality of reasoning is more important than the visual complexity of
the portfolio.
""")


# ============================================================================
# SECTION 38: PRODUCT MANAGEMENT INTERVIEWS
# ============================================================================

print("\n" + "=" * 80)
print("PRODUCT MANAGEMENT INTERVIEWS")
print("=" * 80)

interview_categories = {
    "Product Sense": "Evaluate how you identify users, problems, and solutions.",
    "Product Design": "Evaluate how you design or improve products.",
    "Strategy": "Evaluate market, competition, and business thinking.",
    "Analytics": "Evaluate data interpretation and metric reasoning.",
    "Execution": "Evaluate prioritisation and delivery judgement.",
    "Behavioural": "Evaluate collaboration, leadership, and experience.",
    "Technical": "Evaluate technical understanding where relevant."
}

for category, purpose in interview_categories.items():
    print(f"\n{category}: {purpose}")


# ============================================================================
# SECTION 39: COMMON PRODUCT MANAGEMENT MISTAKES
# ============================================================================

print("\n" + "=" * 80)
print("COMMON PRODUCT MANAGEMENT MISTAKES")
print("=" * 80)

mistakes = [
    "Starting with features instead of problems",
    "Treating user requests as unquestionable requirements",
    "Copying competitors without understanding strategy",
    "Using metrics without understanding context",
    "Confusing activity with product impact",
    "Building before validating assumptions",
    "Ignoring technical constraints",
    "Communicating requirements without explaining the problem",
    "Trying to satisfy every stakeholder request",
    "Measuring outputs instead of outcomes",
    "Over-prioritising short-term requests",
    "Ignoring edge cases and failure scenarios"
]

for index, mistake in enumerate(mistakes, start=1):
    print(f"{index}. {mistake}")


# ============================================================================
# SECTION 40: ADVANCED PRODUCT MANAGEMENT THINKING
# ============================================================================

print("\n" + "=" * 80)
print("ADVANCED PRODUCT MANAGEMENT")
print("=" * 80)

print("""
Advanced Product Management is increasingly characterised by the ability
to operate effectively in ambiguity.

At higher levels, the problem is often not:

    "Which button should we add?"

The problem becomes:

    "Which market should we enter?"

    "Should this product exist?"

    "Which customer segment should we stop serving?"

    "How should we allocate limited resources?"

    "What should the company optimise for?"

    "Which opportunities should be deliberately ignored?"

Senior product leadership therefore requires:

    Systems thinking
    Strategic judgement
    Organisational awareness
    Financial understanding
    Risk management
    Long-term thinking
    Strong communication
    Ability to influence decisions

The career develops from managing features toward managing increasingly
complex decisions and outcomes.
""")


# ============================================================================
# FINAL PRODUCT MANAGEMENT PRINCIPLE
# ============================================================================

print("\n" + "=" * 80)
print("CENTRAL PRINCIPLE OF PRODUCT MANAGEMENT")
print("=" * 80)

print("""
Product Management is fundamentally the disciplined practice of making
better decisions about where an organisation should invest its limited
resources in order to create meaningful value.

The work combines:

    Understanding people
    Understanding problems
    Understanding markets
    Understanding technology
    Understanding business
    Making decisions
    Measuring outcomes

The Product Manager's role is therefore not defined by writing documents,
attending meetings, maintaining backlogs, or managing feature requests.

Those activities are mechanisms.

The underlying responsibility is to create clarity under uncertainty and
to guide product decisions toward meaningful outcomes.
""")

print("=" * 80)
print("END OF PRODUCT MANAGEMENT CAREER LEARNING SCRIPT")
print("=" * 80)
