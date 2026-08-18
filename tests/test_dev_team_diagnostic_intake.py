import json
import tempfile
import unittest
from pathlib import Path

from tools import dev_team_diagnostic_intake as intake


class DiagnosticIntakeTests(unittest.TestCase):
    def test_questions_are_generic_to_user_work(self):
        joined = "\n".join(question for _, question in intake.QUESTIONS).lower()

        forbidden_terms = [
            "diana",
            "spend",
            "financial",
            "pdf",
            "legal tracker",
            "teamconnect",
            "totals",
            "percentages",
            "report",
        ]

        for term in forbidden_terms:
            self.assertNotIn(term, joined)

        self.assertIn("user", joined)
        self.assertIn("work", joined)

    def test_default_project_uses_first_run_slug_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".first-run.json").write_text(
                json.dumps({"slug": "generic-user-work"}),
                encoding="utf-8",
            )

            self.assertEqual(
                intake.default_project(root),
                root / "projects" / "generic-user-work",
            )

    def test_diana_information_lives_under_use_case(self):
        use_case = intake.USE_CASES["diana-spend-reporting-assistant"]

        self.assertEqual(use_case["user"], "Diana")
        self.assertIn("spend reporting assistant", use_case["work"])
        self.assertIn("DianaBrief.md-1.pdf", "\n".join(use_case["source_paths"]))

    def test_response_packet_can_record_use_case_without_changing_generic_questions(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "projects" / "generic-user-work"
            answer = intake.Answer(
                question_id="work_boundary",
                question=intake.QUESTIONS[0][1],
                answer="Use the Diana spend reporting assistant use case.",
                uploads=[],
            )

            result = intake.write_response_packet(
                project,
                [answer],
                use_case=intake.USE_CASES["diana-spend-reporting-assistant"],
            )

            payload = json.loads(result.json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["use_case"]["user"], "Diana")
            self.assertIn("Diana", result.markdown_path.read_text(encoding="utf-8"))
            self.assertNotIn("Diana", "\n".join(question for _, question in intake.QUESTIONS))

    def test_records_answers_and_copies_uploads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects" / "generic-user-work"
            upload = root / "schema.csv"
            upload.write_text("matter,total\nA,100\n", encoding="utf-8")

            answers = [
                intake.Answer(
                    question_id="calculation_location",
                    question="Where are calculations performed?",
                    answer="Python computes totals before the model sees them.",
                    uploads=[upload],
                )
            ]

            result = intake.write_response_packet(project, answers)

            self.assertTrue(result.markdown_path.exists())
            self.assertTrue(result.json_path.exists())
            copied = result.upload_dir / "schema.csv"
            self.assertTrue(copied.exists())
            self.assertEqual(copied.read_text(encoding="utf-8"), "matter,total\nA,100\n")

            payload = json.loads(result.json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["responses"][0]["question_id"], "calculation_location")
            self.assertEqual(payload["responses"][0]["uploads"][0]["stored_path"], str(copied))

    def test_missing_upload_fails_before_writing_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            missing = Path(tmp) / "missing.csv"
            answers = [
                intake.Answer(
                    question_id="schemas",
                    question="Upload schemas.",
                    answer="Attached.",
                    uploads=[missing],
                )
            ]

            with self.assertRaises(FileNotFoundError):
                intake.write_response_packet(project, answers)

            self.assertFalse((project / "evidence" / "dev-team-diagnostic-responses.json").exists())


if __name__ == "__main__":
    unittest.main()
