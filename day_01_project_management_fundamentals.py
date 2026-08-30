# ============================================================
# DAY 01: PROJECT MANAGEMENT FUNDAMENTALS
# ============================================================

print("DAY 01 - PROJECT MANAGEMENT FUNDAMENTALS")


# ============================================================
# 1. WHAT IS A PROJECT?
# ============================================================

print("\n1. WHAT IS A PROJECT?")

project_name = "Website Development"

print("Project:", project_name)
print("A project is a temporary effort undertaken to achieve a")
print("specific objective or deliverable.")


# ============================================================
# 2. PROJECT CHARACTERISTICS
# ============================================================

print("\n2. PROJECT CHARACTERISTICS")

project_characteristics = [
    "Has a specific objective",
    "Has a defined beginning",
    "Has a defined end",
    "Produces a deliverable or outcome",
    "Uses resources",
    "Operates within constraints"
]

for characteristic in project_characteristics:
    print("-", characteristic)


# ============================================================
# 3. PROJECT CONSTRAINTS
# ============================================================

print("\n3. PROJECT CONSTRAINTS")

scope = "Website with 5 major pages"
time = "8 weeks"
budget = 500000

print("Scope:", scope)
print("Time:", time)
print("Budget: ₹", budget)

print("\nA project manager must balance scope, time, cost,")
print("quality, resources, and risks.")


# ============================================================
# 4. PROJECT STAKEHOLDERS
# ============================================================

print("\n4. PROJECT STAKEHOLDERS")

stakeholders = [
    "Project Sponsor",
    "Project Manager",
    "Project Team",
    "Customer",
    "Management"
]

for stakeholder in stakeholders:
    print("-", stakeholder)


# ============================================================
# 5. PROJECT MANAGER
# ============================================================

print("\n5. ROLE OF A PROJECT MANAGER")

responsibilities = [
    "Define project objectives",
    "Plan the project",
    "Coordinate the team",
    "Manage scope",
    "Manage schedule",
    "Manage resources",
    "Monitor risks",
    "Communicate with stakeholders",
    "Track progress"
]

for responsibility in responsibilities:
    print("-", responsibility)


# ============================================================
# 6. PROJECT LIFECYCLE
# ============================================================

print("\n6. PROJECT LIFECYCLE")

project_lifecycle = [
    "Initiation",
    "Planning",
    "Execution",
    "Monitoring and Controlling",
    "Closing"
]

for stage in project_lifecycle:
    print("-", stage)


# ============================================================
# 7. SIMPLE PROJECT PLAN
# ============================================================

print("\n7. SIMPLE PROJECT PLAN")

tasks = [
    "Define requirements",
    "Create project plan",
    "Design solution",
    "Develop solution",
    "Test solution",
    "Deliver project"
]

for number, task in enumerate(tasks, start=1):
    print(number, "-", task)


# ============================================================
# 8. PROJECT RISK
# ============================================================

print("\n8. PROJECT RISK")

risk = "Development delay"

probability = "Medium"
impact = "High"

print("Risk:", risk)
print("Probability:", probability)
print("Impact:", impact)

print("Risks should be identified, assessed, monitored,")
print("and managed throughout the project.")


# ============================================================
# 9. PROJECT SUCCESS
# ============================================================

print("\n9. PROJECT SUCCESS")

success_factors = [
    "Clear objectives",
    "Effective planning",
    "Good communication",
    "Proper resource management",
    "Risk management",
    "Stakeholder satisfaction",
    "Successful delivery"
]

for factor in success_factors:
    print("-", factor)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DAY 01 COMPLETED")
print("=" * 60)

print("""
Today you learned:

1. What a project is
2. Characteristics of a project
3. Project constraints
4. Project stakeholders
5. Role of a project manager
6. Project lifecycle
7. Basic project planning
8. Project risks
9. Project success factors
""")
