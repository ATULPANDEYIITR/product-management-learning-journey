"use strict";

/*
 * Repository governance model.
 * Pull Requests propose changes.
 * Code reviews evaluate those changes.
 * Approvals represent review decisions.
 * Branch protection enforces repository-level merge conditions.
 */

const PRState = Object.freeze({
  DRAFT: "draft",
  OPEN: "open",
  CLOSED: "closed",
  MERGED: "merged"
});

const ReviewState = Object.freeze({
  COMMENTED: "commented",
  APPROVED: "approved",
  CHANGES_REQUESTED: "changes_requested",
  DISMISSED: "dismissed"
});

const CheckState = Object.freeze({
  PENDING: "pending",
  PASSED: "passed",
  FAILED: "failed"
});

const MergeStrategy = Object.freeze({
  MERGE_COMMIT: "merge_commit",
  SQUASH: "squash",
  REBASE: "rebase"
});

class ValidationError extends Error {}

class Commit {
  constructor(sha, message, author) {
    if (!sha || !message || !author) {
      throw new ValidationError("Commit requires sha, message, and author.");
    }
    this.sha = sha;
    this.message = message;
    this.author = author;
  }
}

class Branch {
  constructor(name, commits = []) {
    if (!name) throw new ValidationError("Branch name is required.");
    this.name = name;
    this.commits = [...commits];
    this.protected = false;
  }

  get head() {
    return this.commits.length
      ? this.commits[this.commits.length - 1].sha
      : null;
  }
}

class ReviewComment {
  constructor({ reviewer, filePath, line, body, resolved = false }) {
    if (!reviewer || !filePath || !Number.isInteger(line) || line < 1 || !body) {
      throw new ValidationError("Invalid review comment.");
    }
    this.reviewer = reviewer;
    this.filePath = filePath;
    this.line = line;
    this.body = body;
    this.resolved = resolved;
  }
}

class Review {
  constructor({ reviewer, state, comments = [] }) {
    if (!reviewer || !Object.values(ReviewState).includes(state)) {
      throw new ValidationError("Invalid review.");
    }
    this.reviewer = reviewer;
    this.state = state;
    this.comments = comments;
    this.stale = false;
    this.dismissed = state === ReviewState.DISMISSED;
  }
}

class StatusCheck {
  constructor(name, state) {
    if (!name || !Object.values(CheckState).includes(state)) {
      throw new ValidationError("Invalid status check.");
    }
    this.name = name;
    this.state = state;
  }
}

class BranchProtectionPolicy {
  constructor({
    requiredApprovals = 1,
    requiredChecks = [],
    requireConversationsResolved = true,
    requireLinearHistory = false,
    allowDirectPush = false,
    allowForcePush = false,
    allowBranchDeletion = false,
    allowAdminBypass = false,
    allowedMergeStrategies = [
      MergeStrategy.SQUASH,
      MergeStrategy.REBASE
    ]
  } = {}) {
    if (!Number.isInteger(requiredApprovals) || requiredApprovals < 0) {
      throw new ValidationError("requiredApprovals must be a non-negative integer.");
    }

    this.requiredApprovals = requiredApprovals;
    this.requiredChecks = new Set(requiredChecks);
    this.requireConversationsResolved = requireConversationsResolved;
    this.requireLinearHistory = requireLinearHistory;
    this.allowDirectPush = allowDirectPush;
    this.allowForcePush = allowForcePush;
    this.allowBranchDeletion = allowBranchDeletion;
    this.allowAdminBypass = allowAdminBypass;
    this.allowedMergeStrategies = new Set(allowedMergeStrategies);
  }
}

class PullRequest {
  constructor({
    number,
    title,
    sourceBranch,
    targetBranch,
    author,
    draft = false,
    baseHead
  }) {
    if (!title || !sourceBranch || !targetBranch || !author) {
      throw new ValidationError("Incomplete Pull Request.");
    }

    this.number = number;
    this.title = title;
    this.sourceBranch = sourceBranch;
    this.targetBranch = targetBranch;
    this.author = author;
    this.state = draft ? PRState.DRAFT : PRState.OPEN;
    this.commits = [];
    this.reviews = [];
    this.checks = new Map();
    this.requestedReviewers = new Set();
    this.baseHeadAtCreation = baseHead;
  }

  requestReview(reviewer) {
    if (reviewer === this.author) {
      throw new ValidationError("Authors cannot approve their own Pull Request.");
    }
    this.requestedReviewers.add(reviewer);
  }

  addCommit(commit) {
    if (![PRState.DRAFT, PRState.OPEN].includes(this.state)) {
      throw new ValidationError("Cannot change a closed or merged Pull Request.");
    }

    this.commits.push(commit);

    for (const review of this.reviews) {
      if (review.state === ReviewState.APPROVED) {
        review.stale = true;
      }
    }
  }

  addReview(review) {
    if (review.reviewer === this.author) {
      throw new ValidationError("Self-review is prohibited.");
    }
    this.reviews.push(review);
  }

  setCheck(check) {
    this.checks.set(check.name, check);
  }
}

class Repository {
  constructor(name) {
    this.name = name;
    this.branches = new Map();
    this.pullRequests = new Map();
    this.protection = new Map();
    this.nextPRNumber = 1;
  }

  addBranch(branch) {
    if (this.branches.has(branch.name)) {
      throw new ValidationError(`Branch already exists: ${branch.name}`);
    }
    this.branches.set(branch.name, branch);
  }

  protectBranch(branchName, policy) {
    const branch = this.branches.get(branchName);
    if (!branch) throw new ValidationError("Unknown branch.");
    branch.protected = true;
    this.protection.set(branchName, policy);
  }

  createPullRequest({
    title,
    sourceBranch,
    targetBranch,
    author,
    draft = false
  }) {
    const source = this.branches.get(sourceBranch);
    const target = this.branches.get(targetBranch);

    if (!source || !target) {
      throw new ValidationError("Both source and target branches must exist.");
    }

    if (sourceBranch === targetBranch) {
      throw new ValidationError("Source and target branches must differ.");
    }

    const pr = new PullRequest({
      number: this.nextPRNumber++,
      title,
      sourceBranch,
      targetBranch,
      author,
      draft,
      baseHead: target.head
    });

    pr.commits = [...source.commits];
    this.pullRequests.set(pr.number, pr);
    return pr;
  }

  synchronize(prNumber) {
    const pr = this.getPR(prNumber);
    const target = this.branches.get(pr.targetBranch);

    if (target.head === pr.baseHeadAtCreation) return false;

    pr.baseHeadAtCreation = target.head;

    for (const review of pr.reviews) {
      if (review.state === ReviewState.APPROVED) {
        review.stale = true;
      }
    }

    return true;
  }

  getPR(number) {
    const pr = this.pullRequests.get(number);
    if (!pr) throw new ValidationError(`Unknown Pull Request #${number}.`);
    return pr;
  }

  evaluateMerge(prNumber, {
    strategy = MergeStrategy.SQUASH,
    administrator = false
  } = {}) {
    const pr = this.getPR(prNumber);
    const target = this.branches.get(pr.targetBranch);
    const policy = this.protection.get(pr.targetBranch);
    const reasons = [];

    if (pr.state !== PRState.OPEN) {
      reasons.push("Pull Request must be open.");
    }

    if (pr.commits.length === 0) {
      reasons.push("Pull Request has no changes.");
    }

    if (!Object.values(MergeStrategy).includes(strategy)) {
      reasons.push("Unknown merge strategy.");
    }

    if (policy) {
      if (!policy.allowedMergeStrategies.has(strategy)) {
        reasons.push("Merge strategy is not permitted.");
      }

      const approvals = new Set(
        pr.reviews
          .filter(review =>
            review.state === ReviewState.APPROVED &&
            !review.stale &&
            !review.dismissed &&
            pr.requestedReviewers.has(review.reviewer)
          )
          .map(review => review.reviewer)
      );

      if (approvals.size < policy.requiredApprovals) {
        reasons.push(
          `Approval requirement not met: ${approvals.size}/${policy.requiredApprovals}.`
        );
      }

      for (const requiredCheck of policy.requiredChecks) {
        const check = pr.checks.get(requiredCheck);
        if (!check || check.state !== CheckState.PASSED) {
          reasons.push(`Required check is not passing: ${requiredCheck}.`);
        }
      }

      if (policy.requireConversationsResolved) {
        const unresolved = pr.reviews.some(review =>
          review.comments.some(comment => !comment.resolved)
        );
        if (unresolved) {
          reasons.push("Unresolved review conversations remain.");
        }
      }

      if (
        policy.requireLinearHistory &&
        strategy === MergeStrategy.MERGE_COMMIT
      ) {
        reasons.push("Merge commits are incompatible with linear history.");
      }

      if (administrator && policy.allowAdminBypass) {
        return {
          eligible: pr.state === PRState.OPEN && pr.commits.length > 0,
          reasons: []
        };
      }
    }

    if (
      pr.reviews.some(
        review =>
          review.state === ReviewState.CHANGES_REQUESTED &&
          !review.dismissed
      )
    ) {
      reasons.push("An active reviewer requested changes.");
    }

    return {
      eligible: reasons.length === 0,
      reasons
    };
  }

  merge(prNumber, actor, options = {}) {
    const { strategy = MergeStrategy.SQUASH, administrator = false } = options;
    const result = this.evaluateMerge(prNumber, { strategy, administrator });

    if (!result.eligible) {
      throw new Error(`Merge blocked: ${result.reasons.join(" | ")}`);
    }

    const pr = this.getPR(prNumber);
    const target = this.branches.get(pr.targetBranch);

    if (strategy === MergeStrategy.SQUASH) {
      target.commits.push(
        new Commit(`squash-${pr.number}`, pr.title, actor)
      );
    } else if (strategy === MergeStrategy.MERGE_COMMIT) {
      target.commits.push(
        new Commit(`merge-${pr.number}`, `Merge PR #${pr.number}`, actor)
      );
    } else {
      target.commits.push(...pr.commits);
    }

    pr.state = PRState.MERGED;
  }
}

function main() {
  const repository = new Repository("commerce-platform");

  const main = new Branch("main", [
    new Commit("a001", "Initial application", "alice"),
    new Commit("a002", "Add order service", "alice")
  ]);

  const feature = new Branch("feature/refunds", [
    ...main.commits,
    new Commit("a003", "Implement refunds", "bob")
  ]);

  repository.addBranch(main);
  repository.addBranch(feature);

  repository.protectBranch(
    "main",
    new BranchProtectionPolicy({
      requiredApprovals: 2,
      requiredChecks: ["unit-tests", "security-scan"],
      requireConversationsResolved: true,
      requireLinearHistory: true,
      allowDirectPush: false,
      allowForcePush: false,
      allowBranchDeletion: false,
      allowedMergeStrategies: [
        MergeStrategy.SQUASH,
        MergeStrategy.REBASE
      ]
    })
  );

  const pr = repository.createPullRequest({
    title: "Implement refund workflow",
    sourceBranch: "feature/refunds",
    targetBranch: "main",
    author: "bob"
  });

  pr.requestReview("alice");
  pr.requestReview("carol");

  pr.addReview(
    new Review({
      reviewer: "alice",
      state: ReviewState.APPROVED,
      comments: [
        new ReviewComment({
          reviewer: "alice",
          filePath: "refund.js",
          line: 27,
          body: "Validate refund amount against the original order.",
          resolved: true
        })
      ]
    })
  );

  pr.addReview(
    new Review({
      reviewer: "carol",
      state: ReviewState.APPROVED
    })
  );

  pr.setCheck(new StatusCheck("unit-tests", CheckState.PASSED));
  pr.setCheck(new StatusCheck("security-scan", CheckState.PASSED));

  const decision = repository.evaluateMerge(pr.number);

  console.log(`PR #${pr.number} eligible: ${decision.eligible}`);
  if (!decision.eligible) {
    decision.reasons.forEach(reason => console.log(`BLOCKED: ${reason}`));
  }

  repository.merge(pr.number, "release-manager");

  console.log(`PR state: ${pr.state}`);
  console.log(`main HEAD: ${main.head}`);

  // A new commit invalidates previous approval state.
  const pr2 = repository.createPullRequest({
    title: "Improve refund validation",
    sourceBranch: "feature/refunds",
    targetBranch: "main",
    author: "david"
  });

  pr2.requestReview("alice");
  pr2.addReview(
    new Review({
      reviewer: "alice",
      state: ReviewState.APPROVED
    })
  );

  pr2.setCheck(new StatusCheck("unit-tests", CheckState.PASSED));
  pr2.setCheck(new StatusCheck("security-scan", CheckState.PASSED));

  pr2.addCommit(
    new Commit("a004", "Handle invalid refund amount", "david")
  );

  const staleDecision = repository.evaluateMerge(pr2.number);

  console.log(`PR #${pr2.number} eligible after new commit: ${staleDecision.eligible}`);
  staleDecision.reasons.forEach(reason => console.log(`BLOCKED: ${reason}`));
}

main();
