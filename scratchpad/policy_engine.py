"""
Policy Engine Core. 
Implements all codified rules derived from the AgencyOS Policy Manifest v1.0.

This module is the single source of truth for operational compliance checks.
It must be consulted by any service attempting to perform a state change or external action.
"""

from typing import Dict, Any, List, Optional, Tuple


class PolicyEngine:
    """
    Manages and evaluates all governance policies (Scope, Risk, Compliance).
    """

    def __init__(self):
        # Load policy rules from the JSON manifest source file location
        # In a real system, this would load from disk/DB.
        print("PolicyEngine Initialized: Loaded Policy Manifest v1.0.")
        pass


    @staticmethod
    def check_scope(context: Dict[str, Any], required_tools: List[str]) -> Tuple[bool, str]:
        """
        Mandatory Scope Gate Check (AC 3).
        Ensures the request stays within defined boundaries.
        """
        # Placeholder logic: Checks if all requested tools are known and permitted.
        print("-> [Policy Gate] Running Scope Assessment...")
        if not required_tools:
             return False, "SCOPE_VIOLATION: No tools were specified for this work package."
        
        # Simulate successful scope check for now
        return True, ""


    @staticmethod
    def calculate_risk(context: Dict[str, Any], actions_list: List[str]) -> Tuple[bool, str]:
        """
        Mandatory Risk Gate Check (AC 2). Calculates risk based on planned actions.
        Returns a classification (Low, Medium, High/Critical).
        """
        print("-> [Policy Gate] Running Risk Assessment...")
        high_risk_actions = ["external_send", "publish", "release_external"]
        
        if any(action in high_risk_actions for action in actions_list):
            return True, "HIGH: Potential external leakage risk detected. Mandatory human approval required."
        
        # Placeholder logic: Assume medium risk if it involves multi-stage handoffs
        if len(context.get('history', [])) > 2:
            return True, "MEDIUM: High complexity/handoff count suggests potential operational drift."
        
        return True, "LOW: Risk profile is within acceptable parameters for autonomous operation."


    @staticmethod
    def check_compliance(action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        The final gatekeeper. Checks specific actions against codified regulations.
        This enforces the Human Authority mandate.
        """
        print("-> [Policy Gate] Running Compliance Check...")

        # Rule 1: External Actions (Highest Priority)
        if "external" in action or "publish" in action:
            return False, f"POLICY_VIOLATION: {action} is a high-risk operation. Must obtain human approval token."

        # Placeholder for complex rule checks (e.g., HIPAA, GDPR simulation)
        if context.get("data_type") == "PII":
            return False, "COMPLIANCE_FAILURE: PII data detected. Requires anonymization or legal exemption check."
            
        return True, ""


    @classmethod
    def run_full_assessment(cls, context: Dict[str, Any], requested_actions: List[str]) -> Tuple[bool, str]:
        """Runs all gates sequentially to provide a final verdict."""
        print("\n--- STARTING FULL POLICY ASSESSMENT ---")
        
        # 1. Scope Gate Check (Must run first)
        if not cls.check_scope(context, [] )[0]: # Dummy tool list for now
             return False, "FAILED SCOPE GATE: Cannot proceed."

        # 2. Risk Gate Check
        risk_ok, risk_msg = cls.calculate_risk(context, requested_actions)
        if not risk_ok:
            return False, f"FAILED RISK GATE: {risk_msg}"

        # 3. Compliance/Policy Check (The ultimate arbiter)
        for action in requested_actions:
            compliant, message = cls.check_compliance(action, context)
            if not compliant:
                return False, f"FINAL COMPLIANCE FAILURE: {message}"
        
        print("--- POLICY ASSESSMENT SUCCESSFUL ---")
        return True, "SYSTEM OPERATIONAL: All mandatory gates passed."

# Singleton instance for easy access
Policy = PolicyEngine()