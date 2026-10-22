# Technical Architecture: Monoliths, Microservices, Services, Databases, Caching, Queues, and Scalability

## Architecture Scope

This artifact models the main structural choices involved in building a production-oriented application architecture:

| Area | Architectural responsibility |
|---|---|
| Monolith | Groups application capabilities into one deployable unit |
| Microservices | Separates capabilities into independently deployable service boundaries |
| Services | Own domain behavior and expose explicit application contracts |
| Databases | Persist domain state and define data ownership boundaries |
| Caching | Reduces repeated reads and protects persistent storage from avoidable load |
| Queues | Decouple producers from asynchronous consumers |
| Scalability | Increases capacity by changing resources or adding application instances |

These mechanisms solve different problems. A monolith or microservice architecture determines deployment and ownership boundaries. A service expresses domain behavior inside those boundaries. A database provides durable state. A cache optimizes access to state. A queue changes the timing and coupling of work. Scalability determines how the system responds when workload grows.

A useful conceptual relationship is:

`Client -> Application Boundary -> Service -> Database`

For operations that do not need immediate completion:

`Service -> Queue -> Consumer -> Downstream Service`

For frequently requested read data:

`Service -> Cache -> Database`

For horizontal scaling:

`Load Balancer -> Instance 1`
`               -> Instance 2`
`               -> Instance 3`

Scaling the application layer is usually simpler when instances remain stateless and durable state is held in external systems such as databases, caches, or message brokers.

---

## Monolithic Architecture

A monolith places multiple application capabilities inside one deployable application boundary.

In the Python implementation, `Monolith` contains both `CustomerService` and `OrderService`. They use one `Database`, one cache, and one event queue. The implementation still separates domain responsibilities through classes, but deployment remains unified.

The important distinction is between logical separation and deployment separation. Two classes are not automatically two microservices. A microservice normally has an independently deployable runtime boundary, its own operational lifecycle, and a defined communication contract.

A monolith can be a sound architecture when:

- the domain is relatively small;
- transaction boundaries are strongly connected;
- operational simplicity is more valuable than independent deployment;
- the team is small;
- independent scaling is not yet important;
- the system benefits from local function calls instead of distributed communication.

The main operational advantage is reduced distributed-system complexity. A function call inside the process does not require network serialization, service discovery, network authentication, retries, or distributed tracing.

The principal limitation is coupling. A change to one part of a monolith may require rebuilding and redeploying the entire application. A resource-intensive component can also consume capacity shared with unrelated functionality.

---

## Microservices Architecture

Microservices divide an application into independently deployable service boundaries.

The examples use two domains:

- `CustomerService` owns customer behavior.
- `OrderService` owns order behavior.

The microservice simulation deliberately gives these services separate databases:

`customer-service -> customer-db`

`order-service -> order-db`

This models data ownership rather than merely putting two logical tables into one shared schema.

A service boundary should be based on domain responsibility rather than arbitrary class size. A service becomes useful when it has a coherent business capability, a meaningful operational boundary, and a contract that can evolve independently.

The microservices model introduces costs that do not exist in the same form inside a monolith:

- network failures;
- request timeouts;
- retries;
- partial availability;
- serialization and schema compatibility;
- distributed tracing;
- service discovery;
- independent deployment coordination;
- operational monitoring;
- data consistency across service boundaries.

Microservices therefore should not be treated as an automatic improvement over a monolith. They exchange some forms of application coupling for distributed-system complexity.

---

## Service Boundaries

A service is responsible for a domain capability rather than simply representing a database table.

The implementations make `CustomerService` responsible for:

- customer retrieval;
- customer validation;
- cache-aside reads;
- customer-service availability.

`OrderService` is responsible for:

- validating order input;
- verifying that the customer exists;
- creating the order;
- assigning order state;
- publishing an order-created event.

The order workflow demonstrates a synchronous dependency:

`OrderService -> CustomerService`

The dependency is synchronous because the order cannot safely be created for a customer that does not exist.

The implementation also demonstrates asynchronous work:

`OrderService -> Queue -> Event Consumer`

The event consumer does not need to execute before the order creation request can return.

This distinction is important. Synchronous communication creates a direct availability dependency. Asynchronous communication reduces temporal coupling but introduces delivery, retry, ordering, and idempotency concerns.

---

## Database Ownership

The database model treats persistent state as an ownership concern.

In the microservice architecture:

| Domain | Owning service | Database |
|---|---|---|
| Customers | Customer Service | Customer DB |
| Orders | Order Service | Order DB |

The C++, Java, Python, and JavaScript implementations all preserve this conceptual boundary.

The PostgreSQL model makes the ownership explicit through `service`, `database_instance`, `customer`, and `customer_order`.

A database is not simply a storage implementation. Its location and ownership affect:

- transaction boundaries;
- authorization;
- schema evolution;
- backup responsibilities;
- availability;
- scaling;
- data consistency;
- service coupling.

Sharing a database between supposedly independent services can create hidden coupling. A service may appear independent at the API layer while remaining dependent on another service's tables, migrations, indexes, or transaction behavior.

Database-per-service is not a mandatory rule for every system. It is an architectural technique for enforcing stronger ownership boundaries.

---

## Caching

The implementations use the cache-aside pattern.

The read sequence is:

`Service`
`  |`
`  +-- Cache hit --> return cached value`
`  |`
`  +-- Cache miss --> Database`
`                     |`
`                     +--> populate cache`
`                     +--> return value`

The Python `Cache`, JavaScript `TTLCache`, C++ `Cache`, and Java `CacheManager` all implement this basic mechanism.

A cache entry has a finite lifetime. The examples use TTL expiration to prevent an old value from remaining indefinitely.

Cache behavior is evaluated through:

- hits;
- misses;
- hit ratio;
- capacity;
- expiration;
- invalidation.

The cache must not be treated as the authoritative source of durable state. The database remains authoritative in the model.

When customer data changes, an associated cache entry should be invalidated or refreshed. The Python implementation explicitly invalidates the customer entry after a tier change.

Caching introduces failure and correctness considerations:

- stale data;
- cache stampedes;
- eviction;
- memory limits;
- serialization overhead;
- inconsistent invalidation;
- sensitive data exposure;
- tenant isolation;
- cache availability.

A high cache hit ratio is useful only when the cached data is correct enough for the operation. Caching data that must always be current can create correctness problems even when performance improves.

---

## Queues and Asynchronous Processing

The queue implementations represent asynchronous communication.

The order service publishes an event after creating an order:

`order.created`

The consumer processes the event separately.

This removes the need for the producer to execute every downstream operation synchronously.

Queues are useful when:

- work can happen after the user-facing operation;
- downstream processing is slower than request handling;
- temporary downstream failures should not immediately fail the producer;
- workload should be buffered;
- consumers need independent scaling.

The queue implementations include retry behavior.

The processing lifecycle is:

`pending -> processing attempt -> success`

or:

`pending -> retry -> retry -> dead-letter`

A dead-letter queue or dead-letter collection prevents permanently failing messages from blocking normal processing indefinitely.

A production queue consumer should normally be idempotent. If a message is delivered twice, the resulting business state should not incorrectly be applied twice.

For example, an order notification consumer could maintain a unique notification identifier so that repeated delivery does not produce duplicate notifications.

---

## Queue Consistency and the Outbox Concern

The application-level workflow has two separate operations:

`Database write`
`Queue publish`

If the database write succeeds but queue publication fails, the database contains an order without the corresponding event.

If queue publication succeeds but the database transaction later fails, the event can describe an order that does not exist.

The PostgreSQL implementation models an outbox-style direction by creating the event inside the same database transaction as the order-related workflow.

A production implementation can use:

`Business Transaction -> Outbox Row -> Reliable Publisher -> Message Broker`

This reduces the database/broker dual-write problem.

The outbox row is still not the same thing as successful external delivery. A separate publisher must safely retry publication and record delivery state.

---

## Scalability

Scalability concerns how system capacity changes as workload increases.

The examples use a simple planning model:

`required instances = ceiling(request rate / capacity per instance)`

For an assumed capacity of 100 requests per second:

| Request rate | Required instances |
|---:|---:|
| 50 RPS | 1 |
| 100 RPS | 1 |
| 101 RPS | 2 |
| 250 RPS | 3 |
| 1000 RPS | 10 |

This is an architectural calculation, not a performance benchmark. Real capacity depends on CPU, memory, database latency, network latency, request complexity, concurrency, downstream services, and workload distribution.

Horizontal scaling requires the application instances to be sufficiently independent. Shared in-process state can prevent safe scaling.

For example, if authentication sessions are stored only in process memory:

`Client -> Instance A -> Session`

A later request routed to Instance B may not find that session.

Externalizing state makes scaling easier:

`Client -> Load Balancer`
`              |`
`              +-> Instance A`
`              +-> Instance B`
`              +-> Instance C`
`                     |`
`                     +-> Shared durable systems`

Databases and caches can themselves become bottlenecks. Scaling the application tier does not automatically scale the database.

---

## Python Implementation

The Python script uses standard-library data structures to simulate the architecture.

### Domain model

`Request` and `Response` represent application-level request and response boundaries.

`Service` provides common service availability behavior.

`CustomerService` implements customer lookup and cache-aside reads.

`OrderService` validates a customer before creating an order and publishes an event.

### Database model

`Database` stores separate logical tables and tracks read/write counts.

The implementation validates duplicate keys and explicitly raises failures when the simulated database is unavailable.

### Cache model

`Cache` uses TTL expiration and bounded capacity. It records hits and misses so the simulation can calculate a hit ratio.

The implementation uses lazy expiration. Expired entries are removed when accessed rather than through a background cleanup thread.

### Queue model

`MessageQueue` stores messages until consumers acknowledge them through successful handler execution.

Failures cause retries. Messages that exceed the retry limit are moved into `dead_letters`.

### Architectural comparison

The script runs both a monolithic application and a microservices platform against the same business scenario. This makes the architectural distinction visible without pretending that the business operation itself changes.

It also demonstrates service failure, cache behavior, asynchronous events, queue failures, and scaling calculations.

---

## JavaScript Implementation

The JavaScript implementation emphasizes asynchronous and event-driven behavior.

`EventQueue` extends Node.js `EventEmitter`. Queue publication emits an event, while `drain()` asynchronously invokes the consumer.

The implementation uses `async` and `await` around service operations and queue processing to model event-driven application behavior.

`InMemoryDatabase` maintains explicit table maps.

`TTLCache` provides bounded cache-aside behavior with expiration.

`CustomerService` and `OrderService` use separate database instances in the microservices model.

The script also uses `crypto.randomUUID()` for unique queue message identifiers. This is preferable to constructing identifiers from timestamps or predictable counters when an identifier must remain unique across concurrent producers.

The JavaScript version deliberately does not require an HTTP framework. The architecture is modeled directly so that the domain boundaries remain visible instead of being hidden behind framework configuration.

---

## C++ Implementation

The C++ implementation presents the architecture as a deterministic systems case study.

The database uses typed domain objects:

- `Customer`
- `Order`
- `Event`

`std::optional` represents a lookup that may not find a record.

`Cache` stores customer values with expiration times.

`MessageQueue` uses `std::deque` to preserve event processing order within the simulation.

`OrderService` receives references to its dependencies. This makes ownership explicit and avoids global mutable state.

The C++ implementation also models failure isolation by disabling the customer service after a successful workflow. A subsequent order fails because the synchronous customer dependency is unavailable.

This illustrates a key distributed-system property:

`Service A available + Service B unavailable != System fully available`

If a request requires both services synchronously, the dependency can propagate availability failures.

---

## Java Implementation

The Java implementation is intentionally enterprise-oriented.

Java records represent immutable domain values:

- `Customer`
- `Order`
- `OrderCreatedEvent`
- `ScalingPlan`

Enums model explicit domain states such as `CustomerTier` and `OrderStatus`.

`Order.transitionTo()` enforces legal state transitions instead of allowing arbitrary mutation.

The state machine is:

`CREATED -> PROCESSING -> COMPLETED`

or:

`CREATED -> FAILED`

and:

`PROCESSING -> FAILED`

Terminal states cannot transition again.

This is stronger than storing a string and changing it without validation because invalid business transitions become domain-level failures.

The repository interface defines a persistence contract, while `CustomerRepository` and `OrderRepository` implement separate storage ownership.

`CustomerService` combines repository access with cache-aside behavior.

`OrderService` explicitly depends on `CustomerService` for customer validation and publishes an `OrderCreatedEvent` after persistence.

The implementation also represents queue retry and dead-letter behavior without external libraries.

---

## PostgreSQL Implementation

The SQL artifact models the architecture as a relational operational system.

The schema contains explicit tables for:

- architectures;
- services;
- databases;
- cache policies;
- customers;
- cache observations;
- requests;
- orders;
- queues;
- queue events;
- queue failures.

Foreign keys enforce relationships between architectural entities.

Check constraints prevent invalid states such as:

- non-positive cache capacity;
- non-positive TTL;
- invalid monetary amounts;
- negative retry counts;
- inconsistent event processing timestamps;
- empty service names.

Indexes are limited to query paths that have a clear workload relationship, including customer-service ownership, order lookup by customer and status, pending queue events, request reporting, and cache observation history.

The `touch_order_timestamp()` trigger keeps order modification timestamps synchronized automatically.

The `create_order_event()` function encapsulates queue event creation and verifies that the order event queue is available.

The `service_can_accept_requests()` function exposes an explicit service availability rule.

Views provide operational reporting for:

- service and database inventory;
- cache performance;
- queue health;
- order status totals.

The CTE queries demonstrate aggregation without embedding business logic in application code alone.

---

## Failure Conditions

### Service failure

A service can be healthy, degraded, or unavailable.

A synchronous dependency means an unavailable downstream service can cause the current request to fail.

The examples intentionally demonstrate:

`Order request -> Order Service -> Customer Service DOWN`

The order is rejected because customer validation is mandatory.

### Database failure

Database availability is distinct from service availability.

A healthy service with an unavailable database cannot necessarily serve uncached reads or persistent writes.

The cache can reduce database reads, but it does not eliminate the database's role as the durable source of truth.

### Cache failure

A cache miss is not normally a business failure.

The normal fallback is:

`Cache miss -> Database read -> Cache population`

A cache outage can be handled as a degraded performance condition when the application can continue reading from the database.

This is different from a database outage, which may prevent authoritative reads or writes.

### Queue failure

A queue can be unavailable, delayed, or overloaded.

Retry logic prevents a transient consumer failure from immediately discarding a message.

A dead-letter state prevents infinite retries.

Retry policies must be bounded because unlimited retries can create a feedback loop that increases load on an already failing dependency.

---

## Consistency Trade-offs

A monolithic application can often perform multiple related operations in one local database transaction.

Microservices may require coordination across independent data stores.

For example:

`Order DB`
`Customer DB`
`Billing DB`

cannot automatically participate in one ordinary local database transaction when they are independently owned.

Possible architectural approaches include:

- synchronous validation;
- asynchronous events;
- sagas;
- compensating actions;
- transactional outbox patterns;
- idempotent consumers.

Each approach changes the consistency model and operational complexity.

Strong consistency is not automatically required for every workflow. A customer-facing order creation operation may require strong validation of customer existence, while sending an analytics event can normally tolerate asynchronous processing.

---

## Performance Considerations

Performance should be measured at the actual bottleneck rather than inferred from architecture labels.

A monolith can be faster than microservices for a tightly coupled operation because local function calls avoid network overhead.

Microservices can improve independent scaling when one domain receives significantly more traffic than another.

Caching can reduce repeated database reads.

Queues can smooth bursts by allowing consumers to process work at a controlled rate.

Databases can become bottlenecks when application instances increase faster than database capacity.

A useful performance model is:

`End-to-end latency = local processing + network latency + dependency latency + database latency + queue delay`

For synchronous dependencies, dependency latency contributes directly to request latency.

For asynchronous work, queue delay moves part of the work outside the immediate request path.

---

## Security Considerations

Architecture introduces security boundaries as well as performance boundaries.

Service-to-service communication should use authenticated identities rather than trusting network location alone.

Database credentials should follow least privilege. A customer service should not receive unrestricted access to an order database merely because both databases belong to the same product.

Cache keys should prevent cross-tenant data exposure. A key such as `customer:123` may be insufficient if customer identifiers are only unique inside a tenant.

Sensitive data should not be placed into queue payloads unless the consumer genuinely needs it.

Queue messages should be treated as untrusted input. Consumers should validate message schema, event type, identifiers, and authorization context.

Logs and metrics should avoid exposing credentials, access tokens, payment data, or unnecessary personal information.

---

## Production Design Constraints

The simulations intentionally simplify several production concerns.

A real service deployment normally needs:

- service discovery or stable routing;
- timeouts;
- bounded retries;
- circuit breakers;
- distributed tracing;
- structured logging;
- metrics;
- health checks;
- graceful shutdown;
- deployment strategies;
- schema migration controls;
- backup and recovery;
- capacity planning;
- rate limiting.

A real distributed cache needs an eviction policy appropriate to its workload.

A real message broker needs durable storage, consumer coordination, delivery semantics, ordering decisions, retention policies, and operational monitoring.

A real database needs transaction isolation, connection pooling, backups, replication, failover, migrations, and query-performance monitoring.

These concerns do not change the conceptual distinctions modeled by the five implementations.

---

## Architectural Trade-off Matrix

| Concern | Monolith | Microservices |
|---|---|---|
| Deployment | Single deployment unit | Independent service deployments |
| Local communication | Function or module calls | Network/API calls |
| Database ownership | Often shared | Commonly service-owned |
| Failure isolation | Lower between modules | Potentially stronger |
| Operational complexity | Lower | Higher |
| Independent scaling | Limited | Stronger |
| Distributed transactions | Easier locally | More difficult |
| Service discovery | Usually unnecessary | Often required |
| Network failure | Less prominent | Fundamental concern |
| Team autonomy | Can be lower at scale | Can be higher with good boundaries |

Neither column is universally superior. The correct choice depends on domain coupling, scale, team structure, operational maturity, reliability requirements, and deployment needs.

---

## Architectural Relationship

The four major mechanisms in the model should not be conflated.

A monolith or microservices architecture defines the application structure.

A service defines a domain capability within that structure.

A database stores authoritative persistent state.

A cache accelerates access to frequently requested state.

A queue changes when work is executed and decouples producers from consumers.

Scalability determines how resources are added or changed to satisfy workload requirements.

A coherent architecture can therefore combine these mechanisms:

`Clients`
`   |`
`   v`
`Load Balancer`
`   |`
`   +-------------------+`
`   |                   |`
`   v                   v`
`Customer Service    Order Service`
`   |                   |`
`   v                   v`
`Customer Cache      Order Database`
`   |`
`   v`
`Customer Database`
`                       |`
`                       v`
`                  Order Queue`
`                       |`
`                       v`
`                 Async Consumers`

The architecture becomes maintainable when each component has a clear responsibility, an explicit failure model, an appropriate consistency model, and an operational boundary that matches the workload and domain.
