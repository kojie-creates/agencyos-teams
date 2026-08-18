import tempfile
import unittest
from pathlib import Path

from agencyos.policy_registry import PolicyOutcome, PolicyRegistry


REPO_ROOT = Path(__file__).resolve().parents[1]


class PolicyRegistryPriority3Tests(unittest.TestCase):
    def test_default_policy_holds_external_send_without_human_approval(self):
        registry = PolicyRegistry.default()

        decision = registry.evaluate(
            actor_id="actor-operator",
            actor_roles=["operator"],
            action="external_send",
            resource="artifact-demo",
            risk_level="medium",
            evidence_ids=[],
            approval_ids=[],
        )

        self.assertEqual(decision.outcome, PolicyOutcome.HOLD)
        self.assertEqual(decision.required_approval, "human")
        self.assertIn("external_action_requires_human_approval", decision.applicable_rules)

    def test_default_policy_permits_internal_reversible_artifact_work(self):
        registry = PolicyRegistry.default()

        decision = registry.evaluate(
            actor_id="being-atlas",
            actor_roles=["research"],
            action="write_local_artifact",
            resource="project-demo",
            risk_level="low",
            evidence_ids=[],
            approval_ids=[],
        )

        self.assertEqual(decision.outcome, PolicyOutcome.PERMIT)

    def test_default_policy_blocks_unknown_actor_or_action(self):
        registry = PolicyRegistry.default()

        unknown_actor = registry.evaluate(
            actor_id="actor-unknown",
            actor_roles=[],
            action="write_local_artifact",
            resource="project-demo",
            risk_level="low",
            evidence_ids=[],
            approval_ids=[],
        )
        unknown_action = registry.evaluate(
            actor_id="being-atlas",
            actor_roles=["research"],
            action="delete_project",
            resource="project-demo",
            risk_level="low",
            evidence_ids=[],
            approval_ids=[],
        )

        self.assertEqual(unknown_actor.outcome, PolicyOutcome.BLOCK)
        self.assertEqual(unknown_action.outcome, PolicyOutcome.BLOCK)

    def test_policy_registry_loads_from_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(PolicyRegistry.default().to_json(), encoding="utf-8")

            registry = PolicyRegistry.from_json(path)

            self.assertEqual(registry.version, "agencyos.policy.v1")

    def test_checked_in_runtime_policy_loads(self):
        registry = PolicyRegistry.from_json(REPO_ROOT / "policies" / "runtime-policy.json")

        decision = registry.evaluate(
            actor_id="being-atlas",
            actor_roles=["research"],
            action="write_local_artifact",
            resource="project-demo",
            risk_level="low",
            evidence_ids=[],
            approval_ids=[],
        )

        self.assertEqual(decision.outcome, PolicyOutcome.PERMIT)


if __name__ == "__main__":
    unittest.main()
