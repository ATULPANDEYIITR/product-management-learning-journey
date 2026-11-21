"use strict";

const { EventEmitter } = require("node:events");

class ValidationError extends Error {}
class DuplicateEventError extends Error {}

const EVENT_TYPES = new Set([
    "login",
    "page_view",
    "action",
    "purchase",
    "logout"
]);

const QUALIFYING_EVENTS = new Set([
    "login",
    "page_view",
    "action",
    "purchase"
]);

function validateEvent(event) {
    if (!event || typeof event !== "object") {
        throw new ValidationError("Event must be an object.");
    }

    if (
        typeof event.eventId !== "string" ||
        !event.eventId.trim()
    ) {
        throw new ValidationError("A valid eventId is required.");
    }

    if (
        typeof event.userId !== "string" ||
        !event.userId.trim()
    ) {
        throw new ValidationError("A valid userId is required.");
    }

    if (!EVENT_TYPES.has(event.type)) {
        throw new ValidationError("Unsupported event type.");
    }

    const timestamp = new Date(event.timestamp);

    if (Number.isNaN(timestamp.getTime())) {
        throw new ValidationError("Invalid event timestamp.");
    }

    if (timestamp.getTime() > Date.now() + 300000) {
        throw new ValidationError("Future event timestamp rejected.");
    }

    return Object.freeze({
        eventId: event.eventId.trim(),
        userId: event.userId.trim(),
        type: event.type,
        timestamp: timestamp.toISOString(),
        properties: Object.freeze({ ...(event.properties || {}) })
    });
}

function utcDayStart(date) {
    const result = new Date(date);
    result.setUTCHours(0, 0, 0, 0);
    return result;
}

function uniqueUsers(events, start, end) {
    const users = new Set();

    for (const event of events) {
        const timestamp = new Date(event.timestamp);

        if (
            QUALIFYING_EVENTS.has(event.type) &&
            timestamp >= start &&
            timestamp < end
        ) {
            users.add(event.userId);
        }
    }

    return users;
}

class EngagementStore extends EventEmitter {
    constructor({ sessionTimeoutMinutes = 30 } = {}) {
        super();

        if (
            !Number.isInteger(sessionTimeoutMinutes) ||
            sessionTimeoutMinutes < 1 ||
            sessionTimeoutMinutes > 1440
        ) {
            throw new ValidationError("Invalid session timeout.");
        }

        this.timeoutMs = sessionTimeoutMinutes * 60 * 1000;
        this.events = [];
        this.eventIds = new Set();
        this.userEvents = new Map();
    }

    async ingest(rawEvent) {
        // Validation happens before any state mutation.
        const event = validateEvent(rawEvent);

        if (this.eventIds.has(event.eventId)) {
            throw new DuplicateEventError(
                `Duplicate event: ${event.eventId}`
            );
        }

        this.eventIds.add(event.eventId);
        this.events.push(event);

        if (!this.userEvents.has(event.userId)) {
            this.userEvents.set(event.userId, []);
        }

        this.userEvents.get(event.userId).push(event);

        this.emit("event:accepted", event);

        return event;
    }

    async ingestBatch(rawEvents) {
        if (!Array.isArray(rawEvents)) {
            throw new ValidationError("Batch must be an array.");
        }

        const accepted = [];
        const rejected = [];

        for (const rawEvent of rawEvents) {
            try {
                accepted.push(await this.ingest(rawEvent));
            } catch (error) {
                rejected.push({
                    eventId: rawEvent?.eventId ?? null,
                    reason: error.message
                });

                this.emit("event:rejected", {
                    eventId: rawEvent?.eventId ?? null,
                    error
                });
            }
        }

        return { accepted, rejected };
    }

    calculateDaily(dateString) {
        const selectedDate = new Date(`${dateString}T00:00:00.000Z`);

        if (Number.isNaN(selectedDate.getTime())) {
            throw new ValidationError("Invalid reporting date.");
        }

        const dayStart = utcDayStart(selectedDate);
        const dayEnd = new Date(dayStart.getTime() + 86400000);

        const weekStart = new Date(
            dayStart.getTime() - 6 * 86400000
        );

        const monthStart = new Date(
            dayStart.getTime() - 29 * 86400000
        );

        const dauUsers = uniqueUsers(
            this.events,
            dayStart,
            dayEnd
        );

        const wauUsers = uniqueUsers(
            this.events,
            weekStart,
            dayEnd
        );

        const mauUsers = uniqueUsers(
            this.events,
            monthStart,
            dayEnd
        );

        const dailyEvents = this.events.filter(event => {
            const timestamp = new Date(event.timestamp);

            return (
                QUALIFYING_EVENTS.has(event.type) &&
                timestamp >= dayStart &&
                timestamp < dayEnd
            );
        });

        const sessions = this.buildSessions(dailyEvents);

        const durations = sessions.map(session =>
            (session.lastEvent - session.start) / 1000
        );

        const totalDuration = durations.reduce(
            (sum, value) => sum + value,
            0
        );

        const average = values =>
            values.length
                ? values.reduce((sum, value) => sum + value, 0) /
                  values.length
                : 0;

        const report = Object.freeze({
            date: dateString,
            dau: dauUsers.size,
            wau: wauUsers.size,
            mau: mauUsers.size,
            stickiness: mauUsers.size
                ? Number(
                    (dauUsers.size / mauUsers.size * 100).toFixed(2)
                )
                : 0,
            qualifyingEvents: dailyEvents.length,
            sessions: sessions.length,
            averageSessionDurationSeconds: Number(
                average(durations).toFixed(2)
            ),
            averageSessionsPerUser: Number(
                (
                    sessions.length /
                    new Set(sessions.map(session => session.userId)).size
                || 0).toFixed(2)
            ),
            averageEventsPerSession: Number(
                average(sessions.map(session => session.eventCount)).toFixed(2)
            )
        });

        this.emit("metrics:calculated", report);

        return report;
    }

    buildSessions(events) {
        const grouped = new Map();

        for (const event of events) {
            if (!grouped.has(event.userId)) {
                grouped.set(event.userId, []);
            }

            grouped.get(event.userId).push(event);
        }

        const sessions = [];

        for (const [userId, userEvents] of grouped) {
            userEvents.sort(
                (a, b) =>
                    Date.parse(a.timestamp) - Date.parse(b.timestamp)
            );

            let current = null;

            for (const event of userEvents) {
                const time = Date.parse(event.timestamp);

                if (
                    current === null ||
                    time - current.lastEvent > this.timeoutMs
                ) {
                    if (current) {
                        sessions.push(current);
                    }

                    current = {
                        userId,
                        start: time,
                        lastEvent: time,
                        eventCount: 1
                    };
                } else {
                    current.lastEvent = time;
                    current.eventCount++;
                }
            }

            if (current) {
                sessions.push(current);
            }
        }

        return sessions.sort((a, b) => a.start - b.start);
    }

    getUserFrequency(dateString) {
        const reportDate = new Date(
            `${dateString}T00:00:00.000Z`
        );

        if (Number.isNaN(reportDate.getTime())) {
            throw new ValidationError("Invalid date.");
        }

        const end = new Date(reportDate.getTime() + 86400000);

        const dailyEvents = this.events.filter(event => {
            const timestamp = new Date(event.timestamp);

            return (
                QUALIFYING_EVENTS.has(event.type) &&
                timestamp >= reportDate &&
                timestamp < end
            );
        });

        const frequency = new Map();

        for (const session of this.buildSessions(dailyEvents)) {
            frequency.set(
                session.userId,
                (frequency.get(session.userId) || 0) + 1
            );
        }

        return Object.fromEntries(
            [...frequency.entries()].sort(
                (a, b) => a[0].localeCompare(b[0])
            )
        );
    }
}

async function main() {
    const analytics = new EngagementStore({
        sessionTimeoutMinutes: 30
    });

    analytics.on("event:accepted", event => {
        console.log(`Accepted: ${event.eventId}`);
    });

    analytics.on("event:rejected", event => {
        console.error(`Rejected: ${event.eventId}: ${event.error.message}`);
    });

    analytics.on("metrics:calculated", report => {
        console.log(`Calculated metrics for ${report.date}`);
    });

    const events = [
        {
            eventId: "e1",
            userId: "user_001",
            type: "login",
            timestamp: "2026-11-19T09:00:00Z"
        },
        {
            eventId: "e2",
            userId: "user_001",
            type: "page_view",
            timestamp: "2026-11-19T09:05:00Z"
        },
        {
            eventId: "e3",
            userId: "user_001",
            type: "action",
            timestamp: "2026-11-19T09:15:00Z"
        },
        {
            eventId: "e4",
            userId: "user_001",
            type: "login",
            timestamp: "2026-11-19T11:00:00Z"
        },
        {
            eventId: "e5",
            userId: "user_002",
            type: "login",
            timestamp: "2026-11-19T10:00:00Z"
        },
        {
            eventId: "e6",
            userId: "user_002",
            type: "purchase",
            timestamp: "2026-11-19T10:10:00Z"
        },
        {
            eventId: "e7",
            userId: "user_003",
            type: "page_view",
            timestamp: "2026-11-18T12:00:00Z"
        },
        {
            eventId: "e8",
            userId: "user_003",
            type: "action",
            timestamp: "2026-11-17T12:00:00Z"
        },
        {
            eventId: "e9",
            userId: "user_004",
            type: "login",
            timestamp: "2026-11-01T08:00:00Z"
        },
        {
            eventId: "e10",
            userId: "user_005",
            type: "logout",
            timestamp: "2026-11-19T12:00:00Z"
        }
    ];

    const result = await analytics.ingestBatch(events);

    console.log("\nINGESTION");
    console.log("Accepted:", result.accepted.length);
    console.log("Rejected:", result.rejected.length);

    // Duplicate delivery is handled independently from batch processing.
    try {
        await analytics.ingest(events[0]);
    } catch (error) {
        console.log("Duplicate protection:", error.message);
    }

    console.log("\nENGAGEMENT REPORT");
    const report = analytics.calculateDaily("2026-11-19");
    console.log(JSON.stringify(report, null, 2));

    console.log("\nUSER SESSION FREQUENCY");
    console.log(
        JSON.stringify(
            analytics.getUserFrequency("2026-11-19"),
            null,
            2
        )
    );

    if (
        report.dau !== 2 ||
        report.wau !== 3 ||
        report.mau !== 4 ||
        report.stickiness !== 50
    ) {
        throw new Error("Metric validation failed.");
    }

    console.log("\nAll metric checks passed.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
