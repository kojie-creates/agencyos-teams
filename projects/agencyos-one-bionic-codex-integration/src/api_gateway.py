"""Framework-agnostic API gateway for the integration core loop."""

import json
import os
from pathlib import Path
from uuid import uuid4

from artifact_repository import ArtifactRepository
from external_adapter import ExternalAPIError
from external_adapter import GenericAPIAdapter
from orchestrator import execute_master_workflow
from orchestrator import IntegrationOrchestrator
from platform_governance.auth_gate import AuthGate
from platform_governance.data_source_trust import DataSourceTrustGate
from platform_governance.policy_gate import PolicyGate

API_KEY_ENV_VAR = "AGENCYOS_API_KEY"


class ApiGateway:
    """Routes simulated HTTP requests to backend services."""

    def __init__(
        self,
        workflow_runner=None,
        diagnostic_runner=None,
        external_adapter=None,
        external_workspace=None,
        data_source_trust_service=None,
        data_source_workspace=None,
        policy_engine=None,
        artifact_repository=None,
    ):
        self.workflow_runner = workflow_runner or execute_master_workflow
        self.diagnostic_runner = diagnostic_runner
        self.external_adapter = external_adapter or GenericAPIAdapter()
        self.external_workspace = Path(external_workspace or Path(".") / "external-attempts")
        self.data_source_trust_service = data_source_trust_service or DataSourceTrustGate()
        self.data_source_workspace = Path(data_source_workspace or Path(".") / "data-source-attempts")
        self.policy_engine = policy_engine or PolicyGate()
        self.artifact_repository = artifact_repository

    def handle_request(
        self,
        method: str,
        path: str,
        json_body: dict | None = None,
        query: dict | None = None,
    ) -> dict:
        """Return a JSON-safe HTTP-style response object."""
        method_name = str(method or "").upper()

        if method_name == "POST" and path == "/v1/workflow/start":
            return self._start_workflow(json_body or {})

        if method_name == "GET" and path == "/v1/policy/check":
            return self._check_policy(query or {})

        if method_name == "GET" and path == "/v1/diagnose":
            return self._run_diagnostics(query or {})

        if method_name == "POST" and path == "/v1/data-source/validate":
            return self._validate_data_source(json_body or {})

        if method_name == "POST" and path == "/v1/predict/forecast":
            return self._run_forecast(json_body or {})

        if path.startswith("/v1/external/"):
            return self._run_external_call(method_name, path, json_body or {})

        if method_name == "GET" and path.startswith("/v1/transactions/"):
            transaction_id = path.removeprefix("/v1/transactions/").strip("/")
            return self._get_transaction(transaction_id)

        return {
            "status_code": 404,
            "body": {
                "success": False,
                "error": "NOT_FOUND",
            },
        }

    def _start_workflow(self, body: dict) -> dict:
        goal = str(body.get("goal") or "").strip()
        source_context = str(body.get("source_context") or "CLI").strip() or "CLI"

        if not goal:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": "GOAL_REQUIRED",
                },
            }

        policy = self.policy_engine.check_compliance(goal, source=source_context)

        if self.policy_engine.is_blocking(policy):
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "status": "HALTED",
                    "policy": policy,
                    "required_action": policy["required_action"],
                    "message": (
                        "Workflow Halted by Policy Gate. "
                        f"Reason: {policy['reason']}. "
                        f"Required Action: {policy['required_action']}. "
                        "Cannot proceed until resolved."
                    ),
                },
            }

        result = self.workflow_runner(goal, source_context)
        status_code = 200 if result.get("status") == "COMPLETED" else 500

        return {
            "status_code": status_code,
            "body": {
                "success": status_code == 200,
                **self._json_object(result),
            },
        }

    def _check_policy(self, query: dict) -> dict:
        input_context = query.get("input") or query.get("input_context") or ""
        source_context = query.get("source_context") or "CLI"
        policy = self.policy_engine.check_compliance(
            str(input_context),
            source=str(source_context),
        )

        return {
            "status_code": 200,
            "body": {
                "success": True,
                "policy": policy,
            },
        }

    def _run_diagnostics(self, query: dict) -> dict:
        input_context = str(
            query.get("input") or query.get("input_context") or "Run diagnostics."
        )
        source_context = str(query.get("source_context") or "CLI")
        policy = self.policy_engine.check_compliance(
            input_context,
            source=source_context,
        )

        if self.policy_engine.is_blocking(policy):
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "status": "HALTED",
                    "policy": policy,
                    "required_action": policy["required_action"],
                    "message": (
                        "Workflow Halted by Policy Gate. "
                        f"Reason: {policy['reason']}. "
                        f"Required Action: {policy['required_action']}. "
                        "Cannot proceed until resolved."
                    ),
                },
            }

        runner = self.diagnostic_runner
        if runner is None:
            runner = IntegrationOrchestrator(
                artifact_repository=self.artifact_repository,
            ).run_diagnostics

        result = runner(input_context=input_context, source_context=source_context)
        status_code = 200 if result.get("status") == "COMPLETED" else 500

        return {
            "status_code": status_code,
            "body": {
                "success": status_code == 200,
                **self._json_object(result),
            },
        }

    def _validate_data_source(self, body: dict) -> dict:
        input_context = str(
            body.get("input_context") or body.get("input") or "Validate data source."
        )
        source_context = str(body.get("source_context") or "CLI")
        source = body.get("source") or {}

        policy = self.policy_engine.check_data_source_context(
            input_context,
            source_context=source_context,
        )
        if self.policy_engine.is_blocking(policy):
            transaction_id = self._log_data_source_validation(
                source=source,
                status="DATA_SOURCE_VALIDATION_HALTED",
                result="halted",
                reason=policy["reason"],
                metadata={
                    "source_context": source_context,
                    "policy": policy,
                    "trust_result": None,
                },
            )
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "status": "HALTED",
                    "policy": policy,
                    "required_action": policy["required_action"],
                    "transaction_id": transaction_id,
                },
            }

        trust_result = self.data_source_trust_service.validate_source(source)

        if trust_result["status"] == "FAIL":
            transaction_id = self._log_data_source_validation(
                source=source,
                status="DATA_SOURCE_VALIDATION_HALTED",
                result="halted",
                reason=trust_result["reason"],
                metadata={
                    "source_context": source_context,
                    "policy": policy,
                    "trust_result": trust_result,
                },
            )
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "status": "HALTED",
                    "policy": policy,
                    "trust_result": trust_result,
                    "required_action": trust_result["required_action"],
                    "transaction_id": transaction_id,
                },
            }

        if trust_result["status"] == "FLAGGED":
            transaction_id = self._log_data_source_validation(
                source=source,
                status="DATA_SOURCE_VALIDATION_FLAGGED",
                result="flagged",
                reason=trust_result["reason"],
                metadata={
                    "source_context": source_context,
                    "policy": policy,
                    "trust_result": trust_result,
                },
            )
            return {
                "status_code": 202,
                "body": {
                    "success": False,
                    "status": "FLAGGED",
                    "policy": policy,
                    "trust_result": trust_result,
                    "required_action": trust_result["required_action"],
                    "transaction_id": transaction_id,
                },
            }

        transaction_id = self._log_data_source_validation(
            source=source,
            status="DATA_SOURCE_VALIDATION_COMPLETED",
            result="trusted",
            reason=trust_result["reason"],
            metadata={
                "source_context": source_context,
                "policy": policy,
                "trust_result": trust_result,
            },
        )
        return {
            "status_code": 200,
            "body": {
                "success": True,
                "status": "COMPLETED",
                "policy": policy,
                "trust_result": trust_result,
                "transaction_id": transaction_id,
            },
        }

    def _run_forecast(self, body: dict) -> dict:
        input_context = str(
            body.get("input_context") or body.get("input") or "Run forecast."
        )
        source_context = str(body.get("source_context") or "CLI")
        source = body.get("source") or {}
        input_payload = body.get("input_payload") or body.get("payload") or {}

        orchestrator = IntegrationOrchestrator(
            artifact_repository=self.artifact_repository,
            asset_workspace=self.data_source_workspace,
            policy_gate=self.policy_engine,
            data_source_trust_gate=self.data_source_trust_service,
        )
        result = orchestrator.predict_workflow(
            input_context=input_context,
            source_context=source_context,
            source=source,
            input_payload=input_payload,
        )
        self.artifact_repository = orchestrator.artifact_repository

        if result.get("status") == "COMPLETED":
            status_code = 200
        elif result.get("status") == "HALTED":
            status_code = 403
        else:
            status_code = 500

        return {
            "status_code": status_code,
            "body": {
                "success": status_code == 200,
                **self._json_object(result),
            },
        }

    def _run_external_call(self, method_name: str, path: str, body: dict) -> dict:
        if method_name not in ("GET", "POST"):
            return {
                "status_code": 405,
                "body": {
                    "success": False,
                    "error": "METHOD_NOT_ALLOWED",
                },
            }

        route_parts = path.removeprefix("/v1/external/").strip("/").split("/", 1)
        if len(route_parts) != 2 or not all(route_parts):
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": "EXTERNAL_ROUTE_REQUIRED",
                },
            }

        service, endpoint = route_parts
        input_context = str(body.get("input_context") or body.get("input") or "")
        source_context = str(body.get("source_context") or "CLI")
        openapi_spec = str(body.get("openapi_spec") or "")
        credentials = body.get("credentials") or {}
        payload = body.get("payload") or {}

        policy = self.policy_engine.check_compliance(input_context, source=source_context)
        credential_policy = self._check_external_credential_scope(
            service=service,
            endpoint=endpoint,
            credentials=credentials,
            base_policy=policy,
        )

        if self.policy_engine.is_blocking(credential_policy):
            transaction_id = self._log_external_attempt(
                service=service,
                endpoint=endpoint,
                status="EXTERNAL_CALL_POLICY_HALTED",
                result="policy_halt",
                error_code=credential_policy["reason"],
                metadata={
                    "source_context": source_context,
                    "policy": credential_policy,
                    "attempted_call": False,
                },
            )
            return {
                "status_code": 403,
                "body": {
                    "success": False,
                    "status": "HALTED",
                    "policy": credential_policy,
                    "required_action": credential_policy["required_action"],
                    "transaction_id": transaction_id,
                },
            }

        try:
            external_call = self.external_adapter.execute_call(
                service=service,
                endpoint=endpoint,
                openapi_spec=openapi_spec,
                credentials=credentials,
                payload=payload,
            )
            transaction_id = self._log_external_attempt(
                service=service,
                endpoint=endpoint,
                status="EXTERNAL_CALL_COMPLETED",
                result="success",
                error_code=None,
                metadata={
                    "source_context": source_context,
                    "policy": credential_policy,
                    "attempted_call": True,
                    "external_call": external_call,
                },
            )
            return {
                "status_code": 200,
                "body": {
                    "success": True,
                    "status": "COMPLETED",
                    "policy": credential_policy,
                    "external_call": external_call,
                    "transaction_id": transaction_id,
                },
            }
        except ExternalAPIError as error:
            transaction_id = self._log_external_attempt(
                service=service,
                endpoint=endpoint,
                status="EXTERNAL_CALL_FAILED",
                result="failure",
                error_code=error.error_code,
                metadata={
                    "source_context": source_context,
                    "policy": credential_policy,
                    "attempted_call": True,
                    "error": str(error),
                },
            )
            return {
                "status_code": 502,
                "body": {
                    "success": False,
                    "status": "FAILED",
                    "policy": credential_policy,
                    "error_code": error.error_code,
                    "message": str(error),
                    "transaction_id": transaction_id,
                },
            }

    def _check_external_credential_scope(
        self,
        service: str,
        endpoint: str,
        credentials: dict,
        base_policy: dict,
    ) -> dict:
        if self.policy_engine.is_blocking(base_policy):
            return base_policy

        required_scope = f"{service}:{endpoint}"
        scopes = credentials.get("scopes") or []
        if not credentials.get("token") or required_scope not in scopes:
            return {
                "status": "FAIL",
                "reason": "INVALID_CREDENTIAL_SCOPE",
                "required_action": "CREDENTIAL_REVIEW",
                "source": base_policy.get("source", "CLI"),
                "required_scope": required_scope,
            }

        return {
            **base_policy,
            "required_scope": required_scope,
            "credential_scope_verified": True,
        }

    def _log_external_attempt(
        self,
        service: str,
        endpoint: str,
        status: str,
        result: str,
        error_code: str | None,
        metadata: dict,
    ) -> str:
        repository = self.artifact_repository or ArtifactRepository(
            Path(".") / "artifact-transactions"
        )
        self.artifact_repository = repository
        self.external_workspace.mkdir(parents=True, exist_ok=True)
        attempt_path = self.external_workspace / f"external-{uuid4().hex}.json"
        attempt_record = {
            "service": service,
            "endpoint": endpoint,
            "status": status,
            "result": result,
            "error_code": error_code,
            "metadata": metadata,
        }
        attempt_path.write_text(json.dumps(attempt_record, indent=2), encoding="utf-8")
        return repository.log_asset_transaction(
            source_file=str(attempt_path),
            status=status,
            transaction_metadata={
                "workflow_step": "external_adapter",
                "service": service,
                "endpoint": endpoint,
                "result": result,
                "error_code": error_code,
                **metadata,
            },
        )

    def _log_data_source_validation(
        self,
        source: dict,
        status: str,
        result: str,
        reason: str,
        metadata: dict,
    ) -> str:
        repository = self.artifact_repository or ArtifactRepository(
            Path(".") / "artifact-transactions"
        )
        self.artifact_repository = repository
        self.data_source_workspace.mkdir(parents=True, exist_ok=True)
        attempt_path = self.data_source_workspace / f"data-source-{uuid4().hex}.json"
        attempt_record = {
            "source": source,
            "status": status,
            "result": result,
            "reason": reason,
            "metadata": metadata,
        }
        attempt_path.write_text(json.dumps(attempt_record, indent=2), encoding="utf-8")
        return repository.log_asset_transaction(
            source_file=str(attempt_path),
            status=status,
            transaction_metadata={
                "workflow_step": "data_source_trust",
                "source_name": source.get("source_name", "unknown"),
                "result": result,
                "reason": reason,
                **metadata,
            },
        )

    def _get_transaction(self, transaction_id: str) -> dict:
        if not transaction_id:
            return {
                "status_code": 400,
                "body": {
                    "success": False,
                    "error": "TRANSACTION_ID_REQUIRED",
                },
            }

        if self.artifact_repository is None:
            return {
                "status_code": 503,
                "body": {
                    "success": False,
                    "error": "ARTIFACT_REPOSITORY_UNAVAILABLE",
                },
            }

        try:
            transaction = self.artifact_repository.get_transaction(transaction_id)
        except FileNotFoundError:
            return {
                "status_code": 404,
                "body": {
                    "success": False,
                    "error": "TRANSACTION_NOT_FOUND",
                    "transaction_id": transaction_id,
                },
            }

        return {
            "status_code": 200,
            "body": {
                "success": True,
                "transaction": self._json_object(transaction),
            },
        }

    def _json_object(self, value):
        if isinstance(value, dict):
            return {str(key): self._json_object(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._json_object(item) for item in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)


def create_app(api_gateway: ApiGateway | None = None, api_key: str | None = None):
    """Create the FastAPI wrapper.

    Set AGENCYOS_API_KEY before running the service. The wrapper allows the
    local Vite frontend origins for prototype API consumption. Tests may pass
    api_key directly to keep fixtures isolated.
    """
    from fastapi import FastAPI
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware

    gateway = api_gateway or ApiGateway()
    app = FastAPI(title="AgencyOS Prototype API", version="0.1.0")

    @app.middleware("http")
    async def require_api_key(request: Request, call_next):
        required_key = api_key if api_key is not None else os.getenv(API_KEY_ENV_VAR, "")
        auth_result = AuthGate(required_api_key=required_key).verify_api_key(
            request.headers.get("X-API-KEY")
        )
        if not auth_result.authorized:
            return JSONResponse(
                status_code=auth_result.to_http_status(),
                content={
                    "success": False,
                    "error": (
                        "API_KEY_NOT_CONFIGURED"
                        if auth_result.reason_code == "API_KEY_NOT_CONFIGURED"
                        else "UNAUTHORIZED"
                    ),
                },
            )
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-KEY"],
    )

    @app.api_route("/v1/{route_path:path}", methods=["GET", "POST"])
    async def route_v1(route_path: str, request: Request):
        body = {}
        if request.method in ("POST",):
            body_bytes = await request.body()
            if body_bytes:
                body = await request.json()

        response = gateway.handle_request(
            method=request.method,
            path=f"/v1/{route_path}",
            json_body=body,
            query=dict(request.query_params),
        )
        return JSONResponse(
            status_code=response["status_code"],
            content=response["body"],
        )

    return app


app = create_app()
