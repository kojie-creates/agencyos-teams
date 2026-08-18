import json
import tempfile
import unittest
from pathlib import Path

from tools.capability_registry import (
    CapabilityRecord,
    CapabilityTransition,
    CapabilityTransitionError,
    build_capability_events,
    capability_summary,
    load_capabilities,
    transition_capability,
)


class CapabilityRegistryTests(unittest.TestCase):
    def test_load_capabilities_rejects_unknown_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "active-capabilities.json"
            path.write_text(
                json.dumps(
                    {
                        "capabilities": [
                            {
                                "id": "scope-gate",
                                "name": "Scope Gate",
                                "status": "mysteriously-on",
                                "category": "governance",
                                "source": "skills/AGENCYOS-PRO-AGENTS.md",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unknown capability status"):
                load_capabilities(path)

    def test_capability_summary_groups_statuses(self):
        records = [
            CapabilityRecord("scope-gate", "Scope Gate", "available", "governance", "source.md"),
            CapabilityRecord("runtime-log", "Runtime Event Log", "active", "runtime", "runtime/README.md"),
            CapabilityRecord("personal-context", "Personal Context", "requires_approval", "memory", "personal/README.md"),
        ]

        self.assertEqual(
            capability_summary(records),
            {
                "active": ["Runtime Event Log"],
                "available": ["Scope Gate"],
                "blocked": [],
                "deprecated": [],
                "installed": [],
                "requires_approval": ["Personal Context"],
            },
        )

    def test_transition_requires_approval_before_activation_when_marked(self):
        record = CapabilityRecord(
            "personal-context",
            "Personal Context",
            "requires_approval",
            "memory",
            "personal/README.md",
            requires_approval=True,
        )

        with self.assertRaisesRegex(CapabilityTransitionError, "requires approval"):
            transition_capability(record, "active", approved_by=None)

        transitioned = transition_capability(record, "active", approved_by="Kojie")
        self.assertEqual(transitioned.status, "active")

    def test_build_capability_events_marks_active_and_blocked(self):
        records = [
            CapabilityRecord("runtime-log", "Runtime Event Log", "active", "runtime", "runtime/README.md"),
            CapabilityRecord("personal-context", "Personal Context", "requires_approval", "memory", "personal/README.md"),
            CapabilityRecord("legacy-bloat", "Legacy Bloat", "blocked", "history", "history/README.md"),
        ]

        events = build_capability_events(records, timestamp="2026-08-12T16:45:00Z")

        self.assertEqual([event.type for event in events], ["capability_activated", "capability_blocked"])
        self.assertEqual(events[0].actor, "runtime-log")
        self.assertEqual(events[1].actor, "legacy-bloat")


if __name__ == "__main__":
    unittest.main()
