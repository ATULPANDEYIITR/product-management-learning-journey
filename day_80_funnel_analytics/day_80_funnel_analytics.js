"use strict";

/*
 * Funnel Analytics Engine
 *
 * Event-driven funnel construction, cohort management,
 * conversion analysis, segmentation, and asynchronous reporting.
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");
const crypto = require("node:crypto");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class FunnelEvent {
    constructor({
        eventId,
        userId,
        eventName,
        timestamp,
        properties = {}
    }) {
        if (typeof eventId !== "string" || !eventId.trim()) {
            throw new ValidationError("Invalid event ID.");
        }

        if (typeof userId !== "string" || !userId.trim()) {
            throw new ValidationError("Invalid user ID.");
        }

        if (typeof eventName !== "string" || !eventName.trim()) {
            throw new ValidationError("Invalid event name.");
        }

        const date = new Date(timestamp);

        if (!Number.isFinite(date.getTime())) {
            throw new ValidationError("Invalid event timestamp.");
        }

        if (
            properties === null ||
            typeof properties !== "object" ||
            Array.isArray(properties)
        ) {
            throw new ValidationError("Properties must be an object.");
        }

        this.eventId = eventId;
        this.userId = userId;
        this.eventName = eventName;
        this.timestamp = date;
        this.properties = Object.freeze({ ...properties });

        Object.freeze(this);
    }
}

class FunnelDefinition {
    constructor({
        name,
        steps,
        conversionWindowHours = 168,
        strictOrder = true
    }) {
        if (!name || typeof name !== "string") {
            throw new ValidationError("Funnel name is required.");
        }

        if (!Array.isArray(steps) || steps.length < 2) {
            throw new ValidationError("At least two steps are required.");
        }

        if (
            steps.some(step => typeof step !== "string" || !step.trim()) ||
            new Set(steps).size !== steps.length
        ) {
            throw new ValidationError("Funnel steps must be unique valid names.");
        }

        if (
            !Number.isFinite(conversionWindowHours) ||
            conversionWindowHours <= 0
        ) {
            throw new ValidationError("Invalid conversion window.");
        }

        this.name = name;
        this.steps = Object.freeze([...steps]);
        this.conversionWindowHours = conversionWindowHours;
        this.strictOrder = strictOrder;

        Object.freeze(this);
    }
}

class EventRepository extends EventEmitter {
    #events = new Map();
    #users = new Map();

    add(event) {
        if (!(event instanceof FunnelEvent)) {
            throw new ValidationError("Expected FunnelEvent.");
        }

        if (this.#events.has(event.eventId)) {
            throw new ValidationError(
                `Duplicate event ID: ${event.eventId}`
            );
        }

        this.#events.set(event.eventId, event);

        if (!this.#users.has(event.userId)) {
            this.#users.set(event.userId, []);
        }

        this.#users.get(event.userId).push(event);

        this.emit("event:accepted", event);

        return event.eventId;
    }

    addBatch(events) {
        if (!Array.isArray(events)) {
            throw new ValidationError("Batch must be an array.");
        }

        const incomingIds = events.map(event => event.eventId);

        if (new Set(incomingIds).size !== incomingIds.length) {
            throw new ValidationError("Duplicate IDs in batch.");
        }

        for (const event of events) {
            if (
                !(event instanceof FunnelEvent) ||
                this.#events.has(event.eventId)
            ) {
                throw new ValidationError("Invalid or duplicate batch event.");
            }
        }

        for (const event of events) {
            this.add(event);
        }
    }

    getUserEvents(userId) {
        return [...(this.#users.get(userId) || [])]
            .sort((a, b) => a.timestamp - b.timestamp);
    }

    getAllEvents() {
        return [...this.#events.values()]
            .sort((a, b) => a.timestamp - b.timestamp);
    }

    get size() {
        return this.#events.size;
    }
}

class FunnelEngine {
    constructor(repository) {
        if (!(repository instanceof EventRepository)) {
            throw new ValidationError("Invalid event repository.");
        }

        this.repository = repository;
    }

    evaluateUser(events, funnel) {
        const timestamps = new Array(funnel.steps.length).fill(null);
        const windowMs = funnel.conversionWindowHours * 3600000;

        let nextStep = 0;
        let firstTimestamp = null;

        for (const event of events) {
            if (event.eventName !== funnel.steps[nextStep]) {
                continue;
            }

            if (firstTimestamp === null) {
                firstTimestamp = event.timestamp.getTime();
            }

            if (
                event.timestamp.getTime() - firstTimestamp > windowMs
            ) {
                break;
            }

            timestamps[nextStep] = event.timestamp;
            nextStep++;

            if (nextStep === funnel.steps.length) {
                break;
            }
        }

        return timestamps;
    }

    analyze(funnel, options = {}) {
        if (!(funnel instanceof FunnelDefinition)) {
            throw new ValidationError("Invalid funnel definition.");
        }

        const {
            start = null,
            end = null,
            segment = {}
        } = options;

        const startTime = start ? new Date(start).getTime() : -Infinity;
        const endTime = end ? new Date(end).getTime() : Infinity;

        if (
            Number.isNaN(startTime) ||
            Number.isNaN(endTime) ||
            startTime > endTime
        ) {
            throw new ValidationError("Invalid analysis time range.");
        }

        const counts = new Array(funnel.steps.length).fill(0);
        const userEvents = new Map();

        for (const event of this.repository.getAllEvents()) {
            if (!userEvents.has(event.userId)) {
                userEvents.set(event.userId, []);
            }

            userEvents.get(event.userId).push(event);
        }

        for (const events of userEvents.values()) {
            const entry = events.find(event =>
                event.eventName === funnel.steps[0] &&
                event.timestamp.getTime() >= startTime &&
                event.timestamp.getTime() <= endTime &&
                Object.entries(segment).every(
                    ([key, value]) => event.properties[key] === value
                )
            );

            if (!entry) {
                continue;
            }

            const progression = this.evaluateUser(
                events.filter(
                    event => event.timestamp >= entry.timestamp
                ),
                funnel
            );

            for (let i = 0; i < progression.length; i++) {
                if (progression[i] === null) {
                    break;
                }

                counts[i]++;
            }
        }

        const steps = funnel.steps.map((name, index) => {
            const users = counts[index];
            const previousUsers = index === 0
                ? users
                : counts[index - 1];

            const droppedUsers = previousUsers - users;

            return {
                name,
                users,
                previousUsers,
                droppedUsers,
                conversionRate: previousUsers
                    ? users / previousUsers * 100
                    : 0,
                dropOffRate: previousUsers
                    ? droppedUsers / previousUsers * 100
                    : 0
            };
        });

        const totalUsers = counts[0];
        const convertedUsers = counts[counts.length - 1];

        return Object.freeze({
            funnelName: funnel.name,
            totalUsers,
            convertedUsers,
            overallConversionRate: totalUsers
                ? convertedUsers / totalUsers * 100
                : 0,
            steps: Object.freeze(steps)
        });
    }

    segmentBy(funnel, property) {
        if (!property) {
            throw new ValidationError("Segment property is required.");
        }

        const values = new Set();

        for (const event of this.repository.getAllEvents()) {
            if (
                event.eventName === funnel.steps[0] &&
                Object.hasOwn(event.properties, property)
            ) {
                values.add(event.properties[property]);
            }
        }

        const reports = new Map();

        for (const value of values) {
            reports.set(
                String(value),
                this.analyze(funnel, {
                    segment: { [property]: value }
                })
            );
        }

        return reports;
    }
}

class FunnelReportingService {
    constructor(engine) {
        this.engine = engine;
    }

    async exportJSON(report, filename) {
        const content = JSON.stringify(report, null, 2);

        await fs.writeFile(filename, content, {
            encoding: "utf8",
            flag: "w"
        });

        return filename;
    }

    async generateConcurrentReports(funnel, segments) {
        const jobs = segments.map(async segment => {
            const report = this.engine.analyze(funnel, { segment });
            return { segment, report };
        });

        return Promise.all(jobs);
    }
}

function buildSampleRepository() {
    const repository = new EventRepository();

    const journeys = {
        U001: ["visit", "product_view", "add_to_cart", "checkout", "purchase"],
        U002: ["visit", "product_view", "add_to_cart", "checkout"],
        U003: ["visit", "product_view"],
        U004: ["visit", "product_view", "add_to_cart", "checkout", "purchase"],
        U005: ["visit", "product_view", "add_to_cart"],
        U006: ["visit"],
        U007: ["visit", "product_view", "add_to_cart", "checkout", "purchase"],
        U008: ["visit", "product_view", "checkout"]
    };

    const channels = [
        "organic", "paid", "organic", "paid",
        "referral", "organic", "paid", "referral"
    ];

    const devices = [
        "mobile", "desktop", "mobile", "desktop",
        "mobile", "desktop", "mobile", "desktop"
    ];

    const base = Date.UTC(2026, 10, 1, 9, 0);
    const events = [];

    let counter = 1;

    Object.entries(journeys).forEach(([userId, journey], userIndex) => {
        journey.forEach((eventName, stepIndex) => {
            events.push(new FunnelEvent({
                eventId: `E${String(counter++).padStart(4, "0")}`,
                userId,
                eventName,
                timestamp: new Date(
                    base + userIndex * 15 * 60000 + stepIndex * 3 * 60000
                ),
                properties: {
                    channel: channels[userIndex],
                    device: devices[userIndex],
                    country: userIndex % 2 === 0 ? "IN" : "US"
                }
            }));
        });
    });

    repository.addBatch(events);

    return repository;
}

async function runTests(engine, funnel) {
    const report = engine.analyze(funnel);

    console.assert(report.totalUsers === 8);
    console.assert(report.convertedUsers === 3);
    console.assert(report.steps[1].users === 7);
    console.assert(report.steps[2].users === 5);
    console.assert(report.steps[3].users === 4);
    console.assert(report.steps[4].users === 3);

    const empty = engine.analyze(funnel, {
        start: "2030-01-01T00:00:00Z"
    });

    console.assert(empty.totalUsers === 0);
    console.assert(empty.overallConversionRate === 0);

    console.log("All JavaScript funnel tests passed.");
}

async function main() {
    const repository = buildSampleRepository();

    repository.on("event:accepted", event => {
        if (event.eventName === "purchase") {
            console.log(`Purchase event accepted: ${event.userId}`);
        }
    });

    const funnel = new FunnelDefinition({
        name: "E-commerce Purchase Funnel",
        steps: [
            "visit",
            "product_view",
            "add_to_cart",
            "checkout",
            "purchase"
        ],
        conversionWindowHours: 24,
        strictOrder: true
    });

    const engine = new FunnelEngine(repository);
    const reporter = new FunnelReportingService(engine);

    const report = engine.analyze(funnel);

    console.log("\nFUNNEL ANALYTICS");
    console.log(JSON.stringify(report, null, 2));

    console.log("\nCHANNEL SEGMENTATION");

    for (const [channel, segmentReport] of engine.segmentBy(
        funnel,
        "channel"
    )) {
        console.log(
            `${channel}: ${segmentReport.convertedUsers}/` +
            `${segmentReport.totalUsers}, ` +
            `${segmentReport.overallConversionRate.toFixed(2)}%`
        );
    }

    const deviceReports = await reporter.generateConcurrentReports(
        funnel,
        [{ device: "mobile" }, { device: "desktop" }]
    );

    console.log("\nDEVICE REPORTS");

    for (const item of deviceReports) {
        console.log(
            item.segment.device,
            item.report.overallConversionRate.toFixed(2) + "%"
        );
    }

    await reporter.exportJSON(report, "funnel_report.json");

    await runTests(engine, funnel);
}

main().catch(error => {
    console.error("Funnel analytics failed:", error.message);
    process.exitCode = 1;
});
