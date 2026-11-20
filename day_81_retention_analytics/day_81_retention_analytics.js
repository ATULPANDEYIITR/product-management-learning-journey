"use strict";

/*
 * Event-driven retention analytics.
 *
 * Models:
 * - Event ingestion and deduplication
 * - Monthly acquisition cohorts
 * - Exact-day retention curves
 * - Rolling inactivity-based churn
 * - Resurrection after an inactivity gap
 * - Asynchronous batch processing
 * - Policy evaluation and event notifications
 *
 * Runtime: Node.js 18+
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const { EventEmitter } = require("node:events");

const DAY_MS = 24 * 60 * 60 * 1000;

const EventType = Object.freeze({
    SIGNUP: "signup",
    ACTIVE: "active",
    LOGIN: "login",
    PURCHASE: "purchase"
});

const ACTIVE_EVENTS = new Set([
    EventType.ACTIVE,
    EventType.LOGIN,
    EventType.PURCHASE
]);

class AnalyticsError extends Error {
    constructor(message) {
        super(message);
        this.name = "AnalyticsError";
    }
}

function parseDate(value) {
    if (typeof value !== "string" ||
        !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        throw new AnalyticsError(`Invalid date: ${value}`);
    }

    const timestamp = Date.parse(`${value}T00:00:00.000Z`);

    if (!Number.isFinite(timestamp)) {
        throw new AnalyticsError(`Invalid date: ${value}`);
    }

    const normalized = new Date(timestamp).toISOString().slice(0, 10);

    if (normalized !== value) {
        throw new AnalyticsError(`Invalid calendar date: ${value}`);
    }

    return timestamp;
}

function dateString(timestamp) {
    return new Date(timestamp).toISOString().slice(0, 10);
}

function dayDifference(first, second) {
    return Math.floor((second - first) / DAY_MS);
}

function validateEvent(event) {
    if (!event || typeof event !== "object") {
        throw new AnalyticsError("Event must be an object");
    }

    if (typeof event.userId !== "string" ||
        !event.userId.trim() ||
        event.userId.length > 128) {
        throw new AnalyticsError("Invalid user ID");
    }

    if (!Object.values(EventType).includes(event.type)) {
        throw new AnalyticsError("Unsupported event type");
    }

    return {
        userId: event.userId.trim(),
        timestamp: parseDate(event.date),
        type: event.type
    };
}

class RetentionPolicy {
    constructor({
        churnDays = 30,
        retentionDays = [0, 1, 7, 14, 30]
    } = {}) {
        if (!Number.isInteger(churnDays) || churnDays < 1) {
            throw new AnalyticsError("Invalid churn threshold");
        }

        if (!Array.isArray(retentionDays) ||
            retentionDays.length === 0 ||
            retentionDays.some(
                day => !Number.isInteger(day) || day < 0
            )) {
            throw new AnalyticsError("Invalid retention intervals");
        }

        this.churnDays = churnDays;
        this.retentionDays = [...new Set(retentionDays)].sort(
            (a, b) => a - b
        );
        Object.freeze(this.retentionDays);
    }

    evaluate(inactiveDays, tenureDays) {
        if (tenureDays < this.churnDays) {
            return "NOT_ELIGIBLE";
        }

        return inactiveDays >= this.churnDays
            ? "CHURNED"
            : "ACTIVE";
    }
}

class RetentionEngine extends EventEmitter {
    #events = new Map();
    #users = new Map();
    #processed = false;

    constructor(policy = new RetentionPolicy()) {
        super();
        this.policy = policy;
    }

    ingest(rawEvent) {
        const event = validateEvent(rawEvent);

        let userEvents = this.#events.get(event.userId);

        if (!userEvents) {
            userEvents = new Map();
            this.#events.set(event.userId, userEvents);
        }

        const key = `${event.timestamp}:${event.type}`;

        if (userEvents.has(key)) {
            return false;
        }

        userEvents.set(key, event);
        this.#processed = false;

        this.emit("event:accepted", {
            userId: event.userId,
            type: event.type,
            date: dateString(event.timestamp)
        });

        return true;
    }

    async ingestBatch(events) {
        if (!Array.isArray(events)) {
            throw new AnalyticsError("Batch must be an array");
        }

        let accepted = 0;

        // Validate the complete batch before modifying engine state.
        const normalized = events.map(validateEvent);

        for (const event of normalized) {
            if (this.ingest({
                userId: event.userId,
                date: dateString(event.timestamp),
                type: event.type
            })) {
                accepted++;
            }
        }

        await Promise.resolve();

        this.emit("batch:completed", {
            received: events.length,
            accepted
        });

        return accepted;
    }

    process() {
        const nextUsers = new Map();

        for (const [userId, eventMap] of this.#events) {
            const events = [...eventMap.values()].sort(
                (a, b) => a.timestamp - b.timestamp
            );

            const signupEvents = events.filter(
                event => event.type === EventType.SIGNUP
            );

            if (signupEvents.length === 0) {
                throw new AnalyticsError(
                    `User ${userId} has no signup event`
                );
            }

            const signup = signupEvents[0].timestamp;

            const activityDates = new Set();

            for (const event of events) {
                if (event.timestamp >= signup &&
                    ACTIVE_EVENTS.has(event.type)) {
                    activityDates.add(event.timestamp);
                }
            }

            const orderedActivity = [...activityDates].sort(
                (a, b) => a - b
            );

            nextUsers.set(userId, {
                userId,
                signup,
                activityDates,
                orderedActivity,
                lastActive: orderedActivity.length
                    ? orderedActivity[orderedActivity.length - 1]
                    : signup
            });
        }

        // Replace derived state only after successful validation.
        this.#users = nextUsers;
        this.#processed = true;

        this.emit("processing:completed", {
            users: this.#users.size
        });

        return this;
    }

    #assertProcessed() {
        if (!this.#processed || this.#users.size === 0) {
            throw new AnalyticsError(
                "Process events before requesting analytics"
            );
        }
    }

    retentionCurve(observationDate) {
        this.#assertProcessed();

        const observation = parseDate(observationDate);
        const results = {};

        for (const interval of this.policy.retentionDays) {
            const eligible = [];
            let retained = 0;

            for (const user of this.#users.values()) {
                const target = user.signup + interval * DAY_MS;

                if (target > observation) continue;

                eligible.push(user);

                if (user.activityDates.has(target)) {
                    retained++;
                }
            }

            results[interval] = {
                eligible: eligible.length,
                retained,
                percentage: eligible.length
                    ? Number(
                        (retained / eligible.length * 100).toFixed(2)
                    )
                    : 0
            };
        }

        return results;
    }

    cohortRetention(observationDate, maxAge = 30) {
        this.#assertProcessed();

        if (!Number.isInteger(maxAge) || maxAge < 0) {
            throw new AnalyticsError("Invalid cohort age");
        }

        const observation = parseDate(observationDate);
        const cohorts = new Map();

        for (const user of this.#users.values()) {
            const cohort = dateString(user.signup).slice(0, 7);

            if (!cohorts.has(cohort)) {
                cohorts.set(cohort, []);
            }

            cohorts.get(cohort).push(user);
        }

        const report = {};

        for (const [cohort, users] of cohorts) {
            const periods = {};

            for (let day = 0; day <= maxAge; day++) {
                const eligible = users.filter(
                    user => user.signup + day * DAY_MS <= observation
                );

                if (!eligible.length) continue;

                const retained = eligible.filter(
                    user => user.activityDates.has(
                        user.signup + day * DAY_MS
                    )
                ).length;

                periods[day] = Number(
                    (retained / eligible.length * 100).toFixed(2)
                );
            }

            report[cohort] = periods;
        }

        return report;
    }

    churnAnalysis(observationDate) {
        this.#assertProcessed();

        const observation = parseDate(observationDate);

        const results = {
            active: [],
            churned: [],
            notEligible: []
        };

        for (const user of this.#users.values()) {
            const tenure = dayDifference(user.signup, observation);

            const inactive = dayDifference(
                user.lastActive,
                observation
            );

            const status = this.policy.evaluate(inactive, tenure);

            results[
                status === "ACTIVE"
                    ? "active"
                    : status === "CHURNED"
                        ? "churned"
                        : "notEligible"
            ].push(user.userId);
        }

        const eligible = results.active.length + results.churned.length;

        return {
            ...results,
            eligibleUsers: eligible,
            churnRate: eligible
                ? Number(
                    (results.churned.length / eligible * 100).toFixed(2)
                )
                : 0
        };
    }

    resurrectionAnalysis(observationDate) {
        this.#assertProcessed();

        const observation = parseDate(observationDate);
        const events = [];
        const resurrectedUsers = new Set();

        for (const user of this.#users.values()) {
            const activity = user.orderedActivity;

            for (let index = 1; index < activity.length; index++) {
                const previous = activity[index - 1];
                const current = activity[index];

                const inactiveDays = dayDifference(previous, current);

                if (inactiveDays >= this.policy.churnDays &&
                    current <= observation) {
                    resurrectedUsers.add(user.userId);

                    events.push({
                        userId: user.userId,
                        previousActivity: dateString(previous),
                        resurrectionDate: dateString(current),
                        inactiveDays
                    });
                }
            }
        }

        return {
            resurrectedUsers: resurrectedUsers.size,
            resurrectionEvents: events.length,
            events
        };
    }

    async generateReport(observationDate) {
        this.#assertProcessed();

        // Yield between analytical stages to avoid blocking callers
        // while allowing orchestration through Promises.
        const retention = this.retentionCurve(observationDate);
        await Promise.resolve();

        const cohorts = this.cohortRetention(observationDate);
        await Promise.resolve();

        const churn = this.churnAnalysis(observationDate);
        const resurrection = this.resurrectionAnalysis(observationDate);

        const report = {
            generatedAt: new Date().toISOString(),
            observationDate,
            totalUsers: this.#users.size,
            retention,
            cohorts,
            churn,
            resurrection
        };

        this.emit("report:generated", {
            users: this.#users.size,
            observationDate
        });

        return report;
    }

    async exportReport(filename, report) {
        const destination = path.resolve(filename);
        const temporary = `${destination}.${process.pid}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(report, null, 2),
                { encoding: "utf8", mode: 0o600 }
            );

            await fs.rename(temporary, destination);
        } catch (error) {
            await fs.rm(temporary, { force: true }).catch(() => {});
            throw new AnalyticsError(
                `Report export failed: ${error.message}`
            );
        }
    }
}

function sampleEvents() {
    return [
        ["U001", "2026-01-01", "signup"],
        ["U001", "2026-01-01", "active"],
        ["U001", "2026-01-02", "active"],
        ["U001", "2026-01-08", "active"],
        ["U001", "2026-03-05", "active"],

        ["U002", "2026-01-03", "signup"],
        ["U002", "2026-01-03", "active"],

        ["U003", "2026-01-10", "signup"],
        ["U003", "2026-01-10", "active"],
        ["U003", "2026-02-15", "active"],

        ["U004", "2026-02-01", "signup"],
        ["U004", "2026-02-01", "active"],
        ["U004", "2026-02-02", "active"],

        ["U005", "2026-02-05", "signup"],
        ["U005", "2026-02-05", "active"],

        ["U006", "2026-02-15", "signup"],
        ["U006", "2026-02-15", "active"],
        ["U006", "2026-03-20", "active"],

        ["U007", "2026-03-01", "signup"],
        ["U007", "2026-03-01", "active"],

        ["U008", "2026-03-10", "signup"],
        ["U008", "2026-03-10", "active"],

        ["U009", "2026-03-15", "signup"],
        ["U009", "2026-03-15", "active"]
    ].map(([userId, date, type]) => ({
        userId,
        date,
        type
    }));
}

async function runTests() {
    const engine = new RetentionEngine(
        new RetentionPolicy({ churnDays: 30 })
    );

    let completed = false;

    engine.on("batch:completed", () => {
        completed = true;
    });

    const events = sampleEvents();

    const accepted = await engine.ingestBatch(events);

    if (accepted !== events.length || !completed) {
        throw new Error("Batch ingestion test failed");
    }

    // Duplicate events are ignored.
    const duplicateAccepted = engine.ingest({
        userId: "U001",
        date: "2026-01-02",
        type: "active"
    });

    if (duplicateAccepted) {
        throw new Error("Deduplication test failed");
    }

    engine.process();

    const curve = engine.retentionCurve("2026-05-01");

    if (curve[0].percentage !== 100) {
        throw new Error("Day-zero retention test failed");
    }

    const churn = engine.churnAnalysis("2026-05-01");

    if (churn.eligibleUsers !== 9) {
        throw new Error("Churn eligibility test failed");
    }

    const resurrection = engine.resurrectionAnalysis("2026-05-01");

    if (resurrection.resurrectedUsers < 1) {
        throw new Error("Resurrection test failed");
    }

    let invalidRejected = false;

    try {
        engine.ingest({
            userId: "INVALID",
            date: "2026-02-30",
            type: "active"
        });
    } catch (error) {
        invalidRejected = error instanceof AnalyticsError;
    }

    if (!invalidRejected) {
        throw new Error("Invalid date validation test failed");
    }

    console.log("All JavaScript tests passed");
}

async function main() {
    if (process.argv.includes("--test")) {
        await runTests();
        return;
    }

    const engine = new RetentionEngine(
        new RetentionPolicy({
            churnDays: 30,
            retentionDays: [0, 1, 7, 14, 30]
        })
    );

    engine.on("report:generated", event => {
        console.log("Report generated:", event);
    });

    await engine.ingestBatch(sampleEvents());
    engine.process();

    const report = await engine.generateReport("2026-05-01");

    console.log(JSON.stringify(report, null, 2));

    await engine.exportReport("retention_report.json", report);
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
