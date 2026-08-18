import tempfile
import unittest
from pathlib import Path

from tools.enforcement_kernel import EnforcementKernel, KernelRequest, LifecycleState, TransitionError


class EvidenceLockPriority4Tests(unittest.TestCase):
    def test_verification_rejects_artifact_content_changed_after_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-evidence-lock-hash",
                    title="Evidence lock hash",
                    actor_id="actor-operator",
                    requested_outcome="Verify artifact hash.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(run.run_id, "research", "research.md", "Original output", actor_id="actor-research")
            kernel.create_handoff(run.run_id, actor_id="actor-operator")

            tampered = kernel.store.load(run.run_id)
            tampered.artifacts[0].content = "Changed after artifact hash was recorded"
            kernel.store.save(tampered)

            with self.assertRaises(TransitionError):
                kernel.verify(run.run_id, reviewer_id="actor-verifier")

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("artifact hash", blocked.block_reason.lower())

    def test_verification_records_reviewed_artifact_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-verification-record",
                    title="Verification record",
                    actor_id="actor-operator",
                    requested_outcome="Record verification hash.",
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

            verified = kernel.verify(run.run_id, reviewer_id="actor-verifier")

            self.assertEqual(verified.verification_records[-1].artifact_hash, verified.artifacts[0].content_hash)
            self.assertEqual(verified.verification_records[-1].verifier_id, "actor-verifier")

    def test_verification_blocks_unknown_required_claim_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-claim-lock",
                    title="Claim evidence lock",
                    actor_id="actor-operator",
                    requested_outcome="Verify claim evidence.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=["UNKNOWN::Actual production pipeline is confirmed."],
            )
            kernel.create_handoff(run.run_id, actor_id="actor-operator")

            with self.assertRaises(TransitionError):
                kernel.verify(run.run_id, reviewer_id="actor-verifier")

            blocked = kernel.store.load(run.run_id)
            self.assertEqual(blocked.state, LifecycleState.BLOCKED)
            self.assertIn("claim evidence", blocked.block_reason.lower())

    def test_verification_allows_supported_required_claim_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-claim-supported",
                    title="Supported claim evidence lock",
                    actor_id="actor-operator",
                    requested_outcome="Verify supported claim evidence.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=["SUPPORTED::Reports frequently require manual correction."],
            )
            kernel.create_handoff(run.run_id, actor_id="actor-operator")

            verified = kernel.verify(run.run_id, reviewer_id="actor-verifier")

            self.assertEqual(verified.state, LifecycleState.APPROVED)

    def test_completed_artifact_creates_first_class_claim_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-claim-records",
                    title="Claim records",
                    actor_id="actor-operator",
                    requested_outcome="Create typed claims.",
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

            self.assertEqual(completed.claim_records[-1].text, "Reports frequently require manual correction.")
            self.assertEqual(completed.claim_records[-1].evidence_status, "supported")
            self.assertEqual(completed.claim_records[-1].artifact_id, completed.artifacts[-1].artifact_id)

    def test_evidence_attachment_links_to_claim_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-claim-evidence-link",
                    title="Claim evidence link",
                    actor_id="actor-operator",
                    requested_outcome="Link claim records to evidence.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                    evidence_required_for=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=["SUPPORTED::Reports frequently require manual correction."],
            )

            with_evidence = kernel.attach_evidence(
                run.run_id,
                "research",
                "evidence/research-proof.txt",
                "Resident portal request history export.",
                actor_id="actor-evidence",
            )

            self.assertEqual(with_evidence.claim_records[-1].evidence_ids, [with_evidence.evidence[-1].evidence_id])

    def test_evidence_attachment_can_target_specific_claim_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-targeted-claim-evidence",
                    title="Targeted claim evidence",
                    actor_id="actor-operator",
                    requested_outcome="Link evidence to selected claims.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                    evidence_required_for=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            completed = kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=[
                    "SUPPORTED::Reports frequently require manual correction.",
                    "SUPPORTED::Request history includes completed dates.",
                ],
            )

            with_evidence = kernel.attach_evidence(
                run.run_id,
                "research",
                "evidence/request-history.csv",
                "Request history export.",
                actor_id="actor-evidence",
                claim_ids=[completed.claim_records[0].claim_id],
            )

            self.assertEqual(with_evidence.claim_records[0].evidence_ids, [with_evidence.evidence[-1].evidence_id])
            self.assertEqual(with_evidence.claim_records[1].evidence_ids, [])

    def test_reconciliation_flags_conflicting_claim_record_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-claim-status-conflict",
                    title="Claim status conflict",
                    actor_id="actor-operator",
                    requested_outcome="Reconcile conflicting claim statuses.",
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
                claims=["SUPPORTED::Request history includes completed dates."],
            )
            kernel.complete_artifact(
                run.run_id,
                "build",
                "build.md",
                "Build output",
                actor_id="actor-build",
                claims=["UNKNOWN::Request history includes completed dates."],
            )

            reconciled = kernel.create_handoff(run.run_id, actor_id="actor-operator")

            self.assertEqual(reconciled.reconciliation_records[-1].state, "awaiting_human_decision")
            self.assertIn("claim_status:request history includes completed dates.", reconciled.reconciliation_records[-1].conflict_keys)

    def test_evidence_summary_exact_phrase_links_only_matching_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = EnforcementKernel(Path(tmp))
            run = kernel.start(
                KernelRequest(
                    request_id="req-summary-claim-match",
                    title="Summary claim match",
                    actor_id="actor-operator",
                    requested_outcome="Match evidence summary to claim text.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                    evidence_required_for=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)
            kernel.complete_artifact(
                run.run_id,
                "research",
                "research.md",
                "Research output",
                actor_id="actor-research",
                claims=[
                    "SUPPORTED::Reports frequently require manual correction.",
                    "SUPPORTED::Request history includes completed dates.",
                ],
            )

            with_evidence = kernel.attach_evidence(
                run.run_id,
                "research",
                "evidence/request-history.csv",
                "The export shows request history includes completed dates.",
                actor_id="actor-evidence",
            )

            self.assertEqual(with_evidence.claim_records[0].evidence_ids, [])
            self.assertEqual(with_evidence.claim_records[1].evidence_ids, [with_evidence.evidence[-1].evidence_id])


if __name__ == "__main__":
    unittest.main()
