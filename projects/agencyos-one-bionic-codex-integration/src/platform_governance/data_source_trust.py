"""Reusable data-source trust gate for prototype governed services."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrustResult:
    """Structured trust decision for data-source governance callers."""

    status: str
    reason_code: str
    required_action: str
    source_name: str
    confidence_score: float

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "reason": self.reason_code,
            "reason_code": self.reason_code,
            "required_action": self.required_action,
            "source_name": self.source_name,
            "confidence_score": self.confidence_score,
        }


class DataSourceTrustGate:
    """Classifies whether data inputs can feed downstream prototype workflows."""

    MIN_RELIABILITY_RATING = 0.75
    MAX_DATA_AGE_DAYS = 30

    def validate(self, source_metadata: dict) -> TrustResult:
        source = source_metadata or {}
        source_name = str(source.get("source_name") or "unknown")
        reliability_rating = float(source.get("reliability_rating") or 0)

        if not bool(source.get("owner_approved")):
            return self._decision(
                "FAIL",
                "OWNER_APPROVAL_MISSING",
                "OWNER_APPROVAL",
                source_name,
                reliability_rating,
            )

        if str(source.get("consent_status") or "").upper() != "APPROVED":
            return self._decision(
                "FAIL",
                "CONSENT_NOT_APPROVED",
                "CONSENT_REVIEW",
                source_name,
                reliability_rating,
            )

        if reliability_rating < self.MIN_RELIABILITY_RATING:
            return self._decision(
                "FLAGGED",
                "LOW_RELIABILITY_SOURCE",
                "HUMAN_REVIEW",
                source_name,
                reliability_rating,
            )

        data_age_days = int(source.get("data_age_days") or 0)
        if data_age_days > self.MAX_DATA_AGE_DAYS:
            return self._decision(
                "FLAGGED",
                "DATA_SOURCE_STALE",
                "HUMAN_REVIEW",
                source_name,
                reliability_rating,
            )

        return self._decision(
            "PASS",
            "DATA_SOURCE_TRUSTED",
            "NONE",
            source_name,
            reliability_rating,
        )

    def validate_source(self, source_context: dict) -> dict:
        """Compatibility method for existing prototype callers."""
        result = self.validate(source_context)
        return {
            "status": result.status,
            "reason": result.reason_code,
            "required_action": result.required_action,
            "source_name": result.source_name,
        }

    def _decision(
        self,
        status: str,
        reason_code: str,
        required_action: str,
        source_name: str,
        confidence_score: float,
    ) -> TrustResult:
        return TrustResult(
            status=status,
            reason_code=reason_code,
            required_action=required_action,
            source_name=source_name,
            confidence_score=round(confidence_score, 2),
        )
