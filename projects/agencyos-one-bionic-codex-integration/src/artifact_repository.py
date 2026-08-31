"""Compatibility repository facade for asset transaction manifests."""

from pathlib import Path

from platform_governance.manifest_service import ManifestService
from platform_governance.manifest_service import SimulatedTransactionDatabase
from platform_governance.manifest_service import SQLiteTransactionDatabase


class ArtifactRepository:
    """Stores transaction records through the shared platform manifest service."""

    def __init__(self, root_path, db=None, db_path=None):
        self.root_path = Path(root_path)
        self.manifest_service = ManifestService(
            root_path=self.root_path,
            db=db,
            db_path=db_path,
        )
        self.db = self.manifest_service.db

    def log_asset_transaction(
        self,
        source_file: str,
        status: str,
        transaction_metadata: dict,
    ) -> str:
        """Write a transaction manifest and return its unique transaction ID."""
        return self.manifest_service.log_manifest(
            source_file=source_file,
            status=status,
            transaction_metadata=transaction_metadata,
        )

    def get_transaction(self, transaction_id: str) -> dict:
        """Load a transaction manifest by ID."""
        return self.manifest_service.get_manifest(transaction_id)

    def _transaction_path(self, transaction_id: str) -> Path:
        return self.root_path / f"{transaction_id}.json"
