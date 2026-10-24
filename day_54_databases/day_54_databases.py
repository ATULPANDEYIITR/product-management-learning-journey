from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import json
import re


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


class MergeStrategy(Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str


@dataclass
class Branch:
    name: str
    protected: bool = False
    commits: List[str] = field(default_factory=list)


@dataclass
class Reviewer:
    username: str
    teams: Set[str] = field(default_factory=set)
    active: bool = True


@dataclass
class ReviewComment:
    reviewer: str
    path: str
    line: int
    body: str
    resolved: bool = False


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_sha: str
    comments: List[ReviewComment] = field(default_factory=list)
    dismissed: bool = False


@dataclass
class StatusCheck:
    name: str
    passed: bool
    required: bool = True


@dataclass
class BranchProtection:
    required_review_count: int = 1
    required_status_checks: Set[str] = field(default_factory=set)
    require_conversation_resolution: bool = True
    allow_direct_push: bool = False
    allow_force_push: bool = False
    allow_branch_deletion: bool = False
    require_linear_history: bool = False
    allowed_merge_strategies: Set[MergeStrategy] = field(
        default_factory=lambda: {
            MergeStrategy.MERGE_COMMIT,
            MergeStrategy.SQUASH,
            MergeStrategy.REBASE,
        }
    )
    bypass_users: Set[str] = field(default_factory=set)


@dataclass
class PullRequest:
    number: int
    source_branch: str
    target_branch: str
    title: str
    author: str
    state: PullRequestState = PullRequestState.OPEN
    commits: List[str] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    comments: List[ReviewComment] = field(default_factory=list)
    checks: List[StatusCheck] = field(default_factory=list)
    merge_strategy: MergeStrategy = MergeStrategy.SQUASH

    def add_commit(self, sha: str) -> None:
        if self.state not in {PullRequestState.OPEN, PullRequestState.DRAFT}:
            raise ValueError("Commits cannot be added to a closed or merged pull request.")
        if sha not in self.commits:
            self.commits.append(sha)

    def add_review(self, review: Review) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Reviews can only be submitted to an open pull request.")
        self.reviews.append(review)

    def add_comment(self, comment: ReviewComment) -> None:
        if self.state != PullRequestState.OPEN:
            raise ValueError("Comments can only be added to an open pull request.")
        self.comments.append(comment)

    def has_unresolved_comments(self) -> bool:
        return any(not comment.resolved for comment in self.comments) or any(
            not comment.resolved
            for review in self.reviews
            for comment in review.comments
        )


@dataclass
class Repository:
    name: str
    branches: Dict[str, Branch] = field(default_factory=dict)
    commits: Dict[str, Commit] = field(default_factory=dict)
    reviewers: Dict[str, Reviewer] = field(default_factory=dict)
    pull_requests: Dict[int, PullRequest] = field(default_factory=dict)
    protections: Dict[str, BranchProtection] = field(default_factory=dict)

    def add_branch(self, name: str, protected: bool = False) -> Branch:
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", name):
            raise ValueError("Invalid branch name.")
        if name in self.branches:
            raise ValueError(f"Branch already exists: {name}")
        branch = Branch(name=name, protected=protected)
        self.branches[name] = branch
        return branch

    def add_commit(self, sha: str, message: str, branch_name: str) -> None:
        if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
            raise ValueError("Commit SHA must contain 7-40 hexadecimal characters.")
        if branch_name not in self.branches:
            raise KeyError(f"Unknown branch: {branch_name}")
        if sha in self.commits:
            raise ValueError("Commit already exists.")

        self.commits[sha] = Commit(sha, message)
        self.branches[branch_name].commits.append(sha)

    def register_reviewer(self, reviewer: Reviewer) -> None:
        if reviewer.username in self.reviewers:
            raise ValueError("Reviewer already registered.")
        self.reviewers[reviewer.username] = reviewer

    def create_pull_request(
        self,
        number: int,
        source_branch: str,
        target_branch: str,
        title: str,
        author: str,
        draft: bool = False,
    ) -> PullRequest:
        if source_branch not in self.branches or target_branch not in self.branches:
            raise KeyError("Source and target branches must exist.")
        if source_branch == target_branch:
            raise ValueError("A pull request cannot target its own source branch.")
        if number in self.pull_requests:
            raise ValueError("Pull request number already exists.")
        if not title.strip():
            raise ValueError("Pull request title cannot be empty.")

        state = PullRequestState.DRAFT if draft else PullRequestState.OPEN
        pr = PullRequest(
            number=number,
            source_branch=source_branch,
            target_branch=target_branch,
            title=title.strip(),
            author=author,
            state=state,
        )
        pr.commits = list(self.branches[source_branch].commits)
        self.pull_requests[number] = pr
        return pr

    def set_branch_protection(
        self, branch_name: str, policy: BranchProtection
    ) -> None:
        if branch_name not in self.branches:
            raise KeyError("Unknown branch.")
        if policy.required_review_count < 0:
            raise ValueError("Required review count cannot be negative.")
        self.branches[branch_name].protected = True
        self.protections[branch_name] = policy

    def reopen_pull_request(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.state != PullRequestState.CLOSED:
            raise ValueError("Only closed pull requests can be reopened.")
        pr.state = PullRequestState.OPEN

    def close_pull_request(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.state == PullRequestState.MERGED:
            raise ValueError("Merged pull requests cannot be closed.")
        pr.state = PullRequestState.CLOSED

    def synchronize_pull_request(self, number: int) -> None:
        pr = self.pull_requests[number]
        if pr.state != PullRequestState.OPEN:
            raise ValueError("Only open pull requests can be synchronized.")
        pr.commits = list(self.branches[pr.source_branch].commits)

    def evaluate_merge(self, number: int) -> Tuple[bool, List[str]]:
        pr = self.pull_requests[number]
        reasons: List[str] = []

        if pr.state != PullRequestState.OPEN:
            reasons.append("Pull request is not open.")

        if not pr.commits:
            reasons.append("Pull request contains no commits.")

        target = self.branches[pr.target_branch]
        policy = self.protections.get(pr.target_branch)

        if target.protected and policy is None:
            reasons.append("Protected branch has no policy.")

        if policy:
            if pr.merge_strategy not in policy.allowed_merge_strategies:
                reasons.append("Selected merge strategy is not permitted.")

            if policy.require_conversation_resolution and pr.has_unresolved_comments():
                reasons.append("Unresolved review conversations remain.")

            approvals: Set[str] = set()
            changes_requested: Set[str] = set()

            for review in pr.reviews:
                if review.dismissed:
                    continue

                reviewer = self.reviewers.get(review.reviewer)
                if reviewer is None or not reviewer.active:
                    continue

                # An approval is valid only when it applies to the current PR state.
                if review.commit_sha not in pr.commits:
                    continue

                if review.state == ReviewState.APPROVED:
                    approvals.add(review.reviewer)
                elif review.state == ReviewState.CHANGES_REQUESTED:
                    changes_requested.add(review.reviewer)

            if changes_requested:
                reasons.append("At least one active reviewer requested changes.")

            if len(approvals) < policy.required_review_count:
                reasons.append(
                    f"Only {len(approvals)} eligible approval(s); "
                    f"{policy.required_review_count} required."
                )

            current_checks = {check.name: check for check in pr.checks}
            for required in policy.required_status_checks:
                check = current_checks.get(required)
                if check is None or not check.passed:
                    reasons.append(f"Required status check failed or is missing: {required}")

        return not reasons, reasons

    def merge_pull_request(self, number: int, actor: str) -> str:
        pr = self.pull_requests[number]
        policy = self.protections.get(pr.target_branch)

        if policy and actor in policy.bypass_users:
            eligible = True
            reasons: List[str] = []
        else:
            eligible, reasons = self.evaluate_merge(number)

        if not eligible:
            raise PermissionError("Merge blocked: " + "; ".join(reasons))

        target = self.branches[pr.target_branch]

        if pr.merge_strategy == MergeStrategy.SQUASH:
            synthetic_sha = f"squash{pr.number:04d}"
            target.commits.append(synthetic_sha)
        elif pr.merge_strategy == MergeStrategy.REBASE:
            target.commits.extend(pr.commits)
        else:
            target.commits.extend(pr.commits)

        pr.state = PullRequestState.MERGED
        return f"PR #{pr.number} merged into {pr.target_branch} using {pr.merge_strategy.value}."


def demonstrate() -> None:
    repo = Repository("inventory-platform")

    repo.add_branch("main", protected=True)
    repo.add_branch("feature/database-schema")

    repo.add_commit(
        "a1b2c3d",
        "Create initial inventory schema",
        "main",
    )
    repo.add_commit(
        "b2c3d4e",
        "Add inventory and warehouse relationships",
        "feature/database-schema",
    )

    repo.register_reviewer(
        Reviewer("maya", teams={"database-reviewers"})
    )
    repo.register_reviewer(
        Reviewer("rahul", teams={"application-reviewers"})
    )

    repo.set_branch_protection(
        "main",
        BranchProtection(
            required_review_count=1,
            required_status_checks={"sql-tests", "integration-tests"},
            require_conversation_resolution=True,
            allow_direct_push=False,
            allow_force_push=False,
            require_linear_history=True,
            allowed_merge_strategies={MergeStrategy.SQUASH},
        ),
    )

    pr = repo.create_pull_request(
        number=42,
        source_branch="feature/database-schema",
        target_branch="main",
        title="Add relational inventory model",
        author="atul",
    )

    pr.add_review(
        Review(
            reviewer="maya",
            state=ReviewState.APPROVED,
            commit_sha="b2c3d4e",
        )
    )

    pr.add_comment(
        ReviewComment(
            reviewer="maya",
            path="schema.sql",
            line=18,
            body="Foreign key correctly connects inventory to warehouse.",
            resolved=True,
        )
    )

    pr.checks.extend(
        [
            StatusCheck("sql-tests", True),
            StatusCheck("integration-tests", True),
        ]
    )

    eligible, reasons = repo.evaluate_merge(42)
    print("Merge eligible:", eligible)

    if reasons:
        print("Blocking reasons:")
        for reason in reasons:
            print(" -", reason)

    if eligible:
        print(repo.merge_pull_request(42, "atul"))

    print("\nRepository state:")
    print(
        json.dumps(
            {
                "repository": repo.name,
                "branches": {
                    name: {
                        "protected": branch.protected,
                        "commits": branch.commits,
                    }
                    for name, branch in repo.branches.items()
                },
                "pull_requests": {
                    number: {
                        "title": item.title,
                        "state": item.state.value,
                        "source": item.source_branch,
                        "target": item.target_branch,
                    }
                    for number, item in repo.pull_requests.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    demonstrate()
