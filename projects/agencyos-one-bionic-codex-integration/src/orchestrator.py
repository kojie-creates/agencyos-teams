"""Workflow orchestration skeleton for Bionic + Codex integration."""

import json
from pathlib import Path
from uuid import uuid4

from artifact_repository import ArtifactRepository
from data_source_trust_module import DataSourceTrustService
from forecasting_engine import ForecastingEngine
from monitoring import MonitoringService
from policy_checker import PolicyEngine


class IntegrationOrchestrator:
    """Coordinates workflow stages for an AgencyOS Teams-managed project."""

    def __init__(
        self,
        project_name="agencyos-one-bionic-codex-integration",
        artifact_repository=None,
        asset_workspace=None,
    ):
        self.project_name = project_name
        self.events = []
        self.artifact_repository = artifact_repository
        self.asset_workspace = Path(asset_workspace or Path(".") / "asset-workspace")

    def initialize_workflow(self, goal):
        """Create the initial workflow record for a project goal."""
        if not goal or not str(goal).strip():
            raise ValueError("A project goal is required.")

        return {
            "project": self.project_name,
            "goal": str(goal).strip(),
            "status": "initialized",
            "core_services_executed": True,
            "stages": [
                "scope",
                "policy_check",
                "bionic_handoff",
                "codex_build",
                "verification",
                "closeout",
            ],
        }

    def run_workflow(self, input_context: str, source_context: str = "CLI") -> dict:
        """Dispatch every workflow through the policy gate first."""
        policy = PolicyEngine().check_compliance(
            input_context,
            source=source_context,
        )

        if source_context == "AGENT_TRIGGER":
            self.events.append(
                {
                    "event": "INTERNAL_AGENT_REQUEST",
                    "trust_level": "HIGHER_INTERNAL_TRUST",
                    "policy_enforced": True,
                }
            )

        if policy["status"] == "PASS":
            result = self.initialize_workflow(input_context)
            result["source_context"] = source_context
            result["policy"] = policy
            result["events"] = list(self.events)
            return result

        if policy["status"] in ("FLAGGED", "FAIL"):
            return {
                "project": self.project_name,
                "status": "HALTED",
                "message": (
                    "Workflow Halted by Policy Gate. "
                    f"Reason: {policy['reason']}. "
                    f"Required Action: {policy['required_action']}. "
                    "Cannot proceed until resolved."
                ),
                "reason": policy["reason"],
                "required_action": policy["required_action"],
                "source_context": source_context,
                "policy": policy,
                "events": list(self.events),
                "core_services_executed": False,
            }

        return {
            "project": self.project_name,
            "status": "HALTED",
            "message": (
                "Workflow Halted by Policy Gate. "
                "Reason: UNKNOWN_POLICY_STATUS. "
                "Required Action: HUMAN_REVIEW. "
                "Cannot proceed until resolved."
            ),
            "reason": "UNKNOWN_POLICY_STATUS",
            "required_action": "HUMAN_REVIEW",
            "source_context": source_context,
            "policy": policy,
            "events": list(self.events),
            "core_services_executed": False,
        }

    def process_asset(self, source_file: str, transaction_metadata: dict | None = None) -> dict:
        """Process an asset and make transaction logging the final required step."""
        try:
            source_path = Path(source_file)
            if not source_path.is_file():
                raise FileNotFoundError(f"Asset not found: {source_file}")

            asset_status = "PROCESSED"

            transaction_id = self._artifact_repository().log_asset_transaction(
                source_file=str(source_path),
                status=asset_status,
                transaction_metadata=transaction_metadata or {},
            )

            return {
                "source_file": str(source_path),
                "status": "COMPLETED",
                "asset_status": asset_status,
                "transaction_id": transaction_id,
            }
        except Exception as error:
            return {
                "source_file": source_file,
                "status": "FAILED",
                "reason": "ASSET_TRANSACTION_LOGGING_FAILED",
                "error": str(error),
            }

    def run_diagnostics(self, input_context: str, source_context: str = "CLI") -> dict:
        """Run simulated diagnostics through policy and manifest logging."""
        service_call_order = []
        policy_engine = PolicyEngine()
        policy = policy_engine.check_compliance(input_context, source=source_context)
        service_call_order.append("policy_check")

        if policy_engine.is_blocking(policy):
            return {
                "project": self.project_name,
                "status": "HALTED",
                "message": (
                    "Workflow Halted by Policy Gate. "
                    f"Reason: {policy['reason']}. "
                    f"Required Action: {policy['required_action']}. "
                    "Cannot proceed until resolved."
                ),
                "policy": policy,
                "service_call_order": service_call_order,
                "diagnostics_executed": False,
                "required_action": policy["required_action"],
            }

        diagnostics = MonitoringService().run_diagnostics(
            input_context=input_context,
            source_context=source_context,
        )
        service_call_order.append("monitoring_service")

        diagnostics_path = self._write_diagnostics_report(diagnostics)

        try:
            transaction_id = self._artifact_repository().log_asset_transaction(
                source_file=str(diagnostics_path),
                status="DIAGNOSTICS_COMPLETED",
                transaction_metadata={
                    "workflow_step": "diagnostics",
                    "source_context": source_context,
                    "policy_status": policy["status"],
                    "diagnostic_status": diagnostics["status"],
                },
            )
        except Exception as error:
            return {
                "project": self.project_name,
                "status": "FAILED",
                "reason": "DIAGNOSTIC_TRANSACTION_LOGGING_FAILED",
                "error": str(error),
                "policy": policy,
                "diagnostics": diagnostics,
                "service_call_order": service_call_order,
                "diagnostics_executed": True,
            }

        service_call_order.append("transaction_manifest")

        return {
            "project": self.project_name,
            "status": "COMPLETED",
            "input_context": str(input_context or "").strip(),
            "source_context": source_context,
            "policy": policy,
            "diagnostics": diagnostics,
            "transaction_id": transaction_id,
            "service_call_order": service_call_order,
            "diagnostics_executed": True,
        }

    def predict_workflow(
        self,
        input_context: str,
        source_context: str,
        source: dict,
        input_payload: dict,
    ) -> dict:
        """Run policy, data-source trust, forecast, and manifest logging."""
        service_call_order = []
        policy_engine = PolicyEngine()
        policy = policy_engine.check_data_source_context(
            input_context,
            source_context=source_context,
        )
        service_call_order.append("policy_check")

        if policy_engine.is_blocking(policy):
            return self._complete_prediction_attempt(
                input_context=input_context,
                source_context=source_context,
                source=source,
                input_payload=input_payload,
                status="HALTED",
                manifest_status="FORECAST_HALTED",
                result="halted",
                policy=policy,
                trust_result=None,
                forecast=None,
                service_call_order=service_call_order,
                reason=policy["reason"],
                required_action=policy["required_action"],
            )

        trust_result = DataSourceTrustService().validate_source(source)
        service_call_order.append("data_source_trust")

        if trust_result["status"] != "PASS":
            return self._complete_prediction_attempt(
                input_context=input_context,
                source_context=source_context,
                source=source,
                input_payload=input_payload,
                status="HALTED",
                manifest_status="FORECAST_HALTED",
                result="halted",
                policy=policy,
                trust_result=trust_result,
                forecast=None,
                service_call_order=service_call_order,
                reason=trust_result["reason"],
                required_action=trust_result["required_action"],
            )

        forecast = ForecastingEngine().run_prediction(
            source_context=trust_result,
            input_payload=input_payload,
        )
        service_call_order.append("forecasting_engine")

        return self._complete_prediction_attempt(
            input_context=input_context,
            source_context=source_context,
            source=source,
            input_payload=input_payload,
            status="COMPLETED",
            manifest_status="FORECAST_COMPLETED",
            result="completed",
            policy=policy,
            trust_result=trust_result,
            forecast=forecast,
            service_call_order=service_call_order,
            reason=forecast["predicted_outcome"],
            required_action="HUMAN_REVIEW" if forecast["human_review_required"] else "NONE",
        )

    def execute_master_workflow(self, goal: str, source_context: str) -> dict:
        """Run the full policy-first workflow under one command umbrella."""
        service_call_order = []
        policy_engine = PolicyEngine()

        policy = policy_engine.check_compliance(goal, source=source_context)
        service_call_order.append("policy_check")

        if policy_engine.is_blocking(policy):
            return {
                "project": self.project_name,
                "status": "HALTED",
                "message": (
                    "Workflow Halted by Policy Gate. "
                    f"Reason: {policy['reason']}. "
                    f"Required Action: {policy['required_action']}. "
                    "Cannot proceed until resolved."
                ),
                "policy": policy,
                "service_call_order": service_call_order,
                "core_services_executed": False,
                "required_action": policy["required_action"],
            }

        charter = self._run_charter(goal=goal, source_context=source_context)
        service_call_order.append("charter")

        asset_path = self._write_simulated_asset(goal=goal, charter=charter)
        asset = self.process_asset(
            str(asset_path),
            transaction_metadata={
                "workflow_step": "asset_processor",
                "charter_id": charter["charter_id"],
                "source_context": source_context,
            },
        )
        service_call_order.append("asset_processor")

        if asset["status"] != "COMPLETED":
            return {
                "project": self.project_name,
                "status": "FAILED",
                "reason": "ASSET_PROCESSING_FAILED",
                "policy": policy,
                "charter": charter,
                "asset": asset,
                "service_call_order": service_call_order,
                "core_services_executed": True,
            }

        try:
            final_transaction_id = self._artifact_repository().log_asset_transaction(
                source_file=str(asset_path),
                status="MASTER_WORKFLOW_COMPLETED",
                transaction_metadata={
                    "workflow_step": "transaction_manifest",
                    "asset_transaction_id": asset["transaction_id"],
                    "charter_id": charter["charter_id"],
                    "source_context": source_context,
                    "policy_status": policy["status"],
                },
            )
        except Exception as error:
            return {
                "project": self.project_name,
                "status": "FAILED",
                "reason": "MASTER_TRANSACTION_LOGGING_FAILED",
                "error": str(error),
                "policy": policy,
                "charter": charter,
                "asset": asset,
                "service_call_order": service_call_order,
                "core_services_executed": True,
            }

        service_call_order.append("transaction_manifest")

        return {
            "project": self.project_name,
            "status": "COMPLETED",
            "goal": str(goal).strip(),
            "source_context": source_context,
            "policy": policy,
            "charter": charter,
            "asset": asset,
            "final_transaction_id": final_transaction_id,
            "service_call_order": service_call_order,
            "proof": {
                "policy_status": policy["status"],
                "asset_transaction_id": asset["transaction_id"],
                "final_transaction_id": final_transaction_id,
            },
            "core_services_executed": True,
        }

    def _run_charter(self, goal: str, source_context: str) -> dict:
        return {
            "charter_id": f"charter-{abs(hash((self.project_name, goal, source_context)))}",
            "status": "CHARTER_CREATED",
            "goal": str(goal).strip(),
            "source_context": source_context,
            "workflow": [
                "policy_check",
                "charter",
                "asset_processor",
                "transaction_manifest",
            ],
        }

    def _write_simulated_asset(self, goal: str, charter: dict) -> Path:
        self.asset_workspace.mkdir(parents=True, exist_ok=True)
        asset_path = self.asset_workspace / f"{charter['charter_id']}.txt"
        asset_path.write_text(
            "\n".join(
                [
                    f"Project: {self.project_name}",
                    f"Goal: {str(goal).strip()}",
                    f"Charter: {charter['charter_id']}",
                    "Artifact: simulated master workflow asset",
                ]
            ),
            encoding="utf-8",
        )
        return asset_path

    def _write_diagnostics_report(self, diagnostics: dict) -> Path:
        self.asset_workspace.mkdir(parents=True, exist_ok=True)
        diagnostics_path = self.asset_workspace / "diagnostics-report.txt"
        checks = diagnostics.get("checks", {})
        diagnostics_path.write_text(
            "\n".join(
                [
                    f"Project: {self.project_name}",
                    f"Status: {diagnostics.get('status')}",
                    f"Summary: {diagnostics.get('summary')}",
                    f"Source: {diagnostics.get('source_context')}",
                    f"policy_engine_available: {checks.get('policy_engine_available')}",
                    f"artifact_repository_available: {checks.get('artifact_repository_available')}",
                    f"api_gateway_contract_available: {checks.get('api_gateway_contract_available')}",
                ]
            ),
            encoding="utf-8",
        )
        return diagnostics_path

    def _complete_prediction_attempt(
        self,
        input_context: str,
        source_context: str,
        source: dict,
        input_payload: dict,
        status: str,
        manifest_status: str,
        result: str,
        policy: dict,
        trust_result: dict | None,
        forecast: dict | None,
        service_call_order: list,
        reason: str,
        required_action: str,
    ) -> dict:
        try:
            attempt_path = self._write_prediction_attempt(
                input_context=input_context,
                source_context=source_context,
                source=source,
                input_payload=input_payload,
                status=status,
                result=result,
                policy=policy,
                trust_result=trust_result,
                forecast=forecast,
                reason=reason,
            )
            transaction_id = self._artifact_repository().log_asset_transaction(
                source_file=str(attempt_path),
                status=manifest_status,
                transaction_metadata={
                    "workflow_step": "forecasting",
                    "source_context": source_context,
                    "source_name": (source or {}).get("source_name", "unknown"),
                    "result": result,
                    "reason": reason,
                    "policy": policy,
                    "trust_result": trust_result,
                    "forecast": forecast,
                    "model_scope": "SIMULATED_PROTOTYPE",
                },
            )
        except Exception as error:
            return {
                "project": self.project_name,
                "status": "FAILED",
                "reason": "FORECAST_TRANSACTION_LOGGING_FAILED",
                "error": str(error),
                "policy": policy,
                "trust_result": trust_result,
                "forecast": forecast,
                "service_call_order": service_call_order,
            }

        completed_call_order = list(service_call_order) + ["transaction_manifest"]
        response = {
            "project": self.project_name,
            "status": status,
            "input_context": str(input_context or "").strip(),
            "source_context": source_context,
            "policy": policy,
            "trust_result": trust_result,
            "transaction_id": transaction_id,
            "service_call_order": completed_call_order,
            "required_action": required_action,
        }
        if forecast is not None:
            response["forecast"] = forecast
        if status != "COMPLETED":
            response["reason"] = reason
        return response

    def _write_prediction_attempt(
        self,
        input_context: str,
        source_context: str,
        source: dict,
        input_payload: dict,
        status: str,
        result: str,
        policy: dict,
        trust_result: dict | None,
        forecast: dict | None,
        reason: str,
    ) -> Path:
        self.asset_workspace.mkdir(parents=True, exist_ok=True)
        attempt_path = self.asset_workspace / f"forecast-{uuid4().hex}.json"
        attempt_path.write_text(
            json.dumps(
                {
                    "input_context": str(input_context or "").strip(),
                    "source_context": source_context,
                    "source": source or {},
                    "input_payload": input_payload or {},
                    "status": status,
                    "result": result,
                    "reason": reason,
                    "policy": policy,
                    "trust_result": trust_result,
                    "forecast": forecast,
                    "model_scope": "SIMULATED_PROTOTYPE",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return attempt_path

    def _artifact_repository(self):
        if self.artifact_repository is None:
            self.artifact_repository = ArtifactRepository(Path(".") / "artifact-transactions")
        return self.artifact_repository


def execute_master_workflow(goal: str, source_context: str) -> dict:
    """Top-level entry point for the master workflow dispatcher."""
    return IntegrationOrchestrator().execute_master_workflow(
        goal=goal,
        source_context=source_context,
    )


if __name__ == "__main__":
    result = execute_master_workflow(
        "Coordinate Bionic and Codex through AgencyOS Teams.",
        "CLI",
    )
    print(result)
