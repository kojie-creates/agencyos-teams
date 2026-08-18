from __future__ import annotations

import hashlib
import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


EVENT_TYPES = {
    "task_received",
    "scope_gate_passed",
    "risk_gate_passed",
    "agent_activated",
    "specialist_assigned",
    "handoff_packet_created",
    "deliverable_created",
    "deliverable_hashed",
    "evidence_attached",
    "claim_verified",
    "agent_muted",
    "evidence_lock_passed",
    "decision_packet_created",
    "kojie_approved",
    "task_closed",
    "capability_activated",
    "capability_blocked",
}


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    type: str
    actor: str
    phase: str
    timestamp: str
    artifact: str | None = None
    sha256: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class ActivationState:
    actor: str
    status: str
    windows: list[tuple[str, str, str | None]] = field(default_factory=list)


@dataclass(frozen=True)
class DeliverableHash:
    path: str
    sha256: str
    algorithm: str
    owner: str


@dataclass(frozen=True)
class EvidenceLockStatus:
    passed: bool
    locked_artifacts: list[str]
    missing_hashes: list[str]
    missing_evidence: list[str]
    missing_claim_verification: list[str]


def load_events(path: Path) -> list[RuntimeEvent]:
    events: list[RuntimeEvent] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        data = json.loads(line)
        event_type = data.get("type")
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unknown event type on line {line_number}: {event_type}")
        events.append(RuntimeEvent(**{key: data.get(key) for key in RuntimeEvent.__dataclass_fields__}))
    return events


def write_event(path: Path, event: RuntimeEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_event_dict(event), sort_keys=True) + "\n")


def build_activation_states(events: Iterable[RuntimeEvent]) -> dict[str, ActivationState]:
    active: dict[str, tuple[str, str]] = {}
    windows: dict[str, list[tuple[str, str, str | None]]] = {}

    for event in events:
        if event.type == "agent_activated":
            active[event.actor] = (event.phase, event.timestamp)
            windows.setdefault(event.actor, [])
        elif event.type == "agent_muted":
            phase, start = active.pop(event.actor, (event.phase, event.timestamp))
            windows.setdefault(event.actor, []).append((phase, start, event.timestamp))

    for actor, (phase, start) in active.items():
        windows.setdefault(actor, []).append((phase, start, None))

    return {
        actor: ActivationState(
            actor=actor,
            status="active" if actor in active else "muted",
            windows=actor_windows,
        )
        for actor, actor_windows in sorted(windows.items())
    }


def hash_deliverable(path: Path, *, root: Path, owner: str) -> DeliverableHash:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    return DeliverableHash(path=relative, sha256=digest, algorithm="sha256", owner=owner)


def build_evidence_lock_status(events: Iterable[RuntimeEvent]) -> EvidenceLockStatus:
    deliverables = {event.artifact for event in events if event.type == "deliverable_created" and event.artifact}
    hashes = {event.artifact for event in events if event.type == "deliverable_hashed" and event.artifact and event.sha256}
    evidence = {event.artifact for event in events if event.type == "evidence_attached" and event.artifact}
    claims = {event.artifact for event in events if event.type == "claim_verified" and event.artifact}

    missing_hashes = sorted(deliverables - hashes)
    missing_evidence = sorted(deliverables - evidence)
    missing_claim_verification = sorted(deliverables - claims)
    locked = sorted(deliverables & hashes & evidence & claims)

    return EvidenceLockStatus(
        passed=not missing_hashes and not missing_evidence and not missing_claim_verification,
        locked_artifacts=locked,
        missing_hashes=missing_hashes,
        missing_evidence=missing_evidence,
        missing_claim_verification=missing_claim_verification,
    )


def render_timeline_html(states: dict[str, ActivationState], evidence_lock: EvidenceLockStatus) -> str:
    rows = []
    for state in states.values():
        status = "ACTIVE" if state.status == "active" else "MUTED"
        windows = "; ".join(
            f"{phase}: {start} -> {end or 'still active'}" for phase, start, end in state.windows
        )
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(state.actor)}</code></td>"
            f"<td>{status}</td>"
            f"<td>{html.escape(windows)}</td>"
            "</tr>"
        )

    missing = evidence_lock.missing_hashes + evidence_lock.missing_evidence + evidence_lock.missing_claim_verification
    missing_items = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in missing)
    locked_items = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in evidence_lock.locked_artifacts)
    lock_status = "PASSED" if evidence_lock.passed else "BLOCKED"

    return (
        '<div class="agencyos-runtime-timeline">'
        "<table>"
        "<thead><tr><th>Actor</th><th>State</th><th>Activation windows</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        f"<p>Evidence lock: {lock_status}</p>"
        f"<p>Locked artifacts</p><ul>{locked_items}</ul>"
        f"<p>Missing lock inputs</p><ul>{missing_items}</ul>"
        "</div>"
    )


def _event_dict(event: RuntimeEvent) -> dict[str, str]:
    return {key: value for key, value in event.__dict__.items() if value is not None}
