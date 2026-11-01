'use strict';

/*
 * Product Vision Model
 *
 * The implementation uses an event-driven workflow:
 * draft -> validated -> approved -> active -> retired
 *
 * Product vision, customer value, future state, and strategic direction
 * remain separate domain concepts so that a feature list cannot silently
 * become the product strategy.
 */

const VisionStatus = Object.freeze({
  DRAFT: 'draft',
  VALIDATED: 'validated',
  APPROVED: 'approved',
  ACTIVE: 'active',
  RETIRED: 'retired'
});

const Horizon = Object.freeze({
  NOW: '0-12 months',
  NEXT: '1-3 years',
  FUTURE: '3-5 years'
});

class VisionError extends Error {
  constructor(message) {
    super(message);
    this.name = 'VisionError';
  }
}

class Vision {
  constructor({
    product,
    statement,
    customerValue,
    futureState,
    strategicDirection,
    horizon,
    evidence
  }) {
    this.product = product;
    this.statement = statement;
    this.customerValue = customerValue;
    this.futureState = futureState;
    this.strategicDirection = [...strategicDirection];
    this.horizon = horizon;
    this.evidence = [...evidence];
    this.status = VisionStatus.DRAFT;
  }

  validate() {
    const errors = [];

    if (!this.product?.trim()) {
      errors.push('Product name is required.');
    }

    if (!this.statement || this.statement.trim().length < 30) {
      errors.push('Vision statement must contain at least 30 characters.');
    }

    if (!this.customerValue?.trim()) {
      errors.push('Customer value is required.');
    }

    if (!this.futureState?.trim()) {
      errors.push('Future state is required.');
    }

    if (!Array.isArray(this.strategicDirection) ||
        this.strategicDirection.length === 0) {
      errors.push('At least one strategic direction is required.');
    }

    if (!Array.isArray(this.evidence) || this.evidence.length === 0) {
      errors.push('Evidence is required.');
    }

    const implementationWords = [
      'button',
      'database table',
      'screen',
      'api endpoint'
    ];

    const lower = this.statement.toLowerCase();

    if (implementationWords.some(word => lower.includes(word))) {
      errors.push(
        'The vision describes implementation details instead of a customer outcome.'
      );
    }

    if (!Object.values(Horizon).includes(this.horizon)) {
      errors.push('Invalid planning horizon.');
    }

    return errors;
  }
}

class VisionStore {
  constructor() {
    this.items = new Map();
  }

  save(vision) {
    const errors = vision.validate();

    if (errors.length > 0) {
      throw new VisionError(errors.join(' '));
    }

    this.items.set(vision.product, vision);
  }

  get(product) {
    const vision = this.items.get(product);

    if (!vision) {
      throw new VisionError(`Vision not found: ${product}`);
    }

    return vision;
  }
}

class VisionWorkflow {
  constructor(store) {
    this.store = store;
    this.listeners = new Map();
  }

  on(eventName, listener) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }

    this.listeners.get(eventName).add(listener);
  }

  emit(eventName, payload) {
    const listeners = this.listeners.get(eventName) || new Set();

    for (const listener of listeners) {
      listener(payload);
    }
  }

  transition(product, expectedStatus, nextStatus) {
    const vision = this.store.get(product);

    if (vision.status !== expectedStatus) {
      throw new VisionError(
        `Invalid transition from ${vision.status} to ${nextStatus}.`
      );
    }

    vision.status = nextStatus;
    this.emit('statusChanged', {
      product,
      previousStatus: expectedStatus,
      nextStatus
    });

    return vision;
  }

  validate(product) {
    const vision = this.store.get(product);
    const errors = vision.validate();

    if (errors.length > 0) {
      throw new VisionError(errors.join(' '));
    }

    this.transition(
      product,
      VisionStatus.DRAFT,
      VisionStatus.VALIDATED
    );
  }

  approve(product) {
    const vision = this.store.get(product);

    if (vision.status !== VisionStatus.VALIDATED) {
      throw new VisionError('Only validated visions can be approved.');
    }

    this.transition(
      product,
      VisionStatus.VALIDATED,
      VisionStatus.APPROVED
    );
  }

  activate(product) {
    this.transition(
      product,
      VisionStatus.APPROVED,
      VisionStatus.ACTIVE
    );
  }

  retire(product) {
    this.transition(
      product,
      VisionStatus.ACTIVE,
      VisionStatus.RETIRED
    );
  }
}

class StrategyEvaluator {
  static score(vision, priorities, customerNeeds) {
    const prioritySet = new Set(
      [...priorities].map(item => item.toLowerCase())
    );

    const directionMatches = vision.strategicDirection.filter(
      direction => prioritySet.has(direction.toLowerCase())
    ).length;

    const strategyScore =
      directionMatches / Math.max(prioritySet.size, 1);

    const customerTerms = new Set();

    for (const segment of customerNeeds) {
      for (const term of [...segment.needs, ...segment.painPoints]) {
        customerTerms.add(term.toLowerCase());
      }
    }

    const valueWords = vision.customerValue
      .toLowerCase()
      .split(/\s+/)
      .map(word => word.replace(/[.,:;()]/g, ''))
      .filter(word => word.length > 3);

    const matches = valueWords.filter(
      word => customerTerms.has(word)
    ).length;

    const customerScore = matches / Math.max(valueWords.length, 1);

    return Math.round(
      (strategyScore * 0.6 + customerScore * 0.4) * 10000
    ) / 100;
  }
}

async function simulateWorkflow() {
  const store = new VisionStore();
  const workflow = new VisionWorkflow(store);

  workflow.on('statusChanged', event => {
    console.log(
      `[EVENT] ${event.product}: ` +
      `${event.previousStatus} -> ${event.nextStatus}`
    );
  });

  const vision = new Vision({
    product: 'Operations Intelligence Platform',
    statement:
      'Enable operations teams to make faster, more reliable decisions from a unified understanding of operational conditions.',
    customerValue:
      'Customers gain visibility, reduce decision delays, and improve operational reliability.',
    futureState:
      'Operations become measurable and predictable, allowing teams to identify problems early and coordinate action.',
    strategicDirection: [
      'customer trust',
      'operational efficiency',
      'data-driven decisions',
      'scalable growth'
    ],
    horizon: Horizon.NEXT,
    evidence: [
      'Customer interviews identify fragmented operational information.',
      'Pilot users report delays caused by manual consolidation.',
      'Managers require consistent operational indicators.'
    ]
  });

  store.save(vision);

  workflow.validate(vision.product);
  workflow.approve(vision.product);
  workflow.activate(vision.product);

  const customerSegments = [
    {
      name: 'Operations teams',
      needs: ['visibility', 'speed', 'reliability'],
      painPoints: ['manual work', 'decision delays']
    },
    {
      name: 'Managers',
      needs: ['control', 'insight', 'predictability'],
      painPoints: ['unclear priorities', 'slow reporting']
    }
  ];

  const priorities = new Set([
    'customer trust',
    'operational efficiency',
    'data-driven decisions',
    'scalable growth'
  ]);

  const score = StrategyEvaluator.score(
    vision,
    priorities,
    customerSegments
  );

  console.log('\nPRODUCT VISION');
  console.log('='.repeat(70));
  console.log(`Product: ${vision.product}`);
  console.log(`Status: ${vision.status}`);
  console.log(`Horizon: ${vision.horizon}`);
  console.log(`Vision: ${vision.statement}`);
  console.log(`Customer value: ${vision.customerValue}`);
  console.log(`Future state: ${vision.futureState}`);
  console.log(`Strategic alignment: ${score}%`);

  // The workflow is asynchronous at the application boundary so that
  // persistence or event publishing can later be replaced without changing
  // the domain model.
  await Promise.resolve();

  try {
    workflow.activate('Missing Product');
  } catch (error) {
    if (!(error instanceof VisionError)) {
      throw error;
    }

    console.log(`Expected failure: ${error.message}`);
  }

  const invalid = new Vision({
    product: 'Invalid',
    statement: 'Add a button and database table.',
    customerValue: '',
    futureState: '',
    strategicDirection: [],
    horizon: Horizon.NOW,
    evidence: []
  });

  const validationErrors = invalid.validate();
  console.log(`Validation errors detected: ${validationErrors.length}`);

  if (validationErrors.length === 0) {
    throw new Error('Invalid vision unexpectedly passed validation.');
  }
}

simulateWorkflow().catch(error => {
  console.error(`Workflow failed: ${error.message}`);
  process.exitCode = 1;
});
