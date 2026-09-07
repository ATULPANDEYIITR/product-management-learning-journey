# Types of Products: B2B, B2C, B2B2C, SaaS, Marketplaces, Platforms, APIs, Consumer Apps, Enterprise Products, Product Discovery, and Company Information Ecosystems

## Introduction

Products can be classified in several ways, and no single classification system is sufficient for every product.

A product may be classified according to:

- Who pays for it
- Who uses it
- Who receives the primary value
- How it is distributed
- How it generates revenue
- Whether multiple groups interact through it
- Whether external developers or businesses can build on it
- Whether it is designed for individual consumers or complex organizations

This distinction is important because modern digital products frequently belong to several categories at the same time.

For example, a company may operate:

- A B2B SaaS product for organizations
- A consumer mobile application
- A marketplace connecting buyers and sellers
- A platform supporting third-party participants
- An API product for developers
- Enterprise capabilities for large customers

The Python script accompanying this document models these concepts through classes, functions, simulations, validation, access control, pricing logic, marketplace economics, retention analysis, API behavior, and product classification.

---

# Fundamental Product Concepts

A product is a solution that creates value for one or more groups of users or customers.

Products can be physical, digital, service-based, infrastructure-oriented, or multi-sided.

A product may involve several different participants.

For example, a B2B software product may involve:

- An economic buyer who controls the budget
- A decision maker who evaluates the product
- An administrator who manages the account
- End users who interact with the product daily

These groups can have different needs and incentives.

A technically successful product can fail commercially if it does not satisfy the economic buyer. A commercially attractive product can fail operationally if end users cannot use it effectively.

The script represents products using a base `Product` data class. This base class stores common product characteristics such as:

- Product name
- Description
- Customer types
- Revenue models
- Distribution models
- Target users
- Monthly price

The script uses Python enumerations to define categories consistently.

The major enumerations are:

- `CustomerType`
- `RevenueModel`
- `DistributionModel`

Using enumerations prevents arbitrary strings from being used inconsistently throughout the program.

---

# B2B Products

## Definition

B2B means Business-to-Business.

A B2B product is sold primarily to an organization rather than directly to an individual consumer.

Examples of B2B product categories include:

- Customer relationship management software
- Project management software
- Accounting systems
- Human resources software
- Cybersecurity products
- Cloud infrastructure
- Data analytics software
- Enterprise communication systems

## Important Characteristics

B2B purchasing is frequently more complex than consumer purchasing.

A business purchase may involve:

- Budget approval
- Product evaluation
- Technical evaluation
- Security review
- Legal review
- Procurement
- Contract negotiation
- Implementation planning

This can create a longer sales cycle.

The script models B2B products with the `B2BProduct` class.

Additional properties include:

- Sales cycle duration
- Contract value
- Whether multiple stakeholders are involved

The `estimate_sales_complexity()` method demonstrates how sales complexity can be estimated using simple rules.

A real B2B sales model would be more complex and could consider:

- Customer size
- Number of stakeholders
- Security requirements
- Procurement procedures
- Integration requirements
- Regulatory requirements
- Contract duration
- Customization requirements

## B2B Trade-Offs

Advantages may include:

- Higher contract values
- Predictable recurring revenue
- Long-term customer relationships

Challenges may include:

- Long sales cycles
- Complex implementation
- High customer expectations
- Integration requirements
- Customer concentration risk

---

# B2C Products

## Definition

B2C means Business-to-Consumer.

A B2C product is sold directly to individual consumers.

Examples include:

- Mobile applications
- Streaming services
- E-commerce applications
- Food delivery applications
- Fitness applications
- Consumer banking applications
- Social applications

## Important Characteristics

B2C products often emphasize:

- Ease of use
- Fast onboarding
- User experience
- Brand recognition
- Engagement
- Retention
- Scalability

Consumer purchasing decisions are often faster than enterprise purchasing decisions.

The price per customer may be lower than in B2B products, but the total number of users may be much larger.

The script models B2C products through the `B2CProduct` class.

It includes example calculations for:

- Monthly active users
- Monthly revenue
- Customer acquisition costs

## Important Distinction

B2C describes the commercial relationship between the business and the customer.

A consumer application describes the nature of the primary user.

These concepts frequently overlap but are not identical in purpose.

---

# B2B versus B2C

The main differences between B2B and B2C often include the following.

| Area | B2B | B2C |
|---|---|---|
| Primary customer | Organization | Individual |
| Purchasing process | Often multi-stakeholder | Often individual |
| Sales cycle | Frequently longer | Frequently shorter |
| Contract value | Often higher | Often lower per customer |
| Distribution | Sales teams, partners, procurement | Websites, applications, app stores |
| Product requirements | Administration, integrations, controls | Convenience, usability, engagement |

These are general patterns rather than absolute rules.

A self-service B2B SaaS product can have a very short purchasing cycle.

A consumer product involving financial or legal commitments can have a more complex decision process.

---

# B2B2C Products

## Definition

B2B2C means Business-to-Business-to-Consumer.

A B2B2C company creates value for consumers while reaching them through another business.

The simplified structure is:

Product Company → Partner Business → Consumer

Examples may involve:

- Financial technology infrastructure used by banks
- Technology embedded inside another company's consumer offering
- Commerce infrastructure used by merchants
- Educational technology distributed through institutions

## Product Design Challenge

B2B2C products must often satisfy two different groups:

1. The partner business
2. The final consumer

The partner may require:

- Integration
- Security
- Reporting
- Commercial value
- Administrative controls

The consumer may require:

- Simplicity
- Speed
- Trust
- Reliability

The script models this structure using `B2B2CProduct`.

It calculates estimated consumer reach based on:

- Number of partners
- Estimated consumers reached through each partner

The calculation is simplified but demonstrates how B2B2C distribution can provide access to a larger consumer base through business relationships.

---

# Software as a Service

## Definition

SaaS means Software as a Service.

A SaaS product delivers software as an ongoing service.

Common characteristics include:

- Recurring access
- Centralized updates
- Online delivery
- Account management
- Usage measurement
- Recurring billing

SaaS is not restricted to B2B.

It can include:

- B2B SaaS
- B2C SaaS
- B2B2C SaaS

## SaaS Metrics

The script demonstrates several SaaS metrics.

### Monthly Recurring Revenue

Monthly recurring revenue represents predictable recurring subscription revenue.

A simplified calculation is:

    MRR = Number of Customers × Monthly Price

### Annual Recurring Revenue

A simplified annual calculation is:

    ARR = MRR × 12

### Churn

Churn measures the loss of customers or revenue over time.

The script represents churn as a decimal.

For example:

    0.05 = 5% monthly churn

The `simulate_customer_retention()` method demonstrates how customer counts decline when churn occurs and no new customers are added.

This illustrates an important SaaS principle: customer acquisition alone does not guarantee sustainable growth.

A company may acquire many customers while still experiencing weak long-term growth if churn is high.

---

# Marketplaces

## Definition

A marketplace connects two or more groups and facilitates transactions between them.

A common structure is:

Buyers ↔ Marketplace ↔ Sellers

Marketplaces can connect:

- Buyers and sellers
- Clients and freelancers
- Riders and drivers
- Guests and hosts

## Marketplace Economics

The script calculates:

- Gross Merchandise Value
- Marketplace revenue
- Commission revenue

### Gross Merchandise Value

GMV represents the total value of transactions occurring through the marketplace.

A simplified formula is:

    GMV = Buyers × Transactions per Buyer × Average Transaction Value

### Marketplace Revenue

If the marketplace earns a percentage of transaction value:

    Revenue = GMV × Commission Rate

## Liquidity

A marketplace requires sufficient activity on both sides.

A marketplace with many buyers but few sellers may provide poor selection.

A marketplace with many sellers but few buyers may provide insufficient demand.

This challenge is often described as the chicken-and-egg problem.

The script includes a simplified participant balance function.

A real marketplace would require much more detailed analysis, including:

- Geographic coverage
- Category availability
- Match success
- Transaction frequency
- Response time
- Supply quality
- Pricing
- Repeat behavior

---

# Network Effects

A network effect occurs when a product becomes more valuable as participation increases.

## Direct Network Effects

More users directly increase the value available to other users.

Communication networks are a common example.

## Cross-Side Network Effects

More participants on one side increase value for participants on another side.

For example:

- More sellers can attract more buyers.
- More buyers can attract more sellers.

The script calculates possible pairwise relationships using:

    n × (n - 1) / 2

This does not directly measure economic value.

It demonstrates that the number of possible relationships can grow much faster than the number of participants.

Network effects are not automatically positive.

Negative network effects can occur through:

- Spam
- Congestion
- Excessive competition
- Reduced quality
- Long wait times

---

# Platforms

## Definition

A platform provides a foundation that allows other participants to build, interact, distribute, integrate, or create value.

Platforms may support:

- Developers
- Businesses
- Consumers
- Content creators
- Partners
- Third-party service providers

## Marketplace versus Platform

A marketplace primarily facilitates interaction or transactions between multiple sides.

A platform provides capabilities that allow others to build or extend functionality.

A product can be both.

For example, a commerce ecosystem may:

- Connect buyers and sellers
- Allow developers to build integrations
- Provide APIs
- Support third-party applications

The script models a platform using the `Platform` class.

It includes ecosystem indicators such as:

- Active developers
- Third-party integrations

The ecosystem health score is illustrative and not an industry-standard metric.

---

# APIs as Products

## Definition

API means Application Programming Interface.

An API allows software systems to interact through defined interfaces.

An API can exist internally within a company or be offered externally as a product.

A commercial API requires more than functional endpoints.

Important API product requirements include:

- Authentication
- Authorization
- Documentation
- Versioning
- Reliability
- Rate limiting
- Structured errors
- Monitoring
- Security
- Pricing
- Lifecycle management

## API Authentication

The script demonstrates a simplified API key authentication mechanism.

A request must provide a valid key.

Invalid keys raise an `AuthenticationError`.

Real systems commonly use stronger approaches depending on the security model, such as:

- OAuth
- Signed tokens
- Mutual authentication
- Short-lived credentials

The correct method depends on the product's security requirements.

## Rate Limiting

Rate limiting prevents excessive consumption and abuse.

The script tracks request counts for each API key.

When a key exceeds its allowed request limit, the system raises `RateLimitError`.

Production rate limiting systems must consider:

- Distributed infrastructure
- Time windows
- Burst traffic
- Customer plans
- Abuse detection

---

# API Versioning

APIs are often used by external systems.

A breaking change can disrupt customer software.

Breaking changes may include:

- Removing fields
- Renaming fields
- Changing data types
- Changing endpoint behavior
- Changing authentication requirements

The script demonstrates a versioned API supporting:

- `v1`
- `v2`

Unsupported versions raise a validation error.

Versioning introduces trade-offs.

Maintaining older versions improves compatibility but increases:

- Maintenance cost
- Security responsibilities
- Testing requirements
- Operational complexity

Removing old versions reduces maintenance but can disrupt customers.

---

# Consumer Applications

Consumer applications are primarily designed for individual users.

Important considerations often include:

- Onboarding
- Engagement
- Accessibility
- Performance
- Personalization
- Privacy
- Retention

The script extends the B2C model with `ConsumerApp`.

It calculates:

- DAU/MAU engagement ratio
- Notification opt-in rate

## DAU/MAU

DAU means Daily Active Users.

MAU means Monthly Active Users.

A simplified engagement ratio is:

    DAU / MAU

The script handles the zero-user edge case to avoid division by zero.

This metric should not be interpreted without context.

Different product categories naturally have different usage frequencies.

A product used monthly may be successful even if its daily engagement is low.

---

# Enterprise Products

Enterprise products are designed for organizations with complex operational requirements.

Common enterprise requirements include:

- Role-based access control
- Single sign-on
- Audit logs
- Data governance
- Compliance controls
- Administrative capabilities
- High availability
- Integrations
- Service-level agreements

## Role-Based Access Control

The script demonstrates a simplified RBAC model.

Users have roles such as:

- Administrator
- Manager
- User
- Auditor

Each role receives a defined set of permissions.

The access control system checks whether a user is authorized to perform an action.

This illustrates an important security distinction:

Authentication answers:

    Who are you?

Authorization answers:

    What are you allowed to do?

Enterprise products must usually manage these concerns carefully because organizational users have different responsibilities.

---

# Multi-Tenancy

A tenant represents an organization or customer within a shared system.

Multi-tenant software allows multiple organizations to use the same underlying product infrastructure while maintaining separation between their data.

Common tenant isolation models include:

- Shared database with tenant identifiers
- Separate schemas
- Separate databases
- Separate infrastructure

The script demonstrates a simplified tenant-aware storage system.

Every data retrieval operation filters records using the tenant identifier.

This is a critical security principle.

A missing tenant filter can expose one organization's data to another organization.

Production systems require stronger protection than the simplified example.

Tenant isolation may also depend on:

- Database security
- Authorization rules
- Query design
- Encryption
- Infrastructure configuration
- Monitoring

---

# Product Classification

Product categories frequently overlap.

A product may simultaneously be:

- B2B
- SaaS
- Enterprise
- API-based

Another product may be:

- B2C
- Consumer-facing
- Marketplace-based

The script includes `ProductClassifier`, a rule-based classifier that demonstrates this overlap.

The classifier examines:

- Customer types
- Distribution methods
- Revenue models
- Developer targeting

The output is a set of categories rather than a single category.

This is important because forcing every product into exactly one category can produce misleading analysis.

---

# Product Business Models

A business model explains how a product captures economic value.

The script demonstrates several common models.

## Subscription

Customers pay repeatedly for continued access.

Common in SaaS and digital services.

## Usage-Based Pricing

Customers pay according to consumption.

Common for infrastructure and API products.

Examples of usage units may include:

- API calls
- Storage
- Computing time
- Transactions

## Transaction Fees

A product charges a fee when activity occurs.

## Commission

The product receives a percentage of transaction value.

Common in marketplaces.

## Advertising

Advertisers pay to reach an audience.

## Freemium

Basic functionality is free while advanced features require payment.

## Licensing

Customers pay for the right to use technology or software.

The script provides functions for calculating revenue using several of these models.

---

# Unit Economics

Unit economics measures the financial characteristics of a single unit.

The unit may be:

- One customer
- One user
- One transaction
- One account

The script demonstrates three important concepts.

## Customer Acquisition Cost

CAC estimates the cost of acquiring one customer.

A simplified calculation is:

    CAC = (Marketing Cost + Sales Cost) / New Customers

## Average Revenue Per User

ARPU is:

    Revenue / Active Users

## Simplified Lifetime Value

A simplified model is:

    LTV = Monthly ARPU / Monthly Churn Rate

This formula has important limitations.

It assumes relatively stable:

- Revenue
- Customer behavior
- Churn

Real LTV calculations may include:

- Gross margin
- Cohort behavior
- Expansion revenue
- Variable churn
- Discount rates

The script validates inputs to prevent invalid calculations.

---

# Product Metrics by Product Type

Different products require different metrics.

## B2B

Important metrics may include:

- Contract value
- Sales cycle duration
- Retention
- Expansion revenue
- Implementation success

## B2C

Important metrics may include:

- Active users
- Retention
- Conversion
- Customer acquisition cost
- Engagement

## SaaS

Important metrics may include:

- MRR
- ARR
- Churn
- Retention
- Customer lifetime value

## Marketplaces

Important metrics may include:

- GMV
- Take rate
- Liquidity
- Match rate
- Repeat transactions

## APIs

Important metrics may include:

- API requests
- Active developers
- Error rates
- Latency
- Retention

## Enterprise Products

Important metrics may include:

- Contract value
- Renewal rate
- Availability
- Implementation time
- Support performance

Metrics should be selected according to the product's business model and user behavior.

A metric that is useful for one product may be irrelevant for another.

---

# Retention Cohorts

A cohort is a group of users sharing a characteristic.

A common cohort is a group of users who joined during the same period.

Retention analysis measures how many users remain active over time.

The script simulates a cohort using:

- Initial users
- Monthly retention rate
- Number of months

The model calculates remaining users over time.

Retention analysis is important because total user growth can hide underlying churn.

For example:

- 10,000 new users join.
- 9,000 existing users leave.

The total user count may appear stable or growing while retention remains poor.

---

# Pricing Strategies

The script demonstrates tiered pricing through the `PricingTier` class.

A tier can include:

- Base monthly price
- Included usage
- Overage price

The total price changes when usage exceeds the included amount.

Common pricing strategies include:

- Per-user pricing
- Usage-based pricing
- Flat-rate pricing
- Tiered pricing
- Enterprise pricing
- Transaction-based pricing

Pricing involves trade-offs.

Simple pricing is easier to understand.

Flexible pricing may better align price with customer value.

Usage-based pricing can reduce entry barriers but may reduce cost predictability.

Enterprise pricing can reflect customer complexity but increases sales and negotiation effort.

---

# Product Discovery Ecosystems

Product discovery systems organize information about products.

Their functions may include:

- Search
- Categorization
- Product descriptions
- Launch information
- Tags
- Community interaction
- Product discovery

The script includes a simplified `ProductDiscoveryCatalog`.

Each product listing contains:

- Name
- Category
- Description
- Launch year
- Tags

The catalog supports:

- Keyword search
- Category search

This demonstrates how structured metadata improves product discovery.

:contentReference[oaicite:0]{index=0} is an example of a product discovery ecosystem focused on helping people discover and discuss products.

---

# Company Information Ecosystems

Company information systems organize structured information about organizations and business activity.

Possible data categories include:

- Company name
- Industry
- Founding year
- Products
- Funding activity
- Investors
- Employees
- Locations

The script demonstrates a simplified `Company` model that can contain multiple products.

The example shows that a company and a product are separate entities.

A single company can operate multiple products with different business models.

:contentReference[oaicite:1]{index=1} is an example of a business information ecosystem containing structured information about companies and related business activity.

---

# Product Decision Matrices

Product strategy often involves comparing alternatives across multiple criteria.

The script demonstrates a weighted decision matrix.

Example criteria include:

- Revenue potential
- Customer demand
- Time to market
- Operational feasibility

Each criterion receives a weight.

Each product strategy receives a score.

The weighted score is calculated by multiplying each score by its weight and adding the results.

The script then ranks alternatives.

This approach has limitations.

A numerical model can create an illusion of objectivity if:

- The criteria are poorly selected.
- The weights are arbitrary.
- The scores are biased.
- Important qualitative information is excluded.

Decision matrices are most useful when assumptions are visible and can be challenged.

---

# Product Risks

Each product type creates different risks.

## B2B Risks

- Long sales cycles
- Procurement complexity
- Customer concentration
- Integration requirements

## B2C Risks

- High acquisition costs
- Low switching costs
- Large-scale support
- Competitive markets

## Marketplace Risks

- Chicken-and-egg problems
- Fraud
- Trust failures
- Supply-demand imbalance

## API Risks

- Breaking changes
- Abuse
- Security vulnerabilities
- Availability dependencies

## Enterprise Risks

- Complex implementation
- Security requirements
- Long procurement
- Customization pressure

A major product management challenge is identifying which risks are fundamental to the business model and which can be reduced through design.

---

# Security Considerations

Security is relevant to nearly every digital product.

Important concepts include:

## Authentication

Authentication verifies identity.

Examples include:

- Passwords
- API keys
- Tokens
- Identity providers

## Authorization

Authorization determines which actions an authenticated user may perform.

## Input Validation

Input validation prevents invalid or malformed information from entering a system.

The script demonstrates validation for product names.

It checks:

- Data type
- Empty values
- Excessive length

## Rate Limiting

Rate limiting reduces excessive requests and potential abuse.

## Tenant Isolation

Multi-tenant products must prevent customers from accessing each other's data.

## Audit Logging

Enterprise products often need records of important actions.

Security should influence product architecture from the beginning.

Adding security only after a product is fully designed can create expensive architectural changes.

---

# Performance Considerations

Performance requirements depend on product type.

## Consumer Applications

Common requirements include:

- Fast interaction
- Mobile network resilience
- High traffic scalability

## Enterprise Products

Common requirements include:

- Predictable performance
- Reliability
- Large data processing

## Marketplaces

Common requirements include:

- Search performance
- Matching speed
- Availability updates

## APIs

Common requirements include:

- Low latency
- Efficient payloads
- Rate limiting
- Caching

The script compares:

- Linear search
- Indexed lookup

Linear search examines entries individually.

Indexed lookup performs preprocessing to create a dictionary.

This demonstrates a common engineering trade-off:

Memory and preprocessing can improve repeated lookup performance.

---

# Debugging and Validation

The script demonstrates several defensive programming techniques.

## Exceptions

Invalid states raise exceptions such as:

- `ValueError`
- `TypeError`
- Custom API errors

## Assertions

Assertions verify internal assumptions.

The script includes basic tests for marketplace take-rate calculations.

The tests verify:

- Correct normal calculations
- Zero values
- Negative values
- Invalid rates

Assertions are useful for internal development checks.

They should not be treated as the only validation mechanism for untrusted external input.

---

# Product Type Recommendation Logic

The script includes a rule-based function that suggests possible product models based on characteristics such as:

- Whether businesses are targeted
- Whether consumers are targeted
- Whether multiple groups interact
- Whether developers require access
- Whether recurring software value exists

This demonstrates that product classification can be derived from observable characteristics.

The function is intentionally simplified.

Real product classification requires additional qualitative analysis involving:

- Customer behavior
- Distribution
- Competitive positioning
- Market structure
- Revenue model
- Product architecture

---

# Product Architecture Considerations

Product requirements influence technical architecture.

## B2B SaaS

May require:

- Organization accounts
- Tenant isolation
- Role-based access
- Billing
- Integrations

## Consumer Applications

May require:

- Large-scale infrastructure
- Personalization
- Notification systems
- Mobile optimization

## Marketplaces

May require:

- Matching systems
- Search
- Payments
- Reputation systems
- Trust and safety systems

## Platforms

May require:

- Extensibility
- APIs
- Developer tooling
- Versioning

## Enterprise Products

May require:

- Identity integration
- Audit logs
- Data governance
- Compliance controls

A useful design principle is that architecture should follow actual product requirements.

Technical complexity should not be introduced merely because it is technically possible.

---

# Integrated Product Ecosystems

The final example demonstrates how multiple product categories can coexist.

The simulated ecosystem contains:

- A SaaS dashboard for merchants
- A consumer application
- A marketplace
- An API product

The ecosystem demonstrates that a company can operate different interfaces and business models for different participants.

For example:

Businesses may pay subscriptions.

Consumers may use a free application.

Transactions may generate commissions.

Developers may pay for API usage.

This structure creates multiple revenue models and user groups.

It also creates additional complexity involving:

- Identity
- Data management
- Permissions
- Integrations
- Billing
- Security
- Product strategy

---

# Common Product Classification Mistakes

## Assuming One Product Has One Category

Modern digital products frequently overlap categories.

A product can be:

- B2B
- SaaS
- Enterprise
- API-enabled

at the same time.

## Confusing Buyer and User

The person paying for a product may not be the person using it.

This is especially important in B2B and enterprise products.

## Assuming SaaS Means B2B

SaaS is a software delivery and commercial model.

It can serve businesses or consumers.

## Treating Every Multi-Sided Product as a Marketplace

A platform can support multiple participant groups without directly facilitating transactions.

## Treating APIs Only as Technical Components

An external API requires product-level concerns such as:

- Customer experience
- Documentation
- Versioning
- Reliability
- Pricing

---

# Product Analysis Workflow

A systematic product analysis can follow these questions:

1. Who receives value?
2. Who pays?
3. Are the buyer and user the same?
4. How is the product distributed?
5. How is revenue generated?
6. Are multiple groups interacting?
7. Can external participants build on the product?
8. Are enterprise requirements present?
9. Are APIs and integrations part of the product experience?
10. Which categories accurately describe the product?

This workflow helps avoid overly simplistic classification.

---

# Multi-Model Product Complexity

Combining multiple product models can increase value and complexity.

For example:

A B2B SaaS product requires:

- Account management
- Billing
- Organizational controls

Adding an API introduces:

- Developer experience
- Authentication
- Versioning
- Rate limiting

Adding marketplace functionality introduces:

- Matching
- Payments
- Trust and safety

Adding enterprise functionality introduces:

- Advanced security
- Administration
- Compliance
- Governance

The script includes an illustrative complexity scoring function.

The score is not an industry standard.

It demonstrates the general principle that product complexity often increases as additional user groups, interfaces, integrations, and operational requirements are introduced.

---

# Important Product Type Distinctions

| Product Type | Primary Meaning |
|---|---|
| B2B | Product sold primarily to businesses |
| B2C | Product sold primarily to consumers |
| B2B2C | Product reaching consumers through a business intermediary |
| SaaS | Software delivered as an ongoing service |
| Marketplace | Product facilitating transactions between groups |
| Platform | Foundation enabling others to build or interact |
| API Product | Programmable interface managed as a product |
| Consumer App | Application primarily designed for individual users |
| Enterprise Product | Product designed for complex organizational requirements |

These categories should not be treated as mutually exclusive.

A sophisticated product ecosystem may combine several of them.

The most useful classification depends on the analytical question being asked.

For commercial analysis, customer type and revenue model may be most important.

For technical analysis, APIs, platforms, architecture, and integrations may be more important.

For organizational analysis, enterprise requirements and stakeholder structures may matter most.

For market analysis, marketplaces, network effects, distribution, and ecosystem participation may be central.
