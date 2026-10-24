'use strict';

/*
 * Relational repository-governance model.
 *
 * The repository itself is represented as related objects, while merge
 * eligibility is calculated from branch protection, reviews, comments,
 * approvals, and status checks.
 */

const PullRequestState = Object.freeze({
    DRAFT: 'draft',
    OPEN: 'open',
    CLOSED: 'closed',
    MERGED: 'merged'
});

const ReviewState = Object.freeze({
    COMMENTED: 'commented',
    APPROVED: 'approved',
    CHANGES_REQUESTED: 'changes_requested',
    DISMISSED: 'dismissed'
});

const MergeStrategy = Object.freeze({
    MERGE_COMMIT: 'merge_commit',
    SQUASH: 'squash',
    REBASE: 'rebase'
});

class ValidationError extends Error {}
class MergeBlockedError extends Error {}

class Repository {
    constructor(name) {
        if (!name || !name.trim()) {
            throw new ValidationError('Repository name is required.');
        }

        this.name = name.trim();
        this.branches = new Map();
        this.commits = new Map();
        this.reviewers = new Map();
        this.pullRequests = new Map();
        this.protections = new Map();
        this.nextEventId = 1;
    }

    addBranch(name, protectedBranch = false) {
        if (!/^[A-Za-z0-9._/-]+$/.test(name)) {
            throw new ValidationError(`Invalid branch name: ${name}`);
        }

        if (this.branches.has(name)) {
            throw new ValidationError(`Branch already exists: ${name}`);
        }

        const branch = {
            name,
            protected: protectedBranch,
            commits: []
        };

        this.branches.set(name, branch);
        return branch;
    }

    addCommit(sha, message, branchName) {
        if (!/^[0-9a-f]{7,40}$/.test(sha)) {
            throw new ValidationError('Commit SHA must be 7-40 hexadecimal characters.');
        }

        if (!message || !message.trim()) {
            throw new ValidationError('Commit message is required.');
        }

        const branch = this.branches.get(branchName);

        if (!branch) {
            throw new ValidationError(`Unknown branch: ${branchName}`);
        }

        if (this.commits.has(sha)) {
            throw new ValidationError(`Commit already exists: ${sha}`);
        }

        const commit = Object.freeze({
            sha,
            message: message.trim()
        });

        this.commits.set(sha, commit);
        branch.commits.push(sha);
        return commit;
    }

    registerReviewer(username, teams = []) {
        if (!username || !username.trim()) {
            throw new ValidationError('Reviewer username is required.');
        }

        if (this.reviewers.has(username)) {
            throw new ValidationError('Reviewer already exists.');
        }

        this.reviewers.set(username, {
            username,
            teams: new Set(teams),
            active: true
        });
    }

    protectBranch(branchName, policy) {
        const branch = this.branches.get(branchName);

        if (!branch) {
            throw new ValidationError(`Unknown branch: ${branchName}`);
        }

        if (!Number.isInteger(policy.requiredReviewCount) ||
            policy.requiredReviewCount < 0) {
            throw new ValidationError('Invalid required review count.');
        }

        branch.protected = true;
        this.protections.set(branchName, {
            requiredReviewCount: policy.requiredReviewCount,
            requiredStatusChecks: new Set(policy.requiredStatusChecks || []),
            requireConversationResolution:
                policy.requireConversationResolution ?? true,
            allowDirectPush: policy.allowDirectPush ?? false,
            allowForcePush: policy.allowForcePush ?? false,
            requireLinearHistory: policy.requireLinearHistory ?? false,
            allowedMergeStrategies: new Set(
                policy.allowedMergeStrategies || [MergeStrategy.SQUASH]
            ),
            bypassUsers: new Set(policy.bypassUsers || [])
        });
    }

    createPullRequest({
        number,
        sourceBranch,
        targetBranch,
        title,
        author,
        draft = false
    }) {
        if (this.pullRequests.has(number)) {
            throw new ValidationError('Pull request number already exists.');
        }

        if (!this.branches.has(sourceBranch) ||
            !this.branches.has(targetBranch)) {
            throw new ValidationError('Both branches must exist.');
        }

        if (sourceBranch === targetBranch) {
            throw new ValidationError('Source and target branches must differ.');
        }

        if (!title || !title.trim()) {
            throw new ValidationError('Pull request title is required.');
        }

        const source = this.branches.get(sourceBranch);

        const pullRequest = {
            number,
            sourceBranch,
            targetBranch,
            title: title.trim(),
            author,
            state: draft ? PullRequestState.DRAFT : PullRequestState.OPEN,
            commits: [...source.commits],
            reviews: [],
            comments: [],
            checks: new Map(),
            mergeStrategy: MergeStrategy.SQUASH,
            createdEvent: this.nextEventId++
        };

        this.pullRequests.set(number, pullRequest);
        return pullRequest;
    }

    markReadyForReview(number) {
        const pr = this.getPullRequest(number);

        if (pr.state !== PullRequestState.DRAFT) {
            throw new ValidationError('Only draft pull requests can become ready.');
        }

        pr.state = PullRequestState.OPEN;
    }

    addReview(number, review) {
        const pr = this.getPullRequest(number);

        if (pr.state !== PullRequestState.OPEN) {
            throw new ValidationError('Reviews require an open pull request.');
        }

        if (!this.reviewers.has(review.reviewer)) {
            throw new ValidationError('Reviewer is not registered.');
        }

        if (!Object.values(ReviewState).includes(review.state)) {
            throw new ValidationError('Unknown review state.');
        }

        pr.reviews.push({
            reviewer: review.reviewer,
            state: review.state,
            commitSha: review.commitSha,
            dismissed: false,
            comments: []
        });
    }

    addComment(number, comment) {
        const pr = this.getPullRequest(number);

        if (pr.state !== PullRequestState.OPEN) {
            throw new ValidationError('Comments require an open pull request.');
        }

        if (!comment.body || !comment.body.trim()) {
            throw new ValidationError('Comment body is required.');
        }

        pr.comments.push({
            reviewer: comment.reviewer,
            path: comment.path,
            line: comment.line,
            body: comment.body.trim(),
            resolved: Boolean(comment.resolved)
        });
    }

    setStatus(number, name, passed) {
        const pr = this.getPullRequest(number);

        if (!name || !name.trim()) {
            throw new ValidationError('Status check name is required.');
        }

        pr.checks.set(name, Boolean(passed));
    }

    synchronize(number) {
        const pr = this.getPullRequest(number);

        if (pr.state !== PullRequestState.OPEN) {
            throw new ValidationError('Only open pull requests can synchronize.');
        }

        const source = this.branches.get(pr.sourceBranch);
        pr.commits = [...source.commits];

        /*
         * A new commit invalidates reviews that targeted an older commit.
         * The reviews remain as historical records, but they do not count
         * toward current merge eligibility.
         */
    }

    resolveComment(number, index) {
        const pr = this.getPullRequest(number);

        if (!pr.comments[index]) {
            throw new ValidationError('Comment does not exist.');
        }

        pr.comments[index].resolved = true;
    }

    dismissReview(number, reviewer) {
        const pr = this.getPullRequest(number);

        const review = pr.reviews.find(
            item => item.reviewer === reviewer && !item.dismissed
        );

        if (!review) {
            throw new ValidationError('Active review not found.');
        }

        review.dismissed = true;
        review.state = ReviewState.DISMISSED;
    }

    evaluateMerge(number) {
        const pr = this.getPullRequest(number);
        const policy = this.protections.get(pr.targetBranch);
        const reasons = [];

        if (pr.state !== PullRequestState.OPEN) {
            reasons.push('Pull request is not open.');
        }

        if (pr.commits.length === 0) {
            reasons.push('Pull request contains no commits.');
        }

        if (!policy) {
            return {
                eligible: reasons.length === 0,
                reasons
            };
        }

        if (!policy.allowedMergeStrategies.has(pr.mergeStrategy)) {
            reasons.push('Merge strategy is not permitted.');
        }

        if (
            policy.requireConversationResolution &&
            pr.comments.some(comment => !comment.resolved)
        ) {
            reasons.push('Unresolved review conversation exists.');
        }

        const approvals = new Set();
        const requestedChanges = new Set();

        for (const review of pr.reviews) {
            if (review.dismissed) {
                continue;
            }

            const reviewer = this.reviewers.get(review.reviewer);

            if (!reviewer || !reviewer.active) {
                continue;
            }

            /*
             * Approval is tied to the commit reviewed. This models stale
             * approvals after a new changeset is pushed.
             */
            if (!pr.commits.includes(review.commitSha)) {
                continue;
            }

            if (review.state === ReviewState.APPROVED) {
                approvals.add(review.reviewer);
            }

            if (review.state === ReviewState.CHANGES_REQUESTED) {
                requestedChanges.add(review.reviewer);
            }
        }

        if (requestedChanges.size > 0) {
            reasons.push('A reviewer has requested changes.');
        }

        if (approvals.size < policy.requiredReviewCount) {
            reasons.push(
                `${approvals.size} eligible approval(s), ` +
                `${policy.requiredReviewCount} required.`
            );
        }

        for (const requiredCheck of policy.requiredStatusChecks) {
            if (pr.checks.get(requiredCheck) !== true) {
                reasons.push(`Required status check failed or is missing: ${requiredCheck}`);
            }
        }

        return {
            eligible: reasons.length === 0,
            reasons
        };
    }

    merge(number, actor) {
        const pr = this.getPullRequest(number);
        const policy = this.protections.get(pr.targetBranch);

        const bypass =
            policy && policy.bypassUsers.has(actor);

        const result = bypass
            ? { eligible: true, reasons: [] }
            : this.evaluateMerge(number);

        if (!result.eligible) {
            throw new MergeBlockedError(
                `PR #${number} cannot be merged: ${result.reasons.join('; ')}`
            );
        }

        const target = this.branches.get(pr.targetBranch);

        if (pr.mergeStrategy === MergeStrategy.SQUASH) {
            target.commits.push(`squash-${pr.number}`);
        } else {
            target.commits.push(...pr.commits);
        }

        pr.state = PullRequestState.MERGED;

        return {
            number,
            target: pr.targetBranch,
            strategy: pr.mergeStrategy,
            state: pr.state
        };
    }

    getPullRequest(number) {
        const pr = this.pullRequests.get(number);

        if (!pr) {
            throw new ValidationError(`Unknown pull request: ${number}`);
        }

        return pr;
    }
}

function main() {
    const repository = new Repository('inventory-platform');

    repository.addBranch('main', true);
    repository.addBranch('feature/relational-schema');

    repository.addCommit(
        'a1b2c3d',
        'Create warehouse table',
        'main'
    );

    repository.addCommit(
        'b2c3d4e',
        'Create inventory foreign key relationship',
        'feature/relational-schema'
    );

    repository.registerReviewer('maya', ['database-reviewers']);
    repository.registerReviewer('rahul', ['application-reviewers']);

    repository.protectBranch('main', {
        requiredReviewCount: 1,
        requiredStatusChecks: ['sql-tests', 'integration-tests'],
        requireConversationResolution: true,
        allowDirectPush: false,
        allowForcePush: false,
        requireLinearHistory: true,
        allowedMergeStrategies: [MergeStrategy.SQUASH]
    });

    const pr = repository.createPullRequest({
        number: 101,
        sourceBranch: 'feature/relational-schema',
        targetBranch: 'main',
        title: 'Add relational inventory schema',
        author: 'atul'
    });

    repository.addComment(101, {
        reviewer: 'maya',
        path: 'schema.sql',
        line: 32,
        body: 'The inventory table should reference warehouse with a foreign key.',
        resolved: true
    });

    repository.addReview(101, {
        reviewer: 'maya',
        state: ReviewState.APPROVED,
        commitSha: 'b2c3d4e'
    });

    repository.setStatus(101, 'sql-tests', true);
    repository.setStatus(101, 'integration-tests', true);

    const evaluation = repository.evaluateMerge(101);

    console.log('Merge evaluation:');
    console.log(JSON.stringify(evaluation, null, 2));

    if (evaluation.eligible) {
        console.log('\nMerge result:');
        console.log(JSON.stringify(repository.merge(101, 'atul'), null, 2));
    }

    console.log('\nFinal repository state:');
    console.log(
        JSON.stringify(
            {
                name: repository.name,
                branches: Object.fromEntries(repository.branches),
                pullRequests: Object.fromEntries(repository.pullRequests)
            },
            null,
            2
        )
    );
}

if (require.main === module) {
    try {
        main();
    } catch (error) {
        console.error(`${error.name}: ${error.message}`);
        process.exitCode = 1;
    }
}
