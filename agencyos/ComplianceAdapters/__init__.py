# ComplianceAdapters/__init__.py
from .gdpr_adapter import GDPRAdapter
from .hipaa_adapter import HIPAAAdapter

def get_all_adapters() -> list['RuleInterface']:
    """Collects all initialized compliance adapters."""
    return [GDPRAdapter("GDPR", "General Data Protection Regulation"), 
            HIPAAAdapter("HIPAA", "Health Insurance Portability and Accountability Act")]