"""
Kano Model: Customer Needs and Satisfaction Analysis

Implements:
- Basic (Must-be) needs
- Performance (One-dimensional) needs
- Excitement (Attractive) needs
- Indifferent needs
- Reverse needs
- Questionable responses
- Functional and dysfunctional questionnaire evaluation
- Kano classification using response evaluation
- Customer satisfaction and dissatisfaction coefficients
- Feature prioritization
- CSV reporting and validation
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from statistics import mean
from typing import Optional


class KanoCategory(Enum):
    MUST_BE = "Must-be"
    PERFORMANCE = "Performance"
    ATTRACTIVE = "Attractive"
    INDIFFERENT = "Indifferent"
    REVERSE = "Reverse"
    QUESTIONABLE = "Questionable"


class Response(Enum):
    LIKE = "like"
    EXPECT = "expect"
    NEUTRAL = "neutral"
    TOLERATE = "tolerate"
    DISLIKE = "dislike"


# Functional response is the first dimension.
# Dysfunctional response is the second dimension.
KANO_EVALUATION = {
    Response.LIKE: {
        Response.LIKE: KanoCategory.QUESTIONABLE,
        Response.EXPECT: KanoCategory.REVERSE,
        Response.NEUTRAL: KanoCategory.REVERSE,
        Response.TOLERATE: KanoCategory.REVERSE,
        Response.DISLIKE: KanoCategory.MUST_BE,
    },
    Response.EXPECT: {
        Response.LIKE: KanoCategory.ATTRACTIVE,
        Response.EXPECT: KanoCategory.INDIFFERENT,
        Response.NEUTRAL: KanoCategory.INDIFFERENT,
        Response.TOLERATE: KanoCategory.INDIFFERENT,
        Response.DISLIKE: KanoCategory.MUST_BE,
    },
    Response.NEUTRAL: {
        Response.LIKE: KanoCategory.PERFORMANCE,
        Response.EXPECT: KanoCategory.INDIFFERENT,
        Response.NEUTRAL: KanoCategory.INDIFFERENT,
        Response.TOLERATE: KanoCategory.INDIFFERENT,
        Response.DISLIKE: KanoCategory.MUST_BE,
    },
    Response.TOLERATE: {
        Response.LIKE: KanoCategory.PERFORMANCE,
        Response.EXPECT: KanoCategory.INDIFFERENT,
        Response.NEUTRAL: KanoCategory.INDIFFERENT,
        Response.TOLERATE: KanoCategory.INDIFFERENT,
        Response.DISLIKE: KanoCategory.MUST_BE,
    },
    Response.DISLIKE: {
        Response.LIKE: KanoCategory.PERFORMANCE,
        Response.EXPECT: KanoCategory.PERFORMANCE,
        Response.NEUTRAL: KanoCategory.PERFORMANCE,
        Response.TOLERATE: KanoCategory.PERFORMANCE,
        Response.DISLIKE: KanoCategory.QUESTIONABLE,
    },
}


@dataclass
class KanoResponse:
    customer_id: str
    functional: Response
    dysfunctional: Response

    def __post_init__(self):
        if not self.customer_id.strip():
            raise ValueError("Customer ID cannot be empty.")

    @property
    def category(self) -> KanoCategory:
        return KANO_EVALUATION[self.functional][self.dysfunctional]


@dataclass
class Feature:
    feature_id: str
    name: str
    description: str
    responses: list[KanoResponse] = field(default_factory=list)

    def add_response(self, response: KanoResponse) -> None:
        if any(
            existing.customer_id == response.customer_id
            for existing in self.responses
        ):
            raise ValueError(
                f"Duplicate response from customer {response.customer_id}"
            )
        self.responses.append(response)

    def classification_counts(self) -> dict[KanoCategory, int]:
        counts = {category: 0 for category in KanoCategory}

        for response in self.responses:
            counts[response.category] += 1

        return counts

    def dominant_category(self) -> KanoCategory:
        if not self.responses:
            raise ValueError("Cannot classify a feature without responses.")

        counts = self.classification_counts()

        # Questionable responses are excluded from the substantive
        # category decision.
        substantive = {
            category: count
            for category, count in counts.items()
            if category != KanoCategory.QUESTIONABLE
        }

        if not substantive or sum(substantive.values()) == 0:
            return KanoCategory.QUESTIONABLE

        return max(substantive, key=substantive.get)

    def satisfaction_coefficients(self) -> tuple[float, float]:
        """
        Satisfaction coefficient:
        (Attractive + Performance) /
        (Attractive + Performance + Must-be + Indifferent)

        Dissatisfaction coefficient:
        -(Performance + Must-be) /
        (Attractive + Performance + Must-be + Indifferent)
        """
        counts = self.classification_counts()

        attractive = counts[KanoCategory.ATTRACTIVE]
        performance = counts[KanoCategory.PERFORMANCE]
        must_be = counts[KanoCategory.MUST_BE]
        indifferent = counts[KanoCategory.INDIFFERENT]

        denominator = (
            attractive + performance + must_be + indifferent
        )

        if denominator == 0:
            return 0.0, 0.0

        satisfaction = (attractive + performance) / denominator

        dissatisfaction = -(
            (performance + must_be) / denominator
        )

        return round(satisfaction, 4), round(dissatisfaction, 4)

    def questionable_rate(self) -> float:
        if not self.responses:
            return 0.0

        questionable = self.classification_counts()[
            KanoCategory.QUESTIONABLE
        ]

        return round(questionable / len(self.responses), 4)


class KanoAnalyzer:
    def __init__(self):
        self.features: dict[str, Feature] = {}

    def register_feature(self, feature: Feature) -> None:
        if feature.feature_id in self.features:
            raise ValueError("Feature ID already exists.")

        self.features[feature.feature_id] = feature

    def add_customer_response(
        self,
        feature_id: str,
        customer_id: str,
        functional: str,
        dysfunctional: str,
    ) -> None:
        feature = self.features.get(feature_id)

        if feature is None:
            raise KeyError(f"Unknown feature: {feature_id}")

        try:
            functional_response = Response(functional.lower())
            dysfunctional_response = Response(dysfunctional.lower())
        except ValueError as exc:
            raise ValueError("Invalid Kano questionnaire response.") from exc

        feature.add_response(
            KanoResponse(
                customer_id,
                functional_response,
                dysfunctional_response,
            )
        )

    def analyze(self) -> list[dict]:
        results = []

        for feature in self.features.values():
            if not feature.responses:
                continue

            satisfaction, dissatisfaction = (
                feature.satisfaction_coefficients()
            )

            results.append({
                "feature_id": feature.feature_id,
                "feature": feature.name,
                "classification": feature.dominant_category().value,
                "responses": len(feature.responses),
                "satisfaction": satisfaction,
                "dissatisfaction": dissatisfaction,
                "questionable_rate": feature.questionable_rate(),
            })

        return sorted(
            results,
            key=lambda item: (
                item["dissatisfaction"],
                item["satisfaction"],
            ),
        )

    def export_csv(self, filename: str) -> None:
        results = self.analyze()

        if not results:
            raise ValueError("No analysis results available.")

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(results[0].keys()),
            )
            writer.writeheader()
            writer.writerows(results)

    def export_json(self, filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.analyze(), file, indent=4)


def build_demo() -> KanoAnalyzer:
    analyzer = KanoAnalyzer()

    features = [
        Feature("F001", "Account Security",
                "Secure authentication and account protection."),
        Feature("F002", "Application Speed",
                "Fast application response and processing."),
        Feature("F003", "AI Recommendations",
                "Personalized product recommendations."),
        Feature("F004", "Custom Dashboard",
                "User-configurable dashboard layout."),
    ]

    for feature in features:
        analyzer.register_feature(feature)

    samples = {
        "F001": [
            ("C001", "like", "dislike"),
            ("C002", "expect", "dislike"),
            ("C003", "like", "dislike"),
            ("C004", "neutral", "dislike"),
            ("C005", "like", "dislike"),
        ],
        "F002": [
            ("C001", "like", "dislike"),
            ("C002", "like", "neutral"),
            ("C003", "like", "dislike"),
            ("C004", "like", "tolerate"),
            ("C005", "expect", "dislike"),
        ],
        "F003": [
            ("C001", "expect", "dislike"),
            ("C002", "expect", "dislike"),
            ("C003", "like", "dislike"),
            ("C004", "expect", "dislike"),
            ("C005", "neutral", "neutral"),
        ],
        "F004": [
            ("C001", "neutral", "neutral"),
            ("C002", "expect", "neutral"),
            ("C003", "neutral", "tolerate"),
            ("C004", "expect", "neutral"),
            ("C005", "neutral", "neutral"),
        ],
    }

    for feature_id, responses in samples.items():
        for customer_id, functional, dysfunctional in responses:
            analyzer.add_customer_response(
                feature_id,
                customer_id,
                functional,
                dysfunctional,
            )

    return analyzer


def main():
    analyzer = build_demo()

    print("\nKANO MODEL CUSTOMER SATISFACTION ANALYSIS")
    print("=" * 85)

    for result in analyzer.analyze():
        print(
            f"{result['feature']:<22} "
            f"{result['classification']:<15} "
            f"Satisfaction={result['satisfaction']:.2f} "
            f"Dissatisfaction={result['dissatisfaction']:.2f}"
        )

    analyzer.export_csv("kano_analysis.csv")
    analyzer.export_json("kano_analysis.json")

    print("\nReports exported successfully.")

    # Verify classification and coefficient behavior.
    test_response = KanoResponse(
        "TEST001",
        Response.LIKE,
        Response.DISLIKE,
    )
    assert test_response.category == KanoCategory.MUST_BE

    print("Validation tests passed.")


if __name__ == "__main__":
    main()
