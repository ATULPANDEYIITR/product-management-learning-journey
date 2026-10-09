"""Prototype fidelity laboratory.

Models low-, medium-, and high-fidelity prototypes for a realistic
enterprise expense-management product. Demonstrates artifact structure,
interaction simulation, usability testing, validation, comparison metrics,
and evidence-based progression between fidelity levels.

Run with: python prototyping.py
Python 3.10+; standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Any, Callable
import json
import time


class Fidelity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PrototypeStatus(str, Enum):
    DRAFT = "draft"
    TESTABLE = "testable"
    RETIRED = "retired"


class PrototypeError(Exception):
    """Base exception for prototype-domain failures."""


class InvalidTransitionError(PrototypeError):
    """Raised when a prototype state transition is not permitted."""


class InvalidInteractionError(PrototypeError):
    """Raised when a user attempts an unsupported interaction."""


@dataclass(frozen=True)
class ScreenElement:
    """A visual or interactive element represented at a fidelity level."""

    identifier: str
    label: str
    element_type: str
    interactive: bool
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("Element identifier cannot be empty.")
        if not self.label.strip():
            raise ValueError("Element label cannot be empty.")
        if self.element_type not in {
            "text", "button", "input", "card", "table", "navigation"
        }:
            raise ValueError(f"Unsupported element type: {self.element_type}")


@dataclass
class Prototype:
    """An inspectable prototype with explicit scope and lifecycle."""

    identifier: str
    name: str
    fidelity: Fidelity
    target_users: tuple[str, ...]
    design_question: str
    screens: dict[str, list[ScreenElement]]
    status: PrototypeStatus = PrototypeStatus.DRAFT
    revision: int = 1
    assumptions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.name.strip():
            raise ValueError("Prototype identifier and name are required.")
        if not self.target_users:
            raise ValueError("At least one target-user group is required.")
        if not self.design_question.strip():
            raise ValueError("A testable design question is required.")
        if not self.screens:
            raise ValueError("A prototype must contain at least one screen.")
        for screen_name, elements in self.screens.items():
            if not screen_name.strip():
                raise ValueError("Screen names cannot be empty.")
            identifiers = [element.identifier for element in elements]
            if len(identifiers) != len(set(identifiers)):
                raise ValueError(f"Duplicate element IDs on screen {screen_name}.")

    def publish_for_testing(self) -> None:
        if self.status != PrototypeStatus.DRAFT:
            raise InvalidTransitionError(
                f"Cannot publish a prototype in state {self.status.value}."
            )
        self.status = PrototypeStatus.TESTABLE

    def retire(self) -> None:
        if self.status == PrototypeStatus.RETIRED:
            raise InvalidTransitionError("Prototype is already retired.")
        self.status = PrototypeStatus.RETIRED

    def revise(self, assumption: str) -> None:
        if self.status == PrototypeStatus.RETIRED:
            raise InvalidTransitionError("Retired prototypes cannot be revised.")
        if not assumption.strip():
            raise ValueError("A revision must record its design rationale.")
        self.revision += 1
        self.assumptions.append(assumption)


@dataclass
class InteractionResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class ExpenseWorkflow:
    """Domain behavior shared by interactive prototype experiments."""

    def __init__(self) -> None:
        self.expenses: list[dict[str, Any]] = []
        self.next_id = 1

    def submit_expense(
        self, description: str, amount: float, category: str
    ) -> dict[str, Any]:
        if not description.strip():
            raise ValueError("Expense description is required.")
        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")
        if not category.strip():
            raise ValueError("Expense category is required.")
        if amount > 1_000_000:
            raise ValueError("Expense exceeds the demonstration limit.")

        record = {
            "id": self.next_id,
            "description": description.strip(),
            "amount": round(amount, 2),
            "category": category.strip(),
            "status": "submitted",
        }
        self.expenses.append(record)
        self.next_id += 1
        return record.copy()


class LowFidelityPrototype:
    """Paper-style representation: layout and task sequence, not real UI."""

    def __init__(self) -> None:
        self.frames = {
            "Dashboard": [
                "[Expense summary]",
                "[Submit expense] -> Expense form",
                "[Recent expenses]",
            ],
            "Expense form": [
                "[Description: __________]",
                "[Amount: ______________]",
                "[Category: ____________]",
                "[Submit] -> Confirmation",
            ],
            "Confirmation": [
                "[Expense submitted]",
                "[Return to dashboard]",
            ],
        }

    def render(self, frame: str) -> str:
        if frame not in self.frames:
            raise InvalidInteractionError(f"Unknown paper frame: {frame}")
        return f"--- {frame} ---\n" + "\n".join(self.frames[frame])


class MediumFidelityPrototype:
    """Clickable structural simulation with navigation and form validation."""

    def __init__(self, workflow: ExpenseWorkflow) -> None:
        self.workflow = workflow
        self.current_screen = "dashboard"
        self.form: dict[str, Any] = {
            "description": "",
            "amount": "",
            "category": "",
        }
        self.last_message = ""

    def navigate(self, destination: str) -> InteractionResult:
        allowed = {
            "dashboard": {"new-expense", "history"},
            "new-expense": {"dashboard"},
            "history": {"dashboard"},
            "confirmation": {"dashboard", "history"},
        }
        if destination not in allowed.get(self.current_screen, set()):
            return InteractionResult(
                False,
                f"Navigation from {self.current_screen} to {destination} is not allowed.",
            )
        self.current_screen = destination
        return InteractionResult(True, f"Opened {destination}.")

    def update_field(self, name: str, value: Any) -> InteractionResult:
        if self.current_screen != "new-expense":
            return InteractionResult(False, "The expense form is not open.")
        if name not in self.form:
            return InteractionResult(False, f"Unknown field: {name}.")
        self.form[name] = value
        return InteractionResult(True, f"Updated {name}.")

    def submit(self) -> InteractionResult:
        if self.current_screen != "new-expense":
            return InteractionResult(False, "Open the expense form first.")
        try:
            raw_amount = self.form["amount"]
            if isinstance(raw_amount, bool):
                raise ValueError("Amount must be numeric.")
            amount = float(raw_amount)
            if not amount < float("inf"):
                raise ValueError("Amount must be finite.")
            record = self.workflow.submit_expense(
                str(self.form["description"]),
                amount,
                str(self.form["category"]),
            )
        except (ValueError, TypeError) as exc:
            self.last_message = str(exc)
            return InteractionResult(False, self.last_message)

        self.current_screen = "confirmation"
        self.last_message = "Expense submitted."
        self.form = {"description": "", "amount": "", "category": ""}
        return InteractionResult(True, self.last_message, record)


class HighFidelityPrototype:
    """Stateful interactive simulation with asynchronous feedback timing."""

    def __init__(self, workflow: ExpenseWorkflow) -> None:
        self.workflow = workflow
        self.current_screen = "dashboard"
        self.pending = False
        self.messages: list[str] = []

    def render_view_model(self) -> dict[str, Any]:
        return {
            "screen": self.current_screen,
            "loading": self.pending,
            "navigation": ["dashboard", "new-expense", "history"],
            "expenses": [item.copy() for item in self.workflow.expenses],
            "total": round(
                sum(item["amount"] for item in self.workflow.expenses), 2
            ),
            "messages": self.messages[-3:],
        }

    def submit(
        self,
        description: str,
        amount: float,
        category: str,
        simulated_latency_ms: int = 0,
    ) -> InteractionResult:
        if self.pending:
            return InteractionResult(False, "A submission is already in progress.")
        if simulated_latency_ms < 0 or simulated_latency_ms > 5000:
            return InteractionResult(False, "Latency must be between 0 and 5000 ms.")

        self.pending = True
        try:
            # A bounded delay lets usability tests observe loading-state design.
            if simulated_latency_ms:
                time.sleep(simulated_latency_ms / 1000)
            record = self.workflow.submit_expense(description, amount, category)
            self.current_screen = "confirmation"
            self.messages.append(f"Expense {record['id']} submitted.")
            return InteractionResult(True, "Submission completed.", record)
        except ValueError as exc:
            self.messages.append(f"Validation error: {exc}")
            return InteractionResult(False, str(exc))
        finally:
            # The UI must leave its loading state even after validation failure.
            self.pending = False


@dataclass(frozen=True)
class Task:
    name: str
    expected_outcome: str
    completion_threshold_seconds: float


@dataclass
class TestObservation:
    participant: str
    task_name: str
    completed: bool
    duration_seconds: float
    errors: int
    confidence: int

    def __post_init__(self) -> None:
        if self.duration_seconds < 0 or self.errors < 0:
            raise ValueError("Duration and error count cannot be negative.")
        if not 1 <= self.confidence <= 5:
            raise ValueError("Confidence must be between 1 and 5.")


@dataclass
class UsabilityReport:
    observations: list[TestObservation]

    def calculate(self) -> dict[str, Any]:
        if not self.observations:
            raise ValueError("At least one observation is required.")

        completed = sum(item.completed for item in self.observations)
        durations = [item.duration_seconds for item in self.observations]
        return {
            "participants": len(self.observations),
            "completion_rate": round(completed / len(self.observations), 3),
            "mean_duration_seconds": round(mean(durations), 2),
            "total_errors": sum(item.errors for item in self.observations),
            "mean_confidence": round(
                mean(item.confidence for item in self.observations), 2
            ),
        }


def build_prototypes() -> dict[Fidelity, Prototype]:
    """Create three artifacts whose capabilities match their fidelity."""
    return {
        Fidelity.LOW: Prototype(
            identifier="EXP-LOW",
            name="Expense flow paper sketch",
            fidelity=Fidelity.LOW,
            target_users=("employees", "finance reviewers"),
            design_question="Can employees identify the expense submission path?",
            screens={
                "dashboard": [
                    ScreenElement("submit", "Submit expense", "button", False),
                    ScreenElement("summary", "Expense summary", "card", False),
                ],
                "form": [
                    ScreenElement("description", "Description", "input", False),
                    ScreenElement("amount", "Amount", "input", False),
                ],
            },
            assumptions=["Employees understand the primary call to action."],
        ),
        Fidelity.MEDIUM: Prototype(
            identifier="EXP-MED",
            name="Clickable expense workflow",
            fidelity=Fidelity.MEDIUM,
            target_users=("employees",),
            design_question="Can users complete the form without assistance?",
            screens={
                "dashboard": [
                    ScreenElement("new", "New expense", "button", True),
                ],
                "form": [
                    ScreenElement("description", "Description", "input", True),
                    ScreenElement("amount", "Amount", "input", True),
                    ScreenElement("category", "Category", "input", True),
                ],
            },
            assumptions=["Inline validation will prevent common entry errors."],
        ),
        Fidelity.HIGH: Prototype(
            identifier="EXP-HIGH",
            name="Polished expense interaction model",
            fidelity=Fidelity.HIGH,
            target_users=("employees", "finance reviewers"),
            design_question="Do loading and confirmation states communicate system behavior?",
            screens={
                "dashboard": [
                    ScreenElement("new", "New expense", "button", True,
                                  {"style": "primary"}),
                    ScreenElement("total", "Total expenses", "card", True),
                ],
                "form": [
                    ScreenElement("description", "Description", "input", True,
                                  {"validation": "required"}),
                    ScreenElement("amount", "Amount", "input", True,
                                  {"minimum": 0.01, "maximum": 1_000_000}),
                    ScreenElement("submit", "Submit expense", "button", True,
                                  {"loading_state": True}),
                ],
                "confirmation": [
                    ScreenElement("success", "Expense submitted", "text", False),
                ],
            },
            assumptions=["Visible feedback reduces duplicate submissions."],
        ),
    }


def compare_fidelity(prototypes: dict[Fidelity, Prototype]) -> None:
    """Compare observable design characteristics, not subjective quality."""
    print("\nFidelity comparison")
    for fidelity in Fidelity:
        prototype = prototypes[fidelity]
        element_count = sum(len(items) for items in prototype.screens.values())
        interactive_count = sum(
            element.interactive
            for elements in prototype.screens.values()
            for element in elements
        )
        print(
            f"{fidelity.value:>6}: screens={len(prototype.screens)}, "
            f"elements={element_count}, interactive={interactive_count}, "
            f"revision={prototype.revision}"
        )


def run_usability_experiment() -> dict[str, Any]:
    """Use observations to identify problems before committing to production UI."""
    tasks = [
        Task(
            "submit-expense",
            "An expense appears in the submitted list",
            60.0,
        ),
        Task(
            "recover-invalid-amount",
            "An invalid amount is rejected with understandable feedback",
            30.0,
        ),
    ]
    print("\nUsability tasks")
    for task in tasks:
        print(f"{task.name}: {task.expected_outcome}")

    report = UsabilityReport([
        TestObservation("participant-A", "submit-expense", True, 24.0, 0, 5),
        TestObservation("participant-B", "submit-expense", True, 39.0, 1, 4),
        TestObservation("participant-C", "submit-expense", False, 60.0, 3, 2),
        TestObservation("participant-A", "recover-invalid-amount", True, 12.0, 1, 4),
        TestObservation("participant-B", "recover-invalid-amount", True, 18.0, 2, 3),
        TestObservation("participant-C", "recover-invalid-amount", True, 25.0, 1, 3),
    ])
    metrics = report.calculate()
    print("\nObserved usability metrics")
    print(json.dumps(metrics, indent=2))

    # A prototype can pass a completion-rate threshold while still exposing
    # unacceptable error counts or poor confidence. Metrics need interpretation.
    if metrics["completion_rate"] < 0.9:
        print("Decision: investigate task comprehension and navigation.")
    if metrics["total_errors"] > 3:
        print("Decision: inspect validation, labels, and recovery behavior.")
    return metrics


def demonstrate_interactions() -> None:
    workflow = ExpenseWorkflow()

    print("\nLow-fidelity paper representation")
    paper = LowFidelityPrototype()
    print(paper.render("Expense form"))

    print("\nMedium-fidelity interaction")
    medium = MediumFidelityPrototype(workflow)
    print(medium.navigate("new-expense"))
    medium.update_field("description", "Client travel")
    medium.update_field("amount", "1250.50")
    medium.update_field("category", "Travel")
    print(medium.submit())
    print(medium.submit())  # Repeated submission is rejected outside the form.

    print("\nMedium-fidelity validation failure")
    medium.navigate("new-expense")
    medium.update_field("description", "Office supplies")
    medium.update_field("amount", "-25")
    medium.update_field("category", "Supplies")
    print(medium.submit())

    print("\nHigh-fidelity state and feedback")
    high = HighFidelityPrototype(workflow)
    print(high.submit("Software subscription", 799.00, "Software", 5))
    print(json.dumps(high.render_view_model(), indent=2))

    print("\nHigh-fidelity validation failure")
    print(high.submit("Refund adjustment", 0, "Finance"))
    print(json.dumps(high.render_view_model(), indent=2))


def demonstrate_lifecycle(prototypes: dict[Fidelity, Prototype]) -> None:
    prototype = prototypes[Fidelity.MEDIUM]
    prototype.publish_for_testing()
    prototype.revise(
        "Testing showed that the amount field needs explicit currency context."
    )
    print(
        f"\nLifecycle: {prototype.identifier}, "
        f"status={prototype.status.value}, revision={prototype.revision}"
    )
    prototype.retire()
    try:
        prototype.revise("This change must be rejected.")
    except InvalidTransitionError as exc:
        print(f"Expected lifecycle protection: {exc}")


def main() -> None:
    prototypes = build_prototypes()
    compare_fidelity(prototypes)
    demonstrate_interactions()
    run_usability_experiment()
    demonstrate_lifecycle(prototypes)


if __name__ == "__main__":
    main()
