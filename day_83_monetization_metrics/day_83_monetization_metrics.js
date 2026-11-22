"use strict";

/*
 * Monetization Metrics and Subscription Event Engine
 *
 * Node.js 18+
 *
 * Demonstrates:
 * - Event-driven subscription lifecycle
 * - MRR normalization
 * - ARPU and ARPPU
 * - ARR
 * - CAC
 * - Gross margin
 * - LTV
 * - LTV/CAC
 * - CAC payback
 * - Data validation and event processing
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class DomainError extends Error {
    constructor(message) {
        super(message);
        this.name = "DomainError";
    }
}

const BillingInterval = Object.freeze({
    MONTHLY: 1,
    QUARTERLY: 3,
    SEMIANNUAL: 6,
    ANNUAL: 12
});

const SubscriptionStatus = Object.freeze({
    ACTIVE: "ACTIVE",
    CANCELLED: "CANCELLED",
    PAST_DUE: "PAST_DUE"
});

function validateMoney(value, field) {
    if (
        typeof value !== "number" ||
        !Number.isFinite(value) ||
        value < 0
    ) {
        throw new DomainError(`${field} must be a non-negative number.`);
    }
}

function roundMoney(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
}

function divide(numerator, denominator) {
    if (denominator === 0) return null;
    return numerator / denominator;
}

class Subscription {
    constructor({
        id,
        customerId,
        price,
        intervalMonths,
        status = SubscriptionStatus.ACTIVE
    }) {
        if (!id || !customerId) {
            throw new DomainError("Subscription identifiers are required.");
        }

        validateMoney(price, "Subscription price");

        if (!Object.values(BillingInterval).includes(intervalMonths)) {
            throw new DomainError("Unsupported billing interval.");
        }

        if (!Object.values(SubscriptionStatus).includes(status)) {
            throw new DomainError("Invalid subscription status.");
        }

        this.id = id;
        this.customerId = customerId;
        this.price = price;
        this.intervalMonths = intervalMonths;
        this.status = status;
    }

    get monthlyRevenue() {
        return this.status === SubscriptionStatus.ACTIVE
            ? this.price / this.intervalMonths
            : 0;
    }

    updateStatus(status) {
        if (!Object.values(SubscriptionStatus).includes(status)) {
            throw new DomainError("Invalid subscription transition.");
        }

        const previous = this.status;
        this.status = status;

        return { previous, current: status };
    }
}

class MonetizationLedger extends EventEmitter {
    constructor() {
        super();

        this.customers = new Set();
        this.subscriptions = new Map();
        this.acquisition = {
            marketing: 0,
            sales: 0,
            newCustomers: 0
        };

        this.costs = {
            variable: 0,
            fixed: 0
        };

        this.monthlyChurnRate = null;
        this.processedEvents = new Set();
    }

    registerCustomer(customerId) {
        if (!customerId || this.customers.has(customerId)) {
            throw new DomainError("Invalid or duplicate customer.");
        }

        this.customers.add(customerId);

        this.emit("customer:registered", {
            customerId,
            timestamp: new Date().toISOString()
        });
    }

    addSubscription(subscription) {
        if (!(subscription instanceof Subscription)) {
            throw new DomainError("Expected a Subscription instance.");
        }

        if (!this.customers.has(subscription.customerId)) {
            throw new DomainError("Customer does not exist.");
        }

        if (this.subscriptions.has(subscription.id)) {
            throw new DomainError("Duplicate subscription ID.");
        }

        this.subscriptions.set(subscription.id, subscription);

        this.emit("subscription:created", {
            subscriptionId: subscription.id,
            customerId: subscription.customerId,
            mrr: subscription.monthlyRevenue
        });
    }

    changeSubscriptionStatus(subscriptionId, status) {
        const subscription = this.subscriptions.get(subscriptionId);

        if (!subscription) {
            throw new DomainError("Subscription not found.");
        }

        const change = subscription.updateStatus(status);

        this.emit("subscription:status-changed", {
            subscriptionId,
            ...change
        });
    }

    async processEvent(event) {
        if (!event || !event.id || typeof event.id !== "string") {
            throw new DomainError("Event ID is required.");
        }

        // Prevent duplicate delivery from payment providers.
        if (this.processedEvents.has(event.id)) {
            return { duplicate: true };
        }

        if (event.type === "subscription.cancel") {
            this.changeSubscriptionStatus(
                event.subscriptionId,
                SubscriptionStatus.CANCELLED
            );
        } else if (event.type === "subscription.reactivate") {
            this.changeSubscriptionStatus(
                event.subscriptionId,
                SubscriptionStatus.ACTIVE
            );
        } else {
            throw new DomainError("Unsupported event type.");
        }

        this.processedEvents.add(event.id);

        return { duplicate: false, processed: true };
    }

    setAcquisition({ marketing, sales, newCustomers }) {
        validateMoney(marketing, "Marketing spend");
        validateMoney(sales, "Sales spend");

        if (
            !Number.isInteger(newCustomers) ||
            newCustomers < 0
        ) {
            throw new DomainError("Invalid acquired customer count.");
        }

        this.acquisition = {
            marketing,
            sales,
            newCustomers
        };
    }

    setCosts({ variable, fixed }) {
        validateMoney(variable, "Variable costs");
        validateMoney(fixed, "Fixed costs");

        this.costs = { variable, fixed };
    }

    setChurnRate(rate) {
        if (
            typeof rate !== "number" ||
            !Number.isFinite(rate) ||
            rate < 0 ||
            rate > 1
        ) {
            throw new DomainError("Churn must be between 0 and 1.");
        }

        this.monthlyChurnRate = rate;
    }

    calculate() {
        const activeSubscriptions = [...this.subscriptions.values()]
            .filter(
                s => s.status === SubscriptionStatus.ACTIVE
            );

        const activeCustomers = new Set(
            activeSubscriptions.map(s => s.customerId)
        );

        const mrr = activeSubscriptions.reduce(
            (total, s) => total + s.monthlyRevenue,
            0
        );

        const payingUsers = activeCustomers.size;
        const totalUsers = this.customers.size;

        const arpu = divide(mrr, totalUsers);
        const arppu = divide(mrr, payingUsers);

        const arr = mrr * 12;

        const grossProfit = mrr - this.costs.variable;
        const grossMargin = divide(grossProfit, mrr);

        const cac = divide(
            this.acquisition.marketing +
            this.acquisition.sales,
            this.acquisition.newCustomers
        );

        const ltv =
            arppu !== null &&
            grossMargin !== null &&
            this.monthlyChurnRate !== null &&
            this.monthlyChurnRate > 0
                ? arppu * grossMargin / this.monthlyChurnRate
                : null;

        const ltvCac = divide(ltv ?? 0, cac ?? 0);

        const payback =
            arppu !== null &&
            grossMargin !== null &&
            cac !== null &&
            arppu * grossMargin > 0
                ? cac / (arppu * grossMargin)
                : null;

        return Object.freeze({
            totalUsers,
            payingUsers,
            arpu: arpu === null ? null : roundMoney(arpu),
            arppu: arppu === null ? null : roundMoney(arppu),
            mrr: roundMoney(mrr),
            arr: roundMoney(arr),
            ltv: ltv === null ? null : roundMoney(ltv),
            cac: cac === null ? null : roundMoney(cac),
            grossProfit: roundMoney(grossProfit),
            grossMargin: grossMargin === null
                ? null
                : Number(grossMargin.toFixed(4)),
            ltvCacRatio: ltvCac === null
                ? null
                : Number(ltvCac.toFixed(2)),
            cacPaybackMonths: payback === null
                ? null
                : Number(payback.toFixed(2))
        });
    }
}

class MonetizationPolicy {
    static evaluate(metrics) {
        const findings = [];

        if (metrics.ltvCacRatio === null) {
            findings.push("LTV/CAC cannot be evaluated.");
        } else if (metrics.ltvCacRatio < 1) {
            findings.push("Customer acquisition economics are negative.");
        } else if (metrics.ltvCacRatio < 3) {
            findings.push("LTV/CAC is below the conventional 3:1 reference.");
        } else {
            findings.push("LTV/CAC meets the conventional 3:1 reference.");
        }

        if (
            metrics.grossMargin !== null &&
            metrics.grossMargin < 0
        ) {
            findings.push("Variable costs exceed revenue.");
        }

        if (metrics.cacPaybackMonths !== null &&
            metrics.cacPaybackMonths > 12) {
            findings.push("CAC payback exceeds twelve months.");
        }

        return findings;
    }
}

async function main() {
    const ledger = new MonetizationLedger();

    ledger.on("customer:registered", event => {
        console.log("Customer registered:", event.customerId);
    });

    ledger.on("subscription:created", event => {
        console.log(
            `Subscription ${event.subscriptionId}: MRR ${event.mrr}`
        );
    });

    ledger.on("subscription:status-changed", event => {
        console.log(
            `Subscription ${event.subscriptionId}: ` +
            `${event.previous} -> ${event.current}`
        );
    });

    for (const id of ["C101", "C102", "C103", "C104", "C105"]) {
        ledger.registerCustomer(id);
    }

    ledger.addSubscription(new Subscription({
        id: "S101",
        customerId: "C101",
        price: 1200,
        intervalMonths: BillingInterval.ANNUAL
    }));

    ledger.addSubscription(new Subscription({
        id: "S102",
        customerId: "C102",
        price: 150,
        intervalMonths: BillingInterval.MONTHLY
    }));

    ledger.addSubscription(new Subscription({
        id: "S103",
        customerId: "C103",
        price: 600,
        intervalMonths: BillingInterval.QUARTERLY
    }));

    ledger.setAcquisition({
        marketing: 3000,
        sales: 2000,
        newCustomers: 5
    });

    ledger.setCosts({
        variable: 180,
        fixed: 1200
    });

    ledger.setChurnRate(0.05);

    await ledger.processEvent({
        id: "EVT-001",
        type: "subscription.cancel",
        subscriptionId: "S102"
    });

    // Repeated webhook delivery must not process the event twice.
    await ledger.processEvent({
        id: "EVT-001",
        type: "subscription.cancel",
        subscriptionId: "S102"
    });

    const metrics = ledger.calculate();

    console.log("\nMONETIZATION REPORT");
    console.table(metrics);

    console.log("\nPOLICY FINDINGS");
    for (const finding of MonetizationPolicy.evaluate(metrics)) {
        console.log("-", finding);
    }

    await fs.writeFile(
        "javascript_monetization_report.json",
        JSON.stringify(metrics, null, 2),
        { encoding: "utf8", flag: "w" }
    );
}

main().catch(error => {
    console.error("Monetization engine failed:", error.message);
    process.exitCode = 1;
});
