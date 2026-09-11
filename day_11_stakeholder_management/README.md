# Stakeholder management

## Introduction

Stakeholder management is the systematic process of identifying people, groups, and organizations that can affect a project, are affected by it, or have a legitimate interest in its outcomes. Effective stakeholder management involves understanding stakeholder needs, influence, expectations, concerns, relationships, communication requirements, decision rights, and appropriate engagement strategies.

Stakeholder management is closely connected to project management, product management, change management, governance, leadership, communication, risk management, and organizational behavior.

The Python script provides an executable study reference that moves from fundamental concepts to quantitative analysis, communication planning, conflict management, stakeholder networks, risk analysis, engagement tracking, governance, and production-oriented considerations.

## Fundamental terminology

### Stakeholder

A stakeholder is a person, group, or organization that can influence a project, be affected by its activities or outcomes, or reasonably perceive itself as affected.

Examples include:

- Project sponsors
- Project managers
- Employees
- Customers
- Suppliers
- Investors
- Regulators
- Government organizations
- Partners
- Local communities
- Internal departments
- Senior executives

Stakeholders do not all have the same level of influence or interest. Treating every stakeholder identically can lead to ineffective communication and poor prioritisation.

### Internal stakeholder

An internal stakeholder exists within the organization.

Examples include:

- Project managers
- Employees
- Executives
- Finance teams
- Human resources
- Engineering teams
- Sales teams
- Operations teams
- Legal teams
- Internal customers

Internal stakeholders often have direct relationships with organizational resources, decision-making structures, processes, and policies.

### External stakeholder

An external stakeholder exists outside the organization.

Examples include:

- Customers
- Suppliers
- Vendors
- Regulators
- Investors
- Partners
- Government agencies
- Communities
- Industry organizations

External stakeholders can create contractual, commercial, regulatory, reputational, or operational consequences.

## Internal versus external stakeholders

The distinction is useful because internal and external stakeholders often have different relationships with the organization.

| Dimension | Internal stakeholders | External stakeholders |
|---|---|---|
| Organizational position | Inside the organization | Outside the organization |
| Examples | Employees, executives, departments | Customers, vendors, regulators |
| Typical concern | Execution, resources, priorities | Outcomes, commitments, compliance |
| Influence source | Position, expertise, authority | Contract, market power, regulation, reputation |
| Communication | Operational and organizational | Audience-specific and relationship-oriented |
| Major risks | Resistance, misalignment, resource conflicts | Contractual, regulatory, commercial, reputational |

The distinction is not absolute. An external customer can have greater practical influence than an internal employee, while an internal executive can have extremely high formal authority.

## Stakeholder identification

Stakeholder identification should occur early and should be repeated throughout the project or product lifecycle.

A stakeholder register in the script contains:

- Name
- Internal or external classification
- Role
- Influence
- Interest
- Impact
- Urgency
- Legitimacy
- Proximity
- Expectations
- Concerns
- Preferred communication channels

Stakeholder identification should consider both obvious and less obvious participants.

A narrow approach might identify only the project sponsor and project team. A broader analysis may also identify customers, suppliers, regulators, finance teams, operations teams, communities, and people affected indirectly by the outcome.

## Stakeholder influence

Influence is the ability of a stakeholder to affect decisions, resources, behavior, priorities, outcomes, or project direction.

Influence can come from different sources:

- Formal authority
- Organizational position
- Financial control
- Technical expertise
- Contractual rights
- Regulatory authority
- Customer purchasing power
- Social influence
- Reputation
- Access to critical resources
- Control over dependencies

Formal authority and practical influence are not always identical.

A person without formal authority may have considerable influence because many others trust their expertise or because they control an important dependency.

## Stakeholder interest

Interest represents the degree to which a stakeholder cares about the project or is affected by its outcome.

High interest may result from:

- Direct operational impact
- Financial consequences
- Career consequences
- Customer experience
- Regulatory responsibility
- Strategic importance
- Personal responsibility
- Organizational dependency

Interest can change during the project.

For example, an executive may initially have low interest in a technical implementation but become highly interested when the project begins affecting revenue or regulatory compliance.

## Stakeholder impact

Impact describes the degree to which the project or its decisions affect the stakeholder, or the degree to which stakeholder involvement can materially affect project outcomes.

Impact should be distinguished from influence.

A stakeholder may have:

- High influence and high impact
- High influence and low impact
- Low influence and high impact
- Low influence and low impact

A low-influence stakeholder should not automatically be considered unimportant. Such stakeholders may possess important knowledge, represent affected communities, or become more influential as circumstances change.

## Stakeholder mapping

Stakeholder mapping converts stakeholder analysis into categories that support decision-making.

One of the most widely used conceptual models is the power-interest grid.

The four basic categories are:

### Manage closely

High influence and high interest.

These stakeholders normally require active engagement, regular communication, decision alignment, and careful expectation management.

Examples may include:

- Executive sponsors
- Major customers
- Key decision makers
- Critical business owners

### Keep satisfied

High influence and lower interest.

These stakeholders have substantial ability to affect the project but may not need detailed operational information.

The objective is to maintain confidence without overwhelming them with unnecessary detail.

### Keep informed

Lower influence and high interest.

These stakeholders may care strongly about the outcome even though they have limited formal authority.

Communication should provide sufficient visibility and opportunities for relevant feedback.

### Monitor

Lower influence and lower interest.

These stakeholders generally require lighter monitoring. Their position should still be reviewed because their influence or interest may change.

## Power-interest classification in the script

The script implements the power-interest model using a simple 1-5 scale.

An influence score of 4 or 5 represents high influence.

An interest score of 4 or 5 represents high interest.

The resulting classification is:

- High influence + high interest: Manage closely
- High influence + low interest: Keep satisfied
- Low influence + high interest: Keep informed
- Low influence + low interest: Monitor

The model is a decision aid rather than a permanent classification.

## Influence-impact analysis

The script also calculates:

`influence × impact`

This provides a simple prioritisation signal.

The multiplication is useful because a stakeholder with both high influence and high impact receives a significantly higher score than a stakeholder who is high on only one dimension.

The calculation should not be interpreted as a universal stakeholder-management standard. Organizations can use different scoring models depending on their context.

## Stakeholder salience

Stakeholder salience considers three major dimensions:

- Power
- Legitimacy
- Urgency

The script uses:

`power × legitimacy × urgency`

as an educational salience score.

### Power

The stakeholder has the ability to influence outcomes.

### Legitimacy

The stakeholder has a valid or recognized relationship with the project, organization, decision, or issue.

### Urgency

The stakeholder's claim requires attention because it is time-sensitive or particularly critical.

Salience can change over time. A stakeholder with moderate importance at the beginning of a project may become highly salient when a regulatory deadline or critical operational event occurs.

## Stakeholder prioritisation

A stakeholder register can contain dozens or hundreds of stakeholders. Prioritisation helps determine where management attention should be concentrated.

The script uses a weighted model involving:

- Influence
- Interest
- Impact
- Urgency
- Legitimacy
- Proximity

Each dimension is normalized to a common scale before being combined.

This illustrates an important analytical principle: metrics should be comparable before combining them.

Weights should be explicitly defined rather than hidden inside an unexplained formula.

## Expectations

Stakeholder expectations describe what stakeholders believe should happen.

Examples include:

- Delivery by a specific date
- Specific quality levels
- Budget control
- Frequent reporting
- Product usability
- Regulatory compliance
- Training
- Minimal disruption

Expectation management is one of the central responsibilities of stakeholder management.

Unmanaged expectations can become:

- Conflicts
- Complaints
- Scope problems
- Delays
- Escalations
- Trust problems
- Commercial disputes

## Expectations versus requirements

A requirement is normally a defined need or condition that has been formally established as part of scope or another agreed specification.

An expectation can exist without being formally agreed.

For example:

A requirement may state that a system must support 1,000 concurrent users.

A stakeholder may expect the system to feel instant under all circumstances.

The second statement may be reasonable, but it requires clarification and measurable definition before it should be treated as an implementation commitment.

Effective stakeholder management makes assumptions visible.

## Expectation feasibility

The script evaluates expectations using:

- Importance
- Feasibility

Four broad outcomes are demonstrated:

| Importance | Feasibility | Response |
|---|---|---|
| High | High | Priority commitment |
| High | Low | Negotiate or reset expectations |
| Low | High | Optional improvement |
| Low | Low | Deprioritise |

This approach prevents teams from automatically promising every stakeholder request.

## Communication management

Communication is not simply the act of sending information.

Effective stakeholder communication should consider:

- Who needs the information
- Why the information is needed
- What the stakeholder needs to know
- What decision is required
- What action is expected
- Who owns the action
- When the action is due
- What evidence supports the message
- Which channel is appropriate
- How frequently communication should occur

The script models communication planning through structured communication-plan objects.

## Communication plan

A communication plan can specify:

- Stakeholder
- Purpose
- Information
- Channel
- Frequency
- Owner
- Escalation trigger

Example purposes include:

- Executive visibility
- Coordination
- Expectation alignment
- Compliance
- Decision making
- Risk communication

The communication plan should be proportional to stakeholder importance and information needs.

## Communication channels

Different channels serve different purposes.

### Email

Useful for:

- Written records
- Routine updates
- Formal confirmations
- Distribution of documents

### Meetings

Useful for:

- Complex issues
- Conflict resolution
- Negotiation
- Strategic decisions
- Ambiguous requirements

### Dashboards

Useful for:

- Performance metrics
- Status
- Risks
- Trends
- Executive visibility

### Collaboration platforms

Useful for:

- Operational coordination
- Tasks
- Discussions
- Documentation

### Formal reports

Useful for:

- Regulatory communication
- Contractual reporting
- Governance
- Auditable records

The script demonstrates channel selection based on sensitivity, complexity, urgency, and stakeholder preference.

## Communication quality

Communication volume is not the same as communication effectiveness.

A stakeholder can receive many messages while still lacking:

- Understanding
- Context
- Decision clarity
- Action ownership
- Evidence
- Timing information

The script therefore measures communication effectiveness using:

- Message delivery
- Understanding
- Action completion

The important principle is that communication should be evaluated by outcomes rather than message count alone.

## Structured stakeholder communication

The script represents an important communication as:

- Stakeholder
- Objective
- Key message
- Evidence
- Decision required
- Action owner
- Deadline

This structure reduces ambiguity.

For example, a message that merely says a project is delayed is weaker than a message explaining:

- What changed
- Why it changed
- Evidence supporting the assessment
- Consequences
- Proposed response
- Decision required
- Decision owner
- Deadline

## Communication cadence

Communication cadence is the planned frequency of stakeholder interaction.

Examples include:

- Daily
- Weekly
- Biweekly
- Monthly
- Milestone-based
- Event-driven

Cadence should be adjusted based on stakeholder needs and project conditions.

High-risk periods may require more frequent communication than stable periods.

A fixed cadence should not prevent event-driven communication when an important issue occurs.

## Engagement

Stakeholder engagement describes the quality and level of the relationship between the stakeholder and the project.

The script uses five engagement states:

- Unaware
- Resistant
- Neutral
- Supportive
- Leading

The current state can be compared with a desired state.

This creates an engagement gap.

For example:

`Neutral → Supportive`

indicates that the stakeholder requires targeted engagement to move toward active support.

## Engagement strategy

Engagement strategy should consider:

- Influence
- Interest
- Current engagement
- Desired engagement
- Expectations
- Concerns
- Communication preferences
- Organizational context

The same communication approach should not be applied to an executive sponsor, technical specialist, customer, regulator, and local community.

## RACI

RACI is a responsibility-assignment framework.

The four roles are:

### Responsible

The person or group performing the work.

### Accountable

The person who owns the final outcome or decision.

### Consulted

People whose input is required before completing the activity.

### Informed

People who need to know the outcome or status.

The script validates that a RACI assignment has exactly one accountable party.

RACI can reduce ambiguity around ownership, although organizations may adapt the framework to their governance model.

## Decision rights

Stakeholder management becomes stronger when decision rights are explicit.

A decision record can identify:

- Decision
- Decision owner
- Consulted stakeholders
- Informed stakeholders
- Deadline

Decision rights prevent situations where several stakeholders believe another person is responsible for the final decision.

## Conflict management

Stakeholder conflict is normal because stakeholders may have different:

- Goals
- Incentives
- Constraints
- Timelines
- Budgets
- Risk tolerances
- Success criteria
- Organizational responsibilities

The objective is not necessarily to eliminate disagreement.

The objective is to manage disagreement constructively and reach an appropriate decision.

## Conflict styles

The script demonstrates five common conflict-handling approaches:

- Avoid
- Accommodate
- Compromise
- Compete
- Collaborate

### Avoid

The issue is temporarily or deliberately not confronted.

This can be appropriate for low-importance issues but dangerous when the underlying issue is significant.

### Accommodate

One party gives greater weight to the other party's interests.

This can protect relationships when the issue has relatively low importance to the accommodating party.

### Compromise

Each party gives up something.

This can provide a practical middle ground but may produce a solution that is acceptable rather than optimal.

### Compete

A decision is imposed or strongly advocated.

This may be appropriate for urgent situations or when a clear authority must make a decision.

### Collaborate

The parties examine underlying interests and seek a solution satisfying important interests on both sides.

Collaboration is particularly valuable when both the issue and relationship are highly important.

## Position versus interest

A stakeholder's stated position is not always the same as the underlying interest.

For example:

Position:

"Deliver by 30 June."

Underlying interests:

- Market timing
- Predictability
- Quality
- Commercial commitments

Another stakeholder might state:

"Delivery must be 15 July."

Underlying interests might include:

- Quality
- Manageable workload
- Technical stability
- Predictability

Once underlying interests are visible, negotiation can become more productive.

## Negotiation

Effective stakeholder negotiation should distinguish:

- Stated positions
- Underlying interests
- Minimum acceptable outcomes
- Preferred outcomes
- Constraints
- Shared interests

The script compares stakeholder interests to identify areas of overlap.

Shared interests can provide the foundation for mutually acceptable solutions.

## Stakeholder risks

Stakeholder risks can be managed as part of the broader project risk system.

Examples include:

- Loss of customer confidence
- Executive dissatisfaction
- Resistance to change
- Regulatory concerns
- Supplier disagreement
- Community opposition
- Unclear ownership
- Poor communication
- Unrealistic expectations

The script uses:

`probability × impact`

to calculate a basic risk score.

This is a common risk-analysis technique, although real organizations may use more sophisticated scoring models.

## Stakeholder risk responses

Typical response approaches include:

- Mitigation
- Avoidance
- Transfer
- Acceptance
- Escalation
- Monitoring

The correct response depends on the type of risk, organizational authority, timing, cost, and consequences.

## Change management

Changes can alter stakeholder interests, influence, expectations, risks, and communication requirements.

A change request may affect:

- Scope
- Cost
- Schedule
- Quality
- Resources
- Operations
- Customers
- Suppliers
- Regulators

The script demonstrates a change prioritisation model using:

- Expected benefit
- Disruption
- Urgency

The calculation is intentionally transparent rather than presented as a universal formula.

## Stakeholder sentiment

Stakeholder sentiment can provide an early warning signal.

Possible categories include:

- Negative
- Neutral
- Positive

Sentiment should not be treated as an objective measurement of stakeholder truth. It is an indicator that should be interpreted using evidence.

The script associates sentiment with:

- Stakeholder
- Sentiment
- Confidence
- Evidence

Evidence is important because subjective assumptions about stakeholder attitudes can create management errors.

## Feedback loops

Stakeholder management should contain a feedback loop:

1. Communicate
2. Receive feedback
3. Analyse feedback
4. Identify problems
5. Take corrective action
6. Communicate the response
7. Measure the result

The script implements a `FeedbackLoop` class that stores feedback, calculates average ratings, identifies low-rated topics, and groups feedback by stakeholder.

A feedback process is incomplete if stakeholders provide concerns but never see what happened afterward.

## Stakeholder relationship networks

Stakeholders do not operate independently.

They form networks of:

- Influence
- Communication
- Dependency
- Escalation
- Information flow
- Decision making

The script represents stakeholder relationships as a directed graph.

For example:

`Regulator → Compliance Lead → Project Manager → Project Team`

This represents an information or influence path.

## Network centrality

A stakeholder with many incoming relationships may occupy an important position in the stakeholder network.

The script uses a simple inbound relationship count as an approximation of centrality.

More advanced network analysis can use:

- Degree centrality
- Betweenness centrality
- Closeness centrality
- Eigenvector centrality

These measures can identify stakeholders who are highly connected or who act as bridges between otherwise separate groups.

## Dynamic stakeholder analysis

Stakeholder analysis is not a one-time activity.

A stakeholder can move between categories because of:

- Organizational restructuring
- Leadership changes
- New regulations
- Scope changes
- Project delays
- Customer complaints
- Budget changes
- Market changes
- New dependencies
- Business priorities

The script includes stakeholder snapshots across different periods to track changes in influence, interest, and sentiment.

## Escalation

Escalation should be governed by explicit thresholds rather than personal preference alone.

Possible escalation triggers include:

- Critical severity
- Significant schedule variance
- Budget variance
- Regulatory breach
- Customer dissatisfaction
- Unresolved issue duration
- Decision deadlock
- Contractual risk

The script defines escalation rules using severity and unresolved duration.

Escalation should normally include:

- Issue description
- Evidence
- Business impact
- Stakeholders affected
- Actions already attempted
- Decision required
- Recommended owner
- Required timing

## Governance

Stakeholder governance establishes structure around:

- Decision rights
- Accountability
- Escalation
- Documentation
- Compliance
- Review frequency
- Conflict management

Good governance does not mean every decision requires senior approval. It means the organization knows who is authorized to make which decisions.

## Security and confidentiality

Stakeholder information can contain sensitive data.

Potentially sensitive information includes:

- Personal contact information
- Complaints
- Performance concerns
- Negotiation positions
- Commercial information
- Regulatory information
- Internal disagreements
- Confidential project risks

Important principles include:

### Need-to-know access

Information should be accessible only to people who require it for legitimate work.

### Data minimisation

Collect and retain only information relevant to the management purpose.

### Access control

Sensitive stakeholder records should have appropriate permissions.

### Confidentiality

Sensitive complaints and personal concerns should not be distributed unnecessarily.

### Auditability

Important decisions and approvals should be traceable.

### Privacy

Personal information should be handled according to applicable privacy requirements and organizational policy.

## Edge cases

Stakeholder models can fail when treated too mechanically.

### High interest and low formal power

A stakeholder may have limited formal authority but strong interest.

Such stakeholders may possess valuable operational knowledge or represent affected users.

They should not be ignored.

### High power and low interest

A senior executive may have considerable authority but little interest in operational detail.

The appropriate strategy is usually to maintain confidence and provide concise, decision-relevant information.

### Changing stakeholder position

A stakeholder's influence or interest can change.

The stakeholder register should therefore be periodically reviewed.

### Conflicting expectations

Two high-priority stakeholders may request mutually incompatible outcomes.

The solution is not to promise both. The conflict must be made explicit and resolved through prioritisation, negotiation, governance, or escalation.

### Low-power stakeholders

Low-power stakeholders may still possess legitimacy, expertise, local knowledge, or reputational significance.

Power should therefore never be used as the only stakeholder criterion.

## Common mistakes

### Identifying stakeholders only once

Projects evolve, and stakeholders can change.

### Treating all stakeholders identically

Different stakeholders have different needs and communication preferences.

### Confusing communication volume with communication effectiveness

Sending more messages does not necessarily improve understanding.

### Ignoring low-power stakeholders

Low formal power does not mean zero relevance.

### Overpromising

Promises made without feasibility analysis create future trust and delivery problems.

### Failing to document decisions

Undocumented decisions can lead to different interpretations.

### Using excessive technical language

Communication should match the stakeholder's knowledge and decision requirements.

### Escalating too late

Waiting until an issue becomes critical can reduce the available response options.

## Performance considerations

Basic stakeholder operations are generally efficient.

A simple scan through a stakeholder list is:

`O(n)`

Sorting stakeholders by priority is typically:

`O(n log n)`

A naive comparison of every stakeholder with every other stakeholder is:

`O(n²)`

For a large organization, unnecessary pairwise analysis can become expensive.

The script demonstrates the growth of possible stakeholder pairs using:

`n × (n - 1) / 2`

For example, 1,000 stakeholders produce 499,500 possible unordered pairs.

Production systems should therefore avoid unnecessary all-pairs operations and use appropriate indexing, filtering, graph structures, and database queries.

## Implementation considerations

A production stakeholder management system would normally separate:

- Data storage
- Business rules
- User interface
- Authentication
- Authorization
- Audit logging
- Reporting
- Notification
- Workflow
- Analytics

The Python script keeps everything together because its purpose is educational and executable demonstration.

A production implementation should normally store stakeholder data in a persistent database rather than relying on in-memory objects.

Important production capabilities can include:

- Version history
- Role-based permissions
- Audit trails
- Stakeholder ownership
- Change history
- Communication logs
- Risk linkage
- Decision records
- Approval workflows
- Search and filtering
- Reporting
- Notification rules

## Validation

The script demonstrates validation for:

- Stakeholder names
- Roles
- Numeric scores
- Communication plan fields
- Expectations
- Risk probabilities
- Risk impacts
- Feedback ratings
- RACI assignments
- Decision ownership
- Communication cadence
- Weight totals

Validation is important because poor stakeholder data can lead to poor prioritisation.

For example, a stakeholder influence score outside the expected 1-5 range could distort every downstream calculation.

## Testing

The script contains executable assertions that test:

- Power-interest classification
- Score normalization
- Risk calculations
- Feedback calculations
- Stakeholder network paths
- RACI validation
- Stakeholder validation

Automated tests are valuable because stakeholder management systems can contain many business rules.

A change to one classification rule should not silently break another part of the analysis.

## Practical stakeholder management workflow

A structured stakeholder management process can be represented as:

1. Identify stakeholders.
2. Classify internal and external stakeholders.
3. Record roles and relationships.
4. Assess influence.
5. Assess interest.
6. Assess impact.
7. Consider urgency, legitimacy, and proximity where relevant.
8. Map stakeholders.
9. Record expectations.
10. Record concerns.
11. Identify conflicting expectations.
12. Determine desired engagement.
13. Design communication plans.
14. Assign communication owners.
15. Define decision rights.
16. Establish escalation thresholds.
17. Track stakeholder-related risks.
18. Collect feedback.
19. Monitor sentiment and engagement.
20. Review stakeholder changes.
21. Update the stakeholder register.
22. Close feedback loops.
23. Document important decisions.

The cycle should be repeated throughout the lifecycle because stakeholder conditions are dynamic.

## Real-world applications

Stakeholder management applies across many environments.

### Project management

Stakeholder management supports:

- Scope alignment
- Decision making
- Risk management
- Executive reporting
- Customer communication
- Change control

### Product management

Stakeholders can include:

- Customers
- Product managers
- Engineering teams
- Sales
- Marketing
- Legal
- Finance
- Executives

Stakeholder management helps align product decisions with organizational and customer needs.

### Business transformation

Transformation programs frequently involve:

- Employees
- Leadership
- Customers
- Technology teams
- Vendors
- Regulators

Resistance and unclear expectations can become major transformation risks.

### Software implementation

Implementation projects commonly involve:

- Business users
- Technical teams
- Vendors
- Project sponsors
- Customers
- Security teams
- Compliance teams

Different groups need different communication and engagement strategies.

### Regulatory projects

Regulated environments place greater emphasis on:

- Documentation
- Compliance evidence
- Formal communication
- Decision traceability
- Escalation
- Accountability

### Infrastructure projects

Infrastructure projects may involve:

- Government authorities
- Contractors
- Local communities
- Customers
- Suppliers
- Environmental organizations
- Internal operations teams

The stakeholder map can therefore extend well beyond the project organization.

## Important distinctions

### Influence versus interest

Influence is the ability to affect the project.

Interest is the degree of concern or involvement.

A stakeholder can be high in one and low in the other.

### Influence versus impact

Influence concerns the stakeholder's ability to affect outcomes.

Impact concerns how strongly the stakeholder or its environment is affected.

### Requirement versus expectation

A requirement is formally established.

An expectation may be assumed and therefore needs clarification.

### Communication versus engagement

Communication is the exchange of information.

Engagement is the broader relationship and participation process.

Communication supports engagement but does not automatically create it.

### Responsibility versus accountability

Responsibility concerns performing work.

Accountability concerns ownership of the outcome.

### Position versus interest

A position is what a stakeholder says it wants.

An interest explains why the stakeholder wants it.

Understanding interests can make negotiation more productive.

## Quantitative models and their limitations

Quantitative stakeholder models are useful because they make assumptions visible.

They are not perfect representations of organizational reality.

A score can simplify complex human behavior.

Potential limitations include:

- Subjective scoring
- Incomplete information
- Political behavior
- Hidden influence
- Changing relationships
- Cultural differences
- Organizational dynamics
- Conflicting objectives

For this reason, numerical analysis should support professional judgment rather than replace it.

A stakeholder with an influence score of 3 is not automatically less important than one with a score of 4. The context behind the score matters.

## Best practices

Effective stakeholder management should:

- Identify stakeholders early.
- Reassess stakeholders throughout the lifecycle.
- Distinguish internal and external relationships.
- Assess influence and interest separately.
- Consider impact and urgency.
- Record stakeholder expectations.
- Make assumptions explicit.
- Avoid unrealistic commitments.
- Tailor communication to the audience.
- Use appropriate communication channels.
- Define communication ownership.
- Clarify decision rights.
- Document important decisions.
- Monitor stakeholder sentiment.
- Track stakeholder risks.
- Define escalation criteria.
- Close feedback loops.
- Protect sensitive information.
- Review stakeholder maps when circumstances change.
- Use quantitative scores as decision aids rather than absolute truth.

## Structure represented in the Python script

The script progresses through:

- Fundamental terminology
- Internal and external stakeholder classification
- Stakeholder registers
- Stakeholder identification
- Power-interest mapping
- Influence-impact analysis
- Stakeholder salience
- Weighted prioritisation
- Expectation analysis
- Requirement versus expectation
- Communication planning
- Communication channel selection
- Communication quality
- RACI
- Engagement states
- Engagement strategies
- Conflict management
- Conflict resolution
- Negotiation
- Stakeholder risks
- Change management
- Sentiment analysis
- Feedback loops
- Stakeholder networks
- Centrality
- Dynamic stakeholder trends
- Escalation
- Decision rights
- Meeting design
- Communication cadence
- Common mistakes
- Edge cases
- Validation
- Performance considerations
- Security and confidentiality
- Governance
- Production-oriented design
- End-to-end stakeholder management
- Automated testing
- Operational checklists

The examples are implemented as executable Python structures, functions, classes, calculations, validations, simulations, and assertions so that the concepts can be studied through both definitions and working logic.
