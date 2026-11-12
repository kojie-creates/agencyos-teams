# Governed Service Blueprint (AgencyOS Teams Pattern)
***

## Source Evidence
This blueprint is a direct synthesis of the learnings from the `agencyos-one` development effort, validated against four key documents that define its scope and boundaries.
*   **Technical Closure:** [TECHNICAL_DEVELOPMENT_CLOSEOUT.md]
*   **Business Intent:** [PRODUCT_BRIEF_MVP_RISK_SCREENED_FORECASTING.md]
*   **User Journey Map:** [API_CONSUMER_STORY_MAP.md]
*   **Roadmap Definition:** [PRODUCTIZATION_BACKLOG.md]

## 1. Purpose
This blueprint defines a reusable prototype governance pattern for AgencyOS Teams services. Its goal is to guide future service design with a minimum set of architectural checks and service contracts before production-readiness claims are made. This pattern supports traceable, auditable, and governance-aware service design from day one.

## 2. Proven Reference Implementation
The current `agencyos-one` module serves as the operational proof-of-concept for this blueprint. It demonstrates:
*   **API Gateway Pattern:** Prototype traffic is routed through a single entry point enforcing authentication (API Key $\rightarrow$ future OAuth).
*   **Governance Funnel:** A controlled sequence of Policy Check $\rightarrow$ Data Source Trust Validation $\rightarrow$ Core Logic Execution.
*   **Auditability:** Tested actions result in a hash-backed transaction manifest logged to local persistent storage.

## 3. Required Service Pattern (The Blueprint)
Future services built within the AgencyOS ecosystem should incorporate these recommended layers:
1.  **Authentication Gateway:** Validate an identity token/key *before* touching any business logic.
2.  **Policy Enforcement Point:** A dedicated gate that checks policy rules and consent flags against the request context.
3.  **Data Trust Gate:** Validate input data sources where source provenance affects downstream results (Source Owner, Consent Status, Data Age).
4.  **Core Logic Module:** The specific service execution (e.g., Forecasting, Reporting).
5.  **Audit Trail Commitment:** Inputs, outputs, and status changes should be logged to a standard transaction manifest.

## 4. Minimum Governance Gates
*   **Policy Gate:** Place policy review before data processing or action execution.
*   **Data Trust Check:** Validate source trust metrics (owner approval, consent status) for inputs feeding intelligence modules.
*   **Manifest Logging:** Generate and persist a unique `transaction_id` for each governed request attempt, regardless of success or failure.

## 5. API Gateway Requirements
The external-facing entry point should follow this contract:
*   Provide an OpenAPI 3.1 specification definition.
*   Handle pre-flight CORS requests gracefully before executing core logic.
*   Provide distinct, structured HTTP responses for `401` (Auth), `403` (Policy/Trust Failure), and `2xx`/`5xx`.

## 6. Documentation Requirements
Future services should produce these three artifacts before coding begins:
1.  **Product Brief:** A PRD defining scope, users, and success criteria.
2.  **API Consumer Story Map:** Translates the business flow into granular technical states and API calls.
3.  **OpenAPI Specification:** The single source of truth for client development.

## 7. Adoption Checklist (For New Teams)
Before commencing work on a new governed-service feature, a team should check these boxes:
*   [ ] **Design Review:** Submit PRD and Story Map for architectural review.
*   [ ] **Code Implementation:** Build the service within the defined `.../governance/` structure.
*   [ ] **Testing:** Write tests that cover success paths, policy-fail paths, and authentication failure paths.

## 8. Not Yet Enterprise-Grade (Scope Disclaimer)
This blueprint is derived from a validated local prototype. It does not yet prove centralized identity, multi-tenant governance, production observability, live external data enforcement, or organization-wide adoption. This remains the core scope boundary until specific productization work begins.
