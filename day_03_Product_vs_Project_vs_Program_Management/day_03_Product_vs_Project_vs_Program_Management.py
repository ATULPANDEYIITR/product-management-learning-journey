"""
===============================================================================
PRODUCT vs PROJECT vs PROGRAM MANAGEMENT
PRODUCT MANAGER vs PROJECT MANAGER vs PROGRAM MANAGER
RESPONSIBILITIES | OUTPUTS | KPIs | TIMELINES | OWNERSHIP | JIRA | CONFLUENCE
===============================================================================

PURPOSE
-------
This script is a comprehensive, executable learning guide to understanding:

1. Product Management
2. Project Management
3. Program Management
4. Product Manager vs Project Manager vs Program Manager
5. Responsibilities and ownership
6. Outputs and deliverables
7. KPIs and success metrics
8. Timelines and planning horizons
9. Stakeholder management
10. Roadmaps, backlogs, milestones and dependencies
11. Agile, Scrum, Kanban and hybrid approaches
12. Jira concepts
13. Confluence concepts
14. How Product, Project and Program Management work together
15. Advanced concepts such as OKRs, RACI, risk management,
    dependency management, prioritization and portfolio thinking

IMPORTANT
---------
This is an educational Python script. Python is being used as a structured
learning medium. Most examples are simulations or conceptual models rather
than production implementations.

You can run the entire script directly.

===============================================================================
SECTION 1: THE BIG PICTURE
===============================================================================

A simple way to remember the three disciplines:

PRODUCT = WHAT should we build and WHY?

PROJECT = HOW and WHEN will we deliver a defined initiative?

PROGRAM = HOW do we coordinate multiple related projects and initiatives
           to achieve a larger strategic outcome?

A product usually has a life.

A project usually has a defined beginning and end.

A program coordinates multiple related efforts toward strategic outcomes.

Example:

Company wants to create a new banking application.

PRODUCT MANAGEMENT
-------------------
Question:
    What should the banking application become?

Focus:
    Customer needs
    Market
    Product strategy
    Features
    User experience
    Business value
    Product metrics

PROJECT MANAGEMENT
------------------
Question:
    How do we deliver the mobile banking application's version 1.0
    successfully?

Focus:
    Scope
    Schedule
    Resources
    Budget
    Risks
    Delivery
    Coordination

PROGRAM MANAGEMENT
------------------
Question:
    How do we coordinate the mobile application, backend modernization,
    cybersecurity upgrade, data migration and customer onboarding programs
    so that the organization's digital banking transformation succeeds?

Focus:
    Multiple projects
    Dependencies
    Strategic alignment
    Cross-project risks
    Benefits
    Governance
    Executive communication


===============================================================================
SECTION 2: BASIC DEFINITIONS
===============================================================================
"""


def explain_basic_definitions():
    definitions = {
        "Product": (
            "A product is a solution, service, platform, application, "
            "or experience that continuously creates value for users and "
            "the organization."
        ),

        "Project": (
            "A project is a temporary initiative undertaken to create a "
            "specific result, deliverable, or outcome."
        ),

        "Program": (
            "A program is a coordinated group of related projects and "
            "activities managed together to achieve strategic benefits "
            "that may not be achieved by managing them independently."
        ),

        "Product Management": (
            "The discipline of identifying customer problems, defining "
            "product strategy, prioritizing opportunities, guiding product "
            "development, launching solutions and measuring product value."
        ),

        "Project Management": (
            "The discipline of planning, coordinating and controlling a "
            "temporary initiative so that agreed scope, schedule, cost, "
            "quality and delivery objectives are achieved."
        ),

        "Program Management": (
            "The discipline of coordinating multiple related initiatives "
            "to achieve strategic outcomes, manage dependencies, realize "
            "benefits and maintain organizational alignment."
        ),
    }

    for concept, definition in definitions.items():
        print(f"\n{concept}")
        print("-" * len(concept))
        print(definition)


"""
===============================================================================
SECTION 3: PRODUCT MANAGEMENT
===============================================================================

Product management is fundamentally about maximizing product value.

The Product Manager acts as a bridge between:

Customer
    |
    v
Business Strategy
    |
    v
Product Strategy
    |
    v
Engineering / Design / Data
    |
    v
Market
    |
    v
Feedback
    |
    +---------------------> Product improvement


A Product Manager does NOT simply "manage developers."

A Product Manager manages product direction, priorities, trade-offs and
outcomes.

The Product Manager asks questions such as:

- Who is the customer?
- What problem are we solving?
- Why does this problem matter?
- How frequently does it occur?
- What is the business opportunity?
- What should we build?
- What should we NOT build?
- Which users should we serve first?
- How should we prioritize?
- How will we measure success?
"""


def product_manager_responsibilities():
    responsibilities = [
        "Understand customers and users",
        "Conduct customer discovery",
        "Analyze market and competitors",
        "Define product vision",
        "Define product strategy",
        "Identify customer problems",
        "Create and maintain product roadmap",
        "Prioritize product opportunities",
        "Maintain product backlog",
        "Write or refine product requirements",
        "Define acceptance criteria with relevant teams",
        "Work with UX/UI designers",
        "Work with engineering teams",
        "Coordinate with data and analytics teams",
        "Coordinate product launches",
        "Analyze product performance",
        "Collect customer feedback",
        "Manage product trade-offs",
        "Define product success metrics",
        "Communicate product direction to stakeholders",
    ]

    print("\nPRODUCT MANAGER RESPONSIBILITIES")
    print("=" * 40)

    for number, responsibility in enumerate(responsibilities, start=1):
        print(f"{number:02d}. {responsibility}")


"""
===============================================================================
SECTION 4: PRODUCT MANAGER OUTPUTS
===============================================================================

Typical outputs include:

1. Product Vision
2. Product Strategy
3. Product Roadmap
4. Product Requirements
5. User Stories
6. Acceptance Criteria
7. Prioritized Backlog
8. Product Metrics
9. Experiment Plans
10. Launch Plans
11. Customer Research
12. Product Requirement Documents

Important distinction:

A Product Manager is generally judged more by OUTCOMES than by simply
producing documents.

For example:

Weak measurement:
    "PM created 50 Jira tickets."

Better measurement:
    "Activation increased from 42% to 58%."

Best product thinking:

    Customer Problem
          |
          v
    Product Hypothesis
          |
          v
       Solution
          |
          v
       Experiment
          |
          v
        Metric
          |
          v
       Learning
          |
          v
      Iteration


===============================================================================
SECTION 5: PROJECT MANAGEMENT
===============================================================================

Project management focuses on executing a temporary initiative.

Classic project dimensions include:

SCOPE
SCHEDULE
COST
QUALITY
RESOURCES
RISK
STAKEHOLDERS

A project manager asks:

- What exactly must be delivered?
- When must it be delivered?
- Who is responsible?
- What resources are required?
- What dependencies exist?
- What could go wrong?
- What is the budget?
- How do we track progress?
- What decisions are required?
- What is blocking delivery?
"""


def project_manager_responsibilities():
    responsibilities = [
        "Define project objectives",
        "Create project plans",
        "Establish milestones",
        "Build schedules",
        "Coordinate resources",
        "Track project progress",
        "Manage risks",
        "Manage issues",
        "Manage dependencies",
        "Coordinate stakeholders",
        "Track project scope",
        "Manage change requests",
        "Monitor budget when applicable",
        "Coordinate meetings",
        "Maintain project status reporting",
        "Escalate blockers",
        "Coordinate delivery",
        "Manage project closure",
        "Document lessons learned",
    ]

    print("\nPROJECT MANAGER RESPONSIBILITIES")
    print("=" * 40)

    for number, responsibility in enumerate(responsibilities, start=1):
        print(f"{number:02d}. {responsibility}")


"""
===============================================================================
SECTION 6: PROJECT MANAGER OUTPUTS
===============================================================================

Typical project outputs include:

- Project charter
- Project plan
- Schedule
- Milestone plan
- RAID log
- Risk register
- Issue log
- Dependency tracker
- Status reports
- Resource plan
- Communication plan
- Change log
- Project closure report
- Lessons learned

RAID is commonly used as:

R = Risks
A = Assumptions
I = Issues
D = Dependencies

Example:

Risk:
    API integration may take longer than expected.

Assumption:
    Vendor will provide API documentation by Monday.

Issue:
    Test environment is currently unavailable.

Dependency:
    Mobile application testing depends on backend API completion.


===============================================================================
SECTION 7: PROGRAM MANAGEMENT
===============================================================================

Program management operates at a higher coordination level.

Imagine:

DIGITAL TRANSFORMATION PROGRAM
|
+-- Mobile Banking Project
|
+-- Core Banking Modernization Project
|
+-- Cybersecurity Project
|
+-- Data Migration Project
|
+-- Customer Onboarding Project

Each project can succeed independently while the overall transformation
still fails.

Why?

Because projects can have dependencies.

Example:

Data Migration
       |
       v
Core Banking Modernization
       |
       v
Mobile Banking
       |
       v
Customer Onboarding

The Program Manager ensures these efforts work together.

Program management focuses on:

- Strategic alignment
- Cross-project dependencies
- Benefits realization
- Program risks
- Governance
- Resource conflicts
- Executive communication
- Inter-project coordination
- Organizational change
"""


def program_manager_responsibilities():
    responsibilities = [
        "Align initiatives with strategic objectives",
        "Coordinate multiple projects",
        "Manage cross-project dependencies",
        "Identify program-level risks",
        "Resolve resource conflicts",
        "Track benefits realization",
        "Establish program governance",
        "Coordinate executive stakeholders",
        "Create program-level reporting",
        "Monitor overall program health",
        "Coordinate major decisions",
        "Manage strategic changes",
        "Coordinate transformation activities",
        "Maintain program roadmap",
        "Escalate issues requiring executive intervention",
    ]

    print("\nPROGRAM MANAGER RESPONSIBILITIES")
    print("=" * 40)

    for number, responsibility in enumerate(responsibilities, start=1):
        print(f"{number:02d}. {responsibility}")


"""
===============================================================================
SECTION 8: PRODUCT vs PROJECT vs PROGRAM
===============================================================================
"""


def compare_three_disciplines():
    comparison = {
        "Primary question": {
            "Product": "What should we build and why?",
            "Project": "How do we deliver this initiative successfully?",
            "Program": "How do multiple initiatives work together to achieve strategic benefits?",
        },

        "Primary focus": {
            "Product": "Customer and business value",
            "Project": "Delivery",
            "Program": "Strategic coordination and benefits",
        },

        "Nature": {
            "Product": "Continuous",
            "Project": "Temporary",
            "Program": "Usually longer-term and coordinated",
        },

        "Typical horizon": {
            "Product": "Months to years",
            "Project": "Weeks to years",
            "Program": "Months to several years",
        },

        "Success": {
            "Product": "Business and customer outcomes",
            "Project": "Successful delivery against agreed objectives",
            "Program": "Strategic outcomes and benefits realization",
        },

        "Typical artifacts": {
            "Product": "Vision, roadmap, backlog, requirements",
            "Project": "Plan, schedule, RAID, milestones, status reports",
            "Program": "Program roadmap, dependency map, governance, benefits plan",
        },
    }

    headers = ["Dimension", "Product", "Project", "Program"]

    print("\nPRODUCT vs PROJECT vs PROGRAM")
    print("=" * 90)

    print(
        f"{headers[0]:<25}"
        f"{headers[1]:<25}"
        f"{headers[2]:<25}"
        f"{headers[3]:<25}"
    )

    print("-" * 100)

    for dimension, values in comparison.items():
        print(
            f"{dimension:<25}"
            f"{values['Product']:<25}"
            f"{values['Project']:<25}"
            f"{values['Program']:<25}"
        )


"""
===============================================================================
SECTION 9: PRODUCT MANAGER vs PROJECT MANAGER vs PROGRAM MANAGER
===============================================================================

PRODUCT MANAGER
---------------
Primary ownership:
    Product value and direction

Key question:
    Are we solving the right problem?

Typical KPIs:
    Activation
    Retention
    Conversion
    Engagement
    Revenue
    Customer satisfaction
    Adoption
    Churn
    Product usage

PROJECT MANAGER
---------------
Primary ownership:
    Project execution

Key question:
    Are we delivering the agreed initiative effectively?

Typical KPIs:
    Schedule variance
    Budget variance
    Scope stability
    Milestone completion
    Defect rate
    Delivery predictability
    Resource utilization
    Risk exposure

PROGRAM MANAGER
---------------
Primary ownership:
    Program-level outcomes and coordination

Key question:
    Are all related initiatives collectively producing strategic value?

Typical KPIs:
    Benefits realization
    Strategic milestone achievement
    Cross-project dependency resolution
    Program risk
    Resource utilization
    Business outcome achievement
    Program health


===============================================================================
SECTION 10: OWNERSHIP MODEL
===============================================================================
"""


def ownership_model():
    model = {
        "Product Manager": [
            "Product vision",
            "Product strategy",
            "Customer problem",
            "Feature prioritization",
            "Product roadmap",
            "Product outcomes",
        ],

        "Project Manager": [
            "Project schedule",
            "Delivery coordination",
            "Project risks",
            "Project issues",
            "Project dependencies",
            "Project execution",
        ],

        "Program Manager": [
            "Program alignment",
            "Cross-project dependencies",
            "Program governance",
            "Program risks",
            "Benefits realization",
            "Strategic coordination",
        ],
    }

    print("\nOWNERSHIP MODEL")
    print("=" * 60)

    for role, responsibilities in model.items():
        print(f"\n{role}")
        print("-" * len(role))

        for responsibility in responsibilities:
            print(f"  - {responsibility}")


"""
===============================================================================
SECTION 11: WHAT EACH ROLE OWNS VS INFLUENCES
===============================================================================

Ownership does not mean working alone.

A Product Manager may own product prioritization while engineering owns
technical implementation.

A Project Manager may own project coordination while functional managers
own individual team members.

A Program Manager may own program governance while project managers own
individual projects.

This is why organizations often use RACI.

RACI:

R = Responsible
A = Accountable
C = Consulted
I = Informed
"""


def raci_example():
    activities = {
        "Define product vision": {
            "Product Manager": "A/R",
            "Project Manager": "C",
            "Program Manager": "C",
            "Engineering": "C",
        },

        "Create project schedule": {
            "Product Manager": "C",
            "Project Manager": "A/R",
            "Program Manager": "C",
            "Engineering": "C",
        },

        "Resolve cross-project dependency": {
            "Product Manager": "C",
            "Project Manager": "R",
            "Program Manager": "A",
            "Engineering": "C",
        },

        "Define technical architecture": {
            "Product Manager": "C",
            "Project Manager": "C",
            "Program Manager": "I",
            "Engineering": "A/R",
        },
    }

    print("\nRACI EXAMPLE")
    print("=" * 80)

    for activity, roles in activities.items():
        print(f"\nActivity: {activity}")

        for role, responsibility in roles.items():
            print(f"  {role:<20}: {responsibility}")


"""
===============================================================================
SECTION 12: TIMELINES
===============================================================================

Different management disciplines operate at different time horizons.

PRODUCT
-------
Usually continuous.

Example:
    Product vision: 1-3 years
    Strategic roadmap: 6-18 months
    Feature roadmap: 1-6 months
    Sprint planning: 1-4 weeks

PROJECT
-------
Usually finite.

Example:
    Project:
        January -> June

    Milestones:
        Requirements
        Design
        Development
        Testing
        Deployment
        Closure

PROGRAM
-------
Usually broader.

Example:
    2026 -> 2028

    Program:
        Project A
        Project B
        Project C
        Project D

The exact durations vary by organization.


===============================================================================
SECTION 13: PRODUCT ROADMAP
===============================================================================

A product roadmap communicates product direction.

A roadmap answers:

- Where are we going?
- Why are we going there?
- What outcomes do we expect?
- What major capabilities are planned?
- What is the relative priority?

Modern product teams increasingly avoid treating roadmaps as rigid promises.

Instead of:

    "Feature X will definitely ship on March 15."

An outcome-oriented roadmap might say:

    Q1:
        Improve customer onboarding

    Q2:
        Increase payment success rate

    Q3:
        Expand self-service capabilities

This keeps strategy visible while allowing implementation details to change.


===============================================================================
SECTION 14: PRODUCT BACKLOG
===============================================================================

A backlog is a prioritized collection of work.

Possible backlog items:

- User stories
- Bugs
- Technical improvements
- Research
- Experiments
- Features
- Security work
- Performance improvements

Example:

"""


def product_backlog_example():
    backlog = [
        {
            "id": "P-101",
            "item": "Simplify customer onboarding",
            "priority": "High",
            "type": "Feature",
        },
        {
            "id": "P-102",
            "item": "Add biometric authentication",
            "priority": "High",
            "type": "Feature",
        },
        {
            "id": "P-103",
            "item": "Improve API response time",
            "priority": "Medium",
            "type": "Technical",
        },
        {
            "id": "P-104",
            "item": "Fix profile update error",
            "priority": "Critical",
            "type": "Bug",
        },
    ]

    print("\nPRODUCT BACKLOG")
    print("=" * 80)

    for item in backlog:
        print(
            f"{item['id']} | "
            f"{item['priority']:<8} | "
            f"{item['type']:<10} | "
            f"{item['item']}"
        )


"""
===============================================================================
SECTION 15: USER STORIES
===============================================================================

A common user-story structure:

As a <type of user>,
I want <capability>,
so that <benefit>.

Example:

As a customer,
I want to reset my password through my registered email,
so that I can regain access to my account without contacting support.

Acceptance criteria define what must be true for the story to be accepted.

Example:

1. User enters registered email.
2. System validates email.
3. Reset link is generated.
4. Link expires after the defined period.
5. User can create a new password.
6. Confirmation is displayed.


===============================================================================
SECTION 16: PROJECT PLAN
===============================================================================

A project plan converts objectives into executable work.

Example:

"""


def project_plan_example():
    project = [
        ("Requirements", "Week 1", "Product + Business"),
        ("Architecture", "Week 2", "Engineering"),
        ("UX Design", "Week 2-3", "Design"),
        ("Development", "Week 3-8", "Engineering"),
        ("Testing", "Week 7-9", "QA"),
        ("User Acceptance Testing", "Week 9", "Business"),
        ("Deployment", "Week 10", "Engineering + Operations"),
        ("Project Closure", "Week 11", "Project Manager"),
    ]

    print("\nPROJECT PLAN")
    print("=" * 70)

    for activity, timeline, owner in project:
        print(f"{activity:<30} | {timeline:<12} | {owner}")


"""
===============================================================================
SECTION 17: MILESTONES
===============================================================================

A milestone is a significant checkpoint.

Examples:

- Requirements approved
- Architecture approved
- MVP completed
- Testing completed
- UAT approved
- Production deployment
- Program phase completed

Milestones are useful because executives usually do not need every task.

They need visibility into meaningful checkpoints.


===============================================================================
SECTION 18: KPIs
===============================================================================

KPI = Key Performance Indicator.

The most important principle:

Do not confuse ACTIVITY with OUTCOME.

Activity:
    Number of features developed.

Output:
    Feature released.

Outcome:
    Customer activation increased.

Business impact:
    Revenue increased.

Example product KPI categories:

ACQUISITION
    Website conversion
    Signups

ACTIVATION
    First successful action
    Onboarding completion

ENGAGEMENT
    Daily active users
    Monthly active users
    Session frequency

RETENTION
    Cohort retention
    Churn

REVENUE
    ARR
    MRR
    Average revenue per user
    Conversion

SATISFACTION
    NPS
    CSAT

QUALITY
    Crash rate
    Defect rate
    Support tickets

PERFORMANCE
    Latency
    Availability
    Error rate


===============================================================================
SECTION 19: PROJECT KPIs
===============================================================================

Project KPIs frequently include:

Schedule variance
Budget variance
Scope change
Milestone completion
Defect density
Risk exposure
Issue aging
Resource utilization
Delivery predictability

A project can be considered operationally successful if it delivers the
agreed scope within acceptable constraints.

But project success and product success are NOT identical.

Example:

A team may deliver an application:

    On time
    On budget
    With low defect rates

Yet customers may not use it.

Project:
    Successful delivery.

Product:
    Possible failure.

This distinction is extremely important.


===============================================================================
SECTION 20: PROGRAM KPIs
===============================================================================

Program-level metrics can include:

- Benefits realization
- Strategic objective achievement
- Cross-project dependency resolution
- Program milestone achievement
- Overall risk exposure
- Budget utilization
- Resource capacity
- Business transformation metrics

Example:

Program objective:
    Reduce customer onboarding time by 50%.

Projects:

    Project A:
        Mobile onboarding

    Project B:
        Identity verification

    Project C:
        Data integration

    Project D:
        Customer support automation

The Program Manager tracks whether the collection of initiatives produces
the intended 50% improvement.


===============================================================================
SECTION 21: PRIORITIZATION
===============================================================================

Product Managers constantly face:

    Feature A
    Feature B
    Feature C
    Feature D

But resources are limited.

Therefore prioritization is essential.

Common frameworks:

1. RICE
2. MoSCoW
3. Value vs Effort
4. WSJF
5. Kano Model
6. Opportunity Scoring
7. Cost of Delay

RICE:

R = Reach
I = Impact
C = Confidence
E = Effort

Formula:

RICE = (Reach * Impact * Confidence) / Effort
"""


def calculate_rice(reach, impact, confidence, effort):
    if effort <= 0:
        raise ValueError("Effort must be greater than zero.")

    return (reach * impact * confidence) / effort


def demonstrate_rice():
    features = {
        "Feature A": (10000, 3, 0.8, 20),
        "Feature B": (5000, 2, 0.9, 10),
        "Feature C": (15000, 1, 0.7, 40),
    }

    print("\nRICE PRIORITIZATION")
    print("=" * 60)

    results = []

    for name, values in features.items():
        score = calculate_rice(*values)
        results.append((name, score))

    results.sort(key=lambda x: x[1], reverse=True)

    for name, score in results:
        print(f"{name:<15} RICE Score = {score:.2f}")


"""
===============================================================================
SECTION 22: OKRs
===============================================================================

OKR = Objectives and Key Results.

Objective:
    What meaningful outcome do we want?

Key Results:
    How will we know we achieved it?

Example:

Objective:
    Make customer onboarding dramatically easier.

Key Results:
    KR1: Increase onboarding completion from 55% to 75%.
    KR2: Reduce average onboarding time from 12 minutes to 6 minutes.
    KR3: Reduce onboarding-related support tickets by 30%.

Relationship:

STRATEGY
   |
   v
OBJECTIVE
   |
   v
KEY RESULTS
   |
   v
PRODUCT INITIATIVES
   |
   v
PROJECTS / EPICS / TASKS
   |
   v
MEASURABLE OUTCOMES


===============================================================================
SECTION 23: AGILE
===============================================================================

Agile is an approach centered around:

- Iterative development
- Customer feedback
- Adaptability
- Incremental delivery
- Collaboration
- Continuous learning

Agile does NOT simply mean:

    "Use Jira."

Jira is a tool.

Agile is a way of organizing and managing work.

Common Agile frameworks include:

- Scrum
- Kanban
- Extreme Programming
- Scaled Agile approaches
- Hybrid approaches


===============================================================================
SECTION 24: SCRUM
===============================================================================

Scrum commonly includes:

Roles:
    Product Owner
    Scrum Master
    Developers

Artifacts:
    Product Backlog
    Sprint Backlog
    Increment

Events:
    Sprint
    Sprint Planning
    Daily Scrum
    Sprint Review
    Sprint Retrospective

Important distinction:

Product Manager and Product Owner are not automatically the same role.

Some organizations combine them.

Other organizations separate strategic product management from tactical
product ownership.


===============================================================================
SECTION 25: KANBAN
===============================================================================

Kanban visualizes workflow.

Example:

BACKLOG
   |
   v
TO DO
   |
   v
IN PROGRESS
   |
   v
CODE REVIEW
   |
   v
TESTING
   |
   v
DONE

Kanban emphasizes:

- Flow
- Work-in-progress limits
- Cycle time
- Throughput
- Continuous improvement


===============================================================================
SECTION 26: JIRA
===============================================================================

Jira is a work-management and issue-tracking platform widely used by
software and product teams.

Common Jira concepts:

PROJECT
    Container for related work.

ISSUE
    Individual work item.

EPIC
    Large body of work.

STORY
    User-centered requirement.

TASK
    General work item.

BUG
    Defect.

SUBTASK
    Smaller unit of an issue.

SPRINT
    Timeboxed development period in Scrum.

BACKLOG
    Prioritized list of work.

BOARD
    Visual representation of workflow.

WORKFLOW
    States through which an issue moves.

Typical workflow:

TO DO
  ->
IN PROGRESS
  ->
IN REVIEW
  ->
TESTING
  ->
DONE


===============================================================================
SECTION 27: JIRA EXAMPLE
===============================================================================
"""


def jira_example():
    jira_issues = [
        {
            "key": "APP-101",
            "type": "Epic",
            "summary": "Customer Onboarding",
            "status": "In Progress",
        },
        {
            "key": "APP-102",
            "type": "Story",
            "summary": "Create customer profile",
            "status": "Done",
        },
        {
            "key": "APP-103",
            "type": "Story",
            "summary": "Verify customer identity",
            "status": "In Progress",
        },
        {
            "key": "APP-104",
            "type": "Bug",
            "summary": "OTP validation failure",
            "status": "Testing",
        },
    ]

    print("\nJIRA WORK ITEMS")
    print("=" * 90)

    for issue in jira_issues:
        print(
            f"{issue['key']:<10} | "
            f"{issue['type']:<8} | "
            f"{issue['status']:<15} | "
            f"{issue['summary']}"
        )


"""
===============================================================================
SECTION 28: JIRA FOR PRODUCT MANAGERS
===============================================================================

Product Managers may use Jira to:

- Manage backlog
- Prioritize stories
- Create epics
- Track feature development
- Define acceptance criteria
- Monitor sprint progress
- Connect work to product goals
- Track bugs
- Coordinate with engineering

A Product Manager should not treat Jira as the product strategy itself.

A backlog is not a strategy.

Strategy explains:

    WHERE are we going?
    WHY are we going there?
    WHICH outcomes matter?

Jira helps organize and track execution.


===============================================================================
SECTION 29: JIRA FOR PROJECT MANAGERS
===============================================================================

Project Managers may use Jira to:

- Track project work
- Monitor milestones
- Track blockers
- Track dependencies
- Monitor status
- Create dashboards
- Report progress
- Coordinate teams

Jira can become an operational control center for software projects.


===============================================================================
SECTION 30: JIRA FOR PROGRAM MANAGERS
===============================================================================

Program Managers may use Jira to:

- Track multiple projects
- Monitor cross-project dependencies
- Aggregate status
- Monitor strategic initiatives
- Identify bottlenecks
- Track risks and issues
- Create portfolio-level visibility

At larger organizations, Jira data may be combined with other planning,
reporting or portfolio-management systems.


===============================================================================
SECTION 31: CONFLUENCE
===============================================================================

Confluence is a collaboration and documentation platform.

Think:

Jira = Work tracking

Confluence = Knowledge and documentation

Common Confluence content:

- Product requirements
- Meeting notes
- Architecture documentation
- Decision records
- Project plans
- Runbooks
- Strategy documents
- Onboarding documentation
- Process documentation
- Release notes
- Retrospectives
- Program documentation


===============================================================================
SECTION 32: JIRA + CONFLUENCE
===============================================================================

A useful mental model:

CONFLUENCE
    |
    | Why?
    | Strategy
    | Requirements
    | Decisions
    | Documentation
    |
    v
JIRA
    |
    | What work?
    | Who?
    | Status?
    | Priority?
    | Sprint?
    |
    v
DELIVERY
    |
    v
METRICS
    |
    v
LEARNING
    |
    v
CONFLUENCE / PRODUCT STRATEGY

Example:

Confluence:
    "Customer onboarding strategy"

        |
        v

Jira Epic:
    "Customer Onboarding Improvement"

        |
        +-- Story: Simplify registration
        +-- Story: Improve OTP flow
        +-- Story: Add identity verification
        +-- Bug: Fix verification failure

        |
        v

Analytics:
    Completion rate improves from 55% to 72%.


===============================================================================
SECTION 33: PRODUCT LIFE CYCLE
===============================================================================

A product can move through:

1. Discovery
2. Validation
3. Development
4. Launch
5. Growth
6. Maturity
7. Decline
8. Retirement

Product management exists across the entire lifecycle.

Project management may be used for individual initiatives inside that lifecycle.

Program management may coordinate multiple transformation initiatives
across the organization.


===============================================================================
SECTION 34: DISCOVERY vs DELIVERY
===============================================================================

Product teams often separate:

DISCOVERY
    What should we build?

DELIVERY
    How do we build and release it?

Discovery activities:

- Customer interviews
- Market research
- Prototyping
- Usability testing
- Data analysis
- Experimentation

Delivery activities:

- Engineering
- Testing
- Deployment
- Release management
- Monitoring

Strong product organizations connect discovery and delivery continuously.


===============================================================================
SECTION 35: STAKEHOLDER MANAGEMENT
===============================================================================

Stakeholders may include:

- Customers
- Executives
- Engineering
- Design
- Sales
- Marketing
- Finance
- Legal
- Security
- Operations
- Vendors
- Regulators

Different roles communicate differently.

Product Manager:
    "This customer problem has high strategic value."

Project Manager:
    "The testing milestone is delayed by one week because of
     environment availability."

Program Manager:
    "Three projects share the same integration dependency and require
     executive prioritization."


===============================================================================
SECTION 36: DEPENDENCY MANAGEMENT
===============================================================================

Dependencies are especially important in project and program management.

Example:

Project A:
    Backend API

Project B:
    Mobile Application

Dependency:

    Mobile Application
          |
          v
    Backend API

If Project A is delayed, Project B may be delayed.

A program manager sees the dependency across the entire portfolio.

Dependency categories:

- Technical
- Resource
- Vendor
- Data
- Regulatory
- Organizational
- Schedule
- Financial


===============================================================================
SECTION 37: RISK MANAGEMENT
===============================================================================

Risk is an uncertain event that could affect objectives.

Risk example:

    "The external payment provider may not complete integration on time."

A simple risk model:

Risk Score = Probability × Impact

"""


def calculate_risk_score(probability, impact):
    if not 1 <= probability <= 5:
        raise ValueError("Probability must be between 1 and 5.")

    if not 1 <= impact <= 5:
        raise ValueError("Impact must be between 1 and 5.")

    return probability * impact


def demonstrate_risk():
    risks = [
        ("Vendor delay", 4, 5),
        ("Minor UI issue", 2, 2),
        ("Security vulnerability", 3, 5),
        ("Resource shortage", 4, 4),
    ]

    print("\nRISK REGISTER")
    print("=" * 70)

    for name, probability, impact in risks:
        score = calculate_risk_score(probability, impact)

        if score >= 15:
            level = "HIGH"
        elif score >= 8:
            level = "MEDIUM"
        else:
            level = "LOW"

        print(
            f"{name:<25} "
            f"Probability={probability} "
            f"Impact={impact} "
            f"Score={score:<2} "
            f"Level={level}"
        )


"""
===============================================================================
SECTION 38: SCOPE MANAGEMENT
===============================================================================

Scope describes what is included and excluded.

Example project:

IN SCOPE
    Customer registration
    OTP verification
    Profile creation

OUT OF SCOPE
    International payments
    Loyalty program
    Cryptocurrency integration

Scope creep occurs when uncontrolled work keeps getting added.

Example:

Original project:
    Build login system.

Requests:
    Add social login.
    Add biometric login.
    Add voice login.
    Add passwordless authentication.
    Add AI fraud detection.

Every request may be valuable.

The problem is uncontrolled expansion without corresponding changes to
time, budget, resources or priorities.


===============================================================================
SECTION 39: CHANGE MANAGEMENT
===============================================================================

Change is not automatically bad.

Good management asks:

What is changing?

Why?

What value does it create?

What does it cost?

What dependencies are affected?

What risks change?

What timeline changes?

A project manager may manage formal change requests.

A product manager may reprioritize product scope.

A program manager may assess the effect of changes across multiple projects.


===============================================================================
SECTION 40: PRODUCT STRATEGY
===============================================================================

A product strategy connects:

Business goals
    |
    v
Customer problems
    |
    v
Strategic choices
    |
    v
Product initiatives
    |
    v
Metrics

A strategy should make choices.

If everything is a priority,
nothing is a priority.

A strong product strategy answers:

1. Which customers?
2. Which problems?
3. Why now?
4. Why us?
5. What differentiates us?
6. What will we not do?
7. How will we measure success?


===============================================================================
SECTION 41: PRODUCT ROADMAP vs PROJECT PLAN
===============================================================================

PRODUCT ROADMAP
----------------
Strategic direction.

Example:

Q1:
    Improve onboarding

Q2:
    Improve payments

Q3:
    Expand analytics

PROJECT PLAN
------------
Execution schedule.

Example:

Week 1:
    Requirements

Week 2:
    Architecture

Week 3:
    Development begins

Week 6:
    Testing

Week 8:
    Deployment

A roadmap communicates strategic intent.

A project plan communicates execution.


===============================================================================
SECTION 42: PRODUCT ROADMAP vs PROGRAM ROADMAP
===============================================================================

Product roadmap:
    Direction of one product.

Program roadmap:
    Coordination of multiple initiatives.

Example:

Product roadmap:
    Mobile App
        Q1: Login
        Q2: Payments
        Q3: Analytics

Program roadmap:

Digital Transformation
    |
    +-- Mobile App
    +-- Data Platform
    +-- Cybersecurity
    +-- Cloud Migration
    +-- Customer Experience


===============================================================================
SECTION 43: PRODUCT METRICS FUNNEL
===============================================================================

A product funnel may look like:

Visitors
   |
   v
Signups
   |
   v
Activated Users
   |
   v
Engaged Users
   |
   v
Retained Users
   |
   v
Paying Customers
   |
   v
Advocates

Each stage can have different metrics.

Example:

Conversion Rate = Conversions / Visitors


===============================================================================
SECTION 44: BASIC METRIC CALCULATIONS
===============================================================================
"""


def conversion_rate(conversions, total_users):
    if total_users <= 0:
        raise ValueError("Total users must be greater than zero.")

    return conversions / total_users


def retention_rate(retained_users, starting_users):
    if starting_users <= 0:
        raise ValueError("Starting users must be greater than zero.")

    return retained_users / starting_users


def demonstrate_product_metrics():
    visitors = 10000
    signups = 1800
    retained_users = 900

    signup_conversion = conversion_rate(signups, visitors)
    retention = retention_rate(retained_users, signups)

    print("\nPRODUCT METRICS")
    print("=" * 50)
    print(f"Visitors: {visitors}")
    print(f"Signups: {signups}")
    print(f"Signup conversion: {signup_conversion:.2%}")
    print(f"Retained users: {retained_users}")
    print(f"Signup retention: {retention:.2%}")


"""
===============================================================================
SECTION 45: LEADING vs LAGGING INDICATORS
===============================================================================

Leading indicators:
    Predict future performance.

Examples:
    Trial usage
    Feature adoption
    Product engagement
    Customer interviews completed

Lagging indicators:
    Show what already happened.

Examples:
    Revenue
    Churn
    Profit
    Customer retention

Good management uses both.


===============================================================================
SECTION 46: OUTPUT vs OUTCOME vs IMPACT
===============================================================================

OUTPUT
------
What did we produce?

Example:
    Released mobile onboarding.

OUTCOME
-------
What changed because of it?

Example:
    More customers completed onboarding.

IMPACT
------
What broader business result occurred?

Example:
    Customer acquisition cost decreased and revenue increased.

Hierarchy:

Activity
    ->
Output
    ->
Outcome
    ->
Business Impact

This distinction is one of the most important concepts in modern
product management.


===============================================================================
SECTION 47: PRODUCT-MARKET FIT
===============================================================================

Product-market fit means a product strongly satisfies a meaningful market
need.

Possible signals include:

- Strong retention
- Organic growth
- Repeat usage
- Customer willingness to pay
- Low churn
- Positive customer feedback
- Referral behavior

There is no single universal KPI that proves product-market fit.


===============================================================================
SECTION 48: MVP
===============================================================================

MVP = Minimum Viable Product.

An MVP is the smallest practical version of a solution that allows a team
to learn whether an important hypothesis is valid.

MVP does NOT mean:

    "Build a bad product."

It means:

    "Reduce unnecessary investment while maximizing learning."

Example:

Hypothesis:
    Customers want automated expense categorization.

Instead of building a complete AI financial platform:

MVP:
    Upload statement
    Categorize transactions
    Show categorized result

Measure:

    Adoption
    Accuracy
    Repeat usage
    Customer willingness to pay


===============================================================================
SECTION 49: PRODUCT EXPERIMENTATION
===============================================================================

A product experiment has:

Hypothesis
    |
    v
Experiment
    |
    v
Metric
    |
    v
Result
    |
    v
Decision

Example:

Hypothesis:
    Simplifying signup from 8 fields to 4 fields will improve completion.

Experiment:
    A/B test simplified form.

Metric:
    Signup completion rate.

Decision:
    Roll out if statistically and operationally meaningful.


===============================================================================
SECTION 50: PROJECT HEALTH
===============================================================================

Project health is often summarized using:

GREEN
    On track.

AMBER
    Risk or concern exists.

RED
    Significant issue requiring intervention.

A good status report should not simply say:

    "Project is 80% complete."

Instead explain:

    Overall status
    Achievements
    Risks
    Issues
    Dependencies
    Decisions required
    Next milestones


===============================================================================
SECTION 51: PROGRAM GOVERNANCE
===============================================================================

Governance defines:

- Who decides?
- Who approves?
- Who escalates?
- What information is reported?
- How often are decisions made?
- What thresholds trigger escalation?

Example:

Program Steering Committee:
    Monthly

Program Review:
    Weekly

Project Review:
    Weekly

Delivery Team:
    Daily


===============================================================================
SECTION 52: DECISION MANAGEMENT
===============================================================================

Large programs often fail because decisions are delayed.

A useful decision record contains:

Decision
Reason
Options considered
Decision maker
Date
Impact
Dependencies

This can be documented in Confluence.

Example:

Decision:
    Use existing identity service.

Reason:
    Reduces implementation time.

Alternatives:
    Build new identity service.

Impact:
    Lower development effort but increased dependency on existing platform.


===============================================================================
SECTION 53: ADVANCED CONCEPT: COST OF DELAY
===============================================================================

Cost of Delay estimates the economic consequence of waiting.

If delaying a feature causes:

    Lost revenue
    Lost customers
    Increased operational costs
    Regulatory exposure

then the feature may have high Cost of Delay.

A simplified conceptual model:

Cost of Delay =
    Lost Value
    + Increased Cost
    + Strategic Cost
    + Risk Cost


===============================================================================
SECTION 54: ADVANCED CONCEPT: WSJF
===============================================================================

WSJF = Weighted Shortest Job First.

A simplified formula:

WSJF = Cost of Delay / Job Size

Cost of Delay can incorporate:

    User-business value
    Time criticality
    Risk reduction / opportunity enablement

Higher WSJF generally indicates greater economic priority.


===============================================================================
SECTION 55: ADVANCED CONCEPT: CRITICAL PATH
===============================================================================

The critical path is the sequence of dependent activities that determines
the minimum possible project duration.

Example:

A -> B -> C -> D

If any critical activity is delayed, the overall project may be delayed.

Non-critical tasks may have slack.

Project managers use critical-path thinking to identify schedule sensitivity.


===============================================================================
SECTION 56: ADVANCED CONCEPT: CRITICAL CHAIN
===============================================================================

Critical Chain Project Management considers resource constraints in addition
to task dependencies.

This matters because a theoretically available schedule can fail when:

    Person A
        |
        +--> Project 1
        |
        +--> Project 2
        |
        +--> Project 3

The same resource is overloaded.

Program management is especially concerned with such cross-project
resource conflicts.


===============================================================================
SECTION 57: ADVANCED CONCEPT: PORTFOLIO vs PROGRAM
===============================================================================

PROGRAM
-------
Related initiatives managed together.

PORTFOLIO
---------
Collection of investments managed to achieve strategic objectives.

Example:

Technology Portfolio
|
+-- Digital Banking Program
|   +-- Mobile App Project
|   +-- API Project
|
+-- Cybersecurity Program
|   +-- IAM Project
|   +-- SOC Project
|
+-- Data Program
    +-- Data Lake Project
    +-- Analytics Project

Portfolio management asks:

    Are we investing in the right things?

Program management asks:

    Are these related initiatives working together effectively?

Project management asks:

    Are we delivering this initiative successfully?

Product management asks:

    Are we creating valuable solutions for customers and the business?


===============================================================================
SECTION 58: OPERATING MODEL
===============================================================================

A mature organization can connect all disciplines:

BUSINESS STRATEGY
       |
       v
PORTFOLIO
       |
       v
PROGRAMS
       |
       v
PRODUCTS
       |
       v
PROJECTS / INITIATIVES
       |
       v
EPICS
       |
       v
STORIES / TASKS
       |
       v
DELIVERY
       |
       v
PRODUCT METRICS
       |
       v
LEARNING
       |
       +---------------------> STRATEGY


===============================================================================
SECTION 59: PRACTICAL CASE STUDY
===============================================================================

CASE STUDY:
    A company wants to launch a digital banking platform.

BUSINESS OBJECTIVE:
    Increase digital customer adoption.

PRODUCT MANAGER:
    Identifies customer problems.

Product initiatives:
    - Faster onboarding
    - Better payment experience
    - Personalized dashboard

PROJECT MANAGER:
    Coordinates delivery of the onboarding project.

Project:
    Digital Onboarding Release

Tasks:
    Requirements
    UX
    Engineering
    Testing
    Deployment

PROGRAM MANAGER:
    Coordinates the broader digital transformation.

Program projects:
    - Mobile application
    - API modernization
    - Identity platform
    - Data platform
    - Cybersecurity modernization

PRODUCT KPI:
    Digital adoption rate

PROJECT KPI:
    Release delivered according to agreed objectives

PROGRAM KPI:
    Overall digital transformation benefits realized


===============================================================================
SECTION 60: WHO SHOULD YOU TALK TO?
===============================================================================

If the question is:

    "Should we build this feature?"

Talk to:
    Product Manager

If the question is:

    "When will this project be delivered?"

Talk to:
    Project Manager

If the question is:

    "How do these five initiatives fit together?"

Talk to:
    Program Manager

If the question is:

    "Are we achieving the organization's investment strategy?"

Think:
    Portfolio Management


===============================================================================
SECTION 61: COMMON MISCONCEPTIONS
===============================================================================

MISCONCEPTION 1:
    Product Manager = Project Manager

REALITY:
    Their goals and accountability differ.

MISCONCEPTION 2:
    Product Manager manages developers.

REALITY:
    Product Manager provides product direction and prioritization.
    Engineering leaders manage technical execution and engineering teams.

MISCONCEPTION 3:
    Project Manager decides what product features should exist.

REALITY:
    That is usually a product/business decision, although the Project
    Manager contributes delivery constraints and information.

MISCONCEPTION 4:
    Program Manager is simply a senior Project Manager.

REALITY:
    Program management has a broader strategic and cross-project focus.

MISCONCEPTION 5:
    Jira is project management.

REALITY:
    Jira is a tool that can support Agile, project, product and program
    workflows.

MISCONCEPTION 6:
    Confluence is just a document repository.

REALITY:
    It can function as a shared knowledge and decision-management system.


===============================================================================
SECTION 62: HOW THE THREE ROLES COLLABORATE
===============================================================================

PRODUCT MANAGER
    |
    | Defines problem, value and priority
    v
PROJECT MANAGER
    |
    | Coordinates execution
    v
DELIVERY TEAM
    |
    | Produces solution
    v
CUSTOMER
    |
    | Provides feedback
    v
PRODUCT MANAGER


PROGRAM MANAGER sits across related initiatives:

             PROGRAM MANAGER
             /      |       \
            /       |        \
     PROJECT A  PROJECT B  PROJECT C
         |          |          |
      Teams       Teams       Teams


===============================================================================
SECTION 63: DECISION MATRIX
===============================================================================
"""


def decision_matrix():
    questions = [
        ("What should we build?", "Product Manager"),
        ("Why should we build it?", "Product Manager"),
        ("Which feature has highest customer value?", "Product Manager"),
        ("When will this project finish?", "Project Manager"),
        ("Who owns the delivery schedule?", "Project Manager"),
        ("What are the project risks?", "Project Manager"),
        ("How do multiple projects depend on each other?", "Program Manager"),
        ("Are strategic benefits being realized?", "Program Manager"),
        ("Which investments should the company fund?", "Portfolio Leadership"),
    ]

    print("\nDECISION MATRIX")
    print("=" * 85)

    for question, role in questions:
        print(f"{question:<60} -> {role}")


"""
===============================================================================
SECTION 64: CAREER SKILL MAP
===============================================================================

PRODUCT MANAGER SKILLS
----------------------
Customer discovery
Product strategy
Analytics
Prioritization
Roadmapping
Communication
Experimentation
Business modeling
UX understanding
Technical literacy

PROJECT MANAGER SKILLS
----------------------
Planning
Scheduling
Risk management
Stakeholder management
Budgeting
Dependency management
Communication
Execution
Governance
Reporting

PROGRAM MANAGER SKILLS
----------------------
Strategic thinking
Systems thinking
Cross-functional leadership
Dependency management
Governance
Risk management
Executive communication
Benefits realization
Resource planning
Organizational change

JIRA SKILLS
-----------
Projects
Issues
Epics
Stories
Tasks
Boards
Sprints
Backlogs
Workflows
Dashboards
Filters
Reports

CONFLUENCE SKILLS
-----------------
Pages
Spaces
Templates
Meeting notes
Decision logs
Requirements
Architecture documentation
Knowledge management
Project documentation
Product documentation


===============================================================================
SECTION 65: INTERVIEW QUESTIONS
===============================================================================
"""


def interview_questions():
    questions = [
        "What is the difference between a product, project and program?",
        "What does a Product Manager own?",
        "What does a Project Manager own?",
        "What does a Program Manager own?",
        "How is product success measured?",
        "How is project success measured?",
        "How is program success measured?",
        "What is a product roadmap?",
        "What is a project plan?",
        "What is a program roadmap?",
        "What is the difference between an output and an outcome?",
        "What is RACI?",
        "What is RAID?",
        "What is scope creep?",
        "What is a product backlog?",
        "What is an epic?",
        "What is a user story?",
        "What is an acceptance criterion?",
        "What is a sprint?",
        "What is Kanban?",
        "What is Jira?",
        "What is Confluence?",
        "How do Jira and Confluence work together?",
        "What is RICE prioritization?",
        "What are OKRs?",
        "What is a KPI?",
        "What is the critical path?",
        "What is dependency management?",
        "What is risk management?",
        "What is benefits realization?",
        "What is the difference between program and portfolio management?",
    ]

    print("\nINTERVIEW QUESTIONS")
    print("=" * 60)

    for number, question in enumerate(questions, start=1):
        print(f"{number:02d}. {question}")


"""
===============================================================================
SECTION 66: QUICK MEMORY MODEL
===============================================================================

Remember these four questions:

PRODUCT
    "Are we building the right thing?"

PROJECT
    "Are we delivering the thing right?"

PROGRAM
    "Are all related initiatives working together to create the
     intended strategic benefits?"

PORTFOLIO
    "Are we investing in the right collection of initiatives?"

This is a simplified mental model, but it is extremely useful for interviews.


===============================================================================
SECTION 67: END-TO-END EXAMPLE
===============================================================================

STRATEGIC GOAL:
    Increase digital banking adoption.

PORTFOLIO:
    Digital Transformation Investment

PROGRAM:
    Digital Banking Transformation

PRODUCT:
    Mobile Banking Application

PROJECT:
    Mobile Banking Version 2 Release

EPIC:
    Customer Onboarding

STORIES:
    Create account
    Verify identity
    Add profile
    Enable notifications

TASKS:
    Build API
    Build UI
    Write tests
    Configure deployment

JIRA:
    Tracks the execution work.

CONFLUENCE:
    Stores requirements, decisions, architecture, plans and knowledge.

METRICS:
    Activation
    Retention
    Adoption
    Conversion

OUTCOME:
    More customers successfully use digital banking.


===============================================================================
SECTION 68: FINAL CONCEPTUAL MODEL
===============================================================================

The entire discipline can be remembered as:

PORTFOLIO
    |
    | Investment choices
    v
PROGRAM
    |
    | Strategic coordination
    v
PRODUCT
    |
    | Customer and business value
    v
PROJECT
    |
    | Delivery
    v
EPIC
    |
    | Large capability
    v
STORY
    |
    | User requirement
    v
TASK
    |
    | Execution
    v
OUTPUT
    |
    | What was produced?
    v
OUTCOME
    |
    | What changed?
    v
IMPACT
    |
    | What business/customer value was created?
    v
LEARNING
    |
    +-----------------------> PRODUCT STRATEGY


===============================================================================
SECTION 69: EXECUTABLE DEMONSTRATION
===============================================================================
"""


def run_all_examples():
    print("\n")
    print("=" * 90)
    print("PRODUCT vs PROJECT vs PROGRAM MANAGEMENT")
    print("=" * 90)

    explain_basic_definitions()
    product_manager_responsibilities()
    project_manager_responsibilities()
    program_manager_responsibilities()
    compare_three_disciplines()
    ownership_model()
    raci_example()
    product_backlog_example()
    project_plan_example()
    demonstrate_rice()
    demonstrate_risk()
    demonstrate_product_metrics()
    jira_example()
    decision_matrix()
    interview_questions()

    print("\n")
    print("=" * 90)
    print("LEARNING COMPLETE")
    print("=" * 90)


"""
===============================================================================
SECTION 70: FINAL TAKEAWAY
===============================================================================

The most important concepts to remember are:

1. Product Management focuses on VALUE.
2. Project Management focuses on DELIVERY.
3. Program Management focuses on COORDINATION and BENEFITS.
4. Portfolio Management focuses on INVESTMENT.
5. Product Managers primarily think about customers, strategy and outcomes.
6. Project Managers primarily think about execution, schedule, scope,
   resources, risks and delivery.
7. Program Managers primarily think about strategic alignment,
   dependencies, governance and benefits realization.
8. A roadmap is not the same thing as a project schedule.
9. A backlog is not the same thing as a product strategy.
10. Jira tracks work.
11. Confluence manages knowledge and documentation.
12. Outputs are not the same as outcomes.
13. A project can be delivered successfully while the product fails.
14. Product success is strongly connected to customer and business outcomes.
15. Program success depends on realizing strategic benefits across initiatives.
16. RACI clarifies accountability.
17. RAID helps organize risks, assumptions, issues and dependencies.
18. OKRs connect objectives with measurable results.
19. KPIs measure performance.
20. Prioritization determines where limited resources should be invested.
21. Dependency management becomes increasingly important as organizational
    complexity increases.
22. Strong Product, Project and Program Managers collaborate rather than
    operate in isolation.

THE SIMPLEST MEMORY RULE:

    PRODUCT  -> VALUE
    PROJECT  -> DELIVERY
    PROGRAM  -> COORDINATION
    PORTFOLIO -> INVESTMENT

===============================================================================
END OF SCRIPT
===============================================================================
"""


if __name__ == "__main__":
    run_all_examples()
