'use strict';

const { EventEmitter } = require('node:events');
const fs = require('node:fs/promises');

const Severity = Object.freeze({
  INFO: 'info',
  MINOR: 'minor',
  MAJOR: 'major',
  CRITICAL: 'critical'
});

const IssueType = Object.freeze({
  UI: 'ui',
  USABILITY: 'usability',
  ACCESSIBILITY: 'accessibility',
  INTERACTION: 'interaction',
  INFORMATION_ARCHITECTURE: 'information_architecture'
});

class UXError extends Error {
  constructor(message) {
    super(message);
    this.name = 'UXError';
  }
}

class UXEventBus extends EventEmitter {
  publish(eventName, payload) {
    this.emit(eventName, Object.freeze({
      timestamp: new Date().toISOString(),
      ...payload
    }));
  }
}

class UXScreen {
  constructor({
    id,
    title,
    navigation,
    primaryAction,
    controls,
    labels,
    focusOrder,
    contrast,
    contentSections
  }) {
    if (!id || !title) {
      throw new UXError('Screen id and title are required.');
    }

    if (!Array.isArray(controls) || controls.length === 0) {
      throw new UXError(`Screen ${id} requires interactive controls.`);
    }

    if (!Array.isArray(focusOrder)) {
      throw new UXError(`Screen ${id} requires a focus order.`);
    }

    this.id = id;
    this.title = title;
    this.navigation = [...navigation];
    this.primaryAction = primaryAction;
    this.controls = [...controls];
    this.labels = { ...labels };
    this.focusOrder = [...focusOrder];
    this.contrast = { ...contrast };
    this.contentSections = [...contentSections];
  }
}

class UXPolicyEngine {
  constructor() {
    this.rules = [
      this.navigationRule.bind(this),
      this.accessibleNameRule.bind(this),
      this.keyboardFocusRule.bind(this),
      this.contrastRule.bind(this),
      this.headingRule.bind(this),
      this.primaryActionRule.bind(this)
    ];
  }

  evaluate(screen) {
    return this.rules.flatMap(rule => rule(screen));
  }

  issue(type, severity, screen, description, recommendation) {
    return {
      id: `${type}-${screen.id}-${Math.random().toString(36).slice(2, 8)}`,
      type,
      severity,
      screen: screen.id,
      description,
      recommendation
    };
  }

  navigationRule(screen) {
    if (screen.navigation.length <= 7) {
      return [];
    }

    return [
      this.issue(
        IssueType.INFORMATION_ARCHITECTURE,
        Severity.MINOR,
        screen,
        'Primary navigation contains more than seven top-level destinations.',
        'Group related destinations and reduce top-level navigation choices.'
      )
    ];
  }

  accessibleNameRule(screen) {
    return screen.controls
      .filter(control => !String(screen.labels[control] || '').trim())
      .map(control =>
        this.issue(
          IssueType.ACCESSIBILITY,
          Severity.MAJOR,
          screen,
          `Control "${control}" has no accessible name.`,
          'Provide a visible label or equivalent programmatic accessible name.'
        )
      );
  }

  keyboardFocusRule(screen) {
    const focusSet = new Set(screen.focusOrder);

    return screen.controls
      .filter(control => !focusSet.has(control))
      .map(control =>
        this.issue(
          IssueType.ACCESSIBILITY,
          Severity.CRITICAL,
          screen,
          `Control "${control}" is absent from keyboard focus order.`,
          'Make the control keyboard reachable in a logical sequence.'
        )
      );
  }

  contrastRule(screen) {
    return Object.entries(screen.contrast)
      .filter(([, ratio]) => ratio < 4.5)
      .map(([token, ratio]) =>
        this.issue(
          IssueType.ACCESSIBILITY,
          Severity.MAJOR,
          screen,
          `Contrast token "${token}" has ratio ${ratio}:1.`,
          'Use a color combination meeting the applicable contrast requirement.'
        )
      );
  }

  headingRule(screen) {
    if (screen.contentSections.length === 0) {
      return [
        this.issue(
          IssueType.USABILITY,
          Severity.MAJOR,
          screen,
          'The screen contains no defined content sections.',
          'Use meaningful headings and grouping to establish information hierarchy.'
        )
      ];
    }

    return [];
  }

  primaryActionRule(screen) {
    if (!screen.primaryAction || !screen.controls.includes(screen.primaryAction)) {
      return [
        this.issue(
          IssueType.INTERACTION,
          Severity.MAJOR,
          screen,
          'Primary action is not represented by an interactive control.',
          'Expose the primary task as a clear, actionable control.'
        )
      ];
    }

    return [];
  }
}

class UsabilitySession {
  constructor(user) {
    this.user = Object.freeze({ ...user });
    this.tasks = [];
  }

  recordTask(task) {
    if (!task.name || !Number.isFinite(task.durationMs)) {
      throw new UXError('Task name and numeric duration are required.');
    }

    if (task.durationMs < 0 || task.steps <= 0 || task.errors < 0) {
      throw new UXError('Invalid usability-task measurements.');
    }

    if (task.errors > task.steps) {
      throw new UXError('Task errors cannot exceed task steps.');
    }

    this.tasks.push({
      name: task.name,
      completed: Boolean(task.completed),
      durationMs: task.durationMs,
      steps: task.steps,
      errors: task.errors,
      notes: [...(task.notes || [])]
    });
  }

  metrics() {
    if (this.tasks.length === 0) {
      return {
        completionRate: 0,
        averageDurationMs: 0,
        errorRate: 0
      };
    }

    const completed = this.tasks.filter(task => task.completed).length;
    const totalDuration = this.tasks.reduce(
      (sum, task) => sum + task.durationMs,
      0
    );
    const totalSteps = this.tasks.reduce(
      (sum, task) => sum + task.steps,
      0
    );
    const totalErrors = this.tasks.reduce(
      (sum, task) => sum + task.errors,
      0
    );

    return {
      completionRate: completed / this.tasks.length,
      averageDurationMs: totalDuration / this.tasks.length,
      errorRate: totalErrors / Math.max(totalSteps, 1)
    };
  }
}

class UXWorkbench {
  constructor() {
    this.screens = new Map();
    this.issues = [];
    this.events = new UXEventBus();
    this.policyEngine = new UXPolicyEngine();

    this.events.on('screen:evaluated', event => {
      console.log(
        `[${event.timestamp}] Evaluated ${event.screenId}: ${event.issueCount} issue(s)`
      );
    });
  }

  addScreen(screen) {
    if (this.screens.has(screen.id)) {
      throw new UXError(`Duplicate screen id: ${screen.id}`);
    }

    this.screens.set(screen.id, screen);
    this.events.publish('screen:added', { screenId: screen.id });
  }

  evaluate() {
    this.issues = [];

    for (const screen of this.screens.values()) {
      const screenIssues = this.policyEngine.evaluate(screen);
      this.issues.push(...screenIssues);

      this.events.publish('screen:evaluated', {
        screenId: screen.id,
        issueCount: screenIssues.length
      });
    }

    return [...this.issues];
  }

  report() {
    const bySeverity = Object.groupBy(
      this.issues,
      issue => issue.severity
    );

    return {
      generatedAt: new Date().toISOString(),
      screens: [...this.screens.values()].map(screen => ({
        id: screen.id,
        title: screen.title
      })),
      issueCounts: {
        critical: (bySeverity.critical || []).length,
        major: (bySeverity.major || []).length,
        minor: (bySeverity.minor || []).length,
        info: (bySeverity.info || []).length
      },
      issues: this.issues
    };
  }
}

function buildDemoWorkbench() {
  const workbench = new UXWorkbench();

  workbench.addScreen(
    new UXScreen({
      id: 'dashboard',
      title: 'Project Dashboard',
      navigation: [
        'Projects',
        'Reports',
        'Teams',
        'Activity',
        'Integrations',
        'Billing',
        'Settings',
        'Help'
      ],
      primaryAction: 'Create project',
      controls: [
        'Search',
        'Create project',
        'Open project',
        'Account menu'
      ],
      labels: {
        Search: 'Search projects',
        'Create project': 'Create project',
        'Open project': 'Open project',
        'Account menu': 'Account menu'
      },
      focusOrder: [
        'Search',
        'Create project',
        'Open project',
        'Account menu'
      ],
      contrast: {
        bodyText: 7.2,
        mutedText: 3.3,
        primaryButton: 4.8
      },
      contentSections: ['Projects', 'Recent activity']
    })
  );

  workbench.addScreen(
    new UXScreen({
      id: 'settings',
      title: 'Settings',
      navigation: ['Projects', 'Settings'],
      primaryAction: 'Save settings',
      controls: [
        'Name field',
        'Save settings',
        'Delete account'
      ],
      labels: {
        'Name field': 'Account name',
        'Save settings': 'Save settings'
      },
      focusOrder: [
        'Name field',
        'Save settings',
        'Delete account'
      ],
      contrast: {
        bodyText: 8.0,
        primaryButton: 5.0
      },
      contentSections: ['Profile', 'Security', 'Account']
    })
  );

  return workbench;
}

async function main() {
  const workbench = buildDemoWorkbench();

  const issues = workbench.evaluate();
  const report = workbench.report();

  const session = new UsabilitySession({
    id: 'participant-07',
    keyboardOnly: true,
    reducedMotion: true,
    screenReader: false
  });

  session.recordTask({
    name: 'Find project',
    completed: true,
    durationMs: 18300,
    steps: 5,
    errors: 0
  });

  session.recordTask({
    name: 'Create project',
    completed: true,
    durationMs: 31900,
    steps: 7,
    errors: 1,
    notes: ['Primary action was easy to discover.']
  });

  session.recordTask({
    name: 'Change settings',
    completed: false,
    durationMs: 44700,
    steps: 8,
    errors: 3,
    notes: ['Account-level action required confirmation.']
  });

  const metrics = session.metrics();

  console.log('\n=== UX POLICY REPORT ===');
  console.log(JSON.stringify(report.issueCounts, null, 2));

  console.log('\n=== USABILITY METRICS ===');
  console.log({
    completionRatePercent: Number((metrics.completionRate * 100).toFixed(2)),
    averageDurationSeconds: Number((metrics.averageDurationMs / 1000).toFixed(2)),
    errorRatePercent: Number((metrics.errorRate * 100).toFixed(2))
  });

  console.log('\n=== PRIORITY ISSUES ===');
  for (const issue of issues.filter(
    item => item.severity === Severity.CRITICAL || item.severity === Severity.MAJOR
  )) {
    console.log(
      `[${issue.severity.toUpperCase()}] ${issue.screen}: ${issue.description}`
    );
  }

  const output = {
    report,
    usability: {
      participant: session.user,
      tasks: session.tasks,
      metrics
    }
  };

  await fs.writeFile(
    'ux_policy_report.json',
    JSON.stringify(output, null, 2),
    'utf8'
  );

  console.log('\nReport written to ux_policy_report.json');
}

main().catch(error => {
  console.error(`UX evaluation failed: ${error.message}`);
  process.exitCode = 1;
});
