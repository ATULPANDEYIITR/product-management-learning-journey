from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
import hashlib
import time


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


class CheckState(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class MergeStrategy(Enum):
    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    message: str
    timestamp: float


@dataclass
class Branch:
    name: str
    protected: bool = False
    commits: List[Commit] = field(default_factory=list)

    @property
    def head(self) -> Optional[str]:
        return self.commits[-1].sha if self.commits else None


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_sha: str
    comments: List[str] = field(default_factory=list)
    submitted_at: float = field(default_factory=time.time)


@dataclass
class StatusCheck:
    name: str
    state: CheckState
    commit_sha: str


@dataclass
class BranchProtection:
    required_approvals: int = 1
    required_checks: Set[str] = field(default_factory=set)
    require_conversation_resolution: bool = True
    allow_direct_push: bool = False
    allow_force_push: bool = False
    allow_branch_deletion: bool = False
    require_linear_history: bool = False
    allowed_merge_strategies: Set[MergeStrategy] = field(
        default_factory=lambda: {MergeStrategy.SQUASH, MergeStrategy.REBASE}
    )


@dataclass
class PullRequest:
    number: int
    source: str
    target: str
    author: str
    state: PRState = PRState.OPEN
    commits: List[Commit] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    checks: List[StatusCheck] = field(default_factory=list)
    unresolved_conversations: int = 0
    merge_strategy: Optional[MergeStrategy] = None
    synchronized: bool = True
    merge_error: Optional[str] = None

    def add_commit(self, commit: Commit) -> None:
        self.commits.append(commit)
        self.synchronized = False
        self.merge_error = None

    @property
    def head_sha(self) -> Optional[str]:
        return self.commits[-1].sha if self.commits else None


class WorkflowError(Exception):
    pass


class Repository:
    def __init__(self, name: str):
        self.name = name
        self.branches: Dict[str, Branch] = {}
        self.protection: Dict[str, BranchProtection] = {}
        self.pull_requests: Dict[int, PullRequest] = {}
        self.next_pr = 1
        self.users: Set[str] = set()
        self.reviewer_eligibility: Dict[str, Set[str]] = {}

    def add_user(self, username: str) -> None:
        if not username or " " in username:
            raise ValueError("Invalid username")
        self.users.add(username)

    def create_branch(self, name: str, protected: bool = False) -> None:
        if name in self.branches:
            raise WorkflowError(f"Branch already exists: {name}")
        self.branches[name] = Branch(name=name, protected=protected)
        if protected:
            self.protection[name] = BranchProtection()

    def configure_protection(self, branch: str, policy: BranchProtection) -> None:
        self._require_branch(branch)
        self.protection[branch] = policy
        self.branches[branch].protected = True

    def _require_branch(self, name: str) -> None:
        if name not in self.branches:
            raise WorkflowError(f"Unknown branch: {name}")

    def commit(self, branch: str, author: str, message: str) -> Commit:
        self._require_branch(branch)
        if author not in self.users:
            raise WorkflowError("Unknown author")
        if not message.strip():
            raise ValueError("Commit message cannot be empty")

        previous = self.branches[branch].head or "root"
        digest = hashlib.sha1(
            f"{previous}|{author}|{message}|{time.time_ns()}".encode()
        ).hexdigest()
        commit = Commit(digest[:12], author, message.strip(), time.time())
        self.branches[branch].commits.append(commit)
        return commit

    def create_pull_request(
        self, source: str, target: str, author: str, draft: bool = False
    ) -> PullRequest:
        self._require_branch(source)
        self._require_branch(target)
        if source == target:
            raise WorkflowError("Source and target branches must differ")
        if author not in self.users:
            raise WorkflowError("Unknown author")

        pr = PullRequest(
            number=self.next_pr,
            source=source,
            target=target,
            author=author,
            state=PRState.DRAFT if draft else PRState.OPEN,
            commits=list(self.branches[source].commits),
            synchronized=True,
        )
        self.pull_requests[pr.number] = pr
        self.next_pr += 1
        return pr

    def mark_ready(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.state != PRState.DRAFT:
            raise WorkflowError("Pull Request is not a draft")
        pr.state = PRState.OPEN

    def synchronize(self, number: int) -> None:
        pr = self.pull_requests[number]
        pr.commits = list(self.branches[pr.source].commits)
        pr.synchronized = True
        pr.merge_error = None

    def add_review(
        self,
        number: int,
        reviewer: str,
        state: ReviewState,
        comments: Optional[List[str]] = None,
    ) -> None:
        pr = self.pull_requests[number]
        if reviewer not in self.users:
            raise WorkflowError("Unknown reviewer")
        if reviewer == pr.author:
            raise WorkflowError("Authors cannot approve their own Pull Request")
        if pr.state != PRState.OPEN:
            raise WorkflowError("Reviews require an open Pull Request")

        comments = comments or []
        if state == ReviewState.CHANGES_REQUESTED and not comments:
            raise WorkflowError("Requested changes require a review comment")

        pr.reviews.append(
            Review(
                reviewer=reviewer,
                state=state,
                commit_sha=pr.head_sha or "",
                comments=comments,
            )
        )

    def add_status_check(self, number: int, name: str, state: CheckState) -> None:
        pr = self.pull_requests[number]
        if not pr.head_sha:
            raise WorkflowError("Pull Request has no commits")
        pr.checks.append(StatusCheck(name, state, pr.head_sha))

    def resolve_conversation(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.unresolved_conversations <= 0:
            raise WorkflowError("No unresolved conversation exists")
        pr.unresolved_conversations -= 1

    def merge_eligibility(self, number: int) -> tuple[bool, List[str]]:
        pr = self.pull_requests[number]
        errors: List[str] = []

        if pr.state != PRState.OPEN:
            errors.append("Pull Request is not open")
        if not pr.commits:
            errors.append("Pull Request contains no commits")
        if not pr.synchronized:
            errors.append("Source branch is out of synchronization")
        if pr.merge_strategy is None:
            errors.append("No merge strategy selected")

        policy = self.protection.get(pr.target)
        if policy:
            if not policy.allow_direct_push and pr.source == pr.target:
                errors.append("Direct push cannot replace the Pull Request workflow")

            latest_by_reviewer: Dict[str, Review] = {}
            for review in pr.reviews:
                latest_by_reviewer[review.reviewer] = review

            blocking = [
                r.reviewer
                for r in latest_by_reviewer.values()
                if r.state == ReviewState.CHANGES_REQUESTED
                and r.commit_sha == pr.head_sha
            ]
            if blocking:
                errors.append("Requested changes are still blocking approval")

            approvals = sum(
                1
                for review in latest_by_reviewer.values()
                if review.state == ReviewState.APPROVED
                and review.commit_sha == pr.head_sha
            )
            if approvals < policy.required_approvals:
                errors.append(
                    f"Required approvals not met: {approvals}/{policy.required_approvals}"
                )

            for check_name in policy.required_checks:
                matching = [
                    c for c in pr.checks
                    if c.name == check_name and c.commit_sha == pr.head_sha
                ]
                if not matching or matching[-1].state != CheckState.PASSED:
                    errors.append(f"Required check not passed: {check_name}")

            if policy.require_conversation_resolution and pr.unresolved_conversations:
                errors.append("Unresolved review conversations remain")

            if (
                pr.merge_strategy
                and pr.merge_strategy not in policy.allowed_merge_strategies
            ):
                errors.append("Selected merge strategy is not permitted")

        return not errors, errors

    def merge(self, number: int, strategy: MergeStrategy) -> None:
        pr = self.pull_requests[number]
        pr.merge_strategy = strategy
        eligible, errors = self.merge_eligibility(number)
        if not eligible:
            pr.merge_error = "; ".join(errors)
            raise WorkflowError(pr.merge_error)

        target = self.branches[pr.target]
        source = self.branches[pr.source]

        if strategy == MergeStrategy.MERGE:
            target.commits.extend(source.commits)
        elif strategy == MergeStrategy.SQUASH:
            digest = hashlib.sha1(
                f"squash:{pr.number}:{source.head}:{target.head}".encode()
            ).hexdigest()[:12]
            target.commits.append(
                Commit(digest, pr.author, f"Squash PR #{pr.number}", time.time())
            )
        elif strategy == MergeStrategy.REBASE:
            target.commits.extend(source.commits)

        pr.state = PRState.MERGED

    def close(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.state == PRState.MERGED:
            raise WorkflowError("Merged Pull Request cannot be closed")
        pr.state = PRState.CLOSED

    def reopen(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.state != PRState.CLOSED:
            raise WorkflowError("Only closed Pull Requests can be reopened")
        pr.state = PRState.OPEN
        pr.synchronized = False


def print_result(title: str, value: object) -> None:
    print(f"\n{title}")
    print(value)


def main() -> None:
    repo = Repository("payments-service")

    for user in ("alice", "bob", "carol"):
        repo.add_user(user)

    repo.create_branch("main", protected=True)
    repo.create_branch("feature/payment-validation")

    repo.configure_protection(
        "main",
        BranchProtection(
            required_approvals=2,
            required_checks={"unit-tests", "security-scan"},
            require_conversation_resolution=True,
            allowed_merge_strategies={MergeStrategy.SQUASH, MergeStrategy.REBASE},
        ),
    )

    repo.commit("main", "alice", "Initialize payments service")
    repo.commit(
        "feature/payment-validation",
        "alice",
        "Add payment validation",
    )

    pr = repo.create_pull_request(
        "feature/payment-validation", "main", "alice", draft=True
    )
    print_result("Created draft PR", f"#{pr.number} state={pr.state.value}")

    repo.mark_ready(pr.number)
    repo.synchronize(pr.number)

    pr.unresolved_conversations = 1

    repo.add_review(
        pr.number,
        "bob",
        ReviewState.COMMENTED,
        ["Validate currency before processing."],
    )
    repo.add_review(
        pr.number,
        "carol",
        ReviewState.CHANGES_REQUESTED,
        ["Add validation for unsupported currencies."],
    )

    repo.add_status_check(pr.number, "unit-tests", CheckState.PASSED)
    repo.add_status_check(pr.number, "security-scan", CheckState.PASSED)

    eligible, reasons = repo.merge_eligibility(pr.number)
    print_result("Initial merge eligibility", (eligible, reasons))

    repo.resolve_conversation(pr.number)
    repo.add_review(pr.number, "carol", ReviewState.APPROVED)
    repo.add_review(pr.number, "bob", ReviewState.APPROVED)

    eligible, reasons = repo.merge_eligibility(pr.number)
    print_result("Eligibility after approval", (eligible, reasons))

    repo.merge(pr.number, MergeStrategy.SQUASH)
    print_result("Merged PR", f"#{pr.number} using {pr.merge_strategy.value}")

    print_result("Protected main branch head", repo.branches["main"].head)
    print_result(
        "Production considerations",
        [
            "Treat review approvals as commit-specific decisions.",
            "Invalidate or re-evaluate approvals after new commits.",
            "Enforce protected-branch rules on the server, not only in clients.",
            "Keep audit records for reviews, status checks, merges, and policy changes.",
            "Never expose repository credentials or authorization tokens in logs.",
        ],
    )


if __name__ == "__main__":
    main()
