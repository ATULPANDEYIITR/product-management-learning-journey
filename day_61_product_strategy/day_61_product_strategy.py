from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple
from datetime import datetime, timezone


class ProductStage(Enum):
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    DELIVERY = "delivery"
    SCALE = "scale"


class PRState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class ReviewState(Enum):
    COMMENTED = "commented"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"


class MergeStrategy(Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass
class ProductGoal:
    name: str
    metric: str
    target: float
    current: float

    def achieved(self) -> bool:
        return self.current >= self.target


@dataclass
class ProductStrategy:
    vision: str
    mission: str
    strategic_choices: List[str]
    goals: List[ProductGoal]

    def evaluate(self) -> Dict[str, bool]:
        return {goal.name: goal.achieved() for goal in self.goals}

    def score(self) -> float:
        if not self.goals:
            return 0.0
        return sum(min(goal.current / goal.target, 1.0) for goal in self.goals) / len(self.goals)


@dataclass
class Commit:
    sha: str
    message: str
    author: str
    created_at: datetime


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_sha: str
    comments: int = 0


@dataclass
class PullRequest:
    number: int
    title: str
    author: str
    source_branch: str
    target_branch: str
    commits: List[Commit] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    status_checks: Dict[str, bool] = field(default_factory=dict)
    conversations_open: int = 0
    state: PRState = PRState.OPEN
    draft: bool = False
    merge_strategy: MergeStrategy = MergeStrategy.SQUASH

    def head_sha(self) -> str:
        if not self.commits:
            raise ValueError("Pull Request has no commits")
        return self.commits[-1].sha


@dataclass
class BranchProtection:
    branch_name: str
    required_approvals: int
    required_checks: Set[str]
    require_conversations_resolved: bool = True
    allow_direct_push: bool = False
    allow_force_push: bool = False
    allow_deletion: bool = False
    require_linear_history: bool = False
    allow_administrator_bypass: bool = False


@dataclass
class Repository:
    name: str
    branches: Set[str]
    pull_requests: Dict[int, PullRequest]
    protections: Dict[str, BranchProtection]


class MergeEligibility:
    """
    Evaluates repository-level merge conditions.

    Product strategy determines why these controls exist.
    Branch protection determines which conditions are enforced.
    Reviews and approvals provide evidence against those conditions.
    """

    def __init__(self, repository: Repository):
        self.repository = repository

    def evaluate(self, pr: PullRequest) -> Tuple[bool, List[str]]:
        reasons: List[str] = []

        if pr.target_branch not in self.repository.branches:
            reasons.append("Target branch does not exist.")

        protection = self.repository.protections.get(pr.target_branch)
        if protection is None:
            reasons.append("Target branch has no protection policy.")
            return False, reasons

        if pr.state != PRState.OPEN:
            reasons.append(f"Pull Request state is {pr.state.value}.")

        if pr.draft:
            reasons.append("Draft Pull Requests cannot be merged.")

        if not pr.commits:
            reasons.append("Pull Request contains no commits.")

        latest_sha = pr.head_sha() if pr.commits else None

        valid_approvals = {
            review.reviewer
            for review in pr.reviews
            if review.state == ReviewState.APPROVED
            and review.commit_sha == latest_sha
        }

        requested_changes = {
            review.reviewer
            for review in pr.reviews
            if review.state == ReviewState.CHANGES_REQUESTED
        }

        if requested_changes:
            reasons.append(
                "Requested changes remain from: "
                + ", ".join(sorted(requested_changes))
            )

        if len(valid_approvals) < protection.required_approvals:
            reasons.append(
                f"Only {len(valid_approvals)} current approval(s); "
                f"{protection.required_approvals} required."
            )

        failed_checks = sorted(
            check for check in protection.required_checks
            if pr.status_checks.get(check) is not True
        )
        if failed_checks:
            reasons.append(
                "Required status checks are missing or failing: "
                + ", ".join(failed_checks)
            )

        if protection.require_conversations_resolved and pr.conversations_open:
            reasons.append(
                f"{pr.conversations_open} review conversation(s) remain open."
            )

        return not reasons, reasons

    def merge(self, pr_number: int) -> str:
        pr = self.repository.pull_requests[pr_number]
        eligible, reasons = self.evaluate(pr)

        if not eligible:
            return "MERGE BLOCKED\n- " + "\n- ".join(reasons)

        pr.state = PRState.MERGED
        return (
            f"MERGED PR #{pr.number} using "
            f"{pr.merge_strategy.value.replace('_', ' ')}."
        )


def build_product_strategy() -> ProductStrategy:
    return ProductStrategy(
        vision=(
            "Make repository change management predictable, reviewable, "
            "and safe for engineering teams."
        ),
        mission=(
            "Provide a product workflow that connects proposed changes, "
            "human review, automated validation, and repository governance."
        ),
        strategic_choices=[
            "Use Pull Requests as the controlled change-entry workflow.",
            "Separate review decisions from repository enforcement.",
            "Make approval freshness explicit when the reviewed commit changes.",
            "Use automated status checks as objective merge evidence.",
            "Protect critical branches from uncontrolled writes.",
        ],
        goals=[
            ProductGoal(
                "review_coverage",
                "percentage of production PRs reviewed",
                95.0,
                92.0,
            ),
            ProductGoal(
                "successful_merge_rate",
                "percentage of eligible PRs merged without policy override",
                90.0,
                94.0,
            ),
            ProductGoal(
                "open_conversation_rate",
                "percentage of merged PRs with unresolved conversations",
                1.0,
                0.5,
            ),
        ],
    )


def demonstrate() -> None:
    strategy = build_product_strategy()

    print("PRODUCT STRATEGY")
    print("=" * 72)
    print("Vision:", strategy.vision)
    print("Mission:", strategy.mission)
    print("Strategy score:", f"{strategy.score() * 100:.1f}%")
    print("Goal status:", strategy.evaluate())

    repository = Repository(
        name="payment-platform",
        branches={"main", "develop", "feature/product-strategy"},
        pull_requests={},
        protections={},
    )

    repository.protections["main"] = BranchProtection(
        branch_name="main",
        required_approvals=2,
        required_checks={"unit-tests", "security-scan", "product-policy"},
        require_conversations_resolved=True,
        allow_direct_push=False,
        allow_force_push=False,
        allow_deletion=False,
        require_linear_history=True,
    )

    now = datetime.now(timezone.utc)

    pr = PullRequest(
        number=142,
        title="Introduce product strategy governance metrics",
        author="atul",
        source_branch="feature/product-strategy",
        target_branch="main",
        commits=[
            Commit(
                sha="a1b2c3d4",
                message="Add product strategy governance model",
                author="atul",
                created_at=now,
            ),
            Commit(
                sha="e5f6g7h8",
                message="Address review findings",
                author="atul",
                created_at=now,
            ),
        ],
        status_checks={
            "unit-tests": True,
            "security-scan": True,
            "product-policy": True,
        },
        conversations_open=0,
        draft=False,
    )

    pr.reviews.extend(
        [
            Review("maya", ReviewState.APPROVED, "e5f6g7h8"),
            Review("rohan", ReviewState.APPROVED, "e5f6g7h8"),
        ]
    )

    repository.pull_requests[pr.number] = pr

    engine = MergeEligibility(repository)

    eligible, reasons = engine.evaluate(pr)
    print("\nMERGE ELIGIBILITY")
    print("=" * 72)
    print("Eligible:", eligible)
    if reasons:
        print("\n".join(reasons))
    else:
        print("All protected-branch conditions satisfied.")

    print(engine.merge(pr.number))

    # Demonstrate stale approvals: changing the head commit invalidates
    # approvals that were attached to the previous commit.
    stale_pr = PullRequest(
        number=143,
        title="Change deployment approval policy",
        author="atul",
        source_branch="feature/policy",
        target_branch="main",
        commits=[
            Commit("11111111", "Initial policy change", "atul", now),
            Commit("22222222", "Modify policy after review", "atul", now),
        ],
        reviews=[
            Review("maya", ReviewState.APPROVED, "11111111"),
            Review("rohan", ReviewState.APPROVED, "11111111"),
        ],
        status_checks={
            "unit-tests": True,
            "security-scan": True,
            "product-policy": True,
        },
        conversations_open=0,
    )

    repository.pull_requests[stale_pr.number] = stale_pr

    print("\nSTALE APPROVAL CASE")
    print("=" * 72)
    eligible, reasons = engine.evaluate(stale_pr)
    print("Eligible:", eligible)
    print("\n".join(reasons))

    # Demonstrate failure of a required automated control.
    failed_check_pr = PullRequest(
        number=144,
        title="Update product policy controls",
        author="atul",
        source_branch="feature/security",
        target_branch="main",
        commits=[Commit("99999999", "Update controls", "atul", now)],
        reviews=[
            Review("maya", ReviewState.APPROVED, "99999999"),
            Review("rohan", ReviewState.APPROVED, "99999999"),
        ],
        status_checks={
            "unit-tests": True,
            "security-scan": False,
            "product-policy": True,
        },
        conversations_open=0,
    )

    repository.pull_requests[failed_check_pr.number] = failed_check_pr

    print("\nFAILED STATUS CHECK CASE")
    print("=" * 72)
    eligible, reasons = engine.evaluate(failed_check_pr)
    print("Eligible:", eligible)
    print("\n".join(reasons))


if __name__ == "__main__":
    demonstrate()
