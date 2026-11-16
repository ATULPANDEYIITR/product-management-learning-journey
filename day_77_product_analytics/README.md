# Product Analytics: Events, Properties, Users, Sessions, Funnels and Cohorts

## 1. Project Scope

This project implements a product analytics system for collecting, validating, processing, and interpreting user interaction data.

The system represents the relationship between product usage and measurable business outcomes. It tracks how users interact with an application, identifies recurring usage patterns, measures conversion performance, and evaluates retention across acquisition cohorts.

The five implementations use different engineering approaches:

| Implementation | Primary responsibility |
|---|---|
| Python | Repository-based analytics simulation and reporting |
| JavaScript | Asynchronous event collection and event-driven processing |
| C++17 | Efficient event processing and analytical computation |
| Java 17 | Enterprise domain modeling and analytics services |
| PostgreSQL | Persistent relational storage and analytical queries |

The implementations share a common analytical domain but do not depend on one another.

## 2. Product Analytics Domain

Product analytics converts application interactions into structured observations.

A user may visit a website, view a product, add an item to a cart, begin checkout, and complete a purchase. Each interaction can generate an event.

A typical analytical workflow is:

User identification
    |
    v
Event generation
    |
    v
Property validation
    |
    v
Event collection
    |
    v
Event storage
    |
    v
Session identification
    |
    v
Metric aggregation
    |
    +------> Funnel analysis
    |
    +------> Cohort analysis
    |
    +------> Retention analysis
    |
    v
Business reporting

The six principal concepts have different responsibilities.

| Concept | Meaning | Primary analytical purpose |
|---|---|---|
| Event | An observed user action | Measure product activity |
| Property | An attribute attached to an event | Explain event context |
| User | An identifiable application participant | Measure user behavior |
| Session | A group of related interactions | Measure usage patterns |
| Funnel | An ordered sequence of actions | Measure conversion |
| Cohort | A group sharing an acquisition or starting period | Measure retention |

## 3. Events

An event represents an occurrence within a product.

Examples include:

- `signup`
- `login`
- `page_view`
- `product_view`
- `add_to_cart`
- `checkout_started`
- `purchase`
- `logout`

An event should describe something that actually happened rather than an assumption about user intention.

For example, `checkout_started` indicates that the checkout process began. It does not establish that payment was successful.

### Event structure

The implementations represent an event using the following logical fields:

| Field | Description |
|---|---|
| event_id | Unique event identifier |
| user_id | Associated user |
| event_name | Type of interaction |
| timestamp | Time of occurrence |
| session_id | Associated session |
| properties | Additional contextual attributes |

An event identifier supports duplicate detection and idempotent ingestion.

The timestamp represents event occurrence time. It should be distinguished from ingestion time, which records when the analytics infrastructure received the event.

This distinction matters when events arrive late, are transmitted from offline devices, or are processed asynchronously.

### Event ordering

Events can arrive in a different order from their occurrence.

For example:

| Event | Occurrence time | Arrival time |
|---|---|---|
| Product view | 09:01 | 09:02 |
| Add to cart | 09:03 | 09:05 |
| Purchase | 09:08 | 09:04 |

Sorting by arrival time would produce an incorrect behavioral sequence.

The implementations therefore use event timestamps for session and funnel calculations, with event identifiers as deterministic secondary ordering keys where appropriate.

## 4. Event Properties

Properties describe the context of an event.

For example, a `product_view` event can contain:

| Property | Example |
|---|---|
| product_id | P100 |
| device_type | mobile |
| page | /products/P100 |
| campaign_id | CAMP01 |

A purchase event can contain:

| Property | Example |
|---|---|
| amount | 1499.00 |
| currency | INR |
| quantity | 1 |

Events and properties should remain conceptually separate.

The event name identifies the action. Properties describe the circumstances surrounding that action.

### Property validation

The implementations validate:

- Nonempty property names.
- Supported scalar data types.
- Maximum property counts.
- Maximum string lengths.
- Finite numeric values.
- Required purchase information.
- Nonnegative transaction amounts.

The SQL implementation uses JSONB for flexible event properties while retaining relational constraints for important entities.

JSONB is useful when event types have different attributes. Relational columns remain preferable for identifiers, relationships, timestamps, and frequently queried structured fields.

### Property governance

A production analytics system needs a controlled event and property vocabulary.

Without governance, different application teams may create incompatible event names such as:

- `productView`
- `product_view`
- `view_product`

These names may describe the same behavior but produce fragmented reports.

The PostgreSQL implementation includes `event_definitions` and `property_definitions` to establish a central event catalog.

Sensitive attributes should not be collected unless they have a defined business and legal purpose. Personally identifiable information should not be inserted into unrestricted event properties.

## 5. Users and Identity Resolution

A user represents an identifiable participant in the product.

The implementations distinguish a registered user from an anonymous visitor.

An anonymous visitor may initially generate events using a browser or device identifier. Following registration or authentication, the anonymous identity can be associated with a registered user.

Example:

Anonymous identity: ANON-U001
    |
    v
User registration
    |
    v
Registered user: U001
    |
    v
Historical and future activity attribution

### Identity concepts

| Identifier | Purpose |
|---|---|
| user_id | Internal registered-user identity |
| anonymous_id | Identifier assigned before authentication |
| event_id | Unique event identifier |
| session_id | Identifier for a usage session |

These identifiers are not interchangeable.

Identity linking should be controlled. Automatically merging different registered accounts based only on similar device or behavioral attributes can produce incorrect attribution.

The Python implementation uses a user registry. JavaScript provides an identity-resolution service and anonymous identity mappings. Java models identity resolution through a dedicated service. PostgreSQL implements anonymous identity relationships and a transactional linking procedure.

## 6. Sessions

A session groups related user interactions into a period of product activity.

For example:

09:00  Login
09:02  Page view
09:05  Product view
09:08  Add to cart
09:12  Checkout started

These interactions can belong to one session.

### Inactivity-based sessionization

The implementations use a 30-minute inactivity threshold.

If the difference between consecutive events exceeds the threshold, a new session begins.

For example:

| Event | Time | Session |
|---|---|---|
| Login | 09:00 | S1 |
| Page view | 09:05 | S1 |
| Product view | 09:15 | S1 |
| Page view | 10:00 | S2 |

The threshold is a configurable analytical rule rather than a universal definition.

Applications may use explicit session identifiers, authentication boundaries, mobile application lifecycle events, or other session policies.

### Session metrics

Useful session metrics include:

- Session count.
- Events per session.
- Session duration.
- Sessions per user.
- Average session duration.
- Returning-session frequency.
- Distinct event types per session.

Session duration is calculated from the first and last event timestamps.

A session containing only one event has zero observed duration under this definition. This does not necessarily mean that the user spent no time in the application.

The PostgreSQL `session_event_summary` view demonstrates inactivity-based sessionization through window functions.

The implementation uses a 30-minute inactivity rule and computes sessions dynamically from event history.

## 7. Funnels

A conversion funnel measures the progression of users through an ordered sequence of events.

The implemented purchase funnel is:

Signup
   |
   v
Product view
   |
   v
Add to cart
   |
   v
Checkout started
   |
   v
Purchase

A user who reaches a later step must first satisfy the preceding steps in chronological order.

### Funnel metrics

The principal calculation is:

Conversion Rate = (Users reaching current step / Users reaching previous step) × 100

Consider this example:

| Step | Users | Conversion from previous step |
|---|---:|---:|
| Signup | 5 | 100% |
| Product view | 5 | 100% |
| Add to cart | 4 | 80% |
| Checkout started | 3 | 75% |
| Purchase | 3 | 100% |

The overall conversion rate is:

3 / 5 × 100 = 60%

The largest user loss occurs between product viewing and adding an item to the cart.

This identifies a point for further investigation. It does not independently establish why users abandoned the process.

### Funnel rules

The implementations support:

- Ordered event sequences.
- Unique funnel steps.
- User-level progression.
- Conversion windows.
- Incomplete journeys.
- Zero-conversion conditions.
- Step-level conversion rates.
- Overall conversion rates.

The Python, JavaScript, C++17, and Java implementations use chronological user-event sequences.

The PostgreSQL implementation provides a configurable funnel definition through `funnels` and `funnel_steps`, with an evaluation function for the configured purchase workflow.

A production implementation should ensure that every funnel step uses the same conversion-window configuration. The supplied SQL evaluation function demonstrates the five-step purchase workflow with a seven-day window.

### Funnel interpretation

A funnel is an analytical view of user progression.

It does not require that every user completes the process within one session.

The conversion window determines the period during which subsequent steps qualify.

Funnel results can differ depending on whether analysis uses:

- First occurrence of each event.
- First eligible sequence.
- Repeated event sequences.
- Session-level conversion.
- User-level conversion.

The supplied implementations use an ordered, user-level event sequence with a bounded conversion window.

## 8. Cohorts

A cohort is a group of users sharing a defined starting characteristic.

The implementations use acquisition-month cohorts based on user creation timestamps.

For example:

| User | Registration month | Cohort |
|---|---|---|
| U001 | September 2026 | September |
| U002 | September 2026 | September |
| U003 | September 2026 | September |
| U004 | October 2026 | October |
| U005 | October 2026 | October |

Cohorts make it possible to compare groups over time instead of treating all users as one population.

### Cohort retention

Retention measures how many members of a cohort return during a subsequent period.

A monthly retention calculation is:

Retention Rate = (Active cohort members in month N / Original cohort size) × 100

Example:

| Cohort | Original users | Month 0 | Month 1 |
|---|---:|---:|---:|
| September | 3 | 100% | 66.67% |
| October | 2 | 100% | 0% |

The example demonstrates the difference between acquisition size and subsequent engagement.

Month 0 represents the original cohort month. Subsequent offsets represent calendar months after acquisition.

### Cohort types

Other useful cohort definitions include:

- Acquisition cohorts: grouped by registration date.
- Behavioral cohorts: grouped by an observed action.
- Transaction cohorts: grouped by first purchase.
- Subscription cohorts: grouped by subscription start date.
- Campaign cohorts: grouped by acquisition campaign.

The supplied implementations focus on acquisition-month cohorts.

### Retention distinctions

Retention and conversion measure different outcomes.

A user can complete a purchase without returning in the following month.

A user can also return frequently without making a purchase.

Consequently, retention should not be interpreted as equivalent to revenue, conversion, or engagement.

## 9. Python Implementation

The Python file implements a self-contained analytics simulation using the standard library.

### Architecture

| Component | Responsibility |
|---|---|
| User | Registered-user data |
| Event | Immutable event representation |
| EventStore | User and event storage |
| AnalyticsTracker | Event collection |
| Sessionizer | Session construction |
| EventAnalytics | Event aggregation |
| FunnelAnalyzer | Conversion calculations |
| CohortAnalyzer | Retention calculations |
| JsonlRepository | Event persistence |
| AnalyticsReport | Analytical reporting |

### Important mechanisms

**Dataclasses**

`User`, `Event`, `Session`, and analytical result structures provide explicit domain representations.

**Enums**

`EventType` establishes consistent names for frequently used application events.

**Dictionaries and sets**

Dictionaries group events by user and event type. Sets support unique-user calculations and duplicate detection.

**Exceptions**

Validation and duplicate-event errors distinguish malformed input from repeated ingestion.

**JSONL persistence**

Each event is stored as a separate JSON record.

The persistence mechanism writes to a temporary file before replacing the target file, reducing the risk of leaving a partially written output file.

**Assertions**

The demonstration verifies user counts, event counts, revenue, funnel conversions, unknown-user rejection, and duplicate detection.

### Complexity considerations

For N events:

- Event insertion is approximately O(1) average using a set for duplicate detection.
- Event aggregation is O(N) average.
- Sessionization is O(N log N) due to per-user chronological sorting.
- Funnel processing is O(N log N) due to event sorting.
- Cohort aggregation is approximately O(N + U), excluding sorting, where U represents the number of users.

The in-memory implementation is suitable for controlled datasets and learning workflows. Large production datasets require durable storage and incremental processing.

## 10. JavaScript Implementation

The JavaScript file provides an event-driven and asynchronous implementation.

### Architecture

| Component | Responsibility |
|---|---|
| IdentityRegistry | Anonymous and registered identity mapping |
| EventCollector | Event validation and emission |
| IngestionPipeline | Asynchronous ingestion |
| SessionEngine | Session construction |
| ProductMetrics | Aggregation |
| FunnelEngine | Funnel evaluation |
| CohortEngine | Retention analysis |
| EventFileRepository | JSONL persistence |

### Event-driven processing

The `EventCollector` extends Node.js `EventEmitter`.

When an event is accepted, it emits an `event` notification.

Other components can subscribe without being tightly coupled to the collector.

For example, purchase events can trigger reporting or downstream processing.

### Asynchronous ingestion

`IngestionPipeline` processes queued events in bounded batches.

Promises allow individual ingestion failures to be captured without silently losing unrelated event results.

The configured concurrency controls how many queued operations are processed together.

This demonstration uses in-memory processing. It does not provide a durable message broker or distributed delivery guarantee.

### State management

The implementation uses:

- `Map` for event and user lookup.
- `Set` for unique users and event types.
- Frozen objects for stable event representations.
- Promises for asynchronous ingestion.
- `EventEmitter` for event-driven communication.

### Persistence

The file repository writes JSONL data asynchronously.

It uses a temporary file, synchronizes the file handle, and renames the completed file.

For distributed production systems, this local persistence mechanism would need to be replaced or supplemented with transactional storage and reliable event delivery.

## 11. C++17 Implementation

The C++17 implementation focuses on domain modeling, efficient collection processing, and explicit error handling.

### Architecture

| Component | Responsibility |
|---|---|
| User | User domain structure |
| Event | Structured interaction |
| EventRepository | Event and user storage |
| SessionEngine | Sessionization |
| MetricsEngine | Aggregation |
| FunnelEngine | Conversion analysis |
| CohortEngine | Cohort retention |

### Engineering decisions

`unordered_map` provides average constant-time lookup for user grouping.

`unordered_set` provides efficient duplicate detection and unique-user counting.

`map` provides deterministic ordering for reports and event properties.

`vector` stores ordered event records and analytical results.

`enum class` prevents accidental mixing of event categories with unrelated integer values.

The repository validates complete event batches before modifying its internal state.

This prevents partial insertion caused by a validation failure in the middle of a batch.

### Performance considerations

The main processing costs are:

- Event insertion: O(1) average for hash-based lookup.
- Event grouping: O(N) average.
- Sessionization: O(N log N) due to sorting.
- Funnel evaluation: O(N log N) due to chronological ordering.
- Cohort grouping: O(N + U) average, excluding sorting.

The simulation uses integer minutes instead of timestamp strings. This simplifies temporal calculations and avoids unnecessary parsing.

The month conversion uses a 30-day simulation model. It is not intended to replace real calendar-month calculations in production reporting.

## 12. Java 17 Implementation

The Java implementation uses an enterprise-oriented service architecture.

### Domain and service separation

| Component | Responsibility |
|---|---|
| User | Registered user |
| AnalyticsEvent | Typed event |
| IdentityService | Identity resolution |
| EventIngestionService | Event acceptance |
| SessionService | Session construction |
| MetricsService | Product metrics |
| FunnelService | Conversion analysis |
| CohortService | Retention |
| AnalyticsPolicy | Business validation |

### Records and immutable structures

Java records represent domain objects with explicit fields and constructors.

Event properties are copied into immutable maps.

Funnel and cohort results expose immutable collections.

This reduces accidental modification of analytical results after computation.

### Idempotency

The ingestion service uses `putIfAbsent` to prevent duplicate event identifiers.

If an identical event is received again, the service returns `DUPLICATE`.

If the same event identifier is reused with different content, it raises an exception.

This distinction is important for reliable event ingestion.

### Policy objects

`PurchasePolicy` defines the validation requirements for purchase events.

The interface allows event-specific business policies to be separated from ingestion and reporting logic.

### Enterprise considerations

The service architecture separates identity, ingestion, sessionization, aggregation, and retention calculations.

This supports independent testing and makes it easier to replace individual components with database-backed or distributed implementations.

The example uses concurrent in-memory collections. It does not provide distributed transactions, database-backed uniqueness, or cross-instance consistency.

## 13. PostgreSQL Implementation

The PostgreSQL file provides a relational model for persistent analytics operations.

### Database architecture

| Table or object | Responsibility |
|---|---|
| users | Registered identities |
| anonymous_identities | Anonymous visitor identities |
| event_definitions | Approved event vocabulary |
| property_definitions | Property catalog |
| sessions | Session records |
| events | Collected interactions |
| event_quality_issues | Data-quality exceptions |
| funnels | Funnel configuration |
| funnel_steps | Ordered funnel stages |
| daily_product_metrics | Aggregated metrics |
| cohort_retention | Retention snapshots |
| event_audit | Event modification history |

### Relational relationships

Users
    |
    +---- Anonymous identities
    |
    +---- Sessions
    |        |
    |        +---- Events
    |
    +---- Events
             |
             +---- Event definitions
             |
             +---- Funnel evaluation

Funnels
    |
    +---- Funnel steps
             |
             +---- Event definitions

### Constraints

Primary keys uniquely identify records.

Foreign keys preserve relationships between users, events, sessions, and event definitions.

Unique constraints prevent duplicate external identities and event keys.

Check constraints validate timestamps, identifiers, retention percentages, and other important domain conditions.

The purchase validation trigger ensures that purchase events contain a valid nonnegative numeric amount and a three-character currency code.

Product views and cart additions require a product identifier.

### JSONB

The `events.properties` column uses JSONB.

This permits different event types to store different property sets without requiring a new relational column for every product-specific attribute.

GIN indexing supports property-based filtering.

Frequently accessed identifiers, timestamps, and relationships remain separate relational columns.

### Functions and procedures

The SQL implementation includes:

- `validate_event_properties()` for property validation.
- `audit_event_changes()` for event auditing.
- `link_anonymous_identity()` for transactional identity association.
- `ingest_event()` for event insertion.
- `evaluate_funnel()` for funnel evaluation.
- `refresh_cohort_retention()` for retention aggregation.

### Window functions

The `session_event_summary` view uses `LAG()` to identify the previous event timestamp and `SUM()` to construct session boundaries.

This demonstrates how temporal sessionization can be performed within the database.

### Indexing

The schema creates indexes for:

- User and timestamp retrieval.
- Event type and timestamp retrieval.
- Session event retrieval.
- JSONB property searches.
- Large timestamp-ordered event tables.

BRIN indexing is useful when event timestamps correlate with physical row order.

Index selection should be validated against actual query plans and workload characteristics.

### Transactions

Event insertion and the demonstration data are executed within transactions.

A failed validation or insertion can abort the transaction rather than leaving partially applied data.

The identity-linking procedure uses row-level locking to prevent conflicting concurrent identity updates.

## 14. Metric Definitions

Consistent metric definitions are essential when multiple teams use the same analytics system.

| Metric | Definition |
|---|---|
| Total events | Number of accepted recorded events |
| Active users | Distinct users with qualifying activity |
| Unique users per event | Distinct users generating a particular event |
| Session count | Number of identified sessions |
| Session duration | Difference between first and last event |
| Revenue | Sum of valid purchase amounts |
| Average order value | Revenue divided by purchase count |
| Funnel conversion | Users progressing to the next stage |
| Overall conversion | Final-step users divided by first-step users |
| Retention | Returning cohort members divided by original cohort size |

Currency must be handled carefully.

A revenue total combining INR, GBP, and USD is not economically meaningful without currency normalization.

The demonstration therefore reports revenue by currency in PostgreSQL and uses simple numerical aggregation in the programming-language simulations.

A production reporting layer should normalize amounts using a defined exchange-rate policy when consolidated revenue is required.

## 15. Data Quality and Failure Handling

Product analytics depends on the reliability of its event data.

Common failure conditions include:

| Failure | Consequence | Control |
|---|---|---|
| Duplicate events | Inflated counts | Event identifiers |
| Unknown user | Incorrect attribution | Identity validation |
| Missing purchase amount | Invalid revenue | Property validation |
| Negative transaction amount | Incorrect revenue | Numeric constraints |
| Incorrect timestamps | Invalid sequences | Timestamp validation |
| Late events | Incomplete reporting | Event-time processing |
| Inconsistent event names | Fragmented analytics | Event catalog |
| Incorrect identity linking | Misattributed activity | Controlled identity mapping |
| Invalid session references | Broken session relationships | Foreign keys |
| Incomplete event properties | Incorrect segmentation | Property definitions |

The implementations provide validation and exception handling for the principal failures.

A production system should also define retry behavior, event expiration, schema versioning, access controls, dead-letter handling, and monitoring of ingestion latency.

## 16. Security and Privacy

Product analytics can contain sensitive information even when its primary purpose is behavioral measurement.

Important controls include:

- Collect only necessary attributes.
- Avoid storing passwords, authentication tokens, or payment credentials in event properties.
- Use pseudonymous identifiers where appropriate.
- Restrict access to user-level event records.
- Apply encryption in transit and at rest.
- Define retention and deletion policies.
- Audit administrative operations.
- Separate event ingestion permissions from reporting permissions.
- Validate externally supplied identifiers.
- Avoid placing sensitive values in application logs.

The SQL implementation includes separate ingestion and reporting role examples.

These permissions should be applied by a database administrator using deployment-specific role configuration.

The event audit mechanism records database event insertions and updates. It is not a complete immutable audit system and does not replace database-level security monitoring.

## 17. Implementation Comparison

| Engineering concern | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Event collection | Tracker | Event collector | Repository | Ingestion service | Ingestion function |
| Identity | User registry | Identity registry | User repository | Identity service | Identity tables |
| Properties | Dictionaries | Objects | Maps | Immutable maps | JSONB |
| Sessionization | Class | Stateful engine | Engine class | Service | Window functions |
| Funnels | Analyzer | Engine | Engine | Service | SQL function |
| Cohorts | Analyzer | Engine | Engine | Service | Procedure |
| Persistence | JSONL | JSONL | In-memory | In-memory | Relational tables |
| Error handling | Exceptions | Promise rejection | Exceptions | Custom exceptions | SQL exceptions |

The implementations are intentionally independent.

Python emphasizes analytical experimentation and concise data processing.

JavaScript emphasizes event-driven collection and asynchronous workflows.

C++17 emphasizes explicit data structures and efficient processing.

Java 17 emphasizes enterprise domain boundaries and service separation.

PostgreSQL emphasizes relational integrity, durable storage, and database-side analytics.

## 18. Limitations and Production Boundaries

The supplied programs are executable analytical demonstrations rather than complete distributed analytics platforms.

Important limitations include:

- The programming-language implementations use in-memory event stores.
- The JSONL repositories do not provide distributed transaction guarantees.
- Sessionization is performed over the available event dataset.
- The Python and JavaScript implementations generate session identifiers during analytical processing when no explicit identifier is supplied.
- The C++ simulation uses simplified 30-day months.
- The Java implementation does not provide persistent database transactions.
- The SQL funnel evaluation is tailored to the five configured purchase stages.
- The SQL cohort procedure calculates calendar-month retention from available event history.
- The implementations do not include a production dashboard or visualization frontend.
- Cross-device identity resolution requires stronger identity verification than the demonstration provides.
- Event schema evolution requires explicit compatibility and migration policies.

Large-scale deployments typically require partitioning, retention management, asynchronous delivery, incremental aggregation, monitoring, and workload-specific query optimization.

## 19. Verification Scenarios

The supplied demonstrations exercise the following cases:

| Scenario | Expected behavior |
|---|---|
| Five registered users | All identities accepted |
| Thirty Python events | Successful analytical processing |
| Duplicate event ID | Rejected |
| Unknown user | Rejected |
| Invalid purchase amount | Rejected |
| Incomplete purchase journey | Included in intermediate funnel steps |
| Complete purchase journey | Included in final funnel conversion |
| No qualifying purchase | Zero revenue or conversion |
| Inactive user | Included in cohort denominator |
| Later-month activity | Reflected in retention calculations |
| Missing required event properties | Rejected by validation |
| Anonymous identity association | Linked to a registered user |

The implementations use synthetic data for September and October 2026. Their results are intended to demonstrate the calculations and data relationships, not to represent real customer behavior.
