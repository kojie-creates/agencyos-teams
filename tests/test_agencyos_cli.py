import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgencyOSCliTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", "agencyos", *args],
            cwd=str(cwd or REPO_ROOT),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_run_status_and_events_for_internal_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-internal",
                        "title": "Create internal local artifacts",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Create internal reversible outputs.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research", "build"],
                    }
                ),
                encoding="utf-8",
            )

            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))

            self.assertEqual(run["state"], "ready")
            self.assertEqual(run["risk_level"], "low")
            self.assertEqual(run["execution_mode"], "deterministic_batches")
            self.assertEqual(run["runnable_workstreams"], ["research", "build"])
            self.assertEqual(run["execution_batches"], [["research", "build"]])

            status = self.run_cli("status", "--root", str(root), "--run-id", run["run_id"])
            self.assertEqual(status["state"], "ready")
            self.assertEqual(status["next_actions"], ["dispatch_ready"])

            events = self.run_cli("events", "--root", str(root), "--run-id", run["run_id"])
            self.assertEqual(events["events"][0]["to_state"], "received")
            self.assertEqual(events["events"][-1]["to_state"], "ready")

    def test_high_risk_request_can_be_approved_but_not_by_non_human_actor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-high-risk",
                        "title": "Send external pitch",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Send an external pitch.",
                        "action_class": "external_send",
                        "reversible": False,
                        "external": True,
                        "sensitive": True,
                        "required_workstreams": ["pitch"],
                    }
                ),
                encoding="utf-8",
            )

            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            self.assertEqual(run["state"], "awaiting_human")
            self.assertEqual(run["risk_level"], "high")

            denied = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agencyos",
                    "approve",
                    "--root",
                    str(root),
                    "--run-id",
                    run["run_id"],
                    "--approver-id",
                    "actor-operator",
                    "--decision",
                    "approved",
                    "--rationale",
                    "Not a human actor.",
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(denied.returncode, 0)

            approved = self.run_cli(
                "approve",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--approver-id",
                "human-kojie",
                "--decision",
                "approved",
                "--rationale",
                "Approved for sanitized demo.",
            )
            self.assertEqual(approved["state"], "approved")

    def test_run_rejects_malformed_request_before_kernel_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-malformed",
                        "title": "Missing authority",
                        "actor_id": "actor-operator",
                        "requested_outcome": "This omits required_workstreams.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "-m", "agencyos", "run", "--root", str(root), "--request", str(request_path)],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("schema_validation_error", result.stderr)
            self.assertIn("required_workstreams", result.stderr)


if __name__ == "__main__":
    unittest.main()
