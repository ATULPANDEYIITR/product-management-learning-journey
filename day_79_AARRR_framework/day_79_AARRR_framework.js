"use strict";

/**
 * AARRR Growth Analytics and Experimentation Platform
 *
 * Node.js 18+
 * Standard library only.
 *
 * Engineering focus:
 * - Event-driven processing
 * - Asynchronous ingestion
 * - Idempotency
 * - Acquisition attribution
 * - Behavioral activation
 * - Retention measurement
 * - Revenue analysis
 * - Referral attribution
 * - Conversion experimentation
 * - Policy-based event validation
 */

const { EventEmitter } = require("node:events");
const { randomUUID } = require("node:crypto");
const fs = require("node:fs/promises");

const STAGES = Object.freeze({
    ACQUISITION: "acquisition",
    ACTIVATION: "activation",
    RETENTION: "retention",
    REVENUE: "revenue",
    REFERRAL: "referral"
});

const EVENT_TYPES = Object.freeze({
    VISIT: "visit",
    SIGNUP: "signup",
    ACTIVATION: "activation",
    LOGIN: "login",
    PURCHASE: "purchase",
    SUBSCRIPTION: "subscription",
    REFERRAL_SENT: "referral_sent",
    CANCELLATION: "cancellation"
});

class GrowthError extends Error {}
class ValidationError extends GrowthError {}
class DuplicateEventError extends GrowthError {}
class UnknownUserError extends GrowthError {}

class EventValidator {
    static validate(event) {
        if (!event || typeof event !== "object") {
            throw new ValidationError("Event must be an object.");
        }

        if (
            typeof event.eventId !== "string" ||
            event.eventId.length === 0 ||
            event.eventId.length > 100
        ) {
            throw new ValidationError("Invalid event ID.");
        }

        if (
            typeof event.userId !== "string" ||
            event.userId.length === 0 ||
            event.userId.length > 100
        ) {
            throw new ValidationError("Invalid user ID.");
        }

        if (!Object.values(EVENT_TYPES).includes(event.type)) {
            throw new ValidationError("Unsupported event type.");
        }

        if (
            !Number.isFinite(Date.parse(event.timestamp)) ||
            !event.timestamp.includes("T")
        ) {
            throw new ValidationError("Invalid event timestamp.");
        }

        if (
            event.properties === null ||
            typeof event.properties !== "object" ||
            Array.isArray(event.properties)
        ) {
            throw new ValidationError("Properties must be an object.");
        }

        if (JSON.stringify(event).length > 16_384) {
            throw new ValidationError("Event payload exceeds size limit.");
        }

        return true;
    }
}

class GrowthUser {
    constructor(userId, source, signupDate, referredBy = null) {
        this.userId = userId;
        this.source = source;
        this.signupDate = signupDate;
        this.referredBy = referredBy;
        this.activatedAt = null;
        this.lastActivity = null;
        this.activityDates = new Set();
        this.revenueCents = 0;
        this.transactions = 0;
        this.cancelled = false;
        this.referralsSent = 0;
    }

    get activated() {
        return this.activatedAt !== null;
    }

    get paying() {
        return this.revenueCents > 0;
    }
}

class GrowthPolicy {
    constructor({
        activationWindowDays = 7,
        maxEventAmountCents = 100_000_000,
        requireActivationBeforePurchase = true
    } = {}) {
        if (
            !Number.isInteger(activationWindowDays) ||
            activationWindowDays < 0
        ) {
            throw new ValidationError("Invalid activation window.");
        }

        this.activationWindowDays = activationWindowDays;
        this.maxEventAmountCents = maxEventAmountCents;
        this.requireActivationBeforePurchase =
            requireActivationBeforePurchase;
    }

    validateActivation(user, timestamp) {
        const elapsed =
            (timestamp - user.signupDate) / 86_400_000;

        if (
            elapsed < 0 ||
            elapsed > this.activationWindowDays
        ) {
            throw new ValidationError(
                "Activation is outside the permitted window."
            );
        }
    }

    validateAmount(amount) {
        if (
            !Number.isSafeInteger(amount) ||
            amount <= 0 ||
            amount > this.maxEventAmountCents
        ) {
            throw new ValidationError("Invalid transaction amount.");
        }
    }
}

class GrowthPlatform extends EventEmitter {
    constructor(policy = new GrowthPolicy()) {
        super();

        this.policy = policy;
        this.users = new Map();
        this.events = new Map();
        this.sources = new Map();
        this.dailyActivity = new Map();
        this.processingQueue = [];
        this.processing = false;
    }

    createEvent(userId, type, timestamp, properties = {}) {
        return {
            eventId: randomUUID(),
            userId,
            type,
            timestamp: timestamp.toISOString(),
            properties
        };
    }

    async ingest(event) {
        EventValidator.validate(event);

        if (this.events.has(event.eventId)) {
            throw new DuplicateEventError(
                `Event ${event.eventId} already exists.`
            );
        }

        // JavaScript's synchronous event-state transition is atomic
        // within one event-loop turn. External persistence needs a
        // database transaction and an idempotency constraint.
        const timestamp = new Date(event.timestamp);
        const user = this.users.get(event.userId);
        const p = event.properties;

        switch (event.type) {
            case EVENT_TYPES.VISIT: {
                const source = p.source || "direct";

                if (typeof source !== "string" || !source.trim()) {
                    throw new ValidationError("Invalid source.");
                }

                if (!this.sources.has(source)) {
                    this.sources.set(source, new Set());
                }

                this.sources.get(source).add(event.userId);
                break;
            }

            case EVENT_TYPES.SIGNUP: {
                if (user) {
                    throw new ValidationError("Duplicate signup.");
                }

                const source = p.source || "direct";

                if (typeof source !== "string" || !source.trim()) {
                    throw new ValidationError("Invalid source.");
                }

                const referredBy = p.referredBy || null;

                if (
                    referredBy &&
                    (referredBy === event.userId ||
                     !this.users.has(referredBy))
                ) {
                    throw new ValidationError("Invalid referrer.");
                }

                this.users.set(
                    event.userId,
                    new GrowthUser(
                        event.userId,
                        source,
                        timestamp,
                        referredBy
                    )
                );
                break;
            }

            default: {
                if (!user) {
                    throw new UnknownUserError(
                        "User must register first."
                    );
                }

                if (event.type === EVENT_TYPES.ACTIVATION) {
                    if (user.activated) {
                        throw new ValidationError(
                            "Duplicate activation."
                        );
                    }

                    this.policy.validateActivation(user, timestamp);
                    user.activatedAt = timestamp;
                }

                if (event.type === EVENT_TYPES.LOGIN) {
                    const day = timestamp.toISOString().slice(0, 10);

                    user.activityDates.add(day);
                    user.lastActivity = timestamp;

                    if (!this.dailyActivity.has(day)) {
                        this.dailyActivity.set(day, new Set());
                    }

                    this.dailyActivity.get(day).add(user.userId);
                }

                if (
                    event.type === EVENT_TYPES.PURCHASE ||
                    event.type === EVENT_TYPES.SUBSCRIPTION
                ) {
                    if (
                        this.policy.requireActivationBeforePurchase &&
                        !user.activated
                    ) {
                        throw new ValidationError(
                            "Activation required before purchase."
                        );
                    }

                    this.policy.validateAmount(p.amountCents);

                    user.revenueCents += p.amountCents;
                    user.transactions++;
                }

                if (event.type === EVENT_TYPES.REFERRAL_SENT) {
                    if (!user.activated) {
                        throw new ValidationError(
                            "Activation required before referral."
                        );
                    }

                    user.referralsSent++;
                }

                if (event.type === EVENT_TYPES.CANCELLATION) {
                    user.cancelled = true;
                }

                break;
            }
        }

        this.events.set(event.eventId, Object.freeze({
            ...event,
            properties: Object.freeze({ ...event.properties })
        }));

        this.emit("event", {
            id: event.eventId,
            type: event.type,
            userId: event.userId
        });

        return event.eventId;
    }

    async ingestBatch(events, concurrency = 4) {
        if (!Array.isArray(events)) {
            throw new ValidationError("Batch must be an array.");
        }

        if (
            !Number.isInteger(concurrency) ||
            concurrency < 1 ||
            concurrency > 16
        ) {
            throw new ValidationError("Invalid concurrency.");
        }

        // Parallel workers preserve throughput while each state
        // transition executes synchronously before its first await.
        let cursor = 0;
        const results = new Array(events.length);

        const workers = Array.from(
            { length: Math.min(concurrency, events.length) },
            async () => {
                while (true) {
                    const index = cursor++;

                    if (index >= events.length) return;

                    try {
                        results[index] = {
                            success: true,
                            eventId: await this.ingest(events[index])
                        };
                    } catch (error) {
                        results[index] = {
                            success: false,
                            error: error.message
                        };
                    }
                }
            }
        );

        await Promise.all(workers);
        return results;
    }

    acquisition() {
        const result = {};

        for (const [source, visitors] of this.sources) {
            const signups = [...this.users.values()].filter(
                user => user.source === source
            ).length;

            result[source] = {
                visitors: visitors.size,
                signups,
                conversionRate: visitors.size
                    ? Number((signups / visitors.size * 100).toFixed(2))
                    : 0
            };
        }

        return result;
    }

    activation() {
        const users = [...this.users.values()];
        const activated = users.filter(user => user.activated).length;

        return {
            registered: users.length,
            activated,
            conversionRate: users.length
                ? Number((activated / users.length * 100).toFixed(2))
                : 0
        };
    }

    retention(periodDays = 7) {
        if (!Number.isInteger(periodDays) || periodDays < 1) {
            throw new ValidationError("Invalid retention period.");
        }

        const cohorts = new Map();

        for (const user of this.users.values()) {
            const cohort = user.signupDate.toISOString().slice(0, 10);

            if (!cohorts.has(cohort)) cohorts.set(cohort, []);

            cohorts.get(cohort).push(user);
        }

        const output = {};

        for (const [cohort, members] of cohorts) {
            const retained = members.filter(user =>
                [...user.activityDates].some(day => {
                    const elapsed =
                        (Date.parse(day) - Date.parse(cohort)) /
                        86_400_000;

                    return elapsed >= 0 && elapsed <= periodDays;
                })
            ).length;

            output[cohort] = {
                cohortSize: members.length,
                retained,
                rate: Number(
                    (retained / members.length * 100).toFixed(2)
                )
            };
        }

        return output;
    }

    revenue() {
        const users = [...this.users.values()];
        const revenueCents = users.reduce(
            (sum, user) => sum + user.revenueCents,
            0
        );

        const paying = users.filter(user => user.paying);

        return {
            totalRevenue: revenueCents / 100,
            payingCustomers: paying.length,
            transactions: users.reduce(
                (sum, user) => sum + user.transactions,
                0
            ),
            arpu: users.length
                ? Number((revenueCents / 100 / users.length).toFixed(2))
                : 0,
            arppu: paying.length
                ? Number(
                    (revenueCents / 100 / paying.length).toFixed(2)
                )
                : 0
        };
    }

    referrals() {
        const referred = [...this.users.values()].filter(
            user => user.referredBy
        );

        const referrerCounts = new Map();

        for (const user of referred) {
            referrerCounts.set(
                user.referredBy,
                (referrerCounts.get(user.referredBy) || 0) + 1
            );
        }

        const activated = [...this.users.values()].filter(
            user => user.activated
        ).length;

        return {
            referredSignups: referred.length,
            uniqueReferrers: referrerCounts.size,
            viralCoefficient: activated
                ? Number((referred.length / activated).toFixed(3))
                : 0,
            referrerCounts: Object.fromEntries(referrerCounts)
        };
    }

    dailyActiveUsers() {
        return Object.fromEntries(
            [...this.dailyActivity.entries()]
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([day, users]) => [day, users.size])
        );
    }

    funnel() {
        return {
            acquisition: this.acquisition(),
            activation: this.activation(),
            retention: this.retention(),
            revenue: this.revenue(),
            referral: this.referrals(),
            dailyActiveUsers: this.dailyActiveUsers()
        };
    }

    async exportReport(filepath) {
        const data = JSON.stringify(this.funnel(), null, 2);

        // Restrict output permissions where supported by the platform.
        await fs.writeFile(filepath, data, {
            encoding: "utf8",
            mode: 0o600,
            flag: "wx"
        });
    }
}

class Experiment {
    static compare(control, treatment) {
        if (
            !Array.isArray(control) ||
            !Array.isArray(treatment) ||
            control.length === 0 ||
            treatment.length === 0
        ) {
            throw new ValidationError("Invalid experiment samples.");
        }

        for (const group of [control, treatment]) {
            if (!group.every(value => typeof value === "boolean")) {
                throw new ValidationError(
                    "Experiment outcomes must be boolean."
                );
            }
        }

        const c = control.filter(Boolean).length / control.length;
        const t = treatment.filter(Boolean).length / treatment.length;

        return {
            controlRate: Number((c * 100).toFixed(2)),
            treatmentRate: Number((t * 100).toFixed(2)),
            absoluteLift: Number(((t - c) * 100).toFixed(2)),
            relativeLift: c
                ? Number(((t / c - 1) * 100).toFixed(2))
                : null,
            significanceTested: false
        };
    }
}

async function main() {
    const platform = new GrowthPlatform();

    platform.on("event", event => {
        console.log(
            `Processed ${event.type} for ${event.userId}`
        );
    });

    const base = new Date("2026-10-01T10:00:00.000Z");

    const definitions = [
        ["u001", EVENT_TYPES.VISIT, 0, { source: "organic" }],
        ["u001", EVENT_TYPES.SIGNUP, 0, { source: "organic" }],
        ["u001", EVENT_TYPES.ACTIVATION, 1, {}],
        ["u001", EVENT_TYPES.LOGIN, 3, {}],
        ["u001", EVENT_TYPES.PURCHASE, 4, { amountCents: 4999 }],

        ["u002", EVENT_TYPES.VISIT, 0, { source: "paid" }],
        ["u002", EVENT_TYPES.SIGNUP, 0, { source: "paid" }],
        ["u002", EVENT_TYPES.ACTIVATION, 2, {}],
        ["u002", EVENT_TYPES.LOGIN, 5, {}],
        ["u002", EVENT_TYPES.SUBSCRIPTION, 6, { amountCents: 9900 }],

        ["u003", EVENT_TYPES.VISIT, 1, { source: "organic" }],
        ["u003", EVENT_TYPES.SIGNUP, 1, {
            source: "organic",
            referredBy: "u001"
        }],
        ["u003", EVENT_TYPES.ACTIVATION, 2, {}],
        ["u003", EVENT_TYPES.LOGIN, 4, {}],

        ["u004", EVENT_TYPES.SIGNUP, 2, { source: "social" }],
        ["u004", EVENT_TYPES.ACTIVATION, 3, {}],
        ["u004", EVENT_TYPES.PURCHASE, 5, { amountCents: 2900 }],

        ["u005", EVENT_TYPES.SIGNUP, 3, { source: "paid" }]
    ];

    const events = definitions.map(
        ([userId, type, offset, properties]) =>
            platform.createEvent(
                userId,
                type,
                new Date(base.getTime() + offset * 86_400_000),
                properties
            )
    );

    const results = await platform.ingestBatch(events, 4);

    const failures = results.filter(result => !result.success);

    if (failures.length) {
        throw new Error(
            `Batch processing failed: ${JSON.stringify(failures)}`
        );
    }

    const report = platform.funnel();

    console.log("\nAARRR GROWTH REPORT");
    console.log(JSON.stringify(report, null, 2));

    console.log("\nACQUISITION EXPERIMENT");
    console.log(JSON.stringify(
        Experiment.compare(
            [false, true, false, true, false, false],
            [true, true, false, true, true, false]
        ),
        null,
        2
    ));

    try {
        await platform.exportReport("aarrr-report.json");
        console.log("\nReport written successfully.");
    } catch (error) {
        if (error.code === "EEXIST") {
            console.log("Report already exists. Refusing to overwrite.");
        } else {
            throw error;
        }
    }
}

main().catch(error => {
    console.error("Growth platform failure:", error.message);
    process.exitCode = 1;
});
