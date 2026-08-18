import tempfile
import unittest
from pathlib import Path

from agencyos.project_importer import import_project_folder
from agencyos.schemas import Registry


class ProjectImportPriority2Tests(unittest.TestCase):
    def test_imports_diana_project_markdown_into_registry(self):
        project_path = Path("projects/diana-spend-reporting-assistant")

        registry = import_project_folder(project_path)

        self.assertIsInstance(registry, Registry)
        self.assertEqual(registry.projects[0].id, "project-diana-spend-reporting-assistant")
        self.assertEqual(registry.projects[0].name, "Diana Spend Reporting Assistant")
        self.assertEqual(registry.requests[0].desired_outcome, "Create a routed AgencyOS Teams project packet that turns the customer briefs into a practical recovery path for the spend reporting assistant.")
        self.assertEqual({workstream.name for workstream in registry.workstreams}, {"Source Synthesis", "Technical Diagnostic", "Executive Alignment", "Implementation Path"})
        self.assertEqual({being.id for being in registry.beings}, {"being-jaavis", "being-athena", "being-vera", "being-atlas", "being-bob", "being-miles"})
        self.assertTrue(registry.policies)
        self.assertTrue(registry.handoffs)
        self.assertEqual({item.source_ref for item in registry.evidence}, {"evidence/dev-team-diagnostic-responses.json", "evidence/dev-team-diagnostic-responses.md", "evidence/source-index.md"})
        self.assertEqual({artifact.path for artifact in registry.artifacts}, {"deliverables/customer-brief-synthesis.md", "deliverables/dev-team-diagnostic-memo.md"})
        self.assertTrue(all(artifact.content_hash.startswith("sha256:") for artifact in registry.artifacts))
        self.assertEqual(registry.closeouts[0].project_id, "project-diana-spend-reporting-assistant")
        self.assertIn("First-run packet created", registry.closeouts[0].artifact_ids)
        self.assertEqual(registry.learning[0].project_id, "project-diana-spend-reporting-assistant")
        self.assertIn("deterministic metrics", registry.learning[0].proposed_learning)
        work_items = {item.workstream_id: item for item in registry.work_items}
        self.assertIn("workstream-source-synthesis", work_items)
        self.assertIn("DianaBrief.md-1.pdf", "\n".join(work_items["workstream-source-synthesis"].inputs))
        self.assertIn("deliverables/customer-brief-synthesis.md", work_items["workstream-source-synthesis"].expected_output)
        self.assertIn("Find calculation owner", "\n".join(work_items["workstream-technical-diagnostic"].definition_of_done))
        self.assertEqual(work_items["workstream-implementation-path"].pause_condition, "Dev-team confirmation or implementation evidence.")
        claims_by_text = {claim.text: claim for claim in registry.claims}
        self.assertEqual(claims_by_text["Reports frequently require manual correction."].evidence_status.value, "supported")
        self.assertEqual(claims_by_text["The system likely uses Azure OpenAI."].evidence_status.value, "inferred")
        self.assertEqual(claims_by_text["The actual production pipeline is confirmed."].evidence_status.value, "unknown")
        self.assertTrue(claims_by_text["Reports frequently require manual correction."].artifact_id.startswith("artifact-diana-spend-reporting-assistant-customer-brief-synthesis"))

    def test_importer_writes_registry_json(self):
        project_path = Path("projects/diana-spend-reporting-assistant")

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "registry.json"
            registry = import_project_folder(project_path, output_path=output_path)

            reloaded = Registry.model_validate_json(output_path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded.projects[0].id, registry.projects[0].id)


if __name__ == "__main__":
    unittest.main()
