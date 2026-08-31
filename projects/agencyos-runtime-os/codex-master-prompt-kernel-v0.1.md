# Codex Master Prompt: AgencyOS Runtime Kernel v0.1

## Mission

Implement the first defensible AgencyOS Runtime Kernel milestone. The goal is to move AgencyOS from a coordinating operating layer toward a governed runtime that work must run through.

Do not claim production readiness. Do not claim autonomous self-governance. Human authority remains the final approval boundary.

## Strategic Boundary

Bionic can define operating cadence and prioritization.

Codex implements code, tests, repository changes, and verification.

AnythingLLM, Hermes, Gmail, Slack, browser tools, and local apps are future or optional drivers. They must not bypass AgencyOS authority.

AgencyOS Teams remains the governance, sequencing, evidence, handoff, and closeout framework.

## Kernel Definition

The kernel is the canonical runtime authority engine. It decides whether an action may proceed, whether it must be blocked, whether human approval is required, and what evidence must be written.

All governed actions should follow this shape:

```text
request
-> authority check
-> scoped grant or denial
-> adapter execution
-> evidence receipt
-> state transition
-> closeout or escalation
```

## First Prototype Milestone

Build `AgencyOS Runtime Kernel v0.1` with exactly one narrow end-to-end path:

```text
one task
one policy check
one approved tool request
one Codex driver action
one artifact write
one event ledger entry
one blocked/recovery path
one closeout receipt
```

## Required Modules

Create or extend modules only after inspecting the existing repository shape.

Candidate boundaries:

- `runtime_kernel`
- `policy_gate`
- `process_registry`
- `scheduler`
- `system_calls`
- `driver_registry`
- `event_ledger`
- `artifact_store`
- `approval_gate`
- `closeout_service`

Use existing `src/platform_governance` components where present instead of duplicating authority logic.

## Required System Calls

Implement the smallest useful subset first:

```text
aos.create_task()
aos.read_context()
aos.request_tool()
aos.write_artifact()
aos.log_event()
aos.request_approval()
aos.closeout()
```

If the current codebase uses a different language or naming convention, adapt these as local equivalents while preserving the same contract.

## Process Model

Represent workflows, agents, tasks, and tickets as managed processes with:

- process id
- process type
- owner
- project/workstream scope
- status
- requested capability
- permission result
- evidence references
- created and updated timestamps

Minimum lifecycle:

```text
pending -> approved -> running -> blocked -> complete -> archived
```

Not every transition must be reachable in the first implementation, but blocked, approved, running, complete, and closeout behavior must be tested.

## Policy Requirements

At minimum, policy must detect:

- missing authority
- disallowed capability
- high-risk action requiring human approval
- invalid or missing credential scope
- unsafe external action

Policy results should be explicit:

```text
PASS
FLAGGED
FAIL
```

`FLAGGED` and `FAIL` must halt downstream execution until resolved.

## Evidence Requirements

Every governed action must produce a receipt with:

- request id
- process id
- actor
- requested capability
- policy result
- adapter or driver used
- artifact references
- state transition
- timestamp
- hash-backed manifest reference where applicable

Use tamper-evident, hash-backed language only. Do not call the ledger immutable unless the implementation proves immutability.

## TDD Path

Work policy-first:

1. Inspect current files.
2. Add focused tests for the kernel path.
3. Confirm expected failing tests.
4. Implement minimal code.
5. Run focused tests.
6. Run relevant broader suite.
7. Capture command evidence.
8. Update AgencyOS project evidence.

## Acceptance Criteria

- A task can be created through the runtime.
- A governed action is denied when policy fails.
- A governed action is halted when human approval is required.
- An approved action can call a stub Codex driver.
- The driver writes or references an artifact.
- An event ledger entry is written.
- A closeout receipt is produced.
- Tests prove the happy path and at least one blocked path.
- Documentation states what is proven, simulated, and not claimed.

## Not Yet Claimed

- Production governance.
- Live external integrations.
- Live Hermes integration.
- Live AnythingLLM integration.
- Live Bionic scheduler integration.
- Multi-user administration.
- Full auth system.
- Durable Postgres persistence.
- Deployed API.
- Hardware operating system status.

## Final Deliverable

Return:

- files changed
- tests run
- exact pass/fail evidence
- known simulation boundaries
- next implementation milestone

Do not finish with broad claims. Finish with evidence.
