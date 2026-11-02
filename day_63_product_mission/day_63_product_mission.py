from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
from typing import Iterable


class MissionType(Enum):
    ORGANIZATIONAL = "organizational"
    PRODUCT = "product"


class MissionStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class MissionValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Mission:
    name: str
    statement: str
    purpose: str
    mission_type: MissionType
    status: MissionStatus = MissionStatus.DRAFT
    strategic_themes: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.name.strip():
            raise MissionValidationError("Mission name cannot be empty.")
        if not self.statement.strip():
            raise MissionValidationError("Mission statement cannot be empty.")
        if not self.purpose.strip():
            raise MissionValidationError("Mission purpose cannot be empty.")

        if len(self.statement.strip()) > 300:
            raise MissionValidationError(
                f"Mission statement for '{self.name}' exceeds 300 characters."
            )

        if len(set(theme.lower() for theme in self.strategic_themes)) != len(
            self.strategic_themes
        ):
            raise MissionValidationError(
                f"Mission '{self.name}' contains duplicate strategic themes."
            )


@dataclass
class Product:
    name: str
    organizational_mission: Mission
    product_mission: Mission
    metrics: dict[str, float] = field(default_factory=dict)

    def validate_alignment(self) -> list[str]:
        self.organizational_mission.validate()
        self.product_mission.validate()

        if self.organizational_mission.mission_type != MissionType.ORGANIZATIONAL:
            raise MissionValidationError(
                "The organizational mission must have organizational type."
            )

        if self.product_mission.mission_type != MissionType.PRODUCT:
            raise MissionValidationError(
                "The product mission must have product type."
            )

        org_themes = {
            theme.lower() for theme in self.organizational_mission.strategic_themes
        }
        product_themes = {
            theme.lower() for theme in self.product_mission.strategic_themes
        }

        shared = sorted(org_themes & product_themes)
        if not shared:
            raise MissionValidationError(
                f"Product '{self.name}' has no strategic-theme alignment "
                "with the organizational mission."
            )

        return shared

    def score_purpose_clarity(self) -> float:
        statement_words = set(self.product_mission.statement.lower().split())
        purpose_words = set(self.product_mission.purpose.lower().split())

        meaningful_statement = {
            word.strip(".,:;()") for word in statement_words if len(word) > 3
        }
        meaningful_purpose = {
            word.strip(".,:;()") for word in purpose_words if len(word) > 3
        }

        if not meaningful_statement or not meaningful_purpose:
            return 0.0

        overlap = len(meaningful_statement & meaningful_purpose)
        denominator = max(
            len(meaningful_statement),
            len(meaningful_purpose),
        )

        return round(overlap / denominator * 100, 2)

    def evaluate(self) -> dict:
        shared_themes = self.validate_alignment()
        clarity = self.score_purpose_clarity()

        return {
            "product": self.name,
            "organizational_mission": self.organizational_mission.statement,
            "product_mission": self.product_mission.statement,
            "shared_strategic_themes": shared_themes,
            "purpose_clarity_score": clarity,
            "metric_count": len(self.metrics),
            "status": self.product_mission.status.value,
        }


def save_evaluation(path: Path, evaluation: dict) -> None:
    path.write_text(
        json.dumps(evaluation, indent=2),
        encoding="utf-8",
    )


def load_evaluation(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Evaluation file does not exist: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid evaluation JSON: {path}") from exc


def find_products_by_theme(
    products: Iterable[Product],
    theme: str,
) -> list[str]:
    normalized = theme.strip().lower()
    if not normalized:
        raise ValueError("Theme cannot be empty.")

    matches = []

    for product in products:
        themes = {
            item.lower()
            for item in product.product_mission.strategic_themes
        }
        if normalized in themes:
            matches.append(product.name)

    return sorted(matches)


def main() -> None:
    organizational_mission = Mission(
        name="Acme Organizational Mission",
        statement=(
            "Improve access to trustworthy digital services by making "
            "essential customer interactions simpler and more reliable."
        ),
        purpose=(
            "The organization exists to deliver dependable services that "
            "solve important customer problems."
        ),
        mission_type=MissionType.ORGANIZATIONAL,
        status=MissionStatus.ACTIVE,
        strategic_themes=("customer trust", "simplicity", "reliability"),
    )

    payments_mission = Mission(
        name="Payments Product Mission",
        statement=(
            "Enable customers to complete everyday payments quickly, "
            "clearly, and reliably."
        ),
        purpose=(
            "The payments product exists to reduce friction in everyday "
            "transactions while preserving customer trust and reliability."
        ),
        mission_type=MissionType.PRODUCT,
        status=MissionStatus.ACTIVE,
        strategic_themes=("customer trust", "simplicity", "reliability"),
    )

    payments = Product(
        name="Acme Pay",
        organizational_mission=organizational_mission,
        product_mission=payments_mission,
        metrics={
            "successful_transaction_rate": 99.2,
            "payment_completion_time_seconds": 18.5,
            "customer_satisfaction": 91.4,
        },
    )

    evaluation = payments.evaluate()

    output_path = Path("product_mission_evaluation.json")
    save_evaluation(output_path, evaluation)
    loaded = load_evaluation(output_path)

    print("PRODUCT MISSION EVALUATION")
    print("=" * 32)
    print(f"Product: {loaded['product']}")
    print(f"Organizational mission: {loaded['organizational_mission']}")
    print(f"Product mission: {loaded['product_mission']}")
    print(
        "Shared strategic themes: "
        + ", ".join(loaded["shared_strategic_themes"])
    )
    print(
        f"Purpose clarity score: "
        f"{loaded['purpose_clarity_score']:.2f}%"
    )
    print(f"Operational metrics: {loaded['metric_count']}")
    print(f"Mission status: {loaded['status']}")
    print(f"Saved evaluation: {output_path.resolve()}")

    assert payments.product_mission.mission_type == MissionType.PRODUCT
    assert "customer trust" in evaluation["shared_strategic_themes"]
    assert evaluation["purpose_clarity_score"] > 0

    print("\nTHEME SEARCH")
    print("=" * 32)
    print(
        find_products_by_theme(
            [payments],
            "reliability",
        )
    )

    try:
        invalid_product_mission = Mission(
            name="Invalid Mission",
            statement="",
            purpose="",
            mission_type=MissionType.PRODUCT,
        )
        invalid_product_mission.validate()
    except MissionValidationError as exc:
        print(f"\nValidation failure handled: {exc}")


if __name__ == "__main__":
    main()
