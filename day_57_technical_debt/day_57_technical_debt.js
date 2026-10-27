'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');
const { EventEmitter } = require('node:events');

const DebtCategory = Object.freeze({
  CODE: 'code',
  TEST: 'test',
  ARCHITECTURE: 'architecture',
  SECURITY: 'security',
  INFRASTRUCTURE: 'infrastructure',
  DOCUMENTATION: 'documentation'
});

const DebtStatus = Object.freeze({
  OPEN: 'open',
  PLANNED: 'planned',
  IN_PROGRESS: 'in_progress',
  RESOLVED: 'resolved',
  ACCEPTED: 'accepted'
});

const ReviewState = Object.freeze({
  PENDING: 'pending',
  APPROVED: 'approved',
  CHANGES_REQUESTED: 'changes_requested',
  COMMENTED: 'commented',
  DISMISSED: 'dismissed'
});

class ValidationError extends Error {}

class TechnicalDebtItem {
  constructor({
    id,
    title,
    category,
    owner,
    principalHours,
    remediationHours,
    monthlyInterestHours,
    impact,
    probability,
    urgency,
    securityExposure,
    affectedComponents = [],
    status = DebtStatus.OPEN
  }) {
    this.id = id;
    this.title = title;
    this.category = category;
    this.owner = owner;
    this.principalHours = principalHours;
    this.remediationHours = remediationHours;
    this.monthlyInterestHours = monthlyInterestHours;
    this.impact = impact;
    this.probability = probability;
    this.urgency = urgency;
    this.securityExposure = securityExposure;
    this.affectedComponents = new Set(affectedComponents);
    this.status = status;
    this.validate();
  }

  validate() {
    if (!Number.isInteger(this.id) || this.id <= 0) {
      throw new ValidationError('Debt ID must be a positive integer.');
    }
    if (!this.title?.trim() || !this.owner?.trim()) {
      throw new ValidationError('Debt title and owner are required.');
    }
    if (!Object.values(DebtCategory).includes(this.category)) {
      throw new ValidationError('Unknown technical debt category.');
    }
    if (this.principalHours <= 0 || this.remediationHours <= 0) {
      throw new ValidationError('Debt estimates must be positive.');
    }
    if (this.monthlyInterestHours < 0) {
      throw new ValidationError('Monthly interest cannot be negative.');
    }
    if (this.impact < 1 || this.impact > 10) {
      throw new ValidationError('Impact must be 1..10.');
    }
    if (this.probability < 0 || this.probability > 1) {
      throw new ValidationError('Probability must be 0..1.');
    }
    if (this.urgency < 1 || this.urgency > 10) {
      throw new ValidationError('Urgency must be 1..10.');
    }
    if (this.securityExposure < 0 || this.securityExposure > 10) {
      throw new ValidationError('Security exposure must be 0..10.');
    }
  }

  get riskScore() {
    return this.impact * this.probability * 10
      + this.urgency * 2
      + this.securityExposure * 3;
  }

  get priorityScore() {
    return (
      (this.monthlyInterestHours * 4
        + this.riskScore * 2
        + this.securityExposure * 5)
      / Math.max(this.remediationHours, 1)
    );
  }

  get priority() {
    if (this.priorityScore >= 70) return 'critical';
    if (this.priorityScore >= 40) return 'high';
    if (this.priorityScore >= 20) return 'medium';
    return 'low';
  }
}

class Review {
  constructor(reviewer, state, comments = []) {
    if (!reviewer?.trim()) {
      throw new ValidationError('Reviewer identity is required.');
    }
    if (!Object.values(ReviewState).includes(state)) {
      throw new ValidationError('Invalid review state.');
    }
    this.reviewer = reviewer;
    this.state = state;
    this.comments = [...comments];
    this.submittedAt = new Date();
  }
}

class PullRequest extends EventEmitter {
  constructor({
    number,
    title,
    author,
    sourceBranch,
    targetBranch,
    draft = false,
    technicalDebtIds = []
  }) {
    super();
    if (!title?.trim() || !author?.trim()) {
      throw new ValidationError('Pull Request title and author are required.');
    }
    if (sourceBranch === targetBranch) {
      throw new ValidationError('Source and target branches must differ.');
    }

    this.number = number;
    this.title = title;
    this.author = author;
    this.sourceBranch = sourceBranch;
    this.targetBranch = targetBranch;
    this.draft = draft;
    this.open = true;
    this.synchronized = true;
    this.conflicted = false;
    this.reviews = [];
    this.statusChecks = new Map();
    this.technicalDebtIds = new Set(technicalDebtIds);
    this.unresolvedConversations = 0;
  }

  addReview(review) {
    if (!this.open) {
      throw new ValidationError('Closed Pull Requests cannot receive reviews.');
    }
    this.reviews.push(review);
    this.emit('review', { pullRequest: this, review });
  }

  setStatus(name, passed, required = true) {
    this.statusChecks.set(name, { passed, required });
    this.emit('status', { pullRequest: this, name, passed, required });
  }

  approvalCount() {
    return this.reviews.filter(
      review => review.state === ReviewState.APPROVED
    ).length;
  }

  hasChangeRequest() {
    return this.reviews.some(
      review => review.state === ReviewState.CHANGES_REQUESTED
    );
  }

  requiredChecksPassed() {
    return [...this.statusChecks.values()]
      .filter(check => check.required)
      .every(check => check.passed);
  }
}

class BranchProtectionPolicy {
  constructor({
    branch,
    requiredReviews,
    requiredStatusChecks,
    requireConversationResolution,
    restrictDirectPush,
    restrictForcePush,
    restrictDeletion,
    requireLinearHistory,
    allowAdminBypass,
    maxDebtScore
  }) {
    Object.assign(this, {
      branch,
      requiredReviews,
      requiredStatusChecks: new Set(requiredStatusChecks),
      requireConversationResolution,
      restrictDirectPush,
      restrictForcePush,
      restrictDeletion,
      requireLinearHistory,
      allowAdminBypass,
      maxDebtScore
    });
  }
}

class Repository extends EventEmitter {
  constructor(name) {
    super();
    if (!name?.trim()) throw new ValidationError('Repository name is required.');
    this.name = name;
    this.branches = new Set();
    this.debt = new Map();
    this.pullRequests = new Map();
    this.protection = new Map();
    this.nextDebtId = 1;
    this.nextPrNumber = 1;
  }

  createBranch(name) {
    if (!name?.trim() || this.branches.has(name)) {
      throw new ValidationError(`Invalid or duplicate branch: ${name}`);
    }
    this.branches.add(name);
  }

  addDebt(input) {
    if (input.id !== this.nextDebtId) {
      throw new ValidationError('Debt IDs must be sequential.');
    }
    const item = new TechnicalDebtItem(input);
    this.debt.set(item.id, item);
    this.nextDebtId += 1;
    this.emit('debtAdded', item);
    return item;
  }

  createPullRequest(input) {
    if (!this.branches.has(input.sourceBranch)
      || !this.branches.has(input.targetBranch)) {
      throw new ValidationError('Pull Request references an unknown branch.');
    }

    for (const id of input.technicalDebtIds ?? []) {
      if (!this.debt.has(id)) {
        throw new ValidationError(`Unknown technical debt ID: ${id}`);
      }
    }

    const pr = new PullRequest({
      ...input,
      number: this.nextPrNumber
    });
    this.pullRequests.set(pr.number, pr);
    this.nextPrNumber += 1;

    pr.on('review', event => this.emit('reviewAdded', event));
    pr.on('status', event => this.emit('statusChanged', event));
    this.emit('pullRequestCreated', pr);

    return pr;
  }

  setProtection(policy) {
    if (!this.branches.has(policy.branch)) {
      throw new ValidationError('Protected branch does not exist.');
    }
    this.protection.set(policy.branch, policy);
  }

  debtScoreForPullRequest(pr) {
    return [...pr.technicalDebtIds]
      .map(id => this.debt.get(id))
      .filter(Boolean)
      .reduce((sum, item) => sum + item.priorityScore, 0);
  }

  evaluateMerge(pr, { unresolvedConversations = pr.unresolvedConversations } = {}) {
    const reasons = [];

    if (!pr.open) reasons.push('Pull Request is closed.');
    if (pr.draft) reasons.push('Draft Pull Request cannot be merged.');
    if (pr.conflicted) reasons.push('Merge conflicts are unresolved.');
    if (!pr.synchronized) reasons.push('Base branch synchronization is stale.');

    const policy = this.protection.get(pr.targetBranch);
    if (!policy) return { eligible: reasons.length === 0, reasons };

    if (pr.approvalCount() < policy.requiredReviews) {
      reasons.push(
        `Required approvals: ${pr.approvalCount()}/${policy.requiredReviews}.`
      );
    }

    if (pr.hasChangeRequest()) {
      reasons.push('A reviewer has requested changes.');
    }

    if (!pr.requiredChecksPassed()) {
      reasons.push('A required status check has failed.');
    }

    for (const required of policy.requiredStatusChecks) {
      const check = pr.statusChecks.get(required);
      if (!check?.passed) {
        reasons.push(`Required check failed or missing: ${required}.`);
      }
    }

    if (policy.requireConversationResolution && unresolvedConversations > 0) {
      reasons.push('Review conversations remain unresolved.');
    }

    const debtScore = this.debtScoreForPullRequest(pr);
    if (debtScore > policy.maxDebtScore) {
      reasons.push(
        `Technical debt score ${debtScore.toFixed(2)} exceeds `
        + `limit ${policy.maxDebtScore.toFixed(2)}.`
      );
    }

    return { eligible: reasons.length === 0, reasons };
  }

  prioritizeDebt() {
    return [...this.debt.values()]
      .filter(item => ![DebtStatus.RESOLVED, DebtStatus.ACCEPTED].includes(item.status))
      .sort((a, b) => b.priorityScore - a.priorityScore);
  }

  allocateCapacity(capacityHours, featureHours, debtRatio) {
    if (capacityHours <= 0) throw new ValidationError('Capacity must be positive.');
    if (featureHours < 0) throw new ValidationError('Feature effort cannot be negative.');
    if (debtRatio < 0 || debtRatio > 1) {
      throw new ValidationError('Debt ratio must be 0..1.');
    }

    const debtBudget = capacityHours * debtRatio;
    let remaining = debtBudget;
    const selected = [];

    for (const item of this.prioritizeDebt()) {
      if (item.remediationHours <= remaining) {
        selected.push(item.id);
        remaining -= item.remediationHours;
      }
    }

    return {
      capacityHours,
      featureBudget: capacityHours - debtBudget,
      requestedFeatureHours: featureHours,
      featureGap: Math.max(featureHours - (capacityHours - debtBudget), 0),
      debtBudget,
      selectedDebtIds: selected,
      unusedDebtBudget: remaining
    };
  }
}

async function writeReport(repository, filename) {
  const ranking = repository.prioritizeDebt().map(item => ({
    id: item.id,
    title: item.title,
    category: item.category,
    priority: item.priority,
    priorityScore: Number(item.priorityScore.toFixed(2)),
    monthlyInterestHours: item.monthlyInterestHours
  }));

  const report = {
    repository: repository.name,
    generatedAt: new Date().toISOString(),
    technicalDebt: ranking
  };

  await fs.writeFile(filename, JSON.stringify(report, null, 2), 'utf8');
}

async function main() {
  const repository = new Repository('order-platform');

  repository.on('debtAdded', item => {
    console.log(`Debt recorded: #${item.id} ${item.title}`);
  });

  repository.on('pullRequestCreated', pr => {
    console.log(`Pull Request created: #${pr.number} ${pr.title}`);
  });

  for (const branch of ['main', 'develop', 'feature/order-validation']) {
    repository.createBranch(branch);
  }

  repository.addDebt({
    id: 1,
    title: 'Duplicated order validation',
    category: DebtCategory.CODE,
    owner: 'orders',
    principalHours: 10,
    remediationHours: 18,
    monthlyInterestHours: 7,
    impact: 8,
    probability: 0.8,
    urgency: 8,
    securityExposure: 4,
    affectedComponents: ['orders', 'checkout']
  });

  repository.addDebt({
    id: 2,
    title: 'Missing failure-path integration tests',
    category: DebtCategory.TEST,
    owner: 'quality',
    principalHours: 8,
    remediationHours: 14,
    monthlyInterestHours: 5,
    impact: 7,
    probability: 0.7,
    urgency: 7,
    securityExposure: 3,
    affectedComponents: ['payments']
  });

  repository.addDebt({
    id: 3,
    title: 'Static integration credential',
    category: DebtCategory.SECURITY,
    owner: 'security',
    principalHours: 3,
    remediationHours: 5,
    monthlyInterestHours: 2,
    impact: 10,
    probability: 0.5,
    urgency: 10,
    securityExposure: 10,
    affectedComponents: ['test-environment']
  });

  repository.setProtection(new BranchProtectionPolicy({
    branch: 'main',
    requiredReviews: 2,
    requiredStatusChecks: ['unit-tests', 'security-scan', 'integration-tests'],
    requireConversationResolution: true,
    restrictDirectPush: true,
    restrictForcePush: true,
    restrictDeletion: true,
    requireLinearHistory: true,
    allowAdminBypass: false,
    maxDebtScore: 80
  }));

  const pr = repository.createPullRequest({
    title: 'Refactor order validation',
    author: 'nina',
    sourceBranch: 'feature/order-validation',
    targetBranch: 'main',
    technicalDebtIds: [1, 2]
  });

  pr.setStatus('unit-tests', true);
  pr.setStatus('security-scan', true);
  pr.setStatus('integration-tests', false);

  pr.addReview(new Review('omar', ReviewState.APPROVED, [
    'Validation is easier to follow.'
  ]));

  pr.addReview(new Review('priya', ReviewState.CHANGES_REQUESTED, [
    'Add duplicate-order coverage.'
  ]));

  pr.unresolvedConversations = 1;

  const result = repository.evaluateMerge(pr);

  console.log('\nTechnical debt ranking');
  for (const item of repository.prioritizeDebt()) {
    console.log(
      `#${item.id} ${item.priority.padEnd(8)} `
      + `score=${item.priorityScore.toFixed(2).padStart(6)} `
      + `${item.title}`
    );
  }

  console.log('\nMerge evaluation');
  console.log(result.eligible ? 'ELIGIBLE' : 'BLOCKED');
  result.reasons.forEach(reason => console.log(`- ${reason}`));

  const allocation = repository.allocateCapacity(80, 58, 0.30);
  console.log('\nCapacity allocation');
  console.log(JSON.stringify(allocation, null, 2));

  const reportFile = path.join(process.cwd(), 'technical-debt-report.json');
  await writeReport(repository, reportFile);

  const saved = JSON.parse(await fs.readFile(reportFile, 'utf8'));
  if (saved.technicalDebt.length !== 3) {
    throw new Error('Report validation failed.');
  }

  await fs.unlink(reportFile);

  if (result.eligible) {
    throw new Error('The sample PR should remain blocked.');
  }

  console.log('\nValidation checks passed.');
}

main().catch(error => {
  console.error(`Execution failed: ${error.message}`);
  process.exitCode = 1;
});
