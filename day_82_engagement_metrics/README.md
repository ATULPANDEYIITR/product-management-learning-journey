# Engagement Metrics: DAU, WAU, MAU, Stickiness, Frequency and Session Analytics

## 1. Introduction

Engagement metrics quantify how frequently users interact with a digital product, how many users return over time, and how deeply they interact during individual visits.

They are used to evaluate product adoption, recurring usage, user retention patterns, feature utilization and changes in customer engagement.

The implementations in this repository establish an event-based analytics system across Python, JavaScript, C++17, Java 17 and PostgreSQL.

The system covers:

- Daily Active Users (DAU).
- Weekly Active Users (WAU).
- Monthly Active Users (MAU).
- DAU/MAU stickiness.
- Event frequency.
- Session frequency.
- Session duration.
- Average sessions per user.
- Average events per session.
- Duplicate-event protection.
- Time-window calculations.
- Daily engagement reporting.

The implementations use the same sample business scenario while demonstrating different approaches to event processing, domain modeling, analytics computation and persistent storage.

## 2. Event-Based Engagement Measurement

### 2.1 Engagement events

An engagement event represents an observable interaction between a user and an application.

Examples include:

| Event | Description | Qualifies as activity |
|---|---|---|
| `login` | User authenticates | Yes |
| `page_view` | User views an application page | Yes |
| `action` | User performs an application action | Yes |
| `purchase` | User completes a purchase | Yes |
| `logout` | User ends an authenticated session | No |

The distinction between an event and an active-user event is important.

An event can exist in the analytics database without contributing to DAU, WAU or MAU.

For example, a logout event records application behavior but does not independently establish qualifying engagement.

### 2.2 Event data structure

Each event contains:

| Attribute | Purpose |
|---|---|
| Event ID | Unique identifier for duplicate detection |
| User ID | Identifies the interacting user |
| Event type | Describes the interaction |
| Timestamp | Records when the interaction occurred |
| Properties | Stores additional contextual information |

A representative event relationship is:

    Organization
        |
        +-- Users
              |
              +-- Engagement Events
                      |
                      +-- Event Type
                      +-- Timestamp
                      +-- Properties

The user identifier must remain consistent across events for accurate distinct-user calculations.

Anonymous identifiers, authenticated identifiers and device identifiers should not be treated as equivalent without an explicit identity-resolution policy.

## 3. Daily Active Users (DAU)

DAU represents the number of distinct users who perform at least one qualifying interaction during a calendar day.

Mathematically:

\[
DAU(d)=
\left|
\left\{
u:\exists e,\ 
e.user=u,\ e.time\in d
\right\}
\right|
\]

Where:

- \(d\) is the reporting day.
- \(u\) represents a unique user.
- \(e\) represents an engagement event.

A user performing 100 qualifying events on one day contributes one user to DAU.

Example:

| User | Qualifying events | DAU contribution |
|---|---:|---:|
| User 001 | 3 | 1 |
| User 002 | 2 | 1 |
| User 003 | 0 | 0 |
| User 004 | 1 | 1 |

DAU = 3.

The metric measures the size of the daily active audience rather than the volume of application interactions.

### Implementation

- Python uses a set of user identifiers.
- JavaScript uses a `Set`.
- C++17 uses `std::set`.
- Java uses stream-based distinct-user collection.
- PostgreSQL uses `COUNT(DISTINCT user_id)`.

Distinct-user counting prevents multiple events from the same user from artificially increasing the active-user count.

## 4. Weekly Active Users (WAU)

WAU measures distinct users with at least one qualifying event during a seven-day reporting window.

The implementation uses a rolling seven-day window that includes the reporting date.

\[
WAU(d)=
\left|
\bigcup_{i=0}^{6} ActiveUsers(d-i)
\right|
\]

For a report dated 19 November:

- 19 November is included.
- 18 November is included.
- 17 November is included.
- The remaining four preceding calendar days are included.

A user active on multiple days contributes only once.

WAU provides a broader engagement measurement than DAU.

It is particularly useful for applications whose normal usage frequency is several times per week rather than every day.

## 5. Monthly Active Users (MAU)

MAU measures distinct users with at least one qualifying interaction during a thirty-day rolling window.

\[
MAU(d)=
\left|
\bigcup_{i=0}^{29} ActiveUsers(d-i)
\right|
\]

For a report dated 19 November, the window begins on 21 October and ends at the end of 19 November.

MAU represents the size of the active audience over the monthly measurement window.

It should not be interpreted as the total number of registered accounts.

Registered users who have never interacted during the measurement window are excluded.

### DAU, WAU and MAU comparison

| Metric | Measurement window | Primary interpretation |
|---|---|---|
| DAU | One calendar day | Daily engagement |
| WAU | Seven calendar days | Weekly engagement |
| MAU | Thirty calendar days | Monthly engagement |

For identical event definitions and nested reporting windows:

\[
DAU \leq WAU \leq MAU
\]

This relationship provides a useful data-validation rule.

It does not mean that every user counted in MAU is active every day.

## 6. Stickiness

Stickiness measures how frequently the monthly active audience participates on a daily basis.

The DAU/MAU ratio is one of the most commonly used stickiness measurements.

\[
Stickiness=
\frac{DAU}{MAU}\times100
\]

Example:

- DAU = 2
- MAU = 4

\[
Stickiness=\frac{2}{4}\times100=50\%
\]

A stickiness value of 50% means that daily active users represent half the size of the thirty-day active audience on the selected reporting date.

It does not mean that exactly half of all monthly users return every day.

### Interpretation

| Stickiness | Interpretation |
|---|---|
| Increasing | Daily activity is increasing relative to the monthly audience |
| Decreasing | Daily activity is declining relative to the monthly audience |
| Stable | The daily-to-monthly engagement relationship is relatively consistent |
| Zero | No qualifying daily activity or no monthly active audience |

A zero-MAU condition must be handled explicitly to prevent division by zero.

### Important distinction

Stickiness is not a retention rate.

Retention measures whether users return after an initial interaction or acquisition event.

Stickiness compares active-user populations over different measurement windows.

A product can have high stickiness but poor new-user acquisition.

It can also have substantial MAU with relatively low daily engagement.

## 7. Event Frequency

Event frequency measures the number of qualifying interactions performed by a user within a specified period.

A simple event-frequency measurement is:

\[
Frequency(u,d)=
Count(QualifyingEvents(u,d))
\]

Example:

| User | Daily events |
|---|---:|
| User 001 | 3 |
| User 002 | 2 |
| User 003 | 0 |
| User 004 | 5 |

The total number of qualifying events is 10.

Event frequency is different from active-user counting.

One user can generate multiple events without increasing DAU beyond one.

### Frequency distribution

A frequency distribution groups users according to their number of sessions or interactions.

The implementations provide a session-frequency distribution.

| Sessions per user | Number of users |
|---:|---:|
| 1 | 2 |
| 2 | 1 |
| 3 | 4 |

This distribution helps identify:

- Single-session users.
- Repeat users.
- High-frequency users.
- Changes in application usage intensity.

High frequency does not necessarily indicate positive engagement.

Repeated error events, excessive retries and automated activity can inflate event counts.

Production analytics should therefore distinguish meaningful business interactions from technical and background events.

## 8. Session Analytics

### 8.1 Session definition

A session is a sequence of qualifying interactions performed by the same user without exceeding a configured inactivity threshold.

The implementations use a default inactivity timeout of 30 minutes.

For two consecutive events:

\[
Gap=t_{current}-t_{previous}
\]

A new session starts when:

\[
Gap>30\text{ minutes}
\]

If the gap is exactly 30 minutes, the events remain in the same session.

Example:

| Time | Event | Session |
|---|---|---|
| 09:00 | Login | Session 1 |
| 09:05 | Page view | Session 1 |
| 09:15 | Action | Session 1 |
| 11:00 | Login | Session 2 |

The second session begins because the inactivity gap exceeds the configured timeout.

### 8.2 Session attributes

| Attribute | Description |
|---|---|
| Session ID | Unique session identifier |
| User ID | Associated user |
| Start time | First qualifying event |
| Last event time | Final qualifying event |
| Event count | Number of qualifying interactions |
| Timeout | Inactivity threshold |
| Status | Active or completed |

### 8.3 Session duration

The implemented duration calculation is:

\[
SessionDuration=
LastEventTime-StartTime
\]

For a session starting at 09:00 and ending at 09:15:

\[
Duration=15\text{ minutes}
\]

This measures the elapsed time between observed qualifying events.

It does not measure verified foreground application time.

A session containing only one event has a measured duration of zero seconds.

### 8.4 Average session duration

\[
AverageSessionDuration=
\frac{\sum SessionDurations}
{TotalSessions}
\]

The calculation uses all sessions in the selected reporting population.

Idle periods after the final event are not included.

### 8.5 Average sessions per user

\[
AverageSessionsPerUser=
\frac{TotalSessions}
{DistinctSessionUsers}
\]

This metric measures the average number of sessions initiated by users who generated at least one session during the reporting period.

Users without sessions are excluded from this denominator.

### 8.6 Average events per session

\[
AverageEventsPerSession=
\frac{TotalQualifyingSessionEvents}
{TotalSessions}
\]

This metric describes interaction depth within sessions.

It should be interpreted alongside session duration and the event taxonomy.

## 9. Integrated Metrics Scenario

All five implementations use the same sample reporting scenario.

The reporting date is 19 November 2026.

| User | Activity date | Event count | Session behavior |
|---|---|---:|---|
| User 001 | 19 November | 4 | Two sessions |
| User 002 | 19 November | 2 | One session |
| User 003 | 17 and 18 November | 2 | Earlier activity |
| User 004 | 1 November | 1 | Outside the 30-day window |
| User 005 | 19 November | 1 logout | Not a qualifying user |

Expected engagement results:

| Metric | Expected result |
|---|---:|
| DAU | 2 |
| WAU | 3 |
| MAU | 4 |
| Stickiness | 50% |
| Qualifying events on 19 November | 6 |
| Sessions on 19 November | 3 |
| Average sessions per user | 1.50 |
| Average session duration | 600 seconds |
| Average events per session | 2.00 |

The session duration calculation is based on:

- User 001, first session: 15 minutes.
- User 001, second session: 0 minutes.
- User 002, first session: 10 minutes.

Therefore:

\[
AverageDuration=
\frac{900+0+600}{3}
=500\text{ seconds}
\]

The correct average session duration for the supplied scenario is 500 seconds.

The frequency distribution is:

| Sessions per user | Users |
|---:|---:|
| 1 | 1 |
| 2 | 1 |

The sample contains two users with sessions, three sessions in total.

## 10. Python Implementation

The Python implementation provides an object-oriented event analytics engine.

### Main components

| Component | Responsibility |
|---|---|
| `EventType` | Defines supported event categories |
| `EngagementEvent` | Validates event records |
| `Session` | Represents a grouped interaction sequence |
| `EngagementReport` | Stores calculated metrics |
| `EngagementAnalytics` | Performs ingestion and analytics |

### Important mechanisms

**Dataclasses**

Dataclasses provide structured event, session and report representations.

The immutable event dataclass prevents accidental changes to event attributes after construction.

**Sets**

The implementation uses sets for distinct-user counting and event-ID deduplication.

**Dictionaries**

Dictionaries group events and sessions by user.

**Sessionization**

Events are sorted chronologically within each user before session boundaries are calculated.

**Assertions**

The demonstration includes checks for expected DAU, WAU, MAU and stickiness values.

**Failure handling**

The implementation rejects:

- Missing event identifiers.
- Missing user identifiers.
- Naive timestamps.
- Invalid event types.
- Future event timestamps.
- Invalid session timeouts.

### Complexity

Let:

- \(n\) represent the number of stored events.
- \(u\) represent the number of users.

Distinct-user calculations require approximately \(O(n)\) time.

Session generation requires \(O(n\log n)\) time in the general case because of chronological sorting.

The implementation retains events in memory, making it suitable for learning, demonstrations and moderate datasets rather than unrestricted production ingestion.

## 11. JavaScript Implementation

The JavaScript implementation uses an event-driven architecture.

### Main components

| Component | Responsibility |
|---|---|
| `EngagementStore` | Stores events and maintains indexes |
| `validateEvent()` | Validates incoming records |
| `uniqueUsers()` | Calculates distinct active users |
| `buildSessions()` | Generates session boundaries |
| `calculateDaily()` | Produces engagement reports |
| `getUserFrequency()` | Calculates session frequency |

### Event-driven processing

The implementation extends Node.js `EventEmitter`.

Three application events are supported:

- `event:accepted`
- `event:rejected`
- `metrics:calculated`

This separates event ingestion from reporting and monitoring.

A downstream component can subscribe to these events without modifying the analytics calculations.

### Asynchronous ingestion

The `ingest()` and `ingestBatch()` methods return promises.

Batch ingestion handles individual event failures without discarding all other valid records.

### Data structures

| Structure | Purpose |
|---|---|
| `Set` | Event deduplication and distinct users |
| `Map` | User-to-event indexing |
| Arrays | Event storage and chronological processing |
| Frozen objects | Prevent accidental modification of stored records |

### Operational considerations

The in-memory event store does not provide durable storage.

Production systems require persistent event storage, durable message processing, retry policies and transactional deduplication.

A distributed implementation should also handle out-of-order event delivery and concurrent duplicate submissions.

## 12. C++17 Implementation

The C++17 implementation uses an explicit domain model and standard-library containers.

### Main components

| Component | Responsibility |
|---|---|
| `EventType` | Defines interaction categories |
| `Event` | Stores and validates events |
| `Session` | Represents a session |
| `Metrics` | Holds computed metrics |
| `EngagementEngine` | Performs aggregation and sessionization |

### Engineering decisions

`std::unordered_set` provides efficient average-case duplicate detection.

`std::unordered_map` groups events by user.

`std::set` provides distinct-user collections.

`std::map` maintains an ordered session-frequency distribution.

The implementation uses integer Unix timestamps to make elapsed-time calculations independent of string formatting.

The caller must supply timestamps normalized to UTC.

### Performance characteristics

| Operation | Expected complexity |
|---|---|
| Event ID lookup | Average \(O(1)\) |
| Event ingestion | Average \(O(1)\) |
| User grouping | Average \(O(n)\) |
| Event sorting | \(O(n\log n)\) |
| Session construction | \(O(n)\) after sorting |
| Distinct-user counting | \(O(n\log u)\) with ordered sets |

The implementation avoids third-party dependencies and uses C++17 standard-library functionality.

For very large event streams, a production implementation would use partitioned storage, incremental aggregation and bounded processing windows.

## 13. Java 17 Enterprise Implementation

The Java implementation separates domain objects, event persistence, session generation and reporting services.

### Domain types

The enterprise model uses:

- `User` record.
- `EngagementEvent` record.
- `Session` record.
- `EngagementPolicy` record.
- `EngagementReport` record.

Records provide concise immutable data representations.

### Service separation

**EventRepository**

Maintains event records and user-level event indexes.

It rejects duplicate event identifiers.

**SessionService**

Converts ordered qualifying events into sessions using the configured inactivity threshold.

**EngagementService**

Calculates active-user populations, session statistics and stickiness.

**EngagementPolicy**

Centralizes the reporting configuration.

The policy explicitly defines:

- Session timeout.
- Weekly measurement window.
- Monthly measurement window.
- Reporting timezone.

### Enterprise considerations

The repository uses synchronized methods for thread-safe access within one application process.

This does not provide distributed concurrency control.

A multi-instance service requires database transactions, unique constraints and coordinated event ingestion.

The policy object also makes it possible to test different reporting configurations without changing the underlying metric algorithms.

## 14. PostgreSQL Data Model

The SQL implementation provides persistent relational storage and analytical processing.

### Entity relationships

    Organizations
         |
         +---- Users
                  |
                  +---- Engagement Events
                  |         |
                  |         +---- Event Types
                  |
                  +---- Analytics Sessions

    Organizations
         |
         +---- Daily Engagement Metrics

### Tables

| Table | Purpose |
|---|---|
| `organizations` | Stores application or business organizations |
| `users` | Stores organization-specific user identities |
| `event_types` | Defines activity qualification |
| `engagement_events` | Stores individual interactions |
| `analytics_sessions` | Stores sessionized activity |
| `daily_engagement_metrics` | Stores daily reporting results |

### Referential integrity

Foreign keys ensure that events reference existing users and event types.

A trigger verifies that an event and its associated user belong to the same organization.

The unique event UUID prevents duplicate event insertion.

The session constraints prevent negative durations and invalid timeout values.

### JSONB

The `properties` column stores additional event attributes using PostgreSQL JSONB.

This allows event-specific information without creating a separate relational column for every possible property.

A GIN index supports searches against JSONB attributes.

Frequently queried business dimensions should still be promoted into appropriately indexed relational columns when justified by workload measurements.

### Window functions

The session-generation function uses:

- `LAG()` to retrieve the preceding event timestamp.
- Conditional expressions to identify new sessions.
- `SUM() OVER` to assign session sequence numbers.
- Grouping operations to calculate session boundaries.

These operations implement sessionization directly in the database.

### Common table expressions

CTEs separate the session-generation stages:

1. Ordered event retrieval.
2. Previous-event identification.
3. Session-boundary detection.
4. Session numbering.
5. Session aggregation.
6. Persistent session insertion.

This makes the analytical workflow easier to inspect and maintain.

### Metric persistence

The daily metrics table uses a unique organization/date constraint.

The calculation function uses `INSERT ... ON CONFLICT DO UPDATE`.

Repeated calculations therefore update the reporting record instead of creating duplicate daily metric rows.

## 15. Time Windows and Timezone Handling

Time handling is fundamental to engagement analytics.

A timestamp can represent the same instant differently across geographic regions.

The implementations normalize sample timestamps to UTC.

The SQL implementation uses `TIMESTAMPTZ`.

The Java implementation uses `Instant` and an explicit UTC reporting policy.

The Python implementation requires timezone-aware timestamps.

The JavaScript implementation normalizes event timestamps through ISO 8601.

The C++ implementation uses integer epoch timestamps and expects UTC-normalized input.

### Calendar windows versus rolling windows

A calendar-month metric and a rolling thirty-day metric are different measurements.

This repository uses:

- DAU: one UTC calendar day.
- WAU: seven calendar days including the reporting date.
- MAU: thirty calendar days including the reporting date.

A production dashboard should explicitly disclose the selected window definitions.

A reporting system using local business dates must calculate calendar boundaries using the configured business timezone.

Daylight-saving transitions can cause local calendar days to contain 23 or 25 hours.

UTC avoids this particular ambiguity for globally consistent daily reporting, but it may not match a product's local operating calendar.

## 16. Data Quality and Reliability

### Duplicate events

Distributed event delivery frequently uses at-least-once processing.

An event may be delivered more than once.

Without deduplication, duplicate events can inflate event frequency and session counts.

The implementations use event identifiers to detect repeated submissions.

PostgreSQL enforces uniqueness through `event_uuid`.

For distributed ingestion, deduplication must be atomic with event persistence.

### Late-arriving events

An event may arrive after its actual occurrence time.

Examples include:

- Mobile devices operating offline.
- Network interruptions.
- Delayed message delivery.
- Batch synchronization.
- Application retries.

The event timestamp should represent occurrence time, while the ingestion timestamp should represent receipt time.

These are separate concepts.

Production reporting should define an allowed lateness interval and a correction policy for previously calculated metrics.

### Identity resolution

A single individual may use multiple devices or authentication identities.

Without identity resolution, one individual may be counted as several users.

Identity merging must use governed identifiers and should not rely on unreliable assumptions such as matching display names.

### Automated activity

Bots, monitoring services and automated testing can create qualifying-looking events.

Production event classification should distinguish genuine user interactions from automated activity.

### Event taxonomy

Changing the activity definition changes the meaning of DAU, WAU and MAU.

For example, adding passive background events to the qualifying event list may substantially increase the reported audience.

Metric definitions should therefore be version-controlled and documented.

## 17. Performance and Scalability

### Application-level processing

The Python, JavaScript, C++ and Java implementations use in-memory collections.

Their main advantage is transparent execution and straightforward validation.

Their primary limitation is memory consumption as event volume increases.

For larger systems, suitable architectural components include:

- Partitioned event storage.
- Incremental distinct-user aggregation.
- Time-based data partitioning.
- Event-stream processing.
- Precomputed daily activity tables.
- Materialized reporting tables.
- Controlled retention policies.

### Database optimization

The PostgreSQL implementation includes indexes on:

- Organization and event timestamp.
- Organization, user and event timestamp.
- Event type and timestamp.
- Session organization, user and start time.
- Organization and reporting date.

Index selection should be evaluated against actual query plans and data distribution.

Indexes consume storage and increase write costs.

A composite index should reflect the filtering and ordering patterns of the actual workload.

### Distinct-user aggregation

Distinct-user counting can become expensive when event volumes increase.

Incremental aggregation can reduce repeated scanning.

For example, an organization/date/user activity table can record one qualifying activity entry per user per date.

Daily active users can then be calculated from distinct user records rather than every underlying event.

Any incremental approach must handle late events, corrections and deduplication consistently.

## 18. Security and Privacy

Engagement events may contain sensitive behavioral information.

A production analytics platform should implement:

- Access controls based on organizational boundaries.
- Parameterized SQL queries.
- Secure event ingestion.
- Encryption in transit and at rest.
- Controlled retention periods.
- Auditable administrative access.
- Data minimization.
- Appropriate pseudonymization.
- Restricted access to event properties.
- Protection against unauthorized user identification.

Event properties should not contain passwords, authentication tokens, payment credentials or unnecessary personal information.

The organization-level relationships in the SQL model provide an initial basis for data separation.

They are not a substitute for production authorization policies or PostgreSQL row-level security.

## 19. Limitations of the Implementations

The five implementations deliberately use a common measurement definition, but they do not constitute a distributed production analytics platform.

| Area | Current implementation | Production consideration |
|---|---|---|
| Event storage | In-memory in four programs | Durable event storage |
| SQL storage | PostgreSQL relational tables | Partitioning and workload tuning |
| Identity | One user identifier per event | Governed identity resolution |
| Timezone | UTC | Business-specific reporting calendars |
| Sessions | Inactivity-based | Background and multi-device behavior |
| Late events | Basic timestamp validation | Watermarks and historical recalculation |
| Deduplication | Unique event identifiers | Atomic distributed idempotency |
| Reporting | Direct aggregation | Incremental and scheduled aggregation |
| Security | Input validation | Authentication, authorization and auditing |
| Retention | No automated expiry | Configurable data lifecycle |

Session duration is estimated from observed events rather than continuous user-presence measurement.

The thirty-day MAU definition is a rolling window, not a calendar-month definition.

These distinctions should remain visible in any business reporting that uses the calculated metrics.

## 20. Technical Comparison

| Dimension | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Main purpose | Analytics simulation | Event-driven analytics | Efficient processing engine | Enterprise domain services | Persistent analytics |
| Event storage | List | Array and Map | Vector | Repository collections | Relational table |
| Deduplication | Set | Set | Unordered set | HashMap | Unique constraint |
| User grouping | Dictionary | Map | Unordered map | Streams and maps | SQL grouping |
| Session processing | Classes | Event processing | STL algorithms | Session service | Window functions |
| Reporting | Dataclass | Immutable object | Struct | Record | Reporting table |
| Validation | Exceptions | Custom errors | Exceptions | Domain validation | Constraints and triggers |
| Persistence | None | None | None | None | Yes |

## 21. Practical Interpretation of Engagement Metrics

Engagement metrics should be interpreted as a connected measurement framework rather than independent performance indicators.

| Business question | Relevant metric |
|---|---|
| How many users interact daily? | DAU |
| How many users return during a week? | WAU |
| How large is the active monthly audience? | MAU |
| How does daily engagement compare with monthly engagement? | Stickiness |
| How frequently do users interact? | Event frequency |
| How often do users initiate separate visits? | Session frequency |
| How long do observed sessions last? | Average session duration |
| How many interactions occur within a session? | Events per session |

DAU, WAU and MAU measure audience size across different periods.

Stickiness measures the relationship between daily and monthly activity.

Frequency measures interaction volume or visit frequency.

Session metrics describe how interactions are grouped and distributed over time.

Together, these measurements provide a structured basis for analyzing digital product engagement, identifying behavioral changes and evaluating the effectiveness of product improvements.
