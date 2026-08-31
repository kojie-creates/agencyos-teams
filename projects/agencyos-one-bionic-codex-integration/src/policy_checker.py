"""Compatibility policy checker for the Bionic + Codex integration scaffold."""

from platform_governance.policy_gate import PolicyGate


class PolicyEngine(PolicyGate):
    """Backwards-compatible facade over the shared platform policy gate."""

    def check_compliance(self, input_context: str, source: str | None = None) -> dict:
        """Return the policy status for the supplied context as a dictionary."""
        return super().check_compliance(input_context, source=source)

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
