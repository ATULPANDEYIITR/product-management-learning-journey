"""
PRODUCT MANAGER ROLE
====================

Topic:
Product Manager Role: Responsibilities, Ownership, Decision-Making,
Execution, Strategy, Coordination, and Product Thinking

Purpose:
This script is a detailed, practical and academic learning module for
understanding what a Product Manager actually does, how the role operates,
how decisions are made, how ownership works, how strategy connects to
execution, and how product thinking is applied to real situations.

The script intentionally uses explanations, examples, scenarios,
decision frameworks, calculations, simulations, and exercises.

It does not depend on external libraries.
"""

# ============================================================
# 1. INTRODUCTION TO THE PRODUCT MANAGER ROLE
# ============================================================

print("=" * 80)
print("PRODUCT MANAGER ROLE")
print("=" * 80)

print("""
A Product Manager is responsible for helping a team build the right product,
for the right users, at the right time, in a way that creates measurable
business and user value.

The role sits at the intersection of:

    Users
    Business
    Technology
    Design
    Data
    Operations
    Strategy

A Product Manager is not simply a person who writes requirements.

The role involves understanding problems, deciding what matters, defining
outcomes, coordinating people, making trade-offs, managing uncertainty,
communicating decisions, and ensuring that product work contributes to
meaningful outcomes.

A useful way to understand the role is:

    Problem
       |
       v
    Evidence
       |
       v
    Product Decision
       |
       v
    Prioritisation
       |
       v
    Execution
       |
       v
    Measurement
       |
       v
    Learning
       |
       +--------> New Product Decisions

Product management is therefore a continuous decision-making discipline.

The Product Manager does not personally perform every activity.

Instead, the Product Manager creates clarity around:

    What problem are we solving?
    Why does the problem matter?
    Who experiences it?
    What outcome are we trying to create?
    What should we build?
    What should we not build?
    Why should we build it now?
    How will we know whether it worked?
""")

# ============================================================
# 2. WHAT IS A PRODUCT?
# ============================================================

print("\n" + "=" * 80)
print("2. UNDERSTANDING THE PRODUCT")
print("=" * 80)

print("""
A product is not merely a software application.

A product can be:

    - Mobile application
    - Banking service
    - SaaS platform
    - E-commerce marketplace
    - Physical device
    - Internal enterprise system
    - Financial service
    - Educational platform
    - Healthcare service
    - Transportation service
    - Data platform
    - API
    - Consumer subscription

A product exists because it provides some form of value.

A simplified product equation is:

    Product Value = User Value + Business Value

A product can fail in several ways.

Case 1:
Users like it, but the business cannot economically sustain it.

Case 2:
The business benefits from it, but users find it difficult or useless.

Case 3:
The product solves a real problem, but the organisation cannot execute
the solution effectively.

Case 4:
The product works technically, but nobody needs it.

Therefore, product management must balance several dimensions.
""")

# ============================================================
# 3. PRODUCT MANAGEMENT VS PROJECT MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("3. PRODUCT MANAGEMENT VS PROJECT MANAGEMENT")
print("=" * 80)

print("""
Product management and project management are related but different.

PRODUCT MANAGEMENT focuses primarily on:

    Problem
    User
    Value
    Product direction
    Priorities
    Outcomes
    Strategy
    Product decisions

PROJECT MANAGEMENT focuses primarily on:

    Scope
    Schedule
    Dependencies
    Resources
    Risks
    Delivery coordination
    Project execution

A Product Manager may ask:

    "Should we build this?"

A Project Manager may ask:

    "How can we deliver this successfully within the agreed constraints?"

Example:

A company wants to introduce a digital loan application.

Product Manager:

    - Understands customer problems
    - Studies competitors
    - Defines target customers
    - Identifies important friction
    - Determines product requirements
    - Prioritises capabilities
    - Defines success metrics

Project Manager:

    - Tracks project timeline
    - Coordinates project dependencies
    - Tracks delivery risks
    - Organises project milestones
    - Monitors project status

There can be overlap, especially in smaller organisations.

A Product Manager is fundamentally accountable for product outcomes,
while a Project Manager is fundamentally accountable for project delivery.
""")

# ============================================================
# 4. PRODUCT MANAGER VS PRODUCT OWNER
# ============================================================

print("\n" + "=" * 80)
print("4. PRODUCT MANAGER VS PRODUCT OWNER")
print("=" * 80)

print("""
The terms Product Manager and Product Owner are sometimes used
interchangeably, but they originate from different contexts.

A Product Owner in Scrum typically focuses heavily on:

    - Product Backlog
    - Backlog ordering
    - Sprint-related product decisions
    - Clarifying requirements
    - Acceptance criteria
    - Maximising product value

A Product Manager usually has a broader organisational scope:

    - Product strategy
    - Market understanding
    - Customer research
    - Product vision
    - Roadmap
    - Business outcomes
    - Product metrics
    - Cross-functional alignment
    - Competitive positioning

In some organisations, one person performs both roles.

The important distinction is not the job title.

The important distinction is the scope of responsibility.
""")

# ============================================================
# 5. CORE RESPONSIBILITIES OF A PRODUCT MANAGER
# ============================================================

print("\n" + "=" * 80)
print("5. CORE RESPONSIBILITIES")
print("=" * 80)

responsibilities = [
    "Understand users and their problems",
    "Understand business objectives",
    "Define product direction",
    "Identify and validate opportunities",
    "Convert problems into product requirements",
    "Prioritise product work",
    "Create alignment across functions",
    "Make product decisions",
    "Coordinate execution",
    "Manage trade-offs",
    "Define measurable outcomes",
    "Monitor product performance",
    "Communicate product decisions",
    "Manage stakeholder expectations",
    "Learn from product results",
]

for number, responsibility in enumerate(responsibilities, start=1):
    print(f"{number:02d}. {responsibility}")

print("""
These responsibilities are connected.

A Product Manager cannot prioritise effectively without understanding
the problem.

The Product Manager cannot define strategy without understanding users,
business objectives and market conditions.

The Product Manager cannot execute effectively without alignment.

The Product Manager cannot determine whether execution was successful
without measurable outcomes.

Therefore:

    Research -> Strategy -> Prioritisation -> Execution -> Measurement
        ^                                                   |
        |___________________________________________________|

This feedback loop is central to product management.
""")

# ============================================================
# 6. OWNERSHIP
# ============================================================

print("\n" + "=" * 80)
print("6. PRODUCT OWNERSHIP")
print("=" * 80)

print("""
Ownership is one of the most important concepts in product management.

Ownership does NOT mean:

    "I personally do everything."

Ownership means:

    "I am accountable for creating clarity, making appropriate decisions,
     coordinating the relevant people, and driving the product toward
     the desired outcome."

A Product Manager may not:

    - Write production code
    - Design every interface
    - Conduct every research interview
    - Write every SQL query
    - Run every marketing campaign
    - Test every build

Yet the Product Manager can still own the product outcome.

Consider a product team:

    Product Manager
          |
    +-----+-----+---------+
    |           |         |
  Design      Engineering Data
    |           |         |
    +-----------+---------+
                |
             Product

Ownership requires the Product Manager to maintain clarity across these
different functions.

A strong Product Manager asks:

    What are we trying to achieve?
    Who owns each decision?
    What information is missing?
    What is blocking progress?
    What trade-off has to be made?
    What is the consequence of delaying the decision?

Ownership is therefore closely connected to accountability.
""")

# ============================================================
# 7. ACCOUNTABILITY VS RESPONSIBILITY
# ============================================================

print("\n" + "=" * 80)
print("7. ACCOUNTABILITY VS RESPONSIBILITY")
print("=" * 80)

print("""
Responsibility means having a duty to perform a task.

Accountability means being answerable for the outcome.

Example:

An engineer may be responsible for implementing an API.

The Product Manager may be accountable for ensuring that the API
supports the intended product outcome.

The distinction is important.

A Product Manager should not take over specialised work.

Instead, the Product Manager should ensure that:

    - The problem is clear.
    - The requirement is clear.
    - The expected outcome is clear.
    - The right people are involved.
    - Dependencies are known.
    - Decisions are made.
    - Progress is visible.
    - Results are measured.

Ownership therefore requires influence without necessarily having
formal authority over every person involved.
""")

# ============================================================
# 8. PRODUCT MANAGER AS A DECISION MAKER
# ============================================================

print("\n" + "=" * 80)
print("8. DECISION-MAKING")
print("=" * 80)

print("""
Product management involves a large number of decisions.

Examples include:

    - Which customer problem should we solve?
    - Which market should we enter?
    - Which feature should be prioritised?
    - Which feature should be rejected?
    - Should we build or buy?
    - Should we launch now or wait?
    - Should we optimise conversion or retention?
    - Should we reduce scope?
    - Should we invest in technical debt?
    - Should we change the onboarding flow?
    - Should we increase price?
    - Should we remove a feature?

A good product decision is not necessarily a decision that guarantees
a positive result.

A good decision is one that:

    - Uses the best available evidence.
    - Clearly defines assumptions.
    - Considers relevant constraints.
    - Identifies trade-offs.
    - Has a clear rationale.
    - Is made at an appropriate speed.

Product management happens under uncertainty.

Therefore, waiting for perfect information can itself become a bad decision.
""")

# ============================================================
# 9. DECISION QUALITY
# ============================================================

print("\n" + "=" * 80)
print("9. DECISION QUALITY")
print("=" * 80)

def decision_quality(evidence, clarity, reversibility, urgency):
    """
    Simple educational model.

    Each input is scored from 1 to 10.
    """
    score = (evidence + clarity + reversibility + urgency) / 4
    return round(score, 2)


score = decision_quality(
    evidence=8,
    clarity=9,
    reversibility=7,
    urgency=8
)

print(f"Illustrative decision quality score: {score}/10")

print("""
This numerical model is not a formal industry standard.

It is a way to think about the dimensions of a decision.

Important dimensions include:

EVIDENCE
--------
How much reliable information supports the decision?

CLARITY
-------
How clearly is the problem and desired outcome understood?

REVERSIBILITY
-------------
Can the decision easily be changed?

URGENCY
-------
How costly is delay?

A highly reversible decision can often be made quickly.

An irreversible decision deserves more careful analysis.

For example:

Changing the order of two buttons is relatively reversible.

Changing a company's pricing model may be much harder to reverse.

The Product Manager should therefore match the amount of analysis
to the consequence and reversibility of the decision.
""")

# ============================================================
# 10. REVERSIBLE AND IRREVERSIBLE DECISIONS
# ============================================================

print("\n" + "=" * 80)
print("10. REVERSIBLE VS IRREVERSIBLE DECISIONS")
print("=" * 80)

decisions = {
    "Change UI copy": "Mostly reversible",
    "Change button placement": "Mostly reversible",
    "Run an A/B test": "Highly reversible",
    "Change pricing permanently": "Less reversible",
    "Enter a new country": "Less reversible",
    "Acquire another company": "Highly difficult to reverse",
}

for decision, classification in decisions.items():
    print(f"{decision:<35} -> {classification}")

print("""
The key principle is:

    High reversibility + low risk
        -> faster decision

    Low reversibility + high risk
        -> deeper analysis

This prevents two common problems:

1. Over-analysis of small decisions.
2. Under-analysis of major decisions.
""")

# ============================================================
# 11. PRODUCT STRATEGY
# ============================================================

print("\n" + "=" * 80)
print("11. PRODUCT STRATEGY")
print("=" * 80)

print("""
Product strategy explains how the product intends to create value
and achieve important objectives.

A strategy usually connects:

    Company Goal
        |
        v
    Product Goal
        |
        v
    Target Customer
        |
        v
    Important Problem
        |
        v
    Product Approach
        |
        v
    Expected Outcome
        |
        v
    Measurement

Strategy is not simply a list of features.

Consider two statements.

Statement A:

    "We will build dark mode, AI search, notifications and dashboards."

This is a feature list.

Statement B:

    "We will improve retention among professional users by reducing
     the effort required to complete recurring workflows."

This describes a strategic outcome.

Features are possible mechanisms.

Strategy defines direction and intended value.
""")

# ============================================================
# 12. VISION, STRATEGY, ROADMAP AND BACKLOG
# ============================================================

print("\n" + "=" * 80)
print("12. VISION, STRATEGY, ROADMAP AND BACKLOG")
print("=" * 80)

print("""
These terms are related but should not be treated as identical.

VISION
------
A description of the desired future state.

Example:

    "Make personal financial management simple for first-time investors."

STRATEGY
--------
The approach used to move toward the vision.

Example:

    "Focus first on simplified investment discovery and transparent
     portfolio education for young professionals."

ROADMAP
-------
A communication and planning representation of important product
initiatives and expected sequencing.

Example:

    Q1: Improve onboarding
    Q2: Improve investment discovery
    Q3: Introduce portfolio insights

BACKLOG
-------
A more detailed collection of product work items.

Example:

    - Add risk-profile question
    - Create onboarding validation
    - Add portfolio calculation API
    - Create investment comparison screen

The hierarchy can be represented as:

    Vision
       |
       v
    Strategy
       |
       v
    Strategic Initiatives
       |
       v
    Roadmap
       |
       v
    Product Backlog
       |
       v
    User Stories / Tasks
       |
       v
    Implementation
""")

# ============================================================
# 13. PRODUCT THINKING
# ============================================================

print("\n" + "=" * 80)
print("13. PRODUCT THINKING")
print("=" * 80)

print("""
Product thinking means approaching a situation through the lens of
problems, users, value, evidence, constraints and outcomes.

A feature-oriented mindset asks:

    "What feature should we build?"

A product-thinking mindset asks:

    "What problem exists, for whom, why does it matter, and what is the
     smallest effective intervention that could improve the outcome?"

Example:

Suppose users abandon a loan application.

A weak response:

    "Add a progress bar."

A product-thinking response:

    "Why are users abandoning the application?"

Possible reasons:

    - Application is too long.
    - Users do not have required documents.
    - Eligibility is unclear.
    - Users do not trust the company.
    - Form validation is confusing.
    - Page performance is poor.
    - Interest rate information appears too late.

The progress bar may or may not solve the actual problem.

Product thinking starts with diagnosis rather than solution attachment.
""")

# ============================================================
# 14. PROBLEM SPACE AND SOLUTION SPACE
# ============================================================

print("\n" + "=" * 80)
print("14. PROBLEM SPACE VS SOLUTION SPACE")
print("=" * 80)

print("""
PROBLEM SPACE
-------------

Questions include:

    Who has the problem?
    What exactly is the problem?
    How frequently does it occur?
    How severe is it?
    What causes it?
    What happens if it remains unsolved?
    What alternatives do users currently use?

SOLUTION SPACE
--------------

Questions include:

    What can we build?
    What experiment can we run?
    What design could solve the issue?
    What technology is required?
    What is feasible within our constraints?

A common product mistake is entering solution space too early.

For example:

    Stakeholder:
    "We need a mobile app."

A Product Manager should not immediately create an app specification.

Instead:

    Why do we need it?
    Which customer problem does it solve?
    What evidence supports the problem?
    What alternative solutions exist?
    Is a mobile app actually the best solution?
""")

# ============================================================
# 15. CUSTOMER PROBLEM DEFINITION
# ============================================================

print("\n" + "=" * 80)
print("15. DEFINING A CUSTOMER PROBLEM")
print("=" * 80)

def define_problem(user, situation, difficulty, consequence):
    return f"""
USER:
{user}

SITUATION:
{situation}

DIFFICULTY:
{difficulty}

CONSEQUENCE:
{consequence}
"""

problem = define_problem(
    user="A first-time online investor",
    situation="When comparing investment options",
    difficulty="has difficulty understanding risk and expected return",
    consequence="which creates uncertainty and causes abandonment"
)

print(problem)

print("""
A good problem statement avoids prescribing a solution.

Poor:

    "Users need a better comparison dashboard."

Better:

    "First-time investors struggle to compare investment options
     because risk and return information is difficult to interpret."

The second statement leaves room for different solutions.
""")

# ============================================================
# 16. CUSTOMER DISCOVERY
# ============================================================

print("\n" + "=" * 80)
print("16. CUSTOMER DISCOVERY")
print("=" * 80)

print("""
Customer discovery is the process of understanding users, their needs,
behaviour, context, problems and alternatives.

Common methods include:

    - User interviews
    - Surveys
    - Usability testing
    - Customer support analysis
    - Product analytics
    - Field observation
    - Competitive analysis
    - Review analysis
    - Sales feedback
    - Search behaviour analysis

A Product Manager should distinguish between:

    What users SAY
    What users DO
    What users NEED

These are not always identical.

Example:

A user says:

    "I want more notifications."

Actual behaviour may show:

    Users ignore existing notifications.

The underlying need might actually be:

    "Help me remember important events."

The correct product response may not be "send more notifications."
""")

# ============================================================
# 17. USER INTERVIEW THINKING
# ============================================================

print("\n" + "=" * 80)
print("17. USER INTERVIEW QUESTIONS")
print("=" * 80)

questions = [
    "Tell me about the last time you performed this task.",
    "What were you trying to accomplish?",
    "What happened?",
    "What was difficult?",
    "What did you do when that happened?",
    "What alternatives did you consider?",
    "How frequently does this happen?",
    "What happens if you cannot complete it?",
    "What tools do you currently use?",
    "What is frustrating about the current process?",
]

for question in questions:
    print("-", question)

print("""
Questions about actual past behaviour are generally more useful than
questions asking users to predict hypothetical future behaviour.

For example:

    "Would you use this feature?"

is weaker than:

    "How do you currently solve this problem?"

This is because people can express positive opinions about an idea
without actually using it.
""")

# ============================================================
# 18. PRODUCT DISCOVERY AND DELIVERY
# ============================================================

print("\n" + "=" * 80)
print("18. DISCOVERY AND DELIVERY")
print("=" * 80)

print("""
Product work can broadly be divided into two connected activities.

DISCOVERY
---------

Understanding:

    - Problems
    - Users
    - Opportunities
    - Assumptions
    - Potential solutions
    - Risks
    - Evidence

DELIVERY
--------

Turning a validated direction into a working product.

This includes:

    - Requirements
    - Design
    - Engineering
    - Testing
    - Release
    - Monitoring

A simplified model:

    Discover
       |
       v
    Define
       |
       v
    Design
       |
       v
    Build
       |
       v
    Launch
       |
       v
    Measure
       |
       v
    Learn

This is not necessarily a strictly linear process.

Learning from delivery can create new discovery questions.
""")

# ============================================================
# 19. REQUIREMENTS
# ============================================================

print("\n" + "=" * 80)
print("19. PRODUCT REQUIREMENTS")
print("=" * 80)

print("""
A requirement explains what the product needs to support.

Requirements can be:

FUNCTIONAL
----------

What the system should do.

Example:

    "The user should be able to reset their password using a registered
     email address."

NON-FUNCTIONAL
--------------

How the system should behave.

Examples:

    - Performance
    - Security
    - Availability
    - Scalability
    - Accessibility

BUSINESS REQUIREMENTS
---------------------

What business objective must be supported.

Example:

    "Reduce customer support requests related to password recovery."

USER REQUIREMENTS
-----------------

What the user needs to accomplish.

Example:

    "A user needs to regain account access without contacting support."

A strong Product Manager connects these layers.
""")

# ============================================================
# 20. USER STORIES
# ============================================================

print("\n" + "=" * 80)
print("20. USER STORIES")
print("=" * 80)

print("""
A common user-story structure is:

    As a [type of user],
    I want [capability],
    so that [benefit].

Example:

    As a customer,
    I want to save my preferred payment method,
    so that I do not have to enter payment information repeatedly.

The value of a user story is not its grammatical format.

Its value comes from making user intent and expected value explicit.

A user story should be accompanied by sufficient context and
acceptance criteria.
""")

# ============================================================
# 21. ACCEPTANCE CRITERIA
# ============================================================

print("\n" + "=" * 80)
print("21. ACCEPTANCE CRITERIA")
print("=" * 80)

print("""
Acceptance criteria define conditions that must be satisfied
for a requirement to be considered complete.

Example:

Feature:
Password reset.

Acceptance criteria:

    1. User enters registered email.
    2. System validates whether the account exists.
    3. Reset instructions are sent through the approved channel.
    4. Reset link expires after the defined period.
    5. User can create a valid new password.
    6. Invalid or expired links cannot reset the password.

Acceptance criteria reduce ambiguity between Product, Design,
Engineering and QA.
""")

# ============================================================
# 22. PRIORITISATION
# ============================================================

print("\n" + "=" * 80)
print("22. PRODUCT PRIORITISATION")
print("=" * 80)

print("""
There are usually more potential product initiatives than available
time, people or money.

Prioritisation answers:

    What should we do first?

    What should we do later?

    What should we not do?

A Product Manager should not prioritise based solely on:

    "The loudest stakeholder."

Prioritisation should consider factors such as:

    - Customer impact
    - Business impact
    - Strategic alignment
    - Confidence
    - Effort
    - Risk
    - Dependencies
    - Time sensitivity
""")

# ============================================================
# 23. RICE FRAMEWORK
# ============================================================

print("\n" + "=" * 80)
print("23. RICE PRIORITISATION")
print("=" * 80)

print("""
RICE is a prioritisation framework using:

    Reach
    Impact
    Confidence
    Effort

Formula:

    RICE Score = (Reach * Impact * Confidence) / Effort

Confidence is often represented as a decimal.

Example:
    Reach = 10,000 users
    Impact = 2
    Confidence = 0.8
    Effort = 20 person-weeks

Score:
    (10,000 * 2 * 0.8) / 20
""")

reach = 10000
impact = 2
confidence = 0.8
effort = 20

rice_score = (reach * impact * confidence) / effort

print(f"RICE score = {rice_score}")

print("""
RICE does not produce objective truth.

It creates a structured basis for discussion.

The assumptions behind the numbers are often more important than
the resulting score.
""")

# ============================================================
# 24. VALUE VS EFFORT
# ============================================================

print("\n" + "=" * 80)
print("24. VALUE VS EFFORT")
print("=" * 80)

initiatives = [
    ("Improve onboarding", 9, 5),
    ("New reporting dashboard", 7, 8),
    ("Small UI improvement", 4, 2),
    ("Major platform rewrite", 8, 10),
]

print(f"{'Initiative':<30}{'Value':<10}{'Effort':<10}")

for name, value, effort in initiatives:
    print(f"{name:<30}{value:<10}{effort:<10}")

print("""
A high-value, low-effort initiative often deserves attention.

A low-value, high-effort initiative usually deserves scrutiny.

But prioritisation should never become:

    "Always do easy things."

Strategic initiatives can be difficult and still deserve investment.

The correct question is:

    "Is the expected value worth the cost, risk and opportunity cost?"
""")

# ============================================================
# 25. OPPORTUNITY COST
# ============================================================

print("\n" + "=" * 80)
print("25. OPPORTUNITY COST")
print("=" * 80)

print("""
Every product decision consumes limited resources.

If a team spends three months building Feature A,
it cannot spend those same three months building Feature B.

Therefore:

    Cost of a decision
    =
    Direct cost
    +
    Opportunity cost

Example:

Feature A:
    Expected revenue impact = $500,000

Feature B:
    Expected revenue impact = $800,000

Choosing Feature A may mean giving up some of the potential value
of Feature B.

This is why Product Managers must think in terms of relative priority,
not isolated feature value.
""")

# ============================================================
# 26. EXECUTION
# ============================================================

print("\n" + "=" * 80)
print("26. PRODUCT EXECUTION")
print("=" * 80)

print("""
Execution is the process of turning a product decision into a working
outcome.

Product execution commonly involves:

    1. Define objective.
    2. Clarify requirements.
    3. Identify dependencies.
    4. Align Design and Engineering.
    5. Break work into manageable pieces.
    6. Resolve ambiguity.
    7. Track progress.
    8. Manage scope.
    9. Address risks.
    10. Test.
    11. Launch.
    12. Measure results.

The Product Manager's execution role is primarily about maintaining
clarity and momentum.

A Product Manager should continuously know:

    What are we building?
    Why are we building it?
    What is currently blocking us?
    What decisions are pending?
    What changed?
    What risks emerged?
    What is the expected outcome?
""")

# ============================================================
# 27. SCOPE MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("27. SCOPE MANAGEMENT")
print("=" * 80)

print("""
Scope describes what is included in a product initiative.

Scope creep occurs when additional requirements continuously enter
a project without corresponding adjustments to time, resources or
expected outcomes.

Example:

Original scope:

    Login
    Profile
    Payment

Then:

    Add social login
    Add biometric login
    Add loyalty points
    Add referrals
    Add analytics dashboard
    Add multi-language support

If everything is added without changing resources or timeline,
execution risk increases.

A Product Manager should ask:

    What problem does this addition solve?
    Is it required for the outcome?
    What will we delay if we include it?
    Can it be postponed?
    Does it change the original product hypothesis?
""")

# ============================================================
# 28. TRADE-OFFS
# ============================================================

print("\n" + "=" * 80)
print("28. PRODUCT TRADE-OFFS")
print("=" * 80)

print("""
Product management is largely a discipline of trade-offs.

Common trade-offs include:

    Speed vs quality
    Scope vs timeline
    Short-term revenue vs long-term retention
    User experience vs operational cost
    Customisation vs simplicity
    Innovation vs reliability
    Growth vs profitability
    Feature richness vs usability
    Build vs buy

Example:

A team has two weeks to launch.

Option A:
    Deliver five features with moderate quality.

Option B:
    Deliver two important features with high quality.

The correct decision depends on:

    - Objective
    - User expectations
    - Risk
    - Business importance
    - Technical constraints
    - Cost of failure

There is no universal rule that Option A or B is always correct.
""")

# ============================================================
# 29. STAKEHOLDER MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("29. STAKEHOLDER MANAGEMENT")
print("=" * 80)

print("""
Product Managers work with stakeholders such as:

    - Executives
    - Engineering leaders
    - Designers
    - Sales
    - Marketing
    - Customer support
    - Operations
    - Finance
    - Legal
    - Compliance
    - Security
    - Data teams
    - Customers

Stakeholders often have different objectives.

Sales may want:
    A feature required by an important customer.

Engineering may want:
    Time to reduce technical debt.

Marketing may want:
    A capability that supports a campaign.

Finance may want:
    Cost reduction.

Users may want:
    Faster and simpler workflows.

The Product Manager must bring these perspectives together
without allowing every request to become a product priority.
""")

# ============================================================
# 30. INFLUENCE WITHOUT AUTHORITY
# ============================================================

print("\n" + "=" * 80)
print("30. INFLUENCE WITHOUT AUTHORITY")
print("=" * 80)

print("""
A Product Manager often has responsibility without direct managerial
authority.

The Product Manager may not be the manager of:

    - Engineers
    - Designers
    - Analysts
    - Marketers

Yet the Product Manager must influence their work.

Influence comes from:

    - Clear reasoning
    - Evidence
    - Trust
    - Context
    - Communication
    - Consistency
    - Respect for expertise
    - Good decision-making

Weak influence:

    "Because I am the Product Manager."

Strong influence:

    "Here is the customer evidence, here is the business objective,
     here are the constraints, and here is why this option provides
     the strongest expected outcome."
""")

# ============================================================
# 31. COORDINATION
# ============================================================

print("\n" + "=" * 80)
print("31. CROSS-FUNCTIONAL COORDINATION")
print("=" * 80)

print("""
A Product Manager coordinates across multiple disciplines.

Example:

A payment feature may require:

    Product
       |
    Design
       |
    Engineering
       |
    Security
       |
    Compliance
       |
    Finance
       |
    Operations
       |
    Customer Support

Coordination involves identifying:

    - Who needs to know?
    - Who needs to decide?
    - Who needs to execute?
    - Who can block the work?
    - Who provides specialised expertise?
    - What dependencies exist?

Coordination is not the same as scheduling meetings.

Effective coordination creates shared understanding.
""")

# ============================================================
# 32. RACI
# ============================================================

print("\n" + "=" * 80)
print("32. RACI THINKING")
print("=" * 80)

print("""
RACI is a responsibility framework.

R = Responsible
A = Accountable
C = Consulted
I = Informed

Example:

Activity:
Launch a new payment method.

Product:
    A

Engineering:
    R

Design:
    R

Security:
    C

Compliance:
    C

Customer Support:
    I

The exact allocation depends on the organisation.

The important idea is to avoid ambiguity about ownership.
""")

# ============================================================
# 33. COMMUNICATION
# ============================================================

print("\n" + "=" * 80)
print("33. PRODUCT COMMUNICATION")
print("=" * 80)

print("""
Product Managers communicate in several forms:

    - Product requirement documents
    - Roadmaps
    - Presentations
    - Decision documents
    - Meeting discussions
    - Release notes
    - Executive updates
    - User stories
    - Product briefs
    - Metrics reports

Different audiences need different levels of detail.

Executive audience:

    Business outcome
    Risk
    Investment
    Strategic alignment

Engineering audience:

    Requirements
    Constraints
    Dependencies
    Edge cases
    Acceptance criteria

Design audience:

    User problem
    Context
    User behaviour
    Experience goals

Customer support:

    Product behaviour
    Known limitations
    User impact
    Communication requirements
""")

# ============================================================
# 34. DATA AND PRODUCT MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("34. DATA-DRIVEN PRODUCT MANAGEMENT")
print("=" * 80)

print("""
Product Managers use data to understand:

    - Acquisition
    - Activation
    - Engagement
    - Retention
    - Conversion
    - Revenue
    - Churn
    - Feature usage
    - Funnel performance

Data does not automatically produce the correct decision.

A Product Manager must ask:

    What does the metric actually measure?
    How was it calculated?
    What segment is included?
    What might explain the movement?
    Could another factor have caused it?
    Is the sample large enough?
    Is the metric aligned with the actual outcome?
""")

# ============================================================
# 35. FUNNEL ANALYSIS
# ============================================================

print("\n" + "=" * 80)
print("35. PRODUCT FUNNEL")
print("=" * 80)

funnel = {
    "Visited product page": 10000,
    "Created account": 6000,
    "Started onboarding": 4800,
    "Completed onboarding": 3600,
    "Completed first transaction": 2160
}

previous = None

for stage, users in funnel.items():
    if previous is None:
        conversion = 100.0
    else:
        conversion = users / previous * 100

    print(f"{stage:<35} {users:>6} users | Stage conversion: {conversion:>6.2f}%")
    previous = users

print("""
Funnel analysis helps identify where users drop out.

The Product Manager should not immediately assume that the largest
percentage drop is automatically the most important issue.

The Product Manager should also examine:

    - Volume
    - User value
    - Severity
    - Cause
    - Segment differences
    - Cost of fixing
""")

# ============================================================
# 36. NORTH STAR METRIC
# ============================================================

print("\n" + "=" * 80)
print("36. NORTH STAR METRIC")
print("=" * 80)

print("""
A North Star Metric is intended to represent an important expression
of customer value and product growth.

Examples depend heavily on the product.

For a collaboration product:

    Weekly active teams completing meaningful collaboration.

For a marketplace:

    Successful transactions.

For a learning platform:

    Meaningful learning sessions completed.

A North Star Metric should not become an isolated number.

It should connect to supporting metrics.

Example:

    North Star:
        Successful transactions

    Supporting metrics:
        Visitor conversion
        Search success
        Add-to-cart rate
        Checkout completion
        Payment success
        Repeat purchase rate
""")

# ============================================================
# 37. LEADING AND LAGGING INDICATORS
# ============================================================

print("\n" + "=" * 80)
print("37. LEADING VS LAGGING INDICATORS")
print("=" * 80)

print("""
A leading indicator can provide an earlier signal about future outcomes.

A lagging indicator reflects an outcome after it has occurred.

Example:

Lagging:
    Monthly revenue

Potential leading indicators:
    Trial activation
    Product engagement
    Conversion rate
    Qualified pipeline

Product Managers use both.

A business may have strong current revenue while early indicators
show that retention is deteriorating.

This creates a potential future problem even when current revenue
still looks healthy.
""")

# ============================================================
# 38. A/B TESTING
# ============================================================

print("\n" + "=" * 80)
print("38. EXPERIMENTATION")
print("=" * 80)

print("""
A/B testing compares two variants under controlled conditions.

Example:

    Control:
        Existing checkout

    Treatment:
        Simplified checkout

Suppose:

    Control conversions = 8%
    Treatment conversions = 9.2%

The observed improvement is:

    9.2% - 8% = 1.2 percentage points

Relative improvement:

    (9.2 - 8) / 8 * 100
""")

control = 8
treatment = 9.2

absolute_change = treatment - control
relative_change = absolute_change / control * 100

print(f"Absolute change: {absolute_change:.2f} percentage points")
print(f"Relative change: {relative_change:.2f}%")

print("""
A Product Manager should not interpret an observed difference as
proof of causality without considering statistical validity,
sample size, experiment design, duration and possible confounding factors.

An experiment should begin with a hypothesis.

Example:

    "If checkout form complexity is reduced, checkout completion
     will increase because users will encounter less friction."
""")

# ============================================================
# 39. PRODUCT HYPOTHESES
# ============================================================

print("\n" + "=" * 80)
print("39. PRODUCT HYPOTHESES")
print("=" * 80)

print("""
A hypothesis is a testable statement about a relationship between
an intervention and an expected outcome.

Structure:

    We believe that [change]
    will cause [user behaviour/outcome]
    because [reason/evidence].

Example:

    We believe that simplifying onboarding will increase activation
    because new users currently abandon the process when asked for
    too much information.

A good hypothesis creates something that can be tested.

A vague statement:

    "Users will like the new onboarding."

A stronger statement:

    "Reducing onboarding from eight required fields to four will
     increase account activation among new users."
""")

# ============================================================
# 40. PRODUCT-MARKET FIT
# ============================================================

print("\n" + "=" * 80)
print("40. PRODUCT-MARKET FIT")
print("=" * 80)

print("""
Product-market fit refers broadly to the condition where a product
strongly satisfies an important market need and demonstrates meaningful
user demand.

Signs can include:

    - Strong retention
    - Organic demand
    - Repeat usage
    - Customer referrals
    - Willingness to pay
    - Growing usage
    - Strong customer feedback

Product-market fit is not simply:

    "The product has many users."

A product can have many users because of:

    - Heavy marketing
    - Discounts
    - Network effects
    - Temporary incentives

The Product Manager must understand whether users receive sufficient
value to continue using or paying for the product.
""")

# ============================================================
# 41. ROADMAP THINKING
# ============================================================

print("\n" + "=" * 80)
print("41. PRODUCT ROADMAP")
print("=" * 80)

print("""
A roadmap communicates product direction and priorities over time.

A weak roadmap:

    January:
        Feature A
    February:
        Feature B
    March:
        Feature C

This can make the roadmap look like a promise of exact delivery dates.

A stronger outcome-oriented roadmap might be:

    Q1:
        Improve activation

    Q2:
        Improve repeat usage

    Q3:
        Expand monetisation

Within each area, initiatives can be selected based on evidence
and changing circumstances.

A roadmap is therefore a planning and communication tool, not merely
a calendar of features.
""")

# ============================================================
# 42. OKRs
# ============================================================

print("\n" + "=" * 80)
print("42. OBJECTIVES AND KEY RESULTS")
print("=" * 80)

print("""
OKRs connect objectives with measurable results.

OBJECTIVE:
    What meaningful outcome are we trying to achieve?

KEY RESULT:
    How will we know that the objective has improved?

Example:

Objective:
    Make onboarding significantly easier for new customers.

Key Results:

    KR1: Increase activation from 45% to 60%.
    KR2: Reduce median onboarding completion time from 8 minutes to 5.
    KR3: Reduce onboarding-related support contacts by 25%.

Notice that these are outcomes.

A feature such as:

    "Build an onboarding checklist"

is not itself a Key Result.

It is an initiative that may contribute to the Key Results.
""")

# ============================================================
# 43. INITIATIVES VS OUTCOMES
# ============================================================

print("\n" + "=" * 80)
print("43. OUTPUTS VS OUTCOMES")
print("=" * 80)

print("""
OUTPUT
------

What the team produces.

Examples:

    - New feature
    - Dashboard
    - API
    - Mobile application
    - Integration

OUTCOME
-------

What changes because of the output.

Examples:

    - Higher activation
    - Lower churn
    - Faster task completion
    - Higher revenue
    - Better customer satisfaction

Example:

Output:
    "Released a new onboarding flow."

Outcome:
    "Activation increased from 45% to 58%."

A Product Manager should avoid treating shipment itself as success.
""")

# ============================================================
# 44. BUSINESS MODEL
# ============================================================

print("\n" + "=" * 80)
print("44. PRODUCT AND BUSINESS MODEL")
print("=" * 80)

print("""
A Product Manager needs to understand how the product creates and
captures value.

Common business models include:

    - Subscription
    - Transaction fee
    - Advertising
    - Licensing
    - Marketplace commission
    - Freemium
    - Usage-based pricing
    - Enterprise contracts
    - Hardware plus service

Important concepts include:

    Revenue
    Cost
    Gross margin
    Customer acquisition cost
    Lifetime value
    Retention
    Churn
    Conversion
    Pricing

A product can be useful but economically weak.

Product decisions therefore need commercial context.
""")

# ============================================================
# 45. UNIT ECONOMICS
# ============================================================

print("\n" + "=" * 80)
print("45. UNIT ECONOMICS")
print("=" * 80)

print("""
Unit economics examines the economics of a single customer,
transaction or other relevant unit.

A simplified relationship is:

    LTV > CAC

where:

    LTV = Lifetime Value
    CAC = Customer Acquisition Cost

Example:

    CAC = ₹1,000
    Estimated LTV = ₹4,000

LTV/CAC ratio:

    4,000 / 1,000 = 4

This does not mean the product is automatically healthy.

Other factors matter:

    - Gross margin
    - Payback period
    - Retention
    - Cash requirements
    - Growth rate
    - Operational costs

The Product Manager should understand the economics relevant
to the product.
""")

# ============================================================
# 46. PRODUCT LIFECYCLE
# ============================================================

print("\n" + "=" * 80)
print("46. PRODUCT LIFECYCLE")
print("=" * 80)

print("""
A product can move through different stages.

    Introduction
        |
        v
    Growth
        |
        v
    Maturity
        |
        v
    Decline / Transformation

Different stages create different product problems.

INTRODUCTION:

    - Validate demand
    - Find early users
    - Establish core value

GROWTH:

    - Improve scalability
    - Increase acquisition
    - Improve retention
    - Expand capabilities

MATURITY:

    - Optimise economics
    - Defend market position
    - Improve efficiency
    - Expand carefully

DECLINE:

    - Reposition
    - Reduce investment
    - Find new market
    - Retire product
""")

# ============================================================
# 47. COMPETITIVE ANALYSIS
# ============================================================

print("\n" + "=" * 80)
print("47. COMPETITIVE THINKING")
print("=" * 80)

print("""
Competition is not limited to companies offering an identical product.

Competition can include:

    Direct competitors
    Indirect competitors
    Internal alternatives
    Manual processes
    Doing nothing

Example:

A project-management application competes not only with another
project-management application.

Users may also use:

    - Spreadsheets
    - Email
    - Messaging applications
    - Documents
    - Meetings
    - Manual tracking

The Product Manager should understand the customer's current
alternative, not only named competitors.
""")

# ============================================================
# 48. BUILD VS BUY
# ============================================================

print("\n" + "=" * 80)
print("48. BUILD VS BUY")
print("=" * 80)

print("""
Product teams sometimes need to decide whether to build a capability
internally or purchase/use an external solution.

Factors include:

    Cost
    Time
    Strategic importance
    Differentiation
    Security
    Compliance
    Integration complexity
    Vendor dependency
    Long-term maintenance

Build may be appropriate when:

    - The capability is strategically important.
    - It creates differentiation.
    - Existing solutions are insufficient.

Buy may be appropriate when:

    - The capability is not differentiating.
    - A mature solution already exists.
    - Internal development would consume excessive resources.

The decision is not simply:

    "Build = control"
    "Buy = cheap"

The full lifecycle cost matters.
""")

# ============================================================
# 49. TECHNICAL DEBT
# ============================================================

print("\n" + "=" * 80)
print("49. TECHNICAL DEBT")
print("=" * 80)

print("""
Technical debt occurs when technical shortcuts or accumulated
engineering limitations increase future cost, risk or complexity.

Examples:

    - Old dependencies
    - Poor architecture
    - Duplicate systems
    - Missing tests
    - Slow database queries
    - Temporary workarounds
    - Difficult deployment processes

Technical debt competes for capacity with customer-facing work.

A Product Manager should understand:

    What is the business impact?
    How much risk does it create?
    Does it slow feature delivery?
    Does it affect reliability?
    Is the problem becoming more expensive?

Technical debt should be discussed in terms of impact, not only
engineering terminology.
""")

# ============================================================
# 50. RISK MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("50. PRODUCT RISK")
print("=" * 80)

print("""
Product risk can come from many sources.

USER RISK
    Users may not want the product.

BUSINESS RISK
    Product may not produce sufficient economic value.

TECHNICAL RISK
    System may not be feasible or scalable.

OPERATIONAL RISK
    Organisation may not support the product effectively.

LEGAL / COMPLIANCE RISK
    Product may violate requirements.

SECURITY RISK
    Product may expose systems or data.

EXECUTION RISK
    Team may not deliver within constraints.

A Product Manager should identify important risks early.
""")

# ============================================================
# 51. RISK MATRIX
# ============================================================

print("\n" + "=" * 80)
print("51. RISK MATRIX")
print("=" * 80)

risks = [
    ("Users do not adopt feature", 8, 7),
    ("Engineering integration fails", 6, 6),
    ("Launch is delayed", 5, 8),
    ("Minor UI defect", 2, 3),
]

print(f"{'Risk':<35}{'Probability':<15}{'Impact':<10}")

for risk, probability, impact in risks:
    risk_score = probability * impact
    print(
        f"{risk:<35}"
        f"{probability:<15}"
        f"{impact:<10}"
        f"Score={risk_score}"
    )

print("""
A simple risk score can be:

    Risk Score = Probability * Impact

Again, the exact scoring method varies by organisation.

The purpose is to make risk visible and comparable.
""")

# ============================================================
# 52. MVP
# ============================================================

print("\n" + "=" * 80)
print("52. MINIMUM VIABLE PRODUCT")
print("=" * 80)

print("""
An MVP is not simply:

    "The smallest product we can build."

The useful interpretation is:

    "The smallest viable product that can generate meaningful
     learning or deliver meaningful value for the intended purpose."

Example:

Suppose the problem is helping customers book appointments.

Potential MVP:

    - Search provider
    - Select appointment
    - Confirm booking

Potential non-MVP capabilities:

    - Advanced recommendation engine
    - Loyalty program
    - Social sharing
    - Complex personalisation

The correct MVP depends on the hypothesis being tested.
""")

# ============================================================
# 53. PRODUCT SENSE
# ============================================================

print("\n" + "=" * 80)
print("53. PRODUCT SENSE")
print("=" * 80)

print("""
Product sense is the ability to reason about products, users,
behaviour, value and trade-offs.

A Product Manager with strong product sense can examine a product
and ask:

    Who is this for?
    What job is the user trying to accomplish?
    What is the core value proposition?
    Where does friction occur?
    Why might users return?
    What could cause users to leave?
    What metric represents value?
    What would I improve first?
    What evidence would I need?

Product sense is not intuition alone.

Strong product judgement combines:

    Observation
    Experience
    User understanding
    Data
    Business context
    Technology awareness
    Structured reasoning
""")

# ============================================================
# 54. PRODUCT CASE STUDY
# ============================================================

print("\n" + "=" * 80)
print("54. PRODUCT CASE STUDY")
print("=" * 80)

print("""
SCENARIO:

A food delivery application has noticed that repeat orders have fallen.

Observed data:

    New customer orders are stable.
    First-order conversion is stable.
    Repeat orders have decreased.
    Customer complaints about delivery delays have increased.

A Product Manager should not immediately propose:

    "Add more discounts."

First, define the problem.

Possible hypothesis:

    Delivery reliability has deteriorated, reducing customer trust
    and willingness to reorder.

Potential investigation:

    - Delivery time trend
    - Late-order percentage
    - Cancellation rate
    - Restaurant preparation time
    - Delivery partner availability
    - Customer segment
    - Geographic differences
    - Repeat order behaviour

Potential product interventions may include:

    - Better delivery estimates
    - Restaurant preparation visibility
    - Improved dispatch logic
    - Better partner allocation
    - Proactive delay communication

The solution should depend on evidence.
""")

# ============================================================
# 55. DECISION LOG
# ============================================================

print("\n" + "=" * 80)
print("55. PRODUCT DECISION LOG")
print("=" * 80)

decision_log = []

def record_decision(decision, context, rationale, expected_outcome):
    entry = {
        "decision": decision,
        "context": context,
        "rationale": rationale,
        "expected_outcome": expected_outcome
    }
    decision_log.append(entry)

record_decision(
    decision="Prioritise onboarding simplification",
    context="High abandonment during onboarding",
    rationale="Analytics and customer feedback indicate excessive friction",
    expected_outcome="Increase activation rate"
)

for index, item in enumerate(decision_log, start=1):
    print(f"\nDecision {index}")
    print(f"Decision: {item['decision']}")
    print(f"Context: {item['context']}")
    print(f"Rationale: {item['rationale']}")
    print(f"Expected outcome: {item['expected_outcome']}")

print("""
A decision log helps preserve organisational memory.

It records:

    What was decided?
    Why?
    Based on what information?
    What outcome was expected?

This is especially useful when a team later revisits the same problem.
""")

# ============================================================
# 56. PRODUCT BRIEF
# ============================================================

print("\n" + "=" * 80)
print("56. PRODUCT BRIEF STRUCTURE")
print("=" * 80)

product_brief = {
    "Problem": "Users abandon onboarding because the process is too long.",
    "Target user": "New customers",
    "Evidence": "Large drop-off occurs after multiple required fields.",
    "Goal": "Increase activation.",
    "Hypothesis": "Reducing required information will decrease friction.",
    "Success metric": "Activation rate",
    "Constraints": "Compliance requires certain information.",
    "Initial scope": "Reduce non-essential fields.",
}

for key, value in product_brief.items():
    print(f"{key:<20}: {value}")

print("""
A product brief creates a shared starting point before detailed
implementation work begins.
""")

# ============================================================
# 57. PRODUCT MANAGER DAILY WORK
# ============================================================

print("\n" + "=" * 80)
print("57. A TYPICAL PRODUCT MANAGER WORKING DAY")
print("=" * 80)

print("""
A Product Manager's day can contain very different types of work.

Morning:

    - Review product metrics
    - Check incidents
    - Review team progress
    - Identify blockers

Midday:

    - Discuss requirements with Engineering
    - Review designs
    - Talk to stakeholders
    - Conduct customer research
    - Analyse data

Afternoon:

    - Prioritisation
    - Product planning
    - Decision-making
    - Documentation
    - Strategy work

The work is not necessarily predictable.

A production incident can change the day's priorities immediately.

This is why Product Managers need strong prioritisation and context
switching abilities.
""")

# ============================================================
# 58. WEEKLY PRODUCT MANAGEMENT CYCLE
# ============================================================

print("\n" + "=" * 80)
print("58. WEEKLY PRODUCT MANAGEMENT CYCLE")
print("=" * 80)

weekly_cycle = {
    "Monday": "Review metrics, priorities and risks",
    "Tuesday": "Customer discovery and product analysis",
    "Wednesday": "Design and engineering collaboration",
    "Thursday": "Stakeholder alignment and decision-making",
    "Friday": "Review outcomes, documentation and planning",
}

for day, activity in weekly_cycle.items():
    print(f"{day:<12}: {activity}")

print("""
This is illustrative rather than prescriptive.

Actual product work depends on product stage, organisation,
team structure and current problems.
""")

# ============================================================
# 59. PRODUCT MANAGER SKILL SET
# ============================================================

print("\n" + "=" * 80)
print("59. PRODUCT MANAGER SKILLS")
print("=" * 80)

skills = {
    "Product thinking": "Understand users, problems and value",
    "Communication": "Create clarity across different audiences",
    "Analytical thinking": "Interpret data and evidence",
    "Prioritisation": "Choose among competing opportunities",
    "Decision-making": "Make informed choices under uncertainty",
    "Strategy": "Connect product direction to business objectives",
    "Execution": "Drive work from decision to outcome",
    "Leadership": "Influence without relying only on authority",
    "Customer understanding": "Understand behaviour and needs",
    "Technical literacy": "Understand technical constraints and possibilities",
    "Business understanding": "Understand economics and commercial context",
    "Negotiation": "Resolve conflicting interests and trade-offs",
}

for skill, meaning in skills.items():
    print(f"{skill:<25}: {meaning}")

# ============================================================
# 60. TECHNICAL LITERACY
# ============================================================

print("\n" + "=" * 80)
print("60. TECHNICAL LITERACY FOR PRODUCT MANAGERS")
print("=" * 80)

print("""
A Product Manager does not necessarily need to be a professional
software engineer.

But technical literacy is valuable.

Important concepts include:

    - APIs
    - Databases
    - Authentication
    - Authorisation
    - Frontend
    - Backend
    - Cloud systems
    - Integrations
    - Data pipelines
    - Latency
    - Scalability
    - Reliability
    - Security
    - Technical debt

The purpose is not to replace engineers.

The purpose is to understand:

    What is technically possible?
    What is expensive?
    What is risky?
    What dependencies exist?
    What trade-offs are involved?
""")

# ============================================================
# 61. DESIGN LITERACY
# ============================================================

print("\n" + "=" * 80)
print("61. DESIGN LITERACY")
print("=" * 80)

print("""
A Product Manager should understand basic design concepts such as:

    - User flows
    - Information architecture
    - Usability
    - Accessibility
    - Interaction design
    - Visual hierarchy
    - Error states
    - Empty states
    - Responsive design

The Product Manager should not dictate every design detail.

The Product Manager provides:

    User problem
    Context
    Business objective
    Constraints
    Expected outcome

The designer contributes expertise in:

    Experience
    Interaction
    Visual communication
    Usability
    Human behaviour
""")

# ============================================================
# 62. PRODUCT ANALYTICS
# ============================================================

print("\n" + "=" * 80)
print("62. PRODUCT ANALYTICS QUESTIONS")
print("=" * 80)

analytics_questions = [
    "How many users enter the funnel?",
    "Where do users drop?",
    "Which users are most valuable?",
    "Which features are actually used?",
    "How often are features used?",
    "What behaviour predicts retention?",
    "Which segment has the highest churn?",
    "What changed after the release?",
    "Is the change statistically meaningful?",
    "Could another factor explain the result?",
]

for question in analytics_questions:
    print("-", question)

# ============================================================
# 63. SEGMENTATION
# ============================================================

print("\n" + "=" * 80)
print("63. USER SEGMENTATION")
print("=" * 80)

print("""
Averages can hide important differences.

Suppose overall conversion is:

    10%

But segmented data shows:

    New users:       5%
    Returning users: 20%

An overall metric may hide the real product problem.

Segmentation can be based on:

    - Geography
    - Device
    - Customer type
    - Acquisition channel
    - Usage frequency
    - Subscription plan
    - Industry
    - Behaviour

The Product Manager should ask:

    "Who is experiencing this problem?"

rather than assuming that every user experiences the product
in exactly the same way.
""")

# ============================================================
# 64. CUSTOMER JOURNEY
# ============================================================

print("\n" + "=" * 80)
print("64. CUSTOMER JOURNEY")
print("=" * 80)

journey = [
    "Awareness",
    "Consideration",
    "Acquisition",
    "Onboarding",
    "Activation",
    "Engagement",
    "Retention",
    "Expansion",
    "Advocacy",
]

for index, stage in enumerate(journey, start=1):
    print(f"{index}. {stage}")

print("""
The Product Manager can identify problems at any stage.

For example:

    Awareness problem:
        Users do not know the product exists.

    Acquisition problem:
        Users understand the product but do not sign up.

    Activation problem:
        Users sign up but do not experience core value.

    Retention problem:
        Users experience value once but do not return.

Different problems require different interventions.
""")

# ============================================================
# 65. PRODUCT METRIC TREE
# ============================================================

print("\n" + "=" * 80)
print("65. PRODUCT METRIC TREE")
print("=" * 80)

print("""
A metric tree breaks a high-level outcome into contributing metrics.

Example:

                  Revenue
                     |
          +----------+----------+
          |                     |
      Customers             Revenue/customer
          |
      +---+---+
      |       |
  Acquisition Retention
      |
  Conversion
      |
  Activation

This structure helps Product Managers move from:

    "Revenue decreased."

to:

    "Revenue decreased because repeat purchases decreased."

and then:

    "Repeat purchases decreased because active customers
     are ordering less frequently."

The metric tree supports diagnosis rather than simple reporting.
""")

# ============================================================
# 66. PRODUCT OPERATING MODEL
# ============================================================

print("\n" + "=" * 80)
print("66. PRODUCT OPERATING MODEL")
print("=" * 80)

print("""
A product organisation needs a repeatable operating model.

One possible model is:

    1. Identify opportunity
    2. Gather evidence
    3. Define problem
    4. Estimate potential value
    5. Explore solutions
    6. Test assumptions
    7. Prioritise
    8. Define requirements
    9. Build
    10. Release
    11. Measure
    12. Learn

This cycle creates a relationship between strategy and execution.

Without discovery:

    Execution can become feature production.

Without execution:

    Strategy remains theoretical.

Without measurement:

    Teams cannot reliably determine whether their work created value.
""")

# ============================================================
# 67. PRODUCT GOVERNANCE
# ============================================================

print("\n" + "=" * 80)
print("67. PRODUCT GOVERNANCE")
print("=" * 80)

print("""
Product governance defines how important product decisions are made
and controlled.

It can include:

    - Decision rights
    - Approval processes
    - Compliance requirements
    - Security reviews
    - Release controls
    - Data governance
    - Risk management
    - Product standards

Governance is particularly important in:

    Banking
    Healthcare
    Insurance
    Government
    Enterprise software
    Financial technology

A Product Manager must understand when a product decision can be made
independently and when specialised approval is required.
""")

# ============================================================
# 68. CONFLICT MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("68. CONFLICT MANAGEMENT")
print("=" * 80)

print("""
Product conflicts are normal.

Example:

Engineering:
    "We need six weeks for technical improvements."

Sales:
    "The customer needs the feature in two weeks."

Marketing:
    "The campaign starts next month."

Product:
    Must understand all constraints and determine the appropriate
    product decision.

A productive conflict discussion focuses on:

    Evidence
    Objective
    Constraints
    Trade-offs
    Alternatives
    Consequences

An unproductive discussion focuses on:

    Authority
    Personal preference
    Blame
    Pressure
    Politics

The Product Manager should turn disagreement into an explicit
decision problem.
""")

# ============================================================
# 69. NEGOTIATION
# ============================================================

print("\n" + "=" * 80)
print("69. PRODUCT NEGOTIATION")
print("=" * 80)

print("""
Negotiation often occurs around:

    Scope
    Timeline
    Resources
    Priority
    Quality
    Requirements
    Launch dates

Example:

Stakeholder:
    "We need all ten features by the end of the month."

Product Manager:
    "Given the available engineering capacity, delivering all ten
     features creates a high reliability risk. We can deliver the
     three features most closely tied to the business objective by
     the target date, or we can expand the timeline."

This changes the conversation from:

    "Yes vs No"

to:

    "Which trade-off are we willing to make?"
""")

# ============================================================
# 70. ESCALATION
# ============================================================

print("\n" + "=" * 80)
print("70. ESCALATION")
print("=" * 80)

print("""
Escalation should not simply mean passing a problem to someone senior.

A useful escalation contains:

    Problem
    Context
    Impact
    Options
    Recommendation
    Decision required

Example:

    Problem:
        Payment integration is delayed.

    Impact:
        Launch may move by two weeks.

    Options:
        A. Delay launch.
        B. Launch without the payment method.
        C. Use temporary alternative provider.

    Recommendation:
        Option A because the payment method is core to the product.

    Decision required:
        Confirm revised launch date.
""")

# ============================================================
# 71. PRODUCT LAUNCH
# ============================================================

print("\n" + "=" * 80)
print("71. PRODUCT LAUNCH")
print("=" * 80)

print("""
A launch involves more than deploying software.

Possible launch dimensions include:

    Product readiness
    Engineering readiness
    Design readiness
    Data tracking
    Customer support readiness
    Marketing readiness
    Legal/compliance approval
    Documentation
    Training
    Monitoring
    Rollback plan

A launch checklist may include:

    [ ] Requirements complete
    [ ] QA complete
    [ ] Analytics implemented
    [ ] Monitoring configured
    [ ] Support informed
    [ ] Documentation ready
    [ ] Rollback understood
    [ ] Stakeholders aligned
""")

# ============================================================
# 72. POST-LAUNCH MANAGEMENT
# ============================================================

print("\n" + "=" * 80)
print("72. POST-LAUNCH")
print("=" * 80)

print("""
The product launch is not the end of product management.

After launch, the Product Manager should examine:

    - Adoption
    - Usage
    - Conversion
    - Errors
    - Customer feedback
    - Support tickets
    - Retention
    - Revenue
    - Experiment results

Questions include:

    Did users adopt it?

    Did they use it repeatedly?

    Did the expected behaviour change?

    Did the business metric improve?

    Were there unintended consequences?

A shipped feature that nobody uses is not automatically a successful
product outcome.
""")

# ============================================================
# 73. UNINTENDED CONSEQUENCES
# ============================================================

print("\n" + "=" * 80)
print("73. UNINTENDED CONSEQUENCES")
print("=" * 80)

print("""
Optimising one metric can negatively affect another.

Example:

A company wants to increase checkout conversion.

It removes several verification steps.

Result:

    Conversion increases.

But:

    Fraud increases.

This demonstrates why Product Managers should monitor multiple
dimensions of product health.

Possible categories:

    Growth
    Engagement
    Retention
    Revenue
    Quality
    Safety
    Reliability
    Customer satisfaction

A product decision should be evaluated for both intended and
unintended effects.
""")

# ============================================================
# 74. PRODUCT ETHICS
# ============================================================

print("\n" + "=" * 80)
print("74. PRODUCT ETHICS")
print("=" * 80)

print("""
Product decisions can influence user behaviour.

Important considerations include:

    Privacy
    Consent
    Transparency
    Accessibility
    Safety
    Fairness
    Data usage
    Manipulative design
    Vulnerable users

A Product Manager should distinguish between:

    "Can we build this?"

and:

    "Should we build this?"

Technical feasibility does not automatically imply ethical
or responsible product suitability.
""")

# ============================================================
# 75. PRODUCT THINKING EXERCISE
# ============================================================

print("\n" + "=" * 80)
print("75. PRODUCT THINKING EXERCISE")
print("=" * 80)

scenario = """
A banking application has a large number of users who start
opening a savings account but do not complete the process.

The business wants to add a chatbot.

Apply product thinking.

Step 1:
    Define the problem.

Step 2:
    Identify affected users.

Step 3:
    Examine the funnel.

Step 4:
    Identify where abandonment occurs.

Step 5:
    Investigate possible causes.

Step 6:
    Determine whether users need information, trust, speed,
    document support or something else.

Step 7:
    Evaluate possible solutions.

Step 8:
    Define a measurable outcome.

Step 9:
    Select an experiment.

Step 10:
    Measure the result.
"""

print(scenario)

# ============================================================
# 76. PRODUCT DECISION EXERCISE
# ============================================================

print("\n" + "=" * 80)
print("76. PRODUCT DECISION EXERCISE")
print("=" * 80)

options = {
    "A": {
        "impact": 9,
        "effort": 8,
        "confidence": 0.6,
        "strategic_alignment": 9
    },
    "B": {
        "impact": 6,
        "effort": 3,
        "confidence": 0.9,
        "strategic_alignment": 7
    },
    "C": {
        "impact": 4,
        "effort": 2,
        "confidence": 0.95,
        "strategic_alignment": 3
    }
}

for option, values in options.items():
    efficiency = (
        values["impact"]
        * values["confidence"]
        * values["strategic_alignment"]
        / values["effort"]
    )

    print(
        f"Option {option}: "
        f"impact={values['impact']}, "
        f"effort={values['effort']}, "
        f"confidence={values['confidence']}, "
        f"alignment={values['strategic_alignment']}, "
        f"illustrative score={efficiency:.2f}"
    )

print("""
The calculation demonstrates structured comparison.

It does not replace judgement.

For example, Option A may have strategic importance that cannot
be represented perfectly by a simple formula.
""")

# ============================================================
# 77. PRODUCT MANAGER MINDSET
# ============================================================

print("\n" + "=" * 80)
print("77. PRODUCT MANAGER MINDSET")
print("=" * 80)

mindset = [
    ("Feature thinking", "Problem thinking"),
    ("Output focus", "Outcome focus"),
    ("Opinion", "Evidence"),
    ("Everything is priority", "Explicit prioritisation"),
    ("Build first", "Understand first"),
    ("More features", "More value"),
    ("Personal preference", "User and business needs"),
    ("Avoid decisions", "Make accountable decisions"),
    ("Optimise one team", "Optimise product outcome"),
]

print(f"{'Less effective tendency':<30} -> More product-oriented thinking")

for old, new in mindset:
    print(f"{old:<30} -> {new}")

# ============================================================
# 78. PRODUCT MANAGER DECISION CHECKLIST
# ============================================================

print("\n" + "=" * 80)
print("78. DECISION CHECKLIST")
print("=" * 80)

decision_checklist = [
    "Is the problem clearly defined?",
    "Who experiences the problem?",
    "What evidence supports the problem?",
    "What outcome are we trying to change?",
    "What alternatives exist?",
    "What are the major trade-offs?",
    "What is the expected value?",
    "What is the cost?",
    "What risks exist?",
    "Is the decision reversible?",
    "Who needs to be consulted?",
    "Who owns the final decision?",
    "How will success be measured?",
]

for item in decision_checklist:
    print("[ ]", item)

# ============================================================
# 79. PRODUCT MANAGER EXECUTION CHECKLIST
# ============================================================

print("\n" + "=" * 80)
print("79. EXECUTION CHECKLIST")
print("=" * 80)

execution_checklist = [
    "Objective is defined",
    "Problem is understood",
    "Requirements are clear",
    "Dependencies are identified",
    "Design is aligned",
    "Engineering approach is understood",
    "Acceptance criteria are defined",
    "Risks are visible",
    "Stakeholders are aligned",
    "Analytics are defined",
    "Launch requirements are understood",
    "Post-launch measurement is planned",
]

for item in execution_checklist:
    print("[ ]", item)

# ============================================================
# 80. PRODUCT STRATEGY CHECKLIST
# ============================================================

print("\n" + "=" * 80)
print("80. STRATEGY CHECKLIST")
print("=" * 80)

strategy_checklist = [
    "What is the product vision?",
    "What business objective does the product support?",
    "Who is the target customer?",
    "What important problem are we solving?",
    "Why is the problem worth solving?",
    "What alternatives already exist?",
    "What is our product advantage?",
    "What capabilities are strategically important?",
    "What should we deliberately not do?",
    "What outcome will define success?",
]

for item in strategy_checklist:
    print("[ ]", item)

# ============================================================
# 81. PRODUCT MANAGEMENT SIMULATION
# ============================================================

print("\n" + "=" * 80)
print("81. PRODUCT MANAGEMENT SIMULATION")
print("=" * 80)

class ProductManagerSimulation:
    def __init__(self):
        self.objective = None
        self.problem = None
        self.options = []
        self.decision = None
        self.metric = None
        self.result = None

    def define_objective(self, objective):
        self.objective = objective

    def define_problem(self, problem):
        self.problem = problem

    def add_option(self, option):
        self.options.append(option)

    def make_decision(self, decision):
        self.decision = decision

    def define_metric(self, metric):
        self.metric = metric

    def record_result(self, result):
        self.result = result

    def display(self):
        print("OBJECTIVE:", self.objective)
        print("PROBLEM:", self.problem)
        print("OPTIONS:")
        for option in self.options:
            print(" -", option)
        print("DECISION:", self.decision)
        print("SUCCESS METRIC:", self.metric)
        print("RESULT:", self.result)


simulation = ProductManagerSimulation()

simulation.define_objective(
    "Increase activation of new users"
)

simulation.define_problem(
    "Users abandon onboarding before reaching the first value moment"
)

simulation.add_option(
    "Reduce unnecessary onboarding fields"
)

simulation.add_option(
    "Add onboarding progress indicator"
)

simulation.add_option(
    "Add onboarding tutorial"
)

simulation.make_decision(
    "Test removal of non-essential onboarding fields"
)

simulation.define_metric(
    "Activation rate"
)

simulation.record_result(
    "Activation increased from 45% to 57%"
)

simulation.display()

# ============================================================
# 82. PRODUCT MANAGEMENT AS A SYSTEM
# ============================================================

print("\n" + "=" * 80)
print("82. PRODUCT MANAGEMENT AS A SYSTEM")
print("=" * 80)

print("""
Product management can be understood as a system connecting:

             BUSINESS
                |
                v
             STRATEGY
                |
                v
             PROBLEMS
                |
                v
              USERS
                |
                v
             EVIDENCE
                |
                v
             DECISIONS
                |
                v
          PRIORITISATION
                |
                v
             EXECUTION
                |
                v
             RELEASE
                |
                v
            OUTCOMES
                |
                v
             LEARNING
                |
                +----------------+
                                 |
                                 v
                             DECISIONS

The Product Manager operates across this entire loop.

This is why the role cannot be reduced to writing tickets,
attending meetings or maintaining a roadmap.

The central responsibility is creating and maintaining a chain
of reasoning from problem to outcome.
""")

# ============================================================
# 83. FINAL LEARNING MODEL
# ============================================================

print("\n" + "=" * 80)
print("83. PRODUCT MANAGER ROLE MODEL")
print("=" * 80)

print("""
A Product Manager's work can be viewed through seven connected areas.

1. RESPONSIBILITY
-----------------
Understand the product, users, business objectives and desired outcomes.

2. OWNERSHIP
------------
Create clarity and accountability for product direction and outcomes.

3. DECISION-MAKING
------------------
Make informed product choices under uncertainty.

4. STRATEGY
-----------
Determine where the product should focus and why.

5. EXECUTION
------------
Translate product decisions into coordinated delivery.

6. COORDINATION
---------------
Align Product, Engineering, Design, Data, Business and other functions.

7. PRODUCT THINKING
-------------------
Start with problems, evidence, users and outcomes rather than assuming
that a requested feature is automatically the right solution.

These seven areas are not independent.

Responsibility creates ownership.

Ownership requires decisions.

Decisions shape strategy.

Strategy determines priorities.

Priorities guide execution.

Execution requires coordination.

Product thinking connects every stage back to users, value and outcomes.

A Product Manager therefore operates between strategic intent and
practical execution while continuously learning from evidence.
""")

print("\n" + "=" * 80)
print("END OF PRODUCT MANAGER ROLE LEARNING MODULE")
print("=" * 80)
