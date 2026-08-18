import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from tools import dev_team_diagnostic_intake
from tools import first_run


class FirstRunDevDiagnosticTests(unittest.TestCase):
    def test_detects_dev_team_diagnostic_need_from_first_run_data(self):
        data = {
            "name": "user-work-project",
            "outcome": "Prepare dev-team diagnostic memo for the user's work involved.",
            "notes": "Customer briefs attached.",
        }

        self.assertTrue(first_run.needs_dev_team_diagnostic(data))

    def test_does_not_trigger_from_specific_customer_or_work_names_only(self):
        data = {
            "name": "diana-spend-reporting-assistant",
            "outcome": "Create first-run packet.",
            "notes": "Customer briefs attached.",
        }

        self.assertFalse(first_run.needs_dev_team_diagnostic(data))

    def test_runs_dev_team_diagnostic_after_first_run_when_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = root / "projects" / "user-work-project"
            data = {
                "name": "user-work-project",
                "outcome": "Prepare dev-team diagnostic memo for the user's work involved.",
                "notes": "",
            }
            answer = dev_team_diagnostic_intake.Answer(
                question_id="calculation_location",
                question="Are calculations before AI?",
                answer="Unknown.",
                uploads=[],
            )

            with redirect_stdout(StringIO()):
                ran = first_run.maybe_run_dev_team_diagnostic(
                    data,
                    packet,
                    collect_answers=lambda: [answer],
                )

            self.assertTrue(ran)
            self.assertTrue((packet / "evidence" / "dev-team-diagnostic-responses.md").exists())
            self.assertTrue((packet / "evidence" / "dev-team-diagnostic-responses.json").exists())

    def test_skip_flag_prevents_dev_team_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp) / "projects" / "user-work-project"
            data = {
                "name": "user-work-project",
                "outcome": "Prepare dev-team diagnostic memo for the user's work involved.",
                "notes": "",
                "skip_dev_diagnostic": "True",
            }

            ran = first_run.maybe_run_dev_team_diagnostic(
                data,
                packet,
                collect_answers=lambda: self.fail("collector should not run"),
            )

            self.assertFalse(ran)


if __name__ == "__main__":
    unittest.main()
