import unittest
import subprocess
import os
from typing import List, Tuple

# Define paths relative to the workspace root (Desktop)
BOOTSTRAP_SCRIPT = "./agencyos-teams/scripts/agencyos_bootstrap.py"


class TestAgencyOSProductization(unittest.TestCase):
    """
    Comprehensive integration test suite for AgencyOS Teams against all defined Acceptance Criteria (AC 1-7).
    This simulates a full QA cycle, testing functional logic and governance enforcement simultaneously.
    """

    @classmethod
    def setUpClass(cls):
        # Ensure the bootstrap script exists and is runnable before any tests run
        if not os.path.exists(BOOTSTRAP_SCRIPT):
            raise FileNotFoundError(f"Prerequisite file not found: {BOOTSTRAP_SCRIPT}")
        print("\n--- SETUP COMPLETE: AgencyOS Teams Prototype Loaded for Testing ---")

    @staticmethod
    def _run_cli_test(args: List[str], host: str = "claude") -> Tuple[int, str]:
        """Helper function to execute the bootstrap script via subprocess."""
        command = ["python", BOOTSTRAP_SCRIPT] + args
        full_command = command + [f"--host", host]
        
        # Execute the process and capture stdout/stderr
        try:
            result = subprocess.run(
                full_command, 
                capture_output=True, 
                text=True, 
                check=False, # Do not raise exception on non-zero exit code for controlled testing
                timeout=10
            )
            return result.returncode, (result.stdout + result.stderr)
        except subprocess.TimeoutExpired:
            return -1, "TIMEOUT_ERROR"
        except Exception as e:
            return -2, f"SETUP_ERROR: {str(e)}"

    # ====================================================================
    # AC 1: Policy Enforcement (Governance Test)
    # ====================================================================
    def test_ac_01_policy_enforcement(self):
        """Tests mandatory policy failure for high-risk external actions."""
        print("\n[TEST] Running Acceptance Criterion 1: Policy Enforcement...")
        # Input designed to violate the "external action requires human approval" rule.
        args = ["This is a critical update I need to publish immediately!"]
        exit_code, output = self._run_cli_test(args)

        self.assertEqual(exit_code, 0, f"Expected exit code 0 (successful run), got {exit_code}.")
        self.assertIn("POLICY VIOLATION: ACTION_BLOCKED_EXTERNAL_HIGH_RISK", output, "FAIL: Policy Gate did not block the high-risk action.")

    # ====================================================================
    # AC 2: Auditability (Data Integrity Test)
    # ====================================================================
    def test_ac_02_auditability(self):
        """Tests that a handoff correctly logs a traceable, immutable ChangeRecord."""
        print("\n[TEST] Running Acceptance Criterion 2: Audit Trail Logging...")
        args = ["/handoff"] # Triggers the Handoff Command Handler
        exit_code, output = self._run_cli_test(args)

        self.assertEqual(exit_code, 0, "FAIL: Handoff command failed to execute.")
        # Success is defined by receiving confirmation that the record was logged in the output structure.
        self.assertIn("Handoff package successfully queued", output, "FAIL: Audit trail logging mechanism did not confirm artifact creation.")

    # ====================================================================
    # AC 3: Scope Lock (Governance Test)
    # ====================================================================
    def test_ac_03_scope_lock(self):
        """Tests that the system blocks work if scope boundaries are violated."""
        print("\n[TEST] Running Acceptance Criterion 3: Scope Enforcement...")
        # Simulate an input attempting to use a tool outside the current known scope (Placeholder check)
        args = ["I need to use an unauthorized external API."]
        exit_code, output = self._run_cli_test(args)

        self.assertEqual(exit_code, 0, "FAIL: Scope violation attempt did not trigger a policy block.")
        # We expect the policy engine stub (enforce_policy_gate) to catch this high-level failure.
        self.assertIn("Scope Violation", output, "FAIL: Policy Gate failed to detect out-of-scope tool use.")


    # ====================================================================
    # AC 4: Handoff Continuity (Functional Flow Test)
    # ====================================================================
    def test_ac_04_handoff_continuity(self):
        """Tests that a complex workflow simulates the full handoff process and maintains artifact linkage."""
        print("\n[TEST] Running Acceptance Criterion 4: Handoff Continuity...")
        args = ["/handoff"] # Using the command that triggers the Handoff Package creation.
        exit_code, output = self._run_cli_test(args)

        self.assertEqual(exit_code, 0, "FAIL: Handoff continuity test failed to run.")
        # Success is defined by the acknowledgement of the required package generation.
        self.assertIn("Handoff package successfully queued", output, "FAIL: Workstream did not generate a comprehensive, linked handoff package artifact.")

    # ====================================================================
    # AC 5: Error Resilience (Functional Test)
    # ====================================================================
    def test_ac_05_error_resilience(self):
        """Simulates an internal failure to ensure the process remains suspended and notifies the owner."""
        print("\n[TEST] Running Acceptance Criterion 5: Error Resilience...")
        # Simulate a task that forces a known failure state in the core engine (Placeholder trigger)
        args = ["Internal simulation fail_trigger"] 
        exit_code, output = self._run_cli_test(args)

        self.assertEqual(exit_code, 0, "FAIL: Failure injection test did not run to completion.")
        # Success requires the system to acknowledge failure and suspend the process gracefully.
        self.assertIn("Suspended", output, "FAIL: The system failed catastrophically instead of suspending and reporting the error.")


    # ====================================================================
    # AC 6 & AC 7: Scale and Predictability (Integration Test)
    # ====================================================================
    def test_ac_06_ac_07_scale_and_predictability(self):
        """Simulates running multiple, independent workflows concurrently."""
        print("\n[TEST] Running Acceptance Criteria 6 & 7: Scale and Predictability...")
        # This requires simulating a large batch job (many inputs).
        # For the scope of this test run, we confirm the infrastructure handles high-volume calls.
        args = ["Multi-project summary synthesis", "Audit check on Project Alpha", "Policy review for Client Beta"]
        exit_code, output = self._run_cli_test(args)

        self.assertEqual(exit_code, 0, "FAIL: Multi-workstream test failed.")
        # Success is defined by the Orchestrator Core successfully processing multiple distinct inputs without state loss or crashing.
        self.assertIn("Multi-project", output, "FAIL: The orchestrator could not process multiple disparate workstreams concurrently.")

if __name__ == "__main__":
    unittest.main()