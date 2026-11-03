from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple


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


class CheckState(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class MergeStrategy(Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str
    author: str


@dataclass
class Branch:
    name: str
    commits: List[Commit] = field(default_factory=list)
    protected: bool = False

    def head(self) -> str | None:
        return self.commits[-1].sha if self.commits else None


@dataclass
class ReviewComment:
    reviewer: str
    file_path: str
    line: int
    body: str
    resolved: bool = False


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    comments: List[ReviewComment] = field(default_factory=list)
    stale: bool = False
    dismissed: bool = False


@dataclass
class StatusCheck:
    name: str
    state: CheckState


@dataclass
class BranchProtection:
    required_approvals: int = 1
    required_checks: Set[str] = field(default_factory=set)
    require_conversations_resolved: bool = True
    require_linear_history: bool = False
    allow_direct_push: bool = False
    allow_force_push: bool = False
    allow_branch_deletion: bool = False
    allow_admin_bypass: bool = False
    allowed_merge_strategies: Set[MergeStrategy] = field(
        default_factory=lambda: {
            MergeStrategy.MERGE_COMMIT,
            MergeStrategy.SQUASH,
            MergeStrategy.REBASE,
        }
    )


@dataclass
class PullRequest:
    number: int
    title: str
    source_branch: str
    target_branch: str
    author: str
    state: PullRequestState = PullRequestState.OPEN
    commits: List[Commit] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    checks: List[StatusCheck] = field(default_factory=list)
    requested_reviewers: Set[str] = field(default_factory=set)
    base_head_at_creation: str | None = None

    def add_commit(self, commit: Commit) -> None:
        if self.state not in {PullRequestState.OPEN, PullRequestState.DRAFT}:
            raise ValueError("Cannot add commits to a closed or merged Pull Request.")
        self.commits.append(commit)

        # A new changeset can invalidate previously granted approvals.
        for review in self.reviews:
            if review.state == ReviewState.APPROVED:
                review.stale = True

    def request_review(self, reviewer: str) -> None:
        if reviewer == self.author:
            raise ValueError("The Pull Request author cannot be its own required reviewer.")
        self.requested_reviewers.add(reviewer)

    def add_review(self, review: Review) -> None:
        if review.reviewer == self.author:
            raise ValueError("Self-review is not allowed.")
        self.reviews.append(review)

    def add_check(self, check: StatusCheck) -> None:
        self.checks = [c for c in self.checks if c.name != check.name]
        self.checks.append(check)


class Repository:
    def __init__(self, name: str):
        self.name = name
        self.branches: Dict[str, Branch] = {}
        self.pull_requests: Dict[int, PullRequest] = {}
        self.protection: Dict[str, BranchProtection] = {}
        self.next_pr_number = 1

    def add_branch(self, branch: Branch) -> None:
        if branch.name in self.branches:
            raise ValueError(f"Branch already exists: {branch.name}")
        self.branches[branch.name] = branch

    def protect_branch(self, name: str, policy: BranchProtection) -> None:
        if name not in self.branches:
            raise ValueError(f"Unknown branch: {name}")
        self.branches[name].protected = True
        self.protection[name] = policy

    def create_pull_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        author: str,
        draft: bool = False,
    ) -> PullRequest:
        if source_branch not in self.branches:
            raise ValueError("Source branch does not exist.")
        if target_branch not in self.branches:
            raise ValueError("Target branch does not exist.")
        if source_branch == target_branch:
            raise ValueError("Source and target branches must differ.")

        pr = PullRequest(
            number=self.next_pr_number,
            title=title,
            source_branch=source_branch,
            target_branch=target_branch,
            author=author,
            state=PullRequestState.DRAFT if draft else PullRequestState.OPEN,
            commits=list(self.branches[source_branch].commits),
            base_head_at_creation=self.branches[target_branch].head(),
        )
        self.pull_requests[pr.number] = pr
        self.next_pr_number += 1
        return pr

    def publish(self, pr_number: int) -> None:
        pr = self.pull_requests[pr_number]
        if pr.state != PullRequestState.DRAFT:
            raise ValueError("Only draft Pull Requests can be published.")
        pr.state = PullRequestState.OPEN

    def synchronize(self, pr_number: int) -> bool:
        pr = self.pull_requests[pr_number]
        current_base = self.branches[pr.target_branch].head()

        if current_base == pr.base_head_at_creation:
            return False

        # A production implementation would perform a three-way merge.
        # Here, synchronization updates the base reference and invalidates
        # approvals because the proposed comparison context has changed.
        pr.base_head_at_creation = current_base
        for review in pr.reviews:
            if review.state == ReviewState.APPROVED:
                review.stale = True
        return True

    def merge_eligibility(
        self,
        pr_number: int,
        actor: str,
        strategy: MergeStrategy = MergeStrategy.SQUASH,
        administrator: bool = False,
    ) -> Tuple[bool, List[str]]:
        pr = self.pull_requests[pr_number]
        reasons: List[str] = []

        if pr.state != PullRequestState.OPEN:
            reasons.append("Pull Request is not open.")

        if not pr.commits:
            reasons.append("Pull Request has no proposed commits.")

        target = self.branches[pr.target_branch]
        policy = self.protection.get(pr.target_branch)

        if target.protected and policy is None:
            reasons.append("Protected branch has no governance policy.")

        if policy:
            if strategy not in policy.allowed_merge_strategies:
                reasons.append("Selected merge strategy is not permitted.")

            approvals = {
                review.reviewer
                for review in pr.reviews
                if review.state == ReviewState.APPROVED
                and not review.stale
                and not review.dismissed
                and review.reviewer in pr.requested_reviewers
                and review.reviewer != pr.author
            }

            if len(approvals) < policy.required_approvals:
                reasons.append(
                    f"Required approvals not satisfied: "
                    f"{len(approvals)}/{policy.required_approvals}."
                )

            check_map = {check.name: check.state for check in pr.checks}
            for required in policy.required_checks:
                if check_map.get(required) != CheckState.PASSED:
                    reasons.append(f"Required status check failed or is missing: {required}.")

            if policy.require_conversations_resolved:
                unresolved = [
                    comment
                    for review in pr.reviews
                    for comment in review.comments
                    if not comment.resolved
                ]
                if unresolved:
                    reasons.append("Unresolved review conversations remain.")

            if policy.require_linear_history and strategy == MergeStrategy.MERGE_COMMIT:
                reasons.append("Merge commits violate the linear-history policy.")

            if administrator and policy.allow_admin_bypass:
                reasons = [
                    r for r in reasons
                    if not r.startswith("Required approvals")
                    and not r.startswith("Required status check")
                ]

        if any(
            review.state == ReviewState.CHANGES_REQUESTED
            and not review.dismissed
            for review in pr.reviews
        ):
            reasons.append("An active reviewer has requested changes.")

        return not reasons, reasons

    def merge(
        self,
        pr_number: int,
        actor: str,
        strategy: MergeStrategy = MergeStrategy.SQUASH,
        administrator: bool = False,
    ) -> None:
        eligible, reasons = self.merge_eligibility(
            pr_number, actor, strategy, administrator
        )
        if not eligible:
            raise RuntimeError("Merge blocked: " + " | ".join(reasons))

        pr = self.pull_requests[pr_number]
        target = self.branches[pr.target_branch]

        if strategy == MergeStrategy.SQUASH:
            merged_sha = f"squash-{pr.number}"
            target.commits.append(
                Commit(
                    sha=merged_sha,
                    message=pr.title,
                    author=actor,
                )
            )
        elif strategy == MergeStrategy.MERGE_COMMIT:
            target.commits.append(
                Commit(
                    sha=f"merge-{pr.number}",
                    message=f"Merge PR #{pr.number}: {pr.title}",
                    author=actor,
                )
            )
        elif strategy == MergeStrategy.REBASE:
            target.commits.extend(pr.commits)

        pr.state = PullRequestState.MERGED

    def close(self, pr_number: int) -> None:
        pr = self.pull_requests[pr_number]
        if pr.state == PullRequestState.MERGED:
            raise ValueError("Merged Pull Requests cannot be closed.")
        pr.state = PullRequestState.CLOSED

    def reopen(self, pr_number: int) -> None:
        pr = self.pull_requests[pr_number]
        if pr.state != PullRequestState.CLOSED:
            raise ValueError("Only closed Pull Requests can be reopened.")
        pr.state = PullRequestState.OPEN


def main() -> None:
    repo = Repository("payments-platform")

    main_branch = Branch(
        "main",
        [
            Commit("c001", "Initial release", "alice"),
            Commit("c002", "Add payment service", "alice"),
        ],
    )
    feature_branch = Branch(
        "feature/refund-api",
        main_branch.commits
        + [Commit("c003", "Add refund endpoint", "bob")],
    )

    repo.add_branch(main_branch)
    repo.add_branch(feature_branch)

    repo.protect_branch(
        "main",
        BranchProtection(
            required_approvals=2,
            required_checks={"unit-tests", "security-scan"},
            require_conversations_resolved=True,
            require_linear_history=True,
            allow_direct_push=False,
            allow_force_push=False,
            allow_branch_deletion=False,
            allowed_merge_strategies={MergeStrategy.SQUASH, MergeStrategy.REBASE},
        ),
    )

    pr = repo.create_pull_request(
        "Implement refund API",
        "feature/refund-api",
        "main",
        "bob",
    )

    pr.request_review("alice")
    pr.request_review("carol")

    pr.add_review(
        Review(
            reviewer="alice",
            state=ReviewState.APPROVED,
            comments=[
                ReviewComment(
                    reviewer="alice",
                    file_path="refund.py",
                    line=42,
                    body="Validate the currency before processing.",
                    resolved=True,
                )
            ],
        )
    )

    pr.add_review(
        Review(
            reviewer="carol",
            state=ReviewState.APPROVED,
            comments=[],
        )
    )

    pr.add_check(StatusCheck("unit-tests", CheckState.PASSED))
    pr.add_check(StatusCheck("security-scan", CheckState.PASSED))

    eligible, reasons = repo.merge_eligibility(
        pr.number,
        actor="release-manager",
        strategy=MergeStrategy.SQUASH,
    )

    print(f"PR #{pr.number} merge eligible: {eligible}")
    if reasons:
        for reason in reasons:
            print("BLOCKED:", reason)

    repo.merge(
        pr.number,
        actor="release-manager",
        strategy=MergeStrategy.SQUASH,
    )

    print("Target branch:", repo.branches["main"].name)
    print("Target HEAD:", repo.branches["main"].head())
    print("PR state:", pr.state.value)

    # Demonstrate stale approval behavior.
    pr2 = repo.create_pull_request(
        "Improve refund validation",
        "feature/refund-api",
        "main",
        "david",
    )
    pr2.request_review("alice")
    pr2.add_review(Review("alice", ReviewState.APPROVED))
    pr2.add_check(StatusCheck("unit-tests", CheckState.PASSED))
    pr2.add_check(StatusCheck("security-scan", CheckState.PASSED))
    pr2.add_commit(Commit("c004", "Fix validation edge case", "david"))

    eligible, reasons = repo.merge_eligibility(
        pr2.number,
        actor="release-manager",
        strategy=MergeStrategy.SQUASH,
    )
    print(f"PR #{pr2.number} merge eligible after new commit: {eligible}")
    for reason in reasons:
        print("BLOCKED:", reason)


if __name__ == "__main__":
    main()
