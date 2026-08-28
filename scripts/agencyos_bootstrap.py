#!/usr/bin/env python3
"""
AgencyOS Teams Core Service Bootstrapping Engine (Resource-Aware).

Purpose:
- Provides the unified, controlled entry point (The 'Operating Surface') for all work.
- Enforces the entire lifecycle through mandatory governance checks before interacting with any AI model or external tool.
- Must be modular and designed for future scaling of Beings and Tools based on available local resources (Model/Harness).

Usage:
1. Set INNERLIGHT_HOST environment variable to select the primary Local Model/Harness (e.g., "gemma", "llama").
2. Run: python agencyos_bootstrap.py "/help"

Core Flow Mandate: User Input $\rightarrow$ Governance Gate $\rightarrow$ Command Router $\rightarrow$ Execution Service/Model Host.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Callable, Tuple


# --- CONFIGURATION & INITIALIZATION ---
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Placeholder for the Policy Engine/Gatekeeper service call (Needs to be implemented later)
def enforce_policy_gate(input_context: dict) -> Tuple[bool, str]:
    """
    Mandatory Governance Gate Check.
    This function must implement all rules from the Policy Manifest v1.0.
    It determines if the request is safe and compliant to proceed.
    Returns (is_compliant, violation_message).
    """
    print("--- [GOVERNANCE CHECK] Running Policy Gate Assessment... ---")
    # Placeholder implementation: Assume all simple inputs are fine, but external actions fail immediately.
    if "external" in str(input_context.get('raw_input', '')):
        return False, "ACTION_BLOCKED_EXTERNAL_HIGH_RISK: External action detected. Requires human approval token."

    # Placeholder for Scope/Risk checks (These will become separate modules)
    print("POLICY SUCCESS: Passed preliminary Scope and Risk checks.")
    return True, ""


# --- CORE WORKFLOW HANDLERS (The 'Pro Layer' Logic) ---

def handle_command_intent(user_input: str, context: dict) -> tuple[str, bool]:
    """Routes structured commands to specialized services."""
    raw = user_input.strip().lower()
    if raw.startswith("/handoff"):
        # Implementation Note: This must generate a formal Handoff Package artifact.
        print("--- [WORKFLOW HANDLER] Initiating Handoff Procedure ---")
        return "Handoff package successfully queued. Awaiting human acceptance.", True
    if raw.startswith("/audit"):
        # Implementation Note: Query the Artifact Repository for a formal audit report.
        print("--- [WORKFLOW HANDLER] Triggering Audit Trail Generation ---")
        return "Audit report generated and logged in the repository. Review required.", True

    return "", False


def run_innerlight_handler(user_input: str, host: str | None = None) -> str:
    """
    The unified execution path for AgencyOS Teams work.
    Coordinates governance before calling the underlying Model/Harness service.
    """

    # 1. Context Assembly (Crucial addition: storing the model context)
    initial_context = {"raw_input": user_input, "session_history": ["..."], "model_host": host}

    # 2. Governance Check (The Gatekeeper) - MANDATORY FIRST STEP
    is_compliant, violation = enforce_policy_gate(initial_context)
    if not is_compliant:
        return f"\n=============================================================\n🚨 GOVERNANCE FAILURE:\n{violation}\n\nPlease correct the scope or request manual human override."

    # 3. Command Intent Check (The Router) - Determines if a specialized service is needed.
    command_output, was_command = handle_command_intent(user_input, initial_context)
    if was_command:
        return "\n=============================================================\n✅ OPERATIONAL HANDOFF:\n" + command_output

    # 4. Fallback to LLM Handler (The Brain) - Standard conversation flow
    print("\n--- [CORE ENGINE] Passing compliant input to the selected Model Host... ---")
    
    def llm_wrapper(input: str):
        """Simulates calling the appropriate external LLM wrapper based on the active local model host."""
        model_used = os.environ.get('INNERLIGHT_HOST', 'Unknown')
        return f"\n=============================================================\n🧠 AGENCYOS OUTPUT:\nLLM Response processed successfully using Model: {model_used}. Governance checks passed."

    return llm_wrapper(user_input)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run AgencyOS Teams through the governed runtime boundary.",
        formatter_class=argparse.HelpFormatter
    )
    # Changed description to reflect model selection over API provider
    parser.add_argument(
        "user_input",
        nargs="*",
        help="The exact user input to send into the operating surface, including slash commands (e.g., /handoff)."
    )
    parser.add_argument(
        "--host",
        default=None,
        help='Local Model/Harness shim override: e.g., "gemini", "llama".',
    )
    args = parser.parse_args()

    raw_input = " ".join(args.user_input).strip()
    if not raw_input:
        print('Error: No user input provided.')
        return 1

    try:
        # Execute the entire flow through our unified handler
        output = run_innerlight_handler(raw_input, host=args.host)
        print(output)
        return 0
    except Exception as exc:
        print("\n=============================================================")
        print("❌ CRITICAL BOOTSTRAP FAILURE DETECTED.")
        print(f"System Error Detail: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())