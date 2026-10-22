'use strict';

/*
 * Technical Architecture event-driven simulation.
 *
 * The model focuses on architecture rather than syntax:
 * monolithic boundaries, service boundaries, databases, cache-aside reads,
 * asynchronous queues, failure isolation, and horizontal scaling.
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require('events');
const crypto = require('crypto');

class ValidationError extends Error {}
class ServiceUnavailableError extends Error {}
class DatabaseError extends Error {}

function assertInteger(value, field, minimum = 1) {
    if (!Number.isInteger(value) || value < minimum) {
        throw new ValidationError(`${field} must be an integer >= ${minimum}`);
    }
}

function assertPositiveNumber(value, field) {
    if (!Number.isFinite(value) || value <= 0) {
        throw new ValidationError(`${field} must be a positive number`);
    }
}

class InMemoryDatabase {
    constructor(name) {
        this.name = name;
        this.tables = new Map();
        this.reads = 0;
        this.writes = 0;
        this.available = true;
    }

    table(name) {
        if (!this.tables.has(name)) {
            this.tables.set(name, new Map());
        }
        return this.tables.get(name);
    }

    ensureAvailable() {
        if (!this.available) {
            throw new DatabaseError(`${this.name} is unavailable`);
        }
    }

    insert(tableName, id, row) {
        this.ensureAvailable();

        const table = this.table(tableName);
        if (table.has(id)) {
            throw new ValidationError(`Duplicate key ${id} in ${tableName}`);
        }

        table.set(id, structuredClone(row));
        this.writes += 1;
    }

    get(tableName, id) {
        this.ensureAvailable();

        this.reads += 1;
        const row = this.table(tableName).get(id);
        return row ? structuredClone(row) : null;
    }

    update(tableName, id, patch) {
        this.ensureAvailable();

        const table = this.table(tableName);
        const existing = table.get(id);

        if (!existing) {
            throw new ValidationError(`Unknown record ${id}`);
        }

        table.set(id, { ...existing, ...patch });
        this.writes += 1;
    }

    values(tableName) {
        this.ensureAvailable();
        const rows = [...this.table(tableName).values()];
        this.reads += rows.length;
        return rows.map(structuredClone);
    }
}

class TTLCache {
    constructor({ capacity = 100, ttlMs = 60_000 } = {}) {
        assertInteger(capacity, 'capacity');
        assertInteger(ttlMs, 'ttlMs');

        this.capacity = capacity;
        this.ttlMs = ttlMs;
        this.entries = new Map();
        this.hits = 0;
        this.misses = 0;
    }

    get(key) {
        const entry = this.entries.get(key);

        if (!entry) {
            this.misses += 1;
            return null;
        }

        if (entry.expiresAt <= Date.now()) {
            this.entries.delete(key);
            this.misses += 1;
            return null;
        }

        this.hits += 1;
        return structuredClone(entry.value);
    }

    set(key, value) {
        if (!this.entries.has(key) && this.entries.size >= this.capacity) {
            const oldestKey = this.entries.keys().next().value;
            this.entries.delete(oldestKey);
        }

        this.entries.set(key, {
            value: structuredClone(value),
            expiresAt: Date.now() + this.ttlMs
        });
    }

    invalidate(key) {
        this.entries.delete(key);
    }

    get hitRatio() {
        const total = this.hits + this.misses;
        return total === 0 ? 0 : this.hits / total;
    }
}

class EventQueue extends EventEmitter {
    constructor(name, maxRetries = 3) {
        super();

        assertInteger(maxRetries, 'maxRetries');
        this.name = name;
        this.maxRetries = maxRetries;
        this.messages = [];
        this.deadLetters = [];
    }

    publish(message) {
        this.messages.push({
            id: crypto.randomUUID(),
            payload: structuredClone(message),
            attempts: 0
        });

        this.emit('published', message);
    }

    async drain(handler) {
        while (this.messages.length > 0) {
            const message = this.messages.shift();
            message.attempts += 1;

            try {
                await handler(message.payload);
            } catch (error) {
                if (message.attempts >= this.maxRetries) {
                    this.deadLetters.push({
                        ...message,
                        failure: error.message
                    });
                    this.emit('dead-letter', message);
                } else {
                    this.messages.push(message);
                }
            }
        }
    }
}

class CustomerService {
    constructor(database, cache) {
        this.database = database;
        this.cache = cache;
        this.healthy = true;
        this.requests = 0;
    }

    ensureHealthy() {
        if (!this.healthy) {
            throw new ServiceUnavailableError('Customer service is unavailable');
        }
    }

    async findCustomer(customerId) {
        assertInteger(customerId, 'customerId');
        this.requests += 1;
        this.ensureHealthy();

        const key = `customer:${customerId}`;
        const cached = this.cache.get(key);

        if (cached !== null) {
            return cached;
        }

        const customer = this.database.get('customers', customerId);

        if (!customer) {
            throw new ValidationError(`Customer ${customerId} not found`);
        }

        this.cache.set(key, customer);
        return customer;
    }
}

class OrderService {
    constructor(database, queue, customerService) {
        this.database = database;
        this.queue = queue;
        this.customerService = customerService;
        this.healthy = true;
    }

    ensureHealthy() {
        if (!this.healthy) {
            throw new ServiceUnavailableError('Order service is unavailable');
        }
    }

    async createOrder(customerId, amount) {
        assertInteger(customerId, 'customerId');
        assertPositiveNumber(amount, 'amount');
        this.ensureHealthy();

        await this.customerService.findCustomer(customerId);

        const existing = this.database.values('orders');
        const nextId = existing.length === 0
            ? 1
            : Math.max(...existing.map(order => order.id)) + 1;

        const order = {
            id: nextId,
            customerId,
            amount: Number(amount.toFixed(2)),
            status: 'CREATED',
            createdAt: new Date().toISOString()
        };

        this.database.insert('orders', nextId, order);

        await Promise.resolve(
            this.queue.publish({
                type: 'order.created',
                orderId: nextId,
                customerId,
                amount: order.amount
            })
        );

        return order;
    }
}

class MonolithApplication {
    constructor() {
        this.database = new InMemoryDatabase('monolith-db');
        this.cache = new TTLCache();
        this.queue = new EventQueue('monolith-events');

        this.customers = new CustomerService(this.database, this.cache);
        this.orders = new OrderService(
            this.database,
            this.queue,
            this.customers
        );
    }

    seed() {
        this.database.insert('customers', 1, {
            id: 1,
            name: 'Asha',
            tier: 'PREMIUM'
        });

        this.database.insert('customers', 2, {
            id: 2,
            name: 'Ravi',
            tier: 'STANDARD'
        });
    }

    async placeOrder(customerId, amount) {
        try {
            const order = await this.orders.createOrder(customerId, amount);

            return {
                success: true,
                architecture: 'MONOLITH',
                order
            };
        } catch (error) {
            return {
                success: false,
                architecture: 'MONOLITH',
                error: error.message
            };
        }
    }
}

class MicroservicesApplication {
    constructor() {
        /*
         * Separate databases reinforce ownership boundaries.
         * Services communicate through explicit contracts rather than sharing
         * application-level database tables.
         */
        this.customerDatabase = new InMemoryDatabase('customer-db');
        this.orderDatabase = new InMemoryDatabase('order-db');

        this.customerCache = new TTLCache({
            capacity: 100,
            ttlMs: 60_000
        });

        this.queue = new EventQueue('order-events', 3);

        this.customers = new CustomerService(
            this.customerDatabase,
            this.customerCache
        );

        this.orders = new OrderService(
            this.orderDatabase,
            this.queue,
            this.customers
        );
    }

    seed() {
        this.customerDatabase.insert('customers', 1, {
            id: 1,
            name: 'Asha',
            tier: 'PREMIUM'
        });

        this.customerDatabase.insert('customers', 2, {
            id: 2,
            name: 'Ravi',
            tier: 'STANDARD'
        });
    }

    async placeOrder(customerId, amount) {
        try {
            const order = await this.orders.createOrder(customerId, amount);

            return {
                success: true,
                architecture: 'MICROSERVICES',
                order
            };
        } catch (error) {
            return {
                success: false,
                architecture: 'MICROSERVICES',
                error: error.message
            };
        }
    }
}

function calculateHorizontalScaling(requestsPerSecond, capacityPerInstance = 100) {
    assertPositiveNumber(requestsPerSecond, 'requestsPerSecond');
    assertPositiveNumber(capacityPerInstance, 'capacityPerInstance');

    return {
        requestedRps: requestsPerSecond,
        instances: Math.max(
            1,
            Math.ceil(requestsPerSecond / capacityPerInstance)
        ),
        nominalCapacity:
            Math.max(1, Math.ceil(requestsPerSecond / capacityPerInstance))
            * capacityPerInstance
    };
}

async function demonstrateQueueRetry() {
    const queue = new EventQueue('billing-events', 3);

    queue.publish({
        type: 'payment.capture',
        paymentId: 9001
    });

    let attempts = 0;

    await queue.drain(async () => {
        attempts += 1;
        throw new Error('External payment provider timeout');
    });

    return {
        attempts,
        deadLetters: queue.deadLetters.length
    };
}

async function main() {
    const monolith = new MonolithApplication();
    monolith.seed();

    console.log('Monolith:');
    console.log(await monolith.placeOrder(1, 2499.50));

    const microservices = new MicroservicesApplication();
    microservices.seed();

    microservices.queue.on('published', event => {
        console.log('Event published:', event.type);
    });

    microservices.queue.on('dead-letter', message => {
        console.log('Dead-lettered event:', message.payload.type);
    });

    console.log('\nMicroservices:');
    console.log(await microservices.placeOrder(1, 2499.50));

    await microservices.queue.drain(async event => {
        if (event.type !== 'order.created') {
            throw new ValidationError(`Unsupported event: ${event.type}`);
        }

        console.log(
            `Asynchronous consumer processed order ${event.orderId}`
        );
    });

    console.log('\nCache behavior:');
    await microservices.customers.findCustomer(1);
    await microservices.customers.findCustomer(1);
    console.log({
        hits: microservices.customerCache.hits,
        misses: microservices.customerCache.misses,
        hitRatio: microservices.customerCache.hitRatio
    });

    console.log('\nFailure isolation:');
    microservices.customers.healthy = false;
    console.log(await microservices.placeOrder(1, 500));

    console.log('\nQueue retry behavior:');
    console.log(await demonstrateQueueRetry());

    console.log('\nScaling:');
    for (const rps of [50, 100, 101, 250, 1000]) {
        console.log(calculateHorizontalScaling(rps));
    }

    console.log('\nDatabase ownership:');
    console.log({
        customerDatabase: microservices.customerDatabase.name,
        orderDatabase: microservices.orderDatabase.name
    });
}

main().catch(error => {
    console.error('Fatal architecture simulation error:', error);
    process.exitCode = 1;
});
