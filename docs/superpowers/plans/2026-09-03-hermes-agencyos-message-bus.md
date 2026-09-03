# Hermes AgencyOS Message Bus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Hermes AgencyOS Packet Router v0.1 so Hermes can create authoritative AgencyOS handoff packets, publish durable NATS notifications, and let bot workers claim, complete, and hand off packet work asynchronously.

**Architecture:** Keep `C:\Users\felix\Desktop\agencyos-teams` as the authoritative AgencyOS Teams project record. Implement transport, worker, and adapter code in `C:\Users\felix\Desktop\agencyos-bus-sidecar`, reusing its existing packet store, response store, adapter layer, config, and tests. Use NATS JetStream as the durable notification bus while file-backed packets remain the source of truth.

**Tech Stack:** Python standard library, existing sidecar modules, pytest, optional `nats-py` for live NATS JetStream, file-backed fake bus for tests.

**Spec:** `C:\Users\felix\Desktop\agencyos-teams\docs\superpowers\specs\2026-09-03-hermes-agencyos-message-bus-design.md`

## Global Constraints

- AgencyOS Teams packet files remain authoritative in v0.1.
- NATS carries small packet availability and lifecycle events, not full work context.
- Hermes routes and summarizes; workers perform specialist work.
- Local model lanes include Qwen, Gemma 4, and Bonsai.
- Workers are asynchronous and must not depend on another bot being live in the same chat loop.
- Timeouts produce packet state such as `BLOCKED`, not lost conversations.
- External app actions require `HUMAN_APPROVAL_REQUIRED` until explicit human approval is recorded.
- Do not claim production readiness, continuous availability, deployed bot operations, or real external app execution from this milestone.
- Leave unrelated dirty working-tree changes untouched.

---

## File Structure

Create or modify only these sidecar files unless a test reveals a required local helper split:

- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\bus.py`
  - Add packet update helpers for status, assigned bot, next bot, evidence paths, handoff notes, and retries.
  - Preserve existing `send_message`, `create_packet`, `list_packets`, and `show_packet` behavior unless tests intentionally extend them.
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\message_bus.py`
  - Define `BusEvent`, subject helpers, an in-memory fake bus for tests, and an optional NATS JetStream bus wrapper.
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\hermes_router.py`
  - Provide a Python API and CLI to create a packet, mark it routed, and publish `agencyos.packet.ready.<bot>`.
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\workers.py`
  - Define the worker API for claim, in-progress, complete, blocked, human approval, and next-agent publication.
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\adapters.py`
  - Reuse existing adapters through worker calls. Add no new live external action capability in v0.1.
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\config\sidecar.json`
  - Add bus and worker config with NATS disabled by default so tests and local dry runs stay cheap.
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_message_bus.py`
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_hermes_router.py`
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_workers.py`
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\README.md`
  - Add v0.1 NATS routing usage, evidence boundaries, and smoke-test commands.

---

### Task 1: Packet State Helpers

**Files:**
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\bus.py`
- Test: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_bus.py`

**Interfaces:**
- Consumes: existing `create_packet(sidecar_root: Path, config: dict, message: str, origin_entity: str, target_entities: list[str], next_entity: str, workstream: str) -> dict`
- Produces:
  - `update_packet(sidecar_root: Path, packet_id: str, updates: dict) -> dict`
  - `append_packet_evidence(sidecar_root: Path, packet_id: str, evidence_path: str) -> dict`
  - `record_packet_event(sidecar_root: Path, event_type: str, packet_id: str, data: dict) -> None`

- [ ] **Step 1: Write failing packet update tests**

Append these tests to `tests\test_bus.py`:

```python
def test_update_packet_rehashes_and_persists_status(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    packet = bus.create_packet(
        sidecar_root=tmp_path,
        config=config,
        message="Route this packet.",
        origin_entity="hermes",
        target_entities=["codex"],
        next_entity="codex",
        workstream="projects/example/workstreams/runtime",
    )
    original_hash = packet["packet_hash"]

    updated = bus.update_packet(
        tmp_path,
        packet["packet_id"],
        {"status": "ROUTED", "assigned_to": "codex", "next_agent": "gemma"},
    )

    stored = json.loads((tmp_path / "packets" / f"{packet['packet_id']}.json").read_text(encoding="utf-8"))
    assert updated["status"] == "ROUTED"
    assert updated["assigned_to"] == "codex"
    assert updated["next_agent"] == "gemma"
    assert updated["packet_hash"] != original_hash
    assert stored == updated


def test_append_packet_evidence_preserves_existing_paths(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    packet = bus.create_packet(
        sidecar_root=tmp_path,
        config=config,
        message="Write evidence.",
        origin_entity="hermes",
        target_entities=["codex"],
        next_entity="gemma",
        workstream="projects/example/workstreams/runtime",
    )

    first = bus.append_packet_evidence(tmp_path, packet["packet_id"], "responses/PKT-test/codex.json")
    second = bus.append_packet_evidence(tmp_path, packet["packet_id"], "runtime/events.jsonl")

    assert first["evidence_paths"] == ["responses/PKT-test/codex.json"]
    assert second["evidence_paths"] == ["responses/PKT-test/codex.json", "runtime/events.jsonl"]
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests\test_bus.py::test_update_packet_rehashes_and_persists_status tests\test_bus.py::test_append_packet_evidence_preserves_existing_paths -q
```

Expected: FAIL with `AttributeError: module 'bus' has no attribute 'update_packet'`.

- [ ] **Step 3: Implement packet helpers**

Add these functions to `bus.py` near `show_packet`:

```python
def update_packet(sidecar_root: Path, packet_id: str, updates: dict) -> dict:
    packet = show_packet(sidecar_root, packet_id)
    packet.update(updates)
    packet["packet_hash"] = _hash_json({key: value for key, value in packet.items() if key != "packet_hash"})
    _write_packet(sidecar_root, packet)
    _append_event(sidecar_root, "PACKET_UPDATED", packet_id, {"updates": sorted(updates.keys())})
    return packet


def append_packet_evidence(sidecar_root: Path, packet_id: str, evidence_path: str) -> dict:
    packet = show_packet(sidecar_root, packet_id)
    evidence_paths = list(packet.get("evidence_paths") or packet.get("artifact_paths") or [])
    if evidence_path not in evidence_paths:
        evidence_paths.append(evidence_path)
    return update_packet(sidecar_root, packet_id, {"evidence_paths": evidence_paths, "artifact_paths": evidence_paths})


def record_packet_event(sidecar_root: Path, event_type: str, packet_id: str, data: dict) -> None:
    _append_event(sidecar_root, event_type, packet_id, data)
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests\test_bus.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add bus.py tests\test_bus.py
git commit -m "Add packet state helpers"
```

---

### Task 2: Message Bus Abstraction

**Files:**
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\message_bus.py`
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_message_bus.py`

**Interfaces:**
- Consumes: no sidecar-specific imports
- Produces:
  - `READY_SUBJECTS: dict[str, str]`
  - `subject_for_agent(agent_name: str) -> str`
  - `BusEvent` dataclass with `subject: str` and `payload: dict`
  - `InMemoryMessageBus.publish(subject: str, payload: dict) -> BusEvent`
  - `InMemoryMessageBus.last_event(subject: str | None = None) -> BusEvent | None`
  - `InMemoryMessageBus.events_for(subject: str) -> list[BusEvent]`
  - `NatsJetStreamBus.publish(subject: str, payload: dict) -> BusEvent`

- [ ] **Step 1: Write failing message bus tests**

Create `tests\test_message_bus.py`:

```python
from message_bus import InMemoryMessageBus, subject_for_agent


def test_subject_for_agent_normalizes_known_bot_names():
    assert subject_for_agent("codex") == "agencyos.packet.ready.codex"
    assert subject_for_agent("gemma") == "agencyos.packet.ready.gemma"
    assert subject_for_agent("bionic-gemma") == "agencyos.packet.ready.gemma"
    assert subject_for_agent("anythingllm-qwen") == "agencyos.packet.ready.qwen"
    assert subject_for_agent("qwen") == "agencyos.packet.ready.qwen"
    assert subject_for_agent("bonsai") == "agencyos.packet.ready.bonsai"


def test_in_memory_bus_records_events_by_subject():
    bus = InMemoryMessageBus()
    event = bus.publish(
        "agencyos.packet.ready.codex",
        {"packet_id": "PKT-test", "assigned_to": "codex"},
    )

    assert event.subject == "agencyos.packet.ready.codex"
    assert event.payload["packet_id"] == "PKT-test"
    assert bus.last_event().payload["assigned_to"] == "codex"
    assert bus.events_for("agencyos.packet.ready.codex") == [event]
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests\test_message_bus.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'message_bus'`.

- [ ] **Step 3: Implement message bus abstraction**

Create `message_bus.py`:

```python
"""Durable packet notification bus abstractions for AgencyOS sidecar."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass


READY_SUBJECTS = {
    "hermes": "agencyos.packet.ready.hermes",
    "codex": "agencyos.packet.ready.codex",
    "gemma": "agencyos.packet.ready.gemma",
    "bionic-gemma": "agencyos.packet.ready.gemma",
    "qwen": "agencyos.packet.ready.qwen",
    "anythingllm-qwen": "agencyos.packet.ready.qwen",
    "bonsai": "agencyos.packet.ready.bonsai",
}


@dataclass(frozen=True)
class BusEvent:
    subject: str
    payload: dict


def subject_for_agent(agent_name: str) -> str:
    key = agent_name.strip().lower()
    return READY_SUBJECTS.get(key, f"agencyos.packet.ready.{key.replace('_', '-')}")


class InMemoryMessageBus:
    def __init__(self) -> None:
        self.events: list[BusEvent] = []

    def publish(self, subject: str, payload: dict) -> BusEvent:
        event = BusEvent(subject=subject, payload=dict(payload))
        self.events.append(event)
        return event

    def last_event(self, subject: str | None = None) -> BusEvent | None:
        events = self.events if subject is None else self.events_for(subject)
        return events[-1] if events else None

    def events_for(self, subject: str) -> list[BusEvent]:
        return [event for event in self.events if event.subject == subject]


class NatsJetStreamBus:
    def __init__(self, servers: str = "nats://127.0.0.1:4222", stream: str = "AGENCYOS") -> None:
        self.servers = servers
        self.stream = stream

    def publish(self, subject: str, payload: dict) -> BusEvent:
        asyncio.run(self._publish(subject, payload))
        return BusEvent(subject=subject, payload=dict(payload))

    async def _publish(self, subject: str, payload: dict) -> None:
        try:
            import nats
        except ImportError as error:
            raise RuntimeError("nats-py is required for live NATS publishing") from error

        client = await nats.connect(self.servers)
        try:
            jetstream = client.jetstream()
            await jetstream.add_stream(name=self.stream, subjects=["agencyos.packet.>"])
            await jetstream.publish(subject, json.dumps(payload).encode("utf-8"))
        finally:
            await client.drain()
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests\test_message_bus.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add message_bus.py tests\test_message_bus.py
git commit -m "Add message bus abstraction"
```

---

### Task 3: Hermes Router

**Files:**
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\hermes_router.py`
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_hermes_router.py`

**Interfaces:**
- Consumes:
  - `bus.create_packet(...) -> dict`
  - `bus.update_packet(...) -> dict`
  - `bus.record_packet_event(...) -> None`
  - `message_bus.subject_for_agent(agent_name: str) -> str`
  - bus object with `publish(subject: str, payload: dict) -> BusEvent`
- Produces:
  - `route_packet(sidecar_root: Path, config: dict, task: str, assigned_to: str, next_agent: str, workstream: str, message_bus: object, origin: str = "hermes") -> dict`

- [ ] **Step 1: Write failing Hermes router tests**

Create `tests\test_hermes_router.py`:

```python
import json

from hermes_router import route_packet
from message_bus import InMemoryMessageBus


def test_hermes_route_creates_packet_and_publishes_ready_event(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    fake_bus = InMemoryMessageBus()

    result = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Implement async handoff.",
        assigned_to="codex",
        next_agent="gemma",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    packet = result["packet"]
    event = result["event"]
    stored = json.loads((tmp_path / "packets" / f"{packet['packet_id']}.json").read_text(encoding="utf-8"))

    assert stored["origin_entity"] == "hermes"
    assert stored["assigned_to"] == "codex"
    assert stored["next_agent"] == "gemma"
    assert stored["status"] == "ROUTED"
    assert event.subject == "agencyos.packet.ready.codex"
    assert event.payload["packet_id"] == packet["packet_id"]
    assert event.payload["packet_path"].endswith(f"{packet['packet_id']}.json")


def test_hermes_route_records_bus_publish_event(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    fake_bus = InMemoryMessageBus()

    result = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Check governance.",
        assigned_to="bionic-gemma",
        next_agent="qwen",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    events = [
        json.loads(line)
        for line in (tmp_path / "runtime" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert any(event["event_type"] == "PACKET_ROUTED" for event in events)
    assert any(event["event_type"] == "BUS_EVENT_PUBLISHED" for event in events)
    assert result["event"].subject == "agencyos.packet.ready.gemma"


def test_hermes_route_supports_bonsai_as_third_local_model(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    fake_bus = InMemoryMessageBus()

    result = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Use Bonsai as helper lane.",
        assigned_to="bonsai",
        next_agent="gemma",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    assert result["packet"]["assigned_to"] == "bonsai"
    assert result["packet"]["next_agent"] == "gemma"
    assert result["event"].subject == "agencyos.packet.ready.bonsai"
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests\test_hermes_router.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hermes_router'`.

- [ ] **Step 3: Implement Hermes router**

Create `hermes_router.py`:

```python
"""Hermes router for AgencyOS packet bus handoffs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import bus
from message_bus import InMemoryMessageBus, NatsJetStreamBus, subject_for_agent


DEFAULT_SIDECAR_ROOT = Path(__file__).resolve().parent


def route_packet(
    sidecar_root: Path,
    config: dict,
    task: str,
    assigned_to: str,
    next_agent: str,
    workstream: str,
    message_bus: object,
    origin: str = "hermes",
) -> dict:
    packet = bus.create_packet(
        sidecar_root=sidecar_root,
        config=config,
        message=task,
        origin_entity=origin,
        target_entities=[assigned_to],
        next_entity=assigned_to,
        workstream=workstream,
    )
    packet = bus.update_packet(
        sidecar_root,
        packet["packet_id"],
        {
            "assigned_to": assigned_to,
            "next_agent": next_agent,
            "status": "ROUTED",
            "task": task,
        },
    )
    bus.record_packet_event(
        sidecar_root,
        "PACKET_ROUTED",
        packet["packet_id"],
        {"assigned_to": assigned_to, "next_agent": next_agent},
    )
    subject = subject_for_agent(assigned_to)
    payload = {
        "packet_id": packet["packet_id"],
        "status": "ROUTED",
        "assigned_to": assigned_to,
        "next_agent": next_agent,
        "packet_path": str(sidecar_root / "packets" / f"{packet['packet_id']}.json"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    event = message_bus.publish(subject, payload)
    bus.record_packet_event(
        sidecar_root,
        "BUS_EVENT_PUBLISHED",
        packet["packet_id"],
        {"subject": subject, "payload": payload},
    )
    return {"packet": packet, "event": event}


def _build_message_bus(config: dict) -> object:
    bus_config = config.get("message_bus") or {}
    if bus_config.get("mode") == "nats":
        return NatsJetStreamBus(
            servers=bus_config.get("servers", "nats://127.0.0.1:4222"),
            stream=bus_config.get("stream", "AGENCYOS"),
        )
    return InMemoryMessageBus()


def main() -> int:
    parser = argparse.ArgumentParser(description="Route an AgencyOS handoff packet through Hermes")
    parser.add_argument("--root", default=str(DEFAULT_SIDECAR_ROOT))
    parser.add_argument("--config", default=str(bus.DEFAULT_CONFIG_PATH))
    parser.add_argument("route", choices=["route"])
    parser.add_argument("--task", required=True)
    parser.add_argument("--to", required=True)
    parser.add_argument("--next", default="")
    parser.add_argument("--workstream", default="agencyos-one-bionic-codex-integration")
    args = parser.parse_args()

    sidecar_root = Path(args.root)
    config = bus.load_config(Path(args.config))
    result = route_packet(
        sidecar_root=sidecar_root,
        config=config,
        task=args.task,
        assigned_to=args.to,
        next_agent=args.next,
        workstream=args.workstream,
        message_bus=_build_message_bus(config),
    )
    print(json.dumps({"packet": result["packet"], "event": result["event"].__dict__}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests\test_hermes_router.py tests\test_message_bus.py tests\test_bus.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add hermes_router.py tests\test_hermes_router.py
git commit -m "Add Hermes packet router"
```

---

### Task 4: Worker Claim And Handoff Flow

**Files:**
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\workers.py`
- Create: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_workers.py`

**Interfaces:**
- Consumes:
  - `bus.show_packet(...) -> dict`
  - `bus.update_packet(...) -> dict`
  - `bus.append_packet_evidence(...) -> dict`
  - `bus.record_packet_event(...) -> None`
  - `AdapterRegistry(config).dispatch(entity_name: str, entity: dict, packet: dict) -> dict`
  - `message_bus.subject_for_agent(agent_name: str) -> str`
- Produces:
  - `WorkerResult` dataclass with `packet: dict`, `response: dict | None`, `event: object | None`
  - `run_worker_once(sidecar_root: Path, config: dict, packet_id: str, worker_name: str, message_bus: object) -> WorkerResult`

- [ ] **Step 1: Write failing worker tests**

Create `tests\test_workers.py`:

```python
import json

from hermes_router import route_packet
from message_bus import InMemoryMessageBus
from workers import run_worker_once


def test_worker_claims_packet_writes_response_and_notifies_next_agent(tmp_path):
    config = {
        "agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams",
        "entities": {
            "codex": {"enabled": True, "mode": "stub", "role": "execution"},
            "bionic-gemma": {"enabled": True, "mode": "stub", "role": "governance"},
        },
    }
    fake_bus = InMemoryMessageBus()
    routed = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Implement narrow fix.",
        assigned_to="codex",
        next_agent="bionic-gemma",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    result = run_worker_once(tmp_path, config, routed["packet"]["packet_id"], "codex", fake_bus)

    assert result.packet["status"] == "HANDOFF_READY"
    assert result.packet["assigned_to"] == "codex"
    assert result.packet["next_agent"] == "bionic-gemma"
    assert result.response["entity"] == "codex"
    assert result.response["status"] == "RESPONDED"
    assert result.event.subject == "agencyos.packet.ready.gemma"
    assert any(path.endswith("codex.json") for path in result.packet["evidence_paths"])


def test_worker_marks_completed_when_no_next_agent(tmp_path):
    config = {
        "agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams",
        "entities": {"codex": {"enabled": True, "mode": "stub", "role": "execution"}},
    }
    fake_bus = InMemoryMessageBus()
    routed = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Close this packet.",
        assigned_to="codex",
        next_agent="",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    result = run_worker_once(tmp_path, config, routed["packet"]["packet_id"], "codex", fake_bus)

    assert result.packet["status"] == "COMPLETED"
    assert result.event.subject == "agencyos.packet.completed"


def test_worker_rejects_packet_assigned_to_other_worker(tmp_path):
    config = {
        "agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams",
        "entities": {"codex": {"enabled": True, "mode": "stub", "role": "execution"}},
    }
    fake_bus = InMemoryMessageBus()
    routed = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Gemma should handle this.",
        assigned_to="bionic-gemma",
        next_agent="codex",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    result = run_worker_once(tmp_path, config, routed["packet"]["packet_id"], "codex", fake_bus)

    assert result.packet["status"] == "ROUTED"
    assert result.response is None
    assert result.event is None


def test_worker_records_claim_and_handoff_events(tmp_path):
    config = {
        "agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams",
        "entities": {"codex": {"enabled": True, "mode": "stub", "role": "execution"}},
    }
    fake_bus = InMemoryMessageBus()
    routed = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Record lifecycle.",
        assigned_to="codex",
        next_agent="",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    run_worker_once(tmp_path, config, routed["packet"]["packet_id"], "codex", fake_bus)

    events = [
        json.loads(line)
        for line in (tmp_path / "runtime" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    event_types = [event["event_type"] for event in events]
    assert "PACKET_CLAIMED" in event_types
    assert "PACKET_IN_PROGRESS" in event_types
    assert "PACKET_COMPLETED" in event_types
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests\test_workers.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'workers'`.

- [ ] **Step 3: Implement worker flow**

Create `workers.py`:

```python
"""Bot worker lifecycle for AgencyOS sidecar packet bus."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import bus
from adapters import AdapterRegistry
from message_bus import subject_for_agent


@dataclass
class WorkerResult:
    packet: dict
    response: dict | None
    event: object | None


def run_worker_once(
    sidecar_root: Path,
    config: dict,
    packet_id: str,
    worker_name: str,
    message_bus: object,
) -> WorkerResult:
    packet = bus.show_packet(sidecar_root, packet_id)
    if packet.get("assigned_to") != worker_name:
        return WorkerResult(packet=packet, response=None, event=None)

    packet = bus.update_packet(sidecar_root, packet_id, {"status": "CLAIMED"})
    bus.record_packet_event(sidecar_root, "PACKET_CLAIMED", packet_id, {"worker": worker_name})
    packet = bus.update_packet(sidecar_root, packet_id, {"status": "IN_PROGRESS"})
    bus.record_packet_event(sidecar_root, "PACKET_IN_PROGRESS", packet_id, {"worker": worker_name})

    entity = (config.get("entities") or {}).get(worker_name, {"enabled": True, "mode": "stub"})
    response = AdapterRegistry(config).dispatch(worker_name, entity, packet)
    response_path = bus._write_response(sidecar_root, packet_id, response)
    packet = bus.append_packet_evidence(sidecar_root, packet_id, str(response_path))

    if response.get("status") == "HUMAN_APPROVAL_REQUIRED":
        packet = bus.update_packet(sidecar_root, packet_id, {"status": "HUMAN_APPROVAL_REQUIRED"})
        event = message_bus.publish(
            "agencyos.packet.needs_human",
            {"packet_id": packet_id, "status": "HUMAN_APPROVAL_REQUIRED", "assigned_to": worker_name},
        )
        bus.record_packet_event(sidecar_root, "HUMAN_APPROVAL_REQUIRED", packet_id, {"worker": worker_name})
        return WorkerResult(packet=packet, response=response, event=event)

    next_agent = packet.get("next_agent") or ""
    if next_agent:
        packet = bus.update_packet(
            sidecar_root,
            packet_id,
            {
                "status": "HANDOFF_READY",
                "handoff_notes": f"{worker_name} completed work. Packet is ready for {next_agent}.",
            },
        )
        subject = subject_for_agent(next_agent)
        event = message_bus.publish(
            subject,
            {
                "packet_id": packet_id,
                "status": "HANDOFF_READY",
                "assigned_to": next_agent,
                "previous_agent": worker_name,
                "packet_path": str(sidecar_root / "packets" / f"{packet_id}.json"),
            },
        )
        bus.record_packet_event(sidecar_root, "PACKET_HANDOFF_READY", packet_id, {"next_agent": next_agent})
        return WorkerResult(packet=packet, response=response, event=event)

    packet = bus.update_packet(sidecar_root, packet_id, {"status": "COMPLETED"})
    event = message_bus.publish(
        "agencyos.packet.completed",
        {"packet_id": packet_id, "status": "COMPLETED", "assigned_to": worker_name},
    )
    bus.record_packet_event(sidecar_root, "PACKET_COMPLETED", packet_id, {"worker": worker_name})
    return WorkerResult(packet=packet, response=response, event=event)
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests\test_workers.py tests\test_hermes_router.py tests\test_message_bus.py tests\test_bus.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add workers.py tests\test_workers.py
git commit -m "Add packet worker handoff flow"
```

---

### Task 5: Timeout And Human Approval State

**Files:**
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\workers.py`
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\tests\test_workers.py`

**Interfaces:**
- Consumes:
  - `run_worker_once(...) -> WorkerResult`
  - `bus.update_packet(...) -> dict`
  - `message_bus.publish(...) -> BusEvent`
- Produces:
  - `mark_packet_blocked(sidecar_root: Path, packet_id: str, worker_name: str, reason: str, message_bus: object) -> WorkerResult`
  - `mark_packet_needs_human(sidecar_root: Path, packet_id: str, reason: str, message_bus: object) -> WorkerResult`

- [ ] **Step 1: Write failing timeout and approval tests**

Append these tests to `tests\test_workers.py`:

```python
from workers import mark_packet_blocked, mark_packet_needs_human


def test_mark_packet_blocked_writes_recoverable_state(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    fake_bus = InMemoryMessageBus()
    routed = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="Timeout expected.",
        assigned_to="codex",
        next_agent="gemma",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    result = mark_packet_blocked(
        tmp_path,
        routed["packet"]["packet_id"],
        "codex",
        "worker exceeded work timeout",
        fake_bus,
    )

    assert result.packet["status"] == "BLOCKED"
    assert result.packet["blocked_reason"] == "worker exceeded work timeout"
    assert result.event.subject == "agencyos.packet.blocked"


def test_mark_packet_needs_human_stops_external_action(tmp_path):
    config = {"agencyos_teams_path": "C:/Users/felix/Desktop/agencyos-teams", "entities": {}}
    fake_bus = InMemoryMessageBus()
    routed = route_packet(
        sidecar_root=tmp_path,
        config=config,
        task="External app action.",
        assigned_to="bionic-apps",
        next_agent="",
        workstream="projects/example/workstreams/runtime",
        message_bus=fake_bus,
    )

    result = mark_packet_needs_human(
        tmp_path,
        routed["packet"]["packet_id"],
        "external app action requires approval",
        fake_bus,
    )

    assert result.packet["status"] == "HUMAN_APPROVAL_REQUIRED"
    assert result.packet["approval_state"] == "HUMAN_APPROVAL_REQUIRED"
    assert result.packet["approval_reason"] == "external app action requires approval"
    assert result.event.subject == "agencyos.packet.needs_human"
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m pytest tests\test_workers.py::test_mark_packet_blocked_writes_recoverable_state tests\test_workers.py::test_mark_packet_needs_human_stops_external_action -q
```

Expected: FAIL with import error for `mark_packet_blocked` or `mark_packet_needs_human`.

- [ ] **Step 3: Implement state helpers**

Add to `workers.py` after `run_worker_once`:

```python
def mark_packet_blocked(
    sidecar_root: Path,
    packet_id: str,
    worker_name: str,
    reason: str,
    message_bus: object,
) -> WorkerResult:
    packet = bus.update_packet(
        sidecar_root,
        packet_id,
        {"status": "BLOCKED", "blocked_by": worker_name, "blocked_reason": reason},
    )
    event = message_bus.publish(
        "agencyos.packet.blocked",
        {"packet_id": packet_id, "status": "BLOCKED", "assigned_to": worker_name, "reason": reason},
    )
    bus.record_packet_event(sidecar_root, "PACKET_BLOCKED", packet_id, {"worker": worker_name, "reason": reason})
    return WorkerResult(packet=packet, response=None, event=event)


def mark_packet_needs_human(
    sidecar_root: Path,
    packet_id: str,
    reason: str,
    message_bus: object,
) -> WorkerResult:
    packet = bus.update_packet(
        sidecar_root,
        packet_id,
        {
            "status": "HUMAN_APPROVAL_REQUIRED",
            "approval_state": "HUMAN_APPROVAL_REQUIRED",
            "approval_reason": reason,
        },
    )
    event = message_bus.publish(
        "agencyos.packet.needs_human",
        {"packet_id": packet_id, "status": "HUMAN_APPROVAL_REQUIRED", "reason": reason},
    )
    bus.record_packet_event(sidecar_root, "HUMAN_APPROVAL_REQUIRED", packet_id, {"reason": reason})
    return WorkerResult(packet=packet, response=None, event=event)
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests\test_workers.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add workers.py tests\test_workers.py
git commit -m "Add packet timeout and approval states"
```

---

### Task 6: Config And Documentation

**Files:**
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\config\sidecar.json`
- Modify: `C:\Users\felix\Desktop\agencyos-bus-sidecar\README.md`
- Test: existing sidecar tests

**Interfaces:**
- Consumes:
  - `hermes_router.py route --task ... --to ... --next ...`
  - optional `message_bus.mode = "nats"`
- Produces:
  - documented local dry-run path
  - documented optional NATS path

- [ ] **Step 1: Update config**

Add this top-level block to `config\sidecar.json`:

```json
"message_bus": {
  "mode": "memory",
  "servers": "nats://127.0.0.1:4222",
  "stream": "AGENCYOS",
  "subjects": {
    "created": "agencyos.packet.created",
    "ready_prefix": "agencyos.packet.ready",
    "completed": "agencyos.packet.completed",
    "blocked": "agencyos.packet.blocked",
    "needs_human": "agencyos.packet.needs_human"
  }
}
```

Keep JSON valid. Put a comma before or after this block according to its placement.

- [ ] **Step 2: Update README**

Add a section named `Hermes Packet Router v0.1` to `README.md`:

````markdown
## Hermes Packet Router v0.1

Hermes can route user work into an AgencyOS packet and publish a small packet-available event.

Dry-run route:

```powershell
python hermes_router.py route --task "Create test packet" --to codex --next bionic-gemma
```

The packet file remains authoritative. The bus event only points workers to the packet.

Optional live NATS mode:

```powershell
pip install nats-py
nats-server -js
```

Then set `message_bus.mode` to `nats` in `config/sidecar.json`.

This milestone proves local async packet routing only. It does not prove continuous availability, deployed bots, or external app execution.
````

- [ ] **Step 3: Run full sidecar tests**

Run:

```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 4: Commit**

```powershell
git add config\sidecar.json README.md
git commit -m "Document Hermes packet router setup"
```

---

### Task 7: Final Verification And Evidence

**Files:**
- Modify only if verification exposes a defect in files from Tasks 1-6.

**Interfaces:**
- Consumes: all previous task outputs
- Produces: final verification evidence for the v0.1 milestone

- [ ] **Step 1: Run all sidecar tests**

Run from `C:\Users\felix\Desktop\agencyos-bus-sidecar`:

```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 2: Run dry router command**

Run:

```powershell
python hermes_router.py route --task "Create test packet" --to codex --next bionic-gemma
```

Expected: JSON output containing:

```text
"status": "ROUTED"
"assigned_to": "codex"
"next_agent": "bionic-gemma"
"subject": "agencyos.packet.ready.codex"
```

- [ ] **Step 3: Inspect created packet**

Use the `packet_id` from Step 2:

```powershell
python bus.py show <packet_id>
```

Expected: packet includes `assigned_to`, `next_agent`, `status`, and `packet_hash`.

- [ ] **Step 4: Run final diff check**

Run from `C:\Users\felix\Desktop\agencyos-bus-sidecar`:

```powershell
git diff --check
```

Expected: no output.

- [ ] **Step 5: Report evidence**

Final report must include:

```text
Tests: python -m pytest -q
Smoke: python hermes_router.py route --task "Create test packet" --to codex --next bionic-gemma
Packet: <packet_id>
Boundary: local async packet routing only; no production/deployed/live external app claim.
```

Commit any verification-only documentation only if a new evidence file is created.
