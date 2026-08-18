import tempfile
import unittest
from pathlib import Path

from agencyos.policy_registry import PolicyRegistry
from tools.enforcement_kernel import EnforcementKernel, KernelRequest, LifecycleState, TransitionError


class EnforcementKernelPolicyWiringPriority3Tests(unittest.TestCase):
    def test_unknown_packet_action_is_blocked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-policy-block",
                    title="Unknown action",
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

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("No policy permits", blocked.block_reason)

    def test_external_send_packet_holds_before_dispatch_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            kernel.policy_registry = PolicyRegistry(
                version=kernel.policy_registry.version,
                rules=[rule for rule in kernel.policy_registry.rules if "closeout" not in rule.actions],
            )
            run = kernel.start(
                KernelRequest(
                    request_id="req-policy-hold",
                    title="External draft action",
                    actor_id="actor-operator",
                    requested_outcome="Prepare an external send action.",
                    action_class="external_send",
                    reversible=True,
                    external=True,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            run.packets = kernel.router.create_packets(run.request)
            run.packets[0].capability = "external_send"
            run.runnable_packets = run.packets
            run.state = LifecycleState.READY
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            held = kernel.store.load(run.run_id)
            self.assertEqual(held.state, LifecycleState.AWAITING_HUMAN)
            self.assertIn("External action requires explicit human approval", held.block_reason)

    def test_release_requires_approval_scoped_to_release_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-release-scope",
                    title="External release",
                    actor_id="actor-operator",
                    requested_outcome="Release external artifact.",
                    action_class="external_send",
                    reversible=False,
                    external=True,
                    sensitive=True,
                    required_workstreams=["pitch"],
                )
            )
            kernel.record_human_approval(
                run.run_id,
                approver_id="human-kojie",
                decision="approved",
                rationale="Approved only for review.",
                exact_action="review draft",
            )

            with self.assertRaises(TransitionError):
                kernel.authorize_release(run.run_id, actor_id="human-kojie")

            held = kernel.store.load(run.run_id)
            self.assertEqual(held.state, LifecycleState.APPROVED)
            self.assertIn("release external", held.block_reason)

    def test_closeout_blocks_when_policy_has_no_closeout_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            kernel.policy_registry = PolicyRegistry(
                version=kernel.policy_registry.version,
                rules=[rule for rule in kernel.policy_registry.rules if "closeout" not in rule.actions],
            )
            run = kernel.start(
                KernelRequest(
                    request_id="req-closeout-policy",
                    title="Closeout policy",
                    actor_id="actor-operator",
                    requested_outcome="Create internal artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(run.run_id, "research", "research.md", "Research output", actor_id="actor-research")
            kernel.create_handoff(run.run_id, actor_id="actor-operator")
            kernel.verify(run.run_id, reviewer_id="actor-verifier")

            with self.assertRaises(TransitionError):
                kernel.request_closeout(run.run_id, actor_id="actor-operator")

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("No policy permits", blocked.block_reason)

    def test_sensitive_evidence_attachment_requires_human_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-sensitive-evidence",
                    title="Sensitive evidence",
                    actor_id="actor-operator",
                    requested_outcome="Attach sensitive evidence.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                    evidence_required_for=["research"],
                )
            )
            run.packets = kernel.router.create_packets(run.request)
            run.runnable_packets = run.packets
            run.state = LifecycleState.READY
            kernel.store.save(run)
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(run.run_id, "research", "research.md", "Research output", actor_id="actor-research")
            kernel.create_handoff(run.run_id, actor_id="actor-operator")

            with self.assertRaises(TransitionError):
                kernel.attach_evidence(
                    run.run_id,
                    "research",
                    "evidence/sensitive-client-spend.csv",
                    "Sensitive client spend evidence.",
                    actor_id="actor-evidence",
                )

            held = kernel.store.load(run.run_id)
            self.assertEqual(held.state, LifecycleState.AWAITING_HUMAN)
            self.assertIn("Sensitive evidence requires human approval", held.block_reason)

    def test_verification_blocks_without_independent_review_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            kernel.policy_registry = PolicyRegistry(
                version=kernel.policy_registry.version,
                rules=[rule for rule in kernel.policy_registry.rules if "verify" not in rule.actions],
            )
            run = kernel.start(
                KernelRequest(
                    request_id="req-verify-policy",
                    title="Verification policy",
                    actor_id="actor-operator",
                    requested_outcome="Verify artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(run.run_id, "research", "research.md", "Research output", actor_id="actor-research")
            kernel.create_handoff(run.run_id, actor_id="actor-operator")

            with self.assertRaises(TransitionError):
                kernel.verify(run.run_id, reviewer_id="actor-verifier")

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("No policy permits", blocked.block_reason)

    def test_memory_write_is_blocked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-memory-write",
                    title="Memory write",
                    actor_id="actor-operator",
                    requested_outcome="Attempt persistent memory write.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            run.packets[0].capability = "memory_write"
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("Memory writes require explicit policy and approval", blocked.block_reason)

    def test_governance_policy_change_is_blocked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-governance-change",
                    title="Governance change",
                    actor_id="actor-operator",
                    requested_outcome="Attempt governance policy change.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            run.packets[0].capability = "governance_policy_change"
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("Governance policy changes require designated authority", blocked.block_reason)

    def test_destructive_action_is_blocked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-destructive",
                    title="Destructive action",
                    actor_id="actor-operator",
                    requested_outcome="Attempt destructive action.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            run.packets[0].capability = "destructive_action"
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("Destructive actions require exact target authorization", blocked.block_reason)

    def test_blocked_dispatch_persists_policy_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-policy-record",
                    title="Policy decision record",
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

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.policy_decisions[-1].requested_action, "delete_project")
            self.assertEqual(blocked.policy_decisions[-1].outcome, "block")

    def test_expired_release_approval_cannot_authorize_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-expired-release",
                    title="Expired release",
                    actor_id="actor-operator",
                    requested_outcome="Release external artifact.",
                    action_class="external_send",
                    reversible=False,
                    external=True,
                    sensitive=True,
                    required_workstreams=["pitch"],
                )
            )
            kernel.record_human_approval(
                run.run_id,
                approver_id="human-kojie",
                decision="approved",
                rationale="Expired approval.",
                exact_action="release external",
                expires_at="2000-01-01T00:00:00+00:00",
            )

            with self.assertRaises(TransitionError):
                kernel.authorize_release(run.run_id, actor_id="human-kojie")

            held = kernel.store.load(run.run_id)
            self.assertEqual(held.state, LifecycleState.APPROVED)
            self.assertIn("expired", held.block_reason.lower())

    def test_release_approval_for_stale_artifact_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-stale-hash-release",
                    title="Stale artifact hash",
                    actor_id="actor-operator",
                    requested_outcome="Release external artifact.",
                    action_class="external_send",
                    reversible=False,
                    external=True,
                    sensitive=True,
                    required_workstreams=["pitch"],
                )
            )
            run.state = LifecycleState.APPROVED
            run.human_approval_by = "human-kojie"
            run.approval_records.append(
                kernel.make_approval_record(
                    approver_id="human-kojie",
                    decision="approved",
                    rationale="Approved old artifact.",
                    exact_action="release external",
                    approved_artifact_hash="sha256:old",
                )
            )
            run.artifacts.append(
                kernel.make_artifact(
                    workstream_id="pitch",
                    path="pitch.md",
                    content="Changed artifact",
                    actor_id="actor-pitch",
                )
            )
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.authorize_release(run.run_id, actor_id="human-kojie")

            held = kernel.store.load(run.run_id)
            self.assertIn("artifact hash", held.block_reason.lower())

    def test_denied_tool_use_is_blocked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-denied-tool",
                    title="Denied tool",
                    actor_id="actor-operator",
                    requested_outcome="Attempt denied tool use.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            run.packets[0].granted_permissions = ["read_context"]
            run.packets[0].capability = "tool:send_email"
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("Tool use requires explicit permission", blocked.block_reason)

    def test_public_boundary_with_sensitive_request_is_blocked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-public-boundary",
                    title="Public boundary",
                    actor_id="actor-operator",
                    requested_outcome="Attempt public deliverable with sensitive data.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=True,
                    required_workstreams=["research"],
                )
            )
            run.packets = kernel.router.create_packets(run.request)
            run.packets[0].capability = "write_public_artifact"
            run.packets[0].granted_permissions = ["read_context", "write_public_artifact"]
            run.runnable_packets = run.packets
            run.state = LifecycleState.READY
            kernel.store.save(run)

            with self.assertRaises(TransitionError):
                kernel.dispatch_ready(run.run_id)

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("Sensitive data cannot cross public boundary", blocked.block_reason)


if __name__ == "__main__":
    unittest.main()
