"""
Artifact Repository Service.

Acts as the persistent, immutable storage layer for all generated artifacts and workstream evidence.
This is the single source of truth (SSOT) for provenance tracking.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class ArtifactRepository:
    def __init__(self):
        # In a real system, this would connect to Neo4j or similar graph database.
        self._artifacts_store: Dict[str, Dict[str, Any]] = {}
        print("Artifact Repository Service Initialized: Ready to log immutable evidence.")

    def _generate_record_id(self, work_id: str, action: str) -> str:
        """Creates a unique and traceable ID for the record."""
        return f"{work_id}-{action}-{datetime.now().strftime('%Y%m%d')}_{len(self._artifacts_store)}"

    def log_artifact(self, work_id: str, artifact_type: str, content: Any, owner: str) -> Optional[str]:
        """
        Logs a new artifact, generating the required ChangeRecord. (AC 2).
        Returns the unique ID of the saved record.
        """
        record_id = self._generate_record_id(work_id, f"{artifact_type.lower()}_created")
        
        change_record: Dict[str, Any] = {
            "record_id": record_id,
            "work_package_id": work_id,
            "timestamp": datetime.now().isoformat(),
            "owner": owner,
            "artifact_type": artifact_type,
            "content_summary": str(content)[:100] + "...", # Summarize for quick lookup
            "provenance": {
                "input_inputs": [], # Needs to list all required inputs
                "policies_applied": [], 
                "is_approved": False
            }
        }
        self._artifacts_store[record_id] = change_record
        print(f"✅ Artifact Logged: {record_id}. Provenance record created.")
        return record_id

    def get_full_audit_trail(self, work_id: str) -> List[Dict[str, Any]]:
        """Retrieves all ChangeRecords associated with a specific work package ID."""
        trail = [
            record for record in self._artifacts_store.values() 
            if record.get("work_package_id") == work_id and "ChangeRecord" in record["artifact_type"]
        ]
        return trail

    def search_by_type(self, artifact_type: str) -> List[Dict[str, Any]]:
        """Retrieves all artifacts of a specific type (e.g., 'HandoffPackage')."""
        results = [
            record for record in self._artifacts_store.values() 
            if "artifact_type" in record and record["artifact_type"] == artifact_type
        ]
        return results


# Singleton instance for easy access across the system components
ArtifactRepo = ArtifactRepository()