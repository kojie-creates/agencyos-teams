# Phase Beta 01: Auth Abstraction (Technical Milestone)

**TO:** Codex Code Builder Agent  
**FROM:** Operational Team Lead Agent  
**PROJECT:** agencyos-one-bionic-codex-integration  
**TARGET FILES:**
- src/platform_governance/auth_gate.py
- src/api_gateway.py
- tests/test_initial_scaffold.py

## 🎯 Goal: Decouple Authentication Logic into a Reusable Platform Utility
The immediate goal is to extract the API key validation and formalize the security checking mechanism from `src/api_gateway.py` and move it into a dedicated, reusable component within `platform_governance`. This abstracts the security concern away from the routing layer, making it an easily pluggable standard for all future services.

---
**SCOPE GUARDRAIL:** This ticket prepares the authentication boundary for future hardening. It does not implement production OAuth/OIDC, RBAC, user management, or multi-tenancy.
***

## Implementation Requirements
1.  **New Utility Class (`src/platform_governance/auth_gate.py`)**:
    *   Define the `AuthResult` data structure: Must clearly communicate success, failure reason (e.g., AUTH_FAILED, TOKEN_EXPIRED), and necessary remediation steps.
    *   Implement a primary verification method that handles both the current hardcoded API Key check AND a stubbed OIDC token validation flow.
2.  **Gateway Update (`src/api_gateway.py`)**:
    *   The `API Gateway` must be rewritten to **orchestrate security**. It must now call the new `AuthGate` *first*. The gateway's primary responsibility becomes validating the identity before routing the request to any business logic module (Policy Gate, DST).
    *   If `AuthGate` fails validation, the gateway MUST return a 401 response *before* Policy or DST are invoked.
3.  **Testing (`tests/test_initial_scaffold.py`)**:
    *   Add comprehensive test cases to prove:
        a. **Successful Flow:** Request with valid API Key successfully passes `AuthGate` and reaches the Policy Gate.
        b. **Failure Flow 1 (Unauthorized):** Request with missing or invalid key returns HTTP 401 immediately upon hitting the gateway middleware layer.
        c. **Future-Proofing Test:** The test must confirm that the OIDC stub can be instantiated and correctly reports a `NOT_CONFIGURED` state when no real provider is configured.

## Governance & Boundary Conditions
*   **Abstraction Focus:** The goal is to build an interface for security, not implement full OAuth/OIDC.
*   **Execution Order:** Authentication must *always* happen first in the execution chain.

## Expected Result
The milestone is complete when tests prove that authentication is correctly isolated within a reusable utility class and successfully blocks unauthorized access at the API gateway entry point, without breaking any existing successful workflows.