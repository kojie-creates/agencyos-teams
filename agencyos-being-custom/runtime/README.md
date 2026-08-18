# Runtime

Purpose:

```text
Record AgencyOS activation, handoff, evidence, hash, and closeout events as runtime receipts.
```

Boundary:

```text
Runtime events describe what happened.
They do not grant authority.
They do not replace Kojie's approval.
They do not make a claim true without evidence.
```

## Event Log

Event logs are append-only JSONL files.

Each event should include:

```text
event_id
type
actor
phase
timestamp
artifact when relevant
sha256 when relevant
note when useful
```

Core event types:

```text
task_received
scope_gate_passed
risk_gate_passed
agent_activated
specialist_assigned
handoff_packet_created
deliverable_created
deliverable_hashed
evidence_attached
claim_verified
agent_muted
evidence_lock_passed
decision_packet_created
kojie_approved
task_closed
```

## State Rule

```text
agent_activated -> ACTIVE
agent_muted -> MUTED
```

Agents return to muted after their handoff packet is complete unless a later gate reactivates them.

## Evidence Lock Rule

```text
Every final deliverable must have:
hash
evidence record
claim verification
```

No final decision packet is complete until Evidence Lock passes.

## Capability Registry

```text
runtime/active-capabilities.json
```

The capability registry separates the broad capability surface into explicit states:

```text
available
installed
active
blocked
requires_approval
deprecated
```

Rule:

```text
Available does not mean active.
Installed does not mean permitted.
Requires approval cannot activate without Kojie's approval.
Blocked cannot run until the blocking condition is removed.
Deprecated should not be used for new work.
```

The current summary can be generated with:

```text
python tools/summarize_capabilities.py runtime/active-capabilities.json
```
