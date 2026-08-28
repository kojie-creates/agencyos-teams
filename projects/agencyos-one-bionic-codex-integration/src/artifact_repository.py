"""Artifact repository for asset transaction manifests."""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)


class SimulatedTransactionDatabase:
    """Placeholder persistence adapter for prototype service hardening."""

    def write_transaction(self, data: dict) -> dict:
        logger.info("Persistence simulated for transaction %s", data.get("transaction_id"))
        return {
            "status": "SIMULATED",
            "message": "Persistence simulated by placeholder database.",
        }


class ArtifactRepository:
    """Stores tamper-evident transaction records for processed assets."""

    def __init__(self, root_path, db=None):
        self.root_path = Path(root_path)
        self.db = db or SimulatedTransactionDatabase()
        self.root_path.mkdir(parents=True, exist_ok=True)

    def log_asset_transaction(
        self,
        source_file: str,
        status: str,
        transaction_metadata: dict,
    ) -> str:
        """Write a transaction manifest and return its unique transaction ID."""
        source_path = Path(source_file)
        content = source_path.read_bytes()
        transaction_id = f"txn-{uuid4().hex}"
        manifest = {
            "transaction_id": transaction_id,
            "source_file": str(source_path),
            "status": status,
            "sha256": hashlib.sha256(content).hexdigest(),
            "transaction_metadata": transaction_metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest["persistence"] = self.db.write_transaction(manifest)

        manifest_path = self._transaction_path(transaction_id)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return transaction_id

    def get_transaction(self, transaction_id: str) -> dict:
        """Load a transaction manifest by ID."""
        manifest_path = self._transaction_path(transaction_id)
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    def _transaction_path(self, transaction_id: str) -> Path:
        return self.root_path / f"{transaction_id}.json"
