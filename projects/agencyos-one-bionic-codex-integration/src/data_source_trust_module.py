"""Compatibility data-source trust validation for prototype governance tests."""

from platform_governance.data_source_trust import DataSourceTrustGate


class DataSourceTrustService(DataSourceTrustGate):
    """Backwards-compatible facade over the shared platform trust gate."""

    def validate_source(self, source_context: dict) -> dict:
        """Return a trust decision for a supplied data source context as a dict."""
        return self.validate(source_context).to_dict()
