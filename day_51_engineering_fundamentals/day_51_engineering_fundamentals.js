"use strict";

/*
 * Event-driven repository governance model.
 *
 * Pull Requests represent the change workflow.
 * Reviews represent evaluation of the changes.
 * Approvals are review decisions.
 * Branch protection determines whether the repository permits the merge.
 */

const EventEmitter = require("node:events");

const PullRequestState = Object.freeze({
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

class PullRequest extends EventEmitter {
    constructor({ number, title, author, source, target }) {
        super();

        if (!Number.isInteger(number) || number <= 0) {
            throw new Error("Pull Request number must be positive.");
        }

        if (!author || !source || !target || source === target) {
            throw new Error("Invalid Pull Request branch configuration.");
        }

        this.number = number;
        this.title = title;
        this.author = author;
        this.source = source;
        this.target = target;
        this.state = PullRequestState.DRAFT;

        this.commits = [];
        this.reviewers = new Set();
        this.reviews = new Map();
        this.checks = new Map();
        this.unresolvedConversations = new Set();
        this.synchronizedWithBase = true;
        this.hasConflicts = false;
    }

    addCommit(sha, message) {
        if ([PullRequestState.CLOSED, PullRequestState.MERGED].includes(this.state)) {
            throw new Error("Cannot modify a closed or merged Pull Request.");
        }

        if (!sha || !message) {
            throw new Error("Commit SHA and message are required.");
        }

        this.commits.push(Object.freeze({ sha, message }));
        this.synchronizedWithBase = false;
        this.emit("commitAdded", { sha });
    }

    markReadyForReview() {
        if (this.state !== PullRequestState.DRAFT) {
            throw new Error("Only draft Pull Requests can become ready.");
        }

        if (this.commits.length === 0) {
            throw new Error("A Pull Request needs at least one commit.");
        }

        this.state = PullRequestState.OPEN;
        this.emit("opened", this.number);
    }

    requestReview(reviewer) {
        if (this.state !== PullRequestState.OPEN) {
            throw new Error("Reviews can only be requested on open Pull Requests.");
        }

        if (reviewer === this.author) {
            throw new Error("The author cannot be an external reviewer of their own change.");
        }

        this.reviewers.add(reviewer);
        this.emit("reviewRequested", { reviewer });
    }

    submitReview(reviewer, state, comment = "") {
        if (!this.reviewers.has(reviewer)) {
            throw new Error(`Reviewer ${reviewer} was not requested.`);
        }

        if (!Object.values(ReviewState).includes(state)) {
            throw new Error("Invalid review state.");
        }

        this.reviews.set(reviewer, {
            reviewer,
            state,
            comment,
            submittedAt: new Date().toISOString()
        });

        this.emit("reviewSubmitted", { reviewer, state });
    }

    setCheck(name, passed) {
        if (typeof passed !== "boolean") {
            throw new Error("Status check result must be boolean.");
        }

        this.checks.set(name, passed);
        this.emit("statusChanged", { name, passed });
    }

    addConversation(id) {
        this.unresolvedConversations.add(id);
    }

    resolveConversation(id) {
        if (!this.unresolvedConversations.delete(id)) {
            throw new Error(`Conversation ${id} is not unresolved.`);
        }

        this.emit("conversationResolved", id);
    }

    synchronize() {
        if (this.hasConflicts) {
            throw new Error("Conflicts must be resolved before synchronization.");
        }

        this.synchronizedWithBase = true;
        this.emit("synchronized", this.number);
    }

    resolveConflicts() {
        this.hasConflicts = false;
        this.synchronizedWithBase = false;
        this.emit("conflictsResolved", this.number);
    }
}

class BranchProtectionPolicy {
    constructor({
        requiredApprovals,
        requiredChecks,
        requireResolvedConversations,
        requireLinearHistory,
        allowDirectPush
    }) {
        if (requiredApprovals < 0) {
            throw new Error("Required approvals cannot be negative.");
        }

        this.requiredApprovals = requiredApprovals;
        this.requiredChecks = new Set(requiredChecks);
        this.requireResolvedConversations = requireResolvedConversations;
        this.requireLinearHistory = requireLinearHistory;
        this.allowDirectPush = allowDirectPush;
    }
}

class GovernanceEngine {
    constructor(policy) {
        this.policy = policy;
    }

    evaluate(pr) {
        const failures = [];

        if (pr.state !== PullRequestState.OPEN) {
            failures.push("Pull Request is not open.");
        }

        if (pr.commits.length === 0) {
            failures.push("No commits are present.");
        }

        if (pr.hasConflicts) {
            failures.push("Merge conflicts exist.");
        }

        if (!pr.synchronizedWithBase) {
            failures.push("Pull Request must be synchronized with the base branch.");
        }

        if (
            this.policy.requireResolvedConversations &&
            pr.unresolvedConversations.size > 0
        ) {
            failures.push("Unresolved review conversations remain.");
        }

        const approvals = [...pr.reviews.values()].filter(
            review => review.state === ReviewState.APPROVED
        ).length;

        if (approvals < this.policy.requiredApprovals) {
            failures.push(
                `Required approvals: ${this.policy.requiredApprovals}; received: ${approvals}.`
            );
        }

        for (const check of this.policy.requiredChecks) {
            if (pr.checks.get(check) !== true) {
                failures.push(`Required check '${check}' has not passed.`);
            }
        }

        return {
            eligible: failures.length === 0,
            failures
        };
    }

    merge(pr) {
        const result = this.evaluate(pr);

        if (!result.eligible) {
            throw new Error(`Merge blocked: ${result.failures.join(" ")}`);
        }

        pr.state = PullRequestState.MERGED;
        pr.emit("merged", pr.number);
    }
}

function runScenario() {
    const pr = new PullRequest({
        number: 107,
        title: "Enforce API authorization",
        author: "alice",
        source: "feature/api-authorization",
        target: "main"
    });

    const policy = new BranchProtectionPolicy({
        requiredApprovals: 2,
        requiredChecks: ["build", "tests", "security"],
        requireResolvedConversations: true,
        requireLinearHistory: true,
        allowDirectPush: false
    });

    const governance = new GovernanceEngine(policy);

    pr.on("reviewRequested", event => {
        console.log(`Review requested from ${event.reviewer}`);
    });

    pr.on("statusChanged", event => {
        console.log(`Check ${event.name}: ${event.passed ? "passed" : "failed"}`);
    });

    pr.on("merged", number => {
        console.log(`Pull Request #${number} merged.`);
    });

    pr.addCommit("c101", "Validate API access token");
    pr.addCommit("c102", "Reject unauthorized resource access");
    pr.markReadyForReview();

    pr.requestReview("bob");
    pr.requestReview("carol");

    pr.submitReview("bob", ReviewState.APPROVED, "Authorization boundary is correct.");
    pr.submitReview("carol", ReviewState.APPROVED, "Failure paths are covered.");

    pr.setCheck("build", true);
    pr.setCheck("tests", true);
    pr.setCheck("security", true);

    pr.addConversation("discussion-1");

    let result = governance.evaluate(pr);
    console.log("Eligible before resolving discussion:", result);

    pr.resolveConversation("discussion-1");
    pr.synchronizedWithBase = true;

    result = governance.evaluate(pr);
    console.log("Eligible after resolution:", result);

    governance.merge(pr);

    try {
        pr.addCommit("c103", "Illegal post-merge change");
    } catch (error) {
        console.log("Expected failure:", error.message);
    }
}

runScenario();
