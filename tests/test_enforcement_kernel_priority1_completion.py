import json
import tempfile
import unittest
from pathlib import Path

from tools.enforcement_kernel import EnforcementKernel, KernelRequest, LifecycleState, RiskLevel


class EnforcementKernelPriority1CompletionTests(unittest.TestCase):
    def test_plain_language_without_required_fields_routes_to_intake_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))

            run = kernel.start_plain_text(
                "Help with this project.",
                actor_id="actor-operator",
                human_owner_id="human-kojie",
            )

            self.assertEqual(run.state, LifecycleState.INTAKE_REQUIRED)
            self.assertIn("requested_outcome", run.intake_required)
            self.assertIn("required_workstreams", run.intake_required)

    def test_project_resolution_uses_explicit_first_run_or_authorized_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".first-run.json").write_text(json.dumps({"project_id": "project-first-run"}), encoding="utf-8")
            kernel = EnforcementKernel(root)

            explicit = kernel.start(
                KernelRequest(
                    request_id="req-explicit-project",
                    title="Explicit project",
                    actor_id="actor-operator",
                    requested_outcome="Create a local artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                    existing_project_ref="project-explicit",
                )
            )
            self.assertEqual(explicit.project_id, "project-explicit")

            first_run = kernel.start(
                KernelRequest(
                    request_id="req-first-run-project",
                    title="First-run project",
                    actor_id="actor-operator",
                    requested_outcome="Create a local artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            self.assertEqual(first_run.project_id, "project-first-run")

            created = kernel.start(
                KernelRequest(
                    request_id="req-create-project",
                    title="Create project",
                    actor_id="actor-operator",
                    requested_outcome="Create a local artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                    create_project=True,
                    project_slug="demo-project",
                    human_owner_id="human-kojie",
                )
            )
            self.assertEqual(created.project_id, "project-demo-project")

    def test_routing_adds_registry_assignment_permissions_and_pause_conditions(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))

            run = kernel.start(
                KernelRequest(
                    request_id="req-routing",
                    title="Routing demo",
                    actor_id="actor-operator",
                    requested_outcome="Create local research and evidence artifacts.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research", "evidence"],
                    evidence_required_for=["evidence"],
                )
            )

            assignments = {packet.workstream_id: packet for packet in run.packets}
            self.assertEqual(assignments["research"].actor_id, "being-atlas")
            self.assertEqual(assignments["evidence"].actor_id, "being-vera")
            self.assertIn("write_local_artifact", assignments["research"].granted_permissions)
            self.assertIn("external_send", assignments["research"].withheld_permissions)
            self.assertIn("missing_evidence", assignments["evidence"].pause_conditions)

    def test_failure_packet_retries_then_cancels_downstream_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-failure",
                    title="Failure demo",
                    actor_id="actor-operator",
                    requested_outcome="Create dependent local artifacts.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research", "build"],
                    dependencies={"build": ["research"]},
                )
            )

            kernel.dispatch_ready(run.run_id)
            retried = kernel.fail_work(
                run.run_id,
                "research",
                actor_id="being-atlas",
                error_type="tool_error",
                error_message="Temporary failure.",
                retryable=True,
            )
            self.assertEqual(retried.state, LifecycleState.READY)
            self.assertEqual(retried.failure_packets[-1].resolution, "retry_scheduled")

            kernel.dispatch_ready(run.run_id)
            failed = kernel.fail_work(
                run.run_id,
                "research",
                actor_id="being-atlas",
                error_type="tool_error",
                error_message="Repeated failure.",
                retryable=True,
            )
            self.assertEqual(failed.state, LifecycleState.CANCELLED)
            packet_states = {packet.workstream_id: packet.state for packet in failed.packets}
            self.assertEqual(packet_states["build"], LifecycleState.CANCELLED)

    def test_scheduler_records_dependency_safe_execution_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-batches",
                    title="Batch demo",
                    actor_id="actor-operator",
                    requested_outcome="Plan deterministic batches.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research", "design", "build"],
                    dependencies={"build": ["research", "design"]},
                )
            )

            self.assertEqual(run.execution_mode, "deterministic_batches")
            self.assertEqual(run.execution_batches, [["research", "design"], ["build"]])

    def test_conflicts_are_preserved_and_closeout_creates_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-conflict-closeout",
                    title="Conflict closeout demo",
                    actor_id="actor-operator",
                    requested_outcome="Create local artifacts with claims.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research", "build"],
                )
            )

            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=["monthly_requests=16"],
            )
            kernel.complete_artifact(
                run.run_id,
                "build",
                "build.md",
                "Build output",
                actor_id="actor-build",
                claims=["monthly_requests=20"],
            )
            reconciled = kernel.create_handoff(run.run_id, actor_id="actor-operator")
            self.assertEqual(reconciled.reconciliation_records[-1].state, "awaiting_human_decision")
            self.assertIn("monthly_requests", reconciled.reconciliation_records[-1].conflict_keys)

            kernel.verify(run.run_id, reviewer_id="actor-verifier")
            closed = kernel.request_closeout(run.run_id, actor_id="actor-operator")
            self.assertEqual(closed.state, LifecycleState.CLOSED)
            self.assertEqual(closed.closeout_records[-1].created_by, "actor-operator")
            self.assertEqual(closed.learning_records[-1].lesson, "generated_text_is_not_completion")

    def test_structured_human_approval_is_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-approval",
                    title="Approval demo",
                    actor_id="actor-operator",
                    requested_outcome="Send an external artifact.",
                    action_class="external_send",
                    reversible=False,
                    external=True,
                    sensitive=True,
                    required_workstreams=["pitch"],
                )
            )

            approved = kernel.record_human_approval(
                run.run_id,
                approver_id="human-kojie",
                decision="approved",
                rationale="Approved sanitized release.",
                exact_action="release external pitch",
                constraints=["sanitize resident data"],
                expires_at="2026-08-31T00:00:00+00:00",
            )

            reloaded = kernel.store.load(run.run_id)
            self.assertEqual(approved.state, LifecycleState.APPROVED)
            self.assertEqual(reloaded.approval_records[-1].exact_action, "release external pitch")
            self.assertEqual(reloaded.approval_records[-1].constraints, ["sanitize resident data"])
            self.assertEqual(reloaded.risk_level, RiskLevel.HIGH)


if __name__ == "__main__":
    unittest.main()
