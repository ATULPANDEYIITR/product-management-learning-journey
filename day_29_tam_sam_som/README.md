# TAM, SAM, SOM: Total Addressable Market, Serviceable Available Market, Serviceable Obtainable Market

## 1. Topic Introduction

TAM, SAM, and SOM are market-sizing concepts used to define the size of a commercial opportunity at progressively narrower levels.

The three concepts are:

- **TAM — Total Addressable Market:** the broadest defined opportunity if the relevant customers theoretically purchased the relevant product or service.
- **SAM — Serviceable Available Market:** the portion of TAM that fits the company's product, geography, customer segment, distribution model, regulatory environment, technology requirements, and other explicit service constraints.
- **SOM — Serviceable Obtainable Market:** the portion of SAM that can reasonably be targeted and served under a defined business model, planning period, commercial strategy, and operational capacity.

A market-sizing model is not simply a calculation of three increasingly smaller numbers. The quality of the result depends on the definitions, population boundaries, data sources, assumptions, units, time period, segmentation, pricing, and operational constraints behind those numbers.

A useful hierarchy is:

`TAM >= SAM >= SOM`

for both customer count and the associated revenue measure, provided that all three are defined consistently.

---

## 2. Fundamental Concepts

### 2.1 Market

A market is a defined group of potential buyers and the economic activity associated with a product, service, category, or problem.

A useful market definition specifies:

- Customer type
- Customer geography
- Industry or vertical
- Company size
- Product or service
- Use case
- Pricing basis
- Distribution channel
- Relevant time period
- Currency
- Eligibility requirements

A market should not be defined only as a vague phrase such as "the global software market."

A more precise definition could be:

`Businesses in selected industries, in specified countries, using compatible technology, purchasing an annual analytics subscription during a defined year.`

The precise boundary matters because changing the boundary changes the market size.

---

## 3. TAM

TAM represents the broadest market opportunity within the selected definition.

A simple customer-revenue representation is:

`TAM Revenue = TAM Customers × Annual Revenue per Customer`

For usage-based businesses, a more appropriate equation may be:

`TAM Revenue = Users × Transactions per User per Year × Revenue per Transaction`

For segmented markets:

`TAM Revenue = Sum of Revenue Across All Non-Overlapping Segments`

TAM is sometimes interpreted as a theoretical maximum. The useful interpretation is more precise: it represents the opportunity under a clearly defined market boundary before applying the constraints that define SAM and SOM.

TAM does not mean that a company can realistically capture all of the calculated revenue.

---

## 4. SAM

SAM narrows TAM according to explicit service constraints.

Typical constraints include:

- Geography
- Industry
- Company size
- Product capabilities
- Technology compatibility
- Regulatory eligibility
- Distribution availability
- Supported languages
- Supported currencies
- Customer requirements
- Sales-channel limitations

A simplified model is:

`SAM = TAM × Geography Eligibility × Segment Eligibility × Product Eligibility`

The percentages must be interpreted carefully.

If a geography filter retains 50% of the population and an industry filter retains 60%, multiplying them gives 30% only when the second percentage is correctly interpreted as a conditional share or the independence assumption is justified.

If both percentages describe overlapping raw populations, multiplication can produce an incorrect result.

---

## 5. SOM

SOM represents the obtainable portion of SAM under the defined business scenario.

A simple model might be:

`SOM = SAM × Obtainable Share`

A stronger operational model recognizes that demand is not the only constraint.

For example:

`SOM Customers = Minimum(Desired Customers, Sales Capacity, Implementation Capacity, Support Capacity)`

This is demonstrated directly in the Python, JavaScript, and C++ implementations.

SOM should therefore be tied to a defined period. A statement such as "our SOM is 5%" is incomplete unless the model explains:

- 5% of what?
- Within which geography?
- During which period?
- At what price?
- Through which channel?
- With what sales capacity?
- With what implementation capacity?
- With what support capacity?

---

## 6. TAM, SAM, and SOM Compared

| Dimension | TAM | SAM | SOM |
|---|---|---|---|
| Scope | Broad defined opportunity | Serviceable portion | Obtainable portion |
| Main question | How large is the defined opportunity? | Which part can the offering serve? | Which part can realistically be targeted and served? |
| Typical constraints | Market definition | Product, geography, segment, regulation | Capacity, competition, sales, implementation, strategy |
| Useful output | Broad opportunity | Addressable opportunity | Planning opportunity |
| Common risk | Overly broad definition | Incorrect filtering | Arbitrary capture assumptions |

These are descriptive distinctions rather than independent formulas that must always use one specific method.

---

## 7. Market-Sizing Methods

### 7.1 Top-Down

Top-down analysis starts with a broad market estimate and progressively applies filters.

Example:

`Broad Market = $5 billion`

`Target segment = 20%`

`Target geography = 40%`

`Product fit = 60%`

The resulting estimate is:

`$5 billion × 20% × 40% × 60% = $240 million`

The Python implementation performs this calculation through `top_down_market_size()`.

The JavaScript implementation provides the same model through `topDownMarketSize()`.

The C++ case study includes a top-down cross-check.

### Advantages

- Fast
- Easy to communicate
- Useful when authoritative market totals exist
- Useful as a cross-check

### Limitations

- Sensitive to the quality of the initial market estimate
- Can hide incompatible definitions
- Can introduce arbitrary percentages
- Can multiply overlapping constraints incorrectly
- Can mix different years or geographic definitions

---

## 8. Bottom-Up

Bottom-up analysis starts with identifiable customers, transactions, usage, or other concrete units.

A common SaaS formula is:

`Target Customers × Annual Price = Market Revenue`

If there are 25,000 target customers and annual revenue per customer is $2,400:

`25,000 × $2,400 = $60,000,000`

A penetration scenario can be modeled as:

`25,000 × 8% × $2,400 = $4,800,000`

The Python implementation uses `bottom_up_market_size()`.

The JavaScript implementation uses `bottomUpMarketSize()`.

The C++ implementation uses the same concept through `bottomUpMarketSize()` and then extends it through multiple customer segments.

### Advantages

- Easier to audit
- Inputs correspond to identifiable quantities
- Works well with customer databases
- Naturally supports segmentation
- Useful for operational planning

### Limitations

- Requires reliable customer counts
- Customer counts can become outdated
- Pricing assumptions may be uncertain
- A customer may not actually be willing or able to buy
- Duplicate customers can inflate the market

---

## 9. Segmented Bottom-Up Modeling

A heterogeneous market should often be divided into non-overlapping segments.

The implementations use:

- Small businesses
- Mid-market businesses
- Enterprise businesses

Each segment has:

- Customer count
- Annual price
- Adoption or penetration rate

The market is calculated as:

`Segment Market = Customers × Price × Adoption`

Then:

`Total TAM = Segment 1 + Segment 2 + Segment 3`

The important requirement is that segments should not overlap.

For example, if "companies with 100+ employees" and "technology companies" are treated as independent additive segments, the same company could appear in both groups.

A better segmentation strategy defines mutually exclusive categories or explicitly models intersections.

---

## 10. Usage-Based Markets

Not every business sells annual subscriptions.

A transaction-oriented market can use:

`Market Revenue = Users × Transactions per User × Revenue per Transaction`

The Python implementation provides `usage_based_market_size()`.

The JavaScript implementation provides the same calculation through `usageBasedMarketSize()`.

Potential applications include:

- Payments
- Marketplaces
- Advertising
- API consumption
- Transportation
- Logistics
- Cloud usage
- Transaction-processing services

The correct unit is important. Annual subscription revenue should not be mixed directly with monthly usage unless the time period is normalized.

---

## 11. Market Constraints

The implementations represent SAM constraints with a `MarketConstraint` structure or class.

Examples include:

- Supported geography
- Target industry
- Compatible technology
- Regulatory eligibility
- Product compatibility
- Distribution availability

A simplified constraint model is:

`Eligible Customers = Initial Customers × Constraint 1 × Constraint 2 × Constraint 3`

This is mathematically convenient but requires an important assumption: the constraint percentages must represent appropriate conditional probabilities or eligibility rates.

### Correlated Constraints

Suppose:

- 70% of businesses use a technology
- 60% operate in a specific industry

It is not automatically correct to calculate:

`70% × 60% = 42%`

The technology adoption rate may be much higher or lower within that industry.

A customer-level dataset can resolve this by applying both filters to individual records.

---

## 12. Pricing

Pricing is one of the largest drivers of a revenue-based market estimate.

Common pricing units include:

- Per customer
- Per employee
- Per user
- Per transaction
- Per API call
- Per month
- Per year
- Percentage of transaction value
- Usage volume

The pricing unit must match the market unit.

For example:

`10,000 customers × $100/month`

must be converted to an annual figure when comparing it with an annual market estimate:

`10,000 × $100 × 12 = $12,000,000/year`

---

## 13. Value-Theory Pricing

The Python implementation includes `value_theory_price()`.

The concept is:

`Economic Value Created × Value Capture Rate = Illustrative Price`

If a service creates $20,000 of annual economic value and the modeled value-capture rate is 15%:

`$20,000 × 15% = $3,000`

This is an illustrative pricing model, not proof that customers will pay the resulting amount.

Actual willingness to pay can depend on:

- Alternatives
- Budgets
- Procurement processes
- Switching costs
- Competitive pricing
- Perceived risk
- Product differentiation
- Contract terms

---

## 14. SOM and Operational Capacity

The implementations explicitly model operational capacity.

The C++ case study uses:

- Number of sales representatives
- New customers per representative per year
- Implementation capacity
- Support capacity

Sales capacity is:

`Sales Representatives × New Customers per Representative`

Effective operational capacity is:

`Minimum(Sales Capacity, Implementation Capacity, Support Capacity)`

This prevents a model from claiming an obtainable customer count that the company cannot operationally serve.

A business can have substantial theoretical demand but limited obtainable revenue because of:

- Limited sales staff
- Long enterprise sales cycles
- Implementation bottlenecks
- Customer support capacity
- Manufacturing capacity
- Capital constraints
- Distribution limitations
- Regulatory restrictions

---

## 15. Python Implementation

The Python script is organized as an executable educational workbook.

### Core structures

`MarketSize` represents:

- Annual revenue
- Customer count
- Revenue per customer

`Assumption` stores:

- Name
- Value
- Unit
- Source
- Confidence

`MarketModel` provides a general customer-and-pricing representation.

### Market calculations

The script implements:

- `calculate_market_hierarchy()`
- `top_down_market_size()`
- `bottom_up_market_size()`
- `usage_based_market_size()`
- `segmented_market_size()`
- `apply_constraints()`
- `capacity_constrained_som()`

### Advanced analysis

The script also demonstrates:

- Compound growth
- Market projections
- Sensitivity analysis
- Unit economics
- Value-theory pricing
- Monte Carlo simulation
- Percentile calculations
- Hierarchy validation

### Testing

The Python file contains a lightweight executable test suite using assertions.

The tests validate:

- Revenue per customer
- Bottom-up sizing
- Top-down sizing
- Segmentation
- TAM/SAM/SOM hierarchy
- Compound growth

No external Python package is required.

---

## 16. JavaScript Implementation

The JavaScript file complements the Python implementation by demonstrating how market-sizing logic can be modeled in an application-oriented language.

### Object-oriented modeling

The JavaScript implementation defines:

- `MarketSize`
- `CustomerSegment`
- `MarketConstraint`
- `CapacityModel`
- `UnitEconomics`

This demonstrates how market entities can be represented as objects with data and behavior.

For example, `MarketSize` exposes `revenuePerCustomer` as a computed property.

### Functional calculations

Functions such as:

- `topDownMarketSize()`
- `bottomUpMarketSize()`
- `segmentedMarketSize()`
- `applyConstraints()`
- `marketProjection()`
- `sensitivityAnalysis()`

separate calculations from reporting.

### Asynchronous processing

`calculateScenarioAsync()` returns a Promise.

`scenarioComparisonExample()` uses `Promise.all()` to process multiple market-growth scenarios.

This demonstrates how the same market-sizing calculations could be integrated into a web application, dashboard, API workflow, or event-driven service.

### Deterministic simulation

The JavaScript file implements a small seeded random-number generator.

The purpose is reproducibility. The same seed produces the same educational simulation sequence.

It is explicitly not a cryptographic random-number generator.

---

## 17. C++ Industry-Style Case Study

The C++ program models a hypothetical B2B SaaS analytics business.

### Business problem

The business needs to estimate:

1. The broad addressable opportunity
2. The portion that fits its service definition
3. The portion it can operationally target and serve

### Step 1: TAM

The TAM is built from three segments:

- Small business
- Mid-market
- Enterprise

Each segment has:

- Customer count
- Annual subscription price
- Adoption rate

The total is calculated through `segmentedMarketSize()`.

This is a bottom-up TAM.

### Step 2: SAM

The TAM is narrowed using:

- Target geography
- Target industries
- Compatible technology

The C++ program applies these through `applyConstraints()`.

The model assumes the eligibility percentages are conditional. A production model should validate that assumption.

### Step 3: SOM

The C++ program creates a capacity model containing:

- 15 sales representatives
- 80 new customers per representative per year
- 1,100 annual implementation capacity
- 1,500 annual support capacity

Sales capacity is:

`15 × 80 = 1,200 customers/year`

The effective operational capacity is the minimum of:

- 1,200 sales capacity
- 1,100 implementation capacity
- 1,500 support capacity

Therefore:

`Effective Capacity = 1,100 customers/year`

The SOM calculation limits desired customers by this capacity.

---

## 18. C++ Data Structures

The C++ implementation uses several structures.

### `MarketSize`

Stores:

- Revenue
- Customer count

It also calculates revenue per customer.

### `CustomerSegment`

Stores:

- Segment name
- Customers
- Annual price
- Adoption rate

Its `calculate()` method converts the segment assumptions into a `MarketSize`.

### `MarketConstraint`

Stores:

- Constraint name
- Eligibility percentage

### `CapacityModel`

Stores:

- Sales representatives
- Sales productivity
- Implementation capacity
- Support capacity

It calculates the effective customer capacity.

### `UnitEconomics`

Stores:

- Annual revenue per customer
- Gross margin
- CAC
- Churn

It derives:

- Gross profit
- Estimated customer lifetime
- LTV
- LTV/CAC

---

## 19. Growth Modeling

Market size can change over time.

The standard compound-growth equation is:

`Future Value = Initial Value × (1 + Growth Rate)^Years`

For example, with a $50 million starting market and 12% annual growth:

`Future Value = $50M × 1.12^Years`

The three implementations demonstrate this concept.

Growth assumptions should be tied to a defined period and should not be confused with company revenue growth.

A market may grow while a particular company grows more slowly, faster, or not at all.

---

## 20. Sensitivity Analysis

A market estimate is a function of its assumptions.

If:

`Market = Customers × Price × Adoption`

then uncertainty in any of these variables changes the result.

The implementations evaluate low, base, and high values for a selected parameter.

Example:

| Annual Price | Market Revenue |
|---:|---:|
| $1,000 | $2,000,000 |
| $2,000 | $4,000,000 |
| $3,500 | $7,000,000 |

This does not establish which value is correct. It shows how the output responds to alternative assumptions.

Sensitivity analysis is especially useful when:

- Customer counts are uncertain
- Pricing is not validated
- Adoption is unclear
- Market growth is uncertain
- Eligibility percentages are estimates

---

## 21. Scenario Analysis

A point estimate can hide uncertainty.

Common scenarios include:

- Conservative
- Base
- High-growth

The JavaScript implementation calculates three five-year scenarios with different growth rates.

Scenario analysis is useful because it separates:

`Assumption uncertainty`

from:

`Calculation certainty`

The formula may be mathematically correct while the input assumptions remain uncertain.

---

## 22. Monte Carlo Simulation

The implementations use Monte Carlo simulation to produce a distribution of possible market estimates.

Instead of assuming one exact value for:

- Customers
- Annual price
- Adoption

the simulation samples values from defined ranges.

The resulting distribution provides:

- Minimum
- P10
- Median
- P90
- Maximum
- Average

For example:

`P10` means approximately 10% of simulated outcomes are at or below that value under the selected simulation assumptions.

It does not mean there is a 10% probability that the real market will be exactly that value.

### Important limitation

The educational implementation uses uniform distributions.

Production analysis should use distributions justified by evidence. A normal, lognormal, triangular, beta, empirical, or other distribution may be more appropriate depending on the variable and available data.

---

## 23. Market Size Versus Company Revenue

TAM is not company revenue.

Suppose:

`TAM = $1 billion`

This does not mean:

`Company Revenue = $1 billion`

Company revenue depends on:

- Market share
- Product competitiveness
- Pricing
- Sales execution
- Customer acquisition
- Retention
- Capacity
- Distribution
- Competition
- Product-market fit
- Timing
- Regulation
- Capital
- Operational execution

SOM is intended to narrow the opportunity toward an obtainable planning estimate, but the assumptions behind SOM must still be justified.

---

## 24. Unit Economics

Market size describes the size of an opportunity.

Unit economics describe the economics of serving a customer.

The Python, JavaScript, and C++ implementations model:

`Annual Revenue per Customer`

`Gross Margin`

`Customer Acquisition Cost`

`Annual Churn`

A simplified annual gross-profit calculation is:

`Annual Gross Profit = Annual Revenue × Gross Margin`

An illustrative lifetime estimate under a constant annual churn assumption is:

`Lifetime = 1 / Annual Churn`

LTV can then be approximated as:

`LTV = Annual Gross Profit × Lifetime`

This is a simplified model and should not be treated as a universal financial formula.

---

## 25. Important Distinction: Market Size and Market Share

Market size is the size of the opportunity.

Market share is the portion captured by a particular company or competitor.

For example:

`Market = $100 million`

and:

`Company Share = 5%`

would correspond to:

`Company Revenue = $5 million`

only under a simplified revenue-share model with compatible definitions.

Market share calculations must use consistent:

- Geography
- Product definition
- Time period
- Revenue definition
- Customer population

---

## 26. Important Distinction: SAM Versus SOM

SAM and SOM are frequently confused.

SAM asks:

`Which part of the broader market can this offering serve?`

SOM asks:

`Which part can the business realistically obtain and serve under the selected scenario?`

A business may have:

- Large SAM
- Limited sales capacity
- Limited implementation capacity

In that situation, SOM can be substantially smaller than SAM.

The C++ case study demonstrates this directly.

---

## 27. Important Distinction: TAM and Demand

TAM does not automatically prove demand.

A company may calculate a large theoretical market because many customers technically fit the definition.

That does not prove that those customers:

- Have budget
- Have the problem
- Consider the problem important
- Will switch providers
- Will pay the proposed price
- Can purchase through the proposed channel
- Meet procurement requirements

Market sizing should therefore be separated from demand validation.

---

## 28. Common Mistakes

### 28.1 Using an undefined market

"The global market is $20 billion" is incomplete without knowing what market is being measured.

### 28.2 Mixing time periods

Do not combine:

- 2025 customer counts
- 2026 pricing
- 2024 market revenue

without explicitly adjusting or explaining the difference.

### 28.3 Mixing currencies

A market expressed in USD cannot be directly added to a market expressed in INR without conversion.

### 28.4 Mixing monthly and annual values

`$100/month` and `$1,200/year` are economically equivalent only if the pricing terms actually operate that way.

### 28.5 Double counting customers

Overlapping segments can inflate TAM.

### 28.6 Arbitrary percentages

A model that repeatedly uses:

`TAM × 50% × 50% × 50%`

without evidence can create a precise-looking but weak estimate.

### 28.7 Treating SOM as a random percentage

"Assume we capture 10%" is not a strong SOM model without explaining why 10% is operationally achievable.

### 28.8 Ignoring capacity

Demand does not automatically equal obtainable revenue.

### 28.9 Confusing TAM with revenue forecast

A large market is not a forecast of the company's actual revenue.

### 28.10 Ignoring customer heterogeneity

Enterprise customers may generate substantially more revenue than small customers.

### 28.11 Ignoring pricing structure

Per-seat, per-transaction, subscription, and usage pricing produce different market-sizing equations.

### 28.12 Treating estimates as facts

An assumption should remain visibly distinguishable from observed market data.

---

## 29. Edge Cases

The implementations explicitly handle several edge cases.

### Zero customers

A market with zero customers produces zero revenue.

Revenue per customer must not attempt division by zero.

### Zero revenue

A market can theoretically contain customers while having a zero modeled revenue value.

### Zero adoption

Zero adoption produces zero effective customers under the penetration model.

### 100% adoption

100% represents the full customer population under the selected definition.

### Invalid percentages

Values below 0% or above 100% are rejected.

### Negative prices

Negative market prices are rejected.

### Negative customer counts

Negative customer counts are rejected.

### Zero churn

The unit-economics model treats zero churn as an infinite simplified lifetime rather than performing division by zero.

### Negative growth

Growth below -100% is rejected because it would create an invalid standard compound-growth factor.

---

## 30. Validation

A robust model should validate both inputs and relationships.

The implementations validate:

- Non-negative revenue
- Non-negative customers
- Valid percentages
- Valid growth rates
- Valid sensitivity ranges
- Valid simulation ranges
- Valid capacity values

They also validate the TAM/SAM/SOM hierarchy.

Expected relationships include:

`SAM Customers <= TAM Customers`

`SOM Customers <= SAM Customers`

`SAM Revenue <= TAM Revenue`

`SOM Revenue <= SAM Revenue`

These checks do not prove that the model is correct. They identify structural inconsistencies.

---

## 31. Performance Considerations

Most TAM/SAM/SOM arithmetic is computationally inexpensive.

For a simple formula:

`Customers × Price`

the computational complexity is effectively `O(1)`.

For `n` market segments:

`O(n)`

For `n` constraints:

`O(n)`

For a Monte Carlo simulation with `n` samples:

- Generation is `O(n)`
- Sorting for percentile calculation is `O(n log n)`

The C++ implementation uses `vector` for simulation samples and sorts them before calculating percentiles.

The JavaScript implementation uses arrays and the built-in `sort()` method.

The Python implementation uses lists and sorting.

For very large simulations, memory usage becomes relevant because the sample distribution is retained.

---

## 32. Numerical Considerations

Market-sizing calculations can involve very large numbers.

Potential issues include:

- Floating-point representation
- Integer overflow
- Currency precision
- Rounding
- Currency conversion
- Unit conversion

The C++ implementation uses `double` for monetary calculations and `long long` for customer counts.

For financial production systems, fixed-point decimal arithmetic or an appropriate decimal-money implementation may be preferable to binary floating-point arithmetic.

Rounding should occur at clearly defined presentation or accounting boundaries rather than randomly throughout the calculation.

---

## 33. Security Considerations

Basic market-sizing calculations are not inherently security-sensitive, but production systems can contain commercially sensitive information.

Potential concerns include:

- Customer databases
- Pricing information
- Sales pipeline data
- Competitive intelligence
- Internal forecasts
- Proprietary market research

A production implementation should consider:

- Access control
- Authentication
- Authorization
- Encryption in transit
- Encryption at rest
- Audit logging
- Data minimization
- Input validation
- Secure API design
- Protection of confidential assumptions

The code in this educational implementation intentionally avoids external data sources and credentials.

---

## 34. Data Quality

A market-sizing model is only as useful as the definitions and evidence behind its inputs.

Each important assumption should ideally record:

- Value
- Unit
- Date
- Geography
- Population
- Source
- Method
- Confidence
- Transformation applied

The Python implementation includes an `Assumption` data class to illustrate this principle.

A source value should not be copied into a model without checking:

- What population it covers
- What geography it covers
- What year it represents
- Whether it measures revenue or transactions
- Whether it includes adjacent categories
- Whether it overlaps with other inputs

---

## 35. Production Modeling Considerations

A production market-sizing system can be organized into layers.

### Data layer

Contains:

- Customer counts
- Industry classifications
- Geography
- Company size
- Pricing
- Usage
- Regulatory eligibility

### Modeling layer

Contains:

- TAM calculation
- SAM filters
- SOM constraints
- Growth assumptions
- Scenario logic
- Sensitivity calculations

### Validation layer

Checks:

- Units
- Date consistency
- Duplicate customers
- Missing values
- Impossible percentages
- Hierarchy relationships

### Reporting layer

Presents:

- Market values
- Customer counts
- Scenario ranges
- Assumptions
- Sensitivity results
- Sources

Keeping these concerns separate makes the model easier to audit and maintain.

---

## 36. Practical Applications

TAM, SAM, and SOM models can be applied to:

- SaaS
- Fintech
- Banking products
- Healthcare services
- Logistics
- Manufacturing
- Retail
- Marketplaces
- Advertising
- Cloud services
- Enterprise software
- Consumer applications
- Professional services
- Subscription businesses

The mathematical model should change according to the business's actual economic unit.

---

## 37. Choosing the Appropriate Model

| Situation | Useful Approach |
|---|---|
| Reliable broad industry estimate exists | Top-down cross-check |
| Identifiable customer population exists | Bottom-up |
| Multiple customer types exist | Segmented bottom-up |
| Revenue depends on transactions | Usage-based |
| Product has strict eligibility rules | Constraint-based SAM |
| Operations impose limits | Capacity-constrained SOM |
| Inputs are uncertain | Sensitivity analysis |
| Several uncertain variables interact | Monte Carlo simulation |
| Pricing depends on customer value | Value-theory model |

Using more than one approach can reveal differences that deserve investigation.

---

## 38. Recommended Modeling Sequence

A technically disciplined market-sizing workflow is:

1. Define the market.
2. Define the customer population.
3. Define the geographic boundary.
4. Define the product or service.
5. Define the time period.
6. Define the economic unit.
7. Build a bottom-up model where possible.
8. Build a top-down cross-check where useful.
9. Define SAM constraints.
10. Check whether constraints overlap.
11. Define SOM assumptions.
12. Add operational capacity.
13. Validate pricing.
14. Run sensitivity analysis.
15. Run scenarios when uncertainty is material.
16. Validate units and dates.
17. Document assumptions and sources.
18. Separate market opportunity from revenue forecasting.

---

## 39. Cross-Language Comparison

### Python

Python is effective for market-sizing analysis because it provides:

- Concise numerical code
- Clear data structures
- Fast prototyping
- Easy testing
- Straightforward simulation

The Python implementation emphasizes analytical modeling and educational clarity.

### JavaScript

JavaScript is particularly useful when market-sizing calculations become part of:

- Web dashboards
- Browser applications
- Interactive planning tools
- Event-driven systems
- API-driven applications

The JavaScript implementation therefore includes classes, computed properties, asynchronous scenario processing, and deterministic simulation.

### C++

C++ is useful when market-sizing calculations form part of a larger performance-sensitive application or data-processing system.

The C++ implementation emphasizes:

- Strong type structure
- Explicit validation
- Standard-library data structures
- Exception handling
- Algorithmic complexity
- Compile-time and runtime correctness
- An industry-style case study

The underlying mathematical concepts are language-independent, while the implementation patterns differ according to each language's execution model and ecosystem.

---

## 40. Complete Case Study Flow

The C++ case study implements the following pipeline:

`Customer Segments`

↓

`Bottom-Up TAM`

↓

`Geographic / Industry / Technology Constraints`

↓

`SAM`

↓

`Strategic Obtainable Share`

↓

`Sales Capacity`

`Implementation Capacity`

`Support Capacity`

↓

`Capacity-Constrained SOM`

This structure demonstrates an important principle: each stage should have a clear reason for narrowing the preceding stage.

---

## 41. Interpretation of the Three Numbers

A market-sizing report should never present only:

`TAM = X`

`SAM = Y`

`SOM = Z`

without definitions.

A stronger presentation states:

- What customers are included
- What customers are excluded
- What geography is included
- What period is measured
- What product is measured
- What price is used
- What customer count is used
- What constraints define SAM
- What operational assumptions define SOM
- Which values are measured data
- Which values are assumptions
- Which values are derived calculations

This makes the model auditable.

---

## 42. Practical Interpretation

TAM is primarily a **market-boundary and opportunity concept**.

SAM is primarily a **serviceability and eligibility concept**.

SOM is primarily an **obtainability and operational planning concept**.

The three numbers become meaningful when their definitions and assumptions are transparent. A smaller, well-defined market can be more analytically useful than a very large market based on vague boundaries.

The implementations in this study deliberately expose the calculations rather than hiding assumptions inside a single final number.
