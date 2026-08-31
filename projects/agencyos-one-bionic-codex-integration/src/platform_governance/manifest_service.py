"""Standalone transaction-manifest service for prototype governance events."""

import hashlib
import json
import logging
import sqlite3
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


class SQLiteTransactionDatabase:
    """Local SQLite transaction-manifest store for controlled hardening tests."""

    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def write_transaction(self, data: dict) -> dict:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO transaction_manifests (
                    transaction_id,
                    timestamp,
                    status,
                    original_status,
                    hash_back_data,
                    manifest_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    data["transaction_id"],
                    data["created_at"],
                    self._normalized_status(data.get("status")),
                    data.get("status"),
                    data["sha256"],
                    json.dumps(data, indent=2),
                ),
            )

        return {
            "status": "SQLITE_COMMITTED",
            "db_path": str(self.db_path),
        }

    def read_transaction(self, transaction_id: str) -> dict:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT manifest_json
                FROM transaction_manifests
                WHERE transaction_id = ?
                """,
                (transaction_id,),
            ).fetchone()

        if row is None:
            raise FileNotFoundError(transaction_id)

        manifest = json.loads(row[0])
        manifest["persistence"] = {
            "status": "SQLITE_COMMITTED",
            "db_path": str(self.db_path),
        }
        return manifest

    def _initialize(self):
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transaction_manifests (
                    transaction_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    original_status TEXT NOT NULL,
                    hash_back_data TEXT NOT NULL,
                    manifest_json TEXT NOT NULL
                )
                """
            )

    def _normalized_status(self, status: str | None) -> str:
        normalized = str(status or "").upper()
        if "FLAGGED" in normalized:
            return "FLAGGED"
        if any(token in normalized for token in ("FAIL", "FAILED", "HALTED")):
            return "FAIL"
        return "SUCCESS"


class ManifestService:
    """Owns manifest file creation and local database writes."""

    def __init__(self, root_path, db=None, db_path=None):
        self.root_path = Path(root_path)
        self.db = db or SQLiteTransactionDatabase(
            db_path or self.root_path / "manifests.db"
        )
        self.root_path.mkdir(parents=True, exist_ok=True)

    def log_event(self, status: str, event_data: dict, metadata: dict | None = None) -> str:
        event_path = self.root_path / "events" / f"event-{uuid4().hex}.json"
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_text(json.dumps(event_data or {}, indent=2), encoding="utf-8")
        return self.log_manifest(
            source_file=str(event_path),
            status=status,
            transaction_metadata=metadata or {},
        )

    def log_manifest(
        self,
        source_file: str,
        status: str,
        transaction_metadata: dict | None = None,
    ) -> str:
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

    def get_event(self, transaction_id: str) -> dict:
        return self.get_manifest(transaction_id)

    def get_manifest(self, transaction_id: str) -> dict:
        manifest_path = self._transaction_path(transaction_id)
        if manifest_path.is_file():
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        if hasattr(self.db, "read_transaction"):
            return self.db.read_transaction(transaction_id)
        raise FileNotFoundError(transaction_id)

    def _transaction_path(self, transaction_id: str) -> Path:
        return self.root_path / f"{transaction_id}.json"
