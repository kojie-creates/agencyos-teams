"""Reusable policy gate for prototype governed services."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PolicyResult:
    """Structured policy decision for shared governance callers."""

    status: str
    reason_code: str
    mandatory_remediation: str
    source: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "reason": self.reason_code,
            "reason_code": self.reason_code,
            "required_action": self.mandatory_remediation,
            "mandatory_remediation": self.mandatory_remediation,
            "source": self.source,
        }


class PolicyGate:
    """Runs lightweight prototype guardrail checks against text input."""

    BLOCKING_STATUSES = ("FLAGGED", "FAIL")
    HIGH_RISK_KEYWORDS = ("litigation", "acquisition", "unregulated")

    EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

    def evaluate(self, input_context: str, source_context: str | None = None) -> PolicyResult:
        context = str(input_context or "")
        source = str(source_context or "CLI")

        if self._contains_pii(context):
            return PolicyResult(
                status="FAIL",
                reason_code="PII_DETECTED",
                mandatory_remediation="MASKING",
                source=source,
            )

        if self._contains_high_risk_keyword(context):
            return PolicyResult(
                status="FLAGGED",
                reason_code="HIGH_RISK_KEYWORD",
                mandatory_remediation="HUMAN_REVIEW",
                source=source,
            )

        return PolicyResult(
            status="PASS",
            reason_code="NO_POLICY_VIOLATION",
            mandatory_remediation="NONE",
            source=source,
        )

    def check_compliance(self, input_context: str, source: str | None = None) -> dict:
        """Compatibility method for existing prototype callers."""
        result = self.evaluate(input_context, source_context=source)
        return {
            "status": result.status,
            "reason": result.reason_code,
            "required_action": result.mandatory_remediation,
            "source": result.source,
        }

    def check_data_source_context(
        self,
        input_context: str,
        source_context: str | None = None,
    ) -> dict:
        """Compatibility method for data-source policy pre-checks."""
        return self.check_compliance(input_context, source=source_context)

    def is_blocking(self, policy_result: PolicyResult | dict) -> bool:
        status = (
            policy_result.status
            if isinstance(policy_result, PolicyResult)
            else policy_result.get("status")
        )
        return status in self.BLOCKING_STATUSES

    def _contains_pii(self, context: str) -> bool:
        return any(
            pattern.search(context)
            for pattern in (
                self.EMAIL_PATTERN,
                self.SSN_PATTERN,
                self.CREDIT_CARD_PATTERN,
            )
        )

    def _contains_high_risk_keyword(self, context: str) -> bool:
        normalized = context.lower()
        return any(
            re.search(rf"\b{re.escape(keyword)}\b", normalized)
            for keyword in self.HIGH_RISK_KEYWORDS
        )
