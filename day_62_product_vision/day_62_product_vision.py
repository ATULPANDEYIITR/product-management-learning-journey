from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple


class VisionStatus(Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    ACTIVE = "active"
    RETIRED = "retired"


class Horizon(Enum):
    NOW = "0-12 months"
    NEXT = "1-3 years"
    FUTURE = "3-5 years"


@dataclass(frozen=True)
class CustomerSegment:
    name: str
    needs: Tuple[str, ...]
    pain_points: Tuple[str, ...]


@dataclass
class VisionStatement:
    product: str
    statement: str
    customer_value: str
    strategic_direction: Tuple[str, ...]
    future_state: str
    horizon: Horizon
    status: VisionStatus = VisionStatus.DRAFT
    evidence: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.product.strip():
            errors.append("Product name is required.")
        if len(self.statement.strip()) < 30:
            errors.append("Vision statement is too short.")
        if not self.customer_value.strip():
            errors.append("Customer value is required.")
        if not self.future_state.strip():
            errors.append("Future state is required.")
        if not self.strategic_direction:
            errors.append("At least one strategic direction is required.")
        if not self.evidence:
            errors.append("At least one evidence item is required.")

        banned = {"feature", "button", "screen", "database table"}
        lowered = self.statement.lower()
        if any(word in lowered for word in banned):
            errors.append("Vision should describe an outcome, not implementation details.")

        return errors


class VisionError(Exception):
    pass


class VisionRepository:
    def __init__(self) -> None:
        self._visions: Dict[str, VisionStatement] = {}

    def save(self, vision: VisionStatement) -> None:
        errors = vision.validate()
        if errors:
            raise VisionError("; ".join(errors))
        self._visions[vision.product] = vision

    def get(self, product: str) -> VisionStatement:
        try:
            return self._visions[product]
        except KeyError as exc:
            raise VisionError(f"No vision exists for '{product}'.") from exc

    def all(self) -> List[VisionStatement]:
        return list(self._visions.values())


class VisionService:
    def __init__(self, repository: VisionRepository) -> None:
        self.repository = repository

    def validate(self, product: str) -> List[str]:
        return self.repository.get(product).validate()

    def approve(self, product: str) -> None:
        vision = self.repository.get(product)
        errors = vision.validate()
        if errors:
            raise VisionError("; ".join(errors))
        if vision.status not in {VisionStatus.DRAFT, VisionStatus.VALIDATED}:
            raise VisionError("Only draft or validated visions can be approved.")
        vision.status = VisionStatus.APPROVED

    def activate(self, product: str) -> None:
        vision = self.repository.get(product)
        if vision.status != VisionStatus.APPROVED:
            raise VisionError("Only approved visions can become active.")
        vision.status = VisionStatus.ACTIVE

    def retire(self, product: str) -> None:
        vision = self.repository.get(product)
        if vision.status != VisionStatus.ACTIVE:
            raise VisionError("Only active visions can be retired.")
        vision.status = VisionStatus.RETIRED


def calculate_alignment(
    vision: VisionStatement,
    strategic_priorities: Set[str],
    customer_segments: List[CustomerSegment],
) -> float:
    if not strategic_priorities:
        return 0.0

    direction_matches = sum(
        1
        for direction in vision.strategic_direction
        if direction.lower() in {item.lower() for item in strategic_priorities}
    )
    direction_score = min(direction_matches / len(strategic_priorities), 1.0)

    customer_terms = {
        item.lower()
        for segment in customer_segments
        for item in (*segment.needs, *segment.pain_points)
    }

    value_words = {
        word.strip(".,:;()").lower()
        for word in vision.customer_value.split()
        if len(word) > 3
    }

    customer_score = (
        len(value_words & customer_terms) / max(len(value_words), 1)
    )

    return round((direction_score * 0.6 + customer_score * 0.4) * 100, 2)


def evaluate_future_state(vision: VisionStatement) -> Dict[str, object]:
    return {
        "product": vision.product,
        "horizon": vision.horizon.value,
        "status": vision.status.value,
        "future_state_defined": bool(vision.future_state.strip()),
        "evidence_count": len(vision.evidence),
        "strategic_directions": len(vision.strategic_direction),
    }


def print_report(
    vision: VisionStatement,
    alignment_score: float,
) -> None:
    print("\nPRODUCT VISION REPORT")
    print("=" * 70)
    print(f"Product: {vision.product}")
    print(f"Status: {vision.status.value}")
    print(f"Horizon: {vision.horizon.value}")
    print(f"Vision: {vision.statement}")
    print(f"Customer value: {vision.customer_value}")
    print(f"Future state: {vision.future_state}")
    print(f"Strategic direction: {', '.join(vision.strategic_direction)}")
    print(f"Alignment score: {alignment_score:.2f}%")
    print(f"Evidence: {len(vision.evidence)}")


def main() -> None:
    customers = [
        CustomerSegment(
            name="Operations teams",
            needs=("visibility", "speed", "reliability"),
            pain_points=("manual work", "delayed decisions", "fragmented information"),
        ),
        CustomerSegment(
            name="Managers",
            needs=("control", "insight", "predictability"),
            pain_points=("unclear priorities", "slow reporting"),
        ),
    ]

    strategic_priorities = {
        "customer trust",
        "operational efficiency",
        "data-driven decisions",
        "scalable growth",
    }

    vision = VisionStatement(
        product="Operations Intelligence Platform",
        statement=(
            "Enable operations teams to make faster, more reliable decisions "
            "from a unified understanding of operational conditions."
        ),
        customer_value=(
            "Customers gain visibility, reduce decision delays, and improve "
            "operational reliability."
        ),
        strategic_direction=(
            "customer trust",
            "operational efficiency",
            "data-driven decisions",
            "scalable growth",
        ),
        future_state=(
            "Operations become measurable and predictable, with teams using "
            "shared information to identify problems early and coordinate action."
        ),
        horizon=Horizon.NEXT,
        evidence=[
            "Customer interviews identify fragmented operational information.",
            "Pilot users report delays caused by manual consolidation.",
            "Managers require consistent operational indicators.",
        ],
    )

    repository = VisionRepository()
    service = VisionService(repository)

    try:
        repository.save(vision)

        errors = service.validate(vision.product)
        if errors:
            raise VisionError("; ".join(errors))

        vision.status = VisionStatus.VALIDATED
        service.approve(vision.product)
        service.activate(vision.product)

        alignment = calculate_alignment(
            vision,
            strategic_priorities,
            customers,
        )

        print_report(vision, alignment)
        print("\nFUTURE-STATE EVALUATION")
        for key, value in evaluate_future_state(vision).items():
            print(f"{key}: {value}")

        # Edge-case validation: implementation details should not become
        # substitutes for an outcome-oriented product vision.
        invalid = VisionStatement(
            product="Invalid Product",
            statement="Add a button and database table for users.",
            customer_value="",
            strategic_direction=(),
            future_state="",
            horizon=Horizon.NOW,
        )

        invalid_errors = invalid.validate()
        assert invalid_errors
        assert any("implementation" in error.lower() for error in invalid_errors)

        # A missing product must fail safely rather than creating implicit state.
        try:
            service.activate("Unknown Product")
        except VisionError as exc:
            print(f"\nExpected failure: {exc}")

    except VisionError as exc:
        print(f"Vision processing failed: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
