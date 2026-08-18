# Scaffold From Intake

Use completed intake form to create project structure.

## Minimal Scaffold

For one task:

```text
agency/queue.md
agency/draft/
agency/final/
contracts/definition-of-done-registry.md
```

## Standard Scaffold

For one project:

```text
agency/queue.md
agency/draft/
agency/final/
agency/handoffs/
agency/decisions/decision-log.md
contracts/handoff-packet.md
contracts/definition-of-done-registry.md
```

## Network Scaffold

For multiple agencies:

```text
agencies/<agency-name>/charter.md
agencies/<agency-name>/queue.md
agencies/<agency-name>/private-memory.md
agency/decisions/decision-log.md
agency/handoffs/
contracts/reconciliation-packet.md
memory/memory-boundary-rules.md
```

## Governance Scaffold

For Standard, Strict, or Critical governance:

```text
governance/risk-gate.md
agency/evidence/evidence-ledger.md
agency/reviews/periodic-review-log.md
contracts/monitor-review-closeout.md
contracts/failure-packet.md
```

## Continuous Improvement Scaffold

For monitor or periodic review:

```text
agency/retrospectives/continuous-improvement.md
agency/reviews/periodic-review-log.md
memory/lesson-memory.md
```

## Scaffold Decision Logic

```text
If scope = one task:
  create Minimal Scaffold.

If scope = one project:
  create Standard Scaffold.

If scope = multiple projects or ongoing operating system:
  create Network Scaffold.

If governance standard = Standard, Strict, or Critical:
  add Governance Scaffold.

If closeout path = Monitor or Periodic Review:
  add Continuous Improvement Scaffold.

If primary failure = Context bleed:
  require agency charters and memory boundaries.

If primary failure = Unsupported claims:
  require evidence ledger and Offer <-> Proof binary.

If primary failure = False closure:
  require Truth Agent verification.

If primary failure = No decision owner:
  require human decision owner.
```
