"""Data source trust validation for prototype governance tests."""


class DataSourceTrustService:
    """Classifies whether data inputs can feed downstream prototype workflows."""

    MIN_RELIABILITY_RATING = 0.75
    MAX_DATA_AGE_DAYS = 30

    def validate_source(self, source_context: dict) -> dict:
        """Return a trust decision for a supplied data source context."""
        source = source_context or {}
        source_name = str(source.get("source_name") or "unknown")

        if not bool(source.get("owner_approved")):
            return self._decision(
                "FAIL",
                "OWNER_APPROVAL_MISSING",
                "OWNER_APPROVAL",
                source_name,
            )

        if str(source.get("consent_status") or "").upper() != "APPROVED":
            return self._decision(
                "FAIL",
                "CONSENT_NOT_APPROVED",
                "CONSENT_REVIEW",
                source_name,
            )

        reliability_rating = float(source.get("reliability_rating") or 0)
        if reliability_rating < self.MIN_RELIABILITY_RATING:
            return self._decision(
                "FLAGGED",
                "LOW_RELIABILITY_SOURCE",
                "HUMAN_REVIEW",
                source_name,
            )

        data_age_days = int(source.get("data_age_days") or 0)
        if data_age_days > self.MAX_DATA_AGE_DAYS:
            return self._decision(
                "FLAGGED",
                "DATA_SOURCE_STALE",
                "HUMAN_REVIEW",
                source_name,
            )

        return self._decision(
            "PASS",
            "DATA_SOURCE_TRUSTED",
            "NONE",
            source_name,
        )

    def _decision(
        self,
        status: str,
        reason: str,
        required_action: str,
        source_name: str,
    ) -> dict:
        return {
            "status": status,
            "reason": reason,
            "required_action": required_action,
            "source_name": source_name,
        }
