"""
Survey Design: A Comprehensive Practical Study
===============================================

This standalone script teaches survey design from beginner to advanced level.

Covered:
- Survey objectives
- Research questions and hypotheses
- Population, sampling frame, sample, and census
- Probability and non-probability sampling
- Sampling bias and non-sampling error
- Question types
- Open-ended and closed-ended questions
- Dichotomous, multiple-choice, ranking, matrix, semantic differential,
  Likert, numerical, and demographic questions
- Measurement scales: nominal, ordinal, interval, ratio
- Question wording and response options
- Leading, loaded, double-barreled, ambiguous, hypothetical, and
  acquiescence-inducing questions
- Skip logic and branching
- Pilot testing
- Response quality
- Reliability and validity
- Sampling error and confidence intervals
- Nonresponse bias
- Survey scoring
- Data cleaning and validation
- Basic descriptive analysis
- Cross-tabulation
- Cronbach's alpha
- Net Promoter Score
- Likert-scale analysis
- Survey design comparisons
- Practical Google Forms and Typeform design considerations
- A complete example survey system

The script uses only the Python standard library.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional


# =============================================================================
# 1. FUNDAMENTAL TERMINOLOGY
# =============================================================================

def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


@dataclass
class SurveyObjective:
    """Represents a measurable objective of a survey."""
    objective_id: str
    description: str
    metric: str
    target_population: str

    def display(self) -> None:
        print(f"{self.objective_id}: {self.description}")
        print(f"  Metric: {self.metric}")
        print(f"  Population: {self.target_population}")


print_section("1. Survey Objectives")

objectives = [
    SurveyObjective(
        "OBJ-01",
        "Measure customer satisfaction with an online service.",
        "Mean satisfaction score on a 1-5 scale",
        "Customers who used the service during the last 90 days",
    ),
    SurveyObjective(
        "OBJ-02",
        "Identify the most common service problems.",
        "Percentage selecting each problem category",
        "Customers who contacted support during the last 90 days",
    ),
    SurveyObjective(
        "OBJ-03",
        "Estimate willingness to recommend the service.",
        "Net Promoter Score",
        "Active customers",
    ),
]

for objective in objectives:
    objective.display()


# =============================================================================
# 2. OBJECTIVE -> RESEARCH QUESTION -> SURVEY QUESTION
# =============================================================================

def convert_objective_to_question(objective: SurveyObjective) -> str:
    """
    Converts a broad objective into an operational research question.

    A good research question should be specific enough that the answer can
    be represented by observable survey data.
    """
    if "satisfaction" in objective.description.lower():
        return "How satisfied are customers with the service?"
    if "problems" in objective.description.lower():
        return "Which service problems do customers experience most frequently?"
    if "recommend" in objective.description.lower():
        return "How likely are customers to recommend the service?"
    return f"What does the survey need to measure for {objective.objective_id}?"


for objective in objectives:
    print(f"{objective.objective_id}:")
    print(f"  Research question: {convert_objective_to_question(objective)}")


# =============================================================================
# 3. QUESTION TYPES
# =============================================================================

@dataclass
class SurveyQuestion:
    question_id: str
    text: str
    question_type: str
    required: bool = False
    options: list[str] = field(default_factory=list)
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None

    def validate_answer(self, answer: Any) -> tuple[bool, str]:
        """Validate an answer according to the question definition."""
        if self.required and (answer is None or answer == ""):
            return False, "This question is required."

        if answer is None or answer == "":
            return True, "No answer provided."

        if self.question_type in {"single_choice", "multiple_choice"}:
            if self.question_type == "single_choice":
                if answer not in self.options:
                    return False, "Answer is not one of the permitted options."
            else:
                if not isinstance(answer, list):
                    return False, "Multiple-choice answer must be a list."
                invalid = [item for item in answer if item not in self.options]
                if invalid:
                    return False, f"Invalid choices: {invalid}"

        if self.question_type == "scale":
            if not isinstance(answer, int):
                return False, "Scale answer must be an integer."
            if self.scale_min is None or self.scale_max is None:
                return False, "Scale bounds are not configured."
            if not self.scale_min <= answer <= self.scale_max:
                return False, "Scale answer is outside the permitted range."

        return True, "Valid answer."


questions = [
    SurveyQuestion(
        "Q1",
        "Which plan do you currently use?",
        "single_choice",
        required=True,
        options=["Free", "Basic", "Professional", "Enterprise"],
    ),
    SurveyQuestion(
        "Q2",
        "Which features have you used?",
        "multiple_choice",
        options=["Dashboard", "Reports", "Automation", "API"],
    ),
    SurveyQuestion(
        "Q3",
        "How satisfied are you with the service?",
        "scale",
        required=True,
        scale_min=1,
        scale_max=5,
    ),
    SurveyQuestion(
        "Q4",
        "What should we improve?",
        "open_text",
    ),
]

print_section("2. Question Type Demonstrations")

sample_answers = {
    "Q1": "Professional",
    "Q2": ["Dashboard", "API"],
    "Q3": 4,
    "Q4": "Improve reporting speed.",
}

for question in questions:
    answer = sample_answers.get(question.question_id)
    valid, message = question.validate_answer(answer)
    print(f"{question.question_id}: {answer!r} -> {message}")


# =============================================================================
# 4. COMMON QUESTION TYPES
# =============================================================================

print_section("3. Major Survey Question Types")

question_type_reference = {
    "Dichotomous": "Exactly two meaningful response categories, such as Yes/No.",
    "Single choice": "Respondent selects one option.",
    "Multiple choice": "Respondent selects one or more options.",
    "Open-ended": "Respondent provides free-form text.",
    "Likert": "Measures agreement, frequency, satisfaction, or similar attitudes.",
    "Rating scale": "Respondent assigns a numerical or labeled rating.",
    "Ranking": "Respondent orders alternatives.",
    "Matrix": "Several statements share the same response scale.",
    "Semantic differential": "Respondent selects a position between opposing adjectives.",
    "Numerical": "Respondent supplies a number such as age or spending.",
    "Date/time": "Respondent supplies a temporal value.",
    "Demographic": "Measures characteristics such as age group or occupation.",
}

for name, explanation in question_type_reference.items():
    print(f"{name:22} - {explanation}")


# =============================================================================
# 5. MEASUREMENT SCALES
# =============================================================================

print_section("4. Measurement Scales")

measurement_scales = {
    "Nominal": {
        "meaning": "Categories without inherent numerical order.",
        "examples": ["Country", "Department", "Product category"],
        "valid_operations": ["Counts", "Percentages", "Mode"],
    },
    "Ordinal": {
        "meaning": "Ordered categories where spacing is not guaranteed equal.",
        "examples": ["Low/Medium/High", "Class rank", "Satisfaction categories"],
        "valid_operations": ["Counts", "Percentages", "Median", "Percentiles"],
    },
    "Interval": {
        "meaning": "Equal numerical intervals but no meaningful absolute zero.",
        "examples": ["Temperature in Celsius", "Some constructed index scores"],
        "valid_operations": ["Mean", "Standard deviation", "Differences"],
    },
    "Ratio": {
        "meaning": "Equal intervals and a meaningful zero.",
        "examples": ["Age", "Income", "Number of purchases"],
        "valid_operations": ["All ordinary arithmetic operations"],
    },
}

for scale, details in measurement_scales.items():
    print(f"\n{scale}")
    print(f"  Meaning: {details['meaning']}")
    print(f"  Examples: {', '.join(details['examples'])}")
    print(f"  Operations: {', '.join(details['valid_operations'])}")


# =============================================================================
# 6. GOOD AND BAD QUESTION WORDING
# =============================================================================

print_section("5. Question Wording Quality")

wording_examples = {
    "Leading":
        "Don't you agree that our excellent service is easy to use?",
    "Improved":
        "How easy or difficult is the service to use?",

    "Double-barreled":
        "How satisfied are you with our price and customer support?",
    "Improved":
        "How satisfied are you with the price?",
    "Improved_2":
        "How satisfied are you with customer support?",

    "Ambiguous":
        "Do you use the product regularly?",
    "Improved_2":
        "On how many days did you use the product during the last 30 days?",

    "Loaded":
        "How much do you value our innovative platform?",
    "Improved_3":
        "How valuable is the platform to your work?",

    "Hypothetical":
        "Would you definitely buy this product in the future?",
    "Improved_4":
        "How likely are you to purchase this product within the next 30 days?",
}

for label, example in wording_examples.items():
    print(f"{label}: {example}")


# =============================================================================
# 7. RESPONSE OPTION DESIGN
# =============================================================================

print_section("6. Response Option Design")

def check_options(
    options: list[str],
    *,
    allow_multiple: bool = False,
    has_other: bool = False,
) -> list[str]:
    """
    Performs basic response-option checks.

    Exhaustiveness is context dependent. This function identifies obvious
    structural issues without pretending that every survey has one universal
    set of valid categories.
    """
    problems: list[str] = []

    normalized = [option.strip().lower() for option in options]

    if len(set(normalized)) != len(normalized):
        problems.append("Duplicate response options exist.")

    if "" in normalized:
        problems.append("At least one response option is empty.")

    if not allow_multiple and len(options) < 2:
        problems.append("A single-choice question normally needs alternatives.")

    if has_other and "other" not in normalized:
        problems.append("The question claims to have an Other option but does not.")

    return problems


options = ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
print("Option problems:", check_options(options))


# =============================================================================
# 8. SAMPLING FUNDAMENTALS
# =============================================================================

print_section("7. Population, Sampling Frame, Sample, Census")

population = list(range(1, 101))
sampling_frame = population.copy()

print(f"Population size: {len(population)}")
print(f"Sampling-frame size: {len(sampling_frame)}")

random.seed(42)
sample = random.sample(sampling_frame, 10)

print(f"Random sample of 10: {sample}")
print(
    "A sampling frame should approximate the target population. "
    "A frame can itself introduce coverage error."
)


# =============================================================================
# 9. PROBABILITY SAMPLING
# =============================================================================

def simple_random_sample(population: list[Any], sample_size: int) -> list[Any]:
    """Simple random sampling without replacement."""
    if sample_size < 0 or sample_size > len(population):
        raise ValueError("sample_size must be between 0 and population size.")
    return random.sample(population, sample_size)


def systematic_sample(
    population: list[Any],
    sample_size: int,
    start: Optional[int] = None,
) -> list[Any]:
    """
    Systematic sampling.

    k is approximately N/n. A random starting point is selected, then every
    kth population member is selected.
    """
    if sample_size <= 0 or sample_size > len(population):
        raise ValueError("Invalid sample size.")

    interval = len(population) / sample_size

    if start is None:
        start = random.randrange(max(1, math.ceil(interval)))

    result = []
    index = start - 1

    while len(result) < sample_size and index < len(population):
        result.append(population[index])
        index += max(1, round(interval))

    return result


def stratified_sample(
    population_by_stratum: dict[str, list[Any]],
    sample_size: int,
) -> list[Any]:
    """
    Proportionally allocates a sample across strata.

    In production research, allocation may instead be disproportional when
    small or strategically important strata need more observations.
    """
    total_population = sum(len(values) for values in population_by_stratum.values())

    if total_population == 0:
        return []

    if sample_size > total_population:
        raise ValueError("Sample size cannot exceed population size.")

    result = []

    raw_allocations = {
        key: len(values) / total_population * sample_size
        for key, values in population_by_stratum.items()
    }

    allocations = {
        key: int(math.floor(value))
        for key, value in raw_allocations.items()
    }

    remaining = sample_size - sum(allocations.values())

    remainders = sorted(
        raw_allocations,
        key=lambda key: raw_allocations[key] - allocations[key],
        reverse=True,
    )

    for key in remainders[:remaining]:
        allocations[key] += 1

    for stratum, values in population_by_stratum.items():
        result.extend(random.sample(values, allocations[stratum]))

    return result


print_section("8. Sampling Methods")

population_100 = list(range(1, 101))
print("Simple random:", simple_random_sample(population_100, 8))
print("Systematic:", systematic_sample(population_100, 8, start=3))

strata = {
    "North": list(range(1, 41)),
    "South": list(range(41, 71)),
    "West": list(range(71, 101)),
}

print("Stratified:", stratified_sample(strata, 12))


# =============================================================================
# 10. NON-PROBABILITY SAMPLING
# =============================================================================

print_section("9. Non-Probability Sampling")

non_probability_methods = {
    "Convenience": "Recruit whoever is easiest to reach.",
    "Purposive": "Select participants because they meet defined research criteria.",
    "Quota": "Fill predefined category counts without random selection within categories.",
    "Snowball": "Existing participants help recruit additional participants.",
    "Volunteer": "People self-select into participation.",
}

for method, definition in non_probability_methods.items():
    print(f"{method}: {definition}")

print(
    "\nImportant distinction: a large convenience sample is not automatically "
    "representative of the target population."
)


# =============================================================================
# 11. SAMPLING ERROR AND CONFIDENCE INTERVALS
# =============================================================================

def proportion_standard_error(p: float, n: int) -> float:
    """Approximate standard error of a sample proportion."""
    if n <= 0:
        raise ValueError("n must be positive.")
    if not 0 <= p <= 1:
        raise ValueError("p must be between 0 and 1.")
    return math.sqrt(p * (1 - p) / n)


def approximate_95_percent_ci_for_proportion(
    p: float,
    n: int,
) -> tuple[float, float]:
    """
    Wald-style approximate 95% confidence interval.

    This is an educational implementation. For small samples or proportions
    near 0/1, other intervals such as Wilson intervals are generally preferable.
    """
    se = proportion_standard_error(p, n)
    margin = 1.96 * se
    return max(0.0, p - margin), min(1.0, p + margin)


print_section("10. Sampling Error")

sample_proportion = 0.60
sample_size = 400
ci_low, ci_high = approximate_95_percent_ci_for_proportion(
    sample_proportion,
    sample_size,
)

print(f"Estimated proportion: {sample_proportion:.3f}")
print(f"Approximate 95% interval: {ci_low:.3f} to {ci_high:.3f}")
print(
    "A confidence interval reflects sampling uncertainty under the assumptions "
    "of the statistical method. It does not automatically correct coverage, "
    "nonresponse, wording, or measurement bias."
)


# =============================================================================
# 12. SAMPLE SIZE
# =============================================================================

def approximate_sample_size_for_proportion(
    confidence_z: float,
    margin_of_error: float,
    expected_proportion: float = 0.5,
) -> int:
    """
    Approximate sample size for a population proportion.

    The conservative expected proportion of 0.5 maximizes p(1-p).
    This formula assumes a probability sample and does not automatically
    account for design effects, nonresponse, finite population correction,
    or complex survey designs.
    """
    if confidence_z <= 0:
        raise ValueError("confidence_z must be positive.")
    if not 0 < margin_of_error < 1:
        raise ValueError("margin_of_error must be between 0 and 1.")
    if not 0 < expected_proportion < 1:
        raise ValueError("expected_proportion must be between 0 and 1.")

    variance = expected_proportion * (1 - expected_proportion)
    n = confidence_z**2 * variance / margin_of_error**2
    return math.ceil(n)


print_section("11. Sample Size")

required_n = approximate_sample_size_for_proportion(
    confidence_z=1.96,
    margin_of_error=0.05,
    expected_proportion=0.50,
)

print(f"Approximate sample size: {required_n}")


# =============================================================================
# 13. BIAS
# =============================================================================

print_section("12. Survey Bias")

bias_types = {
    "Coverage bias":
        "Some members of the target population have no or inadequate chance "
        "of appearing in the sampling frame.",
    "Selection bias":
        "The recruitment process systematically favors some participants.",
    "Nonresponse bias":
        "People who do not respond differ in relevant ways from respondents.",
    "Question wording bias":
        "Question wording changes how respondents interpret or answer.",
    "Social desirability bias":
        "Respondents give answers they believe are socially acceptable.",
    "Recall bias":
        "Respondents cannot accurately remember past events.",
    "Acquiescence bias":
        "Respondents tend to agree with statements regardless of content.",
    "Order effect":
        "Earlier questions or response options influence later responses.",
    "Interviewer effect":
        "An interviewer influences responses through behavior or wording.",
    "Mode effect":
        "The survey channel changes response behavior.",
}

for bias_name, explanation in bias_types.items():
    print(f"{bias_name}: {explanation}")


# =============================================================================
# 14. RESPONSE QUALITY
# =============================================================================

@dataclass
class ResponseRecord:
    respondent_id: str
    answers: dict[str, Any]
    completion_seconds: float
    attention_check_passed: bool
    duplicate: bool = False


def detect_suspicious_response(
    response: ResponseRecord,
    minimum_seconds: float = 30.0,
) -> list[str]:
    """
    Flags potential quality problems.

    A flag is not proof that a response is invalid. Human or predefined
    research rules should determine final treatment.
    """
    flags = []

    if response.completion_seconds < minimum_seconds:
        flags.append("Unusually fast completion.")

    if not response.attention_check_passed:
        flags.append("Attention check failed.")

    if response.duplicate:
        flags.append("Potential duplicate response.")

    return flags


print_section("13. Response Quality")

response = ResponseRecord(
    respondent_id="R-001",
    answers={"Q1": "Professional", "Q3": 5},
    completion_seconds=18,
    attention_check_passed=True,
)

print(detect_suspicious_response(response))


# =============================================================================
# 15. RELIABILITY AND CRONBACH'S ALPHA
# =============================================================================

def cronbach_alpha(items: list[list[float]]) -> float:
    """
    Calculate Cronbach's alpha for a set of scale items.

    items format:
        [
            [respondent1_item1, respondent1_item2, ...],
            [respondent2_item1, respondent2_item2, ...],
            ...
        ]

    Alpha is a measure of internal consistency, not proof of validity or
    unidimensionality.
    """
    if not items:
        raise ValueError("At least one respondent is required.")

    number_of_items = len(items[0])

    if number_of_items < 2:
        raise ValueError("At least two items are required.")

    if any(len(row) != number_of_items for row in items):
        raise ValueError("All respondents must have the same number of items.")

    n = len(items)

    if n < 2:
        raise ValueError("At least two respondents are required.")

    item_variances = [
        statistics.variance([row[i] for row in items])
        for i in range(number_of_items)
    ]

    total_scores = [sum(row) for row in items]
    total_variance = statistics.variance(total_scores)

    if total_variance == 0:
        return float("nan")

    alpha = (
        number_of_items
        / (number_of_items - 1)
        * (1 - sum(item_variances) / total_variance)
    )

    return alpha


print_section("14. Reliability")

likert_responses = [
    [4, 5, 4, 5],
    [3, 4, 3, 4],
    [5, 5, 4, 5],
    [4, 4, 4, 4],
    [2, 3, 2, 3],
    [5, 4, 5, 5],
]

alpha = cronbach_alpha(likert_responses)
print(f"Cronbach's alpha: {alpha:.3f}")
print(
    "Alpha should be interpreted in context. Very high alpha can also indicate "
    "redundant items."
)


# =============================================================================
# 16. LIKERT-SCALE ANALYSIS
# =============================================================================

def likert_summary(values: Iterable[int]) -> dict[str, float]:
    """Return basic descriptive statistics for a Likert item."""
    values = list(values)

    if not values:
        raise ValueError("At least one response is required.")

    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "mode": statistics.mode(values),
        "min": min(values),
        "max": max(values),
    }


print_section("15. Likert Analysis")

satisfaction = [4, 5, 3, 4, 4, 2, 5, 4, 3, 5]
print(likert_summary(satisfaction))


# =============================================================================
# 17. NET PROMOTER SCORE
# =============================================================================

def calculate_nps(scores: Iterable[int]) -> float:
    """
    Calculate Net Promoter Score.

    Promoters: 9-10
    Passives: 7-8
    Detractors: 0-6

    NPS = percentage promoters - percentage detractors.
    """
    scores = list(scores)

    if not scores:
        raise ValueError("At least one score is required.")

    if any(score < 0 or score > 10 for score in scores):
        raise ValueError("NPS scores must be between 0 and 10.")

    promoters = sum(score >= 9 for score in scores)
    detractors = sum(score <= 6 for score in scores)

    return (promoters / len(scores) - detractors / len(scores)) * 100


print_section("16. NPS")

nps_scores = [10, 9, 8, 7, 6, 9, 10, 5, 8, 9]
print(f"NPS: {calculate_nps(nps_scores):.1f}")


# =============================================================================
# 18. RANKING ANALYSIS
# =============================================================================

def average_rankings(rankings: list[list[str]]) -> dict[str, float]:
    """
    Calculate average rank for each item.

    Lower average rank means the item was placed earlier more often.
    This is descriptive and should not be treated as an automatic measure
    of statistical significance.
    """
    totals: defaultdict[str, list[int]] = defaultdict(list)

    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            totals[item].append(rank)

    return {
        item: statistics.mean(ranks)
        for item, ranks in totals.items()
    }


print_section("17. Ranking")

ranking_data = [
    ["Speed", "Price", "Support", "Design"],
    ["Support", "Speed", "Design", "Price"],
    ["Speed", "Design", "Support", "Price"],
]

print(average_rankings(ranking_data))


# =============================================================================
# 19. CROSS-TABULATION
# =============================================================================

def cross_tabulate(
    rows: Iterable[Any],
    columns: Iterable[Any],
) -> dict[Any, Counter]:
    """Create a simple contingency table."""
    rows = list(rows)
    columns = list(columns)

    if len(rows) != len(columns):
        raise ValueError("Rows and columns must have the same length.")

    table: dict[Any, Counter] = defaultdict(Counter)

    for row_value, column_value in zip(rows, columns):
        table[row_value][column_value] += 1

    return dict(table)


print_section("18. Cross-Tabulation")

plans = [
    "Free",
    "Free",
    "Basic",
    "Basic",
    "Professional",
    "Professional",
    "Professional",
    "Enterprise",
]

satisfaction_groups = [
    "Satisfied",
    "Neutral",
    "Satisfied",
    "Dissatisfied",
    "Satisfied",
    "Satisfied",
    "Neutral",
    "Satisfied",
]

table = cross_tabulate(plans, satisfaction_groups)

for plan, counts in table.items():
    print(plan, dict(counts))


# =============================================================================
# 20. SURVEY LOGIC / BRANCHING
# =============================================================================

@dataclass
class BranchRule:
    source_question: str
    expected_answer: Any
    destination_question: str

    def matches(self, answers: dict[str, Any]) -> bool:
        return answers.get(self.source_question) == self.expected_answer


print_section("19. Skip Logic")

branch_rules = [
    BranchRule("Q1", "Enterprise", "Q_ENTERPRISE"),
    BranchRule("Q1", "Free", "Q_UPGRADE"),
]

answers = {"Q1": "Enterprise"}

for rule in branch_rules:
    if rule.matches(answers):
        print(
            f"Because {rule.source_question} == {rule.expected_answer!r}, "
            f"show {rule.destination_question}."
        )


# =============================================================================
# 21. SURVEY SCHEMA
# =============================================================================

@dataclass
class Survey:
    title: str
    purpose: str
    population: str
    questions: list[SurveyQuestion]

    def required_questions(self) -> list[SurveyQuestion]:
        return [question for question in self.questions if question.required]

    def validate_response(self, response: dict[str, Any]) -> list[str]:
        errors = []

        for question in self.questions:
            answer = response.get(question.question_id)
            valid, message = question.validate_answer(answer)

            if not valid:
                errors.append(f"{question.question_id}: {message}")

        return errors


survey = Survey(
    title="Customer Experience Survey",
    purpose="Measure satisfaction and identify improvement opportunities.",
    population="Customers who used the service within the last 90 days.",
    questions=questions,
)

print_section("20. Complete Survey Validation")

test_response = {
    "Q1": "Professional",
    "Q2": ["Dashboard", "Reports"],
    "Q3": 6,
    "Q4": "Improve response time.",
}

validation_errors = survey.validate_response(test_response)
print("Errors:")
for error in validation_errors:
    print(" ", error)


# =============================================================================
# 22. PILOT TESTING
# =============================================================================

def calculate_completion_rate(
    invited: int,
    completed: int,
) -> float:
    """Calculate the completion rate."""
    if invited < 0 or completed < 0:
        raise ValueError("Counts cannot be negative.")

    if completed > invited:
        raise ValueError("Completed responses cannot exceed invitations.")

    if invited == 0:
        return 0.0

    return completed / invited * 100


print_section("21. Pilot Testing Metrics")

pilot_metrics = {
    "Invited": 30,
    "Started": 27,
    "Completed": 24,
    "Usable": 23,
}

print(
    "Completion rate:",
    f"{calculate_completion_rate(pilot_metrics['Invited'], pilot_metrics['Completed']):.1f}%",
)

print(
    "Usable response rate relative to invitations:",
    f"{pilot_metrics['Usable'] / pilot_metrics['Invited'] * 100:.1f}%",
)


# =============================================================================
# 23. DATA CLEANING
# =============================================================================

def clean_text(value: Any) -> Optional[str]:
    """Normalize text while preserving missing values."""
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return " ".join(text.split())


def remove_duplicate_responses(
    responses: list[dict[str, Any]],
    respondent_key: str = "respondent_id",
) -> list[dict[str, Any]]:
    """Keep the first response for each respondent ID."""
    seen = set()
    cleaned = []

    for response in responses:
        respondent_id = response.get(respondent_key)

        if respondent_id in seen:
            continue

        seen.add(respondent_id)
        cleaned.append(response)

    return cleaned


print_section("22. Data Cleaning")

raw_text = "   Customer    experience   was excellent.   "
print("Before:", repr(raw_text))
print("After :", repr(clean_text(raw_text)))

raw_responses = [
    {"respondent_id": "R1", "Q3": 5},
    {"respondent_id": "R2", "Q3": 4},
    {"respondent_id": "R1", "Q3": 5},
]

print("Deduplicated:", remove_duplicate_responses(raw_responses))


# =============================================================================
# 24. DATA VALIDATION
# =============================================================================

def validate_age(age: Any) -> tuple[bool, str]:
    """Validate a plausible survey age value."""
    if not isinstance(age, int):
        return False, "Age must be an integer."

    if age < 0 or age > 120:
        return False, "Age is outside the configured plausible range."

    return True, "Valid."


def validate_percentage(value: Any) -> tuple[bool, str]:
    """Validate a percentage."""
    if not isinstance(value, (int, float)):
        return False, "Percentage must be numeric."

    if not 0 <= value <= 100:
        return False, "Percentage must be between 0 and 100."

    return True, "Valid."


print_section("23. Validation")

for age in [25, -3, 150, "25"]:
    print(age, "->", validate_age(age))

for percentage in [25, 100, 101, -2]:
    print(percentage, "->", validate_percentage(percentage))


# =============================================================================
# 25. RESPONSE DISTRIBUTION
# =============================================================================

def frequency_distribution(values: Iterable[Any]) -> dict[Any, int]:
    """Return category frequencies."""
    return dict(Counter(values))


print_section("24. Frequency Distribution")

categories = [
    "Satisfied",
    "Satisfied",
    "Neutral",
    "Dissatisfied",
    "Satisfied",
    "Neutral",
]

print(frequency_distribution(categories))


# =============================================================================
# 26. RESPONSE RATE
# =============================================================================

def response_rate(
    completed: int,
    eligible_invited: int,
) -> float:
    """
    Calculate response rate.

    The exact denominator should follow the study's defined eligibility and
    fieldwork protocol.
    """
    if eligible_invited <= 0:
        raise ValueError("Eligible invited count must be positive.")

    if completed < 0 or completed > eligible_invited:
        raise ValueError("Completed responses are outside valid bounds.")

    return completed / eligible_invited * 100


print_section("25. Response Rate")

print(f"Response rate: {response_rate(320, 1000):.1f}%")


# =============================================================================
# 27. RANDOM RESPONSE SIMULATION
# =============================================================================

def simulate_likert_responses(
    number_of_respondents: int,
    probabilities: list[float],
    values: list[int],
    seed: int = 42,
) -> list[int]:
    """Generate reproducible simulated survey responses."""
    if number_of_respondents < 0:
        raise ValueError("Number of respondents cannot be negative.")

    if len(probabilities) != len(values):
        raise ValueError("Probabilities and values must have equal length.")

    if not math.isclose(sum(probabilities), 1.0, rel_tol=1e-9):
        raise ValueError("Probabilities must sum to 1.")

    if any(probability < 0 for probability in probabilities):
        raise ValueError("Probabilities cannot be negative.")

    generator = random.Random(seed)

    return generator.choices(
        values,
        weights=probabilities,
        k=number_of_respondents,
    )


print_section("26. Simulation")

simulated = simulate_likert_responses(
    100,
    probabilities=[0.05, 0.10, 0.20, 0.40, 0.25],
    values=[1, 2, 3, 4, 5],
)

print(likert_summary(simulated))


# =============================================================================
# 28. DESIGN EFFECT AND CLUSTERING
# =============================================================================

def approximate_design_effect(
    average_cluster_size: float,
    intraclass_correlation: float,
) -> float:
    """
    Approximate cluster-sampling design effect:

        DEFF = 1 + (m - 1) * ICC

    This illustrates why clustered observations can contain less independent
    information than the same number of independently sampled observations.
    """
    if average_cluster_size < 1:
        raise ValueError("Average cluster size must be >= 1.")

    if not 0 <= intraclass_correlation <= 1:
        raise ValueError("ICC must be between 0 and 1.")

    return 1 + (average_cluster_size - 1) * intraclass_correlation


print_section("27. Design Effect")

deff = approximate_design_effect(10, 0.10)
print(f"Approximate design effect: {deff:.2f}")


# =============================================================================
# 29. SURVEY DESIGN CHECKLIST
# =============================================================================

print_section("28. Survey Design Checklist")

checklist = [
    "Define the decision or research problem.",
    "Write measurable survey objectives.",
    "Define the target population.",
    "Define eligibility criteria.",
    "Identify or construct the sampling frame.",
    "Choose a sampling method.",
    "Estimate sample size and account for expected nonresponse.",
    "Choose measurement constructs.",
    "Select appropriate question types.",
    "Use neutral and specific wording.",
    "Make response options mutually appropriate and sufficiently exhaustive.",
    "Separate double-barreled concepts.",
    "Specify reference periods for recall questions.",
    "Use skip logic only where it improves relevance.",
    "Limit unnecessary sensitive questions.",
    "Pilot test the instrument.",
    "Measure completion and response quality.",
    "Document cleaning rules before analyzing data.",
    "Analyze missingness and nonresponse.",
    "Document limitations and sources of bias.",
]

for number, item in enumerate(checklist, start=1):
    print(f"{number:02d}. {item}")


# =============================================================================
# 30. GOOGLE FORMS AND TYPEFORM CONCEPTUAL MAPPING
# =============================================================================

print_section("29. Google Forms and Typeform")

platform_mapping = {
    "Google Forms": [
        "Question sections",
        "Required questions",
        "Choice questions",
        "Linear-scale questions",
        "Multiple-choice grids",
        "Checkbox grids",
        "Response collection",
        "Spreadsheet-oriented workflows",
    ],
    "Typeform": [
        "One-question-at-a-time interaction",
        "Conditional logic",
        "Branching",
        "Question piping",
        "Interactive respondent experience",
        "Form logic and personalization",
        "Integrated response workflows",
    ],
}

for platform, capabilities in platform_mapping.items():
    print(f"\n{platform}")
    for capability in capabilities:
        print(f"  - {capability}")

print(
    "\nPlatform interfaces and feature availability can change. "
    "The design principles demonstrated by this script are independent "
    "of a particular form builder."
)


# =============================================================================
# 31. ADVANCED DESIGN: CONSTRUCTS AND OPERATIONALIZATION
# =============================================================================

@dataclass
class Construct:
    name: str
    definition: str
    indicators: list[str]

    def show(self) -> None:
        print(f"\nConstruct: {self.name}")
        print(f"Definition: {self.definition}")
        print("Indicators:")
        for indicator in self.indicators:
            print(f"  - {indicator}")


construct = Construct(
    name="Perceived service usability",
    definition="The respondent's assessment of how easy the service is to use.",
    indicators=[
        "Ease of learning",
        "Ease of navigation",
        "Ease of completing common tasks",
        "Ease of recovering from errors",
    ],
)

print_section("30. Construct Operationalization")
construct.show()


# =============================================================================
# 32. RELIABILITY VS VALIDITY
# =============================================================================

print_section("31. Reliability and Validity")

comparison = {
    "Reliability": "Consistency of measurement.",
    "Content validity": "Whether the instrument adequately covers the construct domain.",
    "Construct validity": "Whether the measure behaves as expected for the theoretical construct.",
    "Criterion validity": "Relationship between the measure and a relevant external criterion.",
    "Face validity": "Whether the instrument appears appropriate at a superficial level.",
}

for concept, definition in comparison.items():
    print(f"{concept}: {definition}")

print(
    "\nA measure can be reliable without being valid. Repeatedly measuring "
    "the wrong construct consistently does not establish validity."
)


# =============================================================================
# 33. ADVANCED: REVERSE-CODED ITEMS
# =============================================================================

def reverse_code(value: int, minimum: int = 1, maximum: int = 5) -> int:
    """
    Reverse-code a bounded scale.

    Example:
        1 -> 5
        2 -> 4
        3 -> 3
        4 -> 2
        5 -> 1
    """
    if not minimum <= value <= maximum:
        raise ValueError("Value is outside the scale.")

    return maximum + minimum - value


print_section("32. Reverse Coding")

for value in range(1, 6):
    print(f"{value} -> {reverse_code(value)}")


# =============================================================================
# 34. MISSING DATA
# =============================================================================

def missing_rate(values: Iterable[Any]) -> float:
    """Calculate the percentage of missing observations."""
    values = list(values)

    if not values:
        return 0.0

    missing = sum(value is None for value in values)
    return missing / len(values) * 100


print_section("33. Missing Data")

missing_values = [5, 4, None, 3, None, 5, 4]
print(f"Missing rate: {missing_rate(missing_values):.1f}%")

print(
    "Missingness should be investigated rather than automatically replaced "
    "with a convenient value. The appropriate treatment depends on the "
    "research design, variable, mechanism of missingness, and analysis."
)


# =============================================================================
# 35. PERFORMANCE CONSIDERATIONS
# =============================================================================

print_section("34. Performance Considerations")

print(
    "For typical survey datasets, dictionary and list operations are generally "
    "fast enough for cleaning and descriptive analysis."
)
print(
    "For very large datasets, columnar data systems, databases, vectorized "
    "analytics libraries, streaming pipelines, or distributed processing may "
    "be appropriate."
)
print(
    "The main performance bottleneck in survey projects is often data "
    "collection, validation, network transfer, or external platform APIs "
    "rather than simple statistical calculations."
)


# =============================================================================
# 36. SECURITY AND PRIVACY
# =============================================================================

print_section("35. Security and Privacy")

security_principles = [
    "Collect only information required for the stated research purpose.",
    "Avoid collecting passwords, authentication secrets, or unnecessary identifiers.",
    "Separate identifying information from analytical responses when practical.",
    "Restrict access to raw survey data.",
    "Use secure transport and reputable storage controls.",
    "Define retention and deletion rules.",
    "Document consent and participant information where required.",
    "Treat free-text responses as potentially sensitive.",
    "Do not expose respondent-level data in public dashboards.",
    "Review platform privacy and data-processing settings before deployment.",
]

for principle in security_principles:
    print(f"- {principle}")


# =============================================================================
# 37. COMPLETE MINI CASE STUDY
# =============================================================================

print_section("36. Complete Mini Case Study")

case_study_questions = [
    SurveyQuestion(
        "S1",
        "Have you used the service during the last 30 days?",
        "single_choice",
        required=True,
        options=["Yes", "No"],
    ),
    SurveyQuestion(
        "S2",
        "How satisfied are you with the service?",
        "scale",
        required=True,
        scale_min=1,
        scale_max=5,
    ),
    SurveyQuestion(
        "S3",
        "Which areas need improvement?",
        "multiple_choice",
        options=[
            "Speed",
            "Reliability",
            "Support",
            "Pricing",
            "Features",
        ],
    ),
    SurveyQuestion(
        "S4",
        "How likely are you to recommend the service?",
        "scale",
        required=True,
        scale_min=0,
        scale_max=10,
    ),
    SurveyQuestion(
        "S5",
        "What is the most important improvement?",
        "open_text",
    ),
]

case_study_survey = Survey(
    title="Service Experience Study",
    purpose="Measure recent customer experience and improvement priorities.",
    population="Customers who used the service during the last 30 days.",
    questions=case_study_questions,
)

case_responses = [
    {
        "respondent_id": "R1",
        "S1": "Yes",
        "S2": 5,
        "S3": ["Speed"],
        "S4": 10,
        "S5": "Keep the service fast.",
    },
    {
        "respondent_id": "R2",
        "S1": "Yes",
        "S2": 4,
        "S3": ["Support", "Reliability"],
        "S4": 8,
        "S5": "Improve support response time.",
    },
    {
        "respondent_id": "R3",
        "S1": "No",
        "S2": None,
        "S3": [],
        "S4": 4,
        "S5": "I need a better onboarding experience.",
    },
    {
        "respondent_id": "R4",
        "S1": "Yes",
        "S2": 3,
        "S3": ["Pricing"],
        "S4": 6,
        "S5": "Make pricing easier to understand.",
    },
]

for respondent in case_responses:
    errors = case_study_survey.validate_response(respondent)
    print(respondent["respondent_id"], "errors:", errors)


# =============================================================================
# 38. CASE STUDY ANALYSIS
# =============================================================================

recent_users = [
    response for response in case_responses
    if response["S1"] == "Yes"
]

satisfaction_scores = [
    response["S2"]
    for response in recent_users
    if response["S2"] is not None
]

recommendation_scores = [
    response["S4"]
    for response in case_responses
    if response["S4"] is not None
]

improvement_counts = Counter()

for response in recent_users:
    for area in response["S3"]:
        improvement_counts[area] += 1

print_section("37. Case Study Analysis")

print("Recent users:", len(recent_users))
print("Mean satisfaction:", statistics.mean(satisfaction_scores))
print("Median satisfaction:", statistics.median(satisfaction_scores))
print("NPS:", calculate_nps(recommendation_scores))
print("Improvement areas:", dict(improvement_counts))


# =============================================================================
# 39. LIMITATIONS OF THE MINI CASE STUDY
# =============================================================================

print_section("38. Case Study Limitations")

limitations = [
    "The sample is intentionally tiny and is not suitable for population inference.",
    "The respondents are simulated examples rather than a real probability sample.",
    "No sampling frame has been evaluated.",
    "No nonresponse adjustment has been performed.",
    "No questionnaire pilot data has been collected.",
    "The wording and scales would require domain-specific validation.",
    "The descriptive statistics should not be treated as causal evidence.",
]

for limitation in limitations:
    print(f"- {limitation}")


# =============================================================================
# 40. FINAL DESIGN PRINCIPLES
# =============================================================================

print_section("39. Core Design Principles")

principles = [
    "Start with the decision or research objective, not with a favorite question type.",
    "Define the target population before recruiting respondents.",
    "Use the sampling design to match the inference you intend to make.",
    "Write one clear concept per question whenever possible.",
    "Use a defined reference period for questions involving recall.",
    "Make response options appropriate to the construct and measurement scale.",
    "Use neutral wording and avoid unnecessary assumptions.",
    "Minimize respondent burden while preserving measurement quality.",
    "Pilot the instrument before full deployment.",
    "Monitor missingness, completion time, duplicates, and inconsistent responses.",
    "Distinguish measurement error from sampling error.",
    "Treat response quality flags as evidence requiring evaluation, not automatic proof of fraud.",
    "Document every cleaning and analysis rule.",
    "Protect participant privacy throughout collection, storage, analysis, and publication.",
    "Interpret survey results within the limits of the sampling and measurement design.",
]

for principle in principles:
    print(f"- {principle}")


if __name__ == "__main__":
    print_section("Survey Design Study Complete")
    print(
        "This file is intentionally executable. Running it demonstrates "
        "survey-design concepts through progressively more advanced examples."
    )
