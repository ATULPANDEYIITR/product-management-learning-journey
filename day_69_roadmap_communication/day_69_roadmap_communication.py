#!/usr/bin/env python3
"""
Roadmap Communication
Executive, Engineering, Sales, and Customer Roadmap Management.

Features:
- Structured roadmap domain model
- Audience-specific communication
- Milestone and dependency management
- Priority and status tracking
- Progress and risk evaluation
- Timeline validation
- JSON export and import
- Executive summaries
- Engineering delivery details
- Sales enablement messages
- Customer-facing updates
- Automated validation and tests

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("roadmap")


class Audience(str, Enum):
    EXECUTIVE = "executive"
    ENGINEERING = "engineering"
    SALES = "sales"
    CUSTOMER = "customer"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Milestone:
    milestone_id: str
    name: str
    target_date: date
    status: Status = Status.PLANNED
    completion_percentage: float = 0.0

    def validate(self) -> None:
        if not self.milestone_id.strip() or not self.name.strip():
            raise ValueError("Milestone ID and name are required.")

        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion must be between 0 and 100.")

        if self.status == Status.COMPLETED:
            self.completion_percentage = 100.0


@dataclass
class RoadmapItem:
    item_id: str
    title: str
    description: str
    priority: Priority
    status: Status
    start_date: date
    target_date: date
    owner: str
    strategic_objective: str
    business_value: str
    dependencies: list[str] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    completion_percentage: float = 0.0
    confidence: Confidence = Confidence.MEDIUM
    risk: Optional[str] = None
    customer_impact: str = ""
    sales_message: str = ""
    engineering_details: str = ""

    def validate(self) -> None:
        required = [
            self.item_id,
            self.title,
            self.description,
            self.owner,
            self.strategic_objective
        ]

        if any(not value.strip() for value in required):
            raise ValueError("Required roadmap fields cannot be empty.")

        if self.target_date < self.start_date:
            raise ValueError("Target date cannot precede start date.")

        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion must be between 0 and 100.")

        if self.status == Status.COMPLETED:
            self.completion_percentage = 100.0

        if self.status == Status.PLANNED and self.completion_percentage > 0:
            raise ValueError(
                "A planned item cannot have reported implementation progress."
            )

        for milestone in self.milestones:
            milestone.validate()


class Roadmap:
    def __init__(self, name: str, owner: str):
        if not name.strip() or not owner.strip():
            raise ValueError("Roadmap name and owner are required.")

        self.name = name
        self.owner = owner
        self.items: dict[str, RoadmapItem] = {}
        self.version = 1

    def add_item(self, item: RoadmapItem) -> None:
        item.validate()

        if item.item_id in self.items:
            raise ValueError(f"Duplicate roadmap item: {item.item_id}")

        self.items[item.item_id] = item
        self._validate_dependencies()
        self.version += 1

    def update_status(
        self,
        item_id: str,
        status: Status,
        completion: Optional[float] = None
    ) -> None:
        item = self.get_item(item_id)

        previous_status = item.status

        if previous_status == Status.CANCELLED:
            raise ValueError("Cancelled items cannot be updated.")

        if previous_status == Status.COMPLETED and status != Status.COMPLETED:
            raise ValueError("Completed items require an explicit correction workflow.")

        if completion is not None:
            if not 0 <= completion <= 100:
                raise ValueError("Invalid completion percentage.")
            item.completion_percentage = completion

        item.status = status

        if status == Status.COMPLETED:
            item.completion_percentage = 100.0

        if status == Status.PLANNED and item.completion_percentage > 0:
            item.status = previous_status
            raise ValueError("Planned items cannot have implementation progress.")

        self.version += 1

    def get_item(self, item_id: str) -> RoadmapItem:
        try:
            return self.items[item_id]
        except KeyError as exc:
            raise KeyError(f"Unknown roadmap item: {item_id}") from exc

    def _validate_dependencies(self) -> None:
        for item in self.items.values():
            for dependency in item.dependencies:
                if dependency not in self.items:
                    raise ValueError(
                        f"{item.item_id} depends on unknown item {dependency}"
                    )

        visited: set[str] = set()
        active: set[str] = set()

        def visit(item_id: str) -> None:
            if item_id in active:
                raise ValueError("Circular roadmap dependency detected.")

            if item_id in visited:
                return

            active.add(item_id)

            for dependency in self.items[item_id].dependencies:
                visit(dependency)

            active.remove(item_id)
            visited.add(item_id)

        for item_id in self.items:
            visit(item_id)

    def dependency_readiness(self, item_id: str) -> bool:
        item = self.get_item(item_id)

        return all(
            self.get_item(dependency).status == Status.COMPLETED
            for dependency in item.dependencies
        )

    def calculate_progress(self) -> float:
        if not self.items:
            return 0.0

        total = sum(
            item.completion_percentage
            for item in self.items.values()
            if item.status != Status.CANCELLED
        )

        active_count = sum(
            item.status != Status.CANCELLED
            for item in self.items.values()
        )

        return total / active_count if active_count else 0.0

    def risk_register(self) -> list[dict]:
        return [
            {
                "item_id": item.item_id,
                "title": item.title,
                "status": item.status.value,
                "risk": item.risk,
                "confidence": item.confidence.value
            }
            for item in self.items.values()
            if item.status in {Status.BLOCKED, Status.AT_RISK}
            or item.risk
        ]

    def generate_communication(self, audience: Audience) -> str:
        if audience == Audience.EXECUTIVE:
            return self._executive_roadmap()

        if audience == Audience.ENGINEERING:
            return self._engineering_roadmap()

        if audience == Audience.SALES:
            return self._sales_roadmap()

        if audience == Audience.CUSTOMER:
            return self._customer_roadmap()

        raise ValueError("Unsupported communication audience.")

    def _executive_roadmap(self) -> str:
        lines = [
            f"EXECUTIVE ROADMAP: {self.name}",
            f"Accountable owner: {self.owner}",
            f"Portfolio completion: {self.calculate_progress():.1f}%",
            "",
            "STRATEGIC INITIATIVES"
        ]

        for item in self.items.values():
            lines.extend([
                f"- {item.title}",
                f"  Business objective: {item.strategic_objective}",
                f"  Expected value: {item.business_value}",
                f"  Status: {item.status.value}",
                f"  Target: {item.target_date}",
                f"  Confidence: {item.confidence.value}",
                f"  Risk: {item.risk or 'No reported risk'}"
            ])

        lines.append("\nDECISIONS AND RISKS")

        risks = self.risk_register()

        if not risks:
            lines.append("No outstanding risks reported.")
        else:
            for risk in risks:
                lines.append(
                    f"- {risk['title']}: {risk['risk'] or risk['status']}"
                )

        return "\n".join(lines)

    def _engineering_roadmap(self) -> str:
        lines = [
            f"ENGINEERING DELIVERY ROADMAP: {self.name}",
            ""
        ]

        for item in self.items.values():
            lines.extend([
                f"INITIATIVE: {item.title}",
                f"Owner: {item.owner}",
                f"Status: {item.status.value}",
                f"Priority: {item.priority.value}",
                f"Implementation: {item.engineering_details}",
                f"Progress: {item.completion_percentage:.1f}%",
                f"Dependencies: {', '.join(item.dependencies) or 'None'}",
                f"Dependencies ready: {self.dependency_readiness(item.item_id)}",
                f"Target date: {item.target_date}",
                f"Risk: {item.risk or 'None'}"
            ])

            for milestone in item.milestones:
                lines.append(
                    f"  Milestone: {milestone.name} | "
                    f"{milestone.status.value} | "
                    f"{milestone.target_date}"
                )

            lines.append("")

        return "\n".join(lines)

    def _sales_roadmap(self) -> str:
        lines = [
            f"SALES ENABLEMENT ROADMAP: {self.name}",
            ""
        ]

        for item in self.items.values():
            if item.status == Status.CANCELLED:
                continue

            lines.extend([
                f"FEATURE: {item.title}",
                f"Customer value: {item.business_value}",
                f"Sales positioning: {item.sales_message}",
                f"Availability status: {item.status.value}",
                f"Target availability: {item.target_date}",
                f"Confidence: {item.confidence.value}",
                ""
            ])

        lines.append(
            "Sales teams must distinguish planned capabilities "
            "from released and commercially available capabilities."
        )

        return "\n".join(lines)

    def _customer_roadmap(self) -> str:
        lines = [
            f"PRODUCT ROADMAP UPDATE: {self.name}",
            "",
            "PRODUCT DEVELOPMENTS"
        ]

        for item in self.items.values():
            if item.status in {Status.CANCELLED, Status.BLOCKED}:
                continue

            public_status = {
                Status.PLANNED: "Planned",
                Status.IN_PROGRESS: "In development",
                Status.AT_RISK: "Under review",
                Status.COMPLETED: "Completed"
            }[item.status]

            lines.extend([
                f"- {item.title}",
                f"  Status: {public_status}",
                f"  Expected value: {item.customer_impact or item.business_value}",
                f"  Target: {item.target_date}",
                ""
            ])

        lines.append(
            "Dates are targets, not guaranteed delivery commitments. "
            "Changes will be communicated through subsequent updates."
        )

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "owner": self.owner,
            "version": self.version,
            "items": [
                {
                    **asdict(item),
                    "priority": item.priority.value,
                    "status": item.status.value,
                    "confidence": item.confidence.value,
                    "start_date": item.start_date.isoformat(),
                    "target_date": item.target_date.isoformat(),
                    "milestones": [
                        {
                            **asdict(milestone),
                            "target_date": milestone.target_date.isoformat(),
                            "status": milestone.status.value
                        }
                        for milestone in item.milestones
                    ]
                }
                for item in self.items.values()
            ]
        }

    def export_json(self, filepath: str) -> None:
        destination = Path(filepath)

        # Write to a temporary file before replacing the destination.
        temporary = destination.with_suffix(destination.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(self.to_dict(), indent=2),
                encoding="utf-8"
            )
            temporary.replace(destination)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    @classmethod
    def import_json(cls, filepath: str) -> Roadmap:
        data = json.loads(Path(filepath).read_text(encoding="utf-8"))

        roadmap = cls(data["name"], data["owner"])

        for record in data["items"]:
            milestones = [
                Milestone(
                    milestone_id=m["milestone_id"],
                    name=m["name"],
                    target_date=date.fromisoformat(m["target_date"]),
                    status=Status(m["status"]),
                    completion_percentage=m["completion_percentage"]
                )
                for m in record["milestones"]
            ]

            item = RoadmapItem(
                item_id=record["item_id"],
                title=record["title"],
                description=record["description"],
                priority=Priority(record["priority"]),
                status=Status(record["status"]),
                start_date=date.fromisoformat(record["start_date"]),
                target_date=date.fromisoformat(record["target_date"]),
                owner=record["owner"],
                strategic_objective=record["strategic_objective"],
                business_value=record["business_value"],
                dependencies=record["dependencies"],
                milestones=milestones,
                completion_percentage=record["completion_percentage"],
                confidence=Confidence(record["confidence"]),
                risk=record["risk"],
                customer_impact=record["customer_impact"],
                sales_message=record["sales_message"],
                engineering_details=record["engineering_details"]
            )

            roadmap.add_item(item)

        roadmap.version = data.get("version", roadmap.version)
        return roadmap


def create_sample_roadmap() -> Roadmap:
    roadmap = Roadmap(
        name="Enterprise Product Platform 2027",
        owner="Product Management Office"
    )

    roadmap.add_item(
        RoadmapItem(
            item_id="RM-001",
            title="Identity and Access Management",
            description="Centralized enterprise authentication.",
            priority=Priority.CRITICAL,
            status=Status.COMPLETED,
            start_date=date(2026, 10, 1),
            target_date=date(2026, 12, 15),
            owner="Platform Engineering",
            strategic_objective="Improve enterprise security.",
            business_value="Reduced access-management risk.",
            completion_percentage=100,
            confidence=Confidence.HIGH,
            customer_impact="Centralized account security.",
            sales_message="Enterprise identity controls are available.",
            engineering_details="OAuth 2.0, OIDC and role-based access control.",
            milestones=[
                Milestone(
                    "MS-001",
                    "Authentication service",
                    date(2026, 11, 15),
                    Status.COMPLETED,
                    100
                )
            ]
        )
    )

    roadmap.add_item(
        RoadmapItem(
            item_id="RM-002",
            title="Advanced Analytics Dashboard",
            description="Interactive operational analytics.",
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS,
            start_date=date(2026, 11, 1),
            target_date=date(2027, 2, 15),
            owner="Data Engineering",
            strategic_objective="Increase decision visibility.",
            business_value="Faster operational decisions.",
            dependencies=["RM-001"],
            completion_percentage=55,
            confidence=Confidence.MEDIUM,
            customer_impact="Better visibility into business performance.",
            sales_message="Advanced analytics for operational decision-making.",
            engineering_details="Event ingestion, aggregation APIs and dashboard UI.",
            milestones=[
                Milestone(
                    "MS-002",
                    "Data ingestion",
                    date(2026, 12, 15),
                    Status.COMPLETED,
                    100
                ),
                Milestone(
                    "MS-003",
                    "Dashboard integration",
                    date(2027, 1, 30),
                    Status.IN_PROGRESS,
                    40
                )
            ]
        )
    )

    roadmap.add_item(
        RoadmapItem(
            item_id="RM-003",
            title="Customer Self-Service Portal",
            description="Customer-facing account and service portal.",
            priority=Priority.MEDIUM,
            status=Status.PLANNED,
            start_date=date(2027, 1, 1),
            target_date=date(2027, 4, 30),
            owner="Customer Experience Team",
            strategic_objective="Improve customer autonomy.",
            business_value="Reduced support workload.",
            dependencies=["RM-001"],
            confidence=Confidence.HIGH,
            customer_impact="Simplified account and service management.",
            sales_message="A self-service experience is planned.",
            engineering_details="Frontend portal and customer API integration."
        )
    )

    roadmap.add_item(
        RoadmapItem(
            item_id="RM-004",
            title="Automated Reporting",
            description="Scheduled enterprise reporting.",
            priority=Priority.HIGH,
            status=Status.AT_RISK,
            start_date=date(2026, 11, 15),
            target_date=date(2027, 3, 15),
            owner="Business Intelligence Team",
            strategic_objective="Standardize reporting.",
            business_value="Lower manual reporting effort.",
            dependencies=["RM-002"],
            completion_percentage=20,
            confidence=Confidence.LOW,
            risk="Data integration capacity is constrained.",
            customer_impact="Consistent scheduled business reports.",
            sales_message="Automated reporting is under development.",
            engineering_details="Scheduled jobs, report templates and export APIs."
        )
    )

    return roadmap


def run_tests(roadmap: Roadmap) -> None:
    assert len(roadmap.items) == 4
    assert roadmap.calculate_progress() == 43.75
    assert roadmap.dependency_readiness("RM-002")
    assert not roadmap.dependency_readiness("RM-004")

    try:
        roadmap.add_item(
            RoadmapItem(
                item_id="RM-005",
                title="Invalid dependency",
                description="Validation test.",
                priority=Priority.LOW,
                status=Status.PLANNED,
                start_date=date(2027, 1, 1),
                target_date=date(2027, 2, 1),
                owner="Testing",
                strategic_objective="Test validation.",
                business_value="None",
                dependencies=["UNKNOWN"]
            )
        )
        raise AssertionError("Unknown dependencies must be rejected.")
    except ValueError:
        pass

    try:
        RoadmapItem(
            item_id="INVALID",
            title="Invalid dates",
            description="Test",
            priority=Priority.LOW,
            status=Status.PLANNED,
            start_date=date(2027, 5, 1),
            target_date=date(2027, 1, 1),
            owner="Testing",
            strategic_objective="Validation",
            business_value="None"
        ).validate()
        raise AssertionError("Invalid dates must be rejected.")
    except ValueError:
        pass

    logger.info("All roadmap validation tests passed.")


def main() -> None:
    roadmap = create_sample_roadmap()

    run_tests(roadmap)

    for audience in Audience:
        print("\n" + "=" * 75)
        print(roadmap.generate_communication(audience))

    print("\n" + "=" * 75)
    print("PORTFOLIO METRICS")
    print(f"Roadmap version: {roadmap.version}")
    print(f"Progress: {roadmap.calculate_progress():.2f}%")
    print(f"Risk items: {len(roadmap.risk_register())}")

    roadmap.export_json("roadmap.json")
    logger.info("Roadmap exported to roadmap.json")


if __name__ == "__main__":
    main()
