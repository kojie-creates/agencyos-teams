# Phase Beta 02: Postgres Manifest Adapter (Technical Milestone)

**TO:** Codex Code Builder Agent  
**FROM:** Operational Team Lead Agent  
**PROJECT:** agencyos-one-bionic-codex-integration  
**TARGET FILES:**
- src/platform_governance/manifest_service.py
- src/artifact_repository.py
- tests/test_initial_scaffold.py

## 🎯 Goal: Decouple Persistence Logic into a Reusable Platform Utility
The goal is to abstract the storage mechanism away from the core business logic. We must prove that the system can swap its persistence backend (SQLite $\leftrightarrow$ Postgres) without rewriting service calls. This creates a pluggable, standardized Adapter Interface, which is crucial for scaling to production.

---
**SCOPE GUARDRAIL:** This milestone introduces the Postgres adapter boundary. It does not prove production durability, managed database operations, migrations (DDL), backups, or disaster recovery.
***

## Implementation Requirements
1.  **Abstract Interface (`src/platform_governance/manifest_service.py`)**:
    *   Define a mandatory Abstract Base Class (`BaseManifestAdapter`). This protocol must dictate the methods: `connect()`, `write_transaction(data)`, and `disconnect()`.
2.  **Concrete Adapters:**
    *   **`SQLiteManifestDatabaseAdapter`:** Remains functional as the default local adapter, retaining all current logic for compatibility.
    *   **`PostgresManifestDatabaseAdapter`:** Implement this class. It must accept connection parameters from environment variables (e.g., `PG_HOST`, `PG_USER`). Initialization **must gracefully return a specific NOT_CONFIGURED state or raise a clear setup exception** if required credentials are missing, preventing crashes during local development/testing without a running Postgres instance.
3.  **Facade Update (`src/artifact_repository.py`)**:
    *   Update the repository to accept an initialized adapter object (Dependency Injection). It must now manage the lifecycle of this abstract connection object rather than managing raw database connections itself.

## Governance & Boundary Conditions
*   **Adapter Priority:** The service layer calling mechanism must only interact with the abstract `BaseManifestAdapter` interface. This ensures that changing from SQLite to Postgres is a single point of change in the infrastructure code, leaving the business logic untouched.
*   **Test Focus:** Tests must validate the adapter swapping capability without requiring a running database instance for most scenarios.

## Expected Result
The milestone is complete when tests prove:
1.  SQLite continues as the default and functional fallback.
2.  A `PostgresManifestDatabaseAdapter` can be instantiated successfully using environment variables (even if the connection fails immediately afterwards, proving configuration reading).
3.  The system correctly handles the "adapter not configured" state without crashing, logging an informative error message instead.