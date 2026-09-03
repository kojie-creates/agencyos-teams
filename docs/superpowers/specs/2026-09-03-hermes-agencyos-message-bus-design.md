# Hermes AgencyOS Message Bus Design

## Classification

This is an architectural design for turning Hermes from a chat-loop coordinator into an async packet router for AgencyOS Teams.

The goal is not to prove live production readiness. The first milestone should prove local packet creation, durable bus notification, worker claim, handoff completion, and next-agent notification under controlled conditions.

## Goal

Allow a user to issue work through one surface while Hermes creates AgencyOS Teams handoff packets, routes them to the right bot or harness, and notifies the next bot when a packet is ready.

The system must preserve AgencyOS Teams as the work authority. Chat platforms, bot rooms, and model harnesses are communication surfaces or workers, not the source of truth.

## Current Problem

Hermes bots can message each other and work as expected when they stay active long enough.

The workflow is slow because the local model pool is constrained even with three available models: Qwen, Gemma 4, and Bonsai. Bots can time out while waiting for each other in a live chat-style loop.

The fix is to move from synchronous bot conversation to asynchronous packet work. A bot should not need another bot to be online at the same moment. It should claim durable work, complete it, write evidence, and emit a next-agent notification.

## Recommended Architecture

Use three layers:

1. AgencyOS Teams packet store as authority.
2. NATS JetStream as durable notification and work queue.
3. Hermes plus model-specific workers as adapters.

```text
User surface
  -> Hermes router
  -> AgencyOS Teams packet file
  -> NATS JetStream packet event
  -> target bot worker
  -> response and evidence files
  -> handoff packet update
  -> NATS JetStream next-agent event
  -> next bot worker
```

The bus carries packet availability and lifecycle events. The full packet, evidence, status, and closeout remain in AgencyOS Teams files.

## Component Boundaries

### Hermes Router

Hermes receives user work, resolves the first target bot, creates or updates an AgencyOS handoff packet, and publishes the first bus event.

Hermes may route and summarize. Hermes should not perform specialist work that belongs to Codex, Gemma, Qwen, or another named bot.

### AgencyOS Teams Packet Store

AgencyOS Teams owns packet truth:

- packet id
- origin
- assigned bot
- next bot
- scope
- task
- required outputs
- evidence paths
- status
- handoff notes
- approval state
- packet hash

The packet store can remain file-backed in v0.1. NATS should not replace the ledger in the first milestone.

### NATS JetStream

JetStream handles durable work notifications, retry, and replay.

Each bot receives work through a durable consumer. If a bot is offline, the event remains available. If a bot times out, the packet can move to `BLOCKED` or be retried without losing the handoff.

### Bot Workers

Each bot worker subscribes to its own ready subject, claims packets assigned to it, invokes the correct harness or local model, writes its response, updates packet status, and publishes the next event.

Workers should be narrow:

- `codex-worker`: repository execution, verification, artifacts.
- `gemma-worker`: reasoning, governance, scope, claim review.
- `qwen-worker`: triage, summary, low-cost preparation.
- `bonsai-worker`: third local model lane for configurable helper work, overflow, or future specialist routing.
- future workers: additional Hermes bots or specialist Beings.

### Human Approval Gate

Any external action or high-impact action must stop at `HUMAN_APPROVAL_REQUIRED`.

The packet may be prepared by a worker, but app actions, public messages, deletions, credential changes, deployments, and irreversible operations require explicit human approval.

## Packet Lifecycle

Use these states:

```text
CREATED
ROUTED
CLAIMED
IN_PROGRESS
HANDOFF_READY
COMPLETED
BLOCKED
HUMAN_APPROVAL_REQUIRED
FAILED
```

State rules:

- `CREATED`: Hermes wrote the packet.
- `ROUTED`: Hermes selected the assigned bot and bus subject.
- `CLAIMED`: a worker accepted responsibility.
- `IN_PROGRESS`: harness call or local work started.
- `HANDOFF_READY`: current worker finished and named the next bot.
- `COMPLETED`: no next bot remains and closeout evidence exists.
- `BLOCKED`: worker cannot continue, but packet is recoverable.
- `HUMAN_APPROVAL_REQUIRED`: work is waiting on user authority.
- `FAILED`: unrecoverable technical failure after configured retries.

## Bus Subjects

Use explicit subjects:

```text
agencyos.packet.created
agencyos.packet.ready.hermes
agencyos.packet.ready.codex
agencyos.packet.ready.gemma
agencyos.packet.ready.qwen
agencyos.packet.ready.bonsai
agencyos.packet.claimed
agencyos.packet.in_progress
agencyos.packet.handoff_ready
agencyos.packet.completed
agencyos.packet.blocked
agencyos.packet.needs_human
agencyos.packet.failed
```

Subject payloads should be small:

```json
{
  "packet_id": "PKT-20260903-0001",
  "status": "ROUTED",
  "assigned_to": "codex",
  "next_agent": "gemma",
  "packet_path": "projects/example/handoffs/PKT-20260903-0001.json",
  "event_id": "evt-...",
  "created_at": "2026-09-03T00:00:00Z"
}
```

The payload points to the authoritative packet. It should not carry the whole work context.

## Handoff Packet Shape

Minimum packet:

```json
{
  "packet_id": "PKT-20260903-0001",
  "created_at": "2026-09-03T00:00:00Z",
  "origin": "hermes",
  "assigned_to": "codex",
  "next_agent": "gemma",
  "workstream": "projects/example/workstreams/runtime",
  "task": "Implement the narrow change.",
  "scope": "Local controlled milestone.",
  "inputs": [],
  "required_outputs": [
    "code changes",
    "test evidence",
    "handoff notes"
  ],
  "evidence_paths": [],
  "status": "ROUTED",
  "approval_state": "HUMAN_AUTHORITY_RETAINED",
  "handoff_notes": "",
  "packet_hash": "sha256..."
}
```

## Timeout And Retry Behavior

Timeouts should produce packet state, not lost conversations.

Rules:

- If a worker does not claim within the claim timeout, Hermes republishes the ready event or routes to a fallback.
- If a worker claims but does not complete within the work timeout, the packet becomes `BLOCKED`.
- If the same packet blocks repeatedly, the packet becomes `HUMAN_APPROVAL_REQUIRED`.
- No bot should run an indefinite autonomous loop.
- Retry attempts should be recorded in the event ledger.

## First Milestone

Build `Hermes AgencyOS Packet Router v0.1`.

Scope:

- Keep AgencyOS Teams packet files as authority.
- Add a small NATS JetStream publisher and subscriber wrapper.
- Add Hermes route command that creates a packet and publishes `agencyos.packet.ready.<bot>`.
- Add one test worker for Codex.
- Add one simulated Gemma or Qwen worker.
- Prove handoff from one worker to the next.
- Prove timeout becomes `BLOCKED`.
- Prove human approval stops external action.

Out of scope:

- production deployment
- live external app actions
- cloud model fallback
- full UI
- autonomous multi-agent loops
- replacing AgencyOS Teams files with a database

## Verification Plan

Focused tests should cover:

- packet creation writes a file
- packet hash changes when packet content changes
- Hermes selects the correct subject for an assigned bot
- worker claim updates packet status to `CLAIMED`
- worker completion writes evidence paths
- handoff publishes the next-agent ready subject
- timeout writes `BLOCKED`
- approval-required action writes `HUMAN_APPROVAL_REQUIRED`

Manual smoke test:

```powershell
nats-server -js
python tools\hermes_router.py route --task "Create test packet" --to codex --next gemma
python tools\workers\codex_worker.py --once
python tools\workers\gemma_worker.py --once
```

Expected result:

```text
Hermes creates packet.
Codex worker claims and completes first handoff.
Gemma worker receives next packet notification.
AgencyOS packet shows evidence paths and final status.
```

## Evidence Boundaries

This milestone proves local async packet routing only.

It does not prove live production coordination, continuous availability, deployed bot operations, or real external app execution. Those require separate environment setup, credentials, service supervision, and live-run evidence.

## Open Decisions

1. First surface: Telegram, Zulip, Discord, local web UI, or direct CLI.
2. Worker location: inside `agencyos-teams`, inside `agencyos-bus-sidecar`, or split with sidecar owning bus code.
3. First live worker: Codex, Gemma, or Qwen.
4. Bonsai role: helper, overflow, specialist worker, or another named governance lane.
5. NATS installation method: local binary, Docker, or embedded developer runbook.

## Recommendation

Start inside the existing `agencyos-bus-sidecar`, because it already has packet files, response files, adapter boundaries, and tests.

Keep `agencyos-teams` as the authoritative project and handoff record. The sidecar should act as runtime transport and adapter layer.

The next implementation plan should add NATS-backed routing without removing the existing file-backed packet flow.
