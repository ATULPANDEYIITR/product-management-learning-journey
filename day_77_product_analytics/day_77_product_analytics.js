"use strict";

/*
 * Product Analytics Event Processing System
 *
 * Node.js 18+
 *
 * Capabilities:
 * - Event-driven collection
 * - Asynchronous ingestion
 * - User identity management
 * - Property validation
 * - Session management
 * - Event aggregation
 * - Ordered conversion funnels
 * - Monthly retention cohorts
 * - Buffered JSONL persistence
 *
 * Run:
 * node product_analytics.js
 */

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const EventEmitter = require("node:events");


class AnalyticsError extends Error {}
class ValidationError extends AnalyticsError {}
class DuplicateEventError extends AnalyticsError {}


const EventTypes = Object.freeze({
    SIGNUP: "signup",
    LOGIN: "login",
    PAGE_VIEW: "page_view",
    PRODUCT_VIEW: "product_view",
    ADD_TO_CART: "add_to_cart",
    CHECKOUT_STARTED: "checkout_started",
    PURCHASE: "purchase",
    LOGOUT: "logout"
});


function assert(condition, message) {
    if (!condition) {
        throw new ValidationError(message);
    }
}


function validIdentifier(value, name) {
    assert(
        typeof value === "string" &&
        value.trim().length > 0 &&
        value.length <= 150,
        `${name} must be a nonempty string.`
    );
}


function validateProperties(properties) {
    assert(
        properties !== null &&
        typeof properties === "object" &&
        !Array.isArray(properties),
        "Properties must be an object."
    );

    const entries = Object.entries(properties);

    assert(entries.length <= 50, "Property limit exceeded.");

    for (const [key, value] of entries) {
        validIdentifier(key, "Property name");

        assert(
            value === null ||
            ["string", "number", "boolean"].includes(typeof value),
            `Unsupported property type: ${key}`
        );

        if (typeof value === "number") {
            assert(Number.isFinite(value), `Invalid number: ${key}`);
        }

        if (typeof value === "string") {
            assert(value.length <= 2000, `Property too large: ${key}`);
        }
    }
}


function monthKey(date) {
    return `${date.getUTCFullYear()}-${String(
        date.getUTCMonth() + 1
    ).padStart(2, "0")}`;
}


function monthDifference(first, second) {
    return (
        (second.getUTCFullYear() - first.getUTCFullYear()) * 12 +
        second.getUTCMonth() -
        first.getUTCMonth()
    );
}


// ============================================================
// User identity registry
// ============================================================

class IdentityRegistry {

    constructor() {
        this.users = new Map();
        this.anonymousToUser = new Map();
    }

    register(user) {
        validIdentifier(user.userId, "User ID");

        if (this.users.has(user.userId)) {
            throw new ValidationError("User already registered.");
        }

        const record = Object.freeze({
            userId: user.userId,
            anonymousId: user.anonymousId ?? null,
            country: user.country ?? "IN",
            plan: user.plan ?? "free",
            createdAt: new Date(user.createdAt ?? Date.now())
        });

        assert(
            !Number.isNaN(record.createdAt.getTime()),
            "Invalid user creation date."
        );

        if (record.anonymousId) {
            assert(
                !this.anonymousToUser.has(record.anonymousId),
                "Anonymous identity already linked."
            );

            this.anonymousToUser.set(
                record.anonymousId,
                record.userId
            );
        }

        this.users.set(record.userId, record);
        return record;
    }

    resolve(identifier) {
        if (this.users.has(identifier)) {
            return identifier;
        }

        return this.anonymousToUser.get(identifier) ?? null;
    }

    linkAnonymous(anonymousId, userId) {
        assert(this.users.has(userId), "Unknown registered user.");

        const existing = this.anonymousToUser.get(anonymousId);

        if (existing && existing !== userId) {
            throw new ValidationError(
                "Anonymous identity is already linked."
            );
        }

        this.anonymousToUser.set(anonymousId, userId);
    }
}


// ============================================================
// Event collector
// ============================================================

class EventCollector extends EventEmitter {

    constructor(identityRegistry) {
        super();

        this.identityRegistry = identityRegistry;
        this.events = new Map();
        this.maxListeners = 100;
    }

    track(input) {
        validIdentifier(input.eventName, "Event name");

        const userId = this.identityRegistry.resolve(input.userId);

        if (!userId) {
            throw new ValidationError("Unknown user identity.");
        }

        const timestamp = new Date(input.timestamp ?? Date.now());

        assert(
            !Number.isNaN(timestamp.getTime()),
            "Invalid event timestamp."
        );

        const properties = structuredClone(input.properties ?? {});
        validateProperties(properties);

        const eventId = input.eventId ?? crypto.randomUUID();

        if (this.events.has(eventId)) {
            throw new DuplicateEventError(
                `Duplicate event: ${eventId}`
            );
        }

        const event = Object.freeze({
            eventId,
            userId,
            eventName: input.eventName,
            timestamp,
            sessionId: input.sessionId ?? null,
            properties: Object.freeze(properties)
        });

        this.events.set(eventId, event);

        // Consumers can process the event without coupling the collector
        // to reporting, storage, or business-specific logic.
        this.emit("event", event);

        return event;
    }

    getAll() {
        return [...this.events.values()];
    }
}


// ============================================================
// Asynchronous ingestion pipeline
// ============================================================

class IngestionPipeline {

    constructor(collector, concurrency = 4) {
        assert(
            Number.isInteger(concurrency) && concurrency > 0,
            "Concurrency must be positive."
        );

        this.collector = collector;
        this.concurrency = concurrency;
        this.queue = [];
        this.processing = false;
    }

    enqueue(input) {
        return new Promise((resolve, reject) => {
            this.queue.push({ input, resolve, reject });
            this.process();
        });
    }

    async process() {
        if (this.processing) return;

        this.processing = true;

        try {
            while (this.queue.length > 0) {
                const batch = this.queue.splice(
                    0,
                    this.concurrency
                );

                await Promise.all(
                    batch.map(async item => {
                        try {
                            const event = await Promise.resolve().then(
                                () => this.collector.track(item.input)
                            );

                            item.resolve(event);
                        } catch (error) {
                            item.reject(error);
                        }
                    })
                );
            }
        } finally {
            this.processing = false;

            if (this.queue.length > 0) {
                void this.process();
            }
        }
    }
}


// ============================================================
// Stateful session engine
// ============================================================

class SessionEngine {

    constructor(timeoutMinutes = 30) {
        assert(timeoutMinutes > 0, "Invalid session timeout.");

        this.timeoutMs = timeoutMinutes * 60 * 1000;
        this.sessions = new Map();
    }

    process(events) {
        const grouped = new Map();

        for (const event of events) {
            if (!grouped.has(event.userId)) {
                grouped.set(event.userId, []);
            }

            grouped.get(event.userId).push(event);
        }

        const results = [];

        for (const [userId, userEvents] of grouped) {
            userEvents.sort(
                (a, b) => a.timestamp - b.timestamp
            );

            let current = null;

            for (const event of userEvents) {
                const expired = (
                    current === null ||
                    event.timestamp - current.lastEventAt >
                    this.timeoutMs
                );

                const explicitChange = (
                    current !== null &&
                    event.sessionId !== null &&
                    current.sessionId !== event.sessionId
                );

                if (expired || explicitChange) {
                    current = {
                        sessionId:
                            event.sessionId ?? crypto.randomUUID(),
                        userId,
                        startedAt: event.timestamp,
                        lastEventAt: event.timestamp,
                        eventCount: 0,
                        eventNames: new Set()
                    };

                    results.push(current);
                }

                current.eventCount++;
                current.eventNames.add(event.eventName);

                if (event.timestamp > current.lastEventAt) {
                    current.lastEventAt = event.timestamp;
                }
            }
        }

        this.sessions = new Map(
            results.map(session => [
                session.sessionId,
                session
            ])
        );

        return results.map(session => ({
            ...session,
            eventNames: [...session.eventNames],
            durationMs:
                session.lastEventAt - session.startedAt
        }));
    }
}


// ============================================================
// Aggregation engine
// ============================================================

class ProductMetrics {

    constructor(events) {
        this.events = [...events];
    }

    summarize() {
        const eventCounts = new Map();
        const eventUsers = new Map();
        const activeUsers = new Set();

        let revenue = 0;
        let purchases = 0;

        for (const event of this.events) {
            activeUsers.add(event.userId);

            eventCounts.set(
                event.eventName,
                (eventCounts.get(event.eventName) ?? 0) + 1
            );

            if (!eventUsers.has(event.eventName)) {
                eventUsers.set(event.eventName, new Set());
            }

            eventUsers.get(event.eventName).add(event.userId);

            if (event.eventName === EventTypes.PURCHASE) {
                const amount = event.properties.amount ?? 0;

                assert(
                    typeof amount === "number" &&
                    Number.isFinite(amount) &&
                    amount >= 0,
                    "Invalid purchase amount."
                );

                revenue += amount;
                purchases++;
            }
        }

        return {
            totalEvents: this.events.length,
            activeUsers: activeUsers.size,
            eventCounts: Object.fromEntries(eventCounts),
            uniqueUsersPerEvent: Object.fromEntries(
                [...eventUsers].map(([name, users]) => [
                    name,
                    users.size
                ])
            ),
            revenue: Number(revenue.toFixed(2)),
            averageOrderValue: purchases
                ? Number((revenue / purchases).toFixed(2))
                : 0
        };
    }
}


// ============================================================
// Funnel evaluator
// ============================================================

class FunnelEngine {

    evaluate(events, steps, windowHours = 168) {
        assert(steps.length >= 2, "At least two funnel steps required.");

        assert(
            new Set(steps).size === steps.length,
            "Funnel steps must be unique."
        );

        assert(windowHours > 0, "Invalid conversion window.");

        const byUser = new Map();

        for (const event of events) {
            if (!byUser.has(event.userId)) {
                byUser.set(event.userId, []);
            }

            byUser.get(event.userId).push(event);
        }

        const counts = Array(steps.length).fill(0);
        const windowMs = windowHours * 60 * 60 * 1000;

        for (const userEvents of byUser.values()) {
            userEvents.sort(
                (a, b) => a.timestamp - b.timestamp
            );

            let cursor = 0;
            let firstTimestamp = null;

            for (const event of userEvents) {
                if (event.eventName !== steps[cursor]) continue;

                if (firstTimestamp === null) {
                    firstTimestamp = event.timestamp;
                } else if (
                    event.timestamp - firstTimestamp > windowMs
                ) {
                    break;
                }

                counts[cursor]++;

                cursor++;

                if (cursor === steps.length) break;
            }
        }

        const conversionRates = counts.map((count, index) => {
            if (index === 0) {
                return count > 0 ? 100 : 0;
            }

            return counts[index - 1] > 0
                ? Number(
                    (
                        count / counts[index - 1] * 100
                    ).toFixed(2)
                )
                : 0;
        });

        return {
            steps,
            counts,
            conversionRates,
            overallConversion: counts[0]
                ? Number(
                    (counts.at(-1) / counts[0] * 100).toFixed(2)
                )
                : 0
        };
    }
}


// ============================================================
// Cohort retention
// ============================================================

class CohortEngine {

    analyze(users, events) {
        const activity = new Map();

        for (const event of events) {
            if (!activity.has(event.userId)) {
                activity.set(event.userId, new Set());
            }

            activity.get(event.userId).add(
                monthKey(event.timestamp)
            );
        }

        const cohorts = new Map();

        for (const user of users.values()) {
            const key = monthKey(user.createdAt);

            if (!cohorts.has(key)) {
                cohorts.set(key, []);
            }

            cohorts.get(key).push(user.userId);
        }

        const output = [];

        for (const [cohortMonth, userIds] of [...cohorts].sort()) {
            const [year, month] = cohortMonth.split("-").map(Number);

            const cohortDate = new Date(
                Date.UTC(year, month - 1, 1)
            );

            const retention = new Map();

            for (const userId of userIds) {
                for (const activeMonth of activity.get(userId) ?? []) {
                    const [activeYear, activeMonthNumber] =
                        activeMonth.split("-").map(Number);

                    const activeDate = new Date(
                        Date.UTC(activeYear, activeMonthNumber - 1, 1)
                    );

                    const offset = monthDifference(
                        cohortDate,
                        activeDate
                    );

                    if (offset >= 0) {
                        retention.set(
                            offset,
                            (retention.get(offset) ?? 0) + 1
                        );
                    }
                }
            }

            retention.set(0, userIds.length);

            output.push({
                cohortMonth,
                users: userIds.length,
                retention: Object.fromEntries(
                    [...retention]
                        .sort((a, b) => a[0] - b[0])
                        .map(([monthIndex, count]) => [
                            monthIndex,
                            {
                                users: count,
                                rate: Number(
                                    (
                                        count / userIds.length * 100
                                    ).toFixed(2)
                                )
                            }
                        ])
                )
            });
        }

        return output;
    }
}


// ============================================================
// Durable JSONL persistence
// ============================================================

class EventFileRepository {

    async save(events, filePath) {
        const directory = path.dirname(filePath);

        await fs.promises.mkdir(directory, {
            recursive: true
        });

        const temporaryPath =
            `${filePath}.${crypto.randomUUID()}.tmp`;

        const handle = await fs.promises.open(
            temporaryPath,
            "wx",
            0o600
        );

        try {
            for (const event of events) {
                const record = {
                    ...event,
                    timestamp: event.timestamp.toISOString()
                };

                await handle.write(
                    JSON.stringify(record) + "\n"
                );
            }

            await handle.sync();
            await handle.close();

            await fs.promises.rename(
                temporaryPath,
                filePath
            );
        } catch (error) {
            await handle.close().catch(() => {});
            await fs.promises.unlink(temporaryPath).catch(() => {});
            throw error;
        }
    }

    async load(filePath) {
        const content = await fs.promises.readFile(
            filePath,
            "utf8"
        );

        const records = [];

        for (const [index, line] of content
            .split(/\r?\n/)
            .entries()) {

            if (!line.trim()) continue;

            try {
                records.push(JSON.parse(line));
            } catch {
                throw new ValidationError(
                    `Malformed JSONL at line ${index + 1}`
                );
            }
        }

        return records;
    }
}


// ============================================================
// Demonstration
// ============================================================

async function main() {
    const identities = new IdentityRegistry();

    const base = new Date("2026-09-01T09:00:00Z");

    const users = [
        ["U001", 0, "free"],
        ["U002", 2, "premium"],
        ["U003", 1440, "free"],
        ["U004", 43200, "premium"],
        ["U005", 44640, "free"]
    ];

    for (const [userId, offsetMinutes, plan] of users) {
        identities.register({
            userId,
            anonymousId: `ANON-${userId}`,
            country: "IN",
            plan,
            createdAt: new Date(
                base.getTime() + offsetMinutes * 60000
            )
        });
    }

    const collector = new EventCollector(identities);

    const failedEvents = [];

    collector.on("event", event => {
        if (event.eventName === EventTypes.PURCHASE) {
            console.log(
                `Purchase event accepted: ${event.eventId}`
            );
        }
    });

    collector.on("error", error => {
        failedEvents.push(error);
    });

    const pipeline = new IngestionPipeline(collector, 4);

    const journeys = {
        U001: [
            ["signup", 0, {}],
            ["login", 1, {}],
            ["product_view", 5, { productId: "P100" }],
            ["add_to_cart", 10, { productId: "P100" }],
            ["checkout_started", 15, {}],
            ["purchase", 20, { amount: 1499, currency: "INR" }],
            ["page_view", 31 * 1440, { page: "/dashboard" }]
        ],
        U002: [
            ["signup", 0, {}],
            ["login", 1, {}],
            ["product_view", 3, { productId: "P200" }],
            ["add_to_cart", 5, { productId: "P200" }],
            ["checkout_started", 8, {}],
            ["purchase", 12, { amount: 2499, currency: "INR" }],
            ["page_view", 32 * 1440, { page: "/pricing" }]
        ],
        U003: [
            ["signup", 0, {}],
            ["login", 2, {}],
            ["product_view", 4, { productId: "P100" }],
            ["add_to_cart", 6, { productId: "P100" }],
            ["page_view", 31 * 1440, { page: "/products" }]
        ],
        U004: [
            ["signup", 0, {}],
            ["login", 1, {}],
            ["product_view", 3, { productId: "P300" }],
            ["page_view", 31 * 1440, { page: "/dashboard" }]
        ],
        U005: [
            ["signup", 0, {}],
            ["login", 1, {}],
            ["product_view", 2, { productId: "P100" }],
            ["add_to_cart", 4, { productId: "P100" }],
            ["checkout_started", 6, {}],
            ["purchase", 9, { amount: 799, currency: "GBP" }]
        ]
    };

    const tasks = [];

    for (const [userId, journey] of Object.entries(journeys)) {
        const user = identities.users.get(userId);

        for (const [index, [eventName, offset, properties]]
            of journey.entries()) {

            tasks.push(
                pipeline.enqueue({
                    eventId: `${userId}-EVENT-${index + 1}`,
                    userId,
                    eventName,
                    timestamp: new Date(
                        user.createdAt.getTime() + offset * 60000
                    ),
                    sessionId: `${userId}-SESSION-1`,
                    properties
                })
            );
        }
    }

    const settled = await Promise.allSettled(tasks);

    const rejected = settled.filter(
        result => result.status === "rejected"
    );

    assert(rejected.length === 0, "Event ingestion failed.");

    const events = collector.getAll();

    assert(events.length === 30, "Unexpected event count.");

    const sessions = new SessionEngine().process(events);

    const metrics = new ProductMetrics(events).summarize();

    const funnel = new FunnelEngine().evaluate(
        events,
        [
            "signup",
            "product_view",
            "add_to_cart",
            "checkout_started",
            "purchase"
        ]
    );

    const cohorts = new CohortEngine().analyze(
        identities.users,
        events
    );

    assert(metrics.activeUsers === 5, "Incorrect active users.");
    assert(metrics.revenue === 4797, "Incorrect revenue.");
    assert(funnel.counts.at(-1) === 3, "Incorrect conversions.");

    console.log("\nPRODUCT ANALYTICS REPORT");
    console.log("=======================");
    console.log(JSON.stringify(metrics, null, 2));

    console.log("\nSESSION METRICS");
    console.log({
        sessions: sessions.length,
        averageDurationMs: sessions.length
            ? sessions.reduce(
                (sum, session) => sum + session.durationMs,
                0
            ) / sessions.length
            : 0
    });

    console.log("\nCONVERSION FUNNEL");
    console.log(JSON.stringify(funnel, null, 2));

    console.log("\nCOHORT RETENTION");
    console.log(JSON.stringify(cohorts, null, 2));

    const repository = new EventFileRepository();

    const output = path.join(
        process.cwd(),
        "product_analytics_events.jsonl"
    );

    await repository.save(events, output);

    const restored = await repository.load(output);

    assert(
        restored.length === events.length,
        "Persistence verification failed."
    );

    // Verify duplicate detection.
    try {
        collector.track({
            eventId: events[0].eventId,
            userId: "U001",
            eventName: "page_view"
        });
    } catch (error) {
        assert(
            error instanceof DuplicateEventError,
            "Incorrect duplicate error."
        );
    }

    // Verify invalid user handling.
    try {
        collector.track({
            userId: "UNKNOWN",
            eventName: "page_view"
        });
    } catch (error) {
        assert(
            error instanceof ValidationError,
            "Incorrect validation error."
        );
    }

    console.log("\nVALIDATION");
    console.log("Events ingested:", events.length);
    console.log("Events restored:", restored.length);
    console.log("Failed ingestion events:", failedEvents.length);
    console.log("All validation checks passed.");
    console.log("Output:", output);
}


main().catch(error => {
    console.error("Analytics execution failed:", error.message);
    process.exitCode = 1;
});
