'use strict';

/*
 * Product Strategy Policy Simulator
 *
 * Scenario:
 * A software product uses Pull Requests as the controlled delivery workflow.
 * Product strategy defines desired outcomes and strategic choices.
 * Reviews provide human evaluation.
 * Approvals are commit-specific decisions.
 * Branch protection enforces repository-level merge conditions.
 */

const EventEmitter = require('node:events');

const ProductStage = Object.freeze({
  DISCOVERY: 'discovery',
  VALIDATION: 'validation',
  DELIVERY: 'delivery',
  SCALE: 'scale'
});

const PRState = Object.freeze({
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

class ValidationError extends Error {}

class ProductGoal {
  constructor(name, metric, target, current) {
    if (!name || !metric) {
      throw new ValidationError('Goal name and metric are required.');
    }
    if (!Number.isFinite(target) || target <= 0) {
      throw new ValidationError('Goal target must be positive.');
    }
    if (!Number.isFinite(current) || current < 0) {
      throw new ValidationError('Goal current value must be non-negative.');
    }

    this.name = name;
    this.metric = metric;
    this.target = target;
    this.current = current;
  }

  achieved() {
    return this.current >= this.target;
  }
}

class ProductStrategy {
  constructor({ vision, mission, strategicChoices, goals }) {
    if (!vision || !mission) {
      throw new ValidationError('Vision and mission are required.');
    }

    this.vision = vision;
    this.mission = mission;
    this.strategicChoices = [...strategicChoices];
    this.goals = [...goals];
  }

  score() {
    if (this.goals.length === 0) return 0;

    const total = this.goals.reduce(
      (sum, goal) => sum + Math.min(goal.current / goal.target, 1),
      0
    );

    return total / this.goals.length;
  }
}

class Review {
  constructor({ reviewer, state, commitSha }) {
    if (!reviewer || !commitSha) {
      throw new ValidationError('Reviewer and commit SHA are required.');
    }

    this.reviewer = reviewer;
    this.state = state;
    this.commitSha = commitSha;
    this.createdAt = new Date();
  }
}

class PullRequest {
  constructor({
    number,
    title,
    author,
    sourceBranch,
    targetBranch,
    draft = false
  }) {
    if (!Number.isInteger(number) || number <= 0) {
      throw new ValidationError('Pull Request number must be positive.');
    }

    this.number = number;
    this.title = title;
    this.author = author;
    this.sourceBranch = sourceBranch;
    this.targetBranch = targetBranch;
    this.draft = draft;
    this.state = draft ? PRState.DRAFT : PRState.OPEN;
    this.commits = [];
    this.reviews = [];
    this.statusChecks = new Map();
    this.openConversations = new Set();
    this.mergeStrategy = 'squash';
  }

  addCommit(sha, message) {
    if (!/^[a-f0-9]{8,64}$/i.test(sha)) {
      throw new ValidationError('Invalid commit SHA.');
    }
    if (!message.trim()) {
      throw new ValidationError('Commit message cannot be empty.');
    }

    this.commits.push({
      sha,
      message,
      createdAt: new Date()
    });
  }

  addReview(review) {
    if (this.state === PRState.MERGED || this.state === PRState.CLOSED) {
      throw new ValidationError('Closed or merged PRs cannot receive active reviews.');
    }

    this.reviews.push(review);
  }

  setStatus(name, passed) {
    if (!name.trim()) {
      throw new ValidationError('Status check name is required.');
    }

    this.statusChecks.set(name, Boolean(passed));
  }

  openConversation(id) {
    this.openConversations.add(id);
  }

  resolveConversation(id) {
    this.openConversations.delete(id);
  }

  synchronizeBase() {
    if (this.commits.length === 0) {
      throw new ValidationError('Cannot synchronize a PR without commits.');
    }

    this.baseSynchronizedAt = new Date();
    this.baseSynchronized = true;
  }

  get headSha() {
    if (this.commits.length === 0) {
      throw new ValidationError('PR has no commits.');
    }
    return this.commits[this.commits.length - 1].sha;
  }
}

class BranchProtection {
  constructor({
    branch,
    requiredApprovals,
    requiredChecks,
    requireConversationsResolved = true,
    allowDirectPush = false,
    allowForcePush = false,
    allowDeletion = false,
    requireLinearHistory = false
  }) {
    this.branch = branch;
    this.requiredApprovals = requiredApprovals;
    this.requiredChecks = new Set(requiredChecks);
    this.requireConversationsResolved = requireConversationsResolved;
    this.allowDirectPush = allowDirectPush;
    this.allowForcePush = allowForcePush;
    this.allowDeletion = allowDeletion;
    this.requireLinearHistory = requireLinearHistory;
  }
}

class Repository extends EventEmitter {
  constructor(name) {
    super();

    if (!name.trim()) {
      throw new ValidationError('Repository name is required.');
    }

    this.name = name;
    this.branches = new Set();
    this.pullRequests = new Map();
    this.protections = new Map();
  }

  addBranch(name) {
    this.branches.add(name);
  }

  protectBranch(policy) {
    if (!this.branches.has(policy.branch)) {
      throw new ValidationError('Protected branch must exist.');
    }
    this.protections.set(policy.branch, policy);
  }

  addPullRequest(pr) {
    if (this.pullRequests.has(pr.number)) {
      throw new ValidationError(`PR #${pr.number} already exists.`);
    }

    if (!this.branches.has(pr.targetBranch)) {
      throw new ValidationError('Target branch does not exist.');
    }

    this.pullRequests.set(pr.number, pr);
    this.emit('pull-request-created', pr);
  }
}

class PolicyEngine {
  constructor(repository) {
    this.repository = repository;
  }

  evaluate(pr) {
    const reasons = [];
    const policy = this.repository.protections.get(pr.targetBranch);

    if (!policy) {
      reasons.push('Target branch has no protection policy.');
      return { eligible: false, reasons };
    }

    if (pr.state !== PRState.OPEN) {
      reasons.push(`PR state is ${pr.state}.`);
    }

    if (pr.draft) {
      reasons.push('Draft PR cannot be merged.');
    }

    if (pr.commits.length === 0) {
      reasons.push('PR contains no commits.');
    }

    let currentApprovals = new Set();
    let changesRequested = new Set();

    if (pr.commits.length > 0) {
      const head = pr.headSha;

      for (const review of pr.reviews) {
        if (review.state === ReviewState.APPROVED &&
            review.commitSha === head) {
          currentApprovals.add(review.reviewer);
        }

        if (review.state === ReviewState.CHANGES_REQUESTED) {
          changesRequested.add(review.reviewer);
        }
      }
    }

    if (changesRequested.size > 0) {
      reasons.push(
        `Requested changes: ${[...changesRequested].sort().join(', ')}.`
      );
    }

    if (currentApprovals.size < policy.requiredApprovals) {
      reasons.push(
        `${currentApprovals.size} current approval(s); ` +
        `${policy.requiredApprovals} required.`
      );
    }

    const failedChecks = [...policy.requiredChecks].filter(
      check => pr.statusChecks.get(check) !== true
    );

    if (failedChecks.length > 0) {
      reasons.push(
        `Required checks not passing: ${failedChecks.sort().join(', ')}.`
      );
    }

    if (
      policy.requireConversationsResolved &&
      pr.openConversations.size > 0
    ) {
      reasons.push(
        `${pr.openConversations.size} conversation(s) remain unresolved.`
      );
    }

    return {
      eligible: reasons.length === 0,
      reasons
    };
  }

  merge(prNumber) {
    const pr = this.repository.pullRequests.get(prNumber);

    if (!pr) {
      throw new ValidationError(`PR #${prNumber} does not exist.`);
    }

    const result = this.evaluate(pr);

    if (!result.eligible) {
      return {
        merged: false,
        reasons: result.reasons
      };
    }

    pr.state = PRState.MERGED;
    this.repository.emit('pull-request-merged', pr);

    return {
      merged: true,
      strategy: pr.mergeStrategy
    };
  }
}

function buildStrategy() {
  return new ProductStrategy({
    vision:
      'Make repository change management predictable, reviewable, and safe.',
    mission:
      'Connect product intent with controlled engineering delivery.',
    strategicChoices: [
      'Use Pull Requests as the controlled change-entry mechanism.',
      'Keep review decisions separate from enforcement policy.',
      'Tie approvals to the exact reviewed commit.',
      'Use automated checks as objective merge evidence.',
      'Protect production branches from uncontrolled writes.'
    ],
    goals: [
      new ProductGoal(
        'review_coverage',
        'production PRs reviewed',
        95,
        92
      ),
      new ProductGoal(
        'policy_compliant_merges',
        'merges satisfying policy',
        90,
        94
      )
    ]
  });
}

function main() {
  const strategy = buildStrategy();

  console.log('PRODUCT STRATEGY');
  console.log('Vision:', strategy.vision);
  console.log('Mission:', strategy.mission);
  console.log('Strategy score:', `${(strategy.score() * 100).toFixed(1)}%`);

  const repository = new Repository('payment-platform');

  repository.on('pull-request-created', pr => {
    console.log(`Event: PR #${pr.number} created`);
  });

  repository.on('pull-request-merged', pr => {
    console.log(`Event: PR #${pr.number} merged`);
  });

  repository.addBranch('main');
  repository.addBranch('feature/product-strategy');

  repository.protectBranch(
    new BranchProtection({
      branch: 'main',
      requiredApprovals: 2,
      requiredChecks: [
        'unit-tests',
        'security-scan',
        'product-policy'
      ],
      requireConversationsResolved: true,
      allowDirectPush: false,
      allowForcePush: false,
      allowDeletion: false,
      requireLinearHistory: true
    })
  );

  const pr = new PullRequest({
    number: 142,
    title: 'Introduce product strategy governance metrics',
    author: 'atul',
    sourceBranch: 'feature/product-strategy',
    targetBranch: 'main'
  });

  pr.addCommit('a1b2c3d4', 'Implement product strategy model');
  pr.addCommit('e5f6a7b8', 'Address review findings');

  pr.addReview(
    new Review({
      reviewer: 'maya',
      state: ReviewState.APPROVED,
      commitSha: 'e5f6a7b8'
    })
  );

  pr.addReview(
    new Review({
      reviewer: 'rohan',
      state: ReviewState.APPROVED,
      commitSha: 'e5f6a7b8'
    })
  );

  pr.setStatus('unit-tests', true);
  pr.setStatus('security-scan', true);
  pr.setStatus('product-policy', true);

  repository.addPullRequest(pr);

  const engine = new PolicyEngine(repository);

  console.log('\nMERGE EVALUATION');
  console.log(engine.evaluate(pr));

  console.log('\nMERGE RESULT');
  console.log(engine.merge(142));

  const staleApproval = new PullRequest({
    number: 143,
    title: 'Change governance policy',
    author: 'atul',
    sourceBranch: 'feature/product-strategy',
    targetBranch: 'main'
  });

  staleApproval.addCommit('11111111', 'Initial change');
  staleApproval.addCommit('22222222', 'Modify change after review');

  staleApproval.addReview(
    new Review({
      reviewer: 'maya',
      state: ReviewState.APPROVED,
      commitSha: '11111111'
    })
  );

  staleApproval.addReview(
    new Review({
      reviewer: 'rohan',
      state: ReviewState.APPROVED,
      commitSha: '11111111'
    })
  );

  staleApproval.setStatus('unit-tests', true);
  staleApproval.setStatus('security-scan', true);
  staleApproval.setStatus('product-policy', true);

  repository.addPullRequest(staleApproval);

  console.log('\nSTALE APPROVAL EVALUATION');
  console.log(engine.evaluate(staleApproval));

  const unresolvedConversation = new PullRequest({
    number: 144,
    title: 'Update strategic control',
    author: 'atul',
    sourceBranch: 'feature/product-strategy',
    targetBranch: 'main'
  });

  unresolvedConversation.addCommit('33333333', 'Update strategic control');

  unresolvedConversation.addReview(
    new Review({
      reviewer: 'maya',
      state: ReviewState.APPROVED,
      commitSha: '33333333'
    })
  );

  unresolvedConversation.addReview(
    new Review({
      reviewer: 'rohan',
      state: ReviewState.APPROVED,
      commitSha: '33333333'
    })
  );

  unresolvedConversation.setStatus('unit-tests', true);
  unresolvedConversation.setStatus('security-scan', true);
  unresolvedConversation.setStatus('product-policy', true);
  unresolvedConversation.openConversation('comment-17');

  repository.addPullRequest(unresolvedConversation);

  console.log('\nUNRESOLVED CONVERSATION EVALUATION');
  console.log(engine.evaluate(unresolvedConversation));
}

main();
