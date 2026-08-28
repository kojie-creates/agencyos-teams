# orchestrator.py
from .rule_interfaces import Context, CheckResult, RuleInterface, EngineInterface
from .policy_registry import PolicyRegistry

class UGE_Orchestrator:
    """
    The Unified Governance Engine Orchestrator.
    Manages the sequential execution of all compliance and governance checks.
    """

    def __init__(self):
        print("UGE Initialized. Loading services from PolicyRegistry...")
        # Initialization hook to ensure all adapters/engines are loaded here
        pass 

    def run_full_audit(self, context: Context) -> List[CheckResult]:
        """Executes the complete governance and compliance audit pipeline."""
        all_results = []

        # STEP 1: Run Core Governance Integrity Checks (The 'How')
        print("--> [STEP 1/3] Running Core Governance Engine Assessments...")
        governance_engines = PolicyRegistry.get_all_engines()
        for engine in governance_engines:
            result = engine.assess(context) # Uses the abstract assess method
            if result.severity == 'CRITICAL':
                print(f"🛑 CRITICAL GOVERNANCE FAILURE detected: {result.check_type}. Blocking operation.")
                return [result] # Fail fast on critical governance failures.
            all_results.append(result)

        # STEP 2: Run Compliance Checks (The 'What')
        print("--> [STEP 2/3] Running Context-Specific Compliance Adapters...")
        compliant_adapters = PolicyRegistry.get_compliant_adapters(context)
        for adapter in compliant_adapters:
            results = adapter.run_checks(context) # Uses the abstract run_checks method
            all_results.extend(results)

        # STEP 3: Finalization and Reporting (The Output)
        print("--> [STEP 3/3] Audit Complete. Compiling final report.")
        # Logic here to aggregate results, check for overall pass criteria, and write the final audit log.
        return all_results