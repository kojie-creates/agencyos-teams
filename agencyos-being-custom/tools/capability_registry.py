from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

try:
    from agencyos_runtime import RuntimeEvent
except ModuleNotFoundError:
    from tools.agencyos_runtime import RuntimeEvent


CAPABILITY_STATUSES = {
    "available",
    "installed",
    "active",
    "blocked",
    "requires_approval",
    "deprecated",
}


@dataclass(frozen=True)
class CapabilityRecord:
    id: str
    name: str
    status: str
    category: str
    source: str
    requires_approval: bool = False
    reason: str | None = None


@dataclass(frozen=True)
class CapabilityTransition:
    capability_id: str
    from_status: str
    to_status: str
    approved_by: str | None = None


class CapabilityTransitionError(ValueError):
    pass


def load_capabilities(path: Path) -> list[CapabilityRecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = [CapabilityRecord(**item) for item in data.get("capabilities", [])]
    for record in records:
        if record.status not in CAPABILITY_STATUSES:
            raise ValueError(f"unknown capability status: {record.status}")
    return records


def capability_summary(records: list[CapabilityRecord]) -> dict[str, list[str]]:
    summary = {status: [] for status in sorted(CAPABILITY_STATUSES)}
    for record in records:
        summary[record.status].append(record.name)
    return {status: sorted(names) for status, names in summary.items()}


def transition_capability(
    record: CapabilityRecord,
    to_status: str,
    *,
    approved_by: str | None = None,
) -> CapabilityRecord:
    if to_status not in CAPABILITY_STATUSES:
        raise CapabilityTransitionError(f"unknown target status: {to_status}")
    if to_status == "active" and record.requires_approval and not approved_by:
        raise CapabilityTransitionError(f"{record.name} requires approval before activation")
    return CapabilityRecord(
        id=record.id,
        name=record.name,
        status=to_status,
        category=record.category,
        source=record.source,
        requires_approval=record.requires_approval,
        reason=record.reason,
    )


def build_capability_events(records: list[CapabilityRecord], *, timestamp: str) -> list[RuntimeEvent]:
    events: list[RuntimeEvent] = []
    for record in records:
        if record.status == "active":
            events.append(
                RuntimeEvent(
                    event_id=f"cap-{record.id}-active",
                    type="capability_activated",
                    actor=record.id,
                    phase="capability_registry",
                    timestamp=timestamp,
                    note=record.name,
                )
            )
        elif record.status == "blocked":
            events.append(
                RuntimeEvent(
                    event_id=f"cap-{record.id}-blocked",
                    type="capability_blocked",
                    actor=record.id,
                    phase="capability_registry",
                    timestamp=timestamp,
                    note=record.name,
                )
            )
    return events
