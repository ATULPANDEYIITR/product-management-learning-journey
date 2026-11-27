'use strict';

/*
 * A/B Testing Engine
 *
 * Node.js 18+
 * Standard-library implementation.
 *
 * Features:
 * - Event-driven experiment lifecycle
 * - Deterministic participant assignment
 * - Control and treatment groups
 * - Exposure tracking
 * - Conversion measurement
 * - Statistical significance
 * - Confidence intervals
 * - Sample-size planning
 * - Guardrail evaluation
 * - JSON reporting
 */

const crypto = require('node:crypto');
const fs = require('node:fs/promises');
const EventEmitter = require('node:events');

const ExperimentState = Object.freeze({
    DRAFT: 'draft',
    RUNNING: 'running',
    COMPLETED: 'completed',
    STOPPED: 'stopped'
});

const Group = Object.freeze({
    CONTROL: 'control',
    TREATMENT: 'treatment'
});

const Decision = Object.freeze({
    INCONCLUSIVE: 'inconclusive',
    TREATMENT_WINS: 'treatment_wins',
    CONTROL_WINS: 'control_wins',
    SIGNIFICANT_NO_PRACTICAL_WIN: 'significant_no_practical_win'
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class ExperimentError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ExperimentError';
    }
}

function validateProbability(value, name) {
    if (
        typeof value !== 'number' ||
        !Number.isFinite(value) ||
        value <= 0 ||
        value >= 1
    ) {
        throw new ValidationError(
            `${name} must be between zero and one.`
        );
    }
}

function normalCDF(x) {
    // Numerical approximation of the standard normal CDF.
    const t = 1 / (1 + 0.2316419 * Math.abs(x));

    const density =
        0.3989422804014327 * Math.exp(-0.5 * x * x);

    const polynomial =
        t * (
            0.319381530 +
            t * (
                -0.356563782 +
                t * (
                    1.781477937 +
                    t * (
                        -1.821255978 +
                        t * 1.330274429
                    )
                )
            )
        );

    const positive = 1 - density * polynomial;

    return x >= 0 ? positive : 1 - positive;
}

function inverseNormal(p) {
    if (!(p > 0 && p < 1)) {
        throw new ValidationError('Invalid normal probability.');
    }

    let low = -8;
    let high = 8;

    for (let i = 0; i < 100; i++) {
        const mid = (low + high) / 2;

        if (normalCDF(mid) < p) {
            low = mid;
        } else {
            high = mid;
        }
    }

    return (low + high) / 2;
}

function calculateStatistics(control, treatment, alpha = 0.05) {
    if (
        !control ||
        !treatment ||
        control.total <= 0 ||
        treatment.total <= 0
    ) {
        throw new ValidationError(
            'Both groups require observations.'
        );
    }

    if (
        control.conversions < 0 ||
        control.conversions > control.total ||
        treatment.conversions < 0 ||
        treatment.conversions > treatment.total
    ) {
        throw new ValidationError('Invalid conversion counts.');
    }

    validateProbability(alpha, 'Significance level');

    const p1 = control.conversions / control.total;
    const p2 = treatment.conversions / treatment.total;

    const pooled =
        (control.conversions + treatment.conversions) /
        (control.total + treatment.total);

    const standardError = Math.sqrt(
        pooled * (1 - pooled) *
        (1 / control.total + 1 / treatment.total)
    );

    const z = standardError === 0
        ? 0
        : (p2 - p1) / standardError;

    const pValue = standardError === 0
        ? 1
        : 2 * (1 - normalCDF(Math.abs(z)));

    const difference = p2 - p1;

    const unpooledSE = Math.sqrt(
        p1 * (1 - p1) / control.total +
        p2 * (1 - p2) / treatment.total
    );

    const critical = inverseNormal(1 - alpha / 2);

    return Object.freeze({
        controlRate: p1,
        treatmentRate: p2,
        absoluteLift: difference,
        relativeLift: p1 === 0 ? null : difference / p1,
        zScore: z,
        pValue,
        confidenceInterval: Object.freeze([
            difference - critical * unpooledSE,
            difference + critical * unpooledSE
        ]),
        significant: pValue < alpha
    });
}

function calculateRequiredSampleSize(
    baseline,
    absoluteEffect,
    alpha = 0.05,
    power = 0.80
) {
    validateProbability(baseline, 'Baseline rate');

    if (
        !Number.isFinite(absoluteEffect) ||
        absoluteEffect <= 0 ||
        baseline + absoluteEffect >= 1
    ) {
        throw new ValidationError('Invalid minimum detectable effect.');
    }

    validateProbability(alpha, 'Significance level');
    validateProbability(power, 'Statistical power');

    const treatment = baseline + absoluteEffect;
    const average = (baseline + treatment) / 2;

    const za = inverseNormal(1 - alpha / 2);
    const zb = inverseNormal(power);

    const numerator = Math.pow(
        za * Math.sqrt(2 * average * (1 - average)) +
        zb * Math.sqrt(
            baseline * (1 - baseline) +
            treatment * (1 - treatment)
        ),
        2
    );

    return Math.ceil(
        numerator / Math.pow(absoluteEffect, 2)
    );
}

class Experiment extends EventEmitter {
    #config;
    #state = ExperimentState.DRAFT;
    #assignments = new Map();
    #observations = new Map();
    #salt;
    #startedAt = null;
    #endedAt = null;

    constructor(config) {
        super();

        if (!config || typeof config.name !== 'string' ||
            !config.name.trim()) {
            throw new ValidationError('Experiment name is required.');
        }

        validateProbability(
            config.allocationRatio ?? 0.5,
            'Allocation ratio'
        );

        validateProbability(
            config.controlRate,
            'Control conversion rate'
        );

        validateProbability(
            config.treatmentRate,
            'Treatment conversion rate'
        );

        validateProbability(
            config.alpha ?? 0.05,
            'Significance level'
        );

        this.#config = Object.freeze({
            name: config.name.trim(),
            allocationRatio: config.allocationRatio ?? 0.5,
            controlRate: config.controlRate,
            treatmentRate: config.treatmentRate,
            alpha: config.alpha ?? 0.05,
            minimumEffect: config.minimumEffect ?? 0.01
        });

        this.#salt = config.assignmentSalt ??
            crypto.randomBytes(32).toString('hex');
    }

    get state() {
        return this.#state;
    }

    get participantCount() {
        return this.#assignments.size;
    }

    start() {
        if (this.#state !== ExperimentState.DRAFT) {
            throw new ExperimentError('Invalid start transition.');
        }

        this.#state = ExperimentState.RUNNING;
        this.#startedAt = new Date().toISOString();

        this.emit('started', {
            name: this.#config.name,
            timestamp: this.#startedAt
        });
    }

    #bucket(participantId) {
        // Stable hashing keeps assignment consistent across requests.
        const digest = crypto
            .createHmac('sha256', this.#salt)
            .update(participantId)
            .digest();

        return digest.readUInt32BE(0) / 0x100000000;
    }

    assign(participantId) {
        if (this.#state !== ExperimentState.RUNNING) {
            throw new ExperimentError('Experiment is not running.');
        }

        if (
            typeof participantId !== 'string' ||
            !participantId.trim()
        ) {
            throw new ValidationError('Participant ID is required.');
        }

        const id = participantId.trim();

        if (this.#assignments.has(id)) {
            throw new ExperimentError('Duplicate assignment.');
        }

        const bucket = this.#bucket(id);

        const group = bucket < this.#config.allocationRatio
            ? Group.CONTROL
            : Group.TREATMENT;

        const assignment = Object.freeze({
            participantId: id,
            group,
            assignedAt: new Date().toISOString()
        });

        this.#assignments.set(id, assignment);

        this.emit('assigned', assignment);

        return assignment;
    }

    recordOutcome(participantId, outcome) {
        if (this.#state !== ExperimentState.RUNNING) {
            throw new ExperimentError('Experiment is not running.');
        }

        if (!this.#assignments.has(participantId)) {
            throw new ExperimentError('Participant is not assigned.');
        }

        if (this.#observations.has(participantId)) {
            throw new ExperimentError('Outcome already recorded.');
        }

        if (typeof outcome.converted !== 'boolean') {
            throw new ValidationError(
                'Conversion outcome must be boolean.'
            );
        }

        const record = Object.freeze({
            participantId,
            converted: outcome.converted,
            latencyMs: outcome.latencyMs ?? null,
            recordedAt: new Date().toISOString()
        });

        if (
            record.latencyMs !== null &&
            (
                !Number.isFinite(record.latencyMs) ||
                record.latencyMs < 0
            )
        ) {
            throw new ValidationError('Invalid latency measurement.');
        }

        this.#observations.set(participantId, record);

        this.emit('outcome', record);
    }

    getGroupMetrics() {
        const metrics = {
            control: {
                total: 0,
                conversions: 0,
                latencyTotal: 0,
                latencyCount: 0
            },
            treatment: {
                total: 0,
                conversions: 0,
                latencyTotal: 0,
                latencyCount: 0
            }
        };

        for (const [id, outcome] of this.#observations) {
            const group = this.#assignments.get(id).group;
            const metric = metrics[group];

            metric.total++;

            if (outcome.converted) {
                metric.conversions++;
            }

            if (outcome.latencyMs !== null) {
                metric.latencyTotal += outcome.latencyMs;
                metric.latencyCount++;
            }
        }

        return Object.fromEntries(
            Object.entries(metrics).map(([name, metric]) => [
                name,
                Object.freeze({
                    ...metric,
                    conversionRate: metric.total
                        ? metric.conversions / metric.total
                        : null,
                    averageLatency: metric.latencyCount
                        ? metric.latencyTotal / metric.latencyCount
                        : null
                })
            ])
        );
    }

    evaluate() {
        const metrics = this.getGroupMetrics();

        if (!metrics.control.total || !metrics.treatment.total) {
            throw new ExperimentError(
                'Both groups require recorded outcomes.'
            );
        }

        const result = calculateStatistics(
            metrics.control,
            metrics.treatment,
            this.#config.alpha
        );

        const practical =
            result.absoluteLift >= this.#config.minimumEffect;

        let decision = Decision.INCONCLUSIVE;

        if (result.significant) {
            if (result.absoluteLift > 0 && practical) {
                decision = Decision.TREATMENT_WINS;
            } else if (result.absoluteLift < 0) {
                decision = Decision.CONTROL_WINS;
            } else {
                decision = Decision.SIGNIFICANT_NO_PRACTICAL_WIN;
            }
        }

        const report = Object.freeze({
            experiment: this.#config.name,
            state: this.#state,
            assignedParticipants: this.#assignments.size,
            observedParticipants: this.#observations.size,
            metrics,
            statisticalResults: result,
            practicallySignificant: practical,
            decision,
            generatedAt: new Date().toISOString()
        });

        this.emit('evaluated', report);

        return report;
    }

    complete() {
        if (this.#state !== ExperimentState.RUNNING) {
            throw new ExperimentError('Invalid completion transition.');
        }

        this.#state = ExperimentState.COMPLETED;
        this.#endedAt = new Date().toISOString();

        this.emit('completed', {
            name: this.#config.name,
            timestamp: this.#endedAt
        });
    }

    stop(reason = 'Manual stop') {
        if (this.#state !== ExperimentState.RUNNING) {
            throw new ExperimentError('Invalid stop transition.');
        }

        this.#state = ExperimentState.STOPPED;
        this.#endedAt = new Date().toISOString();

        this.emit('stopped', {
            reason,
            timestamp: this.#endedAt
        });
    }

    async exportReport(filename) {
        const report = this.evaluate();

        // Exclusive creation avoids accidentally overwriting an existing report.
        await fs.writeFile(
            filename,
            JSON.stringify(report, null, 2),
            {
                encoding: 'utf8',
                flag: 'wx',
                mode: 0o600
            }
        );

        return filename;
    }
}

async function runDemo() {
    const experiment = new Experiment({
        name: 'E-commerce Checkout Optimization',
        controlRate: 0.10,
        treatmentRate: 0.12,
        allocationRatio: 0.5,
        alpha: 0.05,
        minimumEffect: 0.01,
        assignmentSalt: 'reproducible-demo-secret'
    });

    experiment.on('started', event => {
        process.stdout.write(`Started: ${event.name}\n`);
    });

    experiment.on('assigned', event => {
        if (event.participantId === 'user-1') {
            process.stdout.write(
                `First assignment: ${event.group}\n`
            );
        }
    });

    experiment.on('completed', event => {
        process.stdout.write(`Completed: ${event.name}\n`);
    });

    experiment.start();

    let randomState = 42;

    function random() {
        randomState = (
            Math.imul(randomState, 1664525) + 1013904223
        ) >>> 0;

        return randomState / 4294967296;
    }

    for (let i = 0; i < 20000; i++) {
        const id = `user-${i + 1}`;
        const assignment = experiment.assign(id);

        const rate = assignment.group === Group.CONTROL
            ? 0.10
            : 0.12;

        experiment.recordOutcome(id, {
            converted: random() < rate,
            latencyMs: 150 + random() * 100
        });
    }

    experiment.complete();

    const report = experiment.evaluate();

    console.log('\nEXPERIMENT RESULTS');
    console.log(JSON.stringify(report, null, 2));

    console.log('\nSAMPLE SIZE PLANNING');
    console.log(
        'Required per group:',
        calculateRequiredSampleSize(0.10, 0.02)
    );

    try {
        await experiment.exportReport('ab_test_report.json');
        console.log('Report saved.');
    } catch (error) {
        if (error.code === 'EEXIST') {
            console.log('Report already exists; not overwritten.');
        } else {
            throw error;
        }
    }
}

function runTests() {
    const equal = calculateStatistics(
        { total: 1000, conversions: 100 },
        { total: 1000, conversions: 100 }
    );

    if (equal.pValue !== 1) {
        throw new Error('Equal groups test failed.');
    }

    const sample = calculateRequiredSampleSize(0.10, 0.02);

    if (sample <= 0) {
        throw new Error('Sample size calculation failed.');
    }

    const experiment = new Experiment({
        name: 'Validation Experiment',
        controlRate: 0.10,
        treatmentRate: 0.12,
        assignmentSalt: 'test-salt'
    });

    experiment.start();

    const first = experiment.assign('participant-1');
    const second = experiment.assign('participant-2');

    if (!Object.values(Group).includes(first.group) ||
        !Object.values(Group).includes(second.group)) {
        throw new Error('Invalid group assignment.');
    }

    try {
        experiment.assign('participant-1');
        throw new Error('Duplicate assignment was accepted.');
    } catch (error) {
        if (!(error instanceof ExperimentError)) {
            throw error;
        }
    }

    console.log('All JavaScript tests passed.');
}

if (require.main === module) {
    runTests();

    runDemo().catch(error => {
        console.error('Experiment failure:', error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    Experiment,
    ExperimentState,
    Group,
    Decision,
    calculateStatistics,
    calculateRequiredSampleSize
};
