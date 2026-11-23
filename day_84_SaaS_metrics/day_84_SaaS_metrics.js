'use strict';

/**
 * SaaS Metrics and Revenue Operations Engine
 *
 * Node.js 18+
 *
 * Features:
 * - Event-driven subscription lifecycle
 * - MRR movement classification
 * - NRR and GRR evaluation
 * - Logo and revenue churn
 * - CAC and CAC payback
 * - Asynchronous metric processing
 * - Policy-based metric validation
 * - Immutable period snapshots
 * - Revenue reconciliation
 */

const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');

const round = (value, places = 2) => {
    const factor = 10 ** places;
    return Math.round((value + Number.EPSILON) * factor) / factor;
};

function requireFiniteNonNegative(value, field) {
    if (
        typeof value !== 'number' ||
        !Number.isFinite(value) ||
        value < 0
    ) {
        throw new RangeError(
            `${field} must be a finite non-negative number`
        );
    }
}

function validatePeriod(period) {
    if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(period)) {
        throw new TypeError('Period must use YYYY-MM format');
    }
}

class DomainError extends Error {
    constructor(message) {
        super(message);
        this.name = 'DomainError';
    }
}

class Subscription {
    constructor({
        customerId,
        customerName,
        monthlyRevenue,
        segment = 'SMB',
        status = 'active'
    }) {
        if (!customerId || !customerId.trim()) {
            throw new DomainError('Customer ID is required');
        }

        requireFiniteNonNegative(monthlyRevenue, 'MRR');

        if (!['active', 'churned'].includes(status)) {
            throw new DomainError('Invalid subscription status');
        }

        this.customerId = customerId;
        this.customerName = customerName;
        this.monthlyRevenue = monthlyRevenue;
        this.segment = segment;
        this.status = status;

        Object.freeze(this);
    }
}

class RevenueLedger extends EventEmitter {
    #periods = new Map();

    record(period, movement) {
        validatePeriod(period);

        const {
            customerId,
            startingMRR,
            endingMRR
        } = movement;

        if (!customerId || !customerId.trim()) {
            throw new DomainError('Customer ID is required');
        }

        requireFiniteNonNegative(startingMRR, 'Starting MRR');
        requireFiniteNonNegative(endingMRR, 'Ending MRR');

        if (!this.#periods.has(period)) {
            this.#periods.set(period, new Map());
        }

        const customers = this.#periods.get(period);

        if (customers.has(customerId)) {
            throw new DomainError(
                `Duplicate movement for ${customerId}`
            );
        }

        const classification = this.#classify(
            startingMRR,
            endingMRR
        );

        const record = Object.freeze({
            customerId,
            startingMRR,
            endingMRR,
            ...classification
        });

        customers.set(customerId, record);

        this.emit('movement:recorded', {
            period,
            customerId,
            classification
        });

        return record;
    }

    #classify(start, end) {
        if (start === 0 && end > 0) {
            return {
                type: 'new',
                newMRR: end,
                expansionMRR: 0,
                contractionMRR: 0,
                churnedMRR: 0
            };
        }

        if (start > 0 && end === 0) {
            return {
                type: 'churn',
                newMRR: 0,
                expansionMRR: 0,
                contractionMRR: 0,
                churnedMRR: start
            };
        }

        if (end > start) {
            return {
                type: 'expansion',
                newMRR: 0,
                expansionMRR: end - start,
                contractionMRR: 0,
                churnedMRR: 0
            };
        }

        if (end < start) {
            return {
                type: 'contraction',
                newMRR: 0,
                expansionMRR: 0,
                contractionMRR: start - end,
                churnedMRR: 0
            };
        }

        return {
            type: 'unchanged',
            newMRR: 0,
            expansionMRR: 0,
            contractionMRR: 0,
            churnedMRR: 0
        };
    }

    snapshot(period) {
        validatePeriod(period);

        const customers = this.#periods.get(period);

        if (!customers || customers.size === 0) {
            throw new DomainError(
                `No movements for ${period}`
            );
        }

        const result = {
            period,
            startingMRR: 0,
            endingMRR: 0,
            newMRR: 0,
            expansionMRR: 0,
            contractionMRR: 0,
            churnedMRR: 0,
            startingCustomers: 0,
            endingCustomers: 0,
            churnedCustomers: 0,
            newCustomers: 0
        };

        for (const item of customers.values()) {
            result.startingMRR += item.startingMRR;
            result.endingMRR += item.endingMRR;
            result.newMRR += item.newMRR;
            result.expansionMRR += item.expansionMRR;
            result.contractionMRR += item.contractionMRR;
            result.churnedMRR += item.churnedMRR;

            if (item.startingMRR > 0) {
                result.startingCustomers++;

                if (item.endingMRR === 0) {
                    result.churnedCustomers++;
                }
            }

            if (item.endingMRR > 0) {
                result.endingCustomers++;
            }

            if (item.type === 'new') {
                result.newCustomers++;
            }
        }

        const expectedEndingMRR =
            result.startingMRR +
            result.newMRR +
            result.expansionMRR -
            result.contractionMRR -
            result.churnedMRR;

        if (
            Math.abs(
                expectedEndingMRR - result.endingMRR
            ) > 0.000001
        ) {
            throw new DomainError(
                'MRR reconciliation failed'
            );
        }

        return Object.freeze(result);
    }
}

class MetricPolicy {
    static retention(snapshot) {
        const {
            startingMRR,
            expansionMRR,
            contractionMRR,
            churnedMRR
        } = snapshot;

        if (startingMRR <= 0) {
            return {
                nrr: null,
                grr: null,
                reason: 'No opening revenue baseline'
            };
        }

        const grossRetained =
            startingMRR - churnedMRR - contractionMRR;

        const netRetained =
            grossRetained + expansionMRR;

        if (grossRetained < -0.000001) {
            throw new DomainError(
                'Invalid gross revenue retention'
            );
        }

        return {
            grr: round(
                grossRetained / startingMRR * 100
            ),
            nrr: round(
                netRetained / startingMRR * 100
            )
        };
    }

    static churn(snapshot) {
        return {
            logoChurnRate:
                snapshot.startingCustomers === 0
                    ? null
                    : round(
                        snapshot.churnedCustomers /
                        snapshot.startingCustomers * 100
                    ),

            revenueChurnRate:
                snapshot.startingMRR === 0
                    ? null
                    : round(
                        (
                            snapshot.churnedMRR +
                            snapshot.contractionMRR
                        ) /
                        snapshot.startingMRR * 100
                    )
        };
    }

    static expansion(snapshot) {
        return snapshot.startingMRR === 0
            ? null
            : round(
                snapshot.expansionMRR /
                snapshot.startingMRR * 100
            );
    }

    static growth(snapshot) {
        return snapshot.startingMRR === 0
            ? null
            : round(
                (
                    snapshot.endingMRR -
                    snapshot.startingMRR
                ) /
                snapshot.startingMRR * 100
            );
    }

    static cac(cost, customers) {
        requireFiniteNonNegative(cost, 'Acquisition cost');

        if (!Number.isInteger(customers) || customers <= 0) {
            throw new DomainError(
                'New customer count must be a positive integer'
            );
        }

        return cost / customers;
    }

    static payback(cac, monthlyMRR, grossMargin) {
        requireFiniteNonNegative(cac, 'CAC');
        requireFiniteNonNegative(monthlyMRR, 'MRR');

        if (
            !Number.isFinite(grossMargin) ||
            grossMargin <= 0 ||
            grossMargin > 100
        ) {
            throw new DomainError(
                'Gross margin must be greater than 0 and at most 100'
            );
        }

        if (monthlyMRR === 0) {
            throw new DomainError(
                'Payback cannot be calculated with zero MRR'
            );
        }

        return cac / (monthlyMRR * grossMargin / 100);
    }
}

class AnalyticsService {
    constructor(ledger) {
        this.ledger = ledger;
    }

    async generate(period) {
        // Yield to the event loop before processing the snapshot.
        await new Promise(resolve => setImmediate(resolve));

        const snapshot = this.ledger.snapshot(period);

        return Object.freeze({
            ...snapshot,
            retention: MetricPolicy.retention(snapshot),
            churn: MetricPolicy.churn(snapshot),
            expansionRate: MetricPolicy.expansion(snapshot),
            mrrGrowthRate: MetricPolicy.growth(snapshot)
        });
    }
}

class CohortAnalyzer {
    static analyze(cohorts) {
        const results = new Map();

        for (const [cohort, periods] of Object.entries(cohorts)) {
            const baseline = periods.M0;

            requireFiniteNonNegative(
                baseline,
                `${cohort} baseline`
            );

            if (baseline === 0) {
                throw new DomainError(
                    `Zero baseline in cohort ${cohort}`
                );
            }

            const retention = new Map();

            for (const [period, revenue] of Object.entries(periods)) {
                requireFiniteNonNegative(revenue, 'Cohort revenue');

                retention.set(
                    period,
                    round(revenue / baseline * 100)
                );
            }

            results.set(cohort, retention);
        }

        return results;
    }
}

async function main() {
    const ledger = new RevenueLedger();

    ledger.on('movement:recorded', event => {
        console.log(
            `[EVENT] ${event.customerId}: ${event.classification.type}`
        );
    });

    const records = [
        ['C001', 1000, 1200],
        ['C002', 2000, 1500],
        ['C003', 1500, 0],
        ['C004', 500, 500],
        ['C005', 0, 1000],
        ['C006', 0, 800]
    ];

    for (const [customerId, startingMRR, endingMRR] of records) {
        ledger.record('2026-10', {
            customerId,
            startingMRR,
            endingMRR
        });
    }

    const service = new AnalyticsService(ledger);
    const report = await service.generate('2026-10');

    console.log('\nMONTHLY SAAS METRICS');
    console.table({
        'Starting MRR': report.startingMRR,
        'Ending MRR': report.endingMRR,
        'New MRR': report.newMRR,
        'Expansion MRR': report.expansionMRR,
        'Contraction MRR': report.contractionMRR,
        'Churned MRR': report.churnedMRR,
        'NRR (%)': report.retention.nrr,
        'GRR (%)': report.retention.grr,
        'Logo churn (%)': report.churn.logoChurnRate,
        'Revenue churn (%)': report.churn.revenueChurnRate
    });

    const cac = MetricPolicy.cac(12000, 2);
    const payback = MetricPolicy.payback(cac, 900, 80);

    console.log('\nACQUISITION ECONOMICS');
    console.log({
        cac: round(cac),
        paybackMonths: round(payback, 2)
    });

    const cohorts = CohortAnalyzer.analyze({
        '2026-Q3': {
            M0: 10000,
            M1: 9800,
            M2: 10500,
            M3: 11000
        },
        '2026-Q4': {
            M0: 15000,
            M1: 14200
        }
    });

    console.log('\nCOHORT RETENTION');
    for (const [cohort, periods] of cohorts) {
        console.log(cohort, Object.fromEntries(periods));
    }

    // Domain-level failure checks.
    assert.throws(
        () => MetricPolicy.cac(1000, 0),
        DomainError
    );

    assert.throws(
        () => MetricPolicy.payback(5000, 1000, 0),
        DomainError
    );

    assert.throws(
        () => ledger.record('2026-10', {
            customerId: 'C001',
            startingMRR: 100,
            endingMRR: 200
        }),
        DomainError
    );

    console.log('\nAll validation checks passed.');
}

main().catch(error => {
    console.error('Analytics execution failed:', error.message);
    process.exitCode = 1;
});
