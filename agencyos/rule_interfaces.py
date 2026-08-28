# rule_interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict

class Context:
    """Standardized context object passed to all governance and compliance checks."""
    def __init__(self, operation_id: str, data_context: dict, user_role: str, jurisdiction: List[str]):
        self.operation_id = operation_id
        self.data_context = data_context  # e.g., {'source': 'CRM', 'pii_present': True}
        self.user_role = user_role         # e.g., "Data Scientist"
        self.jurisdiction = jurisdiction   # List of applicable regulations (e.g., ['HIPAA', 'GDPR'])

class CheckResult:
    """Standardized result object for all checks."""
    def __init__(self, check_type: str, is_compliant: bool, severity: str, details: str):
        self.check_type = check_type   # e.g., "COMPLIANCE:HIPAA" or "GOV:ADV_AI"
        self.is_compliant = is_compliant # True/False
        self.severity = severity       # 'CRITICAL', 'WARN', 'INFO'
        self.details = details

class RuleInterface(ABC):
    """Abstract Base Class for all Compliance Adapters."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run_checks(self, context: Context) -> List[CheckResult]:
        """Runs the specific compliance checks for the given context."""
        pass

class EngineInterface(ABC):
    """Abstract Base Class for all Governance Engines."""
    @abstractmethod
    def assess(self, context: Context) -> CheckResult:
        """Assesses system integrity and risk based on operational context."""
        pass