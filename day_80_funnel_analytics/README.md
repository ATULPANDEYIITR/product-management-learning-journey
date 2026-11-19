# Funnel Analytics

## Project Description

Funnel Analytics is an event-based measurement system for understanding how users progress through a sequence of business activities.

The implementation models an e-commerce purchase journey:

**Website Visit → Product View → Add to Cart → Checkout → Purchase**

The system measures:

- Funnel construction and ordered progression.
- Unique users reaching each step.
- Step-level conversion rates.
- User drop-offs between consecutive steps.
- Overall conversion rates.
- Cohort selection.
- Traffic-channel segmentation.
- Device-based segmentation.
- Conversion-window compliance.
- Event validation and reporting.

The five implementations use different engineering approaches to represent the same analytical problem.

## 1. Core Concepts

### 1.1 Funnel Analytics

A conversion funnel represents a sequence of activities that users are expected to complete.

For an e-commerce application:

| Stage | Event | Business meaning |
|---|---|---|
| 1 | `visit` | User enters the website |
| 2 | `product_view` | User views a product |
| 3 | `add_to_cart` | User adds a product to the cart |
| 4 | `checkout` | User initiates checkout |
| 5 | `purchase` | User completes a purchase |

A funnel identifies where users stop progressing.

A user who visits a website but does not view a product contributes to the first stage but not the second.

A user who reaches checkout but does not purchase contributes to the checkout stage but not the final conversion stage.

### 1.2 Event Tracking

An event records an activity performed by a user at a particular time.

The principal event attributes are:

| Attribute | Description |
|---|---|
| Event ID | Unique identifier for an event |
| User ID | Identifier of the user performing the activity |
| Event name | Activity being recorded |
| Timestamp | Time at which the activity occurred |
| Channel | Acquisition source |
| Device | Device category |
| Country | Geographic attribute |
| Properties | Additional event-specific attributes |

Event records are different from user records.

A user can generate many events. A single user may visit several pages, add multiple products to a cart, and generate multiple checkout events.

Event-level counts and unique-user counts must therefore be distinguished.

### 1.3 Funnel Construction

A funnel definition contains:

- Funnel name.
- Ordered event steps.
- Conversion window.
- Optional cohort and segmentation conditions.

A funnel is constructed by identifying users who entered through the first step and evaluating their subsequent progression.

The implementations use distinct event records rather than assuming that every event represents a new user.

Repeated occurrences of the same event do not increase the number of users counted at a funnel stage.

### 1.4 Sequential Progression

The standard funnel requires events to occur in the configured order.

For example:

`visit → product_view → add_to_cart → checkout → purchase`

A user who performs:

`visit → product_view → checkout`

does not qualify for the checkout stage in a strict sequential funnel because the add-to-cart stage was not completed.

This distinction is important when interpreting funnel results.

An unrestricted event-presence analysis could incorrectly count users who skipped intermediate stages.

### 1.5 Conversion Window

A conversion window specifies the maximum permitted duration between cohort entry and funnel progression.

For example, a 24-hour conversion window requires qualifying events to occur within 24 hours of the first funnel event.

A purchase occurring after the configured window does not qualify as a conversion for that analysis.

The window prevents unrelated activities occurring much later from being attributed to the original user journey.

## 2. Conversion Rates and Drop-Offs

### 2.1 Step-Level Conversion Rate

Step-level conversion measures the percentage of users who reached the current stage out of those who reached the previous stage.

Formula:

\[
CR_i = \frac{U_i}{U_{i-1}} \times 100
\]

Where:

- \(U_i\) = Users reaching the current stage.
- \(U_{i-1}\) = Users reaching the previous stage.

For the first stage, the conversion rate is defined as 100% when the cohort contains users.

### 2.2 Drop-Off Rate

Drop-off measures the proportion of users who failed to progress from one stage to the next.

\[
DropOff_i =
\frac{U_{i-1}-U_i}{U_{i-1}}\times100
\]

A high drop-off rate indicates a stage requiring further investigation.

Possible causes include:

- Poor page performance.
- Complicated navigation.
- Unclear product information.
- Unexpected delivery charges.
- Payment failures.
- Excessive checkout requirements.
- Limited payment options.

Drop-off identifies where a problem may exist. It does not independently establish the cause.

### 2.3 Overall Conversion Rate

Overall conversion measures the percentage of initial cohort users who complete the final stage.

\[
OverallConversion =
\frac{FinalStageUsers}{InitialCohortUsers}
\times100
\]

For the sample dataset:

| Stage | Users | Conversion from previous stage | Drop-off |
|---|---:|---:|---:|
| Website Visit | 8 | 100.00% | 0.00% |
| Product View | 7 | 87.50% | 12.50% |
| Add to Cart | 5 | 71.43% | 28.57% |
| Checkout | 4 | 80.00% | 20.00% |
| Purchase | 3 | 75.00% | 25.00% |

Overall conversion:

\[
\frac{3}{8}\times100=37.50\%
\]

The largest proportional drop-off occurs between product viewing and adding a product to the cart.

## 3. Cohort Analysis

A cohort is a group of users selected according to a shared entry condition.

In this implementation, the initial website visit determines cohort membership.

Users are selected using their first qualifying visit within the specified reporting period.

This prevents later events from incorrectly creating additional cohort entries.

### 3.1 Cohort Selection

The analysis supports:

- Start timestamp.
- End timestamp.
- Acquisition channel.
- Device category.
- User-level entry conditions.

The first funnel event establishes the cohort-entry timestamp.

Subsequent events are evaluated relative to that timestamp.

### 3.2 Cohort and Event Windows

Two separate time conditions must be distinguished:

| Time condition | Purpose |
|---|---|
| Cohort reporting period | Determines which users enter the analysis |
| Conversion window | Determines how long users have to progress through the funnel |

For example, a user entering on 1 November can belong to a November cohort while their purchase is evaluated using a 24-hour conversion window.

The reporting period does not automatically extend the conversion window.

## 4. Segmentation

Segmentation compares funnel performance between groups of users.

It helps identify whether conversion behavior differs across acquisition channels, devices, geographic areas, or campaigns.

### 4.1 Traffic-Channel Segmentation

The implementations include:

| Channel | Description |
|---|---|
| Organic | Unpaid search or discovery |
| Paid | Paid advertising |
| Referral | Traffic from external referrals |
| Direct | Direct website access |
| Email | Email campaign traffic |

A channel comparison can reveal differences in acquisition quality.

For example, paid traffic may produce a large number of visitors but a relatively low purchase conversion rate.

Organic traffic may produce fewer visitors but a higher proportion of completed purchases.

### 4.2 Device Segmentation

The supported device categories are:

- Mobile.
- Desktop.
- Tablet.

Device segmentation helps identify usability differences.

A high mobile drop-off at checkout could indicate:

- Difficult form entry.
- Poor mobile layout.
- Payment interface problems.
- Slow loading times.
- Inadequate mobile navigation.

### 4.3 Geographic Segmentation

Country-level segmentation can identify regional differences in conversion.

Possible contributing factors include payment availability, currency, shipping coverage, pricing, and language.

Geographic comparisons should account for differences in traffic volume and customer composition.

### 4.4 Segment Comparability

Segment comparisons should use consistent:

- Funnel definitions.
- Event naming conventions.
- Conversion windows.
- Cohort-entry rules.
- Reporting periods.

A comparison between segments with different measurement rules can produce misleading results.

## 5. Distinctions Between Funnel Measurements

| Measurement | What it measures |
|---|---|
| Event count | Number of recorded activities |
| Unique users | Distinct users performing an activity |
| Funnel count | Users qualifying for an ordered stage |
| Step conversion | Progression from one stage to another |
| Drop-off | Users lost between consecutive stages |
| Overall conversion | Entry-to-final-stage completion |
| Cohort analysis | Performance of a defined user group |
| Segmentation | Differences between user groups |

An event count is not equivalent to a conversion count.

For example, a user who views a product ten times still represents one user at the product-view stage.

## 6. Python Implementation

**File:** `funnel_analytics.py`

The Python implementation provides an object-oriented analytical engine.

### Main Components

| Component | Responsibility |
|---|---|
| `Event` | Validates and represents individual events |
| `FunnelDefinition` | Defines ordered steps and conversion windows |
| `EventStore` | Stores events and indexes them by user |
| `FunnelAnalyzer` | Calculates user-level funnel progression |
| `SegmentAnalyzer` | Compares conversion performance by segment |
| `FunnelReport` | Holds analytical results |
| `StepMetrics` | Stores stage-level conversion and drop-off data |

### Event Storage

The event store maintains two dictionaries:

- An event-ID dictionary for duplicate detection.
- A user-ID dictionary for efficient user-level retrieval.

This avoids repeatedly scanning the entire event collection when retrieving an individual user's journey.

Batch insertion validates duplicate identifiers before modifying the store.

### Funnel Evaluation

The analyzer processes events in timestamp order.

For each user, it:

1. Identifies the first qualifying entry event.
2. Applies the cohort conditions.
3. Selects subsequent events.
4. Checks the conversion window.
5. Evaluates ordered progression.
6. Updates stage-level user counts.
7. Calculates conversion and drop-off rates.

### Validation and Reporting

The implementation includes:

- Duplicate-event protection.
- Timezone-aware timestamp validation.
- Funnel-step validation.
- Empty-cohort handling.
- Conversion-rate bounds.
- Monotonically decreasing funnel counts.
- JSON report export.
- Assertions for sample-data verification.

The implementation uses only Python standard-library modules.

## 7. JavaScript Implementation

**File:** `funnel_analytics.js`

The JavaScript implementation uses an event-driven architecture.

### Main Components

| Component | Responsibility |
|---|---|
| `FunnelEvent` | Immutable event representation |
| `FunnelDefinition` | Validated funnel configuration |
| `EventRepository` | Event storage and event notifications |
| `FunnelEngine` | Sequential funnel evaluation |
| `FunnelReportingService` | JSON export and concurrent reporting |

### Event-Driven Processing

`EventRepository` extends Node.js `EventEmitter`.

After an event is accepted, the repository emits an `event:accepted` notification.

Other components can subscribe to this event without requiring the repository to know their implementation details.

This separates event ingestion from downstream processing.

### Map and Set Data Structures

The implementation uses:

- `Map` for event storage and user indexing.
- `Set` for unique segment values.
- Arrays for ordered event journeys.
- Immutable event and funnel objects to reduce accidental modification.

### Asynchronous Reporting

The reporting service supports asynchronous file output through Node.js filesystem APIs.

It also uses `Promise.all()` to execute independent segment-report calculations concurrently.

For large-scale deployment, concurrency should be bounded when segment calculations become computationally expensive.

### Failure Handling

The implementation validates:

- Event identifiers.
- User identifiers.
- Timestamps.
- Funnel definitions.
- Duplicate events.
- Time ranges.
- Segment properties.

Errors propagate to the main execution handler, which reports failures and sets the process exit code.

## 8. C++17 Implementation

**File:** `funnel_analytics.cpp`

The C++ implementation emphasizes explicit domain modeling, memory-efficient data structures, and analytical invariants.

### Main Components

| Component | Responsibility |
|---|---|
| `EventType` | Enumerates funnel event types |
| `Device` | Defines device categories |
| `Event` | Represents an individual activity |
| `FunnelDefinition` | Stores funnel configuration |
| `EventStore` | Maintains event and user indexes |
| `FunnelGovernanceEngine` | Evaluates funnel progression |
| `FunnelReport` | Stores aggregated analytical results |

### Data Structures

The event store uses:

- `unordered_map` for event lookup.
- `unordered_map` for user-level event indexing.
- `vector` for chronological user journeys.
- `unordered_set` for duplicate batch detection.
- `set` for uniqueness validation.

These structures provide efficient lookup and aggregation without third-party dependencies.

### Domain Validation

The engine enforces:

- Unique event identifiers.
- Non-empty user identifiers.
- Unique funnel steps.
- Positive conversion windows.
- Sequential event progression.
- Non-increasing funnel counts.

The report validator detects inconsistencies before results are displayed.

### Performance Characteristics

Let:

- \(E\) represent the number of events.
- \(U\) represent the number of users.
- \(S\) represent the number of funnel stages.

Event insertion and hash-based lookup have average constant-time complexity.

User-level sorting costs approximately:

\[
O\left(\sum_{u=1}^{U} E_u\log E_u\right)
\]

where \(E_u\) is the number of events generated by user \(u\).

The analytical progression pass is linear in the number of processed events.

The design is suitable for in-memory analytical workloads. Large event datasets require persistent storage and incremental aggregation.

## 9. Java 17 Implementation

**File:** `FunnelAnalytics.java`

The Java implementation provides an enterprise-oriented domain model.

### Main Components

| Component | Responsibility |
|---|---|
| `AnalyticsEvent` | Immutable event record |
| `FunnelDefinition` | Validated funnel configuration |
| `EventRepository` | Event storage and retrieval |
| `CohortPolicy` | Defines cohort eligibility |
| `ChannelPolicy` | Applies acquisition-channel conditions |
| `DevicePolicy` | Applies device conditions |
| `FunnelAnalysisService` | Evaluates funnel progression |
| `FunnelReportingService` | Produces reports |

### Records and Immutable Data

Java 17 records represent events, funnel definitions, metrics, and reports.

Records provide concise immutable data structures with generated accessors and value-based equality.

Collections are copied during object construction to prevent accidental external modification.

### Policy-Based Segmentation

The `CohortPolicy` interface separates cohort eligibility from funnel calculation.

Two policy implementations are included:

- `ChannelPolicy`.
- `DevicePolicy`.

This allows the same funnel evaluation service to analyze different user populations without duplicating the progression algorithm.

### Enterprise Design Considerations

The repository synchronizes its public methods to protect in-memory state during concurrent access.

Batch validation occurs before event insertion.

Custom domain boundaries separate:

- Event collection.
- Cohort eligibility.
- Funnel calculation.
- Report generation.

A production implementation could extend these boundaries with database transactions, distributed event ingestion, authorization, and scheduled reporting.

## 10. PostgreSQL Implementation

**File:** `funnel_analytics.sql`

The PostgreSQL implementation models a relational event analytics system.

It includes schema creation, domain types, relational constraints, indexes, reporting views, analytical functions, stored procedures, and sample records.

### Relational Data Model

The primary relationships are:

- One user can generate many events.
- One funnel contains multiple ordered steps.
- Each event belongs to one user.
- Each event has a defined category.
- Each funnel step identifies the event category required for progression.

Conceptual relationship:

    USERS
      |
      | 1:N
      |
    EVENTS

    FUNNELS
      |
      | 1:N
      |
    FUNNEL_STEPS

    EVENTS + USERS + FUNNEL_STEPS
                  |
                  v
           COHORT ANALYSIS
                  |
                  v
          FUNNEL PROGRESSION
                  |
                  v
          CONVERSION METRICS
                  |
                  v
             REPORTING

### Database Objects

| Object | Purpose |
|---|---|
| `users` | Stores user identity and country |
| `funnels` | Defines funnel configurations |
| `funnel_steps` | Stores ordered funnel stages |
| `events` | Stores user activity |
| `funnel_summary` | Reports funnel configuration |
| `channel_performance` | Compares acquisition and device segments |
| `revenue_by_channel` | Aggregates purchase revenue |
| `daily_funnel_events` | Stores daily aggregated reporting data |

### Constraints

The database enforces:

- Primary-key integrity.
- Foreign-key relationships.
- Unique external user identifiers.
- Unique funnel-step numbers.
- Positive conversion windows.
- Valid country codes.
- Non-negative revenue.
- JSON object properties.

The event validation trigger enforces business rules for revenue and future-dated events.

Purchase events require positive revenue. Non-purchase events must have zero revenue.

### Indexing

The following indexes support common analytical access patterns:

| Index | Analytical purpose |
|---|---|
| `idx_events_user_time` | Retrieves chronological user journeys |
| `idx_events_type_time` | Filters events by category and time |
| `idx_events_channel_device` | Supports segmentation |
| `idx_events_session` | Supports session-level analysis |
| `idx_events_properties` | Supports JSONB property filtering |
| `idx_funnel_steps_order` | Retrieves ordered funnel stages |

Index selection should be reviewed against actual query plans and production data distribution.

### Funnel Calculation Function

`calculate_funnel()` accepts:

- Funnel identifier.
- Optional reporting start time.
- Optional reporting end time.
- Optional traffic channel.
- Optional device category.

It returns:

- Step number.
- Step name.
- Event category.
- Users reached.
- Previous-stage users.
- Dropped users.
- Conversion rate.
- Drop-off rate.

The SQL uses CTEs to separate cohort construction, event progression, stage aggregation, and rate calculation.

### Views and Aggregations

`channel_performance` compares conversion rates by channel and device.

`revenue_by_channel` calculates purchasing users, purchase-event counts, total revenue, and average order value.

`daily_funnel_events` provides daily event aggregation.

The materialized view reduces repeated aggregation work for reporting workloads.

It must be refreshed when the underlying event data changes.

### Idempotent Event Ingestion

`ingest_event()` uses a unique event UUID and conflict handling.

Repeated delivery of the same event key does not create another event record.

This is useful when an event producer retries a request after a timeout or uncertain response.

Idempotency prevents duplicate records from inflating analytical counts.

## 11. Analytical Workflow

The complete processing workflow is:

    Event Generation
          |
          v
    Event Validation
          |
          v
    Event Storage
          |
          v
    Duplicate Detection
          |
          v
    Cohort Construction
          |
          v
    Entry-Time Identification
          |
          v
    Ordered Event Evaluation
          |
          v
    Conversion-Window Validation
          |
          v
    Stage-Level Aggregation
          |
          v
    Conversion and Drop-Off Calculation
          |
          v
    Channel and Device Segmentation
          |
          v
    Reporting and Export

Each stage has a separate responsibility.

Event validation establishes whether incoming records satisfy the data contract.

Cohort construction determines which users belong to the analysis.

Progression evaluation determines whether users completed the required sequence.

Aggregation calculates the metrics.

Segmentation compares different user populations.

Reporting presents the resulting measurements.

## 12. Important Analytical Edge Cases

### 12.1 Duplicate Events

A tracking system may send the same event more than once because of retries, browser refreshes, or network failures.

Duplicate event identifiers must be rejected or handled idempotently.

Counting duplicate events as separate users would inflate funnel measurements.

### 12.2 Repeated User Activities

A user may view the same product repeatedly.

Repeated events should not create additional distinct users at a funnel stage.

The analytical unit must be clearly defined as a user, session, or event.

The implementations use distinct users.

### 12.3 Out-of-Order Events

Distributed event collection can produce records that arrive in a different order from their occurrence timestamps.

Analytical processing should use event occurrence time rather than ingestion order.

The SQL implementation includes an audit query for timestamp ordering.

### 12.4 Missing Intermediate Steps

A user may reach a later event without completing an earlier stage.

Strict sequential funnels exclude such users from the later qualifying stage.

A non-strict funnel would require a different progression rule.

### 12.5 Zero-User Cohorts

A selected period or segment may contain no qualifying users.

Division by zero must be avoided.

The implementations return zero conversion and drop-off rates when the relevant denominator is zero.

### 12.6 Conversion Outside the Window

A user may complete a purchase after the configured conversion window.

That purchase does not qualify for the selected funnel analysis.

Different business questions may require different conversion windows.

### 12.7 Multiple Sessions

A user may interact with the application across several sessions.

The current examples use user-level journeys and do not reset funnel progression at session boundaries.

A session-based funnel requires a session identifier in the cohort and progression logic.

### 12.8 Attribution Differences

Acquisition attribution can vary according to first-touch, last-touch, or multi-touch rules.

The sample implementations assign the channel from the cohort-entry event.

This is a simplified first-touch cohort attribution model, not a complete marketing attribution system.

## 13. Security and Data Governance

Event analytics systems may process sensitive behavioral information.

Important controls include:

- Use pseudonymous user identifiers.
- Avoid storing passwords, payment credentials, and unnecessary personal information in event properties.
- Restrict access to raw events.
- Apply role-based database permissions.
- Validate incoming event payloads.
- Use parameterized database queries.
- Encrypt data in transit and at rest.
- Define retention and deletion policies.
- Audit access to analytical datasets.
- Restrict exported reports according to their data sensitivity.

The SQL sample demonstrates structural integrity and payload validation. Production deployments must also implement appropriate database roles, permissions, and retention controls.

## 14. Performance and Scalability

The sample programs use in-memory storage and are designed for learning and moderate datasets.

For large-scale event analytics, important considerations include:

| Concern | Engineering approach |
|---|---|
| High event volume | Batch ingestion |
| Duplicate delivery | Idempotency keys |
| Large event tables | Time-based partitioning |
| Repeated aggregation | Materialized views |
| User-level retrieval | Composite indexes |
| Expensive segmentation | Pre-aggregated cohorts |
| Late-arriving events | Event-time processing |
| Large reports | Pagination and incremental computation |
| Concurrent ingestion | Transactional storage |
| Long retention periods | Archival and retention policies |

For PostgreSQL, partitioning by event time can improve maintenance and query performance for large event tables.

For distributed systems, event-time watermarks and late-event handling are important when computing near-real-time conversion metrics.

## 15. Implementation Comparison

| Dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Primary focus | Analytical modeling | Event-driven processing | Efficient evaluation | Enterprise domain modeling | Relational analytics |
| Event storage | Dictionaries | Maps | Hash maps | Collections | Relational tables |
| Event notifications | Direct processing | EventEmitter | Explicit processing | Service-based | Database operations |
| Segmentation | Property dictionaries | Object properties | Channel/device filters | Policy objects | SQL grouping |
| Validation | Exceptions | Custom errors | Exceptions | Domain validation | Constraints and triggers |
| Reporting | JSON export | Async JSON export | Console reports | Structured reports | Views and queries |
| Dependencies | Standard library | Node.js standard library | STL | Java standard library | PostgreSQL |

## 16. Execution

### Python

Requirements: Python 3.10 or later.

File: `funnel_analytics.py`

Run using:

`python funnel_analytics.py`

### JavaScript

Requirements: Node.js 18 or later.

File: `funnel_analytics.js`

Run using:

`node funnel_analytics.js`

### C++17

Requirements: A C++17-compatible compiler.

File: `funnel_analytics.cpp`

Compile using:

`g++ -std=c++17 -O2 -Wall -Wextra funnel_analytics.cpp -o funnel_analytics`

Run using:

`./funnel_analytics`

On Windows:

`funnel_analytics.exe`

### Java 17

Requirements: Java 17 or later.

File: `FunnelAnalytics.java`

Compile using:

`javac FunnelAnalytics.java`

Run using:

`java FunnelAnalytics`

### PostgreSQL

Requirements: PostgreSQL 15 or later.

File: `funnel_analytics.sql`

Execute using:

`psql -U postgres -d your_database -f funnel_analytics.sql`

The SQL creates the `funnel_analytics` schema and its database objects.

The script includes sample users, funnel definitions, event records, validation mechanisms, reporting queries, and transactional ingestion.

The `gen_random_uuid()` function is provided by PostgreSQL's built-in UUID generation support in supported versions.

## 17. Testing and Expected Results

The sample dataset contains eight distinct users.

Their journeys produce the following expected progression:

| Measurement | Expected result |
|---|---:|
| Total users | 8 |
| Product viewers | 7 |
| Cart additions | 5 |
| Checkout users | 4 |
| Purchasers | 3 |
| Overall conversion | 37.50% |

The programs validate these results through assertions or explicit checks.

The SQL implementation provides corresponding retrieval and aggregation queries.

These expected figures apply to the supplied sample journeys and the configured 24-hour conversion window.
