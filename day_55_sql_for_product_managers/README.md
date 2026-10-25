# SQL for Product Managers: Practical Analytics

## Purpose

This project uses a realistic product analytics dataset to explain how SQL answers product management questions. The examples connect product events, users, products, acquisition channels, and revenue.

The five implementations approach the same analytical problems from different perspectives:

- Python uses SQLite to execute real SQL queries and validate reporting results.
- JavaScript implements event-driven, in-memory analytics with JavaScript collections.
- C++17 builds an efficient reporting engine using typed domain objects and STL containers.
- Java 17 models analytics data with records, immutable collections, streams, and a service layer.
- PostgreSQL defines a relational schema, reusable reporting functions, constraints, indexes, and analytical queries.

## Business scenario

A software company offers three products:

| Product | Category | Business question |
|---|---|---|
| Analytics Pro | Analytics | How much revenue did it generate? |
| Team Workspace | Collaboration | How many customers purchased it? |
| Mobile Insights | Analytics | How does it compare with other products? |

The company records user signups and product events, including views, activations, purchases, and churn. Each purchase can record revenue. Acquisition channels identify how users discovered the company.

The example dataset contains six users and fourteen events. March 2026 purchase revenue is 297.00 monetary units. A further purchase in April is deliberately excluded from March reports.

The data is illustrative rather than a representation of a real company. Monetary values are shown without assuming a particular currency.

## Relational data model

The central relationships are:

    Products ────────┐
                     ├──── Events
    Users ───────────┘

Each event references one user and one product. Users have acquisition attributes, while products have category and launch-date attributes.

The `products` table describes the catalog. The `users` table describes registered users. The `events` table stores observations of product activity.

Primary keys identify individual records. Foreign keys prevent events from referring to nonexistent users or products. Check constraints restrict event types and prevent negative revenue. The sample implementations also validate identifiers and references before running reports.

This separation allows product metadata to remain consistent without repeating product names, categories, countries, or acquisition channels in every event record.

## The SELECT statement

`SELECT` determines which columns and calculated values appear in a result.

A product manager might retrieve product names and categories when preparing a product portfolio report. An event-level query can select dates, user identifiers, event types, and revenue for a specified reporting period.

Selecting only necessary columns makes queries easier to interpret and can reduce data transfer when working with large tables.

`SELECT` can also calculate values using expressions. For example, dividing paying users by registered users produces a conversion percentage when the denominator is nonzero.

The examples use explicit column names rather than `SELECT *` for analytical reports. This makes the expected result structure clear and avoids silently adding unrelated columns when a table changes.

## Filtering with WHERE

`WHERE` removes records that do not meet a condition.

Common product analytics filters include:

- `event_type = 'purchase'` to isolate purchase activity.
- `category = 'Analytics'` to examine one product category.
- A date range to restrict results to a reporting period.
- Multiple conditions combined with `AND` or `OR`.
- Comparisons such as `revenue > 50` to find higher-value events.

For March reporting, the PostgreSQL implementation uses a half-open interval where appropriate: the event date is on or after March 1 and before April 1. This pattern is especially useful when the source column contains timestamps rather than dates.

A filter applies to individual rows before grouping. A report that filters to purchases before calculating revenue therefore aggregates purchase records rather than views, activations, or churn events.

SQL uses three-valued logic when `NULL` is present. A comparison with `NULL` does not evaluate to true. Use `IS NULL` or `IS NOT NULL` when checking missing values.

## GROUP BY and aggregation

`GROUP BY` creates groups of records that share selected values. Aggregate functions then calculate one result per group.

| Function | Purpose | Product analytics example |
|---|---|---|
| `COUNT(*)` | Counts rows | Number of purchase events |
| `COUNT(DISTINCT user_id)` | Counts unique users | Number of paying customers |
| `SUM(revenue)` | Adds numeric values | Revenue by product |
| `AVG(revenue)` | Calculates an arithmetic mean | Average revenue per purchase event |
| `MIN()` | Finds the smallest value | Earliest event date |
| `MAX()` | Finds the largest value | Latest event date |

The distinction between event counts and unique-user counts matters. A user who purchases three times contributes three purchase events but only one paying user.

Revenue aggregation must also use the intended grain. Summing revenue after joining a purchase to several matching detail records can duplicate revenue. The PostgreSQL CTE example aggregates purchases by product and month before joining the product names.

### WHERE versus HAVING

`WHERE` filters rows before aggregation. `HAVING` filters groups after aggregation.

For example, `WHERE event_type = 'purchase'` selects purchase records. Grouping those records by category and applying `HAVING SUM(revenue) >= 50` retains only categories whose aggregated revenue reaches the threshold.

A useful rule is to filter individual records with `WHERE` and calculated group results with `HAVING`.

## JOIN operations

Joins combine related information from multiple tables.

### INNER JOIN

An `INNER JOIN` returns rows with matching records on both sides. Joining events to users and products adds acquisition channel, country, product name, and category to event data.

Use this when the report requires valid matching records from every joined table.

### LEFT JOIN

A `LEFT JOIN` preserves every record from the left table, even if there is no matching record on the right.

The revenue-by-product report begins with the product catalog and left-joins purchases. Products with no purchases remain visible, with zero revenue provided by `COALESCE`.

The purchase event conditions are placed in the `ON` clause. Moving them to a `WHERE` clause can remove products without matching purchases, effectively changing the intended result.

### Avoiding join errors

Before aggregating joined data, establish the relationship between the tables and the expected number of matching rows.

For example, joining each purchase to a one-to-many product-feature table can repeat the purchase amount for every matching feature. Aggregate at the required grain first or use a query structure that preserves the intended counting unit.

Use `COUNT(DISTINCT user_id)` when the question asks for unique users, but do not use it automatically to conceal a join problem. Understand why records multiply before selecting an aggregate.

## Product analytics questions

### Revenue by product

The revenue reports filter purchase events by date, group them by product, and calculate purchase counts, total revenue, and average purchase-event revenue.

The March sample produces:

| Product | Purchase events | Revenue |
|---|---:|---:|
| Analytics Pro | 2 | 248.00 |
| Mobile Insights | 1 | 49.00 |
| Team Workspace | 0 | 0.00 |

This report supports comparisons between products and highlights products with no recorded purchases during the reporting period.

Revenue is not the same as profit, recurring revenue, or customer lifetime value. These measures require their own definitions and data.

### Acquisition performance

The acquisition report groups users by channel and calculates registered users, paying users, revenue, and payer conversion.

Payer conversion is defined as:

`Distinct paying users / distinct registered users × 100`

A channel can produce high revenue because it attracts many customers, because customers spend more, or because a small number of customers make large purchases. Conversion and revenue should therefore be interpreted together.

The Python and PostgreSQL reports use a date filter for purchase events while retaining the relevant registered users. The JavaScript and Java examples aggregate purchases across their full sample event histories, so their channel revenue can include purchases outside March.

This difference is deliberate: report definitions must specify whether the time window applies to signups, purchase activity, or both.

### Activation analysis

The event funnel counts distinct users who viewed, activated, or purchased during March. It also calculates activation as a percentage of viewers.

These are distinct-user counts, not proof that a user followed the sequence view, then activation, then purchase. The same user can generate events on different dates or in different orders.

A sequential conversion funnel needs a defined attribution rule, such as whether activation must occur after a view within a specified number of days. The current sample implementations do not claim to measure that ordered behavior.

### Daily revenue

Daily revenue groups purchase events by date and sums their revenue.

This supports identifying high-revenue days and monitoring changes over time. A daily report should use a consistent timezone when source data contains timestamps and should distinguish the transaction date from the date revenue is recognized by accounting systems.

## Python implementation

The Python script creates an in-memory SQLite database, defines tables and indexes, loads sample data, and executes parameterized SQL queries.

The `ProductAnalytics` class provides a reusable reporting interface. Its methods implement revenue by product, acquisition performance, a distinct-user funnel, daily revenue, and a query for products without events.

The `QueryResult` dataclass stores column names and returned rows. Its display method formats tabular output without external packages.

Date validation prevents reversed or invalid reporting periods. SQL parameters are passed separately from query text, which avoids building queries by concatenating user-provided values.

Assertions verify March revenue and the number of acquisition channels. The connection is closed in a `finally` block, including when a query fails.

SQLite is used to keep the example self-contained. Its SQL behavior is similar to PostgreSQL for the queries shown, but SQLite and PostgreSQL differ in data types, functions, date handling, concurrency, and query planning.

## JavaScript implementation

The JavaScript file treats products, users, and events as arrays of objects.

`Map` supports grouping records by a key. `Set` provides unique-user counts without counting a user's repeated purchases as separate customers. Array filtering implements row-level conditions, while reductions calculate totals and averages.

The revenue report models `LEFT JOIN` behavior by starting with every product and attaching matching purchases when available. The acquisition report groups users by channel and associates purchase records with those users.

Input validation checks unique identifiers, references, event types, dates, and nonnegative revenue. The asynchronous `main` function uses promises to coordinate report calculations and validates the expected March revenue.

This is an in-memory analytical model, not a SQL engine. It does not implement general SQL parsing, relational query optimization, transactions, or database isolation. Its time and memory costs depend on the number of records and on how many intermediate arrays and maps are constructed.

## C++17 implementation

The C++ program models products, users, and events with structs and represents event types with an enum.

Revenue is stored as integer cents rather than binary floating-point values. This avoids common rounding errors in currency calculations. The report converts cents to a decimal representation only when printing results.

An `unordered_map` provides identifier-to-index lookups, while sets support unique-user counts in the acquisition report. The revenue report initializes an entry for every product before processing purchases, preserving zero-revenue products.

Validation checks duplicate identifiers, invalid references, negative revenue, and inconsistent event revenue. The report sorts products by revenue and then product name to produce deterministic output.

Building indexes takes linear time in the number of products and users. Processing events is linear in the number of events for each report, with additional sorting cost of approximately O(P log P) for P products.

The example's date validator checks date shape and basic month/day ranges. It does not implement the full Gregorian calendar. Production systems should use a dedicated date library or validate dates at ingestion.

## Java 17 implementation

The Java implementation uses records for immutable domain values and `List.copyOf` to prevent external mutation of stored collections.

`ProductAnalyticsService` separates validation and analytical operations from the executable entry point. Identifier indexes support efficient reference checks and user lookups. Streams group purchase events, aggregate revenue with `BigDecimal`, and sort report results.

`BigDecimal` is used for monetary calculations. This avoids relying on binary floating-point arithmetic for amounts that require decimal precision.

The service calculates product revenue and acquisition performance, while explicit validation rejects duplicate identifiers, unknown references, invalid date ranges, and inconsistent monetary data.

The code targets Java 17. Records and stream operations reduce the amount of repetitive domain code, but they do not replace the need to define metric semantics or control the size of in-memory datasets.

## PostgreSQL implementation

The SQL script creates a dedicated `product_analytics` schema containing products, users, and events.

Primary keys, foreign keys, unique constraints, and check constraints enforce basic data integrity. Indexes support common event-date filtering and joins. The indexes are illustrative; production index selection should be based on query plans, table sizes, and actual workload patterns.

The `event_details` view provides a reusable join between events, users, and products. The `validate_date_range` function rejects missing or reversed date boundaries. Reporting functions return structured tables for revenue by product and acquisition performance.

The queries use PostgreSQL-specific capabilities:

- `FILTER` limits the rows supplied to an aggregate.
- `COUNT(DISTINCT ...)` counts unique users.
- `COALESCE` substitutes a value for `NULL`.
- `NULLIF` prevents division by zero.
- Common table expressions organize intermediate aggregation.
- `DATE_TRUNC` groups events into calendar months.
- `RAISE EXCEPTION` and exception blocks support validation and error handling.

The setup transaction groups schema and sample-data operations. Database constraints protect stored data even when writes originate outside the example reporting functions.

The sample inserts use `ON CONFLICT` to avoid duplicate seeded identifiers on repeated execution. This makes the setup convenient for learning, but it is not a general-purpose migration strategy. Existing records are not automatically reconciled with changed sample values.

## Metric definitions and analytical limitations

SQL syntax cannot compensate for an ambiguous business definition. Before using a query in a product review, specify the following:

| Metric | Required decision |
|---|---|
| Active users | Which events qualify as activity? |
| Conversion rate | What defines the eligible population and conversion window? |
| Revenue | Which transactions and recognition dates count? |
| Retention | What counts as returning, and over which interval? |
| Average purchase | Average per transaction or per customer? |
| Acquisition performance | Which date controls cohort membership? |

The sample data includes event records but does not provide session identifiers, refunds, subscription schedules, customer-level costs, or a complete cohort definition. It therefore cannot independently calculate reliable retention, gross margin, recurring revenue, or lifetime value.

The acquisition reports also demonstrate why counting distinct users and summing purchase revenue answer different questions. A single user can make multiple purchases, and one large transaction can dominate a channel's total revenue.

## Execution

### Python

Save the first source file as `product_analytics.py` and run it with Python 3. The script uses only the standard library.

### JavaScript

Save the second source file as `product-analytics.js` and execute it with a modern Node.js runtime.

### C++17

Save the third source file as `product_analytics.cpp`. Compile it with a C++17-compatible compiler, for example with the `-std=c++17` language option, and execute the resulting program.

### Java 17

Save the fourth source file as `ProductAnalyticsApp.java`. Compile and run it using Java 17 or later.

### PostgreSQL

Save the fifth source file as `product_analytics.sql` and execute it against a PostgreSQL database where the executing role has permission to create a schema, tables, functions, indexes, and views.

The database script uses the `product_analytics` schema and creates reusable reporting functions. Its sample reporting queries run after the setup transaction commits.

## Security and operational considerations

- Use parameterized SQL for values supplied by users or application code.
- Restrict database roles to the tables and operations they need.
- Do not expose personal or sensitive user-level data in product reports unless there is a legitimate requirement.
- Validate event data before aggregation so invalid identifiers and monetary values do not distort metrics.
- Define timezone, date-window, currency, and counting rules consistently across dashboards.
- Examine execution plans before adding indexes to large production tables.
- Avoid interpreting correlation between acquisition channel and revenue as proof that a channel caused the revenue.
- Test empty date ranges, products without events, users with repeated purchases, missing relationships, and zero denominators.

These implementations show how SQL concepts translate into practical product analytics while keeping data retrieval, metric definitions, aggregation, and business interpretation distinct.
