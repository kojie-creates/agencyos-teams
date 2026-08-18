import json
import hashlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgencyOSCliPriority1CompletionTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", "agencyos", *args],
            cwd=str(cwd or REPO_ROOT),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_cli_runs_priority1_workflow_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-p1-complete",
                        "title": "Create internal local artifacts",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Create internal reversible outputs.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research", "build"],
                        "evidence_required_for": ["build"],
                    }
                ),
                encoding="utf-8",
            )

            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            dispatched = self.run_cli("dispatch", "--root", str(root), "--run-id", run["run_id"])
            self.assertEqual(dispatched["state"], "in_progress")

            self.run_cli(
                "complete",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "research",
                "--path",
                "research.md",
                "--content",
                "Research output",
                "--actor-id",
                "actor-research",
                "--claim",
                "monthly_requests=16",
            )
            completed = self.run_cli(
                "complete",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "build",
                "--path",
                "build.md",
                "--content",
                "Build output",
                "--actor-id",
                "actor-build",
                "--claim",
                "monthly_requests=16",
            )
            self.assertEqual(completed["state"], "handoff_pending")
            state_path = root / ".agencyos-runtime" / "runs" / f"{run['run_id']}.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            artifact_path = root / state["artifacts"][0]["path"]
            self.assertEqual(artifact_path.read_text(encoding="utf-8"), "Research output")
            self.assertTrue(artifact_path.is_relative_to(root / ".agencyos-runtime" / "artifacts" / run["run_id"]))

            handoff = self.run_cli("handoff", "--root", str(root), "--run-id", run["run_id"], "--actor-id", "actor-operator")
            self.assertEqual(handoff["state"], "handoff_pending")

            blocked = self.run_cli("close", "--root", str(root), "--run-id", run["run_id"], "--actor-id", "actor-operator")
            self.assertEqual(blocked["state"], "evidence_required")

            evidenced = self.run_cli(
                "evidence",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "build",
                "--path",
                "evidence/build-proof.txt",
                "--summary",
                "Build proof",
                "--actor-id",
                "actor-evidence",
            )
            self.assertEqual(evidenced["state"], "under_review")

            verified = self.run_cli("verify", "--root", str(root), "--run-id", run["run_id"], "--reviewer-id", "actor-verifier")
            self.assertEqual(verified["state"], "approved")

            closed = self.run_cli("close", "--root", str(root), "--run-id", run["run_id"], "--actor-id", "actor-operator")
            self.assertEqual(closed["state"], "closed")

    def test_cli_reject_records_human_rejection_for_high_risk_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-p1-reject",
                        "title": "External send",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Send an external message.",
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
            rejected = self.run_cli(
                "reject",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--approver-id",
                "human-kojie",
                "--rationale",
                "Needs more evidence before release.",
            )

            self.assertEqual(rejected["state"], "rejected")

    def test_cli_runs_lists_sqlite_backed_runtime_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-p2-history",
                        "title": "Runtime history",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Create internal reversible outputs.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                    }
                ),
                encoding="utf-8",
            )

            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            history = self.run_cli("runs", "--root", str(root))

            self.assertEqual(history["runs"][0]["run_id"], run["run_id"])
            self.assertEqual(history["runs"][0]["state"], "ready")

    def test_cli_import_project_writes_registry_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "registry.json"

            result = self.run_cli(
                "import-project",
                "--project",
                "projects/diana-spend-reporting-assistant",
                "--output",
                str(output_path),
            )

            self.assertEqual(result["project_id"], "project-diana-spend-reporting-assistant")
            self.assertTrue(output_path.exists())

    def test_cli_policy_decisions_lists_sqlite_policy_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-policy-history",
                        "title": "Policy history",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Attempt unknown action.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                    }
                ),
                encoding="utf-8",
            )
            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))

            db_path = root / ".agencyos-runtime" / "runtime.sqlite3"
            db = sqlite3.connect(db_path)
            try:
                data = json.loads(
                    db.execute(
                        "select payload_json from runs where run_id = ?",
                        (run["run_id"],),
                    ).fetchone()[0]
                )
            finally:
                db.close()
            data["packets"][0]["capability"] = "delete_project"
            data["runnable_packets"][0]["capability"] = "delete_project"
            db = sqlite3.connect(db_path)
            try:
                db.execute(
                    "update runs set payload_json = ? where run_id = ?",
                    (json.dumps(data), run["run_id"]),
                )
                db.commit()
            finally:
                db.close()

            subprocess.run(
                [sys.executable, "-m", "agencyos", "dispatch", "--root", str(root), "--run-id", run["run_id"]],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
            )
            decisions = self.run_cli("policy-decisions", "--root", str(root), "--run-id", run["run_id"])

            self.assertEqual(decisions["policy_decisions"][0]["requested_action"], "delete_project")
            self.assertEqual(decisions["policy_decisions"][0]["outcome"], "block")

    def test_cli_claim_records_lists_sqlite_claim_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-claim-history",
                        "title": "Claim history",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Create claim records.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                    }
                ),
                encoding="utf-8",
            )
            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            self.run_cli("dispatch", "--root", str(root), "--run-id", run["run_id"])
            self.run_cli(
                "complete",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "research",
                "--path",
                "research.md",
                "--content",
                "Research output",
                "--actor-id",
                "actor-research",
                "--claim",
                "SUPPORTED::Reports frequently require manual correction.",
            )

            claims = self.run_cli("claim-records", "--root", str(root), "--run-id", run["run_id"])

            self.assertEqual(claims["claim_records"][0]["text"], "Reports frequently require manual correction.")
            self.assertEqual(claims["claim_records"][0]["evidence_status"], "supported")

    def test_cli_evidence_can_target_claim_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-target-claim",
                        "title": "Target claim evidence",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Attach evidence to selected claim.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                        "evidence_required_for": ["research"],
                    }
                ),
                encoding="utf-8",
            )
            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            self.run_cli("dispatch", "--root", str(root), "--run-id", run["run_id"])
            self.run_cli(
                "complete",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "research",
                "--path",
                "research.md",
                "--content",
                "Research output",
                "--actor-id",
                "actor-research",
                "--claim",
                "SUPPORTED::Reports frequently require manual correction.",
                "--claim",
                "SUPPORTED::Request history includes completed dates.",
            )
            before = self.run_cli("claim-records", "--root", str(root), "--run-id", run["run_id"])
            target_claim_id = before["claim_records"][0]["claim_id"]

            self.run_cli(
                "evidence",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "research",
                "--path",
                "evidence/request-history.csv",
                "--summary",
                "Request history export.",
                "--actor-id",
                "actor-evidence",
                "--claim-id",
                target_claim_id,
            )
            after = self.run_cli("claim-records", "--root", str(root), "--run-id", run["run_id"])

            self.assertEqual(len(after["claim_records"][0]["evidence_ids"]), 1)
            self.assertEqual(after["claim_records"][1]["evidence_ids"], [])

    def test_cli_model_draft_writes_local_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-model-draft",
                        "title": "Model draft",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Draft with model adapter.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                    }
                ),
                encoding="utf-8",
            )
            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            self.run_cli("dispatch", "--root", str(root), "--run-id", run["run_id"])

            drafted = self.run_cli(
                "model-draft",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "research",
                "--path",
                "drafts/research.md",
                "--prompt",
                "summarize request",
                "--model",
                "gpt-local-draft",
                "--actor-id",
                "actor-research",
            )

            self.assertEqual(drafted["state"], "handoff_pending")
            state_path = root / ".agencyos-runtime" / "runs" / f"{run['run_id']}.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            artifact_path = root / state["artifacts"][0]["path"]
            self.assertIn("[gpt-local-draft draft]", artifact_path.read_text(encoding="utf-8"))
            model_calls = self.run_cli("model-calls", "--root", str(root), "--run-id", run["run_id"])
            self.assertEqual(len(model_calls["model_call_records"]), 1)
            self.assertEqual(model_calls["model_call_records"][0]["provider"], "local_model_draft")
            self.assertEqual(model_calls["model_call_records"][0]["result"], "success")
            self.assertEqual(model_calls["model_call_records"][0]["artifact_id"], state["artifacts"][0]["artifact_id"])

    def test_cli_model_draft_blocks_disabled_openai_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-model-openai-disabled",
                        "title": "OpenAI disabled",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Try disabled OpenAI model adapter.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                    }
                ),
                encoding="utf-8",
            )
            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            self.run_cli("dispatch", "--root", str(root), "--run-id", run["run_id"])

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agencyos",
                    "model-draft",
                    "--root",
                    str(root),
                    "--run-id",
                    run["run_id"],
                    "--workstream-id",
                    "research",
                    "--path",
                    "drafts/research.md",
                    "--prompt",
                    "summarize request",
                    "--model",
                    "gpt-5.6-luna",
                    "--provider",
                    "openai",
                    "--actor-id",
                    "actor-research",
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Model provider openai is not enabled", result.stderr)
            failure_packets = self.run_cli("failure-packets", "--root", str(root), "--run-id", run["run_id"])
            self.assertEqual(len(failure_packets["failure_packets"]), 1)
            self.assertEqual(failure_packets["failure_packets"][0]["error_type"], "model_policy_error")
            self.assertEqual(failure_packets["failure_packets"][0]["resolution"], "blocked")
            model_calls = self.run_cli("model-calls", "--root", str(root), "--run-id", run["run_id"])
            self.assertEqual(len(model_calls["model_call_records"]), 1)
            self.assertEqual(model_calls["model_call_records"][0]["result"], "failure")

    def test_cli_export_run_writes_portable_proof_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export_path = root / "exports" / "run-export.json"
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": "cli-export",
                        "title": "Export run",
                        "actor_id": "actor-operator",
                        "requested_outcome": "Export proof bundle.",
                        "action_class": "internal_artifact",
                        "reversible": True,
                        "external": False,
                        "sensitive": False,
                        "required_workstreams": ["research"],
                    }
                ),
                encoding="utf-8",
            )
            run = self.run_cli("run", "--root", str(root), "--request", str(request_path))
            self.run_cli("dispatch", "--root", str(root), "--run-id", run["run_id"])
            self.run_cli(
                "complete",
                "--root",
                str(root),
                "--run-id",
                run["run_id"],
                "--workstream-id",
                "research",
                "--path",
                "research.md",
                "--content",
                "Research output",
                "--actor-id",
                "actor-research",
                "--claim",
                "SUPPORTED::Reports frequently require manual correction.",
            )

            exported = self.run_cli("export-run", "--root", str(root), "--run-id", run["run_id"], "--output", str(export_path))

            self.assertEqual(exported["run_id"], run["run_id"])
            self.assertEqual(exported["output"], str(export_path))
            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(bundle["run"]["run_id"], run["run_id"])
            self.assertEqual(bundle["manifest"]["schema_version"], "agencyos.export.manifest.v1")
            self.assertEqual(bundle["manifest"]["counts"]["artifacts"], 1)
            self.assertEqual(bundle["manifest"]["counts"]["model_call_records"], 0)
            self.assertEqual(bundle["manifest"]["counts"]["failure_packets"], 0)
            self.assertEqual(bundle["manifest"]["counts"]["closeout_records"], 0)
            self.assertEqual(bundle["manifest"]["counts"]["learning_records"], 0)
            self.assertEqual(bundle["model_call_records"], [])
            self.assertEqual(bundle["failure_packets"], [])
            self.assertEqual(bundle["manifest"]["artifact_hashes"], [bundle["artifacts"][0]["content_hash"]])
            self.assertTrue(bundle["manifest"]["bundle_hash"].startswith("sha256:"))
            self.assertEqual(bundle["artifacts"][0]["content_hash"][:7], "sha256:")
            self.assertEqual(bundle["claim_records"][0]["evidence_status"], "supported")

            verified = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(verified["valid"], True)
            self.assertEqual(verified["bundle_hash"], bundle["manifest"]["bundle_hash"])

            bundle["artifacts"][0]["content"] = "Tampered output"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            tampered = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(tampered["valid"], False)
            self.assertIn("bundle_hash", tampered["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["artifacts"][0]["content"] = "Research output"
            bundle["manifest"]["counts"]["artifacts"] = 999
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            forged_result = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(forged_result["valid"], False)
            self.assertEqual(forged_result["counts_valid"], False)
            self.assertIn("counts", forged_result["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["manifest"]["counts"]["artifacts"] = 1
            bundle["artifacts"][0]["content"] = "Tampered but manifest hash recomputed"
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            content_tampered = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(content_tampered["valid"], False)
            self.assertEqual(content_tampered["artifact_content_hashes_valid"], False)
            self.assertIn("artifact_content_hashes", content_tampered["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["schema_version"] = "agencyos.export.v99"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            wrong_version = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(wrong_version["valid"], False)
            self.assertEqual(wrong_version["schema_valid"], False)
            self.assertIn("schema", wrong_version["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["schema_version"] = "agencyos.export.v1"
            bundle["events"][1]["from_state"] = "closed"
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            bad_events = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(bad_events["valid"], False)
            self.assertEqual(bad_events["event_chain_valid"], False)
            self.assertIn("event_chain", bad_events["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["events"][1]["from_state"] = "received"
            bundle["run"]["state"] = "closed"
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            bad_final_state = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(bad_final_state["valid"], False)
            self.assertEqual(bad_final_state["run_state_valid"], False)
            self.assertIn("run_state", bad_final_state["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["run"]["state"] = bundle["events"][-1]["to_state"]
            bundle.pop("claim_records")
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            bundle["manifest"]["counts"]["claim_records"] = 0
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            missing_section = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(missing_section["valid"], False)
            self.assertEqual(missing_section["required_sections_valid"], False)
            self.assertIn("required_sections", missing_section["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["claim_records"] = [
                {
                    "claim_id": "claim-forged",
                    "artifact_id": "artifact-missing",
                    "text": "Forged claim.",
                    "evidence_status": "supported",
                    "evidence_ids": [],
                    "claim_type": "general",
                    "required_approval": None,
                }
            ]
            bundle["manifest"]["counts"]["claim_records"] = 1
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            bad_claim_refs = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(bad_claim_refs["valid"], False)
            self.assertEqual(bad_claim_refs["references_valid"], False)
            self.assertIn("references", bad_claim_refs["failed_checks"])

            bundle = json.loads(export_path.read_text(encoding="utf-8"))
            bundle["claim_records"][0]["artifact_id"] = bundle["artifacts"][0]["artifact_id"]
            bundle["artifacts"].append(dict(bundle["artifacts"][0]))
            bundle["manifest"]["counts"]["artifacts"] = 2
            bundle["manifest"]["artifact_hashes"] = [artifact["content_hash"] for artifact in bundle["artifacts"]]
            forged = dict(bundle)
            forged.pop("manifest", None)
            hash_input = json.dumps(forged, sort_keys=True, separators=(",", ":"))
            bundle["manifest"]["bundle_hash"] = f"sha256:{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()}"
            export_path.write_text(json.dumps(bundle), encoding="utf-8")
            duplicate_ids = self.run_cli("verify-export", "--input", str(export_path))

            self.assertEqual(duplicate_ids["valid"], False)
            self.assertEqual(duplicate_ids["duplicate_ids_valid"], False)
            self.assertIn("duplicate_ids", duplicate_ids["failed_checks"])


if __name__ == "__main__":
    unittest.main()
