# GovernanceEngines/__init__.py
from .adversarial_engine import AdversarialEngine
from .data_lineage_tracker import DataLineageTracker

def get_all_engines() -> list['EngineInterface']:
    """Collects all initialized governance engines."""
    return [AdversarialEngine(), 
            DataLineageTracker()]