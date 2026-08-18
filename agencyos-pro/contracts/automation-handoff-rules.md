# Automation Handoff Rules

Default posture:

```text
Known handoffs run automatically.
The human owns authority.
The Orchestrator owns routing.
Agencies own outputs.
Governance owns checks.
InnerLight owns reasoning coherence.
```

The workflow should pause only when the next step requires human judgment, approval, missing source input, risk tolerance, budget, legal review, public claim approval, or resolution of conflicting agency outputs.

## Orchestrator Responsibilities

```text
Start parallel agencies when the route is known.
Run an InnerLight signal check before routing ambiguous, high-pressure, or conflict-heavy work.
Package prior outputs into the next agency prompt.
Attach evidence, assumptions, constraints, and approval gates.
Check each output against the definition of done.
Route clean outputs to the next owner.
Ask the human only at a declared human gate.
```

## Agency Responsibilities

```text
Accept the routed input.
Produce the declared output.
Declare assumptions.
Flag missing inputs.
Flag risk or approval blockers.
Avoid asking the human to trigger a known next step.
```

## Human Gates

```text
Goal approval
Decision rights
Risk tolerance
Brand or claim approval
Budget or resource commitment
Legal, privacy, or compliance review
Pilot scope
Launch approval
Conflicting recommendations
Continue, revise, or stop decisions
```

## Handoff Packet Fields

```text
Trigger:
Source agency:
Destination agency or agencies:
InnerLight signal:
Inputs attached:
Output expected:
Evidence attached:
Assumptions:
Tool access:
Permissions:
Human gate:
Pause condition:
Auto-next:
Definition of done:
```

## Parallel Fanout Rule

```text
If multiple agencies can work from the same approved input without waiting on each other, the Orchestrator starts them in parallel.
Each agency returns structured output to the Orchestrator.
The Orchestrator merges outputs, resolves conflicts, and routes the next batch.
```
