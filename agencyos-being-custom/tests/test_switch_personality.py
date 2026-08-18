import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "switch_personality.py"


class SwitchPersonalityTests(unittest.TestCase):
    def test_switch_updates_banner_pointer_source_date_shape_and_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personality_dir = root / "personality"
            personality_dir.mkdir()
            (personality_dir / "Jaavis.md").write_text("# Jaavis\n", encoding="utf-8")
            active = personality_dir / "ACTIVE-PERSONALITY.md"
            active.write_text(
                "\n".join(
                    [
                        "# Active Personality",
                        "",
                        "Current active personality: Katie",
                        "",
                        "Active personality: Katie",
                        "Source: personality/Katie.md",
                        "Last switched: 2026-08-12",
                        "",
                        "Default shape: Katie.",
                        "User-defined type: Warm Enthusiastic Conversational.",
                        "### Default Shape: Katie",
                        "## User-Defined Type: Warm Enthusiastic Conversational",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "Jaavis",
                    "--root",
                    str(root),
                    "--date",
                    "2026-08-13",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = active.read_text(encoding="utf-8")
            self.assertIn("Current active personality: Jaavis", text)
            self.assertIn("Active personality: Jaavis", text)
            self.assertIn("Source: personality/Jaavis.md", text)
            self.assertIn("Last switched: 2026-08-13", text)
            self.assertIn("Default shape: Jaavis.", text)
            self.assertIn("User-defined type: Polite Formal Loyal Dry Wit.", text)
            self.assertIn("### Default Shape: Jaavis", text)
            self.assertIn("## User-Defined Type: Polite Formal Loyal Dry Wit", text)

    def test_switch_rejects_missing_personality_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "personality").mkdir()
            active = root / "personality" / "ACTIVE-PERSONALITY.md"
            active.write_text("Active personality: Katie\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "Nope", "--root", str(root)],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("personality/Nope.md not found", result.stderr)

    def test_switch_two_slug_specialist_resolves_primary_personality(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personality_dir = root / "personality"
            personality_dir.mkdir()
            (personality_dir / "Vera.md").write_text("# Vera\n", encoding="utf-8")
            (personality_dir / "ROLE-PERSONALITY-MAP.md").write_text(
                "\n".join(
                    [
                        "| Specialist | Specialist Handle | Display Name | Energy Parents | Domain Fit |",
                        "| --- | --- | --- | --- | --- |",
                        "| Audit | @vera-quill | Vera Quill | @vera + @elias | Assurance. |",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            active = personality_dir / "ACTIVE-PERSONALITY.md"
            active.write_text(
                "\n".join(
                    [
                        "# Active Personality",
                        "",
                        "Current active personality: Vera",
                        "",
                        "Active personality: Vera",
                        "Source: personality/Vera.md",
                        "Last switched: 2026-08-12",
                        "",
                        "Default shape: Vera.",
                        "User-defined type: Vera Personality.",
                        "### Default Shape: Vera",
                        "## User-Defined Type: Vera Personality",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "@vera-quill",
                    "--root",
                    str(root),
                    "--date",
                    "2026-08-13",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = active.read_text(encoding="utf-8")
            self.assertIn("Current active personality: @vera-quill", text)
            self.assertIn("Active personality: @vera-quill", text)
            self.assertIn("Source: personality/Vera.md", text)
            self.assertIn("Default shape: Vera Quill.", text)
            self.assertIn("User-defined type: Specialist Route.", text)

    def test_switch_one_slug_handle_resolves_core_personality(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            personality_dir = root / "personality"
            personality_dir.mkdir()
            (personality_dir / "Jaavis.md").write_text("# Jaavis\n", encoding="utf-8")
            active = personality_dir / "ACTIVE-PERSONALITY.md"
            active.write_text("Active personality: @vera-quill\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "@jaavis",
                    "--root",
                    str(root),
                    "--date",
                    "2026-08-13",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = active.read_text(encoding="utf-8")
            self.assertIn("Current active personality: @jaavis", text)
            self.assertIn("Active personality: @jaavis", text)
            self.assertIn("Source: personality/Jaavis.md", text)
            self.assertIn("Default shape: Jaavis.", text)


if __name__ == "__main__":
    unittest.main()
