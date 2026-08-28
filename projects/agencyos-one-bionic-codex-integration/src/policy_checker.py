"""Policy checker for the Bionic + Codex integration scaffold."""

import re


class PolicyEngine:
    """Runs lightweight guardrail checks against text input."""

    BLOCKING_STATUSES = ("FLAGGED", "FAIL")
    HIGH_RISK_KEYWORDS = ("litigation", "acquisition", "unregulated")

    EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

    def check_compliance(self, input_context: str, source: str | None = None) -> dict:
        """Return the policy status for the supplied context."""
        context = str(input_context or "")
        source_context = str(source or "CLI")

        if self._contains_pii(context):
            return {
                "status": "FAIL",
                "reason": "PII_DETECTED",
                "required_action": "MASKING",
                "source": source_context,
            }

        if self._contains_high_risk_keyword(context):
            return {
                "status": "FLAGGED",
                "reason": "HIGH_RISK_KEYWORD",
                "required_action": "HUMAN_REVIEW",
                "source": source_context,
            }

        return {
            "status": "PASS",
            "reason": "NO_POLICY_VIOLATION",
            "required_action": "NONE",
            "source": source_context,
        }

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

    def is_blocking(self, policy_result: dict) -> bool:
        """Return True when policy requires the workflow to halt."""
        return policy_result.get("status") in self.BLOCKING_STATUSES

    def check_data_source_context(
        self,
        input_context: str,
        source_context: str | None = None,
    ) -> dict:
        """Run the generic policy gate before data-source trust validation."""
        return self.check_compliance(input_context, source=source_context)


def check_policy(input_data):
    """Return a placeholder policy decision."""
    return PolicyEngine().check_compliance(str(input_data))
