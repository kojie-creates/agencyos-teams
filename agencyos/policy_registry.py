# policy_registry.py
from typing import Dict, List
from .rule_interfaces import RuleInterface, EngineInterface

class PolicyRegistry:
    """Central repository and factory for discovering and initializing all available checks."""
    _adapters: Dict[str, RuleInterface] = {}
    _engines: Dict[str, EngineInterface] = {}

    @classmethod
    def register(cls, adapter: RuleInterface):
        """Registers a compliance adapter by its name/jurisdiction."""
        if adapter.name in cls._adapters:
            print(f"Warning: Overwriting existing adapter for {adapter.name}")
        cls._adapters[adapter.name] = adapter

    @classmethod
    def register_engine(cls, engine: EngineInterface):
        """Registers a governance engine by its internal name."""
        if engine.__class__.__name__ in cls._engines:
            print(f"Warning: Overwriting existing engine for {engine.__class__.__name__}")
        cls._engines[engine.__class__.__name__] = engine

    @classmethod
    def get_compliant_adapters(cls, context: Context) -> List[RuleInterface]:
        """Filters and returns only the adapters relevant to the context's jurisdiction."""
        relevant_adapters = []
        for adapter in cls._adapters.values():
            # Simplified logic for demonstration; a real system would check 'jurisdiction' field on the adapter itself.
            if "HIPAA" in context.jurisdiction and isinstance(adapter, ComplianceAdapter): # Placeholder type checking
                 relevant_adapters.append(adapter)
        return relevant_adapters

    @classmethod
    def get_all_engines(cls) -> List[EngineInterface]:
        """Returns all available governance engines for a full risk assessment."""
        return list(cls._engines.values())

# NOTE: This file must be updated with specific imports (e.g., from .ComplianceAdapters import ...) 
# to instantiate and register the concrete classes during application startup.