import json
import tempfile
import unittest
from pathlib import Path

from tools.agencyos_runtime import (
    ActivationState,
    EvidenceLockStatus,
    RuntimeEvent,
    build_activation_states,
    build_evidence_lock_status,
    hash_deliverable,
    load_events,
    render_timeline_html,
)


class AgencyOSRuntimeTests(unittest.TestCase):
    def test_load_events_rejects_unknown_event_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "event_id": "evt-1",
                        "type": "agent_drifted_mysteriously",
                        "actor": "@jaavis",
                        "phase": "intake",
                        "timestamp": "2026-08-12T12:00:00Z",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unknown event type"):
                load_events(path)

    def test_build_activation_states_tracks_active_and_muted_windows(self):
        events = [
            RuntimeEvent(
                event_id="evt-1",
                type="agent_activated",
                actor="@atlas",
                phase="research",
                timestamp="2026-08-12T12:00:00Z",
            ),
            RuntimeEvent(
                event_id="evt-2",
                type="agent_muted",
                actor="@atlas",
                phase="research",
                timestamp="2026-08-12T12:05:00Z",
            ),
            RuntimeEvent(
                event_id="evt-3",
                type="agent_activated",
                actor="@vera",
                phase="evidence_lock",
                timestamp="2026-08-12T12:10:00Z",
            ),
        ]

        states = build_activation_states(events)

        self.assertEqual(
            states["@atlas"],
            ActivationState(
                actor="@atlas",
                status="muted",
                windows=[("research", "2026-08-12T12:00:00Z", "2026-08-12T12:05:00Z")],
            ),
        )
        self.assertEqual(states["@vera"].status, "active")
        self.assertEqual(states["@vera"].windows[0], ("evidence_lock", "2026-08-12T12:10:00Z", None))

    def test_hash_deliverable_uses_sha256_and_records_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            deliverable = root / "deliverables" / "copy.md"
            deliverable.parent.mkdir()
            deliverable.write_text("launch copy\n", encoding="utf-8")

            record = hash_deliverable(deliverable, root=root, owner="@aria-bloom")

            self.assertEqual(record.owner, "@aria-bloom")
            self.assertEqual(record.path, "deliverables/copy.md")
            self.assertEqual(len(record.sha256), 64)
            self.assertEqual(record.algorithm, "sha256")

    def test_evidence_lock_requires_hashes_evidence_and_claim_verification(self):
        events = [
            RuntimeEvent(
                event_id="evt-1",
                type="deliverable_created",
                actor="@mason-true",
                phase="build",
                timestamp="2026-08-12T12:00:00Z",
                artifact="deliverables/intake.html",
            ),
            RuntimeEvent(
                event_id="evt-2",
                type="deliverable_hashed",
                actor="@soren-gate",
                phase="evidence_lock",
                timestamp="2026-08-12T12:01:00Z",
                artifact="deliverables/intake.html",
                sha256="a" * 64,
            ),
            RuntimeEvent(
                event_id="evt-3",
                type="evidence_attached",
                actor="@vera",
                phase="evidence_lock",
                timestamp="2026-08-12T12:02:00Z",
                artifact="deliverables/intake.html",
            ),
            RuntimeEvent(
                event_id="evt-4",
                type="claim_verified",
                actor="@vera-quill",
                phase="evidence_lock",
                timestamp="2026-08-12T12:03:00Z",
                artifact="deliverables/intake.html",
            ),
        ]

        status = build_evidence_lock_status(events)

        self.assertEqual(
            status,
            EvidenceLockStatus(
                passed=True,
                locked_artifacts=["deliverables/intake.html"],
                missing_hashes=[],
                missing_evidence=[],
                missing_claim_verification=[],
            ),
        )

    def test_render_timeline_html_contains_active_and_muted_states(self):
        states = {
            "@jaavis": ActivationState(
                actor="@jaavis",
                status="muted",
                windows=[("intake", "2026-08-12T12:00:00Z", "2026-08-12T12:10:00Z")],
            ),
            "@vera": ActivationState(
                actor="@vera",
                status="active",
                windows=[("evidence_lock", "2026-08-12T12:15:00Z", None)],
            ),
        }
        lock = EvidenceLockStatus(
            passed=False,
            locked_artifacts=[],
            missing_hashes=["deliverables/intake.html"],
            missing_evidence=[],
            missing_claim_verification=[],
        )

        html = render_timeline_html(states, lock)

        self.assertIn("@jaavis", html)
        self.assertIn("MUTED", html)
        self.assertIn("@vera", html)
        self.assertIn("ACTIVE", html)
        self.assertIn("deliverables/intake.html", html)


if __name__ == "__main__":
    unittest.main()
