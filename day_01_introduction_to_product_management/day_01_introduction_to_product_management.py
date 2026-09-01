"""
======================================================================
DAY 01: INTRODUCTION TO PRODUCT MANAGEMENT
======================================================================

TOPIC:
Introduction to Product Management

COVERS:
- What is a Product?
- What is Product Management?
- Why Product Management exists
- Product Manager role
- Product vs Feature
- Product vs Project
- Digital vs Physical Products
- Users vs Customers vs Buyers vs Stakeholders
- Product Thinking
- Product Discovery
- Product Delivery
- Product Value
- Product Strategy
- Product Vision
- Product Goals
- Product Roadmaps
- Product Requirements
- PRDs
- User Stories
- Acceptance Criteria
- MVP
- Product Lifecycle
- Product-Market Fit
- Product Metrics
- Prioritization
- Trade-offs
- Stakeholder Management
- Cross-functional teams
- Product Documentation
- Notion
- Google Docs
- Product Hypotheses
- Output vs Outcome vs Impact
- Advanced Product Management Mental Models
- Product Decision Making
- Product Operating Rhythm
- Product Management Skill Stack
- Case Study
- Knowledge Check

======================================================================
HOW TO USE THIS SCRIPT
======================================================================

Run the file in Python.

Example:

    python day_01_introduction_to_product_management.py

The script is intentionally verbose. Read each section carefully rather
than simply executing it.

======================================================================
"""


# ======================================================================
# UTILITY FUNCTIONS
# ======================================================================

def title(text):
    print("\n")
    print("=" * 80)
    print(text.upper())
    print("=" * 80)


def section(number, text):
    print("\n")
    print(f"{number}. {text}")
    print("-" * 80)


def subsection(text):
    print(f"\n{text}")
    print("~" * len(text))


def bullet(text, level=0):
    print("    " * level + "• " + text)


def explain(term, definition, example=None):
    print(f"\n{term}")
    print(f"Definition: {definition}")

    if example:
        print(f"Example: {example}")


def question(number, text):
    print(f"\n{number}. {text}")


# ======================================================================
# INTRODUCTION
# ======================================================================

title("DAY 01 - INTRODUCTION TO PRODUCT MANAGEMENT")

print("""
Welcome to Product Management.

This lesson is designed to build your foundation from zero.

The objective is not merely to memorize definitions.

The objective is to understand how Product Managers think.

A Product Manager must continuously answer questions such as:

    Who are we building for?
    What problem are we solving?
    Why does this problem matter?
    How important is the problem?
    What evidence do we have?
    What solution should we consider?
    What should we prioritize?
    What should we deliberately NOT build?
    How does this support the business?
    How will we measure success?
    What did we learn after launch?

The central Product Management loop is:

    PROBLEM
       |
       v
    RESEARCH
       |
       v
    OPPORTUNITY
       |
       v
    PRIORITIZATION
       |
       v
    SOLUTION
       |
       v
    EXECUTION
       |
       v
    LAUNCH
       |
       v
    MEASUREMENT
       |
       v
    LEARNING
       |
       +-----------> NEXT DECISION


The biggest mindset shift:

Do not think:

    "What feature should we build?"

Start thinking:

    "What important problem should we solve,
     for whom,
     why,
     and how do we know?"
""")


# ======================================================================
# SECTION 1
# ======================================================================

section(1, "What Is a Product?")

explain(
    "PRODUCT",
    "A product is a solution, offering, experience, service, system, "
    "or combination of capabilities created to provide value to a "
    "specific group of users or customers."
)

print("""
A product is NOT necessarily a physical object.

A product can be:

    Physical
    Digital
    Software
    Hardware
    Service
    Platform
    Marketplace
    Subscription
    API
    Data product
    Internal company system
    Hybrid physical + digital system
""")


subsection("Examples of Products")

examples = [
    "A smartphone",
    "A banking application",
    "A food delivery platform",
    "An electric vehicle",
    "A payment gateway",
    "A cloud storage service",
    "A project management platform",
    "An internal HR system",
    "A developer API",
    "A subscription-based learning platform",
]

for item in examples:
    bullet(item)


subsection("Product Is About Value")

print("""
Suppose you buy a smartphone.

You are not really buying:

    glass
    metal
    processor
    camera
    battery

You are buying a collection of outcomes:

    communication
    entertainment
    productivity
    photography
    navigation
    access to services
    social interaction
    convenience

Therefore:

    PRODUCT = VALUE DELIVERY SYSTEM

The physical or digital artifact is only one part of that system.
""")


# ======================================================================
# SECTION 2
# ======================================================================

section(2, "Product vs Feature")

explain(
    "FEATURE",
    "A feature is a specific capability or functionality contained "
    "within a product."
)

print("""
Example:

PRODUCT:
    Banking application

FEATURES:
    Check balance
    Transfer money
    Pay bills
    Download statement
    Freeze card
    Set transaction limits

The product is larger than any single feature.

A common beginner mistake is:

    Feature = Product

That is incorrect.

A feature exists to contribute to product value.

The Product Manager therefore asks:

    Why do we need this feature?
    Which user problem does it solve?
    Which outcome should it improve?
    How important is that outcome?
    What happens if we do not build it?
""")


# ======================================================================
# SECTION 3
# ======================================================================

section(3, "Product vs Project vs Program vs Feature")

definitions = {
    "Product": (
        "A continuing offering designed to create value for users "
        "and the business."
    ),
    "Feature": (
        "A specific capability within a product."
    ),
    "Project": (
        "A temporary effort undertaken to achieve a defined objective."
    ),
    "Program": (
        "A coordinated collection of related projects or initiatives."
    ),
    "Platform": (
        "A reusable foundation that supports multiple products, "
        "teams, users, or capabilities."
    )
}

for term, definition in definitions.items():
    explain(term, definition)


print("""
Example:

COMPANY:
    E-commerce company

PRODUCT:
    Online shopping platform

FEATURE:
    Wishlist

PROJECT:
    Redesign checkout

PROGRAM:
    Global commerce modernization

PLATFORM:
    Internal commerce infrastructure


Important distinction:

A project ends.

A product generally continues evolving.

This difference is fundamental.
""")


# ======================================================================
# SECTION 4
# ======================================================================

section(4, "What Is Product Management?")

explain(
    "PRODUCT MANAGEMENT",
    "Product Management is the discipline of understanding customer "
    "problems and business opportunities, deciding what is worth solving, "
    "guiding product development, and continuously measuring and improving "
    "the resulting product."
)

print("""
Product Management sits at the intersection of:

    CUSTOMER
       |
       |
BUSINESS ---- PRODUCT ---- TECHNOLOGY
       |
       |
     DATA
       |
     DESIGN


A Product Manager must understand enough about multiple disciplines
to make informed product decisions.

The PM does not need to be:

    The best engineer
    The best designer
    The best marketer
    The best salesperson
    The best data scientist

But the PM must be capable of working intelligently with all of them.
""")


# ======================================================================
# SECTION 5
# ======================================================================

section(5, "Why Does Product Management Exist?")

print("""
Imagine a company with:

    100 engineers
    20 designers
    10 marketers
    10 salespeople
    5 analysts
    5 finance professionals
    5 operations professionals

Every department has its own perspective.

Engineering may ask:

    "Can we build it?"

Design may ask:

    "Can users understand it?"

Marketing may ask:

    "Can we position it?"

Sales may ask:

    "Will customers buy it?"

Finance may ask:

    "Is it economically viable?"

Legal may ask:

    "Is it compliant?"

Leadership may ask:

    "Does this support the strategy?"

Customers may ask:

    "Does this solve my problem?"

Someone must connect these perspectives.

That coordination and decision problem is one major reason
Product Management exists.
""")


subsection("The Coordination Problem")

print("""
Without product management, an organization can experience:

    Conflicting priorities
    Feature overload
    Duplicate work
    Poor communication
    Misaligned teams
    Unclear ownership
    Weak customer understanding
    Technical work with little customer value
    Business requests with poor feasibility
    Roadmaps that become promises rather than strategy

The PM helps create:

    CLARITY
    ALIGNMENT
    PRIORITIZATION
    DECISION-MAKING
    CUSTOMER FOCUS
    OUTCOME FOCUS
""")


# ======================================================================
# SECTION 6
# ======================================================================

section(6, "What Does a Product Manager Actually Do?")

responsibilities = [
    "Understand users and customers",
    "Understand the market",
    "Identify customer problems",
    "Analyze product data",
    "Conduct or support research",
    "Frame problems",
    "Identify opportunities",
    "Define product goals",
    "Develop product strategy",
    "Prioritize opportunities",
    "Create roadmap direction",
    "Write or coordinate product requirements",
    "Collaborate with designers",
    "Collaborate with engineers",
    "Manage stakeholders",
    "Make product decisions",
    "Coordinate launches",
    "Define success metrics",
    "Analyze product performance",
    "Learn from outcomes",
    "Iterate the product",
]

for responsibility in responsibilities:
    bullet(responsibility)


subsection("The PM Is a Decision Maker")

print("""
The PM is often required to make decisions under uncertainty.

For example:

    Should we build feature A or B?

    Should we enter market X or Y?

    Should we prioritize growth or profitability?

    Should we fix an existing problem or launch something new?

    Should we delay the launch for quality improvements?

    Should we sunset an underperforming product?

The PM rarely has perfect information.

Therefore Product Management involves:

    judgment
    evidence
    prioritization
    trade-offs
    communication
    accountability
""")


# ======================================================================
# SECTION 7
# ======================================================================

section(7, "What a Product Manager Is NOT")

myths = [
    (
        "PM = Project Manager",
        "Product Management and Project Management overlap in execution "
        "but have different primary responsibilities."
    ),
    (
        "PM = Requirements Writer",
        "Requirements are one part of product work, not the entire job."
    ),
    (
        "PM = Boss of Engineering",
        "Engineering usually owns technical implementation and engineering decisions."
    ),
    (
        "PM = Feature Factory Manager",
        "The PM should optimize for outcomes rather than feature count."
    ),
    (
        "PM = Person Who Says Yes to Stakeholders",
        "A PM must prioritize, challenge assumptions, and make trade-offs."
    ),
]

for myth, reality in myths:
    print(f"\nMYTH: {myth}")
    print(f"REALITY: {reality}")


# ======================================================================
# SECTION 8
# ======================================================================

section(8, "Users, Customers, Buyers and Stakeholders")

roles = {
    "User": "The person who actually uses the product.",
    "Customer": "The person or organization receiving or purchasing value.",
    "Buyer": "The person responsible for purchasing.",
    "Decision Maker": "The person who can approve or reject a decision.",
    "Stakeholder": "A person or group affected by, influencing, funding, operating, or governing the product."
}

for role, definition in roles.items():
    explain(role, definition)


print("""
Example: Enterprise cybersecurity product

EMPLOYEE
    User

SECURITY MANAGER
    User + Decision Influencer

PROCUREMENT
    Buyer

CISO
    Decision Maker

COMPANY
    Customer

LEGAL
    Stakeholder

IT
    Stakeholder

FINANCE
    Stakeholder


The important lesson:

    User != always Customer
    Customer != always Buyer
    Buyer != always Decision Maker

A PM must understand the entire decision ecosystem.
""")


# ======================================================================
# SECTION 9
# ======================================================================

section(9, "Digital Products")

print("""
Digital products include:

    Mobile applications
    Web applications
    SaaS platforms
    APIs
    Cloud services
    Digital marketplaces
    Streaming services
    Online learning platforms
    Digital financial products
    Data products
""")


subsection("Characteristics of Digital Products")

digital_characteristics = [
    "Can often be updated rapidly",
    "Can be distributed globally",
    "Can have very low marginal distribution cost",
    "Can capture detailed usage data",
    "Can support experimentation",
    "Can scale rapidly",
    "Can have network effects",
    "Can be continuously improved",
    "Can be personalized",
    "Can fail through software bugs or infrastructure problems",
]

for item in digital_characteristics:
    bullet(item)


# ======================================================================
# SECTION 10
# ======================================================================

section(10, "Physical Products")

physical_characteristics = [
    "Require materials",
    "Require manufacturing",
    "Depend on supply chains",
    "Require logistics",
    "Create inventory",
    "May require physical distribution",
    "Can have physical defects",
    "May require certification",
    "May involve safety considerations",
    "Can be expensive to change after production",
]

for item in physical_characteristics:
    bullet(item)


subsection("Hybrid Products")

print("""
Modern products frequently combine digital and physical components.

Examples:

    Smartphone
        Hardware + operating system + apps + cloud services

    Automobile
        Physical vehicle + software + connectivity + services

    Smartwatch
        Hardware + firmware + mobile application + cloud

    ATM
        Hardware + software + banking network + physical operations

    Food delivery
        Mobile application + restaurants + payments + logistics

Therefore:

    Product Management must consider the complete value chain.
""")


# ======================================================================
# SECTION 11
# ======================================================================

section(11, "Product Thinking")

print("""
Product thinking is one of the most important skills in Product Management.

Weak question:

    "What feature should we build?"

Better question:

    "What problem are users experiencing?"

Even better:

    "Which important problem should we solve,
     for which users,
     and why now?"

Advanced question:

    "What outcome are we trying to change,
     what evidence shows the problem exists,
     what alternatives exist,
     and what is the smallest useful intervention
     that can test our assumption?"
""")


subsection("Feature-First Thinking vs Problem-First Thinking")

print("""
FEATURE-FIRST:

    "Competitors have AI chat.
     We should build AI chat."

PROBLEM-FIRST:

    "Customers are waiting too long for support.
     Why?
     Is the problem discoverability?
     Is it response time?
     Is it confusing documentation?
     Would chat actually solve the problem?"

The second approach is stronger because it investigates the problem
before committing to the solution.
""")


# ======================================================================
# SECTION 12
# ======================================================================

section(12, "Product Discovery")

explain(
    "PRODUCT DISCOVERY",
    "The process of learning about users, problems, opportunities, "
    "constraints and potential solutions before or during product development."
)

print("""
Discovery tries to reduce uncertainty.

Typical discovery questions:

    Who has the problem?
    How frequently does it occur?
    How painful is it?
    What do users do today?
    What alternatives exist?
    How much value would solving it create?
    Is the problem strategically important?
    Can we technically solve it?
    Can we build a sustainable business around it?
""")


subsection("Discovery Methods")

discovery_methods = [
    "Customer interviews",
    "User interviews",
    "User observation",
    "Usability testing",
    "Surveys",
    "Support-ticket analysis",
    "Sales-call analysis",
    "Product analytics",
    "Competitive analysis",
    "Market research",
    "Prototyping",
    "Concept testing",
    "A/B testing",
    "Journey mapping",
]

for method in discovery_methods:
    bullet(method)


print("""
The right discovery method depends on the uncertainty.

Example:

Question:
    "Do users understand this design?"

Method:
    Usability testing

Question:
    "Where do users abandon the flow?"

Method:
    Funnel analysis

Question:
    "Why do users abandon the flow?"

Method:
    Interviews + analytics

Question:
    "Does the change increase conversion?"

Method:
    Controlled experiment, where appropriate
""")


# ======================================================================
# SECTION 13
# ======================================================================

section(13, "Product Delivery")

explain(
    "PRODUCT DELIVERY",
    "The process of turning a chosen product direction into a reliable "
    "product capability and making it available to users."
)

print("""
Delivery may involve:

    Product
    Design
    Engineering
    QA
    Security
    Legal
    Operations
    Marketing
    Sales
    Customer Support

The PM helps ensure that everyone understands:

    What are we building?
    Why are we building it?
    Who is it for?
    What are the constraints?
    What does success mean?
    What decisions remain unresolved?
""")


# ======================================================================
# SECTION 14
# ======================================================================

section(14, "Discovery vs Delivery")

print("""
DISCOVERY:

    Are we solving the right problem?

DELIVERY:

    Are we building and releasing the chosen solution correctly?


A team can fail in two ways:

FAILURE TYPE 1:
    Build the wrong product perfectly.

FAILURE TYPE 2:
    Identify the right problem but execute poorly.

Strong Product Management tries to reduce both risks.
""")


# ======================================================================
# SECTION 15
# ======================================================================

section(15, "Product Value")

value_types = {
    "Functional Value":
        "Helps users accomplish something.",
    "Economic Value":
        "Makes money, saves money, or improves efficiency.",
    "Time Value":
        "Reduces time or effort.",
    "Emotional Value":
        "Creates confidence, enjoyment, trust, comfort, or status.",
    "Social Value":
        "Helps users communicate, participate, or belong.",
    "Risk Reduction":
        "Reduces errors, uncertainty, fraud, losses, or operational risk."
}

for value_type, definition in value_types.items():
    explain(value_type, definition)


print("""
The PM should ask:

    What value are we creating?

    For whom?

    How important is the value?

    How frequently does the problem occur?

    What does the user do today?

    Why would they switch?

    Can the company deliver this value profitably?

    Can the company defend this value over time?
""")


# ======================================================================
# SECTION 16
# ======================================================================

section(16, "Product Vision")

explain(
    "PRODUCT VISION",
    "A description of the future state the product or product organization "
    "is trying to create."
)

print("""
Example:

Weak:

    "We want to build a banking app."

Vision-oriented:

    "Make everyday banking simple, transparent, and accessible from anywhere."


Vision answers:

    Where are we going?

Strategy answers:

    How will we move there?

Goals answer:

    What measurable progress do we need?

Initiatives answer:

    What major work could help?

Features answer:

    What capabilities will users receive?
""")


# ======================================================================
# SECTION 17
# ======================================================================

section(17, "Product Strategy")

print("""
A useful hierarchy:

    VISION
       |
       v
    STRATEGY
       |
       v
    GOALS
       |
       v
    PRIORITIES
       |
       v
    INITIATIVES
       |
       v
    FEATURES
       |
       v
    TASKS
       |
       v
    OUTCOMES
""")


subsection("What Is Strategy?")

print("""
Strategy is fundamentally about choices.

A strategy should clarify:

    Where will we compete?
    Who will we serve?
    What problems will we prioritize?
    What will differentiate us?
    What capabilities matter?
    What will we deliberately NOT pursue?

Strategy requires trade-offs.

If everything is a priority,
nothing is truly a priority.
""")


# ======================================================================
# SECTION 18
# ======================================================================

section(18, "Product Goals")

print("""
A product goal describes the change the team wants to create.

Example:

BAD:

    "Build onboarding redesign."

This is an output.

BETTER:

    "Increase successful onboarding."

This is closer to an outcome.

EVEN BETTER:

    "Increase onboarding completion from 45% to 60% without increasing fraud
     or support contacts."

Now the desired outcome is measurable and includes guardrails.
""")


# ======================================================================
# SECTION 19
# ======================================================================

section(19, "Output vs Outcome vs Impact")

explain(
    "OUTPUT",
    "What the team produces.",
    "A new onboarding screen."
)

explain(
    "OUTCOME",
    "A measurable change in behavior or product performance.",
    "Onboarding completion increases."
)

explain(
    "IMPACT",
    "The broader value created for customers or the business.",
    "More qualified customers successfully activate and become retained customers."
)

print("""
Hierarchy:

    OUTPUT
       |
       v
    OUTCOME
       |
       v
    IMPACT


Important:

    Shipping does not guarantee an outcome.

    An outcome does not automatically guarantee long-term impact.

Therefore PMs should avoid measuring success only through:

    Features shipped
    Tickets closed
    Story points completed
    Lines of code
    Number of releases
""")


# ======================================================================
# SECTION 20
# ======================================================================

section(20, "Product Roadmaps")

explain(
    "PRODUCT ROADMAP",
    "A communication and planning artifact that expresses product direction, "
    "priorities, themes, initiatives, outcomes, or expected sequencing over time."
)

print("""
A roadmap can communicate:

    Strategic themes
    Problems
    Outcomes
    Initiatives
    Product bets
    Time horizons
    Confidence
    Dependencies


A roadmap should NOT automatically be treated as:

    A fixed promise
    A complete feature list
    An engineering backlog
    A detailed project schedule


The further into the future we look,
the less certainty we usually have.

Therefore:

    NEAR TERM
        More detail

    MID TERM
        Moderate detail

    LONG TERM
        Higher-level direction
""")


# ======================================================================
# SECTION 21
# ======================================================================

section(21, "Product Requirements")

explain(
    "REQUIREMENT",
    "A condition, capability, constraint, or expectation that a product "
    "must satisfy."
)

requirements = {
    "User Requirement":
        "What the user needs.",
    "Business Requirement":
        "What the business needs.",
    "Functional Requirement":
        "What the system should do.",
    "Non-Functional Requirement":
        "How well the system should perform."
}

for requirement_type, definition in requirements.items():
    explain(requirement_type, definition)


print("""
Example:

USER REQUIREMENT:

    "I need to regain access to my account."

FUNCTIONAL REQUIREMENT:

    "The user can reset their password."

NON-FUNCTIONAL REQUIREMENT:

    "The reset request should complete within an acceptable response time."

BUSINESS REQUIREMENT:

    "Reduce password-recovery support contacts."

Notice that one problem can generate multiple types of requirements.
""")


# ======================================================================
# SECTION 22
# ======================================================================

section(22, "PRD - Product Requirements Document")

print("""
A practical PRD may contain:

    1. Title
    2. Context
    3. Problem statement
    4. Target users
    5. Evidence
    6. Goal
    7. Non-goals
    8. Proposed approach
    9. User experience
    10. Functional requirements
    11. Non-functional requirements
    12. Edge cases
    13. Dependencies
    14. Risks
    15. Analytics
    16. Acceptance criteria
    17. Rollout plan
    18. Open questions
    19. Decision log


A good PRD should create clarity.

It should NOT pretend that every uncertainty has already been solved.
""")


# ======================================================================
# SECTION 23
# ======================================================================

section(23, "User Stories")

explain(
    "USER STORY",
    "A concise representation of a user need or capability, generally "
    "written from the user's perspective."
)

print("""
Common format:

    As a [user],
    I want [capability],
    so that [benefit/outcome].


Example:

    As a customer,
    I want to reset my password,
    so that I can regain access to my account.
""")


subsection("Important Limitation")

print("""
A user story is not always enough.

Complex requirements may also need:

    Business rules
    Edge cases
    Security requirements
    Error handling
    Dependencies
    Analytics
    Performance requirements
    Regulatory constraints
    Acceptance criteria
""")


# ======================================================================
# SECTION 24
# ======================================================================

section(24, "Acceptance Criteria")

explain(
    "ACCEPTANCE CRITERIA",
    "Specific conditions that describe when a product capability satisfies "
    "the agreed expectations."
)

print("""
Example:

USER STORY:

    As a customer,
    I want to reset my password,
    so that I can regain access.

ACCEPTANCE CRITERIA:

    A valid email can initiate password recovery.

    An invalid account does not expose sensitive information.

    The user receives the recovery instructions.

    The reset link expires according to the defined security policy.

    The new password must satisfy password rules.
""")


# ======================================================================
# SECTION 25
# ======================================================================

section(25, "MVP")

explain(
    "MVP - MINIMUM VIABLE PRODUCT",
    "A deliberately limited product or test designed to validate important "
    "assumptions while providing enough value to generate meaningful learning."
)

print("""
MVP does NOT mean:

    Bad product
    Broken product
    Cheapest possible product
    Lowest quality
    Random collection of features


The important concept is:

    MINIMUM VIABLE LEARNING


Before building software, an MVP might be:

    Prototype
    Landing page
    Manual service
    Spreadsheet
    Concierge service
    Pilot
    Limited release
    Wizard-of-Oz experiment
""")


# ======================================================================
# SECTION 26
# ======================================================================

section(26, "Product Hypotheses")

print("""
A hypothesis is an assumption that can be tested.

Template:

    We believe that [USER SEGMENT]
    has [PROBLEM]
    and that [INTERVENTION]
    will cause [OUTCOME]
    because [REASON/EVIDENCE].
""")


print("""
Example:

    We believe that new users abandon onboarding because
    identity verification requirements are unclear.

    Providing clearer explanations will increase completion

    because it reduces uncertainty.
""")


print("""
The structure becomes:

    ASSUMPTION
        |
        v
    INTERVENTION
        |
        v
    BEHAVIOR CHANGE
        |
        v
    OUTCOME
""")


# ======================================================================
# SECTION 27
# ======================================================================

section(27, "Prioritization")

print("""
Product teams never have unlimited resources.

Constraints include:

    Time
    Money
    Engineering capacity
    Design capacity
    Attention
    Organizational capacity
    Technical constraints


Therefore the PM must answer:

    What should we do?

    What should we do next?

    What should we postpone?

    What should we stop?

    What should we never build?
""")


subsection("RICE")

print("""
RICE is a prioritization framework.

RICE:

    Reach × Impact × Confidence
    ---------------------------
             Effort


It helps compare initiatives using:

    Reach
    Impact
    Confidence
    Effort

Important:

A framework does not magically produce the correct answer.

It helps make assumptions explicit.
""")


subsection("MoSCoW")

print("""
MoSCoW:

    MUST HAVE
    SHOULD HAVE
    COULD HAVE
    WON'T HAVE

It can be useful for clarifying scope and expectations.
""")


subsection("Value vs Effort")

print("""
Another simple approach:

    HIGH VALUE + LOW EFFORT
        Strong candidate

    HIGH VALUE + HIGH EFFORT
        Strategic decision

    LOW VALUE + LOW EFFORT
        Consider carefully

    LOW VALUE + HIGH EFFORT
        Usually deprioritize
""")


# ======================================================================
# SECTION 28
# ======================================================================

section(28, "Opportunity Cost")

print("""
Opportunity cost is one of the most important Product Management concepts.

Suppose you have capacity for only one initiative.

OPTION A:
    Improve onboarding

OPTION B:
    Build a recommendation engine

OPTION C:
    Improve reporting

Choosing A means you are also choosing:

    NOT B
    NOT C
    at least for now


Therefore prioritization is not just:

    "How valuable is this?"

It is:

    "Is this more valuable than the alternatives we could pursue?"
""")


# ======================================================================
# SECTION 29
# ======================================================================

section(29, "Product Trade-offs")

tradeoffs = [
    "Speed vs Quality",
    "Growth vs Profitability",
    "Simplicity vs Flexibility",
    "Customization vs Standardization",
    "Short-term Revenue vs Long-term Trust",
    "Automation vs Human Support",
    "Privacy vs Personalization",
    "Reliability vs Release Velocity",
    "Scope vs Timeline",
    "Innovation vs Stability",
]

for item in tradeoffs:
    bullet(item)


print("""
A strong PM does not pretend trade-offs do not exist.

A strong PM makes trade-offs visible.

The PM should explain:

    What are the options?
    What do we gain?
    What do we sacrifice?
    What assumptions are we making?
    What risks are we accepting?
    How reversible is the decision?
    What evidence could change our mind?
""")


# ======================================================================
# SECTION 30
# ======================================================================

section(30, "Product Lifecycle")

lifecycle = [
    ("1. Opportunity",
     "A problem, need, market change, technology shift, or strategic opportunity is identified."),

    ("2. Discovery",
     "The team investigates customers, problems, alternatives, feasibility, and economics."),

    ("3. Validation",
     "Important assumptions are tested."),

    ("4. Development",
     "The solution is designed, engineered, tested, and prepared."),

    ("5. Launch",
     "The product is introduced to users or customers."),

    ("6. Adoption",
     "Users begin discovering and using the product."),

    ("7. Growth",
     "The organization improves acquisition, activation, retention, monetization, and scale."),

    ("8. Maturity",
     "The product focuses more on optimization, efficiency, differentiation, and economics."),

    ("9. Decline / Renewal",
     "The product may be repositioned, redesigned, replaced, merged, or retired.")
]

for stage, description in lifecycle:
    print(f"\n{stage}")
    print(f"    {description}")


# ======================================================================
# SECTION 31
# ======================================================================

section(31, "Product Lifecycle Priorities")

print("""
EARLY STAGE

    Problem validation
    Customer understanding
    Value proposition
    MVP
    Risk reduction
    Learning speed


GROWTH STAGE

    Acquisition
    Activation
    Retention
    Product-market fit
    Scale
    Experimentation


MATURITY STAGE

    Efficiency
    Monetization
    Differentiation
    Segmentation
    Defensibility
    Platform leverage


DECLINE STAGE

    Cost management
    Customer migration
    Repositioning
    Sunset planning
    Replacement
    Legacy management


The PM's job changes as the product changes.
""")


# ======================================================================
# SECTION 32
# ======================================================================

section(32, "Product-Market Fit")

explain(
    "PRODUCT-MARKET FIT",
    "A condition where there is strong evidence that a product satisfies "
    "an important market need for a sufficiently valuable customer segment."
)

print("""
Possible evidence includes:

    Strong retention
    Repeat usage
    Organic growth
    Referrals
    Willingness to pay
    Customer pull
    Strong engagement
    Reduced dependence on artificial incentives


Important:

    A product launch is not automatically product-market fit.

    A large number of downloads is not automatically product-market fit.

    One successful customer is not automatically product-market fit.


Product-market fit is an evidence-based judgment.
""")


# ======================================================================
# SECTION 33
# ======================================================================

section(33, "Product Metrics")

metrics = {
    "Acquisition":
        "How users discover and enter the product.",

    "Activation":
        "Whether users reach an initial value moment.",

    "Engagement":
        "How users interact with the product.",

    "Retention":
        "Whether users continue receiving value over time.",

    "Conversion":
        "Whether users complete a desired action.",

    "Revenue":
        "Economic value generated.",

    "Churn":
        "Users or revenue lost.",

    "Quality":
        "Reliability, errors, defects, latency, support problems, etc.",

    "North Star Metric":
        "A high-level metric intended to represent sustained product value."
}

for metric, definition in metrics.items():
    explain(metric, definition)


print("""
Example:

An online learning product launches a new onboarding flow.

BAD SUCCESS METRIC:

    "We launched onboarding."

This measures output.

BETTER:

    "Onboarding completion increased."

This measures outcome.

EVEN BETTER:

    "Onboarding completion increased from 40% to 55% while early churn
     and support contacts remained stable."

This combines outcome and guardrails.
""")


# ======================================================================
# SECTION 34
# ======================================================================

section(34, "Leading vs Lagging Indicators")

explain(
    "LEADING INDICATOR",
    "A signal that may provide early evidence about future performance."
)

explain(
    "LAGGING INDICATOR",
    "A measure that reflects an outcome after it has occurred."
)

print("""
Example:

Goal:
    Improve long-term retention.

Potential leading indicators:

    Successful onboarding
    First-value completion
    Early engagement

Lagging indicator:

    90-day retention

The PM should understand how these metrics relate rather than treating
every metric as equally meaningful.
""")


# ======================================================================
# SECTION 35
# ======================================================================

section(35, "Cross-Functional Product Team")

print("""
A common modern product team includes:

    Product Manager
    Product Designer
    Engineers
    Engineering Lead
    Data / Analytics
    Other specialists as needed


PRODUCT MANAGER

    Customer context
    Business context
    Prioritization
    Product decisions
    Outcomes


DESIGNER

    User experience
    Interaction
    Usability
    Visual and behavioral design


ENGINEERING

    Technical feasibility
    Architecture
    Implementation
    Reliability
    Technical risk


DATA / ANALYTICS

    Measurement
    Analysis
    Experimentation
    Behavioral evidence
""")


print("""
A weak operating model:

    PM thinks
       ↓
    Designer receives requirements
       ↓
    Engineer receives design
       ↓
    Product ships


A stronger model:

    PM + Design + Engineering
              |
              v
       Shared Problem
              |
              v
         Exploration
              |
              v
       Shared Solution
              |
              v
          Execution
              |
              v
           Learning
""")


# ======================================================================
# SECTION 36
# ======================================================================

section(36, "Leadership Without Authority")

print("""
Product Managers frequently need to influence people they do not manage.

The PM may not be the manager of:

    Engineers
    Designers
    Marketing
    Sales
    Legal
    Operations


Yet the PM must align them around product decisions.

This requires:

    Clear communication
    Credibility
    Evidence
    Empathy
    Negotiation
    Structured reasoning
    Relationship building
    Consistency
    Decision clarity


Leadership in Product Management is often:

    INFLUENCE WITHOUT DIRECT AUTHORITY
""")


# ======================================================================
# SECTION 37
# ======================================================================

section(37, "Stakeholder Management")

print("""
Stakeholders may include:

    Executives
    Sales
    Marketing
    Customer Support
    Finance
    Legal
    Compliance
    Operations
    Engineering
    Design
    Customers
    Partners


Stakeholder management does NOT mean:

    Make everyone happy.

It means:

    Understand interests.
    Understand incentives.
    Communicate clearly.
    Manage expectations.
    Explain decisions.
    Make trade-offs visible.
    Escalate real conflicts.
""")


subsection("Input vs Decision Authority")

print("""
A stakeholder may provide:

    INPUT

without necessarily having:

    FINAL DECISION AUTHORITY

For example:

    Sales can provide customer demand signals.

    Engineering can provide technical constraints.

    Legal can identify regulatory risk.

    Finance can identify economic constraints.

The PM integrates these inputs into product decisions within the
organization's governance model.
""")


# ======================================================================
# SECTION 38
# ======================================================================

section(38, "Product Documentation")

print("""
Useful Product Management documents include:

    Product Vision
    Product Strategy
    Product Brief
    Problem Statement
    User Personas
    User Journey
    Opportunity Assessment
    PRD
    User Stories
    Acceptance Criteria
    Roadmap
    Experiment Plan
    Launch Plan
    Metrics Definition
    Decision Log
    Research Repository
    Post-Launch Review
""")


subsection("Why Documentation Matters")

print("""
Documentation creates organizational memory.

Without documentation:

    Decisions are forgotten.
    Context disappears.
    New employees repeat old discussions.
    Stakeholders interpret decisions differently.
    Teams lose track of assumptions.


Good documentation answers:

    What are we doing?
    Why are we doing it?
    What evidence supports it?
    What did we decide?
    What remains uncertain?
    Who owns the next step?
""")


# ======================================================================
# SECTION 39
# ======================================================================

section(39, "Notion for Product Management")

print("""
Notion can be used as a product-management knowledge workspace.

Example structure:

    PRODUCT HOME
    |
    +-- Vision
    |
    +-- Strategy
    |
    +-- Goals
    |
    +-- Roadmap
    |
    +-- Discovery
    |      |
    |      +-- Interviews
    |      +-- Research
    |      +-- Opportunities
    |
    +-- Delivery
    |      |
    |      +-- Requirements
    |      +-- Decisions
    |      +-- Launches
    |
    +-- Metrics
    |
    +-- Meeting Notes
""")


subsection("Useful Notion Databases")

print("""
Opportunity Database:

    Opportunity
    Customer Segment
    Problem
    Evidence
    Impact
    Confidence
    Effort
    Strategic Alignment
    Status
    Owner
    Decision
    Date


Decision Database:

    Decision
    Context
    Options
    Decision
    Rationale
    Evidence
    Owner
    Date
    Review Date


Research Database:

    Research Question
    Method
    Customer Segment
    Insight
    Evidence
    Date
    Source
""")


print("""
Important:

    NOTION IS A TOOL.

The real PM skill is:

    Structuring information
    Creating clarity
    Recording decisions
    Connecting evidence
    Enabling collaboration

Knowing Notion buttons does not make someone a PM.
""")


# ======================================================================
# SECTION 40
# ======================================================================

section(40, "Google Docs for Product Management")

print("""
Google Docs is useful for collaborative narrative documentation.

Good use cases include:

    Product Briefs
    PRDs
    Strategy Documents
    Research Summaries
    Launch Plans
    Decision Documents
    Executive Proposals
    Meeting Notes
""")


subsection("Good Documentation Practices")

best_practices = [
    "Start with the problem.",
    "State the target user.",
    "State the goal.",
    "Separate facts from assumptions.",
    "Link supporting evidence.",
    "Define important terms.",
    "Document decisions.",
    "Identify open questions.",
    "Use comments for unresolved discussions.",
    "Keep the document readable.",
]

for practice in best_practices:
    bullet(practice)


# ======================================================================
# SECTION 41
# ======================================================================

section(41, "Advanced Product Mental Models")

mental_models = [
    "Think in outcomes, not outputs.",
    "Start with the problem, not the requested feature.",
    "Treat assumptions as risks.",
    "Test high-risk assumptions early.",
    "Optimize learning speed when uncertainty is high.",
    "Prefer reversible decisions when uncertainty is high.",
    "Be careful with irreversible decisions.",
    "Prioritize based on opportunity cost.",
    "Consider second-order effects.",
    "Look at the entire customer journey.",
    "Combine qualitative and quantitative evidence.",
    "Understand incentives before interpreting behavior.",
    "Measure customer value rather than activity alone.",
    "Do not confuse correlation with causation.",
    "Do not optimize one metric while damaging the system.",
]

for model in mental_models:
    bullet(model)


# ======================================================================
# SECTION 42
# ======================================================================

section(42, "Second-Order Thinking")

print("""
Example:

Decision:

    Increase push notifications.

First-order effect:

    More sessions.

A weak PM might conclude:

    "The feature worked."


A stronger PM asks:

    What happens next?

Possible second-order effects:

    Notification fatigue
    Reduced trust
    Notification disabling
    Uninstalls
    Lower long-term retention


Therefore:

    Immediate metric improvement
        does NOT necessarily mean
    long-term product success.
""")


# ======================================================================
# SECTION 43
# ======================================================================

section(43, "Reversible vs Irreversible Decisions")

print("""
Some decisions are easy to reverse.

Examples:

    Button copy
    Minor UI change
    Small experiment


Some decisions are harder to reverse.

Examples:

    Entering a new country
    Major architecture migration
    Acquiring another company
    Signing a major long-term contract
    Launching a highly regulated product


When uncertainty is high:

    Prefer learning quickly through reversible decisions where practical.

When decisions are difficult to reverse:

    Gather stronger evidence.
    Analyze risks.
    Involve appropriate stakeholders.
    Consider second-order consequences.
""")


# ======================================================================
# SECTION 44
# ======================================================================

section(44, "Product Decision Framework")

print("""
A practical product decision process:

    STEP 1
        Define the decision.

    STEP 2
        Define the desired outcome.

    STEP 3
        Gather relevant evidence.

    STEP 4
        Identify assumptions.

    STEP 5
        Identify constraints.

    STEP 6
        Generate realistic options.

    STEP 7
        Compare trade-offs.

    STEP 8
        Make the decision.

    STEP 9
        Communicate the rationale.

    STEP 10
        Define how success will be evaluated.

    STEP 11
        Revisit the decision when new evidence appears.
""")


subsection("Decision Log Template")

print("""
    Decision:
    Date:
    Context:
    Problem:
    Options:
    Chosen Option:
    Why:
    Evidence:
    Risks:
    Assumptions:
    Owner:
    Review Date:
""")


# ======================================================================
# SECTION 45
# ======================================================================

section(45, "Product Operating Rhythm")

print("""
A product organization may have different operating cadences.

DAILY:

    Unblock decisions
    Answer questions
    Monitor critical issues


WEEKLY:

    Product review
    Discovery review
    Delivery review
    Metric review


MONTHLY:

    Goal review
    Customer insights
    Roadmap review
    Business performance


QUARTERLY:

    Strategy
    Objectives
    Major bets
    Resource allocation


The exact cadence varies.

The important principle is recurring:

    Learning
    Prioritization
    Decision-making
    Communication
""")


# ======================================================================
# SECTION 46
# ======================================================================

section(46, "Product Management Skill Stack")

skills = [
    "Customer Research",
    "Product Discovery",
    "Problem Framing",
    "Product Strategy",
    "Prioritization",
    "Roadmapping",
    "Requirements",
    "UX Collaboration",
    "Technical Literacy",
    "Data Literacy",
    "Product Analytics",
    "Experimentation",
    "Communication",
    "Stakeholder Management",
    "Negotiation",
    "Decision Making",
    "Business Understanding",
    "Market Analysis",
    "Leadership Without Authority",
    "Execution Management",
]

for skill in skills:
    bullet(skill)


print("""
You do not need to become the world's best specialist in every domain.

You need sufficient literacy to:

    Ask good questions.
    Understand constraints.
    Challenge assumptions.
    Make informed decisions.
    Communicate clearly.
    Work effectively with specialists.
""")


# ======================================================================
# SECTION 47
# ======================================================================

section(47, "Product Management Tool Stack")

tool_stack = {
    "Documentation": [
        "Notion",
        "Google Docs"
    ],

    "Planning": [
        "Notion",
        "Spreadsheets",
        "Roadmap tools"
    ],

    "Design": [
        "Figma or equivalent"
    ],

    "Delivery": [
        "Jira or equivalent"
    ],

    "Analytics": [
        "Product analytics platforms",
        "SQL",
        "Excel",
        "Google Sheets"
    ],

    "Research": [
        "Forms",
        "Survey tools",
        "Interview repositories"
    ],

    "Communication": [
        "Email",
        "Chat",
        "Video conferencing"
    ]
}

for category, tools in tool_stack.items():
    print(f"\n{category}")

    for tool in tools:
        bullet(tool, 1)


print("""
Remember:

    TOOL ≠ SKILL

The ability to create a Kanban board is not Product Management.

The skill is understanding:

    What belongs on the board?
    Why?
    In what order?
    What outcome is expected?
    What decision depends on it?
""")


# ======================================================================
# SECTION 48
# ======================================================================

section(48, "Mini Case Study - Banking Onboarding")

print("""
CASE:

A digital bank notices that many new applicants start onboarding
but fail to complete identity verification.


STEP 1 - OBSERVE

Analyze:

    Signup funnel
    Verification funnel
    Error rates
    Drop-off points


STEP 2 - FORM QUESTIONS

Potential causes:

    Complexity
    Lack of trust
    Technical failure
    Missing documents
    Poor instructions
    Regulatory requirements


STEP 3 - INVESTIGATE

Use:

    Analytics
    Customer interviews
    Usability testing
    Support tickets
    Error logs


STEP 4 - FRAME THE PROBLEM

Example:

    "New users struggle to understand verification requirements,
     creating uncertainty and abandonment."


STEP 5 - FORM HYPOTHESIS

    "Clearer guidance will increase verification completion."


STEP 6 - CONSIDER SOLUTIONS

    A. Rewrite instructions
    B. Add contextual guidance
    C. Add document examples
    D. Add progress indicators
    E. Add human assistance


STEP 7 - PRIORITIZE

Evaluate:

    Impact
    Confidence
    Effort
    Risk
    Regulatory constraints


STEP 8 - BUILD

    Product
    Design
    Engineering
    Compliance
    Operations


STEP 9 - MEASURE

PRIMARY METRIC:

    Verification completion


GUARDRAILS:

    Fraud rate
    Support contacts
    Error rate
    Processing time


STEP 10 - LEARN

If completion increases without harming risk:

    Scale.

If completion does not improve:

    Investigate the next bottleneck.


The complete loop:

    PROBLEM
       ↓
    EVIDENCE
       ↓
    HYPOTHESIS
       ↓
    PRIORITIZATION
       ↓
    SOLUTION
       ↓
    EXECUTION
       ↓
    LAUNCH
       ↓
    MEASUREMENT
       ↓
    LEARNING
""")


# ======================================================================
# SECTION 49
# ======================================================================

section(49, "Product Management Glossary")

glossary = {
    "Product":
        "A solution or offering that creates value.",

    "Product Management":
        "Discipline of guiding product decisions toward customer and business outcomes.",

    "Product Manager":
        "Professional responsible for guiding product direction, decisions, priorities, and outcomes within an organizational context.",

    "User":
        "Person who uses the product.",

    "Customer":
        "Person or organization receiving or purchasing product value.",

    "Buyer":
        "Person responsible for purchasing.",

    "Feature":
        "Specific product capability.",

    "Requirement":
        "Condition or capability the product must satisfy.",

    "Roadmap":
        "Communication and planning view of product direction and priorities.",

    "MVP":
        "Minimum viable product or test designed to generate meaningful learning and value.",

    "Discovery":
        "Learning about problems, opportunities, users, and solution viability.",

    "Delivery":
        "Building, releasing, and operating a chosen solution.",

    "Outcome":
        "Measurable change resulting from product work.",

    "Output":
        "Artifact or capability produced by the team.",

    "Impact":
        "Broader customer or business value created.",

    "Stakeholder":
        "Person or group affected by or influencing the product.",

    "Backlog":
        "Prioritized collection of work.",

    "Experiment":
        "Structured test of an assumption or hypothesis.",

    "Retention":
        "Continuation of product usage or customer value over time.",

    "Churn":
        "Loss of customers, users, or revenue.",

    "Product-Market Fit":
        "Strong evidence that a product satisfies a valuable market need.",

    "North Star Metric":
        "High-level metric intended to represent sustained product value."
}

for term, definition in glossary.items():
    print(f"\n{term}")
    print(f"    {definition}")


# ======================================================================
# SECTION 50
# ======================================================================

section(50, "Knowledge Check")

questions = [
    "What is a product?",
    "Why is a product more than a physical or digital artifact?",
    "What is the difference between a product and a feature?",
    "What is the difference between a product and a project?",
    "Why does Product Management exist?",
    "What does a Product Manager actually do?",
    "What should a Product Manager NOT become?",
    "What is the difference between a user and a customer?",
    "What is the difference between a buyer and a decision maker?",
    "What are the major characteristics of digital products?",
    "What are the major characteristics of physical products?",
    "What are hybrid products?",
    "What is product thinking?",
    "What is the difference between problem-first and feature-first thinking?",
    "What is product discovery?",
    "What is product delivery?",
    "Why are discovery and delivery both important?",
    "What is product value?",
    "What is product vision?",
    "What is product strategy?",
    "What is a product goal?",
    "What is a product roadmap?",
    "What is a requirement?",
    "What is a PRD?",
    "What is a user story?",
    "What are acceptance criteria?",
    "What is an MVP?",
    "What is a product hypothesis?",
    "Why is prioritization important?",
    "What is opportunity cost?",
    "What are common product trade-offs?",
    "What is the product lifecycle?",
    "How does the PM's focus change across lifecycle stages?",
    "What is product-market fit?",
    "What are acquisition and activation?",
    "What is retention?",
    "What is churn?",
    "What is a North Star Metric?",
    "What is the difference between output and outcome?",
    "What is the difference between outcome and impact?",
    "What is cross-functional collaboration?",
    "What does leadership without authority mean?",
    "What is stakeholder management?",
    "How can Notion support Product Management?",
    "How can Google Docs support Product Management?",
    "Why are product tools not the same as product skills?",
    "What is second-order thinking?",
    "What is a reversible decision?",
    "How should a PM make a product decision?",
    "Explain the complete product management loop."
]

for i, q in enumerate(questions, start=1):
    question(i, q)


# ======================================================================
# FINAL SUMMARY
# ======================================================================

title("FINAL DAY 01 SUMMARY")

print("""
The central idea of Product Management is:

    CREATE MEANINGFUL VALUE
    FOR CUSTOMERS AND USERS
    WHILE SUPPORTING BUSINESS OBJECTIVES
    UNDER REAL-WORLD CONSTRAINTS.


A Product Manager constantly connects:

    CUSTOMER
       ↓
    PROBLEM
       ↓
    EVIDENCE
       ↓
    OPPORTUNITY
       ↓
    PRIORITIZATION
       ↓
    PRODUCT DECISION
       ↓
    DESIGN
       ↓
    ENGINEERING
       ↓
    LAUNCH
       ↓
    USER BEHAVIOR
       ↓
    MEASUREMENT
       ↓
    LEARNING
       ↓
    NEXT DECISION


The most important mindset shift is:

    OLD THINKING:

        "What should we build?"

    PRODUCT THINKING:

        "What problem is worth solving,
         for whom,
         why,
         what evidence do we have,
         what outcome do we want,
         and how will we know whether we succeeded?"


Remember these distinctions:

    PRODUCT ≠ FEATURE

    PRODUCT ≠ PROJECT

    OUTPUT ≠ OUTCOME

    USER ≠ CUSTOMER

    ROADMAP ≠ BACKLOG

    MVP ≠ BAD PRODUCT

    DATA ≠ AUTOMATIC ANSWER

    TOOL ≠ PRODUCT MANAGEMENT SKILL


A mature PM thinks in:

    Problems
    Outcomes
    Customers
    Evidence
    Trade-offs
    Priorities
    Strategy
    Experiments
    Decisions
    Learning
""")


# ======================================================================
# LEARNING PROGRESSION
# ======================================================================

title("WHAT TO LEARN NEXT")

print("""
After completing this foundation, the next Product Management topics
should progress in approximately this order:

    1. Customer Discovery

    2. Customer Interviews

    3. User Personas

    4. Customer Segmentation

    5. Jobs-to-be-Done

    6. User Journey Mapping

    7. Problem Statements

    8. Opportunity Identification

    9. Opportunity Solution Trees

    10. Product Vision

    11. Product Strategy

    12. Competitive Analysis

    13. Market Research

    14. Product Goals

    15. OKRs

    16. Product Roadmaps

    17. Prioritization Frameworks

    18. PRDs

    19. User Stories

    20. Acceptance Criteria

    21. UX for Product Managers

    22. Technical Product Management

    23. Product Analytics

    24. SQL for Product Managers

    25. Metrics

    26. Funnels

    27. Cohort Analysis

    28. A/B Testing

    29. Experimentation

    30. Growth Product Management

    31. Retention

    32. Monetization

    33. Product-Market Fit

    34. Go-To-Market

    35. B2B Product Management

    36. Platform Product Management

    37. API Product Management

    38. AI Product Management

    39. Product Operations

    40. Product Leadership


DAY 01 COMPLETE.

""")
