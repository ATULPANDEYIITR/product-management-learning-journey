"use strict";

/*
 * Git and software workflow policy engine.
 * The implementation uses event-driven state changes so repository actions
 * can be observed and audited without coupling policy evaluation to storage.
 */

const crypto = require("node:crypto");
const { EventEmitter } = require("node:events");

const PRState = Object.freeze({
  DRAFT: "draft",
  OPEN: "open",
  CLOSED: "closed",
  MERGED: "merged",
});

const ReviewState = Object.freeze({
  COMMENTED: "commented",
  APPROVED: "approved",
  CHANGES_REQUESTED: "changes_requested",
  DISMISSED: "dismissed",
});

const CheckState = Object.freeze({
  PENDING: "pending",
  PASSED: "passed",
  FAILED: "failed",
});

const MergeStrategy = Object.freeze({
  MERGE: "merge",
  SQUASH: "squash",
  REBASE: "rebase",
});

class WorkflowError extends Error {}

function assertNonEmpty(value, field) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new WorkflowError(`${field} must be non-empty`);
  }
}

class Repository extends EventEmitter {
  constructor(name) {
    super();
    assertNonEmpty(name, "Repository name");
    this.name = name;
    this.users = new Set();
    this.branches = new Map();
    this.protection = new Map();
    this.pullRequests = new Map();
    this.nextPr = 1;
  }

  addUser(username) {
    assertNonEmpty(username, "Username");
    if (/\s/.test(username)) {
      throw new WorkflowError("Username cannot contain whitespace");
    }
    this.users.add(username);
  }

  createBranch(name) {
    assertNonEmpty(name, "Branch name");
    if (this.branches.has(name)) {
      throw new WorkflowError(`Branch already exists: ${name}`);
    }

    this.branches.set(name, {
      name,
      commits: [],
    });
    this.emit("branch.created", { branch: name });
  }

  protectBranch(name, policy) {
    this.requireBranch(name);
    if (policy.requiredApprovals < 0) {
      throw new WorkflowError("Required approvals cannot be negative");
    }
    this.protection.set(name, {
      requiredApprovals: policy.requiredApprovals,
      requiredChecks: new Set(policy.requiredChecks),
      requireResolvedConversations: policy.requireResolvedConversations,
      allowedMergeStrategies: new Set(policy.allowedMergeStrategies),
      allowForcePush: policy.allowForcePush,
      allowDeletion: policy.allowDeletion,
      requireLinearHistory: policy.requireLinearHistory,
    });
  }

  requireBranch(name) {
    if (!this.branches.has(name)) {
      throw new WorkflowError(`Unknown branch: ${name}`);
    }
  }

  commit(branchName, author, message) {
    this.requireBranch(branchName);
    if (!this.users.has(author)) {
      throw new WorkflowError("Unknown commit author");
    }
    assertNonEmpty(message, "Commit message");

    const branch = this.branches.get(branchName);
    const previous = branch.commits.at(-1)?.sha ?? "root";
    const sha = crypto
      .createHash("sha256")
      .update(`${previous}|${author}|${message}|${Date.now()}|${Math.random()}`)
      .digest("hex")
      .slice(0, 12);

    const commit = Object.freeze({
      sha,
      author,
      message: message.trim(),
      timestamp: new Date().toISOString(),
    });

    branch.commits.push(commit);
    this.emit("commit.created", { branch: branchName, commit });
    return commit;
  }

  createPullRequest(source, target, author, draft = false) {
    this.requireBranch(source);
    this.requireBranch(target);

    if (source === target) {
      throw new WorkflowError("Source and target must differ");
    }
    if (!this.users.has(author)) {
      throw new WorkflowError("Unknown PR author");
    }

    const sourceBranch = this.branches.get(source);
    const pr = {
      number: this.nextPr++,
      source,
      target,
      author,
      state: draft ? PRState.DRAFT : PRState.OPEN,
      commits: [...sourceBranch.commits],
      reviews: [],
      checks: [],
      unresolvedConversations: 0,
      synchronized: true,
      mergeStrategy: null,
      mergeError: null,
    };

    this.pullRequests.set(pr.number, pr);
    this.emit("pull_request.created", { pr: this.snapshot(pr) });
    return pr;
  }

  snapshot(pr) {
    return {
      number: pr.number,
      source: pr.source,
      target: pr.target,
      state: pr.state,
      head: pr.commits.at(-1)?.sha ?? null,
    };
  }

  openPullRequest(number) {
    const pr = this.getPr(number);
    if (pr.state !== PRState.DRAFT) {
      throw new WorkflowError("Only draft PRs can be marked ready");
    }
    pr.state = PRState.OPEN;
    this.emit("pull_request.ready", this.snapshot(pr));
  }

  synchronize(number) {
    const pr = this.getPr(number);
    pr.commits = [...this.branches.get(pr.source).commits];
    pr.synchronized = true;
    pr.mergeError = null;
    this.emit("pull_request.synchronized", this.snapshot(pr));
  }

  getPr(number) {
    const pr = this.pullRequests.get(number);
    if (!pr) {
      throw new WorkflowError(`Unknown Pull Request #${number}`);
    }
    return pr;
  }

  addReview(number, reviewer, state, comments = []) {
    const pr = this.getPr(number);

    if (!this.users.has(reviewer)) {
      throw new WorkflowError("Unknown reviewer");
    }
    if (reviewer === pr.author) {
      throw new WorkflowError("PR author cannot approve their own PR");
    }
    if (pr.state !== PRState.OPEN) {
      throw new WorkflowError("Review requires an open PR");
    }
    if (
      state === ReviewState.CHANGES_REQUESTED &&
      comments.length === 0
    ) {
      throw new WorkflowError("Requested changes require comments");
    }

    pr.reviews.push({
      reviewer,
      state,
      commitSha: pr.commits.at(-1)?.sha ?? null,
      comments: [...comments],
      timestamp: new Date().toISOString(),
    });

    this.emit("review.submitted", {
      number,
      reviewer,
      state,
    });
  }

  addStatusCheck(number, name, state) {
    const pr = this.getPr(number);
    assertNonEmpty(name, "Status check name");

    pr.checks.push({
      name,
      state,
      commitSha: pr.commits.at(-1)?.sha ?? null,
    });

    this.emit("check.updated", { number, name, state });
  }

  addConversation(number) {
    const pr = this.getPr(number);
    pr.unresolvedConversations += 1;
  }

  resolveConversation(number) {
    const pr = this.getPr(number);
    if (pr.unresolvedConversations === 0) {
      throw new WorkflowError("No unresolved conversations");
    }
    pr.unresolvedConversations -= 1;
  }

  evaluate(number, strategy = null) {
    const pr = this.getPr(number);
    const reasons = [];
    const policy = this.protection.get(pr.target);
    const head = pr.commits.at(-1)?.sha ?? null;

    if (pr.state !== PRState.OPEN) reasons.push("PR is not open");
    if (!head) reasons.push("PR has no commits");
    if (!pr.synchronized) reasons.push("Source branch is not synchronized");
    if (!strategy) reasons.push("Merge strategy is not selected");

    if (policy) {
      const latest = new Map();

      for (const review of pr.reviews) {
        latest.set(review.reviewer, review);
      }

      const approvals = [...latest.values()].filter(
        (review) =>
          review.state === ReviewState.APPROVED &&
          review.commitSha === head
      ).length;

      const changesRequested = [...latest.values()].some(
        (review) =>
          review.state === ReviewState.CHANGES_REQUESTED &&
          review.commitSha === head
      );

      if (changesRequested) {
        reasons.push("A current review requests changes");
      }

      if (approvals < policy.requiredApprovals) {
        reasons.push(
          `Approvals ${approvals}/${policy.requiredApprovals}`
        );
      }

      for (const required of policy.requiredChecks) {
        const passed = pr.checks.some(
          (check) =>
            check.name === required &&
            check.state === CheckState.PASSED &&
            check.commitSha === head
        );
        if (!passed) reasons.push(`Check not passed: ${required}`);
      }

      if (
        policy.requireResolvedConversations &&
        pr.unresolvedConversations > 0
      ) {
        reasons.push("Unresolved conversations remain");
      }

      if (
        strategy &&
        !policy.allowedMergeStrategies.has(strategy)
      ) {
        reasons.push("Merge strategy is prohibited");
      }
    }

    return {
      eligible: reasons.length === 0,
      reasons,
    };
  }

  merge(number, strategy) {
    const pr = this.getPr(number);
    const result = this.evaluate(number, strategy);

    if (!result.eligible) {
      pr.mergeError = result.reasons.join("; ");
      throw new WorkflowError(pr.mergeError);
    }

    const target = this.branches.get(pr.target);
    const source = this.branches.get(pr.source);

    if (strategy === MergeStrategy.SQUASH) {
      const sha = crypto
        .createHash("sha256")
        .update(`squash:${pr.number}:${source.commits.at(-1).sha}`)
        .digest("hex")
        .slice(0, 12);

      target.commits.push({
        sha,
        author: pr.author,
        message: `Squash PR #${pr.number}`,
        timestamp: new Date().toISOString(),
      });
    } else {
      target.commits.push(...source.commits);
    }

    pr.mergeStrategy = strategy;
    pr.state = PRState.MERGED;
    this.emit("pull_request.merged", {
      number,
      strategy,
      target: pr.target,
    });
  }
}

async function runWorkflow() {
  const repo = new Repository("orders-service");

  repo.on("review.submitted", (event) => {
    console.log(
      `[audit] review=${event.state} reviewer=${event.reviewer} PR=#${event.number}`
    );
  });

  repo.on("pull_request.merged", (event) => {
    console.log(
      `[audit] merged PR=#${event.number} strategy=${event.strategy}`
    );
  });

  ["alice", "bob", "carol"].forEach((user) => repo.addUser(user));
  repo.createBranch("main");
  repo.createBranch("feature/order-validation");

  repo.protectBranch("main", {
    requiredApprovals: 2,
    requiredChecks: ["tests", "security"],
    requireResolvedConversations: true,
    allowedMergeStrategies: new Set([
      MergeStrategy.SQUASH,
      MergeStrategy.REBASE,
    ]),
    allowForcePush: false,
    allowDeletion: false,
    requireLinearHistory: true,
  });

  repo.commit("main", "alice", "Create order service");
  repo.commit(
    "feature/order-validation",
    "alice",
    "Validate order quantities"
  );

  const pr = repo.createPullRequest(
    "feature/order-validation",
    "main",
    "alice",
    true
  );

  repo.openPullRequest(pr.number);
  repo.synchronize(pr.number);

  repo.addConversation(pr.number);
  repo.addReview(
    pr.number,
    "bob",
    ReviewState.COMMENTED,
    ["Please verify maximum order quantity."]
  );
  repo.addReview(
    pr.number,
    "carol",
    ReviewState.CHANGES_REQUESTED,
    ["Reject quantities above the configured limit."]
  );

  repo.addStatusCheck(pr.number, "tests", CheckState.PASSED);
  repo.addStatusCheck(pr.number, "security", CheckState.PASSED);

  console.log("Before resolution:", repo.evaluate(pr.number, MergeStrategy.SQUASH));

  repo.resolveConversation(pr.number);
  repo.addReview(pr.number, "bob", ReviewState.APPROVED);
  repo.addReview(pr.number, "carol", ReviewState.APPROVED);

  console.log("After approvals:", repo.evaluate(pr.number, MergeStrategy.SQUASH));

  repo.merge(pr.number, MergeStrategy.SQUASH);

  console.log("Final PR state:", pr.state);
  console.log(
    "Protected branch head:",
    repo.branches.get("main").commits.at(-1).sha
  );

  // Asynchronous event processing models audit/log delivery without blocking
  // the repository transaction itself.
  await new Promise((resolve) => setImmediate(resolve));
}

runWorkflow().catch((error) => {
  console.error(`Workflow failed: ${error.message}`);
  process.exitCode = 1;
});
