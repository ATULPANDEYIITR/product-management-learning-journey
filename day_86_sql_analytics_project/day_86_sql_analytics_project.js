"use strict";

/*
 * Product Analytics Engine
 * Node.js 18+
 *
 * Event-driven ingestion, asynchronous batch processing,
 * funnel analytics, retention, segmentation and reporting.
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const { EventEmitter } = require("node:events");

const OUTPUT_DIRECTORY = path.join(process.cwd(), "analytics_output");

const EVENT_TYPES = Object.freeze({
    VIEW: "view",
    ADD_TO_CART: "add_to_cart",
    CHECKOUT: "checkout",
    PURCHASE: "purchase",
    REFUND: "refund"
});

const FUNNEL_STAGES = Object.freeze([
    EVENT_TYPES.VIEW,
    EVENT_TYPES.ADD_TO_CART,
    EVENT_TYPES.CHECKOUT,
    EVENT_TYPES.PURCHASE
]);

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

class DuplicateEventError extends Error {
    constructor(eventId) {
        super(`Duplicate event: ${eventId}`);
        this.name = "DuplicateEventError";
    }
}

class Product {
    constructor({ id, name, category, price, cost }) {
        if (!Number.isInteger(id) || id <= 0) {
            throw new ValidationError("Invalid product ID");
        }

        if (!name?.trim() || !category?.trim()) {
            throw new ValidationError("Product name and category required");
        }

        if (
            !Number.isFinite(price) ||
            !Number.isFinite(cost) ||
            price < 0 ||
            cost < 0
        ) {
            throw new ValidationError("Invalid product financial values");
        }

        this.id = id;
        this.name = name;
        this.category = category;
        this.price = price;
        this.cost = cost;

        Object.freeze(this);
    }
}

class Customer {
    constructor({ id, registeredAt, channel, region }) {
        if (!Number.isInteger(id) || id <= 0) {
            throw new ValidationError("Invalid customer ID");
        }

        const registered = new Date(registeredAt);

        if (Number.isNaN(registered.getTime())) {
            throw new ValidationError("Invalid registration date");
        }

        this.id = id;
        this.registeredAt = registered;
        this.channel = channel;
        this.region = region;

        Object.freeze(this);
    }
}

function validateEvent(event, products, customers) {
    if (!event || typeof event !== "object") {
        throw new ValidationError("Event must be an object");
    }

    if (!Number.isInteger(event.id) || event.id <= 0) {
        throw new ValidationError("Invalid event ID");
    }

    if (!customers.has(event.customerId)) {
        throw new ValidationError("Unknown customer");
    }

    if (!products.has(event.productId)) {
        throw new ValidationError("Unknown product");
    }

    if (!Object.values(EVENT_TYPES).includes(event.type)) {
        throw new ValidationError("Unsupported event type");
    }

    const timestamp = new Date(event.timestamp);

    if (Number.isNaN(timestamp.getTime())) {
        throw new ValidationError("Invalid event timestamp");
    }

    if (
        timestamp.getTime() <
        customers.get(event.customerId).registeredAt.getTime()
    ) {
        throw new ValidationError("Event predates registration");
    }

    const quantity = event.quantity ?? 1;
    const amount = event.amount ?? 0;

    if (!Number.isInteger(quantity) || quantity <= 0) {
        throw new ValidationError("Quantity must be a positive integer");
    }

    if (!Number.isFinite(amount) || amount < 0) {
        throw new ValidationError("Invalid monetary amount");
    }

    if (event.type !== EVENT_TYPES.PURCHASE && amount !== 0) {
        throw new ValidationError(
            "Only purchase events may contain transaction amounts"
        );
    }

    return Object.freeze({
        id: event.id,
        customerId: event.customerId,
        productId: event.productId,
        type: event.type,
        timestamp,
        quantity,
        amount,
        sessionId: event.sessionId || null
    });
}

class EventStore extends EventEmitter {
    #products = new Map();
    #customers = new Map();
    #events = new Map();
    #customerIndex = new Map();
    #productIndex = new Map();

    constructor(products, customers) {
        super();

        for (const product of products) {
            this.#products.set(product.id, product);
        }

        for (const customer of customers) {
            this.#customers.set(customer.id, customer);
        }

        if (this.#products.size !== products.length) {
            throw new ValidationError("Duplicate product IDs");
        }

        if (this.#customers.size !== customers.length) {
            throw new ValidationError("Duplicate customer IDs");
        }
    }

    get products() {
        return this.#products;
    }

    get customers() {
        return this.#customers;
    }

    get size() {
        return this.#events.size;
    }

    add(event) {
        const normalized = validateEvent(
            event,
            this.#products,
            this.#customers
        );

        if (this.#events.has(normalized.id)) {
            throw new DuplicateEventError(normalized.id);
        }

        this.#events.set(normalized.id, normalized);

        if (!this.#customerIndex.has(normalized.customerId)) {
            this.#customerIndex.set(normalized.customerId, []);
        }

        if (!this.#productIndex.has(normalized.productId)) {
            this.#productIndex.set(normalized.productId, []);
        }

        this.#customerIndex.get(normalized.customerId).push(normalized);
        this.#productIndex.get(normalized.productId).push(normalized);

        this.emit("event", normalized);

        return normalized;
    }

    async ingestBatch(events, { batchSize = 1000 } = {}) {
        if (!Array.isArray(events)) {
            throw new ValidationError("Batch must be an array");
        }

        if (!Number.isInteger(batchSize) || batchSize <= 0) {
            throw new ValidationError("Invalid batch size");
        }

        let inserted = 0;
        const failures = [];

        for (let offset = 0; offset < events.length; offset += batchSize) {
            const batch = events.slice(offset, offset + batchSize);

            for (const event of batch) {
                try {
                    this.add(event);
                    inserted++;
                } catch (error) {
                    failures.push({
                        eventId: event?.id ?? null,
                        error: error.message
                    });
                }
            }

            await new Promise(resolve => setImmediate(resolve));
        }

        return {
            received: events.length,
            inserted,
            rejected: failures.length,
            failures
        };
    }

    getEvents(start, end) {
        const startTime = new Date(start).getTime();
        const endTime = new Date(end).getTime();

        if (
            Number.isNaN(startTime) ||
            Number.isNaN(endTime) ||
            startTime > endTime
        ) {
            throw new ValidationError("Invalid reporting interval");
        }

        return [...this.#events.values()].filter(event => {
            const timestamp = event.timestamp.getTime();
            return timestamp >= startTime && timestamp <= endTime;
        });
    }

    getCustomerEvents(customerId) {
        return [...(this.#customerIndex.get(customerId) || [])];
    }
}

class AnalyticsService {
    constructor(store) {
        this.store = store;
    }

    productPerformance(start, end) {
        const metrics = new Map();

        for (const event of this.store.getEvents(start, end)) {
            if (!metrics.has(event.productId)) {
                metrics.set(event.productId, {
                    views: 0,
                    cartEvents: 0,
                    purchases: 0,
                    units: 0,
                    revenue: 0,
                    buyers: new Set()
                });
            }

            const row = metrics.get(event.productId);

            switch (event.type) {
                case EVENT_TYPES.VIEW:
                    row.views++;
                    break;

                case EVENT_TYPES.ADD_TO_CART:
                    row.cartEvents++;
                    break;

                case EVENT_TYPES.PURCHASE:
                    row.purchases++;
                    row.units += event.quantity;
                    row.revenue += event.amount;
                    row.buyers.add(event.customerId);
                    break;

                case EVENT_TYPES.REFUND:
                    row.revenue -= event.amount;
                    break;
            }
        }

        return [...metrics.entries()].map(([id, row]) => {
            const product = this.store.products.get(id);
            const estimatedCost = row.units * product.cost;

            return {
                product: product.name,
                category: product.category,
                views: row.views,
                cartEvents: row.cartEvents,
                purchases: row.purchases,
                units: row.units,
                uniqueBuyers: row.buyers.size,
                revenue: Number(row.revenue.toFixed(2)),
                estimatedCost: Number(estimatedCost.toFixed(2)),
                estimatedMargin: Number(
                    (row.revenue - estimatedCost).toFixed(2)
                ),
                conversionRate: row.views
                    ? Number((row.purchases / row.views * 100).toFixed(2))
                    : 0
            };
        }).sort((a, b) => b.revenue - a.revenue);
    }

    funnel(start, end) {
        const users = new Map(
            FUNNEL_STAGES.map(stage => [stage, new Set()])
        );

        for (const event of this.store.getEvents(start, end)) {
            if (users.has(event.type)) {
                users.get(event.type).add(event.customerId);
            }
        }

        const firstCount = users.get(EVENT_TYPES.VIEW).size;
        let previous = null;

        return FUNNEL_STAGES.map(stage => {
            const count = users.get(stage).size;

            const result = {
                stage,
                users: count,
                conversionFromPrevious: previous
                    ? Number((count / previous * 100).toFixed(2))
                    : null,
                conversionFromFirst: firstCount
                    ? Number((count / firstCount * 100).toFixed(2))
                    : null
            };

            previous = count;
            return result;
        });
    }

    orderedSessionFunnel(start, end) {
        const sessions = new Map();

        for (const event of this.store.getEvents(start, end)) {
            if (!event.sessionId) continue;

            if (!sessions.has(event.sessionId)) {
                sessions.set(event.sessionId, []);
            }

            sessions.get(event.sessionId).push(event);
        }

        const counts = new Map(
            FUNNEL_STAGES.map(stage => [stage, 0])
        );

        for (const events of sessions.values()) {
            events.sort((a, b) => a.timestamp - b.timestamp);

            let index = 0;

            for (const event of events) {
                if (
                    index < FUNNEL_STAGES.length &&
                    event.type === FUNNEL_STAGES[index]
                ) {
                    index++;
                }
            }

            FUNNEL_STAGES.forEach((stage, i) => {
                if (index > i) {
                    counts.set(stage, counts.get(stage) + 1);
                }
            });
        }

        return Object.fromEntries(counts);
    }

    retention(start, end) {
        const cohortMembers = new Map();
        const monthlyActivity = new Map();

        const monthKey = date => {
            const d = new Date(date);
            return `${d.getUTCFullYear()}-${String(
                d.getUTCMonth() + 1
            ).padStart(2, "0")}`;
        };

        for (const customer of this.store.customers.values()) {
            if (
                customer.registeredAt >= new Date(start) &&
                customer.registeredAt <= new Date(end)
            ) {
                const key = monthKey(customer.registeredAt);

                if (!cohortMembers.has(key)) {
                    cohortMembers.set(key, new Set());
                }

                cohortMembers.get(key).add(customer.id);
            }
        }

        for (const event of this.store.getEvents(start, end)) {
            const key = monthKey(event.timestamp);

            if (!monthlyActivity.has(key)) {
                monthlyActivity.set(key, new Set());
            }

            monthlyActivity.get(key).add(event.customerId);
        }

        const results = [];

        for (const [cohort, members] of cohortMembers) {
            const [year, month] = cohort.split("-").map(Number);
            const cohortIndex = year * 12 + month - 1;
            const endDate = new Date(end);
            const endIndex = endDate.getUTCFullYear() * 12
                + endDate.getUTCMonth();

            for (let index = cohortIndex; index <= endIndex; index++) {
                const key = `${Math.floor(index / 12)}-${String(
                    index % 12 + 1
                ).padStart(2, "0")}`;

                const active = [...members].filter(id =>
                    monthlyActivity.get(key)?.has(id)
                ).length;

                results.push({
                    cohort,
                    monthNumber: index - cohortIndex,
                    cohortSize: members.size,
                    activeCustomers: active,
                    retentionRate: Number(
                        (active / members.size * 100).toFixed(2)
                    )
                });
            }
        }

        return results;
    }

    segmentation(referenceDate) {
        const reference = new Date(referenceDate);

        if (Number.isNaN(reference.getTime())) {
            throw new ValidationError("Invalid reference date");
        }

        const output = [];

        for (const customer of this.store.customers.values()) {
            const purchases = this.store.getCustomerEvents(customer.id)
                .filter(event =>
                    event.timestamp <= reference &&
                    event.type === EVENT_TYPES.PURCHASE
                );

            const refunds = this.store.getCustomerEvents(customer.id)
                .filter(event =>
                    event.timestamp <= reference &&
                    event.type === EVENT_TYPES.REFUND
                );

            if (!purchases.length) {
                output.push({
                    customerId: customer.id,
                    segment: "No Purchase",
                    recency: null,
                    frequency: 0,
                    monetary: 0
                });
                continue;
            }

            const latest = Math.max(
                ...purchases.map(e => e.timestamp.getTime())
            );

            const recency = Math.floor(
                (reference.getTime() - latest) / 86400000
            );

            const frequency = purchases.length;

            const monetary = purchases.reduce(
                (sum, event) => sum + event.amount, 0
            ) - refunds.reduce(
                (sum, event) => sum + event.amount, 0
            );

            if (monetary < 0) {
                throw new ValidationError(
                    `Refunds exceed purchases for customer ${customer.id}`
                );
            }

            let segment;

            if (recency <= 30 && frequency >= 3 && monetary >= 5000) {
                segment = "Champions";
            } else if (recency <= 60 && frequency >= 2) {
                segment = "Loyal Customers";
            } else if (recency <= 30 && frequency === 1) {
                segment = "Recent Customers";
            } else if (recency > 90 && frequency >= 2) {
                segment = "At Risk";
            } else if (recency > 180) {
                segment = "Dormant";
            } else {
                segment = "Regular Customers";
            }

            output.push({
                customerId: customer.id,
                segment,
                recency,
                frequency,
                monetary: Number(monetary.toFixed(2))
            });
        }

        return output;
    }

    channelPerformance(start, end) {
        const metrics = new Map();

        for (const event of this.store.getEvents(start, end)) {
            const customer = this.store.customers.get(event.customerId);

            if (!metrics.has(customer.channel)) {
                metrics.set(customer.channel, {
                    visitors: new Set(),
                    buyers: new Set(),
                    revenue: 0
                });
            }

            const row = metrics.get(customer.channel);

            if (event.type === EVENT_TYPES.VIEW) {
                row.visitors.add(customer.id);
            }

            if (event.type === EVENT_TYPES.PURCHASE) {
                row.buyers.add(customer.id);
                row.revenue += event.amount;
            }

            if (event.type === EVENT_TYPES.REFUND) {
                row.revenue -= event.amount;
            }
        }

        return [...metrics.entries()].map(([channel, row]) => ({
            channel,
            visitors: row.visitors.size,
            buyers: row.buyers.size,
            revenue: Number(row.revenue.toFixed(2)),
            conversionRate: row.visitors.size
                ? Number((
                    row.buyers.size / row.visitors.size * 100
                ).toFixed(2))
                : 0
        })).sort((a, b) => b.revenue - a.revenue);
    }
}

class ReportExporter {
    static async writeJSON(filename, data) {
        await fs.mkdir(OUTPUT_DIRECTORY, { recursive: true });

        const destination = path.join(
            OUTPUT_DIRECTORY,
            path.basename(filename)
        );

        const temporary = `${destination}.${crypto.randomUUID()}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(data, null, 2),
                { encoding: "utf8", flag: "wx" }
            );

            await fs.rename(temporary, destination);
        } catch (error) {
            await fs.rm(temporary, { force: true });
            throw error;
        }
    }

    static toCSV(rows) {
        if (!rows.length) return "";

        const columns = Object.keys(rows[0]);

        const escape = value => {
            if (value === null || value === undefined) return "";

            const text = String(value);

            if (/^[=+\-@]/.test(text)) {
                return `"'\u200B${text.replaceAll('"', '""')}"`;
            }

            return `"${text.replaceAll('"', '""')}"`;
        };

        return [
            columns.map(escape).join(","),
            ...rows.map(row =>
                columns.map(column => escape(row[column])).join(",")
            )
        ].join("\n");
    }
}

function createSampleDataset() {
    const products = [
        new Product({
            id: 101, name: "Laptop Pro",
            category: "Electronics", price: 1200, cost: 850
        }),
        new Product({
            id: 102, name: "Wireless Mouse",
            category: "Accessories", price: 35, cost: 12
        }),
        new Product({
            id: 103, name: "Mechanical Keyboard",
            category: "Accessories", price: 95, cost: 48
        }),
        new Product({
            id: 104, name: "Smart Watch",
            category: "Wearables", price: 250, cost: 140
        }),
        new Product({
            id: 105, name: "USB-C Hub",
            category: "Accessories", price: 55, cost: 22
        })
    ];

    const customers = [
        new Customer({
            id: 1, registeredAt: "2026-01-05",
            channel: "Organic", region: "North"
        }),
        new Customer({
            id: 2, registeredAt: "2026-01-12",
            channel: "Paid Search", region: "South"
        }),
        new Customer({
            id: 3, registeredAt: "2026-02-03",
            channel: "Social", region: "East"
        }),
        new Customer({
            id: 4, registeredAt: "2026-02-15",
            channel: "Organic", region: "West"
        }),
        new Customer({
            id: 5, registeredAt: "2026-03-01",
            channel: "Referral", region: "North"
        }),
        new Customer({
            id: 6, registeredAt: "2026-03-10",
            channel: "Paid Search", region: "South"
        }),
        new Customer({
            id: 7, registeredAt: "2026-04-02",
            channel: "Social", region: "East"
        }),
        new Customer({
            id: 8, registeredAt: "2026-04-15",
            channel: "Referral", region: "West"
        })
    ];

    const raw = [
        [1, 1, 101, "view", 0, 0],
        [2, 1, 101, "add_to_cart", 1, 0],
        [3, 1, 101, "checkout", 2, 0],
        [4, 1, 101, "purchase", 3, 1200],
        [5, 1, 102, "purchase", 40, 35],
        [6, 1, 103, "purchase", 60, 95],
        [7, 2, 102, "view", 1, 0],
        [8, 2, 102, "add_to_cart", 2, 0],
        [9, 2, 102, "purchase", 4, 35],
        [10, 2, 102, "refund", 10, 35],
        [11, 3, 104, "view", 5, 0],
        [12, 3, 104, "purchase", 7, 250],
        [13, 4, 103, "view", 12, 0],
        [14, 4, 103, "add_to_cart", 13, 0],
        [15, 4, 103, "checkout", 14, 0],
        [16, 4, 103, "purchase", 15, 95],
        [17, 5, 105, "view", 20, 0],
        [18, 5, 105, "purchase", 22, 55],
        [19, 6, 101, "view", 25, 0],
        [20, 6, 101, "add_to_cart", 26, 0],
        [21, 7, 104, "view", 28, 0],
        [22, 8, 102, "view", 29, 0],
        [23, 8, 102, "purchase", 30, 35]
    ];

    const events = raw.map(
        ([id, customerId, productId, type, day, amount]) => ({
            id,
            customerId,
            productId,
            type,
            timestamp: new Date(
                Date.UTC(2026, 3, 1 + day, 10)
            ),
            amount,
            quantity: 1,
            sessionId: `S-${customerId}-${Math.floor(day / 7)}`
        })
    );

    return { products, customers, events };
}

async function main() {
    const { products, customers, events } = createSampleDataset();

    const store = new EventStore(products, customers);

    let eventNotifications = 0;

    store.on("event", () => eventNotifications++);

    const ingestion = await store.ingestBatch(events, {
        batchSize: 5
    });

    const analytics = new AnalyticsService(store);

    const start = "2026-04-01T00:00:00.000Z";
    const end = "2026-06-30T23:59:59.999Z";

    const reports = {
        ingestion,
        eventNotifications,
        productPerformance: analytics.productPerformance(start, end),
        conversionFunnel: analytics.funnel(start, end),
        orderedSessionFunnel: analytics.orderedSessionFunnel(start, end),
        retention: analytics.retention(
            "2026-01-01T00:00:00.000Z", end
        ),
        segmentation: analytics.segmentation(end),
        channelPerformance: analytics.channelPerformance(start, end)
    };

    if (store.size !== events.length) {
        throw new Error("Event ingestion count mismatch");
    }

    if (reports.conversionFunnel[0].users <
        reports.conversionFunnel[3].users) {
        throw new Error("Invalid funnel ordering");
    }

    try {
        store.add(events[0]);
        throw new Error("Duplicate event test failed");
    } catch (error) {
        if (!(error instanceof DuplicateEventError)) {
            throw error;
        }
    }

    await ReportExporter.writeJSON("analytics.json", reports);

    await ReportExporter.writeJSON(
        "segmentation.json",
        reports.segmentation
    );

    await fs.writeFile(
        path.join(OUTPUT_DIRECTORY, "products.csv"),
        ReportExporter.toCSV(reports.productPerformance),
        "utf8"
    );

    console.log(JSON.stringify(reports, null, 2));
    console.log("\nAnalytics execution completed.");
}

main().catch(error => {
    console.error("Analytics failure:", error.message);
    process.exitCode = 1;
});
