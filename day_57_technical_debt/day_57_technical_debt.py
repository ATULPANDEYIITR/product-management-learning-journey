from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Iterable
import json
import math
import tempfile


class DebtCategory(Enum):
    CODE = "code"
    TEST = "test"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"


class DebtStatus(Enum):
    OPEN = "open"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str
    author: str
    changed_files: int
    additions: int
    deletions: int


@dataclass
class TechnicalDebtItem:
    item_id: int
    title: str
    category: DebtCategory
    description: str
    owner: str
    principal_hours: float
    remediation_hours: float
    interest_hours_per_month: float
    impact: int
    probability: float
    urgency: int
    security_exposure: int
    affected_components: set[str]
    status: DebtStatus = DebtStatus.OPEN
    created_on: date = field(default_factory=date.today)
    last_reviewed: date | None = None

    def validate(self) -> None:
        if self.principal_hours <= 0:
            raise ValueError("Debt principal must be positive.")
        if self.remediation_hours <= 0:
            raise ValueError("Remediation estimate must be positive.")
        if not 1 <= self.impact <= 10:
            raise ValueError("Impact must be between 1 and 10.")
        if not 0 <= self.probability <= 1:
            raise ValueError("Probability must be between 0 and 1.")
        if not 1 <= self.urgency <= 10:
            raise ValueError("Urgency must be between 1 and 10.")
        if not 0 <= self.security_exposure <= 10:
            raise ValueError("Security exposure must be between 0 and 10.")
        if not self.owner.strip():
            raise ValueError("Every debt item requires an owner.")

    @property
    def monthly_interest(self) -> float:
        return max(self.interest_hours_per_month, 0.0)

    @property
    def risk_score(self) -> float:
        return (
            self.impact * self.probability * 10
            + self.urgency * 2
            + self.security_exposure * 3
        )

    @property
    def estimated_cost(self) -> float:
        return self.principal_hours + self.remediation_hours

    @property
    def priority_score(self) -> float:
        # A high score means that leaving the item unresolved is expensive.
        score = (
            self.monthly_interest * 4
            + self.risk_score * 2
            + self.security_exposure * 5
        ) / max(self.remediation_hours, 1.0)
        return round(score, 2)

    @property
    def priority(self) -> Priority:
        score = self.priority_score
        if score >= 70:
            return Priority.CRITICAL
        if score >= 40:
            return Priority.HIGH
        if score >= 20:
            return Priority.MEDIUM
        return Priority.LOW

    def projected_interest(self, months: int) -> float:
        if months < 0:
            raise ValueError("Months cannot be negative.")
        # Simple linear model intentionally exposes the assumption.
        return self.monthly_interest * months


@dataclass(frozen=True)
class StatusCheck:
    name: str
    passed: bool
    required: bool
    details: str = ""


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    submitted_at: datetime
    comments: list[str] = field(default_factory=list)

    @property
    def is_approval(self) -> bool:
        return self.state == ReviewState.APPROVED


@dataclass
class PullRequest:
    number: int
    title: str
    source_branch: str
    target_branch: str
    author: str
    commits: list[Commit]
    draft: bool = False
    open: bool = True
    reviews: list[Review] = field(default_factory=list)
    status_checks: list[StatusCheck] = field(default_factory=list)
    technical_debt_ids: set[int] = field(default_factory=set)
    merge_strategy: str = "squash"
    synchronized_with_base: bool = True
    has_conflicts: bool = False

    def changed_files(self) -> int:
        return sum(c.changed_files for c in self.commits)

    def add_review(self, review: Review) -> None:
        if not self.open:
            raise ValueError("Closed Pull Requests cannot receive new reviews.")
        self.reviews.append(review)

    def approval_count(self) -> int:
        return sum(
            1
            for review in self.reviews
            if review.state == ReviewState.APPROVED
        )

    def unresolved_change_requests(self) -> int:
        return sum(
            1
            for review in self.reviews
            if review.state == ReviewState.CHANGES_REQUESTED
        )

    def required_checks_passed(self) -> bool:
        return all(check.passed for check in self.status_checks if check.required)

    def reopen(self) -> None:
        self.open = True

    def close(self) -> None:
        self.open = False

    def synchronize(self) -> None:
        self.synchronized_with_base = True
        self.has_conflicts = False


@dataclass(frozen=True)
class BranchProtection:
    branch: str
    required_reviews: int
    required_status_checks: tuple[str, ...]
    require_conversation_resolution: bool
    restrict_direct_push: bool
    restrict_force_push: bool
    restrict_deletion: bool
    require_linear_history: bool
    allow_bypass_for_admin: bool
    max_new_debt_score: float


class Repository:
    def __init__(self, name: str) -> None:
        self.name = name
        self.branches: dict[str, list[Commit]] = {}
        self.debt: dict[int, TechnicalDebtItem] = {}
        self.pull_requests: dict[int, PullRequest] = {}
        self.protection: dict[str, BranchProtection] = {}
        self.next_debt_id = 1
        self.next_pr_number = 1

    def create_branch(self, name: str) -> None:
        if not name or name in self.branches:
            raise ValueError(f"Invalid or duplicate branch: {name}")
        self.branches[name] = []

    def add_commit(self, branch: str, commit: Commit) -> None:
        if branch not in self.branches:
            raise KeyError(f"Unknown branch: {branch}")
        if not commit.sha or len(commit.sha) < 7:
            raise ValueError("Commit SHA is too short.")
        self.branches[branch].append(commit)

    def add_debt(self, item: TechnicalDebtItem) -> int:
        item.validate()
        if item.item_id != self.next_debt_id:
            raise ValueError("Debt IDs must be sequential in this repository.")
        self.debt[item.item_id] = item
        self.next_debt_id += 1
        return item.item_id

    def create_pull_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        author: str,
        commits: list[Commit],
        *,
        draft: bool = False,
        technical_debt_ids: Iterable[int] = (),
    ) -> PullRequest:
        if source_branch not in self.branches:
            raise KeyError(f"Unknown source branch: {source_branch}")
        if target_branch not in self.branches:
            raise KeyError(f"Unknown target branch: {target_branch}")
        if source_branch == target_branch:
            raise ValueError("A Pull Request needs different source and target branches.")
        if not title.strip() or not author.strip():
            raise ValueError("Pull Request title and author are required.")

        debt_ids = set(technical_debt_ids)
        unknown = debt_ids - self.debt.keys()
        if unknown:
            raise ValueError(f"Unknown technical debt IDs: {sorted(unknown)}")

        pr = PullRequest(
            number=self.next_pr_number,
            title=title,
            source_branch=source_branch,
            target_branch=target_branch,
            author=author,
            commits=commits,
            draft=draft,
            technical_debt_ids=debt_ids,
        )
        self.pull_requests[pr.number] = pr
        self.next_pr_number += 1
        return pr

    def set_protection(self, policy: BranchProtection) -> None:
        if policy.branch not in self.branches:
            raise KeyError(f"Unknown protected branch: {policy.branch}")
        self.protection[policy.branch] = policy

    def debt_score_for_pr(self, pr: PullRequest) -> float:
        return round(
            sum(self.debt[item_id].priority_score for item_id in pr.technical_debt_ids),
            2,
        )

    def evaluate_merge(
        self,
        pr: PullRequest,
        actor: str,
        *,
        is_admin: bool = False,
        unresolved_conversations: int = 0,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []

        if not pr.open:
            reasons.append("Pull Request is closed.")
        if pr.draft:
            reasons.append("Draft Pull Request cannot be merged.")
        if pr.has_conflicts:
            reasons.append("Merge conflicts must be resolved.")
        if not pr.synchronized_with_base:
            reasons.append("Source branch is not synchronized with the base branch.")

        policy = self.protection.get(pr.target_branch)
        if policy is None:
            return not reasons, reasons

        if policy.restrict_direct_push and pr.target_branch == "main":
            # A PR already represents an indirect change path, so this condition
            # documents that direct pushes are prohibited at the branch boundary.
            pass

        if pr.approval_count() < policy.required_reviews:
            reasons.append(
                f"Required approvals not met: "
                f"{pr.approval_count()}/{policy.required_reviews}."
            )

        if pr.unresolved_change_requests() > 0:
            reasons.append("A reviewer has requested changes.")

        if not pr.required_checks_passed():
            reasons.append("One or more required status checks failed.")

        actual_checks = {check.name for check in pr.status_checks if check.passed}
        missing_checks = set(policy.required_status_checks) - actual_checks
        if missing_checks:
            reasons.append(
                f"Missing required status checks: {sorted(missing_checks)}."
            )

        if policy.require_conversation_resolution and unresolved_conversations:
            reasons.append("Review conversations remain unresolved.")

        debt_score = self.debt_score_for_pr(pr)
        if debt_score > policy.max_new_debt_score:
            reasons.append(
                f"Technical-debt threshold exceeded: "
                f"{debt_score:.2f} > {policy.max_new_debt_score:.2f}."
            )

        if is_admin and policy.allow_bypass_for_admin:
            bypassable = {
                "Required approvals",
                "A reviewer has requested changes.",
            }
            reasons = [
                reason for reason in reasons
                if not any(marker in reason for marker in bypassable)
            ]

        if actor == pr.author and policy.required_reviews > 0:
            reasons.append("Author cannot satisfy required independent review alone.")

        return not reasons, reasons

    def prioritize_debt(self) -> list[TechnicalDebtItem]:
        return sorted(
            (item for item in self.debt.values() if item.status != DebtStatus.RESOLVED),
            key=lambda item: item.priority_score,
            reverse=True,
        )

    def portfolio_metrics(self) -> dict[str, float]:
        active = [
            item for item in self.debt.values()
            if item.status not in {DebtStatus.RESOLVED, DebtStatus.ACCEPTED}
        ]
        return {
            "active_items": len(active),
            "principal_hours": round(sum(i.principal_hours for i in active), 2),
            "remediation_hours": round(sum(i.remediation_hours for i in active), 2),
            "monthly_interest_hours": round(
                sum(i.monthly_interest for i in active), 2
            ),
            "weighted_risk": round(
                sum(i.risk_score for i in active), 2
            ),
        }


def balance_feature_work(
    capacity_hours: float,
    feature_hours: float,
    debt_items: list[TechnicalDebtItem],
    debt_allocation_ratio: float,
) -> dict[str, float | list[int]]:
    if capacity_hours <= 0:
        raise ValueError("Capacity must be positive.")
    if feature_hours < 0:
        raise ValueError("Feature estimate cannot be negative.")
    if not 0 <= debt_allocation_ratio <= 1:
        raise ValueError("Debt allocation ratio must be between 0 and 1.")

    debt_budget = capacity_hours * debt_allocation_ratio
    feature_budget = capacity_hours - debt_budget

    selected: list[int] = []
    remaining = debt_budget

    for item in sorted(debt_items, key=lambda x: x.priority_score, reverse=True):
        if item.remediation_hours <= remaining:
            selected.append(item.item_id)
            remaining -= item.remediation_hours

    return {
        "capacity_hours": round(capacity_hours, 2),
        "feature_budget": round(feature_budget, 2),
        "requested_feature_hours": round(feature_hours, 2),
        "feature_gap": round(max(feature_hours - feature_budget, 0), 2),
        "debt_budget": round(debt_budget, 2),
        "selected_debt_ids": selected,
        "unused_debt_budget": round(remaining, 2),
    }


def save_report(repository: Repository, path: Path) -> None:
    metrics = repository.portfolio_metrics()
    ranking = [
        {
            "id": item.item_id,
            "title": item.title,
            "category": item.category.value,
            "priority": item.priority.value,
            "priority_score": item.priority_score,
            "monthly_interest_hours": item.monthly_interest,
        }
        for item in repository.prioritize_debt()
    ]

    payload = {
        "repository": repository.name,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "metrics": metrics,
        "ranking": ranking,
    }

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_demo() -> None:
    repository = Repository("payment-platform")

    for branch in ("main", "develop", "feature/checkout-refactor"):
        repository.create_branch(branch)

    repository.add_commit(
        "main",
        Commit(
            sha="a1b2c3d4",
            message="stabilize checkout service",
            author="nina",
            changed_files=4,
            additions=72,
            deletions=21,
        ),
    )

    debt_items = [
        TechnicalDebtItem(
            item_id=1,
            title="Legacy checkout validation",
            category=DebtCategory.CODE,
            description="Duplicated validation rules create inconsistent behavior.",
            owner="checkout-team",
            principal_hours=12,
            remediation_hours=20,
            interest_hours_per_month=8,
            impact=8,
            probability=0.8,
            urgency=8,
            security_exposure=5,
            affected_components={"checkout", "payments"},
        ),
        TechnicalDebtItem(
            item_id=2,
            title="Missing integration coverage",
            category=DebtCategory.TEST,
            description="Payment failure paths are not represented in integration tests.",
            owner="quality-team",
            principal_hours=8,
            remediation_hours=16,
            interest_hours_per_month=6,
            impact=7,
            probability=0.7,
            urgency=7,
            security_exposure=4,
            affected_components={"payments"},
        ),
        TechnicalDebtItem(
            item_id=3,
            title="Outdated deployment scripts",
            category=DebtCategory.INFRASTRUCTURE,
            description="Manual deployment steps increase operational variance.",
            owner="platform-team",
            principal_hours=6,
            remediation_hours=10,
            interest_hours_per_month=3,
            impact=6,
            probability=0.6,
            urgency=5,
            security_exposure=3,
            affected_components={"deployment"},
        ),
        TechnicalDebtItem(
            item_id=4,
            title="Hard-coded service credential",
            category=DebtCategory.SECURITY,
            description="A legacy test integration contains a static credential reference.",
            owner="security-team",
            principal_hours=4,
            remediation_hours=6,
            interest_hours_per_month=2,
            impact=10,
            probability=0.5,
            urgency=10,
            security_exposure=10,
            affected_components={"integration-tests"},
        ),
    ]

    for item in debt_items:
        repository.add_debt(item)

    policy = BranchProtection(
        branch="main",
        required_reviews=2,
        required_status_checks=("unit-tests", "security-scan", "integration-tests"),
        require_conversation_resolution=True,
        restrict_direct_push=True,
        restrict_force_push=True,
        restrict_deletion=True,
        require_linear_history=True,
        allow_bypass_for_admin=False,
        max_new_debt_score=90,
    )
    repository.set_protection(policy)

    commits = [
        Commit(
            sha="f1234567",
            message="refactor checkout validation",
            author="nina",
            changed_files=8,
            additions=190,
            deletions=125,
        ),
        Commit(
            sha="f7654321",
            message="add payment failure tests",
            author="nina",
            changed_files=5,
            additions=140,
            deletions=20,
        ),
    ]

    pr = repository.create_pull_request(
        "Refactor checkout validation",
        "feature/checkout-refactor",
        "main",
        "nina",
        commits,
        technical_debt_ids={1, 2},
    )

    pr.status_checks = [
        StatusCheck("unit-tests", True, True, "All unit tests passed."),
        StatusCheck("security-scan", True, True, "No high-severity findings."),
        StatusCheck("integration-tests", False, True, "Payment timeout test failed."),
    ]

    pr.add_review(
        Review(
            reviewer="omar",
            state=ReviewState.APPROVED,
            submitted_at=datetime.now(),
            comments=["Validation boundary is clearer."],
        )
    )

    pr.add_review(
        Review(
            reviewer="priya",
            state=ReviewState.CHANGES_REQUESTED,
            submitted_at=datetime.now(),
            comments=["Add coverage for duplicate payment requests."],
        )
    )

    mergeable, reasons = repository.evaluate_merge(
        pr,
        actor="nina",
        unresolved_conversations=1,
    )

    print("Technical debt ranking")
    print("-" * 72)
    for item in repository.prioritize_debt():
        print(
            f"#{item.item_id:<2} {item.priority.value:<8} "
            f"score={item.priority_score:>6.2f} "
            f"interest={item.monthly_interest:>5.1f}h/month "
            f"{item.title}"
        )

    print("\nPortfolio metrics")
    for key, value in repository.portfolio_metrics().items():
        print(f"{key}: {value}")

    print("\nPull Request merge eligibility")
    print(f"PR #{pr.number}: {'ELIGIBLE' if mergeable else 'BLOCKED'}")
    for reason in reasons:
        print(f"- {reason}")

    plan = balance_feature_work(
        capacity_hours=80,
        feature_hours=60,
        debt_items=repository.prioritize_debt(),
        debt_allocation_ratio=0.30,
    )
    print("\nCapacity allocation")
    print(json.dumps(plan, indent=2))

    with tempfile.TemporaryDirectory() as directory:
        report_path = Path(directory) / "technical-debt-report.json"
        save_report(repository, report_path)
        assert report_path.exists()
        loaded = json.loads(report_path.read_text(encoding="utf-8"))
        assert loaded["metrics"]["active_items"] == 4

    # Assertions exercise important invariants without requiring a test framework.
    assert debt_items[0].priority_score > 0
    assert debt_items[3].security_exposure == 10
    assert pr.approval_count() == 1
    assert not mergeable
    assert any("required approvals" in r.lower() for r in reasons)
    assert any("status checks" in r.lower() for r in reasons)

    print("\nValidation checks passed.")


if __name__ == "__main__":
    run_demo()
