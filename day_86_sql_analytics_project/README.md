# Product SQL Analytics Project

## Project Description

This project implements a product analytics system for an e-commerce business. It examines product performance, customer behavior, purchasing patterns, conversion funnels, customer retention, and customer segmentation.

The project uses five complementary implementations:

- Python: object-oriented analytics and reporting.
- JavaScript: event-driven ingestion and asynchronous analytics.
- C++17: an indexed analytics engine using STL data structures.
- Java 17: an enterprise-oriented analytics service with immutable domain records.
- PostgreSQL: a relational analytics database with views, window functions, constraints, indexes, triggers, and stored procedures.

The implementations share a consistent business domain and sample dataset. Their internal algorithms and engineering approaches differ.

## Business Scenario

An online retailer collects customer interactions throughout the purchasing process.

A typical customer journey is:

Customer Registration
        |
        v
Product Discovery
        |
        v
Product View
        |
        v
Add to Cart
        |
        v
Checkout
        |
        v
Purchase
        |
        v
Repeat Purchase / Refund

The business needs to answer questions such as:

- Which products generate the most revenue?
- Which products attract attention but fail to convert?
- How many customers progress through each purchasing stage?
- Where do customers abandon the purchase process?
- Which customer acquisition channels produce buyers?
- How many customers return after registration?
- Which customers are valuable, loyal, dormant, or at risk?
- How does customer purchasing behavior change over time?

## 1. Data Model

The system uses four primary domain entities.

| Entity | Purpose | Important attributes |
|---|---|---|
| Customer | Represents a registered buyer | Customer ID, registration date, channel, region |
| Product | Represents a catalog item | Product ID, category, price, cost |
| Event | Represents an interaction | Event ID, customer, product, event type, timestamp |
| Session | Groups related interactions | Session ID, customer activity, chronological events |

The PostgreSQL implementation also maintains a customer segmentation snapshot table.

### Customer

A customer represents an individual registered with the retailer.

Important attributes:

- `customer_id`: unique identifier.
- `registration_date`: date of registration.
- `acquisition_channel`: source through which the customer was acquired.
- `region`: geographical classification.

Acquisition channels include Organic, Paid Search, Social, and Referral.

### Product

A product represents an item available for purchase.

Its attributes include:

- Product identifier.
- Product name.
- Product category.
- Selling price.
- Unit cost.
- Active status.

Product price and cost are separate because revenue and profitability are different measurements.

### Event

An event represents an observable customer action.

The project defines five event types.

| Event | Meaning | Financial transaction |
|---|---|---|
| `view` | Customer views a product | No |
| `add_to_cart` | Customer adds a product to a cart | No |
| `checkout` | Customer initiates checkout | No |
| `purchase` | Customer completes a purchase | Yes |
| `refund` | A purchase value is refunded | Financial adjustment |

An event has a timestamp, customer identifier, product identifier, quantity, and optional session identifier.

A purchase event contains its transaction amount. Refunds are recorded separately.

This separation prevents product views and cart actions from being incorrectly interpreted as revenue.

## 2. Product Dataset Analysis

Product analysis evaluates commercial performance at the product and category levels.

### Core measurements

**Product views**

The number of recorded product-view events.

**Cart events**

The number of times customers add the product to a cart.

**Purchase events**

The number of recorded purchase transactions.

**Units sold**

The total purchased quantity.

**Unique buyers**

The number of distinct customers who purchased the product.

**Gross revenue**

The sum of purchase transaction amounts.

**Net revenue**

Gross revenue minus recorded refunds.

**Estimated cost**

Units sold multiplied by the product's unit cost.

**Estimated margin**

Net revenue minus estimated cost.

The margin calculation is an approximation. It does not include shipping, taxes, payment-processing charges, discounts, operating costs, or inventory adjustments.

### Conversion measurements

View-to-cart conversion:

`Cart Events / Product Views × 100`

Cart-to-purchase conversion:

`Purchase Events / Cart Events × 100`

View-to-purchase conversion:

`Purchase Events / Product Views × 100`

These calculations measure event-level ratios. They should not be confused with unique-customer conversion rates.

### Category analysis

Category analysis aggregates products into broader commercial groups.

For example:

| Category | Products |
|---|---|
| Electronics | Laptop Pro |
| Accessories | Wireless Mouse, Mechanical Keyboard, USB-C Hub |
| Wearables | Smart Watch |

Category analysis helps identify which product groups contribute most to revenue and estimated margin.

The SQL implementation uses `GROUP BY` and aggregate functions. The other implementations aggregate events through dictionaries, maps, and indexed collections.

## 3. Conversion Funnel Analysis

A conversion funnel measures customer progression through the purchasing process.

The standard funnel contains four stages:

| Stage | Event | Business interpretation |
|---|---|---|
| 1 | View | Customer discovers a product |
| 2 | Add to Cart | Customer expresses purchasing interest |
| 3 | Checkout | Customer begins transaction completion |
| 4 | Purchase | Customer completes a transaction |

### User-level funnel

The user-level funnel counts distinct customers who performed each event during a reporting period.

For example:

| Stage | Customers |
|---|---:|
| View | 100 |
| Add to Cart | 60 |
| Checkout | 40 |
| Purchase | 25 |

Conversion from the previous stage:

`Current Stage Customers / Previous Stage Customers × 100`

Conversion from the initial stage:

`Current Stage Customers / View Customers × 100`

The difference between these calculations is important.

The first measures progression between adjacent stages. The second measures the proportion of initial viewers reaching a particular stage.

The Python, JavaScript, C++, and Java implementations use distinct customer sets to avoid counting one customer multiple times at the same stage.

The PostgreSQL implementation uses conditional aggregation and window functions.

### Session-level funnel

A user-level funnel and a session-level funnel answer different questions.

A customer can view a product during one session and purchase it during another session.

A session-level funnel groups events by session identifier and evaluates the progression of events within that session.

The project includes an ordered session-funnel implementation that requires the following progression:

`View → Add to Cart → Checkout → Purchase`

The ordered session calculation prevents a purchase event from automatically qualifying as a complete funnel when the earlier required stages are absent.

### Funnel limitations

The sample implementations use a simplified stage-presence or chronological event-sequence model.

A production funnel may also require:

- Session timeout rules.
- Event deduplication.
- Attribution windows.
- Multiple product interactions.
- Cross-device identity resolution.
- Explicit order identifiers.
- Repeated checkout attempts.
- Late-arriving events.

A purchase event should ideally be associated with a unique order identifier to distinguish transaction counts from repeated event delivery.

## 4. Customer Retention Analysis

Retention analysis determines whether customers return after their initial registration or acquisition.

### Cohort analysis

A cohort is a group of customers sharing a common starting characteristic.

This project uses registration month as the cohort definition.

For example:

- January cohort: customers registered in January.
- February cohort: customers registered in February.
- March cohort: customers registered in March.
- April cohort: customers registered in April.

Each cohort is observed across subsequent calendar months.

### Retention rate

The retention formula is:

`Active Customers in Period / Original Cohort Size × 100`

Suppose a cohort contains 100 customers.

| Month | Active customers | Retention |
|---|---:|---:|
| Month 0 | 100 | 100% |
| Month 1 | 70 | 70% |
| Month 2 | 55 | 55% |
| Month 3 | 40 | 40% |

This table illustrates how customer activity changes over time.

### Cohort retention matrix

The SQL implementation produces a monthly cohort report with:

- Cohort month.
- Activity month.
- Month number.
- Cohort size.
- Active customer count.
- Retention percentage.

A retention matrix allows analysts to compare different acquisition cohorts.

For example, a February cohort can be compared with a March cohort to determine whether newer customers demonstrate stronger repeat activity.

### Retention definition

The sample implementations define activity as the presence of any recorded event.

This includes product views and other interactions.

Consequently, the metric measures behavioral activity rather than repeat purchasing.

A stricter commercial retention metric should define activity using purchase events or another clearly specified qualifying action.

### Calendar-month and observation-window considerations

Customers registered near the end of a month have less observation time than customers registered at its beginning.

The SQL implementation uses calendar-month cohorts. A production analysis should distinguish incomplete observation periods from genuine customer inactivity.

Alternative retention definitions include:

- Day-one retention.
- Day-seven retention.
- Day-thirty retention.
- Weekly retention.
- Monthly purchasing retention.
- Rolling retention.

## 5. Customer Segmentation

Customer segmentation divides customers into meaningful groups based on their behavior.

This project implements RFM segmentation.

RFM represents:

- Recency.
- Frequency.
- Monetary value.

### Recency

Recency measures how recently a customer completed a purchase.

`Recency = Reference Date - Latest Purchase Date`

A smaller recency value generally indicates more recent purchasing activity.

### Frequency

Frequency measures the number of purchase transactions recorded for a customer.

`Frequency = Number of Purchase Events`

In a production database, transaction frequency should normally use distinct order identifiers rather than raw event counts.

### Monetary value

Monetary value represents the customer's net purchasing value.

`Monetary = Purchase Value - Refund Value`

The implementation rejects negative monetary values because the sample segmentation rules assume non-negative net customer purchasing value.

### Implemented customer segments

| Segment | Rule |
|---|---|
| Champions | Recency at most 30 days, at least 3 purchases, monetary value at least 5,000 |
| Loyal Customers | Recency at most 60 days and at least 2 purchases |
| Recent Customers | Recency at most 30 days and exactly 1 purchase |
| At Risk | Recency greater than 90 days and at least 2 purchases |
| Dormant | Recency greater than 180 days |
| Regular Customers | Other customers with purchases |
| No Purchase | No recorded purchase |

These are illustrative business rules rather than statistically calibrated segment boundaries.

### Practical interpretation

**Champions**

Customers with recent, repeated, and substantial purchasing activity.

**Loyal Customers**

Customers who demonstrate repeat purchasing behavior.

**Recent Customers**

Customers who have recently completed their first purchase.

**At Risk**

Previously purchasing customers who have not purchased recently.

**Dormant**

Customers whose latest purchase is substantially older.

**Regular Customers**

Customers who do not satisfy the other specified conditions.

**No Purchase**

Registered customers without recorded purchases.

The segmentation model can support targeted retention campaigns, loyalty programs, customer reactivation, and differentiated communication.

## 6. Acquisition Channel Analysis

Acquisition analysis evaluates the contribution of different customer acquisition sources.

The project includes:

- Organic.
- Paid Search.
- Social.
- Referral.

### Important measurements

**Visitors**

Distinct customers with at least one product-view event.

**Buyers**

Distinct customers with at least one purchase event.

**Revenue**

Purchase revenue less recorded refunds.

**Conversion rate**

`Distinct Buyers / Distinct Visitors × 100`

**Revenue per buyer**

`Net Revenue / Distinct Buyers`

A channel producing the largest number of visitors does not necessarily produce the largest revenue.

The analysis therefore separates traffic generation from commercial performance.

A complete marketing attribution system would also require campaign identifiers, attribution windows, touchpoint ordering, advertising expenditure, and attribution methodology.

## 7. Python Implementation

The Python implementation models the analytics domain through dataclasses, enumerations, dictionaries, sets, and a central analytics engine.

### Main components

| Component | Responsibility |
|---|---|
| `Product` | Product validation and financial attributes |
| `Customer` | Registration and acquisition information |
| `Event` | Validated customer interaction |
| `AnalyticsEngine` | Product, funnel, retention, and segmentation calculations |

### Technical mechanisms

- Dictionaries provide direct product and customer lookup.
- Sets provide distinct-customer counting.
- Event indexes support customer- and product-level analysis.
- Dataclasses provide structured immutable domain records.
- Enumerations restrict valid event categories.
- Exceptions reject invalid data.
- CSV and JSON modules generate persistent reports.
- Assertions validate important execution conditions.

The script uses only the Python standard library.

### Generated reports

The script creates an `analytics_output` directory containing:

- `product_performance.json`
- `conversion_funnel.json`
- `session_funnel.json`
- `retention.json`
- `segmentation.json`
- `channel_performance.json`
- `data_quality.json`
- `product_performance.csv`
- `segmentation.csv`

## 8. JavaScript Implementation

The JavaScript implementation emphasizes event ingestion, asynchronous processing, and operational reporting.

### Main components

| Component | Responsibility |
|---|---|
| `Product` | Product domain validation |
| `Customer` | Customer domain validation |
| `EventStore` | Event storage and indexing |
| `AnalyticsService` | Analytical calculations |
| `ReportExporter` | JSON and CSV export |

### Event-driven architecture

The `EventStore` extends Node.js `EventEmitter`.

When a valid event is inserted, the store emits an event notification.

This separates event ingestion from event listeners and allows the architecture to support additional processing subscribers.

### Asynchronous batch processing

The `ingestBatch()` method:

- Accepts an event collection.
- Validates batch size.
- Processes events in batches.
- Records individual validation failures.
- Allows the event loop to process other work between batches.
- Returns insertion and rejection statistics.

A rejected event does not prevent unrelated valid events in the same batch from being processed.

### Operational considerations

The implementation uses private class fields and `Map` collections to protect internal state.

The exporter writes to a temporary file before renaming it to the final destination. This reduces the risk of exposing partially written reports.

The CSV exporter also applies basic spreadsheet formula-injection protection.

The in-memory event store is suitable for learning and bounded workloads. Production ingestion requires durable storage, transactional persistence, concurrency controls, and explicit duplicate-event policies.

## 9. C++17 Implementation

The C++ implementation focuses on efficient domain processing and explicit data structures.

### Main components

- `Product`
- `Customer`
- `Event`
- `ProductMetrics`
- `CustomerMetrics`
- `AnalyticsEngine`

### Data structures

| Structure | Application |
|---|---|
| `unordered_map` | Product and customer lookup |
| `unordered_set` | Duplicate-event detection |
| `unordered_set` | Distinct customer counting |
| `vector` | Event storage |
| `map` | Ordered reports |
| `array` | Fixed conversion-funnel stages |

The engine validates identifiers, customer relationships, product relationships, monetary amounts, and event chronology.

The implementation uses indexed customer events to avoid repeatedly scanning the complete event collection during customer segmentation.

The program uses no external dependencies.

## 10. Java 17 Implementation

The Java implementation models the analytics system as an enterprise-oriented service.

### Domain design

Java records represent:

- `Product`
- `Customer`
- `Event`
- `DateRange`
- `ProductReport`
- `FunnelReport`
- `RetentionReport`
- `CustomerReport`
- `ChannelReport`
- `QualityReport`

Enumerations define event types, funnel stages, and customer segments.

### Repository layer

`EventRepository` manages domain records and validates relationships.

It maintains:

- Product lookup.
- Customer lookup.
- Event storage.
- Customer event indexes.
- Event-count tracking.

The repository uses concurrent collections and synchronized insertion to protect its in-memory state.

### Service layer

`ProductAnalyticsService` provides separate methods for:

- Product performance.
- Conversion funnel.
- Ordered session funnel.
- Cohort retention.
- Customer segmentation.
- Channel performance.
- Data quality.

Immutable report records provide structured outputs.

The implementation uses Java streams for transformations and sorting where they improve readability.

The in-memory repository is not a replacement for a transactional database. A production system would normally use a persistence layer with database transactions, durable event identifiers, and carefully defined isolation behavior.

## 11. PostgreSQL Database Architecture

PostgreSQL provides the relational foundation for persistent analytical queries.

### Schema structure

The project creates the `product_analytics` schema.

Its principal tables are:

| Table | Purpose |
|---|---|
| `customers` | Customer registration and acquisition data |
| `products` | Product catalog and financial attributes |
| `analytics_events` | Customer interaction and transaction events |
| `customer_segments` | Calculated customer segmentation snapshots |

### Relationships

`customers.customer_id` is referenced by `analytics_events.customer_id`.

`products.product_id` is referenced by `analytics_events.product_id`.

`customer_segments.customer_id` references the customer table.

These foreign-key relationships prevent events and segmentation records from referencing nonexistent customers or products.

### Constraints

The database uses:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Not-null constraints.
- A trigger validating event chronology.

The trigger prevents an event from being recorded before the associated customer's registration date.

### Indexing

The SQL script creates indexes for:

- Event timestamps.
- Customer and event timestamp combinations.
- Product and event timestamp combinations.
- Event type and timestamp combinations.
- Session identifiers.
- Customer acquisition channels.
- Registration dates.
- Product categories.
- JSONB event metadata.

The indexes are intended to support common reporting filters and joins.

Their usefulness should be validated against actual query plans and production data distributions.

## 12. PostgreSQL Analytical Techniques

### Aggregate functions

The project uses:

- `COUNT`
- `COUNT(DISTINCT ...)`
- `SUM`
- `AVG`
- `MAX`
- `FILTER`
- `COALESCE`
- `NULLIF`

Conditional aggregation calculates different event categories without requiring separate queries for every metric.

### Common Table Expressions

CTEs divide analytical calculations into understandable stages.

The retention and revenue queries use CTEs to separate intermediate aggregation from final reporting.

### Window functions

The project uses:

- `LAG()` for previous-stage and previous-month comparisons.
- `FIRST_VALUE()` for initial funnel conversion.
- `ROW_NUMBER()` for chronological session event ordering.
- Windowed aggregation for cohort reporting.

These functions allow calculations across related rows without collapsing the complete dataset into a single aggregate result.

### Views

The database defines reusable views:

- `product_performance`
- `conversion_funnel`
- `monthly_customer_activity`
- `customer_cohorts`
- `cohort_retention`
- `customer_rfm`
- `customer_segmentation`
- `channel_performance`
- `customer_value`
- `data_quality_report`

Views centralize analytical definitions and reduce repeated query logic.

### Stored procedure

`refresh_customer_segments()` calculates current customer metrics and stores their segmentation results.

It uses `INSERT ... ON CONFLICT DO UPDATE` to refresh existing customer snapshots without creating duplicate customer records.

The procedure accepts a reference date, allowing the segmentation calculation to be reproduced for a specific reporting date.

### Transactions

The SQL script uses an explicit transaction.

It also demonstrates a savepoint and rollback for an intentionally invalid event insertion.

The trigger rejects the event because its timestamp predates customer registration.

## 13. Data Quality and Validation

Reliable analytics depends on the quality of the underlying event data.

The project implements several validation controls.

| Validation | Purpose |
|---|---|
| Unique event identifiers | Reject duplicate event records |
| Foreign keys | Prevent unknown customer and product references |
| Event type constraints | Restrict supported event categories |
| Positive quantities | Prevent invalid units |
| Non-negative amounts | Reject invalid transaction values |
| Registration chronology | Prevent pre-registration events |
| Valid timestamps | Reject invalid or missing dates |
| Refund accounting | Subtract refunds from purchase value |
| Reference-date checks | Prevent invalid recency calculations |

### Important production data-quality concerns

The sample dataset does not fully model:

- Duplicate order notifications.
- Partial refunds.
- Multiple-currency transactions.
- Tax and shipping treatment.
- Chargebacks.
- Returns involving multiple products.
- Event delivery delays.
- Device identity resolution.
- Bot-generated traffic.
- Event schema versioning.

A production implementation should maintain an explicit event contract and a separate transaction or order model.

## 14. Performance Considerations

### Python

Dictionary and set operations provide average constant-time lookup and membership checks.

Event indexing reduces repeated customer and product searches.

Sorting analytical reports introduces an additional sorting cost.

### JavaScript

`Map` and `Set` provide efficient keyed access and distinct-customer tracking.

Batch ingestion avoids processing an arbitrarily large input collection in a single uninterrupted event-loop operation.

The sample implementation still maintains an in-memory copy of all events, so memory consumption increases with event volume.

### C++17

`unordered_map` and `unordered_set` provide average constant-time lookup and membership checks.

Vectors provide efficient sequential iteration.

Ordered maps are used where sorted reporting is useful.

Hash-table performance can degrade under unfavorable collision patterns, and memory consumption must be considered when scaling event storage.

### Java 17

Concurrent collections support concurrent read access and synchronized insertion.

The service uses customer-level event indexes for repeated segmentation calculations.

For high-volume workloads, aggregation should move closer to the database or into dedicated streaming and analytical infrastructure.

### PostgreSQL

Indexes reduce the need for full-table scans when query predicates match indexed columns.

The script uses composite indexes for common customer and product reporting patterns.

`EXPLAIN (ANALYZE, BUFFERS)` demonstrates how to inspect execution plans and buffer usage.

Large analytical datasets may benefit from:

- Date-based table partitioning.
- Materialized views.
- Incremental aggregation.
- Precomputed cohort tables.
- Summary tables.
- Appropriate vacuum and analyze operations.
- Workload-specific index tuning.

Indexes consume storage and increase write costs. Adding indexes without evaluating query patterns can reduce ingestion performance.

## 15. Business Interpretation

The analytical outputs support several practical business decisions.

| Analytical result | Potential business application |
|---|---|
| High views, low purchases | Investigate product pricing, content, or checkout friction |
| High cart activity, low checkout completion | Examine shipping costs and checkout usability |
| High revenue, low estimated margin | Review product costs and pricing |
| Strong customer retention | Identify successful acquisition cohorts |
| Weak customer retention | Examine onboarding and repeat-purchase behavior |
| Champions segment | Evaluate loyalty and premium customer programs |
| At Risk segment | Prioritize customer reactivation |
| Dormant segment | Evaluate re-engagement campaigns |
| High channel revenue | Examine channel investment efficiency |
| High visitors, low conversion | Investigate traffic quality and targeting |

These are analytical signals, not automatic proof of causation.

For example, a weak conversion rate may be associated with pricing, stock availability, product descriptions, acquisition quality, or other factors. Further investigation is required before selecting an intervention.

## 16. Important Analytical Distinctions

| Concept | What it measures | What it does not automatically measure |
|---|---|---|
| Product views | Recorded product-view events | Unique customers |
| Purchase events | Recorded transaction events | Number of unique orders |
| Revenue | Recorded transaction value | Profit |
| Estimated margin | Revenue less estimated product cost | Net accounting profit |
| User-level funnel | Distinct users at each stage | Ordered progression |
| Session-level funnel | Progression within sessions | Cross-session purchasing behavior |
| Retention | Return activity under a specified definition | Repeat purchases unless explicitly defined |
| RFM segmentation | Historical customer purchasing behavior | Future customer value |
| Channel conversion | Observed channel-associated conversion | Causal marketing effectiveness |

The definitions matter because apparently similar metrics can produce different results.

## 17. Limitations

The five implementations share a simplified analytical model.

The sample data is synthetic and intended for reproducible testing.

The Python, JavaScript, C++, and Java programs use in-memory storage. They do not provide persistent transactional event storage.

The PostgreSQL implementation provides persistent relational structures, but its sample analytical definitions require further refinement before production deployment.

Specific limitations include:

- No complete order and order-item data model.
- No explicit campaign attribution.
- No multi-currency normalization.
- No identity resolution across devices.
- No formal bot filtering.
- No incremental event-processing checkpoint.
- No statistical significance testing.
- No predictive churn model.
- No experimentally validated segmentation thresholds.
- No full financial accounting model.

The retention implementation uses recorded activity rather than a universally standardized retention definition.

The funnel calculations use simplified stage-presence and chronological sequencing rules. A production funnel should define session boundaries, conversion windows, event deduplication, and attribution explicitly.

The RFM rules are business-defined thresholds. They should be calibrated using the actual distribution of customer behavior.

The estimated product margin does not account for all operating expenses or financial adjustments.

## 18. Execution and Expected Outputs

### Python

Requires Python 3.10 or later.

Run the script using:

`python product_analytics.py`

It prints product, funnel, retention, segmentation, channel, and data-quality reports and writes JSON and CSV files.

### JavaScript

Requires Node.js 18 or later.

Run:

`node product_analytics.js`

The program performs asynchronous batch ingestion, evaluates analytics, and writes JSON and CSV reports.

### C++17

Compile using:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic product_analytics.cpp -o product_analytics`

Run:

`./product_analytics`

On Windows, execute `product_analytics.exe`.

### Java 17

Compile:

`javac ProductAnalytics.java`

Run:

`java ProductAnalytics`

### PostgreSQL

Execute the SQL script in a dedicated PostgreSQL database using a PostgreSQL client.

The script creates the schema, tables, constraints, indexes, trigger, sample records, analytical views, stored procedure, and reporting queries.

The script is designed for a fresh development environment. Existing objects in the same schema may require migration planning before reuse.

## 19. Learning Outcomes

The project demonstrates the relationship between business questions, event data, analytical definitions, and executable database operations.

Its central technical concepts are:

- Relational data modeling.
- Event-driven analytics.
- Product-level aggregation.
- Conditional aggregation.
- Conversion funnel analysis.
- Ordered session analysis.
- Cohort-based retention.
- RFM customer segmentation.
- Acquisition channel measurement.
- Window functions.
- Common Table Expressions.
- Database constraints and triggers.
- Transaction handling.
- Index design.
- Data validation.
- Cross-language analytical implementation.

The central analytical workflow is:

Data Collection
    |
    v
Data Validation
    |
    v
Relational Storage
    |
    v
Event Aggregation
    |
    v
Product Analysis
    |
    +----> Funnel Analysis
    |
    +----> Retention Analysis
    |
    +----> Customer Segmentation
    |
    +----> Channel Analysis
    |
    v
Business Reporting
