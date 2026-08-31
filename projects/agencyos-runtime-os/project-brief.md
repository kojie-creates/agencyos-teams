# AgencyOS Runtime OS Brief

## Project Name

AgencyOS Runtime OS

## Owner

Kojie

## Goal

Convert AgencyOS from an operating layer for AI-assisted work into a runtime that work runs on. The target is not a hardware operating system. The target is an agentic work operating system that owns execution state, permissions, lifecycle, recovery, and APIs for governed human-AI work.

## Core Shift

```text
Operating layer = coordinates work
Operating system = owns execution state, permissions, lifecycle, recovery, and APIs
```

AgencyOS becomes more than a framework when agents, tools, workflows, memory, and artifacts must request authority through it before acting.

## Minimum Credible OS Threshold

| Requirement | AgencyOS Version |
| ----------- | ---------------- |
| Kernel | PolicyGate / OBEXGATE-style authority engine |
| Process model | Workflows, agents, tasks, tickets as managed processes |
| Scheduler | Bionic cadence, priority queue, deadlines, retries |
| System calls | Standard APIs for tools, memory, files, agents, approvals |
| Permissions | Human gates, role scopes, credential scopes |
| File system | Artifacts, evidence, manifests, project state |
| Drivers | Codex, AnythingLLM, Hermes, Gmail, Slack, browser, local apps |
| Shell | Desktop app, CLI, chat interface |
| Services | Memory, routing, logging, notifications, recovery |
| Package system | Skills, Beings, templates, connectors |
| Observability | Event log, receipts, dashboards, audit exports |
| Recovery | Rollback, pause, quarantine, re-run, closeout |

## Runtime Principle

```text
Agent wants to act
-> AgencyOS checks authority
-> AgencyOS grants scoped capability
-> action runs through adapter
-> result writes evidence
-> state updates
-> human gate closes or escalates
```

## Roadmap

### 1. Define AgencyOS Kernel

Create one canonical policy/runtime engine. All governed actions pass through it before tool use, memory writes, workflow transitions, external calls, or closeout.

### 2. Create AOS System Calls

Define stable runtime APIs:

```text
aos.create_task()
aos.read_context()
aos.request_tool()
aos.write_artifact()
aos.log_event()
aos.request_approval()
aos.closeout()
```

These calls become the contract between agents, shells, services, and drivers.

### 3. Make Agents Into Processes

Hermes, Codex, Bionic, AnythingLLM, and other agents become managed processes with:

- process identity
- scoped permissions
- project/workstream context
- runtime state
- receipt output
- pause/block/closeout behavior

### 4. Add A Real Scheduler

Move beyond Morning Brief into a real execution queue:

```text
pending -> approved -> running -> blocked -> complete -> archived
```

The scheduler should support Bionic cadence, priorities, deadlines, retries, owner assignment, and blocked-state recovery.

### 5. Add Driver And Adapter Layer

Create adapters for controlled execution:

- Codex driver
- AnythingLLM driver
- Hermes driver
- browser driver
- Gmail driver
- Slack driver
- local filesystem driver

Drivers should expose capabilities through AgencyOS system calls, not direct unrestricted agent access.

### 6. Add Persistent State

Use SQLite first, with Postgres later when multi-user or server deployment is justified. Every workflow, permission, event, artifact, adapter call, approval, and closeout needs durable state.

### 7. Add Isolation

Each project and workstream gets its own:

- context scope
- memory scope
- artifact namespace
- tool permissions
- credential permissions
- event ledger
- closeout path

### 8. Add Package Format

Make Beings, Skills, workflows, policies, templates, and connectors installable modules with metadata, permissions, versioning, and compatibility checks.

### 9. Make The Desktop App The Shell

The desktop UI is not the OS. It is the shell for operating the OS. The CLI, chat interface, and Hermes-style persistent interface can become additional shells over the same runtime.

## Suggested Workstreams

| Workstream | Purpose |
| ---------- | ------- |
| Kernel and Authority | Canonical PolicyGate / OBEXGATE runtime boundary |
| System Calls and SDK | Stable `aos.*` APIs for tools, memory, approvals, artifacts, and closeout |
| Process Model | Managed lifecycle for agents, workflows, tickets, and tasks |
| Scheduler | Queue, cadence, retries, deadlines, and blocked-state handling |
| Driver Layer | Codex, AnythingLLM, Hermes, browser, Gmail, Slack, filesystem adapters |
| State and Evidence | SQLite/Postgres schema, manifests, receipts, event ledger, audit export |
| Shells | Desktop app, CLI, chat, and persistent operator surface |
| Package System | Installable Skills, Beings, workflows, policies, templates, connectors |

## Governance Requirements

- Human authority remains the final approval boundary.
- Agents do not gain autonomous authority from personality, role, persistence, or tool access.
- Every governed action writes evidence.
- Every external action has a policy check, scoped permission, and receipt.
- Every memory write has provenance and revocation behavior.
- Every claim about capability must separate verified runtime behavior from intended architecture.

## Evidence Requirements

Before claiming the runtime milestone is defensible:

- prove the canonical kernel blocks disallowed actions
- prove system calls route through the kernel
- prove agent processes have lifecycle state
- prove driver calls are permissioned and logged
- prove artifacts and events persist
- prove recovery transitions work
- prove at least one shell can operate the runtime
- prove closeout creates tamper-evident, hash-backed receipts

## Non-Goals

- Do not claim AgencyOS is a hardware operating system.
- Do not claim production readiness before live runtime, persistence, auth, shell flows, driver execution, and recovery are verified.
- Do not let Hermes, Codex, Bionic, AnythingLLM, or any other agent bypass AgencyOS authority.
- Do not treat simulated adapters as live integrations.
- Do not treat logs as tamper-proof unless the implementation proves that property.

## First Prototype Milestone

Build `AgencyOS Runtime Kernel v0.1`:

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

This milestone proves the shape of an agentic work operating system without overstating production readiness.
