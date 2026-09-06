# Product Lifecycle: Discovery, Validation, Development, Launch, Growth, Maturity, Decline, Retirement

## Introduction

The Product Lifecycle describes how a product evolves from an initial opportunity through investigation, validation, construction, market introduction, expansion, stabilization, decline, and eventual retirement.

A product does not necessarily move through these stages in a perfectly linear sequence. Teams may return from validation to discovery, revisit development after launch, reposition a mature product, or attempt revitalization during decline. Some products may also be discontinued before reaching maturity, while others may remain in a mature state for many years.

The Python script accompanying this README turns the lifecycle into an executable study model. It demonstrates product-management concepts through data structures, calculations, prioritization models, experiments, simulations, quality checks, financial metrics, product analytics, lifecycle decisions, security controls, and retirement planning.

The examples use a fictional workflow-management product called **FlowBoard**.

---

## Lifecycle at a Glance

The script models eight major stages:

| Stage | Primary Question | Dominant Objective |
|---|---|---|
| Discovery | Is there a meaningful problem or opportunity? | Understand |
| Validation | Is the problem, solution, and business case credible? | Test |
| Development | Can the solution be built reliably? | Build |
| Launch | Can the product establish initial adoption? | Introduce |
| Growth | Can adoption and economics scale? | Expand |
| Maturity | How can the product remain valuable and profitable? | Optimize |
| Decline | What should be done as demand or strategic value weakens? | Decide |
| Retirement | How can the product be discontinued responsibly? | Transition |

The boundaries are conceptual rather than absolute.

---

# Discovery

## Meaning of Product Discovery

Product discovery is the process of understanding customers, their problems, existing alternatives, market conditions, constraints, and potential opportunities before committing substantial resources to a particular solution.

The central principle is:

> Understand the problem before optimizing the solution.

Discovery reduces the risk of solving a problem that customers do not consider important.

## Customer Problems

The script represents a discovered problem with the `CustomerProblem` class.

A problem can be examined through dimensions such as:

- Customer segment
- Frequency
- Severity
- Existing alternatives
- Willingness to pay
- Amount of supporting evidence

The script also calculates an illustrative problem score.

The score is a teaching heuristic, not an industry-standard formula. Product teams should avoid treating a numerical score as objective truth.

## Customer Interviews

The `conduct_customer_interview()` function demonstrates structured interview evidence.

Useful discovery questions generally investigate:

- What does the customer currently do?
- How frequently does the problem occur?
- What happens when the problem occurs?
- What alternatives are currently used?
- What has the customer already tried?
- What does the problem cost in time, money, risk, or opportunity?
- How important is solving it?
- What evidence demonstrates that the problem is real?

Behavioral evidence is generally more valuable than hypothetical enthusiasm.

A statement such as "I would probably use this" is weaker evidence than an observed customer behavior such as repeatedly using a workaround, paying for an alternative, or allocating employee time to solve the problem.

## Personas

The `create_persona()` function demonstrates a basic persona containing:

- Role
- Goals
- Frustrations
- Behaviors

A useful persona should represent meaningful behavioral differences rather than simply demographic descriptions.

## Value Proposition

The `build_value_proposition()` function demonstrates the relationship between:

- Target customer
- Problem
- Product solution
- Desired outcome

A value proposition should communicate customer value rather than simply list product features.

---

# Market Discovery

## Competitive Analysis

The script models competitors through the `Competitor` class.

Competitive analysis can examine:

- Price
- Market presence
- Strengths
- Weaknesses
- Distribution
- Features
- Customer segments
- Switching costs
- Differentiation
- Brand position

Competition is not limited to companies offering identical products. A spreadsheet, manual process, internal tool, consultant, or doing nothing can also be an alternative.

## TAM, SAM, and SOM

The script demonstrates three market-sizing concepts.

### TAM

Total Addressable Market represents the theoretical revenue opportunity if the entire relevant market were served.

The simplified formula is:

`TAM = Potential Customers × Annual Revenue Per Customer`

### SAM

Serviceable Available Market represents the portion of TAM that the product can realistically serve based on factors such as geography, customer segment, capabilities, or distribution.

### SOM

Serviceable Obtainable Market represents the realistically obtainable portion of SAM.

These calculations are estimates rather than guaranteed revenue forecasts.

---

# Opportunity Prioritization

The `Opportunity` class demonstrates a weighted opportunity model.

The example considers:

- Customer value
- Business value
- Strategic alignment
- Confidence
- Effort

The resulting score divides weighted value by estimated effort.

This demonstrates a fundamental product-management principle: prioritization should account for both expected value and required investment.

Numerical frameworks are useful for creating consistency, but they cannot completely replace judgment. Inputs such as customer value and strategic alignment often contain substantial uncertainty.

---

# Validation

## Meaning of Validation

Validation determines whether important assumptions are supported by evidence.

The central question changes from:

"Could we build this?"

to:

"Should we build this?"

Validation can investigate several dimensions.

### Desirability

Do customers actually want the proposed solution?

### Feasibility

Can the organization technically and operationally deliver it?

### Viability

Can the product produce sustainable business value?

### Usability

Can customers understand and use the product successfully?

### Strategic Fit

Does the opportunity support the organization's strategy?

### Regulatory and Risk Fit

Can the product operate within relevant legal, privacy, security, contractual, and operational constraints?

---

# Hypothesis-Driven Product Management

The `Hypothesis` class represents a falsifiable assumption.

A strong hypothesis specifies:

- What is expected
- Which metric will measure it
- What threshold constitutes success

For example, a product team might hypothesize that a certain customer segment will request a trial after seeing a product demonstration.

The important principle is to define the success criterion before observing the result. This reduces the temptation to change the definition of success after seeing the evidence.

---

# Experiments

The `design_experiment()` function demonstrates an experiment specification.

A useful experiment includes:

- Hypothesis
- Target metric
- Success threshold
- Duration
- Population
- Experimental design
- Decision rule

The synthetic validation experiment in the script uses deterministic random data for educational purposes.

Synthetic data is not evidence of actual customer demand. It only demonstrates how an experiment could be represented computationally.

---

# MVP

## Minimum Viable Product

An MVP is the smallest real product capable of generating meaningful learning and customer value for a defined problem.

An MVP is not necessarily:

- The cheapest product possible
- A broken product
- A prototype
- A collection of every requested feature

The purpose of an MVP is to reduce important uncertainty while delivering sufficient value to a real target customer.

The script uses `Feature` objects and a simplified prioritization mechanism to demonstrate MVP scope selection.

---

# Prioritization

## RICE-Style Prioritization

The script demonstrates a RICE-style calculation.

A conventional RICE model uses:

`Reach × Impact × Confidence ÷ Effort`

The implementation in the script combines customer and business value into an illustrative impact dimension.

The key concepts are:

- Reach: how many users or customers are affected
- Impact: how strongly the feature influences the intended outcome
- Confidence: how certain the team is about its assumptions
- Effort: engineering, design, operational, or other required work

RICE is a prioritization framework, not a mathematical law.

## Value vs Effort

A simpler approach is to compare expected value with estimated effort.

This can be useful when precise reach estimates are unavailable.

The weakness is that a simple value-effort ratio can ignore strategic considerations, confidence, dependencies, timing, and market dynamics.

---

# Requirements

The script represents requirements through the `Requirement` class.

A requirement should be:

- Clear
- Testable
- Relevant
- Prioritized
- Traceable
- Understandable by the people implementing and validating it

The script distinguishes:

### Functional Requirements

Functional requirements describe what the product should do.

Examples include:

- Users can create tasks.
- Users can assign tasks.
- Users can search projects.

### Non-Functional Requirements

Non-functional requirements describe qualities or constraints.

Examples include:

- Availability
- Performance
- Security
- Privacy
- Scalability
- Accessibility
- Reliability

Both types can materially affect product success.

---

# User Stories

The `create_user_story()` function demonstrates the familiar structure:

`As a [role], I want to [action], so that [benefit].`

A user story identifies:

- User
- Desired behavior
- Intended value

A user story is not necessarily a complete specification. Acceptance criteria, business rules, technical constraints, and edge cases may still be required.

---

# Development

Development transforms validated product requirements into a functioning product.

Important development concerns include:

- Architecture
- Engineering design
- User interface implementation
- Data structures
- APIs
- Integrations
- Testing
- Security
- Performance
- Observability
- Documentation
- Deployment
- Reliability

Product management remains involved during development because assumptions can change when engineering constraints or new evidence emerge.

---

# Agile Development and Sprints

The `Sprint` class demonstrates basic sprint planning.

A sprint can include:

- Sprint number
- Sprint goal
- Planned work
- Completed work

The script calculates average velocity.

Velocity is a planning observation rather than a productivity score. Comparing velocity across unrelated teams can produce misleading conclusions because teams may use different estimation systems, work types, constraints, and definitions of completion.

---

# Velocity and Estimation

The script uses average completed story points to estimate the number of future sprints.

This demonstrates:

`Estimated Sprints = Remaining Work ÷ Average Velocity`

The result is rounded upward because partial sprints are still required to complete remaining work.

Real planning should consider:

- Historical variability
- Dependencies
- Team changes
- Scope changes
- Technical uncertainty
- Interruptions
- Quality work
- Operational work

---

# Burndown

The `calculate_burndown()` function calculates remaining work after successive periods.

A burndown can help reveal:

- Whether work is decreasing
- Whether scope is changing
- Whether delivery is behind expectation
- Whether remaining work is concentrated near the end

A burndown should not be interpreted in isolation. A team can burn down work while delivering little customer value.

---

# Quality Assurance

Quality is part of the product lifecycle rather than a final activity performed immediately before launch.

Quality practices can include:

- Unit testing
- Integration testing
- System testing
- Regression testing
- Acceptance testing
- Performance testing
- Security testing
- Accessibility testing
- Usability testing
- Production monitoring

The script uses acceptance criteria and defect calculations to demonstrate basic quality mechanisms.

---

# Defect Escape Rate

The script defines defect escape rate as:

`Escaped Defects ÷ Total Defects`

This measures the proportion of identified defects that were discovered after reaching later stages such as production.

A high escape rate may indicate weaknesses in:

- Requirements
- Design
- Testing
- Review
- Automation
- Release controls
- Observability

The metric must be interpreted in context because not all defects have the same severity.

---

# Release Management

The `Release` class demonstrates basic release readiness.

A release includes:

- Version
- Release date
- Features
- Known issues
- Rollback plan

A critical known issue can block release readiness in the example.

Production release decisions can also depend on:

- Security
- Data migration
- Backward compatibility
- Operational readiness
- Support capacity
- Monitoring
- Feature flags
- Rollback capability
- Legal requirements
- Customer commitments

---

# Launch

Launch is the transition from controlled product development to market exposure.

A launch plan can contain:

- Target segment
- Positioning
- Pricing
- Distribution channels
- Marketing
- Sales
- Customer support
- Analytics
- Operational readiness
- Launch objectives

A launch is not the end of product development. It creates new evidence from actual market behavior.

---

# Launch Readiness

The script calculates a simplified launch-readiness score across five dimensions:

- Product readiness
- Support readiness
- Analytics readiness
- Marketing readiness
- Rollback readiness

A real launch checklist may be substantially larger.

The purpose of a readiness framework is to expose missing dependencies before market exposure.

---

# Launch Funnel

The `FunnelMetrics` class models:

`Visitors → Signups → Activated Users → Paying Customers`

Each transition has a conversion rate.

The script calculates:

- Visitor-to-signup conversion
- Signup-to-activation conversion
- Activation-to-paid conversion
- Visitor-to-paid conversion

A funnel identifies where users are lost.

For example, strong visitor-to-signup conversion followed by poor activation suggests that the problem may be product onboarding or perceived product value rather than acquisition.

---

# Activation

Activation represents an early product behavior associated with realizing meaningful value.

The appropriate activation event differs by product.

Examples might include:

- Completing a first workflow
- Inviting a teammate
- Creating a first project
- Completing a first transaction
- Using a core feature repeatedly

Activation should be defined around meaningful customer value rather than arbitrary activity.

---

# Growth

Growth occurs when a product develops repeatable mechanisms for increasing:

- Customers
- Users
- Revenue
- Usage
- Retention
- Distribution
- Market share

Growth can come from:

- Paid acquisition
- Sales
- Partnerships
- Organic search
- Referrals
- Product-led growth
- Network effects
- Expansion revenue
- New geographic markets
- New customer segments

Growth should be evaluated together with retention and economics.

---

# MRR and ARR

The script calculates recurring revenue using:

`MRR = Customers × Average Monthly Revenue Per Customer`

and:

`ARR = MRR × 12`

These are simplified subscription-business calculations.

They should not be confused with accounting revenue recognition or comprehensive financial reporting.

---

# Unit Economics

Unit economics examine the economics associated with acquiring and serving customers.

The script implements:

- CAC
- ARPU
- LTV
- LTV/CAC
- CAC payback period

---

# Customer Acquisition Cost

CAC is represented as:

`CAC = Sales and Marketing Cost ÷ New Customers`

CAC can vary by:

- Channel
- Customer segment
- Geography
- Sales motion
- Product tier
- Time period

Blended CAC can hide major differences between acquisition channels.

---

# ARPU

Average Revenue Per User is represented as:

`ARPU = Revenue ÷ Active Customers`

ARPU can be affected by:

- Pricing
- Packaging
- Discounts
- Expansion
- Customer mix
- Usage
- Contract structure

---

# Lifetime Value

The script uses a simplified subscription model:

`LTV ≈ ARPU × Gross Margin ÷ Monthly Churn`

This is an approximation.

It assumes relatively stable revenue, margin, and churn. Real LTV analysis can incorporate:

- Cohort retention
- Expansion
- Contraction
- Gross-margin changes
- Segment behavior
- Contract duration
- Discounting
- Acquisition channel
- Customer-specific economics

---

# LTV/CAC

The script calculates:

`LTV/CAC = LTV ÷ CAC`

A higher ratio can indicate stronger unit economics, while a low ratio can indicate acquisition or retention problems.

The metric should not be optimized blindly. Increasing LTV through excessive pricing or reducing CAC by lowering customer quality can produce misleading improvements.

---

# CAC Payback

CAC payback estimates how long it takes for gross profit generated by a customer to recover acquisition cost.

The simplified calculation is:

`CAC Payback = CAC ÷ Monthly Gross Profit Per Customer`

Shorter payback generally reduces capital requirements.

---

# Retention

Retention measures the proportion of users or customers who remain active over time.

The script implements:

`Retention = Retained Users ÷ Starting Users`

Retention is particularly important because acquisition without retention can create a continuously leaking customer base.

---

# Cohort Analysis

The `Cohort` class demonstrates cohort retention curves.

A cohort is a group of users sharing a common starting point, such as:

- Signup month
- Subscription month
- Acquisition campaign
- Product version
- Geographic launch period

Cohort analysis can reveal whether product quality is improving.

For example, newer cohorts retaining better than older cohorts can indicate successful product improvements.

---

# Churn

Churn represents customers or revenue leaving the product.

Customer churn and revenue churn are not identical.

A business can have:

- High customer churn but stable revenue
- Low customer churn but declining revenue
- Negative net revenue churn because expansion exceeds churn

The script demonstrates churn reasons such as:

- Missing integrations
- Price
- Low usage
- Competitor switching

Understanding the cause of churn is usually more actionable than merely knowing its percentage.

---

# Net Revenue Retention

The script implements:

`NRR = (Starting Revenue + Expansion - Contraction - Churn) ÷ Starting Revenue`

NRR can exceed 100% when expansion revenue from existing customers exceeds revenue lost through contraction and churn.

This makes NRR particularly useful for subscription products with expansion opportunities.

---

# Growth Loops

The `GrowthLoop` class demonstrates a loop in which existing users generate opportunities for new users.

A simplified mechanism is:

`Users × Actions × Invite Rate × Conversion Rate`

Growth loops differ from one-time acquisition campaigns because the output of one cycle becomes an input to later cycles.

Examples include:

- Referral loops
- Collaboration loops
- User-generated-content loops
- Marketplace loops
- Network-effect loops

The quality of a growth loop depends on actual user behavior and economics.

---

# Pricing

Pricing is part of product strategy.

The script models pricing tiers using `PricingPlan`.

Pricing decisions can consider:

- Customer willingness to pay
- Customer value
- Competitor pricing
- Cost structure
- Segmentation
- Usage
- Packaging
- Strategic positioning
- Sales motion

Price is not simply a cost-plus calculation. It also communicates positioning and determines how value is monetized.

---

# Price Elasticity

The `price_sensitivity()` function demonstrates a simplified elasticity model.

Elasticity describes how demand changes relative to price changes.

A negative elasticity indicates that higher prices are associated with lower demand in the model.

Real-world pricing experiments need careful interpretation because observed demand can also be affected by:

- Product changes
- Seasonality
- Customer mix
- Competitors
- Discounts
- Sales channels
- Economic conditions

---

# Maturity

A mature product usually has:

- Established customers
- Recognizable market position
- More predictable demand
- Significant installed base
- Stronger operational processes
- Greater competitive pressure
- Increasing optimization needs

Maturity does not mean that the product is obsolete.

A mature product can remain strategically important and financially strong for many years.

---

# Maturity Strategies

The script distinguishes several broad strategies.

### Invest for Growth

Appropriate when the market is expanding and the product has room to increase penetration.

### Optimize and Expand

Appropriate when growth remains attractive and economics are healthy.

### Defend and Harvest

Appropriate when growth is slower but profitability is strong.

### Reassess Strategic Role

Appropriate when economics and growth are insufficient or uncertain.

Real product strategy should consider competitive dynamics, customer dependence, organizational capabilities, and future market changes.

---

# Gross Margin

Gross margin is represented as:

`Gross Margin = (Revenue - Cost of Goods Sold) ÷ Revenue`

Gross margin measures the portion of revenue remaining after direct costs associated with delivering the product.

The appropriate cost definition varies by business model.

---

# Operating Margin

The script calculates:

`Operating Margin = (Revenue - COGS - Operating Expenses) ÷ Revenue`

Operating margin incorporates broader operating expenses.

A product can have attractive gross margins while still being unprofitable because of:

- Sales costs
- Marketing costs
- Research and development
- Support
- Infrastructure
- Administration

---

# Market Share

The script calculates:

`Market Share = Product Sales ÷ Total Market Sales`

Market share can be expressed by:

- Revenue
- Units
- Customers
- Transactions
- Usage

The appropriate measure depends on the market.

---

# Experimentation and A/B Testing

The script demonstrates a simple A/B test through `ExperimentVariant`.

It calculates:

- Conversion rate
- Absolute lift
- Relative lift
- Approximate two-proportion z-test
- Approximate p-value

---

# Absolute vs Relative Lift

Suppose the control converts at 10% and treatment converts at 11%.

Absolute lift:

`11% - 10% = 1 percentage point`

Relative lift:

`(11% - 10%) ÷ 10% = 10%`

These are different measurements and should not be confused.

---

# Statistical Significance

The script includes an approximate two-proportion z-test.

A low p-value can indicate that the observed difference would be relatively unlikely under a specified null hypothesis.

Statistical significance does not automatically mean:

- The effect is commercially important.
- Customers prefer the product.
- The experiment was well designed.
- The result will replicate.
- The change is worth implementing.

Product decisions should consider effect size, business value, confidence intervals, experiment quality, and practical significance.

---

# Decline

Decline occurs when one or more important indicators weaken over time.

Possible signals include:

- Declining active users
- Falling revenue
- Increasing churn
- Reduced engagement
- Lower margins
- Increasing support costs
- Competitive displacement
- Technology obsolescence
- Changing customer behavior
- Regulatory changes
- Strategic deprioritization

Decline should be diagnosed rather than assumed.

A temporary downturn does not necessarily mean the product has entered structural decline.

---

# Decline Signals

The script uses `DeclineSignal` to compare current and previous values.

Examples include:

- Users where higher is better
- Revenue where higher is better
- Churn where lower is better

The `deterioration()` method normalizes deterioration according to the direction that represents improvement.

This demonstrates an important principle: metrics cannot be interpreted correctly without knowing whether higher or lower values are desirable.

---

# Strategic Responses to Decline

Possible responses include:

### Revitalize

Invest in product improvements, repositioning, new segments, or new capabilities.

### Harvest

Reduce investment while continuing to capture profitable remaining demand.

### Reposition

Change the product's target segment, positioning, or use case.

### Divest

Transfer or sell the product where appropriate.

### Retire

Discontinue the product in a controlled manner.

The right decision depends on customer value, economics, strategic fit, dependencies, and available alternatives.

---

# Decline Does Not Always Mean Retirement

A declining product may still be strategically important.

Examples include products that:

- Generate substantial cash flow
- Serve critical customers
- Provide infrastructure for other products
- Have contractual commitments
- Support ecosystem relationships
- Have high switching costs
- Require a carefully managed successor

The decision to retire should therefore be separate from simply observing decline.

---

# Retirement

Retirement is the intentional discontinuation of a product.

A responsible retirement process can include:

1. Strategic decision
2. Impact assessment
3. Retirement timeline
4. Internal alignment
5. Customer communication
6. Migration planning
7. Data export
8. Contract management
9. Support planning
10. Security review
11. Infrastructure shutdown
12. Final documentation

---

# Retirement Planning

The `RetirementPlan` class demonstrates:

- Announcement date
- End-of-sale date
- End-of-support date
- Migration plan
- Data-export capability
- Communication channels
- Responsible owner

A product should not be retired merely because its infrastructure can technically be switched off.

---

# Migration

Migration completion is represented as:

`Migrated Customers ÷ Eligible Customers`

Migration planning should consider:

- Customer segmentation
- Migration tooling
- Data compatibility
- Downtime
- Training
- Contracts
- Support
- Pricing differences
- Feature differences
- Customer communications

High-risk customers may require dedicated migration assistance.

---

# Data and Security During Retirement

Retirement can introduce security risks because legacy systems are often difficult to maintain.

Important concerns include:

- Data retention
- Data deletion
- Secure exports
- Access revocation
- Credential rotation
- Backup handling
- Third-party dependencies
- Archived systems
- Log retention
- Regulatory obligations
- Customer contractual commitments

Security responsibilities do not disappear merely because a product is no longer commercially active.

---

# Security Across the Lifecycle

The script provides a security-control mapping for every stage.

## Discovery

Identify security, privacy, regulatory, and trust requirements early.

## Validation

Test assumptions involving sensitive information, permissions, identity, and threat scenarios.

## Development

Use secure development practices, access controls, dependency management, code review, and security testing.

## Launch

Verify:

- Logging
- Monitoring
- Incident response
- Configuration
- Authentication
- Authorization
- Backup and recovery

## Growth

Scaling can introduce new risks involving:

- Increased attack surface
- Identity management
- Abuse
- Fraud
- Data volume
- Infrastructure complexity

## Maturity

Security debt can accumulate over time. Mature products need:

- Patching
- Dependency upgrades
- Permission reviews
- Secret rotation
- Threat reassessment
- Legacy-system management

## Decline

Security controls should not be abandoned simply because investment is declining.

## Retirement

Retirement requires secure handling of remaining data and infrastructure.

---

# Technical Debt and Product Debt

The script represents debt through `DebtItem`.

Debt can include:

### Technical Debt

Shortcuts or design decisions that increase future engineering cost.

### Product Debt

Accumulated usability problems, inconsistent workflows, outdated features, poor documentation, fragmented experiences, or other product-quality issues.

Debt prioritization should consider:

- Impact
- Urgency
- Effort
- Risk
- Strategic importance

Not every debt item should be eliminated immediately.

---

# Product Roadmaps

The script represents roadmap items through:

- Time period
- Objective
- Success metric
- Target

A strong roadmap emphasizes outcomes rather than simply listing features.

For example, "Improve activation from 45% to 60%" is an outcome-oriented objective, whereas "Build onboarding dashboard" describes an output.

Outputs can be useful, but the product team should understand the intended outcome behind them.

---

# Product Analytics

The `ProductMetrics` class provides a structure for monthly:

- Customers
- MAU
- Revenue
- Churn
- CAC
- Gross margin

The `analyze_metric_trend()` function calculates:

- Minimum
- Maximum
- Mean
- Median

These descriptive statistics are useful starting points but do not explain causality.

A metric trend should be investigated against:

- Product changes
- Marketing campaigns
- Pricing changes
- Seasonality
- Customer mix
- Competitor behavior
- Operational incidents
- Market conditions

---

# Product Health

The `ProductHealth` class combines:

- Activation
- Retention
- Revenue growth
- Gross margin
- Satisfaction

into a weighted health score.

The purpose is to demonstrate multi-dimensional evaluation.

A single product metric rarely captures the full health of a product.

For example:

- High growth with poor retention can be unhealthy.
- High retention with negative economics can be unsustainable.
- Strong revenue with poor customer satisfaction can create long-term risk.
- Strong satisfaction with insufficient demand can indicate a small but unscalable market.

---

# Portfolio Management

Organizations frequently operate multiple products simultaneously.

The lifecycle of each product may differ.

One product may be:

- In discovery
- Another in growth
- Another mature
- Another in decline

Portfolio management therefore requires allocation of:

- Capital
- People
- Engineering capacity
- Marketing resources
- Management attention

The script uses `PortfolioProduct` to demonstrate broad investment postures.

---

# Stage-Based Product Decisions

The `product_decision()` function demonstrates why the same evidence can lead to different decisions depending on lifecycle stage.

In discovery, weak evidence may justify additional research.

During growth, strong customer and business value may justify investment in scaling.

During decline, the same weak growth may trigger a retirement assessment.

The lifecycle stage provides context for interpreting metrics.

---

# Important Distinctions

## Discovery vs Validation

Discovery explores problems and opportunities.

Validation tests explicit hypotheses.

Discovery is broader and exploratory; validation is more focused and evidence-driven.

## Validation vs Development

Validation asks whether an opportunity and solution deserve investment.

Development determines how to construct and operate the solution.

## MVP vs Prototype

A prototype primarily helps the team learn or communicate an idea.

An MVP is intended to create real customer value while generating meaningful evidence.

## Launch vs Growth

Launch establishes initial market exposure.

Growth establishes repeatable mechanisms for expanding adoption and economics.

## Growth vs Maturity

Growth emphasizes expansion.

Maturity emphasizes optimization, efficiency, differentiation, and defense.

## Maturity vs Decline

Maturity can involve stable or improving economics.

Decline involves weakening demand, economics, strategic relevance, or competitive position.

## Decline vs Retirement

Decline is a condition.

Retirement is a strategic decision.

## Feature Delivery vs Product Outcome

Feature delivery measures what was built.

Product outcomes measure whether customer or business conditions improved.

---

# Edge Cases

The product lifecycle is not always cleanly sequential.

## A Product Can Decline Before Maturity

A product may be launched and then fail to achieve sufficient adoption.

## A Product Can Re-enter Growth

A mature or declining product can sometimes regain growth through:

- Repositioning
- New technology
- New customer segments
- Major product improvements
- New distribution channels
- Strategic partnerships

## Different Metrics Can Move in Opposite Directions

The script's `classify_lifecycle_ambiguity()` function demonstrates conditions such as:

- Users increasing while revenue decreases
- Users decreasing while revenue increases
- Growth occurring without profitability

These situations require deeper analysis.

## Product and Market Lifecycles Can Differ

A product may be mature while its market continues growing.

A product may also decline even while the broader market grows because competitors are taking share.

## Technology Lifecycle and Product Lifecycle Can Differ

A product can have strong demand while its underlying technology becomes obsolete.

Conversely, new technology can exist without a viable product market.

---

# Common Mistakes

## Starting With a Solution

Building a product before understanding the problem can result in low-value products.

A better approach is to investigate customer behavior and existing alternatives first.

## Treating Opinions as Evidence

Customer enthusiasm is useful but weaker than observed behavior.

## Building Too Much Before Validation

Large investments increase the cost of being wrong.

## Measuring Vanity Metrics

Page views, downloads, or registrations may look impressive without demonstrating customer value.

## Scaling Acquisition Before Retention

Acquiring more users does not solve a retention problem.

## Ignoring Unit Economics

Growth can destroy value when customer acquisition costs exceed the economic value generated by customers.

## Confusing Launch With Product-Market Fit

A successful launch does not prove long-term demand.

## Ignoring Product Debt

Accumulated usability and technical problems can eventually slow innovation and increase operational costs.

## Waiting Too Long During Decline

Delayed action can reduce the number of strategic options available.

## Treating Retirement as Infrastructure Shutdown

Retirement requires customer, data, security, contractual, operational, and communication planning.

---

# Limitations of Quantitative Frameworks

The Python script contains many numerical models, but numerical precision should not be mistaken for decision precision.

A score such as 8.4 versus 7.9 does not necessarily mean that one opportunity is objectively superior.

Quantitative frameworks are most useful when they:

- Make assumptions visible
- Encourage consistent comparison
- Identify missing information
- Support prioritization discussions
- Provide measurable decision criteria

They become dangerous when teams use them mechanically without examining the quality of their inputs.

---

# Performance Considerations

The script is designed for education and small-scale analysis.

Most functions operate in:

- O(n) time for simple list processing
- O(1) space for basic calculations
- O(n) space where complete result collections are returned

For example, `average_cohort_retention()` processes cohort retention data and stores the resulting averages.

The algorithms are intentionally straightforward because readability and conceptual clarity are more important here than optimization for massive datasets.

For production analytics systems, teams may need:

- Database aggregation
- Columnar storage
- Incremental processing
- Caching
- Distributed computation
- Streaming pipelines
- Data-quality monitoring

---

# Implementation Considerations

Production product-management systems may integrate:

- Product analytics
- CRM systems
- Billing systems
- Customer-support platforms
- Experimentation systems
- Project-management tools
- Data warehouses
- Feature-flag systems
- Monitoring platforms

The script deliberately avoids external dependencies so that the lifecycle concepts can be studied without requiring a particular software environment.

---

# Data Quality

Product decisions depend on trustworthy data.

Common data-quality problems include:

- Duplicate customers
- Missing events
- Incorrect timestamps
- Inconsistent customer identifiers
- Tracking changes between product versions
- Bot traffic
- Test accounts
- Incomplete revenue attribution
- Incorrect churn definitions

A mathematically correct calculation can still produce a poor decision if the underlying data is incorrect.

---

# Metric Definitions Matter

A product team should define metrics precisely.

For example, "active user" can mean:

- Logged in during a period
- Performed a core action
- Completed a transaction
- Opened an application

These definitions can produce very different results.

Metrics should have documented:

- Name
- Definition
- Data source
- Time window
- Inclusion rules
- Exclusion rules
- Owner
- Calculation method

---

# Production Considerations

A mature product-management process should connect product strategy to operational reality.

Important production concerns include:

- Reliability
- Availability
- Incident management
- Capacity
- Monitoring
- Security
- Privacy
- Support
- Cost
- Deployment
- Rollback
- Disaster recovery
- Compliance

The script demonstrates availability through:

`Availability = 1 - Unavailable Time ÷ Total Time`

---

# Product Operations

Product operations become increasingly important as products scale.

Responsibilities can include:

- Product data quality
- Release coordination
- Customer communication
- Support processes
- Product documentation
- Internal enablement
- Experiment governance
- Product tooling
- Lifecycle governance

A product that is technically successful but operationally difficult can still produce poor customer outcomes.

---

# Product Governance

The `ProductDecisionRecord` class demonstrates a decision-record approach.

A strong decision record captures:

- Decision
- Context
- Alternatives
- Rationale
- Owner
- Date

Decision records improve organizational memory and make important strategic choices easier to understand later.

---

# Change Management

Products change continuously.

A change may affect:

- Customers
- Revenue
- Operations
- Engineering
- Security
- Support
- Legal obligations

The `ChangeRequest` class demonstrates a simplified scoring model involving:

- Customer impact
- Business impact
- Technical risk
- Urgency

High-impact changes should receive appropriate analysis before implementation.

---

# End-to-End FlowBoard Simulation

The script includes a complete fictional lifecycle for FlowBoard.

The sequence is:

1. Discovery
2. Validation
3. Development
4. Launch
5. Growth
6. Maturity
7. Decline
8. Retirement

The metrics change at each stage.

This demonstrates an important principle: the product-management objective changes as the product evolves.

During discovery, the primary goal is learning.

During development, the primary goal is reliable delivery.

During launch, the primary goal is establishing adoption.

During growth, the focus shifts toward scalable acquisition, activation, retention, and economics.

During maturity, optimization and defense become more important.

During decline, the organization must determine whether the product should be revitalized, repositioned, harvested, divested, or retired.

During retirement, controlled transition becomes the central concern.

---

# Lifecycle-Specific Decision Questions

## Discovery

- Who has the problem?
- How important is the problem?
- How frequently does it occur?
- What alternatives exist?
- Who pays for the problem today?
- Why has it not already been solved?
- Is the opportunity strategically relevant?

## Validation

- Does the proposed solution solve the problem?
- Will customers use it?
- Will they pay?
- Can it be built?
- Can it be delivered reliably?
- Can it produce sustainable economics?
- What assumptions remain uncertain?

## Development

- Is the MVP sufficiently scoped?
- Are requirements testable?
- Are dependencies understood?
- Are quality requirements defined?
- Are security and privacy requirements addressed?
- Is analytics instrumentation available?

## Launch

- Is the product ready?
- Is the target market defined?
- Is positioning clear?
- Is pricing appropriate?
- Is support prepared?
- Is analytics functioning?
- Is rollback possible?

## Growth

- Is acquisition repeatable?
- Is activation strong?
- Is retention healthy?
- Are unit economics sustainable?
- Can infrastructure scale?
- Can customer support scale?

## Maturity

- Is the product profitable?
- Is market share stable?
- What differentiates the product?
- What customer needs remain unsolved?
- Which improvements produce the greatest economic value?
- Should investment increase, remain stable, or decrease?

## Decline

- Is the decline temporary or structural?
- Why are customers leaving?
- Is the market changing?
- Are competitors taking share?
- Can the product be revitalized?
- Is the product still strategically important?
- What would retirement cost?

## Retirement

- Who is affected?
- When will sales stop?
- When will support stop?
- How will customers migrate?
- How will data be exported?
- What happens to remaining infrastructure?
- What contractual obligations remain?
- How will customer communications be handled?

---

# Real-World Relevance

The product lifecycle framework applies across many product categories.

Examples include:

- SaaS applications
- Mobile applications
- Consumer electronics
- Banking products
- Insurance products
- Enterprise software
- Marketplaces
- E-commerce services
- Media products
- Industrial products
- Transportation services
- Internal enterprise platforms

The lifecycle is especially useful when different organizational functions need a shared understanding of what the product currently requires.

---

# Relationship Between Product Lifecycle and Product Management

Product management connects customer problems, business objectives, technology, and execution.

At different lifecycle stages, the product manager's emphasis changes.

| Lifecycle Stage | Typical Product Management Emphasis |
|---|---|
| Discovery | Customer research and opportunity identification |
| Validation | Experiments and evidence |
| Development | Requirements, prioritization, execution, quality |
| Launch | Go-to-market coordination and measurement |
| Growth | Acquisition, activation, retention, economics |
| Maturity | Optimization, differentiation, profitability |
| Decline | Strategic assessment and resource allocation |
| Retirement | Migration, communication, risk management |

The underlying responsibility remains the same: maximize sustainable customer and business value under constraints.

---

# Key Metrics by Lifecycle Stage

| Stage | Useful Metrics |
|---|---|
| Discovery | Interview evidence, problem frequency, severity, market size |
| Validation | Conversion, willingness to pay, experiment outcomes, usability |
| Development | Velocity, defects, cycle time, quality, release readiness |
| Launch | Acquisition, activation, conversion, reliability |
| Growth | Growth rate, retention, churn, CAC, LTV, NRR |
| Maturity | Market share, margins, retention, profitability, efficiency |
| Decline | Revenue decline, user decline, churn, market share loss, cost-to-serve |
| Retirement | Migration completion, remaining customers, unresolved dependencies, retirement risk |

Metrics should always be interpreted according to the product's business model.

---

# Best Practices

## Start With Customer Problems

Investigate actual customer behavior before committing heavily to a solution.

## Define Evidence Before Running Experiments

Specify metrics and thresholds before observing results.

## Prioritize Explicitly

Make value, confidence, effort, reach, and strategic considerations visible.

## Keep the MVP Focused

Build enough to create value and learn without unnecessarily increasing complexity.

## Instrument the Product

Important customer behaviors should be measurable.

## Monitor Retention

Retention frequently reveals product value more clearly than acquisition numbers.

## Track Unit Economics

Growth should be evaluated together with acquisition costs, revenue, margins, and customer lifetime value.

## Use Cohorts

Aggregate averages can hide changes in customer behavior. Cohort analysis helps identify whether newer users behave differently.

## Manage Technical and Product Debt

Debt should be prioritized according to impact and risk rather than ignored until it becomes an emergency.

## Treat Security as a Lifecycle Responsibility

Security should be considered during discovery, development, operation, decline, and retirement.

## Plan for Retirement Early

Products should have a plausible long-term strategic path even if retirement is not currently expected.

---

# How the Python Script Is Organized

The script progresses through the lifecycle and supporting product-management disciplines.

Major implementation sections include:

- Lifecycle stage definitions
- Customer discovery
- Problem scoring
- Personas
- Value propositions
- Competitive analysis
- Market sizing
- Opportunity prioritization
- Hypothesis validation
- Conversion and retention calculations
- MVP prioritization
- Requirements
- User stories
- Sprint planning
- Velocity and burndown
- Quality assurance
- Release readiness
- Launch planning
- Funnel analysis
- Activation
- Growth
- MRR and ARR
- CAC and LTV
- Cohort retention
- Churn
- Net revenue retention
- Growth loops
- Pricing
- Market share
- Gross and operating margins
- Product maturity
- A/B testing
- Statistical approximation
- Decline detection
- Retirement planning
- Migration
- Security controls
- Technical and product debt
- Roadmap quality
- Product operations
- Governance
- Product health
- Portfolio management
- Lifecycle decision logic
- End-to-end simulation
- Automated tests

---

# Running the Script

The file requires Python 3 and uses only the Python standard library.

Running the script executes:

1. Lifecycle explanations
2. Discovery examples
3. Market-sizing calculations
4. Competitive analysis
5. Opportunity prioritization
6. Validation experiments
7. MVP selection
8. Requirement examples
9. Development planning
10. Quality calculations
11. Launch analysis
12. Growth metrics
13. Unit economics
14. Cohort analysis
15. Churn analysis
16. Maturity analysis
17. A/B experimentation
18. Decline analysis
19. Retirement analysis
20. Security lifecycle mapping
21. Portfolio analysis
22. Product health calculations
23. Lifecycle simulation
24. Lifecycle checklists
25. Common product-management mistakes
26. Conceptual comparisons
27. Automated unit tests

The script's test suite uses Python's built-in `unittest` framework.

---

# Testing and Error Handling

The script deliberately validates many inputs.

Examples include rejecting:

- Negative customer counts
- Negative revenue
- Invalid percentages
- Conversion counts greater than opportunity counts
- Retained users greater than starting users
- Zero or negative sprint velocity
- Invalid experiment parameters
- Invalid margin ranges
- Invalid lifecycle metric ranges

These checks demonstrate an important production principle: calculations should not silently accept impossible business data.

---

# Practical Interpretation

The most important lesson from the implementation is that a product lifecycle is not merely a chart showing sales rising and falling.

It is a sequence of changing management problems.

Early in the lifecycle, uncertainty is high and learning is the priority.

During development, execution and quality become critical.

At launch, the organization must establish adoption while observing real customer behavior.

During growth, the challenge becomes scaling acquisition, retention, operations, infrastructure, and economics.

During maturity, optimization and strategic defense become increasingly important.

During decline, the organization must distinguish temporary weakness from structural deterioration and choose a deliberate response.

During retirement, customer continuity, data management, communication, security, and operational control become central.

The Python implementation expresses these changes through executable models, metrics, decision rules, validation logic, simulations, and lifecycle-specific controls.
