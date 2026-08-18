# AgencyOS Pro Agents

Purpose:

```text
Make AgencyOS Pro agents available to AgencyOS Being Core as installable Skills.
```

Source:

```text
C:\Users\felix\Desktop\agencyos-pro
```

AgencyOS Pro agents are treated as Skills inside the AI Being anatomy.

```text
Skills = agent prompts, role prompts, workflow prompts, tool routines, and capability prompts.
```

## Core Operating Agents

| Skill | Source Role | Purpose |
| --- | --- | --- |
| Parent Orchestrator | Operator | Routes work across agencies, resolves ambiguity, starts automation, and pauses at human gates. |
| Central Orchestrator | Scenario operator | Converts a brief into a routed work plan with agencies, handoffs, evidence, and approvals. |
| Config Selector | Configuration | Chooses the operating pattern based on failure mode and work shape. |
| Agency Selector | Routing | Selects which agencies should own the work. |
| Scope Gate | Governance | Defines what is in, out, urgent, paused, or complete. |
| Risk Gate | Governance | Determines risk level and required controls. |
| Truth Agent | Verification | Verifies artifacts, evidence, owners, and closeout labels before closure. |

## Coordinator Skills

| Skill | Purpose |
| --- | --- |
| Research Coordinator | Routes market, source, and context discovery. |
| Engineering Coordinator | Routes architecture, build, code, QA, and technical proof. |
| Growth Coordinator | Routes positioning, content, outreach, launch, and sales enablement. |
| Operations Coordinator | Routes delivery, process, tooling, data, performance, and fulfillment. |
| Insights Coordinator | Routes analytics, experiments, customer insight, and strategy learning. |

## Specialist Skills

Research:

```text
Market Intelligence
Research Analyst
Idea Generator
Knowledge Librarian
```

Engineering:

```text
Architect
UX Designer
Code Developer
QA / Testing
```

Growth:

```text
Marketing Strategy
Content Creation
Sales Enablement
Community Manager
```

Operations:

```text
DevOps
Data Pipeline
Security
Performance Optimization
```

Insights:

```text
Analytics
Experimentation
Customer Insight
Strategy Advisor
```

Governance:

```text
Policy
Risk Assessment
Ethics Review
Audit
Truth Agent
```

## Scenario Agency Skills

FluidLogic market transition:

```text
Research Agency
Strategy and Positioning Agency
Offer and Pilot Design Agency
Sales Enablement Agency
Content Studio Agency
Launch Agency
Risk and Proof Agency
Insights Agency
```

Unemployed developer / beginner voice-over / AI builder:

```text
Income Triage Agency
Market Signal Agency
Builder Portfolio Agency
Voice-Over Samples Agency
Outreach and Applications Agency
Delivery Operations Agency
Risk and Proof Agency
Insights Agency
```

## Installation Rule

Install an AgencyOS Pro agent as a Skill only when:

```text
the work repeats
the ownership is clear
the input packet is known
the output packet is known
the evidence requirement is known
the human gate is known
```

Skill install packet:

```text
Skill name:
Source agent:
Purpose:
Inputs:
Outputs:
Allowed tools:
Permissions:
Evidence required:
Human gates:
Definition of done:
Closeout label:
```

## Boundary

```text
AgencyOS Pro agents can become Skills.
Skills do not bypass Skeleton, Governance, Presence, or human authority.
```

