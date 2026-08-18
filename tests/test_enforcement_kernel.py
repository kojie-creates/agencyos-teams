import tempfile
import unittest
from pathlib import Path

from tools.enforcement_kernel import (
    EnforcementKernel,
    KernelRequest,
    LifecycleState,
    RiskLevel,
    TransitionError,
)


class EnforcementKernelTests(unittest.TestCase):
    def test_internal_reversible_request_blocks_closeout_until_evidence_then_closes(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            request = KernelRequest(
                request_id="req-internal-demo",
                title="Create internal reversible demo artifacts",
                actor_id="actor-operator",
                requested_outcome="Create two local internal artifacts with evidence.",
                action_class="internal_artifact",
                reversible=True,
                external=False,
                sensitive=False,
                required_workstreams=["research", "build"],
                evidence_required_for=["build"],
            )

            run = kernel.start(request)

            self.assertEqual(run.risk_level, RiskLevel.LOW)
            self.assertEqual([packet.workstream_id for packet in run.runnable_packets], ["research", "build"])
            self.assertEqual(run.execution_mode, "deterministic_batches")

            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(run.run_id, "research", "research.md", "Research output", actor_id="actor-research")
            kernel.complete_artifact(run.run_id, "build", "build.md", "Build output", actor_id="actor-build")
            kernel.create_handoff(run.run_id, actor_id="actor-operator")

            blocked = kernel.request_closeout(run.run_id, actor_id="actor-operator")
            self.assertEqual(blocked.state, LifecycleState.EVIDENCE_REQUIRED)
            self.assertIn("build", blocked.missing_evidence)

            kernel.attach_evidence(run.run_id, "build", "evidence/build-proof.txt", "Build proof", actor_id="actor-evidence")
            reviewed = kernel.verify(run.run_id, reviewer_id="actor-verifier")
            self.assertEqual(reviewed.state, LifecycleState.APPROVED)

            closed = kernel.request_closeout(run.run_id, actor_id="actor-operator")
            self.assertEqual(closed.state, LifecycleState.CLOSED)

            replay = kernel.replay(run.run_id)
            self.assertEqual(replay[-1].to_state, LifecycleState.CLOSED)
            self.assertTrue(any(event.to_state == LifecycleState.EVIDENCE_REQUIRED for event in replay))
            self.assertIn("closed", kernel.status_report(run.run_id).lower())

    def test_high_risk_external_request_pauses_at_human_gate_and_cannot_release_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            request = KernelRequest(
                request_id="req-external-demo",
                title="Send public property manager pitch",
                actor_id="actor-operator",
                requested_outcome="Send a Toya and Cirrus facing pilot pitch.",
                action_class="external_send",
                reversible=False,
                external=True,
                sensitive=True,
                required_workstreams=["pitch"],
            )

            run = kernel.start(request)

            self.assertEqual(run.risk_level, RiskLevel.HIGH)
            self.assertEqual(run.state, LifecycleState.AWAITING_HUMAN)
            with self.assertRaises(TransitionError):
                kernel.authorize_release(run.run_id, actor_id="actor-operator")

            approved = kernel.record_human_approval(
                run.run_id,
                approver_id="human-kojie",
                decision="approved",
                rationale="Approved sanitized demo release.",
            )
            self.assertEqual(approved.state, LifecycleState.APPROVED)

            release_ready = kernel.authorize_release(run.run_id, actor_id="human-kojie")
            self.assertEqual(release_ready.state, LifecycleState.RELEASE_READY)

    def test_rejects_illegal_transition(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            request = KernelRequest(
                request_id="req-illegal",
                title="Illegal transition demo",
                actor_id="actor-operator",
                requested_outcome="Try to close before handoff.",
                action_class="internal_artifact",
                reversible=True,
                external=False,
                sensitive=False,
                required_workstreams=["one"],
            )
            run = kernel.start(request)

            with self.assertRaises(TransitionError):
                kernel.transition(run.run_id, LifecycleState.CLOSED, actor_id="actor-operator")

    def test_dependency_cycle_blocks_planning(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            request = KernelRequest(
                request_id="req-cycle",
                title="Cycle demo",
                actor_id="actor-operator",
                requested_outcome="Create cyclic packets.",
                action_class="internal_artifact",
                reversible=True,
                external=False,
                sensitive=False,
                required_workstreams=["a", "b"],
                dependencies={"a": ["b"], "b": ["a"]},
            )

            run = kernel.start(request)

            self.assertEqual(run.state, LifecycleState.BLOCKED)
            self.assertIn("cycle", run.block_reason.lower())


if __name__ == "__main__":
    unittest.main()
