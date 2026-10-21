from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class PullRequestState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class ReviewState(Enum):
    COMMENTED = "commented"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    comments: List[str] = field(default_factory=list)


@dataclass
class BranchProtection:
    required_approvals: int = 2
    required_checks: Set[str] = field(
        default_factory=lambda: {"build", "tests", "security"}
    )
    require_conversation_resolution: bool = True
    allow_force_push: bool = False
    allow_direct_push: bool = False
    allow_deletion: bool = False
    require_linear_history: bool = True


@dataclass
class PullRequest:
    number: int
    title: str
    source_branch: str
    target_branch: str
    author: str
    state: PullRequestState = PullRequestState.DRAFT
    commits: List[Commit] = field(default_factory=list)
    requested_reviewers: Set[str] = field(default_factory=set)
    reviews: Dict[str, Review] = field(default_factory=dict)
    status_checks: Dict[str, bool] = field(default_factory=dict)
    unresolved_conversations: int = 0
    merge_conflicts: bool = False
    synchronized_with_base: bool = True

    def add_commit(self, commit: Commit) -> None:
        if self.state in {PullRequestState.MERGED, PullRequestState.CLOSED}:
            raise ValueError("Cannot modify a closed or merged Pull Request.")
        self.commits.append(commit)
        self.synchronized_with_base = False

    def open(self) -> None:
        if not self.commits:
            raise ValueError("A Pull Request requires at least one commit.")
        if self.state not in {PullRequestState.DRAFT, PullRequestState.OPEN}:
            raise ValueError("Only draft Pull Requests can be opened.")
        self.state = PullRequestState.OPEN

    def request_review(self, reviewer: str) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Reviews can only be requested on an open Pull Request.")
        if reviewer == self.author:
            raise ValueError("Authors cannot request themselves as an external reviewer.")
        self.requested_reviewers.add(reviewer)

    def add_review(self, review: Review) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Only open Pull Requests can receive reviews.")
        if review.reviewer == self.author:
            raise ValueError("Self-review is not permitted.")
        self.reviews[review.reviewer] = review

    def update_status(self, check: str, passed: bool) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Status checks belong to an open Pull Request.")
        self.status_checks[check] = passed

    def resolve_conversation(self) -> None:
        if self.unresolved_conversations <= 0:
            raise ValueError("There are no unresolved conversations.")
        self.unresolved_conversations -= 1

    def synchronize_with_base(self) -> None:
        if self.merge_conflicts:
            raise ValueError("Conflicts must be resolved before synchronization.")
        self.synchronized_with_base = True

    def close(self) -> None:
        if self.state == PullRequestState.MERGED:
            raise ValueError("A merged Pull Request cannot be closed.")
        self.state = PullRequestState.CLOSED


class MergeEvaluator:
    def __init__(self, protection: BranchProtection):
        self.protection = protection

    def evaluate(self, pr: PullRequest) -> tuple[bool, List[str]]:
        failures: List[str] = []

        if pr.state != PullRequestState.OPEN:
            failures.append("Pull Request is not open.")

        if not pr.commits:
            failures.append("No commits are associated with the Pull Request.")

        if pr.merge_conflicts:
            failures.append("Merge conflicts exist.")

        if not pr.synchronized_with_base:
            failures.append("Pull Request is not synchronized with the base branch.")

        if self.protection.require_conversation_resolution:
            if pr.unresolved_conversations > 0:
                failures.append("Unresolved review conversations remain.")

        approvals = 0
        for review in pr.reviews.values():
            if review.state == ReviewState.APPROVED:
                approvals += 1

        if approvals < self.protection.required_approvals:
            failures.append(
                f"At least {self.protection.required_approvals} approvals are required."
            )

        for check in self.protection.required_checks:
            if pr.status_checks.get(check) is not True:
                failures.append(f"Required status check '{check}' has not passed.")

        return not failures, failures

    def merge(self, pr: PullRequest) -> None:
        eligible, failures = self.evaluate(pr)
        if not eligible:
            raise RuntimeError("Merge blocked: " + " ".join(failures))
        pr.state = PullRequestState.MERGED


def demonstrate() -> None:
    protection = BranchProtection(
        required_approvals=2,
        required_checks={"build", "tests", "security"},
        require_conversation_resolution=True,
        allow_force_push=False,
        allow_direct_push=False,
        allow_deletion=False,
        require_linear_history=True,
    )

    pr = PullRequest(
        number=42,
        title="Harden authentication middleware",
        source_branch="feature/auth-hardening",
        target_branch="main",
        author="alice",
    )

    pr.add_commit(Commit("a1001", "Validate session expiration"))
    pr.add_commit(Commit("a1002", "Reject malformed authorization headers"))
    pr.open()

    pr.request_review("bob")
    pr.request_review("carol")

    pr.add_review(
        Review(
            reviewer="bob",
            state=ReviewState.APPROVED,
            comments=["Authentication boundary is correctly enforced."],
        )
    )
    pr.add_review(
        Review(
            reviewer="carol",
            state=ReviewState.APPROVED,
            comments=["Validation and failure handling are acceptable."],
        )
    )

    pr.update_status("build", True)
    pr.update_status("tests", True)
    pr.update_status("security", True)

    pr.unresolved_conversations = 1

    evaluator = MergeEvaluator(protection)
    eligible, failures = evaluator.evaluate(pr)

    print("Initial merge eligibility:", eligible)
    print("Blocking conditions:", failures)

    pr.resolve_conversation()
    pr.synchronized_with_base = True

    evaluator.merge(pr)
    print("Final Pull Request state:", pr.state.value)

    try:
        pr.add_commit(Commit("a1003", "Attempt modification after merge"))
    except ValueError as exc:
        print("Expected failure:", exc)


if __name__ == "__main__":
    demonstrate()
