import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.enforcement_kernel import EnforcementKernel, KernelRequest


class RuntimeStorePriority2Tests(unittest.TestCase):
    def test_runtime_store_writes_json_jsonl_and_sqlite_mirror(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-store",
                    title="Store demo",
                    actor_id="actor-operator",
                    requested_outcome="Create a local artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )

            runtime_dir = root / ".agencyos-runtime"
            self.assertTrue((runtime_dir / "runs" / f"{run.run_id}.json").exists())
            self.assertTrue((runtime_dir / "runs" / f"{run.run_id}.events.jsonl").exists())
            self.assertTrue((runtime_dir / "runtime.sqlite3").exists())

            db = sqlite3.connect(runtime_dir / "runtime.sqlite3")
            try:
                stored_run = db.execute(
                    "select run_id, project_id, state, risk_level from runs where run_id = ?",
                    (run.run_id,),
                ).fetchone()
                stored_events = db.execute(
                    "select to_state from runtime_events where run_id = ? order by rowid",
                    (run.run_id,),
                ).fetchall()
            finally:
                db.close()

            self.assertEqual(stored_run, (run.run_id, run.project_id, "ready", "low"))
            self.assertEqual([row[0] for row in stored_events], ["received", "classified", "planned", "ready"])

    def test_runtime_store_loads_run_from_sqlite_when_json_snapshot_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-sqlite-authority",
                    title="SQLite authority",
                    actor_id="actor-operator",
                    requested_outcome="Load from SQLite.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            snapshot = root / ".agencyos-runtime" / "runs" / f"{run.run_id}.json"
            snapshot.unlink()

            loaded = kernel.store.load(run.run_id)

            self.assertEqual(loaded.run_id, run.run_id)
            self.assertEqual(loaded.project_id, run.project_id)
            self.assertEqual(loaded.state.value, "ready")

    def test_runtime_store_replays_events_from_sqlite_when_jsonl_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-sqlite-events",
                    title="SQLite events",
                    actor_id="actor-operator",
                    requested_outcome="Replay from SQLite.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            event_log = root / ".agencyos-runtime" / "runs" / f"{run.run_id}.events.jsonl"
            event_log.unlink()

            events = kernel.replay(run.run_id)

            self.assertEqual([event.to_state.value for event in events], ["received", "classified", "planned", "ready"])

    def test_runtime_store_validates_sqlite_payload_before_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-pydantic-boundary",
                    title="Pydantic boundary",
                    actor_id="actor-operator",
                    requested_outcome="Validate runtime payload.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            db = sqlite3.connect(root / ".agencyos-runtime" / "runtime.sqlite3")
            try:
                payload = db.execute(
                    "select payload_json from runs where run_id = ?",
                    (run.run_id,),
                ).fetchone()[0]
                data = json.loads(payload)
                data.pop("request")
                db.execute(
                    "update runs set payload_json = ? where run_id = ?",
                    (json.dumps(data), run.run_id),
                )
                db.commit()
            finally:
                db.close()

            with self.assertRaisesRegex(ValueError, "schema_validation_error"):
                kernel.store.load(run.run_id)

    def test_policy_decisions_are_queryable_in_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-policy-sqlite",
                    title="Policy sqlite",
                    actor_id="actor-operator",
                    requested_outcome="Attempt unknown action.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            run.packets[0].capability = "delete_project"
            kernel.store.save(run)

            with self.assertRaises(Exception):
                kernel.dispatch_ready(run.run_id)

            db = sqlite3.connect(root / ".agencyos-runtime" / "runtime.sqlite3")
            try:
                row = db.execute(
                    """
                    select requested_action, outcome, reason
                    from policy_decisions
                    where run_id = ?
                    """,
                    (run.run_id,),
                ).fetchone()
            finally:
                db.close()

            self.assertEqual(row[0], "delete_project")
            self.assertEqual(row[1], "block")
            self.assertIn("No policy permits", row[2])

    def test_claim_records_are_queryable_in_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-claim-sqlite",
                    title="Claim sqlite",
                    actor_id="actor-operator",
                    requested_outcome="Create claim records.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            completed = kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=["SUPPORTED::Reports frequently require manual correction."],
            )

            db = sqlite3.connect(root / ".agencyos-runtime" / "runtime.sqlite3")
            try:
                row = db.execute(
                    """
                    select claim_id, artifact_id, text, evidence_status, evidence_ids_json
                    from claim_records
                    where run_id = ?
                    """,
                    (run.run_id,),
                ).fetchone()
            finally:
                db.close()

            self.assertEqual(row[0], completed.claim_records[-1].claim_id)
            self.assertEqual(row[1], completed.artifacts[-1].artifact_id)
            self.assertEqual(row[2], "Reports frequently require manual correction.")
            self.assertEqual(row[3], "supported")
            self.assertEqual(row[4], "[]")


if __name__ == "__main__":
    unittest.main()
